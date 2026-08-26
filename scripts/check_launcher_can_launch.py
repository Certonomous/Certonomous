#!/usr/bin/env python3
"""A FROZEN LAUNCHER THAT CANNOT LAUNCH -- two checks for one defect class.

Renamed from check_time_dir_globs.py, which named only its first check.  What
this file actually enforces is broader and is worth naming for what it is:
**a launcher can be frozen, hashed, committed and reviewed, and still be unable
to start a single solve.**  T4 shipped one twice in one night.

FOUR INSTANCES OF ONE DEFECT, and the pattern is the finding:

  * T4 guard      -- `[0-9]*` matched `0.orig`, so the guard refused the exact
                     state the next line required.  Caught by ARM 1.
  * T4 alphat     -- a `compressible::` wall function in a case run by an
                     INCOMPRESSIBLE solver; every arm exited rc=1 at zero
                     iterations.  The mesh dry run could not see it, because
                     `blockMesh` and `checkMesh` NEVER READ `0.orig/`.
  * K0d readability -- a readability arm passed while `0/U` was unreadable,
                     because `blockMesh` never reads `0/`.
  * K0f selftest  -- passed with a FAKE SOLVER on PATH.

**Every one of those checks exercised the channel its author was thinking about
rather than the channel that consumes the artifact.**  So ARM 2 runs the REAL
solver for ONE ITERATION and requires it to reach `Time = 1` -- the only arm
that actually consumes `0/`.

  ARM 1  no shell glob is used as a time-directory matcher
  ARM 2  the real solver reaches Time = 1 on the coarse case, in scratch

Exit codes: 0 clean   1 a check failed   2 refusal

--- ARM 1 ---
Flag SHELL GLOBS used as OpenFOAM time-directory matchers.

WHY THIS IS A CHECK AND NOT A THIRD LESSON.  `0.orig` starts with a digit, so
the shell glob `[0-9]*` matches it as readily as it matches `0`, `200` or
`1000.5`.  An OpenFOAM case keeps its tracked initial conditions in `0.orig`,
so a glob written to mean "time directories" silently includes the one
directory that is NOT a time directory and IS the input the tree is rebuilt
from.  Three instances are on the record:

  1. THERMAL_K0_runs/run_cases.sh:70 -- a `rm -rf [0-9]*` trim written that way
     "deleted every case's initial conditions".
  2. K2e_runs/build_cases.py:76 -- the same collision, recorded again.
  3. T4_runs/run_one_t4.sh:62 (2026-08-26) -- a launch guard that died on
     `0.orig` calling it a time directory, while the NEXT line required that
     same `0.orig` to exist.  The launcher could not pass its own guard on any
     case its own builder produced.

A defect class that has bitten three times gets an executable check, not a
paragraph.  This is that check.

WHAT IS CLEAN AND IS NOT FLAGGED.  Python matchers using `re.fullmatch` with
`[0-9]+(\\.[0-9]+)?` are correct -- `0.orig` fails fullmatch -- and so is
`find -regex '.*/[0-9]+(\\.[0-9]+)?'`, because find anchors the whole path.
`foamListTimes -rm` is correct by construction: `0.orig` is not a parseable
time and is invisible to it.  `/proc/[0-9]*` is a pid scan, not a case tree.

SHARED INSTRUMENT.  Filed in scripts/ for verification and cfd as well as
heat-transfer; no team owns it.

Exit codes: 0 clean   1 at least one suspect glob   2 refusal
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys

# a bracket-glob starting at a digit class, in something that looks like a path
# NOTE the tail is `*` ONLY.  `[0-9]+` is a REGEX quantifier -- shell globs
# have no `+` -- so flagging it produced false positives on correctly-anchored
# regexes (`grep -E '^[0-9]+$'`, `sed 's/[0-9]+(\.[0-9]+)?/'`, and the very
# find -regex form that is the REPAIR).  Measured: 61 hits before this
# restriction, and the difference was entirely regex, not globs.
GLOB = re.compile(r"""(?P<pre>[\w"'$}./\]-]*/)?\[0-9\](?P<tail>\*)""")
PROC = re.compile(r"/proc/\[0-9\]")
# a regex context: the glob sits inside a quoted regex or an re.* call
REGEXY = re.compile(r"(re\.|regex|-regex|regextype|\bs/\^|\bsed\b|\bawk\b)")

SHELL_EXT = (".sh", ".bash")


# a glob whose LAST path segment is what we test.
# THE LEADING PATH IS OPTIONAL, AND THAT IS A REPAIR, NOT A LOOSENING.  The
# original form REQUIRED a `/` before the bracket, so a BARE glob -- `for d in
# [0-9]*` or `rm -rf [0-9]*` -- was never extracted and could not be flagged.
# Every fixture in this file's own selftest carried a `/`, so the selftest could
# not see the gap.  MEASURED: `for d in [0-9]*; do :; done` -> 0 hits before.
SEG = re.compile(
    r"""(?:[\w"'$}{./\\-]*/)?(?P<seg>[\w.$-]*\[[0-9!^-]+\][^\s"';)|&]*)""")


def glob_hits_0orig(seg):
    """MEASURED, not guessed: does this shell glob actually match `0.orig`?

    The whole defect is that `[0-9]*` matches `0.orig` as readily as `0`.  So
    rather than judging a pattern by its shape, this DRIVES it: the segment is
    matched against `0.orig` and against a real time name.  A pattern that
    cannot match `0.orig` is not this defect, whatever it looks like --
    `0.[0-9]*`, `[1-9]*` and `[0-9]*.[0-9]*` are all excluded BY MEASUREMENT.
    """
    seg = seg.strip().rstrip('";)|&')
    if not seg:
        return False, False
    try:
        return (fnmatch.fnmatchcase("0.orig", seg),
                fnmatch.fnmatchcase("200", seg) or fnmatch.fnmatchcase("0", seg))
    except re.error:
        return False, False


def scan_text(path, text):
    """THIS CHECKER DOES NOT SCAN ITSELF, and that is a precision decision with
    a number behind it.

    Its selftest fixtures are LITERAL defective patterns held in string
    constants, so scanning its own source flags four of them.  Measured on a
    462-file corpus: including this file gives 11 hits of which 7 are real
    (63.6 %); excluding it gives 7 of 7 (100 %).  NONE of the four is a launcher
    defect -- they are the controls.  A tool that reports its own test data as
    findings trains its readers to skim, which is exactly the failure L-339
    records.

    REGEXY IS APPLIED PER PIPELINE STAGE, NOT PER LINE, AND THAT IS THE
    REPAIR THAT MATTERS.

    The original vetoed the WHOLE LINE if `sed`/`awk`/`regex` appeared anywhere
    on it.  The one genuine hit in this lab reads

        LAST=$(ls -d "$BASE"/[0-9]* 2>/dev/null | sed 's#.*/##' | sort -g | tail -1)

    -- `THERMAL_K0_runs/run_controls.sh:141` -- where the glob and the `sed` are
    SEPARATE STAGES OF A PIPELINE.  One word in a later stage was suppressing a
    real defect in an earlier one.  MEASURED: 0 hits before this change, 1 after.

    Splitting on `|` keeps the suppression exactly where it belongs: a
    `sed 's/^writePrecision  [0-9]*;/.../'` still has its quantifier and its
    `sed` in the SAME stage and is still correctly suppressed.

    KNOWN LIMIT, stated rather than discovered: a pipe inside a quoted regex
    would split mid-argument.  It cannot produce a false
    NEGATIVE on a glob, because a glob in a different stage is still scanned.
    """
    hits = []
    if os.path.abspath(path) == os.path.abspath(__file__):
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for stage in line.split("|"):
            if REGEXY.search(stage):
                continue
            for m in SEG.finditer(stage):
                seg = m.group("seg")
                around = stage[max(0, m.start() - 40):m.end() + 10]
                if PROC.search(around):
                    continue
                bad, times = glob_hits_0orig(seg)
                if bad and times:
                    hits.append((i, line.rstrip(), seg))
                    break
            else:
                continue
            break
    return hits


def files_at_head(root, paths):
    if paths:
        return [(p, open(p).read()) for p in paths if os.path.isfile(p)]
    out = []
    ls = subprocess.run(["git", "-C", root, "ls-tree", "-r", "HEAD",
                         "--name-only"], capture_output=True, text=True)
    if ls.returncode != 0:
        print("REFUSE: could not enumerate HEAD")
        sys.exit(2)
    for rel in ls.stdout.splitlines():
        if rel.endswith(SHELL_EXT):
            b = subprocess.run(["git", "-C", root, "show", "HEAD:" + rel],
                               capture_output=True)
            if b.returncode == 0:
                out.append((rel, b.stdout.decode("utf-8", "replace")))
    return out


def selftest():
    """PLANTED POSITIVE CONTROL.  A checker that has not been shown able to
    find a known instance cannot have its zero believed."""
    bad = 'for d in "$CDIR"/[0-9]*; do\n    [ -d "$d" ] && die "time dir"\ndone\n'
    good = ("while IFS= read -r d; do :; done < <(find \"$CDIR\" -maxdepth 1 "
            "-type d -regextype posix-extended -regex '.*/[0-9]+(\\.[0-9]+)?')\n")
    proc = 'for p in /proc/[0-9]*; do :; done\n'
    # ------------------------------------------------------------------
    # THE PERMANENT POSITIVE-CONTROL FIXTURE (registered 2026-08-26).
    #
    # THIS CHECKER REPORTED "NO HITS" WHILE UNABLE TO FIND THE ONE KNOWN HIT IN
    # THE LAB.  That is standing rule 3 turned on the instrument that hunts
    # absences: A READER NOT SHOWN ABLE TO SEE A NON-ZERO IS NOT EVIDENCE.  The
    # fixture below is a BYTE-COPY of the genuine defect at
    # verification/runs/THERMAL_K0_runs/run_controls.sh:141.  If this checker
    # cannot find it, the checker REFUSES (exit 2) rather than reporting a
    # clean sweep it has not earned.
    #
    # TWO THINGS HID IT, AND EACH HAS ITS OWN FIXTURE BELOW:
    #   * REGEXY vetoed the WHOLE LINE because a LATER PIPELINE STAGE contains
    #     `sed`.  One word downstream suppressed a real defect upstream.
    #   * SEG required a `/` before the bracket, so a BARE `[0-9]*` was never
    #     extracted at all.
    # Every pre-existing fixture in this selftest had a slash and no sed, so
    # none of them could have exposed either.  THAT IS THE SAME DEFECT CLASS
    # THIS FILE EXISTS TO POLICE, ARRIVING IN THE FILE ITSELF.
    KNOWN_HIT = ('LAST=$(ls -d "$BASE"/[0-9]* 2>/dev/null '
                 "| sed 's#.*/##' | sort -g | tail -1)\n")
    KNOWN_HIT_SOURCE = "verification/runs/THERMAL_K0_runs/run_controls.sh:141"
    bare_glob = 'for d in [0-9]*; do :; done\n'

    ok = True
    for label, text, want in (("POSITIVE CONTROL: the known lab hit", KNOWN_HIT, 1),
                              ("a BARE glob, no leading slash", bare_glob, 1),
                              ("the T4 defect verbatim", bad, 1),
                              ("the repaired find -regex form", good, 0),
                              ("a /proc pid scan", proc, 0),
                              ("a rm -rf trim", 'rm -rf "$c"/[0-9]*\n', 1),
                              ("0.[0-9]* -- cannot match 0.orig",
                               'rm -rf processor*/0.[0-9]*\n', 0),
                              ("[1-9]* -- cannot match 0.orig",
                               'rm -rf "$c"/[1-9]*\n', 0)):
        got = len(scan_text("x.sh", text))
        good_ = (got == want)
        ok &= good_
        print("  %-34s expected %d found %d  %s"
              % (label, want, got, "OK" if good_ else "FAIL"))
    # THE REFUSAL, and it is exit 2 rather than exit 1 on purpose: an
    # instrument that cannot find a defect it is KNOWN to contain has not
    # failed a test, it is UNFIT TO REPORT.  A clean sweep from it would be a
    # planted zero with no control.
    if len(scan_text("x.sh", KNOWN_HIT)) != 1:
        print("REFUSE: this checker CANNOT FIND the known hit at "
              + KNOWN_HIT_SOURCE + ".  A checker not shown able to see a "
              "non-zero cannot have its zero believed (standing rule 3). "
              "Refusing rather than reporting a clean sweep it has not earned.")
        return 2
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def one_iteration_arm(case_dir, solver, foam_bashrc, keep=False):
    """ARM 2 -- run the REAL solver for ONE iteration in a SCRATCH root.

    This is the only arm that consumes `0/`.  A mesh check cannot substitute:
    `blockMesh` and `checkMesh` never open a field file, so a bad boundary
    condition, a missing library or a wrong solver name survives them intact
    and is discovered only when the campaign fires.

    Copies first and never touches the case it inspects.
    """
    import shutil, subprocess, tempfile
    tmp = tempfile.mkdtemp(prefix="arm2_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            return False, "scratch copy resolved inside the case tree"
        # arm 0/ exactly as the launcher does
        z = os.path.join(dst, "0")
        if os.path.isdir(z):
            shutil.rmtree(z)
        orig = os.path.join(dst, "0.orig")
        if not os.path.isdir(orig):
            return False, "no 0.orig to arm from"
        shutil.copytree(orig, z)
        cd = os.path.join(dst, "system", "controlDict")
        txt = open(cd).read()
        txt = re.sub(r"^\s*endTime\s+[0-9.eE+-]+\s*;", "endTime 1;", txt, flags=re.M)
        txt = re.sub(r"^\s*writeInterval\s+[0-9.eE+-]+\s*;", "writeInterval 1;", txt, flags=re.M)
        open(cd, "w").write(txt)

        log = os.path.join(dst, "log.arm2")
        cmd = ("source %s > /dev/null 2>&1; %s -case %s > %s 2>&1"
               % (foam_bashrc, solver, dst, log))
        r = subprocess.run(["bash", "-lc", cmd])
        body = open(log, errors="replace").read() if os.path.isfile(log) else ""
        reached = bool(re.search(r"^Time = 1\s*$", body, re.M))
        if r.returncode != 0 or not reached:
            fatal = ""
            m = re.search(r"--> FOAM FATAL[\s\S]{0,400}", body)
            if m:
                fatal = " | " + " ".join(m.group(0).split())[:300]
            return False, ("solver rc=%d, reached Time=1: %s%s"
                           % (r.returncode, reached, fatal))
        return True, "solver rc=0 and reached Time = 1"
    finally:
        if not keep:
            import shutil as _s
            _s.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--one-iteration", metavar="CASE_DIR",
                    help="ARM 2: run the real solver for one iteration in scratch")
    ap.add_argument("--solver", default="buoyantBoussinesqSimpleFoam")
    ap.add_argument("--foam-bashrc",
                    default="/usr/lib/openfoam/openfoam2606/etc/bashrc")
    ap.add_argument("--root", default=".")
    ap.add_argument("--worktree", action="store_true",
                    help="scan the given paths on disk instead of HEAD")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    if a.one_iteration:
        ok, why = one_iteration_arm(a.one_iteration, a.solver, a.foam_bashrc)
        print("ARM 2 one-iteration: %s -- %s" % ("PASS" if ok else "FAIL", why))
        if not ok:
            return 1

    if a.worktree:
        items = [(p, open(p).read()) for p in a.paths if os.path.isfile(p)]
    else:
        items = files_at_head(a.root, a.paths)
    if not items:
        print("REFUSE: nothing to scan")
        return 2

    n = 0
    for path, text in items:
        for line_no, line, seg in scan_text(path, text):
            n += 1
            print("TIME-DIR-GLOB %s:%d   pattern %r matches BOTH a time dir and 0.orig"
                  % (path, line_no, seg))
            print("    %s" % line.strip()[:120])
    print("scanned %d shell file(s): %d suspect time-directory glob(s)"
          % (len(items), n))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
