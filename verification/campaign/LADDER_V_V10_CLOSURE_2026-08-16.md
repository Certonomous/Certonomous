# Ladder V — V10 closed at HEAD `6097856c`, 2026-08-16, by a non-author of the repair

*(HEAD advanced to `0035ef96` while this closure was being written.
`git diff --name-only fe54ec0a 0035ef96` over all five enumerated surfaces returned **zero files**, and
`git diff --name-only 6097856c 0035ef96` over this ladder file returned zero. Every figure and line
number below held at all three trees.)*

**Verdict: `PASS`.** Both blockers of the `1a08e75d` grade fell against the landed blobs at `fe54ec0a`,
and a whole-file sweep of all five enumerated surfaces — run with a positive control confirmed by
readback, a struck negative control, an over-blanking control and a live positive control against the
pre-repair tree — returned no live in-scope inconsistency on any of them.

**Why this closer existed.** V10 was graded `FAIL` at `1a08e75d` on two blockers
(`campaign/LADDER_V_V10_GRADE_2026-08-16.md`). Both were repaired at `fe54ec0a` (2026-08-16T17:10:19Z),
which closed by refusing to grade its own repair. That refusal was correct and it is why a third agent
was dispatched. The repairing agent's report was treated here as a claim to be tested, not as evidence:
every figure below was re-derived or re-executed, and none was copied from that report, from the grade,
or from the dispatch.

**Independence.** This grader wrote none of `fe54ec0a`, `1a08e75d`, `f3c27a0c`, `cca64eaf`, `60073572`
or `377d6afb`, and none of the text on any of the five surfaces. Independence rested on the untracked
dispatch record and not on git authorship, which carries one Ubuntu identity for the whole lab (D130).

**Tree stability.** `git diff --name-only fe54ec0a 6097856c` over `closure.html`, `ACTIVE_RESEARCH.md`,
all four wall members plus `wall/wall.html`, `docs/PRODUCT_LIST.md` and the whole round-5 package
returned **zero files**. Every measurement below was taken from `git show fe54ec0a:<path>` — the landed
blobs, not the working tree — and holds byte-identically at HEAD.

---

## 1. V10's declared scope, stated before anything was measured

`campaign/LADDER_V_TRIPLE_VERIFICATION.md:359-362`:

> **V10. Cross-surface number sweep**: closure.html, the Active Research board, the wall,
> PRODUCT_LIST, and the submission package must all carry round-5 numbers with the same caveats —
> one inconsistent surface fails the rung (the board was still showing round 3 at last report; that
> class of drift is what this rung exists to catch).

In this grader's words: **five artifacts are enumerated by name** — `demo-output/website/closure.html`;
`demo-output/website/ACTIVE_RESEARCH.md`; the wall (`wall/wall.json`, `benchmarks.json`,
`benchmarks.html` and the generator `sdk/scripts/build_benchmarks.py`, the four members graded under
that word since the 2026-08-15 regrade §3.8 — `wall/wall.html` was swept here as a fifth candidate
member rather than argued about, and returned zero); `docs/PRODUCT_LIST.md`; and
`demo-output/website/closure_challenge_submission_round5/`, all **eleven** tracked members.
**The claim class is round-5 numbers and the caveats travelling with them.** **The criterion is
disjunctive and carries no tolerance** — one inconsistent surface fails, with no count, no severity
floor and no exemption for an error sitting beside its own correction.

**The prior reading of the class boundary was tested here rather than inherited.** The `1a08e75d` grade
held that round-4 and round-3 figures kept as dated history are not round-5 numbers and so sit outside
the class, and routed two findings to the docket on that ground. Tested against the criterion's own
parenthetical — *"the board was still showing round 3 at last report; that class of drift is what this
rung exists to catch"* — the rung was declared against a surface **presenting a superseded round as
current**. A figure explicitly labelled and dated as superseded is not that drift; it is the record
performing its function. Executed, not asserted: all three sites the docket holds
(`ACTIVE_RESEARCH.md:73`, `:652`, `:668`) were read at the blob and each sits under an explicit dated
superseding header — `:73` under *"Update 2026-08-04 UTC"* naming round 4 the entry of record and the
round-3 headline superseded, `:652` and `:668` inside a block opening *"Round 4 (2026-07-31)
(superseded as entry of record by round 5 above, 2026-08-07)"*. **The prior reading held.** Section 5
records where it does *not* reach, which is a different question and the one this pass was asked.

---

## 2. The board, re-derived here

`LIVE_BOARD` was lifted from `sdk/scripts/probability_of_rank.py` by `ast.literal_eval` on the module's
assignment node — parsed, never imported — and joined to `official_test_harness_result.round5_per_case_full`
in `demo-output/website/closure_challenge_round5_qcr.json`. Board `fetched` = `2026-08-11T23:33Z`,
**six entrants, seven rows counting ours.**

| case | ours | live best-other | held by | rank of 7 | we lead |
|---|---|---|---|---|---|
| `alpha_15_13929_4048` | 0.050105 | **0.0432** | Tian, Buchanan, Hickel & Dwight | 2 | no |
| `alpha_15_13929_2024` | 0.101112 | **0.0998** | Tian, Buchanan, Hickel & Dwight | 2 | no |
| `alpha_05_4071_4048` | 0.046108 | 0.0569 | Wu & Zhang | 1 | yes |
| `alpha_05_4071_2024` | 0.071863 | **0.0748** | Yang | 1 | yes |
| `AR_1_Ret_360` | 0.045470 | **0.0291** | Yang | 3 | no |
| `AR_3_Ret_360` | 0.039982 | **0.0311** | Yang | 4 | no |
| `AR_14_Ret_180` | 0.035339 | **0.0250** | Yang | 4 | no |
| `NASA_2DWMH` | 0.063198 | **0.0294** | Tian, Buchanan, Hickel & Dwight | 7 | no |

Per-case ranks **2, 2, 1, 1, 3, 4, 4, 7 of 7**. Best-on-board **2 of 8**, earned by our own model
**0 of 8** — both survivors were the two rows the decline gate withheld our model from. Overall
`0.056647191704213645` = **rank 1 of 7**, margin to Yang's mean-of-eight `0.0580125` =
**`0.0013653082957863563`**. Input-side check available without a fetch: every entrant's eight per-case
values meaned to its published overall to 4 dp, **six of six**.

Two derived quantities were needed to adjudicate hits in section 4 and were computed here rather than
read. **Head-to-head wins against us, per entrant:** Yang 4 of 8, Reissmann, Fang & Sandberg 4 of 8,
Wu & Zhang 3, Tian, Buchanan, Hickel & Dwight 3, Liu, Wang, Zhao & Xiao 1, Montoya, Oulghelou &
Cinnella 1. **Duct standings:** the live duct leader was Yang at `0.0291 / 0.0311 / 0.0250`; Reissmann
placed 2nd, 2nd and 2nd of seven at `0.0387 / 0.0341 / 0.0325`; ours placed 3rd, 4th and 4th.

A known discrepancy, non-load-bearing and decided nothing here: the module's `SEED_BOUND_ON_OVERALL`
parsed as a rounded `0.0024`, which against the margin gives 175.8%, while the 177% carried in
`CLOSURE_CHALLENGE_STATUS.md` came from the equivalent-S bound. Both were consistent.

---

## 3. The `1a08e75d` falsifier, executed clause by clause against `fe54ec0a`'s blobs

The grade wrote itself a two-part falsifier, each part disjunctive, and closed *"Both fall ⇒ V10 is
PASS."* Each clause was executed at the landed blob.

### C1 — `closure.html`, §6 *"What is not solved"*

| clause as written | executed | met |
|---|---|---|
| *"Show `closure.html:558-561` struck"* | The false parenthesis `(0.0387, 0.0341, 0.0325 against our 0.0455, 0.0400, 0.0353)` sat inside a balanced `<s>…</s>` opening at **`:562`** of the landed blob — the repair having grown the paragraph, so the graded region moved down the file — measured at strike depth 1 and dated *"struck 2026-08-16"*. The attribution `the gap to <s>Reissmann</s> <b>Yang</b>` was struck and corrected in the same sentence at `:570`. **The depth probe was itself controlled**: a token known struck and a token known live in the same file returned depth 1 and depth 0 respectively. | **MET** |
| *"or show `0.0387 / 0.0341 / 0.0325` to be the minimum of the six live entrants' three duct columns"* | Re-derived in §2: the minima were **`0.0291 / 0.0311 / 0.0250`**, Yang's. `0.0387 / 0.0341 / 0.0325` were Reissmann's, 2nd/2nd/2nd of seven. | not met, and correctly so |

The disjunction was satisfied on its first clause, so **C1 fell**. What survived unstruck was then read
and re-derived rather than assumed, because a strike-and-keep repair can leave a false remainder:
*"All three round-5 duct scores landed within 0.0004 of Wu & Zhang's published entry, the one carrying
the same untrained QCR term — 0.0455, 0.0399, 0.0350 against our 0.0455, 0.0400, 0.0353, so 0.00003,
0.00008 and 0.00034 apart … We were behind the leader on all three."* Every clause of that checked out
against §2: Wu & Zhang's live duct column was `0.0455 / 0.0399 / 0.0350`; the three separations
computed to `0.000030`, `0.000082`, `0.000339`; Yang led all three and our three values were larger
than his; and the stated gaps to Yang, `0.0164 / 0.0089 / 0.0103`, reproduced to the digit. The tense
was moved to the past under W-5, so the sentence no longer asserted a present state.

### C2 — `benchmarks.html`, the wall table

| clause as written | executed | met |
|---|---|---|
| *"column 2 as `0.0432 / 0.0998 / 0.0569 / 0.0748`"* | The four rows landed at `:131-134`, column 2 reading `<s>0.0592</s> 0.0432`, `<s>0.1195</s> 0.0998`, `0.0569`, `<s>0.0760</s> 0.0748` — each live value equal to the minimum re-derived in §2, each superseded value struck beside it. | **MET** |
| *"the two `alpha_15` rows without a `t-gold` `#1`"* | Both rows carried `<span class="tag t-open"><s>#1</s> → <b>2nd of 7 — WE LOSE</b></span>` naming the holder. `t-gold` occurred **once** in the whole file, at `:42`, and that occurrence was the CSS rule declaration; the pattern `t-gold[^>]*>\s*#1` returned **zero**. | **MET** |
| *"and without a `win`-class negative margin"* | Both margin cells carried `class="n lose"` with `<s>−15.4%</s>` struck beside `+16.0%` and `+1.3%`. Both restated signs reproduced from §2's values against the live minima. | **MET** |
| *"and the lede no longer claiming four leads"* | `Cases where we lead the entire public leaderboard` occurred once, at `:112`, inside `<s>…</s>`, replaced live by *"The four hill cases, re-derived against the live board: we lead two, and neither lead is our model's."* | **MET** |
| *"or show `benchmarks.html:118-121` struck"* | not needed | — |

**C2 fell**, on all four clauses of the re-derivation branch. Both surviving leads were tagged
`BASELINE, NOT OUR MODEL`, which agreed with §2's *"earned by our model 0 of 8"* and with the same
page's hero KPI.

**Both blockers fell, so the grade's own stated condition for `PASS` was satisfied.** That condition
was treated here as necessary and not sufficient: the sweep in section 4 was run in full regardless,
because the two blockers were themselves surfaces no earlier V10 sweep had covered.

---

## 4. The independent whole-file sweep, and its four controls

The repairing agent's sweep was not accepted. A separate instrument was written and run over
**nineteen files** — the five enumerated surfaces expanded to every tracked member, including
`wall/wall.html` and all eight prediction CSVs. It blanked `<s>…</s>`, `<del>…</del>` and `~~…~~`
regions in place with newline offsets preserved so line numbers survived, then searched the remainder
for the eight four-entry-board literals `0.0592 0.1195 0.0760 0.0387 0.0341 0.0325 0.0364 0.0350` and
for fourteen ordinal, count, phrase and markup patterns including `rank N of 5`, `Nth of 5`,
`4 of 8`, `5 of 8`, `OUR MODEL LEADS`, `best score on the entire leaderboard`,
`lead the entire public leaderboard`, `beats all four published entries` and `t-gold…>#1`.

**Every multi-word pattern was compiled with `\s+` between words and never with a literal space.**
That was not a precaution — it was the defect that made the repairing agent's own first instrument
return 7 on the file whose wrapped heading was the blocker.

**Control 1 — positive, confirmed by readback before any zero was believed.** A control line was
appended to a scratch copy of `wall/wall.json` and **deliberately split across a newline between
`entire` and `public`**, so a literal-space pattern would miss it exactly as the earlier instrument had.
Presence was confirmed by readback (`grep -c` returned **1** on the planted copy and **0** on the
untouched baseline) *before* the sweep was run. Baseline **2** hits → planted **8** hits: a gain of
exactly **six**, one per planted token, and the wrapped phrase fired as `'lead the entire\npublic
leaderboard'`. **The control fired, so the zeros below are measurements.**

**Control 2 — negative, struck.** The identical string wrapped in `<s>…</s>` in a second scratch copy
returned **2** hits — the untouched baseline, a gain of **zero**. The stripper suppressed the plant and
nothing else.

**Control 3 — over-blanking.** Each file was swept twice, with stripping off and on, and the difference
reconciled: `closure.html` 25 raw → 4 live, `benchmarks.html` 8 → 2, `ACTIVE_RESEARCH.md` 34 → 17,
`PRODUCT_LIST.md` 15 → 13, `build_benchmarks.py` 4 → 3, and 0 suppressed on every other file — **136
raw hits to 89 live, 47 suppressed.** Each of the 47 was then located and its containing span
identified: **all 47 sat inside a genuine strike span, 0 unexplained.**

**And that reconciliation caught a defect in itself before it was believed, which is the only reason
it is reported as evidence.** Its first run flagged **20** of the 47 as falling outside any strike
span — on `ACTIVE_RESEARCH.md`, `docs/PRODUCT_LIST.md` and `build_benchmarks.py`. The flags were
real but the instrument was wrong: the depth probe knew `<s>` and `<del>` and **did not know markdown
`~~`**, which is the strike form those three files use (`ACTIVE_RESEARCH.md:12`,
*"~~rank 1 of 5 scored locally at benchmark commit `deb91557`~~"*; `build_benchmarks.py:85`,
*"~~rank 1 of 5~~ RANK 1 OF 7"*). Re-run against both mechanisms, all 20 resolved to real `~~…~~`
spans and the unexplained count went to **0**. A reconciliation that had been trusted on its first
pass would have reported twenty phantom over-blankings; one that had been skipped would have
asserted the same zero without earning it.

**Control 4 — live positive against the pre-repair tree.** The same instrument was run unchanged
against `git show 1a08e75d:` for both repaired files. It returned **6** live hits on `closure.html`,
including `0.0387`, `0.0341` and `0.0325` all at `:560`, and **10** on `benchmarks.html`, including the
wrapped lede at `:109` and four `t-gold">#1` badges at `:118-121`. **The instrument was demonstrated to
see both graded blockers, at their graded lines, before it was believed on the tree where it saw
nothing.**

**Strike balance, audited independently.** `closure.html` **27 open / 27 close**, `benchmarks.html`
**16 / 16**, depth never below 0 or above 1 in either, final depth 0 in both. The repairing agent's
figures reproduced exactly. `ACTIVE_RESEARCH.md`, `PRODUCT_LIST.md`, both JSON members, `wall.html` and
the generator carried no `<s>` tags at all.

### 4.1 Result, surface by surface — every live hit adjudicated by opening it

| surface | live hits | adjudication |
|---|---|---|
| `closure.html` | **4** | `:353` our own round-4 `0.0325`, inside a dated correction with the four-entry ordinals struck beside it; `:373` and `:560` Wu & Zhang's live `0.0350` on `AR_14_Ret_180`, correct against §2; `:494` `OUR MODEL LEADS` quoted inside the very correction that struck those badges. **Clean.** |
| `ACTIVE_RESEARCH.md` | **17** | Corrections quoting the figure they strike (`:576`, `:622`, `:769`, `:774-775`); our own round-4 `0.0325` (`:616`, `:661`, `:666`); one correct live value (`:721`, *"Best score on the entire leaderboard: 2 of the 8 cases"*, which agreed with §2); and three round-4/round-3 kept-history ordinals (`:73`, `:652`, `:668`) already on the docket as **D238** and outside the class per §1. **Clean in class.** |
| `benchmarks.html` | **2** | Both at `:85`, *"four of eight cases won"* in the t-test paragraph. Re-derived rather than read: that is a **head-to-head** count against us, and Yang beat us on exactly **4 of 8** (§2). Correct as written. **Clean.** |
| `wall/wall.json` | **2** | The same head-to-head sentence at `:56`. Correct. **Clean.** |
| `benchmarks.json` | **2** | The same sentence at `:56`. Correct. **Clean.** |
| `build_benchmarks.py` | **3** | `:89` `rank 1 of 5` **quoted inside the comment that corrects it** (*"`rank 1 of 5` was true of the FOUR-entry board"*), with the literal itself struck at `:85`; `:147` the generator string for the head-to-head sentence. **Clean.** |
| `wall/wall.html` | **0** | **Clean.** |
| `PRODUCT_LIST.md` | **13** | Twelve carried their correction in the same sentence or were re-derived correct — `:73`'s *"4 of 8 cases won"* for Yang **and** Reissmann cleared by arithmetic in §2, both exactly 4 of 8 head-to-head. The thirteenth is `:1811`, ruled in section 5. |
| package `DESCRIPTION_DOCUMENT.md` | **3** | All three our own round-4 `0.0325` (`:141`, `:165`, `:184`). **Clean.** |
| package `MANIFEST.json`, `README.md` | **0** | **Clean.** |
| package `test/*.csv`, 8 files | **43** | Every hit a substring of a prediction float in a headerless three-column numeric file (`0.0592658`, `0.0350395`, `-0.0350626`). Data, not claims. **Clean.** |

---

## 5. The one in-scope surface item, ruled explicitly: `PRODUCT_LIST.md:1811`

`docs/PRODUCT_LIST.md` is an enumerated V10 surface, and `:1811` was read at the blob:

> **Strongest verified asset, and it does not depend on our score at all:** on exactly the two cases the
> train-only gate DECLINED, the supplied baseline beats all four published entries (0.046108 vs 0.0569;
> 0.071863 vs 0.0760).

**Ruling: OUTSIDE V10's claim class. Filed as D246, not appended to the rung.** The ground is stated in
full because the reasoning, not the conclusion, is what a later grader has to check.

1. **Its round-5 numbers were correct and current.** `0.046108` and `0.071863` were our round-5 per-case
   values on `alpha_05_4071_4048` and `alpha_05_4071_2024`, re-derived in §2 and unchanged by the board
   move. V10's class is *round-5 numbers and the caveats travelling with them*; the round-5 numbers on
   this line were not stale in any respect.
2. **Its substance survived the board move, measured.** `0.046108 < 0.0569` and `0.071863 < 0.0748` —
   the declined baseline beat **all six** live entrants on both cases, both rows placing 1 of 7 in §2.
   `0.0569` was moreover **still the live minimum**, Wu & Zhang's. The single superseded figure was
   `0.0760`, against a live `0.0748`.
3. **It sat under an explicit date heading**, `### 2026-08-10 (night) — the cold reviewer reproduces the
   score exactly`, a dated log of what a cold pass found on the night **before** the board moved at
   `2026-08-11T23:33Z`, in a file whose structure is a dated chronological journal.
4. **It contradicted no correction standing on its own page.** This was the decisive test, because a page
   stating the correction in one place and the superseded figure in another was the exact pattern that
   killed both C1 and C2. Executed: **`0.0748` occurred nowhere in `docs/PRODUCT_LIST.md`** — zero
   occurrences in the whole file. The fatal pattern was absent.
5. **The page's own binding rule did not reach it.** `:98` bound *"no surface, internal or outward, may
   print 'rank 1' without … naming the board it is a rank on by entrant count and retrieval date."* That
   rule governs **rank claims**. `:1811` printed no rank; it printed a comparison. Contrast
   `ACTIVE_RESEARCH.md:700-710`, whose frame warning binds *"every ordinal on this page"* — a broader
   rule, and the one D238's three sites sit under.

**What remained wrong with the line, stated plainly**: it named its board by entrant count and **not by
retrieval date**, and its `0.0760` was a four-entry minimum against a live `0.0748`. That is **D238's
class in a second file** — an incomplete board identifier on a kept dated figure — and D238 is the row
on which one chief ruling was being costed. This grader did not pre-empt that ruling and did not repair
the line.

**The consequence is recorded so that reopening is a lookup and not a search:** if the D238 ruling holds
that an incomplete board identifier on a kept dated figure **is** an inconsistency in V10's sense, then
V10 must be reopened, and it reopens on exactly one line, `docs/PRODUCT_LIST.md:1811`, and on no other
site found by this pass. The `PASS` below is conditional on the class boundary drawn in §1 and §5, and
that conditionality is the honest statement of it.

---

## 6. Verdict

**`PASS`.** Both blockers of `1a08e75d` fell against the landed blobs at `fe54ec0a`, each clause of the
grade's own falsifier executed and reported above. A whole-file sweep of all nineteen tracked members of
the five enumerated surfaces, run with a readback-confirmed positive control that fired 6/6 on a
deliberately wrapped plant, a struck negative control that gained 0, a reconciled over-blanking control,
and a live positive control that saw both graded blockers at their graded lines in the pre-repair tree,
returned **no live in-scope inconsistency on any surface**. Every live hit was opened and adjudicated;
none was cleared by pattern alone. V10's criterion carries no tolerance and none was applied — the one
surface item that could have carried it, `PRODUCT_LIST.md:1811`, was ruled outside the claim class on
five stated grounds in §5, filed as **D246**, and the condition under which it reopens the rung was
written down rather than left implicit.

**Falsifier for this closure.** Show any of the four clauses of C2 or the one satisfied clause of C1
unmet at `fe54ec0a` and the rung reopens. Show a live, unstruck, present-tense four-entry-board
comparison on any of the nineteen files swept, at any line this pass did not adjudicate, and the rung
reopens. Show that `0.0432 / 0.0998 / 0.0569 / 0.0748` are not the live minima of the four hill columns,
or that Yang did not lead all three ducts, and section 2 falls and everything resting on it with it.
Show that `docs/PRODUCT_LIST.md` states `0.0748` anywhere, and §5's decisive test fails and `:1811`
becomes a same-page contradiction and a blocker.

**Compliance.** No solver runs, no scoring calls; the ledger stood at 6 and was not touched. Nothing
sent, uploaded, emailed or registered. `deb91557` was not moved. `dist/`,
`demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not opened or written. No
file this pass graded was edited by it, and no file a peer was declared live on was touched. Nothing on
any of the five surfaces was repaired by this grader — the repair at `fe54ec0a` was another agent's, and
grading it was the whole of this pass's work.
