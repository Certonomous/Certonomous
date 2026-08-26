#!/usr/bin/env python3
"""
F3 SUCCESSOR -- THE INSTRUMENTED RUNNER. Steadiness is MEASURED, not assumed.

WHY THIS FILE EXISTS
--------------------
cfd-supervisor ruled limb (a) on 2026-08-26: re-author the runners so a real
time series of THE GRADED QUANTITY exists, and grade steadiness from it. This is
lawful because the successor is a NEW pre-registration before its first compute;
F3's `postProcess -latestTime` is F3's and does not bind it.

THE SENTENCE THE NEXT DRAFTER MUST NOT GET WRONG, put here on the supervisor's
instruction so it cannot be reached past:

    STEADINESS FOR A DENSITY-BASED EXPLICIT TIME-MARCHER IS DRIFT IN THE GRADED
    QUANTITY OVER A SUSTAINED WINDOW, NEVER A RESIDUAL.

Measured, not argued: `rhoCentralFoam` runs the `diagonal` solver, which solves
each step EXACTLY. All 8,071 `Time =` blocks in F3's wedge/M3.0_th15/fine log
report `Initial residual = 0, Final residual = 0, No Iterations 0` for rho, rhoUx,
rhoUy and rhoE. A residual gate here is a gate quantity that CAN NEVER BE
NON-ZERO -- the class that has now bitten VMFL059 and F12's P4.

INSTRUMENTATION IS AN OBSERVATION, NOT AN INTERVENTION -- AND THIS FILE PROVES IT
--------------------------------------------------------------------------------
Three guarantees, in increasing strength:

1. **ADDITIVE ONLY.** Not one key the frozen generator wrote is modified. No
   `writeInterval`, no `purgeWrite`, no `writeControl`, no `deltaT`, no `maxCo`.
   The series comes from function objects APPENDED in a new `functions` block.
   `assert_controldict_additive()` refuses unless the diff is exactly that.
2. **timeStep-BASED OUTPUT, NEVER `adjustableRunTime`.** `adjustTimeStep` is
   `yes` on these cases, so an `adjustableRunTime` output control would CLIP
   STEPS ONTO WRITE TIMES AND CHANGE THE TRAJECTORY. Every appended function
   object uses `writeControl timeStep`, which cannot touch deltaT, and
   `refuse_clipping_output()` refuses if the string `adjustableRunTime` appears
   anywhere in the written controlDict.
3. **BIT-IDENTITY, TWO-ARMED.** See `bitcheck` below. This is the control that
   actually settles it, and one arm is not enough.

THE GRADED PATH IS NOT TOUCHED. `p_wall_mean`, `beta` and `cd` are produced by
the same code as F3's runners, at the same final time, from the same artifacts.
The series is a SECOND, ADDITIVE read. If the series machinery were deleted, the
graded numbers would be unchanged.

REFUSAL DISCIPLINE: `raise`/`sys.exit(2)` only. NO `assert` carries a refusal,
a guard, a control or a gate anywhere in this file (L-332) -- `python3 -O`
deletes every `assert`, and this file is DRIVEN under `-O` and REQUIRED to
refuse. An AST check requiring zero `Assert` nodes runs as a launch precondition.
NOTE: the frozen generators DO carry assert-guards (`make_wedge_case.py:47`,
`make_diamond_case.py:58`) -- build guards, deleted by `-O`, producing wrong
INPUTS silently. `check_generator_guards()` below drives them under `-O` and
refuses, because a build guard that vanishes is the case for re-registration.
"""
import os
import re
import sys
import ast
import glob
import json
import math
import time
import shutil
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
F3_ROOT = os.path.dirname(HERE)
sys.path.insert(0, F3_ROOT)

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---------------------------------------------------------------------------
# REGISTERED CLASS C CONSTANTS -- fixed HERE, before any run exists, so that the
# question "can the runs meet them?" is answered by the runs and not by the
# constants. Element 4 in particular is registered as a NUMBER before anybody
# knows whether it can be filled.
# ---------------------------------------------------------------------------
WINDOW_FRACTION = 0.25      # element 1: the sustained window is the final 25% of endTime
MIN_WINDOW_SAMPLES = 30     # element 4: below this the row REFUSES. It does not degrade.
DRIFT_TOL_FRAC = {          # elements 2 and 3, as a FRACTION of the graded value
    # Derived from the pre-registered band, one order of magnitude beneath it:
    # a value cannot be claimed inside a +-X% band while still moving by more
    # than X/10 % across the window it is claimed on. Fixed before any in-scope
    # value was read. NOT derived from any measured deviation.
    "p_wall_mean": 0.0005,      # band +-0.5%  -> 0.05%
    "beta_deg":    0.0020,      # band +-2.0%  -> 0.20%
    "cd":          0.0010,      # band +-1.0%  -> 0.10%
}
# Output cadence, in SOLVER STEPS (never runTime, never adjustableRunTime).
# CHOSEN FROM MEASURED STEP COUNTS, not guessed. Counting `Time = ` blocks in
# every F3 conversion log gives a WORST level of 3,919 steps (wedge coarse), so
# the final 25% window holds ~979 steps at the least-resolved level this rung
# will run. At N = 20 that is ~49 window samples against the MIN_WINDOW_SAMPLES
# floor of 30 -- a 1.6x margin AT THE BINDING LEVEL, not at the comfortable one.
# The fine levels give ~100 (wedge 8,056 steps; diamond 9,129).
# The window boundary comparison is STRICT (`t >= t_start`, no epsilon): adding
# a tolerance to a gate boundary is a fitted threshold, and with a 1.6x margin a
# one-sample floating-point boundary effect cannot move any verdict.
SERIES_EVERY_N_STEPS = 20
MEASURED_STEP_COUNTS = {          # `grep -cE "^Time = " log.rhoCentralFoam`
    "wedge/M2.0_th15/coarse": 3919, "wedge/M2.0_th15/medium": 4040,
    "wedge/M2.0_th15/fine": 8056,   "wedge/M3.0_th15/fine": 8071,
    "diamond/M2.0_eps7p125/coarse": 6019, "diamond/M2.0_eps7p125/medium": 6019,
    "diamond/M2.0_eps7p125/fine": 9129,
    "cone/M2.35_th10/coarse": 4431, "cone/M2.35_th10/medium": 8841,
    "cone/M2.35_th10/fine": 17663,
}


class Refusal(Exception):
    pass


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def guard_fresh_case_dir(case_dir):
    """Rule 4's age guard dates a run from its own 0/. A pre-existing tree
    defeats it, so this refuses BEFORE any generator runs."""
    if os.path.exists(case_dir):
        entries = sorted(os.listdir(case_dir))
        if entries:
            refuse("case directory already exists and is NOT EMPTY: %s\n"
                   "  contains: %s\n"
                   "  The age guard dates a run from its own 0/T; a pre-existing "
                   "tree defeats it. Refusing before the generator runs."
                   % (case_dir, ", ".join(entries[:12])))
    parent_stale = [p for p in (os.path.join(case_dir, "0"),
                                os.path.join(case_dir, "constant"),
                                os.path.join(case_dir, "system"))
                    if os.path.exists(p)]
    if parent_stale:
        refuse("pre-existing case structure: %s" % ", ".join(parent_stale))
    return True


def numeric_time_dirs(case_dir):
    """Time directories in NUMERIC order.

    F3's runners use `sorted(glob.glob(...))[-1]` -- a LEXICOGRAPHIC sort
    (`run_wedge_case.py:94`, `:131`). With one sampled time that is harmless and
    it was never wrong for F3. The moment there is more than one -- which is
    exactly what this rung creates -- "9.0" sorts after "10.0" and the LATEST
    time is silently the WRONG one. Re-authored here rather than inherited.
    """
    out = []
    for d in os.listdir(case_dir):
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and os.path.isdir(os.path.join(case_dir, d)):
            out.append((float(d), d))
    out.sort(key=lambda t: t[0])
    return [name for _, name in out]


def read_controldict_keys(case_dir):
    """Read the WRITTEN controlDict and return the keys that decide whether
    output can perturb the trajectory. Quoted into the record; never assumed."""
    p = os.path.join(case_dir, "system", "controlDict")
    if not os.path.exists(p):
        refuse("no controlDict written at %s" % p)
    txt = open(p).read()
    keys = {}
    for k in ("application", "adjustTimeStep", "writeControl", "writeInterval",
              "purgeWrite", "deltaT", "endTime", "maxCo", "maxDeltaT",
              "runTimeModifiable", "timePrecision"):
        m = re.search(r"^\s*%s\s+([^;]+);" % re.escape(k), txt, re.M)
        keys[k] = m.group(1).strip() if m else None
    return keys, txt


def refuse_clipping_output(case_dir):
    """`adjustableRunTime` CLIPS deltaT ONTO WRITE TIMES. With adjustTimeStep on,
    that changes the time-step sequence and therefore the trajectory -- the
    instrumentation would no longer be an observation. Refuse it outright.

    MEASURED on F3's own output that `runTime`/`writeTime` do NOT clip here:
    the wedge requested writes at endTime/3 = 0.866667 with endTime 2.600000 and
    WROTE at 1.733263 and 2.5999683 -- off the requested values by 7.1e-5 and
    3.17e-5. A clipping control would have landed on them exactly. The diamond
    likewise wrote forces at 1.999939 / 4.0002418 / 5.99989277 against an
    interval of 2.0 and endTime 6.0. Non-clipping, from disk, not from doctrine.
    """
    keys, txt = read_controldict_keys(case_dir)
    if "adjustableRunTime" in txt:
        refuse("controlDict contains `adjustableRunTime`, which clips time steps "
               "onto write times and CHANGES THE TRAJECTORY. This rung's output "
               "must be timeStep-based. %s" % os.path.join(case_dir, "system", "controlDict"))
    if keys["adjustTimeStep"] not in ("no", "yes"):
        refuse("controlDict does not state adjustTimeStep; cannot establish "
               "whether output control can perturb the step sequence")
    return keys


FUNCTIONS_MARKER = "// ---- SUCCESSOR SERIES INSTRUMENTATION (ADDITIVE) ----"


def assert_controldict_additive(before_txt, case_dir):
    """The instrumentation must ADD a functions block and change NOTHING ELSE.
    Compared line by line, not by eyeball."""
    _, after_txt = read_controldict_keys(case_dir)
    before_lines = before_txt.rstrip("\n").split("\n")
    after_lines = after_txt.rstrip("\n").split("\n")
    if after_lines[:len(before_lines)] != before_lines:
        for i, (a, b) in enumerate(zip(before_lines, after_lines)):
            if a != b:
                refuse("instrumentation MODIFIED a line the generator wrote "
                       "(line %d):\n  frozen: %r\n  now:    %r\n"
                       "This rung's instrumentation must be additive only."
                       % (i + 1, a, b))
        refuse("the written controlDict is not a prefix-preserving extension of "
               "the generator's output")
    added = after_lines[len(before_lines):]
    if not any(FUNCTIONS_MARKER in l for l in added):
        refuse("the appended block does not carry the instrumentation marker; "
               "cannot confirm what was added")
    if "adjustableRunTime" in "\n".join(added):
        refuse("the APPENDED block uses adjustableRunTime")
    return dict(lines_before=len(before_lines), lines_added=len(added),
                added_block="\n".join(added))


def check_generator_guards():
    """The frozen generators carry BUILD GUARDS AS `assert` -- deleted by
    `python3 -O`, producing a wrong MESH silently. Drive them under -O and
    require a refusal. A build guard that vanishes under a flag is not a guard,
    and a wrong input is cured by re-registration, not by patching a fired file.
    """
    probe = (
        "import sys; sys.path.insert(0, %r)\n"
        "import make_wedge_case as m\n"
        "m.RES['bad'] = (30, 20, 60, 21)\n"          # ny != ny2 -> the guard must fire
        "import tempfile, os\n"
        "d = tempfile.mkdtemp()\n"
        "try:\n"
        "    m.make_case(os.path.join(d, 'c'), 2.5, 10.0, 'bad', 31.85)\n"
        "    print('GUARD_DID_NOT_FIRE')\n"
        "except AssertionError:\n"
        "    print('GUARD_FIRED')\n"
        "except Exception as e:\n"
        "    print('GUARD_OTHER:' + type(e).__name__)\n"
    ) % F3_ROOT
    out = {}
    for flag in ([], ["-O"]):
        p = subprocess.run([sys.executable] + flag + ["-c", probe],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out["python3 " + (" ".join(flag) or "(no flag)")] = p.stdout.decode().strip()
    return out


def ast_no_asserts(paths):
    """Zero `Assert` nodes in this rung's own path. A launch precondition."""
    bad = {}
    for p in paths:
        try:
            tree = ast.parse(open(p).read())
        except Exception as e:
            refuse("cannot parse %s for the assert census: %s" % (p, e))
        lines = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's path, and `python3 -O` "
               "deletes every one of them (L-332): %s" % json.dumps(bad))
    return dict(files_checked=len(paths), assert_nodes=0)


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------

def sh(cmd, cwd, logfile=None):
    full = "source %s >/dev/null 2>&1; %s" % (FOAM_BASHRC, cmd)
    t0 = time.time()
    p = subprocess.run(["bash", "-c", full], cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    if logfile:
        with open(logfile, "wb") as f:
            f.write(p.stdout)
    if p.returncode != 0:
        refuse("command failed (%s) rc=%d; see %s" % (cmd, p.returncode, logfile))
    return dt


# ---------------------------------------------------------------------------
# Iterative-convergence state -- a REAL check that CAN fail
# ---------------------------------------------------------------------------

SOLVE_RE = re.compile(
    r"^(\w+):\s+Solving for (\w+), Initial residual = ([0-9.eE+-]+), "
    r"Final residual = ([0-9.eE+-]+), No Iterations (\d+)", re.M)


def iterative_state_from_log(log_path):
    """`diagonal` solves the step EXACTLY: the linear system is solved directly,
    so per-step linear convergence holds BY CONSTRUCTION and the residual is
    identically zero. That is the basis for CONVERGED here -- a solver-class
    fact, NOT a tolerance test on a number that cannot move.

    THIS IS STILL A REAL CHECK. If fvSolution is ever changed to an iterative
    solver, the lines stop reading `diagonal` with zero final residual and this
    function falls through to a genuine tolerance test that can return
    NOT_CONVERGED. It is not a rubber stamp.
    """
    if not os.path.exists(log_path):
        refuse("solver log missing, cannot establish iterative state: %s" % log_path)
    txt = open(log_path, errors="replace").read()
    rows = SOLVE_RE.findall(txt)
    if not rows:
        refuse("no solver lines parsed from %s; the iterative-convergence state "
               "cannot be established and an unestablished state is not a "
               "converged one" % log_path)
    solvers = set(r[0] for r in rows)
    finals = [float(r[3]) for r in rows]
    iters = [int(r[4]) for r in rows]
    n_blocks = len(re.findall(r"^Time = ", txt, re.M))
    if solvers == {"diagonal"} and max(finals) == 0.0 and max(iters) == 0:
        return "CONVERGED", dict(
            basis="diagonal (DIRECT) solver: every step solved exactly; final "
                  "residual identically zero by construction, NOT by tolerance",
            solvers=sorted(solvers), solve_lines=len(rows), time_blocks=n_blocks,
            max_final_residual=0.0, max_iterations=0)
    worst = max(finals)
    state = "CONVERGED" if worst < 1e-6 else "NOT_CONVERGED"
    return state, dict(
        basis="iterative solver detected; tolerance test applied",
        solvers=sorted(solvers), solve_lines=len(rows), time_blocks=n_blocks,
        max_final_residual=worst, max_iterations=max(iters), tolerance=1e-6)


# ---------------------------------------------------------------------------
# CLASS C plateau test -- all four elements, element 4 LIVE
# ---------------------------------------------------------------------------

def plateau_state(times, values, quantity, end_time):
    """Class C, in the shape this team ruled on 2026-08-25.

    1. sustained window floor -- the final WINDOW_FRACTION of physical time
    2. trend fit that REJECTS a growing series
    3. explicit stationarity test able to report NOT stationary
    4. REFUSAL below MIN_WINDOW_SAMPLES -- registered as a number before any run
       existed, and NOT waived. Dropping element 4 always makes a run gradeable,
       which is exactly why it is the one that gets dropped.

    Returns (state, detail). `state` is "PLATEAUED" or "NOT_PLATEAUED".
    A window too short to judge is a REFUSAL, never a PLATEAUED.
    """
    t = np.asarray(times, dtype=float)
    v = np.asarray(values, dtype=float)
    if t.size != v.size:
        refuse("%s: series length mismatch (%d times, %d values)" % (quantity, t.size, v.size))
    order = np.argsort(t)
    t, v = t[order], v[order]

    t_start = end_time * (1.0 - WINDOW_FRACTION)
    win = t >= t_start
    n_win = int(win.sum())

    detail = dict(quantity=quantity, n_total=int(t.size), n_window=n_win,
                  window_from=float(t_start), window_to=float(end_time),
                  window_fraction=WINDOW_FRACTION,
                  min_window_samples=MIN_WINDOW_SAMPLES)

    # ---- element 4, FIRST, because it decides whether the rest may run ----
    if n_win < MIN_WINDOW_SAMPLES:
        refuse("%s: SUSTAINED WINDOW CANNOT BE FILLED -- %d samples in the final "
               "%.0f%% of the run, minimum %d. Element 4 of the Class C gate "
               "REFUSES. It does NOT degrade to a band-only PASS, and it does "
               "not borrow the last reading as a plateau. ONE READING IS NOT "
               "EVIDENCE OF CONVERGENCE."
               % (quantity, n_win, 100 * WINDOW_FRACTION, MIN_WINDOW_SAMPLES))

    tw, vw = t[win], v[win]
    ref = abs(float(vw[-1]))
    if ref == 0.0:
        refuse("%s: the graded value is exactly zero at the final time; a "
               "relative drift test has no scale and this reader has not been "
               "shown able to see a non-zero" % quantity)
    tol = DRIFT_TOL_FRAC[quantity]

    # ---- element 2: trend fit, and it must REJECT a growing series ----
    A = np.vstack([tw, np.ones_like(tw)]).T
    slope, icept = np.linalg.lstsq(A, vw, rcond=None)[0]
    span = float(tw[-1] - tw[0])
    drift_frac = abs(float(slope) * span) / ref
    trend_ok = drift_frac <= tol
    detail.update(slope=float(slope), window_span=span,
                  drift_over_window_frac=float(drift_frac),
                  drift_tolerance_frac=tol, trend_ok=bool(trend_ok))

    # ---- element 3: explicit stationarity, able to say NOT stationary ----
    half = n_win // 2
    m1 = float(np.mean(vw[:half]))
    m2 = float(np.mean(vw[half:]))
    step_frac = abs(m2 - m1) / ref
    scatter = float(np.std(vw)) / ref
    stationary = step_frac <= tol
    detail.update(mean_first_half=m1, mean_second_half=m2,
                  half_step_frac=float(step_frac),
                  window_scatter_frac=scatter,
                  stationary=bool(stationary))

    state = "PLATEAUED" if (trend_ok and stationary) else "NOT_PLATEAUED"
    detail["state"] = state
    detail["why"] = ("drift %.3e and half-step %.3e both within %.3e"
                     % (drift_frac, step_frac, tol)) if state == "PLATEAUED" else (
                     "drift %.3e (ok=%s) / half-step %.3e (ok=%s) against tol %.3e"
                     % (drift_frac, trend_ok, step_frac, stationary, tol))
    return state, detail


def plateau_plant_control(times, values, quantity, end_time):
    """PLANTED CONTROL on the plateau test itself (standing rule 3).

    A plateau test that returns PLATEAUED for everything would certify a ramp.
    So the SAME series is re-tested with a KNOWN ramp added, and the test is
    REQUIRED to reject it. If it cannot see the ramp, its verdict on the real
    series is not evidence and this refuses.
    """
    v = np.asarray(values, dtype=float)
    t = np.asarray(times, dtype=float)
    ref = abs(float(v[np.argmax(t)]))
    # a ramp 100x the tolerance across the whole run -- unmistakably NOT flat
    plant = 100.0 * DRIFT_TOL_FRAC[quantity] * ref
    v_ramped = v + plant * (t - t.min()) / max(t.max() - t.min(), 1e-300)
    st, det = plateau_state(t, v_ramped, quantity, end_time)
    if st != "NOT_PLATEAUED":
        refuse("PLATEAU CONTROL FAILED for %s: a planted ramp of %.6e (100x the "
               "registered tolerance) was graded %s. The plateau test has not "
               "been shown able to reject a drifting series, so its PLATEAUED "
               "verdicts are NOT EVIDENCE." % (quantity, plant, st))
    return dict(control="PZ-PLATEAU_%s" % quantity, planted_ramp=float(plant),
                graded=st, required="NOT_PLATEAUED", passed=True)
