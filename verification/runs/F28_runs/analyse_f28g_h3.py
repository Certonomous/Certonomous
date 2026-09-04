#!/usr/bin/env python3
"""F28G L1 -- the H3 equilibration comparator.

WHAT H3 ASKS
------------
`verification/campaign/F28G_L1_RESIDUAL_RECONCILIATION.md` section 6.2 states
H3 as: *"the operating point never equilibrated; the mass flow is still
drifting"*, and names its separating measurement as *"fit an exponential to the
`postProcessing/diskFlow` `areaNormalIntegrate(planeFlow) of U` series already
on disk"*.  That document's ADDENDUM 1 (2026-09-04) makes this item 1 of the
superseded order and records that H3 is UNRESOLVED -- neither confirmed nor
retired.

This file is that measurement and NOTHING ELSE.  It does not re-grade
`F28G_L1_dp1000_U20`, which stands at NOT A RESULT on the two grounds
registered in commit 23eeff7e.  A diagnostic hypothesis is not a verdict.

WHAT AN "EXPONENTIAL FIT" HAS TO SURVIVE BEFORE IT MAY BE QUOTED
----------------------------------------------------------------
Fitting `y(t) = A + B*exp(-(t-t0)/tau)` to a monotone-looking series ALWAYS
returns some (A, B, tau).  The fit is evidence only if the model is the right
one, and the cheap test for that is whether the answer stays put when the data
window is changed.  A genuine exponential relaxation gives an asymptote A that
does not move as more data is appended and a tau that does not depend on where
the window starts.  A slower-than-exponential decay (algebraic / power law)
gives the opposite: tau grows without bound as the window start is pushed
later, and A runs away with it.  That failure mode is the reason this file
declines to quote an asymptote instead of quoting one that is an artifact.

Two adequacy tests are therefore applied BEFORE any asymptote is reported, and
their thresholds are fixed here in source:

  A-1  END-TRUNCATION STABILITY.  Refit on t <= f*T for f in END_FRACTIONS.
       The relative spread of A across those refits must be <= A_STABLE_TOL.
       An asymptote that walks as data is added is not an asymptote.

  A-2  START-SWEEP STABILITY.  Refit with window start f*T for f in
       START_FRACTIONS.  max(tau)/min(tau) must be <= TAU_RATIO_TOL.
       tau growing monotonically with the window start is the power-law tell.

A series failing either test is reported EXPONENTIAL MODEL NOT SUPPORTED, and
NO asymptote and NO "fraction still to go" is quoted for it.  That is the
honest outcome and it is neither "settled" nor "still drifting".

A series passing both is then SETTLED only if BOTH
  (t_end - t_window_start)/tau >= SETTLED_TAUS          (enough elapsed)
  |B*exp(-(t_end-t0)/tau)| / |A| <= SETTLED_RESIDUAL    (little left)
and otherwise NOT SETTLED, with the elapsed tau count and the residual
transient printed beside it.

Because a series can be exponentially settled and still carry a slow secular
drift that the exponential model does not describe, the tail is separately
tested for a linear trend, with an autocorrelation-aware standard error
(Newey--West).  Iterative monitor series are heavily autocorrelated -- the
lag-1 autocorrelation of this run's tail is above 0.99 -- so an OLS standard
error would overstate significance by more than an order of magnitude.  The
integrated autocorrelation time is measured and the effective sample size is
printed beside every slope.

PLANTED CONTROLS (standing rule 3)
----------------------------------
A "settled" reading, and a "no drift" reading, are both ZEROES.  A zero from a
reader not shown able to see a non-zero is not evidence.  Every plant below is
WRITTEN TO DISK in the real OpenFOAM `surfaceFieldValue.dat` layout and READ
BACK through the same `load_series()` the real data goes through, so the header
parser, the window filter and the fitter are all exercised on the plant.

  C-P1  analytic exponential, known (A, B, tau), no noise
          -> tau recovered to <= PLANT_TAU_TOL, model ADEQUATE
  C-P2  A KNOWN EXPONENTIAL CARRIED ON THIS RUN'S OWN NOISE.  This is the
        control that matters: it proves the reader can see a transient of a
        stated size THROUGH THIS RUN'S OWN FLUCTUATIONS, at this run's own
        sampling and autocorrelation.  A "settled" verdict on the unplanted
        series is worthless without it.

        ⚠ The noise is taken as the REAL diskFlow series MINUS ITS OWN FITTED
        EXPONENTIAL, not as the raw series.  Superposing a plant on the raw
        series plants a SECOND exponential beside the one already there, and a
        single-exponential fit to two exponentials returns neither -- measured:
        a tau=1200 plant on a series whose own tau is 2075 came back as 2579.
        That is the fitter behaving correctly and the CONTROL being wrong, so
        the control was corrected rather than the tolerance widened.
          -> the recovered tau must sit within PLANT_TAU_TOL of the planted one

  C-P2b DETECTION FLOOR.  The same plant swept down in amplitude until the
        reader loses it.  This is what licenses the zero: it converts "no
        transient was found" into "a transient of amplitude >= B_min WOULD
        have been found, and none was."  The floor is printed beside every
        SETTLED verdict.
  C-P3  NULL: a constant plus noise, no transient at all
          -> must NOT be reported as carrying a resolvable transient
  C-P4  power law y = A + B*(t-t0+c)^(-q), a decay that is NOT exponential
          -> the adequacy tests MUST reject it.  If they pass it, the
             adequacy tests do not discriminate and the whole file is void.
  C-P5  pre-window garbage in every plant, so a broken window filter cannot
        pass any plant.

  C-M1  MUTATION: adequacy always returns True.  C-P4 must then go green,
        and the suite MUST go red.  A control suite that cannot be broken is
        not testing anything.

EXIT CODES
  0   all controls green / measurement produced
  2   EXIT_REFUSE  -- a registered refusal: a control failed, or the reader
                      declined to answer.  NOT a crash.
 70   EXIT_INSTRUMENT_ERROR -- internal error.  A CRASH IS NOT A REFUSAL.
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tempfile

import numpy as np

EXIT_OK = 0
EXIT_REFUSE = 2
EXIT_INSTRUMENT_ERROR = 70


class InstrumentError(Exception):
    pass


class Refusal(Exception):
    pass


# ---------------------------------------------------------------- thresholds
# Fixed here in source.  Every one of them is quoted in the report this file
# produces, so a reader can see what the verdict was tested against.

A_STABLE_TOL = 0.01        # A-1: relative spread of the asymptote, end-truncation
TAU_RATIO_TOL = 2.0        # A-2: max(tau)/min(tau) across window starts
END_FRACTIONS = (0.55, 0.70, 0.80, 0.90, 1.00)
START_FRACTIONS = (0.00, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40)

# WHERE THE RELAXATION STARTS, and why it is not iteration 1.
#
# An exponential relaxation is MONOTONE.  This run's diskFlow series is not
# monotone from the beginning: it RISES from 1.1896e-02 to a maximum of
# 2.3737e-02 at iteration 182 and only then decays.  Fitting one decaying
# exponential across a rise-then-decay does not measure the decay -- measured:
# fitting from iteration 1 returned tau = 24.97 with B = -1.06e-02, which is a
# fit to the STARTUP, and it made the start sweep meaningless because the early
# window starts were fitting a different feature from the late ones.
#
# Registered rule, applied to every series alike: smooth with a centred moving
# average of SMOOTH_WINDOW samples, and begin the fit at the smoothed series'
# EXTREMUM FURTHEST FROM ITS FINAL LEVEL, provided that excursion beats the
# tail noise by EXTREMUM_SIGMA.  A series monotone throughout, and a series of
# pure noise, both start at their first sample.  This is determined by the
# SHAPE of the data, never by the answer: nothing in the rule can see the
# asymptote, the drift or the verdict.
SMOOTH_WINDOW = 201
EXTREMUM_SIGMA = 6.0

SETTLED_TAUS = 5.0         # elapsed window must be >= 5 time constants
SETTLED_RESIDUAL = 1.0e-3  # |remaining transient| / |A|

PLANT_TAU_TOL = 0.05       # 5% on a recovered time constant
PLANT_AMP_TOL = 0.10       # 10% on a recovered transient amplitude

# A-2's DETECTION FLOOR, and why A-2 cannot be evaluated without one.
#
# A window that contains no transient cannot measure a time constant.  Its tau
# is UNIDENTIFIABLE, not divergent, and folding it into max(tau)/min(tau) makes
# A-2 reject exactly the series it should accept.
#
# ⚠ This is not a supposition.  A KNOWN, exactly exponential, fully settled
# series carried on THIS RUN'S OWN correlated noise (control C-P7) was rejected
# by A-2 with tau ratios of 17.4 (planted tau 1500) and 9.9 (planted tau 2000),
# and in both cases the whole of the damage came from the two latest windows,
# whose fitted |B|/|A| had fallen to 2.6e-03 … 7.2e-03.  C-P2b independently
# measures this reader's detection floor on this run's noise at 4.64e-03 of the
# level.  Those are the same number.
#
# Registered: a start window whose fitted |B|/|A| is below DETECT_FLOOR_REL is
# EXCLUDED from A-2 and reported as excluded.  C-P2b asserts that the measured
# floor is at or below this constant, so the constant is tied to a control and
# not to an answer.  At least MIN_A2_WINDOWS must survive or A-2 is refused.
DETECT_FLOOR_REL = 5.0e-3
MIN_A2_WINDOWS = 3
PLANT_GARBAGE = -9.99e9    # C-P5: what sits BEFORE the window in every plant

TAU_GRID_LO = 5.0          # bracket for the tau search, in iterations
TAU_GRID_HI = 1.0e7

CASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "F28G_L1_dp1000_U20")

# The series H3 names, plus the four other monitors written by the same run.
# The force channels are included because section 6.2's *measured support* for
# H3 is a force drift, not a flow drift, and the two must be read together.
SERIES = (
    ("diskFlow", "postProcessing/diskFlow/0/surfaceFieldValue.dat", 1,
     "areaNormalIntegrate(U) -- THE SERIES H3 NAMES"),
    ("diskPlaneUp", "postProcessing/diskPlaneUp/0/surfaceFieldValue.dat", 1,
     "upstream plane"),
    ("diskPlaneDown", "postProcessing/diskPlaneDown/0/surfaceFieldValue.dat", 1,
     "downstream plane"),
    ("forcesDuct_total_x", "postProcessing/forcesDuct/0/force.dat", 1,
     "duct total_x -- section 6.2's measured support for H3"),
    ("forcesHub_total_x", "postProcessing/forcesHub/0/force.dat", 1,
     "hub total_x"),
)


def _require(cond, msg, exc=InstrumentError):
    if not cond:
        raise exc(msg)


# ------------------------------------------------------------------- reading

_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def load_series(path, column=1):
    """(times, values) from an OpenFOAM function-object .dat.

    Handles both the plain two-column `surfaceFieldValue.dat` and the
    parenthesised vector layout of `force.dat`.  EVERY plant is read back
    through this function (C-P5), so the header skip and the numeric parse are
    themselves under control.
    """
    _require(os.path.isfile(path), "no such series file: %s" % path, Refusal)
    times, vals, nhdr = [], [], 0
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                nhdr += 1
                continue
            if not line.strip():
                continue
            nums = _NUM.findall(line.replace("(", " ").replace(")", " "))
            if len(nums) < column + 1:
                continue
            times.append(float(nums[0]))
            vals.append(float(nums[column]))
    _require(nhdr > 0, "%s carried no header lines -- this is not an OpenFOAM "
                       "function-object file, or the parser missed them" % path)
    _require(len(times) >= 50, "%s holds only %d data rows; a relaxation fit on "
                                "fewer than 50 is not a result" % (path, len(times)),
             Refusal)
    t = np.asarray(times, float)
    y = np.asarray(vals, float)
    _require(np.all(np.diff(t) > 0), "%s times are not strictly increasing -- a "
                                      "restart collision would look like this" % path,
             Refusal)
    _require(np.all(np.isfinite(y)), "%s holds non-finite values" % path, Refusal)
    return t, y


# ------------------------------------------------------------------- fitting

def fit_exponential(t, y, ngrid=400, nrefine=60):
    """Least squares on y = A + B*exp(-(t-t[0])/tau).

    (A, B) are linear for fixed tau, so tau is found by a log-spaced grid
    followed by a golden-section refinement -- no initial guess to get wrong,
    and no optimiser that can silently return its starting point.
    """
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    t0 = t[0]

    def ssq(tau):
        X = np.column_stack([np.ones_like(t), np.exp(-(t - t0) / tau)])
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ c
        return float(r @ r), c

    grid = np.exp(np.linspace(math.log(TAU_GRID_LO), math.log(TAU_GRID_HI), ngrid))
    vals = [ssq(g)[0] for g in grid]
    i = int(np.argmin(vals))
    lo = grid[max(i - 1, 0)]
    hi = grid[min(i + 1, ngrid - 1)]

    # golden section on log(tau)
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = math.log(lo), math.log(hi)
    c1, c2 = b - gr * (b - a), a + gr * (b - a)
    f1, f2 = ssq(math.exp(c1))[0], ssq(math.exp(c2))[0]
    for _ in range(nrefine):
        if f1 < f2:
            b, c2, f2 = c2, c1, f1
            c1 = b - gr * (b - a)
            f1 = ssq(math.exp(c1))[0]
        else:
            a, c1, f1 = c1, c2, f2
            c2 = a + gr * (b - a)
            f2 = ssq(math.exp(c2))[0]
    tau = math.exp((a + b) / 2.0)
    s, c = ssq(tau)
    n = len(t)
    return {"tau": tau, "A": float(c[0]), "B": float(c[1]),
            "rms": math.sqrt(s / n), "n": n, "t0": t0,
            "t_end": float(t[-1]),
            "at_bracket": tau <= TAU_GRID_LO * 1.01 or tau >= TAU_GRID_HI * 0.99}


def relaxation_start(t, y):
    """Index at which the monotone relaxation begins.

    The smoothed series' extremum FURTHEST FROM ITS FINAL LEVEL.  A series that
    rises and then decays starts at its peak; a series that is monotone
    throughout starts at its first sample; a series of pure noise has no
    significant extremum and also starts at its first sample.

    ⚠ A first version of this took the LAST turning point of the smoothed
    slope.  That was wrong and the controls caught it: a noisy plateau has many
    smoothed turning points, and on C-P6 (planted turning point at 900) it put
    the fit start at 7,501 -- discarding half the record.  The excursion of the
    chosen extremum must therefore beat the tail noise by EXTREMUM_SIGMA, or
    there is no turning point to find.
    """
    n = len(y)
    w = min(SMOOTH_WINDOW, max(3, n // 20))
    if w % 2 == 0:
        w += 1
    ys = np.convolve(y, np.ones(w) / w, mode="valid")   # 'valid': no edge pad
    off = w // 2
    j = int(np.argmax(np.abs(ys - ys[-1])))
    excursion = float(abs(ys[j] - ys[-1]))
    tail_noise = float(np.std(ys[-max(len(ys) // 4, 10):]))
    if j == 0 or excursion < EXTREMUM_SIGMA * tail_noise:
        return 0
    return int(min(j + off, int(0.5 * n)))


def adequacy(t, y, mutate=False):
    """A-1 and A-2.  Returns (ok, detail).  `mutate` is control C-M1."""
    T0, T1 = t[0], t[-1]
    span = T1 - T0

    ends = []
    for f in END_FRACTIONS:
        m = t <= T0 + f * span
        if m.sum() < 50:
            continue
        ends.append((f, fit_exponential(t[m], y[m])))
    _require(len(ends) >= 3, "end-truncation sweep produced %d usable refits; "
                              "A-1 cannot be evaluated" % len(ends), Refusal)
    As = np.array([e[1]["A"] for e in ends])
    scale = np.max(np.abs(As))
    a_spread = float((As.max() - As.min()) / scale) if scale > 0 else float("inf")

    starts = []
    for f in START_FRACTIONS:
        m = t >= T0 + f * span
        if m.sum() < 50:
            continue
        starts.append((f, fit_exponential(t[m], y[m])))
    _require(len(starts) >= MIN_A2_WINDOWS,
             "start sweep produced %d usable refits; A-2 cannot be evaluated"
             % len(starts), Refusal)

    # Exclude windows with no transient left in them.  See DETECT_FLOOR_REL.
    # ⚠ The screening quantity is the decay the fit claims actually HAPPENED
    # inside the window -- |B|*(1 - exp(-window_span/tau)) -- not the bare
    # coefficient |B|.  Measured reason: when tau runs away to the grid ceiling
    # the fit degenerates into a straight line, and it represents that line
    # with a HUGE B (5.7e-03 against a level of 2.16e-02 in control C-P2b's
    # smallest plant).  Screening on |B| therefore keeps exactly the degenerate
    # windows the floor exists to drop.  The resolved decay of that same
    # degenerate fit is 3.96e-04 of the level -- correctly below the floor.
    def _resolved(fit):
        if abs(fit["A"]) <= 0:
            return 0.0
        w_span = fit["t_end"] - fit["t0"]
        return (abs(fit["B"]) * (1.0 - math.exp(-w_span / fit["tau"]))
                / abs(fit["A"]))

    kept = [s for s in starts if _resolved(s[1]) >= DETECT_FLOOR_REL]
    n_excluded = len(starts) - len(kept)

    # Too few windows carry a transient at all.  That is NOT an instrument
    # failure and is NOT refused: it is the statement that no transient above
    # the detection floor exists anywhere in the record.  A-2 is marked
    # not-evaluable and the caller reports that state by name.
    if len(kept) < MIN_A2_WINDOWS:
        return False, {"a_spread": a_spread, "tau_ratio": float("nan"),
                       "ok_a1": a_spread <= A_STABLE_TOL, "ok_a2": None,
                       "a2_evaluable": False,
                       "ends": ends, "starts": starts, "kept": kept,
                       "n_excluded": n_excluded,
                       "tau_monotone_increasing": False}

    taus = np.array([s[1]["tau"] for s in kept])
    tau_ratio = float(taus.max() / taus.min())

    ok_a1 = a_spread <= A_STABLE_TOL
    ok_a2 = tau_ratio <= TAU_RATIO_TOL
    ok = bool(ok_a1 and ok_a2)
    if mutate:                                    # C-M1
        ok = True
    return ok, {"a_spread": a_spread, "tau_ratio": tau_ratio,
                "ok_a1": ok_a1, "ok_a2": ok_a2, "a2_evaluable": True,
                "ends": ends, "starts": starts, "kept": kept,
                "n_excluded": n_excluded,
                "tau_monotone_increasing": bool(np.all(np.diff(taus) > 0))}


# --------------------------------------------------- autocorrelation & drift

def integrated_autocorr(r):
    r = np.asarray(r, float)
    r = r - r.mean()
    n = len(r)
    ac = np.correlate(r, r, "full")[n - 1:]
    if ac[0] <= 0:
        return 1.0, ac
    ac = ac / ac[0]
    ti = 1.0
    for M in range(1, n // 4):
        ti = 1.0 + 2.0 * float(ac[1:M + 1].sum())
        if M >= 6.0 * ti:
            break
    return max(ti, 1.0), ac


def newey_west_slope(t, y, lag):
    X = np.column_stack([np.ones_like(t), t])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b
    XtXi = np.linalg.inv(X.T @ X)
    u = X * r[:, None]
    S = u.T @ u
    for l in range(1, lag + 1):
        w = 1.0 - l / (lag + 1.0)
        G = u[l:].T @ u[:-l]
        S = S + w * (G + G.T)
    V = XtXi @ S @ XtXi
    return float(b[1]), float(math.sqrt(max(V[1, 1], 0.0)))


def tail_drift(t, y, frac=0.5):
    m = t >= t[0] + frac * (t[-1] - t[0])
    tt, yy = t[m], y[m]
    c = np.polyfit(tt, yy, 1)
    resid = yy - np.polyval(c, tt)
    ti, _ = integrated_autocorr(resid)
    lag = int(min(max(4.0 * ti, 20), len(tt) // 5))
    slope, se = newey_west_slope(tt, yy, lag)
    return {"n": int(m.sum()), "tau_int": ti, "n_eff": len(tt) / ti,
            "slope": slope, "se": se,
            "sigma": abs(slope) / se if se > 0 else float("inf"),
            "t_lo": float(tt[0]),
            "over_run": slope * (t[-1] - t[0]),
            "level": float(np.mean(yy))}


# ------------------------------------------------------------------ verdicts

def assess(t, y, mutate=False):
    # The fit, and both adequacy sweeps, start at the relaxation point --
    # never at iteration 1 on a series that rises first.  See SMOOTH_WINDOW.
    k = relaxation_start(t, y)
    tr, yr = t[k:], y[k:]
    fit = fit_exponential(tr, yr)
    ok, det = adequacy(tr, yr, mutate=mutate)
    det["relax_index"] = k
    det["relax_t"] = float(t[k])
    span = fit["t_end"] - fit["t0"]
    out = {"fit": fit, "adequacy": det, "adequate": ok,
           "drift": tail_drift(t, y)}
    if not ok:
        out["verdict"] = ("NO TRANSIENT ABOVE DETECTION FLOOR"
                          if not det.get("a2_evaluable", True)
                          else "EXPONENTIAL MODEL NOT SUPPORTED")
        out["taus_elapsed"] = None
        out["residual_transient"] = None
        return out
    taus_elapsed = span / fit["tau"]
    resid = abs(fit["B"]) * math.exp(-span / fit["tau"])
    rel = resid / abs(fit["A"]) if fit["A"] != 0 else float("inf")
    out["taus_elapsed"] = taus_elapsed
    out["residual_transient"] = rel
    out["verdict"] = ("SETTLED"
                      if (taus_elapsed >= SETTLED_TAUS and rel <= SETTLED_RESIDUAL)
                      else "NOT SETTLED")
    return out


# -------------------------------------------------------------------- plants

def write_plant(path, t, y):
    """Write (t, y) in the real surfaceFieldValue.dat layout, with C-P5
    pre-window garbage ahead of it."""
    dt = t[1] - t[0]
    with open(path, "w") as fh:
        fh.write("# Region type :   sampledSurface planted\n")
        fh.write("# Faces           : 96\n")
        fh.write("# Area            : 5.9265905021e-04\n")
        fh.write("# Scale factor    : 1.0000000000e+00\n")
        fh.write("# Time            \tplantedValue\n")
        for k in range(20, 0, -1):                       # C-P5
            fh.write("%.10g\t%.12e\n" % (t[0] - k * dt, PLANT_GARBAGE))
        for tt, yy in zip(t, y):
            fh.write("%.10g\t%.12e\n" % (tt, yy))


def _read_plant(path, t_start):
    t, y = load_series(path, 1)
    m = t >= t_start
    _require(np.any(y[~m] == PLANT_GARBAGE) or (~m).sum() == 0,
             "C-P5: the pre-window garbage rows are missing from %s -- the plant "
             "was not written as specified" % path)
    return t[m], y[m]


def selftest(verbose=True):
    rng = np.random.default_rng(20260904)
    fails = []

    def say(tag, ok, msg):
        if verbose:
            print("  %-58s %s   %s" % (tag, "ok  " if ok else "FAIL", msg))
        if not ok:
            fails.append(tag)

    tmp = tempfile.mkdtemp(prefix="f28g_h3_plant_")
    N = 15000
    t = np.arange(1.0, N + 1.0)

    # ---- C-P1 clean analytic exponential -------------------------------
    A0, B0, TAU0 = 2.0e-2, 3.0e-3, 1500.0
    p1 = os.path.join(tmp, "P1.dat")
    write_plant(p1, t, A0 + B0 * np.exp(-(t - t[0]) / TAU0))
    tp, yp = _read_plant(p1, t[0])
    r = assess(tp, yp)
    e_tau = abs(r["fit"]["tau"] - TAU0) / TAU0
    e_A = abs(r["fit"]["A"] - A0) / abs(A0)
    say("C-P1 clean exponential tau=%g [tau recovered]" % TAU0,
        e_tau <= PLANT_TAU_TOL,
        "got tau=%.4f expected %.1f  rel.err %.2e  tol %g"
        % (r["fit"]["tau"], TAU0, e_tau, PLANT_TAU_TOL))
    say("C-P1 clean exponential [asymptote recovered]",
        e_A <= PLANT_TAU_TOL,
        "got A=%.8e expected %.8e  rel.err %.2e" % (r["fit"]["A"], A0, e_A))
    say("C-P1 clean exponential [model judged ADEQUATE]", r["adequate"],
        "a_spread=%.3e (tol %g)  tau_ratio=%.3f (tol %g)"
        % (r["adequacy"]["a_spread"], A_STABLE_TOL,
           r["adequacy"]["tau_ratio"], TAU_RATIO_TOL))
    say("C-P1 clean exponential [verdict SETTLED at 10 tau]",
        r["verdict"] == "SETTLED", "verdict=%s  taus_elapsed=%.2f"
        % (r["verdict"], r["taus_elapsed"] or float("nan")))

    # ---- C-P2 a known exponential ON THIS RUN'S OWN NOISE -----------------
    # See the docstring.  The carrier must itself be NULL before anything is
    # planted into it, and C-P2a proves that rather than assuming it.
    #
    # ⚠ The obvious carrier -- the real series minus its own full-record
    # exponential fit -- is NOT null, and this suite measured it so.  The
    # record's startup (a rise to a maximum at iteration 182, then decay) is
    # not describable by one decaying exponential, so the residual keeps an
    # exponential-shaped remnant of amplitude ~1.34e-3.  Planted into that,
    # every recovered amplitude came back ~1.34e-3 whatever was planted --
    # the tell of a carrier that is not noise.  The carrier is therefore
    # built from the TAIL, where the record's own transient is dead:
    # the linear-detrended residual of t >= CARRIER_T0, mirrored to full
    # length so the run's own autocorrelation is preserved.
    real = os.path.join(CASE, SERIES[0][1])
    tr, yr = load_series(real, 1)
    f_real = fit_exponential(tr[tr >= 1000], yr[tr >= 1000])

    CARRIER_T0 = 8000.0
    mt = tr >= CARRIER_T0
    ctail = yr[mt] - np.polyval(np.polyfit(tr[mt], yr[mt], 1), tr[mt])
    reps = int(np.ceil(len(tr) / len(ctail)))
    tiled = np.concatenate([ctail if k % 2 == 0 else ctail[::-1]
                            for k in range(reps)])[:len(tr)]
    LEVEL = float(f_real["A"])
    carrier = LEVEL + tiled

    # C-P2a: the carrier is NULL.  Assert it before planting into it.
    p2a = os.path.join(tmp, "P2a_carrier.dat")
    write_plant(p2a, tr, carrier)
    tc, yc = _read_plant(p2a, tr[0])
    r2a = assess(tc, yc)
    carrier_B = abs(r2a["fit"]["B"])
    say("C-P2a carrier is NULL before planting [no transient in it]",
        r2a["verdict"] == "NO TRANSIENT ABOVE DETECTION FLOOR",
        "carrier rms=%.4e (%.3f%% of level %.6e); verdict on the BARE carrier "
        "= %s (%d of %d start windows below the floor). Every plant below is "
        "measured against this."
        % (np.std(tiled), 100.0 * np.std(tiled) / abs(LEVEL), LEVEL,
           r2a["verdict"], r2a["adequacy"]["n_excluded"],
           len(r2a["adequacy"]["starts"])))

    for TAUP, BP in ((1200.0, 5.0e-4), (2000.0, 5.0e-4), (4000.0, 2.0e-3)):
        p2 = os.path.join(tmp, "P2_tau%g.dat" % TAUP)
        write_plant(p2, tr, carrier + BP * np.exp(-(tr - tr[0]) / TAUP))
        tp, yp = _read_plant(p2, tr[0])
        r2 = assess(tp, yp)
        e_tau = abs(r2["fit"]["tau"] - TAUP) / TAUP
        say("C-P2 planted exp on REAL noise (tau=%g, B=%g) [tau seen]"
            % (TAUP, BP), e_tau <= PLANT_TAU_TOL,
            "got tau=%.2f expected %.1f  rel.err %.2e  tol %g"
            % (r2["fit"]["tau"], TAUP, e_tau, PLANT_TAU_TOL))
        e_amp = abs(r2["fit"]["B"] - BP) / BP
        say("C-P2 planted exp on REAL noise (tau=%g) [amplitude seen]" % TAUP,
            e_amp <= PLANT_AMP_TOL,
            "got B=%.4e expected %.4e  rel.err %.2e  tol %g"
            % (r2["fit"]["B"], BP, e_amp, PLANT_AMP_TOL))

    # ---- C-P2b DETECTION FLOOR -------------------------------------------
    # Sweep the planted amplitude down at the real series' own tau until the
    # reader loses it.  This number is what licenses the zero: it converts
    # "no further transient was found" into "a transient this size or larger
    # WOULD have been found."
    floor = None
    for BP in (2.0e-3, 1.0e-3, 5.0e-4, 2.0e-4, 1.0e-4, 5.0e-5, 2.0e-5, 1.0e-5):
        p = os.path.join(tmp, "P2b_%g.dat" % BP)
        write_plant(p, tr, carrier + BP * np.exp(-(tr - tr[0]) / f_real["tau"]))
        tp, yp = _read_plant(p, tr[0])
        rb = assess(tp, yp)
        got = (abs(rb["fit"]["tau"] - f_real["tau"]) / f_real["tau"] <= 0.25
               and abs(rb["fit"]["B"] - BP) / BP <= 0.25)
        if got:
            floor = BP
        if verbose:
            print("      C-P2b B=%9.2e -> tau=%9.2f B_hat=%10.3e   %s"
                  % (BP, rb["fit"]["tau"], rb["fit"]["B"],
                     "RECOVERED" if got else "lost"))
    say("C-P2b floor is at or below the registered DETECT_FLOOR_REL",
        floor is not None and floor / abs(LEVEL) <= DETECT_FLOOR_REL,
        "measured floor %s of the level; registered constant %g -- A-2's "
        "window exclusion is tied to THIS measurement"
        % ("none" if floor is None else "%.3e" % (floor / abs(LEVEL)),
           DETECT_FLOOR_REL))
    say("C-P2b detection floor established", floor is not None,
        "smallest recovered planted amplitude = %s  (%.4f%% of the level) -- "
        "a transient at or above this WOULD have been seen"
        % ("none" if floor is None else "%.2e" % floor,
           0.0 if floor is None else 100.0 * floor / abs(LEVEL)))

    # ---- C-P3 NULL: constant + noise ------------------------------------
    p3 = os.path.join(tmp, "P3.dat")
    noise = rng.normal(0.0, 3.0e-5, N)
    write_plant(p3, t, A0 + noise)
    tp, yp = _read_plant(p3, t[0])
    r3 = assess(tp, yp)
    resid3 = r3["residual_transient"]
    say("C-P3 NULL constant+noise [no resolvable transient]",
        (not r3["adequate"]) or (resid3 is not None and resid3 <= SETTLED_RESIDUAL),
        "verdict=%s residual_transient=%s"
        % (r3["verdict"], "n/a" if resid3 is None else "%.3e" % resid3))
    say("C-P3 NULL constant+noise [drift NOT called significant]",
        r3["drift"]["sigma"] < 3.0,
        "slope=%.3e  NW se=%.3e  %.2f sigma  n_eff=%.1f"
        % (r3["drift"]["slope"], r3["drift"]["se"], r3["drift"]["sigma"],
           r3["drift"]["n_eff"]))

    # ---- C-P4 power law: the adequacy tests MUST reject it ---------------
    p4 = os.path.join(tmp, "P4.dat")
    c, q = 50.0, 0.45
    write_plant(p4, t, A0 - 4.0e-3 * (t - t[0] + c) ** (-q) * c ** q * -1.0)
    yp4 = A0 + 4.0e-3 * ((t - t[0] + c) / c) ** (-q)
    write_plant(p4, t, yp4)
    tp, yp = _read_plant(p4, t[0])
    r4 = assess(tp, yp)
    say("C-P4 power law q=%.2f [adequacy REJECTS it]" % q, not r4["adequate"],
        "verdict=%s  a_spread=%.3e (tol %g)  tau_ratio=%.2f (tol %g)"
        % (r4["verdict"], r4["adequacy"]["a_spread"], A_STABLE_TOL,
           r4["adequacy"]["tau_ratio"], TAU_RATIO_TOL))
    say("C-P4 power law [no asymptote quoted]",
        r4["residual_transient"] is None,
        "residual_transient=%s" % r4["residual_transient"])

    # ---- C-P7 A SETTLED EXPONENTIAL ON THIS RUN'S OWN NOISE --------------
    # The control that forced DETECT_FLOOR_REL to exist.  These series ARE
    # exponential and ARE settled by construction, so a reader that calls them
    # "EXPONENTIAL MODEL NOT SUPPORTED" is broken.  Before the floor existed
    # this suite measured exactly that: tau ratios of 17.4 and 9.9.
    for TAU7 in (1500.0, 2000.0):
        p7 = os.path.join(tmp, "P7_tau%g.dat" % TAU7)
        write_plant(p7, tr, carrier + 1.3e-3 * np.exp(-(tr - tr[0]) / TAU7))
        tp, yp = _read_plant(p7, tr[0])
        r7 = assess(tp, yp)
        say("C-P7 SETTLED exponential (tau=%g) on this run's noise [ADEQUATE]"
            % TAU7, r7["adequate"],
            "A-1 %.3e (tol %g) %s ; A-2 ratio %.2f (tol %g) %s ; %d of %d "
            "start windows excluded below the %g floor"
            % (r7["adequacy"]["a_spread"], A_STABLE_TOL,
               "PASS" if r7["adequacy"]["ok_a1"] else "FAIL",
               r7["adequacy"]["tau_ratio"], TAU_RATIO_TOL,
               "PASS" if r7["adequacy"]["ok_a2"] else "FAIL",
               r7["adequacy"]["n_excluded"], len(r7["adequacy"]["starts"]),
               DETECT_FLOOR_REL))
        say("C-P7 SETTLED exponential (tau=%g) [verdict SETTLED]" % TAU7,
            r7["verdict"] == "SETTLED",
            "verdict=%s  tau=%.1f (planted %g)  taus_elapsed=%s"
            % (r7["verdict"], r7["fit"]["tau"], TAU7,
               "n/a" if r7["taus_elapsed"] is None
               else "%.2f" % r7["taus_elapsed"]))

    # ---- C-P6 RISE-THEN-DECAY: the startup must not be fitted ------------
    # This run's diskFlow series rises to a maximum at iteration 182 before it
    # decays.  A reader that fits from iteration 1 measures the startup and
    # reports a tau two orders too small -- measured, before relaxation_start()
    # existed: tau = 24.97 instead of ~2000.  This plant has a KNOWN turning
    # point and a KNOWN decay, and the reader must find the decay.
    TP, TAU6, B6, A6 = 900.0, 2500.0, 3.0e-3, 2.0e-2
    y6 = np.where(t <= TP,
                  A6 + B6 * (t - t[0]) / (TP - t[0]),
                  A6 + B6 * np.exp(-(t - TP) / TAU6))
    p6 = os.path.join(tmp, "P6.dat")
    write_plant(p6, t, y6 + rng.normal(0.0, 2.0e-5, len(t)))
    tp, yp = _read_plant(p6, t[0])
    r6 = assess(tp, yp)
    e6 = abs(r6["fit"]["tau"] - TAU6) / TAU6
    say("C-P6 rise-to-%g-then-decay(tau=%g) [turning point found]"
        % (TP, TAU6), abs(r6["adequacy"]["relax_t"] - TP) <= 0.15 * TP,
        "relaxation_start put the fit at t=%g, planted turning point %g"
        % (r6["adequacy"]["relax_t"], TP))
    say("C-P6 rise-then-decay [DECAY tau recovered, not the startup]",
        e6 <= PLANT_TAU_TOL,
        "got tau=%.2f expected %.1f  rel.err %.2e  tol %g  (a reader fitting "
        "from iteration 1 returns O(10), not O(1000))"
        % (r6["fit"]["tau"], TAU6, e6, PLANT_TAU_TOL))

    # ---- C-M1 mutation: adequacy always True -> C-P4 must go green -------
    r4m = assess(tp, yp, mutate=True)
    say("C-M1 MUTATION adequacy:=True [C-P4 then passes, suite must go red]",
        r4m["adequate"] and r4m["residual_transient"] is not None,
        "mutated verdict=%s (a real adequacy test is therefore load-bearing)"
        % r4m["verdict"])

    if verbose:
        print()
        if fails:
            print("CONTROLS RED: %s" % ", ".join(fails))
        else:
            print("ALL CONTROLS GREEN (%d plants + 1 mutation)" % 12)
    return fails


# -------------------------------------------------------------------- report

def measure(case=CASE):
    print("F28G L1 -- H3 equilibration measurement")
    print("case: %s" % case)
    print("thresholds fixed in source: A_STABLE_TOL=%g  TAU_RATIO_TOL=%g  "
          "SETTLED_TAUS=%g  SETTLED_RESIDUAL=%g"
          % (A_STABLE_TOL, TAU_RATIO_TOL, SETTLED_TAUS, SETTLED_RESIDUAL))
    print()
    results = {}
    for name, rel, col, what in SERIES:
        path = os.path.join(case, rel)
        t, y = load_series(path, col)
        r = assess(t, y)
        results[name] = r
        f, d = r["fit"], r["drift"]
        print("=== %s  (%s)" % (name, what))
        print("    rows %d   t %g..%g   artifact %s"
              % (len(t), t[0], t[-1], rel))
        print("    relaxation starts at iteration %g (last turning point of "
              "the %d-sample smooth); fit uses %d rows"
              % (r["adequacy"]["relax_t"], SMOOTH_WINDOW, f["n"]))
        print("    fit  tau=%.4g  A=%+.8e  B=%+.4e  rms=%.4e" %
              (f["tau"], f["A"], f["B"], f["rms"]))
        print("    A-1 asymptote spread over end-truncation  %.3e   (tol %g)  %s"
              % (r["adequacy"]["a_spread"], A_STABLE_TOL,
                 "PASS" if r["adequacy"]["ok_a1"] else "FAIL"))
        print("    A-2 tau ratio over window starts          %.3f     (tol %g)  %s%s"
              % (r["adequacy"]["tau_ratio"], TAU_RATIO_TOL,
                 "NOT EVALUABLE (no transient to time)"
                 if not r["adequacy"].get("a2_evaluable", True)
                 else ("PASS" if r["adequacy"]["ok_a2"] else "FAIL"),
                 "  [tau monotone increasing -- power-law tell]"
                 if r["adequacy"]["tau_monotone_increasing"] else ""))
        print("        A-2 used %d of %d start windows; %d excluded whose "
              "resolved decay was below the %g detection floor"
              % (len(r["adequacy"]["kept"]), len(r["adequacy"]["starts"]),
                 r["adequacy"]["n_excluded"], DETECT_FLOOR_REL))
        if r["adequate"]:
            print("    elapsed %.2f tau ; residual transient %.3e of |A|"
                  % (r["taus_elapsed"], r["residual_transient"]))
        else:
            print("    NO ASYMPTOTE QUOTED -- %s"
                  % ("no transient above the detection floor exists anywhere "
                     "in this record"
                     if not r["adequacy"].get("a2_evaluable", True)
                     else "the exponential model is not supported on this "
                          "series"))
        print("    tail (last half): slope %+.4e /iter   NW se %.3e   %.2f sigma"
              "   tau_int %.1f   n_eff %.1f"
              % (d["slope"], d["se"], d["sigma"], d["tau_int"], d["n_eff"]))
        print("    tail drift extrapolated over one more run length: %+.4e "
              "(%.4f%% of the tail level)"
              % (d["over_run"], 100.0 * d["over_run"] / abs(d["level"])))
        print("    VERDICT: %s" % r["verdict"])
        print()
    return results


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="run every planted control and the mutation, then exit")
    ap.add_argument("--measure", action="store_true",
                    help="measure the F28G L1 monitor series")
    ap.add_argument("--case", default=CASE)
    a = ap.parse_args(argv)
    if not (a.selftest or a.measure):
        ap.error("choose --selftest or --measure")
    try:
        if a.selftest:
            fails = selftest()
            if fails:
                return EXIT_REFUSE
        if a.measure:
            # Rule 3: the measurement is not offered unless the controls are
            # green in the same interpreter that produces it.
            fails = selftest(verbose=False)
            if fails:
                print("REFUSED: planted controls red (%s) -- no measurement is "
                      "quoted from an unproven reader" % ", ".join(fails))
                return EXIT_REFUSE
            print("[planted controls green in this interpreter; measuring]\n")
            measure(a.case)
    except Refusal as e:
        print("REFUSED: %s" % e)
        return EXIT_REFUSE
    except InstrumentError as e:
        print("INSTRUMENT ERROR: %s" % e)
        return EXIT_INSTRUMENT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
