# Ladder V — V12 re-graded against HEAD `4651ae93`, 2026-08-16, by a non-author of the repair

*(Measured at `6097856c` and re-measured at `4651ae93` after HEAD advanced mid-grade.
`git diff --name-only 6097856c 4651ae93` touched eleven files; of the six surfaces this grade
rests on, five were byte-identical across the move and the sixth,
`demo-output/website/CLOSURE_CHALLENGE_STATUS.md`, changed without moving either line this grade
cites — `:579` and `:609` were re-read at `4651ae93`. Every figure and line number below held at
both trees.)*

**Verdict: `FAIL`.**

**The three residuals that produced the standing FAIL were repaired, and repaired well.** R1, R2
and R3 were each opened in the landed blob at `6dbb3be6` rather than read from its commit message,
and every figure in the repaired text was re-derived here by execution. All of them reproduced,
to the digit. **The rung fails on a fourth residual of the same class, in the one answer block the
repair never reached.**

**Why this grade was owed.** V12's verdict of record was `FAIL` (2026-08-16), reached by the D227
entitlement measurement at `campaign/LADDER_V_D227_ENTITLEMENT_2026-08-16.md` §4, which found the
grade at `9c2734f8` **NOT ENTITLED** to the label it issued. All three residuals were repaired
thirty-four minutes later at `6dbb3be6` (2026-08-15T21:34:43Z against 21:00:12Z), and that repair
had never been graded by a non-author. The ledger row asked for exactly this pass and said the
answer could be `PASS`.

**Independence.** The grader wrote none of `LADDER_V_PASS3_COLD_2026-08-11.md` at any commit, none
of `6dbb3be6`, none of `9c2734f8`, and none of `LADDER_V_D227_ENTITLEMENT_2026-08-16.md`.
Independence rested on the untracked dispatch record, not on git authorship, which carries one
Ubuntu identity for the whole lab (D130).

---

## 1. The closing condition, in my words before I quote it

V12 asked for a red-team document with two properties. **First**, it had to state the three
weakest points of the entry as a hostile outside reviewer would state them, and set beside each
one **the best answer the record can support** — not merely an answer, and not merely a true
answer, but the strongest one the lab's own record already holds. **Second**, the product had to
be usable as Sanaa's standing briefing when the steward asks a follow-up question: it **becomes**
the briefing, so it is a live instrument rather than a signed snapshot of a moment.

Quoted from its face, `LADDER_V_TRIPLE_VERIFICATION.md:370-372` at `4651ae93`:

> **V12. The cold agent writes the skeptic's report**: the three weakest points of the entry as an
> outside reviewer would state them, each with the record's best answer beside it. This becomes
> Sanaa's briefing for any follow-up questions from the steward.

Two readings of clause (i) were settled by the D227 measurement and are taken here as governing,
because departing from them at the verdict paragraph after adopting them at the scope paragraph is
precisely what voided the grade at `9c2734f8`:

* ***"The record's BEST answer" is a quality clause even with no accuracy clause imported.*** An
  answer demonstrably worse than one the record already holds is not the record's best answer.
* **A product that must not yet be read as the briefing has not met a criterion saying it becomes
  one.**

---

## 2. The board, re-derived here rather than read

No figure below was copied from any document, including the dispatch that ordered this grade.
`LIVE_BOARD` was lifted out of `sdk/scripts/probability_of_rank.py` by `ast.literal_eval` on the
module's assignment nodes — **parsed, never imported** — together with `CASES`, `SEED_DEPENDENT`,
`SEED_BOUND_ON_OVERALL`, `B_MAIN`, `SEED_MAIN`, `N_OUTER`, `N_INNER`, `SEED_DOUBLE` and the three
`DECIDED_*` thresholds, and joined to `round5_per_case_full` in
`demo-output/website/closure_challenge_round5_qcr.json`. Each of the six transcribed rows
reproduced its own published overall to four decimals before anything else ran.

| quantity | re-derived here |
|---|---|
| positions | **7** — six entrants on the board fetched 2026-08-11T23:33Z, plus our row |
| our per-case ranks | **2, 2, 1, 1, 3, 4, 4, 7 of 7** |
| best on board | **2 of 8** (`alpha_05_4071_4048`, `alpha_05_4071_2024`) |
| earned by our model | **0 of 8** — both best-on-board cases sat on the untrained RANS identity floor at the scored precision (`0.0461`, `0.0719`), i.e. the organisers' own field passed through by the decline gate |
| overall | `0.056647191704213645`, **rank 1 of 7**, nearest rival Yang at `0.0580125` |
| margin | **`0.0013653083`** over Yang |
| P(rank 1) | **50.2%** — `200,609 / 400,000` at seed `20260810` |
| interval | **0–97% at 95%** — double bootstrap 2,000 × 4,000 at seed `31415`, `[0.0025, 0.9690]` |
| seed bound vs margin | **177%** on the JSON bound `0.002419121853891026`; **176%** on the script's rounded `0.0024` |
| pairwise not decided | **4 of 6** — Yang, Reissmann, Wu & Zhang, Tian; Liu and Montoya decided |
| leave-one-out losing point rank 1 | **3 of 8** — `alpha_15_13929_4048` → 2, `alpha_15_13929_2024` → 3, `alpha_05_4071_4048` → 2 |

Every one of those matched the board this grade was told to expect, so the "if you do not obtain
those, that is the finding" branch did not fire. **The one number that admits two answers is the
seed-bound share**, and that is R3's subject rather than a discrepancy: `0.0024 / 0.0013653083` =
**175.8%** and `0.002419121853891026 / 0.0013653083` = **177.2%**.

---

## 3. The three named residuals, each opened in the landed blob

### R1 — **REPAIRED.**

At `6dbb3be6` the recommendation at `:552-555` was struck in place and kept, and an R1 block at
`:557-566` recorded why. The restated recommendation at `:568-598` carried the live figure with
both of the things the document's own binding rule demands — **`P(rank 1) = 50.2%`**, the
**`0–97% at 95%`** interval, and the board named by **entrant count and retrieval date**. Its third
condition, that a commit anchor is not an admissible board identifier, was checked rather than
accepted: the construction it names as still live in the **shipped** `site/closure.html:502` **was
still live at `4651ae93`**, read directly out of `dist/certonomous-demo/site/closure.html:502`,
which carries *"rank 1 of 5 is our local scoring at a pinned benchmark commit"* unstruck. The
citation is exact and the word *"shipped"* is doing real work: the **source** page
`demo-output/website/closure.html` had that sentence struck twenty hours earlier at `3010e12f`
(2026-08-15T01:33:24Z) and replaced with *"rank 1 of 7 entrants counting us"*. Distinguishing the
source from the shipping archive, and citing the archive by path and line, was the harder and the
correct call.

### R2 — **REPAIRED.**

At `:650-652`, *"all four published entries"* was struck and replaced with *"all SIX published
entries"*, and the stale `0.0760` struck in favour of **`0.0748`**. Re-derived here over the
`alpha_05_4071_*` columns: on `alpha_05_4071_4048` the best of the six was **`0.0569`** (Wu &
Zhang) against our `0.046108`; on `alpha_05_4071_2024` the best was **`0.0748`** (Yang) against our
`0.071863`. The block's account of the displaced value also held — `0.0760` was Reissmann's, best
on the four-entry board and second on the six, ahead of Liu's `0.0769`. The block added *"the count
belonging to our own model is 0 of 8"*, which is the figure §2 above derived independently.

### R3 — **REPAIRED.**

The two adjacent bullets no longer stated one bound two ways. The arithmetic table at `:417-422`
was reproduced exactly here: `0.056647191704213645 ± 0.002419121853891026` = **`0.059066`** and
**`0.054228`**, and `0.056647191704213645 ± 0.0024` = **`0.059047`** and **`0.054247`**, the struck
pair, identified as `SEED_BOUND_ON_OVERALL` at `sdk/scripts/probability_of_rank.py:64`. Both
adverse figures sorted **2nd of 7**, as the block claimed, so the conclusion did not move.

### The rest of the repaired text, checked because a repair that gets the repair right and the
### surrounding numbers wrong is a worse outcome than no repair

Everything the W2 repair block stated re-derived exactly: `34.2%` / `50.2%` / `65.4%` under adverse
/ as-scored / favourable seed loading; per-case dispersion against Yang `0.020441`, **fifteen
times** the margin; the `AR_1_Ret_360` gap to Wu & Zhang's printed `0.0455` at `2.96e-05`, **0.591
of a half-ulp**, which is what makes `4 or 5 of 8` the only honest cell; best published on `AR_1`
and `AR_3` of `0.0291` and `0.0311`, leaving us behind by `0.0164` and `0.0089`. **The count
`200,609 / 400,000` at `:433` was reproduced here to the draw.** The R1 block's own separate
bootstrap reported `200,924 / 400,000` at `:605` and declared itself *"written for this repair with
its own seed"* — two independent Monte-Carlo runs agreeing at `50.2%` is corroboration, not a
second value of one quantity, and it is not counted against the rung.

---

## 4. The residual that fails the rung: `:339`, inside W1's answer

The 2026-08-15 repairs reached **W2** (the repair block) and **W3** (R2). They never reached
**W1**, and the repair block said so in its own scoping: its binding rule was written to govern
*"every corrected figure **below**"*, and W1 sits above it. R2's block conceded the same shape one
section later — *"§W3 was outside the scope of the 2026-08-15 repair block"* — and extended the
repair downward. It was never extended upward.

At `4651ae93`, `LADDER_V_PASS3_COLD_2026-08-11.md:336-340`, unstruck, inside the answer beside
weakest point **W1**:

> - **The `AR_14_Ret_180` loss accepted in advance, in writing**, with the reason stated: keeping
>   ML on AR_14 while switching the other two is exactly the per-case selection the rule exists to
>   forbid. **The loss then happened** — 0.0325 → 0.0353, the nominal best-on-board tie gone —
>   **and was not reverted.** A pre-registration that never costs anything is decoration; this one
>   cost something and was honoured.

**Measured, not argued.** The `AR_14_Ret_180` column of the six-entry board, parsed from
`LIVE_BOARD` and never imported, ran Yang `0.0250`, Reissmann `0.0325`, Wu & Zhang `0.0350`,
Montoya `0.0487`, Tian `0.0527`, Liu `0.0548`. Round 4's `0.0325` therefore stood **2nd of 7**,
tied with Reissmann for **second**, with Yang `0.0075` clear of both. Round 5's `0.035339` stood
**4th of 7**. On the four-entry board, and only there, `0.0325` was rank **1 of 5** and the tie was
for best.

**So there was no best-on-board tie on the board of record to give up.** What the pre-registration
actually cost on that board was a fall from second place to fourth on one case.

**Why this is inside clause (i) and not a trivium.**

1. **It is load-bearing for W1's answer.** W1's charge is that the lab's pre-registration was
   theatre — that it froze the last degree of freedom after the one that mattered had been spent.
   The answer's clinching move is *"a pre-registration that never costs anything is decoration;
   this one cost something and was honoured."* The size of that cost **is** the rebuttal, and it
   was overstated, in the direction that flatters us, on the one page arguing that the lab's
   self-reporting can be trusted.
2. **The record already held the better answer, and had held it for three days before the
   repair.** `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:579` at `4651ae93` reads
   `~~3 of 5 — **the nominal best-on-board tie is lost**~~ → **4 of 7** (best is Yang's 0.0250; the
   tie is lost)`, and `:609` carries *"on the six-entry board fetched 2026-08-11 the case sits 4th
   of 7 entrants, behind Yang's 0.0250 as well — note added 2026-08-12"*. **The lab itself struck
   the four-entry form of this exact sentence.** By the lab's own repaired reading the phrase is
   board-count dependent, and the four-entry version stands withdrawn everywhere the lab has
   looked — except here.
3. **The same document holds the frame that condemns it.** `:373-380` declares the six-entry board
   the board of record and requires every figure to travel with its board identity; `:452` states
   the six-entry best-on-board count as **2 of 8**, naming the two decline-gate cases, of which
   `AR_14` is not one. The document contradicts `:339` 113 lines later.
4. **The "world moved after delivery" defence does not reach it, and it is the strongest defence
   available.** The document was written 2026-08-10; the board moved 2026-08-11T23:33Z. D227 §5
   ruled that a closing condition cannot be failed by the world moving after delivery — but that
   ruling protected V13, whose product is a **signed snapshot**. V12's clause (ii) makes its
   product a **living briefing** that must answer the steward's next question, and the rung's own
   owners adopted that reading twice rather than pleading the delivery date: the repair block wrote
   *"A red-team brief that hands the skeptic a weaker version of the true case is a defect in the
   rung's own instrument"*, and repaired W2 and W3 for currency on that ground. **Having declined
   the defence twice, W1 cannot claim it.**

`§0` offers no cover either. At `:44-48` the cold pass listed `CLOSURE_CHALLENGE_STATUS.md` among
what it deliberately did not open, describing it as *"the authority the package cites for its
best-on-board count"*. That explains the origin of `:339` honestly and it is to the pass's credit,
but the closing condition is about the record's best answer, and no global currency caveat was ever
added at the head of the document.

**Clause (i) was therefore not met at `4651ae93`.** Clause (ii) carried no self-declared blocker
this time — the R1 block stated in terms that the struck sentence *"must not be acted on"* and
supplied an admissible restatement — so the verdict rests on clause (i) alone.

---

## 5. The sweep, its controls, and its strike-balance audit

Two sweeps were run over the **whole** file, never over enumerated line ranges. Every pattern was
built with `\s+` and no literal space, because this file's headings soft-wrap. Both were run twice,
once with controls planted and once live, so each pattern class could be shown to fire.

**Strike-balance audit (live file).** `~~` markers **34**, even; depth walked marker by marker
stayed in `[0,1]` and ended at **0**; `~~~` fences **0**; `<s>` **0**, `</s>` **0**, `\sout{`
**0**. Balanced, so blanking was safe. **17 strike spans** were then blanked **in place**, each
struck character replaced by a space so that byte offsets and therefore line numbers were
preserved; length was asserted unchanged after blanking.

**Controls, confirmed by readback before each run.** The positive control was a two-line block
carrying one live instance of **every** pattern class — *"all four published entries"*, `rank 1 of
5`, `0.0760`, `0.674 / 0.67 / 68%`, `0.0029`, `0.0028863`, `84%`, `0.059047`, `0.054247`,
`2–100%`, and for the second sweep *"best on the board"*, *"beats every published entry"*, *"the
tie is lost"* — deliberately split **across a line break** so that a literal-space pattern would
have missed it. The negative control was the identical text wrapped in `~~ ~~`. Each control was
located by exact substring and its two lines printed back before the sweep ran.

| pattern class | control run | live run | class proven live |
|---|---|---|---|
| four-entry framing near entries/entrants/board | 15 | 14 | yes |
| bare `all four` | 4 | 3 | yes |
| `rank 1 of 5` / five-entry denominator | 3 | 2 | yes |
| stale best-published `0.0760` | 2 | 1 | yes |
| stale `0.674` / `0.67` / `68%` | 8 | 5 | yes |
| stale margin `0.0029` / `0.0028863` | 6 | 4 | yes |
| stale seed-bound share `84%` | 1 | **0** | yes |
| stale loaded overalls `0.059047` / `0.054247` | 5 | 3 | yes |
| stale `2–100%` interval | 1 | **0** | yes |
| board-comparative claims (second sweep) | 16 | 13 | yes |

**The two zeros are load-bearing and both are backed by a control that fired**: `84%` and `2–100%`
survive in the file only inside strike spans, and the blanking is what removed them. The negative
control appeared in **no** class in either run, which is the other half of the proof — the blanker
does blank.

**Adjudication of the live hits.** The second sweep enumerated every unstruck board-comparative
claim in the file and tagged each by its enclosing heading, so clause (i) could be closed by
enumeration rather than by spot reading. Inside the three W answer blocks it returned **W1: one
line, `:339`** — the residual of §4 — **W2: `:452`, `:457`, `:459`, `:499`, `:512`**, all
six-entry-correct or explicitly reconciled by the repair block, and **W3: `:650`, `:651`, `:652`,
`:665`, `:675`**, all repaired. Outside the W blocks it returned `:46` (§0's frame note) and `:265`
(§2's package-defect D7). Of the first sweep's fourteen four-entry-framing hits, eleven were the
repair blocks naming the four-entry board **in order to strike it**, which is the intended shape;
the remaining three (`:116`, `:702`, `:720`) are handled in §6.

---

## 6. Filed, not appended: findings outside V12's declared scope

Three findings fell outside clause (i) — they sit in §1 (`A11`, which is V11's product), in §2's
package-defect list, or on other surfaces entirely. Under the dispatch they are **filed as docket
rows and are not part of this verdict**. They landed at `644793a6` as **D250, D251, D252**; the
commit message of this grade at `b4596cb4` named them D248–D250, which is wrong — those two IDs
were claimed by another agent between the read that chose them and the read immediately before the
docket landing, and the docket commit took the next free IDs instead.

* **D250** — four-entry reproduction framing outside the W blocks: `:116-119` (*"All four accepted
  submissions re-score… **4 / 4**"*), `:265` (*"best-on-board count of 4 of 8"*), `:702` (*"all
  four published entrants re-scoring to their board values"*). The reproduction check was re-run
  here over **all six** entrants and all six reproduced their published four-decimal overalls, so
  the record now supports **6 / 6**. (`:720`, *"All four are writing"*, is the four recommended
  fixes and is not a board claim.)
* **D251** — `:339`'s four-entry sentence had travelled unstruck to two further surfaces:
  `demo-output/website/ACTIVE_RESEARCH.md:29`, a **V10-enumerated** surface whose *same paragraph*
  was repaired `1 of 5` → `1 of 7` on 2026-08-15 while the tie clause beside it was left; and
  `campaign/LADDER_V_V13_CLOSEOUT.md:184`, verbatim.
* **D252** — the shipped archive states its rank two ways: `dist/certonomous-demo/site/closure.html`
  reads *"rank 1 of 7 on the live"* at `:139` and *"rank 1 of 5"* at `:502`. The path is
  **untracked**, so no `git grep` sweep can see either line; `:502` was already named by the R1
  block, `:139` was not, and the inconsistency between them was on no record found here.

---

## 7. Verdict

**V12: `FAIL`, 2026-08-16, against `4651ae93`.**

The three residuals of record were repaired at `6dbb3be6` and the repair is, on the evidence
above, unusually good — every figure in it re-derived here by execution and every one of them
landed exactly, including two the repair could have rounded away. **The rung fails because the
repair was residual-driven rather than sweep-driven.** It closed the three defects a grader had
named and did not ask whether the same defect class survived in the one answer block outside its
declared scope. It did — in the answer whose subject is whether this lab's self-reporting can be
trusted, overstating what the lab's own pre-registration cost it, against a correction the lab had
already written down three days earlier on its own status page.

**What would close it.** Strike `:339`'s *"the nominal best-on-board tie gone"* in place, keep it
visible, and state the six-entry reading beside it — round 4's `0.0325` stood **2 of 7**, tied with
Reissmann for second behind Yang's `0.0250`, and round 5's `0.035339` stands **4 of 7**; the loss
and the refusal to revert are unaffected and remain the honest core of the bullet. Then sweep W1 as
W2 and W3 were swept. That is a writing task, it needs no scoring call and no compute, and the
grade after it could legitimately be a plain `PASS`.

**`PASS WITH RESIDUALS` was not available** and was not used: it was withdrawn lab-wide at
`7c44cbe2`, and issuing it is what voided the grade at `9c2734f8`. The verdict here is one of the
two legal labels.

---

*Non-author grade of rung V12, Ladder V. No package file, score, board or ledger was modified by
this pass; no solver was launched; no scoring call was made and the ledger stands at 6; nothing was
submitted, uploaded, registered or sent. `dist/` was read and not written.*
