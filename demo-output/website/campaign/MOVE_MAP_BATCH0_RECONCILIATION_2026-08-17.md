# MOVE_MAP batch 0 — every rule count re-derived over HEAD, and the one path that does not classify

**Nothing was moved, renamed, copied, deleted or untracked. `.gitignore` was not
edited. `git mv` was not invoked. The shared index was not touched — no
`git add`, no `git read-tree` against it.** Batch 0 is measurement. It moves
nothing on purpose: three agents are writing this tree while it is measured, and
13,000 renames through a tree being rewritten is how work is lost.

**Anchor: `fc9301c5`**, and every count below is over
`git ls-tree -r -z --name-only fc9301c5`. Never `git ls-files`. Never a
filesystem walk, except where one is unavoidable (§3) and then it is declared.

**HEAD moved during the measurement**, from `fc9301c5` to `3f46e4e9`, and the
drift was measured rather than assumed: `comm` over the two path snapshots
returns **0 paths added and 0 removed** — `3f46e4e9` is a content-only edit — so
**the whole table below holds unchanged at both anchors**, 14,293 paths at each.
That is a property of this window, not a guarantee; the frame is named so the
next reader can re-take it.

---

## 1. The frame, re-measured — the gap is now 479 and it grew while nobody edited it

`MOVE_MAP_2026-08-16.md` §2 states its totals *"reconcile to
`git ls-files | wc -l` exactly"*. `git ls-files` lists **index** entries, and
`docs/USING_THIS_LAB.md` §8.5's mandated commit form builds a tree under
`GIT_INDEX_FILE` and never writes the shared index. Every file a conforming
agent lands is therefore in HEAD and absent from `git ls-files` until somebody
runs `git add` or `git reset`, which under a live fleet nobody does. §8.7 records
the same defect from the specimen's side.

Measured at `fc9301c5`:

```
git ls-files                          | wc -l   ->  13,814
git ls-tree -r --name-only fc9301c5   | wc -l   ->  14,293
comm -13   (in HEAD, absent from the index)     ->     479
comm -23   (in the index, absent from HEAD)     ->       0
```

Both snapshots were taken with `-z` and checked for duplicates (14,293 lines,
14,293 unique; 13,814 and 13,814). `stderr` was captured on both walks and was
empty.

**The asymmetry is the whole finding.** Nothing is staged that HEAD lacks, so all
479 are landed work the index has not caught up with. The gap was **160** at
`f40f6ef5` this morning and **477** at a later reading; it is **479** now. It
does not shrink on its own and only a `git add`/`git reset` nobody is going to
run would close it.

**479 files is 3.35% of the tracked corpus, and it is not distributed evenly.**
It is concentrated in exactly the places a mover cares about:

| Rule | HEAD-only files | What they are |
|---|---:|---|
| R7 `docs/**` | **360** | 344 of them an OpenFOAM case corpus under `docs/campaigns/F14-cooling-ladder/`; 15 papers; 1 build note |
| R20 campaign run archives | **102** | 97 `THERMAL_K0_runs`, 5 `F4_runs` |
| R21 campaign records | 7 | today's ladder grades, `MOVE_MAP_EXECUTION_2026-08-17.md` itself |
| R9 `scripts/**` | 5 | `lab_paths.py`, `hand_carry.py`, `heat_balance.py`, `check_verdict_cells.py`, `mutation_harness_known_test_names.py` |
| R3 `sdk/**` | 3 | the two new test modules and `rans_identity_baseline.py` |
| R22 `dafoam` | 1 | |
| **no rule at all** | **1** | `AWS_TREE_PLAN.md` — §2.3 |

---

## 2. The re-derived rule table

Classified over the `fc9301c5` snapshot by an anchored-regex classifier that
assigns every path to exactly one rule. "old" is the map's own figure at
`371be610` over the index frame of 20,762.

| Rule | Scope | old (`371be610`, index) | **new (`fc9301c5`, HEAD)** | Δ |
|---|---|---:|---:|---:|
| **R0** | root keeps | 3 | **3** | 0 |
| **R1** | `LESSONS.md`, `LOCATIONS.md` → `docs/` | 2 | **2** | 0 |
| **R2** | `FILMING_COMMANDS.md`, `LAPTOP_SHOOT.md` → `media/` | 2 | **2** | 0 |
| **R3** | `sdk/**` — unchanged | 327 | **330** | **+3** |
| **R4** | `models/**` — unchanged | 202 | **202** | 0 |
| **R5** | `demo-surfaces/**` → `cases/` | 6 | **6** | 0 |
| **R6** | `docs/aws/**` → `ops/aws/**` | 1 | **1** | 0 |
| **R7** | `docs/**` except `docs/aws/` — unchanged | 137 | **497** | **+360** |
| **R8** | `scripts/{installed,laptop_bundle}/**` + launchers → `ops/**` | 26 | **26** | 0 |
| **R9** | `scripts/**` — the apparatus that stays | 52 | **57** | **+5** |
| **R10** | `demo-output/{acts,gui-proof,fallbacks}/**` → `media/**` | 77 | **77** | 0 |
| **R11** | `demo-output/plots/**` → `media/plots/**` | 752 | **752** | 0 |
| **R12** | 10 loose `demo-output/*.png` → `media/` | 10 | **10** | 0 |
| **R13** | the served set → `web/` | 5 | **5** | 0 |
| **R14** | `benchmarks.json` → `research/closure/data/` | 1 | **1** | 0 |
| **R15** | `benchmarks.png` → `research/closure/plots/` | 1 | **1** | 0 |
| **R16** | 19 loose `website/*.md` → `research/closure/md/` | 19 | **19** | 0 |
| **R17** | 21 loose `website/*.json` → `research/closure/data/` | 21 | **21** | 0 |
| **R18** | `wall/wall.json` → `research/closure/data/` | 1 | **1** | 0 |
| **R19** | `website/paraview/**` → `ops/paraview/**` | 1 | **1** | 0 |
| **R20** | campaign `*_{runs,work}/**` → `verification/runs/**` | 7,940 | **8,042** | **+102** |
| **R21** | campaign records → `verification/campaign/**` | 269 | **278** | **+9** |
| **R22** | 10 physics families → `cases/<family>/**` | 3,547 | **3,548** | **+1** |
| **R23** | 11 research topics → `research/<topic>/**` | 394 | **394** | 0 |
| **R24** | `{certificates,credibility,monitor}/**` → `verification/**` | 7 | **7** | 0 |
| **U1** | the two root wheels | 2 | **0** | **−2** |
| **U2** | `mbc_retry*.{err,log}` | ~~12~~ **10** | **0** | **−10** |
| **U3** | campaign output already ignore-matched | 5,802 | **0** | **−5,802** |
| **U4** | case/research output already ignore-matched | 1,136 | **0** | **−1,136** |
| **KEEP** | `uq_batch.{err,log}` — miscounted into U2 | (0) | **2** | **+2** |
| **X1** | `dist/certonomous-demo.zip` | 1 | **1** | 0 |
| **X2** | `Stl_files/naca4412_wing.stl` | 1 | **1** | 0 |
| **X3** | `latex/**` + `motorbike-video/**` | 5 | **5** | 0 |
| | **unclassified** | 0 | **1** | **+1** |

The four U rows falling to zero is **batch 1, which landed**: 6,950 paths left
tracking, all of them U-rule, none of them R-rule. It is not drift.

**R22 and R23 breakdowns at HEAD.** R22: `dafoam` 3,269, `tmr` family 138
(108 + 13 + 12 + 5), `committee-grids` 105, `hlpw6` 12, `mega-batch` 9,
`unsteady-cylinder` 8, `valve` 7 — total 3,548, the map's 3,547 plus one dafoam
file. R23: `race` family 186 (179 + 6 + 1), `agenda` 139, `closure_*` 53
(24 + 9 + 9 + 11), `optimization` 8, `uq` 8 (5 + 3) — total 394, unmoved.

### 2.1 The batch sizes the plan quotes, re-derived

| Batch | plan's figure | at HEAD | Δ |
|---|---:|---:|---:|
| 4 — `media/`, `ops/`, `docs/` (R10 R11 R12 R2 R6 R8 R19 R1) | 871 | **871** | 0 |
| 5 — research (R14–R18, R23) | 437 | **437** | 0 |
| 6 — cases (R5, R22) | 3,553 | **3,554** | +1 |
| 7 — verification (R20, R21, R24) | 8,216 | **8,327** | **+111** |
| 8 — the webroot cut (R13) | 5 | **5** | 0 |

**Batch 7 is 111 files larger than the plan says**, and 102 of those 111 are the
`THERMAL_K0_runs` and `F4_runs` files that the index frame cannot see at all.

### 2.2 R8/R9 — a boundary the map records by count and by no membership

R8 is stated as *"`scripts/{installed,laptop_bundle}/**` + 15 named launchers →
`ops/**`, 26"*. **The 15 names are enumerated in no committed artefact.**
`git grep` over `*.py *.md *.sh` finds the phrase and no list; `phase2_move_map.py`
is F1's superseded generator and carries a different target tree.

This matters because **R8 is in the move bucket and R9 is in the keep bucket**, so
the boundary between them is the boundary between two of the four top-level
reconciliation buckets — and the identity closes for *any* placement of it,
because only the sum `R8 + R9 = scripts/**` is fixed. An independent
reconstruction here first produced 27/56, which reconciled to exactly the same
total and was only caught because the keep subtotal 723 is separately recorded.
Reconstructed as `installed/` (7) + `laptop_bundle/` (4) + the 12 shell
launchers/keepalives/preflight + `installed_registry.py` + `memwatch.py` +
`ledger_backup.py` = **26**, which reproduces both R8 = 26 and R9 = 52 at the
index frame. That is a reconstruction that fits, not the map's own list, and it
is recorded as such. Recorded as **L-94**.

The delta lands wholly on R9: none of the five new `scripts/` files is a
launcher, a keepalive or a preflight — all five are check/audit apparatus, which
is what R9 keeps.

### 2.3 The one path that does not classify — `AWS_TREE_PLAN.md`

```
AWS_TREE_PLAN.md      root-level, tracked at HEAD, absent from the index,
                      landed at d07ef7f7 today
```

R0's keep list is closed and named — `README.md`, `.gitignore`,
`.gitattributes`. R1 moves the two root records that existed at `371be610`
(`LESSONS.md`, `LOCATIONS.md`) into `docs/`. `AWS_TREE_PLAN.md` is a third root
record of the same class, written after the map, and **no rule in the map reaches
it**. Under the target tree of §1 a loose root record belongs in `/docs/`, which
is R1's own destination, but that is a decision and it is not this batch's to
take. **It is named here so that it is a decision and not an omission**: left
unruled it is a file the mover walks past, and §1's target tree has no root
markdown but `README.md`.

---

## 3. The reconciliation, in the HEAD frame

**The `uq_batch` correction is verified, by execution and by exit code.**
`docs/USING_THIS_LAB.md` §8.6's rule was applied — `--no-index`, because
`git check-ignore` is silent about tracked paths, and gate on the exit code, not
on the printed rule:

```
git check-ignore --no-index -q uq_batch.err   -> exit 1   NOT ignored
git check-ignore --no-index -q uq_batch.log   -> exit 1   NOT ignored
git check-ignore --no-index -q mbc_retry7.log -> exit 0   ignored   (.gitignore:101)
git check-ignore --no-index -q scipy-1.2.3-cp312.whl -> exit 0   ignored
```

The last two files do not exist on disk, which is what shows the U1 and U2
patterns are doing the work rather than matching today's filenames.
`.gitignore:112-113` carries `!/uq_batch.err` and `!/uq_batch.log` under a
comment that says *"They stay tracked"* in as many words. **The map's U2 count of
12 is wrong; it is 10, and the two `uq_batch` files belong in the keep bucket.**
The correction stands, and it is re-verified here rather than carried.

**The identity at the index frame, re-derived, reproduces the correction exactly:**

```
    723   keep in place   R0(3) R3(327) R4(202) R7(137) R9(52) + uq_batch(2)
 13,084   move
      7   exceptions      X1(1) X2(1) X3(5)
      0   unclassified
 ------
 13,814   =  git ls-files | wc -l          <-- and this frame is 479 short of HEAD
```

**The identity at HEAD — the frame that is not a scratch state:**

```
  1,091   keep in place   R0(3) R3(330) R4(202) R7(497) R9(57) + uq_batch(2)
 13,194   move            R20(8,042) R21(278) R22(3,548) R23(394) R11(752)
                          R10(77) R8(26) R16(19) R17(21) R12(10) R24(7)
                          R5(6) R13(5) R1(2) R2(2) R6(1) R14(1) R15(1)
                          R18(1) R19(1)
      7   exceptions      X1(1) X2(1) X3(5)
      1   UNCLASSIFIED    AWS_TREE_PLAN.md
 ------
 14,293   =  git ls-tree -r --name-only fc9301c5 | wc -l
```

**It does not close with zero unclassified, and the one path that fails is named
above.** It closes with one, and that one is a real gap in the rule set rather
than a measurement error: `1,091 + 13,194 + 7 + 1 = 14,293`.

**A counting hazard, re-confirmed.** `git ls-files -- 'demo-output/*.png'` returns
**874**, not R12's 10, because git pathspec globs match across `/`. R12 is only
measurable with an anchored regex over a path snapshot; `^demo-output/[^/]+\.png$`
over the `fc9301c5` snapshot returns **10**.

---

## 4. The hand-carry set, re-derived over HEAD

`python3 scripts/hand_carry.py derive`, run twice about a minute apart. `stderr`
was captured on both runs and was **empty**; the section headers were
**byte-identical** between the two.

| Tree | files | bytes | destination |
|---|---:|---:|---|
| `demo-output/website/solve_registry` | 300 | 1,508,128,888 | `evidence/solve_registry` |
| `demo-output/website/surfaces` | 7 | 2,180,257 | `evidence/surfaces` |
| | **307** | **1,510,309,145** | |

**Confirmed: 2 trees, 307 files, 1,510,309,145 bytes**, exactly the plan's figure.
Re-measured independently with an `os.walk` carrying an explicit `onerror`
handler and a per-file `lstat` guard that *reports* rather than skips: 300 files
/ 1,508,128,888 B and 7 files / 2,180,257 B, **0 walk errors, 0 unreadable
files**. Both trees hold **0 tracked files at HEAD**, so they are genuinely dark
and `git mv` genuinely cannot reach them.

**`campaign/THERMAL_K0_runs/` is correctly off the list, and the reason it was
ever on it is live today.** At `fc9301c5` it holds **97 tracked files at HEAD and
0 in the index**. An index-framed derivation run right now would still call it
dark and still put it on the carry list, where it would be hand-moved out from
under the `git mv` that R20 is about to make against it. The struck claim stays
struck.

The other three buckets, at this frame:

- **RIDES ALONG — 963 trees, 33,819 files, 10,560,965,662 bytes.** Carried only
  if every `git mv` names a DIRECTORY. A per-file loop leaves 10.56 GB behind.
- **STAYS PUT — 622 trees, 15,734 files, 1,455,590,108 bytes.** The plan's §3.5
  reads *"7 trees, ~16,020 files, ~1.49 GB"*. **The file count moved by −286 and
  the tree count by +615**, and the cause is the R7 growth of §2: 344 tracked
  files landed inside `docs/campaigns/F14-cooling-ladder/`, which was one
  maximal dark tree and is now several hundred maximal dark subtrees threaded
  between the tracked ones. The bucket did not gain trees; a tree fragmented.
- **DISCARD — 6 trees, 30 files, 864,836 bytes.** Reported, never carried.

**Batch 6's stated precondition is no longer live and must be re-measured, not
trusted.** §4's batch 6 row requires *"786 files under `dafoam/**/work_sail/` are
root-owned — `chown` them BEFORE the batch"*. At this frame
`find . -path ./.git -prune -o ! -user ubuntu -print` returns **0 files**
repo-wide, with empty stderr. `work_sail` is at
`demo-output/website/dafoam/work_sail` (one level, not two) and holds 215 files,
all `ubuntu`-owned. Either the `chown` has been done or the ownership changed;
**the note is stale in the safe direction, and batch 6 re-runs this `find` rather
than reading this line.**

### 4.1 An instrument note on `hand_carry.py`'s measurement, not repaired here

`measure()` walks with `os.walk(abs_dir)` and no `onerror`, and its per-file
`lstat` is wrapped in `except OSError: continue`. A file it cannot stat is
therefore dropped from the count, from the byte total **and** from the path-set
digest, silently and without reaching stderr. `maximal_dark_trees()` has the
same `os.walk` shape. It cost nothing at this frame — the independent
error-reporting walk above found 0 failures and 0 non-`ubuntu` files — but the
before/after check in `carry()` compares two measurements taken by the same
blinded instrument, so a permission change *between* them is the one thing it
cannot see, and 786 root-owned files were the standing hazard until today. Not
repaired: batch 0 moves nothing and edits nothing, and this belongs to whoever
runs 7H.

---

## 5. The batch 2 / batch 7 conflict is live

Re-derived at `fc9301c5`, and every figure re-measured:

```
demo-output/website/campaign/MESH_AUDIT_runs/
    78 tracked files at HEAD, 78 files on disk, 380,082 bytes
    suffix distribution: 78 x .checkMesh, and nothing else
```

Every one of the 78 is a `*.log.checkMesh` — solver-utility output, precisely the
class §7.2 sends to batch 2. `hand_carry.py derive`'s projection reports it and
**only** it: *GOES DARK AFTER BATCH 2's UNTRACKING (1)*. The moment batch 2
lands, the directory holds no tracked file, and batch 7's `git mv` of it aborts —
taking every other source in that invocation with it, because `git mv` with
several sources aborts all of them.

**The class is not already ignored, which fixes when it happens.**
`git check-ignore --no-index -q` on one of the 78 returns **exit 1**: no existing
rule matches it. So these files did not leave in batch 1 and cannot; they leave
only when batch 2 writes the *new* rule for the solver-output class. The hazard
is created by batch 2 and by nothing before it.

### The resolution the plan requires

§3.3 gives two ways out and §4's batch 2 row requires one of them to be chosen
**before batch 2 runs** — *"Stopping here is safe; proceeding to 7 without §3.3's
fix is not."* They are not equivalent, and the difference is worth stating
because the plan's own verification line does not separate them:

**(A) Exclude the 78 from batch 2's untracking** until batch 7 has moved the tree
to `verification/runs/MESH_AUDIT_runs`, then untrack them there. The carry set
stays at 2 trees / 307 files / 1,510,309,145 B, so **G1 continues to pass against
the baseline this document records**, and the move stays a `git mv` — index and
disk never disagree. **This is the option that preserves every invariant the plan
already states**, and it is the one recommended here.

**(B) Let it go dark and hand-carry it in 7H**, which §4's 7H row explicitly
allows — *"§3.1's two trees, plus `MESH_AUDIT_runs` if batch 2 took it."* This is
permitted, but it is not free and both costs must be paid in the same commit as
batch 2:

1. **G1's baseline changes.** The carry set becomes **3 trees, 385 files,
   1,510,689,227 bytes**. G1 is *"the carry set must not have grown"*; under (B)
   it grows by design, and unless the baseline is re-stated in the batch-2 commit
   G1 reddens at batch 4 for a reason that is not a defect — which is how a gate
   gets loosened.
2. **The projection must be told what batch 2 actually did.**
   `hand_carry.batch2_survivors()` classifies `*.log.checkMesh` inside a `*_runs`
   tree as output *by file class*, not by what the batch's own list contained.
   Under **(A)** the projection keeps reporting `MESH_AUDIT_runs` as going dark
   even though batch 2 spared it, so batch 2's stated verification — *"the
   goes-dark-after-batch-2 section must read 0 afterwards, not 1"* — **does not
   pass under (A) unless `batch2_survivors()` is amended in the same commit** to
   encode the exclusion. Under **(B)** it reads 0 for the wrong reason: the tree
   is already in the carry set and the projection reports only the difference.

**So the verification line as written is satisfied trivially by (B) and not at all
by (A), which is the reverse of the safety ordering.** Batch 2 must therefore
land, in one commit: its choice, stated; the corresponding amendment — either to
`batch2_survivors()` under (A) or to G1's recorded baseline under (B); and its
own goes-dark re-derivation as evidence. A batch-2 that lands the untracking and
leaves the gate to be interpreted afterwards is the failure mode this section
exists to prevent.

---

## 6. What will break — every moved count, judged

**Benign — new work landing, and the rule is right about it.**

- **R3 +3, R9 +5, R21 +9, R22 +1.** New modules, new tests, new ladder records,
  one dafoam file. Each lands in the rule its content belongs to. The only
  consequence is arithmetic: batch 7 is 9 files larger than the plan says on
  R21's account.
- **R20 +102.** 97 `THERMAL_K0_runs` files and 5 `F4_runs`. R20 is exactly right
  about them, and this is the movement that most needed re-deriving, because it
  is invisible in the index frame — where `THERMAL_K0_runs` reads 0 tracked and
  was, on that basis, put on a hand-carry list once already. **Benign as a
  classification and load-bearing as a count**, and §3.2's two `.gitignore`
  re-points at `:122-123` are what keep those 97 files tracked after the move.
- **The four U rows falling to zero.** Batch 1, landed and verified: 6,950 left
  tracking, all U-rule, zero R-rule.

**Not benign — a classification error.**

- **R7 +360, of which 344 are a solver case corpus.**
  `docs/campaigns/F14-cooling-ladder/` holds 344 tracked files at HEAD and **0 in
  the index** — 274 under `K0c_runs/`, 41 under `K0b_mesh_sensitivity/`, 23
  reference data, plus the rung records. The leaf directories are
  `system/` (75), `constant/` (53), `0.orig/` (52): OpenFOAM case dictionaries and
  initial conditions, the same class of artifact that `campaign/*_runs/` holds.
  **R7 says `docs/**` is unchanged, so the map routes those 344 files to
  `docs/`, while their siblings under `demo-output/website/campaign/*_runs/` go
  to `verification/runs/` under R20.** The map now sends one class of file to two
  destinations depending on which directory the agent who created it happened to
  choose, and §1's target tree describes `/docs/` as
  *"charters/ standards/ research/ papers/ + DOCKET LESSONS LOCATIONS
  USING_THIS_LAB"* — a run archive is not in that description.
  R7 was measured as 137 documentation files and is 497. **This is a rule that
  has silently changed meaning and it should be ruled on before batch 4**, which
  is the batch that touches `docs/`. It is not urgent — R7 moves nothing, so
  nothing breaks at rest — but "R7 keeps `docs/**`" will read as a decision about
  a run archive the first time somebody quotes it.
- **`AWS_TREE_PLAN.md`, unclassified.** §2.3. One file, no rule, and the
  reconciliation no longer closes at zero. A path in no rule is a path the mover
  walks past.

**A note on the shape of both.** The index frame contained neither of them: the
identity closes at 13,814 with **zero** unclassified and 137 documentation files
in R7. That is not a coincidence. The frame that under-reports hides exactly the
class of file that is *new*, and new files are exactly the class most likely to
need a rule that does not exist yet. A completeness gate read over that frame is
structurally guaranteed to stay green. Recorded as **L-95**.

---

## 7. Method, and what is a moving target

- **Every rule count is over a fixed commit**, `git ls-tree -r -z` at
  `fc9301c5`, and re-taken at `3f46e4e9` with an identical path set. A commit is
  a fixed frame; a filesystem walk is not, which is why the rule table uses the
  first and only §4 uses the second.
- **`stderr` was captured on every walk and every `git` invocation** in this
  pass and was empty on all of them. The two `hand_carry derive` runs produced
  byte-identical headers.
- **No count was piped into `head`.** Every total in this document is a `wc -l`
  or a `uniq -c` over a complete stream; the two places a listing is truncated
  for display, the total is stated separately beside it.
- **This sweep does not appear in its own results.** Every intermediate file —
  the path snapshots, the classifier, the derive output — was written outside the
  repository, so nothing here is counting itself.
- **The tree is being written by other agents while it is measured**, and HEAD
  moved once during this pass. The rule table is *not* over a moving target: it
  is over `fc9301c5`, checked at `3f46e4e9`. §4's byte totals *are* over a moving
  target — they are a filesystem walk of live trees — and are stable only across
  the two runs a minute apart that were compared. §3 of the execution plan says
  the same thing about the same numbers and it is still true.

## 8. What batch 0 did not do

No file was moved, renamed, copied, deleted or untracked. No directory was
created or removed. `.gitignore` was not edited and `git mv` was not invoked. The
shared index was not touched. `scripts/hand_carry.py` was run in `derive` mode
only, which never writes inside the repository, and its §4.1 defect was reported
rather than repaired. **The other half of batch 0 as the map states it — marking
`docs/PHASE2_MOVE_MAP.tsv` and `docs/PHASE2_STRUCTURE_PROPOSAL.md` superseded —
was not performed here and remains outstanding**; this pass was the
re-derivation, and saying so is what stops batch 0 from being recorded as
complete when half of it is.
