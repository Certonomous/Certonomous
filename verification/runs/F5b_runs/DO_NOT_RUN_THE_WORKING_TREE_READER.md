# WARNING — the working-tree copy of `analyse_f5b_physics.py` is BROKEN. Do not run it.

**Stamp:** 2026-08-25. **Raised by:** cfd lab-lane. **Status: awaiting Sanaa's decision.**

**This file is a warning artifact. It touches nothing. The reader itself has NOT been
modified since the denial and MUST NOT be, by anyone, until Sanaa rules.**

## What is wrong

The working-tree copy of `verification/runs/F5b_runs/analyse_f5b_physics.py` carries a
**half-applied repair** and is **not runnable as a grader**:

- It calls **`_finish_after_time_dir(...)`**, a helper that **does not exist** — one dangling
  reference.
- That path would make an unresolved endTime directory **short-circuit clauses 5, 7 and 8**
  instead of evaluating them. **That is a degradation, and this reader's entire design is to
  refuse rather than degrade.**

**Anything this file reports in its current state is untrustworthy.** It has not been used to
grade anything and must not be.

## What is NOT wrong

**Nothing is committed. HEAD is clean.**

| | |
| --- | --- |
| HEAD blob | `6c6d34d02e6de925457dbfdbf75a0e004168f345` |
| stage-2 freeze blob (`a80d5f36`) | `6c6d34d02e6de925457dbfdbf75a0e004168f345` — **identical** |
| broken working-tree blob | `277463b1dfd4fd85fcd1de13cb738b9435811d0f` (uncommitted) |

**The original frozen reader is intact at HEAD and recoverable from git.** A byte-exact
pre-repair copy is also held outside the repository by the lane that made the change.

## Why it was left broken rather than fixed

The repair was being applied in two steps under `VERIFICATION_CHARTER.md` §2d.1's
four-condition repair exception. Step 1 applied. **Step 2 — the correction that removes the
dangling call and the degradation — was DENIED by the permission system.**

**The denial was not routed around.** No retry under a different command shape, no
`git checkout --` / `reset` / `stash` (forbidden outright by standing rule 10), and no
delegation to another agent — a peer performing a denied action bypasses the user's
permission decision, which standing rule 9 forbids. Both remaining options (finish the
repair, or restore the file) are themselves **edits to the file whose edit was denied**, so
picking whichever shape the classifier happens to permit would be routing around the denial
by trial. **The file is therefore left exactly as it stands.**

## The state that must be preserved

**No agent has inspected F5b's gate quantity, and none may until Sanaa rules.** The reader
stopped at completion and printed no `A_L`; `coefficient.dat` has never been opened or
plotted. **That is what keeps the §2d.1 freeze condition intact and every option open — a
lane that peeked would have foreclosed all of them.**

## F5b's verdict is unaffected

**`NOT A RESULT`** stands on its own, from the frozen reader run unmodified before any of
this: completion clauses 4 and 6 failed because the reader resolved the endTime directory by
**string match** on `END_TIME_STR = "21.9440"` while OpenFOAM wrote `case/21.944/`.
Recorded in `physics_p1/RESULTS.md`; costed in `docs/COST_CALIBRATION.md` row **C-65**.

## Do not

- **Do not run this file.**
- **Do not edit, restore, rename, move or delete it** until Sanaa rules on the denial.
- **Do not grade F5b with it**, or with any patched copy.
- **Do not inspect F5b's gate quantity** by any means, including a quick look at a `.dat` or
  a plot. Doing so voids the §2d.1 addendum path and would force a fresh solve.
