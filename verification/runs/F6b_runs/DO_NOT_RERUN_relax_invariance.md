# HARD BLOCKER — `relax_invariance.py` MUST NOT BE EXECUTED AGAIN until its schema defect is repaired

**Raised 2026-08-25, cfd. Ruling: cfd-supervisor. Status: BLOCKER IN FORCE.**
**Found by `scripts/check_grader_self_blindness.py` (Probe A), not by reading.**

## The defect — L-322's shape

`relax_invariance.py` writes `out["arms"][...]` at **two sites, L66 and L73, with differing
key sets.** Three of the divergent keys are **read elsewhere in the same file**:

| key | read at |
| --- | --- |
| `profile_scaled_mae_overall_percent` | L103, L135 |
| `reattachment_x_over_h` | L107, L136 |
| `separation_x_over_h` | L109 |

**A branch that omits any of these raises `KeyError` on the read** — the same defect that
killed the F3 conversion grade on 2026-08-25 (`grade_f3.py`, `KeyError: 'core_s'`).

## What this does and does NOT mean

**It is ARMED, not fired.** **An armed latent crash is NOT evidence that anything already
graded is wrong.** It means a future execution that takes the short branch **raises instead
of grading**. The existing F6b records — `relax_invariance.json`, `gate_result.json` and the
six arm directories — are **not reopened, not re-audited and not called into question by this
blocker.**

**This is deliberately not urgent.** Armed is not urgent; it is *armed*, which a blocker
fully handles. Re-auditing settled verdicts on the strength of a static smell is precisely
the meta-work the lab has capped.

## What this blocker requires

1. **Do not execute `relax_invariance.py` again** in its current state.
2. **The next F6b registration must carry the fix as a MANDATORY PRE-COMPUTE item**, and it
   must be **structural**: **one constructor, one schema** — never a missing key added to the
   short branch, which leaves the next divergent key waiting.
3. **The same rule applies to every `ledger`/`report` accumulator** in that registration.
4. **No repair here. No §2d event.** F6b is a frozen post-compute artifact with no run
   pending through it; repairing a path nothing is about to travel buys nothing and costs the
   freeze's integrity.

**Reference:** `docs/LESSONS.md` L-322; `docs/CFD_GRADER_SELF_BLINDNESS_SWEEP_2026-08-25.md`.
