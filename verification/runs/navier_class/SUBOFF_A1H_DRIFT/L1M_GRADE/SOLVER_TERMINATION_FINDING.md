# ~~ALL SEVEN SUBOFF A1h L1M SOLVERS DIED BETWEEN 00:11:04Z AND 00:14:24Z ON 2026-09-14~~
# ALL SEVEN WERE **DELIBERATELY STOPPED** BETWEEN 00:11:04Z AND 00:14:24Z ON 2026-09-14, ON SANAA'S ORDER

> **VERSION 1.0 -> 1.1, amended 2026-09-14. The title above is STRUCK and kept.
> THE TERMINATION IS EXPLAINED: it was a deliberate, owner-ordered stop executed by a
> sibling cfd lane. See AMENDMENT 1 at the foot for the mechanism, pids and timestamps.
> SECTION 3 BELOW ("WHAT IS NOT ESTABLISHED") IS STRUCK AS A CONCLUSION AND KEPT AS A
> METHOD RECORD.** Sections 1 and 2 stand unaltered and are still correct: every
> exclusion in section 2 holds, and the reason none of them fitted is that the cause was
> inside this session and not visible to this lane.
> *Line numbers above this banner have shifted by its own length; nothing in this
> repository cites this file by line.*

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

## 3. ~~WHAT IS NOT ESTABLISHED — SAID PLAINLY~~ — **STRUCK 2026-09-14, KEPT**

> **STRUCK AS A CONCLUSION.** The agent of the termination *is* established — AMENDMENT 1.
> Kept verbatim below because it is the record of how a termination was narrowed by an
> observer to whom the cause was not known, and because its caution about the buffered
> log was right on the mechanism even while wrong on the agent.

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


---

# AMENDMENT 1 — 2026-09-14. THE CAUSE, RELAYED BY THE CFD-SUPERVISOR: A DELIBERATE STOP ON SANAA'S ORDER

**Version 1.0 -> 1.1. This amendment alters no gate, threshold, cap or label; the act's
verdict is unchanged and remains `NOT A RESULT` on strict completion.**

## A1.1 WHAT ACTUALLY HAPPENED

The cfd-supervisor reports that a **sibling cfd lane stopped the seven points on Sanaa's
instruction**, concurrently with this lane arming the grader and without this lane being
told. Sanaa's words as relayed by the supervisor: *"no lets stop them and stop drivaer as
well that way we gain 32 ranks. But cfd first checks that all residuals are converged."*

**PROVENANCE, STATED SO A SUCCESSOR CAN WEIGH IT.** Everything in this section §A1.1 and
in §A1.2 is **relayed by the cfd-supervisor**, not measured by this lane. This lane
measured only what is in §1 and §2 above. The relay is recorded as a relay.

## A1.2 THE MECHANISM — AND IT EXPLAINS EVERY FEATURE §1 COULD NOT ATTRIBUTE

| step | what was done | why the log looks the way it does |
|---|---|---|
| checkpoint first | `runTimeModifiable false` in all seven, so `writeNow` **could not** be injected; each solver was allowed to reach its next scheduled write (`writeInterval 15`) and was stopped only after that write had provably completed | the last written time on each point is a clean multiple of 15 |
| the signal | **`SIGTERM` to the `mpirun`**, the target identified by `/proc/<pid>/cwd` and re-verified by cwd in the same instant the signal went. **`pkill -f` was not used.** | `mpirun` reaping a SIGTERMed child **returns 1 and prints nothing** — hence `simpleFoam_rc=1`, mid-iteration, with no `End`, no `FOAM FATAL` and no signal banner |

Checkpoint integrity was verified before the stop, relayed: **196 of 196 field files
banner-closed, 0 truncated**, with a planted control that correctly named a deliberately
truncated copy of `BETA_p00/processor0/2880/U`.

**ONE PRECISION CORRECTION, MADE RATHER THAN ABSORBED.** The supervisor's message calls
`1486309 / 1486327 / 1486345 / 1486350 / 1486354 / 1486399 / 1486419` the **wrapper** pids.
They are not. The `solve_a1h.sh` wrappers this lane observed alive at 00:09Z were
**1479996, 1479998, 1479999, 1480000, 1480001, 1480002, 1480003** (all PPID 1). The
`14863xx` family is the **`mpirun`/`simpleFoam` layer beneath them** — corroborated
independently by the `auto-stop` cron, which logged `ALIVE: solver or mesher running
(simpleFoam, pid 1486312)` at both 00:05:02Z and 00:10:01Z. The signal went to the right
process; only the label on it was wrong.

## A1.3 WHAT SECTION 2 IS WORTH NOW

Every exclusion in §2 **holds**: not OOM, not a reboot, not `auto-stop`, not the queue
runner, not a displacing workload, not this lane. They were exhaustive over the causes
**visible from outside this session**, and the cause lay inside it. §3's caution — that a
block-buffered stdout means the clean tail proves nothing either way — was **right about
the mechanism** and only wrong about the agent: the tail is clean because `mpirun` prints
nothing when it reaps a SIGTERMed child, exactly as §3 warned a reader not to over-read.

**THE LESSON THIS FILE NOW CARRIES:** a lane can exclude every external cause correctly
and still be wrong, because **a sibling lane in the same session is not an external cause
and is invisible to `ps`, `dmesg` and `journalctl` as a *cause***. The cheap fix is
coordination, not more forensics.

## A1.4 WHAT IS NOT CHANGED, AND WHY

- **`endTime` is not amended.** A chief's or supervisor's operationalisation is not
  Sanaa's consent (standing rule 9); her relayed words authorise a stop and say nothing
  about redefining a gate. The seven points stopped at Time 2671–2881 of 3000 and fail
  standing rule 4 on every channel.
- **The verdict stands as the frozen comparator filed it: `NOT A RESULT`**
  (`LANDING.txt`, `A1H_L1M_GRADE.json`). It is `NOT A RESULT` a second, independent way
  under prereg §4.2, the fit being positive where Roddy's is negative.
- **`grade_watch_a1h_l1m_v2.sh` stays armed and unchanged.** Waiting on
  `last Time == 3000 AND solve_rc == 0` is the correct landing condition; a stopped run
  cannot satisfy it, which is the instrument working.
