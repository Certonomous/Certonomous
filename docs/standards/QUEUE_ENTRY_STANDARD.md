# QUEUE ENTRY STANDARD

**Version 1.0, dated 2026-08-26. Written by a cfd lane on the cfd supervisor's
dispatch.**

**THIS DOCUMENT CREATES A STANDARD. IT RETIRES NOTHING, WIDENS NOTHING AND
AMENDS NOTHING.** Every existing standard, gate threshold, charter clause and
completion rule stands exactly as written. Retiring or widening any of them is
**reserved to Sanaa** (`CLAUDE.md`, FIRST-ACTION RULE, reserved list), and this
lane takes no part of it. Where this standard quotes a standing rule it quotes
it; a quotation is not an extension.

---

## 0. Scope, and the boundary this standard was built inside

A **queue entry** is a JSON file describing **one proposed solver launch**. The
queue is a **passive list**. It is read on demand by
`scripts/queue_entry_check.py`, which validates entries, prints one verdict per
entry, and **exits**.

**There is no daemon and there will be none under this standard.** A proposal
for a self-scheduling launcher that autonomously started solvers was **DENIED by
the permission system**, and that denial stands. This substrate is deliberately
smaller and of a different kind:

* no service loop, no `while True`, no `setsid`, no `nohup`, no backgrounding;
* no watchdog, no restart logic, no cron, no timer;
* **the validator never starts a solver and never launches a run.** The only
  child process it starts is `git`, restricted to `cat-file`, `rev-parse` and
  `ls-tree` by an allowlist enforced at the single call site, so it cannot
  commit, stage, or touch an index.

Presence in a queue directory causes nothing to happen. A human or an agent runs
the validator; a human or an agent, holding the authorisation, runs the launch.

---

## 1. THE CLAUSE THIS STANDARD EXISTS TO CARRY

`docs/charters/SUPERVISION_CHARTER.md` §3 gives each family supervisor four
checks that **may never be delegated**. The fourth reads, in that charter's own
words:

> **Pre-registration presence before compute.** No family compute launches
> without its pre-registration committed. ... The family supervisor checks the
> commit exists, not that somebody meant to write one.

Therefore:

> ### Enqueueing is not authorisation.
>
> **The supervisor's personal check 4 happens at ENQUEUE time.** This
> validator's sha check is a **second, mechanical guard — never a replacement
> for the personal check.** **No entry in a queue directory has been authorised
> by virtue of being there.**

Three consequences, each of which is the standard and not commentary:

1. **A green verdict from the validator is not an approval.** It says the entry
   is well formed and that two git objects exist. It says nothing about whether
   the run should happen, whether the gate is right, or whether anybody read the
   pre-registration. `ACCEPTED` is printed together with that disclaimer, in the
   same accepting branch, so the two cannot be separated by a reader skimming
   output.
2. **The mechanical guard may not be cited as the personal check.** "The
   validator accepted it" is a summary of a machine's read, and
   `SUPERVISION_CHARTER.md` §3 exists because a check whose result is relayed is
   a summary and not a check. Naming the validator in place of the supervisor is
   **permission laundering** (`CLAUDE.md` standing rule 9) and is refused as
   such.
3. **`enqueued_by` is a required field because check 4 has an owner.** The
   entry records who enqueued it, and therefore who is answerable for the
   personal check that accompanied the enqueue. An entry that cannot name that
   person is refused at SCHEMA.

---

## 2. Where entries live

    verification/queue/<team>/<CASE_ID>.json

for the six standing teams, and no other location:

| team | drop path |
|---|---|
| cfd | `verification/queue/cfd/` |
| heat-transfer | `verification/queue/heat-transfer/` |
| ansys-verification | `verification/queue/ansys-verification/` |
| closure | `verification/queue/closure/` |
| dafoam | `verification/queue/dafoam/` |
| verification | `verification/queue/verification/` |

Each directory carries a `README.md` restating the schema and the
enqueueing-is-not-authorisation clause at the point of use, because a rule kept
only in a standard is a rule read once.

**The queue directories ship EMPTY.** The substrate was built with nothing
enqueued in it.

---

## 3. The entry schema

One JSON object per file. **Every field below is required; the validator
REFUSES an entry missing any one of them**, and refuses it by name.

| field | type | rule |
|---|---|---|
| `team` | string | one of the six above |
| `case_id` | string | non-empty; the case or rung the launch belongs to |
| `prereg_commit` | string | **full 40-character lowercase hex sha**. An abbreviated sha is ambiguous, and a freeze cannot rest on an ambiguous referent |
| `prereg_path` | string | repository-relative (no leading `/`, no `..`); the pre-registration **as it exists at that sha** |
| `launch_cmd` | list of strings | **an argv list, never a shell string.** A shell string hides word-splitting, globbing and redirection from every reader of the entry |
| `cwd` | string | **absolute** path of the case directory the argv would run in |
| `ranks` | integer | `>= 1` (a JSON `true` is rejected: `bool` is an `int` in Python and would otherwise pass) |
| `cost_core_min_estimate` | number `> 0` | the pre-registered cost in **core-minutes** = wall s × ranks ÷ 60. `CLAUDE.md` standing rule 12: **every run is costed in its pre-registration**, and an overrun stops the run rather than receiving a new budget |
| `cost_basis` | string | must contain **`not measured`**, and one of **`derived`** or **`reported-by-owner`** |
| `memory_floor_gb` | number `> 0` | RAM the case needs |
| `enqueued_by` | string | who enqueued it — see §1 consequence 3 |

### 3.1 Why `cost_basis` is policed by string content

`docs/charters/COMPUTE_BUDGET_CHARTER.md` §5: **this box cannot read its own
billing.** Any dollar figure originating here is derived from a rate the owner
stated, or reported by the owner, and **is not a measurement**. A cost silently
presented as measured is precisely the shape that charter exists to stop, so the
honesty of the basis is a *validated field*, not a note in a README. The rate on
record is **c7a.4xlarge at $0.0513/core-h** (owner-stated 2026-08-21/22).

### 3.2 A complete entry, one screen

```json
{
  "team": "cfd",
  "case_id": "F17_L2_BASELINE",
  "prereg_commit": "0123456789abcdef0123456789abcdef01234567",
  "prereg_path": "cases/F17_example/PREREGISTRATION.md",
  "launch_cmd": ["mpirun", "-np", "8", "simpleFoam", "-parallel"],
  "cwd": "/home/ubuntu/Certonomous/verification/runs/F17/L2",
  "ranks": 8,
  "cost_core_min_estimate": 480.0,
  "cost_basis": "derived: 60 wall-min x 8 ranks = 480 core-min; $0.41 at the owner-stated $0.0513/core-h, reported-by-owner, not measured (COMPUTE_BUDGET_CHARTER section 5)",
  "memory_floor_gb": 6.0,
  "enqueued_by": "cfd-supervisor"
}
```

---

## 4. Validation. Every one REFUSES with `sys.exit(2)`, naming the check

| # | check | what it does | why |
|---|---|---|---|
| 1 | `SCHEMA` | all fields present, types correct, `launch_cmd` an argv list, `cwd` absolute, `cost_basis` honest | an entry that cannot be read cannot be guarded |
| 2 | `COMMIT-EXISTS` | `git cat-file -e <prereg_commit>^{commit}` | **the commit must exist.** A freeze cites a sha that exists or it cites nothing |
| 3 | `PREREG-AT-COMMIT` | `git cat-file -e <prereg_commit>:<prereg_path>` | **the pre-registration must exist AT that commit.** A sha with no document at it is the laundering shape: a real-looking freeze reference proving nothing, because the document it names was never in the tree the sha fixes |
| 4 | `AGE-GUARD` | refuse if `cwd` is absent, or already contains `0/` or any numeric time directory (`0`, `0.1`, `250`, `1e-05`) | **`CLAUDE.md` standing rule 4.** The completion rule requires every field at `endTime` to be **newer than the case's own `0/T`**; a pre-existing time directory makes that unprovable for the run that would follow. A run is never launched into a tree that already holds an answer |
| 5 | `RANKS` | `ranks >= 1` | a launch with no rank is not a launch |

Exit codes: `0` all accepted, `2` any refusal or a failed selftest, `1` usage.

Checks 2 and 3 do not double-report: a malformed sha is refused once, at
`SCHEMA`, and the git checks stand down rather than adding noise to a refusal
already made.

---

## 5. Instrument rules binding any tool written under this standard

Each was paid for by a **measured** failure in this lab, and each is quoted
here, not invented here.

1. **No `assert` may carry a refusal, a guard, a control or a gate** — `L-332`.
   `python3 -O` and `PYTHONOPTIMIZE=1` **delete every assert from the compiled
   code**, leaving no trace: the function proceeds to the next statement. A
   refusal written as an assert is a refusal *offer*, accepted or declined by an
   interpreter flag the runner usually does not know they are choosing. Measured
   on a cfd guard: refused under `python3`; under `-O`, **proceeded to
   `git add -A` on the shared tree**. Every refusal is a `raise` or a
   `sys.exit(2)`.
2. **The selftest runs under `python3 -O`, and every refusal must STILL FIRE.**
   "The selftest passes under `-O`" is the **weak** test — a stripped selftest
   passes by doing nothing. The strong test is that each *refusal* is still
   observed. In addition the tool **parses its own AST and refuses if a single
   `ast.Assert` node exists**, and the AST counter is itself shown able to count
   a planted assert, so its zero is a reading rather than a blind spot.
3. **Never an unconditional success print.** Every success line is emitted from
   **inside the branch that verified the thing it claims**, so removing a check
   removes its claim. Measured: a cfd instrument printed `PLANTED CONTROL
   PASSED` and `SELFTEST PASS` under `-O` on an estimator returning zeros — it
   certified a pass that never ran, which is standing rule 3's failure reached
   through the interpreter.
4. **Read-only git, enforced rather than intended.** No commit, no staging, no
   index, no `git add` in any form. The allowlist is `cat-file`, `rev-parse`,
   `ls-tree`, checked at the single call site, and a write subcommand raises.
5. **A zero needs a live planted control** — `CLAUDE.md` standing rule 3. Every
   refusal in §4 has a planted entry shaped exactly like the failure it catches;
   each must fire, and then **the owning guard is mutated to a no-op and the
   control must flip**. A refusal that survives its own guard's removal is not
   coming from the guard it is credited to.
6. **Any sweep is enumerated with `git ls-tree -r HEAD --name-only`, never
   `git ls-files`**, and carries a planted control proving the enumeration can
   see a known member. Files landed by the private-index protocol have no
   shared-index entry, so `git ls-files` misreports them.

---

## 6. What this standard does NOT do

* It does not authorise any run. See §1.
* It does not create, widen, retire or reinterpret any gate, threshold,
  completion rule or charter clause.
* It does not replace `docs/standards/RUN_LOG_STANDARD.md`,
  `docs/standards/MONITOR_STANDARD.md` or any pre-registration requirement; an
  entry is an intent to launch, and every downstream record is still owed in
  full.
* It does not schedule, order, prioritise or start anything. There is no
  ordering semantics in this standard at all: the queue is a set of proposals,
  not a run order.

---

## 7. Provenance

* `docs/charters/SUPERVISION_CHARTER.md` §3, check 4 — the undelegable
  pre-registration check, quoted in §1.
* `CLAUDE.md` standing rule 2 (pre-registration frozen by sha), rule 3 (planted
  zero), rule 4 (strict completion rule and the age guard), rule 9 (permission
  laundering), rule 12 (core-minutes, cost_basis honesty), rule 13 (the
  scratchpad is not a handoff channel — hence a queue under `verification/`, not
  under a scratch path).
* `docs/charters/COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own
  billing.
* `docs/LESSONS.md` L-332 — no `assert` carries a guard.
* Implementation: `scripts/queue_entry_check.py`; per-team READMEs at
  `verification/queue/<team>/README.md`.

---

## CROSS-REFERENCE — 2026-08-27 (a POINTER, not an amendment)

**No clause of this standard is edited, retired or widened by this note, and none above it
has moved: lines whose number changed above this section: 0.** Amending this document is
**reserved to Sanaa** (`CLAUDE.md`, FIRST-ACTION RULE). This is a signpost so a reader of the
entry contract finds a validator behaviour that is not described above.

- **`docs/standards/QUEUE_ENTRY_TEAM_BINDING.md`** (spec, frozen `b23b5638`, amended v1.1
  2026-08-27) and **`docs/standards/QUEUE_ENTRY_VALIDATOR_RULINGS.md` → R-TEAM-BINDING**
  (cfd-supervisor, `[lab-attributed]`, **Sanaa may overrule**): `scripts/queue_entry_check.py`
  now also refuses an entry whose `team` field disagrees with the team directory it sits in,
  and — under the opt-in flag `--require-binding` only — an entry whose location makes that
  check impossible. Both are **tooling-correctness clauses**: they refuse an entry that
  contradicts **its own declared field**, add a refusal reason to a mechanism the runner
  already has, and create no new gate on lab process.
- **A correction of fact readers of §-whatever should know:** this standard's description of
  the queue as passive was overtaken on 2026-08-26 by `scripts/queue_runner.py`. See
  **L-348 / D535** and the per-team `verification/queue/<team>/README.md` corrections. That
  discrepancy is **referred, not repaired here** — it is a clause of this standard, and
  clauses are Sanaa's.
