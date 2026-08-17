# MOVE_MAP batch 3 — the path shim binds every rule, 98 consumers import it, and two rules turned out never to have been implemented at all

**No file was moved, renamed, copied, deleted or untracked. No directory was
created or removed. `git mv` was not invoked. `.gitignore` was not edited. The
shared index was not touched — no `git add`, no `git read-tree` against it.**
Batch 3 changes **no path**. It changes what NAMES a path: `scripts/lab_paths.py`
gains the rules it was missing, and 98 modules stop spelling the tree and import
it instead.

**Anchors.** Every path-derived count is over `git ls-tree -r -z --name-only`
at a named commit, never `git ls-files`. **HEAD moved once mid-pass** —
`267a4021` → `b8c398a4`, two commits from the thermal lane, **6,901 → 7,077
tracked paths** — and that is not incidental: it moved a ratified number, and
§1.2 is about which numbers a ruling makes safe against that and which it does
not. stderr was captured on every walk and every `git` invocation and was empty
on all of them. No count was piped into `head`.

**Inherited, not re-decided.** R25 = 315 with the campaign segment preserved;
`AWS_TREE_PLAN.md` in R1; option A for `MESH_AUDIT_runs` and `docs/campaigns`;
the reconciliation closing at 780 keep + 13,511 move + 7 exceptions + 0
unclassified at `4d7c195a`. This pass ratifies none of them and re-opens none of
them. It does report that **one of those numbers is a frame and has already
moved** (§1.2), and that the rule it came from is insensitive to the move —
which is the property the ruling was written for.

---

## 1. R25, bound — and the effect re-measured before it was bound

### 1.1 The measurement, reproduced exactly

`MOVE_MAP_EXECUTION_2026-08-17.md` §3.5 states that binding R25 moves 617 dark
trees out of STAYS PUT and leaves the carry set untouched. That was re-measured
here **before the rule was written**, by a probe that splices R25 into
`redirect()` and runs `hand_carry.derive` **twice against one
`git ls-tree -r HEAD` snapshot handed to both runs**, so the two sides cannot
differ by a frame.

At **`267a4021`**, 6,901 tracked paths, stderr empty:

| Bucket | R25 unbound | R25 bound | Δ |
|---|---|---|---|
| HAND-CARRY | 2 trees / 307 f / **1,510,309,145 B** | 2 / 307 / **1,510,309,145** | **none** |
| RIDES ALONG | 1,709 / 40,236 / 13,433,873,797 | 2,326 / 45,683 / 14,269,333,444 | +617 / +5,447 / +835,459,647 |
| STAYS PUT | 622 / 15,734 / 1,455,590,047 | 5 / 10,287 / 620,130,400 | −617 / −5,447 / −835,459,647 |
| DISCARD | 6 / 31 / 930,527 | same | none |

**617 trees, 5,447 files and 835,459,647 gitignored bytes move from STAYS PUT to
RIDES ALONG, and the carry set is byte-identical — the same two trees, the same
307 files, the same 1,510,309,145 bytes, the same sorted path digest.** The
claim reproduces to the byte. G1's baseline does not move, so binding R25 did
not need G1 re-stated.

The 617 are one tree fragmented: `docs/campaigns/F14-cooling-ladder/` holds
hundreds of maximal dark subtrees because 344 tracked files landed among them.
**They ride along ONLY if batch 7's `git mv` names the DIRECTORY.** A per-file
`git mv` loop leaves 835 MB of them behind, on top of the 10.5 GB §3.4 already
counts.

### 1.2 R25 = 315 IS A FRAME, AND IT HAD ALREADY MOVED BY THE TIME THE RULE WAS BOUND

Re-run at **`b8c398a4`**, 7,077 tracked paths, same paired form, R25 disabled by
a never-matching regex on one side and live on the other:

```
R25 tracked files: 490     K0c_runs 274, K0b_mesh_sensitivity 41, KV1_runs 175
STAYS PUT -> RIDES ALONG:  624 trees, 5,518 files, 836,073,120 gitignored bytes
carry set byte-identical:  True   (2 trees / 307 files / 1,510,309,145 B)
```

**`KV1_runs` did not exist at `4d7c195a` and holds 175 tracked files at
`b8c398a4`.** R25 is **490**, not 315, and the ratified figure was already a
reading at a frame when it was ratified — `MOVE_MAP_BATCH0_RULINGS_2026-08-17.md`
§1.1 says so in as many words and shows the same number holding across two
anchors, which is a different claim from the number being fixed.

**Nothing needs re-ruling, and the reason is the shape of the ruling rather than
luck.** RULING 1 is *"a run tree is classified by what it is"* — a **rule over a
pattern**, not an enumeration of two directories. `KV1_runs` matches `*_runs`,
so `redirect()` routes it to
`verification/runs/F14-cooling-ladder/KV1_runs/**` the moment it appears, with
no edit. Had the ruling been written as a list of the two trees it had seen,
batch 7 would today move 315 files and strand 175 in `docs/` with no line
anywhere saying so. **The count is the thing that drifts; the rule is the thing
that was ratified.** Every downstream figure derived from 315 — batch 7's
`8,643`, the `13,511` move subtotal — is stale in the direction of being too
small, and is re-derived by whoever runs batch 7 rather than carried.

### 1.3 What was bound, and where the decision lives

`_R25` and `_R25_BACK` are regex rules in `_special` / `_unspecial`, beside the
R20/R21 campaign split, because R25 is *"a child segment matching a pattern"*
and a prefix table cannot say that. The campaign segment is preserved. Two
BIND-ONLY rows (`F14_K0C_RUNS`, `F14_K0B_MESH_SENSITIVITY`) name the two trees
so `state()` reports each side of the move; `redirect()` never consults them,
because `_special` already answers and a prefix row that is dead code is a row a
later reader will trust.

**The inverse needed a discriminator and it is stated in the source.**
`verification/runs/` receives from both R20 and R25. R20 puts a
`*_runs`/`*_work` TREE name in the first segment; R25 puts a CAMPAIGN name. So
`_unspecial` reads R25's form only when the first segment is *not* itself a run
archive, and a campaign that named itself `X_runs` is read as R20's — R20 owns
that namespace and R25 is the guest in it. Without this, a citation to
`verification/runs/F14-cooling-ladder/K0c_runs/x` would be read back as
`demo-output/website/campaign/F14-cooling-ladder/K0c_runs/x`, a path that has
never existed.

`run_archive()` gained the campaign namespace: R25's trees sit one segment
deeper than R20's, and the accessor that answers *"where is run archive X"*
returned `None` for all 490 of them.

---

## 2. THE FINDING — R16 and R17 were never implemented, and the test that claims rule coverage could not see it

`lab_paths._MOVES` implements R1–R15 and R18–R25. **There is no rule for R16 and
R17**, and there never was. Measured at `267a4021` by classifying every tracked
path directly under the webroot:

| Loose webroot file | tracked | `redirect()` said | the map says |
|---|---:|---|---|
| `*.md` (R16) | **19** | `web/<name>` | `research/closure/md/<name>` |
| `*.json` (R17) | **21** | `web/<name>` | `research/closure/data/<name>` |
| `benchmarks.json` (R14) | 1 | `research/closure/data/benchmarks.json` | same |
| `benchmarks.png` (R15) | 1 | `research/closure/plots/benchmarks.png` | same |
| `*.html` (R13) | 3 | `web/<name>` | same |

**40 tracked files were routed to a root the map never sends them to**, and the
consequence is not cosmetic: `web/` is R13, and R13 is *five files*. A `web/`
holding 45 is a different tree from the one §1 of the map describes.

**Why no test caught it.** `test_every_move_rule_of_section_2_2_is_represented`
asserted rule coverage by reading `{m.rule for m in MOVES}` — the **table**.
R12, R16, R17, R20, R21 and R25 are not table rows; they are regex rules. The
test listed the rules it expected and R16/R17 were simply not on the list, and
could not have been checked from that collection even if they had been. It was
green throughout. `test_the_webroot_is_fully_classified` was green too, because
every webroot file *did* reach a rule — the wrong one. **A coverage claim taken
over the wrong collection is a claim about the collection.**

### 2.1 The repair, and why it is in batch 3 rather than filed

R16/R17 are bound as a loose-file rule in `_special`, excluding any path that
has its own table row (`_EXPLICIT_LEGACY`), with the matching inverse excluding
any target that has one (`_EXPLICIT_TARGET`). `benchmarks.json` stays R14's and
`wall/wall.json` stays R18's — the same destination for the JSON, and a
**different** destination for `benchmarks.png`, which is the one a loose rule
ignoring the table would have got wrong.

It is here rather than filed because **batch 3b could not be correct without
it.** Twenty-one of the ~40 `sdk/scripts/closure_*.py` generators write a
`closure_challenge_*.json` into the webroot. Converting them against an
unimplemented R17 would have bound each output to `web/`, and the whole point of
this batch is that a constant resolves correctly on both sides of the move.

`lab_paths.RULES` is now a named set covering table rows and regex rules alike,
with `test_every_move_rule_of_section_2_2_is_represented` reading it and
`test_the_rules_set_is_not_a_wish_list` as its control: every rule id claimed
must actually fire on some path, so a name added to the set without a rule
behind it does not turn the coverage test green.

`test_the_webroot_keeps_exactly_the_five_served_files` runs over the tracked
corpus and asserts `web/` receives **exactly** `SERVED_SET`. That is the
assertion that would have caught this on the day.

---

## 3. Batch 3b — 98 files, 140 edit sites, and the one that is not mechanical

### 3.1 The population, measured rather than carried

`MOVE_MAP` §4.3 says *"~150 files whose constant names its own subtree"*.
`git grep -a -l -e demo-output -e demo_output HEAD -- '*.py' '*.sh'` returns
**189 files, 148 of them outside `demo-output/` itself**, across **663 mention
lines**. Classified by token position — comment, docstring, string literal,
bare code — **499 are string literals, 114 docstrings, 31 comments**, and of the
148 files, **98 carry at least one genuine filesystem path constant**. The rest
carry only prose, citations inside record text, and labelled control-corpus
keys.

**140 edit sites in 98 files.** The rewrite is a table of exact
(file, old text, new text, expected count) triples that **validates every entry
against every file and writes nothing at all unless all of them match** — a
snippet that drifted is a stop, not a half-applied batch — and compiles each
rewritten source before staging it.

### 3.2 The bootstrap, and the one thing still re-spelled

Every converted file gains the same five-line block, inserted after the last
top-level import that precedes the first **code** use of `lab_paths` (found in
the AST, so a mention of the name in a comment cannot move it):

```python
import sys as _sys                       # noqa: E402
import pathlib as _pathlib               # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[N] / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths                         # noqa: E402
```

It is the one path still spelled per file, and it spells only `scripts/`, which
R9 leaves where it is. Stating that plainly is better than pretending the count
went to zero.

### 3.3 `scripts/self_audit.py` — the genuine multi-successor case, handled separately

This is the constant MOVE_MAP §4.1 calls *"the worst in the repo"*, and it is
not a prefix substitution. `WEB = REPO/"demo-output"/"website"` had children
joined onto it reaching **seven different destinations plus a whole-tree
`rglob("*.md")` that scatters across eight**. It was not rewritten as one name.
Each child was named separately, and `WEB` now means only the webroot proper:

| was | is | rule |
|---|---|---|
| `WEB / "mega-batch" / "ledger.jsonl"` | `lab_paths.MEGA_BATCH / "ledger.jsonl"` | R22 → `cases/` |
| `WEB / "wall" / "wall.json"` | `lab_paths.WALL_JSON` | R18 → `research/closure/data/` |
| `WEB / "campaign" / "F2_runs" / …` | `lab_paths.RUNS / "F2_runs" / …` | R20 → `verification/runs/` |
| `WEB / "campaign" / "F5a_….md"` | `lab_paths.CAMPAIGN / …` | R21 → `verification/campaign/` |
| `WEB / "dafoam" / …` | `lab_paths.DAFOAM / …` | R22 → `cases/dafoam/` |
| `WEB / "benchmarks.json"` ×3 | `lab_paths.BENCHMARKS_JSON` | R14 |
| `WEB / "ACTIVE_RESEARCH.md"` | `lab_paths.web_file("ACTIVE_RESEARCH.md")` | R16 |
| `WEB / "closure_challenge_*.json"` ×3 | `lab_paths.web_file(…)` | R17 |
| `REPO / "…/agenda/docket.json"` | `lab_paths.AGENDA / "docket.json"` | R23 |
| `WEB.glob("closure_challenge_submission*")` | `lab_paths.SUBMISSION_PACKAGES()` | R23, three destinations |
| `roots = ("demo-output/", …)` at `:4309` | `lab_paths.SWEEP_ROOTS()` | seven roots, five of which move |
| `_BUNDLE_PAGES` triple at `:6484` | `lab_paths.BUNDLE_PAGES()` | R13 |
| `WEB.rglob("*.md")` at `:4319` and `:4837` | `_record_documents()` over `lab_paths.RECORD_ROOTS()` | eight roots |

**`WEB.rglob("*.md")` is the one that had to be proved rather than argued**,
because it is the corpus of `check_evidence_paths_exist` — the guard §4.2 calls
the sleeper. Executed:

```
_record_documents()        372 documents
sorted(WEB.rglob("*.md"))  372 documents
identical lists            True
```

(371 at `b8c398a4`, 372 after a peer landed a record; the two sides are read in
one process, so the frame cannot separate them.)

Not the same count — the same list, in the same order. Before the move
`RECORD_ROOTS()` deduplicates to the single webroot, so the replacement cannot
walk overlapping roots and count every finding eight times, and it cannot walk
none and report a clean sweep of zero. Both failure modes are the ones this
corpus keeps re-finding, and both are excluded by comparing the lists.

Three new accessors carry the load: **`web_file(name)`** — the write-side
sibling of `resolve()`, because a generator names its output before the output
exists and `resolve()` returning `None` is the wrong answer for a write;
**`SUBMISSION_PACKAGES()`**; and `RECORD_ROOTS()`, which already existed.

### 3.4 What was deliberately NOT converted, and why

- **`scripts/check_absolutes.py:743`'s `_SHIPPING_RE`.** Untouched. The file is
  **byte-identical to HEAD**, verified by `cmp` against `HEAD:`'s blob. Its
  post-move form `^(?:web/|.*/latex/|.*\.tex$)` must land in the MOVE commit and
  **not before**, because no `web/` path exists yet and an early alternative is
  a rule matching nothing — §5 Class 2 of the execution plan, still queued for
  that commit, re-confirmed here rather than assumed. It is read at exactly one
  place, `:762`.
- **Shell.** `launch_solve.sh`, `demo_servers.sh`, `audit_camera_discretion.sh`,
  `mega_batch_keeper.sh`, `case_preflight.sh`. Shell cannot import the module.
  `demo_servers.sh:46` and `audit_camera_discretion.sh:141-142` are §5 Class 1
  and land in their move commits; `mega_batch_keeper.sh`'s three verbatim
  re-spellings are the pattern §4.1 names and remain, stated rather than fixed
  by a mechanism this batch does not have.
- **Record data.** `sdk/chief_engineer/exec_bits.py`'s **198-path executable-bit
  waiver inventory** is a frozen list of repository paths, not a constant; the
  `OWNERS` longest-prefix ladder at `:391-393` is a classifier over path
  strings, not a path. `scripts/check_pdf_surfaces.py`'s
  `KNOWN_CLASS_INSTANCES`, `scripts/check_convergence_validate.py`'s twelve
  fixture logs and `scripts/check_derived_figures.py`'s `SOURCES` keys are
  **labelled control corpora**. Rewriting a labelled corpus to make an
  instrument pass is how positive controls stop being controls; these get the
  batch-9 treatment — the guard resolves through `lab_paths.resolve()`, the
  corpus is not edited. `check_derived_figures.SOURCES` is the one of these
  already converted, because its values are consumed as a path and not as a
  label.
- **Synthetic fixture trees.** `test_bundle_drift_gate.py:90`,
  `test_form_or_value_and_empty_selection.py:471` and
  `test_proposal_surface_coverage.py:500` build a `demo-output/website` under a
  temporary root. `lab_paths` binds against the LIVE repository, so pointing a
  fixture at it would be wrong in the dangerous direction — the test would stop
  testing its fixture and start testing the lab.
- **`scripts/phase2_move_map.py`**, superseded by batch 0 and marked stale.
- **The 41 consumer scripts that live inside `demo-output/` itself.** They move
  with the corpus they belong to.

### 3.5 One behaviour change, declared

`scripts/add_proposals_{r5,r6,r7,r8,w5_flatplate}.py` held
`DOCKET = pathlib.Path("demo-output/website/agenda/docket.json")` — a
**relative** path, resolved against the caller's working directory, so those
five only ever worked when run from the repository root. Their sibling
`add_proposals_r4.py` used an absolute literal and
`add_proposals_supervisor_review_2026_08_07.py` used `REPO / …`. Bound through
`lab_paths.AGENDA` they are now absolute like the rest of the family. **That is
a behaviour change, in the safe direction, and it is stated rather than
absorbed into "behaviour-identical".**

`sdk/scripts/probability_of_rank.py`'s `OUR_RECORD` changed from
`sdk/scripts/../../demo-output/website/closure_challenge_round5_qcr.json` to the
normalised `demo-output/website/closure_challenge_round5_qcr.json`. Same file;
its one use is as a default argument to `open()`.

---

## 4. How "behaviour-identical" was checked — two instruments, and what each is blind to

**A path constant rewritten to a successor that does not exist yet resolves to
nothing, and a check whose corpus resolves to nothing returns a clean zero.** So
no rewrite was accepted on inspection.

**Instrument A — import and dump.** Every one of the 98 files is imported in its
own subprocess, before and after, and every module-level constant naming a
repository path is dumped and compared. **97 of 98 identical**; the one
difference is §3.5's `OUR_RECORD` normalisation. **22 files cannot be imported
at all** — they want `Ofpp`, `sklearn`, or a DAFoam container — and that is
recorded as `__import_error__` on both sides rather than counted as a pass: the
error class is identical before and after, and **no new import error was
introduced**.

**Instrument B — what paths does this file NAME.** A static AST evaluator
resolves each file's own repo-root aliases, `Path(...)`, `os.path.join`, `/`,
`str()`, `.resolve()`, `.relative_to()`, its own module-level path variables to
fixpoint, and every `lab_paths` name and accessor **called for real against the
live module**. The set of repository paths each file names must be identical
before and after, with the BEFORE side taken from `HEAD`'s blobs so both sides
pass through the same instrument. **94 of 98 identical.** The four:
`self_audit.py` "loses" three literals that are now produced by
`BUNDLE_PAGES()` — asserted separately, value for value, in §3.3;
`morning_report.py`, `probability_of_rank.py` and `race_benchmark.py` each
*gain* a path the instrument could not evaluate on the before side.

**Between them every file is covered by at least one instrument except
`sdk/workflows/race_benchmark.py`**, which fails to import and whose before-side
expression (`OUT_ROOT.parent / "demo-output" / …`) the static evaluator could
not reach. That one was read by eye. **Saying which file is unverified is the
point of the accounting.**

**Instrument C — the one that actually caught something.** Instrument B reported
`scripts/morning_report.py` as having *lost* a path, and the reason was a
`NameError` waiting to happen: `WEB` was split into six separately-named sources
and **an f-string 280 lines below still read `WEB`**. The module compiles, and
`lab_check.py` classifies it `writes-to-tree` and never runs it, so the suite
would have stayed green over a broken code path. Repaired to `SRC_AHMED`, and
then generalised: **every rewritten file's free names are compared against the
same answer from HEAD's blob**, so a name this batch un-bound is caught and a
name that was already undefined is not blamed on it. **0 of 98 files un-bind a
name that is still read.**

**Instrument D — the suite, and it caught the worst thing in this batch.**
Instruments A, B and C all said the rewrite was behaviour-identical, and on the
question they ask — *does this constant name the same path* — they were right.
The suite failed anyway: **`sdk/tests/test_empty_set_is_not_agreement.py` 4
failed and `sdk/tests/test_form_or_value_and_empty_selection.py` 4 failed**,
against a baseline of 0 in both, and the reason is the exact hazard this batch
exists to guard against, arriving from the direction nobody was watching.

Those two files are the lab's own **empty-set controls**. They blind a check by
rebinding `self_audit`'s module-level `WEB`, `REPO`, `ACTIVE`, `WALL`,
`CAMPAIGN` or `MISSION` to an empty directory, and assert the check returns
**UNKNOWN** rather than a clean sweep of nothing — defect class B1, L-45.
`_ABSENT_SOURCE_CASES` covers **thirteen checks** that way, each with a live-arm
control beside it.

**The rewrite reached past those handles.** `ladder = WEB / "campaign" /
"F5a_….md"` became `lab_paths.CAMPAIGN / "F5a_….md"`; `docket_path = REPO /
"demo-output" / … ` became `lab_paths.AGENDA / "docket.json"`; the two rglobs
became `RECORD_ROOTS()`. Every one of those is *more* correct across the move
and **none of them can be blinded any more**. `check_evidence_paths_exist`,
`check_ungated_completed_runs`, `check_fd_grades_current_standard`,
`check_rung_estimates_state_their_iterations` and
`check_closure_entry_of_record` kept reading the live tree and returned WARN,
PASS and FAIL where the tests demanded UNKNOWN.

**The guards were still correct. What was destroyed was the only evidence that
they are.** That is the same failure as a check reading nothing and reporting
clean, one level up: an instrument whose blindness can no longer be
demonstrated. It is worth stating plainly that **three instruments purpose-built
for this batch all passed it**, and the thing that caught it was a test somebody
wrote for a different reason eight weeks earlier.

**The repair is one function, `self_audit._at()`.** Every call-time path in the
module goes through it: a `lab_paths` answer is re-rooted on **this module's**
`REPO`, and on **this module's** `WEB` when `WEB` has actually been rebound —
the second condition being what stops the two re-rootings from fighting while
the webroot is still inside the repository. Once a region has genuinely moved
out of both, the answer passes through unchanged, which is what batches 4-8
need. All 13 absent-source cases and both live-arm controls pass again.

**Existence and non-emptiness, asserted.** The 98 files name **155 distinct
repository paths**. **42 are directories, all 42 exist, and none is empty.** 99
are files that exist. **14 do not exist — and the identical 14 did not exist
before the rewrite either**: synthetic fixture paths, a deliberate
must-not-match control (`a-surface-no-list-has-ever-contained.md`), and two
`…:1` finding strings. **`newly non-existent = []`.**

**The token count.** Across the 98 files, `demo-output` mention lines fall
**291 → 143**; 148 removed. The 143 that remain are prose, docstrings, labelled
corpus keys and record text, each of which is in §3.4 with a reason.

---

## 5. The gates, both sides, with their finding sets

**A verdict is not a finding set.** Below, `--no-tests` and the full suite in the
same frame both sides.

### 5.1 `scripts/lab_check.py --no-tests`

`FAIL`, exit 1, ran 20/20, before and after, with the **same seven non-green
checks in both frames** and no check changing verdict:

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

**One correction to the standing baseline's wording.**
`MOVE_MAP_BATCH2_EXECUTION_2026-08-17.md` §6.1 lists `check_absolutes` as
**FAIL**. At `b8c398a4` it is **UNKNOWN, exit 3, "outside the published
contract"** — still not green, still one of the seven, but a different class,
and the difference matters because 3 and 1 mean different things in this lab's
own contract. Recorded rather than smoothed.

The eighth non-green item of the standing baseline is the suite itself, which
`--no-tests` skips by design. **The full suite: `6 failed, 2436 passed` after,
against `6 failed, 2421 passed` before — the same four files and the same six
tests** (`test_exec_bits` 1, `test_fail_open_scan` 1,
`test_installed_matches_tracked` 3, `test_pdf_surfaces` 1). The **+15** is this
commit's own new tests in `test_lab_paths.py`. The intermediate run that found
the empty-set regression read **14 failed**; that is §4's instrument D and it is
in this record rather than smoothed out of it.

### 5.1a The two finding lines whose NUMBERS moved, and neither is a verdict

`diff` over the two runs' finding lines is **two lines out of 34**:

| Finding | before | after | why |
|---|---|---|---|
| `cited evidence paths` | 2 of **1,721** | 2 of **1,744** | the population grew by 23 because this pass and a peer each landed a record; **the finding is 2 in both** |
| `bundle drift vs shipped zip` | 0 missing, **6** behind | 0 missing, **8** behind | three of the 98 converted files — `sdk/chief_engineer/{agenda,lab_stats,ledger_learning}.py` — are shipped **verbatim** in the tracked `dist/certonomous-demo.zip`, so editing them moves the archive further behind the tree |

**The second is a real and permanent consequence of this batch**, not a
measurement artifact: `dist/certonomous-demo.zip` is rebuilt by
`scripts/build_laptop_bundle.py`, which `lab_check.py` classifies
`writes-to-tree` and this batch does not run. It is owed to whoever rebuilds the
bundle, and it will grow again with every later batch that touches a bundled
source. Neither line changes a verdict: `self_audit.py` is FAIL on both sides
for the same four FAIL sub-findings.

### 5.2 The three standing gates

| Gate | before | after |
|---|---|---|
| **G1** carry set | 2 trees, 307 files, **1,510,309,145 B** | **byte-identical** |
| **G2** control corpora | 223 path fields, 0 unresolved | 223, 0 |
| **G3** root binding | `roots OK`, `AMBIGUOUS = ()`, `UNRESOLVED = (CLOSURE, CLOSURE_DATA, CLOSURE_MD, CLOSURE_PLOTS, EVIDENCE)` | same |

**The carry set is byte-identical** — same two trees, same 307 files, same
1,510,309,145 bytes, same sorted path digest — under R25 bound and unbound, at
both anchors.

G2 was **fired both ways** rather than counted: a planted citation that must
resolve does (`demo-output/website/closure.html`), and one to a document that
never existed returns `None`. A corpus whose every field resolves can have
stopped discriminating, and the count alone would not say so.

G3's five `UNRESOLVED` names are the **destination-only** names — the
`research/closure/` family and `evidence/`, which R14–R18, R23 and the
hand-carry assemble and which do not exist until batches 5 and 7H. Leaving them
unresolved is the honest answer; `unknown_reason()` turns them into UNKNOWN
rather than into a path that is not there.

---

## 6. WHAT BREAKS IF BATCH 3 LANDS AND BATCH 4 NEVER DOES

**Nothing breaks, and unlike batches 0–2 that is not because the batch is
small.** It is because of the property `lab_paths` is built around: every name
is bound to a **pair**, resolved against the filesystem at import, successor
first and legacy second. With no move made, every name resolves to its legacy
path — which is the same path the literal named — and all three instruments in
§4 say so file by file. The tree is exactly where it was.

**Four things are permanently different, and they are the real answer:**

1. **The reorganisation stops being a flag day and becomes reversible in
   pieces.** This is the deliverable. Before batch 3, every later batch had to
   move files and edit their consumers in one commit or leave a window where a
   constant named nothing. After it, batches 4–8 move files and the constants
   follow by themselves; a half-landed batch 7 leaves a tree where `RUNS`
   resolves to the new path, `CAMPAIGN` to the old one, and both are right.
   **Skipping batch 4 costs nothing; skipping batch 3 makes every later batch
   thirteen times more expensive and each of them a flag day.**

2. **Two rules exist that did not exist before.** R16, R17 and R25 are now
   implemented. If the reorganisation is abandoned entirely, that is 40 + 490
   files' worth of routing that is correct in a table nobody executes — dead
   weight, not a defect. If it resumes in six months, it is 530 files that would
   otherwise have gone to the wrong root with nothing saying so.

3. **`check_evidence_paths_exist` now takes its corpus from a root list rather
   than from one tree**, and `SWEEP_ROOTS()` emits **both** spellings of every
   root while both exist. Before any move that is a no-op — 371 documents either
   way, identical lists. After batch 8 it is the difference between the guard
   reading 1,236 citations and reading almost none, which is §4.2's sleeper and
   the reason batch 9 exists.

4. **One latent `NameError` is gone from `morning_report.py`** — §4, instrument
   C. It was introduced by this batch and caught by this batch, which is the
   only reason it is in this list rather than in the next incident.

**And one thing that does NOT change, deliberately.**
`check_absolutes.py:743`'s `_SHIPPING_RE` still says `demo-output/website/`. If
batch 8 never lands, that is correct. If it lands without re-pointing it in the
same commit, the webroot silently stops being classified a shipping surface —
a severity-ranking degradation, not a fail-open (§2.1 of the execution plan
traced every consumer), landing at the priority a ranking defect earns. **It is
queued for that commit and this batch confirmed it is still there, unedited,
byte-identical to HEAD.**

---

## 7. Method

- **Every rule count is over `git ls-tree -r -z --name-only` at a named
  commit.** Never `git ls-files`. The two anchors are `267a4021` (6,901 paths)
  and `b8c398a4` (7,077); which figures are at which is stated beside them.
  `sdk/tests/test_lab_paths.py`'s own corpus sweeps were moved from `ls-files`
  to `ls-tree -r HEAD` in this commit for the same reason — a corpus-wide
  assertion taken over the index is an assertion about a stale corpus.
- **stderr was captured on every walk, every `git` invocation and every
  subprocess** and was empty on all of them.
- **No count was piped into `head`.**
- **Every before/after pair passes through the same instrument in the same
  frame.** The BEFORE side of instrument B is taken from HEAD's blobs, not from
  a copy saved earlier, so an improvement to the instrument cannot appear as a
  finding.
- **Nothing is ordered or selected by a date.** The one drift claim — `KV1_runs`
  — is a set difference between two named commits.
- **What is a moving target and what is not.** §1.1's bucket counts and §2's
  rule counts are over fixed commits and are not. §1.2's 490 and the byte totals
  in §1.1 and §5.2 are filesystem walks of live trees and are; the DISCARD
  bucket in particular grew from 6 trees to 13 during this pass because running
  the tests writes `__pycache__`, which is reported and never carried.
- **This record does not appear in its own results.** Every measurement was
  taken before the commit that lands this file.

## 8. What batch 3 did not do

No file was moved, renamed, copied, deleted or untracked; nothing left the disk.
No directory was created or removed. `git mv` was not invoked. `.gitignore` was
not edited. The shared index was not touched, and its pre-existing conditions
were inspected and reported, never reverted. `_SHIPPING_RE` was not touched. The
198 exec-bit waiver paths, the three labelled control corpora and every
synthetic fixture tree keep their literals. No shell script was converted. The
198 files of the execution plan's §3.1(c), the 78 of §3.1(a) and the 109 of
§3.1(b) remain tracked. `LOCATIONS.md` was not updated and is still owed from
batch 2. No solver was launched and nothing was registered.
