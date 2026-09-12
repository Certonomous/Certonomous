# Per-point extrusion-vector diagnostic — PREDICTION, WRITTEN BEFORE THE NUMBERS

**cfd lane, 2026-09-12. Zero compute — reads `LAYERFIX_A1_coarse_relativeSizes/constant/polyMesh`,
an artifact already on disk and already committed. No mesh is rebuilt. If this ever
rebuilds a mesh it needs a registration committed before compute; it does not.**

I have computed no normal, no dot product and no distribution for any patch.

## Why this quantity

`medialAxisMeshMover.C:117`, the **live** test:

    if ((pointWallDist[e[0]].data() & pointWallDist[e[1]].data()) < minCos)

`.data()` is the **extrusion vector**. An edge is marked medial-axis when its two
endpoints want to extrude in **different directions**. B2 proved that relieving the
*marking* (`minMedialAxisAngle` 90 → 130, node-events 59,321 → 52,535, −11.4 %) does
**not** extrude these patches — so the question is no longer whether the limb fires but
**what the extrusion field itself looks like** on a patch that cannot take layers.

The base extrusion vector is the point normal snappy starts from — the log's
*"Determining displacement for added points according to pointNormal"*. It is computable
from the existing mesh: area-weighted face normals accumulated onto each boundary point.

## The measurement

For each patch, over every edge of its boundary faces, with `d₀`, `d₁` the unit point
normals at the edge's endpoints:

- **`f_opp`** = fraction of edges with **`d₀·d₁ < 0`** — opposing, marked at 90°
- **`f_130`** = fraction with **`d₀·d₁ < −0.6428`** — still marked at 130°
- median `d₀·d₁`

Groups: the **12 real candidates** against the **5 controls** (`floorNoSlip`,
`NotchbackRoof`, `NotchbackWindowrear`, `NotchbackB_Pillar`, `BodyHood`).

## PREDICTION

> **Blocked patches carry a materially higher `f_opp` than controls.** Thin protruding
> parts — brake discs, wheel supports, exhaust tip — have faces on opposite sides whose
> normals point nearly opposite, so `d₀·d₁ ≈ −1`. Controls are contiguous body panels
> whose normals vary smoothly, so `d₀·d₁ ≈ 1` almost everywhere.

Concretely: **controls median `d₀·d₁` > 0.9 and `f_opp` near zero; blocked patches
carrying a visible opposing population.**

## WHAT WOULD REFUTE IT — named before looking

- **Controls show comparable or higher `f_opp` than blocked patches** → prediction
  **REFUTED**, wrong-signed.
- **Blocked patches show coherent normals** (median > 0.9, `f_opp` near zero) like the
  controls → **REFUTED**; the extrusion field is not what distinguishes them, and the
  cause is not in this quantity either.

## DEGENERACY LIMB AND BASELINE — both fixed now

- **MAJORITY-CLASS BASELINE: 12/17 = 0.706.** A classifier calling everything "blocked"
  scores exactly that. **Any M not exceeding 12/17 is NOT A RESULT**, whatever it looks
  like.
- **DEGENERACY LIMB:** if the best single threshold places **all seventeen** patches in
  one class, the metric has no resolution and M is meaningless **regardless of value**.
  This is the limb whose absence let `perimeter²/area` score 12/17 and look like a
  finding until the threshold was inspected.
- **NO RESOLUTION:** if blocked and control groups show the **same** distribution, the
  diagnostic is **NOT A RESULT** however clean the blocked-patch numbers are.

## Held fixed

`nMedialAxisIter` is **absent from the dict and defaults to `nTotalPoints`** — an
unlimited walk (`medialAxisMeshMover.C:182`). **It is not touched here and must not
become a silent variable in this diagnostic.** Patch size is **not** promoted to a
hypothesis by this work; it remains a correlation with `NotchbackB_Pillar` against it.
A2 stays unlaunched.
