# CURRICULUM D19R2 — THE D19R RE-GRADE. NO NEW COMPUTE. PRE-REGISTRATION (FROZEN)

**Item id:** `CURRICULUM-D19R2`
**What it grades:** `CURRICULUM-D19R` phase 1, **exactly as it stands on disk**, at
`/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau/`
**Case directory:** `cases/dafoam/ladder-a/A1/curriculum_D19R2/`
**Solver compute: ZERO.** No arm is re-run. No run root is created. No container starts.

**Status: `PENDING`.** The grading run has not happened. Nothing here is a result.

---

## 0. THE SUCCESSOR ID, DERIVED FROM PRECEDENT ON DISK

`D19` → `D19R` → **`D19R2`**, the same shape as `SO-3a` → `SO-3aR` → `SO-3aR2`. Read from disk rather than chosen: `cases/dafoam/ladder-a/A1/curriculum_D19` and `curriculum_D19R` exist; **`curriculum_D19R2` did not exist before this item, and no `*D19R2*` run root exists under `/home/ubuntu/certonomous-runs/`** — checked with a reader shown able to return EXISTS for the two that do.

**D19 and D19R are NOT edited, NOT re-graded and NOT contradicted by this item.** D19R's arms are read forward unchanged; its grader is **imported**, never modified.

---

## 1. WHY THIS ITEM EXISTS

`D19R` phase 1 **ran clean**: `MESH`, `X2`, `S8`, `N2`, `S1`, `R1` all `rc=0`, chain rc 0, every arm inside its cap, the selector wrote its step, **12.416 core-min against 13.6 predicted**, and phase 2 correctly held itself back as unauthorised. **Its grader then refused, `rc=2`, and emitted no verdict.** The compressible single-point gradient gate therefore has no verdict, and the compressible multipoint optimisation Sanaa ordered cannot launch behind it.

**The arms are bought and on disk. This item grades them.**

### 1.1 Why a SUCCESSOR and not a repair of D19R's grader

`D19R` **has had first compute**, so its gates are closed. A repair of its frozen grader is a `VERIFICATION_CHARTER.md` §2d.1 question — the four-condition repair exception — which this family has **refused four times**. A successor sidesteps §2d.1 entirely and is this family's established pattern: `SO-1cR`, `D19R` itself, `SO-3aR2`, `D4S-F3SR`, `A2-B2R`.

---

## 2. THE DEFECT — `D19R-GRADER-DEF-1`. THERE ARE **TWO** BLOCKERS, AND THE SECOND IS NOT IN THE PUBLISHED DIAGNOSIS

Both were **measured on the frozen bytes** at this freeze, not read off a report.

### 2.1 Blocker 1 — the enforcer was called where the reader belonged

`d19r_grade.py:482`, the **first** statement of `grade()`:

```
prov = PROV.require_travelling_provenance({}, refuse=refuse)
```

`d19r_precondition.py:97-119` reads `out.get("verdict")` off that literal `{}`, gets `None`, finds `None` not in `VOCAB`, and **refuses — before a single gate is read**, thirty lines before composition. **As coded, D19R cannot emit a phase-1 verdict on any input.**

**THE GUARD IS NOT THE DEFECT, AND THIS MATTERS FOR THE REPAIR.** Its own docstring states its contract: *"Called on the output object immediately before it is written … Returns `out` unchanged on success so it can wrap an emit expression directly and cannot be forgotten by a caller who merely calls it and drops the result."*

**Driven at this freeze — the guard RETURNS when called correctly:**

| driven | result |
|---|---|
| `require_travelling_provenance({})` — D19R's own call form | **REFUSED**, `G-PROV`, `verdict_outside_the_fixed_vocabulary: None` |
| `require_travelling_provenance(out)` on a real emit object | **RETURNED the object unchanged** (`r is out` → `True`), verdict `GATE FAIL`, suffix carried |
| same, verdict outside `VOCAB` | **REFUSED** |
| same, `provenance` not carried | **REFUSED** |
| same, suffix stripped from `verdict_statement` | **REFUSED** |

**The call site conflated two different functions.** `read_upstream()` **reads** the provenance — it returns `{md5, path, rows, verdict, suffix, …}`, which is exactly what gate `G19R-1i` publishes. `require_travelling_provenance(out)` **enforces** that the provenance travels attached to the verdict, and is designed to wrap the emit. D19R called the **enforcer** where the **reader** belonged, on an empty dict, at the top instead of the bottom. That `prov` is then published as `gates["G19R-1i"]` at `d19r_grade.py:508` is the tell: a gate *reading* was expected there, and the enforcer never returns one.

### 2.2 Blocker 2 — MEASURED HERE, AND RELOCATING THE CALL ALONE WOULD NOT HAVE WORKED

Counted as dict keys in `d19r_grade.py`:

| key | occurrences | required by the guard? |
|---|---|---|
| `"provenance"` | **0** | **yes** — compared against the upstream it reads |
| `"verdict_statement"` | **0** | **yes** — must contain `SUFFIX` |
| `"verdict_suffix"` | 1 | no — **a different key name**, carrying the suffix text where the guard does not look |

**D19R's emit object carries neither key the guard requires.** A repair that only moved the call to wrap the emit would have refused a **second** time on `provenance_not_carried`, and a **third** on `suffix_absent_from_verdict_statement`. **This item repairs both blockers, and its selftest drives blocker 2 explicitly against D19R's own frozen source.**

---

## 3. WHAT THIS ITEM MAY AND MAY NOT DO — THE BINDING CONSTRAINT

> **NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES. This item grades D19R's registered gates AS REGISTERED.**

**And that is proved rather than promised, because this module contains none of them to move.**

`d19r2_grade.py` **re-implements no gate**. Every gate function — `g_completion`, `g_planted`, `g_reproduction`, `g_plateau`, `g_decomposition`, `g_disposition`, `g_toolchain`, `g_caps` — and every registered constant is reached through the **imported frozen module**, never copied:

`REPRO_FD_PCT` 0.5 · `REPRO_ADJ_PCT` 0.1 · `PLATEAU_TOL_PCT` **10.0** · `DECOMP_TOL_PCT` 2.0 · `PLANT_K` 5.0 · `PLANT_K_SHRUNK` 0.5 · `CAPS` {MESH 5.0, X2 20.0, S8 40.0, N2 10.0, S1 10.0, R1 8.0} · `ITEM_CEILING_CORE_MIN` 233.0 · `COMPONENTS` the five · `VOCAB` the six tokens · `RESULT_LABELS` {V-PLATEAU, V-NOPLATEAU}.

**Two driven checks stand behind that**, because an unenforced claim about one's own source is worth nothing:

* **`pin_check()`** — existence asserted **before** any md5 (`DAFOAM_CHARTER.md` §18.3), then md5. Refuses on drift. Driven RED against a swapped pin.
* **`shadow_sweep()`** — parses **this module's own AST** and refuses if it assigns any of the **27** registered constant names. **Driven RED against a planted `PLATEAU_TOL_PCT = 999.0`.** A sweep that has never reported a finding is not known to be able to.

**The `max` rule is not relaxed, `shape[7]` is not excluded, and no component is dropped.** D19R's §5 records that gate design is **reserved to Sanaa**; this item does not touch it.

### 3.1 The one piece of logic this item carries, and how it is checked

`F.grade()` cannot be called — its first statement refuses — so the **composition** is transcribed. It is the only new logic here, and **every registered branch is driven** in the selftest, in the registered order:

| branch | verdict |
|---|---|
| `G19R-1a` repro ≠ PASS | **NOT A RESULT** |
| `G19R-1h` completion or `G19R-1f` toolchain ≠ PASS | **NOT A RESULT** |
| `G19R-1b` plateau ≠ PASS | **GATE FAIL** |
| `G19R-1d` decomposition ≠ PASS | **GATE FAIL** |
| `G19R-1g` caps ≠ PASS | **GATE FAIL** |
| all PASS | **PASS** |

plus a precedence leg (repro failure beats plateau failure). **A `GATE FAIL` is never softened**, and a verdict outside `VOCAB` refuses.

---

## 4. THE GRADING PATH AND THE FROZEN DEPENDENCIES

| file | md5 | role |
|---|---|---|
| **`d19r2_grade.py`** | **`817698f6c5e5059fcc9f757d99caff90`** | **THE GRADING PATH** — see §4.1 |
| `curriculum_D19R/d19r_grade.py` | `707ccb0c8ace88d7f171a2e7299fde13` | **IMPORTED, NEVER EDITED.** Every gate and every constant |
| `curriculum_D19R/d19r_precondition.py` | `c66fff1e4d07573d774523b5e39ad813` | **IMPORTED, NEVER EDITED.** The provenance guard |

Both dependency md5s were recomputed **on disk** and from their **committed blobs at `HEAD`** at this freeze; both agree. `pin_check()` asserts them at grade time and refuses on drift.

**Upstream, read and verified at this freeze:** `read_upstream()` resolves D15's graded output at `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/D15_grade_20260827T114315Z.json`, md5 `73e02ebf49b6459e40abc2d6525d7bea`, `verdict: GATE FAIL`, `rows: {SHIPPED: GATE FAIL, PATCHED: PASS}`. **The travelling suffix is carried on every verdict string this item emits**, and its absence is a refusal.

### 4.1 The grading path is verified THREE WAYS

`d19r2_grade.py` is verified by recomputing its md5 **on disk**, from the **committed blob at `HEAD`**, and from the **committed blob at this document's own freeze commit** — the same discipline SO-3's §10 uses, and for the same reason: a pin that was not verified is a pin that is being guessed at, and this family lost SO-2MR's first arm to md5 pins that were stale the instant a rename ran. **The three readings are taken in the freeze commit's own shell invocation and are recorded in that commit's message.**

**The freeze sha is deliberately not written into the grader.** No sha exists at the moment that file is written — this document is inside the same commit — so a sha written there could only be wrong or back-dated. The binding runs the other way and is checkable: this section pins the file by md5, and `pin_check()` asserts its two imported dependencies at grade time.

---

## 5. WHAT THIS ITEM REGISTERS AS COST

**Zero solver core-minutes. No arm is re-run.** If any arm were found to need re-running, **this item STOPS and the question returns to the supervisor** — that would change the cost picture and the ruling, and it is not a decision this item takes.

The only spend is the grading invocation itself: a **single-threaded Python process** reading JSON already on disk. **Registered ceiling for the grading invocation: 2.0 core-min**, expected well under 0.5. **An overrun stops it; it does not get a new budget.** Dollars **DERIVED, not measured** at `$0.0513/core-h` reported-by-owner — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Ceiling `$0.00171` derived.

**D19R's own 12.416 core-min is already recorded against D19R and is NOT re-charged to this item.** D19's spend likewise stays D19's.

---

## 6. ⚠ THIS ITEM REGISTERS **NO PREDICTION ABOUT THE OUTCOME**, AND THAT IS DELIBERATE

**The arms already exist on disk.** A "prediction" registered now would be unfalsifiable theatre: rule 2's freeze has evidentiary content **because it precedes the data**, and here it cannot. Registering P1–P6 afresh would be prediction-after-the-fact wearing a pre-registration's clothes, which is worse than registering none.

**D19R's own P1–P6 stand as they were frozen, before D19R's compute**, and are the predictions this re-grade scores against. D19R registered **P1: `G19R-1b` `GATE FAIL`, outcome `V-NOPLATEAU`, driven by `shape[7]` on `CD`** — so a `GATE FAIL` here is a **registered, predicted, legitimate outcome and not a failure of the run.**

### 6.1 DISCLOSURE: what this lane has already seen of the data

Honesty requires naming it rather than letting a reader assume the freeze was blind.

Before this document was written, this lane ran a **read-only input census** — existence and JSON-parse only, `grade()` never called, no verdict produced — and in doing so read three precondition fields and the selector's own summary:

* `selector_saw_adjoint = False`, `N2.grades_nothing = True`, `R1.grades_nothing = True` — the three preconditions `grade()` checks before any gate.
* `s* = {shape: 0.001, patchV: 0.01}` and **`all_two_sided: False`**.

**`all_two_sided: False` is a strong indication that `G19R-1b` will `GATE FAIL` and the result label will be `V-NOPLATEAU`.** This lane has therefore **seen a signal about the answer before the freeze**, which is exactly why §6 registers no prediction. **What is frozen here is the INSTRUMENT and the METHOD, not a guess about a number this lane has already glimpsed.**

---

## 7. WHAT THE RE-GRADE CAN AND CANNOT ESTABLISH

**It CAN establish:** a phase-1 verdict for D19R's arms under D19R's registered gates, with the travelling provenance attached; whether `G19R-1b`'s joint two-sided decade-bracketed plateau exists at `s*`; `G19R-1e`'s flagged-component disposition if it does not; the `G19R-1a` reproduction against D19; `G19R-1d`'s np=1 vs np=2 agreement; and whether the compressible gate is open or shut.

**It CANNOT establish, and must never be read as establishing:**

* **Anything about the SHIPPED toolchain.** Phase 1 is `PATCHED`-row only, by D19R's §9. Every verdict string carries the frozen suffix naming D15's shipped failure, and emitting one without it is a refusal.
* **That a plateau does not exist.** `V-NOPLATEAU` reads *"no plateau of half-decade width or greater on this grid"* — **never** *"no plateau"*. A plateau narrower than a half-decade would not be detected.
* **A verdict about the arms' physics that D19R's arms did not already contain.** A re-grade reads bytes; it measures nothing new.
* **Authorisation for phase 2.** Eligibility is gated on `G19R-1b` `PASS` and on nothing else. `G19R-1e` cannot launch it, and neither can this document.
* **Anything that would be true only if a threshold had moved.** None did (§3).

**A `GATE FAIL` or `NOT A RESULT` here is a fine outcome and was the predecessor's own registered prediction.** This instrument is explicitly built so that it can produce one: six of its seven composition branches are non-`PASS`, and all seven are driven.

---

## 8. NAMED RESIDUALS

* **R1 — THE GRADER HAS NEVER BEEN RUN AGAINST THE REAL ROOT, BY DESIGN.** The supervisor's check 4 and check 1 come before it grades anything, so running it would pre-empt their gate. What was done instead is a **read-only input census**: all nine inputs — D19R's ledger, `S8`, `X2`, `S1`, `N2`, `R1`, the selector, and D19's `S2`/`X2` references — **exist and parse**, and the three preconditions hold. **That is not a grade and does not predict one.** If the grader refuses on the real root for any reason, that is a finding at that moment, not something this freeze has excluded.
* **R2 — THE COMPOSITION IS A TRANSCRIPTION.** It is the only logic not imported. Every branch is driven, but a transcription is still a place a byte could differ from D19R's frozen source, and this document says so rather than claiming the composition is imported when it is not.
* **R3 — THIS LANE HAS SEEN `all_two_sided: False`.** Disclosed in §6.1. It is why no prediction is registered.
* **R4 — `G19R-1a` DEPENDS ON D19's ARTEFACTS, WHOSE OWN GRADER REFUSED.** D19's `S2/d19_S.json` and `X2/d19_X.json` are read forward as physics under Sanaa's 2026-08-26 rule that bookkeeping never voids physics. Both exist and parse (9,820 and 1,188 bytes). **D19's grader refusal was an infrastructure clause, not a statement about these bytes** — but this item inherits that reading rather than re-establishing it.

---

## 9. FREEZE

Frozen at this document's own commit. The grading path is fixed here by md5 (§4). **Before the grading run**, amendments are legal and must state the condition and how it was checked. **After it**, changes land only as dated addenda that cannot alter a gate, a threshold, a cap or a label.

**This document authorises nothing.** It is a freeze, not a clearance. The supervisor's check 4 and their check 1 on the verdict-critical path come before this instrument grades anything.

**SUBMISSIONS ARE PARKED** — nothing here is filed, sent, posted or registered outside this box.
