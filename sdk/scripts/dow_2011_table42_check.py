"""Dow (2011) Table 4.2, transcribed from the thesis and checked.

Source, READ IN FULL this session (2026-08-05):
  E. A. Dow, "Quantification of Structural Uncertainties in RANS Turbulence
  Models", SM thesis, MIT Department of Aeronautics and Astronautics,
  submitted 18 August 2011, supervised by Qiqi Wang. DSpace handle
  1721.1/68407. Held at
  docs/papers/uncertainty_quantification/dow_mit_sm2011_structural_uncertainties_rans.pdf with a text
  extraction alongside.

Zero compute: no solver, no mesh, no fit. Pure arithmetic on eight rows of a
published table. Nothing is trained on anything, so the in-sample clause of
LITERATURE_CHARTER section 7 does not arise.

WHY THIS FILE EXISTS. Table 4.2 is the single number the lab would quote from
this thesis: the fraction of the RANS-to-DNS velocity discrepancy that an
inferred eddy-viscosity field can absorb. That fraction is the whole
justification for treating model-form uncertainty as uncertainty in nu_T, and
it is the number an implementation program is priced against. Two things make
it worth checking by arithmetic rather than by transcription:

1. The DSpace copy is a scan and the OCR mangles two of the sixteen numbers.
   Geometry 8 reads "0.840" in the table and 0.0840 in the prose of section
   4.5.2; geometry 4 reads "0.0.117".
2. The thesis states the last column's definition in words that do not match
   the printed values. Section 4.5.2: "The last column of table 4.2 indicates
   the percentage change in the norm of the velocity discrepancy, i.e.
   1 - J(vT)/J(v_k-w)". J is defined in section 2.3.1 as a SQUARED L2 norm,
   so 1 - J*/J_kw is the change in the squared norm, and that is not what the
   table prints. What the table prints is 1 - sqrt(J*/J_kw), the change in the
   norm itself, which is what the sentence's own words say and what its
   formula does not.

The distinction is not cosmetic for us. On geometry 8 the two readings are
89.3 percent and 98.9 percent of the discrepancy attributed to nu_T. A program
that quotes the wrong one over-claims or under-claims by an order of magnitude
in the residual it leaves for everything the eddy-viscosity hypothesis cannot
represent.

Run: python3 sdk/scripts/dow_2011_table42_check.py
Exit 0 iff every check passes.
"""
from __future__ import annotations

import math
import sys

# Table 4.2 as printed, p. 58 of the thesis (page 58 of the scan's own
# numbering; line 2629 onwards of the text extraction). Columns:
#   geometry, J(nu_T^{k-omega}), J(nu_T^*), printed percentage.
# J* for geometries 4 and 8 are the OCR-damaged cells and are carried here as
# None so that this script derives them rather than guessing them.
TABLE_4_2 = (
    ("1", 23.5, 0.148, 92.1),
    ("2", 0.515, 0.0449, 70.5),
    ("3", 16.2, 0.254, 87.5),
    ("4", 6.19, None, 86.3),      # OCR: "0.0.117"
    ("5", 7.15, 0.0646, 90.5),
    ("6", 0.165, 0.0127, 72.3),
    ("7", 15.9, 0.308, 86.1),
    ("8", 7.35, None, 89.3),      # OCR: "0.840"; prose section 4.5.2 says 0.0840
)

# The prose value for geometry 8, section 4.5.2: "For the geometry shown in
# figures 4-7 and 4-8, the initial objective function value was J(v_k-w) =
# 7.35. For the optimized turbulent viscosity field, the objective function
# value was J(vT) = 0.0840."
GEOM_8_PROSE_J_STAR = 0.0840

# The percentages are printed to one decimal place, so agreement is asserted
# to that increment and no further. LESSONS L-28: no claim below a printed
# increment.
TOL_PERCENT = 0.05


def pct_norm(j_star: float, j_kw: float) -> float:
    """1 - sqrt(J*/J_kw): the change in the velocity discrepancy NORM."""
    return 100.0 * (1.0 - math.sqrt(j_star / j_kw))


def pct_squared(j_star: float, j_kw: float) -> float:
    """1 - J*/J_kw: the change in the SQUARED norm, i.e. the formula as the
    thesis writes it."""
    return 100.0 * (1.0 - j_star / j_kw)


def implied_j_star(j_kw: float, printed_pct: float) -> float:
    """Invert the norm reading to recover an OCR-damaged J* cell."""
    return j_kw * (1.0 - printed_pct / 100.0) ** 2


def main() -> int:
    failures: list[str] = []
    checks = 0

    print("Dow 2011 Table 4.2, checked by arithmetic")
    print("=" * 78)
    print(f"{'geom':>5} {'J_kw':>8} {'J*':>9} {'norm %':>8} {'sq %':>8} "
          f"{'printed':>8}  verdict")

    for geom, j_kw, j_star, printed in TABLE_4_2:
        if j_star is None:
            derived = implied_j_star(j_kw, printed)
            print(f"{geom:>5} {j_kw:>8} {'OCR':>9} {'':>8} {'':>8} "
                  f"{printed:>8}  J* implied by the norm reading = "
                  f"{derived:.4g}")
            continue
        got_norm = pct_norm(j_star, j_kw)
        got_sq = pct_squared(j_star, j_kw)
        ok = abs(got_norm - printed) <= TOL_PERCENT
        checks += 1
        if not ok:
            failures.append(
                f"geometry {geom}: 1 - sqrt(J*/J_kw) = {got_norm:.2f} percent "
                f"against a printed {printed} percent")
        print(f"{geom:>5} {j_kw:>8} {j_star:>9} {got_norm:>8.1f} "
              f"{got_sq:>8.1f} {printed:>8}  {'ok' if ok else 'FAIL'}")

    # Check 7: the two OCR-damaged cells, recovered and cross-checked.
    print()
    print("The two damaged cells")
    print("-" * 78)

    g4_implied = implied_j_star(6.19, 86.3)
    g4_from_ocr = pct_norm(0.117, 6.19)
    print(f"geometry 4: table reads '0.0.117'. Reading it as 0.117 gives "
          f"{g4_from_ocr:.2f} percent, which prints as {round(g4_from_ocr, 1)} "
          f"against the printed 86.3. Inverting the printed percentage instead "
          f"implies J* = {g4_implied:.4g}, and the two agree to the last digit "
          f"the table carries, so the damaged cell is 0.117")
    checks += 1
    if round(g4_from_ocr, 1) != 86.3:
        failures.append(
            f"geometry 4: J* = 0.117 gives {g4_from_ocr:.2f} percent, which "
            f"does not print as the table's 86.3")

    g8_norm = pct_norm(GEOM_8_PROSE_J_STAR, 7.35)
    g8_table_as_ocred = pct_norm(0.840, 7.35)
    print(f"geometry 8: table reads '0.840', prose reads 0.0840. The prose "
          f"value gives {g8_norm:.1f} percent against the printed 89.3; the "
          f"OCR value gives {g8_table_as_ocred:.1f} percent. The prose is "
          f"right and the table cell has lost a zero")
    checks += 1
    if abs(g8_norm - 89.3) > TOL_PERCENT:
        failures.append(
            f"geometry 8: prose J* gives {g8_norm:.2f} percent, printed 89.3")
    checks += 1
    if abs(g8_table_as_ocred - 89.3) <= TOL_PERCENT:
        failures.append(
            "geometry 8: the OCR cell also reproduces the printed percentage, "
            "so this script cannot tell the two apart and its conclusion is "
            "not supported")

    # Check 8: the definition in the prose disagrees with the printed column.
    print()
    print("The definition the thesis prints against the column it prints")
    print("-" * 78)
    worst = max(abs(pct_squared(js, jk) - p)
                for _, jk, js, p in TABLE_4_2 if js is not None)
    best = max(abs(pct_norm(js, jk) - p)
               for _, jk, js, p in TABLE_4_2 if js is not None)
    print(f"1 - J*/J_kw, the formula as written in section 4.5.2, misses the "
          f"printed column by up to {worst:.1f} percentage points")
    print(f"1 - sqrt(J*/J_kw), the norm reading, misses it by at most "
          f"{best:.2f} percentage points")
    checks += 1
    if not (worst > 5.0 and best <= TOL_PERCENT):
        failures.append(
            "the two readings are not separated by this table, so the "
            "correction claimed above is not supported by it")

    print()
    print("=" * 78)
    if failures:
        for line in failures:
            print(f"FAIL: {line}")
        print(f"{len(failures)} of {checks} checks failed")
        return 1
    print(f"{checks} of {checks} checks passed")
    print()
    print("Carried forward: on Dow's eight random 2-D channel geometries an "
          "inferred nu_T field absorbs 70.5 to 92.1 percent of the "
          "RANS-to-DNS velocity discrepancy measured as a norm, which is "
          "91.3 to 99.4 percent measured as energy. Quote the norm reading "
          "and say which one it is.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
