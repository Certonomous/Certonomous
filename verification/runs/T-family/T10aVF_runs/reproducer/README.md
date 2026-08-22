# Minimal reproducer — `viewFactorsGen` coincident-edge (`alpha`) row-sum defect

**Status: NOT FILED ANYWHERE.** This directory belongs to the T10a-VF
characterisation arm (`docs/campaigns/T-family/T10aVF_PREREGISTRATION.md`,
`T10aVF_RESULTS.md`). Whether anything is sent upstream is Sanaa's call.

## What it shows

For **any closed enclosure of opaque surfaces**, the view factors from a face
to all faces of the enclosure sum to **exactly 1**:

```
    sum_j F_ij = 1     for every i,   whatever the mesh.
```

This is a closure identity, not a modelling approximation. It does not become
approximate when a sphere is faceted, when the mesh is coarse, or when the
enclosure is concave: a closed polyhedron is still closed.

`viewFactorsGen` (OpenFOAM ESI v2606, build `_481094f-20260618`) violates it,
by up to **+4.4 %** on a concentric-sphere enclosure and by **+1.9 %** on the
corner faces of a plain cube, and the error **does not shrink with mesh
refinement**. Setting one dictionary key, `alpha`, from its default `0.21` to
`exp(-3/2) = 0.223130160148...` removes almost all of it.

## Requirements

OpenFOAM ESI v2606 (`blockMesh`, `viewFactorsGen`) and `python3` (standard
library only). Nothing else. Four cases, `blockMesh` only — **no
snappyHexMesh, no external mesh, no solver, no solution time directory.** Each case is
five small text files.

## Run

```
./Allrun
```

**Measured, three independent runs from clean: 16.1 s wall at 87 % of one core,
39.1 s at 39 %, and 19.2 s at 74 % (differing only in how busy the shared
c7a.4xlarge was) -- about 14-15 core-seconds every time.** All three printed
the table below to the last digit shown. Registered ceiling for this arm: 120 s.

As shipped this directory is **172 KB of 22 text files** and holds no mesh, no
matrix and no time directory: `Allrun` generates everything.

## Expected output

`Allrun` prints four tables. The `mean err %` column is `100*(mean rowSum - 1)`
and **must be 0 in all four**.

| case | patch | mean rowSum | min | max | mean err % |
| --- | --- | ---: | ---: | ---: | ---: |
| `box` (cube, `alpha`=0.21 default) | each of the 6 walls | **1.003755** | 1.000622 | **1.019234** | +0.3755 |
| `box_alphafix` (`alpha`=exp(-3/2)) | each of the 6 walls | 1.001342 | 0.999929 | 1.002769 | +0.1342 |
| `sphere` (concentric spheres, `alpha`=0.21 default) | `inner` (convex) | 1.003081 | 1.000747 | 1.004822 | +0.3081 |
| | `outer` (**concave**) | **1.040255** | 1.036839 | **1.044022** | **+4.0255** |
| `sphere_alphafix` (`alpha`=exp(-3/2)) | `inner` | 1.003081 | 1.000747 | 1.004822 | +0.3081 |
| | `outer` | 1.000994 | 0.997967 | 1.004899 | +0.0994 |

`rowsum.py` is a convenience only. Each case's `0/viewFactorField`, written by
`viewFactorsGen` itself under `writeViewFactorMatrix true`
(`viewFactorsGen.C:1200-1243`), already contains the same per-face row sums --
for `sphere`, `outer` mean 1.0402552, min 1.0368391, max 1.0440224.

Two numbers carry the whole story:

* `box` **max = 1.019234**. A cube is exact geometry with no curvature and no
  faceting error of any kind. A corner face of a cube wall has exactly **two**
  edge-sharing neighbours it can see (across the two box edges it lies on), and
  `1.019234 - 1 = 0.019234`, i.e. **2 x 0.009617**.
* `sphere` `outer` **mean = 1.040255**. A face on the concave outer sphere sees
  **four** edge-sharing neighbours, and `0.040255 = 4 x 0.010064`.

The per-neighbour constant is `-(2 ln alpha + 3)/(4 pi) = 0.0096524` at
`alpha = 0.21`. It contains no mesh size, which is why refining the mesh does
not help: over a 6.25x range of face count the concave-patch mean error stays
between +3.41 % and +4.03 %.

The `inner` patch of `sphere` is the control. It is **convex**, so no face on
it can see any of its own edge neighbours, `alpha` is never exercised on it,
and its two rows are **bit-identical** between `sphere` and
`sphere_alphafix`. Its residual +0.31 % is ordinary faceting/quadrature error
and converges with the mesh; it is not this defect.

## Where the error comes from

`applications/utilities/preProcessing/viewFactorsGen/viewFactorsGen.C`:

* line 969 — a face pair closer than `distTol` (default 8 equivalent radii)
  goes to the 2LI double-contour branch. Two faces sharing an edge always do.
* lines 1054-1058 — inside 2LI, an edge pair whose midpoints coincide (which is
  exactly the **shared edge**, traversed in opposite senses, `cos_ij = -1`) has
  its quadrature order forced to 0, *whatever the outer Gauss order*.
* lines 390-394 — at order 0 the log singularity is evaluated by substituting
  `r -> alpha*|s_i|`, giving `cos_ij * L^2 * 2 ln(alpha L)`.

The exact self-edge contour integral is

```
    int_0^L int_0^L ln((s-t)^2) ds dt  =  L^2 * (2 ln L - 3)
```

so the substitution is exact **iff `2 ln(alpha) = -3`, i.e.
`alpha = exp(-3/2) = 0.223130160148...`.** The shipped default is `0.21`.
After the `1/(4 pi A_i)` normalisation at lines 1096-1097 the residual is the
mesh-independent constant `-(2 ln alpha + 3)/(4 pi)` added to `F_ij` once per
mutually-visible edge-sharing neighbour.

The value is documented inconsistently in the code itself: the file header at
line 45 gives `alpha 0.22` while the code default at line 483 is `0.21`.
Neither is `exp(-3/2)`; `0.22` would leave `4 x 0.00225 = +0.90 %` on a concave
patch.

## What this reproducer does NOT show

* It does not measure any flux, temperature or heat transfer coefficient. No
  solver is run.
* It does not claim any published result is wrong.
* It does not test a patch. `alpha = exp(-3/2)` is applied as a **dictionary
  value through the shipped code path**; that it drives the residual to ~0 is
  evidence about the mechanism, not a verified fix. In particular `alpha` is
  also used for a second purpose in `GaussQuad` (the `mag(r) < SMALL` guard
  inside the order>0 branch, line 411), which this reproducer does not isolate.
* `smoothing true` in `viewFactorCoeffs` renormalises the rows and hides all of
  this. These cases are generated with no smoothing, and the matrix examined is
  the raw `constant/F` as written by the utility.
* Nothing here concerns `createViewFactors`, which is separate code with
  separate models.
