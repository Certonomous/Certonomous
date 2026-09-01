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
    TAIL.compile_and_require_tail(SHEET)


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(HERE))))


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
