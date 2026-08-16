# Lab state for the owner — 2026-08-16

**Written for one sitting. Every state claim below carries the commit that established it. Nothing
here was graded by this document; where a verdict was contested, the holder and the record of the
contest are named.**

**The headline, without softening: the ladder did NOT close, and it is not close to closing.** Ten
of sixteen rungs stood at PASS. Four stood at FAIL. One rung's PASS was withdrawn as not entitled and
a re-grade was in flight. One rung did not close its round. **R-VALUE — the only rule by which the
two open rungs can ever close — stood at zero, and that zero is a FLOOR rather than a fact: every
probe that ever established it planted the tokens it searched for, so it proves what no round SAID,
not what no round WAS (s2).**

**This document was re-verified against HEAD `22e32c03` and four rungs had moved since it first
landed.** Every figure in it was re-derived at that tree rather than carried from the record that
first stated it, under a rule this lab wrote after one of my own unchecked figures reached this page
(**D287**). Figures that could not be reproduced were removed rather than repeated.

*No solver was launched. No scoring call was made; the ledger stood at 6. Nothing was sent,
uploaded, posted, registered or emailed; the submission remained PARKED. `deb91557` was not moved.*

---

## 1. The ladder, rung by rung, verified against HEAD `22e32c03`

*Re-verified 2026-08-16T18:4xZ. Every figure below was re-derived at this tree rather than carried
from the record that first stated it (D287). Four rungs moved since this document first landed.*

Verdicts are the ones the records carry. **The withdrawn labels "PASS WITH RESIDUALS" and "PASS WITH
EXCEPTIONS" are not used as verdicts anywhere below**; both were withdrawn (`7c44cbe2`, and for V5
the chief ruling on `a8c25b47`) because neither appears in the charters' fixed vocabulary.

| Rung | State | Established by |
|---|---|---|
| **V1** clean-environment re-score | **PASS** (twice) | Pass 1, 2026-08-10 |
| **V2** pre-registration chain | **PASS** | Pass 1, 2026-08-10 |
| **V3** leakage assertions | **PASS** — one leg failed on re-run and was fixed | Pass 1, 2026-08-10 |
| **V4** duct traced end to end | **PASS** | Pass 1, 2026-08-10 |
| **V5** QCR provenance | **FAIL** | chief ruling on `a8c25b47`, 2026-08-16 |
| **V6** compliance audit vs round 5 | **PASS** (plain) | `7c44cbe2`, from the grade at `60073572` |
| **V7** known defects killed | **PASS** — three defects, not the two known | Pass 2, 2026-08-10 |
| **V8** claims table | **PASS** (plain) | `7c44cbe2`, from the grade at `2a686b0a` |
| **V9** prior-art completeness | **PASS** — **re-graded and the contest is resolved** | re-graded by a non-author at `27295b9b`, 2026-08-16 |
| **V10** cross-surface number sweep | **PASS WITHDRAWN as not entitled; a re-grade was in flight** | reopened at `f7170481`; the PASS it withdrew was `c2cd83bf` |
| **V11** cold reproduction | **PASS** — bit-for-bit from the package alone | Pass 3, 2026-08-10 |
| **V12** skeptic's report | **FAIL** — repairs in flight | `7c44cbe2` (not entitled) and re-graded FAIL at `b4596cb4` |
| **V13** close-out | **PASS** (plain), four findings filed | `7c44cbe2`, from the grade at `9c2734f8` |
| **V14** mechanical surface discovery | **FAIL** — blocked on the owner | `7c44cbe2` (not entitled), on residual 1 of the regrade at `6d95f812` |
| **V15** ladder-written text | **FAIL** — **round 9 landed and is NOT belief-neutral**; round 10 running | round 9 at `bbf81c91` |
| **V16** rank-claim guard reach | **DID NOT CLOSE** — round 12; round 13 running | `ae09cb3c` |

### Five things a reader must carry out of that table

1. **V10's ledger row still recorded a PASS at HEAD.** `LADDER_V_TRIPLE_VERIFICATION.md:1000` read
   *"…→ `PASS`, closed 2026-08-16"* while the reopen at `f7170481` withdrew it. **The ledger and the
   reopen disagreed, and the ledger was the stale side.** The reopen also recorded that the blocker
   itself was repaired, so V10 was **not** left failing on a live surface — what was owed was a
   fresh grade by a non-author.
2. **V14's own regrade document did not say FAIL.** `6d95f812` recorded a passing label with six
   residuals; the FAIL came from the separate entitlement measurement adopted at `7c44cbe2`, on
   residual 1 — three live, true, stale claims inside the shipping archive the criterion names by
   name. Both facts are needed or the record reads as a contradiction.
3. **V15's round 9 has since landed** (`bbf81c91`) and is **NOT belief-neutral** — it found things,
   so it contributes nothing toward closing V15. Round 10 was running.
4. **V9's PASS was contested on method, the contest was resolved, and the rung SURVIVED it.** The
   original clearing evidence was *"both discriminating fragments return ZERO hits, with the positive
   control `Closure` firing in 7 members."* `Closure` is unrelated to the claim: its firing showed
   the sweep could open the files, not that it could recognise the claim in any wording but two exact
   substrings. **Absence of two literals was measured; absence of a claim was concluded.** A
   non-author re-graded it at `27295b9b` using recognition controls and returned **PASS** — the
   struck sentence is genuinely absent from all 90 archive members. **The method objection was right
   and the verdict was right anyway**, which are two different things and both are recorded.
   **And the objection was not academic: the re-grade found a live paraphrase the literals would have
   missed.** `demo-output/website/agenda/docket.json:1594` reads *"controlling where a data-driven
   correction **may act**"* where the certified fragment reads *"is allowed to act"* — re-derived
   here at HEAD, and the certified literal appears **nowhere** in that file. Filed as **D286**,
   outside V9's scope, deliberately unrepaired.
5. **Ten rungs at PASS is not "nearly closed."** The termination rule requires all sixteen, plus a
   re-run introducing zero new failures, plus that zero measured by a non-author. Clause 1 alone was
   unmet by six rungs.

---

## 2. R-VALUE stood at ZERO **as a floor**, and it is the only route open to V15 and V16

The rule, as written (`LADDER_V_TRIPLE_VERIFICATION.md:551-554`, 2026-08-11):

> **R-VALUE.** Each grade round records what it found and what it cost. When **two consecutive
> rounds return only findings that would not change an external reader's belief**, the rung closes
> as PASS WITH RESIDUALS, and the residuals become docket items.

**The count stood at zero on both rungs — and it is a FLOOR, not a population count.** That
distinction was established by V15 round 9 (`bbf81c91`, finding F4) and it corrects how this number
has been reported, including by me:

> *"The lab's headline `R-VALUE = 0` is established only to the strength of a token search whose
> positive control plants the tokens it searches for. That proves REACHABILITY, not RECOGNITION."*

**The bound, stated so the claim can be checked rather than believed:** no round document contains
the tokens `R-VALUE`, `belief-neutral`, or any inflection of *neutral* used to declare a round
neutral. Round 9 widened the sweep from a phrase to the root word and **read and classified all 145
occurrences** in the tracked corpus at `fe54ec0a`, which **narrows the gap and does not close it**.
**A round that wrote "nothing here changes what an outside reader believes" would satisfy R-VALUE's
own wording and share no token with any probe ever run**, and no instrument in this lab would see
it. A recognition control was running at the time of writing.

**What is not in doubt:** every V15 round from 1 to 9 and every V16 round through 12 was recorded by
its own grader as *not* belief-neutral, in those words. Round 12 recorded five new material findings,
three of them new shapes (`ae09cb3c`); round 9 recorded four findings by its grader's own execution
and a floor of 27 (`bbf81c91`). **So the count is zero on the evidence available, and the honest form
of that sentence is "at most zero has been demonstrated", not "zero is the fact."**

**What it would take, stated plainly: two rounds in a row that find nothing an outside reader would
care about.** Not two rounds with small findings — two rounds whose findings would not move an
external reader's belief. **Since the rule was written on 2026-08-11, no round has been recorded as
belief-neutral, and every round since has been graded by someone who found something.** There is no
other route by which V15 or V16 closes; the rungs cannot be argued shut.

*(The label R-VALUE awards was itself withdrawn at `7c44cbe2` as outside the charters' vocabulary.
That is a naming question and does not change the gate.)*

---

## 3. The owner's decision queue

Each item is stated so it can be acted on without re-deriving anything. **None requires research.**

### 3.1 The `dist/` rebuild — blocks a rung, and it is NOT gated behind anything
`dist/certonomous-demo.zip` was built **2026-08-14T21:16:50Z** and ships **three true, live, stale
claims** (`3rd of 5`, `rank 1 of 5`, and a seed-bound comparison), verified by opening the container
(`6d95f812` §4.10). **It is V14's residual 1 and therefore the thing V14 fails on.** A rebuild also
picks up a QCR-attribution repair under `dist/` that only a rebuild can reach — a V5 leg-3 site
(`6d95f812:98-101`). **The repair is a rebuild and the rebuild is yours; no agent performed it.** **It is not gated:**
every record that prescribes it (D233, D224) calls for *"a plain re-run with no hand-editing"* and
names **no** precondition.

**A second decision is open and is also yours:** whether shipping Act 1 with a withdrawn-certificate
notice, rather than a sealed page, is acceptable **on camera** — the console still replays the
recording's `certificate.ready`, so it announces a seal whose link now reads *"no certificate for
this mission"* (D177; the control-room surface is D136). *(Corrected 2026-08-16, after this document
first landed: it stated that this decision "comes first" and had to be taken before the rebuild.
**No record sequences it that way.** Every record that prescribes the rebuild — D233, D224 — calls
for a plain re-run with no hand-editing. The two decisions are both yours and neither is recorded as
gating the other.)*

### 3.2 The `latex/` PDF rebuild
`demo-output/website/latex/closure_challenge_report.pdf` — **40 pages**, tracked, `CreationDate`
**2026-08-11T03:26:36Z** — was rendered to image and read visually for the first time tonight (D243)
and **carried live, unstruck four-entry-board claims on its own front page while its LaTeX source
sat repaired beside it.** It is **outside every sweep run tonight** and, in the chief's words at
`3285a530`, *"must not be read as cleared by the 33-to-10 shipping result."* **The rebuild is yours.**

### 3.3 Ratify the recovered closure outcomes into `docket.json`
Nine agenda items had no outcome sentence; all nine now have one (`b0f9ec7c`), and **five were
recovered rather than authored** — the agent that did the work had written the sentence and only the
docket had lost it. **D219 reserves the ratification to you.** The sequence was established by
execution and is two steps:

1. **`refresh_docket()` — one call — clears every LOST id.** Verified read-only: each is returned by
   `read_inbox()` with no id and no objective collision, so none is stranded. **The batch stood at
   eight**, the eighth being the W1-only arm dismissed under a chief ruling tonight.
2. **`set_status(<id>, <status>, outcome=…)` for the two UNABSORBED only** —
   `r2-closure-coefficient-uncertainty` and `hlpw6-testcase1-coarse-grid-entry` — whose evidence
   lives in an artifact no merge can reach.

*(A defect in the checker's own printed remedy, which had told operators to use `set_status` for the
LOST class — a silent no-op there — was found and repaired by another agent at `6a593518`.)*

### 3.4 The HLPW6 workshop — a standing constraint, not a capability gap
Creating an account, requesting a participant identifier and opening a merge request are **three
external interactions**, and the item's own charter forbids all three to agents, verbatim: *"do not
contact the workshop organisers … do not request a participant identifier, do not open a merge
request … do not create any account. **Katie decides whether this lab approaches this workshop at
all.**"* **The item did what it was told**: it was charged *"Prepare, do not send"* and to return a
result plus an honest assessment, and its "cannot be sent" finding **is** that assessment.

**Approving the approach would not by itself make the entry sendable.** Twenty second-order
configurations were tried on a harder committee grid and **all twenty diverged inside 29 iterations**
(`6d72b13c`), and the mandatory eight-view deliverable needs a rendering pipeline the lab does not
have. Both are separate unsolved work. Independent of the decision, the work already produced a
reusable asset: `ugrid_to_foam.py`, validated to an exact boundary-face match on a 2.66M-cell grid.

### 3.5 May a non-owner append a dated additive addendum to another agent's signed report?
**A precedent was set by act and never ruled.** At `fe612d03` (2026-08-08) an agent amended another
agent's signed report additively and dated. **Two addenda were held PROVISIONAL pending a ruling** —
`campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md:213` and
`campaign/QCR_ACTIVITY_CHECK_2026-08-08.md:144`, both marked *"HELD PROVISIONAL, 2026-08-16, by chief
ruling on `a8c25b47`"* — and `LADDER_V_TRIPLE_VERIFICATION.md:245` records that **nothing is declared
closed on either.** This blocks V5 work; it is a governance question, not a measurement.

### 3.6 Board identification — the 29 come before the 210
Routed to you in the chief's order at `3285a530`:

* **First, 29 sites are governed by two rules that disagree** — a dated heading saying *judge by its
  own date* against a page frame warning binding *"every ordinal on this page"* to the live board,
  **both in force** — so those sites **have no determinate reading at all.** That is why they lead:
  they are not undecided pending a preference, they are currently unreadable.
* **Second, 210 sites (26% of the exemption surface)** where the nearest-heading, any-ancestor and
  document-H1 readings disagree. Costed and deliberately not decided.

**The ruling landed at `3285a530` (D255).** *Already ruled and applied, so not yours:* meta quotation is exempt as an identity (1,504 of 1,885
sites), leaving 381 governable assertions; and shipping-surface assertions now require a retrieval
timestamp (33 sites, applied at `dc9d9364`). **Accuracy repairs were never gated on any of this** —
only claims whose *sole* defect is an ambiguous board identifier were held.

### 3.7 W4's upstream addendum — a post, therefore yours
Filing means opening an issue against **`mdolab/dafoam`**. That is an external post, reserved to you
in writing in three places, one of which names filing the upstream report among the two most
dangerous acts an ignorant agent could take. **Filing readiness is a separate question from filing
permission**: the report's own readiness table carries two rows NOT DONE (a reproducer on a stock
upstream tutorial, and mechanism-to-a-line), so permission and readiness can be decided
independently and neither implies the other.

---

## 4. What the night bought, including what reflects badly

**104 commits were landed on 2026-08-16** (re-counted at HEAD `22e32c03`; it read 85 when this
document first landed, which is the rate the night ran at).

**Rungs moved — and three moved downward.** **V5, V12 and V14 had all read as passing and all now
read FAIL**: V5 by chief ruling, V12 and V14 because a measurement of whether they were *entitled* to
their label found they were not (`7c44cbe2`). **A fourth movement was a retraction of something
already reported upward: V10 was closed PASS at `c2cd83bf` and that PASS was withdrawn as not
entitled at `f7170481` the same night.** V16 ran round 12 and did not close. **No rung moved from
FAIL to PASS tonight.**

**Live false claims found and repaired.** Two shipping pages stated the declined baseline beat *"all
four published entries"* against a board that had carried six since 2026-08-11 (`6263a13b`). A page
named the wrong duct leader and a wall table badged two lost cases gold (`fe54ec0a`). Three further
stale characterisations were repaired at `f7170481`. **One live false artifact was found and NOT
repaired** — the 40-page PDF of §3.2, because its repair is yours.

**Two rulings landed, and one of them shrank by two thirds when it was measured.** The V5 leg-3
granularity ruling issued **per-file on frozen records** (`bcad2bbc`) after its own measurement
refuted three of its four premises: of **118** claim-bearing sites in scope, **82 (69.5%)** already
attribute Spalart (2000) elsewhere in the same file and flip to passing **with no work done**, so
only **36 sites across 22 files** get an addendum written. *A ruling that read as closing 118 while
closing 36* was corrected before it issued rather than after. The board-identification ruling landed
the same night (`3285a530`).

**The repository restructure was attempted and reverted, and the reorganization is deferred by you
until the ladder work is checked and complete.** Verified at HEAD: every key path resolves where it
was, and the tracked count stood at **20,748**.

**Instruments repaired.** The commit-declaration gate, which had been fail-false for exactly the
files this lab's own protocol creates (`b917f56d`); the coverage checker's printed remedy
(`6a593518`); and the file-set of two standing instruments, which had never opened the `.tex` arm
(`530fcf15`).

**The method finding worth keeping.** A blind sweep can only *miss*; it cannot manufacture a defect.
**So a FAIL is never endangered by a blind instrument — every claim of ABSENCE is.** Its corollary:
**a positive control proves either reachability or recognition, and these are not the same thing.**
Both get written up identically, and only one earns the sentence *"the control fired, so the zero is
a measurement."* That distinction is what reopened V10 and what put V9 and V7 under re-examination
(D277).

---

## 5. What is still unknown, named as unknown

* **Whether V9 and V7 survive re-examination.** Both were cleared by literal-string searches whose
  recogniser could not see a reworded claim. Non-authors were routed; no result existed at HEAD.
* **How much stale text remains outside every instrument's reach.** `git grep -a` reached **20,722 of
  20,748** tracked files at HEAD; `dist/` is untracked and reachable by no `git grep` route at all,
  and **49 of the 50 tracked PDFs had never been rendered and read**. *(Corrected 2026-08-16, after
  this document first landed: it read "67 tracked PDFs", inheriting an error from D243. `git ls-files
  '*.pdf'` returns **50** at HEAD and **50** at D243's own frame `5a0127d3`. The 68 in "68-PDF arm" is
  **50 tracked plus 18 gitignored**, never 68 tracked.)*
* **Whether the EIG ranking finding can ever be acted on.** Its statistics correlate against a
  per-item grade that exists in **no committed artifact**, so the headline figure cannot be
  recomputed by anyone. A chief ruling to implement it was **withdrawn** on that ground (D276). It is
  a finding about that study, not a task anyone is avoiding.
* **Whether independence can be demonstrated to an outside reader at all.** Every commit on this
  machine carries one identity; independence rests on untracked per-agent dispatch records that exist
  in no clone (D130). **Every "graded by a non-author" claim in this document is unverifiable from
  the repository**, and that limit is the honest state rather than a defect to be repaired by
  assertion.
* **The V15 round 9 result**, which was in flight and uncommitted at the time of writing.

---

*Compliance: no solver runs, no scoring calls, ledger at 6 and untouched. Nothing sent, uploaded,
posted, emailed, registered or created; no account made and no organiser, workshop or maintainer
contacted. `deb91557` was not moved. `docket.json` was not written. `dist/` was not opened.
`demo-output/website/latex/` was opened **read-only**, by `pdfinfo`, to re-derive the page count and
creation date in s3.2 rather than inherit them; nothing in it was written. No rung was graded or
re-graded here. No file on another agent's hold was edited.*
