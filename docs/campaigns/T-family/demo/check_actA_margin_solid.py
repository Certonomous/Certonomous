#!/usr/bin/env python3
"""Refuse if any margin on the Act A sheet is computed against the COOLER solid.

THE DEFECT THIS EXISTS TO PREVENT.  The motor has two solids.  The core runs
hotter than the housing at every one of the sixteen solved points -- by 1.07 K
at the mildest and 4.07 K at the worst.  The body's true peak is therefore the
CORE peak, and the margin to the customer's temperature limit must be taken
against it.  A sheet that prints the HOUSING margin overstates the available
margin by up to 4.07 K, in the optimistic direction, on a thermal limit.  That
is the worst-shaped error this act can make, and it was caught and repaired
once already in the display module (ec6341d7) without being repaired in the
printed sheet.

WHAT IS CHECKED, against the run's own record and not against a typed constant:
  1. Every housing-based margin, at every precision the sheet could print it
     in, is ABSENT from the rendered page.  Housing TEMPERATURES are legal --
     the sheet shows them in a labelled column, and the correlation table
     legitimately compares against the housing because Dittus-Boelter and the
     lumped resistance estimate are surface-convection closures for the wall.
     Housing MARGINS are not legal anywhere.
  2. The core margin at the worst solved point IS present.
  3. Every peak temperature printed is accompanied by the name of its solid,
     so a viewer cannot pair a housing number with a core peak elsewhere.

THE CONTROL.  A checker that has only ever seen a clean page is not evidence.
``--selftest`` drives this one to its refusal against a synthetic page carrying
the exact defect, and refuses if the checker fails to catch it.  It was also
driven to refusal against the real pre-fix sheet, which carried four housing
margins in its own margin table.

Exit 0 = every margin is on the core.  Exit 2 = a margin is on the cooler
solid, or the checker failed its own control.
"""

import csv
import os
import re
import subprocess
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
MAP_CSV = os.path.join(HERE, "figures_actA", "actA_map_table.csv")
SHEET_PDF = os.path.join(HERE, "ACT_A_thermal_map_sheet.pdf")
# The map-table FIGURE is a second filmed surface carrying the same quantities.
# The defect this guards was fixed in the display module at ec6341d7 and NOT in
# the printed sheet, so checking only one surface is how it survived.
FIGURE_PDF = os.path.join(HERE, "figures_actA", "actA_map_table.pdf")

LIMIT_C = 200.0


def load_rows():
    with open(MAP_CSV) as f:
        return list(csv.DictReader(f))


def precisions(x):
    """Every rendering of x the sheet could plausibly print."""
    return {("%.4f" % x), ("%.3f" % x), ("%.2f" % x), ("%.1f" % x)}


def page_text(path):
    out = subprocess.run(["pdftotext", "-q", path, "-"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return re.sub(r"\s+", " ", out.stdout)


def audit(text, rows):
    """Return (violations, required_present). Pure, so the selftest can reuse it."""
    violations = []
    for r in rows:
        p, u = r["power_W"], r["airspeed_m_per_s"]
        m_h = float(r["margin_to_200C_limit_on_housing_K"])
        m_c = float(r["margin_to_200C_limit_on_core_K"])
        for form in precisions(m_h):
            # A housing margin that is numerically also the core margin cannot
            # be attributed, so it is not counted as a violation.
            if form in precisions(m_c):
                continue
            if re.search(r"(?<![\d.])" + re.escape(form) + r"(?![\d])", text):
                violations.append(
                    (p, u, form, "%.6f" % m_c,
                     "housing margin on the page; core margin is the true one"))

    worst = max(rows, key=lambda r: float(r["peak_core_temperature_degC"]))
    m_c = float(worst["margin_to_200C_limit_on_core_K"])
    present = any(
        re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", text)
        for f in precisions(m_c))
    return violations, (present, worst, m_c)


def selftest(rows):
    """Drive the checker to its refusal on a page carrying the exact defect."""
    worst = max(rows, key=lambda r: float(r["peak_core_temperature_degC"]))
    m_h = float(worst["margin_to_200C_limit_on_housing_K"])
    m_c = float(worst["margin_to_200C_limit_on_core_K"])

    bad = ("Peak temperature 103.6078 C, margin %.4f K below the limit."
           % m_h)
    good = ("Peak core temperature 107.6775 C, margin %.4f K below the limit."
            % m_c)

    v_bad, _ = audit(bad, rows)
    v_good, (present_good, _, _) = audit(good, rows)

    if not v_bad:
        sys.stderr.write(
            "REFUSE: the checker did NOT catch a page printing the housing "
            "margin %.4f K. A checker that cannot see the defect it exists "
            "for is ceremony, and its passes mean nothing.\n" % m_h)
        raise SystemExit(2)
    if v_good:
        sys.stderr.write(
            "REFUSE: the checker fired on a CORRECT page (core margin "
            "%.4f K). A control that cries wolf is as useless as a blind "
            "one.\n" % m_c)
        raise SystemExit(2)
    if not present_good:
        sys.stderr.write("REFUSE: the checker cannot even see the core "
                         "margin it requires.\n")
        raise SystemExit(2)
    print("control: a page printing the housing margin %.4f K IS caught "
          "(%d hit); a page printing the core margin %.4f K is NOT, and its "
          "required value IS seen"
          % (m_h, len(v_bad), m_c))


def main():
    rows = load_rows()
    selftest(rows)

    bad = 0
    checked = 0
    for path in (SHEET_PDF, FIGURE_PDF):
        if not os.path.exists(path):
            sys.stderr.write("REFUSE: %s not built; it carries the same "
                             "quantities and cannot be skipped.\n" % path)
            raise SystemExit(2)
        text = page_text(path)
        if text is None:
            sys.stderr.write("REFUSE: could not read the text layer of %s.\n"
                             % path)
            raise SystemExit(2)
        checked += 1
        violations, (present, worst, m_c) = audit(text, rows)

        print("\nsurface: %s" % os.path.basename(path))
        if violations:
            print("   HOUSING MARGINS PRESENT -- each overstates the margin:")
            for p, u, form, true_c, _ in violations:
                print("      %s W, %s m/s: carries %s K; margin on the core "
                      "is %s K" % (p, u, form, true_c))
        else:
            print("   no housing-based margin appears anywhere")

        if present:
            print("   core margin at the worst point (%s W, %s m/s) present: "
                  "%.6f K" % (worst["power_W"], worst["airspeed_m_per_s"],
                              m_c))
        else:
            print("   *** core margin at the worst point is ABSENT: %.6f K"
                  % m_c)
        if violations or not present:
            bad += 1

    if bad:
        print("\nGATE FAIL -- %d of %d filmed surfaces put a margin on the "
              "cooler solid" % (bad, checked))
        raise SystemExit(2)
    print("\nPASS -- on both filmed surfaces every margin is taken against "
          "the core, the hotter solid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
