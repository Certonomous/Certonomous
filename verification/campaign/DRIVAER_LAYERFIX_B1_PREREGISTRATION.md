# DRIVAER LAYERFIX B1 — THE LOCAL HYPOTHESIS — PRE-REGISTRATION

**Team:** cfd | **Rung id:** `DRIVAER_LAYERFIX_B1` | **Registered:** 2026-09-11
**Status at freeze:** PRE-COMPUTE. Verified at freeze time:
`verification/runs/navier_class/DRIVAER/LAYERFIX_B1_coarse_medialRatio`
does not exist on disk. No compute has been spent against this registration.

**THIS IS NOT AN EXTENSION OF `DRIVAER_LAYERFIX`.** That registration's gates
closed at its first compute. **This is not arm A2 by another name**: A2 is a
*medium-resolution repeat of A1* and remains contingent on A1 being `PASS`, which
it is not. B1 is a different arm at the same resolution testing a different
parameter, and it has its own gate, band, cap and label below.

---

## 1. WHAT IS ALREADY ESTABLISHED — NOT RE-DERIVED HERE

From `DRIVAER_LAYERFIX` A1 (`GATE FAIL`, committed `01401740f`):

- `relativeSizes false` with an absolute 0.75 mm first layer against a 50 mm
  surface cell gave a **66.7:1** near-wall aspect ratio and **0 %** layers.
- `relativeSizes true` (A1) lifted that to **50.057 %** achieved layer cells —
  **the global aspect-ratio mechanism is CONFIRMED** — but `GATE FAIL` against
  A1's registered 70 % band.
- A1's mesh is **not spliced**: `constant/polyMesh` points and faces agree, no
  `0/polyMesh`, max aspect ratio 19.53, **zero** negative volumes.

## 2. THE LOCAL HYPOTHESIS

A1's achieved per-patch table partitions sharply. **Large smooth surfaces carry
layers; small parts in tight gaps carry none.**

> **H1: the `maxThicknessToMedialRatio 0.3` limb truncates extrusion in tight
> gaps, and it — not the global thickness spec — is what holds the
> wheel/underbody group at zero.**

**Registered prior, measured in A1's own log before this freeze:** the medial-axis
limb fires on **11,391 → 7,862 → 6,977 → 6,725 → 6,622 → 6,588 → 6,579 → 6,577
nodes**, once per layer iteration, **59,321 node-events in total, and it never
stops** — it plateaus at ~6,577 rather than decaying to zero. For comparison, in
the same run isolated-region removal totals **2,284** and mesh-quality
un-extrusion totals **1,705**. The named limb is **~26x** the quality limb by
event count. That is the reason H1 is worth a run and it is stated before the run.

## 3. THE ONE CHANGE

`LAYERFIX_B1_coarse_medialRatio` is a copy of `LAYERFIX_A1_coarse_relativeSizes`'s
inputs with **exactly one** change in `addLayersControls`:

    maxThicknessToMedialRatio 0.6;     (was 0.3)

Everything else — `relativeSizes true`, `finalLayerThickness 0.5`,
`expansionRatio 1.25`, `minThickness 0.02`, `nSurfaceLayers 5` on all 50 patches,
`featureAngle 130`, `minMedialAxisAngle 90`, `nGrow 0`, `nLayerIter 50`,
`nRelaxedIter 20`, the mesh quality dict, the blockMesh and the STL — is
unchanged and will be verified byte-identical by `cmp` before launch. Serial,
1 rank, as A1 was.

## 4. THE TWO PATCH GROUPS — FIXED NOW, BY NAME, FROM A1's COMMITTED TABLE

**LOCAL GROUP (14 patches, A1 achieved < 0.15 layers)** — the group H1 predicts
will move:

`BrakeDiscfront` 0.00, `BrakeDiscrear` 0.00, `CTRL_SURFACE_Outlet` 0.00,
`ExhaustSystem1` 0.00, `Mirrors2` 0.00, `Rimsfront` 0.00, `Rimsrear` 0.00,
`TirePlinthfront` 0.00, `TirePlinthrear` 0.00, `WheelSupportfront2` 0.00,
`WheelSupportrear` 0.00, `WheelSupportfront1` 0.02, `Tiresrear` 0.03,
`Tiresfront` 0.11

**CONTROL GROUP (5 patches, A1 achieved >= 4.00)** — the group that must NOT
regress, because a change that buys the wheels at the body's expense is not a fix:

`floorNoSlip` 4.62, `NotchbackRoof` 4.45, `NotchbackWindowrear` 4.34,
`NotchbackB_Pillar` 4.31, `BodyHood` 4.14

## 5. THE NOISE FLOOR — REGISTERED SIGHT-UNSEEN, BEFORE ANY B1 NUMBER EXISTS

> **A local-group patch counts as REACHED only at achieved mesh layers >= 1.00.**

Below 1.00 there is no continuous prismatic layer on that patch — it is partial
extrusion, which is what A1 already has. **0.00 -> 0.02 is not a finding. 0.00 ->
0.99 is not a finding either**, and the threshold is stated at 1.00 now precisely
so that it cannot be lowered later to make a weak result readable. The figure is
the same `--min-mesh-layers 1.0` the committed guard already refuses on, so it is
inherited rather than invented for this rung.

## 6. THE GATE — FROZEN, AND IT PARTITIONS THE WHOLE OUTCOME SPACE

Let **R** = number of the 14 LOCAL-GROUP patches reaching >= 1.00 achieved layers.
Let **G** = global achieved layer-cell fraction. Let **C** = minimum achieved
layers across the 5 CONTROL-GROUP patches.

Evaluated in this order. Every outcome falls in exactly one row.

| condition | label |
|---|---|
| build rc != 0, or cap exceeded, or the index test (§8) shows a splice, or the guard cannot read a required field | **NOT A RESULT** |
| **C < 3.00** — the control group regressed | **REGRESSION** — reported with R and G beside it; **H1 is NOT confirmed whatever R is**, because the change cost more than it bought |
| **G < 50.057 %** — global worse than A1 | **REGRESSION** — same treatment |
| **R >= 7** (half or more of the local group), C >= 3.00, G >= 50.057 % | **H1 CONFIRMED** — `maxThicknessToMedialRatio` is what held the local group at zero |
| **1 <= R <= 6**, C >= 3.00, G >= 50.057 % | **H1 PARTIAL** — the limb reaches some of the group; the group is heterogeneous and one parameter is not the whole explanation |
| **R = 0**, C >= 3.00, G >= 50.057 % | **H1 REFUTED** — doubling `maxThicknessToMedialRatio` moves NOT ONE of the 14. The limb is not what blocks them, and the next hypothesis must be sought elsewhere (candidates, registered now so the refutation is not retro-fitted: `minMedialAxisAngle 90`, `featureAngle 130` across the many small patch junctions, or the gap being narrower than `minThickness` permits at any ratio) |

**WHY R >= 7 AND NOT SOME OTHER NUMBER, justified before the run:** H1 claims ONE
parameter holds the WHOLE group at zero. If that is true, relieving it should reach
a majority of the group. If it reaches only a minority, the group is not one
phenomenon and a single-parameter explanation is wrong — which is what `PARTIAL`
says. The threshold is the majority of a group whose membership was fixed by A1's
committed numbers, not by anything measurable in B1.

**This gate can kill H1.** `R = 0` is a reachable, pre-named outcome with a
consequence, and the alternative hypotheses are listed now so that a refutation
cannot be converted into "we always thought it was something else".

## 7. COST (rule 12) — ANCHORED ON THE SUCCEEDING BUILD

**Anchor: A1, which SUCCEEDED, not `DIAG_v3`, which collapsed.** A1's own
calibration row (`C-20260911T224532.862876Z-206c4909`) established that a
collapsing layer phase costs MORE than a succeeding one — `DIAG_v3` ground 32
layer iterations down to nothing while A1 converged in 8 and built a 1.46x larger
mesh FASTER. **A cost anchored on a failed build systematically over-prices its own
fix**, so `DIAG_v3` is explicitly rejected as the anchor here.

| | |
|---|---|
| anchor | A1 **measured 2.52 core-min** (151 wall s x 1 rank), committed `01401740f` |
| adjustment | B1 permits thicker layers near medial axes, so it should extrude at least as much as A1 and may add iterations. Allow **+20 %**. |
| **point estimate** | **3.0 core-min** |
| **CAP** | **15 core-min** — same as A1; enforced by a 900 s `timeout` inside the wrapper, and rc 124 writes `CAP_BREACH.txt` |

3.0 core-min = 0.05 core-h x $0.0513/core-h = **$0.0026 DERIVED, NEVER MEASURED** —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
per-run pre-authorisation. Disk: A1 measured ~60 MiB; B1 should be similar or
somewhat larger and is **not** disk-constrained (root volume grown 2026-09-11,
508 GiB free).

Estimate-versus-actual lands as a row in `docs/COST_CALIBRATION.md` at completion.

## 8. THE INDEX TEST IS MANDATORY AND RUNS BEFORE ANY `checkMesh` NUMBER IS BELIEVED

DrivAer **splices its mesh when the layer phase collapses**: `DIAG_v3`'s
`constant/polyMesh` held snapped points (157,745) against layer faces (410,969),
and `checkMesh` on that mix returned 52,333 "negative volumes" and a max aspect
ratio of 2.78e+101 — numbers about a mesh that never existed
(`verification/runs/navier_class/DRIVAER/MESH_SPLICE_PROOF.md`).

> **Before any B1 `checkMesh` figure enters this record:** read
> `constant/polyMesh/points`' declared count, scan `constant/polyMesh/faces` for
> its maximum vertex index, and require **points supplied == max index + 1** with
> **zero unused trailing points** and **no `0/polyMesh` directory**. A failure of
> this test makes the rung **NOT A RESULT** (§6 row 1) — it does not make the
> mesh bad, it makes the *reading* void.

**And the standing rule that earned it:** a physically impossible value is evidence
about the INSTRUMENT and outranks every plausible-looking value printed beside it.

## 9. WHAT THIS DOCUMENT DOES NOT CLAIM

- It does not re-open A1's gate, band, cap or label.
- It does not authorise A2, which stays contingent on A1 being `PASS`.
- A `CONFIRMED` here licences nothing about near-wall resolution, y+, or fitness
  for any solve. It is a meshing-mechanism result only.
- `maxThicknessToMedialRatio 0.6` is **a probe, not a proposed production value**.
  If H1 is confirmed, the production setting is a separate question with its own
  registration.
- The builder `cases/navier_class/DRIVAER/mesh/build_drivaer_level.py` hardcodes
  `relativeSizes false` at line 241 **deliberately**, its docstring stating that a
  fixed absolute first layer holds y+ constant across a grid triple. Nothing here
  proposes changing that file; B1 edits its own case copy only, and the y+
  consequence of relative sizing is a real cost that a production fix must answer
  and this rung does not.
