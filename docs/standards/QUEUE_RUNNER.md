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
5. Cap watch: if a launched case has no STATUS after 1.10 × (registered core-min × 60 /
   ranks) seconds, `CAP_OVERRUN.txt` is written beside it. **Caps report; they never
   kill** (`COMPUTE_BUDGET_CHARTER.md`).

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
  `REFUSED`, `SKIP`, `CAP-OVERRUN` are the only event words).
- Options: `--busy-ceiling`, `--core-fraction`, `--interval`, `--root`, `--once`.
- Stop: `kill $(cat verification/queue/runner.pid)` — launched solvers are in their own
  sessions and are unaffected.
- Selftest (rule 3 planted controls, scratch root only): `python3 scripts/queue_runner.py --selftest`.

First live tick, 2026-08-26 16:10:12Z, pid 106422: launched dafoam `D12R_phase3`, then
`D12R_phase4` one tick later.
