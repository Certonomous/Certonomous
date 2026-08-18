# MOVE_MAP batch 7 — R25 is DEFERRED under a live solver, the `.gitignore` split lands with its 78-file option-A closure, and the depth defect is nineteen modules rather than seven

**2,367 tracked files moved by 294 `git mv` invocations — 33 naming a
DIRECTORY, 261 naming a loose file that has no directory to name — one source
per invocation, stderr AND stdout captured and empty on all 294, exit 0 on all
294.** Nothing was deleted. **78 files were untracked** and every one of them is
still on disk at its new path: that is option A closing, not a loss, and §5 is
the arithmetic. The **shared index was neither read nor written**: all 294
renames ran under a private `GIT_INDEX_FILE` seeded by `git read-tree` against
the observed HEAD.

**R25 IS DEFERRED, AND IT IS THE FINDING OF THIS BATCH.** The plan prices
batch 7 as R20, R21, R24 **and R25**. R25's sources are
`docs/campaigns/F14-cooling-ladder/{K0c_runs, K0b_mesh_sensitivity, K2b_runs,
K0cT_runs}`, and at the moment this batch ran a **live
`buoyantBoussinesqPimpleFoam` (PID 1809944) was writing
`K2b_runs/K2bU_trans/log.buoyantBoussinesqPimpleFoam`**, three peer shell loops
were polling that directory with their CWD inside it, and the F14 lane had
landed **six commits in the previous 75 minutes**. §2 is the measurement and the
criterion. Moving a tree out from under a live writer is the one precondition
`MOVE_MAP_EXECUTION_2026-08-17.md` §4 and batch 6's §9 both state and neither
had to spend. **1,554 tracked files remain owed**, and what they need is in §2.3
so the next pass does not re-derive it.

Measured over `git ls-tree -r -z --name-only`, at a named commit, **never
`git ls-files`**. stderr was captured on every walk, every `git` invocation and
every subprocess. No count was piped into `head`.

**Anchors.** The pass opened at **`aebbcac8`** and the moves were made at
**`fccedd3a`**, which is the HEAD the private index was seeded from. Three peer
commits landed between those two — `d4575a69`, `f6c799fa`, `fccedd3a` — and
**one of them, `f6c799fa`, modified a batch-7 source**
(`campaign/NINE_ACT_GATE_TABLE.md`). The drift check fired on it, the batch
**aborted rather than moving a stale snapshot**, and the whole 294-source
snapshot was re-taken at `fccedd3a` before anything moved. That is the check
working, and it is reported rather than smoothed away.

---

## 1. THE `.gitignore` SPLIT — twelve rules, and one source root became two destination roots

Batch 6 §8.2 handed this over: *"the `campaign/` half still reads
`demo-output/website/campaign/**/log.*` and must be re-pointed in batch 7's own
commit, together with `.gitignore:122-123`'s two `THERMAL_K0_runs`
re-inclusions."* Both halves are in this commit.

**Derived, not carried.** Every non-comment line of `.gitignore` was tested for
whether it names a batch-7 source, by prefix rather than by grep. **Twelve
rules** name an R20/R21/R24 source; **fourteen more name an R25 source and are
DELIBERATELY UNTOUCHED**, because R25's trees have not moved (§2).

| was | now | why |
|---|---|---|
| `:58 campaign/D5_rsm_runs/*/[0-9]*/` | `verification/runs/D5_rsm_runs/*/[0-9]*/` | R20, single destination |
| `:59 campaign/*_runs/*/[0-9]*/` | `verification/runs/*_runs/*/[0-9]*/` | R20, single destination |
| **`:133 !campaign/THERMAL_K0_runs/*/0.orig/`** | `!verification/runs/THERMAL_K0_runs/*/0.orig/` | **the re-inclusion pair** |
| **`:134 !campaign/THERMAL_K0_runs/*/0.orig/**`** | `!verification/runs/THERMAL_K0_runs/*/0.orig/**` | **the re-inclusion pair** |
| `:210 campaign/**/[1-9]*/` | 3 rules | one root became two |
| `:211 campaign/**/0.[0-9]*/` | 3 rules | one root became two |
| `:220 !campaign/4G_runs/` | `!verification/runs/4G_runs/` | R20 |
| `:223 campaign/**/log.*` | 3 rules | one root became two |
| `:224 campaign/**/*.log` | 3 rules | one root became two |
| `:225 campaign/**/*.log.*` | 3 rules | one root became two |
| `:240 !campaign/MESH_AUDIT_runs/` | **REMOVED** | option A closes, §5 |
| `:241 !campaign/MESH_AUDIT_runs/**` | **REMOVED** | option A closes, §5 |

### 1.1 The batch-2 comment misrouted the SPLIT, not only the batch

Batch 6 found that *"batch 7 must re-point these two roots"* named `campaign/`
and `dafoam/`, and that `dafoam/` was R22 and therefore batch 6's. The residue
is subtler and it is this batch's: **`campaign/` is ONE source root and TWO
destination roots.** R20 sends `campaign/<tree>_runs` to `verification/runs/`
and R21 sends everything else to `verification/campaign/`, so a rule scoped
`campaign/**` cannot be re-pointed by substituting one prefix.

**The second spelling is load-bearing and was measured before it was written.**
`git check-ignore --no-index -v` over all **19,679 files on disk** under the 294
sources reports **8 ignored files under R21 territory** — one
`motorBike_production.log.checkMesh` under `DRAW_SCATTER_RETROFIT/` and seven
`*.log` under `MESH_CERT_RULINGS_2026-08-10/recheck_logs/`. A re-point to
`verification/runs/**` alone would have **un-ignored those 8**.

**And the R20 spelling is `*_runs`/`*_work`, not `**`, which is batch 2's own
scope ruling preserved.** R25 lands `docs/campaigns/<campaign>/<tree>_runs` at
`verification/runs/<campaign>/<tree>_runs`, whose FIRST segment is a campaign
name. A `verification/runs/**/log.*` would therefore reach the F14 lane's run
trees the moment R25 lands — silently, to another lane's next solver log — which
is exactly what `.gitignore:165-186`'s header refused to do. `*_runs`/`*_work`
matches R20's territory exactly and R25's not at all.

### 1.2 THE ASSERTION, with stderr captured

All **2,367 tracked destinations** through `git check-ignore --no-index
--stdin`, **stderr empty**, exit 0:

```
tracked destinations   2,367
IGNORED                   78   -- all 78 MESH_AUDIT_runs, section 5
OTHER IGNORED              0
```

**0 of the 2,289 surviving tracked destinations is ignored.** The 78 are ignored
by design and untracked in this same commit.

Whole-tree, at the same instrument: **19,679 files on disk under
`verification/`, 17,390 ignored, 2,289 not ignored** — against 17,312 / 2,367
measured at the old spelling before the move. **Zero files were un-ignored; 78
were newly ignored and all 78 are `MESH_AUDIT_runs`.** The per-file ignore
decision, mapped forward through `lab_paths.redirect()`, is otherwise identical
on both sides — asserted as a Python set difference in both directions, not as a
count.

`demo-output/website/campaign/R4_runs/.gitignore` is a **tracked nested ignore
file** that carries 760 of the ignore decisions and every one of its patterns is
relative, so it travels inside the tree and needed no re-point. It is one of the
105 tracked files in that rename.

---

## 2. R25 IS DEFERRED — the measurement, the criterion, and what is owed

### 2.1 The criterion, stated before it was applied

A source is not moved if, immediately before the move, **(a)** a process is
writing inside it, **(b)** another process has its working directory inside it,
or **(c)** the lane that owns it has committed to it within the pass. Each is
falsifiable and each was tested.

### 2.2 R25 fails all three

```
$ ps -eo pid,cmd | grep -i foam
1809944 buoyantBoussinesqPimpleFoam
1811364 ... cd .../docs/campaigns/F14-cooling-ladder/K2b_runs && until [ -f K2bU_trans/COST.txt ] ...
1814609 ... cd .../docs/campaigns/F14-cooling-ladder/K2b_runs && until python3 -c ...
1814748 ... cd .../docs/campaigns/F14-cooling-ladder/K2b_runs && until python3 -c ...

newest write under docs/campaigns/  05:43:36  K2b_runs/K2bU_trans/log.buoyantBoussinesqPimpleFoam
the clock                           05:43:36
```

The file was being written **in the second the measurement was taken**. Three
peer shell loops hold that directory as their CWD. The F14 lane committed at
04:07, 04:22, 04:24, 04:39, 04:40, 04:42, 04:51, 05:15, 05:17 and 05:21 — **ten
commits in 75 minutes**, three of them inside this pass.

By contrast, the newest write anywhere under the **294 sources this batch did
move** was **04:56** (`NINE_ACT_GATE_TABLE.md`, landed by peer commit
`f6c799fa`), 48 minutes before the move, and `find . ! -user ubuntu` returned
**0 files repo-wide, stderr empty**.

**What a `git mv` of `K2b_runs` would have done** is not a hypothetical: it
would have renamed the directory out from under an open solver (whose writes
would have continued into the moved inode, invisible at the path its own lane
reads), left three polling loops testing `K2bU_trans/COST.txt` against a
directory that no longer exists, and put the next F14 commit at a path this
batch had just vacated. §3.4 of the plan calls a per-file `git mv` loop the way
to lose gigabytes silently; this is the other way.

### 2.3 What is owed, measured so the next pass does not re-derive it

| | at the ruling (`4d7c195a`) | batch 5's frame | at `aebbcac8` | at `fccedd3a` |
|---|---:|---:|---:|---:|
| R25 tracked files | 315 | ~487 | 1,514 | **1,554** |

It grew by **40 files in 45 minutes** while this pass ran. Also owed with it:

* the **fourteen `.gitignore` rules** at lines 144-149, 161-163 and 260-264,
  which name `K0c_runs`, `K0b_mesh_sensitivity`, `K2b_runs` and `K0cT_runs` and
  are correct exactly as long as those trees have not moved;
* `exec_bits.OWNERS` — 0 waived paths are under `docs/campaigns/` today, so R25
  does not inherit a family assignment and **must decide one**: those files are
  "Infrastructure and Standards" under `docs/` and would become "Cases" under
  `verification/runs/`. The comment beside the new rows says so;
* nothing in `lab_paths` — `F14_K0C_RUNS` and `F14_K0B_MESH_SENSITIVITY` are
  already bound to pairs and report `state() == "legacy"`, which is correct.

**`lab_paths` was not edited by this batch**, for the same reason batch 6 needed
no edit: every R20/R21/R24 name was already bound.

---

## 3. THE POPULATION, RE-DERIVED — 2,367 against the plan's 8,643 and batch 5's 2,854

`MOVE_MAP_EXECUTION_2026-08-17.md` §4 prices batch 7 at **8,643 files at
`4d7c195a`**. Batch 4 corrected that to **2,854**. Re-derived here at
`fccedd3a` by running `lab_paths.redirect()` over every tracked path and keeping
those whose successor is under `verification/`:

| | files |
|---|---:|
| R20, 27 run archives under `campaign/` | 2,083 |
| R21, 3 directories + 261 loose files under `campaign/` | 277 |
| R24, `certificates` + `credibility` + `monitor` | 7 |
| **executed by this batch** | **2,367** |
| R25, `docs/campaigns/F14-cooling-ladder/**` | **1,554 — DEFERRED** |
| batch 7 as planned | 3,921 |

**Against the plan: −6,276 on the planned 8,643, and −487 on batch 5's 2,854.**
The first difference is batch 2's untracking, exactly as batch 6 found for its
own figure (3,554 → 2,118, all of it dafoam). The second is not a loss at all:
batch 5's 2,854 was measured before the F14 lane had landed most of R25, and
**R25 alone is now larger than the whole figure batch 5 quoted.** Every tracked
path classifies into exactly one of the four rows with **zero unattributed**,
and the webroot's 2,377 tracked files reconcile: 2,361 `campaign/` + 7 R24 +
4 X3 + 4 served + 1 `wall/wall.html`, less the served PNG counted once.

`demo-output/website/` retains **10 tracked files** after this batch: the four
R13 served pages, the served PNG under `campaign/`, and X3's five.

---

## 4. GRANULARITY, AND THE PROOF ON BOTH SIDES

**33 of the 294 sources are directories and each went by exactly one `git mv`
naming the DIRECTORY. The other 261 are loose files sitting directly in
`campaign/`, which have no directory to name**, so per-file is the correct
granularity for them and the ride-along invariant does not apply to a file.

`hand_carry.measure()` ran against each source immediately before its move and
against its destination immediately after — file count on disk, byte total, and
the sha256 of the **sorted relative-path set**. It **raises** rather than
returning a short number on any walk or stat failure; **all 66 directory
measurements reported `walk_errors = 0`**, and the 261 files were compared by
full-content sha256.

| source -> destination | tracked | on disk | bytes | sorted path-set sha256(16) | source gone | destination set |
|---|---:|---:|---:|---|---|---|
| `campaign/F7_runs` -> `verification/runs/F7_runs` | 442 | 10901 | 2,718,352,001 | `663c17207654c868` | yes | **IDENTICAL** |
| `campaign/R4_runs` -> `verification/runs/R4_runs` | 105 | 1033 | 1,662,257,181 | `4ac241b0dda66656` | yes | **IDENTICAL** |
| `campaign/F8_runs` -> `verification/runs/F8_runs` | 56 | 653 | 716,951,956 | `1c4a65d41370a9f7` | yes | **IDENTICAL** |
| `campaign/W2_sparta_runs` -> `verification/runs/W2_sparta_runs` | 170 | 1130 | 623,471,432 | `1d31a9b514ad7db8` | yes | **IDENTICAL** |
| `campaign/F5_runs` -> `verification/runs/F5_runs` | 66 | 99 | 231,936,665 | `7fe9c8640d6513f5` | yes | **IDENTICAL** |
| `campaign/W3_runs` -> `verification/runs/W3_runs` | 81 | 240 | 150,423,363 | `753834262ae82fec` | yes | **IDENTICAL** |
| `campaign/F3_runs` -> `verification/runs/F3_runs` | 211 | 691 | 146,473,695 | `4121a152d727733d` | yes | **IDENTICAL** |
| `campaign/DMR_runs` -> `verification/runs/DMR_runs` | 27 | 839 | 144,039,094 | `ace5ca2c3e5980c0` | yes | **IDENTICAL** |
| `campaign/MODEL_FORM_runs` -> `verification/runs/MODEL_FORM_runs` | 122 | 511 | 139,631,511 | `9f0242deafee914f` | yes | **IDENTICAL** |
| `campaign/F4_runs` -> `verification/runs/F4_runs` | 177 | 1007 | 135,251,158 | `77de7210565a41dc` | yes | **IDENTICAL** |
| `campaign/F9_work` -> `verification/runs/F9_work` | 122 | 520 | 129,017,369 | `4857a7c2f46019e7` | yes | **IDENTICAL** |
| `campaign/F6b_runs` -> `verification/runs/F6b_runs` | 89 | 506 | 89,076,061 | `4e52e9ab8fdceffd` | yes | **IDENTICAL** |
| `campaign/DPW8_V2_runs` -> `verification/runs/DPW8_V2_runs` | 29 | 261 | 42,141,268 | `3ccf15da42a43fe4` | yes | **IDENTICAL** |
| `campaign/4G_runs` -> `verification/runs/4G_runs` | 16 | 42 | 23,013,604 | `cf6af939afe4e439` | yes | **IDENTICAL** |
| `campaign/W1_runs` -> `verification/runs/W1_runs` | 18 | 42 | 16,944,738 | `e7b99d695bacfc70` | yes | **IDENTICAL** |
| `campaign/THERMAL_K0_runs` -> `verification/runs/THERMAL_K0_runs` | 80 | 368 | 12,553,796 | `72d3c50c54f8ba51` | yes | **IDENTICAL** |
| `campaign/W1_hump_runs` -> `verification/runs/W1_hump_runs` | 18 | 24 | 10,257,495 | `bfe40cdf5f929e90` | yes | **IDENTICAL** |
| `campaign/D5_rsm_runs` -> `verification/runs/D5_rsm_runs` | 60 | 188 | 10,107,672 | `5805fb1b10005b06` | yes | **IDENTICAL** |
| `campaign/FPE_DIAG_runs` -> `verification/runs/FPE_DIAG_runs` | 7 | 22 | 7,246,631 | `0554168f723f9998` | yes | **IDENTICAL** |
| `campaign/F2_runs` -> `verification/runs/F2_runs` | 17 | 77 | 5,366,163 | `e7044a915cbdb4b2` | yes | **IDENTICAL** |
| `campaign/F5c_runs` -> `verification/runs/F5c_runs` | 59 | 109 | 2,104,364 | `02dab3a0eda6f392` | yes | **IDENTICAL** |
| `campaign/MESH_AUDIT_runs` -> `verification/runs/MESH_AUDIT_runs` | 78 | 78 | 380,082 | `1906f3c55295b5da` | yes | **IDENTICAL** |
| `campaign/F12_runs` -> `verification/runs/F12_runs` | 8 | 8 | 262,893 | `d1a7385450994173` | yes | **IDENTICAL** |
| `monitor` -> `verification/monitor` | 3 | 3 | 138,794 | `7dcbc96b326f7ff0` | yes | **IDENTICAL** |
| `campaign/B52_RUNG6_REPLICATE_runs` -> `verification/runs/B52_RUNG6_REPLICATE_runs` | 17 | 23 | 88,713 | `9e5c692f30e699c8` | yes | **IDENTICAL** |
| `campaign/MESH_CERT_RULINGS_2026-08-10` -> `verification/campaign/MESH_CERT_RULINGS_2026-08-10` | 10 | 17 | 82,851 | `4120f13244b4fa67` | yes | **IDENTICAL** |
| `campaign/reports` -> `verification/campaign/reports` | 2 | 2 | 75,610 | `56fb8175c520c8b8` | yes | **IDENTICAL** |
| `campaign/GEN_ALT_runs` -> `verification/runs/GEN_ALT_runs` | 5 | 12 | 41,917 | `e2a43b35ab4603f5` | yes | **IDENTICAL** |
| `campaign/DRAW_SCATTER_RETROFIT` -> `verification/campaign/DRAW_SCATTER_RETROFIT` | 4 | 5 | 28,772 | `e8ab04ceb93d4ae0` | yes | **IDENTICAL** |
| `credibility` -> `verification/credibility` | 1 | 1 | 26,444 | `9daee440a8ae3d9e` | yes | **IDENTICAL** |
| `campaign/F11_runs` -> `verification/runs/F11_runs` | 2 | 2 | 19,366 | `f9a7698c3065b268` | yes | **IDENTICAL** |
| `certificates` -> `verification/certificates` | 3 | 3 | 13,695 | `abdd6aae40415aed` | yes | **IDENTICAL** |
| `campaign/F5b_runs` -> `verification/runs/F5b_runs` | 1 | 1 | 1,352 | `01da6e45e7f2f9a7` | yes | **IDENTICAL** |
| **261 loose R21 files**, one `git mv` each | 261 | 261 | 6,101,082 | per-file sha256 | yes | **IDENTICAL** |
| **BATCH 7** | **2,367** | **19,679** | **7,023,878,788** | | | |

Every source is **gone**. Every destination holds **exactly the source's sorted
relative-path set**, asserted as a Python **set equality plus a byte total**,
with the sorted-path sha256 carried as a **third witness only** — batch 5
measured two trees sharing a digest and differing in bytes, so a digest alone
would have called a destructive flat merge clean. All 33 digests are identical
across the move as well.

**There is no merge family in this batch.** All 294 destinations are distinct,
`redirect()` over the whole tracked corpus reports **0 successor collisions
repo-wide**, and no destination lands on a tracked path that does not move.

### 4.1 THE RIDE-ALONG INVARIANT IS WORTH 6.21 GB HERE

`hand_carry.derive()` at `fccedd3a`, before anything moved:

| bucket | whole repository | **under a batch-7 source** |
|---|---|---|
| HAND-CARRY | 2 trees / 307 files / 1,510,309,145 B | **0 / 0 / 0** |
| RIDES ALONG | 2,212 / 24,003 / 7,743,986,953 | **1,457 / 16,631 / 6,210,209,869** |
| STAYS PUT | 257 / 33,892 / 7,843,794,447 | **0 / 0 / 0** |
| DISCARD | 11 / 56 / 1,904,409 | **1 / 1 / 28,362** |

**A per-file `git mv` loop over the 33 directories would have left 6,210,209,869
bytes behind**, and `git status` would have said nothing, because every one of
those files is gitignored. The five largest carriers:

| carrier | dark trees | files | bytes |
|---|---:|---:|---:|
| `campaign/F7_runs` | 680 | 10,309 | 2,604,353,520 |
| `campaign/R4_runs` | 54 | 872 | 1,649,375,242 |
| `campaign/F8_runs` | 28 | 579 | 640,369,807 |
| `campaign/W2_sparta_runs` | 89 | 935 | 478,086,333 |
| `campaign/DMR_runs` | 34 | 798 | 142,086,011 |
| 16 more | 572 | 3,138 | 695,938,956 |

**The one DISCARD row under a batch-7 source is reported rather than treated as
zero.** `campaign/F7_runs/__pycache__` (1 file, 28,362 B) rides along physically
because it sits inside a moving directory. That is the directory rename, not the
hand-carry mechanism, which never carries a discard row; it is named here so the
"0 discard rows" line of batch 6's table is not read as a general property.

### 4.2 The arithmetic closes on the other side, to the byte

After the move, `hand_carry derive` reads:

```
RIDES ALONG   2,212 -> 781      24,003 -> 7,868     7,743,986,953 -> 1,793,047,491
STAYS PUT       257 -> 258      33,892 -> 53,571    7,843,794,447 -> 14,867,690,928
HAND-CARRY        2 -> 2           307 -> 307       1,510,309,145 -> 1,510,309,145
GOES DARK AFTER BATCH 2:  0 -> 0
```

The 1,457 ride-along rows did not vanish; they are under `verification/`, which
is itself dark at a HEAD that predates this commit, so STAYS PUT absorbs them —
**+1 tree**, and that tree is `verification/` at **19,681 files and
7,023,933,919 bytes**. Against the 19,679 files and 7,023,878,788 bytes that
moved, that is **+2 files and +55,131 bytes**, and both are accounted for
exactly:

```
19 repaired modules, comment growth        +17,812 B
verification/campaign/MESH_CERT_RULINGS_2026-08-10/__pycache__/recheck_95.cpython-312.pyc   +8,968 B
verification/runs/F7_runs/__pycache__/f7a_contract.cpython-312.pyc                        +28,351 B
                                           -------
                                            55,131 B   exact
```

The two `.pyc` files were written **at their new paths** by
`test_recheck_population.py` and `test_f7a_contract.py` during the after-run,
which is itself evidence that those two tests followed the map. Both are
untracked and gitignored.

**The carry set did not move.** 2 trees / 307 files / **1,510,309,145 bytes**,
digests `1b53ed5a4e9d63cb` and `5519de4237b71ce4`, `walk_errors = 0` — identical
to the plan's, to batch 4's, to batch 5's and to batch 6's. **The hand-carry was
not run**: `solve_registry` and `surfaces` are still under the webroot, and that
is 7H's.

---

## 5. `MESH_AUDIT_runs` — option A closes, and nothing was lost

The ruling of 2026-08-17: batch 2 spares the 78 `*.log.checkMesh` so that batch
7's `git mv` does not abort on a tree with no tracked file, and they are
untracked at their new path afterwards. `.gitignore:231-241` says **"REMOVING IT
IS PART OF BATCH 7"** in as many words.

Executed in this commit, in this order:

1. `git mv demo-output/website/campaign/MESH_AUDIT_runs verification/runs/MESH_AUDIT_runs` — 78 tracked, 78 on disk, **380,082 bytes**, path set identical, digest `1906f3c55295b5da`;
2. the two negations removed from `.gitignore`;
3. `git update-index --force-remove --stdin` over **only those 78 paths**, in the private index, stderr empty.

**Nothing was deleted.** After the commit: **78 files on disk at
`verification/runs/MESH_AUDIT_runs`, 380,082 bytes, 0 tracked, 78 ignored** —
matched by `verification/runs/*_runs/**/*.log.*`, which is the rule that would
have reached them at the old spelling. The figures are byte-identical to the
ruling's own re-measurement at `4d7c195a`.

This is the only place in this commit where a source has no destination, and it
is why the tree diff's D set is 2,367 while its A set is 2,289 (§9).

---

## 6. THE DEPTH DEFECT — nineteen modules, not seven, and one of them is not batch 7's

Batch 6 found `sdk/tests/test_a2_shape.py:28` deriving a repository root as
`_LADDER.parents[3]`, a depth assumption about a moving path with **no path
literal in it**, so the exhaustive no-suffix-filter scan that reads every
tracked non-markdown file cannot match it (L-127, D385).

**Found by searching for relative-depth derivation, not for paths.** Patterns:
`.parents[N]`, `.parent.parent`, `../..`, `dirname(dirname`, `.parts[`,
`cd ..`. Run over **all 2,368 tracked files under the batch-7 sources with no
suffix filter**, 0 unreadable: **19 non-markdown files carry the class, at 20
sites.** The brief inherited a figure of seven; the re-derivation is 19, and
**18 of the 19 land on `/home/ubuntu` after the move** — proved by executing the
unrepaired expression at the new path:

```
verification/campaign/RULE_O_DENOMINATOR_MEASUREMENT_2026-08-15.py  parents[3] -> /home/ubuntu
verification/campaign/V16_{AUTHOR_HELDOUT_SET,GRADE_HELDOUT_SETS,
                           GRADE_ROUND5_PROBES,GRADE_ROUND6_PROBES,
                           PRECISION_SET}.py                        parents[3] -> /home/ubuntu
verification/runs/F5_runs/{run_rung,cylinder_ladder,cylinder_ladder_3d}.py
                                                                    parents[4] -> /home/ubuntu
verification/runs/F5b_runs/run_pitch.py                             parents[4] -> /home/ubuntu
verification/runs/F5c_runs/{collect,run_step}.py                    parents[4] -> /home/ubuntu
verification/runs/F8_runs/s10_replay/{s10d_corpus_replay,
                                      replay_s10_s12_pfinit}.py     parents[5] -> /home/ubuntu
verification/runs/F9_work/{setup_f9_round3,f9_criteria,analyze_f9}.py
                                                                    parents[3] -> /home/ubuntu
verification/runs/THERMAL_K0_runs/run_controls.sh          $HERE/../../../.. -> /home/ubuntu
verification/runs/F9_work/finalize_f9.py    parents[1] -> .../verification   (NOT /home/ubuntu)
```

`finalize_f9.py` is the nineteenth and it fails differently: it reached
`solve_registry` by counting two segments up, so after the move it names
`verification/solve_registry`, a directory that will never exist. **7H carries
`solve_registry` to `evidence/solve_registry`, 1,508,128,888 bytes**, so a
repo-root-relative literal would dangle there too. That one binds the NAME:
`lab_paths.SOLVE_REGISTRY`, which is bound to the pair and correct on both sides
of the carry.

### 6.1 The repair is a SEARCH, and it fails closed

Every one of the 19 now derives the root by searching upward for the marker
`scripts/lab_paths.py` — R9 leaves `scripts/` where it is — rather than counting
segments:

```python
_REPO_ROOT = next((_p for _p in Path(__file__).resolve().parents
                   if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError("cannot locate scripts/lab_paths.py above %s; refusing to "
                       "guess a repository root" % __file__)
```

and the shell one walks up with `dirname` and `exit 2`s rather than continuing
with a root that is not there. **The answer no longer depends on the file's
depth**, which is the property `parents[N]` cannot have.

**Proved by execution, 19 of 19**: every repaired derivation returns
`/home/ubuntu/Certonomous`, the shell one returns it and finds
`scripts/heat_balance.py` beside it, and the names it feeds resolve —
`RULE_O`'s `PROB`, `QCR` and `ZIP` all exist, `analyze_f9`'s `SDK` and `CURRIC`
exist, `finalize_f9`'s `REG` is `lab_paths.SOLVE_REGISTRY`.

**And the must-not-match control, without which a search that answered
"repository root" to everything would satisfy all nineteen.** A repaired module
copied to a temporary directory with no marker above it **raises
`RuntimeError: cannot locate scripts/lab_paths.py above /tmp/.../probe.py;
refusing to guess a repository root`** instead of returning a path. That is
`b0ab070d`'s rule — a root that is not there blinds the caller, it never passes
it.

### 6.2 A batch-5 residue found inside one of the nineteen

`RULE_O_DENOMINATOR_MEASUREMENT_2026-08-15.py:70` reads
`REPO / "demo-output" / "website" / "closure_challenge_round5_qcr.json"`. **R16/R17
moved every loose webroot `*.json` to `research/closure/data/` in batch 5**, so
that literal has been dangling since, and this measurement has been reading a
file that is not there. It is repaired to
`lab_paths.web_file("closure_challenge_round5_qcr.json")` — which now returns
`research/closure/data/closure_challenge_round5_qcr.json`, verified to exist —
because the repair of the line above it cannot be proved by execution while the
line below it raises.

---

## 7. THE LISTS AND THE GENERATORS, CHECKED BEFORE THE COMMIT

Batch 5 found a record-root list that would have dropped 19 documents; batch 6
found a generator about to write a served page into a data directory and a
waiver register that would have reported 137 paths twice. Every root list,
sweep root, corpus definition and generator whose output lands in a batch-7
destination was enumerated and **executed or read at the constant**.

### 7.1 `exec_bits.OWNERS` — 61 waived paths routed to UNASSIGNED

**Measured before the move: 61 of the 255 waived paths are under a batch-7
source** — 59 R20, 2 R21 — and every one of them routed to **UNASSIGNED** at its
successor, which
`test_the_register_is_split_across_families_and_says_so` asserts cannot happen.
This is exactly the row batch 4 added for `ops/` and batch 6 added for `cases/`.

Three rows added — `verification/campaign/` and `verification/runs/` → **Cases**,
`verification/` → **Demo and website**. **The family assignment is preserved,
not re-decided**: all 61 were "Cases" under `demo-output/website/campaign/` and
are "Cases" now, measured both ways. The catch-all answers for R24's three
directories, which were "Demo and website" under `demo-output/website/`, and for
0 register entries today. After the repair `audit()` reports **`stale_waivers`
0** and the register matches at both spellings — batch 6's `_spellings()` does
the rest, and it needed no change.

### 7.2 `RECORD_ROOTS()` — 374 records before, 374 after, and the SET is identical

`lab_paths.RECORD_ROOT_NAMES` already carries `CAMPAIGN`, `RUNS`,
`CERTIFICATES`, `CREDIBILITY` and `MONITOR`, so the batch-7 destinations were
bound before this batch ran. Proved rather than assumed: `_record_documents()`
returns **374 documents before and 374 after**, and the before-set mapped
forward through `redirect()` is **set-identical to the after-set — 0 lost, 0
gained**. The root tuple gains five entries and `demo-output/website` stays,
because X3 and the served set are still under it.

### 7.3 The generators, at their constants

| generator | writes into | at the constant | verdict |
|---|---|---|---|
| `scripts/morning_report.py:290` | `verification/campaign/reports/` | `lab_paths.CAMPAIGN / "reports"` | **follows** |
| `sdk/scripts/model_form_batch.py:80-82` | `verification/runs/MODEL_FORM_runs/`, `verification/campaign/` | `lab_paths.RUNS`, `lab_paths.CAMPAIGN` | **follows** |
| `sdk/scripts/build_certificate_compare.py:41` | `verification/certificates/` | `lab_paths.CERTIFICATES` | **follows** |
| `sdk/scripts/build_credibility_record.py:63` | `verification/credibility/` | `lab_paths.CREDIBILITY` | **follows** |
| `sdk/scripts/replay_s12_unsettled_stop.py:148`, `replay_monitor_rules.py:206`, `score_s6_partition.py:51` | `verification/monitor/` | `lab_paths.MONITOR` | **follows** |
| `scripts/self_audit.py:4450`, `check_verdict_cells.py:75`, `mint_retrospective_certificates.py:58`, `check_belief_neutrality.py:253`, `citation_tier_audit.py:374`, `cbfs_bentaleb_forensics.py:209`, `shock_bench.py:36-37` | batch-7 destinations | `lab_paths.RUNS` / `.CAMPAIGN` | **follows** |
| **`cases/dafoam/f6d_random_matrix_uq/make_campaign_json.py:7`** | `verification/campaign/F6d_random_matrix_uq.json` | **`HERE.parents[1] / "campaign"`** | **repaired** |
| **`sdk/scripts/model_form_batch.py:231`** | reads `verification/runs/F6b_runs/medium` | **a `REPO_ROOT / "demo-output" / ...` literal** | **repaired** |
| `scripts/check_convergence_validate.py:118` | reads `verification/runs/F8_runs/...` | `_located()` → `lab_paths.resolve()` | **follows**, batch 6's repair |
| `sdk/tests/test_log_signatures.py:515` `ArchiveSweepTests._roots()` | sweeps `verification/` | already lists it | **follows**, batch 6's repair |
| `scripts/phase2_move_map.py` | — | **SUPERSEDED**, refuses to run without an override | inspected |
| `scripts/check_pdf_surfaces.py:168` `KNOWN_CLASS_INSTANCES` | — | dated register, keys compared as **strings**, never stat'd | inspected, no repair |
| `sdk/scripts/closure_round5_qcr_forward.py:167` | — | a provenance string naming a path **at a commit** | inspected, left |

**`make_campaign_json.py` is this batch's `build_wall.py`, and it was already
broken before batch 7 touched anything.** It reaches the campaign root by
counting two segments up from itself. **Batch 6 (R22) moved it** from
`demo-output/website/dafoam/f6d_random_matrix_uq/` to
`cases/dafoam/f6d_random_matrix_uq/`, at which point `parents[1] / "campaign"`
became `cases/campaign` — a directory that does not exist — and its final line,
`(CAMP / "F6d_random_matrix_uq.json").write_text(...)`, has been writing into
nothing since. It is a **generator whose output lands in a batch-7 destination**,
which is the only reason it was in this batch's frame at all; it now reads
`lab_paths.CAMPAIGN`. **This is the same defect class as the nineteen, one
batch late, and it is reported as batch 6's residue rather than as batch 7's
finding.**

`model_form_batch.py:1115` and `:1144` are the same story:
`REPO_ROOT / "demo-output" / "website" / "dafoam" / ...` in two
`sys.path.insert` calls, dangling since batch 6. Repaired to
`lab_paths.DAFOAM` while the file was open for its batch-7 literal, and named
here as batch-6 residue.

### 7.4 A test that would have passed while asserting nothing

`sdk/tests/test_rank_claim_surfaces.py:1109`,
`test_the_real_corpus_instances_stay_clean`, loops over two path literals and
**`continue`s when a path does not exist**. R21 moves the first of them, after
which the loop skips both real instances and the test passes having read
nothing — the silent-zero failure this corpus records repeatedly. The names now
follow the map, **and a floor was added** —
`assertEqual(2, checked, "both real-corpus instances must be read")` — so a
corpus that shrank reddens instead of going quiet. The floor passes.

`_held_out` at `:1738` and `:2451` carried the same literal but already asserted
`path.exists()` with the message *"without it this test asserts nothing"*; those
would have failed loudly. Both now read `lab_paths.CAMPAIGN`.

### 7.5 FIVE INSTRUMENTS CHANGED VERDICT OR COUNT AS A SIDE EFFECT, AND EACH WAS REPAIRED TO FOLLOW THE MAP RATHER THAN ADJUSTED

Each was found by RUNNING the gates, not by reading them, and for each the test
of whether the change was a repair or a loosening is the same: **does it restore
the pre-move answer?** All five do, and the numbers are given so the claim is
checkable.

**(a) `scripts/check_verdict_cells.py` went PASS -> FAIL, with two
`CELL-VS-RECORD` findings that were artefacts of the move.** `_landed(p)` asks
`git log --diff-filter=A -- <path>` for the commit that ADDED a grade record.
In the window between the `git mv` and the commit the new path has no history at
all, so `_landed` returned **0** for all 264 campaign records and every record
read as newer than every other; after the commit `git log` would find the MOVE
and report today as the landing date of a record dated 2026-08-11, because
without `--follow` a rename IS an add at the new path. **This is D356 arriving
through a different door** -- that repair exists because `git log -1` reported
the last EDIT rather than the landing, and its rule is *"repairing a record must
not re-date it"*. A MOVE must not re-date it either. Repaired with
`_history_spellings()`, which asks every name the repository has had or will
have for the path and takes the **earliest** add -- the same rule the docstring
already stated for a path added more than once, and the same shape as
`exec_bits._spellings`. After: **exit 0, 16 rung rows read, 0 FAIL, 3 WARN, 0
QUERY**, and its own `--selftest` reports **12/12 controls correct** with the
landing control **HELD** rather than SKIP: `add=1786822451 last=1786995260
_landed=1786822451`.

**(b) `scripts/self_audit.py:3603` `_ranking_board_date()`** returned `''` for
`BOARD_MOVED_2026-08-11.md` at its new spelling and printed *"(date
unreadable)"* into the published-board provenance -- in a function whose own
docstring says *"the one thing a referent that exists to be current must not do
is misreport its own age"*. Same repair, same rule. After: **2026-08-11**.

**(c) `scripts/self_audit.py` `_tracked_files()` SHRANK THE SWEPT CORPUS BY
2,367 SURFACES WITHOUT A WORD, and this is the one that would have been missed.**
It read `git ls-files` -- the INDEX -- and every caller then does
`if not path.is_file(): continue`. The shared index still lists the pre-move
paths and this lab's private-index protocol never writes it, so 2,367 surfaces
were named at locations the tree no longer uses and were **dropped in silence**.
Measured across the move with the old frame:

```
placement words agree with the published board   80 -> 45 lab record placements
rank claims carry the right values               35 -> 14 more on lab records
```

**Both counts FELL, and a count that falls is a blinded instrument, not a
repair.** Neither moved a verdict, so a verdict-list comparison could not see it
-- which is batch 5's *"46 tests behind one `skipped` line"* in a third
instrument. Repaired to `git ls-tree -r HEAD` (D274's ruled frame, the repair
`scripts/lab_check.py:486-496` already made for `tracked_frame`) **and** resolved
through `lab_paths.resolve()`, so the sweep follows the map in the window between
a `git mv` and its commit as well as after it. Proved by execution: the two
counts return to **80** and **35** exactly, and the frame reads 8,275 tracked
paths of which 8,265 are on disk -- the ten absent ones being another lane's
in-flight deletions, present in HEAD and not in the worktree.

**(d) and (e) Two blinding tests stopped blinding, and one frame test asked git
the wrong question.** `test_empty_set_is_not_agreement.py`'s
`_ABSENT_SOURCE_CASES` rebinds `self_audit`'s handles to an empty directory and
asserts UNKNOWN: a check that cannot be blinded cannot be shown to refuse an
empty sweep. `check_ungated_completed_runs` was listed as blindable by `WEB`
alone; R21 takes its one record out of the webroot, `_at()`'s WEB re-rooting
stops applying, and the check went on reading the real ladder and returned WARN
where a blinded check must return UNKNOWN. **`REPO` added -- the third instance
of the sentence batch 5 wrote beside the two entries above it.**
`test_form_or_value_and_empty_selection.py`'s empty-SELECTION arm planted its
ladder record at `<web>/campaign/`; the plant location is now DERIVED from
`lab_paths.CAMPAIGN` so it needs no edit at any future batch.
`test_two_board_referents.py:152` asked `git ls-files` whether the ranking
record is tracked -- (c)'s frame defect in a test -- and now asks
`git ls-tree -r HEAD` under every spelling, which leaves the assertion exactly
as strong: a record tracked under NO name still fails it. **All three fail
LOUDLY rather than quietly, which is the good direction and is what these files
exist for.** After the repairs the three modules read **84 passed, 99 subtests
passed**, against 82 passed / 3 failed / 98 subtests before.


---

## 8. THE GATES, BOTH SIDES, WITH THEIR FINDING SETS

### 8.1 `scripts/lab_check.py`

| | before, at `aebbcac8` | after |
|---|---|---|
| `--no-tests` | **FAIL, exit 1, ran 20/20**, 306.4 s, stderr empty | **FAIL, exit 1, ran 20/20**, 289.4 s, stderr empty |
| full | **FAIL, exit 1, ran 21/21**, 1,508.9 s, stderr empty | **FAIL, exit 1, ran 21/21**, 1,504.4 s, stderr empty |
| pytest | **6 failed / 2,447 collected / 0 skipped**, 92 files enumerated and collected | **7 failed / 2,447 collected / 0 skipped**, 92 files enumerated and collected |

**The `--no-tests` verdict list is BYTE-IDENTICAL between the two frames**,
compared as sorted verdict lists by `diff` rather than by eye: the same six
FAILs (`check_pdf_surfaces`, `check_proposal_surface_coverage`,
`check_rung_attribution`, `contention_audit`, `installed_registry`,
`self_audit`), the same `BLOCKING UNKNOWN scripts/check_absolutes.py: exit 3`,
the same 15 unrun. The full run's list is identical to it plus the pytest row
and reports 14 unrun on both sides.

**`self_audit`'s own fifteen-line finding block is identical line for line,
tier for tier and NUMBER for number, with exactly one exception**, and the
exception is the one this batch is expected to move:

```
- [FAIL] cited evidence paths      339 of 1871  ->  436 of 1872
```

Everything else -- `rank claims carry the right values` at 4 travelling and 35
lab-record, `placement words` at 80 lab-record, `campaign json citations` at
6 of 7, `bundle drift` at 9 behind the tree, all eleven WARNs -- is unmoved.
Section 7.5(c) is why that took a repair rather than luck: with the old frame
the middle two of those read 14 and 45.

`scripts/check_verdict_cells.py` is **PASS on both sides** (§7.5(a)) and
`scripts/check_convergence_validate.py` reads **PASS, 13 of 13 known answers**
on both sides, batch 6's `_located()` needing no change.

### 8.1a THE SEVENTH PYTEST FAILURE IS A PRE-COMMIT-WINDOW ARTEFACT, AND IT RETIRES AT THIS COMMIT BY ITS OWN CLAUSE

`sdk/tests/test_hand_carry.py::TheBatch2GateOnTheLiveTree::test_the_live_gate_reads_one_when_the_exclusion_is_dropped`
is batch 2's option-A/option-B two-way control on `MESH_AUDIT_runs`. Its class
carries this `setUp`:

```python
if not any(p.startswith(self.tree + "/") for p in self.tracked):
    self.skipTest(f"{self.tree} holds no tracked file at HEAD: batch 2 "
                  "or batch 7 has since run and this plant is spent")
```

`self.tracked` is `git ls-tree -r HEAD`. In the window between the `git mv` and
this commit, **HEAD still says the 78 files are tracked at the old path while
the worktree has already moved them**, so the guard does not fire and the
projection -- which walks the worktree -- correctly reports nothing where the
test expects `demo-output/website/campaign/MESH_AUDIT_runs`.

**It was NOT adjusted.** The plant is spent by design, and it retires the moment
HEAD agrees with the worktree: this commit's own tree contains **no path under
`demo-output/website/campaign/MESH_AUDIT_runs/`** -- asserted before
`update-ref` as part of the D set, which is exactly the 2,367 sources -- so
after it lands the `setUp` skips and BOTH tests in that class leave the suite.

**That is 2 tests behind a `skipped` line, and it is named here rather than
absorbed**, because batch 5 lost 46 tests behind one such line while its
failing-module list got *shorter*. The two are
`test_the_live_gate_reads_zero_under_the_ruled_option` (passing) and
`test_the_live_gate_reads_one_when_the_exclusion_is_dropped` (failing in the
window). The landed state is therefore **6 failed / 2,447 collected / 2
skipped**, and the six are the standing baseline: `test_exec_bits` 1,
`test_fail_open_scan` 1, `test_installed_matches_tracked` 3,
`test_pdf_surfaces` 1 -- the same four modules with the same per-module counts
as before this batch.

**Collected is 2,447 on both sides and `skipped` is 0 on both sides of the
measured frames**, with 92 files enumerated and 92 collected on both. Nothing
left the suite: batch 7 moves nothing into or out of `scripts/` or
`sdk/tests/`, so the candidate universe does not move at all, and the three
tests §7.5(d,e) repaired are the same tests before and after -- the module
totals 33, 39 and 12 are unchanged.

### 8.2 The three standing gates

| gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B**, digests `1b53ed5a4e9d63cb` / `5519de4237b71ce4`, `walk_errors = 0` | **2 / 307 / 1,510,309,145, byte-identical**, same digests |
| **G1** rides-along | 2,212 / 24,003 / 7,743,986,953 | 781 / 7,868 / 1,793,047,491 — the batch-7 delta, §4.2 |
| **G1** goes-dark-after-batch-2 | **0** | **0** |
| **G2** control corpora | **223 path fields, 0 unresolved** | **223, 0** |
| **G3** root binding | `roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (EVIDENCE,)` | `roots OK`, **`AMBIGUOUS = (CAMPAIGN, RUNS)`**, `UNRESOLVED = (EVIDENCE,)` |

**No gate was adjusted.**

**G3's `AMBIGUOUS` moved and it is CORRECT, not a defect.** `CAMPAIGN` and
`RUNS` both report `state() == "both"` because
`demo-output/website/campaign/` still exists and holds exactly one file: the
served PNG `duct_secondary_flow_AR_7_validation_qcr.png`, which is **R13 and
therefore batch 8's**, deliberately left behind so `closure.html:350` keeps
reaching it relatively. The region genuinely is on both sides until batch 8
runs, and `_bind()` prefers the successor, so every consumer reads
`verification/`. This is reported rather than repaired: making `AMBIGUOUS` empty
would mean moving a file batch 8 owns.

**G2 was fired ten ways**, because a count alone cannot show a corpus still
discriminates:

| arm | citation | resolves to |
|---|---|---|
| 1 must resolve, unmoved | `demo-output/website/closure.html` | itself |
| 2 **must NOT resolve** | `demo-output/website/never_existed.md` | `None` |
| 3 batch-4 successor | `demo-output/plots/C_d/frame_0001.png` | `media/plots/…` |
| 4 batch-5 successor | `demo-output/website/agenda/docket.json` | `research/agenda/…` |
| 5 batch-6 successor | `…/dafoam/ADJOINT_MEMORY_ENVELOPE.md` | `cases/dafoam/…` |
| 6 **this batch, R20** | `…/campaign/F3_runs` | `verification/runs/F3_runs` |
| 7 **this batch, R21** | `…/campaign/CAMPAIGN_STATUS.md` | `verification/campaign/…` |
| 8 **this batch, R24** | `…/certificates/README.md` | `verification/certificates/…` |
| 9 **this batch, the file that must NOT move** | `…/campaign/duct_secondary_flow_AR_7_validation_qcr.png` | **itself** |
| 10 the webroot still resolves | `…/wall/wall.html` | itself |

Arms 6/7 and 9 together are the R20/R21 split as a live two-way control, and
arm 9 is the one that reddens if a mover "tidies" the served PNG out of
`campaign/` ahead of batch 8. **The left-hand spelling in arms 3-8 is the
pre-move one and is withdrawn — do not cite it.**

---

## 9. THE CITATION GUARD — 436 of 1,872, and 428 of them are the guard failing to follow a rename

Measured with the guard's own regexes, roots and retraction pattern, over the
same 374 records, before and after:

| | before | after |
|---|---:|---:|
| repo-rooted citations | 1,871 | **1,872** |
| not resolving at the LITERAL path | **339** | **436** |
| …of those, resolving at the SUCCESSOR via `lab_paths.resolve()` | 331 | **428** |
| …**genuinely nowhere** | **8** | **8** |

**The last row did not move, and the eight rows are the same eight documents at
their new spellings** — seven of them now read at `verification/campaign/…`,
one at `cases/dafoam/…`. Nothing became uncited and nothing was edited: every
record here is append-only.

**The trajectory: 12 → 197 → 333 → 436**, and it is dominated by the instrument
rather than by the corpus — **428 of 436 resolve at their successor the moment
batch 9's resolver lands**. Batch 6 handed over 333 of 1,830 with 5 nowhere;
peers had moved that to 339 of 1,871 with 8 nowhere before this batch ran, and
this batch adds 97, all of them followable renames.

**The resolver was NOT built here.** It is batch 9 and it is specified with a
two-way planted control — *"a citation that must resolve and one that must
not"* — and a resolver landed without that control is the shape of a guard that
has stopped discriminating. What batch 7 adds to the case for batch 9 is 97
more rows and the observation that **1,554 R25 files are still to come**.

---

## 10. WHAT WAS NOT DONE

### 10.1 `_SHIPPING_RE` is not re-pointed, and `check_absolutes.py` is byte-identical to HEAD

`MOVE_MAP_EXECUTION_2026-08-17.md` §5 Class 2 requires
`scripts/check_absolutes.py`'s `_SHIPPING_RE` to gain its `web/` alternative
**in the commit that creates `web/` and not before**. **Batch 7 does not create
`web/`** — R13 is batch 8 — and `ls web` returns *no such file or directory*
after this batch as before it. **Confirmed by `cmp` against
`git show HEAD:scripts/check_absolutes.py` rather than assumed: the whole file
is byte-identical to HEAD's blob.** `git rev-parse HEAD:scripts/check_absolutes.py` and
`git hash-object scripts/check_absolutes.py` both return
`9b0fce64ed2ae84338f291aafab2294e73e561f5`, and the pattern still reads
`^(?:demo-output/website/|.*/latex/|.*\.tex$)` at `:743`.

### 10.2 The rest

The hand-carry was not run (§4.2). `lab_paths.py` was not edited. No citation
inside any append-only record was edited. `docs/LOCATIONS.md` is still owed and
is now five roots behind. The crontab was neither read back nor edited: batch 7
moves nothing it names. The shared index was not written — it is now **2,367
entries stale by construction**, and the surgical
`git update-index --force-remove --stdin` over only this agent's paths is filed
as owed. No solver was launched and nothing was registered.

---

## 11. WHAT BREAKS IF BATCH 8 NEVER RUNS

**Nothing breaks, and `verification/` is complete for R20, R21 and R24.**

1. **The four served pages still answer over HTTP at their current paths.**
   Batch 8 is R13 and it is the only batch that can take a live surface down;
   this one does not touch `demo-output/website/{closure,benchmarks,shoot}.html`
   or `wall/wall.html`.
2. **`demo-output/website/campaign/` still exists and holds exactly one file**,
   the served PNG `closure.html:350` reaches relatively. That is why
   `AMBIGUOUS` is `(CAMPAIGN, RUNS)` (§8.2), and it is the correct state, not a
   residue.
3. **`_SHIPPING_RE` stays queued** and stays byte-identical (§10.1). Adding the
   `web/` alternative now would be a rule matching nothing.
4. **`check_evidence_paths_exist` is already blind and batch 8 does not make it
   blinder.** 436 of 1,872 citations do not resolve at their literal path today;
   428 of them resolve at their successor. Batch 9 is what fixes that, and §9
   says why it must carry its own control.
5. **R25's 1,554 files are the outstanding half of this batch**, not of batch 8,
   and §2.3 is what they need.

**What becomes more expensive if R25 waits.** It grew 315 → 1,554 tracked files
in one day and 40 in the 45 minutes this pass took. Every hour it waits, the
lane that owns it writes more into it, and the fourteen `.gitignore` rules that
describe it have to be re-pointed around more live content.

---

## 12. METHOD

- Every path-derived count is over `git ls-tree -r -z --name-only`, at a named
  commit, **never `git ls-files`**. The shared index was not read for any
  measurement and not written by any step. `git status` and `git diff HEAD` were
  not used for anything, and **git's rename inference is never quoted here**.
- **stderr was captured on every walk, every `git` invocation and every
  subprocess**, including all 294 `git mv` calls, which were checked for a
  non-empty **stdout** as well as a non-empty stderr and a non-zero exit.
- **No count was piped into `head`.**
- Path comparisons are **Python set comparisons plus a byte total**, with a
  sha256 of the sorted relative-path set as a **third witness** — never a digest
  alone.
- `hand_carry.measure()` **raises** on any walk or stat failure; all 66
  directory measurements reported `walk_errors = 0`.
- The **inverse `mv` list was written before the batch started**, 294 lines plus
  the `rmdir`, reverse order. It is an `mv` list and not `git reset --hard`:
  a reset restores the 2,367 tracked files and leaves 17,312 untracked,
  gitignored ones (6.21 GB in dark trees) in the new directories, where
  `git status` will not show them and `git clean` would delete them.
- The sources were **re-measured immediately before the move** against the
  opening snapshot, with an abort on any drift. **Drift fired once** — peer
  commit `f6c799fa` modified `campaign/NINE_ACT_GATE_TABLE.md` — the batch
  stopped, the snapshot was re-taken at `fccedd3a`, and the second drift check
  read **0 of 294**.
- The ownership precondition was re-run rather than inherited:
  `find . -path ./.git -prune -o ! -user ubuntu -print` returns **0 files
  repo-wide, stderr empty**.
- **Every file this batch edits was `cmp`'d against `git show HEAD:<path>`
  immediately before the commit was built**, because batch 6 §9.1 had an
  uncommitted `.gitignore` edit replaced by a peer lane with no error and no
  signal. **29 edited files, checked against HEAD's blob at the moment the commit was
  built: 29 identical to HEAD-plus-this-batch, 0 re-applied.** The detector is
  not `cmp worktree HEAD` -- they are SUPPOSED to differ -- it is: take HEAD's
  blob, apply this batch's edit list to it, and compare with the worktree. That
  distinguishes "my edit is still there" from "a peer replaced the file", and
  the repair for the second is to write HEAD's current content with this
  batch's edits on top, which preserves the peer's change instead of
  overwriting it. Peer commits landing on a batch-7 SOURCE between the move and
  the commit are checked separately, by comparing the source blobs at the move
  anchor and at the commit's parent.
- Every `.gitignore`, module and test edit is an exact-string replacement with
  an expected count, applied by a script that **writes nothing at all unless
  every entry matches**, and compiles every rewritten Python source before
  keeping it. A snippet that drifted is a stop, not a half-applied batch — and
  that is what makes the edits re-appliable on top of a peer's newer content.
- **The after-gates were run THREE times and the reported frame is the last
  one**, because each run found an instrument that had stopped following the
  map and each repair invalidated the frame that found it (§7.5). The
  intermediate readings are not hidden: the first after-run read 20/20 with
  `check_verdict_cells` FAIL, the second read 10 pytest failures, and the third
  -- with every repair in -- reads the byte-identical check list and 7 pytest
  failures, of which the seventh is §8.1a's window artefact. **No gate was
  loosened to reach that**: every repair is pinned by restoring a number
  measured before the move (0 FAIL / 3 WARN, 12/12 controls, 80, 35, 84 passed).
- This record does not appear in its own results: every measurement was taken
  before the commit that lands it, and the after-suite ran before this file
  existed.
