# MOVE_MAP batch 5 — R23's many-to-one merge ratified by measuring what flattening it would destroy, three rules that were written down and never bound, and forty-six tests that left the suite behind a single `skipped` line

**437 tracked files moved by 54 `git mv` invocations — 11 naming a DIRECTORY
where the source is a directory, 43 naming a loose file that has no directory to
name — one source per invocation, stderr captured and empty on all 54, exit 0 on
all 54.** Nothing was deleted. Nothing was untracked. `.gitignore` was not edited
and did not need to be: all **437 destination paths** were passed through
`git check-ignore --no-index --stdin` and **0 are ignored**, stderr empty. The
**shared index was neither read nor written**.

**Anchors, and HEAD moved three times under this pass.** It opened at
**`8c57d2a0`**, 7,079 tracked paths over `git ls-tree -r -z --name-only HEAD`,
never `git ls-files`. Three peer commits landed while it ran:

| | | touches a batch-5 source? | tracked |
|---|---|---|---:|
| `7a98c33d` | batch 4's forward repair of D371 | **no** | 7,079 |
| `99e30ea4` | batch 4's record, final gate numbers | **no** | 7,079 |
| `4d87c58e` | L-113 | **no** | 7,079 |

**Every one of the 437 sources is still in HEAD at `4d87c58e`, and none of the
three commits names one** — checked by set difference against
`git ls-tree -r HEAD`, not by reading a diff. The moves were made at
`7a98c33d`; the commit is built against whatever HEAD is observed at the moment
it is built, with the index reconstructed from THAT commit's `(mode, blob)`
entries rather than reused from the one `git mv` wrote, so a peer commit landing
between the move and the commit cannot be reverted by this one. `7a98c33d`'s
five executable files were already in the worktree the before-suite read,
verified by `cmp` against its blobs: all five byte-identical, so the before frame
and `7a98c33d` are the same content.

stderr was captured on every walk, every `git` invocation and every subprocess
and was empty on all of them. No count was piped into `head`.

**Inherited, not re-decided.** Option A for `MESH_AUDIT_runs` and
`docs/campaigns`; R25 with the campaign segment preserved; the hand-carry
destinations; `AWS_TREE_PLAN.md` in R1. This pass re-opens none of them. It
**ratifies exactly one thing**, because the plan says batch 5 must: §5's rule
that a many-to-one merge preserves the child segment.

---

## 1. THE RATIFICATION — R23 preserves the child segment, and the evidence is a measurement rather than a preference

`MOVE_MAP_EXECUTION_2026-08-17.md` §5: *"§2.2's R23 sends four `closure_*` source
directories to `research/closure` without saying whether each keeps its own
segment… `lab_paths` applies that reasoning uniformly and preserves the child
segment on every many-to-one merge… §4.3's own example reads the other way…
**batch 5 must ratify it before it runs.**"*

### 1.1 It is implemented that way, confirmed before anything moved

`scripts/lab_paths.py`'s `_MOVES` is the one place the decision lives, and it was
executed rather than read:

```
demo-output/website/closure_eval                        -> research/closure/closure_eval
demo-output/website/closure_challenge_submission        -> research/closure/closure_challenge_submission
demo-output/website/closure_challenge_submission_round4 -> research/closure/closure_challenge_submission_round4
demo-output/website/closure_challenge_submission_round5 -> research/closure/closure_challenge_submission_round5
demo-output/website/race-gui                            -> research/race/race-gui
demo-output/website/race-reynolds-gradient              -> research/race/race-reynolds-gradient
demo-output/website/r2-coefficient-uq-flatplate         -> research/uq/r2-coefficient-uq-flatplate
demo-output/website/r2-closure-coefficient-uncertainty  -> research/uq/r2-closure-coefficient-uncertainty
```

Every R23 row has a **distinct** destination; a scan of `redirect()` over the
whole tracked corpus reports **zero successor collisions repo-wide** and zero
destinations landing on a tracked path that does not move.

### 1.2 THE COUNTER-FACTUAL, MEASURED — flattening the four closure sources destroys 18 files

The four sources hold **24 + 9 + 9 + 11 = 53 tracked files**. Flattened into one
`research/closure/` namespace, as §4.3's worked example reads, they land on **35
distinct relative paths**: **18 files are silently overwritten**, on **9 names,
each contributed by three of the four sources**:

```
3x  MANIFEST.json
3x  test/AR_14_Ret_180.csv        3x  test/alpha_05_4071_2024.csv
3x  test/AR_1_Ret_360.csv         3x  test/alpha_05_4071_4048.csv
3x  test/AR_3_Ret_360.csv         3x  test/alpha_15_13929_2024.csv
3x  test/NASA_2DWMH.csv           3x  test/alpha_15_13929_4048.csv
```

The three `MANIFEST.json` are the round-over-round submission manifests, whose
entire content is that they differ from each other.

**And a path-set check alone would have called the merge clean.**
`closure_challenge_submission` and `closure_challenge_submission_round4` have the
**same sorted path-set sha256, `55e372ce9b626836`**, and differ in bytes —
326,909 against 326,868. Two trees can share a count, a name set and a digest and
have nothing else in common; that is why every assertion in §3 is a **set
comparison** and why this one is a comparison of what the flat form would lose.

**RATIFIED. The child segment is preserved.** Pinned by
`test_the_r23_closure_merge_preserves_the_child_segment`, which asserts the four
closure destinations, the two `race*` siblings and the two `uq` siblings, and
carries the must-not-match control that keeps it from degenerating: the PARENT of
a merge family still flattens (`race/benchmarks.md` → `research/race/benchmarks.md`,
`tmr/a.json` → `cases/tmr/a.json`), so a `redirect()` that appended the child
segment to everything would fail this test rather than pass it.

---

## 2. What moved, re-derived rather than carried

`MOVE_MAP_EXECUTION_2026-08-17.md` §4 prices batch 5 at **437 files**.
Re-derived at `7a98c33d` by running `lab_paths.redirect()` over every tracked
path and keeping those whose successor is under `research/`:

| Rule | Source → destination | files |
|---|---|---:|
| R14 | `website/benchmarks.json` → `research/closure/data/` | **1** |
| R15 | `website/benchmarks.png` → `research/closure/plots/` | **1** |
| R16 | 19 loose `website/*.md` → `research/closure/md/` | **19** |
| R17 | 21 loose `website/*.json` → `research/closure/data/` | **21** |
| R18 | `website/wall/wall.json` → `research/closure/data/` | **1** |
| R23 | 11 research topics → `research/<topic>/` | **394** |
| | **executed** | **437** |

**437 exactly, at the map's own number**, and unlike batch 7's it has not
drifted: none of these rules reaches a run archive, so batches 1 and 2's 14,353
untrackings touched none of it.

R23's own breakdown, against `MOVE_MAP_2026-08-16.md` §2.2's: `race` 179 +
`race-gui` 6 + `race-reynolds-gradient` 1 = **186**; `agenda` **139**;
`closure_eval` 24 + `closure_challenge_submission` 9 + `_round4` 9 + `_round5` 11
= **53**; `optimization` **8**; `r2-coefficient-uq-flatplate` 5 +
`r2-closure-coefficient-uncertainty` 3 = **8**. Total **394**. Every one of the
five figures reproduces the map to the file.

**`R6 — proposals` is inside R23's `agenda` move and needed no rename.**
`MOVE_MAP_2026-08-16.md` §11 measured all 131 proposal files as already
kebab-case with zero exceptions, so the rule is satisfied by the directory move:
`demo-output/website/agenda/proposals/` → `research/agenda/proposals/`, **131
files, no file renamed**. The plan's batch-5 verification line was executed
against the new path: `json.load` over `research/agenda/proposals/*.json` parses
**131 of 131, 0 errors**.

---

## 3. Granularity, and the proof on both sides

**Eleven of the 54 sources are directories and each went by exactly one `git mv`
naming the directory.** The other 43 are individual files — R14's, R15's, R18's
and R16/R17's 40 loose webroot files — which have no directory to name and can
carry nothing. `wall/` is a **split** directory and was treated as one:
`wall.json` is R18 and left; `wall.html` is one of R13's five served files and
**stays under the webroot until batch 8**, which is asserted rather than assumed
— G2's fifth arm in §7.2.

For every directory source, `scripts/hand_carry.py`'s repaired `measure()` was
run against the source immediately before the move and the destination
immediately after — file count, byte total, and the sha256 of the **sorted
relative-path set**. `measure()` raises rather than returning a short number when
a walk or a stat fails; **all 22 measurements reported `walk_errors = 0`**.

| Source → destination | files | bytes | sorted path-set sha256(16) | source gone | destination set |
|---|---:|---:|---|---|---|
| `demo-output/website/agenda` → `research/agenda` | 139 | 1,696,572 | `e10dbf43497dcbba` | yes | **identical** |
| `demo-output/website/race` → `research/race` | 179 | 1,388,148 | `480488ff3135a4aa` | yes | **identical ∪ children, §3.1** |
| `demo-output/website/race-gui` → `research/race/race-gui` | 6 | 571,467 | `90a657ffef38cd2f` | yes | **identical** |
| `demo-output/website/race-reynolds-gradient` → `research/race/race-reynolds-gradient` | 1 | 9,248 | `00d73da636430b0d` | yes | **identical** |
| `demo-output/website/closure_eval` → `research/closure/closure_eval` | 24 | 9,878,679 | `3a4013fcb559b6d0` | yes | **identical** |
| `demo-output/website/closure_challenge_submission` → `research/closure/closure_challenge_submission` | 9 | 326,909 | `55e372ce9b626836` | yes | **identical** |
| `demo-output/website/closure_challenge_submission_round4` → `research/closure/closure_challenge_submission_round4` | 9 | 326,868 | `55e372ce9b626836` | yes | **identical** |
| `demo-output/website/closure_challenge_submission_round5` → `research/closure/closure_challenge_submission_round5` | 11 | 329,740 | `413445222f1e2d4c` | yes | **identical** |
| `demo-output/website/optimization` → `research/optimization` | 8 | 1,113,650 | `487dddbf83860be0` | yes | **identical** |
| `demo-output/website/r2-coefficient-uq-flatplate` → `research/uq/r2-coefficient-uq-flatplate` | 5 | 926,418 | `99e7b2878ad8adc0` | yes | **identical** |
| `demo-output/website/r2-closure-coefficient-uncertainty` → `research/uq/r2-closure-coefficient-uncertainty` | 3 | 229,731 | `d7097f7a41547596` | yes | **identical** |
| | **394** | **16,797,430** | | | |
| 43 loose files | **43** | 1,138,774 | — | all 43 gone | all 43 present |
| **BATCH 5** | **437** | **17,936,204** | | | |

Every source is **gone**, and every destination holds **exactly the source's
sorted relative-path set**, asserted as a Python set equality — not only as a
digest, and not only as a count.

### 3.1 `research/race` is the one destination that is not a copy of one source, and the assertion says so

`race`, `race-gui` and `race-reynolds-gradient` are three sources and one
destination tree: R23 flattens the parent and preserves the two children's
segments, so `research/race/` ends up holding all three. A naive
"destination == source" check FAILS on it and reported a false red on the first
pass; the honest assertion is against the **union**:

```
research/race expected 186 paths, got 186, set-identical: True
  bytes 1,968,863 == 1,388,148 + 571,467 + 9,248          : True
  sorted path-set sha256                                   : a0b80a1f277ddea9
```

Stated rather than smoothed away, because a check that reddens on the plan
working is the failure mode batch 4 recorded on
`test_sweep_roots_reproduces_self_audit_4309_before_the_move`, and the fix is to
assert the right thing, never to loosen the assertion.

### 3.2 THE RIDE-ALONG INVARIANT IS NOT EXERCISED BY THIS BATCH EITHER, AND THAT IS A MEASUREMENT

`hand_carry.derive()` at `7a98c33d` reports **zero** rows in any of its four
buckets whose source is at or under any batch-5 source, and **zero** ride-along
rows whose carrier is one. Every one of the eleven directories has an on-disk
file count exactly equal to its tracked file count — 139/139, 179/179, 6/6, 1/1,
24/24, 9/9, 9/9, 11/11, 8/8, 5/5, 3/3. **So a per-file `git mv` loop would have
lost nothing here**, and saying so is more useful than claiming a protection this
batch did not need.

Directory granularity was used anyway, for the plan's own reason — the mechanics
are proven on small batches before they are trusted with the 14,269,950,892
gitignored bytes across 2,334 dark trees that batches 6 and 7 carry, where the
invariant is worth all of it.

---

## 4. THE FINDINGS — three rules that were written down and never bound

All three are the same defect class as R16/R17 in batch 3 and R1's missing
`AWS_TREE_PLAN` row in batch 4: **a rule ratified in a record or stated in a
comment, and not bound in the code, is a rule the mover does not have.** All
three would have failed **silently**.

### 4.1 `RECORD_ROOT_NAMES` had no name for `research/closure`, and batch 5 is the batch that moves records out of the webroot

`lab_paths.RECORD_ROOTS()` replaces `self_audit.py`'s `WEB.rglob("*.md")` and is
what `_record_documents()` — and therefore `check_evidence_paths_exist` — sweeps.
Its tuple named `AGENDA`, `RACE`, `OPTIMIZATION`, both `uq` trees and the four
`closure_*` trees. It did **not** name `research/closure`, and **R16 sends 19
loose `*.md` records there**.

Measured both ways at the post-move tree, in one invocation:

| `RECORD_ROOT_NAMES` | roots | records swept |
|---|---:|---:|
| with `CLOSURE` (this commit) | 7 | **372** |
| without it | 10 | **353** |

**Exactly R16's 19 records, lost.** Not failed — lost: the sweep would have run,
scanned a corpus 19 documents smaller, and reported on it. That is the silent-zero
this repository has recorded repeatedly and the reason `RECORD_ROOTS` exists at
all. `CLOSURE` is the whole `research/closure` root, so under the dedup it also
subsumes the four `closure_*` names, which is why it is one name and not four —
the root count falls from 10 to 7 and the record count **rises**.

Pinned by `test_record_documents_never_loses_a_record_the_rglob_reached`, §5.1.

### 4.2 `build_benchmarks.py` carried a comment describing a split that was never made

`sdk/scripts/build_benchmarks.py:65-67`, written in batch 3b, says in as many
words: *"This module READS `mega-batch/` and WRITES `benchmarks.json` (R14) and
`benchmarks.png` (R15), which go to two different roots under
`research/closure/`. One `_OUT` cannot name all three, so each is named."* The
next line was `_OUT = lab_paths.WEB`, and `main()` wrote both files into it.

Left alone, the first regeneration after this batch would have re-created
`benchmarks.json` and `benchmarks.png` **in the webroot** — beside the five files
R13 says the webroot holds — while the moved copies under `research/closure/`
went stale, with nothing failing. Split into `_OUT_JSON = lab_paths.BENCHMARKS_JSON`
and `_OUT_PNG = lab_paths.BENCHMARKS_PNG`; executed after the move, the module
now binds `research/closure/data/benchmarks.json` and
`research/closure/plots/benchmarks.png`.

### 4.3 `build_wall.py`'s single `_OUT` would have written the LIVE SERVED PAGE into `research/closure/data/`

`MOVE_MAP_EXECUTION_2026-08-17.md` §5 Class 1 names *"`build_wall.py:38`'s
`_OUT` splitting into two constants"* and files it under batch 8. **It belongs to
batch 5**, and that is the more interesting half. The constant was
`_OUT = lab_paths.WALL_JSON.parent`, and it was correct only while `wall.json`
and `wall.html` shared a directory. R18 moves `wall.json` in **this** batch and
R13 keeps `wall.html` under the webroot until **batch 8**, so from the moment
batch 5 landed, `_OUT` would have resolved to `research/closure/data/` and the
next `build_wall` run would have written the served page to
`research/closure/data/wall.html` — a path that does not exist and must never
exist, quoted as the defect and **withdrawn; do not cite it** — leaving the page
on port 8080 frozen at its last build and reporting success.

Split into `_WALL_JSON` and `_WALL_HTML`; executed after the move, the module
binds `research/closure/data/wall.json` and
**`demo-output/website/wall/wall.html`** — the two sides of the split, one moved
and one not.

### 4.4 The rest of the same-commit set, and the scan that produced it

D371 rules that a Class-1 path scan for any later batch **must have no suffix
filter**. This one had none: **every tracked non-`.md` file was read** (970
binaries skipped on a NUL probe, and one path **withdrawn, do not cite it** —
`scripts/mutation_harness_known_test_names.py`, reported as tracked-at-HEAD and
absent from the worktree, which is the standing `lab_check` UNKNOWN and not this
batch's). The suffix-filtered form would have
missed nine files; **all nine turned out to be records or fixtures, none
executable** — three campaign/tmr JSON records carrying citation fields, the
superseded `docs/PHASE2_MOVE_MAP.tsv`, and the three G2 control corpora, which is
exactly what G2 exists to check. **A clean negative result, and it is reported as
one.**

| File | What it named | Why it could not wait |
|---|---|---|
| `scripts/lab_paths.py` | `RECORD_ROOT_NAMES` had no `CLOSURE` | §4.1 — 19 records leave the sweep |
| `sdk/scripts/build_benchmarks.py` | one `_OUT` for two roots | §4.2 — regenerates into the webroot |
| `sdk/scripts/build_wall.py` | one `_OUT` for a moved file and a served one | §4.3 — writes the live page to the wrong root |
| `scripts/self_audit.py` | `_grade_source_path` was `REPO / source` | the GRADES table declares two batch-5 records as the evidence it grades against; a literal-only lookup turns RULE 3 (PRESENT) into `UNPROVEN` — *"an absent artifact is a fact about the box"* — for a file that is on the box under its new name. Routed through `lab_paths.resolve()`, which also closes the four declarations batches 6 and 7 move |
| `sdk/chief_engineer/agenda.py` | `premise_violations` tested `(root / citation).exists()` | `agenda/docket.json` is the most-cited file in the docket; every proposal citing it would have started reading as a premise nobody checked. The `repo=` argument still gets the literal test, because a synthetic root is not this tree |
| `scripts/add_proposals_supervisor_review_2026_08_07.py` | `DOCKET` and `INBOX` spelled the prefix | outside batch 3b's conversion set; both now come from `lab_paths.AGENDA` |
| `scripts/launch_solve.sh` | an absolute `…/agenda/docket.json` | shell cannot import, but the python it embeds can, and now does |
| `scripts/calibration_scorecard.py` | the printed `FRAME:` line | `PROPOSALS` already resolved correctly and the frame line did not. A frame line naming a different directory from the one the numbers came out of is worse than no frame line; it is derived now |
| `sdk/tests/test_rank_claim_surfaces.py` | two `REPO / rel` + `exists()` loops over five moved surfaces | *"ABSENCE FAILS"* is the point of those loops; located by `resolve()` now, and **absence still fails** because `resolve()` returns `None` for a path that is nowhere |
| `sdk/tests/test_untrained_qcr_attribution.py` | `benchmarks.json` and `wall/wall.json` | same, and the module did not import the shim at all |
| `sdk/tests/test_lab_paths.py` | two equality pins, §5.1 and §5.3 | both redden on the functions working |
| `scripts/check_summary_consistency.py` | `CONTROL_PATH` fed into `git show`, §7.3 | **PASS → UNKNOWN exit 3**; a shim answers *where is it now* and a commit needs *where was it then* |
| `sdk/tests/test_summary_consistency.py` | the same two control blobs, **at module scope** | a `SkipTest` at import took **46 tests** out of the run behind one `skipped` line, §7.3 |
| `sdk/tests/test_normative_clause_check.py` | `git show 5bec65f0^:<GUIDELINES>` | its positive control stopped being readable |
| `sdk/tests/test_empty_set_is_not_agreement.py` | `_ABSENT_SOURCE_CASES` blinded on `WEB` alone | after batch 5, `WEB` blinds one record root of seven, §7.3 |
| `sdk/tests/test_form_or_value_and_empty_selection.py` | two `_Swap(WEB=…)` sites and one fixture spelling the old layout | same, plus an UNKNOWN that quietly changed its reason |

---

## 5. Two tests, and why each was changed the way it was

### 5.1 `test_record_documents_reproduces_the_rglob_before_the_move` — equality was the wrong pin

It asserted `_record_documents() == sorted(WEB.rglob("*.md"))`. That held only
while every record root was under the one webroot. **Batch 5 is the first batch
that takes records out of it**, so equality now reddens on the sweep gaining the
roots it was built to gain. This is batch 4's finding on `SWEEP_ROOTS`, recurring
one instrument over.

What is load-bearing is the **direction**: a sweep that gains a root walks more;
a sweep that loses one scans fewer and passes. So the test is now
`test_record_documents_never_loses_a_record_the_rglob_reached`, with five arms —
nothing the rglob still reaches may be missing; nothing may be reached twice;
every extra must be a real `*.md` under a real rule destination; **every record
that left the webroot must still be reached** (the batch-5 arm, which names
itself and skips rather than silently passing before the batch lands); and a
must-not-match control asserting `docs/LESSONS.md` is **not** in the sweep,
without which a `_record_documents()` that returned every markdown file in the
repository would satisfy all four arms above.

### 5.2 The R23 ratification is pinned, with the control that keeps it from degenerating

`test_the_r23_closure_merge_preserves_the_child_segment` — §1.2. Its
must-not-match control asserts that the PARENT of a merge family still flattens,
so the test cannot be satisfied by a `redirect()` that appends a child segment to
everything.

`test_no_two_tracked_paths_collide_on_one_successor` already runs over the whole
tracked corpus and would have caught a flattened R23 — but only once the
flattening existed. §1.2's counter-factual is the same fact measured **before**
the decision, which is the form a ratification needs.

### 5.3 `test_submission_packages_reproduces_the_webroot_glob` — the same shape, one function over

It asserted `SUBMISSION_PACKAGES() == sorted(WEB.glob("closure_challenge_submission*"))`
*whenever the webroot exists*. The webroot still exists after batch 5 — it keeps
4,487 tracked files until batch 8 — and R23 emptied that glob, so the arm fired
against `[]`. **Equality with the thing being replaced is a pre-move pin and
nothing else.** It now asserts all three packages are found, sorted, and are
directories, on whichever side they are; keeps the pre-move equality arm for
while the glob still returns anything; and leaves
`test_submission_packages_is_not_a_hardcoded_three` — the control that catches an
accessor reciting three names it can no longer find — untouched beside it.

Three equality pins, three batches: `SWEEP_ROOTS` in batch 4, `_record_documents`
and `SUBMISSION_PACKAGES` here. **Every accessor written to replace a
whole-tree glob acquires a test that pins it to that glob, and every one of them
reddens at the batch the accessor was written for.** Whoever runs batch 6 should
expect the same and should look for it rather than be surprised by it.

---

## 6. What was NOT done, and each is a decision rather than an omission

### 6.1 `_SHIPPING_RE` is not re-pointed here, and `web/` is why

`MOVE_MAP_EXECUTION_2026-08-17.md` §5 Class 2 requires
`scripts/check_absolutes.py`'s `_SHIPPING_RE` to land its `web/` alternative
**in the commit that creates `web/` and not before**. **Batch 5 does not create
`web/`** — R13, the served set, is batch 8 — and `ls web` returns *no such file
or directory* after this batch as before it. The pattern still reads
`^(?:demo-output/website/|.*/latex/|.*\.tex$)` at `check_absolutes.py:743`, and
the file is **byte-identical to HEAD**, confirmed by diffing against `HEAD:`'s
blob rather than assumed. It stays queued for batch 8.

### 6.2 R8's fifteen launchers are not touched, and the deferral is inherited unchanged

Batch 4 deferred them because they are enumerated in **no committed artefact**
(D370, L-111), and batch 0 had recorded the same shape as L-94. **Batch 5 does
not touch that boundary**: R8 moves to `ops/`, and every one of batch 5's 437
files moves to `research/`. No launcher was moved, **no membership list was
reconstructed**, and the crontab line, the `demo_servers.sh --directory`
re-point and the `/usr/local/bin/auto-stop.sh` re-install still travel together
with whoever rules that list. The `@reboot` crontab entry still invokes
`scripts/demo_servers.sh` at its unchanged path and does not dangle.

### 6.3 The guard resolver is batch 9's, and batch 5 is what makes it non-optional

This is the largest single effect of the batch and it is stated plainly rather
than absorbed. `check_evidence_paths_exist` tests `(REPO / cited).exists()` — the
**literal** path only. Measured over the same 372 records, same instrument, same
regexes, before and after:

| | before (372 records) | after (373 records) |
|---|---:|---:|
| repo-rooted citations | 1,777 | 1,820 |
| not resolving at the LITERAL path | **12** | **197** |
| …of those, resolving at the SUCCESSOR via `lab_paths.resolve()` | 7 | **193** |
| …**genuinely nowhere** | **5** | **4** |

The population grew by 43 because this record and batch 4's landed in the corpus.
**This record contributes zero of the 197**, checked by running the guard's own
regexes over it alone: every pre-move spelling it quotes carries the withdrawal
wording the guard's `retracted` pattern reads, because batch 4 recorded a draft
of its own §7 inflating the finding it existed to report and that is a trap worth
not repeating.

**The corpus is not more broken after this batch than before it — it is less.**
The 185 new rows are citations the guard cannot *follow*, not citations that
point at nothing: `lab_paths.resolve()` finds every one of them at its successor,
which is precisely the resolver `MOVE_MAP_EXECUTION_2026-08-17.md` §4 batch 9
specifies. The number that measures the corpus rather than the instrument is the
last row, and it went **5 → 4**.

**The repair was NOT made here**, and the reason is not timidity: batch 9 is
specified with a **two-way planted control** — *"a citation that must resolve and
one that must not"* — and a resolver landed without that control is the shape of
a guard that stops discriminating. The 1,236 citations inside append-only records
stay unedited, as the plan requires. What is corrected is the plan's own timing:
§4 says the guard goes blind at **batch 8**, and blind is the wrong word and 8 is
the wrong batch. **Batch 5 is where the guard stops being able to follow the
tree**, batch 4 already moved it 5 rows (which batch 4 reported, at 7 of 1,777),
and after batch 5 the check is answering a question about `lab_paths` rather than
about the corpus.

### 6.4 `docs/LOCATIONS.md` still does not mention `research/`, `media/` or `ops/`

Owed since batch 2 and still owed. Batch 4 created two roots without updating it;
batch 5 creates a third. Recorded here so the debt is one line rather than three
discoveries.

---

## 7. The gates, both sides, with their finding sets

### 7.1 `scripts/lab_check.py --no-tests` and the full suite

Before, at `8c57d2a0` over the worktree that `7a98c33d` then committed:
`--no-tests` **FAIL, exit 1, ran 20/20**, 298.8 s. Full run **FAIL, exit 1, ran
21/21**, 1,493.7 s. After: `--no-tests` **FAIL, exit 1, ran 20/20**, full
**FAIL, exit 1, ran 21/21**, 1,449.1 s. **stderr empty on all four runs.**

| Check | before | after |
|---|---|---|
| `scripts/check_pdf_surfaces.py` | FAIL | FAIL |
| `scripts/check_proposal_surface_coverage.py` | FAIL | FAIL |
| `scripts/check_rung_attribution.py` | FAIL | FAIL |
| `scripts/contention_audit.py` | FAIL | FAIL |
| `scripts/installed_registry.py` | FAIL | FAIL |
| `scripts/self_audit.py` | FAIL | FAIL |
| `scripts/check_absolutes.py` | **BLOCKING UNKNOWN, exit 3** | **BLOCKING UNKNOWN, exit 3** |
| `scripts/check_summary_consistency.py` | PASS | **PASS — after the repair of §7.3; it read UNKNOWN exit 3 on the first pass** |
| the other 12 | PASS | PASS |
| `sdk/tests` (pytest) | **6 failed / 2,443 collected / 0 skipped** | **6 failed / 2,444 collected / 0 skipped** |

The six suite failures are the standing baseline in both frames and are the same
six tests in the same four modules: `test_exec_bits` 1, `test_fail_open_scan` 1,
`test_installed_matches_tracked` 3, `test_pdf_surfaces` 1. **The collected total
rises by exactly one** — §5.2's R23 ratification test — which is the whole of the
delta and is the number §7.3 is about.

**Two frame numbers move and neither is a verdict.** `--no-tests` reports
`15 unrun check(s)` after against `15` before, and the full run `14` against
`14`; `admitted` is unchanged at 112 and `not admitted` at 67. Batch 5 moves
nothing into or out of `scripts/` or `sdk/tests/`, so unlike batch 4 the
candidate universe does not move at all.

**`cited evidence paths` is the one check-level finding whose COUNT changes**,
from 12 of 1,777 to 197 of 1,820. §6.3 is what that number is and is not.

### 7.1a THE FIRST AFTER-RUN WAS NOT GREEN, AND WHAT IT CAUGHT IS §7.3

The first post-move suite returned **17 failed out of 2,398** — eleven new
failures and **forty-five fewer tests collected**. Both halves were repaired
before this commit was built, so nothing here is a repair-forward after a
landing: this is the pre-commit verification doing its job, which is the reason
the plan puts a full suite on both sides of a batch rather than only after it.
The eleven failures and the missing forty-five are §7.3.

### 7.3 THE FINDING THE VERDICTS COULD NOT SHOW — 46 tests left the suite behind one `skipped` line

Eleven new failures across five modules, and **all eleven are one of two
defects**. Neither is a defect in the move.

**(a) A path shim resolves against the FILESYSTEM; four `git show` lookups into
immutable commits were being fed from it.** `lab_paths.web_file()` answers
*where a file is now* — correct for a live read, and the wrong question entirely
for `git show <commit>:<path>`, where the file sits at whatever path THAT commit
used. R16 moved `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` and
`CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` to `research/closure/md/`, and three
callers broke together:

| Site | Effect |
|---|---|
| `scripts/check_summary_consistency.py:226` | both controls unreadable → its own *"a control that misfires makes the whole run UNKNOWN"* rule fired as designed → **PASS → UNKNOWN exit 3**, the only check of twenty whose verdict moved |
| `sdk/tests/test_normative_clause_check.py:118` | the positive control `test_fires_on_prerepair_clause_b` failed |
| `sdk/tests/test_summary_consistency.py:196` | **at MODULE SCOPE** — `unittest.SkipTest` at import took the entire file out of the run |

**The third one is the finding.** Forty-six tests became **one `skipped` line**.
The suite's verdict did not change — it was already FAIL on six — and the
failing-module list got *shorter*, not longer. `47 tests` in that file, `skipped
1` in the summary, and nothing named what was gone. **The only signal was the
collected TOTAL: 2,443 → 2,398.** That is why this plan says to report finding
sets rather than verdicts, and why the count is worth comparing even when both
sides are red for the same reason.

Repaired by `check_summary_consistency._in_commit()` and a sibling in the
normative test: the spelling is **probed inside the named commit** with
`git cat-file -e` across the literal path, `lab_paths.unredirect()` of it and
`lab_paths.redirect()` of it. Not a hard-coded legacy string, which rots the
other way the moment a control commit is written after a move. All five of the
check's controls fire afterwards — P1 1 hit, N1 0, N2 0, P2 1 hit, N3 0 with 1
exempt — and the module-scope `SkipTest` now names the path it tried and the
`CONTROL_PATH` it came from. Collection is back to **2,444**.

**(b) D368 recurred, at the batch that made it unavoidable.**
`test_empty_set_is_not_agreement.py`'s `_ABSENT_SOURCE_CASES` and
`test_form_or_value_and_empty_selection.py`'s `_Swap` blind a check by rebinding
`self_audit`'s `WEB`, `REPO`, `ACTIVE`, `WALL`, `CAMPAIGN` or `MISSION` and
assert UNKNOWN rather than a clean sweep of nothing. Until batch 5 **every root
`RECORD_ROOTS()` returns was under the webroot**, so rebinding `WEB` emptied all
of them. After batch 5 there are seven roots and `WEB` blinds **one**:
`check_evidence_paths_exist` returned FAIL, `check_fd_grades_current_standard`
PASS and `check_closure_entry_of_record` PASS, where all three must return
UNKNOWN. Five failures.

**`_at()` was still correct. The handle had stopped covering the region.** The
handle that does cover all seven is `REPO`, which `_at()` re-roots on
unconditionally, and it is now named in both case lists. And a fixture that
spells a layout is the same defect in different clothes: `test_rung_estimates`
built its docket at `<tmp>/demo-output/website/agenda/docket.json` under a
swapped `REPO`, a directory the check no longer looks in, so its UNKNOWN quietly
changed from the *empty-selection* reason to the *absence* reason — a different
finding that still counted as a pass in the total. The fixture now derives its
layout from the shim and follows every remaining batch with no edit.

**The question to carry into batches 6, 7 and 8 is not a fix, it is a question:
for every blinding test, which handle covers the region after the move?**

### 7.2 The three standing gates

| Gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B**, digests `1b53ed5a4e9d63cb` / `5519de4237b71ce4` | **byte-identical** — same two trees, same 307 files, same bytes, same digests |
| **G1** rides-along | 2,334 trees, 45,770 files, 14,269,950,892 B | **identical** |
| **G1** goes-dark-after-batch-2 | 0 | **0** |
| **G2** control corpora | 223 path fields, 0 unresolved | **223, 0** |
| **G3** root binding | `roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (CLOSURE, CLOSURE_DATA, CLOSURE_MD, CLOSURE_PLOTS, EVIDENCE)` | `roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (EVIDENCE,)` |

**G1's carry set was derived BEFORE anything moved**, as the invariant requires:
the two genuinely dark trees are `demo-output/website/solve_registry` (300 files,
1,508,128,888 B) and `demo-output/website/surfaces` (7 files, 2,180,257 B), and
they were confirmed byte-identical to the plan's figures and to batch 4's, twice.
Neither is under a batch-5 source and neither moved.

**Two of G1's buckets DID change and neither is the carry set.** `STAYS PUT` goes
5 trees / 10,287 files → 6 / 10,724, the extra row being `research/` itself at
**437 files / 17,936,204 bytes** — the batch's own output, dark only because it is
measured against a HEAD that predates the commit that tracks it, and gone the
moment the commit lands. `mission-output/` moved by −61 bytes under another lane,
which §3.5 already records as a live 573 MB tree with 13 tracked consumers.
`DISCARD` goes 8 trees / 23 files → 7 / 41: `__pycache__` churn from this pass's
own compiles, which §3.1 says moves with every test run and which is never
carried.

**G3's `UNRESOLVED` falling from five names to one is the batch landing.**
`CLOSURE`, `CLOSURE_DATA`, `CLOSURE_MD` and `CLOSURE_PLOTS` were
**destination-only** names with no legacy directory — deliberately unresolved
until the batch that assembles `research/closure/` from eight scattered sources,
which is this one. `EVIDENCE` remains, and correctly: batch 7H assembles it.
`AMBIGUOUS` is empty **after** the move as well as before, which is the
non-trivial half — every batch-5 name reports `state() == "moved"` and none
reports `"both"`.

**G2 was fired five ways**, because a count alone cannot show a corpus still
discriminates: a citation that must resolve does
(`demo-output/website/closure.html`); one to a document that never existed returns
`None`; batch 4's arm still resolves (`demo-output/plots/C_d/frame_0001.png` →
`media/plots/…`); this batch's arm resolves at its successor
(`demo-output/website/agenda/docket.json` → `research/agenda/docket.json`,
`wall/wall.json` → `research/closure/data/wall.json`; **the left-hand spelling in
each pair is the pre-move one and is withdrawn — do not cite it**); and — the arm
this batch adds — **`demo-output/website/wall/wall.html` must still resolve to
`demo-output/website/wall/wall.html`**, which is the R18/R13 split measured on the
one directory batch 5 splits.

**No gate was adjusted.** Two tests were, both in the direction of asserting more
(§5), and both fired against the state that would have failed them.

---

## 8. WHAT BREAKS IF BATCH 5 LANDS AND BATCH 6 NEVER DOES

**Nothing breaks, and `research/` is complete rather than half-assembled — which
is the opposite of what the plan predicted for this batch, and the reason is that
batch 5 was run whole.**

`MOVE_MAP_EXECUTION_2026-08-17.md` §4 predicts *"`research/closure/` is
half-assembled… a reader finds a `research/closure/` that contains the outputs
and none of the inputs"*. That is what a **partial** batch 5 leaves. This one
landed R14, R15, R16, R17, R18 and all eleven R23 sources in one commit, so
`research/closure/` holds `data/` (23 files), `md/` (19), `plots/` (1) **and**
all four `closure_*` source trees; `research/race/`, `research/agenda/`,
`research/uq/` and `research/optimization/` are each complete.

What is true if batch 6 never lands:

1. **`cases/` does not exist and the webroot still holds every physics family.**
   `demo-output/website/` retains 4,487 tracked files — `dafoam/`, `tmr*`,
   `mega-batch/`, `hlpw6/`, `valve/`, `unsteady-cylinder/`, `committee-grids/`,
   `campaign/`, the five served files, and X3's never-touch trees. Every citation
   to them still resolves at its literal path, so nothing degrades; the tree is
   simply mid-migration and legible as such.

2. **`research/` and the webroot both hold research artefacts, and one pair is
   split on purpose.** `wall.json` is under `research/closure/data/` while
   `wall.html` is under `demo-output/website/wall/`. That is R18 and R13 meeting,
   it is correct, and `build_wall.py` now names both sides (§4.3). A reader who
   assumes the two live together is wrong, and the constant is where the truth is.

3. **`lab_paths` answers `moved` for 1,294 files and `legacy` for the rest, and
   both are right.** All 223 control-corpus citations still resolve; so do 193 of
   the 197 record citations the literal-only guard now reports (§6.3).

4. **The shared index is exactly 437 entries stale, and for once that is a
   small and well-defined number.** It was reconciled to HEAD by the coordinator
   while this pass ran — 7,079 = 7,079, zero staged renames, adds, deletions or
   modifications, verified here rather than taken on report — after having held
   856 REVERSE renames pointing every batch-4 path back at its pre-move
   location, plus 145 stale blobs including `LESSONS.md` at its old root path
   three lessons behind. **This pass is unaffected either way**: all 54 `git mv`s
   ran under a private `GIT_INDEX_FILE`, and the commit's index is rebuilt from
   the observed HEAD rather than from the one `git mv` wrote, so neither the
   shared index's old state nor its new one is read. After this commit lands, the
   shared index will list the 437 sources at their pre-move paths. The surgical
   `git update-index --force-remove --stdin` over **only this agent's 437 paths**
   was **not run**, because this pass was directed not to write the shared index;
   it is filed as owed, and the path list is §3's table plus the 43 loose files.

5. **Two batch-4 figures are inherited corrected rather than carried.** R8 is
   11 moved + 15 unnameable, not 26 executed (§6.2). And **batch 7 is 2,854, not
   8,643, with the move subtotal 6,270 rather than 13,511** — batch 2's
   untracking of 7,403 mostly-R20 files dominates, so both are stale HIGH by
   roughly threefold, which is the opposite sign to D366's reading of the same
   pair. Batch 5 does not re-derive them; it records that they are not to be
   carried.

6. **The guard's citation count stays at 197 until batch 9.** §6.3. This is the
   one thing batch 5 leaves worse than it found it, it is loud rather than
   silent, and it is 4 rather than 197 once the resolver lands.

**And the batch that becomes cheaper.** Batch 6's R22 sends ten physics families
to `cases/`, and `cases/tmr` is a four-source many-to-one merge with the same
shape as §1's. **That decision is now ratified and pinned** rather than
outstanding, and `test_tmr_family_merge_does_not_collide` and this batch's R23
test are the two halves of it.

---

## 9. Method

- Every path-derived count is over `git ls-tree -r -z --name-only`, at a named
  commit, **never `git ls-files`**. The shared index was not read for any
  measurement and not written by any step; `git status` and `git diff HEAD` were
  read once, found to be reporting the 857 batch-4 destinations as *deleted*
  because the shared index still lists their old paths, and **not used for
  anything**. Files on disk were confirmed by `ls`, and membership by
  `git cat-file`.
- **stderr was captured on every walk, every `git` invocation and every
  subprocess** and was empty on all of them, including all 54 `git mv` calls,
  which were checked for a non-empty stderr as well as for a non-zero exit.
- **No count was piped into `head`.**
- Every before/after pair passes through the same instrument in the same frame.
  Path comparisons are **set** comparisons, plus a digest, never a count.
- `measure()` **raises** on any walk or stat failure rather than returning a
  smaller number; all 22 directory measurements reported `walk_errors = 0`.
- The **inverse `mv` list was written before the batch started**, as §4 of the
  plan requires — 54 lines, children before parents — and the sources were
  re-measured against the plan immediately before the move with **zero drift**
  and every one of the eleven quiet (newest write 3.1 h ago in `agenda/`, 24–30 h
  in the other ten), so no tree was carried out from under a live writer.
- Commit membership between two named commits was used wherever a question could
  have been answered by a date; nothing here is ordered or selected by one.
- This record does not appear in its own results: every measurement was taken
  before the commit that lands it.

### 9.1 Five moved files had worktree content ahead of HEAD, and it was neither captured nor destroyed

The five are named by their PRE-MOVE spellings, which are **withdrawn — do not
cite them**; each is now at its successor.
`demo-output/website/agenda/docket.json`, `ACTIVE_RESEARCH.md`,
`CLOSURE_CHALLENGE_STATUS.md`, `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` and
`closure_challenge_C2_error_decomposition.md` differed from their HEAD blobs when
the batch ran — other lanes' in-flight work. `git mv` renames the **worktree**
file, so that content travelled to the new path intact, while the commit records
**HEAD's** blob there. Nothing was captured under this batch's message and
nothing was lost; the five files' unlanded content is now at their new paths and
still unlanded, and whoever owns it lands it there.

The batch-4 lane's own record,
`demo-output/website/campaign/MOVE_MAP_BATCH4_EXECUTION_2026-08-18.md`, has 63
worktree-only lines at this frame. It was read and **not touched**.

---

## 10. What batch 5 did not do

No file was deleted or untracked; nothing left the disk. `.gitignore` was not
edited (§0 measured that it did not need to be, both by
`hand_carry.gitignore_repoint()` and by passing all 437 destinations through
`git check-ignore --no-index`). The shared index was not written and its
pre-existing state was not reverted. `_SHIPPING_RE` was not touched (§6.1).
R8's 15 launchers were not moved and no membership list was invented for them
(§6.2). `check_evidence_paths_exist` was not converted to `lab_paths.resolve()`
— that is batch 9 and it needs its two-way control (§6.3). No citation inside any
append-only record was edited. `docs/LOCATIONS.md` was not updated and is still
owed (§6.4). The hand-carry was not run: `solve_registry` and `surfaces` are
still under the webroot, at 1,510,309,145 bytes, which is 7H's. The crontab was
not read back or edited, because batch 5 moves nothing it names. No solver was
launched and nothing was registered.
