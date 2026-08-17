# Ladder V — V6 and V10 RE-GRADED after the 2026-08-15 repairs

**Date: 2026-08-15, ~19:16–19:40Z. Graded at HEAD `be0a0c5d`.**

> **LABEL AMENDMENT, 2026-08-17, at `3f46e4e9`, appended by a non-author of this grade and of the
> ruling that corrected it. Append-only under W-4: nothing below is deleted, renumbered, or
> re-measured away.**
>
> **Verdict of record for V6: `PASS`.** Every measurement in this document stands. What was wrong
> was the LABEL. `PASS WITH RESIDUALS` was withdrawn lab-wide at `7c44cbe2` (D249): it is absent
> from the five-term vocabulary fixed at `docs/charters/VERIFICATION_CHARTER.md:95-96` and restated
> at `docs/charters/REPORTING_CHARTER.md:210-211`, it appears nowhere in `docs/charters/`, and it is
> invisible to section 16's negative-verdict sweep **by construction**, because that sweep
> enumerates the vocabulary and this label opens with the word PASS.
>
> **Stripping the label does NOT automatically leave a plain `PASS`, so it was measured rather than
> assumed** — the same strip left `FAIL` on V5. V6-R1, V6-R2 and V6-R3 were re-classified against
> this rung's criterion as written at `LADDER_V_TRIPLE_VERIFICATION.md:332-334`, on the two-limb
> test the chief applied to V5, V12 and V14: an exception is IN SCOPE only if it sits inside the
> criterion's **frame** *and* maps onto a **named clause** of it. All three sit inside the frame
> (the currency block, §1 below) — but **none maps onto either clause**. Clause (i), *"every finding
> gets a round-5 verdict"*, is met at eleven rows over nine sections with no gap; clause (ii)'s QCR
> compliance line is present and answers four questions. R1/R3 are the preamble's byte-identity
> bookkeeping against the block's own earlier version, which the preamble itself demotes — *"Byte-identity
> is not the finding, though"*; R2 is a wrong line-distance in the **evidence** column beside a §4.8
> verdict that is correct and whose stated ground (§4.8 headed `FALSIFIED 2026-08-11`) is true at
> HEAD line 584. **All three are therefore OUT OF SCOPE, R-CONVERGE files them, and the rung is a
> plain `PASS`.**
>
> **They are filed at last, as `docs/DOCKET.md` D353.** This grade appended all three to the live
> rung and filed none of them; D233 recorded them only inside its own narrative. R-CONVERGE's
> plain-PASS route requires the filing to actually happen, and until now it had not.
>
> **Re-measured at `3f46e4e9`, not read** — in a clean detached worktree and again in the dirty
> checkout, identical in both, and both were run because `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` is
> modified in the working tree and a single-frame measurement could not have known the block was
> untouched. Four recognition controls planted by line index and read back before the run; all four
> fired. **Eleven rows, nine byte-identical, §4.7 and §4.8 differing** — V6-R1/R3 live and
> unrepaired. The §4.8 locator distance is now **584 − 323 = 261** — not the stated **212**, and no
> longer the **256** measured on 2026-08-16, so the residual has drifted a further five lines.
>
> **V10 is untouched by this amendment**; its `FAIL` is unchanged and unre-opened.

~~**Verdicts: V6 — PASS WITH RESIDUALS (three, all named below). V10 — FAIL (four blockers, all named below).**~~
**Verdicts: V6 — `PASS` (three findings, all named below, all out of scope, all filed as D353). V10 — `FAIL` (four blockers, all named below).**

This document re-grades rungs V6 and V10 of `LADDER_V_TRIPLE_VERIFICATION.md` after the repairs at
`87324012`, `7a0419f7`, `a20a720b`, `cafb3f8b` and `bd8280de`, superseding nothing in
`LADDER_V_V6_V10_GRADE_2026-08-15.md` (`377d6afb`) — that grade stands as the record of the pre-repair
tree, and one of its own figures is corrected here.

Everything below was **executed**, not read. Where a prior document and a measurement disagree, the
measurement is reported and the document is named.

---

## 0. Independence, and why the repository cannot establish it

**Git cannot establish it here.** Every commit on this box carries the same shared
`Ubuntu <ubuntu@ip-172-31-43-247…>` identity, so the author field discriminates nothing.
**Session-container start time also fails**: the container backing this thread has been open since
2026-08-04, long before any commit at issue.

**What does establish it is the dispatch record.** This thread's task first exists in the agent-thread
transcript `~/.claude/projects/-home-ubuntu-Certonomous/64b13819-….jsonl` **after** that file's final
record, whose timestamp is `2026-08-15T19:15:25.474Z` and whose content is the
`<task-notification>` reporting that the agent named *"Repair V6 and V10 failing surfaces"* had
**finished**. This thread's first executed command ran at `2026-08-15T19:16:20Z` (`date -u`).

Committer timestamps of everything this grade must be clear of:

| commit | committed (UTC) | subject (abridged) |
|---|---|---|
| `377d6afb` | 2026-08-15T02:55:46Z | the prior V6/V10 grade |
| `87324012` | 2026-08-15T19:08:21Z | V6's blocker repaired |
| `7a0419f7` | 2026-08-15T19:09:03Z | V10's three failing surfaces |
| `09234034` | 2026-08-15T19:10:22Z | D133 repair (carried a foreign docket row) |
| `a20a720b` | 2026-08-15T19:11:09Z | D93 closed on its repair half; D141, D142 filed |
| `cafb3f8b` | 2026-08-15T19:11:51Z | D93's closure sentence re-anchored |
| `bd8280de` | 2026-08-15T19:13:38Z | the repair's own self-inflicted fault 1, discharged |

The latest is 19:13:38Z; this thread did not exist until at least 19:15:25Z. **No sequence of events
makes this thread an author of any of them.**

**And no reader of the repository can re-derive that.** The evidence is a per-machine, untracked
`~/.claude/projects/…jsonl`. It is not in `git ls-files`, not in the ignored arm, not shipped. This is
exactly **D130**: the non-author rule is enforced by records that do not travel with the artifact. An
external reviewer must take this section on trust or reject the rung; there is no third option, and
saying so is part of the grade rather than a disclaimer on it.

---

## 1. Declared scope (R-CONVERGE)

**In scope — the two rungs' closing conditions as written, and nothing else:**

* **V6** (`LADDER_V_TRIPLE_VERIFICATION.md:79-81`): *"Re-run the §4 adversarial audit against the
  ROUND-5 entry specifically — the existing audit predates QCR; every finding gets a round-5 verdict,
  and QCR gets its own compliance line (used at solve time only? touched no test data? stated in the
  description?)."*
  → the currency block of `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:296-334`, its
  eleven rows, the §4 sections they summarise, and the QCR compliance table.
* **V10** (`:133-136`): *"Cross-surface number sweep: closure.html, the Active Research board, the wall,
  PRODUCT_LIST, and the submission package must all carry round-5 numbers with the same caveats — one
  inconsistent surface fails the rung."*
  → exactly those five surfaces: `demo-output/website/closure.html`,
  `demo-output/website/ACTIVE_RESEARCH.md`, `demo-output/website/wall/wall.json` (with its generator
  `sdk/scripts/build_benchmarks.py` and siblings `benchmarks.html` / `benchmarks.json`),
  `docs/PRODUCT_LIST.md`, `demo-output/website/closure_challenge_submission_round5/`.
* The **chief ruling at `04489465`** binds: the board referent is fixed by the claim, not by the rung.
  Undated present-tense claims grade against the **live** board; dated claims grade against the board
  they name, **and must name it by entrant count and retrieval date**.

**Out of scope, FILED not appended:** mechanical repo-wide surface discovery (V14's rung), `dist/`,
`latex/`, tracked PDFs, `docs/DOCKET.md` as a surface, and the P33 re-scope (D142).

---

## 2. V6 — the eleven-row verification, executed

### 2.1 The row count: ELEVEN. Confirmed.

Extracted programmatically (parse from the `| § | the finding as written |` header at `:310` to the
first non-pipe line), at HEAD and at `472f9f92`, sha256 per row:

| # | row key | HEAD line | byte-identical to `472f9f92`? |
|---|---|---|---|
| 1 | `**4.1**` | 312 | **yes** |
| 2 | `**4.1** *(citations)*` | 313 | **yes** |
| 3 | `**4.2**` | 314 | **yes** |
| 4 | `**4.3**` | 315 | **yes** |
| 5 | `**4.4**` | 316 | **yes** |
| 6 | `**4.5**` | 317 | **yes** |
| 7 | `**4.6**` | 318 | **yes** |
| 8 | `**4.7**` | 319 | **no** (corrected 2026-08-12) |
| 9 | `**4.7** *(asymmetry)*` | 320 | **yes** |
| 10 | `**4.8**` | 321 | **no** (repaired 2026-08-15 at `87324012`) |
| 11 | `**4.9**` | 322 | **yes** |

**Eleven rows, not twelve. The prior grade's twelve was wrong and the repair's eleven is right.**
The same extractor at `472f9f92` also returns eleven, so no row was added or removed in four days.

### 2.2 The ten: it is NINE at HEAD, and the repair's own edit is what made it nine

Run over four trees, `__pycache__` purged first:

| tree | rows | byte-identical | differing |
|---|---|---|---|
| `472f9f92` | 11 | 11 | — |
| `377d6afb` (pre-repair) | 11 | **10** | `§4.7` |
| `87324012` (the repair) | 11 | **9** | `§4.7`, `§4.8` |
| `bd8280de` | 11 | **9** | `§4.7`, `§4.8` |
| **HEAD `be0a0c5d`** | 11 | **9** | `§4.7`, `§4.8` |

`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:299-301` reads:

> *"**eleven rows, one stale — §4.8, repaired above.** Ten of the eleven are byte-identical to what
> `472f9f92` wrote (sha256 of each line, **HEAD against `git show 472f9f92:`**), the eleventh being
> §4.7, corrected 2026-08-12."*

At HEAD that is **nine of eleven**, and the two that differ are §4.7 **and §4.8**. The sentence is a
measurement of the **pre-repair** tree, written in the present tense, with `HEAD` named as its anchor,
in the same commit that falsified it. **This is D79's shape at zero commits' remove**: not a "before"
taken at an older commit, but a "before" taken on the tree the same edit was about to change. The
partition it asserts — {10 identical} ∪ {§4.7} = 11 — has no place in it for the row the block exists
to announce as repaired.

The enumeration two sentences later is, by contrast, exactly right: *"§4.1–§4.6 and §4.9 are
byte-identical and still right"* names precisely the nine rows I measure as identical. **Only the
numeral is wrong**, and it is wrong in the direction of counting the repaired row among the untouched
ones.

### 2.3 The repair's stated conclusion, tested directly

> *"byte-identity decides nothing either way — §4.8 was byte-identical and wrong; the other ten are
> byte-identical and still right."*

**The principle is correct and is the most valuable sentence in the block.** §4.8's row went from true
to false with nobody editing it, because the world moved (the board changed on 2026-08-11) and the
section it summarised was re-headed at `5c9c63fb` while its summary row was not. A diff-based currency
check would have reported this document clean for four days, and did.

**The arithmetic attached to the principle is wrong in two places**: it is nine, not ten (§2.2), and
§4.8 is no longer byte-identical, so the sentence's own contrast collapses if read at HEAD rather than
at 377d6afb. Restated correctly, and this version survives measurement:
*§4.8 **was** byte-identical and wrong; **nine** rows are byte-identical and still right; §4.7 is not
byte-identical and is right; so byte-identity predicts nothing in either direction.*

### 2.4 §4.8 now agrees with its section. Confirmed.

* Currency-block row `:321` — `**FALSIFIED 2026-08-11 — AND THIS ROW WAS THE STALE HALF OF THIS
  DOCUMENT FOR FOUR DAYS. CORRECTED 2026-08-15.**`, with the *"needs a network read this pass did not
  perform"* clause struck in place, not deleted.
* Section heading `:577` — `### 4.8 Leaderboard position is current — ~~VERIFIED~~ **FALSIFIED
  2026-08-11**`, unchanged since `5c9c63fb`.

**They agree.** V6's recorded blocker is discharged.

**But the row's own locator is wrong.** `:321` says §4.8 is *"212 lines below in this same file"*.
Measured, `(line of '### 4.8 ') − (line of the '| **4.8** |' row)`:

| tree | row | section | distance |
|---|---|---|---|
| `472f9f92` | 288 | 528 | 240 |
| `377d6afb` | 307 | 563 | **256** |
| `87324012` | 321 | 577 | **256** |
| HEAD | 321 | 577 | **256** |

**212 was never the distance at any commit.** It came from the prior grade,
`LADDER_V_V6_V10_GRADE_2026-08-15.md:148` and `:193`, which wrote *"`:519+`, 212 lines below in the
same file"* — and at `377d6afb`, line 519 is **§4.7's heading**, not §4.8's. The repair was dispatched
to verify rather than inherit, and on this one figure it transcribed. `/usr/bin/grep -c '212 lines
below'` returns 1 at `87324012` and 0 at `472f9f92`: the phrase is new prose, and it is new wrong prose.

### 2.5 The rest of the block, re-executed rather than read

Everything the block offers as its evidence, run at HEAD:

* **Eight round-5 CSVs**: all `1000` rows × `3` comma-separated columns, no header, zero alphabetic
  characters outside scientific notation. `sha256(AR_1_Ret_360.csv)` =
  `bb8d61fbbfd99f5099628cedf7b76a203558daa87e3235006b0c8527ea703e7e` — matches the `bb8d61fb…` the row
  claims and the value V4 traced end-to-end. ✔
* **§4.7's four external surfaces** — `benchmarks.html:92-94`, `benchmarks.json:56`, `wall/wall.json:56`,
  `sdk/scripts/build_benchmarks.py:126,138` — all four carry the organiser-baseline qualification in the
  same sentence as the count, and all four carry **2 of 8 / ZERO of eight**. ✔
* **QCR compliance line**: present, four questions (the rung's three plus the zero-fitted-parameters
  question), each with an executed anchor. ✔
* **Every §4 finding has a round-5 verdict**: nine sections, eleven rows, no gap. ✔

### 2.6 V6 verdict

~~**PASS WITH RESIDUALS.**~~ **`PASS`.** *(Label amended 2026-08-17 at `3f46e4e9` by a non-author;
see the LABEL AMENDMENT at the head of this file. The three residuals below are OUT OF SCOPE on the
two-limb test — inside the frame, mapping onto neither clause — so R-CONVERGE files them and the
rung is a plain `PASS`. Filed as `docs/DOCKET.md` D353. Nothing in the reasoning below is
withdrawn.)* The rung's closing condition as written is *every finding gets a round-5
verdict, and QCR gets its own compliance line answering three questions*. Both are met, and the row
that was failing currency is now current and agrees with its section.

**Residual V6-R1** — `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:299-300`: *"Ten of the eleven are
byte-identical … the eleventh being §4.7"* is **nine of eleven, differing in §4.7 and §4.8**, under an
explicit `HEAD` anchor. Self-inflicted by the commit that wrote it.

**Residual V6-R2** — `:321`: *"212 lines below in this same file"* is **256**, and 212 is a locator
transcribed from the grade being repaired, where it pointed at §4.7's heading.

**Residual V6-R3** — the block's headline conclusion about byte-identity is right in principle and
wrong in its count, so a reader who checks it finds the sentence false and may discard the principle
with it. That is the residual worth the most, because the principle is correct.

None of the three removes a verdict, changes a verdict, or touches the QCR compliance line, which is
why they are residuals and not blockers. All three are inside the block whose entire purpose is to
certify its own currency, which is why they are residuals and not nothing.

**Falsifier for V6.** Extract the eleven rows at HEAD and sha256 each against
`git show 472f9f92:demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`. If ten are identical and
only §4.7 differs, V6-R1 is withdrawn. Compute
`(line of '### 4.8 ') − (line of the '| **4.8** |' row)`; if it is 212, V6-R2 is withdrawn. Exhibit any
§4.x section whose heading verdict disagrees with its currency-block row, and V6 becomes **FAIL**.

---

## 3. V10 — every number re-derived, by two independent routes and a third

### 3.1 The routes

* **Route 1 — my own arithmetic.** `LIVE_BOARD` read out of `sdk/scripts/probability_of_rank.py` by
  `ast.literal_eval` on the module's assignment node (never imported), and `round5_per_case_full` /
  `rans_identity_floor_per_case` read out of
  `demo-output/website/closure_challenge_round5_qcr.json`. Min-over-entrants, rank-by-sort, done here.
* **Route 2 — `scripts/self_audit.py::_closure_facts()`**, loaded by file path and executed.
* **Route 3 — `sdk/scripts/probability_of_rank.py` re-executed end to end** (pure arithmetic over
  already-scored values; **zero scoring calls, zero solver runs, ledger unchanged at 6**), regenerating
  the bootstrap from its seeds rather than reading the committed record.

Route 3 exists because routes 1 and 2 are **not fully independent on two figures**: `self_audit.py:448`
states outright that the interval *"is the one number that cannot be recomputed here"*, and
`_closure_facts()` reads `interval` and `p_rank1` from `sdk/scripts/probability_of_rank_record.json`.
Route 3 regenerates them from `SEED_MAIN = 20260810` / `SEED_DOUBLE = 31415`.

**The routes do not disagree anywhere they overlap.** There is no finding here.

### 3.2 The per-case board, re-derived

Live board = six entrants, `fetched` = `2026-08-11T23:33Z`, corroborated by
`probability_of_rank_record.json` (`frame.entries` = 6, same `fetched`). Ours + six = **seven rows**.

| case | ours (`round5_per_case_full`) | live best-other | held by | we lead? | is our row the declined baseline? |
|---|---|---|---|---|---|
| `alpha_15_13929_4048` | 0.050105 | **0.0432** | Tian, Buchanan, Hickel & Dwight | **no** | no |
| `alpha_15_13929_2024` | 0.101112 | **0.0998** | Tian, Buchanan, Hickel & Dwight | **no** | no |
| `alpha_05_4071_4048` | 0.046108 | 0.0569 | Wu & Zhang | **yes** | **yes** |
| `alpha_05_4071_2024` | 0.071863 | **0.0748** | Yang | **yes** | **yes** |
| `AR_1_Ret_360` | 0.045470 | **0.0291** | Yang | no | no |
| `AR_3_Ret_360` | 0.039982 | **0.0311** | Yang | no | no |
| `AR_14_Ret_180` | 0.035339 | **0.0250** | Yang | no | no |
| `NASA_2DWMH` | 0.063198 | **0.0294** | Tian, Buchanan, Hickel & Dwight | no | no |

"Declined baseline" is `rans_identity_floor_per_case[case] == round(ours, 4)`; it holds on exactly the
two cases we lead, by route 1, and route 2 returns `declined = [alpha_05_4071_4048,
alpha_05_4071_2024]` by its own path.

**We are behind on both hills.** 0.050105 > 0.0432 and 0.101112 > 0.0998. Confirmed.

### 3.3 Every V10 figure the repairs wrote, checked

| figure written by the repair | where | route 1 | route 2 | route 3 | verdict |
|---|---|---|---|---|---|
| best-on-board **2 of 8** | closure.html, ACTIVE_RESEARCH, PRODUCT_LIST | 2 (`alpha_05_4071_4048`, `alpha_05_4071_2024`) | `best` = same two | — | **correct** |
| **zero of 8 earned** by our model | all three | 0 (both wins are the declined floor) | `earned` = `[]` | — | **correct** |
| overall **rank 1 of 7** | PRODUCT_LIST `:53` | 1st of 7 (0.056647 < 0.0580 < … < 0.0779) | `entries` = 6 ⇒ 7 rows, `our_overall` matches | `POINT RANK 1`, 6 entries | **correct** |
| `AR_14_Ret_180` **4th of 7** | closure.html `:358`, PRODUCT_LIST `:108` | per-case ranks `[2,2,1,1,3,4,4,7]` ⇒ AR_14 = **4** | — | — | **correct** |
| interval **0–97% at 95%** | PRODUCT_LIST `:87`, `:94` | — | `interval` = `[0, 97]` | `double95` = 0.2%–96.9% | **correct** |
| **three deletions wide** | PRODUCT_LIST `:88-90` | — | — | LOO point ranks: `alpha_15_13929_4048`→2, `alpha_15_13929_2024`→3, `alpha_05_4071_4048`→2; all others→1 | **correct** |
| drop the hump ⇒ **P = 78.5%**, not 91% | PRODUCT_LIST `:90` | — | — | `drop NASA_2DWMH … P(rank 1) 78.5%` | **correct** |
| alpha_15 best-others **0.0592→0.0432**, **0.1195→0.0998** | ACTIVE_RESEARCH `:699-701` | 0.0432, 0.0998 (both Tian) | — | — | **correct** |
| P(rank 1) headline **50%** | closure.html, ACTIVE_RESEARCH, package | — | `p_rank1` = 50 | 50.15%, Wilson 50.00–50.31% | **correct** |
| margin over Yang **0.001365** | PRODUCT_LIST `:60` | 0.0580125 − 0.056647192 = 0.0013653 | — | −0.001365 | **correct** |
| **four** undecided pairs, incl. the leader | PRODUCT_LIST `:95-96` | — | — | Yang, Reissmann, Wu & Zhang, Tian **not decided**; Liu, Montoya decided | **correct** |
| "6 of 8 comparison figures were wrong" | ACTIVE_RESEARCH `:727-728` | **7 of 8** — see §3.5 | — | — | **WRONG** |

**Every arithmetic figure the four repairs put on the page re-derives.** The one count that does not is
a count *about* the repair, not a board figure — and it is wrong on two surfaces in the same way.

### 3.4 BLOCKER 1 — `closure.html:480-494`, the per-case table, untouched by the repair

The repair fixed the warn-box at `:353-358` and stopped there. **134 lines below its own new
`4th of 7`, the same page still says `3rd of 5` about the same duct.**

`:483-493`, live and unstruck at HEAD:

| table row | "Best published" printed | live best-other | tag printed | live truth |
|---|---|---|---|---|
| Periodic hill, steep, coarse | `0.0592` | **0.0432** | **`OUR MODEL LEADS`** (gold) | **we lose** |
| Periodic hill, steep, fine | `0.1195` | **0.0998** | **`OUR MODEL LEADS`** (gold) | **we lose** |
| Periodic hill, shallow, coarse | `0.0569` | 0.0569 | `BASELINE, NOT OUR MODEL` | correct |
| Periodic hill, shallow, fine | `0.0760` | **0.0748** | `BASELINE, NOT OUR MODEL` | correct |
| Square duct, AR 1 | `0.0387` | **0.0291** | **`2nd of 5`** | **3rd of 7** |
| Square duct, AR 3 | `0.0341` | **0.0311** | **`3rd of 5`** | **4th of 7** |
| Square duct, AR 14 | `0.0325` | **0.0250** | **`3rd of 5`** | **4th of 7** |
| NASA hump | `0.0364` | **0.0294** | `LAST` | correct |

**Seven of the eight "Best published" values are four-entry-board numbers.** Three placement tags are
four-entry ordinals. **Two rows carry a gold `OUR MODEL LEADS` badge on cases we do not lead** — and
the page's own lede fifteen lines above, at `:474-476`, already says *"both `alpha_15` hills lost to
Tian, Buchanan, Hickel and Dwight."* The page states the correction in prose and the error in the
badge, and the badge is the half a reader sees first. `OUR MODEL LEADS` predates this repair
(`8eae5cec`) and is a **present-tense, undated claim**, so under the ruling at `04489465` it grades
against the **live** board, where it is false.

### 3.5 BLOCKER 2 — the disclaimer meant to cover Blocker 1 is wrong twice

`closure.html:480-482`:

> *"The **fourth column** below compares against the best of the *four*-entry board and has not been
> re-derived against the six; against the six, the "best published" column would be lower on **six of
> the eight rows**."*

1. **It names the wrong column.** The columns are `Test flow | Best published | Certonomous |
   Uncorrected | (tag)`. The stale column is the **second**. The **fourth** is `Uncorrected`, the
   organisers' untouched standard solve — and the lede at `:472` says so in exactly those words
   (*"in the fourth column, against the untouched standard simulation"*). A reader following the
   disclaimer checks the one column that is not stale.
2. **Its count is wrong.** Re-derived: the "best published" column is lower against the six-entry board
   on **seven** of the eight rows (all but `alpha_05_4071_4048`, whose 0.0569 is still Wu & Zhang's and
   still the minimum). It has been wrong since it was written at `5c9c63fb`, when the board was already
   six entries deep.
3. **It covers neither the placement tags nor the `OUR MODEL LEADS` badges** — the two claim classes
   that actually flip.

### 3.6 BLOCKER 3 — `ACTIVE_RESEARCH.md:12`, `:18`, `:562`: three live `rank 1 of 5`

Unstruck at HEAD, all three about the **current entry of record**:

* `:11-12` — *"Last updated: 2026-08-07 UTC (Ladder C — **round 5 is the entry of record: overall 0.0566,
  rank 1 of 5 scored locally at benchmark commit `deb91557`**"*
* `:17-18` — *"**round 5 (2026-08-07) is the entry of record: overall 0.0566, locally rank 1 of 5**"*
* `:561-563` — the Ladder C section headline: *"**Round 5 (2026-08-07), the entry of record: … RANK 1 of
  5 scored locally at benchmark commit `deb91557`**"*

Each fails **both** halves of the ruling at `04489465`. The denominator is the four-entry clone's; the
live value is **1 of 7**. And each identifies its board **by commit** — which the corpus's own repaired
rule, written by this same repair into `PRODUCT_LIST.md:97-99`, declares inadmissible: *"A commit anchor
is not an admissible board identifier: `deb91557` is the four-entry scoring clone and it scores but does
not rank."*

The same repair added a **frame warning** to this very file at `:662-672` stating *"The board of record
for **every ordinal on this page** is the SIX-entry board retrieved 2026-08-11T23:33Z."* The page now
contradicts its own frame warning three times, and the frame warning is 650 lines below the first
contradiction.

*(The `rank 3 of 5` at `:614` and `Best-on-board 5 of 8` at `:630` sit inside a paragraph explicitly
headed **"Round 4 (2026-07-31) *(superseded as entry of record by round 5 above, 2026-08-07)*"**. Those
are kept history under the same doctrine V6 applies to §4, and are recorded here as a residual rather
than a blocker — but they still name no board by count and date, and the class needs one ruling, not
three.)*

### 3.7 BLOCKER 4 — the repair's own new prose miscounts, on two surfaces, in the same direction

`ACTIVE_RESEARCH.md:726-728`, written 2026-08-15:

> *"**Six** of its eight comparison values were wrong against the live board, not one: the two alpha_15
> best-others (0.0592, 0.1195), `alpha_05_4071_2024`'s (0.0760), and all three duct best-others."*

Re-derived, the struck paragraph's eight comparison values against the live board:

| # | value as written | live | wrong? |
|---|---|---|---|
| 1 | `0.0592` | 0.0432 | ✗ |
| 2 | `0.1195` | 0.0998 | ✗ |
| 3 | `0.0569` | 0.0569 | ✔ **the only survivor** |
| 4 | `0.0760` | 0.0748 | ✗ |
| 5 | `0.0387` | 0.0291 | ✗ |
| 6 | `0.0341` | 0.0311 | ✗ |
| 7 | `0.0325` / `0.0350` | 0.0250 | ✗ |
| 8 | `0.0364` | 0.0294 | ✗ |

**Seven, not six.** The enumeration omits `NASA_2DWMH`'s *"0.0632 vs best 0.0364"* — 0.0364 is Wu &
Zhang's, the minimum of the **four**-entry column; Tian's 0.0294 is the live minimum. The `LAST` verdict
attached to it survives; the number does not.

**This is the same off-by-one as Blocker 2, six where the truth is seven, on a different surface.** One
of the two is four days old and one was written today, so it is not a shared source: it is the same
mistake made twice, and both times inside a sentence whose whole subject is a count that went stale.

### 3.8 The surfaces that PASS, verified rather than assumed

* **The wall.** `wall/wall.json:56`, `benchmarks.json:56`, `benchmarks.html:92-94`, and the generator
  `sdk/scripts/build_benchmarks.py:126,138`: hero KPI `0 of 8`, body `2 of 8`, the four-entry `4 of 8`
  struck and kept, the organiser-baseline disclosure in the same sentence as the count, and the four
  undecided pairs named. ✔
* **The submission package.** `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`: six-entry
  board named by count and retrieval date at `:54-55`, `:239-241`, `:385-386`; `2 of 8` and `ZERO of 8`
  at `:104`, `:112`; `P(rank 1) = 50%` and `0–97% at 95%` at `:434-435`, `:446`, `:457`; `78.5%` at
  `:510`; every four-entry figure struck in place. `MANIFEST.json` and `README.md` carry no board
  figures. ✔
* **`docs/PRODUCT_LIST.md`.** Every figure the repair wrote re-derives (§3.3). Its surviving `4 of 8` at
  `:125` is a statement *about* the held cover email's defect and carries its correction in the same
  sentence (*"states a best-on-board count of 4 of 8 that is 2 of 8 on the live board, and zero of 8 for
  our own model"*). ✔ — with the note that this is the **cover email itself** still needing the redraft
  the bullet describes, which is Katie's item and not a rung finding.

### 3.9 V10 verdict

**FAIL.** The rung's own words: *"one inconsistent surface fails the rung."* Two of the five surfaces
are inconsistent, and one of them is inconsistent **with itself** on the same page.

* **Blocker V10-B1** — `closure.html:483-493`: seven four-entry comparison values, three four-entry
  placement tags, and two gold `OUR MODEL LEADS` badges on cases lost to Tian, Buchanan, Hickel &
  Dwight. `3rd of 5` for `AR_14_Ret_180` sits 134 lines below the same page's repaired `4th of 7` for
  the same duct.
* **Blocker V10-B2** — `closure.html:480-482`: the disclaimer names the wrong column, undercounts by
  one, and covers neither the tags nor the badges.
* **Blocker V10-B3** — `ACTIVE_RESEARCH.md:12`, `:18`, `:562`: three live `rank 1 of 5` claims on the
  current entry of record, each naming the board by commit `deb91557`, each contradicting the frame
  warning the same repair added at `:662-672`.
* **Blocker V10-B4** — `ACTIVE_RESEARCH.md:726-728`: *"Six of its eight comparison values were wrong"*
  is seven of eight.

**Falsifier for V10.** Re-render `closure.html`'s per-case table from `LIVE_BOARD` and
`round5_per_case_full`: if column 2 reproduces as
`(0.0592, 0.1195, 0.0569, 0.0760, 0.0387, 0.0341, 0.0325, 0.0364)` and rows 1–2 reproduce as wins,
B1 falls. Show `Uncorrected` — not `Best published` — to be the column carrying four-entry board values,
and show seven of eight to be six, and B2 falls. Show any of `ACTIVE_RESEARCH.md:12/:18/:562` struck, or
naming the six-entry board by entrant count and retrieval date, and B3 falls. Show `0.0364` to be the
minimum of the six live entrants' `NASA_2DWMH` column, and B4 falls. **All four fall ⇒ V10 is PASS.**

---

## 4. The left-standing residual fault: the repairing agent's judgement was RIGHT

`bd8280de` discharged one self-inflicted fault and deliberately left a second: `_best_on_board_faults`
fires on `docs/DOCKET.md` because D93's closure note **quotes** `PRODUCT_LIST.md:79`'s withdrawn
sentence — *"AR_14 is now 3 of 5 and best-on-board is 4 of 8"* — in order to report that it was
withdrawn.

**Measured at HEAD:** `docs/DOCKET.md` returns **1** fault in production shape and **1**
whitespace-collapsed, and it is that quotation. The repair's *"2 → 1"* is confirmed on both shapes.

**The judgement was right, on two independent grounds, and the rung's criterion is what decides it.**

1. **`docs/DOCKET.md` is not a V10 surface.** V10 enumerates five: closure.html, the Active Research
   board, the wall, PRODUCT_LIST, the submission package. The docket is the lab's finding register, not
   a surface carrying round-5 numbers to a reader of the entry. The fault is outside the rung entirely.
2. **Even inside the rung it would clear it.** V10's test is *"carry round-5 numbers with the same
   caveats."* The quotation is immediately followed, in the same sentence, by *"both four-entry figures,
   live values **4 of 7** and **2 of 8** with **zero of 8** earned by our own model, both surviving rows
   being the organisers' own unmodified RANS field the decline gate passed through untouched."* The
   round-5 number is there; the baseline caveat is there; the withdrawn figure is marked as withdrawn.
   That is the strike-and-keep form the whole corpus uses.

A residual fault that is a quotation of a withdrawn figure is **acceptable when the correction and the
caveat travel in the same sentence, and only then**. That is the line, and this instance is on the right
side of it. The general point stands and is the transferable half: **a register that may not quote the
figure it withdrew cannot report a withdrawal**, and contorting prose to clear a guard that cannot tell
use from mention (D4) makes the record worse, not the guard better.

---

## 5. What the instruments could not tell me

Reported as facts about the guards, not about the text.

* **`board_placement_faults` returned `([], [])` — zero rule-A and zero rule-B faults — on
  `closure.html`, `ACTIVE_RESEARCH.md`, `PRODUCT_LIST.md` and
  `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`**, executed here against `{'entries': 6}`.
  `closure.html` carries `2nd of 5`, `3rd of 5` and `3rd of 5` live in that same text.
  **A 0/0 from this guard confirms nothing**, and Blockers B1 and B3 were found by re-derivation, not by
  it. The documented reasons all apply: **D88** (no arithmetic predicate), **D85** (strike-marked
  sentences skipped — and every corrected figure on these pages is inside a strike), **D89** (cannot
  fault any sentence about Yang in the shipping configuration, and Yang holds the live best on four of
  the eight cases and is named in three of the four repairs).
* **`_best_on_board_faults` never opens any of these files in production** (**D129**: its only caller
  binds it to the wall's `our_entry` string). Every hit I report from it comes from feeding it a file by
  hand. Fed the four surfaces it returns 2 / 3 / 4 / 3 hits, and **every one is a struck quotation of a
  withdrawn count** — it cannot tell use from mention (**D4**). Its `_BEST_COUNT` is bounded by
  `[^.\n]`, so multi-line struck quotations are invisible in production shape and visible only
  collapsed; I ran both shapes on `docs/DOCKET.md` and they agree at 1.
* **Nothing in this lab compares a summary block's row against the section it summarises.** That is
  precisely V6's blocker (D141) and it is still true after the repair: the two residuals in §2 —
  a count of nine reported as ten, and a distance of 256 reported as 212 — are both machine-checkable
  in three lines and both survived a post-write sweep.
* **Reach, per arm, stated so the frame can be argued with.** Every count in §2 and §3 is from the
  **tracked** arm, by `git grep -a` (never bare `git grep`, which skips the 981 files git marks binary,
  as does the shell's `grep` function) and `/usr/bin/grep` on named paths. The **untracked** arm holds
  4 files and none of them a closure surface. The **gitignored** arm (37,244 files) was probed with
  `git ls-files --others --ignored --exclude-standard -z | xargs -0 /usr/bin/grep -aIlF -f <patterns>`
  in 11.6 s and returned **one** hit: `dist/certonomous-demo/site/closure.html`, a *different* build
  from the tracked page, carrying the same five stale table tags and no `4th of 7`. It is inside this
  dispatch's do-not-touch list and is **FILED, not repaired** (D143). The **run tree** at
  `/home/ubuntu/certonomous-runs/` was probed by filename to depth 6 for `*.html`, `ACTIVE_RESEARCH.md`
  and `PRODUCT_LIST.md`: only DAFoam/OpenFOAM report pages, no closure surface. **A full content grep of
  the run tree exceeded 120 s and was not completed** — that is the hole in this grade's frame and it is
  stated rather than papered over.
* **Before and after were taken on the same tree.** Every byte-identity and line-distance count in §2 was
  run at HEAD *and* at `472f9f92`, `377d6afb`, `87324012` and `bd8280de` from the same working copy, with
  `__pycache__` purged before each cell — because a "before" taken at an older commit lets a repair's
  self-inflicted damage cancel invisibly (**D79**), and §2.2 is that exact failure caught only because
  the before was retaken.

---

## 6. Summary

| rung | verdict | what decides it |
|---|---|---|
| **V6** | ~~**PASS WITH RESIDUALS**~~ **`PASS`** (V6-R1 nine-not-ten; V6-R2 ~~256~~ **261**-not-212 at `3f46e4e9`; V6-R3 a right principle with wrong arithmetic attached) — *label amended 2026-08-17; all three findings are out of scope and filed as D353* | eleven rows confirmed; nine byte-identical confirmed; §4.8's row and §4.8's heading agree; every §4 finding has a round-5 verdict; the QCR compliance line answers all three questions and a fourth |
| **V10** | **FAIL** (V10-B1 the per-case table; V10-B2 its disclaimer; V10-B3 three live `rank 1 of 5`; V10-B4 six-not-seven) | *"one inconsistent surface fails the rung"* — two of five are inconsistent, and `closure.html` contradicts itself on the same page |

Every arithmetic figure the four repairs put on a surface re-derives correctly by three routes. **What
failed is not the arithmetic — it is reach.** Three of the four repairs stopped at the sentence they
were dispatched to fix while an older, larger, more visible copy of the same claim sat further down the
same file: `closure.html`'s warn-box repaired and its table left, `ACTIVE_RESEARCH.md`'s paragraph
repaired and its own headline left. That is D93's recorded shape — *"the repair stopped one line
short"* — recurring on two more surfaces in the commits that closed D93.

No solver runs. No scoring calls. Ledger stands at 6. Nothing sent, uploaded or registered. The scoring
pin `deb91557` was not moved.
