#!/usr/bin/env python3
"""
F17c -- THE PRE-SPEND CAP PROJECTOR.  A SEPARATE, SELF-TESTING MODULE, in the
AMENDED form (cases/F27_WOMERSLEY_PIPE/proj_f27.py), because the inline form it
replaces is L-349.

WHAT IT REPLACES.  The F23 / F24 / F25 launchers, and F17b's own, project the
next level's cost with a CONTENTION MULTIPLIER read from /proc at the moment
the level starts:

    PROJ = PROJ_CORE_S[level] / 60 * max(1.0, ranks / max(free_cores, 0.5))
    PROJ = PROJ_SERIAL_S[level] / min(ranks, free_cores) * ranks / 60   # F17b

`free_cores = nproc - load1`.  The queue runner fires at an 85 % busy ceiling,
so by construction the box is near-full when a level begins, `free` pins at its
floor, and the multiplier pins at its MAXIMUM.  F24_PRANDTL_MEYER halted at
exit 3 before its fine level because of it, against a measured contention
effect of 1.86x where the formula applied 8.0x (cfd-supervisor, verified
personally, 2026-08-27; L-349).  A guard that refuses work precisely because
the box is full is self-defeating under the standing directive to keep the
instances busy.

WHY THIS RUNG CANNOT AFFORD THAT DEFECT IN PARTICULAR.  F17c's deliverable IS
its fine level: 48,000 iterations at 768x512, 93.6 % of the ladder's projected
spend.  A projector that halts before it returns nothing at all -- the coarse
and medium levels alone re-measure what F17 and F17b already have on disk.

CONTENTION_MULTIPLIER = 1.0, AND THE ARGUMENT IS THIS RUNG'S OWN, NOT F27's.
F27 sets 1.0 because its rates were measured UNDER load and a multiplier would
double-count what the measurement already contains.  That argument is not
available here: F17b's rates were measured at wall/CPU ratios of 1.0077,
1.0080 and 1.0001 -- essentially uncontended.  The argument that IS available
is stronger and is a measurement rather than an inference: THOSE RATIOS ARE
THE CONTENTION EFFECT, MEASURED, ON THIS EXACT WORK.  A 1-rank job on a
16-core box needs one core, and the queue runner will not launch below 2.4
free; F17b ran 21:22-21:51Z on a session-busy box and lost 0.8 % of wall time
to scheduling at worst.  0.8 % sits inside the +/- 16 % run-to-run spread the
rate band already carries (the SAME 24,576-cell mesh measured 0.5826 us/cell-
iteration under F17 and 0.6751 under F17b).  A multiplier would add an effect
this rung has bounded below one percent.  The box probe is still taken and
still recorded as an INFRASTRUCTURE observation (L-342); it changes no
arithmetic.

THE RATES, AND THE FINDING THEY CARRY.  MEASURED on THESE THREE MESHES, on
this box, on 1 rank, from F17b's own logs (verification/runs/F17b_runs/<level>/
log.simpleFoam), as the MARGINAL cost per iteration -- first and last
ExecutionTime readings differenced, so startup is excluded -- divided by the
cell count:

    coarse   24,576 cells   0.6751 core-us per cell-iteration
    medium   98,304 cells   0.9347
    fine    393,216 cells   0.7447

THE RATE IS NOT MONOTONE IN PROBLEM SIZE.  It rises 38.5 % from coarse to
medium and FALLS 20.3 % from medium to fine.  Across six levels spanning 256x
in size (F17's 1,536 / 6,144 / 24,576 at 0.5063 / 0.4676 / 0.5826 and F17b's
three above) it rises, falls, rises and falls again, peaking at 98,304 cells.
THIS RUNG THEREFORE REGISTERS NO PER-DOUBLING GROWTH EXPONENT.  The lab's
standing calibration defect -- +110 / +136 / +137 % measured against +72 / +75
/ +80 % registered on F21 / F22 / F18b, with base rates right to 7-10 % -- is
consistent with fitting a monotone exponent to a rate that is not monotone: any
exponent taken from two levels extrapolates the wrong way to the third.  The
GROWTH factors below are per-level RATIOS from one measurement, not an
exponent, and GROWTH["fine"] IS LESS THAN ONE.  A projector that could not
carry a growth factor below 1 would over-project this ladder by 25 %.
A MECHANISM IS OFFERED AND IS NOT MEASURED: this box is an AMD EPYC 9R14 with
16 MiB L2 and 64 MiB L3 in 2 instances, and the three working sets straddle
that.  It is a hypothesis; the non-monotonicity is the measurement.

--selftest DRIVES THE HALT PATH IN BOTH DIRECTIONS WITH INJECTED NUMBERS.  It
never reads /proc, never reads the box, and never reads a run directory.

Zero `assert` (L-332); refuses under `python3 -O`.
Exit codes: 0 PROCEED   3 HALT (projected to cross the cap)   2 REFUSE   1 usage
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: proj_f17c.py must not run under `python3 -O`.\n")
    sys.exit(2)

import os
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f17c as EX          # noqa: E402

LEVEL_NAMES = [n for n, _nx, _ny in EX.LEVELS]
CELLS = dict((n, nx * ny) for n, nx, ny in EX.LEVELS)

RATE_US_PER_CELL_ITER = dict(coarse=0.6751, medium=0.9347, fine=0.7447)
RATE_BASIS = ("MEASURED on THESE THREE MESHES, this box, 1 rank, from F17b's own logs "
              "(2026-08-26): marginal ExecutionTime per iteration 0.016592 / 0.091880 / "
              "0.292833 s over 4,000 iterations at 24,576 / 98,304 / 393,216 cells, "
              "startup excluded by differencing the first and last readings, divided by "
              "the cell count = 0.6751 / 0.9347 / 0.7447 core-microseconds per "
              "cell-iteration. The rate is NOT MONOTONE in problem size (+38.5 % then "
              "-20.3 %), so NO per-doubling growth exponent is registered. Run-to-run "
              "spread on the SAME 24,576-cell mesh: 0.5826 (F17) vs 0.6751 (F17b) = 16 %.")

# FROZEN per-level RATIOS from that one measurement, used ONLY to carry a
# measured rate forward one level. NOT an exponent. GROWTH["fine"] < 1.
GROWTH = dict(medium=RATE_US_PER_CELL_ITER["medium"] / RATE_US_PER_CELL_ITER["coarse"],
              fine=RATE_US_PER_CELL_ITER["fine"] / RATE_US_PER_CELL_ITER["medium"])
CONTENTION_MULTIPLIER = 1.0
CONTENTION_NOTE = ("1.0, on THIS rung's own measurement and not on F27's argument. F17b's "
                   "three 1-rank levels ran at wall/CPU ratios 1.0077 / 1.0080 / 1.0001 on a "
                   "session-busy box: the contention effect on this exact work is bounded "
                   "below 0.8 %, which sits inside the +/- 16 % run-to-run spread the rate "
                   "band already carries. The L-349 form pins at its maximum on a full box "
                   "and is absent here, checked structurally and behaviourally by --selftest. "
                   "The box probe is recorded as INFRASTRUCTURE (L-342) and changes no "
                   "arithmetic.")


class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


def cell_iterations(level):
    if level not in CELLS:
        refuse("unknown level %r" % level)
    return CELLS[level] * EX.n_iter(level)


def measured_rate_us(cell_iters_done, clock_s, ranks):
    """core-microseconds per cell-iteration, from a COMPLETED level's ClockTime."""
    if cell_iters_done <= 0 or clock_s < 0 or ranks <= 0:
        refuse("a measured rate needs positive cell-iterations, ranks and a non-negative "
               "ClockTime; got %r, %r, %r" % (cell_iters_done, clock_s, ranks))
    return float(clock_s) * float(ranks) * 1.0e6 / float(cell_iters_done)


def rate_for(level, completed):
    """The rate to project `level` with.

    `completed` is a list of {"name", "cell_iters", "clock_s", "ranks"} for the
    levels THIS RUN has already finished, in ladder order. Empty -> the frozen
    measured constant. Non-empty -> the LAST completed level's OWN measured rate
    carried forward by the frozen per-level ratio.
    """
    if level not in CELLS:
        refuse("unknown level %r" % level)
    if not completed:
        return RATE_US_PER_CELL_ITER[level], "frozen measured constant (no level of this run has finished yet)"
    last = completed[-1]
    for k in ("name", "cell_iters", "clock_s", "ranks"):
        if k not in last:
            refuse("a completed-level record needs %r; got %s" % (k, sorted(last)))
    if last["name"] not in CELLS:
        refuse("unknown completed level %r" % last["name"])
    i, j = LEVEL_NAMES.index(last["name"]), LEVEL_NAMES.index(level)
    if j <= i:
        refuse("level %r is not after the last completed level %r" % (level, last["name"]))
    r = measured_rate_us(last["cell_iters"], last["clock_s"], last["ranks"])
    g = 1.0
    for k in range(i + 1, j + 1):
        g *= GROWTH[LEVEL_NAMES[k]]
    return r * g, ("THIS RUN's measured rate at %s (%.4f core-us/cell-iteration from ClockTime "
                   "%.6g s x %d ranks / %d cell-iterations) carried forward by the frozen "
                   "per-level ratio %.4f" % (last["name"], r, last["clock_s"], last["ranks"],
                                             last["cell_iters"], g))


def project_core_min(level, completed):
    rate, basis = rate_for(level, completed)
    ci = cell_iterations(level)
    proj = ci * rate * CONTENTION_MULTIPLIER / 1.0e6 / 60.0
    return dict(level=level, cell_iterations=ci, rate_us_per_cell_iteration=rate,
                rate_basis=basis, contention_multiplier=CONTENTION_MULTIPLIER,
                contention_note=CONTENTION_NOTE, projected_core_min=proj)


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
    """EVERY NUMBER BELOW IS INJECTED. Nothing here reads /proc, the box, or a
    run directory."""
    ok = True
    print("proj_f17c --selftest: the halt path driven in BOTH directions, on INJECTED numbers only")

    p0 = project_core_min("coarse", [])
    ok &= check("first level projects from the frozen measured constant",
                "frozen" in p0["rate_basis"]
                and abs(p0["rate_us_per_cell_iteration"] - 0.6751) < 1e-12,
                "%.3f core-min" % p0["projected_core_min"])
    done = [dict(name="coarse", cell_iters=cell_iterations("coarse"), clock_s=66.0, ranks=1)]
    p1 = project_core_min("medium", done)
    r_meas = measured_rate_us(cell_iterations("coarse"), 66.0, 1)
    ok &= check("later level projects from THIS RUN's own completed level",
                "THIS RUN" in p1["rate_basis"]
                and abs(p1["rate_us_per_cell_iteration"] - r_meas * GROWTH["medium"]) < 1e-9,
                "measured %.4f -> projected rate %.4f core-us/cell-iteration"
                % (r_meas, p1["rate_us_per_cell_iteration"]))

    # THE FINDING, ASSERTED AS A PROPERTY OF THE FROZEN CONSTANTS: the rate is
    # NOT monotone, so one of the two growth ratios is below 1. A projector that
    # silently clamped growth at 1.0 -- the natural "growth is growth" reflex --
    # would over-project the fine level, and this control would catch it.
    ok &= check("the registered rate is NON-MONOTONE and GROWTH['fine'] < 1",
                GROWTH["medium"] > 1.0 and GROWTH["fine"] < 1.0,
                "GROWTH medium %.5f, fine %.5f" % (GROWTH["medium"], GROWTH["fine"]))
    clamped = cell_iterations("fine") * RATE_US_PER_CELL_ITER["medium"] / 1.0e6 / 60.0
    honest = project_core_min("fine", [])["projected_core_min"]
    ok &= check("clamping growth at 1.0 would over-project the fine level",
                clamped > honest, "%.1f vs %.1f core-min (%.1f %% high)"
                % (clamped, honest, 100.0 * (clamped / honest - 1.0)))

    # THE DEFECT THAT IS ABSENT, checked BEHAVIOURALLY and STRUCTURALLY -- never
    # by grepping this file's text, which quotes the defective form in its
    # docstring and would fail its own check for saying so.
    import ast as _ast
    import inspect as _inspect
    tree = _ast.parse(open(os.path.abspath(__file__)).read())
    body_max = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.FunctionDef) and node.name in (
                "project_core_min", "rate_for", "measured_rate_us", "decide", "cell_iterations"):
            body_max += [n.lineno for n in _ast.walk(node)
                         if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
                         and n.func.id in ("max", "min")]
    sig = list(_inspect.signature(project_core_min).parameters)
    exact = p1["cell_iterations"] * p1["rate_us_per_cell_iteration"] / 1.0e6 / 60.0
    ok &= check("no contention multiplier anywhere in the projection arithmetic",
                CONTENTION_MULTIPLIER == 1.0 and not body_max and sig == ["level", "completed"]
                and abs(p1["projected_core_min"] - exact) < 1e-12,
                "no max()/min() call node in any projection function; signature %s takes no "
                "box reading; projected == cell_iterations x rate exactly" % sig)
    ok &= check("the projection is a pure function of (level, completed)",
                project_core_min("fine", done)["projected_core_min"]
                == project_core_min("fine", done)["projected_core_min"])

    # THE HALT PATH, DRIVEN BOTH WAYS on injected spend/cap
    d_go, t_go = decide(10.0, 100.0, 375.0)
    d_halt, t_halt = decide(300.0, 100.0, 375.0)
    ok &= check("PROCEED when spent + projected <= cap", d_go == "PROCEED", "%.1f <= 375" % t_go)
    ok &= check("HALT when spent + projected > cap", d_halt == "HALT", "%.1f > 375" % t_halt)
    d_edge, _ = decide(275.0, 100.0, 375.0)
    ok &= check("the boundary spent + projected == cap PROCEEDS (the cap is inclusive)",
                d_edge == "PROCEED")
    d_over, _ = decide(275.0, 100.000001, 375.0)
    ok &= check("one microminute past the cap HALTS (the guard is not a rounding)",
                d_over == "HALT")

    # the CLI is the same code path: an injected run must exit 3, and 0
    import subprocess
    me = os.path.abspath(__file__)
    r = subprocess.run([sys.executable, me, "--level", "fine", "--spent", "300", "--cap", "375",
                        "--completed", json.dumps(done)], capture_output=True, text=True)
    ok &= check("the CLI exits 3 on a projected crossing", r.returncode == 3, r.stdout.strip()[-90:])
    r2 = subprocess.run([sys.executable, me, "--level", "coarse", "--spent", "0", "--cap", "375",
                         "--completed", "[]"], capture_output=True, text=True)
    ok &= check("the CLI exits 0 when the projection fits", r2.returncode == 0, r2.stdout.strip()[-90:])
    r3 = subprocess.run([sys.executable, "-O", me, "--selftest"], capture_output=True, text=True)
    ok &= check("refuses under python3 -O", r3.returncode == 2, r3.stderr.strip()[-70:])

    for args, why in (((cell_iterations("coarse"), -1.0, 1), "negative ClockTime"),
                      ((0, 1.0, 1), "zero cell-iterations")):
        try:
            measured_rate_us(*args)
            ok &= check("refuses %s" % why, False, "did not refuse")
        except Refusal:
            ok &= check("refuses %s" % why, True)
    try:
        rate_for("coarse", [dict(name="medium", cell_iters=1, clock_s=1.0, ranks=1)])
        ok &= check("refuses projecting BACKWARD along the ladder", False, "did not refuse")
    except Refusal:
        ok &= check("refuses projecting BACKWARD along the ladder", True)
    try:
        cell_iterations("enormous")
        ok &= check("refuses an unregistered level", False, "did not refuse")
    except Refusal:
        ok &= check("refuses an unregistered level", True)

    total, done2 = 0.0, []
    for nm in LEVEL_NAMES:
        p = project_core_min(nm, done2)
        total += p["projected_core_min"]
        done2.append(dict(name=nm, cell_iters=cell_iterations(nm),
                          clock_s=p["projected_core_min"] * 60.0, ranks=1))
        print("    %-7s %11d cell-iterations x %.4f core-us = %8.3f core-min"
              % (nm, p["cell_iterations"], p["rate_us_per_cell_iteration"], p["projected_core_min"]))
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
                         "[{name, cell_iters, clock_s, ranks}, ...]")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.level or a.spent is None or a.cap is None:
        sys.stderr.write("usage: proj_f17c.py --level <name> --spent <core_min> --cap <core_min> "
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
    print("%s level=%s cell_iterations=%d rate=%.4f core-us/cell-iteration projected=%.4f "
          "core-min spent=%.4f total=%.4f cap=%.4f contention=%.1f basis=%s"
          % (d, p["level"], p["cell_iterations"], p["rate_us_per_cell_iteration"],
             p["projected_core_min"], a.spent, total, a.cap, CONTENTION_MULTIPLIER, p["rate_basis"]))
    return 3 if d == "HALT" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        sys.exit(2)
