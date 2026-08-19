#!/usr/bin/env python3
"""
The near-wall thermal diagnostic K0cR_RESULTS.md section 4 named as owed.

K0cR measured a contradiction: on the square cavity SSG's peak nu_t/nu FELL
18-21 percent while its wall heat flux ROSE 11-14 points.  A bulk
eddy-viscosity explanation predicts those move together, so the mechanism must
be in the near-wall DISTRIBUTION of alpha_t rather than in its domain maximum.
This resolves the profile and asks the question directly.

ZERO COMPUTE.  Every field read here was written by a solve that has already
been recorded and paid for.

ZERO WRITES.  The square cases already carry Cx/Cy on disk, so no postProcess
call is made and no case directory -- least of all a recorded baseline in
K0cS_runs -- is modified.  That is also why this diagnostic is SQUARE-CAVITY
ONLY: the tall cases do not carry cell centres, generating them would write into
K0cX_runs, and the contradiction this exists to explain is on the square cavity
anyway.

GRADES NOTHING.  No band, no verdict, no row.  It is a mechanism probe.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LADDER = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LADDER, "K0cS_runs"))
import analyse_k0cs as SQ          # noqa: E402

PAIRS = [
    ("R_sq_c", os.path.join(HERE, "R_sq_c"),
     "S_KE_c", os.path.join(LADDER, "K0cS_runs", "S_KE_c")),
    ("R_sq_f", os.path.join(HERE, "R_sq_f"),
     "S_KE_f", os.path.join(LADDER, "K0cS_runs", "S_KE_f")),
]
NCELL = 8       # cells out from the hot wall


def latest(case):
    ts = [(float(d), d) for d in os.listdir(case)
          if os.path.isdir(os.path.join(case, d)) and d.replace(".", "").isdigit()]
    return sorted(ts)[-1][1]


def profile(case_dir, label):
    t = latest(case_dir)
    need = ("Cx", "Cy", "T", "alphat", "nut")
    for f in need:
        p = os.path.join(case_dir, t, f)
        if not os.path.isfile(p):
            print(f"  REFUSE: {label} has no {f} at time {t}; this diagnostic "
                  f"does not generate one, by design")
            return None
    cx = SQ.read_internal(os.path.join(case_dir, t, "Cx"))
    cy = SQ.read_internal(os.path.join(case_dir, t, "Cy"))
    T = SQ.read_internal(os.path.join(case_dir, t, "T"))
    at = SQ.read_internal(os.path.join(case_dir, t, "alphat"))
    nt = SQ.read_internal(os.path.join(case_dir, t, "nut"))

    L = float(SQ.case_txt(case_dir, "L").split()[0])
    nu = float(SQ.case_txt(case_dir, "nu").split()[0])
    Pr = float(SQ.case_txt(case_dir, "Pr"))
    alpha = nu / Pr

    xs = sorted(set(round(v, 12) for v in cx))
    ys = sorted(set(round(v, 12) for v in cy))
    idx = {(round(x, 12), round(y, 12)): i for i, (x, y) in enumerate(zip(cx, cy))}
    ymid = min(ys, key=lambda v: abs(v - 0.5 * L))

    rows = []
    for j in range(min(NCELL, len(xs))):
        i = idx[(xs[j], ymid)]
        a_t, n_t = at[i], nt[i]
        rows.append(dict(cell=j, x=xs[j], x_over_L=xs[j] / L,
                         alphat_over_alpha=a_t / alpha,
                         nut_over_nu=n_t / nu,
                         Prt_eff=(n_t / a_t) if a_t > 0 else None,
                         T=T[i]))
    return dict(time=t, alpha=alpha, nu=nu, rows=rows)


def main():
    print("NEAR-WALL THERMAL DIAGNOSTIC -- square cavity, hot wall, mid-height")
    print("Answers K0cR_RESULTS.md section 4.  Grades nothing.")
    print("=" * 96)
    for arm_name, arm_dir, base_name, base_dir in PAIRS:
        a = profile(arm_dir, arm_name)
        b = profile(base_dir, base_name)
        if not a or not b:
            continue
        print(f"\n### {arm_name} (SSG)  vs  {base_name} (kEpsilon)")
        print(f"    alpha = {a['alpha']:.6g} m2/s   times {a['time']} / {b['time']}")
        print("    %-4s %-11s | %12s %12s | %12s %12s | %9s %9s" %
              ("cell", "x/L", "at/a SSG", "at/a kEps", "nt/n SSG", "nt/n kEps",
               "Prt SSG", "Prt kEps"))
        for ra, rb in zip(a["rows"], b["rows"]):
            pa = f"{ra['Prt_eff']:.4f}" if ra["Prt_eff"] else "-"
            pb = f"{rb['Prt_eff']:.4f}" if rb["Prt_eff"] else "-"
            print("    %-4d %-11.3e | %12.5g %12.5g | %12.5g %12.5g | %9s %9s" %
                  (ra["cell"], ra["x_over_L"],
                   ra["alphat_over_alpha"], rb["alphat_over_alpha"],
                   ra["nut_over_nu"], rb["nut_over_nu"], pa, pb))
        # the number that sets the wall heat flux
        wa, wb = a["rows"][0], b["rows"][0]
        if wb["alphat_over_alpha"] > 0:
            d = 100.0 * (wa["alphat_over_alpha"] - wb["alphat_over_alpha"]) \
                / wb["alphat_over_alpha"]
            print(f"    FIRST CELL alpha_t/alpha: {wb['alphat_over_alpha']:.5g}"
                  f" -> {wa['alphat_over_alpha']:.5g}   ({d:+.2f} %)")
        else:
            print(f"    FIRST CELL alpha_t/alpha: {wb['alphat_over_alpha']:.5g}"
                  f" -> {wa['alphat_over_alpha']:.5g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
