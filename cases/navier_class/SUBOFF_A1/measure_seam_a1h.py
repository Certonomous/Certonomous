#!/usr/bin/env python3
"""SUBOFF A1h -- MEASURE THE MIRROR SEAM.  Gate M-7 of the frozen pre-registration.

`SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md` §2.1, frozen at
79b4de868e1e8bbf08e14cd6db3c1d6acb3240df, registers M-7 as:

    minimum cell volume and maximum non-orthogonality RESTRICTED TO CELLS WITH ANY
    VERTEX AT |z| < 1e-6; min volume > 0, seam max non-orthogonality <= 70 deg AND
    no worse than the whole-mesh maximum.

WHY THE RESTRICTION IS THE POINT.  M-1..M-6 would be satisfied by a mesh whose seam is
a sheet of slivers: 18.24 M cells will drown a thin bad layer at z = 0 in any
whole-mesh statistic.  A mirror goes wrong at the seam and nowhere else, so the gate
must look only there.

THE SELECTION IS VERTEX-BASED BECAUSE THE REGISTRATION SAYS SO.  A face-based proxy
(cells that owned a `symm` face before the mirror) is nearly the same set and is not
the registered one; at a refinement transition a cell can touch the plane along an
edge without owning a face there.  The frozen text governs.

PLANTS (standing rule 3).  A seam reader can be blind like any other, and tonight this
act has already caught four readers that were:
  S-A  the seam selector is run at the registered plane AND at an impossible plane
       (|z - 1e9| < 1e-6).  It must find cells at the first and NONE at the second.
       A selector that returns the same answer for both is not selecting.
  S-B  a known bad value is injected at a known seam cell index and must come back
       as the reported extremum.  A reducer that cannot see a planted extremum
       cannot be trusted to report one it was not shown.
Both refuse with exit 2 rather than degrading.

This script READS ONLY.  It writes nothing into the mesh case; its report goes to
--out, and it asserts that --out is outside the case.

Author: cfd lab-lane, 2026-09-13.
"""

import argparse
import json
import os
import re
import sys
import time

if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n")
    sys.exit(2)

SEAM_TOL = 1.0e-6          # |z| ceiling, frozen in §2.1 M-7
NONORTHO_MAX = 70.0        # MESH_STANDARD §3.1, frozen in §2.1 M-5
PLANT_BAD_NONORTHO = 123.456
PLANT_BAD_VOLUME = -9.87e-30


class Refuse(Exception):
    pass


def refuse(msg):
    raise Refuse(msg)


# --------------------------------------------------------------- OF parsing --
_HDR = re.compile(rb"^\s*(\d+)\s*$")


def _open(path):
    if not os.path.isfile(path):
        refuse(f"required mesh file absent: {path}")
    return open(path, "rb")


def stream_list(path):
    """Yield the body lines of an OpenFOAM ASCII list, plus its declared count.

    The format is: header dict, then a line holding ONLY the count, then `(`, then
    `count` entries, then `)`.  The count line is found by taking the FIRST bare
    integer line that is immediately followed by a line whose first character is `(`
    -- never merely the first bare integer, because FoamFile headers contain
    `version 2.0;` and similar.
    """
    fh = _open(path)
    count = None
    prev = None
    for raw in fh:
        s = raw.strip()
        if count is None:
            m = _HDR.match(s)
            if m:
                prev = int(m.group(1))
                continue
            if prev is not None and s.startswith(b"("):
                count = prev
                if len(s) > 1:                      # "(" with content on same line
                    yield s[1:]
                continue
            prev = None
            continue
        if s.startswith(b")"):
            break
        if s:
            yield s
    fh.close()
    if count is None:
        refuse(f"could not find the list count in {path}")
    stream_list.last_count = count


def declared_count(path):
    """The declared entry count of an OpenFOAM ASCII list."""
    fh = _open(path)
    prev = None
    for raw in fh:
        s = raw.strip()
        m = _HDR.match(s)
        if m:
            prev = int(m.group(1))
            continue
        if prev is not None and s.startswith(b"("):
            fh.close()
            return prev
        prev = None
    fh.close()
    refuse(f"could not find the list count in {path}")


def seam_points(points_path, tol=SEAM_TOL, plane_z=0.0):
    """Boolean list over point ids: True where |z - plane_z| < tol."""
    n = declared_count(points_path)
    flag = bytearray(n)
    i = 0
    for s in stream_list(points_path):
        # "(x y z)" possibly several per line
        for m in re.finditer(rb"\(([^)]*)\)", s):
            parts = m.group(1).split()
            if len(parts) != 3:
                continue
            if abs(float(parts[2]) - plane_z) < tol:
                flag[i] = 1
            i += 1
    if i != n:
        refuse(f"{points_path}: declared {n} points, parsed {i}")
    return flag, n


def seam_cells(mesh_dir, pflag, n_cells, tol=SEAM_TOL):
    """Cells owning or neighbouring any face that carries a seam vertex."""
    faces_path = os.path.join(mesh_dir, "faces")
    n_faces = declared_count(faces_path)
    fflag = bytearray(n_faces)
    i = 0
    for s in stream_list(faces_path):
        for m in re.finditer(rb"\(([^)]*)\)", s):
            for tok in m.group(1).split():
                if pflag[int(tok)]:
                    fflag[i] = 1
                    break
            i += 1
    if i != n_faces:
        refuse(f"{faces_path}: declared {n_faces} faces, parsed {i}")

    cflag = bytearray(n_cells)
    for nm in ("owner", "neighbour"):
        p = os.path.join(mesh_dir, nm)
        if nm == "neighbour" and not os.path.isfile(p):
            continue
        j = 0
        for s in stream_list(p):
            for tok in s.split():
                if fflag[j]:
                    c = int(tok)
                    if 0 <= c < n_cells:
                        cflag[c] = 1
                j += 1
    return cflag, n_faces


def read_vol_scalar(path):
    """internalField of an OpenFOAM ASCII volScalarField -> list of floats."""
    if not os.path.isfile(path):
        refuse(f"field absent: {path} -- run checkMesh -writeAllFields first")
    txt = open(path, "rb").read()
    k = txt.find(b"internalField")
    if k < 0:
        refuse(f"{path}: no internalField")
    seg = txt[k:]
    # `nonuniform` MUST be tested FIRST.  "uniform" is a SUFFIX of "nonuniform", so a
    # substring test for b"uniform" is TRUE for every nonuniform field -- which is
    # how this reader first refused an 18-million-value list as "unparsable uniform".
    # Same trap as the numeric prefix that made `grep -F '3.343886'` match
    # `3.3438861e-05`: a bare substring test does not respect token boundaries.
    head = seg[:80]
    if b"nonuniform" not in head and b"uniform" in head:
        m = re.search(rb"\buniform\s+([-0-9.eE+]+)", seg[:200])
        if not m:
            refuse(f"{path}: unparsable uniform internalField")
        return None, float(m.group(1))
    m = re.search(rb"\n\s*(\d+)\s*\n\s*\(", seg)
    if not m:
        refuse(f"{path}: unparsable nonuniform internalField")
    n = int(m.group(1))
    start = k + m.end()
    end = seg.find(b")", m.end())
    vals = [float(x) for x in seg[m.end():end].split()]
    if len(vals) != n:
        refuse(f"{path}: declared {n} values, parsed {len(vals)}")
    return vals, None


def extrema(vals, cflag, uniform=None):
    """(seam_min, seam_max, all_min, all_max, n_seam) over the flagged cells."""
    if vals is None:
        n = sum(cflag)
        return uniform, uniform, uniform, uniform, n
    smin = smax = None
    amin = amax = None
    n = 0
    for i, v in enumerate(vals):
        amin = v if amin is None or v < amin else amin
        amax = v if amax is None or v > amax else amax
        if cflag[i]:
            n += 1
            smin = v if smin is None or v < smin else smin
            smax = v if smax is None or v > smax else smax
    return smin, smax, amin, amax, n


# ------------------------------------------------------------------ plants ---
def plant_s_a(points_path):
    """S-A: the selector must discriminate a real plane from an impossible one."""
    at0, n = seam_points(points_path, plane_z=0.0)
    n0 = sum(at0)
    far, _ = seam_points(points_path, plane_z=1.0e9)
    nfar = sum(far)
    if n0 == 0:
        refuse("rule 3, S-A: the seam selector found ZERO points at z = 0 on a mesh "
               "mirrored about z = 0. Either the mirror did not happen or the "
               "selector is blind; a zero from a selector not shown able to see a "
               "non-zero is not evidence.")
    if nfar != 0:
        refuse(f"rule 3, S-A: the seam selector found {nfar} points at |z - 1e9| < "
               f"{SEAM_TOL}. It is not selecting on z at all.")
    return {"points_total": n, "at_z0": n0, "at_impossible_plane": nfar,
            "verdict": "PASS"}


def plant_s_b(vals, cflag, label):
    """S-B: a planted extremum at a known seam cell must come back as the extremum."""
    if vals is None:
        return {"verdict": "SKIPPED (uniform field, no per-cell values)"}
    idx = next((i for i, f in enumerate(cflag) if f), None)
    if idx is None:
        refuse("rule 3, S-B: no seam cell to plant into.")
    keep = vals[idx]
    bad = PLANT_BAD_NONORTHO if label == "nonOrthoAngle" else PLANT_BAD_VOLUME
    vals[idx] = bad
    smin, smax, _a, _b, _n = extrema(vals, cflag)
    vals[idx] = keep
    got = smax if label == "nonOrthoAngle" else smin
    if abs(got - bad) > 1e-12 * max(1.0, abs(bad)):
        refuse(f"rule 3, S-B ({label}): planted {bad} at seam cell {idx}; the "
               f"reducer returned {got}. It cannot see a planted extremum, so it "
               f"cannot be trusted to report one it was not shown.")
    return {"planted": bad, "at_cell": idx, "returned": got, "verdict": "PASS"}


# -------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser(description="A1h gate M-7, the mirror seam")
    ap.add_argument("--case", required=True)
    ap.add_argument("--fields-time", default=None,
                    help="time dir holding checkMesh -writeAllFields output")
    ap.add_argument("--n-cells", type=int, default=None,
                    help="cell count checkMesh printed, cross-checked against the "
                         "count derived from owner/neighbour")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    case = os.path.abspath(a.case)
    out = os.path.abspath(a.out)
    if out == case or out.startswith(case + os.sep):
        sys.stderr.write(f"REFUSED: --out {out} is inside the case it measures. "
                         f"This script reads only.\n")
        sys.exit(2)

    mesh = os.path.join(case, "constant", "polyMesh")
    rep = {"case": case, "mesh": mesh, "gate": "M-7 (frozen §2.1)",
           "seam_tolerance_m": SEAM_TOL,
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        rep["plant_S_A_selector"] = plant_s_a(os.path.join(mesh, "points"))
        pflag, npts = seam_points(os.path.join(mesh, "points"))
        # owner's DECLARED count is the FACE count, not the cell count.  The cell
        # count is derived as max(owner, neighbour) + 1 and then CROSS-CHECKED
        # against the count `checkMesh` printed, which is passed in: a derived
        # figure that agrees with an independently measured one is evidence; either
        # alone is a guess.  They must agree or this refuses.
        n_cells = 0
        for nm in ("owner", "neighbour"):
            fp = os.path.join(mesh, nm)
            if not os.path.isfile(fp):
                continue
            for line in stream_list(fp):
                for tok in line.split():
                    v = int(tok) + 1
                    if v > n_cells:
                        n_cells = v
        rep["n_cells_derived_from_connectivity"] = n_cells
        if a.n_cells is not None:
            rep["n_cells_from_checkMesh"] = a.n_cells
            if n_cells != a.n_cells:
                refuse(f"cell count disagreement: connectivity gives {n_cells}, "
                       f"checkMesh reported {a.n_cells}. One of the two readers is "
                       f"wrong and neither may be preferred silently.")
        rep["n_cells"] = n_cells
        cflag, n_faces = seam_cells(mesh, pflag, n_cells)
        rep["n_faces"] = n_faces
        rep["n_seam_points"] = sum(pflag)
        rep["n_seam_cells"] = sum(cflag)
        if rep["n_seam_cells"] == 0:
            refuse("no seam cells found -- the selector saw seam POINTS but no cell "
                   "carries one. Refusing rather than reporting a vacuous PASS.")

        ft = a.fields_time
        if ft is None:
            cand = [d for d in os.listdir(case)
                    if d.replace(".", "", 1).isdigit()
                    and os.path.isfile(os.path.join(case, d, "cellVolume"))]
            if not cand:
                refuse("no time directory holding `cellVolume` -- run "
                       "`checkMesh -allGeometry -allTopology -writeAllFields` first")
            ft = sorted(cand, key=float)[-1]
        rep["fields_time"] = ft

        res = {}
        for label in ("cellVolume", "nonOrthoAngle"):
            vals, uni = read_vol_scalar(os.path.join(case, ft, label))
            rep[f"plant_S_B_{label}"] = plant_s_b(vals, cflag, label)
            smin, smax, amin, amax, nseam = extrema(vals, cflag, uni)
            res[label] = {"seam_min": smin, "seam_max": smax,
                          "whole_mesh_min": amin, "whole_mesh_max": amax,
                          "n_seam_cells": nseam}
        rep["measurements"] = res

        vmin = res["cellVolume"]["seam_min"]
        nseam_max = res["nonOrthoAngle"]["seam_max"]
        nall_max = res["nonOrthoAngle"]["whole_mesh_max"]
        clauses = {
            "seam_min_volume_positive": (vmin is not None and vmin > 0.0),
            "seam_max_nonortho_within_70": (nseam_max is not None
                                            and nseam_max <= NONORTHO_MAX),
            "seam_no_worse_than_whole_mesh": (nseam_max is not None
                                              and nall_max is not None
                                              and nseam_max <= nall_max + 1e-9),
        }
        rep["M7_clauses"] = clauses
        rep["verdict"] = "PASS" if all(clauses.values()) else "GATE FAIL"
        rep["reason"] = (f"seam min cellVolume {vmin!r} m^3; seam max nonOrthoAngle "
                         f"{nseam_max!r} deg against whole-mesh {nall_max!r} deg and "
                         f"the {NONORTHO_MAX} deg ceiling")
    except Refuse as e:
        sys.stderr.write(f"REFUSED: {e}\n")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        rep["verdict"] = "BLOCKED"
        rep["refusal"] = str(e)
        json.dump(rep, open(out, "w"), indent=2, sort_keys=True)
        sys.exit(2)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rep, open(out, "w"), indent=2, sort_keys=True)
    print(f"A1h GATE M-7 -- {rep['verdict']}")
    print(f"  seam cells: {rep['n_seam_cells']} of {rep['n_cells']} "
          f"({rep['n_seam_points']} seam points of {npts})")
    for k, v in res.items():
        print(f"  {k}: seam[{v['seam_min']}, {v['seam_max']}]  "
              f"whole[{v['whole_mesh_min']}, {v['whole_mesh_max']}]")
    for k, v in clauses.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    print(f"  report: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
