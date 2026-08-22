NOT FILED — draft for Sanaa's decision

# Bug report: `viewFactorsGen` view factors do not sum to 1 over a closed enclosure — up to +4.4 % on a concave patch, and the error does not shrink with mesh refinement

**Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been
contacted, nothing has been posted.** This document is prepared to be filed
against `OpenFOAM` (ESI / openfoam.com), utility
`applications/utilities/preProcessing/viewFactorsGen`. **Whether it is sent is
Sanaa's call, not the lab's.** It is **candidate #4** in
`docs/upstream/UPSTREAM_QUEUE.md`.

**NOT SUBMISSION-READY.** One thing is missing and it is not optional: **no
novelty search has been done.** Candidates #1–#3 each carry a recorded sweep of
issue trackers, forums and mailing lists establishing that the defect is
unreported. This one carries none. Nobody has checked whether this is already
an open issue, already fixed on a development branch, or already discussed on
cfd-online. **It must not be filed until that check exists.** Everything below
is complete and reproduced; the gap is provenance, not evidence.

---

## The claim, in one sentence

`viewFactorsGen` regularises the coincident-edge singularity of its 2LI
double-contour integral by substituting `r -> alpha*|s_i|` with a default
`alpha = 0.21`, where the substitution is exact only at
`alpha = exp(-3/2) = 0.223130160148...`, and the resulting error
`-(2 ln alpha + 3)/(4 pi) = +0.0096524` is **independent of mesh size** and is
added to `F_ij` once for every mutually-visible edge-sharing neighbour of the
emitting face — so on a concave patch, where all four edge neighbours are
visible, every row of the view-factor matrix is wrong by **+3.9 %** at every
resolution.

## Version

```
Using: OpenFOAM-2606 (2606) - visit www.openfoam.com
Build: _481094f-20260618
Arch:  LSB;label=32;scalar=64
```

Installed at `/usr/lib/openfoam/openfoam2606`. The source is present and the
line numbers below are from that tree.

---

## The invariant being violated

For **any closed enclosure of opaque surfaces**,

```
    sum_j F_ij = 1        for every face i,  whatever the mesh.
```

This is closure, not a modelling approximation. It stays exact when a sphere is
faceted into flat quads: a closed polyhedron is still closed. It needs no
reference solution, no analytic case and no experiment to check.

## Minimal reproducer

`verification/runs/T-family/T10aVF_runs/reproducer/` — four cases,
`blockMesh` only (**no snappyHexMesh, no external mesh, no solver, no solution
time directory**), five small text files each, plus `Allrun` and a stdlib-only
`rowsum.py`. Runs in **~15 core-seconds**.

```
./Allrun
```

### Expected output (`sum_j F_ij` must be exactly 1 everywhere)

| case | patch | mean rowSum | min | max | mean err % |
| --- | --- | ---: | ---: | ---: | ---: |
| `box` — closed cube 16x16 per wall, `alpha` = 0.21 (default) | each of 6 walls | **1.003755** | 1.000622 | **1.019234** | +0.3755 |
| `box_alphafix` — same mesh, `alpha` = exp(-3/2) | each of 6 walls | 1.001342 | 0.999929 | 1.002769 | +0.1342 |
| `sphere` — concentric spheres r=0.05/0.1, `alpha` = 0.21 (default) | `inner` (convex) | 1.003081 | 1.000747 | 1.004822 | +0.3081 |
| | `outer` (**concave**) | **1.040255** | 1.036839 | **1.044022** | **+4.0255** |
| `sphere_alphafix` — same mesh, `alpha` = exp(-3/2) | `inner` | 1.003081 | 1.000747 | 1.004822 | +0.3081 |
| | `outer` | 1.000994 | 0.997967 | 1.004899 | +0.0994 |

Reproduced twice from clean, identical to the last digit shown.

**You do not need `rowsum.py` to see this.** With `writeViewFactorMatrix true`
the utility writes its own per-face row-sum field to `0/viewFactorField`
(`viewFactorsGen.C:1200-1243`). For the `sphere` case it contains, on the
concave patch, mean **1.0402552**, min 1.0368391, max 1.0440224 — the same
numbers. `viewFactorsGen` reports the violated identity itself.

Two numbers carry it:

* `box` **max = 1.019234**, on exact cube geometry with no curvature and no
  faceting error of any kind. A corner face of a cube wall has exactly **two**
  edge-sharing neighbours it can see, across the two box edges it lies on, and
  `0.019234 = 2 x 0.009617`.
* `sphere` `outer` **mean = 1.040255**. A face on a concave sphere sees **four**
  edge neighbours, and `0.040255 = 4 x 0.010064`.

The `inner` patch is the built-in control: it is convex, so no face on it sees
any of its own edge neighbours, `alpha` is never exercised, and its rows are
**bit-identical** between `sphere` and `sphere_alphafix`.

---

## Root cause

`applications/utilities/preProcessing/viewFactorsGen/viewFactorsGen.C`:

1. **line 969** — a face pair with `dist <= distTol` (default 8 equivalent
   radii) goes to the 2LI double-contour branch. Two faces sharing an edge sit
   at `dist = 2/sqrt(pi) = 1.128` and always do.
2. **lines 1054-1058** — inside the 2LI edge double loop, an edge pair whose
   midpoints coincide has `quadOrder` forced to 0 **whatever the outer Gauss
   order `gi` is**. For two faces sharing an edge that pair is exactly the
   shared edge, traversed in opposite senses, so `cos_ij = -1` and the term is
   the dominant, singular one.
3. **lines 386-394** — at order 0, `GaussQuad` evaluates

   ```
   dIntFij = max(cosij * log(r&r) * magSi * magSj, 0);   with  r = alpha*magSi*di
   ```

   i.e. `cos_ij * L^2 * 2 ln(alpha L)`.

The exact self-edge contour integral over a segment of length `L` is

```
    int_0^L int_0^L ln((s-t)^2) ds dt  =  L^2 * (2 ln L - 3)
```

so the substitution is exact **iff `2 ln(alpha) + 3 = 0`, i.e.
`alpha = exp(-3/2) = 0.223130160148...`.** After the `1/(4 pi A_i)`
normalisation at lines 1096-1097, with `A_i = L^2` for a square face, the
residual added to `F_ij` is

> **`e(alpha) = -(2 ln alpha + 3) / (4 pi)`**, per mutually-visible
> edge-sharing neighbour — **a pure number, with no `h` in it.**

`e(0.21) = +0.0096524`.

Two further remarks on the same lines, **stated as observations, not as part of
the claim**:

* The value is documented inconsistently in the file itself: the header at
  **line 45** gives `alpha 0.22`, while the code default at **line 483** is
  `0.21`. Neither is `exp(-3/2)`; `0.22` would still leave `+0.90 %` on a
  concave patch.
* The `max(..., 0)` clip at line 394 applies only to the order-0 branch and
  would silently discard a legitimately negative contribution whenever
  `alpha*|s_i| > 1` (i.e. faces of edge length above ~4.8 m at the default).
  Not exercised by any case here.

---

## Evidence

### 1. It does not converge — concentric spheres, identical settings

| radiative faces | `outer` (concave) mean rowSum | excess | `inner` (convex) mean rowSum |
| ---: | ---: | ---: | ---: |
| 768 | 1.0340923 | +3.41 % | 0.9893824 |
| 1728 | 1.0402552 | +4.03 % | 1.0030814 |
| 3072 | 1.0403450 | +4.03 % | 1.0019404 |
| 4800 | 1.0395530 | +3.96 % | 1.0012772 |

A **6.25x** span of face count. The concave-patch error does not decrease — it
is not even monotone. On the same meshes the convex patch converges as
`O(h^1.6..1.9)`, which is what an ordinary faceting/quadrature error looks like.
Three further resolutions from a separate mesh family (600 / 1536 / 4056 faces)
give +4.10 / +4.03 / +3.96 %.

Summing the *edge-sharing entries alone* and subtracting their
`alpha = exp(-3/2)` values on the same mesh gives **0.03925, 0.03926, 0.03926,
0.03925** across those four resolutions — constant to four digits while the
face count changes 6.25-fold, and accounting for **99.2 %** of the row excess at
the finest level.

### 2. It follows the geometry's edge count, not its curvature

`n_ev` = mean number of edge-sharing neighbours the emitting face can actually
see.

| geometry | patch | `n_ev` | mean excess | patch max excess |
| --- | --- | ---: | ---: | ---: |
| solid sphere, one patch | fully concave | 4.000 | **+4.06 %** | +4.39 % |
| concentric spheres | `outer`, concave | 4.000 | **+4.03 %** | +4.40 % |
| closed cylinder | `side` — concave circumferentially, **flat axially** | 2.254 | **+2.75 %** | +4.14 % |
| closed cylinder | `ends`, flat | 0.250 | +0.48 % | +3.37 % |
| closed cube | any wall, flat | 0.250 | +0.38 % | **+1.92 %** |
| concentric cubes | `inner`, convex | 0.000 | +0.23 % | +0.40 % |

The cylinder is the sharpest test: a curved concave patch that is concave in
**one direction only** shows about **half** the sphere's error. Curvature as
such does not predict a factor of two; edge counting does.

On flat patches only the faces lying along a geometric edge of the enclosure
have a visible edge neighbour, so the patch **mean** falls like `O(h)` — but the
patch **maximum stays pinned**: 1.9868 % -> 1.9234 % over a 4x face count on a
cube, against `2 e(0.21) = 1.9305 %`. It looks like convergence and is not.

### 3. `alpha` is the lever, and the law is `e(alpha)` — 1728-face concentric spheres, one mesh

| `alpha` | mean rowSum, concave patch | measured excess / edge-pair | `e(alpha)` |
| ---: | ---: | ---: | ---: |
| 0.10 | **1.5212611** | +0.1303153 | +0.1277354 |
| 0.15 | **1.2586230** | +0.0646557 | +0.0632036 |
| 0.20 | 1.0718490 | +0.0179623 | +0.0174176 |
| **0.21 (shipped default)** | **1.0402552** | +0.0100638 | +0.0096524 |
| 0.22 (value in the file header) | 1.0101421 | +0.0025355 | +0.0022485 |
| **exp(-3/2) = 0.223130** | **1.0009944** | +0.0002486 | 0 |
| 0.25 | **0.9273640** | −0.0181590 | −0.0180968 |
| 0.30 | **0.8094318** | −0.0476420 | −0.0471142 |

A **71 percentage-point swing** in a quantity that is exactly 1 by definition,
from one dictionary key, tracking the closed form to within 3 % over the whole
range. Interpolated zero crossing **0.223493** against `exp(-3/2) = 0.223130`.

### 4. `GaussQuadTol` cannot reach it — as the mechanism requires

| `GaussQuadTol` | mean rowSum, concave patch |
| ---: | ---: |
| 0.01 (default) | 1.0402552 |
| 0.001 | 1.0402632 |
| 1e-6 | 1.0402632 |

A **10 000x** tightening moves the answer by `8e-6` absolute. It cannot help,
because the coincident-edge term is forced to order 0 whatever the Gauss order
is. Anyone tightening this tolerance to chase the error will conclude the
result is converged.

### 5. Two workarounds, neither recommended as a fix

* `alpha = 0.223130160148` — restores unit row sums on all five geometries at
  all resolutions tested (residual `<= 0.4 %`, and `<= 0.13 %` on every mesh
  except the coarsest). **But `alpha` is used for a second purpose in the same
  function** (the `mag(r) < SMALL` guard in the order>0 branch, line 411), which
  this work did not isolate.
* `distTol = 1` — pushes edge-sharing pairs below the 2LI threshold and into
  2AI; the concave-patch error drops from +4.03 % to +0.13 %. But it also sends
  every other near pair to the crude one-point 2AI rule.

The proper fix is presumably to evaluate the coincident-edge term with its exact
closed form `L^2 (2 ln L - 3)` rather than through the `alpha` substitution.
**That fix has not been written or tested here.**

---

## Why this is easy to miss

`viewFactorCoeffs { smoothing true; }` renormalises the rows of `F` before the
radiosity solve, so a user running the default path never sees a row sum that is
not 1. The error is still in the relative distribution of `F_ij` within the row;
it is only the *symptom* that is hidden.

---

## What is NOT claimed

1. **No novelty.** No search of the issue tracker, the forum or the mailing
   list has been done. This may be known, reported, or already fixed. See the
   header.
2. **No flux, temperature or heat transfer coefficient is claimed.** No solver
   was run in this work. The only solved-field figure quoted anywhere in the
   supporting record is from a separate campaign
   (`docs/campaigns/T-family/T10a_RESULTS.md`): a uniform-300 K closed box, where
   the exact radiative flux is zero, returns `max |qr| = 13.95 W/m^2 = 3.0 %` of
   `sigma T^4`.
3. **No claim that any published result is wrong**, and no claim about how large
   this error is relative to other errors in a radiation simulation.
4. **No verified fix.** `alpha = exp(-3/2)` was applied only as a dictionary
   value through the shipped code path. No patched binary was built.
5. **Nothing about `createViewFactors`**, which is separate newer code with its
   own models and no `alpha`; its 2AI uses signed cosines where
   `viewFactorsGen` takes `mag()` of both. A 2D Hottel case run through
   `createViewFactors` showed a row-sum **deficit** of 2.7–3.3 %, which is a
   different phenomenon and is not investigated here.
6. **Agglomeration is untested.** The one agglomerated run collapsed a
   1728-face mesh to 15 coarse faces — too aggressive to be informative — and
   produced a matrix bit-identical between `alpha = 0.21` and
   `alpha = exp(-3/2)`, i.e. the coincident-edge branch was never reached. A
   meaningful agglomeration sweep has not been run.
7. **`intTol` observation, reported not claimed.** `intTol` is not an
   integration tolerance: `shootRays_CGAL.H:58,61` uses it as the fractional
   shrink applied to each end of the visibility ray. At `intTol = 1e-4`,
   648 of 1728 faces come back seeing **nothing at all** and the convex patch's
   mean row sum collapses to 0.161. That is a separate fragility of the same
   utility and is mentioned only so a reader does not tighten this key expecting
   accuracy.

---

## Supporting record

| what | path |
| --- | --- |
| pre-registration, frozen before any sweep ran (commit `7ed70d6b`) | `docs/campaigns/T-family/T10aVF_PREREGISTRATION.md` |
| full results, all gates and their failures | `docs/campaigns/T-family/T10aVF_RESULTS.md` |
| reproducer | `verification/runs/T-family/T10aVF_runs/reproducer/` |
| 34 sweep cases, logs, machine-readable results | `verification/runs/T-family/T10aVF_runs/` |
| the campaign in which the defect was first seen | `docs/campaigns/T-family/T10a_RESULTS.md` |
