# VR9 — LEDGER DUPLICATE ADJUDICATION

**Repair-registration. Frozen before any work under it. Written 2026-08-31.**

> **⚠ READ §5 FIRST. THIS ITEM'S PREDICTED VERDICT IS `PASS`.** It is offered as a standing
> monitor, not as a finding, and the supervisor should weigh that before filing it. I say so here
> rather than at the foot, because a rung whose author expects it to vindicate the lab is exactly
> the rung that should be hardest to file.

## 1. The finding this monitors

`CLAUDE.md` rule 11 fixes how a new id is assigned: **from the TAIL-MAX, never from a count** —
*"Block count, distinct count and highest number are three different figures (L-43 has two blocks,
L-52 does not exist)."*

The residual hazard is the **duplicate itself**. A duplicate makes count and tail-max disagree, and
a count-derived id then **collides with a live entry**. Rule 11 also establishes that **some
duplicates are deliberate** — `L-43`'s second block is the rule's own example. So the honest
question is not *"are there duplicates"* but **"is every duplicate ACCOUNTED FOR."**

## 2. WHAT IS MINE

The **sweep** is mine. The ledgers belong to six teams and **renumbering is each owner's act.**
This item renumbers nothing and edits nothing.

### 2a. Rule-2 condition, and how it was checked

No compute has been spent under this document. The run artefacts —
`STATUS.VR9_LEDGER_DUPLICATE_ADJUDICATION` and `launcher.queue.out` under the registered cwd
`/home/ubuntu/Certonomous/verification/runs/verification/VR9_LEDGER_DUPLICATE_ADJUDICATION/` —
**do not exist**, checked by direct `ls` before this file was written.

### 2b. Disclosed: the driver was DRIVEN before enqueue

`verification/credibility/vr9_ledger_duplicate_adjudication.py` was driven with `--selftest`:
**8 cases, 0 failures, rc 0**.

### 2c. SCOPE, STATED AS A LIMIT — and why `N-` is EXCLUDED

Three ledgers: `docs/LESSONS.md` (`L-`), `docs/DOCKET.md` (`D-`), `docs/COST_CALIBRATION.md`
(`C-`).

**`docs/NUMERICS_KNOWLEDGE.md` (`N-`) is deliberately OUT OF SCOPE.** It already has a dedicated
checker, `scripts/check_numerics_index.py`, wired into `check_harness` stage `[5/5]` by
`DEAD_LEVER_AUDIT` §19. Re-sweeping it from a second, unwired instrument would duplicate a live
control and risk contradicting it. **A first draft of this driver also parsed ZERO `N-` ids with a
plausible-looking regex** — and *"I cannot read this ledger"* and *"this ledger is clean"* are the
same output from a broken parser, of which only one is a finding (§19's own C3/C4 controls).
Excluding it is the honest call, not a convenience.

## 3. Gate (frozen)

A committed driver that:

- **G1** enumerates ids **row-anchored** — opening a heading or the first table cell. **This is
  load-bearing:** a free-text `C-\d+` scan of `COST_CALIBRATION.md` returns **910** hits against
  **229** real rows.
- **G2** reports, per ledger, occurrences, distinct ids, tail-max, the **rule-11 next id**, and the
  id **a count would wrongly give**.
- **G3** classifies each duplicate **ADJUDICATED** — either *declared in the ledger* as a
  deliberate second block, or *ruled* by name in `docs/DEAD_LEVER_AUDIT.md` — or
  **UNADJUDICATED**.
- **G4** controls, both limbs, **on real bytes** (§2j): the reader must be shown seeing a real
  duplicate, returning ADJUDICATED on a real declared second block, and — critically — the
  **audit lookup must be shown to DISCRIMINATE**: withholding the audit text must flip at least one
  ruled duplicate to UNADJUDICATED, or the lookup is inert and is doing no work.
- **G5** **REFUSES (exit 2)** when a matcher yields zero ids or a ledger is missing.

## 4. Threshold / label

- **PASS** = every duplicate id is adjudicated.
- **GATE FAIL** = any duplicate is unadjudicated.
- **NOT A RESULT** = a control limb misbehaves.
- **BLOCKED** = a ledger cannot be read.

Only `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` may be emitted.

**An ADJUDICATED duplicate is EXPLAINED, not CLEARED.** Where `DEAD_LEVER_AUDIT` §22 records a
renumber as **OWED**, that debt is printed beside the verdict, so a pair cannot become permanent by
having been ruled once.

## 5. PREDICTED OUTCOME — `PASS`, and the honest weight of that

**I predict PASS**, and I record why that is a weakness of this rung rather than a strength.

Measured during drafting: **7** duplicate ids across the three ledgers — `L-43`, `L-61`, `L-404`
in `LESSONS.md` and `C-215`…`C-218` in `COST_CALIBRATION.md` — and **all 7 are adjudicated.** The
three `L-` pairs are explicit deliberate second blocks (`L-404`'s own heading reads *"SECOND
BLOCK … in the deliberate second-block form (`L-43`, `L-61`)"*). The four `C-` pairs were **ruled
by this team at `DEAD_LEVER_AUDIT` §22, commit `524a70bd`, 2026-08-31T15:20Z** — roughly forty
minutes before this document was drafted.

**So this item, run today, would grade work its own supervisor had just finished.** It produces no
new finding. Its value is entirely prospective: it fires the moment an **undeclared** duplicate
lands, and `DOCKET.md`'s 584 ids and `LESSONS.md`'s 409 grow constantly.

**The gate can fail** — that is not a formality. Limb P4 demonstrates it: withholding the audit
text flips `L-43` to UNADJUDICATED, so the classifier is not one that says yes to everything.

## 6. Cap and cost

**Registered estimate: 0.05 core-minutes. Cap: 0.5 core-minutes.**

Arithmetic, **costed on the CONTENDED box** (load average 7.8–15.0 over 16 cores at drafting):

```
selftest drive, measured on the contended box : 0.105 s wall x 1 rank / 60 = 0.00175 core-min
registered estimate, with contention headroom :   3    s wall x 1 rank / 60 = 0.05    core-min
cap, ~10x the registered estimate             :  30    s wall x 1 rank / 60 = 0.50    core-min
```

Dollars **DERIVED, NOT MEASURED** at $0.0513/core-h, itself **reported-by-owner**:

```
estimate : 0.05 core-min / 60 x $0.0513 = $0.0000428   DERIVED-NOT-MEASURED
cap      : 0.50 core-min / 60 x $0.0513 = $0.000428    DERIVED-NOT-MEASURED
```

**Zero solver compute.** An overrun **stops the run** (rule 12).

## 7. Not claimed

No id is renumbered and no ledger is edited. `DEAD_LEVER_AUDIT` §22 is **not re-litigated** — its
ruling is an **input** to this item, never an output of it. `N-` is untouched. No verdict is
withdrawn: a duplicate id is a defect in the **record's addressing**, never in the physics the row
describes.
