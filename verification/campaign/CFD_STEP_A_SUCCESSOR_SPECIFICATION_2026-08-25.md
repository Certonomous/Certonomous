# cfd — **SPECIFICATION OWED: how a successor registration must reach standing rule 5 clause (a)**

**Drafted 2026-08-25 by a cfd lab-lane under cfd-supervisor, on his ruling
`verification/campaign/CFD_CONVERGENCE_CLASSIFICATION_RULING_2026-08-25.md` §4
("binding forward"). `[lab-attributed]`; overrulable.**

> ## THIS IS A SPECIFICATION. IT IS **OWED**, AND IT IS **NOT APPLIED**.
>
> **No grader is edited by this document. `grade_f3.py` and `grade_f4.py` are
> NOT touched and MUST NOT BE.** Both belong to registrations that have
> **FIRED**; rule 2 closed their gates at first compute, and **replacing an
> instrument after seeing what it graded is exactly the fit rule 2 exists to
> prevent.** The two `ABSENT` notes filed today record what those two
> conversions could not evaluate; **this document says what the NEXT
> registration must do, before its solver starts.**
>
> **It moves no verdict and grades nothing.**

**ZERO COMPUTE — no solver started, no case directory created, nothing written
under any `runs/` tree.** The measurements in §2 are sub-second read-only
interpreter calls against `scripts/roache_triple.py` with synthetic inputs in a
temp directory; **no lab artifact was read, written or touched by them.**

---

## 1. THE DEFECT THIS REPAIRS

`grade_f4.py` calls `RT.triple_from_cells` (`:629`) and **never
`RT.grade_ladder`** (zero occurrences). `grade_f3.py` reimplements the triple
in-file as `roache()` (`:357`, classes `:371–:388`) and imports the shared
instrument **not at all**. Neither supplies iterative-convergence or plateau
states, and neither pre-registration registers a clause that would have required
them.

> **`grade_ladder` (`scripts/roache_triple.py:536`) is the ONLY implementation of
> rule 5 clause (a) in this repository.** A grading path that reaches the triple
> by any other route does not implement clause (a) weakly — **it does not
> implement it at all.**

## 2. WHAT THE INSTRUMENT ACTUALLY DOES — MEASURED, NOT READ

**The ruling's binding sentence reads *"supplies `iterative_states` and
`plateau_states`, or refuses."* That is the right requirement and it is NOT the
instrument's current contract.** Driven directly, `grade_ladder` behaves as
follows. Each row below was executed, not inferred, on a three-level synthetic
ladder with a passing planted-zero control:

| what the caller supplies | what `grade_ladder` does | under `python3 -O` |
|---|---|---|
| `iterative_states=None` | **`Refusal` raised** — *"no iterative-convergence states supplied; step (a) of rule 5 cannot be evaluated and an unevaluated step is not a passed one"* (`:585–:588`) | **identical — the refusal survives**, because it is a `raise`, not an `assert` |
| **`iterative_states={}`** | **`PASS`.** Step (a) passes **vacuously** | same |
| **`iterative_states={'c':'CONVERGED'}` on a c/m/f ladder** | **`PASS`.** Levels `m` and `f` are **never checked** | same |
| all three `CONVERGED` | `PASS` — correct | same |
| any level not `CONVERGED` | `NOT A RESULT` — correct | same |

**Two consequences, both load-bearing for this specification:**

**(2a) THE REFUSAL IS BYPASSABLE BY AN EMPTY DICT.** `:585` tests
`iterative_states is None`. **`{}` is not `None`**, so it skips the refusal, and
`bad_it` (`:581–:582`) iterates *the supplied dict's* keys — of which there are
none. **A caller who supplies `{}` gets a `PASS` on step (a) having measured
nothing, and the record shows `iterative_convergence: {}` rather than a refusal.**

**(2b) THERE IS NO COVERAGE CHECK AGAINST `levels`.** `bad_it` and `bad_pl` are
built from the state dicts, never compared to the ladder's level names. **A dict
naming one of three levels silently leaves two ungated.**

**(2c) `plateau_states=None` is LEGAL and is not the same defect.** The docstring
(`:549–:553`) permits it *"when the quantity has no plateau to measure"* and
requires the record to **say so** — *"an absent measurement is reported as
absent, never as a pass"* (`VERIFICATION_CHARTER.md` §9). **So the ruling's "or
refuses" is exactly right for `iterative_states` and is stricter than the
instrument for `plateau_states`, where the obligation is a DECLARATION rather
than a refusal.** This specification adopts the stricter reading and makes the
declaration mandatory and pre-registered.

## 3. THE SPECIFICATION

### S-1 — THE CALL. One entry point, no reimplementation.

Every cfd grading path that issues a grid-triple verdict **calls
`roache_triple.grade_ladder`**, thus:

```
row = RT.grade_ladder(
    quantity,                 # the registered gate name
    levels,                   # [{name, cells, value}, ...] COARSE FIRST, >= 3
    dim,                      # required; printed beside every order and GCI
    band,                     # (lo, hi) pre-registered.  No band, no grade.
    plant_control,            # planted_zero_control(...) or external_plant_control(...)
    iterative_states=...,     # MANDATORY -- see S-2
    plateau_states=...,       # MANDATORY or DECLARED-ABSENT -- see S-3
    fs=RT.FS, form=..., reference=...)
```

**`triple_from_cells` and `all_triples` are NOT grading entry points.** They are
the clause-(2) engine. A successor registration may call them for diagnostics
**only where the record says the call grades nothing**, and never on the path
that produces a verdict.

**A grader that computes its own convergence ratio, class or order is
non-conforming**, whatever its arithmetic. `grade_f3.py`'s `roache()` is
arithmetically defensible and still bypasses clause (a); **correct arithmetic in
the wrong place is the defect.**

### S-2 — WHAT `iterative_states` MUST CARRY

- **A mapping `{level name: state}` whose keys are EXACTLY the `name` of every
  level in `levels`** — no level absent, no key that names no level.
- **Each value is the result of a measurement made on that level's own run**,
  cited in the record by artifact path. `"CONVERGED"` is the only value that
  passes; anything else routes the row to `NOT A RESULT`.
- **The measurement itself is pre-registered** — the criterion, its window and
  its threshold are in the frozen document **before the solver starts**, and
  §4 fixes its shape.
- **`{}` is FORBIDDEN.** Where no measurement exists the caller supplies `None`
  and takes the refusal. **An empty dict is a claim to have checked; `None` is
  an admission of not having checked, and only the second is honest.**

### S-3 — WHAT `plateau_states` MUST CARRY

- The same mapping discipline as S-2, with `"PLATEAUED"` the only passing value.
- **`None` is permitted for a quantity with no plateau to measure, and ONLY
  when the pre-registration says so in terms, naming the quantity and the
  reason.** The graded record must then carry `plateau: null` **beside an
  explicit declaration of absence** — the discipline
  `verification/runs/F12_runs/roache_triple_pin.json` already keeps.
- **An undeclared `None` is non-conforming.** *That is precisely the state the
  two notes filed today record, and it is what this clause exists to make
  impossible to reach again by omission.*

### S-4 — THE REFUSAL, WHEN THE STATES CANNOT BE SUPPLIED

**The refusal is a refusal, not a softer verdict.**

- The grader **raises** — `raise` or `sys.exit`, **never `assert`** — and exits
  non-zero. It does **not** return `NOT A RESULT`, because `NOT A RESULT` is a
  graded outcome and this is a failure to be able to grade.
- The refusal message names **the quantity, the missing states, and the level
  names that could not be supplied.**
- **Every refusal path is exercised under `python3 -O` in the grader's own
  selftest**, and the selftest fails if the refusal does not fire there.
- **The grader carries an AST check requiring ZERO `Assert` nodes in its own
  source**, run in the selftest. *It catches a revert without running anything —
  which is the point, because the failure it guards against is invisible at
  runtime.*

**Rationale, from this lab's own measurement:** the supervisor's closeout
`CFD_ASSERT_EXPOSURE_CLOSEOUT_2026-08-25.md` measured that under `-O` a stripped
`assert` does not merely go silent — **the prints that followed it still ran, so
the script CERTIFIED a control that never executed.** A guard that can be
compiled away is worse than no guard, because it manufactures the assertion of
having checked.

### S-5 — WHAT THE RECORD MUST SHOW

The graded artifact carries, per row: `iterative_convergence`, `plateau`, the
artifact path each state was measured from, and the pre-registered criterion.
**A row whose `iterative_convergence` is `{}`, or whose keys do not cover its
levels, is non-conforming on its face** — so the defect is visible to a reader
of the JSON without re-running anything.

## 4. THE MEASUREMENT BEHIND THE STATES — POINTER, NOT A NEW GATE

**This specification does not invent a convergence criterion**, and choosing one
now, having seen what the fired conversions graded, would be the same fit rule 2
forbids. cfd has one already registered: **F6a §3.1 `(P-a)`–`(P-d)`**
(`verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md:502–542`), the Class C
gate the census names as **the best in the lab**, with the supervisor's
ADDENDUM 3 governing `(P-a)`. The census §4 draft
(`CFD_CONVERGENCE_GATE_CLASSIFICATION_2026-08-25.md`) sets out C-1 sustained
floor, C-2 trend fit rejecting a growing series, and the remaining elements.

> **A successor registration adopts a criterion of that shape and freezes it
> before its solver starts. This document fixes only HOW the result of that
> criterion reaches rule 5 — not what the criterion is.**

## 5. TWO INSTRUMENT DEFECTS **REFERRED**, NOT FIXED HERE

`scripts/roache_triple.py` is the lab-wide shared instrument and Roache/GCI
gating is **verification territory**. **This lane does not edit it and has not.**
Both findings in §2 are referred to cfd-supervisor for onward referral:

1. **`iterative_states={}` bypasses the `:585` refusal** and passes step (a)
   vacuously (§2a). A one-line repair exists — test falsiness rather than
   identity — but it changes the behaviour of an instrument every graded triple
   in the lab passes through, **and that is not a cfd lane's call.**
2. **No coverage check binds the state dicts to `levels`** (§2b), so a partial
   dict leaves levels silently ungated.
3. **Reported alongside, measured and NOT overclaimed:** `scripts/roache_triple.py`
   contains **4 `Assert` nodes** — 3 in **`_seal` (`:629`)**, the function whose
   docstring calls them *"the two structural assertions that make the printed row
   trustworthy"* (it carries three), and 1 in `require_dim` (`:186`).
   **Under `python3 -O` all four are stripped.** `_seal`'s asserts are the guard
   on rule 1's vocabulary and on rule 5's one-way door.
   **This lane did NOT measure a realized failure from them** — in the probe runs
   the verdicts were legal, so the asserts had nothing to catch — **so the
   exposure is reported as LATENT AND MEASURED-BY-COUNT, not as demonstrated.**
   Given the closeout's finding that "latent" understated the same shape once
   already, it is referred rather than filed away.

**None of the three is in cfd's gift, and none is acted on here.**

## 6. STATUS

> **OWED. NOT APPLIED. NOT DUE FROM ANY FIRED REGISTRATION.**
>
> This specification binds the **next** cfd registration that grades a grid
> triple, and it binds it **at its pre-registration**, not at its grading. It
> imposes nothing on `grade_f3.py`, `grade_f4.py`, `grade_f11.py`,
> `rae2822_case9.py` or any other instrument whose gates rule 2 has closed.

## 7. COST

**ZERO COMPUTE. No `docs/COST_CALIBRATION.md` row is owed and none is filed** —
rule 12's estimate-versus-actual comparison attaches to a process completion
with a solver spend. This is a records-and-specification item with no solver
run, and **saying so is more honest than filing a row of zeroes.**
