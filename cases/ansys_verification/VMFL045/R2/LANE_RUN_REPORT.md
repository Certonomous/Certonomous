# VMFL045-R2 — opus-4.8 lane RUN REPORT OF RECORD (interim; state and cost only)

**Channel:** lane→supervisor `SendMessage` is one-way (my prior report reached the
chief, not the supervisor). This committed file is the reliable channel. **INTERIM** —
the run is still solving; this records STATE and COST only. **No grading, no verdict,
no tier, no triple** — held (see §5).

**Process-failure correction (chief's, accepted):** after launch I ended a turn saying
I would "wait for the monitor's L3 midpoint event." A watcher dies with the agent that
armed it — that phrasing is the dead-agent tell. I reattached and read state off disk;
I did NOT restart or touch the run. The run itself was unaffected: it is detached under
`setsid` and continued independently.

## 1. Run state (read off disk at 2026-08-25T02:34:09Z)
- **The run is HEALTHY and STILL SOLVING L3.** `rhoCentralFoam` ALIVE, 100% CPU,
  L3 etime ~216s. `COST.txt` ABSENT, `CAP_EXCEEDED.txt` ABSENT,
  `L3_360x304/RUN_RC.txt` ABSENT — L3 not yet finished by the driver.
- **Frozen shas confirmed BY THE RUN at launch** (from `launch.stdout.txt`):
  pre-registration blob `592e872b`, comparator blob `382ff497` (my freeze-fix). The
  run is grading-path-bound to the amended, re-verified comparator.
- **Pre-flight smoke test PASSED** (rc=0, 1 s) on the coarsest mesh — run 1's exact
  failure mode (`Entry 'e' not found`) is GONE; L3's log shows `smoothSolver: Solving
  for e` stepping cleanly, so the `(h|e)` fvSolution fix carries the viscous energy path.

## 2. Per-level results so far (from each level's RUN_RC.txt / launch.stdout.txt)
| level | cells | rc | wall s | core-min | gateZone | gateZoneInner |
|---|---|---|---|---|---|---|
| L1_90x76 | 6 840 | 0 | 22 | 0.3667 | 252 | 148 |
| L2_180x152 | 27 360 | 0 | 160 | 2.6667 | 1 005 | 590 |
| L3_360x304 | 109 440 | (in flight) | — | — | 4 025 | 2 358 |

Both frozen sampling zones are non-empty at every level (guard 3 satisfied).

## 3. Cost so far (measured from logs; serial, RANKS=1)
- L1 + L2 = **3.0334 core-min** measured. L3 accumulating.
- Cap **48 core-min** (serial timeout 2880 s); pre-registered point estimate **20.4**.
- L3 projection from L2's per-cell/timestep scaling: order ~20 core-min, total ~24
  core-min — a PROJECTION, not a measurement; the real figure lands in `COST.txt`.
- **Estimate-vs-actual calibration (rule 12) will be computed at completion**, not now.

## 4. Contention — what else was on the box (supervisor's directive)
- **SAMPLE 1 (at launch)** and **SAMPLE 2 (during L3, EARLY — explicitly NOT the
  midpoint)** are on disk in `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL045/R2/CONTENTION.txt`. A peer ansys-verification
  job, **VMFL003**, was and is running concurrently (deliberately); load ~3.0 on 16
  cores — LIGHT.
- **The mid-L3 sample I was to take on a monitor event was NOT written before my turn
  ended** (the monitor emits events; it does not write samples). Rather than
  reconstruct it from a now-reading, I launched a **detached `setsid` watcher** that
  writes the genuine **SAMPLE 3 (mid-L3, on L3's first field write)** and **SAMPLE 4
  (end)** to `CONTENTION.txt` itself — independent of my agent. If mid-L3 is ever
  missed it will be recorded as **missing**, not filled.

## 5. Strict completion and grading — HELD
- **Strict completion rule: N/A yet** — the run is not complete. At completion I will
  report, without concluding, which of {rc=0; an `End` line; last time == endTime;
  fields present; `ExecutionTime` count == endTime; every field newer than the level's
  own `0/`} hold at each level.
- **Grading conflict, surfaced not resolved:** my supervisor authorised me to grade
  with the frozen comparator and produce the records. The chief (global supervisor)
  then instructed **grade nothing; the verdict, tier and triple are the supervisor's**.
  These are two agent instructions, and no agent message is Sanaa's consent. I am
  holding to the **conservative** instruction: **I have run no comparator and issued no
  verdict.** The comparator is frozen and ready; grading awaits a single, unconflicted
  authorisation.

## 6. Robustness in place
- Run detached under `setsid` (survives my agent).
- Detached contention watcher writes mid-L3 + end samples to disk (survives my agent).
- A single completion waiter will wake me once the run reaches a terminal state.
- Nothing in the run directory was cleared or touched on reattach.
