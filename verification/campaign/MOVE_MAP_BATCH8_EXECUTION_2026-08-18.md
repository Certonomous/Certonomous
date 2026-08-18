# MOVE_MAP batch 8 — the webroot cut

**Executed 2026-08-18. Parent `9f3971f6` (R25). Repository lane.**

Batch 8 is **R13, the served set** — five files — and it is the commit that
creates `web/`. It also lands the one repair batch 7 left behind: **D403**, the
K0b mesh-sensitivity rung, unrunnable since R20 moved the archive it reads.

**Nothing else was done.** No other rule was executed. `evidence/` was not
created — the 2-tree carry set is 7H's. Batch 9's citation resolver was not
built.

---

## 1. THE MOVE — five files, and `web/` did not exist before this commit

The five sources are the map's section-3 served set. Their pre-move spellings
are stated here without backticks because every one of them ceased to exist at
this commit and none of them is a citation any longer:

    demo-output/website/closure.html      ->  `web/closure.html`
    demo-output/website/benchmarks.html   ->  `web/benchmarks.html`
    demo-output/website/shoot.html        ->  `web/shoot.html`
    demo-output/website/wall/wall.html    ->  `web/wall/wall.html`
    demo-output/website/campaign/duct_secondary_flow_AR_7_validation_qcr.png
                                          ->  `web/campaign/duct_secondary_flow_AR_7_validation_qcr.png`

`lab_paths.redirect()` was run over `SERVED_SET` before a byte moved and agreed
with the map on all five destinations. `lab_paths` itself needed **no edit**:
its `WEB_*_HTML` rows and the `_special` rule for the PNG were written in batch
3 against exactly this move.

The PNG keeps its `campaign/` segment because `closure.html:350` reaches it
relatively, which is what makes the page move a pure rename with **zero edits to
any served page**. Both source directories emptied completely and were removed:
`wall/` held only the page (its `wall.json` left under R18 in batch 5) and
`campaign/` held only the served PNG (R20/R21 took the other 14,011 in batch 7).

**Every rename is asserted at `(mode, blob)`, not summarised.** The commit
machinery stages each destination with `update-index --cacheinfo` using HEAD's
own blob id, and the blob is `cmp`-ed against the file on disk before and after
the `mv`. `diff-tree -M100%` reporting five `R100` rows is therefore the
content-preservation proof rather than a description of one.

---

## 2. THE SERVED PAGES ANSWER — verified by FETCHING, not by reading

The asset closure was re-derived rather than trusted. Across all four pages,
`src=`/`href=` references that are not `data:`, not `#` fragments and not
external total **exactly one**: `closure.html:350`'s
`<img src="campaign/duct_secondary_flow_AR_7_validation_qcr.png">`. That
reproduces the map's section-3 measurement at this HEAD.

| GET (port 8080) | before | after |
|---|---|---|
| `/` | 200, 606 B | 200, 414 B (the directory index; the root now lists 5 entries, not 9) |
| `/closure.html` | 200, 55,351 B | **200, 55,351 B** |
| `/benchmarks.html` | 200, 22,817 B | **200, 22,817 B** |
| `/shoot.html` | 200, 53,700 B | **200, 53,700 B** |
| `/wall/wall.html` | 200, 10,302 B | **200, 10,302 B** |
| `/campaign/duct_…qcr.png` | 200, 1,149,137 B | **200, 1,149,137 B** |
| `:8765/` control room | 200, 152,335 B | **200, 152,335 B** — untouched |

**Every byte count is identical**, which is the served-content half of the
`(mode, blob)` assertion arriving by a second, independent route.

The one asset was fetched **relative to its page**, the way a browser resolves
it, and answered 200.

**The running server was re-pointed, and that is an out-of-tree dependency no
repository sweep reaches** (map section 5.2). `scripts/demo_servers.sh:46` was
changed from the old webroot to `--directory web` in this commit, the live
process (pid 1447, started at boot with the old flag) was killed, and
`scripts/demo_servers.sh` was re-run — the same script the `@reboot` line in
`ops/installed/crontab.ubuntu` invokes, so the boot path and the live path now
agree. That crontab line names `scripts/demo_servers.sh`, which does not move,
so no crontab edit was needed and none was made.

**Must-not-serve controls**, without which "the pages answer" is a sentence about
a server that answers everything: `/demo-output/website/closure.html` → **404**,
`/latex/closure_challenge_report.tex` → **404**, `/solve_registry/` → **404**.
The cut is real; the new root serves five files and not nineteen thousand.

---

## 3. `_SHIPPING_RE` RE-POINTED IN THIS COMMIT, AND PROVED AGAINST THE MOVED SURFACES

`scripts/check_absolutes.py`'s `_SHIPPING_RE` has been queued since batch 3 and
confirmed byte-identical to HEAD by every batch since, because an alternative
naming a directory that does not exist is a rule matching nothing. It is
re-pointed **here, in the same commit as the move**, to the map's specified
value:

    ^(?:demo-output/website/|.*/latex/|.*\.tex$)   ->   ^(?:web/|.*/latex/|.*\.tex$)

Proved by executing `blast_radius` over the surfaces, not by reading the diff:

| surface | before | after |
|---|---|---|
| `web/closure.html` | no match | **match** |
| `web/benchmarks.html` | no match | **match** |
| `web/shoot.html` | no match | **match** |
| `web/wall/wall.html` | no match | **match** |
| `web/campaign/duct_…qcr.png` | no match | **match** |
| `demo-output/website/latex/closure_challenge_report.tex` (X3, stays) | match | match |
| `demo-output/website/latex/closure_challenge_report.log` (X3, stays) | match | match |
| **control** `verification/campaign/CAMPAIGN_STATUS.md` | no match | no match |
| **control** `scripts/self_audit.py` | no match | no match |
| **control** a path where `web` is a prefix but not a segment | no match | no match |
| **control** `web/` not at the root | no match | no match |

Dropping the old alternative strands nothing: `.*/latex/` already covers the
webroot's `latex/` tree, which does not move (map X3), and that was verified as
one of the seven rows above rather than argued.

**THE STANDING RULING IS NOT OVERSTATED.** `_SHIPPING_RE` feeds `blast_radius`
alone, `blast` feeds severity **ranking** alone, and no score it produces can
flip a verdict. This is a **ranking repair, not a fail-open**, exactly as struck
at `b0ab070d`. Measured rather than asserted: of the five moved surfaces,
**four are `.html` and `blast_radius` sets their shipping bit from the suffix
regardless of the pattern**, so they scored 1 on both sides. **Exactly one
surface — the PNG — depends on the pattern**, and it is the one that moved
`blast` from **0 ("narrative") to 1 ("ships/travels")**. The degradation this
re-point repairs is one surface wide and it is a sort order.

---

## 4. D403 REPAIRED, AND THE RUNG PROVED RUNNABLE BY EXECUTION

R25 filed D403 after executing the guard and watching it REFUSE, and correctly
ruled the repair outside its own mandate. Both sites now resolve through
`lab_paths`.

`verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity/build_and_run.sh` was
the only one of the two a literal scan could see. Its sibling
`analyse_k0b_mesh.py` assembled the same path from **separate quoted segments**
— `os.path.join(REPO, "demo-output", "website", "campaign", "THERMAL_K0_runs",
…)` — and is invisible to a literal scan and to a depth scan alike. That is
L-137's class, and it is the reason all three scan shapes were run here.

Both now **find** the repository root by walking up for
`scripts/lab_paths.py` rather than counting `..` segments, and both ask
`lab_paths.run_archive("THERMAL_K0_runs")` for the archive by name.

**Proved by execution, both sides:**

| | before | after |
|---|---|---|
| `build_and_run.sh` | `REFUSE: K0b source case not found at …`, **exit 2** | **exit 0** — both meshes built, blockMeshDict edited to `(32 32 1)` and `(128 128 1)`, and **all 11 byte-for-byte `cmp` checks passed on each**, 22 in total |
| `analyse_k0b_mesh.py` `K0B_64` | named a directory with `isdir() == False` | `verification/runs/THERMAL_K0_runs/K0b_cavity_Ra1e5`, **exists** |
| the three-mesh triple | 2 of 3 legs present | **3 of 3** — 32x32, 64x64, 128x128 all on disk |

The guard was executed from a scratch working directory so that **no tracked
case file was touched**; the `cmp` loop still compared against the real archive.
The scratch directory was removed and `git status` over the rung showed only the
two intended edits.

**The must-not-match control**, without which a repair that answered "some
directory" to everything would satisfy this: both files copied to a directory
with no repository above them print
`REFUSE: no scripts/lab_paths.py in any parent of …` and exit non-zero, rather
than returning a path.

**What is NOT done and is D403's open half:** the ladder has not been *re-run*
since the move, so K0b's published mesh-sensitivity numbers have still not been
checked against a rebuilt 64x64 leg. That is compute this batch was not
authorised to spend and the docket row says so.

---

## 5. ALL THREE SCAN SHAPES, RUN OVER EVERYTHING BATCH 8 TOUCHES

Twelve surfaces: the five moved files and the seven edited ones.

| shape | what it looked for | on the twelve | repo-wide |
|---|---|---|---|
| **1. literal** | the joined path | `audit_camera_discretion.sh:141-142` and `build_and_run.sh:29` — **both repaired here** | records and superseded plans only |
| **2. depth idiom** | `parents[N]`, `parent.parent`, `../..`, `dirname(dirname` | 4 sites, **all correct and all in files that do not move** (`check_absolutes.py:143` is `parents[1]` from `scripts/`; three `sdk/tests` sites are `parents[2]`) | 19 modules, batch 7's population, unchanged |
| **3. quoted token** | the segments as quoted tokens | `test_rank_claim_surfaces.py:221,244` (a **live** read of `closure.html` the literal scan could not see) and `analyse_k0b_mesh.py:49` — **both repaired here** | **eight further dangling sites, filed as D404** |

Shape 3 earned its place twice in one batch: it is the only shape that found
the two live `closure.html` reads this move would have broken, and the only one
that found `analyse_k0b_mesh.py`.

### 5.1 The eight it found outside this batch's mandate — D404, not repaired here

Every one is `REPO / "demo-output" / "website" / …` or the `os.path.join` form,
left dangling by batch 6 or batch 7, and every one has a live successor under
`lab_paths.resolve()`. Four of them name **their own tree** at its pre-move
spelling. Two of them — in `sdk/workflows/` — are already converted to
`lab_paths.WEB` and then append an unconverted tail, which is D402's *"a census
of converted FILES is not a census of converted SITES"* one root deeper. They
are filed rather than fixed: eight foreign repairs inside the one commit that
can take a live surface down is how a batch stops being characterisable.

---

## 6. INSTRUMENTS — TAUGHT THE MAP, NEVER ADJUSTED, AND PINNED BY THE PRE-MOVE NUMBER

| instrument | pre-move | post-move |
|---|---:|---:|
| `self_audit` `placement words agree with the published board` | **80** | **80** |
| `self_audit` `rank claims carry the right values` (lab records) | **35** | **35** |
| `hand_carry.batch2_untrack_list`, option A (ruled, default) | **198** | **198** |
| the same with the exclusions dropped (the option-B arm, fired by hand) | 655 | 655 |

All four hold. Batch 7's `_tracked_files` repair and R25's `batch2_survivors`
repair are both still in force across a move that changes 12 paths.

### 6.1 ONE INSTRUMENT DID CHANGE, IT WAS FOUND BY EVALUATING RATHER THAN READING, AND IT IS REPORTED RATHER THAN ADJUSTED

`lab_paths.WEB` is read by **six** call sites, and this commit changes what
every one of them computes without naming any of them in the diff. All three
scan shapes pass over all six, correctly, because not one contains a path.

Three become correct (`build_laptop_bundle.py:526`, `self_audit.py:129`,
`capture_video.py:53`). Two were already dangling and stay dangling
(`nasa_hump.py:60`, `rae2822_case9.py:98` — both in D404). The sixth is
`sdk/scripts/closure_in_sample_gate.py:112`, where `_WEBROOT_REL` is a
**sweep root**:

```python
_WEBROOT_REL = str(lab_paths.WEB.relative_to(lab_paths.REPO))
_SCAN_JSON_ROOTS = (_WEBROOT_REL, "models")
_SCAN_MD_ROOTS = (_WEBROOT_REL, "docs")
```

**Measured rather than feared.** The old webroot held **0 `.json` and 1 `.md`**
when this batch ran, because batches 5-7 had already taken everything else out
of it. The corpus therefore lost exactly one file — a filming shotlist under
`motorbike-video/` — on a gate that neither `lab_check` nor the suite invokes.
**No verdict moved.** It is reported and not adjusted, and it is L-138.

**The size is luck and the shape is the lesson**: run batch 8 before batch 5 and
those same three lines take that gate from the whole webroot to five HTML files
with every scan still clean.

### 6.2 THREE MORE INSTRUMENTS WERE PINNED TO THE PRE-MOVE SIDE, AND RUNNING THEM EARLY IS WHY THEY ARE NOT IN THE AFTER-FRAME AS FAILURES

Before running the full suite, the three test modules this batch edits were run
on their own. **Eight arms failed**, all of them this move's doing, none of them
visible in any of the three scans:

1. `sdk/tests/test_lab_paths.py::test_bundle_pages_reproduces_self_audit_6484_before_the_move`
   pinned all three `_BUNDLE_PAGES` sources to their legacy spelling. Amended to
   name **both** sides with the disk deciding which is in force, plus a
   member-paths-do-not-move assertion, an on-disk existence assertion, and the
   `shoot.html`-is-deliberately-absent control. An assertion rewritten to the new
   spelling alone can no longer fail in the pre-move direction, which is not a
   repair.
2. `sdk/tests/test_lab_paths.py::test_record_roots_covers_every_record_the_rglob_reached`
   asserted against the **legacy webroot literal**. Amended to assert against the
   BOUND webroot on both sides.
3. `sdk/tests/test_bundle_drift_gate.py` — **seven arms at once.** Its hermetic
   fixture planted the three site pages at `self.root / "demo-output" /
   "website"`, assembled from quoted segments inside a tmp tree, while the gate
   under test reads `_BUNDLE_PAGES`, which R13 moves. The gate looked in one
   place and the fixture wrote in another. The plant location is now DERIVED
   from `lab_paths.WEB`, so no future batch has to edit this file — the same
   repair batch 7 made to `test_form_or_value_and_empty_selection.py`.

After the amendments those three modules read **222 passed, 122 subtests passed,
0 failed**, against 214 passed / 8 failed before.

### 6.3 THE RECORD SWEEP LOST A DOCUMENT AND GAINED ONE, SO ITS COUNT DID NOT MOVE

`self_audit._record_documents()` reads **383** documents before this batch and
**383** after it, and the two 383s are not the same corpus:

    LOST   demo-output/website/motorbike-video/shotlist.md   (withdrawn, do not cite)
    GAINED verification/campaign/MOVE_MAP_BATCH8_EXECUTION_2026-08-18.md

`RECORD_ROOT_NAMES` contains `WEB`; when `WEB` moves to `web/`, the markdown
still sitting under the legacy webroot in map-X3's never-move `motorbike-video/`
tree stops being swept. This batch's own record replaced it one-for-one **by
coincidence**, and the coincidence is the finding: batches 5 and 7 both caught a
shrinking sweep **by its count**, and a count could not have caught this one.

It is **reported and not adjusted.** No verdict moves — the one lost document is
a filming shotlist and `cited evidence paths` FAILs on both frames — and
widening `RECORD_ROOT_NAMES` mid-move is a mover changing a gate's reading for
its own convenience. What was added instead is an **assertion**, in the amended
test above: the number of records under the legacy webroot that no record root
reaches must stay at most one, so the day it becomes many the suite says so.
It is filed with D404.

---

## 7. THE GATES, BOTH SIDES, WITH THEIR FINDING SETS

Every frame below was re-established **after** an earlier baseline was found to
have overlapped this batch's own edit window by 63 seconds. That run was
discarded, the worktree was restored to HEAD blob-for-blob, and both gates were
re-run from a clean tree. A baseline measured across its own treatment is not a
baseline.

| gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees / 307 files / **1,510,309,145 B**, digests `1b53ed5a4e9d63cb` / `5519de4237b71ce4`, `walk_errors = 0` | **byte-identical**, same digests, `walk_errors = 0` |
| **G1** rides-along | 0 / 0 / 0 | **0 / 0 / 0** |
| **G1** goes-dark-after-batch-2 | **0** | **0** |
| **G1** `batch2_untracked` | **198** | **198** |
| **G1** tracked frame | 8,199 | **8,199** |
| **G2** control corpora | 301 path fields, **0 unresolved** | **301, 0** |
| **G3** root binding | `UNRESOLVED = (EVIDENCE,)`, `AMBIGUOUS = (CAMPAIGN, RUNS)` | `UNRESOLVED = (EVIDENCE,)`, **`AMBIGUOUS = (WEB,)`** |
| **G3** R13 name states | `WEB_*_HTML` all `legacy`, `WEB` `legacy` | **all `moved`**; `WEB` `both` |

**No gate was adjusted.**

**The carry set is 7H's and was not touched.** Both its trees
(`solve_registry`, `surfaces`) still sit under the old webroot; batch 8 moved
five files and none of them is under either tree.

**G3's `AMBIGUOUS` moved, and both halves of the move are correct.** `CAMPAIGN`
and `RUNS` cleared — they read `both` only because the served PNG was still in
`campaign/`, and R13 was the rule that owned it, exactly as batch 7 predicted.
`WEB` took their place and reads `both` because `web/` now exists **and** the
old webroot still holds `latex/` and `motorbike-video/` (map X3, they never
move) plus the two dark carry trees. `_bind()` prefers the successor, so every
consumer reads `web/`. Making `AMBIGUOUS` empty would mean moving trees the map
says stay.

**`SWEEP_ROOTS()` GAINED `web/`** — 12 roots to 13. A sweep that gains a root
walks more; the failure direction is the one that loses one.

**G2 was fired fifteen ways**, and arms 9-13 are R13 as a live two-way control:
before this batch each of the five served paths resolved to **itself**, after it
each resolves to its `web/` successor, while arm 1 (the `latex/` tree that does
not move) resolves to itself on both sides and arms 2 and 15 — one legacy
spelling and one `web/` spelling that never existed — return `None` on both
sides. A resolver that had started answering "web/" to everything would fail
arm 1 and arm 15; one that had stopped following R13 would fail 9-13.

### 7.1 `scripts/lab_check.py --no-tests`

| | before | after |
|---|---|---|
| verdict | **FAIL, exit 1, ran 20/20**, 319.1 s, **stderr empty** | **FAIL, exit 1, ran 20/20**, 320.9 s, **stderr empty** |
| finding set | 7 FAIL + 1 BLOCKING UNKNOWN + 15 unrun | 8 FAIL + 1 BLOCKING UNKNOWN + 15 unrun |

**The verdict lists were compared by `diff` over sorted output, not by eye, and
they differ by exactly one line:**

```
> FAIL scripts/check_docket_reconciliation.py: exit 2
```

**That line is a pre-commit-window artefact and it retires at this commit by the
check's own clause.** `check_docket_reconciliation` compares the docket in HEAD
against the docket in the worktree, and it says what it found: *"IN THE
WORKTREE, NOT IN HEAD (1): D404 -- UNLANDED WORK. ... Land it BY ID through the
private-index form; never by committing the worktree file, which captures every
other agent's row sitting in it."* That is this batch's own new docket row,
written and not yet landed, and the instruction it prints is exactly the commit
protocol being followed. Its own RECOGNITION control passed 5 planted forms and
correctly rejected 1 negative, so the check is discriminating rather than merely
firing. It is verified to return to PASS immediately after the commit, and that
verification is recorded rather than asserted.

**Everything else is unmoved**, `self_audit`'s fifteen-line finding block
included -- compared line for line and NUMBER for number, with exactly one
exception, and the exception is the one this batch is expected to move:

```
- [FAIL] cited evidence paths      441 of 1901  ->  483 of 1941
```

`rank claims carry the right values` at 4 travelling and **35** lab-record,
`placement words` at **80** lab-record, `campaign json citations` at 6 of 7,
`bundle drift` at 9 behind the tree, and all eleven WARNs are identical.

The seven FAILs are `check_belief_neutrality`, `check_pdf_surfaces`,
`check_proposal_surface_coverage`, `check_rung_attribution`, `contention_audit`,
`installed_registry`, `self_audit`, plus the standing
`BLOCKING UNKNOWN scripts/check_absolutes.py: exit 3`. **This is one more FAIL
than batch 7 handed over** — `check_belief_neutrality` (*"A ROUND ASSERTS
NEUTRALITY — route to a non-author grader"*) has appeared since `9f3971f6` and
is present on **both** of this batch's frames. Batch 8 did not cause it and did
not repair it.

`installed_registry`'s two failures are the `ubuntu crontab` DRIFT (a peer lane's
`.autostop-hold` refresher, added to the live crontab and not to the tracked
copy) and a STALE waiver. Both pre-date this batch and are on both frames.
Neither `scripts/demo_servers.sh` nor `scripts/audit_camera_discretion.sh` is a
registered installed artifact, so editing them added no registry finding — that
was checked before the edits, not after.

### 7.2 `pytest`

| | before | after |
|---|---|---|
| | **6 failed / 2,447 collected / 2 skipped**, 523 subtests, 1,189.6 s | **6 failed / 2,447 collected / 2 skipped**, 523 subtests, 1,185.9 s |

**The same six tests, in the same four modules, with the same per-module
counts**, and they are the standing baseline rather than anything this batch
did: `test_exec_bits` 1
(`ThisRepositoryTests::test_no_shebang_script_is_both_unexecutable_and_unregistered`),
`test_fail_open_scan` 1
(`TheScanRefusesItsOwnDefectTests::test_the_repo_scan_carries_frame_filter_and_commit`),
`test_installed_matches_tracked` 3
(`InstalledMatchesTrackedTests::test_no_registered_artifact_has_drifted_from_its_tracked_copy`,
`PendingInstallWaiversTests::test_no_pending_install_waiver_has_quietly_stopped_excusing_anything`,
`EveryFindingTheRunPrintsReachesTheExitCode::test_main_ACTUALLY_consumes_the_rule_and_not_just_prints_it`),
`test_pdf_surfaces` 1
(`TestFindsTheStaleArtifactByName::test_report_pdf_is_named_as_outliving_its_named_source`).

**Eight arms that WOULD have been in this column were repaired before the run
rather than after it** -- see section 6.2. Running the three edited modules on
their own, first, is the only reason this table reads 6 and not 14.

**THE TWO SKIPS ARE NAMED RATHER THAN LEFT BEHIND A COUNT.** They are
`sdk/tests/test_hand_carry.py::TheBatch2GateOnTheLiveTree::`
**`test_the_live_gate_reads_zero_under_the_ruled_option`** (`:618`) and
**`test_the_live_gate_reads_one_when_the_exclusion_is_dropped`** (`:623`), both
skipping on *"…`MESH_AUDIT_runs` holds no tracked file at HEAD: batch 2 or batch
7 has since run and this plant is spent"*. They are batch 7's spent plant, they
skip on both sides, and batch 8 neither put them there nor took them away —
`MESH_AUDIT_runs` is not among the five files this batch moves. The option-B arm
of the function they guard was fired by hand instead and read 655 against option
A's 198, both sides.

---

## 8. THE CITATION GUARD — 441 of 1,901 BEFORE, 483 of 1,941 AFTER, and the nowhere set is 9 over 5 plus exactly 3 the new root created

Measured with the guard's own regexes, roots and retraction pattern:

| | before | after |
|---|---:|---:|
| records scanned | 383 | 383 |
| repo-rooted citations | 1,901 | **1,941** |
| not resolving at the LITERAL path | **441** | **483** |
| …of those, resolving at the SUCCESSOR via `lab_paths.resolve()` | 432 | 471 |
| …**genuinely nowhere** | **9**, over **5** distinct paths | **12**, over **8** distinct paths |

**The trajectory: 12 -> 197 -> 333 -> 436 -> 441 -> 483 of 1,941.** The
handover figure was 440 of 1,897; this batch measured **441 of 1,901** on a
clean pre-move frame, a drift of +1 finding over +4 citations that arrived with
the corpus between R25's commit and this one, not with the instrument. Of the
483, **471 resolve at their successor the moment batch 9's resolver lands** —
the guard still does not follow a rename, and that is the whole of the increase
except for what follows.

**The nowhere set decomposes exactly, and nothing regressed.** It was 9 over 5
distinct paths; it is 12 over 8. **All nine of the originals are still there,
unchanged, at the same documents and lines.** The three additions are not new
breakage: they are three probe strings that only became citations because this
commit gave the guard a new root (section 8.1).

**The five genuinely-nowhere paths, named rather than counted**, because four of
the five are deliberate and only one is a real dangling citation:

Each row below QUOTES a path rather than citing it — **withdrawn, do not
cite** — and each row says so on its own line, because the guard's retraction
window is +/-2 lines and a five-row table is taller than that. Writing this
table without those words is how a record documenting nine findings becomes
fourteen.

| path | occurrences | what it is |
|---|---:|---|
| `demo-output/website/never_existed.md` | 2 | **G2's arm-2 must-not-resolve control**, quoted in two batch records. Nowhere by construction — withdrawn, do not cite. |
| `cases/tmr/a.json` | 2 | a worked example in the batch-5 and batch-6 records — withdrawn, do not cite. |
| `media/shoot.html` | 1 | the map's own **rejected alternative** for `shoot.html`. Batch 8 took the other branch, so it stays nowhere by decision — withdrawn, do not cite. |
| `scripts/analyze_fd.py` | 3 | **the one real dangling citation** — a script that never existed, cited by three documents; withdrawn here, do not cite. |
| `sdk/scripts/../../demo-output/website/closure_challenge_round5_qcr.json` | 1 | a `..`-relative spelling quoted in the batch-3 record — withdrawn, do not cite. |

### 8.1 CREATING `web/` GAVE THE GUARD A THIRTEENTH ROOT, AND IT IMMEDIATELY FOUND THREE

`SWEEP_ROOTS()` gained `web/` at this commit, so three strings in
`MOVE_MAP_EXECUTION_2026-08-17.md:179-180` were promoted from unanchored text to
repo-rooted citations: `web/benchmarks.json`, `web/plot.png` and `web/closure.md`
— withdrawn, do not cite them. They are **deliberately non-existent probe paths**
used in that record to falsify `check_absolutes`'s fail-open, and they were never
meant to resolve. Nothing regressed; the guard simply began reading a root that
did not exist until now, which is the GAIN direction.

**This is the sharpest argument yet for batch 9's two-way control.** Three of the
three new findings are quotations, not citations, and four of the nine standing
ones are too. A resolver that only follows renames will report all seven as
unresolved forever. The distinction it must make is *quoted vs cited*, and today
that distinction is made by a +/-2-line regex window that this very table
defeated on the first attempt.

**The resolver was NOT built here.** It is batch 9 and it is specified with a
two-way planted control — a citation that must resolve and one that must not —
and a resolver landed without that control is the shape of a guard that has
stopped discriminating. What batch 8 adds to the case for batch 9 is that the
nowhere set is stable at 9 over 5 across a move, and that **four of those five
are quotations rather than citations**, which is a distinction the resolver will
have to make and which the current `retracted` context window of ±2 lines makes
only by accident.

---

## 9. WHAT REMAINS

**For 7H** — untouched by this batch and byte-identical across it:
the hand-carry set, **2 trees / 307 files / 1,510,309,145 bytes**,
`demo-output/website/solve_registry` (300 files, 1,508,128,888 B) and
`demo-output/website/surfaces` (7 files, 2,180,257 B), both to `evidence/`.
`lab_paths.EVIDENCE` is the one name still in `UNRESOLVED`, deliberately, and
`unknown_reason()` turns it into UNKNOWN rather than a path that is not there.
Until they move, `lab_paths.WEB` reads `both` — and it will keep reading `both`
afterwards, because `latex/` and `motorbike-video/` never move.

**For batch 9** — the `check_evidence_paths_exist` redirect table of map section
4.2, with its two-way planted control. The case for it is now 471 followable renames, and section 8.1 adds a
requirement the earlier batches did not state: the resolver must distinguish a
QUOTED path from a CITED one, because 7 of the 12 unresolvable rows are
quotations and one of them is this batch's own record.

**Not batch 8's, recorded so nobody rediscovers them mid-window:**

- **D404**, the eight dangling assembled-from-segments constants (section 5.1).
- **The laptop bundle already ships a broken image.** Map section 3 defect 1:
  `scripts/build_laptop_bundle.py` copies the pages into `site/` and copies **no
  images**, so `closure.html`'s `<img src="campaign/…png">` resolves to nothing
  inside `dist/`. It is **pre-existing, not created here** — the page path is
  already correct through `lab_paths` and became `web/closure.html` at this
  commit without touching the image behaviour. Deliberately not fixed: it
  changes shipped bundle content, which is not a path move.
- **`docs/charters/COMPUTE_BUDGET_CHARTER.md:227`** states the old serving
  command in prose. It is a charter and the chief's to edit; reported, not
  touched.
- **`check_belief_neutrality`**, failing on both frames and not batch 8's.
