#!/usr/bin/env python3
"""
DARPA SUBOFF hull + sail + four stern appendages -- BUILT-MESH FEATURE PROBE.

Measures, from a BUILT mesh, the quantities §4.3 and §5 of
verification/campaign/SUBOFF_A1f_APPENDED_VERTICAL_PLANE_PREREGISTRATION.md
registered BEFORE the mesh existed:

  RM1  "cells across the appendage root" (Sanaa's named check) -- a RATIO:
       the fin's full thickness at the root maximum-thickness station divided by
       the MEASURED median chordwise cell spacing on the fin patch in the root
       band.  It is a ratio and is labelled one: there are no cells INSIDE a
       solid fin, so a probe that tried to COUNT through the appendage would
       return zero for a perfectly good mesh.
  RM2  a direct COUNT of distinct cell-centre levels across the fin's root
       trailing-edge base, in the wake window.
  RM3  a direct COUNT of distinct cell-centre levels along the fin's exposed
       span, just off the fin surface.
  Q1   the concave-cell AREA share on each graded wall patch -- AREA, not cell
       count.  The two differ by more than a factor of twelve because concave
       cells live where the small cells are, and a cell share overstates the
       population's weight on an integrated force in the flattering direction.
  plus the layer table per patch and the checkMesh gate values.

RULE-3 PLANTED-ZERO CONTROL.  Zero is the dangerous answer here: at a fin root on
a HALF MODEL, zero is what a probe in the wrong coordinate, the wrong units or
the wrong half of the domain looks like, and it is also what a perfectly resolved
feature would NOT look like.  So a KNOWN number of synthetic cell centres is
pushed through the SAME counting function on EVERY invocation, BEFORE any mesh is
read, and the probe REFUSES (exit 2) unless the function returns exactly that
number AND returns 0 for a window that excludes the plant.  The area reader
carries its own plant for the same reason.

NEVER RUNS IN THE GRADED TREE.  It writes constant/C, which would make the rule-4
age guard unreadable.  It copies to a scratch dir and refuses if --scratch is
inside the case.

ZERO `assert` (L-332).  Refusals are sys.exit(2).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)
import os, re, json, math, shutil, argparse, subprocess
import numpy as np

PLANT_N = 13                  # known, odd, non-round
PLANT_AREA = 7.0              # m^2, known and non-round
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

FT2M = 0.3048
FIN_H_M = 13.146284 * FT2M
FIN_TIP_R_M = (5.0 / 6.0) * FT2M
FIN_ROOT_R_M = 0.08268545
FIN_CHORD_ROOT_M = 0.23228535
FIN_CHORD_TIP_M = 0.5 * FT2M
T_OVER_C_HALF_MAX = 0.10002881          # max z/c, Groves Table 3
XI_AT_MAX_T = 0.2997
FINS = {"fin000_upper_rudder": 0.0, "fin090_horizontal": 90.0,
        "fin180_lower_rudder": 180.0}


# ------------------------------------------------------------------ counting --
def count_levels(coord, lo, hi, sep):
    """Number of DISTINCT levels of `coord` inside [lo, hi].  Distinct means
    separated by more than `sep`.  This is THE counting function; the plant runs
    through this exact function and nothing else."""
    v = np.sort(coord[(coord >= lo) & (coord <= hi)])
    if v.size == 0:
        return 0
    return 1 + int(np.sum(np.diff(v) > sep))


def plant_control_count():
    xs = np.linspace(1.0e-4, 1.0e-3, PLANT_N)
    got = count_levels(xs, 0.0, 2.0e-3, 1.0e-6)
    if got != PLANT_N:
        sys.stderr.write(f"REFUSED (rule 3): planted {PLANT_N} levels and the "
                         f"counting function returned {got}.  The reader cannot be "
                         "shown able to see a non-zero; no zero it reports is "
                         "evidence.\n"); sys.exit(2)
    got0 = count_levels(xs, 10.0, 11.0, 1.0e-6)
    if got0 != 0:
        sys.stderr.write(f"REFUSED (rule 3): a window EXCLUDING the plant returned "
                         f"{got0}, not 0.  The counter is not reading its window.\n")
        sys.exit(2)
    return {"PLANT_N": PLANT_N, "returned": got,
            "excluded_window_returned": got0, "verdict": "ARMED"}


def area_share(areas, mask):
    """Fraction of total area carried by the masked faces.  THE area function;
    the area plant runs through this exact function."""
    tot = float(areas.sum())
    if tot <= 0.0:
        return None
    return float(areas[mask].sum() / tot)


def plant_control_area():
    a = np.array([1.0, 2.0, PLANT_AREA])
    m = np.array([False, False, True])
    got = area_share(a, m)
    want = PLANT_AREA / (1.0 + 2.0 + PLANT_AREA)
    if abs(got - want) > 1e-12:
        sys.stderr.write(f"REFUSED (rule 3): planted an area share of {want!r} and "
                         f"the area function returned {got!r}.\n"); sys.exit(2)
    got0 = area_share(a, np.array([False, False, False]))
    if got0 != 0.0:
        sys.stderr.write(f"REFUSED (rule 3): an EMPTY mask returned {got0!r}, "
                         "not 0.0.\n"); sys.exit(2)
    return {"PLANT_AREA": PLANT_AREA, "returned": got, "expected": want,
            "empty_mask_returned": got0, "verdict": "ARMED"}


# ------------------------------------------------------------------- readers --
def scratch_copy(case, scratch):
    if os.path.abspath(scratch).startswith(os.path.abspath(case)):
        sys.stderr.write("REFUSED: --scratch is inside the case.  This probe writes "
                         "constant/C and must never touch a graded tree.\n")
        sys.exit(2)
    work = os.path.join(scratch, "appended_probe_case")
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(os.path.join(work, "constant"))
    shutil.copytree(os.path.join(case, "constant", "polyMesh"),
                    os.path.join(work, "constant", "polyMesh"))
    shutil.copytree(os.path.join(case, "system"), os.path.join(work, "system"))
    return work


def cell_centres(work):
    cmd = (f"set +u; source {FOAM_BASHRC} '' >/dev/null 2>&1; cd {work} && "
           f"postProcess -func writeCellCentres -constant > log.writeCellCentres 2>&1")
    subprocess.run(["bash", "-lc", cmd], check=False)
    p = os.path.join(work, "constant", "C")
    if not os.path.isfile(p):
        sys.stderr.write(f"REFUSED: writeCellCentres produced no constant/C.  See "
                         f"{work}/log.writeCellCentres.\n"); sys.exit(2)
    txt = open(p).read()
    # PARSE ONLY internalField.  Measured defect inherited from the SUBOFF_A1
    # probe: slicing to EOF also swallows boundaryField and counts BOUNDARY FACE
    # centres as cells.  The rule-3 plant does NOT catch that -- it validates the
    # COUNTER, not the PARSER -- so the parse is cross-checked against the element
    # count OpenFOAM itself writes, and the probe refuses on a mismatch.
    i = txt.index("internalField"); j = txt.find("boundaryField", i)
    body = txt[i:j if j > 0 else len(txt)]
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)", body)
    vals = re.findall(r"\(([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\)", body)
    if m is None or not vals:
        sys.stderr.write("REFUSED: constant/C has no parseable internalField.\n")
        sys.exit(2)
    if len(vals) != int(m.group(1)):
        sys.stderr.write(f"REFUSED: parsed {len(vals)} cell centres but constant/C "
                         f"declares {m.group(1)}.  The parser is reading something "
                         "that is not a cell centre.\n"); sys.exit(2)
    return np.array(vals, dtype=float)


def _foam_list_ints(path):
    """Parse an OpenFOAM labelList / cellSet into an int array.

    MEASURED DEFECT, recorded rather than quietly fixed: the first version found
    the list's opening bracket by searching for "(" after the first "}" following
    "FoamFile".  On `constant/polyMesh/sets/concaveCells` that raised
    ValueError -- the header's brace structure is not what the heuristic assumed.
    A parser that guesses at a header is the same class of error as a comparator
    that guesses at a window.  This one BRACE-MATCHES the FoamFile block, so it
    does not care what is inside it, and it REFUSES if the declared element count
    and the parsed count disagree.
    """
    txt = open(path).read()
    i = txt.index("FoamFile")
    j = txt.index("{", i)
    depth = 0
    for k in range(j, len(txt)):
        if txt[k] == "{":
            depth += 1
        elif txt[k] == "}":
            depth -= 1
            if depth == 0:
                break
    body = txt[k + 1:]
    lo = body.index("("); hi = body.rindex(")")
    vals = np.fromstring(body[lo + 1:hi].replace("\n", " "), sep=" ", dtype=float)
    m = re.search(r"(\d+)\s*\(", body[:lo + 1])
    if m is not None and int(m.group(1)) != len(vals):
        sys.stderr.write(f"REFUSED: {path} declares {m.group(1)} entries and "
                         f"{len(vals)} were parsed.\n"); sys.exit(2)
    return vals.astype(np.int64)


def boundary_patches(path):
    txt = open(path).read()
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", txt):
        nm, body = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", body)
        sf = re.search(r"startFace\s+(\d+)\s*;", body)
        if nf and sf:
            out[nm] = (int(sf.group(1)), int(nf.group(1)))
    return out


def boundary_face_areas(case, patches):
    """Face-area magnitudes and owner cells for every boundary face, computed from
    points/faces/owner.  Only the boundary tail of faces/owner is needed."""
    pm = os.path.join(case, "constant", "polyMesh")
    ptxt = open(os.path.join(pm, "points")).read()
    i = ptxt.index("(", ptxt.index("}")); j = ptxt.rindex(")")
    pts = np.array(re.findall(r"\(([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\)",
                              ptxt[i:j]), dtype=float)
    ftxt = open(os.path.join(pm, "faces")).read()
    fi = ftxt.index("(", ftxt.index("}")); fj = ftxt.rindex(")")
    face_strs = re.findall(r"(\d+)\(([^)]*)\)", ftxt[fi:fj])
    owner = _foam_list_ints(os.path.join(pm, "owner"))
    start = min(s for s, _ in patches.values())
    res = {}
    for nm, (s, n) in patches.items():
        A = np.empty(n); own = owner[s:s + n]
        for k in range(n):
            cnt, idx = face_strs[s + k]
            v = pts[np.fromstring(idx, sep=" ", dtype=float).astype(np.int64)]
            c = v.mean(axis=0)
            a = np.zeros(3)
            for t in range(len(v)):
                a = a + 0.5 * np.cross(v[t] - c, v[(t + 1) % len(v)] - c)
            A[k] = np.linalg.norm(a)
        res[nm] = (A, own)
    return res, start


def concave_cells(case):
    p = os.path.join(case, "constant", "polyMesh", "sets", "concaveCells")
    if not os.path.isfile(p):
        return None
    return set(_foam_list_ints(p).tolist())


def layer_table(case):
    """Parse snappyHexMesh's final layer table: patch, faces, layers, thickness."""
    p = os.path.join(case, "log.snappyHexMesh")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    k = txt.rfind("patch")
    blk = txt[txt.rfind("----", 0, k):]
    rows = {}
    for line in blk.splitlines():
        m = re.match(r"\s*(\S+)\s+(\d+)\s+([0-9.]+)\s+([0-9.eE+-]+)\s+([0-9.]+)\s*$", line)
        if m:
            rows[m.group(1)] = {"faces": int(m.group(2)),
                                "layers_achieved": float(m.group(3)),
                                "overall_thickness_m": float(m.group(4)),
                                "overall_thickness_pct_of_target": float(m.group(5))}
    ov = re.findall(r"Overall the layer addition.*", txt)
    return {"rows": rows, "notes": ov[-3:] if ov else []}


def checkmesh_gates(case):
    p = os.path.join(case, "log.checkMesh.FULLFLAG")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    g = lambda rx: (float(re.search(rx, txt).group(1))
                    if re.search(rx, txt) else None)
    conc = re.search(r"(\d+)\s+concave cells", txt)
    return {"cells": g(r"cells:\s+(\d+)"),
            "max_non_orthogonality": g(r"non-orthogonality Max:\s*([0-9.]+)"),
            "max_skewness": g(r"Max skewness = ([0-9.]+)"),
            "max_aspect_ratio": g(r"Max aspect ratio = ([0-9.]+)"),
            "concave_cells": int(conc.group(1)) if conc else 0,
            "failed_checks_line": (re.search(r"Failed \d+ mesh checks?\.", txt).group(0)
                                   if re.search(r"Failed \d+ mesh checks?\.", txt)
                                   else "Mesh OK." if "Mesh OK." in txt else None)}


# ---------------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fin-base-root-mm", type=float, required=True)
    a = ap.parse_args()

    pc = plant_control_count()                 # rule 3, BEFORE any mesh is read
    pa = plant_control_area()
    print(f"rule-3 plants: count {pc['verdict']}, area {pa['verdict']}")

    man = json.load(open(os.path.join(a.case, "BUILD_MANIFEST.json")))
    d_fin = man["cell_sizes_m"]["fin_surface"]
    d_fte = man["cell_sizes_m"]["fin_TE_box"]

    work = scratch_copy(a.case, a.scratch)
    C = cell_centres(work)

    root_full_thk = 2.0 * T_OVER_C_HALF_MAX * FIN_CHORD_ROOT_M          # 46.47 mm
    base_root = a.fin_base_root_mm * 1e-3
    x_maxt_root = (XI_AT_MAX_T - 1.0) * FIN_CHORD_ROOT_M + FIN_H_M
    fins = {}
    for nm, az in FINS.items():
        rad = math.radians(az)
        s_hat = np.array([0.0, math.cos(rad), math.sin(rad)])
        t_hat = np.array([0.0, -math.sin(rad), math.cos(rad)])
        s = C @ s_hat; t = C @ t_hat; x = C[:, 0]

        # --- RM1: measured chordwise cell spacing on the fin in the ROOT BAND ---
        # cells hugging the fin surface, within one fin cell of it, in the first
        # 20 mm of exposed span above the hull.
        band = ((s > FIN_ROOT_R_M) & (s < FIN_ROOT_R_M + 0.020) &
                (np.abs(t) < root_full_thk) &
                (x > FIN_H_M - FIN_CHORD_ROOT_M) & (x < FIN_H_M))
        xs = np.sort(x[band])
        if xs.size < 4:
            h_chord = None; rm1 = None
        else:
            d = np.diff(xs); d = d[d > 0.2 * d_fin]
            h_chord = float(np.median(d)) if d.size else None
            rm1 = (root_full_thk / h_chord) if h_chord else None

        # --- RM2: COUNT across the root TE base, in the wake window -------------
        wake = ((x > FIN_H_M + 0.2 * d_fte) & (x < FIN_H_M + 1.6 * d_fte) &
                (s > FIN_ROOT_R_M) & (s < FIN_ROOT_R_M + 0.020))
        rm2 = count_levels(t[wake], -0.5 * base_root, 0.5 * base_root, 0.25 * d_fte)

        # --- RM3: COUNT along the exposed span, just off the fin surface --------
        off = ((x > x_maxt_root - 0.5 * d_fin) & (x < x_maxt_root + 0.5 * d_fin) &
               (np.abs(t) > 0.5 * root_full_thk) & (np.abs(t) < 0.5 * root_full_thk + 3 * d_fin))
        rm3 = count_levels(s[off], FIN_ROOT_R_M, FIN_TIP_R_M, 0.25 * d_fin)

        fins[nm] = {
            "azimuth_deg": az,
            "RM1_cells_across_the_appendage_root_RATIO": rm1,
            "RM1_floor": 16,
            "RM1_root_full_thickness_m": root_full_thk,
            "RM1_measured_chordwise_cell_spacing_m": h_chord,
            "RM2_count_across_root_TE_base": int(rm2), "RM2_floor": 8,
            "RM3_count_along_exposed_span": int(rm3), "RM3_floor": 24,
            "n_cells_in_RM1_band": int(band.sum()),
        }

    # --- Q1: concave-cell AREA share per graded wall patch ----------------------
    patches = boundary_patches(os.path.join(a.case, "constant", "polyMesh", "boundary"))
    walls = {k: v for k, v in patches.items()
             if k in ("hull", "sail") or k.startswith("fin")}
    cc = concave_cells(a.case)
    q1 = {}
    if cc is None:
        q1 = {"status": "NOT MEASURED: constant/polyMesh/sets/concaveCells absent. "
                        "checkMesh writes it only when the concave check reports "
                        "cells; absence is reported as absence, NEVER as zero."}
    else:
        areas, _ = boundary_face_areas(a.case, walls)
        tot_a = 0.0; tot_c = 0.0
        for nm, (A, own) in areas.items():
            m = np.array([int(o) in cc for o in own])
            q1[nm] = {"faces": int(A.size), "concave_owner_faces": int(m.sum()),
                      "cell_share_of_faces": float(m.mean()),
                      "Q1_AREA_share": area_share(A, m),
                      "patch_area_m2": float(A.sum())}
            tot_a += float(A.sum()); tot_c += float(A[m].sum())
        q1["ALL_GRADED_WALLS"] = {"Q1_AREA_share": tot_c / tot_a if tot_a else None,
                                  "area_m2": tot_a}

    out = {
        "case": os.path.abspath(a.case), "level": man["level"],
        "rule3_plant_count": pc, "rule3_plant_area": pa,
        "n_cells_parsed": int(C.shape[0]),
        "cell_sizes_m": man["cell_sizes_m"],
        "fins": fins,
        "Q1_concave_area_share": q1,
        "layer_table": layer_table(a.case),
        "checkMesh": checkmesh_gates(a.case),
        "NOTE": "RM1 is a RATIO (numerator = source geometry, denominator = "
                "MEASURED cell spacing).  RM2 and RM3 are COUNTS and carry the "
                "rule-3 plant.  Q1 is an AREA share, not a cell share.  Measured "
                "from a SCRATCH COPY; the graded tree was not written to.  The "
                "gate verdict is the cfd-supervisor's.",
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    for nm, r in fins.items():
        print(f"{nm}: RM1 {r['RM1_cells_across_the_appendage_root_RATIO']}, "
              f"RM2 {r['RM2_count_across_root_TE_base']}, "
              f"RM3 {r['RM3_count_along_exposed_span']}")
    print(json.dumps(out["checkMesh"], indent=1))


if __name__ == "__main__":
    main()
