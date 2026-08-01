# Cost scaling laws per solver family, fitted from the ledger

Fitted 2026-08-01 by `sdk/scripts/fit_cost_scaling.py` from
`demo-output/website/mega-batch/ledger.jsonl`, 208,193 rows. Numbers in
`cost_scaling.json` beside this file. No compute was spent: this reads one
ledger.

**Headline: the bar the lab uses to decide a family's forecasts are
trustworthy is passed by a law with no explanatory power, and this ledger
contains two families that pass it that way.**

---

## 1. What a cost is here, and the rank count

Core-minutes are wall seconds times MPI ranks over sixty. **A law fitted on
wall time is not a cost law until the ranks are stated**, and 59 of the 66
approved compute estimates on the docket state none.

Every row in this ledger is serial. The mega-batch runner invokes every
OpenFOAM family through `workflows/tmr_verification._foam`, which runs
`[*_run_prefix(), *args]` with no `mpirun` and no `-parallel`; the wing and
reduced-order families are single process by construction. So **ranks = 1 on
every row and core-minutes = wall_seconds / 60 throughout this page**. That
equality is a property of this ledger. It does not transfer to a decomposed
run, and the one measurement the lab has of a decomposed run says four ranks
came out 15 percent cheaper in core-minutes than serial while running 4.71x
faster, so the transfer is not even monotone.

## 2. Cleaning, stated rather than assumed

| dropped | rows | why |
| --- | --- | --- |
| torn line | 1 | does not parse; the row it held is lost |
| not ok | 91 | the runner recorded the evaluation as failed |
| above the stall threshold | 6 | over 3600 s, the audit's own threshold; these are the six ~16,300 s rows clustered in two wall-clock windows across two independent solver families, which is a host stall recorded as normal runs |

A law fitted through the stall rows inherits the stall, which is the whole
reason they are named here rather than filtered silently.

## 3. Two laws per family, and they answer different questions

* **A priori.** Wall time as a power law in the design parameters alone, the
  quantities a proposal knows before anything runs. This is the only law that
  can price an unstarted item.
* **A posteriori.** Wall time as a power law in the run's own size, cells and
  iterations. It explains cost and cannot forecast it. It is fitted anyway,
  because the gap between the two measures how much of a family's cost is
  unknowable in advance.

Each fit is trained on the first 80 percent of its family in ledger order and
graded on the last 20 percent, so the grade is on later work rather than on a
random slice of the same afternoon.

## 4. The results

| family | rows | a priori R2 | holdout median error | null median error | skill vs null | longest run within 20% |
| --- | --- | --- | --- | --- | --- | --- |
| `openfoam-cylinder-unsteady` | 417 | **0.972** | **1.9%** | 7.6% | **+75%** | 83 |
| `rhosimplefoam-naca0012-transonic` | 280 | **0.818** | **12.2%** | 34.4% | **+64%** | 9 |
| `openfoam-cylinder` | 69,223 | 0.423 | 47.6% | 53.4% | +11% | 15 |
| `simplefoam-ahmed-3d-viscous` | 35 | 0.336 | 2.3% | **0.5%** | **-338%** | 17 |
| `vspaero-wing` | 69,134 | **0.0002** | 6.0% | **0.13%** | **-4393%** | 6,457 |
| `reduced-order` | 12,817 of 69,007 | 0.000 | 36.0% | 50.0% | +28% | **0** |

"Null" is the constant predictor: the training set's own median wall time,
graded on the same holdout.

## 5. The finding, and it is about the bar rather than about any family

The lab's rule is that a family's forecasts become auto-approvable once three
consecutive predictions land within 20 percent (`scripts/self_audit.py`,
`check_cost_predictions`). Five of the six families clear it.

**`vspaero-wing` clears it 6,457 times in a row with an R2 of 0.0002.** Its
four exponents are 0.003, -0.0003, 0.0011 and 0.0004: the law is a constant
wearing four decorations. It clears the bar because the family's wall time
barely varies, median 5.23 s against a mean of 5.51 s, so *any* prediction near
5 s is inside 20 percent of almost every row. Predicting the family's median
outright is **45 times more accurate** than the fitted law, 0.13 percent
against 6.0 percent.

`simplefoam-ahmed-3d-viscous` does the same thing more quietly: 17 of 17 inside
20 percent, and 4.4 times worse than its own median.

> **A run of predictions inside 20 percent measures the spread of the family,
> not the skill of the law.** The bar is necessary and it is not sufficient,
> and on a family whose cost is nearly constant it is passed by anything.

The fix is one line and it is in the fitter: every law is graded against the
constant predictor on the same holdout, and the list that means something is
`families_whose_law_also_beats_predicting_the_median`. Three families are on
it: `openfoam-cylinder-unsteady`, `rhosimplefoam-naca0012-transonic` and
`openfoam-cylinder`.

**A second, smaller defect in the same check.** Its three recorded pairs for
`pimpleFoam unsteady cylinder` include one labelled "Re 1000 3D pilot, 8
ranks", sitting in the same family as two serial rows. A family that mixes rank
counts is not a like-for-like cost population, and a streak counted across the
mixture is counting two different quantities.

## 6. What the laws actually say

**`openfoam-cylinder-unsteady`, the one family whose cost is genuinely
predictable.** A priori, wall time goes as `Re^0.217` with R2 0.972 and a
holdout median error of 1.9 percent, 83 of 83 inside 20 percent. A posteriori
it is `steps^1.156` with `cells^-0.047`, R2 0.992, median error 0.67 percent.
**Cost is essentially linear in time steps and independent of mesh size within
this family**, which is what an unsteady run with a fixed grid should look
like.

**`rhosimplefoam-naca0012-transonic`.** A priori, `mach^5.76` dominates
everything else: `alpha^-0.085` and `Re^-0.021` are noise beside it. A transonic
solve gets dramatically more expensive as the shock strengthens, and a cost
estimate for this family that does not carry the Mach number is not an estimate.
A posteriori it is `iterations^1.026`.

**Iterations, in both families that record them, carry an exponent of
essentially one: 1.156 and 1.026.** Cost is linear in iterations and the
within-family cell exponents are small, because cells barely vary inside a
family. That is the arithmetic behind the flat-plate overrun: the rung's cells
were priced correctly and its iterations were not, and the iterations are the
term that carries the exponent.

**`openfoam-cylinder`, 69,223 clean rows and still 47.6 percent median error.** The
mesh refinement exponent, 1.78, is the only meaningful one. This family's cost
is not predictable from its design to better than a factor of about 1.5, and
the honest use of that is a band rather than a point estimate.

**`reduced-order` is the only family that fails the bar**, longest run 0, and
it is the cheapest one on the ledger. Its wall times run from 0 to 0.432 s and
are dominated by scheduling noise rather than by arithmetic, so there is no law
to find.

**And 81 percent of its rows have no cost recorded at all.** 56,190 of its
69,007 clean rows carry `wall_seconds` of exactly 0.0, against 12,817 carrying
a positive value up to 0.432 s. That is not timer resolution rounding a
continuum, because the positive values are spread across the whole range rather
than piled just above zero; it is two different paths through the same family,
one of which records nothing. **27 percent of the entire ledger is rows with a
zero cost**, and any throughput figure that divides work by row count, rather
than by measured seconds, is counting them. The published 212.28 core-hours is
unaffected, because zeros add zero. The published 208,102 successful
evaluations is not: a quarter of it cost nothing that was measured.

## 7. What this does not establish

The holdout is the tail of the ledger, not a fresh campaign, so these are
in-corpus grades. None of them has been used to price an item on the docket and
then checked against the run, which is the only test that closes
`check_cost_predictions`. The laws are ready for that; the pairs do not exist
yet.
