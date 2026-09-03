#!/usr/bin/env python3
"""Reduce an OpenFOAM solver log to the MAX-OVER-EQUATIONS initial residual, and
classify its trajectory at a deadline.

WHY THIS EXISTS.  Sanaa's ruling of 2026-09-03 ~20:00Z requires, fleet-wide and for
all solver modes including detached runs: "at deadline, classify the
max-over-equations residual as descending / plateaued-or-oscillating / diverging;
extend bounded and booked, stop gracefully as 'non-convergent, reported not gated,'
or kill, respectively. Sidecar attached to the log, not the process."  Her 2026-09-03
~20:00Z physics taxonomy names "a residual print that isn't the max over equations"
as a BLOCKING PHYSICS FIX.

MEASURED GAP THIS CLOSES (cfd lane, 2026-09-03).  OpenFOAM never prints a single
max-over-equations number -- it prints one line per equation per solve.  The reduction
must therefore live in the monitor, and no monitor on this box performed it: a sweep of
scripts/, sdk/ and verification/runs/ for a max-over-equations reducer returned exactly
one hit, sdk/workflows/mega_batch.py:669, which is Ahmed-body specific AND reduces the
FINAL residual.  scripts/check_convergence.py documents final-residual reading as its
own failure mode 4: OpenFOAM's residualControl is checked against the INITIAL column.
This file reduces the INITIAL column.

THE SUBTLETY THAT MAKES THIS NON-TRIVIAL, AND IT IS NOT COSMETIC.  Within one time step
a field is solved more than once -- p under nCorrectors, and again under each
nNonOrthogonalCorrector.  Only the FIRST solve of a field in a time step carries that
step's initial residual; the later ones start from an already-corrected field and are
smaller by construction.  Taking the last, or taking a mean, understates convergence and
does so MORE on exactly the meshes that need most correctors -- which is to say, on a
high-non-orthogonality mesh like ONERA M6.  This reducer takes the FIRST initial
residual per field per time step, then the max over fields.

NO BARE `assert` ANYWHERE IN THIS FILE (L-332).  `python3 -O` deletes every assert, so a
guard written as one is a guard the runner can switch off without knowing.  Every
refusal here is an explicit `raise` or `sys.exit`.

DETACHED RUNS.  This reads a LOG FILE and nothing else.  It never needs the solver's pid,
never signals a process, and works on a run started by the queue daemon in another
session or after this agent is gone.  The sidecar is written beside the log.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile

# --- the fleet-wide default values.  Sanaa 2000Z: "Same values everywhere unless a
# --- team states why its solver needs different ones."  A team that overrides one
# --- must say so; the sidecar records both the value used and whether it is a default.
DEFAULTS = {
    # window over which the trajectory is judged, in SOLVER ITERATIONS -- never in
    # printed samples. A log written at printInterval 100 yields one sample per 100
    # iterations, so a window expressed in samples would mean a different amount of
    # physics on every case, and the classification would depend on a print setting.
    # The observed print interval is measured from consecutive `Time =` values and the
    # window is converted; both are recorded in the sidecar. 1,000 iterations matches
    # the plateau clause drafted at RUNG1_M6_PREREGISTRATION section 4.1 G2b.
    "window_iterations": 1000,
    # fewest PRINTED SAMPLES inside the window before any classification is offered
    "min_samples": 10,
    # DESCENDING if the window falls by at least this many decades
    "descend_decades": 0.10,
    # DIVERGING if the window RISES by at least this many decades
    "diverge_decades": 0.50,
    # DIVERGING immediately on a non-finite residual, whatever the trend
    "nonfinite_is_divergent": True,
}

RE_TIME = re.compile(r"^Time = ([0-9.eE+-]+)\s*$", re.M)

# TWO PRINT FORMS ARE IN CIRCULATION ON THIS BOX AND A READER THAT KNOWS ONE SEES
# NOTHING IN THE OTHER.  This is the L-459 shape in a new place, and it was found the
# only way it can be found: by pointing this reducer at a real production log and
# getting ABSENT instead of a number.
#
#   FORM A, stock OpenFOAM solvers (simpleFoam, rhoSimpleFoam, ...):
#     smoothSolver:  Solving for Ux, Initial residual = 0.0123, Final residual = 1e-9, No Iterations 4
#   FORM B, DAFoam drivers (DARhoSimpleCFoam, ...):
#     U0 initRes: 2.06074576919884e-07 finalRes: 2.007944497583799e-08 nIters: 2
#     -- measured at /home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log,
#        which contains ZERO occurrences of the string "Initial residual".
#
# Both are matched, and a planted control below REQUIRES the reducer to read a real
# log of each form before any number it prints is treated as evidence.
_NUM = r"([0-9.eE+-]+|nan|inf|-nan|-inf)"
RE_SOLVE_A = re.compile(
    r"Solving for ([A-Za-z_][A-Za-z0-9_.]*),\s*Initial residual\s*=\s*" + _NUM, re.I)
RE_SOLVE_B = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s+initRes:\s*" + _NUM, re.I)
SOLVE_FORMS = (("A_stock_openfoam", RE_SOLVE_A), ("B_dafoam", RE_SOLVE_B))

DESCENDING = "descending"
PLATEAU = "plateaued-or-oscillating"
DIVERGING = "diverging"

ACTION = {
    DESCENDING: "extend bounded and booked",
    PLATEAU: "stop gracefully -- non-convergent, reported not gated",
    DIVERGING: "kill",
}


class ReducerError(Exception):
    """Explicit refusal. Never an assert (L-332)."""


def _f(tok: str):
    try:
        v = float(tok)
    except ValueError:
        return math.nan
    return v


def reduce_log(text: str, exclude=()):
    """-> (steps, print_forms_seen).

    steps: list of {step, time, max_initial_residual, carried_by, per_field}.
    The FIRST initial residual per field per time step is the one kept.
    print_forms_seen: which of the two circulating print forms actually matched, so a
    caller can tell "no residuals in this log" from "residuals this reader cannot see".
    """
    excl = {e.lower() for e in exclude}
    steps = []
    cur = None
    forms_seen = set()

    def close():
        if cur is None or not cur["per_field"]:
            return
        vals = cur["per_field"]
        # a non-finite value dominates: it IS the max, and it is reported as such
        nf = [k for k, v in vals.items() if not math.isfinite(v)]
        if nf:
            cur["max_initial_residual"] = math.inf
            cur["carried_by"] = sorted(nf)[0]
            cur["nonfinite_fields"] = sorted(nf)
        else:
            k = max(vals, key=lambda kk: vals[kk])
            cur["max_initial_residual"] = vals[k]
            cur["carried_by"] = k
        steps.append(cur)

    for line in text.splitlines():
        mt = RE_TIME.match(line)
        if mt:
            close()
            cur = {"step": len(steps) + 1, "time": mt.group(1),
                   "per_field": {}, "max_initial_residual": None,
                   "carried_by": None}
            continue
        for fname, rx in SOLVE_FORMS:
            ms = rx.search(line)
            if not ms or cur is None:
                continue
            forms_seen.add(fname)
            fld = ms.group(1)
            if fld.lower() in excl:
                break
            # FIRST solve of this field in this step wins; later correctors are ignored
            if fld not in cur["per_field"]:
                cur["per_field"][fld] = _f(ms.group(2))
            break
    close()
    return steps, sorted(forms_seen)


def classify(series, cfg, print_interval=1.0):
    """series: floats (max-over-equations) in time-step order.
    print_interval: iterations between consecutive printed samples, MEASURED."""
    pi = print_interval if print_interval and print_interval > 0 else 1.0
    n_win = max(2, int(math.ceil(float(cfg["window_iterations"]) / pi)))
    win = series[-n_win:] if len(series) > n_win else list(series)
    out = {
        "window_iterations_requested": float(cfg["window_iterations"]),
        "print_interval_iterations_MEASURED": pi,
        "window_samples_implied": n_win,
        "window_iterations_actually_spanned": (len(win) - 1) * pi,
        "window_used": len(win),
        "min_samples": int(cfg["min_samples"]),
        "first_in_window": win[0] if win else None,
        "last_in_window": win[-1] if win else None,
    }
    if len(win) < int(cfg["min_samples"]):
        out["classification"] = None
        out["action"] = None
        out["reason"] = (f"{len(win)} samples in window; "
                         f"{cfg['min_samples']} are needed before any classification "
                         f"is offered. NOT a plateau, NOT a pass -- undetermined.")
        return out
    if cfg["nonfinite_is_divergent"] and any(not math.isfinite(v) for v in win):
        out["classification"] = DIVERGING
        out["action"] = ACTION[DIVERGING]
        out["reason"] = "a non-finite max-over-equations residual is in the window"
        out["decades"] = None
        return out
    if any(v <= 0 for v in win):
        out["classification"] = None
        out["action"] = None
        out["reason"] = ("a non-positive residual is in the window; log10 is undefined "
                         "and no trend is claimed")
        return out
    decades = math.log10(win[0]) - math.log10(win[-1])   # >0 means it FELL
    out["decades_fallen_over_window"] = decades
    # oscillation is reported whatever the class -- it is information, not a verdict
    signs = [1 if b > a else (-1 if b < a else 0)
             for a, b in zip(win, win[1:])]
    flips = sum(1 for a, b in zip(signs, signs[1:]) if a and b and a != b)
    out["direction_changes_in_window"] = flips
    out["oscillation_fraction"] = flips / max(1, len(signs) - 1)
    if decades <= -float(cfg["diverge_decades"]):
        out["classification"] = DIVERGING
        out["action"] = ACTION[DIVERGING]
        out["reason"] = (f"rose {-decades:.3f} decades over the window, at or beyond "
                         f"the {cfg['diverge_decades']} decade divergence threshold")
    elif decades >= float(cfg["descend_decades"]):
        out["classification"] = DESCENDING
        out["action"] = ACTION[DESCENDING]
        out["reason"] = (f"fell {decades:.3f} decades over the window, at or beyond "
                         f"the {cfg['descend_decades']} decade descent threshold")
    else:
        out["classification"] = PLATEAU
        out["action"] = ACTION[PLATEAU]
        out["reason"] = (f"moved {decades:+.3f} decades over the window, inside "
                         f"[-{cfg['diverge_decades']}, {cfg['descend_decades']}) -- "
                         f"neither descending nor diverging")
    return out


# ---------------------------------------------------------------- planted controls
_CTRL_LOG = """\
Starting time loop

Time = 1

DILUPBiCGStab:  Solving for Ux, Initial residual = 1e-01, Final residual = 1e-09, No Iterations 4
DILUPBiCGStab:  Solving for Uy, Initial residual = 5e-01, Final residual = 1e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 2e-01, Final residual = 1e-07, No Iterations 8
GAMG:  Solving for p, Initial residual = 9e-09, Final residual = 1e-11, No Iterations 2
ExecutionTime = 1 s

Time = 2

DILUPBiCGStab:  Solving for Ux, Initial residual = 8e-01, Final residual = 1e-09, No Iterations 4
DILUPBiCGStab:  Solving for Uy, Initial residual = 3e-01, Final residual = 1e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 1e-01, Final residual = 1e-07, No Iterations 8
ExecutionTime = 2 s
"""


def controls():
    """Prove the reducer can see a non-zero, can see the RIGHT one, and can say
    something other than the answer we would like. Returns (ok, report)."""
    rep = {}

    # C1 -- the max must MOVE BETWEEN FIELDS. Step 1's max is Uy (0.5); step 2's is
    # Ux (0.8). A reducer that tracks one field, or takes the last line, gets both
    # wrong. A reducer that cannot see a non-zero here cannot be trusted on a zero.
    st, _ = reduce_log(_CTRL_LOG)
    got = [(s["max_initial_residual"], s["carried_by"]) for s in st]
    want = [(0.5, "Uy"), (0.8, "Ux")]
    rep["C1_max_moves_between_fields"] = {
        "expected": want, "got": got, "fired": got == want}

    # C2 -- the FIRST p solve (2e-01) must win over the corrector solve (9e-09).
    # Taking the corrector would report 2e-01 -> the step max would still be Uy, so
    # C1 alone cannot catch it; this control reads the per-field value directly.
    p1 = st[0]["per_field"].get("p")
    rep["C2_first_solve_per_step_wins"] = {
        "p_first_solve": 2e-01, "p_corrector_solve": 9e-09,
        "value_kept": p1, "fired": p1 == 2e-01}

    # C3 -- the classifier must be able to return EACH of the three classes. A
    # classifier that can only say one thing is not evidence for the thing it says.
    cfg = dict(DEFAULTS)
    cfg["min_samples"] = 10
    cfg["window_iterations"] = 100
    falling = [10.0 ** (-i / 20.0) for i in range(100)]
    rising = [10.0 ** (i / 20.0) for i in range(100)]
    flat = [1.0 + 0.001 * ((-1) ** i) for i in range(100)]
    seen = {classify(falling, cfg)["classification"],
            classify(rising, cfg)["classification"],
            classify(flat, cfg)["classification"]}
    rep["C3_all_three_classes_reachable"] = {
        "falling": classify(falling, cfg)["classification"],
        "rising": classify(rising, cfg)["classification"],
        "flat": classify(flat, cfg)["classification"],
        "fired": seen == {DESCENDING, DIVERGING, PLATEAU}}

    # C4 -- a non-finite residual must be seen, not silently coerced.
    nanlog = _CTRL_LOG.replace("Initial residual = 8e-01",
                              "Initial residual = nan")
    st2, _ = reduce_log(nanlog)
    rep["C4_nonfinite_is_seen"] = {
        "nonfinite_fields_in_step_2": st2[1].get("nonfinite_fields"),
        "fired": st2[1].get("nonfinite_fields") == ["Ux"]}

    # C5 -- BOTH PRINT FORMS. The stock-OpenFOAM form and the DAFoam form must each
    # yield the same reduction from logically identical content. This control exists
    # because the reducer, pointed at a REAL DAFoam log, returned ABSENT: that log
    # contains zero occurrences of "Initial residual". A reducer that knows one form
    # reports nothing on the other and, without this control, would report that
    # nothing as a clean read.
    ctrl_b = ("Time = 1\n"
              "Ux initRes: 1e-01 finalRes: 1e-09 nIters: 4\n"
              "Uy initRes: 5e-01 finalRes: 1e-09 nIters: 4\n"
              "p initRes: 2e-01 finalRes: 1e-07 nIters: 8\n"
              "p initRes: 9e-09 finalRes: 1e-11 nIters: 2\n"
              "Time = 2\n"
              "Ux initRes: 8e-01 finalRes: 1e-09 nIters: 4\n"
              "Uy initRes: 3e-01 finalRes: 1e-09 nIters: 4\n"
              "p initRes: 1e-01 finalRes: 1e-07 nIters: 8\n")
    stb, formsb = reduce_log(ctrl_b)
    sta, formsa = reduce_log(_CTRL_LOG)
    gb = [(s["max_initial_residual"], s["carried_by"]) for s in stb]
    ga = [(s["max_initial_residual"], s["carried_by"]) for s in sta]
    rep["C5_both_print_forms_read"] = {
        "form_A_stock_openfoam": {"forms_detected": formsa, "reduction": ga},
        "form_B_dafoam": {"forms_detected": formsb, "reduction": gb},
        "reductions_agree": ga == gb,
        "fired": (formsa == ["A_stock_openfoam"] and formsb == ["B_dafoam"]
                  and ga == gb == want)}

    return all(c["fired"] for c in rep.values()), rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("log", nargs="?", help="OpenFOAM solver log to reduce")
    ap.add_argument("--sidecar", help="output path (default: <log>.residual_sidecar.json)")
    ap.add_argument("--exclude", default="", help="comma-separated fields to ignore")
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted controls and exit")
    for k, v in DEFAULTS.items():
        if isinstance(v, bool):
            continue
        ap.add_argument(f"--{k.replace('_', '-')}", type=type(v), default=None)
    a = ap.parse_args()

    ok, rep = controls()
    if a.selftest:
        print(json.dumps({"controls": rep, "all_fired": ok}, indent=2, sort_keys=True))
        sys.exit(0 if ok else 2)
    if not ok:
        print(json.dumps({"REFUSED": "a planted control did not fire; no number this "
                                     "reducer prints is evidence",
                          "controls": rep}, indent=2, sort_keys=True))
        sys.exit(2)
    if not a.log:
        raise SystemExit("usage: residual_max_over_equations.py <solver.log> "
                         "[--sidecar PATH] [--selftest]")
    if not os.path.exists(a.log):
        raise SystemExit(f"ABSENT: {a.log} -- an absent solver log reads ABSENT, "
                         f"never converged, never clean.")

    cfg = dict(DEFAULTS)
    overridden = []
    for k in DEFAULTS:
        v = getattr(a, k, None)
        if v is not None and not isinstance(DEFAULTS[k], bool):
            if v != DEFAULTS[k]:
                overridden.append(k)
            cfg[k] = v

    with open(a.log, errors="replace") as f:
        text = f.read()
    steps, forms = reduce_log(text, [x for x in a.exclude.split(",") if x])
    if not steps:
        raise SystemExit(f"NO SOLVE LINES FOUND in {a.log}. The reducer read the file "
                         f"and saw no 'Solving for <field>, Initial residual =' line. "
                         f"in EITHER known print form (stock OpenFOAM "
                         f"'Solving for X, Initial residual =' or DAFoam 'X initRes:'). "
                         f"That is ABSENT, not converged, not clean.")
    series = [s["max_initial_residual"] for s in steps]
    # MEASURE the print interval rather than reading controlDict: the log is the only
    # artifact we are guaranteed to have for a detached run, and a controlDict on disk
    # can post-date the run (measured trap, RUNG1_M6_PREREGISTRATION section 8).
    tvals = []
    for st in steps:
        try:
            tvals.append(float(st["time"]))
        except (TypeError, ValueError):
            pass
    deltas = sorted(b - a for a, b in zip(tvals, tvals[1:]) if b > a)
    print_interval = deltas[len(deltas) // 2] if deltas else 1.0
    cls = classify(series, cfg, print_interval)

    side = a.sidecar or (a.log + ".residual_sidecar.json")
    out = {
        "instrument": os.path.abspath(__file__),
        "attached_to_the_LOG_not_the_process": True,
        "log": os.path.abspath(a.log),
        "log_bytes": os.path.getsize(a.log),
        "reduction": "MAX OVER EQUATIONS of the INITIAL residual; FIRST solve of each "
                     "field in each time step (correctors ignored)",
        "why_initial_not_final": "OpenFOAM's residualControl is checked against the "
                                 "INITIAL column; scripts/check_convergence.py "
                                 "documents final-residual reading as its failure mode 4",
        "print_form_detected": forms,
        "print_interval_iterations_MEASURED_from_Time_lines": print_interval,
        "time_steps_read": len(steps),
        "time_steps_are_PRINT_INTERVALS_not_necessarily_iterations": True,
        "fields_seen": sorted({k for s in steps for k in s["per_field"]}),
        "first_step": {"time": steps[0]["time"],
                       "max_initial_residual": steps[0]["max_initial_residual"],
                       "carried_by": steps[0]["carried_by"]},
        "last_step": {"time": steps[-1]["time"],
                      "max_initial_residual": steps[-1]["max_initial_residual"],
                      "carried_by": steps[-1]["carried_by"]},
        "thresholds_used": cfg,
        "thresholds_are_fleet_defaults": not overridden,
        "thresholds_overridden": overridden,
        "at_deadline": cls,
        "planted_controls": rep,
        "controls_all_fired": ok,
        "THIS_IS_NOT_A_VERDICT": "This sidecar carries no verdict of the fixed "
                                 "vocabulary. It classifies a residual trajectory so "
                                 "the monitor can act; the frozen grader judges the run.",
    }
    with open(side, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"WROTE {side}")
    print(f"  steps={len(steps)}  fields={out['fields_seen']}")
    print(f"  max-over-equations: first={series[0]:.6g} last={series[-1]:.6g} "
          f"(carried by {steps[-1]['carried_by']})")
    print(f"  at deadline: {cls.get('classification')} -> {cls.get('action')}")
    print(f"  reason: {cls.get('reason')}")


if __name__ == "__main__":
    main()
