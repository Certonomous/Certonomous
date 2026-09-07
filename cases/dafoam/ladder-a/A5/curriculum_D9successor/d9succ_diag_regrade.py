#!/usr/bin/env python3
"""
D9successor DIAGNOSTIC tag-corrected regrade.  ***DIAGNOSTIC ONLY — NOT THE OFFICIAL
VERDICT.***  Authorized by the dafoam-supervisor's crash-triage ruling 2026-09-07.

WHY THIS EXISTS.  The frozen graded run (PERMISSION 60dddc2c, freeze 433a24a8) produced
the frozen-path verdict NOT A RESULT, but that verdict is CONFOUNDED by an L-504
launcher-vs-grader tag-derivation mismatch, NOT by physics:
  * the FROZEN launcher d9succ_stage_and_run.sh writes the FD-stage dirs with
    `sed 's/./p/;s/-/m/;s/+/p/'` applied to the literal step strings -> fd_5p0em5,
    fd_1p0em4, fd_2p0em4, fd_1p0em3;
  * the FROZEN grader d9succ_grade.py's fmt_tag uses "%.1e" (which ZERO-PADS the
    exponent) -> it looks for fd_5p0em05, fd_1p0em04, fd_2p0em04, fd_1p0em03.
So the frozen grader finds 0 of 3 FD dirs though all three USABLE records EXIST and are
VALID (status COMPLETE, J_an/J_fd len 27, endpoint shape).

WHAT THIS DOES.  It imports the FROZEN grader by path and MONKEYPATCHES only its
`fmt_tag` to reproduce the launcher's sed derivation, then calls the frozen `grade()`
VERBATIM.  The frozen grader file on disk is NEVER edited (rule 6); every gate, band,
plant and refusal path is the frozen logic.  The ONLY change is the FD-stage directory
NAME the reader looks for.  This reveals the TRUE G-FDPERF / G-GRAD the tag bug hid.
It is a DIAGNOSTIC; the official verdict remains the frozen grader's NOT A RESULT until
the supervisor rules on the grading-path reconciliation.
"""
import argparse
import importlib.util
import os
import re
import sys

FROZEN_GRADER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d9succ_grade.py")


def launcher_tag(h):
    """Reproduce the FROZEN launcher's FD-dir tag: the step string with the exponent
    NOT zero-padded, then sed s/./p/; s/-/m/; s/+/p/.  Matches fd_5p0em5 etc."""
    s = ("%.1e" % h)                      # e.g. "5.0e-05"
    s = re.sub(r'e([+-])0*(\d)', r'e\1\2', s)   # de-zero-pad exponent -> "5.0e-5"
    return s.replace('.', 'p').replace('-', 'm').replace('+', 'p')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--cpuset", type=int, default=15)
    ap.add_argument("--meshlog", default="")
    a = ap.parse_args()

    spec = importlib.util.spec_from_file_location("d9succ_grade_frozen", FROZEN_GRADER)
    dg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dg)

    # sanity: prove the frozen fmt_tag and the launcher tag actually DISAGREE (the bug),
    # and that our correction matches the launcher, before we trust the regrade.
    print("=== D9successor DIAGNOSTIC tag-corrected regrade (NOT THE OFFICIAL VERDICT) ===")
    for h in dg.FD_STEPS:
        print("  step %g: frozen fmt_tag -> fd_%s ; launcher/corrected -> fd_%s"
              % (h, dg.fmt_tag(h), launcher_tag(h)))

    dg.fmt_tag = launcher_tag          # monkeypatch ONLY the dir-name derivation
    meshlog = a.meshlog or None
    try:
        worst, lines, facts = dg.grade(a.root, a.cpuset, meshlog=meshlog)
    except dg.Refuse as e:
        print("DIAGNOSTIC REGRADE REFUSES (exit 2): %s" % e)
        sys.exit(2)
    print("--- gate lines (frozen logic, corrected FD-dir names) ---")
    for ln in lines:
        print(ln)
    print("DIAGNOSTIC VERDICT (NOT OFFICIAL): %s" % dg.NAME[worst])
    if facts.get("rows"):
        print("\nPER-COMPONENT ENDPOINT TABLE (adjoint vs FD at each component's OWN plateau step):")
        print("  %-5s %-11s %-16s %-16s %-12s %s" %
              ("idx", "h*", "FD(h*)", "adjoint", "rel", "usable-by-step"))
        for i, hh, fd, an, rel, usable in facts["rows"]:
            if hh is None:
                print("  %-5d %-11s %-16s %-16.9e %-12s %s   FD-UNGRADEABLE%s"
                      % (i, "-", "-", an, "-", "".join("U" if u else "." for u in usable),
                         " (NAMED IN ADVANCE)" if i in dg.IDX16_CLASS else ""))
            else:
                print("  %-5d %-11.1e %-16.9e %-16.9e %-12.6e %s"
                      % (i, hh, fd, an, rel, "".join("U" if u else "." for u in usable)))
    print("\n(DIAGNOSTIC ONLY. Official verdict remains the frozen grader's, pending the "
          "supervisor's grading-path reconciliation ruling.)")
    sys.exit(0 if worst == 0 else 1)


if __name__ == "__main__":
    main()
