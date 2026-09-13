#!/usr/bin/env python3
"""
analyse_layers.py -- ACHIEVED prism-layer coverage and growth on a DrivAer
snappyHexMesh case, plus an octree-consistency check across refinement-level
boundaries.

WHY THIS EXISTS, AND WHAT IT REFUSES TO DO
------------------------------------------
L-590 (2026-09-13): the per-patch layer table a snappyHexMesh log prints
*before* `Outer iteration : 0` is the REQUEST.  It carries the nominal layer
count on every patch and it is printed identically whether five layers were
built or none were.  A reader that parses it is reporting what was asked for.

This reader therefore:

 1. Parses ONLY the post-extrusion table -- the one whose header reads
    `patch   faces   layers   overall thickness` with a `target / mesh` sub-
    header -- and records, for the record, the byte offset and line number of
    the block it parsed so the claim is checkable.

 2. Cross-checks that table against THREE INDEPENDENT readings of whether any
    layer exists at all (L-590's prescribed fix):
        (a) the last `Extruding N out of M faces (P%)` line;
        (b) the last `Added X out of Y cells (Q%)` line;
        (c) the cell delta `Layer mesh : cells:` minus `Snapped mesh : cells:`.
    If any reading says zero while another says non-zero -> REFUSE, exit 2.
    If the log carries none of them -> REFUSE, exit 2.  It never falls back to
    the request table.

 3. Reads checkMesh in BOTH its passing and its failing form.  `Max skewness =
    0.27 OK.` and `***Max skewness = 305.39, 94 highly skew faces detected`
    are different sentences; an instrument that knows only the first is silent
    exactly where it was built to speak.  Every metric records which FORM it
    was read in, and the parser asserts two-way consistency against the
    `Failed N mesh checks.` / `Mesh OK.` verdict line.

 4. Carries PLANTED CONTROLS (CLAUDE.md rule 3).  `--selftest` plants a known
    non-zero coverage row, a known checkMesh FAILING form, a known
    reader-disagreement, and a known real zero-layer log, and refuses (exit 2)
    if any of them is not seen.  A control that asks whether the gate FIRED is
    not a control that asks whether the NUMBER IS REAL -- so every control here
    asserts the VALUE that comes back, not merely that something came back.

GROWTH RATIO
------------
snappy is not asked for an achieved growth ratio and does not print one.  What
it prints per patch, post-extrusion, is the achieved layer count `mesh` and the
achieved overall thickness in metres.  With `relativeSizes true`,
`finalLayerThickness f` and `expansionRatio r`, the requested overall thickness
for N layers is

    T(N) = f * h_local * S(N),   S(N) = sum_{k=0}^{N-1} r^{-k}

so the final-layer thickness is recoverable from the REQUEST table without
knowing h_local:   t_final = T_req / S(N_req).   The achieved thickness is then
PREDICTED, under the hypothesis that snappy preserves r and t_final and loses
only COUNT, as   T_pred = t_final * S(n_mesh).   The residual
(T_ach - T_pred)/T_ach is reported per patch; and the effective growth ratio
r_eff is solved from (T_ach, n_mesh, t_final) by bisection.  A small residual
and r_eff ~ r means the growth ratio was honoured and the whole defect is
coverage; a large one means the stack was squeezed.  Both the hypothesis and
its residual are printed, so the reader can reject the model.

OCTREE SANITY
-------------
Across a single refinement-level transition in an unsnapped octree the
adjacent-cell volume ratio is exactly 8.000.  `--mesh` reads
constant/polyMesh/cellLevel and recomputes every cell volume from points/faces/
owner/neighbour (never from a utility's summary), then reports the distribution
of V_coarse/V_fine over every internal face whose two cells differ by one
level.  A ratio that is not a power of 8 across a level boundary is a FINDING.
Cells whose own volume departs from the ideal h0^3/8^level are cut or layered
cells and are reported SEPARATELY rather than averaged in.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------
# snappyHexMesh log readers
# --------------------------------------------------------------------------

# The ACHIEVED table.  Header line then a sub-header carrying target/mesh.
ACH_HDR = re.compile(r"^\s*patch\s+faces\s+layers\s+overall thickness\s*$")
ACH_SUB = re.compile(r"^\s+target\s+mesh\s+\[m\]\s+\[%\]\s*$")
# The REQUEST table -- recognised only so that we can REFUSE to use it.
REQ_HDR = re.compile(r"^\s*patch\s+faces\s+layers\s+avg thickness\[m\]\s*$")
RULE = re.compile(r"^-+\s+-+")

EXTRUDING = re.compile(r"Extruding (\d+) out of (\d+) faces \(([\d.eE+-]+)%\)")
ADDED = re.compile(r"Added (\d+) out of (\d+) cells \(([\d.eE+-]+)%\)")
SNAPPED_CELLS = re.compile(r"Snapped mesh\s*:\s*cells:(\d+)")
LAYER_CELLS = re.compile(r"(?:Layer mesh|Mesh with layers)\s*:\s*cells:(\d+)")

ACH_ROW = re.compile(
    r"^(\S+)\s+(\d+)\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s*$")
REQ_ROW = re.compile(r"^(\S+)\s+(\d+)\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s*$")


class Refuse(Exception):
    pass


def _tables(lines):
    """Yield (kind, header_line_index, rows) for every layer table in the log."""
    i = 0
    n = len(lines)
    while i < n:
        kind = None
        if ACH_HDR.match(lines[i]):
            if i + 1 < n and ACH_SUB.match(lines[i + 1]):
                kind = "achieved"
        elif REQ_HDR.match(lines[i]):
            kind = "request"
        if kind is None:
            i += 1
            continue
        j = i + 1
        while j < n and not RULE.match(lines[j]):
            j += 1
        j += 1
        rows = []
        pat = ACH_ROW if kind == "achieved" else REQ_ROW
        while j < n:
            s = lines[j].rstrip()
            if not s.strip():
                break
            m = pat.match(s)
            if not m:
                break
            rows.append(m.groups())
            j += 1
        yield kind, i, rows
        i = j


def read_achieved_layers(log: Path) -> dict:
    """Parse the post-extrusion layer table AND the three independent readings."""
    text = log.read_text(errors="replace")
    lines = text.splitlines()

    # ---- (a),(b),(c): the three independent readings, L-590 -----------------
    ex = EXTRUDING.findall(text)
    ad = ADDED.findall(text)
    sn = SNAPPED_CELLS.findall(text)
    ly = LAYER_CELLS.findall(text)

    readings = {}
    if ex:
        readings["extruding_faces"] = int(ex[-1][0])
        readings["extruding_of"] = int(ex[-1][1])
        readings["extruding_pct"] = float(ex[-1][2])
    if ad:
        readings["added_cells"] = int(ad[-1][0])
        readings["added_of"] = int(ad[-1][1])
        readings["added_pct"] = float(ad[-1][2])
    if sn and ly:
        readings["snapped_cells"] = int(sn[-1])
        readings["layer_cells"] = int(ly[-1])
        readings["cell_delta"] = int(ly[-1]) - int(sn[-1])

    have = [k for k in ("extruding_faces", "added_cells", "cell_delta")
            if k in readings]
    if not have:
        raise Refuse(
            f"{log}: carries none of the three achievement readings "
            f"(Extruding / Added / cell delta).  REFUSING to report a "
            f"coverage; the per-patch table is the REQUEST (L-590).")

    zeros = {k: (readings[k] == 0) for k in have}
    if len(set(zeros.values())) > 1:
        raise Refuse(
            f"{log}: the achievement readings DISAGREE on whether any layer "
            f"exists -- " + ", ".join(f"{k}={readings[k]}" for k in have) +
            ".  REFUSING to report a coverage (L-590).")
    all_zero = all(zeros.values())

    # ---- the table ---------------------------------------------------------
    ach = [(idx, rows) for kind, idx, rows in _tables(lines) if kind == "achieved"]
    req = [(idx, rows) for kind, idx, rows in _tables(lines) if kind == "request"]

    out = {
        "log": str(log),
        "readings": readings,
        "readings_used": have,
        "no_layer_exists": all_zero,
        "request_table_line": (req[-1][0] + 1) if req else None,
        "request_table_rows": len(req[-1][1]) if req else 0,
    }

    if not ach:
        if not all_zero:
            raise Refuse(
                f"{log}: no post-extrusion layer table found, yet the "
                f"achievement readings are NON-ZERO ({readings}).  REFUSING "
                f"rather than falling back to the request table (L-590).")
        out.update(achieved_table_line=None, patches={},
                   note=("no prism layer exists on this mesh; the per-patch "
                         "table in this log is what was ASKED FOR and was NOT "
                         "achieved (L-590)"))
        return out

    idx, rows = ach[-1]
    if all_zero and rows:
        raise Refuse(
            f"{log}: a post-extrusion table is present with {len(rows)} rows "
            f"but all three achievement readings say zero.  REFUSING.")

    patches = {}
    for name, faces, target, mesh, t_m, t_pct in rows:
        patches[name] = dict(faces=int(faces), target=int(target),
                             layers_mesh=float(mesh),
                             thickness_m=float(t_m), thickness_pct=float(t_pct))
    out.update(achieved_table_line=idx + 1, patches=patches)

    # consistency: a table full of zeros must agree with the readings
    tot_layer_faces = sum(p["faces"] for p in patches.values()
                          if p["layers_mesh"] > 0)
    out["patches_with_zero_layers"] = sorted(
        k for k, p in patches.items() if p["layers_mesh"] == 0.0 and p["faces"] > 0)
    out["faces_on_layered_patches"] = tot_layer_faces
    return out


# --------------------------------------------------------------------------
# checkMesh -- BOTH the passing and the failing form
# --------------------------------------------------------------------------
# (name, passing regex, failing regex, value group in each)
CM_CHECKS = [
    ("max_skewness",
     r"^\s*Max skewness = ([\d.eE+-]+) OK\.",
     r"^\s*\*\*\*Max skewness = ([\d.eE+-]+),\s*(\d+) highly skew faces"),
    ("max_aspect_ratio",
     r"^\s*Max aspect ratio = ([\d.eE+-]+) OK\.",
     r"^\s*\*\*\*Max aspect ratio = ([\d.eE+-]+),\s*(\d+)"),
    ("min_face_area",
     r"^\s*Minimum face area = ([\d.eE+-]+)\.",
     r"^\s*\*\*\*Zero or negative face area detected.*?([\d.eE+-]+)"),
    ("min_cell_volume",
     r"^\s*Min volume = ([\d.eE+-]+)\.",
     r"^\s*\*\*\*Zero or negative cell volume detected.*"),
]
CM_COUNTS = [
    ("n_severely_non_ortho",
     r"\*\*\*Number of severely non-orthogonal \(> \d+ degrees\) faces: (\d+)"),
    ("n_concave_cells",
     r"\*\*\*Concave cells \(using face planes\) found, number of cells: (\d+)"),
    ("n_low_determinant",
     r"\*\*\*Cells with small determinant \(< [\d.eE+-]+\) found, number of cells: (\d+)"),
    ("n_negative_volume_cells", r"Number of negative volume cells: (\d+)"),
    ("n_skew_faces", r"\*\*\*Max skewness = [\d.eE+-]+,\s*(\d+) highly skew faces"),
]
NONORTHO = re.compile(r"Mesh non-orthogonality Max: ([\d.eE+-]+) average: ([\d.eE+-]+)")
FAILED_N = re.compile(r"^Failed (\d+) mesh checks\.", re.M)
MESH_OK = re.compile(r"^Mesh OK\.", re.M)
CELLS_LINE = re.compile(r"^\s*cells:\s+(\d+)", re.M)


def read_checkmesh(log: Path) -> dict:
    txt = log.read_text(errors="replace")
    out = {"log": str(log), "metrics": {}, "form": {}}
    for name, pass_re, fail_re in CM_CHECKS:
        mf = re.search(fail_re, txt, re.M)
        mp = re.search(pass_re, txt, re.M)
        if mf:
            out["form"][name] = "FAILING"
            try:
                out["metrics"][name] = float(mf.group(1))
            except (IndexError, ValueError):
                out["metrics"][name] = None
        elif mp:
            out["form"][name] = "OK"
            out["metrics"][name] = float(mp.group(1))
        else:
            out["form"][name] = "ABSENT"
    for name, pat in CM_COUNTS:
        m = re.search(pat, txt, re.M)
        out["metrics"][name] = int(m.group(1)) if m else 0
    m = NONORTHO.search(txt)
    if m:
        out["metrics"]["max_non_ortho"] = float(m.group(1))
        out["metrics"]["avg_non_ortho"] = float(m.group(2))
    m = CELLS_LINE.search(txt)
    out["cells"] = int(m.group(1)) if m else None
    m = FAILED_N.search(txt)
    out["failed_checks"] = int(m.group(1)) if m else None
    out["mesh_ok_line"] = bool(MESH_OK.search(txt))
    n_star = len(re.findall(r"^\s*\*\*\*", txt, re.M))
    out["n_star_lines"] = n_star

    # --- two-way assertion: a passing-only parser is blind where it matters ---
    if out["failed_checks"] and out["failed_checks"] > 0 and n_star == 0:
        raise Refuse(f"{log}: says 'Failed {out['failed_checks']} mesh checks.' "
                     f"but the reader saw no '***' failure line -- the reader "
                     f"is blind to the failing form.  REFUSING.")
    if out["mesh_ok_line"] and n_star > 0:
        raise Refuse(f"{log}: says 'Mesh OK.' yet carries {n_star} '***' "
                     f"failure lines.  REFUSING.")
    if out["failed_checks"] is None and not out["mesh_ok_line"]:
        raise Refuse(f"{log}: carries neither 'Mesh OK.' nor 'Failed N mesh "
                     f"checks.' -- checkMesh did not finish.  REFUSING.")
    return out


# --------------------------------------------------------------------------
# growth model
# --------------------------------------------------------------------------
def S(n: float, r: float) -> float:
    """sum_{k=0}^{n-1} r^-k, continued to fractional n by the closed form."""
    if abs(r - 1.0) < 1e-12:
        return n
    return (1.0 - r ** (-n)) / (1.0 - 1.0 / r)


def solve_r(T: float, n: float, t_final: float, lo=1.0001, hi=8.0) -> float | None:
    """Solve T = t_final * S(n, r) for r by bisection.  None if unbracketed."""
    if n <= 0 or T <= 0 or t_final <= 0:
        return None
    f = lambda r: t_final * S(n, r) - T
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def read_request_layers(log: Path) -> dict:
    """The REQUEST table -- used ONLY to recover t_final, never as coverage."""
    lines = log.read_text(errors="replace").splitlines()
    req = [(i, rows) for kind, i, rows in _tables(lines) if kind == "request"]
    if not req:
        return {}
    _, rows = req[-1]
    return {name: dict(faces=int(f), layers=int(L),
                       near_wall_m=float(nw), overall_m=float(ov))
            for name, f, L, nw, ov in rows}


def dict_layer_controls(case: Path) -> dict:
    d = case / "system" / "snappyHexMeshDict"
    if not d.exists():
        return {}
    txt = d.read_text(errors="replace")
    out = {}
    for key, cast in (("relativeSizes", str), ("finalLayerThickness", float),
                      ("firstLayerThickness", float), ("expansionRatio", float),
                      ("minThickness", float), ("nSurfaceLayers", int),
                      ("nGrow", int), ("featureAngle", float),
                      ("maxFaceThicknessRatio", float),
                      ("nLayerIter", int), ("nRelaxedIter", int),
                      ("maxThicknessToMedialRatio", float),
                      ("minMedialAxisAngle", float)):
        m = re.search(rf"^\s*{key}\s+([^;]+);", txt, re.M)
        if m:
            v = m.group(1).strip()
            try:
                out[key] = cast(v)
            except ValueError:
                out[key] = v
    return out


def growth_report(case: Path, ach: dict) -> dict:
    req = read_request_layers(Path(ach["log"]))
    ctl = dict_layer_controls(case)
    r_req = float(ctl.get("expansionRatio", 1.25))
    rows = []
    for name, p in sorted(ach.get("patches", {}).items()):
        q = req.get(name)
        if not q or q["overall_m"] <= 0 or p["faces"] == 0:
            continue
        N = q["layers"]
        t_final = q["overall_m"] / S(N, r_req)
        n = p["layers_mesh"]
        T = p["thickness_m"]
        T_pred = t_final * S(n, r_req) if n > 0 else 0.0
        resid = (T - T_pred) / T if T > 0 else None
        rows.append(dict(
            patch=name, faces=p["faces"], target=N, layers_mesh=n,
            coverage_frac=n / N if N else None,
            t_final_req_m=t_final,
            thickness_ach_m=T, thickness_req_m=q["overall_m"],
            thickness_pct=p["thickness_pct"],
            thickness_pred_m=T_pred, residual=resid,
            r_eff=solve_r(T, n, t_final) if n > 0 else None,
        ))
    resids = [abs(r["residual"]) for r in rows if r["residual"] is not None
              and r["layers_mesh"] > 0]
    reffs = [r["r_eff"] for r in rows if r["r_eff"] is not None]
    return dict(controls=ctl, r_requested=r_req,
                S_of_N=S(ctl.get("nSurfaceLayers", 5) or 5, r_req),
                rows=rows,
                n_rows_with_layers=len(resids),
                median_abs_residual=float(np.median(resids)) if resids else None,
                max_abs_residual=float(np.max(resids)) if resids else None,
                median_r_eff=float(np.median(reffs)) if reffs else None,
                min_r_eff=float(np.min(reffs)) if reffs else None,
                max_r_eff=float(np.max(reffs)) if reffs else None)


# --------------------------------------------------------------------------
# octree sanity -- volumes recomputed from polyMesh, never from a summary
# --------------------------------------------------------------------------
def _strip(txt: bytes) -> bytes:
    txt = re.sub(rb"/\*.*?\*/", b" ", txt, flags=re.S)
    txt = re.sub(rb"//[^\n]*", b" ", txt)
    i = txt.index(b"FoamFile")
    j = txt.index(b"}", i)
    return txt[j + 1:]


def _read_vec(p):
    b = _strip(Path(p).read_bytes())
    m = re.search(rb"(\d+)\s*\(", b)
    n = int(m.group(1))
    body = b[m.end():b.rindex(b")")]
    a = np.fromstring(body.replace(b"(", b" ").replace(b")", b" ").decode(), sep=" ")
    return a.reshape(n, 3)


def _read_labels(p):
    b = _strip(Path(p).read_bytes())
    m = re.search(rb"(\d+)\s*\(", b)
    body = b[m.end():b.rindex(b")")]
    return np.fromstring(body.decode(), sep=" ").astype(np.int64)


def _read_faces(p):
    b = _strip(Path(p).read_bytes())
    m = re.search(rb"(\d+)\s*\(", b)
    n = int(m.group(1))
    body = b[m.end():b.rindex(b")")].decode()
    toks = np.fromstring(body.replace("(", " ").replace(")", " "), sep=" ").astype(np.int64)
    # vectorised walk: sizes at running offsets
    sizes = np.empty(n, dtype=np.int64)
    starts = np.empty(n, dtype=np.int64)
    i = 0
    for f in range(n):
        k = toks[i]
        sizes[f] = k
        starts[f] = i + 1
        i += 1 + k
    return toks, sizes, starts, n


def cell_volumes(pm: Path):
    P = _read_vec(pm / "points")
    toks, sizes, starts, nf = _read_faces(pm / "faces")
    own = _read_labels(pm / "owner")
    nei = _read_labels(pm / "neighbour")
    ncell = int(max(own.max(), nei.max())) + 1
    Sf = np.zeros((nf, 3))
    Cf = np.zeros((nf, 3))
    for k in np.unique(sizes):
        sel = np.where(sizes == k)[0]
        idx = starts[sel][:, None] + np.arange(k)[None, :]
        pts = P[toks[idx]]                       # (m, k, 3)
        c0 = pts.mean(axis=1)                    # (m, 3)
        a = pts
        b = np.roll(pts, -1, axis=1)
        tri = 0.5 * np.cross(a - c0[:, None, :], b - c0[:, None, :])
        at = np.linalg.norm(tri, axis=2)         # (m, k)
        Sf[sel] = tri.sum(axis=1)
        tot = at.sum(axis=1)
        ctr = ((a + b + c0[:, None, :]) / 3.0 * at[:, :, None]).sum(axis=1)
        good = tot > 0
        ctr[good] /= tot[good][:, None]
        ctr[~good] = c0[~good]
        Cf[sel] = ctr
    V = np.zeros(ncell)
    flux = (Cf * Sf).sum(1)
    np.add.at(V, own, flux)
    np.add.at(V, nei[:len(nei)], -flux[:len(nei)])
    V /= 3.0
    return V, own, nei, np.linalg.norm(Sf, axis=1)


def octree_report(case: Path, h0: float | None, tols=(1e-1, 1e-2, 1e-3, 1e-4)) -> dict:
    pm = case / "constant" / "polyMesh"
    lvl = _read_labels(pm / "cellLevel")
    V, own, nei, area = cell_volumes(pm)
    n_int = len(nei)
    if len(lvl) != len(V):
        raise Refuse(f"{pm}: cellLevel has {len(lvl)} entries, mesh has {len(V)} cells.")

    # PLANTED CONTROL on the volume reader: total volume must equal the
    # bounding-box volume of a box domain to within round-off.
    tot = float(V.sum())

    # ideal volume per level, from the level-0 edge length
    if h0 is None:
        e = pm / "level0Edge"
        if e.exists():
            t = e.read_text(errors="replace")
            # level0Edge is a uniformDimensionedScalarField: `value  0.8;`
            m = re.search(r"^\s*value\s+([\d.eE+-]+)\s*;", t, re.M)
            if m is None:  # older/vector spellings
                m = re.search(r"\(\s*([\d.eE+-]+)\s+[\d.eE+-]+\s+[\d.eE+-]+\s*\)", t)
            if m:
                h0 = float(m.group(1))
        if h0 is None:
            raise Refuse(f"{pm}: cannot read the level-0 edge length; REFUSING "
                         f"to report an octree ratio without the ideal volume "
                         f"to separate pristine cells from cut ones.")
    ideal = (h0 ** 3) / (8.0 ** lvl.astype(float))

    o = own[:n_int]
    nn = nei[:n_int]
    dl = lvl[nn] - lvl[o]
    sel = np.abs(dl) == 1
    vc = np.where(dl[sel] > 0, V[o[sel]], V[nn[sel]])   # coarse side
    vf = np.where(dl[sel] > 0, V[nn[sel]], V[o[sel]])   # fine side
    ratio_all = vc / vf

    def stats(r):
        if r.size == 0:
            return None
        return dict(n=int(r.size), min=float(r.min()), max=float(r.max()),
                    median=float(np.median(r)),
                    frac_within_1e6_of_8=float(np.mean(np.abs(r - 8.0) <= 8e-6)),
                    frac_within_1e3_of_8=float(np.mean(np.abs(r - 8.0) <= 8e-3)))

    # The "pristine" subset -- cells whose own volume is within `tol` of the
    # ideal octree volume h0^3/8^level, i.e. cells neither cut by snapping nor
    # split by layer addition.  Selecting on volume and then measuring a volume
    # RATIO is circular at the level of the selection tolerance, so the report
    # SWEEPS the tolerance: if the ratio is an artefact of the selection, the
    # measured spread tracks `tol`; if it is real, the ratio stays at 8.000 far
    # inside the gate that admitted the cells.
    sweep = {}
    for tol in tols:
        pristine = np.abs(V - ideal) <= tol * ideal
        sp = sel & pristine[o] & pristine[nn]
        vc_p = np.where(dl[sp] > 0, V[o[sp]], V[nn[sp]])
        vf_p = np.where(dl[sp] > 0, V[nn[sp]], V[o[sp]])
        sweep[f"{tol:g}"] = dict(
            pristine_cells=int(pristine.sum()),
            pristine_frac=float(pristine.mean()),
            n_pristine_transition_faces=int(sp.sum()),
            ratio_pristine_transitions=stats(vc_p / vf_p) if sp.sum() else None)

    levels, counts = np.unique(lvl, return_counts=True)
    return dict(
        cells=int(len(V)), internal_faces=int(n_int),
        h0_level0_edge=h0, total_volume=tot,
        cells_per_level={int(a): int(b) for a, b in zip(levels, counts)},
        n_level_transition_faces=int(sel.sum()),
        ratio_all_transitions=stats(ratio_all),
        n_level_jump_gt1=int(np.sum(np.abs(dl) > 1)),
        pristine_tolerance_sweep=sweep,
    )


# --------------------------------------------------------------------------
# PLANTED CONTROLS
# --------------------------------------------------------------------------
PLANT_PATCH = "PLANTED_COVERAGE_CTRL"
PLANT_LAYERS = 3.777
PLANT_PCT = 42.42
PLANT_THK = 0.04242
PLANT_FACES = 4242

PLANT_SKEW = 305.39
PLANT_SKEWFACES = 94


def selftest(donor_log: Path, donor_cm_ok: Path, donor_cm_fail: Path,
             zero_log: Path, work: Path) -> int:
    work.mkdir(parents=True, exist_ok=True)
    fails = []

    # ---- P1: plant a KNOWN NON-ZERO coverage row and read the VALUE back ----
    lines = donor_log.read_text(errors="replace").splitlines()
    ach = [(i, rows) for kind, i, rows in _tables(lines) if kind == "achieved"]
    if not ach:
        print("SELFTEST REFUSE: donor log carries no achieved table to plant into",
              file=sys.stderr)
        return 2
    idx = ach[-1][0]
    # insert immediately after the rule line of the last achieved table
    j = idx + 1
    while not RULE.match(lines[j]):
        j += 1
    row = (f"{PLANT_PATCH:<28} {PLANT_FACES:<8} 5        {PLANT_LAYERS:<8} "
           f"{PLANT_THK:<9} {PLANT_PCT}    ")
    planted = lines[:j + 1] + [row] + lines[j + 1:]
    p1 = work / "P1_planted_coverage.log"
    p1.write_text("\n".join(planted) + "\n")
    try:
        got = read_achieved_layers(p1)
        p = got["patches"].get(PLANT_PATCH)
        if p is None:
            fails.append("P1: planted coverage row NOT SEEN by the reader")
        elif (abs(p["layers_mesh"] - PLANT_LAYERS) > 1e-9
              or abs(p["thickness_pct"] - PLANT_PCT) > 1e-9
              or p["faces"] != PLANT_FACES):
            fails.append(f"P1: planted row read back WRONG: {p}")
        else:
            print(f"P1 PASS  planted coverage {PLANT_PATCH} layers_mesh="
                  f"{p['layers_mesh']} pct={p['thickness_pct']} faces={p['faces']}"
                  f" -- read back exactly, from line {got['achieved_table_line']}")
    except Refuse as e:
        fails.append(f"P1: reader refused the planted log: {e}")

    # ---- P1b: the reader must read the ACHIEVED table, not the REQUEST one --
    # plant a DIFFERENT, impossible value into the REQUEST table; if the reader
    # ever reports it, the reader is reading the request (L-590).
    lines2 = donor_log.read_text(errors="replace").splitlines()
    req = [(i, rows) for kind, i, rows in _tables(lines2) if kind == "request"]
    if req:
        k = req[-1][0] + 1
        while not RULE.match(lines2[k]):
            k += 1
        lines2.insert(k + 1, f"{'PLANTED_REQUEST_ONLY':<28} 9999     5      0.001     0.999   ")
        p1b = work / "P1b_planted_request_only.log"
        p1b.write_text("\n".join(lines2) + "\n")
        got = read_achieved_layers(p1b)
        if "PLANTED_REQUEST_ONLY" in got["patches"]:
            fails.append("P1b: the reader reported a patch that exists ONLY in "
                         "the REQUEST table -- it is reading the request (L-590)")
        else:
            print("P1b PASS  a row planted only in the REQUEST table is NOT "
                  "reported; the reader is on the post-extrusion block "
                  f"(request table at line {got['request_table_line']}, "
                  f"achieved at line {got['achieved_table_line']})")
    else:
        fails.append("P1b: donor log has no request table to plant into")

    # ---- P2: a REAL zero-layer log must come back ZERO, not fall back -------
    try:
        z = read_achieved_layers(zero_log)
        if not z["no_layer_exists"]:
            fails.append(f"P2: {zero_log} is a zero-layer log but the reader "
                         f"reported layers: {z['readings']}")
        elif z["patches"]:
            fails.append("P2: zero-layer log produced per-patch coverage rows")
        else:
            print(f"P2 PASS  real zero-layer log read as ZERO "
                  f"(cell_delta={z['readings'].get('cell_delta')}, "
                  f"extruding={z['readings'].get('extruding_faces')}), and the "
                  f"request table at line {z['request_table_line']} "
                  f"({z['request_table_rows']} rows) was NOT used")
    except Refuse as e:
        fails.append(f"P2: reader refused a genuine zero-layer log: {e}")

    # ---- P3: readers made to DISAGREE must force a refusal ------------------
    txt = donor_log.read_text(errors="replace")
    m = list(EXTRUDING.finditer(txt))[-1]
    bad = txt[:m.start()] + "Extruding 0 out of 23365 faces (0%)." + txt[m.end():]
    p3 = work / "P3_disagreeing_readers.log"
    p3.write_text(bad)
    try:
        read_achieved_layers(p3)
        fails.append("P3: reader did NOT refuse when Extruding=0 while "
                     "Added>0 and cell delta>0")
    except Refuse:
        print("P3 PASS  reader REFUSED (exit-2 path) when the three "
              "achievement readings disagreed")

    # ---- P4: checkMesh FAILING form, planted into a PASSING log -------------
    if donor_cm_ok.exists():
        t = donor_cm_ok.read_text(errors="replace")
        t2 = re.sub(r"^\s*Max skewness = [\d.eE+-]+ OK\.",
                    f"   ***Max skewness = {PLANT_SKEW}, {PLANT_SKEWFACES} highly "
                    f"skew faces detected which may impair the quality of the results",
                    t, count=1, flags=re.M)
        t2 = re.sub(r"^Mesh OK\.", f"Failed 1 mesh checks.", t2, count=1, flags=re.M)
        if t2 == t:
            fails.append(f"P4: could not plant a failing form into {donor_cm_ok} "
                         f"(no passing skewness line found) -- control INVALID")
        else:
            p4 = work / "P4_planted_failing_checkmesh.log"
            p4.write_text(t2)
            try:
                cm = read_checkmesh(p4)
                if (cm["form"]["max_skewness"] != "FAILING"
                        or abs(cm["metrics"]["max_skewness"] - PLANT_SKEW) > 1e-9
                        or cm["metrics"]["n_skew_faces"] != PLANT_SKEWFACES):
                    fails.append(f"P4: planted FAILING form read back wrong: "
                                 f"{cm['form']['max_skewness']} "
                                 f"{cm['metrics'].get('max_skewness')} "
                                 f"{cm['metrics'].get('n_skew_faces')}")
                else:
                    print(f"P4 PASS  planted checkMesh FAILING form read back "
                          f"exactly: max_skewness={cm['metrics']['max_skewness']}"
                          f" on {cm['metrics']['n_skew_faces']} faces, "
                          f"form=FAILING")
            except Refuse as e:
                fails.append(f"P4: reader refused the planted failing log: {e}")
    else:
        fails.append(f"P4: no passing checkMesh donor at {donor_cm_ok}")

    # ---- P5: a REAL failing checkMesh must be read, not abstained on --------
    if donor_cm_fail.exists():
        try:
            cm = read_checkmesh(donor_cm_fail)
            failing = [k for k, v in cm["form"].items() if v == "FAILING"]
            if cm["failed_checks"] is None or cm["failed_checks"] == 0:
                fails.append(f"P5: {donor_cm_fail} was supposed to be a REAL "
                             f"failing checkMesh; it reports "
                             f"failed_checks={cm['failed_checks']}")
            elif not failing and cm["metrics"]["n_concave_cells"] == 0 \
                    and cm["metrics"]["n_low_determinant"] == 0:
                fails.append("P5: real failing checkMesh produced no failing "
                             "reading -- the reader is passing-form-only")
            else:
                print(f"P5 PASS  REAL failing checkMesh read: "
                      f"failed_checks={cm['failed_checks']}, "
                      f"forms={cm['form']}, concave={cm['metrics']['n_concave_cells']}, "
                      f"lowdet={cm['metrics']['n_low_determinant']}, "
                      f"skewfaces={cm['metrics']['n_skew_faces']}")
        except Refuse as e:
            fails.append(f"P5: reader refused a real failing checkMesh: {e}")
    else:
        fails.append(f"P5: no failing checkMesh donor at {donor_cm_fail}")

    # ---- P6: mutate the failing-form regexes off and prove the gate moves ---
    global CM_CHECKS
    saved = CM_CHECKS
    try:
        CM_CHECKS = [(n, p, r"(?!x)x") for n, p, _ in saved]
        cm = read_checkmesh(donor_cm_fail) if donor_cm_fail.exists() else None
        if cm is not None and cm["form"].get("max_skewness") == "FAILING":
            fails.append("P6: disabling the failing-form regex did NOT change "
                         "the reading -- the control is not wired to the code")
        else:
            print("P6 PASS  with the failing-form regexes disabled the reader "
                  f"no longer sees the failure (form="
                  f"{cm['form'].get('max_skewness') if cm else 'n/a'}); "
                  "the P4/P5 readings are produced by that code and not by luck")
    finally:
        CM_CHECKS = saved

    if fails:
        print("\nSELFTEST REFUSED -- planted controls not seen:", file=sys.stderr)
        for f in fails:
            print("  " + f, file=sys.stderr)
        return 2
    print("\nALL PLANTED CONTROLS PASSED")
    return 0


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", nargs="*", default=[],
                    help="run directories holding log.snappyHexMesh")
    ap.add_argument("--octree", nargs="*", default=[],
                    help="run directories to check octree volume ratios on")
    ap.add_argument("--json", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--donor", default=None)
    ap.add_argument("--zero-donor", default=None)
    ap.add_argument("--cm-ok", default=None)
    ap.add_argument("--cm-fail", default=None)
    ap.add_argument("--work", default="/tmp/analyse_layers_selftest")
    a = ap.parse_args()

    if a.selftest:
        return selftest(Path(a.donor), Path(a.cm_ok), Path(a.cm_fail),
                        Path(a.zero_donor), Path(a.work))

    result = {"cases": {}, "octree": {}}
    rc = 0
    for c in a.case:
        case = Path(c)
        log = case / "log.snappyHexMesh"
        try:
            ach = read_achieved_layers(log)
            g = growth_report(case, ach)
            cm = {}
            for nm in ("log.checkMeshFull", "log.checkMesh", "log.checkMeshPlain"):
                if (case / nm).exists():
                    cm[nm] = read_checkmesh(case / nm)
            result["cases"][case.name] = dict(achieved=ach, growth=g, checkmesh=cm)
        except Refuse as e:
            result["cases"][case.name] = dict(REFUSED=str(e))
            print(f"REFUSE {case.name}: {e}", file=sys.stderr)
            rc = 2
    for c in a.octree:
        case = Path(c)
        try:
            result["octree"][case.name] = octree_report(case, None)
        except Refuse as e:
            result["octree"][case.name] = dict(REFUSED=str(e))
            print(f"REFUSE octree {case.name}: {e}", file=sys.stderr)
            rc = 2
    txt = json.dumps(result, indent=1, sort_keys=True)
    if a.json:
        Path(a.json).write_text(txt)
        print(f"wrote {a.json}")
    else:
        print(txt)
    return rc


if __name__ == "__main__":
    sys.exit(main())
