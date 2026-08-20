# PREREGISTRATION — Kaandorp & Dwight 2020 Tensor-Basis Random Forest (TBRF)

**Status: written before any model was fitted.** Nothing in this file was chosen
after seeing a training or test result. The comparators, the acceptance bands and
the falsifying outcomes below are frozen at the moment this file is committed.

**This is a labelled VARIANT, not an exact reproduction.** Section 2 lists every
departure. Section 5 states what a PASS here would and would not mean.

* Paper: M. L. A. Kaandorp & R. P. Dwight, *Data-Driven Modelling of the Reynolds
  Stress Tensor using Random Forests with Invariance*, Computers & Fluids,
  arXiv:1810.08794v2 (17 Mar 2020).
* PDF on disk (title page checked): `/home/ubuntu/Certonomous/docs/papers/closure/Kaandorp2020_random_forests.pdf`
* Data: Closure Challenge benchmark clone `/home/ubuntu/closure-challenge-benchmark`
  at commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`
  (source `https://github.com/rmcconke/closure-challenge-benchmark.git`;
  sha256 of `git ls-files -s data` = `e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401`).
  Read-only. Derived arrays are written **outside** the repo to
  `/home/ubuntu/closure-data/kaandorp_tbrf/`.

---

## 1. The paper's own numbers (title-verified, quoted before we run anything)

| Where | Quantity | Value |
|---|---|---|
| **Table 3, preprint p. 37** | RMSE of `[b]ij`, square duct **SD3500**, case **C3** = 5 features (FS1, S and R invariants only) | TBRF **0.0995**, TBNN **0.0871** |
| **Table 3, preprint p. 37** | same, case **C4** = 17 features (FS1+FS2+FS3) | TBRF **0.0521**, TBNN **0.0681** |
| **Table 4, preprint p. 41** | Backward-facing step **BFS5100**, reattachment `x_reattach [x/h]` | RANS **5.45**, RANS+`b_ij,TBRF` **6.32**, DNS (Le et al. 1997) **6.28**, experiment (Jovic & Driver 1994) **6.0 ± 0.15** |
| **Table 2, preprint p. 31** | Training set for **all four** cases C1-C4 | PH5600 + PH10595 + CD12600, `N_sample` = **21,000** |
| **p. 30** | Hyperparameters | 100 TBDTs; **11 of 17** features drawn per split; **min 9 samples per leaf**; regularisation **Γ = 1e-12**. For C3: fully grown trees, all 5 features per split |
| **p. 30** | Feature pre-filter | features with variance **< 1e-4** discarded ("either did not contain any information at all, or were largely spurious") |
| **p. 19-20** | Split search | brute-force over feature index `j`; Brent 1-D optimisation over threshold `s`; brute force for `s` once a bin holds **< 150** samples |
| **p. 20-21, 57** | Aggregation | **median** over the 100 trees, not the mean; Gaussian spatial smoothing with **σ = 3 cell lengths** applied only before propagation through the solver |
| **p. 24, sec. 2.7** | Propagation | `τ ≈ (2/3)kI + 2k[(1-γ)b_B + γ b_ML]`, continuation on γ from 0, raised in steps of 0.1 "until the solver became unstable, yielding γ_max = 0.8" |

The paper's own text on the **central claim** (p. 36): *"it can generally be seen
that the introduction of extra features has significantly more effect than the
choice of neural-networks versus random-forests"* — i.e. **feature set matters
more than model class** (verification flag F18).

The paper's own text on **realisability** (F19): the TBRF produced realisable `b`
without any explicit constraint; the TBNN did not, near the wall.

---

## 2. Why this is a VARIANT — every departure, disclosed

### 2.1 Cases that do not exist on this machine

| Paper's case | Role in paper | On disk? | What we do instead |
|---|---|---|---|
| **CD12600** converging-diverging channel (Laval & Marquillie) | 1 of 3 training flows | **NO** | Train on the remaining two flow families only. Our training set is therefore **2 of the paper's 3 training flows**. |
| **SD3500** square duct `Re_b` = 3500 | prediction case for C3/C4, the Table-3 numbers | **NO** | Two square ducts that **bracket** it: `AR_1_Ret_180` (`Re_b` = 2500, `Re_tau` = 165) and `AR_1_Ret_360` (`Re_b` = 5693, `Re_tau` = 342). Primary = `AR_1_Ret_360`. |
| **BFS5100** backward-facing step `Re` = 5100 | prediction case for C2, the Table-4 numbers | **NO** | **Table 4 is not attempted.** No sharp-step BFS case exists here. Reported as BLOCKED-ON-DATA. |
| **CBFS13700** curved backward-facing step | prediction case C1 | **YES — the same case** | Used as a secondary held-out test case. |
| **PH5600**, **PH10595** | training flows | **YES** | PH5600 as the 29-hill parametric family; PH10595 is the Breuer hill, the same case. |

**Consequence: the numbers 0.0995 / 0.0521 / 6.32 cannot be hit or missed here.**
Different Reynolds number, different duct, one third of the training data absent,
and no BFS case at all. Any statement of the form "we reproduced 0.0521" would be
false. See section 5.

### 2.2 Other disclosed departures

| # | Departure | Why | Effect on the headline claim |
|---|---|---|---|
| D1 | `gradU` is **not shipped** for `DUCT`, `PH_Breuer`, `CBFS`. It is computed by `of_read.structured_gradient()`, a curvilinear chain-rule gradient on the structured block. Verified against the `gradU` OpenFOAM itself wrote on three periodic hills: **0.47-0.96 % relative L2 in the interior** (median cellwise 0.10-0.13 %), 2.5-3.3 % including the one-sided boundary rows (`BASELINES.md` sec. 1). | data | affects both feature sets identically |
| D2 | Turbulent time scale `T = k/ε` with `ε = β* k ω` (`β* = 0.09`, Menter 1994 eq. A6) is **bounded below** by the Durbin bound `6 sqrt(ν/ε)`. Kaandorp state no such bound. | `k/ε` is unbounded in the low-`k` freestream and would produce `O(10^12)` invariants there | affects both feature sets identically; also applied to the sibling TBNN reproduction so the two are comparable |
| D3 | Wall distance `d` (needed for FS3 feature q3) is **not shipped** for `DUCT`, `PH_Breuer`, `CBFS`. It is computed as the distance from each cell centre to the nearest face centre or vertex of a `polyMesh` patch of `type wall`. **Verification to be reported:** compared against the shipped `walldist` field on the 29 hills. | data | FS-17 only |
| D4 | FS3 normalisation. Kaandorp's Table 1 lists a "normalization factor" per feature but not the combination rule. We use the rule stated by their two cited sources — Wang, Wu & Xiao 2017 Table 1 and Wu, Xiao & Paterson 2018 eq. (8), both VERIFIED-PDF on disk: `q = q_raw / (|q_raw| + |q_norm|)`, bounded in `[-1,1]`, **except** the wall-distance Reynolds number which is already dimensionless. | ambiguity in the paper | FS-17 only; disclosed, not tuned |
| D5 | FS2's three starred entries (`R²A_kS*`, `R²A_kS²*`, `R²SA_kS²*`) carry the note "all cyclic permutations of labels of anti-symmetric tensors need to be taken into account". We take **one** labelling per entry, giving 10 FS2 features and **25 raw features in total (6 + 10 + 9)**. This is the reading consistent with the paper's own arithmetic: 25 raw minus the low-variance filter = the 17 they report. | ambiguity in the paper | FS-17 only |
| D6 | Split-threshold search. The paper uses Brent 1-D optimisation over `s`, falling back to brute force below 150 samples in a bin. Brent is a continuous optimiser applied to an objective that is piecewise constant in `s`, so it can stop at a non-optimal split. We use **exact brute force over every distinct threshold** when a node holds `≤ BF_MAX` samples and over `Q` quantile candidates otherwise; `BF_MAX` and `Q` are fixed before training and reported in `RESULTS.md`. This is at least as good as Brent and is deterministic. | speed + determinism | affects both feature sets identically |
| D7 | **Depth cap.** The paper's trees are grown to the leaf-size limit only. We additionally cap `max_depth = 30`, so a single run cannot blow past its compute budget. Reported: the fraction of leaves that hit the depth cap rather than the 9-sample limit (if that fraction is non-negligible the cap is a real departure and will be said so). | compute safety (the `kill` command is unavailable in this environment; every run must terminate on its own) | affects both feature sets identically |
| D8 | **Basis scaling.** Each basis tensor `T^(m)` is divided by a constant `c_m` = RMS of `‖T^(m)‖_F` over the **training** sample, computed once, from training data only, never from test data, never tuned. This is a diagonal reparametrisation of `g` and changes nothing except what `Γ I` means. Without it `Γ = 1e-12` is numerically indistinguishable from `Γ = 0` on a matrix whose entries span 12 decades. | numerical conditioning | affects both feature sets identically |
| D9 | **A-priori only.** No re-solve. `γ_max`, the Gaussian σ = 3 filter and the modified `k`-equation of their section 2.7 are **not** exercised. Table 4 is therefore out of reach for two independent reasons (no BFS case, no propagation). | scope | Table 4 not attempted |
| D10 | Cells where `k_LES < 1e-4 × mean(k_LES)` are masked out of both fitting and scoring, as in `BASELINES.md` (`b = τ/2k` is meaningless there). Mask counts reported per case. | data | affects both feature sets identically |

**D1, D2, D6, D7, D8 and D10 are applied identically to the 5-feature and the
17-feature model.** Claim (i) is a difference between two models that differ only
in their feature set, so it is insulated from all six.

---

## 3. Frozen experimental design

### 3.1 Splits (frozen; a code assertion enforces them)

**TRAIN (20 cases, 312,000 cells before masking):**
the 19 group-clean parametric periodic hills at `Re_H` = 5600 + `PHLL10595`.

"Group-clean" means: the benchmark's own README warns that the 29 hills are not 29
independent flows — they come in triples sharing (`alpha`, domain length) and
differing only in domain height (`2024/3036/4048`), so the benchmark's suggested
train split leaks near-duplicates of its own test hills. We therefore drop, on top
of the benchmark's 4 test and 4 validation hills, the **two remaining group
siblings** `alpha_15_13929_3036` and `alpha_05_4071_3036`. 29 − 4 − 4 − 2 = 19.

**HELD-OUT TEST (frozen, never seen in fitting):**

| Tag | Case | Why | SST `b_rms` to beat (BASELINES.md sec. 3/4) |
|---|---|---|---|
| **T1 (PRIMARY)** | `AR_1_Ret_360` — square duct, AR 1, `Re_tau` 342, `Re_b` 5693, 3025 cells | closest available analogue of the paper's SD3500 and a **strict** benchmark test case; brackets `Re_b` = 3500 from above | **0.5843** |
| T2 | `AR_1_Ret_180` — square duct, AR 1, `Re_tau` 165, `Re_b` 2500, 2209 cells | brackets `Re_b` = 3500 from below | **0.6541** |
| T3 | `CBFS13700` — curved backward-facing step, 21000 cells | **literally the paper's case C1** | **0.3051** |

**IN-DISTRIBUTION CONTROL (reported, no claim rides on it):** the 4 benchmark TEST
hills `alpha_15_13929_{2024,4048}`, `alpha_05_4071_{2024,4048}`. With the two group
siblings removed from training these are now group-clean, but they remain the same
flow class at the same `Re` as the training set, so a good number here is evidence
of interpolation, not of generalisation.

**NOT USED AT ALL:** `NASA_2DWMH` (different flow class, `Re_c` = 936000, and its
`r_unlim` diagnostic reaches 262 — an extrapolation regime that would dominate any
aggregate); all other ducts (`AR_3,5,7,10,14`); the 4 benchmark validation hills.

### 3.2 Disjointness assertion (runs in code, aborts the run on failure)

The training script asserts, and `RESULTS.md` will report the assertion output:

1. `set(TRAIN_CASES) ∩ set(TEST_CASES) == ∅` (case-level).
2. `set(TRAIN_CASES) ∩ set(CONTROL_CASES) == ∅`.
3. No (`alpha`, `length`) group appears in both `TRAIN_CASES` and
   `TEST_CASES ∪ CONTROL_CASES` (group-level; this is the leak the benchmark README
   warns about).
4. Every global cell index drawn into the `N_sample` = 21,000 training draw has
   `case_id ∈ TRAIN_CASES`; the intersection of the drawn global cell-index set with
   the global cell-index set of every test/control case is empty.
5. The features of a test case are assembled from that case's own fields only —
   no cross-case normalisation constant, no global standardisation fitted on
   test data. The only train-fitted constants that touch test data are the FS
   variance filter, the basis scale factors `c_m` (D8) and the Mahalanobis
   mean/covariance, and all three are computed from the 21,000 training samples.

### 3.3 Model (the paper's hyperparameters, used verbatim — no tuning)

`N_trees` = 100, `min_samples_leaf` = 9, `Γ` = 1e-12, `max_features` = 11 for the
17-feature model and **all** features for the 5-feature model (the paper's own C3
setting), median aggregation over trees, `N_sample` = 21,000 drawn from the
training pool. **We do not tune any hyperparameter.**

**One deliberate deviation from the paper's C3, stated before running.** The paper's
C3 (5 features) additionally uses **fully grown** trees (`min_samples_leaf` = 1),
while its C4 (17 features) uses 9. That difference confounds the very contrast
Table 3 is used to argue: C3-vs-C4 differs in feature set *and* in tree depth. Our
**headline** FS-5 model therefore uses `min_samples_leaf` = 9, identical to FS-17,
so that claim (i) isolates the feature set and nothing else. The paper-faithful
FS-5 configuration (`min_samples_leaf` = 1, fully grown, all 5 features) is run
**separately** as a secondary, budget permitting, and reported beside it. If the
two FS-5 configurations disagree about claim (i), that fact is the result. The paper tuned theirs on
PH2800 + SD3200, neither of which exists here; rather than substitute a tuning set
and give ourselves a free parameter, we take their published values as given. This
removes a researcher degree of freedom by construction.

**Seeds: 0, 1, 2, 3, 4** (5 forests per feature set). A seed controls the 21,000-sample
draw, the bagging draw of each tree, and the per-split feature subsets. Reported as
mean ± sample std over the 5 seeds.

### 3.4 Feature sets

* **FS-5** = the FS1 invariants (traces of `S²`, `S³`, `R²`, `R²S`, `R²S²`, `R²SRS²`;
  6 raw) after the paper's variance < 1e-4 filter. The paper's C3 has 5 survivors.
* **FS-17** = FS1 + FS2 + FS3 (6 + 10 + 9 = 25 raw) after the same filter. The
  paper's C1/C2/C4 have 17 survivors.

**The surviving counts on our training set are an output, not an input.** If we do
not get 5 and 17 we report the numbers we get and name the models by their actual
counts; the claim below is about *more features vs fewer*, and does not require the
counts to match the paper's.

### 3.5 Metrics

The paper does **not** state which RMSE convention Table 3 uses. Both are reported,
always labelled:

* `b_rms_F` = `sqrt(mean_cells ‖b_pred − b_LES‖_F²)` — the `BASELINES.md` convention,
  the only one directly comparable to the SST rows.
* `b_rmse_comp` = `b_rms_F / 3` — per-tensor-component RMSE, the convention under
  which Kaandorp's 0.0521 is the more plausible reading.

Scored on masked-valid cells only (D10). The paper's 0.0521 is quoted **beside**
`b_rmse_comp` as context, never as a target that was hit.

### 3.6 Trivial baselines, frozen now

| Tag | Predictor | Value on T1 / T2 / T3 (`b_rms_F`) |
|---|---|---|
| **B0** | uncorrected k-omega SST `b` (Charter 2c baseline) | 0.5843 / 0.6541 / 0.3051 (from `BASELINES.md`, already computed, not re-derived here) |
| **B1** | constant `b` = mean of `b_LES` over the 21,000 training samples | to be computed |
| **B2** | `b ≡ 0` (isotropic); equals `sqrt(mean ‖b_LES‖_F²)`, i.e. the size of the truth itself | to be computed |

A method that does not beat **B1** and **B2** has learned nothing at all, whatever
it does against B0.

---

## 4. The falsifiable claims

### Claim (i) — THE CENTRAL CLAIM OF THE PAPER (F18)

> Adding the full feature set (FS-17) beats the `S,R`-only feature set (FS-5) on
> held-out `b_ij` error, by a margin larger than seed noise.

* **Metric:** `b_rms_F` on **T1 = `AR_1_Ret_360`** (primary). T2 and T3 reported.
* **PASS** iff `mean_17 + 2·sd_17 < mean_5 − 2·sd_5` on T1 — a clean 2-sigma
  separation in the right direction, over 5 seeds each.
* **GATE REACHED** iff `mean_17 < mean_5` but the 2-sigma bands overlap.
* **GATE FAIL** iff `mean_17 ≥ mean_5` on T1, i.e. the extra 12 features do not
  help or actively hurt.
* **Falsifying outcome, stated in advance:** if FS-17 is not better than FS-5 on a
  held-out square duct, the paper's central mechanism — that `S,R` invariants alone
  cannot describe duct secondary flow because they collapse to a 2-dimensional
  input space (their own explanation, p. 36) — did not transfer to this data, and
  that is the result we ship.
* Paper's corresponding numbers: 0.0995 → 0.0521, a 47.6 % reduction.

### Claim (ii) — beats the Charter-2c SST baseline

> TBRF's a-priori `b_ij` prediction beats the uncorrected k-omega SST `b`
> on the held-out cases.

* **Metric:** `b_rms_F`, FS-17 model, against **B0** (0.5843 / 0.6541 / 0.3051).
* **PASS** iff, on **T1**, `mean_17 + 2·sd_17 < 0.5843` **and** the relative
  reduction `(0.5843 − mean_17)/0.5843 ≥ 0.10`.
* **GATE REACHED** iff it beats 0.5843 by less than 10 % relative, or beats it on
  T1 but not on T2 and T3.
* **GATE FAIL** iff `mean_17 ≥ 0.5843` on T1.
* Additionally required and reported for every verdict: the comparison against
  **B1** and **B2**. Beating B0 while losing to B2 (`b ≡ 0`) would be reported as
  **NOT A RESULT**, because it would mean the "improvement" is only that SST's `b`
  is worse than predicting nothing.
* **Falsifying outcome:** a TBRF that cannot beat a converged industrial closure on
  the metric it was trained to minimise, on a case it has never seen, is a
  documented failure of the method on this data.

### Claim (iii) — realisability without a constraint (F19)

> The unconstrained TBRF prediction stays inside the barycentric triangle.

* **Metric:** violating fraction = fraction of masked-valid test cells whose
  barycentric coordinates (Banerjee et al. 2007 mapping, `of_read.barycentric`) have
  a negative component, i.e. Schumann realisability is violated.
* **Compared against the truth's own violating fraction**, not against zero
  (`BASELINES.md` sec. 5): `AR_1_Ret_360` truth **0.0159**, `AR_1_Ret_180` truth
  **0.0000**, `CBFS13700` truth **0.0000**; SST's own `b` violates in **0.0000** of
  cells on all three.
* **PASS** iff the TBRF violating fraction on T1 is `≤` the truth's own 0.0159 —
  i.e. the model is no less realisable than the labels it was trained on.
* **GATE REACHED** iff it exceeds the truth's fraction but stays below 0.05.
* **GATE FAIL** iff it exceeds 0.05 on T1.
* Reported alongside: the same fraction for FS-5, the maximum negative barycentric
  coordinate, and `mean |trace(b_pred)|` (elementwise median over trees does not
  preserve tracelessness exactly; the size of that artefact is a number we owe).
* **Falsifying outcome:** if the unconstrained TBRF here produces unrealisable `b`
  at a rate above the truth's own, F19's "TBRF never produced unrealisable `b`"
  did not transfer, and we say so.

### Preregistered sensitivity (NOT a tuning knob)

`Γ ∈ {1e-12 (the paper's value — headline), 1e-6, 1e-3}`, FS-17, 3 seeds each for
the two non-paper values. **The headline claims are computed at Γ = 1e-12 only.**
The sensitivity exists because the tensor basis is rank-deficient on 2-D training
data (only `T¹…T⁴` are independent for a 2-D mean flow, Pope 1975), so `Γ` controls
what the six unconstrained directions of `g` do when they are later multiplied by
non-zero `T⁵…T¹⁰` on the 3-D duct. Reporting a better number at a different `Γ` as
the headline would be tuning on the test set and is forbidden by this file.

### Reported diagnostics that carry no claim

* **Extrapolation detection.** Mahalanobis distance of each test cell's FS-17
  feature vector from the training feature cloud (robust median/IQR standardisation,
  training covariance + 1e-6 I). Reported: median and p95 for training-in-sample vs
  each test case, plus the fraction of test cells outside the per-feature training
  `[min, max]` box. This quantifies how far outside its training data the duct
  prediction is; it does not by itself pass or fail anything.
* Feature-survivor list from the variance filter, and which FS1 invariants are
  identically zero on 2-D training data (`trace(S³)` and `trace(R²S)` vanish
  identically for a 2-D incompressible mean flow; whether the filter finds them is
  a check on the implementation).
* Fraction of leaves terminated by the depth cap (D7).
* Wall-distance verification against the shipped `walldist` on the hills (D3).

---

## 5. What a PASS here would and would not mean

**A PASS on (i), (ii) or (iii) is a PASS on the variant claim written above and on
nothing else.** In particular:

* **We cannot claim the paper's 0.0521, 0.0995, or 6.32.** Different duct, different
  Reynolds number, one of three training flows missing, and no BFS case on disk.
  `RESULTS.md` will state this in the verdict line of every claim.
* **Everything here is a-priori** (frozen-field). It says nothing about what the
  predicted `b` does inside the momentum equation. A model that halves `b_rms_F`
  can still diverge, or worsen `U`, when re-solved. No re-solve is attempted; if one
  is added later it must carry a `div(U)` RMS continuity check.
* **Table 4 is BLOCKED-ON-DATA**, not failed. No sharp backward-facing step exists
  in this benchmark.
* **The truth is itself partly unrealisable** — 1.6 % of `AR_1_Ret_360` cells,
  1.2-2.5 % of hill cells. A model trained to regress `b_LES` cannot reach zero
  error against these labels, and its realisability rate must be read against
  theirs.

---

## 6. Compute

Estimate before running: 1600 trees total (2 feature sets × 5 seeds × 100, plus
2 non-paper `Γ` × 3 seeds × 100), 21,000 samples each, 10×10 least-squares
accumulations. FEASIBILITY.md's estimate for this paper is **2-6 core-hours**;
our budget ceiling for this run is set at **60 core-hours**, well inside the
487-core-hour pre-authorisation. `max_depth = 30` (D7) and a hard per-tree sample
count bound the run so that it terminates on its own. Actual core-hours are
reported in `RESULTS.md`.
