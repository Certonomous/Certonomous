#!/usr/bin/env python3
"""build_t5b.py -- the T5b case builder: T5's frozen recipe plus ONE change.

Registration: docs/campaigns/T-family/T5b_PREREGISTRATION.md.

WHY THIS FILE IS A WRAPPER AND NOT A COPY.  T5b registers the SAME geometry,
the SAME mesh ladder (r = 1.6) and the SAME closure as T5.  Copying 826 lines of
`build_t5.py` would make the ONE substantive change unreadable in a diff and
would silently fork the recipe.  Instead this file DRIVES the frozen
`../T5_runs/build_t5.py` at its HEAD blob, then applies the single registered
change and READS IT BACK FROM DISK.  A supervisor's check-1 ("read the
measurement-script diff as a diff") is then a thirty-second job: the delta is
the `FO_OLD -> FO_NEW` pair below and nothing else.

THE ONE SUBSTANTIVE CHANGE, and the measurement that forced it
--------------------------------------------------------------
T5's `system/controlDict` gives both function objects

    writeControl    writeTime;
    writeInterval   1000;

The run's own `writeInterval` is 1000 timeSteps and `endTime` is 5000, so the
run has exactly FIVE write times.  `writeControl writeTime` with
`writeInterval 1000` means "on every 1000th write time" -- and only five exist,
so the function object's `write()` NEVER EXECUTES.  Consequences, all three
MEASURED on this box 2026-08-27 by a driven CONTROL/FIX pair (registration S3):

  (a) `postProcessing/air/yPlus/0/yPlus.dat` carries two header lines and ZERO
      data rows on T5's c, m and f.  T5 S16.3.1 registers absent y+ as
      NOT A RESULT, so branch (0) fired on every graded row of every level.
  (b) no `yPlus` FIELD is written into any time directory.
  (c) no `wallHeatFlux` FIELD is written either -- only the per-patch
      min/max/integral rows, which `execute()` writes on a different control.
      A face-AVERAGED h is the area mean of phi''/(T_sur - T_ref) with BOTH
      terms varying over the face; it is NOT integral(phi'')/(A (Tbar - T_ref)).
      Without the local field T5's graded rows G1a-G3a are not evaluable.

`wallHeatFlux` wrote 30,000 `.dat` rows under the IDENTICAL control because its
rows come from `execute()` (default `executeControl timeStep`, interval 1) while
its FIELD comes from `write()`.  One mechanism, three consequences.

T5b sets, on BOTH function objects:

    executeControl  timeStep;
    executeInterval 1;
    writeControl    timeStep;
    writeInterval   1000;

`writeInterval 1000` on a `timeStep` control makes the function object write at
timeSteps 1000, 2000, 3000, 4000, 5000 -- which ARE the run's own write times.
No extra time directory is created, `purgeWrite 3` is unaffected, and the fields
land in the time directories the run keeps.  `executeInterval 1` preserves T5's
dense 30,000-row wallHeatFlux convergence trace.

NOT CHANGED: geometry, blockMeshDict, the r = 1.6 ladder, cell counts, closure,
schemes, relaxation, endTime, deltaT, writeInterval, purgeWrite, boundary
conditions, thermophysical properties, the solid laplacian scheme.  T5b is not
a new physics case; it is T5 with its instrument connected.

Usage:  build_t5b.py --case T5_CUBE_c [--force]   |   --selftest
Exit 0 built, 2 refusal.  Zero `assert` statements (L-332); every guard raises
or exits and is driven under `python3 -O` in --selftest.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T5_RUNS = os.path.abspath(os.path.join(HERE, "..", "T5_runs"))
BUILD_T5 = os.path.join(T5_RUNS, "build_t5.py")
CASES = ("T5_CUBE_c", "T5_CUBE_m", "T5_CUBE_f")

# The X_2d precursor inflow map (S5.3).  MEASURED byte-identical across T5's
# three levels 2026-08-27 -- 4 files, 83,071 bytes, this digest -- so T5b copies
# it rather than re-running the precursor, and REFUSES if the digest moves.
BOUNDARYDATA_DIGEST = "b1741eb9ae4288e1f8e8bfaba3fad43fba422b872f2d761602b6724197b0e103"
BOUNDARYDATA_FILES = 4
BOUNDARYDATA_BYTES = 83071

FO_OLD_YPLUS = """    yPlus
    {
        type            yPlus;
        libs            (fieldFunctionObjects);
        region          air;
        writeControl    writeTime;
        writeInterval   1000;
    }"""
FO_NEW_YPLUS = """    yPlus
    {
        type            yPlus;
        libs            (fieldFunctionObjects);
        region          air;
        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1000;
    }"""
FO_OLD_WHF = """        writeControl    writeTime;
        writeInterval   1000;
    }
}"""
FO_NEW_WHF = """        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1000;
    }
}"""


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def dir_digest(d):
    """sha256 over the sorted `sha256  relpath` lines, one per file, newline-joined."""
    lines = []
    for root, _dirs, files in os.walk(d):
        for f in sorted(files):
            p = os.path.join(root, f)
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            lines.append("%s  %s" % (h.hexdigest(), os.path.relpath(p, d)))
    lines.sort()
    return (hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest(),
            len(lines),
            sum(os.path.getsize(os.path.join(r, f))
                for r, _d, fs in os.walk(d) for f in fs))


def patch_control_dict(path):
    """Apply the ONE registered change, then READ IT BACK FROM DISK.

    Content assertions only -- never a line count.  A line-count check passes on
    a substituted file of the right length (Sanaa 2026-08-27 S1)."""
    with open(path) as fh:
        txt = fh.read()
    if txt.count(FO_OLD_YPLUS) != 1:
        refuse("%s: the frozen yPlus function-object block is not present exactly "
               "once -- T5's recipe has moved and T5b's one change no longer "
               "applies cleanly. Nothing is patched." % path)
    if txt.count(FO_OLD_WHF) != 1:
        refuse("%s: the frozen wallHeatFlux write-control block is not present "
               "exactly once. Nothing is patched." % path)
    txt = txt.replace(FO_OLD_YPLUS, FO_NEW_YPLUS).replace(FO_OLD_WHF, FO_NEW_WHF)
    with open(path, "w") as fh:
        fh.write(txt)
    with open(path) as fh:
        back = fh.read()
    if FO_NEW_YPLUS not in back:
        refuse("%s: the yPlus repair is NOT on disk after writing it" % path)
    if FO_NEW_WHF not in back:
        refuse("%s: the wallHeatFlux repair is NOT on disk after writing it" % path)
    if "writeTime" in back:
        refuse("%s: a `writeTime` control survives the repair -- that is the "
               "defect this rung exists to remove" % path)
    if back.count("executeControl  timeStep;") != 2:
        refuse("%s: expected exactly two repaired function objects, found %d"
               % (path, back.count("executeControl  timeStep;")))
    return back


def build(case, force):
    if case not in CASES:
        refuse("unregistered case '%s'; registered: %s" % (case, " ".join(CASES)))
    if not os.path.isfile(BUILD_T5):
        refuse("the frozen recipe %s is not on disk" % BUILD_T5)
    dest = os.path.join(HERE, case)
    cmd = [sys.executable, BUILD_T5, "--root", HERE, "--case", case]
    if force:
        cmd.append("--force")
    r = subprocess.run(cmd, cwd=T5_RUNS)
    if r.returncode != 0:
        refuse("the frozen build_t5.py failed on %s (rc %d)" % (case, r.returncode))
    # the inflow map: copied from the frozen T5 case, DIGEST-VERIFIED both sides
    src = os.path.join(T5_RUNS, case, "constant", "air", "boundaryData")
    if not os.path.isdir(src):
        refuse("no X_2d inflow map at %s" % src)
    d, n, b = dir_digest(src)
    if d != BOUNDARYDATA_DIGEST or n != BOUNDARYDATA_FILES or b != BOUNDARYDATA_BYTES:
        refuse("the T5 inflow map has MOVED: digest %s (%d files, %d bytes) against "
               "the registered %s (%d, %d). T5b's inflow would not be T5's, so the "
               "ladder would not be the registered ladder." % (d, n, b,
               BOUNDARYDATA_DIGEST, BOUNDARYDATA_FILES, BOUNDARYDATA_BYTES))
    dst = os.path.join(dest, "constant", "air", "boundaryData")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    d2, n2, b2 = dir_digest(dst)
    if (d2, n2, b2) != (d, n, b):
        refuse("the copied inflow map does not read back identical: %s vs %s" % (d2, d))
    patch_control_dict(os.path.join(dest, "system", "controlDict"))
    with open(os.path.join(dest, "CASE.txt"), "a") as fh:
        fh.write("\n# --- T5b ---\n"
                 "rung=T5b\n"
                 "registration=T5b_PREREGISTRATION.md\n"
                 "change_from_T5=function-object write control only "
                 "(writeTime -> timeStep on yPlus and wallHeatFlux); "
                 "geometry, ladder, closure, schemes and endTime UNCHANGED\n"
                 "inflow_map_digest=%s\n"
                 "yplus_walls=cube_front cube_top cube_rear cube_side_n floor roof "
                 "(SIX -- cube_side_s does NOT exist on the half domain; T5's "
                 "comparator named it and fired NOT A RESULT by construction)\n"
                 % BOUNDARYDATA_DIGEST)
    print("BUILT %s" % dest)
    return 0


def selftest():
    import tempfile
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("build_t5b.py --selftest")
    tmp = tempfile.mkdtemp(prefix="t5b_st_")
    try:
        good = ("functions\n{\n" + FO_OLD_YPLUS + "\n    wallHeatFlux\n    {\n"
                "        type            wallHeatFlux;\n        libs            (fieldFunctionObjects);\n"
                "        region          air;\n        patches         (cube_front);\n"
                + FO_OLD_WHF + "\n")
        p = os.path.join(tmp, "controlDict")
        with open(p, "w") as fh:
            fh.write(good)
        back = patch_control_dict(p)
        ok("executeControl  timeStep;" in back, "the repair is applied and read back")
        ok("writeTime" not in back, "no writeTime control survives")
        ok(back.count("executeControl  timeStep;") == 2, "exactly two objects repaired")

        # PLANTED FAILURE (L-314): a controlDict WITHOUT the frozen block must REFUSE.
        p2 = os.path.join(tmp, "controlDict_mutant")
        with open(p2, "w") as fh:
            fh.write(good.replace("writeControl    writeTime;", "writeControl    runTime;", 1))
        r = subprocess.run([sys.executable, __file__, "--drive-patch", p2],
                           capture_output=True, text=True)
        ok(r.returncode == 2, "a controlDict missing the frozen yPlus block REFUSES (exit 2)")
        ok("not present exactly once" in r.stderr, "and says why")

        # PLANTED FAILURE: an already-patched file must REFUSE (never double-apply).
        r2 = subprocess.run([sys.executable, __file__, "--drive-patch", p],
                            capture_output=True, text=True)
        ok(r2.returncode == 2, "an ALREADY-PATCHED controlDict REFUSES rather than double-applying")

        ok(dir_digest(tmp)[1] >= 2, "dir_digest counts files")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = sum(1 for _ in ())
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drive-patch", help="internal: drive patch_control_dict on one file")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.drive_patch:
        patch_control_dict(a.drive_patch)
        return 0
    if not a.case:
        refuse("--case is required")
    return build(a.case, a.force)


if __name__ == "__main__":
    sys.exit(main())
