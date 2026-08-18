# MOVE_MAP batch 4 — the first batch that moves files, and the rule that could not be executed because it was only ever counted

**857 tracked files moved by 23 `git mv` invocations, every one naming a
DIRECTORY where the source is a directory, one source per invocation, stderr
captured and empty on all 23.** Nothing was deleted. Nothing was untracked. The
`.gitignore` was not edited and did not need to be — measured, §4.3. The
**shared index was not written**: `git mv` ran under a private
`GIT_INDEX_FILE`, which was demonstrated in a scratch repository rather than
assumed (§6.1).

**Anchor `5d1b41a0`, 7,078 tracked paths** over `git ls-tree -r -z --name-only
HEAD`, never `git ls-files`. stderr was captured on every walk and every `git`
invocation and was empty on all of them. No count was piped into `head`. HEAD
did not move during the pass; the CAS was made against `5d1b41a0` and the
anchor was re-read immediately before the commit.

**Inherited, not re-decided.** Option A for `MESH_AUDIT_runs` and
`docs/campaigns`; R25 with the campaign segment preserved; the hand-carry
destinations. This pass ratifies none of them.

---

## 1. What moved, re-derived rather than carried

`MOVE_MAP_2026-08-16.md` §9 prices batch 4 at **872 files at `4d7c195a`**.
Re-derived at `5d1b41a0` by running `lab_paths.redirect()` over every tracked
path and keeping the ones whose successor is under `media/`, `ops/` or R1's two
`docs/` targets:

| Rule | Source → destination | files |
|---|---|---:|
| R11 | `demo-output/plots/` → `media/plots/` | **752** |
| R10 | `demo-output/{acts,gui-proof,fallbacks}/` → `media/` | 41 + 32 + 4 = **77** |
| R12 | 10 loose `demo-output/*.png` → `media/` | **10** |
| R2 | `FILMING_COMMANDS.md`, `LAPTOP_SHOOT.md` → `media/` | **2** |
| R8 | `scripts/installed/`, `scripts/laptop_bundle/` → `ops/` | 7 + 4 = **11** |
| R6 | `docs/aws/` → `ops/aws/` | **1** |
| R19 | `demo-output/website/paraview/` → `ops/paraview/` | **1** |
| R1 | `LESSONS.md`, `LOCATIONS.md`, `AWS_TREE_PLAN.md` → `docs/` | **3** |
| | **executed** | **857** |
| R8 | *"+ 15 named launchers"* → `ops/` | **15 — NOT EXECUTED, §2** |
| | **the map's 872** | 857 + 15 |

857 + 15 = 872 exactly, at a frame four commits and two untracking batches away
from the one the map measured at. The batch-4 population is one of the few
figures in this plan that has **not** drifted, and the reason is that none of
its rules reaches a run archive: batches 1 and 2 untracked 14,353 files, all of
them solver output under `campaign/` and `dafoam/`, and batch 4 owns none of it.

### 1.1 Two figures that HAVE drifted, re-derived here because the plan says to

| | as recorded | at `5d1b41a0` | direction |
|---|---:|---:|---|
| **R25** | 315 (`4d7c195a`), then 490 (`b8c398a4`) | **490** — `K0c_runs` 274, `K0b_mesh_sensitivity` 41, `KV1_runs` 175 | confirms `b8c398a4` |
| **batch 7** (R20+R21+R24+R25) | **8,643** (`4d7c195a`) | **2,854** — R20 2,083, R25 490, R21 274, R24 7 | **stale HIGH by 3×** |
| **move subtotal** | **13,511** (`4d7c195a`) | **6,270** | **stale HIGH by 2.2×** |

**D366 recorded these two as *stale small*, and at the moment it was written
that was right** — R25 had grown by 175 files and nothing else had moved. What
has happened since is larger and pushes the other way: **batch 2 untracked
7,403 files, the great majority of them under `campaign/*_runs/`, which is
R20's population.** The net is that batch 7 is now a third of its recorded
size. Both corrections are real; they have opposite signs, and the one that
dominates is not the one on the docket. This is L-109's shape again — the rule
is what was ratified, the count is what drifts — and it is recorded here rather
than left for whoever runs batch 7 to rediscover.

---

## 2. THE FINDING — R8's fifteen launchers are named nowhere, and the batch-4 hazard is inside that set

`MOVE_MAP_2026-08-16.md` §2.2 prices **R8 at 26 files**:
`scripts/{installed,laptop_bundle}/**` **plus 15 named launchers**. Measured at
`5d1b41a0`, the two directories hold **11** tracked files, so 11 + 15 = 26 and
the rule closes to the file — as does batch 4's own 872 = 857 + 15.

**There is no list of the 15.** Searched, and each search is a negative result
rather than an impression:

- **`scripts/lab_paths.py`** implements R8 as two table rows and nothing else.
  `redirect("scripts/demo_servers.sh")` and `redirect("scripts/auto-stop.sh")`
  both return `None`.
- **`MOVE_MAP_2026-08-16.md`** mentions launchers in four places — §1's tree
  sketch, §2.2's cell, §5.2's two out-of-tree items — and enumerates none.
  `demo_servers.sh` and `auto-stop.sh` are the only two named anywhere, and
  they are named in prose about the crontab, not in a move list.
- **`MOVE_MAP_EXECUTION_2026-08-17.md`** inherits the count and does not
  enumerate.
- **`docs/PHASE2_MOVE_MAP.tsv`** does enumerate — it moves **all** of
  `scripts/` to `ops/`, which is the F1 plan superseded at batch 0 precisely
  because `/scripts/` is retained. It is marked `DO NOT EXECUTE ANY ROW BELOW`.
- **The tree itself** holds 12 top-level `scripts/*.sh`. At most seven read as
  launcher, keepalive or preflight under any reading; the other eight of the
  fifteen would have to be `*.py`, and no line anywhere says which.

**The arithmetic is what hid it.** Every reconciliation this map has run closed
at zero unclassified, because 26 is consistent with 11 + 15 whatever the 15
are. A subtotal that closes proves the counts agree with each other; it says
nothing about whether the population can be *named*, and a batch is executed by
naming files. That is `LESSONS.md` L-111, and it is L-94's *"the class needs a
membership list, not a shape"* one level up — there the shape could at least be
run and inspected; here there is no shape at all, only a cardinal.

### 2.1 The handling: a stated scope reduction, in the safe direction

The 15 are **not moved**, and batch 4 is 857 files rather than 872. This is the
same disposition batch 2 made of its §3.1(c) 198 files, for the same reason and
after the same kind of finding: *"having just caught the classifier untracking
initial conditions, untracking 198 more files on the same classifier's verdict
would be repeating the error rather than learning from it."* Nothing is lost by
deferring — the files stay where every constant already resolves them.

### 2.2 AND THIS IS THE HAZARD THE PLAN PUTS IN BATCH 4, SO IT IS SAID PLAINLY

`MOVE_MAP_EXECUTION_2026-08-17.md` §4 calls batch 4 *"the one batch whose
incompleteness is not visible from inside the repository"*, because the live
`@reboot` crontab entry invokes `/home/ubuntu/Certonomous/scripts/demo_servers.sh`
and R8 moves that script to `ops/`.

**`demo_servers.sh` is one of the 15. It did not move. The crontab does not
dangle, and the hazard is DEFERRED WITH THE LAUNCHER SET, NOT DISCHARGED.**
Whoever moves the 15 inherits it, together with §5 Class 1's
`demo_servers.sh:46` `--directory` re-point, which belongs to batch 8.

The plan's second out-of-tree batch-4 item — *"`/usr/local/bin/auto-stop.sh`
re-installed via `installed_registry.py`"* — was **not done, and it is not the
fleet's to do.** `scripts/installed_registry.py:245-266` registers that pair
`PendingInstall` with `owner="Katie / Sanaa (docket A4)"` and an expiry of
2026-08-21, and the tracked `ops/installed/certonomous-lab-check.cron` says the
same of its own install command in as many words: *"That is Katie's or Sanaa's
command, not the fleet's."* The re-install was in batch 4 only because R8 moves
`auto-stop.sh`; `auto-stop.sh` did not move, so there is nothing to re-install,
and doing it anyway would have crossed the boundary that register exists to
hold. Registry state, unchanged by this batch: the auto-stop pair reads
**MATCH** with a **STALE waiver** — the fix has since been installed by its
owner and the waiver now excuses nothing.

---

## 3. The crontab, verified by executing what each line invokes

The crontab holds **three** entries, not the one §5.2 describes. The two added
2026-08-17 refresh `/home/ubuntu/Certonomous/.autostop-hold`, and they are what
keeps this box powered on.

```
@reboot sleep 30 && /home/ubuntu/Certonomous/scripts/demo_servers.sh
0 */6 * * *      touch /home/ubuntu/Certonomous/.autostop-hold
@reboot sleep 20 && touch /home/ubuntu/Certonomous/.autostop-hold
```

**Read-back is not verification.** A path that reads correctly can still name a
file that is gone, and a path that reads wrong can still work. So each line's
command was **executed**, before the batch and again after it:

| Line | executed | before | after |
|---|---|---|---|
| 1 | `/home/ubuntu/Certonomous/scripts/demo_servers.sh` | rc 0; 8765 and 8080 already listening, logged | rc 0; both still listening, logged |
| 2 | `touch …/.autostop-hold` | rc 0; mtime advanced | rc 0; mtime advanced |
| 3 | identical command to line 2 | rc 0 | rc 0 |

`demo_servers.sh` is idempotent by construction — it starts only a server that
is not already listening — so re-running it is safe and its own log line
(`control room already listening on 8765`) is the evidence that it ran and
decided. The file it invokes is **still at `scripts/demo_servers.sh`**, §2.2.

`crontab -l` was not edited. The tracked copy moved with its directory —
`scripts/installed/crontab.ubuntu` → `ops/installed/crontab.ubuntu` — and its
registry entry moved with it (§4.2). That copy is **5 lines behind the live
crontab**, which is the standing `DRIFT ubuntu crontab` finding
`installed_registry.py` reports, owned by the box's owner, and unchanged by
this batch in either direction.

---

## 4. How the moves were made, and what was proved about them

### 4.1 Granularity, and the proof on both sides

Eight of the 23 sources are **directories** and each went by exactly one
`git mv` naming the directory. The remaining 15 are **individual files** — R1's
three, R2's two and R12's ten loose PNGs — which have no directory to name and
can carry nothing.

For every directory source, `scripts/hand_carry.py`'s `measure()` was run
against the source immediately before the move and the destination immediately
after: file count, byte total, and the **sha256 of the sorted relative-path
set**. `measure()` walks with an explicit `onerror` and **raises** rather than
returning a short number, which is the repair D-recorded today after it was
found swallowing `OSError`. All 23 measurements reported `walk_errors = 0`.

| Source → destination | files | bytes | sorted path-set sha256 (16) | destination |
|---|---:|---:|---|---|
| `demo-output/plots` → `media/plots` | 752 | 70,087,637 | `1be311a8ba298828` | **identical** |
| `demo-output/acts` → `media/acts` | 41 | 7,798,376 | `6f34cab5792391b0` | **identical** |
| `demo-output/gui-proof` → `media/gui-proof` | 32 | 7,059,040 | `dd47c7b78791a45d` | **identical** |
| `demo-output/fallbacks` → `media/fallbacks` | 4 | 1,028,265 | `19126e3120f85739` | **identical** |
| `demo-output/website/paraview` → `ops/paraview` | 1 | 15,186 | `6d8926c39e42d9e3` | **identical** |
| `docs/aws` → `ops/aws` | 1 | 2,667 | `c8719e3915d76118` | **identical** |
| `scripts/installed` → `ops/installed` | 7 | 30,823 | `b24225ea19a81c44` | **identical** |
| `scripts/laptop_bundle` → `ops/laptop_bundle` | 4 | 13,005 | `c59ff3adc11aeb2f` | **identical** |

Every source directory is **gone** after its move, and every destination holds
**exactly the source's sorted path set** — asserted as a set comparison, not
only as a digest, and not only as a count. Two trees can share a count and a
byte total and have nothing else in common.

**Total on disk: 857 files, 88,166,353 bytes.**

### 4.2 THE RIDE-ALONG INVARIANT IS NOT EXERCISED BY THIS BATCH, AND THAT IS A MEASUREMENT

The invariant on batches 4–7 is that gitignored content rides along on a
directory rename and a per-file loop leaves it behind. At this frame that is
worth **1,709 → 2,334 dark trees / 14,269,950,892 bytes** repository-wide, with
R25 bound.

**None of it is under a batch-4 source.** Every one of the eight source
directories has an on-disk file count exactly equal to its tracked file count
(752/752, 41/41, 32/32, 4/4, 1/1, 1/1, 7/7, 4/4), and
`hand_carry.derive()`'s four buckets at `5d1b41a0` contain **zero** rows whose
source is at or under any batch-4 source. So a per-file `git mv` loop would
have lost nothing here, and stating that is more useful than claiming a
protection this batch did not need.

Directory granularity was used anyway, for the reason §9 of the plan gives —
*"the mechanics are proven on 871 files before they are trusted with 8,216"* —
and the mechanism itself was demonstrated in a scratch repository rather than
argued: a `git mv` of a directory holding one tracked file and one gitignored
sibling moved **both**, and left the shared index untouched (§6.1).

### 4.3 `.gitignore`: nothing to re-point, and it was measured

`hand_carry.gitignore_repoint()` reports ignore patterns naming a moved tree by
its old path. It names none of batch 4's, and the direct check agrees: all
**857 destination paths** were passed through
`git check-ignore --no-index --stdin`, and **0 are ignored**, stderr empty. The
only `paraview` lines in `.gitignore` (`:20-21`) are filename patterns
(`paraview.*.btr`) and are path-independent.

---

## 5. What had to land in the same commit, and why each one is not optional

`MOVE_MAP_EXECUTION_2026-08-17.md` §5 Class 1 is *"every line that must land in
the commit that moves the file it names, or a live surface breaks between
commits"*. Batch 4's Class 1 set was derived by scanning **every tracked
`*.py`, `*.sh`, `*.ps1`, `*.cron`, `*.json`, `*.yaml`** for a literal naming
any batch-4 source, then classifying each hit as prose, docstring citation, or
a path the process actually uses.

| File | What it named | Why it could not wait |
|---|---|---|
| `scripts/lab_paths.py` | **R1 had no row for `AWS_TREE_PLAN.md`** | RULING 2 put it in R1 in `MOVE_MAP_2026-08-16.md` §2.6 and the table was never given the row, so `redirect()` returned `None` for a file the map counts. The **same defect class as R16/R17 in batch 3**: a rule ratified in a record and not bound in the module is a rule the mover does not have |
| `scripts/corpus_figures.py` | `_read("LESSONS.md")` and the `rel == "LESSONS.md"` exclusion | `_read` returns `""` for a file that is not there, so every lesson figure would have come back a **clean zero** — and `lab_check.py` classifies this module `cannot-fail` and never runs it, so no suite could have caught it. D367's class exactly |
| `scripts/installed_registry.py` | 7 `tracked=` paths and their `reinstall=` commands | the registry **is** the pairs; a `tracked=` naming a file that is gone makes every gate it feeds read ABSENT for a reason that is not true |
| `sdk/chief_engineer/exec_bits.py` | 3 waived paths, and `OWNERS` had no `ops/` prefix | a waived path that no longer exists is `stale_waivers`, its successor is `unregistered`, and `owner_of()` returns `UNASSIGNED` — **six findings and one reddened test for three files whose content did not change** |
| `scripts/self_audit.py:6567` | `Path("scripts/laptop_bundle")` in `_BUNDLE_VERBATIM` | the bundle-drift check would compare the shipped zip against a source directory that is not there |
| `sdk/tests/test_pdf_surfaces.py:36` | `demo-output/acts/round3/naca_certificate.pdf` | a clean-PDF control that names a path that does not exist is not a control |
| `ops/installed/certonomous-lab-check.cron` | its own install command | the file's one purpose is to be installed by the command written inside it |
| `scripts/demo_servers.sh:25` | a comment citing `docs/aws/provision.sh` | citation hygiene; not load-bearing, and said so |

**`scripts/check_absolutes.py:743`'s `_SHIPPING_RE` was NOT touched, and this
is the batch that had to decide.** Its post-move form is
`^(?:web/|.*/latex/|.*\.tex$)` and §5 Class 2 requires it to land *in the MOVE
commit and not before*. **Batch 4 does not create `web/`** — R13, the served
set, is batch 8 — so an alternative added here would be a rule matching
nothing, which is the exact reason the clause says *not before*. The file is
**byte-identical to HEAD**, confirmed by `cmp` against `HEAD:`'s blob, and it
stays queued for batch 8.

### 5.1 One test was amended, and it was amended because it was right

`test_sweep_roots_reproduces_self_audit_4309_before_the_move` pinned
`SWEEP_ROOTS()` to **equality** with the seven roots `self_audit.py:4309`
whitelisted at `4d7c195a`. Batch 4 creates `media/` and `ops/`, and
`SWEEP_ROOTS()` emits a destination root the moment it exists — which is the
whole point of the function, because a citation written after the move has to
resolve while one written before it still does. **Equality was the wrong pin:
it reddens on the function working**, and batch 4 is the first batch that could
find that out.

What is load-bearing is that a root never **leaves**: a whitelist that silently
shrinks is `check_evidence_paths_exist` scanning fewer documents and passing,
which is this corpus's most repeated failure. So the test now asserts the seven
are all still present and in order, that anything added is a real directory on
disk **and** some rule's destination, and a **must-not-match control** asserts
that `web/`, `cases/`, `research/`, `verification/` and `evidence/` — none of
which exists until batches 5 to 8 — are never emitted.

Fired against planted mutants in a symlink mirror of the repository, so the
mutated module's `REPO` still resolves to this tree (the first harness put the
copy in a scratch directory, `SWEEP_ROOTS()` returned `()`, and **all tests
reddened identically under every mutant** — a table that discriminates nothing,
which is what a false red looks like, and it is batch 2 §2.1's finding
recurring):

| Mutant | `never_loses_one_of_the_seven` | the must-not-match control |
|---|---|---|
| the module as committed | green | green |
| `docs/` silently leaves the whitelist | **RED** | green |
| emits every root whether or not it exists | **RED** (`extra='ops/'` and the absent roots) | **RED** |

---

## 6. The commit form

### 6.1 `git mv` under a private index — demonstrated, not assumed

`git mv` writes an index, and the shared `.git/index` on this box is read by
every agent. It also honours `GIT_INDEX_FILE`. Both facts were checked in a
scratch repository before being used here: with `GIT_INDEX_FILE` exported and
seeded by `git read-tree HEAD`, `git mv src/dir dst/dir`

- **renamed the directory on disk**, and the **gitignored sibling `x.log`
  travelled with it** — the ride-along property, executed rather than argued;
- staged `R100 src/dir/a.txt → dst/dir/a.txt` in the **private** index;
- left the **shared index still listing `src/dir/a.txt`**, verified by reading
  it back under `env -u GIT_INDEX_FILE`.

So all 23 `git mv` invocations ran under the private index, and the shared
index was **neither read into the commit nor written**.

### 6.2 The consequence, stated rather than left to be discovered

The shared index now holds **857 entries at the old paths**, exactly as batch 2
left 7,386 stale entries and recorded them as owed. Under the two mandated
commit forms this is inert: the pathspec form builds a temporary index from
HEAD plus the author's own worktree paths, and the private-index form never
invokes `git commit` at all. What it does affect is a **bare** `git commit`,
which `ops/installed/pre-commit` refuses by name and by path — which is what
that hook is for. The surgical cleanup §8.5 mandates (`git update-index
--force-remove --stdin` over **only this agent's paths**) was **not run**,
because this pass was directed not to write the shared index; it is filed as
owed, with the paths recoverable from this record's move list.

### 6.3 The append-only merge, per D369

`docs/LESSONS.md`, `docs/LOCATIONS.md` and `docs/DOCKET.md` were **diffed
against HEAD's blobs for worktree-only lines before anything was written**:
**0 in all three**, so the restore-from-HEAD form is safe here and no unlanded
tail exists to be destroyed. The next free ids were re-derived at the commit
attempt by comparing **id sets** under a period-anchored regex — `L` set 109
ids, max 110, **L-111 free**; `D` set 368 ids, max 369, **D370 free** — not by
reading the bottom of the file.

---

## 7. The gates, both sides, with their finding sets

### 7.1 `scripts/lab_check.py --no-tests` and the full suite

Before, at `5d1b41a0`: `--no-tests` **FAIL, exit 1, ran 20/20**, 297.7 s,
stderr empty. Full run **FAIL, exit 1, ran 21/21**, 1,529.0 s, stderr empty.

| Check | before | after |
|---|---|---|
| `scripts/check_pdf_surfaces.py` | FAIL | FAIL |
| `scripts/check_proposal_surface_coverage.py` | FAIL | FAIL |
| `scripts/check_rung_attribution.py` | FAIL | FAIL |
| `scripts/contention_audit.py` | FAIL | FAIL |
| `scripts/installed_registry.py` | FAIL | FAIL |
| `scripts/self_audit.py` | FAIL | FAIL |
| `scripts/check_absolutes.py` | **BLOCKING UNKNOWN, exit 3** | **BLOCKING UNKNOWN, exit 3** |
| the other 13 | PASS | PASS |
| `sdk/tests` (pytest) | **6 failed / 2,442 collected** | see the report accompanying this commit |

The six suite failures before are `test_exec_bits` 1, `test_fail_open_scan` 1,
`test_installed_matches_tracked` 3, `test_pdf_surfaces` 1 — the standing
baseline, unchanged.

**Two frame numbers move and neither is a verdict.** `lab_check.py`'s candidate
enumeration walks `scripts/` and `sdk/tests/` recursively, so moving
`scripts/{installed,laptop_bundle}/` out of `scripts/` removes 11 paths from
the candidate universe: `candidates 190` falls by 11 and `skipped 78` falls by
the same 11. **`admitted` is unchanged at 112 (20 script gates, 92 test
files)** — none of the eleven was ever admitted; they were skipped as *not an
executable module*, *shell* or *cannot-fail*. A count that falls because the
population fell is not a check going quiet, and the two are told apart by the
admitted count rather than by argument.

### 7.2 The three standing gates

| Gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B**, digests `1b53ed5a…` / `5519de42…` | **byte-identical**, same two trees, same 307 files, same digests |
| **G1** rides-along | 2,334 trees, 45,770 files, 14,269,950,892 B | **identical** |
| **G2** control corpora | 223 path fields, 0 unresolved | **223, 0** |
| **G3** root binding | `roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (CLOSURE, CLOSURE_DATA, CLOSURE_MD, CLOSURE_PLOTS, EVIDENCE)` | **same** |

**G1 was computed against the projected post-batch tracked set before the
commit**, by applying batch 4's own rename map to HEAD's 7,078 paths and
handing the result to `derive()` — the same projection instrument batch 2 used
— so the carry set was known not to grow before the ref moved, and again
afterwards against the real HEAD.

**G2 was fired three ways**, because a count alone cannot show a corpus is
still discriminating: a citation that must resolve does
(`demo-output/website/closure.html`); one to a document that never existed
returns `None`; and — the arm this batch adds —
`demo-output/plots/C_d/frame_0001.png`, a path **this batch moved**, resolves
at `media/plots/C_d/frame_0001.png`. That third arm is the pair-binding of
`lab_paths` doing the thing the whole reorganisation depends on, measured on a
path that actually moved rather than on a synthetic one.

**G3's five `UNRESOLVED` names are the destination-only ones** — the
`research/closure/` family and `evidence/`, which batches 5 and 7H assemble.
`AMBIGUOUS` is empty **after** the move as well as before, which is the
non-trivial half: every batch-4 name now reports `state() == "moved"`, and none
reports `"both"`.

---

## 8. WHAT BREAKS IF BATCH 4 LANDS AND BATCH 5 NEVER DOES

**Nothing breaks, and for once that is not the whole answer, because batch 4 is
the first batch that can leave something wrong in the filesystem rather than in
a table.**

1. **The tree acquires two roots that hold only leaves.** `media/` holds 841
   files and `ops/` 13, and neither is referenced by anything the map has not
   already re-pointed. `demo-output/` still exists and still holds the whole
   webroot; `scripts/` still holds every check. A reader arriving at `media/`
   finds exactly what §1's target tree says should be there, which is not true
   of `research/closure/` after batch 5 stops half-way. **Batch 4 is the only
   move batch whose partial state is not misleading**, because its rules are
   leaves: no rule splits a directory, no rule merges two, and every
   destination is complete the moment it exists.

2. **`lab_paths` now answers `moved` for 857 files and `legacy` for the rest,
   and both are right.** That is the property batch 3 was built for, and batch 4
   is the first evidence that it holds against a real rename rather than a test
   fixture. Every one of the 223 control-corpus citations still resolves.

3. **R8 is half-executed and the half that is missing is the half with the
   out-of-tree dependency.** §2. This is the one thing batch 4 leaves worse than
   it found it in one narrow sense: the map's R8 = 26 now describes a rule of
   which 11 have moved and 15 cannot be named. Whoever rules the membership list
   inherits the crontab line, the `--directory` re-point and the auto-stop
   re-install together, and D370 says so.

4. **The shared index is 857 entries staler.** §6.2.

**And one thing that does not change, deliberately.**
`check_absolutes.py:743`'s `_SHIPPING_RE` still names `demo-output/website/`.
Batch 4 does not create `web/`, so that is still correct; it is queued for the
commit that does, and this batch confirmed it byte-identical to HEAD rather
than assuming it.

---

## 9. Method

- Every path-derived count is over `git ls-tree -r -z --name-only 5d1b41a0`,
  7,078 paths. Never `git ls-files`; the shared index was not read for any
  measurement and not written by any step.
- **stderr was captured on every walk, every `git` invocation and every
  subprocess** and was empty on all of them, including all 23 `git mv` calls,
  which were checked for a non-empty stderr as well as for a non-zero exit.
- **No count was piped into `head`.**
- Every before/after pair passes through the same instrument in the same frame.
  The path-set comparison is a set comparison and a digest, never a count.
- `measure()` **raises** on any walk or stat failure rather than returning a
  smaller number, and every one of the 23 measurements reported
  `walk_errors = 0`.
- The inverse `mv` list was written **before** the batch started, as §9 of the
  plan requires, and is reproduced by reversing §4.1's table.
- Nothing here is ordered or selected by a date.
- This record does not appear in its own results: every measurement was taken
  before the commit that lands it.

## 10. What batch 4 did not do

No file was deleted or untracked; nothing left the disk. `.gitignore` was not
edited (§4.3 measured that it did not need to be). The shared index was not
written, and its pre-existing state was not reverted. `_SHIPPING_RE` was not
touched. R8's 15 launchers were not moved and no membership list was invented
for them (§2). `/usr/local/bin/auto-stop.sh` was not re-installed and the
crontab was not edited (§2.2, §3). The 198 files of batch 2's §3.1(c), the 78
of §3.1(a) and the 109 of §3.1(b) remain tracked. `LOCATIONS.md` was moved to
`docs/` and **not updated**; it is still owed from batch 2. No solver was
launched and nothing was registered.
