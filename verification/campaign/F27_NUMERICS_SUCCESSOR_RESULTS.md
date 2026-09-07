# F27-Womersley numerics successor — results: **BLOCKED on the pre-registered cap (a lawful halt)**

Run 2026-09-07 against the frozen pre-registration
`verification/campaign/F27_NUMERICS_SUCCESSOR_PREREGISTRATION.md` (freeze commit
`b86fe0cc`, FROZEN / AUTHORISED, cfd-supervisor checks 1 AND 4
PERSONAL+UNDELEGATED, both PASS; est ~372 / hard cap 500 core-min, 4 ranks).
Levers over the parent (frozen, confirmed by the supervisor's check-1 diff):
`nNonOrthogonalCorrectors` 1->3, plus limited laplacian / snGrad / grad schemes;
every band, gate and planted control byte-identical to the frozen parent, not
widened. Grading path `grade_f27_successor.py` (sha256 `53f74800…`), hashed at
grade time by the driver's rule-2 gate. Verdict set by the cfd supervisor; this
record files it.

## Verdicts

| level / gate | verdict | why |
| --- | --- | --- |
| **coarse** | strictly complete | reached `End`, RC = 0. |
| **medium** | strictly complete | reached `End`, RC = 0. |
| **fine** | not run | **HALTED BEFORE SPENDING** on a lawful rule-12 projected cap breach; the level directory holds only `box_before.txt` (no mesh, no solve). |
| **The grid triple (as a whole)** | **`BLOCKED`** | only 2 of 3 levels ran; the triple is INCOMPLETE, so no GCI is gradeable. This is a lawful halt on the pre-registered cap, **not** a crash. |

## The cap breach — the arithmetic, measured

The fine level was refused **before any spend** because its projected cost alone
crosses the whole-run cap. From
`verification/runs/F27_NUMERICS_SUCCESSOR_runs/CAP_BREACH`:

- spent so far (coarse + medium): **15.0 core-min**
- projected fine level **alone**: **526.7893 core-min**
- projected total: 15.0 + 526.7893 = **541.7893 core-min** > cap **500** core-min

Basis: THIS RUN's measured medium rate **20.733 core-us/cell-step** (ClockTime
214 s x 4 ranks / 41,287,680 cell-steps), carried forward by the **frozen
registered growth factor 2.3078** -> **47.8462 core-us/cell-step** on the fine
level's **660,602,880 cell-steps**. Contention factor 1.0.

**The cap was NOT raised** (correct, rule 12: an overrun stops the run; it does
not get a new budget). The fine directory contains only an infrastructure
observation file (`box_before.txt`), which the pre-spend projector does not read;
no mesh and no solver ran.

## Why the estimate missed

The changed numerics (`nNonOrthogonalCorrectors` 1->3 plus the limited schemes)
grew the per-cell-step cost such that the **fine level alone (526.8 core-min)
exceeds the entire whole-run estimate (372 core-min)**. The pre-registration
under-predicted the changed-numerics per-cell-step growth. Calibration row
`docs/COST_CALIBRATION.md`.

## What completing the fine level would take

Completing the triple requires the fine level to run, which requires a **cap
decision by the chief / Sanaa** (escalation / rule-12 territory). **Rule 12
forbids an in-flight cap raise** by any lane or supervisor — the halt stands until
a higher authority sets a new budget. Nothing here raises it.

## Cost — measured

**15.0 core-min spent** (coarse + medium) before the lawful halt; the fine level
spent nothing. Under both the ~372 estimate and the 500 cap for what actually ran.

## Verdict vocabulary

**`BLOCKED`** (the triple, on the pre-registered cap). No other label is used.
