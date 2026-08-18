# W3 — the generated-case refinement ladders change knobs between rungs

**2026-08-02, zero solver compute.** Read from the archived case dictionaries
and from the builder that wrote them.

Raised while working `agp-804d7038bf9e`, "Add a fourth refinement rung to the
Ahmed reference body, 25° slant grid ladder", and its four siblings
(`agp-11fa38e9a055` Ahmed 35°, `agp-d0b3c7cb6a58` cube, `agp-e71b0542e6f9`
NACA 0012, `agp-7273e7f80ddc` NACA 0015 sail, `agp-64393439352d` NACA 4412).
All six ask for one more rung on a three-rung ladder. **A fourth rung will not
help, because the three rungs are not one ladder.**

---

## 1. What the archived dictionaries say

Every rung's mesh recipe was read from that rung's own
`system/snappyHexMeshDict` and `system/blockMeshDict`, and every cell count
from that rung's own `constant/polyMesh/owner` header, matched against the
count stored in `models/curriculum/uq-studies/<body>.json`.

| body | rung | cells | background blockMesh | `body { level (…) }` | eMesh level | region level | case |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ahmed_25 | coarse | 20 621 | **(42 9 25)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb` |
| ahmed_25 | medium | 45 753 | **(60 13 36)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-ahmed_25-medium-b37e86` |
| ahmed_25 | production | 79 439 | (60 13 36) | **(3 4)** | **3** | **2** | `/home/ubuntu/certonomous-runs/act7-ahmed_25-b14562` |
| ahmed_35 | coarse | 20 425 | **(42 9 25)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-ahmed_35-coarse-186b41` |
| ahmed_35 | medium | 45 813 | **(60 13 36)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-ahmed_35-medium-d198f3` |
| ahmed_35 | production | 79 778 | (60 13 36) | **(3 4)** | **3** | **2** | `/home/ubuntu/certonomous-runs/act7-ahmed_35-02688b` |
| naca0012_wing | coarse | 27 265 | **(23 42 14)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-naca0012_wing-coarse-09bec1` |
| naca0012_wing | medium | 67 356 | **(33 60 20)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-naca0012_wing-medium-520ccb` |
| naca0012_wing | production | 140 580 | (33 60 20) | **(3 4)** | **3** | **2** | `/home/ubuntu/certonomous-runs/study-naca0012_wing-1021cb` |
| naca4412_wing | coarse | 27 237 | **(23 42 14)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-naca4412_wing-coarse-a6c5e0` |
| naca4412_wing | medium | 67 826 | **(33 60 20)** | (2 3) | 2 | 1 | `/home/ubuntu/certonomous-runs/study-naca4412_wing-medium-337080` |
| naca4412_wing | production | 137 569 | (33 60 20) | **(3 4)** | **3** | **2** | `/home/ubuntu/certonomous-runs/study-naca4412_wing-1af072` |

Read the bold. **The first step of each ladder refines the background mesh and
holds the near-body levels fixed. The second step refines the near-body levels
and holds the background mesh fixed** — medium and production share the
background triple exactly, character for character.

Neither of the two steps is repeated. **No knob moves twice in any of these
four ladders.**

## 2. Why that is disqualifying, and not merely untidy

A pure background change *is* a uniform refinement: snappyHexMesh subdivides
background cells by 2^level, so halving the background cell size halves the
cell size everywhere, in the refined region and the farfield alike, with one
ratio r. That is the ladder the B-52's valid family runs, and it is why
`b52.json`'s `recipe_audit` accepts 135 779 / 193 880 / 255 358 / 330 950 as
extrapolation-comparable.

A pure level change is not. Raising `body { level (2 3) }` to `(3 4)`, the
eMesh level 2 → 3 and the region level 1 → 2 subdivides cells **only at the
surface, along the feature edges, and inside the `nearBody` box.** The
farfield is untouched: its h is identical in the medium and production meshes.
There is therefore no single r for that step — h falls by 2 near the body and
by 1 far from it — and Richardson extrapolation, which is an expansion in one
h, has nothing to expand in.

So each of these four ladders contains **one valid refinement pair and one
step that is not a grid refinement at all.** One valid pair is two rungs, and
two rungs cannot yield an observed order.

Worse for the published surface: **the invalid step is the top one.** The
finest rung — the mesh the act actually solves, the one the credentials wall
prints a cell count for — is the one not connected to the rest of its ladder
by a valid refinement.

## 3. The cause, in the builder, in one line

`sdk/workflows/geometry_study.py`, `refinement_rungs()`:

```python
base = max(2, int(refinement))
medium_level = max(2, base - 1)
coarse_level = max(2, base - 2)
medium = {... "block_scale": 0.85 if medium_level == base else None}
coarse = {... "block_scale": 0.7  if coarse_level == medium_level else None}
```

Every act on this path runs `refinement = 3`. Put 3 in:

* `medium_level = max(2, 2) = 2`;
* `coarse_level = max(2, 1) = 2` — **the floor collapses it onto the medium
  level**;
* so `coarse_level == medium_level` is true and the coarse rung, and only the
  coarse rung, gets `block_scale 0.7`.

The function's own docstring says "Each rung steps the whole level family down
one." **At refinement 3 — which is every act — that is false.** Only one step
down happens; the other rung is manufactured with a different knob entirely.

The docstring is candid about why the second knob is there: "when the floor
would make two rungs identical, the coarser one also scales the
background-mesh divisions so the cell budgets stay distinct; the runtime
cell-count guard still refuses to report a study if they do not."

That is the whole defect in one sentence. The bug being fixed was the B-52
wall lesson — a knob at its floor produced two identical meshes and no study.
The fix made the cell counts distinct, and the guard that was added checks
**distinctness**. Distinctness is not comparability. Two rungs can differ in
every cell and still not be two rungs of one ladder, and nothing downstream
was ever asked whether they were.

## 4. What it did to the fitted orders

Both steps of each ladder are labelled by their cell-count ratio, but only one
of them earns that label.

| body | background step | level step | \|Δ₂/Δ₁\| | fitted p | verdict |
| --- | --- | --- | --- | --- | --- |
| ahmed_25 | r 1.3043, ΔCd −0.011204 | r 1.2019, ΔCd −0.004975 | 0.444 | 1.95 | extrapolation outside measured range |
| ahmed_35 | r 1.3090, ΔCd −0.018453 | r 1.2031, ΔCd −0.006072 | 0.329 | **3.169** | order outside window |
| naca0012_wing | r 1.3518, ΔCd −0.006398 | r 1.2780, ΔCd −0.010237 | 1.600 | **3.173** | order outside window |
| naca4412_wing | r 1.3554, ΔCd −0.001318 | r 1.2658, ΔCd −0.007253 | **5.503** | **10.467** | order outside window |

The NACA 4412 row is the clearest. Its level step has the **smaller** nominal
cell ratio (1.2658 against 1.3554) and moves Cd **5.5 times further**. Fit a
power law to a pair like that and it returns p = 10.467. That number has been
read as a statement about the NACA 4412's convergence. It is a statement about
dividing a near-wall refinement by a farfield one.

The direction differs by body and it differs the way physics says it should:
on the two thin wings the near-body step dominates (ratios 1.600 and 5.503),
on the two blunt Ahmed bodies the farfield step does (0.444 and 0.329). That
consistency is itself evidence that the two steps are measuring different
things rather than the same thing twice.

**The pattern across the corpus.** The two families in this lab that vary only
the background — the B-52's valid family, and the constant-ratio Ahmed 25°
ladder built under R4 — fail on the *behaviour of their increments*: growing
increments, non-monotone. The four two-knob ladders fail on the *order*:
3.169, 3.173, 10.467, and 1.95 with an extrapolation outside its own data.

> **[RESTATED 2026-08-10 under `docs/charters/VERIFICATION_CHARTER.md` §17 — no draw-scatter evidence exists at the rung this feature turns on.]** The statement above is a claim about the SHAPE of a sequence of grid-refinement increments for **the four geometry_study ladders**. Under the adopted rule such a claim is published only with draw-scatter evidence at the deciding rung, or with the absence of that evidence stated on its face. **No replicate mesh has ever been drawn at this ladder's deciding rung.** Recipe class per `campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md`: **CONFOUNDED** — more than one knob moves between its rungs, so its increments were never discretization increments in the first place. This feature is unsupported twice over. **This is not a withdrawal — the feature is unchecked, not shown false**; the remedy the rule specifies is exactly this sentence. Original text retained.


> **CORRECTED 2026-08-02 06:00, by the experiment this section motivated.**
> The sentence that stood here read *"One-knob ladders fail on physics;
> two-knob ladders fail on arithmetic."* **That is wrong and the wing families
> falsified it the same night.** The NACA 0012 built as a genuine four-rung
> single-knob family returns an observed order of **24.048** — further outside
> the window than the 3.173 this audit blamed on the mixed step, on a ladder
> with no mixed step in it. See `W3_WING_VALID_FAMILY_RESULTS.md`; the
> pre-registered prediction P1 was written to be falsifiable by exactly this
> and it was falsified.
>
> What survives is everything in §1–§3: the four ladders *are* two recipes,
> the medium → production step *is* not a uniform refinement, and the cause in
> `refinement_rungs()` is what it is. What does not survive is the claim that
> the mixed step is what makes the orders absurd. Removing it did not make
> them sane. Something common to these flows does that, and the recipe defect
> was **masking** it rather than causing it.

Four of the nine stored ladders' anomalous verdicts have a common upstream
defect. They do not have their explanation.

## 5. What is NOT claimed here

* **cube, NACA 0015 sail, motorBike are not audited.** Only their production
  cases survive on this box (`study-cube-2904cb` 299 493 cells,
  `study-naca0015_sail-fdd45c` 243 929, `study-motorBike-f8b4a2` 353 688, each
  at level (3 4)/eMesh 3/region 2); their coarse and medium cases are gone, so
  the split is *predicted* for cube and the sail by the code path in §3 and is
  consistent with their cell ratios, but it is not read from their own
  dictionaries and it is not asserted. motorBike is on the `familiar=True`
  branch, which returns level (3 4)/(4 5) with `block_scale None` — a pure
  *level* ladder, one knob throughout, and a different defect from this one
  rather than the same one.
* **No verdict is made more flattering.** Every ladder named here was already
  not-conclusive and stays not-conclusive. This audit takes evidence away from
  the fitted orders; it does not hand any ladder a band it did not have.
  `uq.reportable_band` returns None for all of them before and after.
* **No curriculum JSON's `numerical` block is refitted in this pass** and no
  wall row is rebuilt. Refitting would mean fitting on the one valid pair,
  which is two rungs, which is no fit at all; that is a decision about what
  the record should say when a body has no usable ladder, and it belongs with
  the open ruling `w3-a-declined-ladder-still-publishes-an-envelope` rather
  than in a rung item. **What the four `recipe_audit` blocks added alongside
  this file do is record which rungs are comparable, exactly as `b52.json`
  already does. Nothing else moves.**

## 6. What the six rung items should actually be

Adding a fourth rung to `coarse / medium / production` extends a mixed
sequence by one and returns a fourth number to fit across the same broken
step. What each body needs instead is what R4 built for the Ahmed 25°:

**two further rungs above the production mesh at the production recipe,
varying only the background blockMesh divisions, at a constant ratio** — which
with the production rung makes a genuine three-rung single-knob family.

That construction is proven on this box. R4 built it for the Ahmed 25° at
79 439 / 144 240 / 254 911 / 454 691 cells, h-ratios 1.2200 / 1.2090 / 1.2128,
and it cost 6.2 core-minutes for the first three rungs at 4 ranks
(`R4_ASYMPTOTIC_RESULTS.md` §cost). It also came back **non-monotone**, so a
valid ladder is not a promise of a conclusive one — which is the honest thing
to say before building three more of them.

**The Ahmed 25° item `agp-804d7038bf9e` is therefore already answered on the
measurement**, by rungs that exist: its valid production-recipe family is
79 439 / 144 240 / 254 911 / 454 691 at Cd 0.084801801 / 0.079359699 /
0.073992743 / 0.074882228, and it is non-monotone. R4's re-solve of the
production rung (0.084801801) sits 1.05 × 10⁻⁵ from the stored value
0.08481225252258064, inside the measured 1.23 × 10⁻⁵ run-to-run floor, which
is the cross-check that R4's family and the stored production rung are the
same setup.
