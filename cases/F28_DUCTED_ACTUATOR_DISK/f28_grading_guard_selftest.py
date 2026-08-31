#!/usr/bin/env python3
"""F28 -- SELFTEST FOR THE n == 1 GRADING GUARD IN make_mesh.py.

BOTH LIMBS.  A guard with only a positive limb is one this lab has already been
burned by, so this asserts BOTH that the guard REFUSES an inadmissible one-cell
segment and that it ACCEPTS a legitimate one.  A guard that refuses everything
passes a negative-limb-only test and is useless.

The defect being guarded: `solve_ratio(length, n=1, first)` returned 1.0
unconditionally, so `seg()` reported the REQUESTED first-cell size back to the
caller while the DELIVERED size was `length`.  `distribution()` scored its
junction match against that fiction and preferred it.

Run:  python3 cases/F28_DUCTED_ACTUATOR_DISK/f28_grading_guard_selftest.py
Exit: 0 all limbs pass, 1 a limb failed.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "case", "mesh", "make_mesh.py")

spec = importlib.util.spec_from_file_location("f28_make_mesh", GEN)
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)

fails = []


def check(name, ok, detail=""):
    print("  %-4s %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  -- " + detail) if detail else ""))
    if not ok:
        fails.append(name)


print("=== LIMB 1 (NEGATIVE): the guard must REFUSE length != first ===")
# The exact planted case that fired at F28 L1 column c1: a one-cell segment
# 0.82 * 0.0275 m long, sold as a 3.5e-4 m first cell.
PLANT_LEN, PLANT_FIRST = 0.82 * 0.0275, 3.5e-4
try:
    q = mm.solve_ratio(PLANT_LEN, 1, PLANT_FIRST)
    check("planted c1 case (%.5g m sold as %.3g m) refused"
          % (PLANT_LEN, PLANT_FIRST), False,
          "guard did NOT refuse; returned q = %r" % q)
except ValueError as e:
    check("planted c1 case (%.5g m sold as %.3g m) refused"
          % (PLANT_LEN, PLANT_FIRST), True, str(e)[:70] + "...")

# The L2 column c2 case, a different column at a different level.
try:
    mm.solve_ratio(0.015925, 1, 8.86e-4)
    check("planted L2 c2 case refused", False, "guard did NOT refuse")
except ValueError:
    check("planted L2 c2 case refused", True)

# A near miss just OUTSIDE tolerance must still refuse -- the guard must not be
# so loose that a real error slips through.
near = 3.5e-4 * (1.0 + 10.0 * mm.N1_REL_TOL)
try:
    mm.solve_ratio(near, 1, 3.5e-4)
    check("near-miss at 10x tolerance refused", False, "guard too loose")
except ValueError:
    check("near-miss at 10x tolerance refused", True)

print("\n=== LIMB 2 (POSITIVE): the guard must ACCEPT length == first ===")
try:
    q = mm.solve_ratio(1.25e-3, 1, 1.25e-3)
    check("legitimate one-cell segment accepted, q == 1.0", q == 1.0,
          "q = %r" % q)
except ValueError as e:
    check("legitimate one-cell segment accepted, q == 1.0", False,
          "guard WRONGLY refused: %s" % e)

# Exactly at the tolerance edge, from the inside, must be accepted.
inside = 3.5e-4 * (1.0 + 0.1 * mm.N1_REL_TOL)
try:
    mm.solve_ratio(inside, 1, 3.5e-4)
    check("within-tolerance one-cell segment accepted", True)
except ValueError as e:
    check("within-tolerance one-cell segment accepted", False, str(e)[:60])

print("\n=== LIMB 3: the guard must not have broken the n >= 2 path ===")
q = mm.solve_ratio(0.085, 44, 1.0e-5)
s = sum(1.0e-5 * q ** i for i in range(44))
check("n=44 series still closes on its length", abs(s - 0.085) < 1e-12,
      "q = %.8f, sum = %.12g" % (q, s))
e, qq, last = mm.seg(mm.TIP_GAP, 22, 1.0e-5)
check("seg() unchanged for n=22", abs(qq - q) > 0 and last > 1.0e-5,
      "q = %.6f, last = %.4e" % (qq, last))

print("\n=== LIMB 4 (LATENT): _series_sum n == 1 guard ===")
try:
    mm._series_sum(1.0e-3, 2.0e-3, 1)
    check("_series_sum(n=1) refused", False, "did NOT refuse")
except ValueError:
    check("_series_sum(n=1) refused", True)

print("\n=== LIMB 5: no column at any level still buys a fictional spacing ===")
for lvl in (1, 2, 3):
    nr, nx, hx = mm.level_counts(lvl)
    for name, xa, xb, ka, kb in mm.COLS:
        spec_s, d = mm.distribution(xb - xa, nx[name], hx[ka], hx[kb], name)
        c = d.get("cells")
        if not c:
            continue
        f, L = d["length_fraction"], xb - xa
        bad = ""
        if c[0] == 1 and abs(f * L - hx[ka]) > 1e-9 * max(hx[ka], 1e-12):
            bad = "left segment 1 cell of %.5g m sold as %.3g m" % (f * L,
                                                                    hx[ka])
        if c[1] == 1 and abs((1 - f) * L - hx[kb]) > 1e-9 * max(hx[kb], 1e-12):
            bad = "right segment 1 cell of %.5g m sold as %.3g m" % (
                (1 - f) * L, hx[kb])
        check("L%d %s honest" % (lvl, name), not bad, bad)

print()
if fails:
    print("SELFTEST FAILED: %d limb(s): %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("SELFTEST PASSED: all limbs, both directions.")
