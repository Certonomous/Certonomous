#!/usr/bin/env python3
"""
F16 -- THE GRADING PATH for Stokes' second problem.
It calls `scripts/roache_triple.py::grade_ladder` and rule 5 is reached through
that call and through NOTHING ELSE.  Exactly one call node, censused by AST at
every entry (a regex counts prose; see `control_grade_ladder_is_called`).

REFUSAL DISCIPLINE
------------------
`raise` / `sys.exit(2)` only.  ZERO `assert` statements, checked by AST parse
(L-332).  `grade_ladder` reaches its own gate through four asserts in the SHARED
`roache_triple.py` (:195, :632, :634, :637) carrying rule 1 and rule 5, which
`python3 -O` deletes; that file is referred to verification and is not this
team's to edit, so THIS FILE REFUSES TO RUN UNDER `-O` at entry.

CONVERGENCE IS CLASS C (CFD_CONVERGENCE_GATE_RULING_2026-08-25.md §2), all four
elements, element 4 exiting rather than returning a state.
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED: grade_f16.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including roache_triple.py:195,632,634,637,\n"
        "  which carry require_dim and the _seal invariants: the verdict must be\n"
        "  in the fixed vocabulary, the gate must be one-way against the band\n"
        "  verdict, and NO GCI may be quoted on a non-monotone triple. With those\n"
        "  deleted, rule 1 and rule 5 are not enforced by anything.\n")
    sys.exit(2)

import os
import re
import ast
import json
import math
import shutil
import tempfile
import argparse
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE. Rule 5 lives here and nowhere else.
import exact_stokes as EX               # THE EXACT SOLUTION, verified by substitution.

DIM = 1                                 # refinement in ONE direction: r = 2 exactly
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

CELLS = dict((n, ny) for n, ny, _ns in EX.LEVELS)
NSTEPS = dict((n, ns) for n, _ny, ns in EX.LEVELS)
DY = dict((n, EX.dy_of(ny)) for n, ny, _ns in EX.LEVELS)
DT = dict((n, EX.dt_of(ns)) for n, _ny, ns in EX.LEVELS)
END_TIME = EX.N_PERIODS * EX.PERIOD

# THE ONE DECLARED PARAMETER BOTH BANDS ARE BUILT FROM.  Declared BEFORE any
# run: the multiplicative window allowed around the ANALYTIC truncation-error
# prediction derived in exact_stokes.predicted_pointwise_error_amplitude.  The
# prediction is asymptotic and drops both the error's phase and the temporal
# contribution, so an equality would be a wrong band, not a strict one.  Three
# is not fitted, not measured, and not revisable after first compute.
BAND_FACTOR = 3.0

P_SOLVER_TOL = 1.0e-9                   # matches system/fvSolution, checked below
CAP_CORE_MIN = 20.0                     # wall_s * ranks / 60, summed over levels
RANKS = dict(coarse=1, medium=1, fine=1)

CLASS_C = dict(
    min_samples=20,      # element 4: 20 of the 41 phase-locked samples
    window=12,           # element 1: the criterion holds over 12 whole periods.
                         #   Justified, not inherited: the slowest transient this
                         #   domain supports decays at nu*(pi/H)^2 = 0.158 1/s,
                         #   a 6.3 s time constant, so a 12 s window is ~1.9
                         #   time constants and a surviving transient cannot hide
                         #   inside it.
    trend_tol=2.0e-4,
    stat_tol=1.0e-4,
    var_ratio=(0.2, 5.0),
    floor=1.0e-14,
)

WRITE_PATH_NOTE = (
    "OpenFOAM `sets` functionObject, `setFormat raw`, writing "
    "<case>/postProcessing/profile/<time>/profile_U.xy with THREE coordinate "
    "columns (x y z) followed by the three velocity components -- six columns. "
    "Layout pinned against REAL solver output already on this box: "
    "verification/runs/F6b_runs/coarse/postProcessing/singleGraph_x0/3418/"
    "line_k_nut_omega_p_U.xy carries 10 columns = 3 coordinates + four scalars "
    "+ 3 U components, which is where the three-coordinate layout was measured "
    "rather than assumed.")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# READERS
# ---------------------------------------------------------------------------
def read_xy_u(path):
    """Read a `sets`/raw .xy carrying ONE vector. Refuses on any other shape."""
    if not os.path.isfile(path):
        refuse("no sampled file at %s" % path)
    arr = np.loadtxt(path, comments="#", ndmin=2)
    if arr.ndim != 2 or arr.shape[1] != 6:
        refuse("%s has %s columns; a `sets`/raw sample of one vector has exactly "
               "6 (x y z Ux Uy Uz). %s"
               % (path, arr.shape[1] if arr.ndim == 2 else "?", WRITE_PATH_NOTE))
    if arr.shape[0] < 16:
        refuse("%s has only %d sampled points; refusing to integrate a profile "
               "error norm over that" % (path, arr.shape[0]))
    order = np.argsort(arr[:, 1])
    return arr[order, 1], arr[order, 3]


def _phase_of(path):
    """omega*t at the sample, from the time directory the file sits in."""
    t = float(os.path.basename(os.path.dirname(path)))
    return EX.OMEGA * t


def e2_from_xy(path):
    """G-F16-1: the domain-normalised L2 velocity-profile error.

        E2 = sqrt( (1/H) Int_0^H (u_num - u_exact)^2 dy ) / U0

    evaluated at a phase-locked instant (the file's own time), so the exact
    solution is evaluated at exactly the time the sample was written.
    """
    y, ux = read_xy_u(path)
    t = float(os.path.basename(os.path.dirname(path)))
    ue = np.array([EX.u_exact(float(yi), t) for yi in y])
    trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(math.sqrt(trap((ux - ue) ** 2, y) / EX.H) / EX.U0)


def u_at_delta_from_xy(path):
    """G-F16-2: u(delta)/U0, linearly interpolated between the two bracketing
    cell centres.  y = delta is a cell FACE at every level of this ladder, so a
    nearest-cell reading would be biased by half a cell and the bias would not
    refine away cleanly; the interpolation error is O(dy^2), the same order as
    the quantity being graded, and is absorbed in the registered band."""
    y, ux = read_xy_u(path)
    if not (y[0] <= EX.DELTA <= y[-1]):
        refuse("%s: y = delta = %g is outside the sampled range [%g, %g]. The "
               "gate quantity is ABSENT, which is reported as absent and never "
               "graded as a pass." % (path, EX.DELTA, y[0], y[-1]))
    return float(np.interp(EX.DELTA, y, ux) / EX.U0)


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (standing rule 3)
# ---------------------------------------------------------------------------
def _plant_column(src, dst, col, delta):
    rows = 0
    with open(dst, "w") as out:
        for line in open(src):
            if line.startswith("#") or not line.strip():
                out.write(line)
                continue
            parts = line.split()
            parts[col] = repr(float(parts[col]) + delta)
            out.write(" ".join(parts) + "\n")
            rows += 1
    return rows


def plant_control_e2(path, level):
    """Offset the Ux column by a known amount: every pointwise error moves by
    exactly that, so the post-plant E2 is PREDICTABLE from the pre-plant error
    array, and the reader must reproduce the prediction to 1e-14."""
    d = RT.PLANT
    y, ux = read_xy_u(path)
    t = float(os.path.basename(os.path.dirname(path)))
    ue = np.array([EX.u_exact(float(yi), t) for yi in y])
    trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    before = float(math.sqrt(trap((ux - ue) ** 2, y) / EX.H) / EX.U0)
    predicted = float(math.sqrt(trap((ux + d - ue) ** 2, y) / EX.H) / EX.U0)
    tmp = tempfile.mkdtemp(prefix="f16_plant_e2_")
    try:
        work = os.path.join(tmp, os.path.basename(path))
        os.makedirs(os.path.join(tmp, os.path.basename(os.path.dirname(path))),
                    exist_ok=True)
        work = os.path.join(tmp, os.path.basename(os.path.dirname(path)),
                            os.path.basename(path))
        if _plant_column(path, work, 3, d) == 0:
            refuse("nothing to plant into %s: no data rows" % path)
        after = e2_from_xy(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted) > 1e-14:
        refuse("PLANTED-ZERO CONTROL FAILED for E2 on %s: a Ux offset of %.6e "
               "must move E2 to %.17g by definition; the reader returned %.17g. "
               "The reader has not been shown able to see a plant, so its values "
               "are NOT EVIDENCE." % (path, d, predicted, after))
    return RT.external_plant_control("e2_from_xy", before, after,
                                     plant=(predicted - before),
                                     artifact=path, level=level)


def plant_control_u_delta(path, level):
    """Offset the Ux column: the interpolated value at y = delta must move by
    exactly that offset divided by U0. An exact, non-asymptotic prediction."""
    d = RT.PLANT
    before = u_at_delta_from_xy(path)
    tmp = tempfile.mkdtemp(prefix="f16_plant_ud_")
    try:
        sub = os.path.join(tmp, os.path.basename(os.path.dirname(path)))
        os.makedirs(sub, exist_ok=True)
        work = os.path.join(sub, os.path.basename(path))
        if _plant_column(path, work, 3, d) == 0:
            refuse("nothing to plant into %s: no data rows" % path)
        after = u_at_delta_from_xy(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs((after - before) - d / EX.U0) > 1e-12:
        refuse("PLANTED-ZERO CONTROL FAILED for u(delta) on %s: a Ux offset of "
               "%.6e must move the interpolated value by exactly %.6e; the "
               "reader moved it %.6e. Its values are NOT EVIDENCE."
               % (path, d, d / EX.U0, after - before))
    return RT.external_plant_control("u_at_delta_from_xy", before, after,
                                     plant=d / EX.U0, artifact=path, level=level)


# ---------------------------------------------------------------------------
# CLASS C -- four elements; element 4 EXITS
# ---------------------------------------------------------------------------
def class_c(t, v, label, cfg=None):
    cfg = CLASS_C if cfg is None else cfg
    t = np.asarray(t, dtype=float)
    v = np.asarray(v, dtype=float)
    if v.size < cfg["min_samples"]:
        refuse("CLASS C ELEMENT 4: %s has %d samples; the registered minimum is "
               "%d. NOT A RESULT. A verdict computed from what happened to be on "
               "disk is exactly the defect this limb exists to stop."
               % (label, v.size, cfg["min_samples"]))
    w = int(cfg["window"])
    if v.size < w:
        refuse("CLASS C ELEMENT 1: %s has %d samples, fewer than the registered "
               "sustained window of %d" % (label, v.size, w))
    tw, vw = t[-w:], v[-w:]
    scale = max(abs(float(np.mean(vw))), cfg["floor"])
    detail = dict(samples=int(v.size), window=w, window_span=float(tw[-1] - tw[0]),
                  window_mean=float(np.mean(vw)), scale=scale)
    slope = float(np.polyfit(tw, vw, 1)[0])
    drift = abs(slope) * (tw[-1] - tw[0]) / scale
    detail.update(fitted_slope=slope, relative_drift_over_window=drift,
                  trend_tol=cfg["trend_tol"])
    if drift > cfg["trend_tol"]:
        return "NOT_PLATEAUED_TREND", detail
    h = w // 2
    m1, m2 = float(np.mean(vw[:h])), float(np.mean(vw[h:]))
    s1 = float(np.var(vw[:h])) + cfg["floor"]
    s2 = float(np.var(vw[h:])) + cfg["floor"]
    ratio = s2 / s1
    detail.update(half_mean_first=m1, half_mean_second=m2,
                  half_mean_split=abs(m1 - m2) / scale, stat_tol=cfg["stat_tol"],
                  variance_ratio=ratio, var_ratio_band=cfg["var_ratio"])
    if abs(m1 - m2) / scale > cfg["stat_tol"]:
        return "NOT_STATIONARY_MEAN", detail
    if not (cfg["var_ratio"][0] <= ratio <= cfg["var_ratio"][1]):
        return "NOT_STATIONARY_VARIANCE", detail
    return "PLATEAUED", detail


def control_class_c_can_say_no():
    n = CLASS_C["min_samples"] + 21
    t = np.arange(n, dtype=float) * EX.PERIOD
    flat = np.full(n, -0.3095) + 1e-12 * np.sin(np.arange(n))
    ok, _ = class_c(t, flat, "control_flat")
    if ok != "PLATEAUED":
        refuse("CLASS C CONTROL FAILED: a flat series was reported %r, not "
               "PLATEAUED. The gate refuses everything and grades nothing." % ok)
    ramp = flat + 0.002 * t / t[-1]
    grow, _ = class_c(t, ramp, "control_ramp")
    if grow != "NOT_PLATEAUED_TREND":
        refuse("CLASS C ELEMENT 2 CONTROL FAILED: a drifting series was reported "
               "%r. A trend fit that cannot reject a growing series is not "
               "element 2." % grow)
    step = flat.copy()
    step[-(CLASS_C["window"] // 2):] += 0.0005
    stat, _ = class_c(t, step, "control_step")
    if stat not in ("NOT_STATIONARY_MEAN", "NOT_PLATEAUED_TREND"):
        refuse("CLASS C ELEMENT 3 CONTROL FAILED: a mean shift across the window "
               "halves was reported %r. The stationarity test cannot report NOT "
               "stationary." % stat)
    probe = ("import sys; sys.path.insert(0, %r)\n"
             "import grade_f16 as g\n"
             "import numpy as np\n"
             "try:\n"
             "    g.class_c(np.arange(5.0), np.ones(5), 'short')\n"
             "    print('CONTROL_FAILED_NO_REFUSAL')\n"
             "except SystemExit as e:\n"
             "    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n") % HERE
    p = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if "REFUSED" not in p.stdout.decode():
        refuse("CLASS C ELEMENT 4 CONTROL FAILED: a 5-sample series did not make "
               "class_c exit 2 (got %r)." % p.stdout.decode().strip())
    return dict(control="PZ-F16-CLASSC_four_limbs_each_shown_able_to_refuse",
                flat="PLATEAUED", ramp=grow, step=stat, short_series="exit 2",
                passed=True)


# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE -- a CENSUS OVER EVERY TIME STEP, not a last reading
# ---------------------------------------------------------------------------
FINAL_RES_RE = re.compile(
    r"solution singularity|Solving for p.*Final residual = ([0-9eE+\-.]+)")


def iterative_state(log_path):
    """Every time step's FINAL pressure residual must be at or below the
    solver's registered tolerance.

    This is NOT a Class A gate.  Class A's defect is a TWO-POINT SAMPLE at the
    end of a run; this is a census over all N steps, and it reports the count
    that failed, not whether the last one passed.  A transient run has no
    steady residual to plateau, so a plateau test would be the wrong instrument
    here and saying so is better than applying one that cannot mean anything.
    """
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated and an "
               "UNEVALUATED step is not a passed one" % log_path)
    vals = []
    for line in open(log_path, errors="replace"):
        if "Solving for p" in line and "Final residual" in line:
            m = re.search(r"Final residual = ([0-9eE+\-.]+)", line)
            if m:
                vals.append(float(m.group(1)))
    if not vals:
        refuse("no `Solving for p ... Final residual` lines in %s; the iterative "
               "state is ABSENT and an absent measurement is reported as absent, "
               "never as a pass" % log_path)
    bad = [v for v in vals if v > P_SOLVER_TOL]
    detail = dict(basis="per-time-step final p residual, census over ALL steps",
                  n_readings=len(vals), tolerance=P_SOLVER_TOL,
                  n_above_tolerance=len(bad), worst=max(vals))
    if bad:
        return "NOT_CONVERGED_%d_STEPS_ABOVE_TOL" % len(bad), detail
    return "CONVERGED", detail


# ---------------------------------------------------------------------------
# COMPLETION -- standing rule 4
# ---------------------------------------------------------------------------
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$")


def completion(case_dir, log_path, level):
    """rc (the launcher's), End, the final-step limb, fields, age guard, and --
    because this case runs a FIXED deltaT -- the `Time` count identity too.

    THE LIMB IS `latest + dt_final > endTime`, NOT `latest >= endTime` (which
    refused 4 of 9 genuinely complete F4 runs) and NOT a two-sided tolerance
    (choosing an epsilon after seeing which runs it admits is the fitted-
    threshold move).
    """
    out = dict(case=case_dir, log=log_path)
    if not os.path.isfile(log_path):
        return dict(out, done=False, why="no solver log at %s" % log_path)
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    dt = DT[level]
    out.update(n_times=len(times), latest=times[-1] if times else None, dt=dt)
    if not times:
        return dict(out, done=False, why="no `Time =` lines in the log")
    if "End" not in text:
        return dict(out, done=False, why="no `End` line: the solver did not finish")
    if not (times[-1] + dt > END_TIME):
        return dict(out, done=False,
                    why="latest %.9g + dt %.9g does not exceed endTime %.9g"
                        % (times[-1], dt, END_TIME))
    expected = int(round(END_TIME / dt))
    if len(times) != expected:
        return dict(out, done=False,
                    why="fixed-deltaT identity fails: %d `Time` lines, endTime/dt "
                        "= %d" % (len(times), expected))
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no 0/U to date the launch against; the "
                                         "age guard cannot be evaluated")
    t0 = os.path.getmtime(zero_u)
    end_dir = None
    for d in os.listdir(case_dir):
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and abs(float(d) - END_TIME) < 1e-9:
            end_dir = os.path.join(case_dir, d)
    if end_dir is None:
        return dict(out, done=False, why="no time directory at endTime %g" % END_TIME)
    missing, stale = [], []
    for f in ("U", "p"):
        fp = os.path.join(end_dir, f)
        if not os.path.isfile(fp):
            missing.append(f)
        elif os.path.getmtime(fp) <= t0:
            stale.append(f)
    if missing:
        return dict(out, done=False, why="fields missing at endTime: %s" % missing)
    if stale:
        return dict(out, done=False,
                    why="AGE GUARD: fields %s at endTime are NOT newer than the "
                        "case's own 0/U" % stale)
    return dict(out, done=True,
                why="End present; latest + dt > endTime; %d `Time` lines == "
                    "endTime/dt; U and p present at endTime and newer than 0/U"
                    % len(times))


# ---------------------------------------------------------------------------
# CENSUSES
# ---------------------------------------------------------------------------
def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read()))
                 if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path and `python3 -O` "
               "deletes every one (L-332): %s" % json.dumps(bad))
    return dict(files_checked=len(paths), assert_nodes=0)


def control_grade_ladder_is_called():
    """AST census of real call nodes, plus the text matcher driven BOTH ways on
    synthetic files so the terminal-reproducible evidence is itself controlled."""
    src = open(os.path.abspath(__file__)).read()
    calls = [n.lineno for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "grade_ladder"]
    if len(calls) != 1:
        refuse("expected EXACTLY ONE grade_ladder CALL NODE in this file; found "
               "%d at lines %s. More than one is a second gate; zero is the "
               "887ddfaf defect." % (len(calls), calls))
    pat = re.compile(r"RT\.grade_ladder\s*\(")
    grep_hits = [i + 1 for i, ln in enumerate(src.splitlines()) if pat.search(ln)]
    tmp = tempfile.mkdtemp(prefix="f16_gl_control_")
    try:
        neg = os.path.join(tmp, "no_call.py")
        open(neg, "w").write("def f():\n    return 1\n")
        if [i for i, ln in enumerate(open(neg).read().splitlines()) if pat.search(ln)]:
            refuse("GREP CONTROL FAILED: the matcher found a call in a file that "
                   "has none. Its hits mean nothing.")
        pos = os.path.join(tmp, "yes_call.py")
        open(pos, "w").write("import x as RT\ndef f():\n"
                             "    return RT.grade_ladder(q, l, d, b, p)\n")
        if not [i for i, ln in enumerate(open(pos).read().splitlines()) if pat.search(ln)]:
            refuse("GREP CONTROL FAILED: the matcher MISSED a planted call.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F16-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways",
                ast_call_nodes=calls, grep_lines=grep_hits,
                negative_control="miss on a file with no call",
                positive_control="hit on a planted call", passed=True)


def control_solver_tolerance_matches_dict():
    """The iterative census compares against P_SOLVER_TOL. That constant must be
    the tolerance the solver actually used, or the census grades against a
    number nobody enforced."""
    dic = os.path.join(HERE, "case", "system", "fvSolution")
    if not os.path.isfile(dic):
        refuse("no %s: the registered solver tolerance cannot be checked against "
               "the dictionary the run will use" % dic)
    txt = open(dic).read()
    m = re.search(r"\bp\b[^}]*?tolerance\s+([0-9eE+\-.]+)\s*;", txt, re.S)
    if not m:
        refuse("could not find the p solver tolerance in %s" % dic)
    got = float(m.group(1))
    if got != P_SOLVER_TOL:
        refuse("P_SOLVER_TOL = %g but system/fvSolution sets %g. The iterative "
               "census would grade against a threshold the solver never used."
               % (P_SOLVER_TOL, got))
    return dict(control="solver_tolerance_agrees_with_fvSolution",
                registered=P_SOLVER_TOL, on_disk=got, passed=True)


# ---------------------------------------------------------------------------
# BANDS
# ---------------------------------------------------------------------------
def bands():
    """Both bands descend from ONE declared parameter, BAND_FACTOR = 3, applied
    to the ANALYTIC truncation-error prediction derived and documented in
    exact_stokes.py:

        |e(y)| ~ (k^2 dy^2 / 6) U0 exp(-k y)

    G-F16-1 (E2): the domain-normalised L2 norm of that amplitude at the FINEST
    spacing, times [1/3, 3].
    G-F16-2 (u at delta): the EXACT value, plus or minus 3x the same amplitude
    evaluated at y = delta.

    Neither number comes from a measured deviation: at the moment of freeze no
    run of this case exists anywhere on this box.
    """
    dy_f = DY["fine"]
    e2p = EX.predicted_L2_error(dy_f)
    ud = EX.u_at_delta_exact_normalised()
    tol = BAND_FACTOR * EX.predicted_error_at_delta(dy_f)
    return {
        "G-F16-1_E2_velocity_profile_L2": dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("analytic second-order truncation prediction E2 = %.9e at "
                       "dy_fine = %g, times [1/%g, %g]" % (e2p, dy_f, BAND_FACTOR,
                                                           BAND_FACTOR))),
        "G-F16-2_u_at_delta": dict(
            band=(ud - tol, ud + tol), reference=ud, dim=DIM,
            principle=("exact u(delta)/U0 = %.15f +/- %g x the analytic "
                       "pointwise truncation amplitude at y = delta, = +/- %.9e"
                       % (ud, BAND_FACTOR, tol))),
    }


# ---------------------------------------------------------------------------
# THE DEMONSTRATION -- both gates shown able to take a failing AND a passing
# value, through the real readers, on files in the pinned write format
# ---------------------------------------------------------------------------
def synth_xy(path, y, ux):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for yi, ui in zip(y, ux):
            f.write("%.12g \t%.12g \t%.12g \t%.12g \t%.12g \t%.12g\n"
                    % (0.0, yi, 0.0, ui, 0.0, 0.0))


def demonstrate(bnd):
    """ZERO COMPUTE."""
    tmp = tempfile.mkdtemp(prefix="f16_demo_")
    rows = []
    try:
        dy = DY["fine"]
        y = np.arange(dy / 2.0, EX.H, dy)
        t = float(EX.N_PERIODS * EX.PERIOD)
        exact = np.array([EX.u_exact(float(yi), t) for yi in y])
        amp = EX.predicted_pointwise_error_amplitude(dy)

        # The physically-shaped error the prediction describes: amplitude
        # exp(-k y), the profile the truncation analysis gives.
        shape = np.exp(-EX.K * y)
        for scale, want in ((1.0, "inside"), (40.0, "outside")):
            f = os.path.join(tmp, "%g" % t, "profile_U.xy")
            synth_xy(f, y, exact + scale * amp * shape)
            val = e2_from_xy(f)
            lo, hi = bnd["G-F16-1_E2_velocity_profile_L2"]["band"]
            rows.append(dict(gate="G-F16-1_E2_velocity_profile_L2",
                             construction="exact + %g x the predicted truncation "
                                          "amplitude profile" % scale,
                             value=val, band=[lo, hi],
                             inside=bool(lo <= val <= hi), intended=want))

        for scale, want in ((1.0, "inside"), (40.0, "outside")):
            f = os.path.join(tmp, "%g" % t, "profile_U.xy")
            synth_xy(f, y, exact + scale * amp * shape)
            val = u_at_delta_from_xy(f)
            lo, hi = bnd["G-F16-2_u_at_delta"]["band"]
            rows.append(dict(gate="G-F16-2_u_at_delta",
                             construction="exact + %g x the predicted truncation "
                                          "amplitude profile" % scale,
                             value=val, band=[lo, hi],
                             inside=bool(lo <= val <= hi), intended=want))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: a construction intended to "
                   "land %s the band returned %.6g against band %s. A gate that "
                   "cannot take both values is not a gate."
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH a passing and a "
                   "failing value" % g)
    return rows


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
GATES = {"G-F16-1_E2_velocity_profile_L2": (e2_from_xy, plant_control_e2),
         "G-F16-2_u_at_delta": (u_at_delta_from_xy, plant_control_u_delta)}


def numeric_time_dirs(root):
    if not os.path.isdir(root):
        return []
    out = [(float(d), os.path.join(root, d)) for d in os.listdir(root)
           if re.match(r"^[0-9]+(\.[0-9]+)?$", d)]
    out.sort(key=lambda t: t[0])
    return out


def series_for(case_dir, reader):
    """The plateau series is the GRADED QUANTITY ITSELF, phase-locked: one
    sample per whole period, so every sample is at omega t = 0 (mod 2 pi) and
    the series measures period-to-period change rather than the oscillation."""
    root = os.path.join(case_dir, "postProcessing", "profile")
    ts, vs, last = [], [], None
    for t, d in numeric_time_dirs(root):
        if abs(t / EX.PERIOD - round(t / EX.PERIOD)) > 1e-9:
            continue
        f = os.path.join(d, "profile_U.xy")
        if not os.path.isfile(f):
            continue
        ts.append(t)
        vs.append(reader(f))
        last = f
    if last is None:
        refuse("no phase-locked profile samples under %s. The gate quantity is "
               "ABSENT." % root)
    return ts, vs, last


def grade_one(root, gate, bnd):
    reader, planter = GATES[gate]
    levels, detail = [], []
    for name, _ny, _ns in EX.LEVELS:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING",
                        note="level %r absent from %s" % (name, root))
        comp = completion(case_dir, os.path.join(case_dir, "log.icoFoam"), name)
        if not comp["done"]:
            return dict(gate=gate, verdict="PENDING",
                        note="level %r is not complete: %s" % (name, comp["why"]),
                        completion=comp)
        ts, vs, last = series_for(case_dir, reader)
        it_state, it_detail = iterative_state(os.path.join(case_dir, "log.icoFoam"))
        pl_state, pl_detail = class_c(ts, vs, "%s/%s" % (name, gate))
        levels.append(dict(name=name, cells=CELLS[name], value=vs[-1]))
        detail.append(dict(name=name, cells=CELLS[name], value=vs[-1],
                           artifact=last, dy=DY[name], dt=DT[name],
                           completion=comp, iterative=it_state,
                           iterative_detail=it_detail, plateau=pl_state,
                           plateau_detail=pl_detail))

    pc = planter(detail[-1]["artifact"], detail[-1]["name"])
    spec = bnd[gate]

    # ---- THE ONE AND ONLY GATE CALL.
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"],
        plant_control=pc,
        iterative_states=dict((d["name"], d["iterative"]) for d in detail),
        plateau_states=dict((d["name"], d["plateau"]) for d in detail),
        reference=spec["reference"])

    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["gated_by"] = ("scripts/roache_triple.py::grade_ladder -- rule 5 is "
                       "reached through this call and through nothing else")
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r"
               % (gate, row["verdict"]))
    return row


def selftest_predicate(controls, demo, census):
    if census["assert_nodes"] != 0:
        return False, "assert nodes present in this rung's path"
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if len(demo) != 4:
        return False, "expected 4 demonstration rows, got %d" % len(demo)
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green; both gate quantities shown able to take a "
                  "passing AND a failing value through the real reader on the "
                  "real write format; 0 assert nodes; exactly one grade_ladder "
                  "call node; __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs",
                                                   "F16_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__),
                             os.path.join(HERE, "exact_stokes.py")])
    controls = [EX.control_symbolic_substitution(),
                EX.control_substitution_is_able_to_fail(),
                EX.control_truncation_floor_is_dominated(),
                EX.control_ladder_is_geometrically_similar(),
                control_class_c_can_say_no(),
                control_grade_ladder_is_called(),
                control_solver_tolerance_matches_dict()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"],
                                                  reference=v["reference"],
                                                  principle=v["principle"]))
                                         for k, v in bnd.items()),
                              gate_demonstration=demo,
                              write_path=WRITE_PATH_NOTE,
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        # THE CLAIM IS INSIDE THE PASSING BRANCH.
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    rows = [grade_one(a.root, g, bnd) for g in sorted(GATES)]
    out = a.out or os.path.join(a.root, "F16_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F16-SL2", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F16_SL2_PREREGISTRATION.md",
                       assert_census=census, controls=controls,
                       gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                       cap_core_min=CAP_CORE_MIN, rows=rows),
                  f, indent=2, default=str)
    print("F16 -- STOKES' SECOND PROBLEM -- TALLY")
    print("=" * 78)
    for r in rows:
        print("%-40s %s" % (r["gate"], r["verdict"]))
        for k in ("why", "note"):
            if k in r:
                print("    %s" % r[k])
    print("=" * 78)
    print("gated by: scripts/roache_triple.py::grade_ladder")
    print("written: %s" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
