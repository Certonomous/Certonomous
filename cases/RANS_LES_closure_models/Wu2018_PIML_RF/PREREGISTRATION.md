# PREREGISTRATION - Wu, Xiao & Paterson (2018) physics-informed random forest

Written **before** any training. Amendments go in `RESULTS.md`.

Date written: 2026-08-20.

## 1. The paper

**Source status: VERIFIED-PDF.** `docs/papers/closure/Wu2018_physics_augmenting.pdf`,
printed title page: *Physics-Informed Machine Learning Approach for Augmenting
Turbulence Models: A Comprehensive Framework*, Jin-Long Wu, Heng Xiao, Eric
Paterson, arXiv:1801.02762v4, 9 Sep 2018 (Phys. Rev. Fluids 3:074602).

Its two stated innovations (abstract, preprint p. 1): "a systematic procedure to
generate mean flow features based on the integrity basis for mean flow tensors",
and "using machine learning to predict linear and nonlinear parts of the Reynolds
stress tensor separately. Inspired by the finite polynomial representation of
tensors in classical turbulence modeling, such a decomposition is instrumental in
overcoming the ill-conditioning of RANS equations."

**Their two demonstrations (preprint pp. 20-22):**

* square duct - train at `Re` = 2200 and 3500 (Pinelli DNS), predict `Re` = 125000
  (Gessner & Emery experiment);
* periodic hills - **train on a steeper hill whose hill width is 0.8 of the test
  hill's** and predict the standard hill at `Re` = 5600 (their Fig. 2, p. 22).

The paper reports its results through profile figures rather than one error table,
so **there is no single scalar headline number to hit**. That is recorded here so
that no number is later invented for it.

The companion paper that states the ill-conditioning claim quantitatively is now
also VERIFIED-PDF on disk: `Wu2018_rans_explicit_closure_ill_conditioned.pdf`,
*RANS Equations with Explicit Data-Driven Reynolds Stress Closure Can Be
Ill-Conditioned*, arXiv:1803.05581v3 (JFM 869:553-586, 2019).

## 2. What is reproduced, and what is a VARIANT

**Their periodic-hill geometry-transfer experiment maps onto our data almost
exactly.** The benchmark's 29 parametric hills differ precisely in hill steepness
(`alpha_05` to `alpha_15`) at fixed `Re_H` = 5600, so "train on one hill shape,
predict another" is a native experiment here rather than a translation. Their
duct `Re`-transfer maps onto `Ret_180 -> Ret_360`.

VARIANT departures, disclosed:

* **Target.** Wu et al. predict the Reynolds-stress discrepancy in the
  eigen-decomposition coordinates (`Delta k`, `Delta xi`, `Delta eta`, and the
  Euler-angle perturbations). We predict the **anisotropy discrepancy directly**,
  `Delta b = b_LES - b_RANS`, six independent components, because that is the
  quantity `sst_baseline_metrics.py` already scores and it makes the result
  directly comparable to the TBNN and TBRF reproductions in the sibling
  directories. This is a real departure and it changes what "realisable" means:
  `b_RANS + Delta b` is not realisable by construction, and the violation rate is
  therefore a reported number, not zero.
* **Features.** The 17 bounded markers of `_common/features_ext.py`, which are
  built in their normalisation style but are not their exact list (they use a
  wall-distance-based Reynolds number; the benchmark does not ship `walldist` on
  the ducts, PH_Breuer or CBFS).
* **No a-posteriori solve in this stage.** Their central claim - that the
  *linear/nonlinear split* is what makes the corrected RANS equations
  well-conditioned - can only be tested by re-solving. OpenFOAM v2606 is
  installed and works here, so that is a scope decision, and it is stated as
  such. Until it is done, **this reproduction cannot test the paper's main claim**,
  only its regression step.

## 3. Two experiments, both pre-registered

**E1 - the benchmark split** (identical to the TBNN and TBRF reproductions, so
all three are comparable): train on 23 cases, validate on 5, test on the 8 strict
TEST cases. Same `assert_disjoint()`.

**E2 - the hill-shape transfer, which is Wu et al.'s own experiment**: train on
the `alpha_10` family only (9 hills, the mid-steepness shape) and test on
`alpha_05` (shallowest) and `alpha_15` (steepest) - the two extremes of the
geometry axis, neither seen. This is the closest analogue on this data to "train
on a hill of width 0.8, predict the standard hill", and it is the more honest
generalisation test of the two.

## 4. Baselines

**B1** k-omega SST's own `b_rms` per case (`BASELINES.md`); **B2** `b = 0`;
**B3** training-mean `Delta b`; **B4** the TBNN and TBRF results from the sibling
directories on the identical E1 split.

## 5. Acceptance band and falsifiers

* **PASS**: E1 test `b_rms` below SST on >= 6 of 8 TEST cases **and** E2 test
  `b_rms` below SST on both held-out hill families.
* **GATE REACHED**: E1 passes but E2 does not - i.e. the method works
  interpolating within a flow family but does not transfer across hill shape,
  which is the transfer Wu et al. claim.
* **GATE FAIL**: E1 beats SST on 4-5 of 8.
* **NOT A RESULT**: fails to beat `b = 0`.
* **Falsifier:** if the random forest's E2 error is *worse* than SST on the
  unseen hill shapes, the paper's geometry-transfer claim does not reproduce on
  this data and that is the finding.

## 6. Seeds, checks, compute

Five seeds (0-4); the forest's bootstrap and feature subsampling are seeded, the
split is not. Reported in every case: realisability violation fraction of
`b_RANS + Delta b` **beside the truth's own** 1.2-2.5% (hills) / up to 1.6%
(ducts) from `BASELINES.md` sec. 5; Mahalanobis distance of test features from
the training distribution; explicit "no velocity field produced, no continuity
check applicable, a-priori only". Estimated **< 0.5 core-hours**; `n_estimators`
capped at 100 and `max_depth` at 20.
