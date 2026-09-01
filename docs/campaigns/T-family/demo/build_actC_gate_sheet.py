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
import time
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
    # ⛔ THE STALE-PDF GUARD, AND IT WAS EARNED THE HARD WAY (2026-09-01).
    #
    # `check_sheet_tail_rendered.compile_tex` returns the PDF path "if it
    # exists", not if this compile produced it.  So when `pdflatex` FAILS
    # under `-halt-on-error`, the PREVIOUS pdf is still sitting on disk, the
    # tail guard reads THAT file, finds the tail on it, and the build reports
    # success.  Measured here: a caption edit broke the source, pdflatex wrote
    # no output at all, and this script printed "compiled, and the sheet's
    # last line is verified present" over a PDF ninety minutes old.
    #
    # That is the planted-zero failure in build form -- a pass from a check
    # that never saw a new artifact -- and on a filmed sheet it means shooting
    # the previous version of a screen while believing the edit landed.
    #
    # Two clauses, because either alone can be fooled: the old PDF is REMOVED
    # before the compile, so a failed run leaves nothing to read; and the
    # mtime is asserted to have advanced past the moment we started, so a
    # rebuild that somehow restored an old file is caught too.
    pdf = SHEET[:-4] + ".pdf"
    started = time.time()
    if os.path.exists(pdf):
        os.remove(pdf)
    TAIL.compile_and_require_tail(SHEET)
    if not os.path.exists(pdf):
        sys.stderr.write("REFUSE: no sheet was produced by this compile.\n")
        return 2
    age = os.path.getmtime(pdf)
    if age < started - 1.0:
        sys.stderr.write(
            "REFUSE: the sheet on disk is OLDER than this compile (%.0f s "
            "before it started). A previous build is being read as this "
            "one's output, which is how the version on camera stops being "
            "the version that was edited.\n" % (started - age))
        return 2
    print("compiled, and the sheet's last line is verified present on the "
          "page: %s" % os.path.basename(pdf))
    print("stale-PDF guard: the sheet was removed before the compile and its "
          "timestamp is after the compile began")
    return 0


if __name__ == "__main__":
    sys.exit(main())
