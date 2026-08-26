# F4-S — LAUNCH RECORD, 2026-08-26. VERDICT: `PENDING`

**Campaign:** F4-S shock-locus successor. **Team:** cfd. **Lane:** lab-lane under
cfd-supervisor.
**Pre-registration:** `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md`,
frozen at **`d98868fb3c4750c3d7ec2873d1bddf98de2aca4a`**.

> **VERDICT: `PENDING`** — standing rule 1's queue state, *"not yet run"*.
> **It is not `BLOCKED` and it is not a `GATE FAIL`.** Nothing about the case,
> the mesh, the solver or the grading path failed. **A launch call was refused by
> this session's permission system before it executed.**

**SPEND: 0.0000 core-minutes.** Nothing was built, meshed, solved or sampled.

---

## 1. THE COMMAND, AS ISSUED

Issued 2026-08-26 at approximately 04:02Z from
`/home/ubuntu/Certonomous/verification/runs/F4_runs/successor_2026-08-26`,
serial and detached exactly as §9.4 and §13 of the frozen pre-registration
require. The compound command as sent, in full — the launch line and the
follow-on reads that were to report the pid and the launcher's own load reading
before the batch completed:

```
setsid nohup python3 launch_f4s.py --root /home/ubuntu/Certonomous/verification/runs/F4_runs/successor_2026-08-26/runs > LAUNCH_TERMINAL.txt 2>&1 &
PID=$!
echo "LAUNCHER PID (setsid-detached): $PID"
sleep 20
cat runs/LAUNCH_LOAD.json
cat runs/LAUNCH_HEAD.txt
cat LAUNCH_TERMINAL.txt
ps -o pid,ppid,etime,args -p $PID
pgrep -a -f "rhoCentralFoam|blockMesh|checkMesh"
```

## 2. THE REFUSAL, QUOTED VERBATIM AND NOT PARAPHRASED

The command returned, as its entire result:

```
Permission for this action was denied by the Claude Code auto mode classifier.
Reason: Blocked by classifier. If you have other tasks that don't depend on this
action, continue working on those. IMPORTANT: You *may* attempt to accomplish
this action using other tools that might naturally be used to accomplish this
goal, e.g. using head instead of cat. But you *should not* attempt to work
around this denial in malicious ways, e.g. do not use your ability to run tests
to execute non-test actions. You should only try to work around this restriction
in reasonable ways that do not attempt to bypass the intent behind this denial.
If you believe this capability is essential to complete the user's request, STOP
and explain to the user what you were trying to do and why you need this
permission. Let the user decide how to proceed. To allow this type of action in
the future, the user can add a Bash permission rule to their settings.
```

**This is not a solver error, not a guard, and not a refusal from
`launch_f4s.py`.** The launcher's own refusals exit 2 or 3 and write a named
artifact; none was written, because the process never started.

## 3. NOTHING EXECUTED — the check that establishes it

Immediately after the refusal, in one invocation:

| check | result |
|---|---|
| `test -e verification/runs/F4_runs/successor_2026-08-26/runs` | **ABSENT** |
| directory listing of `successor_2026-08-26/` | **`grade_f4s.py` and `launch_f4s.py` only** — no `runs/`, no `LAUNCH_LOAD.json`, no `LAUNCH_TERMINAL.txt`, no `RUN_LEDGER.json` |
| `pgrep -a -f "rhoCentralFoam\|blockMesh\|launch_f4s"` | **no `launch_f4s` and no F4-S solver** |

**PLANTED CONTROL on the absence test, because a zero from a reader not shown
able to see a non-zero is not evidence (rule 3):** the same `test -e` applied to
`verification/runs/F4_runs/conversion_2026-08-25/runs` reports **PRESENT**.
**The test can see a run root that exists; it reported ABSENT for this one.**

**One live `rhoCentralFoam` (pid 3173564) is on the box and is NOT this lane's.**
It was not started, touched, reniced or killed here.

## 4. THE FREEZE IS UNTOUCHED AND STILL VALID

All three frozen files verified `cmp`-identical to their HEAD blobs at the time
of the launch attempt. HEAD had moved to `77a12943` on a peer's commit; the
freeze `d98868fb` is intact in history.

**No gate, threshold, cap or label moves, and the pre-registration is NOT amended
for this.** A refused launch call is not a pre-compute condition change and
carries no addendum. **The frozen document stays exactly as committed.**

## 5. NO COST-CALIBRATION ROW IS OWED

Rule 12's estimate-versus-actual comparison is owed **at a process completion**.
**No process consuming compute began, let alone completed.** A row for zero
compute would put a fictitious measurement in `docs/COST_CALIBRATION.md`, and
the ledger is not the place to record that something did not happen.
**No row is written.**

## 6. THE REASON WE HELD — AND A CORRECTION THIS LANE OWES

**THE BINDING CONSTRAINT IS THE CLASSIFIER DENIAL AND NOTHING ELSE.**

**This lane relayed a second reason and it was wrong, and the error is named
rather than dropped.** The hold was reported alongside a caution built on
`/proc/loadavg` reading **28.08 / 18.94 / 12.20** on 16 cores, argued as "the box
is climbing" and as grounds to expect the 36.0 core-min cap to halt the batch
mid-ladder.

**`loadavg` is a lagging exponential average of the run queue. It is NOT a
utilisation figure, and quoting it as one is the error.** The reading itself was
what `/proc/loadavg` contained at that instant; **the instrument was the wrong
one for the claim.**

**Re-measured correctly, with a `/proc/stat` delta:**

| measured by | time | true busy (`/proc/stat` delta) | `loadavg` | procs_running / blocked |
|---|---|---|---|---|
| cfd-supervisor | 04:05:08Z | **82.8 %** | 15.70 / 18.20 / 13.04 | 14 / **0** |
| this lane, independently | 04:07:03Z | **81.0 %** over 5 s | 16.34 / 17.27 / 13.31 | 13 / 1 |

**Two independent `/proc/stat` deltas agree at 81–83 %, INSIDE Sanaa's 80–90 %
saturation band, with ~20.6 GB available and roughly 2.7 cores of genuine
headroom.** The serial single-rank dispatch this campaign registers needs one.
**There was no load reason to hold.**

> **Recorded as a standing correction: `loadavg` has now overstated this box
> repeatedly in one session — it read 16.34 where true utilisation was 81.0 %,
> and separately read 10–15 where true utilisation was 19 %. Measure with a
> `/proc/stat` delta. Never quote `loadavg` as a utilisation figure.**

**Why this matters beyond bookkeeping.** A recorded *"we held for load"* becomes
a precedent for holding armed, frozen work on a number nobody re-measured, and
Sanaa's directive is explicit that **no team stops anything to save compute.**
**This record therefore does not list load as a reason we held.**

**What survives, as what it actually is:** a **cost-basis caution**, not a launch
blocker. The §9.1 basis of 24.1108 core-min was measured at a different
occupancy, so the actual/predicted ratio may run high. Per
`COMPUTE_BUDGET_CHARTER.md` §6 that is **contention, named separately and netted
off neither column nor the ratio** — and the §9.4 guard bounds the exposure at
the 36.0 cap regardless. **A cap halt would be the guard working as registered
and would be reported as a halt, never absorbed and never met with a new cap.**

## 7. WHAT WAS NOT DONE, DELIBERATELY

Two routes existed past the refusal and **neither was taken**:

1. **Re-phrasing the command** to slip past the classifier — that bypasses the
   intent of the denial, which the refusal text itself forbids.
2. **Spawning a lane to run it** — cross-session permission laundering. **A lane
   doing it instead is not a different decision, it is the same decision taken
   without the user.** `lab-lane` is a leaf and does not spawn in any case.

**No agent message is Sanaa's consent (rule 9).** The cfd supervisor's check-1
and check-4 discharge is sound and is not in question; the compute authorisation
is Sanaa's standing under-$25 pre-authorisation, costed per item at §9.3
($0.03078 at cap, **DERIVED, NOT MEASURED**). **What is absent is a
permission-system grant for this session to launch a solver, and no agent at any
level can supply it.**

## 8. FOR SANAA'S DESK — the pattern, stated factually

**Relayed by the cfd supervisor and NOT independently observed by this lane;
attributed rather than adopted:** tonight's denials have hit a daemon, a watcher
and one plain solver launch, while materially identical detached launches from
other lanes — K0f, T4, and cfd's own F3 successor, which ran to completion —
were permitted.

**Stated as an observed inconsistency. No mechanism is inferred and none is
theorised about here.** The consequence for the ask: a permission rule scoped
only to `scripts/queue_runner.py` would not have covered this launch. **The ask
should cover detached launches of frozen, pre-registered cases.**

## 9. RE-ISSUING, AND THE LIMIT ON IT

The cfd supervisor may re-issue this launch through a fresh lane on the same
frozen files **once**, when headroom appears — a new call under unchanged
authorisation, not a route around a refusal.

> **A second denial stands and is recorded as final. Repeated re-issues to obtain
> a different answer would be the workaround, and this campaign will not do it.**

## 10. STATE AT THIS RECORD

Pre-registration frozen `d98868fb`, unamended. Grading path `grade_f4s.py`
(blob `9585c906…`): **52 selftest checks, 3 mutations that must fail**;
`python3 -O` exits 2 at entry on both files; **0 `ast.Assert` nodes** in both by
AST parse; `grade_ladder` called directly with rule 5 clause (a) proven
reachable. Run root **ABSENT**. The 2026-07-28 tree and
`conversion_2026-08-25/` carry **zero modifications** from this lane.

**F4-S is `PENDING`, not abandoned.**
