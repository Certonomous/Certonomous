# FS2 degeneracy audit and FS5 extrapolation-coverage check

**Generated** by `make_fs2_report.py` from `fs2_audit.json` and
`invariance_check.json`. Re-running reproduces it. **No model was trained.**

Library: **110 features** on **40 cases**, 641,652 cells, zero non-finite values.
Numerical rank uses SVD of the column-standardised matrix with tolerance `1e-10 * sigma_max`. A feature is DEAD if `max|v| < 1e-12` (absolute test only - see sec. 5).

## 1. Feature-matrix rank per family

| family | cells | rank | deficiency | dead | near-constant | `sigma_1/sigma_N` |
|---|---|---|---|---|---|---|
| `cbfs` | 21,000 | **100** / 110 | 10 | 25 | 2 | 2.00e+18 |
| `duct` | 101,026 | **96** / 110 | 14 | 48 | 2 | 1.17e+33 |
| `hill` | 452,400 | **100** / 110 | 10 | 22 | 2 | 2.18e+17 |
| `hill_breuer` | 15,600 | **100** / 110 | 10 | 30 | 2 | 2.23e+17 |
| `hump` | 51,626 | **100** / 110 | 10 | 44 | 2 | 2.85e+18 |
| `POOLED` | 641,652 | **100** / 110 | 10 | 12 | 2 | 3.28e+17 |

**No family reaches full rank.** The ducts are worst: rank **96 of 110** with **48 algebraically-zero features**, and a condition number of **1.2e+33**. Any method that inverts or regularises this matrix on duct data is working in a space 14 dimensions smaller than it thinks.

## 2. Features that are algebraically zero on ALL data (pooled)

**12 of 110**, listed in full:

* `trW2SWS2__A`  (pooled `max|v|` = 5.204e-18)
* `trW2SPS2__A`  (pooled `max|v|` = 9.500e-18)
* `trW2SKS2__A`  (pooled `max|v|` = 1.464e-18)
* `trP2KS2__A`  (pooled `max|v|` = 2.563e-13)
* `trK2PS2__A`  (pooled `max|v|` = 5.932e-13)
* `trWPSKS2__A`  (pooled `max|v|` = 3.469e-18)
* `trW2SWS2__B`  (pooled `max|v|` = 6.830e-18)
* `trW2SPS2__B`  (pooled `max|v|` = 2.082e-17)
* `trW2SKS2__B`  (pooled `max|v|` = 2.819e-18)
* `trP2KS2__B`  (pooled `max|v|` = 3.241e-13)
* `trK2PS2__B`  (pooled `max|v|` = 5.932e-13)
* `trWPSKS2__B`  (pooled `max|v|` = 6.505e-18)

Every one is a high-order invariant containing a product of three or more of `S`, `Omega`, `A_p`, `A_k`. They vanish because every case in this benchmark is a statistically two-dimensional mean flow - the same collapse that takes Pope's ten-tensor basis to rank 3 (sec. 4).

### Dead per family (a feature can be dead on one family and live on another)

| family | dead count |
|---|---|
| `cbfs` | 25 |
| `duct` | 48 |
| `hill` | 22 |
| `hill_breuer` | 30 |
| `hump` | 44 |

## 3. Invariance check (charter section 6)

Case `CBFS13700`, 21,000 cells. A Galilean boost `c = [0.3057, -0.1735, 0.1074]` and a rigid rotation of 0.7 rad applied to the raw fields; every feature and every normaliser recomputed. Tolerance `1e-12`.

* **Rotation: max relative change 6.939e-06.** 3 features exceed tolerance and all three are artefacts, not failures: `trW2SWS2__A/B` are algebraically zero (`max|v|` ~ 3e-18, sec. 2) so the relative measure divides roundoff by zero, and `q8_kConvection` sits at 3.3e-12 for an O(1) feature. **All 110 features are rotation invariant to roundoff.**
* **Galilean boost: max relative change 2.000e+00. 58 of 110 features are NOT Galilean invariant.**

They fall into exactly two groups, and the split is the finding:

**(a) 53 tensor invariants, every one of which contains `A_p`** - the antisymmetric tensor built from the pressure gradient. Wu, Xiao & Paterson normalise `grad p` by `rho |DU/Dt|` (their Table 1, preprint p. 8) and argue in Appendix C that the set is Galilean invariant. That argument holds for the **unsteady** material derivative `DU/Dt = dU/dt + U.grad U`, where the unsteady term supplies the compensating shift. **A steady RANS field has no `dU/dt`**, so the implementable normaliser is `|U.grad U|`, which is not boost-invariant - and neither is any invariant built on it. This is a property of steady-state implementation, not an error in the paper.

**(b) 5 scalar features that use the raw velocity `U`:** `q10_streamlineCurv`, `q2_turbIntensity`, `q4_pgradAlongStreamline`, `q8_kConvection`, `q9_nonOrthogonality`.

Full per-feature numbers are in `invariance_check.json`.

## 4. Tensor-basis per-cell rank (charter section 5(b))

numerical rank of the 10x9 flattened tensor stack per cell, singular values above 1e-8*sigma_max; up to 4000 cells per case, seed 0.

* **Case means run 3.006 to 3.987**; mean of case means **3.738**.
* **Maximum rank reached in any cell of any case: 5.**

**Provenance.** The charter (section 5(b)) records that a figure of "3.24 on average, never above 5" is quoted in three records from a pointer that does not resolve, and rules that it must not be quoted until it has a live source. **This table is that source.** It is a fresh measurement from `/home/ubuntu/closure-data/tbnn/dataset.npz` and it does not reproduce 3.24 as a *case-mean* statistic: the case means average **3.738**. 3.24 was a *pooled-sample* number over randomly drawn training cells, which the duct cases - the lowest-rank family, at 3.018 - pull down. Both are computable; they are different statistics and should not be quoted interchangeably. The bound that matters is unchanged and is confirmed here: **never above 5, against a nominal basis size of 10.**

| case | mean per-cell rank | min | max |
|---|---|---|---|
| `AR_1_Ret_180` | 3.006 | 3 | 4 |
| `AR_1_Ret_360` | 3.018 | 3 | 4 |
| `AR_5_Ret_180` | 3.020 | 3 | 5 |
| `AR_3_Ret_360` | 3.023 | 3 | 5 |
| `AR_3_Ret_180` | 3.024 | 3 | 5 |
| `AR_14_Ret_180` | 3.025 | 3 | 5 |
| `AR_7_Ret_180` | 3.027 | 3 | 4 |
| `AR_10_Ret_180` | 3.030 | 3 | 5 |
| `alpha_05_4071_4048` | 3.791 | 3 | 4 |
| `alpha_05_4071_3036` | 3.803 | 3 | 4 |
| `NASA_2DWMH` | 3.865 | 2 | 4 |
| `alpha_10_6000_4048` | 3.884 | 3 | 4 |
| `alpha_15_13929_2024` | 3.892 | 3 | 4 |
| `alpha_05_10071_2024` | 3.898 | 3 | 4 |
| `alpha_10_6000_3036` | 3.900 | 3 | 4 |
| `alpha_10_12000_2024` | 3.901 | 3 | 4 |
| `alpha_05_4071_2024` | 3.901 | 3 | 4 |
| `alpha_15_7929_2024` | 3.907 | 3 | 4 |
| `alpha_15_10929_2024` | 3.912 | 3 | 4 |
| `alpha_10_6000_2024` | 3.914 | 3 | 4 |
| `alpha_05_7071_2024` | 3.916 | 3 | 4 |
| `alpha_15_7929_3036` | 3.918 | 3 | 4 |
| `alpha_10_9000_2024` | 3.919 | 3 | 4 |
| `alpha_05_7071_3036` | 3.922 | 3 | 4 |
| `alpha_15_7929_4048` | 3.922 | 3 | 4 |
| `alpha_075` | 3.924 | 3 | 4 |
| `alpha_05_7071_4048` | 3.925 | 3 | 4 |
| `alpha_125` | 3.927 | 3 | 4 |
| `alpha_10_9000_3036` | 3.930 | 3 | 4 |
| `alpha_10_9000_4048` | 3.933 | 3 | 4 |
| `alpha_15_13929_3036` | 3.937 | 3 | 4 |
| `alpha_05_10071_3036` | 3.939 | 3 | 4 |
| `alpha_15_10929_3036` | 3.942 | 3 | 4 |
| `alpha_10_12000_3036` | 3.944 | 3 | 4 |
| `alpha_15_10929_4048` | 3.946 | 3 | 4 |
| `alpha_15_13929_4048` | 3.955 | 3 | 4 |
| `alpha_05_10071_4048` | 3.956 | 3 | 4 |
| `alpha_10_12000_4048` | 3.957 | 3 | 4 |
| `PHLL10595` | 3.967 | 3 | 4 |
| `CBFS13700` | 3.987 | 3 | 4 |

## 5. A criterion that had to be corrected, recorded

The first version of this audit flagged a feature DEAD if `max|v|` fell below either an absolute threshold **or** `1e-12` times the largest value *anywhere in the matrix*. That relative test is meaningless on an incommensurable library: the Pope invariants under the Durbin-bounded normalisation reach `|lam3| = 1.5e11` and `|lam5| = 1.5e14`, so the relative threshold became **150** and every bounded feature - all eleven `q` markers, every normalised invariant - was reported dead. The test is now **absolute only**. Recorded because the wrong version produced a confident, plausible, entirely false answer.

That the Pope invariants span fourteen orders of magnitude is itself an FS2 finding: they are the only unbounded block in the library, and they will dominate any unstandardised distance metric built on it.

## 6. FS5 extrapolation coverage: TEST cases against the TRAINING range

Training range is the per-feature min/max over the 32 non-TEST cases. A test cell is 'outside' if any feature falls beyond that range.

| TEST case | cells | cells outside on >=1 feature | features ever outside |
|---|---|---|---|
| `alpha_15_13929_4048` | 15,600 | **0.00%** | 0 / 110 |
| `alpha_15_13929_2024` | 15,600 | **0.01%** | 1 / 110 |
| `alpha_05_4071_2024` | 15,600 | **0.06%** | 6 / 110 |
| `alpha_05_4071_4048` | 15,600 | **0.06%** | 4 / 110 |
| `AR_14_Ret_180` | 31,819 | **0.96%** | 18 / 110 |
| `AR_3_Ret_360` | 8,748 | **2.77%** | 22 / 110 |
| `AR_1_Ret_360` | 3,025 | **3.07%** | 16 / 110 |
| `NASA_2DWMH` | 51,626 | **31.79%** | 49 / 110 |

**`NASA_2DWMH` is out of family by this instrument too**: **31.79%** of its cells fall outside the training range on at least one feature, and **49 of 110** features go out of range somewhere on it. The four hills sit at 0.00-0.06% and the three ducts at 0.96-3.07%. This is a third independent instrument agreeing with the Mahalanobis statistic (13.17% of hump cells beyond the training p99) and with the measured hump blow-up of every tensor-basis model.

### Worst features on the hump, by fraction of cells out of range

| feature | cells outside | worst excursion (training spans) |
|---|---|---|
| `I1_trS2__A` | 20.37% | 0.26 |
| `trW2S2__A` | 20.37% | 0.26 |
| `q3_timeScaleRatio` | 20.37% | 0.12 |
| `q11_turbReynolds` | 16.17% | 0.03 |
| `trK2S2__A` | 14.28% | 1.59 |
| `trK2SWS2__A` | 11.28% | 0.74 |
| `trK2WS__A` | 10.22% | 0.41 |
| `trWKPS__A` | 9.82% | 0.16 |
| `trWPKS__A` | 9.67% | 0.13 |
| `q7_viscRatio` | 8.82% | 0.13 |
| `lam3` | 8.82% | 4933718.23 |
| `I5_trK2__A` | 7.60% | 0.06 |

## 7. What this audit cannot see

* **It is a degeneracy and coverage audit, not a selection.** Nothing is ranked by usefulness and nothing is removed. FS3 does that.
* **Rank is measured on the standardised matrix**, so it answers "how many independent directions" and not "how well conditioned for a particular regressor".
* **The invariance check ran on one case** (`CBFS13700`). The conclusions are algebraic and should hold everywhere, but they are measured on one field.
* **Dead-on-this-benchmark is not dead in general.** The twelve pooled-dead invariants vanish because these flows are two-dimensional; a three-dimensional case would revive them, and that is precisely why a model fitted here cannot be trusted there.

