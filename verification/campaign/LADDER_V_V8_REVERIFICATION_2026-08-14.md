# Ladder V — rung V8 re-verification, 2026-08-14

**Verdict: V8 FAILS — one blocking finding (G1), one changed-shape finding (F4′),
three residuals. The 2026-08-11 round's five findings are otherwise cleared.**

Owner: an agent that wrote none of the graded text and none of the repairs under
test. Grading is against primary artifacts and executed instruments only. Where a
repair's own commit message is cited it is cited as a **claim under test**, never as
evidence. This document **does not replace**
`LADDER_V_V8_REVERIFICATION_2026-08-11.md`; that round stands as written and is the
subject of this one.

---

## 0. FRAME, stated before any count

| item | value |
|---|---|
| clock at start of this pass | **2026-08-14 23:42:33 UTC** (`date -u`, run before anything else) |
| repository HEAD when graded | `839f6355` (2026-08-14 23:40:10 +0000) |
| working tree | clean except `sdk/.filming-keepalive` (M) and untracked `.autostop-hold` — neither in the graded set |
| subject commits under test | `cc906ec9` (F1's second repair, 22:39:07Z) and `63453645` (the machine record's dated supersession, 23:10:12Z), both ancestors of HEAD |
| graded surfaces | `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` **§5 banner + §5.1–§5.4** (lines 591–1031), `demo-output/website/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` (526 lines), `.../README.md` (93 lines) |
| state of graded files | draft at `b14356b0` (23:24:43Z), description document at `cc906ec9` (22:39:07Z), package README at `9477a2ed` (2026-08-10 21:35Z — **untouched since the last round**) |
| tooling | `/bin/grep` throughout, never the shell's `grep`, which is `ugrep --ignore-files` and honours `.gitignore`; `__pycache__` purged before every Python cell |
| board referents | SCORING pin `deb91557` (four entrants) at `/home/ubuntu/closure-challenge-benchmark` — **not moved**; RANKING record `campaign/BOARD_MOVED_2026-08-11.md` (six entrants), re-verified unchanged by the 2026-08-14T21:01Z fetch recorded in `campaign/BOARD_RESCORE_2026-08-14.md` §1.2 |

**What this frame structurally cannot contain.** Three files. It does not reach
`closure.html`, `benchmarks.*`, `wall/`, `dist/`, `docs/PRODUCT_LIST.md`,
`latex/*.tex`, or §1–§4 and §6–§10 of the submission draft. Those are V10's and
V14's rungs. Findings there are FILED, not appended here.

### R-CONVERGE — scope declared BEFORE grading

1. **Artifacts:** the three files above, at HEAD `839f6355`.
2. **Claims:** (a) the five findings F1–F5 of 2026-08-11, each re-executed;
   (b) the four §6 observations of that round; (c) every quantitative or placement
   sentence **newly landed in those three files since `174e52bd`** — 12 commits,
   +395/−111 lines.
3. **Pass criterion:** V8 as written in `LADDER_V_TRIPLE_VERIFICATION.md` — every
   quantitative sentence maps to a named artifact, the banned-claims list holds,
   and (2026-08-10 strengthening + amendment, 2026-08-12 recomputation note) every
   rank claim carries P(rank 1), its interval, **its board**, and the not-decided
   pairs. Plus termination clause 2: the previous fix round's own output introduces
   **no new failures**.
4. **Anything else → docket.** Filed as D85, D86, D87.

### FINDING ON THE CONDITION ITSELF (brief item 1)

**V8's closing condition does not name its own surfaces, and this round inherited a
frame rather than deriving one.** The rule says *"the cover email + description
document"*. It does not say which sections of a 1596-line policy document are the
cover email, and it does not mention the package `README.md` at all — which the
2026-08-11 round nevertheless graded (R1–R9). That round's frame is reasonable and
is adopted here **unchanged, for comparability**, but it is a *choice*, not a
derivation, and two graders could have drawn it differently. Recorded as a finding
rather than smoothed over: a rung whose subject is claim-language precision should
not leave its own extent to the grader.

---

## 1. THE VERDICT

**V8 FAILS.** The rewritten and re-repaired text is materially better than what the
last round graded: the board move of 2026-08-11T23:33Z has been carried into the
best-on-board count, the P(rank 1) figure, its interval, the undecided-pair list and
the Standing row, in both graded documents, with strike-and-keep throughout. Four of
the five findings of 2026-08-11 are **CLEARED** on executed evidence. It fails on
one arithmetic claim that **inverts** under the live board and is live in the cover
email, and on a certification sentence that a later commit falsified.

| # | finding | where | severity |
|---|---|---|---|
| **G1** | **The seed bound "covers 84% of the margin" survives in the draft against a margin that no longer exists — and against the live one the same bound is 177%, which reverses the sentence's meaning.** Re-derived here: bound 0.002419121853891026 (`closure_challenge_seed_sensitivity.json` → `spreads.overall_equivalent_S_bound`) ÷ live margin 0.0013658082957863568 = **1.7712**; ÷ the four-entry Reissmann margin 0.0028863365997926355 = 0.8381. **The travelling description document withdrew this conclusion at `cc906ec9`** (§8: *"It does not cover 84% of the margin"*, 177%); the draft did not. Three live sites, two of them binding | draft **§5.4 cover email** `:1007`; **§5.3 item 9** `:903–906`; §5.2 `:728–729` | **BLOCKING** |
| **F4′** | **CHANGED SHAPE.** The 2026-08-11 repair of F4 replaced *"kept verbatim"* with a precise certification: *"**Its thirty body lines are byte-identical** — **every row of the ten-row defect table** … — but its heading was replaced … and the blank line that closed the blockquote became `>`."* Executed byte-diff of the kept banner against `git show e87650db^` returns **three** differing lines of 32, not two: the heading, the closing blank, **and row 22 — a row of the ten-row defect table**, edited at `2cec44ee` (2026-08-12). So 29 body lines are byte-identical, not thirty, and the clause certifying the table is false | draft `:598–599` vs `:649` | **HIGH** |
| **G2** | The cover email asserts a margin live and strikes the same figure seven lines below it. `:998–999` reads *"the lowest overall on your published board, **by 0.0029 over Reissmann, Fang and Sandberg**"*, unstruck; `:1005–1006` strikes *"~~68%, 2–100%, by 0.0029 over Reissmann~~"* and says *"The margin above is **0.0014 over Yang**"* — but the margin above was never struck, so the paragraph states both | draft `:998–1006` | MEDIUM |
| **G3** | The travelling document's §5 opens its standing subsection with *"On the published board at `deb91557` our 0.056647 is the best overall number, by **0.0028863** over Reissmann, Fang & Sandberg"* — a commit anchor, but **not** the entrant-count-and-retrieval-date idiom the same document adopted 320 lines earlier for exactly this failure mode. It also sits **above** the recomputation box whose own rule reads *"anything **below** not struck is live against the six-entry board"*, so the box's scope rule does not reach it | `DESCRIPTION_DOCUMENT.md:373–374` | LOW (residual) |

**Why G1 blocks rather than annotates.** It is not a stale figure; it is a figure
whose *direction of argument reverses*. "A bound covering 84% of a margin qualifies a
lead; a bound at 177% of a margin means there is no lead left to qualify" — that is
the travelling document's own sentence, written at `cc906ec9`, about this exact
arithmetic. The draft's §5.3 item 9 does not merely repeat the superseded figure: it
declares *"The **operative** comparison is the 0.0028863 margin over Reissmann, Fang
& Sandberg"* and then binds the whole package — ***"No document in this package may
quote the margin without this qualifier"***. A live mandatory instruction now
requires every document in the package to state a figure the travelling document has
formally withdrawn. And §5.4 carries it into the cover email, where it flatters us.

---

## 2. THE FIVE FINDINGS OF 2026-08-11, RE-EXECUTED

| # | 2026-08-11 finding | status today | executed evidence |
|---|---|---|---|
| **F1** | Wu & Zhang given the wrong ordinal in the travelling document | **CLEARED — with a named durability residual (§3)** | Text at `DESCRIPTION_DOCUMENT.md:54–56` now states the ordinal **with the board's entrant count and two retrieval timestamps on the face of the sentence**, and strikes the superseded ordinal in place. Ordinal agrees with the ranking record's table (`BOARD_MOVED_2026-08-11.md:17–24`), re-verified unchanged by the 2026-08-14T21:01Z fetch in `BOARD_RESCORE_2026-08-14.md` §1.2. Guard run at HEAD over the three graded surfaces: **rule-A 0, rule-B 0** on each |
| **F2** | Draft flagged a live defect in a file that no longer had it | **CLEARED** | Draft `:619–623` now reads *"That correction **has landed**: `fdb1ec5c`, 2026-08-11 01:41:00Z, four minutes after this paragraph was written"*, and dates its own check. Its assertion re-executed: `/bin/grep -c "0.0595338"` on the travelling document = **0**; `0.0595335` at `:378` and `:385` |
| **F3** | *"Reissmann's **four** published CSV directories"* | **CLEARED** | Draft `:615` now reads **eight**. Counted on disk: `/home/ubuntu/closure-challenge-benchmark/submissions/reissmann/` holds **8** case directories (plus `reissman_info.txt` and `score_eval.ipynb`) |
| **F4** | *"kept verbatim"* true of the table, false of the headline | **CHANGED SHAPE → F4′, see §1** | The word *verbatim* was correctly retired; the replacement certification was then falsified by `2cec44ee` editing a row **inside** the block it certifies. Executed diff: 3 of 32 lines differ |
| **F5** | One entrant's value attributed to *"the accepted submissions"* as a set | **CLEARED** | `DESCRIPTION_DOCUMENT.md:377–379` now reads *"0.0595335 — **that entrant's value alone, not a figure for the accepted submissions as a set**"* |

### The four §6 observations of 2026-08-11

| obs | status | evidence |
|---|---|---|
| 1. §10 rank claim without figure or interval; *"published 0.059525"* | **CLEARED** (out of this round's declared scope; checked because it was raised) | §10 now strikes the bare placement and carries **P(rank 1) = 50%** with **0–97% at 95%** and its six-entry board, and no longer calls the transcribed value published |
| 2. Paired *t* values rest on the transcribed basis; the disclosure covers only "every pairwise **probability**" | **STILL OPEN — residual** | The disclosure at `DESCRIPTION_DOCUMENT.md:385–390` still says *"every pairwise probability"*; the *t* column is not named. Unchanged in one full round |
| 3. `closure_challenge_stability_physicality_audit.md` §2 states the operator floor as 0.1–0.5% while its own JSON spans 0.078–0.74% | **STILL OPEN** — filed as **D87** | `:218–219` unchanged |
| 4. `PROBABILITY_OF_RANK_2026-08-10.md` asserting the outward margin uses `0.0595338` | **CLEARED** | `:302–308` now carries a dated strike-and-keep amendment naming both errors |

---

## 3. F1 — DURABILITY, GRADED BY MUTATION RATHER THAN BY READING

The brief's question is the right one: the sentence is **correct today**; is the
repair **durable**? Three things were asked and all three were executed.

**(a) Does it carry its board and its date on its face? YES.** The sentence names the
board by **entrant count** and by **two retrieval timestamps**, and the note under it
states in as many words that *"an ordinal is only ever true of a named board at a
named date"*. This is a genuine improvement over the 2026-08-11 repair, which carried
neither and was falsified within hours.

**(b) Is it regenerated from a source, or typed? TYPED.** The note claims the
placement *"is **parsed from** `campaign/BOARD_MOVED_2026-08-11.md`"*. Executed:
`git grep -n "DESCRIPTION_DOCUMENT" -- '*.py'` returns **three** hits, all of them
inside `scripts/self_audit.py` comments and `sdk/tests/test_rank_claim_surfaces.py`.
**No generator writes this file.** The ordinal in that sentence is a typed literal.

**(c) What happens the next time the board moves? NOTHING FIRES.** Measured, not
argued — four runs of `board_placement_faults` at HEAD with `__pycache__` purged,
the scoring pin as the name-to-rank referent and `BOARD_MOVED_2026-08-11.md` as the
ranking referent:

| mutation | rule-A faults | reading |
|---|---|---|
| **M0** control, current text | **0** | clean |
| **M1** the struck parenthetical deleted, current ordinal kept | **1** | the guard faults the **correct** sentence, because the pin binds that entrant to its four-entry position |
| **M2** ordinal falsified to a position the entrant does not hold, struck parenthetical left in place | **0** | **the guard cannot see it** |
| **M3** falsified **and** struck parenthetical deleted | **1** | positive control — the instrument does fire when nothing adjudicates |

The mechanism is in the source and is not a bug: `board_placement_faults` skips a
placement when another placement **within `_PLACE_ADJUDICATED` (400) characters**
binds the same entrant to the board's own rank. The strike-and-keep marker is such a
placement. So the marker that makes the repair honest to a *reader* is the same
marker that makes the sentence **permanently invisible to the guard** — M2 proves it
accepts any ordinal there.

And the second referent does not close the gap. `_ranking_board()` is consumed in
exactly one place: `positions = len(ranking)`, the *count* of positions. **No code
path anywhere checks any entrant's live-board rank.** The guard's own verdict frame
says so — *"NOT re-pointed: the name-to-rank binding, deliberately"*.

**Durability verdict on F1: PASS WITH A NAMED RESIDUAL.** Correct today, honestly
dated, and **mechanically undefended**: it is a typed literal, no generator produces
it, and the one instrument that exists returns 0 whether it is right or wrong. The
next board move falsifies it silently, exactly as the last one did. The residual is
filed as **D85** with the mutation table as its evidence.

*The detector was confirmed live, not silently OFF, before any of this was read: the
benchmark README yields a board (`reissmann 1, wu 2, liu 3, montoya 4`) and the
ranking record yields 6 entrants. Its stated margin — 2 table blocks, 1 qualifying —
is one third-party edit from OFF, which is V16's residual and is not re-litigated
here.*

---

## 4. THE MACHINE-RECORD CHAIN (brief item: "a machine record as source of truth")

`closure_challenge_round5_qcr.json` →
`/leaderboard_comparison_dated_2026_08_07/qcr_vs_rank2_duct_consistency` is the
record that seeded F1's **first** repair, and that repair was falsified the same
night. Checked at HEAD:

- The key is **byte-identical** and still holds the ordinal true of the four-entry
  board its block is dated to. Overwriting it would have made a dated record false
  of its own date; it was correctly not overwritten.
- A dated sibling, `qcr_vs_rank2_duct_consistency_2026_08_11_six_entry_board`,
  is present and is placed **above** the key it supersedes, so a reader or parser
  walking the block in order meets the live statement first. This matches the
  idiom already used by `rank_companion_2026_08_11_six_entry_board` and
  `best_on_board_count_2026_08_11_six_entry_board`.
- **The key was not renamed**, so both surfaces that cite it by name still resolve.

**One residual in that chain, and it is in a ladder report.**
`LADDER_V_V8_REVERIFICATION_2026-08-11.md` §1 cites that key as *"the lab's own
source record for this exact sentence"* — i.e. as the **source of truth** for the
travelling ordinal — and carries no pointer to the supersession. A reader following
F1's citation today lands on the superseded value with nothing on the page to say so.
Corrections to the ladder's own reports do not reopen the ladder (termination rule),
and that document is not mine to edit; filed as **D86**.

---

## 5. THE MECHANICAL CHECKS, RE-EXECUTED

**(a) `not statistically decided`, unbroken on one line.**

| file | per-line | whole-text | verdict |
|---|---|---|---|
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | 6 | 6 | equal → no wrapped occurrence |
| `DESCRIPTION_DOCUMENT.md` | 6 | 6 | equal → no wrapped occurrence |
| package `README.md` | 0 | 0 | makes no rank, best-on-board or probability claim; the rule does not engage |

**Positive control re-seeded this round** (one occurrence broken across a newline, one
clean): **1 per-line vs 2 whole-text.** The instrument can see a wrap, so the
equalities above are measured absences. **PASS.**

**(b) Every `P(rank 1)` carries its interval.** Mechanical sweep over whitespace-collapsed
text, 21 occurrences across the two claim-bearing files. Every occurrence of the
**headline** figure carries `0–97% at 95%` (or, struck, `2–100%` labelled four-entry).
The occurrences without an interval in their window are the **seed-loading legs**
(34.2% / 65.4%), the deletion sensitivity (78.5%) and two references to *"the
P(rank 1)"* carrying no number — each labelled with its loading and each inside the
same section as the headline figure and its interval. **PASS.**

**(c) Banned-claims list.** `/bin/grep -niE "comfortab|novel|official rank"` over all
three files: no `comfortab*` anywhere; every `novel` hit is a **denial**
(*"We claim no novelty for the decline gate either"*, *"Not novelty for the decline
gate"*, *"presenting confidence-gated correction as novel **must be struck**"*);
every `official rank` hit is a denial (*"Not an official rank"*, *"not an official
placement"*). **PASS.**

**(d) Best-on-board count and its baseline clause.** The board move took this count
from 4 of 8 to **2 of 8**, and both survivors are the organisers' own declined
baseline rows, so the count belonging to the trained model is **zero of 8**. Checked
at every site in the graded set — draft §5.2 table, §5.3 item 2, §5.4 item 2 cover
email, §4.7; description document §3.2. **Every site states the count and the
baseline clause in the same breath, and three of them state the zero explicitly.**
No bare count anywhere. **PASS — and this is the strongest work in the round**: the
count moved *against* us and was carried everywhere, unprompted by any external
reader.

**(e) Package integrity, recomputed from disk.** SHA-256 of all eight shipped CSVs
against `MANIFEST.json`: **8 of 8 match**. Shape read off disk: **8 × (1000 rows ×
3 columns)**, no header. **PASS.**

**(f) Scoring-call ledger.** `closure_challenge_round5_qcr.json` →
`scoring_calls.cumulative_distinct_prediction_sets_scored` = **6**, history *floor,
rounds 1–5*. **Unmoved.** No scorer was run in this pass at all — every figure here
is re-derived by arithmetic over committed records, which is a narrower instrument
than the 2026-08-11 round used and is stated so rather than implied.

**(g) Placement guard, whole corpus, at HEAD.** `check_board_placement_words()` over
**1478** tracked UTF-8 surfaces: status WARN, **0 faults on any travelling surface**.
Every fault is internal — `docs/DOCKET.md`, `docs/INSTRUMENT_INTEGRITY_LEDGER.md`,
and three test files whose fixtures are deliberately wrong placements (the known
D81 shape). This confirms `cc906ec9`'s "3 → 0" **measured at HEAD**, not across the
commit gap.

---

## 6. WHAT CHANGED IN THE GRADED TEXT SINCE THE LAST ROUND, AND WHAT IT COST

Twelve commits, +395/−111 lines across two of the three graded files; the package
`README.md` was not touched. The work is overwhelmingly the six-entry board being
carried inward: the count, the probability, the interval, the undecided-pair list,
the margin row and the leader's name. Of the four new findings in §1, **three (G1,
G2, G3) are the same shape**: a repair that updated the *figure* in one place and
left a *sentence built on the old figure* standing a few lines away — the strike
landed on the quotation rather than on the assertion. F4′ is a fourth shape: a later
commit editing text that an earlier commit had certified byte-identical.

**Termination rule, clause 2.** A full re-run of V8 over the text written by the
previous fix rounds **introduces new failures** — G1, G2 and F4′ are all text
written after `174e52bd`. **The fixed point is not reached. Round N+1 exists.**

---

## 7. RESIDUALS, IF AND WHEN G1 AND F4′ CLOSE

Named here so that a later round closing this rung under R-VALUE does not have to
rediscover them:

1. **F1 is mechanically undefended (D85).** Typed literal, no generator, and the
   guard returns 0 for any ordinal in that sentence while the strike marker stands.
2. **The paired *t* disclosure is one word narrow.** *"Every pairwise probability"*
   should read *"every pairwise probability and the paired *t*"*; both *t* values
   rest on the transcribed input and re-derive to −0.497 / −0.956 at full precision
   on the four-entry basis.
3. **G3**: the travelling document's own standing sentence uses a commit anchor
   where the document elsewhere requires entrant count and retrieval date.
4. **V8's condition does not name its own surfaces** (§0). Two graders could draw
   this frame differently and neither would be wrong.

---

## 8. VERDICT, AND WHAT WOULD FALSIFY IT

**V8: FAIL.** Blocked by **G1** — a quantitative claim in the cover email, and a
binding instruction in §5.3 governing the whole package, that state the seed bound
covers 84% of the margin when against the live board the same bound is 177% of it
and the travelling document has withdrawn that conclusion. Aggravated by **F4′**, a
certification of byte-identity falsified by a later commit inside the block it
certifies.

**F1 specifically: PASS WITH A NAMED RESIDUAL** — correct, dated, board-named, and
undefended by any instrument (§3).

**What would falsify this verdict, stated as executable checks:**

- **G1 is wrong** if the three draft sites are inside a struck or dated block that
  my reading missed. Falsifier: `/bin/grep -n "84%" ` on the draft showing each hit
  inside `~~…~~` or under a dated supersession header. I read all four hits; `:652`
  is inside the kept 2026-08-10 banner and is **not** counted against the rung.
  `:729`, `:906` and `:1007` are live prose.
- **G1 is wrong** if 0.002419 / 0.0013658 ≠ 1.77. Falsifier: recompute from
  `closure_challenge_seed_sensitivity.json` and the live-board Yang overall
  0.058013 in `PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md:42`.
- **F4′ is wrong** if the pre-rewrite banner is not the 32 lines I extracted.
  Falsifier: `git show e87650db^:…DRAFT.md | sed -n '554,585p'` diffed against
  `sed -n '628,659p'` of HEAD — three differing lines, or fewer.
- **The F1 durability residual is wrong** if any code path reads an entrant's rank
  from the ranking record. Falsifier: a use of `_ranking_board()`'s return other
  than `len(...)`. I found one use; a second would overturn §3(c).
- **This whole grade is wrong** if the guard was OFF and I read its silence as
  agreement. Falsifier: the guard's frame line, which prints the parsed board and
  the entrant count; both were non-empty in every run here.

*Read-only pass over the graded surfaces. Nothing edited but this file and
`docs/DOCKET.md`. **No solver run, no scoring call — the ledger stands at 6.** The
scoring pin `deb91557` was not moved. Nothing sent, uploaded or registered;
submissions remain PARKED and dispatch is the owner's.*
