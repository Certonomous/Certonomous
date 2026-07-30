"""
F6d -- aggregate the random-matrix ensemble into a probabilistic band on the
periodic-hill quantities of interest, and put it side by side with

  * the LES reference (Frohlich et al. 2005 / the shipped U_LES field),
  * the kOmegaSST baseline,
  * the eigenspace-perturbation corner union computed on THE SAME case with
    THE SAME injection path (ens/corner_*).

Nothing is filtered.  Members that fail to converge, or whose Cf trace
fragments, are counted and reported as such -- a Monte Carlo band computed
after silently dropping its hardest members is not a band, and F6a's own
scoping note (F6a_epistemic_propagation.md Sec. 9.2) named exactly that risk
in advance.

Usage:  python3 aggregate.py > aggregate_result.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyse  # noqa: E402

ENS = HERE / "ens"
END = 4000

# Frohlich, J., Mellen, C.P., Rodi, W., Temmerman, L., Leschziner, M.A. (2005),
# J. Fluid Mech. 526, 19-66 -- as already cited and recorded by the F6b gate
# (f6b_periodic_hills/case_breuer_re10595/gate_result.json).
LES_REATTACH = (4.6, 4.7)
LES_SEPARATE = 0.2


def collect(pattern):
    rows = []
    for d in sorted(ENS.glob(pattern)):
        if not d.is_dir():
            continue
        r = analyse.analyse_case(d)
        log = d / "log.simpleFoam"
        if log.exists():
            r["residuals"] = analyse.residual_history(log)
        rows.append(r)
    return rows


RESIDUAL_GATE = 1e-3   # final Ux INITIAL residual


def usable(r):
    """A member is admitted if it ran to the full iteration budget and yielded a
    primary recirculation region.  Fragmentation of the wall-shear trace is
    RECORDED (n_reversed_regions), not used to exclude: the extra reversed
    patches are a real response to the perturbed stress field, and the primary
    bubble is well defined regardless.  Convergence is also recorded, not used
    to exclude -- the band is reported both over all admitted members and over
    the residual-gated subset, so the reader can see whether the gate moves it."""
    if r.get("time") != END:
        return False, f"no wallShearStress at iteration {END} (latest written: {r.get('time')})"
    if r.get("reattachment_x_over_h") is None:
        return False, "no reversed-flow region on the bottom wall at all"
    return True, None


def _stats(x, s, m):
    out = {}
    if x.size:
        out["reattachment"] = {
            "n": int(x.size),
            "min": float(x.min()), "max": float(x.max()),
            "mean": float(x.mean()), "std": float(x.std(ddof=1)) if x.size > 1 else 0.0,
            "p05": float(np.percentile(x, 5)), "p50": float(np.percentile(x, 50)),
            "p95": float(np.percentile(x, 95)),
            "credible_90_width": float(np.percentile(x, 95) - np.percentile(x, 5)),
            "support_width": float(x.max() - x.min()),
            "covers_LES_range": bool(x.min() <= LES_REATTACH[1] and x.max() >= LES_REATTACH[0]),
            "frac_at_or_below_LES_upper": float((x <= LES_REATTACH[1]).mean()),
        }
    if s.size:
        out["separation"] = {"min": float(s.min()), "max": float(s.max()),
                             "mean": float(s.mean())}
    if m.size:
        out["profile_mae_pct"] = {"n": int(m.size), "min": float(m.min()),
                                  "max": float(m.max()), "mean": float(m.mean()),
                                  "p05": float(np.percentile(m, 5)),
                                  "p95": float(np.percentile(m, 95))}
    return out


def _arrays(rows):
    x = np.array([r["reattachment_x_over_h"] for r in rows]) if rows else np.array([])
    s = np.array([r["separation_x_over_h"] for r in rows]) if rows else np.array([])
    m = np.array([r["profile_mae_vs_LES_overall_percent"] for r in rows
                  if r.get("profile_mae_vs_LES_overall_percent") is not None])
    return x, s, m


def summarize(rows, label):
    good, bad = [], []
    for r in rows:
        ok, why = usable(r)
        if ok:
            good.append(r)
        else:
            bad.append({"case": r["case"], "reason": why,
                        "n_cf_crossings": r.get("n_cf_crossings")})

    def ux(r):
        return r.get("residuals", {}).get("final_initial_residuals", {}).get("Ux")

    gated = [r for r in good if (ux(r) is not None and ux(r) <= RESIDUAL_GATE)]
    res_all = np.array([ux(r) for r in good if ux(r) is not None])
    nreg = np.array([r.get("n_reversed_regions", 0) for r in good])

    out = {
        "label": label,
        "n_built": len(rows),
        "n_admitted": len(good),
        "n_failed_to_produce_a_bubble": len(bad),
        "failed": bad,
        "residual_gate_Ux": RESIDUAL_GATE,
        "n_meeting_residual_gate": len(gated),
        "final_Ux_residual": ({"min": float(res_all.min()), "median": float(np.median(res_all)),
                               "max": float(res_all.max())} if res_all.size else None),
        "n_reversed_regions": ({"min": int(nreg.min()), "median": float(np.median(nreg)),
                                "max": int(nreg.max()),
                                "frac_single_region": float((nreg == 1).mean())}
                               if nreg.size else None),
        "all_admitted": _stats(*_arrays(good)),
        "residual_gated_subset": _stats(*_arrays(gated)),
        "members": [{"case": r["case"],
                     "separation": r["separation_x_over_h"],
                     "reattachment": r["reattachment_x_over_h"],
                     "reattachment_lastcross": r.get("reattachment_lastcross"),
                     "n_reversed_regions": r.get("n_reversed_regions"),
                     "profile_mae_pct": r.get("profile_mae_vs_LES_overall_percent"),
                     "time": r["time"],
                     "final_Ux_residual": ux(r)}
                    for r in good],
    }
    return out


def profile_coverage(cases, times, label):
    """Does the ensemble envelope actually CONTAIN the LES velocity profile?

    This is the coverage test that matters for a band: at every sampled point
    of every one of the 9 standard stations, check whether U_LES,x lies inside
    the ensemble's [min, max] of U_x.  Reported as the fraction covered, plus
    the mean envelope half-width in the same units, so that "covers the truth"
    and "is informative" can be judged together instead of one at a time.
    """
    f = analyse.les_interp()
    tot = cov = 0
    widths = []
    per_station = {}
    for st in range(9):
        cols = []
        ref = None
        for c, t in zip(cases, times):
            p = analyse.station_profiles(c, t)
            if st not in p:
                continue
            xs, ys, U = p[st]
            cols.append(U[:, 0])
            ref = (xs, ys)
        if not cols or ref is None:
            continue
        A = np.array(cols)
        lo, hi = A.min(axis=0), A.max(axis=0)
        UL = f(np.column_stack(ref))[:, 0]
        inside = (UL >= lo) & (UL <= hi)
        per_station[f"x{st}"] = {"n_points": int(inside.size),
                                 "frac_covered": float(inside.mean()),
                                 "mean_envelope_width": float((hi - lo).mean())}
        tot += inside.size
        cov += int(inside.sum())
        widths.append((hi - lo).mean())
    return {"label": label, "n_members": len(cases),
            "frac_LES_points_inside_envelope": (cov / tot if tot else None),
            "mean_envelope_width_Ux": float(np.mean(widths)) if widths else None,
            "per_station": per_station}


def main():
    result = {
        "case": "F6b PH_Breuer, Re_H = 10595, 15600 cells",
        "baseline": {},
        "les_reference": {"separation_x_over_h": LES_SEPARATE,
                          "reattachment_x_over_h_range": list(LES_REATTACH),
                          "citation": "Frohlich et al. 2005, JFM 526:19-66"},
    }

    # the unperturbed kOmegaSST baseline, read from the F6b case itself
    base = analyse.analyse_case(analyse.CASE, 10000)
    result["baseline"] = {
        "source": str(analyse.CASE / "10000" / "wallShearStress"),
        "separation_x_over_h": base.get("separation_x_over_h"),
        "reattachment_x_over_h": base.get("reattachment_x_over_h"),
        "n_cf_crossings": base.get("n_cf_crossings"),
        "profile_mae_vs_LES_overall_percent": base.get("profile_mae_vs_LES_overall_percent"),
    }

    nullr = collect("null")
    if nullr:
        result["null_test"] = summarize(nullr, "null (R_sample = R_bar)")

    corners = collect("corner_*")
    if corners:
        result["eigenspace_corners"] = summarize(corners, "eigenspace corner union")
        xs = [r["reattachment_x_over_h"] for r in corners
              if r.get("reattachment_x_over_h") is not None]
        if xs:
            result["eigenspace_corners"]["corner_union_envelope"] = [min(xs), max(xs)]
            result["eigenspace_corners"]["per_corner"] = {
                r["case"]: {"separation": r.get("separation_x_over_h"),
                            "reattachment": r.get("reattachment_x_over_h"),
                            "reattachment_lastcross": r.get("reattachment_lastcross"),
                            "n_cf_crossings": r.get("n_cf_crossings"),
                            "n_reversed_regions": r.get("n_reversed_regions"),
                            "profile_mae_pct": r.get("profile_mae_vs_LES_overall_percent"),
                            "time": r["time"],
                     "final_Ux_residual": r.get("residuals", {})
                                                  .get("final_initial_residuals", {}).get("Ux")}
                for r in corners}

    sd = HERE / "signdemo"
    if sd.is_dir():
        result["live_model_runs"] = {}
        for d in sorted(sd.iterdir()):
            if not d.is_dir():
                continue
            r = analyse.analyse_case(d)
            if r.get("time") is None:
                result["live_model_runs"][d.name] = {"status": "no output"}
                continue
            r["residuals"] = analyse.residual_history(d / "log.simpleFoam")
            result["live_model_runs"][d.name] = {
                "separation": r.get("separation_x_over_h"),
                "reattachment": r.get("reattachment_x_over_h"),
                "reattachment_lastcross": r.get("reattachment_lastcross"),
                "n_reversed_regions": r.get("n_reversed_regions"),
                "n_cf_crossings": r.get("n_cf_crossings"),
                "final_Ux_residual": r["residuals"]["final_initial_residuals"].get("Ux"),
                "iterations": r["residuals"]["final_iteration"],
            }

    for pref, lab in (("d0.2_s*", "random matrix, delta=0.2 (paper Case 1)"),
                      ("d0.6_s*", "random matrix, delta=0.6 (paper Case 2)")):
        rows = collect(pref)
        if rows:
            key = pref.split("_")[0]
            s = summarize(rows, lab)
            cases = [ENS / m["case"] for m in s["members"]]
            times = [m["time"] for m in s["members"]]
            if cases:
                s["profile_coverage"] = profile_coverage(cases, times, lab)
            result.setdefault("random_matrix", {})[key] = s

    # the same coverage test for the corner union, run in the corner method's
    # own live-turbulence-model form (signdemo/live_*)
    live = [HERE / "signdemo" / n for n in ("live_oneC", "live_twoC", "live_threeC")]
    live = [d for d in live if (d / "4000").is_dir()]
    if live:
        result["live_corner_union_profile_coverage"] = profile_coverage(
            live, [4000] * len(live), "eigenspace corner union (live model)")

    print(json.dumps(result, indent=2))
    (HERE / "aggregate_result.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
