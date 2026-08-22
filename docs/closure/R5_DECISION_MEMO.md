# Decision memo — what the closure line does next after R4's GATE FAIL

**For Sanaa.** Prepared by the closure team, 2026-08-22, under
`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md` and
`docs/charters/CLOSURE_MODELLING_CHARTER.md` v1.1.2.
**Documentation only: nothing was trained, fitted, solved, submitted, uploaded,
filed or registered to produce it. Zero compute.**

**THE CHOICE BELOW IS SANAA'S.** This memo lays out options, costs, what each
would have to pre-register, and the failure mode that would make each **NOT A
RESULT**. It ends with a **recommendation**, marked as one. Under doctrine
Part 3 R3 and Charter §22.7 the lab ranks and argues; **it does not choose.**
The **Repo 2 release** and the **one pre-registered zero-shot scoring call**
remain hers alone; this lane prepared neither.

**A note on this file's name.** The restart doctrine **dictates no filename for
a post-GATE-FAIL decision memo**; the only naming precedent in
`docs/closure/` is `R2_SHORTLIST_MEMO.md`, and this file follows it. Be aware
that the doctrine's own **R5** label means something else — *"Round-5
diagnostics feed the build as constraints"* (Part 3, R5) — and **this memo does
not claim to be that stage's artefact.** `docs/LAB_STATE.md` records R5 as
having *"no verdict artefact"*; that is still true and this file does not change
it.

---

## 1. Where the line stands, in four sentences

R4 returned **VERDICT: GATE FAIL** on both registered halves — the discovered
`b^Delta` missed the a-priori train-mean bar at **2 of 4** families against 3,
and the discovered symbolic model **diverged on all twelve** training
propagations at iterations 5–18
(`cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §6).
**The registered NOT A RESULT branch did not fire**: the per-case frozen-field
ceiling beats NULL by **99.6 %** on `PHLL10595` and **60.2 %** on `CBFS13700`,
reaches **99.99 %** on `AR_5_Ret_180`, lands `CBFS13700` at **0.3975** against
the W2 record's independent **0.39753**, recovers the duct secondary vortex to
**0.4–0.6 %** of DNS where a linear EVM gives **exactly zero**, and reattachment
to **0.9–3.4 %** of the LES (same file, §5.1–5.3 and §11.2).
**The harness carries the truth; the model does not** — the first lane in this
programme where the failure has that shape, because the two prior lanes returned
**NOT A RESULT** on ceilings that could not beat doing nothing.
That makes this a **decision point, not a retry**: a GATE FAIL whose apparatus
is proven is a different situation from a GATE FAIL whose apparatus is not.

**Three measured constraints that bound every option below.** All are from
R4's own artefacts and all are re-solved, not a-priori.

1. **The failure is not implementation.** IC1 agrees solver against independent
   Python to **3.97e−12** on `kDeficit` and **5.08e−13** on `bijDelta`
   (`R4_sparta_build/artefacts/ic1_discovered.json`); the frozen extraction
   reproduces the W2 record **byte-identically** on `PHLL10595` and
   `CBFS13700`; NULL reproduces the shipped baseline to ≤ 1e−5 relative on the
   hills, `PHLL10595` and `CBFS13700`; three FS3 seeds return identical term
   sets (`RESULTS.md` §2.1, §4.2, §5.2, §4.7).
2. **Amplitude on `b^Delta` alone is measured to be insufficient.** The paper's
   own `xi = 0.1` remedy converges on **three of four ducts** and **still
   diverges on every hill, on `PHLL10595` and on `CBFS13700`**
   (`RESULTS.md` §5.1, §5.4, §11.5).
3. **The discovered `R` alone destabilises every separated flow.** With
   `b^Delta` switched off entirely it **still diverges on all six hills and on
   `CBFS13700`** (`sum local` to **9.8e+05** after 163 iterations) and survives
   on `PHLL10595` only at **49.18x** the baseline error (`RESULTS.md` §5.4).
   **This bounds what D443/D444's `TRUTH + R` 98.3 % duct-error cut licenses:**
   it licenses a claim about `R` as a *correction*, not about a *discovered* `R`
   as a model (`RESULTS.md` §11.5).

Constraint 3 is the one that decides most of what follows, and it is why the
option list below splits (a) into two variants.

---

## 2. The cost calibration — R4's own measured rates

Every core-hour figure in §3 is derived from these. Rate **$0.0513 per
core-hour** (`R4_sparta_build/RESULTS.md` §10). **All figures are 1 rank, core
not wall**; R4's box carried 12 concurrent thermal solvers from another lane
throughout, so wall time ran roughly twice core time (same section).

**Whole-build calibration** (`RESULTS.md` §10):

| item | measured | cost |
|---|---|---|
| 27 frozen extractions + 5 convergence diagnostics | **0.244 core-h** | $0.013 |
| FS3 selection, run twice (departure D-6) | **0.524 core-h** | $0.027 |
| all propagation, 60 solves, from per-case `wall_seconds` | **8.435 core-h** | $0.433 |
| **R4 total** | **9.203 core-h** | **$0.472** |

`9.203 x 0.0513 = $0.4721`, which is the $0.472 of record.

**Unit rates**, from the per-case `wall_seconds` files under
`/home/ubuntu/closure-data/r4/aposteriori/<case>/<config>/`, which sum to
**8.4347 core-h** and so reproduce §10's 8.435:

| unit | derivation | rate |
|---|---|---|
| one **converged propagation solve**, mean over the 12 CEILING runs | `11,176 s / 12 / 3600` | **0.259 core-h** ($0.0133) |
| one **12-case single-configuration sweep** (CEILING) | `11,176 s / 3600` | **3.104 core-h** ($0.159) |
| one **12-case NULL sweep** (4 of 12 hit the 20,000 cap) | `10,763 s / 3600` | **2.990 core-h** ($0.153) |
| one **12-case sweep that diverges in 5–18 iterations** (DISCOVERED) | `94 s / 3600` | **0.026 core-h** ($0.0013) |
| one **12-case `xi = 0.1` sweep** | `2,617 s / 3600` | **0.727 core-h** ($0.037) |
| one **11-case `R`-only sweep** | `5,715 s / 3600` | **1.588 core-h** ($0.081) |
| one **27-case frozen re-extraction** | `660.5 s / 3600`, summed from each `frozen/<case>/log.frozen` `ExecutionTime` | **0.184 core-h** ($0.0094) |
| one **hill frozen extraction at the 5,000 backstop** | e.g. `alpha_10_9000_3036` `ExecutionTime = 31.16 s` | **0.0087 core-h** ($0.00044) |
| one **FS3 selection pass** | `0.524 / 2` | **0.262 core-h** ($0.0134) |

**Per-family converged CEILING solve costs**, used where an option re-solves the
full 27-case set: hills **0.1969 core-h** (mean of the five converged/capped hill
CEILING runs, `3,545 s / 5 / 3600`; the diverged `alpha_10_12000_4048` run is
excluded), four ducts together **0.630 core-h**, `PHLL10595` **0.151 core-h**,
`CBFS13700` **1.318 core-h**. A **27-case** single-configuration sweep is
therefore `21 x 0.1969 + 0.630 + 0.151 + 1.318 =` **6.234 core-h** ($0.320).

**The ceiling above all of this** is Charter §18: **487 core-hours
pre-authorised; a projected spend at or above that figure stops and is costed
before launch.** One option below crosses it and is marked.

---

## 3. The options

Each row states what it would establish, what it would cost with the arithmetic
shown, what would have to be pre-registered **before any run**, and the failure
mode that would make it **NOT A RESULT**.

### Summary table

| # | option | compute | cost | crosses §18's 487 core-h? |
|---|---|---|---|---|
| **A** | re-preregister **`b^Delta`** amplitude control | 0.55 – **3.63** core-h | $0.028 – **$0.186** | no |
| **A′** | amplitude / realisability control on **the pair** (`b^Delta` **and** `R`) | 0.52 – **5.37** core-h | $0.027 – **$0.275** | no |
| **B1** | re-open R2 → **FIML-C** (rank 2) | pilot **0.61**; full build **621.6** | $0.031; **$31.89** | **YES at full build** |
| **B2** | re-open R2 → **TBNN + `R` head** (rank 3) | **20.90** + unestimated head | **$1.072** + unknown | no |
| **C** | fix the `omega` source, complete the **15 hills** | **0.184** (repair+re-extract) | **$0.009** | no |
| **C2** | C, then rebuild R4 on all 27 cases | **19.15** | **$0.982** | no |
| **D** | stop discovery, **bank the harness result** | **0.000** | **$0.000** | no |

---

### A. Re-preregister the `b^Delta` amplitude control

**Two variants, and they are different experiments.**
**A1 — a realisability constraint inside the fit**: the regression is constrained
or penalised so that the total anisotropy `b_lin + b^Delta` stays inside the
realisable set, and a **numeric realisability threshold is registered in the
verdict ladder** as Charter §4 requires.
**A2 — `xi` as a REGISTERED part of the model**: a single scalar on the
`b^Delta` coefficients, selected inside the training set by the frozen protocol
and written into `MODEL.md` **before any propagation**, not applied afterwards as
a remedy.

**What it would establish.** Whether R4's GATE FAIL is about the discovered
**form** or about its **amplitude** — i.e. whether a SpaRTA-class `b^Delta` of
this form can be propagated at all once its magnitude is bounded. It would
establish **nothing about generalisation** and would open no test case.

**What it would cost.**

```
constrained / penalised FS3 pass   2 x 0.262   = 0.524 core-h   (the x2 is an
                                                 ESTIMATE: a constrained path
                                                 costs more than R4's
                                                 unconstrained elastic net)
a-priori scoring + realisability                ~ 0
propagation, 12 cases, if it converges
                                   12 x 0.259  = 3.108 core-h
propagation, 12 cases, if it dies as R4's did   = 0.026 core-h
NULL and CEILING re-used from R4's artefacts    = 0.000 core-h
                                                 -------------
                          planning figure         3.632 core-h
                          3.632 x 0.0513        = $0.186
                          floor (all diverge)     0.550 core-h = $0.028
```

**What would have to be pre-registered before any run.**
1. **A numeric realisability clause in the verdict ladder** — Charter §4's own
   frozen wording is available: *"**NOT A RESULT** if the predicted `b` is
   non-realisable in more than **3x** the truth's own violation fraction on the
   same cells, or if `max ||b||_F` exceeds `sqrt(2/3)` by more than a factor of
   **2**, regardless of RMSE."* R4's discovered model would have failed this at
   **19.1 %** of `CBFS13700` against a truth rate of **3.6 %** and at
   `max ||b^Delta||_F = 7.559` (`R4_sparta_build/artefacts/apriori_realisability.json`).
2. **The constraint strength or `xi`, and how it is chosen**, fixed before any
   propagation, from training-family measurements only.
3. **The train-mean tensor bar** (Charter §3, `_common/BASELINES.md` §6.4) and
   the pass fraction — R4 registered ≥ 3 of 4 families.
4. **Re-use of R4's NULL and CEILING as measured comparators**, named with the
   artefact and its hash, or a re-run; not left ambiguous.
5. **A non-dimensional continuity gate** (see §4, amendment candidate 2).
6. **The complete six-condition extraction completion rule** as R4 ended with
   it, registered up front rather than extended after first compute (R4's D-4).
7. **The zero-shot assertion in code**, as `r4_lib.assert_no_test_case`.
8. **A compute cap**, with the reduction clause.

**The failure mode that makes it NOT A RESULT.**
*The constraint strength or `xi` is chosen after seeing a propagation outcome.*
That is calibration on the graded quantity, not discovery, and R4's record
already shows the shape: `xi = 0.1` was a **post-hoc, ungraded diagnostic**
(departure D-7) precisely because it was reached for after the registered arm
diverged. A second, quieter version of the same failure: **reading `eps(U)`
off a run that wrote no time directory** — `latest_time` returns `0`, `0/U` is
the shipped baseline, and the ratio comes back at exactly 1.0000, which looks
physical and is not (R4 §5; its `score_aposteriori.py` refuses this and the
refusal must carry forward).

**And the measured warning against this option as briefed.** Constraint 3 of §1:
the discovered `R` alone diverges on all six hills and on `CBFS13700` with
`b^Delta` identically zero. **A remedy aimed at `b^Delta` amplitude alone cannot
address that**, so A is measured in advance to be insufficient on the separated
flows unless the discovered `R` changes too. That is what A′ is for.

---

### A′. Amplitude / realisability control on the pair — `b^Delta` **and** `R`

**What it would establish.** The same question as A, asked of the correction pair
that R4 actually fitted. Because `R`-only already diverges on the separated
flows, this is the smallest experiment that could plausibly move the
a-posteriori verdict rather than confirm the R-only measurement at higher cost.

**What it would cost.**

```
constrained fit (both targets)     2 x 0.262   = 0.524 core-h
b^Delta-scaled propagation sweep   12 x 0.259  = 3.108 core-h
R-scaled propagation sweep         (measured analogue: the 11-case R-only
                                    sweep at 1.588 core-h, scaled to 12)
                                   1.588 x 12/11 = 1.733 core-h
                                                 -------------
                          planning figure         5.365 core-h
                          5.365 x 0.0513        = $0.275
                          floor (all diverge)     0.524 + 0.026 x 2 = 0.576 core-h = $0.030
```

**What would have to be pre-registered.** Everything under A, plus: **the `R`
control is a single scalar or a single constraint applied uniformly**, and
**the same value everywhere**. A per-family or per-case scaling is **per-case
switching**, which Charter §22.1 says is not a model.

**The failure mode that makes it NOT A RESULT.** A's failure mode, plus: a
scaling tuned per family to buy convergence. If the record ends up saying "the
model converges with `xi_duct` and `xi_hill`", **there is no model** — there are
two, and the one-model doctrine is the thing R4 exists inside.

---

### B. Re-open R2's ranking

`docs/closure/R2_SHORTLIST_MEMO.md` ranked **1 SpaRTA-class, 2 FIML-C, 3
TBNN-class**, and Sanaa picked SpaRTA-class on 2026-08-21 (*"R3: Sparta"*,
recorded in that file and in D443/D444). **Re-opening the ranking is a
re-opening of R3, which is Sanaa's decision and not the lab's** (Charter §22.7).
What follows is what the memo's measured numbers say each alternative would cost
**here**, priced at R4's rates.

**What the memo said would change the ranking**, quoted so the trigger is
explicit: *"A working field-inversion adjoint here would move FIML-C to rank
1"*; *"A TBNN-class model with an `R`/`kDeficit` head, shown a-posteriori, would
collapse the gap to SpaRTA-class"*. **Neither has happened.** What has happened
is that rank 1's build ladder returned GATE FAIL with a working ceiling, which
the memo did not anticipate and which is new information for a re-ranking.

#### B1 — FIML-C (rank 2)

**What it would establish.** Whether a correction inside the transported
equations, trained by field inversion, propagates here. It carries the corpus's
only cross-solver portability demonstration (Singh, Medida & Duraisamy 2017:
trained on S814 at `Re = 1e6`/`2e6`, applied to S805/S809/S814 across
`1e6/2e6/3e6`, hump bubble *"15 % more accurate"*, overhead *"< 10 %"*, and the
trained model reproduced in **AcuSolve**, a different unstructured FE solver —
`R2_SHORTLIST_MEMO.md` §3).

**What it would cost — and this cannot be costed from R4's rates, because R4 ran
no adjoint.** What R4's rates *can* supply is a floor:

```
assume one field inversion = N primal + adjoint pairs, N = 100 (an ESTIMATE)
assume one adjoint = one primal solve (an optimistic FLOOR; R2 memo §3 records
      the transonic adjoint DIVERGED at 21,840 / 42,120 / 79,560 / 99,840 cells)

one training case at the mean converged solve cost:
      100 x 2 x 0.259  = 51.8 core-h  =  $2.66
a 12-case build:
      12 x 51.8        = 621.6 core-h =  $31.89
                       -> ABOVE the 487 core-h pre-authorisation (Charter §18):
                          STOP AND COST BEFORE LAUNCH

a single-duct pilot on the cheapest case (AR_1_Ret_180 CEILING solve = 11 s):
      100 x 2 x 11 s   = 2,200 s = 0.611 core-h = $0.031
```

**So the affordable arm is a single-duct pilot at $0.031, and the real cost is
adjoint development, which is not a core-hour figure.** The R2 memo prices it as
*"tens of core-hours, with a real risk of not converging"* and records that **no
per-cell field design variable exists anywhere in `sdk/` or `cases/`**.

**What would have to be pre-registered.** A **finite-difference verification
table for the field design-variable class, before any inverted field is
reported** — the R2 memo quotes `R5_ADJOINT_CONDITIONING.md` verbatim: *"No
finite-difference gradient verification was performed, on any configuration, at
any point in this investigation."* Plus the continuity, train-mean and
comparator clauses common to every option.

**The failure mode that makes it NOT A RESULT.** An inverted field produced by a
gradient never FD-verified for **this** design-variable class. The engine that
carries over under doctrine R4 is FD-verified for **shape/patchV**
(`R2_SHORTLIST_MEMO.md` §3, quoting `DAFOAM_CASE_STATUS.md`'s own adjoint-gate
labels, which are not this charter's verdict vocabulary: CD/patchV 0.23 % PASS,
CL/shape 1.67 % PASS, **CD/shape FAIL** on a sign-flipped component), and a
gradient verified for the wrong class is not a verified gradient.

#### B2 — TBNN-class with an `R` / `kDeficit` head (rank 3)

**What it would establish.** Whether the SpaRTA failure is about **symbolic
sparsity** rather than about the correction pair — replacing the symbolic
expression with a network while keeping `b^Delta + R`.

**What it would cost.**

```
TBRF/TBNN training, measured in this lab   = 17.79 core-h = $0.913
      (R2_SHORTLIST_MEMO.md §4: 52 forests x 100 trees, 9.69 preregistered
       + 8.10 post-hoc)
R / kDeficit head                          = UNESTIMATED - the memo says so
      verbatim: "Adding an `R` head is the real cost and is unestimated"
12-case propagation sweep   12 x 0.259     = 3.108 core-h = $0.159
                                             -------------
                                             20.898 core-h = $1.072 + unknown
```

**What would have to be pre-registered.** Everything under A, and the
realisability clause is not optional here: this lab's own TBNN lane put
**6.47–15.34 %** of test cells outside the barycentric triangle against a truth
of **0.79 %** and SST's **0.10 %**, reaching `||b||_F ~ 1.48e+07` on the hump,
and its TBRF put **19.2 %** on `CBFS13700` (`R2_SHORTLIST_MEMO.md` §4,
Charter §4).

**The failure mode that makes it NOT A RESULT.** **It is the same failure R4 just
measured, at twenty times the compute.** R4's discovered model violated
realisability on **19.06 %** of `CBFS13700` cells; the lab's TBRF violated on
**19.2 %** of the same case. A TBNN + `R` head with no registered realisability
threshold would reproduce R4's GATE FAIL for **$1.07** instead of **$0.19**, and
the a-priori/a-posteriori inversion the R2 memo documents means a good a-priori
`b` score would not warn of it.

---

### C. Fix the `omega` source and complete the 15 incomplete hill targets

**This is a prerequisite for any option that needs more training data**, which is
A, A′ and B2. It is not itself a model result.

**What it would establish.** Whether the 15 hills that failed extraction can be
extracted at all, and — if they can — whether the discovered term sets and
coefficients move when the hills family enters the fit through **21** members
instead of **6**. R4 states the exposure plainly: the six that converged are
**not a random sample**; they are the ones whose frozen `omega` equation happened
not to go negative, which correlates with the flow
(`R4_sparta_build/RESULTS.md` §7, §11.3(c)).

**The mechanism is already diagnosed.** `kOmegaSSTFrozen.C` carries the explicit
source `gamma*(PkLim + Rterm)/max(nut, 1e-12)`; the baseline hills carry `nut`
down to **5.55e-12**, so the source is amplified by up to **1e11** where the
numerator is not simultaneously small, and that is where `omega` goes negative
(`RESULTS.md` §2.3). **Four repairs were tested and all four failed** — flooring
`k_LES ≤ 0` cells at `1e-4` and at `1e-2` of mean `k_LES`, inserting
`div(phi,omega) Gauss linearUpwind grad(U)` (the 21 hills are the only benchmark
family whose `fvSchemes` declares none), and raising the backstop 5,000 → 20,000,
which returned `max rel domega = 0.105158858322751` **identical to fifteen
significant figures** — a limit cycle, not slow convergence. **The untried repair
is a bounded, positivity-preserving discretisation of that source**, and R4 did
not write one because doing so **changes the extraction operator** that
`PREREGISTRATION.md` §5 registers as the W2-validated path — *"that is a new
preregistration, not a repair inside this one."*

**What it would cost.**

```
C  (the repair, and re-extraction of all 27 under one operator)
       27-case frozen re-extraction               = 0.184 core-h = $0.009
       identity re-validation on PHLL10595 and CBFS13700
             (byte comparison against the W2 record)  ~ 0
                                                    -------------
                                                      0.184 core-h = $0.009

C2 (C, then rebuilding R4's fit and propagation on the enlarged 27-case set)
       C                                          = 0.184 core-h
       FS3 selection pass                         = 0.262 core-h
       three 27-case configuration sweeps
             3 x 6.234                            = 18.702 core-h
                                                    --------------
                                                     19.148 core-h = $0.982
```

**C is the cheapest item on this memo by a factor of twenty**, and it is the only
one that removes a known bias from every coefficient the line currently holds.

**What would have to be pre-registered.**
1. **The new extraction operator, in full**, and the fact that it *is* a new
   operator — the frozen R4 targets and the repaired targets are **different
   quantities** and no number crosses between them without saying so.
2. **The identity test that the operator must still pass**: `kOmegaSSTFrozen`'s
   defining identity to **8.8e-14** on PH10595 and **1.7e-13** on `CBFS13700`
   (`PREREGISTRATION.md` §5, from `../Schmelzer2020_SpaRTA/RESULTS.md` §3), and
   the byte-identical reproduction of the W2 record on both cases
   (`R4_sparta_build/RESULTS.md` §2.1) — registered as a **gate**, before the
   repair is written.
3. **The complete six-condition completion rule**, including *"`omega` bounded
   before the field write ⇒ INCOMPLETE"*, registered up front. In R4 that
   condition was added **after** first compute (departure D-4) and it is what
   reclassified two hills that reported `CONVERGED (settle criterion) at
   iteration 51` with an `L2(R)` drift of **exactly 0.0** after being clipped
   flat.
4. **What happens if the repair converges some hills and not others** — a
   registered rule, not a judgement made afterwards.

**The failure mode that makes it NOT A RESULT.**
*The repaired operator converges the hills but no longer reproduces the record.*
If the identity or the byte-identical W2 reproduction breaks, the targets are a
different quantity, every comparison to R4 is void, and the enlarged dataset
carries an unmeasured operator error rather than fifteen extra hills.
*And the sharper one:* **a repair that converges by clipping flat**. R4 measured
exactly this shape — an `omega` solve with an initial residual of 0.933 followed
by `bounding omega, min: -193215225.4`, after which `omega initRes = 9.26e-18`
and `max rel domega = 0` at every subsequent iteration, reported as CONVERGED.
**A settle criterion that measures change cannot tell a converged field from a
clipped one**, and a plausible-looking field from a broken repair is the L-221
failure shape.

---

### D. Do nothing further on discovery; bank the harness result

**What it would establish — and it is already established; banking it is a
documentation act, not an experiment.** That this lab has a **measured,
reproducible frozen-field ceiling**: an extraction operator that reproduces an
independent record byte-for-byte, an injection path that carries the truth into a
re-solved field, comparators that reduce to an identity, and scorers that refuse
to read a field that was never written. Plus the negative result, which is a
result: **a SpaRTA-class model discovered by three registered selection methods
at three seeds, on the twelve training cases that survived extraction, misses the
train-mean bar and cannot be propagated.**

**What it would cost.** **0.000 core-h, $0.000.** No solver run.

**What would have to be pre-registered.** Nothing — there is no run. What it
would need instead is the **Repo 2 release gate**, which is Sanaa's alone
(doctrine Part 5; Charter §22.8), including the **SONNET cold-reader gate** and
the leakage-vocabulary grep before any push, and **R6's internal-scoring
phrasing** (doctrine open action 4), which is already on her desk and already
blocking.

**The failure mode that makes it NOT A RESULT.** *Presenting the ceiling as a
model result.* The ceiling reads `bijDelta` and `kDeficit` **extracted from the
LES/DNS truth**; it is an upper bound available only when the answer is already
known, it predicts nothing, and a surface that says "our closure recovers
reattachment to within 3.4 % of the LES" without saying the correction was
extracted from the DNS has made the claim R4's boundary report
(`R4_sparta_build/RESULTS.md` §11) exists to prevent. A second failure mode:
**banking closes nothing else** — R6 stays NOT DONE, FS6 stays NOT DONE, the
hump stays unmeasured for every class, and the 15 hills stay unextracted.

---

## 4. Two amendment candidates carried forward for the NEXT preregistration

**Neither is applied to R4's frozen file.** `PREREGISTRATION.md` (sha256
`058444309f87a9e1f6faccca2086bf16364df7a06bb7702d155c35b1fcacbbe8`) was verified
at lane start and at every commit and **was never edited**; **every R4 row was
graded as written**, and neither candidate moves any R4 verdict. They are
recorded in `R4_sparta_build/RESULTS.md` §11.7 and in the R4 docket row, and are
repeated here so that whoever writes the next preregistration does not have to
find them.

**1. No realisability threshold is registered in R4's §6 — Charter §4's omission,
repeated.** §6 requires realisability of the total `tau` to be *reported* at
`tol = 1e-6` beside the truth's own rate and registers **no bar**, so gate **G4**
cannot fail. A model outside the realisable set on **19.1 %** of `CBFS13700`
cells, with `max ||b^Delta||_F = 7.559` against a realisable bound near
`sqrt(2/3) = 0.8165`, reached propagation without failing on that axis
(`R4_sparta_build/artefacts/apriori_realisability.json`; `RESULTS.md` §4.6, §6).
**Charter §4 exists because `Ling2016_TBNN` was on track for a PASS in exactly
that configuration**, and it supplies the wording to freeze — the 3x-the-truth
violating-fraction clause and the 2x-`sqrt(2/3)` norm clause quoted in §3A above.
**Any option in §3 that fits or propagates a `b` must register it.**

**2. The continuity gate's `1e-4` is dimensional.** `sum local div(U)` carries
dimensions; the ducts run at a bulk velocity of ~37.5 m/s on a 1 mm half-height
and the hills at ~1 m/s, so one absolute threshold does not mean the same thing
on the two families. It is what makes `AR_1_Ret_180`'s CEILING row **NOT
CONVERGED** at **1.0628e−04** while every hill row passes at **≤ 3.45e−07**
(`RESULTS.md` §5.3, gate G3). **That row is graded as written** (Charter §11); a
non-dimensional form is a candidate for the next file, **not a re-grade of this
one**.

---

## 5. RECOMMENDATION — this is a recommendation, and the choice is Sanaa's

**Marked as a recommendation.** The lab ranks and argues; under doctrine Part 3
R3 and Charter §22.7 it does not choose. **Sanaa decides.**

**Recommended: C first, then A′. Not B, on current evidence. D holds regardless.**

**C first, and it is close to free.** At **0.184 core-h / $0.009** it is the
cheapest item on this memo by a factor of twenty, and it is the only one that
removes a known bias rather than adding a model. Every coefficient the closure
line currently holds — `R = 2k[1.261646 − 42.82548 I1 − 31.54762 I2 +
14.28260 I2²](T1:A)`, `b^Δ = −7.550380 T2 − 16.07578 I2 T2 + 5.039083 T3`
(`R4_sparta_build/MODEL.md`) — is fitted on a hills family represented by **six
non-randomly-selected members out of twenty-one**, selected by which cases'
`omega` equation happened not to go negative. **Until that is fixed, no fit on
this data can be told apart from a fit on a biased sample**, and every option
that trains anything inherits the bias. The mechanism is already diagnosed to the
`1/nu_t` amplification; the four failed repairs are recorded so no one retries
them; and the untried repair is named. It carries a real risk — the extraction
operator changes, so the identity gate must be registered *before* the repair is
written — but that risk is registrable and the cost is nine tenths of a cent.

**Then A′, not A.** A as briefed controls `b^Delta` amplitude alone, and R4
already measured that this cannot be enough: with `b^Delta` switched off
**entirely**, the discovered `R` **still diverges on all six hills and on
`CBFS13700`**, and the paper's own `xi = 0.1` converges three ducts and no
separated flow at all (`RESULTS.md` §5.4). Registering an amplitude or
realisability control on **`b^Delta` alone** would spend **$0.186** to re-measure
a divergence whose cause is partly elsewhere. **A′ — one uniformly-applied
control on the pair, registered in `MODEL.md` before propagation, with Charter
§4's numeric realisability clause in the verdict ladder — is the smallest
experiment that could move the a-posteriori verdict rather than confirm the
R-only row**, at **5.365 core-h / $0.275**, or **$0.030** if it diverges early
and says so quickly. Run after C, it also answers the question C opens: whether
the term sets move on 21 hills.

**Not B, on current evidence, and the reason is specific to each.** **B1's
blocker is unchanged since the R2 memo was written**: no per-cell field design
variable exists anywhere in `sdk/` or `cases/`, and the FD-verified adjoint is
verified for the wrong design-variable class. At full scale it is **621.6
core-h**, above Charter §18's 487-core-h pre-authorisation. If Sanaa wants the
option kept alive cheaply, the **single-duct pilot at 0.611 core-h / $0.031** is
the right size — but it is an adjoint-development decision, not a compute
decision. **B2 would spend $1.07 to reproduce, at twenty times the cost, the
failure R4 just measured for $0.19**: the lab's own TBRF violates realisability
on **19.2 %** of `CBFS13700` and R4's discovered model violated on **19.06 %** of
the same case — the same number, the same case, two model classes. The memo's own
trigger for promoting either class has not been met.

**D holds regardless, and it should be said plainly: the harness result is
already banked in the record whichever option is chosen.**
`R4_sparta_build/RESULTS.md` §11 states what was established, what was not, and
where the boundary lies. **What D adds is only the decision to stop discovery**,
and that is the one option here that closes the line rather than advancing it.
Choosing it would be defensible — the ceiling is a real, reproducible,
independently-corroborated measurement and the negative result is a result — but
it leaves the 15 hills unextracted, R6 NOT DONE and the hump unmeasured for every
class.

**Two sentences, if only two are read.** **Fix the extraction first — it costs
$0.009 and it is the only thing standing between the closure line and a fit whose
training sample is not selected by which cases happened to converge.** **Then, if
discovery continues, register the amplitude and realisability control on the pair
rather than on `b^Delta` alone, because the `R`-only arm has already measured
that `b^Delta` alone is not where the divergence lives.**

**THE CHOICE IS SANAA'S.** Re-opening R2's ranking is a re-opening of R3 and is
hers under Charter §22.7. **The Repo 2 release and the one pre-registered
zero-shot scoring call are hers alone; this lane ran neither, opened no test or
validation case, and prepared no submission.**

---

## 6. What this memo cannot see

* **It has no measurement of any option's outcome.** Every core-hour figure above
  is a projection from R4's measured rates onto work that has not been run, and
  the estimates inside them — the `x2` on a constrained fit, `N = 100` inversion
  iterations, one adjoint costed as one primal — are labelled as estimates where
  they appear and are not measurements.
* **It cannot say whether the untried `omega`-source repair converges.** R4 says
  the same: *"whether a bounded, positivity-preserving discretisation of that
  source would converge is **not known**, because writing one would change the
  extraction operator"* (`R4_sparta_build/RESULTS.md` §7). Option C's cost is the
  cost of finding out, not the cost of a known fix.
* **It cannot say whether any option generalises.** Every number it rests on is a
  training-family number. No TEST or validation case has been opened by any lane
  in this rebuild, and none is opened by reading this memo.
* **It carries no hump number for any class**, because none exists
  (`R2_SHORTLIST_MEMO.md` §6). The hump is now *checkable* rather than blocked
  (`R4_sparta_build/PREREGISTRATION.md` Addendum A1;
  `cases/RANS_LES_closure_models/NASA_hump_gate/RESULTS.md` gate B-G0b,
  **PASS** at `Δ = 1.77e-4`), which raises what a coverage report must promise,
  not what any lane may look at.
* **It prices no adjoint development**, because nothing comparable has been run
  here; the R2 memo's *"tens of core-hours, with a real risk of not converging"*
  is the only figure available and it is that memo's estimate, not a measurement.
* **It does not re-rank R2.** It prices two of R2's alternatives at R4's measured
  rates and reports what has and has not changed since that memo was written.
  **A re-ranking is R2 work and a re-pick is R3, which is Sanaa's.**
* **No model-form band is quoted anywhere above.** Charter §22.4 (v1.1.2) would
  require that any band shown here name the axis it cannot see, and the
  eigenspace family's blind spot is `k`-magnitude — the same axis as `R`, the
  correction this line exists to carry. None is shown, so nothing is presented as
  bounding an error it cannot see.
