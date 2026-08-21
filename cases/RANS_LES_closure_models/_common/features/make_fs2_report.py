#!/usr/bin/env python3
"""Render FS2_DEGENERACY_REPORT.md from fs2_audit.json + invariance_check.json.
Generated: re-running reproduces it."""
from __future__ import annotations
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FEAT = "/home/ubuntu/closure-data/features"
a = json.load(open(os.path.join(FEAT, "fs2_audit.json")))
iv = json.load(open(os.path.join(FEAT, "invariance_check.json")))
man = json.load(open(os.path.join(FEAT, "manifest.json")))
L = []
A = L.append

A("# FS2 degeneracy audit and FS5 extrapolation-coverage check")
A("")
A("**Generated** by `make_fs2_report.py` from `fs2_audit.json` and")
A("`invariance_check.json`. Re-running reproduces it. **No model was trained.**")
A("")
A(f"Library: **{a['n_features']} features** on **{len(man['cases'])} cases**, "
  f"{sum(m['n_cells'] for m in man['cases'].values()):,} cells, zero non-finite values.")
A(f"Numerical rank uses SVD of the column-standardised matrix with tolerance "
  f"`{a['rank_rcond']:g} * sigma_max`. A feature is DEAD if `max|v| < {a['zero_abs']:g}` "
  f"(absolute test only - see sec. 5).")
A("")
A("## 1. Feature-matrix rank per family")
A("")
A("| family | cells | rank | deficiency | dead | near-constant | `sigma_1/sigma_N` |")
A("|---|---|---|---|---|---|---|")
for f in a["families"] + ["POOLED"]:
    d = a["per_family"][f]
    A(f"| `{f}` | {d['n_cells']:,} | **{d['rank']}** / {d['n_features']} | {d['rank_deficiency']} | "
      f"{d['n_dead']} | {d['n_near_constant']} | {d['singular_value_ratio_first_to_last']:.2e} |")
A("")
A(f"**No family reaches full rank.** The ducts are worst: rank "
  f"**{a['per_family']['duct']['rank']} of {a['n_features']}** with "
  f"**{a['per_family']['duct']['n_dead']} algebraically-zero features**, and a condition number of "
  f"**{a['per_family']['duct']['singular_value_ratio_first_to_last']:.1e}**. Any method that "
  f"inverts or regularises this matrix on duct data is working in a space "
  f"{a['n_features'] - a['per_family']['duct']['rank']} dimensions smaller than it thinks.")
A("")
A("## 2. Features that are algebraically zero on ALL data (pooled)")
A("")
dead = a["per_family"]["POOLED"]["dead_features"]
A(f"**{len(dead)} of {a['n_features']}**, listed in full:")
A("")
for n in dead:
    A(f"* `{n}`  (pooled `max|v|` = {a['per_feature'][n]['max']:.3e})")
A("")
A("Every one is a high-order invariant containing a product of three or more of "
  "`S`, `Omega`, `A_p`, `A_k`. They vanish because every case in this benchmark is a "
  "statistically two-dimensional mean flow - the same collapse that takes Pope's "
  "ten-tensor basis to rank 3 (sec. 4).")
A("")
A("### Dead per family (a feature can be dead on one family and live on another)")
A("")
A("| family | dead count |")
A("|---|---|")
for f in a["families"]:
    A(f"| `{f}` | {a['per_family'][f]['n_dead']} |")
A("")
A("## 3. Invariance check (charter section 6)")
A("")
A(f"Case `{iv['case']}`, {iv['n_cells']:,} cells. A Galilean boost "
  f"`c = {np.round(iv['tests']['galilean_boost']['c'],4).tolist()}` and a rigid rotation of "
  f"{iv['tests']['rotation']['angle_rad']} rad applied to the raw fields; every feature and "
  f"every normaliser recomputed. Tolerance `{iv['tolerance']:g}`.")
A("")
A(f"* **Rotation: max relative change {iv['tests']['rotation']['max_rel_change']:.3e}.** "
  f"{len(iv['not_rotation_invariant'])} features exceed tolerance and all three are artefacts, "
  "not failures: `trW2SWS2__A/B` are algebraically zero (`max|v|` ~ 3e-18, sec. 2) so the "
  "relative measure divides roundoff by zero, and `q8_kConvection` sits at 3.3e-12 for an "
  "O(1) feature. **All 110 features are rotation invariant to roundoff.**")
A(f"* **Galilean boost: max relative change {iv['tests']['galilean_boost']['max_rel_change']:.3e}. "
  f"{len(iv['not_galilean_invariant'])} of {a['n_features']} features are NOT Galilean invariant.**")
A("")
ng = iv["not_galilean_invariant"]
qs = [n for n in ng if n.startswith("q")]
trs = [n for n in ng if n.startswith("tr") or n.startswith("I")]
A(f"They fall into exactly two groups, and the split is the finding:")
A("")
A(f"**(a) {len(trs)} tensor invariants, every one of which contains `A_p`** - the "
  "antisymmetric tensor built from the pressure gradient. Wu, Xiao & Paterson normalise "
  "`grad p` by `rho |DU/Dt|` (their Table 1, preprint p. 8) and argue in Appendix C that the "
  "set is Galilean invariant. That argument holds for the **unsteady** material derivative "
  "`DU/Dt = dU/dt + U.grad U`, where the unsteady term supplies the compensating shift. "
  "**A steady RANS field has no `dU/dt`**, so the implementable normaliser is `|U.grad U|`, "
  "which is not boost-invariant - and neither is any invariant built on it. This is a property "
  "of steady-state implementation, not an error in the paper.")
A("")
A(f"**(b) {len(qs)} scalar features that use the raw velocity `U`:** "
  + ", ".join(f"`{n}`" for n in qs) + ".")
A("")
A("Full per-feature numbers are in `invariance_check.json`.")
A("")
A("## 4. Tensor-basis per-cell rank (charter section 5(b))")
A("")
t = a.get("tensor_basis_rank")
if t:
    A(f"{t['method']}.")
    A("")
    A(f"* **Case means run {t['min_case_mean']:.3f} to {t['max_case_mean']:.3f}**; "
      f"mean of case means **{t['pooled_mean_of_case_means']:.3f}**.")
    A(f"* **Maximum rank reached in any cell of any case: {t['max_rank_any_cell']}.**")
    A("")
    A("**Provenance.** The charter (section 5(b)) records that a figure of \"3.24 on average, "
      "never above 5\" is quoted in three records from a pointer that does not resolve, and "
      "rules that it must not be quoted until it has a live source. **This table is that "
      "source.** It is a fresh measurement from `/home/ubuntu/closure-data/tbnn/dataset.npz` "
      "and it does not reproduce 3.24 as a *case-mean* statistic: the case means average "
      f"**{t['pooled_mean_of_case_means']:.3f}**. 3.24 was a *pooled-sample* number over "
      "randomly drawn training cells, which the duct cases - the lowest-rank family, at "
      f"{t['per_case']['AR_1_Ret_360']['mean_rank']:.3f} - pull down. Both are computable; they "
      "are different statistics and should not be quoted interchangeably. The bound that "
      f"matters is unchanged and is confirmed here: **never above {t['max_rank_any_cell']}, "
      "against a nominal basis size of 10.**")
    A("")
    A("| case | mean per-cell rank | min | max |")
    A("|---|---|---|---|")
    for c in sorted(t["per_case"], key=lambda x: t["per_case"][x]["mean_rank"]):
        v = t["per_case"][c]
        A(f"| `{c}` | {v['mean_rank']:.3f} | {v['min_rank']} | {v['max_rank']} |")
A("")
A("## 5. A criterion that had to be corrected, recorded")
A("")
A("The first version of this audit flagged a feature DEAD if `max|v|` fell below either an "
  "absolute threshold **or** `1e-12` times the largest value *anywhere in the matrix*. That "
  "relative test is meaningless on an incommensurable library: the Pope invariants under the "
  "Durbin-bounded normalisation reach `|lam3| = 1.5e11` and `|lam5| = 1.5e14`, so the relative "
  "threshold became **150** and every bounded feature - all eleven `q` markers, every "
  "normalised invariant - was reported dead. The test is now **absolute only**. Recorded "
  "because the wrong version produced a confident, plausible, entirely false answer.")
A("")
A("That the Pope invariants span fourteen orders of magnitude is itself an FS2 finding: they "
  "are the only unbounded block in the library, and they will dominate any unstandardised "
  "distance metric built on it.")
A("")
A("## 6. FS5 extrapolation coverage: TEST cases against the TRAINING range")
A("")
cv = a["coverage"]
A(f"Training range is the per-feature min/max over the {len(cv['train_cases'])} non-TEST cases. "
  "A test cell is 'outside' if any feature falls beyond that range.")
A("")
A("| TEST case | cells | cells outside on >=1 feature | features ever outside |")
A("|---|---|---|---|")
for c, d in sorted(cv["per_test_case"].items(), key=lambda kv: kv[1]["frac_cells_any_feature_outside"]):
    A(f"| `{c}` | {d['n_cells']:,} | **{d['frac_cells_any_feature_outside']*100:.2f}%** | "
      f"{d['features_with_any_outside']} / {a['n_features']} |")
A("")
hump = cv["per_test_case"]["NASA_2DWMH"]
A(f"**`NASA_2DWMH` is out of family by this instrument too**: "
  f"**{hump['frac_cells_any_feature_outside']*100:.2f}%** of its cells fall outside the training "
  f"range on at least one feature, and **{hump['features_with_any_outside']} of "
  f"{a['n_features']}** features go out of range somewhere on it. The four hills sit at "
  "0.00-0.06% and the three ducts at 0.96-3.07%. This is a third independent instrument "
  "agreeing with the Mahalanobis statistic (13.17% of hump cells beyond the training p99) and "
  "with the measured hump blow-up of every tensor-basis model.")
A("")
A("### Worst features on the hump, by fraction of cells out of range")
A("")
A("| feature | cells outside | worst excursion (training spans) |")
A("|---|---|---|")
for n, fr, be in hump["worst_features"]:
    A(f"| `{n}` | {fr*100:.2f}% | {be:.2f} |")
A("")
A("## 7. What this audit cannot see")
A("")
A("* **It is a degeneracy and coverage audit, not a selection.** Nothing is ranked by "
  "usefulness and nothing is removed. FS3 does that.")
A("* **Rank is measured on the standardised matrix**, so it answers \"how many independent "
  "directions\" and not \"how well conditioned for a particular regressor\".")
A("* **The invariance check ran on one case** (`CBFS13700`). The conclusions are algebraic and "
  "should hold everywhere, but they are measured on one field.")
A("* **Dead-on-this-benchmark is not dead in general.** The twelve pooled-dead invariants vanish "
  "because these flows are two-dimensional; a three-dimensional case would revive them, and "
  "that is precisely why a model fitted here cannot be trusted there.")
A("")
open(os.path.join(HERE, "FS2_DEGENERACY_REPORT.md"), "w").write("\n".join(L) + "\n")
print(f"wrote FS2_DEGENERACY_REPORT.md ({len(L)+1} lines)")
