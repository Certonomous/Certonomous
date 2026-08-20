# RESULTS - Wu, Xiao & Paterson (2018) physics-informed random forest, VARIANT

Preregistration: `PREREGISTRATION.md`, written before any training and unchanged.
Code: `run_rf.py`. Raw log: `train_log.json`. Predictions and forests live outside
the repo in `/home/ubuntu/closure-data/`.

## VERDICT: **PASS**, with one case failing and one claim untested

**PASS** on the pre-registered band: E1 beats k-omega SST on **7 of 8** strict
TEST cases (band required >= 6), and E2 - the hill-shape transfer that is Wu et
al.'s own experiment - beats SST on **18 of 18** held-out hills, both families.

Two things the verdict does **not** cover, stated here rather than in a footnote:

1. **The one case it loses is the NASA wall-mounted hump**, where the forest is
   *worse than SST* and worse than predicting zero anisotropy. That is not noise:
   it is the only test case whose features lie far outside the training
   distribution, and the extrapolation statistic pre-registered in sec. 6 says so
   quantitatively (below).
2. **This is an a-priori result.** No velocity field was produced and nothing was
   re-solved. Wu et al.'s central claim - that splitting the linear from the
   nonlinear part of `tau` is "instrumental in overcoming the ill-conditioning of
   RANS equations" (abstract) - **is not tested here at all**, because testing it
   requires a solve. OpenFOAM v2606 is installed at
   `/usr/lib/openfoam/openfoam2606` and `simpleFoam` runs on this machine, so
   this is a scope decision, not a capability limit.

## 1. Provenance

| Item | Value |
|---|---|
| paper | `docs/papers/closure/Wu2018_physics_augmenting.pdf`, **VERIFIED-PDF**, arXiv:1801.02762v4 (Phys. Rev. Fluids 3:074602, 2018) |
| data | Closure Challenge benchmark, `https://github.com/rmcconke/closure-challenge-benchmark.git`, commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`; local clone `/home/ubuntu/closure-challenge-benchmark` (outside the repo); `sha256` of `git ls-files -s data` = `e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401` |
| derived arrays | `/home/ubuntu/closure-data/tbnn/dataset.npz`, `/home/ubuntu/closure-data/tbnn/features_ext.npz` (built by `_common/build_dataset.py`, `_common/build_features_ext.py`) |
| model | `sklearn.ensemble.RandomForestRegressor`, 100 trees, `max_depth` 20, `min_samples_leaf` 9, `max_features="sqrt"` |
| target | `Delta b = b_LES - b_RANS`, 6 independent components |
| inputs | the 17 bounded markers of `_common/features_ext.py` |
| seeds | 0, 1, 2, 3, 4 |
| wall clock | 245.4 s for both experiments x 5 seeds, i.e. **~0.3 core-hours** on 4 threads |

## 2. Disjointness assertion, printed verbatim from the run

```
[assert] case sets pairwise disjoint: train=23 val=5 test=8
[assert] (alpha,length) groups disjoint: train=13 val=3 test=6; no group appears on both sides
[assert] cells are never split across cases: every case contributes all of its cells to exactly one of train/val/test
[assert] E2 train=9 alpha_10 hills; test=9 alpha_05 + 9 alpha_15; disjoint by construction
```

Cells: train 342,014, validation 77,611, test 152,634 (of 641,652 with truth).
A further **567 cells** were dropped as non-finite: `b_RANS` is undefined where
the converged RANS `k` falls below the anisotropy floor even though `k_LES` does
not. That count is in `train_log.json` as `n_dropped_nonfinite`; it is 0.09% of
the valid set.

## 3. E1 - the benchmark split. Mean over 5 seeds, RMS of `||b_pred - b_LES||_F`

| Case | cells | RF (5-seed mean) | seed spread | k-omega SST | `b = 0` | beats SST? |
|---|---|---|---|---|---|---|
| `AR_14_Ret_180` | 31624 | **0.0667** | 0.0007 | 0.5799 | 0.5842 | **yes** |
| `AR_1_Ret_360` | 2955 | **0.1276** | 0.0011 | 0.5972 | 0.5996 | **yes** |
| `AR_3_Ret_360` | 8644 | **0.1157** | 0.0020 | 0.5523 | 0.5580 | **yes** |
| `NASA_2DWMH` | 47102 | **0.3540** | 0.0031 | 0.3318 | 0.3398 | **NO** |
| `alpha_05_4071_2024` | 15503 | **0.1231** | 0.0011 | 0.3271 | 0.3457 | **yes** |
| `alpha_05_4071_4048` | 15543 | **0.1873** | 0.0005 | 0.3512 | 0.3791 | **yes** |
| `alpha_15_13929_2024` | 15573 | **0.1672** | 0.0022 | 0.3339 | 0.3355 | **yes** |
| `alpha_15_13929_4048` | 15576 | **0.0625** | 0.0004 | 0.2889 | 0.3128 | **yes** |
Pooled over all 152,520 scored TEST cells: **RF 0.2213-0.2225** (5 seeds) against
**SST 0.4138** and **`b = 0` 0.4234**.

The seed spread is **0.0004 to 0.0031** per case - two orders of magnitude smaller
than every margin above except the NASA hump's, where the margin over SST is
-0.022 and the spread is 0.003, so the loss on that case is also real and not
seed noise.

### 3.1 The pre-registered B3 baseline, and how low the bar is

Baseline **B3** is the mean `b_LES` over all 342,014 training cells - a *single
constant tensor*, no inputs. On the 8 TEST cases it scores:

| Case | B3 (constant) | k-omega SST | RF |
|---|---|---|---|
| `AR_14_Ret_180` | 0.4036 | 0.5799 | see above |
| `AR_1_Ret_360` | 0.4221 | 0.5972 | see above |
| `AR_3_Ret_360` | 0.3866 | 0.5523 | see above |
| `NASA_2DWMH` | 0.2949 | 0.3318 | see above |
| `alpha_05_4071_2024` | 0.2586 | 0.3271 | see above |
| `alpha_05_4071_4048` | 0.3014 | 0.3512 | see above |
| `alpha_15_13929_2024` | 0.2714 | 0.3339 | see above |
| `alpha_15_13929_4048` | 0.2258 | 0.2889 | see above |

**B3 beats k-omega SST on all 8 cases.** Predicting one constant anisotropy
everywhere is a better a-priori anisotropy model than the shipped linear
eddy-viscosity closure. The random forest beats B3 on **7 of 8** - the same 7 -
so criterion (ii) of the band is met, but the margin that matters is the one over
B3, not the one over SST. Any closure paper that reports only "we beat the RANS
baseline on `b`" has cleared a bar a constant clears.

**The SST column here is not the SST column in `BASELINES.md`.** It is recomputed
on the identical cell mask by `_common/baseline_on_mask.py`, because this
reproduction drops the 567 non-finite cells that `BASELINES.md` keeps. The
differences are small (e.g. `AR_14_Ret_180` 0.5799 here against 0.5767 there) but
they are differences, and comparing across masks would be wrong.

## 4. E2 - hill-shape transfer, Wu et al.'s own experiment

Train on the nine `alpha_10` hills only; test on all nine `alpha_05` (shallowest)
and all nine `alpha_15` (steepest). Neither shape is seen in training.

| Case | cells | RF (5-seed mean) | seed spread | k-omega SST | `b = 0` |
|---|---|---|---|---|---|
| `alpha_05_10071_2024` | 15551 | **0.0994** | 0.0008 | 0.2839 | 0.2979 |
| `alpha_05_10071_3036` | 15574 | **0.1282** | 0.0006 | 0.3038 | 0.3224 |
| `alpha_05_10071_4048` | 15566 | **0.1078** | 0.0006 | 0.2858 | 0.3119 |
| `alpha_05_4071_2024` | 15503 | **0.1389** | 0.0007 | 0.3271 | 0.3457 |
| `alpha_05_4071_3036` | 15544 | **0.1223** | 0.0009 | 0.3235 | 0.3498 |
| `alpha_05_4071_4048` | 15543 | **0.1935** | 0.0004 | 0.3512 | 0.3791 |
| `alpha_05_7071_2024` | 15527 | **0.0976** | 0.0006 | 0.2824 | 0.2999 |
| `alpha_05_7071_3036` | 15558 | **0.2691** | 0.0006 | 0.3867 | 0.4040 |
| `alpha_05_7071_4048` | 15558 | **0.0772** | 0.0004 | 0.2764 | 0.3056 |
| `alpha_15_10929_2024` | 15555 | **0.1324** | 0.0004 | 0.3160 | 0.3199 |
| `alpha_15_10929_3036` | 15574 | **0.1295** | 0.0009 | 0.3139 | 0.3288 |
| `alpha_15_10929_4048` | 15570 | **0.1006** | 0.0014 | 0.2928 | 0.3179 |
| `alpha_15_13929_2024` | 15573 | **0.1707** | 0.0015 | 0.3339 | 0.3355 |
| `alpha_15_13929_3036` | 15577 | **0.0865** | 0.0010 | 0.2991 | 0.3122 |
| `alpha_15_13929_4048` | 15576 | **0.0700** | 0.0006 | 0.2889 | 0.3128 |
| `alpha_15_7929_2024` | 15526 | **0.0941** | 0.0004 | 0.2922 | 0.2995 |
| `alpha_15_7929_3036` | 15568 | **0.0580** | 0.0004 | 0.2923 | 0.3101 |
| `alpha_15_7929_4048` | 15561 | **0.1053** | 0.0009 | 0.3015 | 0.3270 |
**18 of 18 beat SST**, by factors of 1.4x to 5.0x. Pooled: **RF 0.1303-0.1306**
against **SST 0.3096** on the same cells. The geometry-transfer claim reproduces on
this data.

The worst case is `alpha_05_7071_3036` (RF 0.2689 vs SST 0.3867) - still better
than SST, but the only one above 0.2.

## 5. Realisability of the predicted anisotropy

Reported beside the truth's own violation rate, as `BASELINES.md` sec. 5 requires,
never beside zero. `b_pred = b_RANS + Delta b_RF` is **not** realisable by
construction - that is a real cost of predicting a discrepancy rather than
predicting `b` inside a tensor basis.

| Experiment | fraction of test cells with `b_pred` outside the barycentric triangle | the **truth's** own violation fraction on the same cells | SST's |
|---|---|---|---|
| E1 (8 TEST cases) | **1.54-1.60%** | **0.79%** | 0.10% (cell-weighted; all of it on the hump) |
| E2 (18 held-out hills) | **1.05-1.07%** | **1.64%** | 0.00% |

Reading: on E1 the forest roughly doubles the violation rate relative to the
truth's own; on E2 it is **below** the truth's own rate. Neither is zero and
neither can be, since the target itself is unrealisable in 0.8-1.6% of cells.

## 6. Extrapolation statistic (pre-registered, sec. 6)

Mahalanobis distance of each test cell's 17 features from the training feature
distribution, against the training set's own 99th percentile.

| Experiment | train p99 | test median | test p99 | fraction of test cells beyond train p99 |
|---|---|---|---|---|
| E1 | 9.05 | 3.39 | **32,362.6** | **5.0%** |
| E2 | 9.14 | 2.99 | 10.20 | **1.3%** |

**This is the whole story of the NASA hump.** E2's test cells are, by this
measure, inside the training distribution (p99 of 10.2 against a training p99 of
9.1) and E2 wins everywhere. E1's test p99 is **3,500x** the training p99, driven
by the hump's stagnation region and freestream, and E1 loses exactly there. The
statistic was pre-registered before the run and it predicts the one failure
without being fitted to it.

## 7. Feature importance (E1, seed 0)

| Feature | importance |
|---|---|
| `q_nonorthogonality` | 0.144 |
| `q_turb_reynolds` | 0.132 |
| `q_streamline_curv` | 0.128 |
| `q_turb_intensity` | 0.102 |
| `q_visc_ratio` | 0.086 |
| `lam5` = `tr(r^2 s^2)` | 0.068 |

The five Pope invariants together account for less than a fifth of the total
importance; the bounded flow markers carry the rest. That is consistent with
Kaandorp & Dwight's finding that "the introduction of extra features has
significantly more effect than the choice of neural-networks versus
random-forests" (VERIFIED-PDF: arXiv:1810.08794v2, p. 36) - though here it is a
different feature list and a different flow set, so it is corroboration, not a
reproduction of their number.

## 8. Departures from the paper, all disclosed in the preregistration

* **D1.** Target is `Delta b` directly, not the eigen-decomposition perturbations
  (`Delta k`, `Delta xi`, `Delta eta`, Euler angles) that Wu et al. use. This is
  why realisability is not automatic here and is why sec. 5 exists.
* **D2.** Features are our own 17-marker set, not their integrity-basis list; no
  wall-distance feature, because the benchmark ships `walldist` only on the hills
  and the hump.
* **D3.** Different flows, different Reynolds numbers, different high-fidelity
  sources from theirs. **The paper reports no single scalar headline number**, so
  there is nothing here that could be mistaken for hitting or missing their
  value; the comparison is method-level.
* **D4.** No linear/nonlinear split, because that split only does work inside a
  solve, and no solve was run.

## 9. What this result cannot see

* **It cannot see whether any of this survives being re-solved.** The map from
  `b` to `U` runs through the momentum balance and is not monotone; a model that
  cuts the anisotropy error by 2-5x can still produce a worse velocity field or
  fail to converge. That is precisely the failure documented in
  `docs/papers/closure/Wu2018_rans_explicit_closure_ill_conditioned.pdf`
  (**VERIFIED-PDF**, arXiv:1803.05581v3, JFM 869:553-586, 2019). Until Stage C of
  a propagation study is run, the number 0.2213 is an a-priori regression score
  and nothing more.
* **No continuity check is applicable**: no velocity field is produced.
* **It cannot see the truth's own uncertainty.** The benchmark release carries no
  error bar on the interpolated LES/DNS, so none of these margins can be compared
  against a data uncertainty band. The truth is itself unrealisable in 0.8-1.6%
  of cells.
* **It cannot see 3-D effects.** Every benchmark case is a statistically 2-D mean
  flow; the per-cell rank of Pope's 10-tensor basis on this data is **3.24 on
  average, never above 5** (measured, `Kaandorp2020_TBRF/train_log.json`). Any
  conclusion here about "which features matter" is a conclusion about 2-D flows.
* **`alpha_05_7071_*` appears in E1's training set and in E2's test set.** The two
  experiments are internally disjoint but are not independent of each other; E2's
  numbers must not be read as a second confirmation of E1's.
