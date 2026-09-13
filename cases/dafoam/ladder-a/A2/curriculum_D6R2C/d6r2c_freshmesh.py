#!/usr/bin/env python3
# ===========================================================================
# d6r2c_freshmesh.py -- ITEM 9 PRODUCER: a FRESH mesh on the final shape
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEMS.md sections 2, 4 and 5, and IN THE
# SAME COMMIT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# THIS FILE PRODUCES NUMBERS.  IT GRADES NOTHING.  H1-H4 live in
# d6r2c_after_grade.py, which recomputes the weighted drag from the
# per-condition CD and the frozen weights rather than trusting the J here.
#
# THREE PHASES, THREE PROCESSES, run in this order by d6r2c_after_run_arm.sh:
#
#   --phase deform  load the FROZEN model on the BASE mesh; add the family
#                   script's own CGNS surface nodes as an extra point set to the
#                   frozen geometry component; set shape = s*, twist = t*; write
#                   surfaceMesh_final.cgns AND the H1 bijection against the
#                   IDWarp-deformed wall points the O_mp run left on disk.
#   --phase mesh    run the FAMILY SCRIPT'S OWN genWingMesh.py, UNMODIFIED and
#                   md5-asserted, then plot3dToFoam / autoPatch / createPatch /
#                   renumberMesh -- the family script's own sequence.
#   --phase solve   stage the fresh mesh, load the FROZEN model on it, set
#                   shape = s*, twist = t*, patchV = a* (NO re-trim: comparison
#                   (i) of registration section 2e), solve all three conditions.
#
# Three processes because loading DAFoam twice in one process on two different
# meshes is not a thing this file will assume works.
#
# NOTHING IS DOWNLOADED.  The family script's `wget` branch is guarded by
# `if [ -f ... ]` and the file is on the box; this file STAGES the inputs and
# ASSERTS their md5s, and it never invokes preProcessing.sh's fetch branch.
#
# HONEST GAP (registration section 11a): THIS FILE HAS NEVER BEEN EXECUTED
# AGAINST THE SOLVER OR AGAINST pyHyp.  `--selftest` drives the pure logic --
# the bijection matcher, the OpenFOAM points reader, the record assembly and
# every refusal path -- on synthetic inputs, touching no container.
# ===========================================================================
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"
GENWINGMESH_MD5 = "dab5e959187ab2e2bfb4e2c0ded0feb6"   # the family script's mesh step
SURFACE_MD5 = "3050ea454c2d0304bafa2c1a80c53b76"       # surfaceMesh.cgns, once coarsened
BASE_POINTS_MD5 = "0fb1935a9b8781b73ac4ccb136e3ec68"   # base/constant/polyMesh/points.gz
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"
FINAL_RECORD_N = 88
# "a bijection ... within SHAPE_MATCH_TOL = 1.0e-8 (absolute, metres)"  (sec 2c)
SHAPE_MATCH_TOL = 1.0e-8
# "the CGNS surface has 1008 faces / 1031 unique nodes, so the comparison is
# known to be possible before the run"  (sec 2c).  THE REGISTERED COMPARISON IS
# AGAINST THE UNIQUE NODES.  Copied from the registration, not chosen here.
# Both sides measured and both are 1031: the CGNS surface in the pinned image,
# and the OpenFOAM `wing` patch (1008 faces, 1031 unique points) on the host.
CGNS_UNIQUE_NODES = 1031
WALL_PATCH = "wing"
RECORD = "d6r2c_freshmesh.json"

from d6r2c_decomp import (Refusal, load_frozen_model, read_final_dv,  # noqa: E402
                          _md5_file, dv_divisor, dv_divisor_for)


# ---------------------------------------------------------------------------
# OpenFOAM readers -- plain parsers, no OpenFOAM needed
# ---------------------------------------------------------------------------

def _open_maybe_gz(path):
    if os.path.isfile(path + ".gz"):
        return gzip.open(path + ".gz", "rt", errors="ignore")
    if os.path.isfile(path):
        return open(path, errors="ignore")
    raise Refusal("REFUSE_MISSING_FOAM_FILE %s[.gz]" % path)


def read_points(path_no_ext):
    """Read an OpenFOAM pointField into a list of (x, y, z)."""
    with _open_maybe_gz(path_no_ext) as fh:
        txt = fh.read()
    i = txt.find("(")
    # the FoamFile header carries braces, never a bare '(' before the count
    hdr_end = txt.find("}")
    i = txt.find("(", hdr_end)
    count_str = txt[:i].strip().split()[-1]
    n = int(count_str)
    body = txt[i + 1:]
    pts = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line[0] != "(":
            if line.startswith(")"):
                break
            continue
        a, b, c = line.strip("()").split()
        pts.append((float(a), float(b), float(c)))
        if len(pts) == n:
            break
    if len(pts) != n:
        raise Refusal("REFUSE_POINTS_TRUNCATED %s: header says %d, read %d"
                      % (path_no_ext, n, len(pts)))
    return pts


def read_boundary_patch(boundary_path, patch):
    """(nFaces, startFace) for one patch, from constant/polyMesh/boundary."""
    with _open_maybe_gz(boundary_path) as fh:
        txt = fh.read()
    k = txt.find("\n    %s\n" % patch)
    if k < 0:
        k = txt.find("\n%s\n" % patch)
    if k < 0:
        raise Refusal("REFUSE_NO_PATCH %r in %s" % (patch, boundary_path))
    blk = txt[k:txt.find("}", k)]
    nf = st = None
    for line in blk.splitlines():
        t = line.strip().rstrip(";").split()
        if len(t) == 2 and t[0] == "nFaces":
            nf = int(t[1])
        if len(t) == 2 and t[0] == "startFace":
            st = int(t[1])
    if nf is None or st is None:
        raise Refusal("REFUSE_PATCH_FIELDS %r: nFaces=%r startFace=%r" % (patch, nf, st))
    return nf, st


def read_faces(path_no_ext):
    """Read an OpenFOAM faceList as a list of point-index tuples."""
    with _open_maybe_gz(path_no_ext) as fh:
        txt = fh.read()
    hdr_end = txt.find("}")
    i = txt.find("(", hdr_end)
    n = int(txt[:i].strip().split()[-1])
    faces = []
    for line in txt[i + 1:].splitlines():
        line = line.strip()
        if not line or "(" not in line:
            if line.startswith(")"):
                break
            continue
        inner = line[line.find("(") + 1:line.rfind(")")]
        faces.append(tuple(int(x) for x in inner.split()))
        if len(faces) == n:
            break
    if len(faces) != n:
        raise Refusal("REFUSE_FACES_TRUNCATED %s: header says %d, read %d"
                      % (path_no_ext, n, len(faces)))
    return faces


def wall_point_ids(polymesh_dir, patch=WALL_PATCH):
    nf, st = read_boundary_patch(os.path.join(polymesh_dir, "boundary"), patch)
    faces = read_faces(os.path.join(polymesh_dir, "faces"))
    ids = set()
    for f in faces[st:st + nf]:
        ids.update(f)
    return sorted(ids), nf


# ---------------------------------------------------------------------------
# THE H1 BIJECTION -- the check that the fresh mesh is the FINAL shape
# ---------------------------------------------------------------------------

def bijection(a_pts, b_pts, tol=SHAPE_MATCH_TOL):
    """Every point of `a` matched to exactly one point of `b` within `tol`, and
    the matching one-to-one.

    Registration section 2c.  A count mismatch, a non-bijective matching or any
    unmatched point is NOT A RESULT with both counts and the worst distance
    printed -- NEVER a silent fallback to a Hausdorff distance."""
    out = {"n_a": len(a_pts), "n_b": len(b_pts), "tol": tol}
    if len(a_pts) != len(b_pts):
        out.update({"bijective": False, "n_unmatched": abs(len(a_pts) - len(b_pts)),
                    "worst_dist": float("inf"),
                    "why": "count mismatch -- registration sec 2c"})
        return out
    try:
        from scipy.spatial import cKDTree
        tree = cKDTree(b_pts)
        d, idx = tree.query(a_pts, k=1)
        d = list(d)
        idx = list(idx)
    except ImportError:
        d, idx = [], []
        for p in a_pts:
            best, bi = float("inf"), -1
            for j, q in enumerate(b_pts):
                s = sum((p[k] - q[k]) ** 2 for k in range(3))
                if s < best:
                    best, bi = s, j
            d.append(best ** 0.5)
            idx.append(bi)
    n_unmatched = sum(1 for x in d if x > tol)
    out.update({"bijective": len(set(idx)) == len(idx) and n_unmatched == 0,
                "n_unmatched": n_unmatched,
                "worst_dist": max(d) if d else float("inf"),
                "n_distinct_targets": len(set(idx))})
    return out


# ---------------------------------------------------------------------------
# PHASES
# ---------------------------------------------------------------------------

def phase_deform(arm_dir, runscript, evals, base_dir, omp_dir, surface_in, surface_out):
    from mpi4py import MPI
    rank0 = MPI.COMM_WORLD.rank == 0
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT (Sanaa Launch item 6)")
    got = _md5_file(surface_in)
    if got != SURFACE_MD5:
        raise Refusal("REFUSE_SURFACE_MD5 got %s want %s -- the family script's own "
                      "surface is not the file staged" % (got, SURFACE_MD5))
    dv_star, _, _ = read_final_dv(evals)

    ns = load_frozen_model(runscript)
    prob = ns["prob"]
    geo = getattr(prob.model, "geometry_cl05")

    from cgnsutilities.cgnsutilities import readGrid   # in the pinned image
    grid = readGrid(surface_in)
    coords, blocks = [], []
    for blk in grid.blocks:
        # ADDENDUM 3: the pinned image's cgnsutilities Block exposes `coords`,
        # NOT `X` -- measured, Block.__init__ is (self, zoneName, dims, coords).
        # `blk.X` raised AttributeError and killed arm FM3 in 15 s.
        x = blk.coords
        blocks.append(x.shape)
        coords.extend([tuple(float(v) for v in p) for p in x.reshape(-1, 3)])

    # ADDENDUM 4: add the point set DIRECTLY to DVGeo, NOT through the mphys
    # component.  `nom_addPointSet` appends the name to `omPtSetList`, and
    # OM_DVGEOCOMP.compute() then does `outputs[ptName] = ...` for every listed
    # set -- but an OpenMDAO output cannot be created after `prob.setup()`, which
    # `load_frozen_model` has already run.  That raised
    #   KeyError: 'geometry_cl05' <class OM_DVGEOCOMP>: Variable name 'cgnssurf' not found
    # and killed the deform path.  compute() guards its loop with
    # `if ptName in self.omPtSetList`, so a set added straight to DVGeo is
    # SKIPPED there and is still updated by `DVGeo.update()` below.
    #
    # IT MUST STAY BEFORE run_model().  addPointSet embeds the points against the
    # FFD's CURRENT control points; embedding after the design variables were
    # applied would bake the deformation into the parametric coordinates and
    # `update()` would hand back an UNDEFORMED surface.
    geo.DVGeo.addPointSet(_flat(coords).reshape(-1, 3), "cgnssurf")
    meta = prob.model.get_design_vars(recurse=True, get_sizes=True, use_prom_ivc=True)
    scalers = {k.split(".")[-1]: dv_divisor(v) for k, v in meta.items()}
    for name in ("shape", "twist"):
        s = dv_divisor_for(scalers, name)
        prob.set_val(name, [v / s for v in dv_star[name]])
    prob.run_model()
    new = geo.DVGeo.update("cgnssurf").reshape(-1, 3)

    off = 0
    for i, shape in enumerate(blocks):
        n = shape[0] * shape[1] * shape[2]
        # ALL block-structured points are written back, duplicates included:
        # every one is needed to reconstitute the CGNS blocks, and DVGeo deforms
        # duplicates identically because it is a function of position.
        grid.blocks[i].coords = new[off:off + n].reshape(shape)
        off += n
    grid.writeToCGNS(surface_out)

    # ---- H1 COMPARES THE SURFACE'S UNIQUE NODES, WHICH IS WHAT SEC 2c NAMES --
    # The block-structured array repeats interface nodes (measured in the pinned
    # image: 9 blocks, 1215 points, 1031 unique, 184 duplicates).  The frozen
    # text never describes that array; it registers "1031 unique nodes" and says
    # the bijection "is known to be possible before the run".  Supplying the
    # unique set is CONFORMANCE, not a reshape to make a gate satisfiable --
    # AND THAT IS ONLY TRUE BECAUSE OF THE REFUSAL BELOW.
    #
    # DO NOT "SIMPLIFY" THIS TO DEDUPLICATE `new`.  The index map is built from
    # the ORIGINAL coordinates, which are a property of the md5-asserted surface
    # and are fixed before any deformation happens, so THE INPUT TO H1 CANNOT
    # DEPEND ON THE ANSWER H1 IS COMPUTING.  Deduplicating the DEFORMED array
    # would give 1031 today and would silently change size the day two nodes
    # collapsed together -- a gate whose own input moves with the thing under
    # test.  Same anti-circularity principle as L-588.
    seen, uniq_idx = set(), []
    for i, p in enumerate(coords):
        if p not in seen:
            seen.add(p)
            uniq_idx.append(i)
    if len(uniq_idx) != CGNS_UNIQUE_NODES:
        raise Refusal(
            "REFUSE_CGNS_UNIQUE_NODE_COUNT block_structured=%d unique=%d "
            "registered=%d -- the surface is not the surface section 2c "
            "registered; this is a finding about the geometry and the run stops "
            "rather than proceed on a count nobody registered"
            % (len(coords), len(uniq_idx), CGNS_UNIQUE_NODES))

    # the IDWarp-deformed wall points THE O_mp RUN LEFT ON DISK
    deformed = read_deformed_wall_points(base_dir, omp_dir)
    h1 = bijection([tuple(new[i]) for i in uniq_idx], deformed)
    if rank0:
        with open(os.path.join(arm_dir, "h1.json"), "w") as fh:
            json.dump({"h1": {"n_cgns_nodes": h1["n_a"],
                              "n_cgns_block_structured": len(coords),
                              "n_cgns_unique_nodes": len(uniq_idx),
                              "n_cgns_unique_registered": CGNS_UNIQUE_NODES,
                              "n_foam_wall_points": h1["n_b"],
                              "bijective": bool(h1["bijective"]),
                              "n_unmatched": int(h1["n_unmatched"]),
                              "worst_dist": float(h1["worst_dist"])},
                       "surface_in_md5": got,
                       "surface_out_md5": _md5_file(surface_out)}, fh, indent=1)
    return 0


def _flat(coords):
    """A FLAT (3N,) array of coordinates -- which is what pygeo's
    `nom_addPointSet` requires and what this function's name promises.

    ADDENDUM 4: it did NOT flatten, and arm FM4 died in 11 s on
    `ValueError: cannot reshape array of size 3645 into shape (405,3)`.
    pygeo/mphys/mphys_dvgeo.py:119 does

        self.DVGeo.addPointSet(points.reshape(len(points) // 3, 3), ptName)

    so it reads `len(points)` as 3N, not N.  Passing the (N, 3) array made
    `len()` return 1215 instead of 3645, so pygeo reshaped to (405, 3) and the
    size did not divide.  A function named `_flat` that returns a 2-D array is
    the whole defect; the name was the specification and the body ignored it.
    """
    import numpy as np
    a = np.array(coords, dtype=float).reshape(-1)
    if a.size != len(coords) * 3:
        raise Refusal("REFUSE_FLATTEN_SHAPE %d coords produced %d values, expected %d"
                      % (len(coords), a.size, len(coords) * 3))
    return a


def read_deformed_wall_points(base_dir, omp_dir, point="mp05"):
    """Reassemble the global deformed wall points from the O_mp run's own output.

    The optimiser's mesh is the base mesh WARPED BY IDWarp; OpenFOAM writes the
    warped points into <time>/polyMesh/points per processor, and
    constant/polyMesh/pointProcAddressing maps them back to global ids.  READ
    ONLY -- this function never writes into the graded arm."""
    ids, _ = wall_point_ids(os.path.join(base_dir, "constant", "polyMesh"))
    want = set(ids)
    glob = {}
    pd = os.path.join(omp_dir, point)
    procs = sorted(d for d in os.listdir(pd) if d.startswith("processor"))
    if not procs:
        raise Refusal("REFUSE_NO_PROCESSOR_DIRS under %s" % pd)
    for pr in procs:
        addr_path = os.path.join(pd, pr, "constant", "polyMesh", "pointProcAddressing")
        with _open_maybe_gz(addr_path) as fh:
            txt = fh.read()
        i = txt.find("(", txt.find("}"))
        n = int(txt[:i].strip().split()[-1])
        addr = [int(x) for x in txt[i + 1:].replace(")", " ").split()[:n]]
        pts = read_points(os.path.join(pd, pr, "1000", "polyMesh", "points"))
        if len(pts) != len(addr):
            raise Refusal("REFUSE_ADDR_MISMATCH %s: %d points, %d addresses"
                          % (pr, len(pts), len(addr)))
        for local, g in enumerate(addr):
            if g in want:
                glob[g] = pts[local]
    missing = want - set(glob)
    if missing:
        raise Refusal("REFUSE_WALL_POINTS_INCOMPLETE %d of %d global wall points not "
                      "recovered from %s" % (len(missing), len(want), pd))
    return [glob[g] for g in ids]


def phase_mesh(arm_dir, genwingmesh, surface_out, log):
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT (Sanaa Launch item 6)")
    got = _md5_file(genwingmesh)
    if got != GENWINGMESH_MD5:
        raise Refusal("REFUSE_GENWINGMESH_MD5 got %s want %s -- the family script's "
                      "own mesh step is not the file staged" % (got, GENWINGMESH_MD5))
    # genWingMesh.py hard-codes fileName = "surfaceMesh.cgns".  The DEFORMED
    # surface is staged UNDER THAT NAME so the family script is never edited
    # (rule 6) and never sees a modified option.
    staged = os.path.join(arm_dir, "surfaceMesh.cgns")
    import shutil
    shutil.copyfile(surface_out, staged)
    steps = [[sys.executable, genwingmesh],
             ["plot3dToFoam", "-noBlank", "volumeMesh.xyz"],
             ["autoPatch", "60", "-overwrite"],
             ["createPatch", "-overwrite"],
             ["renumberMesh", "-overwrite"]]
    rc = 0
    with open(log, "a") as lf:
        for cmd in steps:
            lf.write("\n=== %s ===\n" % " ".join(cmd))
            lf.flush()
            r = subprocess.run(cmd, cwd=arm_dir, stdout=lf, stderr=subprocess.STDOUT)
            if r.returncode != 0:
                rc = r.returncode
                lf.write("\nSTEP FAILED rc=%d\n" % rc)
                break
        if rc == 0:
            lf.write("\n=== checkMesh ===\n")
            lf.flush()
            subprocess.run(["checkMesh"], cwd=arm_dir, stdout=lf, stderr=subprocess.STDOUT)
    with open(os.path.join(arm_dir, "mesh_rc.txt"), "w") as fh:
        fh.write(str(rc))
    return rc


def phase_solve(arm_dir, runscript, evals, out_path):
    from mpi4py import MPI
    rank0 = MPI.COMM_WORLD.rank == 0
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT (Sanaa Launch item 6)")
    t0 = time.time()
    dv_star, _, evals_md5 = read_final_dv(evals)
    ns = load_frozen_model(runscript)
    prob, POINTS, W, T = ns["prob"], ns["POINTS"], ns["WEIGHTS"], ns["CL_TARGETS"]
    meta = prob.model.get_design_vars(recurse=True, get_sizes=True, use_prom_ivc=True)
    scalers = {k.split(".")[-1]: dv_divisor(v) for k, v in meta.items()}
    for name, vals in dv_star.items():
        if name in ("shape", "twist") or name.startswith("patchV_"):
            s = dv_divisor_for(scalers, name)
            prob.set_val(name, [v / s for v in vals])
    prob.run_model()      # comparison (i): NO re-trim
    cd = {p: float(prob.get_val("%s.aero_post.CD" % p)[0]) for p in POINTS}
    cl = {p: float(prob.get_val("%s.aero_post.CL" % p)[0]) for p in POINTS}
    aoa = {p: float(prob.get_val("patchV_" + p)[1]) for p in POINTS}
    if not rank0:
        return 0
    h1 = json.load(open(os.path.join(arm_dir, "h1.json")))
    pm = os.path.join(arm_dir, "constant", "polyMesh")
    rec = {"kind": "FRESHMESH",
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "uid": os.getuid(), "gid": os.getgid(),
           "ranks": MPI.COMM_WORLD.size,
           "evals_md5": evals_md5, "runscript_md5": RUNSCRIPT_MD5,
           "genwingmesh_md5": GENWINGMESH_MD5,
           "staged_surface_md5": h1.get("surface_out_md5"),
           "mesh_rc": int(open(os.path.join(arm_dir, "mesh_rc.txt")).read().strip()),
           "mesh": {"nCells": _mesh_count(pm, "nCells"),
                    "nPoints": _mesh_count(pm, "nPoints"),
                    "points_md5": _md5_file(os.path.join(pm, "points.gz"))},
           "base_points_md5": BASE_POINTS_MD5,
           "h1": h1["h1"],
           "solve": {"CD": cd, "CL": cl, "AoA_deg": aoa,
                     "J": sum(W[p] * cd[p] for p in POINTS),
                     "primal_converged": _converged(arm_dir, POINTS),
                     "primal_final_res": _final_res(arm_dir, POINTS)},
           "cl_targets": T, "weights": W,
           "comparison": "(i) same DVs including a*, NO re-trim -- registration sec 2e",
           "checkmesh_report_path": "mesh_generation.log",
           "wall_s": time.time() - t0,
           "DEADLINE_IN_CONTAINER_S": "NONE"}
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    return 0


def _mesh_count(polymesh_dir, key):
    with _open_maybe_gz(os.path.join(polymesh_dir, "owner")) as fh:
        for line in fh:
            if key in line:
                for tok in line.replace('"', " ").split():
                    if tok.startswith(key + ":"):
                        return int(tok.split(":")[1])
            if "(" in line:
                break
    raise Refusal("REFUSE_NO_MESH_COUNT %r in %s/owner" % (key, polymesh_dir))


def _converged(arm_dir, points):
    out = {}
    for p in points:
        rp = os.path.join(arm_dir, "mp" + p[2:], "primal_residual.json")
        out[p] = bool(json.load(open(rp))["converged"]) if os.path.isfile(rp) else True
    return out


def _final_res(arm_dir, points):
    out = {}
    for p in points:
        rp = os.path.join(arm_dir, "mp" + p[2:], "primal_residual.json")
        out[p] = json.load(open(rp)).get("final_res") if os.path.isfile(rp) else None
    return out


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic only.  No container, no pyHyp, no run directory.
# ---------------------------------------------------------------------------

def selftest():
    import shutil
    import tempfile
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    # --- the bijection matcher, in both directions -------------------------
    a = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    check("H1 identical clouds -> bijective", bijection(a, list(a))["bijective"], True)
    check("H1 identical clouds -> worst 0", bijection(a, list(a))["worst_dist"], 0.0)
    b = [(x + 1e-9, y, z) for (x, y, z) in a]
    check("H1 offset 1e-9 < tol -> bijective", bijection(a, b)["bijective"], True)
    b = [(x + 1e-7, y, z) for (x, y, z) in a]
    r = bijection(a, b)
    check("H1 offset 1e-7 > tol -> NOT bijective", r["bijective"], False)
    check("H1 offset 1e-7 -> all 4 unmatched", r["n_unmatched"], 4)
    # the planted control of registration section 7: one coordinate moved by PLANT
    b = list(a)
    b[2] = (b[2][0] + 1.234e-3, b[2][1], b[2][2])
    r = bijection(a, b)
    check("H1 PLANT 1.234e-3 in ONE coordinate -> NOT bijective", r["bijective"], False)
    check("H1 PLANT -> exactly one unmatched", r["n_unmatched"], 1)
    check("H1 count mismatch -> NOT bijective", bijection(a, a[:3])["bijective"], False)
    check("H1 count mismatch -> worst is inf", bijection(a, a[:3])["worst_dist"], float("inf"))
    check("H1 count mismatch reports both counts",
          (bijection(a, a[:3])["n_a"], bijection(a, a[:3])["n_b"]), (4, 3))
    # a DEGENERATE matching: two a-points onto one b-point is NOT a bijection
    dup = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (5.0, 0.0, 0.0), (6.0, 0.0, 0.0)]
    r = bijection(dup, [(0.0, 0.0, 0.0), (9.0, 0.0, 0.0), (5.0, 0.0, 0.0), (6.0, 0.0, 0.0)])
    check("H1 two-onto-one -> NOT bijective", r["bijective"], False)

    tmp = tempfile.mkdtemp(prefix="d6r2c_fm_selftest_")
    try:
        # --- the OpenFOAM readers, on synthetic files ----------------------
        pm = os.path.join(tmp, "polyMesh")
        os.makedirs(pm)
        with open(os.path.join(pm, "points"), "w") as fh:
            fh.write('FoamFile\n{\n version 2.0;\n}\n\n4\n(\n(0 0 0)\n(1 0 0)\n'
                     '(0 1 0)\n(1 1 0)\n)\n')
        check("points reader count", len(read_points(os.path.join(pm, "points"))), 4)
        check("points reader value", read_points(os.path.join(pm, "points"))[3], (1.0, 1.0, 0.0))
        with open(os.path.join(pm, "faces"), "w") as fh:
            fh.write('FoamFile\n{\n version 2.0;\n}\n\n2\n(\n4(0 1 3 2)\n4(0 1 2 3)\n)\n')
        check("faces reader count", len(read_faces(os.path.join(pm, "faces"))), 2)
        check("faces reader value", read_faces(os.path.join(pm, "faces"))[0], (0, 1, 3, 2))
        with open(os.path.join(pm, "boundary"), "w") as fh:
            fh.write('FoamFile\n{\n version 2.0;\n}\n\n1\n(\n    wing\n    {\n'
                     '        type            wall;\n        nFaces          1;\n'
                     '        startFace       1;\n    }\n)\n')
        check("boundary reader", read_boundary_patch(os.path.join(pm, "boundary"), "wing"), (1, 1))
        ids, nf = wall_point_ids(pm)
        check("wall point ids from the SECOND face", ids, [0, 1, 2, 3])
        check("wall nFaces", nf, 1)
        try:
            read_boundary_patch(os.path.join(pm, "boundary"), "nosuchpatch")
            check("missing patch refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("missing patch -> REFUSE_NO_PATCH", str(e).startswith("REFUSE_NO_PATCH"), True)
        # a truncated points file must REFUSE, never silently return fewer
        with open(os.path.join(pm, "points"), "w") as fh:
            fh.write('FoamFile\n{\n version 2.0;\n}\n\n4\n(\n(0 0 0)\n(1 0 0)\n)\n')
        try:
            read_points(os.path.join(pm, "points"))
            check("truncated points refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("truncated points -> REFUSE_POINTS_TRUNCATED",
                  str(e).startswith("REFUSE_POINTS_TRUNCATED"), True)
        # --- the md5 pins refuse rather than proceed -----------------------
        fake = os.path.join(tmp, "fake.py")
        open(fake, "w").write("x\n")
        try:
            phase_mesh(tmp, fake, fake, os.path.join(tmp, "log"))
            check("wrong genWingMesh md5 refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("wrong genWingMesh md5 -> REFUSE_GENWINGMESH_MD5",
                  str(e).startswith("REFUSE_GENWINGMESH_MD5"), True)
        # --- the family script's own bytes are where this file says ---------
        gw = "/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/genWingMesh.py"
        if os.path.isfile(gw):
            check("the family script's mesh step is at its registered path and md5",
                  _md5_file(gw), GENWINGMESH_MD5)
        sm = "/home/ubuntu/certonomous-runs/A2-mach-wing/surfaceMesh.cgns"
        if os.path.isfile(sm):
            check("the family script's own surface is on the box at its registered md5",
                  _md5_file(sm), SURFACE_MD5)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("D6R2C_FRESHMESH SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="D6R2C after-item 9 producer.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--phase", choices=("deform", "mesh", "solve"))
    ap.add_argument("--arm-dir", default=os.getcwd())
    ap.add_argument("--runscript", default="d6r2c_opt_runScript.py")
    ap.add_argument("--evals", default="d6r2c_evals_final.jsonl")
    ap.add_argument("--base-dir", default="../base")
    ap.add_argument("--omp-dir")
    ap.add_argument("--surface-in", default="surfaceMesh_base.cgns")
    ap.add_argument("--surface-out", default="surfaceMesh_final.cgns")
    ap.add_argument("--genwingmesh", default="genWingMesh.py")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.phase is None:
        ap.error("--phase is required")
    try:
        if a.phase == "deform":
            return phase_deform(a.arm_dir, a.runscript, a.evals, a.base_dir,
                                a.omp_dir, a.surface_in, a.surface_out)
        if a.phase == "mesh":
            return phase_mesh(a.arm_dir, a.genwingmesh, a.surface_out,
                              os.path.join(a.arm_dir, "mesh_generation.log"))
        return phase_solve(a.arm_dir, a.runscript, a.evals,
                           os.path.join(a.arm_dir, RECORD))
    except Refusal as e:
        print("D6R2C_FRESHMESH REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
