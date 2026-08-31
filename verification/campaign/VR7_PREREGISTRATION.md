# VR7 — CALIBRATION ROW COMPLETENESS

**Repair-registration. Frozen before any work under it. Written 2026-08-31.**

## 1. The finding this measures

`CLAUDE.md` rule 12 requires an estimate-versus-actual comparison **at every process
completion** — Sanaa's directive of 2026-08-23, verbatim: *"for all teams involved once a process
is completed, the estimated costs must be compared with the actual incurred costs so we can
improve the lab's estimates"* — landing as a row in `docs/COST_CALIBRATION.md`. The rule closes:
**"A completion report without this comparison is incomplete."**

This item measures how much of that obligation is actually discharged: of the rungs this lab has
**launched**, how many carry a row?

## 2. WHAT IS MINE, AND WHAT THIS ITEM INDICTS

The **measurement** is mine. The **rows** are each team's own to write and this item writes none.

**THIS ITEM INDICTS ITS OWN TEAM FIRST, and that is why it is admissible.** Verification's six VR
rungs are all launched and all graded, and none carries a calibration row. A rung that could only
vindicate its author is not worth filing; this one convicts him.

### 2a. Rule-2 condition, and how it was checked

No compute has been spent under this document. The condition is that the queue run this item
registers **has not happened**: the run artefacts it will create —
`STATUS.VR7_CALIBRATION_ROW_COMPLETENESS` and `launcher.queue.out` under the registered cwd
`/home/ubuntu/Certonomous/verification/runs/verification/VR7_CALIBRATION_ROW_COMPLETENESS/` —
**do not exist**, checked by direct `ls` of that directory before this file was written.
Amendments before the first queue launch are legal and carry this same statement; after it, gates
are closed.

### 2b. Disclosed: the driver was DRIVEN before enqueue

Stated honestly rather than presented as first contact, following VR5/VR6's precedent.
`verification/credibility/vr7_calibration_row_completeness.py` was driven with `--selftest` before
enqueue: **7 cases, 0 failures, rc 0**. The §5 prediction is informed by that drive. An entry
naming a script that has never run is the `L-344` class and is not enqueued here.

## 3. Gate (frozen)

A committed driver under `verification/credibility/` that:

- **G1** enumerates every **distinct launched rung** from `verification/queue/LAUNCH_LOG.tsv` —
  written by `scripts/queue_runner.py`, the real producer.
- **G2** determines, per rung, whether its `case_id` appears **inside a row-anchored entry** of
  `docs/COST_CALIBRATION.md`. **ROW-ANCHORED IS LOAD-BEARING:** a free-text scan of that file
  returns **910** hits against **229** real rows, because rows cite other rungs in prose. A prose
  mention is not that rung's calibration row.
- **G3** controls, both limbs, **on real bytes** (§2j): the reader must be shown returning
  `HAS_ROW` on a real covered rung **and** `NO_ROW` on a token proven absent, in the same
  invocation; and a real prose line carrying an id must be rejected as a row.
- **G4** **REFUSES (exit 2)** rather than degrading when either file is unreadable or the matcher
  yields zero ids — *"I cannot read the ledger"* and *"nothing is calibrated"* are the same output
  from a broken parser and only one is a finding.

## 4. Threshold / label

- **PASS** = every launched rung carries a row-anchored calibration entry.
- **GATE FAIL** = any launched rung does not.
- **NOT A RESULT** = a control limb misbehaves.
- **BLOCKED** = neither input file can be read.

This item may emit **only** `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.
`GATE REACHED` is not reachable here: this is a completeness census, not a threshold approach.

## 5. PREDICTED OUTCOME — stated as a prediction, before the run

**I predict GATE FAIL, and I predict it against my own team's record.**

Measured 2026-08-31 during drafting, disclosed under §2b: **210** distinct launched rungs, of which
**57** carry a mention and **153** do not. **All six VR rungs are in the uncalibrated set.**

If the run instead returns PASS, that is a **falsification of this prediction** and the honest
reading is that my draft-time measurement was wrong — not that the gate should move.

## 6. Cap and cost

**Registered estimate: 0.05 core-minutes. Cap: 0.5 core-minutes.**

Arithmetic, **costed on the CONTENDED box** (load average 7.8–15.0 over 16 cores at drafting;
the box was at 28.5 earlier the same day, and the quiet-box figure is the flattering one and is
not used):

```
selftest drive, measured on the contended box : 0.135 s wall x 1 rank / 60 = 0.00225 core-min
registered estimate, with contention headroom :   3    s wall x 1 rank / 60 = 0.05    core-min
cap, ~10x the registered estimate             :  30    s wall x 1 rank / 60 = 0.50    core-min
```

Dollars **DERIVED, NOT MEASURED** at $0.0513/core-h — itself **reported-by-owner**, because the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5):

```
estimate : 0.05 core-min / 60 x $0.0513 = $0.0000428   DERIVED-NOT-MEASURED
cap      : 0.50 core-min / 60 x $0.0513 = $0.000428    DERIVED-NOT-MEASURED
```

**Zero solver compute.** An overrun **stops the run**; it does not get a new budget (rule 12).

## 7. Not claimed

No verdict is withdrawn by this item, and no run is re-graded. A missing calibration row is a
**bookkeeping defect in the record**, never a defect in the physics it failed to price — Sanaa's
universal rule of 2026-08-26: **bookkeeping never voids physics.** The remedy is to **write** the
rows, never to delete anything, and the rows belong to their teams.

This item does not price anything itself and produces no calibration row of its own.
