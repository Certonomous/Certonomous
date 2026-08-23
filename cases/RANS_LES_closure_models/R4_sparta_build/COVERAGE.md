# COVERAGE — FS2/FS5 coverage for the R4 SpaRTA-class model

> **LATE DELIVERY 2026-08-23 — registered §7, due with `MODEL.md`, disclosed as
> departure D-14.** `PREREGISTRATION.md` §7 (lines 199–205) required this file to
> ship with `MODEL.md` on 2026-08-22. It did not. The non-delivery was not
> disclosed among departures D-1…D-13 and is not among the ten bullets of
> `RESULTS.md` §7. It was found on 2026-08-23 by the R5 discharge-record lane and
> verified personally by the closure supervisor the same day. **This delivery
> discharges the deliverable. It does not discharge the disclosure duty, which
> stays on record as breached** (`RESULTS.md` §12, D-14).

**Generated** by `make_coverage.py` from `/home/ubuntu/closure-data/r4/dataset/`.
Re-running reproduces it. Machine-readable twin: `artefacts/coverage.json`.
**Nothing is fitted. No model is trained. No TEST or validation case is opened —
the guard is `r4_lib.assert_no_test_case`, and `make_coverage.py::guard_is_armed`
plants a control on it (it must raise on `NASA_2DWMH`) before its silence on the
training set is trusted.** **No test number is computed anywhere below**, as §7
requires; §4 states what must be computed at the scoring call and against what.

**Compute:** 30.6 core-seconds (0.51 core-minutes), 1 rank, numpy reads only.
Registered cap for this delivery: 0.1 core-h. **Two `numpy.linalg.svd` sweeps
over 172,106 cells** and percentile reductions; no solver ran.

---

## 0. What this covers, and the one place the registration had to be interpreted

**The model this covers** is the FS4 freeze in `MODEL.md`:

    R        = 2k [ 1.261646025 − 42.82547649 I1 − 31.54761765 I2 + 14.28260064 I2² ] T1
    b^Delta  = −7.550379605 T2 − 16.07577893 I2 T2 + 5.039083086 T3

Selected **tensors**: `T1`, `T2`, `T3`. **`T4` is not selected** and is not
covered here. Selected **scalar features**: `I1`, `I2`; the derived multiplier
`I2²` is carried separately because it is the column that was actually fitted.

**The interpretation, stated rather than assumed.** §7 asks for "each selected
feature's range" and, for "every selected **term**", a fraction of cells outside
the training range. A selected term such as `I2²·T1` is **tensor-valued**, and a
range requires a scalar, so the registration is not literally executable as
written on a term. It is resolved here by covering **(a)** every scalar
multiplier that appears in a selected term — `I1`, `I2`, `I2²` — and **(b)** the
Frobenius norm `||T_n||_F` of every selected tensor. A term's value is a product
of one of (a) with one of (b), so a cell inside the range of both factors is
inside the range of the term. **What was NOT computed** is the alternative
reading: nine per-component ranges per tensor, i.e. 27 additional columns. That
is recorded here as an uncomputed option, **not silently approximated** — a
future lane that wants component-wise coverage must compute it, and this file
does not claim to contain it.

**Cells.** The exact fit mask of `fs3_select.py` (its lines 89–90:
`k_LES_shipped > 0` and finite in every candidate and target) is reproduced
here. It selects **172,106 of 172,171** cells, dropping **65 (0.038 %), all of
them hills** — identical to `RESULTS.md` §3.3, which is an independent
reproduction of that accounting, not a restatement of it.

**Fields.** All numbers are on the **frozen** fields (`U = U_LES`) that the
SpaRTA regression actually fitted, with `τ = 1/ω`, `S = (τ/2)(A+Aᵀ)`,
`Ω = (τ/2)(A−Aᵀ)` — the conventions `kOmegaSSTSparta` itself uses. **They are
not on the baseline RANS fields**, which is the field the 110-feature FS1/FS2
library is built on (`_common/features/build_features.py` reads the baseline
case's latest time directory). `RESULTS.md` §3.2 measures how far apart those
two fields are on this very basis, so the distinction is load-bearing and the
FS2 report's own coverage table is **not** a substitute for this one.

**Scaling.** `R`'s candidate columns were divided per case by the case median of
`k·ω` (departure D-2). `I1`, `I2` and `||T_n||_F` are unaffected by that
constant, so every range below is the range that was fitted.

**Realised, not registered, training set.** These are the **12** cases that
reached COMPLETE under the strict completion rule, not the 27 the
pre-registration names (departure D-1). Fifteen hills have no frozen extraction,
and the six that survived are **not a random sample** (`RESULTS.md` §11.3(c)).
**Every range in this document inherits that bias**, and no widening of it is
implied by the cell counts being large.

| case | family | cells | fitted | dropped |
|---|---|---|---|---|
| `alpha_10_12000_4048` | hills | 15,600 | 15,584 | 16 |
| `alpha_125` | hills | 15,600 | 15,593 | 7 |
| `alpha_15_10929_3036` | hills | 15,600 | 15,590 | 10 |
| `alpha_15_10929_4048` | hills | 15,600 | 15,587 | 13 |
| `alpha_15_13929_3036` | hills | 15,600 | 15,590 | 10 |
| `alpha_15_7929_3036` | hills | 15,600 | 15,591 | 9 |
| `AR_1_Ret_180` | ducts | 2,209 | 2,209 | 0 |
| `AR_3_Ret_180` | ducts | 6,627 | 6,627 | 0 |
| `AR_5_Ret_180` | ducts | 11,045 | 11,045 | 0 |
| `AR_10_Ret_180` | ducts | 22,090 | 22,090 | 0 |
| `PHLL10595` | `PHLL10595` | 15,600 | 15,600 | 0 |
| `CBFS13700` | `CBFS13700` | 21,000 | 21,000 | 0 |
| **total** | | **172,171** | **172,106** | **65** |

---

## 1. Each selected feature's range, per training family and pooled

§7 item 1 and item 2. `min / p01 / p50 / p99 / max` over fitted cells.

**`I1 = S_mn S_nm`**

| set | min | p01 | p50 | p99 | max |
|---|---|---|---|---|---|
| hills | 9.196e-10 | 1.708e-05 | 0.01394 | 0.07462 | **0.8385** |
| ducts | 2.227e-13 | 2.295e-09 | 0.02055 | 0.07354 | 0.08499 |
| `PHLL10595` | 1.692e-08 | 8.301e-05 | 0.01334 | 0.09365 | 0.1566 |
| `CBFS13700` | 8.832e-12 | 1.452e-06 | 0.01056 | 0.1291 | 0.8212 |
| **POOLED** | **2.227e-13** | 3.706e-08 | 0.01413 | 0.09127 | **0.8385** |

**`I2 = Ω_mn Ω_nm`** (non-positive by construction; `MODEL.md` states `I2 <= 0`)

| set | min | p01 | p50 | p99 | max |
|---|---|---|---|---|---|
| hills | **−0.8526** | −0.03786 | −0.009146 | −7.016e-06 | −2.009e-12 |
| ducts | −0.08481 | −0.07337 | −0.02063 | −2.295e-09 | −2.227e-13 |
| `PHLL10595` | −0.05727 | −0.04279 | −0.009861 | −1.423e-05 | −9.919e-12 |
| `CBFS13700` | −0.7825 | −0.1295 | −0.006477 | −7.827e-10 | −5.095e-16 |
| **POOLED** | **−0.8526** | −0.08029 | −0.009976 | −1.083e-08 | **−5.095e-16** |

**`I2²`** — the column fitted in `R`'s fourth term

| set | min | p01 | p50 | p99 | max |
|---|---|---|---|---|---|
| hills | 4.035e-24 | 4.922e-11 | 8.365e-05 | 0.001433 | **0.7269** |
| ducts | 4.958e-26 | 5.269e-18 | 4.255e-04 | 0.005384 | 0.007193 |
| `PHLL10595` | 9.838e-23 | 2.025e-10 | 9.724e-05 | 0.001831 | 0.003279 |
| `CBFS13700` | 2.596e-31 | 6.126e-19 | 4.196e-05 | 0.01676 | 0.6123 |
| **POOLED** | 2.596e-31 | 1.172e-16 | 9.953e-05 | 0.006446 | **0.7269** |

**`||T1||_F`**

| set | min | p01 | p50 | p99 | max |
|---|---|---|---|---|---|
| hills | 3.033e-05 | 0.004133 | 0.1181 | 0.2732 | **0.9157** |
| ducts | 4.719e-07 | 4.791e-05 | 0.1434 | 0.2712 | 0.2915 |
| `PHLL10595` | 1.301e-04 | 0.009111 | 0.1155 | 0.3060 | 0.3957 |
| `CBFS13700` | 2.972e-06 | 0.001205 | 0.1027 | 0.3593 | 0.9062 |
| **POOLED** | 4.719e-07 | 1.925e-04 | 0.1189 | 0.3021 | **0.9157** |

**`||T2||_F`**

| set | min | p01 | p50 | p99 | max |
|---|---|---|---|---|---|
| hills | 1.956e-10 | 2.063e-05 | 0.01637 | 0.05228 | **1.195** |
| ducts | 3.149e-13 | 3.246e-09 | 0.02904 | 0.1038 | 0.1200 |
| `PHLL10595` | 1.688e-08 | 8.464e-05 | 0.01612 | 0.05471 | 0.06403 |
| `CBFS13700` | 8.396e-13 | 2.722e-07 | 0.009241 | 0.1830 | 1.120 |
| **POOLED** | 3.149e-13 | 4.403e-08 | 0.01704 | 0.1117 | **1.195** |

**`||T3||_F`**

| set | min | p01 | p50 | p99 | max |
|---|---|---|---|---|---|
| hills | 3.766e-10 | 7.004e-06 | 0.005693 | 0.03048 | 0.3438 |
| ducts | 9.091e-14 | 9.371e-10 | 0.008390 | 0.03002 | 0.03470 |
| `PHLL10595` | 6.969e-09 | 3.390e-05 | 0.005445 | 0.03824 | 0.06399 |
| `CBFS13700` | 7.211e-12 | 9.533e-07 | 0.004335 | 0.05276 | **0.3784** |
| **POOLED** | 9.091e-14 | 1.597e-08 | 0.005773 | 0.03729 | **0.3784** |

**Reading.** The ducts are the **narrowest** family on every one of the six
columns — their `I1` tops out at 0.085 against a pooled 0.839, their `||T2||_F`
at 0.120 against 1.195 — and the extremes on five of six columns belong to the
hills. `CBFS13700` owns the largest `||T3||_F`. Nothing here is a defect; it is
the shape of the training box the coefficients were fitted inside, and §4 is
where it becomes a duty.

---

## 2. Each family against the others — leave-one-family-out coverage

§7 item 1's "against the others", executed with the **same fold structure the
fit used** (leave-one-family-out over hills / ducts / `PHLL10595` /
`CBFS13700`). "Outside" means beyond the min–max set by the other three
families. "Worst excursion" is in units of the other-three range span.

| held-out family | cells | **cells outside on ≥1 selected feature** |
|---|---|---|
| hills | 93,535 | **0.00107 %** (1 cell in 93,535) |
| ducts | 41,971 | **0.0905 %** |
| `PHLL10595` | 15,600 | **0.0000 %** — every cell inside |
| `CBFS13700` | 21,000 | **0.2238 %** |

Per feature:

| held out | feature | other-3 range | held-out range | outside | below | above | worst excursion (spans) |
|---|---|---|---|---|---|---|---|
| hills | `I1` | [2.227e-13, 0.8212] | [9.196e-10, 0.8385] | 0.00107 % | 0 | 0.00107 % | 0.0211 |
| hills | `I2` | [−0.7825, −5.095e-16] | [−0.8526, −2.009e-12] | 0.00107 % | 0.00107 % | 0 | 0.0896 |
| hills | `I2²` | [2.596e-31, 0.6123] | [4.035e-24, 0.7269] | 0.00107 % | 0 | 0.00107 % | **0.187** |
| hills | `||T1||_F` | [4.719e-07, 0.9062] | [3.033e-05, 0.9157] | 0.00107 % | 0 | 0.00107 % | 0.0105 |
| hills | `||T2||_F` | [3.149e-13, 1.120] | [1.956e-10, 1.195] | 0.00107 % | 0 | 0.00107 % | 0.0669 |
| hills | `||T3||_F` | [9.091e-14, 0.3784] | [3.766e-10, 0.3438] | 0 | 0 | 0 | 0 |
| ducts | `I1` | [8.832e-12, 0.8385] | [2.227e-13, 0.08499] | 0.0620 % | 0.0620 % | 0 | 1.03e-11 |
| ducts | `I2` | [−0.8526, −5.095e-16] | [−0.08481, −2.227e-13] | 0 | 0 | 0 | 0 |
| ducts | `I2²` | [2.596e-31, 0.7269] | [4.958e-26, 0.007193] | 0 | 0 | 0 | 0 |
| ducts | `||T1||_F` | [2.972e-06, 0.9157] | [4.719e-07, 0.2915] | 0.0620 % | 0.0620 % | 0 | 2.73e-06 |
| ducts | `||T2||_F` | [8.396e-13, 1.195] | [3.149e-13, 0.1200] | 0.00953 % | 0.00953 % | 0 | 4.39e-13 |
| ducts | `||T3||_F` | [7.211e-12, 0.3784] | [9.091e-14, 0.03470] | 0.0905 % | 0.0905 % | 0 | 1.88e-11 |
| `PHLL10595` | all six | — | — | **0** | 0 | 0 | 0 |
| `CBFS13700` | `I1` | [2.227e-13, 0.8385] | [8.832e-12, 0.8212] | 0 | 0 | 0 | 0 |
| `CBFS13700` | `I2` | [−0.8526, −2.227e-13] | [−0.7825, −5.095e-16] | 0.219 % | 0 | 0.219 % | 2.61e-13 |
| `CBFS13700` | `I2²` | [4.958e-26, 0.7269] | [2.596e-31, 0.6123] | 0.219 % | 0.219 % | 0 | 6.82e-26 |
| `CBFS13700` | `||T1||_F` | [4.719e-07, 0.9157] | [2.972e-06, 0.9062] | 0 | 0 | 0 | 0 |
| `CBFS13700` | `||T2||_F` | [3.149e-13, 1.195] | [8.396e-13, 1.120] | 0 | 0 | 0 | 0 |
| `CBFS13700` | `||T3||_F` | [9.091e-14, 0.3438] | [7.211e-12, 0.3784] | 0.00476 % | 0 | 0.00476 % | **0.101** |

**Two readings, and the second one matters more.**

1. **Cross-family coverage inside the training set is very nearly complete on
   the selected features.** The worst family loses 0.22 % of its cells, one
   family loses none at all, and every duct excursion and almost every
   `CBFS13700` excursion is a **floor** excursion of order 1e-11 spans or
   smaller — a cell whose `I1` is nearer zero than any cell in the other three
   families, which is a laminar-limit artefact, not an extrapolation. Only two
   excursions exceed a tenth of a span: the hills' `I2²` at **0.187** and
   `CBFS13700`'s `||T3||_F` at **0.101**.
2. **Therefore R4's failure was not a training-set coverage failure.** The
   discovered model missed the a-priori bar on 2 of 4 families and diverged on
   all twelve propagations (`RESULTS.md` §6, gates G1 and G2) **inside a feature
   box its own folds cover almost completely.** Coverage is not the axis that
   explains the GATE FAIL — `RESULTS.md` §4.6 and §5.4 locate that in
   realisability and in the discovered `R`. **This document rules nothing in or
   out; it removes one candidate explanation and says which measurements own the
   rest.**

---

## 3. Per-cell rank and conditioning of the SELECTED tensor set `{T1, T2, T3}`

§7 item 3's training-side reference. Per cell, the singular values of the
3 × 9 stack of the three flattened selected tensors; rank counts
`σ_i > 1e-10 · σ_1` — the **same convention** `assemble_dataset.py` used for its
`{T1..T4}` numbers, so the two are comparable. Full cell count, no subsample.

| family | cells | mean rank | min…max | `σ1/σ3` p50 | p99 | max |
|---|---|---|---|---|---|---|
| hills | 93,535 | **3.000** | 3…3 | 20.88 | 698.9 | 4.998e+05 |
| ducts | 41,971 | **3.000** | 3…3 | 17.30 | **5.113e+04** | 5.191e+06 |
| `PHLL10595` | 15,600 | **3.000** | 3…3 | 21.31 | 358.4 | 2.245e+05 |
| `CBFS13700` | 21,000 | **3.000** | 3…3 | 29.74 | 2.672e+04 | **4.430e+07** |
| **POOLED** | **172,106** | **3.000** | **3…3** | 20.81 | 1.634e+04 | 4.430e+07 |

**The selected set is full rank in every fitted cell of every training family —
172,106 of 172,106 at rank 3.** This is the direct answer to the question
`PREREGISTRATION.md` §2.1 was written about: the exact duct degeneracy that file
records is `T4 = −T3`, and **`T4` is not in the selected set**, so the
degeneracy that motivated the registered exclusion does not touch the model that
was actually frozen. (`RESULTS.md` §3.2 separately measures that on frozen
fields the `{T1..T4}` rank is 3.965–3.978 rather than 3.000 anyway.)

**Rank alone is the weaker half of this table and must not be quoted without the
other half.** Rank answers "independent?"; `σ1/σ3` answers "how nearly
dependent?". The pooled median is a benign **20.8**, but the **ducts' p99 is
5.1e+04** and the pooled maximum is **4.4e+07**: on roughly one duct cell in a
hundred the three selected tensors are within five orders of magnitude of
collinear, and a coefficient set fitted across such cells is being asked to
allocate mass in a direction the data barely distinguishes. **A rank of 3 with a
condition number of 5e+04 is not a well-posed local basis**, and any future
record quoting the rank-3 result quotes this line beside it.

---

## 4. What a future test exposure must check — the specification, no numbers

§7 item 3, and `PREREGISTRATION.md` **Addendum A1** (lines 252–262), which
confines its consequence to exactly this section. **No test number is computed
here and none may be until Sanaa triggers the one pre-registered scoring call.**
This section is the checklist that call executes.

**The test families, and their status.** The benchmark TEST set is
`alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_2024`,
`alpha_05_4071_4048`, `AR_14_Ret_180`, `AR_1_Ret_360`, `AR_3_Ret_360` and
`NASA_2DWMH`. Per Addendum A1 the hump is **checkable, not blocked**: the
shelf-D lane's gate B-G0b converged the shipped hump baseline in 156 iterations
to `U_rms` 0.1261769 against a published 0.1260 (Δ = 1.77e-4 against a
registered band of 5e-3, PASS; `../NASA_hump_gate/RESULTS.md`). A1 also requires
this file to carry the hump's FS2 numbers, and they are the loudest warning in
this document: **31.79 % of `NASA_2DWMH` cells fall outside the pooled training
range on at least one feature, and 49 of 110 features go out of range somewhere
on it — the worst of any test family by a factor of ten**
(`_common/features/FS2_DEGENERACY_REPORT.md` §6). Those are **FS1-library,
baseline-RANS-field** numbers, not numbers on the six columns of §1; they bound
expectation, they do not substitute for the check below.

**At the scoring call, for each test case, compute and report:**

1. **Per selected feature** — `I1`, `I2`, `I2²`, `||T1||_F`, `||T2||_F`,
   `||T3||_F` — the fraction of that case's cells falling outside the **POOLED**
   range of §1, split into below-min and above-max, with the worst excursion in
   units of the pooled span. **Reference values are the POOLED rows of §1** and
   they are fixed by this document's commit.
2. **Any-feature** — the fraction of cells outside on ≥ 1 of the six. The
   in-training reference is §2's held-out column: **0.0011 % / 0.0905 % /
   0.0000 % / 0.2238 %**. A test family two orders of magnitude above the worst
   of those is out of family on this instrument.
3. **Per-cell rank of `{T1, T2, T3}`** on the test family, at `σ_i > 1e-10 σ_1`,
   with the histogram — against the training reference **3.000, min 3, max 3,
   172,106 of 172,106 cells** (§3). **Any cell below rank 3 is a cell where the
   selected basis collapses and the three coefficients are not separately
   identified.**
4. **`σ1/σ3` per cell**, p50 / p99 / max, against the training reference
   **20.81 / 1.634e+04 / 4.430e+07** (§3). Report it beside the rank, never
   instead of it and never without it.
5. **The features on the same field.** All four quantities above are computed on
   the **frozen** convention of §0. A test exposure that computes them on
   baseline RANS fields is measuring a different quantity and its numbers do not
   compare to the references here.

**What the answer obliges.** FS5, as folded into
`CLOSURE_MODELLING_CHARTER.md` §22.5, permits exactly two responses beyond its
declared factor: **retrain-coverage expansion**, or **explicit documented
acceptance**. This document names them and **does not choose between them**,
because choosing needs a factor and there is none — see §5.

---

## 5. What could not be delivered as registered, recorded and not approximated

1. **FS5's "declared factor" does not exist, and this document does not create
   one.** The doctrine (`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md`:252) and
   the charter (`CLOSURE_MODELLING_CHARTER.md`:822 and :827) each state that a
   factor is declared **in advance**; a repository sweep for the phrase returns
   those three statements of the requirement and **no instance of any build
   meeting it** — stated three times, met zero times. A factor invented in a
   late-delivered document, after the coefficients exist and after the verdict
   is on the docket, would be a post-hoc threshold and is refused
   (`CLAUDE.md` rule 2). **Declaring it is an act for the next
   pre-registration, before its compute.** Until then §4's checks produce
   numbers with no bar to cross, and that limitation is this document's, not the
   reader's to discover.
2. **The per-component reading of "every selected term" is not computed** — see
   §0. Six scalar columns are covered; 27 per-component tensor columns are not.
3. **These ranges are the realised 12-case training set, not the registered
   27-case one**, and the six surviving hills are not a random sample
   (departure D-1; `RESULTS.md` §11.3(c)). A future exposure comparing against
   §1 is comparing against a biased box, and the bias is not quantified here
   because quantifying it needs the fifteen extractions that do not exist.
4. **Nothing here is a coverage statement about `T4`.** `T4` is not selected.
   `PREREGISTRATION.md` §2.1's duct exclusion and `RESULTS.md` §11.4's
   correction to its justification both concern `T4` and both stand untouched by
   this file.

---

## 6. Instrument caveat carried forward — `q1_wallRe` is clipped, and the FS5 sweep cannot see past the clip

**This does not affect any number above**: R4's model does not use `q1_wallRe`,
which is not among its selected features. It is recorded here because §4 sends a
future reader to `FS2_DEGENERACY_REPORT.md` §6 for the FS1-library coverage
numbers, and that instrument has a blind spot on the exact axis that named the
R5 constraint this document sits under.

`_common/features/FEATURE_LIBRARY.md:174` defines the library's wall-distance
Reynolds number as **`q1_wallRe = min(sqrt(k)·d/(50·ν), 2)`** — clipped at 2.
Its pooled statistics in `/home/ubuntu/closure-data/features/fs2_audit.json` are
**`max = 2.0`, `p99 = 2.0`, `p50 = 2.0`**: the column saturates at its clip on
more than half of all cells. A test cell whose true `Re_y` exceeds the trained
maximum therefore **cannot register as above the training range on that column,
because the training maximum is the clip**. The round-5 diagnostic that put this
constraint on the R-ladder was measured on the **unclipped** `Re_y`, at **1.85×
and 2.07×** its trained maximum on two ducts
(`research/closure/md/CLOSURE_CHALLENGE_STATUS.md`:418–423). **The FS5 sweep as
built would not have seen it.** The repair — an unclipped companion column, or a
declared exemption for clipped features — is owed before the next build's FS5
discharge and is not made here.

---

## 7. What this document cannot see

* **It grades nothing and it moves no verdict.** R4 is closed at **GATE FAIL**
  (`RESULTS.md` §0 and §6) and nothing here touches that. No gate, threshold,
  cap or label is created, and none could be: §7 registered a **document**, not
  a gate.
* **It computes no test number**, so it says nothing about generalisation, about
  any of the eight scored cases, or about the hump beyond quoting FS2's
  committed baseline-field statistic.
* **It is a coverage statement, not a selection and not a diagnosis.** Nothing
  is ranked by usefulness, nothing is removed, and §2's reading that coverage
  does not explain the GATE FAIL removes one candidate explanation without
  establishing another.
* **It inherits every limitation of the 12-case realised training set**, listed
  at §5 item 3.
* **Its `σ1/σ3` tail is measured, its consequence is not.** That roughly one
  duct cell in a hundred carries a near-collinear selected basis is a
  measurement; whether that materially moved the fitted coefficients is
  **unmeasured**, and measuring it means refitting, which this delivery does not
  do and is not licensed to do — the FS4 freeze is final (`MODEL.md`).
* **Nothing was sent.** Nothing here is filed, uploaded, registered or submitted
  outside this box.
