# RESULTS — Kaandorp & Dwight 2020 Tensor-Basis Random Forest, labelled VARIANT

**Status: DOCUMENTED FAILURE of the preregistered configuration, with the cause
identified and measured.** All three preregistered claims are **GATE FAIL** on the
primary held-out case. Nothing was retried into a pass: the configuration that
does pass two of the three is reported separately, below, and is labelled
POST-HOC throughout because the decision to run it was taken after seeing the
preregistered result.

* Preregistration: `PREREGISTRATION.md` in this directory, written and posted to
  the supervisor **before** any model was fitted. Acceptance bands, comparators
  and falsifying outcomes were frozen there and are used here verbatim.
* Paper: Kaandorp & Dwight, arXiv:1810.08794v2 (VERIFIED-PDF,
  `docs/papers/closure/Kaandorp2020_random_forests.pdf`).
* Data: Closure Challenge benchmark clone `/home/ubuntu/closure-challenge-benchmark`,
  commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`,
  source `https://github.com/rmcconke/closure-challenge-benchmark.git`,
  sha256 of `git ls-files -s data` =
  `e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401`.
  Read-only. All derived arrays are **outside the repo**, in
  `/home/ubuntu/closure-data/kaandorp_tbrf/`.
* Compute used: **9.69 core-hours** (0.66 wall-hours) for the preregistered run
  and **8.10 core-hours** (0.55 wall-hours) for the post-hoc run of sec. 6 —
  **17.79 core-hours** total, 52 forests x 100 trees. Inside the 60-core-hour
  ceiling this preregistration set and far inside the 487-core-hour
  authorisation. Nothing here needs further compute approval.

---

## 1. Scoreboard

Primary held-out case **T1 = `AR_1_Ret_360`** (square duct, AR 1, `Re_tau` 342,
`Re_b` 5693, 2962 masked-valid cells, a **strict** benchmark test case). Metric
`b_rms_F = sqrt(mean ||b_pred - b_LES||_F^2)`, mean ± sample std over **5 seeds**.

| Claim | Preregistered test | Our number (T1) | Paper's corresponding number | **VERDICT** |
|---|---|---|---|---|
| **(i)** F18 central claim: the full feature set beats `S,R`-only | `mean_full + 2sd < mean_SR - 2sd` | full (16 feat) **6.382 ± 2.110** vs `S,R`-only (5 feat) **3.666 ± 2.299** — the full set is **worse** | 0.0995 (5 feat) -> **0.0521** (17 feat), a 47.6 % reduction | **GATE FAIL** |
| **(ii)** beats the Charter-2c SST `b_rms` | `mean + 2sd < 0.5843` and ≥10 % relative | **6.382 ± 2.110** vs SST **0.5843** — **10.9x worse**. Also loses to the train-mean predictor B1 (0.4718) and to `b ≡ 0` (0.6002) | (paper reports no SST comparator for Table 3) | **GATE FAIL** |
| **(iii)** F19: unconstrained TBRF stays realisable | `≤` the truth's own 0.0159; GATE FAIL above 0.05 | **0.0752 ± 0.0129** of cells outside the barycentric triangle, **4.7x the truth's own rate** | paper: TBRF "never produced unrealisable `b`" with no constraint | **GATE FAIL** |
| **Table 4** BFS5100 reattachment | not attempted | — | RANS 5.45 / TBRF 6.32 / DNS 6.28 / expt 6.0 ± 0.15 | **BLOCKED** (no BFS case on disk; no re-solve attempted) |

**We do not claim the paper's 0.0521, 0.0995 or 6.32, and we did not hit or miss
them.** Different duct, different Reynolds number, one of three training flows
absent. Those numbers appear here only as the context the preregistration froze.

**Every number in this file is A-PRIORI, on frozen fields. Nothing was
re-solved.** Under charter §2 that means **no claim is made here that this closure
improves any flow**, and none is: all three verdicts are GATE FAIL, and a GATE
FAIL needs no re-solve to stand — a model that puts `||b||_F` above the physical
bound `sqrt(2/3)` in 15.0 % of `CBFS13700` cells and 4.1 % of `AR_1_Ret_360` cells
has already disqualified itself from the momentum equation. **Stopping at
a-priori is a scope decision, not a property of the method**, and the reason is
that the a-priori result made the a-posteriori question moot for the
preregistered configuration. The post-hoc configuration of sec. 6 *is* worth
re-solving and is not re-solved here: that is the outstanding work item, ~0.3
core-hours per case, and it must carry an RMS `div(U)` check (charter §7).

---

## 2. The frozen comparators, and every model we ran

`b_rms_F`, mean ± std over seeds. **Bold** = the preregistered headline pair.
Green-field reading: any number above the SST row is a model that lost to the
closure it was meant to replace.

| model (seeds) | `AR_1_Ret_360` **T1** | `AR_1_Ret_180` T2 | `CBFS13700` T3 | `a15_13929_4048` | `a15_13929_2024` | `a05_4071_4048` | `a05_4071_2024` |
|---|---|---|---|---|---|---|---|
| **FS-16 full** (5) | **6.382 ± 2.110** | 6.258 ± 2.065 | 47.680 ± 46.397 | 0.098 ± 0.021 | 0.243 ± 0.068 | 0.193 ± 0.003 | 0.162 ± 0.076 |
| **FS-5 `S,R` only** (5) | **3.666 ± 2.299** | 3.592 ± 2.249 | 4.213 ± 1.949 | 0.145 ± 0.009 | 1.440 ± 2.258 | 0.903 ± 0.425 | 1.579 ± 0.829 |
| FS-5 paper-grown (`min_leaf`=1) (5) | 2.172 ± 1.200 | 2.143 ± 1.181 | 0.911 ± 0.327 | 0.151 ± 0.014 | 0.224 ± 0.004 | 0.333 ± 0.174 | 0.238 ± 0.055 |
| FS-8 (`S,R,∇k`) *exploratory* (5) | 7.262 ± 4.630 | 7.110 ± 4.549 | 4.328 ± 1.181 | 0.154 ± 0.024 | 0.395 ± 0.144 | 0.397 ± 0.152 | 0.436 ± 0.282 |
| FS-16, `Γ`=1e-6 *sensitivity* (3) | 5.720 ± 2.139 | 5.592 ± 2.088 | 1.621 ± 0.456 | 0.089 ± 0.017 | 0.242 ± 0.085 | 0.194 ± 0.002 | 0.204 ± 0.125 |
| FS-16, `Γ`=1e-3 *sensitivity* (3) | 5.788 ± 2.658 | 5.656 ± 2.604 | 0.405 ± 0.043 | 0.132 ± 0.003 | 0.222 ± 0.005 | 0.231 ± 0.004 | 0.246 ± 0.116 |
| **B0 SST (`BASELINES.md`)** | **0.5843** | **0.6541** | **0.3051** | 0.2885 | 0.2989 | 0.3498 | 0.3202 |
| B0 SST, recomputed here | 0.5972 | 0.6624 | 0.3187 | 0.2889 | 0.3339 | 0.3512 | 0.3271 |
| **B1 train-mean `b`** | **0.4718** | **0.5213** | 0.3440 | 0.2279 | 0.2628 | 0.3063 | 0.2589 |
| **B2 `b ≡ 0`** | 0.6002 | 0.6605 | 0.3460 | 0.3129 | 0.3356 | 0.3793 | 0.3466 |
| tensor-basis representation ceiling | 0.0433 | 0.0449 | 0.0048 | 0.0000 | 0.0001 | 0.0000 | 0.0001 |
| rms Frobenius norm of `b_LES` (size of the truth) | 0.6002 | 0.6605 | 0.3460 | 0.3129 | 0.3356 | 0.3793 | 0.3466 |

Notes on this table:

* The two SST rows differ because `BASELINES.md` masks the RANS anisotropy with
  `k_ref = mean|k_RANS|` while this pipeline uses `k_ref = mean|k_LES|` for both
  tensors, so the two keep slightly different cell sets. **The frozen gate is the
  `BASELINES.md` row**, as preregistered, and it is the stricter of the two.
* The **tensor-basis representation ceiling** is the per-cell least-squares
  projection of `b_LES` onto `span{T^(1..10)}`: the smallest `b_rms_F` **any**
  model of Pope's form can reach on that case. On the hills it is 0.0000-0.0001;
  on the ducts it is 0.043-0.045. The basis is not the binding constraint here.
* `B2` and `rms ||b_LES||_F` are the same quantity by construction; both are
  printed because the coincidence is the point — predicting **nothing** scores
  exactly the size of the truth, and every duct model in this table is worse.
* On the four in-distribution control hills, FS-16 **does** beat FS-5 (0.098 vs
  0.145, 0.243 vs 1.440, 0.193 vs 0.903, 0.162 vs 1.579) — but not with 2σ
  separation on any of them, and no claim was preregistered on the controls
  because they are the same flow class at the same `Re` as the training set.

### Feature-set survivors (the paper's own variance < 1e-4 filter, applied verbatim)

25 raw features (FS1 6, FS2 10, FS3 9). **Survivors: FS1 alone = 5** — exactly the
count in the paper's Table 2 for case C3 — **and all sets together = 16**, against
the paper's 17. The one marginal feature is `q9` (ratio of total to normal
Reynolds stresses), variance **3.94e-5** against the 1e-4 cut; including it would
give 17. The nine features the filter removes are `trace(R²SRS²)` and **seven of
the ten FS2 (∇k) invariants**, all of which are identically zero on a 2-D mean
flow. **The ∇k extension contributes only 3 usable invariants when the training
set is 2-D**, which is what our training set — and the paper's — is.

---

## 3. Realisability (claim iii), against the truth's own rate

Fraction of masked-valid cells whose barycentric coordinates (Banerjee et al.
2007 mapping) have a negative component. Tolerance **1e-7**, see sec. 7.

| model | `AR_1_Ret_360` **T1** | `AR_1_Ret_180` | `CBFS13700` | `a15_13929_4048` | `a15_13929_2024` | `a05_4071_4048` | `a05_4071_2024` |
|---|---|---|---|---|---|---|---|
| **FS-16 full** | **0.0752 ± 0.0129** | 0.0938 ± 0.0152 | 0.1924 ± 0.0375 | 0.0109 ± 0.0021 | 0.0180 ± 0.0017 | 0.0140 ± 0.0007 | 0.0210 ± 0.0028 |
| FS-5 `S,R` only | 0.1634 ± 0.0335 | 0.1844 ± 0.0319 | 0.1475 ± 0.0057 | 0.0139 ± 0.0021 | 0.0242 ± 0.0017 | 0.0272 ± 0.0010 | 0.0307 ± 0.0010 |
| FS-5 paper-grown | 0.2778 ± 0.0152 | 0.3050 ± 0.0122 | 0.1034 ± 0.0389 | 0.0135 ± 0.0013 | 0.0284 ± 0.0023 | 0.0134 ± 0.0046 | 0.0307 ± 0.0029 |
| FS-16, `Γ`=1e-3 | 0.2197 ± 0.0159 | 0.2691 ± 0.0112 | 0.0658 ± 0.0143 | 0.0150 ± 0.0027 | 0.0323 ± 0.0012 | 0.0155 ± 0.0053 | 0.0265 ± 0.0026 |
| **TRUTH's own rate** (`BASELINES.md`) | **0.0159** | **0.0000** | **0.0000** | 0.0128 | 0.0230 | 0.0141 | 0.0246 |
| SST's rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

**F19 does not transfer.** The flag records that Kaandorp's TBRF "never produced
unrealisable `b`" with no constraint, while their TBNN did. Here the unconstrained
TBRF is unrealisable in **7.5 % of held-out duct cells and 19.2 % of curved-step
cells**, against a truth that is unrealisable in 1.6 % and 0.0 %. On the four
in-distribution control hills it is 1.1-2.1 % against a truth of 1.3-2.5 %, i.e.
**no worse than the labels** — so the property holds where the model interpolates
and fails where it extrapolates. That distinction is the finding; "TBRF is
realisable" without it is not a property of the algorithm.

A second, harder diagnostic: `||b||_F ≤ sqrt(2/3) = 0.8165` for **any** realisable
state, and the FS-16 model violates that bound in **4.1 %** of `AR_1_Ret_360`
cells and **15.0 %** of `CBFS13700` cells. Predictions there are not merely
outside the triangle, they are unbounded.

**Trace.** The elementwise median over trees does not preserve tracelessness.
Measured `mean |trace(b_pred)|`: 0.004-0.007 on the hills (negligible against
`||b|| ~ 0.3`), but **0.260** on `AR_1_Ret_360` and **2.110** on `CBFS13700` —
another face of the same blow-up, not an aggregation artefact.

---

## 4. Extrapolation statistic

Mahalanobis distance of each test cell's 16-feature vector from the training
feature cloud (robust median/IQR standardisation, training covariance + 1e-6 I,
fitted on the 21,000 training samples only), plus the fraction of test cells
outside the per-feature training `[min, max]` box.

| case | Mahalanobis median | p95 | outside the training box |
|---|---|---|---|
| training sample (in-bag reference) | 3.54 | 6.59 | 0.000 |
| `alpha_15_13929_4048` (control) | 2.74 | 5.69 | 0.000 |
| `alpha_05_4071_4048` (control) | 2.65 | 6.75 | 0.002 |
| `alpha_15_13929_2024` (control) | 3.17 | 6.77 | 0.001 |
| `alpha_05_4071_2024` (control) | 3.43 | 7.04 | 0.002 |
| **`AR_1_Ret_360`** (T1) | 4.38 | **36.00** | **1.000** |
| **`AR_1_Ret_180`** (T2) | 4.54 | **53.29** | **1.000** |
| **`CBFS13700`** (T3) | 5.45 | **159.98** | 0.483 |

**Every single cell of both held-out ducts lies outside the per-feature box of the
training set**, and the Mahalanobis p95 is 5-10x the training p95. The three cases
where the model failed are exactly the three the detector flags, and the four
where it did not fail are exactly the four it does not. A model that reported this
statistic beside its prediction would have refused to answer on the ducts.

---

## 5. Why it failed: the mechanism, measured

Three numbers, in order.

**(a) The Pope basis is rank 3-4, not 10, on every flow in this benchmark.** Mean
numerical rank of the 9x10 matrix `[T^(1) … T^(10)]` at a cell (tol
`1e-8 · max|T|`, 500-cell sample per case): `AR_1_Ret_360` **3.089**,
`AR_1_Ret_180` 3.09, `CBFS13700` 3.988, hills 3.82-3.98. Pope's own result that a
2-D mean flow needs only `T^(1..4)` is confirmed; the ducts are worse, not better,
because their mean flow is 2-D in the cross-plane.

**(b) So six of the ten fitted coefficients are unconstrained, and with the
paper's `Γ` = 1e-12 nothing pins them down.** Over all leaves of a 100-tree FS-16
forest: `median |g| = 2.6e-5`, `p99 |g| = 3.4e4`, `max |g| = 4.0e6`. Nine orders
between median and p99. `Γ` = 1e-12 against normal-equation entries of order 1e4
is `Γ` = 0.

**(c) Those coefficients then multiply basis tensors three decades outside their
training range.** Frobenius norms, p99 over cells:

| | `T^(1)` | `T^(2)` | `T^(6)` | `T^(7)` | `T^(8)` | `T^(9)` |
|---|---|---|---|---|---|---|
| training pool | 34.6 | 1.69e3 | 4.15e4 | **1.02e6** | 1.02e6 | 5.86e5 |
| `AR_1_Ret_360` | 223 | 7.02e4 | 1.11e7 | **1.74e9** | 1.74e9 | 1.01e9 |

**The error is a tail, not a level.** On `CBFS13700` the FS-16 model's error field
has median 0.170, p90 3.40, p99 153.9 and RMS 47.7. **The median cell beats SST's
own `b_rms` of 0.319.** Rescaling only the cells that violate `||b||_F ≤ 0.8165`
back onto that bound — a post-hoc projection carrying no new information — takes
the RMS from 47.68 to **0.567** on CBFS and from 6.38 to **0.411** on
`AR_1_Ret_360`. The preregistered verdict stands on the preregistered metric; this
paragraph says where the metric's mass is.

**Kaandorp's median-over-trees is doing enormous work, and we can price it.** Same
forests, mean over trees instead of median: `AR_1_Ret_360` **67,860** (vs 6.38),
`CBFS13700` **256** (vs 47.7), control hills 48-9,491 (vs 0.10-0.24). Their
sec. 2.5 claim that the median is what makes the TBRF robust is not a stylistic
preference; it is four orders of magnitude, and it is the only thing standing
between this algorithm and complete nonsense on out-of-family data.

---

## 6. POST-HOC — one departure removed, and two of the three claims flip

**This section is not a preregistered verdict and must not be read as one.** The
decision to run it was taken **after** seeing section 1. It is reported because it
identifies the cause, and because the configuration it uses is strictly *closer*
to the paper than the preregistered one.

Departure **D2** bounded the turbulent time scale below by Durbin's
`6 sqrt(ν/ε)`. Kaandorp's eq. (7) uses `T = k/ε` with no bound. D2 was inherited
from `_common/tensor_basis.py` and disclosed in the preregistration with the
stated reason "`k/ε` is unbounded in the low-`k` freestream". **That reason was
wrong.** `k/ε = 1/(0.09 ω)` is bounded wherever `ω` is; it is `6 sqrt(ν/ε)` that
diverges when `k` and `ε` vanish together. Worse, `k/ε` is Reynolds-similar and
`6 sqrt(ν/ε)` is not — it carries `ν` explicitly, so it means something different
on a non-dimensional hill (`H` = 1, `ν` = 1.786e-4) than on a duct meshed in
millimetres (`h` = 1 mm, `ν` = 1.5e-5). Measured: the Durbin branch is active in
**71.8 %** of `AR_1_Ret_360` cells and **46.0 %** of `CBFS13700` cells against
**8.9-11.3 %** of training-hill cells, and it inflates the time scale by up to
**2500x** on the duct.

Rebuilding the features with D2 removed and rerunning the identical pipeline
(same seeds, same splits, same code; feature survivors become **4** for FS1 and
**15** for all sets, since `trace(R²S)` also drops out):

| quantity, on T1 `AR_1_Ret_360` | preregistered (D2 on) | **POST-HOC (D2 off, Kaandorp eq. 7)** | gate |
|---|---|---|---|
| full-feature `b_rms_F` | 6.382 ± 2.110 | **0.3160 ± 0.0080** | SST 0.5843 |
| `S,R`-only `b_rms_F` | 3.666 ± 2.299 | **0.4090 ± 0.0034** | — |
| unrealisable fraction | 0.0752 ± 0.0129 | **0.1339 ± 0.0180** | truth 0.0159 |
| Mahalanobis p95 | 36.00 | **6.20** | training p95 6.59 |
| fraction outside the training box | 1.000 | 1.000 | — |

| claim | POST-HOC outcome (**not** the preregistered verdict) |
|---|---|
| (i) full beats `S,R`-only | 0.3160 + 2(0.0080) = 0.332 < 0.4090 − 2(0.0034) = 0.402 — **would have been PASS**, a 22.7 % reduction against the paper's 47.6 % |
| (ii) beats SST | 0.3160 vs 0.5843 — a **45.9 %** reduction, 2σ separated, and it also beats B1 (0.4718) and B2 (0.6002) — **would have been PASS** |
| (iii) realisability | 0.1339 vs the truth's 0.0159 — **still GATE FAIL**, and worse than the preregistered run |

Two things this says. First, **the preregistered failure of claims (i) and (ii)
is attributable to a disclosed departure and not to the method**: with the paper's
own normalisation the paper's central contrast reproduces in direction, on a
strictly held-out duct at a Reynolds number the paper never saw. Second,
**claim (iii) fails either way, and fails harder once the model is otherwise
working.** F19's realisability property is not a property of the TBRF; it is a
property of a TBRF that has not been asked to extrapolate.

`CBFS13700` stays broken in both configurations (5.770 ± 1.683 post-hoc, against
SST 0.3051) — its Mahalanobis maximum is 990.7 and 48.3 % of its cells are outside
the training box even after the fix.

Post-hoc `Γ` sensitivity, same configuration: `Γ` = 1e-6 gives 0.3361 ± 0.0028 and
`Γ` = 1e-3 gives 0.3662 ± 0.0050 (3 seeds) on T1, so the result is **not** an artefact of the
regulariser; the paper's 1e-12 is the best of the three here.

---

## 7. Verification checks and numerical notes

| check | result |
|---|---|
| **Split disjointness** (asserted in code, run aborts on failure) | case-disjoint OK; **group-disjoint OK** (no (`alpha`, length) hill group in both train and eval); no global cell index shared between the 21,000-sample training draw and any evaluation case. Training pool = **311,597 masked-valid cells over 20 cases** (19 group-clean PHLL29 hills + PHLL10595). This differs from other counts in the case tree because those splits include the ducts and CBFS in training and do not drop the two group siblings. |
| **Velocity gradient (D1)** | `gradU` is not shipped for `DUCT`, `PH_Breuer` or `CBFS`; `of_read.structured_gradient()` supplies it, verified at **0.47-0.96 % relative L2 in the interior** (median cellwise 0.10-0.13 %) against the `gradU` OpenFOAM itself wrote on three hills — `BASELINES.md` sec. 1 |
| **Wall distance (D3)** | computed from `polyMesh` patches of `type wall` (face centres + vertices, KD-tree). Against the shipped `walldist` on the 29 hills: **median cellwise relative error 2e-15 to 1e-14** (machine precision), relative L2 0.055-0.47 %, worst absolute error 0.004-0.049 `H` |
| **Depth cap (D7)** | `max_depth` = 30. Hit **0 times per forest** for FS-16 and 12.4 times for FS-5 (of ~1820 leaves), so the cap is not binding for the headline pair. It **is** binding for the paper-grown FS-5 (`min_leaf`=1): 3724 hits per 100-tree forest of ~13,222 leaves, i.e. 2.8 % of leaves — disclosed as a real departure for that configuration only |
| **Realisability tolerance** | `b_LES` and `T` are stored float32. On `CBFS13700`, **4.60 % of truth cells lie exactly on an edge of the barycentric triangle in float64** (min coordinate exactly 0.0); the float32 round-trip moves them to −2.98e-8 and a zero-tolerance test then reports the *reference data* as unrealisable. All fractions in sec. 3 use **tol = 1e-7**, which clears that floor and is six orders below any meaningful violation. The tolerance changes **no** model number (tol-0 and tol-1e-7 fractions are identical for every prediction); it only restores the truth's CBFS rate to the 0.0000 that `BASELINES.md` computes in float64 |

---

## 8. Sibling comparator — two independent implementations, same failure

A second sub-agent ran an independent TBRF on this machine, with a **different
split, different feature construction and different code** (`run_tbrf.py` in this
directory; outputs in `/home/ubuntu/closure-data/tbrf/`).

**Its numbers and ours are not the same test and must not be read as one column.**
Its training set includes `AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`,
`AR_10_Ret_180` **and** `CBFS13700`. Its `AR_1_Ret_360` result of **0.1157**
(3-seed mean) is therefore **in-family interpolation from four trained ducts to a
fifth**, whereas our 6.382 (preregistered) and 0.3160 (post-hoc) are extrapolation
from hills only to a duct never seen in any form. Both are legitimate; they answer
different questions.

Where the two runs agree is the mechanism, and the agreement is exact:

* **Per-cell tensor-basis rank.** Sibling: mean 3.24 over its whole pool. Ours,
  per case: **3.089-3.988**. Same conclusion — the 10-tensor basis spans 3 to 4
  dimensions on 2-D-dominated mean flows, so `g^(5..10)` are unconstrained by
  training and multiply **non-zero** `T^(5..10)` on 3-D flows.
* **Out-of-family blow-up.** The sibling's only genuinely out-of-family test case
  is the NASA wall-mounted hump, and it gives **136.1 / 282.1 / 173.5** across its
  three seeds (mean 197.3). `NASA_2DWMH` is **not** in our evaluation set at all —
  our preregistration excludes it — so we have no hump number of our own, and any
  hump figure attributed to this reproduction is a mis-attribution. Our equivalent
  out-of-family cases are the two held-out ducts and CBFS, which blow up by the
  same two orders of magnitude.
* Its own realisability falsifier also failed: 10.2-11.4 % non-realisable test
  cells, `||b|| ~ 2e2` on the hump; and its TBNN comparator was worse still
  (6.5-15.3 % non-realisable, `||b|| ~ 1.7e7`). Our claim (iii) was frozen before
  any of this and is unaffected by it.

---

## 9. What this reproduction CANNOT see

* **It cannot reproduce 0.0521, 0.0995 or 6.32.** `SD3500` (the paper's duct),
  `CD12600` (one of its three training flows) and `BFS5100` are not on this
  machine. Our ducts bracket `Re_b` = 3500 from above and below; they are not it.
* **Table 4 is BLOCKED-ON-DATA**, not failed. There is no sharp backward-facing
  step in this benchmark.
* **Everything here is a-priori, on frozen fields. No re-solve was attempted.**
  This says nothing about what the predicted `b` does inside the momentum
  equation — and the a-priori numbers make the a-posteriori question moot for the
  preregistered configuration: 15.0 % of `CBFS13700` cells and 4.1 % of
  `AR_1_Ret_360` cells carry a `b` with `||b||_F > sqrt(2/3)`, which no solver will
  survive. Kaandorp's own stabilisation (`γ_max` = 0.8 continuation, `σ` = 3-cell
  Gaussian smoothing, modified `k`-equation) is **not** exercised here, and the
  fact that they needed all three is the relevant context: F19 records that they
  found `γ_max` = 0.8 by raising `γ` in steps of 0.1 until the solver diverged.
  A re-solve of the post-hoc configuration is the obvious next step and is
  affordable (~0.3 core-hours per case); it must carry a `div(U)` RMS continuity
  check.
* **Which RMSE convention Table 3 uses is not stated in the paper.** Our
  `b_rms_F` is the Frobenius convention of `BASELINES.md`, the only one comparable
  to the SST rows. The per-component convention is `b_rms_F / 3`: our post-hoc T1
  number is 0.3160 Frobenius = **0.1053 per component**, against the paper's
  0.0521. That is a comparison of two different flows and is offered as scale, not
  as a score.
* **The truth is itself partly unrealisable** (1.6 % of `AR_1_Ret_360` cells) and
  carries interpolation error near walls and in the freestream. A model regressing
  `b_LES` cannot reach zero against these labels.
* **No uncertainty estimate accompanies the LES/DNS truth** in the release, so no
  error here can be compared against a data uncertainty band.
* **Five seeds is a small sample for a std**, and the seed spread on the failing
  cases is the same order as the mean (6.382 ± 2.110). The 2σ bands in the
  preregistration are correspondingly wide; claim (i) fails on the *sign* of the
  difference, not on the band.
* **`max_depth` = 30 is ours, not the paper's**, and it binds on 2.8 % of leaves
  in the paper-grown FS-5 configuration only.

---

## 10. Files

Produced by this reproduction (all in this directory unless stated):

| file | what |
|---|---|
| `PREREGISTRATION.md` | frozen before fitting; the verdicts above are scored against it |
| `build_features.py` | FS1/FS2/FS3 assembly, Pope basis, wall distance, splits; `NO_DURBIN=1` builds the post-hoc variant |
| `tbrf_faithful.py` | the TBDT/TBRF implementation (prefix-sum exact split search) |
| `run_experiment.py` | the preregistered run: assertions, baselines, extrapolation statistic, 26 forests |
| `analyse.py` | post-hoc error-distribution and coefficient diagnostics |
| `scoreboard.py` | renders section 1-3 tables from `results.json` |
| `/home/ubuntu/closure-data/kaandorp_tbrf/` | `features.npz`, `features_nodurbin.npz`, `results.json`, `results_nodurbin.json`, `diagnostics.json`, `ckpt/`, `ckpt_nodurbin/`, `train.log`, `train_nodurbin.log`, provenance JSONs |

**Not ours, untouched:** `run_tbrf.py` and `tbrf.py`/`tbrf_original_recovered.py`
(an earlier sub-agent's; see `INCIDENT_tbrf_overwrite_2026-08-20.md` for the
overwrite incident and its resolution).

---

## 11. Departures from the preregistration, appended after the run

**2026-08-20, after the preregistered run completed.** `PREREGISTRATION.md` is
otherwise unchanged; nothing above this line altered a frozen band.

1. **Claim (ii) is additionally judged against B1**, the train-mean `b` predictor.
   The preregistered PASS band names only the SST gate (0.5843). B1 (0.4718) is
   the *stricter* bar on this case, so adding it cannot move the goalposts toward
   a pass. Reported in sec. 1 and sec. 2. The verdict is unchanged: the
   preregistered model loses to SST, to B1 and to `b ≡ 0`.
2. **The `Γ` sensitivity ran 3 seeds, as preregistered**, in both the
   preregistered and the post-hoc configuration. Seed counts are printed with
   every number in this file.
3. **The post-hoc no-Durbin configuration (sec. 6) was not preregistered.** It
   carries no verdict. Its numbers are labelled "would have been" throughout.
4. **Feature counts are 5 and 16, not the paper's 5 and 17.** The preregistration
   said the surviving counts are an output and the models would be named by their
   actual counts; they are.
