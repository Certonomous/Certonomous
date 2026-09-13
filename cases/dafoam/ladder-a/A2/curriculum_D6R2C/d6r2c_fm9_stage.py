#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm9_stage.py -- THE ONE REGISTERED CHANGE OF ARM FM9
# ===========================================================================
#
# Registered by PREREGISTRATION_FRESHMESH_ARRIVES.md sections 2 and 11, and IN
# THE SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (rule 2).
#
# WHAT IT DOES, IN ONE SENTENCE.  It puts the freshly extruded mesh into every
# condition case and REMOVES the stale decomposition, so that the solver's next
# prob.setup() decomposes THE FRESH MESH instead of reading a decomposition of
# the base mesh that was built one phase earlier.
#
# WHY IT EXISTS.  MEASURED 2026-09-13: FM5, FM7 and FM8 each generated the fresh
# mesh correctly and NEVER SOLVED ON IT.
#     FM8  arm/constant/polyMesh/points.gz  (FRESH)   written 08:28:11
#          all 12 mp0X/processorN/.../points.gz       written 08:27:06-08:27:09
#     FM5  fresh 06:48:26                             solver mesh 06:47:13
# The mesh the solver read was written 62-73 SECONDS BEFORE THE FRESH MESH
# EXISTED, and mp0X/constant/polyMesh was still the BASE mesh dated 2026-07-28.
# Nothing in d6r2c_freshmesh.py or its launcher ever staged the fresh mesh into
# the condition cases.  H2 checked that the mesh EXISTED, came from the pinned
# genWingMesh.py, and DIFFERED from the base -- ALL THREE TRUE WHILE THE SOLVER
# READ SOMETHING ELSE.  A CHECK MUST EXERCISE THE THING, NOT DESCRIBE IT (L-595).
#
# AND THERE IS NO FIELD TRANSFER IN THIS ARM.  The cell-for-cell index transfer
# that FM8 used is NOT VALID once the fresh mesh genuinely arrives: warped-to-
# fresh point displacement is a MEASURED median of 17.8 first-cell heights, p99
# 2284, max 4391, with 74.4 % of points beyond one cell height -- the wall points
# coincide exactly (0.0, which is H1's equality from the other side) and the
# interiors diverge.  The index correspondence is TOPOLOGICAL, NOT SPATIAL.  It
# looked exact in FM8 only because ITS DESTINATION WAS NEVER THE FRESH MESH.
# So this arm starts from the case's own freestream 0.orig and changes ONE THING.
#
# HONEST GAP (section 11a): this file has never run against a real decomposed
# case.  --selftest drives the pure logic on synthetic trees.
# ===========================================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time

# "the three conditions" -- PREREGISTRATION.md section 1
RUN_DIRS = ("mp04", "mp05", "mp06")
# "the base mesh, which the fresh mesh must NOT equal" (sec 3, M1)
BASE_POINTS_MD5 = "0fb1935a9b8781b73ac4ccb136e3ec68"
# "the mesh FM5/FM7/FM8 actually solved on -- the base mesh decomposed" (sec 1a)
STALE_PROC_POINTS_MD5 = "c7f5feda2f4dc6774cf320d4cb2ffcb3"
# the polyMesh files a condition case needs
MESH_FILES = ("points.gz", "faces.gz", "owner.gz", "neighbour.gz", "boundary")
RECORD = "d6r2c_fm9_stage.json"


class Refusal(Exception):
    """Refuse, never degrade."""


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def processor_dirs(mp_dir):
    if not os.path.isdir(mp_dir):
        return []
    return sorted(d for d in os.listdir(mp_dir) if re.fullmatch(r"processor\d+", d))


def stage_mesh(arm_dir, run_dirs=RUN_DIRS, _fresh_md5=None):
    """Copy the fresh mesh into every condition case and REMOVE the stale
    decomposition.

    THE REMOVAL IS THE OPERATIVE HALF.  Copying the mesh into
    mp0X/constant/polyMesh changes nothing on its own: DAFoam decomposes only
    when processorN/ is ABSENT, and if a decomposition is already there it reads
    that instead -- which is precisely how FM5, FM7 and FM8 solved on a mesh they
    had not generated.  Evidence that removal is sufficient: their own deform
    phase created processorN/ from a clean tree, at 08:27:06 in FM8's case."""
    src = os.path.join(arm_dir, "constant", "polyMesh")
    if not os.path.isdir(src):
        raise Refusal("REFUSE_NO_FRESH_MESH %s -- phase mesh must run first" % src)
    for f in MESH_FILES:
        if not os.path.isfile(os.path.join(src, f)):
            raise Refusal("REFUSE_INCOMPLETE_FRESH_MESH %s missing from %s" % (f, src))
    fresh_md5 = _fresh_md5 or _md5(os.path.join(src, "points.gz"))
    if fresh_md5 == BASE_POINTS_MD5:
        raise Refusal(
            "REFUSE_FRESH_IS_BASE the generated mesh's points.gz md5 equals the "
            "BASE mesh's (%s).  A 'fresh' mesh identical to the base means the "
            "deformation never reached the mesher, and staging it would prove "
            "nothing" % BASE_POINTS_MD5)

    rec = {"kind": "FM9_STAGE",
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "uid": os.getuid(), "gid": os.getgid(),
           "fresh_points_md5": fresh_md5,
           "base_points_md5_must_differ": BASE_POINTS_MD5,
           "stale_processor_points_md5_must_differ": STALE_PROC_POINTS_MD5,
           "conditions": {}}

    for mp in run_dirs:
        dst_case = os.path.join(arm_dir, mp)
        if not os.path.isdir(dst_case):
            raise Refusal("REFUSE_NO_CONDITION_CASE %s" % dst_case)
        dst = os.path.join(dst_case, "constant", "polyMesh")
        before = _md5(os.path.join(dst, "points.gz")) if os.path.isfile(
            os.path.join(dst, "points.gz")) else None
        os.makedirs(dst, exist_ok=True)
        for f in MESH_FILES:
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            for stale in (d, d + ".gz", d[:-3] if d.endswith(".gz") else d + ".gz"):
                if os.path.isfile(stale) and stale != s:
                    os.remove(stale)
            shutil.copyfile(s, d)
        after = _md5(os.path.join(dst, "points.gz"))
        if after != fresh_md5:
            raise Refusal("REFUSE_STAGE_READBACK %s/constant/polyMesh/points.gz "
                          "reads %s after the copy, not the fresh %s"
                          % (mp, after, fresh_md5))
        # ---- AND NOW THE OPERATIVE HALF: REMOVE THE STALE DECOMPOSITION ----
        removed = []
        for pd in processor_dirs(dst_case):
            shutil.rmtree(os.path.join(dst_case, pd))
            removed.append(pd)
        left = processor_dirs(dst_case)
        if left:
            raise Refusal(
                "REFUSE_PROCESSOR_DIRS_REMAIN %s still carries %r after removal. "
                "THE SOLVER WOULD READ THEM INSTEAD OF DECOMPOSING THE FRESH "
                "MESH, which is exactly the FM5/FM7/FM8 defect" % (mp, left))
        rec["conditions"][mp] = {
            "constant_points_md5_before": before,
            "constant_points_md5_after": after,
            "was_base_before": before == BASE_POINTS_MD5,
            "processor_dirs_removed": removed,
            "processor_dirs_remaining": left,
        }
    rec["all_conditions_staged"] = len(rec["conditions"]) == len(run_dirs)
    return rec


# ---------------------------------------------------------------------------
# THE RECONSTRUCTION -- how a reader proves WHICH MESH THE SOLVER LOADED
# ---------------------------------------------------------------------------
# This is the technique that exposed the defect: the decomposed points plus each
# processor's pointProcAddressing rebuild the undecomposed mesh the solver held.
# A PROCESSOR'S OWN points.gz md5 CAN NEVER EQUAL THE WHOLE MESH'S -- it holds a
# SUBSET -- so a gate written as "the twelve hashes equal the fresh mesh's" is not
# achievable and would have to be weakened to pass.  Rebuilding and comparing the
# ARRAYS is achievable, is exact, and is what the grader does.

def _body(path):
    import gzip
    o = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    t = o.read()
    o.close()
    i = t.index("// * * *")
    return t[t.index("\n", i):]


def read_points(path):
    t = _body(path)
    a = t.index("(")
    b = t.rindex(")")
    v = [float(x) for x in t[a + 1:b].replace("(", " ").replace(")", " ").split()]
    return [(v[3 * k], v[3 * k + 1], v[3 * k + 2]) for k in range(len(v) // 3)]


def read_labels(path):
    t = _body(path)
    a = t.index("(")
    b = t.rindex(")")
    return [int(x) for x in t[a + 1:b].split()]


def _open_either(base):
    for p in (base, base + ".gz"):
        if os.path.isfile(p):
            return p
    raise Refusal("REFUSE_MISSING_FILE %s (and %s.gz)" % (base, base))


def reconstruct_loaded_points(mp_dir, n_points):
    """The undecomposed point list the SOLVER held, rebuilt from its own
    processor directories via pointProcAddressing.

    REFUSES on a hole or a duplicate: a partially rebuilt mesh cannot answer
    'which mesh was loaded'."""
    procs = processor_dirs(mp_dir)
    if not procs:
        raise Refusal("REFUSE_NO_PROCESSOR_DIRS in %s -- the solver left no "
                      "decomposition to read" % mp_dir)
    out = [None] * n_points
    for pd in procs:
        pm = os.path.join(mp_dir, pd, "constant", "polyMesh")
        addr = read_labels(_open_either(os.path.join(pm, "pointProcAddressing")))
        pts = read_points(_open_either(os.path.join(pm, "points")))
        if len(addr) != len(pts):
            raise Refusal("REFUSE_ADDR_COUNT %s: %d addresses, %d points"
                          % (pd, len(addr), len(pts)))
        for k, g in enumerate(addr):
            if not (0 <= g < n_points):
                raise Refusal("REFUSE_ADDR_RANGE %s: global point %d outside "
                              "[0, %d)" % (pd, g, n_points))
            if out[g] is not None and out[g] != pts[k]:
                raise Refusal("REFUSE_ADDR_CONFLICT %s: global point %d written "
                              "twice with different coordinates" % (pd, g))
            out[g] = pts[k]
    holes = [i for i, v in enumerate(out) if v is None]
    if holes:
        raise Refusal("REFUSE_ADDR_HOLE %d of %d points unwritten (first %r)"
                      % (len(holes), n_points, holes[:5]))
    return out


def max_point_difference(a, b):
    """Max Euclidean distance between corresponding points.  EXACT equality is
    0.0; anything else is a different mesh."""
    if len(a) != len(b):
        raise Refusal("REFUSE_POINT_COUNT %d vs %d" % (len(a), len(b)))
    worst = 0.0
    for p, q in zip(a, b):
        d = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2) ** 0.5
        if d > worst:
            worst = d
    return worst


def phase_stage(arm_dir, out_path):
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT this arm runs as ubuntu, never root")
    rec = stage_mesh(arm_dir)
    rec["note"] = ("THE ONE REGISTERED CHANGE: the fresh mesh is now in every "
                   "condition case and the stale decomposition is gone, so the "
                   "solver's next prob.setup() decomposes THE FRESH MESH.")
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    print("D6R2C_FM9_STAGE fresh=%s conditions=%d all_staged=%s"
          % (rec["fresh_points_md5"][:12], len(rec["conditions"]),
             rec["all_conditions_staged"]))
    return 0


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic only.  No container, no run directory.
# ---------------------------------------------------------------------------

def selftest():
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    HDR = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
           "    object %s;\n}\n"
           "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")

    def wpoints(path, pts):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(HDR % ("vectorField", "points")
                     + "%d\n(\n%s\n)\n" % (len(pts),
                                           "\n".join("(%g %g %g)" % p for p in pts)))

    def wlabels(path, v, obj="pointProcAddressing"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(HDR % ("labelList", obj)
                     + "%d\n(\n%s\n)\n" % (len(v), "\n".join(str(x) for x in v)))

    tmp = None
    try:
        import tempfile
        tmp = tempfile.mkdtemp(prefix="d6r2c_fm9_stage_selftest_")

        def mk_arm(root, fresh_pts=(1.0, 2.0, 3.0), with_procs=True, n_mp=3):
            src = os.path.join(root, "constant", "polyMesh")
            os.makedirs(src, exist_ok=True)
            for f in MESH_FILES:
                with open(os.path.join(src, f), "w") as fh:
                    fh.write("FRESH %s %r\n" % (f, fresh_pts))
            for mp in RUN_DIRS[:n_mp]:
                d = os.path.join(root, mp, "constant", "polyMesh")
                os.makedirs(d, exist_ok=True)
                for f in MESH_FILES:
                    with open(os.path.join(d, f), "w") as fh:
                        fh.write("BASE %s\n" % f)
                if with_procs:
                    for k in range(4):
                        p = os.path.join(root, mp, "processor%d" % k, "constant",
                                         "polyMesh")
                        os.makedirs(p, exist_ok=True)
                        with open(os.path.join(p, "points.gz"), "w") as fh:
                            fh.write("STALE\n")
            return root

        # ---- the staging works, and the removal is verified ------------------
        a = mk_arm(os.path.join(tmp, "a"))
        rec = stage_mesh(a)
        check("every condition staged", rec["all_conditions_staged"], True)
        check("every condition's mesh now reads the FRESH hash",
              sorted({v["constant_points_md5_after"] for v in rec["conditions"].values()}),
              [rec["fresh_points_md5"]])
        check("the stale decomposition is GONE from every condition",
              [v["processor_dirs_remaining"] for v in rec["conditions"].values()],
              [[], [], []])
        check("and the removal is RECORDED, not assumed",
              sorted(rec["conditions"]["mp04"]["processor_dirs_removed"]),
              ["processor0", "processor1", "processor2", "processor3"])
        check("no processor directory survives on disk",
              sum(len(processor_dirs(os.path.join(a, mp))) for mp in RUN_DIRS), 0)

        # ---- A FAILING CONTROL FOR EVERY REFUSAL -----------------------------
        b = os.path.join(tmp, "b")
        os.makedirs(b, exist_ok=True)
        try:
            stage_mesh(b)
            check("no fresh mesh -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("no fresh mesh -> REFUSE_NO_FRESH_MESH",
                  str(e).startswith("REFUSE_NO_FRESH_MESH"), True)
        c = mk_arm(os.path.join(tmp, "c"))
        os.remove(os.path.join(c, "constant", "polyMesh", "owner.gz"))
        try:
            stage_mesh(c)
            check("incomplete fresh mesh -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("a fresh mesh missing owner.gz -> REFUSE_INCOMPLETE_FRESH_MESH",
                  str(e).startswith("REFUSE_INCOMPLETE_FRESH_MESH"), True)
        d = mk_arm(os.path.join(tmp, "d"))
        try:
            stage_mesh(d, _fresh_md5=BASE_POINTS_MD5)
            check("fresh == base -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("a 'fresh' mesh identical to the base -> REFUSE_FRESH_IS_BASE",
                  str(e).startswith("REFUSE_FRESH_IS_BASE"), True)
            check("...and the refusal says staging it would prove nothing",
                  "would prove nothing" in str(e), True)
        e2 = mk_arm(os.path.join(tmp, "e"), n_mp=2)
        try:
            stage_mesh(e2)
            check("a missing condition case -> refusal", "no refusal", "Refusal")
        except Refusal as ex:
            check("a missing condition case -> REFUSE_NO_CONDITION_CASE",
                  str(ex).startswith("REFUSE_NO_CONDITION_CASE"), True)
        # NEGATIVE: an arm that already has no processor dirs must still stage
        f = mk_arm(os.path.join(tmp, "f"), with_procs=False)
        check("NEGATIVE -- no stale decomposition is not an error",
              stage_mesh(f)["all_conditions_staged"], True)

        # ---- THE RECONSTRUCTION, which is how the gate reads what was loaded --
        # deliberately non-contiguous, non-sorted addressing
        g = os.path.join(tmp, "g", "mp04")
        GLOBAL = [(float(i), 0.0, 0.0) for i in range(6)]
        for pd, addr in (("processor0", [4, 0, 2]), ("processor1", [1, 5, 3])):
            pm = os.path.join(g, pd, "constant", "polyMesh")
            wlabels(os.path.join(pm, "pointProcAddressing"), addr)
            wpoints(os.path.join(pm, "points"), [GLOBAL[i] for i in addr])
        check("reconstruct: points land at their GLOBAL index",
              reconstruct_loaded_points(g, 6), GLOBAL)
        check("max_point_difference of a mesh with itself is EXACTLY 0.0",
              max_point_difference(GLOBAL, GLOBAL), 0.0)
        moved = list(GLOBAL)
        moved[3] = (3.0, 1.0e-9, 0.0)
        check("...and a ONE-NANOMETRE move is visible",
              max_point_difference(GLOBAL, moved) == 1.0e-9, True)
        try:
            reconstruct_loaded_points(os.path.join(tmp, "g", "nosuch"), 6)
            check("no processor dirs -> refusal", "no refusal", "Refusal")
        except Refusal as ex:
            check("no processor dirs -> REFUSE_NO_PROCESSOR_DIRS",
                  str(ex).startswith("REFUSE_NO_PROCESSOR_DIRS"), True)
        h = os.path.join(tmp, "h", "mp04")
        pm = os.path.join(h, "processor0", "constant", "polyMesh")
        wlabels(os.path.join(pm, "pointProcAddressing"), [0, 1])
        wpoints(os.path.join(pm, "points"), [GLOBAL[0], GLOBAL[1]])
        try:
            reconstruct_loaded_points(h, 6)
            check("a hole -> refusal", "no refusal", "Refusal")
        except Refusal as ex:
            check("an unwritten point -> REFUSE_ADDR_HOLE",
                  str(ex).startswith("REFUSE_ADDR_HOLE"), True)

        # ---- EXTERNAL ANCHORS, typed as assertions not as sources ------------
        check("EXTERNAL: the base mesh hash", BASE_POINTS_MD5,
              "0fb1935a9b8781b73ac4ccb136e3ec68")
        check("EXTERNAL: the mesh FM5/FM7/FM8 actually solved on",
              STALE_PROC_POINTS_MD5, "c7f5feda2f4dc6774cf320d4cb2ffcb3")
        check("EXTERNAL: the three conditions", RUN_DIRS, ("mp04", "mp05", "mp06"))
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_FM9_STAGE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="FM9 phase stage: put the fresh mesh where the solver reads it.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--arm-dir", default=os.getcwd())
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    try:
        return phase_stage(a.arm_dir, os.path.join(a.arm_dir, RECORD))
    except Refusal as e:
        print("D6R2C_FM9_STAGE REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
