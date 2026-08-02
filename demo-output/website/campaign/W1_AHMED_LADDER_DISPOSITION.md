# W1 — the Ahmed asymptotic ladder: half of it is already answered, and the half that is not was never priced

Approved item `w1-ahmed-family-asymptotic-ladder`, estimated **240
core-minutes**. Ruled 2026-08-02 at **0 core-minutes**: no solver was launched.
Every number below is read off a committed record on this box.

The item's gate: *"An observed order inside the theoretical range on a mesh
family refined uniformly, **for at least one slant**."*

**Ruling: the 25° slant is answered — in the negative, on measurement — and the
item is re-scoped to the 35° slant and re-priced from 240 core-minutes to
about 27.**

---

## 1. The 25° slant: attempted, and refused on evidence

`r4-asymptotic-range-ladders` (W3, done, 400 core-minute estimate) ran exactly
the experiment this item asks for, on the 25° slant, and its result is
`campaign/R4_ASYMPTOTIC_RESULTS.md`, pre-registered before any solve in
`R4_PREREGISTRATION.md` (committed `6cdf8a41`).

Five rungs, **one mesh recipe**, the background blockMesh division triple the
only knob — which is a genuinely uniform refinement, since snappyHexMesh
subdivides background cells by `2^level` and one ratio scales `h` everywhere.
Four MPI ranks on every rung, scotch, identical across rungs.

| rung | cells | cells/rank at 4 ranks | Cd | increment |
| --- | --- | --- | --- | --- |
| c1 | 79,439 | 19,860 | 0.084801801 | |
| c2 | 144,240 | 36,060 | 0.079359699 | −5.442e-03 |
| c3 | 254,911 | 63,728 | 0.073992743 | −5.367e-03 |
| c4 | 454,691 | 113,673 | 0.074882228 | **+8.895e-04** |
| c4b (replicate control) | 468,509 | 117,127 | 0.074979080 | |
| c5 | 834,351 | 208,588 | **refused** — 4,000 iterations, never converged | |

Three findings, all measured:

- **The first two increments are equal to within 1.4%.** Equal increments under
  uniform refinement are the signature of `p ≈ 0`; the fit on (c1, c2, c3)
  returns **p = 0.175**, outside the credible window [0.5, 2.5], and its
  Richardson extrapolation is **−0.0845 — a negative drag coefficient**.
- **The fourth rung turns around.** On (c2, c3, c4), or on all four,
  `uq.eca_hoekstra_band` returns `monotone: False` and refuses an order at all,
  with `not_conclusive_reason` *"the three rungs do not move one way under
  refinement."*
- **The sixth rung stops converging.** Iterations to convergence run 158, 212,
  220, 623, 1668 — and then c5 does not converge in 4,000, with a final-window
  2σ of 5.2e-03, **6.26% of its own value and six times the ladder increments
  this whole study is made of**. It is struck from the ladder by the lab's own
  rule, at a measured cost of **267.4 core-minutes on 4 ranks** (208,588
  cells/rank).

R4 §6 rules on it in its own words: *"refining this ladder further is not the
way to settle the Ahmed body. The next rung costs more and converges less. The
question is a formulation question — steady versus unsteady — not a grid
question, and no amount of the item's remaining budget would have answered
it."*

The item's rationale calls the body "3D separated flow with a documented
bistable wake". R4's hypothesis — stated there as a hypothesis, and repeated
here as one — is that the 25° slant sits on the drag crisis where the C-pillar
vortices and the slant separation bubble trade places, so finer meshes resolve
more of an unsteadiness the steady formulation is not allowed to have, and the
ladder is *"converging towards a solution the steady equations do not
possess"*.

**Nothing this item could buy would change that.** Its gate cannot be met on
the 25° slant by refinement, and spending its 240 core-minutes there would
re-run an experiment that is already on the record with a pre-registration in
front of it.

---

## 2. The 35° slant: not answered, and its stored ladder was invalidated today

R4 ran the 25° slant only. The 35° slant's stored three-rung ladder in
`models/curriculum/uq-studies/ahmed_35.json` reports `observed_order: 3.169`,
`monotone: true`, clamped to 2.5, not conclusive on `order_window`.

**That number is a fit over a family whose top step is not a refinement.**
The W3 recipe audit committed today (`cb7025c6`) reads each rung's own
`snappyHexMeshDict`, `blockMeshDict` and `polyMesh/owner` and finds, on
`ahmed_35` as on `ahmed_25`, `naca0012_wing` and `naca4412_wing`:

> coarse → medium refines the background blockMesh and holds the near-body
> levels fixed; medium → production refines the near-body levels … and holds
> the background blockMesh **IDENTICAL**.

A background change scales `h` everywhere and has a single `r`. A level change
refines only at the surface, the feature edges and inside `nearBody`, and
leaves the farfield `h` untouched, so **no single `r` exists for that step**.
The invalid step is the top one — the finest rung, the mesh the act solves, is
the rung not connected to its ladder.

So the 35° slant has **no valid uniform ladder at all**, and its `p = 3.169` is
not evidence for or against the gate. This is the half of the item that is
genuinely open, and it is open for a reason nobody had recorded until today.

**Whether it is doomed like the 25° is not known, and there is a physical
reason to expect otherwise.** The 25° slant is marginal precisely because it
sits *on* the drag crisis. The 35° slant is past it, with the flow fully
separated off the slant — a regime a steady formulation has a better claim to.
That is a reason to try, not a prediction, and it is written here before
anything runs.

---

## 3. Re-pricing, from measurement rather than from a default

The item carries **240 core-minutes**. R4 measured the identical four-rung
experiment on the identical body at the identical rank count:

| stage | ranks | cells/rank | measured |
| --- | --- | --- | --- |
| meshing, c1+c2+c3 concurrent | 1 each | — | 1.21 core-min |
| c3 re-mesh + c4 meshing | 1 each | — | ≈2.6 core-min |
| c1 solve | 4 | 19,860 | 0.84 core-min |
| c2 solve | 4 | 36,060 | 2.00 core-min |
| c3 solve | 4 | 63,728 | 3.39 core-min |
| c4 solve | 4 | 113,673 | 16.74 core-min |
| **four rungs and their meshes** | | | **≈26.8 core-min** |

**About 27 core-minutes, not 240** — a factor of nine. Four ranks is the right
count and stays: the smallest rung is 19,860 cells/rank, comfortably above the
5,600 cells/rank inversion point, and the largest is 113,673.

R4 recorded why its own 400 was wrong, and it applies verbatim here: the
estimate's basis was *"the B-52's own 1,267-second and motorBike's
1,022-second rebuild times"*, i.e. it was priced on **mesh generation for a
different body**, and the Ahmed body meshes in about 15 seconds a rung. R4
called that "a fact about the estimator, not only about this item". This is the
second item to be caught by it.

---

## 4. Two things this ruling hands to other people rather than doing

**A collision to name, not to resolve.** `agp-11fa38e9a055` (W3, approved, 20
core-minutes) is "Add a fourth refinement rung to the Ahmed reference body, 35°
slant grid ladder". Adding a *fourth* rung to the stored 35° ladder inherits
the defect W3 itself found this morning: the existing third step is not a
refinement, so a fourth rung extends a family that has no single `r` across its
top. The fix is not a fourth rung, it is a rebuilt family on one recipe with
one knob, which is what this item now is. **W3 holds that item and this note
does not touch it.**

**A successor R4 earned and nobody filed.** R4 §6 names the next question in
plain words — steady versus unsteady — and no item anywhere in the docket asks
it. Searching every proposal for "ahmed" returns the two slant-validation
items, two rung-adding items, and this one; none is an unsteady formulation.
**Filed today as `w1-ahmed-25-unsteady-formulation`**, HARD on criteria 1 and 3,
priced from R4's own measured rungs rather than from a default.

---

## Related

- `demo-output/website/campaign/R4_ASYMPTOTIC_RESULTS.md` §3, §6, §9.
- `demo-output/website/campaign/R4_PREREGISTRATION.md`, committed before the solves.
- `demo-output/website/campaign/W3_LADDER_RECIPE_AUDIT.md` and commit `cb7025c6`.
- `models/curriculum/uq-studies/ahmed_25.json`, `ahmed_35.json`, `recipe_audit`.
