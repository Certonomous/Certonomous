#!/usr/bin/env python3
"""
T9a-D REGISTERED PREDICTIONS -- a 1-D finite-volume emulator of the composite
wall, run BEFORE any D_* case exists.

WHAT THIS IS.  It is NOT an instrument and it grades NOTHING.  It is the
arithmetic that turns Sanaa's three qualitative hypotheses into numbers that
can be written down before the solver answers, so that the T9a-D rows are
graded against a registered prediction rather than against whatever comes out.

WHAT IT REPRODUCES.  laplacianFoam's steady discrete operator on the T9a wall,
exactly:

  * one cell row in x, layer interfaces on faces, uniform spacing per layer;
  * internal face conductance  g = k_f / d,  d the centre-to-centre distance,
    k_f the face conductivity produced by the fvSchemes laplacian(DT,T) entry:
       Gauss linear   ->  k_f = w k_P + (1-w) k_N        (arithmetic, w the
                                                          linear/cd weight)
       Gauss harmonic ->  k_f = 1 / ((1-w)/k_P + w/k_N)  (OpenFOAM's harmonic
                          is 1/reverseLinear(1/gamma); reverseLinear weights
                          are 1 - cd weights, harmonic.H / reverseLinear.H,
                          ESI v2606, read from the installed source);
  * fixedValue faces: g_b = k_P / d_b, d_b the centre-to-face distance, because
    0/DT is zeroGradient on both faces so the patch gamma is the cell gamma;
  * q'' and the interface temperatures read back through the SAME formulas the
    frozen analyse_t9a.measure_wall uses -- mean of the two boundary fluxes,
    and the flux-continuous face temperature
    (k_L/d_L T_L + k_R/d_R T_R) / (k_L/d_L + k_R/d_R).

THE HONESTY CHECK THAT COMES FIRST.  Before predicting anything, the emulator
is run on the three FROZEN T9a wall levels and compared against the numbers
already published in T9a_RESULTS.md section 1 (from gate_t9a.json, on disk since
2026-08-20).  If it does not reproduce those to 1e-9 K it predicts nothing and
this file refuses.  Reproducing them is an IDENTITY, not evidence: both solve
the same discrete equations.  It is therefore reported and NEVER gated on
(Charter 2a).

Zero solver compute.  No OpenFOAM, no case, no mesh.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_t9a as EXACT           # noqa: E402  (frozen, imported, never edited)

T_HOT, T_COLD = 350.0, 300.0
FROZEN_LAYERS = ((0.05, 0.8), (0.10, 0.04), (0.02, 16.0))

LADDER = {"c": (10, 20, 5), "m": (16, 32, 8), "f": (26, 51, 13),
          "x": (42, 82, 21)}          # x = f * 1.6, T1c integer rounding

# published by the frozen comparator on 2026-08-20 (gate_t9a.json), quoted here
# so the emulator is checked against a file it does not read
FROZEN_PUBLISHED = {
    "c": dict(q=20.42558753033517, T_i1=348.775651609146, T_i2=300.0229993844026),
    "m": dict(q=20.06944025663026, T_i1=348.777747338424, T_i2=300.0235315248449),
    "f": dict(q=19.854990714112837, T_i1=348.7786732145509, T_i2=300.02387174218796),
}


def mesh1d(layers, cells):
    xf, xc, dx, kc = [0.0], [], [], []
    x0 = 0.0
    for (L, k), n in zip(layers, cells):
        h = L / n
        for i in range(n):
            xc.append(x0 + (i + 0.5) * h)
            dx.append(h)
            kc.append(k)
            xf.append(x0 + (i + 1) * h)
        x0 += L
    return xf, xc, dx, kc


def face_k(k_P, k_N, w, scheme):
    """w is OpenFOAM's cd (linear) weight for the OWNER cell."""
    if scheme == "linear":
        return w * k_P + (1.0 - w) * k_N
    if scheme == "harmonic":
        return 1.0 / ((1.0 - w) / k_P + w / k_N)
    raise ValueError(scheme)


def solve(layers, cells, scheme, T_hot=T_HOT, T_cold=T_COLD):
    xf, xc, dx, kc = mesh1d(layers, cells)
    n = len(xc)
    g = []
    for i in range(n - 1):
        d = xc[i + 1] - xc[i]
        xface = xf[i + 1]
        w = (xc[i + 1] - xface) / d          # OpenFOAM cd weight of the owner
        g.append(face_k(kc[i], kc[i + 1], w, scheme) / d)
    d_hot = xc[0] - xf[0]
    d_cold = xf[-1] - xc[-1]
    g_hot, g_cold = kc[0] / d_hot, kc[-1] / d_cold

    a = [0.0] * n
    b = [0.0] * n
    c = [0.0] * n
    d = [0.0] * n
    for i in range(n):
        gl = g_hot if i == 0 else g[i - 1]
        gr = g_cold if i == n - 1 else g[i]
        b[i] = -(gl + gr)
        if i > 0:
            a[i] = gl
        else:
            d[i] -= gl * T_hot
        if i < n - 1:
            c[i] = gr
        else:
            d[i] -= gr * T_cold
    T = EXACT.thomas(a, b, c, d)          # frozen tridiagonal solver, reused

    q_hot = kc[0] * (T_hot - T[0]) / d_hot
    q_cold = kc[-1] * (T[-1] - T_cold) / d_cold

    x1 = layers[0][0]
    x2 = layers[0][0] + layers[1][0]

    def iface_T(xi):
        iL = max(i for i in range(n) if xc[i] < xi)
        iR = iL + 1
        wL = kc[iL] / (xi - xc[iL])
        wR = kc[iR] / (xc[iR] - xi)
        return (wL * T[iL] + wR * T[iR]) / (wL + wR)

    return dict(q=0.5 * (q_hot + q_cold), q_hot=q_hot, q_cold=q_cold,
                T_i1=iface_T(x1), T_i2=iface_T(x2), n_cells=n)


def exact_for(layers):
    """Re-evaluate the closed form with the frozen exact_t9a, its WALL_LAYERS
    overridden IN MEMORY.  The file on disk is never touched; both of its
    independent routes (series resistance and a harmonic-face FV solve) are
    run and must agree, exactly as the rung registered."""
    saved = EXACT.WALL_LAYERS
    try:
        EXACT.WALL_LAYERS = tuple(layers)
        a = EXACT.wall_closed_form()
        b = EXACT.wall_numeric(n_per_layer=(400, 800, 160))
        for key in ("q", "T_i1", "T_i2"):
            if abs(a[key] - b[key]) / abs(a[key]) > 1e-9:
                raise SystemExit(f"REFUSE: exact routes disagree on {key}")
        return a
    finally:
        EXACT.WALL_LAYERS = saved


def ratios(vals):
    return [abs(vals[i]) / abs(vals[i + 1]) if vals[i + 1] else float("nan")
            for i in range(len(vals) - 1)]


def main():
    out = {}
    print("=" * 78)
    print("STEP 1 (identity, reported and NEVER gated): does the emulator "
          "reproduce the\n        frozen T9a wall levels already published?")
    print("=" * 78)
    ex0 = exact_for(FROZEN_LAYERS)
    worst = 0.0
    for lv in ("c", "m", "f"):
        s = solve(FROZEN_LAYERS, LADDER[lv], "linear")
        p = FROZEN_PUBLISHED[lv]
        dq, d1, d2 = (s["q"] - p["q"], s["T_i1"] - p["T_i1"],
                      s["T_i2"] - p["T_i2"])
        worst = max(worst, abs(d1), abs(d2))
        print(f"  {lv}: q  {s['q']:.9f} vs {p['q']:.9f}   d = {dq:+.3e}")
        print(f"     T_i1 {s['T_i1']:.9f} vs {p['T_i1']:.9f}   d = {d1:+.3e} K")
        print(f"     T_i2 {s['T_i2']:.9f} vs {p['T_i2']:.9f}   d = {d2:+.3e} K")
    if worst > 1e-9:
        print(f"REFUSE: emulator does not reproduce the frozen levels "
              f"(worst {worst:.3e} K > 1e-9). It predicts nothing.")
        return 2
    print(f"  IDENTITY HOLDS: worst temperature difference {worst:.2e} K. "
          f"Reported, not gated.")

    base_e1 = [solve(FROZEN_LAYERS, LADDER[lv], "linear")["T_i1"] - ex0["T_i1"]
               for lv in ("c", "m", "f")]
    out["baseline"] = dict(exact=ex0, e1_mK=[1e3 * e for e in base_e1],
                           e1_ratios=ratios(base_e1))
    print(f"\n  baseline R1 level errors (mK): "
          f"{', '.join(f'{1e3*e:+.4f}' for e in base_e1)}   "
          f"ratios {', '.join(f'{r:.3f}' for r in ratios(base_e1))}")

    print("\n" + "=" * 78)
    print("STEP 2  H-A  interface scheme: Gauss harmonic, frozen mesh, frozen k")
    print("=" * 78)
    a_e1, a_rows = [], {}
    for lv in ("c", "m", "f"):
        s = solve(FROZEN_LAYERS, LADDER[lv], "harmonic")
        e1 = s["T_i1"] - ex0["T_i1"]
        a_e1.append(e1)
        a_rows[lv] = dict(q=s["q"], T_i1=s["T_i1"], T_i2=s["T_i2"],
                          e_q_pct=100 * (s["q"] - ex0["q"]) / ex0["q"],
                          e1_mK=1e3 * e1,
                          e2_mK=1e3 * (s["T_i2"] - ex0["T_i2"]))
        print(f"  {lv}: q {s['q']:.6f} ({a_rows[lv]['e_q_pct']:+.4f} %)   "
              f"e(T_i1) {1e3*e1:+.5f} mK   e(T_i2) {a_rows[lv]['e2_mK']:+.5f} mK")
    drop = [abs(b) / abs(a) if a else float("inf") for b, a in zip(base_e1, a_e1)]
    print(f"  |e1| drop factor vs frozen scheme, per level: "
          f"{', '.join(f'{d:.3g}' for d in drop)}")
    print(f"  successive |e1| ratios under harmonic: "
          f"{', '.join(f'{r:.3f}' for r in ratios(a_e1))}")
    out["H_A"] = dict(levels=a_rows, e1_mK=[1e3 * e for e in a_e1],
                      drop_factor=drop, e1_ratios=ratios(a_e1))

    print("\n" + "=" * 78)
    print("STEP 3  H-B  a fourth level x, frozen scheme, frozen k")
    print("=" * 78)
    b_rows, b_e1 = {}, []
    for lv in ("m", "f", "x"):
        s = solve(FROZEN_LAYERS, LADDER[lv], "linear")
        e1 = s["T_i1"] - ex0["T_i1"]
        b_e1.append(e1)
        b_rows[lv] = dict(n_cells=s["n_cells"], q=s["q"], T_i1=s["T_i1"],
                          T_i2=s["T_i2"], e1_mK=1e3 * e1)
        print(f"  {lv} ({s['n_cells']:3d} cells): T_i1 {s['T_i1']:.9f}   "
              f"e {1e3*e1:+.5f} mK")
    import math
    d21, d32 = b_e1[1] - b_e1[2], b_e1[0] - b_e1[1]
    p = math.log(abs(d32 / d21)) / math.log(1.6) if d21 else float("nan")
    gci = 1.25 * abs(d21 / b_rows["x"]["T_i1"]) / (1.6 ** p - 1)
    band_mK = 1e3 * gci * abs(b_rows["x"]["T_i1"])
    print(f"  m/f/x triple: differences {1e3*d32:+.5f}, {1e3*d21:+.5f} mK  "
          f"-> p = {p:.3f}")
    print(f"  GCI band on x = {band_mK:.4f} mK   |error at x| = "
          f"{abs(1e3*b_e1[2]):.4f} mK   band covers error: "
          f"{band_mK >= abs(1e3*b_e1[2])}")
    out["H_B"] = dict(levels=b_rows, p=p, band_mK=band_mK,
                      e1_x_mK=1e3 * b_e1[2],
                      band_covers=bool(band_mK >= abs(1e3 * b_e1[2])),
                      e1_ratios=ratios(b_e1))

    print("\n" + "=" * 78)
    print("STEP 4  H-C  property jump 400x -> 40x (k2 0.04 -> 0.4), frozen "
          "scheme and mesh")
    print("=" * 78)
    LAY_C = ((0.05, 0.8), (0.10, 0.4), (0.02, 16.0))
    exC = exact_for(LAY_C)
    print(f"  exact at 40x: sum_R {exC['sum_R']:.9f}, q'' {exC['q']:.6f}, "
          f"T_i1 {exC['T_i1']:.6f}, T_i2 {exC['T_i2']:.6f}")
    c_rows, c_e1 = {}, []
    for lv in ("c", "m", "f"):
        s = solve(LAY_C, LADDER[lv], "linear")
        e1 = s["T_i1"] - exC["T_i1"]
        c_e1.append(e1)
        c_rows[lv] = dict(q=s["q"], T_i1=s["T_i1"], T_i2=s["T_i2"],
                          e_q_pct=100 * (s["q"] - exC["q"]) / exC["q"],
                          e1_mK=1e3 * e1,
                          e2_mK=1e3 * (s["T_i2"] - exC["T_i2"]))
        print(f"  {lv}: q {s['q']:.6f} ({c_rows[lv]['e_q_pct']:+.4f} %)   "
              f"e(T_i1) {1e3*e1:+.5f} mK   e(T_i2) {c_rows[lv]['e2_mK']:+.5f} mK")
    dropC = [abs(b) / abs(c) if c else float("inf")
             for b, c in zip(base_e1, c_e1)]
    print(f"  |e1| shrink factor 400x -> 40x, per level: "
          f"{', '.join(f'{d:.3g}' for d in dropC)}")
    print(f"  successive |e1| ratios at 40x: "
          f"{', '.join(f'{r:.3f}' for r in ratios(c_e1))}")
    out["H_C"] = dict(exact=exC, levels=c_rows, e1_mK=[1e3 * e for e in c_e1],
                      shrink_factor=dropC, e1_ratios=ratios(c_e1))

    with open(os.path.join(HERE, "T9aD_predictions.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("\nwritten: T9aD_predictions.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
