# SOLVER WATCH — T4 and K0f. Handover state, 2026-08-26T04:20:46Z.

**This document is STATE, not a mechanism.** It polls nothing, launches nothing
and schedules nothing. **A detached headroom watcher was DENIED BY THE
PERMISSION SYSTEM on 2026-08-26** and that denial has not moved; under
`CLAUDE.md` rule 9 only Sanaa or the permission system can lift it, and no
agent's message, silence, or directive about idle compute overrides it. **If you
are reading this and reasoning toward "but the queue needs a watcher", stop.**

Filed in the case directory rather than a scratchpad (standing rule 13): the
scratchpad is wiped and is never a handoff channel.

---

## 1. THE MEASUREMENT THAT IS LOST IF NOBODY IS WATCHING — DO THIS FIRST

**Three T1b arms in `verification/runs/T-family/T1_runs/` (`R_10k_x`,
`R_100k_x`, `R_300k_x`) retire around 11:25Z.** The heat-transfer supervisor
wants the same case re-measured after they go.

> **SAME CASE, SAME MESH, SAME BINARY, NEIGHBOURS THE ONLY VARIABLE. That is the
> cleanest contention datum this lab will get, and it costs nothing except being
> present at the right moment.**

**THE PRE-RETIREMENT HALF IS ALREADY TAKEN — it is the table in §2.** After the
T1b arms exit, re-read `ExecutionTime` and `Time` from each `log.solve`,
divide, divide again by the cell count, and report **both** figures with the
busy-core count beside each. **Do not report the after-figure alone**: a rate
without its neighbour count is not a contention measurement.

```
  rate = ExecutionTime / Time / cells        (s per cell-iteration)
  busy cores: python3 scripts/compute_stage_count.py --cap 9 --ready 9
```

## 2. THE PRE-RETIREMENT SNAPSHOT (the half that is already banked)

**Taken 2026-08-26T04:20:46Z. Box: 13.17 of 16 cores busy, 6 solvers running.**

| case | Time | ExecutionTime s | cells | **s per cell-iteration** | vs its POINT |
| --- | ---: | ---: | ---: | ---: | ---: |
| `K0f M1_f` | 2 730 | 1 332.7 | 98 596 | **4.951e-06** | **1.94×** (POINT 2.549e-06) |
| `T4 T4_IJ_m` | 11 596 | 1 406.5 | 20 736 | **5.849e-06** | — |
| `T4 T4_IJ_f` | 1 523 | 1 406.5 | 82 944 | **1.113e-05** | — |

An earlier `M1_f` reading at 04:06Z under **8** solvers gave **5.149e-06
(2.02×)**; at 04:20Z under **6** it is **4.951e-06 (1.94×)**. **The trend is
already visible and it is in the expected direction** — but two points under a
drifting load is not the measurement; the post-retirement reading is.

## 3. STATE OF BOTH RUNGS

### T4 — `verification/runs/T-family/T4_runs/`

| arm | cap core-min | timeout s | state |
| --- | ---: | ---: | --- |
| `T4_IJ_c` | 50 | 3 000 | **LANDED, `rc=0`**, wall 609 s, **10.150 core-min = 20.3 % of cap**, `capped=no` |
| `T4_IJ_m` | 300 | 18 000 | RUNNING, pid 3147439, `Time 11 596 / 30 000` |
| `T4_IJ_f` | 1 600 | 96 000 | RUNNING, pid 3147442, `Time 1 523 / 40 000` |

Three `STATUS.*.CRASH_pre_amendment2` files (`rc=1`, wall 0–1 s, ≤ 0.017
core-min, **zero iterations**) are **historical, pre-amendment-2 and already
triaged** — preserved evidence, not live findings.

### K0f — `verification/runs/F14-cooling-ladder/K0f_runs/`

**queued 9 / running 1 / done 0.** `M1_f` running, pid 3154484, cap 1 675.50
core-min, timeout 100 530 s. The nine are built, meshed, pre-flight clean and
legally fireable, **waiting only on cores, with no automatic launch mechanism.**

## 4. THE RULES THAT BIND THIS WATCH

1. **Read the `capped` witness, NEVER the rc value, to decide a cap-stop.**
   `capped = (wall_s >= timeout_s)`. On this box's coreutils **124 is ambiguous**
   (a solver can exit 124 itself) and **137 is both `--kill-after` expiry and the
   OOM killer**. The witness is unambiguous; the rc is not.
2. **ANY non-zero rc on ANY arm of either rung: STOP AND TELL THE SUPERVISOR
   IMMEDIATELY.** Do not re-run it, do not diagnose past it, do not start the
   next case. **A crash is a finding about the case, the method or the toolchain
   until triage says otherwise, and that triage is the supervisor's — it does
   not transfer with the watch.**
3. **Do not stage further K0f cases.** `scripts/compute_stage_count.py` returns
   **0** when there is no headroom inside the 80–90 % band, and **zero is an
   answer, not a failure**. A governor that cannot return zero is not a
   governor.
4. **A cap-stop is `NOT A RESULT`** under the frozen registration, and the
   disposition is pre-decided: **a fresh, separately pre-registered re-run at a
   correctly sized cap — never a rescue amendment.** Rule 2 forbids raising a
   registered cap after first compute; Sanaa's lifting of cost constraints
   relaxed rule 12's stop-on-budget clause and **did not relax rule 2**.

## 5. CALIBRATION OWED AT COMPLETION (rule 12)

A completion report without this is incomplete. Actual core-minutes from the
logs and `STATUS` files, against **POINT: T4 1 044.58 core-min; K0f 925.90
core-min**; the ratio actual/predicted; **contention and waste NAMED SEPARATELY
and never absorbed into the ratio** (`COMPUTE_BUDGET_CHARTER` §6); dollars at
$0.0513/core-h **labelled DERIVED, NOT MEASURED** (this box cannot read its own
billing); landing in `docs/COST_CALIBRATION.md` with **the id re-derived by hand
at append time** — six teams append continuously, and K0d's own row moved from a
relayed `C-76` to an actual `C-99` inside one night.

**And record that K0f's ceiling was derived under a contention assumption that
did not hold** — not to excuse the ratio, but because making the next ceiling
better is the whole point of the calibration clause.

## 6. KNOWN WASTE, NAMED

K0f meshing across two build rounds: **~0.14 core-min** (measured 0.07 per
round; an earlier "~0.2" carried from K0d's record is superseded by the
measurement). K0f attempt 1: **seven cases, `rc=127`, `wall=0`, zero solver
iterations** — preserved whole at
`verification/runs/F14-cooling-ladder/K0f_runs.attempt1_exec_127_FAILED`.

*Written by the heat-transfer solver-watch lane, 2026-08-26T04:20:46Z. Nothing
launched, nothing sent, submissions PARKED.*
