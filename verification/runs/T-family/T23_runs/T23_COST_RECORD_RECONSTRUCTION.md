# T23 — cost-record reconstruction after the queue runner destroyed the launcher record

**Scope.** The four cases `T23_P305_U{10,20,30,40}` in
`/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/`.

**What this document is.** A re-derivation of the cost record from artifacts that
survive, and an explicit refusal to reconstruct anything the artifacts do not
carry. **A destroyed measurement is not re-created by inference.** Every figure
below is labelled **MEASURED** with the artifact it was read from, or **STILL
VOID**. Nothing here is estimated, interpolated, or scaled from a sibling case.

**Physics is untouched.** See §6.

---

## 1. WHAT WAS DESTROYED, AND BY WHAT MECHANISM

`run_t23.sh` (one copy per case, e.g.
`/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/T23_P305_U10/run_t23.sh`)
captures `rc` on the line immediately after the solver call and writes nine
fields to `STATUS.$NAME` at lines 74–87:

    case= rc= wall_s= ranks= core_min= cap_core_min= timeout_s= capped= solver= end_utc= note=

The queue runner, in the form that launched these four, wrote its **own** line to
**the same path**. Its inner command was (`scripts/queue_runner.py`, pre-repair
form, now at lines 530–532):

    cd '<cwd>' && <argv> > '<launcher.queue.out>' 2>&1; R=$?;
    echo "launcher_rc=$R end=<utc> note=exit-status-of-the-launch-argv-NOT-the-solver-rc" > '<status>'

with `status = cwd / f"STATUS.{case_id}"`. The launch argv is
`["bash", ".../run_t23.sh"]`, so the runner's `echo … >` truncate-write lands
**after** the wrapper's own write and destroys all nine fields.

**The mechanism is not inferred from the file's contents — it is read off the
surviving launcher record.** Each queue entry's `_launch.status_file` names the
colliding path, e.g. for `T23_P305_U10`:

    /home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/T23_P305_U10/STATUS.T23_P305_U10

and the same path appears in the `LAUNCH_LOG.tsv` rows and the `runner.log`
`LAUNCHED` lines. [MEASURED]

**`launcher.queue.out` is 0 bytes on all four cases** [MEASURED, `stat`], so —
unlike `cases/F27_WOMERSLEY_PIPE`, whose same-class loss on 2026-08-28 had a
stdout copy — **there is no second copy of the destroyed text.**

**The defect is repaired and the repair post-dates these runs.** The runner now
writes `STATUS.queue.<case_id>`, a name it owns, so the collision is impossible
by construction (`scripts/queue_runner.py:509`, whose own comment names these
four cases as the measured damage). That repair landed at commit `9e356f09`,
committer date **2026-08-31 20:21:02 +0000** — **two hours and forty-eight
minutes after `T23_P305_U10` launched at 17:33:02Z.** [MEASURED, `git log -1`]
`queue_runner.py` is cfd's instrument; nothing in this document touches it.

---

## 2. WHAT SURVIVES — the exact list of cost-bearing artifacts, per case

Identical set for all four cases; `<C>` is `U10` / `U20` / `U30` / `U40` and
`<D>` is `/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/T23_P305_<C>`.

| # | artifact | what it still carries |
|---|---|---|
| 1 | `<D>/log.solve` | header `nProcs : 1`, `Exec : chtMultiRegionSimpleFoam`; 10 000 `ExecutionTime … ClockTime …` lines; one `End`; zero `FOAM FATAL` |
| 2 | `<D>/run_t23.sh` | `RANKS=1` (:21), `TIMEOUT_S=6000` (:22), `SOLVER="chtMultiRegionSimpleFoam"` (:24) — i.e. the **inputs** to the destroyed `ranks`, `timeout_s`, `cap_core_min` and `solver` fields |
| 3 | `<D>/STATUS.T23_P305_<C>` | the runner's three keys only: `launcher_rc=0`, `end=<utc>`, the self-disclaiming `note=` |
| 4 | `/home/ubuntu/Certonomous/verification/queue/heat-transfer/launched/T23_P305_<C>.json` | `ranks: 1`, `cap_core_min_registered: 100.0`, `cost_core_min_estimate: 30.8`, `cost_basis`, `prereg_commit`, and **`_launch.started_epoch`** — a float launch instant |
| 5 | `/home/ubuntu/Certonomous/verification/queue/LAUNCH_LOG.tsv` lines 253–256 | launch utc, pid, sid, **ranks = 1**, estimate 30.8, prereg sha, status path |
| 6 | `/home/ubuntu/Certonomous/verification/queue/runner.log` lines 8476–8483 | box-busy and MemAvailable at each of the four launch instants |
| 7 | filesystem mtimes | `<D>/0/housing/T` (touched immediately before the solver line) and `<D>/log.solve` (last solver write), both sub-second |

**Absent on all four** [MEASURED, directory listing]: any `rc` file
(`RC.txt`, `RUN_RC.txt`), any `CAP_OVERRUN.txt`, any `ESTIMATE_OVERRUN.txt`,
and **any `START.T23_P305_<C>` file** — see §5.

**A correction to the loss inventory, and it makes the loss smaller than
reported.** Of the eight destroyed fields, **seven have a surviving source
elsewhere** and only one does not:

| destroyed field | recoverable? | from |
|---|---|---|
| `ranks` | **yes** | three artifacts agree: `log.solve` header `nProcs : 1`; `run_t23.sh:21`; launcher record `ranks: 1` (and `LAUNCH_LOG.tsv` column 6) |
| `solver` | **yes** | `log.solve` header `Exec : chtMultiRegionSimpleFoam`; `run_t23.sh:24` |
| `timeout_s` | **yes** | `run_t23.sh:22` — `TIMEOUT_S=6000` |
| `cap_core_min` | **yes** | `6000 × 1 / 60 = 100.0`, and independently `cap_core_min_registered: 100.0` in the launcher record |
| `capped` | **yes, derived** | `capped` is set iff `rc == 124`; the log carries one `End` line and a final `ClockTime` far below 6000 s, so `capped = 0` |
| `rc` | **yes, derived** | one `End`, zero `FOAM FATAL`, last time == `endTime` — the derivation the grading record already makes |
| `case`, `end_utc` | **yes** | directory name; runner `STATUS` `end=` |
| **`wall_s`** | **not as the recorded value** | it is *bracketed* by four independent measurements — §3 |

---

## 3. RE-DERIVATION — `core-minutes = wall seconds × ranks ÷ 60`

### 3.1 RANKS — established, not assumed

**`ranks = 1`, MEASURED, from three mutually independent artifacts**: the
`log.solve` header line `nProcs : 1` (written by the solver itself),
`run_t23.sh:21` `RANKS=1`, and the launched queue entry's `ranks: 1`. Serial, so
core-minutes and wall-minutes coincide here.

### 3.2 WALL SECONDS — which instrument, and why

**`ExecutionTime` is CPU time and is NOT wall time. It is reported below and it
is NOT used as wall.** OpenFOAM prints both on the same line; the wall figure is
**`ClockTime`**, and `ClockTime` is what is used.

`ClockTime` is printed as an **integer number of seconds**, so every per-case
wall figure below carries **± ~1 s** of quantization (visible at `U40`, where
`ClockTime = 1781` reads *below* `ExecutionTime = 1781.16`). ±1 s is ±0.0167
core-min per case.

### 3.3 The four cases

| case | ranks (source) | `ClockTime` (wall, s) | `ExecutionTime` (CPU, s) | **core-min, ClockTime × 1 ÷ 60** | label |
|---|---|---:|---:|---:|---|
| `T23_P305_U10` | 1 (`nProcs`, `run_t23.sh:21`, queue entry) | **1785** | 1784.02 | **29.7500** | **MEASURED** |
| `T23_P305_U20` | 1 (same three) | **1814** | 1813.14 | **30.2333** | **MEASURED** |
| `T23_P305_U30` | 1 (same three) | **1831** | 1829.39 | **30.5167** | **MEASURED** |
| `T23_P305_U40` | 1 (same three) | **1781** | 1781.16 | **29.6833** | **MEASURED** |
| **subset** | | **7211** | 7207.71 | **120.1833** | **MEASURED** |

Source artifact for every value: the final `ExecutionTime = … s  ClockTime = … s`
line of `<D>/log.solve`, immediately above that file's single `End` line.

**Four of four are MEASURED. None is STILL VOID.**

### 3.4 THE LOWER-BOUND CAVEAT — stated, and then MEASURED rather than left as prose

`ClockTime` covers **the solver process only**. The destroyed `wall_s` was
`T1 − T0` around the `timeout "${TIMEOUT_S}s" "$SOLVER"` line
(`run_t23.sh:64–69`), so it additionally included solver process start-up and
teardown; and neither figure includes what `run_t23.sh` does before `T0` (bash
start-up, sourcing the OpenFOAM `bashrc`, the age guard, `cp -r 0.orig 0`,
`touch 0/housing/T`). **The §3.3 figures are therefore a LOWER BOUND on the true
launcher-inclusive cost.**

The size of that gap is not asserted — it is measured, from three further
surviving clocks:

| case | (a) `0/housing/T` mtime → `log.solve` mtime | (b) `_launch.started_epoch` → runner `STATUS` `end=` | (c) launcher overhead before the solve, `started_epoch` → `0/housing/T` mtime |
|---|---:|---:|---:|
| `U10` | 1784.41 s | 1784.32 s | **0.17 s** |
| `U20` | 1813.96 s | 1813.30 s | **0.21 s** |
| `U30` | 1830.10 s | 1830.27 s | **0.22 s** |
| `U40` | 1782.00 s | 1782.25 s | **0.22 s** |
| **sum** | **7210.47 s** = 120.1745 core-min | 7210.14 s | **0.82 s = 0.0136 core-min** |

Column (a) is the closest surviving analogue of the destroyed `wall_s`:
`0/housing/T` is touched at `run_t23.sh:58`, six lines before `T0`, and
`log.solve` is last written by the solver's own `End`. Column (b) spans the whole
launch argv and is quantized by the runner's whole-second `end=` stamp.

**All three clocks agree with `ClockTime` to within 1.6 s per case**, i.e. inside
`ClockTime`'s own ±1 s quantization plus the `end=` truncation. **The excluded
launcher overhead is 0.82 s across all four cases — 0.0136 core-min, or 0.011 %
of the subset figure.** So the lower bound is a lower bound by a measured
0.011 %, not by an unknown amount.

**What is still not recoverable:** the *recorded* `wall_s` integers themselves.
Column (a) reconstructs the quantity to within about a second; it does not
restore the destroyed record, and nothing below claims it does.

---

## 4. THE CAP QUESTION

**Registered cap, from the frozen pre-registration.**
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T23_PREREGISTRATION.md` §5.2,
frozen at commit `fe666fd5d3cf148b1266bf693d1199cec3c7d607`:

| figure | value |
|---|---:|
| per case POINT | 30.8 core-min (**DERIVED**) |
| **per case CAP** | **100.0 core-min — REGISTERED, hard, 3.25 × POINT** |
| subset (4 cases) POINT | 123.2 core-min |
| **subset CAP** | **400.0 core-min — REGISTERED, hard** |

**The frozen file is the file that ran** [MEASURED]: worktree blob
`c341476f3680c14ec593c52d12e49214cf83ebb3`, identical to the blob at
`fe666fd5…:docs/campaigns/T-family/T23_PREREGISTRATION.md` **and** at `HEAD:` the
same path.

**The cap was ENACTED, not merely written**, and the enacting artifact survives
the record loss: `run_t23.sh:22` `TIMEOUT_S=6000` with `RANKS=1`, i.e.
`cap_core_min = 6000 × 1 ÷ 60 = 100.0` — the same 100.0 that the launcher record
carries as `cap_core_min_registered`. **The `timeout` is what would have stopped
the run; the queue runner's `CAP_OVERRUN.txt` only reports.**

**Answer.** Every re-derived figure is inside the registered cap, with wide
margin:

| case | wall s | registered per-case cap | utilisation | over 3600 wall s? |
|---|---:|---:|---:|---|
| `U10` | 1785 | 6000 s / 100.0 core-min | 29.75 % | **no** |
| `U20` | 1814 | 6000 s / 100.0 core-min | 30.23 % | **no** |
| `U30` | 1831 | 6000 s / 100.0 core-min | 30.52 % | **no** |
| `U40` | 1781 | 6000 s / 100.0 core-min | 29.68 % | **no** |
| subset | 7211 | 400.0 core-min | **30.05 %** | — |

**No case exceeded 3600 wall s**; the longest ran 1831 s, 50.9 % of the stall
threshold. The `COMPUTE_BUDGET_CHARTER.md` §2 stall rule matches nothing here, so
**gross and cleaned are identical and no judgement enters the figure.**

**WHAT THIS PROVES AND WHAT IT DOES NOT.**

* **It proves no overrun occurred.** A `timeout 6000s` that fired would have
  produced `rc = 124`, no `End` line, and a final time short of `endTime`. The
  logs carry one `End`, last time `10000 == endTime`, and 10 000 `ExecutionTime`
  lines. The run completed on its own; the cap was never reached, let alone
  exceeded.
* **It does NOT restore the destroyed record.** The fields `cap_core_min`,
  `timeout_s` and `capped` as *written by the wrapper* are gone and stay gone.
  What stands in their place is the same information read off a *different*
  artifact (`run_t23.sh`) plus a derivation from the log. That is weaker
  provenance than a written measurement, and it is labelled as such rather than
  presented as the original.
* **It does NOT make the cap self-policing in the general case.** The cap held
  here because the run finished at 30 % of it. Had a run been capped, `capped=1`
  would have been the field that said so, and that field would have been
  destroyed by the same mechanism.

---

## 5. A SECOND GAP IN THE RECORD, REPORTED RATHER THAN SMOOTHED

The pre-registration §5.4 registers, one-way and before the fact:

> *"a run whose recorded load average at launch shows a saturated box produces a
> COST but NOT a calibration row. … Each launcher writes a `START.<case>` file
> **before** the solver starts, carrying `start_utc`, all three `/proc/loadavg`
> windows and `nproc`."*

**No `START.T23_P305_U*` file exists for any of the four, and `run_t23.sh`
contains no code to write one** [MEASURED, on disk and in the launcher's own
text]. This is a divergence between the frozen text and the launcher actually
used. It is **not** part of the queue-runner loss — the file was never written —
and it is recorded here because it is a second place where a registered
instrument is missing from the record. The frozen document is not edited
(standing rule 6) and the launcher is not retro-fitted.

The graded record `docs/campaigns/T-family/T23_RESULTS.md` §5.2 already evaluated
§5.4's precondition from a **named substitute**, `verification/queue/runner.log`.
That reading is independently re-measured here at lines 8476–8483 of that file:
box busy **11.9 % / 12.7 % / 22.3 % / 25.7 %** (~1.9 / 2.0 / 3.6 / 4.1 of 16
cores), MemAvailable 29.0 / 28.9 / 28.6 / 28.5 GB, at 17:33:02Z / 17:34:07Z /
17:35:12Z / 17:36:17Z [MEASURED]. **The box was not saturated at any of the four
launches**, and the four wall times span only 1781–1831 s, a 2.8 % spread, which
is what a low-contention concurrent set looks like. The substitution is named
rather than silent: it is not the instrument §5.4 registered.

---

## 6. THE PHYSICS IS UNAFFECTED — L-342

**Sanaa's universal rule of 2026-08-26: bookkeeping never voids physics.** The
`_field_classes` block the runner itself wrote into each launched queue entry
classes the destroyed items as **INFRASTRUCTURE**, and states the rule: *"a
missing or inconsistent INFRASTRUCTURE field is a BOOKKEEPING DEFECT reported
beside the verdict and voids only the cost claim; only a PHYSICS_CRITICAL field
may produce NOT A RESULT (L-342)"*.

**The reason the physics stands is specific, and it is that `rc` derives from the
log and not from the destroyed fields.** Every conjunct of standing rule 4 is
evaluable on artifacts the runner never touched:

| conjunct | evidence | reading |
|---|---|---|
| `rc = 0` | `log.solve`: exactly one `End`, **zero** `FOAM FATAL`, last time == `endTime` | **DERIVED-FROM-LOG, never read from `STATUS`** [MEASURED] |
| `End` line | one per case | [MEASURED] |
| last time == `endTime` | time directories are `{0, 10000}`; `endTime` 10000 | [MEASURED] |
| `ExecutionTime` count == `endTime` | **10 000** lines in each of the four logs | [MEASURED] |
| fields present | `10000/{fluid,housing,core}/` | as recorded in `T23_GRADE.txt` |
| **age guard** | `10000/fluid/T` mtime **newer** than that case's own `0/housing/T` on all four | [MEASURED, `st_mtime`] |

`launcher_rc=0` in the surviving `STATUS` line was **not** accepted as `rc` — a
zero there is the exact shape of the `setsid` trap the wrapper exists to avoid,
and the file disclaims itself on its own face. **The verdicts of
`T23_GRADE.txt` / `T23_GRADE.json` are untouched by this document.** What the
record loss voided was the **cost claim**, and only the cost claim.

---

## 7. WHAT THIS DOCUMENT CORRECTS IN THE LEDGER

The existing ledger row `C-20260831T183346.079343Z-d971eca8` in
`docs/COST_CALIBRATION.md` records the T23 actual as **120.1285 core-min**, taken
from the four **`ExecutionTime`** lines, and discloses that choice in its own
text: *"the ExecutionTime basis is used for the ratio because it is the solver's
own figure"*.

**That disclosure is honest and the arithmetic in it is correct. The instrument
is not the one the unit requires.** `CLAUDE.md` rule 12 defines the unit as
**wall seconds × ranks ÷ 60**, and `ExecutionTime` is CPU time. The row framed
the choice as *the solver's own figure* versus *launch-to-end wall* — but a third
option satisfies both halves and sits on the same printed line: **`ClockTime` is
the solver's own figure AND it is wall.**

| | ExecutionTime basis (row as landed) | **ClockTime basis (this document)** |
|---|---:|---:|
| subset actual | 120.1285 core-min | **120.1833 core-min** |
| ratio actual / 123.2 registered | 0.9751 | **0.9755** |
| per-cell-iteration rate | 4.541148e-06 s | **4.543221e-06 s** |
| USD, **DERIVED NOT MEASURED** at $0.0513/core-h | $0.102710 | **$0.102757** |

The difference is **+0.0548 core-min, +0.046 %**. **No verdict, gate, cap
utilisation or transferable finding changes**: the ClockTime rate still lands
inside the measured Cartesian bracket [4.1541e-06, 4.6476e-06] near its `_f` end,
cap utilisation moves 30.03 % → 30.05 %, and the stall rule still matches
nothing. A correction row is appended to the ledger **beside** the existing row,
naming it by subject; **the existing row is not edited and none of its figures
is contradicted** — they remain correct as ExecutionTime figures.

---

## 8. VERDICT ON THE COST CLAIM

**MEASURED, 4 of 4 — as a lower bound whose gap is itself measured at 0.011 %.**
**STILL VOID: 0 of 4.**

The subset cost is **120.1833 core-min [MEASURED, `ClockTime` × 1 rank ÷ 60,
from the four `log.solve` files]**, a lower bound on the launcher-inclusive cost
by a measured 0.82 s (0.0136 core-min). USD **$0.102757 — DERIVED, NOT
MEASURED**, at the owner-stated c7a.4xlarge $0.0513/core-h (REPORTED-BY-OWNER
2026-08-21/22; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). Registered subset CAP 400.0 core-min: **not
approached.** No case over 3600 wall s.

**And the thing this document most wants on the record:** the reconstruction was
possible only because `ranks`, `solver`, `timeout_s` and four independent wall
clocks happened to survive in *other* artifacts. That is luck, not design. Had
these four cases run at more than one rank with a decomposition the log did not
print, `core-min` would have been **STILL VOID** and no honest figure could have
been written at all.

---

*Written by a heat-transfer lane, 2026-08-31. Nothing in this document is sent,
filed or submitted anywhere (standing rule 7).*
