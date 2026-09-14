# ALL SEVEN SUBOFF A1h L1M SOLVERS DIED BETWEEN 00:11:04Z AND 00:14:24Z ON 2026-09-14

**A crash is a finding until triage says otherwise. Triage is the supervisor's own check;
this file is the evidence, gathered by a cfd lab-lane, and it names what it could not
establish.**

## 1. THE FACTS

Zero `simpleFoam` processes remain (`ps -eo cmd | grep -c '[s]impleFoam'` → **0**); all
seven `solve_a1h.sh` wrappers are gone. Each wrote `simpleFoam_rc=1` into its own
`STATUS.solve` and `1` into `solve_rc`.

| point | last `Time` in `log.simpleFoam` | `End` lines | FOAM FATAL / signal lines | `solve_rc` | `solve_rc` mtime (UTC) |
|---|---|---|---|---|---|
| BETA_m04 | 2821 | 0 | 0 | 1 | 00:11:04 |
| BETA_p04 | 2806 | 0 | 0 | 1 | 00:11:24 |
| BETA_m12 | 2746 | 0 | 0 | 1 | 00:12:04 |
| BETA_m08 | 2791 | 0 | 0 | 1 | 00:13:45 |
| BETA_p08 | 2836 | 0 | 0 | 1 | 00:13:45 |
| BETA_p00 | 2881 | 0 | 0 | 1 | 00:13:54 |
| BETA_p12 | 2671 | 0 | 0 | 1 | 00:14:24 |

Every log ends **mid-iteration** — part-way through the pressure/turbulence block of the
iteration after the last completed one — with no `End`, no `FOAM FATAL ERROR`, no signal
banner. `endTime` is 3000, so all seven stopped at **89–96 % complete**, after ~14 h 35 m
of wall time each.

## 2. WHAT WAS EXCLUDED, AND HOW

- **Not the OOM killer.** `free -g` at 00:16Z: 622 GB available, 0 swap used.
  `dmesg -T` carries no `oom-kill`, no `Out of memory`, no `Killed process` in the window.
- **Not a reboot or an auto-stop power-off.** `uptime` reads 1 day 2:44 — no restart. The
  `auto-stop` cron logged `ALIVE: solver or mesher running (simpleFoam, pid 1486312)` at
  00:10:01 and, at 00:15:02, `ALIVE: ... (snappyHexMesh, pid 1768257)` — it never fired.
- **Not the queue runner.** `scripts/queue_runner.py` states in its own header that it
  never kills, and `verification/runs/navier_class/SUBOFF_A1H_DRIFT/QUEUE.log` records
  `QUEUE_HALTED=2026-09-13T09:10:24Z`. It also launched nothing in the window:
  `verification/queue/LAUNCH_LOG.tsv`'s last row is `2026-09-13T16:37:40Z`.
- **Not a workload displacing them.** No non-kernel process started between 00:05 and
  00:16Z other than this session's own shells. Load average fell from 52.5 to 36.9 — i.e.
  cores were *released*, not contended for.
- **Not this lane.** Everything this lane ran against the seven cases was a **read** or a
  **copy out** to scratch. The one process this lane stopped was its own watcher
  (pid 1805460, `kill 1805460`, at 00:16Z) — **after** all seven `solve_rc` files already
  existed, and `pkill -f` was never used. The first death (00:11:04Z) precedes this lane's
  first read of that case.

## 3. WHAT IS NOT ESTABLISHED — SAID PLAINLY

**The agent of the termination is unknown.** `journalctl` for 00:08–00:16Z carries no
signal, kill or cgroup event touching these processes; the only entries are a DAFoam
container exiting at 00:11:17Z and the minute cron. `mpirun` returning **1** is consistent
with a rank exiting non-zero, which is *not* the signature of an external `SIGKILL`
(that usually surfaces as 137 or a signal banner).

**And the absent error message proves nothing either way.** The wrapper redirects with
`> log.simpleFoam 2>&1`, so stdout is block-buffered; a rank killed outright loses its
buffer, and so would a genuine `FOAM FATAL` written in the final partial block. **The
clean-looking tail is not evidence of a signal.** The remaining route to a cause is the
per-rank state and the `processorN` write times, which this lane did not exhaust.

## 4. CONSEQUENCE FOR THE ACT

All seven fail standing rule 4 on **every** channel (`rc != 0`, no `End`,
`last Time != 3000`, no `3000/` fields, age guard cannot evaluate). The frozen comparator
returns **`NOT A RESULT`** — see `LANDING.txt` and `A1H_L1M_GRADE.json`. The detached
grader `grade_watch_a1h_l1m_v2.sh` stays armed on the landing condition, so a relaunch or
resume is graded without an agent present.
