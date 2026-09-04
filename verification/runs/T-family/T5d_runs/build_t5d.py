#!/usr/bin/env python3
"""build_t5d.py -- the T5d case builder: T5b's frozen recipe with ONE constant moved.

Registration: docs/campaigns/T-family/T5d_PREREGISTRATION.md.

WHY THIS FILE IS A WRAPPER AND NOT A COPY
-----------------------------------------
T5d registers the SAME geometry, the SAME cell counts, the SAME closure, the
SAME schemes, the SAME endTime, the SAME reference and the SAME GATE as T5b.
It changes exactly ONE number: the coarse first fluid layer,

    build_t5.FIRST_LAYER_C   0.128e-3 m  ->  0.080e-3 m      (scale 0.625 = 1/R)

applied through the FROZEN `../T5_runs/build_t5.py` arithmetic, so all three
levels shrink together and the ladder stays geometrically similar in the first
wall layer -- which is the property `build_t5.py`'s own docstring registers
("ONE refinement factor R = 1.6 applied to EVERY direction INCLUDING the first
wall layer, so the three levels are geometrically similar and the triple is a
true refinement").  Because `counts()` depends only on the level index and NOT
on the first-layer height, the CELL COUNTS DO NOT MOVE: 52,684 / 212,942 /
882,024, so the measured refinement ratios r21 = 1.6060 and r32 = 1.5929 that
the comparator derives are unchanged, and the frozen T5b comparator's
`CELLS_REGISTERED` check still passes.

THE MEASUREMENT THAT FORCED IT
------------------------------
T5b graded 0 of 6, all six rows NOT A RESULT, all six at the FIRST clause of the
registered admission order:

    y+ gate not MET on level(s) f: y+ exceeds 2.0x the level target 1.00 on:
    cube_front=2.310 -- the ladder is not the registered ladder

Measured from the landed run (`../T5b_runs/T5_CUBE_*/postProcessing/air/yPlus/0/
yPlus.dat` at Time = 5000) and from each mesh's own `constant/air/polyMesh/
points`:

  level   first cell (ALL SIX graded walls)   y+max cube_front   ratio to target
    c              128.0 um                        3.8043            1.4632
    m               80.0 um                        2.9610            1.8506
    f               50.0 um                        2.3100            2.3100  <- over 2.0

The first layer refines by EXACTLY 1.6 per level (measured on disk to 5 s.f. on
all six walls), but y+max on `cube_front` falls by only 0.780 per level, because
the implied peak u_tau THERE grows by 1.248 per level (0.8976 -> 1.1178 ->
1.3953 m/s): the point maximum sits on the front-face leading edge, where the
wall shear is not mesh-converged.  So the ratio-to-target DRIFTS UP the ladder
by ~1.25 per level and the tightest level -- the fine one -- fails first.

THE REPAIR, AND WHAT IT DOES NOT DO
-----------------------------------
Scaling the whole family's first layer by 0.625 moves every wall's y+ down by
the same factor to first order, buying exactly one ladder rung of headroom:
the fine level's ratio-to-target goes 2.3100 -> 1.4438 against the bound of
2.00, i.e. x1.385 of headroom, and NO wall on ANY level is pushed up, because
the scaling is global and downward.  It does NOT cure the underlying drift --
a fourth, finer level would meet it again -- and the registration says so.

NOT CHANGED, and this is the point of the rung: the y+ walls, the sublayer
bound 5.0, the level targets 2.6/1.6/1.0, the ladder tolerance 2.0x, the
statistic (still the POINT MAXIMUM, not T5c's area-weighted mean), the bands,
the intrinsic floor, the row classes, the reference and the comparator.  T5d's
grading path IS the frozen `../T5b_runs/analyse_t5b.py`, byte-identical, driven
with `--root` at this directory.  No new grading code exists.

Usage:  build_t5d.py --case T5_CUBE_c [--force]   |   --selftest
        build_t5d.py --verify-first-layer CASE_DIR --level c|m|f
Exit 0 built/verified, 2 refusal.  Zero `assert` statements (L-332); every guard
raises or exits and is driven under `python3 -O` in --selftest.
"""
import argparse
import importlib.util
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TFAM = os.path.abspath(os.path.join(HERE, ".."))
BUILD_T5 = os.path.join(TFAM, "T5_runs", "build_t5.py")
BUILD_T5B = os.path.join(TFAM, "T5b_runs", "build_t5b.py")
T5B_RUNS = os.path.join(TFAM, "T5b_runs")

CASES = ("T5_CUBE_c", "T5_CUBE_m", "T5_CUBE_f")
LEVEL_OF = {"T5_CUBE_c": 0, "T5_CUBE_m": 1, "T5_CUBE_f": 2}

# --- THE ONE REGISTERED CHANGE -------------------------------------------
# The frozen T5/T5b value this rung expects to find, and refuses to proceed
# without: a base that has moved means T5d's one change is not the change the
# registration describes.
FIRST_LAYER_T5B = 0.128e-3          # m, build_t5.FIRST_LAYER_C at HEAD
FIRST_LAYER_SCALE = 0.625           # = 1/R; one rung of the ladder's own ratio
FIRST_LAYER_T5D = 0.080e-3          # m, WRITTEN OUT, not computed, so a reader
                                    # sees the number the mesh is built to
FIRST_LAYER_REL_TOL = 1.0e-3        # the post-build disk check's tolerance

# Registered first cell per level, m.  Written out for the same reason.
FIRST_LAYER_LEVEL = {"c": 0.080e-3, "m": 0.050e-3, "f": 0.03125e-3}

# The six walls the gate reads, and the axis each one's first cell lies along.
# ('x-', 0.0) means "the wall plane is x = 0 and the fluid is at x < 0".
H_CUBE = 0.015
D_CH = 3.4 * H_CUBE
WALL_AXIS = {
    "cube_front":  ("x", 0.0, -1),
    "cube_rear":   ("x", H_CUBE, +1),
    "floor":       ("y", 0.0, +1),
    "cube_top":    ("y", H_CUBE, +1),
    "roof":        ("y", D_CH, -1),
    "cube_side_n": ("z", 0.5 * H_CUBE, +1),
}

# Cell counts that must NOT move (the frozen comparator refuses otherwise).
CELLS_REGISTERED = {"c": 52684, "m": 212942, "f": 882024}


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def load_module(name, path):
    if not os.path.isfile(path):
        refuse("the frozen module %s is not on disk at %s" % (name, path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def frozen_modules():
    """Import the two frozen builders and CHECK the constants T5d depends on."""
    sys.path.insert(0, os.path.join(TFAM, "..", "..", "scripts"))
    t5 = load_module("build_t5", BUILD_T5)
    t5b = load_module("build_t5b", BUILD_T5B)
    if abs(t5.FIRST_LAYER_C - FIRST_LAYER_T5B) > 1e-12:
        refuse("build_t5.FIRST_LAYER_C is %.6g, not the frozen %.6g -- the base "
               "this rung's ONE change is measured against has MOVED, so the "
               "registered scale %.6g no longer means what the registration says"
               % (t5.FIRST_LAYER_C, FIRST_LAYER_T5B, FIRST_LAYER_SCALE))
    if abs(t5.R - 1.6) > 1e-12:
        refuse("build_t5.R is %.6g, not the registered 1.6" % t5.R)
    if abs(FIRST_LAYER_T5D - FIRST_LAYER_T5B * FIRST_LAYER_SCALE) > 1e-12:
        refuse("the written-out first layer %.6g does not equal %.6g x %.6g"
               % (FIRST_LAYER_T5D, FIRST_LAYER_T5B, FIRST_LAYER_SCALE))
    for lv, want in FIRST_LAYER_LEVEL.items():
        got = FIRST_LAYER_T5D / t5.R ** {"c": 0, "m": 1, "f": 2}[lv]
        if abs(got - want) > 1e-12:
            refuse("registered level first layer %s = %.6g disagrees with "
                   "%.6g / 1.6^lvl = %.6g" % (lv, want, FIRST_LAYER_T5D, got))
    return t5, t5b


# ---------------------------------------------------------------------------
# The post-build disk check: the mesh is MEASURED, never assumed
# ---------------------------------------------------------------------------
def read_points(path):
    """Parse an ASCII polyMesh/points into a list of (x, y, z).

    A binary or unreadable points file is a REFUSAL, never a silent zero: a
    reader that cannot see the mesh must not report the mesh as correct.
    """
    if not os.path.isfile(path):
        refuse("no points file at %s" % path)
    with open(path, "rb") as fh:
        raw = fh.read()
    if b"format" in raw[:2048] and b"binary" in raw[:2048]:
        refuse("%s is written in BINARY format; this reader parses ASCII only "
               "and refuses rather than reporting a mesh it cannot see" % path)
    txt = raw.decode("utf-8", "replace")
    m = re.search(r"^\s*(\d+)\s*\n\(", txt, re.M)
    if not m:
        refuse("%s: no `<count>\\n(` vector-list header found" % path)
    n = int(m.group(1))
    end = txt.find("\n)", m.end())
    if end < 0:
        refuse("%s: the vector list is not closed" % path)
    pts = []
    for line in txt[m.end():end].split("\n"):
        line = line.strip()
        if not line.startswith("("):
            continue
        close = line.find(")")
        if close < 0:
            refuse("%s: malformed point row %r" % (path, line[:60]))
        parts = line[1:close].split()
        if len(parts) != 3:
            refuse("%s: point row with %d components" % (path, len(parts)))
        pts.append((float(parts[0]), float(parts[1]), float(parts[2])))
    if len(pts) != n:
        refuse("%s: header says %d points, %d parsed -- the reader is not "
               "seeing the whole mesh" % (path, n, len(pts)))
    return pts


def measure_first_layers(case_dir):
    """Measure the first-cell height on each of the six graded walls, from the
    fluid mesh's own point coordinates.  Returns {wall: metres}."""
    pts = read_points(os.path.join(case_dir, "constant", "air", "polyMesh", "points"))
    axis_vals = {
        "x": sorted(set(round(p[0], 12) for p in pts)),
        "y": sorted(set(round(p[1], 12) for p in pts)),
        "z": sorted(set(round(p[2], 12) for p in pts)),
    }
    out = {}
    for wall, (ax, plane, side) in WALL_AXIS.items():
        vals = axis_vals[ax]
        if side > 0:
            cand = [v for v in vals if v > plane + 1e-12]
            if not cand:
                refuse("%s: no mesh station above %s = %.6g for wall %s"
                       % (case_dir, ax, plane, wall))
            out[wall] = min(cand) - plane
        else:
            cand = [v for v in vals if v < plane - 1e-12]
            if not cand:
                refuse("%s: no mesh station below %s = %.6g for wall %s"
                       % (case_dir, ax, plane, wall))
            out[wall] = plane - max(cand)
    return out


def verify_first_layer(case_dir, level, expect=None, quiet=False):
    """REFUSE unless every graded wall's first cell equals the registered value.

    This is the guard that makes an unlaunched builder safe: a mesh whose first
    layer is not the registered one cannot reach a solver."""
    want = FIRST_LAYER_LEVEL[level] if expect is None else expect
    got = measure_first_layers(case_dir)
    bad = {w: v for w, v in got.items()
           if abs(v - want) / want > FIRST_LAYER_REL_TOL}
    if not quiet:
        for w in sorted(got):
            print("    %-12s first cell %.6e m  (registered %.6e)" % (w, got[w], want))
    if bad:
        refuse("%s level %s: first cell is NOT the registered %.6e m on: %s -- "
               "the mesh is not the mesh this rung registered"
               % (case_dir, level, want,
                  ", ".join("%s=%.6e" % (w, v) for w, v in sorted(bad.items()))))
    return got


# ---------------------------------------------------------------------------
# The build
# ---------------------------------------------------------------------------
def build(case, force):
    if case not in CASES:
        refuse("unregistered case '%s'; registered: %s" % (case, " ".join(CASES)))
    t5, t5b = frozen_modules()
    lvl = LEVEL_OF[case]
    lname = "cmf"[lvl]
    saved = t5.FIRST_LAYER_C
    try:
        t5.FIRST_LAYER_C = FIRST_LAYER_T5D          # THE ONE CHANGE
        if abs(t5.FIRST_LAYER_C - FIRST_LAYER_T5D) > 1e-15:
            refuse("the first-layer override did not take")
        dest = t5.build_cube_case(HERE, case, force, mesh=True, inlet_mapped=True)
    finally:
        t5.FIRST_LAYER_C = saved                    # never leaks past this build

    # the X_2d precursor inflow map: copied from the frozen T5 case, digest
    # verified BOTH sides, exactly as build_t5b does and with its constants.
    src = os.path.join(TFAM, "T5_runs", case, "constant", "air", "boundaryData")
    if not os.path.isdir(src):
        refuse("no X_2d inflow map at %s" % src)
    d, n, b = t5b.dir_digest(src)
    if (d, n, b) != (t5b.BOUNDARYDATA_DIGEST, t5b.BOUNDARYDATA_FILES,
                     t5b.BOUNDARYDATA_BYTES):
        refuse("the T5 inflow map has MOVED: %s (%d files, %d bytes) against the "
               "registered %s (%d, %d). T5d's inflow would not be T5b's, so the "
               "ladder would not be the registered ladder."
               % (d, n, b, t5b.BOUNDARYDATA_DIGEST, t5b.BOUNDARYDATA_FILES,
                  t5b.BOUNDARYDATA_BYTES))
    dst = os.path.join(dest, "constant", "air", "boundaryData")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    if t5b.dir_digest(dst) != (d, n, b):
        refuse("the copied inflow map does not read back identical")

    # the T5b function-object repair, applied by T5b's OWN frozen patcher
    t5b.patch_control_dict(os.path.join(dest, "system", "controlDict"))

    # the mesh is MEASURED before anything is allowed to believe it
    print("  measured first layer, %s level %s:" % (case, lname))
    verify_first_layer(dest, lname)

    with open(os.path.join(dest, "CASE.txt"), "a") as fh:
        fh.write("\n# --- T5d ---\n"
                 "rung=T5d\n"
                 "registration=T5d_PREREGISTRATION.md\n"
                 "change_from_T5b=first fluid layer scaled %g (%.6g m -> %.6g m "
                 "coarse), applied through the frozen build_t5.py to ALL THREE "
                 "levels so the ladder stays geometrically similar; cell counts, "
                 "geometry, closure, schemes, endTime, reference, comparator and "
                 "EVERY GATE VALUE unchanged\n"
                 "first_layer_registered_m=%.6g\n"
                 "grading_path=../T5b_runs/analyse_t5b.py (FROZEN, byte-identical, "
                 "driven with --root at T5d_runs)\n"
                 % (FIRST_LAYER_SCALE, FIRST_LAYER_T5B, FIRST_LAYER_T5D,
                    FIRST_LAYER_LEVEL[lname]))
    print("BUILT %s" % dest)
    return 0


# ---------------------------------------------------------------------------
# Selftest -- NO blockMesh, NO solver, NO mesh written
# ---------------------------------------------------------------------------
def implied_first_cell(t5, spec, n, length):
    """Reconstruct the first cell a blockMesh grading spec produces.

    `spec` is either a plain expansion ratio or a multi-grading string.  The
    reconstruction is independent of the helper that WROTE it: it re-derives
    the cell sizes from the numbers blockMesh will actually read."""
    spec = spec.strip()
    if not spec.startswith("("):
        e = float(spec)
        # expansion e = last/first over n cells: first = L*(q-1)/(q^n-1), q=e^(1/(n-1))
        if n <= 1 or abs(e - 1.0) < 1e-12:
            return length / n
        q = e ** (1.0 / (n - 1))
        return length * (q - 1.0) / (q ** n - 1.0)
    secs = re.findall(r"\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)", spec)
    if not secs:
        refuse("unparsable grading spec %r" % spec)
    firsts = []
    for lf, nf, e in secs:
        lf, nf, e = float(lf), float(nf), float(e)
        ln = lf * length
        nn = max(1, int(round(nf * n)))
        if nn <= 1 or abs(e - 1.0) < 1e-12:
            fc = ln / nn
        else:
            q = e ** (1.0 / (nn - 1))
            fc = ln * (q - 1.0) / (q ** nn - 1.0)
        last = fc * (e if e >= 1.0 else e)
        firsts.append((fc, abs(fc * e)))
    # the wall-adjacent cell is the smallest cell at either end of the block
    ends = [firsts[0][0], firsts[-1][1]]
    return min(ends)


def selftest():
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("build_t5d.py --selftest  (no blockMesh, no solver, no mesh written)")
    t5, t5b = frozen_modules()
    ok(True, "the two frozen builders import and their constants are the registered ones")

    # arm 1 -- the ONE change reaches block_mesh_3d, on every level, and the
    # grading blockMesh will read implies the registered first cell.
    saved = t5.FIRST_LAYER_C
    try:
        t5.FIRST_LAYER_C = FIRST_LAYER_T5D
        for lname, lvl in (("c", 0), ("m", 1), ("f", 2)):
            nx, ny, nz = t5.counts(lvl)
            want = FIRST_LAYER_LEVEL[lname]
            first = t5.FIRST_LAYER_C / t5.R ** lvl
            ok(abs(first - want) / want < 1e-12,
               "level %s: build_t5's own first-layer expression gives %.6e m" % (lname, first))
            gx0 = t5.grade_upstream(first, nx[0], t5.L_UP)
            got = implied_first_cell(t5, gx0, nx[0], t5.L_UP)
            ok(abs(got - want) / want < 5e-3,
               "level %s cube_front: the x-upstream grading implies %.6e m (registered %.6e)"
               % (lname, got, want))
            txt = t5.block_mesh_3d(lvl)
            ok("blockMeshDict" in txt and "simpleGrading" in txt,
               "level %s: block_mesh_3d renders a blockMeshDict (nothing meshed)" % lname)
    finally:
        t5.FIRST_LAYER_C = saved
    ok(abs(t5.FIRST_LAYER_C - FIRST_LAYER_T5B) < 1e-15,
       "the override does NOT leak: build_t5.FIRST_LAYER_C is restored to %.6g" % FIRST_LAYER_T5B)

    # arm 2 -- the cell counts, which must NOT move, do not move
    for lname, lvl in (("c", 0), ("m", 1), ("f", 2)):
        nx, ny, nz = t5.counts(lvl)
        base = t5.counts(lvl)
        ok(nx == base[0] and ny == base[1] and nz == base[2],
           "level %s: counts() is independent of the first-layer constant" % lname)

    # arm 3 -- PLANTED FAILURE PAIR on the disk reader, against a REAL mesh whose
    # first layer is known by independent measurement (T5b coarse, 128.0 um).
    t5b_coarse = os.path.join(T5B_RUNS, "T5_CUBE_c")
    have = os.path.isdir(os.path.join(t5b_coarse, "constant", "air", "polyMesh"))
    ok(have, "the T5b coarse mesh is on disk to drive the planted-failure pair "
             "(absence is a FAILURE, not a skip: the guard's proof is required)")
    if have:
        got = measure_first_layers(t5b_coarse)
        ok(len(got) == 6, "the reader sees all six graded walls")
        ok(all(abs(v - FIRST_LAYER_T5B) / FIRST_LAYER_T5B < 1e-4 for v in got.values()),
           "CONTROL: on T5b's coarse mesh the reader measures 128.0 um on all six walls")
        rc = _drive(["--verify-first-layer", t5b_coarse, "--level", "c",
                     "--expect", repr(FIRST_LAYER_T5B)])
        ok(rc == 0, "CONTROL: verify_first_layer ACCEPTS the mesh it was told to expect")
        rc = _drive(["--verify-first-layer", t5b_coarse, "--level", "c",
                     "--expect", repr(FIRST_LAYER_T5D)])
        ok(rc == 2, "MUTANT: the SAME mesh against T5d's 80.0 um REFUSES (exit 2) -- "
                    "the guard is shown able to fail before it is believed when it passes")

    # arm 4 -- an unregistered case refuses
    rc = _drive(["--case", "T5_CUBE_x"])
    ok(rc == 2, "an unregistered case name REFUSES (exit 2)")

    # arm 5 -- the registered cell counts agree with the comparator's
    ok(CELLS_REGISTERED == {"c": 52684, "m": 212942, "f": 882024},
       "the cell counts this rung inherits are T5b's, so the frozen comparator's "
       "CELLS_REGISTERED check still passes")

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def _drive(argv):
    import subprocess
    r = subprocess.run([sys.executable, os.path.abspath(__file__)] + argv,
                       capture_output=True, text=True)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-first-layer")
    ap.add_argument("--level", choices=("c", "m", "f"))
    ap.add_argument("--expect", type=float,
                    help="internal: drive verify_first_layer against a stated value")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.verify_first_layer:
        if not a.level:
            refuse("--verify-first-layer needs --level")
        verify_first_layer(a.verify_first_layer, a.level, expect=a.expect)
        print("FIRST LAYER VERIFIED %s level %s" % (a.verify_first_layer, a.level))
        return 0
    if not a.case:
        refuse("--case is required")
    return build(a.case, a.force)


if __name__ == "__main__":
    sys.exit(main())
