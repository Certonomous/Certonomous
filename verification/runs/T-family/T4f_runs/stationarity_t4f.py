#!/usr/bin/env python3
"""DRAFT transient-statistics instrument for T4f (S1 stationarity, S2 averaging-window adequacy,
period measurement) with its own planted control (CLAUDE.md rule 3).

It reads the INSTANTANEOUS G-row peak time series that build_t4f's `sets` functionObject writes
(postProcessing/gLines/<t>/<Gx>_U.xy), through the FROZEN analyse_t4.peak_of on each sampled profile,
and decides the transient-statistics gates that analyse_t4f consults:

  S1 STATIONARITY   -- the discard covered the initial transient: the measured stationarity onset
                       t_stat <= T_init, and there is no net drift across the averaging window
                       (|mean(1st half) - mean(2nd half)| <= EPS_STAT).
  S2 WINDOW ADEQUACY-- the running average of the windowed peak has converged
                       (|mean(last 25%) - mean(prev 25%)| <= EPS_AVG) AND either the window holds
                       >= N_MIN oscillation periods OR the signal is STEADY (ptp < AMP_FLOOR -- a
                       measured finding falsifying the unsteadiness premise, reported not hidden).
  period_s          -- averaging-window length / n_periods (from detrended zero-crossings).
  S4 (part ii)      -- the dt-halving spot-check: True only if the spot-check marker is present; absent
                       -> S4 not satisfied (the SAFE direction -> analyse_t4f NOT A RESULTs).  Part (i)
                       (fixed dt <= probe CFL dt) is enforced by build_t4f (endTime/deltaT integer) +
                       the calibration probe.

BECAUSE THIS INSTRUMENT DECIDES A GATE, it carries a planted control: a reader not shown able to BOTH
confirm a stationary limit cycle AND reject a drifting or too-short signal is not evidence.
  ARM STAT  -- synthetic transient-then-stationary limit cycle -> S1 AND S2 MUST hold
  ARM DRIFT -- synthetic monotone drift across the window        -> S1 MUST fail
  ARM SHORT -- synthetic stationary but < N_MIN periods, not steady -> S2 MUST fail
  ARM DET   -- identical input twice -> identical classification (determinism)
Self-test must be green under python3 and python3 -O.

NO `assert` STATEMENT IN THIS FILE (L-332).

STATUS: DRAFT.  Not frozen.  Constants are prediction-first choices to confirm at the section-3 review
(T4f_PREREGISTRATION.md section 8, open question 5).
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T4 = os.path.join(os.path.dirname(HERE), "T4_runs")
sys.path.insert(0, T4)
import analyse_t4 as A          # noqa: E402  FROZEN peak_of / U_BULK / D

# registered prediction-first constants (T4f_PREREGISTRATION.md section 4b / 3)
T_INIT_S = 0.03
T_END_S = 0.08
N_MIN = 20
EPS_STAT = 1.0e-3               # U/U_bulk, 5% of the 0.02 band half-width
EPS_AVG = 1.0e-3
AMP_FLOOR = 5.0e-4             # ptp below this -> the windowed signal is STEADY (premise falsified)


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _ols(ts, ys):
    """(slope, intercept) of an OLS linear fit y ~ t."""
    n = len(ts)
    mt, my = _mean(ts), _mean(ys)
    den = sum((t - mt) ** 2 for t in ts)
    if den == 0.0:
        return 0.0, my
    slope = sum((t - mt) * (y - my) for t, y in zip(ts, ys)) / den
    return slope, my - slope * mt


def _sign_changes(resid):
    n = 0
    prev = 0
    for r in resid:
        s = (r > 0) - (r < 0)
        if s != 0:
            if prev != 0 and s != prev:
                n += 1
            prev = s
    return n


def classify(times, values, t_init=T_INIT_S):
    """Decide S1/S2, measure t_stat, period and n_periods from a peak time series (values already in
    U/U_bulk).  Deterministic and pure."""
    pairs = sorted(zip(times, values))
    times = [t for t, _ in pairs]
    values = [v for _, v in pairs]
    win = [(t, v) for t, v in pairs if t >= t_init]
    if len(win) < 8:
        return dict(S1=False, S2=False, t_stat_s=None, period_s=None, n_periods=0,
                    note="fewer than 8 samples in the averaging window")
    wt = [t for t, _ in win]
    wv = [v for _, v in win]
    mean_win = _mean(wv)

    # --- S1: t_stat (first time whose tail mean is within EPS_STAT of the window mean) + no net drift
    t_stat = None
    for i in range(len(times)):
        tail = values[i:]
        if len(tail) >= 8 and abs(_mean(tail) - mean_win) <= EPS_STAT:
            t_stat = times[i]
            break
    half = len(wv) // 2
    m1, m2 = _mean(wv[:half]), _mean(wv[half:])
    drift_ok = abs(m1 - m2) <= EPS_STAT
    S1 = drift_ok and (t_stat is not None) and (t_stat <= t_init + 1e-12)

    # --- period / n_periods from detrended zero-crossings over the window
    slope, icpt = _ols(wt, wv)
    resid = [v - (slope * t + icpt) for t, v in zip(wt, wv)]
    ptp = (max(resid) - min(resid)) if resid else 0.0
    steady = ptp < AMP_FLOOR
    n_sign = _sign_changes(resid)
    n_periods = n_sign / 2.0
    window_len = wt[-1] - wt[0]
    period_s = (window_len / n_periods) if n_periods > 0 else None

    # --- S2: running-average convergence AND (>= N_MIN periods OR steady)
    q = max(2, len(wv) // 4)
    conv = abs(_mean(wv[-q:]) - _mean(wv[-2 * q:-q])) <= EPS_AVG
    S2 = conv and (steady or n_periods >= N_MIN)

    return dict(S1=bool(S1), S2=bool(S2), t_stat_s=t_stat, period_s=period_s,
                n_periods=n_periods, steady=bool(steady), ptp=ptp, drift=abs(m1 - m2),
                running_mean_converged=bool(conv))


# ------------------------------------------------- reading the real series
def read_series(case_dir, r_over_d, tag):
    """Peak(|U|)/U_bulk at each sampled time for one G-row, from the sets FO output
    postProcessing/gLines/<t>/<tag>_U.xy (raw setFormat)."""
    root = os.path.join(case_dir, "postProcessing", "gLines")
    if not os.path.isdir(root):
        return [], []
    times, vals = [], []
    for tname in sorted(os.listdir(root), key=lambda s: float(s) if re.fullmatch(r"[0-9.eE+-]+", s) else 1e18):
        cand = [f for f in os.listdir(os.path.join(root, tname))
                if f.startswith(tag) and f.endswith(".xy")]
        if not cand:
            continue
        prof = []
        for line in open(os.path.join(root, tname, cand[0])):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split()
            if len(p) < 4:
                continue
            y = float(p[0])
            ux, uy, uz = float(p[1]), float(p[2]), float(p[3])
            prof.append((y / A.D, math.sqrt(ux * ux + uy * uy + uz * uz) / A.U_BULK))
        if prof:
            times.append(float(tname))
            vals.append(A.peak_of(prof)[0])
    return times, vals


def evaluate(case_dir, foam_bashrc, stations=(1.0, 2.0, 3.0)):
    """S1/S2/period for the case; S1/S2 hold only if EVERY graded station holds them.  S4 part (ii)
    (dt-halving spot check) is True only if its marker is present (safe direction)."""
    tags = {1.0: "G1", 2.0: "G2", 3.0: "G3"}
    per = {}
    s1_all = s2_all = True
    period = None
    t_stat = None
    n_periods = None
    for r in stations:
        ts, vs = read_series(case_dir, r, tags.get(r, "G%g" % r))
        if not ts:
            per[tags.get(r)] = dict(S1=False, S2=False, note="no sampled series on disk")
            s1_all = s2_all = False
            continue
        c = classify(ts, vs)
        per[tags.get(r)] = c
        s1_all = s1_all and c["S1"]
        s2_all = s2_all and c["S2"]
        period = c.get("period_s") if period is None else period
        t_stat = c.get("t_stat_s") if t_stat is None else t_stat
        n_periods = c.get("n_periods") if n_periods is None else n_periods
    s4 = os.path.isfile(os.path.join(case_dir, "DT_HALVING_SPOTCHECK_PASS"))
    return dict(S1=bool(s1_all), S2=bool(s2_all), S4=bool(s4),
                period_s=period, t_stat_s=t_stat, n_periods=n_periods, per_station=per)


# --------------------------------------------------------------- planted control (selftest)
def _synth(kind, dt=1.0e-4, t_end=T_END_S):
    """Synthetic peak series for the planted-control arms."""
    n = int(t_end / dt)
    ts = [i * dt for i in range(n + 1)]
    out = []
    base = 1.08
    f_high = N_MIN / (t_end - T_INIT_S)        # exactly N_MIN periods in the window
    f_low = 4.0 / (t_end - T_INIT_S)           # only 4 periods in the window (< N_MIN)
    for t in ts:
        trans = 0.5 * math.exp(-t / 0.006)     # initial transient, decays well before T_init=0.03
        if kind == "STAT":                     # transient then stationary limit cycle, N_MIN periods
            v = base + trans + 0.02 * math.sin(2 * math.pi * f_high * t)
        elif kind == "DRIFT":                  # monotone drift across the whole window
            v = base + trans + 0.6 * t         # rises ~0.048 over [0.03,0.08] >> EPS_STAT
        elif kind == "SHORT":                  # stationary but only 4 periods, not steady
            v = base + trans + 0.02 * math.sin(2 * math.pi * f_low * t)
        else:
            v = base
        out.append(v)
    return ts, out


def selftest():
    fails = []

    def expect(name, cond):
        print("  [%s] %s" % ("ok " if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    print("stationarity_t4f selftest (planted control on the windowed classifier):")
    ts, vs = _synth("STAT")
    c = classify(ts, vs)
    expect("ARM STAT: S1 True (t_stat=%.4g <= %.3g)" % (c["t_stat_s"] or -1, T_INIT_S), c["S1"])
    expect("ARM STAT: S2 True (n_periods=%.1f >= %d)" % (c["n_periods"], N_MIN), c["S2"])

    ts, vs = _synth("DRIFT")
    c = classify(ts, vs)
    expect("ARM DRIFT: S1 False (drift=%.4g > EPS_STAT)" % c["drift"], not c["S1"])

    ts, vs = _synth("SHORT")
    c = classify(ts, vs)
    expect("ARM SHORT: S2 False (n_periods=%.1f < %d, not steady)" % (c["n_periods"], N_MIN), not c["S2"])

    ts, vs = _synth("STAT")
    c1, c2 = classify(ts, vs), classify(list(ts), list(vs))
    expect("ARM DET: identical input -> identical (S1,S2,t_stat)",
           (c1["S1"], c1["S2"], c1["t_stat_s"]) == (c2["S1"], c2["S2"], c2["t_stat_s"]))

    import ast
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    expect("AST assert count = 0", n_assert == 0)
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else 0)
