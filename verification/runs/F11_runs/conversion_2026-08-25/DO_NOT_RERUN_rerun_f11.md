# HARD BLOCKER — `rerun_f11.py` MUST NOT BE EXECUTED AGAIN until its schema defect is repaired

**Raised 2026-08-25, cfd. Ruling: cfd-supervisor. Status: BLOCKER IN FORCE.**

## The defect

`rerun_f11.py` writes `ledger["runs"][key]` at **three sites — L953, L964, L1021 — with
differing key sets.** Four of the divergent keys are **read elsewhere**:

| key | read at |
| --- | --- |
| `cost_basis` | L571 |
| `predicted_core_s` | L572 |
| `ranks` | L573 |
| `wall_cap_s` | L574 |

**A branch that omits any of these raises `KeyError` on the read.** This is exactly the
defect that killed the F3 conversion grade the same day — `grade_f3.py` died on
`KeyError: 'core_s'` because its `PENDING` branch omitted a key the summary read
unconditionally.

## Why it is a blocker and not a repair

**F11 is graded and closed** (`RESULTS.md`, verdict `NOT A RESULT` on all six gate rows;
calibration row **C-64**). No run is pending through this launcher, and it is a **frozen
post-compute artifact** cleared at supervisor check 1.

**Opening a §2d event to repair a path nothing is about to travel buys nothing and costs the
freeze's integrity.** So the defect is **registered and blocked**, not patched.

## What this blocker requires

1. **Do not execute `rerun_f11.py` again** in its current state. It has an armed latent crash
   on any run where a branch takes the short schema.
2. **The next F11 registration must carry the fix as a MANDATORY PRE-COMPUTE item**, and it
   must be **structural**: **one constructor, one schema** — not a missing key added to the
   short branch. Two construction sites that can drift apart is the defect; patching the
   symptom leaves the next divergent key waiting.
3. **The same rule applies to every `ledger`/`report` accumulator** in the next registration,
   not only to this one.

## Provenance — and why it argues for shipping a lesson WITH its check

This is the **third instance of L-322's shape found in a single day**, and **the first found
by an instrument rather than by reading**:

| # | artifact | how found |
| --- | --- | --- |
| 1 | `analyse_f5b_physics.py` (L-321 shape) | by eye, after it cost a 39.4 core-min solve its verdict |
| 2 | `grade_f3.py` (L-322 shape) | by eye, after it crashed on a completed run |
| 3 | **`rerun_f11.py`** | **by `scripts/check_grader_self_blindness.py`, within an hour of the tool existing** |

**Two found by eye at the cost of two graded runs; one found by a tool before it cost
anything.** That is the argument for shipping a lesson with its executable check rather than
the lesson alone.

**Reference:** `docs/LESSONS.md` L-321, L-322; `scripts/check_grader_self_blindness.py`
(Probe A).
