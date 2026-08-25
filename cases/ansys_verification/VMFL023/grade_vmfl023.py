#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL023 -- Oscillating Laminar Flow Around a Circular Cylinder.  THE COMPARATOR.

FROZEN AT THE PRE-REGISTRATION COMMIT.  NO THRESHOLD, BAND, REFERENCE VALUE,
WINDOW OR PLANT CONSTANT IN THIS FILE IS SETTABLE FROM THE COMMAND LINE OR THE
ENVIRONMENT.  The grading path is fixed at the pre-registration commit
(CLAUDE.md rule 2); run_vmfl023.sh verifies at launch that the copy on disk
hashes equal to HEAD's blob.

  python3 grade_vmfl023.py --selftest    # every control, ZERO compute
  python3 grade_vmfl023.py               # grade the three-level family

Unlike VMFL036, this case needs NO repair arm: the manual's page is INTERNALLY
CONSISTENT.  Its stated rho = 1, mu = 0.02, D = 2, U = 1 give Re = 100 and the
page ITSELF states Re = 100.  That consistency is ASSERTED below, not assumed.
"""

import cmath
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL023"

# ===========================================================================
# 1.  THE CASE, AS THE MANUAL STATES IT (p.89).  Nothing here is inferred.
# ===========================================================================
RHO = 1.0            # kg/m3        manual p.89
MU = 0.02            # kg/m-s       manual p.89
D_CYL = 2.0          # m            manual p.89 "Diameter of the cylinder = 2 m"
U_INF = 1.0          # m/s          manual p.89
RE = RHO * U_INF * D_CYL / MU                       # 100.0
RE_STATED_BY_PAGE = 100.0   # the page's own words: "(Re = 100)" and both tables

REF_ST = 0.165       # manual Tables .23.2 / .23.3, "Target"
ANSYS_FLUENT_ST = 0.178      # CONTEXT ONLY -- never a gate (manual ratio 1.1)
ANSYS_CFX_ST = 0.167         # CONTEXT ONLY -- never a gate (manual ratio 1.01)

# ===========================================================================
# 2.  THE GATE.  Frozen before any compute; justified in PREREGISTRATION.md
#     line 6 from the published correlation spread, NEVER from a first run.
# ===========================================================================
TOL = 0.03           # |St_lab - 0.165| / 0.165 <= 0.03 at the FINEST level

# The published 2D-shedding correlations at Re = 100.  These are the band's
# justification and are ALSO a control: the reference the manual prints must sit
# inside the spread of the correlations the literature actually uses, or the
# reference itself is the thing in question (the VMFL036 lesson).
def st_williamson1988(re):   return -3.3265 / re + 0.1816 + 1.6e-4 * re
def st_roshko1954(re):       return 0.212 * (1.0 - 21.2 / re)
def st_fey1998(re):          return 0.2684 - 1.0356 / math.sqrt(re)
def st_williamsonbrown(re):  return 0.2731 - 1.1129 / math.sqrt(re) + 0.4821 / re
CORRELATIONS = [("Williamson 1988", st_williamson1988),
                ("Roshko 1954", st_roshko1954),
                ("Fey et al. 1998", st_fey1998),
                ("Williamson & Brown 1998", st_williamsonbrown)]

# ===========================================================================
# 3.  THE MEASUREMENT WINDOW AND THE METHOD.  BOTH FROZEN HERE.
# ===========================================================================
ENDTIME = 300.0      # s
DELTAT = 0.005       # s, FIXED at every level (see line 8 of the registration)
WINDOW = (180.0, 300.0)      # the SETTLED window, declared before any run
MIN_CROSSINGS = 8            # refuse a window that does not contain enough cycles
# Stationarity control: the settled window is split in half and the peak-to-peak
# lift amplitude of each half compared.  A window still growing is NOT settled.
STATIONARITY_TOL = 0.05      # 5% between the two half-window amplitudes

# ===========================================================================
# 4.  THE LADDER.  r = 2 BY CONSTRUCTION (K frozen; see the mesh generator).
# ===========================================================================
K_STRETCH = 200.0
LEVELS = [("L1_96x32", 24, 32), ("L2_192x64", 48, 64), ("L3_384x128", 96, 128)]
RATIO = 2.0
FS = 1.25
REQUIRED_FIELDS = ["U", "p"]

# Roache classifier thresholds (semantics identical to VMFL036).
EPS_ABS = 1.0e-12
STAG_TOL = 1.0e-3

# ===========================================================================
# 5.  PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  None is optional.
# ===========================================================================
PLANT_FREQ = 0.0825          # Hz -> St = f*D/U = 0.165 EXACTLY, by construction.
PLANT_ST_TOL = 1.0e-6
PLANT_LIFT_AMP = 3.3e-02     # N, the amplitude of the planted sinusoid


class Refusal(Exception):
    pass


def refuse(code, msg):
    raise Refusal("REFUSE[%s]: %s" % (code, msg))


# ===========================================================================
# force.dat reader.  Column layout from the FILE'S OWN header, never positional.
# ===========================================================================
def read_force_dat(path):
    if not os.path.isfile(path):
        refuse("F1", "no force.dat at %s" % path)
    cols = None
    rows = []
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            body = s.lstrip("#").strip()
            if "total_y" in body and body.split()[0].lower().startswith("time"):
                cols = body.replace("\t", " ").split()
            continue
        if cols is None:
            refuse("F2", "%s has data rows before any column header naming total_y "
                         "-- the reader will not guess a column layout" % path)
        parts = s.replace("\t", " ").split()
        if len(parts) != len(cols):
            refuse("F3", "%s: row has %d fields against %d header names"
                         % (path, len(parts), len(cols)))
        try:
            rows.append([float(t) for t in parts])
        except ValueError:
            refuse("F3", "%s: non-numeric field in a data row" % path)
    if cols is None:
        refuse("F2", "%s: no column header naming total_y was found" % path)
    if not rows:
        refuse("F4", "%s: header found but ZERO data rows" % path)
    if "total_y" not in cols:
        refuse("F2", "%s: header has no total_y column" % path)
    iy = cols.index("total_y")
    return {"cols": cols, "time": [r[0] for r in rows],
            "fy": [r[iy] for r in rows]}


# ===========================================================================
# St FROM THE LIFT SERIES.  St is a FREQUENCY, so it depends only on the TIMING
# of the signal and NOT on any reference area -- no Aref sensitivity can reach
# this gate.
#
# PRIMARY: upward zero-crossings of the detrended lift, located by linear
#   interpolation between samples, then a LEAST-SQUARES LINE through
#   (crossing index, crossing time).  Its slope IS the period.  Resolution is set
#   by deltaT and the number of cycles, not by any bin width.
# SECONDARY: the manual's own method -- an FFT peak.  Reported beside the primary
#   WITH ITS BIN WIDTH, because on a 120 s record the bin width is 1/120 Hz,
#   i.e. dSt = 0.0167 = 10% of 0.165.  A method whose resolution is 10% cannot
#   resolve a 3% band, and that is stated, not hidden.
# ===========================================================================
def st_zero_crossing(t, fy, window):
    idx = [i for i, tt in enumerate(t) if window[0] <= tt <= window[1]]
    if len(idx) < 100:
        refuse("W1", "the settled window %s holds only %d samples" % (window, len(idx)))
    tw = [t[i] for i in idx]
    yw = [fy[i] for i in idx]
    mean = sum(yw) / len(yw)
    y = [v - mean for v in yw]
    cross = []
    for i in range(len(y) - 1):
        if y[i] <= 0.0 < y[i + 1]:
            frac = (0.0 - y[i]) / (y[i + 1] - y[i])
            cross.append(tw[i] + frac * (tw[i + 1] - tw[i]))
    if len(cross) < MIN_CROSSINGS:
        refuse("W2", "the settled window %s holds %d upward zero-crossings, fewer "
                     "than the frozen minimum %d -- St cannot be measured from it"
                     % (window, len(cross), MIN_CROSSINGS))
    n = len(cross)
    xs = list(range(n))
    mx = sum(xs) / n
    mt = sum(cross) / n
    num = sum((xs[i] - mx) * (cross[i] - mt) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    if den <= 0:
        refuse("W3", "degenerate crossing regression")
    period = num / den
    if period <= 0:
        refuse("W3", "non-positive period %g from the crossing regression" % period)
    resid = [cross[i] - (mt + period * (xs[i] - mx)) for i in range(n)]
    rms = math.sqrt(sum(r * r for r in resid) / n)
    return {"period": period, "st": D_CYL / (period * U_INF), "n_cross": n,
            "rms_resid_s": rms, "mean_fy": mean,
            "amp_ptp": max(y) - min(y), "n_samples": len(idx)}


def st_fft(t, fy, window):
    idx = [i for i, tt in enumerate(t) if window[0] <= tt <= window[1]]
    yw = [fy[i] for i in idx]
    mean = sum(yw) / len(yw)
    y = [v - mean for v in yw]
    n = len(y)
    span = t[idx[-1]] - t[idx[0]]
    df = 1.0 / span
    best_k, best_mag = 0, -1.0
    kmax = min(n // 2, int(1.0 / df) + 2)   # only up to 1 Hz; St = 0.165 -> f = 0.0825
    for k in range(1, kmax):
        acc = 0.0 + 0.0j
        w = -2.0j * math.pi * k / n
        for j in range(n):
            acc += y[j] * cmath.exp(w * j)
        m = abs(acc)
        if m > best_mag:
            best_mag, best_k = m, k
    f = best_k * df
    return {"f_hz": f, "st": f * D_CYL / U_INF, "bin_hz": df,
            "bin_st": df * D_CYL / U_INF, "n": n, "span_s": span}


def stationarity(t, fy, window):
    mid = 0.5 * (window[0] + window[1])
    out = []
    for w in ((window[0], mid), (mid, window[1])):
        idx = [i for i, tt in enumerate(t) if w[0] <= tt <= w[1]]
        yw = [fy[i] for i in idx]
        m = sum(yw) / len(yw)
        out.append(max(yw) - min(yw))
    rel = abs(out[1] - out[0]) / max(abs(out[0]), 1e-30)
    return {"amp_first_half": out[0], "amp_second_half": out[1], "rel": rel,
            "settled": rel <= STATIONARITY_TOL}


# ===========================================================================
# Roache triple (CLAUDE.md rule 5).  Identical semantics to VMFL036.
# ===========================================================================
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine, d21=d21, d32=d32,
               ratio=ratio, fs=fs, p=None, R=None, gci_fine=None,
               f_extrapolated=None, why=None)
    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"
        return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"
        out["why"] = "coarse-medium difference below %g, medium-fine not" % EPS_ABS
        return out
    R_ = d21 / d32
    out["R"] = R_
    if R_ < 0:
        out["state"] = "OSCILLATORY"
        return out
    if abs(R_ - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"
        return out
    if R_ > 1.0:
        out["state"] = "DIVERGENT"
        return out
    p = math.log(1.0 / R_) / math.log(ratio)
    out["p"] = p
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"
        out["why"] = "r^p - 1 <= 0"
        return out
    out["state"] = "CONVERGING"
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


# ===========================================================================
# Strict completion (CLAUDE.md rule 4).  NO DEPARTURE IS DECLARED.  The step
# count clause is the LITERAL generalisation for a transient with a FIXED deltaT:
#     ExecutionTime count == endTime / deltaT
# ===========================================================================
N_STEPS_EXPECTED = int(round(ENDTIME / DELTAT))


def _time_dirs(level_dir):
    out = []
    for n in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, n)):
            try:
                out.append((float(n), n))
            except ValueError:
                pass
    return sorted(out)


def completion_check(level_dir):
    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("C1", "no RUN_RC.txt in %s -- the run's own exit code is not on disk"
                     % level_dir)
    rcd = dict(re.findall(r"(\w+)=(.*)", open(rc_path).read()))
    if int(rcd.get("rc", "1")) != 0:
        refuse("C1", "%s records rc=%s -- a non-zero exit is a finding, triage it"
                     % (rc_path, rcd.get("rc")))
    log = os.path.join(level_dir, "log.pimpleFoam")
    if not os.path.isfile(log):
        refuse("C2", "no log.pimpleFoam in %s" % level_dir)
    log_lines = open(log, errors="replace").read().split("\n")
    if not any(l.strip() == "End" for l in log_lines):
        refuse("C2", "no 'End' line in %s" % log)
    times = _time_dirs(level_dir)
    if not times:
        refuse("C3", "no time directories in %s" % level_dir)
    t_last, t_last_name = times[-1]
    if abs(t_last - ENDTIME) > 1e-6:
        refuse("C3", "last time %g is not endTime %g in %s (rule 4 checked "
                     "LITERALLY -- no departure is declared for this case)"
                     % (t_last, ENDTIME, level_dir))
    n_exec = sum(1 for l in log_lines if l.startswith("ExecutionTime = "))
    if n_exec != N_STEPS_EXPECTED:
        refuse("C5", "ExecutionTime count is %d against endTime/deltaT = %d in %s "
                     "-- rule 4's count clause, checked literally"
                     % (n_exec, N_STEPS_EXPECTED, log))
    for f in REQUIRED_FIELDS:
        p = os.path.join(level_dir, t_last_name, f)
        if not os.path.isfile(p):
            refuse("C4", "field %s missing at endTime in %s" % (f, level_dir))
    zero_dir = os.path.join(level_dir, "0")
    if not os.path.isdir(zero_dir):
        refuse("C6", "no 0/ in %s -- the age guard has no datum" % level_dir)
    m0 = max(os.path.getmtime(os.path.join(zero_dir, f))
             for f in os.listdir(zero_dir)
             if os.path.isfile(os.path.join(zero_dir, f)))
    for f in REQUIRED_FIELDS:
        p = os.path.join(level_dir, t_last_name, f)
        if os.path.getmtime(p) <= m0:
            refuse("C6", "AGE GUARD: %s is not newer than the newest file in %s -- "
                         "this field was not produced by the run that was allowed "
                         "to answer" % (p, zero_dir))
    # Courant: an implicit PISO run above Co ~ 1 is not trustworthy for a
    # frequency, and the registration promises Co < 1 at every level.
    co = [float(l.split("max:")[1]) for l in log_lines
          if l.startswith("Courant Number") and "max:" in l]
    if not co:
        refuse("C7", "no Courant Number lines in %s" % log)
    return {"rc": 0, "endtime_dir": t_last_name, "n_steps": n_exec,
            "co_max": max(co),
            "wall_s": float(rcd.get("wall_s", "nan")),
            "core_min": float(rcd.get("core_min", "nan")),
            "ranks": int(rcd.get("ranks", "1"))}


def read_level(name):
    d = os.path.join(RUN_ROOT, name)
    if not os.path.isdir(d):
        refuse("L0", "level directory %s does not exist" % d)
    comp = completion_check(d)
    fdat = os.path.join(d, "postProcessing", "forces", "0", "force.dat")
    f = read_force_dat(fdat)
    if f["time"][-1] < ENDTIME - 1e-6:
        refuse("F5", "%s: the force series ends at %g, before endTime %g"
                     % (fdat, f["time"][-1], ENDTIME))
    zc = st_zero_crossing(f["time"], f["fy"], WINDOW)
    ft = st_fft(f["time"], f["fy"], WINDOW)
    stat = stationarity(f["time"], f["fy"], WINDOW)
    return {"dir": d, "force_dat": fdat, "completion": comp,
            "zc": zc, "fft": ft, "stat": stat, "St": zc["st"]}


# ===========================================================================
# PLANTED-ZERO CONTROLS -- run against the REAL artifacts of a real level.
# ===========================================================================
def control_frequency_plant(level):
    """Overwrite a COPY of the level's real force.dat with a sinusoid of a KNOWN
    frequency and require the estimator to return it.  An estimator not shown able
    to see a KNOWN non-trivial frequency has not been shown able to see any."""
    src = level["force_dat"]
    tmp = tempfile.mkdtemp(prefix="vmfl023_plant_")
    try:
        base = read_force_dat(src)
        cols = base["cols"]
        iy = cols.index("total_y")
        dst = os.path.join(tmp, "force.dat")
        out = []
        for line in open(src):
            s = line.rstrip("\n")
            t = s.strip()
            if t.startswith("#") or not t:
                out.append(s)
                continue
            parts = t.replace("\t", " ").split()
            tt = float(parts[0])
            parts[iy] = "%.12e" % (PLANT_LIFT_AMP
                                   * math.sin(2.0 * math.pi * PLANT_FREQ * tt))
            out.append(" ".join(parts))
        open(dst, "w").write("\n".join(out) + "\n")
        g = read_force_dat(dst)
        seen = st_zero_crossing(g["time"], g["fy"], WINDOW)
        want = PLANT_FREQ * D_CYL / U_INF        # 0.165 exactly
        if abs(seen["st"] - want) > PLANT_ST_TOL:
            refuse("P1", "PLANTED-FREQUENCY CONTROL FAILED: a sinusoid at f = %g Hz "
                         "(St = %.10g by construction) was planted into a copy of "
                         "%s and the estimator returned St = %.10g (delta %.3e).  "
                         "This estimator has NOT been shown able to see a KNOWN "
                         "frequency, so no St it reports is evidence (rule 3)."
                         % (PLANT_FREQ, want, src, seen["st"], seen["st"] - want))
        fseen = st_fft(g["time"], g["fy"], WINDOW)
        return {"plant_f": PLANT_FREQ, "plant_st": want, "seen_st": seen["st"],
                "seen_fft_st": fseen["st"], "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_flat_plant(level):
    """A DEAD signal must be REFUSED, not reported as some St.  A flat lift series
    has no crossings; the estimator must refuse rather than invent a frequency."""
    src = level["force_dat"]
    tmp = tempfile.mkdtemp(prefix="vmfl023_flat_")
    try:
        base = read_force_dat(src)
        iy = base["cols"].index("total_y")
        dst = os.path.join(tmp, "force.dat")
        out = []
        for line in open(src):
            s = line.rstrip("\n")
            t = s.strip()
            if t.startswith("#") or not t:
                out.append(s); continue
            parts = t.replace("\t", " ").split()
            parts[iy] = "0.000000000000e+00"
            out.append(" ".join(parts))
        open(dst, "w").write("\n".join(out) + "\n")
        g = read_force_dat(dst)
        try:
            st_zero_crossing(g["time"], g["fy"], WINDOW)
        except Refusal:
            return {"refused_flat": True}
        refuse("P2", "FLAT-SIGNAL CONTROL FAILED: a lift series set identically to "
                     "zero produced an St instead of a refusal.  An estimator that "
                     "reports a frequency for a dead signal reports one for "
                     "anything.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_roache_classifier():
    seen = {}
    seen["CONVERGING"] = roache(1.0 + 4.0, 1.0 + 1.0, 1.0 + 0.25)
    seen["DIVERGENT"] = roache(1.0 + 0.25, 1.0 + 1.0, 1.0 + 4.0)
    seen["OSCILLATORY"] = roache(1.0 + 1.0, 1.0 - 1.0, 1.0 + 0.25)
    seen["STAGNANT"] = roache(3.0, 2.0, 1.0)
    seen["EXACT"] = roache(2.0, 2.0, 2.0)
    for want, got in seen.items():
        if got["state"] != want:
            refuse("R1", "ROACHE CLASSIFIER CONTROL FAILED: a triple constructed to "
                         "be %s was classified %s" % (want, got["state"]))
    if abs(seen["CONVERGING"]["p"] - 2.0) > 1e-9:
        refuse("R2", "ROACHE CONTROL FAILED: an exactly-second-order triple gave "
                     "observed order %.12g, not 2" % seen["CONVERGING"]["p"])
    return {k: v["state"] for k, v in seen.items()}


def control_reference_consistency():
    """THE VMFL036 LESSON, APPLIED HERE AS A CONTROL.  The manual's target must be
    reproducible from the manual's OWN stated properties.  If Re derived from the
    page disagrees with the Re the page states, or if the printed target sits
    outside the spread of the published correlations at that Re, the REFERENCE is
    the thing in question and the gate is mis-specified."""
    if abs(RE - RE_STATED_BY_PAGE) > 1e-9:
        refuse("X1", "REFERENCE CONSISTENCY FAILED: rho*U*D/mu from the page's own "
                     "stated properties is %.6f but the page states Re = %.1f.  The "
                     "page is INTERNALLY INCONSISTENT and the gate would be "
                     "mis-specified (the VMFL036/VMFL059 class)."
                     % (RE, RE_STATED_BY_PAGE))
    vals = [(n, fn(RE)) for n, fn in CORRELATIONS]
    lo = min(v for _n, v in vals)
    hi = max(v for _n, v in vals)
    if not (lo * 0.98 <= REF_ST <= hi * 1.02):
        refuse("X2", "REFERENCE CONSISTENCY FAILED: the manual's target St = %.4f "
                     "sits outside the published correlation spread [%.5f, %.5f] at "
                     "Re = %.1f" % (REF_ST, lo, hi, RE))
    return {"re_derived": RE, "re_stated": RE_STATED_BY_PAGE,
            "corr": vals, "lo": lo, "hi": hi}


def control_completion_refuses():
    tmp = tempfile.mkdtemp(prefix="vmfl023_comp_")
    try:
        try:
            completion_check(tmp)
        except Refusal:
            return {"refused_empty_dir": True}
        refuse("K1", "COMPLETION CONTROL FAILED: an EMPTY directory passed the "
                     "strict-completion check instead of being refused")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_estimator_synthetic():
    """The estimator, on a synthetic series with NO run directory involved, so the
    controls do not depend on a run existing."""
    t = [i * DELTAT for i in range(int(ENDTIME / DELTAT) + 1)]
    fy = [PLANT_LIFT_AMP * math.sin(2 * math.pi * PLANT_FREQ * tt) + 1.7 for tt in t]
    got = st_zero_crossing(t, fy, WINDOW)
    want = PLANT_FREQ * D_CYL / U_INF
    if abs(got["st"] - want) > PLANT_ST_TOL:
        refuse("S1", "SYNTHETIC ESTIMATOR CONTROL FAILED: St %.10g against the "
                     "constructed %.10g" % (got["st"], want))
    # The window mean of a sinusoid over a NON-INTEGER number of periods is not
    # exactly the DC offset: the partial cycle leaves a residual bounded by
    # amp / (pi * n_cycles) = 3.3e-2 / (pi * ~9.9) = 1.06e-03.  The tolerance is
    # that BOUND, computed here rather than loosened by hand.  It does not matter
    # for St: a common shift moves every crossing equally and the regression
    # SLOPE -- which IS the period -- is untouched.  That is why S1 above passes
    # to 1e-6 while this residual is 3e-4.
    dc_bound = PLANT_LIFT_AMP / (math.pi * (WINDOW[1] - WINDOW[0]) * PLANT_FREQ)
    if abs(got["mean_fy"] - 1.7) > dc_bound:
        refuse("S2", "SYNTHETIC ESTIMATOR CONTROL FAILED: a deliberate DC offset of "
                     "1.7 was not detrended (mean read %.6g, bound %.3e)"
                     % (got["mean_fy"], dc_bound))
    f = st_fft(t, fy, WINDOW)
    return {"st": got["st"], "want": want, "n_cross": got["n_cross"],
            "fft_st": f["st"], "fft_bin_st": f["bin_st"]}


def selftest():
    print("VMFL023 comparator --selftest   (ZERO compute; no run directory read)")
    print("-" * 78)
    x = control_reference_consistency()
    print("  reference    Re from the page's OWN properties = %.4f; the page states "
          "%.1f -> CONSISTENT" % (x["re_derived"], x["re_stated"]))
    for n, v in x["corr"]:
        print("               %-26s St(Re=100) = %.5f" % (n, v))
    print("               correlation spread [%.5f, %.5f] brackets the manual's "
          "target %.4f" % (x["lo"], x["hi"], REF_ST))
    r = control_roache_classifier()
    print("  roache       every state SEEN: %s" % ", ".join(sorted(r.values())))
    s = control_estimator_synthetic()
    print("  estimator    a constructed sinusoid at St = %.6f was recovered as "
          "%.6f from %d crossings; a 1.7 DC offset was detrended"
          % (s["want"], s["st"], s["n_cross"]))
    print("               FFT on the same series: St = %.5f, bin width dSt = %.5f "
          "-- the manual's OWN method cannot resolve the 3%% band (bin is %.1f%% "
          "of the target)" % (s["fft_st"], s["fft_bin_st"],
                              100.0 * s["fft_bin_st"] / REF_ST))
    c = control_completion_refuses()
    print("  completion   an empty directory is REFUSED (rule 4 refuses, never "
          "degrades): %s" % c["refused_empty_dir"])
    print("-" * 78)
    print("SELFTEST GREEN")
    return 0


def verify_frozen(sha):
    import subprocess
    repo = subprocess.check_output(
        ["git", "-C", HERE, "rev-parse", "--show-toplevel"]).decode().strip()
    rel = "cases/ansys_verification/VMFL023/grade_vmfl023.py"
    want = subprocess.check_output(
        ["git", "-C", repo, "rev-parse", "%s:%s" % (sha, rel)]).decode().strip()
    got = subprocess.check_output(
        ["git", "-C", repo, "hash-object", os.path.join(repo, rel)]).decode().strip()
    print("  %s %s  disk=%s frozen=%s" % ("OK " if want == got else "DRIFT",
                                          rel, got[:12], want[:12]))
    return 0 if want == got else 1


def dryrun_reader(path):
    d = read_force_dat(path)
    print("  reader OK: %d rows, columns %s, total_y located by NAME"
          % (len(d["time"]), ",".join(d["cols"][1:])))
    return 0


# ===========================================================================
# 6.  THE VERDICT.
# ===========================================================================
def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify-frozen" in argv:
        return verify_frozen(argv[argv.index("--verify-frozen") + 1])
    if "--dryrun-reader" in argv:
        return dryrun_reader(argv[argv.index("--dryrun-reader") + 1])

    print("VMFL023 -- Oscillating Laminar Flow Around a Circular Cylinder.")
    print("manual p.89; target St = %.3f; Re = %.1f; run root %s"
          % (REF_ST, RE, RUN_ROOT))
    selftest()
    lv = [read_level(n) for (n, _a, _b) in LEVELS]
    print("")
    print("=" * 78)
    for (name, nt, nr), L_ in zip(LEVELS, lv):
        c = L_["completion"]
        print("  %-12s cells=%-7d St=%.6f  T=%.5f s  %d crossings  "
              "regression rms=%.2e s" % (name, 4 * nt * nr, L_["St"],
                                         L_["zc"]["period"], L_["zc"]["n_cross"],
                                         L_["zc"]["rms_resid_s"]))
        print("               Cl ptp=%.5e  Co_max=%.4f  wall=%.0fs  %.2f core-min"
              % (L_["zc"]["amp_ptp"], c["co_max"], c["wall_s"], c["core_min"]))
        print("               settled? first-half ptp %.5e vs second-half %.5e "
              "(%.2f%%, tol %.0f%%) -> %s"
              % (L_["stat"]["amp_first_half"], L_["stat"]["amp_second_half"],
                 100.0 * L_["stat"]["rel"], 100.0 * STATIONARITY_TOL,
                 "SETTLED" if L_["stat"]["settled"] else "NOT SETTLED"))
        print("               FFT (the manual's own method): St=%.5f, bin dSt=%.5f"
              % (L_["fft"]["st"], L_["fft"]["bin_st"]))

    cfp = control_frequency_plant(lv[-1])
    cfl = control_flat_plant(lv[-1])
    print("  CONTROL freq plant : a sinusoid at St = %.6f planted into a copy of "
          "the finest level's real force.dat; the estimator returned %.6f.  It is "
          "shown able to see a KNOWN frequency." % (cfp["plant_st"], cfp["seen_st"]))
    print("  CONTROL flat plant : a lift series set identically to zero is REFUSED, "
          "not reported as some St: %s" % cfl["refused_flat"])

    not_settled = [n for (n, _a, _b), L_ in zip(LEVELS, lv) if not L_["stat"]["settled"]]
    hi_co = [n for (n, _a, _b), L_ in zip(LEVELS, lv) if L_["completion"]["co_max"] >= 1.0]
    sts = [L_["St"] for L_ in lv]
    tri = roache(sts[0], sts[1], sts[2])

    print("")
    print("  ROACHE TRIPLE  f_coarse=%.6f  f_med=%.6f  f_fine=%.6f"
          % (tri["f_coarse"], tri["f_med"], tri["f_fine"]))
    print("                 d32=%.3e  d21=%.3e  R=%s  state=%s"
          % (tri["d32"], tri["d21"],
             "n/a" if tri["R"] is None else "%.6f" % tri["R"], tri["state"]))
    if tri["p"] is not None:
        flag = "  <-- SUSPICIOUSLY HIGH (above the formal order 2)" if tri["p"] > 2.3 else ""
        print("                 observed order p_obs = %.4f (formal p_f = 2)%s"
              % (tri["p"], flag))
    if tri["gci_fine"] is not None:
        print("                 GCI_fine at Fs = %.2f : %.4f%%   Richardson f_ex = %.6f"
              % (FS, 100.0 * tri["gci_fine"], tri["f_extrapolated"]))
    else:
        print("                 GCI: NOT QUOTED -- the three values are not monotone.")

    st_fine = sts[-1]
    rel = abs(st_fine - REF_ST) / REF_ST
    print("")
    print("  St(finest) = %.6f   manual target = %.3f   |rel| = %.4f%%"
          % (st_fine, REF_ST, 100.0 * rel))
    print("  (context only, never a gate: Ansys Fluent %.3f = %+.2f%%, "
          "Ansys CFX %.3f = %+.2f%%)"
          % (ANSYS_FLUENT_ST, 100.0 * (ANSYS_FLUENT_ST - REF_ST) / REF_ST,
             ANSYS_CFX_ST, 100.0 * (ANSYS_CFX_ST - REF_ST) / REF_ST))

    if not_settled:
        verdict = "NOT A RESULT"
        why = ("rule 5 step 1: level(s) %s are NOT SETTLED over the frozen window "
               "%s -- the lift amplitude is still changing, so its frequency is not "
               "a shedding frequency" % (", ".join(not_settled), WINDOW))
    elif hi_co:
        verdict = "NOT A RESULT"
        why = ("level(s) %s ran at max Courant >= 1, above what the registration "
               "promised" % ", ".join(hi_co))
    elif tri["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = ("rule 5 step 2: the grid triple is %s, not CONVERGING.  The value "
               "%.6f and both differences are printed above." % (tri["state"], st_fine))
    elif rel <= TOL:
        verdict = "GATE REACHED"
        why = ("rule 5 step 3: the triple is CONVERGING and |rel| = %.4f%% is inside "
               "the frozen band %.1f%%.  TIER CEILING: the reference is a "
               "CORRELATION read from an experimentally-established St-Re curve "
               "(White 1994), corroborated by a NUMERICAL study (Kim & Lee 2002).  "
               "A correlation buys V, NEVER P, so HOLDS is not available and GATE "
               "REACHED is the ceiling whatever the number."
               % (100.0 * rel, 100.0 * TOL))
    else:
        verdict = "GATE FAIL"
        why = ("rule 5 step 3: the triple is CONVERGING and |rel| = %.4f%% is "
               "OUTSIDE the frozen band %.1f%%." % (100.0 * rel, 100.0 * TOL))
    print("")
    print("  VERDICT: %s" % verdict)
    print("  %s" % why)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as e:
        print("")
        print(str(e))
        print("The comparator REFUSES (exit 2) rather than degrade.")
        sys.exit(2)
