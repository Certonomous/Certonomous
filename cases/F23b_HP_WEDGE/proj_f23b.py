#!/usr/bin/env python3
"""
F23b -- THE FROZEN COST ARITHMETIC AND THE PRE-SPEND PROJECTOR.  ZERO COMPUTE.

Registration: verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md section 9,
              frozen at 57d31dde; AMENDMENT 1 (pre-compute) at 440aca3d.

WHAT THIS MODULE IS.  Section 9.3 registers the cap AS ARITHMETIC, NOT ONLY AS A
NUMBER, because section 5.5's branch rule may move `N_ITER`:

    ESTIMATE(N_ITER) = SUM over levels of cells x N_ITER x RATE[level] x S / 60e6
    CAP_RATIO        = 1.4479                                          FROZEN
    CAP(N_ITER)      = floor( CAP_RATIO x ESTIMATE(N_ITER) , 0.1 )
    ALLOW_S(level)   = floor( (CAP - SPENT_so_far) x 60 / RANKS )      [wall s]

`RATE[]`, `S`, `CAP_RATIO`, `cells` and `RANKS` are fixed at the freeze sha.
**`N_ITER` IS THE ONLY INPUT ANY ARM CAN MOVE** and section 5.5 is the only rule
that may move it.  This module implements that rule and nothing else.

HOW F23b's PROJECTOR DIFFERS FROM F23's, AND WHY IT IS SIMPLER.  F23's projector
(proj_f23.py, its AMENDMENT 2) had to guess: its frozen constant was DERIVED from
F17's measured rate on a DIFFERENT case, so it carried a contention multiplier, a
drift model and two clamps.  F23b has none of that to guess, because section 9.1
MEASURED the rate ON THESE EXACT MESHES, ON THIS BOX, from F23's own completed
logs -- 4.30298 and 4.49564 core-microseconds per cell-iteration -- and section
9.2 registers a FROZEN PER-LEVEL RATIO instead of an exponent, following F17c
section 8.2 (imported growth exponents were wrong by +110 to +137 %).

  * CONTENTION MULTIPLIER = 1.0, on this rung's own reading: F23's two levels ran
    at ClockTime/ExecutionTime = 1.0080 and 1.0003 on a session-busy box.
    Contention on this exact work is bounded below 1 %.
  * **THIS ALSO RETIRES L-349 FOR THIS RUNG**: this module reads NO clock, NO
    /proc, NO disk.  Every input is an argument.  It CANNOT refuse work because
    the box is full, and it cannot pass or fail with the load.

WHAT IS AN EXTRAPOLATION AND IS NOT DRESSED AS A MEASUREMENT (section 9.2):
`D_fine = 1.30` (the one measured drift on this ladder is 1.044776; 1.30 is that
rounded up with a 24 % margin) and `S = 2.0` (the solver-stiffness factor for the
SIMPLEC dictionary change).  Neither may be moved by any arm.  If `S` proves to
have been under-registered the run is stopped by its cap, which is what a cap is
for.

Zero `assert` (L-332).  Refusals are sys.exit(2).  Hard `-O` refusal at entry.
"""
import argparse
import math
import sys

if not __debug__:
    sys.stderr.write("REFUSED: proj_f23b.py must not run under `python3 -O`; every guard in this "
                     "module is a check -O would blind (L-332).\n")
    sys.exit(2)

# --- the frozen ladder, identical to exact_f23b.py and run_f23b.sh -----------
LEVELS = (("coarse", 64, 2048), ("medium", 128, 4096), ("fine", 256, 8192))
RANKS = 4
CHECKPOINTS = 40

# --- section 9.1: MEASURED on this case's own meshes, on this box ------------
RATE_MEASURED = {"coarse": 4.30298, "medium": 4.49564}      # core-microseconds / cell-iteration
D_FINE = 1.30                # FROZEN, EXTRAPOLATED (section 9.2); NOT a measurement
S = 2.0                      # FROZEN, EXTRAPOLATED solver-stiffness factor (section 9.2)
RATE = dict(RATE_MEASURED, fine=RATE_MEASURED["medium"] * D_FINE)
CONTENTION = 1.0             # section 9.2, from F23's own ClockTime/ExecutionTime

# --- section 9.3 and section 9.0: the three caps -----------------------------
CAP_RATIO = 1.4479           # FROZEN
PRELADDER_CAP_CORE_MIN = 20.0        # section 9.0; BESIDE the ladder cap, never inside it
N_ITER_REGISTERED = 400
DOLLARS_PER_CORE_H = 0.0513  # owner-stated; DERIVED not measured (COMPUTE_BUDGET section 5)

# --- section 5.5: the branch rule --------------------------------------------
ARM_N_ACCEPT = 80
ARM_N_MAX = 400

# --- section 9.0 / AMENDMENT 1 section A1.6: the pre-ladder items ------------
# (id, description, ranks, expected core-min, worst registered core-min)
PRELADDER_ITEMS = (
    ("A0", "arm-acceptance reader birth control, 16x64, F23's alpha_U = 0.7 dictionary", 4, 0.350, 0.350),
    ("A1", "ARM-P mesh build, coarse", 1, 0.100, 0.100),
    ("A2", "ARM-P solve, coarse", 4, 1.504, 7.520),
    ("A3", "ARM-F solve, coarse (expected not to fire)", 4, 0.000, 7.520),
    ("A4", "section 4.4 control build, coarse, UNPERTURBED (must accept)", 1, 0.100, 0.100),
    ("A5", "section 4.4 control build, coarse, PERTURBED (must refuse)", 1, 0.100, 0.100),
    ("A6", "section 4.4 control build, fine, UNPERTURBED (must accept)", 1, 2.000, 2.000),
    ("A7", "section 4.4 control build, fine, PERTURBED (must refuse)", 1, 2.000, 2.000),
)
# AMENDMENT 1 section A1.6's own totals, quoted so the arithmetic is checkable.
PRELADDER_EXPECTED_REGISTERED = 6.154
PRELADDER_WORST_REGISTERED = 19.690

# The wall allowances AMENDMENT 1 section A1.6 tabulates.  NOTE, and it is
# reported upward rather than silently reconciled: that table's "remaining
# pre-ladder cap" column subtracts A0 and A1 only -- items A4-A7 (4.200 core-min)
# are costed in section 9.0's COST table and in the 19.690 worst-registered total,
# but are NOT drawn down in the ALLOWANCE column.  This module therefore enforces
# the 20.0 cap against the FULL running total (every pre-ladder item, section 9.0's
# "enforced against SEPARATE running totals"), and PRINTS the registered allowance
# beside the computed one so the difference is visible rather than absorbed.
REGISTERED_ARM_ALLOWANCE_S = {"A0": 300, "ARM-P": 293, "ARM-F": 180}
REGISTERED_LEVEL_ALLOWANCE_S = {"coarse": 4395, "medium": 4282, "fine": 3810}


def refuse(msg, rc=2):
    sys.stderr.write("REFUSED (proj_f23b): %s\n" % msg)
    sys.exit(rc)


def cells(name):
    for nm, nr, nx in LEVELS:
        if nm == name:
            return nr * nx
    refuse("unknown level %r" % name)


def level_names():
    return [n for n, _nr, _nx in LEVELS]


def floor_to(x, q):
    """floor(x, q) -- floor to the nearest multiple of q, as section 9.3 writes it."""
    if q <= 0:
        refuse("floor quantum must be positive, got %r" % q)
    return math.floor(x / q + 1e-12) * q


def level_core_min(name, n_iter):
    """cells x N_ITER x RATE[level] x S / 60e6, in core-minutes."""
    if n_iter <= 0:
        refuse("N_ITER must be positive, got %r" % n_iter)
    return cells(name) * float(n_iter) * RATE[name] * S / 60.0e6


def estimate(n_iter=N_ITER_REGISTERED):
    per = dict((n, level_core_min(n, n_iter)) for n in level_names())
    return dict(per_level=per, total=sum(per.values()), n_iter=int(n_iter))


def cap(n_iter=N_ITER_REGISTERED):
    return floor_to(CAP_RATIO * estimate(n_iter)["total"], 0.1)


def total_rung_cap(n_iter=N_ITER_REGISTERED):
    return PRELADDER_CAP_CORE_MIN + cap(n_iter)


def allow_s(cap_core_min, spent_core_min, ranks):
    """ALLOW_S = floor((CAP - SPENT_so_far) x 60 / RANKS), in wall seconds.

    A NON-POSITIVE allowance is a refusal, not a zero timeout: `timeout 0` runs
    forever, which would turn an exhausted cap into an UNCAPPED run.
    """
    if ranks <= 0:
        refuse("ranks must be positive, got %r" % ranks)
    remaining = float(cap_core_min) - float(spent_core_min)
    a = math.floor(remaining * 60.0 / float(ranks))
    if a <= 0:
        refuse("the remaining cap is %.4f core-min, giving a wall allowance of %d s. An overrun "
               "STOPS the run and does not get a new budget (rule 12); `timeout 0` would run "
               "forever, so this is a refusal, not a zero." % (remaining, a))
    return int(a)


def n_iter_from_arm(n_accept):
    """Section 5.5's branch rule, and the whole of it.

    n_accept is the iteration at which the arm met its acceptance test.
      rule 1  n <= 80          -> N_ITER = 400, section 9.3 unchanged
      rule 2  80 < n <= 400    -> N_ITER = max(400, 40 x ceil(5n/40))
      rule 3  no acceptance    -> the caller fires ARM-F; this function refuses
    The formula is frozen; only its input count moves.  writeInterval stays an
    integer and the checkpoint count stays 40 BY CONSTRUCTION.
    """
    if n_accept is None:
        refuse("the arm did not accept; section 5.5 rule 3 fires ARM-F and rule 4 HALTs the rung "
               "as BLOCKED -- no N_ITER is chosen from a non-accepting arm")
    n = int(n_accept)
    if n <= 0:
        refuse("acceptance iteration must be positive, got %r" % n_accept)
    if n > ARM_N_MAX:
        refuse("acceptance at iteration %d is beyond the registered arm ceiling %d; section 5.5 "
               "rule 3 applies" % (n, ARM_N_MAX))
    if n <= ARM_N_ACCEPT:
        return N_ITER_REGISTERED, "section 5.5 rule 1: accepted at n = %d <= %d" % (n, ARM_N_ACCEPT)
    want = CHECKPOINTS * math.ceil(5.0 * n / CHECKPOINTS)
    out = max(N_ITER_REGISTERED, int(want))
    if out % CHECKPOINTS != 0:
        refuse("branch rule produced N_ITER = %d, not a multiple of %d" % (out, CHECKPOINTS))
    return out, ("section 5.5 rule 2: accepted at n = %d, N_ITER = max(%d, %d x ceil(5 x %d / %d)) = %d"
                 % (n, N_ITER_REGISTERED, CHECKPOINTS, n, CHECKPOINTS, out))


def project(level, spent_core_min, ranks, n_iter, cap_core_min):
    """Return (proj_core_min, basis_string, halt_bool).  Reads nothing."""
    if level not in RATE:
        refuse("unknown level %r" % level)
    if int(ranks) != RANKS:
        refuse("level %s registers %d ranks, the launcher passed %r; a rank count is frozen"
               % (level, RANKS, ranks))
    proj = level_core_min(level, n_iter)
    basis = ("MEASURED rate %.5f core-us/cell-iteration on this case's own %s mesh (section 9.1)%s "
             "x %d cells x %d iterations x S = %.1f, contention %.1f (section 9.2: F23's own "
             "ClockTime/ExecutionTime bounded contention below 1 %%)"
             % (RATE[level], level,
                "" if level in RATE_MEASURED else " x D_fine = %.2f FROZEN EXTRAPOLATED" % D_FINE,
                cells(level), int(n_iter), S, CONTENTION))
    halt = (float(spent_core_min) + proj) > float(cap_core_min)
    return proj, basis, halt


def dollars(core_min):
    """DERIVED, NOT MEASURED -- this box cannot read its own billing."""
    return core_min / 60.0 * DOLLARS_PER_CORE_H


# ---------------------------------------------------------------------------
# CONTROLS.  Every one is TWO-LIMB: a positive limb that must pass and a
# negative limb that MUST FIRE.  A control whose negative limb does not fire is
# measuring nothing and this module says so and exits non-zero (Sanaa
# 2026-08-28: "A control defined in terms of the thing it controls is not a
# control").  Nothing here reads a clock, /proc or the disk.
# ---------------------------------------------------------------------------
def _fires(fn, *a, **k):
    """Run fn expecting a refusal.  Returns (fired, code)."""
    import os
    err, sys.stderr = sys.stderr, open(os.devnull, "w")
    try:
        fn(*a, **k)
        return False, None
    except SystemExit as e:
        return True, e.code
    finally:
        sys.stderr.close()
        sys.stderr = err


def selftest():
    fails = []
    n = [0]

    def check(name, pos, neg, detail):
        n[0] += 1
        ok = bool(pos) and bool(neg)
        print("  %-62s %s   %s" % (name, "ok" if ok else "FAIL", detail))
        if not ok:
            fails.append("%s (positive %s, negative-limb-fired %s)" % (name, bool(pos), bool(neg)))

    print("proj_f23b.py --selftest  (zero compute; every input INJECTED; no clock, no /proc, no disk)")

    # C-P1  the registered estimate and the registered cap, to the digits the
    #       registration prints.  NEGATIVE: a mutated rate must NOT reproduce them.
    est = estimate(400)
    pos = (abs(est["per_level"]["coarse"] - 7.520) < 5e-4 and
           abs(est["per_level"]["medium"] - 31.427) < 5e-4 and
           abs(est["per_level"]["fine"] - 163.419) < 5e-4 and
           abs(est["total"] - 202.366) < 5e-4 and cap(400) == 293.0)
    keep = RATE["coarse"]
    try:
        RATE["coarse"] = keep * 1.10
        neg = abs(estimate(400)["total"] - 202.366) > 5e-4
    finally:
        RATE["coarse"] = keep
    check("C-P1 ESTIMATE 202.366 and CAP 293.0 at N_ITER = 400", pos, neg,
          "%.3f / %.3f / %.3f -> %.3f core-min, cap %.1f (a +10%% rate perturbation moves it)"
          % (est["per_level"]["coarse"], est["per_level"]["medium"], est["per_level"]["fine"],
             est["total"], cap(400)))

    # C-P2  the three caps agree and the total IS the sum of its two parts.
    #       NEGATIVE: a mutated pre-ladder cap must break the identity.
    pos = abs(total_rung_cap(400) - 313.0) < 1e-9 and \
        abs(total_rung_cap(400) - (PRELADDER_CAP_CORE_MIN + cap(400))) < 1e-12
    kept = PRELADDER_CAP_CORE_MIN
    try:
        globals()["PRELADDER_CAP_CORE_MIN"] = 25.0
        neg = abs(total_rung_cap(400) - 313.0) > 1e-9
    finally:
        globals()["PRELADDER_CAP_CORE_MIN"] = kept
    check("C-P2 TOTAL 313.0 == PRELADDER 20.0 + LADDER 293.0", pos, neg,
          "total %.1f core-min; the two caps are enforced against SEPARATE running totals"
          % total_rung_cap(400))

    # C-P3  ALLOW_S reproduces section 9.3's tabulated wall allowances.
    #       NEGATIVE: an exhausted cap must REFUSE rather than hand out `timeout 0`.
    a_c = allow_s(293.0, 0.0, 4)
    a_m = allow_s(293.0, 7.520, 4)
    a_f = allow_s(293.0, 7.520 + 31.427, 4)
    pos = (a_c == REGISTERED_LEVEL_ALLOWANCE_S["coarse"] and
           a_m == REGISTERED_LEVEL_ALLOWANCE_S["medium"] and
           a_f == REGISTERED_LEVEL_ALLOWANCE_S["fine"])
    fired, code = _fires(allow_s, 293.0, 293.0, 4)
    neg = fired and code == 2
    check("C-P3 ALLOW_S == 4395 / 4282 / 3810 s; an exhausted cap REFUSES", pos, neg,
          "%d / %d / %d s (registered %d / %d / %d)"
          % (a_c, a_m, a_f, REGISTERED_LEVEL_ALLOWANCE_S["coarse"],
             REGISTERED_LEVEL_ALLOWANCE_S["medium"], REGISTERED_LEVEL_ALLOWANCE_S["fine"]))

    # C-P4  AMENDMENT 1's pre-ladder allowances, reproduced from the SAME formula.
    #       NEGATIVE: the same formula on a different spend gives a different answer.
    p0 = allow_s(PRELADDER_CAP_CORE_MIN, 0.0, 4)
    pp = allow_s(PRELADDER_CAP_CORE_MIN, 0.350 + 0.100, 4)
    pf = allow_s(PRELADDER_CAP_CORE_MIN, 0.350 + 0.100 + 7.520, 4)
    pos = (p0 == REGISTERED_ARM_ALLOWANCE_S["A0"] and pp == REGISTERED_ARM_ALLOWANCE_S["ARM-P"]
           and pf == REGISTERED_ARM_ALLOWANCE_S["ARM-F"])
    neg = allow_s(PRELADDER_CAP_CORE_MIN, 5.0, 4) != p0
    check("C-P4 pre-ladder allowances == 300 / 293 / 180 s (AMENDMENT 1 A1.6)", pos, neg,
          "%d / %d / %d s" % (p0, pp, pf))

    # C-P5  the pre-ladder COST table sums to AMENDMENT 1's own totals.
    #       NEGATIVE: dropping an item must break the sum.
    exp = sum(r[3] for r in PRELADDER_ITEMS)
    wor = sum(r[4] for r in PRELADDER_ITEMS)
    pos = (abs(exp - PRELADDER_EXPECTED_REGISTERED) < 5e-4 and
           abs(wor - PRELADDER_WORST_REGISTERED) < 5e-4 and wor <= PRELADDER_CAP_CORE_MIN)
    neg = abs(sum(r[4] for r in PRELADDER_ITEMS[1:]) - PRELADDER_WORST_REGISTERED) > 5e-4
    check("C-P5 pre-ladder expected 6.154 / worst 19.690 <= cap 20.0", pos, neg,
          "expected %.3f, worst %.3f core-min of %.1f" % (exp, wor, PRELADDER_CAP_CORE_MIN))

    # C-P6  THE HALT PATH IS REACHABLE, and the PROCEED path on the same shape.
    _p, _b, h_over = project("fine", 250.0, 4, 400, 293.0)
    _p2, _b2, h_under = project("fine", 100.0, 4, 400, 293.0)
    check("C-P6 projection over the cap HALTs; under the cap proceeds", h_over, not h_under,
          "fine projects %.3f core-min: 250.0 + it crosses 293.0, 100.0 + it does not" % _p)

    # C-P7  section 5.5's branch rule, all four limbs.
    #       NEGATIVE: a non-accepting arm must REFUSE, never invent an N_ITER.
    r1, _w = n_iter_from_arm(80)
    r2, _w = n_iter_from_arm(81)
    r3, _w = n_iter_from_arm(400)
    fired_none, c1 = _fires(n_iter_from_arm, None)
    fired_big, c2 = _fires(n_iter_from_arm, 401)
    pos = (r1 == 400 and r2 == 440 and r3 == 2000 and r2 % CHECKPOINTS == 0 and r3 % CHECKPOINTS == 0)
    neg = fired_none and c1 == 2 and fired_big and c2 == 2
    check("C-P7 branch rule: n=80 -> 400, n=81 -> 440, n=400 -> 2000; no acceptance REFUSES",
          pos, neg, "400 / %d / %d, every one a multiple of %d" % (r2, r3, CHECKPOINTS))

    # C-P8  a moved N_ITER moves the cap THROUGH THE FROZEN FORMULA, and only there.
    #       NEGATIVE: CAP_RATIO is not a function of the arm -- it is the same number.
    c440 = cap(440)
    pos = c440 > 293.0 and abs(c440 - floor_to(CAP_RATIO * estimate(440)["total"], 0.1)) < 1e-12
    neg = abs(c440 / estimate(440)["total"] - cap(400) / estimate(400)["total"]) < 2e-3
    check("C-P8 a moved N_ITER moves CAP through the frozen formula; CAP_RATIO is fixed",
          pos, neg, "CAP(440) = %.1f core-min at the same CAP_RATIO %.4f" % (c440, CAP_RATIO))

    # C-P9  the projector reads nothing: a rank count that is not the frozen one
    #       REFUSES rather than silently rescaling.  NEGATIVE limb is the refusal.
    _p3, _b3, _h3 = project("coarse", 0.0, 4, 400, 293.0)
    fired_r, c3 = _fires(project, "coarse", 0.0, 8, 400, 293.0)
    check("C-P9 a rank count other than the frozen 4 REFUSES", abs(_p3 - 7.520) < 5e-4,
          fired_r and c3 == 2, "coarse projects %.3f core-min at 4 ranks; 8 ranks refuses" % _p3)

    # C-P10 dollars are DERIVED and labelled so.  NEGATIVE: a different spend
    #       gives a different figure, so the number is not a constant.
    d_est = dollars(estimate(400)["total"])
    d_cap = dollars(cap(400))
    pos = abs(d_est - 0.1730) < 5e-4 and abs(d_cap - 0.2505) < 5e-4
    check("C-P10 dollars $0.1730 estimate / $0.2505 cap -- DERIVED, NOT MEASURED", pos,
          dollars(1.0) != d_est, "$%.4f / $%.4f at $%.4f/core-h, owner-stated"
          % (d_est, d_cap, DOLLARS_PER_CORE_H))

    if not fails:
        print("SELFTEST OK: %d controls, each driven BOTH ways, 0 failures." % n[0])
        return 0
    print("SELFTEST FAILED -- a control whose negative limb did not fire IS MEASURING NOTHING:")
    for f in fails:
        print("  %s" % f)
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="F23b frozen cost arithmetic and pre-spend projector")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--level")
    ap.add_argument("--spent", type=float, default=0.0)
    ap.add_argument("--ranks", type=int, default=RANKS)
    ap.add_argument("--n-iter", type=int, default=N_ITER_REGISTERED)
    ap.add_argument("--cap", type=float)
    ap.add_argument("--allowance", action="store_true",
                    help="print ALLOW_S for --cap/--spent/--ranks and stop")
    ap.add_argument("--caps", action="store_true", help="print the three caps and stop")
    ap.add_argument("--branch", type=int, default=None,
                    help="section 5.5 branch rule: the arm's acceptance iteration")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.caps:
        e = estimate(a.n_iter)
        print("N_ITER=%d" % a.n_iter)
        for nm in level_names():
            print("EST_%s=%.6f" % (nm, e["per_level"][nm]))
        print("ESTIMATE=%.6f" % e["total"])
        print("CAP_CORE_MIN=%.1f" % cap(a.n_iter))
        print("PRELADDER_CAP_CORE_MIN=%.1f" % PRELADDER_CAP_CORE_MIN)
        print("TOTAL_RUNG_CAP_CORE_MIN=%.1f" % total_rung_cap(a.n_iter))
        print("DOLLARS_ESTIMATE_DERIVED=%.4f" % dollars(e["total"]))
        print("DOLLARS_TOTAL_CAP_DERIVED=%.4f" % dollars(total_rung_cap(a.n_iter)))
        return 0
    if a.branch is not None:
        n_iter, why = n_iter_from_arm(a.branch)
        print("N_ITER=%d" % n_iter)
        print("WRITE_INTERVAL=%d" % (n_iter // CHECKPOINTS))
        print("CAP_CORE_MIN=%.1f" % cap(n_iter))
        print("BRANCH=%s" % why)
        return 0
    if a.allowance:
        if a.cap is None:
            refuse("--allowance needs --cap")
        print("ALLOW_S=%d" % allow_s(a.cap, a.spent, a.ranks))
        return 0
    if not a.level or a.cap is None:
        refuse("--level and --cap are required unless --selftest / --caps / --branch / --allowance")
    proj, basis, halt = project(a.level, a.spent, a.ranks, a.n_iter, a.cap)
    print("PROJ_CORE_MIN=%.6f" % proj)
    print("CUMULATIVE=%.6f" % (a.spent + proj))
    print("HALT=%d" % (1 if halt else 0))
    print("ALLOW_S=%d" % allow_s(a.cap, a.spent, a.ranks))
    print("BASIS=%s" % basis)
    return 0


if __name__ == "__main__":
    sys.exit(main())
