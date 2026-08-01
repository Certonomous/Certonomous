# Forecast of the approved backlog

`w6-forecast-the-approved-backlog`. Docket snapshot `2026-08-01T00:18:23Z`.
The docket is live and agents are still filing, so every count below is
stated against that snapshot and will drift.

**Headline: compute is not the binding constraint. Sequencing is, and one
item is 36% of the whole backlog.**

---

## 1. What is approved

| | count | core-min |
|---|---|---|
| approved, total | 112 | 9,929.4 |
| of which **zero-compute** | 45 | 0 |
| of which **needs a solver** | 67 | 9,929.4 |

9,929.4 core-min = **165.5 core-hours**.

Cost basis of the 67 compute items, taken from their own `cost_basis` field:

* 48 items, **8,433 core-min (85%)**, say "estimate".
* 19 items, **1,496 core-min (15%)**, cite a measurement.

Eighty-five percent of the compute this lab is about to spend is priced by
guess. That is the single most important number on this page.

## 2. The machine, measured

* 16 vCPU, 30 GiB. `compute_audit` reserves 2, so **14 usable**.
* Core-minute = wall seconds x MPI ranks / 60 (`COMPUTE_BUDGET_CHARTER.md` §2).
* **Right now:** three `simpleFoam` processes at ~100% CPU (two F6a diffusion
  rungs, one W2 sparta CBFS propagation), load average 3.26.

**Measured sustained throughput.** The mega-batch ledger
(`demo-output/website/mega-batch/ledger.jsonl`, 208,193 rows) ran 208,102
successful evaluations over a 151.4-hour wall span for 212.28 cleaned
compute-hours. Every family in it is serial, so that is 212.28 core-hours.

> **212.28 / 151.39 = 1.40 cores busy, sustained, over 6.3 continuous days.**

That is this lab's only end-to-end throughput measurement, and it says the
lab historically uses **10% of its own box**. It is not a solver figure; it
includes every real-world gap — restarts, retries, agent turnaround, and the
box powering itself off, which it did on 2026-07-30 at 10:40 mid-campaign.

"Cleaned" removes 6 stall rows worth 26.98 core-hours (11.3% of the gross
headline), clustered in two wall-clock windows across two independent solver
families, i.e. host stalls rather than solver cost.

## 3. Wall time for the whole approved backlog

| occupancy | basis | wall time |
|---|---|---|
| 1.40 cores | **measured** sustained, mega-batch ledger | **118.0 h = 4.9 days** |
| 2.24 cores | 4 workers at the same measured per-worker duty cycle | 73.9 h = 3.1 days |
| 14 cores | 14 usable cores packed solid — a ceiling, never observed | 11.8 h = 0.5 days |

A 7-day week at the measured 1.40 cores buys **14,132 core-min**. The stated
backlog is 9,929.4. So:

> **The backlog fits in a week if — and only if — the estimates are under by
> less than 1.42x on average.**

They are not. See §4.

## 4. Estimates I distrust, and why

### 4.1 The calibration the lab already owns

Three misses are already on the record, and two of the three are the same
direction — **under**.

| item | estimated | actual | factor |
|---|---|---|---|
| `agp-e5136061890b` TMR bump fourth rung | 30 | 406.5 solve, ~410 total | **13.6x under** |
| `tmr-flatplate-finest-grids` | 327 | 483.6 | **1.48x under** |
| `naca0012-derive-reference-then-relayer` (superseded pricing) | 3.04 | 180–240 | **~15x under** |
| refit of stored studies priced as a re-run | 8 studies "need compute" | 7 refittable in place | over; 6 needed no compute |

The two mechanisms behind the under-misses are both still live in the docket:

1. **A diagnosis priced as a rung.** `agp-e5136061890b` was priced at 30
   core-min for building one rung; what the roadmap actually asked for was a
   diagnosis, which cost 406.5. The estimate priced the wrong job.
2. **The grid was priced, the iterations were not.** The flat-plate finest
   rung's cells were estimated correctly; it overran because nothing asked how
   long that grid takes to settle. It ran 36,000 SIMPLE iterations, not the
   21,000 in the field.
3. **A repair priced from the wall time of the run it replaces.** The
   defective solve was cheap *because* it was defective.

### 4.2 Items whose estimates carry the same defect today

**`hlpw6-testcase1-coarse-grid-entry`, 3,600 core-min — 36% of the entire
backlog.** Its own `cost_basis` says the memory is "the genuine risk and is
not established": rung A6 held 30 GB free at 579,072 cells, this grid is
2,661,338 cells, 4.6x larger, on a 30 GiB box. The scaling is linear-in-cells
from an *incompressible* run applied to a compressible one. Independent
evidence that this is optimistic: `ADJOINT_MEMORY_ENVELOPE.json` records
DAFoam succeeding at 63,920 cells and failing at 99,840, and A3 at 399,360
cells censored at its 20 GB cap. This item is not merely mispriced; it may be
infeasible on this machine, and its own text says so. **Do not queue it until
the single-angle memory probe it names has run.**

**The eight `agp-*` ladder rungs at 20 core-min each, 160 total.** Every one
is priced "the finest rung holds N cells and the next roughly doubles it" —
the exact reasoning the flat-plate rung proves incomplete, because the
overrun there was iterations, not cells. Direction: under. Two of the eight
sit above 300,000 cells (`agp-880b4f92bdc5` 330,950, `agp-64393439352d`
337,334), where the flat-plate 1.48x is the optimistic end.

**970 core-min of pure defaults.** 26 approved items are priced at exactly
the charter's default (60 for a capability, 20 for a report or a rung, 30 for
a bump) with a `cost_basis` that says nothing but "estimate". There is no
information in these numbers at all. They are not wrong so much as empty, and
they will be wrong in whichever direction the work turns out to run.

**`w1-ahmed-family-asymptotic-ladder`, 240.** The Ahmed 3D viscous family is
the only ledger family where failures are material: 35 successes against 17
failures, a **33% failure rate**. No retry factor is in the estimate.

**Everything mesh-bearing.** The same Ahmed recipe measured 34 s in-batch and
2.95 min in `mission-output/geometry-study` — **5x on identical work**,
attributed to host load. The race benchmark measured the same effect
independently at +32% between two passes. Three solvers are running now.
Every mesh-bearing estimate in this docket assumes an idle box, and the box
is not idle.

**`closure-duct-field-inversion`, 420** — its own basis says it is "flagged
as needing a timed pilot before it is trusted". Take that at face value: this
number is a placeholder, not an estimate.

**`w5-regrade-every-published-gradient-claim`, 300** — priced at
"~1 core-minute per case for the small cases", multiplied by an unknown
number of cases. The multiplier, not the unit cost, is the uncertainty, and
the multiplier is not stated.

### 4.3 The correction applied here

Two hard calibration points (1.48x and 13.6x) are not a distribution. **I use
a flat 3x planning multiplier and I am labelling it a guess, not a
measurement.** It is bracketed by the two points the lab owns and it is the
number the affordable set below is cut against. It is not derived from
anything.

## 5. The 45 zero-compute items: dispatch these now

45 of 112 approved items cost no compute at all: W8 11, W7 9, W6 8, W5 7,
W3 6, W2 3, W1 1. They are reads of the tree, guard wiring, label fixes,
citation resolution, charter clauses, refits of records that already store
their own rungs, and paper reading.

**They must not be queued behind solves.** They compete for nothing a solver
wants. Three solvers are running now and 13 cores are free; every one of
these 45 can start this minute. Historically this is where the lab loses
time: the refit case is on the record — 6 studies were priced as needing
compute and needed none, and the price is what stopped the work.

## 6. Affordable this week

Budget: 14,132 core-min at the measured 1.40 cores over 7 days, divided by
the 3x planning multiplier of §4.3 = **4,710 core-min of stated cost**,
worked in the agenda's own rank order (`agenda.py`: gain points by source
kind, divided by max(est_core_min, 1.0), descending).

**Affordable: the top 62 of 67 compute items, 4,606.4 core-min stated.**
Plus all 45 zero-compute items, which cost nothing and are not in this
budget.

**Not affordable this week — 5 items, 5,323 core-min, 54% of the backlog:**

| core-min | item | why it is last |
|---|---|---|
| 3,600 | `hlpw6-testcase1-coarse-grid-entry` | rank 67 of 67 on value per core-minute; memory feasibility unestablished by its own text |
| 603 | `agp-4369c99cdd7f` | rank 66; scaled from the bump ladder "with headroom", no headroom stated |
| 420 | `closure-duct-field-inversion` | rank 65; its own basis asks for a timed pilot first |
| 400 | `r4-asymptotic-range-ladders` | rank 63; measured basis, but three constant-ratio rungs on two bodies is an iteration count nobody has estimated |
| 300 | `w5-regrade-every-published-gradient-claim` | rank 64; the case count is not stated |

The ranking puts all five at the bottom on its own arithmetic. That is a
coincidence worth noticing rather than trusting: the heuristic divides by
cost, so expensive items sink whatever they are worth, and `hlpw6` is a
workshop entry whose value is not captured by "challenge = 4 points".

## 7. What actually decides the week

Compute does not. At the measured rate the stated backlog is 4.9 days and
even at 3x it is 62 of 67 items. What decides the week is:

1. **`hlpw6` gets probed before it gets queued**, or it eats 36% of the
   backlog and may not fit in memory at all.
2. **The 45 zero-compute items start immediately** rather than waiting behind
   a solve queue they do not need.
3. **The box stays up.** The lab's measured occupancy is 1.40 of 14 cores.
   The gap is not solver speed; it is time the box spends not solving.
