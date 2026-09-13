# Curriculum D6R2C — PRE-REGISTRATION for the GRADIENT SPOT-CHECK (arm `GS1`)

**Item id:** `D6R2C-GS1`, arm **`GS1`**. Sanaa's item 10 requires a *"gradient spot-check table"*, and
her *"what is not done here"* excludes only the **full FD sweep**. **The spot-check is owed and has
never been done.**
**Version 1.0 — DRAFT, NOT YET FROZEN.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`.
**This item has burned 0 core-min and started 0 containers at the time of writing.**
**The rule-2 pre-compute condition, checked:** the registered run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-GS1-a2-wing-gradient-spotcheck` **does not exist**.
It is frozen by the commit that introduces this file **together with its three instruments** (§11).
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).

---

## 0. A CORRECTION TO THE DESIGN THE SUPERVISOR APPROVED, FLAGGED AT THE TOP SO IT IS RULED ON AND NOT DISCOVERED

The design put up and approved said **"every FD evaluation warm-started from the IDENTICAL transferred
field"**. **IT IS NOT DELIVERABLE IN ONE CONTAINER AND IT IS NOT WHAT THIS DOCUMENT REGISTERS.**

The evidence is the lab's own frozen record, `PREREGISTRATION_AFTER_ITEMS.md` §4a, **measured**:
*"each state after the first is warm-started from the previous state's converged fields."* DAFoam reads
`processorN/0/` **once**, at `prob.setup()`; every `run_model()` after that begins where the previous one
finished. **So the two members of each central-difference pair DO NOT start from the same field.**

**THAT IS KNOWN IN ADVANCE, DELIBERATELY NOT REMOVED, AND MEASURED INSTEAD.** The alternative — restart
the container per evaluation and re-transfer — was costed at **~216 core-min against ~100** and
**rejected on evidence order, not on price**: its entire benefit rests on an inference about where the
noise floor sits, and **this arm measures that floor rather than assuming it** (§2c). If the measured
spread makes the shape ladder unusable, **the per-evaluation restart is the registered successor,
bought by a number instead of by an approval.**

*A later reader must be able to see that the sequential contamination was known, chosen and measured —
because the alternative reading, that nobody noticed the pairs start from different states, is the one
they will otherwise reach.*

---

## 1. WHAT IS BEING CHECKED, AND AGAINST WHICH RECORD

### 1a. THE FINDING THAT COMES FIRST — THE LAB'S OWN FD CAPABILITY WOULD HAVE RETURNED NOISE

`d6r2c_opt_runScript.py:572` carries a `check_totals` task:

```python
prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
```

**It exists and was NEVER ENTERED** — zero occurrences in `O_mp`'s run log, no artefact on disk. *(The
brief for this item said `check_totals` "appears zero times in `O_mp`"; the precise statement is that
the branch is present at `:572` and was never executed, and the distinction matters because it means the
capability was registered and unused rather than absent.)*

**AND HAD IT EVER RUN AS WRITTEN IT WOULD HAVE BEEN UNINFORMATIVE FOR THE VERY DV WITH THE LARGEST
SHAPE SENSITIVITY.** At `step = 1e-3`, `shape[84]`'s central-difference signal is `2h|g| = 2.479e-06`
against a measured noise of `8.765e-07` (`N-D48`) — **a signal-to-noise ratio of 2.8**. It would also
have swept all 106 DVs at two evaluations each: **212 primals**.

**That is an eighth member of this item's defect family: a clause that would have produced a number, and
the number would have been meaningless.** The seven before it: a grading path that did not exist
(L-579); a threshold whose branch was never entered; a cap that was a different number in two files; a
pin that was never read; a count in the wrong unit; a dependency a pin did not cover; and a clause that
defaults to pass when its input is missing.

### 1b. THE ADJOINT AT THE OPTIMUM — THE RECORD, AND THE METHOD THAT FOUND IT

`O_mp/OptView.hst` (SQLite, md5 **`2a96b47a19e84e40a95c30e1634ce356`**) holds **52 `funcsSens`
records**.

> **THE RECORD IS `key = 172`, `iter = 86`, `isMajor = True`.**

**AND THE METHOD IS REGISTERED, NOT JUST THE RESULT.** It was found by comparing **each** record's
`xuser` shape vector against `n = 88`'s from `O_mp/d6r2c_evals.jsonl`, pinned at md5
**`2c0b8143caad198cd2e21d8047986aa3`**, and taking the exact match: **`max|Δshape| = 0.000e+00`** — an
exact match, not a nearest one. The design point the sweep perturbs is read from that same pinned
record, `F` record **`n = 88`, `fail = 0`**, and the producer refuses if either the md5 or the `fail`
flag is not what is registered here.

> **THE LAST `funcsSens` RECORD IS `key = 173` AND IS NOT THE ONE AT THE FINAL DESIGN POINT.**
> **Taking the last record would have been the obvious move and it would have been wrong** — the same
> shape as reading an index as a count. Naming the method inoculates the next reader.

### 1c. THE THREE DESIGN VARIABLES, EACH DERIVED FROM THAT RECORD

| DV | `dJ/d(dv)`, driver-scaled | why this one |
|---|---|---|
| **`shape[84]`** | **`-0.0012395965734695029`** | max `\|g\|` over the 96 shape DVs; **7.4× the median** `\|g\|` of `1.679709e-04` |
| **`twist[2]`** | **`0.0063348068779340615`** | max `\|g\|` over the 7 twist DVs |
| **`patchV_cl05[1]`** (AoA) | **`0.01719085469787987`** | max over the trim DVs, and **the largest single sensitivity in the whole problem** — 13.9× `shape[84]`. `U0` is pinned and never free, so the AoA component is the only candidate |

**A LIMIT ON THE FIRST CHOICE, AND IT IS NOT A FOOTNOTE.** `shape[83] = -0.0012394586288117077` is
**within 0.011 %** of `shape[84]`. They are a near-degenerate pair.

> **`shape[84]` IS "THE MAXIMUM-SENSITIVITY SHAPE DV" BY A MARGIN THIS EXPERIMENT CANNOT RESOLVE.**
> The FD checks the adjoint's **value** at 84, which is unaffected by the tie. **The CHOICE is not a
> demonstrated ranking and is not reported as one.**

---

## 2. THE DESIGN

### 2a. THE SPACE — DRIVER-SCALED, BECAUSE THAT IS THE SPACE THE ADJOINT IS REPORTED IN

Perturbations are applied in the **driver-scaled** space, and the adjoint is read in the driver-scaled
space, so the comparison is like-for-like. **The parent burned two arms on scaled-versus-physical**
(`PREREGISTRATION.md` ADDENDUM 1, `PREREGISTRATION_AFTER_ITEMS.md` ADDENDUM 2) and this document does
not add a third. The scalers are read from OpenMDAO's own metadata, **never re-typed**, and a guard that
cannot **measure** the divisor **refuses** rather than assuming `1.0`.

### 2b. THE LADDER — FOUR STEPS, EXTENDING **UP**

**`h ∈ {1e-1, 1e-2, 1e-3, 1e-4}`**, central differences, per DV. **Three steps is the minimum a plateau
can be read from; four gives three adjacent comparisons.**

**IT EXTENDS UP, AND THE ARITHMETIC IS WHY.** Signal is `2h|g|`; the measured noise is `8.765e-07`:

| DV | `h=1e-1` | `h=1e-2` | `h=1e-3` | `h=1e-4` |
|---|---|---|---|---|
| `shape[84]` | S/N **283** | **28** | **2.8** | **0.3** |
| `twist[2]` | 1446 | 145 | 14.5 | 1.4 |
| `patchV_cl05[1]` | 3923 | 392 | 39 | 3.9 |

**REGISTERED IN ADVANCE, BECAUSE IT MAY BE THE RESULT: for `shape[84]` only `h=1e-1` and `h=1e-2` clear
that noise, AND TWO POINTS ARE NOT A PLATEAU.** If `8.765e-07` is the right floor for this procedure,
**the charter's bright line is unreachable for shape** — not because the adjoint is wrong but because
the solver's own noise swamps the difference before the step is small enough to be asymptotic.

**AND A MEASURED WARNING AT THE OTHER END.** `N-D3` records, on a comparable case, that **the primal
fails to converge at `5e-2` and `1e-1`**. **The `h=1e-1` step may therefore stall.** A stalled step is a
**missing measurement** (§3a), not a gradient disagreement. **If it stalls and the small end is noise,
the usable window for shape may contain ONE step or NONE, and that is a finding about this
configuration, reported as one and never dressed as a plateau.**

### 2c. SIX UNPERTURBED EVALUATIONS — THE SPREAD, MEASURED WHERE IT LIVES

**Two before the ladder, one after each DV block, one at the end.** Reported **first** in the record, so
a reader has the scatter in hand before the ladder's numbers.

**WHY SIX AND WHY SPREAD OUT.** Two points give one difference at one instant. Six spread through the
arm, under exactly the sequential warm-starting every FD pair experiences, **distinguish a CONSTANT
scatter from one that GROWS through the arm** — and those have completely different implications for
whether the later DVs' ladders can be believed at all.

> **REPORTED, NEVER GATED.** It is **"the observed spread between identical evaluations"**, with the
> numbers. **It is NOT a standard deviation and it is NOT a floor.** Six points are six points.
> **A threshold derived in-run is what rule 2 forbids**, so no gate reads it; every step's
> signal-to-spread ratio is printed beside it so a reader can judge the ladder for themselves.

### 2d. THE WARM START — REUSED, NOT REINVENTED

The arm is warm-started **once** by `d6r2c_fm6_init.py`'s cell-for-cell index transfer, **reused
unchanged at md5 `75bf53d8e798980332ef8dfdcc25b0c6`**. That is the one thing measured on 2026-09-13
(arm `FM8`) to make this configuration converge at the optimum, and **~60 % of `O_mp`'s primal
evaluations failed at large `|shape|` without it** — the optimum being at large `|shape|`.

**What it licenses and what it does not:** the FD estimate is conditioned on the initial field. It is
**not** a cold-start finite difference and is not reported as one.

---

## 3. THE GATES, FROZEN

Graded by **`d6r2c_gs1_grade.py --item GS1`**, after the container exits. **The grader recomputes every
FD estimate from the two `J` values** rather than trusting the producer's arithmetic, and refuses on a
disagreement above `1.0e-12`.

- **`G1` — COMPLETION AND HYGIENE.** `rc = 0`; **24 FD evaluations and 6 unperturbed evaluations
  present**, each with `fail = 0` and finite `J`; a `FOOTER`; every artefact newer than the arm's own
  age datum; **zero** files under the arm newer than the datum owned by uid 0 or gid 0; the §8 cap not
  crossed. `primalMinResTol = 1.0e-8` — **the tolerance the graded run uses, NEVER loosened**
  (`DAFOAM_CHARTER` §3; `N-D3` measures that a loose primal tolerance, not the step, can own the
  disagreement: 25.9/32.0/32.2 % at `1e-6` against 0.032 % at `1e-8`).
- **`G2` — THE ADJOINT IS THE REGISTERED ONE. THE EXTERNAL ANCHOR (L-588).** The producer's recorded
  adjoint equals §1c's three values; the record identity equals `key = 172, iter = 86`; and the
  `OptView.hst`, runscript and inherited-record md5s equal their pins. **Every one of these was produced
  by a run this arm did not perform and fixed before it ran.**
The producer writes **`d6r2c_gs1.jsonl`** into the arm directory as it goes — a `HEADER` carrying the
adjoint and the pins, one `EVAL` record per evaluation, a `FOOTER` — and `G1` grades that file. Its
absence is a refusal (`REFUSE_MISSING_RECORD`), not a pass.

- **`G3` — THE TABLE EXISTS BEFORE ANY PLATEAU OR AGREEMENT CLAIM.** A **refusal, not a gate**
  (`REFUSE_NO_TABLE`), the same discipline as the sibling registration's `D5`.
  **FAILED STEPS APPEAR AS ROWS.** `DAFOAM_CHARTER` §3: *"a sweep that hides its failed steps is
  reporting a plateau it has not measured."*
- **`G4` — THE PLATEAU, PER COMPONENT.** `PLATEAU_MIN_STEPS = 3` consecutive steps whose FD estimates
  agree pairwise within **`PLATEAU_TOL = 5.0e-3 × |adjoint|`**. `N-D3`: **plateau membership is a
  PER-COMPONENT property and the vector norm can dip where no component supports it.**

**LABELS.** `PASS` = `G1 ∧ G2 ∧ G4` for **all three** components. `GATE FAIL` = `G1 ∧ G2` hold and `G4`
misses for at least one component, **with which component named and the full table printed**.
`NOT A RESULT` = `G1` or `G2` fails, or the cap is crossed. `G3` is a refusal, not a label.
**No other label and no synonyms** (rule 1).

### 3a. A STALLED FD EVALUATION — DECIDED IN ADVANCE

> **A stalled or absent evaluation is a MISSING MEASUREMENT, NOT A GRADIENT DISAGREEMENT.** It is
> recorded **as a row** with its status, **never averaged in, never interpolated over**, and
> **A LADDER WITH A HOLE CANNOT BE SAID TO SHOW A PLATEAU.** `primalMinResTol` is never loosened to
> make one converge.

### 3b. `PLATEAU_TOL = 5.0e-3` — DERIVED, NOT CHOSEN

`N-D3` measures this stack's flat region on a comparable case as **"dead flat at 2.5–3.0 %"** from
`1e-4` to `3e-2`. **The width of that flat band is 0.5 percentage points of the adjoint value**, so
adjacent FD estimates inside a plateau agree to within **`5.0e-3 × |adjoint|`**. That is the threshold,
and it comes from a measurement rather than from taste.

**`PLATEAU_MIN_STEPS = 3`, because two points are a line.** Any two numbers agree to within something;
three is the smallest set that can show a *flat region* rather than a coincidence.

### 3c. THE ORDER IS PART OF THE REGISTRATION

The two unperturbed evaluations come **first**; one follows each DV block; one ends the arm. **Ordering
is free and it is not an implementation detail** — a reader must have the scatter before the ladder, and
the drift track must be interleaved to be a drift track at all.

### 3d. `primalMinResTol` IS NEVER LOOSENED

Not to make a step converge, not to widen a plateau, not at all.

### 3e. THE FM7 LESSON, CARRIED — A WARM-START REFUSAL

`FM7` transferred every field correctly and **the solver never saw them**, and the floor that followed
looked exactly like a refutation of the registered change. **You cannot refute a change that did not
take effect.**

> On the **warped** mesh a freestream start produces `p initRes = 0.0003970258637` at `Time = 100` and a
> floor of `1.2161568500e-06` — **measured in `FM5`'s and `FM7`'s deform phase, in runs this arm did not
> perform.** If `GS1`'s **first** solve reproduces either **bit for bit**, the transfer did not reach the
> solver and **nothing in the sweep is evidence about a warm-started finite difference**.
> **A REFUSAL, NOT A GATE** — §11a registers this condition in words and this makes it executable
> (`VERIFICATION_CHARTER` §2d.1). **Equality, not proximity**: a control drives one ulp off each anchor
> and requires it **not** to fire.

---

## 4. WHAT THIS DELIVERS — THREE DIFFERENT BARS, KEPT APART

**Conflating these is the overclaim this item has spent a night retracting.**

| bar | delivered? |
|---|---|
| **Sanaa's item-10 spot-check table** | **YES** — the table, whatever it shows, plateau or not |
| **`DAFOAM_CHARTER` §2 per-component reporting** | **YES, for 3 of 106 components** |
| **`DAFOAM_CHARTER` §2 PASS / CONDITIONAL / FAIL band** | **NO.** That band is on an **AGGREGATE over the whole gradient vector** — the vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖`. **Three components of 106 cannot produce it, and this arm does not compute it.** The per-component errors are placed **against** the 5 %/15 % boundaries so a reader can see where they sit; **they are not the charter's verdict** |
| **`DAFOAM_CHARTER` bright line — a step PROVED to lie in the plateau** | **ONLY for components whose ladder actually shows one.** Per `N-D3` that is a per-component property. On §2b's arithmetic it may hold for AoA and twist and **not** for shape, and the record names which components it was met for rather than claiming the line |

---

## 5. THE ARM

| arm | what it is | ranks | run under this registration? |
|---|---|---|---|
| `GS1` | `stage → init → sweep`, one container, 30 evaluations | 4 | **YES** |

**Run root, NEW and separate:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-GS1-a2-wing-gradient-spotcheck`
The `D6R2C`, `D6R2C-AFTER`, `D6R2C-AFTER8R2` and `D6R2C-AFTER9R2` roots are all in `FORBIDDEN_ROOTS`.

**NO MESH IS GENERATED.** This arm runs on the **warped mesh at the optimum** — the same mesh `O_mp`
used. No fresh extrusion, no CGNS, no surface staging; those inputs are neither staged nor pinned.

**Phases.** `stage` builds the model so DAFoam creates the decomposition and **stops without solving**;
`init` writes `processorN/0/` **where the solver reads**; `sweep` runs the ladder. **`FM7` died because
the transfer landed after the decomposition the solver actually read**, and the launcher's selftest
asserts the phase order against the generated command block.

**Ranks, placement, hygiene** inherited unchanged: `RANKS = 4`, `CPUSET = 2,3,4,5`,
`--memory=20g --memory-swap=20g`, `--user 1000:1000 --group-add 1002`, never root, image pinned by
digest, `O_mp` mounted `:ro` and never written. **Nothing is stopped by a cap** (directive #17).

---

## 6. THE MONITOR

**None.** This arm is primal-only — no adjoint is solved, no optimiser runs — so the item-7 stop rules
have no iterate to act on. A primal that fails to converge is covered by `G1` as a **completion** gate
and by §3a as a **missing measurement**, not by a stop rule.

---

## 7. THE PLANTED CONTROL (rule 3)

`d6r2c_gs1_grade.py` plants **`PLANT = 1.234e-03`** into values it read back from disk and **REFUSES
(`exit 2`)** if any plant leaves the verdict at `PASS`. Five live plants: into the **recorded** adjoint
of each of the three DVs, and into the `J` of two FD evaluations.

**THE PLANT GOES INTO WHAT THE GRADER READS, NOT INTO ITS OWN REGISTERED COPY.** A plant into the
constant this file already holds would be compared against itself and would be **invisible by
construction** — which is how the first draft of this control passed while proving nothing, and it is
the same failure as a cap control that reads its own constant.

`--selftest` drives **52 grader controls and 41 producer controls**, both directions, on synthetic trees
in a temporary directory. **A failing control is driven for every gate**, anchored to this document's
literals **typed as assertions, not as sources**. Negative controls that must **not** fire: a re-grade;
a large unperturbed spread; one ulp off each warm-start anchor; a single off-plateau step that still
leaves three agreeing.
**Driven at this draft: `D6R2C_GS1_GRADE SELFTEST PASS n=52`, `D6R2C_GS1_FD SELFTEST PASS n=41`,
`D6R2C_GS1_LAUNCH SELFTEST PASS n=16`, all exit 0.**

---

## 8. COST, IN CORE-MINUTES, BEFORE THE RUN (rule 12)

**Measured anchor:** one primal evaluation of all three conditions = **48.081 s wall at 4 ranks**
(`O_mp/d6r2c_evals.jsonl`, `F` record `n = 2`, `eval_wall_s`).

| phase | wall s | basis |
|---|---|---|
| `stage` — model build, **no primal** | 30.0 | **ESTIMATE, LABELLED** |
| `init` — the transfer | 5.0 | **ESTIMATE, LABELLED** |
| `sweep` model load | 30.0 | **ESTIMATE, LABELLED** |
| 24 FD + 6 unperturbed evaluations | 1442.4 | `30 × 48.081`, **measured anchor** |
| **TOTAL** | **1507.4** | |

```
PREDICTION      1507.4 s × 4 ranks / 60 = 100.495 core-min
REGISTERED CAP  3.00 × 100.495          = 301.485 core-min
```

**THE CAP IS 3.00× THE REGISTERED PREDICTION, NOT 3× AN UNROUNDED INTERMEDIATE.** Those differ in the
last digit — `301.485` against `301.486` — and only the first is re-derivable from the two figures this
document states. **The selftest asserting this document's literal is what caught it.**

**Derived dollars:** `100.495 core-min = 1.675 core-h × $0.0513 = $0.0859`; at the cap, `$0.2578`.
**DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5); `cost_basis` **reported-by-owner**.

**THE WEAKEST NUMBERS, NAMED:** the three phase estimates (65 s total, 4.3 % of the prediction), none
measured because these phases have never run in this combination. **A misprediction there cannot reach
the cap**: the evaluations dominate at 95.7 %, and the arm would need every evaluation to take 3× its
measured time to cross.

**THE CAP HAS ONE SOURCE.** `d6r2c_gs1_grade.py` derives it from the prediction; the launcher **asks the
grader** after `G-FREEZE` has pinned it. A cap in two files is two things that can drift.

**Calibration row OWED** to `docs/COST_CALIBRATION.md` at completion (rule 12).

---

## 9. THE GRADED QUANTITY

```
J = 0.25 × CD04  +  0.50 × CD05  +  0.25 × CD06
targets: cl04 → CL = 0.400 , cl05 → CL = 0.500 , cl06 → CL = 0.600
```

Carried unchanged from `PREREGISTRATION.md` §1 — the objective `O_mp` was optimised against. The grader
**recomputes `J`** from the per-condition `CD` and these weights. *(A registration that does not state
the weights of its own objective has not registered its objective.)*

---

## 10. WHAT THIS ITEM DOES NOT CLAIM

- **It does not re-grade `O_mp`** (`GATE FAIL`), nor any closed arm.
- **It is not the full FD sweep.** Three components of 106; Sanaa excluded the full sweep and this is
  not it.
- **It does not produce the charter's aggregate band.** §4.
- **It does not claim a plateau exists.** §2b registers, with arithmetic, that for `shape[84]` the
  window may hold one step or none.
- **It does not claim `shape[84]` is demonstrably the most sensitive shape DV.** §1c: the margin over
  `shape[83]` is 0.011 %, below what this experiment can resolve.
- **It does not claim a cold-start finite difference.** §2d, and §0 for the sequential contamination.
- **It does not touch `primalMinResTol`.**
- **It does not verify the adjoint implementation.** It checks three components of one gradient at one
  design point against finite differences — a spot-check, which is what was asked for.

---

## 11. THE FROZEN INSTRUMENTS

| file | role | md5 at freeze | selftest |
|---|---|---|---|
| `d6r2c_gs1_grade.py` | **THE GRADING PATH** — `G1`–`G4`, the table, the plateau, the warm-start refusal, the plants, `--print-cap` | `a67791e31e7fb887972256499a40312d` | **`PASS n=52`** |
| `d6r2c_gs1_fd.py` | producer — the plan, the perturbations, the sweep | `663baeb6bfbec80ff6a9243169dbc7a4` | **`PASS n=41`** |
| `d6r2c_gs1_run_arm.sh` | launcher — `G-ROOT`, `G-BOX`, `G-FREEZE`, `G-DEPS`, `G-COLD`, digest pin, ledger. **Carries no cap of its own** | `6b7fa4ca9f28de2d06d2dad4d76f2c09` | **`PASS n=16`** |

**REUSED UNCHANGED, and the pins are the evidence that nothing else moved:**

| file | md5 |
|---|---|
| `d6r2c_fm6_init.py` — the transfer, from `FM8` | **`75bf53d8e798980332ef8dfdcc25b0c6`** |
| `d6r2c_opt_runScript.py` — the frozen model | **`2f2ae43a627146cf8e0f065b035ada4b`** |

**A DISCLOSURE ABOUT `G-DEPS` ON THIS ARM.** This arm's staged set has **no local inter-module
dependencies at all** — `d6r2c_gs1_fd.py` carries its own `load_frozen_model` and `d6r2c_fm6_init.py`
imports nothing local — so **`G-DEPS` is vacuously satisfied here**. **Saying so is the point:** a guard
that has nothing to find must not be reported as if it had searched and cleared something. Its failing
control is therefore driven against a **known-bad set from this same directory** (the set that killed
`FM6`), which proves **the guard is live** even though this arm gives it nothing to catch.

### 11a. THE HONEST GAP

**Neither `d6r2c_gs1_fd.py` nor this arm's phase sequence has ever been executed against the solver.**
`--selftest` drives the pure logic: the plan and its ordering, the perturbation arithmetic, the central
difference, the divisor guard and every refusal path.

**Specifically untested:** that `phase stage` leaves a decomposition without solving a primal. It
**refuses** (`REFUSE_NO_DECOMPOSITION`) if it does not, naming it a producer defect — **stopped,
`NOT A RESULT`, repaired under `VERIFICATION_CHARTER` §2d.1, and the grading path is not touched by such
a repair.**

---

## 12. THE CONSTANT SWEEP — THE STANDING PRE-FREEZE CHECK

Per `PREREGISTRATION_AFTER_ITEM8_R2.md` §8c: **every constant in every named instrument is compared
against the value this registration states for it, and the comparison is reported in full, matches
included.** The result is §12a.

### 12a. THE SWEEP, EVERY ROW

**29 rows. 29 OK. 0 mismatches.** Where a constant lives in **both** instruments — `ADJ_RECORD_KEY`,
`ADJ_RECORD_ITER`, `OPTVIEW_MD5`, `ADJOINT_SHAPE83`, `LADDER`, `N_UNPERTURBED`, `RUNSCRIPT_MD5`,
`EVALS_MD5`, `PLANT`, `DVS` — the two agree with each other as well as with this text.

Covered: the three adjoint values and the near-degenerate `shape[83]`; the record key and iter; the four
md5 pins; the ladder, `N_FD`, `N_UNPERTURBED`; `PLATEAU_TOL`, `PLATEAU_MIN_STEPS`; the charter's 5 % and
15 % boundaries; `PRIMAL_MIN_RES_TOL`; both warm-start anchors; `PREDICTION_CORE_MIN`, `CAP_FACTOR` and
the derived cap; `PLANT`; the objective weights; the DV list; `FINAL_RECORD_N`; the record filename; the
reused transfer's pin; and **the absence of a cap literal in the launcher**, which must not exist
because the cap has one source.

**TWO ROWS FAILED ON THE FIRST PASS AND BOTH WERE GAPS IN THIS DOCUMENT, NOT IN THE INSTRUMENTS** —
`EVALS_MD5` and the producer's record filename `d6r2c_gs1.jsonl` were carried by the code and stated
nowhere in the text, so a reader could not have checked those literals against anything. Closed at §1b
and §3. **That is the second time this check has caught exactly this, and both times the instruments
were right and the prose was short.**
