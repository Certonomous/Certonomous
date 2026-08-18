# EIG per core-minute vs the gain-table heuristic — a lookback on the closed docket

**2026-08-10. Zero solver core-min. Nothing was re-run; this is a re-ranking of
114 already-closed items against their already-recorded outcomes.**

Item: `agenda/proposals/expected-information-gain-per-core-min-beats-the-current-ranking-heuristic.json`
(status `approved`, decision note "chief approval 2026-08-10"). Strategy §3,
information-theoretic experiment design.

---

## 0. Verdict and recommendation, first

**The claim as filed — "proposals ranked by EIG/core-min beat the current
heuristic on a lookback test" — is NOT established.** Both rankings are
*anti-*correlated with what the closed items actually delivered.

**What IS established, and it is the useful half: the EIG numerator beats the
gain-table numerator, decisively and robustly.** The information content of a
proposal's pre-declared outcomes predicts delivered value (ρ = +0.31, p = 0.0008;
+0.20, p = 0.035 under a machine rule that never reads an outcome). The source-kind
gain table does not (ρ = +0.12, p = 0.21).

**What the lookback also found, and nobody was looking for it: the `/core-min`
denominator is the broken part of BOTH rankings.** It is arithmetically inert on
54 of 114 closed items, and where it is live it points the wrong way — expensive
items delivered more (ρ(cost, value) = +0.28, p = 0.002).

### RECOMMENDATION: **ADOPT WITH MODIFICATION**

1. **Adopt the EIG numerator.** Replace `_GAIN_POINTS[source_kind]` in
   `sdk/chief_engineer/agenda.py` with the branch-entropy score of §3, implemented
   as the **mechanical keyword rule** of §6 — not as an agent's judgement call.
   The mechanical rule reads only `expected_knowledge_gain` and `gate`, never an
   outcome, and it reproduces the hand scoring at ρ = +0.70 while carrying no
   hindsight.
2. **Do NOT adopt "EIG/core-min" as a phrase or as a claim.** The composite does
   not beat the incumbent on the pre-declared correlation metric by enough to act
   on, and the strategy's PROOF clause as worded is **not met**. Record it as not
   met rather than as met with caveats.
3. **Fix the denominator before ranking on it at all.** 52 of 114 closed items were
   filed at `est_core_min = 0` and 54 sit at or below the 1.0-core-min floor, so
   the division does nothing for them; the control room's label "expected knowledge
   gain per core minute, deterministic" describes a quantity that on half the
   docket is just the numerator. Either price zero-cost items honestly or state
   that the ranking is a numerator ranking for report-shaped work.
4. **Re-run the strict test next quarter.** Zero of the 98 graded predictions
   carries a numeric confidence, so this lookback runs on an ordinal proxy. Once
   `pre-registrations-carry-a-confidence-line` lands, `H(p)` becomes computable
   from stated probabilities instead of inferred from prose, and outcome three of
   this item's own pre-declaration ("the ordinal proxy is too coarse") gets its
   dated retest.

**Do not change the ranking in force on this document alone.** The item's own gate
says the ranking is not changed on an inconclusive lookback; recommendation 1 is a
numerator change with positive evidence behind it and belongs to the chief, and
recommendations 2–4 change nothing until he rules.

---

## 1. The metric, fixed before either ranking was computed

Declared in this order, and not revised afterwards:

- **Cohort.** All 114 docket items at `status: done`. Every one carries an
  `outcome` field; that field is the ground truth. (`docket.json`, 263 proposals:
  114 done, 84 proposed, 51 approved, 14 dismissed.)
- **Ground truth `V`, graded from the `outcome` text on a 0–3 scale:**
  - **3 — record-changing:** overturned a belief the record was acting on, closed an
    open anomaly, moved a scored number or the entry of record, convicted a
    mechanism, or produced a standing rule the record now enforces.
  - **2 — substantive:** delivered a number or a fix the record uses; a clean
    negative that closed a line of inquiry.
  - **1 — marginal:** confirmed what was already believed, or found the work
    already done; bookkeeping landed, no decision moved.
  - **0 — null:** no usable result at all.
  - Distribution: **0 × V=0, 13 × V=1, 43 × V=2, 58 × V=3.** No item scored 0 —
    the lab closes items that produced *something*, which compresses the scale and
    is itself worth knowing.
- **Comparison metrics** (all three fixed in advance):
  1. Spearman ρ between ranking score and `V`;
  2. top-20 precision, P(V = 3) among each ranking's top 20, and bottom-20
     precision, P(V ≤ 1) among its bottom 20;
  3. head-to-head concordance on the pairs the two rankings order *differently*.
- **Both rankings use only pre-run information:** `source_kind`, `est_core_min`,
  `cost_basis`, `expected_knowledge_gain`, `gate`. Never `outcome`,
  never `measured_core_min`.

---

## 2. The incumbent, restated exactly

`sdk/chief_engineer/agenda.py`, `rank_value()`:

```
rank_value = _GAIN_POINTS[source_kind] / max(est_core_min, 1.0)

_GAIN_POINTS = {challenge 4.0, measurement 3.0, gate 3.0, capability 2.0,
                ledger 2.0, reading 2.0, inbox 2.0, report 1.0}
```

The module's own comment records that this table has already failed once: three
kinds in real use were absent, 24 of 55 proposals ranked on a silent 2.0 default,
and `gate` outranked `challenge` by 50% on every tie — inverting the priority order
the table existed to serve. That is the recorded motive for testing a replacement.

**What the table is actually betting on, graded:**

| source_kind | gain | n | mean V |
|---|---|---|---|
| challenge | **4.0** (highest) | 4 | **2.00** (lowest) |
| measurement | 3.0 | 24 | 2.38 |
| gate | 3.0 | 25 | **2.64** (highest) |
| capability | 2.0 | 17 | 2.41 |
| ledger | 2.0 | 11 | 2.36 |
| reading | 2.0 | 13 | 2.31 |
| report | **1.0** (lowest) | 19 | 2.21 |

The table's top and bottom are both misplaced. `challenge` is scored at 4.0 and
delivered the least; `report` is scored at 1.0 and delivered more than `challenge`.
Two caveats against over-reading this: n = 4 for `challenge`, and two of those four
(`w5-sparta-is-still-the-cheapest-real-result`, `w5-sparta-frozen-rans-is-the-unblock`)
are duplicate filings of the same SpaRTA rung that closed by pointing at an
existing record. But the ordering is not rescued by removing them, and the
underlying point holds independently: **source kind explains almost nothing about
delivered value** (ρ = +0.12, p = 0.21, and the whole table takes only four
distinct values across 114 items).

---

## 3. EIG, defined operationally for this lab's proposal shapes

A proposal's information content is the entropy of its **pre-declared outcome
set**. A proposal whose two named branches are both instructive and roughly
equiprobable carries a full bit; one whose stated outcome is already believed
carries almost nothing.

`EIG_bits = H(p)` over the branches named in `expected_knowledge_gain` (falling
back to `gate`), with the prior read ordinally from the proposal's own prose,
because **zero of the 98 graded predictions in
`CALIBRATION_SCORECARD_2026-08.md` carries a numeric confidence** — the strict
computation is unavailable this quarter and the scorecard says so.

| tier | rule (read from the proposal, never from the outcome) | p | bits | n | mean V |
|---|---|---|---|---|---|
| **A3** | three distinguishable outcomes named, each stated to change a decision | uniform / 3 | 1.585 | 2 | **3.00** |
| **A** | two mutually exclusive branches named, neither implied by the record, both stated instructive ("either… or…", "both outcomes", "either way the lab learns") | 0.50 | 1.000 | 35 | **2.71** |
| **B** | two branches named but one clearly favoured by the record already | 0.25 | 0.811 | 7 | **1.71** |
| **C** | one outcome named whose *value* is unknown but whose *existence* is assumed (a measurement, a sweep, a count) | 0.10 | 0.469 | 26 | 2.46 |
| **D** | a deliverable: the outcome is that the thing gets built, written or adopted | 0.02 | 0.141 | 44 | 2.18 |

**Denominator, using the scorecard's own basis split.** The scorecard's sharpest
measured finding is that *the predictor is the basis, not a factor*:
measured-basis estimates missed by at most 1.84×, forecast-priced ones ran to
13.55×. So a forecast-priced core-minute is not worth a measured one:

```
EIG_score = EIG_bits / max(est_core_min × k, 1.0),   k = 1.0 if cost_basis starts "measured", else k_f
```

`k_f` is swept at 1, 2, 3 below; **the verdict is insensitive to it** (ρ = −0.194,
−0.191, −0.182), which is the honest way of saying the basis split, however well
measured, is not what is wrong here.

---

## 4. Results against the pre-declared metric

| ranking | Spearman ρ vs V | Kendall τ | top-20 P(V=3) | bottom-20 P(V≤1) | distinct scores |
|---|---|---|---|---|---|
| **heuristic, gain/core-min** | **−0.282** (p = 0.0024) | −0.233 | 0.40 | 0.10 | 27 |
| **EIG/core-min, k_f = 1** | −0.194 (p = 0.038) | −0.162 | 0.40 | 0.15 | 39 |
| **EIG/core-min, k_f = 2** | **−0.191** (p = 0.042) | −0.158 | 0.40 | 0.15 | 43 |
| **EIG/core-min, k_f = 3** | −0.182 (p = 0.053) | −0.151 | 0.40 | 0.15 | 43 |
| *numerator only:* gain points | +0.118 (p = 0.21) | +0.111 | 0.35 | 0.20 | 4 |
| *numerator only:* **EIG bits** | **+0.311** (p = 0.00076) | +0.277 | **0.65** | 0.25 | 5 |
| *control:* 1 / max(est,1) — cheap first | −0.282 (p = 0.0024) | −0.244 | 0.40 | 0.15 | 24 |
| *control:* max(est,1) — expensive first | **+0.282** | +0.244 | **0.70** | 0.20 | 24 |

Three things fall out of that table, in ascending order of importance.

**(a) EIG/core-min is less wrong than the heuristic, not right.** ρ moves from
−0.282 to −0.191, bottom-20 precision from 0.10 to 0.15, top-20 is a tie at 0.40.
"Less negative" is not "beats".

**(b) The entire improvement is in the numerator, and it is real.** EIG bits alone
reaches ρ = +0.311 with p = 0.00076 and top-20 precision of 0.65 against the gain
table's 0.35 — nearly double. On the 60 items where the denominator is actually
live (`est_core_min > 1`), EIG bits alone scores **ρ = +0.342 (p = 0.007)** while
gain points score **−0.019 (p = 0.88)** and the full heuristic **−0.200 (p = 0.13)**.

**(c) The denominator is the broken part of both rankings.** The single control
line — *rank by cost, most expensive first* — beats both rankings on every metric
in the table (ρ = +0.282, top-20 precision 0.70). Expensive items delivered more.
And on **54 of 114** items the denominator is arithmetically inert: 52 were filed
at `est_core_min = 0` and hit the 1.0 floor.

**Head-to-head on the 885 pairs the two rankings order differently** (pairs tied in
V excluded):

| | count | share |
|---|---|---|
| EIG right, heuristic wrong | **424** | 47.9% |
| heuristic right, EIG wrong | 241 | 27.2% |
| neither strictly right | 220 | 24.9% |

Sign test on the 665 decisive pairs: **p = 1.2 × 10⁻¹²**. On this metric EIG/core-min
does beat the heuristic, clearly. It is the one pre-declared metric on which the
claim holds, and §6 shows most of that margin survives a de-confounding rewrite.

---

## 5. Where EIG mis-ranks — stated against my own metric

**EIG's top 20 contains three items that delivered V ≤ 1:**

| item | tier | why EIG was wrong |
|---|---|---|
| `w4-dafoam-community-forums` | A (1.0 bit) | "Either the search shortens dramatically or the finding is confirmed novel" — a perfect two-branch pre-declaration whose outcome is one line: *"if ever filed it is a comment on #57"*. A well-drafted question about a low-stakes thing. |
| `w3-refit-stored-studies-in-place` | B | "any verdict that moves under the corrected fit is a finding" — no verdict moved. EIG rewarded the *possibility* of a finding; the record got bookkeeping. |
| `w5-disclose-the-bump-claim` | B | already satisfied before it ran. |

**EIG puts 25 V = 3 items in its bottom 40 — including the highest-value item on
the whole docket.** `w3-qcr-forward-on-the-ducts-is-the-rank-1-route` (tier A,
est 95 core-min) is the item that produced round 5, the 0.0654 → 0.056647 move and
the local rank-1 standing. **Both rankings bury it.** So do
`fiml-adjoint-conditioning-unblock` (est 240, unblocked the whole Stage-1 line),
`tmr-flatplate-finest-grids` (est 327, the first conclusive ladder in the corpus)
and `s1-cbfs-field-inversion-run` (est 600). The heuristic buries 27 V = 3 items in
its bottom 40, including all of the same four. **Neither ranking would have led the
lab to the work that actually changed the record**, and that is the finding the
chief should take from this document ahead of the verdict.

**A non-monotonicity inside my own tier scale.** Tier B (0.811 bits) has mean V =
1.71 — *below* tiers C (0.469, mean 2.46) and D (0.141, mean 2.18). The scale is
not monotone in delivered value. n = 7, so this may be noise; but the mechanism is
plausible and unflattering: a tier-B proposal is one whose author already knew
which branch would fire, and knowing that is exactly what makes an item cheap to
close and dull to read. If the numerator is adopted, tier B should be merged into
tier D rather than sitting between A and C.

---

## 6. Adversarial pass — is this confounded by hindsight?

**Yes, in two named ways, and here is what survives each.**

### Confound 1 — I graded the outcomes knowing them. The heuristic did not.

Unfixable in principle: a lookback is hindsight by construction. Two mitigations
were run.

- **Grade robustness.** Perturb every `V` by ±1 at random (15% of grades moved
  each way), 2,000 draws. **EIG bits beats gain points on 99.0% of them.** The
  numerator result is not an artefact of individual grading calls.
- **The `V` scale has no zeros.** Nothing scored 0, so "which was a null nobody
  used" resolves to 13 items at V = 1, mostly of one shape: *the work was already
  done before the item ran* (`w5-tmr-iteration-caps` — done 15 minutes before
  filing; `w8-in-sample-inversion-clause`; `w5-figures-must-show-every-rung`) or
  *duplicate filings* (the two SpaRTA items). **Neither ranking can see that
  class**, because "is this already done?" is not a function of source kind, cost
  or outcome entropy. It is the largest single source of wasted docket attention in
  this cohort and it is invisible to both candidates. A duplicate-detection check
  at intake would outperform either ranking change.

### Confound 2 — I assigned the EIG tiers after reading all 114 outcomes.

This is the serious one, and it is fixed by removing the judgement entirely. A
**mechanical rule** was written that reads only `expected_knowledge_gain` + `gate`
and matches regular expressions — `three .* outcomes` → 1.585 bits;
`either…or` / `two .* outcomes` / `both outcomes` / `each outcome changes` /
`either way` → 1.0; `whether` → 0.811; otherwise 0.141. It cannot see an outcome.

| | hand tiers | **mechanical rule** |
|---|---|---|
| EIG bits alone, ρ vs V | +0.311 (p = 0.0008) | **+0.197 (p = 0.035)** |
| top-20 P(V = 3) | 0.65 | **0.70** |
| head-to-head vs heuristic | 424 : 241 | **357 : 312** |
| agreement with hand tiers | — | ρ = +0.70 |

**The numerator result survives de-confounding** — weaker (ρ +0.20 vs +0.31) but
still significant, and its top-20 precision is actually *higher* than the hand
version's and double the gain table's. **The head-to-head result mostly does not
survive**: 357:312 is a much thinner margin than 424:241, which means roughly half
of §4's headline head-to-head win was hindsight in my tier assignments. Recorded
against my own metric, not softened. The mechanical rule is therefore what
recommendation 1 proposes to adopt, and its weaker numbers are the ones the chief
should price.

### Confound 3 — the density test that appears to rescue the incumbent, and is circular

A density ranking should arguably be graded against *realised density*, not against
total delivered value. Done, on the 34 items carrying a `measured_core_min`:

| ranking | ρ vs realised V / measured-core-min |
|---|---|
| heuristic | **+0.768** (p < 0.001) |
| EIG/core-min | +0.626 |
| EIG bits alone | −0.257 (p = 0.14) |
| gain points alone | −0.249 (p = 0.16) |

Taken at face value this reverses the whole document. **It is circular and must not
be taken at face value.** The controls: `1/max(est,1)` *alone* scores **+0.767** —
i.e. the heuristic's entire apparent win is its denominator predicting the target's
denominator (`est` vs `measured`: ρ = +0.692). And `V` alone scores **−0.153**
against the density target, meaning the target is essentially `1/measured` and
carries almost no information about value. Test discarded, and recorded here so
nobody re-runs it and reaches the opposite conclusion.

### What would falsify this document

A second cohort — the next 50 closed items — graded by someone who has not read
this file, with EIG tiers assigned by the mechanical rule at *filing* time rather
than retrospectively. If EIG bits do not beat gain points there, recommendation 1
is wrong. That test costs zero core-min and should be dated when the confidence
line lands.

---

## 7. Which pre-declared outcome fired

The item pre-declared three. **Outcome two fired, with a twist that belongs to
outcome one.** The information-gain ranking did *not* beat the table as a composite
(outcome two, "the table's crude priorities encode something the measure misses");
but the reason is not that the table encodes a hidden priority order — the table's
priorities are measurably *inverted* against outcomes (§2). What the table's
denominator encodes is a budget, and a budget is not a value predictor. The
numerator half of outcome one holds on its own evidence.

## 8. Provenance and reproduction

- Cohort and both rankings: `demo-output/website/agenda/docket.json`, 114 `done` items
- Incumbent heuristic: `sdk/chief_engineer/agenda.py`, `_GAIN_POINTS`,
  `rank_value()`, `RANK_FLOOR_CORE_MIN`; charter §Axis A in
  `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`
- Basis split and the missing-confidence limit:
  `demo-output/website/campaign/CALIBRATION_SCORECARD_2026-08.md` §3, §4
- Solver core-min spent: **0**. Cases opened: **0**. Records modified: this file only.
