# Probability of rank — a posterior over our score against the board

> # ⚠ THE INTERNAL-ONLY GATE ON THIS FIGURE IS WITHDRAWN — chief ruling, 2026-08-11
>
> *Recorded by Ladder V Pass 2 at the chief's direction. The header below, the
> propagation rule in the next section, and every "INTERNAL ONLY" marking in this
> document are **superseded on the question of who may see the number**. Nothing
> else in the document changes: the arithmetic, the caveats, the four-clause
> companion and the sweep token all stand exactly as written.*
>
> **What changed, and why the reversal is right.** Pass 3 (cold reproduction,
> `campaign/LADDER_V_PASS3_COLD_2026-08-11.md`) computed **0.674** from public
> data — the README's published board plus our own eight CSVs — in about a
> minute, with no access to this document. That is decisive, and it is decisive in
> the direction of publishing:
>
> - **A figure an outsider reproduces trivially is not protected by being
>   withheld.** The withholding buys nothing.
> - **It costs credibility.** A number that is obviously computable, obviously
>   computed, and conspicuously absent reads as concealed rather than careful —
>   and it reads that way to precisely the reader whose good opinion the whole
>   disclosure strategy is built to earn.
> - **It is the honest half of the rank claim.** Publishing "rank 1" while
>   withholding "and here is how little that survives resampling" inverts the
>   lab's own standard.
>
> **The figure now travels with the entry**, carrying its interval (an eight-case
> sample cannot pin it tighter than 2–100% at 95%) and its not-decided pairs
> (Reissmann, Wu & Zhang). **Every other banned-claims rule stands unchanged**, and
> so does the requirement that both wordings contain the literal string
> `not statistically decided`.
>
> **The one thing the reversal does not license:** the figure may not be stated
> without its interval. A bare "68%" is a worse claim than no figure at all,
> because 68% sounds settled and 2–100% is what the eight cases actually support.

**2026-08-10. ~~INTERNAL ONLY. This number never appears in any external claim.~~
SUPERSEDED 2026-08-11 — see the banner above. The figure is publishable, with its
interval and its not-decided pairs attached.**

> **On the face of this document, three times over.**
> 1. **INTERNAL.** This figure is for the house to reason with. It is not to be
>    published, quoted outside this lab, attached to any package, or cited in any
>    submission-facing document. Submissions are PARKED by standing instruction;
>    this item is not a submission action and does not prepare one.
> 2. **The scoring underneath it is LOCAL.** Our 0.056647 was produced by the
>    benchmark's own unmodified scorer on this box at benchmark commit
>    `deb91557`; nothing has ever been submitted, and if the steward's scoring
>    differs from ours, the steward's number is the number.
> 3. **No new scoring call was made for this document.** Zero. The lab's
>    scoring-call ledger stands at **6** and is unchanged. Every number below is
>    arithmetic over per-case scores that were already on disk.

### The propagation rule — ~~STANDING, confirmed by the chief 2026-08-10~~ AMENDED 2026-08-11

Inherit this rather than re-deciding it. When a ruling orders this figure
propagated to surfaces, some of which are public:

- **Internal surfaces carry the figure** — `P(rank 1) = 68%`, the 2–100% band,
  the leave-one-out numbers.
- ~~**Public surfaces — anything shipping in `dist/` — carry the qualitative
  clause only**, never the figure~~ **— WITHDRAWN 2026-08-11 (banner at the head
  of this document).** Public surfaces may now carry the figure, and the entry's
  own cover material must. What they may never carry is the figure *without* its
  interval. The qualitative clause is still required everywhere and is still the
  thing the sweep token lives in: the margin sits against a per-case spread five
  times larger, the standing is two cases wide, `AR_1` and `AR_3` are ties below
  published precision.
- **Both wordings contain the literal string `not statistically decided`**, which
  is the sweep token V10 greps for, so the mechanical sweep is unaffected by the
  split.
- **The principle, stated generally because it will recur:** *an order to
  propagate is never an order to violate the thing being propagated.* This
  document is internal by its own gate; publishing its figure in the act of
  obeying a propagation order would break that gate. Where the two conflict,
  carry the qualitative half and raise the conflict — do not execute blind and do
  not silently drop the surface.
- **A rank claim that omits P(rank 1) and the not-decided pairs fails Ladder V
  rung V8** (protocol strengthened 2026-08-10).
- **Do not add the sweep token to a surface where "rank 1" means Reissmann, a
  docket rank, or a cited paper's table.** Fourteen such false positives exist in
  the tree; tokening them would corrupt the very sweep the token exists to serve.
  §7 carries the audited surface list.

Item: `agenda/proposals/probability-of-rank-a-posterior-over-our-score-against-the-board.json`
(status `approved`, decision note "chief approval 2026-08-10"). Strategy §3, last
bullet. Zero solver core-min, zero scoring calls.

---

## 1. The headline

**P(rank 1) = 68%** — 67.6% over 400,000 case-level bootstrap resamples.

The interval that matters is **not** the Monte Carlo one. Stated in the order of
increasing honesty:

| interval | value | what it measures |
|---|---|---|
| Monte Carlo (Wilson, B = 400,000) | **67.5% – 67.8%** | only that the resampling ran long enough. Not an uncertainty about the world. |
| Leave-one-case-out (8 refits) | **38% – 91%** | how much of the 68% one case is carrying |
| Double bootstrap, 68% band | **26% – 94%** | what an 8-case sample can actually pin down |
| Double bootstrap, 95% band | **2% – 100%** | the same question, at the conventional level |

**The honest reading: the point estimate is 68%, and eight cases cannot resolve
it better than "somewhere between a coin flip and near-certain".** The 95% double
bootstrap spanning almost the whole unit interval is not a defect of the method;
it is the correct answer to "how well do eight numbers determine a probability of
rank", and it is the single most useful line in this document.

### Full rank distribution (400,000 resamples, full-precision scores)

| our rank | probability |
|---|---|
| **1** | **67.6%** |
| 2 | 18.6% |
| 3 | 12.8% |
| 4 | 0.86% |
| 5 | 0.19% |

Rank 3 at 12.8% against rank 4 at 0.86% is not noise: resamples that draw the two
Ret_360 ducts and `NASA_2DWMH` heavily put both Reissmann and Wu & Zhang above us
at once, and there is no cheap way to be 4th.

### Pairwise — P(our resampled mean beats theirs)

| opponent | published overall | our margin | P(we lead) | paired-difference *t* (n = 8) |
|---|---|---|---|---|
| Reissmann, Fang & Sandberg | 0.059525 | −0.002878 | **69.4%** | −0.495 |
| Wu & Zhang | 0.062412 | −0.005765 | **84.7%** | −0.953 |
| Liu, Wang, Zhao & Xiao | 0.073687 | −0.017040 | **98.7%** | — |
| Montoya, Oulghelou & Cinnella | 0.077863 | −0.021216 | **99.8%** | — |

---

## 2. Which comparisons are decided by case-selection luck, not by method quality

This is the part the item was filed for. Stated plainly, name by name.

**Decided by luck, not by method — Reissmann.** Our margin is 0.002878. The paired
per-case difference against Reissmann has mean −0.002878 and standard deviation
0.016436 across the eight cases, giving a standard error of 0.005811 and
**t = −0.495**. The dispersion is *five times* the margin. We beat Reissmann on
four cases and lose on four. A 69.4% probability of leading is what "we might well
be ahead" looks like when it is written down honestly, and it is **not** a
statement that our method is better than theirs. It is a statement that on this
particular set of eight cases we scored lower, and that a different eight cases
drawn from the same population would flip it about three times in ten.

**Also not decided — Wu & Zhang.** Margin 0.005765, **t = −0.953**, P(we lead)
84.7%. Larger and more comfortable than the Reissmann comparison, still short of
anything a statistician would call settled.

**Decided by method — Liu and Montoya.** 98.7% and 99.8%. We beat Liu on 7 of 8
cases and Montoya on 7 of 8. Those two comparisons survive case resampling and are
worth believing.

**Two per-case comparisons are below published precision and must never be quoted
as wins or losses at all:**

- `AR_1_Ret_360`: ours **0.045470** against Wu & Zhang's published **0.0455**. The
  gap is **0.00003** — smaller than the fourth decimal their number is published
  to. Called "2 of 5 nominally" in §0f; it is a coin-flip at the precision the
  board carries, and the bootstrap variant that honours published-precision ties
  moves P(rank 1) from 67.6% to 67.9% with a 0.6-point sliver where we are tied
  rather than sole first.
- `AR_3_Ret_360`: ours 0.039982 against their 0.0399 — we are **0.00008 worse**,
  the same order. Reported as "3 of 5"; it is a tie.

**The AR_14 margin the item names, scored.** Round 4 held `AR_14_Ret_180` at a
0.00003 margin over Reissmann. Round 5 gave it up (0.0324698 → 0.0353386, +0.0029),
which was pre-registered and accepted in writing. The record was right to call that
lead nominal: **a 0.00003 margin on one case moves the eight-case overall by
0.000004, which is 0.13% of the rank-1 margin.** Whether we held it or lost it was
never going to decide the standing. What decided the standing was the −0.0731
combined on the two Ret_360 ducts.

### The seed bound is comparable to the whole margin

The PH model behind `alpha_15_13929_4048`, `alpha_15_13929_2024` and `NASA_2DWMH`
was trained at one seed. The truth-free seed-spread bound on the overall is
**0.0024** against a **0.002878** rank-1 margin (`closure_challenge_stability_
physicality_audit.md` §1; the bound is not tightenable without a scoring call, and
no scoring call was made). Loading that bound adversely onto the three
seed-dependent cases and re-running the bootstrap:

| scenario | our overall | P(rank 1) | P(we lead Reissmann) |
|---|---|---|---|
| adverse seed (+0.0024) | 0.059047 | **52.0%** | 54.1% |
| as scored | 0.056647 | **67.6%** | 69.4% |
| favourable seed (−0.0024) | 0.054247 | **80.5%** | — |

**A seed draw the lab did not control moves P(rank 1) from 52% to 81%.** Put
beside the bootstrap's own 26–94% band, the correct internal sentence is: *we are
probably ahead, we cannot show that we are, and the two largest sources of doubt —
which eight cases, which seed — are both outside our method.*

---

## 3. Leave-one-case-out: what the standing rests on

Each row deletes one case and re-runs both the point ranking and a 7-case bootstrap.

| case deleted | point margin vs Reissmann | our point rank | P(rank 1) |
|---|---|---|---|
| `alpha_15_13929_2024` | **+0.001392** | **2** | **38.1%** |
| `alpha_15_13929_4048` | −0.001986 | 1 | 57.3% |
| `alpha_05_4071_4048` | −0.001222 | 1 | 54.6% |
| `alpha_05_4071_2024` | −0.002702 | 1 | 63.2% |
| `AR_14_Ret_180` | −0.003696 | 1 | 69.7% |
| `AR_3_Ret_360` | −0.004132 | 1 | 72.4% |
| `AR_1_Ret_360` | −0.004259 | 1 | 73.2% |
| `NASA_2DWMH` | −0.006428 | 1 | 91.1% |
| *(none — as scored)* | −0.002878 | 1 | 67.6% |

**One case carries the standing: `alpha_15_13929_2024`.** Delete it and we are rank
2 on the point score. Our 0.1011 there against Reissmann's 0.1339 is a −0.0328
lead, by far the largest single-case lead on the board, and it alone supplies
0.0041 of the 0.0029 overall margin — i.e. **more than the entire margin**. Every
other case, taken together, is a net negative against Reissmann.

**And one case is pure cost: `NASA_2DWMH`.** Delete our only last-place case and
P(rank 1) goes to 91%. That 0.0632 against Wu & Zhang's 0.0364 costs 0.0034 of
overall — more than the rank-1 margin, again.

This independently reproduces, by a different route, what the earlier error
decomposition found: **the standing is two cases wide.** The posterior is dominated
by `alpha_15_13929_2024` on the credit side and `NASA_2DWMH` on the debit side, and
outcome three of the proposal's pre-declared three is the one that fired.

---

## 4. Method, and what it does and does not assume

**Resampling unit: the case.** Draw 8 of the 8 official test cases with
replacement; recompute all five entrants' overall (unweighted mean of the 8 scaled
MAEs) on the *same* resampled index set; record our rank. B = 400,000, seed 20260810
(`numpy.random.default_rng`). The double bootstrap is 2,000 outer × 4,000 inner,
seed 31415.

**Inputs, all already on disk.** Ours at full precision from
`closure_challenge_round5_qcr.json` → `official_test_harness_result.
round5_per_case_full`; the other four transcribed from the benchmark README at
`deb91557` via `closure_eval/closure_eval_master_table.md` §A. Reproduction check
performed: the mean of each entrant's eight published 4-decimal per-case values
reproduces their published overall exactly (Reissmann 0.059525, Wu & Zhang
0.062412, Liu 0.073687, Montoya 0.077863), so the 4-decimal columns are the real
published values and not a rounding of something else.

**Three caveats, as the item's gate requires them, on the face of the document:**

1. **The scoring is local and nothing has been submitted.** Stated at the top.
2. **The cases are not exchangeable and the bootstrap assumes they are.** Four
   periodic-hill cases, three ducts and one wall-mounted hump are not eight draws
   from one population. The three ducts moved together under a single constitutive
   change (−0.0356/−0.0375/+0.0029 in round 5) and carry zero seed variance; the
   PH cases and NASA share one trained model and one seed. A bootstrap that draws
   `AR_1` three times is drawing one physical fact three times. The consequence is
   that the reported spread is if anything **too narrow**, not too wide: the
   effective number of independent cases is nearer 3 than 8.
3. **The other entrants' scores are fixed published values, so what is resampled
   is case selection, not their methods.** Their per-case numbers carry no error
   bars here and get none. This is a posterior over *which cases the benchmark
   chose*, not over *what four other groups would score if they ran again*.

**A fourth caveat the gate did not ask for.** P(rank 1) is a probability about a
resampling procedure, not a Bayesian posterior over a state of the world. Read it
as "how robust is the observed ordering to which cases were chosen", and nothing
more.

---

## 5. What the house should say internally, and what it must not say

**May be said internally:** *Our round-5 entry scores best on the board as scored
locally on these eight cases. Resampling the cases puts the probability that we
would still be first on a comparable set at roughly 68%, with an eight-case sample
unable to pin that tighter than a coin flip to near-certain. Against Reissmann
specifically the comparison is not decided; against Liu and Montoya it is. A single
seed draw moves the figure by nearly thirty points.*

**Must not be said, internally or otherwise:** that we are 68% likely to win the
benchmark. Three separate reasons, each sufficient: nothing has been submitted; the
steward has not scored us; and this is a case-resampling frequency, not a
probability about a leaderboard.

**Standing instruction unchanged.** Submissions remain PARKED. This document is not
evidence that a send is pending and is not to be cited in anything submission-facing.

---

## 7. The audited surface list — what V10 checks against

Propagation completed 2026-08-10 under chief rulings 1, 3 and 4. **Fifteen files
carry the sweep token**, and a single grep for `not statistically decided` across
the repository returns exactly these fifteen and nothing else. Thirteen are
propagation targets; the remaining two are `docs/PRODUCT_LIST.md` (chief-owned,
done at `a57d8d3b`) and this document itself.

**The token is lower-case `not statistically decided` in every file.** One surface
initially carried "are NOT statistically decided" and was silently invisible to the
sweep until normalised — worth knowing, because a case variant is exactly how this
check would quietly under-report.

| # | surface | wording | why |
|---|---|---|---|
| 1 | `CLOSURE_CHALLENGE_STATUS.md` §0f | internal | the standings record |
| 2 | `ACTIVE_RESEARCH.md` | internal | the research board |
| 3 | `closure.html` (banner + §5) | **external** | ships in `dist/` |
| 4 | `benchmarks.html` | **external** | ships in `dist/` |
| 5 | `benchmarks.json` | **external** | ships in `dist/` |
| 6 | `wall/wall.json` | **external** | ships in `dist/` |
| 7 | `sdk/scripts/build_benchmarks.py` | **external** | generator of 5 and 6; edited in the same commit per its own comment |
| 8 | `campaign/LADDER_V_TRIPLE_VERIFICATION.md` | internal | the V8 criterion itself |
| 9 | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §10 | **external** | a draft of an outward artifact — no figure, so nobody must remember to strip one on the day it is sent |
| 10 | `agenda/CHALLENGE_LANDSCAPE.md` | internal | asserts the entry of record |
| 11 | `campaign/CHALLENGE_SLATE_2026-08.md` | internal | asserts round-5 rank 1 |
| 12 | `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` §4 | internal | **the rule document** — the companion is written in as clause (c) |
| 13 | `closure_challenge_round5_qcr.json` | internal | the machine record; appended as a sibling key, the dated block and all CSV hashes untouched |
| 14 | `docs/PRODUCT_LIST.md` | internal | **chief-owned**, done at `a57d8d3b`; not edited here |
| 15 | `campaign/PROBABILITY_OF_RANK_2026-08-10.md` | internal | this document — the source of the figure |
| 16 | `latex/closure_challenge_report.tex` | internal | **added after this list was written** — see the note below |

**Grep count V10 checks against: 16 CLAIM-BEARING SURFACES** *(was 15;
re-measured by Ladder V Pass 2, 2026-08-11)* **— plus a growing count of
verification records, which is why a bare integer is the wrong check.**

> **Correction, 2026-08-11 — the count moved the same day this list was written,
> and the list did not.** §7 above records the `.tex` under *"Routed elsewhere"*:
> it asserted rank 1 at ten sites and the chief routed it to its Opus owner
> rather than tokening it here. **That owner then did the work**, at `15f2921a`
> (2026-08-10T16:23:32Z, *"Every rank-1 claim gains its probability and its
> not-decided pairs"*) — **21 minutes after** `a57d8d3b`, the commit this
> document cites as the last propagation. So the file moved from *routed* to
> *compliant* between the writing of this list and the next sweep, and the
> stated count of 15 was already one short when it was written down.
>
> **A grep for `not statistically decided` across the repository now returns 16
> files, and every one of the 16 is a surface that should carry it** — the 15
> tabled above plus the `.tex`. Verified 2026-08-11: no case-variant misses (a
> case-insensitive grep returns the same 16), and no new false positive was
> tokened. The `.tex` names both undecided pairs, carries both paired *t*
> statistics, and marks the 68% figure *"internal figure"* at its own §-level.
>
> **Standing note for whoever runs V10 next, because this will recur:** a routed
> surface is not an excluded surface — it is a surface whose *owner* differs.
> When it comes back compliant the count changes, so **re-measure the count, do
> not read it off this table.** The table is the audit of *which* surfaces are
> right; the grep is the authority on *how many*.
>
> **And the bare integer is now the wrong check outright — retire it.** During
> this very sweep the raw grep went 16 → 17 while the sweep was running, because
> a concurrently-executing Ladder V pass wrote its own report
> (`campaign/LADDER_V_PASS3_COLD_2026-08-11.md`) and the token appears in it
> legitimately, exactly as it appears in row 8's protocol document. Pass 2's own
> report takes it to 18. **A verification record that quotes the rule is not a
> surface making a rank claim**, and a check of the form *"the count must equal
> N"* will now fail every time the ladder does its job. **The check V10 should
> run is the invariant, not the integer:**
>
> 1. **No claim-bearing surface makes a rank claim without the token** — the 16
>    rows above, each re-read, not counted.
> 2. **No file carries the token where "rank 1" does not mean our standing** —
>    the 14 audited false positives below stay untokened.
> 3. ~~**No external surface carries the 68% figure**~~ **— REPLACED by the
>    2026-08-11 reversal.** The new invariant is **no surface carries the figure
>    without its interval.** *(Measurement taken before the reversal, kept as the
>    record of the state the gate was in: the six externals — rows 3–7, 9 —
>    carried the token and zero instances of the figure; the ten internals carried
>    both. Under the new rule those six are now* under*-disclosed rather than
>    correctly gated, and bringing them up is a follow-on item, not a defect of
>    this sweep.)*
>
> All three held on 2026-08-11 **as the rules stood when they were measured**.
> Records that merely *quote* the rule — pass reports, this document, row 8 — are
> outside the count by construction.
>
> **One open risk, named and not fixed here (not this pass's file to edit).** The
> `.tex` is described in its own commit message as *"the closure line written
> down for an outsider"*, and it prints `P(rank 1) = 68%` at twelve sites. It does
> not ship in `dist/` (checked: `dist/certonomous-demo/` contains
> `site/{closure,benchmarks}.html` and `wall/` only, no LaTeX), so it is not a
> public surface today and no gate is breached today. But an internal-only figure
> living twelve times over in a document written to be handed to an outsider is
> one decision away from a breach, and the decision would not feel like one.
> Raised to the chief and to the `.tex`'s owner rather than edited.

### Deliberately NOT tokened — 14 false positives

A naive grep for "rank 1" returns 14 further files where the phrase does **not**
mean our standing. Tokening them would corrupt the sweep V10 depends on:

- **"rank 1" means Reissmann:** `CLOSURE_EVALUATION_PROTOCOL.md` (their cited
  papers), `CLOSURE_METHODS_COMPARISON.md`, `CLOSURE_RANK1_CAMPAIGN.md` (a
  round-4-era plan in which *we were behind*), `campaign/W3_QCR_DUCT_FALSIFIER.md`
  ("our deficit to rank 1"), `dafoam/ladder-b/B1_reproduction_plans.md`,
  `campaign/R5_PREREGISTRATION.md`, `campaign/R5_RULE_FREEZE.md`.
- **"rank 1" means a docket or slate rank:** `agenda/BLOCKERS.md`,
  `campaign/R4_PREREGISTRATION.md`, `campaign/reports/MORNING_REPORT_2026-08-04.md`,
  `campaign/reports/MORNING_REPORT_2026-08-07.md`,
  `campaign/F8_MRF_HAND2001_GATE.md`,
  `agenda/proposals/f8-mrf-forces-against-hand-2001.json`.
- **"rank 1" means a cited paper's table or a gradient rank:**
  `campaign/W2_SPARTA_REGRESSION.md` (Table 2),
  `campaign/W2_SPARTA_REGRESSION_PREREGISTRATION.md` (M(3) on CBFS),
  `dafoam/VERIFICATION_cbfs_unblock_supervisor_sweep.md` (rank 10 of |g|).

### Deliberately NOT edited — frozen and self-referential records

- **Frozen, anti-hindsight:** `campaign/R5_PREREGISTRATION.md` and
  `campaign/R5_RULE_FREEZE.md` are the artifacts Ladder V rung V2 **passed** on —
  the criterion at `0bade54a` predating every solve is the whole proof. Editing
  either after the fact would falsify the chain that makes the entry defensible.
  Same for `campaign/R4_PREREGISTRATION.md` and
  `campaign/W2_SPARTA_REGRESSION_PREREGISTRATION.md`.
- **Dated snapshots that record what a surface said on their date:** the two
  morning reports, `campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` (a rung's own
  evidence of the surfaces as they stood), and
  `CLOSURE_FAMILY_SUPERVISION_REVIEW_2026-08-07.md`.
- **Self-referential:** `agenda/docket.json` and
  `agenda/proposals/w3-qcr-forward-on-the-ducts-is-the-rank-1-route.json` record
  historically what the round-5 call produced; and
  `agenda/proposals/probability-of-rank-a-posterior-over-our-score-against-the-board.json`
  is the item that produced this document.
- **Routed elsewhere:** `latex/closure_challenge_report.tex` asserts rank 1 at ten
  sites and belongs to its Opus owner; the chief has routed it.

## 6. Provenance

- Per-case scores, ours: `demo-output/website/closure_challenge_round5_qcr.json`
- Per-case scores, board: `demo-output/website/closure_eval/closure_eval_master_table.md` §A,
  transcribed from the benchmark README at `deb91557`
- Standings and the AR_14 / seed qualifiers: `demo-output/website/CLOSURE_CHALLENGE_STATUS.md` §0f
- Seed bound: `closure_challenge_stability_physicality_audit.md` §1
- Scoring calls made by this document: **0**. Ledger unchanged at 6.
- Solver core-min: **0**.
