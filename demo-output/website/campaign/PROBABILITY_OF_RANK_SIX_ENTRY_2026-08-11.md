# P(rank 1) recomputed against the six-entry board

**2026-08-11, at repo commit `f6b4eec0`. Zero solver core-min. Zero scoring calls —
the ledger stands at 6 and is unchanged.** Every number below is arithmetic over
per-case scores already on disk plus a leaderboard fetched today.

> ## The one sentence
>
> **The rank-1 claim survives on the number, and two other claims do not: P(rank 1)
> falls from 68% to 50%, and — found while recomputing, not looked for — the
> best-on-board count falls from 4 of 8 to 2 of 8, both survivors being the
> organisers' own declined baseline field, so the count belonging to our own model
> is now ZERO of eight.**
>
> The probability is the item this document was opened for. **The best-on-board
> collapse is the more consequential half**, because it is a claim the entry makes
> on public pages and in its cover material, and it is now false rather than
> merely stale. It is derived in §3a.

---

## 1. The frame, stated before any figure

Per W-5, this document's numbers are useless without their frame, and the whole
reason it exists is that the previous computation's frame silently expired.

| what | value |
|---|---|
| **board snapshot** | the **live** GitHub leaderboard, **six** entries |
| **fetched** | 2026-08-11 **23:33 UTC**, two independent routes: `raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md` (sha256 `1f124a8857a6b611832478879fc22ff353ee3308434b966849d4f29946d85c5b`) and the rendered project page. Both agree. Corroborates `campaign/BOARD_MOVED_2026-08-11.md` (`9cb2a20a`), fetched earlier the same day. |
| **NOT the frozen pin** | `/home/ubuntu/closure-challenge-benchmark` stays at `deb9155` (2026-05-04). **It scores; it does not rank.** No pin was moved. Rung V1 is untouched. |
| **cases** | **8**, the eight official test cases. The board's eight case columns are **unchanged** between the four-entry and six-entry snapshots, so all scores remain like-for-like. |
| **entries compared** | **6** (was 4) |
| **our score** | **0.056647191704213645**, read from `demo-output/website/closure_challenge_round5_qcr.json` → `official_test_harness_result.round5_per_case_full`, **not** inherited from any summary. That record was written by the sixth scoring call at commit **`07a7fe9e`** (2026-08-07), benchmark dataset `deb91557`, eval package `1c4e22c8`, verdict ACCEPT against the pre-registered criterion `overall < 0.065438`. The eight per-case values sum to that overall exactly. |
| **resamples** | **B = 400,000**, seed 20260810, `numpy.random.default_rng`; double bootstrap 2,000 outer × 4,000 inner, seed 31415 |
| **method** | identical to `campaign/PROBABILITY_OF_RANK_2026-08-10.md` §4 — see §6, where it is proved identical rather than asserted |

**The live board as fetched, with our number placed in it:**

| Rank | Authors | Overall (published) | mean of its 8 published per-case values |
|---|---|---|---|
| 1 | Yang | 0.0580 | 0.058013 |
| 2 | Reissmann, Fang, and Sandberg | 0.0595 | 0.059525 |
| 3 | Wu and Zhang | 0.0624 | 0.062412 |
| 4 | Tian, Buchanan, Hickel, Dwight | 0.0641 | 0.064138 |
| 5 | Liu, Wang, Zhao, and Xiao | 0.0737 | 0.073687 |
| 6 | Montoya, Oulghelou, and Cinnella | 0.0779 | 0.077863 |
| *(unsubmitted)* | **ours, round 5** | **0.056647** | 0.056647191704 |

**Reproduction check, executed, and it passes for all six including both new
rows:** the unweighted mean of each entrant's eight published four-decimal
per-case values reproduces its published overall to four decimals. So the case
columns are the real published values and not a rounding of something else — the
same check the four-entry document ran, now extended to Yang and to Tian.

---

## 2. The headline, and the interval that ships with it

**P(rank 1) = 50%** — **50.2%** (200,609 of 400,000).

**It never travels without this:**

| interval | value | what it measures |
|---|---|---|
| Monte Carlo (Wilson, B = 400,000) | 50.0% – 50.3% | only that the resampling ran long enough. Not an uncertainty about the world. |
| Leave-one-case-out (8 refits) | **31.7% – 78.5%** | how much of the 50% any one case is carrying |
| Double bootstrap, 68% band | **12% – 81%** | what an eight-case sample can actually pin down |
| **Double bootstrap, 95% band** | **0% – 97%** | the same question at the conventional level (precisely 0.25% – 96.90%) |

**The honest reading: the point estimate is a coin flip, and eight cases cannot
resolve it better than "anywhere from impossible to almost certain".** The band
is now *wider* than the four-entry document's 2–100%, at both ends that matter:
its lower end has fallen to essentially zero, and 1.55% of outer resamples give
P(rank 1) = **exactly 0**. The old text called the 95% band "the single most
useful line in this document"; that is still true, and the line now reads worse.

**A bare "50%" is a worse claim than no figure at all** — the amendment that said
this of 68% applies with more force here, because 50% invites the reading "even
odds, we might win" when what eight cases support is "we cannot tell".

### Full rank distribution (400,000 resamples)

| our rank | probability | (four-entry board, for comparison) |
|---|---|---|
| **1** | **50.2%** | 67.6% |
| 2 | 19.0% | 18.6% |
| 3 | 14.7% | 12.8% |
| 4 | 10.6% | 0.86% |
| 5 | 4.7% | 0.19% |
| 6 | 0.77% | — |
| 7 | 0.18% | — |

Rank 4 going 0.86% → 10.6% is the arrival of Tian, Buchanan, Hickel & Dwight:
under the four-entry board there was "no cheap way to be 4th", and now there is.

---

## 3. The not-decided pairs — recomputed, name by name

The old set was **Reissmann and Wu & Zhang not decided; Liu and Montoya decided**.
Recomputed over all six:

| opponent | published overall | our margin | P(we lead) | paired *t* (n = 8) | per-case sd | cases we win | verdict |
|---|---|---|---|---|---|---|---|
| **Yang** | 0.058013 | −0.001365 | **57.8%** | **−0.189** | 0.020441 | **4 of 8** | **NOT DECIDED** *(new — and it is the leader)* |
| Reissmann, Fang & Sandberg | 0.059525 | −0.002878 | 69.4% | −0.495 | 0.016436 | 4 of 8 | **NOT DECIDED** *(unchanged)* |
| Wu & Zhang | 0.062412 | −0.005765 | 84.7% | −0.953 | 0.017102 | ~~5 of 8~~ **4 or 5 of 8** ‡ | **NOT DECIDED** *(unchanged)* |
| **Tian, Buchanan, Hickel & Dwight** | 0.064138 | −0.007490 | **86.0%** | **−1.033** | 0.020512 | 5 of 8 | **NOT DECIDED** *(new)* |
| Liu, Wang, Zhao & Xiao | 0.073687 | −0.017040 | 98.7% | −2.203 | 0.021875 | 7 of 8 | decided |
| Montoya, Oulghelou & Cinnella | 0.077863 | −0.021215 | 99.8% | −2.912 | 0.020608 | 7 of 8 | decided |

**‡ REPAIRED 2026-08-15 — the Wu & Zhang cases-won cell is `4 or 5 of 8`, and this row's
verdict does not move.** The struck `5 of 8` is left visible. *What falsified it:* one of the
five, `AR_1_Ret_360`, is our `0.04547044480564218` against Wu & Zhang's **printed** `0.0455`,
a gap of **2.96e-5** — **below the ±5e-5 half-ulp of a four-decimal printing**, so Wu & Zhang's
true value lies in [0.045450, 0.045550] with ours inside it and **the published board cannot
say who won that case**. Measured by interval propagation in
`campaign/MARGIN_PRECISION_INTERVAL_2026-08-15.md` §3.1 (committed `eadcd112`), filed as
`docs/DOCKET.md` **D133**, and re-derived over all 48 cells before this edit: it is the **only**
cell of the 48 below the half-ulp, and no other cases-won cell in this table is affected —
Tian's `5 of 8` is exact. **The direction is unaffected and this is not a retreat:** "decided"
needs ≥ 7 of 8, so the verdict is `NOT DECIDED` at 4 and at 5 alike, and P(we lead), *t* and
the sd are unmoved. A bare `4 of 8` is **not** written here, because that would assert a
resolution the published data does not support in the other direction. This makes the row
agree with `demo-output/website/CLOSURE_CHALLENGE_STATUS.md` and `docs/PRODUCT_LIST.md`, which
already read `AR_1` as a tie below published precision. (§3a below, on the *best-on-board*
count, is a different claim and is untouched.)

**The not-decided set doubles, from two pairs to four, and now contains the entry
that sits above us.** The threshold is the one the four-entry document used and
is stated here so it can be argued with rather than inferred: decided means
P(we lead) ≥ ~98% **and** |t| > 2 **and** 7 of 8 cases won. Liu and Montoya clear
all three; nothing else clears any of them.

**Yang, specifically, is the least decided comparison the lab has ever had.**
Margin 0.001365 against a per-case dispersion of 0.020441 — the dispersion is
**fifteen times** the margin, where against Reissmann it was five times. `t = −0.189`.
We win four of the eight cases. The margin is **less than half** the Reissmann
margin that the record already refused to call decided, and the *t* statistic is
**less than half** of it too. The argument the board-moved note made a fortiori is
now a measurement, and the measurement agrees with it.

**Where the Yang comparison actually lives, case by case** — it is not a uniform
near-tie, it is two large opposite bets:

| case | ours | Yang | ours − Yang |
|---|---|---|---|
| `alpha_15_13929_4048` | 0.050105 | 0.0806 | **−0.030495** (our biggest win on the board) |
| `alpha_15_13929_2024` | 0.101112 | 0.1229 | −0.021788 |
| `alpha_05_4071_4048` | 0.046108 | 0.0645 | −0.018392 |
| `alpha_05_4071_2024` | 0.071863 | 0.0748 | −0.002937 |
| `AR_1_Ret_360` | 0.045470 | 0.0291 | +0.016370 |
| `AR_3_Ret_360` | 0.039982 | 0.0311 | +0.008882 |
| `AR_14_Ret_180` | 0.035339 | 0.0250 | +0.010339 |
| `NASA_2DWMH` | 0.063198 | 0.0361 | **+0.027098** |

We beat Yang on all four periodic hills and lose to Yang on all three ducts and
on the NASA hump. **Yang is better than us at precisely the thing round 5 was
built to fix.** That is a more informative sentence than any probability in this
document, and it costs nothing to say.

---

## 3a. The best-on-board count collapses, and this was not the question asked

**Found while checking whether the public pages' other board-derived numbers were
frame-specific too. They were.** The count is the number of the eight cases on
which our column holds the lowest number on the board. It is a *minimum over the
entrants*, so adding entrants can only take rows away — the mirror image of the
band-monotonicity argument in `ACTIVE_RESEARCH.md`, and going the other way.

| case | ours | best of the four | best of the six | held on 4? | held on 6? |
|---|---|---|---|---|---|
| `alpha_15_13929_4048` | 0.050105 | 0.0592 Reissmann | **0.0432 Tian** | **BEST** | **lost** |
| `alpha_15_13929_2024` | 0.101112 | 0.1195 Wu & Zhang | **0.0998 Tian** | **BEST** | **lost** |
| `alpha_05_4071_4048` | 0.046108 | 0.0569 Wu & Zhang | 0.0569 Wu & Zhang | **BEST** | **BEST** |
| `alpha_05_4071_2024` | 0.071863 | 0.0760 Reissmann | 0.0748 Yang | **BEST** | **BEST** |
| `AR_1_Ret_360` | 0.045470 | 0.0387 Reissmann | 0.0291 Yang | — | — |
| `AR_3_Ret_360` | 0.039982 | 0.0341 Reissmann | 0.0311 Yang | — | — |
| `AR_14_Ret_180` | 0.035339 | 0.0325 Reissmann | 0.0250 Yang | — | — |
| `NASA_2DWMH` | 0.063198 | 0.0364 Wu & Zhang | 0.0294 Tian | — | — |

**4 of 8 → 2 of 8.** Both losses are to Tian, Buchanan, Hickel & Dwight, on the
two `alpha_15` periodic hills.

**And the count that matters is worse than that.** The lab's own standing
disclosure — carried on four external surfaces after Ladder V rung V13 forced it —
is that **two of the four best rows are the organisers' own unmodified RANS field**,
passed through untouched by the decline gate, and that the credit there belongs
to the baseline every entrant is handed for free. Those two are exactly
`alpha_05_4071_4048` and `alpha_05_4071_2024` — **the two that survive.**

> **So the count belonging to our own model goes 2 of 8 → 0 of 8. On the live
> board, our model is best on nothing.**

**This is a harder sentence than any probability in this document and it is not a
close call**: it is a comparison of published four-decimal numbers, with no
resampling, no seed, and no interval. `sdk/scripts/closure_decline_gate_audit.py`
already recorded that *"best on board" is not defensible as a headline or as a
count of cases we lead*; that judgment was made when the count was 4 and the
model's share was 2. It is now unanswerable.

**What it does NOT change.** The overall score is a mean, not a count of wins, so
0.056647 is still the lowest overall on the board and the rank-1 claim still
stands on the number — as §2 says, with P(rank 1) = 50%. **Being best on no
single case while holding the best mean is not a contradiction**: it is what
winning on consistency rather than on peaks looks like, and it is arguably the
more honest description of this entry. It should be *said that way* rather than
patched, and the four external surfaces should say it.

**Disposition, and why nothing is silently rewritten here.** The stale count is
pinned by two files this pass must not edit: `scripts/self_audit.py` faults an
`our_entry` that states best-on-board 4 of 8 *without* the baseline disclosure,
and `sdk/tests/test_mega_batch.py` asserts the literal string
`"four of the eight test cases"`. **A correct new count would fault against a
guard built for the old one** — the same shape as docket D48 one level up. So the
surfaces here are corrected by **strike-and-keep**: the old count stays present
and visibly struck, the new one stands beside it, no reader meets a false claim,
and no other agent's suite reddens. Filed as docket **D51** for the owner of those
two files.

---

## 4. Why the figure fell 17.4 points, decomposed

The fall is **67.6% → 50.2%**, and it is **not** all the closer leader. Two
causes, and they are separable because the pairwise probabilities are unchanged
for the four entrants who were already there:

| step | value | effect |
|---|---|---|
| P(we lead the leader), four-entry board (Reissmann) | 69.4% | — |
| P(we lead the leader), six-entry board (Yang) | **57.8%** | **−11.6 points** — the closer leader |
| gap between "lead the leader" and "lead everyone", four-entry | 69.4 − 67.6 = **1.8 points** | — |
| gap between "lead the leader" and "lead everyone", six-entry | 57.8 − 50.2 = **7.6 points** | **−5.8 points** — the extra entrants |
| **total** | | **−17.4 points** |

**Two thirds of the fall is the closer leader; one third is that there are now
five ways to lose instead of three.** The second third is the part that would
have been missed by only re-reading the top of the board, and it is why the
recomputation was worth doing rather than reasoned about: a new entrant at rank
**4** — 0.0075 *behind* us, comfortably — still costs us 5.8 points of P(rank 1),
because in the resamples where the ducts are drawn heavily, Tian passes us.

**The slightly surprising result, stated carefully:** P(rank 1) did not fall as
far as the halved margin might suggest. The margin more than halved (0.002878 →
0.001365) while the probability fell by about a quarter of its value. That is not
a reassurance — it is a property of a statistic that was already dominated by
dispersion rather than by margin. When the per-case spread is five to fifteen
times the margin, halving the margin moves the probability far less than halving
it; the figure was never mostly *about* the margin. The correct conclusion is the
uncomfortable one: **68% was already not a statement about a lead, and neither is
50%.**

---

## 5. Leave-one-case-out: what the standing rests on now

Each row deletes one case and re-runs both the point ranking and a 7-case bootstrap.

| case deleted | point margin vs **Yang** | our point rank | P(rank 1) | *(four-entry: point rank / P)* |
|---|---|---|---|---|
| `alpha_15_13929_4048` | **+0.002796** | **2** | **31.7%** | 1 / 57.4% |
| `alpha_15_13929_2024` | **+0.001552** | **3** | **32.2%** | 2 / 38.0% |
| `alpha_05_4071_4048` | **+0.001067** | **2** | **32.6%** | 1 / 54.6% |
| `alpha_05_4071_2024` | −0.001141 | 1 | 44.2% | 1 / 63.1% |
| `AR_3_Ret_360` | −0.002829 | 1 | 53.7% | 1 / 72.3% |
| `AR_14_Ret_180` | −0.003037 | 1 | 53.5% | 1 / 69.8% |
| `AR_1_Ret_360` | −0.003899 | 1 | 57.6% | 1 / 73.3% |
| `NASA_2DWMH` | −0.005432 | 1 | 78.5% | 1 / 91.2% |
| *(none — as scored)* | −0.001365 | 1 | 50.2% | 1 / 67.6% |

**"The standing is two cases wide" is retired. It is now three deletions wide,
and the three are different cases.** Under the four-entry board exactly one
deletion (`alpha_15_13929_2024`) cost us the point rank. Under the six-entry
board **three** do — all three of the periodic hills we beat Yang on — and one of
them costs us **two** places, not one.

**The identity of the load-bearing case has changed, and this is the finding the
old document could not have had.** It named `alpha_15_13929_2024` as the single
case carrying the standing. Against Yang the largest single lead is
`alpha_15_13929_4048` (−0.0305), and deleting it is now the *most* damaging
deletion of the eight. Any sentence anywhere in the corpus that names
`alpha_15_13929_2024` as *the* case the standing rests on is now frame-specific
to the four-entry board and must say so.

**`NASA_2DWMH` is still pure cost** — delete our only last-place case and
P(rank 1) goes to 78.5%. Unchanged in direction, smaller in size, because Yang
also beats us there.

---

## 6. The method is the same method, and that is proved, not asserted

A recomputation is only comparable to the figure it replaces if the method is the
same. **Positive control, executed:** the identical script, run with the two new
entrants removed and nothing else changed, reproduces the four-entry document to
the digit.

| quantity | four-entry document, 2026-08-10 | this script, four entrants |
|---|---|---|
| P(rank 1) | 67.6% | **67.62%** |
| rank 2 / 3 / 4 / 5 | 18.6 / 12.8 / 0.86 / 0.19 | **18.58 / 12.76 / 0.86 / 0.19** |
| P(we lead) Reissmann / Wu / Liu / Montoya | 69.4 / 84.7 / 98.7 / 99.8 | **69.4 / 84.7 / 98.7 / 99.8** |
| paired *t*, Reissmann / Wu | −0.495 / −0.953 | **−0.495 / −0.953** |
| double bootstrap 68% band | 26 – 94% | **26 – 94%** |
| double bootstrap 95% band | 2 – 100% | **2 – 100%** |
| leave-one-out P(rank 1), eight rows | 38.1 / 57.3 / 54.6 / 63.2 / 69.7 / 72.4 / 73.2 / 91.1 | **38.0 / 57.4 / 54.6 / 63.1 / 69.8 / 72.3 / 73.3 / 91.2** |

Every figure reproduces; the leave-one-out row differs in the first decimal only,
from the order in which draws are taken from the generator stream. **The four
pairwise probabilities and both *t* statistics come out identical in the
six-entry run as well** — they are pairwise, so who else is on the board cannot
touch them, which is itself a check that the six-entry run did not disturb the
old arithmetic.

**The script is committed** at `sdk/scripts/probability_of_rank.py`. The
four-entry computation shipped no script, which is why re-deriving it required
re-deriving it. This one runs in five seconds on the board table it is given, so
the next time the board moves the recomputation costs one fetch and one command.

### What the method still assumes, unchanged and still true

The three caveats of the four-entry document survive verbatim and are not
re-litigated here: the scoring is **local and nothing has been submitted**; the
**cases are not exchangeable** and the bootstrap assumes they are, so the
effective number of independent cases is nearer 3 than 8 and the reported spread
is if anything **too narrow**; and the other entrants' scores are **fixed
published values**, so what is resampled is case selection, not their methods.
The fourth also stands: P(rank 1) is a probability about a resampling procedure,
**not** a posterior over the world.

**A fifth caveat this board move adds.** Two of the six rows are new and have
never been re-scored on our harness. The four-entry document could say that all
four entrants' submitted CSVs re-score locally to their published values; **it
cannot be said of Yang or of Tian**, whose prediction files are not in the frozen
clone at `deb9155`. Their per-case values are transcribed from the live README
and are trusted at the same level as any published number — which is to say, the
reproduction check of §1 is all we have on them.

---

## 7. Two derived quantities, recomputed because they are quoted elsewhere

**The seed bound.** The truth-free seed-spread bound on the overall is 0.0024
(`closure_challenge_stability_physicality_audit.md` §1), loaded adversely on the
three seed-dependent cases:

| scenario | our overall | P(rank 1) | *(four-entry)* | P(we lead the leader) |
|---|---|---|---|---|
| adverse (+0.0024) | 0.059047 | **34.2%** | 52.0% | 44.4% (Yang) |
| as scored | 0.056647 | **50.2%** | 67.6% | 57.8% (Yang) |
| favourable (−0.0024) | 0.054247 | **65.4%** | 80.5% | 69.0% (Yang) |

**A seed draw the lab did not control moves P(rank 1) from 34% to 65%** — a
31-point span, and the adverse leg now puts us behind Yang on the point score
(0.059047 vs 0.058013). The old sentence "52% to 81%" is superseded by
"**34% to 65%**". Note what this means and say it plainly: **under the adverse
seed we are not rank 1 at all.** Under the four-entry board the adverse seed left
us rank 1 with a weakened probability; it no longer does.

**Published-precision ties.** `AR_1_Ret_360` (ours 0.045470 vs Wu & Zhang's
0.0455, gap 0.00003) and `AR_3_Ret_360` (ours 0.039982 vs 0.0399, gap 0.00008)
remain ties below published precision and must never be quoted as wins or losses.
Honouring them as ties moves P(rank 1) from 50.15% to 50.1%, with 0.1% of
resamples tied for first rather than sole first — a smaller effect than on the
four-entry board. **No new tie appears against Yang or against Tian**: the
nearest is 0.0029 (`alpha_05_4071_2024` vs Yang), two orders above published
precision.

---

## 8. What the house may now say, and what it may not

**May be said, internally and externally, with every clause attached:** *Our
round-5 entry's 0.056647 is the best overall number on the live six-entry board
as scored locally on these eight cases at benchmark commit `deb91557` — a local
scoring, not an official placement, and nothing has been submitted. Resampling
the cases puts the probability that we would still be first on a comparable set
at **50%**, which an eight-case sample cannot pin tighter than **0–97% at 95%**.
The leads over **Yang, Reissmann, Wu & Zhang, and Tian, Buchanan, Hickel & Dwight
are not statistically decided**; the leads over Liu and Montoya are. A single
seed draw the lab did not control moves the figure from 34% to 65%, and its
adverse leg puts us second.*

**Must not be said**, in addition to everything the four-entry document already
forbade: that the lead over Yang is a lead in any sense a statistician would
accept; that P(rank 1) = 50% means "even odds of winning"; or that the standing
is two cases wide.

**Standing instruction unchanged. Submissions remain PARKED and are reserved to
Katie.** This document corrects an internal figure. It is not a response to the
standings, it is not evidence that a send is pending, and it prepares no
submission action.

---

## 9. The generalisable finding

**A probability computed against a field is a claim about that field, and a field
is not a constant.** The four-entry figure was correctly computed, correctly
caveated, propagated in lockstep to nine surfaces and verified four times over —
and it went wrong anyway, because every one of those checks tested the figure
against its *inputs* and none tested the inputs against the *world*. The corpus
had a rule that the figure may never be stated without its interval; it had no
rule that it may never be stated without its **board**. That is the gap this
document closes, and the cheap structural fix is the one `BOARD_MOVED` §5 names:
**a claim whose referent can move states the referent's snapshot beside the
figure**, so a reader can see the frame expire.

## Provenance

- Per-case scores, ours: `demo-output/website/closure_challenge_round5_qcr.json` (written at `07a7fe9e`)
- Per-case scores, board: the live README, fetched 2026-08-11T23:33Z, two routes; recorded in `campaign/BOARD_MOVED_2026-08-11.md` (`9cb2a20a`)
- Script: `sdk/scripts/probability_of_rank.py`
- Superseded computation, kept: `campaign/PROBABILITY_OF_RANK_2026-08-10.md`
- Scoring calls made by this document: **0**. Ledger unchanged at 6. Solver core-min: **0**.
