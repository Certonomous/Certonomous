#!/usr/bin/env python3
"""report_diagnostics.py -- the REPORTED-AND-NEVER-GRADED measurements of K0cS.

    python3 report_diagnostics.py       # writes diagnostics_k0cs.json

Everything here is a measurement that the specification (Section 3.3) keeps out
of the graded set, plus the method sensitivities that quantify how much a
grading choice could have moved a verdict.  None of it is a gate row and none of
it may be reported as one.

Kept separate from analyse_k0cs.py on purpose: the analyser decides verdicts and
nothing else, so a diagnostic added here can never accidentally become a row.
"""
import json
import math
import os
import sys
import importlib.util as _u

HERE = os.path.dirname(os.path.abspath(__file__))
_s = _u.spec_from_file_location("a", os.path.join(HERE, "analyse_k0cs.py"))
A = _u.module_from_spec(_s); _s.loader.exec_module(A)

CASES = ["S_SST_c", "S_SST_f", "S_KE_c", "S_KE_f", "S_LS_c", "S_LS_f",
         "C1_laminar", "C2_seed_d100", "C3_prt128", "C4_adiabatic"]
# Ampofo Table 2, pp. 3556-3557, parsed from the PDF text at analysis time.
TABLE2 = os.path.join(HERE, "ampofo_table2_midheight.tsv")


def table2():
    if not os.path.isfile(TABLE2):
        A.refuse(f"REFUSE: {TABLE2} is missing; the mid-height traverse "
                 "comparison has no reference and is not guessed.")
    rows = []
    for line in open(TABLE2):
        if line.startswith("#"):
            continue
        p = line.split()
        if len(p) >= 11:
            rows.append([float(v) for v in p[:11]])
    return rows


def one(case):
    d = os.path.join(HERE, case)
    t = A.latest_time(d)
    A.foam(d, f"postProcess -func writeCellCentres -time {t} > log.cc 2>&1")
    cx = A.read_internal(os.path.join(d, t, "Cx"))
    cy = A.read_internal(os.path.join(d, t, "Cy"))
    T = A.read_internal(os.path.join(d, t, "T"))
    U = A.read_internal(os.path.join(d, t, "U"), vector=True)
    Tw = A.read_patch(os.path.join(d, t, "T"), "hotWall")
    at = A.read_patch(os.path.join(d, t, "alphat"), "hotWall")
    L = float(A.case_txt(d, "L").split()[0])
    dT = float(A.case_txt(d, "dT").split()[0])
    nu = float(A.case_txt(d, "nu").split()[0])
    Pr = float(A.case_txt(d, "Pr"))
    Tc = float(A.case_txt(d, "T_cold").split()[0])
    alpha = nu / Pr
    xs = sorted(set(round(v, 12) for v in cx))
    ys = sorted(set(round(v, 12) for v in cy))
    idx = {(round(x, 12), round(y, 12)): i for i, (x, y) in enumerate(zip(cx, cy))}
    w = A.face_widths(ys, L)

    # --- wall-gradient METHOD sensitivity -------------------------------
    # Ampofo p. 3564 and Tian p. 859 both extracted the wall gradient by a
    # LINEAR BEST FIT over the first 6-9 near-wall measuring points.  The
    # analyser grades on the two-point wall gradient.  On a solved field the
    # two need not agree, and how much they disagree is a property of the
    # model's near-wall structure, not of the experiment.
    meth = {}
    for label, N in (("two_point", 1), ("lsq_first_6", 6), ("lsq_first_9", 9)):
        vals = []
        for j, y in enumerate(ys):
            Tf = Tw[j] if len(Tw) > 1 else Tw[0]
            aeff = 1.0
            if at is not None:
                aeff = 1.0 + (at[j] if len(at) > 1 else at[0]) / alpha
            if N == 1:
                g = (T[idx[(xs[0], y)]] - Tf) / xs[0]
            else:
                px = [0.0] + [xs[i] for i in range(N)]
                pv = [Tf] + [T[idx[(xs[i], y)]] for i in range(N)]
                g = A.lsq_slope(px, pv)
            vals.append(-(L / dT) * g * aeff)
        meth[label] = sum(v * ww for v, ww in zip(vals, w)) / sum(w)
    meth["spread_pct"] = 100.0 * (max(meth.values()) - min(meth.values())) \
        / meth["two_point"]

    # --- conductive-layer linearity, the assumption the reference rests on
    yj = min(ys, key=lambda y: abs(y - 0.5 * L)); j = ys.index(yj)
    px = [0.0]; pv = [Tw[j] if len(Tw) > 1 else Tw[0]]
    for x in xs:
        if x <= 0.002:
            px.append(x); pv.append(T[idx[(x, yj)]])
    sl = A.lsq_slope(px, pv); mean = sum(pv) / len(pv)
    ic = mean - sl * (sum(px) / len(px))
    ss_res = sum((v - (sl * x + ic)) ** 2 for x, v in zip(px, pv))
    ss_tot = sum((v - mean) ** 2 for v in pv)

    # --- mid-height traverse against Ampofo Table 2 ----------------------
    below = max([y for y in ys if y <= 0.5 * L])
    above = min([y for y in ys if y >= 0.5 * L])
    f = 0.0 if above == below else (0.5 * L - below) / (above - below)
    pxn = [x / L for x in xs]
    vv = [U[idx[(x, below)]][1] + f * (U[idx[(x, above)]][1] - U[idx[(x, below)]][1])
          for x in xs]
    th = [(T[idx[(x, below)]] + f * (T[idx[(x, above)]] - T[idx[(x, below)]]) - Tc) / dT
          for x in xs]

    def ip(tg, arr):
        for i in range(len(pxn) - 1):
            if pxn[i] <= tg <= pxn[i + 1]:
                g = (tg - pxn[i]) / (pxn[i + 1] - pxn[i])
                return arr[i] + g * (arr[i + 1] - arr[i])
        return arr[-1]

    rows = table2()
    core = [r for r in rows if 0.1 <= r[0] <= 0.9]
    bl = [r for r in rows if r[0] < 0.1 or r[0] > 0.9]

    def rms(sel, col, arr):
        e = [ip(r[0], arr) - r[col] for r in sel]
        return math.sqrt(sum(x * x for x in e) / len(e))

    mm = A.measure(d, case)
    up, dn = mm["Vpeak"], mm["Vmin"]
    return dict(
        case=case, model=mm.get("model"),
        wall_gradient_method=meth,
        conductive_layer_linearity=dict(
            r2=1 - ss_res / ss_tot, points=len(px),
            max_dev_K=max(abs(v - (sl * x + ic)) for x, v in zip(px, pv))),
        midheight_traverse_vs_ampofo_table2=dict(
            stations=len(rows),
            theta_rms_K_boundary_layers=rms(bl, 5, th) * dT,
            theta_rms_K_core=rms(core, 5, th) * dT,
            v_rms_ms_boundary_layers=rms(bl, 1, vv),
            v_rms_ms_core=rms(core, 1, vv)),
        antisymmetry_defect_pct=100.0 * abs(abs(up) - abs(dn)) / max(abs(up), abs(dn)),
        theta_centre=mm["theta_centre"],
        heat_balance_pct=mm["heat_balance_pct"],
        nut_over_nu_max=mm["nut_over_nu_max"],
        k_max=mm["k_max"], vrms_isotropic=mm["vrms_isotropic"])


def main():
    out = {}
    for c in CASES:
        if not os.path.isfile(os.path.join(HERE, f"DONE.{c}")):
            print(f"  {c}: no completion marker, skipped")
            continue
        out[c] = one(c)
        d = out[c]
        print(f"{c:<14} Nu method spread {d['wall_gradient_method']['spread_pct']:5.2f} %  "
              f"theta rms BL {d['midheight_traverse_vs_ampofo_table2']['theta_rms_K_boundary_layers']:5.2f} K  "
              f"core {d['midheight_traverse_vs_ampofo_table2']['theta_rms_K_core']:5.2f} K  "
              f"antisym {d['antisymmetry_defect_pct']:5.2f} %  "
              f"theta_c {d['theta_centre']:.4f}  heatbal {d['heat_balance_pct']:.4f} %")
    with open(os.path.join(HERE, "diagnostics_k0cs.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
