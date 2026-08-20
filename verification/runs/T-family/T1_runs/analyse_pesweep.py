#!/usr/bin/env python3
"""
The amended Peclet diagnostic: does the T1c excess scale as 1/Pe^2 ?

REGISTERED IN `DIAGNOSTIC_PREDICTION.md` BEFORE ANY SWEEP CASE WAS BUILT.
The prediction being tested, verbatim from that file:

  "If axial conduction is the cause, a log-log fit of excess against Pe over
   the five points has slope -2, and the Re = 25 point lands near +1.2 %."

and its falsifying outcomes, also registered in advance:

  slope ~ 0                  -> axial conduction refuted, cause unidentified
  slope far from -2          -> some other Peclet-dependent mechanism; the
                                fitted slope is then the finding
  Re = 400 failing 30 D/40 D -> that point is DISCARDED, not explained

Nothing here may move a T1c verdict.  These cases carry no band and cannot pass
or fail.  Explaining a failure is not excusing it.

TWO THINGS THIS CARRIES FORWARD BECAUSE THEY WERE PAID FOR:

  * a zero is not believed until a planted perturbation is recovered from it.
    The convergence check plants 1.234e-03 K into the earlier checkpoint and
    confirms the reader returns exactly that, so a zero from a broken parser
    cannot be mistaken for a converged solution (L-139).
  * the excess is measured against the SAME station and the SAME estimator as
    the baseline it is compared to.  The first version of this diagnostic
    compared a single-mesh excess against a Richardson-extrapolated one and was
    void for it.
"""
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t1c as T1C                                # noqa: E402

NU_EXACT = 48.0 / 11.0
BASELINE = "L_q_f"
STATION = 40.0
DEV_CHECK_STATION = 30.0
SWEEP = [("D_Re25", 25.0), ("D_Re50", 50.0), (BASELINE, 100.0),
         ("D_Re200", 200.0), ("D_Re400", 400.0)]
PLANT = 1.234e-03


def planted_zero_control(case):
    """Re-run the convergence reader with a known perturbation planted in the
    EARLIER checkpoint.  A reader that returns 0.0 for a case that differs by
    exactly PLANT is broken, and its zeros mean nothing.

    THE ASSERTION IS max(real, PLANT), NOT PLANT.  The first version of this
    demanded the reader return PLANT exactly and declared it BROKEN on D_Re25,
    which really moves 2.761e-01 K between its last two checkpoints -- a
    perturbation of 1.234e-03 K planted into one cell cannot raise a maximum
    that is already 224 times larger.  The reader was fine; the control was
    asking the wrong question.  What the control actually establishes is that a
    1.234e-03 K difference is VISIBLE to the reader, so a zero it returns is a
    statement about the fields and not about itself.
    """
    d = os.path.join(HERE, case)
    ts = sorted((x for x in os.listdir(d)
                 if x.replace(".", "").isdigit() and float(x) > 0),
                key=float)
    tmp = tempfile.mkdtemp(prefix="plant_")
    try:
        work = os.path.join(tmp, case)
        os.makedirs(work)
        for sub in ("constant", "system"):
            shutil.copytree(os.path.join(d, sub), os.path.join(work, sub))
        for t in ts[-2:]:
            shutil.copytree(os.path.join(d, t), os.path.join(work, t))
        p = os.path.join(work, ts[-2], "T")
        txt = open(p).read().split("\n")
        # PLANT BY INDEX, THEN READ IT BACK.  The first version of this looked
        # for a numeric line whose PREDECESSOR was all digits -- but an
        # OpenFOAM internal field is "<count>", then "(", then the values, so
        # the predecessor of the first value is "(" and nothing was ever
        # planted.  The control then reported a perfectly good reader as
        # BROKEN on D_Re50, because both the real and the planted difference
        # were zero for the same reason: no perturbation existed.
        start = None
        for i in range(len(txt) - 2):
            if txt[i].strip().isdigit() and txt[i + 1].strip() == "(":
                start = i + 2
                break
        if start is None:
            raise RuntimeError(f"cannot locate the internal field in {p}")
        before = float(txt[start].strip())
        txt[start] = repr(before + PLANT)
        open(p, "w").write("\n".join(txt))
        # read the file back: the plant must be ON DISK, not merely intended
        back = float(open(p).read().split("\n")[start].strip())
        if abs((back - before) - PLANT) > 1e-12:
            raise RuntimeError(f"the plant did not land: {before} -> {back}")
        return T1C.iterative_convergence(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def excess(case, station=STATION):
    m = T1C.measure(os.path.join(HERE, case), station)
    m["excess_pct"] = 100.0 * (m["Nu"] - NU_EXACT) / NU_EXACT
    return m


def fit_loglog(pe, ex):
    n = len(pe)
    X = [math.log(p) for p in pe]
    Y = [math.log(e) for e in ex]
    mx, my = sum(X) / n, sum(Y) / n
    sxx = sum((x - mx) ** 2 for x in X)
    sxy = sum((x - mx) * (y - my) for x, y in zip(X, Y))
    slope = sxy / sxx
    inter = my - slope * mx
    ss_res = sum((y - (inter + slope * x)) ** 2 for x, y in zip(X, Y))
    ss_tot = sum((y - my) ** 2 for y in Y)
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    se = math.sqrt(ss_res / (n - 2) / sxx) if n > 2 else float("nan")
    return slope, inter, r2, se


def main():
    out = {"registered_in": "DIAGNOSTIC_PREDICTION.md, amended design",
           "exact": NU_EXACT, "points": [], "discarded": []}

    unconverged = []
    print("CONVERGENCE, each zero controlled by a planted 1.234e-03 K "
          "perturbation")
    for case, _ in SWEEP:
        c = T1C.iterative_convergence(os.path.join(HERE, case))
        ctl = planted_zero_control(case)
        rec = c["max_change"]
        got = ctl["max_change"]
        want = max(rec, PLANT)
        ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)
        print(f"  {case:8s} max change {rec:.3e}  [{c['state']}]   "
              f"planted control returns {got:.6e} "
              f"(expected max(real, plant) = {want:.6e}: "
              f"{'RECOVERED' if ok else 'BROKEN READER'})")
        if not ok:
            print("REFUSE: the convergence reader failed its planted control")
            return 2
        if c["state"] != "CONVERGED":
            unconverged.append((case, rec))

    if unconverged:
        print("\n  NOT ITERATIVELY CONVERGED: " +
              ", ".join(f"{c} ({v:.3e} K)" for c, v in unconverged))
        out["unconverged"] = [dict(case=c, max_change=v)
                              for c, v in unconverged]

    print(f"\nEXCESS OVER THE EXACT 48/11 = {NU_EXACT:.7f}, "
          f"station {STATION:.0f} D, constant-flux arm")
    print(f"{'case':9s} {'Re':>6s} {'Pe':>8s} {'Nu':>12s} {'excess %':>10s} "
          f"{'f.Re':>9s}")
    pts = []
    for case, Re in SWEEP:
        m = excess(case)
        Pe = m["Re"] * float(T1C.case_txt(os.path.join(HERE, case), "Pr"))
        flag = ""
        if case == "D_Re400":
            m30 = excess(case, DEV_CHECK_STATION)
            d = abs(m30["excess_pct"] - m["excess_pct"])
            flag = (f"   30D/40D differ by {d:.4f} pp "
                    f"(excess {abs(m['excess_pct']):.4f} pp)")
            if d > abs(m["excess_pct"]):
                out["discarded"].append(
                    dict(case=case, reason="30 D and 40 D disagree by more "
                                           "than the excess being measured",
                         excess_30D=m30["excess_pct"],
                         excess_40D=m["excess_pct"]))
                print(f"{case:9s} {Re:6.0f} {Pe:8.2f} {m['Nu']:12.6f} "
                      f"{m['excess_pct']:10.4f} {m['fRe']:9.4f}"
                      f"   DISCARDED --{flag}")
                continue
        print(f"{case:9s} {Re:6.0f} {Pe:8.2f} {m['Nu']:12.6f} "
              f"{m['excess_pct']:10.4f} {m['fRe']:9.4f}{flag}")
        pts.append((Pe, m["excess_pct"], case))
        out["points"].append(dict(case=case, Re=Re, Pe=Pe, Nu=m["Nu"],
                                  excess_pct=m["excess_pct"], fRe=m["fRe"],
                                  station_xD=m["sample_xD"]))

    pos = [(p, e, c) for p, e, c in pts if e > 0]
    print(f"\n{len(pos)} of {len(pts)} points have a POSITIVE excess "
          f"(a log-log fit needs one)")
    if len(pos) < 3:
        print("REFUSE: fewer than three positive points; a slope on this is "
              "not a measurement")
        out["verdict"] = "NOT A RESULT (too few positive points to fit)"
        json.dump(out, open(os.path.join(HERE, "pesweep.json"), "w"),
                  indent=1, default=str)
        return 1

    slope, inter, r2, se = fit_loglog([p for p, _, _ in pos],
                                      [e for _, e, _ in pos])
    print(f"\nlog-log fit of excess against Pe over {len(pos)} points:")
    print(f"  slope    = {slope:+.4f}  +/- {se:.4f} (standard error)")
    print(f"  R^2      = {r2:.5f}")
    print(f"  predicted slope for axial conduction, O(1/Pe^2) = -2")
    z = (slope + 2.0) / se if se and not math.isnan(se) else float("nan")
    print(f"  the fit is {abs(z):.1f} standard errors from -2")
    out.update(slope=slope, slope_se=se, r2=r2, sigma_from_minus2=z)

    p25 = [e for p, e, c in pos if c == "D_Re25"]
    if p25:
        print(f"\n  the Re = 25 point, predicted at +1.20 %: "
              f"measured {p25[0]:+.4f} %")
        out["Re25_measured_pct"] = p25[0]
        out["Re25_predicted_pct"] = 1.197
    json.dump(out, open(os.path.join(HERE, "pesweep.json"), "w"),
              indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
