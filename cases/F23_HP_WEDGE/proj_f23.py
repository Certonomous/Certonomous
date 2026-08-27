#!/usr/bin/env python3
"""
F23 -- PRE-SPEND PROJECTOR (AMENDMENT 2, 2026-08-27).  ZERO COMPUTE.

WHAT THIS REPLACES, AND WHY
===========================
The launcher's pre-level projector was

    PROJ = PROJ_CORE_S[level] / 60.0 * max(1.0, ranks / max(free_cores, 0.5))

-- a FROZEN constant times a GUESSED contention multiplier.  For a 4-rank entry
on a saturated box `free` pins at the 0.5 floor and the multiplier pins at its
maximum, 8.0x.  F24_PRANDTL_MEYER's two COMPLETED levels refute that magnitude
from its own logs (verification/campaign/F24_PRANDTL_MEYER_RESULTS.md section 5,
calibration row C-161): the measured effect at free = 0.5 was 1.86x where the
formula applied 8.0x -- overstated about 4.3x.  Applied to F23 the same pin projects
3,627 core-min of a 1,100 cap at the fine level and HALTS after burning ~75
core-min on two levels that cannot form a Roache triple.

F23 carries a SECOND reason to project from its own levels, sharper than F25's.
F23's frozen PROJ_CORE_S is not even a measurement of F23: run_f23.sh:42-47
records it as DERIVED from F17's measured rate on a DIFFERENT case and says in
terms "NOT MEASURED on this case".  C-152/C-153 is precisely this failure --
F21 and F22 each measured their own base rate correctly and each still missed,
because they imported another case's growth exponent.  So for F23 the frozen
constant is a borrowed curve times a guessed multiplier, and the first completed
level replaces BOTH with something this case actually did.

Worse than the magnitude is the SHAPE: `free` is probed inside the launcher at
the moment each level starts, HOURS after launch, so whether a registered
three-level ladder ever produces its fine level depends on the instantaneous box
load at that moment.  A verification instrument whose ladder completes or not
according to box contention is not reproducible, and it is self-defeating under
the standing directive to keep the box busy -- it converts a full box into a
refusing box.

WHAT REPLACES IT
================
Project from THE CASE'S OWN COMPLETED LEVELS.  Once a level has run, the
launcher knows this case's core-seconds per cell-iteration ON THIS BOX UNDER
THIS LOAD.  Three regimes, in order:

  (1) NO level measured yet (the first level only).  No measurement exists, so
      fall back to the frozen PROJ_CORE_S constant, times a contention factor
      BOUNDED AT CONT_MAX:

          CONT = min(CONT_MAX, max(1.0, ranks / max(free, 0.5)))

      CONT_MAX = 2.0.  Its basis, stated as exactly what it is: the ONE point
      the lab holds is F24's medium level, 1.86x its frozen base with the probe
      reading free = 0.5.  That 1.86x is an UPPER BOUND ON CONTENTION ALONE,
      because it also carries base-rate misprediction.  2.0 bounds it; 8.0 does
      not.  ONE POINT IS NOT A LAW and this constant is not claimed to be one.

  (2) ONE level measured.  rate = core_s / cell_iters from that level -- a rate
      that ALREADY CARRIES whatever load it ran under, so NO further contention
      term is applied (multiplying an already-contended measured rate by a
      contention factor double-counts the same effect).  The residual
      uncertainty is not contention, it is RATE DRIFT across the size jump, and
      the only drift model available before a second measurement is the one the
      pre-registration already committed:

          D = clamp(frozen_rate[next] / frozen_rate[measured], 1.0, DRIFT_MAX)
          PROJ = rate * cell_iters[next] * D / 60

  (3) TWO OR MORE levels measured.  The case's OWN measured drift supersedes the
      frozen model -- this is C-152/C-153's lesson in code (F21 and F22 each
      MEASURED their base rate correctly on their own coarse grid and each MISSED
      by importing another case's growth exponent):

          g = rate[last] / rate[previous]
          D = clamp(g, 1.0, DRIFT_MAX)
          PROJ = rate[last] * cell_iters[next] * D / 60

THE TWO CLAMPS, AND WHY THEY ARE WHERE THEY ARE
===============================================
  * FLOOR 1.0 on D -- an IMPROVING rate is never extrapolated.  F24 measured
    2.519 then 1.674 core-us per cell-iteration: the rate got FASTER as fixed
    per-run overheads (mesh, decomposition, MPI startup, I/O) amortised over 8x
    the cell-iterations.  That improvement SATURATES.  Extrapolating it would
    project F24's fine level at 801 core-min, more optimistic than any bound the
    record supports.  Clamped at 1.0 the same replay projects 1,205 core-min.

  * CEILING DRIFT_MAX = 2.5 on D -- justified from measurement, not from taste.
    The per-doubling rate ratios the lab MEASURED on 2026-08-27 are 2.36 and 2.23
    (F22, row C-153) and 2.10 and 2.13 (F21, row C-152).  A ceiling of 2.0 would
    have UNDER-projected all four.  2.5 covers every growth the lab has measured
    and still bounds a runaway.  If a future case measures above 2.5 the ceiling
    is what makes the projection an UNDER-estimate, and the post-level ACTUAL
    check -- unchanged, on measured ClockTime x ranks / 60 -- is what then stops
    the run.  The projector is a runaway guard; the actual check is the budget.

WHAT IS NOT CHANGED BY THIS AMENDMENT
=====================================
The registered CAP (1100 core-min) does not move.  The post-level incremental
check on ACTUAL spend does not move.  The halt on a crossing does not move: a
projection over the cap still HALTS at exit 3, unlaunched levels stay PENDING,
and the cap is never raised (CLAUDE.md rule 12).  No gate, threshold, band or
label is touched.

Zero `assert` (L-332).  Refusals are sys.exit(2).  Hard `-O` refusal at entry.
"""
import argparse
import os
import sys

CONT_MAX = 2.0            # bound on the first-level contention factor (see above)
DRIFT_MAX = 2.5           # bound on the per-level rate-drift factor (see above)
DRIFT_MIN = 1.0           # an improving rate is never extrapolated

# --- the frozen ladder, identical to run_f23.sh and exact_f23.py -------------
N_ITER = 4000
RANKS = 4
# name -> (nr, nx); cells = nr * nx (a 2-D wedge: nr across the gap, nx along it).
# DIM = 2 here, against F25's 3: the ladder refines in BOTH directions, r = 2 exactly,
# so the cell count quadruples per level where F25's octuples.
LEVELS = (("coarse", 64, 2048), ("medium", 128, 4096), ("fine", 256, 8192))
# frozen serial-equivalent core-seconds per level.  NOTE, and it is the point of
# this amendment: these are DERIVED from F17's measured rate on a DIFFERENT case
# (run_f23.sh:42-47, "NOT MEASURED on this case"), not measured on F23.
FROZEN_CORE_S = {"coarse": 583.0, "medium": 3940.0, "fine": 26640.0}


def refuse(msg, rc=2):
    sys.stderr.write("REFUSED (proj_f23): %s\n" % msg)
    sys.exit(rc)


def _o_guard():
    if not __debug__:
        refuse("python -O disables the checks this module is made of; run without -O")


def cell_iters(name):
    for nm, nr, nx in LEVELS:
        if nm == name:
            return float(nr * nx) * float(N_ITER)
    refuse("unknown level %r" % name)


def frozen_rate(name):
    """core-seconds per cell-iteration implied by the FROZEN constant."""
    return FROZEN_CORE_S[name] / cell_iters(name)


def clamp(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


def project(level, spent_core_min, free_cores, ranks, measured, cap_core_min):
    """Return (proj_core_min, basis_string, halt_bool).

    `measured` is an ordered list of (level_name, core_seconds) for levels this
    invocation has ALREADY COMPLETED, oldest first.  Nothing here reads the
    disk, a clock or /proc: every input is handed in, so the controls can inject
    a box reading instead of probing a live one (the L-339 class -- a selftest
    that reads live /proc/stat is load-flaky).
    """
    if level not in FROZEN_CORE_S:
        refuse("unknown level %r" % level)
    if ranks <= 0:
        refuse("ranks must be positive, got %r" % ranks)
    want = cell_iters(level)

    if len(measured) == 0:
        cont = clamp(ranks / max(float(free_cores), 0.5), 1.0, CONT_MAX)
        proj = FROZEN_CORE_S[level] / 60.0 * cont
        basis = ("frozen constant %.1f core-s (no level measured yet) x contention %.4f "
                 "[= clamp(ranks %d / max(free %.4f, 0.5), 1.0, CONT_MAX %.1f)]"
                 % (FROZEN_CORE_S[level], cont, ranks, float(free_cores), CONT_MAX))
    else:
        last_name, last_core_s = measured[-1]
        if last_core_s <= 0.0:
            refuse("measured core-seconds for level %r must be positive, got %r"
                   % (last_name, last_core_s))
        rate = float(last_core_s) / cell_iters(last_name)
        if len(measured) == 1:
            g = frozen_rate(level) / frozen_rate(last_name)
            src = ("frozen rate ratio %s->%s %.4f (ONE level measured)"
                   % (last_name, level, g))
        else:
            prev_name, prev_core_s = measured[-2]
            if prev_core_s <= 0.0:
                refuse("measured core-seconds for level %r must be positive" % prev_name)
            prev_rate = float(prev_core_s) / cell_iters(prev_name)
            g = rate / prev_rate
            src = ("MEASURED rate drift %s->%s %.4f (this case's own two levels)"
                   % (prev_name, last_name, g))
        d = clamp(g, DRIFT_MIN, DRIFT_MAX)
        proj = rate * want * d / 60.0
        basis = ("measured rate %.6g core-s per cell-iteration from level %s "
                 "(%.1f core-s / %.6g cell-iterations; the load it ran under is ALREADY in it, "
                 "so NO contention factor is applied) x %.6g cell-iterations x drift %.4f "
                 "[= clamp(%s, %.1f, %.1f)]"
                 % (rate, last_name, float(last_core_s), cell_iters(last_name),
                    want, d, src, DRIFT_MIN, DRIFT_MAX))
    halt = (spent_core_min + proj) > cap_core_min
    return proj, basis, halt


def parse_measured(s):
    out = []
    if not s:
        return out
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split(":")
        if len(bits) != 2:
            refuse("--measured entries are <level>:<core_seconds>, got %r" % part)
        try:
            out.append((bits[0], float(bits[1])))
        except ValueError:
            refuse("--measured core-seconds is not a number in %r" % part)
    return out


# ---------------------------------------------------------------------------
# PLANTED CONTROLS.  The box reading is INJECTED at every one of them; none of
# them reads /proc, a clock or the disk (L-339: a control that reads live load
# passes or fails with the box).  Every control names what it would catch.
# ---------------------------------------------------------------------------
def selftest():
    global CONT_MAX
    fails = []

    def check(name, cond, detail):
        print("  %-58s %s   %s" % (name, "ok" if cond else "FAIL", detail))
        if not cond:
            fails.append(name)

    print("proj_f23.py --selftest  (zero compute; every box reading INJECTED)")

    # C1  the 8.0x pin is GONE: a 4-rank entry at free = 0.5 gets CONT_MAX, not 8.
    p1, b1, h1 = project("coarse", 0.0, 0.5, 4, [], 1100.0)
    want1 = FROZEN_CORE_S["coarse"] / 60.0 * CONT_MAX
    check("C1 first level, saturated box -> contention pinned at CONT_MAX",
          abs(p1 - want1) < 1e-9 and not h1,
          "%.4f core-min (the OLD form would have given %.4f)"
          % (p1, FROZEN_CORE_S["coarse"] / 60.0 * (4 / 0.5)))

    # C2  an idle box costs nothing extra.
    p2, _b, _h = project("coarse", 0.0, 16.0, 4, [], 1100.0)
    check("C2 first level, idle box -> contention 1.0",
          abs(p2 - FROZEN_CORE_S["coarse"] / 60.0) < 1e-9, "%.4f core-min" % p2)

    # C3  ONE level measured AT its frozen rate reproduces the frozen projection
    #     for the next level exactly -- the amendment does not silently move the
    #     registered numbers when the case behaves as registered.
    p3, _b, _h = project("medium", 4.1, 0.5, 4, [("coarse", FROZEN_CORE_S["coarse"])], 1100.0)
    check("C3 one level at its frozen rate -> the frozen projection, unchanged",
          abs(p3 - FROZEN_CORE_S["medium"] / 60.0) < 1e-6,
          "%.4f core-min vs frozen %.4f" % (p3, FROZEN_CORE_S["medium"] / 60.0))

    # C4  FLOOR: an improving measured rate is NOT extrapolated.  Planted g = 0.5.
    slow = FROZEN_CORE_S["coarse"]
    fast_medium = slow * (cell_iters("medium") / cell_iters("coarse")) * 0.5   # rate halved
    p4, b4, _h = project("fine", 100.0, 0.5, 4,
                         [("coarse", slow), ("medium", fast_medium)], 100000.0)
    rate_m = fast_medium / cell_iters("medium")
    check("C4 improving rate -> drift clamped UP to 1.0, never extrapolated",
          abs(p4 - rate_m * cell_iters("fine") / 60.0) < 1e-6 and "drift 1.0000" in b4,
          "%.2f core-min" % p4)

    # C5  CEILING: a runaway measured rate is clamped at DRIFT_MAX.  Planted g = 4.
    slow_medium = slow * (cell_iters("medium") / cell_iters("coarse")) * 4.0
    p5, b5, _h = project("fine", 100.0, 0.5, 4,
                         [("coarse", slow), ("medium", slow_medium)], 1e9)
    rate_m5 = slow_medium / cell_iters("medium")
    check("C5 runaway rate -> drift clamped DOWN to DRIFT_MAX",
          abs(p5 - rate_m5 * cell_iters("fine") * DRIFT_MAX / 60.0) < 1e-6
          and ("drift %.4f" % DRIFT_MAX) in b5,
          "%.2f core-min" % p5)

    # C6  THE HALT PATH IS REACHABLE, and on a MEASURED projection, not a guess.
    huge = FROZEN_CORE_S["medium"] * 50.0
    p6, _b, h6 = project("fine", 500.0, 8.0, 4,
                         [("coarse", FROZEN_CORE_S["coarse"]), ("medium", huge)], 1100.0)
    check("C6 measured rate projecting OVER the cap -> HALT true",
          h6 and (500.0 + p6) > 1100.0,
          "proj %.1f core-min, cumulative %.1f of 1100" % (p6, 500.0 + p6))

    # C7  and the PROCEED path is reachable on the same shape.
    p7, _b, h7 = project("fine", 80.0, 8.0, 4,
                         [("coarse", FROZEN_CORE_S["coarse"]),
                          ("medium", FROZEN_CORE_S["medium"])], 1100.0)
    check("C7 measured rate projecting UNDER the cap -> HALT false",
          (not h7) and (80.0 + p7) <= 1100.0,
          "proj %.1f core-min, cumulative %.1f of 1100" % (p7, 80.0 + p7))

    # C8  PLANTED: the controls can SEE the constant they are guarding.  If
    #     CONT_MAX were the old 8.0, C1's answer would differ -- shown, not asserted.
    keep = CONT_MAX
    try:
        CONT_MAX = 8.0
        p8, _b, _h = project("coarse", 0.0, 0.5, 4, [], 1100.0)
    finally:
        CONT_MAX = keep
    check("C8 PLANTED: mutating CONT_MAX to the old 8.0 CHANGES C1's answer",
          abs(p8 - p1) > 1e-6, "%.4f vs %.4f core-min" % (p8, p1))

    # C9  a non-positive measured reading is REFUSED, not silently used.
    #     Caught IN PROCESS, deliberately NOT via os.fork(): a forked child
    #     inherits this function's BUFFERED stdout and flushes it again when
    #     refuse()'s SystemExit unwinds, printing every control above a second
    #     time.  Measured 2026-08-27: C1-C8 appeared twice whenever stdout was a
    #     pipe, so anyone counting "ok" lines to check the control count read 17
    #     where there are 9.  The fork also never reached its own os._exit(0).
    _err, sys.stderr = sys.stderr, open(os.devnull, "w")
    try:
        project("medium", 0.0, 8.0, 4, [("coarse", 0.0)], 1100.0)
        rc9 = None
    except SystemExit as e:
        rc9 = e.code
    finally:
        sys.stderr.close()
        sys.stderr = _err
    check("C9 a zero measured core-seconds REFUSES (exit 2), never divides",
          rc9 == 2, "SystemExit code %r (None would mean it returned a number)" % (rc9,))

    if not fails:
        print("SELFTEST OK: %d controls, 0 failures." % 9)
        return 0
    print("SELFTEST FAILED: %s" % ", ".join(fails))
    return 1


def main(argv=None):
    _o_guard()
    ap = argparse.ArgumentParser(description="F23 pre-spend projector (Amendment 2)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--level")
    ap.add_argument("--spent", type=float, default=0.0)
    ap.add_argument("--free", type=float, default=0.5)
    ap.add_argument("--ranks", type=int, default=RANKS)
    ap.add_argument("--measured", default="")
    ap.add_argument("--cap", type=float)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.level or a.cap is None:
        refuse("--level and --cap are required unless --selftest")
    proj, basis, halt = project(a.level, a.spent, a.free, a.ranks,
                                parse_measured(a.measured), a.cap)
    print("PROJ_CORE_MIN=%.6f" % proj)
    print("CUMULATIVE=%.6f" % (a.spent + proj))
    print("HALT=%d" % (1 if halt else 0))
    print("BASIS=%s" % basis)
    return 0


if __name__ == "__main__":
    sys.exit(main())
