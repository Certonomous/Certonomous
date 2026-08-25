# HARD BLOCKER — `f9_criteria.py` MUST NOT BE EXECUTED AGAIN until its schema defect is repaired

**Raised 2026-08-25, cfd. Ruling: cfd-supervisor. Status: BLOCKER IN FORCE.**
**Found by `scripts/check_grader_self_blindness.py` (Probe A), not by reading.**

## The defect — L-322's shape, TWICE in one file

| container | written at | divergent key | read at |
| --- | --- | --- | --- |
| `out["stationarity"]` | **L604, L608** | `status` | **L816, L826** |
| `out["cycle_convergence"]` | **L644, L648** | `status` | **L816, L826** |

In both cases one construction branch omits `status` while the consumer reads it
unconditionally. **A branch that takes the short schema raises `KeyError: 'status'`** — the
same defect that killed the F3 conversion grade on 2026-08-25.

**`status` is a verdict-adjacent key**, which makes this worth blocking rather than noting:
the branch that omits it is the one least likely to have been exercised, and most likely to
be taken on an unusual run.

## What this does and does NOT mean

**It is ARMED, not fired.** **An armed latent crash is NOT evidence that anything already
graded is wrong.** It means a future execution taking the short branch **raises instead of
grading**. The existing F9 records — `f9_criteria.json`, `f9_analysis.json`,
`beta_boundary_results.json` — are **not reopened, not re-audited and not called into
question by this blocker.**

## What this blocker requires

1. **Do not execute `f9_criteria.py` again** in its current state.
2. **The next F9 registration must carry the fix as a MANDATORY PRE-COMPUTE item**, and it
   must be **structural**: **one constructor, one schema**, for **both** containers — not a
   `status` key added to each short branch, which leaves the next divergent key waiting.
3. **The same rule applies to every `ledger`/`report` accumulator** in that registration.
4. **No repair here. No §2d event. No triage of the graded records.**

**Reference:** `docs/LESSONS.md` L-322; `docs/CFD_GRADER_SELF_BLINDNESS_SWEEP_2026-08-25.md`.
