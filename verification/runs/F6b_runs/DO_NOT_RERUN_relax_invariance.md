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

---

## AMENDMENT 1 — 2026-08-25 — **BLOCKER STANDS. THE STATED DEFECT IS CORRECTED.**

**Ruling: cfd-supervisor, personally. `[lab-attributed]`, overrulable.**
**Lines whose number changed above this section: 0.** The original text above is preserved
exactly as raised, not rewritten (standing rule 6).

**Status: `BLOCKER IN FORCE` — UPHELD. But the exposure named above is the WRONG ONE, and a
repair aimed at it would fix nothing.**

**What the table above names as exposed is GUARDED and NOT REACHABLE.** The short branch (L66)
writes `{"case": ..., "state": "NO WRITTEN TIME"}`, which carries no `converged` key, and the
consumer guards with `.get()`:

| line | guard | effect on the short branch |
| --- | --- | --- |
| L92 | `if not r.get("converged"):` | `None` → `not None` → **True** → INCONCLUSIVE, reads nothing |
| L96 | `elif not r.get("steady_bubble"):` | INCONCLUSIVE, reads nothing |
| L101 | `else:` | the `r[...]` subscripts live here, and the short branch never arrives |

**Arms B and C are safe.** `profile_scaled_mae_overall_percent`, `reattachment_x_over_h` and
`separation_x_over_h` read off `r` cannot raise.

**THE REAL EXPOSURE IS THE INCUMBENT ARM `A`, AND THE SWEEP DID NOT NAME IT.** At L87,
`A = out["arms"]["A"]`, and `A` is then subscripted **unguarded** at **five** sites — L102,
L103, L107, L109 and L135. **If arm A itself takes the short branch, every one raises
`KeyError`**, with no `.get()` in between.

**Two independent reach routes, and the second does not involve arms B or C at all:**

1. Arm A short-branches **and** B or C converged with a steady bubble → the `else` at L101
   executes → raise at L102.
2. Arm A short-branches **and** `medium_relax_PC` exists with exactly two crossings → raise at
   L135. **Reached even if B and C both short-branch**, because L129–L135 is a separate loop
   with its own condition.

**The repair is on the `A[...]` reads, not the `r[...]` reads.** The `r[...]` reads are already
correct and are the pattern the `A[...]` reads should adopt. **A repair that hardens `r[...]`
and leaves `A[...]` alone leaves this file exactly as armed as it is today.**

The existing F6b records are **not** reopened by this amendment. Full reasoning:
`docs/CFD_LATENT_CRASH_TRIAGE_2026-08-25.md` §2 and §3.
