# Probability of rank — a posterior over our score against the board

**2026-08-10. INTERNAL ONLY. This number never appears in any external claim.**

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

## 6. Provenance

- Per-case scores, ours: `demo-output/website/closure_challenge_round5_qcr.json`
- Per-case scores, board: `demo-output/website/closure_eval/closure_eval_master_table.md` §A,
  transcribed from the benchmark README at `deb91557`
- Standings and the AR_14 / seed qualifiers: `demo-output/website/CLOSURE_CHALLENGE_STATUS.md` §0f
- Seed bound: `closure_challenge_stability_physicality_audit.md` §1
- Scoring calls made by this document: **0**. Ledger unchanged at 6.
- Solver core-min: **0**.
