# R5 — PRE-REGISTRATION: THE RUNNER `STATUS.<case_id>` COLLISION GUARD, as a frozen, capped, schedulable REPAIR ITEM

**Team:** cfd. **Owner:** cfd-supervisor. **Registering lane:** cfd lane **R45**, 2026-08-28.
**Status at writing: FROZEN ON COMMIT. No code exists. Zero compute has been spent.**
**Verdict at registration: `PENDING`.** Fully specified, fully capped, schedulable, and — unlike
the larger relocation it overlaps (§4) — **owned entirely inside cfd and requiring no referral.**

**Authority for registering a repair as a queue item.** Sanaa's amendment of 2026-08-28T17:01Z,
verbatim: *"the finding-repairs are the queue: they're frozen, capped, schedulable work items like
any case"*. **Measured by this lane at 2026-08-28T17:38Z: `verification/queue/cfd/*.json` → 0
entries.**

**Model and house style:** `R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md`,
`R2_QUEUE_HOST_SCOPE_REPAIR_PREREGISTRATION.md`, `R3_COMMIT_RENAME_MODE_PREREGISTRATION.md`, all
frozen at **`f7da1a24ca8c730d5c49a7ea429840c43378bf1e`**, verified by this lane an ancestor of HEAD
`1f74d6de1780c4cac36d7a1539ecde97266fd23d` at 2026-08-28T17:30:10Z.

---

## 1. WHAT THIS ITEM IS, IN ONE PARAGRAPH

`scripts/queue_runner.py:496` computes `status = cwd / f"STATUS.{case_id}"` from a path **the
entry supplies**, and `:501` truncates it with a shell `>` after the launch argv returns. When a
case's own launcher writes the same basename into the same directory, **the runner's one line
replaces the launcher's record, and the surviving line looks correct.** This item makes the
runner's write **unable to occupy a path it did not name** — by writing `STATUS.queue.<case_id>`
unconditionally — and proves by control that the record is still written, that the guard is
load-bearing, and that nothing else in the runner moved. **It authorises no solver compute and
does not touch any other team's launcher.**

## 2. WHAT THIS LANE VERIFIED ITSELF — THE COLLISION IS REAL, AND ONE CLAIM IN THE BRIEF IS FALSE

Every reading below is from one named artefact, in this lane's own invocations at HEAD
`1f74d6de`, with both instruments' worktree copies confirmed equal to their HEAD blobs by
`git rev-parse HEAD:<path>` against `git hash-object <path>` — the only index-immune comparison
available while the shared index stages ~300 whole-file deletions.

### 2.1 The two writers, and that their paths are byte-identical

- `scripts/queue_runner.py:496` — `status = cwd / f"STATUS.{case_id}"`; `:497` `out = cwd /
  "launcher.queue.out"`; `:501-502` the detached wrapper is
  `cd '<cwd>' && <argv> > '<out>' 2>&1; R=$?; echo "launcher_rc=$R end=… note=…" > '<status>'`.
  **The `>` fires after the argv returns.**
- `cases/F27_WOMERSLEY_PIPE/run_f27.sh:57` — `STATUS="$ROOT/STATUS.F27_WOMERSLEY_PIPE"` with
  `ROOT="/home/ubuntu/Certonomous/cases/F27_WOMERSLEY_PIPE"` (`:48`). The queue entry's `cwd` is
  that same directory. **The two paths are byte-identical.**
- `run_f27.sh:87-92` writes it from an **EXIT trap**, so the launcher writes first and the runner
  writes second, unconditionally. `:89-90` emits a **richer** record:
  `launcher_rc=%s end=%s note=exit-status-of-run_f27.sh-NOT-the-solver-rc cap_core_min=%s
  spent_core_min=%s`.

**The launcher already knew.** `run_f27.sh:83-86` says in its own comment: *"When the queue runner
launches this script it writes its own STATUS line after the argv returns, superseding this one
with the identical meaning."* **That comment is right about the ordering and wrong about the
meaning** — the two records are not of identical meaning, because two of the launcher's four
fields have no counterpart in the runner's line. The collision was documented and its cost was
mis-assessed.

### 2.2 The destruction, measured

`cases/F27_WOMERSLEY_PIPE/STATUS.F27_WOMERSLEY_PIPE`, **93 bytes**, mtime **2026-08-28 09:01**,
**untracked at HEAD**, holds exactly:

    launcher_rc=0 end=2026-08-28T09:01:29Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc

**That is the runner's format, not F27's** — no `cap_core_min=`, no `spent_core_min=`, and the
`note=` field names *the launch argv* rather than `run_f27.sh`. **F27's own record was overwritten.
Confirmed independently of the brief.**

### 2.3 **FALSIFICATION — THE BRIEF SAYS THE DESTROYED RECORD IS "NOT RECONSTRUCTABLE". IT IS.**

The brief directs this registration to *"say so plainly"* that the loss is not reconstructable.
**This lane checked before writing that sentence and it is false.** `run_f27.sh:336` `say`s the
same two figures to **stdout**, and the runner redirects the argv's stdout to
`cwd/launcher.queue.out` (`:497`, `:501`). Read from that one named file:

- `cases/F27_WOMERSLEY_PIPE/launcher.queue.out:29` —
  `ALL THREE LEVELS COMPLETE. Cumulative spend: 265.46666666666664 core-min of 680.`
- `:3` — `CAP AGREES between launcher and grader: 680 core-minutes.`
- and the surviving STATUS line itself still carries `launcher_rc=0`.

**All three fields of the destroyed record survive verbatim in a sibling file six inches away.**
`spent_core_min = 265.4666666666666` core-min and `cap_core_min = 680`, i.e. **39.04 % of cap** —
recovered, not estimated. The loss is therefore **the loss of a record, not the loss of the
information in it**, and this document says that rather than the more dramatic thing it was asked
to say.

**Two reasons this makes the repair MORE urgent, not less.**

1. **The recovery is perishable.** `launcher.queue.out` is written by the runner into the same
   `cwd` by the same mechanism (`:497`) and is **truncated on the next launch of the same case**.
   The recovery window is "until F27 is relaunched", and nothing on disk records that it is closing.
2. **The redundancy is an accident of one launcher.** `run_f27.sh` happens to print its spend. A
   launcher that wrote its cap and spend **only** to STATUS would lose them outright, and nothing
   in the lab stops the next one from doing exactly that. The guard is registered against the
   class, not against F27.

### 2.4 The blast radius, measured over every entry — and the datum that decides §3

For all **134** entries under `verification/queue/*/` and `verification/queue/*/*/`, this lane
computed the runner's own target `cwd/STATUS.<case_id>` and read the first line of each:

| reading | count |
|---|---|
| entries scanned | **134** |
| **the runner's target path ALREADY EXISTS on disk** | **117** |
| target absent | 17 |
| existing file in the runner's format (`launcher_rc=` or the pre-`ba365479` `rc=`) | 116 |
| existing file **not** in any runner format | **1** — `cases/dafoam/ladder-a/A2/curriculum_D6R/STATUS.D6R_chain_wait`, dafoam's wrapper series |

*A correction of this lane's own first reading, recorded because it is the instrument class this
brief warns about.* The first pass classified **6** files as foreign, on a predicate requiring the
literal `note=exit-status-of-the-launch-argv`. Five of the six read `rc=0 end=…` and are **an
older runner format**, not a foreign one: `git log -S'launcher_rc=$R' -- scripts/queue_runner.py`
names commit **`ba365479`**, whose own subject says it introduced `launcher_rc` *"labelled as NOT
the solver's rc (L-342; the false T5_X_2d rc=0)"*. **A classifier keyed on the current format
reports every historical record as foreign.** The corrected count is 1, which agrees with
`docs/standards/QUEUE_RUNNER_RECORD_LOCATION.md` §2's independent finding of exactly one
non-runner-format `STATUS.*`.

**And the census cannot see the damage it is looking for.** A `STATUS` file that has *already* been
clobbered reads as a runner record — F27's does. **A collision that has completed is
indistinguishable from no collision ever having occurred**, so this census is a lower bound and the
only instrument that can find the class is a read of the **launchers**, which is §5.

### 2.5 The baseline this item may not regress, measured today

    python3 scripts/queue_runner.py --selftest   →   rc 0, "SELFTEST PASS: 41/41 checks,
                                                     0 asserts", 5.24 wall s

**The brief's 41/41, rc 0, ~5 wall s is CONFIRMED.** Read on the bare command with output
redirected to a file — never `cmd | tail; echo $?`, which reports `tail`'s status. Run only after
reading its isolation: `tempfile.mkdtemp(prefix="queue_runner_selftest_")` at `:772`,
`shutil.rmtree(tmp)` at `:1376` against that tree alone, no literal reference to the real queue
root anywhere in `:772-1376`, and `SIGTERM` sent only to a scratch-root daemon it spawns itself
(`:1083`). **The live daemon `pid 1120800` was verified alive before (elapsed 1-00:01:13) and after
(1-00:01:47).** For reference, `queue_entry_check.py --selftest` measured **rc 0, 31 controls,
0.50 wall s** in the same invocation.

**THE NEW BAR: `41/41, rc 0` plus the rows added here, and not one row fewer.**

## 3. WHICH REPAIR — THE TWO CANDIDATES, AND THE RECOMMENDATION

### 3.1 Candidate (b) — REFUSE TO LAUNCH WHEN THE TARGET PATH ALREADY EXISTS — **REFUSED, ON A MEASURED FACT**

**117 of the 134 entries on disk already have a file at the runner's exact target path (§2.4).**
Candidate (b) would refuse the relaunch of **87 % of the lab's queue on the day it lands.**

The failure mode is not hypothetical because **nothing in the runner removes or archives that
file.** `archive_previous_records()` (`:454-470`) iterates **`launched_dir.glob("*.json")`** and
`os.replace`s the matching **JSON launch record** to `<stem>.<utc>.json`; its docstring says so and
its provenance is ansys VMFL064-R2's mis-attributed `CAP_OVERRUN`. **It never looks at `cwd`, never
touches `STATUS.<case_id>`, and could not: it is handed `launched_dir`, not `cwd`.** So under (b)
the stale STATUS survives every archive cycle and blocks the relaunch permanently, and the only
remedy is a human deleting a record — which is how a guard gets disabled by the first person it
inconveniences.

**The disk already shows operators paying that cost by hand**:
`verification/runs/ansys_verification/VMFLGPU001/STATUS.VMFLGPU001.attempt1` and `.attempt2`,
`verification/runs/F15_runs/STATUS.F15.attempt1`, `F16_runs/STATUS.F16.attempt1` — manual
`.attemptN` renames. Candidate (b) would make that manual step **mandatory, lab-wide, for five
teams who did not write the defect.**

*(A variant — archive-then-write, extending `archive_previous_records` to the STATUS file — is
noted and NOT registered. It fixes (b)'s refusal problem but leaves the runner writing into a
namespace it does not own, which is the actual defect, and it puts the runner in the business of
renaming files in other teams' case directories. It is recorded here so a reader knows it was
considered and why it was declined.)*

### 3.2 Candidate (a) — WRITE `STATUS.queue.<case_id>` ALWAYS — **RECOMMENDED**

    status = cwd / f"STATUS.queue.{case_id}"        # queue_runner.py:496, one line

**Defended against (b), point by point:**

1. **It removes the collision by construction; (b) detects it by state.** (a) cannot be defeated by
   what happens to be on disk. A guard whose correctness depends on tree state that **nothing
   maintains** — and §3.1 measured that nothing maintains it — is a guard that fails open the first
   time somebody cleans up, and fails closed 117 times before that.
2. **It never blocks a relaunch.** Zero of 134 entries are affected at launch time. Rollout cost is
   one line and no operator action.
3. **It preserves the write unconditionally**, which is the whole point of the bookkeeping. (b)
   converts a silent data loss into a **launch outage** — trading a bookkeeping defect for a
   physics-blocking one, which is the wrong direction under L-342 (*a bookkeeping failure
   invalidates the bookkeeping, never the physics*).
4. **It is right on the merits, not merely convenient.** The runner's own docstring at `:498-500`
   and its `_field_classes` at `:526-535` class this file as **INFRASTRUCTURE** recording *the
   launch argv's exit status and explicitly not the solver's rc*. A record about the **launch**
   should not occupy the name a record about the **case** already uses.
5. **No reader breaks, and this is measured rather than assumed.** `cap_watch()` resolves the file
   through `Path(li.get("status_file", …))` — the **absolute path the runner itself stamped** into
   `_launch.status_file` at `:530` — and never reconstructs it from `cwd`. It follows the rename
   for free. `docs/standards/QUEUE_RUNNER_RECORD_LOCATION.md` §3.2 reached the same finding by an
   independent sweep with its own planted control, and named the only other reader class —
   `cases/dafoam/_common/dafoam_wait_then_launch_selftest.sh` — as reading a file **dafoam's own
   wrapper** writes, with no runner in the loop.
6. **The notice is free.** The runner's `LAUNCHED` log line already prints `STATUS=<path>`
   (`:541-543`). Under (a) it prints the new path, so the change announces itself in the runner's
   own log with **no new mechanism**.

**The honest cost of (a), stated rather than discovered later.** Two files named `STATUS.*` can now
sit in one directory — the launcher's and the runner's — and a **human** reader must know which is
which. That cost is accepted for three reasons: the machine reader is unambiguous (point 5); the
alternative to two records is **one record and one destroyed record**; and §7's annotation exists
precisely to tell the human reader which is which for the one case where the destruction already
happened.

**RECOMMENDATION: candidate (a).** Registered as the item's repair.

## 4. INTERACTION WITH `QUEUE_RUNNER_RECORD_LOCATION.md` — AND THE HONEST ANSWER IS YES, R5 IS SUBSUMED

`docs/standards/QUEUE_RUNNER_RECORD_LOCATION.md`, at HEAD, frozen at **`47e86a46`** (verified an
ancestor of HEAD by this lane), rules candidate **(b)** of *its* three: the runner writes its four
records under `<queue_root>/<team>/launched/records/`, prefixed by case id, with a `.gitignore`
holding `*`. Its §5.1 **independently found the F27 destruction** and describes it in the same
terms this document does.

**Does R5 become unnecessary if that spec lands? YES — and this document says so plainly rather
than defending its own existence.** Under the relocation the runner writes nothing into `cwd` at
all, so the collision cannot occur; and the relocation's destinations already carry the case id, so
it also closes the cross-case flag collision of §5.2. **R5 is a strict subset of it.**

**R5 is registered anyway, as the NARROW, INDEPENDENTLY-SHIPPABLE guard, on four grounds:**

1. **The relocation is REFERRED AND NOT RULED.** Its own head matter says: *"the change is cfd-owned
   code but it alters an artifact location that dafoam's `dafoam_wait_then_launch.sh` documents a
   measured dependency on … This document is written; the code does not land until routed."* **R5
   requires no referral**: it changes one basename inside cfd's own script, breaks no documented
   invariant of another team, and needs no `.gitignore`, no new directory and no migration.
2. **It falsifies a documented invariant in dafoam's file and the relocation does; R5 does not.**
   The relocation makes `dafoam_wait_then_launch.sh:36-39`'s stated measured fact **false** (that
   comment records the runner overwriting `cwd/STATUS.<case_id>`). R5 makes it *narrower* — the
   runner still writes into `cwd`, just not onto that name — which is a smaller edit to another
   team's understanding of the world, and one R5 **reports** rather than makes on their behalf.
3. **Cheap guards should not wait on cross-team routing.** R5's cap is **0.7000 core-min**; the
   relocation is a four-line change plus a directory, a `.gitignore` and a blast-radius review
   across six teams. Holding a one-line guard hostage to that is how a live loss stays live.
4. **They compose without conflict, and the retirement path is registered now.** If the relocation
   lands **after** R5, its `:496` line is rewritten wholesale and R5's basename question becomes
   moot: **R5's clause is then retired as a dated addendum to this document, not left as dead
   code**, and the relocation's own chosen basename governs. If it lands **before** R5, R5's §9
   absence condition fails at launch and R5 is **`BLOCKED`** under §8 clause 1 — its defect having
   been fixed by another item, which is a fine reason for a repair not to run and is stated in the
   fixed vocabulary rather than as prose.

## 5. THE SWEEP THE BRIEF ORDERED — `cap_watch`'s FLAGS, AND EVERY `run_*.sh` IN THE LAB

Method: `git ls-tree -r --name-only HEAD` → **375 tracked `*.sh`** (never `git ls-files`, which
reads the poisoned shared index), each opened and read individually — never a bare recursive
`grep`, which is ugrep 7.8.4 here and races its multi-file output order. **97 scripts mention one
of the four runner basenames**; every assignment line was printed and read.

*The sweep is shown able to see a real collision before it is allowed to report anything:* it found
`cases/F27_WOMERSLEY_PIPE/run_f27.sh:57`, the known-true positive of §2.1, and
`cases/dafoam/_common/dafoam_wait_then_launch.sh:82`. **A sweep that returned zero without first
finding F27 would be measuring its own regex.**

### 5.1 `STATUS.<case_id>` — collisions with a launcher

| script | line | its path | collides with the runner's? |
|---|---|---|---|
| `cases/F27_WOMERSLEY_PIPE/run_f27.sh` | `:57` | `$ROOT/STATUS.F27_WOMERSLEY_PIPE`, `ROOT` = the case dir = the entry's `cwd` | **YES — byte-identical.** §2.2 |
| `cases/dafoam/_common/dafoam_wait_then_launch.sh` | `:82` | `$CWD/STATUS.$CASE_ID`, `CWD=$(pwd)` = the `cwd` the runner `Popen`s with | **YES — byte-identical, and it is another team's.** REPORTED, NOT REPAIRED |
| `verification/runs/T-family/{T13,T14,T15,T16,T17,T18,T19,T3,T4b,T5,T5b,T9aR1b,T9aR1c,T10aR2}_runs/*.sh`, `scripts/launch_k0f{,_ext1}.sh` — **20 scripts** | `:44`–`:120` | `$ROOT/STATUS.$CASE` where `ROOT="$(dirname "$CASE_DIR")"` and `CASE="$(basename "$CASE_DIR")"` | **NO.** The launcher writes into the **parent** of `cwd`; the runner writes into `cwd`. Different directories, checked per script |
| `verification/runs/T-family/T1_runs/run_one_dts_u.sh` | `:70` | `$ROOT/STATUS_u.$CASE` | **NO** — different directory *and* different basename |
| `cases/ansys_verification/VMFLGPU*/run_vmflgpu*.sh` — **7 scripts** | various | `$BUILD_ROOT/STATUS.smoke` | **NO** — a build-tree file, not a case-id file |
| `cases/RANS_LES_closure_models/M1_multimodel_sweep/run_m1.sh` | `:52` | `$CASE_DIR/STATUS` (no case-id suffix) | **NO** |
| `cases/dafoam/curriculum_D12R2/d12y_w3_chain_driver.sh` `:41`, `cases/dafoam/ladder-a/A2/curriculum_D14/d14m_driver.sh` `:115` | | `$HERE/STATUS.W3_chain`, `$BASE/STATUS.MESH` | **`STATUS.MESH` NO** (no entry carries that case id). **`STATUS.W3_chain` YES** — dafoam's chain driver writes the same basename the `W3_chain` entry's runner target uses. REPORTED, NOT REPAIRED |

**Result: three colliding launchers, not one.** `QUEUE_RUNNER_RECORD_LOCATION.md` §5.1's *"a sweep
of all `cases/F*/run_f*.sh` found this case only"* is **correct within its stated scope and is not
the lab-wide answer**; that spec names dafoam's wrapper separately in its own §5.2. **Two of the
three are dafoam's and this item does not touch them** — the brief's instruction is followed
exactly: reported, not repaired. **Candidate (a) fixes all three at once**, because it moves the
runner off the contested name rather than asking three launchers to move off it.

### 5.2 `CAP_OVERRUN.txt` and `ESTIMATE_OVERRUN.txt` — A DIFFERENT COLLISION, AND NOBODY HAS NAMED IT

`cap_watch()` writes `Path(meta["cwd"]) / "CAP_OVERRUN.txt"` (`:611`) and
`Path(meta["cwd"]) / "ESTIMATE_OVERRUN.txt"` (`:627`).

**Finding 1 — no launcher collides with these.** Of the 375 scripts, **exactly one** mentions
either basename and it is a **comment**: `verification/runs/T-family/T5b_runs/run_one_t5b.sh:16`.
**Zero launchers write them.** The runner-versus-launcher collision does **not** extend to the
overrun flags.

**Finding 2 — but they collide with EACH OTHER, across cases, because neither name carries a case
id.** Measured over the 134 entries: **8 `cwd` values are shared by more than one `case_id`.**

| shared `cwd` | distinct `case_id`s sharing it |
|---|---|
| `/home/ubuntu/Certonomous` | **4** — `VR1_SELECTOR_ACCEPTANCE`, `VR2_ORDERING_ARM_MONITOR`, `VR3_GUARD_SET_ATTRIBUTION`, `VR4_EXEC_HOST_CONTROL` (verification) |
| `cases/dafoam/curriculum_D12R2` | **11** — `W2R_phase2`, six `W2R_*_wait`, `W3_chain`, `W3_chain_r2/r3/r4` |
| `cases/dafoam/ladder-a/A2/curriculum_D5` | 4 — `D5_chain`, `_r2`, `_r3`, `_r4` |
| `cases/dafoam/curriculum_D12R` | 2 · `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED` | 2 |
| `cases/dafoam/ladder-a/A2/curriculum_D6` | 2 · `.../A3/curriculum_D7FR` | 2 · `.../A6/curriculum_D8R` | 2 |

In each of those eight directories there is **one slot** for `CAP_OVERRUN.txt`. The flag's text
names the case it belongs to (`:613-615`), so a reader who opens it is not deceived — **but a
second case's overrun overwrites the first's, and the first then has no flag at all.** That is the
same class as VMFL064-R2, whose mis-attribution is the documented reason
`archive_previous_records()` exists (`:454-461`).

**Measured lab-wide today: 8 `CAP_OVERRUN.txt` and 5 `ESTIMATE_OVERRUN.txt` on disk**, none of them
in a directory currently shared by two case ids, so **the cross-case flag collision is LATENT and
has not fired.** *(For reconciliation: `QUEUE_RUNNER_RECORD_LOCATION.md` §2's "4 and 0" was scoped
to `cases/`; exactly 4 of my 8 and 0 of my 5 are under `cases/`. The two counts agree.)*

**THIS IS REPORTED AND NOT REPAIRED HERE, deliberately.** It is a **different defect** — runner
versus runner, not runner versus launcher — its fix is a per-case prefix rather than a namespace,
and the relocation spec of §4 already specifies exactly that prefix. Folding it into R5 would widen
a one-line guard into a second repair with its own controls and its own cap, and would let this
item's PASS stand on evidence about a defect it was not registered against. **It is routed to the
cfd-supervisor as a finding, with the eight directories named above so nobody has to re-derive
them.**

## 6. THE OBSERVABLE — AND IT IS NOT A RICHARDSON QUANTITY

**The observable is the CONTROL OUTCOME VECTOR** `(S1 … S9)`, each element `FIRED` / `HELD` /
`FLIPPED` / `NOT RUN`, together with the set-equality reading of S9.

**Stated explicitly, so it cannot later be asked for:**

- There is **no grid triple**, no refinement ratio `r`, no mesh, no field, no level.
- **NO OBSERVED ORDER OF ACCURACY IS COMPUTED** and none will be reported.
- **NO GCI IS COMPUTED OR QUOTED**, at `Fs = 1.25` or any other factor.
- `scripts/roache_triple.py` is **not called**. Standing rule 5 is **INAPPLICABLE** — not waived,
  not satisfied — because it grades a row that has a grid triple and this row has none. In-family
  precedent: `cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md` §4, the same precedent R1 §3,
  R2 §3 and R3 §3 cite.
- **F27's recovered `265.4666666666666` core-min of a 680 cap (§2.3) is NOT an observable of this
  item.** It is a figure recovered from an existing artefact while verifying the defect, reported
  under §7, and it is not graded here.

## 7. F27's RECORD — BOARDED, ANNOTATED BY SOMEBODY ELSE, AND NOT EDITED BY THIS ITEM

**The file is not repaired and not rewritten.** `cases/F27_WOMERSLEY_PIPE/STATUS.F27_WOMERSLEY_PIPE`
stands as it is: a **run artifact**, untracked at HEAD, holding the **runner's** record.

**What is owed is an annotation, and it is a record, not an edit.** It must state: that the
surviving line is the **runner's** record and not the case's; that `run_f27.sh:88-91`'s richer
record occupied that path first and was overwritten by `queue_runner.py:501`; and that the
overwritten fields are **recovered, not lost** — `cap_core_min = 680` and
`spent_core_min = 265.4666666666666` (**39.04 % of cap**), both read from
`cases/F27_WOMERSLEY_PIPE/launcher.queue.out:29` and `:3`, **with the warning that
`launcher.queue.out` is itself truncated by the runner on the next launch of F27, so the recovery
window is open only until then.**

**Where it belongs:** beside the artifact it describes, in the F27 case directory, as a new
`STATUS_PROVENANCE.F27_WOMERSLEY_PIPE.txt` — **not** as an edit to the STATUS file (which would
destroy the evidence a second time), **not** in `docs/` (it is a run-artifact provenance note, not
a standard), and **not** in any scratchpad (L-186: the scratchpad is not a handoff channel and a
repository document never cites a scratch path). `run_f27.sh` is a **frozen** grading path and rule
6 forbids editing it; the annotation touches neither it nor the pre-registration.

**THIS LANE HAS NOT WRITTEN THAT ANNOTATION AND MUST NOT.** The brief says so explicitly, and it
is right for a second reason: the annotation asserts a fact about a completed run's cost record,
and `SUPERVISION_CHARTER.md` §3's big-claim check belongs to the supervisor. **The paragraph above
is the specification of the annotation, not the annotation.**

## 8. THE REGISTERED GATES, THE BIRTH REQUIREMENT, AND THE CRITERIA

### 8.1 The gates — fixed before the work runs

| gate | statement | verdict if met | verdict if not |
|---|---|---|---|
| **G-R5-1 — THE POSITIVE CONTROL FIRES ON THE UNREPAIRED CODE (S1)** | In a scratch queue root of **production's shape**, with a **planted pre-existing `cwd/STATUS.<case_id>` holding a known sentinel**, an entry driven through the **real** `tick()`/`launch()` on the **unrepaired** runner leaves that file **NOT containing the sentinel** and containing `launcher_rc=`. **The destruction is reproduced, not assumed** | required for **PASS** | **GATE FAIL** — the defect was never demonstrated, so nothing was shown repaired |
| **G-R5-2 — THE DEFECT STOPS FIRING ON THE REPAIRED CODE (S2)** | Same fixture, same real `tick()`, repaired runner: the planted file is **byte-identical** to its planted bytes (`sha256` equal), and `sha256` is taken **before and after** in the same invocation | required for **PASS** | **GATE FAIL** |
| **G-R5-3 — THE RECORD IS STILL WRITTEN AT ALL (S3)** | After S2, `cwd/STATUS.queue.<case_id>` **exists**, is **newer** than the launch, its first line matches `^launcher_rc=\d+ end=\S+ note=`, and `_launch.status_file` in the moved `launched/` JSON is **byte-equal to that absolute path** | required for **PASS** | **GATE FAIL** — a "fix" that stops writing destroys the launch bookkeeping and would pass any naive collision check |
| **G-R5-4 — THE NEGATIVE CONTROL: NO PRE-EXISTING FILE, NORMAL LAUNCH (S4)** | With **no** file at either path, the same real `tick()` launches normally: `tick()` returns the launched state, the entry is moved to `launched/`, `LAUNCH_LOG.tsv` gains **exactly one** row, and `STATUS.queue.<case_id>` is written | required for **PASS** | **GATE FAIL** — a repair that refuses everything passes S1–S3 |
| **G-R5-5 — RELAUNCH IS NOT BLOCKED (S5)** | The **same entry launched twice in a row** into the same `cwd`, through the real `tick()` both times, launches **both** times; the second overwrites `STATUS.queue.<case_id>` and `archive_previous_records()` archives the first **JSON record** to `<stem>.<utc>.json`. **This is the limb candidate (b) would have failed on 117 of 134 entries** | required for **PASS** | **GATE FAIL** |
| **G-R5-6 — `cap_watch` STILL FINDS THE FILE (S6)** | With an overrun forced by an injected clock, `cap_watch()` resolves the record through `_launch.status_file` and behaves exactly as it does today: the flag is written and its `status_seen_utc` retirement path still fires | required for **PASS** | **GATE FAIL** — the rename must be followed by the one real reader |
| **G-R5-7 — THE MUTATION FLIPS (S7)** | With `:496` reverted to `f"STATUS.{case_id}"` and **nothing else changed**, **S2 flips to destruction and S3 flips onto the old path**. A one-line guard whose reversion changes nothing was never load-bearing | required for **PASS** | **GATE FAIL** |
| **G-R5-8 — FLAG-PROOF (S8)** | An `ast` walk over `scripts/queue_runner.py` returns **zero** `ast.Assert` nodes, counted by AST and never by grep — the runner's own selftest already checks this at `:767-769` and it must still hold | required for **PASS** | **GATE FAIL** |
| **G-R5-9 — NO REGRESSION, AND NOTHING ELSE MOVED (S9)** | `queue_runner.py --selftest` returns **rc 0 at 41/41 plus the rows added here and not one fewer**; its check-name set differs from today's by **only** the added rows; `queue_entry_check.py --selftest` returns rc 0 with 31 controls; and §8.3's invariance set is **bit-identical** | required for **PASS** | **GATE FAIL** |

**PASS iff all nine hold. Any one not holding is `GATE FAIL`.** §8.4's conditions take precedence.

### 8.2 The birth requirement — Sanaa directive 1, as a refusal condition on this instrument

Sanaa, 2026-08-28T17:01Z: *"A planted control must travel the real production path — written by the
real producer's code, read through the real reader … no instrument grades anything until that
answer is yes, demonstrated."*

**THE REAL PRODUCER, NAMED.** `scripts/queue_runner.py::launch()` — `:496` the `status` path,
`:501-502` the detached wrapper string, `:503-507` the `Popen(["setsid","nohup","bash","-c",inner],
cwd=str(cwd))` that actually writes it, `:520` `shutil.move`, `:530` the `_launch.status_file`
stamp, `:536` `dst.write_text`. **The bytes in the STATUS file must be written by that `Popen`, not
by the control.**

**THE REAL READER, NAMED.** `queue_runner.tick()` for the launch decision, and `cap_watch()`
resolving `_launch.status_file` for S6. **Not a re-implementation and not a stub.**

**BR-1 — MANDATORY; THE DRIVER EXITS 2 AND GRADES NOTHING UNLESS, IN THE SAME INVOCATION:**

> (i) the scratch queue root has **production's shape** —
> `<scratch>/…/verification/queue/<team>/` — the shape
> `QUEUE_ENTRY_TEAM_BINDING.md` amendment 2 made mandatory after a control passed vacuously on a
> flat root;
> (ii) the planted `cwd/STATUS.<case_id>` is written **before** the tick, its `sha256` recorded, and
> its content is a **sentinel that the runner's format cannot produce** — it carries
> `cap_core_min=` and `spent_core_min=` in `run_f27.sh:89`'s exact shape, so "was it destroyed" is
> answered by content and never by mtime;
> (iii) **S1 fires first**: the destruction is observed on the **unrepaired** runner, with the
> post-tick file shown **not** to contain the sentinel, before the repaired run may report that it
> does not destroy it;
> (iv) the launch argv is a **trivial real command** and the driver waits for the wrapper to
> complete — it asserts `STATUS.queue.<case_id>` **exists and is newer than the launch epoch**
> before reading it, so no control ever reads a file the wrapper has not finished writing;
> (v) **no path under the real `verification/queue/` is opened for writing at any point**, and the
> live daemon `runner.pid` is read but never signalled.
>
> **If any of (i)–(v) fails the driver exits 2 and grades NOTHING.**

**WHY A HAND-WRITTEN STATUS FILE IS REFUSED, in this document's own words.** A STATUS file written
by the control is a schema the producer never emitted; grading against it would certify that the
control can overwrite its own file. Sanaa's directive names this exact failure. **And the plant,
not the assertion, is where blindness lives**: a sentinel the runner's own format could have
produced would make S2 unfalsifiable, which is why (ii) fixes the sentinel's shape rather than
leaving it to the implementer.

### 8.3 The invariance set — bit-identical, `sha256` before and after

1. **Every file under `verification/queue/`** — every team directory, every `held/`, `launched/`,
   `LAUNCH_LOG.tsv`, and the runner's own logs.
2. **Every file under `cases/F27_WOMERSLEY_PIPE/`**, including `STATUS.F27_WOMERSLEY_PIPE`,
   `launcher.queue.out` and `run_f27.sh`. **§7 is an annotation somebody else writes; this item
   must be shown not to have touched F27 at all**, and the recovery window of §2.3 depends on
   `launcher.queue.out` surviving untouched.
3. `docs/standards/QUEUE_RUNNER_RECORD_LOCATION.md`, `QUEUE_ENTRY_HOST_SCOPE.md`,
   `QUEUE_ENTRY_TEAM_BINDING.md`, `QUEUE_ENTRY_VALIDATOR_RULINGS.md`, `QUEUE_ENTRY_STANDARD.md`,
   `RUNNER_CAP_ENFORCEMENT_CLAUSE.md` — frozen standards; rule 6.
4. This document, and `R1`/`R2`/`R3`/`R4`.
5. `scripts/queue_entry_check.py` — **byte-identical, in full. R5 does not touch the validator.**
6. `cases/dafoam/_common/dafoam_wait_then_launch.sh` and every other team's launcher — **named so
   the "reported, not repaired" ruling of §5.1 is mechanical and not merely promised.**
7. `scripts/roache_triple.py` — named because it is the lab's shared comparator and this item must
   be shown not to have touched it, **not** because it is used (§6: it is not called).

**The permitted edit to `scripts/queue_runner.py` is ONE HUNK: line `:496`, and the control rows
added to `selftest()`.** Any third hunk is `GATE FAIL` under G-R5-9. **The diff is read as a diff by
the supervisor personally** — `SUPERVISION_CHARTER.md` §3 check 1, which may never be delegated and
which no control result discharges.

**The live daemon.** `--daemon` was running as **pid 1120800** at 2026-08-28T17:34Z, elapsed
1-00:01:47, verified alive after this lane ran the runner's selftest. **This item must not restart,
signal or race it.** Any restart is the supervisor's decision. *A landed edit to `:496` changes the
behaviour of the next launch the running daemon performs only when it is restarted; whether and
when to restart is stated here as the supervisor's call and is deliberately left unanswered.*

### 8.4 Criteria — how the verdict is reached, in order

1. **BLOCKED** if §9's absence condition or §10's enqueue preconditions are unmet at launch —
   including the case where `QUEUE_RUNNER_RECORD_LOCATION.md`'s relocation has already landed and
   `:496` no longer writes into `cwd` (§4 ground 4). Nothing is graded.
2. **NOT A RESULT** if BR-1 refuses (exit 2) — the instrument was never shown able to see the
   destruction through the real code path.
3. **NOT A RESULT** if the driver's own completion clause fails: rc != 0, no terminal record line,
   or any of S1–S9 reported `NOT RUN`.
4. **GATE FAIL** if any of G-R5-1 … G-R5-9 is not met, naming which.
5. **PASS** iff all nine are met and none of 1–3 applies.

**No partial credit and no degraded reading** — rule 4's *refuse rather than degrade*.

## 9. COST, CAP AND CALIBRATION — rule 12 — AND THE RULE-2 ABSENCE CONDITION

### 9.1 The basis, term by term, each labelled MEASURED or ALLOWANCE

`ranks = 1`. Core-minutes = wall s × ranks ÷ 60.

| term | wall s | basis |
|---|---|---|
| a) `queue_runner.py --selftest` × 3 — the pre-repair baseline for S9, the post-repair run, and the mutation run of S7 | **15.8** | **MEASURED.** One run took **5.24 wall s**, rc 0, 41/41, in this lane's invocation, after its `mkdtemp` isolation was read and the live daemon verified alive on both sides. **This is the term R2 §9.1 declined to measure and carried at 40.0 s for two runs; the truth for two is 10.5 s.** |
| b) the new rows S1–S7, each driving a **real** `tick()`/`launch()` with a real detached wrapper in a production-shape scratch root, plus S5's double launch and S6's injected-clock `cap_watch` | 8.0 | **ALLOWANCE**, on the measured rate of the existing suite: 41 controls including ~10 real ticks in 5.24 s ≈ 0.5 s per tick; 7 new controls plus wrapper-completion waits. |
| c) the §5 sweep re-driven over all 375 tracked `*.sh` and all 134 entries — mandatory at implementation, because a tree state has a shelf life | 2.0 | **ALLOWANCE.** The same sweep ran in under 1 wall s in this invocation. |
| d) the §8.3 `sha256` invariance set and the record write | 2.5 | **ALLOWANCE.** |
| **TOTAL** | **28.3** | |

### 9.2 THE ESTIMATE, THE CAP AND THE RATIO

| | value |
|---|---|
| **cost_core_min_estimate** | **0.4717** core-min (28.3 wall s × 1 rank ÷ 60) |
| **cap_core_min_registered** | **0.7000** core-min |
| **cap / estimate** | **1.4840** |
| dollars at the estimate | **$0.000403** — **DERIVED, NOT MEASURED** |
| dollars at the cap | **$0.000599** — **DERIVED, NOT MEASURED** |

Rate **$0.0513 per core-hour**, c7a.4xlarge, **owner-stated 2026-08-21/22 and
reported-by-owner, never measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **A tiny cost is still a cost**; rule 12 disqualifies a proposal
carrying none.

**HOW THE CAP IS ENFORCED, and it is never raised.** The cap converts to a wall allowance of
**42.0 s** at 1 rank, handed to `timeout` **around terms (b), (c) and (d)** — the three allowance
terms. Term (a) is measured and is not the exposure. An overrun **kills the step and STOPS the
item**, leaving the controls incomplete, which §8.4 clause 3 grades **NOT A RESULT**. **The correct
response to term (b) proving larger than 8 s is a NOT A RESULT and a re-registration with a
measured basis — not a new budget.**

### 9.3 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion the record **must** carry: actual core-minutes from the driver's own log, gross and
cleaned separately; waste named separately and never absorbed into the ratio; the ratio
actual/predicted against **0.4717**; the gap attributed to contention, waste or misprediction —
and, because term (b) is the only large allowance, the attribution must say explicitly how much of
any gap is term (b)'s; dollars **derived, not measured**. A row lands in
**`docs/COST_CALIBRATION.md`**. **A completion report without this comparison is incomplete.**

**Not this item's row, but owed:** F27's own estimate-versus-actual is now computable from §2.3 —
**265.4666666666666 core-min actual against a 680 core-min registered cap, 39.04 % of cap** — and
belongs in F27's calibration row, not in R5's. It is stated here because this lane recovered the
figure and the recovery is perishable (§2.3), **not** because R5 claims it.

### 9.4 RULE-2 ABSENCE CONDITION, CHECKED IN THIS WRITING INVOCATION

**At 2026-08-28T17:35:08Z, in this lane's own invocation, each checked FOUR ways —
`os.path.exists` → False, `os.path.lexists` → False (so not a dangling symlink), `os.path.isdir`
→ False, `glob` on the literal path → `[]`:**

- `/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS` — **DOES NOT EXIST**
- `/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS/R5_STATUS_COLLISION_2026-08-28` —
  **DOES NOT EXIST**
- `/home/ubuntu/Certonomous/scripts/run_r5_status_collision_repair.sh` — **DOES NOT EXIST**

**A fifth, wider check:** `glob('verification/runs/TOOLING*')` → **`[]`** and
`glob('scripts/run_r[45]*')` → **`[]`**. **0.000 core-min have been spent under this
registration.** No driver, no control record, no scratch queue root and no planted STATUS file
written by this item exists anywhere.

**A sixth condition, specific to this item and load-bearing for §4 ground 4:**
`scripts/queue_runner.py` at HEAD `1f74d6de` hashes to blob
`94fdabfcaf661d0d7cf3bdf1bbffae81e3845f03`, **identical to the worktree copy**, and its `:496`
still reads `status = cwd / f"STATUS.{case_id}"`. **The relocation has NOT landed.** If it has by
launch time, §8.4 clause 1 applies and the verdict is `BLOCKED`.

Amendments **before** first compute remain legal under rule 2 and must state this condition and how
it was checked. **After first compute the gates are closed**; changes land only as dated addenda
that cannot alter a gate, threshold, cap or label, and originals are struck, never rewritten.

**Nothing is ever deleted by this item.** The driver creates; it holds no `rm -rf`, `rmtree` or
`shutil.rmtree` against any case, run or scratch tree it did not itself create in the same
invocation, and §8.3's invariance set is what proves it after the fact.

## 10. LAUNCH SHAPE — for the supervisor's check 4; **NOT an authorisation**

    bash /home/ubuntu/Certonomous/scripts/run_r5_status_collision_repair.sh \
         --prereg-commit=<the sha of THIS document's adding commit>

The driver **fires nothing without `--prereg-commit`** and verifies the sha is a commit in this
repository.

**ENQUEUE PRECONDITIONS — five, and the queue validator checks NONE of them** (that gap is R4's
subject; until R4 lands, this list is the only thing between an absent driver and a `LAUNCHED`
record):

1. `scripts/run_r5_status_collision_repair.sh` **exists** at the absolute path above.
2. `bash scripts/run_r5_status_collision_repair.sh --selftest` returns **rc 0**.
3. The single-hunk `queue_runner.py` diff of §8.3 is read **as a diff** by the supervisor
   personally.
4. `queue_runner.py:496` still writes into `cwd` — i.e. the §4 relocation has not landed. If it
   has, the correct action is **`BLOCKED`**, not a rewritten R5.
5. The `prereg_commit` placeholder in the held queue entry has been replaced with the real sha of
   this document's adding commit, re-derived from `git log --diff-filter=A -- <path>` and **never
   from a subject line**.

A queue entry is drafted at `verification/campaign/queue_entry_R5_RUNNER_STATUS_COLLISION.json` and
is **HELD beside this registration. THIS LANE DOES NOT ENQUEUE IT and has committed nothing.**
**Enqueueing is not authorisation.**

## 11. WHAT IS **NOT** CLAIMED, REGISTERED OR AUTHORISED HERE

- **No verdict of any rung is re-graded, in any team.** F27's verdict, bands and cap are untouched.
  The destroyed record is **INFRASTRUCTURE** under L-342 (`queue_runner.py:526-535` classes
  `STATUS.<case_id>` and `launcher.queue.out` explicitly), and **a bookkeeping loss never voids
  physics** — Sanaa's universal rule, 2026-08-26. The loss touches the cost claim, and §2.3 shows
  even that survives.
- **F27's STATUS file is NOT edited, repaired, restored or deleted by this item**, and **this lane
  did not annotate it.** §7 specifies an annotation; it does not write one.
- **`run_f27.sh` is not edited.** It is a frozen grading path; rule 6.
- **No other team's launcher is repaired.** `dafoam_wait_then_launch.sh:82` and
  `d12y_w3_chain_driver.sh:41` are **reported** (§5.1) and are in the invariance set (§8.3 clause 6)
  precisely so that "reported, not repaired" is mechanical rather than promised.
- **The cross-case `CAP_OVERRUN.txt` / `ESTIMATE_OVERRUN.txt` collision is REPORTED, NOT REPAIRED**
  (§5.2). It is a different defect with a different fix, and this item's PASS must not rest on
  evidence about it.
- **`scripts/queue_entry_check.py` is not modified at all** (§8.3 clause 5).
- **No gate, threshold, cap or label of any other registration is added, moved or removed.** R1's,
  R2's, R3's and R4's are untouched; R2's 40.0 s term is **recorded as mispredicted, not amended**.
- **`QUEUE_RUNNER_RECORD_LOCATION.md` is neither adopted, refused, pre-empted nor amended.** Its
  chief-level referral is untouched and R5 does not route around it; §4 states plainly that the
  relocation subsumes this item.
- **Runner cap ENFORCEMENT is not switched on.** `cap_watch` still reports and never kills;
  `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md` (D539) stays ADVISORY, INERT and OFF, and
  switching it on is Sanaa's alone.
- **The live daemon is not restarted, signalled or reconfigured** (§8.3).
- **No observed order and no GCI is produced** (§6); `roache_triple.py` is not called.
- **No solver compute is authorised.** This item runs three selftests and a control harness.
- **Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7). Submissions are
  **PARKED**.

---

*Registration ends. Written before implementation; the commit that lands it is the freeze.*

---

## DRAFTING NOTE — 2026-08-28T17:4xZ, BEFORE THE FREEZE, BEFORE ANY COMPUTE

**HEAD at this lane's reads was `1f74d6de1780c4cac36d7a1539ecde97266fd23d`** (2026-08-28T17:30:10Z);
`f7da1a24`, `ed77957c`, `47e86a46` and `ba365479` were each verified ancestors of it in this lane's
own invocation. Peers commit constantly and a HEAD sha in a document has a shelf life. **The
supervisor re-derives the freeze sha at the freeze, from `git log --diff-filter=A -- <this path>`,
never from a subject line.**

**This lane committed nothing, staged nothing and launched nothing.** All four artifacts — two
registrations and two held queue entries — stand as **untracked** working-tree files. The shared
git index was not touched, no `git add` of any form was issued, and `refs/heads/main` was not moved.
**The freeze is the supervisor's act.**

**Filing, measured before the files were written:** `python3 scripts/check_filing.py` returned
**37 violations across 8 rules (rc 1)** at 2026-08-28T17:35Z. The after-reading and the attribution
of any change belong to the freezing invocation; an improvement claimed by the wrong agent is a
false record in the cheap direction.
