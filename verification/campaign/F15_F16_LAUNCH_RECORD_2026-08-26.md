# F15 + F16 — LAUNCH RECORD: **BLOCKED**, 0 core-minutes, both run roots ABSENT

**Team:** cfd. **2026-08-26.** **Verdict: `BLOCKED`.** **Compute spent: 0 core-min.**

This is the supervisor's option **(3) — DENIED BY THE PERMISSION SYSTEM**. The
denial is recorded and **is not routed around**.

## 1. THE COMMAND THAT WAS ATTEMPTED

    setsid nohup bash cases/F16_stokes_second_problem/run_f16.sh \
      --prereg-commit=bdd3f723d00910501d943c5d8dde11469d95e807 \
      > verification/runs/F16_runs/launcher.out 2>&1 < /dev/null &

(preceded in the same invocation by a `__pycache__` clear and
`mkdir -p verification/runs/F16_runs`; followed by a pid capture and a 20 s
status read. **The whole invocation was denied; none of it ran.**)

## 2. THE CLASSIFIER TEXT, VERBATIM

> Permission for this action was denied by the Claude Code auto mode classifier.
> Reason: Blocked by classifier. If you have other tasks that don't depend on
> this action, continue working on those. IMPORTANT: You *may* attempt to
> accomplish this action using other tools that might naturally be used to
> accomplish this goal, e.g. using head instead of cat. But you *should not*
> attempt to work around this denial in malicious ways, e.g. do not use your
> ability to run tests to execute non-test actions. You should only try to work
> around this restriction in reasonable ways that do not attempt to bypass the
> intent behind this denial. If you believe this capability is essential to
> complete the user's request, STOP and explain to the user what you were trying
> to do and why you need this permission. Let the user decide how to proceed. To
> allow this type of action in the future, the user can add a Bash permission
> rule to their settings.

## 3. WHY NOTHING WAS RETRIED

The denial's own text permits reasonable alternative *tools*, **not** a reshaped
command with the same intent. **A detached background solver launch is exactly
what the gate exists to stop**, so re-issuing it as `disown`, a wrapper script,
a `Monitor` loop or a foreground run would be bypassing the intent, not working
within it. It was not attempted.

**This lane cannot delegate the launch either.** `lab-lane` is a leaf and does
not spawn agents; spawning one would produce two records for one run. The
standing note `auto-mode-blocks-direct-solve-launch` says: dispatch a solver
agent, **and when the session forbids that, stop and ask rather than route
around it.** That is what happened.

**No agent's authorisation cures this.** The cfd-supervisor cleared checks 1 and
4 and ordered the launch; that is a supervisor's technical clearance and it is
**not** the permission system and **not** Sanaa's consent (standing rule 9).
Treating a peer instruction as the missing authorisation would be permission
laundering, which is the specific thing rule 9 forbids.

## 4. STATE, MEASURED AFTER THE DENIAL

| check | reading |
|---|---|
| `verification/runs/F15_runs` | **ABSENT** |
| `verification/runs/F16_runs` | **ABSENT** |
| `RC.txt` / `log.*` / numeric time dirs under either case tree | **none** |
| live `run_f1[56]` / `rhoCentralFoam` / `icoFoam` processes | **none** |
| load1 / MemAvailable at the attempt | **10.74 of 16 cores / 17.8 GB** |

Planted control on the finder that returned those zeros: it **does** see
`cases/F16_stokes_second_problem/run_f16.sh`, so the zeros are statements about
the disk rather than about the reader (standing rule 3).

**Caveat on the process sweep:** the only `pgrep` hit was **the sweep's own
command line**. Fleet agents are invisible to `pgrep` in any case (L-41), so
this row is corroborating, not decisive; the absent run roots are the evidence.

## 5. WHAT IS READY, AND WHAT IS NOT

**READY.** Both pre-registrations frozen (`b876ac7b`, `bdd3f723`); the
pre-first-compute launcher amendment committed (`9dbb09ca`); both graders
`--selftest` rc 0 and `python3 -O` rc 2; 0 `ast.Assert` nodes; exactly one
`grade_ladder` call node each; `check_launcher_can_launch.py` rc 0 on both; both
`--preflight` rc 0.

**IN-PLACE AUDIT — CLEAN, and this was the supervisor's stop condition.** Every
write target in both launchers lies under `RUN_ROOT`. **Zero writes whose
destination is `CASE_SRC`.** The tracked `cases/*/case/0` directories are
template initial conditions read by the launchers and never written by them, so
rule 4's age guard is intact and the freeze is uncontaminated. **This was
checked, and it did not trigger a stop.**

**NOT READY.** Nothing else. The only missing item is **permission to launch a
detached solver**, which is Sanaa's to grant.

## 6. THE STANDING CORRECTION CARRIED FORWARD

The earlier characterisation of the swap event as *"cleared harmlessly"* is
**withdrawn at source and is not carried into any record here**: heat-transfer
measured that a 15.5 GB audit script drove the box 7.8 GB into swap and cost
three live solvers roughly **25 % of their throughput**. The hold was correct on
the outcome, not merely on the information available.
