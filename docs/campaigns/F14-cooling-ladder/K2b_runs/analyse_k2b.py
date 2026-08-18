#!/usr/bin/env python3
"""analyse_k2b.py -- read the K2b-pilot measurements out of the SOLVER'S OWN LOG.

    python3 analyse_k2b.py <caseDir> [<caseDir> ...] [--json out.json]

Nothing here recomputes a field.  Every number below is parsed from
`log.buoyantBoussinesqSimpleFoam`, which is the tracked artefact, because the
whole point of the S13 monitor convention is that a reader can re-derive the
verdict from the log a run actually printed.  `postProcessing/` is
`.gitignore`d and is deliberately not a source here.

WHAT IT REPORTS, AND WHERE EACH THING IS GOVERNED
-------------------------------------------------
1. S13 CONVERGENCE on the graded quantity T_in (mass-flow-weighted T over
   `rack_in`; spec section 7 row 1, and with N = 1 in the slice this IS
   T_in,max).  PEAK-TO-PEAK SPREAD over a FIXED window, thresholds read from
   `docs/physics_rules.yaml` block `thermal` and never copied here:
   `monitor_peak_to_peak_max_pct`, `monitor_window_iterations`,
   `monitor_sample_interval_iterations`, `monitor_min_samples`.
   Fewer than the minimum number of samples is REFUSED, not scored.
2. THE BOUSSINESQ SPAN, spec section 4's mandatory a-posteriori check:
   beta.(T_max - T_min) against `boussinesq_beta_dT_max`, reported at EVERY
   monitor sample and not only at the end, because a span that crosses the
   limit mid-run and comes back is a finding about the run and not a nuisance.
3. THE RECIRCULATION INDEX theta = (T_in - T_sup)/dT_rack (spec section 7 row
   3, defined there and self-contained), and the recirculated fraction implied
   by spec section 4's steady-mixing relation theta_out = dT/(1 - r).
4. THE OFFSET READBACK, which is the reachability control for
   `outletMappedUniformInlet`: T_out,area - T_in,area must equal dT_rack, and
   reads 0 on the BC's fallback branch (see build_k2b.py's docstring).
5. THE AVERAGING COMPARISON spec section 3.3 mandates: mass-flow-weighted
   against area-weighted on the same face.
6. THE MASS LEDGER, sum(phi) per open patch, which the enthalpy ledger rests on
   (`heat_balance_open_case_gates_mass_imbalance`).
7. THE GRAVITY READBACK, which is the only VALUE-level witness available for
   control C1.  The solver log prints `Reading g` and never prints g's value,
   so the log alone is a RECOGNITION control: it proves the file was opened,
   not what was in it.  `buoyantBoussinesqSimpleFoam` writes both `p` and
   `p_rgh` and they differ by exactly the `gh` field, so
   max|p - p_rgh| over the written fields IS g's magnitude times the domain
   height, read out of the solver's own output.  It reads 0.000 on a g = 0
   twin, which is what makes C1 a control that can fail rather than a twin
   whose only evidence is that its answer moved.  This one reads a written
   TIME DIRECTORY rather than the log; time directories are `.gitignore`d, so
   the number is reproduced by re-running the recipe, not by reading a
   tracked file, and the report says so.
"""

import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))

NUM = r"([-+0-9.eE]+)"
RE_TIME = re.compile(r"^Time = (\d+)\s*$")
RE_SFV = re.compile(r"^\s+(\w+)\((\w+)\) of (\w+) = " + NUM + r"\s*$")
RE_MIN = re.compile(r"^\s+min\((\w+|mag\(U\))\) = " + NUM + r" in cell")
RE_MAX = re.compile(r"^\s+max\((\w+|mag\(U\))\) = " + NUM + r" in cell")
RE_YPLUS = re.compile(r"^\s+patch (\S+) y\+ : min = " + NUM + r", max = " + NUM
                      + r", average = " + NUM)


def load_rules():
    """thermal thresholds, GOVERNED -- never copied into this script."""
    path = os.path.join(REPO, "docs", "physics_rules.yaml")
    want = ("monitor_peak_to_peak_max_pct", "monitor_window_iterations",
            "monitor_sample_interval_iterations", "monitor_min_samples",
            "boussinesq_beta_dT_max", "boussinesq_dT_max_K_at_TRef_300",
            "heat_balance_tol_pct", "monitor_min_resolved_ulp")
    out = {}
    inblock = False
    with open(path) as fh:
        for line in fh:
            if re.match(r"^thermal:\s*$", line):
                inblock = True
                continue
            if inblock and re.match(r"^\S", line):
                break
            if not inblock:
                continue
            m = re.match(r"^\s+(\w+):\s*([-+0-9.eE]+)\s*$", line)
            if m and m.group(1) in want:
                out[m.group(1)] = float(m.group(2))
    missing = [k for k in want if k not in out]
    if missing:
        raise SystemExit(f"REFUSE: physics_rules.yaml thermal is missing {missing}")
    return out, path


def read_field_internal(path):
    """The internalField of an ascii OpenFOAM volScalarField, as a list."""
    txt = open(path, errors="replace").read()
    m = re.search(r"^internalField\s+(uniform|nonuniform)([^;]*);", txt, re.M | re.S)
    if not m:
        return None
    if m.group(1) == "uniform":
        return [float(m.group(2).strip())]
    body = m.group(2)
    m2 = re.search(r"\(\s*(.*?)\s*\)\s*$", body, re.S)
    if not m2:
        return None
    return [float(x) for x in m2.group(1).split()]


def gravity_readback(case):
    """max|p - p_rgh| over the internal field of the latest written time.

    In buoyantBoussinesqSimpleFoam p = p_rgh + gh, so this IS |g|.h_domain
    read out of the solver's own written fields.  0 on a g = 0 case."""
    times = [d for d in os.listdir(case)
             if os.path.isdir(os.path.join(case, d)) and re.fullmatch(r"[1-9]\d*", d)]
    if not times:
        return None
    t = str(max(int(x) for x in times))
    pp = os.path.join(case, t, "p")
    pr = os.path.join(case, t, "p_rgh")
    if not (os.path.exists(pp) and os.path.exists(pr)):
        return None
    a, b = read_field_internal(pp), read_field_internal(pr)
    if a is None or b is None or len(a) != len(b):
        return None
    d = [x - y for x, y in zip(a, b)]
    return dict(time=int(t), n_cells=len(d), gh_min=min(d), gh_max=max(d),
                gh_span=max(d) - min(d), max_abs=max(abs(x) for x in d),
                source=f"{os.path.basename(case)}/{t}/p minus p_rgh "
                       f"(a written time directory, which is .gitignore'd)")


def read_case_txt(case):
    d = {}
    p = os.path.join(case, "CASE.txt")
    if os.path.exists(p):
        for line in open(p):
            parts = line.rstrip("\n").split(None, 1)
            if len(parts) == 2:
                d[parts[0]] = parts[1].strip()
    return d


def parse_log(path):
    """-> list of dicts, one per monitor sample, keyed by iteration."""
    samples = {}
    it = None
    yplus = {}
    with open(path, errors="replace") as fh:
        for line in fh:
            m = RE_TIME.match(line)
            if m:
                it = int(m.group(1))
                continue
            if it is None:
                continue
            m = RE_SFV.match(line)
            if m:
                op, patch, fld, val = m.groups()
                try:
                    samples.setdefault(it, {})[f"{op}:{patch}:{fld}"] = float(val)
                    samples[it][f"raw:{op}:{patch}:{fld}"] = val
                except ValueError:
                    pass
                continue
            m = RE_MIN.match(line)
            if m:
                samples.setdefault(it, {})[f"min:{m.group(1)}"] = float(m.group(2))
                continue
            m = RE_MAX.match(line)
            if m:
                samples.setdefault(it, {})[f"max:{m.group(1)}"] = float(m.group(2))
                continue
            m = RE_YPLUS.match(line)
            if m:
                yplus[m.group(1)] = dict(min=float(m.group(2)),
                                         max=float(m.group(3)),
                                         avg=float(m.group(4)), at_iter=it)
    return samples, yplus


def s13(series, rules, raw=None):
    """PEAK-TO-PEAK SPREAD over a FIXED window.  Not a residual reading, not an
    endpoint difference, not a fraction of the run -- physics_rules.yaml thermal
    section 1 states why each of those three failed on a measured case."""
    window = int(rules["monitor_window_iterations"])
    interval = int(rules["monitor_sample_interval_iterations"])
    minn = int(rules["monitor_min_samples"])
    tol = rules["monitor_peak_to_peak_max_pct"]
    if not series:
        return dict(verdict="REFUSED", reason="no samples in the log")
    last = series[-1][0]
    win = [(i, v) for i, v in series if i > last - window - interval // 2]
    if len(win) < minn:
        return dict(verdict="REFUSED",
                    reason=f"{len(win)} samples in the last {window} iterations, "
                           f"minimum is {minn}; a spread over that few points is "
                           f"not a spread",
                    n_samples=len(win))
    vals = [v for _, v in win]
    mean = sum(vals) / len(vals)
    p2p = max(vals) - min(vals)
    pct = 100.0 * p2p / abs(mean) if mean else float("inf")
    # THE NULL-VARIATION REFUSAL (physics_rules thermal.monitor_min_resolved_ulp,
    # MONITOR_STANDARD S13 clause added at v1.11). A spread the log cannot
    # resolve cannot distinguish "stopped moving" from "never started"; it is
    # REFUSED rather than scored, because scoring it returns the BEST POSSIBLE
    # score on the LEAST converged case. Measured here on K2bP_fine.
    if raw:
        sig = 0
        for t in raw:
            d = t.strip().lower().split("e")[0].replace("-", "").replace(".", "").lstrip("0")
            sig = max(sig, len(d) if d else 1)
        import math
        ulp = 10.0 ** (math.floor(math.log10(abs(mean))) - (sig - 1)) if mean and sig else 0.0
        floor = rules.get("monitor_min_resolved_ulp", 10)
        if ulp > 0 and p2p < floor * ulp:
            return dict(verdict="REFUSED", peak_to_peak=p2p, peak_to_peak_pct=pct,
                        print_resolution=ulp, resolved_ulp=p2p / ulp,
                        min_resolved_ulp=floor, mean=mean, n_samples=len(win),
                        reason=(f"spread {p2p:.6g} is {p2p/ulp:.3g} ulp of a series "
                                f"printed at {ulp:.6g}; below {floor:g} ulp it is not "
                                f"resolved by the log. Scoring it would have returned "
                                f"{pct:.6f} % -- a PASS -- on a quantity that may never "
                                f"have started moving."))
    return dict(verdict="PASS" if pct <= tol else "FAIL",
                window_iterations=window, sample_interval=interval,
                n_samples=len(win), first_iter=win[0][0], last_iter=win[-1][0],
                mean=mean, peak_to_peak=p2p, peak_to_peak_pct=pct,
                threshold_pct=tol,
                endpoint_diff_pct=100.0 * abs(vals[-1] - vals[0]) / abs(mean)
                if mean else None)


def analyse(case, rules, rules_path):
    logp = os.path.join(case, "log.buoyantBoussinesqSimpleFoam")
    if not os.path.exists(logp):
        return dict(case=os.path.basename(case), error="no solver log")
    meta = read_case_txt(case)
    dt_rack = float(meta.get("dT_rack", "12.0").split()[0])
    t_sup = float(meta.get("T_sup", "289.0").split()[0])
    beta = 3.333333333e-03      # constant/transportProperties, the case's own
    samples, yplus = parse_log(logp)
    iters = sorted(samples)
    if not iters:
        return dict(case=os.path.basename(case), error="no monitor samples in log")

    def series(key):
        return [(i, samples[i][key]) for i in iters if key in samples[i]]

    tin = series("weightedAverage:rack_in:T")
    tin_a = series("areaAverage:rack_in:T")
    tout_a = series("areaAverage:rack_out:T")
    tout_m = series("weightedAverage:rack_out:T")
    tret = series("weightedAverage:return:T")
    tmax = series("max:T")
    tmin = series("min:T")
    umax = series("max:mag(U)")

    r = dict(case=os.path.basename(case),
             rules_source=os.path.relpath(rules_path, REPO),
             iterations=iters[-1], n_monitor_samples=len(iters),
             dT_rack_K=dt_rack, T_sup_K=t_sup, beta=beta)

    # ---- 1. S13 on the graded quantity
    r["S13_T_in"] = s13(tin, rules, [samples[i]["raw:weightedAverage:rack_in:T"]
                                     for i in iters
                                     if "raw:weightedAverage:rack_in:T" in samples[i]][-9:])
    r["S13_note"] = ("graded quantity is T_in = mass-flow-weighted T over "
                     "rack_in; with N = 1 in the slice this is T_in,max")
    # THE SAME CRITERION ON A SECOND QUANTITY, AND IT IS NOT DECORATION.
    # T_in sits in the cold aisle, which on a balanced case is CONTAINED: an
    # oscillation in the room's free outlet never reaches it, and S13 read on
    # T_in alone is blind to a run that is still swinging everywhere else.
    # The return patch is the room's only free boundary and is the cheapest
    # second sentinel there is -- it is already printed at the same cadence.
    r["S13_T_return"] = s13(tret, rules, [samples[i]["raw:weightedAverage:return:T"]
                                          for i in iters
                                          if "raw:weightedAverage:return:T" in samples[i]][-9:])

    # ---- 2. the Boussinesq span, at EVERY sample, spec section 4
    spans = [(i, mx - mn) for (i, mx), (_, mn) in zip(tmax, tmin)]
    if spans:
        worst_i, worst = max(spans, key=lambda t: t[1])
        limit = rules["boussinesq_beta_dT_max"]
        r["boussinesq"] = dict(
            span_final_K=spans[-1][1], beta_span_final=beta * spans[-1][1],
            span_max_K=worst, beta_span_max=beta * worst, span_max_at_iter=worst_i,
            limit_beta_dT=limit,
            limit_span_K=rules["boussinesq_dT_max_K_at_TRef_300"],
            margin_final=limit - beta * spans[-1][1],
            breached_ever=bool(beta * worst >= limit),
            breach_iters=[i for i, s in spans if beta * s >= limit],
            T_max_final=tmax[-1][1], T_min_final=tmin[-1][1])

    # ---- 3. recirculation index and the implied recirculated fraction
    if tin and tout_m:
        theta_in = (tin[-1][1] - t_sup) / dt_rack
        theta_out = (tout_m[-1][1] - t_sup) / dt_rack
        # spec section 4: theta_out = dT/(1 - r)  ->  r = 1 - dT/(dT.theta_out)
        rec = 1.0 - 1.0 / theta_out if theta_out > 0 else None
        r["recirculation"] = dict(
            T_in_K=tin[-1][1], T_out_K=tout_m[-1][1],
            theta_in=theta_in, theta_out=theta_out,
            recirculated_fraction_r=rec,
            T_in_excess_over_supply_K=tin[-1][1] - t_sup,
            # what dT_rack this measured r would put at the 30.0 K line
            dT_rack_at_span_limit_K=(rules["boussinesq_dT_max_K_at_TRef_300"]
                                     * (1.0 - rec)) if rec is not None else None)

    # ---- 4. the offset readback: the reachability control for the BC.
    # AGAINST THE MASS-FLUX-WEIGHTED inlet average, because that is the branch
    # the BC actually takes (build_k2b.py docstring).  Read against the AREA
    # average instead and this control reports a 0.7 % error that is not an
    # error at all but the difference between two averages -- which is the same
    # mistake the spec made, only pointing the other way.
    if tin and tout_a:
        got = tout_a[-1][1] - tin[-1][1]
        r["offset_readback"] = dict(
            T_out_area_K=tout_a[-1][1], T_in_mass_weighted_K=tin[-1][1],
            T_in_area_K=tin_a[-1][1] if tin_a else None,
            offset_vs_area_average_K=(tout_a[-1][1] - tin_a[-1][1]) if tin_a else None,
            measured_offset_K=got, expected_offset_K=dt_rack,
            error_K=got - dt_rack,
            error_pct=100.0 * (got - dt_rack) / dt_rack,
            fallback_branch_would_read_K=0.0,
            history_K=[(i, samples[i]["areaAverage:rack_out:T"]
                        - samples[i]["weightedAverage:rack_in:T"])
                       for i in iters
                       if "areaAverage:rack_out:T" in samples[i]
                       and "weightedAverage:rack_in:T" in samples[i]][:3])

    # ---- 5. the averaging comparison spec section 3.3 mandates
    if tin and tin_a:
        r["averaging_comparison"] = dict(
            rack_in_mass_weighted_K=tin[-1][1], rack_in_area_weighted_K=tin_a[-1][1],
            difference_K=tin[-1][1] - tin_a[-1][1],
            difference_pct_of_dT=100.0 * (tin[-1][1] - tin_a[-1][1]) / dt_rack,
            note="the BC itself uses the MASS-FLUX-weighted branch; see build_k2b.py")

    # ---- 6. the mass ledger
    mass = {p: samples[iters[-1]].get(f"sum:{p}:phi")
            for p in ("tile", "return", "rack_in", "rack_out")}
    if all(v is not None for v in mass.values()):
        net = sum(mass.values())
        thru = sum(abs(v) for v in mass.values()) / 2.0
        r["mass_ledger"] = dict(per_patch_m3_s=mass, net_m3_s=net,
                                throughflow_m3_s=thru,
                                imbalance_pct=100.0 * abs(net) / thru,
                                tol_pct=rules["heat_balance_tol_pct"],
                                verdict="PASS" if 100.0 * abs(net) / thru
                                <= rules["heat_balance_tol_pct"] else "FAIL")

    if umax:
        r["U_max_final_m_s"] = umax[-1][1]
    if tret:
        r["T_return_K"] = tret[-1][1]
    if yplus:
        r["yPlus"] = yplus
    g = gravity_readback(case)
    if g:
        r["gravity_readback"] = g
    return r


def emit(r):
    print(f"\n=== {r['case']} " + "=" * (58 - len(r['case'])))
    if "error" in r:
        print(f"  ERROR: {r['error']}")
        return
    print(f"  iterations {r['iterations']}   monitor samples {r['n_monitor_samples']}"
          f"   dT_rack {r['dT_rack_K']} K   T_sup {r['T_sup_K']} K")
    s = r["S13_T_in"]
    print(f"  S13 (peak-to-peak of T_in over a fixed window): {s['verdict']}")
    if s["verdict"] == "REFUSED":
        print(f"      {s['reason']}")
        if "resolved_ulp" in s:
            print(f"      spread {s['peak_to_peak']:.3e}  print resolution "
                  f"{s['print_resolution']:.3e}  = {s['resolved_ulp']:.3g} ulp "
                  f"(floor {s['min_resolved_ulp']:g})")
    else:
        print(f"      window {s['window_iterations']} it @ every {s['sample_interval']}"
              f", {s['n_samples']} samples, iters {s['first_iter']}-{s['last_iter']}")
        print(f"      mean {s['mean']:.6f} K   peak-to-peak {s['peak_to_peak']:.3e} K"
              f" = {s['peak_to_peak_pct']:.5f} %   threshold {s['threshold_pct']} %")
        print(f"      (endpoint difference over the same window: "
              f"{s['endpoint_diff_pct']:.5f} % -- never larger, which is why the "
              f"spread is the conservative reading)")
    s2 = r.get("S13_T_return")
    if s2:
        print(f"  S13 on the RETURN temperature, the room's only free boundary: "
              f"{s2['verdict']}")
        if s2["verdict"] != "REFUSED":
            print(f"      mean {s2['mean']:.6f} K   peak-to-peak "
                  f"{s2['peak_to_peak']:.3e} K = {s2['peak_to_peak_pct']:.5f} %"
                  f"   threshold {s2['threshold_pct']} %")
    b = r.get("boussinesq")
    if b:
        print(f"  Boussinesq span check (spec 4, MANDATORY a posteriori):")
        print(f"      final  T_max {b['T_max_final']:.4f}  T_min {b['T_min_final']:.4f}"
              f"  span {b['span_final_K']:.4f} K   beta.span {b['beta_span_final']:.6f}"
              f"  limit {b['limit_beta_dT']}")
        print(f"      worst  span {b['span_max_K']:.4f} K at iteration "
              f"{b['span_max_at_iter']}   beta.span {b['beta_span_max']:.6f}")
        print(f"      breached ever: {b['breached_ever']}"
              + (f"  at iterations {b['breach_iters'][:8]}" if b["breach_iters"] else ""))
    c = r.get("recirculation")
    if c:
        print(f"  Recirculation (spec 7 row 3):")
        print(f"      T_in {c['T_in_K']:.4f} K  = T_sup + {c['T_in_excess_over_supply_K']:.4f} K"
              f"   theta_in {c['theta_in']:.4f}")
        print(f"      T_out {c['T_out_K']:.4f} K   theta_out {c['theta_out']:.4f}"
              f"   implied recirculated fraction r = {c['recirculated_fraction_r']:.4f}")
        print(f"      at this r a rack dT of {c['dT_rack_at_span_limit_K']:.2f} K "
              f"puts the domain span on the 30.0 K line")
    o = r.get("offset_readback")
    if o:
        print(f"  Offset readback (REACHABILITY control for outletMappedUniformInlet):")
        print(f"      T_out,area - T_in,mdot = {o['measured_offset_K']:.9f} K"
              f"   expected {o['expected_offset_K']} K"
              f"   error {o['error_K']:+.3e} K = {o['error_pct']:+.3e} %")
        print(f"      the BC's fallback branch would read "
              f"{o['fallback_branch_would_read_K']} K here, so this control can fail")
        if o.get("offset_vs_area_average_K") is not None:
            print(f"      read against the AREA average instead it would say "
                  f"{o['offset_vs_area_average_K']:.6f} K -- not an error in the "
                  f"BC, the difference between two averages")
    a = r.get("averaging_comparison")
    if a:
        print(f"  Averaging comparison (spec 3.3): mass-weighted {a['rack_in_mass_weighted_K']:.6f} K"
              f"  area-weighted {a['rack_in_area_weighted_K']:.6f} K")
        print(f"      difference {a['difference_K']:+.3e} K = "
              f"{a['difference_pct_of_dT']:+.4f} % of dT_rack")
    m = r.get("mass_ledger")
    if m:
        print(f"  Mass ledger: " + "  ".join(f"{k} {v:+.6f}" for k, v in
                                             m["per_patch_m3_s"].items()))
        print(f"      net {m['net_m3_s']:+.3e} m3/s on {m['throughflow_m3_s']:.4f} "
              f"through-flow = {m['imbalance_pct']:.5f} %  ({m['verdict']} at "
              f"{m['tol_pct']} %)")
    if "U_max_final_m_s" in r:
        print(f"  max|U| {r['U_max_final_m_s']:.4f} m/s   T_return "
              f"{r.get('T_return_K', float('nan')):.4f} K")
    g = r.get("gravity_readback")
    if g:
        print(f"  Gravity readback (VALUE-level witness; the log only prints "
              f"'Reading g'):")
        print(f"      max|p - p_rgh| = {g['max_abs']:.6f} m2/s2 over {g['n_cells']} "
              f"cells at time {g['time']}   (gh span {g['gh_span']:.6f})")
        print(f"      source: {g['source']}")
    y = r.get("yPlus")
    if y:
        print("  y+ (MEASURED, spec 6 -- never assumed):")
        for p, v in sorted(y.items()):
            print(f"      {p:12s} min {v['min']:.3f}  max {v['max']:.3f}"
                  f"  avg {v['avg']:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="+")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    rules, rules_path = load_rules()
    out = []
    for c in a.cases:
        r = analyse(os.path.abspath(c), rules, rules_path)
        out.append(r)
        emit(r)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
