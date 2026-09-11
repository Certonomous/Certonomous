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
---

## RESULT — 2026-09-11 — **NOT SUPPORTIVE**. Measured after the partition above was
committed at `2410c4cbd`. *Lines whose number changed above this section: 0.*

| group | `perimeter²/area` range |
|---|---|
| CONTROL (layers work) | **15.83 – 81.04** |
| FAILURE (0.00–0.12 layers) | **9.78 – 80.38** |

**The ranges overlap almost completely.** `BodySide` (a control) scores 81.04, the
second highest of all seventeen; `WheelSupportrear` (a failure) scores 9.78, the
lowest of all seventeen.

**Best single threshold: M = 12/17** — and it is the **degenerate classifier**: at
8.78 every patch scores above it, so all seventeen are called failures and the twelve
real failures are "correct" by construction. **The metric carries no discriminating
signal at all.**

Partition row: **M ≤ 14/17 → NOT SUPPORTIVE.** `featureAngle 130` is left **no better
supported than `minMedialAxisAngle 90`**, and **H2's two limbs stay TIED**.

**Direction was not inverted** (failure median 27.9 against control median 17.8), so
the wrong-signed refutation row does not fire either. The hypothesis is neither
supported nor refuted — it is simply not tested by this quantity.

**The `Mirrors2` clause passed only VACUOUSLY** and is reported as such: it lands on
the failure side, but under a threshold that puts *everything* on the failure side.
That check cannot distinguish anything here and should not be counted as passed.

**The pre-marking of the secondary metric was vindicated, and it is why it could not
be used to rescue this.** `boundary_fraction` ranges 0.041–0.089 for controls against
0.006–0.487 for failures — but `Rimsfront` and `Tiresfront` carry 74,569 and 84,096
triangles against `BrakeDiscfront`'s 2,721, and their `bfrac` is an order of magnitude
lower for that reason alone. Exactly the tessellation artifact named in advance. Had
the primary metric not been fixed first, that spread could have been read as a signal.

**Carry forward:** the discriminator for the DrivAer zero-layer group is **not**
clearance (H3, refuted), **not** `maxThicknessToMedialRatio` (H1, refuted), and **not**
patch shape as measured by perimeter-to-area. Patch *size* remains a real but
non-determining correlation (median 77 mesh faces for failures against 491), with
`NotchbackB_Pillar` at 54 faces and 4.31 layers as the standing counterexample.
