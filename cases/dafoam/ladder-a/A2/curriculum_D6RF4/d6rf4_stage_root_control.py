#!/usr/bin/env python3
# ===========================================================================
# D6RF4 ROOT-STAGING CONTROL -- the driven discriminator for d6rf4_stage_root.sh
#
# WHY THIS FILE EXISTS.
#
# `d6rf4_launcher_guard_drive.py` passes 27/27, and the strings `L-251`,
# `run root`, `stat -c`, `777` and `BASE` return NOTHING in it: all 27 legs are
# freeze- and permission-shaped.  THE GUARD THAT ACTUALLY STOPPED THIS ARM AT
# 16:33:09Z WAS IN NONE OF THE 27.  That is the SECOND measured coverage hole
# in this one item, after the age-datum guard sat outside all 100 of its suites.
#
# `FAIL_OPEN_GATE_AUDIT.md` §28.19.2 rules what to do about it: a suite that
# passes identically before and after a repair has measured YOUR SUITE, not
# your fix -- so re-aim it.  `§28.19.3`: THE EVIDENCE FOR A REPAIR IS A CONTROL
# THAT FAILS ON THE DEFECTIVE STATE AND PASSES ON THE REPAIRED ONE.  A guard
# with no control is a guard nobody has shown works, and this item has now been
# bitten twice by exactly that.  THIS FILE IS THAT CONTROL.
#
# ---------------------------------------------------------------------------
# WHAT IT DRIVES, AND WHY IT IS NOT A RE-IMPLEMENTATION.
#
# The three assumptions this repair exists to satisfy live in
# `d6rf4_run_arm.sh`, which is FROZEN and is NOT EDITED by this repair.  So
# this control does not re-implement them.  It EXTRACTS THEM VERBATIM FROM THE
# LAUNCHER'S OWN BYTES, BY LINE NUMBER --
#
#     :515       the L-251 mode assertion
#     :518-527   the nine $BASE-side instrument md5 assertions
#     :632-636   the undeformed reference mesh, via the launcher's own
#                `field_path` / `assert_field` helpers, extracted with them
#
# -- and evaluates those exact lines against a sandbox root that
# `d6rf4_stage_root.sh` built.  If the launcher is renumbered, the extracted
# lines stop matching their registered shapes and THIS CONTROL REFUSES (exit 2)
# rather than testing the wrong lines and reporting a pass.
#
# ---------------------------------------------------------------------------
# BOTH DIRECTIONS, AND THE POSITIVE ONE IS NOT DECORATION.
#
# CLAUDE.md rule 3: a zero from a reader not shown able to see a non-zero is
# not evidence.  Its mirror holds here -- a harness in which EVERYTHING aborts
# would score every failure direction green while proving nothing.  D1 is
# therefore the plant: the same extracted launcher lines, against a properly
# staged root, MUST PASS AND PRINT `LAUNCHER_ASSUMPTIONS_ALL_PASS`.  Every
# refusing direction is only meaningful because D1 passes.
#
# ---------------------------------------------------------------------------
# NOTHING IS LAUNCHED.  No container is created, no queue row is placed, no
# solver runs, and the REGISTERED run root
# `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe`
# IS NEVER TOUCHED -- every direction runs in a throwaway sandbox.  The control
# asserts that at the end and refuses if the registered root appeared.
#
# The sandbox lives in a temp directory and its path is REDACTED to `<sandbox>`
# in the evidence file: CLAUDE.md rule 13, a repository document never cites a
# scratch path.
#
# EXIT CODES:  0 all directions as registered;  1 a direction did not behave as
# registered;  2 REFUSED -- the launcher's shape moved and the anchors no
# longer match, so nothing was driven.
# ===========================================================================
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
LAUNCHER = HERE / "d6rf4_run_arm.sh"
STAGER = HERE / "d6rf4_stage_root.sh"
REGISTERED_BASE = pathlib.Path(
    "/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe")

# THE ANCHORS.  Line numbers AND the shape each line must have.  Both are
# checked: a number alone would silently test whatever moved into that slot.
L_MODE = 515
L_MD5_FIRST, L_MD5_LAST = 518, 527
L_MESH_FIRST, L_MESH_LAST = 632, 636

RE_MODE = re.compile(
    r'^test "\$\(stat -c \'%a\' "\$BASE"\)" = "777" \|\| \{ echo "ABORT L-251 '
    r'run root mode \$\(stat -c \'%a\' "\$BASE"\)"; exit 4; \}\s*$')
RE_MD5 = re.compile(
    r'^\s*echo "\$(MD5_[A-Z0-9_]+)\s+\$BASE/([A-Za-z0-9_.]+)"\s*\|\s*md5sum -c -')
RE_MESH = re.compile(
    r'^\s*BASE_MESH=\$\(field_path "\$BASE/base/constant/polyMesh" points\)')
RE_PIN = re.compile(r'^(MD5_[A-Z0-9_]+)=([0-9a-f]{32})\s*(?:#.*)?$')

results = []       # (verdict, direction, detail)
refusals = []


def refuse(msg):
    print("REFUSE %s" % msg)
    refusals.append(msg)


def load_launcher():
    """Extract the three assumption sites verbatim, with their shapes asserted."""
    lines = LAUNCHER.read_text(errors="replace").splitlines()
    if len(lines) < L_MESH_LAST:
        refuse("the launcher has %d lines; anchor %d is past the end"
               % (len(lines), L_MESH_LAST))
        return None

    mode_line = lines[L_MODE - 1]
    if not RE_MODE.match(mode_line):
        refuse("line %d of the launcher is not the registered L-251 mode "
               "assertion.  Found: %r" % (L_MODE, mode_line))
        return None

    md5_block = lines[L_MD5_FIRST - 1:L_MD5_LAST]
    asserted = [RE_MD5.match(l) for l in md5_block]
    n_assert = sum(1 for m in asserted if m)
    if n_assert != 9:
        refuse("lines %d-%d of the launcher carry %d $BASE-side md5 assertions, "
               "not the registered 9" % (L_MD5_FIRST, L_MD5_LAST, n_assert))
        return None
    for l, m in zip(md5_block, asserted):
        if m is None and not l.lstrip().startswith("#"):
            refuse("line inside %d-%d is neither an assertion nor a comment: %r"
                   % (L_MD5_FIRST, L_MD5_LAST, l))
            return None
    files = [m.group(2) for m in asserted if m]

    mesh_block = lines[L_MESH_FIRST - 1:L_MESH_LAST]
    if not RE_MESH.match(mesh_block[0]):
        refuse("line %d of the launcher is not the registered reference-mesh "
               "read.  Found: %r" % (L_MESH_FIRST, mesh_block[0]))
        return None
    if "$MD5_REF_MESH" not in "\n".join(mesh_block):
        refuse("lines %d-%d do not compare against $MD5_REF_MESH"
               % (L_MESH_FIRST, L_MESH_LAST))
        return None

    # The launcher's own helpers, extracted with the block that calls them, so
    # the mesh check runs through the launcher's `field_path`, not a copy.
    try:
        fp0 = next(i for i, l in enumerate(lines) if l.startswith("field_path() {"))
        af0 = next(i for i, l in enumerate(lines) if l.startswith("assert_field() {"))
        af1 = next(i for i, l in enumerate(lines) if i > af0 and l == "}")
    except StopIteration:
        refuse("could not locate field_path()/assert_field() at column 0 in the "
               "launcher; the mesh assertion cannot be run through its own helpers")
        return None
    helpers = lines[fp0:af1 + 1]

    pins = [l for l in lines if RE_PIN.match(l)]
    names = [RE_PIN.match(l).group(1) for l in pins]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        refuse("the launcher assigns %s more than once; in shell the LAST "
               "assignment wins" % ", ".join(dupes))
        return None
    if "MD5_REF_MESH" not in names:
        refuse("the launcher has no MD5_REF_MESH assignment")
        return None

    return dict(mode=mode_line, md5=md5_block, mesh=mesh_block,
                helpers=helpers, pins=pins, files=files)


def harness(parts, base):
    """The launcher's own lines, verbatim, over an explicit $BASE."""
    body = ["set -uo pipefail",
            "BASE=%s" % shell_quote(str(base)),
            'stage_say() { echo "$*"; }',
            "ARM=P_conv"]
    body += parts["pins"]
    body += parts["helpers"]
    body.append("# ---- launcher :%d" % L_MODE)
    body.append(parts["mode"])
    body.append("# ---- launcher :%d-%d" % (L_MD5_FIRST, L_MD5_LAST))
    body += parts["md5"]
    body.append("# ---- launcher :%d-%d" % (L_MESH_FIRST, L_MESH_LAST))
    body += parts["mesh"]
    body.append('echo "LAUNCHER_ASSUMPTIONS_ALL_PASS"')
    return "\n".join(body) + "\n"


def shell_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def run(cmd, env=None, cwd=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                       text=True, env=e, cwd=cwd)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def stage(base, evid, extra_env=None, stager=None, cwd=None):
    env = {"BASE": str(base), "STAGE_EVID": str(evid)}
    if extra_env:
        env.update(extra_env)
    return run(["bash", str(stager or STAGER)], env=env, cwd=cwd)


def drive_launcher(parts, base, tmp):
    script = tmp / "assumptions.sh"
    script.write_text(harness(parts, base))
    return run(["bash", str(script)])


def record(ok, direction, detail):
    results.append(("OK   " if ok else "FAIL ", direction, detail))


def main():
    parts = load_launcher()
    if parts is None:
        print("\nCONTROL REFUSED -- the launcher's shape has MOVED and NOTHING "
              "WAS DRIVEN.  Testing the wrong lines and reporting a pass is the "
              "failure this refusal exists to prevent.")
        return 2

    launcher_md5 = run(["md5sum", str(LAUNCHER)])[1].split()[0]
    stager_md5 = run(["md5sum", str(STAGER)])[1].split()[0]
    print("D6RF4 ROOT-STAGING CONTROL")
    print("  launcher %s md5=%s  anchors :%d, :%d-%d, :%d-%d VERIFIED IN SHAPE"
          % (LAUNCHER.name, launcher_md5, L_MODE, L_MD5_FIRST, L_MD5_LAST,
             L_MESH_FIRST, L_MESH_LAST))
    print("  stager   %s md5=%s" % (STAGER.name, stager_md5))
    print("  the launcher's %d $BASE-side assertions name: %s"
          % (len(parts["files"]), " ".join(parts["files"])))
    print()

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d6rf4_stage_ctl_"))
    try:
        # ---------------------------------------------------------- ANCHOR
        record(True, "A0 ANCHOR",
               "launcher lines :%d, :%d-%d (9 assertions) and :%d-%d matched "
               "their registered shapes; field_path()/assert_field() extracted "
               "with them, so the mesh check runs through the LAUNCHER'S OWN "
               "helper and not a copy"
               % (L_MODE, L_MD5_FIRST, L_MD5_LAST, L_MESH_FIRST, L_MESH_LAST))

        # ------------------------------------------------- D1  THE PLANT
        b1 = tmp / "d1"
        rc, out = stage(b1, tmp / "d1.evid")
        if rc != 0:
            record(False, "D1 POSITIVE (THE PLANT)",
                   "the stager itself refused rc=%d; nothing downstream is "
                   "interpretable: %s" % (rc, out.strip().splitlines()[-1:]))
        else:
            rc1, out1 = drive_launcher(parts, b1, tmp)
            ok = rc1 == 0 and "LAUNCHER_ASSUMPTIONS_ALL_PASS" in out1
            record(ok, "D1 POSITIVE (THE PLANT)",
                   "staged root -> the launcher's OWN :%d, :%d-%d and :%d-%d "
                   "lines ALL PASS, rc=%d.  THIS IS THE READER SHOWN ABLE TO "
                   "SEE A PASS; every refusal below is evidence only because "
                   "this one does not refuse"
                   % (L_MODE, L_MD5_FIRST, L_MD5_LAST, L_MESH_FIRST,
                      L_MESH_LAST, rc1))

        # -------------------------------------- D2  THE MEASURED FAILURE
        b2 = tmp / "d2_never_created"
        rc2, out2 = drive_launcher(parts, b2, tmp)
        ok = rc2 == 4 and "ABORT L-251" in out2
        record(ok, "D2 ROOT ABSENT",
               "unstaged root -> launcher :%d aborts rc=%d with 'ABORT L-251 "
               "run root mode ' and an EMPTY mode field -- byte-for-byte the "
               "16:33:09Z abort in launcher.queue.out.  THE DEFECT IS "
               "REPRODUCED, not inferred" % (L_MODE, rc2))

        # ------------------------------------------------ D3  MODE WRONG
        b3 = tmp / "d3"
        stage(b3, tmp / "d3.evid")
        os.chmod(b3, 0o775)
        rc3, out3 = drive_launcher(parts, b3, tmp)
        ok = rc3 == 4 and "ABORT L-251" in out3 and "775" in out3
        record(ok, "D3 MODE 775 NOT 777",
               "staged root chmod'd to 775 -> launcher :%d aborts rc=%d naming "
               "775.  L-251 is a MODE gate, not an existence gate, and merely "
               "creating the directory is NOT the repair" % (L_MODE, rc3))

        # ------------- D4  EVERY ONE OF THE NINE ASSERTIONS, INDIVIDUALLY
        b4 = tmp / "d4"
        stage(b4, tmp / "d4.evid")
        pristine = tmp / "d4_pristine"
        shutil.copytree(b4, pristine)
        bad = []
        for f in parts["files"]:
            shutil.rmtree(b4)
            shutil.copytree(pristine, b4)
            os.chmod(b4, 0o777)
            with open(b4 / f, "ab") as fh:
                fh.write(b"\n# PLANTED BYTE -- this file no longer hashes to its pin\n")
            rc4, out4 = drive_launcher(parts, b4, tmp)
            if not (rc4 == 4 and f in out4 and "FAILED" in out4.upper()):
                bad.append("%s(rc=%d)" % (f, rc4))
        record(not bad,
               "D4 ONE MD5 WRONG, DRIVEN %d TIMES" % len(parts["files"]),
               "each of the %d staged instruments corrupted IN TURN -> the "
               "launcher aborts rc=4 at THAT file's own assertion every time; "
               "no assertion sails past.  Untested assertions: %s"
               % (len(parts["files"]), ", ".join(bad) if bad else "NONE"))

        # ------------------------------------------- D5  MESH DIRECTORY GONE
        b5 = tmp / "d5"
        stage(b5, tmp / "d5.evid")
        shutil.rmtree(b5 / "base" / "constant" / "polyMesh")
        rc5, out5 = drive_launcher(parts, b5, tmp)
        ok = rc5 == 5 and "THE DIRECTORY IS ABSENT" in out5
        record(ok, "D5 MESH DIRECTORY ABSENT",
               "polyMesh removed -> launcher :%d-%d aborts rc=%d through its "
               "OWN assert_field, and the abort distinguishes a MISSING "
               "DIRECTORY from a missing field"
               % (L_MESH_FIRST, L_MESH_LAST, rc5))

        # ------------------------------------------- D6  MESH FILE GONE
        b6 = tmp / "d6"
        stage(b6, tmp / "d6.evid")
        for n in ("points", "points.gz"):
            p = b6 / "base" / "constant" / "polyMesh" / n
            if p.exists():
                p.unlink()
        rc6, out6 = drive_launcher(parts, b6, tmp)
        ok = rc6 == 5 and "NEITHER" in out6
        record(ok, "D6 MESH FILE ABSENT UNDER BOTH NAMES",
               "points and points.gz both removed, directory kept -> rc=%d and "
               "the abort says the directory EXISTS but holds NEITHER name, "
               "and prints what is actually there" % rc6)

        # ------------------------------------------- D7  MESH MD5 MOVED
        b7 = tmp / "d7"
        stage(b7, tmp / "d7.evid")
        mesh = b7 / "base" / "constant" / "polyMesh" / "points.gz"
        if not mesh.exists():
            mesh = b7 / "base" / "constant" / "polyMesh" / "points"
        with open(mesh, "ab") as fh:
            fh.write(b"\x00PLANTED")
        rc7, out7 = drive_launcher(parts, b7, tmp)
        ok = rc7 == 5 and "reference mesh md5" in out7
        record(ok, "D7 REFERENCE MESH MD5 MOVED",
               "the undeformed reference mesh perturbed -> rc=%d at the "
               "launcher's MD5_REF_MESH comparison.  A present-but-wrong mesh "
               "is the double-deformation confound that killed D4's arm F, and "
               "presence alone does not satisfy :%d" % (rc7, L_MESH_LAST))

        # ------------------------------- D8  STAGER REFUSES A FOREIGN ROOT
        b8 = tmp / "d8"
        b8.mkdir()
        os.chmod(b8, 0o777)
        (b8 / "ledger.txt").write_text("ITEM=D19T\n")
        rc8, out8 = stage(b8, tmp / "d8.evid")
        ok = rc8 == 43 and "another item" in out8
        record(ok, "D8 STAGER REFUSES A FOREIGN ROOT",
               "a root whose ledger reads ITEM=D19T -> stager rc=%d, and it "
               "REFUSES rather than staging D6RF4 instruments on top of another "
               "item's run root" % rc8)

        # -------------------- D9  STAGER REFUSES A PRE-EXISTING ARM DIRECTORY
        b9 = tmp / "d9"
        stage(b9, tmp / "d9.evid")
        (b9 / "P_conv").mkdir()
        (b9 / "P_conv" / "partial.txt").write_text("1.1 GB of partial result stands in for this\n")
        rc9, out9 = stage(b9, tmp / "d9b.evid")
        still_there = (b9 / "P_conv" / "partial.txt").exists()
        ok = rc9 == 43 and "already exists" in out9 and still_there
        record(ok, "D9 STAGER REFUSES A PRE-EXISTING ARM DIRECTORY",
               "a stale P_conv/ present -> stager rc=%d AND THE PARTIAL RESULT "
               "IS STILL ON DISK (%s).  Recovery is an explicit mv; there is no "
               "rm -rf in the stager" % (rc9, "kept" if still_there else "GONE"))

        # ---------------- D10  STAGER REFUSES A BAD SOURCE BEFORE CREATING
        sandbox_case = tmp / "case_badsrc"
        shutil.copytree(HERE, sandbox_case)
        with open(sandbox_case / "d6rf4_units_assert.py", "ab") as fh:
            fh.write(b"\n# PLANTED\n")
        b10 = tmp / "d10_should_not_exist"
        rc10, out10 = stage(b10, tmp / "d10.evid",
                            stager=sandbox_case / "d6rf4_stage_root.sh")
        ok = rc10 == 41 and "ABORT SOURCE md5" in out10 and not b10.exists()
        record(ok, "D10 BAD SOURCE REFUSED BEFORE ANYTHING IS CREATED",
               "an item-directory instrument that does not hash to the "
               "launcher's pin -> stager rc=%d and the run root WAS NEVER "
               "CREATED (%s).  A half-staged root would move the abort from "
               ":%d to :%d and hide the cause"
               % (rc10, "absent" if not b10.exists() else "CREATED ANYWAY",
                  L_MODE, L_MD5_FIRST))

        # ------------- D11  A LAUNCHER THAT ASSERTS NOTHING IS A REFUSAL
        sandbox_case2 = tmp / "case_noassert"
        shutil.copytree(HERE, sandbox_case2)
        lp = sandbox_case2 / "d6rf4_run_arm.sh"
        kept = [l for l in lp.read_text(errors="replace").splitlines()
                if not RE_MD5.match(l)]
        lp.write_text("\n".join(kept) + "\n")
        b11 = tmp / "d11_should_not_exist"
        rc11, out11 = stage(b11, tmp / "d11.evid",
                            stager=sandbox_case2 / "d6rf4_stage_root.sh")
        ok = rc11 == 40 and "REFUSE-EMPTY" in out11 and not b11.exists()
        record(ok, "D11 A DERIVATION THAT FINDS NOTHING REFUSES",
               "the $BASE-side assertions stripped from a launcher copy -> "
               "stager rc=%d REFUSE-EMPTY.  A stager that quietly staged zero "
               "files would let the launcher abort at :%d exactly as it already "
               "did -- the planted-zero shape in a stager (rule 3)"
               % (rc11, L_MODE))

        # ------------- D12  A DUPLICATE PIN IS A REFUSAL, NOT A LAST-WINS
        sandbox_case3 = tmp / "case_dupepin"
        shutil.copytree(HERE, sandbox_case3)
        lp3 = sandbox_case3 / "d6rf4_run_arm.sh"
        src3 = lp3.read_text(errors="replace").splitlines()
        for i, l in enumerate(src3):
            if l.startswith("MD5_ANCHOR_GATE="):
                src3.insert(i + 1, "MD5_ANCHOR_GATE=" + "0" * 32)
                break
        lp3.write_text("\n".join(src3) + "\n")
        b12 = tmp / "d12_should_not_exist"
        rc12, out12 = stage(b12, tmp / "d12.evid",
                            stager=sandbox_case3 / "d6rf4_stage_root.sh")
        ok = rc12 == 40 and "REFUSE-PIN" in out12 and not b12.exists()
        record(ok, "D12 A DUPLICATE MD5 PIN REFUSES",
               "a second MD5_ANCHOR_GATE= assignment planted in a launcher copy "
               "-> stager rc=%d REFUSE-PIN.  d6rf4_run_arm.sh:92-96 records that "
               "this happened for real and the STALE value came second; in shell "
               "the last assignment wins, so the count is pinned, not the "
               "appearance trusted" % rc12)

        # ------------- D13  IDEMPOTENCE: A PRESENT ROOT IS NOT RE-STAGED
        b13 = tmp / "d13"
        stage(b13, tmp / "d13.evid")
        (b13 / "ledger.txt").open("a").write(
            "ARM=P_conv rc=1 core_min=0.000 note=an-earlier-nonzero-fire\n")
        before = sorted((p.name, p.stat().st_mtime_ns)
                        for p in b13.iterdir() if p.is_file())
        rc13, out13 = stage(b13, tmp / "d13b.evid")
        after = sorted((p.name, p.stat().st_mtime_ns)
                       for p in b13.iterdir() if p.is_file())
        ok = (rc13 == 0 and "D6RF4_ROOT_PRESENT" in out13
              and "CEILING OK" in out13
              and [x for x in before if x[0] != "ledger.txt"]
              == [x for x in after if x[0] != "ledger.txt"])
        record(ok, "D13 IDEMPOTENT, AND THE CEILING GUARD RE-RUNS",
               "a second run over a present root -> rc=%d, D6RF4_ROOT_PRESENT, "
               "NOTHING re-staged and NOTHING removed (instrument mtimes "
               "identical), AND the cumulative ceiling guard runs again.  This "
               "is what puts d6rf3_chain_driver.sh's 'before EVERY arm' clause "
               "in front of a RE-fire, not only the first fire" % rc13)

        # ------------- D14  THE CEILING GUARD ACTUALLY BITES
        b14 = tmp / "d14"
        stage(b14, tmp / "d14.evid")
        with (b14 / "ledger.txt").open("a") as fh:
            fh.write("ARM=P_conv rc=1 core_min=10.000 note=planted-prior-spend\n")
        rc14, out14 = stage(b14, tmp / "d14b.evid")
        ok = rc14 == 42 and "ABORT CEILING" in out14
        record(ok, "D14 THE CEILING GUARD BITES ON A PLANTED PRIOR SPEND",
               "10.000 core-min planted into the ledger -> 10.000 + the 54.00 "
               "cap = 64.000 over the registered 54.00 ceiling -> stager rc=%d.  "
               "An overrun stops the run; it does not get a new budget "
               "(rule 12)" % rc14)

        # ------------- D15  AN UNREADABLE LEDGER IS UNMEASURED, NEVER ZERO
        b15 = tmp / "d15"
        stage(b15, tmp / "d15.evid")
        (b15 / "ledger.txt").unlink()
        rc15, out15 = stage(b15, tmp / "d15b.evid")
        ok = rc15 == 41 and "ledger.txt absent" in out15
        record(ok, "D15 AN ABSENT LEDGER REFUSES, IT IS NOT SPEND 0.0",
               "the ledger removed from a present root -> stager rc=%d.  The "
               "launcher's own G-ROOT.3 is `if [ -f ledger.txt ]` and so passes "
               "VACUOUSLY here printing ledger_clean=yes -- which it did, in "
               "launcher.queue.out, 62 s before the abort" % rc15)

        # ------------------------------------------------- THE FINAL ASSERT
        touched = REGISTERED_BASE.exists()
        record(not touched, "D16 THE REGISTERED RUN ROOT WAS NEVER CREATED",
               "%s after all directions: %s.  Every direction ran in a "
               "throwaway sandbox; this control launches nothing and stages "
               "nothing into the registered root"
               % (REGISTERED_BASE, "PRESENT -- CONTROL VIOLATED ITS OWN BOUND"
                  if touched else "still ABSENT"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(d) for _, d, _ in results)
    for verdict, direction, detail in results:
        print("%s %-*s  %s" % (verdict, width, direction, detail))
    print()
    failed = [d for v, d, _ in results if v.strip() == "FAIL"]
    if failed:
        print("RESULT %d OF %d DIRECTIONS DID NOT BEHAVE AS REGISTERED: %s"
              % (len(failed), len(results), ", ".join(failed)))
        return 1
    print("RESULT ALL %d DIRECTIONS AS REGISTERED" % len(results))
    print("  The repair's evidence is D1 against D2-D7: the SAME extracted "
          "launcher lines pass on a staged root and refuse on every defective "
          "one.  That is a driven discriminator (FAIL_OPEN_GATE_AUDIT.md "
          "§28.19.3), not a suite that passes either way.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
