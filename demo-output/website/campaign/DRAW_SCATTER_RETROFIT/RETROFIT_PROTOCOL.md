# Draw-scatter retrofit — SHARED PROTOCOL, binding on both halves

**Verification Charter §17 retrofit. Written 2026-08-10 before any retrofit mesh
exists.** Split ruled by the chief: **Cases family — `ahmed_25`, `ahmed_35`,
`motorBike`**; **DAFoam family — `naca0015_sail`, `cube`**.

**This document is the transmission channel for the conventions the chief asked
me to pass on, and for three pre-flight findings that change the campaign for
BOTH halves. Read it before meshing anything.**

---

## 1. THE BAR CONVENTION — the one that matters most

> **The bar is fixed before the number exists, and calibrated by SIMULATION
> against the null, never chosen.**

**Use the shared module — do not reimplement it.** `scatter_bar.py`, in this
directory:

```python
from scatter_bar import calibrate, classify
bar = calibrate(n=4)                 # fixed seed 20260810 -> identical bar for both agents
v   = classify(draws, bar, published_index=0)
```

**One implementation, because two implementations of a calibration are two
things that can disagree about what was calibrated** — the same reasoning that
put every lever echo behind one predicate today. The seed is fixed so both halves
derive the *same* bar rather than two bars that happen to agree.

**The precedent, and the standard it sets:** on Ahmed 25° c3 the bar was the 10th
percentile of the null (`R ≤ 0.28`). The measured `R` came in at **0.324 — the
14.6th percentile, a near miss.** It was **reported as a near miss and the bar
was not touched.** Had the bar been the 15th percentile the verdict would have
flipped from B3 to B2, and saying so is the point.

> **A stated false-positive rate is worthless if the threshold moves after the
> draws land.** Report near misses as near misses. Five ladders graded to two
> conventions are worth less than three graded to one.

## 2. PRE-FLIGHT FINDING A — `R` has essentially NO POWER at n = 3

The retrofit buys **n = 3** (1 published draw + 2 new). Calibrated against the
null:

| n | `R_bar` (10th pct) | null median |
| --- | --- | --- |
| **3** | **0.0754** | 0.365 |
| 4 | 0.2722 | 0.594 |
| 5 | 0.4142 | 0.686 |

**At n = 3 you would need the two surviving draws to be nearly identical to
declare outlier-dominated.** `R` must **not** be the deciding statistic at n = 3.
Compute and report it; do not grade on it.

> **The deciding statistic is the INCREMENT-MOVEMENT test** — the one that
> actually decided both the B-52 and the Ahmed:
>
> replace the rung's single published draw with the **mean of its draws**,
> recompute the increment, and compare:
>
> | branch | criterion |
> | --- | --- |
> | **SURVIVES** | within 25% of the published increment **and** same sign |
> | **DISSOLVES** | below 50% of it, **or** the sign flips |
> | **PARTIAL** | between |
>
> Also report **where the published draw sits in its own distribution** — but at
> n = 3 an extremum has prior probability 2/3 under no selection at all, so it is
> reported, never graded.

**This finding is now written into Verification Charter §17 itself** (correction of 2026-08-10), so it binds whoever runs the next retrofit rather than living only in one arm's report.

## 3. PRE-FLIGHT FINDING B — a RECIPE AUDIT must precede the draws, and it is free

**A ladder whose rungs use different mesh recipes is not measuring discretization
at all** — its increments confound the recipe change with refinement. Drawing
replicates on such a ladder measures the scatter of a quantity that was never an
increment. The charter already holds the sibling rule: *a recipe audit precedes
an order* (§ "A recipe audit precedes an order").

**Measured, zero compute, on the five approved ladders:**

| ladder | `recipe_audit` | status |
| --- | --- | --- |
| `ahmed_25` | *"the three stored rungs are TWO mesh recipes, and no knob moves twice"* | **RECIPE-INVALID — do not draw** |
| `ahmed_35` | *same finding* | **RECIPE-INVALID — do not draw** |
| `motorBike` | **ABSENT** | audit required before drawing |
| `cube` | **ABSENT** | audit required before drawing |
| `naca0015_sail` | **ABSENT** | audit required before drawing |

**Consequence for both halves: three of the five approved ladders have never had
a recipe audit, and the other two FAILED one.** Every arm's first act is a
zero-compute recipe audit; only single-recipe ladders proceed to draws.

**Consequence for `ahmed_25` / `ahmed_35` (Cases half): the honest disposition is
RESTATE ON RECIPE GROUNDS, at zero compute, not a draw-scatter measurement.**
Their shape claims are already unsupportable for a reason that predates this
rule, and spending draws on them would measure the wrong quantity. Reported to
the chief as an under-spend of approved budget with the reason stated.

## 4. THE CERTIFICATION GATE (chief ruling, applies per ladder, priced separately)

**Every mesh is certified at the gate BEFORE any solve**, per ladder, priced as
its own line and **not absorbed into the 12.8–21.7 core-min**. Both M6 members
the DAFoam family touched today were **quarantined with no birth certificate at
all** until minted; the curriculum ladders have never been through that gate and
are likely in the same state.

**Two chief rulings, so neither half decides them mid-campaign:**

1. **A mesh returning `broken` is a FINDING, not a delay.** Report immediately
   and **stop that ladder**. A born-broken mesh under a published ladder feature
   outranks the scatter measurement it interrupts.
2. **A ladder whose meshes cannot be certified at all is reported as
   *UNVERIFIABLE AT SOURCE*** — not forced into restate or withdraw. **That third
   outcome must stay available or the rule manufactures verdicts it has not
   earned.**

## 5. What each arm reports, per ladder

| field | |
| --- | --- |
| **certification** | every mesh's verdict; `broken` → stop and report |
| **recipe audit** | single-recipe or not; not-single → RESTATE on recipe grounds, no draws |
| **bar** | `r_bar`, `n`, stated false-positive rate, from `scatter_bar.calibrate` |
| **scatter measured** | `s` at the deciding rung, and `s` excluding the extreme |
| **verdict** | increment-movement branch (SURVIVES / DISSOLVES / PARTIAL); `R` reported, not graded at n = 3 |
| **disposition** | the published feature **RESTATES**, **WITHDRAWS**, or is **UNVERIFIABLE AT SOURCE** |
| **cost** | measured, with certification as its own line |

## 6. Gates carried from the B-52 and Ahmed arms

**G1** delivered cell count within ±2.0% of the published rung, decided **before
any solve**; re-draw allowed, every refused attempt recorded, ≤2 re-draws; if the
allowance is exhausted the shortfall **is** the result and is not extended.
**G2** birth certificate written at creation, `certificate_admits` before launch.
**G3** the rung's own convergence rule met. **G4** lever echo.
**Rank count fixed** across a family — varying it injects a decomposition
artifact into the quantity being measured.

**Mesh-first screening is recommended and was measured to pay for itself:** mesh
several candidates (cheap), admit on delivered cells, solve only the admitted
ones. On Ahmed leg 1 this was not done and a third of the spend bought refusals;
on leg 2 it was, and 5 of 5 candidates were admitted.
