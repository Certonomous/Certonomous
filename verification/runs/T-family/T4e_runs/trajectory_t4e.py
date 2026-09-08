#!/usr/bin/env python3
"""T4e fine-level C6.3 TRAJECTORY instrument -- it BOTH measures the fine C6.3
trajectory vs iteration AND controls the run (it triggers the clean early stop on
robust D1 confirmation).  Because it AFFECTS the measurement (it decides when the
solver stops), it carries a PLANTED control on its NEW logic -- the windowed
classifier -- per CLAUDE.md rule 3.

WHAT IS MEASURED.  At each written fine checkpoint k (writeInterval 4000, purgeWrite
0 so every one survives) the C6.3 quantity is
    C6.3(k) = max over G1/G2/G3 of | peak(U/U_bulk) at k - peak at k-1 |
read through the FROZEN analyse_t4.sample_profile / analyse_t4.peak_of -- the SAME
reader control C6.3 grades with, imported here and never re-implemented.  The
trajectory is the series {(iteration_k, C6.3(k))}.  This instrument does NOT change
the C6.3 2e-4 tol (analyse_t4e.py owns that gate); the classifier below is a
SEPARATE decision rule.

THE ROBUST-CONFIRMATION THRESHOLD (registered VERBATIM in T4e_registered.json
early_termination_D1, pinned prediction-first; the supervisor set it):

  D1 is ROBUSTLY CONFIRMED (=> clean early terminate of the fine leg) when ALL THREE
  hold over a sliding window of the most recent W = 15 consecutive fine-level
  checkpoints (= 60,000 iters), evaluated only once iteration >= 64,000 (past the
  initial transient):
   (1) NON-DECAY / OSCILLATION-DOMINATES-TREND: the OLS slope of ln(C6.3) vs iteration
       corresponds to a per-checkpoint decay ratio rho_fit >= 0.95 (fast-decay
       backstop; a genuine transient shows rho <= ~0.81), AND the net trend the OLS
       linear fit of C6.3 vs iteration explains across the window
       (net_trend_drop = |slope| x (iter_last - iter_first)) is <= 0.5 x the detrended
       peak-to-peak swing (ptp_detrended = max(resid) - min(resid)) -- i.e. the
       oscillation swing is at least 2x the net drift. A limit cycle has ~zero net
       trend << oscillation and passes; a monotone OR noisy decay has the trend
       dominating and fails. (The former endpoint clause window-last >= 0.85 x
       window-first is DEPRECATED: it false-rejects a limit cycle caught in an unlucky
       phase and admits a noisy slow decay at rho 0.95-0.99.)
   (2) BOUNDED WELL ABOVE TOL: window-mean C6.3 >= 1e-3 (5x the 2e-4 tol), AND
       window-max/window-min <= 5.
   (3) OSCILLATORY (limit cycle, not a stall): the detrended C6.3 series has >= 4
       sign changes (>= 2 full oscillation periods) within the window.
  endTime 160,000 remains the HARD cap: if D1 is never robustly confirmed by 160,000,
  the outcome is D2 (if C6.3 cleared 2e-4 -> grade the full triple) or D3
  (decaying-not-cleared -> continuation rung).

THE CLEAN STOP.  On robust confirmation the instrument rewrites the fine case's
system/controlDict `stopAt endTime` -> `stopAt writeNow` (runTimeModifiable true,
set by build_t4e.py).  OpenFOAM re-reads controlDict at the next time step, writes
the current fields and stops with a clean `End` line.  This is NOT a kill -- a killed
solver leaves no End line and the fields it half-wrote cannot be trusted.  The D1
marker is WRITTEN BY THIS INSTRUMENT (never inferred): D1_CONFIRMED_TERMINATE.<case>
in the run root, recording the confirmation iteration and the trajectory evidence,
clearly distinguished from an accidental timeout cap.

COMPLETION SEMANTICS.  The D1 branch is a NON-CONVERGENCE finding: `last time ==
endTime` is NOT claimed and NOT needed (the deliverable is the measured limit-cycle
trajectory, not a converged field).  Verdict NOT A RESULT (unsteadiness), discharged
by routing to the transient/URANS successor.  mark_done_t4e.py (unchanged strict
rule 4 + age guard) and the Roache triple in analyse_t4e.py govern ONLY the D2/D3
branches, which DO require reaching endTime 160000.  Early-stop never masquerades as
a rule-4 completion.

THE PLANTED CONTROL (rule 3), TWO ARMS + a slow-decay arm.  A classifier that always
fires, or never fires, is worthless; a reader not shown able to BOTH see D1 AND
reject decay is not evidence.  --controls (also driven by --selftest) plants:
  ARM A  -- a synthetic sustained limit cycle -> the confirmation MUST FIRE;
  ARM B  -- a synthetic decaying series at rho <= 0.81 -> MUST NOT fire;
  ARM S  -- a synthetic slow decay at rho ~ 0.99      -> MUST NOT fire.
plus gate arms (iteration < 64000, and < W checkpoints) that MUST NOT fire, and a
determinism arm (identical series -> identical verdict).

NO `assert` STATEMENT IN THIS FILE (L-332).  Refusals are explicit exits;
--selftest counts AST asserts and drives every arm under python3 AND python3 -O.

Usage:
  trajectory_t4e.py --selftest                          # planted controls, no case
  trajectory_t4e.py --controls                          # the three arms only
  trajectory_t4e.py --case-dir DIR [--foam-bashrc F] --once
                                                        # classify the live series once
  trajectory_t4e.py --case-dir DIR [--foam-bashrc F] --once --commit
                                                        # ... and, IF confirmed, apply the
                                                        # clean stop + write the D1 marker

Exit codes: 0 ok / not confirmed;  3 D1 CONFIRMED (with --commit: stop applied,
            marker written);  1 selftest failed;  2 REFUSAL.
"""
import argparse
import ast
import datetime
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T4DIR = os.path.join(os.path.dirname(HERE), "T4_runs")
sys.path.insert(0, T4DIR)
import analyse_t4 as A                                   # noqa: E402  FROZEN reader (sample_profile, peak_of)

REG = json.load(open(os.path.join(HERE, "T4e_registered.json")))
FINE_CASE = "T4e_IJ_f"
ET = REG["early_termination_D1"]["params"]
W = int(ET["W_checkpoints"])
WRITE_INTERVAL = int(ET["writeInterval"])
EVAL_ITER_MIN = int(ET["eval_only_once_iter_ge"])
RHO_FIT_MIN = float(ET["cond1_non_decay"]["rho_fit_min"])
TREND_OVER_OSC_MAX = float(ET["cond1_non_decay"]["trend_over_osc_max"])
# DEPRECATED (T4e §3 review, supervisor aaa7330ecb6ea9c60): the former cond1 endpoint clause
# `window-last >= last_ge_frac_of_first * window-first` (0.85) is removed. It false-REJECTS a
# genuine limit cycle caught in an unlucky window phase, and it lets a NOISY slow decay
# (rho 0.95-0.99 with >=4 noise sign-changes) pass all three -> false D1. Replaced by the
# trend-vs-oscillation test below (net_trend_drop <= TREND_OVER_OSC_MAX * ptp_detrended).
MEAN_MIN = float(ET["cond2_bounded_above_tol"]["window_mean_min"])
MAXMIN_MAX = float(ET["cond2_bounded_above_tol"]["window_max_over_min_max"])
SIGN_CHANGES_MIN = int(ET["cond3_oscillatory"]["detrended_sign_changes_min"])
GROWS = [(k, float(v["r_over_D"])) for k, v in REG["graded_rows"].items() if k.startswith("G")]

EXIT_OK, EXIT_SELFTEST_FAIL, EXIT_REFUSE, EXIT_CONFIRMED = 0, 1, 2, 3


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------- math helpers
def _ols(xs, ys):
    """Ordinary least squares slope, intercept of ys vs xs."""
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    den = n * sxx - sx * sx
    if den == 0.0:
        return 0.0, sy / n
    slope = (n * sxy - sx * sy) / den
    intercept = (sy - slope * sx) / n
    return slope, intercept


def _sign_changes(resid):
    """Number of sign changes in a residual series; exact zeros carry the prior sign."""
    sc = 0
    prev = 0
    for r in resid:
        if r == 0.0:
            continue
        s = 1 if r > 0.0 else -1
        if prev != 0 and s != prev:
            sc += 1
        prev = s
    return sc


# --------------------------------------------------------- the physics read
def c63_series(case_dir, foam_bashrc):
    """The fine C6.3 trajectory READ FROM DISK through the FROZEN reader.

    Returns [(iteration, C6.3), ...] for k >= 2 (the first checkpoint has no
    predecessor).  Every G-row peak is read via analyse_t4.sample_profile /
    analyse_t4.peak_of -- never re-implemented here.
    """
    times = sorted((t for t in os.listdir(case_dir)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0),
                   key=float)
    if len(times) < 2:
        return []
    peaks = {}   # time -> {r_over_d: peak U/U_bulk}
    for t in times:
        row = {}
        for _, rod in GROWS:
            prof = A.sample_profile(case_dir, t, rod, foam_bashrc)
            if prof is None:
                return None   # a reader miss is a refusal upstream, not a fabricated series
            row[rod] = A.peak_of(prof)[0]
        peaks[t] = row
    series = []
    for i in range(1, len(times)):
        prev, cur = times[i - 1], times[i]
        ch = max(abs(peaks[cur][rod] - peaks[prev][rod]) for _, rod in GROWS)
        series.append((float(cur), ch))
    return series


# ------------------------------------------------------- the windowed classifier
def classify_window(series):
    """Evaluate the three registered conditions on the most-recent W checkpoints.

    `series` is [(iteration, C6.3), ...].  Returns a dict; `confirmed` is
    cond1 AND cond2 AND cond3.  A non-positive C6.3 in the window (a
    converged/stalled checkpoint) cannot be a sustained limit cycle -> cond1 False.
    """
    out = dict(enough=len(series) >= W, confirmed=False)
    if len(series) < W:
        out["reason"] = "only %d checkpoints, need W=%d" % (len(series), W)
        return out
    win = series[-W:]
    iters = [float(it) for it, _ in win]
    c = [float(v) for _, v in win]
    first, last = c[0], c[-1]
    mn, mx, mean = min(c), max(c), sum(c) / len(c)

    # --- linear fit of C6.3 vs iteration: shared by cond1 (trend) and cond3 (detrend) ---
    sl, ic = _ols(iters, c)
    resid = [v - (sl * it + ic) for it, v in zip(iters, c)]
    net_trend_drop = abs(sl) * (iters[-1] - iters[0])   # net change the trend line explains
    ptp_detrended = max(resid) - min(resid)             # oscillation swing about the trend

    # --- cond 1: NON-DECAY / OSCILLATION-DOMINATES-TREND -------------------
    # rho_fit is the fast-decay backstop; the trend-vs-oscillation test rejects BOTH a
    # monotone slow decay (trend dominates, ptp ~ 0) AND a noisy slow decay (trend still
    # dominates the small oscillation). A limit cycle has ~zero net trend << oscillation.
    if mn <= 0.0:
        cond1 = False
        rho_fit = float("nan")
    else:
        slope_ln, _ = _ols(iters, [math.log(v) for v in c])
        rho_fit = math.exp(slope_ln * WRITE_INTERVAL)
        cond1 = (rho_fit >= RHO_FIT_MIN) and (net_trend_drop <= TREND_OVER_OSC_MAX * ptp_detrended)

    # --- cond 2: BOUNDED WELL ABOVE TOL -----------------------------------
    cond2 = (mean >= MEAN_MIN) and (mn > 0.0) and (mx / mn <= MAXMIN_MAX)

    # --- cond 3: OSCILLATORY (detrended sign changes) ---------------------
    sc = _sign_changes(resid)
    cond3 = sc >= SIGN_CHANGES_MIN

    out.update(
        window_iters=[iters[0], iters[-1]],
        window_first=first, window_last=last,
        net_trend_drop=net_trend_drop, ptp_detrended=ptp_detrended,
        rho_fit=rho_fit, window_mean=mean, window_max=mx, window_min=mn,
        max_over_min=(mx / mn if mn > 0 else float("inf")), sign_changes=sc,
        cond1_non_decay=cond1, cond2_bounded=cond2, cond3_oscillatory=cond3,
        confirmed=bool(cond1 and cond2 and cond3))
    return out


def robust_confirmed(series, current_iter):
    """The full registered gate: current_iter >= 64000 AND W checkpoints AND the
    three conditions.  Returns (bool, evidence-dict)."""
    ev = classify_window(series)
    ev["current_iter"] = current_iter
    ev["iter_gate_ge_%d" % EVAL_ITER_MIN] = (current_iter >= EVAL_ITER_MIN)
    if current_iter < EVAL_ITER_MIN:
        ev["confirmed"] = False
        ev.setdefault("reason", "iteration %d < eval floor %d (still in the transient)"
                      % (current_iter, EVAL_ITER_MIN))
    return bool(ev["confirmed"]), ev


# ----------------------------------------------------------- the clean stop
def apply_stop_trigger(case_dir):
    """Rewrite system/controlDict stopAt endTime -> writeNow.  Refuses unless
    runTimeModifiable is true (else the rewrite is never read at runtime) and unless
    exactly one `stopAt endTime` line is present.  NOT a kill."""
    cd_path = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd_path):
        refuse("no system/controlDict at %s -- cannot arm the clean stop" % cd_path)
    txt = open(cd_path).read()
    if not re.search(r"^\s*runTimeModifiable\s+true\s*;", txt, re.M):
        refuse("controlDict has no 'runTimeModifiable true' -- a stopAt rewrite would "
               "NOT be read at runtime (build_t4e.py must set it); refusing to arm a "
               "stop that would silently do nothing")
    new, n = re.subn(r"^(\s*stopAt\s+)endTime(\s*;)", r"\g<1>writeNow\g<2>", txt, flags=re.M)
    if n != 1:
        refuse("controlDict: expected exactly one 'stopAt endTime' line to rewrite to "
               "'stopAt writeNow', found %d" % n)
    tmp = cd_path + ".t4e_stop.tmp"
    open(tmp, "w").write(new)
    os.replace(tmp, cd_path)
    print("clean stop ARMED: controlDict stopAt endTime -> writeNow at %s "
          "(solver writes current fields and stops with an End line)" % cd_path)


def write_d1_marker(root, case, current_iter, ev, series):
    """Write the DISTINCT D1 marker.  It is the instrument's own record -- never
    inferred, and never a rule-4 completion or a timeout cap."""
    p = os.path.join(root, "D1_CONFIRMED_TERMINATE.%s" % case)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "marker=D1_CONFIRMED_TERMINATE",
        "case=%s" % case,
        "written_utc=%s" % now,
        "confirmation_iteration=%d" % current_iter,
        "meaning=DELIBERATE clean early termination on ROBUST D1 confirmation "
        "(controlDict stopAt writeNow). This is NOT a rule-4 completion (last==endTime "
        "is neither claimed nor needed) and NOT a timeout cap. The deliverable is the "
        "measured limit-cycle C6.3 trajectory below, not a converged field.",
        "verdict=NOT A RESULT (unsteadiness) -- DISCHARGED by routing to the "
        "transient/URANS successor rung (T4e_registered.json d1_transient_route).",
        "W_checkpoints=%d" % W,
        "eval_iter_floor=%d" % EVAL_ITER_MIN,
        "cond1_non_decay=%s (rho_fit=%.4f >= %.2f ; net_trend_drop=%.4e <= %.2f x ptp_detrended=%.4e)"
        % (ev.get("cond1_non_decay"), ev.get("rho_fit", float("nan")), RHO_FIT_MIN,
           ev.get("net_trend_drop", float("nan")), TREND_OVER_OSC_MAX, ev.get("ptp_detrended", float("nan"))),
        "cond2_bounded=%s (mean=%.4e >= %.1e ; max/min=%.3f <= %.1f)"
        % (ev.get("cond2_bounded"), ev.get("window_mean", float("nan")), MEAN_MIN,
           ev.get("max_over_min", float("nan")), MAXMIN_MAX),
        "cond3_oscillatory=%s (detrended sign changes=%d >= %d)"
        % (ev.get("cond3_oscillatory"), ev.get("sign_changes", -1), SIGN_CHANGES_MIN),
        "trajectory_iteration:C6.3=" + ";".join("%d:%.6e" % (int(it), v) for it, v in series),
    ]
    open(p, "w").write("\n".join(lines) + "\n")
    print("D1 marker written: %s" % p)
    return p


# --------------------------------------------------------------- live once-mode
def run_once(case_dir, foam_bashrc, commit):
    case_dir = os.path.abspath(case_dir)
    root = os.path.dirname(case_dir)
    case = os.path.basename(case_dir)
    if case != FINE_CASE:
        refuse("trajectory_t4e.py measures the FINE level only; got %r, expected %s"
               % (case, FINE_CASE))
    latest = A.latest_time(case_dir)
    if latest is None:
        print("no checkpoint beyond 0 yet -- nothing to classify")
        return EXIT_OK
    current_iter = int(float(latest))
    series = c63_series(case_dir, foam_bashrc)
    if series is None:
        refuse("the FROZEN reader returned nothing on a checkpoint -- refusing to "
               "fabricate a trajectory (rule 3: a zero from a blind reader is not evidence)")
    if not series:
        print("fewer than 2 checkpoints -- no C6.3 trajectory yet")
        return EXIT_OK
    confirmed, ev = robust_confirmed(series, current_iter)
    print("iter=%d  checkpoints=%d  window=%s" % (current_iter, len(series), ev.get("window_iters")))
    print("  cond1 non-decay      = %s" % ev.get("cond1_non_decay"))
    print("  cond2 bounded>>tol   = %s" % ev.get("cond2_bounded"))
    print("  cond3 oscillatory    = %s" % ev.get("cond3_oscillatory"))
    print("  ROBUSTLY CONFIRMED   = %s" % confirmed)
    if not confirmed:
        return EXIT_OK
    if commit:
        # belt-and-braces: the FROZEN reader's own planted-zero control on the live case
        A.planted_zero_control(case_dir, latest, foam_bashrc, r_over_d=GROWS[0][1])
        apply_stop_trigger(case_dir)
        write_d1_marker(root, case, current_iter, ev, series)
    else:
        print("  (--commit not given: NOT arming the stop and NOT writing the marker)")
    return EXIT_CONFIRMED


# --------------------------------------------------------------- planted controls
def _synth_limit_cycle(n=W, wi=WRITE_INTERVAL, A0=2.0e-3, amp=0.5e-3, period_chk=3.5,
                       start_iter=EVAL_ITER_MIN):
    return [(start_iter + i * wi, A0 + amp * math.sin(2.0 * math.pi * i / period_chk))
            for i in range(n)]


def _synth_decay(rho, C0, n=W, wi=WRITE_INTERVAL, start_iter=EVAL_ITER_MIN):
    return [(start_iter + i * wi, C0 * (rho ** i)) for i in range(n)]


def _synth_noisy_decay(rho, C0, osc, n=W, wi=WRITE_INTERVAL, period_chk=3.5, start_iter=EVAL_ITER_MIN):
    """A slow decay at `rho` with a superimposed oscillation of amplitude `osc` big
    enough to give >= 4 detrended sign changes (so cond3 passes) but small enough that
    the decay TREND still dominates (so cond1's trend-vs-oscillation clause rejects it).
    This is the exact false-D1 hole the §3 review closed."""
    return [(start_iter + i * wi, C0 * (rho ** i) + osc * math.sin(2.0 * math.pi * i / period_chk))
            for i in range(n)]


def controls():
    """The rule-3 planted control on the windowed classifier: it must BOTH fire on a
    planted limit cycle AND reject planted decay (both fast and slow)."""
    fails = []

    def arm(name, series, want_fire, current_iter=None):
        ci = current_iter if current_iter is not None else int(series[-1][0])
        confirmed, ev = robust_confirmed(series, ci)
        ok = (confirmed == want_fire)
        detail = ("cond1=%s cond2=%s cond3=%s | rho_fit=%.4f net_trend=%.3e ptp=%.3e "
                  "(trend<=%.2f*ptp?) mean=%.2e max/min=%.2f signchg=%s"
                  % (ev.get("cond1_non_decay"), ev.get("cond2_bounded"), ev.get("cond3_oscillatory"),
                     ev.get("rho_fit", float("nan")), ev.get("net_trend_drop", float("nan")),
                     ev.get("ptp_detrended", float("nan")), TREND_OVER_OSC_MAX,
                     ev.get("window_mean", float("nan")), ev.get("max_over_min", float("nan")),
                     ev.get("sign_changes", "-")))
        print("  [%s] %-34s confirmed=%-5s want=%-5s | %s"
              % ("ok " if ok else "FAIL", name, confirmed, want_fire, detail))
        if not ok:
            fails.append(name)
        return ev

    print("trajectory_t4e planted controls (rule 3; classifier must see D1 AND reject decay):")
    arm("ARM A: sustained limit cycle -> FIRES", _synth_limit_cycle(), True)
    arm("ARM B: decay rho=0.81 -> NOT fire", _synth_decay(0.81, 5.0e-3), False)
    arm("ARM S: slow decay rho=0.99 -> NOT fire", _synth_decay(0.99, 3.0e-3), False)
    arm("ARM S2: NOISY slow decay rho=0.97 -> NOT fire",
        _synth_noisy_decay(0.97, 3.0e-3, 0.2e-3), False)
    # gate arms: a genuine limit cycle must still NOT fire before the transient / with < W
    arm("GATE: limit cycle but iter<64000 -> NOT fire", _synth_limit_cycle(start_iter=8000),
        False, current_iter=60000)
    arm("GATE: limit cycle but only W-1 checkpoints -> NOT fire",
        _synth_limit_cycle(n=W - 1), False)
    # determinism (the negative-arm analogue): identical series -> identical verdict
    s = _synth_limit_cycle()
    c1, _ = robust_confirmed(s, int(s[-1][0]))
    c2, _ = robust_confirmed(list(s), int(s[-1][0]))
    okd = (c1 == c2 is True)
    print("  [%s] DETERMINISM: identical series -> identical verdict (%s==%s)"
          % ("ok " if okd else "FAIL", c1, c2))
    if not okd:
        fails.append("determinism")
    return fails


def selftest():
    fails = controls()
    me = os.path.abspath(__file__)
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(me).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n_assert, planted))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return EXIT_OK if not fails else EXIT_SELFTEST_FAIL


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--case-dir")
    ap.add_argument("--foam-bashrc", default="/usr/lib/openfoam/openfoam2606/etc/bashrc")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.controls:
        return EXIT_OK if not controls() else EXIT_SELFTEST_FAIL
    if a.case_dir and a.once:
        return run_once(a.case_dir, a.foam_bashrc, a.commit)
    ap.print_help()
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
