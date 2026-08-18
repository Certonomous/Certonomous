# MOVE_MAP batch 6 — the ride-along invariant is finally worth what it claims (7.22 GB), the `.gitignore` half the batch-2 comment routed to the wrong batch, and a waiver register that would have reported 137 files twice and cancelled

**2,118 tracked files moved by 11 `git mv` invocations, every one naming a
DIRECTORY, one source per invocation, stderr captured and empty on all 11, exit
0 and empty stdout on all 11.** Nothing was deleted. Nothing was untracked. The
**shared index was neither read nor written**: all 11 renames ran under a
private `GIT_INDEX_FILE` seeded by `git read-tree HEAD`, and the commit's index
was rebuilt from the observed HEAD's `(mode, blob)` entries rather than reused
from the one `git mv` wrote.

**`.gitignore` WAS edited, and this is the first move batch that had to edit
it.** Twenty rules named a batch-6 source. Left alone, `git mv` would have
vacated the paths they name and the rules would have stopped ignoring anything —
§4.1.

**The invariant that batches 4 and 5 could only assert is the one this batch
actually spends.** Batch 5 measured **zero** dark trees under its own sources
and said so rather than claiming a protection it did not need. Re-measured here,
at `0869284e`, over the same instrument: **252 dark trees, 23,605 files and
7,223,663,928 bytes ride along on the eleven batch-6 renames**, and **zero**
rows of the hand-carry, stays-put and discard buckets sit under any batch-6
source. A per-file `git mv` loop would have left 7.22 GB behind. §3.2.

Measured over `git ls-tree -r -z --name-only`, at a named commit, **never
`git ls-files`**. stderr was captured on every walk, every `git` invocation and
every subprocess and was empty on all of them. No count was piped into `head`.

**Anchors, and HEAD moved six times under this pass.** It opened at
**`0869284e`**, 7,080 tracked paths over `git ls-tree -r -z --name-only HEAD`,
never `git ls-files`. Six peer commits landed while it ran, all of them the F14
cooling-ladder lane's:

| | | touches a batch-6 source? | touches a file this batch edits? |
|---|---|---|---|
| `b845b603` | the Boussinesq limit is not one number | **no** | no |
| `e4a977ef` | the heat-balance audit deleted its own history (D375) | **no** | `docs/DOCKET.md`, `docs/LESSONS.md` |
| `fa2c8bb0` | K2b pilot | **no** | `.gitignore` |
| `495a94ea` | the VALIDATED chip | **no** | no |
| `bffa7ca0` | K0c turbulent rung | **no** | `.gitignore` |
| `cccf7a9f` | K0c-T cross-references | **no** | no |

**All 2,118 batch-6 source paths are present in HEAD at `cccf7a9f`**, checked by
set membership against `git ls-tree -r HEAD` rather than by reading a diff, and
**none of the six commits names one**. The moves were made at `0869284e`; the
commit is built against whatever HEAD is observed at the moment it is built,
with the index reconstructed from THAT commit's `(mode, blob)` entries rather
than reused from the one `git mv` wrote, so a peer commit landing between the
move and the commit cannot be reverted by this one. **One of the six overwrote
this pass's uncommitted `.gitignore` edit and §9.1 is what happened.**

---

## 1. THE MERGE-FAMILY ASSERTIONS — ratified by batch 5, re-derived here, and one of the two families is not a merge at all

`MOVE_MAP_BATCH5_EXECUTION_2026-08-18.md` §1 ratified that a many-to-one merge
**preserves the child segment**, having measured that flattening R23's four
`closure_*` sources would silently overwrite **18 files on 9 names**, and that
two of those sources **share a sorted path-set sha256 and differ in bytes**, so
a digest check alone would have called the flat merge clean. Batch 6 inherits
that ruling and does not re-open it. What it does is what the brief requires:
**confirm it holds for every batch-6 merge family before anything moved**, and
assert **set equality plus byte totals**, never a digest alone.

### 1.1 Which families exist, derived rather than assumed

Eleven `_MOVES` rows land under `cases/`. Grouping them by *destination
directories fed by more than one source* gives exactly **one** merge family:

| destination | sources | |
|---|---:|---|
| `cases/tmr` | **4** | `TMR`, `TMR_TRANSIENT_300CU`, `TMR_TRANSIENT_A10`, `TMR_FLATPLATE_FINEST` |

`cases/` itself is **not** a merge family and saying so matters: eleven sources
land in it, but each lands on its **own distinct child**, so nothing merges.
**11 of 11 destinations are distinct**, and `redirect()` run over the whole
tracked corpus at `0869284e` reports **0 successor collisions repo-wide** and
**0 destinations landing on a tracked path that does not move**.

### 1.2 THE COUNTER-FACTUAL, MEASURED — flattening `cases/tmr` destroys 12 files, and half of them differ in bytes while the other half do not

The four sources hold **108 + 13 + 12 + 5 = 138 tracked files**. Flattened into
one `cases/tmr/` namespace, as `MOVE_MAP_EXECUTION_2026-08-17.md` §4.3's worked
example reads, they land on **126 distinct relative paths**: **12 files are
silently overwritten, on 12 names**, every one of them contributed by the two
transient NACA 0012 cases:

```
2x 0/U    2x 0/k     2x 0/nut    2x 0/omega   2x 0/p    2x controlDict.solve
2x driver_status.json   2x fvSolution.init   2x fvSolution.march
2x mesh.boundary        2x mesh.faces        2x mesh.points
```

**Six of the twelve differ in bytes and six are byte-identical, and the split is
the finding.** `mesh.faces` is 325,111 bytes in one case and 1,468,631 in the
other; `mesh.points` 230,354 against 903,913; `driver_status.json` 988 against
213; `0/U`, `controlDict.solve` and `mesh.boundary` differ at equal length. The
other six — `0/k`, `0/nut`, `0/omega`, `0/p`, `fvSolution.init`,
`fvSolution.march` — are byte-identical, which is exactly what makes the
overwrite quiet: **a flat merge of these two cases loses the entire 225x65 mesh
and the driver status that says which case it is, while every field file it
lands on top of agrees.**

**Batch 5's digest hazard does NOT recur here, and that is reported as the
negative result it is.** The four sources have four **distinct** sorted
path-set digests — `1293330da80050d2`, `9d715247d2eee1b3`, `5f24ab261706df1f`,
`e676949245bbfd7f` — so unlike R23's `closure_challenge_submission` /
`_round4` pair, a digest comparison *would* have caught this one. That is luck,
not method, and it is why every assertion in §3 is a **Python set comparison
plus a byte total**, with the digest carried alongside as a third witness
rather than as the check.

**Under the child-preserving rule the four sources land on 138 distinct
destination paths with 0 collisions**, asserted before the move.

---

## 2. What moved, re-derived rather than carried — and the plan's figure is stale HIGH by 1,436, all of it in one rule

`MOVE_MAP_EXECUTION_2026-08-17.md` §4 prices batch 6 at **3,553 files**, amended
in the same table to **3,554 at `4d7c195a`**. Re-derived at `0869284e` by running
`lab_paths.redirect()` over every tracked path and keeping those whose successor
is under `cases/`: **2,118**.

**Every file of the 1,436-file difference is dafoam, and it is batch 2's, not
drift.** Commit membership between the two named commits, over
`git ls-tree -r --name-only`, per source:

| Rule | Source → destination | at `4d7c195a` | at `0869284e` |
|---|---|---:|---:|
| R22 | `website/dafoam` → `cases/dafoam` | 3,269 | **1,833** |
| R22 | `website/committee-grids` → `cases/committee-grids` | 105 | 105 |
| R22 | `website/tmr` → `cases/tmr` | 108 | 108 |
| R22 | `website/tmr-naca0012-transient-300cu` → `cases/tmr/…` | 13 | 13 |
| R22 | `website/tmr-naca0012-transient-a10-225x65` → `cases/tmr/…` | 12 | 12 |
| R22 | `website/tmr-flatplate-finest-grids` → `cases/tmr/…` | 5 | 5 |
| R22 | `website/hlpw6` → `cases/hlpw6` | 12 | 12 |
| R22 | `website/mega-batch` → `cases/mega-batch` | 9 | 9 |
| R22 | `website/unsteady-cylinder` → `cases/unsteady-cylinder` | 8 | 8 |
| R22 | `website/valve` → `cases/valve` | 7 | 7 |
| R5 | `demo-surfaces` → `cases/demo-surfaces` | 6 | 6 |
| | | **3,554** | **2,118** |

**Ten of the eleven rows are unchanged to the file.** The eleventh fell by
exactly 1,436, which is batch 2 untracking dafoam's solver logs and solver time
directories under the `.gitignore` rules §4.1 re-points. This is the same shape
batch 5 recorded for batch 7 — *"2,854, not 8,643"* — and the same sign: the
plan's move subtotals are stale **HIGH**, and they are stale because the
untracking batches ran, not because anything was lost. **Nothing else moved**:
`git ls-tree -r HEAD` classifies all 2,118 into exactly one of the eleven rows
with **zero unattributed**.

---

## 3. Granularity, and the proof on both sides

**All eleven sources are directories and each went by exactly one `git mv`
naming the DIRECTORY.** There is no loose-file half to this batch: unlike batch
5's 43 stray webroot files, every batch-6 source has a directory to name, which
is the whole reason the ride-along invariant is worth 7.22 GB here and was worth
nothing in batch 5.

`scripts/hand_carry.py`'s `measure()` was run against each source immediately
before its move and against its destination immediately after — file count on
disk, byte total, and the sha256 of the **sorted relative-path set**. `measure()`
raises rather than returning a short number when a walk or a stat fails; **all
22 measurements reported `walk_errors = 0`**.

| Source → destination | tracked | on disk | bytes | sorted path-set sha256(16) | source gone | destination set |
|---|---:|---:|---:|---|---|---|
| `website/tmr` → `cases/tmr` | 108 | 154 | 87,804,913 | `62475db012491d52` | yes | **identical ∪ children, §3.1** |
| `website/tmr-naca0012-transient-300cu` → `cases/tmr/…` | 13 | 15 | 29,744,300 | `acef817219456801` | yes | **identical** |
| `website/tmr-naca0012-transient-a10-225x65` → `cases/tmr/…` | 12 | 12 | 2,381,350 | `5f24ab261706df1f` | yes | **identical** |
| `website/tmr-flatplate-finest-grids` → `cases/tmr/…` | 5 | 9 | 5,003,395 | `28de64fdb36a4c44` | yes | **identical** |
| `website/dafoam` → `cases/dafoam` | 1,833 | **24,466** | **7,077,477,743** | `cd699ea970faed61` | yes | **identical** |
| `website/committee-grids` → `cases/committee-grids` | 105 | 105 | 2,144,138 | `99d9ef0614b90dfc` | yes | **identical** |
| `website/hlpw6` → `cases/hlpw6` | 12 | 12 | 124,623 | `8880abdc99975902` | yes | **identical** |
| `website/mega-batch` → `cases/mega-batch` | 9 | **1,244** | **502,355,915** | `04a3e8785df7cf19` | yes | **identical** |
| `website/unsteady-cylinder` → `cases/unsteady-cylinder` | 8 | 8 | 6,913 | `aecfec661eebe8db` | yes | **identical** |
| `website/valve` → `cases/valve` | 7 | 7 | 807,410 | `fb6da6f34f4ac31c` | yes | **identical** |
| `demo-surfaces` → `cases/demo-surfaces` | 6 | 6 | 12,492,467 | `5661594b53ce1289` | yes | **identical** |
| **BATCH 6** | **2,118** | **26,038** | **7,720,343,167** | | | |

Every source is **gone**, and every destination holds **exactly the source's
sorted relative-path set**, asserted as a Python **set equality** and a **byte
total**, with the digest carried as a third witness — not as the check.
`cases/` measured as a whole afterwards holds **26,038 files and 7,720,343,167
bytes**, equal to the sum of the eleven sources to the byte.

**The tracked column and the on-disk column are the point.** 2,118 tracked
files travelled and **23,920 untracked ones travelled with them**, because every
`git mv` named a directory. `dafoam` alone is 1,833 tracked inside 24,466 on
disk.

### 3.1 `cases/tmr` is the one destination that is not a copy of one source, and the assertion says so

Four sources, one destination tree: R22 flattens the parent (`tmr/`) and
preserves the three children's segments, so `cases/tmr/` ends up holding all
four. A naive "destination == source" check is the wrong assertion here — batch
5 recorded a false red from exactly that shape on `research/race` — so the
honest one is against the **union**, and it was made in three parts:

```
cases/tmr own subtree (excluding the three child segments)
                        154 paths, expected 154, path-set sha256 62475db012491d52
                        == the source's own digest                        : True
cases/tmr expected 190 paths, got 190, SET-IDENTICAL                      : True
  bytes 124,933,958 == 87,804,913 + 29,744,300 + 2,381,350 + 5,003,395    : True
  sorted path-set sha256                                                  : b1bcc6010fc2a859
```

### 3.2 THE RIDE-ALONG INVARIANT IS EXERCISED BY THIS BATCH, AND THIS IS THE MEASUREMENT

Batch 5 reported *"a per-file `git mv` loop would have lost nothing here"* and
said so rather than claiming a protection it did not need. **Batch 6 is the
batch that needed it.** `hand_carry.derive()` at `0869284e`, before anything
moved:

| bucket | whole repository | **under a batch-6 source** |
|---|---|---|
| HAND-CARRY | 2 trees / 307 files / 1,510,309,145 B | **0 / 0 / 0** |
| RIDES ALONG | 2,334 / 45,770 / 14,269,950,892 | **252 / 23,605 / 7,223,663,928** |
| STAYS PUT | 5 / 10,287 / 620,130,400 | **0 / 0 / 0** |
| DISCARD | 6 / 39 / 1,554,115 | **0 / 0 / 0** |

Five of the eleven sources carry dark trees:

| carrier | dark trees | files | bytes |
|---|---:|---:|---:|
| `demo-output/website/dafoam` | 238 | 22,324 | 6,807,297,223 |
| `demo-output/website/mega-batch` | 1 | 1,229 | 395,586,636 |
| `demo-output/website/tmr` | 11 | 46 | 18,111,522 |
| `demo-output/website/tmr-naca0012-transient-300cu` | 1 | 2 | 2,008,950 |
| `demo-output/website/tmr-flatplate-finest-grids` | 1 | 4 | 659,597 |
| | **252** | **23,605** | **7,223,663,928** |

**A per-file `git mv` loop would have left 7,223,663,928 bytes behind**, and
`git status` would have said nothing, because every one of those files is
gitignored. **Zero hand-carry rows sit under any batch-6 source**, so nothing in
this batch needed the hand-carry mechanism — the directory rename reaches all of
it.

**The arithmetic closes on the other side, and that is the confirmation.** After
the move, `RIDES ALONG` reads 2,082 trees / 22,165 files / 7,046,286,964 bytes:

```
2,334 − 252 = 2,082          45,770 − 23,605 = 22,165
14,269,950,892 − 7,223,663,928 = 7,046,286,964
```

exact in all three columns. The 252 rows did not vanish; they are now under
`cases/`, which is itself dark at a HEAD that predates the commit tracking it,
so `STAYS PUT` absorbs them — 5 trees / 10,287 files / 620,130,400 B becomes
6 / 36,325 / 8,340,473,681, the new row being `cases/` at exactly the 26,038
files and 7,720,343,167 bytes of §3's table. **That is the ride-along set
arriving, counted by a second instrument.**

---

## 4. THE FINDINGS — three lists that did not know about `cases/`, and one of them was routed to the wrong batch in writing

All four below are the defect class batch 3 found on R16/R17, batch 4 on R1's
missing `AWS_TREE_PLAN` row and batch 5 on `RECORD_ROOT_NAMES`: **a rule that is
written down and not bound is a rule the mover does not have.** Two of the four
would have failed silently; one would have failed loudly and cancelled itself in
the totals; one would have re-created the directory it was moved out of.

### 4.1 `.gitignore` — twenty rules named a batch-6 source, and the batch-2 comment routes the fix to the wrong batch IN WRITING

`.gitignore:140-158` is batch 2's own header, and it ends:

> *"Those trees are excluded exactly as `MESH_AUDIT_runs` is, and batch 7
> untracks them at their new path. **Batch 7 must re-point these two roots when
> it moves them**, which is the obligation `MOVE_MAP_EXECUTION_2026-08-17.md`
> section 3.2 already records for lines 122-123 above."*

**"These two roots" are `demo-output/website/campaign/` and
`demo-output/website/dafoam/`, and they do not move in the same batch.**
`campaign/` is R20/R21, batch 7. `dafoam/` is **R22, batch 6** — this one. The
sentence is half right and the wrong half is the dangerous half, because a
`.gitignore` obligation deferred to a batch that runs *after* the move leaves a
window in which the rules name a path `git mv` has just vacated.

Twenty rules across five blocks named a batch-6 source. All twenty were
re-pointed in this commit, and nothing else in `.gitignore` was touched:

| Block | Rules | Re-pointed to |
|---|---:|---|
| mega-batch live/transient (`work/`, `ledger.jsonl`, `run.log`, `STOP`) | 4 | `cases/mega-batch/…` |
| mega-batch runner state (`runner.log`, `.err.log`, `.pid`, `keeper.log`, `learned_study.json`, `work/`) | 6 | `cases/mega-batch/…` |
| F6d random-matrix ensembles (`ens/`, `signdemo/`, `signcheck/`, `f6a_recheck/`, `f6d_option_a/`) | 5 | `cases/dafoam/f6d_random_matrix_uq/…` |
| batch-2 solver time directories under dafoam | 2 | `cases/dafoam/**/…` |
| batch-2 solver logs under dafoam | 3 | `cases/dafoam/**/…` |
| | **20** | |

`demo-output/website/solve_registry/` on the same line as the runner block was
**left alone**: it is 7H's hand-carry, it has not moved, and re-pointing an
ignore rule ahead of its tree is the mirror image of this defect.

**The re-point untracks nothing, and that was measured before it was made.**
Over `git ls-tree -r HEAD`, **1,833 tracked dafoam files, 0 of which match
`log.*`, `*.log`, `*.log.*`, a `[1-9]*/` segment or a `0.[0-9]*/` segment** at
either spelling. What the rules hold is the untracked side: the five F6d trees
alone are **16,146 files and 4,924,886,566 bytes**, and the whole dafoam rename
carries **238 dark trees / 22,324 files / 6,807,297,223 bytes**.

### 4.2 `exec_bits.WAIVED_NO_EXEC_BIT` — 137 waived paths, and the two findings it would have raised CANCEL in the count

`sdk/chief_engineer/exec_bits.py` carries the dated waiver register of tracked
shebang-bearing files with no exec bit. It is a list of **paths**, matched by
string equality against `git ls-tree -r HEAD`. **137 of its 255 entries are
under a batch-6 source** — dafoam 111, committee-grids 20, hlpw6 6.

Left alone, `audit()` after this batch reports each of those 137 **twice**:

* `stale_waivers` — the waived path is no longer in HEAD → *"a waived file …
  that no longer exists, so the register is out of date"*, 137 of them, turning
  `test_the_waiver_register_still_describes_the_tree` from PASS to FAIL;
* `unregistered` — the same file at `cases/…` is a shebang script with no bit
  and no waiver → 137 of them, on top of the standing 16, turning
  `test_no_shebang_script_is_both_unexecutable_and_unregistered` redder.

**And the two cancel.** 137 leave one list and 137 enter the other; the register
length does not move, the total shebang count does not move, and a reader
comparing sizes sees nothing. That is batch 5's *"46 tests behind one skipped
line"* in a different instrument: the finding is real, loud in the right list,
and invisible to every aggregate.

`OWNERS` is the same defect one function over. `owner_of` maps a path to the
family that answers for it by longest prefix, and there was no `cases/` row —
so after the move every one of the 137 routes to **UNASSIGNED**, and
`test_the_register_is_split_across_families_and_says_so` asserts in as many
words that *"a waived path with no owning family cannot be routed"*. This is
literally the row batch 4 had to add for `ops/`, and the comment it left beside
it is what made this one findable.

**Repaired by teaching the MATCH the map, not by re-writing the register.**
`exec_bits._spellings()` returns every name the repository has had or will have
for a path — the literal, `lab_paths.redirect()` of it and
`lab_paths.unredirect()` of it — and `audit()` matches each waived entry against
HEAD under all of them. The register keeps the spelling it was written with,
because `WAIVER_REGISTER_DATED` makes it a dated enumeration and re-writing
history's spellings is not what makes it true. `tracked_shebang_scripts` probes
the shebang under the same spellings, so the window between the `git mv` and the
commit that records it does not blank the register either. Two `OWNERS` rows
were added — `cases/dafoam/` → DAFoam, `cases/` → Demo and website — and the
family assignment of every file is **preserved, not re-decided**: each of the
137 keeps the family it had before the move.

Pinned by three tests, and the two controls are the load-bearing half:
`test_a_waived_path_is_still_matched_after_its_tree_moves`;
`test_a_waived_path_that_is_nowhere_under_either_spelling_is_still_stale`,
without which a matcher that answered *covered* to everything would pass the
first; and `test_a_moved_waiver_that_gained_its_bit_is_still_stale`, without
which following the map could swallow the finding the register exists to make.

### 4.3 `check_convergence_validate.py` — a known-answer suite pinned to four paths batch 6 moves, and one class of its answers fails SILENTLY

`scripts/check_convergence_validate.py` is admitted by `lab_check` and reads
**PASS, 13 of 13 known-answer cases** in the before frame. Four of its thirteen
name a log under `demo-output/website/dafoam/` and two more name one under
`demo-output/website/solve_registry/`, which batch 7H hand-carries.

`check_convergence.classify()` returns **`CANNOT_TELL`** for a log it cannot
open — *"log file not found"* — which is the right verdict and the wrong
outcome here, in two different ways depending on the row.

**Measured, by running the unrepaired literal form against the moved tree:**

```
hump_baseline_f6a              expect=CONVERGED      literal form -> CANNOT_TELL   FAIL (loud)
A4_ahmed_adjoint_check_totals  expect=CONVERGED      literal form -> CANNOT_TELL   FAIL (loud)
A4_ahmed_fine_primal           expect=NOT_CONVERGED  literal form -> CANNOT_TELL   FAIL (loud)
```

**Three of thirteen, and this check's verdict moves PASS → FAIL as a pure side
effect of the move.** Batch 6's own exposure is therefore the loud kind, and
that is stated rather than dramatised.

**The silent kind is 7H's and the same three lines close it.** Two rows name a
log under `solve_registry/` — `threeC_isotropic_corner` (CONVERGED) and
`f5a_re2000_transient`, whose known answer **is `CANNOT_TELL`**. When 7H carries
that tree, the second row starts reporting `OK` **because the file is missing**,
on a row whose whole point is that a steady convergence gate does not apply to
an unsteady run: a pass produced by absence, on a suite whose docstring says *"a
checker that cannot reproduce the known answers is not a checker."*

Repaired by `_located()`, which routes each relative path through
`lab_paths.resolve()` — literal, successor or predecessor — and falls back to
the literal spelling under `REPO` when it resolves nowhere, so `classify` still
prints `log file not found: <the path we looked for>` and **absence still
fails**. After the move the check reads **PASS, 13 of 13** again, both standalone
and inside `lab_check`.

### 4.4 The generators, enumerated by where they actually write

The brief's second standing lesson is that **generators write to their `_OUT`
constants**, and batch 5 caught `build_wall.py` about to write the live served
page into a data directory. Every generator whose output lands in a batch-6
destination was enumerated and **executed or read at the constant**, not at the
comment:

| Generator | Output lands in | Where it actually writes | Verdict |
|---|---|---|---|
| `sdk/workflows/mega_batch.py:1123-1124` | `cases/mega-batch/` | `lab_paths.MEGA_BATCH / …` | **follows** |
| `sdk/chief_engineer/ledger_learning.py:69`, `lab_stats.py:183`, `sdk/scripts/build_benchmarks.py:78`, `fit_cost_scaling.py:74,290`, `assess_ledger_wall_times.py:58`, `scripts/ledger_backup.py:37`, `morning_report.py:284`, `self_audit.py:130` | `cases/mega-batch/` | same | **follows** |
| `sdk/workflows/tmr_verification.py:1752,3719` | `cases/tmr/` | `lab_paths.TMR` | **follows** |
| `sdk/workflows/_a2_shape.py:39`, `adjoint_optimization.py:130`, `onera_m6.py:63` | `cases/dafoam/ladder-a/` | `lab_paths.DAFOAM / …` | **follows** |
| `sdk/scripts/mega_batch_keeper.sh:22-24` | `cases/mega-batch/` | **three literal `$REPO/demo-output/website/mega-batch/…`** | **repaired** |
| `sdk/scripts/run_mega_batch.ps1:20-21` | `cases/mega-batch/` | **two literals** | **repaired** |
| `sdk/scripts/make_naca0015.py:32` | `cases/demo-surfaces/` | **literal `REPO / "demo-surfaces"`** | **repaired** |
| `sdk/scripts/build_a2_shape_frames.py:34` | `cases/dafoam/ladder-a/` | `OUT="/out/…"` inside the container; the **host mount in the docstring** was a literal | **repaired** |
| `sdk/chief_engineer/server.py:55` | reads `cases/demo-surfaces/` | **literal**, and it is the served copy set | **repaired** |
| `sdk/scripts/regenerate_pressure_slices.py:83,92`, `render_sail_streamlines.py:55` | read `cases/demo-surfaces/` | **literals** | **repaired** |

**`mega_batch_keeper.sh` is the one the module header predicted.**
`scripts/lab_paths.py`'s own opening census names it — *"3 verbatim in
`mega_batch_keeper.sh`"* — as the reason the shim exists at all, and it was
still spelling the prefix three times. Shell cannot import the shim, so it asks
it once and binds `$MB`; the PowerShell launcher does the same. That is the form
`scripts/launch_solve.sh` already uses and batch 5 extended.

**`make_naca0015.py` is the batch-6 analogue of batch 5's `build_wall.py`.** It
is a generator whose `DEFAULT_OUTPUTS` **write** the sail geometry into the copy
set. A literal there re-creates `demo-surfaces/` on the next run and leaves
`cases/demo-surfaces/naca0015_sail.stl` — the one `server.py` serves — frozen at
its last build, with nothing failing.

**`server.py` is the only live surface batch 6 touches**, and it touches it by
default value only: `CERTONOMOUS_SURFACES` still overrides.

---

## 5. The equality pin that reddened, and it reddened on the plan working

Batch 5 closed with a prediction: *"Every accessor written to replace a
whole-tree glob acquires a test that pins it to that glob, and every one of them
reddens at the batch the accessor was written for. Whoever runs batch 6 should
expect the same and should look for it rather than be surprised by it."*

**It happened, one module over from where it was predicted, and it was found by
running the tests rather than by reading them.** Three tests in
`sdk/tests/test_log_signatures.py` fail after the move and passed before it:

```
ArchiveSweepTests::test_the_sweep_names_only_the_withdrawn_run_and_the_audited_probe_points
ArchiveSweepTests::test_only_the_withdrawn_run_trips_more_than_the_clip_branch
MagnitudeExplosionTests::test_archive_sweep_names_the_known_fires_and_no_others
```

All three sweep **one root**: `ROOT = lab_paths.DEMO_OUTPUT` and
`sweep(lab_paths.DEMO_OUTPUT)`. `DEMO_OUTPUT` is a **non-moving** name — it is
bound to `demo-output` on both sides of every batch — and that is exactly why it
failed to follow: **R22 took the DAFoam log archive out from under it.** The
third test's own floor is what named the size of the loss: `graded` fell from
above 150 to **128**, and the first test lost the withdrawn run
`A4_fine_primal_par4.log` and all four audited probe points from its named
expectation.

**This is the good failure mode and it is worth saying why.** The first test
names its five logs **individually** — its own comment says *"named individually,
not counted. A sixth log appearing here is a new finding"* — so a corpus that
shrank removed named expectations and the assertion could not be satisfied by a
smaller number. Had it asserted a count, batch 6 would have shrunk the archive
sweep silently, which is the failure this whole plan exists to prevent.

**Repaired by making the root list follow the map, not by relaxing the
assertion.** `ArchiveSweepTests._roots()` returns the existing directories among
`DEMO_OUTPUT`, `cases/`, `verification/` and `evidence/`, skipping absent ones,
and `_archived_logs()` sweeps all of them; the magnitude replay sweeps the same
list. `verification/` and `evidence/` do not exist yet, so **the list needs no
edit at batch 7 or 7H** — which is the property `lab_paths` was built for.
After the repair: **72 passed, 10 subtests passed**, the five named logs are
back, and `graded` is above its floor again.

**Falsified rather than assumed.** The three tests were observed FAILING against
the moved tree with the single-root form and PASSING with the repaired one, in
that order, so the repair is pinned by having been seen to matter. The floor
`self.assertGreater(len(logs), 300, "the log archive did not resolve")` is
untouched and is what reddens if a future batch moves a region out without
naming it here.

**`SWEEP_ROOTS()` was deliberately NOT used for this.** It returns eleven
prefixes including `sdk/`, `scripts/`, `models/`, `docs/` and
`mission-output/`, and `mission-output/` holds solver logs — including
`nasa-hump/act6-nasa_hump/log.simpleFoam`, which
`check_convergence_validate.py` names as an independent known answer. Sweeping
it would have **grown** the corpus, and a corpus that grows under a repair is
the other half of §"a count that FELL is a blinded instrument; a count that
ROSE is a corpus that absorbed something it should not have."

### 5.1 D368 did NOT recur, and that is a measurement rather than an absence of news

Batch 5 closed on the question to carry forward: *"for every blinding test,
which handle covers the region after the move?"* `test_empty_set_is_not_agreement`
and `test_form_or_value_and_empty_selection` blind a check by rebinding
`self_audit`'s handles and assert UNKNOWN rather than a clean sweep of nothing;
batch 5 had to move them from `WEB` to `REPO` when the record corpus split into
seven roots.

**Batch 6 splits it again — seven roots to fourteen — and both modules pass
untouched.** `REPO` is the handle `_at()` re-roots on unconditionally, so it
covers `cases/` exactly as it covers `research/`, and the repair batch 5 made
generalises to every remaining batch. Executed, not reasoned: both modules are
green in the post-move run and neither was edited.

---

## 6. What was NOT done, and each is a decision rather than an omission

### 6.1 `_SHIPPING_RE` is not re-pointed, and it is byte-identical to HEAD

`MOVE_MAP_EXECUTION_2026-08-17.md` §5 Class 2 requires
`scripts/check_absolutes.py`'s `_SHIPPING_RE` to gain its `web/` alternative
**in the commit that creates `web/` and not before**. **Batch 6 does not create
`web/`** — R13, the served set, is batch 8 — and `ls web` returns *no such file
or directory* after this batch as before it. The pattern still reads
`^(?:demo-output/website/|.*/latex/|.*\.tex$)` at `check_absolutes.py:743`, and
**the whole file is byte-identical to HEAD's blob**, confirmed by `cmp` against
`git show HEAD:scripts/check_absolutes.py` rather than assumed. It stays queued
for batch 8.

### 6.2 The guard resolver is batch 9's, and batch 6 does not move its number

`check_evidence_paths_exist` tests `(REPO / cited).exists()` — the **literal**
path only. Measured with the guard's own regexes and roots, before and after:

| | before (373 records) | after |
|---|---:|---:|
| repo-rooted citations | 1,828 | **1,830** |
| not resolving at the LITERAL path | **197** | **333** |
| …of those, resolving at the SUCCESSOR via `lab_paths.resolve()` | 193 | **328** |
| …**genuinely nowhere** | **4** | **5**, §6.2a |

Batch 5 handed this over at **197 of 1,820**, of which 193 resolve at their
successor and 4 are genuinely nowhere; re-measured here at `0869284e` it is
**197 of 1,828** — the population grew by 8 under other lanes and the finding
did not move at all, which is the check that the inherited number is a fact
about the corpus rather than a fact about batch 5's frame.

`MOVE_MAP_EXECUTION_2026-08-17.md` §4 says the guard goes blind at **batch 8**.
Batch 5 corrected that to **batch 5**, and batch 6 is the second batch to
confirm the correction from the other side: the number was already 197 before
this batch ran. **The resolver is batch 9 and was NOT built here**, because
batch 9 is specified with a **two-way planted control** — *"a citation that must
resolve and one that must not"* — and a resolver landed without that control is
the shape of a guard that stops discriminating. What batch 6 adds to the case
for batch 9 is stated in §6.2a.

### 6.2a The citation guard went 197 → 333, and one of the five is an example filename that only became countable because `cases/` exists

Measured with the guard's own regexes, roots and retraction pattern, over the
same 373 records, before and after:

| | before | after |
|---|---:|---:|
| repo-rooted citations | 1,828 | **1,830** |
| not resolving at the LITERAL path | **197** | **333** |
| …of those, resolving at the SUCCESSOR via `lab_paths.resolve()` | 193 | **328** |
| …**genuinely nowhere** | **4** | **5** |

**The 136 new rows are citations the guard cannot FOLLOW, not citations that
point at nothing** — `lab_paths.resolve()` finds every one of them at its
successor, which is precisely the resolver batch 9 specifies.

**The last row is the one that measures the corpus, and it moved 4 → 5. The
increment is an instrument artefact and it is named rather than absorbed.** The
new row is

```
demo-output/website/campaign/MOVE_MAP_BATCH5_EXECUTION_2026-08-18.md:101
    cites  cases/tmr/a.json
```

which is batch 5's own record quoting `tmr/a.json` → `cases/tmr/a.json` as the
**illustrative example** in its sentence about the parent of a merge family
still flattening. Before batch 6, `cases/` was not a root of
`lab_paths.SWEEP_ROOTS()`, so that string did not start with a known root and
the guard never counted it. **Creating `cases/` made a previously-invisible
example filename countable.** It is not a broken citation and it is not edited:
the record is append-only, and the honest reading is that the guard's
root-anchoring is what changed, not the corpus.

The other four are unchanged from batch 5's four, one of them now read at its
new path (`cases/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md` citing
`scripts/analyze_fd.py`, which is the same finding at a different spelling).

**What this number says about batch 9's urgency.** It has now gone 12 → 197 →
333 over three batches, and batch 7 moves 2,854 more files. The count is
dominated by the instrument rather than by the corpus and the ratio is getting
worse: **328 of 333 are the guard failing to follow a rename**. Every one of
them becomes a resolving citation the moment batch 9's resolver lands, and
until it does, `check_evidence_paths_exist` is answering a question about
`lab_paths` rather than about the tree. It was **not built here**: batch 9 needs
its own two-way planted control, and a resolver landed without one is the shape
of a guard that has stopped discriminating.

---

### 6.4 `docs/LOCATIONS.md` still does not mention `research/`, `media/`, `ops/` — and now `cases/`

Owed since batch 2 and owed by three batches now. Batch 4 created two roots
without updating it, batch 5 a third, batch 6 a fourth, and its §"where the
bulk lives" table still prices `demo-output/website/dafoam/` at 20,105 files
and 5.76 GB under a path that no longer exists. Recorded here so the debt stays
one line rather than four discoveries. It is not repaired in a move commit
because it is 687 lines of shared governed documentation and the repair is a
document pass, not a path rewrite.

### 6.5 R8's fifteen launchers, the crontab, and the hand-carry

Untouched, and inherited unchanged. R8 moves to `ops/` and every one of batch
6's 2,118 files moves to `cases/`; no launcher was moved and **no membership
list was reconstructed** (D370, L-111). The `@reboot` crontab entry still
invokes `scripts/demo_servers.sh` at its unchanged path and does not dangle;
the crontab was neither read back nor edited, because batch 6 moves nothing it
names. The hand-carry was not run: `solve_registry` and `surfaces` are still
under the webroot at 1,510,309,145 bytes, which is 7H's.

## 7. The gates, both sides, with their finding sets

### 7.1 `scripts/lab_check.py` and the full suite

Before, at `0869284e` over the pre-move worktree: `--no-tests` **FAIL, exit 1,
ran 20/20**, 298.5 s. Full run **FAIL, exit 1, ran 21/21**, 1,513.8 s.
After: `--no-tests` **FAIL, exit 1, ran 20/20**, 212.0 s. Full **FAIL, exit 1,
ran 21/21**, 917.2 s.
**stderr empty on all four runs.**

| Check | before | after |
|---|---|---|
| `scripts/check_pdf_surfaces.py` | FAIL | FAIL |
| `scripts/check_proposal_surface_coverage.py` | FAIL | FAIL |
| `scripts/check_rung_attribution.py` | FAIL | FAIL |
| `scripts/contention_audit.py` | FAIL | FAIL |
| `scripts/installed_registry.py` | FAIL | FAIL |
| `scripts/self_audit.py` | FAIL | FAIL |
| `scripts/check_absolutes.py` | **BLOCKING UNKNOWN, exit 3** | **BLOCKING UNKNOWN, exit 3** |
| `scripts/check_convergence_validate.py` | **PASS, 13/13 known answers** | **PASS, 13/13 known answers** |
| the other 12 | PASS | PASS |
| `sdk/tests` (pytest) | **6 failed / 2,444 collected / 0 skipped** | **6 failed / 2,447 collected / 0 skipped** |

**The six suite failures are the standing baseline in both frames** and are the
same six tests in the same four modules: `test_exec_bits` 1,
`test_fail_open_scan` 1, `test_installed_matches_tracked` 3,
`test_pdf_surfaces` 1.

**Collected counts, not verdicts, because batch 5's finding was invisible to the
verdicts.** Collected goes **2,444 → 2,447**, and
the delta is **exactly the three tests added to `sdk/tests/test_exec_bits.py`**
in §4.2 — 15 tests in that module before, 18 after. Nothing left the suite:
`skipped` is **0** on both sides, 92 files collected on both sides, and the
failing-module list is the same four modules with the same per-module counts.
`--no-tests` reports `15 unrun check(s)` on both sides and the full run `14` on
both; `admitted` is 112 and `not admitted` 67 on both. **Batch 6 moves nothing
into or out of `scripts/` or `sdk/tests/`, so the candidate universe does not
move at all.**

The `--no-tests` finding set and the full finding set are **byte-identical**
between the two frames, compared as sorted verdict lists by `diff` rather than
by eye.

### 7.2 The three standing gates

| Gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B**, digests `1b53ed5a4e9d63cb` / `5519de4237b71ce4` | mid-pass **5 trees / 1,294 files / 1,883,205,283 B**, final **2 / 307 / 1,510,309,145, byte-identical** — §7.2a |
| **G1** rides-along | 2,334 trees, 45,770 files, 14,269,950,892 B | immediately after the move **2,082 / 22,165 / 7,046,286,964 — the batch-6 delta exactly, §3.2**; final 2,207 / 23,859 / 7,680,400,220 under four peer commits |
| **G1** goes-dark-after-batch-2 | 0 | **0** |
| **G2** control corpora | 223 path fields, 0 unresolved | **223, 0** |
| **G3** root binding | `roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (EVIDENCE,)` | **`roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (EVIDENCE,)`** |

**No gate was adjusted.** G1's carry set changed and is reported rather than
repaired; §7.2a establishes it is not this batch's.

**G3's `UNRESOLVED` does not move, and that is the non-trivial half.** Batch 5
watched four destination-only names resolve as `research/closure/` was
assembled. Batch 6 creates `cases/` and moves `UNRESOLVED` not at all, because
every R22/R5 name was already bound to a **pair** and resolved at its legacy
side before the batch. `AMBIGUOUS` is empty **after** as well as before: all
eleven batch-6 names report `state() == "moved"` and none reports `"both"`.

**G2 was fired eight ways**, because a count alone cannot show a corpus still
discriminates:

| arm | citation | resolves to |
|---|---|---|
| 1 must resolve, unmoved | `demo-output/website/closure.html` | itself |
| 2 **must NOT resolve** | `demo-output/website/never_existed.md` | `None` |
| 3 batch-4 successor | `demo-output/plots/C_d/frame_0001.png` | `media/plots/…` |
| 4 batch-5 successor | `demo-output/website/agenda/docket.json` | `research/agenda/docket.json` |
| 5 **this batch, R22** | `demo-output/website/dafoam/ADJOINT_MEMORY_ENVELOPE.md` | `cases/dafoam/…` |
| 6 **this batch, merge CHILD preserved** | `…/tmr-flatplate-finest-grids/runs` | `cases/tmr/tmr-flatplate-finest-grids/runs` |
| 6b **this batch, merge PARENT flattened** | `…/tmr/C4_naca0012_closure.json` | `cases/tmr/C4_naca0012_closure.json` |
| 7 **this batch, R5 root** | `demo-surfaces/naca0015_sail.stl` | `cases/demo-surfaces/…` |
| 8 the webroot still resolves | `demo-output/website/wall/wall.html` | itself |

Arms 6 and 6b together are the merge decision as a live two-way control: the
child keeps its segment and the parent flattens, so a `redirect()` that appended
a child segment to everything would fail 6b and one that flattened everything
would fail 6. **The left-hand spelling in arms 3-7 is the pre-move one and is
withdrawn — do not cite it.**

### 7.2a G1's CARRY SET GREW MID-PASS, IT WAS ANOTHER LANE'S LIVE SOLVER, AND IT CAME BACK ON ITS OWN

Measured immediately after the move, the carry set read **5 trees / 1,294 files
/ 1,883,205,283 B**. Three rows had joined, all under
`docs/campaigns/F14-cooling-ladder/`:

| new HAND-CARRY row | files | bytes | oldest file | newest file | tracked at that HEAD |
|---|---:|---:|---|---|---:|
| `K2b_runs` | 514 | 212,734,443 | 03:35 | 03:48 | **0** |
| `K0cT_runs` | 469 | 160,076,950 | 03:42 | 03:48 | **0** |
| `K2e_runs` | 4 | 84,745 | 03:37 | 03:48 | **0** |

**Every file in all three was created while this batch ran**, and `pgrep`
named the writer: **`buoyantBoussinesqSimpleFoam`, PID 1200604**, writing
`log.buoyantBoussinesqSimpleFoam` into those trees at that moment. None is under
a batch-6 source. All three are R25 run archives that `hand_carry` classifies as
hand-carry because they held **no tracked file** and no ancestor was renamed as
a unit.

**Then the F14 lane committed, and the rows went away.** Four peer commits
landed during this pass — `fa2c8bb0`, `495a94ea`, `bffa7ca0`, `cccf7a9f` — which
track those trees; re-derived at `cccf7a9f` the carry set is **2 trees / 307
files / 1,510,309,145 bytes, byte-identical to the plan's, to batch 4's and to
batch 5's**, with the same two digests `1b53ed5a4e9d63cb` and
`5519de4237b71ce4` and `walk_errors = 0`.

**Both readings are reported because either one alone is misleading.** The first
would have said batch 6 grew the carry set by 987 files; the second alone would
have said nothing happened. What actually happened is
`MOVE_MAP_EXECUTION_2026-08-17.md` §3.1 exactly — *"every count in this section
is a frame, and these trees move under you"*, the same paragraph that records
`THERMAL_K0_runs` reading 387, 362 and 368 files in forty minutes and then not
belonging on the list at all. **A dark tree is dark until its lane commits.**
The gate was **not adjusted**, and the transient was not smoothed away.

**RIDES ALONG shows the same two effects and they are separable.** Immediately
after the move it read 2,082 / 22,165 / 7,046,286,964 — the batch-6 delta to the
byte (§3.2). At `cccf7a9f` it reads 2,207 / 23,859 / 7,680,400,220: +125 trees
and +634 MB, all of it the F14 lane's newly-tracked run trees acquiring dark
subtrees under an ancestor R25 renames. None of it is batch 6's.

---

## 8. WHAT BREAKS IF BATCH 6 LANDS AND BATCH 7 NEVER DOES

**Nothing breaks, and `cases/` is complete rather than half-assembled.**
`MOVE_MAP_EXECUTION_2026-08-17.md` §4 predicts for a partial batch 6 that
*"`cases/tmr` exists and `cases/dafoam` does not"*. This one landed all ten R22
sources and R5 in one commit, so `cases/` holds every physics family the map
sends it and the webroot holds none of them.

What is true if batch 7 never lands:

1. **`verification/` does not exist and the webroot still holds
   `campaign/`.** `demo-output/website/` retains 2,376 tracked files —
   `campaign/` and its run archives, `certificates/`, `credibility/`,
   `monitor/`, `paraview/`, the five served files, `solve_registry/`,
   `surfaces/`, and X3's `latex/` and `motorbike-video/`. R20, R21, R24, R19 and
   R25 are all unrun. Every citation to them resolves at its literal path, so
   nothing degrades.

2. **The `.gitignore` is SPLIT ACROSS THE TWO BATCHES ON PURPOSE, and the half
   that is still deferred is the dangerous one to forget.** §4.1 re-pointed the
   dafoam half of batch 2's solver-output rules; the `campaign/` half still
   reads `demo-output/website/campaign/**/log.*` and must be re-pointed **in
   batch 7's own commit**, together with `.gitignore:122-123`'s two
   `THERMAL_K0_runs` re-inclusions, without which that case's 97 tracked
   initial-condition files stop being tracked at the next index refresh
   (`MOVE_MAP_EXECUTION_2026-08-17.md` §3.2). Batch 6 has now demonstrated the
   mechanics of that re-point on 20 rules; batch 7 has 8 more of the same kind
   and one negation pair, and the batch-2 comment that misrouted this batch's
   half has been amended in place so the next reader meets the correction where
   the rules are.

3. **`MESH_AUDIT_runs` is still the standing precondition on batch 7 and batch
   6 did not change it.** Option A held: the 78 `*.log.checkMesh` files are
   still tracked, `hand_carry derive`'s goes-dark-after-batch-2 section reads
   **0** on both sides of this batch, and the carry set is byte-identical.

4. **`lab_paths` answers `moved` for the batch-4/5/6 regions and `legacy` for
   the rest, and both are right.** `AMBIGUOUS` is empty after the move as well
   as before — every batch-6 name reports `state() == "moved"` and none reports
   `"both"`. `UNRESOLVED` is `(EVIDENCE,)` on both sides, and correctly: 7H
   assembles it.

5. **The shared index is exactly 2,118 entries stale**, and by construction:
   all 11 `git mv`s ran under a private `GIT_INDEX_FILE` and the commit's index
   was rebuilt from the observed HEAD, so neither the shared index's state
   before this pass nor its state after was read. After this commit lands the
   shared index lists the 2,118 sources at their pre-move paths. The surgical
   `git update-index --force-remove --stdin` over **only this agent's 2,118
   paths** was **not run**, because this pass was directed not to write the
   shared index; it is filed as owed and the path list is §2's table.

6. **The citation guard's number does not move because of batch 6, and it does
   not become less urgent.** §6.2.

**And the batch that becomes more expensive if it waits.** Batch 7 is the
largest mass and it is now the only batch whose `.gitignore` obligation is
outstanding. Every day it waits, another lane writes into
`demo-output/website/campaign/` under rules that will have to be re-pointed
around live content — which is exactly the condition batch 6 avoided by moving
trees whose newest write was 11.3 hours old.

---

## 9. Method

- Every path-derived count is over `git ls-tree -r -z --name-only`, at a named
  commit, **never `git ls-files`**. The shared index was not read for any
  measurement and not written by any step. `git status` and `git diff HEAD` were
  not used for anything: the shared index lists batch 4's, 5's and now 6's
  destinations at their old paths, and git's rename inference is never quoted
  here.
- **stderr was captured on every walk, every `git` invocation and every
  subprocess** and was empty on all of them, including all 11 `git mv` calls,
  which were checked for a non-empty **stdout** as well as a non-empty stderr
  and a non-zero exit.
- **No count was piped into `head`.**
- Every before/after pair passes through the same instrument in the same frame.
  Path comparisons are **Python set comparisons plus a byte total**, with a
  sha256 of the sorted relative-path set carried as a third witness — never a
  digest alone, which is the trap batch 5 measured on R23.
- `hand_carry.measure()` **raises** on any walk or stat failure rather than
  returning a smaller number; all 22 directory measurements reported
  `walk_errors = 0`.
- The **inverse `mv` list was written before the batch started**, as
  `MOVE_MAP_EXECUTION_2026-08-17.md` §4 requires — 11 lines plus the `rmdir`,
  **children before parents**, because `cases/tmr/*` must come out before
  `cases/tmr`. It is an `mv` list and not `git reset --hard`, and §3.4's own
  note is why: a reset restores the 2,118 tracked files and leaves 23,920
  untracked, gitignored ones (7.22 GB) in the new directories where
  `git status` will not show them and `git clean` would delete them.
- The sources were **re-measured immediately before each move** against the
  plan's own figures, with an abort on any drift; drift was **zero on all
  eleven**. The newest write anywhere under a batch-6 source was **11.3 hours**
  old (dafoam) and 26-32 hours for the other ten, so no tree was carried out
  from under a live writer. `pgrep` for a solver returned only this shell's own
  command line — the L-6 false positive `mega_batch_keeper.sh` documents — and
  nothing else.
- The ownership precondition was **re-run rather than inherited**, as the plan's
  own amendment demands: `find . -path ./.git -prune -o ! -user ubuntu -print`
  returns **0 files repo-wide, stderr empty**, before the batch. `find cases
  -user root | wc -l` returns **0** after it.
- Commit membership between two named commits (`4d7c195a` and `0869284e`) was
  used wherever a question could have been answered by a date; nothing here is
  ordered or selected by one.
- This record does not appear in its own results: every measurement was taken
  before the commit that lands it, and the after-suite ran before this file
  existed.

### 9.1 A PEER LANE OVERWROTE THIS SESSION'S UNCOMMITTED `.gitignore` EDIT, AND NOTHING SAID SO

Recorded because it is the destructive twin of D361 and it cost real work.
Between this batch's `.gitignore` edit and its commit, the F14 lane landed four
commits, two of which add blocks to `.gitignore`. Afterwards the **worktree**
`.gitignore` was byte-identical to the new HEAD and **all twenty of this
batch's re-points were gone** — not conflicted, not reported, simply absent. It
was caught by `cmp`-ing the worktree copy against `git show HEAD:.gitignore`
before building the commit, which is the check the brief's *"the write-back is a
MERGE, never an overwrite — read the worktree copy at write time"* rule exists
to force.

D361 records the benign direction of this — a peer commit **capturing** this
lab's `LESSONS.md` append, so the lesson landed under someone else's message.
This is the other direction: a peer **replacing** the worktree file, so an
uncommitted edit is destroyed with no error and no signal. `docs/USING_THIS_LAB.md`
§9's private-index protocol protects the committer from capturing others and has
no clause protecting an uncommitted worktree edit from being replaced, which is
exactly the gap D361 already names.

**Repaired by re-applying, not by re-writing.** The twenty re-points were
re-applied on top of the peer's current content by exact-string replacement, and
both of the peer's new blocks (`K2b_runs`, `K0cT_runs`) are intact in the
committed file — verified by diffing the result against `HEAD:.gitignore` and
reading every hunk. **The eleven other files this batch edits were checked the
same way and none was touched.**

**The concrete guard is the one D361 already proposes and this incident
seconds:** land an edit the moment it is written rather than batching it to the
end of a pass. A move batch cannot do that for its move, but it can for its
`.gitignore`, and next time it should.

---

## 10. What batch 6 did not do

No file was deleted or untracked; nothing left the disk. The shared index was
not written and its pre-existing state was not reverted. `_SHIPPING_RE` was not
touched and `scripts/check_absolutes.py` is byte-identical to HEAD (§6.1). R8's
15 launchers were not moved and no membership list was invented for them.
`check_evidence_paths_exist` was not converted to `lab_paths.resolve()` — that
is batch 9 and it needs its two-way control (§6.2). No citation inside any
append-only record was edited. `docs/LOCATIONS.md` was not updated and is still
owed (§6.4). The hand-carry was not run. The crontab was not read back or
edited. `lab_paths.py` itself was **not edited**: R22's ten rows and R5's one
were already bound, and batch 6 is the first move batch that needed no change
to the map. No solver was launched and nothing was registered.
