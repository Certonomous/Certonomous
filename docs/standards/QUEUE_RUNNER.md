# QUEUE_RUNNER — the lab's detached, OS-level queue runner

**Script:** `scripts/queue_runner.py` (landed `29223b1b`; cfd owns it as OpenFOAM tooling).
**Order:** Sanaa, 2026-08-26 ~03:00Z (*"the queues must also be detached from the lab
that way they dont depend on the lab being active"*); permission in her own words at
HEAD `bc0e687e`; permission rules added by her 2026-08-26 (`Bash(setsid *)`,
`Bash(nohup *)`, `Bash(python3 scripts/queue_runner.py*)`).
**Entry schema:** `docs/standards/QUEUE_ENTRY_STANDARD.md` and
`verification/queue/<team>/README.md` — this document does not restate it.

## What it does, each tick (60 s)

1. Measures the box: busy % from a 5 s `/proc/stat` delta (never `loadavg`),
   `MemAvailable` from `/proc/meminfo`.
2. Reads every `verification/queue/<team>/*.json`. Each is validated by
   `scripts/queue_entry_check.py`'s own checks (schema, full 40-hex `prereg_commit`
   that exists and holds `prereg_path`, age guard on `cwd`, `ranks`). **An entry that
   fails is MOVED to `<team>/refused/<id>.json` with the reasons in
   `<id>.REFUSED.txt`. Nothing is ever deleted.**
3. Launches **at most ONE** entry per tick, **first-fit over the whole queue** (a held
   wide entry never blocks a narrow one behind it; every HELD is logged), round-robin
   across teams, oldest first within a team, and only when: busy < 85 % (default; the midpoint of Sanaa's 80–90 %
   band read as a *launch* ceiling), busy-cores + `ranks` ≤ 0.9 × cores, and
   `MemAvailable` ≥ the entry's `memory_floor_gb`. Otherwise the entry is `HELD` and
   stays queued.
4. The launch form is fixed:
   `setsid nohup bash -c 'cd <cwd> && <argv> > <cwd>/launcher.queue.out 2>&1; R=$?; echo "launcher_rc=$R end=<utc> note=exit-status-of-the-launch-argv-NOT-the-solver-rc" > <cwd>/STATUS.<case_id>'`
   — **the launch argv's exit status is captured inside the detached wrapper and is
   labelled as such**: it is an INFRASTRUCTURE record (L-342) and never claims the
   solver's rc — a launcher that refuses at zero compute and exits 0 must not read as
   a completed solve. Rule 4 is applied from the case's own RC/log files (`setsid`/`timeout` return 0 for
   every outcome; measured `4225ef0c`, `83769288`). The entry is moved to
   `<team>/launched/<id>.json` with `_launch` (utc, pid, sid, status file) appended,
   and one line goes to `verification/queue/LAUNCH_LOG.tsv`.
5. Cap watch — two flags, keyed on what the entry registered (*edited 2026-08-26T20:52:53Z on the cfd
   supervisor's 17:46Z order, after F20's flag fired at 1.10 × its ESTIMATE while the run
   sat at 29 % of its CAP; this document is not frozen*):
   - the entry carries the **optional numeric field `cap_core_min_registered`** →
     `CAP_OVERRUN.txt` is written beside the run when it has no STATUS after
     **1.00 × cap × 60 / ranks** seconds, and not before;
   - the field is absent → `ESTIMATE_OVERRUN.txt` at **1.10 × `cost_core_min_estimate` × 60 /
     ranks** seconds, and its text says it is an **ESTIMATE overrun, not a cap**.
   Both files say REPORTED, NOT ENFORCED; the runner log line is `CAP-OVERRUN` or
   `ESTIMATE-OVERRUN`; a STATUS file silences both. **Caps report; they never kill**
   (`COMPUTE_BUDGET_CHARTER.md`). `scripts/queue_entry_check.py` accepts the optional field
   unchanged (measured: F20's entry carrying it → `ACCEPTED`, rc 0). Both cases are planted
   controls in `--selftest` (cap file at the cap time and not at cap − 1 s; estimate file
   at 1.10 × estimate and not before; the same record with the cap field stripped flips
   to the estimate path).
   - **Which launch a flag is about (added 2026-08-26T22:15Z, cfd supervisor's 22:05Z finding):**
     ansys `VMFL064-R2`'s `CAP_OVERRUN.txt` was stamped 20:45:38Z with elapsed 10,585 s — the
     time since the case's FIRST launch (17:49:13Z, pid 326419), which had finished; its owner
     had removed STATUS to re-run, the watcher fired the instant STATUS vanished, and the
     20:45:43Z relaunch (pid 390178) then overwrote `launched/VMFL064-R2.json`, so the flag
     named a launch that no longer had a record. Same class: heat-transfer `T5_C` (17:41Z
     record, never a STATUS) flagged 20:52:11Z and 20:54:01Z beside the 20:54:06Z `T5_C_v2`
     relaunch of the same cwd. A launched record keyed on `case_id` alone was governing a cwd
     somebody else had re-armed. Now: (i) a launch **ARCHIVES** any current record of the same
     file name or the same `case_id` as `launched/<name>.<its _launch.utc, colons stripped>.json`
     (e.g. `VMFL064-R2.2026-08-26T174913Z.json`; log word `ARCHIVED previous launch record for
     <id> (<utc>, pid <pid>)`; nothing deleted), and the cap watch reads **only current records**
     — a name matching `\.\d{4}-\d{2}-\d{2}T\d{6}Z(\.\d+)?\.json$` is never watched; (ii) a
     record whose STATUS the watch has **seen** is stamped `_launch.status_seen_utc` once and
     never fires again — STATUS vanishing afterwards is a re-armed cwd, not this launch running
     on; (iii) both flag texts name the launch they judge, `[launch_utc=<_launch.utc> pid=<pid>
     started_epoch=<epoch>]`, and a flag is written **at most once per launch record** (before:
     once per FILE, `not flag.exists()`, so a stale flag silenced every later launch of the same
     cwd for ever); a flag naming another launch of the same cwd is superseded with its text kept
     beneath. Planted in `--selftest`: launch A through the real launch path, STATUS seen, watch
     at +10,000 s and again after STATUS is removed → nothing; the same watch with the stamp not
     consulted → the stale flag naming A (flips); relaunch of the same `case_id` → A archived
     under its utc, B fresh; watch at B + 1 s → nothing; at B + cap + 1 s → the flag names B on
     top, A's text beneath; at B + 3,600 s → unchanged; the `T5_C` shape (same `case_id` under
     `_v2.json`) with the archive step disabled → the stale flag naming the old launch, with it
     enabled → archived, nothing fires (flips).

## What it never does

- Never authorises. `SUPERVISION_CHARTER.md` §3 check 4 (pre-registration committed
  before compute) is the supervisor's own, discharged **at enqueue**. A file in a queue
  directory is a proposal that the supervisor has already checked, or it is a defect.
- Never sequences phases of one item. Two entries of one item enqueued together may
  launch on consecutive ticks; a launcher that requires a prior phase must refuse for
  itself (dafoam's `D12R_phase4` was launched 65 s after `D12R_phase3` on 2026-08-26 —
  its own `step_plan2.json` guard is what stands between them).
- Never dispatches off-box: `host` ≠ this box → `SKIP` with a logged reason.
- Never kills, never deletes, never edits/stages/commits in git, never runs under
  `python3 -O` (refuses, rc 2), carries no `assert`.
- Never lets a superseded launch record judge a cwd (added 2026-08-26T22:15Z, after
  `VMFL064-R2` and `T5_C`): a relaunch of a `case_id` archives the previous record instead of
  overwriting it, a record whose STATUS has been seen is finished for good, and every overrun
  flag names the launch it is about. The runner still never removes STATUS and never decides
  whether a re-run is legitimate — that is the owning team's; it only stops mistaking the
  owner's re-arming for its own launch running on.

## Filling a queue

Drop `verification/queue/<team>/<CASE_ID>.json` with the required fields
(`team, case_id, prereg_commit, prereg_path, launch_cmd (argv list), cwd (absolute),
ranks, cost_core_min_estimate, cost_basis (must say "not measured" and "derived" or
"reported-by-owner"), memory_floor_gb, enqueued_by`) — check it first with
`python3 scripts/queue_entry_check.py verification/queue/<team>/<CASE_ID>.json`.
Optional: `host` (default local). `cwd` must not already hold `0/` or a numeric time
directory (rule 4).

## Operating it

- **Self-restart ("even if the lab dies", Sanaa 73eccb1b):** `scripts/queue_runner.sh` starts the
  runner only if the pidfile's process is not alive; installed in the `ubuntu` crontab as
  `@reboot` and `* * * * *`, so a killed runner is back within 60 s and a rebooted box
  starts one. Restarts are logged to `verification/queue/runner.restarts.log`.

- Start: `setsid nohup python3 scripts/queue_runner.py --daemon > verification/queue/runner.out 2>&1 < /dev/null &`
- Lock: `verification/queue/runner.pid` (refuses to start if that pid is alive).
- Log: `verification/queue/runner.log` (one line per tick; `EMPTY`, `HELD`, `LAUNCHED`,
  `REFUSED`, `SKIP`, `CAP-OVERRUN`, `ESTIMATE-OVERRUN`, `START`, `EXIT`, `ARCHIVED` (added
  2026-08-26T22:15Z) are the only event words).
- **Exit path (added 2026-08-26T21:15Z, cfd supervisor's order after runner pid 189825 died
  between 20:47:43Z and 20:48:01Z with no recorded reason):** the daemon handles SIGTERM,
  SIGINT and SIGHUP and every way out of its loop writes one line
  `EXIT reason=<signal name|ExceptionClass: msg|normal> pid=<pid>` to `runner.log` before the
  process ends (a signal → rc 128+signum; an escaping exception → logged with its innermost
  frame and RE-RAISED, never swallowed; `--once` → `normal`). A runner that leaves no `EXIT`
  line was killed by something it could not handle (SIGKILL, OOM) — that absence is itself the
  record. `--selftest` sends SIGTERM to a scratch-root daemon and requires the line (planted:
  absent before the signal, present after). The per-entry `ERROR (tick, continuing)` line is
  unchanged: one bad entry is logged and the queue goes on; it is not silent.
- **Selftest under load (same date):** the box reading is injected in `--selftest`
  (`tick(..., measure=fake)`), so its controls no longer read the live `/proc/stat` — control 5b
  had failed on a box at ≥ 94 % busy and passed on re-run (the L-339 class). One control hands
  in a 99 % reading and must be HELD, then a 10 % reading and must launch.
- Options: `--busy-ceiling`, `--core-fraction`, `--interval`, `--root`, `--once`.
- Stop: `kill $(cat verification/queue/runner.pid)` — launched solvers are in their own
  sessions and are unaffected.
- Selftest (rule 3 planted controls, scratch root only): `python3 scripts/queue_runner.py --selftest`.

First live tick, 2026-08-26 16:10:12Z, pid 106422: launched dafoam `D12R_phase3`, then
`D12R_phase4` one tick later.

## Deploying the runner on a second instance (e.g. the GPU box, ansys-verification)

The runner is host-generic: it reads `nproc`, `/proc/stat` and `/proc/meminfo`, and
launches whatever argv an entry carries. To run it there:

1. Have the repository (or at minimum `scripts/queue_runner.py`, `scripts/queue_runner.sh`,
   `scripts/queue_entry_check.py` and a `verification/queue/<team>/` tree) checked out at
   the same path, `/home/ubuntu/Certonomous`, with the same `git` history — the validator
   resolves `prereg_commit` with `git cat-file` against that checkout, so a sha the remote
   checkout does not have is REFUSED there (pull before enqueueing).
2. Entries meant for that box carry `"host": "<its hostname or IP>"`; entries without
   `host` are local everywhere. Each runner launches only entries whose `host` is empty,
   `local`, or its own `uname -n`; the rest are `SKIP`ped with a logged reason. So the same
   queue tree can be shared (e.g. rsync'd) between the two boxes without double launches,
   provided every remote-only entry names its host.
3. GPU cases: `ranks` counts CPU ranks for the ceiling; a GPU solver still names `ranks`
   (1 if it drives one device) and states GPU-hours in `cost_basis` (rule 12 — GPU spend
   sits outside the CPU blanket and is priced from the console).
4. Install the same crontab lines (`@reboot` and `* * * * *` → `scripts/queue_runner.sh`)
   under the account that owns the checkout; confirm with `crontab -l` and
   `systemctl is-active cron`.
5. Selftest there first: `python3 scripts/queue_runner.py --selftest` (scratch root only).
