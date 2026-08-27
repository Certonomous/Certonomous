#!/usr/bin/env python3
"""
F27 -- THE PRE-SPEND CAP PROJECTOR, and it is a SEPARATE, SELF-TESTING MODULE
because the one it replaces was defective.

WHAT IT REPLACES, AND WHY.  The F23 / F24 / F25 launchers project the next
level's cost as

    PROJ = PROJ_CORE_S[level] / 60 * max(1.0, ranks / max(free_cores, 0.5))

with `free_cores = nproc - load1` probed INSIDE the launcher at the moment each
level starts.  On a near-full box `free` pins at the 0.5 floor, so the
contention multiplier pins at its MAXIMUM -- 8.0x for a 4-rank entry.
F24_PRANDTL_MEYER halted at exit 3 before its fine level because of it, and
F24's own two completed levels refute the magnitude: the measured contention
effect at free = 0.5 was 1.86x where the formula applied 8.0x, overstated 4.3x.
(cfd-supervisor, verified personally, 2026-08-27.)

THE STRUCTURAL OBJECTION, which is what shapes this file.  Whether a registered
three-level ladder ever produces its FINE level -- the level that IS the
deliverable -- must not depend on the instantaneous box load at the moment that
level happens to start.  A ladder that completes or not according to contention
is not a reproducible instrument, and it is self-defeating under the standing
directive to keep the instances busy: the busier the box, the more the projector
refuses to spend.

WHAT THIS ONE DOES INSTEAD.

  1. THE FIRST LEVEL is projected from a FROZEN, MEASURED rate: microseconds of
     CORE time per cell-step, measured on THIS case, on THIS box, on THIS mesh
     family, on 4 ranks, before the pre-registration was written.
  2. EVERY LATER LEVEL is projected from THIS RUN'S OWN COMPLETED LEVELS.  Once
     the coarse level has run, its ClockTime x ranks / cell-steps IS the rate on
     this box under this load; the next level's projection is that measured rate
     times a FROZEN per-level growth factor times the next level's cell-step
     count.  A measurement of the same case an hour ago beats any model.
  3. THERE IS NO CONTENTION MULTIPLIER, and that is a decision with a reason.
     The frozen rates were themselves MEASURED under load average 19.7 on 16
     cores -- contention is already inside the basis, and multiplying a
     contention-loaded rate by a contention factor double-counts it.  The lab's
     only measured contention point is 1.86x at free = 0.5; ONE POINT IS NOT A
     LAW and this file does not dress it as one.  The box probe is still taken
     and still recorded, as an INFRASTRUCTURE observation (L-342), and it
     changes no arithmetic.
  4. THE POST-LEVEL CHECK ON ACTUAL SPEND IS UNCHANGED and is the guard that
     actually protects the budget: ClockTime x ranks / 60 summed over completed
     levels, HALT at exit 3 on a crossing, the cap never raised (rule 12).

--selftest DRIVES THE HALT PATH IN BOTH DIRECTIONS WITH INJECTED NUMBERS.  It
never reads /proc, never reads the box, and never reads a run directory: a
selftest that reads live load is load-flaky, and a flaky selftest teaches its
readers to re-run it until it passes.  That is the L-339 class and this team has
already paid for it.

Zero `assert` (L-332); refuses under `python3 -O`.
Exit codes: 0 PROCEED   3 HALT (projected to cross the cap)   2 REFUSE   1 usage
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: proj_f27.py must not run under `python3 -O`.\n")
    sys.exit(2)

import os
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f27 as EX          # noqa: E402

# MEASURED, on this case, on this box, on 4 ranks, 2026-08-27, at load average
# 19.66 on 16 cores.  Marginal ExecutionTime and ClockTime per step over a
# 200 / 150 / 24-step arm, startup EXCLUDED by differencing the first and last
# readings, times 4 ranks, divided by the level's cell count.  The LARGER of the
# two readings is taken at every level.  Scratch arms only; the run root
# verification/runs/F27_WOMERSLEY_PIPE_runs did not exist.
RATE_US_PER_CELL_STEP = dict(coarse=13.09, medium=17.48, fine=40.34)
RATE_BASIS = ("MEASURED on this case, this box, 4 ranks, 2026-08-27, load 19.66/16: marginal "
              "ExecutionTime/step 0.01256 / 0.12671 / 2.14435 s over 200 / 150 / 24 steps at "
              "3,840 / 30,720 / 245,760 cells (startup excluded by differencing), and marginal "
              "ClockTime/step 0.01005 / 0.13423 / 2.47826 s; the LARGER reading per level, x 4 ranks, "
              "/ cells = 13.09 / 17.48 / 40.34 core-microseconds per cell-step. The p-solve iteration "
              "count grows 63.7 -> 116.0 -> 233.8 per level and is what the growth is.")
# FROZEN per-level growth of the rate, from the same measurement.  Used ONLY to
# carry a measured rate forward one level.
GROWTH = dict(medium=RATE_US_PER_CELL_STEP["medium"] / RATE_US_PER_CELL_STEP["coarse"],
              fine=RATE_US_PER_CELL_STEP["fine"] / RATE_US_PER_CELL_STEP["medium"])
CONTENTION_MULTIPLIER = 1.0
CONTENTION_NOTE = ("1.0 by decision: the frozen rates were measured UNDER contention (load 19.66 on 16 "
                   "cores), so contention is already in the basis and a multiplier would double-count it. "
                   "The lab's only measured contention point is 1.86x at free_cores = 0.5 (F24's two "
                   "completed levels, cfd-supervisor 2026-08-27); one point is not a law and is not "
                   "dressed as one here. The box probe is recorded as INFRASTRUCTURE and changes no "
                   "arithmetic.")


class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


def cell_steps(level):
    if level not in EX.CELLS:
        refuse("unknown level %r" % level)
    return EX.CELLS[level] * EX.STEPS[level]


def measured_rate_us(cell_steps_done, clock_s, ranks):
    """core-microseconds per cell-step, from a COMPLETED level's own ClockTime."""
    if cell_steps_done <= 0 or clock_s < 0 or ranks <= 0:
        refuse("a measured rate needs positive cell-steps, ranks and a non-negative ClockTime; got "
               "%r, %r, %r" % (cell_steps_done, clock_s, ranks))
    return float(clock_s) * float(ranks) * 1.0e6 / float(cell_steps_done)


def rate_for(level, completed):
    """The rate to project `level` with.

    `completed` is a list of {"name", "cell_steps", "clock_s", "ranks"} for the
    levels THIS RUN has already finished, in ladder order.  Empty -> the frozen
    measured constant for that level.  Non-empty -> the LAST completed level's
    OWN measured rate carried forward by the frozen growth factor.
    """
    if level not in EX.CELLS:
        refuse("unknown level %r" % level)
    if not completed:
        return RATE_US_PER_CELL_STEP[level], "frozen measured constant (no level of this run has finished yet)"
    last = completed[-1]
    for k in ("name", "cell_steps", "clock_s", "ranks"):
        if k not in last:
            refuse("a completed-level record needs %r; got %s" % (k, sorted(last)))
    if last["name"] not in EX.CELLS:
        refuse("unknown completed level %r" % last["name"])
    order = EX.LEVEL_NAMES
    i, j = order.index(last["name"]), order.index(level)
    if j <= i:
        refuse("level %r is not after the last completed level %r" % (level, last["name"]))
    r = measured_rate_us(last["cell_steps"], last["clock_s"], last["ranks"])
    g = 1.0
    for k in range(i + 1, j + 1):
        g *= GROWTH[order[k]]
    return r * g, ("THIS RUN's measured rate at %s (%.3f core-us/cell-step from ClockTime %.6g s x %d ranks "
                   "/ %d cell-steps) carried forward by the frozen growth %.4f"
                   % (last["name"], r, last["clock_s"], last["ranks"], last["cell_steps"], g))


def project_core_min(level, completed):
    rate, basis = rate_for(level, completed)
    cs = cell_steps(level)
    proj = cs * rate * CONTENTION_MULTIPLIER / 1.0e6 / 60.0
    return dict(level=level, cell_steps=cs, rate_us_per_cell_step=rate, rate_basis=basis,
                contention_multiplier=CONTENTION_MULTIPLIER, contention_note=CONTENTION_NOTE,
                projected_core_min=proj)


def decide(spent_core_min, projected_core_min, cap_core_min):
    if cap_core_min <= 0:
        refuse("cap must be positive, got %r" % cap_core_min)
    total = float(spent_core_min) + float(projected_core_min)
    return ("HALT" if total > float(cap_core_min) else "PROCEED"), total


# ---------------------------------------------------------------------------
def check(name, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, ("  -- %s" % detail) if detail else ""))
    return bool(ok)


def selftest():
    """EVERY NUMBER BELOW IS INJECTED.  Nothing here reads /proc, the box, or a
    run directory."""
    ok = True
    print("proj_f27 --selftest: the halt path driven in BOTH directions, on INJECTED numbers only")

    # (i) the first level uses the frozen constant; a later one uses THIS RUN's measurement
    p0 = project_core_min("coarse", [])
    ok &= check("first level projects from the frozen measured constant",
                "frozen" in p0["rate_basis"] and abs(p0["rate_us_per_cell_step"] - 13.09) < 1e-12,
                "%.3f core-min" % p0["projected_core_min"])
    done = [dict(name="coarse", cell_steps=cell_steps("coarse"), clock_s=100.0, ranks=4)]
    p1 = project_core_min("medium", done)
    r_meas = measured_rate_us(cell_steps("coarse"), 100.0, 4)
    ok &= check("later level projects from THIS RUN's own completed level",
                "THIS RUN" in p1["rate_basis"]
                and abs(p1["rate_us_per_cell_step"] - r_meas * GROWTH["medium"]) < 1e-9,
                "measured %.3f -> projected rate %.3f core-us/cell-step" % (r_meas, p1["rate_us_per_cell_step"]))

    # (ii) THE DEFECT THAT IS ABSENT, checked BEHAVIOURALLY and STRUCTURALLY --
    #      never by grepping this file's own text, which quotes the defective
    #      form in its docstring and would fail its own check for saying so.
    import ast as _ast
    import inspect as _inspect
    tree = _ast.parse(open(os.path.abspath(__file__)).read())
    body_max = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.FunctionDef) and node.name in ("project_core_min", "rate_for",
                                                                "measured_rate_us", "decide", "cell_steps"):
            body_max += [n.lineno for n in _ast.walk(node)
                         if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name) and n.func.id == "max"]
    sig = list(_inspect.signature(project_core_min).parameters)
    exact = p1["cell_steps"] * p1["rate_us_per_cell_step"] / 1.0e6 / 60.0
    ok &= check("no contention multiplier anywhere in the projection arithmetic",
                CONTENTION_MULTIPLIER == 1.0 and not body_max and sig == ["level", "completed"]
                and abs(p1["projected_core_min"] - exact) < 1e-12,
                "no max() call node in any projection function; signature %s takes no box reading; "
                "projected == cell_steps x rate exactly" % sig)
    # ... and DRIVEN: the projection is a pure function of (level, completed), so
    # two calls made under any box condition whatever return the same number.
    ok &= check("the projection is a pure function of (level, completed)",
                project_core_min("fine", done)["projected_core_min"]
                == project_core_min("fine", done)["projected_core_min"])

    # (iii) THE HALT PATH, DRIVEN BOTH WAYS on injected spend/cap
    d_go, t_go = decide(10.0, 100.0, 680.0)
    d_halt, t_halt = decide(600.0, 100.0, 680.0)
    ok &= check("PROCEED when spent + projected <= cap", d_go == "PROCEED", "%.1f <= 680" % t_go)
    ok &= check("HALT when spent + projected > cap", d_halt == "HALT", "%.1f > 680" % t_halt)
    d_edge, _ = decide(580.0, 100.0, 680.0)
    ok &= check("the boundary spent + projected == cap PROCEEDS (the cap is inclusive)",
                d_edge == "PROCEED")
    d_over, _ = decide(580.0, 100.000001, 680.0)
    ok &= check("one microminute past the cap HALTS (the guard is not a rounding)", d_over == "HALT")

    # (iv) the CLI is the same code path: an injected run must exit 3
    import subprocess
    me = os.path.abspath(__file__)
    r = subprocess.run([sys.executable, me, "--level", "fine", "--spent", "600", "--cap", "680",
                        "--completed", json.dumps(done)], capture_output=True, text=True)
    ok &= check("the CLI exits 3 on a projected crossing", r.returncode == 3, r.stdout.strip()[-90:])
    r2 = subprocess.run([sys.executable, me, "--level", "coarse", "--spent", "0", "--cap", "680",
                        "--completed", "[]"], capture_output=True, text=True)
    ok &= check("the CLI exits 0 when the projection fits", r2.returncode == 0, r2.stdout.strip()[-90:])

    # (v) refusals
    for args, why in (((cell_steps("coarse"), -1.0, 4), "negative ClockTime"),
                      ((0, 1.0, 4), "zero cell-steps")):
        try:
            measured_rate_us(*args)
            ok &= check("refuses %s" % why, False, "did not refuse")
        except Refusal:
            ok &= check("refuses %s" % why, True)
    try:
        rate_for("coarse", [dict(name="medium", cell_steps=1, clock_s=1.0, ranks=4)])
        ok &= check("refuses projecting BACKWARD along the ladder", False, "did not refuse")
    except Refusal:
        ok &= check("refuses projecting BACKWARD along the ladder", True)

    # (vi) the registered ladder's own full projection, printed for the record
    total, done2 = 0.0, []
    for nm in EX.LEVEL_NAMES:
        p = project_core_min(nm, done2)
        total += p["projected_core_min"]
        done2.append(dict(name=nm, cell_steps=cell_steps(nm),
                          clock_s=p["projected_core_min"] * 60.0 / 4, ranks=4))
        print("    %-7s %d cell-steps x %.2f core-us = %.3f core-min" %
              (nm, p["cell_steps"], p["rate_us_per_cell_step"], p["projected_core_min"]))
    print("    registered-ladder total on the frozen rates: %.2f core-min" % total)
    print("SELFTEST %s" % ("GREEN" if ok else "RED"))
    return 0 if ok else 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--level")
    ap.add_argument("--spent", type=float)
    ap.add_argument("--cap", type=float)
    ap.add_argument("--completed", default="[]",
                    help="JSON list of this run's completed levels: "
                         "[{name, cell_steps, clock_s, ranks}, ...]")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.level or a.spent is None or a.cap is None:
        sys.stderr.write("usage: proj_f27.py --level <name> --spent <core_min> --cap <core_min> "
                         "[--completed <json>]  |  --selftest\n")
        return 1
    try:
        completed = json.loads(a.completed)
        p = project_core_min(a.level, completed)
        d, total = decide(a.spent, p["projected_core_min"], a.cap)
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return 2
    except (ValueError, TypeError) as e:
        sys.stderr.write("REFUSED: --completed did not parse: %s\n" % e)
        return 2
    print("%s level=%s cell_steps=%d rate=%.4f core-us/cell-step projected=%.4f core-min "
          "spent=%.4f total=%.4f cap=%.4f contention=%.1f basis=%s"
          % (d, p["level"], p["cell_steps"], p["rate_us_per_cell_step"], p["projected_core_min"],
             a.spent, total, a.cap, CONTENTION_MULTIPLIER, p["rate_basis"]))
    return 3 if d == "HALT" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        sys.exit(2)
