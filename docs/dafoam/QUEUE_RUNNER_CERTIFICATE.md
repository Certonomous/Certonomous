# QUEUE RUNNER CERTIFICATE — the dafoam runner path, from disk evidence only

**Written 2026-08-26T21:03Z by dafoam `lab-lane` Q-A for `dafoam-supervisor`**, on Sanaa's order at `3c3ef86c` (the kill test: an entry filed, the agent absent, the runner launches it, the STATUS lands). Every statement below cites a file on this box as it stood at the write time; nothing here is relayed from an agent's memory. Verdict vocabulary: `PASS` / `NOT A RESULT` / `PENDING` only. Permission for the launches certified here: `bc0e687e` (Sanaa's words, boarded verbatim). Nothing here leaves the box (rule 7).

> **ID-NAMESPACE WARNING.** `D5`, `D6`, `D14` in this document are the dafoam **curriculum** items (`cases/dafoam/EXPERTISE_CURRICULUM.md`), not the `docs/DOCKET.md` rows of the same number.

---

## 1. What is certified — `PASS`, five clauses, each with its artefact

### 1.1 The runner launched a dafoam entry from the drop path with no hand on it

`verification/queue/LAUNCH_LOG.tsv` (tab-separated: utc, team, case, pid, sid, ranks, est core-min, prereg sha, STATUS path):

| utc | case | pid = sid | ranks | est | prereg |
|---|---|---|---|---|---|
| `2026-08-26T17:40:32Z` | `D14M` | 307428 | 1 | 0.67 | `dd6c808e35a9cf61291058c3ad15a9a7e590347c` |
| `2026-08-26T17:48:08Z` | `D5_chain_r2` | 323226 | 4 | 1378.3 | `a893355d808f4a10c012d6eeea7ef2c4fc198876` |

`verification/queue/runner.log:205` `17:40:32Z LAUNCHED team=dafoam case=D14M …` and `:222` `17:48:08Z LAUNCHED team=dafoam case=D5_chain_r2 pid=323226 sid=323226 ranks=4 est=1378.3 core-min prereg=a893355d`, each preceded by the tick's own box reading (`:221` `busy=38.5% (~6.2/16 cores) MemAvailable=28.2 GB; 6 entries queued`). Both entries were moved to `verification/queue/dafoam/launched/` with the runner's `_launch` block (`D5_chain_r2.json`: `utc 2026-08-26T17:48:08Z, pid 323226, sid 323226, started_epoch 1787766488.05`). `pid == sid` on every row: each launch is its own session leader, as `docs/standards/QUEUE_RUNNER.md` §4 registers. Thirteen dafoam rows stand in `LAUNCH_LOG.tsv` at the write; 38 `LAUNCHED` lines lab-wide in `runner.log`.

### 1.2 The agents were absent, and the launched work ran on

**The fleet kill, on disk:** `git log` carries no commit between `2f812a30` (`2026-08-26 17:49:05Z`, dafoam UPDATE T-Q2b) and `33dbe337` (`2026-08-26 20:42:22Z`, `CHIEF: third fleet kill ~17:50Z; re-form at 2026-08-26T20:42Z`) — a 2 h 53 min gap in a repository that had been receiving commits every few minutes (`git log --format='%ad %s' --date=iso`). No `docs/LAB_STATE.md` block, no lane record and no supervisor block carries a stamp inside that window. That absence is the evidence of the absence; the kill itself leaves no artefact.

**The runner across the gap:** `verification/queue/runner.log:49` `2026-08-26T16:41:57Z START pid=189825 sid=189825 … HEAD=ba36547`; `verification/queue/runner.restarts.log:1` `2026-08-26T16:41:57Z queue_runner.sh: (re)started runner pid 189825`. The log carries **one tick per minute, unbroken, from 16:41:57Z to 20:47:43Z** (`:403-405` `20:40:38Z / 20:41:38Z / 20:42:38Z EMPTY: no entries in any team queue`; the runner launched `VMFL064-R2` at `20:45:43Z`, `:` in `LAUNCH_LOG.tsv`). Read live by this lane at `20:47:38Z`: `ps -o pid,etime,lstart -p 189825` → `189825 04:05:41 Wed Aug 26 16:41:56 2026 python3 /home/ubuntu/Certonomous/scripts/queue_runner.py --daemon` — alive since 16:41:56Z, i.e. through 17:50Z.

**The launched work across the gap** (`/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density/`, the D5 run root; driver pid 323228 under the runner's sid 323226):

| record | content | mtime |
|---|---|---|
| `STATUS.O48` | `preflight arm=O48 stamp=20260826T174808Z driver_pid=323228 …` then `rc=0 stamp=20260826T204020Z arm=O48 source=launcher_exit=docker_inspect_ExitCode launch_out=O48_launch.out h5_min_GiB=27.83 aggregate_waited_s=0 permission=bc0e687e` | `2026-08-26 20:40:20Z` |
| `ledger.txt` `ARM=O48` row | `rc=0 wall_s=10268 ranks=4 core_min=684.533 cap_core_min=800.0 enforced_wall_s=12000 memory=12g inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=28.38 memavail_post_GiB=27.86 cpuset=8,10,11,13 delivered_cores_mean=[3.9954 n=680 max_nr_throttled=42539] … log=O48_20260826T174911Z_325871.log` | row written 20:40:20Z |
| `O48/opt_IPOPT.txt`, `O48/OptView.hst`, `O48_20260826T174911Z_325871.log` (2.42 MB), `O48_…cpu.jsonl` (680 samples) | the arm's artefacts, produced 17:49→20:40Z | 20:39–20:40Z |
| `STATUS.ACC48` (preserved as `STATUS.ACC48.deadline_20260826T204405Z`) | `preflight arm=ACC48 stamp=20260826T204020Z driver_pid=323228` then `rc=124 stamp=20260826T204405Z arm=ACC48 source=launcher_exit=docker_inspect_ExitCode …` | `2026-08-26 20:44:05Z` |
| `STATUS.chain` | `chain=started arms=[O48 ACC48 F48 O192 ACC192 F192] pid=323228 stamp=20260826T174808Z` → `arm=O48 rc=0 stamp=20260826T204020Z` → `arm=ACC48 rc=124 stamp=20260826T204405Z` → `chain=STOPPED_AT_FIRST_NONZERO arm=ACC48 rc=124 stamp=20260826T204405Z` | 20:44:05Z |
| the runner's own record, `cases/dafoam/ladder-a/A2/curriculum_D5/STATUS.D5_chain_r2` | `launcher_rc=124 end=2026-08-26T20:44:05Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc` | `2026-08-26 20:44:05Z` |

Every one of these was written between 17:49Z and 20:44Z, inside the window in which no agent existed. **The O48 arm — 10,268 s of solver wall, 684.533 core-min, 100 IPOPT majors — started, ran, was bookkept from `docker inspect`, and had its ledger row and STATUS written by the detached driver, with no agent alive.** The ACC48 `rc=124` at 20:44:05Z is the arm's registered in-container deadline firing (a pre-registration defect, `D5-PREREG-DEF-1`, D5 Addendum 3 `b5b428bc`); it is cited here only as the second STATUS that landed unattended — its rc is an honest record written by the same path.

### 1.3 The STATUS files are the driver's, from `docker inspect`, not the runner's `$?`

The rc in `STATUS.O48` / `STATUS.ACC48` / the ledger rows is `source=launcher_exit=docker_inspect_ExitCode` (the launcher reads `.State.ExitCode` before its post-bookkeeping `docker rm`; no `--rm`; `d5_run_arm.sh`). The runner's `STATUS.D5_chain_r2` carries `launcher_rc=124 … NOT-the-solver-rc` — the L-342 label, an infrastructure record, agreeing with the driver's last rc by coincidence of the chain's stop code, not by construction. Both classes are on disk and neither is composed from the other.

### 1.4 The self-restart clause was exercised today — twice, by cron, within 60 s each time

`crontab -l` (user `ubuntu`, read 20:47Z; `systemctl is-active cron` → `active`):

```
@reboot sleep 30 && /home/ubuntu/Certonomous/scripts/demo_servers.sh
@reboot /bin/bash /home/ubuntu/Certonomous/scripts/queue_runner.sh
* * * * * /bin/bash /home/ubuntu/Certonomous/scripts/queue_runner.sh
```

`verification/queue/runner.restarts.log`, complete at the write:

```
2026-08-26T16:41:57Z queue_runner.sh: (re)started runner pid 189825
2026-08-26T20:48:01Z queue_runner.sh: (re)started runner pid 399517
2026-08-26T20:54:01Z queue_runner.sh: (re)started runner pid 419529
```

`runner.log`: pid 189825's last tick `20:47:43Z EMPTY`; `:413` `20:48:01Z START pid=399517 … HEAD=e73740cb`; pid 399517's last tick `20:53:11Z EMPTY`; `:423` `20:54:01Z START pid=419529 … HEAD=53fb4b19`; `verification/queue/runner.pid` = `419529`, `ps -p 419529` alive (started 20:54:01Z). Each restart landed at the top of the next minute after the previous runner's last tick — the `* * * * *` line doing what `QUEUE_RUNNER.md` says it does. The `HEAD=` field moved across the second restart to the commit after cfd's `117bf190` (`2026-08-26 20:52:53Z`, `queue_runner: cap watch keys on cap_core_min_registered …`), consistent with a runner stopped to pick up its owner's new code; **who stopped pids 189825 and 399517 is not on disk** (no kill record exists in `runner.out`, `runner.log` or the restarts log), and this certificate does not say.

### 1.5 Runner-launched later phases handed off with no agent in the loop (W2R), before the kill

`docs/LAB_STATE.md` UPDATE T-Q2b (`2f812a30`, 17:49:05Z) and the records under `cases/dafoam/curriculum_D12R2/`: `W2R_plan_wait` (runner-launched 17:28:37Z, pid 289429) saw `PHASE1_COMPLETE` at 17:46:08Z and ran the frozen comparator (`step_plan.json`, `admissible:false`); `W2R_phase2_wait` (runner-launched 17:15:37Z, pid 250242) saw the plan at 17:46:38Z and fired the registered no-launch branch at 0.0 core-min. This closure happened **with agents alive** (17:46Z < 17:50Z) and is certified only as *runner-launched wrappers evaluating their own preconditions and handing off among themselves*, not as an unattended run.

---

## 2. What is NOT certified — stated plainly

1. **A runner restart across a reboot has not been exercised.** The only reboot today was 15:19Z (`last -x reboot`: `7.0.0-1011-aws … Wed Aug 26 15:19 still running`), and the runner's first start was 16:10:12Z (`runner.log:1` `START pid=106422`), by hand, after that reboot; `restarts.log` begins at 16:41:57Z. The `@reboot` line is installed and is **untested**: `PENDING`.
2. **D14-M did not run unattended.** `STATUS.D14M` `launcher_rc=0 end=2026-08-26T17:41:47Z` — complete nine minutes before the kill. It certifies clause 1.1 (runner launch) only.
3. **The runner does not sequence, and did not.** D5's arms were sequenced by the item's own detached driver; the runner launched one argv once. A chain stop (`STOPPED_AT_FIRST_NONZERO`) is not re-fired by the runner — the re-fire is a new entry (`D5_chain_r3.json`, this lane, 20:55Z), as `QUEUE_RUNNER.md` registers.
4. **The runner's cap watch reports; it did not and cannot kill.** The ACC48 `rc=124` came from the `timeout` inside the container (`D4S_DEADLINE_IN_CONTAINER_S: 150` in the log), not from the runner. No `CAP_OVERRUN.txt` exists for `D5_chain_r2` (the 1.10 × 1378.3 × 60 / 4 = 22,742 s watch had not elapsed).
5. **Nothing here is a physics verdict.** O48's `rc=0` row is a completion record under L-342's physics-critical class; the D5 grade (`d5_grade.py`) has not run and the item is `PENDING`.
6. **The runner's own liveness across the kill rests on one `ps` reading and the unbroken minute ticks in `runner.log`; the `ps` line is this lane's reading, quoted, not a file.** The ticks are the file.

---

## 3. Verdict

**Kill test, dafoam runner path: `PASS`** on clauses 1.1–1.4 — an entry filed at 17:48:08Z by a lane that then died, launched by the runner in the same minute, its solver arm run to `rc=0` and its STATUS and ledger row landed at 20:40:20Z with no agent alive; the runner itself alive from 16:41:56Z through the kill and re-spawned by cron twice within 60 s of stopping. Clauses in §2 are `PENDING` (reboot restart) or out of scope, and are named.

Provenance of every path above: `verification/queue/{LAUNCH_LOG.tsv,runner.log,runner.restarts.log,runner.pid}`, `verification/queue/dafoam/launched/D5_chain_r2.json`, `cases/dafoam/ladder-a/A2/curriculum_D5/STATUS.D5_chain_r2`, `/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density/{STATUS.O48,STATUS.ACC48.deadline_20260826T204405Z,STATUS.chain,ledger.txt}`, `git log`, `crontab -l`, `last -x reboot`.
