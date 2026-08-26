#!/usr/bin/env python3
"""Flag SHELL GLOBS used as OpenFOAM time-directory matchers.

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


# a glob whose LAST path segment is what we test
SEG = re.compile(r"""[\w"'$}{./\\-]*/(?P<seg>\[[0-9!^-]+\][^\s"';)|&]*)""")


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
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if REGEXY.search(line):
            continue
        for m in SEG.finditer(line):
            seg = m.group("seg")
            around = line[max(0, m.start() - 40):m.end() + 10]
            if PROC.search(around):
                continue
            bad, times = glob_hits_0orig(seg)
            if bad and times:
                hits.append((i, line.rstrip(), seg))
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
    ok = True
    for label, text, want in (("the T4 defect verbatim", bad, 1),
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
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=".")
    ap.add_argument("--worktree", action="store_true",
                    help="scan the given paths on disk instead of HEAD")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

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
