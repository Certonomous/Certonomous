#!/usr/bin/env python3
"""Compile the Act C sheet and REFUSE if its last line did not reach the page.

WHAT THIS DOES, AND EXACTLY WHAT IT DOES NOT
--------------------------------------------
It COMPILES and CHECKS.  It does NOT generate.

**Act C's numbers are hand-written in the .tex today.**  Nothing here reads
them from a run record, and the existence of this script must not be taken as
evidence that they are record-derived -- they are not, yet.  That inference is
the kind of thing that quietly becomes a false claim without anyone ever
writing one down, which is why it is denied here in the open.

Generating Act C's values from the run record is OWED, not optional, and it
lands when the replacement run does: Act C's present source is the 960-cell
feasibility case, and when its successor grades, every number on this sheet
must be generated from that record rather than typed -- the same discipline
already enforced on Act A by ``regen_actA_sheet.py``, and the reason Act A's
26-value correction could be trusted.  **This script is the first increment of
that generator, not a throwaway**: the compile-and-check tail is the part that
is content-independent, so it is correct now and stays correct after the
numbers are replaced.

WHY IT EXISTS NOW
-----------------
A one-page LaTeX sheet whose content just exceeds the page silently DROPS its
final line, while pdflatex still returns rc=0 and reports the page count you
expected.  Act C's last line is its Lead Numericist limitation --

    "one mesh, one time step, and no numerical error bar on any module number"

-- which is the single sentence on that sheet we least want to lose, and the
one this failure mode takes first.  Measured on the sibling Act A sheet: ONE
added sentence is enough to trigger the loss.  Act C is hand-maintained, so
before this script there was no path that forced the check to run.

Exit 0 = compiled and the tail is on the page.  Exit 2 = it does not compile,
or the tail was silently dropped.
"""

import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(HERE))))
SHEET = os.path.join(HERE, "ACT_C_battery_module_sheet.tex")


def main():
    if not os.path.exists(SHEET):
        sys.stderr.write("REFUSE: %s is missing.\n" % SHEET)
        raise SystemExit(2)

    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    try:
        import check_sheet_tail_rendered as TAIL
    except ImportError:
        # A guard that degrades to silence when its instrument is absent is
        # the planted-zero failure in a new costume.
        sys.stderr.write("REFUSE: scripts/check_sheet_tail_rendered.py is "
                         "missing; this will not certify a sheet it cannot "
                         "check.\n")
        raise SystemExit(2)

    print("Act C: compiling and checking the tail. "
          "This script does NOT generate the sheet's numbers; they are "
          "hand-written and owed a generator when the replacement run lands.")
    TAIL.compile_and_require_tail(SHEET)
    return 0


if __name__ == "__main__":
    sys.exit(main())
