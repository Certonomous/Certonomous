#!/usr/bin/env python3
"""report_diagnostics.py -- the REPORTED-AND-NEVER-GRADED half of the K0cX rung.

    python3 report_diagnostics.py       # reads gate_k0cx.json, writes diagnostics_k0cx.json

Kept SEPARATE from analyse_k0cx.py on purpose: the analyser decides verdicts and
nothing else, so a diagnostic added here can never accidentally become a gate
row.  Everything in this file grades nothing.

What is here, and which pre-registered question each answers:

  F2  the mesh trend on core stratification over THREE mesh levels
  F3  the relaminarisation diagnostics, per case, with the K0cS thresholds
  F4  the Prt sensitivity against the value MEASURED in this cavity
  C-REPRO  this build's kOmegaSST against K0cT's published numbers, read out of
           K0cT's own gate_k0ct.json rather than retyped
  near-identities: heat balance on a sealed cavity, y+, wall alphat
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "gate_k0cx.json")


def _find_up(relpath):
    d = HERE
    while True:
        cand = os.path.join(d, relpath)
        if os.path.exists(cand):
            return os.path.abspath(cand)
        if os.path.isdir(os.path.join(d, ".git")):
            return os.path.abspath(os.path.join(d, relpath))
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(relpath)
        d = parent


K0CT = _find_up("verification/runs/F14-cooling-ladder/K0cT_runs/gate_k0ct.json")

# K0cS_RESULTS.md Section 4, the relaminarised fine mesh.  These are the
# THRESHOLDS the pre-registration named, not new numbers.
K0CS_RELAM = dict(nut_over_nu_max=6.1e-4, bounding_k_events=25996,
                  fmu_implied_max=0.034, uv_peak=3.89e-17,
                  iterations=40000)
PREREG = dict(nut_over_nu_min=10.0, bounding_k_max=1000.0, fmu_min=0.5,
              uv_min=1e-5)


def main():
    if not os.path.isfile(GATE):
        sys.stderr.write("REFUSE: gate_k0cx.json not found; run analyse_k0cx.py "
                         "first. Nothing here re-measures a case.\n")
        return 2
    g = json.load(open(GATE))
    M = g["measurements"]
    out = {}

    # ---------------------------------------------------------------- F3 ----
    relam = {}
    for c in sorted(M):
        m = M[c]
        d = m["diagnostics"]
        if m["model"] == "laminar":
            continue
        iters = d.get("iterations") or 0
        bk = d.get("bounding_k_events") or 0
        relam[c] = dict(
            model=m["model"], rung=m["rung"], mesh=m["mesh_level"],
            cells=m["cells"], Prt=m["Prt"],
            nut_over_nu_max=d["nut_over_nu_max"],
            k_max=d["k_max"], eps_max=d["eps_max"],
            fmu_implied_max=d["fmu_implied_max"],
            cmu_k2_eps_max=d["cmu_k2_eps_max"],
            uv_peak_midheight=d["uv_peak_midheight"],
            bounding_k_events=bk,
            bounding_k_fraction=(bk / iters if iters else None),
            bounding_epsilon_events=d.get("bounding_epsilon_events"),
            bounding_omega_events=d.get("bounding_omega_events"),
            iterations=iters,
            yplus_max=m["yplus_max"],
            wall_alphat_over_alpha=d["wall_alphat_over_alpha"],
            Re_t_first_cell_midheight=d.get("Re_t_first_cell_midheight"),
            fmu_launder_sharma_formula_first_cell=d.get(
                "fmu_launder_sharma_formula_first_cell"),
            # the pre-registered thresholds, applied
            meets_prereg_nut=bool(d["nut_over_nu_max"] > PREREG["nut_over_nu_min"]),
            meets_prereg_bounding=bool(bk < PREREG["bounding_k_max"]),
            meets_prereg_fmu=(None if d["fmu_implied_max"] is None
                              else bool(d["fmu_implied_max"] > PREREG["fmu_min"])),
            meets_prereg_uv=(None if d["uv_peak_midheight"] is None
                             else bool(d["uv_peak_midheight"] > PREREG["uv_min"])),
            relaminarised=bool(d["nut_over_nu_max"] < 1.0))
    out["F3_relaminarisation"] = dict(
        k0cs_reference=K0CS_RELAM, prereg_thresholds=PREREG, cases=relam,
        any_relaminarised=any(v["relaminarised"] for v in relam.values()))

    # ---------------------------------------------------------------- F2 ----
    trend = {}
    for tag in ("SST", "KE", "LS", "LAM"):
        for rung in ("lo", "hi"):
            seq = []
            for lvl in ("c", "f", "x"):
                c = f"X_{rung}_{lvl}_{tag}"
                if c in M:
                    seq.append((lvl, M[c]["cells"], M[c]["S"], M[c]["Nu_avg"]))
            if len(seq) < 2:
                continue
            Sref = g["reference_parsed"]["S"][rung] if rung == "hi" else 0.0
            devs = [abs(s - Sref) for _, _, s, _ in seq]
            steps = []
            for i in range(len(seq) - 1):
                steps.append(dict(
                    frm=seq[i][0], to=seq[i + 1][0],
                    dS=seq[i + 1][2] - seq[i][2],
                    d_deviation=devs[i + 1] - devs[i],
                    moved=("TOWARD" if devs[i + 1] < devs[i] else "AWAY")))
            trend[f"{tag}_{rung}"] = dict(
                model=tag, rung=rung,
                levels=[dict(level=l, cells=n, S=s, Nu=nu) for l, n, s, nu in seq],
                deviations_from_reference=devs, steps=steps,
                total_movement=devs[-1] - devs[0],
                net_direction=("TOWARD" if devs[-1] < devs[0] else "AWAY"))
    out["F2_mesh_trend_on_S"] = trend

    # ---------------------------------------------------------------- F4 ----
    prt = {}
    for base, sens in (("X_lo_f_SST", "P_lo_f_SST"),
                       ("X_hi_f_SST", "P_hi_f_SST"),
                       ("X_hi_f_KE", "P_hi_f_KE")):
        if base not in M or sens not in M:
            continue
        b, s = M[base], M[sens]
        prt[sens] = dict(
            model=b["model"], rung=b["rung"],
            Prt_base=b["Prt"], Prt_measured=s["Prt"],
            Prt_change_pct=100.0 * (s["Prt"] - b["Prt"]) / b["Prt"],
            Nu_base=b["Nu_avg"], Nu_sens=s["Nu_avg"],
            dNu_pct=100.0 * (s["Nu_avg"] - b["Nu_avg"]) / b["Nu_avg"],
            S_base=b["S"], S_sens=s["S"], dS=s["S"] - b["S"],
            Vup_base=b["Vup"], Vup_sens=s["Vup"],
            nut_base=b["diagnostics"]["nut_over_nu_max"],
            nut_sens=s["diagnostics"]["nut_over_nu_max"],
            # the square cavity's own answer to the same question
            k0cs_dNu_pct=1.75,
            larger_than_square_cavity=None)
        prt[sens]["larger_than_square_cavity"] = bool(
            abs(prt[sens]["dNu_pct"]) > 1.75)
    out["F4_prt_sensitivity"] = prt

    # ------------------------------------------------------------ C-REPRO ---
    repro = {}
    if os.path.isfile(K0CT):
        kt = json.load(open(K0CT))["cases"]
        nug = None
        rg = os.path.join(os.path.dirname(K0CT), "regrade_nusselt.json")
        if os.path.isfile(rg):
            nug = json.load(open(rg))
        for mine, theirs in (("X_lo_f_SST", "T_lo_f"), ("X_hi_f_SST", "T_hi_f"),
                             ("X_lo_c_SST", "T_lo_c"), ("X_hi_c_SST", "T_hi_c")):
            if mine not in M or theirs not in kt:
                continue
            a, b = M[mine], kt[theirs]["measure"]
            def rel(x, y):
                return 100.0 * abs(x - y) / abs(y) if y else None
            repro[mine] = dict(
                k0ct_case=theirs,
                S=[a["S"], b["S"], rel(a["S"], b["S"])],
                Nu_avg=[a["Nu_avg"], 0.5 * (b["Nu_hot"] + b["Nu_cold"]),
                        rel(a["Nu_avg"], 0.5 * (b["Nu_hot"] + b["Nu_cold"]))],
                Vup=[a["Vup"], b["Vup"], rel(a["Vup"], b["Vup"])],
                Tmid_C=[a["Tmid_C"], b["Tmid_C"]],
                within_1pct=None)
            worst = max(v[2] for v in (repro[mine]["S"], repro[mine]["Nu_avg"],
                                       repro[mine]["Vup"]) if v[2] is not None)
            repro[mine]["worst_rel_pct"] = worst
            repro[mine]["within_1pct"] = bool(worst <= 1.0)
        if nug:
            repro["_k0ct_regrade_reference"] = nug["reference_parsed_from_addendum"]
    out["C_REPRO"] = repro

    # ------------------------------- Betts Table 1 centre-line turbulence ---
    # REPORTED, NOT GRADED.  The specification's Section 2.4 has no row for
    # either quantity, so no band exists and none is invented.  The comparison
    # is at the CENTRE-LINE on both sides, which is the like-for-like one:
    # K0cT_NUSSELT_REGRADE.md 5.1 compared a domain maximum against a
    # centre-line value and said so, and both are carried here.
    ct = {}
    R = g["reference_parsed"]
    for c in sorted(M):
        m = M[c]
        if m["model"] == "laminar":
            continue
        rr = m["rung"]
        nn = m["diagnostics"].get("nut_over_nu_centre")
        uu = m["diagnostics"].get("uv_centre")
        lo, hi = R["uv_centreline"][rr]
        ct[c] = dict(
            model=m["model"], rung=rr, mesh=m["mesh_level"], Prt=m["Prt"],
            nut_over_nu_centre=nn,
            nut_over_nu_centre_reference=R["nut_over_nu_centreline"][rr],
            nut_centre_E_pct=(None if nn is None else
                              100.0 * (nn - R["nut_over_nu_centreline"][rr])
                              / R["nut_over_nu_centreline"][rr]),
            nut_over_nu_domain_max=m["diagnostics"]["nut_over_nu_max"],
            uv_centre=uu, uv_centre_reference_range=[lo, hi],
            uv_centre_inside_range=(None if uu is None else bool(lo <= uu <= hi)),
            uv_centre_E_pct_vs_range_mid=(None if uu is None else
                                          100.0 * (uu - 0.5 * (lo + hi))
                                          / (0.5 * (lo + hi))))
    out["betts_table1_centreline_REPORTED_NOT_GRADED"] = ct

    # ------------------------------------------------- near-identities ------
    out["near_identities_REPORTED_NEVER_GATED"] = {
        c: dict(model=M[c]["model"], rung=M[c]["rung"], mesh=M[c]["mesh_level"],
                heat_balance_pct=M[c]["heat_balance_pct"],
                yplus_max=M[c]["yplus_max"],
                wall_alphat_over_alpha=M[c]["diagnostics"]["wall_alphat_over_alpha"],
                Nu_hot=M[c]["Nu_hot"], Nu_cold=M[c]["Nu_cold"])
        for c in sorted(M)}

    # ------------------------------------------------------------- cost -----
    tot_exec = 0.0
    tot_wall = 0.0
    per = {}
    for c in sorted(M):
        d = M[c]["diagnostics"]
        e = d.get("exec_seconds") or 0.0
        wsec = d.get("wall_seconds") or 0.0
        tot_exec += e
        tot_wall += wsec
        per[c] = dict(exec_seconds=e, wall_seconds=wsec,
                      core_minutes=e / 60.0, iterations=d.get("iterations"))
    out["cost"] = dict(per_case=per,
                       total_exec_core_minutes=tot_exec / 60.0,
                       total_wall_core_minutes=tot_wall / 60.0,
                       pilots_core_minutes=1.77,
                       rate_usd_per_core_hour=0.0513)
    out["cost"]["total_core_minutes"] = tot_exec / 60.0 + 1.77
    out["cost"]["total_usd"] = out["cost"]["total_core_minutes"] / 60.0 * 0.0513

    with open(os.path.join(HERE, "diagnostics_k0cx.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)

    # ------------------------------------------------------------- print ----
    print("F3  RELAMINARISATION DIAGNOSTICS  (K0cS fine mesh: nut/nu 6.1e-04, "
          "25 996 bounding-k of 40 000, fmu 0.034)")
    print("-" * 118)
    print(f"{'case':<15}{'model':>17}{'cells':>7}{'nut/nu max':>12}{'k max':>11}"
          f"{'fmu max':>10}{'bound k':>9}{'frac':>8}{'uv peak':>11}{'y+ max':>9}"
          f"{'relam':>7}")
    for c, v in relam.items():
        f = v["fmu_implied_max"]
        print(f"{c:<15}{v['model']:>17}{v['cells']:>7}{v['nut_over_nu_max']:>12.4g}"
              f"{(v['k_max'] or 0):>11.3g}{(f if f is not None else float('nan')):>10.4g}"
              f"{v['bounding_k_events']:>9.0f}"
              f"{(v['bounding_k_fraction'] or 0):>8.3f}"
              f"{(v['uv_peak_midheight'] or 0):>11.3g}{v['yplus_max']:>9.3f}"
              f"{'YES' if v['relaminarised'] else 'no':>7}")

    print("\nF2  MESH TREND ON CORE STRATIFICATION  (K0cS: SST moved AWAY 0.080, "
          "LS AWAY 0.158)")
    print("-" * 118)
    for k, v in trend.items():
        seq = "  ".join(f"{l['level']}:{l['S']:.4f}" for l in v["levels"])
        st = "  ".join(f"{s['frm']}->{s['to']} {s['moved']} {abs(s['d_deviation']):.4f}"
                       for s in v["steps"])
        print(f"{k:<10} {seq:<34} net {v['net_direction']:<7} "
              f"{abs(v['total_movement']):.4f}   [{st}]")

    print("\nF4  Prt SENSITIVITY AT THE MEASURED VALUE  (K0cS square cavity: "
          "dNu = -1.75 % for 0.85 -> 1.28)")
    print("-" * 118)
    for c, v in prt.items():
        print(f"{c:<13} {v['model']:<16} Prt {v['Prt_base']:.3f} -> "
              f"{v['Prt_measured']:.3f} ({v['Prt_change_pct']:+.1f} %)   "
              f"Nu {v['Nu_base']:.4f} -> {v['Nu_sens']:.4f} ({v['dNu_pct']:+.2f} %)   "
              f"dS {v['dS']:+.4f}   nut/nu {v['nut_base']:.2f} -> {v['nut_sens']:.2f}")

    print("\nC-REPRO  THIS BUILD AGAINST K0cT's PUBLISHED NUMBERS  (threshold 1 %)")
    print("-" * 118)
    for c, v in repro.items():
        if c.startswith("_"):
            continue
        print(f"{c:<13} vs {v['k0ct_case']:<10} S {v['S'][0]:.5f} / {v['S'][1]:.5f} "
              f"({v['S'][2]:.3f} %)   Nu {v['Nu_avg'][0]:.4f} / {v['Nu_avg'][1]:.4f} "
              f"({v['Nu_avg'][2]:.3f} %)   worst {v['worst_rel_pct']:.3f} %   "
              f"{'OK' if v['within_1pct'] else '*** EXCEEDS 1 % -- BUILD DEFECT ***'}")

    print("\nBETTS TABLE 1 CENTRE-LINE, REPORTED AND NOT GRADED  "
          "(nu_T/nu 35 lo / 55 hi;  u'v' 2.4-2.8e-3 lo / 4.2-5.0e-3 hi)")
    print("-" * 118)
    print(f"{'case':<15}{'model':>17}{'nut/nu centre':>15}{'ref':>6}{'E %':>9}"
          f"{'nut/nu max':>12}{'uv centre':>12}{'in range':>10}")
    for c, v in ct.items():
        e = v["nut_centre_E_pct"]
        print(f"{c:<15}{v['model']:>17}{(v['nut_over_nu_centre'] or 0):>15.3f}"
              f"{v['nut_over_nu_centre_reference']:>6.0f}"
              f"{(e if e is not None else float('nan')):>9.1f}"
              f"{v['nut_over_nu_domain_max']:>12.3f}"
              f"{(v['uv_centre'] or 0):>12.3g}"
              f"{str(v['uv_centre_inside_range']):>10}")

    print(f"\nCOST  {out['cost']['total_core_minutes']:.1f} core-minutes = "
          f"${out['cost']['total_usd']:.3f}   "
          f"(solver ExecutionTime basis; wall-clock sum "
          f"{out['cost']['total_wall_core_minutes']:.1f} core-minutes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
