# CFD LANE REPORT — the conversion batch, 2026-08-25

**Lane:** cfd `lab-lane` under `cfd-supervisor`. **Committed channel** — lane→supervisor
messaging is one-way, so this file is the report.

> **HEADLINE, and it contradicts the brief this lane was given.**
> **THE F3 AND F11 CONVERSIONS ARE NOT ARMED. BOTH ARE ALREADY FIRED, GRADED AND CLOSED.**
> There was nothing to fire. Firing either would have overwritten a graded artifact and
> broken a freeze, and in F11's case would also have run a launcher that is under a
> standing HARD BLOCKER. **No compute was spent on either, and no verdict was
> manufactured to fill the gap.**

---

## 1. What this lane actually did

| # | item | outcome |
| --- | --- | --- |
| 1 | Finish, self-test and land `scripts/parallel_batch.py` | **DONE**, commit `5c892f53` |
| 2 | Correct its verdict vocabulary on the supervisor's ruling | **DONE**, commit `92f7ceaf` |
| 3 | Fire F3 | **NOT A RESULT is already on record — the case is CLOSED.** Nothing armed |
| 4 | Fire F11 | **CLOSED.** Nothing armed, and the launcher is blocked |
| 5 | Disk-vs-HEAD sweep of frozen documents | **DONE — 13 tracked files differ; 8 are BEHIND HEAD** |
| 6 | F4 conversion pre-registration | see §6 |

---

## 2. PART 1 — the batch harness, landed and then corrected

**`/home/ubuntu/Certonomous/scripts/parallel_batch.py`**

| | |
| --- | --- |
| first commit | **`5c892f53`** |
| correction commit | **`92f7ceaf`** |
| sha256 (current, at `92f7ceaf`) | **`55168aa12d1b7e7581d47dda6cc138bbc3bd724553807b758d709ee39a0d5bab`** |
| sha256 (at `5c892f53`, superseded) | `d48e3883936382db378a18f002e9af0b0b8d45b163181fe4883a88f8a1e2acf4` |
| selftest | **32/32, exit 0** (was 26/26; was 19/20 before the pinning repair) |

**This is a measurement-adjacent script. Its diff goes to the supervisor before any number
it produces is believed. This lane's selftest is evidence, not the supervisor's read.**

### 2.1 The three behavioural changes asked for

1. **The cap no longer kills.** On a core-minute cap crossing the runner stamps the breach
   into the job record on disk and into every contention sample from that moment, **the job
   keeps running**, and the batch emits a labelled report line for the supervisor.
   `cap_action=kill` restores the literal rule-12 behaviour for any caller who asks, and the
   kill path is still exercised by `--selftest`. What still stops a job is the **runaway
   ceiling** — box protection on a shared 16-core box, not a budget gate.
2. **Concurrency is sized from measurement, not from 8–12.** Per-core busy fraction from
   `/proc/stat`; cores above `--core-busy-max` are treated as somebody else's and never
   offered; `MemAvailable` re-read from `/proc/meminfo` immediately before **every** launch
   against a floor. `--jobs 0` means "as many as the free cores allow". A narrowing is logged
   with its arithmetic, never absorbed.
3. **Costing is unchanged.** Sanaa lifted the *constraint*, not the *measurement*. A job
   spec with no positive `core_minute_cap` is **REFUSED outright**.

**Disclosed tension, so it is not discovered later.** `CLAUDE.md` rule 12 as written says an
overrun **stops the run**. Change 1 departs from that sentence on the strength of Sanaa's
2026-08-25 directive as relayed by cfd-supervisor. **Neither commit edits `CLAUDE.md`, and
this lane did not treat the relay as consent to edit it (standing rule 9).** The departure is
implemented, labelled in the module docstring, and put in front of the supervisor as a diff.

### 2.2 The defect this lane found in the inherited file — the CONTROL was broken

The pinning read-back sampled `/proc/<pid>/status Cpus_allowed_list` **once**, the instant
`Popen` returned, and read `0-15` on every job. `Popen` returns after the fork, before the
affinity syscall has necessarily landed. **The check therefore reported UNPINNED on a batch
that was in fact pinned — a control that could not see the thing it controls for.**

Fixed **at the source, not by loosening the assertion**: the mask is set in the **child before
exec** (`os.sched_setaffinity` in `preexec_fn`, single-thread precondition asserted), `taskset
-c` stays on the argv as a redundant second application, and `verify_pinning()` polls the
kernel's own mask until it **equals** the requested cores. A job still alive whose mask never
narrows is **REFUSED and stopped**, never run unpinned.

**The 19/20 run is the fire-evidence for this check: it was shown able to FAIL before it was
shown to pass.**

### 2.3 Guard 5, new — the fresh-case launch guard (rule 4)

A job naming `foam_case` is **REFUSED** when that case already holds `0/` or **any** numeric
time directory. Rule 4's age guard dates a run by requiring every field at `endTime` to be
newer than the case's own `0/` field; a pre-existing `0/` destroys that dating before the
solver starts. **This is a LAUNCH guard in the launcher. It neither replaces nor weakens any
completion criterion — rule 4's completion clauses stay entirely in the per-campaign
comparators, unchanged.**

Shown able to **fire** on `0/`, able to fire on a **non-zero** time dir (`0.5/` — a guard
matching only the literal string `0` is not the guard), able to stay **quiet** on a fresh
case, and the `allow_existing_times` bypass shown to work.

**Two usage constraints, recorded in the docstring on the supervisor's note rather than left
to be rediscovered:** (a) it reads the case **root only** — a decomposed case keeps its times
under `processor*/`, so it is covered **incidentally** by the root `0/` check and that check
must not be "optimised away"; (b) it wants the **run directory, not a pre-populated
template** — a caller reaching for `allow_existing_times: true` to quiet it has pointed it at
the wrong directory and the guard becomes decorative.

### 2.4 The supervisor's ruling, implemented at `92f7ceaf`

`summary_verdict()` returned **`GATE FAIL`** for a runaway stop and for any nonzero rc. Both
are cases in which **no gate was evaluated and no value exists**. `GATE FAIL` asserts a gate
*was* evaluated and the value *missed* its band. **Standing rule 5 fixes the direction: a gate
may turn a PASS or GATE FAIL *into* NOT A RESULT, never the reverse — and this code ran the
reverse**, promoting an execution failure into a stronger claim than the evidence supports.

Corrected mapping: `STATE_STOPPED` → **NOT A RESULT**; `rc != 0` → **NOT A RESULT**;
`STATE_BLOCKED` → **BLOCKED**; all DONE at rc 0 → **PASS**; a cap breach alone changes nothing.
**`GATE FAIL` is now unreachable from this runner by design** — it has no bands, so it can
never be the thing that decides a value missed one.

**Exit codes de-conflated**, because `EXIT_OK if PASS else EXIT_FAIL` could not tell a run that
never started from one that produced a wrong number: `0` PASS, `1` GATE FAIL (reserved,
unreachable here), `2` REFUSE, `3` NOT A RESULT, `4` BLOCKED. An unrecognised verdict string
exits 2 rather than guessing.

**Six new checks, each changed branch shown able to give the other answer.** A real crashing
job (`sh -c 'exit 7'`) verdicts NOT A RESULT, and the **mutation control** `rc 7 → 0` flips it
to PASS — the branch reads `rc`, it is not a constant. The runaway batch verdicts NOT A
RESULT, and `STOPPED → DONE` flips it to PASS.

### 2.5 `scripts/check_grader_self_blindness.py` — DOES it apply?

**Yes, and it was run.** Probe A hunts the L-322 shape (two `dict(...)` assignments to one
subscript target with differing key sets, where a consumer reads a key some branch does not
write) — this runner builds job records at three sites, which is exactly that shape.

It reports **clean on both probes** for `scripts/parallel_batch.py`. **That is a smell test
passing, not a proof of correctness, and it is recorded as the weaker thing it is.** The
structural answer is the one that matters: **one record constructor**, `RECORD_KEYS` +
`make_record()` asserting on schema drift in both directions, so a BLOCKED/PENDING branch
cannot omit a key the summary reads.

---

## 3. PART 2 — F3 IS CLOSED. Nothing was armed.

### 3.1 The freeze checks the brief asked for — all PASS

| check | result |
| --- | --- |
| `F3_CONVERSION_PREREGISTRATION.md` disk == HEAD | **YES** — both `e5f48c68e307c99dc0da44451f13497b922cbe2d` |
| `grade_f3.py` disk blob == HEAD blob | **YES** — both `6fea2e1d64cc3c377dd0e05ee4c08f6e83e1d049` |
| `grade_f3.py` sha256 == ADDENDUM 3's post-repair figure | **YES** — `e7602996cb75fd61e95a51a85910b24cf0a675b6eee05e8b7c3d2e5ae0b88570` |

ADDENDUM 3 read before use, as instructed. It supersedes AMENDMENT 1's `:557` clause on that
one point and alters no gate, threshold, cap or label.

### 3.2 …and the case those checks guard is already graded

`F3_CONVERSION_GRADED.json` carries the verdicts; `RC.txt` reads **0**; **10 of the 12
registered runs are on disk** (`runs/cone/M2.35_th10/{coarse,medium,fine}`,
`runs/wedge/M2.0_th15/{coarse,medium,fine}`, `runs/wedge/M3.0_th15/fine`,
`runs/diamond/M2.0_eps7p125/{coarse,medium,fine}`). The tally is closed at
**5 PASS, 1 GATE FAIL, 1 NOT A RESULT, 3 PENDING**.

**The two runs that were never launched are still absent**, verified this session:
`runs/wedge/M2.5_th10` and `runs/diamond/M2.5_eps5` — **ABSENT**. Nothing is half-fired.

### 3.3 The three PENDING rows, and why Sanaa's cost directive does NOT unblock them

`PENDING_ROWS_DISPOSITION.md` already ruled these **BLOCKED**: the frozen **39.5 core-min HARD
CAP** was spent (33.4177 measured), and §7's pre-wave budget check refused wave 6 by 40.54
core-s. **This lane re-examined that under Sanaa's 2026-08-25 lifting of cost constraints and
reaches the same answer, for a reason that is not about money:**

> **The F3 cap cannot be raised, and the obstacle was never scarcity.** Rule 2 closes gates,
> thresholds, **caps** and labels after first compute. The reason is evidentiary, not
> budgetary: **a cap raised after seeing which rows it refused is a cap re-posed to fit an
> answer.** Sanaa lifted a *spending constraint*; she did not retire rule 2, and retiring a
> gate threshold or charter clause is reserved to her explicitly and was not done.

**This is the exact shape of permission laundering the lab warns about** — "cost constraints
are lifted" is readable as "the F3 cap can be raised", and it cannot. **Recorded so the next
reader does not make that step.** The lawful route remains a **successor registration** for a
new rung with its own cap and its own bands, frozen before compute — and F3 §9's own
restriction stands: a single-mesh band-only row is citable but is **not a credential**
(`BAND_ONLY_RULING_2026-08-25.md`, which the supervisor ruled personally).

---

## 4. F11 IS CLOSED, AND ITS LAUNCHER IS UNDER A HARD BLOCKER

All **six** registered runs are on disk (`runs/re100/{coarse,medium,fine}`,
`runs/re1000/{coarse,medium,fine}`), `RC.txt` reads **0**, and `RESULTS.md` closes the case at
**`NOT A RESULT` on all six gate rows** — every band verdict was PASS, and rule 5's
iterative-convergence limb converted them, which is the gate operating in its only permitted
direction. Calibration row **C-64** is already filed.

**`DO_NOT_RERUN_rerun_f11.md` is in force**: `rerun_f11.py` writes `ledger["runs"][key]` at
three sites with differing key sets, four of which are read unconditionally elsewhere — an
armed `KeyError` on any run taking the short branch. **This lane did not execute it.**

---

## 5. THE STALENESS SWEEP — a defect class, and it has reached a CHARTER

The brief flagged that `F11_CONVERSION_PREREGISTRATION.md`'s worktree copy is **105 lines
behind HEAD**. **Confirmed, and the mechanism is now identified — and it is not confined to
F11.**

### 5.1 F11 specifically: proved, not inferred

The worktree blob is **`00d62c82ec25…`**, which is **byte-identical to the blob at
`34219bf5`** (AMENDMENT 1). HEAD carries `fd34c3b0b1c4…` from **`53298a45`** (AMENDMENT 2,
committed **01:16:28**). **The worktree file's mtime is 01:08:05 — it was never written
again after Amendment 1.**

**Therefore AMENDMENT 2's 105 lines were staged into the object database from something other
than this file, and the working copy never received them.** A path that stages from the
worktree (`git update-index --add -- <path>`) cannot produce this; a path that writes a blob
from a scratch file (`git hash-object -w` + `--cacheinfo`) can, and does.

**This is rule 13's failure mode wearing a different hat.** The amendment was composed in
scratch and hashed straight into the commit; **the working copy — which is what every
subsequent lane, every `grep`, and every comparator reads — never got it.**

**Why it matters concretely: a lane grading against the worktree copy would grade against a
document whose "Sanaa's directive, verbatim" attribution has been withdrawn.** The withdrawal
is in HEAD only.

**The worktree file was NOT reverted, restored or touched** (rule 10: an unexpected state is
inspected, never reverted).

### 5.2 The sweep, widened past `verification/campaign/`

Within **`verification/campaign/*.md`, F11 is the only differing file** — that much is clean.
Widened to **all 557 tracked `.md` under `verification/` and `docs/`, compared blob-by-blob
against HEAD**, **13 differ**. Classified by whether the disk copy is a **strict prefix** of
HEAD (i.e. *behind*, missing appended content) or the reverse:

| file | relation | mtime |
| --- | --- | --- |
| **`docs/charters/ANSYS_VERIFICATION_CHARTER.md`** | **BEHIND HEAD — missing 373 lines** | 2026-08-25 00:46 |
| `docs/FAIL_OPEN_GATE_AUDIT.md` | BEHIND HEAD — missing 150 lines | 2026-08-23 19:59 |
| `docs/ansys_verification/CASE_MAP_AUDIT.md` | BEHIND HEAD — missing 79 lines | 2026-08-25 01:05 |
| `docs/ansys_verification/RUN_STATUS_EVIDENCE.md` | BEHIND HEAD — missing 74 lines | 2026-08-25 01:09 |
| **`verification/campaign/F11_CONVERSION_PREREGISTRATION.md`** | **BEHIND HEAD — missing 105 lines** | 2026-08-25 01:08 |
| `docs/ansys_verification/ARCHIVE_HOME_RULING.md` | BEHIND HEAD — missing 34 lines | 2026-08-24 17:19 |
| `docs/ansys_verification/RECORDS_DRAFTS.md` | BEHIND HEAD — missing 22 lines | 2026-08-25 00:06 |
| **`docs/LAB_STATE.md`** | **BEHIND HEAD — missing 36 lines** | 2026-08-25 20:41 |
| `docs/ansys_verification/CASE_MAP.md` | DIVERGENT (disk 616, HEAD 664) | 2026-08-25 03:21 |
| `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | DIVERGENT (disk 428, HEAD 424) | 2026-08-25 20:41 |
| `docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md` | AHEAD of HEAD (+460, uncommitted) | 2026-08-25 20:42 |
| `docs/campaigns/F14-cooling-ladder/K0d_LANE_REPORT_FIRE.md` | AHEAD of HEAD (+214, uncommitted) | 2026-08-25 19:25 |
| `docs/campaigns/T-family/T10aR_PREREGISTRATION.md` | AHEAD of HEAD (+95, uncommitted) | 2026-08-22 19:45 |

**Eight are BEHIND HEAD, and every one of the eight is a strict prefix — the signature of an
appended amendment that landed in the commit and never landed on disk.** That is one
mechanism, not eight coincidences.

**`docs/charters/ANSYS_VERIFICATION_CHARTER.md` is 373 lines behind and spans four separate
appends** (`e05bd728` v1.2, `649aa42a` dated note, `3abac11f` v1.3, `75030b12` v1.4). **A lane
reading that charter off disk today is reading a document that stops at v1.1.**

**`docs/LAB_STATE.md` is 36 lines behind** — the lab's *only* handoff channel, missing the
2026-08-25T20:28Z VMFLGPU re-ruling.

**The three AHEAD rows are other teams' live, uncommitted work** (two were being written
minutes before this sweep). **This lane touched none of the thirteen.**

**Recommendation, referred not taken:** the private-index protocol in rule 10 stages from the
worktree and is safe. **The unsafe path is composing an amendment in scratch and hashing it
straight into the object database.** A cheap guard is a post-commit assertion that
`git hash-object <path>` equals `git rev-parse HEAD:<path>` for every path in the commit —
the same shape as the post-commit `git diff HEAD~1 HEAD --stat` verify that rule 10 already
mandates, and this lane ran that assertion on both of its own commits.

---

## 6. F4 — NOT FIRED, and why

**There is no F4 conversion pre-registration.** `verification/runs/F4_runs/conversion_2026-08-24/`
exists and is **empty**; no run directory has been created and no F4 compute has been spent by
this lane.

**Do not fire F4 without a committed pre-registration is the supervisor's check 4 and is not
delegable.** This lane did not fire it.

**One hazard must be carried into whoever drafts it, and is recorded here rather than left to
be rediscovered: BAND CONTAMINATION HAS ALREADY OCCURRED FOR THIS LANE.** In establishing what
F4 *is*, this lane read `CAMPAIGN_STATUS.md:465`, which publishes the 2026-07-28 measured
deviations — **standoff +0.7–2.3 %, Cp RMS 3.87–3.91 %**. **Any band this lane now writes has
seen the answers it would be judging.** F3's own §2 confronts exactly this and defends against
it by deriving every band from a **stated principle** — a reference class, or the detector's
quantization floor computed from mesh geometry — **never from a measured deviation**. Any F4
drafter must meet that standard explicitly and disclose the exposure, as this paragraph does.

---

## 7. COST CALIBRATION (standing rule 12)

**No solver compute was spent by this lane. 0.0000 core-minutes of graded compute.** The two
`--selftest` runs and the sweep are single-core scripted work of a few minutes, and the
harness's own pinned selftest children are trivially short.

**No row is added to `docs/COST_CALIBRATION.md`, and that is deliberate: no process consuming
graded compute completed.** Manufacturing a calibration row for a selftest would put a
fictitious measurement in the ledger — the same reasoning `PENDING_ROWS_DISPOSITION.md` §7
recorded, and it is followed here rather than restated as new.

**The F3 and F11 calibrations are already on record and are NOT restated as new work:** F3
rows **C-66** (original) and **C-68** (correction), ratio **1.1290** over launched runs only,
waste zero, contention bounded/not measured/under-counted; F11 row **C-64**, **6.0835
core-min actual against 8.0200 predicted, ratio 0.759**, waste zero, gap attributed to
over-prediction.

---

## 8. THE LOG-LANDING ASSERTION — stated honestly

`.gitignore` lines 260–266 hide `verification/runs/*_runs/**/log.*` and its `*.log` variants,
so solver logs — the primary evidence — are invisible to `git add`. `git update-index --add`
bypasses ignore rules and **can** land them, and the assertion that they landed is the point.

**This lane produced NO new solver logs, because it fired no solver.** The assertion is
therefore **not applicable to these two commits** and is **not claimed as performed.** It is
built into the procedure for any future fire: after `git write-tree`, confirm every log path
appears in `git diff-tree --stat`; after the commit, assert `git cat-file -e HEAD:<logpath>`
for every one; fail loudly on any miss.

**What this lane DID assert on both commits** is the rule-10 pair: `git diff-tree --stat $H $T`
showing exactly one path before the commit, and `git diff HEAD~1 HEAD --stat` showing exactly
one path after it.

---

## 9. VERDICTS

| item | verdict | basis |
| --- | --- | --- |
| `scripts/parallel_batch.py` as an instrument | **PASS** — 32/32 selftest, exit 0 | this lane's own test; **evidence, not the supervisor's read** |
| F3 conversion launch request | **BLOCKED** | frozen 39.5 core-min cap spent; rule 2 closes caps after first compute; Sanaa's cost lift does not reach it |
| F11 conversion launch request | **BLOCKED** | case closed and graded; launcher under a standing hard blocker |
| F4 conversion | **PENDING** | no pre-registration exists; supervisor's non-delegable check 4 |
| Frozen-document staleness | **finding, 8 files BEHIND HEAD** | blob comparison against HEAD, strict-prefix test |

**Nothing in this report is an estimate presented as a measurement. Every figure cites an
artifact still on disk.**
