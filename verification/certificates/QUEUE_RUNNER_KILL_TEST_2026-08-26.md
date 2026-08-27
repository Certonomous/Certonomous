# CERTIFICATE — QUEUE RUNNER KILL-RESTART TEST, 2026-08-26

**Written 2026-08-26T20:57:41Z by a cfd lab-lane for the cfd supervisor. Stamp from `date -u`.** Sanaa's
criterion (`3c3ef86c`): the queue runner is *"certified to work even when fleets die"*. The
test criterion fixed before the kill: **restart within 120 s, launched solver unaffected.**
Permission: `kill` of the runner pid was DENIED by the classifier at the supervisor's 17:46Z
attempt (quoted verbatim in `docs/LAB_STATE.md`, cfd section); the rule now allows it and the
command below ran without a denial.

## VERDICT: **PASS**

- Restart latency **26 s** (criterion 120 s): kill at **20:53:36Z**, cron wrapper's restart
  line at **20:54:01Z**; polling granularity 5 s, so the true figure lies in [21 s, 26 s].
- Launched solver unaffected: F18b's `icoFoam` **pid 359655 alive before and after** (elapsed
  01:44:43 → 01:47:51 across the test), its wrapper **pid 315474 alive** (PPID 1, SID 315474),
  its log `verification/runs/F18b_runs/fine/log.icoFoam` **grew 113,556 → 115,218 bytes** during
  the test (last `Time = 0.17125`); no overrun file appeared for F18b.

## What was done (one shell invocation each; commands as prose)

1. Recorded `date -u`, the pid from `verification/queue/runner.pid`, and its PPID/SID/elapsed
   via `ps -o pid,ppid,sid,etime,cmd -p <pid>`: **old runner pid 399517, PPID 1, SID 399517,
   elapsed 05:35** at 20:53:36Z. (That pid was itself a cron restart at 20:48:01Z — see
   "prior evidence" below; it was running HEAD `e73740cb`, i.e. the pre-fix code.)
2. Ran `kill 399517` ONCE (rc 0). One second later `kill -0` reported the process gone.
   Confirmed by `ps` that 315474 (wrapper) and 359655 (icoFoam) survived — launched
   solvers are in their own sessions (`setsid`), so the runner's death does not reach them.
3. Polled `verification/queue/runner.restarts.log` every 5 s (150 s ceiling) for a new line.
   New line at the 26-s poll: `2026-08-26T20:54:01Z queue_runner.sh: (re)started runner pid
   419529`. `runner.pid` then read 419529.
4. `ps` on the new pid: **419529, PPID 1, SID 419529**, `python3
   /home/ubuntu/Certonomous/scripts/queue_runner.py --daemon`.
5. Confirmed the new runner runs the NEW code (Task 2, commit `117bf190`, landed 20:52Z): its
   START line reads `HEAD=53fb4b19` (a descendant of `117bf190`); `scripts/queue_runner.py`
   mtime 20:51:32Z precedes the process start 20:54:01Z; and its first log line after START is
   `ESTIMATE-OVERRUN reported for T5_C -> …/T5_CUBE_c/ESTIMATE_OVERRUN.txt` — an event word that
   exists only in the new code.
6. Waited for three tick lines under the new pid in `verification/queue/runner.log`:
   - `2026-08-26T20:54:06Z box busy=83.4% (~13.3/16 cores) MemAvailable=24.0 GB; 6 entries queued`
     → `LAUNCHED team=heat-transfer case=T5_C pid=419636 sid=419636 ranks=1 est=45.6 core-min prereg=299296a2`
   - `2026-08-26T20:55:11Z box busy=76.8% (~12.3/16 cores) MemAvailable=26.4 GB; 5 entries queued`
     → `LAUNCHED team=heat-transfer case=T5_H_c pid=421111 sid=421111 ranks=1 est=45.6 core-min`
   - `2026-08-26T20:56:16Z box busy=100.0% (~16.0/16 cores) MemAvailable=26.2 GB; 7 entries queued`
     → `HELD T5_M_v2.json: busy 100.0% >= ceiling 85.0%`
   The restarted runner is not merely alive: it launched two heat-transfer entries and held a
   third at the ceiling, with no agent attached to any step.
7. Re-checked F18b (item above): same pid, log growing.

## Crontab as installed (`crontab -l`, user `ubuntu`)

    @reboot sleep 30 && /home/ubuntu/Certonomous/scripts/demo_servers.sh
    @reboot /bin/bash /home/ubuntu/Certonomous/scripts/queue_runner.sh
    * * * * * /bin/bash /home/ubuntu/Certonomous/scripts/queue_runner.sh

`scripts/queue_runner.sh` exits 0 if the pidfile's process answers `kill -0`; otherwise it
starts `setsid nohup python3 scripts/queue_runner.py --daemon` and appends one line to
`verification/queue/runner.restarts.log`. Idempotent: the runner's own pidfile lock refuses a
second copy.

## Prior evidence from the board (before this test)

- `verification/queue/runner.restarts.log:1` — `2026-08-26T16:41:57Z queue_runner.sh:
  (re)started runner pid 189825`: the cron wrapper, not an agent, started the daemon that ran
  through the afternoon (cfd supervisor's ninth and twelfth board writes).
- `verification/queue/runner.restarts.log:2` — `2026-08-26T20:48:01Z queue_runner.sh:
  (re)started runner pid 399517`: a second unattended restart, found already on the log when
  this lane began (not performed by this lane; the death of 189825 is not explained by any
  record this lane read).
- F19_SOD: entry filed 17:33:06Z → `LAUNCHED … pid=292839` 17:34:02Z → `STATUS.F19_SOD`
  17:34:20Z, no agent attached to any step (twelfth board write).
- F18b_TG2D_EXT: filed 17:44:13Z → `LAUNCHED pid=315473` 17:44:53Z, no agent attached; that
  is the solver this test showed surviving the kill.
- F20_ISENTROPIC_VORTEX: runner-launched 17:51:23Z, all three levels complete 19:01:23Z,
  graded PASS ×2 (`ca6a3164`).

## Measured numbers, one table

| item | value | artifact |
|---|---|---|
| old runner pid / PPID / SID / elapsed | 399517 / 1 / 399517 / 05:35 | `ps` at 20:53:36Z |
| kill time | 2026-08-26T20:53:36Z, `kill` rc 0 | shell |
| restart line | `2026-08-26T20:54:01Z … pid 419529` | `verification/queue/runner.restarts.log:3` |
| new pid / PPID / SID | 419529 / 1 / 419529 | `ps`; `runner.log` START line |
| restart latency | 26 s (poll granularity 5 s; wall 25 s by timestamps) | above |
| new code | START `HEAD=53fb4b19`; `ESTIMATE-OVERRUN` word present | `verification/queue/runner.log` |
| tick lines under new pid | 3 (20:54:06Z, 20:55:11Z, 20:56:16Z) | `verification/queue/runner.log` |
| F18b wrapper / solver pids | 315474 / 359655, alive before and after | `ps` |
| F18b log growth during test | +1,662 bytes; last `Time = 0.17125` | `verification/runs/F18b_runs/fine/log.icoFoam` |

## Side observation, for heat-transfer (not part of the verdict)

`verification/runs/T-family/T5_runs/T5_CUBE_c/` carries both `CAP_OVERRUN.txt` (20:52Z, old
code, 1.10 × estimate) and `ESTIMATE_OVERRUN.txt` (20:54:01Z, new code). **Both refer to the
STALE launched record `verification/queue/heat-transfer/launched/T5_C.json` (launched
17:41:37Z, pid 310364, no STATUS ever written), not to the 20:54:06Z relaunch of the same
case_id and cwd as `T5_C_v2.json`.** A launched record that never writes STATUS is watched
forever; that is the runner working as specified on a record its owning team may wish to
retire. Infrastructure records only (L-342).

Nothing in this test was sent, filed or uploaded (rule 7). No process other than the runner
pid was signalled.

---

# SECOND KILL — 2026-08-26T22:16:42Z, on the re-armed-cwd fix (`257d1116`)

**Written 2026-08-26T22:20Z by a cfd lab-lane for the cfd supervisor; stamps from `date -u`.**
Criterion fixed before the kill: **restart within 120 s, `EXIT` line present, launched solvers
unaffected, new code loaded.** The first kill above is not rewritten. `kill` (SIGTERM, once) of
the runner pid ran without a classifier denial.

## VERDICT: **PASS** (all four clauses)

| clause | measured | artifact |
|---|---|---|
| restart within 120 s | kill **22:16:42Z** → restart line **22:17:01Z**: **19 s** by timestamps (poll granularity 5 s, seen at the 20-s poll, ≤ 23 s from the kill stamp) | `verification/queue/runner.restarts.log:5` |
| `EXIT` line present | `2026-08-26T22:16:42Z EXIT reason=SIGTERM pid=459727` — the **first** `EXIT` line the file has ever carried (0 before the kill, 1 after) | `verification/queue/runner.log:582` |
| launched solvers unaffected | `icoFoam` **pid 359655** (`F18b_runs/fine`) alive before and after, `log.icoFoam` 188,496 → 190,996 bytes, last `Time = 0.28125` → `0.285`; `pimpleFoam` **pid 481754** (`F21_runs/medium`) alive before and after, `log.pimpleFoam` 819,748 → 918,793 bytes, last `Time = 5.00520833333` → `5.609375` | `pgrep -a`, the two logs |
| new code loaded | new START line `HEAD=77096fe8`, a descendant of the fix commit `257d1116` (`git merge-base --is-ancestor`: yes; `scripts/queue_runner.py` unchanged between the two, mtime 22:14:17Z < process start 22:17:01Z); and a field that exists only in the new code — `_launch.status_seen_utc` — was written by the new daemon into **34 of 41** launched records within its first three ticks | `verification/queue/runner.log:583`; `verification/queue/*/launched/*.json` |

## Prior finding recorded first: the 21:15–21:16Z stop of pid 419529 left NO `EXIT` line

`runner.log:464` is `2026-08-26T21:14:41Z HELD F17b_KV40_EXT.json …` and `runner.log:465` is the
cron restart's `2026-08-26T21:16:02Z START pid=459727 … HEAD=0cf8f4f6 exit_logging=SIGTERM+SIGINT+SIGHUP+exception+normal`;
nothing between them. `grep -c 'EXIT reason'` over the whole file read **0** before this kill.
Pid 419529 ran `HEAD=53fb4b19`, which predates `29d1a3fe` (the EXIT path), so the absence is
expected of that code and says nothing about how it was stopped; `runner.restarts.log:4`
(`21:16:02Z … pid 459727`) is the only record of the event. This kill is the first exercise of the
EXIT path on the live runner.

## What was done (one script, one shell invocation; commands as prose)

1. Pre-kill at **22:16:41Z**: `runner.pid` = **459727**, `ps -o pid,ppid,sid,etime`: PPID 1, SID
   459727, elapsed 01:00:39 (started 21:16:02Z by cron, HEAD 0cf8f4f6). `pgrep -a`: icoFoam 359655,
   pimpleFoam 481754; their logs' sizes and last `Time =` as in the table. `runner.log` 581 lines,
   `runner.restarts.log` 4 lines.
2. `kill 459727` once (rc 0) at **22:16:42Z**; `kill -0` one second later: gone. Three seconds
   later the `EXIT reason=SIGTERM pid=459727` line was on the log, stamped 22:16:42Z.
3. Polled `runner.restarts.log` every 5 s: new line at the 20-s poll, `2026-08-26T22:17:01Z
   queue_runner.sh: (re)started runner pid 502797`; `runner.pid` then read 502797.
4. `ps` on 502797: **PPID 1, SID 502797** (its own session — L-336, detachment by session id),
   `python3 /home/ubuntu/Certonomous/scripts/queue_runner.py --daemon`.
5. START line: `2026-08-26T22:17:01Z START pid=502797 sid=502797 … HEAD=77096fe8
   exit_logging=SIGTERM+SIGINT+SIGHUP+exception+normal`.
6. Three ticks under the new pid, all `HELD` at the ceiling (the box was at 94.8–99.9 % busy):
   `22:17:06Z box busy=94.8% (~15.2/16 cores) MemAvailable=21.6 GB; 27 entries queued`,
   `22:18:11Z box busy=99.9% … 27 entries queued`, `22:19:16Z box busy=96.9% … 27 entries queued`.
   No launch occurred during the test (nothing was launchable); the queue of 27 entries was
   carried across the restart intact.
7. Post at **22:19:20Z**: both solver pids alive, both logs grown, both last `Time =` advanced
   (table). No process other than the runner pid was signalled; nothing sent, filed or uploaded.

## Between the kills (for the record)

Pid 419529 (from the first kill) ran 20:54:01Z until a stop between 21:14:41Z and 21:16:02Z with
no `EXIT` line (pre-EXIT-path code; see above). Pid 459727 ran 21:16:02Z until this kill,
60 min 39 s, and left the EXIT line. Restart lines so far: 16:41:57Z (189825), 20:48:01Z
(399517), 20:54:01Z (419529), 21:16:02Z (459727), 22:17:01Z (502797).

---

# THIRD KILL — 2026-08-27T16:25:31Z, on the LAB-WIDE runner at 18 h 08 m uptime

**Written 2026-08-27T16:3xZ by cfd lane R for the cfd supervisor; every stamp from `date -u`.**
Sanaa's criterion (`3c3ef86c`) unchanged: the queue runner is *"certified to work even when
fleets die."* Criteria fixed **before** the kill, the same four as the second kill: **(a)** an
`EXIT reason=SIGTERM pid=<pid>` line reaches `runner.log`; **(b)** cron restarts it **within
120 s**, PPID 1 and its OWN session id (L-336); **(c)** the new daemon runs the CURRENT code;
**(d)** launched solvers survive, with their logs still growing.

**Frozen-record assertion (rule 6):** the FIRST and SECOND kill sections above are frozen
records. **Lines removed: 0. Lines whose number changed above this section: 0.** The file was
158 lines at HEAD `05241ab2` and this section is appended at its foot only; sha256 of the
pre-append file `3fe449de…a679`.

## VERDICT: **PASS** (all four clauses)

| clause | measured | artifact |
|---|---|---|
| (a) `EXIT` line | `2026-08-27T16:25:31Z EXIT reason=SIGTERM pid=502797` — the file's **second** `EXIT` line ever (count 1 → 2; for THIS pid 0 → 1, so the line is this kill's and not a carried-over match) | `verification/queue/runner.log:3000` |
| (b) restart ≤ 120 s | kill **16:25:31Z** → cron restart line **16:26:01Z**: **30 s by timestamps** (detected at the 6th 5-s poll, 32 s after the kill; the cron floor is 60 s worst case, and this landed inside one minute boundary). New pid **856460**, **PPID 1**, **SID 856460** — its own session, detached by session id | `verification/queue/runner.restarts.log:6`; `ps -o pid,ppid,sid` |
| (c) current code | new `START` line `2026-08-27T16:26:02Z START pid=856460 sid=856460 … HEAD=a6df22fa …`; `git merge-base --is-ancestor a6df22fa 05241ab2` → **yes** (ancestor-or-equal of live HEAD) | `verification/queue/runner.log:3001` |
| (d) solvers survive | three independent launched solves alive before AND after, all three logs grown, all three last `Time =` advanced (table below) | `ps`, the three logs |

## (c), stated honestly: HEAD moved, `queue_runner.py` did NOT

The old daemon started at `HEAD=77096fe8`; the new one at `HEAD=a6df22fa`; live HEAD read
`dd7c5e98` at the pre-kill stamp and `05241ab2` minutes later (peers commit constantly). But
**`scripts/queue_runner.py` is byte-identical at `77096fe8`, at `a6df22fa` and in the worktree**
— sha256 `07b10068c533…` at all three; `git log 77096fe8..a6df22fa -- scripts/queue_runner.py`
returns **no commits**; file mtime **2026-08-26T22:14:17Z**, i.e. before the *previous* daemon
started. So clause (c) is satisfied in the sense it states (the restarted daemon is running the
code at live HEAD), and **this kill did not exercise a code change** — there was none to
exercise. Recorded so no reader infers from this certificate that a new runner build was proved.

## Old daemon, as found

pid **502797**, PPID **1**, SID **502797**, started **Wed 2026-08-26 22:17:00 UTC** by cron
(`runner.restarts.log:5`), elapsed **18:08:28** at the kill; its `START` line
(`runner.log:583`) reads `HEAD=77096fe8 … exit_logging=SIGTERM+SIGINT+SIGHUP+exception+normal`.
`runner.log` 2,999 lines and `runner.restarts.log` 5 lines pre-kill. Last tick before the kill:
`2026-08-27T16:25:00Z HELD F25_DUCT3D.json: busy 89.5% >= ceiling 85.0%`.

## The kill

**ONE** `kill 502797` (SIGTERM, no `-9`, no second signal) at **2026-08-27T16:25:31Z**, rc **0**.
Two seconds later `kill -0` reported the process gone and the `EXIT` line was already on the log.
**No process other than the runner pid was signalled.** No classifier denial was returned on any
command in this test — the whole procedure ran, and the supervisor's standing instruction to
record a denial verbatim therefore has nothing to record.

## Three ticks under the new pid — the runner is working, not merely alive

    2026-08-27T16:26:07Z HELD F25_DUCT3D.json: busy 91.2% >= ceiling 85.0%
    2026-08-27T16:27:12Z HELD F25_DUCT3D.json: busy 95.5% >= ceiling 85.0%
    2026-08-27T16:28:17Z HELD F25_DUCT3D.json: busy 91.9% >= ceiling 85.0%

The box was at 91–96 % busy throughout (three solves running), so the correct behaviour is to
HOLD, and it held. **Honest limit: no LAUNCH occurred during this test** — nothing was
launchable at the ceiling — so this kill certifies the tick loop, the queue read and the ceiling
decision, and does **not** re-certify the launch path (the first kill did, with two launches).

## Queue carried across the restart

| team | queued before | queued after | launched records before → after |
|---|---|---|---|
| ansys-verification | 0 | 0 | 5 → 5 |
| cfd | **1** (`F25_DUCT3D.json`) | **1** (same entry, still HELD) | 10 → 10 |
| closure | 0 | 0 | 0 → 0 |
| dafoam | 0 | 0 | 23 → 23 |
| heat-transfer | 0 | **1** | 46 → 46 |
| verification | 0 | 0 | 0 → 0 |

**1 queued entry carried across intact**, unchanged in name and still HELD. The heat-transfer
0 → 1 is **not** this test: a peer filed an entry into `verification/queue/heat-transfer/`
during the 168 s the test ran. Nothing was refused, moved or deleted; no `refused/` directory
gained a file.

## (d) Solvers before and after — three independent solves, none touched

| solve | pids | before (16:25:30Z) | after (16:28:18Z) |
|---|---|---|---|
| **F18b fine**, `icoFoam` serial, `verification/runs/F18b_runs/fine` | **359655**, alive both | elapsed 21:16:36; `log.icoFoam` **1,300,677 B**; last **`Time = 1.94625`** | elapsed 21:19:24; **1,303,782 B** (+3,105); last **`Time = 1.95125`** |
| **T3 R_ff**, `buoyantBoussinesqSimpleFoam` on **8 ranks**, `verification/runs/T-family/T3_runs/R_ff` | **411907** (timeout wrapper), **411908** (mpirun), **411911–411918** (the 8 ranks) — **10 pids, identical list before and after** | `log.solve` **39,240,751 B**; last **`Time = 40416`** | **39,327,436 B** (+86,685); last **`Time = 40505`** (+89 iterations) |
| **T15_UP_f**, `buoyantBoussinesqPimpleFoam` serial, `verification/runs/T-family/T15_runs/T15_UP_f` | **709355** (timeout wrapper), **709356**, alive both | `log.solve` **23,068,110 B**; last **`Time = 92.33`** | **23,222,757 B** (+154,647); last **`Time = 92.95`** |

The T-family 8-rank job is the strongest of the three: an `mpirun` tree in its own session
survived the runner's death with **every one of its eight ranks** and kept advancing at its
normal rate. Launched solves are `setsid`-detached, so a SIGTERM to the runner cannot reach
them — measured a third time.

## Full restart history at this certificate's foot

`verification/queue/runner.restarts.log`, six lines: 16:41:57Z (189825), 20:48:01Z (399517),
20:54:01Z (419529), 21:16:02Z (459727), 22:17:01Z (502797) — all 2026-08-26 — and
**2026-08-27T16:26:01Z (856460)**, this test. Pid 502797's **18 h 08 m** unattended run is the
longest the record holds, and it spanned the whole fleet-death-and-reform of the session change.

Nothing in this test was sent, filed or uploaded (rule 7). Cost: **0 core-min of solver
compute** — the test signalled one daemon and read files; the 168 s of polling is agent time,
not compute.
