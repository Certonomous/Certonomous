# MOVE_MAP batch 2 — the solver-output rule, the untracking, and the live campaign the rule reached that no gate could see

**No file was moved, renamed, copied or deleted. No directory was created or
removed. `git mv` was not invoked. The shared index was not touched — no
`git add`, no `git read-tree` against it, and the 47 staged deletions and the
25-line-stale `.gitignore` it holds were left exactly as found.** Batch 2 writes
one `.gitignore` block and removes a class of file from git's index. Every one
of those files is still on disk, at the same path, with the same byte count.

**Anchor: `fc1e3bac`.** Every path-derived count below is over
`git ls-tree -r -z --name-only fc1e3bac` — **14,299 paths, 14,299 unique**,
stderr empty on the walk. Never `git ls-files`: the index is 485 paths behind
HEAD at this frame and the missing paths are by construction the newest, which
is the frame defect `docs/USING_THIS_LAB.md` §8.7 records.

**HEAD moved twice during the pass and the drift was measured rather than
assumed.** `676e2bb8` and `6be16310` landed while this was being prepared,
touching `LESSONS.md` and `LOCATIONS.md` only. Re-derived at `6be16310`: the
path set is **14,299 at both**, and the untrack list is **identical — 0 added,
0 removed**, compared as a set difference between two named commits rather than
by count. **The list is re-derived again by the commit script against the
commit's own parent, whatever that is at the moment the ref moves**, and any
drift from the `fc1e3bac` derivation is reported in both directions before
anything is removed: a new solver log landing under the two roots legitimately
grows the list, and anything *leaving* it would mean a peer had untracked or
deleted something and is not legitimate.

**Inherited, not re-decided.** R25 = 315 with the campaign segment preserved;
`AWS_TREE_PLAN.md` in R1; the reconciliation closing at 780 keep + 13,511 move +
7 exceptions + 0 unclassified = 14,298 at `4d7c195a`; option A for
`MESH_AUDIT_runs`. This pass ratifies none of them and re-opens none of them.

---

## 1. THE FINDING — batch 2's rule reached a live campaign, and the gate that is supposed to catch that reads 0 either way

`MOVE_MAP_EXECUTION_2026-08-17.md` §3.3 records one interaction between batch 2
and batch 7, `MESH_AUDIT_runs`, and §4's batch-2 row states the verification
that guards it: *"the goes-dark-after-batch-2 section must read 0 afterwards,
not 1."* **There is a second interaction, it is larger, and that verification
cannot see it.**

### 1.1 What the class rule reached

`hand_carry.batch2_class_candidates` reaches **7,677** tracked paths at
`fc1e3bac`. **109 of them are R25 files** — that is, files inside
`docs/campaigns/F14-cooling-ladder/K0c_runs/`, which RULING 1 of 2026-08-17
sends to `verification/runs/F14-cooling-ladder/K0c_runs/` under batch 7, and
which are part of the **315** that ruling counts.

| What the 109 are | Files |
|---|---:|
| `0.orig/{T,U,alphat,p_rgh}` — initial conditions | **44** |
| `log.{blockMesh,checkMesh,cellCentres}`, `log.buoyantBoussinesqSimpleFoam{,.stage2,.stage3}` | **65** |
| | **109** |

`K0b_mesh_sensitivity` contributes **0**: its 41 tracked files are all under
`system/`, `constant/` and `0.orig/`, and only the last of those was reachable.

**And the thermal lane is writing that tree right now.** `.gitignore:125-138`,
the block that governs those two run trees, was written **today** by the lane
that owns them, and its own comment records the cost of getting this class wrong
in as many words: *"one `[0-9]*` loop deleted every initial-condition directory
in the K0b tree."*

### 1.2 Why batch 2's stated verification does not catch it

`project_after_untracking` reports trees that **go dark** — that lose their last
tracked file, after which batch 7's `git mv` of them aborts. `MESH_AUDIT_runs`
is caught because all 78 of its tracked files are in the class.
`K0c_runs` is not, because only 109 of its **274** are: **165 tracked files
remain**, `git mv` never aborts, and no maximal dark subtree is created that an
ancestor's rename does not already carry.

Fired four ways at `fc1e3bac`, stderr empty on every run:

| Firing | GOES DARK AFTER BATCH 2 |
|---|---:|
| option A, the module as committed | **0** |
| option B, exclusions dropped | **1** — `MESH_AUDIT_runs`, 78 f |
| option A **plus batch 2 taking all 109 F14 files** | **0** |
| the same again, with R25 **bound** into `redirect()` by a probe | **0** |

**Rows 1 and 3 are the finding.** The projection reads 0 whether batch 2 spares
the F14 files or takes every one of them, so a green batch-2 gate is not
evidence that batch 2 left R25 alone. Row 4 rules out the obvious explanation:
this is not the `lab_paths` R25 binding being absent — binding it by probe does
not change the answer — it is that **the gate is a go-dark detector and this
hazard is not a go-dark.** The two hazards look identical in a batch plan and
are not the same shape at all.

### 1.3 The handling

**The same ruling, applied the same way.** `docs/campaigns` is added to
`hand_carry.BATCH2_EXCLUSIONS`, beside `demo-output/website/campaign/MESH_AUDIT_runs`,
and batch 2's `.gitignore` block is **scoped to the two roots it untracks** and
mentions `docs/` nowhere. Batch 7 untracks the F14 run trees at their new path
under `verification/runs/`, exactly as it does `MESH_AUDIT_runs`.

Three reasons, and the first is the one that would have mattered on its own:

1. **A repo-wide rule would silently ignore a live lane's future output.** A
   tracked file overrides an ignore rule, so the 65 logs already committed would
   have stayed tracked — but every solver log the thermal lane writes next would
   be ignored at birth, and it would find them un-addable with nothing saying
   why.
2. **R25 = 315 was ratified this morning.** Untracking 65 of the 315 changes a
   ratified count in the same day with no ruling, and changes what batch 7
   moves.
3. **The gate cannot arbitrate.** §1.2. Where a gate cannot see the difference,
   the difference belongs in a named constant, not in a judgement each batch
   re-makes.

**Pinned by tests, and by a mutant that survived the first cut.**
`test_the_ruled_exclusion_keeps_r25_files_out_of_batch_2s_list` reads the
**default** rather than a hand-passed tuple, and
`test_the_go_dark_gate_reads_zero_either_way_so_it_is_not_the_check` asserts the
negative result of §1.2 directly, so if the gate ever becomes able to see this
hazard the constant is revisited rather than quietly kept. The first cut of the
first test passed `("docs/campaigns",)` explicitly and was green against a
constant that did not contain it — it pinned the filtering and not the ruling,
which is the defect the option-A amendment already names: *"a gate whose default
differs from the batch's own choice reads one thing while the batch does
another."* It was caught by a planted mutant and not by review.

---

## 2. THE SECOND FINDING — the class rule called 122 tracked initial conditions solver output

`batch2_class_candidates` spared the path segments `system`, `constant` and `0`
and **did not spare `0.orig`**, which is the OpenFOAM spelling for the initial
conditions a case is rebuilt from. It sits in the same row of
`MOVE_MAP_2026-08-16.md` §7.2's disposition table as `0/` — *"initial conditions
(`0/`) … stay tracked — source"* — and the rule reached it anyway, because the
function tests segment equality and the segment is `0.orig`, not `0`.

Measured at `fc1e3bac`: **160 tracked `0.orig/` files exist and the unrepaired
class rule reached 122 of them.**

| Tree | reachable | tracked |
|---|---:|---:|
| `demo-output/website/campaign/F7_runs/F7a_R1` | 45 | 45 |
| `docs/campaigns/F14-cooling-ladder/K0c_runs` | 44 | 44 |
| `demo-output/website/campaign/THERMAL_K0_runs` | 20 | 20 |
| `demo-output/website/dafoam/{work,ladder-a/A5_work}` | 13 | 13 |
| trees the rule did not reach | 0 | 38 |
| | **122** | **160** |

**64 of the 122 are tracked ONLY because two `.gitignore` negation blocks
re-include them**, at `:122-123` and `:135-138`, and **both blocks were written
on 2026-08-17 by the lanes that own those trees**. A batch-2 list built from the
unrepaired function would have untracked the files those two blocks exist to
keep, on the same day they were written, and the second block's comment names
that exact outcome as something that has already happened once.

**Repaired at the classifier, not at the exclusion list**, because this is not a
deferral: a `0.orig` file is case input and the rule should never have reached
it. `src_seg` gains `0.orig` and `0.org`. The second spelling matches nothing in
this tree today and is there because a rule proven only against today's
filenames has been proven only against today's filenames.

### 2.1 The mutant table

Each amendment falsified against its own test, and each mutant caught by the
test written for it rather than by collateral. The harness places a copy of
`lab_paths.py` beside each mutant: the first attempt did not, every mutant died
in `importlib` with `FileNotFoundError`, and **all four tests reddened
identically under all three mutants** — a table that discriminates nothing,
which is what a false red looks like.

| Mutant planted | initial conditions | the control | the ruled exclusion | the go-dark pair |
|---|---|---|---|---|
| `src_seg` back to `{system, constant, 0}` | **RED** | green | green | green |
| `stays()` returns `True` for everything | green | **RED** | green | **RED** |
| `docs/campaigns` dropped from the constant | green | green | **RED** | green |
| the module as committed | green | green | green | green |

The second row is the must-not-match control and it is load-bearing: without it,
a `stays()` that spared everything satisfies the initial-conditions test and
untracks nothing, which is a batch 2 that reports success having done nothing.

---

## 3. What batch 2 untracked

**7,403 files, 3,631,998,729 bytes on disk.** Derived not from a classifier but
from `git check-ignore --no-index` over all 14,299 tracked paths, run against
`fc1e3bac`'s `.gitignore` and against `fc1e3bac`'s `.gitignore` plus the new
block, in two scratch repositories outside this tree. **The list is exactly the
set the new rule newly matches** — there is no separate list to drift from the
rule.

`--no-index` is not a detail. `git check-ignore` is silent about tracked paths,
and tracked-but-ignored is the entire population an untracking batch is about;
the first audit of this class returned **0 rows for every candidate**, which is
the shape of a clean result and was the instrument. §8.6 records the same zero
from the previous untracking.

| Class | Files |
|---|---:|
| solver time-directory fields | **6,331** |
| solver logs (`log.*`, `*.log`, `*.log.*`) | **1,072** |
| | **7,403** |

```
tracked at HEAD           14,299 files   4,475,301,712 B
leaving tracking           7,403 files   3,631,998,821 B   (blob bytes)
remaining tracked          6,896 files     843,302,891 B
                          51.8% of files, 81.2% of tracked bytes
```

**Assertions on the list, each run rather than reasoned:**

| Assertion | Result |
|---|---|
| paths under `docs/` | **0** |
| paths under `MESH_AUDIT_runs` | **0** |
| paths under a `0/` or `0.orig/` segment | **0** |
| paths under a `system/` or `constant/` segment | **0** |
| paths outside `campaign/` and `dafoam/` | **0** |
| tracked paths that STOP being ignored | **0** |
| **files on disk that stop being ignored** | **0** |
| paths in the list not matched by the rule | **0** |

### 3.0 THE THIRD FINDING — the first rule un-ignored 572 files, and only the wider oracle saw it

The first draft of the block wrote the time-directory rule as `**/[0-9]*/` and
then re-included `0/` and `0.orig/` beneath it, following the shape
`.gitignore:122-138` already uses. Over the **tracked** frame that draft was
perfect: 7,403 newly ignored, 0 un-ignored, every assertion above green.

Re-run over **every file on disk under the two roots — 43,663 of them, not just
the 14,299 tracked ones — it stopped 572 currently-ignored files from being
ignored**: 479 under `0/`, 73 under `0.orig/`, 20 under `interpolatedFields`.
They were already excluded by a rule at their own depth, and the re-inclusion
reached past the exclusion the new rule had created to the exclusion an old rule
already had. Un-ignoring 572 files of solver output is the setup for
`.gitignore:56`'s own recorded incident — *"I ran `git add -A` on a directory
that contained solver output"*, 25 million lines and a 513 MB `.git`.

**A tracked-frame oracle cannot see this, by construction**: a file that is both
ignored and untracked is invisible to a census of tracked paths, and it is
exactly the population an ignore rule governs. The repair removes the need for
the negation rather than tuning it — `[1-9]*/` and `0.[0-9]*/` never match `0`
or `0.orig` in the first place, since `0.orig` fails `0.[0-9]` on its `o`.
Verified over every directory segment on disk under both roots: **577 distinct
digit-leading segments, of which exactly three are not purely numeric** —
`0.orig`, `2026-08-08` and `4G_runs` — each either unmatched or handled by a
named exception. After the repair, over all 43,663 files: **7,404 newly ignored,
0 un-ignored**, and the tracked list is byte-identical to the draft's, so the
untracking did not move.

The one on-disk file newly ignored that is not in the untrack list is
`campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5/log.cellCentres`, a solver log that
was already untracked.

**The claim §7.2 said to check rather than assume, checked.** *"After the
untracking, exactly one tracked blob still exceeds 50 MB, and it is
`campaign/F8_runs/phase6_mrf/constant/triSurface/blade.stl`."* At `fc1e3bac`
exactly one tracked blob exceeds 50 MB, it is that file at **68,053,713 bytes**,
it sits under `constant/` and is therefore source, and it survives this batch as
the only one. The claim holds, and it holds because of the rule rather than by
luck.

### 3.1 What the rule deliberately does NOT reach, and why each is a deferral

**(a) `MESH_AUDIT_runs` — 78 files.** Option A, ruled. The negation is written
into `.gitignore` beside the rule rather than left in a record, so the sparing is
legible to whoever next reads the rule, and **removing it is part of batch 7.**

**(b) `docs/campaigns` — 109 files.** §1.

**(c) 198 files §7.2 calls *"loose field/mesh files outside time dirs"* — NOT
UNTRACKED, and this is a scope reduction stated rather than smoothed.** §7.2
lists three UNTRACK classes and this batch takes two. The third was reconstructed
by the same classifier that had just been shown wrong about `0.orig`, and
inspecting its 198 files — 101 distinct leaf names — found it sweeping in things
that are unambiguously **case input and solver source**:

- `demo-output/website/campaign/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/` —
  **8 files of a custom OpenFOAM solver's C++ source**, plus 2 in its `Make/`;
- `controlDict`, `controlDict.solve`, `blockMeshDict`, `turbulenceProperties`,
  `caseDef`, `fieldDef` — **26 case dictionaries** that happen not to sit under a
  `system/` or `constant/` segment.

Having just caught the classifier untracking initial conditions, untracking 198
more files on the same classifier's verdict would be repeating the error rather
than learning from it. **The class needs a membership list, not a shape** — which
is `L-94`'s finding applied to a disposition rather than to a partition — and it
is deferred to whoever rules it. Nothing is lost by deferring: the files stay
tracked, which is the safe direction.

### 3.2 One file in the list is a moving target, and it is named

`demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5/log.blockMesh` is
**2,731 bytes in `fc1e3bac` and 2,639 on disk** — the only one of the 7,403
whose worktree content differs from its blob. A lane re-ran `blockMesh` and did
not commit the shorter log. Untracking it makes that uncommitted difference
permanent as ignored bulk, which is the intended end state for solver output and
is recorded here so it is not later read as a loss. The other 7,402 are
byte-identical between blob and disk.

---

## 4. Nothing left the disk

Untracking removes a file from git's index. It does not touch the filesystem,
and the whole value of §7.3's *"a 70% reduction … without deleting anything"*
rests on that being verified rather than assumed.

Every one of the 7,403 paths was `lstat`ed immediately before the commit and
again immediately after, and **the two size tables were compared path by path,
not by total** — two trees can share a total and differ in every file.

| | Files present | Bytes |
|---|---:|---:|
| before the commit | 7,403 / 7,403 | 3,631,998,729 |
| after the commit | 7,403 / 7,403 | 3,631,998,729 |
| paths differing in size | **0** | |
| paths missing | **0** | |

---

## 5. The commit form, and why the mandated one could not have been used

`git commit -F msg -- <paths>` takes those paths' content **from the working
tree**, so a `git rm --cached` on a file that stays on disk is silently re-added
by the very commit meant to remove it — no error, an ordinary diffstat, and the
untracking gone. §8.5 demonstrates it in a scratch repository rather than
inferring it.

So this batch used the index-isolated form: a **private** `GIT_INDEX_FILE`, so no
peer's staged work is read into the tree; a **tree-diff assertion before the ref
moves**, because after it moves there is nothing left to refuse; and
`update-ref` given the **observed parent**, so it fails rather than clobbers.

**The assertion counts the `D` entries and compares the set, rather than trusting
the command.** A `git diff --name-status` that a caller only eyeballs is the same
class of evidence as the diffstat §8.5 says looks ordinary. It asserts: the
number of `D` rows equals the untrack list's length; **the set of `D` paths
equals the untrack list exactly, both directions**; `A` = 1; `M` = 5; no row
carries any other status; and the total row count is the sum of those.

**`.gitignore` was rebuilt from the parent commit's BLOB**, never from the
worktree and never from the shared index. The worktree copy is byte-identical to
HEAD's, but **the shared index's copy is 25 lines behind HEAD** and lacks both
`0.orig` protection blocks — so an index-sourced rebuild would have reverted, in
this batch's own commit, the two blocks §2 exists to protect.

`LESSONS.md` and `docs/DOCKET.md` were rebuilt the same way, from the parent's
blob plus this pass's rows, with the next free ID **re-derived at the commit
attempt** by comparing ID sets under a period-anchored regex. Both were then
written back into the worktree, because the private-index form never touches it
and §9 item 8 records that every such commit widens the HEAD/worktree gap
monotonically.

---

## 6. The gates, both sides, with their finding sets

**A verdict is not a finding set, and only the finding set can show that nothing
moved for a reason that is not this batch.**

### 6.1 `scripts/lab_check.py --no-tests`

`FAIL`, exit 1, ran 20/20, **before and after**, with the **same seven failing
checks in both frames**:

| Check | before | after |
|---|---|---|
| `scripts/check_absolutes.py` | FAIL | FAIL |
| `scripts/check_pdf_surfaces.py` | FAIL | FAIL |
| `scripts/check_proposal_surface_coverage.py` | FAIL | FAIL |
| `scripts/check_rung_attribution.py` | FAIL | FAIL |
| `scripts/contention_audit.py` | FAIL | FAIL |
| `scripts/installed_registry.py` | FAIL | FAIL |
| `scripts/self_audit.py` | FAIL | FAIL |
| the other 13 | PASS | PASS |

The eighth failing check of the standing baseline is the suite itself, which
`--no-tests` skips by design and reports as `UNKNOWN … the suite was not run`.
Every one of the seven has a standing reason on record and none of them is
reachable by an ignore rule: `installed_registry` is the crontab drift the box's
owner owns, `check_absolutes` is condemning citations under the frame defect
`docs/USING_THIS_LAB.md` §8.7 records, and the rest are surface and attribution
findings already filed.

### 6.2 The three standing gates

| Gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B** | **identical** |
| **G2** control corpora | 223 path fields, 0 unresolved | 223, 0 |
| **G3** root binding | `roots OK`, `AMBIGUOUS = ()` | same |

G2 was fired both ways rather than counted: a planted citation that must resolve
does, and a planted citation to a document that never existed returns `None`. A
corpus whose every field resolves can have stopped discriminating, and the count
alone would not say so.

**G1 was also pre-computed against the projected post-batch tracked set before
the commit**, so the carry set was known not to grow before anything was
removed rather than checked afterwards.

### 6.3 Batch 2's own verification, fired both ways

| Firing | GOES DARK AFTER BATCH 2 |
|---|---:|
| batch 2's **literal list**, handed to the gate | **0** |
| the module **default** | **0** |
| both exclusions dropped | **1** — `MESH_AUDIT_runs`, 78 f |

The default and the literal list agreeing is the property the option-A amendment
asked for: *"the default must BE the ruled option, or the gate reads one thing
and the batch does another."* And §1.2 remains true of all three rows — this gate
cannot see the F14 interaction, which is why §1 is a measurement and not a gate
result.

---

## 7. WHAT BREAKS IF BATCH 2 LANDS AND BATCH 3 NEVER DOES

**Nothing breaks, and the plan's own answer is right — but it is right for a
reason that is worth stating, because the reason is not "batch 2 is small".**

Batch 2 changes **no path**. Every constant in every `.py` and `.sh` file
resolves to the same file it did before, because untracking moves nothing;
`lab_paths.resolve()` returns the same answer for all 223 control-corpus fields
after as before, which is G2. Batch 3b converts consumers to import `lab_paths`
instead of re-spelling the prefix, and there is nothing for it to protect against
yet. Batch 2 is stable in this state and defensible with no reference to the
target tree at all — the same standing batch 1 has.

**Three things change permanently at batch 2 regardless of batch 3, and they are
the real answer:**

1. **The box and a fresh clone diverge by 3.63 GB.** Every check that resolves a
   citation by touching the filesystem — `check_evidence_paths_exist`,
   `lab_paths.resolve()`, `hand_carry.measure()` — keeps passing **on this
   machine**, and would find 7,403 fewer files in a clone. That is the intended
   trade of §7.3 and it is the point of the batch, but it means from here on a
   green suite is evidence about this box and not about the repository. Batch 1
   already made this true of 6,950 files; batch 2 more than doubles it.
2. **`LOCATIONS.md` is the only surface that enumerates untracked evidence**, and
   §7.3 makes that enumeration part of the deal — *"every untracked file stays on
   disk at its new path and is enumerated by `LOCATIONS.md`"*. It is not updated
   by this pass and is owed. Its one load-bearing claim was checked (§3) and
   holds; the enumeration is a separate obligation and is filed, not done.
3. **The shared index still holds 7,386 of the 7,403 entries.** This pass was
   directed not to touch the shared index and did not. §8.5's protocol closes an
   untracking with a surgical `git update-index --force-remove --stdin` over
   **only the paths that agent removed** — leaving every other entry alone — and
   until somebody runs it, a `git commit -- <one of those paths>` by any agent
   re-adds that file to the tree, silently. This is the one loose end batch 2
   leaves and it is nobody's by default, so it is filed as owed rather than
   assumed.

**And one thing that breaks if batch 7 runs without reading this record.** Both
`.gitignore` exceptions written here — `MESH_AUDIT_runs`'s negation and the
scoping of the whole block to two roots — are **path-anchored**, so batch 7's
`git mv` moves the trees out from under them. §3.2 of the execution plan already
requires two such re-points at `:122-123`; this batch adds a third and a fourth,
and the deferred untrackings of §3.1(a) and §3.1(b) are the reason they exist.

---

## 8. Method

- **Every rule count is over one fixed commit**, `git ls-tree -r -z` at
  `fc1e3bac`, checked for duplicates (14,299 lines, 14,299 unique). Never
  `git ls-files`. The untrack list itself was re-derived a second time, against
  the commit's actual parent at the moment of the commit, rather than carried
  from the earlier snapshot — the thermal lane is live and a snapshot is not a
  frame the commit is made in.
- **`stderr` was captured on every walk, every `git` invocation and every
  `check-ignore` pass** and was empty on all of them.
- **No count was piped into `head`.** Every total is a `wc -l`, a `comm` or a
  classifier total over a complete stream. Where a listing is truncated for
  display the total is stated beside it.
- **Nothing here is ordered or selected by a commit date.** Every figure is a
  commit-membership question, taken from a named tree object; re-dating a blob
  cannot move one. The one date-shaped phrase, *"written today"*, is about two
  `.gitignore` blocks whose own text carries the date.
- **What is a moving target and what is not.** §1, §2 and §3's path counts are
  over `fc1e3bac` and are not. §3's on-disk byte totals and §6.2's G1 byte totals
  are filesystem walks of live trees and are; §3.2 names the one file that moved
  under this pass while it was measured.
- **This record does not appear in its own results.** Every intermediate — the
  path snapshots, the two oracle repositories, the classifier probes, the three
  mutants — was written outside the repository, and every count was taken at
  `fc1e3bac`, before the commit that lands this file.

## 9. What batch 2 did not do

No file was moved, renamed, copied or deleted; nothing left the disk (§4). No
directory was created or removed. `git mv` was not invoked. The shared index was
not touched, and its two pre-existing conditions — 47 staged deletions and a
`.gitignore` 25 lines behind HEAD — were inspected and reported, never reverted.
`scripts/lab_paths.py` was not edited and R25 is still not bound in it. The 198
files of §3.1(c), the 78 of §3.1(a) and the 109 of §3.1(b) remain tracked. No
solver was launched and nothing was registered. `LOCATIONS.md` was not updated
and §7's item 2 says so rather than leaving it to be discovered.
