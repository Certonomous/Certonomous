#!/usr/bin/env python3
"""F9 analysis: parse probe output from the steady reference runs and the two
pulsatile runs, build the CFD dp(Q) map, check cycle-to-cycle periodicity,
evaluate the three gates, and compare against the ROM (valve_study.py) at
matched conditions (65 deg opening).

Run from anywhere; paths are relative to this file's directory.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mpmath as mp
mp.mp.dps = 30

HERE = Path(__file__).resolve().parent
SDK = HERE.parents[3] / "sdk"
CURRIC = HERE.parents[3] / "models" / "curriculum" / "aortic_valve"
for p in (SDK, CURRIC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from workflows import valve_pulsatile_cfd as v  # noqa: E402
from workflows.tmr_verification import (  # noqa: E402
    time_weighted_stats, measure_period, halves_drift)
from waveform import phase_points  # noqa: E402
from workflows.valve_study import _cycle_weighted_loss  # noqa: E402

RHO = v.RHO


def parse_probe_file(path: Path):
    """Return (times, {probe_index: [values...]}) for a probes .../p or U file.
    U rows hold vectors '(ux uy uz)'; only ux is kept (this is a pipe flow,
    radial/tangential components are ~0 by construction)."""
    times = []
    data: dict[int, list[float]] = {}
    n_probes = None
    with path.open() as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("#"):
                if line.startswith("# Probe"):
                    idx = int(line.split()[2])
                    n_probes = max(n_probes or 0, idx + 1)
                continue
            parts = line.split()
            t = float(parts[0])
            rest = " ".join(parts[1:])
            if "(" in rest:
                # vector field: split on ) ( boundaries after stripping outer parens
                rest = rest.strip()
                vecs = rest.replace(")(", ") (").split(") (")
                vals = []
                for vv in vecs:
                    vv = vv.strip("() ")
                    vals.append(float(vv.split()[0]))  # ux only
            else:
                vals = [float(x) for x in parts[1:]]
            times.append(t)
            for i, val in enumerate(vals):
                data.setdefault(i, []).append(val)
    return times, data


def steady_dp(case_dir: Path, tail_frac: float = 0.1) -> dict:
    """Time-weighted dp = rho*(p_upstream - p_throat) over the tail window,
    plus a flatness check (peak-to-trough / mean) so a not-yet-settled case
    is flagged, not silently reported."""
    p_path = case_dir / "postProcessing" / "probes1" / "0" / "p"
    times, p = parse_probe_file(p_path)
    t_end = times[-1]
    t_start = t_end * (1.0 - tail_frac)
    up = time_weighted_stats(times, p[0], t_start)
    th = time_weighted_stats(times, p[1], t_start)
    dn = time_weighted_stats(times, p[2], t_start)
    dp_series = [(p[0][i] - p[1][i]) * RHO for i in range(len(times))]
    dp_stats = time_weighted_stats(times, dp_series, t_start)
    drift = halves_drift(times, dp_series, t_start, t_end)
    return {
        "t_end": t_end,
        "dp_upstream_to_throat_Pa": dp_stats["mean"] if dp_stats else None,
        "dp_band_Pa": dp_stats["band"] if dp_stats else None,
        "dp_upstream_to_downstream_Pa": (up["mean"] - dn["mean"]) * RHO
                                        if up and dn else None,
        "flatness_relative_drift": drift["relative_drift"] if drift else None,
    }


def fit_power_law(qs, dps):
    """dp = k * Q^n via log-log least squares."""
    import statistics
    xs = [math.log(q) for q in qs]
    ys = [math.log(dp) for dp in dps]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    k = math.exp(intercept)
    return k, slope


def cd_from_dp(q: float, dp: float, area: float) -> float | None:
    if dp <= 0:
        return None
    return q / (area * math.sqrt(2.0 * dp / RHO))


def womersley_profile(alpha: float, R: float, q_mean: float, q_amp: float,
                      omega: float, t: float, y_list):
    """Analytic Womersley (1955) velocity profile, u(r,t), for a pipe flow
    driven by Q(t) = q_mean + q_amp*sin(omega t): a steady Poiseuille
    component (from q_mean) plus the closed-form oscillatory Womersley
    component (from q_amp), superposed by linearity of the governing
    (laminar, fully-developed) equation. y = r/R in [0,1].
    """
    i = mp.mpc(0, 1)
    Lambda = i ** mp.mpf("1.5") * alpha    # i^(3/2) * alpha
    j0_L = mp.besselj(0, Lambda)
    j1_L = mp.besselj(1, Lambda)
    g_avg = 1 - (2 * j1_L) / (Lambda * j0_L)
    out = []
    for y in y_list:
        u_steady = 2 * q_mean / (mp.pi * R ** 2) * (1 - y ** 2)
        g = 1 - mp.besselj(0, Lambda * y) / j0_L
        u_osc = mp.im((q_amp / (mp.pi * R ** 2 * g_avg)) * g
                      * mp.e ** (i * omega * t))
        out.append(float(u_steady + u_osc))
    return out


def profile_flatness(u_values) -> float | None:
    """Centerline / area-weighted-mean velocity: 2.0 for a parabola (steady
    Poiseuille), -> 1.0 as the profile flattens toward plug flow."""
    if not u_values or u_values[-1] == 0:
        return None
    return u_values[0] / (sum(u_values) / len(u_values))


def womersley_comparison(case_dir: Path, t_cycle: float, alpha: float):
    """CFD radial profile (probes 3..11 at station X_PROFILE) vs the
    analytic Womersley profile, at several phases in the last full cycle."""
    p_path = case_dir / "postProcessing" / "probes1" / "0" / "p"
    if not p_path.exists():
        return {"status": "no data"}
    u_path = case_dir / "postProcessing" / "probes1" / "0" / "U"
    times, U = parse_probe_file(u_path)
    t_end = times[-1]
    if t_end < t_cycle:
        return {"status": "insufficient run length for one full cycle"}
    t_start = t_end - t_cycle
    r_list = [(i + 0.5) / v.N_RADIAL_PROBES * 0.92 * v.R_PIPE
             for i in range(v.N_RADIAL_PROBES)]
    y_list = [r / v.R_PIPE for r in r_list]
    omega = 2.0 * math.pi / t_cycle
    phases = []
    for frac in (0.0, 0.25, 0.5, 0.75):
        t_target = t_start + frac * t_cycle
        idx = min(range(len(times)), key=lambda k: abs(times[k] - t_target))
        cfd_profile = [U[3 + j][idx] for j in range(v.N_RADIAL_PROBES)]
        t_local = times[idx] - t_start          # phase measured from cycle start
        analytic = womersley_profile(alpha, v.R_PIPE, v.Q_MEAN, v.Q_AMP,
                                     omega, t_local, y_list)
        cfd_flat = profile_flatness(cfd_profile)
        an_flat = profile_flatness(analytic)
        rel_err = (sum(abs(c - a) for c, a in zip(cfd_profile, analytic))
                  / max(sum(abs(a) for a in analytic), 1e-12))
        phases.append({
            "t_over_T": round(frac, 3), "t_actual": times[idx],
            "cfd_profile": cfd_profile, "analytic_profile": analytic,
            "cfd_flatness": cfd_flat, "analytic_flatness": an_flat,
            "mean_abs_rel_error": rel_err,
        })
    return {"alpha": alpha, "station_x": v.X_PROFILE, "phases": phases}


def unsteady_dp_series(case_dir: Path):
    p_path = case_dir / "postProcessing" / "probes1" / "0" / "p"
    times, p = parse_probe_file(p_path)
    dp = [(p[0][i] - p[1][i]) * RHO for i in range(len(times))]
    return times, dp


def cycle_analysis(case_dir: Path, t_cycle: float, n_cycles_avail: float):
    times, dp = unsteady_dp_series(case_dir)
    t_end = times[-1]
    result = {"t_end": t_end, "n_cycles_requested": n_cycles_avail}
    if t_end < t_cycle:
        result["periodicity"] = "insufficient run length for even one cycle"
        return result, times, dp
    # last full cycle window
    t_start = max(0.0, t_end - t_cycle)
    stats = time_weighted_stats(times, dp, t_start)
    result["last_cycle_mean_dp_Pa"] = stats["mean"] if stats else None
    result["last_cycle_band_Pa"] = stats["band"] if stats else None
    if t_end >= 2 * t_cycle:
        t_prev_start = max(0.0, t_end - 2 * t_cycle)
        drift = halves_drift(times, dp, t_prev_start, t_end)
        result["cycle_to_cycle_drift"] = drift["relative_drift"] if drift else None
        result["first_cycle_mean_dp_Pa"] = drift["first_half_mean"] if drift else None
        result["second_cycle_mean_dp_Pa"] = drift["second_half_mean"] if drift else None
    else:
        result["cycle_to_cycle_drift"] = None
        result["note"] = "fewer than 2 full cycles available; periodicity not established"
    return result, times, dp


def main():
    root = HERE
    out = {}

    # ---- steady reference map ----
    Qpeak = v.Q_PEAK
    levels = {"q25": 0.25 * Qpeak, "q50": 0.50 * Qpeak,
             "q75": 0.75 * Qpeak, "q100": 1.00 * Qpeak}
    steady = {}
    for tag, Q in levels.items():
        d = root / f"steady_{tag}"
        if not (d / "postProcessing" / "probes1" / "0" / "p").exists():
            steady[tag] = {"Q": Q, "status": "no data yet"}
            continue
        rec = steady_dp(d)
        rec["Q"] = Q
        rec["Cd_cfd"] = cd_from_dp(Q, rec["dp_upstream_to_throat_Pa"], v.A_ORIFICE)
        steady[tag] = rec
    out["steady_reference_map"] = steady

    ready = [s for s in steady.values() if "dp_upstream_to_throat_Pa" in s
            and s["dp_upstream_to_throat_Pa"] is not None]
    if len(ready) >= 2:
        qs = [s["Q"] for s in ready]
        dps = [s["dp_upstream_to_throat_Pa"] for s in ready]
        k, n = fit_power_law(qs, dps)
        out["steady_powerlaw_fit"] = {"k": k, "n": n,
                                      "form": "dp = k * Q^n"}

    # ---- pulsatile runs ----
    T_phys = v.T_CYCLE
    T_low = 4.0 * v.T_CYCLE
    for name, T, expect_cycles in (("pulsatile_physio", T_phys, 3.0),
                                   ("pulsatile_lowalpha", T_low, 1.5)):
        d = root / name
        p_path = d / "postProcessing" / "probes1" / "0" / "p"
        if not p_path.exists():
            out[name] = {"status": "no data yet"}
            continue
        rec, times, dp = cycle_analysis(d, T, expect_cycles)
        rec["alpha"] = v.womersley_alpha(T)
        rec["t_cycle"] = T

        # Gate 1: quasi-steady-map prediction along this run's own Q(t),
        # cycle-time-weighted, vs the run's actual cycle-weighted CFD dp.
        if "steady_powerlaw_fit" in out and rec.get("last_cycle_mean_dp_Pa") is not None:
            k, n = out["steady_powerlaw_fit"]["k"], out["steady_powerlaw_fit"]["n"]
            t_end = times[-1]
            t_start = max(0.0, t_end - T)
            omega = 2.0 * math.pi / T
            qs_dp = []
            for t in times:
                if t < t_start:
                    continue
                Q_t = v.Q_MEAN + v.Q_AMP * math.sin(omega * t)
                qs_dp.append(max(Q_t, 0.0))
            dp_qs_series = [k * (q ** n) if q > 0 else 0.0 for q in qs_dp]
            t_window = [t for t in times if t >= t_start]
            qs_stats = time_weighted_stats(t_window, dp_qs_series, t_start)
            rec["quasi_steady_predicted_cycle_mean_dp_Pa"] = (
                qs_stats["mean"] if qs_stats else None)
            if qs_stats:
                rec["gate1_deviation_from_quasi_steady_pct"] = (
                    100.0 * (rec["last_cycle_mean_dp_Pa"] - qs_stats["mean"])
                    / qs_stats["mean"])

        # Gate 2: analytic Womersley profile comparison
        rec["womersley_gate"] = womersley_comparison(d, T, v.womersley_alpha(T))

        out[name] = rec

    # Gate 3: matched-condition comparison against the ROM (valve_study.py,
    # 65 deg opening -- the same angle this whole geometry is built at).
    phases = phase_points()
    rom_cycle_loss = _cycle_weighted_loss(65.0, phases)
    out["gate3_rom_comparison"] = {"rom_cycle_weighted_loss_Pa": rom_cycle_loss,
                                   "rom_discharge_coeff": 0.62}
    physio = out.get("pulsatile_physio", {})
    if physio.get("last_cycle_mean_dp_Pa") is not None:
        cfd_val = physio["last_cycle_mean_dp_Pa"]
        out["gate3_rom_comparison"]["cfd_cycle_weighted_dp_Pa"] = cfd_val
        out["gate3_rom_comparison"]["deviation_pct"] = (
            100.0 * (cfd_val - rom_cycle_loss) / rom_cycle_loss)

    (root / "f9_analysis.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
