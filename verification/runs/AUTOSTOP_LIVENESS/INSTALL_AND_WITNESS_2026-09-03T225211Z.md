# AUTO-STOP PATCH — INSTALL EVENT AND FIRST PRODUCTION WITNESS

**Record written** 2026-09-03T~2300Z by a `lab-lane` for the **cfd** team, read-only,
zero compute, no `sudo`, no signal sent to any process.

**Verdict carried by this record:** the install is **verified by measurement**. The
class of wrongful stop is **closed at the root cron entry** and **NOT proven closed at
any AWS-side mechanism** — see §4, which the box cannot see and which therefore stays
open. **F0 remains `PENDING`** — see §5, and note that the reading offered as evidence
toward it is F0's *partner's* direction, not F0's.

**Two corrections to the brief that commissioned this record are in §3 and §6. The
disk contradicted the brief on both, and the disk wins.**

---

## 1. THE INSTALL EVENT — SANAA'S ACT, EXECUTED PERSONALLY

No agent installed anything. `sudo` into `/usr/local/bin` is reserved to Sanaa by
`CLAUDE.md` (FIRST-ACTION RULE, "Reserved to Sanaa"), and this record asserts only what
`/var/log/auth.log` shows. The three lines are the ones frozen in the patch header at
`scripts/auto_stop_patched.sh:52-76`. Verbatim from the authentication log, all three
inside the same second:

```
Sep 03 22:52:11 sudo[911899]: ubuntu : PWD=/home/ubuntu/Certonomous ; USER=root ;
    COMMAND=/usr/bin/cp -a /usr/local/bin/auto-stop.sh /usr/local/bin/auto-stop.sh.bak.20260903T225211Z
Sep 03 22:52:11 sudo[911901]: ubuntu : PWD=/home/ubuntu/Certonomous ; USER=root ;
    COMMAND=/usr/bin/install -o root -g root -m 0755 /home/ubuntu/Certonomous/scripts/auto_stop_patched.sh /usr/local/bin/auto-stop.sh
Sep 03 22:52:11 sudo[911903]: ubuntu : PWD=/home/ubuntu/Certonomous ; USER=root ;
    COMMAND=/usr/bin/env DRY_RUN=1 /usr/local/bin/auto-stop.sh
```

The order is backup, install, dry run — the header's order, unmodified. Nothing else
ran under `sudo` in that second.

---

## 2. THE INSTALLED FILE, MEASURED

| Reading | Value |
|---|---|
| `md5sum /usr/local/bin/auto-stop.sh` | **`b2af2e5a6d4f05003cc0b106a3b90d54`** |
| the patch, per board 52's pre-install reading | `b2af2e5a6d4f05003cc0b106a3b90d54` — **EQUAL** |
| the OLD live file, per board 52's pre-install reading | `7c958c0acceabf988052d6b639023bbc` — **NOT equal** |
| `git cat-file -p 696dba49:scripts/auto_stop_patched.sh \| md5sum` | **`b2af2e5a6d4f05003cc0b106a3b90d54`** — EQUAL to the installed file |
| byte diff, committed blob vs installed file | **IDENTICAL** (`diff` exit 0) |
| `git cat-file -p HEAD:scripts/auto_stop_patched.sh \| md5sum` | `b2af2e5a6d4f05003cc0b106a3b90d54` — worktree has **not** drifted from HEAD here (L-476 check made, negative) |
| owner / group / mode | **`root` / `root` / `0755`** — as the install line specified |
| size | **43,957 B** — equal to the committed blob's 43,957 B |
| birth / modify time | 2026-09-03 22:52:11 UTC |

**The installed file equals the patch, and equals the committed blob at `696dba49`, not
merely the worktree copy.** The hash was taken against the object store, so a worktree
edit could not have produced a false agreement.

Commit `696dba49` read back from `git log` by its own subject line, not carried from a
variable (L-479):

> `696dba492491e2c9ee0db2c445f2965b2ef88d7e` 2026-09-03 16:26:30 +0000
> *auto-stop: see containerized solves, queue chains and live run trees -- the
> 02:25:05Z poweroff that killed 15.6 core-hours of DAFoam*

### The rollback path is real

| File | md5 | mtime |
|---|---|---|
| `/usr/local/bin/auto-stop.sh.bak.20260903T225211Z` | **`7c958c0acceabf988052d6b639023bbc`** | Aug 18 15:49 (preserved by `cp -a`) |
| `/home/ubuntu/Certonomous/scripts/auto-stop.sh` (tracked old copy) | `7c958c0acceabf988052d6b639023bbc` | — |
| `/usr/local/bin/auto-stop.sh.orig-20260730` | `e40ae4e5f7923c03e298e82b300daaf4` | Jul 30 14:59 |
| `/usr/local/bin/auto-stop.sh.orig-20260812` | `e40ae4e5f7923c03e298e82b300daaf4` | Jul 28 05:32 |

**The backup equals the OLD live file byte for byte.** Board 52 recorded that no
`.bak.*` existed before this install; one exists now, it is the right bytes, and the
header's rollback line (`sudo install … <the .bak file> /usr/local/bin/auto-stop.sh`)
would restore exactly what was replaced. Two older `.orig-*` snapshots predate this
lineage and are a different, 640-byte script; they are not a rollback target for the
current file and are recorded here only so a later reader does not mistake them for one.

---

## 3. THE WITNESS LINES — VERBATIM, AND EXACTLY WHAT THEY DO AND DO NOT SHOW

The dry run, verbatim from `/var/log/syslog`:

```
2026-09-03T22:52:12.091610+00:00 ip-172-31-43-247 auto-stop: [DRY_RUN] ALIVE: solver or mesher running (buoyantBoussinesqSimpleFoam, pid 342276)
```

and — stronger, and not in the brief because it had not happened yet — the **first
real, non-dry-run invocation of the installed patched file by root cron**, 169 seconds
later:

```
2026-09-03T22:55:01.204548+00:00 ip-172-31-43-247 CRON[914076]: (root) CMD (/usr/local/bin/auto-stop.sh)
2026-09-03T22:55:01.454067+00:00 ip-172-31-43-247 auto-stop: ALIVE: solver or mesher running (buoyantBoussinesqSimpleFoam, pid 342276)
```

pid 342276 is heat-transfer's containerless 8-rank `T3_runs/R_fx` solver. It was
observed only; nothing was signalled.

### ⚠ CORRECTION 1 — THIS SOLVER WAS NEVER THE BLIND SPOT

The brief calls pid 342276 *"the precise blind spot that powered the box off
mid-campaign."* **The disk says otherwise, and the disk wins.**

- `buoyantBoussinesqSimpleFoam` is in the **OLD** script's clause-(1) `SOLVERS` list —
  `scripts/auto-stop.sh:98`, and the old script contains the name twice.
- The old script **did** see this exact pid, repeatedly, up to the last invocation
  before the install: `2026-09-03T22:50:01` … `auto-stop: ALIVE: solver or mesher
  running (buoyantBoussinesqSimpleFoam, pid 342276)`, and identically at 22:45, 22:40,
  22:35, 22:30, 22:25, 22:20, 22:15, 22:10, 22:05 and 22:00.
- The 02:25:05Z hole was **containerized** work, not containerless. The patch's own
  header (`scripts/auto_stop_patched.sh:80-99`) records it: two Docker containers,
  `a1wr_sweep_C_…` and `a1wr_sweep_I_…`, both `Finished 2026-09-03T02:25:05.6…Z`,
  **`Exit 143` = 128+15 = SIGTERM** — killed *by* the poweroff, 7h49m into a 10.33 h
  budget. Clause (1) reads host `/proc`; that is why the patch adds clause (4) (docker)
  and clause (6) (the run-tree backstop).

**So what the ALIVE lines actually witness is that the patched script did not REGRESS
clause (1)** — the branch the old script already passed on this same pid. That is worth
having and it is not nothing: an install that broke the branch which does work would be
worse than no install. But it is **not** a witness of the new clauses.

### The new clauses are unexercised in production, by construction

`keep()` is `touch "$MARKER"; say "ALIVE: $1"; exit 0` (`scripts/auto_stop_patched.sh:293`)
— it **exits**. Clause order is (0) `:298`, (1) `:309`, (2) `:339`, (3) `:380`,
(4) `:471`, (5) `:563`, (6) `:692`. While any host solver is up, clause (1) fires and
the script exits before clauses (4), (5) and (6) are ever reached. `docker ps` is
**empty** right now, so clause (4) has nothing to see even if it were reached.

**Therefore: clauses (4), (5) and (6) — the three clauses that address the actual
02:25:05Z defect — have NO production witness on this box as of this record.** Their
support is board 52's construction argument plus the sandboxed control suite, and
nothing on the live path. This is named here rather than left for a later reader to
discover.

---

## 4. WHAT INVOKES IT — AND THE HALF I COULD NOT SEE

### The root cron entry names the replaced path. Measured, not inferred.

Root's crontab file (`/var/spool/cron/crontabs/root`) is **not readable without
`sudo`**, and I did not attempt to read it with one. It was not needed: cron logs every
command it runs, and I am in group `adm`, so `/var/log/syslog` is readable. It shows,
every five minutes without a gap across the last hour:

```
CRON[914076]: (root) CMD (/usr/local/bin/auto-stop.sh)
```

**The invoked path is `/usr/local/bin/auto-stop.sh` — literally the path that was
replaced.** Not a copy, not a wrapper, not a differently-named script. Cadence `*/5`
(observed 22:00, 22:05, 22:10, 22:15, 22:20, 22:25, 22:30, 22:35, 22:40, 22:45, 22:50,
22:55 — twelve consecutive, no miss). Same entry visible in `journalctl -u cron`.

The dead-limb failure mode does **not** apply here: the file that was installed is the
file that is being executed, and the 22:55:01Z line above is the installed file's own
output under that invocation.

### Everything else on the box is clear

- `crontab -l` (user `ubuntu`): four entries — `demo_servers.sh`, `queue_runner.sh`
  ×2, `index_autoclear.sh`. **None names auto-stop.**
- `/etc/crontab`: stock Debian `run-parts` lines only.
- `/etc/cron.d/`: `e2scrub_all`, `sysstat`, `.placeholder`. **None names auto-stop.**
- `/etc/cron.hourly|daily|weekly|monthly`: stock packages only (`apport`, `apt-compat`,
  `dpkg`, `logrotate`, `man-db`, `sysstat`, `e2scrub`). **None names auto-stop.**
- `grep -rl "auto-stop" /etc` → **no match anywhere in `/etc`.**
- `systemctl list-timers --all` → 17 timers, all stock (`sysstat`, `fwupd-refresh`,
  `dpkg-db-backup`, `logrotate`, `man-db`, `apt-daily*`, `motd-news`,
  `update-notifier-*`, `systemd-tmpfiles-clean`, `e2scrub_all`, `fstrim`,
  `apport-autoreport`, `snapd.snap-repair`, `ua-timer`). **None activates auto-stop or
  any stop/shutdown unit.**
- `grep -rl "auto-stop\|auto_stop" /etc/systemd /lib/systemd/system /run/systemd/system`
  → **no match.**
- No `/etc/rc.local`. `/etc/profile.d/` holds locale, byobu, cloud-init, gawk and
  OpenFOAM selector scripts only.
- `hibinit-agent.service` is `enabled` but `inactive dead`. It is EC2's hibernation
  **setup** agent; it configures swap for hibernation and does not initiate stops.
- Instance lifecycle from IMDS: **`on-demand`** — this is not a Spot instance, so Spot
  interruption is excluded as a stop mechanism.

**One invoker, one path, and it is the installed path.**

### ⛔ THE HALF THIS BOX CANNOT SEE — AN AWS-SIDE STOP IS NOT EXCLUDED

I could not determine whether a second, AWS-side stop mechanism exists, and I will not
report an absence I was not equipped to see (`CLAUDE.md` rule 3's principle: *a zero
from a reader not shown able to see a non-zero is not evidence*).

What blocks it, measured:

- **No AWS CLI**: `which aws` → not found.
- **No credentials file**: `/home/ubuntu/.aws` does not exist.
- **No IAM instance role**: IMDS `latest/meta-data/iam/security-credentials/` returns
  **HTTP 404**. The instance carries no role, so it has no AWS API identity at all.

The box therefore **cannot query** CloudWatch alarms, EC2 instance attributes,
EventBridge rules, Auto Scaling actions, or any Instance Scheduler. A CloudWatch alarm
with a `StopInstances` action, an EventBridge scheduled stop, or an
`InstanceInitiatedShutdownBehavior` setting would all be entirely untouched by this
install and would still power the box off, and **none of them would leave a trace here
before the fact.**

**What would settle it**, from a credentialed shell or the console, region **`us-east-2`**,
instance **`i-0e417e686a5a6ac1a`**:

1. `aws cloudwatch describe-alarms --region us-east-2` — look for any alarm whose
   `AlarmActions` / `OKActions` / `InsufficientDataActions` contain `…:ec2:stop`.
2. `aws ec2 describe-instances --instance-ids i-0e417e686a5a6ac1a --region us-east-2
   --query 'Reservations[].Instances[].{ISB:InstanceInitiatedShutdownBehavior,Hib:HibernationOptions}'`.
3. `aws scheduler list-schedules --region us-east-2` and `aws events list-rules --region us-east-2`
   — an EventBridge scheduled `StopInstances`.
4. `aws autoscaling describe-auto-scaling-instances --instance-ids i-0e417e686a5a6ac1a --region us-east-2`.

**Until one of those is run, the AWS-side entry point is `PENDING`, not clear.**

### THE HONEST FORM OF THE CLAIM

> **The wrongful-stop class is closed at the root cron entry point.** The invoking
> entry names the installed path, the installed path is the patch bit for bit, and the
> patch can only make the box harder to stop. **It is NOT closed at the AWS control
> plane**, which this box has no credentials to inspect, and **the new clauses (4)/(5)/(6)
> that address the actual 02:25:05Z container hole have no production witness yet.**

This is a **partial fix, recorded as one.**

---

## 5. F0 — READ FROM ITS OWN REGISTRATION, AND IT STAYS `PENDING`

F0's registered text is control `F0` of `scripts/test_auto_stop_liveness.py`:

- **Body**, `:779-785` — `def F0(tmp, sb, procs):` calls **`needs_quiet_box()` as its
  first statement**, then spawns the *identical* probe binary under the basename
  `notASolverAtAll` and runs the script.
- **Registered expectation**, in the frozen control table at `:848` —
  `("F0  clause(1) same binary, other name     ", "IDLE",  F0)`. **The expectation is
  `IDLE`.**
- **Its flip-table partner**, `:867` — `("F1", "F0", "clause (1) solver basename match")`.
  F1 (`:847`) expects **`ALIVE`**, using the same binary under `SOLVER_PROBE_NAME =
  "simpleFoam"` (`:109`). The table's own rule: *"A pair whose two halves AGREE is
  REFUSED even if both individually met expectation."*
- **`needs_quiet_box()`**, `:624-629`, raises `Skipped` with the reason: *"a real solver
  is running on this box …; clause (1) reads the real /proc and cannot be sandboxed, so
  an IDLE-half control here would be measuring the box, not the patch."*

### ⚠ CORRECTION 2 — THE WITNESS IS F0's PARTNER, NOT F0

The brief states that F0 *"was waiting on a live-trigger witness"* and that *"a DRY_RUN
ALIVE reading on a real containerless solver is evidence toward it."* **F0's registered
text says the opposite.**

F0 is the **IDLE half**. An `ALIVE` reading is the **F1 direction**. Worse than merely
irrelevant: a busy box is the precise state under which F0's own precondition
**refuses to run it at all**. The 22:52:12Z and 22:55:01Z lines are field evidence for
the clause F1 tests — clause (1) matching a real solver basename — and they are the
condition that makes F0 unrunnable.

Answering the brief's question directly: F0's registered condition requires **(b)** —
the complementary direction, that the script does **not** hold the box when the only
candidate is a renamed non-solver. **A `DRY_RUN` on a busy box cannot show it**, and
this record does not pretend it did. Reading it the other way would be exactly the
planted-zero shape this lab refuses: **seeing the reader report a non-zero does not
prove it can report a zero.**

**F0: `PENDING`.**
**What remains, named:** a quiet box — no process whose `basename(/proc/PID/exe)` is in
the 22-name `SOLVERS` list — for long enough for the trigger to fire.

**The trigger is armed and alive.** `scripts/f0_window_trigger.sh`, **pid 452822**,
armed 2026-09-03T185205Z, artifact
`verification/runs/AUTOSTOP_LIVENESS/F0_window_trigger_2026-09-03T185205Z.txt`. Poll
60 s, 3 consecutive quiet polls required, deadline 28,800 s → expires
**2026-09-04T~025205Z**. Its last poll, 2026-09-03T225333Z: *"alive …, waiting: pid
342276 is buoyantBoussinesqSimpleFoam."* It refuses rather than reports if the window
never opens, and its `on_exit` handler writes a `NOT A RESULT` line so a dead trigger
is readable as dead.

---

## 6. THE WRONGFUL-STOP INCIDENTS — FOUR, NOT ONE, AND THEY ARE NOT MERGED

The brief asked which incident(s) the record actually holds. It holds **four distinct
events**, each with its own artifact. They are listed separately because merging them
would misattribute a mechanism.

| # | Timestamp (UTC) | Mechanism | Record |
|---|---|---|---|
| 1 | **2026-07-30**, box down 10:40 | a host idle detector not recognising a running solver | `docs/LESSONS.md:6874` — *"recorded here on 2026-07-30 and demonstrated again by this loss"*; `last -x`: `shutdown system down … Thu Jul 30 10:40 - 14:46 (04:06)`. `/usr/local/bin/auto-stop.sh.orig-20260730` (mtime Jul 30 14:59) corroborates a repair made right after. |
| 2 | **2026-08-12 15:35** | `auto-stop: idle 30min, shutting down` — killed a tmux session | quoted in both scripts' headers: `scripts/auto-stop.sh:14`, `scripts/auto_stop_patched.sh:14` |
| 3 | **2026-08-17 17:45:14** | clause (3): the control-room transcript directory was migrated; the **old directory still existed**, so `find` succeeded, matched nothing recent, and an occupied box read as idle. **Five agents were working.** | `docs/LESSONS.md:4438`, under **L-93** (`docs/LESSONS.md:4396`). `last -x`: `shutdown system down … Mon Aug 17 17:45 - 18:07`. |
| 4 | **2026-09-03 02:25:05** | clause (1) reads host `/proc` and could not see **containerized** work | `docs/LAB_STATE.md:24430`; **L-456** (`docs/LESSONS.md:~21889`); commit `696dba49`'s subject; `scripts/auto_stop_patched.sh:80-99`. `last -x`: `shutdown system down … Thu Sep 3 02:25 - 15:34 (13:09)`. Cost: **15.6 core-hours of DAFoam** (per `696dba49`); A1WR Stage 2's 19-point in-memory chain died with the process. |

The chief's cited 02:25Z incident and the supervisor's remembered 2026-07-30
mid-campaign power-off are **incidents 4 and 1** — two different events, four months
of different mechanisms apart. This record cites them separately.

### The 02:25:05Z line, verbatim from `/var/log/syslog`, and its already-known defect

```
2026-09-03T02:20:01.311072+00:00 CRON[347091]: (root) CMD (/usr/local/bin/auto-stop.sh)
2026-09-03T02:20:04.758302+00:00 auto-stop: idle 29min, under threshold 30min -- no action
2026-09-03T02:25:01.796717+00:00 CRON[348138]: (root) CMD (/usr/local/bin/auto-stop.sh)
2026-09-03T02:25:05.239475+00:00 auto-stop: idle 34min, shutting down
2026-09-03T02:25:05.259503+00:00 auto-stop: idle 34min, under threshold 30min -- no action
2026-09-03T02:25:05.427805+00:00 systemd[1]: Stopping finalrd.service - Create final runtime dir for shutdown pivot root...
```

The contradictory pair 20 ms apart is **not** a second stop mechanism and **not** a new
finding: `shutdown -h now` schedules the halt and returns, so control fell through to
the final `say`. It is already diagnosed and fixed in the installed file — the comment
and the `exit 0` at `scripts/auto_stop_patched.sh:765-776`. It is transcribed here only
so a future reader reconstructing the poweroff is not misled by the second line, which
is false on its own terms (34 is not under 30).

---

## 7. WHAT THIS RECORD CLAIMS, AND WHAT CARRIES WHICH PART

**Claimed, on measurement:**

1. The patched script is **installed** at `/usr/local/bin/auto-stop.sh`, root:root 0755,
   43,957 B, md5 `b2af2e5a…`, byte-identical to the committed blob at `696dba49`. §2.
2. **Sanaa executed the install personally**, at 2026-09-03T22:52:11Z, in the header's
   order. §1.
3. A **rollback path exists** and is the correct bytes: the `.bak.20260903T225211Z`
   backup equals the old live file's md5 `7c958c0a…`. §2.
4. The **root cron entry invokes the installed path** — measured from cron's own log
   lines, twelve consecutive five-minute invocations. §4.
5. The patched file's **clause (1) ALIVE branch is witnessed firing in production**, at
   22:55:01Z, on the containerless solver pid 342276. §3.
6. **No cron entry, systemd timer, systemd unit, or `/etc` file other than root's cron
   invokes auto-stop**; the instance is `on-demand`, not Spot. §4.

**NOT claimed, and stated as open:**

- **The class is not closed at the AWS control plane.** No credentials, no role, no
  CLI. Four named commands would settle it. §4.
- **Clauses (4), (5) and (6) have no production witness.** `keep()` exits at clause (1),
  so they are unreachable while a host solver runs, and `docker ps` is empty. §3.
- **F0 is `PENDING`.** The ALIVE reading is its partner's direction, and F0's own
  precondition refuses it on a busy box. §5.

**Which argument carries which part.** Board 52 established the patch's invariant **by
construction only** — deleted = 0, added = 562, all 216 original lines present in order,
every added line a `say` or a `keep`, so the patch can only make the box *harder* to
stop. That construction argument still carries the **safety** half: it is why installing
this file could not introduce a new way to stop the box, and it covers every clause
including the three with no live witness. The **live witness** added tonight carries a
different and narrower half: it proves the installed bytes **execute**, that root cron
**reaches them**, and that clause (1) **did not regress**. Neither argument reaches
clauses (4)/(5)/(6) in production, and neither reaches the AWS control plane.

---

**Compute:** zero. No solver launched, no process signalled. `JF1G_P1_C2` (pid 491048)
and the foreign heat-transfer solver (pid 342276) were observed only.

**Filing:** `verification/runs/AUTOSTOP_LIVENESS/` per `FILING_CHARTER.md` **R6** — run
outputs under `verification/runs/<CAMPAIGN>/`, never beside the prose. No scratch path
is cited anywhere in this record (`CLAUDE.md` rule 13).
