#!/usr/bin/env python3
"""Compile the Act C GATE sheet, and REFUSE if its last line never reached the
page.

WHY THIS EXISTS RATHER THAN A BARE `pdflatex`.  A one-page LaTeX sheet whose
content just exceeds the page SILENTLY DROPS its final line: `pdflatex` returns
0, reports the page count you expect, and warns about nothing.  Page count is
not evidence of completeness.

THE ASYMMETRY THAT MAKES IT DANGEROUS HERE.  On this sheet the honesty
statement sits LAST -- *"the run completes, the gate refuses it, and no thermal
result exists"*.  The failure mode therefore deletes exactly the sentence that
makes the sheet honest, while leaving every number above it intact.  A sheet
that lost that line would read as a clean result screen.

So this compiles through `check_sheet_tail_rendered.compile_and_require_tail`,
which reads the compiled text layer back off the page and refuses unless the
last substantive source line is really on it.  The guard is the committed one,
imported rather than reimplemented.

Usage: python3 build_actC_gate_sheet.py
Exit:  0 compiled and the tail is on the page.  2 REFUSAL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SHEET = os.path.join(HERE, "ACT_C_GATE_sheet.tex")
FIGDIR = os.path.join(HERE, "figures_actC_gate")
FIGURES = ("actC_gate_checks.pdf", "actC_gate_over_run.pdf",
           "actC_gate_sequence.pdf")


def main():
    if not os.path.exists(SHEET):
        sys.stderr.write("REFUSE: %s is missing.\n" % SHEET)
        return 2
    missing = [f for f in FIGURES if not os.path.exists(os.path.join(FIGDIR, f))]
    if missing:
        sys.stderr.write(
            "REFUSE: figure(s) %s are not built. Run "
            "figures_actC_gate/make_actC_gate_screens.py first; a sheet "
            "compiled against a missing figure renders a grey box where a "
            "result belongs and still reports one page.\n" % missing)
        return 2

    sys.path.insert(0, os.path.join(REPO, "scripts"))
    try:
        import check_sheet_tail_rendered as TAIL
    except Exception as exc:                                    # noqa: BLE001
        sys.stderr.write("REFUSE: scripts/check_sheet_tail_rendered.py is not "
                         "importable (%s). The tail guard is not optional on "
                         "this sheet: its last line is the honesty "
                         "statement.\n" % exc)
        return 2
    if not hasattr(TAIL, "compile_and_require_tail"):
        sys.stderr.write("REFUSE: the committed tail guard does not expose "
                         "compile_and_require_tail; this script will not "
                         "reimplement it.\n")
        return 2
    TAIL.compile_and_require_tail(SHEET)
    print("compiled, and the sheet's last line is verified present on the "
          "page: %s" % os.path.basename(SHEET).replace(".tex", ".pdf"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
