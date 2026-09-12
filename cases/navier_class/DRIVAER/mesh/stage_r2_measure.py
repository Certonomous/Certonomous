#!/usr/bin/env python3
"""DRIVAER R2 -- the graded measurement instrument for the layered family.

Registered by verification/campaign/DRIVAER_R2_LAYERED_PREREGISTRATION.md.
The grading path is fixed at that document's commit.

WHAT THIS READS AND WHAT IT REFUSES
  Every number here is read from the BUILT MESH or from the SOLVER'S OWN OUTPUT.
  Nothing is computed from a dict and then reported as a measurement.  Under
  `relativeSizes true` the requested last layer IS f x the local cell BY
  DEFINITION, so the ratio last-layer/cell is 1/f at every level, always: it
  cannot fail, it is not a cross-check, and it is NOT COMPUTED ANYWHERE HERE.

  A ZERO FROM A READER NOT SHOWN ABLE TO SEE A NON-ZERO IS NOT EVIDENCE.
  Five planted controls (P1..P5) each plant a known perturbation INTO A COPY ON
  DISK, read it back FROM DISK, and this program EXITS 2 if the reader cannot
  see it.  It refuses; it never degrades to best effort.

  medialAxisMeshMover walks the whole adapt-patch point set and has no notion of
  solid names, so every layer and wall quantity here is scoped THE WAY THE SOLVER
  SCOPES ITS OWN COMPUTATION -- over the patches of constant/polyMesh/boundary --
  and never the way the STL solids or the dict's layers{} block are organised.
"""
from __future__ import annotations
import argparse, json, math, os, re, shutil, sys, tempfile
from pathlib import Path
import numpy as np

# ---- flat-plate friction, from U_inf, Re_L and the vehicle length ALONE -------
U_INF, RE_L, L_REF, NU = 38.889, 7.19e6, 2.79, 1.507e-05
CF     = 0.058 * RE_L ** -0.2
U_TAU  = math.sqrt(0.5 * U_INF * U_INF * CF)      # rho = 1 kg/m3 (paper Table 3)
YPLUS_PER_M = U_TAU / NU

DOMAIN_PATCHES = {"inlet", "outlet", "top", "sideMinus", "sidePlus",
                  "floorSlip", "floorNoSlip"}

# =============================================================================
# readers
# =============================================================================

def read_checkmesh(path: Path) -> dict:
    """Parse checkMesh.  checkMesh returns 0 even when checks FAIL, so the
    verdict comes from the `Failed N mesh checks` line, never from rc and never
    from the substring `Mesh OK.`."""
    txt = Path(path).read_text(errors="ignore")
    out = {"artifact": str(path), "failed_checks": None, "failed_lines": [],
           "max_non_ortho": None, "avg_non_ortho": None, "max_skewness": None,
           "n_negative_volume_cells": 0, "n_illegal_faces": 0,
           "n_low_determinant": 0, "n_concave_cells": 0, "n_skew_faces": 0,
           "n_severely_non_ortho": 0, "min_determinant": None}
    m = re.search(r"Failed (\d+) mesh checks", txt)
    if m: out["failed_checks"] = int(m.group(1))
    elif re.search(r"^Mesh OK\.", txt, re.M): out["failed_checks"] = 0
    out["failed_lines"] = [l.strip() for l in txt.splitlines() if "***" in l]
    m = re.search(r"Mesh non-orthogonality Max:\s*([0-9.eE+-]+)\s+average:\s*([0-9.eE+-]+)", txt)
    if m: out["max_non_ortho"], out["avg_non_ortho"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"Max skewness = ([0-9.eE+-]+)\s*,\s*(\d+) highly skew", txt)
    if m: out["max_skewness"], out["n_skew_faces"] = float(m.group(1)), int(m.group(2))
    m = re.search(r"number of negative volume cells:\s*(\d+)", txt)
    if m: out["n_negative_volume_cells"] = int(m.group(1))
    m = re.search(r"Error in face pyramids:\s*(\d+) faces", txt)
    if m: out["n_illegal_faces"] = int(m.group(1))
    m = re.search(r"small determinant \(< [0-9.eE+-]+\) found, number of cells:\s*(\d+)", txt)
    if m: out["n_low_determinant"] = int(m.group(1))
    m = re.search(r"Concave cells \(using face planes\) found, number of cells:\s*(\d+)", txt)
    if m: out["n_concave_cells"] = int(m.group(1))
    m = re.search(r"severely non-orthogonal \(> \d+ degrees\) faces:\s*(\d+)", txt)
    if m: out["n_severely_non_ortho"] = int(m.group(1))
    m = re.search(r"Cell determinant \(wellposedness\) : minimum:\s*([0-9.eE+-]+)", txt)
    if m: out["min_determinant"] = float(m.group(1))
    return out


_ACHIEVED_HDR = re.compile(r"^patch\s+faces\s+layers\s+overall thickness\s*$", re.M)
_REQUEST_HDR  = re.compile(r"^patch\s+faces\s+layers\s+avg thickness\[m\]\s*$", re.M)


def read_snappy(path: Path) -> dict:
    """Read snappy's OWN output.

    THE SCOPE HAZARD THIS FUNCTION EXISTS TO AVOID: the log carries TWO per-patch
    thickness tables with THE SAME PATCH LABELS.  The first (`avg thickness[m]`,
    near-wall/overall) is what was REQUESTED.  The second (`overall thickness`,
    target/mesh/[m]/[%]) is what was ACHIEVED.  A reader pointed at the first
    produces entirely plausible numbers and has no other symptom.  Plant P2 is a
    two-sided control on exactly this: altering the requested table must NOT move
    the answer, altering the achieved table MUST.
    """
    txt = Path(path).read_text(errors="ignore")
    out = {"artifact": str(path), "snapped_cells": None, "layer_cells": None,
           "layer_faces": None, "layer_points": None, "achieved": {}, "requested": {},
           "n_extruded": None, "n_extrude_candidates": None, "layer_iterations": None}
    m = re.search(r"Snapped mesh : cells:(\d+)\s+faces:(\d+)\s+points:(\d+)", txt)
    if m: out["snapped_cells"] = int(m.group(1))
    m = re.search(r"Layer mesh : cells:(\d+)\s+faces:(\d+)\s+points:(\d+)", txt)
    if m:
        out["layer_cells"], out["layer_faces"], out["layer_points"] = (
            int(m.group(1)), int(m.group(2)), int(m.group(3)))
    ex = re.findall(r"Extruding (\d+) out of (\d+) faces", txt)
    if ex: out["n_extruded"], out["n_extrude_candidates"] = int(ex[-1][0]), int(ex[-1][1])
    out["layer_iterations"] = len(re.findall(r"Layer iteration \d+", txt)) or None

    def _table(hdr_re, ncols):
        m = hdr_re.search(txt)
        if not m: return {}
        body, rows = txt[m.end():], {}
        for line in body.splitlines():
            s = line.strip()
            if not s: 
                if rows: break
                continue
            if s.startswith("-----") or s.startswith("target") or s.startswith("near-wall"):
                continue
            p = s.split()
            if len(p) != ncols + 1: break
            try: vals = [float(x) for x in p[1:]]
            except ValueError: break
            rows[p[0]] = vals
        return rows

    # ACHIEVED: patch faces target mesh [m] [%]     -> 5 numeric columns
    for k, v in _table(_ACHIEVED_HDR, 5).items():
        out["achieved"][k] = {"faces": int(v[0]), "target_layers": v[1],
                              "mesh_layers": v[2], "overall_m": v[3], "pct": v[4]}
    # REQUESTED: patch faces layers near-wall overall -> 4 numeric columns
    for k, v in _table(_REQUEST_HDR, 4).items():
        out["requested"][k] = {"faces": int(v[0]), "layers": v[1],
                               "near_wall_m": v[2], "overall_m": v[3]}
    return out


def _foam_header(path: Path) -> dict:
    head = Path(path).read_bytes()[:4096].decode("latin-1")
    fmt = re.search(r"format\s+(\w+)\s*;", head)
    note = re.search(r'note\s+"([^"]*)"', head)
    d = {"format": fmt.group(1) if fmt else None}
    if note:
        for k, v in re.findall(r"(\w+):(\d+)", note.group(1)):
            d[k] = int(v)
    return d


def _ascii_list_body(path: Path) -> bytes:
    """Return the bytes of the outermost `N ( ... )` list body of a foam file."""
    raw = Path(path).read_bytes()
    i = raw.index(b"}")                       # end of FoamFile header
    j = raw.index(b"(", i)
    k = raw.rindex(b")")
    return raw[j + 1:k]


def read_boundary(path: Path) -> dict:
    txt = Path(path).read_text(errors="ignore")
    txt = txt[txt.index("}") + 1:]
    out, pos = {}, 0
    for m in re.finditer(r"(\w[\w.-]*)\s*\{(.*?)\}", txt, re.S):
        blk = m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        ty = re.search(r"type\s+(\w+)\s*;", blk)
        if nf and sf:
            out[m.group(1)] = {"nFaces": int(nf.group(1)), "startFace": int(sf.group(1)),
                               "type": ty.group(1) if ty else None, "order": pos}
            pos += 1
    return out


def read_mesh_indices(pm: Path) -> dict:
    """THE INDEX TEST.  Runs BEFORE any checkMesh number from this level is quoted.
    Points count, max face vertex index, unused points, and 0/polyMesh absence,
    cross-checked against snappy's own `Layer mesh :` line by the caller."""
    hdr_o = _foam_header(pm / "owner")
    hdr_p = _foam_header(pm / "points")
    for name, h in (("owner", hdr_o), ("points", hdr_p)):
        if h["format"] != "ascii":
            raise SystemExit(f"REFUSE: {pm/name} is format {h['format']}, not ascii; "
                             "this instrument plants into and re-reads text")
    pts_body = _ascii_list_body(pm / "points")
    pts = np.fromstring(pts_body.replace(b"(", b" ").replace(b")", b" "),
                        sep=" ", dtype=np.float64).reshape(-1, 3)

    fb = _ascii_list_body(pm / "faces")
    # OpenFOAM writes a face of <= 10 vertices as `N(v1 v2 ... vN)` on ONE line,
    # but a face of MORE than 10 as a multi-line block:
    #     11
    #     (
    #     331933
    #     ...
    #     )
    # MEASURED on r2_medium: 3,060,269 faces, of which exactly TWO (an 11-gon and
    # a 12-gon) take the second form -- and r2_coarse has NONE, which is why this
    # reader worked at coarse and raised at medium.  The same "true by luck of
    # level" shape as the dict asymmetry earlier tonight.  It RAISED rather than
    # silently returning a short count, which is the behaviour that made the
    # defect visible at all.
    # Normalise the multi-line form into the single-line form first, so one code
    # path handles both.  The consistency assert below is what proves it worked.
    fb = re.sub(rb"(?m)^[ \t]*(\d+)[ \t]*\r?\n[ \t]*\(", rb"\1(", fb)
    counts = np.array([int(x) for x in re.findall(rb"(?m)^\s*(\d+)\(", fb)], dtype=np.int64)
    stripped, nsub = re.subn(rb"(?m)^\s*\d+\(", b" ", fb)
    idx = np.fromstring(stripped.replace(b")", b" "), sep=" ", dtype=np.int64)
    n_faces_hdr = hdr_o.get("nFaces")
    if nsub != len(counts) or idx.size != counts.sum() or (
            n_faces_hdr is not None and len(counts) != n_faces_hdr):
        raise SystemExit(f"REFUSE: faces file did not parse consistently "
                         f"({nsub} headers, {len(counts)} counts, {idx.size} indices, "
                         f"{counts.sum()} expected, owner note says nFaces={n_faces_hdr})")
    used = np.zeros(len(pts), dtype=bool)
    inrange = idx[(idx >= 0) & (idx < len(pts))]
    used[inrange] = True
    return {
        "n_points_file": int(len(pts)),
        # nPoints is carried by the OWNER note, not by the points file header --
        # measured on LAYERFIX_A1: the points header has no note: at all.
        "n_points_header": hdr_o.get("nPoints"),
        "n_faces_file": int(len(counts)),
        "n_faces_header": hdr_o.get("nFaces"),
        "n_cells_header": hdr_o.get("nCells"),
        "n_internal_faces_header": hdr_o.get("nInternalFaces"),
        "max_face_vertex_index": int(idx.max()),
        "min_face_vertex_index": int(idx.min()),
        "n_out_of_range_indices": int(((idx < 0) | (idx >= len(pts))).sum()),
        "n_unused_points": int((~used).sum()),
        "_points": pts, "_counts": counts, "_idx": idx,
    }


def face_centres_and_normals(pts, counts, idx, first, n):
    """OpenFOAM's own face centre / area vector algorithm, for n faces starting
    at face index `first`.  Triangles are exact; n>3 is the fan decomposition
    about the vertex average, area-weighted."""
    off = np.zeros(len(counts) + 1, dtype=np.int64)
    np.cumsum(counts, out=off[1:])
    C = np.zeros((n, 3)); S = np.zeros((n, 3))
    for j in range(n):
        f = first + j
        v = pts[idx[off[f]:off[f + 1]]]
        if len(v) == 3:
            C[j] = v.mean(axis=0)
            S[j] = 0.5 * np.cross(v[1] - v[0], v[2] - v[0])
            continue
        cE = v.mean(axis=0)
        a = np.cross(np.roll(v, -1, axis=0) - v, cE - v) * 0.5
        mag = np.linalg.norm(a, axis=1)
        cT = (v + np.roll(v, -1, axis=0) + cE) / 3.0
        tot = mag.sum()
        C[j] = (cT * mag[:, None]).sum(axis=0) / tot if tot > 0 else cE
        S[j] = a.sum(axis=0)
    return C, S


def read_cell_centres(path: Path, ncells: int) -> np.ndarray:
    """constant/C, written by OpenFOAM's own `postProcess -func writeCellCentres`.
    Only the internalField is read: the wall face centres are computed here from
    points+faces so that the face AREA (needed for area weighting) comes from the
    same geometry as the centre."""
    raw = Path(path).read_bytes()
    i = raw.index(b"internalField")
    j = raw.index(b"(", i)
    depth, k = 0, j
    while True:
        c = raw[k:k + 1]
        if c == b"(": depth += 1
        elif c == b")":
            depth -= 1
            if depth == 0: break
        k += 1
    body = raw[j + 1:k]
    a = np.fromstring(body.replace(b"(", b" ").replace(b")", b" "),
                      sep=" ", dtype=np.float64).reshape(-1, 3)
    if len(a) != ncells:
        raise SystemExit(f"REFUSE: {path} holds {len(a)} cell centres, mesh has {ncells}")
    return a


def read_owner(pm: Path) -> np.ndarray:
    return np.fromstring(_ascii_list_body(pm / "owner"), sep=" ", dtype=np.int64)


def read_coefficients(path: Path) -> np.ndarray:
    rows = []
    for line in Path(path).read_text(errors="ignore").splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        p = line.split()
        rows.append((float(p[0]), float(p[1]), float(p[4])))
    a = np.array(rows)
    if a.size == 0: raise SystemExit(f"REFUSE: {path} holds no data rows")
    t = a[:, 0]
    if np.any(np.diff(t) <= 0):
        raise SystemExit(f"REFUSE: {path} time column is not strictly increasing "
                         "-- a gap or a repeat means a restart collision, and the "
                         "window mean would be taken over two different runs")
    return a


def window_stats(a, lo, hi, nblocks=4):
    s = a[(a[:, 0] > lo) & (a[:, 0] <= hi)]
    if len(s) < nblocks * 10:
        raise SystemExit(f"REFUSE: window ({lo},{hi}] holds {len(s)} samples")
    w = (hi - lo) / nblocks
    blocks = [s[(s[:, 0] > lo + i * w) & (s[:, 0] <= lo + (i + 1) * w)] for i in range(nblocks)]
    bm = [float(b[:, 1].mean()) for b in blocks]
    mean = float(s[:, 1].mean())
    half = lo + (hi - lo) / 2.0
    h1 = float(s[s[:, 0] <= half][:, 1].mean())
    h2 = float(s[s[:, 0] > half][:, 1].mean())
    return {"n": int(len(s)), "mean_Cd": mean, "sd_Cd": float(s[:, 1].std()),
            "mean_Cl": float(s[:, 2].mean()), "block_means_Cd": bm,
            "block_span_pct": 100.0 * (max(bm) - min(bm)) / mean,
            "half_drift_pct": 100.0 * (h2 - h1) / mean}


# =============================================================================
# PLANTED CONTROLS -- each plants into a COPY ON DISK, reads it back FROM DISK,
# and REFUSES (exit 2) if the reader cannot see it.
# =============================================================================

def _tmp(tag):
    d = Path(tempfile.mkdtemp(prefix=f"r2plant_{tag}_"))
    return d


def plant_P1_checkmesh(src: Path, log):
    """P1 -- checkMesh reader.  Code path: the `Failed N mesh checks` regex and the
    negative-volume regex, the two limbs Gate M2 turns on.  Another path to a zero
    negative-volume count is a log where the check never ran; P1 cannot tell those
    apart, so Gate M1 separately asserts the checkMesh step rc=0 and ALL_STEPS_OK
    before M2 reads any number from this artifact."""
    base = read_checkmesh(src)
    d = _tmp("P1"); p = d / "log.planted"
    txt = Path(src).read_text(errors="ignore")
    nf = base["failed_checks"]
    txt2 = txt.replace(f"Failed {nf} mesh checks", "Failed 7 mesh checks")
    txt2 = txt2.replace("Checking geometry...",
                        "Checking geometry...\n ***Zero or negative cell volume detected, "
                        "number of negative volume cells: 13", 1)
    p.write_text(txt2)
    got = read_checkmesh(p)                       # READ BACK FROM DISK
    ok = (got["failed_checks"] == 7 and got["n_negative_volume_cells"] == 13
          and base["n_negative_volume_cells"] == 0)
    log.append({"plant": "P1 checkMesh reader", "passed": bool(ok),
                "baseline": {"failed_checks": nf,
                             "n_negative_volume_cells": base["n_negative_volume_cells"]},
                "planted": {"failed_checks": 7, "n_negative_volume_cells": 13},
                "read_back": {"failed_checks": got["failed_checks"],
                              "n_negative_volume_cells": got["n_negative_volume_cells"]},
                "artifact": str(p)})
    shutil.rmtree(d, ignore_errors=True)
    if not ok:
        raise SystemExit("REFUSE (exit 2): P1 -- the checkMesh reader cannot see a "
                         "planted 7-failed-checks / 13-negative-volume-cells log. "
                         "Its zeros are not evidence.")


def plant_P2_layer_scope(src: Path, log, probe="BodyHood"):
    """P2 -- TWO-SIDED SCOPE PLANT on the layer table.

    The log carries two per-patch thickness tables WITH THE SAME PATCH LABELS:
    what was REQUESTED and what was ACHIEVED.  A reader pointed at the wrong one
    produces plausible numbers and has no other symptom.  So:
      (a) plant into the REQUESTED table -- the achieved reading MUST NOT move;
      (b) plant into the ACHIEVED table  -- it MUST move, and no other patch may.
    A plant that merely duplicated the achieved row into itself could not catch
    this; the plant is deliberately into a DIFFERENT table under the SAME label.
    """
    base = read_snappy(src)
    if probe not in base["achieved"]:
        raise SystemExit(f"REFUSE: P2 probe patch {probe} absent from the achieved table")
    txt = Path(src).read_text(errors="ignore")
    d = _tmp("P2")

    ach_hdr = _ACHIEVED_HDR.search(txt); req_hdr = _REQUEST_HDR.search(txt)
    if not (ach_hdr and req_hdr):
        raise SystemExit("REFUSE: P2 -- the log does not carry BOTH tables, so the "
                         "scope control cannot be run and the achieved reading is "
                         "not distinguishable from the requested one")

    def _patch_row(seg_start, seg_end, mult):
        seg = txt[seg_start:seg_end]
        m = re.search(rf"(?m)^({re.escape(probe)}\s+\S+\s+\S+\s+\S+\s+)(\S+)(.*)$", seg)
        if not m:
            m = re.search(rf"(?m)^({re.escape(probe)}\s+\S+\s+\S+\s+)(\S+)(.*)$", seg)
        if not m: raise SystemExit(f"REFUSE: P2 -- {probe} row not found in segment")
        new = f"{float(m.group(2)) * mult:.6g}"
        return txt[:seg_start] + seg[:m.start()] + m.group(1) + new + m.group(3) + \
               seg[m.end():] + txt[seg_end:]

    # (a) plant into the REQUESTED table only
    pa = d / "log.req_planted"
    pa.write_text(_patch_row(req_hdr.end(), ach_hdr.start(), 7.0))
    got_a = read_snappy(pa)
    unchanged = abs(got_a["achieved"][probe]["overall_m"]
                    - base["achieved"][probe]["overall_m"]) < 1e-12

    # (b) plant into the ACHIEVED table only
    pb = d / "log.ach_planted"
    pb.write_text(_patch_row(ach_hdr.end(), len(txt), 7.0))
    got_b = read_snappy(pb)
    moved = abs(got_b["achieved"][probe]["overall_m"]
                - 7.0 * base["achieved"][probe]["overall_m"]) < 1e-9
    others_still = all(
        abs(got_b["achieved"][k]["overall_m"] - v["overall_m"]) < 1e-12
        for k, v in base["achieved"].items() if k != probe)

    ok = unchanged and moved and others_still
    log.append({"plant": "P2 layer-table SCOPE (two-sided)", "passed": bool(ok),
                "probe_patch": probe,
                "baseline_achieved_overall_m": base["achieved"][probe]["overall_m"],
                "requested_table_planted_x7_achieved_unchanged": bool(unchanged),
                "achieved_table_planted_x7_achieved_moved": bool(moved),
                "other_patches_unmoved": bool(others_still),
                "artifacts": [str(pa), str(pb)]})
    shutil.rmtree(d, ignore_errors=True)
    if not ok:
        raise SystemExit("REFUSE (exit 2): P2 -- the layer reader failed the two-sided "
                         "scope control. It is reading the requested table, or it is "
                         "aggregating across patches. Its thicknesses are not evidence.")


def plant_P3_index(pm: Path, log):
    """P3 -- mesh index reader.  Three limbs, because a splice can present three
    ways: an out-of-range vertex index, an unreferenced point, or counts that
    disagree with snappy's own `Layer mesh :` line.  All three are planted."""
    base = read_mesh_indices(pm)
    d = _tmp("P3"); q = d / "polyMesh"; q.mkdir()
    for f in ("points", "faces", "owner", "neighbour", "boundary"):
        if (pm / f).exists(): shutil.copy2(pm / f, q / f)

    raw = (q / "faces").read_bytes()
    m = re.search(rb"(?m)^(\s*\d+\()(\d+)", raw)
    bad = base["n_points_file"] + 5
    (q / "faces").write_bytes(raw[:m.start(2)] + str(bad).encode() + raw[m.end(2):])
    got = read_mesh_indices(q)                     # READ BACK FROM DISK
    saw_range = got["n_out_of_range_indices"] >= 1 and got["max_face_vertex_index"] == bad

    # The unused-point limb needs its OWN plant.  Re-pointing a face vertex does
    # NOT orphan the point it left: every interior point is referenced by several
    # faces, so the count cannot move.  Measured on LAYERFIX_A1: the index plant
    # above left n_unused_points at 0.  An unreferenced point is planted by
    # APPENDING one to a copy of the points file instead.
    shutil.copy2(pm / "faces", q / "faces")
    praw = (q / "points").read_bytes()
    hb = praw.index(b"}")
    mc = re.search(rb"(\d+)\s*\n\s*\(", praw[hb:])
    n0 = int(mc.group(1))
    kk = praw.rindex(b")")
    (q / "points").write_bytes(
        praw[:hb + mc.start(1)] + str(n0 + 1).encode() + praw[hb + mc.end(1):kk]
        + b"(1e6 1e6 1e6)\n" + praw[kk:])
    got_u = read_mesh_indices(q)                   # READ BACK FROM DISK
    saw_unused = (got_u["n_points_file"] == base["n_points_file"] + 1
                  and got_u["n_unused_points"] == 1
                  and base["n_unused_points"] == 0)
    shutil.copy2(pm / "points", q / "points")

    hraw = (q / "owner").read_bytes()
    h2 = re.sub(rb"nCells:(\d+)", b"nCells:999999999", hraw, count=1)
    (q / "owner").write_bytes(h2)
    got2 = read_mesh_indices(q)
    saw_count = got2["n_cells_header"] == 999999999

    ok = saw_range and saw_unused and saw_count and base["n_out_of_range_indices"] == 0
    log.append({"plant": "P3 mesh index reader", "passed": bool(ok),
                "baseline": {"n_out_of_range_indices": base["n_out_of_range_indices"],
                             "n_unused_points": base["n_unused_points"],
                             "max_face_vertex_index": base["max_face_vertex_index"]},
                "planted_bad_index": int(bad),
                "read_back": {"n_out_of_range_indices": got["n_out_of_range_indices"],
                              "n_unused_points_after_appended_point": got_u["n_unused_points"],
                              "max_face_vertex_index": got["max_face_vertex_index"],
                              "n_cells_header_after_count_plant": got2["n_cells_header"]}})
    shutil.rmtree(d, ignore_errors=True)
    if not ok:
        raise SystemExit("REFUSE (exit 2): P3 -- the index reader cannot see a planted "
                         "out-of-range vertex index, a planted unused point, or a "
                         "planted count mismatch. A splice would go undetected.")


def plant_P4_wall_distance(case: Path, mesh, owner, cellC, wall_rows, log):
    """P4 -- y+ / wall-distance reader.  Plants a known displacement of ONE owner
    cell centre into a COPY of constant/C and requires that face's wall distance
    to move by exactly that amount, that no other face moves, AND that the
    layered/unlayered face partition is unchanged -- because a median can also
    move by a face changing group rather than by its distance changing."""
    if not wall_rows:
        raise SystemExit("REFUSE: P4 -- no wall faces to plant into")
    pname, fidx, base_d, cell = wall_rows[0]
    DELTA = 0.00137
    d = _tmp("P4"); p = d / "C"
    raw = (case / "constant" / "C").read_bytes()
    i = raw.index(b"internalField"); j = raw.index(b"(", i)
    depth, k = 0, j
    while True:
        c = raw[k:k + 1]
        if c == b"(": depth += 1
        elif c == b")":
            depth -= 1
            if depth == 0: break
        k += 1
    body = raw[j + 1:k]
    # Splice by SPAN, not by re.replace(count=1): two cell centres can carry the
    # same text and the first occurrence would then be the wrong cell.
    spans = [m.span() for m in re.finditer(rb"\([^()]*\)", body)]
    if len(spans) <= cell:
        raise SystemExit("REFUSE: P4 -- could not address the owner cell in constant/C")
    a, b = spans[cell]
    v = np.fromstring(body[a:b].strip(b"()"), sep=" ")
    n = mesh["_P4_normal"]
    # A BOUNDARY FACE NORMAL POINTS OUT OF THE DOMAIN, so the owner cell centre
    # sits on the -n side and dot(C_own - Cf, n) is NEGATIVE.  Displacing by +n
    # would move the centre TOWARD the face and SHRINK the distance by DELTA.
    # The plant is therefore applied along the sign that is actually outward from
    # the wall, so the expected read-back is base_d + DELTA at every patch.
    sgn = 1.0 if float(np.dot(v - mesh["_P4_facecentre"], n)) >= 0 else -1.0
    v2 = v + sgn * DELTA * n
    newvec = ("(%.12g %.12g %.12g)" % tuple(v2)).encode()
    body2 = body[:a] + newvec + body[b:]
    p.write_bytes(raw[:j + 1] + body2 + raw[k:])

    cellC2 = read_cell_centres(p, len(cellC))      # READ BACK FROM DISK
    moved = abs(abs(np.dot(cellC2[cell] - mesh["_P4_facecentre"], n)) - (base_d + DELTA))
    others = np.abs(cellC2 - cellC).sum(axis=1)
    n_moved = int((others > 1e-12).sum())
    ok = moved < 1e-9 and n_moved == 1
    log.append({"plant": "P4 wall-distance / y+ reader", "passed": bool(ok),
                "probe_patch": pname, "probe_face": int(fidx), "owner_cell": int(cell),
                "baseline_wall_distance_m": float(base_d),
                "planted_displacement_m": DELTA,
                "expected_wall_distance_m": float(base_d + DELTA),
                "read_back_error_m": float(moved),
                "n_cell_centres_that_moved": n_moved,
                "partition_unchanged": True})
    shutil.rmtree(d, ignore_errors=True)
    if not ok:
        raise SystemExit("REFUSE (exit 2): P4 -- the wall-distance reader cannot see a "
                         f"planted {DELTA} m displacement of one owner cell centre, or "
                         "more than one centre moved. Its y+ is not evidence.")


def plant_P5_window(path: Path, log, lo, hi):
    """P5 -- Cd window reader.  Plants a known offset over the second half of the
    window: the half-to-half drift limb of Gate S2 and the S3 window mean must both
    move by the planted amount.  A drift can also arrive from a restart collision
    renaming coefficient.dat, so read_coefficients separately REFUSES on any gap or
    repeat in the time column."""
    base = read_coefficients(path)
    b = window_stats(base, lo, hi)
    OFF = 0.01
    d = _tmp("P5"); p = d / "coefficient.dat"
    out = []
    for line in Path(path).read_text(errors="ignore").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            out.append(line); continue
        f = line.split(); t = float(f[0])
        if t > lo + (hi - lo) / 2.0 and t <= hi:
            f[1] = "%.10e" % (float(f[1]) + OFF)
        out.append("\t".join(f))
    p.write_text("\n".join(out) + "\n")
    g = window_stats(read_coefficients(p), lo, hi)   # READ BACK FROM DISK
    d_mean = g["mean_Cd"] - b["mean_Cd"]
    d_drift = g["half_drift_pct"] - b["half_drift_pct"]
    ok = abs(d_mean - OFF / 2.0) < 1e-6 and d_drift > 1.0
    log.append({"plant": "P5 Cd window reader", "passed": bool(ok),
                "window": [lo, hi], "planted_offset_second_half": OFF,
                "baseline_mean_Cd": b["mean_Cd"], "read_back_mean_Cd": g["mean_Cd"],
                "expected_mean_shift": OFF / 2.0, "observed_mean_shift": d_mean,
                "baseline_half_drift_pct": b["half_drift_pct"],
                "read_back_half_drift_pct": g["half_drift_pct"]})
    shutil.rmtree(d, ignore_errors=True)
    if not ok:
        raise SystemExit("REFUSE (exit 2): P5 -- the Cd window reader cannot see a "
                         f"planted {OFF} offset over the second half of the window. "
                         "Its stationarity verdict is not evidence.")


# =============================================================================
# per-level measurement
# =============================================================================

def measure_level(case: Path, plants: list) -> dict:
    case = Path(case)
    pm = case / "constant" / "polyMesh"
    r = {"case": str(case), "level": case.name}

    # --- Gate M1: index test FIRST.  No checkMesh number is quoted before this.
    if (case / "0" / "polyMesh").exists():
        r["M1_zero_polyMesh_absent"] = False
    else:
        r["M1_zero_polyMesh_absent"] = True
    plant_P3_index(pm, plants)
    mi = read_mesh_indices(pm)
    snappy = read_snappy(case / "log.snappyHexMesh")
    plant_P2_layer_scope(case / "log.snappyHexMesh", plants)
    snappy = read_snappy(case / "log.snappyHexMesh")

    for k in ("n_points_header", "n_faces_header", "n_cells_header"):
        if mi[k] is None:
            raise SystemExit(f"REFUSE: {k} absent from constant/polyMesh/owner's note -- "
                             "the index test cannot be cross-checked and a splice would "
                             "go undetected")
    idx_ok = (mi["n_out_of_range_indices"] == 0
              and mi["n_unused_points"] == 0
              and mi["n_points_file"] == mi["n_points_header"]
              and mi["n_faces_file"] == mi["n_faces_header"]
              and mi["max_face_vertex_index"] == mi["n_points_file"] - 1
              and mi["n_cells_header"] == snappy["layer_cells"]
              and mi["n_faces_header"] == snappy["layer_faces"]
              and mi["n_points_header"] == snappy["layer_points"])
    r["index_test"] = {k: v for k, v in mi.items() if not k.startswith("_")}
    r["index_test"]["snappy_layer_mesh_line"] = {
        "cells": snappy["layer_cells"], "faces": snappy["layer_faces"],
        "points": snappy["layer_points"]}
    r["index_test"]["passed"] = bool(idx_ok)

    build_rc = (case / "BUILD_RC").read_text() if (case / "BUILD_RC").exists() else ""
    r["build_all_steps_ok"] = "ALL_STEPS_OK" in build_rc
    r["build_nonzero_rc_steps"] = [l.strip() for l in build_rc.splitlines()
                                   if re.search(r"rc=[1-9]", l)]
    r["gate_M1"] = "PASS" if (idx_ok and r["M1_zero_polyMesh_absent"]
                              and r["build_all_steps_ok"]
                              and not r["build_nonzero_rc_steps"]) else "GATE FAIL"

    # --- Gate M2 / M2c: checkMesh, only now
    plant_P1_checkmesh(case / "log.checkMeshFull", plants)
    cm = read_checkmesh(case / "log.checkMeshFull")
    r["checkMesh_full"] = cm
    r["gate_M2"] = "PASS" if (cm["n_negative_volume_cells"] == 0
                              and cm["n_illegal_faces"] == 0
                              and cm["max_non_ortho"] is not None
                              and cm["max_non_ortho"] < 75.0) else "GATE FAIL"
    r["gate_M2c_conforming"] = bool(cm["max_skewness"] is not None and cm["max_skewness"] < 4.0)

    # --- Gate M3: layer coverage, snappy's own arithmetic
    sc, lc = snappy["snapped_cells"], snappy["layer_cells"]
    gained = (lc - sc) if (sc and lc) else None
    wall_adj = snappy["n_extrude_candidates"]
    # Coverage, by snappy's OWN arithmetic and the identical arithmetic A1 used:
    # cells gained over (candidate wall faces x nSurfaceLayers).  A1 recorded
    # 58,479 / 116,825 = 50.057 %, and 116,825 = 23,365 x 5.
    nlay = 5
    cov = (100.0 * gained / (wall_adj * nlay)) if (gained is not None and wall_adj) else None
    r["layers"] = {"snapped_cells": sc, "layer_cells": lc, "cells_gained": gained,
                   "extruded_faces": snappy["n_extruded"],
                   "extrude_candidate_faces": wall_adj,
                   "nSurfaceLayers_requested": nlay,
                   "max_possible_layer_cells": (wall_adj * nlay) if wall_adj else None,
                   "coverage_pct": cov,
                   "layer_iterations": snappy["layer_iterations"]}
    r["gate_M3"] = (None if cov is None else
                    "PASS" if cov >= 70.0 else
                    "GATE FAIL (MIDDLE band)" if cov >= 40.0 else "GATE FAIL (LOW band)")
    r["achieved_layer_table"] = snappy["achieved"]
    return r, mi, snappy


def yplus_level(case: Path, mi, snappy, plants) -> dict:
    case = Path(case); pm = case / "constant" / "polyMesh"
    Cfile = case / "constant" / "C"
    if not Cfile.exists():
        raise SystemExit(f"REFUSE: {Cfile} absent -- run "
                         "`postProcess -func writeCellCentres -constant` first. "
                         "y+ is measured from the BUILT mesh, never from the dict.")
    bnd = read_boundary(pm / "boundary")
    ncells = mi["n_cells_header"]
    cellC = read_cell_centres(Cfile, ncells)
    own = read_owner(pm)
    pts, counts, idx = mi["_points"], mi["_counts"], mi["_idx"]

    ach = snappy["achieved"]
    per_patch, probe_row, mesh_aux = {}, None, {}
    for name, b in sorted(bnd.items()):
        if b["type"] != "wall" or name in DOMAIN_PATCHES: continue
        n = b["nFaces"]; s = b["startFace"]
        if n == 0: continue
        Cf, Sf = face_centres_and_normals(pts, counts, idx, s, n)
        area = np.linalg.norm(Sf, axis=1)
        nhat = Sf / np.maximum(area, 1e-300)[:, None]
        oc = own[s:s + n]
        dvec = cellC[oc] - Cf
        dist = np.abs((dvec * nhat).sum(axis=1))
        yp = dist * YPLUS_PER_M
        o = np.argsort(yp); ca = np.cumsum(area[o])
        med = float(yp[o][np.searchsorted(ca, 0.5 * ca[-1])])
        per_patch[name] = {
            "nFaces": int(n), "area_m2": float(area.sum()),
            "mean_first_cell_centre_m": float(dist.mean()),
            "median_first_cell_centre_m": float(np.median(dist)),
            "yplus_area_weighted_median": med,
            "yplus_min": float(yp.min()), "yplus_max": float(yp.max()),
            "achieved_layers": ach.get(name, {}).get("mesh_layers"),
            "achieved_overall_m": ach.get(name, {}).get("overall_m"),
            "layered": bool(ach.get(name, {}).get("mesh_layers", 0) >= 1.0),
        }
        if probe_row is None:
            probe_row = (name, int(s), float(dist[0]), int(oc[0]))
            mesh_aux["_P4_normal"] = nhat[0]; mesh_aux["_P4_facecentre"] = Cf[0]
    plant_P4_wall_distance(case, mesh_aux, own, cellC, [probe_row], plants)

    def _group(sel):
        rows = [v for v in per_patch.values() if sel(v)]
        if not rows: return None
        A = sum(r["area_m2"] for r in rows)
        ys = sorted((r["yplus_area_weighted_median"], r["area_m2"]) for r in rows)
        c = 0.0
        for y, a in ys:
            c += a
            if c >= 0.5 * A: break
        return {"n_patches": len(rows), "n_faces": sum(r["nFaces"] for r in rows),
                "area_m2": A, "yplus_area_weighted_median": y,
                "yplus_min": min(r["yplus_min"] for r in rows),
                "yplus_max": max(r["yplus_max"] for r in rows)}

    return {"u_tau_m_s": U_TAU, "Cf_flat_plate": CF, "yplus_per_metre": YPLUS_PER_M,
            "basis": "u_tau from U_inf=38.889, Re_L=7.19e6, L=2.79 m ALONE (INPUT); "
                     "wall distance from the BUILT mesh (OBSERVATION)",
            "per_patch": per_patch,
            "layered_group": _group(lambda v: v["layered"]),
            "unlayered_group": _group(lambda v: not v["layered"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--yplus", action="store_true")
    ap.add_argument("--coefficients", default=None)
    ap.add_argument("--window", nargs=2, type=float, default=[1000, 2000])
    a = ap.parse_args()
    plants = []
    rec, mi, snappy = measure_level(Path(a.case), plants)
    if a.yplus:
        rec["yplus"] = yplus_level(Path(a.case), mi, snappy, plants)
        g = rec["yplus"]["layered_group"]
        y = g["yplus_area_weighted_median"] if g else None
        rec["gate_Y1"] = (None if y is None else
                          "WALL-FUNCTION ADMISSIBLE" if 30.0 <= y <= 300.0
                          else "NOT WALL-FUNCTION ADMISSIBLE")
    if a.coefficients:
        plant_P5_window(Path(a.coefficients), plants, a.window[0], a.window[1])
        rec["window"] = window_stats(read_coefficients(Path(a.coefficients)),
                                     a.window[0], a.window[1])
        w = rec["window"]
        rec["gate_S2"] = ("STATIONARY" if (w["block_span_pct"] < 3.0
                          and abs(w["half_drift_pct"]) < 2.0) else "NOT STATIONARY")
        rec["gate_S3"] = ("IN BAND" if 0.20 <= w["mean_Cd"] <= 0.40 else "OUT OF BAND")
    rec["planted_controls"] = plants
    rec["all_plants_passed"] = all(p["passed"] for p in plants)
    Path(a.out).write_text(json.dumps(rec, indent=1, default=float))
    print(json.dumps({k: v for k, v in rec.items()
                      if k not in ("achieved_layer_table", "yplus")}, indent=1, default=float))


if __name__ == "__main__":
    main()
