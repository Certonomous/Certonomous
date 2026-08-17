# Ladder V — rung V8 re-verification, 2026-08-17

**Verdict: GATE FAIL — one blocking finding. Every other leg of the rung clears on
executed evidence, including all three findings (G1, G2, G3) that the 2026-08-14
round of record left open.**

Owner: an agent that wrote none of the graded text and none of the repairs under
test. Measured in a clean detached worktree at `d3f04232`; the shared index was
not touched and holds stale ancestor blobs in the reverting direction, which is
why the live checkout was not used.

---

## 0. FRAME

| item | value |
|---|---|
| repository HEAD when graded | `d3f04232` (parent `f7a14346`) |
| measurement worktree | detached, `git status --short` = 0 entries |
| graded set, byte-identity | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` and `closure_challenge_submission_round5/` are **byte-identical between `f7a14346` and `d3f04232`**, so measurements taken at the earlier frame carry forward unchanged |
| scoring calls | **zero**. Every figure below is arithmetic over committed records |

### The criterion, quoted from source

`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:339-344`:

> - **V8. Claims-language audit of the cover email + description document**: every quantitative
>   sentence maps to a named artifact; the banned-claims list enforced — no novelty claim on gated
>   correction (§7.4), no "comfortable" AR_14 lead (0.00003), no best-on-board counts that lean on
>   organizer-baseline rows (§4.7), no "official rank" language anywhere (local scoring stated
>   plainly), soft-adaptive-leakage disclosure present in the lab's own words (§4.3). A claims
>   table: sentence → artifact → verdict.

Plus the 2026-08-10 strengthening and amendment and the 2026-08-12 recomputation
note (`:345-381`): every rank claim, internal or external, carries **P(rank 1)**,
**its interval**, **its board**, and the **not-decided pairs**.

### R-CONVERGE — scope declared BEFORE grading

1. **Artifacts:** the cover email (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §5) and
   the travelling package (`DESCRIPTION_DOCUMENT.md`, package `README.md`) — the
   frame of the 2026-08-11 and 2026-08-14 rounds, **adopted unchanged for
   comparability**.
2. **Claims:** the open findings of record (G1, F4′) and the 2026-08-15 residuals
   R1–R3; plus every quantitative or placement sentence in the graded set.
3. **Anything else → docket**, not appended to the rung.

**The frame is the whole disagreement between the last two rounds, so it is ruled
explicitly rather than inherited silently.** The 2026-08-15 grade read V8 as
reaching only §5.4 and `DESCRIPTION_DOCUMENT.md`, put the §5 banner out of frame,
and recorded "PASS WITH RESIDUALS" — a label defined nowhere and since withdrawn
by chief ruling. That grade said in its own §7: *"A grader who reads V8's criterion
as covering the whole draft should read this verdict as FAIL on F4."* The bytes
were never in dispute between the two rounds; only the frame was. I rule §5 **in
frame**, on two grounds taken from the record rather than from preference:

- **V8's own deliverable lives in §5.** The criterion ends *"A claims table:
  sentence → artifact → verdict"*, and §5.2 **is** that claims table. The banner is
  the preamble that dates and governs it. A rung cannot put the container of its own
  deliverable out of frame.
- **V15 routes this text through V8 by an explicit rule** (`LADDER_V_TRIPLE_VERIFICATION.md:502-503`):
  *"any text written during the ladder — by any pass, including fix passes — must
  pass V8's claims table before the ladder goes green."* The sentence that fails
  below was written by the V8 fix round itself (`b65bdf01`). It is ladder-written
  text, and V15 sends ladder-written text to V8's claims table.

---

## 1. THE BOARD, RE-DERIVED — never quoted

Computed from the scoring artifacts, not read off any brief, README or prior
record: our per-case values from `closure_challenge_round5_qcr.json` →
`official_test_harness_result.round5_per_case_full`; the board from
`sdk/scripts/probability_of_rank.py`'s `LIVE_BOARD` (fetched 2026-08-11T23:33Z);
the bound from `closure_challenge_seed_sensitivity.json` →
`spreads.overall_equivalent_S_bound`. `sdk/scripts/probability_of_rank.py` was
**executed**, not cited.

| quantity | re-derived value |
|---|---|
| entrants on the board / positions counting ours | 6 / **7** |
| our overall | **0.056647191704213645** (mean of the eight; agrees with `round5_overall_full` to 1e-12) |
| our overall standing | **rank 1 of 7** |
| per-case ranks, in `CASES` order | **2, 2, 1, 1, 3, 4, 4, 7** of 7 |
| best-on-board (strictly lowest) | **2 of 8** — `alpha_05_4071_4048`, `alpha_05_4071_2024`; both are the organisers' own declined baseline rows, so **0 of 8 earned by the trained model** |
| nearest entrant / margin | Yang 0.0580125 / **0.0013653082957863563** |
| seed bound ÷ margin | 0.002419121853891026 / 0.0013653 = **1.7719 → 177%** |
| P(rank 1) | **50.2%** (50.15% over 400,000 draws) |
| double-bootstrap 95% band | **0.2% – 96.9% → "0–97% at 95%"** |
| not-decided pairs | **four** — Yang, Reissmann/Fang & Sandberg, Wu & Zhang, Tian/Buchanan/Hickel & Dwight; Liu and Montoya decided |

**Every figure supplied to me as ground truth re-derived exactly. None failed
re-measurement.** `deb91557` is confirmed as a scoring pin that **scores but does
not rank** (the script's own docstring, and it carries four entrants); it is not
an admissible board identifier, and the graded set says so in its own words.

Two figures the travelling document states were re-derived independently and hold:
`AR_1_Ret_360` ties Wu & Zhang at 0.0455 − 0.045470 = **0.00003**, and
`AR_3_Ret_360` at 0.0399 − 0.039982 = **0.00008**.

---

## 2. THE RECOGNISER, ITS CONTROLS, AND ITS RECALL

Delimiter blanking, offsets preserved, **in the mandated order**: strike spans
first (`~~`, `<s>`, `<del>`) and tracked; then line-continuation prefixes (`>`,
`> >`, list markers, table pipes); then emphasis (`**`, `*`, backticks, `<b>`,
`<em>`, `<strong>`, `<i>`) — **never `~`, never `_`**. Markers overwritten with
spaces in place, same length, newlines untouched; a length assertion fails the
sweep on any offset drift. Joiners are `[-\s]{1,20}` between words. Whole files,
never enumerated line ranges.

**A defect in my own instrument, found by the controls and stated because it is
the reason the controls exist.** The word-joiner `[-\s]{1,20}` **cannot match a
zero-width separator**, so `84%` — the exact string this rung turns on — did not
match, while `84 per cent` did. Four recognition controls failed on the first run.
A separate boundary class `[-\s]{0,20}` was added for number↔symbol joins and the
controls then passed. A reachability control would have reported the files opened
successfully and hidden this completely.

**Known-site recall, measured not asserted.** The recogniser was run against the
draft at `f8c889cc`, the frame of the verdict of record, where that round named
four `84%` sites: `:652`, `:729`, `:906`, `:1007`. The sweep returns all four.
**Recall 4/4 = 100%** on independently-named known positives.

**Controls — every one a RECOGNITION control; no reachability control was used or
credited.** Planted **by line index, never by anchor string**, into a copy, and
**every plant read back from disk before anything was run**. Readback caught two
further errors that would each have produced a silent zero: a multi-line payload
that shifted every later plant index, and a plant that landed **inside a genuine
multi-line strike span** and was legitimately blanked.

| control | kind | class | result |
|---|---|---|---|
| plain, claim's own vocabulary | RECOGNITION | A_84pct | fired |
| inflected (*"84 per cent … covering it"*) | RECOGNITION | A_84pct | fired |
| wrapped across three `>` lines | RECOGNITION | A_84pct | fired |
| emphasis-wrapped (`**84%**`, backticks) | RECOGNITION | A_84pct | fired |
| reordered clause | RECOGNITION | A_ratio_ctx | fired |
| 177% form | RECOGNITION | A_177pct | fired |
| bare rank claim | RECOGNITION | B_rank | fired |
| rank claim wrapped across a newline | RECOGNITION | B_rank | fired |
| `P(rank 1) = 50%` | RECOGNITION | C_prob | fired |
| interval form | RECOGNITION | C_interval | fired |
| *"a comfortable lead on the AR_14 duct"* | RECOGNITION | D_comfortable | fired |
| *"our official rank is first"* | RECOGNITION | D_officialrank | fired |
| *"the decline gate is novel"* | RECOGNITION | D_novel | fired |
| commit anchor as board | RECOGNITION | E_commitboard | fired |
| best-on-board count | RECOGNITION | F_bestonboard | fired |
| byte-identity certification | RECOGNITION | G_byteident | fired |
| AR_14 tie/lead | RECOGNITION | H_ar14 | fired |
| `not statistically decided` | RECOGNITION | H_notdecided | fired |
| **struck negative** `~~…84%…~~` | RECOGNITION (negative) | A_84pct | **silent** |
| **struck negative** `<del>a comfortable lead</del>` | RECOGNITION (negative) | D_comfortable | **silent** |
| **struck negative** `<s>we hold rank 1</s>` | RECOGNITION (negative) | B_rank | **silent** |

18 recognition controls fire, 3 struck negatives stay silent. **Every zero below
is therefore a measured absence.**

---

## 3. THE BLOCKING FINDING

**The banner's certification of byte-identity is false at HEAD, and has been false
and unrepaired through three consecutive rounds.**

`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:620-621` certifies:

> **Its thirty body lines are byte-identical** — every row of the ten-row defect
> table, including the round-4 numbers it indicts — but its heading was replaced
> and demoted `##` → `###` … the blank line that closed the blockquote became `>`.

Executed at `d3f04232` by a third extraction path independent of both prior rounds
(heading-anchored alignment, not fixed line numbers): the kept banner was pulled
from `git show e87650db^` and from HEAD, aligned index by index, compared
byte-for-byte.

- Block is **1 heading + 31 lines** at both revisions.
- **Three of 32 lines differ: indexes 0, 21 and 31.**
- Index 0 (heading) — **declared** by the sentence.
- Index 31 (closing blank → `>`) — **declared** by the sentence.
- **Index 21 — NOT declared.** It is row 22, and it **is a row of the ten-row
  defect table** the clause explicitly certifies. The difference is the
  parenthetical inserted at `2cec44ee` (2026-08-12): *"(figures as recorded at this
  banner's date against the four-entry board; the rule's live figures are 50% and
  0–97% on the six-entry board …)"*.

So **twenty-nine** body lines are byte-identical, not thirty, and the clause
*"every row of the ten-row defect table"* is false. The certification was written
at `b65bdf01`; row 22 was edited later, at `2cec44ee`. **A later commit falsified
an earlier certification and nothing since has repaired it.**

This is a quantitative sentence that does not map to its named artifact — the first
clause of V8's criterion, verbatim — and it is ladder-written text, which V15
`:502-503` routes through V8's claims table. Both the 2026-08-14 round (as F4′,
HIGH) and the 2026-08-15 grade (as R1, *"F4 is NOT repaired"*) measured the same
bytes and got the same answer. This is the third independent reproduction.

---

## 4. EVERYTHING ELSE IN THE RUNG CLEARS

| leg | status | executed evidence |
|---|---|---|
| **G1** — the 84%/177% inversion | **CLEARS** | Four live `84%` sites remain in the draft. Three (`:782`, `:1000`, `:1142`) sit **inside explicit dated corrections** that state *"177%, not 84%"* and give the derivation. The fourth (`:673`) is inside the kept 2026-08-10 banner and **is genuinely byte-identical** to the pre-rewrite record, so it stands as a dated record on its own bytes. The cover email and the travelling document both state 177% with the reversal named as a reversal |
| **G2** — the letter giving two answers | **CLEARS** | `:1121-1122` now strikes *"~~by 0.0029 over Reissmann, Fang and Sandberg~~"* and states **"by 0.001365 over Yang, at 0.058013"**; the letter discloses its own four-day window |
| **G3** — commit anchor as board | **CLEARS** | `DESCRIPTION_DOCUMENT.md` restates the standing in the six-entry/retrieval-date idiom; §5.3's binding rule now states *"a commit anchor is **not** an admissible board identifier"* |
| **rank claims carry the quadruple** | **PASS** | Cover email `:1119-1131`: six-entry board, both retrieval timestamps, margin over the named entrant, **P(rank 1) = 50.2% with a 95% interval of 0–97%**, the four undecided pairs, and *"it is not a placement on your board and we do not claim one"*. Travelling document `:285-292`: *"seven rows counting ours, so **rank 1 of 7**"* — matches my re-derivation exactly |
| **no bare probability** | **PASS** | Every occurrence of the headline figure carries its interval. The intervalless occurrences are the seed-loading legs (34.2% / 65.4%) and the deletion sensitivity (78.5%), each labelled with its loading and each in the same section as the headline figure — all three re-derived by my own run of the script |
| **no "comfortable" AR_14 lead** | **PASS** | **Zero** `comfortab*` hits in all three graded files. Repo-wide, 21 hits of the `comfortable`-near-`AR_14` class: **every one is a prohibition or a record of the defect** (*"must not be reported as a comfortable…"*, *"No surface claims a comfortable AR_14…"*), none an assertion |
| **no "official rank" language** | **PASS** | Every hit is a denial — *"Not an official rank"* (`DESCRIPTION_DOCUMENT.md:548`), *"not an official placement"* |
| **no novelty on gated correction** | **PASS** | Every hit is a denial — *"No sentence in this package presents confidence-gated correction as novel"* (`:362`), *"Not novelty for the decline gate"* (`:551`) |
| **best-on-board not leaning on baseline rows** | **PASS** | Re-derived independently as **2 of 8, both organiser baseline rows, 0 of 8 to the trained model**. §4.7's heading states it; no bare count found |
| **soft-adaptive-leakage disclosure in the lab's own words** | **PASS** | Disclosure 3b carries the round-5 concession quoted from `R5_RULE_FREEZE.md` |
| **package `README.md`** | **PASS** | Makes no rank, probability or best-on-board claim. Its `deb91557` is a `git checkout` reproduction instruction, not a board identifier; its *"byte-identical"* is about CSV files and is true |

---

## 5. VERDICT

**V8: GATE FAIL.** One blocking finding: the byte-identity certification at
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:620-621` is false, by three lines against a
sentence that declares two, with the undeclared line falling inside the very table
the clause certifies. Unrepaired across three rounds.

Stated plainly because the last round's label obscured it: **this is a plain GATE
FAIL, not a pass with residuals.** The graded text is in genuinely good condition —
G1, G2 and G3 all clear, the board move is carried everywhere including where it
costs us, and the travelling document is the strongest it has been. One false
sentence still fails the rung, because "every quantitative sentence maps to a named
artifact" is the whole of the criterion and this one does not.

**A vocabulary discrepancy, reported for ruling rather than resolved.**
`docs/charters/VERIFICATION_CHARTER.md:95-96` and
`docs/charters/REPORTING_CHARTER.md:210-211` fix the gate vocabulary as **PASS,
GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED**. The ladder's own rung cells use
bare **FAIL**. I have used the charter term. Which of the two governs a rung cell
is not mine to decide and is flagged, not smoothed.

### What would falsify this verdict

- The certification is defensible if the pre-rewrite banner is not the 32 lines I
  extracted. Falsifier: align `git show e87650db^` against HEAD from the banner
  heading and get two differing lines, or find index 21 declared by the sentence.
- The verdict flips to PASS if §5 is ruled out of V8's frame. That is a live
  question, not a settled one — but it must be ruled on its merits, and it must
  contend with V15 `:502-503`.

---

## 6. BLIND CLASS — what this instrument structurally cannot see

1. **Rendered binaries.** 12,700 of 13,816 tracked files were swept as UTF-8;
   **1,116 were not decodable and were not read** — 875 `.png`, 122 `.gz`, 50
   `.stl`, **50 `.pdf`**, 11 `.bin`, and 6 others. **The 50 PDFs were not rendered
   and read visually in this pass.** `\sout{}` is strike-and-keep and grep cannot
   see it, so a PDF is not swept by being grepped; it is simply unswept here.
   `demo-output/website/latex/closure_challenge_report.pdf` is the one that would
   matter, and it is **named as unmeasured rather than reported as zero**.
2. **The LaTeX source was swept but is out of V8's frame.**
   `closure_challenge_report.tex` carries live hits for `D_comfortable` (`:887`,
   `:970`, `:1013`, `:1054`), `D_officialrank`, `B_rank`, `C_interval` and
   `E_commitboard`. Not adjudicated here — V10's and V14's rungs. **Filed, not
   appended.**
3. **Semantics.** The recogniser matches strings, not assertions. It cannot
   distinguish a claim from a prohibition or a quotation; every hit above was read
   by eye, which does not scale and is not an instrument.
4. **Zero-width and homoglyph evasion.** Blanking covers `~~`, `<s>`, `<del>`,
   quote/list/table prefixes and the listed emphasis markers. A claim split by a
   zero-width space, an HTML comment, `_`-emphasis (deliberately never blanked), or
   a Unicode homoglyph digit would pass unseen.
5. **The corpus-wide prefilter.** The repo-wide pass gated files on
   `8[-\s]{0,20}4|comfortab|official`, which is strictly wider than the classes it
   gates but is not universal — a `84` split across a newline would evade it. The
   graded set was swept **unfiltered**, so this bounds only the out-of-frame sweep.
6. **Untracked and ignored trees.** Only tracked files were swept. `dist/` and
   other gitignored trees were not reached in this pass.

*Read-only over the graded surfaces. No solver, no scoring call — the ledger stands
at 6. The scoring pin `deb91557` was not moved. Nothing sent, uploaded or
registered.*
