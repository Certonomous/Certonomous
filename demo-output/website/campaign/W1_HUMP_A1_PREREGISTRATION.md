# W1 hump a1 shear-stress-limiter sensitivity arm — pre-registration

Written 2026-08-08, before any solve. Item: `f6a-hump-a1-limiter-sensitivity`
(filed this date at intake-zero violations; ordered by the chief's entry-2
outcome block, commit `0a764729`, approved in the chief's resume directive).
Successor to the executed challenge-conditions record
(`W1_HUMP_CHALLENGE_RESULTS.md`, pre-reg `74797a57`): Gate V passed there,
Gate P failed on reattachment at +13.92%, and the QCR2000 arm's null ruled
out the constitutive route, implicating the separated-shear-layer stress
magnitude. This arm asks the next falsifiable question: **is the SST
shear-stress limiter the mechanism?**

## 1. The single parameter, and why these values

In v2606 kOmegaSST, nut = a1 k / max(a1 omega, b1 F23 S): wherever the
strain argument wins (separated shear layers are the design case), nut is
proportional to **a1**. Stock a1 = 0.31 encodes Bradshaw's structure
parameter; the literature's own spread for that parameter is roughly ±10%.
Two arms, one variable each, nothing else changed from the executed SST leg
(same shipped mesh, same `residualControl` U/p/k 5e-7 / omega 1e-10, same
cap 5000, same 4 ranks, cold start from the same shipped `0/`):

| arm | a1 | mechanism reading if the bubble responds |
| --- | --- | --- |
| a1_028 | 0.28 (−10%) | less nut in the limited region, longer bubble expected |
| a1_034 | 0.34 (+10%) | more nut, shorter bubble expected |

Comparator: the executed SST leg, separation 0.6544, reattachment 1.2531
(registry `w1hump_challenge_sst_20260807T224139Z`).

## 2. Gate (the review's wording made numeric)

Materiality bar, same instrument and bar as the QCR arm: an arm is
**material** iff |reatt(arm) − 1.2531| ≥ **0.010 x/c** (Cf sign crossings
via the unmodified `hump_gate_analysis.py`).

- **Outcome one — mechanism:** at least one arm is material. The finding is
  the sensitivity with sign, reported as Δreatt per Δa1 across the three
  points (0.28, 0.31, 0.34); the mis-scaled-stress hypothesis gains a
  mechanism, not just an implication.
- **Outcome two — upstream:** both arms below the bar. The limiter is
  exonerated at the ±10% scale and the omega-budget question moves upstream
  to the production/destruction balance, per the review's dichotomy.
- An arm that hits the 5000 cap without `residualControl` is reported
  unconverged and ungated (L-24); an arm that crashes is recorded per the
  guidelines §4 table and excluded without softening the bar.

## 3. Predictions (numeric, scored afterwards, kept as written)

1. Both arms converge on `residualControl` within the cap (the two executed
   legs took 1922 and 1637).
2. **Outcome one lands**, direction as the mechanism table: a1 = 0.34 moves
   reattachment **toward** experiment by ≥ 0.010 (window: −0.010 to −0.060
   from 1.2531), a1 = 0.28 moves it **away** by ≥ 0.010 (window: +0.010 to
   +0.060). The limiter is active in the bubble's shear layer.
3. Neither arm repairs Gate P: reattachment stays outside 1.100 ± 5% in
   both arms (the bias is bigger than a ±10% constant sweep).
4. Cost: ≤ 12 core-min total, gross, wall × 4 ranks (measured basis 5.58
   per converged leg).

## 4. Budget and bookkeeping

12 core-min approved on the item. Runs
`/home/ubuntu/certonomous-runs/w1-hump-challenge/{a1_028,a1_034}`; registry
entries per solve; evidence appended to the W1 hump results line; docket
outcome on the item. Separation is recorded per arm as a secondary
observable, not gated.

---
*Nothing below this line existed when the runs were launched.*
