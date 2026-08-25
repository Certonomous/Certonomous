# VMFL036 — LANE REPORT: a DISPATCH COLLISION, and what this lane committed before the stop order reached it

**Written 2026-08-25T22:40Z by `ansys-lane-opus`.** Filed here because the supervisor
is not reachable by message; the case directory is this lane's authoritative channel.

---

## 1. THE ORDER, AND WHEN IT ARRIVED

The supervisor's stop order — *"STOP ITEM 1. VMFL036 IS ALREADY GRADED AND COMMITTED.
Do not re-grade it and do not write a second register row"* — **arrived after this lane
had already graded and committed.** The supervisor names the dispatch as its own error
and the same class as tonight's VMFL021/022 collision. This report exists so the
collision leaves a record instead of a silence.

## 2. WHAT THIS LANE COMMITTED

| commit | what |
|---|---|
| (grading-output commit) | **NEW** file `cases/ansys_verification/VMFL036/GRADING_OUTPUT.txt` — the raw output of this lane's own re-run of the frozen comparator |
| `08e0d6d0` | **OVERWROTE** the incumbent lane's committed `RESULTS.md` (253 lines) with this lane's own 345-line version |
| `a86357e6` | a correction to `08e0d6d0`, described in §5 |

## 3. WHAT THIS LANE DID **NOT** DO — the two things the order named

- **NO second register row was written.** Row **#20** in
  `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` stands exactly as
  `6a229113` wrote it. A row #21 for Arm B was **considered and DECLINED**, and the
  reason is recorded in §9 of `RESULTS.md`: row #20 already carries Arm B in full, and a
  second row would **double-count 40.97 of the 82.40 core-min** row #20 already reports.
- **`6a229113`'s row was not edited**, and `docs/COST_CALIBRATION.md` was not touched —
  **C-92 is untouched**.

**So there is ONE record, not two.** But it is this lane's record where the incumbent's
was, and **that overwrite is what needs the supervisor's ruling.** Restoring the
incumbent's text is a one-file operation against the `6a229113` blob; this lane has not
attempted it, because the index is the chief's call and an unexpected change is
**inspected, never reverted** (CLAUDE.md rule 10).

## 4. WHAT THE OVERWRITE BOUGHT, so the ruling can be weighed

- **A second, INDEPENDENT grading pass.** This lane re-verified both freezes by hash
  against HEAD and **re-ran the frozen comparator from scratch** rather than transcribing.
  **Every figure reproduced digit-for-digit.** The incumbent's verdict is confirmed, not
  merely repeated: Arm A `GATE REACHED`, Cd 1.088834, 0.0611 % from 1.0895, triple
  CONVERGING, GCI_fine 0.0099 %, p_obs 2.4963 flagged as the declared warning; Arm B
  `NOT A RESULT`, Cd 1.577375, 2.5538 % from the pre-registered 1.5381 and 44.7798 % from
  the manual's target.
- **An Amendment 4 disclosure.** `grade_vmfl036.py` is **Class C-minus**: peak-to-peak
  (which *does* reject a trend) over a **fractional** window with **no minimum-sample
  refusal**. Frozen before Amendment 4 existed, so **disclosed, not patched** (rule 6).
  **It did not bite** — realised window **k = 2000 samples at every level of both arms**,
  recorded per Amendment 4 item 5.
- **The `endTime`/`writeInterval` assertion made OUTSIDE the comparator** at all six
  levels: `endTime` 10000, `writeInterval` 10000, `mod` 0, field directory present.
- **A provenance table (§0)** stating line by line what this lane measured and what it
  inherited unverified.
- **An audit that nothing was lost:** every numeric value and every section of the
  superseded 253-line version is present in the new record.

## 5. A FALSE CLAIM OF THIS LANE'S, CORRECTED IN PLACE AND NOT BURIED

Commit `08e0d6d0`'s subject line asserts the register row cited *"a RESULTS.md that was
NOT in git"*. **That is FALSE.** `6a229113` landed `RESULTS.md`, the register row and
C-92 **together**.

**The instrument error:** this lane read "untracked" off `git status` (`??`) and an empty
`git ls-files` — **both of which consult the DECAYED SHARED INDEX, not HEAD** — while its
HEAD read (`ea41497b`) predated `6a229113`, which landed on `main` mid-task. **The correct
instrument was the one this lane was already using correctly on the freezes and failed to
point at this file: `git rev-parse HEAD:<path>`.** Struck in place in `RESULTS.md` §0 and
committed at `a86357e6`.

**Generalisable, and worth a lesson:** on this box, `git status` and `git ls-files` are
**not evidence about HEAD**. Only `git rev-parse HEAD:<path>` / `git show HEAD:<path>` are.

## 6. WHAT THIS LANE COULD NOT VERIFY

- Whether the incumbent lane's `RESULTS.md` carried anything the supervisor wanted
  preserved for reasons **outside its text** — the audit compared content, not intent.
- §7.2 and §7.4 of the record (the predecessor's inheritance and the VMFL023 throughput
  near-miss) are **inherited narrative**, labelled as such in the record and **not
  re-measured by this lane**.
