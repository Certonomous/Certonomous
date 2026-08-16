# D227 measured — were the five PASS WITH RESIDUALS rungs entitled to that verdict?

**Executed 2026-08-16T00:47Z → 01:2xZ by a non-author of every artifact it grades.** No solver
run. No scoring call — **the scoring ledger stands at 6**. Nothing sent, uploaded, filed or
registered; the submission is **PARKED** and reserved to Katie. The scoring pin `deb91557` was not
moved. `dist/` was read and **not written**. This pass wrote three things: this document, the
**ledger rows** of `campaign/LADDER_V_TRIPLE_VERIFICATION.md`, and `docs/DOCKET.md`.

**Dispatched by the chief ruling at `20966952`** (2026-08-16T00:46:33Z), which names the test
rather than the answer and asks to be measured rather than inherited. It is measured in §7.

**Verdicts, up front, so they can be argued with before the evidence is read:**

| rung | residuals | entitlement | what decides it |
|---|---|---|---|
| **V6** | 3 | **ENTITLED** | none of the three is a finding's verdict or the QCR compliance line; all three sit in the block's own bookkeeping preamble or in an evidence locator beside a verdict that is correct |
| **V8** | 3 | **ENTITLED** | the criterion names two artifacts; all three residuals sit outside both, are not rank claims, and are not the figure the amendments govern |
| **V12** | 3 | **NOT ENTITLED → FAIL** | **R1** — the answer beside weakest point W2 instructs the lab to publish `P(rank 1) ≈ 0.67`, which the same document strikes 34 lines above. The criterion's own words are *"the record's **best** answer beside it"* |
| **V13** | 4 | **ENTITLED** | three of the four went stale *after* the close-out was signed, by other agents' later commits; the fourth is not a PASS/FAIL cell and carries an in-cell pointer to the section that updates it |
| **V14** | 6 | **NOT ENTITLED → FAIL** | **residual 1** — three live, unstruck, true travelling faults inside `dist/certonomous-demo.zip`, the archive the criterion names **by name**. Verified by opening the container at HEAD. Residual 6 independently |

**Two of the five were not entitled. Three were — but not to *that verdict*: see §7.**

---

## 0. INDEPENDENCE — established from the dispatch record, and worth exactly what §0 says

**Git cannot establish it.** Every commit on this box carries one identity,
`Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`, auto-configured from username and
hostname; there is no `user.name` set. The author field separates no two agents here.

**The session container cannot establish it.** This session has been open since 2026-08-04, before
every commit at issue.

**`scripts/check_rung_attribution.py` is NOT cited here and must not be cited by anyone.** Per
**D173** it returns `VERDICT: AUTHOR` for every pairing because it names a **session**, not an
agent. A grade defended by it is undefended. It is not run in this pass.

**What does establish it: the per-agent dispatch record.** My own record is
`~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/agent-ad1da5054d70fe96f.meta.json`,
whose content is `{"agentType":"general-purpose","description":"Measure PASS WITH RESIDUALS
entitlement","toolUseId":"toolu_01QN6iZNpv6AZSHQhFUDy2Ae","spawnDepth":1}` and whose creation
timestamp, read with `ls --time-style=full-iso`, is **2026-08-16 00:47:09.339024368 +0000**. That
is the earliest moment at which this agent existed on this machine. My first executed command
(`date -u`) ran at **00:47:12Z**, three seconds later.

**Every artifact I grade predates that record.** Committer timestamps, read with
`git log -1 --format=%cI` per commit and not from any prior document:

| what I grade | commit | committed (UTC) | margin before my first record |
|---|---|---|---|
| the V6/V10 regrade (V6 = PASS WITH RESIDUALS) | `60073572` | 2026-08-15T19:34:11Z | **5 h 12 m** |
| the V5/V8 grade (V8 = PASS WITH RESIDUALS) | `2a686b0a` | 2026-08-15T20:07:27Z | **4 h 39 m** |
| the V12/V13/V14 grade (V12, V13 = PASS WITH RESIDUALS) | `9c2734f8` | 2026-08-15T21:00:12Z | **3 h 46 m** |
| the V5/V14 regrade (V14 = PASS WITH RESIDUALS) | `6d95f812` | 2026-08-16T00:20:34Z | **26 m** |
| V12's residual repair | `6dbb3be6` | 2026-08-15T21:34:43Z | **3 h 12 m** |
| the consolidation | `04144e7c` / `43eac3f2` | 00:43:36Z / 00:44:34Z | **3 m 33 s / ~~2 h 35 s~~ 2 m 35 s** *(unit corrected 2026-08-16: `43eac3f2` at 00:44:34Z against the dispatch record opening at 00:47:09.339Z is **155 s = 2 m 35 s**; `2 h 35 s` would be 7,235 s. Typographic, but it sits on the row that establishes ordering, and the corrected value tightens the margin rather than loosening it.)* |
| **the chief ruling that dispatched me** | `20966952` | **00:46:33Z** | **36 s** |

The tightest margin is 36 seconds and it is the ruling that created this task — the correct
ordering, and the reason it is printed rather than rounded away. **No sequence of events makes
this agent an author of any of them.** I have written to none of the graded surfaces; the three
files this pass writes are named in the header.

> **THE LIMIT, and it must travel with the claim. NO READER OF THIS REPOSITORY CAN RE-DERIVE THE
> PARAGRAPH ABOVE.** The `subagents/` directory is **untracked and per-machine**: it is not in
> `git ls-files`, not in the ignored arm, not in any clone, not in any archive, and not in this
> document. An external reviewer must take §0 on trust or reject every rung graded under it, and
> there is no third option. This is docket **D130**. What I have is a machine-local record
> consistent with independence, not a portable proof of it.

**Guard output is reported here as a fact about the guard, never as evidence about text.** No
verdict below rests on any guard's silence. Where a guard is mentioned it is because a residual is
*about* the guard.

**The PDF arm.** I rendered no PDF, so I grade no PDF claim. `\sout{}` is strike-and-keep, so a
withdrawn figure sits in a correctly-repaired document's text layer exactly as it sits in a stale
one. Where a PDF matters to a verdict — V14's residual 6 — I grade *the fact that the arm is
unmeasured*, which is a fact about the sweep and not about any PDF's contents.

---

## 1. THE PREMISE, RE-VERIFIED: NO ROUND HAS EVER DECLARED ITSELF BELIEF-NEUTRAL

The ruling's fact was re-executed rather than inherited, because if any round had declared itself
neutral the whole question changes.

**Method.** `/usr/bin/grep -ain -E "R-VALUE|belief.neutral|belief neutral"` over every V15 and V16
round document at HEAD, plus `git log -1 --format=%B` over the three V16 rounds that produced no
document, plus a tracked sweep with `git grep -a` for any *positive* neutrality declaration.

| rung | round | document | neutrality language found | self-declared neutral? |
|---|---|---|---|---|
| V15 | 1 | `LADDER_V_V15_LADDER_TEXT_CLAIMS.md` | **none — zero hits** | no declaration |
| V15 | 2 | `LADDER_V_V15_ROUND2.md` | **none — zero hits** | no declaration |
| V15 | 4 | `LADDER_V_V15_ROUND4.md` | **none — zero hits** | no declaration |
| V15 | 5 | `V15_ROUND5_NUMBER_RECONCILIATION.md` | none | silent |
| V15 | 6 | `LADDER_V_V15_ROUND6.md:297-298` | R-VALUE named **as a rule defect**, not as a verdict | no declaration |
| V15 | 7 | `LADDER_V_V15_ROUND7.md:709` | *"Is this round BELIEF-NEUTRAL? **No.**"* | **NOT neutral** |
| V15 | 8 | `LADDER_V_V15_ROUND8.md:514` | *"**VERDICT: this round is NOT belief-neutral.**"* | **NOT neutral** |
| V16 | 1–4 | `V16_GRADE.md` | **none — zero hits**; predate the rule | no declaration |
| V16 | 5 | `V16_GRADE_ROUND5.md:137` | *"the R-VALUE counter does not reach two"* | **NOT neutral** |
| V16 | 6 | `V16_GRADE_ROUND6.md:168-169` | *"did **not** return only belief-neutral findings"* | **NOT neutral** |
| V16 | 7 | `V16_GRADE_ROUND7.md:216-241` | *"This grade is not clean, so it does not supply the second of the two"* | **NOT neutral** |
| V16 | 8 | **no document** — `5e4a0cc5` only | commit message: **0** hits for `R-VALUE` or `neutral` | none possible |
| V16 | 9 | **no document** — `067caac0` only | commit message: **0** hits | none possible |
| V16 | 10 | **no document** — `0c7b968d` only | commit message: **0** hits | none possible |
| V16 | 11 | `LADDER_V_V16_ROUND11.md:3-4` | *"the round is NOT belief-neutral … count stays at **zero**"* | **NOT neutral** |

**CONFIRMED, and the confirmation is stronger than the ruling's version of it.** No round in this
ladder's record has ever declared itself belief-neutral. The consecutive-neutral count is **zero on
both rungs and has never been anything else.** R-VALUE has never been within one round of closing
anything, so **R-VALUE cannot be the ground on which any of the five rungs closed.** A tracked sweep
for any positive neutrality declaration returns three lines, all of which are the *statement that
the count is zero*.

> **ONE CORRECTION TO THE RULING'S OWN FACE, in the D141 shape the ruling keeps indicting.**
> `LADDER_V_TRIPLE_VERIFICATION.md:577-579` states *"V15 rounds 1, 2, 4, 6, 7, 8 each self-declare
> NOT neutral."* **Measured: rounds 1, 2 and 4 contain no occurrence of `R-VALUE`, `belief-neutral`
> or any neutrality verdict at all.** Their `# NO.` answers the *termination rule's fixed-point*
> question — *"is the ladder at the fixed point?"* — which is a different question with a different
> subject. Round 6 names R-VALUE only to file a defect **in the rule**, not to score itself.
> **Three rounds self-declare NOT neutral on V15, not six.** The ruling's conclusion is unaffected
> and in fact strengthened: *more* rounds are silent than it said, so *fewer* rounds have ever
> addressed neutrality at all. Filed as **D232**.

---

## 2. RUNG V6 — **ENTITLED**

### The closing condition, quoted as written

> **V6.** Re-run the §4 adversarial audit against the ROUND-5 entry specifically — the existing
> audit predates QCR; **every finding gets a round-5 verdict, and QCR gets its own compliance line**
> (used at solve time only? touched no test data? stated in the description?).

`LADDER_V_TRIPLE_VERIFICATION.md:305-307`. Two determinate clauses: **(i)** every §4 finding
carries a round-5 verdict; **(ii)** a QCR compliance line answering three named questions. The
deliverable is the currency block at `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:` ~~`296-334`~~ **`296-335`**
*(range corrected 2026-08-16: the block's QCR compliance table carries four rows, `:332`, `:333`, `:334`
and `:335`, and `:335` — "Stated in the description?" — is the last compliance row. `296-334` cut off
the row answering the question the clause exists to ask.)*

### The three residuals, re-derived by my own execution and not read

I re-extracted the eleven rows from the `| § | the finding as written |` header at both trees,
sha256 per row, `__pycache__` purged first:

| measure | grade of record says | **I measure** |
|---|---|---|
| rows at `472f9f92` / at HEAD | 11 / 11 | **11 / 11** |
| rows byte-identical HEAD vs `472f9f92` | 9 | **9** — the two differing are `**4.7**` and `**4.8**` |
| `(line of '### 4.8 ') − (line of the '\| **4.8** \|' row)` | 256 | **577 − 321 = 256** |
| live occurrences of *"212 lines below"* | 1 | **1** |
| live occurrences of *"Ten of the eleven"* | 1 | **1** |

Both V6-R1 and V6-R2 are **live and real at HEAD**. Neither has been repaired.

### Placement

- **V6-R1** (*"Ten of the eleven are byte-identical … the eleventh being §4.7"* → nine, §4.7 **and**
  §4.8) and **V6-R3** (the headline conclusion right in principle, wrong in count) both sit in the
  block's **preamble narration**, which is neither a finding's verdict nor the compliance line. The
  comparison is against `472f9f92` — **the block's own earlier version**, not the pre-QCR audit — so
  the count measures how many rows *this repair changed*, which is internal bookkeeping. The
  preamble says so itself: *"Byte-identity is not the finding, though."* **OUTSIDE both clauses.**
- **V6-R2** (*"212 lines below in this same file"* → 256) sits inside the **evidence column** of the
  §4.8 verdict row. The verdict itself — `FALSIFIED 2026-08-11` — is **correct**: I confirmed §4.8's
  heading reads `~~VERIFIED~~ **FALSIFIED 2026-08-11**` at HEAD. The locator is wrong by 44 lines to
  a uniquely-headed section in the same file. A wrong pointer beside a correct verdict does not make
  the verdict absent or wrong. **OUTSIDE clause (i).**
- Clause (ii) is untouched by all three: the compliance line is present with four answers, the
  rung's three plus the zero-fitted-parameters question.

### The ambiguity, stated and graded both ways

**Is "gets a round-5 verdict" a verdict clause or a whole-row accuracy clause?**

- **Verdict reading.** The row must carry a round-5 verdict and that verdict must be true. Met on
  all eleven. R1/R2/R3 outside → **ENTITLED**.
- **Whole-row reading.** Every byte of every row must be true. Then R2 is inside → **FAIL**.

**The verdict reading governs, and the lab's own precedent is why.** V6's recorded FAIL at
`377d6afb` was on row §4.8 asserting *"§4.8 HOLDS"* and *"needs a network read this pass did not
perform"* — a **substantively wrong verdict, inverted against the world**. It was not failed on a
citation. Under the whole-row reading V6's criterion becomes unbounded: every anchor, hash and line
number in eleven dense rows would gate a rung whose sentence says *"every finding gets a round-5
verdict."* That is a criterion no execution can reliably satisfy, and this lab has already ruled
that such a criterion tells you nothing about the corpus.

**V6: ENTITLED.** The residuals are real, unrepaired, and outside. **What would flip it:** exhibit
any §4.x section whose heading verdict disagrees with its currency-block row, or show that a
falsehood in a row's evidence column is a failure of clause (i). Neither is available on the
measurement.

---

## 3. RUNG V8 — **ENTITLED**, with the wide reading named

### The closing condition, quoted as written, including its three protocol edits

> **V8. Claims-language audit of the cover email + description document**: every quantitative
> sentence maps to a named artifact; the banned-claims list enforced — no novelty claim on gated
> correction (§7.4), no *"comfortable"* AR_14 lead (0.00003), no best-on-board counts that lean on
> organizer-baseline rows (§4.7), no *"official rank"* language anywhere **(local scoring stated
> plainly)**, soft-adaptive-leakage
> disclosure present in the lab's own words (§4.3). **A claims table: sentence → artifact →
> verdict.**

**Quotation repaired 2026-08-16.** The parenthetical **(local scoring stated plainly)** was missing
from this blockquote, dropped with no ellipsis under a heading that promises the condition *"quoted
as written"*. It is restored above rather than marked with an ellipsis, because the heading claims
completeness and an ellipsis would only make the omission legible instead of removing it. The clause
is load-bearing for this section's own argument: it is the half of the "no official rank" ban that
says what the lab **may** state, and V8's entitlement turns on the distinction. Verified against
`LADDER_V_TRIPLE_VERIFICATION.md:315` at `73588fb7`, this document's own frame.

`:311-317`, plus three chief protocol edits at `:318-354` which extend the rung to **any rank
claim, internal or external** (P(rank 1) + interval + not-decided pairs), add the prohibition that
**no surface may state the figure without the interval**, and add that **the figure may never
appear without its interval and its board**.

So the criterion reaches **two named artifacts** for the claims audit, and **any surface** for rank
claims and for the P(rank 1) figure. It reaches nothing else.

### Re-derived rather than read

`spreads.overall_equivalent_S_bound` read by walking the JSON = `0.002419121853891026`.
`0.002419121853891026 / 0.001365 = 1.7722504424110082` → **177%**; and the old figure is accounted
for rather than denied: `/ 0.0028863 = 0.8381` → the four-entry board's margin over Reissmann.
**G1's reversal is real and I reproduce it independently.**

**V8's own falsifier, executed by me:** *find a surviving live, unstruck, undated "covers 84%" in
the cover email or the description document.* `DESCRIPTION_DOCUMENT.md` carries three `84%`
occurrences, all inside strikes or inside the sentence denying it (`:244` *"It does not cover 84%
of the margin"*). The draft carries ~~seven~~ **eight occurrences on seven lines** *(corrected 2026-08-16: `:967` carries
**two**; the seven lines are `:666`, `:743`, `:775`, `:967`, `:993`, `:1132`, `:1135`)*; `:743`, `:775`, `:967`, `:993`, `:1132`, `:1135` are all
inside `~~…~~` strike-and-keep or are the corrections themselves — I read `:955-1005` to confirm
§5.3 item 9's `84%` sits between a `~~` opener at `:965` and its closer at `:968`. **The only live
unstruck `84%` in the corpus is `:666`, which is V8-R2. The falsifier does not fire.**

### Placement

- **V8-R1** — the false certification *"its thirty body lines are byte-identical … every row of the
  ten-row defect table"* at `:613-614`. Sits in **§5's kept, dated 2026-08-10 banner preamble** — a
  record *of an audit of* §5, not §5 itself. Not the cover email, not the description document, not
  a rank claim, not the figure. **OUTSIDE.**
- **V8-R2** — the unstruck `84%` at `:666`. Same banner; the row is a *finding about* §5.2, not
  §5.2. And `84%` is the **seed-bound-to-margin ratio**, not P(rank 1): the amendments govern *"the
  figure"* and *"any rank claim"*, and this is neither. **OUTSIDE.**
- **V8-R3** — *no instrument enforces the triple*, and `check_derived_figures.py`'s own control
  `NEG-4` asserts `fired=False` by design. **V8's criterion requires no instrument at any point.**
  It asks for an audit and a claims table. **OUTSIDE.**
- **D85** is carried beside V8 as a standing row, not as one of the three; it concerns the absence
  of an instrument defending a *correct* ordinal in `DESCRIPTION_DOCUMENT.md`. Same reasoning as R3:
  durability is not a clause of this criterion. **OUTSIDE.**

### The ambiguity, stated and graded both ways

The grade of record declared it itself: *"A grader who reads V8's criterion as covering the whole
draft should read this verdict as FAIL on F4."*

- **Narrow (as written): "the cover email + description document."** All three residuals outside →
  **ENTITLED**.
- **Wide: the whole of `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`.** R1 and R2 inside → **FAIL**.

**The narrow reading governs, and it is not the convenient choice — it is the pre-registered one.**
The rung text has named two artifacts since 2026-08-10; the wide reading is unstated and arrives
later. The chief's own V5 ruling rejects a reading that arrives without being pre-registered, and
that the movement here is *outward* rather than inward does not make it less a movement.

**I tested the consistency objection rather than assuming it away.** G1's three clearing sites are
all inside the draft (§5.2, §5.3 item 9, §5.4), which looks like the wide reading in use. It is
not: **§5.4 *is* the cover email**; **§5.2 *is* "a claims table: sentence → artifact → verdict"**,
which is clause (3) of the criterion verbatim; and §5.3 is the description document's mandatory
disclosure specification, which the draft's own §5.1 item 3 defines as such. The banner at
`:609-680` is a *dated record of an audit of* those sections. **The line is coherent: the artifacts
are in, the audit record about them is out.**

**V8: ENTITLED.** **What would flip it:** a chief ruling that V8's artifact list is the draft rather
than the two documents it names. That is one sentence and it would make this FAIL on R1.

---

## 4. RUNG V12 — **NOT ENTITLED. The honest verdict is FAIL.**

### The closing condition, quoted as written

> **V12. The cold agent writes the skeptic's report**: the three weakest points of the entry as an
> outside reviewer would state them, **each with the record's best answer beside it**. **This
> becomes Sanaa's briefing** for any follow-up questions from the steward.

`:371-372`. Two clauses: **(i)** three weakest points, each with **the record's best answer** beside
it; **(ii)** the product **becomes** Sanaa's briefing to the steward.

The grade of record recorded the criterion's ambiguity honestly and in its own words: *"The
criterion as written contains **no accuracy clause and no currency clause.**"* It then wrote *"I
grade against the criterion as written PLUS the derived currency standard"* — and then declined to
block on that standard, on the ground that *"the rung's criterion asks for the three weakest points
and they are there and correct."* **That is the retreat from Reading B to Reading A between the
scope paragraph and the verdict paragraph, and it is where the entitlement is lost.**

### Placement — and the criterion decides this without needing the derived standard

- **R1.** `LADDER_V_PASS3_COLD_2026-08-11.md`, the answer block under weakest point **W2**, carried
  the rung's one actionable recommendation: *"put the number in the external text. 'Rank 1 on the
  point estimate; **P(rank 1) ≈ 0.67** by a case-level bootstrap over eight cases'…"* — **unstruck**
  — while a bullet **34 lines above in the same answer** reads *"~~P(rank 1) = 0.674~~ Struck
  2026-08-15: four-entry board. **Now 50.2%**."* Seventeen points, in the direction that flatters
  us, in the one sentence of the rung that proposes text for a surface that leaves the lab.
- **R2.** The answer under weakest point **W3**: *"the supplied baseline beats **all four published
  entries** (… a **best published 0.0760**)."* The record holds **six** entries and the second value
  is **Yang's 0.0748**, not Reissmann's 0.0760.
- **R3.** Adjacent bullets in W2's answer state one bound two ways — the JSON to eighteen digits
  (177%) and the rounded script constant `SEED_BOUND_ON_OVERALL = 0.0024`. The conclusion is
  unaffected, so this one is a derivation defect and I do not rest the verdict on it.

**R1 and R2 sit INSIDE clause (i), and the deciding words are the criterion's own: *"the record's
BEST answer."*** That phrase does not require the answer to be true of the world — the grade is
right that there is no accuracy clause. It requires the answer to be **the best answer the record
supports**. For both R1 and R2 a better answer was already present *in the same document*: 50.2%
with its 0–97% interval sits 34 lines above R1, and *"beats all six"* is what the record supports
against R2's *"all four."* **An answer that is demonstrably worse than one the record already holds
is not the record's best answer.** So the residuals are inside the criterion **even on the literal
reading with no accuracy clause imported**, and they are inside a second time on the derived
currency standard the grade said it was adopting.

**R1 is independently inside clause (ii).** The grade's own sentence is *"R1 must close before this
document is read as a briefing."* The criterion says the product **becomes** the briefing. **A
product that must not yet be read as the briefing has not met a criterion that says it becomes
one.**

### The verdict

**V12: NOT ENTITLED. The honest verdict at `9c2734f8` is FAIL, on R1, and independently on R2.**
This is the falsifier shape the chief named: the residual list was doing the work the criterion was
supposed to do. The rung's product is the instrument, the instrument handed the steward a weaker
version of the true case, and *"three weakest points are there"* was allowed to stand for *"each
with the record's best answer beside it."*

> **WHAT THIS DOES NOT SAY.** All three residuals were **repaired at `6dbb3be6`, 34 minutes after
> the grade** (21:34:43Z against 21:00:12Z) — I read the repairs at `:555-566` and `:650`, where
> *"all four published entries"* is now struck. **That repair is ungraded by a non-author.** A fresh
> non-author grade against HEAD could well return PASS, and should be dispatched. What is settled
> here is the entitlement of the verdict **as issued and as carried**, which is what D227 asks. A
> repair landing after a grade does not retroactively entitle the grade.

---

## 5. RUNG V13 — **ENTITLED**

### The closing condition, quoted as written

> **V13. Ladder report in negative-verdict-review format**: every rung PASS/FAIL with evidence
> links, the claims table, the skeptic's report, and a single consolidated list of anything that
> changed during verification. **No rung self-graded; the three pass-owners sign their own
> sections.**

`:893-895`. Four required contents plus two conditions on the report's own authorship. **Like V12,
it contains no accuracy clause and no currency clause** — but unlike V12 it contains **no quality
word either**: nothing in it is the counterpart of *"the record's best."*

### Placement, with the decisive distinction

**Three of the four residuals are decay that happened AFTER the artifact was signed, by other
agents' commits.** A closing condition cannot be failed by the world moving after delivery; that
would make the criterion unsatisfiable, and this lab has already ruled that an unsatisfiable
criterion is not a high standard.

- **V13-a** — §8's drift figure `51/56` is `50/56` at HEAD, `certificate.py` a sixth stale member.
  The grade's own words: *"was true when written."* A drift count is none of the four required
  contents. **OUTSIDE.**
- **V13-b** — the corrected V15 ledger row names rounds 5–7 and **round 8 exists** (`05354615`,
  2026-08-15T20:18:50Z, **three minutes after the grader's own record opened**). Two grounds for
  outside: the row lives in `LADDER_V_TRIPLE_VERIFICATION.md`, not in V13's deliverable; and the
  ladder's termination rule states in terms that *"what does NOT reopen the ladder: corrections to
  the ladder's own REPORTS … **and this document**."* **OUTSIDE.**
- **V13-d** — `LADDER_V_TRIPLE_VERIFICATION.md:1193-1194` and the ledger's V13 row assert §8 is
  *"not edited"* and *"both slots are still empty as slots"*. I confirmed both sentences live at
  HEAD, and confirmed `9e466dd4` added a `DISCHARGED 2026-08-15` block to §8 at 02:07:33Z, after
  `29beb7cf` wrote the claim at 01:01:21Z. **Same two grounds. OUTSIDE.**
- **V13-c** — the one arguably wrong at delivery. `LADDER_V_V13_CLOSEOUT.md:94` reads *"NO —
  SELF-GRADED at the last step"* in the **"Independently confirmed by"** column while `:597` of the
  same file says V10 *"moves off CLOSED-BY-ITS-AUTHOR."* Three reasons it is outside: **(a)** it is
  not a PASS/FAIL cell — the V10 row's verdict cell reads the full `PASS → FAIL → FAIL → closed`
  chain and is correct; **(b)** the two are not in fact flatly contradictory, because `:597`
  qualifies itself in the same sentence — *"but only as a statement about `2b251689`"* — and then
  reports `51/56` and **FAIL** at its own HEAD; **(c)** the §2 row ends *"See §8 PENDING-2"*, an
  in-cell pointer to the section that updates it. **OUTSIDE**, and I agree with the grade that this
  is *"the D141 shape with a seatbelt"* — a convention rather than an instrument, which is a real
  observation and not a rung failure.

### The ambiguity, stated and graded both ways

- **Literal (as written).** Four contents present, two authorship conditions met → all four
  residuals outside → **ENTITLED**.
- **Purposive (the report must be a coherent statement of the ladder's state at all times).**
  V13-c is inside → **FAIL**.

**The literal reading governs, and here the reason is not merely that it is written that way.** The
purposive reading makes V13 a rung that **cannot ever close**: a close-out is a signed snapshot of a
ladder that moves several times an hour, so under a standing-accuracy requirement its criterion is
falsified by the next commit no matter what it says. Three of these four residuals are exactly that
mechanism operating. **A rung whose stated failure mode is guaranteed to occur is not a gate.**

**V13: ENTITLED — and I closed the one clause no grade of record had executed rather than leaving it
open.** Every clause checked by me directly:

| clause | measured at HEAD |
|---|---|
| every rung PASS/FAIL with evidence links | **§2**, ~~`:82-96`~~ **`:85-99`** — fifteen rows, each with Verdict, Owner, Evidence and confirmation columns *(range corrected 2026-08-16: the **count of fifteen was right**; `:82-96` spans only **twelve** rows, V1 through V12, dropping V13, V14 and V15. The table's rows run `:85` (V1) to `:99` (V15), under the header at `:83-84`.)* |
| the claims table | **§3**, `:124` |
| the skeptic's report | **§4**, `:158` |
| a single consolidated list of anything that changed | **§5**, `:297` |
| **no rung self-graded; the three pass-owners sign their own sections** | **§9**, `:616-641` — **MET, and this is the clause nobody had executed.** Pass 1, Pass 2, Pass 3 and Pass 4 signatures are each **quoted from that owner's own report at the commit carrying it** (`5a21b4fd`, `92562841`, `636c0b91`, `d358fd96`/`6afe15e3`/`c1ebfb4f`/`171b1241`), and §9 opens *"V13 collects the pass owners' signatures; it does not sign for them, and it grades no rung"* |

**What would flip it:** show that any of the four required contents is absent, or that a signature
in §9 is not the owner's own words at the commit it cites. Neither is available on the measurement.

---

## 6. RUNG V14 — **NOT ENTITLED. The honest verdict is FAIL.**

### The closing condition, quoted as written

> **V14 (A14). Mechanical surface discovery, not a maintained list.** The cross-surface sweep is
> replaced by a **repo-wide search for every score literal** … **plus every prior-art sentence
> fragment**, **across tracked files, built artifacts, and shipping archives including `dist/`**.
> The searcher **must prove its own reach first** (gzip, ignore-files, untracked trees, archives
> that must be opened to be read) **and state what its frame structurally cannot contain**. **A
> surface nobody listed is exactly where a stale claim survives**, so the rung fails if its method
> is a list rather than a search.

`:382-389`, plus the chief's denominator ruling at `:391-430`: **reach is repo-wide, gating is
travelling-scoped, and the remainder is reported with its count.**

### The grade of record read this as a method test only. That is the reading the entitlement turns on.

Its verdict paragraph opens: *"The rung's criterion is a **method** test … failing 'if its method is
a list rather than a search.'"* But the criterion's **first** clause is a **coverage** requirement —
a search *across tracked files, built artifacts, and shipping archives **including `dist/`***. The
method clause is an *additional* failure mode introduced by *"so the rung fails if…"*. **Reading
"the rung fails if X" as "the rung fails only if X" is what converts a coverage criterion into a
method criterion**, and it is the single move that makes residual 1 look external.

### Placement, measured by opening the container myself

I read `dist/certonomous-demo.zip` (read-only; `dist/` was not written). sha256
`34b8feed8301d91a8aa36d506326c89d74cf4b8ac42c2eb19a2948af1c00ba33`, **90 file members**, 13
directory entries. Member `certonomous-demo/site/closure.html` carries **`date_time (2026, 8, 12,
16, 31, 22)`**, 525 lines. Its three faults, read out of the bytes:

| member line | text, as it ships | state at the tracked source |
|---|---|---|
| `:341` | *"the tie is gone, the case falls to **3rd of 5**"* | struck; the three surviving `3rd of 5` are all inside `<s>` tombstones |
| `:502` | *"holds no official rank — **rank 1 of 5** is our local"* | `demo-output/website/closure.html:590` — **`<s>`struck 2026-08-15** |
| `:503` | *"scoring at a pinned benchmark commit, with a seed-uncertainty bound **comparable to its margin**"* | `:591` — struck in the same tombstone; the bound is **177%** of the margin, which I re-derived |

`of 7` appears **once** in the shipped member and **eleven times** in the tracked source. **The
three faults are live, unstruck, and true.**

- **Residual 1 — INSIDE, and it is the paradigm case the rung was created for.** `dist/` is named
  in the criterion **by name**. The chief's own ruling makes **gating travelling-scoped**, and this
  archive is *the only file that leaves this box* (D118). A true fault on the travelling surface is
  precisely what V14 gates on under the ruling the grade adopted. And the ladder's §"PASS 4"
  preamble says in terms that V14 exists because the first full run found *"a tracked shipping
  archive carrying round-3 numbers with zero caveats"* that was *"nobody's rung."* **Excusing a
  stale tracked shipping archive makes V14 structurally incapable of failing on the finding that
  created it** — a gate whose stated failure mode cannot occur, which is W-2 the right way round.
- **The mitigation offered does not reach the criterion.** *"The source is right, the artifact is
  stale, the rebuild is the owner's"* answers **who repairs it**. It does not answer **whether the
  surface is in the rung's declared scope**, and the criterion names it. This is the chief's own
  V5 ruling applied where it was earned: ***"left to its owner" is a routing rule, not a frame
  exclusion*** — *"it answers who edits, never whether a surface is in frame."* **That is now the
  fourth time this week ownership has stood where a frame was needed.**
- **Residual 6 — INSIDE, independently.** *"The PDF arm is unmeasured."* The criterion requires the
  search to run across tracked files and to *"state what its frame **structurally** cannot
  contain."* ~~Sixty-eight tracked PDFs~~ **Fifty tracked PDFs** hold this corpus's largest single
  concentration of withdrawn claims. *(Count corrected 2026-08-16, and the word doing the work is
  "tracked": this bullet argues under V14's own **"across tracked files"** clause, so the supporting
  count must be the tracked one. **50 PDFs are tracked; 68 is the whole-tree count.** The 18 extra are
  all named `certificate.pdf` — 4 under `dist/certonomous-demo/mission-output/*` and 14 under
  `mission-output/*` — and every one is untracked and therefore invisible to `git ls-tree`,
  `git grep` and `git ls-files` alike. Measured by set difference between `git ls-tree -r --name-only`
  and a whole-tree `find`, not by subtraction.)* A PDF is **not** something the frame structurally cannot contain — it renders to PNG; the
  grade's own words are that rendering *"was outside the time this grade had."* **An arm skipped for
  time and disclosed as a blind spot is a gap, not a structural limit**, and the criterion's escape
  hatch is for limits, not for gaps.
- **Residuals 3 and 5 — INSIDE, more weakly.** *"The searcher must prove its own reach first"* is a
  named clause. Residual 3 is the **sole reason `:342` is unreached**; residual 5 is a **confirmed
  execution gap** on `0.0029` at `closure.html:411`, a tracked travelling surface. Both are reach
  failures on real claims, disclosed rather than closed. I do not rest the verdict on them.
- **Residuals 2 and 4 — OUTSIDE.** Residual 2 was *correctly* not widened (widening a context window
  to make a control pass changes what counts as evidence) and is disclosed with its three distances.
  Residual 4 has **no instance in this corpus**.

### The verdict

**V14: NOT ENTITLED. The honest verdict at `6d95f812` is FAIL, on residual 1, and independently on
residual 6.**

**The grade pre-agreed with this, and I am taking the concession it offered rather than arguing past
it.** Its own words: *"a grader who reads V14's gate as 'no travelling fault may stand, whatever its
cause' should read this rung as **FAIL until the rebuild** — I have named the residual precisely so
that disagreement is a one-step check and not a matter of opinion."* I read the gate that way,
because the criterion names `dist/`. And its falsifier — *"rebuild and re-run; if the travelling arm
does not go to zero … this PASS is wrong"* — **has not been executed at all**, so the PASS rests on
an untested counterfactual about an artifact whose three live faults I have just read out of the
bytes.

**What would flip it:** rebuild `dist/certonomous-demo.zip` from the current tracked site, re-run
`check_rank_claim_values`, and show the travelling arm at zero with no tracked travelling surface
faulting; and render the 68 PDFs and grade the arm. **The rebuild is the owner's and is one command
(`scripts/build_laptop_bundle.py`), and it clears V5-5 in the same act.** V14 should be re-graded
the moment it lands.

---

## 7. THE RULING ITSELF, GRADED

`LADDER_V_TRIPLE_VERIFICATION.md:571-605`, chief, `20966952`.

### What survives, and it is most of it

1. **The premise is true and I re-derived it independently** (§1). R-VALUE's condition has never
   been met on any rung, ever.
2. **The two-route analysis is sound.** R-CONVERGE *does* independently provide that a finding
   outside a rung's declared scope is **filed, not appended**. So a rung whose declared closing
   condition is met, with its surviving findings all out of scope, is a real pass with real
   filings. That is not a loophole; it is what R-CONVERGE says.
3. **The test is decidable per rung, and I decided all five without needing anything the ruling did
   not supply.** Two came back NOT ENTITLED. A test that returns a mixed answer under adversarial
   application is a working test.
4. **It refused the cost-free answer and said why** — *"a rule that can be satisfied by relabelling
   is not a rule"* — and it marked the five provisional rather than promoting them on its own
   say-so.
5. **Its stated falsifier is NOT triggered.** The falsifier is *"a rung whose residuals sit inside
   its closing condition and whose PASS WITH RESIDUALS **I have let stand**."* The chief let none of
   them stand: it declared all five provisional, barred them from being read as send-gate passes,
   and dispatched this measurement. V12 and V14 are **the answer the test was built to produce**,
   not a refutation of it.

### What does not survive: **the R-CONVERGE route does not produce PASS WITH RESIDUALS. It produces PASS.**

**This is the ruling's one real defect and it is a naming defect with teeth.**

R-VALUE is the **only** place in this lab where `PASS WITH RESIDUALS` is defined, and it defines it
as the terminal state of a two-round neutrality count, in which *"the residuals become docket
items."* R-CONVERGE's own words for an out-of-scope finding are that it *"is filed as a separate
docket item, **not appended to the live rung**."*

**So on the R-CONVERGE route the out-of-scope findings are not the rung's residuals at all — they
are docket rows belonging to other rungs or to nobody's rung.** The rung's own correct verdict is
**plain PASS**, with a list of filings beside it. Borrowing R-VALUE's label for that state **is the
relabelling the ruling forbids, running in the other direction**: it takes a verdict R-VALUE has
never once authorised and attaches it to a state R-CONVERGE reaches by a different mechanism, so
that the two become indistinguishable on the ledger's face.

**And it is not cosmetic.** **D38(1)** already records `PASS WITH RESIDUALS` as a **sixth gate
verdict** against `VERIFICATION_CHARTER.md:95` — *"The verdict vocabulary is fixed"* — and
**invisible by construction to §16's negative-verdict-review sweep**. A verdict no sweep can see is
a verdict nothing re-examines. The R-CONVERGE route, by adopting R-VALUE's label, launders a plain
PASS into a category the charter does not have and the sweep cannot find. That is how five rungs
came to carry a verdict whose only written entry condition has been met zero times, without anyone
noticing for a day.

### The ruling as it should read, and what it costs

| rung | ruling's provisional verdict | **entitled verdict** |
|---|---|---|
| V6 | PASS WITH RESIDUALS | **PASS**, with V6-R1/R2/R3 filed as docket rows |
| V8 | PASS WITH RESIDUALS | **PASS**, with V8-R1/R2/R3 filed as docket rows |
| V12 | PASS WITH RESIDUALS | **FAIL** |
| V13 | PASS WITH RESIDUALS | **PASS**, with V13-a/b/c/d filed as docket rows |
| V14 | PASS WITH RESIDUALS | **FAIL** |

**Under this, no rung in Ladder V carries `PASS WITH RESIDUALS`, and R-VALUE's two-round bar is
restored as the only door to it — which is exactly the outcome the ruling said it was protecting.**
The ruling reached for the right protection and then left the label unguarded.

**So: is `PASS WITH RESIDUALS` exclusively an R-VALUE verdict? YES — the label is. The *state* it
names is reachable two ways, and the R-CONVERGE way is called PASS.** That is the amendment I am
proposing, and it costs the ruling nothing it was trying to keep: three rungs still pass, two still
fail, and every residual still gets written down. What changes is that the ledger stops carrying a
verdict the charter does not contain.

**FALSIFIER FOR §7.** Produce a reading on which R-CONVERGE's *"filed as a separate docket item, not
appended to the live rung"* is compatible with those same findings being **the rung's own named
residuals**, or show that `PASS WITH RESIDUALS` is defined anywhere outside `:561-565`. Either
would restore the ruling's label. I swept the tracked corpus for a second definition and found
none.

---

## 8. LEDGER ROWS — WHAT I REPAIRED, AND WHAT I DELIBERATELY DID NOT

**Six rows repaired**, all of them rungs whose state I measured myself in this pass, each
strike-and-kept with `~~…~~`, dated 2026-08-16 and anchored. **`<s>` was not used**: this document's
target carries one dangling `<s>` opener against zero closers, and a balanced `<s>`/`</s>` pair
added into that file can pair with the dangling opener and blank the text between. Markdown `~~`
is used throughout and the file's `~~` count was even before and after.

| D226 row | rung | repaired? | why |
|---|---|---|---|
| **b** | **V6** | **YES** — FAIL → **PASS** (residuals filed) | settled in §2; written once, after the settlement |
| **c** | **V8** | **YES** — FAIL → **PASS** (residuals filed) | settled in §3 |
| **d** | **V9** | **YES** — confirmation column corrected | **re-measured by my own execution**, not inherited: both discriminating fragments of the struck prior-art sentence return **0** hits over all 90 members, whitespace-normalised, with the positive control `Closure` firing in **7**. Wrong for five days |
| **f** | **V12** | **YES** — DELIVERED → **FAIL** | settled in §4 |
| **g** | **V13** | **YES** — DELIVERED → **PASS** (residuals filed) | settled in §5 |
| **h** | **V14** | **YES** — PASS as executed → **FAIL** | settled in §6 |
| **a** | V5 | **NO** | I did not grade V5. Its verdict of record is FAIL in three independent grades, and a fourth may be in flight — **five agents work concurrently.** A row I write for a rung I did not measure is D141 at zero commits' remove, which is the defect D226 exists to record |
| **e** | V10 | **NO** | **D229 is live and contested**: the verdict of record is a FAIL of a tree that no longer exists, and the correct row depends on a grade nobody has issued. Writing either verdict now would settle by ledger what must be settled by execution |
| **i** | V15 | **NO** | round 9 is owed and may land at any moment; same concurrency ground |
| **j** | V16 | **NO** | round 12 is owed; same ground |
| **k** | GREEN REQUIRES table | **NO** — **out of my licence.** My dispatch permits `LADDER_V_TRIPLE_VERIFICATION.md`'s **ledger rows only**, and that table is not a ledger row. **It is now stale in two further places by this pass's own settlement** — V8 reads *"OPEN — and it has now failed three times"* against PASS, and V14 reads OPEN against FAIL. Named here rather than edited, and filed as **D234** |
| **l** | V5 ruling face | **NO** | already **D228**, and a ruling's face is the chief's alone |

**Four rows left, each with its reason, and none of them left because it was hard.** The rule I
applied is the one D226 itself states: a ledger row must be written by someone who measured the
thing it summarises.

---

## 9. WHAT THIS PASS COULD NOT MEASURE

- **My own independence, portably** (§0). Machine-local and untracked; **D130**.
- **The PDF arm.** No PDF rendered, so no PDF claim graded. Where PDFs decide something — V14's
  residual 6 — I graded *the fact that the arm is unmeasured*, which needs no PDF read.
- **The 955 PNGs, and rendered text.** No text search reaches either.
- **Whether V12's `6dbb3be6` repair is correct**, only that it is present — I read the repaired
  lines. Grading it is a fresh non-author's job.
- **Whether the §9 signatures are genuinely their owners'**, only that each is quoted at a commit
  that exists and carries that report. Signature authenticity is not establishable on this box for
  the same reason independence is not (§0) — one identity, `Ubuntu <ubuntu@…>`, on every commit.
- **The run tree.** No solver logs or run archives were read; nothing in this grade needed them.

---

## 10. DOCKET ROWS FILED

**D232** — the D227 ruling's own count of V15's self-declaring rounds is wrong in the same D141
shape it indicts; six named, three measured.
**D233** — the entitlement measurement: V12 and V14 were not entitled to PASS WITH RESIDUALS, and
`PASS WITH RESIDUALS` is a label R-CONVERGE cannot issue.
**D234** — the GREEN REQUIRES table is now stale in two further rows against this settlement, and it
sits outside every recent pass's editing licence.

> **ID ALLOCATION NOTE, recorded because it happened to this pass and the brief warned about it.**
> I checked the docket's highest ID and found **D229**, then drafted three rows as D230–D232. **The
> write aborted on its own assertion**: between the check and the write, another of the five
> concurrent agents had taken **D230 and D231**. The rows were re-allocated to **D232–D234** and the
> freeness of each was **asserted again inside the second write**, which is why nothing was
> overwritten and no ID was reused. **Checking before writing is not enough at this concurrency; the
> assertion has to be inside the write, and this is a worked example of why.**
>
> Two further guards fired in the same write and both were worth having. **(1)** A column-count
> assertion caught a draft row whose evidence cell quoted a `grep -E` alternation — the literal `|`
> characters would have silently split one cell into three and shifted every column of that row.
> **(2)** No `<s>` was used anywhere: `docs/DOCKET.md` carries **nine** dangling `<s>` openers
> against **three** closers, so a balanced pair added here can pair with a dangling opener and blank
> an unrelated row. Counts re-checked after the write and unchanged at 9 and 3.

*This document graded five rungs and one ruling. It is now an author of the text above and of the
six ledger rows, so under R-ISOLATE it may not measure any of them again.*
