#!/usr/bin/env python3
"""F9 round 3 (2026-07-30): automated convergence criteria, an
entrance-length prediction test, and a discharge-coefficient audit.

Everything here reads probe files already on disk. Nothing is hand-judged.

--------------------------------------------------------------------------
CRITERION F9-CYC-1  --  cycle-to-cycle convergence of a pulsatile solve
--------------------------------------------------------------------------
For a run forced at period T, cut whole cycles backwards from t_end:
``cycle_j`` = [t_end - j*T, t_end - (j-1)*T], j = 1 (last) .. n.

For each monitored signal s(t) and each cycle, five functionals:

    mean_j   time-weighted cycle mean (trapezoid; the timestep is adaptive)
    max_j    cycle maximum
    min_j    cycle minimum
    band_j   max_j - min_j  (the cycle's own dynamic range)
    w_j(phi) the waveform resampled onto 256 uniform phase points

and between CONSECUTIVE cycles (later vs earlier):

    e_mean = |mean_j - mean_{j+1}| / |mean_j|
    e_max  = |max_j  - max_{j+1}|  / |max_j|
    e_band = |band_j - band_{j+1}| / band_j
    e_wave = max_phi |w_j - w_{j+1}| / band_j        (L-inf, band-normalised)
    e_wav2 = rms_phi |w_j - w_{j+1}| / band_j        (L-2,   band-normalised)

PASS when every one of the five is below TOL_CYC = 1e-3 for the most recent
consecutive pair. The waveform norms are normalised by the cycle's own band,
not by its mean, because the mean of a pulsatile signal passes through zero
and a mean-normalised error there is meaningless.

WHY 1e-3. It sits far below the discretization error this case actually
carries (measured separately by the grid levels below), so periodicity
contributes nothing to the reported uncertainty. The threshold is a
stated number, not a judgement, and it is not moved after seeing a
result.

WHY NOT STROKE VOLUME. Cycle-integrated stroke volume is the obvious
candidate metric and it is USELESS here: the solver is incompressible with
rigid walls and a prescribed inlet flux, so the volume flux through every
cross-section equals the imposed inlet flux at every instant, exactly, by
mass conservation. Stroke volume is a boundary condition, not a solution
output; it is periodic to round-off in cycle 1 of a diverging run just as
much as in a converged one. It is computed and reported below only to
demonstrate that, so that no later reader reaches for it as evidence.

--------------------------------------------------------------------------
CRITERION F9-STAT-1  --  stationarity of a fixed-BC ("steady") solve
--------------------------------------------------------------------------
Over the tail window W = [(1-f)*t_end, t_end] with f = 0.1:

    band_ratio    (max - min)/|mean|                      < 1e-2
    halves_drift  |mean(2nd half W) - mean(1st half W)|/|mean| < 1e-3
    trend         |slope|*|W| / |mean|   (LSQ slope over W)     < 1e-3
    window_shift  |mean(f=0.1) - mean(f=0.2)| / |mean|          < 1e-3

All four must pass. ``trend`` and ``window_shift`` are the two the
by-hand check did not do: a slow monotone creep can sit inside a narrow
band, and a mean that moves when the window moves is not a converged value
whatever its band looks like.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (str(HERE), str(ROOT / "sdk"),
          str(ROOT / "models" / "curriculum" / "aortic_valve")):
    if p not in sys.path:
        sys.path.insert(0, p)

from analyze_f9 import parse_probe_file                     # noqa: E402
from workflows import valve_pulsatile_cfd as v              # noqa: E402
from workflows.tmr_verification import (                    # noqa: E402
    time_weighted_stats, measure_period)
from workflows.valve_study import _cycle_weighted_loss      # noqa: E402
from waveform import phase_points                           # noqa: E402

import mpmath as mp                                         # noqa: E402
mp.mp.dps = 25

RHO = v.RHO
TOL_CYC = 1.0e-3
TOL_BAND = 1.0e-2
TOL_DRIFT = 1.0e-3
N_PHASE = 256


# ==========================================================================
# probe plumbing
# ==========================================================================

def probe_dir(case: Path) -> Path:
    base = case / "postProcessing" / "probes1"
    subs = sorted(base.iterdir(), key=lambda d: float(d.name))
    return subs[0]


# A restart writes its own probe file starting at the restart time. Splicing
# the parent's record in front of it is legitimate ONLY because the restart
# reproduces the parent's state at the join by construction (same mesh, same
# schemes, same fields read back from the parent's own checkpoint). The join
# is recorded so a reader can see where it is.
RESTART_PARENT = {"lowalpha_ext": "pulsatile_lowalpha"}


def probe_field(case: Path, field: str):
    times, data = parse_probe_file(probe_dir(case) / field)
    parent = RESTART_PARENT.get(case.name)
    if parent:
        p_case = case.parent / parent
        if (p_case / "postProcessing").is_dir():
            pt, pd = parse_probe_file(probe_dir(p_case) / field)
            join = times[0]
            keep = [i for i, t in enumerate(pt) if t < join - 1e-12]
            times = [pt[i] for i in keep] + times
            data = {k: [pd[k][i] for i in keep] + data[k] for k in data}
    return times, data


def dp_series(case: Path, a: int, b: int):
    times, p = probe_field(case, "p")
    return times, [(p[a][i] - p[b][i]) * RHO for i in range(len(times))]


def radial_probe_indices(case: Path, station_block: int = 0):
    """Radial-profile probes are 3.. in blocks of N_RADIAL_PROBES."""
    n = v.N_RADIAL_PROBES
    lo = 3 + station_block * n
    return list(range(lo, lo + n))


def r_over_R():
    return [((i + 0.5) / v.N_RADIAL_PROBES) * 0.92 for i in
            range(v.N_RADIAL_PROBES)]


# ==========================================================================
# F9-CYC-1
# ==========================================================================

def _resample_phase(times, vals, t0, t1, n=N_PHASE):
    grid = np.linspace(t0, t1, n, endpoint=False)
    return np.interp(grid, np.asarray(times), np.asarray(vals))


def cycle_functionals(times, vals, t_cycle):
    """Per-cycle functionals, cycle 1 = last complete cycle."""
    t_end = times[-1]
    t_first = times[0]
    out = []
    j = 1
    tol = 1e-3 * t_cycle
    while t_end - j * t_cycle >= t_first - tol:
        t0 = t_end - j * t_cycle
        t1 = t_end - (j - 1) * t_cycle
        win = [(t, s) for t, s in zip(times, vals) if t0 - 1e-12 <= t <= t1 + 1e-12]
        if len(win) < 8:
            break
        st = time_weighted_stats([t for t, _ in win], [s for _, s in win], t0)
        w = _resample_phase(times, vals, t0, t1)
        out.append({"cycle_back": j, "t0": t0, "t1": t1,
                    "mean": st["mean"], "max": st["hi"], "min": st["lo"],
                    "band": st["hi"] - st["lo"], "_wave": w})
        j += 1
    return out


def cyc1(times, vals, t_cycle, label):
    cyc = cycle_functionals(times, vals, t_cycle)
    pairs = []
    for j in range(len(cyc) - 1):
        late, early = cyc[j], cyc[j + 1]          # late = nearer t_end
        band = max(late["band"], 1e-30)
        dw = late["_wave"] - early["_wave"]
        e = {
            "pair": f"cycle-{len(cyc)-j-1}->cycle-{len(cyc)-j}",
            "e_mean": abs(late["mean"] - early["mean"]) / max(abs(late["mean"]), 1e-30),
            "e_max": abs(late["max"] - early["max"]) / max(abs(late["max"]), 1e-30),
            "e_band": abs(late["band"] - early["band"]) / band,
            "e_wave_inf": float(np.max(np.abs(dw))) / band,
            "e_wave_rms": float(np.sqrt(np.mean(dw ** 2))) / band,
        }
        e["worst"] = max(e[k] for k in
                         ("e_mean", "e_max", "e_band", "e_wave_inf", "e_wave_rms"))
        e["pass"] = bool(e["worst"] < TOL_CYC)
        pairs.append(e)
    verdict = ("NOT_TESTABLE (fewer than 2 complete cycles on record)"
               if not pairs else ("PERIODIC" if pairs[0]["pass"] else "NOT_PERIODIC"))
    res = {"signal": label, "t_cycle": t_cycle, "n_complete_cycles": len(cyc),
           "tolerance": TOL_CYC, "verdict": verdict,
           "cycles": [{k: c[k] for k in
                       ("cycle_back", "t0", "t1", "mean", "max", "min", "band")}
                      for c in cyc],
           "consecutive": pairs}
    if len(pairs) >= 2 and pairs[1]["worst"] > 0:
        res["convergence_ratio_last_over_previous"] = (
            pairs[0]["worst"] / pairs[1]["worst"])
    return res


def stroke_volume_per_cycle(case: Path, t_cycle: float, station_block: int = 0):
    """Cycle-integrated volume flux from the radial probe rake.

    Reported to make the point in the docstring concrete, NOT as a
    convergence metric.
    """
    times, U = probe_field(case, "U")
    idx = radial_probe_indices(case, station_block)
    ys = np.array(r_over_R())
    r = ys * v.R_PIPE
    prof = np.array([U[i] for i in idx])            # (9, nt)
    # area-weighted integral with the axis and the wall closed off linearly
    r_full = np.concatenate(([0.0], r, [v.R_PIPE]))
    q = []
    for k in range(prof.shape[1]):
        u = prof[:, k]
        u_full = np.concatenate(([u[0]], u, [0.0]))
        q.append(float(2.0 * math.pi * np.trapezoid(u_full * r_full, r_full)))
    return cyc1(times, q, t_cycle, "volume flux at the upstream rake (m^3/s)")


# ==========================================================================
# F9-STAT-1
# ==========================================================================

def stat1(times, vals, label, tail_frac=0.1):
    t_end = times[-1]

    def win_mean(f):
        t0 = t_end - f * (t_end - times[0])
        st = time_weighted_stats(times, vals, t0)
        return st

    st = win_mean(tail_frac)
    st2 = win_mean(2.0 * tail_frac)
    t0 = t_end - tail_frac * (t_end - times[0])
    w = [(t, s) for t, s in zip(times, vals) if t >= t0]
    tt = np.array([t for t, _ in w]); ss = np.array([s for _, s in w])
    mid = 0.5 * (tt[0] + tt[-1])
    m1 = float(np.mean(ss[tt <= mid])); m2 = float(np.mean(ss[tt > mid]))
    slope = float(np.polyfit(tt, ss, 1)[0])
    mean = st["mean"]
    m = {
        "window": [tt[0], tt[-1]], "n_samples": len(tt), "mean": mean,
        "band": st["band"], "band_ratio": st["band"] / abs(mean),
        "halves_drift": abs(m2 - m1) / abs(mean),
        "trend": abs(slope) * (tt[-1] - tt[0]) / abs(mean),
        "window_shift": abs(st2["mean"] - mean) / abs(mean),
    }
    m["pass_band"] = bool(m["band_ratio"] < TOL_BAND)
    m["pass_halves"] = bool(m["halves_drift"] < TOL_DRIFT)
    m["pass_trend"] = bool(m["trend"] < TOL_DRIFT)
    m["pass_window"] = bool(m["window_shift"] < TOL_DRIFT)
    m["verdict"] = ("STATIONARY" if all(m[k] for k in
                    ("pass_band", "pass_halves", "pass_trend", "pass_window"))
                    else "NOT_STATIONARY")
    m["signal"] = label
    per = measure_period(times, vals, t0)
    if per:
        m["oscillation_period_s"] = per
        m["oscillation_freq_Hz"] = 1.0 / per
    return m


# ==========================================================================
# Entrance-length prediction test (harmonic decomposition)
# ==========================================================================

def womersley_osc_complex(alpha, R, q_amp, y):
    i = mp.mpc(0, 1)
    lam = i ** mp.mpf("1.5") * alpha
    j0 = mp.besselj(0, lam)
    g_avg = 1 - (2 * mp.besselj(1, lam)) / (lam * j0)
    g = 1 - mp.besselj(0, lam * y) / j0
    return complex(q_amp / (mp.pi * R ** 2 * g_avg) * g)


def harmonic_fit(times, vals, T, t0, t1):
    """u ~ a0 + Im[A e^{i w t}] with t the ABSOLUTE solver time, matching the
    inlet Function1 sine (level + amplitude*sin(2 pi f t)). Returns
    (a0, A, rms_residual)."""
    w = 2.0 * math.pi / T
    tt = np.array([t for t in times if t0 <= t <= t1])
    yy = np.array([s for t, s in zip(times, vals) if t0 <= t <= t1])
    M = np.stack([np.ones_like(tt), np.sin(w * tt), np.cos(w * tt)], axis=1)
    sol, *_ = np.linalg.lstsq(M, yy, rcond=None)
    resid = yy - M @ sol
    return float(sol[0]), complex(sol[1], sol[2]), float(np.sqrt((resid ** 2).mean()))


def entrance_test(case: Path, T: float, station_blocks: dict[str, int]):
    """Split the CFD profile into its steady and first-harmonic parts and
    grade each against its own exact solution.

    PREDICTION UNDER THE ENTRANCE-LENGTH EXPLANATION (pre-stated):
      * The STEADY part of the analytic solution is Hagen-Poiseuille, whose
        development length is L_s/D ~ 0.05*Re ~ 210 D. The pipe offers 5 D.
        So the CFD steady part must NOT match; it must stay close to the
        flat inlet profile.
      * The FIRST-HARMONIC part is a Stokes layer whose development length
        is set by how far the mean flow carries a particle in one radian of
        forcing, L_osc = U_bulk/omega, i.e. L_osc/D = Re/(4 alpha^2). For
        the physio run that is 3.7 D against 3.0 D available (80% developed);
        for the low-alpha run 15.0 D against 3.0 D (20%). So the harmonic
        part MUST match well at alpha=16.7 and markedly worse at alpha=8.4 --
        the opposite ordering to what a solver defect would give, and the
        opposite to what the total-profile error alone suggests.
    """
    times, U = probe_field(case, "U")
    t_end = times[-1]
    t0 = t_end - T
    alpha = v.womersley_alpha(T)
    omega = 2.0 * math.pi / T
    ys = r_over_R()
    out = {"alpha": alpha, "t_window": [t0, t_end],
           "L_osc_over_D": v.U_MEAN / omega / v.D_PIPE,
           "Re_mean": v.U_MEAN * v.D_PIPE / v.NU,
           "L_steady_over_D_005Re": 0.05 * v.U_MEAN * v.D_PIPE / v.NU,
           "stations": {}}
    for label, blk in station_blocks.items():
        idx = radial_probe_indices(case, blk)
        rows = []
        num_s = den_s = num_h = den_h = 0.0
        for j, y in enumerate(ys):
            a0, A, rms = harmonic_fit(times, U[idx[j]], T, t0, t_end)
            pois = 2.0 * v.Q_MEAN / (math.pi * v.R_PIPE ** 2) * (1 - y ** 2)
            Aan = womersley_osc_complex(alpha, v.R_PIPE, v.Q_AMP, y)
            rows.append({"r_over_R": y, "a0_cfd": a0, "a0_poiseuille": pois,
                         "harm1_cfd_abs": abs(A), "harm1_exact_abs": abs(Aan),
                         "harm1_cfd_deg": math.degrees(np.angle(A)),
                         "harm1_exact_deg": math.degrees(np.angle(Aan)),
                         "harm1_rel_err": abs(A - Aan) / abs(Aan),
                         "residual_rms": rms})
            num_s += abs(a0 - pois); den_s += abs(pois)
            num_h += abs(A - Aan); den_h += abs(Aan)
        out["stations"][label] = {
            "steady_part_rel_err": num_s / den_s,
            "harmonic1_rel_err": num_h / den_h,
            "profile": rows,
        }
    return out


# ==========================================================================
# Discharge-coefficient audit
# ==========================================================================

BETA = math.sqrt(v.A_ORIFICE / v.A_PIPE)


def cd_audit(dp_throat: float, q: float, area: float, a_pipe: float) -> dict:
    """Three coefficients from the SAME measurement, so the record cannot
    keep quoting one of them against a literature value defined as another.

      Cd_naive  = Q / (A_o sqrt(2 dp/rho))
          The definition analyze_f9.py used. It is the coefficient of the
          reduced-order model's own formula dp = 0.5 rho (Q/(Cd A))^2, i.e.
          it assumes the approach velocity is zero.
      C_iso     = Cd_naive * sqrt(1 - beta^4)
          The ISO 5167 discharge coefficient, which carries the
          velocity-of-approach factor E = 1/sqrt(1-beta^4) explicitly.
          This is the ONLY one comparable with ISO's 0.60-0.62.
      E         = 1/sqrt(1-beta^4), reported alone because at beta -> 1 it,
          not the discharge coefficient, dominates.
    """
    beta = math.sqrt(area / a_pipe)
    b4 = beta ** 4
    cd_naive = q / (area * math.sqrt(2.0 * dp_throat / RHO))
    return {"beta": beta, "beta^4": b4, "E_approach": 1.0 / math.sqrt(1 - b4),
            "Cd_naive_no_approach_term": cd_naive,
            "C_iso_style": cd_naive * math.sqrt(1 - b4),
            "dp_inviscid_bernoulli_Pa":
                0.5 * RHO * (q / area) ** 2 * (1 - b4),
            "dp_measured_Pa": dp_throat}


def rom_gap_decomposition(cfd_cycle_mean_dp: float) -> dict:
    """Split the -94% ROM/CFD gap into named, separately checkable pieces.

    The record attributed it all to 'beta outside the ISO calibration
    range'. Three effects are stacked in it, and only the third is that.
    """
    phases = phase_points()
    rom = _cycle_weighted_loss(v.OPENING_ANGLE_DEG, phases)
    a = v.A_ORIFICE
    cd = 0.62
    # (1) same ROM formula, but averaged over the CFD's OWN waveform.
    #     ROM weights are stroke-volume weights over SYSTOLE ONLY; the CFD
    #     number is a time mean over the whole sinusoidal cycle. For a
    #     quadratic loss law the two differ by <Q^2>.
    msq_rom = sum(p.weight * p.flow_rate ** 2 for p in phases)
    msq_cfd = v.Q_MEAN ** 2 + 0.5 * v.Q_AMP ** 2      # <(Qm + Qa sin)^2>
    step1 = 0.5 * RHO * msq_cfd / (cd * a) ** 2
    # (2) add the velocity-of-approach factor the ROM formula omits
    step2 = step1 * (1.0 - BETA ** 4)
    # (3) whatever is left is the discharge coefficient being wrong
    return {
        "rom_as_published_Pa": rom,
        "cfd_cycle_mean_Pa": cfd_cycle_mean_dp,
        "total_deviation_pct": 100.0 * (cfd_cycle_mean_dp - rom) / rom,
        "mean_square_flow_rom": msq_rom,
        "mean_square_flow_cfd_waveform": msq_cfd,
        "step1_same_formula_cfd_waveform_Pa": step1,
        "step1_share_pct": 100.0 * (step1 - rom) / rom,
        "step2_plus_approach_factor_Pa": step2,
        "step2_share_pct": 100.0 * (step2 - step1) / rom,
        "residual_discharge_coefficient_Pa": cfd_cycle_mean_dp,
        "step3_share_pct": 100.0 * (cfd_cycle_mean_dp - step2) / rom,
        "implied_C_iso_from_residual": cd * math.sqrt(step2 / cfd_cycle_mean_dp),
    }


def waveform_compare(case_a: Path, case_b: Path, t_cycle: float,
                     a: int = 0, b: int = 1) -> dict:
    """Phase-aligned comparison of the LAST cycle of two runs of the same
    case that differ in one numerical control. Used for the timestep pair
    (maxCo 0.9 vs 0.45) and for the mesh pair.
    """
    ta, va = dp_series(case_a, a, b)
    tb, vb = dp_series(case_b, a, b)
    t_end = min(ta[-1], tb[-1])
    t0 = t_end - t_cycle
    wa = _resample_phase(ta, va, t0, t_end)
    wb = _resample_phase(tb, vb, t0, t_end)
    band = float(np.max(wa) - np.min(wa))
    sa = time_weighted_stats(ta, va, t0)
    sb = time_weighted_stats(tb, vb, t0)
    return {"cycle_window": [t0, t_end],
            "mean_a": sa["mean"], "mean_b": sb["mean"],
            "rel_mean_diff": abs(sb["mean"] - sa["mean"]) / abs(sa["mean"]),
            "rel_peak_diff": abs(float(np.max(wb)) - float(np.max(wa)))
                             / abs(float(np.max(wa))),
            "waveform_Linf_over_band": float(np.max(np.abs(wb - wa))) / band,
            "waveform_rms_over_band": float(np.sqrt(np.mean((wb - wa) ** 2))) / band}


def _observed_order(f3, f2, f1, r21, r32):
    """Observed order of convergence for three levels whose refinement
    ratios need NOT be equal.

    The familiar p = ln|e32/e21| / ln(r) is only valid when r21 == r32.
    With unequal ratios p solves the transcendental equation
    (Roache; Celik et al.)

        p = |ln|e32/e21| + q(p)| / ln(r21),
        q(p) = ln((r21^p - s)/(r32^p - s)),  s = sign(e32/e21)

    which is solved here by bisection on the residual. Returns None when no
    root exists in a sane range, which is itself informative: it means the
    three levels are not describable by a single power of h.
    """
    e21 = f1 - f2
    e32 = f2 - f3
    if e21 == 0 or e32 == 0:
        return None
    s = 1.0 if (e32 / e21) > 0 else -1.0

    def residual(p):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        return p - abs(math.log(abs(e32 / e21)) + q) / math.log(r21)

    lo, hi = 0.05, 20.0
    try:
        a, b = residual(lo), residual(hi)
    except (ValueError, ZeroDivisionError):
        return None
    if a * b > 0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        try:
            m = residual(mid)
        except (ValueError, ZeroDivisionError):
            return None
        if a * m <= 0:
            hi, b = mid, m
        else:
            lo, a = mid, m
    return 0.5 * (lo + hi)


def grid_triplet(dps: dict[str, float]) -> dict:
    """Roache grid-convergence index over three levels.

    Refuses to quote a GCI when the three values are not monotone, because
    the Richardson extrapolation it rests on does not apply there.
    """
    f3, f2, f1 = dps["coarse"], dps["base"], dps["fine"]
    r21, r32 = dps["r21"], dps["r32"]
    e21, e32 = f1 - f2, f2 - f3
    R = e21 / e32 if e32 else float("nan")
    out = {"f_coarse": f3, "f_base": f2, "f_fine": f1, "r21": r21, "r32": r32,
           "convergence_ratio_R": R}
    if not (0 < R < 1):
        out["verdict"] = ("NOT MONOTONE-CONVERGENT (R outside (0,1)); "
                          "Richardson extrapolation does not apply and no "
                          "GCI is quoted")
        out["relative_spread_coarse_to_fine"] = abs(f1 - f3) / abs(f1)
        return out
    p = _observed_order(f3, f2, f1, r21, r32)
    if p is None:
        out["verdict"] = "no single power of h fits these three levels"
        return out
    f_ext = f1 + e21 / (r21 ** p - 1)
    gci = 1.25 * abs(e21 / f1) / (r21 ** p - 1)
    out.update({"observed_order_p": p, "richardson_extrapolated": f_ext,
                "GCI_fine_pct": 100.0 * gci,
                "verdict": "monotone convergent"})
    return out


def grid_powerlaw_fit(hs, fs) -> dict:
    """Least-squares fit of f(h) = f0 - C h^p across ALL levels at once.

    A single triplet's observed order can be fooled by one noisy level; a
    fit over every level cannot, and its residuals say directly whether one
    power of h describes the whole sequence.
    """
    hs = np.asarray(hs, dtype=float)
    fs = np.asarray(fs, dtype=float)
    best = None
    for p in np.linspace(0.2, 4.0, 3801):          # p is the only nonlinearity
        A = np.stack([np.ones_like(hs), -hs ** p], axis=1)
        coef, *_ = np.linalg.lstsq(A, fs, rcond=None)
        r = fs - A @ coef
        ss = float(r @ r)
        if best is None or ss < best[0]:
            best = (ss, float(p), float(coef[0]), float(coef[1]))
    ss, p, f0, C = best
    A = np.stack([np.ones_like(hs), -hs ** p], axis=1)
    resid = (fs - A @ np.array([f0, C])).tolist()
    return {"f0_extrapolated": f0, "C": C, "observed_order_p": p,
            "residuals": resid,
            "max_abs_residual": max(abs(x) for x in resid)}


def rom_open_limit() -> dict:
    """Does the reduced-order loss law have a physical beta -> 1 limit?

    As the leaflets open the orifice tends to the full bore and the geometry
    tends to an unobstructed straight pipe. An ORIFICE loss must vanish in
    that limit: there is no orifice left. The screen's law
    ``dp = 0.5 rho (Q/(Cd A))^2`` instead tends to a finite floor, because
    nothing in it depends on the pipe area at all.

    The comparison quantity is the only loss a straight pipe of this bore
    actually has: fully developed Hagen-Poiseuille friction over the same
    0.3013 m the F9 mesh spans, cycle-weighted with the screen's own phase
    points and weights (the friction loss is linear in Q, so the weighting
    differs from the quadratic one).
    """
    import workflows.valve_study as vs
    phases = phase_points()
    mu = RHO * v.NU
    rows = []
    for ang in list(vs.CANDIDATE_ANGLES) + [90.0]:
        area = math.pi * (v.R_PIPE * math.sin(math.radians(min(ang, 90.0)))) ** 2
        beta = math.sqrt(area / v.A_PIPE)
        rom = sum(p.weight * 0.5 * RHO * (p.flow_rate / (0.62 * area)) ** 2
                  for p in phases)
        pois = sum(p.weight * 128.0 * mu * v.L_TOTAL * p.flow_rate
                   / (math.pi * v.D_PIPE ** 4) for p in phases)
        rows.append({"angle_deg": ang, "beta": beta,
                     "area_ratio": area / v.A_PIPE,
                     "rom_cycle_weighted_Pa": rom,
                     "poiseuille_friction_same_length_Pa": pois,
                     "rom_over_friction": rom / pois})
    return {"note": "beta = sin(opening angle); at 90 deg the bore is the pipe",
            "pipe_length_m": v.L_TOTAL, "rows": rows}


# ==========================================================================
def main():
    out: dict = {"criteria": {"TOL_CYC": TOL_CYC, "TOL_BAND": TOL_BAND,
                              "TOL_DRIFT": TOL_DRIFT}}

    # ---- F9-STAT-1 on every fixed-BC run ---------------------------------
    steady_cases = ["steady_q25", "steady_q50", "steady_q75", "steady_q100",
                    "steady_beta_50deg", "steady_beta_55deg",
                    "mesh_coarse_q100", "mesh_fine_q100"]
    out["stationarity"] = {}
    for c in steady_cases:
        case = HERE / c
        if not (case / "postProcessing").is_dir():
            out["stationarity"][c] = {"status": "no data"}
            continue
        rec = {}
        for lbl, a, b in (("dp_upstream_to_throat", 0, 1),
                          ("dp_upstream_to_downstream", 0, 2)):
            times, vals = dp_series(case, a, b)
            rec[lbl] = stat1(times, vals, lbl)
        # If the downstream tap oscillates, is the oscillation physical?
        # A jet/shear-layer instability sheds near St = f d / U_throat ~ 0.2.
        # Only asked of a signal that FAILED stationarity, and measured over
        # the last 40% of the run so several shedding periods are in the
        # window (the 10% stationarity tail is too short to time one).
        ang = {"steady_beta_50deg": 50.0, "steady_beta_55deg": 55.0}.get(c, 65.0)
        d_or = 2.0 * v.R_PIPE * math.sin(math.radians(ang))
        u_th = v.Q_PEAK / (math.pi * (d_or / 2) ** 2)
        f = None
        if rec["dp_upstream_to_downstream"]["verdict"] == "NOT_STATIONARY":
            times, vals = dp_series(case, 0, 2)
            per = measure_period(times, vals, 0.6 * times[-1])
            if per:
                f = 1.0 / per
                rec["dp_upstream_to_downstream"]["oscillation_period_s"] = per
                rec["dp_upstream_to_downstream"]["oscillation_freq_Hz"] = f
        else:
            rec["dp_upstream_to_downstream"].pop("oscillation_period_s", None)
            rec["dp_upstream_to_downstream"].pop("oscillation_freq_Hz", None)
        if f:
            rec["dp_upstream_to_downstream"]["strouhal_f_d_over_Uthroat"] = (
                f * d_or / u_th)
            rec["dp_upstream_to_downstream"]["orifice_d_m"] = d_or
            rec["dp_upstream_to_downstream"]["U_throat_ms"] = u_th
        out["stationarity"][c] = rec

    # ---- F9-CYC-1 on every pulsatile run ---------------------------------
    puls = [("pulsatile_physio", v.T_CYCLE), ("pulsatile_lowalpha", 4 * v.T_CYCLE),
            ("lowalpha_ext", 4 * v.T_CYCLE), ("physio_dt_half", v.T_CYCLE)]
    out["cycle_convergence"] = {}
    for c, T in puls:
        case = HERE / c
        if not (case / "postProcessing").is_dir():
            out["cycle_convergence"][c] = {"status": "no data"}
            continue
        rec = {}
        for lbl, a, b in (("dp_upstream_to_throat", 0, 1),
                          ("dp_upstream_to_downstream", 0, 2)):
            times, vals = dp_series(case, a, b)
            rec[lbl] = cyc1(times, vals, T, lbl)
        try:
            rec["volume_flux_BC_imposed"] = stroke_volume_per_cycle(case, T)
        except Exception as exc:                     # pragma: no cover
            rec["volume_flux_BC_imposed"] = {"status": f"unavailable: {exc}"}
        out["cycle_convergence"][c] = rec

    # ---- entrance-length prediction test ---------------------------------
    out["entrance_length_test"] = {}
    for c, T, blocks in (
            ("pulsatile_physio", v.T_CYCLE, {"2D_upstream_of_plate(3.0D_from_inlet)": 0}),
            ("pulsatile_lowalpha", 4 * v.T_CYCLE, {"2D_upstream_of_plate(3.0D_from_inlet)": 0}),
            ("womersley_probe_check", v.T_CYCLE,
             {"2D_upstream_of_plate(3.0D_from_inlet)": 0,
              "3D_upstream_of_plate(2.0D_from_inlet)": 1,
              "4D_upstream_of_plate(1.0D_from_inlet)": 2,
              "4.5D_upstream_of_plate(0.5D_from_inlet)": 3})):
        case = HERE / c
        if not (case / "postProcessing").is_dir():
            continue
        out["entrance_length_test"][c] = entrance_test(case, T, blocks)

    # ---- discharge-coefficient audit -------------------------------------
    audits = {}
    for c, ang in (("steady_q100", 65.0), ("steady_beta_50deg", 50.0),
                   ("steady_beta_55deg", 55.0)):
        case = HERE / c
        if not (case / "postProcessing").is_dir():
            continue
        times, vals = dp_series(case, 0, 1)
        st = stat1(times, vals, "dp_upstream_to_throat")
        theta = math.radians(ang)
        area = math.pi * (v.R_PIPE * math.sin(theta)) ** 2
        audits[c] = cd_audit(st["mean"], v.Q_PEAK, area, v.A_PIPE)
        audits[c]["angle_deg"] = ang
        audits[c]["stationarity_verdict"] = st["verdict"]
    out["discharge_coefficient_audit"] = audits

    physio = out["cycle_convergence"].get("pulsatile_physio", {})
    cyc_mean = None
    if isinstance(physio.get("dp_upstream_to_throat"), dict):
        cs = physio["dp_upstream_to_throat"]["cycles"]
        cyc_mean = cs[0]["mean"] if cs else None
    if cyc_mean:
        out["rom_gap_decomposition"] = rom_gap_decomposition(cyc_mean)
    out["rom_open_limit"] = rom_open_limit()

    # timestep sensitivity: same mesh, same cycle, maxCo 0.9 vs 0.45
    if (HERE / "physio_dt_half" / "postProcessing").is_dir():
        out["timestep_sensitivity"] = waveform_compare(
            HERE / "pulsatile_physio", HERE / "physio_dt_half", v.T_CYCLE)

    # grid convergence on the steady q100 reference point
    levels = {}
    for tag, case, h in (("coarse", "mesh_coarse_q100", 2.0),
                         ("base", "steady_q100", 1.0),
                         ("med", "mesh_med_q100", 1.0 / 1.5),
                         ("fine", "mesh_fine_q100", 0.5)):
        c = HERE / case
        if not (c / "postProcessing").is_dir():
            continue
        times, vals = dp_series(c, 0, 1)
        st = stat1(times, vals, "dp_upstream_to_throat")
        end_time = float([ln.split()[-1].rstrip(";") for ln in
                          (c / "system" / "controlDict").read_text().splitlines()
                          if ln.startswith("endTime")][0])
        levels[tag] = {"case": case, "h_rel": h, "mean": st["mean"],
                       "stationarity": st["verdict"], "t_end": times[-1],
                       "end_time_requested": end_time,
                       "stopped_early": times[-1] < 0.999 * end_time}
    # A level stopped before its requested endTime is admissible ONLY if it
    # passes F9-STAT-1 on its own tail AND every level that DID run to
    # endTime was already at its final value by that same time. Otherwise
    # "it looked flat when I stopped it" is exactly the hand-judgement this
    # round exists to remove.
    early = [t for t, L in levels.items() if L["stopped_early"]]
    for tag in early:
        t_stop = levels[tag]["t_end"]
        worst = 0.0
        for other, L in levels.items():
            if L["stopped_early"]:
                continue
            ts, vs = dp_series(HERE / L["case"], 0, 1)
            i = min(range(len(ts)), key=lambda k: abs(ts[k] - t_stop))
            worst = max(worst, abs(vs[i] - vs[-1]) / abs(vs[-1]))
        levels[tag]["completed_levels_settled_by_t_stop"] = worst
        if not (levels[tag]["stationarity"] == "STATIONARY"
                and worst < TOL_DRIFT * 2):
            levels[tag]["stationarity"] = "RUN INCOMPLETE"
    out["grid_levels"] = levels
    have = [t for t in ("coarse", "base", "med", "fine") if t in levels
            and levels[t]["stationarity"] == "STATIONARY"]
    # every consecutive triplet, so the observed order can be checked for
    # consistency instead of resting on one choice of three levels
    out["grid_convergence"] = {}
    if len(have) >= 2:
        out["grid_powerlaw_fit"] = grid_powerlaw_fit(
            [levels[t]["h_rel"] for t in have], [levels[t]["mean"] for t in have])
    for i in range(len(have) - 2):
        c3, c2, c1 = have[i], have[i + 1], have[i + 2]
        rec = grid_triplet({
            "coarse": levels[c3]["mean"], "base": levels[c2]["mean"],
            "fine": levels[c1]["mean"],
            "r21": levels[c2]["h_rel"] / levels[c1]["h_rel"],
            "r32": levels[c3]["h_rel"] / levels[c2]["h_rel"]})
        rec["levels_used"] = [c3, c2, c1]
        out["grid_convergence"][f"{c3}-{c2}-{c1}"] = rec
    # the constant-ratio triplet, if the levels allow one: r21 == r32 is the
    # configuration the index was derived for, so it is reported separately
    for i in range(len(have)):
        for j in range(i + 1, len(have)):
            for k in range(j + 1, len(have)):
                a, b, cc = have[i], have[j], have[k]
                r21 = levels[b]["h_rel"] / levels[cc]["h_rel"]
                r32 = levels[a]["h_rel"] / levels[b]["h_rel"]
                if abs(r21 - r32) > 1e-9:
                    continue
                rec = grid_triplet({"coarse": levels[a]["mean"],
                                    "base": levels[b]["mean"],
                                    "fine": levels[cc]["mean"],
                                    "r21": r21, "r32": r32})
                rec["levels_used"] = [a, b, cc]
                rec["note"] = "constant refinement ratio, the configuration the index assumes"
                out["grid_convergence"][f"{a}-{b}-{cc} (r constant)"] = rec

    # total-head check: are the two taps used for every Cd figure on the
    # same streamline with the same total head? If they are, the measured
    # dp is a reversible acceleration and carries no loss information.
    th = {}
    for c in ("steady_q25", "steady_q50", "steady_q75", "steady_q100",
              "steady_beta_50deg", "steady_beta_55deg", "mesh_coarse_q100",
              "mesh_med_q100", "mesh_fine_q100"):
        case = HERE / c
        if not (case / "postProcessing").is_dir():
            continue
        times, p = probe_field(case, "p")
        _, U = probe_field(case, "U")
        # tail-window means, not a single timestep, so a case whose
        # downstream field oscillates cannot be judged on one snapshot
        t0 = times[-1] - 0.1 * (times[-1] - times[0])
        hu = [p[0][i] + 0.5 * U[0][i] ** 2 for i in range(len(times))]
        ht = [p[1][i] + 0.5 * U[1][i] ** 2 for i in range(len(times))]
        dpv = [(p[0][i] - p[1][i]) * RHO for i in range(len(times))]
        h_up = time_weighted_stats(times, hu, t0)["mean"]
        h_th = time_weighted_stats(times, ht, t0)["mean"]
        dpm = time_weighted_stats(times, dpv, t0)["mean"]
        th[c] = {"window": [t0, times[-1]], "head_upstream_m2s2": h_up,
                 "head_throat_m2s2": h_th,
                 "head_loss_Pa": (h_up - h_th) * RHO,
                 "measured_dp_Pa": dpm,
                 "u_upstream": time_weighted_stats(times, U[0], t0)["mean"],
                 "u_throat": time_weighted_stats(times, U[1], t0)["mean"],
                 "head_loss_fraction_of_dp": (h_up - h_th) * RHO / dpm}
    out["total_head_check"] = th

    (HERE / "f9_criteria.json").write_text(json.dumps(out, indent=2, default=str))
    print("wrote", HERE / "f9_criteria.json")

    # ---- terse console summary -------------------------------------------
    print("\n-- F9-STAT-1 --")
    for c, rec in out["stationarity"].items():
        if "status" in rec:
            print(f"  {c:20s} {rec['status']}")
            continue
        for lbl, m in rec.items():
            print(f"  {c:20s} {lbl:28s} {m['verdict']:15s} "
                  f"mean={m['mean']:10.2f} band/mean={m['band_ratio']:.3e} "
                  f"drift={m['halves_drift']:.2e} trend={m['trend']:.2e} "
                  f"wshift={m['window_shift']:.2e}")
    print("\n-- F9-CYC-1 --")
    for c, rec in out["cycle_convergence"].items():
        if "status" in rec:
            print(f"  {c:20s} {rec['status']}")
            continue
        for lbl, m in rec.items():
            worst = m["consecutive"][0]["worst"] if m.get("consecutive") else float("nan")
            print(f"  {c:20s} {lbl:34s} {m['verdict']:20s} "
                  f"cycles={m['n_complete_cycles']} worst={worst:.3e}")
    print("\n-- entrance-length test --")
    for c, rec in out["entrance_length_test"].items():
        print(f"  {c}  alpha={rec['alpha']:.2f}  L_osc/D={rec['L_osc_over_D']:.2f} "
              f"L_steady/D={rec['L_steady_over_D_005Re']:.0f}")
        for s, m in rec["stations"].items():
            print(f"     {s:42s} steady-part err={m['steady_part_rel_err']*100:6.1f}%  "
                  f"harmonic-1 err={m['harmonic1_rel_err']*100:6.1f}%")
    print("\n-- Cd audit --")
    for c, m in out["discharge_coefficient_audit"].items():
        print(f"  {c:20s} beta={m['beta']:.4f} E={m['E_approach']:.3f} "
              f"Cd_naive={m['Cd_naive_no_approach_term']:.3f} "
              f"C_iso={m['C_iso_style']:.3f} "
              f"dp_meas={m['dp_measured_Pa']:.1f} dp_inviscid={m['dp_inviscid_bernoulli_Pa']:.1f}")
    if "rom_gap_decomposition" in out:
        d = out["rom_gap_decomposition"]
        print("\n-- ROM gap decomposition --")
        print(f"  ROM as published        {d['rom_as_published_Pa']:10.2f} Pa")
        print(f"  + CFD waveform          {d['step1_same_formula_cfd_waveform_Pa']:10.2f} Pa "
              f"({d['step1_share_pct']:+.1f}% of ROM)")
        print(f"  + approach factor       {d['step2_plus_approach_factor_Pa']:10.2f} Pa "
              f"({d['step2_share_pct']:+.1f}%)")
        print(f"  + true Cd (= CFD)       {d['cfd_cycle_mean_Pa']:10.2f} Pa "
              f"({d['step3_share_pct']:+.1f}%)")
        print(f"  total {d['total_deviation_pct']:+.1f}%   implied C_iso "
              f"{d['implied_C_iso_from_residual']:.3f}")


if __name__ == "__main__":
    main()
