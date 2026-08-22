# PREREGISTRATION — R4 SPARTA-CLASS build lane (FS3/FS4)

Frozen before any fit. Departures go in a dated section of `RESULTS.md`, never by
editing this file. Date: 2026-08-21. Docket D443.

## 0. ZERO-SHOT DISCIPLINE (charter §22.3, doctrine R1)

### 0.1 The split, from the benchmark's own README (lines 71–77)

| flow | TRAINING (used here) | VALIDATION (used here) | **TEST — OFF LIMITS** |
|---|---|---|---|
| PHLL29 | the 21 remaining hills | `alpha_05_10071_4048/2024`, `alpha_15_7929_4048/2024` | `alpha_15_13929_4048/2024`, `alpha_05_4071_4048/2024` |
| DUCT | `AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`, `AR_10_Ret_180` | `AR_7_Ret_180` | `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180` |
| CBFS13700 | ✓ (training) | — | — |
| PHLL10595 | ✓ (training) | — | — |
| NASAHUMP | — | — | ✓ |

The README's rule is quoted verbatim: *"It is **strictly forbidden** to train or
validate on any data from the **test cases**."*

**Training families for this lane: 21 hills (327,600 cells), 4 ducts (41,971),
`PHLL10595` (15,600), `CBFS13700` (21,000) — 406,171 cells total.** Validation is
the 4 hills + `AR_7_Ret_180`, used only for cross-family model selection inside
FS3. **No test case is opened for any purpose until Sanaa triggers the scoring
call.**

`CBFS13700` and `PHLL10595` are **training** cases under this split, so their
prior use in this programme was legitimate and they remain in scope.

### 0.2 Declared prior exposure — a leakage risk I am carrying, not hiding

Two earlier lanes in this programme (`../Wu2018_PIML_RF/aposteriori/` and
`.../aposteriori_frozenk/`) **scored a-posteriori results on `AR_1_Ret_360` and
`AR_3_Ret_360`, which are TEST cases.** That was legitimate then — those lanes
evaluated an already-trained model once, under a frozen preregistration, and did
no tuning on the outcome. It is nonetheless true that **I have seen** those
numbers (e.g. arm-L TRUTH at −22.2% and −28.9%).

Registered commitment: **no design decision in this lane is conditioned on those
observations.** Every library exclusion, selection rule, gate and threshold below
is derived from *training-family* measurements alone, each with its measurement
cited. Where a choice could have been influenced, the training-family evidence
that determines it is named explicitly so a reader can check the provenance. If
the scoring call later shows those two ducts behaving differently from the
training ducts, that is a result, not a surprise to be explained away.

## 1. SOLVER CONSTRAINT, established from source before designing

`kOmegaSSTSparta` — the symbolic-propagation model — implements **T1, T2, T3
only**. `kOmegaSSTSparta.C` builds `T1 = S`, `T2 = SW − WS`,
`T3 = S² − (1/3)I tr(S²)` (lines 204–208) and dispatches with
`n == 1 ? T1 : n == 2 ? T2 : T3` (lines 221, 235). **There is no T4**, and a term
registered with `n = 4` would **silently evaluate as T3** — a latent defect
recorded here and reported to the owner of `sdk/`.

Schmelzer et al. use **T1–T4 and I1, I2** [VERIFIED-PDF: Schmelzer, Dwight &
Cinnella 2020, Eqs. (9)–(10), arXiv:1905.07510v2 preprint **p. 8**].

**Registered consequence.** The candidate library is **T1, T2, T3 only** for any
model intended for symbolic propagation. If FS3 selects a T4 term, that model is
propagated by **static-field injection** and is labelled *the weaker check*, with
the reason stated in `RESULTS.md`. No term is ever registered with `n = 4`.

## 2. THE LIBRARY, crossed with FS2 — measured on TRAINING families only

Ansatz [Schmelzer Eq. (8), p. 8]: `b^Delta_ij = sum_m c_m I1^p I2^q T^(n)_ij`,
with `tau = 1/omega`, `S = (tau/2)(A + A^T)`, `Omega = (tau/2)(A − A^T)`,
`I1 = S_mn S_nm`, `I2 = Omega_mn Omega_nm`. Same ansatz for `R` contracted with
the velocity gradient, as `kOmegaSSTSparta` implements it.

### 2.1 The decisive FS2 finding: on the duct family the basis is exactly degenerate

Measured on `AR_1_Ret_180` (training duct), over every cell:

* **`T4 = −T3` to machine precision** — `||T3 + T4|| / ||T3||` median **2.74e-17**,
  p99 **6.41e-16**, max **7.08e-15**.
* **`I2 = −I1` identically** — `|tr(S²) + tr(Ω²)| / |tr(S²)|` median **0.000e+00**.
* Per-cell rank of `{T1..T4}` is **exactly 3.000** on the ducts: **4,000 of 4,000
  sampled cells at rank 3, none at rank 4.**

This is the algebra of a fully developed duct, where the mean velocity gradient
has only `dU/dy` and `dU/dz`, so `S² + Ω²` is isotropic and the deviatoric parts
cancel. On the separated training flows the two are independent: per-cell rank
**3.149** (hills), **3.269** (`PHLL10595`), **3.184** (`CBFS13700`), and
`||T3+T4||/||T3||` median **0.146** on `CBFS13700`.

**Registered exclusion, with the FS2 line as the cited reason:** on any fit whose
training set is **ducts only**, `T4` and `I2` are **excluded** — including both
would be an exact collinearity, and the elastic net would split the coefficient
between them by the strength of its L2 term rather than by physics, producing a
"discovered" model that is an artefact of the regulariser. On **mixed-family**
fits both are retained, because the collinearity is partial there, and the
**condition number of the fitted design matrix is reported per fit**.

### 2.2 FS2 exclusions carried over from the 110-feature audit

Measured per training family (`fs2_training_only.json`; method and tolerances in
`_common/features/FS2_DEGENERACY_REPORT.md`):

| training family | cells | rank / 110 | algebraically dead | condition number |
|---|---|---|---|---|
| hills (21) | 327,600 | 100 | 22 | 5.4e17 |
| **ducts (4)** | 41,971 | **96** | **48** | **1.7e33** |
| `PHLL10595` | 15,600 | 100 | 30 | 2.2e17 |
| `CBFS13700` | 21,000 | 100 | 25 | 2.0e18 |
| pooled training | 406,171 | 100 | **12** | — |

The **12 pooled-training dead features** (`trW2SWS2`, `trW2SPS2`, `trW2SKS2`,
`trP2KS2`, `trK2PS2`, `trWPSKS2`, each in both normalisation variants) are
excluded from every fit. They are algebraically zero because every training case
is a statistically two-dimensional mean flow.

### 2.3 Normalisers (L-184)

`I1`, `I2` are formed with `tau = 1/omega`, which **carries no molecular
viscosity** and is therefore Reynolds-similar. **No `nu`-carrying normaliser is
used anywhere in this lane.** The Durbin-bounded variant (feature-library block
B) is **excluded** for exactly that reason: it contains `nu` through
`6 sqrt(nu/eps)`, so two geometrically identical flows at different `Re` do not
map to the same feature value, and this lane's training set spans `Re_H` 5,600 to
13,700 plus `Re_tau` 164–166.

### 2.4 Complexity prior

Schmelzer's discovered models carry **1–5 terms**. Registered: candidate models
are capped at **5 terms**; the exponent grid is `p, q ∈ {0, 1, 2}` with
`p + q <= 2`; ties in cross-validated error are broken toward **fewer terms**.

## 3. FS3 — selection methods, compared prediction-first

Three methods, all run, all reported, **inside the training set only**:

1. **Mutual information** (`sklearn.feature_selection.mutual_info_regression`)
   between each candidate column and the target.
2. **Permutation importance** on a held-out training *family*.
3. **L1 / elastic-net path** — `ElasticNetCV`, `l1_ratio ∈ {0.1, 0.5, 0.7, 0.9,
   0.95, 0.99, 1.0}`, 60-point `alpha` path, chosen by cross-**family** CV.

**Cross-family validation, registered:** folds are **whole families**
(leave-one-family-out over {hills, ducts, `PHLL10595`, `CBFS13700`}), never
random cells. Random cell splits leak: the 21 hills come in `(alpha, length)`
triples differing only in domain height (`BASELINES.md` sec. 6.2).

Agreement between the three rankings is reported as a number (Spearman rank
correlation of the top-20), because three methods agreeing is evidence and three
disagreeing is a finding.

## 4. FS4 — the freeze

The selected term set is **frozen per model class** (one set for `b^Delta`, one
for `R`) and written to `MODEL.md` **before any propagation run**, with
coefficients, terms, and the training families used. After that point no term is
added or removed. Any later change is a new preregistration.

## 5. STEP 2 — targets and training

Targets from **`kOmegaSSTFrozen`** (the W2-validated `k`-corrective-frozen-RANS
path; its extraction satisfies its defining identity to **8.8e-14** on PH10595
and **1.7e-13** on CBFS13700 — verified independently in
`../Schmelzer2020_SpaRTA/RESULTS.md` sec. 3), run on **training flows only**, to
produce `bijDelta` and `kDeficit` fields from the LES/DNS truth.

Seeds: **0, 1, 2** wherever a method is stochastic (permutation importance, CV
folds, any bootstrap). Elastic net is deterministic given `(alpha, l1_ratio)`;
the seed controls fold assignment only.

## 6. STEP 3 — gates, registered now

**a-priori (the Charter-2c bar, not SST).** The discovered `b^Delta` must beat
the **TRAIN-MEAN tensor** on training-family `b_rms`. The train-mean constant
beats k-omega SST on 8 of 8 held-out cases (`BASELINES.md` sec. 6.4), so **SST is
not the bar and is not quoted as one**. Registered: **PASS** requires the
discovered model below train-mean `b_rms` on **>= 3 of the 4 training families**.

**a-posteriori, on training flows.** Propagate the discovered symbolic model via
`kOmegaSSTSparta` (T1–T3 terms) and report per training family:

* `eps(U)/eps(U_0)` against **the frozen-field ceiling computed per case in this
  lane** (Schmelzer Table 1 style — the ceiling is measured here, not quoted);
  registered gate **`eps(U)/eps(U_0) <= 0.6`** on `PHLL10595` and `CBFS13700`,
  the two cases where a per-case ceiling is directly comparable;
* **continuity**: `sum local div(U)` from the solver log, registered
  **`<= 1e-4`** else **NOT CONVERGED** whatever the velocity error;
* **realisability of the total `tau`**, at `tol = 1e-6`, beside the truth's own
  rate;
* **structure**: duct secondary-flow magnitude as % of bulk (training ducts;
  DNS values from `BASELINES.md` sec. 4) and reattachment on training hills and
  `CBFS13700` against LES;
* **iteration counts and stagnation state per configuration**, with **both
  comparators** — NULL (zero-correction, same solver and stopping rule) and the
  shipped BASE — and `NULL − BASE` named (N-B22, N-B23).

**Verdicts** from the fixed vocabulary. **GATE FAIL** if the a-priori bar is
missed, or if any propagation diverges or stagnates without meeting the
convergence rule. **NOT A RESULT** if the per-case frozen-field ceiling itself
fails to beat NULL by 30% — the lesson of the two prior lanes, registered here in
advance rather than discovered again.

## 7. FS2/FS5 coverage shipped with the model

`COVERAGE.md` ships with `MODEL.md` and states: each selected feature's range on
each training family against the others; the pooled training range; and **what a
future test exposure must check** — for every selected term, the fraction of test
cells outside the training range, and the per-cell rank of the selected tensor
set on the test family. No test number is computed until the scoring call.

## 8. Compute

Target extraction (frozen-RANS, 27 training cases) ~1; FS3 selection ~2;
propagation runs (4 families x {NULL, ceiling, discovered} x 3 seeds) ~8–15.
**Estimate 12–20 core-hours; cap 40.** Past 32 the seed count drops to 1 for
propagation and the reduction is reported. All runs bounded, checkpointed,
`writeInterval` set from the start, and resumable; nothing is ever killed.

## 9. What this lane cannot see

* **Nothing about generalisation.** Every number is a training-family number.
  The a-posteriori gates test whether the discovered model *propagates*, not
  whether it transfers.
* **The duct family cannot exercise T4** (sec. 2.1), so a coefficient on T4
  fitted with ducts in the training set is determined entirely by the separated
  flows.
* **`kOmegaSSTSparta` cannot propagate T4 at all** (sec. 1), so a model needing it
  is testable only by the weaker static-field route.
* **A `b`-only correction has a ceiling this programme has already measured
  twice**: injecting the exact anisotropy with `kDeficit = 0` made `U_rms` worse
  on every case tried, even with `k` frozen exactly. This lane fits **both**
  `b^Delta` **and** `R` precisely because of that, but the risk that the pair is
  still not enough is real and is why sec. 6 registers a NOT A RESULT branch.
* **No uncertainty band on the truth**, and the two-dimensionality of every
  training case bounds what any tensor-basis conclusion can mean.

---

# ADDENDUM, dated 2026-08-21, post-freeze. Nothing above is altered.

Two interface facts arrived after the freeze. Both were verified against disk
before being recorded; neither changes any gate, threshold or exclusion.

## A1. `NASA_2DWMH` moves from BLOCKED to checkable-at-the-scoring-call

Earlier lanes in this programme reported the hump **BLOCKED** because its shipped
case runs `RASModel AugmentedkOmegaSST` from a library absent on this machine.
The shelf-D lane has since closed that gap with a preregistered gate:
`kOmegaSSTCorrected` at zero corrections, with the shipped `omegaMin` and
`fvOptions`, restarted from the shipped hump field, converges in **156
iterations** to `U_rms` **0.1261769** against the published **0.1260** —
**Δ = 1.77e-4** against a registered band of 5e-3 (**PASS**;
`../NASA_hump_gate/RESULTS.md`, gate B-G0b). The shipped baseline is therefore
behaviourally reproducible with the stock-derived model.

**Consequence for this lane, and it is confined to `COVERAGE.md`:** sec. 7's
"what a future test exposure must check" lists the hump among the **checkable**
test families rather than as blocked, and carries its FS2 numbers — **31.79% of
its cells outside the pooled training range on at least one feature, and 49 of
110 features going out of range somewhere on it**, the worst of any test family
by a factor of ten (`_common/features/FS2_DEGENERACY_REPORT.md` sec. 6).

**Zero-shot is unaffected: no hump number is computed by this lane until Sanaa
triggers the scoring call.** The change is that the hump's eventual exposure is
now a *measurement* rather than a *blocked row*, which raises what COVERAGE.md
must promise, not what this lane may look at.

## A2. The shelf-D band caveat, cited in the form the source actually states it

If this lane's model ships a shelf-D model-form band, it cites
`_common/uq_eigenspace/UQ_EIGENSPACE.md` **with its registered caveat**. The
precise statement there, which is stronger and more specific than "shape or
forcing but not both":

> Emory's eq. (4) keeps `k` **outside** the bracket, so the eigenspace family
> perturbs **shape and orientation only**; a `k`-magnitude error is outside the
> envelope **by construction**. Across these cases the RANS `k` is **0.59 to
> 0.72** of the LES `k` in the mean, so **2–7% of cells have a production the
> envelope cannot reach whatever `delta_B` does** (§5). And: *"Neither published
> framework on this shelf contains the thing it is meant to bound, and they fail
> on different axes."*

That file also records that a meaningful a-posteriori envelope needs either a
forward model carrying `k`, or `delta_B` well below 1, and that **neither was
run — both are registered as unrun** (§6).

This matters directly to R4 rather than being a footnote: this lane fits `R`
(the `k`-equation correction) precisely because a `b`-only correction cannot
carry `k`, and the eigenspace band has the **same** blind spot on the **same**
axis. **A band from that machinery must not be presented as bounding the error of
a model whose main correction is to `k`.** Where the two are shown together, the
overlap in what neither can see is stated.
