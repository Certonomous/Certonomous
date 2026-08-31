# Curriculum D19R — THE COMPRESSIBLE FD PLATEAU, RE-BRACKETED AT HALF-DECADES, WITH THE AGE DATUM REPAIRED AND A NAMED "NO PLATEAU EXISTS" VERDICT — PRE-REGISTRATION

**Frozen 2026-08-31 by the dafoam team's D19R lane, BEFORE any D19R run root exists. FREEZE ONLY: not enqueued, zero D19R solver core-minutes spent by this document.**

**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box. SUBMISSIONS ARE PARKED and sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Authority.** The same directive D19 carries — Sanaa 2026-08-31, `etc/sessions/2026-08-31T2037Z_sanaa_dafoam_compressible_multipoint.md`: *"yes so the dafoam team can do the compressible using the patched gradients, and we need to find a solution for multipoint optmization (both compresisble and incompressible"*. **This item is the FIRST half only — compressible, patched gradients, SINGLE POINT**, and it inherits D19 §0 and §12 verbatim in substance: it registers exactly one operating point, it produces no `SHIPPED`-row `G5` `PASS`, and **it does not release, weaken, satisfy or comment on SO-3b's gate.**

---

## 0. NAME, PRECEDENT, AND WHAT THIS ITEM IS A SUCCESSOR TO

**Successor id: `D19R`.** Precedent read from disk, not assigned by preference: this family suffixes a first successor with `R` and a second with `R2` — `curriculum_SO1a` → `curriculum_SO1aR`, `curriculum_SO2M` → `curriculum_SO2MR`, `curriculum_SO1b` → `curriculum_SO1bR`, `curriculum_SO1c` → `curriculum_SO1cR`, `curriculum_AV1` → `curriculum_AV1R`, `curriculum_AV2` → `curriculum_AV2R`, `curriculum_D12` → `curriculum_D12R` → `curriculum_D12R2`, `curriculum_SO3a` → `curriculum_SO3aR` → `curriculum_SO3aR2`. **`D19R` was verified free before being written into this document**: `cases/dafoam/ladder-a/A1/curriculum_D19R` did not exist, `/home/ubuntu/certonomous-runs/CURRICULUM-D19R*` matched nothing, and `grep -rn D19R docs/ cases/` returned no hit.

**Run root, registered and asserted ABSENT at freeze:** `/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau`. It does not exist at the time of this freeze, which is the condition `CLAUDE.md` rule 2 requires a pre-compute amendment to be able to state, and it is stated here.

### 0.1 D19 IS NOT EDITED, NOT REGRADED, AND NOT CONTRADICTED

**D19's gates closed at its first compute and its documents are frozen.** `cases/dafoam/ladder-a/A1/curriculum_D19/PREREGISTRATION.md` (`f032d94e`), its phase-1 instrument (`32bd000f`) and every phase-1 artefact under `/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt` are **evidence and stay exactly as they are**. This document does not rewrite them, does not re-grade them, and does not append to them. **D19 carries no graded verdict** — its grader refused, and a refusal is not a verdict.

**What D19 phase 1 actually produced, and why it is readable.** All four arms `rc=0`, `chain_rc=0`, all `PATCHED`, `G9` toolchain identity `OK` on all four, **8.683 core-min against a registered 8.7 — ratio 0.998**. Phase 2 correctly did not launch (`chain=PHASE1_COMPLETE_PHASE2_NOT_LAUNCHED_NOT_AUTHORISED`). The grader then refused on `G1`, an **infrastructure** clause (§2 below), not on a physics clause. Sanaa's universal rule of 2026-08-26 — *bookkeeping never voids physics* — is what permits this document to read D19's FD artefacts as evidence. **Every D19-derived number in this document is labelled as coming from an item whose grader refused, and no D19 number is quoted as a graded result anywhere.**

---

## 1. ⚠ THE BRIEF THAT COMMISSIONED THIS ITEM CONTAINED A FALSE PREMISE, AND IT IS CORRECTED HERE BEFORE ANYTHING IS REGISTERED

The commissioning brief instructed this lane to **"WIDEN THE STEP SWEEP … Extend the range in BOTH directions"**, on the reading that D15's `CD` `shape[7]` failure (fine side) and D16's `CL` `shape[6]` failure (coarse side) are *"two functionals, two components, failing off opposite ends — that is the plateau not being where it was looked for."*

**That reading is refuted by D19's own phase-1 sweep, which the brief's author had not yet read when the brief was written, and which this lane read before designing anything.** The `dafoam-supervisor` independently reached the same conclusion mid-task and withdrew the instruction; **this lane reproduced the supervisor's arithmetic from `S2/d19_S.json` before acting on it, and it reproduces exactly** (§1.2).

### 1.1 The measurement that settles it — D19's five-level `PATCHED` sweep

Read from `/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt/S2/d19_S.json`. `dCD` at each level, 3e-2 → 1e-5:

| component | 3e-2 | 1e-2 | 1e-3 | 1e-4 | 1e-5 |
|---|---|---|---|---|---|
| `shape[0]` | -7.161034e-03 | -7.228465e-03 | -7.216985e-03 | -7.175069e-03 | -6.748097e-03 |
| `shape[3]` | +9.441591e-03 | +9.321031e-03 | +9.296948e-03 | +9.337640e-03 | +9.765411e-03 |
| `shape[6]` | -8.726231e-03 | -1.366191e-02 | -1.413279e-02 | -1.418024e-02 | -1.446391e-02 |
| **`shape[7]`** | **-1.473205e-04** | **-2.089092e-04** | **-2.065253e-04** | **-1.618542e-04** | **+2.660843e-04** |
| `patchV[1]` | +1.955610e-03 | +1.959702e-03 | +1.959854e-03 | +1.964311e-03 | +2.003458e-03 |

**`shape[7]` on `CD` CHANGES SIGN between 1e-4 and 1e-5.** Adjacent-level deviations, coarse→fine, each normalised by the coarser member of the pair: `shape[7]` **41.81 % / 1.14 % / 21.63 % / 264.40 %**; `shape[6]` **56.56 % / 3.45 % / 0.34 % / 2.00 %**; `shape[0]` 0.94 / 0.16 / 0.58 / 5.95; `shape[3]` 1.28 / 0.26 / 0.44 / 4.58; `patchV[1]` 0.21 / 0.008 / 0.23 / 1.99.

**Four of five components have a clean plateau at 1e-3..1e-4.** `shape[6]`'s only bad neighbour is the 3e-2 **coarse** end. `shape[7]` is bad at both ends and everywhere in between, its best two-sided score over the whole five decades being **21.63 %** against a 10.0 % band.

### 1.2 Therefore: widening is measured-worse in both directions, and this item does NOT widen

- **Coarser than 3e-2 is measured-worse.** `shape[6]` is already 56.56 % off at 3e-2 and `shape[7]` 41.81 %. Independently, `ladder-a/A_stepsize_study.md` records that on this exact A1 ground **the primal FAILS at 5e-2 and 1e-1**. Registering steps there buys failed rows, not a plateau.
- **Finer than 1e-5 is measured-worse.** `shape[7]` has already changed sign at 1e-5 and is 264 % from its neighbour. Nothing flattens below it.
- **`shape[6]`'s cure is to DROP the coarse end, not to add a coarser one** — and this is corroborated across grounds: D16's independent failure was `CL` `shape[6]` at the **coarse** end (14.0978 % coarse / 1.1268 % fine). **The same component fails the same way on a different functional on a different ground.** That corroboration is stated here because it is what makes the coarse-end diagnosis a finding rather than one item's bad luck.

> **THE BRACKET IS THEREFORE UNCHANGED AT `[1e-5, 3e-2]` (`shape`) AND `[1e-4, 3e-1]` (`patchV`), AND WHAT CHANGES IS THE SPACING.** D19 sampled decades; a flat narrower than a decade is invisible to a decade grid. D19R samples **half-decades**, which is the only refinement the existing data leaves room for.

### 1.3 The trap this creates, named and closed before it can be sprung

A half-decade grid makes neighbour deviations **smaller for a purely geometric reason** — the neighbours are closer. Grading a two-sided plateau against half-decade neighbours would relax `G19-1b`'s strictness **by regridding**, without anybody editing a threshold. **Relaxing a gate threshold is reserved to Sanaa** (`CLAUDE.md` rule 9; `ESCALATION_CHARTER.md`), and it is not available to this lane by arithmetic any more than by edit.

> **FROZEN RULE `G19R-1b-N`.** The neighbour deviation at a candidate step `s` is computed against `s x 10` and `s / 10` — **DECADE-separated neighbours, identical in strictness to D19's `G19-1b`**. The half-decade points are additional candidate **centres**; they are **never** used as neighbours. A candidate is admissible only if **both** `s x 10` and `s / 10` are in the registered sweep.

---

## 2. ⚠ THE AGE DATUM — WHAT BROKE, WHY IT IS AN INSTRUMENT DEFECT, AND HOW IT IS REPAIRED WITHOUT WEAKENING

### 2.1 The refusal, and the cause, MEASURED

`D19_phase1_grade_20260831T215400Z.out`: `REFUSE G1`, `age_datum_moved` on `S1/0`, `recorded 1788213189`, `rederived_by_existence 1788213232`.

`CLAUDE.md` rule 4's age guard dates a run by *"the case's own `0/T`"*, on the premise that `0/T` *"is touched last at launch and so dates the run allowed to produce the answer"*. D19's launcher generalised that to "max mtime over the arm's `0/`, plus the file count" (`d19_run_arm.sh:230-246`).

**Measured by this lane, from the D19 run root:**

1. `S1/0/U.gz` mtime **1788213232** — exactly the rederived datum, 43 s into a 51 s run.
2. `S1/0/U.gz` carries `internalField nonuniform List<vector> 4032` — a **converged** field. `S1/0.orig/U` carries `internalField uniform (100 0 0)`. **The solver rewrote the file; it did not merely touch it.**
3. That write's `inout` patch reads `inletValue uniform (99.75762098674072 6.958236491079174 0)`. `atan(6.958236/99.757621) = 3.99 deg` — exactly the item's **last** evaluation, `patchV[1] − 0.01` off a 4.0 deg baseline. **The `patchV` design variable is applied by rewriting `0/U`'s inlet boundary condition**, and OpenFOAM writes the whole object — internalField included — under `writeCompression on`.
4. **IT IS NOT A SERIAL-ARM DEFECT, and this corrects the triage handed to this lane.** `S2/processor0/0/U.gz` was rewritten the same way, mid-run, mtime **1788213122**, `nonuniform List<vector> 2016`. The premise is false on **every** arm; the serial arm is merely the only one where the rewrite lands in the directory the guard watches. **A repair scoped to "the serial case" would leave the parallel arms guarded by luck rather than by a true premise.** *(The relayed triage also stated that MESH/X2/S2 have "NO time dirs". At case level that is true; at case level it is also not the whole case — `X2/processor0/0.0001` and `S2/processor0/163` both exist. Corrected here so no later reader builds on it.)*
5. **A SECOND DEFECT NOBODY HAS REPORTED: THE COUNT CHECK PASSED BY COINCIDENCE.** `S1/0` held **9** files before and **9** after — but **six of the nine filenames changed** (`T`→`T.gz`, `U`→`U.gz`, `p`→`p.gz`, `nut`→`nut.gz`, `nuTilda`→`nuTilda.gz`, `alphat`→`alphat.gz`). **A count is not an identity.** Had the mtime clause not fired, the count clause would have waved through a directory whose every graded file had been replaced.

**CAUSE CLASS: INSTRUMENT.** The guard refused rather than degrading, which is correct behaviour; it was enforcing a premise that does not hold for this solver family. **It does not mean a stale answer**: the datum moved **forward**, which makes the comparison stricter, not looser.

### 2.2 The repair — three legs, and the age assertion is NOT weakened

Instrument: `d19r_age_guard.py`, committed with this document.

- **L1 — the datum leaves the solver's write set STRUCTURALLY.** D19's launcher runs `docker run … -v "$BASE":/mnt`, so `$BASE` and everything under it is writable by the solve; `$BASE`'s **parent** is not mounted. D19R stamps a launch sentinel at `<parent of run root>/.d19r_datums/<run root basename>/<ARM>.sentinel`, **after** staging and **before** the container starts. *"The solver does not write here"* stops being a belief about DAFoam and becomes a property of the mount namespace — and it is **asserted, not hoped**: `assert_sentinel_outside_mounts()` refuses if the sentinel is at or under any declared mount source, and the launcher passes the `-v` sources it actually uses, read from its own command line.
- **L2 — rule 4's assertion is UNCHANGED.** Every graded artefact's mtime must be **strictly greater** than the sentinel epoch. Nothing is deleted, bypassed, softened to `>=`, or given a tolerance. **Only the datum's provenance changed.**
- **L3 — content identity replaces the count.** At stage time the launcher records an **md5 manifest** of the arm's INPUT set (`0.orig/`, `constant/`, `system/`, `FFD/`, the staged instruments). The grader asserts every entry byte-identical. **`0/` and `processor*/` are excluded BY NAME, with the reason recorded inside the manifest**, because they are solver write targets: *a guard must not assert a premise the solver falsifies.* This is strictly **stronger** than the count it replaces and strictly **narrower** in what it claims about `0/`.

### 2.3 THE RED LEGS — RUN AT FREEZE, AND EVERY ONE FIRED

*A guard that cannot fail is not a guard. This lab certified one such guard earlier today and had to retract it.* `python3 d19r_age_guard.py --selftest`, exit 0, at freeze:

| leg | plant | required | observed |
|---|---|---|---|
| `RED-1` | artefact mtime **10 s older** than the sentinel — a stale answer inherited from a previous run | REFUSE | `ARTEFACT_NOT_NEWER_THAN_DATUM` — **fired** |
| `RED-2` | artefact mtime **exactly equal** to the sentinel | REFUSE (strictly greater) | `ARTEFACT_NOT_NEWER_THAN_DATUM` — **fired** |
| `RED-3` | one manifest input's **content** changed, **file count unchanged 9 → 9** | REFUSE | `MANIFEST_ENTRY_MUTATED` — **fired** |
| `RED-4` | sentinel path placed **inside** the bind-mount source | REFUSE at launch | `AGE_DATUM_INSIDE_MOUNT` — **fired** |
| `RED-5` | manifest entry removed from disk | REFUSE | `MANIFEST_ENTRY_MISSING` — **fired** |
| `GREEN-1` | **D19's exact false refusal**: `0/T` replaced by `0/T.gz`, `0/U` rewritten *after* the sentinel, artefact newer | ACCEPT | accepted — **the regression does not recur** |
| `GREEN-2` | clean case | ACCEPT | accepted |

`RED-3` is the one worth naming: it is the defect §2.1(5) shows D19's count clause could not see, and it fires on a directory of unchanged cardinality.

---

## 3. ⚠ THE `0/U` FD-BASELINE HYPOTHESIS — MEASURED, AND CLOSED. THE FD NUMBERS ARE NOT SUSPECT

The brief required this lane to establish whether the FD arms re-read a **mutated** `0/` between evaluations — because an evaluation starting from a *converged* state rather than the original initial condition would change an FD answer, and that is the family that killed `SO-3aR`.

**Finding: the mutation is REAL, and its effect on the FD answer is bounded at ≤ 0.041 % by three independent histories. The hypothesis is CLOSED, not open.**

**(a) The mutation is real and universal.** §2.1(2)-(4): `0/U` (serial) and `processor*/0/U` (parallel) both end the run holding a converged nonuniform internalField, against a staged `uniform (100 0 0)`.

**(b) `0/` is not rewritten per evaluation.** `S1/0/{T,p,nut,nuTilda,alphat}.gz` all carry mtime **1788213194** — written once, ~5 s in, and never again across the remaining ten primals. Only `U` is rewritten late, and §2.1(3) identifies why: it is the `patchV` DV's boundary-condition update, not a per-evaluation restart.

**(c) THE DECISIVE TEST — vary the history and see whether the number moves.** Three arms measured the same derivatives at the same steps with **very different warm-start histories and different write locations**:

| arm | ranks | `0/U` written to | primals before the graded component |
|---|---|---|---|
| D19 `S1` | 1 | the **case** `0/` — the mutated one | 12-primal chain |
| D19 `S2` | 2 | `processor*/0/` | 52-primal chain |
| D15 `F-P` | 2 | `processor*/0/` | 32-primal chain, a separate run on 2026-08-27 |

- **D19 `S1` vs D19 `S2` at `s* = 1e-3`/`1e-2`, ten readings (5 components × `CD`,`CL`): worst 0.041027 %** (`shape[6]`/`CL`), best 0.000126 %.
- **D19 `S2` vs D15's frozen `F-P` at the three shared steps, 28 readings: worst 0.003385 %**, most exactly 0.000000 %.
- Baselines agree bit-for-bit: D19 `S2` `CD_baseline` = D15 `F-P` `CD_baseline` = `0.014600274376560973`.

> **If evaluations were starting from a progressively mutated initial condition, three histories of 12, 32 and 52 primals would not land on the same derivative to four and five significant figures.** They do. **The FD numbers are not suspect.**

**(d) What this lane could NOT verify, stated plainly.** This lane did **not** instrument DAFoam to observe whether `0/` is re-read from disk between `run_model()` calls. What is established is a **bound on the consequence**, not the mechanism: whatever the read behaviour is, it did not move a derivative by more than **0.041 %** across three histories. **`G19R-1d` (§5) carries that bound forward as a live gate at 2.0 %, so the check runs again on D19R's own data rather than resting on D19's.**

**(e) A premise of the supervisor's own correction, checked and partly declined.** The supervisor closed this hypothesis on `eta_raw` (9.652e-11 serial / 1.301e-10 parallel, `eta_floored=False`), and separately argued the fine-side failure is not round-off because the noise floor `eta/(2h)` is at worst **0.402 %** at `h=1e-4` against a 21.63 % disagreement. **Both figures reproduce exactly for this lane.** But `eta` is measured `baseline` versus `baseline_repeat` **before any perturbed primal**, and `D15_D16_FD_STEP_TABLE.md` §1.2 already records that this is *"the weakest bound available"* — it measures *rerun determinism on the same mesh*, **not** *"the convergence-tolerance scatter of a primal restarted on a perturbed mesh, which is the noise that actually matters and which these artefacts do not measure at all."* **So `eta` is the wrong instrument to close either question with**, and the supervisor's conclusions — with which this lane agrees — rest here on (c) and on §1.1's sign flip, not on `eta`. **The right floor has still never been measured, and arm `N2` (§4) measures it.**

---

## 4. THE ARMS, AND THE SWEEP, FROZEN

All arms run in the `PATCHED` image of §8. `MESH` is a script arm; all others are solver arms and are subject to `CLAUDE.md` rule 4 as repaired by §2.2.

| arm | np | what it does | predicted (core-min) | cap (core-min) |
|---|---|---|---|---|
| `MESH` | 1 | builds the 4,032-cell mesh; asserts cell count and md5-identity against D15's mesh | 0.5 | 5.0 |
| `X2` | 2 | patched adjoint, `CD` and `CL`, all DVs | 3.4 | 20.0 |
| `S8` | 2 | the **EIGHT-level half-decade sweep**, 5 components, `CD` and `CL` | 6.4 | 40.0 |
| `N2` | 2 | **perturbed-mesh repeatability** — the noise floor that has never been measured | 1.7 | 10.0 |
| `S1` | 1 | the selected step only, serial, for `G19R-1d` | 0.9 | 10.0 |
| `R1` | 1 | **sensitivity-equalised step diagnostic — NON-GRADED** (§4.3) | 0.7 | 8.0 |
| | | **phase 1 total** | **13.6** | **93.0** |

### 4.1 The sweep, frozen

**`shape`: {3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5}** — eight levels.
**`patchV`: {3e-1, 1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4}** — eight levels.

Central differences, `step_calc="abs"` (`VERIFICATION_CHARTER.md` §7 step 5 — **unchanged; this item does not depart from the charter-fixed protocol**). Primal tolerance `primalMinResTol = 1.0e-8`, D15's graded value, per `DAFOAM_CHARTER.md` §3.

**Components, frozen — identical to D15's and D19's** (`d15_grade.py:78`): `shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`.

**The four new levels are 3e-3, 3e-4, 3e-5 (and `patchV`'s 3e-2, 3e-3, 3e-4).** Five of the eight are D19's own levels and are the reproduction control.

**Admissible candidates under `G19R-1b-N`** (both decade neighbours present in the sweep): `shape` **{1e-3, 1e-4, 3e-3, 3e-4}**; `patchV` **{1e-2, 1e-3, 3e-2, 3e-3}**.

**Of those, `VERIFICATION_CHARTER.md` §7 step 5's sanctioned grading range for `shape` is `[1e-3, 1e-2]`, so the GRADED candidate set is `{1e-3, 3e-3}`** (`patchV` `{1e-2, 3e-2}`). `1e-4` and `3e-4` are **measured and reported as rows** — §7 requires a sweep to report its failed steps as rows — and are registered as **NOT graded**, because they sit below the sanctioned range.

> **THE SINGLE MOST VALUABLE NEW POINT IN THIS ITEM IS `3e-3`.** D15 graded at `1e-3`, which `D15_D16_FD_STEP_TABLE.md` §1.3(a) shows is an **edge** of §7's range with its only in-range neighbour on one side — *"two points at the ends of a range bound a flat; they do not bracket one."* D19's candidates were `{1e-2, 1e-3}` and `1e-2`'s coarse neighbour was `3e-2`, not a decade. **`3e-3` is the first candidate in this family's history that sits in the INTERIOR of §7's sanctioned range with a TRUE DECADE bracket on both sides.** That, and not a wider range, is what D19's data leaves unmeasured.

### 4.2 `N2` — the noise floor that actually matters

`D15_D16_FD_STEP_TABLE.md` §1.2 leaves an explicit open gap: `shape[7]`'s fine-step S/N of 248.8 bounds the induced error near **0.4 %** while the observed break is **21.6 %**, *"roughly 50x larger than that bound explains"*, and the record states the bound is the wrong one because *"these artefacts do not measure"* perturbed-mesh convergence scatter at all.

**`N2` measures it.** At the perturbed design points — not the baseline — it re-runs the primal **three times** for `shape[7]±s` and `shape[6]±s` (the contrast component, 70x larger and flat) at `s ∈ {1e-3, 1e-4}`, plus three baselines: **21 primals**. It reports the scatter of `CD` and `CL` across repeats at each perturbed point, as an absolute and as a fraction of the differenced signal.

**This is a MEASUREMENT arm, not a gate.** It grades nothing. Its registered purpose is to close §1.2's gap so the family stops quoting a bound its own record says does not apply.

### 4.3 `R1` — the sensitivity-equalised diagnostic, and exactly what it may not do

`shape[7]`'s `|dCD|` is ~2.07e-4 against siblings at 7.2e-3, 9.3e-3 and 1.42e-2 — **35x to 70x smaller. It is a near-null component.** [**INFERENCE, flagged as such and registered to be tested, not assumed**: a component whose true sensitivity is two orders below its siblings is exactly where a *shared absolute* step ladder fails to find a plateau, because a step sized for the large-sensitivity modes is far off-scale for this one.]

`R1` tests it. `shape[7]` only, at a **sensitivity-equalised** ladder `s = kappa * s_abs` with

> **`kappa = |FD(CD, shape[6]) at 1e-3| / |FD(CD, shape[7]) at 1e-3|`, computed from `S8`'s own FD values — NEVER from the adjoint —** and the ladder truncated to `s <= 3e-2`, the primal's measured safe ceiling (`A_stepsize_study.md`: the primal FAILS at 5e-2 and 1e-1).

**Registered constraints, because this arm is the one most likely to be misread later:**

1. **`R1` CANNOT PRODUCE A `PASS`, cannot change any gate, and cannot be cited as a plateau.** Its verdict field is fixed at `DIAGNOSTIC`.
2. **`kappa` is computed from FD and from nothing else.** No adjoint quantity enters any step choice in this item, so `DAFOAM_CHARTER.md` §3's prohibition on *"Selecting the step after seeing which one agrees"* is enforced by the data flow.
3. **`R1`'s output never reaches the selector.** The selector's adjoint-blindness assertion (§5.1) is joined by a second assertion that no `R1` artefact is present in its input.
4. **A departure from `step_calc="abs"` is a departure from a charter-fixed protocol, and this item does not make one.** `R1` is a diagnostic *alongside* the abs ladder, never instead of it. Whether a relative step may ever *grade* a DAFoam FD table is a standards question for the `verification-supervisor` and Sanaa, and **this document does not answer it and does not act as though it had.**

---

## 5. THE GATES

Verdicts come from the fixed vocabulary and from nothing else: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

**`G19R-1a` REPRODUCTION.** For each of the five levels shared with D19, each of the five components, both `CD` and `CL`: `S8` reproduces D19's `S2/d19_S.json` to **≤ 0.5 %**; and `X2`'s adjoint reproduces D19's `X2/d19_X.json` to **≤ 0.1 %**. → `PASS` / **`NOT A RESULT`**. A miss means this is not the same instrument and nothing downstream may be compared.

**`G19R-1b` PLATEAU — the gate the item turns on, AND ITS RULE IS D19's UNCHANGED.** Among the graded candidates `{1e-3, 3e-3}` (`shape`) / `{1e-2, 3e-2}` (`patchV`), the selector chooses `s*`. `PASS` **iff every one of the five components on BOTH `CD` and `CL` has both DECADE-separated neighbour deviations ≤ 10.0 %** — **`max`, not `min`.** Otherwise **`GATE FAIL`**, and phase 2 launches nothing.

> **THE `max` RULE IS NOT RELAXED, NOT EXEMPTED, AND `shape[7]` IS NOT EXCLUDED.** On D19's data one near-null component vetoes an item that four of five components support. **Whether that is the right gate is a GATE-DESIGN question and gate design is reserved to Sanaa** (`CLAUDE.md` rule 9). This lane does not decide it, the `dafoam-supervisor` does not decide it, and this document is built so that **whichever way she rules, the answer is already computed** — see `G19R-1e`.

**`G19R-1c` PLANTED CONTROL, SIZED RELATIVE (`CLAUDE.md` rule 3).**

> **`plant_i = K * (band/100) * |d_ref_i|`, with `K = 5.0` REGISTERED AT FREEZE**, `band` the gate's own band in percent and `d_ref_i` the reference the plant perturbs.

**Why relative and not absolute:** `SO-2M` was lost hours ago to a bare absolute plant of `1.234e-03` that turned out to be **2.48 %** of its own reference and **could not cross its own 5 % band**. A plant that cannot cross the band it is asked to cross proves nothing. `K = 5.0` moves the reading by `5 x band` percentage points — a 5x margin, so a reader that cannot see it is broken rather than merely insensitive.

**And the SUFFICIENCY LEG IS DRIVEN RED at freeze**, which is the half with teeth: the same control at **`K_shrunk = 0.5`** moves the reading by **half the band** and **must report NOT-CROSSED**. *A control that reports "crossed" at every plant size is not measuring crossing.* Measured at freeze, on D19's `shape[7]`/`CD` FD at 1e-3 (`d_ref = -2.065253e-04`, band 10.0 %): `K=5.0` → plant `1.032627e-04` → reading moves **50.0000 pp > 10.0 pp — CROSSES**; `K=0.5` → plant `1.032627e-05` → reading moves **5.0000 pp — DOES NOT CROSS. RED LEG DROVE RED.** Not a graded gate — a **refusal condition on every reader in the item**.

**`G19R-1d` DECOMPOSITION (`DAFOAM_CHARTER.md` §5).** At `s*`, `S1` (np=1) and `S8` (np=2) agree to **≤ 2.0 %** on every component and both functions. → `PASS` / **`GATE FAIL`**. This gate also carries §3(d)'s open mechanism: it is the live re-test of the `0/U` bound on D19R's own data.

**`G19R-1e` FLAGGED-COMPONENT DISPOSITION (`DAFOAM_CHARTER.md` §3) — EVIDENCE, NEVER A VERDICT.** §3 requires that *"a component whose FD estimate does not stabilise anywhere in the sweep is flagged and excluded by name from any aggregate quoted as agreement — never dropped silently, and never rescued by a step at which it happens to cross."* So, **if and only if `G19R-1b` `GATE FAIL`s**, the grader additionally computes and reports: which components stabilise at **no** admissible candidate; each one's **share of the `|J_adj|` norm** (D19 measured `shape[7]` at **1.135 %** of the `CD` gradient norm); and the plateau reading over the remaining components with the flagged ones **named**.

> **`G19R-1e` DOES NOT LET PHASE 2 LAUNCH.** The phase-2 branch is gated on `G19R-1b` `PASS` and on nothing else. Letting a subordinate reading launch the optimiser **is** relaxing the gate by another name. `G19R-1e` exists so that a decision to proceed on a flagged-component basis is available **to Sanaa, on measured evidence**. This item does not take that decision.

**`G19R-1f` TOOLCHAIN (§6).** Container image digest **and** `libidwarp.so` md5, both as printed by the run and as read from the artefact, matching §8. Any mismatch → **`GATE FAIL`** on that row.

**`G19R-1g` CAPS (rule 12).** Every arm within its §4 cap; phase 1 within **93.0** core-min; item within **233.0** core-min. **An overrun STOPS the run; it does not get a new budget.**

**`G19R-1h` COMPLETION (rule 4, as repaired by §2.2).** `rc = 0`; the arm's terminal marker; artefacts present; **every artefact strictly newer than the arm's launch sentinel**; the input manifest byte-identical. Any clause failing → the arm is **`NOT A RESULT`**.

**`G19R-1i` TRAVELLING PROVENANCE.** Inherited from D19 §9 unchanged: `d19r_precondition.py` pins D15's graded output by absolute path and md5, asserts `rows.SHIPPED == "GATE FAIL"`, `rows.PATCHED == "PASS"`, `verdict == "GATE FAIL"`, and **refuses to emit ANY D19R verdict** if it cannot read them. **Every D19R verdict string carries the frozen suffix**: *"on the PATCHED toolchain; the SHIPPED toolchain FAILS the gradient gate on this exact ground (D15 shipped worst 44.8738 % on `shape[6]`, aggregate 34.6807 %)"*.

### 5.1 The selector

Unchanged from D19 §5.1 in rule and in enforcement. Among admissible graded candidates, `s*` minimises `max` over components and both functions of the two **decade-separated** neighbour deviations; ties break to the **larger** step. **The selector reads only `rows[].fd`, is handed no adjoint, asserts at entry that no adjoint array and no `R1` artefact is present in its input, and refuses if either is.** The prohibition is enforced by code, not by the author's intention.

### 5.2 THE NAMED VERDICTS, INCLUDING THE ONE THAT IS A RESULT RATHER THAN A FAILURE

**`V-PLATEAU`** — `G19R-1a` `PASS`, `G19R-1b` `PASS`, `G19R-1d` `PASS`: a two-sided decade-bracketed plateau exists at `s*` for all five components on both functions. Phase 2 becomes eligible. Item phase-1 verdict **`PASS`**.

> **`V-NOPLATEAU` — A NAMED, LEGITIMATE, VALUABLE OUTCOME, REGISTERED HERE SO IT CANNOT LATER BE READ AS A FAILURE OF THE RUN.** If **no** admissible graded candidate has max-over-components-and-functions decade neighbour deviation ≤ 10.0 %, the registered finding is: **no step in the sanctioned range brackets a joint two-sided plateau for the five registered components on this ground.** The gate verdict is **`GATE FAIL`** on `G19R-1b`, phase 2 launches nothing, **and the item's reported RESULT is `V-NOPLATEAU`** — a measurement about the ground, reported with `G19R-1e`'s disposition and `N2`'s noise floor beside it. **`GATE FAIL` is the verdict; `V-NOPLATEAU` is what was learned. Both are reported and neither is used to soften the other.**

**What would falsify "a plateau exists at all", stated so it can be checked.** The proposition *"a joint two-sided plateau exists for these five components somewhere in `[1e-5, 3e-2]`"* is falsified iff `min` over the four admissible candidates of `max` over components and functions of the decade neighbour deviation **> 10.0 %**, **and** the failing component's deviation is non-monotone in neither direction — i.e. it degrades away from its best candidate on **both** sides. **The residual is registered rather than hidden: a plateau narrower than a half-decade in step would not be detected by this grid**, and `V-NOPLATEAU` therefore reads *"no plateau of half-decade width or greater"*, never *"no plateau"* full stop.

---

## 6. THE REGISTERED PREDICTIONS — falsifiable, frozen before any D19R compute

| # | prediction | what a MISS means |
|---|---|---|
| **P1** | **`G19R-1b` `GATE FAIL`, outcome `V-NOPLATEAU`, driven by `shape[7]` on `CD`, whose best decade-bracketed score over the graded candidates `{1e-3, 3e-3}` EXCEEDS 10.0 %.** Basis: D19's measured five-level curve, in which `shape[7]`/`CD` degrades away from 1e-3 toward **both** ends (41.81 % / 1.14 % / 21.63 % / 264.40 % adjacent) and **changes sign** between 1e-4 and 1e-5. | **A HIT IS A RESULT, NOT A DISAPPOINTMENT.** A MISS — a plateau found at `3e-3` — is the better outcome and means D19's decade grid was too coarse to see a half-decade flat; phase 2 becomes eligible and this lane was wrong in a useful direction. |
| **P2** | `G19R-1a` holds: `S8` reproduces D19's `S2` to ≤ 0.5 % on all five shared levels, adjoint to ≤ 0.1 %. | Phase 1 `NOT A RESULT`; the instrument is not D19's. |
| **P3** | `G19R-1d` holds: np=1 vs np=2 at `s*` ≤ 2.0 %. **Prior: D19 measured worst 0.041027 % on this exact pair.** | A4's decomposition defect reaches this ground, **or** §3(d)'s open mechanism has a consequence D19 did not see. Phase 2 does not launch. |
| **P4** | **`N2`: the perturbed-mesh repeatability scatter at `shape[7]±1e-4` EXCEEDS the same-mesh `eta` (1.301e-10) by at least 10x.** Basis: `D15_D16_FD_STEP_TABLE.md` §1.2's stated reason the 0.4 % bound fails to explain a 21.6 % break by ~50x. | The perturbed-mesh floor is **not** materially above the same-mesh floor, `eta` was the right bound after all, **and the 21.6 % break is then UNDIAGNOSED and is reported in those words** — not attributed to cancellation. |
| **P5** | **`R1`: a sensitivity-equalised step finds a two-sided plateau for `shape[7]` where the shared absolute ladder does not.** | The near-null-component inference of §4.3 is **refuted**, and `shape[7]`'s behaviour is not a step-scaling artefact. Reported as a refutation. **`R1` is `DIAGNOSTIC` either way and grades nothing.** |
| **P6** | Cost: phase 1 in **[8, 93]** core-min. | Reported as an overrun and attributed per §7; the run **stops**, it does not get a new budget. |

**Predicted outcome, stated so it can be wrong.** P1, P2, P3, P4, P5 HIT → phase-1 verdict **`GATE FAIL`** with result **`V-NOPLATEAU`**, `G19R-1e`'s disposition naming `shape[7]` (1.135 % of the `CD` gradient norm) as the sole flagged component, `N2` closing §1.2's open gap, and **the compressible optimisation does NOT launch.** **That is the correct outcome, not a problem to engineer around**, and it puts a measured gate-design question on Sanaa's desk instead of a number nobody can defend.

---

## 7. COST (rule 12; `DAFOAM_CHARTER.md` §12)

| | predicted (core-min) | cap (core-min) |
|---|---|---|
| phase 1 | **13.6** | **93.0** |
| phase 2 (unchanged from D19 §3, and NOT authorised by this document) | 36.8 | 140.0 |
| **item** | **50.4** | **233.0** |

**Basis — MEASURED, from D19's own phase-1 ledger** (`/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt/ledger.txt`), which is the strongest anchor this family has ever had for this item (ratio 0.998):

| anchor | measured |
|---|---|
| `MESH`, np=1 | **0.467** core-min |
| `X2`, np=2 | **3.333** core-min |
| `S2`, np=2, 52 primals | **4.033** core-min → **0.0776 core-min per primal at np=2** |
| `S1`, np=1, 12 primals | **0.850** core-min → **0.0708 core-min per primal at np=1** |

From it: `S8` = 8 levels x 5 components x 2 signs + 2 baselines = **82 primals** x 0.0776 = **6.36** → registered **6.4**. `N2` = 21 primals x 0.0776 = **1.63** → **1.7**. `S1` = 12 primals x 0.0708 = **0.85** → **0.9**. `R1` = 9 primals x 0.0708 = **0.64** → **0.7**. `MESH` **0.5**, `X2` **3.4**, each rounded up from its measured anchor.

**Dollars are DERIVED, NOT MEASURED, and the rate is REPORTED-BY-OWNER.**

> **`cost_basis`, frozen wording:** *"Core-minutes are MEASURED, from the D19R launcher's own per-arm ledger rows (wall_s x ranks / 60). Dollars are DERIVED from those core-minutes at the c7a.4xlarge rate of $0.0513 per core-hour. **That rate is REPORTED BY THE OWNER (Sanaa, 2026-08-21/22) and is NOT MEASURED BY THIS BOX** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure in this item is a measurement and none is presented as one."*

At that rate: phase 1 predicted **$0.0116 derived**, cap **$0.0795 derived**. Both far under the $25 pre-authorisation, **and the item is costed regardless, because a blanket authorisation is not a per-item read** (rule 9).

**Stop rule.** An arm exceeding its cap **stops**. Phase 1 exceeding 93.0 core-min **stops** and closes on what it has, labelled by what was actually reached. **Waste is named separately and never absorbed into the ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

**At completion the estimate-versus-actual comparison is computed and appended to `docs/COST_CALIBRATION.md`** under that file's append rules — ratio actual/predicted, gap attributed to contention, waste or misprediction. **A completion report without it is incomplete** (rule 12; Sanaa 2026-08-23). **D19 phase 1's own owed row — predicted 8.7, actual 8.683, ratio 0.998 — is landed with this freeze and not deferred.**

---

## 8. TOOLCHAIN IDENTITY (§6) — an image ID and a library hash, never a version string

| row | container image digest | `libidwarp.so` md5 |
|---|---|---|
| `PATCHED` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |
| `SHIPPED` *(not run in phase 1 — see §9)* | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |

Both corroborated by D19's own phase-1 ledger, which printed `D19_G9_OK … libidwarp_so_md5=85f59e87253e0a71a813f64ca6e4c425 digest=sha256:2927768a…` on all four arms.

---

## 9. ⚠ PHASE 1 IS `PATCHED`-ROW ONLY, AND THIS IS SAID EXPLICITLY BECAUSE A DAFOAM VERDICT IS NORMALLY TWO ROWS

`DAFOAM_CHARTER.md` §6 and §1: *"a DAFoam verdict is two rows — shipped and patched — or it is not a verdict about DAFoam."* **D19R phase 1 registers ONE row, `PATCHED`, exactly as D19 phase 1 did. The reason is stated rather than left to be noticed:**

1. **Phase 1 measures a property of the FD table, not of an adjoint.** `G19R-1b` reads `rows[].fd` and no adjoint at all; the plateau of a finite-difference curve is a property of the **primal** and the **step**, and both images run the same primal. A `SHIPPED` sweep would reproduce the `PATCHED` sweep by construction and would buy nothing but core-minutes.
2. **`X2` is the one place a row distinction could bite, and D15 has already measured it** on this exact ground: shipped worst **44.8738 %** on `shape[6]`, aggregate **34.6807 %**, against patched **0.0072 %** / **0.047405 %**. Re-measuring it is not a new result.
3. **Nothing in this item is proposed to stand on the shipped gradient**, and `G19R-1i` makes the shipped `GATE FAIL` travel attached to every D19R claim, in code.
4. **PATCHED-only is authorised** under Sanaa's `bda2d8cc`. **Phase 2, if it is ever reached, is TWO ROWS and is not touched by this paragraph.**

**This is a registered narrowing, disclosed before compute, not an omission discovered afterwards.**

---

## 10. WHAT THIS ITEM DECLARES IT DOES NOT DO

**No Roache triple; rule 5 is UNREACHABLE rather than waived.** Single mesh, 4,032 cells, no grid family, **no GCI is quoted anywhere in this item**, no claim about the continuum. Registered pre-compute per `VERIFICATION_CHARTER.md` §2f.

**No forward-AD or complex-step reference, and `DAFOAM_CHARTER.md` §2 requires saying why.** Both images ship `libDASolverADF.so` (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a), so a non-FD reference **is** reachable on this box and this item does **not** reach for it. **It would settle `shape[7]` outright, because it has no step at all** — `D15_D16_FD_STEP_TABLE.md` §5 says so and D19 §11 repeated it. The reason is scope and tonight's clock, not availability. **It is named here so the omission is on the face of the document, and it is the strongest single follow-on this ground admits** — recommended to the `dafoam-supervisor` as the successor item whatever D19R returns.

**No dot-product / duality check.** D15, D16 and D19 all recorded `G6` as not measured; nothing here changes that.

**No edit to D15, D16 or D19.** All frozen. A dated addendum at the foot of any of their `RESULTS.md` is the `dafoam-supervisor`'s call, not this lane's.

**No edit to `docs/capability/dafoam_GRID.md`.** The staleness finding stands where `D15_D16_FD_STEP_TABLE.md` §4 reported it; correcting the grid is the supervisor's call.

**No change to `G19-1b`'s `max` rule, no exemption for `shape[7]`, no gate-threshold relaxation of any kind.** Reserved to Sanaa (rule 9).

**Phase 2 is NOT authorised by this document.** The chain driver writes `PHASE1_COMPLETE_PHASE2_NOT_LAUNCHED_NOT_AUTHORISED` and exits 0, as D19's did.

---

## 11. INSTRUMENT TABLE (`DAFOAM_CHARTER.md` §18.3) — every file this item EXECUTES or IMPORTS

Existence is asserted by `test -e` **before** any md5 is taken, inside the asserting invocation, under a planted control confirming the reader can return non-ABSENT.

| file | role | status at freeze |
|---|---|---|
| `curriculum_D19R/d19r_age_guard.py` | the §2.2 repaired age datum, its manifest, and the §5 `G19R-1c` relative plant | **PRESENT**, committed with this document, `--selftest` exit 0, all seven legs fired |
| `curriculum_D19R/d19r_xf.py` | the sweep / adjoint / serial instrument (`-mode X\|S8\|N2\|S1\|R1`) | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D19R/d19r_runScript.py` | the producer | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D19R/d19r_select_step.py` | the §5.1 selector, adjoint-blind and `R1`-blind by assertion | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D19R/d19r_precondition.py` | the `G19R-1i` travelling-provenance guard | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D19R/d19r_run_arm.sh` | the launcher, stamping the §2.2 sentinel and manifest | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D19R/d19r_chain_driver.sh` | arm sequencing; phase 2 not wired | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D19R/d19r_grade.py` | the grading path, frozen at its own commit before compute | **ABSENT — to be written and committed BEFORE any launch** |
| `curriculum_D15/d15_runScript.py` | the configuration this item inherits | **PRESENT** |
| `curriculum_D15/d15_decomposeParDict` | the np=2 decomposition | **PRESENT** |
| `curriculum_D19/d19_xf.py`, `d19_run_arm.sh`, `d19_grade.py` | the D19 instruments this item derives from and cites by line | **PRESENT, FROZEN, NOT EDITED** |

**The ABSENT files are gates on the launch, not omissions from the freeze.** This document freezes the **gates, thresholds, bands, caps, labels, predictions, costs and the sweep** — rule 2's entire subject. The grading path must itself be frozen at its own commit before compute and hashed against the committed blob at grading time (rule 2, third clause).

---

## 12. STATUS

**`PENDING`.** Frozen, **not enqueued**, no run root, **zero D19R solver core-minutes spent**. **Launching is the `dafoam-supervisor`'s call**, requires the §11 ABSENT files committed first, and requires the supervisor's personal check 4 — *pre-registration committed before compute* — to be satisfied against **this** committed blob. **This lane does not launch on its own initiative and does not treat any brief as that go-ahead.**

---

## AMENDMENT 1 — 2026-08-31 — THE §11 INSTRUMENTS ARE BUILT, DRIVEN AND FROZEN; AND TWO DEFECTS IN THIS ITEM'S OWN AGE GUARD ARE DISCLOSED AND REPAIRED

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.** This section is appended at the foot; §0–§12 are byte-unchanged. `CLAUDE.md` rule 6.

**PRE-COMPUTE, AND THE CONDITION IS STATED AND WAS CHECKED, as `CLAUDE.md` rule 2 requires.** The registered run root **`/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau` DOES NOT EXIST**, checked this invocation by `ls -d` (`No such file or directory`), and **no container carries this item's `d19r_` prefix**, checked by `docker ps` (count 0). **Zero D19R solver core-minutes have been spent.** Gates, thresholds, bands, caps, labels and predictions are therefore still open to amendment and **none of them is amended here** — this amendment adds no gate, moves no threshold and changes no prediction.

### A1.1 The §11 ABSENT files are now PRESENT, frozen, and each was DRIVEN

| file | md5 at freeze | driven |
|---|---|---|
| `d19r_age_guard.py` | `e7f1ccb1794a163548f7dfefe8912a30` | `--selftest` rc 0 — ten legs, §A1.2 |
| `d19r_runScript.py` | `a5e18503ea29d0e37c3cf1668533cd34` | header md5 `d1efc43583fbeb59fb5116816b055a07` — **byte-identical to D15's and D19's**, which is what `G19R-1a` rests on |
| `d19r_xf.py` | `a0f44316bd961204e41e438464f834d4` | compiles; modes `X`/`S8`/`N2`/`S1`/`R1` |
| `d19r_select_step.py` | `e5e1566b3b11685a13e75820703a0bbb` | `--selftest` rc 0 — six CONTROL-N cases incl. two new R1-blindness cases; CONTROL P both legs; CONTROL D flips the decision |
| `d19r_precondition.py` | `c66fff1e4d07573d774523b5e39ad813` | `--selftest` rc 0 — 1 accepted, 6 refused; reads D15's real graded JSON, md5 `73e02ebf49b6459e40abc2d6525d7bea` |
| `d19r_grade.py` | `707ccb0c8ace88d7f171a2e7299fde13` | `--selftest` rc 0 — 12 checks |
| `d19r_run_arm.sh` | `cb420118f799762158efa3e886f9f576` | `bash -n` OK; refusal paths rc 64 |
| `d19r_chain_driver.sh` | `1daf1acd6f8230fc0f715f693d5f298e` | `bash -n` OK; refusal paths rc 64, incl. the retired arm name `S2` |

**Every frozen md5 constant inside the scripts was verified to resolve to the real file** — a stale hash aborts every launch, so the check is run, not assumed.

**`G19R-1b-N` VALIDATED AGAINST D19's REAL DATA, and this is the load-bearing check.** Applied to D19's measured `S2/d19_S.json` at the level D19 graded, the decade rule returns **21.6299 %**, binding on `shape[7]`/`CD` — **reproducing D19's own registered `selector.out` figure `score_pct=21.629866`**. Every other component is comfortably two-sided (worst other **3.3318 %**). **The half-decade refinement therefore provably does not relax the gate**, which is the claim §1.3 makes and which is now measured rather than argued.

### A1.2 ⚠ TWO DEFECTS IN `d19r_age_guard.py` — DISCLOSED, REPAIRED, AND DRIVEN RED

Found at the `dafoam-supervisor`'s check 1 by their own adversarial probe, and **reproduced independently by this lane before either was touched.** Both are disclosed here rather than quietly fixed, because the guard's own evidence artefact is the thing this item asks a reader to trust.

**(a) THE WRITE-TARGET EXCLUSION WAS DESCRIPTIVE, NOT ENFORCING.** `build_manifest` built its `excluded_write_targets` record by listing the arm, while its entries came from the caller's `input_subdirs`, and nothing made the two agree. Reproduced: `build_manifest(arm, ["0", "system"])` emitted a manifest whose `excluded_write_targets` said `["0"]` while its own entries pinned `0/T` and `0/U`. **A record asserting something the code did not guarantee** — the defect class this guard exists to prevent. It was **fail-closed** (it would refuse every run, never pass a bad one), so it was never a correctness hole; it was a false assertion. **Repaired by an assert that REFUSES a caller passing a write target, rather than silently filtering it, so a caller's mistake is surfaced rather than absorbed.**

**(b) THE DATUM WAS TRUNCATED AND ERRED PERMISSIVE — AND IT WAS WORSE THAN REPORTED.** `datum = int(os.stat(sentinel).st_mtime)` truncated down while artefact mtimes stayed float. The supervisor raised it as a departure from the docstring's "strictly greater". **This lane's own probe showed it admitted a genuinely stale artefact**: sentinel at 1000.9, artefact at 1000.5 — the artefact **older than the launch** — was **ACCEPTED**. A sub-second window is still a window. **Fixed to full precision rather than documented.**

**Why the original selftest could not see (a):** it only ever passed a correct `input_subdirs`. **A fixture authored from the consumer's own expectations is a tautology on shape**, and this lab lost an item to exactly that this morning. The lesson is recorded here, not only in the code.

**The guard now has TEN legs and every one fires** (`--selftest` rc 0 under both `python3` and `python3 -O`): `RED-1` stale artefact → refused; `RED-2` mtime equal → refused; `RED-3` input content mutated at unchanged count 9→9 → refused; `RED-4` sentinel inside the mount → refused at launch; `RED-5` manifest entry missing → refused; **`RED-6` artefact 0.4 s older than launch — defect (b)'s regression → refused**; **`RED-7`/`RED-7b` caller pins `0/` or `processor0` — defect (a)'s regression → refused**; `GREEN-1` D19's exact false refusal → accepted; `GREEN-2` clean → accepted.

**AND THE GUARD WAS DRIVEN AGAINST D19's REAL MUTATED ARM DIRECTORY, not only the fixture.** A copy of D19's actual `S1/` — the one whose `0/T` no longer exists, whose `0/` holds `T.gz U.gz alphat.gz epsilon k nuTilda.gz nut.gz omega p.gz`, and whose `0/U.gz` the solver rewrote — was staged, sentinel-stamped and manifested (25 input entries, `0` excluded by name). With `0/U.gz` rewritten **after** the sentinel and the artefact newer still: **ACCEPTED — D19's false refusal does not recur on the real directory.** With the artefact then set older than the sentinel: **REFUSED, `ARTEFACT_NOT_NEWER_THAN_DATUM`.** Green and red, both on real data.

### A1.3 What is still owed before launch, and what this amendment does NOT do

**It does not authorise a launch.** Launching remains the `dafoam-supervisor`'s call and requires their personal check 4 — *pre-registration committed before compute* — against the committed blob carrying **this** amendment. **This lane does not launch on its own initiative.**

**It does not change a gate, a threshold, a band, a cap, a label or a prediction.** `G19R-1b` keeps `max`, keeps 10.0 %, and keeps all five components; `shape[7]` is not excluded; `P1` still predicts `GATE FAIL` / `V-NOPLATEAU`.

**Named honestly as untested-until-launch:** no arm has run, so the container path, the MPI launch, the `N2` repeatability arm and the `R1` `kappa` computation have been driven only through their host-side validation and refusal paths. **`R1`'s ladder is a prediction, not a measurement**: at D19's measured values `kappa` would be ≈ **68.43**, which truncates the ladder's coarsest rung against the registered `3e-2` ceiling and leaves **three** rungs. The real `kappa` comes from D19R's own `S8` and may differ.
