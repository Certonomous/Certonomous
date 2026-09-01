#!/usr/bin/env python3
"""Regenerate every measured value on the Act A sheet from the run's own record.

WHY THIS EXISTS.  Sanaa's 2026-09-01 03:10Z item (4) fixes the sheet at 0.1
degC significant figures UNTIL the grid triple lands, and the displayed
precision moves again once it does.  Hand-editing thirty numbers each time that
dial turns is how a transcription error gets in, and it is how the sheet and
the figures drift apart.  So the precision is ONE named parameter here, and the
sheet's numeric blocks are rewritten from
``figures_actA/actA_map_table.csv`` -- the same record the figures read.

TURN THE DIAL HERE:
    DECIMALS_DEGC = 1     ->  107.7   (current: 03:10Z standing instruction)
    DECIMALS_DEGC = 0     ->  108     (expected if T23G grades G-GCI-DISPLAY)
    DECIMALS_DEGC = 4     ->  107.6775 (pre-03:10Z)
then run this script and recompile.  Nothing else needs touching.

WHICH SOLID.  The core runs hotter than the housing at all sixteen points, so
the core peak is the body's peak and every MARGIN is taken against it.  The
housing appears only in labelled columns: Table 2's own housing column, and
Table 3, where the comparison is legitimately against the wall because
Dittus-Boelter and the lumped resistance estimate are surface-convection
closures.  ``check_actA_margin_solid.py`` enforces that split.

ROUNDING IS PER CELL, FROM THE RECORD.  Each cell rounds its own measured
value.  At 0.1 degC that means a difference cell can differ from the difference
of the two rounded peaks printed beside it -- 155 W / 10 m/s prints 2.1 while
62.0 minus 60.0 reads 2.0.  Reconciling the column would mean printing a number
that is not the measured one, so the measured one is printed and the
discrepancy is disclosed rather than smoothed.  ``report()`` lists every such
row.
"""

import csv
import os
import re
import subprocess
import sys


# ---------------------------------------------------------------- the dial --
DECIMALS_DEGC = 1        # significant figures after the point, degC and K
DECIMALS_RATIO = 3       # the overprediction ratios are dimensionless

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "ACT_A_thermal_map_sheet.tex")
MAP_CSV = os.path.join(HERE, "figures_actA", "actA_map_table.csv")

POWERS = [80, 155, 230, 305]
SPEEDS = [10, 20, 30, 40]
INLET_C = 14.85          # 288 K, the sheet's stated cooling-air temperature
LIMIT_C = 200.0

# The closed-form hand estimates the sheet compares against, in degC.  These
# are not solver output; they are the customer's own sizing method, kept here
# as the constants they are.  duct correlation, flat plate.
HAND = {10: (329.1, 195.1), 20: (197.3, 120.3),
        30: (148.0, 92.4), 40: (121.6, 77.4)}

# Figure 1 geometry: the 200 degC limit line sits at 53.33 mm, and the four
# airspeeds sit at these x positions in mm.
Y_PER_DEGC = 53.33 / LIMIT_C
X_OF = {10: 0.0, 20: 28.0, 30: 56.0, 40: 84.0}


def T(x):
    return "%.*f" % (DECIMALS_DEGC, x)


def load():
    with open(MAP_CSV) as f:
        rows = list(csv.DictReader(f))
    d = {}
    for r in rows:
        d[(int(r["power_W"]), int(r["airspeed_m_per_s"]))] = r
    if len(d) != 16:
        sys.stderr.write("REFUSE: expected 16 solved points, found %d\n"
                         % len(d))
        raise SystemExit(2)
    return d


# ------------------------------------------------------------ the blocks ----
def block_t1(d):
    out = []
    for p in POWERS:
        cells = " & ".join(
            T(float(d[(p, u)]["peak_core_temperature_degC"])) for u in SPEEDS)
        out.append("\\textbf{%d} & %s & not quantified (single mesh level) \\\\"
                   % (p, cells))
    return "\n".join(out) + "\n"


def block_t2(d):
    out = []
    for p in POWERS:
        r = d[(p, 10)]
        vals = [T(float(r["peak_core_temperature_degC"])),
                T(float(r["peak_housing_temperature_degC"])),
                T(float(r["core_above_housing_K"])),
                T(float(r["margin_to_200C_limit_on_core_K"]))]
        note = "worst solved point" if p == 305 else "clears the limit"
        if p == 305:
            cells = " & ".join("\\textbf{%s}" % v for v in [str(p)] + vals)
        else:
            cells = " & ".join([str(p)] + vals)
        out.append("%s & %s \\\\" % (cells, note))
    return "\n".join(out) + "\n"


def block_t3(d):
    """Solved HOUSING, named as such -- these closures are for the wall."""
    out = []
    for u in SPEEDS:
        duct, plate = HAND[u]
        hous = float(d[(305, u)]["peak_housing_temperature_degC"])
        rise = hous - INLET_C
        r_duct = (duct - INLET_C) / rise
        r_plate = (plate - INLET_C) / rise
        emph = (u in (10, 40))
        f = (lambda s: "\\textbf{%s}" % s) if emph else (lambda s: s)
        out.append("%d & %s & %s & %s & %s & %s \\\\" % (
            u, "%.1f" % duct, "%.1f" % plate, T(hous),
            f("%.*f" % (DECIMALS_RATIO, r_duct)),
            f("%.*f" % (DECIMALS_RATIO, r_plate))))
    return "\n".join(out) + "\n"


def block_coolest(d):
    best = min(d.values(),
               key=lambda r: float(r["peak_core_temperature_degC"]))
    return (r"""{\footnotesize Coolest core peak %s$\,^{\circ}\mathrm{C}$, at
$%s\,\mathrm{W}$ and $%s\,\mathrm{m\,s^{-1}}$. Margins carry no error bar.}
"""
            % (T(float(best["peak_core_temperature_degC"])),
               best["power_W"], best["airspeed_m_per_s"]))


def block_curves(d):
    """Figure 1 plots the CORE, so its coordinates come from the core column."""
    out = []
    for p in POWERS:
        y = {u: float(d[(p, u)]["peak_core_temperature_degC"]) * Y_PER_DEGC
             for u in SPEEDS}
        dot = "1.3" if p == 305 else "1.1"
        out.append("  %% %d W core -> %s"
                   % (p, " ".join("%.2f" % y[u] for u in SPEEDS)))
        if p == 305:
            out.append("  \\linethickness{0.9pt}")
        for a, b in [(10, 20), (20, 30), (30, 40)]:
            xa, xb, ya, yb = X_OF[a], X_OF[b], y[a], y[b]
            out.append("  \\qbezier(%.2f,%.2f)(%.0f,%.2f)(%.2f,%.2f)"
                       % (xa, ya, (xa + xb) / 2, (ya + yb) / 2, xb, yb))
        for pair in (SPEEDS[:2], SPEEDS[2:]):
            out.append("  " + "".join(
                "\\put(%.2f,%.2f){\\circle*{%s}}" % (X_OF[u], y[u], dot)
                for u in pair))
    return "\n".join(out) + "\n"


BLOCKS = {"t1": block_t1, "t2": block_t2, "t3": block_t3,
          "coolest": block_coolest, "curves": block_curves}


def report(d):
    """Disclose every cell whose displayed subtraction will not check out."""
    bad = []
    for p in POWERS:
        for u in SPEEDS:
            r = d[(p, u)]
            c = round(float(r["peak_core_temperature_degC"]), DECIMALS_DEGC)
            h = round(float(r["peak_housing_temperature_degC"]), DECIMALS_DEGC)
            shown = round(float(r["core_above_housing_K"]), DECIMALS_DEGC)
            if abs(round(c - h, DECIMALS_DEGC) - shown) > 1e-9:
                bad.append((p, u, c, h, round(c - h, DECIMALS_DEGC), shown,
                            u == 10))
    return bad


def compile_and_check_tail():
    """Compile the sheet, then REFUSE if its last line did not reach the page.

    This is wired into the regeneration path on purpose.  A one-page sheet
    whose content just exceeds the page silently drops its final line while
    pdflatex still returns rc=0 and reports the page count you expected, and
    on these sheets the honesty statements sit LAST -- so the failure
    preferentially deletes the caveats and leaves the headline numbers intact.
    Measured on this sheet: ONE added sentence is enough.

    A check somebody has to remember to run is a check that gets skipped on
    the night it matters, so regenerating runs it and refuses rather than
    leaving a sheet with a missing tail sitting there looking finished.
    """
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    try:
        import check_sheet_tail_rendered as TAIL
    except ImportError:
        sys.stderr.write("REFUSE: scripts/check_sheet_tail_rendered.py is "
                         "missing; the regeneration will not certify a sheet "
                         "it cannot check.\n")
        raise SystemExit(2)
    _assert_sheet_is_from_current_source_before(SHEET)
    TAIL.compile_and_require_tail(SHEET)
    _assert_sheet_is_from_current_source_after(SHEET)
    _assert_load_bearing_lines_rendered(SHEET)


#: Set by the "before" check and read by the "after" check, in one process.
_SHEET_MTIME_BEFORE = {}


def _assert_sheet_is_from_current_source_before(tex_path):
    """Record the pdf's mtime before the build, so staleness is detectable."""
    pdf = tex_path[:-4] + ".pdf"
    _SHEET_MTIME_BEFORE[pdf] = (os.path.getmtime(pdf)
                                if os.path.exists(pdf) else None)


def _assert_sheet_is_from_current_source_after(tex_path):
    """REFUSE a sheet whose pdf did not actually move in this build.

    ⛔ THE DEFECT THIS DEFENDS AGAINST. ``compile_tex`` in the shared tail guard
    tested EXISTENCE ONLY -- it captured ``returncode`` and never read it. When
    ``pdflatex`` failed under ``-halt-on-error`` it wrote nothing, THE PREVIOUS
    PDF WAS STILL ON DISK, and it was handed back as though this compile had
    produced it: the tail guard read the stale file, found the tail present, and
    the build PRINTED SUCCESS. Measured by the Act C lane on their own sheet
    against a PDF EIGHTY-THREE MINUTES OLD, caught only because a token count
    did not move.

    THIS IS A POST-CONDITION, DELIBERATELY, NOT A REPLACEMENT FOR THE COMPILE
    STEP. The shared body is being hardened by the lane that found the defect,
    and shadowing their ``compile_tex`` with a local copy would hide whatever
    they improve. Asserting the OUTCOME instead -- that a newer pdf exists --
    stays correct whether the shared fix has landed or not, and costs two
    ``stat`` calls.

    It is the same rule as the planted zero, the glyph whitelist and the
    ``.rc.*`` glob: a green result is only evidence if the instrument could
    have seen the failure.
    """
    pdf = tex_path[:-4] + ".pdf"
    if not os.path.exists(pdf):
        sys.stderr.write("REFUSE: no sheet pdf exists after the build.\n")
        raise SystemExit(2)
    before = _SHEET_MTIME_BEFORE.get(pdf)
    now = os.path.getmtime(pdf)
    if before is not None and now <= before:
        sys.stderr.write(
            "REFUSE: %s did not change in this build -- its timestamp has not "
            "moved, so the tail guard just certified an artefact from an "
            "EARLIER run. The compile failed and left the previous pdf in "
            "place.\n" % os.path.basename(pdf))
        raise SystemExit(2)
    if now < os.path.getmtime(tex_path):
        sys.stderr.write(
            "REFUSE: %s is older than its source; this build did not produce "
            "it.\n" % os.path.basename(pdf))
        raise SystemExit(2)
    print("sheet pdf confirmed newer than its source (%s)"
          % os.path.basename(pdf))


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(HERE))))


#: Sentences that must appear on the rendered page, VERBATIM, whatever else is
#: edited. Amendment 2026-09-01: added after a rebuild showed that asserting the
#: TAIL protects everything above it against TRUNCATION ONLY.
#:
#: WHY THE TAIL ASSERTION IS NOT ENOUGH ON ITS OWN. The shared guard requires the
#: source's last substantive line as a contiguous phrase on the page, and against
#: silent bottom truncation that is SUFFICIENT for everything above it: an
#: overfull page eats upward from the end, so if the last line arrived, so did
#: every line before it. That reasoning is sound and this assertion does not
#: replace it.
#:
#: But truncation is not the only way a line dies. AN EDIT CAN DELETE A
#: MID-DOCUMENT SENTENCE WHILE THE TAIL SURVIVES INTACT, and against that the
#: tail assertion is silent -- it infers the middle from a geometry that only
#: holds for truncation. This sheet produced two live instances of the editing
#: shape in one evening: a caption that became FALSE when its table moved to the
#: sheet, and a cost line that satisfied one requirement while being silent on
#: two others. Neither was truncation; both were edits.
#:
#: The sentence below is the most load-bearing on the sheet. It is the one a
#: viewer most needs and would least notice missing, and it is the line that
#: keeps the empty uncertainty column honest rather than looking like an
#: oversight. It is cheap to assert and it closes the exposure ordering cannot.
LOAD_BEARING_LINES = (
    "The uncertainty column of Table 1 is empty on purpose: one mesh level "
    "supports no error bar, and none is invented.",
)


def _rendered_text(pdf_path):
    """The page as text, whitespace-normalised so a line wrapped by LaTeX still
    matches the sentence it was written as."""
    import subprocess

    out = subprocess.run(["pdftotext", "-q", pdf_path, "-"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write("REFUSE: could not read the rendered sheet back.\n")
        raise SystemExit(2)
    return " ".join(out.stdout.split())


def _assert_load_bearing_lines_rendered(tex_path):
    """REFUSE unless every load-bearing sentence is on the rendered page.

    Asserted as a CONTIGUOUS PHRASE, not as a set of words. The shared guard's
    own docstring records why: when Act C's tail was dropped, ZERO of its words
    were absent from the page, so a bag-of-words test passed over a deleted
    limitation statement.
    """
    pdf = tex_path[:-4] + ".pdf"
    page = _rendered_text(pdf)
    missing = [line for line in LOAD_BEARING_LINES
               if " ".join(line.split()) not in page]
    if missing:
        sys.stderr.write(
            "REFUSE: %d load-bearing sentence(s) are NOT on the rendered "
            "sheet. The tail may be intact and the sheet still be dishonest -- "
            "an edit can delete a middle line while the last one survives.\n"
            % len(missing))
        for line in missing:
            sys.stderr.write("   missing: %s\n" % line)
        raise SystemExit(2)
    print("load-bearing lines verified present: %d" % len(LOAD_BEARING_LINES))


def selftest_load_bearing():
    """Drive the assertion BOTH WAYS on a scratch copy of the rendered sheet.

    A second assertion that has never been shown to fire is decoration.

    ⚠ THE REUSABLE TRAP, FOR WHOEVER WRITES THE NEXT ONE OF THESE. A phrase
    assertion needs TWO DIFFERENT STRINGS, and conflating them is what bit the
    first draft of this function:

      * THE ASSERTED PHRASE is matched against the RENDERED page, and is written
        as the sentence reads. LaTeX wraps lines wherever it likes, so the match
        is done on whitespace-NORMALISED text (:func:`_rendered_text`); without
        that normalisation a sentence broken across two rendered lines would
        read as absent and the guard would refuse a perfectly good page.

      * THE NEEDLE that builds the negative arm is matched against the SOURCE,
        to delete the sentence before recompiling, and must therefore be a
        fragment that actually sits on ONE SOURCE LINE. The first draft used
        "empty on purpose", which STRADDLES A LINE WRAP in the .tex and matched
        nothing.

    The source string and the rendered string are not the same string. A needle
    chosen by reading the sentence -- the obvious thing to do -- is chosen from
    neither, and will silently match nothing in the source.

    WHAT SAVED IT was that the arm REFUSED TO BUILD rather than proving nothing:
    it could not construct its own failure case, and said so, instead of
    reporting a pass. An arm that cannot build its negative case must refuse,
    never continue -- otherwise the first draft of this guard would have shipped
    green having tested exactly nothing.
    """
    import shutil
    import tempfile

    pdf = SHEET[:-4] + ".pdf"
    if not os.path.exists(pdf):
        sys.stderr.write("REFUSE: build the sheet before selftesting.\n")
        raise SystemExit(2)

    # POSITIVE: the real page must pass.
    page = _rendered_text(pdf)
    for line in LOAD_BEARING_LINES:
        if " ".join(line.split()) not in page:
            sys.stderr.write("REFUSE: positive arm failed -- %r is not on the "
                             "real page.\n" % line)
            raise SystemExit(2)

    # NEGATIVE: a page WITHOUT the sentence must be refused. Built by deleting
    # the sentence from a scratch copy of the SOURCE and recompiling, so the
    # arm exercises a genuinely rendered page rather than a doctored string.
    work = tempfile.mkdtemp(prefix="actA_lb_")
    try:
        src = open(SHEET, encoding="utf-8").read()
        # The sentence is LINE-WRAPPED in the source, so the needle must be a
        # fragment that actually sits on one source line. "empty on purpose"
        # straddles the wrap and matched nothing; the negative arm then refused
        # to build rather than silently proving nothing, which is the arm
        # working.
        needle = "uncertainty column of Table"
        if needle not in src:
            sys.stderr.write("REFUSE: cannot build the negative arm -- the "
                             "sentence is not in the source to remove.\n")
            raise SystemExit(2)
        cut = "\n".join(l for l in src.splitlines() if needle not in l)
        scratch_tex = os.path.join(work, os.path.basename(SHEET))
        open(scratch_tex, "w", encoding="utf-8").write(cut)
        import subprocess
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode",
                            os.path.basename(scratch_tex)],
                           cwd=work, capture_output=True, text=True)
        scratch_pdf = scratch_tex[:-4] + ".pdf"
        if not os.path.exists(scratch_pdf):
            sys.stderr.write("REFUSE: the negative arm did not compile, so it "
                             "proves nothing (pdflatex rc=%d).\n" % r.returncode)
            raise SystemExit(2)
        cut_page = _rendered_text(scratch_pdf)
        still = [l for l in LOAD_BEARING_LINES
                 if " ".join(l.split()) in cut_page]
        if still:
            sys.stderr.write("REFUSE: negative arm did NOT fire -- the "
                             "sentence was removed from the source and still "
                             "reads as present. The assertion is asleep.\n")
            raise SystemExit(2)
        print("load-bearing selftest PASS: present on the real page, absent "
              "and detected on a page built without it")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    d = load()
    src = open(SHEET, encoding="utf-8").read()
    n = 0
    for tag, fn in BLOCKS.items():
        pat = re.compile(r"(%%<<ACTA %s>>\n).*?(%%<<END %s>>\n)"
                         % (tag, tag), re.S)
        if not pat.search(src):
            sys.stderr.write("REFUSE: marker %r not found in the sheet; the "
                             "generator cannot silently write nothing.\n" % tag)
            raise SystemExit(2)
        src = pat.sub(lambda m: m.group(1) + fn(d) + m.group(2), src)
        n += 1
    open(SHEET, "w", encoding="utf-8").write(src)
    print("regenerated %d blocks at %d decimal place(s)" % (n, DECIMALS_DEGC))

    bad = report(d)
    if bad:
        print("\nDISCLOSED -- rounding makes these difference cells disagree "
              "with the two rounded peaks printed beside them:")
        for p, u, c, h, sub, shown, onscreen in bad:
            print("   %3d W %2d m/s: %s - %s = %s, column prints %s%s"
                  % (p, u, c, h, sub, shown,
                     "   <-- ON SCREEN (Table 2)" if onscreen else
                     "   (not shown; Table 2 is the 10 m/s column)"))
        print("Each cell is rounded from the record. Reconciling the column "
              "would print a number that was never measured.")
    else:
        print("every difference cell agrees with its two rounded peaks")

    print()
    compile_and_check_tail()
    return 0


if __name__ == "__main__":
    sys.exit(main())
