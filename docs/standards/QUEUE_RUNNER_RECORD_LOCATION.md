# Queue runner — RECORD LOCATION

**Status: SPEC, FROZEN AT ITS COMMIT. No code exists yet, and none is written until this
is ruled.** Written **before** the implementation so the implementation cannot be shaped to
pass its own test (`CLAUDE.md` rule 2's discipline applied to tooling). The commit that
lands this file is the freeze; the code that follows cites that sha, and any departure is a
dated amendment at the foot, never an edit above it (rule 6).

**Owner:** cfd-supervisor (`scripts/queue_runner.py` is cfd tooling).
**Provenance:** the defect was found by the cfd-supervisor on 2026-08-28 by reading
`scripts/queue_runner.py::launch()`. Every count, path, line number and behavioural claim
below was **re-measured against the code and the tree by cfd lane RUNWRITE** the same day,
between HEAD `0d461139` and HEAD `04c7b0da`. **Five statements in the brief were falsified
on that check** and are corrected in §2a rather than carried forward. Sibling precedent and
model: `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md`.

**This document adds no gate, no threshold, no cap and no label.** It changes **where four
runner-owned bookkeeping files are written**, and nothing else. It changes no verdict, no
grading path and no entry schema.

> **REFERRAL, NOT A DECISION — for the chief.** `scripts/queue_runner.py` is **shared lab
> infrastructure used by all six teams**. The change is cfd-owned code but it alters an
> artifact location that dafoam's `cases/dafoam/_common/dafoam_wait_then_launch.sh`
> **documents a measured dependency on** (§5.2), and it is visible to every team's launch
> bookkeeping. **The blast radius is §7 and it is cfd's to state, not cfd's to accept on
> the lab's behalf.** This document is written; the code does not land until routed.

---

## 1. The invariant

**A file written by the queue runner is the RUNNER'S bookkeeping and belongs in the
runner's own tree. It is never written into a path the entry supplies.**

Formally: for every file whose sole author is `scripts/queue_runner.py`, the destination
directory is derived from the **queue root**, never from `entry["cwd"]`. The entry's `cwd`
remains the process working directory of the launched argv and keeps that meaning
unchanged.

Four files are in scope. The brief named two; **there are four**, and the two the brief
missed are the overrun flags:

| file | written at | today's destination |
|---|---|---|
| `STATUS.<case_id>` | `queue_runner.py:496` | `entry["cwd"]` |
| `launcher.queue.out` | `queue_runner.py:497` | `entry["cwd"]` |
| `CAP_OVERRUN.txt` | `queue_runner.py:611` | `Path(meta["cwd"])` |
| `ESTIMATE_OVERRUN.txt` | `queue_runner.py:627` | `Path(meta["cwd"])` |

When `cwd` is the case directory — **the lab convention, and the validator's own EXEC
message at `queue_entry_check.py:351` says so in those words** — all four land inside
`cases/`, beside frozen inputs, against `FILING_CHARTER.md` and `CLAUDE.md`'s WHERE THINGS
LIVE table.

---

## 2. What was measured

At HEAD, on disk, 2026-08-28 (`find cases -type f` over the four basenames, excluding the
one prose `STATUS.md`):

- **84 files across 34 case directories.**
- Split: **46** `STATUS.<case_id>`, **34** `launcher.queue.out`, **4** `CAP_OVERRUN.txt`,
  **0** `ESTIMATE_OVERRUN.txt`.
- **45 of the 46 `STATUS.*` files are in the runner's own format** (first field `rc=` or
  `launcher_rc=`). Exactly **one** is not:
  `cases/dafoam/ladder-a/A2/curriculum_D6R/STATUS.D6R_chain_wait`. So this is
  overwhelmingly the runner's mess, not the teams'.
- Owner split of the 80 `STATUS`/`launcher.queue.out` files: **52 dafoam, 28 cfd** (14
  `F1*`/`F2*` case dirs, two files each).
- Largest `launcher.queue.out` on disk: **218,209 bytes**
  (`cases/dafoam/ladder-a/A6/curriculum_D8R/launcher.queue.out`). This figure decides §4.3.
- **`.gitignore` carries zero rules** for any of the four basenames. That absence is why
  four of them reached the tree.

Tracked at HEAD, by `git ls-tree -r --name-only HEAD` — **never `git ls-files`**, which
reads the shared index and currently stages ~297 whole-file deletions:

- At `0d461139`: **4**.
- At `04c7b0da` (current): **2** — `cases/ansys_verification/VMFL023/STATUS.md` (prose, and
  correctly not a violation) and `cases/dafoam/curriculum_D12R2/STATUS.W3_chain`.

---

## 2a. FIVE STATEMENTS IN THE BRIEF THAT WERE FALSIFIED ON CHECK

Recorded because the supervisor asked for falsification before a commit, not after.

**(1) "TWO runner-owned records" — there are FOUR.** `cap_watch()` writes
`CAP_OVERRUN.txt` (`:611`) and `ESTIMATE_OVERRUN.txt` (`:627`) into `Path(meta["cwd"])` by
the same mechanism. Four such files exist under `cases/` today. A repair scoped to two
would leave the class half open, and the half it left open is the half that fires only on
an overrun — i.e. the half nobody looks at until something has already gone wrong.

**(2) "50 such files on disk across 21 case directories" — measured 84 across 34.** The
brief's figure is low by two-thirds. The difference is not a rounding: it is the entire
`cases/dafoam/ladder-a/` subtree plus the four overrun flags.

**(3) "`scripts/check_filing.py` IS BLIND TO THIS CLASS" — FALSE at HEAD.** The rule
**already exists**: `R6-RUNARTIFACT`, `check_filing.py:232-241`, keyed on
`RUNNER_ARTIFACTS = {"launcher.queue.out", "CAP_OVERRUN.txt", "ESTIMATE_OVERRUN.txt"}`
(`:313`) plus `STATUS.*` excluding `.md` (`:234`), scoped to `cases/`. It was landed by
verification at `82365c76` earlier the same day, with six planted control limbs of which
three are negative. It **fires**: measured today it returned the exact violations, and it
correctly does **not** flag `VMFL023/STATUS.md`. `check_filing.py --selftest` measured rc 0
today (15 planted violations, 20 correct filings that must survive). **The brief's "34
violations" is also stale — the tool returned 37, then 35 as the tree moved.** §6
therefore specifies **no new rule**; it records the existing one and names its two residual
blind spots.

**(4) The AGE-GUARD is NOT a second obstacle to option (a), and the brief's supporting
argument for that is wrong in cfd's favour.** `check_age_guard_cwd`
(`queue_entry_check.py:306-326`) scans **only direct children** of `cwd` for `TIME_DIR`.
The F-family run roots hold **level** directories (`coarse/`, `medium/`, `fine/`), not time
directories, so repointing `cwd` at a run root would **not** trip the age guard. Only
`EXEC` blocks (a). Stating the objection accurately makes it narrower and therefore
harder to wave away.

**(5) "The 4 tracked files are not in scope; a deletion is Sanaa's decision" — the
premise moved under the brief while this spec was being written.** A cfd peer landed
`04c7b0da` at 17:17:34Z, **during this measurement**, relocating the two F17c files as a
**true rename (R100)** to `verification/runs/F17c_runs/` — explicitly *not* a deletion, on
exactly the reasoning the brief gives. The tracked count is now **2**, and the one
remaining `R6-RUNARTIFACT` violation is dafoam's `STATUS.W3_chain`, which is dafoam's to
move. §8 is unchanged in substance — this spec still governs future writes only — but it no
longer describes 4 files, and it must not be read as authorising a deletion of the
remaining 2.

*Method note, because the instrument nearly fooled this lane too:* the first sweep found
`cases/F17c_kovasznay_floor/STATUS.F17c_KV40_FLOOR`; a later `cat` of the same path
returned `No such file or directory`. The tree had moved under a two-command measurement.
The finding was only recovered by re-running the sweep and **diffing the two sweeps against
each other** rather than trusting the first. Counts in this document are stamped with the
HEAD they were taken at for that reason.

---

## 3. THE COMPATIBILITY MEASUREMENT — the one that decides the recommendation

**Question, from the brief: does ANYTHING read `launcher.queue.out` or `STATUS.<case_id>`
from the case directory?**

Method. `git ls-tree -r --name-only HEAD` filtered to source and document extensions (5,408
files), then `grep -l` over that explicit list — never a bare recursive `grep`, which is
ugrep here and races its multi-file output order. Each hit was then opened and read
individually.

**Instrument control (rule 3): this sweep was shown able to see a real read.** It found
`cases/dafoam/_common/dafoam_wait_then_launch_selftest.sh:49-50`, which does
`grep -c 'event=WAIT ' "$CASEDIR/STATUS.L1"` — a genuine filesystem read of a case-side
`STATUS.*` file. A sweep that returned zero without first finding that would be measuring
its own regex.

### 3.1 `launcher.queue.out` — ZERO readers, repo-wide

17 code files mention the string. Every one is accounted for:

- **1 writer**: `scripts/queue_runner.py`.
- **1 checker keyed on BASENAME**: `scripts/check_filing.py:313`. Location-independent by
  construction — it flags the name under `cases/` and explicitly must **not** flag it under
  `verification/runs/` (planted negative, `:329`). Moving the file satisfies this rule
  rather than breaking it.
- **14 classification-string sites, no filesystem access**: the `INFRASTRUCTURE` tuples of
  13 `cases/F*/grade_f*.py` graders (e.g. `grade_f17c.py:110`), which list
  `"STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner"` as an
  L-342 field class — a *label*, never a path opened; and
  `verification/runs/T-family/T5_runs/analyse_t5.A10_PROPOSED.py:496`, whose
  `INFRASTRUCTURE_ARTEFACTS` tuple is **defined at `:495` and never referenced again
  anywhere in the file** (measured: one occurrence of the identifier).
- **1 prose comment**: `verification/runs/T-family/T3_runs/launch_t3_rff.sh:59`.
- The remaining mentions are `.md` prose, `queue_entry_*.json` `cwd_note` fields (e.g.
  `cases/F19_SOD/queue_entry_F19_SOD.json:20`) and `launched/*.json` records.

**Nothing opens it. Moving `launcher.queue.out` is free.**

### 3.2 `STATUS.<case_id>` — one reader class, and it reads someone else's file

- **`cap_watch()` reads it** — via `Path(li.get("status_file", ...))`, i.e. the **absolute
  path the runner itself stamped** into `_launch.status_file` at `:530`. It never
  reconstructs the path from `cwd`. **It follows the move for free, with no edit.** This is
  the single most important compatibility fact in this document.
- **`cases/dafoam/_common/dafoam_wait_then_launch_selftest.sh`** greps
  `$CASEDIR/STATUS.<id>` — but the file it reads is written by **dafoam's own wrapper**
  (`dafoam_wait_then_launch.sh:82`, `STATUS="$CWD/STATUS.$CASE_ID"`), not by the runner.
  The selftest drives the wrapper directly, with no runner in the loop. **Unaffected.**
- The dafoam chain drivers (`d17_chain_driver.sh:141`, `d18_chain_driver.sh:156`,
  `d12y_w3_chain_driver.sh:41`, `d12y_plan_step.sh:72`, and peers) **write** `$BASE/STATUS.*`
  themselves and read back their own lines. **Unaffected by a runner change**, and *not
  cleaned by it either* — see §8.

### 3.3 VERDICT ON THE COMPATIBILITY QUESTION

**No code in this repository reads either file from the case directory as a runner-written
artifact.** Option (b) breaks no reader and needs no migration and no compatibility shim.
It has exactly **one** named cross-team coupling, and it is a **write** coupling, not a
read: §5.2.

---

## 4. THE THREE CANDIDATES, AND THE RULING

### 4.1 (a) Repoint every entry's `cwd` to its run root — **REFUSED, on a measured fact**

The supervisor's objection is **correct and is now measured per case.** Read from each
launcher at HEAD:

| case | run root | created by | pre-exists at first launch? |
|---|---|---|---|
| F17c | `verification/runs/F17c_runs` | `run_f17c.sh:189` `mkdir -p "$RUN_ROOT"` | **NO** |
| F23 | `verification/runs/F23_HP_WEDGE_runs` | `run_f23.sh:183` `mkdir -p "$RUN_ROOT"` | **NO** |
| F25 | `verification/runs/F25_DUCT3D_runs` | `run_f25.sh:186` `mkdir -p "$RUN_ROOT"` | **NO** |
| F27 | `verification/runs/F27_WOMERSLEY_PIPE_runs` | `run_f27.sh:265` `mkdir -p "$RUN_ROOT"` | **NO** |
| F26D | `verification/runs/F26D_runs` | `run_f26d.sh:50` `mkdir -p "$RUN_ROOT"` | **NO** |

**Five for five: the launcher creates its own run root.** `F23b` has a pre-registration
(`verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md`) but **no case directory and no
queue entry at HEAD**, so it has no `cwd` to repoint — recorded rather than guessed.

Consequences, both measured:

1. `queue_entry_check.py::check_cwd_launchable` (`:330`, dispatched as `"EXEC"` at `:419`)
   **REFUSES an absent `cwd`**, and carries a planted control (`CONTROL A (cwd absent)`,
   `:764`) that would fail if it did not. A repointed entry for a case that has not run is
   refused at validation, before any launch.
2. `queue_runner.py:509` calls `Popen(..., cwd=str(cwd))`, which raises `FileNotFoundError`
   on an absent directory, and the inner `cd '<cwd>' &&` at `:502` fails likewise.

So **(a) is not universal.** It works only for a re-run into a run root that already
exists. Measured today: `F26_RINGLEB_runs` is **ABSENT**, so F26D could not be repointed at
all right now. ansys's `b7bed168` worked because that entry's run root existed; that is a
property of that case, not a generalisable route.

(a) also requires editing **every** entry across six teams — files whose `prereg_commit` is
frozen — to fix a defect in one line of one shared script. The cost is borne by five teams
who did not write the defect.

**Correction in cfd's disfavour, for the record:** the brief also offered the AGE-GUARD as
an objection to (a). It is not one (§2a item 4). (a) is refused on `EXEC` alone.

### 4.2 (c) `queue_entry_check.py` refuses a `cwd` under `cases/` — **REFUSED FIRST**

It inherits (a)'s defect entirely: it forces every team onto a route that `EXEC` refuses
for any case that has not yet run, so it converts a filing violation into a **launch
blocker**. It is also a **widening of a validator refusal** applied to five other teams'
entries — the dangerous direction — and it **contradicts a written ruling**: the `EXEC`
message at `:351` states in its own text that "the CASE directory is the lab convention".
Reversing that is `QUEUE_ENTRY_VALIDATOR_RULINGS.md` territory at minimum and plausibly
Sanaa's. It is refused before (a) because it is refused on the same fact **plus** a
governance one.

### 4.3 (b) The runner writes its records in the runner's own tree — **RECOMMENDED**

Defended against the other two:

1. **It is the only one of the three that fixes the defect where the defect is.** The
   files are written by one line each of one script. Four line changes, one `mkdir`, one
   `.gitignore`. No entry changes. No schema change. No validator change. No other team
   touches anything.
2. **It is free on the compatibility measurement (§3.3)** — zero readers, and `cap_watch`
   follows automatically through `_launch.status_file`.
3. **It is right on the merits, not merely convenient.** The runner's own docstring calls
   `STATUS` an **INFRASTRUCTURE** record under L-342 (`:522-526`, and `:534` classes it
   beside `_launch.pid` and `LAUNCH_LOG.tsv` rows) recording *the launch argv's exit
   status and explicitly not the solver's rc*. It is bookkeeping about a **launch**, not an
   output of a **solve**. `LAUNCH_LOG.tsv` — its exact sibling — already lives at
   `root / "LAUNCH_LOG.tsv"` (`:537`). The four files in scope are the outliers.
4. **It fixes two clobbering defects nobody had named** (§5.1, §5.2).

**Residual honestly named:** (b) does **not** clean `cases/`. It removes the runner's
future contribution only. See §8.

#### The destination, and why not simply `launched/`

The brief proposed `verification/queue/<team>/launched/`. **Specified instead:**

```
<queue_root>/<team>/launched/records/STATUS.<case_id>
<queue_root>/<team>/launched/records/<case_id>.launcher.queue.out
<queue_root>/<team>/launched/records/<case_id>.CAP_OVERRUN.txt
<queue_root>/<team>/launched/records/<case_id>.ESTIMATE_OVERRUN.txt
```

with `<queue_root>/<team>/launched/records/.gitignore` containing a single line `*`,
written by the runner at `mkdir` time if absent, never overwritten if present.

Three reasons, each measured:

- **`launched/` is TRACKED.** Its `*.json` records are committed at HEAD (60+ files across
  five teams). Dropping a **218 KB** stdout capture (§2) beside them creates a fresh
  commit hazard in a directory people routinely `git add`. The `.gitignore` closes it. The
  absence of any such rule today is precisely how four files reached the tree.
- **A per-case prefix prevents a new collision.** `launcher.queue.out` is currently
  disambiguated by living in a per-case directory; a shared `records/` directory removes
  that, so the case id must be carried in the name. The overrun flags need it for the
  same reason.
- **A subdirectory keeps `is_current_record()` / `ARCHIVED_RE` glob semantics intact.**
  `archive_previous_records` (`:454`) and `cap_watch` (`:583`) both iterate
  `launched_dir.glob("*.json")`; non-JSON siblings are already ignored, but a subdirectory
  makes the separation structural rather than incidental.

**Overwrite-on-relaunch is preserved deliberately and is not a regression:** today a
relaunch of the same `case_id` overwrites `cwd/STATUS.<case_id>`; under (b) it overwrites
`records/STATUS.<case_id>`. Identical semantics, and `archive_previous_records` continues to
archive the **JSON record** that names the old paths. Changing this is out of scope and is
flagged as a possible successor, not smuggled in.

---

## 5. TWO CLOBBERING DEFECTS THIS FIX ALSO CLOSES — neither named in the brief

### 5.1 The runner destroys F27's own status record (cfd's own case)

`cases/F27_WOMERSLEY_PIPE/run_f27.sh:57` sets `STATUS="$ROOT/STATUS.F27_WOMERSLEY_PIPE"`
where `ROOT` is the **case** directory (`:48`). That is **byte-for-byte the same path** the
runner computes at `queue_runner.py:496`. `run_f27.sh::write_status()` (`:88-91`) writes a
**richer** record there — it carries `cap_core_min=` and `spent=` fields the runner's line
does not have — and the runner's `>` redirect fires **after** the launcher exits.

**Measured:** the on-disk file is **one line**, in the runner's format
(`launcher_rc=0 end=2026-08-28T09:01:29Z note=exit-status-of-the-launch-argv-...`). F27's
own cap and spend record **was overwritten and is gone**. This is a live loss of a cost
artifact, in cfd's own territory, and it is invisible because the surviving line looks
correct. (b) ends it. A sweep of all `cases/F*/run_f*.sh` found **this case only**.

### 5.2 The dafoam wrapper coupling — THE ONE CROSS-TEAM ITEM, and it must be routed

`cases/dafoam/_common/dafoam_wait_then_launch.sh:82` independently computes
`STATUS="$CWD/STATUS.$CASE_ID"` and **appends** its wait/refusal series there. Its header
comment (`:36-39`) states as **measured fact**:

> `scripts/queue_runner.py` overwrites `STATUS.<case_id>` with its own one `launcher_rc=`
> line when this wrapper exits (`>` at `launch()`, measured); the wrapper's full series
> therefore ALSO lands, identically, in `WRAPPER.<case_id>.log` beside it, which the runner
> never touches.

Under (b) that sentence becomes **false**: the runner no longer touches
`cwd/STATUS.<case_id>` at all, so dafoam's series **survives** in it. Nothing breaks —
`WRAPPER.<case_id>.log` still holds the full series, and the wrapper's selftest reads only
files the wrapper itself writes (§3.2) — and the change is a strict improvement, because a
record stops being destroyed. **But it falsifies a documented invariant in another team's
file, and a spec that quietly invalidates another team's comment is doing the thing this
lab writes amendments to prevent.** `cases/dafoam/curriculum_D12R2/d12y_plan_step.sh:72`
carries the same shape.

**Routed, not decided:** dafoam is entitled to be told before this lands, and to say
whether they want the wrapper's `STATUS` path changed at the same time. cfd does not edit
dafoam's files.

---

## 6. `check_filing.py` — THE RULE ALREADY EXISTS. NO NEW RULE IS SPECIFIED.

The brief asked for a rule to catch this class. **It landed earlier the same day**
(verification, `82365c76`) and this spec must not duplicate it. Recorded here so the
supervisor's check has something to check against:

- **`R6-RUNARTIFACT`**, `check_filing.py:232-241`. Scoped to `p.startswith("cases/")`.
  Fires on `base in RUNNER_ARTIFACTS` — `{"launcher.queue.out", "CAP_OVERRUN.txt",
  "ESTIMATE_OVERRUN.txt"}` (`:313`) — **or** `base.startswith("STATUS.") and not
  base.endswith(".md")` (`:234`).
- **It answers the brief's discrimination question, and the answer is yes.** The `.md`
  suffix is the discriminator and it is load-bearing:
  `cases/ansys_verification/VMFL023/STATUS.md` is a **prose** interim-status document and
  is **not** flagged; `STATUS.W3_chain` and `STATUS.F17c_KV40_FLOOR`, in the runner's
  `launcher_rc=... end=... note=...` format, **are**. Both limbs are planted (`:322-329`,
  three positive and three negative). Verified live today: the tool returns
  `STATUS.W3_chain` and does not return `STATUS.md`.
- **It uses the correct instrument.** Enumeration is `git ls-tree -r HEAD --name-only`
  (`:99-100`), not `git ls-files` — the same trap the brief warns about, already avoided.
- **`--selftest` measured today: rc 0**, 15 planted violations and 20 correct filings that
  must survive, every one behaved.

**Two residual blind spots, NAMED AND NOT FIXED HERE** (they are verification's file, and
naming them is this spec's whole obligation):

1. **It sees only files TRACKED AT HEAD.** The 84 on-disk files of §2 are invisible to it;
   it reports the 1 that is committed. The rule is a *commit* guard, not a *tree* guard. It
   is therefore **complementary to** this spec, not a substitute: R6-RUNARTIFACT stops the
   artifact reaching git, §4.3 stops it being written. Neither alone closes the class.
2. **It is scoped to `cases/`.** A runner artifact written under `docs/` or `models/` would
   pass. No such entry exists at HEAD (measured), so this is latent, not realised.

Any edit to that rule requires `scripts/check_filing.py --selftest`. **This spec proposes
no such edit.**

---

## 7. Controls — `--selftest`, planted, driving the REAL path, with mutations that must flip

Sanaa's 2026-08-28T17:01Z directive 1 governs, verbatim: *"A planted control must travel
the real production path — written by the real producer's code, read through the real
reader — and prove the instrument sees a non-zero the same way reality would deliver one."*
Every control below drives the **real `launch()`** and the **real `cap_watch()`** through
the real `tick()` in a scratch queue root — the mechanism `--selftest` already uses. No
control asserts on a path it constructed itself without the runner having written it.

### 7.1 The six new controls, with their assertions stated exactly

**C-LOC-1 — THE NEGATIVE CONTROL: the records are STILL WRITTEN.** *(This one first,
because a "fix" that simply stops writing them would pass every location check and destroy
the launch bookkeeping.)* Drive control 2's entry (`argv = ["true"]`) through
`tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)`; poll ≤ 5 s. Assert **all** of:

- `(records / "STATUS.SELFTEST_OK").exists()` is `True`
- `text.startswith("launcher_rc=0")` is `True`
- `"NOT-the-solver-rc" in text` is `True`
- `(records / "SELFTEST_OK.launcher.queue.out").exists()` is `True`

**C-LOC-2 — THE LOCATION ASSERTION, in its strongest form.** After C-LOC-1's launch:

- `sorted(p.name for p in case_dir.iterdir()) == []`

Stated as directory **emptiness**, not as "no `STATUS.SELFTEST_OK`". A weaker assertion
would pass if the runner wrote `STATUS.SELFTEST_OK.tmp`, or wrote the out file and not the
status file, or left a lock. The case directory is created empty by the control and the
argv is `true`, so emptiness is exactly the right bar and it is checkable.

**C-LOC-3 — THE PLANTED TOKEN, through the real producer and the real redirect.** A second
entry, `case_id = "SELFTEST_PLANT"`, `launch_cmd = ["bash", "-c", "echo PLANT_7f3a1c; exit 0"]`.
After the tick and a poll on its STATUS, assert:

- `"PLANT_7f3a1c" in (records / "SELFTEST_PLANT.launcher.queue.out").read_text()`
- `"PLANT_7f3a1c" not in (records / "STATUS.SELFTEST_PLANT").read_text()`

The first limb proves the **redirect is live at the new path** — C-LOC-1 alone would pass
on a zero-byte file, and a zero from a reader not shown able to see a non-zero is not
evidence (rule 3). The second limb proves the two records stayed **distinct** rather than
one being aliased onto the other by the edit.

**C-LOC-4 — THE MUTATION THAT MUST FLIP.** A local `_mutant_launch_in_cwd` reproducing
today's `:496-497` (both paths back under `cwd`), driven through the same `tick`. Assert:

- C-LOC-2's assertion **FAILS** under the mutant (the case dir is not empty), **and**
- C-LOC-1's assertion **still PASSES** under the mutant.

This is the control that proves the two are measuring **different** things: C-LOC-2 is
sensitive to location and C-LOC-1 is not. Without it, one control could be silently
carrying the other.

**C-LOC-5 — THE OVERRUN FLAGS, both of them, at the new location and at the SAME times.**
Existing controls 12 and 14 (`flag_text(d)` at `:958`, and the hand-wired
`_launch = dict(status_file=str(cap_dir / "STATUS.SELFTEST_CAP"), ...)` at `:902` and
`:919`) are re-pointed at `records`. **The timing assertions are carried over
byte-identical** — `CAP_OVERRUN` absent at 59 s and present at 61 s; `ESTIMATE_OVERRUN`
absent at 65 s, present at 67 s, text says NOT A CAP — because the timing is what those
controls exist to test and only the location changes. Assert additionally:

- `not (cap_dir / "CAP_OVERRUN.txt").exists()` and `not (est_dir / "ESTIMATE_OVERRUN.txt").exists()`

**C-LOC-6 — THE dafoam COUPLING, made observable.** Before the tick, write
`WRAPPER_PLANT_c41d\n` into `case_dir / "STATUS.SELFTEST_WRAP"` (the shape
`dafoam_wait_then_launch.sh:82` produces). After the launch completes, assert:

- `(case_dir / "STATUS.SELFTEST_WRAP").read_text() == "WRAPPER_PLANT_c41d\n"`

Under today's code this **fails** — the runner truncates it. That is the §5.2 behaviour
change made into a checkable fact rather than a paragraph, and it is the control to put in
front of dafoam.

### 7.2 The existing controls: which change, which do not, and why

`--selftest` measured at HEAD today: **41/41 checks, 0 asserts, rc 0, 5 wall s.** Acceptance
bar after the change: **47/47, 0 asserts, rc 0.** Every update below is justified, not
silently edited.

| control | site | change | justification |
|---|---|---|---|
| #3 `valid entry -> LAUNCHED once, STATUS launcher_rc=0` | `:807-816` | read `records / "STATUS.SELFTEST_OK"` | asserts **format and count**, not location; C-LOC-2 now owns location |
| #5 `launched record carries the L-342 field-class split` | `:824` | **NO CHANGE** | asserts the *string* `"STATUS.SELFTEST_OK"` is in `physics_critical`. That is a **basename**, and it stays true. This is the control that looks like it must change and must not — changing it would weaken a rule-4 field-class assertion to fix a filing bug |
| #12, #13 (cap) | `:899-914`, `:958` | `flag_text` reads `records` | timing assertions byte-identical (§7.1 C-LOC-5) |
| #14, #15 (estimate) | `:916-930` | as above | as above |
| #16 (finished) | `:931-940` | `(records / "STATUS.SELFTEST_FIN")` written by the control at `:933` | the control **writes** this file to simulate a landed STATUS; it must write it where `cap_watch` will now look |
| #18–#23 re-armed cwd | `:967-1010`, `launch_case()` `:949` | `rearm_status = records / "STATUS.SELFTEST_REARM"` | `launch_case` already takes `status: Path` as a **parameter**; one expression changes and the archive/supersede logic is untouched |
| #24, #25 T5_C class | `:1030-1031` | `s2 = records / f"STATUS.SELFTEST_REARM2_{tag}"` | as above |
| GPU controls 1–6, plants 1–4 | `gpu_wait_status` `:1147-1149` | poll `records / f"STATUS.{name}"` | the helper polls for launch completion; the GPU clause itself is untouched |
| never-appears control | `:1191-1192` | **NO CHANGE** | `status_file=str(tmp / "STATUS.NEVER_APPEARS")` is a **synthetic** path that must never exist; unaffected by where real ones go |

**A control whose update is not in this table is a control whose update was not
authorised.** If implementation finds one, it is a dated amendment at the foot of this
file, not an edit above it.

---

## 8. What this spec does NOT do

1. **It does not back-fill.** It governs **FUTURE WRITES ONLY**. The 84 on-disk files and
   the 2 tracked at HEAD are untouched by it, exactly as the rename-mode spec excluded
   existing fossils.
2. **It does not delete anything, and must not be read as authorising a deletion.** A
   deletion is Sanaa's decision and goes to her desk. Note that `04c7b0da` relocated cfd's
   two F17c files by **rename**, not deletion; that route exists and remains open to each
   owner **for their own files**. `cases/dafoam/curriculum_D12R2/STATUS.W3_chain` is
   dafoam's, and cfd does not move it.
3. **It does not clean `cases/`.** It removes the **runner's** future contribution. Team
   drivers that compute a case-side `STATUS` path themselves — `d17_chain_driver.sh:141`,
   `d18_chain_driver.sh:156`, `d12y_w3_chain_driver.sh:41`, `d12y_plan_step.sh:72`,
   `dafoam_wait_then_launch.sh:82`, and `run_f27.sh:57` (cfd's own) — keep writing there,
   and the launched process still runs with `cwd` = the case directory, so anything a
   launcher writes by relative path still lands in `cases/`. Those are their owners' to fix.
4. **It changes no verdict, gate, threshold, cap, label or grading path**, and no landed
   result depends on where these four files sit: all four are **INFRASTRUCTURE** under
   L-342 by the runner's own declaration (`queue_runner.py:534`), and an
   infrastructure field can void a cost claim but never produce NOT A RESULT.
5. **It adds no `check_filing.py` rule** (§6).
6. **It does not edit any other team's file.**

---

## 9. Cost

Zero solver compute. Selftests only.

| item | measured / registered |
|---|---|
| `queue_runner.py --selftest` baseline at HEAD | **5 wall s x 1 rank = 0.083 core-min**, rc 0, 41/41 — MEASURED 2026-08-28 |
| `check_filing.py --selftest` baseline at HEAD | **< 1 wall s x 1 rank = 0.017 core-min**, rc 0 — MEASURED 2026-08-28 |
| estimate for the full implement-and-verify cycle | **1.0 core-min** (≈ 10 selftest cycles plus greps) |
| **CAP** | **5.0 core-min.** An overrun stops the work; it does not get a new budget (`CLAUDE.md` rule 12) |
| dollars at cap | **$0.0043 — DERIVED, NOT MEASURED**, at c7a.4xlarge $0.0513/core-h, a rate that is **reported-by-owner** (the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |

The rule-12 estimate-versus-actual comparison is owed to `docs/COST_CALIBRATION.md` at
implementation completion and is **not discharged by this document**.

---

## 10. Blast radius — MEASURED, and ROUTED, NOT DECIDED

`scripts/queue_runner.py` is **shared lab infrastructure**. Six teams launch through it.

| team | exposure | measured |
|---|---|---|
| **cfd** | owner; 28 files under `cases/`; §5.1 clobber is cfd's own | direct |
| **dafoam** | 52 files under `cases/`; **§5.2 documented-invariant coupling in two of their files** | direct, and the only one needing agreement |
| **heat-transfer** | launches through the runner; 55 launched records at HEAD | location change only, no reader |
| **ansys-verification** | launches through the runner; already repaired one case case-side at `b7bed168` | location change only, no reader |
| **closure** | 2 launched records at HEAD | location change only, no reader |
| **verification** | owns `check_filing.py::R6-RUNARTIFACT`, which this spec cites and does not edit | informational |

**cfd's position:** the code change is four lines in cfd's own file and breaks no reader in
any team's code (§3.3). **cfd does not treat that as authority to land it.** dafoam's
`dafoam_wait_then_launch.sh` header states a measured dependency that this change falsifies
(§5.2), and a shared-infrastructure change that invalidates another team's written
invariant is routed to the chief and to that team before it lands, not after. **That
routing is the supervisor's act, not this lane's.**

---

## 11. Ruling requested

1. **Does (b) land?** — cfd-supervisor, on §3.3 and §4.
2. **Does dafoam accept §5.2**, and do they want `dafoam_wait_then_launch.sh:82` and
   `d12y_plan_step.sh:72` changed in the same window? — dafoam-supervisor.
3. **Is a shared-infrastructure location change a cfd tooling ruling, or does it go to
   Sanaa's desk?** — chief. This document is written; the code does not land until this is
   answered.
