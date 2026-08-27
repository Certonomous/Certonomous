# Queue-runner cap-enforcement clause — pre-registration

**Status: ADVISORY. INERT. OFF. Not switched on, and no agent may switch it on.**

**Owner:** cfd-supervisor (`scripts/queue_runner.py`). **Raised by:** heat-transfer, relayed by the
chief 2026-08-27, ordered by the cfd supervisor to lane R the same day. **Artifact:** a new
enforcement clause in `queue_runner.py`. **This document is the frozen behaviour spec, written
BEFORE the code**, on the model of `docs/standards/RUNNER_GPU_CLAUSE.md` and
`docs/standards/QUEUE_ENTRY_TEAM_BINDING.md`, so the clause cannot be shaped to pass its own test.
It ships an L-314 planted-failure proof driven in **both** directions.

**Predecessor commits:** the miscitation strike `d8d347c3` (parent `3fae5459`) and its scope
narrowing `b3debbd6`, which together removed the false charter attribution from both overrun flag
texts and from `docs/standards/QUEUE_RUNNER.md` while leaving `117bf190`'s and `257d1116`'s
trigger, threshold and field selection untouched. Those commits changed **strings only** — proven
by AST equality against the pre-strike tree with string constants and docstrings normalised away
(`79d936054e8f5fb213581270ed935f48` on both sides) and by 41/41 byte-identical selftest
(verdict, check-name) pairs (`a48f71750c6c52b3b5fde3d9ad872b77`). This document is the enforcement
half those commits name.

---

## 1. The defect

`scripts/queue_runner.py` writes `CAP_OVERRUN.txt` beside a run that has crossed **1.00 × its
entry's `cap_core_min_registered`** and **does not stop the run**. The run continues, unbounded,
until its own launcher or solver ends it.

`docs/charters/COMPUTE_BUDGET_CHARTER.md:197`, verbatim:

> **A budget overrun stops the run. It does not get a new budget.**

`CLAUDE.md` rule 12 repeats it: *"An overrun **stops the run**; it does not get a new budget."*

Every case-insensitive `cap` occurrence in that charter was enumerated — lines **138, 165, 180,
190, 260, 282, 285** (seven; 138 "A new capability", 190 "Capacity is audited", 260 "capture" are
not budget caps at all) — and **none carves out a report-only cap**. The charter's single *"Not
enforced mechanically"* line (`:363`) names its own three subjects — the measured-versus-estimated
`cost_basis` discipline, the waste split, and the estimate-versus-actual grading — and calls them
*"review disciplines"*. **It does not mention caps.** It governs the calibration discipline.

So enforcement is not a new gate this clause invents. **It is rule 12, which already binds, being
implemented in the one place that can act on it.** That is why this clause is admissible at all.
It is **not** why it may be turned on; see §7.

**What enforcement is today, and it is an accident:** a case is stopped at its cap only if its own
launcher happens to wrap the solver in a `timeout` sized to the cap. `T3_R_ff` does. Cases whose
launcher does not, do not stop. A budget rule enforced by whichever launcher happened to be
written carefully is not enforced.

---

## 2. Scope, and what this clause is NOT about

**This clause governs a case's OWN registered cap and nothing else.**

- It fires **only** on an entry carrying a numeric `cap_core_min_registered > 0`.
- It **never** fires on `cost_core_min_estimate`. The 1.10 × estimate branch
  (`ESTIMATE_OVERRUN.txt`) keeps its present trigger, threshold and report-only behaviour,
  **untouched by this clause**, and an entry with no registered cap is never killed for any reason
  this clause knows about.
- **An estimate overrun is not a cap breach and must never be recorded as one.** As of 2026-08-27
  every `CAP_OVERRUN.txt` on disk (F20, F18, F16b, D14M, T5_CUBE_c, T4b_IJ_m, VMFL064-R2) carries
  the **pre-fix** wording `> 1.10 x registered` — the estimate trigger — inside a file named
  `CAP_OVERRUN.txt`. They are **fossils of a field-selection defect already repaired at HEAD** by
  `117bf190` (key on `cap_core_min_registered`, else name the estimate as an estimate) and
  `257d1116` (the re-armed-cwd artefact). They are outside this clause's reach, this clause must
  never be read as retroactively judging them, and **they must not be edited, deleted or
  "corrected"** — they are the record of the defect and of its repair.

- **NO LIVE CAP BREACH MOTIVATES THIS CLAUSE, AND NONE IS CLAIMED.** Measured independently at
  source by heat-transfer and by cfd, 2026-08-27: `T4b_IJ_c` **14.1** core-min against a cap of
  **25** (0.56×); `T4b_IJ_m` **86.3** against **150** (0.58×); `T5_CUBE_c` **16.1** against an
  estimate of 45.6 — an **underspend**, whose 11,433 s spanned a crashed attempt corrected at
  `C-148`; `F16b` **25.7 %** of cap, `F18` **19.8 %**, `F20` **29.2 %**. **No cap was approached
  anywhere, let alone crossed. No registered-cap breach has ever been recorded by this runner.**
  The defect this clause answers is **structural, not incidental**: the rule at
  `COMPUTE_BUDGET_CHARTER.md:197` has no mechanism behind it. An argument from a claimed breach
  would be a worse argument, and is not made here.

- **A cap in a pre-registration is NOT a cap this clause can see, and that is its principal
  coverage limit.** `cap_core_min_registered` is an **optional** entry field, frequently omitted
  even where the case's pre-registration registers caps: `T4b_PREREGISTRATION.md:464` registers
  caps of **25 / 150 / 860** core-min, while the launched entry `T4b_IJ_m_v2.json` carries
  `cap_core_min_registered: null`. The same holds for `T5_C`, `T4b_IJ_c` and `T3_R_ff`. For every
  such entry this clause is **inert by §5's `no-registered-cap` path** — correctly, since it has
  no cap to enforce. **Switching this clause on would therefore enforce nothing for those cases.**
  Raising coverage is a change to what entries **declare** (a `queue_entry_check.py` question, and
  a separate proposal), never a licence for this clause to infer a cap from a pre-registration it
  did not read. **Inferring an unstated cap and killing on it is exactly the failure §5 forbids.**

---

## 3. THE CENTRAL RULE — a cap stop is a TRANSIENT property of a run, never a property of the file

`queue_runner.py` already draws the distinction this clause must land on the correct side of, and
`RUNNER_GPU_CLAUSE.md` §2 already ruled it once for a resource condition:

| outcome | meaning | effect on the entry |
|---|---|---|
| `move_refused()` | the entry is **invalid** — a **permanent** property of the file | **CONSUMED**: moved to `<team>/refused/` |
| `HELD` | the resource is **busy** — a **transient** property of the box | **STAYS QUEUED**, retried next tick |
| **`CAP-STOPPED`** (this clause) | **this launch** spent its registered cap — a **transient** property of the RUN | **launched record kept and annotated; NEVER `refused/`, never deleted, never silently consumed** |

**A cap stop says nothing about whether the entry was valid.** The entry was valid: it was
validated, launched, and it ran. Moving it to `refused/` would assert a permanent defect in the
file on the strength of a transient fact about one execution, and would lose a frozen, costed
registration silently. That is the most expensive failure this runner can have.

**Whether to re-run is the owning team's call, not the runner's.** The runner does not re-queue,
does not raise the cap, and does not decide that a re-run is legitimate.

---

## 4. Behaviour

Clause name **`CAP-STOPPED`**. New runner log event word: `CAP-STOPPED`, plus `CAP-STOP-REFUSED`
for every fail-closed path in §5.

### 4.1 The trigger

For each **current** record in `<team>/launched/*.json` (never an `ARCHIVED_RE` name — the same
current-record rule the cap watch already applies), with no `STATUS` file present and no
`_launch.status_seen_utc` stamp:

```
spend_core_min = (now - _launch.started_epoch) * ranks / 60
```

The clause fires when `spend_core_min > cap_core_min_registered`, i.e. at exactly the same instant
`CAP_OVERRUN.txt` is written today — **1.00 × cap × 60 / ranks seconds elapsed, and not before.**
This clause adds **no new threshold**. It acts on the threshold already pre-registered in the
entry, at the moment the existing watch already recognises.

### 4.2 What it kills — the recorded session, and only that

**A launch record is a historical fact, never a liveness reading.** `launcher.queue.out` records
the **wrapper** the runner launched; the solver runs as a **descendant under a different pid**.
Three pids read out of that log on 2026-08-27 were all already dead.

- The clause kills **`os.killpg(sid, ...)`** where `sid` is **`_launch.sid`**, the session id the
  runner recorded from `os.getsid(pid)` at launch — the session `setsid` created for this launch
  and nothing else.
- It **never** scrapes a pid or a pgid from `launcher.queue.out`, from `runner.log`, from `ps`, or
  from any log. It **never** matches on a command-line pattern; `pkill` and `pgrep` are forbidden
  in this clause (a pattern kill matches the invoking shell itself).
- **Anti-pid-reuse guard, mandatory.** `sid` is a pid and pids are recycled. At launch the runner
  additionally records **`_launch.sid_starttime`** — field 22 of `/proc/<sid>/stat`, the kernel's
  boot-relative start time of that session leader, which is not reusable. Before signalling, the
  clause re-reads `/proc/<sid>/stat` and requires **an exact match**. Any mismatch, or an absent
  field (a record written before this clause existed), is **NO KILL** under
  `CAP-STOP-REFUSED reason=sid-not-ours`.
- It additionally requires `os.getsid(sid) == sid` — the recorded sid is still a live **session
  leader**, not merely a live pid.

**Signal sequence:** `SIGTERM` to the process group, then a grace period (default **60 s**,
constant, not configurable per entry), then `SIGKILL` to the same group if `os.getsid(sid)` still
resolves. Both signals are logged with the sid.

**It never kills anything it did not launch.** The clause's only input is
`<team>/launched/*.json`; no other process on the box is reachable from its code path.

### 4.3 What it writes

1. **`CAP_STOPPED.txt`** beside the run, in `_launch.cwd`, naming — as the existing flags do — the
   launch it judges (`launch_utc`, `pid`, `sid`, `started_epoch`), the **registered cap**, the
   **measured spend in core-minutes** and its arithmetic (`elapsed s × ranks ÷ 60`), the signals
   sent and their times. This is the durable record.
2. **`STATUS.<case_id>`** with a `CAP-STOPPED` reason, **only if no `STATUS.<case_id>` already
   exists.** The wrapper writes `STATUS` on its own exit and may win the race after `SIGTERM`; the
   runner must never overwrite a `STATUS` the wrapper wrote. When the wrapper's `STATUS` is
   present, `CAP_STOPPED.txt` alone carries the record and says the wrapper's `STATUS` was kept.
3. **`_launch.cap_stopped`** appended to the launched record: `{utc, cap_core_min_registered,
   spend_core_min_measured, sid, sigterm_utc, sigkill_utc|null, status_written_by:
   "runner"|"wrapper"}`. Under **L-342** this is an **INFRASTRUCTURE** field and is added to the
   record's existing `infrastructure` class list, never to `physics_critical`.
4. One `runner.log` line: `CAP-STOPPED team=<t> case=<id> sid=<sid> cap=<c> spend=<s> core-min`.

**The record stays in `launched/`. Nothing is moved to `refused/`. Nothing is deleted.**

### 4.4 The verdict, and the limit of what bookkeeping may do

**A cap stop is `NOT A RESULT` on a registered cap** (the chief's ruling 10 of 2026-08-27, on
`T3_R_ff`). It is **not** a physics failure and must never be reported as one.

And the mechanism matters, because **bookkeeping must not CREATE physics any more than it may void
it** (L-342, Sanaa 2026-08-26). The run is `NOT A RESULT` because it was **terminated before
completion** and therefore fails standing rule 4 independently — no `End` line, last time ≠
`endTime`, fields absent — which any grader establishes from **the case's own log and field files**
without reading a single runner artifact. `CAP_STOPPED.txt` **explains why the run stopped; it does
not constitute the verdict**, and a grader must never issue `NOT A RESULT` on the strength of the
runner's flag alone. Conversely, if a case somehow satisfies rule 4 in full before the signal
lands, the flag does not retract that: the physics artifacts stand and the flag is a cost record.

### 4.5 What it never does

Never deletes, never re-queues, never raises a cap, never edits an entry's registered values, never
writes into a `physics_critical` field, never touches a case's `0/`, time directories or fields,
**never edits, stages or commits in git**, never signals the runner's own process or any process
outside a recorded launch session, and never reads a pid from a log.

---

## 5. FAIL CLOSED — and closed here means DO NOT KILL

**Killing on an unreadable measurement is the worst available failure.** Every one of these is
**NO KILL**, each logged under its own distinct `CAP-STOP-REFUSED reason=` so the reasons cannot be
confused with one another or with a pass:

| condition | reason word | why |
|---|---|---|
| `cap_core_min_registered` absent / non-numeric / ≤ 0 | `no-registered-cap` | nothing to enforce; the estimate branch is unaffected |
| `_launch.sid` absent, non-integer, `≤ 1`, or the `-1` sentinel `launch()` writes when the process finished before `os.getsid` | `no-sid` | **the sid was never recorded**; there is nothing this clause is entitled to signal |
| `_launch.started_epoch` absent or non-numeric | `spend-unmeasurable` | the spend cannot be measured |
| `ranks` absent or non-positive | `spend-unmeasurable` | the core-minute conversion has no rank count |
| `/proc/<sid>/stat` unreadable, or `sid_starttime` absent or mismatched | `sid-not-ours` | a recycled pid; the session may belong to somebody else |
| `os.getsid(sid) != sid` | `sid-not-a-session-leader` | the recorded sid is not the leader of a live session |
| `STATUS.<case_id>` present, or `_launch.status_seen_utc` stamped | `run-finished` | the launch is over; a later missing `STATUS` is a re-armed cwd, not this launch running on |
| the record's name matches `ARCHIVED_RE` | `superseded-record` | a retired record never judges a live cwd |
| **`enforce` is False (the default)** | `enforcement-off` | §7 |

**A failed measurement must never be readable as "over cap."** A zero — or a silence — from a
reader not shown able to see a non-zero is not evidence (standing rule 3). Each of these paths is a
planted control in §6.

---

## 6. Selftest, and the L-314 planted-failure proof in BOTH directions

Scratch root only. Deterministic: the clock is injected as `cap_watch` already injects it; the
wrappers are `bash -c 'sleep N'` in a scratch cwd, never a solver; **no control signals anything
outside a session the selftest itself launched through the real `launch()` path.**

**A selftest that only shows the kill working cannot detect a runner that kills everything.**
Controls 1 and 2 are the pair that matters and neither is optional.

| # | setup | expected |
|---|---|---|
| **1** | entry with a cap, wrapper that **ignores** the cap (`sleep 600`), clock driven past `cap × 60 / ranks`, `enforce=True` | **KILLED**: `os.getsid(sid)` no longer resolves; `CAP_STOPPED.txt` present naming this launch, the cap and the measured spend; `STATUS` carries `CAP-STOPPED`; **the record is still in `launched/` and `refused/` is untouched** |
| **2** | entry with a cap, wrapper **inside** the cap, clock at `cap − 1 s`, `enforce=True` | **UNTOUCHED**: session still alive, no `CAP_STOPPED.txt`, no `STATUS` written by the runner, no signal logged |
| **3** | entry with **no** `cap_core_min_registered`, elapsed far past 1.10 × estimate, `enforce=True` | **NO KILL**, `CAP-STOP-REFUSED reason=no-registered-cap`; `ESTIMATE_OVERRUN.txt` written exactly as today |
| **4** | over cap, `_launch.sid` removed (and separately, set to `-1`) | **NO KILL**, `reason=no-sid`, session still alive |
| **5** | over cap, `_launch.started_epoch` removed | **NO KILL**, `reason=spend-unmeasurable`, session still alive |
| **6** | over cap, `_launch.sid_starttime` mutated to a wrong value | **NO KILL**, `reason=sid-not-ours`, session still alive |
| **7** | over cap, `STATUS` present | **NO KILL**, `reason=run-finished`, however late the clock is driven |
| **8** | over cap, wrapper ignoring the cap, **`enforce` left at its default** | **NO KILL**: session still alive, no `CAP_STOPPED.txt`, only `CAP_OVERRUN.txt` — **this is the off-by-default control** |
| **9** | a live session started by the selftest that has **no record in `launched/`**, present through a full over-cap pass | **alive before and after**; the clause never reaches a session it did not launch |
| **10** | over cap, `launcher.queue.out` **deleted**, `enforce=True` | still **KILLED** — proving the kill uses the recorded sid and not a pid scraped from the log |
| **11** | static: the shipped default of the `enforce` parameter is `False`, **and** `scripts/queue_runner.sh` contains no `--enforce-caps` | both true, or the selftest **FAILS** |

**Planted failures — each must FLIP a named control, proving the guard is load-bearing and
reachable, not merely quiet:**

- **P1 (MANDATORY) — remove the cap comparison, kill unconditionally → control 2 must FAIL**, its
  inside-the-cap session dying. Without P1 the suite cannot distinguish a correct clause from one
  that kills everything, and control 1 alone would pass under both.
- **P2 (MANDATORY) — force `enforce=True` → control 8 must FAIL.** Without P2, control 8 passing
  proves nothing: a wrapper that happens to exit, or a clause that happens not to fire, looks
  identical to an off switch. **The off-state must be shown to be what held the run, not an
  accident.**
- **P3 — treat an unmeasurable spend as over cap → control 5 must FAIL** (the session dies).
- **P4 — skip the `sid_starttime` check → control 6 must FAIL.**
- **P5 — read the pid from `launcher.queue.out` instead of `_launch.sid` → control 10 must FAIL**
  (nothing is killed once the log is gone).
- **P6 — implement the stop as `move_refused()` instead of an annotation → control 1's "record
  still in `launched/`, `refused/` untouched" condition must FAIL.** This is §3's rule under test;
  without it, "never consumed" is an untested claim.

**L-314 Instance 1 applies to the harness:** `set -e` is not in force in the agent Bash context, so
the selftest must return a **checked exit code** and print a **greppable** result line. A guard
whose failure is only printed is not a gate. The existing `--selftest` already does both and these
controls join it.

---

## 7. ROLLOUT — ADVISORY, INERT, OFF, AND NO AGENT MAY TURN IT ON

**This clause kills running solvers.** That is the whole of why the rollout is written this way.

**D539** (verification, 2026-08-27) is the governing precedent and it is on the point:

> **A checker that refuses a commit is a GATE ON LAB PROCESS, and ADDING a gate is reserved to
> Sanaa exactly as retiring one is** … **NO AGENT MAY FLIP IT.** Not cfd, not this team, not the
> chief. **A measured rate that "looks acceptable" is not an authorisation.**

A daemon that terminates other teams' running solves is at least as consequential as a commit
checker. Therefore:

- **The default is `enforce = False`.** The clause runs, evaluates, and takes the
  `CAP-STOP-REFUSED reason=enforcement-off` path. Nothing is signalled. `CAP_OVERRUN.txt` continues
  to be written exactly as it is today, so **landing this clause changes no observable behaviour on
  this box.**
- **The off-state is proven by a control, not asserted.** Control 8 drives a genuinely over-cap
  wrapper through the real code path with the shipped default and requires it **alive**; planted
  failure P2 flips it. Control 11 additionally asserts the shipped default is `False` and that
  `scripts/queue_runner.sh` — the file the crontab actually executes — carries no `--enforce-caps`.
- **Switching it on is Sanaa's decision alone.** Not cfd's, not the chief's, not verification's.
  **No agent's message is her consent** (`CLAUDE.md` rule 9) — not the chief's escalation, not the
  cfd supervisor's order, and not this document. Implementing rule 12 rather than inventing a new
  gate makes the clause **admissible**; it does not make it **authorised**.
- **It sits on Sanaa's desk beside the daemon-restart rule**, which is where the chief put it.

**HONEST CAVEAT, AND IT IS THE REASON §6 CONTROL 8 EXISTS.** It is not true that a change to
`queue_runner.py` reaches the live daemon only when somebody rules on a restart. `crontab -l`
carries `* * * * * /bin/bash /home/ubuntu/Certonomous/scripts/queue_runner.sh`, and that script
starts a runner whenever the pidfile's process is not alive. If daemon **pid 1120800** dies for any
reason — OOM, `SIGKILL`, an escaping exception — cron brings up a new one **within 60 s running
whatever is on disk**, with nobody ruling on it. **The off-state therefore cannot rest on the
restart gate, on any agent's intention, or on this document.** It rests on the shipped default
being `False` and on that default being driven by a control that a planted failure flips.

**Nothing in this pre-registration touches pid 1120800.** No signal, no kill, no restart is
attempted by the lane that wrote it. A daemon restart is blocked on a classifier denial that is on
Sanaa's desk, and routing around a denial is forbidden.

---

## 8. Compute cost (rule 12)

**Pre-registered cost of the work this document governs: 0.0 core-minutes of solver compute.**

- **This pre-registration:** documentation only. No solver, no mesh, no queue entry. **0.0
  core-min.**
- **The implementation, when written:** code plus `--selftest`. The selftest's wrappers are
  `sleep`/`true` in a scratch root on one rank; the added controls are bounded by their injected
  clock, not by wall time. **Pre-registered estimate: ≤ 2.0 core-minutes per full `--selftest`
  invocation**, cap **6.0 core-minutes**. An overrun stops the run and does not get a new budget.
- **Derived, not measured:** at the recorded c7a.4xlarge rate of **$0.0513/core-h**, a 6.0
  core-minute cap is **$0.0051**. `cost_basis`: **reported-by-owner rate, derived dollars, not
  measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate-versus-actual calibration** is owed at the implementation's completion and lands as a
  row in `docs/COST_CALIBRATION.md` per rule 12.

---

## 9. Freeze

This document is the **frozen behaviour spec**. The implementation is graded against **this file at
its commit sha**, and any departure is disclosed as a **dated amendment appended at the foot**, with
a version bump and the assertion `lines whose number changed above this section: 0` — proven by
`md5` of `head -N` against the pre-amendment blob taken from the **amendment commit's true parent**,
never `HEAD~1` (peers commit constantly and HEAD moves; a `HEAD~1` check comes back vacuous).

**Version 1.0, 2026-08-27.** Written by cfd lane R on the cfd supervisor's order, before any
implementation code existed.
