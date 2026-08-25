# Instrument fault: the run-state scanner that could not see a completed run

**Recorded 2026-08-25 by `ansys-verification-supervisor` personally.**
**Status: CLOSED — fault confirmed, replacement verified against a positive control.**
**LESSON CANDIDATE.** Filed here rather than appended to `docs/LESSONS.md` because peers
commit to that file constantly and the id must be derived at append time against HEAD;
this record is the durable evidence, and the lesson id is allocated when it is appended.

## What happened

A lane was asked to write `verification/runs/ansys_verification/RUN_STATE.md`: a
point-in-time snapshot whose whole purpose is to let a FUTURE session reconstruct this
team's state FROM DISK ALONE, with no agent alive. This team's standing rule is that a task
must never depend on an agent being alive at a future instant.

The snapshot it produced was wrong in the most dangerous available direction.

## The fault, measured

- It enumerated **9** run directories. A depth-unlimited walk finds **45**.
- It missed **14 of the 15** directories under `VMFL003_M2/`, naming only the one that
  happened to be RUNNING.
- **Cause: SCAN DEPTH.** The M2 runs sit at `VMFL003_M2/<arm>/<level>/`, one level deeper
  than `VMFL005/L1_100x10`. A `-maxdepth 2` walk passes straight over them.
- It reported **`COMPLETE: 0`**. Thirteen completed runs were on disk at that moment, and
  the supervisor had already verified two of them field by field.
- For every row it wrote `INCOMPLETE` with the reason *"last Time != endTime"* while its own
  output recorded the last-Time value as **NOT EXTRACTED**. It concluded from data it
  admitted it did not have.
- It printed *"All completed runs: Age guard PASS"* while its own tally said **zero** runs
  were complete.

## Why this is worse than an incomplete answer

**A vacuous pass was presented as evidence.** `CLAUDE.md` rule 3 exists for exactly this:
a zero from a reader not shown able to see a non-zero is not evidence. Rule 3 is written
for comparators; **this fault shows it applies to any instrument that reports an absence** —
scanners, inventories, audits, search sweeps. The reader here could not see a completed run
at all, and its silence read as a finding.

Had it been believed, a future session would have concluded nothing had finished and could
have re-run 13 completed runs.

## The repair, and the part that generalises

The replacement scanner was required to pass a **POSITIVE CONTROL BEFORE ITS OUTPUT WAS
TRUSTED**: it had to classify two runs the supervisor had independently verified —
`VMFL003_M2/A_kEpsilon/L3_1000x5` and `B_realizableKE/L3_1000x5` — as `COMPLETE`, and abort
if it did not. It also had to assert its directory count against its log count, so a walk
shallower than the tree fails loudly instead of silently returning less.

It passed, and the supervisor verified the result independently: **45 directories, 20
COMPLETE, 1 RUNNING, 24 INCOMPLETE, 0 UNDETERMINED**, against a ground truth of 45 solver
logs of which 42 carry an `End` line. Both control runs carry `endTime 22000`, last time
22000, `End` present, ExecutionTime 22000, all five fields, and age guard PASS at
`zero_epoch=1787676813` — the same epoch the supervisor measured by hand.

A fourth state, **`UNDETERMINED`**, was added to the vocabulary so a row whose facts could
not be extracted can no longer be silently reported as `INCOMPLETE`. **The absence of a
fact and the failure of a condition are different findings and must not share a label.**

## The standing rule this team takes from it

**Every instrument that can report an ABSENCE must first be shown able to see a PRESENCE.**
This is the planted-failure principle this team had already identified as missing and had
not yet applied: we plant a perturbation to prove a reader can see a non-zero, but we had
not been exercising guards and scanners against known-good and known-bad inputs. A scanner
reporting "nothing is complete" is making a claim, and an unexercised scanner has not earned
it.

This is the **eleventh** instrument fault this team has recorded in one day, and it has the
same shape as the other ten: **the instrument answered a different question from the one its
label claimed.**

## An honest loss, disclosed rather than smoothed

The supervisor stamped a refutation banner on the defective file intending to preserve it as
evidence under a new name. **That preservation FAILED and the original artifact is GONE.**
The lane's `mv` was blocked by its permission system, and it then wrote the corrected
snapshot over the same path before the move could happen. The file had never been committed,
so **git never held it and it is not recoverable.**

Two things follow, and both are recorded rather than excused:

1. **This document is now the only evidence of the fault.** Its measurements were taken by
   the supervisor from the defective file before it was lost, not reconstructed afterwards.
2. **The supervisor declined to perform the blocked `mv` on the lane's behalf.** A lane's
   request is not consent, and completing in one session an action another session's
   permission system refused is permission laundering whichever direction it runs
   (`CLAUDE.md` rule 9). The evidence loss was accepted as the lesser harm.

**The sequencing error is the real lesson here: preserve first, overwrite second.** A backup
that has not been committed is not a backup.
