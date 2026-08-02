# W3 — where the mesh-generation noise floor bites: results

**Meshed and solved 2026-08-02 06:04:01 → 06:07:50 UTC**, plus a B-52
replicate 06:00:38 → 06:07:xx. Pre-registration:
`W3_MESH_NOISE_FLOOR_PREREGISTRATION.md`, commit 438de17c, written before any
of the six replicates was built.

---

## 1. The measurement

Each replicate is byte-identical to its twin except for the background
blockMesh division triple — verified by `diff -r` on `system/` and `0.orig/`
and by md5 on the STL, and the only line that differs is the `hex (…)` one.
All twelve wing solves ran at 4 MPI ranks, scotch, and stopped on
`residualControl`.

### NACA 0012 finite wing

| rung | cells A | cells B | cell Δ | Cd A | Cd B | **scatter** | increment into this rung | scatter / increment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1 | 140 545 | 139 621 | −0.66% | 0.012052229 | 0.009453575 | **2.599 × 10⁻³** | −1.646 × 10⁻³ | **1.58×** |
| r2 | 224 431 | 223 641 | −0.35% | 0.010405872 | 0.009293550 | **1.112 × 10⁻³** | −1.646 × 10⁻³ | 0.68× |
| r3 | 358 430 | 362 032 | +1.00% | 0.008479216 | 0.008072766 | **4.064 × 10⁻⁴** | −1.927 × 10⁻³ | 0.21× |
| r4 | 525 692 | 534 106 | +1.60% | 0.008435098 | 0.008255182 | **1.799 × 10⁻⁴** | −4.412 × 10⁻⁵ | **4.08×** |

### NACA 4412 finite wing

| rung | cells A | cells B | cell Δ | Cd A | Cd B | **scatter** | increment into this rung | scatter / increment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1 | 137 569 | 132 592 | −3.62% | 0.021671412 | 0.022686094 | **1.015 × 10⁻³** | −1.173 × 10⁻³ | 0.87× |
| r2 | 213 918 | 209 402 | −2.11% | 0.020498598 | 0.020478014 | **2.058 × 10⁻⁵** | −1.173 × 10⁻³ | 0.02× |
| r3 | 340 996 | 344 402 | +1.00% | 0.018966957 | 0.019202179 | **2.352 × 10⁻⁴** | −1.532 × 10⁻³ | 0.15× |
| r4 | 518 748 | 561 528 | +8.25% | 0.021940394 | 0.018689055 | **3.251 × 10⁻³** | +2.973 × 10⁻³ | **1.09×** |

## 2. The predictions, scored

**P1 — "the scatter grows with cell count; r4b largest, r1b smallest" — FALSE,
and on the NACA 0012 exactly backwards.** Its scatter falls monotonically,
2.599 × 10⁻³ → 1.112 × 10⁻³ → 4.064 × 10⁻⁴ → 1.799 × 10⁻⁴, a factor of 14.45
across a factor of 3.74 in cells. The reasoning I wrote down — more snapped
cells means more independent decisions that can go differently — predicted the
wrong sign. The 4412 does put its largest scatter at r4, so it half-supports
P1, but its smallest is at r2 and its r1 is not the smallest either. **P1 is
scored FALSE.**

**P2 — "the r1 and r2 scatters are each below 20% of the increment spanning
them" — FALSE, on both bodies, at r1.** The 0012's r1 scatter is **158%** of
the increment and its r2 scatter 68%; the 4412's r1 scatter is 87%. Only the
4412's r2, at 2%, meets the bar P2 set.

P2 carried a stated consequence: *"If this fails, the ladders were never
measuring discretization at any rung."* That is too strong for what the data
say and it is corrected here rather than asserted. The 4412's r2 and r3, and
the 0012's r3, are clean at 2%, 15% and 21%. **What is true is narrower and
worse-placed: the scatter exceeds or rivals the increment at the COARSEST
rung on both bodies** — and every three-rung ladder stored in this lab puts
two of its three rungs at or below that resolution.

**P3 — "the r3 scatter is below the r2→r3 increment on both wings" — TRUE.**
21% on the 0012 and 15% on the 4412.

One of three, again, and the one that held is the least interesting of the
three. That is what pre-registration is for.

## 3. What the numbers actually say

**On the NACA 0012 the scatter follows an inverse-square law in cell count,
and it is not close.** Multiply each scatter by N²:

| N | scatter | scatter × N² / 10⁹ |
| --- | --- | --- |
| 140 545 | 2.599 × 10⁻³ | 0.051 |
| 224 431 | 1.112 × 10⁻³ | 0.056 |
| 358 430 | 4.064 × 10⁻⁴ | 0.052 |
| 525 692 | 1.799 × 10⁻⁴ | 0.050 |

Constant to ±6% over a 3.74× range. The fitted exponent is **2.024**.

> **CORRECTED 2026-08-02 07:18, by four meshes per resolution instead of
> two.** Every scatter in the table above is **a single pairwise difference**
> — one replicate against one original at each resolution. Running four meshes
> at each of two resolutions on this same body
> (`W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md` §6) gives a different answer:
>
> | statistic, r1 → r3 | ratio | implied exponent |
> | --- | --- | --- |
> | the single pair used above | 6.40 | **1.98** |
> | 4-mesh range | 3.93 | **1.46** |
> | 4-mesh standard deviation | 3.77 | **1.42** |
>
> A range over n = 4 and a single pairwise difference are different statistics
> and are not directly comparable, so 2.024 is not wrong on its own terms. But
> **the exponent is not pinned down, and "scatter × N² constant to ±6%" was
> four single draws flattering themselves into a law.** The robust claim is
> that scatter falls with refinement on this body somewhere around N⁻¹·⁴ to
> N⁻², and the tidy inverse square should not be carried forward as
> established. The direction — falling, not rising — is unaffected, and that
> was the part that mattered. Four
points is four points and this is one geometry, so it is a description and not
a law — but it is a very clean description, and it says something concrete:
**mesh-construction scatter on this body is a coarse-mesh problem that
refinement cures, not a fine-mesh problem that refinement causes.**

**So the r4 failure was never about the scatter growing.** The 0012's scatter
at r4 is the smallest it has ever been, 1.799 × 10⁻⁴. The reason
`scatter / increment` blows up to 4.08× there is that **the increment
collapsed**, from 1.927 × 10⁻³ to 4.412 × 10⁻⁵, a factor of 44 in one step.
The ladder ran out of signal; the noise did not catch up with it. The p =
24.048 in `W3_WING_VALID_FAMILY_RESULTS.md` is still an artefact and that
conclusion is unchanged — but the mechanism stated there ("the mesh generator
does not build the same mesh twice, and above 350 000 cells the difference
exceeds what refinement buys") is only half right, and the half that is wrong
is the direction. Corrected here.

**The NACA 4412 does not follow the same law.** Its scatters are 1.015 × 10⁻³,
2.058 × 10⁻⁵, 2.352 × 10⁻⁴, 3.251 × 10⁻³ — no monotone trend, spanning a
factor of 158 with the worst at the finest rung. The one structural difference
on the record is that its r4 mesh carries a max skewness of 3.165 against 1.49
to 1.90 on its three coarser rungs. So whatever regularity the 0012 has, the
4412 does not share it, and a single N⁻² correction applied corpus-wide would
be wrong on this body. **Two geometries, two behaviours. Nothing here
generalizes to a third without measuring it.**

**The coarse rung is the dangerous one.** This is the finding with the widest
reach. Every stored three-rung ladder in this corpus sits at roughly 20 000 to
300 000 cells, and at 140 000 cells — the finer end of that range — an
independently generated mesh moves the NACA 0012's drag by 2.599 × 10⁻³, which
is 21.6% of the value and 158% of the next refinement step. The lab has been
fitting orders of accuracy, and publishing envelopes, on rungs where mesh
construction moves the answer further than refinement does.

## 4. The B-52's turn, re-checked

`B52_RUNG7_RESULTS.md`, committed at db89139c earlier tonight, reported the
B-52's ladder turning at 441 057 cells on a −4.055 × 10⁻³ increment. The
replicate:

| | cells | Cd |
| --- | --- | --- |
| rung7 | 441 057 | 0.048220173 |
| rung7b | 441 079 | **0.050134753** |

**Cell counts 22 apart — 0.005%.** As close to the same resolution as this
generator gets, and the drags are **1.9146 × 10⁻³ apart, 47% of the increment
the turn consists of.**

**The verdict survives; the magnitude does not.** Both replicates fall below
finer2's 0.052275 — rung7 by −4.055 × 10⁻³, rung7b by −2.140 × 10⁻³ — so the
sign of the turn is reproduced, and refitting the five-rung family on rung7b
instead of rung7 gives the same verdict field for field: `monotone` false, no
observed order, held by `monotone`, `reportable_band` None. Only `band_abs`
moves, 0.00506853 → 0.00337750.

So the B-52's finding stands as published, with one number attached that was
not there before: **the turn is −4.055 × 10⁻³ ± 47% from mesh construction
alone**, on a body whose iterative noise at the same rung is 3.584 × 10⁻⁵.
The mesh scatter is **53 times** the iterative scatter at that rung. The
`iterative_audit` this record has carried since 2026-07-31 measured the
smaller of the two noise sources by two orders of magnitude, and nothing was
measuring the larger one.

## 5. What should change

1. **A ladder should carry a measured mesh scatter, and a fit should refuse an
   increment below it.** That is `w3-a-ladder-refined-below-its-own-mesh-noise`
   and this measurement is what it was proposing to make. The measurement is
   cheap — 27 core-minutes bought nine replicate points on three bodies — and
   `uq.eca_hoekstra_band` cannot infer it from a cell-count and value series.
2. **The refusal has to be per-rung, not per-ladder.** The 0012's r3 is clean
   at 21% and its r1 is not, at 158%. A single per-body number would throw away
   the good rungs or keep the bad ones.
3. **A replicate at the COARSEST rung is the one to run first**, which is the
   opposite of where I put mine. All three replicates run before tonight — R4's
   c4b and both wing r4b's — were at the finest rung, because that is where the
   verdict looked fragile. On the 0012 the finest rung is where the mesh is
   *most* reproducible.

## 6. Cost

| stage | ranks | measured |
| --- | --- | --- |
| six wing replicates, mesh | 1 each, 3 concurrent | ≈6 core-min |
| six wing replicates, solve | 4 | 255.34 s ExecutionTime, **17.02 core-min** |
| B-52 rung7b, mesh + serial steps | 1 | ≈1.5 core-min |
| B-52 rung7b, simpleFoam | 2 | 271.04 s ExecutionTime, **9.03 core-min** |
| **total** | | **≈33.6 core-minutes** |

Estimated at 20–25 core-minutes for the six wing replicates in the
pre-registration; measured 23.0 for that part, inside the range. The B-52
replicate was not in that estimate and was added on the strength of §5 of
`W3_WING_VALID_FAMILY_RESULTS.md`, which named it as the cheapest experiment
on the board at "about 12 core-minutes"; it cost 10.5.
