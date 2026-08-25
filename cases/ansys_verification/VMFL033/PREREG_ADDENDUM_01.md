# VMFL033 — PREREG ADDENDUM 01 — 2026-08-25T22:52Z

## A COMPARATOR REPAIR UNDER `VERIFICATION_CHARTER.md` §2d.1: the frozen selftest PRINTED `SELFTEST GREEN` WHILE A CONTROL THAT MUST FAIL HAD FAILED

Dated addendum appended beside the frozen pre-registration, which is **not edited**
(CLAUDE.md rule 6). **No gate, band, threshold, cap, label, reference, normaliser,
plateau window or ladder moved.** The pre-registration's ten lines stand exactly as
frozen at `9b0b573c`.

---

## 1. WHAT WAS FOUND, AND BY WHOM

The supervisor mutation-tested three of this team's comparators, breaking
`completion` so the strict-completion control **must** fail, and measured:

    VMFL036  mutant -> rc 1, no green line   correct
    VMFL023  mutant -> rc 2, no green line   correct
    VMFL033  mutant -> rc 0, GREEN PRINTED   FALSE CLAIM

**This lane did not take that on faith.** It reproduced the mutation itself, and
**confirms the finding**: the frozen `grade_vmfl033.py` exits 0 and prints
`SELFTEST GREEN` with a mutated `completion()` that can never raise, under **both**
`python3` and `python3 -O`.

### 1.1 The cause is NARROWER than the diagnosis, and the difference matters

The supervisor's stated cause was that this comparator's `CONTROL FAILED` fall-throughs
are badly shaped, so a control can silently fail and the function still return.
**Measured, that is not what happened here.** Mutating the reader and the plateau clause
made the frozen selftest exit 2 with no green line — **those two controls were correctly
shaped and DID fail on break.**

> **The real cause is a MISSING control, not a badly-shaped one. The frozen selftest
> never exercised `completion()` at all.** VMFL036 carries an empty-directory completion
> control; this one carried none. Breaking a check that nothing calls changes nothing,
> and the unconditional terminal `print("SELFTEST GREEN")` was then reached.

**Recorded because the two causes need different fixes.** A badly-shaped control is fixed
by reshaping it. **A missing control is invisible to any amount of reshaping** — and it is
invisible to a code review that only inspects the controls that exist.

### 1.2 A SECOND defect, which the supervisor's mutation set could not have found

Reading the code for the first defect exposed a different one. The frozen controls matched
an expected refusal by **substring**, inside `except Refusal:` blocks, with a fall-through
written as `refuse(...)` — **which the same handler catches.** Where the control's own
failure message happened to contain the substring it matches on, its failure was
**swallowed**. The `UNIFORM`-reader control was exactly that shape: it matched on
`"UNIFORM"` and its own failure message read *"the reader accepted a UNIFORM field as
evidence"*.

**DEMONSTRATED, not theorised** — the isolated shape returns normally in BOTH cases:

    reader correctly refuses -> RETURNED NORMALLY
    reader FAILS to refuse   -> RETURNED NORMALLY

> **AND THE MUTATION SET MASKED IT.** Mutating the reader tripped a *different* refusal
> (the count/header check) whose message does **not** contain `"UNIFORM"`, so the control
> re-raised and the mutant looked correct. **A mutation test can hide a defect when the
> mutant trips a neighbouring control.** That is a limit of the method, found by using it,
> and it is why the fix below is structural rather than message-based.

## 2. THE REPAIR

1. **A new exception type, `ControlFailure`, that NO `except Refusal` catches.** Every
   selftest fall-through now raises it. The swallow of §1.2 becomes **structurally
   impossible** rather than avoided by careful wording.
2. **Every control has exactly ONE path that lets the selftest continue — the one where
   its subject behaved.** Every other path raises `ControlFailure`.
3. **Controls ADDED that did not exist:** `C10` strict completion must refuse an **empty
   directory**; `C11` it must refuse a level recording **`rc = 1`** as a finding; `C9` the
   **vector** reader must refuse a file with no `internalField`.
4. **`main` catches `ControlFailure` separately** and exits 2 with *"a selftest that cannot
   fail is not evidence"*.

**The binding rule this serves, which the supervisor states and this lane adopts:** never
print a success claim unconditionally after a check — print inside the passing branch, or
make the failing path exit, so that **removing or breaking the check removes the claim**.

## 3. VERIFIED BY MUTATION, NOT BY READING

**8 mutants x 2 interpreters = 16 runs. Every one: `rc = 2` and NO green line.**
Mutants: `completion` cannot raise; the scalar reader accepts anything; the vector reader
accepts anything; `plateau` never refuses; `roache` always says CONVERGING; `v_exact`
returns 0; `T_exact` returns 0; the independent BVP control is disabled.
**Control on the control:** the unmutated file is `rc = 0` **with** the green line, under
both interpreters.

### 3.1 THE DETECTOR ITSELF WAS WRONG ON THE FIRST PASS, and it is recorded

The first mutation run reported `green=1` on **every** mutant while `rc = 2`. The
behaviour was correct; **the instrument was not.** The detector grepped for the substring
`SELFTEST GREEN`, and the new failure message reads *"No **SELFTEST GREEN** line is
printed…"* — **so the detector matched its own disclaimer.** Re-run with an anchored
`^SELFTEST GREEN$` it reads 0 on every mutant.

**Recorded rather than quietly corrected**, because the direction of the error was
lucky: a detector that over-reports green would, on a different day, have **hidden a real
false green** instead of manufacturing a fake one. **A green flag with no explanation was
not waved through.**

## 4. §2d.1's FOUR CONDITIONS, ANSWERED

**(1) A DEMONSTRABLE ERROR, not a preference.** A selftest that prints `SELFTEST GREEN`
while a control that must fail has failed is not a matter of taste. Reproduced by this
lane under both interpreters.

**(2) ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — the load-bearing
condition, and it is satisfied in its strongest available form.** The error was found by
**mutation testing, which grades nothing** and cannot know which direction a verdict would
move. Stronger still: **the defect is in the SELFTEST, not on the grading path** — it
touches no gate, band, reference, normaliser, window or label, and it **emitted no
number**. Strongest of all: **at the moment of repair NO LEVEL HAD BEEN GRADED AND NO
VERDICT EXISTED**, so there was no verdict and **no direction in which to select**.

**(3) THE RECORD DISCLOSES IT, NAMES THE INSTRUMENT, AND QUANTIFIES WHAT MOVED.** This
document. Instrument: mutation testing (§3). **What moved: NOTHING on the grading path.**
The repair adds three controls, changes an exception type and reshapes fall-throughs. The
gate, both bands, both registered expectations, the plateau window and floor, the Roache
functional, the caps and the tier ceiling are **byte-identical** to the freeze.

**(4) PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES.** **There are none, and that
is the point.** No level had been graded and the comparator had produced no number when
the repair was made. The two levels that had completed under attempt 1 were **never
graded**, and attempt 1 is abandoned in full (§5) rather than carried forward, so no
published value has a pre-repair counterpart.

## 5. ATTEMPT 1 IS ABANDONED, PRESERVED, AND ITS COST NAMED AS WASTE

The graded family had started when the defect surfaced. `L1_nr32` and `L2_nr64` had
completed (`rc = 0`); `L3_nr128` was killed during `blockMesh`, with **zero solver
iterations**. **Nothing was graded and no verdict existed.**

**The whole attempt is abandoned** so the graded family runs entirely under the repaired
comparator, rather than half under each. It is **PRESERVED, not deleted**, at
`verification/runs/ansys_verification/VMFL033_attempt1_ABANDONED_PARTIAL/`.

**WASTE: 1.0334 core-min, MEASURED** (L1 0.4167 + L2 0.6167 + an L3 fragment of 0 solver
seconds), from each level's own `RUN_RC.txt`. **Named separately per
`COMPUTE_BUDGET_CHARTER.md` §6 and NEVER absorbed into the estimate/actual ratio.**

## 6. WHAT DID NOT CHANGE

No gate, band, threshold, cap, label, reference, reference-kind, tier ceiling, normaliser,
plateau window, plateau floor, Roache functional, ladder or decomposition seed moved. The
pre-registration is unedited. The repair is confined to the comparator's **selftest
control flow** and to three **added** controls.
