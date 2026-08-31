# T22_CHTb_L1 — LAUNCH 1 DIED BEFORE THE SOLVER. TRIAGE EVIDENCE, NOT A TRIAGE VERDICT.

**A crash is a finding until triage says otherwise, and triage is the
supervisor's own non-delegable check (`SUPERVISION_CHARTER.md` §3). This lane
DIAGNOSED and did NOT repair, did NOT delete anything, and did NOT relaunch.**
What follows is the evidence the supervisor's triage needs, and nothing more.

## What happened, MEASURED

| fact | value | artifact |
| --- | --- | --- |
| launched | 2026-08-31T16:35:11Z, pid 140701, ranks 1, `prereg=FEASIBIL` | `verification/queue/runner.log` |
| died | 2026-08-31T16:35:11Z — **the same second** | `T22_CHTb_L1/STATUS.T22_CHTb_L1` |
| status written | `launcher_rc=1` — the **queue runner's fallback** STATUS, not `run_t22.sh`'s own block | same file |
| `log.solve` | **absent** — the solver line never executed | case directory |
| `launcher.queue.out` | **0 bytes** — the failure printed nothing | case directory |
| `0/` | **created** (the `cp -r 0.orig 0` succeeded) — so the script died *after* the age guard and *before* the solver | case directory |
| compute consumed | **≈ 0.0 core-min** against a 15.4 core-min estimate. Nothing was computed. | wall < 1 s at 1 rank |

The verdict vocabulary does not apply: this rung is UNREGISTERED and gradeable
as nothing (`T22_FEASIBILITY_NOTE.md`). **The ONE QUESTION IS STILL
UNANSWERED** — the solver never started, so nothing was learned about whether
`chtMultiRegionSimpleFoam` advances a three-region wedge.

## Cause, REPRODUCED WITH A TWO-ARMED CONTROL

`run_t22.sh` sets `set -u` at line 17 and sources the OpenFOAM environment at
line 44 with `set -u` **still in force**. Under `set -u`, that source aborts the
shell:

```
/usr/lib/openfoam/openfoam2606/etc/bashrc: line 184: WM_PROJECT_DIR: unbound variable
```

Reproduced outside the case, both arms, in a scratch shell:

- **ARM A** — `set -u`, then source: **rc 1**, and the `echo` on the line after
  the source **never printed**. The shell died inside the source.
- **ARM B (control)** — same source, no `set -u`: **rc 0**, the echo printed,
  and `command -v chtMultiRegionSimpleFoam` resolved to the real binary.

The arms differ in exactly one thing. And `run_t22.sh:44` carries
`>/dev/null 2>&1` on the source, which is what swallowed the `unbound variable`
message and left `launcher.queue.out` empty — **the redirect is why the failure
was silent, and the silence is the worse half of the defect.**

## THIS IS A REGRESSION AGAINST A FIX THE LAB ALREADY MADE

`verification/runs/T-family/T20_runs/run_one_t20.sh` — which launched five T20
cases clean today — already carries the guard, and says so at its own line 31
(*"the OpenFOAM bashrc is sourced with `set -u` lifted"*). Its lines 130–137
do three things `run_t22.sh` does none of:

1. `set +u` before the source, `set -u` after it;
2. `|| true` on the source itself;
3. a **post-source `command -v "$SOLVER"` check that REFUSES with a legible
   message** if the solver did not resolve — added, per its own comment, after
   *"K0f attempt 1: rc=127 x7"*.

**Scope of the regression, SWEPT WITH BOTH CONTROLS.** 150 shell scripts under
`verification/runs/`, `cases/`, `scripts/` and `models/` that mention the
OpenFOAM bashrc were scanned for `set -u` in force *at* the source line with no
`set +u` lifting it. **Exactly one file matched: `run_t22.sh`.** The positive
control (`run_t22.sh`, known defective) appeared; the negative control
(`run_one_t20.sh`, known guarded) did not. A first, cruder sweep keyed on a
literal `etc/bashrc` on the source line returned a **clean zero that was
false** — it could not see `. "$FOAM_BASHRC"` and so could not see the one
defect that exists. That zero was discarded, not reported. **This is an
isolated defect in T22's own launcher, not a lab-wide condition.**

## What the supervisor's triage must decide, and what stands in the way

1. **The repair** is two lines plus a check, copied from `run_one_t20.sh`:
   `set +u` / source / `set -u`, and a post-source `command -v` refusal so a
   future environment failure is loud instead of silent. Legal here without an
   amendment because **T22 is unregistered and no gate, threshold, band, cap or
   label exists to be moved** — but it is a change to what runs, and it is the
   supervisor's call, not this lane's.
2. **The cwd is now dirtied.** `0/` exists, so both `run_t22.sh`'s own age guard
   and `queue_entry_check.py`'s AGE-GUARD will refuse a relaunch until it is
   cleared. **It has been left exactly as the dead launcher left it.** It holds
   copies of `0.orig` and no answer — a solve never ran (`log.solve` absent) —
   but removing it is a deletion inside a run tree after a launch, and this lane
   does not take that decision.
3. **T22 is idle again** and no longer queued: the runner consumed the entry and
   moved it to `verification/queue/heat-transfer/launched/T22_CHTb_L1.json`. A
   relaunch needs a fresh entry after 1 and 2.

## What was NOT verified

Whether `chtMultiRegionSimpleFoam` will actually run this case once the launcher
is fixed. Nothing here bears on that; the solver has still never started, and
the 15.4 core-min estimate remains **DERIVED, never MEASURED, for this case.**
