#!/usr/bin/env python3
"""
The parabolic-inlet replicate of the constant-Ts Re = 25 and Re = 100 ladders,
compared LIKE FOR LIKE (h -> 0 against h -> 0, same stations, same estimator,
same reference) with the slug-inlet ladders recorded in dts.json.

REGISTERED IN `DIAGNOSTIC_PREDICTION.md` ("NEXT TEST, REGISTERED BEFORE IT IS
BUILT, 2026-08-20 evening") BEFORE ANY *_P CASE WAS BUILT.  The six cases
(D_Ts_Re25_P_c/m/f, L_Ts_P_c/m/f) are byte-identical to D_Ts_Re25_c/m/f and
L_Ts_c/m/f except the inlet entry of U, which is the exact Poiseuille profile
at the mesh's inlet face centroids with a flow-rate-exact scale (see
build_d_ts_p.py, whose verification printout is the proof of "nothing else").

The three registered predictions and the falsifying outcomes are quoted
verbatim below (PREDICTIONS) and each is printed next to the numbers that
decide it.  Nothing here is graded; no band is armed; no T1c verdict moves.

This script REUSES analyse_dts.py's machinery unchanged -- the strict
completion rule and DONE markers, the planted-zero convergence control
(analyse_pesweep.planted_zero_control), measurement at
analyse_t1c.amended_station, the station sensitivity, analyse_t1c.gci, the
heat-balance closure with its validated face geometry, and the Poiseuille
check -- and produces the SAME record per ladder, in dts_p.json, plus the
comparison block.

REFUSES (exit 2) until every one of the six cases passes the completion rule,
and writes NO marker for a case that has not; exactly as analyse_dts.py does.
Exit 0 = completed; 2 = refused.

AMENDMENT, 2026-08-20, DISCLOSED, MADE BEFORE ANY *_P_* CASE FINISHED.
Requested by a second session while the six solves were running; checked
immediately before the edit at 2026-08-20T21:11:40Z: `ls STATUS.*_P_*` ->
"ls: cannot access 'STATUS.*_P_*': No such file or directory" (no DONE.*_P_* either).  What changed, and nothing else: the
"unchanged within its own GCI band" test in prediction (1), the "well under
0.40 pp" resolution in prediction (2), and the falsifying clause no longer use
the SLUG ladder's GCI alone.  The slug Re = 25 GCI of 0.0022 % is a
station-mismatch artefact recorded in DIAGNOSTIC_PREDICTION.md (Addendum,
2026-08-20 evening: the observed order 4.88 is station-corrected to 2.25 and
"its 0.002 % GCI should be read as understated"), so a 0.002 pp tolerance
would fail prediction (1) by artefact.  The band is now
    max(slug GCI_pct, parabolic GCI_pct, corrected slug band)
with the corrected slug band recomputed from the station-corrected e21 and
order (CORRECTED_* constants below), and ALL THREE bands are printed beside
every delta so the reader sees which one decided.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t1c as T1C                                # noqa: E402
import analyse_pesweep as PES                            # noqa: E402
import analyse_dts as DTS                                # noqa: E402

NU_TS = DTS.NU_TS
PR = DTS.PR
PLANT = DTS.PLANT
LEVELS = DTS.LEVELS
LADDERS = [("Re25_P", 25.0, {l: f"D_Ts_Re25_P_{l}" for l in LEVELS}, "Re25"),
           ("Re100_P", 100.0, {l: f"L_Ts_P_{l}" for l in LEVELS}, "Re100")]
ALL_CASES = [(tag, Re, l, cases[l]) for tag, Re, cases, _ in LADDERS
             for l in LEVELS]
SLUG_JSON = os.path.join(HERE, "dts.json")
OUT_JSON = os.path.join(HERE, "dts_p.json")

GRAETZ_RESIDUAL_PCT = 0.0051       # entry residual at x* = 0.1255, from the md
POSTHOC_FLOOR_PCT = 0.082
POSTHOC_B = 134.0
POSTHOC_RE25_PCT = POSTHOC_FLOOR_PCT + POSTHOC_B / (25.0 * PR) ** 2   # +0.507
REGISTERED_DIFF_PP = 0.40

PREDICTIONS = {
    "P1_thermal_floor_not_hydrodynamic": (
        "If the Pe-dependent part is thermal (axial conduction) and the floor "
        "is not hydrodynamic: the Re = 25 h→0 excess stays at +0.51 % and "
        "the Re = 100 one at +0.11 %, each within its own GCI band of the "
        "slug-inlet value, and their difference stays near 0.40 pp."),
    "P2_hydrodynamic_Pe_term": (
        "If the Pe-dependent part is hydrodynamic under-development: the "
        "Re = 25 excess falls towards the Re = 100 value and the difference "
        "shrinks to well under 0.40 pp — by how much is not predicted, "
        "only the direction."),
    "P3_hydrodynamic_floor": (
        "If the floor is hydrodynamic: the Re = 100 excess falls from +0.11 % "
        "towards the Graetz entry residual at x* = 0.1255 quoted above."),
    "falsifying": (
        "if both excesses move by less than their GCI bands, the hydrodynamic "
        "explanation is refuted for both the floor and the Pe term, and the "
        "inlet-corner hypothesis (item 2 above) is next. If the post-hoc "
        "floor + 1/Pe² form is right and hydrodynamics are not involved, "
        "the Re = 25 parabolic-inlet point lands at +0.082 % + 134/17.75² "
        "= +0.507 %; if it lands elsewhere, that form is dropped without a "
        "replacement being fitted to the same four points again."),
}


# STATION-CORRECTED SLUG BANDS (DIAGNOSTIC_PREDICTION.md, "Addendum, 2026-08-20
# evening"): correcting the c/m/f Nusselt differences for the station mismatch
# with the measured fine-level x-slope (-0.32 pp/D) takes the Re = 25 observed
# order from 4.88 to 2.25 (Re = 100: 1.85 -> 2.15).  The GCI is recomputed
# from the corrected e21 (pp of Nu_ref, i.e. % of Nu to first order) at the
# corrected order: Fs e21 / (r^p - 1).  Re 25: 1.25 x 0.0375 / (1.6^2.25 - 1)
# = 0.0249 %, against the raw 0.0022 %.  Re 100: 1.25 x 0.0335 / (1.6^2.15 - 1)
# = 0.0240 %, BELOW the raw 0.0301 %, so the max() below keeps the raw one.
CORRECTED_E21_PP = {"Re25": 0.0375, "Re100": 0.0335}
CORRECTED_ORDER = {"Re25": 2.25, "Re100": 2.15}
CORRECTED_SLUG_BAND_PCT = {
    k: T1C.FS * CORRECTED_E21_PP[k] / (T1C.R_REFINE ** CORRECTED_ORDER[k] - 1.0)
    for k in CORRECTED_E21_PP}


def refuse(msg):
    print(msg)
    sys.exit(2)


def profile_deviation(case, station_xD):
    """Max |U_i / U_b,col - 2 (1 - (r_i/R_wall)^2)| over the column nearest
    station_xD, and the same for the slug-free parabola with U_b nominal."""
    d = DTS.cdir(case)
    t = T1C.latest_time(d)
    Cx = T1C.read_internal(os.path.join(d, t, "Cx"))
    Cy = T1C.read_internal(os.path.join(d, t, "Cy"))
    V = T1C.read_internal(os.path.join(d, t, "V"))
    U = T1C.read_internal(os.path.join(d, t, "U"), vector=True)
    R_wall = T1C.wall_radius(d)
    D = 2.0 * R_wall
    xs = sorted(set(round(v, 10) for v in Cx))
    xsel = min(xs, key=lambda v: abs(v - station_xD * D))
    idx = [i for i, v in enumerate(Cx) if round(v, 10) == xsel]
    Ub_col = sum(U[i][0] * V[i] for i in idx) / sum(V[i] for i in idx)
    dev = [U[i][0] / Ub_col - 2.0 * (1.0 - (Cy[i] / R_wall) ** 2) for i in idx]
    iw = max(idx, key=lambda i: Cy[i])
    return dict(sample_xD=xsel / D, n=len(idx),
                max_abs_dev_from_parabola=max(abs(v) for v in dev),
                rms_dev_from_parabola=math.sqrt(sum(v * v for v in dev) / len(dev)),
                near_wall_U_over_Ub=U[iw][0] / Ub_col,
                near_wall_parabola=2.0 * (1.0 - (Cy[iw] / R_wall) ** 2))


def main():
    if not os.path.isfile(SLUG_JSON):
        refuse(f"REFUSE: {SLUG_JSON} absent; there is no slug ladder to "
               "compare against")
    slug = json.load(open(SLUG_JSON))

    out = {"registered_in": "DIAGNOSTIC_PREDICTION.md, NEXT TEST 2026-08-20 "
                            "evening (parabolic inlet)",
           "compared_against": "dts.json (slug-inlet ladders Re25, Re100)",
           "reference_Nu_Ts": NU_TS, "Pr": PR,
           "saturation_floor": T1C.SATURATION_FLOOR,
           "refinement_ratio": T1C.R_REFINE, "Fs": T1C.FS,
           "predictions_verbatim": PREDICTIONS,
           "graetz_residual_pct": GRAETZ_RESIDUAL_PCT,
           "corrected_slug_band_pct": CORRECTED_SLUG_BAND_PCT,
           "corrected_e21_pp": CORRECTED_E21_PP,
           "corrected_order": CORRECTED_ORDER,
           "posthoc_Re25_pct": POSTHOC_RE25_PCT,
           "completion": {}, "markers": {}, "convergence": {},
           "measurements": {}, "station_sensitivity": {}, "ladders": {},
           "heat_balance": {}, "poiseuille": {}, "poiseuille_inlet_column": {},
           "profile_deviation": {}, "discarded": [], "not_a_result": [],
           "comparison": {}}

    # ---- 1. completion rule and DONE markers (analyse_dts, unchanged) ------
    print("1. STRICT COMPLETION RULE (all clauses must pass before a DONE "
          "marker is written)")
    bad = []
    for tag, Re, lvl, case in ALL_CASES:
        rec = DTS.completion(case)
        out["completion"][case] = rec
        flags = " ".join(f"{k}={'ok' if v else 'FAIL'}"
                         for k, v in rec["checks"].items())
        et = rec.get("endTime")
        # DTS.completion leaves wall_seconds / rc / nProcs unset for a case
        # with no STATUS file yet (unfinished), hence .get()
        print(f"  {case:14s} {'COMPLETE' if rec['complete'] else 'INCOMPLETE':10s}"
              f" latest={rec.get('latest_time')} endTime="
              f"{et if et is None else format(et, '.0f')}"
              f" ExecutionTime lines={rec.get('n_ExecutionTime')}"
              f" cells={rec.get('cells')} exec_s={rec.get('exec_seconds')}"
              f" wall_s={rec.get('wall_seconds')} nProcs={rec.get('nProcs')}"
              f" rc={rec.get('rc')} [{rec.get('status_source')}]")
        print(f"      {flags}")
        if not rec["complete"]:
            bad.append(case)
    if bad:
        refuse("REFUSE: the completion rule failed for " + ", ".join(bad) +
               "; no marker written for them and nothing below is a result")

    for tag, Re, lvl, case in ALL_CASES:
        p = os.path.join(HERE, f"DONE.{case}")
        new = DTS.marker_text(out["completion"][case])
        if os.path.isfile(p):
            old = open(p).read()
            if old == new:
                st = "already present, identical (idempotent)"
            else:
                print(f"  DONE.{case} exists with DIFFERENT content:\n"
                      f"--- on disk ---\n{old}--- computed ---\n{new}")
                refuse(f"REFUSE: DONE.{case} disagrees with the rule's "
                       f"result; it is NOT overwritten")
        else:
            open(p, "w").write(new)
            st = "WRITTEN"
        out["markers"][case] = st
        print(f"  DONE.{case:14s} {st}")
    missing = [c for _, _, _, c in ALL_CASES
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(missing))

    # ---- 2. iterative convergence with the planted-zero control -----------
    print("\n2. ITERATIVE CONVERGENCE, each zero controlled by a planted "
          f"{PLANT:.3e} K perturbation (acceptance: PLANT <= control <= "
          "real + PLANT)")
    unconverged = []
    for tag, Re, lvl, case in ALL_CASES:
        c = T1C.iterative_convergence(DTS.cdir(case))
        ctl = PES.planted_zero_control(case)
        rec = c["max_change"]
        got = ctl["max_change"]
        want = max(rec, PLANT)
        ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)
        print(f"  {case:14s} max change {rec:.3e} K (relative {c['relative']:.3e},"
              f" range {c['field_range']:.4f} K, between {c['between']})"
              f"  [{c['state']}]   planted control returns {got:.6e} "
              f"(expected max(real, plant) = {want:.6e}: "
              f"{'RECOVERED' if ok else 'BROKEN READER'})")
        out["convergence"][case] = dict(c, control_max_change=got,
                                        control_expected=want, control_ok=ok)
        if not ok:
            refuse("REFUSE: the convergence reader failed its planted control")
        if c["state"] != "CONVERGED":
            unconverged.append((case, rec))
    if unconverged:
        print("  NOT ITERATIVELY CONVERGED (kept, reported, NOT discarded): " +
              ", ".join(f"{c} ({v:.3e} K)" for c, v in unconverged))
    else:
        print("  all 6 cases CONVERGED")
    out["unconverged"] = [dict(case=c, max_change=v) for c, v in unconverged]

    # ---- 3. Nu at each case's own amended station --------------------------
    print(f"\n3. Nu AT EACH CASE'S OWN AMENDED STATION "
          f"(analyse_t1c.amended_station(Re, {PR}, {NU_TS}); the SAME station "
          f"as the slug ladder; discard if driving fraction < "
          f"{T1C.SATURATION_FLOOR})")
    print(f"  {'case':14s} {'Re':>5s} {'Pe':>7s} {'station':>8s} {'sample':>8s}"
          f" {'Nu':>10s} {'excess %':>9s} {'slug %':>9s} {'drive':>7s}"
          f" {'T_bulk':>9s} {'fRe':>8s} {'h_wall':>10s} {'ncol':>4s}")
    discarded_re = {}
    for tag, Re, cases, stag in LADDERS:
        station, lo, hi = T1C.amended_station(Re, PR, NU_TS)
        if station is None:
            refuse(f"REFUSE: no admissible station for Re = {Re}")
        S = slug["ladders"][stag]
        if abs(S["station_xD"] - station) > 1e-12:
            refuse(f"REFUSE: station {station} differs from the slug ladder's "
                   f"{S['station_xD']}; the comparison would not be like for like")
        out["ladders"][tag] = dict(Re=Re, Pe=Re * PR, station_xD=station,
                                   window_lo_xD=lo, window_hi_xD=hi,
                                   cases=cases, slug_ladder=stag,
                                   slug_cases=S["cases"], levels={})
        for lvl in LEVELS:
            case = cases[lvl]
            Re_txt = float(T1C.case_txt(DTS.cdir(case), "Re").split()[0])
            if Re_txt != Re:
                refuse(f"REFUSE: {case} CASE.txt says Re = {Re_txt}, ladder "
                       f"says {Re}")
            prof = T1C.case_txt(DTS.cdir(case), "inlet_profile")
            if not prof.startswith("parabolic"):
                refuse(f"REFUSE: {case} CASE.txt inlet_profile is '{prof}'")
            m = T1C.measure(DTS.cdir(case), station)
            m["excess_pct"] = 100.0 * (m["Nu"] - NU_TS) / NU_TS
            m["Re_case_txt"] = Re
            m["Pe"] = Re * PR
            m["station_xD_requested"] = station
            m["discarded"] = m["driving_fraction"] < T1C.SATURATION_FLOOR
            sl = S["levels"][lvl]
            m["slug_case"] = S["cases"][lvl]
            m["slug_excess_pct"] = sl["excess_pct"]
            m["slug_sample_xD"] = sl["sample_xD"]
            if abs(sl["sample_xD"] - m["sample_xD"]) > 1e-9:
                refuse(f"REFUSE: {case} sampled at x/D {m['sample_xD']} but "
                       f"{S['cases'][lvl]} at {sl['sample_xD']}")
            out["measurements"][case] = m
            out["ladders"][tag]["levels"][lvl] = m
            flag = ""
            if m["discarded"]:
                flag = (f"   DISCARDED (driving fraction "
                        f"{m['driving_fraction']:.4f} < "
                        f"{T1C.SATURATION_FLOOR}; NOT rescued)")
                out["discarded"].append(dict(
                    case=case, ladder=tag, driving_fraction=m["driving_fraction"],
                    reason="driving difference at its own station below the "
                           "10 % saturation floor (registered clause)"))
                discarded_re.setdefault(tag, []).append(case)
            print(f"  {case:14s} {Re:5.0f} {Re*PR:7.2f} {station:8.3f} "
                  f"{m['sample_xD']:8.4f} {m['Nu']:10.6f} {m['excess_pct']:+9.4f}"
                  f" {sl['excess_pct']:+9.4f} {m['driving_fraction']:7.4f} "
                  f"{m['T_bulk']:9.4f} {m['fRe']:8.4f} {m['near_wall_h']:10.3e}"
                  f" {m['n_cells_station']:4d}{flag}")

    print("\n  STATION SENSITIVITY on the fine level (REPORTED ONLY): Nu at lo "
          "and hi of the admissible window, slug spread alongside")
    for tag, Re, cases, stag in LADDERS:
        L = out["ladders"][tag]
        case = cases["f"]
        mlo = T1C.measure(DTS.cdir(case), L["window_lo_xD"])
        mhi = T1C.measure(DTS.cdir(case), L["window_hi_xD"])
        elo = 100.0 * (mlo["Nu"] - NU_TS) / NU_TS
        ehi = 100.0 * (mhi["Nu"] - NU_TS) / NU_TS
        ef = L["levels"]["f"]["excess_pct"]
        spread = abs(ehi - elo)
        ss_slug = slug["station_sensitivity"][stag]
        out["station_sensitivity"][tag] = dict(
            case=case, lo_xD_requested=L["window_lo_xD"],
            lo_xD_sampled=mlo["sample_xD"], Nu_lo=mlo["Nu"], excess_lo_pct=elo,
            driving_fraction_lo=mlo["driving_fraction"],
            hi_xD_requested=L["window_hi_xD"],
            hi_xD_sampled=mhi["sample_xD"], Nu_hi=mhi["Nu"], excess_hi_pct=ehi,
            driving_fraction_hi=mhi["driving_fraction"],
            spread_pp=spread, fine_excess_at_station_pct=ef,
            spread_over_abs_fine_excess=(spread / abs(ef) if ef else
                                         float("nan")),
            slug_spread_pp=ss_slug["spread_pp"],
            slug_excess_lo_pct=ss_slug["excess_lo_pct"],
            slug_excess_hi_pct=ss_slug["excess_hi_pct"])
        print(f"  {case:14s} lo x/D {mlo['sample_xD']:.4f}: excess {elo:+.4f} %"
              f" (slug {ss_slug['excess_lo_pct']:+.4f});  hi x/D "
              f"{mhi['sample_xD']:.4f}: excess {ehi:+.4f} % (slug "
              f"{ss_slug['excess_hi_pct']:+.4f}); drive_hi "
              f"{mhi['driving_fraction']:.4f};  spread {spread:.4f} pp (slug "
              f"{ss_slug['spread_pp']:.4f} pp);  fine excess at station "
              f"{ef:+.4f} %")

    # ---- 4. GCI per ladder -------------------------------------------------
    print("\n4. GCI PER LADDER (analyse_t1c.gci; r = 1.6, Fs = 1.25); "
          f"h -> 0 excess % = 100 (richardson - {NU_TS}) / {NU_TS}")
    for tag, Re, cases, stag in LADDERS:
        L = out["ladders"][tag]
        S = slug["ladders"][stag]
        nus = [L["levels"][l]["Nu"] for l in LEVELS]
        conv = T1C.gci(*nus)
        L["gci"] = conv
        exc = {l: L["levels"][l]["excess_pct"] for l in LEVELS}
        L["excess_pct_per_level"] = exc
        unconv = [l for l in LEVELS
                  if out["convergence"][cases[l]]["state"] != "CONVERGED"]
        L["unconverged_levels"] = unconv
        disc = discarded_re.get(tag, [])
        print(f"  {tag:8s} Re={Re:4.0f} Pe={Re*PR:6.2f}  Nu c/m/f = "
              f"{nus[0]:.6f} / {nus[1]:.6f} / {nus[2]:.6f}   per-level excess "
              f"% c/m/f = {exc['c']:+.4f} / {exc['m']:+.4f} / {exc['f']:+.4f}"
              f"   (slug {S['excess_pct_per_level']['c']:+.4f} / "
              f"{S['excess_pct_per_level']['m']:+.4f} / "
              f"{S['excess_pct_per_level']['f']:+.4f})")
        print(f"           gci: {conv}")
        print(f"           slug gci: {S['gci']}")
        why = []
        if disc:
            why.append(f"level(s) {', '.join(disc)} DISCARDED at the "
                       "saturation floor, which voids the h -> 0 excess")
        if conv["state"] != "CONVERGING":
            why.append(f"grid triple is {conv['state']}; no Richardson "
                       "extrapolate exists")
        if unconv:
            why.append(f"level(s) {', '.join(unconv)} not iteratively "
                       "converged (reported; the extrapolate is still computed "
                       "but flagged)")
        if conv["state"] == "CONVERGING" and not disc:
            L["h0_excess_pct"] = 100.0 * (conv["richardson"] - NU_TS) / NU_TS
            L["usable"] = True
            print(f"           order p = {conv['order']:.4f}, GCI = "
                  f"{conv['GCI_pct']:.4f} %, richardson Nu = "
                  f"{conv['richardson']:.6f}, h -> 0 excess = "
                  f"{L['h0_excess_pct']:+.4f} %   (slug h -> 0 "
                  f"{S['h0_excess_pct']:+.4f} %, slug GCI "
                  f"{S['gci'].get('GCI_pct', float('nan')):.4f} %)"
                  + ("   [FLAG: " + "; ".join(why) + "]" if why else ""))
        else:
            L["h0_excess_pct"] = None
            L["usable"] = False
            L["why_not_a_result"] = "; ".join(why)
            out["not_a_result"].append(dict(ladder=tag, why=L["why_not_a_result"]))
            print(f"           NOT A RESULT: {L['why_not_a_result']}")
        fres = [L["levels"][l]["fRe"] for l in LEVELS]
        L["fRe_gci"] = T1C.gci(*fres)
        print(f"           f.Re c/m/f = {fres[0]:.4f} / {fres[1]:.4f} / "
              f"{fres[2]:.4f}  (64 exact)  {L['fRe_gci']}")

    # ---- 6. heat-balance closure (analyse_dts.heat_balance) ----------------
    print("\n6. HEAT-BALANCE CLOSURE from the written fields and the mesh "
          "(kinematic units), with the slug case's closure and inlet "
          "conduction fraction alongside")
    print(f"  {'case':14s} {'closure':>10s} {'Qin_cond/Qw':>12s} "
          f"{'slug closure':>12s} {'slug Qin/Qw':>12s} {'mdot':>12s} "
          f"{'mdot out/in-1':>13s} {'dTb':>8s} {'Tb_first-Tin':>12s} geom")
    for tag, Re, lvl, case in ALL_CASES:
        hb = DTS.heat_balance(case)
        out["heat_balance"][case] = hb
        g = hb["geometry"]
        if not g["valid"]:
            refuse(f"REFUSE: face geometry for {case} does not reproduce the "
                   f"chord geometry to {DTS.GEOM_TOL:.0e}; no flux from it is "
                   "believed")
        scase = out["measurements"][case]["slug_case"]
        shb = slug["heat_balance"][scase]
        print(f"  {case:14s} {hb['closure_residual']:+10.3e} "
              f"{hb['Q_inlet_cond_over_Q_wall']:+12.4e} "
              f"{shb['closure_residual']:+12.3e} "
              f"{shb['Q_inlet_cond_over_Q_wall']:+12.4e} {hb['mdot']:12.6e} "
              f"{hb['mdot_rel_imbalance']:+13.2e} {hb['dTb_implied']:8.5f} "
              f"{hb['Tb_first_minus_T_in']:12.5f} "
              f"{'VALID' if g['valid'] else 'INVALID'}")
        hb["slug_case"] = scase
        hb["slug_closure_residual"] = shb["closure_residual"]
        hb["slug_Q_inlet_cond_over_Q_wall"] = shb["Q_inlet_cond_over_Q_wall"]

    # ---- 7. Poiseuille check: inlet-adjacent column AND the station --------
    print("\n7. POISEUILLE CHECK, centreline-cell U_x / U_bulk against 2.0 "
          "(the exact parabola at the centreline cell's radius is printed "
          "too) -- at the inlet-adjacent column and at the station.  If the "
          "inlet lever worked, the station value is ~1.9997 (the parabola at "
          "that cell), not the slug's 1.9942 / 1.9963.")
    print(f"  {'case':14s} {'column':>7s} {'x/D':>8s} {'U_cl/U_b':>9s} "
          f"{'parabola':>9s} {'dev %':>8s} {'slug U_cl/U_b':>13s} "
          f"{'maxdev':>9s} {'rms':>9s}")
    for tag, Re, cases, stag in LADDERS:
        L = out["ladders"][tag]
        for lvl in LEVELS:
            case = cases[lvl]
            for where, xD in (("inlet", 0.0), ("station", L["station_xD"])):
                pz = DTS.poiseuille(case, xD)
                pd = profile_deviation(case, xD)
                pz.update(profile=pd)
                key = "poiseuille" if where == "station" else \
                    "poiseuille_inlet_column"
                out[key].setdefault(tag, {})[lvl] = pz
                sp = slug["poiseuille"][stag]["ratio_column"] \
                    if (where == "station" and lvl == "f") else float("nan")
                print(f"  {case:14s} {where:>7s} {pz['sample_xD']:8.4f} "
                      f"{pz['ratio_column']:9.5f} "
                      f"{pz['parabola_at_cell_radius']:9.5f} "
                      f"{100*(pz['ratio_column']/pz['parabola_at_cell_radius']-1):+8.4f}"
                      f" {sp:13.5f} {pd['max_abs_dev_from_parabola']:9.2e} "
                      f"{pd['rms_dev_from_parabola']:9.2e}")
        out["profile_deviation"][tag] = {
            l: out["poiseuille"][tag][l]["profile"] for l in LEVELS}

    # ---- 8. LIKE-FOR-LIKE COMPARISON against the slug ladders --------------
    print("\n8. LIKE-FOR-LIKE COMPARISON: h -> 0 excess, parabolic inlet vs "
          "slug inlet (dts.json), same stations, same estimator, same "
          "reference")
    cmp = {}
    for tag, Re, cases, stag in LADDERS:
        L = out["ladders"][tag]
        S = slug["ladders"][stag]
        sg = S["gci"].get("GCI_pct")
        pg = L["gci"].get("GCI_pct")
        cg = CORRECTED_SLUG_BAND_PCT[stag]
        band = max(v for v in (sg, pg, cg) if v is not None)
        decided_by = " = ".join(lbl for v, lbl in ((sg, "slug GCI"),
                                                    (pg, "parabolic GCI"),
                                                    (cg, "corrected slug band"))
                                if v is not None and v == band)
        rec = dict(Re=Re, Pe=Re * PR,
                   slug_h0_pct=S["h0_excess_pct"], slug_gci_pct=sg,
                   corrected_slug_band_pct=cg, band_pct=band,
                   band_decided_by=decided_by,
                   slug_fine_pct=S["excess_pct_per_level"]["f"],
                   parabolic_h0_pct=L["h0_excess_pct"], parabolic_gci_pct=pg,
                   parabolic_fine_pct=L["excess_pct_per_level"]["f"])
        if L["h0_excess_pct"] is not None and S["h0_excess_pct"] is not None:
            dpp = L["h0_excess_pct"] - S["h0_excess_pct"]
            rec["delta_h0_pp"] = dpp
            rec["within_slug_gci"] = (sg is not None and abs(dpp) <= sg)
            rec["within_band"] = abs(dpp) <= band
            rec["delta_over_slug_gci"] = abs(dpp) / sg if sg else float("nan")
            rec["delta_over_band"] = abs(dpp) / band if band else float("nan")
        rec["delta_fine_pp"] = (L["excess_pct_per_level"]["f"] -
                                S["excess_pct_per_level"]["f"])
        cmp[tag] = rec
        print(f"  {tag:8s} Re = {Re:4.0f}: slug h -> 0 excess "
              f"{rec['slug_h0_pct']:+.4f} %   parabolic h -> 0 excess "
              + (f"{rec['parabolic_h0_pct']:+.4f} %   difference "
                 f"{rec['delta_h0_pp']:+.4f} pp;  bands: slug GCI {sg:.4f} %, "
                 f"parabolic GCI {pg if pg is None else round(pg, 4)} %, "
                 f"corrected slug {cg:.4f} % -> band = max = {band:.4f} % "
                 f"({decided_by}); |delta| = {rec['delta_over_band']:.2f} x band"
                 f" -> {'WITHIN' if rec['within_band'] else 'OUTSIDE'}"
                 if rec.get("parabolic_h0_pct") is not None
                 else f"NOT A RESULT ({L.get('why_not_a_result')})"))
        print(f"           fine-level excess: slug {rec['slug_fine_pct']:+.4f} %"
              f"  parabolic {rec['parabolic_fine_pct']:+.4f} %  difference "
              f"{rec['delta_fine_pp']:+.4f} pp")

    c25, c100 = cmp["Re25_P"], cmp["Re100_P"]
    both = (c25.get("parabolic_h0_pct") is not None and
            c100.get("parabolic_h0_pct") is not None)
    diff_slug = c25["slug_h0_pct"] - c100["slug_h0_pct"]
    diff_par = (c25["parabolic_h0_pct"] - c100["parabolic_h0_pct"]) if both \
        else None
    cmp["Re25_minus_Re100_slug_pp"] = diff_slug
    cmp["Re25_minus_Re100_parabolic_pp"] = diff_par
    cmp["registered_difference_pp"] = REGISTERED_DIFF_PP
    print(f"\n  Re25 - Re100 h -> 0 difference: slug {diff_slug:+.4f} pp "
          f"(registered 'near 0.40 pp');  parabolic "
          + (f"{diff_par:+.4f} pp;  change {diff_par-diff_slug:+.4f} pp"
             if diff_par is not None else "NOT A RESULT"))

    # ---- the three registered predictions, verbatim, with the numbers ------
    print("\n  REGISTERED PREDICTIONS (verbatim from DIAGNOSTIC_PREDICTION.md) "
          "and the numbers that decide them.  DIAGNOSTIC: 'consistent' is not "
          "'passes'.")
    verdicts = {}
    d25 = c25.get("delta_h0_pp")
    d100 = c100.get("delta_h0_pp")
    # P1
    print(f"\n  (1) \"{PREDICTIONS['P1_thermal_floor_not_hydrodynamic']}\"")
    if both:
        p1 = (c25["within_band"] and c100["within_band"])
        def bands(c):
            return (f"bands slug {c['slug_gci_pct']:.4f} / parabolic "
                    f"{c['parabolic_gci_pct']:.4f} / corrected slug "
                    f"{c['corrected_slug_band_pct']:.4f} %, max = "
                    f"{c['band_pct']:.4f} % [{c['band_decided_by']}]")
        print(f"      Re 25: {c25['slug_h0_pct']:+.4f} -> "
              f"{c25['parabolic_h0_pct']:+.4f} % (moved {d25:+.4f} pp; "
              f"{bands(c25)}: {'within' if c25['within_band'] else 'OUTSIDE'})")
        print(f"      Re 100: {c100['slug_h0_pct']:+.4f} -> "
              f"{c100['parabolic_h0_pct']:+.4f} % (moved {d100:+.4f} pp; "
              f"{bands(c100)}: {'within' if c100['within_band'] else 'OUTSIDE'})")
        print(f"      difference {diff_slug:+.4f} -> {diff_par:+.4f} pp")
        print(f"      -> {'CONSISTENT' if p1 else 'NOT consistent'}: "
              + ("both unchanged within their max() bands"
                 if p1 else "at least one excess moved by more than its band"))
        verdicts["P1"] = dict(consistent=p1, delta25_pp=d25, delta100_pp=d100)
    else:
        print("      -> cannot be decided: an h -> 0 excess is NOT A RESULT")
    # P2
    print(f"\n  (2) \"{PREDICTIONS['P2_hydrodynamic_Pe_term']}\"")
    if both:
        # "well under 0.40 pp": the difference must shrink by more than the
        # two max() bands combined (the resolution of the comparison), in the
        # registered direction
        band_sum = c25["band_pct"] + c100["band_pct"]
        shrink = diff_slug - diff_par
        well_under = shrink > band_sum and diff_par < REGISTERED_DIFF_PP - band_sum
        p2 = (d25 < 0 and not c25["within_band"] and well_under)
        print(f"      Re 25 moved {d25:+.4f} pp "
              f"({'towards' if d25 < 0 else 'away from'} the Re 100 value; "
              f"{abs(d25)/c25['band_pct']:.2f} x its band {c25['band_pct']:.4f} %"
              f" [{c25['band_decided_by']}]);  "
              f"difference {diff_slug:+.4f} -> {diff_par:+.4f} pp (shrink "
              f"{shrink:+.4f} pp against the combined bands {band_sum:.4f} pp = "
              f"{c25['band_pct']:.4f} + {c100['band_pct']:.4f}"
              f": {'well under 0.40 pp' if well_under else 'NOT well under 0.40 pp'})")
        print(f"      -> {'CONSISTENT' if p2 else 'NOT consistent'}")
        verdicts["P2"] = dict(consistent=p2, diff_slug_pp=diff_slug,
                              diff_parabolic_pp=diff_par)
    else:
        print("      -> cannot be decided")
    # P3
    print(f"\n  (3) \"{PREDICTIONS['P3_hydrodynamic_floor']}\"")
    if both:
        gap_slug = c100["slug_h0_pct"] - GRAETZ_RESIDUAL_PCT
        gap_par = c100["parabolic_h0_pct"] - GRAETZ_RESIDUAL_PCT
        p3 = (d100 < 0 and not c100["within_band"] and
              abs(gap_par) < abs(gap_slug))
        print(f"      Re 100: {c100['slug_h0_pct']:+.4f} -> "
              f"{c100['parabolic_h0_pct']:+.4f} % (moved {d100:+.4f} pp, "
              f"{abs(d100)/c100['band_pct']:.2f} x its band {c100['band_pct']:.4f} %"
              f" [{c100['band_decided_by']}]); Graetz "
              f"entry residual at x* = 0.1255 is +{GRAETZ_RESIDUAL_PCT:.4f} %; "
              f"gap to it {gap_slug:+.4f} -> {gap_par:+.4f} pp "
              f"({100*(1-abs(gap_par)/abs(gap_slug)):+.1f} % of the gap closed)")
        print(f"      -> {'CONSISTENT' if p3 else 'NOT consistent'}")
        verdicts["P3"] = dict(consistent=p3, gap_slug_pp=gap_slug,
                              gap_parabolic_pp=gap_par,
                              graetz_residual_pct=GRAETZ_RESIDUAL_PCT)
    else:
        print("      -> cannot be decided")
    # falsifying / post-hoc
    print(f"\n  FALSIFYING OUTCOMES: \"{PREDICTIONS['falsifying']}\"")
    if both:
        refuted = (c25["within_band"] and c100["within_band"])
        ph_gap = c25["parabolic_h0_pct"] - POSTHOC_RE25_PCT
        ph_ok = (c25["parabolic_gci_pct"] is not None and
                 abs(ph_gap) <= c25["parabolic_gci_pct"])
        print(f"      both excesses moved by less than their max() bands "
              f"(Re 25 {c25['band_pct']:.4f} % [{c25['band_decided_by']}], "
              f"Re 100 {c100['band_pct']:.4f} % [{c100['band_decided_by']}]): "
              f"{refuted} -> hydrodynamic explanation "
              f"{'REFUTED for floor and Pe term; inlet-corner hypothesis is next' if refuted else 'NOT refuted by this test'}")
        print(f"      post-hoc floor + B/Pe^2 at Re 25: "
              f"{POSTHOC_FLOOR_PCT:+.3f} + {POSTHOC_B:.0f}/{25*PR:.2f}^2 = "
              f"{POSTHOC_RE25_PCT:+.4f} %; parabolic Re 25 h -> 0 = "
              f"{c25['parabolic_h0_pct']:+.4f} % (gap {ph_gap:+.4f} pp vs its "
              f"own GCI {c25['parabolic_gci_pct']:.4f} %) -> "
              f"{'lands there' if ph_ok else 'lands elsewhere: the form is DROPPED, no replacement fitted'}")
        verdicts["falsifying"] = dict(hydrodynamic_refuted=refuted,
                                      posthoc_Re25_pct=POSTHOC_RE25_PCT,
                                      posthoc_gap_pp=ph_gap,
                                      posthoc_lands=ph_ok)
    cmp["verdicts"] = verdicts
    out["comparison"] = cmp

    # ---- per-case record ----------------------------------------------------
    print("\nPER-CASE RECORD")
    print(f"  {'case':14s} {'cells':>6s} {'wall_s':>8s} {'exec_s':>9s} "
          f"{'nProcs':>6s} {'conv':>14s} {'Nu':>10s} {'excess %':>9s} "
          f"{'slug %':>9s} {'closure':>10s} {'Qin_cond/Qw':>11s}")
    out["per_case"] = {}
    for tag, Re, lvl, case in ALL_CASES:
        c = out["completion"][case]
        m = out["measurements"][case]
        hb = out["heat_balance"][case]
        cv = out["convergence"][case]
        out["per_case"][case] = dict(
            ladder=tag, level=lvl, Re=Re, cells=c["cells"],
            wall_seconds=c["wall_seconds"], exec_seconds=c["exec_seconds"],
            nProcs=c["nProcs"], convergence_state=cv["state"],
            Nu=m["Nu"], excess_pct=m["excess_pct"], discarded=m["discarded"],
            slug_case=m["slug_case"], slug_excess_pct=m["slug_excess_pct"],
            closure_residual=hb["closure_residual"],
            Q_inlet_cond_over_Q_wall=hb["Q_inlet_cond_over_Q_wall"])
        print(f"  {case:14s} {c['cells']:6d} {c['wall_seconds']:8.1f} "
              f"{c['exec_seconds']:9.2f} {c['nProcs']:6d} {cv['state']:>14s} "
              f"{m['Nu']:10.6f} {m['excess_pct']:+9.4f} {m['slug_excess_pct']:+9.4f} "
              f"{hb['closure_residual']:+10.3e} "
              f"{hb['Q_inlet_cond_over_Q_wall']:+11.4e}")

    with open(OUT_JSON, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(f"\nwrote {OUT_JSON}")
    print("DIAGNOSTIC, NOT GRADED: no band, no pass/fail, no T1c verdict moves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
