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
