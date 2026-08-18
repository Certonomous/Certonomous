# MOVE_MAP batch 0 — the three rulings, the gate that defeated one of them, and the instrument that could lose 1.5 GB without saying so

**Nothing was moved, renamed, copied, deleted or untracked. `.gitignore` was
not edited. `git mv` was not invoked. The shared index was not touched — no
`git add`, no `git read-tree` against it.** This pass rules on what
`MOVE_MAP_BATCH0_RECONCILIATION_2026-08-17.md` measured, records the rulings in
the map, amends the one gate that made the safer of two options fail, and
repairs the hand-carry instrument. It is still preparation.

**Anchor: `4d7c195a`.** Every path-derived count below is over
`git ls-tree -r -z --name-only 4d7c195a` — **14,298 paths, 14,298 unique**,
stderr empty. Never `git ls-files`: the index is 479 paths behind HEAD and they
are by construction the newest, which is the frame defect the reconciliation's
§1 and `docs/USING_THIS_LAB.md` §8.7 both record.

**Every figure here is a commit-membership question, not a date question.**
`D357` records that `check_verdict_cells.py` dated a grade by `git log -1 --
<path>`, so amending a record re-dated it as graded that afternoon and the
instrument reported three rungs it never touched. **Nothing below is ordered or
selected by a commit date.** Every count is *is this path in this tree object*,
taken from one named commit; re-dating a blob cannot move any of them. The one
place a date-shaped word appears is the prose "landed since", and §1.2 states
what that costs: it is a **set difference between two named commits**, not a
date comparison, and where it matters the two commits are named.

**This record does not appear in its own results.** Every count was taken at
`4d7c195a`, before the commit that lands this file; the classifier, the
snapshots, the mutants and the control trees were written outside the
repository.

---

## 1. RULING 1 — a run tree is classified by what it is, not by where it sits

### 1.1 The composition, verified before the rule was written

The reconciliation found R7 grown from 137 to 497 because tracked files landed
under `docs/campaigns/F14-cooling-ladder/`, and put the split at 315 run-tree /
23 reference / 7 document / 1 script. Re-derived at `4d7c195a` over the path
snapshot, by anchored regex, with the totals reconciled rather than sampled:

| Class | Files | What it is |
|---|---:|---|
| `K0c_runs/**` | **274** | OpenFOAM cases: `system/` 66, `constant/` 45, `0.orig/` 44 leaf directories, 65 `log.*`, plus `audit/` 22 and per-case `.json`/`.report.txt` |
| `K0b_mesh_sensitivity/**` | **41** | the same shape: `system/` 9, `constant/` 8, `0.orig/` 8 |
| **run trees, total** | **315** | |
| `reference-data/**` | **23** | 22 `betts_bokhari/*.dat` published tables + `MANIFEST.md` |
| loose `*.md` | **7** | `README.md`, `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`, `K0c_RESULTS.md`, `K0d_TURBULENT_MIXED_CONVECTION_GATE.md`, `K1_STANDING_THERMAL_CHECKS.md`, `K2a_RACK_ROW_MODULE_SPEC.md`, `K2c_RACK_ROW_VALIDATION_SEARCH.md` |
| loose `*.py` | **1** | `compute_reference_metrics.py` |
| | **346** | `274 + 41 + 23 + 7 + 1 = 346` |

**315 / 23 / 7 / 1 is confirmed exactly at `4d7c195a`. It was 315 / 23 / 5 / 1
four commits earlier, and saying so is the point of the section.** At
`7554e5d3` the same derivation returned **344** files and **five** loose
markdown documents; `K2a_RACK_ROW_MODULE_SPEC.md` and
`K2c_RACK_ROW_VALIDATION_SEARCH.md` landed at `e893f57c` in between. This is a
set difference between two named commits, not a reading of any date.

**The two figures the rule is built on did not move: 315 and 23 are identical
at both anchors.** The class that moved is documentation, which is the class
R7 keeps — so the ruling is insensitive to the drift, and the drift is in the
direction that makes R7 larger rather than R25. `docs/campaigns/` holds exactly
one campaign at both anchors, so the 346 is the whole of it. The only other
prose in the tree is `reference-data/MANIFEST.md`, which is **inside** the 23;
counting it as an eighth document would double-count it out of that total.

### 1.2 The rule — R25

> **R25.** `docs/campaigns/<campaign>/<tree>/**` where `<tree>` matches
> `*_runs` or `*_sensitivity` is a **run archive**, and follows **R20's
> destination** — `verification/runs/**` — not R7's *"`docs/**` unchanged"*.
> A run tree is classified by **what it is**, not by which directory the agent
> who created it happened to choose.
>
> **R25 = 315 files**, at `4d7c195a` and at `7554e5d3` alike:
> `K0c_runs` 274, `K0b_mesh_sensitivity` 41.
>
> The campaign's gate specifications, results documents, `README.md` and
> published reference data are **campaign documentation and remain under R7**.

**Why the rule is not "R7 keeps `docs/**`, and that is that".** The leaf
directories under both trees are `system/`, `constant/` and `0.orig/` — solver
case dictionaries and initial conditions — beside `log.*` files. That is the
identical class of artifact `demo-output/website/campaign/*_runs/` holds, which
R20 sends to `verification/runs/`. Left unruled, the map sends one class of
file to two destinations depending on an authoring accident, and §1's target
tree describes `/docs/` as *"charters/ standards/ research/ papers/ + DOCKET
LESSONS LOCATIONS USING_THIS_LAB"* — a 315-file OpenFOAM case corpus is not in
that description.

**One sub-decision inside R25, made here and flagged as the owner's to
ratify: the campaign segment is PRESERVED.** `verification/runs/` is a flat
namespace and R20 already puts **27 distinct `*_runs`/`*_work` tree names**
into it. Measured at `4d7c195a`, `K0c_runs` and `K0b_mesh_sensitivity` collide
with **none** of those 27 today — but they collide the moment a second campaign
lands a tree of the same name, and `docs/campaigns/` is a per-campaign
directory where `demo-output/website/campaign/` is not. So R25's destination is

```
docs/campaigns/F14-cooling-ladder/K0c_runs/**
    -> verification/runs/F14-cooling-ladder/K0c_runs/**
docs/campaigns/F14-cooling-ladder/K0b_mesh_sensitivity/**
    -> verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity/**
```

which is the same reasoning `MOVE_MAP_EXECUTION_2026-08-17.md` §5 applies to
every many-to-one merge — *"preserve the child segment"* — applied to the one
merge that would otherwise be flat. **If the owner prefers the flat form, the
change is one line in `lab_paths._MOVES` and the count does not move.**

### 1.3 R7 restated, net of R25

| | at `fc9301c5` | at `7554e5d3` | at `4d7c195a` |
|---|---:|---:|---:|
| R7 as measured | 497 | 497 | **501** |
| less R25 | — | −315 | **−315** |
| **R7 net** | | 182 | **186** |

**R7 = 186 documentation files.** It was 137 at the map's own index frame; the
+49 is 31 of the F14 campaign's own documents and reference tables plus the
papers and build notes that have landed since, including the two K2 documents
and the validation primary at `e893f57c`. R7 still moves nothing — that is
unchanged — and the sentence *"R7 keeps `docs/**`"* now means what it says
rather than being a decision about a run archive that nobody made.

---

## 2. RULING 2 — `AWS_TREE_PLAN.md` joins R1, and the reconciliation closes at zero

`AWS_TREE_PLAN.md` is a third root-level lab record of the same class as
`LESSONS.md` and `LOCATIONS.md`, written after the map, landed at `d07ef7f7`,
tracked at HEAD and absent from the index. R1 routes that class to `docs/`.

> **R1** (amended 2026-08-17): `LESSONS.md`, `LOCATIONS.md`,
> **`AWS_TREE_PLAN.md`** → `docs/`. **R1 = 3.**

**The identity at HEAD, re-derived with both rulings applied:**

```
    780   keep in place   R0(3) R3(330) R4(202) R7(186) R9(57) + uq_batch(2)
 13,511   move            R20(8,042) R22(3,548) R11(752) R23(394) R25(315)
                          R21(279) R10(77) R8(26) R17(21) R16(19) R12(10)
                          R24(7) R5(6) R13(5) R1(3) R2(2) R6(1) R14(1)
                          R15(1) R18(1) R19(1)
      7   exceptions      X1(1) X2(1) X3(5)
      0   UNCLASSIFIED
 ------
 14,298   =  git ls-tree -r --name-only 4d7c195a | wc -l
```

**`780 + 13,511 + 7 + 0 = 14,298`. It closes with ZERO unclassified, and no
other path fails to classify.** The classifier assigns every path to exactly
one rule; the unclassified bucket is printed in full rather than counted, and
it is empty. Run with the two rulings switched off it reproduces the
reconciliation's own table at this anchor — every rule identical, R7 four
higher at 501 and R21 one higher at 279 because documents have landed since,
and **`AWS_TREE_PLAN.md` alone unclassified**, which is the reconciliation's
own finding reproduced. **That agreement is what makes the closure a result
rather than a classifier tuned until it closed.**

The four U rows stay at zero: batch 1 landed and 6,950 U-rule paths left
tracking. `uq_batch.{err,log}` remain in the keep bucket, per
`.gitignore:112-113`'s named exception.

---

## 3. RULING 3 — batch 2 takes option A, and the gate that defeated it is amended

### 3.1 The choice

`demo-output/website/campaign/MESH_AUDIT_runs/`, re-measured at `4d7c195a`:
**78 tracked files at HEAD, 78 files on disk, 380,082 bytes tracked and
380,082 on disk, and every one of the 78 is a `*.log.checkMesh`** — nothing
else, no other suffix. Identical at `7554e5d3`. That is precisely the
solver-utility class batch 2 untracks, so batch 2 takes the directory's last
tracked file and batch 7's `git mv` of it aborts, taking every other source in
that invocation with it.

**Option A is chosen**: batch 2 **excludes** those 78 from its untracking until
batch 7 has moved the tree to `verification/runs/MESH_AUDIT_runs`, and untracks
them there. A keeps the index and the disk in agreement — the move stays a
`git mv` — and holds the hand-carry set at **2 trees, 307 files,
1,510,309,145 bytes**, so G1 keeps the baseline this corpus already records.
Option B grows the carry set by design to 3 trees / 385 files /
1,510,689,227 bytes and would require G1's baseline restated in the same commit,
which is how a gate gets loosened.

The exclusion is not prose. It is `scripts/hand_carry.py`'s
`BATCH2_EXCLUSIONS`, a named constant, and changing it changes what batch 2
untracks and what the projection reports in one place.

### 3.2 The plan's own gate was satisfied by the riskier option and failed under the safer one

`batch2_survivors()` classified `*.log.checkMesh` inside a `*_runs` tree as
output **by file class**, not by what batch 2's list contained. Batch 2's stated
verification is *"the goes-dark-after-batch-2 section must read 0 afterwards,
not 1"*, and under a class test:

- under **(B)** it read **0** trivially — the tree is already dark, so it is
  already in today's carry set and the projection reports only the difference;
- under **(A)** it read **1** — batch 2 had spared the 78 and nothing was ever
  going to go dark, but the projection kept classifying by suffix.

**So the pass condition rewarded the option that grows the carry set and
punished the option that preserves every invariant the plan states.** A gate
that inverts like that is not a weak gate; it is a gate pointing the wrong way,
and the agent who meets it fixes it by taking B.

### 3.3 The amendment

`batch2_survivors(tracked, untrack_list=None)` now tests **membership of batch
2's actual list**:

```
batch2_class_candidates(tracked)          # what the FILE-CLASS rule reaches
batch2_untrack_list(tracked, exclusions)  # batch 2's LIST = candidates - exclusions
batch2_survivors(tracked, untrack_list)   # p survives iff the LIST does not name it
```

`exclusions` defaults to `BATCH2_EXCLUSIONS`, so **the default IS the ruled
option** — a gate whose default differs from the batch's own choice reads one
thing while the batch does another. `derive --batch2-list FILE` hands the gate
batch 2's literal list once it exists, so the projection stops reconstructing
what it can be told. `derive --batch2-option B` fires the other direction.

### 3.4 The plant, in both directions, on the live tree

`python3 scripts/hand_carry.py derive`, at `4d7c195a`, stderr empty on both
runs and byte-identical to the same pair run at `7554e5d3`:

| Run | batch 2's list | GOES DARK AFTER BATCH 2 | Carry set |
|---|---:|---:|---|
| `derive` (option A, the ruled default) | **7,599 paths** | **0** | 2 trees, 307 files, 1,510,309,145 B |
| `derive --batch2-option B` | **7,677 paths** | **1** — `MESH_AUDIT_runs`, 78 f, 380,082 B | 2 trees, 307 files, 1,510,309,145 B |

**7,677 − 7,599 = 78**, exactly the excluded files, which is the arithmetic
check on the exclusion itself. The carry set is byte-identical between the two
runs and byte-identical to the pre-amendment derivation, so **G1's baseline is
untouched by this change**.

**Neither direction is evidence alone**, so both are pinned by tests and both
were falsified against a planted mutant, re-run at this anchor:

| Mutant | `test_..._when_the_ruled_exclusion_is_honoured` | `test_..._when_the_ruled_exclusion_is_dropped` |
|---|---|---|
| **the pre-amendment class test**, API otherwise intact | **RED** (synthetic and live) | GREEN |
| **the projection can never fire** (`batch2_untrack_list` returns `[]`) | GREEN | **RED** (synthetic and live) |
| the module as committed | GREEN | GREEN |

The first row **is the defect reproduced**: a gate that reads 1 under option A
and 0 under option B. The second row is its mirror, and without it the first
test is satisfied by a projection that fires on nothing. A third test,
`test_the_survivors_are_a_membership_test_and_not_a_class_test`, pins the
property directly by handing the function a list that spares a solver log and
one that names a `RECORD.md` — neither of which a class test can express.

---

## 4. REPAIR — `hand_carry.py` could report success while data went missing

### 4.1 The defect, reproduced rather than restated

`measure()` walked with `os.walk(abs_dir)` and **no `onerror`**, and its
per-file `lstat` was wrapped in a bare `except OSError: continue`.
`maximal_dark_trees()` had the same shape. `os.walk`'s default `onerror`
swallows the exception and yields nothing for that directory, so an unreadable
directory or an unstatable file **dropped out of the file count, the byte total
and the path digest at once**, without a line reaching stderr.

**All three moved together and consistently, which is why the after-check could
not see it.** `carry()` compares two measurements taken by the same instrument;
a blinded instrument agrees with itself. That is a hand-carry verification that
reports success while data went missing — the precise failure the script exists
to prevent, and worse than no check, because it is signed.

### 4.2 The control — a scratch copy, one directory made unreadable

Run outside the repository, on a copy of the real `demo-output/website/surfaces`
tree with a two-file subdirectory added, comparing **HEAD's blob of the module**
— byte-identical to the module at `7554e5d3`, checked — against the repaired
one on the same bytes:

```
CLEAN, both modules
  pre-repair : 9f 2452694B d8c0f97ec83f
  repaired   : 9f 2452694B d8c0f97ec83f      identical

ONE DIRECTORY MADE UNREADABLE  (chmod 000 inner/)
  pre-repair : RETURNED 7f 2180257B 5519de4237b7
               <-- SHORT BY 2 FILES AND 272,437 BYTES, SILENTLY, exit 0
  repaired   : REFUSED -- MeasurementError: 1 walk/stat error(s) ...
               "REFUSING to report a number"
```

And end-to-end, through the command line, on a scratch repository built to the
same shape as a campaign run archive (`LAB_REPO` pointed outside this tree):

| Module | one directory unreadable | exit | stderr |
|---|---|---:|---|
| HEAD's `hand_carry.py` | **HAND-CARRY: 1 tree, 1 file, 689,284 B** — half the tree gone | **0 — PASS** | **empty** |
| the repaired module | `UNKNOWN: 1 walk/stat error(s) …` and the failing path named | **3 — UNKNOWN** | the path, on stderr |

Same tree, same command, and the pre-repair tool reported a green,
self-consistent, wrong number. With everything readable both modules report
**2 files / 724,968 bytes** and exit 0, so the repair does not move a clean
measurement.

### 4.3 What the repair is

- `measure()` walks with an explicit `onerror`, records every walk failure
  **and** every failed `lstat`, prints each to **stderr** as
  `hand_carry: WALK ERROR under <root>: <path>: <errno>`, returns
  `walk_errors` and `error_paths` in the result, and then **raises
  `MeasurementError` rather than returning a smaller number**.
- `maximal_dark_trees()` gains the same `onerror` and refuses the same way. One
  level up, the silent loss is a whole dark tree rather than a file — and an
  unreported dark tree **is** the 1.51 GB left behind.
- `derive()` accumulates the failures across every tree so the operator sees
  all of them in one pass, then refuses.
- `carry()` refuses **before moving anything** if the source cannot be
  measured, and reports FAIL rather than "carried" if the measurement fails
  **after** the move — *"we cannot count what arrived" is not "it arrived"*.
- `verify()` reports FAIL, never OK, for a tree it cannot measure.
- `main()` exits **3 UNKNOWN** on a measurement failure. Under the lab's
  three-valued contract 3 is not green, and it is not 1 either: the tool did
  not compare and fail, it could not measure.

`strict=False` exists for a caller that wants to inspect `walk_errors` itself.
No caller in the module uses it; the tests use it to show what the old code
returned.

### 4.4 The tests, and the mutants that prove they bite

Six new tests in `sdk/tests/test_hand_carry.py`, and the suite for the file
goes from **24 to 35 passing** (plus 2 subtests), stderr clean; with
`test_lab_paths.py` beside it, **72 passed, 69 subtests**:

| Mutant planted | Caught by |
|---|---|
| `measure` swallows again (`except OSError: continue`, no `onerror`) | `test_an_unreadable_directory_is_refused_not_silently_undercounted`, `test_the_error_reaches_stderr_and_is_not_only_an_exception`, `test_the_carry_refuses_rather_than_calling_an_unmeasurable_tree_moved` |
| `maximal_dark_trees` loses its `onerror` | `test_the_dark_tree_walk_refuses_rather_than_missing_a_tree` |
| — | **control:** `test_the_control_a_readable_tree_measures_clean` stays GREEN under all mutants, without which a `measure` that raised on everything would satisfy the lot |

`test_the_carry_refuses_…` asserts the **reason** and not only the exit code,
because a swallowing `measure` also reddens there — via the drift check, which
sees the short count — and a test satisfied by that is masked exactly the way
this file's own header warns about. It also asserts that `mv ` never appears in
the output: the refusal happens before the move.

`test_an_unstatable_file_is_refused_not_silently_undercounted` covers the other
half of the defect — the directory lists but its entries do not stat, so the
walk succeeds and the per-file `except` ate the file — and skips itself, loudly,
on a filesystem that stats entries the directory bits should have refused. All
of these skip under `geteuid() == 0`, because root ignores the bits they plant.

---

## 5. What R25 costs the executable side, measured

**`scripts/lab_paths.py` does not implement R25 yet, and this pass did not add
it.** Binding it is a code change with a gate consequence, and the consequence
was measured rather than left to be discovered, by wrapping `redirect()` in a
probe outside the repository and re-running the whole derivation both ways in a
single invocation at `4d7c195a`:

| Bucket | as committed (no R25) | with R25 bound | Δ |
|---|---|---|---|
| **HAND-CARRY** | 2 trees, 307 f, **1,510,309,145 B** | 2 trees, 307 f, **1,510,309,145 B** | **none** |
| RIDES ALONG | 963 trees, 33,819 f, 10,560,965,662 B | 1,580 trees, 39,266 f, 11,396,425,309 B | +617 trees, +5,447 f, +835,459,647 B |
| STAYS PUT | 622 trees, 15,734 f, 1,455,590,108 B | 5 trees, 10,287 f, 620,130,461 B | −617 trees, −5,447 f, −835,459,647 B |
| DISCARD | 7 trees, 40 f, 1,205,649 B | 7 trees, 40 f, 1,205,649 B | none |

**G1's baseline does not move**, which is the load-bearing half: the ruling
costs the carry gate nothing. What changes is that **617 dark trees / 5,447
files / 835.5 MB of gitignored bulk under `docs/campaigns/F14-cooling-ladder/`
stop being STAYS PUT and become RIDES ALONG** — carried by batch 7's `git mv`
**only if that move names the DIRECTORY**. A per-file loop leaves 835 MB
behind on top of the 10.56 GB the plan already names. That is the same
invariant, with a larger number behind it.

This also settles what the reconciliation observed from the other side: the
STAYS PUT bucket did not gain 615 trees, **a tree fragmented** — F14 accounts
for 617 of the 622 stays-put trees at this frame, and under R25 every one of
them has a carrier.

**These four rows are a filesystem walk of live trees and are a moving target.**
Both columns come from one invocation over one tracked snapshot, so they are
comparable with each other; neither is a constant. The DISCARD row alone moved
between two readings an hour apart (34 files / 996,183 B → 40 / 1,205,649 B) as
`__pycache__` trees appeared under a test run, which is what a moving target
looks like when you watch it.

---

## 6. The batch sizes, re-derived with both rulings

| Batch | plan's figure | at `4d7c195a` | Δ | why |
|---|---:|---:|---:|---|
| 4 — `media/`, `ops/`, `docs/` (R10 R11 R12 R2 R6 R8 R19 **R1**) | 871 | **872** | +1 | R1 gains `AWS_TREE_PLAN.md` |
| 5 — research (R14–R18, R23) | 437 | **437** | 0 | |
| 6 — cases (R5, R22) | 3,553 | **3,554** | +1 | one dafoam file |
| 7 — verification (R20, R21, R24, **R25**) | 8,216 | **8,643** | **+427** | +102 run files and +10 records the index cannot see, **+315 R25** |
| 8 — the webroot cut (R13) | 5 | **5** | 0 | |

Batch 7 is now **427 files larger than the plan states**, and 315 of those are
the ruling. The other 112 are work that landed and is invisible in the index
frame.

---

## 7. The two cautions from batch 0, carried and re-taken

**R8's "15 named launchers" — still `L-94`, and the reconstruction is
reproducible but is not the author's list.** No committed artefact enumerates
them. Reconstructed at `4d7c195a` as **all 12 shell scripts at `scripts/` root**
(`audit_camera_discretion`, `audit_transcripts`, `auto-stop`, `case_preflight`,
`demo_servers`, `filming_keepalive`, `filming_mode`, `kill_worker`,
`launch_solve`, `package_caches`, `session_keepalive`, `verify_warm_replay`)
**plus `installed_registry.py`, `memwatch.py`, `ledger_backup.py`** = 15, and
with `installed/` (7) + `laptop_bundle/` (4) that is **R8 = 26, R9 = 57,
R8 + R9 = 83 = `scripts/**`**. It reproduces both published totals. **A set
that fits is not the author's list**, and only the sum is fixed by the
reconciliation, so an independent reconstruction that put the boundary
elsewhere would close identically. It is recorded as a reconstruction, again.

**Batch 6's ownership precondition is re-measured, not read.** §9's *"786 files
under `dafoam/**/work_sail/` are root-owned"*: at `4d7c195a`,
`find . -path ./.git -prune -o ! -user ubuntu -print` returns **0 files
repo-wide, stderr empty** — the same answer as at `7554e5d3`. `work_sail` is at
`demo-output/website/dafoam/work_sail` — **one level below `dafoam/`, not two**
— and holds no non-`ubuntu` file. The line is stale in the safe direction and
**batch 6 re-runs the `find` rather than trusting either the plan's line or
this one**; ownership is a filesystem property and it can change back between
now and the batch.

---

## 8. The other half of batch 0 — the supersession marks were ALREADY IN PLACE

The reconciliation recorded *"marking `docs/PHASE2_MOVE_MAP.tsv` and
`docs/PHASE2_STRUCTURE_PROPOSAL.md` superseded … was not performed here and
remains outstanding."* **Checked before doing it: both were already marked, at
`dce05a01` on 2026-08-16**, and the marks are in HEAD, not merely in the
worktree —

```
git show HEAD:docs/PHASE2_MOVE_MAP.tsv | head -2
  # ===== SUPERSEDED IN KIND -- DO NOT EXECUTE ANY ROW BELOW =====
  # Marked 2026-08-16 at b0ab070d. Kept, not deleted; history is not rewritten.
```

— and the worktree copies of both files were byte-identical to HEAD's blobs
before this pass touched them. **The item was recorded as outstanding without
being checked, and re-marking would have been a second mark presented as a
first.**

What was genuinely missing is that both marks name only
`campaign/MOVE_MAP_2026-08-16.md` as the successor, and the successor is now a
chain of four documents. **A dated append-only note was added to the end of
each**, naming the whole chain and the date, and touching not one existing
line. Neither file's existing content was rewritten, both keep their
`b0ab070d` mark verbatim, and neither is executable at either end.

---

## 9. Method

- **Every rule count is over one fixed commit**, `git ls-tree -r -z` at
  `4d7c195a`, and the snapshot was checked for duplicates (14,298 lines,
  14,298 unique). Where a figure moved since `7554e5d3`, both anchors are
  named and the difference is a **set difference between two commits**.
- **No count is ordered or selected by a commit date**, which is what `D357`'s
  re-dating defect would otherwise reach: amending a record re-dates it, and a
  date-ordered reading of "newest" then reports records nobody touched.
  Commit-membership questions are immune to that, and every figure here is one.
- **Never `git ls-files`.** The index is 479 paths behind HEAD and the missing
  paths are, by construction, the newest — which is exactly the class most
  likely to need a rule that does not exist yet (`L-95`).
- **`stderr` was captured on every walk and every `git` invocation** and was
  empty on all of them except where an error was deliberately planted, in
  which case the error is quoted.
- **No count was piped into `head`.** Every total is a `wc -l`, a `grep -c` or
  a classifier total over a complete stream. The two listings shown in full
  are shown in full.
- **The pathspec hazard was avoided.** `git ls-files -- 'demo-output/*.png'`
  returns 874, not R12's 10, because git pathspec globs match across `/`;
  every rule count here is an anchored regex over the path snapshot.
- **What is over a moving target and what is not.** §1, §2, §6 and §7's counts
  are over a fixed commit and are not. §4's control and §5's four-bucket table
  are **filesystem walks of live trees** and are; §5's two columns come from a
  single invocation so they are comparable with each other, and §3.4's two
  derivations reproduced byte-identically across two anchors an hour apart.
- **This pass does not appear in its own results.** The classifier, the path
  snapshots, the mutants and the control trees were written outside the
  repository.

## 10. What this pass did not do

No file was moved, renamed, copied, deleted or untracked. No directory was
created or removed inside the repository. `.gitignore` was not edited and
`git mv` was not invoked. The shared index was not touched. `lab_paths.py` was
not edited — R25 is ruled and recorded and **not yet bound**, and §5 states
what binding it costs. `scripts/hand_carry.py` was run in `derive` mode only,
which never writes inside the repository; `carry` was never invoked against
this tree. No batch ran. No `.gitignore` rule was written, so `MESH_AUDIT_runs`
is exactly as tracked today as it was yesterday — option A is a decision
recorded and encoded, not an untracking performed.
