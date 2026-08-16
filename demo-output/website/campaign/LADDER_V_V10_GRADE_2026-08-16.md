# Ladder V — V10 re-graded at HEAD `d91b101a`, 2026-08-16, by a non-author

*(HEAD advanced to `01e94313` while this grade was being written. `git diff --name-only
d91b101a 01e94313` over all five enumerated surfaces returned **zero files**, and both blockers below
were re-measured live at `01e94313` before commit. Every figure and line number in this document
holds at both trees.)*

**Verdict: `FAIL`.** Two of V10's five enumerated surfaces carried live, unstruck, present-tense
four-entry-board comparisons at `d91b101a`, and each contradicted a correction standing on its own
page. The rung's own criterion — *"one inconsistent surface fails the rung"* — decided it.

**Why this grade was dispatched.** The standing V10 verdict was `FAIL` on four blockers, recorded in
`campaign/LADDER_V_V6_V10_REGRADE_2026-08-15.md` at `60073572` (2026-08-15T19:34:11Z). The repair of
all four landed at `cca64eaf` (2026-08-15T19:53:29Z) — **nineteen minutes after the grade** — so the
verdict of record had been formed against a tree that no longer existed. `cca64eaf` closed with the
line *"V10 is NOT marked green here: the repairing agent may not grade its own repair."*

**Independence.** The grader below wrote none of `cca64eaf`, `60073572`, `377d6afb`, `bd8280de` or
`7a0419f7`, and none of the text on any of the five surfaces. Independence rested on the untracked
dispatch record and not on git authorship, which carries one Ubuntu identity for the whole lab (D130).

---

## 1. What V10 declared, quoted from its own face

`LADDER_V_TRIPLE_VERIFICATION.md:359-362`:

> **V10. Cross-surface number sweep**: closure.html, the Active Research board, the wall,
> PRODUCT_LIST, and the submission package must all carry round-5 numbers with the same caveats —
> one inconsistent surface fails the rung (the board was still showing round 3 at last report; that
> class of drift is what this rung exists to catch).

Read against R-CONVERGE, that is a declared scope and a declared pass criterion, and it is unusually
tight for this ladder:

* **The artifacts are enumerated, five of them, by name.** `demo-output/website/closure.html`;
  `demo-output/website/ACTIVE_RESEARCH.md`; the wall (`wall/wall.json`, `benchmarks.json`,
  `benchmarks.html`, and the generator `sdk/scripts/build_benchmarks.py`, the four members the
  2026-08-15 regrade §3.8 graded under that word); `docs/PRODUCT_LIST.md`; and
  `demo-output/website/closure_challenge_submission_round5/`.
* **The claim class is round-5 numbers and the caveats travelling with them.** Round-4 and round-3
  figures held as dated history are not round-5 numbers and are therefore outside the scope; that
  reading is what filed the two rows in §5 rather than appending them here.
* **The criterion is disjunctive and has no tolerance**: one inconsistent surface fails. It carries
  no count, no severity floor and no exemption for a surface whose error sits beside its own
  correction.

Nothing about the scope was undeclared, so there is no finding of the "scope not declared" kind.

---

## 2. The board, re-derived here rather than read

`LIVE_BOARD` was lifted out of `sdk/scripts/probability_of_rank.py` by `ast.literal_eval` on the
module's assignment node — parsed, never imported — and joined to `CASES` from the same parse. Our
per-case values came from `demo-output/website/closure_challenge_round5_qcr.json`
(`official_test_harness_result.round5_per_case_full`), the declined-baseline test from
`rans_identity_floor_per_case` in the same object.

Board `fetched` = `2026-08-11T23:33Z`, six entrants, seven rows counting ours.

| case | ours | live best-other | held by | rank of 7 | we lead | declined baseline |
|---|---|---|---|---|---|---|
| `alpha_15_13929_4048` | 0.050105 | **0.0432** | Tian, Buchanan, Hickel & Dwight | 2 | no | no |
| `alpha_15_13929_2024` | 0.101112 | **0.0998** | Tian, Buchanan, Hickel & Dwight | 2 | no | no |
| `alpha_05_4071_4048` | 0.046108 | 0.0569 | Wu & Zhang | 1 | yes | **yes** |
| `alpha_05_4071_2024` | 0.071863 | **0.0748** | Yang | 1 | yes | **yes** |
| `AR_1_Ret_360` | 0.045470 | **0.0291** | Yang | 3 | no | no |
| `AR_3_Ret_360` | 0.039982 | **0.0311** | Yang | 4 | no | no |
| `AR_14_Ret_180` | 0.035339 | **0.0250** | Yang | 4 | no | no |
| `NASA_2DWMH` | 0.063198 | **0.0294** | Tian, Buchanan, Hickel & Dwight | 7 | no | no |

Best-on-board **2 of 8**, earned by our own model **0 of 8**, overall mean 0.056647191704213645 =
**rank 1 of 7**, margin to Yang's mean-of-eight 0.0580125 = **0.001365**. Each entrant's eight
per-case values meant to its published overall to 4 dp, which is the one input-side check available
without a fetch. Every figure agreed with the live-board ground truth carried in the dispatch and
with `campaign/BOARD_MOVED_2026-08-11.md`.

---

## 3. The instrument, and its controls

The four blockers of `60073572` were each checked at their named lines, and then — because a sweep
over hand-listed regions is the B1 class this ladder ranks first — a mechanical whole-file sweep was
run over every surface. It blanked `<s>…</s>`, `<del>…</del>` and `~~…~~` spans in place (preserving
newline offsets, so line numbers survived) and then searched what remained for the four-entry-board
literals `0.0592 0.1195 0.0760 0.0387 0.0341 0.0325 0.0364 0.0350` and for the ordinal forms
`rank 1 of 5`, `N(st|nd|rd|th) of 5`, `rank 3 of 5`, `4 of 8`, `5 of 8`, `OUR MODEL LEADS`,
`best score on the entire leaderboard`.

**The controls, run before the results were believed:**

* **Positive control.** A line reading `best-on-board 4 of 8, OUR MODEL LEADS, best published 0.0592,
  rank 1 of 5` was planted into a scratch copy of `wall/wall.json`. **Four hits, all at the planted
  line.** The first attempt at this control silently failed to plant (its anchor string was absent
  from the file) and the sweep returned 0 — the instrument was re-run only after the plant was
  confirmed present by readback. That near-miss is the whole reason the control existed.
* **Negative control.** The identical string wrapped in `~~…~~` in a second scratch copy. **Zero
  hits** — the strike-stripper suppressed what it was supposed to suppress and nothing else.

`<s>` nesting was audited separately, because an unbalanced strike tag would make struck and live
text indistinguishable to any reader of the markup: `closure.html` 25 open / 25 close,
`benchmarks.html` 4 / 4, depth never below 0 or above 1 in either, final depth 0 in both. HTML `<s>`
is strike-and-keep in the same way `\sout{}` is, so this balance audit — plus the per-hit depth
probe in §4.2 — is what stands in for a visual render; no headless browser was installed on this
machine (`chromium`, `google-chrome`, `wkhtmltoimage`, `playwright` all absent).

---

## 4. Result surface by surface

### 4.0 The four standing blockers — all four fell

Checked against the falsifier `60073572` §3.9 wrote for itself.

| blocker | falsifier as written | measured at `d91b101a` | fell |
|---|---|---|---|
| **B1** `closure.html:483-493` | column 2 no longer reproduces as the four-entry row; rows 1–2 no longer wins | all eight second-column cells carried the four-entry number struck beside the live one (`0.0432 0.0998 0.0569 0.0748 0.0291 0.0311 0.0250 0.0294`, each equal to the minimum re-derived in §2); duct tags `3rd/4th/4th of 7`; NASA `LAST — 7th of 7`; both `OUR MODEL LEADS` badges struck and replaced with `2nd of 7 — WE LOSE`, `t-gold` gone from both rows, both numerals reclassed `lose` | **yes** |
| **B2** `closure.html:480-482` | show `Uncorrected` not `Best published` to be the stale column, and seven to be six | the disclaimer was struck with all three defects named on its face, including the column error and the count | **yes** |
| **B3** `ACTIVE_RESEARCH.md:12/:18/:562` | show any struck, or naming the six-entry board by count and retrieval date | all three struck at `:12`, `:25`, `:572`, each replaced by `rank 1 of 7` naming six entries, `2026-08-11T23:33Z`, re-verified `2026-08-14T21:01Z`, each stating that a commit anchor is not an admissible board identifier | **yes** |
| **B4** `ACTIVE_RESEARCH.md:726-728` | show `0.0364` to be the live `NASA_2DWMH` minimum | the six-count was struck at `:764-777` and corrected to seven; `0.0364` was re-derived here as Wu & Zhang's four-entry minimum against a live 0.0294 (Tian, Buchanan, Hickel & Dwight) | **yes** |

`cca64eaf` did what it said it did. The rung did not pass, because the two blockers below were never
in anyone's V10 sweep.

### 4.1 BLOCKER V10-C1 — `closure.html:558-561`, §6, live and present-tense

Live at `d91b101a`, at strike depth 0, in the section headed *"6 · What is not solved"* — a
current-state section, not kept history:

> **And the ducts are better, not solved.** All three duct scores now sit within 0.0004 of the
> published entry that carries the same QCR term — and behind **the leader** on every one of them
> (**0.0387, 0.0341, 0.0325** against our 0.0455, 0.0400, 0.0353). The untrained term sets a strong
> floor; it does not close **the gap to Reissmann**.

* `0.0387, 0.0341, 0.0325` were re-derived here as **Reissmann, Fang & Sandberg's** three duct values.
  On the six-entry board the duct leader was **Yang**, at **0.0291, 0.0311, 0.0250**. The paragraph
  labelled a second-place row "the leader" and printed its numbers as the leader's.
* Reissmann's live per-duct standings, computed in §2's frame: 2nd, 2nd, 2nd of seven. Not the leader
  on any of the three.
* **The same page contradicted it fifty lines above.** `:505`, `:506`, `:507`, written by `cca64eaf`,
  each read *"the live best 0.0291 is Yang's"* / *"0.0311 is Yang's"* / *"0.0250 is Yang's"*. This is
  V10-B1's own fatal pattern — a page stating the correction in one place and the superseded figure
  in another — surviving on the same page that had just been repaired for it.
* The claim is **undated and present-tense** (*"now sit"*, *"does not close"*), so under the chief
  ruling at `04489465` it grades against the live board, where it is wrong.
* `git blame` dated the paragraph to `099b2827` (2026-08-07T21:00:07Z) — written before the board
  moved, and live and unstruck for the five days after it did.

The one arithmetic claim in the sentence that is right is the first: our ducts sat within 0.0004 of
**Wu & Zhang's** `0.0455 / 0.0399 / 0.0350` — 0.00003, 0.00008, 0.00034. The QCR-term entrant and
"the leader" are two different entrants, and the sentence merged them.

### 4.2 BLOCKER V10-C2 — `benchmarks.html:109-121`, the wall, four gold `#1` badges

Live at `d91b101a`. `git blame` dated the table to `62cf2a88` / `cb0694d1` (2026-07-29) and its lede
to `49f71b8c` (2026-08-08). The strike-depth probe returned **0 for all four `t-gold">#1` badges** —
none of it is struck.

> *"**Cases where we lead the entire public leaderboard.**"* — over four rows.

| row | `Best published` printed | margin printed | live best-other | holder | our value | live margin | live truth |
|---|---|---|---|---|---|---|---|
| `alpha_15_13929_4048` | 0.0592 | **−15.4%** `win` `#1` | **0.0432** | Tian, Buchanan, Hickel & Dwight | 0.050105 | **+16.0%** | **we lose** |
| `alpha_15_13929_2024` | 0.1195 | **−15.4%** `win` `#1` | **0.0998** | Tian, Buchanan, Hickel & Dwight | 0.101112 | **+1.3%** | **we lose** |
| `alpha_05_4071_4048` | 0.0569 | −19.0% `win` `#1` | 0.0569 | Wu & Zhang | 0.046108 | −19.0% | correct |
| `alpha_05_4071_2024` | 0.0760 | −5.4% `win` `#1` | **0.0748** | Yang | 0.071863 | **−3.9%** | lead holds, number stale |

Three of the four `Best published` values are four-entry-board minima; **two rows carry a gold `#1`
badge and a green negative margin on cases lost to Tian, Buchanan, Hickel & Dwight**; and the
sign of the margin flips on both. The heading claims four leads where §2 measured two, and neither
of the two survivors is our model's.

**Eleven lines above it, the same page's hero KPI reads `0 of 8`**, with `<s>4 of 8 cases best on the
board</s>` struck and the six-entry correction spelled out at `:92-98`. `benchmarks.html` therefore
contradicted itself on the same screen, which is precisely the condition `60073572` called fatal on
`closure.html` — *"the page states the correction in prose and the error in the badge, and the badge
is the half a reader sees first."*

`benchmarks.html` is hand-maintained: `sdk/scripts/build_benchmarks.py` writes only
`benchmarks.json` (`:357`, its single `write_text`), and the strings `Best published`, `0.0592` and
`t-gold">#1` appear nowhere in the generator. There is no regeneration route to this repair.

**How it survived.** `60073572` §3.8 certified the wall `✔` after checking `wall/wall.json:56`,
`benchmarks.json:56`, `benchmarks.html:92-94` and `build_benchmarks.py:126,138` — a sweep over four
hand-picked line ranges. The defect sat at `:109-121`, fifteen lines below the last range checked.
A sweep that searched four line ranges and reported a clean surface is the B1 class this ladder
ranks first, and it produced a `✔` on the surface that carries the lab's hero numbers.

### 4.3 The three surfaces that passed, by execution

* **`ACTIVE_RESEARCH.md`** — B3 and B4 both repaired (§4.0). The mechanical sweep returned 17 raw
  hits; every one resolved on inspection to either a correction quoting the figure it strikes
  (`:576`, `:622`, `:769-777`), our own round-4 `AR_14_Ret_180` score `0.0325` (`:616`, `:661`,
  `:666`), a correct live value (`:721`, *"Best score on the entire leaderboard: 2 of the 8 cases"*),
  or a round-4 kept-history ordinal (`:73`, `:652`, `:668`) — filed in §5, not counted here.
* **`docs/PRODUCT_LIST.md`** — seven raw hits, all `4 of 8` or `0.0760` carrying their correction in
  the same sentence, plus `:73`, which required arithmetic to clear rather than reading: *"Yang (…,
  4 of 8 cases won), Reissmann (…, 4 of 8 won)"* is not a board-wide win count (Yang wins 3 of 8
  against seven rows, Reissmann 0) but a **head-to-head count against us**, and re-derived that way
  both are exactly **4 of 8**. Correct as written.
* **The submission package** — `DESCRIPTION_DOCUMENT.md` returned three hits, all of them our own
  round-4 `0.0325` (`:141`, `:165`, `:184`); `MANIFEST.json` and `README.md` returned zero.
* **`wall/wall.json`** and **`benchmarks.json`** returned zero. The wall failed on its HTML member
  alone.

---

## 5. Filed under R-CONVERGE, not appended to the rung

Both rows were written to `docs/DOCKET.md` in the working tree and **deliberately left uncommitted**:
at the time of this pass that file also carried another agent's uncommitted D236, D237 and an
in-progress D230 edit, and a pathspec commit takes paths from the working tree, so committing it
would have swallowed three of another agent's rows — the capture declared at `78300277`. The two rows
are owed a commit by the docket's owner.

* **D238** — `ACTIVE_RESEARCH.md:73`, `:652`, `:668`: round-4 ordinals (`rank 3 of 5`,
  `Best-on-board 5 of 8`) held as dated history, naming no board by entrant count and retrieval date,
  under a frame warning at `:700-710` that binds *"every ordinal on this page"*. Round-4 figures are
  outside V10's round-5 claim class. `60073572` §3.6 recorded the class as a residual and asked for
  one ruling rather than three; no docket row had carried it.
* **D239** — the sweep-shape finding: every V10 sweep on record enumerated line ranges by hand, and
  the two blockers in §4.1 and §4.2 are what that shape cannot see. This is a finding about the
  ladder's method, not about a V10 surface.

---

## 6. Verdict

**`FAIL`**, on `demo-output/website/closure.html:558-561` (blocker V10-C1) and
`demo-output/website/benchmarks.html:109-121` (blocker V10-C2). Two of five enumerated surfaces
carried live four-entry-board comparisons at `d91b101a`, and each contradicted a correction standing
on its own page. The four blockers of `60073572` were all genuinely repaired by `cca64eaf`; the rung
failed on surfaces no V10 sweep had ever covered.

**Falsifier for this grade.** Show `closure.html:558-561` struck, or show `0.0387 / 0.0341 / 0.0325`
to be the minimum of the six live entrants' three duct columns, and C1 falls. Show
`benchmarks.html:118-121` struck or re-derived — column 2 as `0.0432 / 0.0998 / 0.0569 / 0.0748`,
the two `alpha_15` rows without a `t-gold` `#1` and without a `win`-class negative margin, and the
lede no longer claiming four leads — and C2 falls. **Both fall ⇒ V10 is PASS.**

**Compliance.** No solver runs, no scoring calls; the ledger stood at 6 and was not touched. Nothing
sent, uploaded, emailed or registered. `deb91557` was not moved. `dist/`,
`demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not opened or written.
No file another agent was declared live on was edited.
