# DRAFT — NOT FROZEN, ~~NOT COMMITTED~~ **TRACKED IN GIT BUT NOT FROZEN** (a lane commit that makes this draft readable at HEAD — it is **NOT** the §14 commit-1 freeze, no sha256 is registered by it), NO COMPUTE AUTHORISED

**This file is a DRAFT.** It is not frozen, its sha256 registers nothing, and
**no solver, fit, selection or propagation is authorised by it.** It becomes a
pre-registration only when the closure supervisor commits it ALONE, records its
sha256 in the commit message, and authorises the launch as a separate act
(CLAUDE.md rule 2; `VERIFICATION_CHARTER.md` §2b, §2d). Until then every gate,
threshold, cap and label below is a **proposal to the supervisor**, not a
registration. Nothing here has been sent, filed, uploaded, registered or posted
(CLAUDE.md rule 7; Charter §19).

**Zero compute was spent producing this file.** No run directory was created, no
solver ran, no fit was performed, nothing under `/home/ubuntu/closure-data/` was
written. Every number below is quoted from a record already on disk, with its
artefact path.

---

# PREREGISTRATION (DRAFT) — R4b, the uniform amplitude/realisability control on the PAIR

**Lane:** closure. **Option `A′`** of `docs/closure/R5_DECISION_MEMO.md` §3.
**Date drafted:** 2026-08-24. **Docket row:** not yet assigned (assigned at
commit, from the tail — CLAUDE.md rule 11).
**Predecessors:** `../R4_sparta_build/` (**GATE FAIL**),
`../R5C_omega_repair/` (**GATE FAIL**).

---

## 0. WHY THIS INCREMENT, AND WHOSE DECISION IT IS

### 0.1 The derivation, written out so it can be argued with

Sanaa ratified R3 on 2026-08-24, verbatim as relayed to this lane:

> *"R3 is ratified (SpaRTA-class, TBNN fallback) — R4's CPU-minutes run in
> parallel; they never displace consolidation work."*

That closes `CLOSURE_MODELLING_CHARTER.md` §22.7 (the model class is Sanaa's to
pick and she has picked). Applying her ruling to the memo's option list
eliminates by construction:

| memo option | why it is not this increment |
|---|---|
| **B1** FIML-C | a **different model class**; re-opening R2's ranking is a re-opening of R3 and is hers alone (Charter §22.7). Her ruling names SpaRTA-class. |
| **B2** TBNN + `R` head | TBNN-class is named in her ruling as the **fallback**, not the pick. |
| **D** stop discovery | excluded by *"R4's CPU-minutes run in parallel"* — discovery continues. |
| **C** the `omega`-source repair | **already run, as R5C, and CLOSED `GATE FAIL`** (`../R5C_omega_repair/RESULTS.md` lines 3, 17, 28). Its registered consequence was applied verbatim: *"R4's 12 targets stand. The 15 hills remain INCOMPLETE. The R5C targets are reported and used for nothing."* |
| **A** control on `b^Delta` alone | measured in advance to be insufficient: with `b^Delta` switched off **entirely**, R4's discovered `R` still **diverges on all six hills and on `CBFS13700`** (`sum local` to **9.8e+05** after 163 iterations) and survives `PHLL10595` only at **49.18x** the baseline error (`../R4_sparta_build/RESULTS.md` §5.1, §5.4, §11.5). |

**What remains is `A′`: one uniformly-applied amplitude / realisability control
on the PAIR — `b^Delta` and `R` together — on R4's standing 12 training
targets.**

### 0.2 The status of that derivation

**This is the lab's ranking applied to Sanaa's ruling. It is not her choice of
increment and it does not claim to be.** `docs/LAB_STATE.md` (read at HEAD)
records *"R5/A′ direction after R5C's GATE FAIL (`R5_DECISION_MEMO.md`)"* as
still **on Sanaa's desk**. She may overturn this increment, substitute another,
or stop the line. Under doctrine Part 3 R3 and Charter §22.7 the lab ranks and
argues; it does not choose.

**It re-opens nothing.** It does not re-open R2's ranking and it does not
re-open R3. It runs the class she ratified, on the targets that already stand,
with one registered control added.

### 0.3 Prior art, checked before this file was written (Charter §13)

`../R4_sparta_build/` (the discovered model, its 12 propagations, its NULL and
CEILING comparators), `../R5C_omega_repair/` (the extraction repair, GATE FAIL),
`../Schmelzer2020_SpaRTA/` and `verification/campaign/W2_SPARTA_*` (the frozen
extraction the R4 targets reproduce byte-identically) were all read before
drafting. **No prior artefact answers the question this file asks** — no lane in
this programme has propagated a SpaRTA-class model at a registered, uniformly
applied amplitude on both corrections. R4's `discovered_xi01` arm is the nearest
thing and it is **not** it: it scaled `b^Delta` only, left `R` at full strength,
was added **after** the registered arm diverged, and is `REPORTED, NOT GRADED`
(R4 departure D-7).

---

## 1. THE REGISTERED PREDICTION, BEFORE THE LADDER

**A prediction that cannot miss has no evidentiary content.** Each row below is
a number or an interval, registered before any run, with the reading that
falsifies it. These are predictions, not gates: a falsified prediction is a
**finding**, and it moves no verdict on its own. The gates are §5.

| # | quantity | **PREDICTED** | **FALSIFIED BY** |
|---|---|---|---|
| **P1** | the control strength `xi*` selected by §3.4 | `xi* ∈ [0.02, 0.20]`, point **0.10** | any `xi*` outside `[0.02, 0.20]` |
| **P2** | a-priori families beaten (of 4), gate G1's count | **2**, interval `[1, 3]` | a count of 0 or 4; the point prediction misses at 1 or 3 |
| **P3** | pooled-cell a-priori `b_rms` of the controlled model against R4's uncontrolled model on the same cells | **not lower** (`xi`-scaling cannot beat the pooled OLS optimum) | a pooled `b_rms` lower than R4's by more than 1e-6 relative |
| **P4** | a-priori realisability violating fraction, total `b = b_lin + xi·b^Delta`, at `tol = 1e-6`, on the fit mask | **0.000000 on all 12 cases**, by construction of §3.4 | any case with a non-zero fraction |
| **P5** | of the 12 propagations, the number that CONVERGE under §4's rule | **8**, interval `[6, 12]` | a count outside `[6, 12]`; the point prediction misses at 6, 7, or 9–12 |
| **P6** | `eps(U)/eps(U_0)` on `PHLL10595` and on `CBFS13700` | **> 0.90 on both** | a ratio `<= 0.90` on either |
| **P7** | duct secondary flow, RMS in-plane velocity as % of bulk, on all four training ducts | **> 0.05 %** on all four (a linear EVM gives exactly 0.0000) | any duct at `<= 0.05 %` |

### 1.1 Where each prediction comes from — the reasoning, so it can be attacked

**P1.** The binding constraint on `xi` is the realisable-set boundary. R4
measured `max ||b^Delta_model||_F` at **7.559** on `alpha_10_12000_4048` and
**5.948** on `CBFS13700`, against a realisable bound near
`sqrt(2/3) = 0.816497` (`../R4_sparta_build/artefacts/apriori_realisability.json`;
`RESULTS.md` §4.6). If the extreme-cell norm is what binds,
`0.816497 / 7.559 = 0.108`. The interval `[0.02, 0.20]` brackets that by a
factor of five either way, because the barycentric constraint may bind harder
than the norm and because the truth-relative fraction clause is not a norm
clause. **That the point prediction lands near Schmelzer's own `xi = 0.1` is a
coincidence and is recorded as one** — the paper's value is an ad-hoc remedy for
`b^Delta` only [Schmelzer et al. 2020, preprint p. 13, PAPER-VERIFIED at
`docs/NUMERICS_KNOWLEDGE.md`], and nothing here is derived from it.

**P2.** `b_rms` on the frozen fields is exactly the model's fit error against
its own target, because `b_data = b_lin + b^Delta` holds there identically
(`../R4_sparta_build/score_apriori.py` docstring). The `xi`-family therefore
interpolates two measured endpoints (`artefacts/apriori.json`;
`RESULTS.md` §4.5):

| family | `xi = 0` (linear EVM) | `xi = 1` (R4) | **train-mean bar** |
|---|---|---|---|
| hills | 0.297866 | **0.229615** | 0.258430 |
| ducts | 0.600932 | **0.483897** | 0.368713 |
| `PHLL10595` | 0.279189 | **0.212982** | 0.250098 |
| `CBFS13700` | 0.327812 | **0.376331** | 0.327658 |

Hills and `PHLL10595` are beaten at both endpoints, so a `xi` between them very
probably keeps them. Ducts lose at both endpoints by a wide margin (0.484 and
0.601 against 0.369) and no intermediate `xi` closes that. `CBFS13700` loses at
both endpoints, but **by only 1.54e-04 at `xi = 0`** (0.327812 against
0.327658), and `f(xi) = ||xi·m − t||^2` is a parabola whose minimum lies strictly
below `f(0)` whenever the model has any component along the target — so
`CBFS13700` is the one family that could flip. **Hence 2, with 3 as the live
alternative and 1 as the downside.**

**P3.** R4's coefficients are OLS on the selected support over the pooled
fitted cells (`fs3_select.ols`, departure D-3), so `xi = 1` is the pooled
minimiser of the same loss `b_rms` measures. Any `xi != 1` therefore raises the
pooled figure. This is close to arithmetic; it is registered anyway, because a
prediction that is nearly certain is a **control on the instrument**: if it
fails, the scorer or the model file is wrong, not the physics.

**P4.** §3.4 selects `xi*` as the largest grid value at which the total
anisotropy is realisable on every fitted cell of every training case at
`tol = 1e-6`. A non-zero fraction therefore means the selection did not do what
it says, and the run stops there.

**P5.** The registered convergence rule is §4. Two measured bounds bracket it
(`../R4_sparta_build/RESULTS.md` §5.1):

* **NULL** (zero correction through the identical code path) converges on the
  6 hills, `PHLL10595` and `CBFS13700` — **8 of 12** — and **cap-stops on all
  four ducts** at 20,000 iterations. So "the control is nearly inert" predicts
  **8**, not 12.
* R4's `xi = 0.1` arm (`b^Delta` scaled, **`R` at full strength**) converged
  **all four ducts** (0.8820 / 0.6784 / 0.7476 / 1.0003) and diverged on
  everything else. The pair control damps `R` too, so it is strictly gentler
  than that arm on the flows `R` destabilises.

The two failure directions that push below 6 are: `xi*` small enough that the
ducts revert to NULL's cap-stop, and `xi*` large enough that the hill
instability survives. **8 is the point; `[6, 12]` is the interval.**

**P6.** This is the prediction that says in advance what this experiment is
**not** for. At `xi* ≈ 0.1` the correction is close to inert, and NULL scores
`eps(U)/eps(U_0)` of **0.9999** on `PHLL10595` and **0.9987** on `CBFS13700`
(§5.1 of R4's results). **The registered expectation is that this build answers
"can a SpaRTA-class pair be propagated at all" and answers "no" to "is it
good".** If a ratio comes back at or below 0.90 that is a real, unexpected
result and it is worth more than the rest of the file.

**P7.** The linear EVM produces **exactly 0.0000** secondary flow on all four
ducts; the frozen-field ceiling produces **1.7522 / 1.6440 / 1.4574 / 1.2227**
against DNS **1.7630 / 1.6504 / 1.4622 / 1.2238**; R4's `xi = 0.1` arm produced
**0.1981 / 0.2767 / 0.2498 / 0.2137** (R4 §5.3). Anything strictly above zero
means the anisotropy correction is doing the one thing a linear model cannot.
0.05 % is a tenth of what `xi = 0.1` produced.

---

## 2. ZERO-SHOT DISCIPLINE (Charter §22.3, doctrine R1)

**Training families only. No TEST family and no validation family is opened by
this lane for any purpose.** The split is R4's, unchanged
(`../R4_sparta_build/PREREGISTRATION.md` §0.1, from the benchmark README lines
71–77):

* **TEST — OFF LIMITS:** `alpha_15_13929_4048`, `alpha_15_13929_2024`,
  `alpha_05_4071_4048`, `alpha_05_4071_2024`, `AR_1_Ret_360`, `AR_3_Ret_360`,
  `AR_14_Ret_180`, `NASA_2DWMH`.
* **VALIDATION — not opened here:** `alpha_05_10071_4048`,
  `alpha_05_10071_2024`, `alpha_15_7929_4048`, `alpha_15_7929_2024`,
  `AR_7_Ret_180`.

**The boundary is an assertion in code, not a promise in prose.**
`r4_lib.assert_no_test_case` (path and sha256 in §9) raises on any member of
either set and **is called at the top of every script this lane runs**: the case
builder, the control selector, the runner's manifest read, and the comparator.

**The guard's silence is not trusted until the guard is shown able to speak.**
Every script calls a `guard_is_armed()` control that hands
`assert_no_test_case` a known TEST case (`NASA_2DWMH`) inside a list and
**refuses (exit 2) if the guard does not raise** — the pattern
`make_coverage.py::guard_is_armed` already uses, and it exists because
`assert_no_test_case` takes an iterable: a bare string would intersect
character-by-character and pass everything.

**Nothing is touched per case** (Charter §22.1): one model, one control value,
applied uniformly. **Nothing per family** (see §3.3's refusal).

**Declared prior exposure, carried not hidden.** R4 §0.2 records that earlier
lanes in this programme scored a-posteriori results on `AR_1_Ret_360` and
`AR_3_Ret_360`, which are TEST cases, and that those numbers have been seen.
That declaration is inherited here. **No threshold, exclusion, selection rule or
control value in this file is conditioned on those observations**; every one is
derived from a training-family measurement whose artefact is cited beside it.

---

## 3. THE MODEL, EXACTLY

### 3.1 One model, applied uniformly (Charter §22.1)

The model is **SpaRTA-class**: R4's FS4-frozen term sets, unchanged in form and
in relative coefficient, with **one scalar `xi`** multiplying **every**
coefficient of **both** targets.

```
R        = xi * 2 k [  1.261646025
                     - 42.82547649  I1
                     - 31.54761765  I2
                     + 14.28260064  I2^2 ] (T1:A)

b^Delta  = xi * [ -7.550379605  T2
                 - 16.07577893  I2 T2
                 +  5.039083086  T3 ]
```

Term sets and coefficients are `../R4_sparta_build/MODEL.json` (sha256 in §9),
the FS4 freeze of 2026-08-22. **No term is added, removed or re-selected.** No
term carries `n = 4` (R4 §1: `kOmegaSSTSparta` implements T1, T2, T3 only and
would silently evaluate `n = 4` as `T3`); the builder asserts `n in (1,2,3)`
before writing any case.

`xi` is **ONE number**. The same number multiplies the `R` coefficients and the
`b^Delta` coefficients; the same number is used on every case, in every family,
at every iteration. It is written into `MODEL.md` and `MODEL.json` in this
directory **before any propagation case is built**, and it is not changed
afterwards for any reason.

### 3.2 Why a scalar and not a constrained refit — a design choice, disclosed

The memo's `A′` offers *"a single scalar or a single constraint applied
uniformly"*. **This draft registers the SCALAR.** Reasons, stated so the
supervisor can overrule them before the freeze:

1. It isolates **amplitude** exactly. The term set is R4's, so any change in
   outcome is attributable to magnitude and to nothing else. A constrained refit
   changes the form and the magnitude at once and cannot separate them.
2. It costs no fit (§8), which makes the experiment cheaper than the memo's own
   `A′` estimate rather than more expensive.
3. Its a-priori behaviour is a one-parameter family between two **already
   measured** endpoints, which is what makes P2 and P3 predictable in advance.
   Prediction-first is easier to honour on a design whose endpoints exist.

**What is given up, named:** a constrained refit could in principle find a form
that is realisable *and* accurate, which a rescaling cannot. This build cannot
distinguish "no SpaRTA form of this library propagates" from "this particular
form does not propagate at any amplitude", and §11 says so.

**If the supervisor prefers the constrained refit**, the memo's
`2 x 0.262 = 0.524 core-h` fit line returns to §8 and P2/P3 must be re-derived
before the freeze. That is an amendment **before first compute** and is legal
only with the condition stated and checked (CLAUDE.md rule 2).

### 3.3 REGISTERED REFUSAL — a per-family or per-case scaling is not a model

> **A control value chosen per family, or per case, is per-case switching.
> Charter §22.1 says that is not a model, and this lane refuses it in advance.**

If the record of this build were ever to read *"it converges with `xi_duct` and
`xi_hill`"*, **there is no model — there are two**, and the one-model doctrine is
the thing this build exists inside. Registered consequence: **any outcome
reached by using more than one control value is `NOT A RESULT`**, whatever the
numbers say (§7, failure mode F2).

The same refusal covers a value that varies with iteration, with mesh region,
with a switch on any local quantity, or with anything else. `xi` is one number
in `MODEL.json` and the solver reads it once, folded into the coefficients.

### 3.4 HOW `xi` IS CHOSEN — entirely from TRAINING-family measurements, before any propagation

**Registered, and this is the clause the whole build turns on.**

`xi*` is the **largest** value on the registered grid at which the model's total
anisotropy is realisable on **every fitted cell of every one of the 12 training
cases**:

```
xi* = max { xi in G : for every training case c, for every cell in mask(c),
            b_total = b_lin + xi * b^Delta_model(c)
            is realisable at tol = 1e-6,
            and max_cell ||b_total||_F <= sqrt(2/3) = 0.8164966 }
```

with, registered now:

* **the grid** `G = {0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30,
  0.50, 0.70, 1.00}` — twelve values, fixed here, not refined afterwards;
* **the cell mask** `mask(c)` is EXACTLY R4's fit mask, re-used unmodified:
  `k_LES_shipped > 0` and finite in every candidate and every target
  (`fs3_select.py` lines 89–90), which selects **172,106 of 172,171** cells and
  drops **65 (0.038 %), all hills** — reproduced independently by
  `make_coverage.py` and by `RESULTS.md` §3.3;
* **the fields** are the **frozen** fields (`U = U_LES`, `tau = 1/omega`,
  `S = (tau/2)(A+A^T)`, `Omega = (tau/2)(A−A^T)`), the conventions
  `kOmegaSSTSparta` itself uses and the fields the regression actually fitted —
  **not** the baseline RANS fields;
* **the realisability test** is `_common/of_read.realisability_violation`
  (Schumann barycentric coordinates, all three `>= -tol`), re-used unmodified;
* **`b_lin`** is the frozen dataset's own `b_lin` column, the same one
  `score_apriori.py` reads.

**If no grid value is feasible, `xi* = 0` is not used and the lane stops with
`BLOCKED`** (§5, and see §7 F4) — a zero control is the linear EVM and would
propagate nothing.

**What this selection may NOT see, registered:** `xi*` is chosen on
**realisability alone**. It is not chosen on `b_rms`, not on any a-posteriori
quantity, not on convergence, and not on any test or validation case.
**Selecting `xi` on `b_rms` would be calibration on the quantity gate G1
grades**, and selecting it on convergence would be R4's departure D-7 with a
registered wrapper on it. Both are refused (§7, F1).

### 3.5 The freeze order — mechanically enforced

1. `select_control.py` runs, reads only training frozen fields, writes
   `MODEL.md` and `MODEL.json` **in this directory**, containing `xi*`, the full
   grid, the feasibility result at every grid value, and the binding case and
   cell.
2. `MODEL.md` and `MODEL.json` are **committed** (commit 2 of §10).
3. Only then does `build_r4b_cases.py` run. It **refuses (exit 2)** unless
   `MODEL.json` exists, carries a `frozen_at` timestamp, and hashes equal to the
   committed blob. **No propagation case can be built before the control value
   is on the record.**

---

## 4. THE COMPLETION AND CONVERGENCE RULES — REGISTERED UP FRONT, IN FULL

**R4 added a completion condition AFTER first compute (its departure D-4).
That must not recur.** Both rules below are registered here, complete, before
any run, and neither is extended afterwards.

### 4.1 The six-condition completion rule for a frozen EXTRACTION

Not exercised by this build — this lane re-uses R4's 12 standing targets and
**extracts nothing** — but registered because §6 re-verifies those targets and
because R5C's registration of the same rule is the precedent. A frozen
extraction is COMPLETE only if all six hold (`r4_lib.frozen_complete`, re-used
unmodified, sha256 in §9):

1. recorded `rc = 0`;
2. an `End` line in `log.frozen`, and **no `NOT CONVERGED` line**;
3. the last time directory equals the iteration the solver says it wrote at
   (`Writing fields at iteration N`) — **not** `controlDict`'s `endTime`, which
   is only the backstop cap;
4. every required field present in that directory — `U`, `k`, `omega`, `nut`,
   `bijDelta`, `kDeficit`, `bijData`, `grad(U)`;
5. every one of those fields **NEWER than the case's own `0/`** — the **age
   guard** (CLAUDE.md rule 4): `0/` is touched last at build, so it dates the
   run allowed to produce the answer — and the solver's own settle verification
   marked `[SETTLED]`;
6. **`omega` never bounded before the field write** — `bounding omega` count
   `== 0`. *"`omega` bounded before the field write => INCOMPLETE."*

### 4.2 The completion rule for a PROPAGATION run — this build's own

A propagation run is **COMPLETE** only if all of:

1. recorded `rc = 0` in `<case>/<cfg>/rc`;
2. an `End` line in `log.solve`;
3. **the last time directory equals `endTime` in `controlDict`**, OR the log
   carries `SIMPLE solution converged` (the registered `residualControl 1e-6`
   stop) and the last time directory equals the iteration at which it converged;
4. every required field present in that directory: `U`, `p`, `k`, `omega`,
   `nut`;
5. **every one of those fields NEWER than the case's own `0/U`** — the age
   guard, CLAUDE.md rule 4, applied to the propagation case as well as to the
   extraction;
6. the log carries **no `Foam::sigFpe::sigHandler` frame**. *(The banner line
   every OpenFOAM log opens with contains the phrase "Floating point
   exception", so matching that phrase marks every run diverged, healthy ones
   included. The handler frame is the signature of an actual trap —
   `score_aposteriori.log_facts` already encodes this and it is re-used.)*

### 4.3 CONVERGED, and it is narrower than COMPLETE

A run **CONVERGED** only if it is COMPLETE **and** its log carries
`SIMPLE solution converged` — i.e. it reached the registered
`residualControl 1e-6` on `U`, `p`, `k`, `omega`. **A cap-stop is NOT
converged**; it is recorded as `cap-stop/stagnant` with its iteration count.
This is the count P5 predicts and the count G2 grades.

**A guard refuses a case whose destination directory already holds a `0/` or a
numeric time directory.** No run is resumed in place, restarted in place, or
re-graded after the fact. A run already meeting §4.2 is **skipped, never
re-run**; nothing is ever killed to save budget (Charter §18, and R4's D-6 is
the disclosed exception that proves the rule).

---

## 5. THE GATES — registered now, before any run

**Every gate below can FAIL.** A quantity reported with no bar is named as
reported-not-graded and is not called a gate (R4's G4 and G5 carried no bar;
`RESULTS.md` §11.7 item 1 and §12.2 record both).

Verdict vocabulary: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING`, and nothing else (§12).

### G0 — PLANTED-ZERO CONTROLS. Runs FIRST, before any gate is graded

CLAUDE.md rule 3: *a zero from a reader that has not been shown able to see a
non-zero is not evidence.* **Every reader that could return a zero plants a
known perturbation, reads it back from disk with the same reader that produces
every reported number, and REFUSES (exit 2) if it cannot see it.**

| control | what is planted | into what | refusal |
|---|---|---|---|
| **G0a** field reader, control selection | `PLANT = 1.234e-03` | a scratch copy **on disk** of a real `bijDelta` from a frozen case | exit 2 |
| **G0b** field reader, a-priori scoring | `PLANT = 1.234e-03` | scratch copy of `bijDelta` | exit 2 |
| **G0c** field reader, a-posteriori scoring | `PLANT = 1.234e-03` | scratch copy of `U` from a benchmark case | exit 2 |
| **G0d** field reader, continuity | `PLANT = 1.234e-03` | scratch copy of a written `grad(U)` | exit 2 |
| **G0e** realisability reader | a cell forced to a **known non-realisable** anisotropy (a barycentric coordinate driven to `-1e-3`) | scratch copy of the total-`b` array | exit 2 unless the violating count rises by **exactly one** |
| **G0f** zero-shot guard | `NASA_2DWMH`, inside a list | `assert_no_test_case` | exit 2 unless it raises |

The tolerance for G0a–G0d is `r4_lib.planted_zero_reader_check`'s, re-used
unmodified: the bar is `max(1e-12, 8 * eps * max|field|)` **and** the median
recovery must match the plant to `1e-9` relative. It is magnitude-aware for the
reason R4 recorded as departure D-9 — an absolute `1e-12` bar refused a
demonstrably correct reader on a field reaching `2.8e+06`.

**G0e is new to this build and is the one the realisability gate needs.** A
violating-fraction of `0.0000` is exactly the kind of zero rule 3 exists for:
without a planted non-realisable cell, a broken barycentric routine and a
perfectly realisable model return the same number.

**Verdict:** any G0 control failing → **`NOT A RESULT`**, and the lane stops.
The comparator is not evidence.

### G1 — A-PRIORI, against the TRAIN-MEAN TENSOR (Charter §3, §2c)

> The controlled `b^Delta` must beat the **TRAIN-MEAN constant tensor** on
> training-family `b_rms`. The train-mean constant beats k-omega SST on **8 of
> 8** held-out cases (`_common/BASELINES.md` §6.4), so **SST is not the bar and
> is not quoted as one**. **`PASS` requires the controlled model below
> train-mean `b_rms` on `>= 3` of the 4 training families**, else **`GATE
> FAIL`**.

Identical to R4's registered bar, deliberately, so the two builds are
comparable. Baseline: `_common/trainmean_baseline.json`
(`b_mean = [[0.1756, -0.0382, 0.0018], [-0.0382, -0.1479, -0.0006],
[0.0018, -0.0006, -0.0276]]`, `BASELINES.md` §6.4). **Both** train-mean columns
are reported — this lane's own fitted cells and the shipped constant — as R4
did, and the verdict is taken on **this lane's cells**, the mask of §3.4.

Reported beside it and **NOT the bar**: the linear EVM (`xi = 0`) and `b = 0`.

**For a velocity claim the baseline is uncorrected RANS** (Charter §3), which is
the shipped baseline field `eps(U_0)` of G3 — never the train-mean tensor, and
never SST's anisotropy.

### G2 — A-POSTERIORI PROPAGATION: does it propagate at all

> **`PASS` requires all 12 propagations COMPLETE and CONVERGED** under §4.2 and
> §4.3. **`GATE FAIL` if any propagation diverges, or stagnates without meeting
> the convergence rule.**

Intermediate: **`GATE REACHED`** if `>= 8` of 12 converge but not all 12 —
registered as an intermediate threshold because "the pair can be propagated on
two thirds of the training set" is a different statement from "it propagates"
and from "it diverges on all twelve", and the ladder should be able to say so.
Below 8 converged: **`GATE FAIL`**.

### G3 — A-POSTERIORI ACCURACY, on the two cases with a directly comparable per-case ceiling

> `eps(U)/eps(U_0) <= 0.6` on **`PHLL10595`** and **`CBFS13700`**, else
> **`GATE FAIL`**.

`eps(U) = mean_c |U_c − U_LES,c|^2` over the three components, unweighted over
the whole internal field — the W2 primary convention, the same one R4 used, and
`eps(U_0)` is the same quantity on the **shipped baseline** field (uncorrected
RANS, Charter §3).

**If a case produced no written solution, no `eps` is computed for it** and the
row reads `DIVERGED (iteration N)`. See F3 in §7: reading `eps(U)` off a run
that wrote no time directory returns the shipped baseline at a ratio of exactly
`1.0000`, which looks physical and is not.

### G4 — CONTINUITY, NON-DIMENSIONAL (memo §4 amendment candidate 2, applied here for the first time)

**The defect this repairs, quoted from the memo:** *"`sum local div(U)` carries
dimensions; the ducts run at a bulk velocity of ~37.5 m/s on a 1 mm half-height
and the hills at ~1 m/s, so one absolute threshold does not mean the same thing
on the two families."* It is what made `AR_1_Ret_180`'s CEILING row **NOT
CONVERGED** at `1.0628e-04` while every hill row passed at `<= 3.45e-07`.

**Registered non-dimensional form**, and it is the lab's own published standard
(Charter §7: *"volume-weighted RMS `div(U)` relative to the field's own gradient
scale"*):

```
eps_cont = RMS_vol( div U ) / RMS_vol( ||grad U||_F )
```

both computed from the **same written `grad(U)` field** at the run's last time
directory (`div U = tr(grad U)`), volume-weighted over the internal field. It is
dimensionless by construction and needs no per-case reference velocity or
length, so nothing in it can be chosen after the fact.

**Registered threshold: `eps_cont <= 0.5 %` (5.0e-03), else NOT CONVERGED
whatever the velocity error.**

**Its basis is a measurement the lab published against itself**, quoted in
Charter §7 from `Certonomous_closure_challenge/description/METHOD.md` §6.2:
the **underlying RANS** fields run at **0.08 % to 0.47 %** on this exact
statistic, and the lab's own post-hoc corrected hills at **10.5 %** and
**9.7 %**. A **re-solved** field (Charter §22.2 makes re-solving a design
constraint here) has no excuse to sit outside the band an uncorrected RANS
already achieves. **0.5 % is the top of that measured band.**

**Reported beside it and NOT graded:** the dimensional `sum local` from the
solver log, with R4's `1e-4`, so the two files stay readable against each other.

> **This re-grades NO R4 row.** R4's G3 is graded as written and
> `AR_1_Ret_180`'s CEILING row stands **NOT CONVERGED** (Charter §11). Nothing
> in this file touches `../R4_sparta_build/`.

### G5 — THE REALISABILITY GATE (Charter §4) — frozen before the run, in the charter's own wording

> **`NOT A RESULT` if the predicted `b` is non-realisable in more than `3x` the
> truth's own violation fraction on the same cells, or if `max ||b||_F` exceeds
> `sqrt(2/3)` by more than a factor of `2`, regardless of RMSE.**

Registered numerically:

| quantity | threshold |
|---|---|
| violating fraction of the predicted total `b` | `> 3 x` the truth's own fraction **on the same cells** → `NOT A RESULT` |
| `max ||b||_F` of the predicted total `b` | `> 2 x sqrt(2/3) = 1.6329932` → `NOT A RESULT` |
| tolerance | `tol = 1e-6` on the barycentric coordinates, for **both** the model and the truth, on the same cells, by the same routine |
| cell mask | §3.4's mask exactly — R4's fit mask, `172,106` cells — for the a-priori read; the run's own internal field for the a-posteriori read |
| `b` | the **TOTAL** anisotropy: a-priori `b_lin + xi·b^Delta_model`; a-posteriori the solver's own `tauijRecon` reduced by `b = tau/(2k) − I/3` with `k = tr(tau)/2`, i.e. **the stress the momentum equation actually saw** |

**Read in two places, and both are registered:**

* **G5a, a-priori**, on the frozen fields. Predicted `0.000000` on all 12 by
  construction (P4).
* **G5b, a-posteriori**, on `tauijRecon` at the last written time directory of
  each converged run. **This is where the gate can genuinely fire**, because the
  model is re-evaluated from the current solution every iteration and the
  anisotropy that is realisable on the frozen fields need not stay realisable on
  the solved ones.
* **Registered branch for a case with no written field:** G5b is **not
  gradable** on that case, it is recorded as `not gradable — no solution
  written`, and the case's failure is graded by **G2**. **A missing field is
  never read as a pass.**

**On the four ducts and on `PHLL10595` the truth's own violating fraction is
exactly `0.00000`** (`../R4_sparta_build/RESULTS.md` §4.6), so `3 x 0 = 0` and
**the bar on those five cases is literally zero violating cells.** That reading
is registered here explicitly so nobody has to decide it later. On the hills the
truth violates at `0.01270`–`0.01385`, so the bar is `0.0381`–`0.0416`; on
`CBFS13700` the truth violates at `0.03648`, so the bar is `0.10944`.

### G5.1 — What R4's model would have scored against this gate, and why that matters

**R4's §6 registered NO bar on realisability**, so its gate **G4 could not
fail** — `RESULTS.md` §6 states it in those words, and §11.7 item 1 carries it
forward as amendment candidate 1. **That candidate is applied here for the first
time.** Measured (`../R4_sparta_build/artefacts/apriori_realisability.json`;
`RESULTS.md` §4.6), R4's discovered model on the total `b_lin + b^Delta`:

| case | model violating fraction | truth's own | `3 x` truth = the bar | against this gate |
|---|---|---|---|---|
| `CBFS13700` | **0.19062** | 0.03648 | 0.10944 | **NOT A RESULT** |
| `AR_1_Ret_180` | **0.06790** | 0.00000 | 0.00000 | **NOT A RESULT** |
| `AR_3_Ret_180` | **0.05704** | 0.00000 | 0.00000 | **NOT A RESULT** |
| `AR_5_Ret_180` | **0.05197** | 0.00000 | 0.00000 | **NOT A RESULT** |
| `AR_10_Ret_180` | **0.04423** | 0.00000 | 0.00000 | **NOT A RESULT** |
| the six hills | 0.00077–0.00199 | 0.01270–0.01385 | 0.0381–0.0416 | passes |
| `PHLL10595` | 0.00000 | 0.00000 | 0.00000 | passes |

and `max ||b^Delta_model||_F` reached **7.559** on `alpha_10_12000_4048` and
**5.948** on `CBFS13700`, against `sqrt(2/3) = 0.8164966`.

**Honest scoping of that last figure:** R4 reported the norm on `b^Delta`
**alone**; this gate's norm clause is registered on the **total** `b`, which R4
did not measure. So the 7.559 is comparable to this build's `max ||xi·b^Delta||_F`
column and **not** to its gate column. Both columns are reported so the
comparison is never made across quantities by accident.

**Charter §4 exists because `Ling2016_TBNN` was on track for a PASS in exactly
that configuration** — 6.47–15.34 % of test cells outside the barycentric
triangle against a truth of 0.79 %, at `||b||_F ~ 1.48e+07`. R4 repeated the
omission and said so. **This file does not.**

### G6 — STRUCTURE, with bars (R4's G5 carried none; §12.2 records that as a defect)

**G6a — duct secondary flow.** RMS in-plane velocity as % of bulk, the
registered instrument `score_aposteriori.secondary_flow_pct`. **`GATE REACHED`
if all four training ducts exceed `0.05 %`**, else **`GATE FAIL`**. A linear EVM
gives **exactly 0.0000** on all four (R4 §5.3) — this is the one structure a
`b`-correction can make and a linear model cannot.

**G6b — reattachment.** Bottom-wall reattachment by the registered instrument
`_common/sst_baseline_metrics.py::hill_wall_metrics` (longest-reversed-run
criterion, the same row and criterion for every configuration and for the LES).
**`GATE REACHED` if, on `>= 4` of the 7 separated training cases that converge,
`|x_reatt_model − x_reatt_LES| < |x_reatt_BASE − x_reatt_LES|`** — the model
moves the bubble **toward** the LES — else **`GATE FAIL`**. The shipped baseline
over-predicts the bubble by **39–100 %** and the frozen-field ceiling lands
within **0.9–3.4 %** (R4 §5.3), so both endpoints are measured and the bar sits
between them.

> **Disclosure on G6's numbers.** `0.05 %` and `4 of 7` are **new bars, chosen
> by this lane from the R4 record's measured spread**, with the reasoning shown
> above. They are not read off any prior registration. They are registered here
> **before any run**, which is what makes them legitimate; the supervisor may
> move them before the freeze and may not move them after.

### G7 — THE COMPARATOR IDENTITY (the NOT A RESULT branch, re-used not re-fired)

R4 registered: `NOT A RESULT` if the per-case frozen-field ceiling fails to beat
NULL by 30 %. **That branch was answered and did not fire** — the ceiling beat
NULL by 60.2 % on `CBFS13700`, 99.6 % on `PHLL10595` and 99.99 % on
`AR_5_Ret_180`, on all eleven cases where it converged. §6 registers the
comparators as **re-used**, so the branch is not re-fired; what IS registered is
the condition under which the re-use is void (§6.3).

---

## 6. COMPARATORS — RE-USED, EACH NAMED WITH ITS ARTEFACT PATH AND ITS HASH

**Never ambiguous** (memo §3A requirement 4). Every comparator below is
**re-used from R4** — not re-run — and is named by path and sha256, verified
`disk == HEAD` at the time this draft was written (2026-08-24).

### 6.1 The measured comparator artefacts

| comparator | artefact | sha256 |
|---|---|---|
| **NULL** and **CEILING**, all 12 cases, `eps(U)`, iterations, continuity, realisability, structure | `../R4_sparta_build/artefacts/aposteriori.json` | `4ae78930cfb95efe1de0893257015429078f9a54e44129f3324d6a25b88a9d88` |
| a-priori family scores, all four baselines | `../R4_sparta_build/artefacts/apriori.json` | `727456dc1469c18f080c916dddeaa883a7d01348312349971cfe4c1bbba70cbe` |
| a-priori realisability, model vs truth vs linear EVM, per case | `../R4_sparta_build/artefacts/apriori_realisability.json` | `adc4138f3d6426a1d00f7eee59a7d3c46ab5304bfa91db25397eda3bc2d71344` |
| the 27-case frozen completion inventory (the 12 that stand) | `../R4_sparta_build/artefacts/frozen_inventory.json` | `66d37434934e071b284721343b48700b60d44a92b3e660319f17f8d341335e7f` |
| the candidate-library manifest and fit mask accounting | `../R4_sparta_build/artefacts/dataset_manifest.json` | `6636a473bb78f669a687c6cbd25b13487edc4d7c41a5b5ff462efe5f1d1d0b53` |
| FS2/FS5 coverage of the selected columns | `../R4_sparta_build/artefacts/coverage.json` | `575d908397481738582554eebe38381d0602059b5ff378d2cb9cbdbf515e9540` |
| the FS4 freeze this build scales | `../R4_sparta_build/MODEL.json` | `f630fcc3bd00b5f27913f6bef8a1194468771c47561ac30c9fc28a5f11fa1a46` |

### 6.2 The bulk run directories behind them — verified present, not committed

Checked present and readable while this draft was written; the ceiling and NULL
runs carry `rc = 0`, a recorded `wall_seconds` and their written time
directories (e.g. `PHLL10595/null` at `489`, `PHLL10595/ceiling` at `3513`,
`CBFS13700/ceiling` at `30000`, `AR_1_Ret_180/null` at `20000`):

* `/home/ubuntu/closure-data/r4/aposteriori/<case>/{null,ceiling}/` — 24
  directories, the measured comparators;
* `/home/ubuntu/closure-data/r4/frozen/<case>/` — the 12 standing targets;
* `/home/ubuntu/closure-data/r4/dataset/<case>.npz` — the candidate library.

### 6.3 REGISTERED CONDITION ON THE RE-USE — and it can fail

The comparator step **re-hashes every artefact in §6.1 before quoting any number
from it**. If any hash differs from the value in this table, the comparator
**REFUSES (exit 2)** and the affected comparator is **re-run from scratch under
this build's own budget** and reported as a re-run, never as a re-use.
Likewise, if any of the 24 run directories in §6.2 is absent, the comparator for
that case is **re-run, not inferred**.

**No comparator number is ever carried in prose from a record.** Every one is
read from the hashed JSON by the comparator at grading time.

### 6.4 The CEILING is the control, and what it is NOT

> **The ceiling reads `bijDelta` and `kDeficit` EXTRACTED FROM THE LES/DNS
> TRUTH** by `kOmegaSSTFrozen` and injected as static fields by
> `kOmegaSSTCorrected` at `RScale = bScale = 1`. **It predicts nothing. It is an
> upper bound available only when the answer is already known.** It is not a
> model, it is not this build's model, and no sentence in any record of this
> build may present it as one.

Registered so it cannot slide: a surface reading *"our closure recovers
reattachment to within 3.4 % of the LES"* without saying the correction was
extracted from the DNS has made exactly the claim R4's boundary report
(`RESULTS.md` §11.2) exists to prevent, and this build inherits that prohibition
by name.

**NULL** is `kOmegaSSTSparta` with **empty** `RTerms` and `bDeltaTerms` — zero
correction through the **identical code path**, not stock `kOmegaSST`. It
reproduces the shipped baseline to `<= 1e-5` relative on the hills,
`PHLL10595` and `CBFS13700` (`NULL − BASE`, N-B22/N-B23), and **it does not on
the ducts**, where it stagnates at 1.003 to **1.239** times the shipped baseline
error at the 20,000 cap. That gap is on the record and every duct ratio this
build quotes carries it.

---

## 7. THE FAILURE MODES THAT MAKE THIS **NOT A RESULT** — named in advance

**F1 — the control strength is chosen AFTER seeing a propagation outcome.**
That is calibration on the graded quantity, not discovery. **The worked example
is R4's own departure D-7:** `xi = 0.1` was a post-hoc, ungraded diagnostic
precisely because it was reached for **after** the registered arm diverged on
all twelve cases. §3.4 fixes `xi*` from realisability on training frozen fields
alone, §3.5 makes the ordering mechanical, and the `MODEL.json` commit
timestamps it. **If `xi` is changed after any propagation result is read, the
build is `NOT A RESULT`.**

**F2 — a scaling tuned per family to buy convergence.** *"It converges with
`xi_duct` and `xi_hill`"* means **there is no model — there are two**, and
Charter §22.1 says per-case switching is not a model. Registered refusal at
§3.3. **`NOT A RESULT`.**

**F3 — reading `eps(U)` off a run that wrote no time directory.** `latest_time`
returns `0`, `0/U` is the shipped baseline, and the ratio comes back at exactly
**1.0000**, which looks physical and is not. **The first draft of R4's own table
did report those 1.0000s.** `score_aposteriori.py` refuses this — it computes no
`eps` unless `float(latest_time) > 0` and marks the row `DIVERGED` with the
iteration it died at — **and that refusal carries forward into this build's
comparator, unmodified.** A row that reports a ratio from an unwritten solution
makes the whole table `NOT A RESULT`.

**F4 — no feasible `xi` on the registered grid.** Then the lane reports
**`BLOCKED`** (not `NOT A RESULT`, and not a silently widened grid): the
registered instrument found no admissible control and the acquisition path is a
new pre-registration with a different control family. **Refining the grid after
seeing it fail is F1.**

**F5 — a comparator quoted from prose rather than read from its hashed
artefact**, or a re-used comparator whose hash does not match §6.1 and which is
quoted anyway. **`NOT A RESULT`** for every row that depends on it.

**F6 — a planted-zero control that does not refuse.** If any G0 control is
found to pass on a deliberately broken reader, every zero this build reports is
unsupported. The comparator therefore proves the **refusal path live** — it runs
a mutated reader as a subprocess and requires `rc = 2` — and not merely the
control path (the pattern proven in `_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`
§2). **`NOT A RESULT`** if a mutation does not refuse.

**F7 — grading a test or validation case.** Impossible by §2's asserted guard,
registered as a failure mode anyway. **`NOT A RESULT`**, and the scoring call is
Sanaa's alone.

Any §7 failure mode observed **overrides a PASS and never converts a `GATE FAIL`
into a PASS** (R5C §3.1 rule 4, adopted here).

---

## 8. FS2 AND FS5 — BOTH STANDING GATES, BOTH ARMED (Charter §22.5)

### 8.1 FS2 — armed, per family, BEFORE any training

> *"Before any training, and per family: per-feature variance, range coverage
> and feature-matrix rank. Anything algebraically zero or near-constant is
> flagged BEFORE training, and a coverage report ships with every model."*

**The instrument, named by path and sha256:**

| instrument | path | sha256 |
|---|---|---|
| coverage generator | `../R4_sparta_build/make_coverage.py` | `f8c40810349c1caf5d633797d4e8d3f703a5a6b53de11c9f8b49010f82a6adb6` |
| FS2 audit | `../_common/features/fs2_audit.py` | (re-hashed at freeze; the D476 amendment is landed, `FS5_D476_CLIP_REPAIR_RESULTS.md`) |
| feature builder | `../_common/features/build_features.py` | (re-hashed at freeze) |
| standing FS2 record | `../_common/features/FS2_DEGENERACY_REPORT.md` | (re-hashed at freeze) |

**What this build fits:** nothing. The term set is R4's FS4 freeze and no
selection is re-run, so FS2's "before any training" clause is discharged by the
record that already exists and is **re-verified, not re-derived**:

* per-family rank of the 110-feature library — hills **100/110** (22 dead),
  ducts **96/110** (48 dead), `PHLL10595` **100/110** (30 dead), `CBFS13700`
  **100/110** (25 dead), pooled **100/110** (12 dead), condition numbers
  `5.4e17` / `1.7e33` / `2.2e17` / `2.0e18` (`FS2_DEGENERACY_REPORT.md` §1;
  R4 §2.2);
* the **12 pooled-training dead features** are excluded from every fit and are
  listed by name in that record;
* per-cell rank of the **selected** tensor set `{T1, T2, T3}` on the fitted
  cells: **3 in 172,106 of 172,106**, pooled `sigma1/sigma3` **20.81 / 1.634e+04
  / 4.430e+07** (p50/p99/max) — `../R4_sparta_build/COVERAGE.md` §3,
  `coverage.json` hashed at §6.1. **The ratio is never quoted without the
  rank.**

**A coverage report ships with this model.** `COVERAGE.md` in **this** directory
is registered as a **deliverable of commit 2**, alongside `MODEL.md`, and it
carries the `xi`-scaled model's own numbers plus §8.2's FS5 declaration. **It
ships with the model or the model does not ship** — see §8.3.

### 8.2 FS5 — armed, and THE FACTOR IS DECLARED HERE, IN ADVANCE, AS A NUMBER

> *"Every feature's test-family range is checked against its training range.
> Beyond a declared factor the response is retrain-coverage expansion, or
> explicit documented acceptance."*

**THE DECLARED FACTOR IS `F = 1.25`.**

Applied, per selected feature `f` (`I1`, `I2`, `I2^2`, `||T1||_F`, `||T2||_F`,
`||T3||_F` — the six columns `COVERAGE.md` §1 tabulates):

```
for a feature whose pooled TRAINING maximum is positive:
    trigger if   (family max) / (pooled training max)   >  F
for a feature whose pooled TRAINING minimum is negative (I2 is non-positive):
    trigger if   (family min) / (pooled training min)   >  F
```

**Its basis is the only measurement in this lab that separates a win from a loss
on this axis**, and it is quoted rather than invented: the round-5 diagnostic
measured the trap on the **unclipped** wall-distance Reynolds number at
**1.85x** and **2.07x** its trained maximum on the two ducts the entry was
**losing**, against **0.90x** on the one it **won**
(`research/closure/md/CLOSURE_CHALLENGE_STATUS.md`:418–423, quoted in docket
**D476** and in `../R4_sparta_build/COVERAGE.md` §6). **`F = 1.25` sits between
the observed win at 0.90x and the observed losses at 1.85x**, so the factor can
fire on the losses and does not fire on the win. It is registered **before any
compute** and it is not moved afterwards.

**The two permitted responses, named before the run:**

1. **retrain-coverage expansion** — bring the out-of-range family (or a family
   that covers its range) into the training set and re-derive, as a **new**
   pre-registration; or
2. **explicit documented acceptance** — the exposure proceeds with the excursion
   named, its factor quoted, and the prediction labelled OUT-OF-FAMILY under
   Charter §5, its score **not pooled** with in-family scores.

**No third response exists, and "the number looked fine" is not one.**

**What FS5 discharges IN THIS BUILD.** This build opens no test family, so the
test-vs-training half cannot execute here. What executes here is the **same
factor applied leave-one-family-out inside the training set** — each of hills /
ducts / `PHLL10595` / `CBFS13700` checked against the pooled range of the other
three, at `F = 1.25`, against `COVERAGE.md` §2's measured in-training reference
of **0.0011 % / 0.0905 % / 0.0000 % / 0.2238 %** of held-out cells outside on at
least one selected feature. **A training family that trips `F = 1.25` against
its own siblings is a finding about the training box and is reported as one.**

**The clipped-feature clause (D476, and the lift is effective).** The check runs
on the **unclipped companion column** wherever one exists — `q1_wallRe_raw`,
landed by the D476 repair (`../_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`;
gates A1/A2/A4 **PASS**, A3 **GATE FAIL** and referred), whose adoption block was
lifted conditionally as **D491** and whose condition was **MET** at `f536b114`
(`docs/LAB_STATE.md` at HEAD). Scope, carried unchanged: the companion is an
**audit-side diagnostic only**, never in `F`, never a feature, never a
correction, and `singular_value_ratio_first_to_last` is **not quoted as a
number** in this build. **A clipped feature with no companion is DECLARED
EXEMPT and named in `COVERAGE.md`** — because an above-maximum excursion on a
saturated column is invisible by construction, and an instrument that cannot see
a thing must say so rather than report a clean zero.

### 8.3 THE R4 DISCHARGE FAILURE, RECORDED, AND WHAT THIS BUILD OWES

**R4's per-build FS5 discharge WAS NOT MET.** Docket **D475**. R4's frozen §7
registered `COVERAGE.md` to ship with `MODEL.md`; **it did not ship**, the
strings `FS5` and `coverage` appear **zero times** in R4's 1,313-line v1.0
`RESULTS.md` (control: `FS2` appears six times under the same grep), the
non-delivery is disclosed in **none** of departures D-1…D-13 and in none of the
ten "cannot see" bullets. It was found on 2026-08-23 by the R5 discharge-record
lane and verified personally by the closure supervisor.

**The supervisor's ruling, quoted as such and not paraphrased:**

> **FS5's per-build discharge for R4 WAS NOT MET — the standing gate re-arms.
> The late delivery below discharges the deliverable, not the disclosure duty,
> which stays on record as breached.**

**And the deeper finding:** FS5's *"declared factor"* had, at that date, **never
been declared by any build in this lab — stated three times, met zero times**
(`CLOSURE_LINE_RESTART_DOCTRINE.md`:252; `CLOSURE_MODELLING_CHARTER.md`:822 and
:827). `COVERAGE.md` §5 declined to invent one after the fact, correctly, because
a threshold chosen after the coefficients exist and after the verdict is on the
docket is exactly what pre-registration exists to prevent.

**This build must meet it, and §8.2 is the first declaration.** Registered
consequences:

* `COVERAGE.md` in this directory is a **deliverable of commit 2** — the same
  commit as `MODEL.md`, not a later one;
* **if `COVERAGE.md` is absent at the time any propagation case is built, the
  builder REFUSES (exit 2)**. R4's failure mode was that nothing checked; here
  something does;
* the non-delivery of any registered deliverable is a **departure disclosed in
  the departures section, at the time**, not in a later addendum.

---

## 9. THE INSTRUMENTS — re-used by path and sha256, not copied

**A script that produces, grades or aggregates a measured number is read by the
supervisor as a DIFF before its output is believed.** Every re-used instrument
below is unmodified; each is verified `disk == HEAD` and re-hashed at the freeze
commit and again at grading, and the comparator **refuses** on a mismatch.

| instrument | path | sha256 (2026-08-24, `disk == HEAD`) |
|---|---|---|
| registry, case builders, `assert_no_test_case`, `frozen_complete`, `run_complete`, `planted_zero_reader_check`, `set_libs` (L-221) | `../R4_sparta_build/r4_lib.py` | `23f37c0c2f296bc82e2dd48aeb68ac5baaffa25d8beb3c119430eadcbcf81fe0` |
| propagation case builder (`build()` re-used; `main()` is not) | `../R4_sparta_build/build_aposteriori.py` | `7c1150c5aad67252aeb1fbacf945809bce7bb386b0cbb7dfbdeaacbcce77e4dd` |
| a-priori scorer, G1 | `../R4_sparta_build/score_apriori.py` | `b034c9ef6214ba9c56f11f0145e29a96928320e9693ff73fe3e9e9dc26b04da2` |
| a-posteriori scorer, G2/G3/G5b/G6 | `../R4_sparta_build/score_aposteriori.py` | `6dc3cce2ce00f7d3d7bbda45f528bea6c9023a528babad19ed09f9ec21aa099c` |
| FS3 selection — **NOT re-run**; its fit mask (lines 89–90) is re-used and its output is the frozen `MODEL.json` | `../R4_sparta_build/fs3_select.py` | `287e03d9f2c7b477a79a45f70ca6b18c4284969cff05b5b3786158d4b51e02e4` |
| coverage generator, FS2/FS5 | `../R4_sparta_build/make_coverage.py` | `f8c40810349c1caf5d633797d4e8d3f703a5a6b53de11c9f8b49010f82a6adb6` |
| solver/Python cross-check (IC1) | `../R4_sparta_build/ic1_check.py` | `342ac8ce735c6035e9e770abfa73e8b72eaace2a0d94a25e4ac8d1ac7e7282a0` |
| field reader, barycentric realisability, structured gradients | `../_common/of_read.py` | (re-hashed at freeze) |
| reattachment and secondary-flow instruments | `../_common/sst_baseline_metrics.py` | (re-hashed at freeze) |
| the train-mean baseline (G1's bar) | `../_common/trainmean_baseline.json` | (re-hashed at freeze) |

**Written new by this lane, and each is a diff to be read:**

| new script | what it does |
|---|---|
| `select_control.py` | computes `xi*` by §3.4 and writes `MODEL.md` / `MODEL.json` **before any propagation**. Planted controls G0a, G0e, G0f. |
| `build_r4b_cases.py` | builds the 12 propagation cases by calling `build_aposteriori.build()` unmodified with the `xi`-scaled term sets. Refuses without a committed `MODEL.json` and a present `COVERAGE.md`. |
| `run_r4b.sh` | runs them: the §10.2 pre-launch capacity check, `JOBS=2`, `nice -n 10`, skip-if-complete, never kill. |
| `grade_r4b.py` | the comparator. Grades G0–G7 as written, re-hashes every instrument and every re-used artefact, refuses on any mismatch, writes `artefacts/r4b_grading.json`. |

**`kOmegaSSTSparta` reads T1, T2, T3 only** and would silently evaluate a term
registered with `n = 4` as `T3` (R4 §1). `build_aposteriori.build()`'s caller
asserts `n in (1,2,3)`; that assert is re-used and is re-asserted at the new call
site (CLAUDE.md rule 14: a lesson is not applied until **every** call site
asserts it).

**L-221 / L-222: `libs` entries are inserted with an assert, never replaced.**
`r4_lib.set_libs` does insert-or-replace and then asserts the library name is
present. It matters in both directions here: the 21 hills carry **no** `libs`
line at all, and the ducts, `CBFS13700` and `PHLL10595` carry one naming a
library that does not exist on this machine. A bare `str.replace` is a silent
no-op on the hills and the run then returns the **baseline** field, which looks
like a physical answer.

---

## 10. COMPUTE — costed before launch, with the arithmetic shown (CLAUDE.md rule 12, Charter §18)

### 10.1 Rate, unit, and the honesty label

**Unit: core-minutes / core-hours** = `wall_seconds x ranks / 60` (or `/3600`).
**All runs are serial, 1 rank.** Rate **`$0.0513` per core-hour**, c7a.4xlarge,
**owner-stated 2026-08-21/22 — reported-by-owner and NOT measured**: this box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Every dollar
figure below is DERIVED, NOT MEASURED**, and is labelled so wherever it appears.

**The memo's own `A′` planning figure, quoted first so the difference is
visible** (`R5_DECISION_MEMO.md` §3 A′, from R4's measured unit rates in §2):

```
constrained fit (both targets)      2 x 0.262     = 0.524 core-h
b^Delta-scaled propagation sweep   12 x 0.259     = 3.108 core-h
R-scaled propagation sweep      1.588 x 12/11     = 1.733 core-h
                                                   -------------
                     memo planning figure           5.365 core-h
                     5.365 x 0.0513                = $0.275   DERIVED
                     memo floor (all diverge)
                     0.524 + 0.026 x 2            = 0.576 core-h = $0.030 DERIVED
```

### 10.2 THIS build's registered estimate, and why it differs

This build registers the **scalar** control (§3.2), so **no fit is run** and the
memo's `0.524 core-h` line is **not spent**. The `R`-scaled sweep becomes a
**registered diagnostic contingency** rather than a second graded arm, because
one control on the pair is **one** model and therefore **one** sweep (§3.1).

```
(1) control selection, xi* by §3.4
    12 grid values x barycentric + norm sweep over 172,106 cells,
    numpy reads only, no solver
    basis: make_coverage.py measured 30.6 core-s = 0.0085 core-h for
           two SVD sweeps over the same 172,106 cells
    registered at 2.4x that                        = 0.020 core-h
(2) a-priori scoring, G1 (score_apriori.py re-used)= 0.005 core-h
(3) PAIR-CONTROL propagation sweep, 12 cases
    R4's measured mean converged solve, 11,176 s / 12 / 3600
                                       12 x 0.259  = 3.108 core-h
(4) postProcess -func 'grad(U)' for G4, <= 12 written time dirs
    basis: R5C bounded 29 dirs at <= 0.028 core-h  = 0.012 core-h
(5) a-posteriori scoring + grading                 = 0.005 core-h
                                                    -------------
    GRADED-ARM ESTIMATE                              3.150 core-h
    3.150 x 0.0513                                 = $0.1616  DERIVED

(6) REGISTERED DIAGNOSTIC CONTINGENCY, reported not graded:
    one R-only-at-xi sweep, 12 cases, run ONLY if the graded arm
    diverges, and registered HERE so it is not R4's D-7 again
    measured analogue: the 11-case R-only sweep at 1.588 core-h
                                    1.588 x 12/11  = 1.733 core-h
                                                    -------------
    ESTIMATE WITH CONTINGENCY                        4.883 core-h
    4.883 x 0.0513                                 = $0.2505  DERIVED

    FLOOR, if every propagation dies in 5-18 iterations as R4's did
    (R4's measured 12-case divergent sweep: 94 s = 0.026 core-h)
    0.020 + 0.005 + 0.026 + 0.012 + 0.005          = 0.068 core-h
    with the contingency also diverging, + 0.026    = 0.094 core-h = $0.0048 DERIVED
```

**The difference from the memo is disclosed, not absorbed** (the R5C precedent,
which registered `0.210` against the memo's `0.184` and disclosed the `$0.0014`).
Here it runs the other way: **4.883 core-h against the memo's 5.365**, a
reduction of **0.482 core-h = $0.0247 DERIVED**, and it is entirely the fit line
the scalar design does not spend, partly offset by the `grad(U)` and scoring
lines the memo priced at *"~ 0"*.

### 10.3 THE HARD CAP, and the reduction clause

> **CAP: `8.0 core-h` = `$0.4104` DERIVED.** That is **1.64x** the
> with-contingency estimate and **2.54x** the graded-arm estimate.
>
> **If the projected spend would reach the cap, the lane STOPS and reports
> `BLOCKED`. An overrun stops the run; it does not get a new budget**
> (CLAUDE.md rule 12).

The projection is recomputed from accumulated `wall_seconds` every time the run
set is polled, as `spent + (remaining cases) x (mean converged solve so far)`.

**Reduction clause, registered:** if accumulated spend reaches **4.0 core-h**
(50 % of cap) with the graded sweep incomplete, **the diagnostic contingency (6)
is dropped**, concurrency drops to 1, and the reduction is reported as a
departure in `RESULTS.md`. **The cap does not move.**

**Against Charter §18:** 487 core-hours are pre-authorised; **8.0 core-h is
1.6 % of that ceiling**, and the graded estimate is **0.65 %**. This is far
under the pre-authorisation and does not approach the stop-and-cost line.
Sanaa's 2026-08-21 blanket covers CPU runs of this size; **it is not read as a
new ceiling and this run is costed anyway** (CLAUDE.md rule 9: a blanket is not
a per-item read).

### 10.4 ESTIMATE-VERSUS-ACTUAL CALIBRATION — registered as a duty of completion

CLAUDE.md rule 12, Sanaa's directive of 2026-08-23 verbatim: *"for all teams
involved once a process is completed, the estimated costs must be compared with
the actual incurred costs so we can improve the lab's estimates"*.

Registered: **at this build's completion, a row lands in
`docs/COST_CALIBRATION.md`** stating the pre-registered estimate, the actual in
**core-minutes from the logs** (each case's own `wall_seconds x 1 rank`), the
**ratio actual/predicted**, the attribution of the gap (contention /
misprediction / waste, with **waste separately named and never absorbed into the
ratio**), and the dollar figure **derived at `$0.0513/core-h` and labelled
derived, not measured**. **A completion report without that comparison is
incomplete** and the lane is not done.

---

## 11. CAPACITY DISCIPLINE — registered as a constraint of the run

**~~Sanaa's ruling binds this build:~~ ATTRIBUTION WITHDRAWN — D515, D517.** This is a **RELAYED PARAPHRASE, uncorroborated inside this repository, and it is NOT authority to run.** Quoted here exactly as §0.1 (`:33`) qualifies it — *verbatim as relayed to this lane* — and not as her direct word: *"R4's CPU-minutes run in parallel; they
never displace consolidation work."* That is a constraint on **how** this runs,
not only on whether. **The constraint itself is unaffected: §11.1 below is THIS DOCUMENT'S OWN registered limit, it stands whatever the provenance of the quotation turns out to be, and the withdrawal RELAXES NOTHING — a constraint whose stated authority has been withdrawn is kept, never loosened (D517).** See **AMENDMENT 1** at the foot of this file.

### 11.1 The registered concurrency limit

> **At most `2` concurrent single-rank solves.** Every solve is launched under
> **`nice -n 10`**. **Never more than 2, under any pre-launch reading.**

The box has **16 cores**. R4's own runner defaults to `JOBS=8` and applies **no
`nice`** — re-using it unchanged would violate this clause, so `run_r4b.sh`
sets `JOBS=2` and wraps every solve in `nice -n 10`, and the comparator records
the launch form beside the results.

### 11.2 The registered PRE-LAUNCH CHECK — and it does not trust `pgrep` alone

Before the first solve, and again before each batch, the runner records:

1. **`nproc`** (expected 16);
2. **the 1-minute load average** from `/proc/loadavg` — a number, recorded;
3. **the live solver count**, by `pgrep -a` over solver executable names
   (`simpleFoam`, `buoyant*`, `*Foam`, `kCorrectiveFrozenFoam*`), with the
   matching command lines recorded, not just the count;
4. **the top ten CPU consumers by `%CPU`**, whatever they are.

**Step 4 is not optional and it is why this check is not a `pgrep` count.**
Measured while this draft was written (2026-08-24T19:13Z, a read, no compute):
**3** `buoyantBoussinesqSimpleFoam` solvers live at 99.9 % CPU each — **and a
load average of 72.31 on 16 cores**, because **16 concurrent `tesseract` OCR
processes** from another workstream were consuming the rest of the box. **A
check that counted solver names would have reported "3 solvers, room to spare"
and been wrong by a factor of six.** L-41's shape exactly: the things that make
the box busy are not always visible to a solver-name sweep.

### 11.3 The registered rule for a busier box — fewer, never more

| pre-launch reading | registered concurrency |
|---|---|
| load1 `< 16` **and** fewer than 4 live foreign solvers | **2** |
| load1 `>= 16` **or** `>= 4` live foreign solvers | **1** |
| load1 `>= 40` | **do not launch.** Record **`BLOCKED`** — cause: compute capacity; acquisition path: re-check when the box clears. No solve starts. |

**The rule only ever reduces concurrency.** No reading permits 3 or more, and no
reading permits removing the `nice`.

**Nothing else is touched.** No foreign process is reniced, stopped, or
inspected beyond reading its command line. Before launching anything the lane
also performs the standing check for live peers: `git log --since=<minutes>`,
run-directory mtimes under `/home/ubuntu/closure-data/`, the docket, and only
then the process sweep — because fleet agents are invisible to `pgrep` (L-41).

---

## 12. THE VERDICT LADDER — the fixed vocabulary only

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`,
and **nothing else**. No synonyms, no hedging prose; honesty is carried by the
value, its threshold, the interval and the label (CLAUDE.md rule 1;
`VERIFICATION_CHARTER.md` §2; Charter §12). `PENDING` is a **queue state** for
"not yet run" and is **never** used to soften a `GATE FAIL`.

**Graded in this order, and the order is registered:**

1. **Any G0 control fails** → **`NOT A RESULT`**. The comparator is not
   evidence. Stop.
2. **§3.4 finds no feasible `xi`** → **`BLOCKED`** (F4). Stop.
3. **G5a fails** (a-priori realisability above the §5 thresholds) →
   **`NOT A RESULT`**, and the model is not propagated. Stop. *(This is the
   clause R4 did not have.)*
4. **G1** is graded → `PASS` or `GATE FAIL` on the a-priori bar.
5. **G2** is graded → `PASS` (12 of 12 converged) / `GATE REACHED` (`>= 8`) /
   `GATE FAIL` (`< 8`).
6. **G5b** is graded on every case with a written field → any case above the §5
   thresholds makes the lane **`NOT A RESULT`**, **regardless of RMSE**, and
   that overrides a `PASS` at G1/G2/G3 but **never converts a `GATE FAIL` into a
   `PASS`**.
7. **G4** is graded on every case with a written field → a case above
   `eps_cont = 5.0e-03` is **NOT CONVERGED whatever its velocity error**, and
   its G3 row is reported and not graded.
8. **G3** is graded on `PHLL10595` and `CBFS13700` → `PASS` or `GATE FAIL`.
9. **G6a, G6b** are graded → `GATE REACHED` or `GATE FAIL`.
10. **Any §7 failure mode observed** → **`NOT A RESULT`**, overriding a PASS,
    never converting a `GATE FAIL` into a PASS.
11. **Cap reached before grading** → **`BLOCKED`** (§10.3).

**The lane's headline verdict** is the worst outcome reached on this ladder,
stated once, at the top of `RESULTS.md`, with every gate's own verdict tabled
beneath it. **A record that grades itself in two places will eventually be
quoted from the wrong one** (Charter §12).

**Verdict at freeze time: `PENDING` — nothing has been run.**

---

## 13. THE MODEL-FORM BAND (Charter §22.4, and R4's Addendum A2 carried forward by name)

**No shelf-D model-form band is shipped with this model, and the reason is
registered here rather than left as a silence.**

R4's `PREREGISTRATION.md` **Addendum A2** states the requirement this build
inherits, and it is quoted rather than paraphrased:

> Emory's eq. (4) keeps `k` **outside** the bracket, so the eigenspace family
> perturbs **shape and orientation only**; a `k`-magnitude error is outside the
> envelope **by construction**. Across these cases the RANS `k` is **0.59 to
> 0.72** of the LES `k` in the mean, so **2–7 % of cells have a production the
> envelope cannot reach whatever `delta_B` does**. And: *"Neither published
> framework on this shelf contains the thing it is meant to bound, and they fail
> on different axes."*

**The overlap, stated because §22.4 requires it and because it bites this build
hardest of all:** the model's dominant correction is **`R`, the `k`-equation
correction**, and the eigenspace band's blind axis is **`k`-magnitude**. **They
are the same axis.** A band from that machinery therefore cannot bound this
model's principal error, and attaching one would be presenting an envelope as
bounding an error it cannot see — the D446 shape (`P-A4` graded `NOT A RESULT`
at a velocity coverage of 0.744 inside an envelope **1,344x** the signal).

**Registered, therefore:**

* **No band is quoted anywhere in this build's records**, so nothing is
  presented as bounding an error it cannot see;
* **a band is never applied as a correction**, never subtracted from an error,
  and never quoted as the uncertainty of a model whose correction acts on the
  axis the band does not perturb (`UQ_EIGENSPACE.md`: *"Nothing is fitted.
  Nothing here is a model."*);
* **if a band is ever attached to a prediction from this model**, it ships with
  (a) the axis it cannot see, named; (b) **its width against the signal**,
  because it is the width and not the coverage that decides; (c) the measured
  containment it achieves (production containment **0.9279 to 0.9433** on every
  hill and the curved step); and (d) the measured `delta_B` requirement for the
  flow class in hand (on the ducts, **0.95 to 0.98**, against Emory's calibrated
  `O(0.5)`);
* **§22.4's literal duty — "no prediction is reported without its model-form
  band" — is recorded as OWED AND UNDISCHARGED by this build, not as
  satisfied.** This build reports no prediction outside the training families
  and opens no test case, so nothing leaves the box under a missing band; but
  the duty is not pretended away.

---

## 14. WHAT IS COMMITTED, AND WHEN

| commit | contents | when |
|---|---|---|
| **1** | **this file, ALONE**, with its sha256 in the commit message | **before** any code of this build runs on anything |
| **2** | `select_control.py`, `MODEL.md`, `MODEL.json`, `COVERAGE.md`, the FS2/FS5 discharge | after `xi*` is computed, **before any propagation case is built** |
| **3** | `build_r4b_cases.py`, `run_r4b.sh`, `grade_r4b.py` | after the build, **before grading** |
| **4** | `RESULTS.md` with the verdict, the 12-row table, departures, cost actual vs registered, the `artefacts/*.json`, the docket / lesson / numerics drafts, the `docs/LAB_STATE.md` closure-section update, and the `docs/COST_CALIBRATION.md` row | after grading |

**The grading path is fixed at commit 1** (CLAUDE.md rule 2). The comparator's
sha256 is recorded in `RESULTS.md`, and the frozen file is verified to **BE** the
file that ran, by hashing it against the committed blob — at lane start, at every
commit, and at grading.

**Commits use the private-index protocol** of CLAUDE.md rule 10 — never a bare
`git commit`, never `git add -A` or `git add .`, never the shared index, HEAD
captured **once** per invocation for `read-tree`, the assertion and `-p`, and the
post-commit `git diff HEAD~1 HEAD --stat` verify, which is not optional (L-223).
Docket, lesson and numerics numbers are re-derived from the **tail** at commit
time — the **maximum existing number**, never a count (rule 11) — and
`scripts/check_docket_reconciliation.py` runs **before** the docket is edited.

**Bulk field data is NOT committed.** It lives at
`/home/ubuntu/closure-data/r4b/` and the paths are listed in `RESULTS.md`.

**Nothing is sent.** No submission, no upload, no registration, no post, no
comment, no contact with any steward (CLAUDE.md rule 7; Charter §19, §22.8).
Repo 2 does not exist and is not created. **The one pre-registered zero-shot
scoring call is Sanaa's alone and this build does not make it.**

---

## 15. DEPARTURES

**Empty at freeze. Nothing has been run.**

*(Departures are appended here, each dated, each with the measurement that
forced it, at the time it happens — never in a later addendum, which is what
R4's D-14 was and what §8.3 records.)*

### The amendment rule, registered

* **Before first compute**, an amendment is legal and **must state the condition
  and how it was checked** — naming the run directory that does not exist, with
  the `test -e` reading and its timestamp (CLAUDE.md rule 2;
  `VERIFICATION_CHARTER.md` §2b). The version is bumped and the amendment is
  appended at the foot with `lines whose number changed above this section: 0`.
* **After first compute the gates are CLOSED.** Changes land only as **dated
  addenda that cannot alter a gate, threshold, cap or label**. Originals are
  **struck, never rewritten**, so every existing citation into this file by line
  number still resolves.
* **The ladder is scored as written, even when the ladder is wrong** (L-185,
  Charter §11). If a threshold here turns out to be badly chosen, the run is
  graded on it anyway, the finding is recorded in `RESULTS.md` as a finding
  **about the pre-registration**, and the fix goes in the **next**
  pre-registration. **A pre-registration that can be tightened after the fact
  can be loosened after the fact, and the reader has no way to tell which
  happened.**

---

## 16. WHAT THIS BUILD CANNOT SEE (Charter §16 — mandatory)

* **The training sample is six non-randomly selected hills out of twenty-one.**
  Only 12 of R4's 27 registered training cases reached COMPLETE under the strict
  completion rule, so the hills family enters through **six** members. Those six
  are **not a random sample** — they are the ones whose frozen `omega` equation
  happened not to go negative, which correlates with the flow, not with a coin
  (`../R4_sparta_build/RESULTS.md` §7, §11.3(c)). **No fit on this data can be
  told apart from a fit on a biased sample**, and every coefficient this build
  scales inherits that bias.

* **That bias is NOT repaired here, and the repair was attempted and failed.**
  It was run as **R5C** (memo option C) and closed **`GATE FAIL`** on its
  identity gate: `kDeficit` relative L2 **1.1848e-04** on `alpha_10_12000_4048`
  against a registered **1e-6** (`../R5C_omega_repair/RESULTS.md` §5.1). The
  registered consequence was applied verbatim — *"R4's 12 targets stand. The 15
  hills remain INCOMPLETE. The R5C targets are reported and used for
  nothing."* **This build uses no R5C target.** The finding under that verdict
  is real and is recorded rather than buried: the Patankar split **removed the
  clipping almost completely** — 22 of 27 cases at **zero** `bound(omega)`
  events where R4 clipped on all 5,000 iterations, and **10 of the 15 hills
  became COMPLETE** under the strict rule — and the same damping made the
  change-based settle criterion fire **37 % early** on one target
  (iteration 853 against R4's 1362). **A criterion that measures change cannot
  tell convergence from damping (L-243).**

* **It opens NO test or validation case and establishes NOTHING about
  generalisation.** Every number is a training-family number. The gates test
  whether the controlled model **propagates**, not whether it **transfers**.
  No hump number exists for any class in this programme and none is produced
  here.

* **It cannot separate "no SpaRTA form propagates" from "this form does not
  propagate at any amplitude."** The term set is fixed to R4's FS4 freeze
  (§3.2). A constrained refit could in principle find a form that is realisable
  and accurate; this build does not look for one.

* **It cannot tell whether the six selected columns' coverage explains
  anything.** `COVERAGE.md` §2 already removed one candidate explanation for
  R4's GATE FAIL (leave-one-family-out coverage loses only
  0.0011 / 0.0905 / 0.0000 / 0.2238 % of held-out cells) **without establishing
  another**, and this build establishes no other either.

* **The `sigma1/sigma3` tail is measured and its consequence is not.** Roughly
  one duct cell in a hundred carries a near-collinear selected basis
  (`COVERAGE.md` §3); whether that materially moved the fitted coefficients is
  **unmeasured**, and measuring it means refitting, which this build does not do.

* **Two-dimensionality bounds every tensor-basis conclusion here.** Pope's basis
  collapses to three tensors in two dimensions and every case in this benchmark
  is a statistically two-dimensional mean flow. Everything above is a result for
  a **three-tensor** model.

* **The duct comparator has a measured gap.** `NULL − BASE` is `<= 1e-5`
  relative on the hills, `PHLL10595` and `CBFS13700`, and **is not** on the
  ducts, where NULL stagnates at the 20,000 cap at **1.003 to 1.239** times the
  shipped baseline error. Every duct ratio this build quotes carries that gap.

* **No uncertainty band on the truth**, and **no model-form band is shipped**
  (§13) — so nothing here bounds the model-form error, and the record says so
  rather than implying an envelope exists.

* **It says nothing about `T4`.** `T4` is not in the propagated model and
  `kOmegaSSTSparta` cannot evaluate it. R4 §11.4 measured that §2.1's duct
  degeneracy — the stated justification for excluding `T4` on a ducts-only fit —
  is **absent on the frozen fields the regression actually fits** (per-cell rank
  **3.965**, not 3.000). That correction stands untouched here and this build
  neither applies nor repairs the exclusion.

* **One seed's worth of propagation.** All three FS3 seeds returned identical
  term sets, so a seeded propagation is a bit-identical re-run of one model.
  There is no seed spread to quote because there is no seed dependence to
  measure (R4's D-10). Charter §8's three-seed rule is satisfied at the
  **selection** stage and is **not applicable** at the propagation stage; that
  is stated, not assumed.

---

## 17. CROSS-REFERENCES INTO THE CAMPAIGN TREE (Charter §13)

A closure case directory that does not cross-reference the campaign tree is
incomplete. This build's question is answered nowhere else; the artefacts that
bound it are:

* `verification/campaign/W2_SPARTA_*` — the independent frozen-extraction record
  whose `PHLL10595` and `CBFS13700` fields R4's extraction reproduces
  **byte-identically** (settle at 1492 and 354), and whose `CBFS13700` ceiling
  value **0.39753** R4 reproduced at **0.3975**;
* `verification/campaign/W5_SPARTA_GATE_STATUS.md` — the record of the three
  duplicate SpaRTA tasks in nineteen days, read before this file was drafted;
* `../Schmelzer2020_SpaRTA/RESULTS.md` — the existing lab reproduction, PASS at
  the ceiling gate and the discovered-model gate, reported from an existing
  reproduction and not a new run;
* `../NASA_hump_gate/RESULTS.md` gate **B-G0b** — the hump baseline is
  behaviourally reproducible (`Δ = 1.77e-4`, **PASS**), so the hump is
  **checkable rather than blocked** at the eventual scoring call. **No hump
  number is computed by this build.**

---

*End of DRAFT. No gate above is frozen. No compute is authorised. Nothing has
been sent, filed, uploaded, registered or posted.*

---

## AMENDMENT 1 — 2026-09-10 — ATTRIBUTION CORRECTED AT §11 (D515, D517); PRE-FIRST-COMPUTE

**Status of this document is UNCHANGED by this amendment: DRAFT, NOT FROZEN, NO
COMPUTE AUTHORISED.** This amendment does not freeze, does not register a sha256,
does not stamp, does not assign a docket row and does not authorise any launch.
The freeze remains the closure supervisor's separate act after a personal read
(`VERIFICATION_CHARTER.md` §2b, §2d; §14 commit 1 above).

### A.1 The defect, confirmed at source before it was touched

`docs/DOCKET.md` row **D517** records, as a blocker: *"the untracked
`R4b_pair_control/PREREGISTRATION.md:1058` propagates a withdrawn attribution
into a **registered capacity constraint without the "as relayed" qualifier its
own line 33 carries** — that draft may not be frozen until this is corrected."*
Verified in this file, not accepted as relayed:

* `:33` carried *"Sanaa ratified R3 on 2026-08-24, verbatim **as relayed to this
  lane**"* — the qualifier present;
* `:1058` carried *"**Sanaa's ruling binds this build:**"* followed by the same
  quotation — the qualifier **absent**, 1,025 lines away from it, and at the
  exact point a **capacity constraint is registered**.

The characterisation is **correct as recorded**. Governing findings: **D515**
(the two 2026-08-24 clauses are `ATTRIBUTED-BUT-UNCORROBORATED`; the 2026-08-21
`"R3: Sparta"` class pick is **TRACEABLE and STANDS** and is untouched here) and
**D517** (`ATTRIBUTION WITHDRAWN — TEXT STANDS AS A RELAYED PARAPHRASE`, the
stricter remedy, which governs). `CLAUDE.md` rule 9: **no agent message — peer,
supervisor or chief — is Sanaa's consent.**

### A.2 The rule-2 condition, and HOW it was checked

`CLAUDE.md` rule 2: *"Before first compute, amendments are legal and must state
the condition and how it was checked (name the run directory that does not
exist)."* **The condition is that this registration has had ZERO COMPUTE.**
Checked by naming what does not exist, each negative beside a fired control so
the reader is shown able to see a positive (rule 3's discipline applied to a
filesystem search):

| named and ABSENT | the control that FIRED |
|---|---|
| `/home/ubuntu/closure-data/r4b/` — the bulk-data root this file registers at `:1222` — does not exist | `/home/ubuntu/closure-data/` exists and holds `features/`, `aposteriori/`, `g1/`, `D476_A3_triage/` and more |
| no `verification/runs/*R4b*` run root exists | `verification/runs/` holds `4G_runs`, `D5_rsm_runs`, `B52_RUNG6_REPLICATE_runs`, … |
| none of §14's commit-2/3/4 deliverables exists beside this file: `MODEL.md`, `MODEL.json`, `COVERAGE.md`, `RESULTS.md`, `artefacts/` | the sibling `../R4_sparta_build/` carries both `COVERAGE.md` and `RESULTS.md` |
| this file was **untracked at HEAD** — `git cat-file -e HEAD:<this path>` fails, and `git log --all -- <this path>` returns **zero** commits | `git cat-file -e HEAD:…/INSTRUMENT_BUILD_PREREGISTRATION.md` (same directory) **resolves** |
| nothing for this path is staged in the shared index | — |

No solver, no fit, no selection, no propagation, no time directory, no GPU.
**0.0 core-minutes** are attributable to this registration.

### A.3 What was changed — three lines, IN PLACE, nothing inserted

1. `:1` — the title line. `NOT COMMITTED` is **struck, not rewritten**, because
   this draft is now committed and readable at HEAD. `DRAFT`, `NOT FROZEN` and
   `NO COMPUTE AUTHORISED` **stand unchanged and are not weakened**. The commit
   that landed this file is a **lane commit for readability; it is NOT the §14
   commit-1 freeze** and registers no sha256.
2. `:1058` — the attribution. *"Sanaa's ruling binds this build"* is **struck**
   and replaced by the withdrawal, the relay qualifier, and the D515/D517
   cross-reference **at the point the constraint is registered**, not only 1,025
   lines earlier.
3. `:1060` — one added sentence recording that the constraint itself is
   unaffected and is never read as relaxed.

### A.4 WHAT THIS AMENDMENT DOES NOT MOVE — checked clause by clause

**It moves NO gate, NO threshold, NO cap and NO label.** Verified by naming each
and reading it after the edit:

* **Gates** — §5 (`:413`) and the verdict ladder §12 (`:1111`): untouched, not
  one gate word altered.
* **Thresholds** — §13's model-form band (`:1152`); §4's `residualControl 1e-6`
  and the cap-stop rule (`:401`–`:402`): untouched.
* **Caps** — `CAP: 8.0 core-h = $0.4104 DERIVED` (`:1017`); the graded-arm
  estimate `3.150 core-h` (`:990`); with-contingency `4.883 core-h` (`:999`);
  the floor `0.068`/`0.094 core-h` (`:1004`–`:1005`); the 4.0 core-h reduction
  clause and *"The cap does not move"* (`:1027`–`:1030`): every figure
  **byte-identical** to before this amendment.
* **Labels** — the rule-1 vocabulary and every standing verdict cited here
  (`../R4_sparta_build/` **GATE FAIL**, `../R5C_omega_repair/` **GATE FAIL**):
  untouched.
* **§11's REQUIREMENT is IDENTICAL.** §11.1 (`:1064`–`:1065`) still registers
  **at most 2 concurrent single-rank solves**, every solve under **`nice -n 10`**,
  *"Never more than 2, under any pre-launch reading"*; §11.2's pre-launch check
  (`:1072` onward) is unchanged. What changed is the **authority asserted for**
  the constraint, never the constraint. §11.1 is this document's **own** registered
  clause, not a quotation, so it stands on its own footing; and per D517 a
  constraint whose stated authority has been withdrawn is **kept, never loosened**.

### A.5 THE FULL SWEEP — every other place the quotation is stated flatly

Searched this whole file for the four withdrawn attributions (D517). **Only one
of the four appears here** — the 2026-08-24 R3 ratification quotation. The GPU
cost-approval quotation, the hump-baseline request quotation and the shutdown/stop
quotation are **absent** (control: `consolidation work` fires **2** times in this
same file, so the search can see a positive). Every occurrence and near-occurrence:

| line | how it read | disposition |
|---|---|---|
| `:33` | *"verbatim **as relayed to this lane**"* | **correct already** — the qualifier this amendment propagates |
| `:35`–`:36` | the quotation itself, blockquoted directly under `:33` | governed by `:33`, 2 lines above |
| `:44` | *"Her ruling names SpaRTA-class."* | flat, inside §0, 11 lines below `:33` |
| `:45` | *"TBNN-class is named in her ruling as the **fallback**"* | flat — this is D515's clause (b), the **uncorroborated** one |
| `:46` | *excluded by "R4's CPU-minutes run in parallel"* | flat — D515's clause (c) |
| `:56` | *"the lab's ranking applied to Sanaa's ruling"* | flat, but self-limiting: it says it is **not her choice of increment** |
| `:60` | *"Under doctrine Part 3 R3 and Charter §22.7 the lab ranks…"* | flat reference to the ruling |
| **`:1058`** | *"**Sanaa's ruling binds this build**"* | **THE DEFECT — corrected by this amendment** |

**Ruling recorded here so no reader has to reconstruct it:** the `:33` qualifier
and the D515/D517 withdrawal **govern EVERY occurrence of that quotation anywhere
in this document**, including `:44`, `:45`, `:46`, `:56` and `:60`. Those five
were **not edited in place** — they sit above the externally cited anchor `:308`
and any insertion there would stale a tracked citation (D515's own renumbering
lesson) — and correcting them line by line is left to the supervisor's read.

**NOT withdrawn, and never to be conflated with the above:** the **2026-08-21
`"R3: Sparta"` class pick is TRACEABLE and STANDS** (D515: it names a session, a
message and the document it was ruled on — `R2_SHORTLIST_MEMO.md:304`, D443/D444).
So does `CLAUDE.md` rule 12's own 2026-08-21 blanket, quoted at `:1035`, and the
2026-08-23 cost-calibration directive quoted at `:1041` — **both are in `CLAUDE.md`
itself** and are not relayed attributions. **No new authority is invented for any
withdrawn quotation, and the four remain on Sanaa's desk for one line.**

### A.6 LINE NUMBERING — the assertion, and what it does and does not certify

**Lines whose NUMBER changed above this section: 0.** Nothing was inserted or
deleted anywhere: the three edits are **in-place, same-line-count** substitutions,
and this amendment is a **pure append at the FOOT** (D515's standing lesson: an
in-file "0 lines renumbered" assertion certifies only the lines *above* an
insertion, so the append goes at the foot).

**Stated separately and honestly, because the assertion above does not cover it:
lines whose CONTENT changed above this section: 3 — `:1`, `:1058`, `:1060`.**

The three externally cited anchors into this file therefore still resolve:

* `:33` — cited by `docs/LAB_STATE.md:5999` and `docs/DOCKET.md:880` (**D515**);
* `:308` — cited by `../MATRIX_CONTRIBUTION.md:569`;
* `:1058` — cited by `docs/DOCKET.md:882` (**D517**), and it now lands on the
  **corrected** text, which is precisely what D517 asked for.

*End of AMENDMENT 1. Nothing above is frozen. No compute is authorised. Nothing
has been sent, filed, uploaded, registered or posted.*

---

## AMENDMENT 2 — 2026-09-10 — §14's COMMIT SCHEDULE IS OVERTAKEN BY THE INSTRUMENT FREEZE AT `3d50ceed`; PRE-FIRST-COMPUTE

**Document version: DRAFT+A1 → DRAFT+A2.**

**Status of this document is UNCHANGED by this amendment: DRAFT, NOT FROZEN, NO
COMPUTE AUTHORISED.** This amendment does not freeze, does not register a sha256,
does not stamp, does not fill the six `(re-hashed at freeze)` cells, does not
assign a docket row and does not authorise any launch. The freeze remains the
closure supervisor's separate act after a personal read
(`VERIFICATION_CHARTER.md` §2b, §2d; §14 commit 1 above). **This lane authorises
nothing.**

### B.1 The finding, confirmed at source before anything was written

§14's commit schedule (`:1199` heading; the table rows `:1203`–`:1206`) is
**overtaken by events**. It places four scripts in the future:

* row `:1204`, commit **2** — `select_control.py`, `MODEL.md`, `MODEL.json`,
  `COVERAGE.md`, the FS2/FS5 discharge, *"after `xi*` is computed, before any
  propagation case is built"*;
* row `:1205`, commit **3** — `build_r4b_cases.py`, `run_r4b.sh`,
  `grade_r4b.py`, *"after the build, before grading"*.

**All four scripts are already TRACKED AT HEAD.** Measured, not relayed:
`git cat-file -e HEAD:<path>` resolves for each of the four, and
`git log --diff-filter=A` names one and only one adding commit for each —
**`3d50ceed`**, `2026-08-30 22:42:40 +0000`, whose diffstat is exactly those four
paths and nothing else (`+2,780` lines). The control for that same reader fired:
`MODEL.json`, `MODEL.md`, `COVERAGE.md` and `RESULTS.md` in this same directory
return *"does not exist in 'HEAD'"*, so the check can distinguish tracked from
untracked and is not returning a uniform yes.

`3d50ceed`'s own commit message declares its evidentiary character in its own
words: it landed the four *"with their sha256 in the message, AFTER authoring and
BEFORE the birth demonstrations are graded — so this commit is the freeze the
grading path is fixed to under standing rule 2, and nothing here grades
anything."*

**Consequence, stated plainly: §14's rows `:1204` and `:1205` are unexecutable as
written for those four paths.** Under the rule-10 private-index protocol a commit
of an unchanged path writes the parent tree, the mandatory non-empty assertion
fires, and the invocation correctly aborts. A schedule that cannot be executed is
a defect in the schedule, not a licence to bypass the assertion.

### B.2 The rule-2 condition, and HOW it was checked — freshly, in this lane's own invocation

`CLAUDE.md` rule 2: *"Before first compute, amendments are legal and must state
the condition and how it was checked (name the run directory that does not
exist)."* **The condition is that the R4b SOLVE ARM registered by this document
has had ZERO COMPUTE.** AMENDMENT 1's checks are **not inherited**; every row
below was re-run by this lane, each negative beside a control that fired, so the
reader is shown a search able to see a positive (rule 3's discipline applied to a
filesystem and to git):

| named and ABSENT | the control that FIRED |
|---|---|
| `/home/ubuntu/closure-data/r4b/` — the bulk-data root this file registers at `:1222` — **does not exist** | `/home/ubuntu/closure-data/` exists and lists `features/`, `aposteriori/`, `aposteriori_frozenk/`, `g1/`, `D476_A3_triage/`, `b3_trainmean.json`, … |
| **no `verification/runs/*R4b*` or `*r4b*` run root exists** | `verification/runs/` holds `4G_runs`, `D5_rsm_runs`, `B52_RUNG6_REPLICATE_runs`, `DMR_R3_L2_COURANT_PROBE_runs`, … |
| `artefacts/` beside this file **does not exist**; the directory holds only `INSTRUMENT_BUILD_PREREGISTRATION.md`, `PREREGISTRATION.md`, `QUEUE_ENTRY_DRAFT.json`, `R4b_Ib/` and the four scripts — **no time directory, no `log.*`, no solver output** | the sibling `../R4_sparta_build/` carries both `COVERAGE.md` and `RESULTS.md` |
| commit-2/3/4 deliverables `MODEL.md`, `MODEL.json`, `COVERAGE.md`, `RESULTS.md` are **absent from disk AND untracked at HEAD** | the same two-part reader returns `PRESENT`/`TRACKED` for `grade_r4b.py` |
| **this document's sha256 is pinned NOWHERE in the repository** — a repo-wide content search for it returns zero files, so nothing anywhere treats it as frozen | the same search for the *instrument* registration's sha256 `7a80553c…` returns **two** files, `R4b_Ib/INSTRUMENT_BUILD_PREREGISTRATION_R4b_Ib.md` and `R4b_Ib/grade_r4b_ib.py` |
| `QUEUE_ENTRY_DRAFT.json:4` still reads `"prereg_commit": "PENDING_SUPERVISOR_FREEZE"` — not a sha; and `:24` still carries the build lane's written statement that **check 4 has NOT been performed by anyone** | — (read directly; the file's own text) |

**One positive is disclosed here rather than left to be found, because it looks
like a contradiction and is not.** `/home/ubuntu/closure-data/r4b_instruments/`
**does exist** (19 MB), which `3d50ceed`'s message recorded as absent on
2026-08-30. It holds one subtree, `_dev/`, with `_dev/cases/` and `_dev/birth/`;
its newest file anywhere is dated **2026-08-28 17:43:16Z**, nothing in it
postdates 2026-09-01, and it contains **no `log.*` and no solver time
directory**. It is the **instrument arm's** dev/birth material, governed by the
separate `INSTRUMENT_BUILD_PREREGISTRATION.md` (sha256 `7a80553c…`, pinned at
`R4b_Ib/grade_r4b_ib.py:148`). **It is not compute against this document's
gates**, and this amendment does not claim it as such.

**No solver, no fit, no selection, no propagation, no time directory, no GPU
for the solve arm. 0.0 core-minutes are attributable to this registration.**

### B.3 THE RULING — the closure supervisor's, recorded here so no reader reconstructs it

Recorded **[lab-attributed, closure-supervisor, 2026-09-10]**. `CLAUDE.md` rule 9:
no agent message is Sanaa's consent, and none is claimed here.

1. **§14's commit-3 row is ALREADY DISCHARGED at `3d50ceed`, and commit-2's row
   is discharged IN ITS SCRIPT PART ONLY. The schedule is overtaken, NOT
   violated.** Nothing was done out of order in a way that costs evidence.
2. **The deviation runs in the CONSERVATIVE direction** — see B.4.
3. **The solve arm's grading path is fixed by a COMPOSITION, not by one commit** —
   see B.5.
4. The comparator is **doubly frozen** and has not moved — see B.6.
5. **NO gate, NO threshold, NO cap and NO label moves.** A commit schedule is
   none of those four — see B.7.
6. **§14's "commit 1 = this file, ALONE" is amended ONLY** to the extent that the
   freeze commit will also carry the **six sha256 cells** at `:775`–`:777` and
   `:915`–`:917` that currently read *"(re-hashed at freeze)"*. That is **§9's own
   preamble being executed**, not §14 being loosened: §9 at `:903`–`:905` already
   requires that every re-used instrument *"is verified `disk == HEAD` and
   re-hashed at the freeze commit and again at grading, and the comparator
   **refuses** on a mismatch."* **This amendment does not fill those six cells.**

**ONE REFINEMENT, MEASURED BY THIS LANE IN DISCHARGING THE RULING, RECORDED
RATHER THAN SMOOTHED OVER.** The ruling as dispatched read *"commits 2 and 3 are
already discharged"*. Commit **3** is discharged **in full**: all three of its
named paths are tracked at `3d50ceed`. Commit **2** is discharged **in part
only** — `select_control.py` is tracked, but `MODEL.md`, `MODEL.json`,
`COVERAGE.md` and the FS2/FS5 discharge are **absent from disk and untracked**,
which `3d50ceed`'s own message states in the same words: *"MODEL.md, MODEL.json
and COVERAGE.md remain ABSENT, so `build_r4b_cases.py` would refuse today by its
own registered clauses — correctly."* **Commit 2's document deliverables are
therefore still OWED and are unaffected by this amendment.** Item 1 above is
recorded in the narrower form that the measurement supports.

### B.4 WHY THIS IS A RECORDABLE DEVIATION AND NOT A RULE-2 BREACH — the direction matters

This document was drafted **2026-08-24**. The four instruments were frozen and
sha-pinned **2026-08-30**, at `3d50ceed`. This document's own freeze **has not
happened yet**.

An instrument frozen **earlier** offers strictly **less** opportunity to be
fitted to an answer than one frozen later. Rule 2's evidentiary content is that
*"the gate could not have been chosen to fit the answer"*; an instrument pinned
by sha six days before the registration it serves is pinned **against a future
answer nobody had**, which is the direction rule 2 exists to protect. The
deviation therefore **tightens** the evidence and does not weaken it. That, and
only that, is why it is recorded as a deviation rather than escalated as a
breach.

The counterfactual is stated so it is not left implicit: had the four scripts
been written **after** a result existed, or had they been edited since being
pinned, this would be a different finding entirely. B.6 shows they have not
moved.

### B.5 THE GRADING PATH IS FIXED BY A COMPOSITION — stated explicitly, because §14 implies otherwise

§14 asserts, at `:1208`, *"The grading path is fixed at commit 1"*. That sentence
was true when drafted and is **no longer the whole truth**. It is not struck —
commit 1 remains necessary — but it is completed here:

> **The R4b solve arm's grading path is fixed by the COMPOSITION of (i) this
> document's freeze commit, which has NOT yet been taken and is the closure
> supervisor's act, TOGETHER WITH (ii) the already-frozen, sha-pinned instruments
> landed at `3d50ceed` on 2026-08-30.** Neither half alone fixes it. A reader
> verifying the grading path must hash **both**: this file against its freeze
> commit's blob, and each of the four instruments against the sha256 values
> recorded in `3d50ceed`'s message.

§9's table at `:918`–`:923` still describes those four as *"Written new by this
lane"*. That description is now historical; the four are landed, pinned and
unmodified. **No gate, threshold, cap or label depends on that phrasing**, and it
is left in place rather than edited, per rule 6.

### B.6 THE COMPARATOR IS DOUBLY FROZEN — measured in this lane's invocation

`grade_r4b.py` on disk hashes

`0e2554ae00e486c75a8529f07e77a974c388913d96d1839d0bc8d601cd34ca96`

which is **byte-for-byte the value recorded three independent times**:

| where the same 64 hex digits appear | verified how |
|---|---|
| the file on disk | `sha256sum` in this lane's invocation |
| the blob at HEAD | `git cat-file -p HEAD:<path> \| sha256sum` — so `disk == HEAD` |
| `3d50ceed`'s commit message, measured in the committing invocation | read from `git log` |
| `R4b_Ib/grade_r4b_ib.py:139`, as `PARENT_SHA256` (declared `:138`) | read at that line |

The other three carry the same triple agreement — `select_control.py`
`50d9622d…` (pinned `R4b_Ib/grade_r4b_ib.py:142`), `build_r4b_cases.py`
`b45ddd8e…` (pinned `:145`), `run_r4b.sh` `f915bfed…` (in `3d50ceed`'s message;
no `R4b_Ib` pin, because R4b-Ib does not invoke it). **`disk == HEAD` holds for
all four.** The comparator is frozen **twice over** — once at `3d50ceed`, once as
R4b-Ib's sha-pinned parent — and a drift in either would make R4b-Ib refuse.

**The registered hash cells in THIS document were re-measured against disk in the
same invocation: 15 cells carry a literal sha256 (`:654`–`:660`, `:774`,
`:908`–`:914`) and all 15 MATCH — 15/15, no drift.** That supersedes nothing; it
extends AMENDMENT 1's 7/7 reading of the §9 instrument table (`:908`–`:914`) to
every hash cell in the file. The reader used was shown able to report a mismatch
before its zeroes were believed: fed a planted wrong digest for the same file, it
reported **DRIFT**, so the fifteen `MATCH` results are not a reader that answers
`MATCH` unconditionally. The **six** cells reading *"(re-hashed at freeze)"* at
`:775`–`:777` and `:915`–`:917` are **deliberately still empty** and are the
supervisor's to fill at the freeze.

### B.7 WHAT THIS AMENDMENT DOES NOT MOVE — checked clause by clause, each read after the append

**It moves NO gate, NO threshold, NO cap and NO label.** A commit schedule is
none of the four. Verified by naming each and reading it:

* **Gates** — §5 (`:413`, *"THE GATES — registered now, before any run"*) and
  the verdict ladder §12 (`:1111`, *"THE VERDICT LADDER — the fixed vocabulary
  only"*): untouched, not one gate word altered.
* **Thresholds** — §13's model-form band (`:1152`); §4's `residualControl 1e-6`
  on `U`, `p`, `k`, `omega` with *"A cap-stop is NOT converged"*
  (`:401`–`:402`): untouched.
* **Caps** — `CAP: 8.0 core-h = $0.4104 DERIVED` (`:1017`); the graded-arm
  estimate `3.150 core-h` (`:990`); with-contingency `4.883 core-h` (`:999`);
  the floor `0.068 core-h` / `0.094 core-h = $0.0048 DERIVED` (`:1004`–`:1005`);
  the reduction clause at **`4.0 core-h`** (50 % of cap) dropping the diagnostic
  contingency and concurrency to 1, closing *"The cap does not move."*
  (`:1027`–`:1030`): every figure **byte-identical** to before this amendment.
* **Labels** — the rule-1 vocabulary and every standing verdict cited in this
  document: untouched.
* **§11's capacity constraint is IDENTICAL** and is not re-opened by this
  amendment. AMENDMENT 1 governs `:1058`; this amendment does not touch it.

### B.8 LINE NUMBERING — the assertion, and the proof that makes it true

**Lines whose NUMBER changed above this section: 0.**

**Lines whose CONTENT changed above this section: 0.** This amendment is a
**pure append at the FOOT** and edits nothing in place — unlike AMENDMENT 1,
which disclosed three in-place content changes. Proved, not asserted: the
prefix — every line above this amendment's heading — was hashed **before** the
append and **again after it, in the same shell invocation**, and the two digests
are equal. Both digests are recorded in this lane's report to the supervisor.

Foot-append is mandatory here and not a stylistic choice: **three tracked
citations point into this file by line number**, and any insertion above one of
them stales a tracked citation (D515's standing renumbering lesson). All three
were re-read **after** the append and still land on their intended text:

* `:33` — cited by `docs/LAB_STATE.md:5999` and `docs/DOCKET.md:880` (**D515**);
  reads *"Sanaa ratified R3 on 2026-08-24, verbatim as relayed to this lane:"*;
* `:308` — cited by `../MATRIX_CONTRIBUTION.md:569`; reads the grid line
  *"the grid `G = {0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30,"*;
* `:1058` — cited by `docs/DOCKET.md:882` (**D517**); reads the struck
  attribution and the withdrawal AMENDMENT 1 installed.

### B.9 WHAT STILL STANDS BETWEEN THIS DOCUMENT AND ITS FREEZE — recorded for the supervisor's read only

Descriptive, not authorising. This lane clears none of these.

1. The **six sha256 cells** at `:775`–`:777` and `:915`–`:917` are unfilled
   (§9's preamble, `:903`–`:905`; ruling item 6).
2. The **freeze commit itself** — this file, with its sha256 in the commit
   message — has not been taken. This document's sha is pinned nowhere.
3. `SUPERVISION_CHARTER.md` §3 **check 4** — pre-registration committed before
   compute — has not been performed by anyone;
   `QUEUE_ENTRY_DRAFT.json:24` says so in the build lane's own words.
4. `QUEUE_ENTRY_DRAFT.json:4` carries `PENDING_SUPERVISOR_FREEZE` in place of a
   sha, and the cwd it names does not exist for the solve arm.
5. The **solve arm remains BLOCKED on Sanaa's increment ruling**, which
   `grade_r4b.py` states at `:823`–`:827` rather than leaving to prose.
6. The **withdrawn-attribution occurrences at `:44`, `:45`, `:46`, `:56` and
   `:60`** were left uncorrected by AMENDMENT 1 (A.5) and are the supervisor's
   read; §11's constraint is governed by `:33` and `:1058` and is kept, never
   loosened.
7. Commit 2's **document deliverables** — `MODEL.md`, `MODEL.json`, `COVERAGE.md`
   and the FS2/FS5 discharge — remain absent and owed (B.3 refinement).

*End of AMENDMENT 2. Nothing above is frozen. No compute is authorised. Nothing
has been sent, filed, uploaded, registered or posted.*
