# F4 conversion — LANE STATE, 2026-08-25

**Committed because direct messaging to `cfd-supervisor` is failing** ("no agent
named cfd-supervisor is reachable"), and the supervisor's standing instruction is
that committed files are how this lane is actually read. **This is a state note,
not a record of any result.**

## Position

| item | state |
|---|---|
| **Compute spent by this lane** | **0 core-minutes.** No solver launched, no mesh built, no case directory created. |
| Run root `conversion_2026-08-25/runs/` | **ABSENT** (rule-2 condition holds) |
| `grade_f4.py` | **REPAIRED and committed** — `ae296f69`, blob `f5196143`, sha256 `55636d92…`, `--selftest` 27/27 |
| Superseded grader blob | `48d4a479` (`ad6f2f6b`) — carried the §7 completion defect, **must never be pinned** |
| `F4_CONVERSION_PREREGISTRATION.md` | **DRAFTED, 736 lines, DELIBERATELY UNCOMMITTED. The pin is UNFROZEN.** |
| `rerun_f4.py` (launcher) | **DOES NOT EXIST** — this lane's own disclosure, not a supervisor find |
| Verdict issued | **none** |

## Waiting on

**A second check-1 diff read of the repaired grader**, per the supervisor's
sequence. The repair is `ae296f69`, **+167/−8**, deliberately small enough to
read quickly. The pre-registration is not committed and **rule 2's pin is not
frozen**, because freezing a pin on an instrument still under review would
freeze whatever the review finds.

## What the repair was

The first draft registered `t_last ≥ endTime`. **It would have refused four of
the nine runs this conversion exists to re-derive** — M6/coarse `5.9998543386`,
M7/fine `5.9999993531`, M8/coarse `5.99979092006`, M8/fine `5.999927519`, all
complete, all landing below 6.0 because `adjustTimeStep yes` sizes the final step
from `maxCo` and stops on the first step that would pass the end.

**4 of 9, scattered, no pattern in Mach number and none in refinement** — under
rule 4 those rows become `NOT A RESULT`, and the conversion would have reported
that roughly half of F4's ladder failed to complete. **A false finding with a
plausible shape, on a case whose entire purpose is to make two 2026-07-28 `PASS`
verdicts defensible.** Caught by the supervisor's check-1 read
(`CFD_CHECK1_FINDING_2026-08-25_GRADE_F4.md`, `780e49d8`) **before a core-minute
was spent**; confirmed by this lane from the logs rather than from the report.

Registered instead: **`t_last + Δt_final > endTime`**, with `Δt_final` read from
the run's own last two `Time =` lines — a derivation, not a tolerance. **A
two-sided `|t_last − endTime| ≤ ε` was refused as the repair** and is named in
the pre-registration so it cannot be reintroduced.

**Control C1 was added, and it matters more than the fix.** P1/P2/P3 all test the
*readers*; nothing exercised the completion path against a real landing time,
which is how the defect survived a 21-check selftest. C1 requires the checker to
**accept** a landing under `endTime` by 0.4·Δt and **refuse** one by 3·Δt, runs
in `grade_all()` before any case is graded, and is mutation-tested against a stub
that never refuses.

## Findings against the 2026-07-28 record, now three

1. **Gate 1 was graded `PASS` over a non-monotone triple** that standing rule 5
   forbids grading, with the caveat carried as prose.
2. **Gate 2 was graded `PASS` against no threshold at all** — the Summary's
   Deviation cell for Gate 2 is literally `—`.
3. **No return code was ever recorded.** There is no `RC.txt` anywhere in the
   2026-07-28 tree; completion rests on the runner's own
   `solver_completed_to_endTime` field — the runner's judgment of its own
   success. Found while verifying the §7 repair end to end.

## Not touched

The empty untracked `verification/runs/F4_runs/conversion_2026-08-24/` was
**inspected and NOT removed**. The 2026-07-28 production tree was **never
written to**: the end-to-end verification ran on read-only replicas staged
outside the repository and deleted afterwards, and `grade_all()` refuses any root
outside a `conversion_*` directory precisely because control P2 mutates the case
it grades.

**Nothing sent, filed, uploaded, registered, posted or commented (rule 7).**
