# H2 featureAngle limb — DISCRIMINATION PARTITION, WRITTEN BEFORE THE NUMBERS

**cfd lane, 2026-09-11. Zero compute — a read of an existing STL.**
**Written and committed BEFORE the measurement was run.** I have not seen any
perimeter, area or edge-count figure for any patch. This is the correction to the
H3 partition, which I adopted after seeing six of eleven rows and disclosed as such.

## The question

`Mirrors2` sits in 309.30 mm of clear air with ~90 % of its faces striking nothing,
and takes **0.00** layers. So the blocker is **not geometric clearance**. Patch size
correlates with failure (median 77 mesh faces for failures against 491 for successes)
but does **not** determine it: `NotchbackB_Pillar` has 54 faces and achieves 4.31, and
the ranges overlap 0–809 against 54–5505.

> **Hypothesis under test: size is a proxy for JUNCTION DENSITY. What separates a
> small patch that succeeds from a small patch that fails is the fraction of its
> boundary that is feature or patch-junction edge — perimeter-to-area, not area.**

Direction predicted by H2's `featureAngle 130` limb: **failures carry MORE boundary
per unit area than successes.**

## The metrics, defined before computing them

Per patch, from the STL triangles of that named solid:

1. **`shape = perimeter² / area`** — dimensionless. A disc gives 4π ≈ 12.57; long
   thin or ragged patches give much larger values. **This is the PRIMARY metric.**
2. `boundary_fraction` = edges belonging to exactly one triangle of the patch,
   divided by total unique edges. **SECONDARY, and stated as weaker on purpose:**
   it depends on tessellation density, so a finely-tessellated patch scores lower
   for no geometric reason. `perimeter²/area` is tessellation-independent and is
   therefore the metric the verdict rests on.

Groups: the **12 real candidates** (the §4 local group less `TirePlinthfront` and
`TirePlinthrear`, which have zero mesh faces and were never layer candidates) against
the **5 controls** (`NotchbackRoof`, `BodyHood`, `NotchbackWindowrear`,
`NotchbackB_Pillar`, `BodySide`).

## The partition — every outcome falls in exactly one row

Let **M** = the best achievable classification of the 17 patches by a single threshold
on `perimeter²/area`, counted as patches correctly placed.

| condition | verdict |
|---|---|
| direction INVERTED — controls score higher than failures | **H2-featureAngle REFUTED by this measurement**; the junction-density idea is wrong-signed |
| **M = 17/17** — a clean threshold exists, no overlap | **DISCRIMINATING** — `featureAngle 130` becomes the leading H2 limb with a quantitative case |
| **M = 15 or 16 of 17**, and the group ranges overlap LESS than the face-count ranges did | **PARTIALLY SUPPORTIVE** — better than size, not decisive |
| **M ≤ 14/17**, or overlap no better than face count | **NOT SUPPORTIVE** — `featureAngle` is left no better supported than `minMedialAxisAngle`, and the two H2 limbs stay tied |

**What would make this meaningless, stated now:** if `Mirrors2` — the one patch proven
to be in open air — does not land on the failure side of whatever threshold emerges,
the metric is not capturing the phenomenon that the refutation of H3 exposed, and the
result is **NOT A RESULT** regardless of M.

## Scope

Measurement only. No registration is required and none is claimed. **The moment this
becomes a mesh build it needs one.** B2 does not exist; A2 stays unlaunched; H2's two
limbs remain exactly as `DRIVAER_LAYERFIX_B1_PREREGISTRATION.md` §6 registered them
**before** any of tonight's results.
