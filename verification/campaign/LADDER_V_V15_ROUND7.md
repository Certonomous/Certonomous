# Ladder V — V15 round 7: the claims audit over the 08-12 and 08-14 text

**Grader:** a fleet agent that wrote none of the text under audit and none of the
repairs under test. **Executed 2026-08-14 23:42Z → 2026-08-15 00:27Z.** No solver
run, no scoring call; the scoring ledger stands at 6. Nothing sent, uploaded, filed
or registered externally; submission is PARKED and reserved to Katie.

**The verdict the termination rule asks for is a number, and it is not zero.**

---

## 0. R-CONVERGE — the scope, declared mechanically BEFORE any finding

Round 6's subject ended at `2266c4e3`. This round's corpus is the text that has
landed since, derived with `git log`/`git diff` and not from any list.

| item | value |
|---|---|
| base | `88e915e4` (2026-08-11 23:48:00Z), the last commit of 2026-08-11 |
| HEAD at declaration | `839f6355` (2026-08-14 23:40:10Z) — **99 commits, 117 files** |
| HEAD at verdict | `26fca317` (2026-08-14 23:56:40Z) — **101 commits, 118 files** |
| HEAD when this document was committed | `650c1e04` (2026-08-15 00:18Z) — one further commit (D88/D89) landed after the verdict was fixed; it is NOT graded here and is named so the omission is visible rather than silent |
| churn | `git diff --shortstat 88e915e4..26fca317` → **118 files changed, 38,505 insertions(+), 557 deletions(-)** |
| composition | **56 added, 61 modified, 1 deleted**; 111 prose-bearing (`.md/.py/.sh/.tex/.html/.json/.tsv/.cron`) |
| days | 24 commits on 2026-08-12, 77 on 2026-08-14, **0 on 2026-08-13** |

**HEAD moved three times under this round** (`f8c889cc` and `26fca317` landed at 23:55
and 23:56 while it was executing, both from a concurrent V8 re-verification pass;
`650c1e04` landed at 00:18, after the verdict was fixed, and is excluded).
Every measurement below names the commit it ran at. Neither of those two commits is
excluded — they are inside the declared range and §2/F1 was re-run at the final
HEAD.

**Pass criterion (termination rule clause 2):** a full re-run of V8, V10, V14 and
V15 over the text written by the previous fix round introduces **no new failures** —
not few, zero — and that zero is measured by an agent that wrote none of the text
and states its frame.

**Out of the declared scope → FILED, not appended.** Docket rows D90–D103.

**What this round does NOT re-litigate.** Round 6's F6 items 1 and 3 are charter
amendments owned by the lab owner (docket D38); nothing here reopens them, and
nothing here closes them either — **a rung cannot close over a rule set that
contradicts the charter defining what closing means**, so D38 remains a standing
blocker independent of this round's count.

### 0.1 What this frame structurally cannot contain

- **Rendered text.** `wall.html` proved the class exists this round: a page can
  carry a claim its bytes do not contain. Everything below is bytes.
- **Non-text PDF layers.** `pdftotext` gives the text stream; anything in a figure,
  a chart label or a font-embedded glyph run is invisible, and it silently drops
  en-dashes and `fi` ligatures.
- **The live leaderboard.** Every "compliant" verdict here is graded against the
  record's six-entry board fetched 2026-08-11T23:33Z and re-verified 2026-08-14T21:01Z.
  Nothing was fetched. If the board has moved again, every green below is the exact
  stale referent F2 is about.
- **Files above the guards' 4 MB ceiling**, and the ~6,938 tracked-but-gitignored
  paths that only `git ls-files` reaches. `git ls-files` was used throughout;
  the shell's `grep` (which is `ugrep --ignore-files`) was never used for a count.
- **Run archives outside the repo** at `/home/ubuntu/certonomous-runs/`.

---

## 1. Positive controls, before anything is believed

A sweep that finds nothing must first be shown able to find something — and, this
round, a sweep that finds *something* must be shown not to be finding its own frame.

| method | control | result |
|---|---|---|
| replaying a guard at a historical commit in a detached worktree | run `check_board_placement_words` at `48d3f05a` and see whether it reproduces the figure that commit published | **2 rule-A faults — reproduces the published figure exactly**, so the harness is sound before it is used to contradict anything |
| regenerating the frozen probability record | `python3 sdk/scripts/probability_of_rank.py --json <scratch>` against the committed `probability_of_rank_record.json` | **0 differing values** across the whole nested document, keys identical both ways |
| mutation on a scratch tree | unmutated `git archive HEAD` copy run first | control `12 passed, 1 skipped`, identical to the repo |
| purge discipline | `__pycache__` swept before every Python cell | done; stale bytecode has inverted mutation results in this lab |

### 1.1 A method of mine that failed its own control, withdrawn here rather than reported

I built a citation resolver over every backticked path, `test_*` name and
commit-shaped token in the 107 text files in range. It returned **62 unresolved
paths and 57 unresolved SHAs**. That number is a **frame artifact and is withdrawn**:
the "unresolved SHAs" are overwhelmingly commits in the *benchmark* repository
(`deb91557`, `1c4e22c8`, `d572d40c`) which `git cat-file` in this repo cannot see,
and the "unresolved paths" are overwhelmingly upstream project files, zip members
and run-archive paths that live outside this repo by design. The repo-rooted
citation question already has a correctly-framed instrument —
`self_audit.py::check_cited_evidence_paths`, **1 of 1112 repo-rooted citations
unresolved at HEAD**, and that one (`S1_FIML_FIELD_INVERSION.md:229` → `scripts/analyze_fd.py`)
predates this scope.

This is round 6's F3 lesson arriving on schedule: **I widened a matcher to buy
recall and ran no precision control over the widening.** One survivor of the sweep
is real and is filed as D100; the other 118 are mine.

### 1.2 A measurement of mine that did not reproduce, also withdrawn

My first full-suite run returned `1 failed` on
`test_calibration_scorecard.py::IntakeIsReconciled::test_a_record_dropped_with_no_refusal_recorded_is_caught`
(`AssertionError: -3 != 1`). Re-run alone: **18 passed**. That is a concurrency
artifact from another session writing proposal records mid-run, which is exactly
the diagnosis `d2d6bd6c`'s commit message gave for the same two failures. **The
chief's diagnosis is confirmed by execution and this line records that I tried to
contradict it and could not.**

---

## 2. Failures

Grouped by class rather than numbered by severity; the severity ranking is in §5.
Every one was executed by the grader, in this session, at a named commit.

### F0 — A check can switch off the runner's verdict by writing one line to its own stderr, and the shipped hook maps that to a passing push (docket D101)

`scripts/lab_check.py:690`:

```python
crashed = "Traceback (most recent call last)" in err
...
elif crashed and code != 0:
    v, why = UNKNOWN, ("the check crashed; a traceback is a statement about "
                       "the instrument, not about the lab")
```

`err` is the check's **own stderr**, which the check fully controls. And
`scripts/installed/pre-push:61-68` — the only shipped consumer, added in this same
scope — maps UNKNOWN and everything outside the contract to green:

```sh
3) echo "pre-push: UNKNOWN -- NOT blocking, and that is on purpose ..." >&2
   rc=0 ;;
*) echo "pre-push: the runner exited $rc, outside its own contract." >&2
   echo "          Not blocking; nothing was checked." >&2
   rc=0 ;;
```

**Demonstrated end to end in a scratch git repo** (never in this tree), with one
gate whose exit code is a genuine function of its finding, run twice with the same
finding and the same exit code 1 — the only difference being one line on stderr:

| run | printed | `VERDICT` | true exit | pre-push |
|---|---|---|---:|---|
| A — plain | `[FAIL   ] scripts/probe_gate.py` | **FAIL** | **1** | **blocks** |
| B — `+ sys.stderr.write("Traceback (most recent call last)\n")` | `[UNKNOWN] scripts/probe_gate.py` | **UNKNOWN** | **3** | **`rc=0`, does not block** |

**The finding text is still on stdout in run B.** The runner read it, printed it,
and did not act on it. The same escape exists through `usage_error` at `:703`
(`code == 2 and not out.strip() and err.strip()`), even though `EXIT_CONTRACT` maps
2 to FAIL.

**And the exit contract itself is untested.** Copying `scripts/lab_check.py` and
`sdk/tests/test_lab_check.py` into a scratch tree and mutating exactly one line —

```python
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}   →   EXIT = {PASS: 0, FAIL: 77, UNKNOWN: 99}
```

— gives **25 passed, control and mutant alike** (`__pycache__` purged before both).
Every whole-runner test asserts `rc == lc.EXIT[lc.FAIL]`, i.e. compares the
subprocess's exit code against the module-under-test's own dictionary. Nothing pins
0/1/3, and `pre-push` hardcodes `case "$rc" in 0) 1) 3) *)`, so under that mutation
every FAIL falls into `*)` → *"Not blocking; nothing was checked."* — **and the suite
stays green.**

**This is the round's highest-value finding and it is a new shape.** D78 recorded a
detector that switches *itself* off. This is one level up: **the check controls the
byte string that decides whether the runner counts its finding at all**, and the one
consumer treats the escape hatch as success. A gate whose "did this count?" predicate
is a substring of the graded party's own output is not a gate.

*Secondary, same file, same class:* `CHECK_DIRS = ("scripts", "sdk/tests")` at `:245`
is exactly the typed list the module's own docstring condemns (*"a runner with a
typed list of checks inside it is the same defect wearing a different hat"*), and
`sdk/scripts/` holds 73 tracked `.py` of which several are real gates
(`citation_tier_audit.py`, `closure_in_sample_gate.py`, `dow_2011_table42_check.py`,
`pope_1975_basis_check.py`, `closure_round5_points_order_check.py`) — not run, not
skipped, not in the 60, in no coverage statement. And `[PASS] scripts/installed_registry.py`
appears in the live run **above three bullets saying the lab's own apparatus is
PENDING and ABSENT**: sub-verdicts are scraped for display and never reach
`aggregate()`.

### F1 — The placement guard's own frame line ships a fault count that was already false in the commit that wrote it (docket D90)

`scripts/self_audit.py:2728`, generated into the live verdict of
`check_board_placement_words`, and its docstring twin at `:2461–2463`:

> *"…re-measured at `48d3f05a`, and takes rule-A faults from **2 to 68** over
> DISJOINT sets: **both current faults clear** and 68 new ones appear…"*
> *"…RE-EXECUTED at `48d3f05a` over the same **1455** opened surfaces…"*

Executed, three times, each in its own detached worktree with `__pycache__` purged:

| tree | rule-A faults under the four-entry scoring pin | surfaces opened |
|---|---:|---:|
| `48d3f05a` (22:20Z) — the commit the sentence names | **2** ✔ matches | **1465** ✘ not 1455 |
| `d2d6bd6c` (23:19Z) — **the commit that wrote the sentence** | **5** ✘ | 1476 |
| `26fca317` (HEAD) | **5** ✘ | 1479 |

The three extra faults are all in `sdk/tests/test_two_board_referents.py` —
`'sits at 6'`, `'rank 6'` and `'ranked 9th'` bound to Montoya — and **that file was
added by `d2d6bd6c`, the same commit that shipped the sentence.** So this is not
rot. The author measured the "before" at 22:20, then at 23:19 committed both the
measurement and the file that falsifies it, in one commit.

This is docket D79's shape at one commit's remove instead of five: **a repair's
self-inflicted damage cancelling invisibly because the "before" was taken on a tree
the same author then changed.** And it lands on the one function whose entire
recorded history — the ordinal vocabulary literal, the hardcoded count in three
surfaces, the stale reach table — is about literals surviving inside generated
text. `_place_reach_sentence()` and `_place_precision_sentence()` are generated;
this sentence is an f-string with `2`, `68`, `50`, `18` and `1455` typed into it.

**Severity: wrong when written.** The clause is the standing justification for NOT
re-pointing the name-to-rank binding to the live six-entry board — a live design
decision resting on a count that was wrong at the moment it was published.

### F2 — A repaired `.tex` ships beside an unrepaired `.pdf`, and the only thing that ever checked them is a rung report (docket D91)

`demo-output/website/latex/closure_challenge_report.pdf`, tracked
(`100644 ed88b507`), extracted with `pdftotext`:

```
L17:   a point estimate whose probability is P(rank 1) = 68%, and eight cases cannot pin that
L18:   tighter than 2–100% at 95%, with the lead over the rank-2 entry not statistically decided
L27:   deb91557  rank 1 of 5, scored locally, 0.002878 below Reissmann, Fang & Sandberg's
L1520: rank 1 of 5, scored locally; P 68% (2–100% at 95%)
```

`68%` ×14. `Yang` **0**. `0.0580` **0**. `six-entry` **0**. `0-97` **0**.
Two not-decided pairs, not four. It is a complete four-entry-board artifact.

Its `.tex` source is fully repaired — `0--97\%` ×16, `\textbf{six}-entry`, every
probability `68\%` inside `\sout{}`. The divergence was **created inside this
scope**: the `.tex` was rewritten at `2cec44ee` (2026-08-12 18:05Z) and the PDF blob
was last committed at `98a39662` (2026-08-11 03:29Z), 38 hours earlier.

**Why nothing caught it.** `/usr/bin/grep -c '\.pdf' scripts/self_audit.py` → **0**.
No live check in this lab opens a PDF. The only thing that ever did is
`campaign/LADDER_V_V14_SURFACE_DISCOVERY.md:150–154`, which opened all 68 PDFs with
`pdftotext`, found this one, and certified it:

> *"It is **CURRENT** — carries `0.056647` as the entry of record… Built from
> `closure_challenge_report.tex`; both files share mtime `2026-08-10 16:22`… **In sync.**"*

Today those mtimes are `2026-08-11 03:26` and `2026-08-12 17:54`. And there is no
build path: no `Makefile`, no `latexmk` invocation, nothing in `git ls-files`
rebuilds this artifact, though `pdflatex` is installed.

**This is a new shape, and it is the one worth carrying out of this round.** A14
demanded a *mechanical surface discovery* and got one; what it produced was a
**one-shot measurement written into a report**, and a report cannot notice that its
subject moved. **The surface class V14 discovered went dark the moment V14's sweep
ended, and its green is still on the record.** A rung that discovers a surface class
and does not leave an instrument behind has converted a finding into a certificate.

**Severity.** The PDF is not in `dist/certonomous-demo.zip` and is linked from no
HTML page — it is a tracked compiled deliverable, not a live public page, and this
report does not overclaim it as external. It is nonetheless the artifact anyone
asking for "the report" receives, and it states the banned form: a probability with
a superseded interval, against a board that no longer exists, naming the wrong leader.

### F3 — The 2026-08-14 rank repair fixed one page and left three four-entry sentences live on the other (docket D92)

`demo-output/website/closure.html`, live unstruck prose:

| line | text | why it is wrong |
|---|---|---|
| 389 | *"…0.0566 is the best overall number on the board — **0.0029 below** the published leader"* | 0.0029 is the four-entry margin over Reissmann. The live margin over Yang is **0.001365** — stated on this same page at `:145`, correctly, and struck there |
| 434 | *"— **comparable to the 0.0029 margin** over the published leader"* | same figure; and the sibling page `benchmarks.html:156` carries the identical sentence **already struck**: `<s>…comparable size (0.0024)</s> — <b>struck 2026-08-14.</b>` |
| 525 | *"…holds no official rank — **rank 1 of 5** is our local scoring at a pinned benchmark commit"* | the four-entry ordinal; the same page says `RANK 1 OF 7` twice. **No P, no interval, no board** — the form V8's 2026-08-12 recomputation note bans outright |

One repair pass, two sibling pages, one done. This is docket **D71's own shape**
(*"a correction applied to one surface and not travelled to the copies is not a
correction"*) recurring **on the same day D71 was filed**, and it is not caught by
`check_rank_claim_surfaces` because that check's companion test is **per file**: two
compliant paragraphs elsewhere in `closure.html` clear every claim in it.

### F4 — `docs/PRODUCT_LIST.md`: the repair stopped one line short, and the lab's own copy of the rule now names the banned interval (docket D93)

The 08-14 repair rewrote `:59–68` to the six-entry figures and stopped. What
survives immediately beneath it, as the tail of the sentence it replaced:

> `:69–71` *"Eight cases cannot resolve a rank probability better than **2–100% at
> 95%** (double bootstrap). The standing is **TWO CASES WIDE**: drop alpha_15 and we
> are rank 2 on the point score; **drop the hump and P = 91%**."*

All three figures re-derived by running `sdk/scripts/probability_of_rank.py`
(pure arithmetic over committed scores; no scoring call):

| claim | executed |
|---|---|
| interval `2–100% at 95%` | **0.2%–96.9%** (double bootstrap, 2,000×4,000, seed 31415) |
| *"TWO CASES WIDE"* | **three** deletions move us off point-rank 1: `alpha_15_13929_4048`→2, `alpha_15_13929_2024`→3, `alpha_05_4071_4048`→2 |
| *"drop the hump and P = 91%"* | drop `NASA_2DWMH` → **P(rank 1) = 78.5%** |

The same file states *"a standing three deletions wide"* correctly at `:91`. And
`:53` still reads **"ROUND 5, 0.056647, RANK 1 OF 5"** over a five-row board at
`:55` with no Yang and no Tian.

**The worst line is the rule itself.** `:75–76`:

> *"The figure TRAVELS with the entry, and may never appear without its interval
> **(2-100% at 95%)** and the not-decided pairs."*

That is the lab's own copy of the prohibition, stating the interval the
prohibition now forbids. It is the copy other passes read.

**And the frame that hides it was endorsed twice.** `docs/P33_CROSS_SURFACE_SWEEP.md`
ruled `docs/PRODUCT_LIST.md` out of scope as an *"append-only chronological log
whose historical figures are quotations rather than claims"*, and `docs/DOCKET.md`
D59 records that exclusion as *"a principled exclusion this row does not dispute."*
**Executed, the exclusion is false of this region**: `:53–76` is one live bullet
that the 08-14 repair pass itself edited. A principled exclusion that the repair
pass then writes into is no longer an exclusion.

### F5 — `docs/MOVE_MAP_HISTORY_PURGE.md` decides against a purge on a solver-log figure wrong by ~23× (docket D94)

The document's headline (`:14`) is that reaching 150 MB is *"structurally
impossible"*, and its decomposition ranks **solver logs third at 33.6 MB across 379
blobs** (`:91`, `:140`, `:163`) with a **KEEP** recommendation.

Measured at HEAD with `git ls-tree -r -l HEAD`, on the OpenFOAM `log.<solver>`
naming convention:

| frame | files | size |
|---|---:|---:|
| document's frame — `*.log` **suffix** | 441 | 50.2 MiB |
| OpenFOAM convention — `.../log.<solver>` | **778** | **761.9 MiB** |
| mesh files, for comparison | 374 unique blobs | 365.8 MiB |

**Solver logs are the largest category in the repository, larger than meshes, and
the document ranks them third and keeps them.** The frame error is the whole defect:
`log.pimpleFoam` has no `.log` suffix.

It contradicts itself twice on its own page — the Category-3 table gives one row as
*"~38 MB"* inside a category it totals at 33.6 MB, and `:17` reuses the same 33.6 MB
figure for build artifacts and wheels — and it contradicts its sibling:
`docs/PHASE2_STRUCTURE_PROPOSAL.md:133` says **778 logs**. Two documents in `docs/`
disagree by a factor of two about the same objects.

**W-5:** the file carries **zero** git-resolvable commit anchors against
present-tense state claims and a *"Tracked at HEAD: YES"* column.

### F6 — Three gates written after D78 exit 0 on their own findings, and a test pins one of them there (docket D95)

D78 was filed 2026-08-14 with the criterion *"a gate is a program whose exit code is
a function of its finding."* Executed at HEAD:

| gate | printed | true exit |
|---|---|---:|
| `campaign/F7_runs/f7a_contract.py F7a_R1/res32y128_base` | `VERDICT: FAIL` (max\|d\| 11.03% vs 5% tolerance) | **0** |
| `scripts/calibration_scorecard.py` | `satisfied : False`, `hit rate 3 of 9 (33%)` | **0** |
| `scripts/installed_registry.py` | 1 PENDING, 2 ABSENT | **0** |

Two of these are worse than a missing check:

1. **`sdk/tests/test_f7a_contract.py:576` asserts `out.returncode == 0`** on the
   exact case whose verdict is FAIL, under a docstring reading *"the verdict is
   meant to be re-derivable by anyone with the repo."* **Repairing the exit code
   reddens the suite.** The fail-open is not un-guarded; it is guarded in place.
2. **`calibration_scorecard.py`'s only non-zero path is a construction identity.**
   `:481` returns 2 only when `reconciles` is false, and `:315` defines
   `reconciles = len(on_disk) == len(admitted) + len(refused)`. Every iteration of
   `agenda.read_inbox()`'s loop terminates in exactly one of those two lists, so the
   sum **is** the file count. The live run prints `reconciles: 131 == 128 admitted +
   3 refused` and exits 0 while reporting every finding it has. **The instrument
   that grades this lab's forecasting cannot exit non-zero on a forecasting defect.**

`scripts/withdrawal_sweep.py` is the counter-example and should be said so: it
returns **EXIT=1** on today's tree (2 unowned supersessions), downgrades a broken
instrument to UNKNOWN(3) rather than swallowing it, and there is no state in which it
prints a defect and exits 0.

### F7 — The auto-stop test suite is satisfied by a comment that says a comment cannot satisfy it (docket D96)

`sdk/tests/test_autostop_gate.py:40` guards the three activity clauses of
`scripts/auto-stop.sh` with substring assertions against the raw file text —
`assertIn("pgrep -x", text)` for clause (1), the solver/mesher protection that stops
this box powering off mid-OpenFOAM-run.

`scripts/auto-stop.sh:80–81` is a **comment**:

> `# (1) Solvers and meshers, matched on PROCESS NAME. pgrep -x on the name cannot`
> `#     be triggered by a path, a comment, or a grep that mentions the name.`

Executed on a scratch `git archive HEAD` copy (control run first: `12 passed, 1
skipped`, identical to the repo). Deleted lines 82–84 — the entire
`if pgrep -x '…simpleFoam|…|snappyHexMesh|…'; then keep; fi` block;
`/usr/bin/grep -c simpleFoam scripts/auto-stop.sh` → **0**:

```
12 passed, 1 skipped
```

**The clause can be deleted wholesale and the suite is green, because the assertion
that guards it is satisfied by the comment denying that a comment can satisfy it.**
Clause (2) has no behavioural test at all — mutating its CPU threshold to
`-gt 999999999`, so no worker can ever hold the box, also leaves 12 passed.

This is a new shape and a mean one: it is not an identity in the arithmetic sense,
it is a **detector whose fixture is the documentation of the thing it is detecting.**

### F8 — `sdk/tests/test_exec_bits.py` is RED at HEAD (docket D97)

`0330d78c` (21:30Z), in scope: *"Register `f7a_contract.py` and `phase2_move_map.py`
as waived; **HEAD green on test_exec_bits again**."* At HEAD, 47 commits later:

```
FAILED sdk/tests/test_exec_bits.py::ThisRepositoryTests::test_no_shebang_script_is_both_unexecutable_and_unregistered
1 failed, 14 passed
```

> *"new shebang-bearing tracked file(s) with no exec bit and no entry in
> exec_bits.WAIVED_NO_EXEC_BIT … `scripts/docket_citation_guard.py`"*

The offending file is **the lab's own new docket citation guard**, landed at
`e6057707` (23:32Z), two hours after the commit that declared the register green.
Rotted since — but it is red on the tree this rung is being asked to close over, and
the register has now gone stale six times in three hours.

### F9 — A headline residual and its PASS are literals (docket D98)

`demo-output/website/dafoam/S1_zerocompute_2026-08-14/scripts/s1_zerocompute.py:295–296`:

```python
print("    ratio %.6f  cos %.6f  rms %.6f  -> agreement with the targets %.1e. G-P4: PASS."
      % (r_, c_, rms, 0.0))
```

`r_`, `c_` and `rms` are computed. The `0.0` that becomes the published
**`0.0e+00`** is a literal, and **`G-P4: PASS.` is inside the format string**. That
`0.0e+00` reached `docs/DOCKET.md` D67 and the `gate` field of a live proposal JSON.

**The number is not wrong** — D67's own amendment defends it (*"exact against
unrounded targets; the 1.2e-05 residual is the rounding of the published target"*),
and the sibling script computes the true residual as 1.2e-05. **The defect is that
the artifact offered as its reproduction cannot disconfirm it.** A gate whose PASS
is spelled in the print statement is the identity-as-control shape wearing a
run's clothes.

### F10 — The round's own correction mechanism produced a wrong correction, and the guard it built cannot detect the class it was built for (docket D99)

Four things, one root, all in the last ninety minutes of the scope.

**(a) `docs/DOCKET.md` D84's census is wrong when written.** Its headline reads
*"**Three** surfaces disclose the D63 mis-citation and **all three** misdescribe
what D63 actually is."* Executed with `git grep -n D63` over the tracked tree,
**four** surfaces disclose it, and the fourth is right:

| surface | says D63 went to | |
|---|---|---|
| `scripts/self_audit.py:2549-2552` | *"an unrelated **auto-stop** defect"* | wrong |
| `sdk/tests/test_fault_message_matches_rule.py:36-38` | *"unrelated **auto-stop** defect"* | wrong |
| `docs/DOCKET.md` D54 closing note | *"an unrelated **auto-stop** defect"* | wrong |
| `scripts/docket_citation_guard.py:18` | *"an unrelated **S1 pre-registration** finding"* | **CORRECT** |

The correct one landed at `e6057707` (23:32:20Z) — **eight minutes before D84's own
commit `839f6355`** (23:40:10Z), by the same round, in the file D84's settlement
column names by path. **The row filed to catch a wrong correction is wrong about
how many corrections there are.**

**(b) The guard cannot see the class its own first section names.**
`scripts/docket_citation_guard.py:11` opens: *"the defect is a citation that
RESOLVES, not one that dangles."* It detects only the dangling kind. D84 says so
itself — and D84's own two live examples (`S1_PRIORS_PREREGISTRATION.md:608`
citing `D8` for what is `D8b`, and `PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md:203`
citing `D51` for a finding no row was filed for) sit **inside** the guard's 164
counted citations and pass. That is honestly disclosed and not a defect. What
follows is.

**(c) The guard's control census is stale by two, in the file, within its own round.**
`:84` states *"**Four** cells run before the live sweep."* Executed:
`/usr/bin/grep -c 'cell("'` → **6**, and the live run prints **6** `[ok]` lines.
NEG4 was added at `9daef4c9` and NEG5 at `9ddf0eeb`, neither updating the census.
`839f6355`'s commit message says *"six controls green"* — **the message got it
right while the file it describes still says four**, which is docket D83's own
class one level down.

**(d) The guard's load-bearing design claim has no executable control behind it.**
`:238-240` prints:

```
[info] NEG2  the HEAD-only frame would have flagged it: True -- which is why the frame is the worktree
```

`strict = bool(unresolved(citations_in(neg2), alloc_c))`, and `alloc_c` is
`allocated_ids(_COMMITTED)` where `:195-196` are:

```python
_COMMITTED = "| D1 | a row |\n| D43 | another row |\n| **D44** | a row whose ID is bold |\n"
_WORKTREE  = _COMMITTED + "| D80 | a row this agent just wrote, not yet committed |\n"
```

`neg2` cites `D80`. The two "frames" are **two string literals that differ by one
appended line**, so `strict` is `True` by construction. It is appended with
`lines.append`, not `cell()`, so it is never asserted and cannot move the verdict.
And `/usr/bin/grep -n 'subprocess'` shows the guard's only git calls are
`ls-files` and `rev-parse --short HEAD` — **it never reads `git show HEAD:docs/DOCKET.md`.**
The claim "the frame is the working tree, not HEAD", which is the guard's whole
reason for its frame choice, is evidenced by variable naming.

**(e) And it fail-opens on a file it cannot read.** `sweep()` at `:294-297` is
`except (OSError, ValueError): continue` — the file is skipped and **still counted
in the published `files swept`**, so the reach number is an overcount by exactly
the files it failed to open, with no note.

### F11 — Minor, and stated because it contradicts three surfaces (docket D100)

`scripts/withdrawal_sweep.py:38` documents the WIDER set as *"§8.2's five,
**REPORTED only**"*. Executed: `--wider` → `VERDICT: FAIL`, **EXIT=1** on a
SESSION_ONLY finding, because `:485` feeds `WIDER_MARKERS` into the same `collect()`
that produces the verdict. The file's own usage comment at `:146` says *"gate on all
five"*, which is what the code does. One file, two answers.

### F12 — Three of the five audit documents written on 08-14 publish headline counts that reproduce at no commit, and one of them presents hand-composed text as machine output (docket D102, D103)

**(a) `campaign/WEEKLY_METRICS_2026-08-14.md` — a fenced block that its own caption cannot have produced.** `:9-19` is captioned
`git log --since='2026-08-07' --until='2026-08-15' --pretty=format:'%cd' --date=format:'%m-%d' | sort | uniq -c`
and contains the rows `0 08-09` and `0 08-13`. **`uniq -c` cannot emit a zero count** — a
bucket with no occurrences produces no line at all. The block is hand-composed and
presented as command output. Its headline `672 commits` (`:22`, `:37`, `:96`) and
`5,678 unique files` (`:47`, `:49`, `:96`) reproduce at no commit in the window;
measured at `650c1e04`, `git log --since=… | wc -l` gives **785** and an explicit
committer-date filter over a full `git log` gives **783**.

**And the mechanism behind the disagreement is the transferable part:**
`git log --since=<date>` is **not stable on this repository** — the probe that found
this observed **638** and **709** for the identical pinned invocation inside one
session, silently dropping an entire 71-commit day, and my own two frames differ by 2
at the same commit. `638 + 34 = 672`, and `34` is the hand-inserted `08-07` row whose
true value is 71. **Any recurring metric here built on `--since` is measuring the
traversal cutoff as much as the corpus.** This round's own scope declaration is
stated as an explicit commit range (`88e915e4..26fca317`) rather than a `--since`
window, which is why it is reproducible; that was luck rather than foresight, and it
is recorded so it becomes foresight.

**(b) `campaign/AUDIT_AGED_FAIL_SWEEP_2026-08-14.md` — a before/after measured across
a commit gap, with no anchor.** `:17` and `:20`: *"The self-audit identified **10
FAILs** and **8 WARNs**"*, *"Count: 10 FAILs, 8 WARNs, 3 INFOs"*. No commit anchor
anywhere in the file. Re-executed with the unmodified `self_audit.py` from three
trees: at `45922a65` (the tree the cited scratch output came from) **FAIL 10 / WARN
9**, the ten names reproducing exactly; at **`2c74a891`, the document's own correction
commit 24 minutes later**, **FAIL 8 / WARN 10**, because the two D56 bundle rebuilds
cleared exactly the two checks the document's own correction section discusses; at
`26fca317`, **FAIL 3**. `docs/DOCKET.md` D56 records *"9 FAIL, 9 WARN"* for the same
sweep. **Three counts (10/8, 9/9, 8/10) exist for one 24-minute window and none of the
three surfaces carries an anchor.** This is W-5 doing exactly the work it was written
for, uninstalled.

**(c) `campaign/DEAD_LEVER_AUDIT_ROUND5_2026-08-14.md` — a load-bearing negative claim
falsified by one file, and a zero that is an identity.** Its physics is the
best-verified thing in this whole round: §3.3's four archived logs reproduce
bit-for-bit (iteration-0 KSP residual `1.243721539281e+01` identical across all four,
86/86/79/79 iterations, one substantive line in an 830-line diff), and the refutation
of D40 stands. But:

- `:364` states *"`git grep` over the tracked frame finds no record naming a
  fleet-wide found-dead D3 or D5"*, and `:370` builds on it — *"one third of it is
  unfalsifiable"*. `docs/PRODUCT_LIST.md:1822-1826` is titled **"D3–D5, three more
  reopened"** and describes all three in enough detail to re-verify, landed at
  `093a4b37` on 2026-08-10, **a day before** the record the section calls pending.
  **Wrong when written**, and D60's remedy is built on the absence.
- `:237`'s *"rows carrying `metrics.mesh_refinement`: 0 of 52"* is derivable by
  construction: parsed over all 208,194 ledger rows, `mesh_refinement` occurs 69,288
  times and **every occurrence is under `design`, never under `metrics`, for any
  solver**. The zero would be zero for any selection. Its stated positive control
  (`:240-244`) demonstrates that `design.mesh_refinement` is findable — **a different
  key from the one being counted** — which is the identity-as-control shape with a
  control attached to the wrong noun.

**(d) `sdk/scripts/build_benchmarks.py:99-100` still hardcodes the four-entry board's
last place, directly beneath a comment about this exact regression.**

```python
# (That regression happened once: the round-5 session hand-updated benchmarks.json
#  and wall.json but left this literal at round 3; Ladder V rung V7 caught and fixed
#  it on 2026-08-08.)
_CLOSURE = {
    ...
    "target_rank": 4,
    "target_overall": 0.0779,
```

`0.0779` is Montoya's overall and `4` was Montoya's rank on the four-entry board; on
the six-entry board Montoya is **rank 6**. The literal propagates into
`demo-output/website/benchmarks.json` and `demo-output/website/wall/wall.json` —
machine-read travelling surfaces — and `sdk/chief_engineer/lab_stats.py:351` uses `4`
as its fallback default. `docs/P33_CROSS_SURFACE_SWEEP.md:48` flagged this on
2026-08-12 and it is unrepaired at `650c1e04`. **The same literal, in the same
generator, has now gone stale twice: once on a round change and once on a board move,
under a comment warning that it went stale on a round change.**

---

## 3. The counts, each with its frame

### 3.1 W-5 — commit anchoring in the documents created this round

**Frame:** the 19 `.md` files with `--diff-filter=A` in `88e915e4..26fca317`, counting
tokens matching `\b[0-9a-f]{8}\b` that `git cat-file -t` resolves to a commit.

| anchors | documents |
|---:|---|
| **0** | **5** — `TOKEN_INSTRUMENTATION_SCHEMA_2026-08-14.md`, `WEEKLY_METRICS_2026-08-14.md`, `docs/GITIGNORE_PROPOSAL.md`, `docs/MOVE_MAP_HISTORY_PURGE.md`, `scripts/installed/README.md` |
| 1–3 | 6 |
| 4–14 | 8 |

**This is the round's best news and it should be said plainly.** Round 6 measured
**263 unanchored present-tense state paragraphs in 52 of 61 new documents**. W-5
landed at `6d990fdc` at 21:01 on 2026-08-11 and the discipline has taken: the
grade documents, the DAFoam write-ups and the audits all anchor routinely, and the
five zeros are proposals and READMEs rather than measurement records. Of the five,
only `MOVE_MAP_HISTORY_PURGE.md` carries measured state claims — and it is F5.

### 3.2 Repo-rooted citation resolution

`self_audit.py::check_cited_evidence_paths` at HEAD: **1 of 1112 repo-rooted
citations do not resolve** — `S1_FIML_FIELD_INVERSION.md:229` → `scripts/analyze_fd.py`,
which predates this scope. My own wider sweep is withdrawn at §1.1.

`scripts/docket_citation_guard.py` at HEAD: **89 rows allocated, 164 cue-qualified
citations, all resolving**, with 1 positive and 5 negative controls all correct,
EXIT=0. Its reach is docket-ID citations only; it does not resolve path or test-name
citations, and it says so.

### 3.3 The full suite and the runners

- `python3 scripts/lab_check.py --no-tests` → **VERDICT: FAIL**, true exit **1**
  (12 checks ran, 60 not admitted, 7 unrun whose skip reason could hide a verdict).
  The runner's exit code agrees with its verdict; it is not fail-open at that level.
- `scripts/self_audit.py` at HEAD → **exit 1**, with `cited evidence paths`,
  `declared fleet vs work` and `bundle drift vs tree` FAILing. `bundle drift`
  correctly names `dist/certonomous-demo.zip` as 4 files behind the tree, so F3's
  shipping-archive lag is **detected and unrepaired**, not undetected.
- `sdk/tests/test_exec_bits.py` → **1 failed** (F8).
- Full suite, `python3 -m pytest sdk/tests -q -p no:cacheprovider`, `__pycache__`
  purged first: **3 failed, 1669 passed, 230 subtests passed, 0 skipped, 1038 s.**
  One failure is F8; one is `test_calibration_scorecard.py::IntakeIsReconciled`,
  which does **not** reproduce in isolation (§1.2) and is a concurrent-write
  artifact, exactly as `d2d6bd6c` said.

---

## 4. What was checked and found SOUND

An audit that reports only failures is not an audit.

- **The probability record reproduces bit-for-bit.** `sdk/scripts/probability_of_rank.py --json`
  regenerated against the committed `probability_of_rank_record.json`: **0 differing
  values** across every nested key, keys identical both directions. P(rank 1)
  **50.15%**, double-bootstrap 95% band **0.2%–96.9%**, point rank 1, leader **Yang**,
  and exactly **four** undecided pairs (Yang, Reissmann, Wu & Zhang, Tian/Buchanan/Hickel/Dwight)
  against two decided (Liu, Montoya). **Every figure the V8 rule travels with is
  independently re-derived here, and every one holds.**
- **`_derive_closure_facts`'s provenance check is a real staleness detector, not an
  identity.** It compares the frozen record's `entries`, `fetched` and `our_overall`
  against the live board and entry and degrades loudly. The interval a surface is
  judged against is derived, not typed.
- **The `_INTERVAL_DIALECTS` table is the right fix for the right reason.** A guard
  that failed `closure_challenge_report.tex` for spelling the interval `0--97\%` was
  repaired by enumerating dialects rather than by widening a pattern until the red
  file went green, with the two unexercised HTML-entity rows declared as such.
- **`closure_challenge_report.tex` and `DESCRIPTION_DOCUMENT.md` are compliant.**
  Every rank claim added in this scope carries P, interval, board and pairs; every
  superseded `68\%`/`2--100\%` is inside `\sout{}`/`~~…~~`; the historical `0.674`
  from the cold-repro pass is explicitly labelled a four-entry figure.
- **`benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `BOARD_RESCORE_2026-08-14.md`
  and `CLOSURE_SUBMISSION_REQUIREMENTS.md` are compliant.** The last makes no rank
  claim at all and says why — compliance by abstention, which is the correct move
  for a requirements document.
- **`docs/PHASE2_MOVE_MAP.tsv` fully checks out.** 20,202 rows plus its own headers,
  all source paths exist and are tracked, zero destination collisions, and every
  figure re-derives exactly at its own anchor `1503fa4d`.
- **`scripts/withdrawal_sweep.py`'s exit contract and controls check out** — the
  only gate in the new batch that fails closed.
- **The DAFoam S1 pair's measured numbers check out.** ~40 headline figures across
  both write-ups re-derived from the raw arrays with independent parsers; both
  documents carry verifying commit anchors.
- **`d2d6bd6c`'s diagnosis of the two suite failures is confirmed** (§1.2), against
  my own attempt to contradict it.
- **The tracked `auto-stop.sh` fix is real.** Its `.claude*` glob matches the live
  session directory now; the D65 defect is repaired in the tree, and the registry's
  PENDING waiver states, accurately and at length, that the installed copy is not.

---

## 5. The verdict

**The termination rule wants zero new failures over the previous round's output. It
is not zero.**

| class | count in scope `88e915e4..26fca317` |
|---|---:|
| Claims that re-execution **refutes** — wrong when written | **7** (F1's `2` and `1455`, F4's three figures + the rule text, F5's decomposition, F6's `calibration_scorecard` docstring, F9's literal, F10a's census, F10c's control count) |
| Instrument defects introduced this round | **6** (F0's self-degradation, F0's untested exit contract, F6's three fail-open gates and the test that pins one, F7's comment-satisfied guard, F10d's identity control, F10e's silent skip) |
| Repairs that landed on one surface and not its siblings | **2** (F2's PDF, F3's `closure.html`) |
| Frame exclusions falsified by execution | **2** (F4's P33/D59 exclusion of `PRODUCT_LIST.md`, F0's `CHECK_DIRS`) |
| Live red on the tree | **1** (F8) |
| Documentation contradicting its own code | **2** (F10c, F11) |
| Headline counts that reproduce at no commit | **3** (F12a's `672` and `5,678`, F12b's `10 FAILs`, F12c's falsified negative) |
| Identities presented as controls | **1** (F12c's `metrics.mesh_refinement` zero, whose control validates a different key) |
| Stale literal on a machine-read travelling surface | **1** (F12d) |
| **Discrete, individually actionable NEW MATERIAL FINDINGS** | **25** |

**Filed as docket D90–D103 (14 rows; findings sharing a root cause share a row).**

Ranked by what an outside reader would act on first: **F0, F2, F3, F6, F7, F4, F12,
F1, F5, F10, F8, F9, F11.**

### Is this round BELIEF-NEUTRAL? **No.**

R-VALUE closes a rung when two consecutive rounds return **only findings that would
not change an external reader's belief**. This round is not one of them, and the
count of twenty-five is the smaller reason. **Four of the twenty-five are new shapes**, and
three of those change what a reader should believe about the ladder itself rather
than about one file:

1. **F0 — the graded party controls the predicate that decides whether it was
   graded.** D78 recorded a detector that switches *itself* off. This is one level
   up: `lab_check.py` downgrades FAIL to UNKNOWN on a substring of the check's **own
   stderr**, and `scripts/installed/pre-push` — the runner's only shipped consumer,
   written in this same scope — maps UNKNOWN and every out-of-contract code to
   `rc=0`. Demonstrated with one gate run twice: same finding, same exit code, one
   extra stderr line, FAIL → UNKNOWN → push not blocked. And the numeric contract
   that binds the two can be mutated to `{0, 77, 99}` with all 25 tests green. **An
   outside reader told "this lab now runs one entry point over everything it knows
   how to check" would be believing something the mechanism does not support.**
2. **F2 — a rung's mechanical sweep left a certificate where an instrument was
   needed.** A14 was written after the ladder missed a shipping archive; it
   discovered the PDF surface class, opened all 68 of them, and wrote *"In sync"*
   into a report. Nothing recomputes that. Three days later the `.tex` was repaired
   and the PDF was not, and **no check in this lab opens a PDF at all**. A reader
   told "our mechanical surface-discovery rung passed" is reading a green that
   expired the day it was written.
3. **F7 — a detector whose fixture is the documentation of the thing it detects.**
   The solver-protection clause of the box's own power gate can be deleted entirely
   with its suite green, because the assertion is a substring match satisfied by the
   comment above the code — a comment whose text is *"pgrep -x on the name cannot be
   triggered by a path, a comment, or a grep that mentions the name."* This is not
   the identity-as-control shape already on the record (a quantity derivable from
   its own inputs); it is a *test corpus that contains its own answer key.*
4. **F1 — the "before" and the falsifying change in one commit.** D79's shape was a
   `+2` and a `−2` netting to zero across five commits. Here the author measured at
   22:20, and at 23:19 committed the measurement **and the file that falsifies it**
   together. The gap is not the mechanism; committing the measurement and its
   refutation atomically is — and no existing rule catches it, because the claim
   carries a perfectly good commit anchor pointing at a tree where it was true.

**And the standing blocker is unchanged.** Round 6's F6 items 1 and 3 (docket D38)
are charter amendments owned by Katie. Even a round of fourteen zeros could not close
this rung over them.

### The count for round 6's own termination question

Round 6 asked what zero would take and named F1, F2, F4, F7 as corrections the chief
could make and F5 as needing a frame fix. This round did not re-grade those; it
graded the text written since. **Five rounds running have now produced at least one
new shape.** The falling-count reading remains unavailable: 20 → 14 is two measured
points and the class did not narrow — it moved from lab records outward, onto a
public page (F3), a compiled deliverable (F2), and the box's own power control (F7).

### What would falsify this verdict

Stated plainly, because a verdict whose falsifier is unnamed is not a verdict:

1. **F0 falls** if `scripts/installed/pre-push` is never installed and never will be
   — it is currently **ABSENT** from `.git/hooks/`, which `installed_registry.py`
   reports. My answer is that the shape is in the *runner*, not the hook: the
   downgrade happens in `lab_check.py` and the cron line
   (`scripts/installed/certonomous-lab-check.cron`, also ABSENT) consumes the same
   codes. But if the intended consumer is a human reading stdout, F0 drops from a
   fail-open to a mislabel, and it should drop.
2. **F2 falls** if someone shows the PDF is untracked, or is regenerated by a build
   step I failed to find, or that a live check does open it. My frame is
   `git ls-files` plus `/usr/bin/grep -c '\.pdf' scripts/self_audit.py` → 0; a
   generator outside `self_audit.py` would defeat it.
3. **F7 falls** if a test outside the two files I ran plants a live solver process
   and asserts the box is held. I ran `test_autostop_gate.py` and
   `test_autostop_session_glob.py` only; a behavioural test elsewhere in
   `sdk/tests/` would defeat the mutation result.
4. **F1 falls** if `1455` and `2` reproduce on the *uncommitted worktree* the author
   measured at 22:20 rather than on commit `48d3f05a`. I measured the commit,
   because the commit is what the sentence names; a working tree I cannot see is a
   real possibility and would move F1 from "wrong when written" to "measured on a
   tree that was never committed" — a different and lesser defect.
5. **F4 falls** if `PRODUCT_LIST.md:69–76` is ruled historical prose after all. It
   would not be a good ruling — the 08-14 repair edited lines 59–68 of the same
   bullet — but it is a ruling available to the owner, and D59 has already endorsed
   the exclusion once.
6. **The whole verdict falls to neutrality** if F0, F2, F7 and F1 are shown to be
   instances of shapes already on the record before 2026-08-12. I searched the
   docket for `\.pdf` (**0 rows**) and read D78 and D79 in full to place F0 and F1
   against them; neither the comment-as-fixture shape nor the
   graded-party-controls-the-predicate shape appears in D1–D87 as far as I read
   them. **That is the weakest link in this verdict and I am naming it rather than
   burying it: I read the docket for these four shapes; I did not read all 89 rows
   against all twenty-five findings.**

### Provenance of the evidence, stated because R-ISOLATE part 3 requires it

I dispatched five execution probes and **re-executed the load-bearing step of every
finding above myself**, at a named commit, before writing it down: F0's two-run
demonstration and the `EXIT` mutation, F1's three worktree replays, F2's `pdftotext`
extraction and the `.pdf`-in-`self_audit.py` count, F3's and F4's greps and the
`probability_of_rank.py` re-derivation, F5's `git ls-tree` size measurement, F6's
three exit codes, F12's four checks, F7's clause-deletion mutation with its control, F8's pytest run,
F9's source read, F10's four checks, F11's two invocations. Two probe findings I
could **not** pin to my own satisfaction — `withdrawal_sweep.py`'s `SESSION_ONLY: 0`
and `DIFFUSE: 0` false zeros, and a claimed miscount in docket D59 — are **excluded
from the count** and carried into D98 as unverified leads rather than
reported as findings.

### The honest reading

The numbers in this corpus are, again, largely sound — the probability record
reproduces to the digit, the 20,202-row move map re-derives exactly at its own
anchor, forty DAFoam figures hold. **The failures are concentrated in the seam
between a repair and its copies** (F2, F3, F4), **in gates that report and do not
refuse** (F6), and **in one measurement committed alongside its own refutation**
(F1). That is a better disease than bad measurement, and it is the fourth round
running in which it is the diagnosis — which is itself the finding the termination
rule exists to surface.

**The ladder is not green, and round 8 exists.**

---

*Nothing in this round was sent, filed, uploaded or published. Submission is PARKED
and reserved to Katie. No solver ran; no scoring call was made; the scoring ledger
stands at 6.*
