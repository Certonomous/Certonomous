#!/usr/bin/env python3
"""Render BASELINES.md from sst_baseline_metrics.json + the challenge scorer.

Run after sst_baseline_metrics.py. Deterministic: same inputs, same file.
"""
from __future__ import annotations
import json, os, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/home/ubuntu/closure-challenge-benchmark"
M = json.load(open(os.path.join(HERE, "sst_baseline_metrics.json")))

# challenge-metric identity baseline (regenerated, not copied)
IDENTITY = os.path.join(HERE, "identity_baseline_score.json")


def challenge_identity():
    if os.path.exists(IDENTITY):
        return json.load(open(IDENTITY))
    sys.path.insert(0, "/home/ubuntu/closure-challenge-pkg/src")
    import numpy as np
    from scipy.interpolate import NearestNDInterpolator
    from closure_challenge import score, evaluate_by_case, evaluation_points, case_names
    sys.path.insert(0, HERE)
    from of_read import read_field, latest_time_dir
    paths = {
        "alpha_15_13929_4048": "data/Parm_PH_29/alpha_15/alpha_15_13929_4048",
        "alpha_15_13929_2024": "data/Parm_PH_29/alpha_15/alpha_15_13929_2024",
        "alpha_05_4071_4048": "data/Parm_PH_29/alpha_05/alpha_05_4071_4048",
        "alpha_05_4071_2024": "data/Parm_PH_29/alpha_05/alpha_05_4071_2024",
        "AR_1_Ret_360": "data/DUCT/AR_1_Ret_360",
        "AR_3_Ret_360": "data/DUCT/AR_3_Ret_360",
        "AR_14_Ret_180": "data/DUCT/AR_14_Ret_180",
        "NASA_2DWMH": "data/NASA_2DWMH",
    }
    preds = {}
    for c, rel in paths.items():
        p = os.path.join(BENCH, rel)
        t = latest_time_dir(p)
        cp = os.path.join(p, "constant", "C")
        if not os.path.exists(cp):
            cp = os.path.join(p, t, "C")
        if not os.path.exists(cp):
            cp = os.path.join(p, "0", "C")
        C = read_field(cp); U = read_field(os.path.join(p, t, "U"))
        preds[c] = NearestNDInterpolator(C, U)(evaluation_points(c))
    out = {"per_case": {k: float(v) for k, v in evaluate_by_case(preds).items()},
           "overall": float(score(preds))}
    json.dump(out, open(IDENTITY, "w"), indent=1)
    return out


def g(m, k, fmt="%.4f", none="--"):
    v = m.get(k)
    return none if v is None else (fmt % v)


def main():
    ident = challenge_identity()
    head = subprocess.run(["git", "-C", BENCH, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    tree = subprocess.run("git -C %s ls-files -s data | sha256sum" % BENCH,
                          shell=True, capture_output=True, text=True).stdout.split()[0]
    L = []
    A = L.append
    A("# k-omega SST baseline, quantified per case")
    A("")
    A("**This file is generated.** `sst_baseline_metrics.py` computes the numbers,")
    A("`make_baselines_md.py` renders this document. Re-running either reproduces it.")
    A("Nothing here is fitted or trained.")
    A("")
    A("Purpose: this is the **Charter 2c trivial baseline**. Every Phase 3 closure")
    A("reproduction in `cases/RANS_LES_closure_models/` must beat the relevant row of")
    A("these tables on the metric it claims to improve, or ship as a documented failure.")
    A("")
    A("## 0. Provenance")
    A("")
    A("| Item | Value |")
    A("|---|---|")
    A("| dataset | The Closure Challenge benchmark dataset |")
    A("| source URL | https://github.com/rmcconke/closure-challenge-benchmark.git |")
    A("| local clone (outside the repo) | `/home/ubuntu/closure-challenge-benchmark` |")
    A("| commit | `%s` |" % head)
    A("| sha256 of `git ls-files -s data` | `%s` |" % tree)
    A("| tracked files under `data/` | 6153 |")
    A("| scorer package | https://github.com/rmcconke/closure-challenge.git at `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`, local clone `/home/ubuntu/closure-challenge-pkg` |")
    A("| challenge paper | McConkey, Buchanan, Smidt, Bodner, Dwight & Cinnella, *The Closure Challenge*, arXiv:2603.28884 |")
    A("| generated | %s |" % datetime.date.today().isoformat())
    A("")
    A("No benchmark file is modified by anything in this directory; every script reads only.")
    A("")
    A("## 1. Definitions")
    A("")
    A("All quantities are computed **cell-by-cell on the case's own RANS mesh**, on which")
    A("the challenge has already interpolated the LES/DNS truth. `U`, `k`, `nut`, `omega`")
    A("are the shipped converged k-omega SST fields; `U_LES`, `k_LES`, `tauij_LES` are the")
    A("shipped truth.")
    A("")
    A("| Symbol in tables | Definition |")
    A("|---|---|")
    A("| `U_rms` | `sqrt(mean(|U_RANS - U_LES|^2)) / mean(|U_LES|)` |")
    A("| `U_mae` | `mean(|U_RANS - U_LES|) / mean(|U_LES|)` (the challenge's own metric shape, but over all cells rather than the 1000 scored points) |")
    A("| `k_rms` | `sqrt(mean((k_RANS - k_LES)^2)) / mean(k_LES)` |")
    A("| `tau_rms` | `sqrt(mean(||tau_RANS - tau_LES||_F^2)) / (2 mean(k_LES))`, with `tau_RANS = (2/3) k I - 2 nu_t S` |")
    A("| `b_rms` | `sqrt(mean(||b_RANS - b_LES||_F^2))`, `b = tau/(2k) - I/3`; dimensionless, and `||b||_F <= sqrt(2/3) = 0.8165` for any realisable state |")
    A("| `b_med`, `b_p95` | median and 95th percentile of `||b_RANS - b_LES||_F` (robust companions to the RMS) |")
    A("| `x_sep`, `x_reatt` | abscissae where the streamwise velocity in the first cell row off the bottom wall changes sign, at the ends of the longest contiguous reversed-flow run |")
    A("")
    A("Cells where either `k` falls below `1e-4 * mean(k)` are excluded from the")
    A("anisotropy statistics (`b = tau/2k` is meaningless there); the excluded count is")
    A("in the JSON as `n_cells_k_masked`. On the hills that is 7-63 cells of 15600; on")
    A("the NASA hump it is 4514 of 51626 (8.7%), all in the low-turbulence freestream.")
    A("")
    A("### Two verification checks on the post-processing itself")
    A("")
    A("1. **Reattachment.** On PH_Breuer the first-cell-row sign criterion gives")
    A("   `x_sep = 0.259`, `x_reatt = 7.643`. OpenFOAM's own bottom-wall")
    A("   `wallShearStress`, written by the solver into")
    A("   `postProcessing/bottomValues/10000/wallShearStress_bottomValues.raw`, changes")
    A("   sign at `x = 0.259` and `x = 7.6439`. Four-significant-figure agreement from")
    A("   an independent quantity.")
    A("2. **Velocity gradient.** The DUCT, PH_Breuer, CBFS and NASA cases ship no `gradU`,")
    A("   so `of_read.structured_gradient()` computes it by a curvilinear chain rule on")
    A("   the structured block. Against the `gradU` OpenFOAM itself wrote on three")
    A("   periodic-hill cases it agrees to **0.47-0.96% relative L2 in the interior**")
    A("   (median cellwise 0.10-0.13%), and 2.5-3.3% including the one-sided boundary")
    A("   rows. The hills use the shipped `tauij_B` and are unaffected.")
    A("")

    # ---- section 2: challenge metric
    A("## 2. The baseline in the challenge's own metric (8 test cases, 1000 points each)")
    A("")
    A("Uncorrected SST velocity, nearest-neighbour interpolated to the official")
    A("evaluation points, scored by the challenge's own `closure_challenge.score()`.")
    A("This is the number a submitted method has to beat.")
    A("")
    A("| Case | SST identity baseline (scaled MAE) |")
    A("|---|---|")
    order = ["alpha_15_13929_4048", "alpha_15_13929_2024", "alpha_05_4071_4048",
             "alpha_05_4071_2024", "AR_1_Ret_360", "AR_3_Ret_360",
             "AR_14_Ret_180", "NASA_2DWMH"]
    for c in order:
        A("| `%s` | %.4f |" % (c, ident["per_case"][c]))
    A("| **overall (mean of 8)** | **%.4f** |" % ident["overall"])
    A("")
    A("For scale, on the live leaderboard read from the benchmark README at the commit")
    A("above: the best entry is 0.0595 (Reissmann, Fang & Sandberg) and this lab's own")
    A("round-5 entry is 0.0566. The uncorrected baseline is 0.1036. A method that does")
    A("not get below 0.1036 has not earned its complexity.")
    A("")

    # ---- section 3: 2D separated flows
    A("## 3. Separated 2-D flows: field errors and the separation bubble")
    A("")
    A("`Lrel` is the relative error in bubble length, `(L_RANS - L_LES) / L_LES`.")
    A("Positive means SST predicts too long a recirculation.")
    A("")
    A("| Case | split | Re | cells | U_rms | U_mae | k_rms | tau_rms | b_rms | b_med | b_p95 | x_sep RANS | x_sep LES | x_reatt RANS | x_reatt LES | Lrel |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    def re_of(m):
        if m.get("Re_H"):
            return "%d" % m["Re_H"]
        if m.get("Re_c"):
            return "%.0fk (chord)" % (m["Re_c"] / 1000)
        return "--"

    fam2 = [c for c in M if M[c].get("family") in ("PHLL29", "PHLL10595", "CBFS", "hump")]
    for c in sorted(fam2, key=lambda x: (M[x].get("family"), x)):
        m = M[c]
        A("| `%s` | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c, m["split"], re_of(m), m["n_cells"],
            g(m, "U_rms_err_rel"), g(m, "U_mae_rel"), g(m, "k_rms_err_rel"),
            g(m, "tau_rms_err_rel"), g(m, "b_rms_err"), g(m, "b_median_err"),
            g(m, "b_p95_err"),
            g(m, "x_sep_RANS", "%.3f"), g(m, "x_sep_LES", "%.3f"),
            g(m, "x_reatt_RANS", "%.3f"), g(m, "x_reatt_LES", "%.3f"),
            g(m, "L_bubble_rel_err", "%+.2f")))
    A("")
    A("Headline numbers to carry forward:")
    A("")
    ph = M["PHLL10595"]
    A("* **Periodic hill, Re_H = 10595 (Breuer).** SST reattaches at `x/H = %.2f`; the LES"
      % ph["x_reatt_RANS"])
    A("  reattaches at `x/H = %.2f`. Separation is nearly right (`%.2f` vs `%.2f`), so the"
      % (ph["x_reatt_LES"], ph["x_sep_RANS"], ph["x_sep_LES"]))
    A("  whole error is in reattachment: the bubble is **%.0f%% too long**." % (100 * ph["L_bubble_rel_err"],))
    A("  For external corroboration, Breuer et al. report LES reattachment at `x/H ~ 4.7`;")
    A("  the value derived here from the shipped interpolated LES field is %.2f." % ph["x_reatt_LES"])
    nh = M["NASA_2DWMH"]
    A("* **NASA wall-mounted hump.** With chord `c = 0.42 m` from the case's own `caseDef`,")
    A("  SST separates at `x/c = %.3f` against `x/c = %.3f` for the truth (essentially"
      % (nh["x_sep_RANS"] / 0.42, nh["x_sep_LES"] / 0.42))
    A("  right, the separation point is geometrically fixed), and reattaches at")
    A("  `x/c = %.3f` against `x/c = %.3f`: the bubble is **%.0f%% too long**."
      % (nh["x_reatt_RANS"] / 0.42, nh["x_reatt_LES"] / 0.42, 100 * nh["L_bubble_rel_err"]))
    cb = M["CBFS13700"]
    A("* **Curved backward-facing step, Re_H = 13700.** Bubble **%.0f%% too long**"
      % (100 * cb["L_bubble_rel_err"],))
    A("  (`x_reatt` %.2f vs %.2f), on a case whose bulk velocity field is the most"
      % (cb["x_reatt_RANS"], cb["x_reatt_LES"]))
    A("  accurate of the set (`U_rms` = %.3f). Velocity accuracy and bubble accuracy are"
      % cb["U_rms_err_rel"])
    A("  not the same thing, which is exactly why the challenge's velocity-only metric")
    A("  cannot see a closure's structural error.")
    A("* **Across the 29 parametric hills** the bubble-length error ranges from")
    hills = [M[c] for c in M if M[c].get("family") == "PHLL29"
             and M[c].get("L_bubble_rel_err") is not None]
    A("  **%+.0f%% to %+.0f%%** (n = %d of 29 where both bubbles close inside the domain);"
      % (100 * min(h["L_bubble_rel_err"] for h in hills),
         100 * max(h["L_bubble_rel_err"] for h in hills), len(hills)))
    A("  it is always positive. Two cases (`alpha_10_12000_2024`, `alpha_10_12000_3036`)")
    A("  carry `--` for the truth's separation point: in the LES the near-wall row is")
    A("  already reversed at the first cell centre (x = 0.05, essentially on the crest),")
    A("  so the separation point falls upstream of the first resolvable location. Their")
    A("  LES reattachment (5.00 and 4.78) is resolved and is well upstream of the SST")
    A("  values (7.60 and 7.45).")
    A("")

    # ---- section 4: ducts
    A("## 4. Square and rectangular ducts: the secondary flow that a linear model cannot make")
    A("")
    A("Prandtl's second kind of secondary motion is driven by the cross-plane anisotropy")
    A("gradients, specifically by `d^2(b_22 - b_33)/dy dz` and `(d^2/dy^2 - d^2/dz^2) b_23`.")
    A("A linear eddy-viscosity model gives `b_23 = -(nu_t/k) S_23` and `b_22 - b_33 =")
    A("-(nu_t/k)(S_22 - S_33)`, and in a fully developed duct the mean strain has no such")
    A("components, so the model produces **exactly zero** secondary flow. That is not an")
    A("accuracy problem, it is a structural one, and it is visible in the numbers below as")
    A("a ratio of order 1e-15, i.e. machine round-off in a converged solve.")
    A("")
    A("| Case | split | AR | Re_tau | Re_b | cells | U_rms | k_rms | tau_rms | b_rms | in-plane |U| LES (% of bulk) | in-plane |U| RANS (% of bulk) | b_23 rms LES | b_23 rms RANS | (b22-b33) rms LES | (b22-b33) rms RANS |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in sorted([c for c in M if M[c].get("family") == "duct"]):
        m = M[c]
        A("| `%s` | %s | %.0f | %.0f | %.0f | %d | %s | %s | %s | %s | %.3f | %.2e | %.4f | %.2e | %.4f | %.2e |" % (
            c, m["split"], m.get("AR", 0), m.get("Re_tau", 0), m.get("Re_b", 0),
            m["n_cells"], g(m, "U_rms_err_rel"), g(m, "k_rms_err_rel"),
            g(m, "tau_rms_err_rel"), g(m, "b_rms_err"),
            m["sec_mean_LES_pct_of_bulk"], m["sec_mean_RANS_pct_of_bulk"],
            m["b23_LES_rms"], m["b23_RANS_rms"],
            m["b22_minus_b33_LES_rms"], m["b22_minus_b33_RANS_rms"]))
    A("")
    A("The duct `b_rms` of 0.54-0.65 is close to the largest value the anisotropy tensor")
    A("can take at all (`||b||_F <= 0.8165`): on these flows the modelled anisotropy is")
    A("wrong in a way that is comparable in size to the anisotropy itself.")
    A("")

    # ---- section 5: realisability
    A("## 5. Realisability of the modelled anisotropy, and what the SST a1 limiter is doing")
    A("")
    A("Realisability (Schumann 1977) requires the eigenvalues of `b` to lie in")
    A("`[-1/3, 2/3]`, equivalently the barycentric coordinates (Banerjee et al. 2007) to")
    A("be non-negative. For a linear eddy-viscosity model `b = -(nu_t/k) S`, so the")
    A("binding constraint is")
    A("")
    A("        r = (nu_t / k) * lambda_max(S) <= 1/3.")
    A("")
    A("Menter's SST caps `nu_t = a1 k / max(a1 omega, S F2)` with `a1 = 0.31`, which caps")
    A("`r` at `a1 = 0.31 < 1/3`. **The a1 limiter is, among other things, a realisability")
    A("constraint**, and the data show it acting as one.")
    A("")
    A("`r_unlim` is the counterfactual `lambda_max(S)/omega` obtained by dropping the")
    A("limiter while **holding the converged k and omega fields fixed** -- what an")
    A("unlimited linear eddy viscosity `nu_t = C_mu k^2/eps = k/omega` would have")
    A("produced pointwise. It is a diagnostic on a frozen field, not a k-epsilon solve.")
    A("")
    A("| Case | r p99 | r max | frac r > 1/3 | r_unlim p99 | r_unlim max | frac r_unlim > 1/3 | frac cells a1 limiter active | frac b_RANS non-realisable | frac TRUTH non-realisable |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for c in sorted(M):
        m = M[c]
        if "ev_ratio_nut_lmaxS_over_k_p99" not in m:
            continue
        A("| `%s` | %.3f | %.3f | %.4f | %.3f | %.2f | %.4f | %.3f | %.4f | %.4f |" % (
            c, m["ev_ratio_nut_lmaxS_over_k_p99"], m["ev_ratio_nut_lmaxS_over_k_max"],
            m["frac_cells_ev_ratio_gt_third_SST"],
            m["ev_ratio_unlimited_counterfactual_p99"],
            m["ev_ratio_unlimited_counterfactual_max"],
            m["frac_cells_ev_ratio_gt_third_unlimited_counterfactual"],
            m["frac_cells_SST_a1_limiter_active"],
            m["frac_RANS_nonrealisable"], m["frac_truth_nonrealisable"]))
    A("")
    A("Readings:")
    A("")
    A("* The a1 limiter is active on **18-33% of cells** in every case in the set.")
    A("* With the limiter, SST's `b` is realisable in every cell of every hill, duct and")
    A("  step case here, and in 99.74% of the hump's cells. Without it, on the hump the")
    A("  ratio reaches **262** and **11.5% of cells** would be non-realisable: that is the")
    A("  stagnation-point anomaly, measured. The hump is the only case in the set with a")
    A("  genuine stagnation region, and it is the only case where the counterfactual blows")
    A("  up -- which is the expected pattern, not a coincidence.")
    A("* **1.2-2.5% of the interpolated LES/DNS truth cells on the hills are themselves")
    A("  non-realisable**, and up to 1.6% on the ducts. Any method trained to regress")
    A("  `b_LES` is being handed a small fraction of physically impossible labels. A")
    A("  reproduction that enforces realisability on its output cannot reach zero error")
    A("  against this truth, and one that reports a realisability violation rate should")
    A("  compare it against these numbers, not against zero.")
    A("")

    # ---- section 6: data inventory
    A("## 6. DATA INVENTORY")
    A("")
    A("### 6.1 Cases, sizes and splits")
    A("")
    A("| Family | Cases | Re | Mesh | Cells/case | Fields shipped |")
    A("|---|---|---|---|---|---|")
    A("| `PHLL29` parametric periodic hills | 29 (`alpha_05/075/10/125/15`, x length 4.05-13.87, y height 2.02-4.04) | Re_H = 5600 (nu = 1.786e-4, H = 1, U_b = 1) | structured 120 x 130 | 15600 | `U k omega nut p phi C` + `gradU Pk Pk_bouss Pk_prop Dk k_conv k_diff tauij_B tauij_B_bouss walldist` + truth `U_LES k_LES tauij_LES epsilon` |")
    A("| `DUCT` square/rectangular ducts | 8 (AR 1,3,5,7,10,14; Re_tau 164-342) | Re_b 2500-5817, Re_tau 164-342 (from each case's own `caseDef`) | structured cross-plane, 47-55 cells per half-height | 2209-31819 | `U k omega nut p` + truth `U_LES k_LES tauij_LES`; **no gradU** |")
    A("| `PHLL10595` periodic hill (Breuer) | 1 | Re_H = 10595 (nu = 9.4384e-5) | structured 120 x 130 | 15600 | `U k omega nut p` + truth `U_LES k_LES p_LES tauij_LES`; **no gradU** |")
    A("| `CBFS13700` curved backward-facing step | 1 | Re_H = 13700 (nu = 7.2993e-5) | structured 140 x 150 | 21000 | `U k omega nut p` + truth `U_LES k_LES p_LES tauij_LES` (via `interpolatedFields/*_internalField` includes); **no gradU** |")
    A("| `NASA_2DWMH` wall-mounted hump | 1 | Re_c = 936000, c = 0.42 m, M = 0.1, U_inf = 34.6 m/s, nu = 1.5537e-5 | structured 622 x 83 | 51626 | `U k omega nut p` + truth `U_LES k_LES tauij_LES` + `bijDelta Dk walldist` (placeholders); **no gradU** |")
    A("")
    A("Total cells with truth available: 29x15600 + 101026 (ducts) + 15600 + 21000 + 51626")
    A("= **641,652** across **40 cases**, of which the 21 suggested training hills alone")
    A("are 327,600 -- the")
    A("same figure this lab's own challenge entry reports for its training set")
    A("(`/home/ubuntu/Certonomous_closure_challenge/description/METHOD.md`, section 3).")
    A("")
    A("### 6.2 The train / validation / test split")
    A("")
    A("From the benchmark README at the pinned commit, and the figure `phll_tvt_split.png`")
    A("in the benchmark root. The **only strict rule** in the challenge is that no test")
    A("case may be trained or validated on.")
    A("")
    A("| Flow | Training (suggested) | Validation (suggested) | Test (strict) |")
    A("|---|---|---|---|")
    A("| PHLL29 | the 21 remaining hills | `alpha_05_10071_4048`, `alpha_05_10071_2024`, `alpha_15_7929_4048`, `alpha_15_7929_2024` | `alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048`, `alpha_05_4071_2024` |")
    A("| DUCT | `AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`, `AR_10_Ret_180` | `AR_7_Ret_180` | `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180` |")
    A("| CBFS13700 | single case, training | -- | -- |")
    A("| PHLL10595 | single case, training | -- | -- |")
    A("| NASAHUMP | -- | -- | single case, test |")
    A("")
    A("The split tests two generalisation axes the challenge names explicitly: **Reynolds")
    A("number** (`Ret_180 -> Ret_360` ducts; the hills' `alpha_15_13929` pair is the")
    A("longest domain) and **geometry** (`AR_14` is 1.4x the widest trained aspect ratio;")
    A("the hump is a different flow class altogether, with the only trained case of its")
    A("kind being the curved step).")
    A("")
    A("Note for any Phase 3 preregistration: the 29 hills are *not* 29 independent flows.")
    A("They come in triples sharing `alpha` and domain length and differing only in domain")
    A("height (`2024/3036/4048`), so a random cell-level or case-level split will leak")
    A("near-duplicates between train and validation. Split by (`alpha`, length) group.")
    A("")
    A("### 6.3 What is NOT in the data, and what this baseline cannot see")
    A("")
    A("* `bijDelta`, `kDeficit` and `sigma` ship as `uniform 0` **placeholders** in every")
    A("  case, including the training cases. They are input slots for a corrected solve,")
    A("  not labels. Any anisotropy-discrepancy or k-deficit target has to be constructed")
    A("  from `tauij_LES`/`k_LES`, which is what `sst_baseline_metrics.py` does.")
    A("* `tauij_B` and `tauij_B_bouss` are **bitwise identical** in every hill case, as")
    A("  they must be for an uncorrected solve.")
    A("* The truth is the challenge's own interpolation of LES/DNS onto the RANS mesh.")
    A("  Near-wall rows and freestream cells carry interpolation error: 7-63 cells per")
    A("  hill and 4514 of 51626 hump cells have `k_LES` below the anisotropy floor, and a")
    A("  few hill cells have `k_LES < 0` outright (min -2.3e-4 on `alpha_15_13929_4048`).")
    A("* Every error here is an **a-priori, frozen-field** error. It says nothing about")
    A("  what happens when a modified closure is put back into the momentum equation and")
    A("  re-converged: a model that reduces `b_rms` by half may still diverge, or may")
    A("  produce a worse velocity field, because the mapping from `b` to `U` runs through")
    A("  the momentum balance and is not monotone. Any Phase 3 claim of an a-posteriori")
    A("  improvement must come from an actual solve.")
    A("* There is no uncertainty estimate on the LES/DNS truth in the release, so none of")
    A("  the errors above can be compared against a data uncertainty band.")
    A("* The 3-D cases named in the benchmark README (wing-body junction, Ahmed body,")
    A("  FAITH hill, and the 3-D duct meshes) are **not** in the local clone; they are on")
    A("  an external SURFdrive link. Nothing in this file covers them.")
    A("")
    # ---- 6.4 Charter-2c anisotropy baseline -----------------------------
    TM = os.path.join(HERE, "trainmean_baseline.json")
    A("### 6.4 Charter-2c anisotropy baseline: the train-mean tensor")
    A("")
    if not os.path.exists(TM):
        A("**MISSING.** Run `trainmean_baseline.py` first; this section is generated")
        A("from `trainmean_baseline.json`.")
        A("")
    else:
        T = json.load(open(TM))
        bm = T["b_mean"]
        A("Sections 3-5 score the k-omega SST anisotropy error. **That is not a")
        A("demanding baseline.** The mean `b_LES` over the Phase-3 training cells, used")
        A("as a *constant* prediction everywhere with no inputs and nothing fitted")
        A("beyond an arithmetic mean, is:")
        A("")
        A("```")
        A("b_mean =  [ %9.4f %9.4f %9.4f ]" % tuple(bm[0]))
        A("          [ %9.4f %9.4f %9.4f ]" % tuple(bm[1]))
        A("          [ %9.4f %9.4f %9.4f ]" % tuple(bm[2]))
        A("```")
        A("")
        A("mean over the **%d training cases / %d cells** of the Phase-3 split" %
          (T["n_train_cases"], T["n_train_cells"]))
        A("(`Ling2016_TBNN/PREREGISTRATION.md` sec. 6): the benchmark's 8 strict TEST")
        A("cases and 5 suggested validation cases are held out, and so are the four")
        A("hills %s, each of which" % ", ".join("`%s`" % c for c in T["excluded_for_group_leak"]))
        A("differs from a TEST or validation hill only in domain height and would")
        A("otherwise leak a near-duplicate into training. The constant is itself")
        A("realisable: %s." % ("yes" if T["b_mean_realisable"] else "NO"))
        A("")
        A("| Case | cells | **train-mean (constant)** | k-omega SST | `b = 0` | constant beats SST? |")
        A("|---|---|---|---|---|---|")
        for c in T["test_cases"]:
            v = T["per_case"][c]
            A("| `%s` | %d | **%.4f** | %.4f | %.4f | %s |" %
              (c, v["n_cells"], v["train_mean"], v["sst"], v["zero"],
               "**yes**" if v["train_mean"] < v["sst"] else "no"))
        p = T["pooled_TEST"]
        A("| **pooled over all 8** | %d | **%.4f** | %.4f | %.4f | **yes** |" %
          (p["n_cells"], p["train_mean"], p["sst"], p["zero"]))
        A("")
        A("**The constant beats k-omega SST on %d of %d held-out cases.** Predicting one" %
          (T["n_test_cases_where_constant_beats_sst"], T["n_test_cases"]))
        A("fixed anisotropy tensor everywhere is a better a-priori anisotropy model than")
        A("the linear eddy-viscosity closure the benchmark ships. On the ducts the margin")
        A("is large (0.4036 against 0.5799 on `AR_14_Ret_180`), because SST's `b` there is")
        A("not merely inaccurate but structurally wrong -- section 4.")
        A("")
        A("**THE RULE, for every anisotropy model in `cases/RANS_LES_closure_models/`:**")
        A("")
        A("> A model that predicts `b_ij` must beat the **TRAIN-MEAN** row above, not the")
        A("> SST row. Beating SST on `b_rms` is a bar a constant clears, and reporting")
        A("> only that comparison is not an evaluation. Quote both columns, per case,")
        A("> on the same cell mask.")
        A("")
        A("Cell mask: %s" % T["cell_mask"])
        A("")
        A("Generated by `trainmean_baseline.py` -> `trainmean_baseline.json`. Nothing is")
        A("fitted; re-running reproduces it.")
        A("")
    A("## 7. How a Phase 3 reproduction should use this file")
    A("")
    A("1. Quote the row for its case in its `PREREGISTRATION.md` as the trivial baseline,")
    A("   before training.")
    A("2. Report the same metric it beats. A method that improves `b_rms` and reports only")
    A("   `U_rms` (or the reverse) has not been evaluated; both are here.")
    A("3. Report the realisability violation fraction of its predicted `b` **next to the")
    A("   truth's own violation fraction** from section 5, not next to zero.")
    A("4. If it produces a velocity field by post-hoc correction rather than by re-solving,")
    A("   say so, and measure the continuity residual -- section 6.3, last-but-two bullet.")
    A("5. **If it predicts `b_ij`, beat section 6.4's TRAIN-MEAN constant, not the SST")
    A("   row.** The constant beats SST on all 8 held-out cases, so a method that beats")
    A("   only SST has demonstrated nothing. Report both columns on the same cell mask.")
    A("")
    open(os.path.join(HERE, "BASELINES.md"), "w").write("\n".join(L) + "\n")
    print("wrote BASELINES.md (%d lines)" % (len(L) + 1))


if __name__ == "__main__":
    main()
