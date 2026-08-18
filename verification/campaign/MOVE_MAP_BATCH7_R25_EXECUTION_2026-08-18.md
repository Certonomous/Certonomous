# MOVE_MAP R25 — batch 7's deferred half lands in the quiet window, the move is depth-preserving, and the one thing it broke was assembled from segments

R25 is the half of batch 7 that was correctly deferred. D401 records why: at
batch 7's frame `buoyantBoussinesqPimpleFoam` was writing into
`docs/campaigns/F14-cooling-ladder/` **in the second the measurement was taken**,
three peer shell loops held that directory as their working directory, and the
owning lane had landed ten commits in 75 minutes. This pass moved **1,671
tracked files and 8,049 dark ride-along files — 9,720 files, 2,461,594,000
bytes — in six directory renames**, re-pointed **fourteen** `.gitignore` rules,
**decided** the `exec_bits.OWNERS` family rather than inheriting it, and
repaired **two** instruments that changed count as a side effect of the move.

**Nothing else was done.** No other rule was executed, `_SHIPPING_RE` was not
touched, and two defects this pass found but does not own are docketed rather
than fixed (§10).

---

## 1. THE QUIET WINDOW — three conditions, re-verified immediately before the move

D401 named three conditions and this pass re-measured all three itself rather
than inheriting the brief's figures, then re-measured them again in the minute
before the first `mv`.

| condition | at the opening reading, 07:53 UTC | immediately pre-move, 08:30 UTC |
|---|---|---|
| solver processes, by name | **0** of 283 processes; 0 naming any R25 tree | **0** of 284; 0 naming any R25 tree |
| `/proc/*/cwd` into the tree | **0** holders; **0** open file descriptors | **0** holders; **0** open fds |
| newest write under the tree | **99.0 minutes** old | **135.9 minutes** old |

The third row is the load-bearing one and it is reported as a pair on purpose:
the newest write **aged by the 37 minutes that elapsed**, and the newest file was
the same file at the same timestamp (`K2b_PILOT_RESULTS.md`, 06:14:54 UTC) at
both readings. A single reading cannot distinguish a quiet tree from a tree
between two writes; two readings 37 minutes apart with no new write can.

The process scan is by NAME over the whole process table, not by a grep for one
solver: `[a-zA-Z]*Foam`, `blockMesh`, `snappyHexMesh`, `decomposePar`, `mpirun`,
and separately for any process naming `F14`, `cooling-ladder` or any of the six
tree names. The file-descriptor sweep is separate from the `cwd` sweep because a
solver that has `chdir`'d away still holds its log open.

**Ownership precondition re-run rather than inherited:**
`find . -path ./.git -prune -o ! -user ubuntu -print` returns **0 files
repo-wide, stderr empty**.

---

## 2. THE POPULATION AND THE SPLIT, RE-DERIVED

**Population.** Over `git ls-tree -r HEAD` at `a1fbe127`:
`docs/campaigns/` holds **1,713 tracked files**, all of them under the single
campaign `F14-cooling-ladder`. The trajectory the brief carried is
315 → 1,514 → 1,554 → 1,713, and **this reading is 1,713 — unchanged**. It was
expected to differ again and it did not, which is itself the measurement that
says the lane has stopped: the tree grew by 40 files in the 45 minutes batch 7
took, and by 0 in the 2h16m since its last write.

**The frame is stated because it changes the answer.** `git ls-tree -r HEAD` is
8,198 tracked files repo-wide. `git ls-files` — the shared index — is not read
anywhere in this pass, for measurement or for anything else.

**The split, by composition rather than by carrying the ruling's figure.**
Every one of the 1,713 was matched against
`^docs/campaigns/([^/]+)/([^/]*_(?:runs|sensitivity))/(.+)$`:

| | files |
|---|---:|
| **MOVE** — run trees under `*_{runs,sensitivity}` | **1,671** |
| **STAY** — documentation | **42** |
| sum | 1,713 |

The six run trees, and the destination each takes **with the campaign segment
preserved**:

| source | files | destination |
|---|---:|---|
| `docs/campaigns/F14-cooling-ladder/K2e_runs` | 577 | `verification/runs/F14-cooling-ladder/K2e_runs` |
| `…/K2b_runs` | 374 | `verification/runs/F14-cooling-ladder/K2b_runs` |
| `…/K0c_runs` | 274 | `verification/runs/F14-cooling-ladder/K0c_runs` |
| `…/K0cT_runs` | 230 | `verification/runs/F14-cooling-ladder/K0cT_runs` |
| `…/KV1_runs` | 175 | `verification/runs/F14-cooling-ladder/KV1_runs` |
| `…/K0b_mesh_sensitivity` | 41 | `verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity` |

**Four of those six are trees the ruling never saw.** R25 was ruled over
`K0c_runs` (274) and `K0b_mesh_sensitivity` (41) — the 315 of the original
ruling — and `K2e_runs`, `K2b_runs`, `K0cT_runs` and `KV1_runs` landed
afterwards. The pattern reaches them; a list would not have.

The 42 that stay are 14 gate specifications and results documents, a `README.md`,
two analysis scripts at the campaign root (`digitize_wibron2018.py`,
`compute_reference_metrics.py`) and the 25 files of `reference-data/`. They are
documentation and reference data and R7 keeps them under `docs/**`.

**ON THE COLLISION CLAIM, MEASURED RATHER THAN REPEATED.** The brief states that
a bare `K0c_runs` would collide in the flat `verification/runs/` namespace.
Measured at `a1fbe127`: `verification/runs/` holds **26** tree names and **none
of the six collides** — `K0c_runs`, `K0cT_runs`, `K2b_runs`, `K2e_runs`,
`KV1_runs` and `K0b_mesh_sensitivity` are all free today, and the nearest name is
`THERMAL_K0_runs`. **The campaign segment is preserved anyway**, because that is
what RULING 1 ratified and because the reason it gives is not about today:
`verification/runs/` is a FLAT namespace and `docs/campaigns/` is a PER-CAMPAIGN
one, so the collision it prevents is the second campaign's, not this one's. The
claim as stated is a prediction, not a present fact, and it is reported that way.

---

## 3. GRANULARITY, AND THE PROOF ON BOTH SIDES

**Six `mv` calls, one per directory, and the directories exist to be named.**
A per-file loop over the 1,671 tracked files would have moved 1,671 files and
left **8,049 untracked, gitignored files — 1.80 GB in 824 maximal dark trees —
behind in `docs/campaigns/`**, where `git status` would not have shown them.
`hand_carry.derive()` at the pre-move frame reports `rides_along` = **824 trees /
8,035 files / 1,804,861,379 bytes**, and **every one of the 824 is under an R25
source** — R25 was the last rule in the map still carrying dark trees. That is
what the ride-along invariant is worth here.

`docs/` and `verification/` are on the same device (`st_dev` 66305), so each `mv`
is a `rename(2)`: no byte is copied and no byte can be lost in transit. All six
returned **exit 0 with empty stdout and, across all six, 0 bytes on stderr**.

**The assertion is set equality PLUS a byte total, with the digest as a third
witness only** — batch 5 found two sources sharing a path-set digest while
differing in bytes, so a digest alone is not a measurement.

| tree | files | bytes | path-set sha256 | src == dst |
|---|---:|---:|---|---|
| `K0b_mesh_sensitivity` | 4,984 | 765,862,337 | `8ecce06ac2702a17` | set ✓ count ✓ bytes ✓ digest ✓ |
| `K0cT_runs` | 788 | 595,752,905 | `e2b6d583810fd8bd` | set ✓ count ✓ bytes ✓ digest ✓ |
| `K0c_runs` | 798 | 122,799,767 | `1557f0614d5fc282` | set ✓ count ✓ bytes ✓ digest ✓ |
| `K2b_runs` | 2,331 | 960,816,381 | `2e74bf91418929d7` | set ✓ count ✓ bytes ✓ digest ✓ |
| `K2e_runs` | 577 | 11,976,698 | `fb81b5ff0c1d3b04` | set ✓ count ✓ bytes ✓ digest ✓ |
| `KV1_runs` | 242 | 4,385,912 | `f60bbc623120b9ba` | set ✓ count ✓ bytes ✓ digest ✓ |
| **TOTAL** | **9,720** | **2,461,594,000** | | **all four witnesses agree on all six** |

The walker `raise`s on any walk or stat failure rather than returning a smaller
number; **0 errors** on both sides. **0 residual source directories.** The
inverse `mv` list — six lines plus the `rmdir`, reverse order — was written
before the batch started; it is an `mv` list and not a `git reset --hard`,
because a reset restores the 1,671 tracked files and leaves the 8,049 untracked
ones in the new directories, where `git status` will not show them and
`git clean` would delete them.

**Drift check before the move.** The sources were re-measured against the
opening snapshot immediately before the first `mv`, with an abort on any
difference in count, bytes or digest: **0 of 6 trees drifted**, and HEAD was
unchanged at `a1fbe127`.

**Eight tracked files are absent from the worktree** and are carried by blob
rather than by disk: eight `HEATBALANCE_*.{json,txt}` under `K2b_runs/K2bP_C3*`,
present in HEAD and deleted in another lane's uncommitted worktree state. The
index rename carries HEAD's blob to the new path and the peer's pending deletion
survives at the new path. This is the same class batch 7 reported as "ten absent
ones being another lane's in-flight deletions", and it is why 1,671 tracked files
correspond to 1,663 on disk.

---

## 4. THE `.gitignore` — fourteen rules, and **fourteen destinations**

**Derived by prefix, not carried.** Every non-comment line of `.gitignore` was
tested for whether it names an R25 source. **Fourteen do** — the count batch 7
predicted — but **not at the lines batch 7 cited**: they are at **`:144-149`,
`:161-163` and `:284-288`**, not `:260-264`, the file having grown 24 lines under
peer edits since batch 7 wrote that number. The line numbers were re-derived; had
they been trusted, the third block would have been edited in the wrong place.

**One source root, one destination root — so fourteen rules in and fourteen out.**
L-135's warning is that a source root can become two destination roots and the
count must be taken on the DESTINATIONS. It does not bite here, and that was
checked rather than assumed: every one of the fourteen names an explicit tree
(`K0c_runs`, `K0b_mesh_sensitivity`, `K2b_runs`, `K0cT_runs`), and each maps
through `lab_paths.redirect` to exactly one destination. R20/R21's split — where
`campaign/**` had to become three rules — has no analogue in R25.

**AND THE R20 SPELLING IS PRESERVED, WHICH IS THE POINT OF THIS SECTION.**
`.gitignore:227-252` is spelled `verification/runs/*_runs/**` and
`verification/runs/*_work/**`, deliberately and not `verification/runs/**`, so
that R25's trees are not swept the moment they land. R25's destinations are
`verification/runs/F14-cooling-ladder/<tree>`, whose **first segment under
`verification/runs/` is a CAMPAIGN NAME**. Verified: `F14-cooling-ladder` matches
neither `*_runs` nor `*_work`, and `*` does not cross a `/`, so **none of those
20 rules reaches a single one of the 9,720 files**. Batch 7 wrote that spelling
for exactly this batch; it is preserved, and no `**` rule was added.

### 4.1 THE ASSERTION, with stderr captured

`git check-ignore --no-index -v --non-matching --stdin`, exit 0, **stderr empty
on every invocation**. `--no-index` because the shared index is never read.

**Every file on disk under the six trees, both sides — 9,720 paths:**

| | before | after |
|---|---:|---:|
| ignored | **8,057** | **8,057** |
| not ignored | **1,663** | **1,663** |

and the twelve rules that fire, fire **at identical counts** at the new
spelling: 4,913 / 1,462 / 794 / 359 / 307 / 155 / 112 / 60 / 45 / 44 / 22 / 8.
The 1,663 not-ignored are exactly the 1,663 tracked files present on disk;
**0 tracked files are ignored** on either side.

**A `!` rule reports as a MATCH and means NOT IGNORED**, so the classification
splits on whether the reported pattern begins with `!` rather than on whether
`check-ignore` reported a line at all. Counting matches would have called 224
re-included `0.orig` files ignored.

**Whole-tree, both directions, as a Python set difference:**

```
whole tree, 67,706 files on disk
  BEFORE  ignored=59,522   not-ignored=8,184
  AFTER   ignored=59,522   not-ignored=8,184
  FILES NEWLY UN-IGNORED, WHOLE TREE:  0
  files newly ignored,   whole tree:   0
  per-file decision identical across the whole tree: True
```

The BEFORE side is computed in a **scratch git repository** holding HEAD's
`.gitignore` and HEAD's `verification/runs/R4_runs/.gitignore` — because
`check-ignore --no-index` evaluates path STRINGS, the before-decision can be
taken without restoring the live `.gitignore` and without racing a peer for it.
The path list is the live tree's, with destinations mapped back to sources.

`verification/runs/R4_runs/.gitignore` is a tracked nested ignore file; every
pattern in it is relative, so it travels inside its tree and needed no re-point.
**No R25 tree contains a nested `.gitignore` or `.gitattributes`, and none
contains a symlink** — checked, all three zero.

---

## 5. `exec_bits.OWNERS` — DECIDED, and the decision is "Cases" with NO NEW ROW

Batch 7 left this explicitly: *"ONE THING R25 WILL HAVE TO DECIDE RATHER THAN
INHERIT … 0 register entries are under `docs/campaigns/` today, so this is a
decision R25 must make and not one batch 7 has silently made."*

**Re-measured before deciding, not carried:** of the 255 paths in
`WAIVED_NO_EXEC_BIT` and the 4 in `REQUIRED_EXECUTABLE`, **0 are under
`docs/campaigns/`** — 0 under `docs/` at all. So **no path changes family
because of this move**, and there is no assignment to preserve.

**The decision: let the existing `verification/runs/` row answer — "Cases" — and
add no row.** Recorded in the comment at that row, with the reasoning:

* Batch 7 PRESERVED a family because **61 register entries** would otherwise
  have been relabelled by a mover. That is a repair. Here the number is **0**,
  so the same act would not be a repair; it would be an invention.
* The alternative — a `verification/runs/F14-cooling-ladder/` row reading
  "Infrastructure and Standards" — would have the mover carving a family
  boundary **inside** `verification/runs/`, where all 26 sibling trees are
  "Cases", on the strength of where these files used to live. Carving an
  exemption is a larger act than letting a uniform prefix rule apply.
* The substance agrees: a broken `run_cases.sh` in a cooling-ladder run tree is
  answered for by whoever answers for one in `4G_runs`.

**Asserted after the move:**

| | before | after |
|---|---:|---:|
| `missing_required` | 0 | **0** |
| `unregistered` | 33 | **33** |
| `stale_waivers` | **0** | **0** |
| `waived_by_owner` | Cases 61 / DAFoam 111 / Demo and website 26 / Infra 57 | **identical** |

`owner_of("verification/runs/F14-cooling-ladder/K0c_runs/x.sh")` returns
**"Cases"**, which is the decision in effect.

**Note on the 33.** 27 of the 33 `unregistered` findings are shebang scripts
inside the moved trees. They are `unregistered`, not waived, so `owner_of` is
never called on them and the OWNERS decision does not touch them; they are
reported at HEAD's spelling until HEAD catches up, which is `_spellings` working
as designed. The count is 33 on both sides.

---

## 6. `lab_paths` NEEDED NO EDIT — confirmed by execution, not assumed

`_R25 = re.compile(r"^docs/campaigns/([^/]+)/([^/]+_(?:runs|sensitivity))(/.*)?$")`
is a PATTERN, and a pattern reaches the four trees that landed after the ruling.
Confirmed by running it over the real corpus rather than over an example:

* `redirect()` over all **1,671** source paths: 1,671 map to
  `verification/runs/F14-cooling-ladder/…`, **0 unmapped**.
* `resolve()` over the same 1,671 before the move: **1,663 resolve**, and the
  8 that do not are precisely the 8 files another lane has deleted from the
  worktree and not committed. Not a defect; the same 8 everywhere in this record.
* `run_archive("K0c_runs", "F14-cooling-ladder")` returns the source before the
  move and the destination after it, and `run_archive("NO_SUCH_runs")` returns
  `None` — the must-not-match control.
* `MOVES` binds **two** of the six (`F14_K0C_RUNS`, `F14_K0B_MESH_SENSITIVITY`),
  and both moved `state()` from `legacy` to **`moved`** across this pass, which
  is the transition that says the batch ran.

**The other four were deliberately NOT added to `MOVES`.** They do not need
binding — the pattern answers for them — and adding four names would change G3's
bound-name set and therefore G3's reported output. A mover does not move a gate's
reading for its own convenience.

---

## 7. THE DEPTH-DERIVATION CLASS — searched properly, and R25 is DEPTH-PRESERVING

Batch 6 found 7 modules deriving a repository root by counting `parents[N]`;
batch 7 searched the idiom rather than the path and found **19**, of which 18
landed on `/home/ubuntu` after its move. The class has **no path literal in it**,
so no literal scan sees it.

**Searched the same way, over all 1,671 tracked files under the R25 sources, no
suffix filter, 0 unreadable.** Patterns: `parents[`, `parent.parent`, `../..`,
`dirname(dirname`, `resolve().parents`, `__file__`, `BASH_SOURCE`.
**20 files carry the idiom, at 7 root-derivation sites.**

**And all 7 are correct at the new path, proved by executing the expression
there.** The reason is structural and it is the finding of this section:

> **`docs/campaigns/` and `verification/runs/` are BOTH TWO SEGMENTS, so R25 is
> the first move in this map that does not change any file's depth.**

Asserted over the corpus, not argued: `p.count("/") == redirect(p).count("/")`
for **1,671 of 1,671** paths, **0 exceptions**.

| site | derivation | at the OLD path | at the NEW path |
|---|---|---|---|
| `K0b_mesh_sensitivity/analyse_k0b_mesh.py:48` | `join(HERE,"..","..","..","..")` | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |
| `K0b_mesh_sensitivity/build_and_run.sh:29` | `$HERE/../../../..` | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |
| `K0cT_runs/analyse_k0ct.py:69` | 4 × `..` | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |
| `K0c_runs/analyse_k0c.py:123` | 4 × `..` | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |
| `K2b_runs/analyse_k2b.py:55` | 4 × `..` | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |
| `K2b_runs/audit_k2b.sh:39` | `$HERE/../../../..` | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |
| `KV1_runs/mutate_advective.py:90` | **`_find_repo()` — already a SEARCH** | `/home/ubuntu/Certonomous` | **`/home/ubuntu/Certonomous`** |

**No repair was made, and that is a decision rather than an omission.** Six of
the seven count segments, and counting is the fragile form; but all six are
provably correct on both sides, and rewriting six correct expressions inside a
1,671-file move commit adds diff and risk to buy nothing this batch can measure.
The seventh already searches — `_find_repo` walks up for `scripts/heat_balance.py`
and `SystemExit`s rather than guessing — and its docstring records that a
hand-counted chain was wrong on its first run. **The standing recommendation
stands and is repeated in D403's "to settle": convert the six to a search, in a
batch that owns them, before a move that is NOT depth-preserving reaches them.**

---

## 8. THE ONE THING THE MOVE BROKE, AND NEITHER SCAN COULD SEE IT

`KV1_runs/mutate_advective.py:124`:

```python
SEALED_CASES = sorted(
    d for d in glob.glob(os.path.join(REPO, "docs", "campaigns",
                                      "F14-cooling-ladder", "K0c_runs", "*"))
    if os.path.isfile(os.path.join(d, "constant", "polyMesh", "boundary")))
```

**The substring `docs/campaigns` does not occur in that file.** The path is
assembled from segments, so the literal scan — which found 243 files under the
sources naming `docs/campaigns`, every one of them prose or a citation to a
document that STAYS — cannot match it. It counts no parents, so the depth scan
cannot match it either. **Two clean scans and a live breakage between them.**

It guards the sealed half of the advective-term mutation harness. Measured:
unrepaired at the new tree the glob returns **0** cases against
`SEALED_EXPECTED = 11`, so the harness `SystemExit`s — it fails closed, which is
that constant doing its job, but the harness is dead either way.

**A third scan shape found it: the TOKEN.** Searching repo-wide for the path's
segments as quoted tokens (`"campaigns"`, `"F14-cooling-ladder"`, `"K0c_runs"`,
and the other five tree names) returned exactly **two** files — this one, and
`sdk/tests/test_lab_paths.py:808`, whose fixture tree is synthetic and correctly
keeps its literals. That is L-137.

**Repaired by asking for the archive by name, not by spelling:**
`lab_paths.run_archive("K0c_runs", "F14-cooling-ladder")`, which probes every
spelling the map knows, prefers the successor, and REFUSES rather than returning
an empty corpus. Proved by execution at the new path: `_K0C_RUNS` resolves,
**`SEALED_CASES == 11 == SEALED_EXPECTED`** — the pre-move number restored —
`AUDITOR` and `RULES` exist and both `OPEN_CASES` exist. The operator-facing
REFUSE message's rebuild recipe is now derived from the same handle
(`os.path.relpath(_K0C_RUNS, REPO)`) so it cannot go stale separately.

**The must-not-match control**, without which a search that answered
"repository root" to everything would satisfy the repair: the repaired module
copied to a directory with no repository above it prints
`REFUSE: no scripts/heat_balance.py in any parent of …` and exits, rather than
returning a path.

---

## 9. INSTRUMENTS THAT CHANGED COUNT AS A SIDE EFFECT — one, found by running the gates

Batch 7 found five and the worst shrank a swept corpus by 2,367 surfaces, which
dropped two fault counts and looked exactly like improvement. Each was found by
RUNNING the gates, not by reading them, and the test of whether a change is a
repair or a loosening is the same: **does it restore the pre-move answer?**

### 9.1 `hand_carry.batch2_untrack_list` — 198 → **655**, in the direction that UNTRACKS MORE

`BATCH2_EXCLUSIONS` is `("demo-output/website/campaign/MESH_AUDIT_runs",
"docs/campaigns")` and it was matched against the tracked path by plain string
prefix. The moment the trees leave `docs/campaigns/`, the exclusion stops
matching and batch 2's own untrack list grows from **198 to 655** — **457 files
that a ruling of 2026-08-17 explicitly SPARED**, including the 65 solver logs the
constant's own comment says no repair removes.

**This is the `_spellings` class in a third instrument.** The exclusion is a
list of paths and a move invalidates one. The repair is batch 7's, applied
identically: the exclusion keeps the spelling its ruling was written with — it is
a dated ruling and re-writing it is not what makes it true — and the MATCH is
taught the map, probing `lab_paths.redirect` and `lab_paths.unredirect` for every
name the path has had or will have.

**Pinned by restoring a pre-move number, and fired in both directions:**

| | before the move | after the move |
|---|---:|---:|
| `batch2_untrack_list` unrepaired | 198 | **655** |
| `batch2_untrack_list` **repaired** | **198** | **198** |
| option B control, `exclusions=()` | 655 | **655** |
| `project_after_untracking` (goes dark) | 0 | **0** |

The repair changes **0** of the pre-move decisions, so it is not a loosening;
the repaired after-set is the before-set **mapped forward path for path**, not
merely the same size; and the option-B arm still takes all 655 candidates, so the
gate can still FAIL. A repair that made the gate unable to fail would read 198 in
both arms.

**It never moved a verdict** — `goes dark after batch 2` reads 0 either way,
which the constant's own comment predicted — so a verdict-list comparison could
not have seen it. It was found by diffing the derived COUNTS across the move.

### 9.2 Four instruments checked and NOT changed

* **`self_audit._tracked_files`** — batch 7's repair (read `git ls-tree -r HEAD`,
  resolve through `lab_paths`) already follows the map, and it does so for R25
  without further work: `placement words` reads **80** lab-record placements and
  `rank claims carry the right values` reads **35** more on lab records on both
  sides, which are batch 7's restored numbers. Had the frame regressed to
  `git ls-files`, they would have fallen to 45 and 14.
* **`exec_bits._spellings`** — already probes `lab_paths` both ways; the register
  is matched under the successor spelling and `stale_waivers` stays 0.
* **`hand_carry.tracked_paths`** — already reads HEAD, never the index.
* **`lab_paths`** — needed no edit (§6).

---

## 9.5 THE GATES, BOTH SIDES, WITH THEIR FINDING SETS

### `scripts/lab_check.py --no-tests`

| | before | after |
|---|---|---|
| verdict | **FAIL, exit 1, ran 20/20**, 316.0 s, **stderr empty** | **FAIL, exit 1, ran 20/20**, 314.6 s, **stderr empty** |
| verdict list | 7 FAIL + 1 BLOCKING UNKNOWN + 15 unrun | **BYTE-IDENTICAL, 25 lines, compared by `diff`** |

The seven FAILs are `check_belief_neutrality`, `check_pdf_surfaces`,
`check_proposal_surface_coverage`, `check_rung_attribution`, `contention_audit`,
`installed_registry`, `self_audit`; the BLOCKING UNKNOWN is
`check_absolutes.py: exit 3`; 15 unrun on both sides. **`diff` reports no
difference.**

**`self_audit`'s fifteen-line finding block is identical line for line, tier for
tier and NUMBER for number, with exactly one exception**, and the exception is
the one this batch is expected to move:

```
- [FAIL] cited evidence paths      439 of 1888  ->  440 of 1897
```

Everything else is unmoved — `rank claims carry the right values` at 4
travelling and **35** lab-record, `placement words` at **80** lab-record,
`campaign json citations` at 6 of 7, `bundle drift` at 9 behind the tree, all
eleven WARNs. **The 80 and the 35 are batch 7's restored numbers**: had
`self_audit._tracked_files` regressed to the index frame they would read 45 and
14, which is the defect that looks exactly like improvement.

### The citation guard — 440 of 1,897, and the delta is fully accounted for

| | before | after |
|---|---:|---:|
| repo-rooted citations | 1,888 | **1,897** |
| …that do not resolve | 439 | **440** |
| …of those, resolve under a spelling `lab_paths` knows | — | **431** |
| …**genuinely nowhere** | — | **9 occurrences over 5 distinct paths** |
| records swept | 375 | **382** |

**Both deltas are one cause, and it is a corpus that GREW.**
`verification/runs` is a `RECORD_ROOT` and `docs/campaigns` is not, so seven
`.md` records inside the moved trees entered the swept corpus:
`K0b_mesh_sensitivity/README.md`, and `README.md` + `GATE_TABLE.md` for each of
`K0c_runs`, `K0cT_runs` and `K2e_runs`. Measured directly, those seven contribute
**exactly 9 repo-rooted citations (the whole denominator delta) and exactly 1
unresolved (the whole numerator delta)** — `K0b_mesh_sensitivity/README.md:3`
citing `demo-output/website/campaign/THERMAL_K0_RESULTS.md`, which
`lab_paths.resolve()` finds at `verification/campaign/THERMAL_K0_RESULTS.md`, so
it joins the 431 and not the 9.

**This is the inverse of batch 7's worst finding and it is reported as one.**
There the swept corpus shrank by 2,367 surfaces in silence and two fault counts
FELL, which looks like improvement. Here it grew by 7 and lost 0 — every one of
the 375 pre-existing records is outside the move set and could not have left —
and the fault count ROSE by 1. A count that rises from a widened corpus is
coverage; a count that falls from a narrowed one is blindness. **The guard was
not adjusted**: it tests literal existence rather than asking the map, which is
why 431 of its 440 findings are renames it has not followed, and repairing that
is the resolver batch 9 lands.

**0 of the 440 unresolved citations names an R25 source or destination path.**

### The three standing gates

| gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B**, digests `1b53ed5a4e9d63cb` / `5519de4237b71ce4`, `walk_errors = 0` | **2 / 307 / 1,510,309,145 — BYTE-IDENTICAL**, same digests, `walk_errors = 0` |
| **G1** goes-dark-after-batch-2 | **0** | **0** |
| **G1** `batch2_untracked` | **198** | **198** (repaired; unrepaired it read 655 — §9.1) |
| **G1** rides-along | 824 trees / 8,035 files / 1,804,861,379 B | **0 / 0 / 0** — every one was an R25 tree and they are now at their destination |
| **G3** root binding | `UNRESOLVED = (EVIDENCE,)`, `AMBIGUOUS = (CAMPAIGN, RUNS)` | **identical** |
| **G3** R25 pair state | `F14_K0C_RUNS` / `F14_K0B_MESH_SENSITIVITY` = `legacy` | **`moved`** — the transition that says the batch ran |

**No gate was adjusted.** G1's `rides_along` going to zero is the correct end
state rather than a defect: it counts dark trees a future `git mv` will carry,
and after R25 there are none left in the map.

**G3's `AMBIGUOUS` does not move, and that is the non-trivial half.** `CAMPAIGN`
and `RUNS` still read `both` because `demo-output/website/campaign/` still holds
the served PNG that batch 8 owns. R25 neither creates nor clears an ambiguity.

### `pytest`

| | before | after |
|---|---|---|
| | **6 failed / 2,447 collected / 2 skipped**, 523 subtests, 1,206.7 s | **6 failed / 2,447 collected / 2 skipped**, 523 subtests, 1,203.5 s |

The six are the standing baseline and are the same six tests, in the same four
modules, with the same per-module counts: `test_exec_bits` 1
(`ThisRepositoryTests::test_no_shebang_script_is_both_unexecutable_and_unregistered`),
`test_fail_open_scan` 1
(`TheScanRefusesItsOwnDefectTests::test_the_repo_scan_carries_frame_filter_and_commit`),
`test_installed_matches_tracked` 3
(`InstalledMatchesTrackedTests::test_no_registered_artifact_has_drifted_from_its_tracked_copy`,
`PendingInstallWaiversTests::test_no_pending_install_waiver_has_quietly_stopped_excusing_anything`,
`EveryFindingTheRunPrintsReachesTheExitCode::test_main_ACTUALLY_consumes_the_rule_and_not_just_prints_it`),
`test_pdf_surfaces` 1
(`TestFindsTheStaleArtifactByName::test_report_pdf_is_named_as_outliving_its_named_source`).

**THE TWO SKIPS ARE NAMED RATHER THAN LEFT BEHIND A COUNT**, because batch 5
lost 46 tests behind one such line while its failing-module list got shorter.
They are `sdk/tests/test_hand_carry.py::TheBatch2GateOnTheLiveTree::`
**`test_the_live_gate_reads_zero_under_the_ruled_option`** (:618) and
**`test_the_live_gate_reads_one_when_the_exclusion_is_dropped`** (:623), both
skipping on *"`demo-output/website/campaign/MESH_AUDIT_runs` holds no tracked
file at HEAD: batch 2 or batch 7 has since run and this plant is spent"*. They
are batch 7's spent plant, skipped on both sides of this batch, and **this batch
did not put them there and did not take them away** — which matters, because
§9.1 repairs the very function those two tests fire in both directions. The
option-B arm of that repair was therefore fired by hand and reads all 655
candidates.

**Nothing left the suite**: 2,447 collected and 523 subtests on both sides. R25
moves nothing into or out of `scripts/` or `sdk/tests/`, so the candidate
universe does not move at all.

---

## 10. WHAT WAS NOT DONE, AND WHY

### 10.1 `_SHIPPING_RE` is not re-pointed, and `check_absolutes.py` is byte-identical to HEAD

```
_SHIPPING_RE = re.compile(r"^(?:demo-output/website/|.*/latex/|.*\.tex$)")
```

still names the webroot, which is correct: batch 8 is the commit that creates
`web/`, and re-pointing this ahead of it would make the shipping-surface score
name a root that does not exist. **`sha256(scripts/check_absolutes.py)` is
`8c06a3b4050722a3745cc23afe22dbc400b60fe29f655fbfebe4040c3dbdfa3d` on disk and
the same for `git show HEAD:scripts/check_absolutes.py`** — the whole file,
byte-identical, not merely the one line.

### 10.2 Two defects found by this pass, DOCKETED rather than fixed

**(a) The K0b mesh-sensitivity rung has been unrunnable since batch 7** —
`K0b_mesh_sensitivity/build_and_run.sh:29` and `analyse_k0b_mesh.py:49` both name
`demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5`, which R20 moved
to `verification/runs/THERMAL_K0_runs/` in batch 7. Proved by execution at the
pre-R25 tree: the shell guard is FALSE and the script exits 2 with
*"REFUSE: K0b source case not found"*, and `os.path.isdir(K0B_64)` is `False`
while the successor exists with 12 tracked files. `K0B_64` is the **64x64 rung
of a three-rung mesh ladder**, so two of the ladder's three points cannot be
assembled. **Not R25's defect and not repaired by R25**: it predates this move,
both files fail identically before and after it, and batch 7's own precedent for
fixing a foreign residue in flight (§6.2) turned on the repair being unprovable
otherwise, which does not hold here. Filed as **D403**, with the repair named.

**(b) A stale line citation in an operator-facing REFUSE message.**
`mutate_advective.py` tells the operator that `constant/polyMesh/` is untracked
"(.gitignore:60)"; the rule is `**/constant/polyMesh/` at **`.gitignore:66`**.
Pre-existing, cosmetic, inside a string this batch otherwise rewrites — and left
alone precisely because "inside a string I am already editing" is not a reason,
and a line number that drifts is the class this record has already re-derived
once (§4).

### 10.3 The rest

No other rule was executed. No file outside the six trees was moved, renamed,
copied or deleted. The hand-carry was not run. No shell script was converted.
No solver was launched. `docs/LOCATIONS.md` is still owed from batch 2.
**Git's rename inference is never quoted in this record**, and
`git status --porcelain` was not used for any measurement — it is reporting
another lane's staged renames on this tree and is useless here.

---

## 11. METHOD

- Every path-derived count is over `git ls-tree -r HEAD` at a named commit,
  **never `git ls-files`**. The shared index was not read for any measurement
  and not written by any step.
- **stderr was captured on every walk, every `git` invocation and every
  subprocess**, including all six `mv` calls, which were checked for a non-empty
  **stdout** as well as a non-empty stderr and a non-zero exit. All six: exit 0,
  0 bytes stdout, 0 bytes stderr.
- **No count was piped into `head`.**
- Path comparisons are **Python set comparisons plus a byte total**, with a
  sha256 of the sorted relative-path set as a **third witness** — never a digest
  alone.
- The measurement walker **raises** on any walk or stat failure; all twelve
  directory measurements reported 0 errors.
- The **inverse `mv` list was written before the batch started**, six lines plus
  the `rmdir`, reverse order, and it is an `mv` list and not `git reset --hard`.
- The sources were **re-measured immediately before the move** against the
  opening snapshot, with an abort on any drift: **0 of 6 trees drifted.**
- Every `.gitignore`, module and docstring edit is an exact-string replacement
  with an expected count, applied by a script that **writes nothing at all
  unless every one of its 21 entries matches**, and which compiles every
  rewritten Python source before keeping it.
- **Every file this batch edits was checked against HEAD's blob plus this
  batch's edits immediately before the commit was built** — not `cmp` against
  HEAD, which is supposed to differ. The detector takes HEAD's blob, applies the
  edit list to it, and compares with the worktree, which distinguishes "my edit
  is still there" from "a peer replaced the file".
- The next free lesson and docket ID are **re-derived per commit attempt** by ID
  **set** comparison with a period-anchored regex, and the write asserts that the
  set grew by exactly the one new id and that nothing was removed.
