# RESULTS - a-posteriori re-solve of the Wu 2018 PIML random forest

Preregistration: `PREREGISTRATION.md`, frozen before any solve, plus a dated
post-freeze **ADDENDUM** (G0a, G0b, NULL as fifth configuration, the 30% cross-lane
ceiling reading, the realisability tolerance, and the CBFS in-sample caveat).
Nothing in the frozen text was edited.

## VERDICT: **NOT A RESULT** — the ceiling gate failed on all three cases, and the ML rows are void by the pre-registered falsifier 3

Injecting the **true** anisotropy `b_LES - b_RANS` makes the velocity field
**worse**, on every case:

| Case | shipped BASE `U_rms` | NULL `U_rms` | **TRUTH `U_rms`** | registered ceiling (>= 50% cut) |
|---|---|---|---|---|
| `AR_1_Ret_360` | 0.1985 | 0.1987 | **0.3215** | **FAILED** — 62% *worse*, not 50% better |
| `AR_3_Ret_360` | 0.1846 | 0.1865 | **0.2898** | **FAILED** — 57% worse |
| `CBFS13700` | 0.0516 | 0.0516 | **0.0843** | **FAILED** — 63% worse |

Pre-registration sec. 3.1 registered that a TRUTH row failing to cut `U_rms` by
50% makes that case **NOT A RESULT**, and falsifier 3 registered that a TRUTH row
*worse* than BASE voids every ML row for that case. Both fired, on all three
cases, so **no verdict is taken on H1, H2 or H3 and the ML numbers below carry no
claim.** They are printed because they were run, not because they mean anything.

**This is not a failure of the test; it is the test working.** The ceiling
configuration exists precisely to catch an injection path that cannot express the
correction, and it caught one before a single ML number was interpreted.

### Why: `b^Delta` is frozen but `k` is transported, and with `kDeficit = 0` the `k` budget collapses

The model realises `tau = 2k(b_linear + b^Delta)` with `k` from the **current**
iterate. The `k`-equation production is `P_k = -2k(b_linear + b^Delta):grad(U)`,
so injecting `b^Delta` changes production with nothing to balance it. Measured:

| Case | `k` mean, baseline SST | `k` mean, TRUTH run | ratio | vs `k_LES` |
|---|---|---|---|---|
| `AR_1_Ret_360` | 26.68 | **8.74** | **0.33** | 0.20 |
| `CBFS13700` | 0.00302 | 0.00275 | 0.91 | 0.68 |

On the duct, transported `k` collapses to **a third** of baseline and **a fifth**
of the true `k_LES`. Even a perfect `b^Delta` then yields a Reynolds stress
scaled by that factor, so the momentum balance is wrong regardless of how good
the anisotropy is.

**The anisotropy itself is excellent** — that is what makes this clean.
`b_rms` against the LES falls from **0.5833** (NULL) to **0.0251** (TRUTH) on
`AR_1_Ret_360`, and the duct secondary flow that a linear model cannot produce
at all appears: **0.0000% -> 0.3645%** of bulk against a DNS 1.508%, i.e. 24% of
the true magnitude recovered from a structural zero. The injection path does
exactly what it claims to the *anisotropy*; it is the *velocity* that degrades.

**Cross-check that isolates the cause.** The same solver, the same injection
path, with **both** corrections (`b^Delta` **and** `R`) reaches
`eps(U)/eps(U_0)` = **0.0017** on PH10595 in the lab's own W2 campaign
(`verification/campaign/W2_SPARTA_FROZEN_CBFS.md`). The path is sound. What
fails is the **`b`-only** configuration — which is the configuration a model that
predicts only `b_ij` can supply. Schmelzer et al. carry `R` for this reason;
this lane registered `kDeficit = 0` because the forest predicts no `k`
correction, and that decision is what the ceiling gate exposed.

### What this says about the a-priori PASS

The a-priori study cut `b_rms` from 0.4138 to 0.2213 and passed. Here the same
forest, injected, cuts `b_rms` far further (to 0.0424-0.1324) and **raises**
`U_rms` by 57-63%. **An a-priori anisotropy score bounds nothing about the solved
velocity field** — which is exactly the claim of
`Wu2018_rans_explicit_closure_ill_conditioned.pdf` (arXiv:1803.05581v3), verified
on disk, and it is now measured on this lab's own data.

## 4. Results


### AR_1_Ret_360 — n = 3,025 cells, DNS secondary flow **1.508%** of bulk

**Comparators.** Shipped **BASE** `U_rms` = **0.1985** (`U_mae` 0.1263). **NULL** = STAGNATED-NOT-CONVERGED at 94,846 iterations, final initial residuals `Ux`=7.36e-16, `Uy`=3.33e-01, `Uz`=2.61e-01, `p`=1.53e-01, `k`=9.58e-09, `omega`=9.77e-16. **NULL − BASE = +0.0002** (the benchmark's own convergence gap, N-B23).

| cfg | `U_rms` | `U_mae` | sec% of bulk | `k`/`k`base | `b_rms` vs LES | viol | continuity | max resid | iters | converged? |
|---|---|---|---|---|---|---|---|---|---|---|
| `null` | **0.1987** | 0.1411 | 0.0000 | 1.001 | 0.5833 | 0.0000 | 3.9e-13 | 3.3e-01 | 94,846 | **no** |
| `truth` | **0.3215** | 0.2558 | 0.3645 | 0.328 | 0.0251 | 0.0116 | 1.6e-04 | 9.7e-07 | 528 | yes |
| `mean` | **0.6724** | 0.5354 | 0.1136 | 0.007 | 0.3522 | 0.0000 | 6.8e-06 | 1.0e-06 | 1,427 | yes |
| `ml_s0` | **0.4659** | 0.3511 | 0.3297 | 0.319 | 0.1297 | 0.0005 | 1.8e-04 | 9.9e-07 | 523 | yes |
| `ml_s1` | **0.4723** | 0.3551 | 0.3559 | 0.320 | 0.1315 | 0.0000 | 8.9e-05 | 9.8e-07 | 527 | yes |
| `ml_s2` | **0.4756** | 0.3571 | 0.3386 | 0.313 | 0.1324 | 0.0000 | 1.6e-04 | 9.4e-07 | 522 | yes |

### AR_3_Ret_360 — n = 8,748 cells, DNS secondary flow **1.411%** of bulk

**Comparators.** Shipped **BASE** `U_rms` = **0.1846** (`U_mae` 0.1251). **NULL** = STAGNATED-NOT-CONVERGED at 33,436 iterations, final initial residuals `Ux`=1.71e-12, `Uy`=5.02e-01, `Uz`=4.89e-01, `p`=3.22e-01, `k`=9.89e-09, `omega`=9.30e-16. **NULL − BASE = +0.0019** (the benchmark's own convergence gap, N-B23).

| cfg | `U_rms` | `U_mae` | sec% of bulk | `k`/`k`base | `b_rms` vs LES | viol | continuity | max resid | iters | converged? |
|---|---|---|---|---|---|---|---|---|---|---|
| `null` | **0.1865** | 0.1412 | 0.0000 | 1.001 | 0.5427 | 0.0000 | 6.0e-13 | 5.0e-01 | 33,436 | **no** |
| `truth` | **0.2898** | 0.2421 | 0.3084 | 0.359 | 0.0261 | 0.0020 | 1.2e-05 | 9.9e-07 | 3,053 | yes |
| `mean` | **0.5229** | 0.4360 | 0.6832 | 0.107 | 0.3943 | 0.0003 | 3.1e-05 | 1.0e-06 | 19,904 | yes |
| `ml_s0` | **0.3865** | 0.3040 | 0.3389 | 0.314 | 0.1141 | 0.0000 | 3.1e-05 | 9.9e-07 | 2,063 | yes |
| `ml_s1` | **0.3818** | 0.3017 | 0.3479 | 0.317 | 0.1146 | 0.0000 | 4.2e-05 | 9.9e-07 | 2,049 | yes |
| `ml_s2` | **0.3834** | 0.3026 | 0.3493 | 0.313 | 0.1165 | 0.0000 | 3.7e-05 | 9.9e-07 | 2,050 | yes |

### CBFS13700 — n = 21,000 cells

**Comparators.** Shipped **BASE** `U_rms` = **0.0516** (`U_mae` 0.0258). **NULL** = CONVERGED at 984 iterations, final initial residuals `Ux`=3.13e-08, `Uy`=9.89e-08, `p`=1.15e-08, `k`=9.30e-07, `omega`=9.82e-09. **NULL − BASE = -0.0000** (the benchmark's own convergence gap, N-B23).

| cfg | `U_rms` | `U_mae` | sec% of bulk | `k`/`k`base | `b_rms` vs LES | viol | continuity | max resid | iters | converged? |
|---|---|---|---|---|---|---|---|---|---|---|
| `null` | **0.0516** | 0.0293 | -- | 1.011 | 0.3052 | 0.0000 | 4.5e-14 | 9.3e-07 | 984 | yes |
| `truth` | **0.0843** | 0.0482 | -- | 0.913 | 0.0227 | 0.0176 | 2.2e-13 | 2.0e-06 | 18,192 | **no** |
| `mean` | **0.1615** | 0.1000 | -- | 0.048 | 0.3654 | 0.0063 | 2.7e-07 | 3.8e-02 | 9,962 | **no** |
| `ml_s0` | **0.0813** | 0.0458 | -- | 0.901 | 0.0424 | 0.0119 | 4.1e-13 | 2.1e-06 | 16,899 | **no** |
| `ml_s1` | **0.0807** | 0.0454 | -- | 0.896 | 0.0427 | 0.0116 | 2.4e-13 | 2.0e-06 | 7,922 | **no** |
| `ml_s2` | *(no output — still running at cap)* | | | | | | | | | |

**Reading the `null` rows.** On both ducts NULL is **STAGNATED-NOT-CONVERGED**:
its `Ux`, `k` and `omega` residuals reach 1e-12 to 1e-16, but `Uy`, `Uz` and `p`
sit at O(0.1-0.5) and never fall. That is not a failed solve. A linear
eddy-viscosity model produces a secondary flow that is identically zero to
machine precision (`BASELINES.md` sec. 4), so OpenFOAM normalises the cross-plane
momentum residuals by a field of magnitude ~1e-16 and the ratio is meaningless -
there is nothing for those components to converge *to*. The NULL velocity field
is nonetheless converged where it matters: `NULL - BASE` is **+0.0002** and
**+0.0019** in `U_rms`, so NULL and the shipped baseline agree to within the
benchmark's own convergence gap, and the H1 comparison is unaffected by which is
used. **On CBFS13700 NULL is CONVERGED** (984 iterations, max residual 9.3e-7)
and matches BASE to four decimals.

**H1 against both comparators**, printed because one of them is stagnated:

| Case | ML mean `U_rms` | seed spread | H1 vs NULL | H1 vs shipped BASE |
|---|---|---|---|---|
| `AR_1_Ret_360` | 0.4713 | 0.0097 | **False** | **False** |
| `AR_3_Ret_360` | 0.3839 | 0.0047 | **False** | **False** |
| `CBFS13700` | 0.0810 | 0.0006 | **False** | **False** |

Both readings agree, so nothing turns on the stagnated comparator. Recorded in
full because a stagnated NULL must be labelled, not silently used.

**Convergence counts are a normaliser diagnostic, not a quality signal (N-B22).**
The injected runs converge in **522-3,053** iterations where NULL runs past
**94,000** without meeting the rule - because a non-zero `b^Delta` gives the
cross-plane equations a real source and therefore a real residual. TRUTH (528)
and ML (523) converge in near-identical counts while producing very different
fields, so iteration count here measures whether the residual normaliser is
non-degenerate. It says nothing about accuracy.

## 1. Provenance

| Item | Value |
|---|---|
| solver | the lab's existing `kOmegaSSTCorrected` (`sdk/openfoam/sparta/spartaTurbulenceModels/`), **read-only, unmodified**. No new solver was written |
| application | `simpleFoam`, `libs ("libspartaTurbulenceModels.so")`, OpenFOAM v2606 |
| benchmark | `/home/ubuntu/closure-challenge-benchmark`, commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`, **read-only**; cases copied out to `/home/ubuntu/closure-data/aposteriori/wu2018/` |
| forest | `sklearn` RF, 100 trees, `max_depth` 20, `min_samples_leaf` 9, `max_features="sqrt"`, seeds 0/1/2, retrained on the pre-registered E1 split (23 cases, 341,717 cells) |
| injected field | `bijDelta` = the forest's `Delta b`; `kDeficit` = `uniform 0` |
| scripts | `make_fields.py` (fields + gate G0), `build_cases.sh`, `run_g0a.sh`, `run_solves.sh`, `score.py` |

## 2. Gates

### G0 - sign and convention of the injected tensor: **PASS**

Pure algebra, no solve. The solver realises
`b_total = -(nu_t/k) S + bijDelta` (`kOmegaSSTCorrected.H`; `.C` line 315), and
the forest's target is `Delta b = b_LES - b_RANS` with
`b_RANS = -(nu_t^base/k^base) S^base`, so `bijDelta := Delta b` directly.
Reconstructing `b_total` from the shipped baseline fields and comparing against
the forest's own `b_pred`, over all 15 injected fields:

**worst relative L2 = 1.24e-16** (registered threshold 1e-10). **PASS.**

This gate contains no solve and is therefore unaffected by the benchmark's own
convergence level - see the ADDENDUM sec. A1.

### G0a - the correction terms are inert when zero: **PASS**

Stock `kOmegaSST` against `kOmegaSSTCorrected` with `kDeficit = 0`,
`bijDelta = 0`, from the same shipped fields for the same 200 iterations:

| Case | rel-L2 difference in `U` | registered threshold | result |
|---|---|---|---|
| `AR_1_Ret_360` | **0.000e+00** | < 1e-10 | PASS |
| `AR_3_Ret_360` | **0.000e+00** | < 1e-10 | PASS |
| `CBFS13700` | **0.000e+00** | < 1e-10 | PASS |

Bit-identical, not merely within tolerance: `kOmegaSSTCorrected` is a faithful
superset of stock SST, and every difference reported below is attributable to the
injected anisotropy and nothing else.

### G0b - the shipped fields are NOT converged, which is why NULL exists

First-iteration initial residuals on restarting the **shipped** field with zero
corrections - i.e. a direct measurement of how converged the benchmark's own
"converged" solution is:

| Case | `Ux` | `Uy` | `Uz` | `p` | `k` | `omega` |
|---|---|---|---|---|---|---|
| `AR_1_Ret_360` | **1.64e-3** | 3.06e-1 | 4.14e-1 | 2.01e-1 | 3.57e-5 | 1.89e-8 |
| `AR_3_Ret_360` | **9.29e-4** | 3.68e-1 | 4.39e-1 | 2.63e-1 | 1.74e-5 | 3.64e-8 |
| `CBFS13700` | 2.13e-9 | 1.06e-7 | -- | 3.41e-5 | 5.65e-4 | 4.08e-5 |

**Read these carefully.** The duct `Uy`/`Uz` figures are **not** evidence of a
badly converged secondary flow: a linear eddy-viscosity model produces a
secondary flow that is identically zero to machine precision
(`BASELINES.md` sec. 4), so OpenFOAM is normalising a residual by a field of
magnitude ~1e-16 and the ratio is meaningless. The figures that do mean something
are `Ux` **1.6e-3 / 9.3e-4** on the ducts and `k` **5.7e-4** on CBFS: the shipped
duct solutions stopped on a `residualControl` that listed only `k` and `omega`
(`system/fvSolution`: `k 5e-6; omega 1e-10;`), leaving the streamwise momentum
equation an order of magnitude short of the 1e-6 used here.

**Consequence, registered in ADDENDUM A2 before the solves:** the NULL
configuration - zero corrections, same solver, same mesh copy, same stopping rule
as every injected run - is the comparator used for H1, and the BASE-vs-NULL gap
is reported as the benchmark's own convergence offset rather than being absorbed
into the model's score.

## 3. Configurations

Five per case, all run to the same registered stopping rule (all of
`U, p, k, omega` initial residuals below **1e-6**; hard caps 200,000 iterations
on the ducts and 40,000 on CBFS; a 3,600 s `timeout` inside the script):

| Tag | `bijDelta` | role |
|---|---|---|
| BASE | -- | the shipped converged field, no re-solve |
| NULL | `0` | the honest comparator: same solver and stopping rule, no correction |
| TRUTH | `b_LES - b_RANS` | the ceiling |
| MEAN | `b_mean - b_RANS` | the Charter-2c constant (`BASELINES.md` sec. 6.4) |
| ML x3 | forest `Delta b`, seeds 0/1/2 | the thing under test |

## 4. Results

*(filled from `scores.json` when the solves land)*

## 5. What this result cannot see

* **The a-priori number is not recoverable by construction.** `bijDelta` is frozen
  while `nu_t`, `k` and `S` evolve, so the converged `b` is not the predicted `b`
  and the a-priori `b_rms` of 0.2213 cannot be read off the solved field.
* **`NASA_2DWMH` is BLOCKED**, on a missing library and not on compute: its case
  runs `RASModel AugmentedkOmegaSST` from
  `libfrozenIncompressibleTurbulenceModels.so`, absent from `$FOAM_USER_LIBBIN`,
  `$FOAM_LIBBIN` and `$FOAM_SITE_LIBBIN`. The one case the a-priori study failed
  therefore remains untested a-posteriori.
* **`CBFS13700` is in-sample** for this forest (a training case of the E1 split);
  only the two ducts are strict held-out tests, and they share a flow class.
* **Model error and injection-path error are separable only through TRUTH**, which
  is why TRUTH is a configuration and a gate rather than a nicety.
* **No uncertainty band on the truth**: the benchmark ships none.
* **`k` and `omega` are transported with an added production term but their own
  constants are unchanged**, so any error owed to the SST transport equations
  themselves is present in every configuration, TRUTH included.

## 6. Departures from the preregistration - dated

* **D-1, 2026-08-21, mid-run.** The build script set `writeInterval` equal to the
  iteration cap, so a configuration that hit the registered 3,600 s `timeout`
  before converging would have written **no** time directory and been
  unscorable. `runTimeModifiable` is `true` in these cases, so `writeInterval`
  was changed to 1,000 and `purgeWrite` to 2 on the seven still-running
  configurations while they ran. This changes **write frequency only** - no
  equation, discretisation, boundary condition, relaxation factor or stopping
  rule was touched, and the eleven already-finished runs are unaffected because
  they had already converged and written. Recorded because a mid-run edit to a
  case directory is an intervention, even a numerics-neutral one.

## 7. Compute

| Item | Core-hours |
|---|---|
| field generation + forest retraining (3 seeds) + gate G0 | 0.05 |
| gate G0a (6 runs x 200 iterations) | 0.02 |
| 11 converged solves | **0.31** (1,115 core-seconds, measured) |
| 7 solves that ran to the registered 3,600 s timeout without meeting the stopping rule | <= **7.0** (bounded by the timeout, 6-wide) |
| **total** | **<= 7.4 of the 15-hour lane cap** |

The two duct NULL runs and the five CBFS injected runs account for essentially
all of it. Nothing was killed by hand: every solve ended either by meeting the
registered residual criterion or by its own `timeout`.

## 8. Files

| File | Lines | Role |
|---|---|---|
| `PREREGISTRATION.md` | 312 | frozen, plus dated post-freeze ADDENDUM (G0a, G0b, NULL, cross-lane ceiling, tolerance, in-sample caveat) |
| `RESULTS.md` | 295 | verdict, tables, diagnosis, departures |
| `make_fields.py` | 195 | `bijDelta`/`kDeficit` generation + gate G0 |
| `build_cases.sh` | 91 | case copies out of the read-only benchmark |
| `run_g0a.sh` | 25 | gate G0a |
| `run_solves.sh` | 21 | the 18 bounded solves |
| `score.py` | 166 | all metrics, NULL state, dual H1 |
| `NUMERICS_DRAFT.md` | 78 | N-B22..N-B25 |
| `LESSONS_DRAFT.md` | 106 | L-TBD-W1..W4 |
| `g0a.json` | 4 | gate G0a evidence |

Data, case copies and solver output live outside the repo at
`/home/ubuntu/closure-data/aposteriori/wu2018/`; `scores.json` and
`fields_report.json` there carry every number in this file.
