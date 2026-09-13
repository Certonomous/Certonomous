# PPTC VP1304 — PRISM-A2 PRE-REGISTRATION **DRAFT**

**FROZEN 2026-09-13 by cfd-supervisor. THIS COMMIT IS THE FREEZE** and discharges standing
check 4. Gates, thresholds, cap and labels below are closed as of this commit.

**SUPERVISOR'S RULING ON W1, made at the freeze and part of it.** `relativeSizes false` on
any patch disables `handleWarpedFaces` mesh-wide (`snappyLayerDriver.C:3789`; `relativeSizes()`
is a `boolList`, so `found(false)` is true as soon as one patch is absolute). W1 stays
**WATCHED, NOT GATED**, because the lane measured that this guard's own threshold is
`edge0Len/(1<<ownLevel)` — the same poisoned length — so it has been over-firing against a
threshold 95.5x too small. Disabling it removes a broken guard, not a working one.
**Registered requirement in its place, because "watched" must still be measured:** the 56,953
faces this guard currently zeroes are to be **tracked within the run** — how many extruded, and
how many produced a face pyramid below `minVol`. That is a same-mesh, within-run measurement
and it is NOT a cross-mesh count against the 1,028 baseline, which the same-mesh assert forbids.

**THE OLD STATUS LINE READ: "THIS IS A DRAFT AND IS NOT A FREEZE."** It is struck, not
rewritten, and recorded here because three documents were frozen tonight whose status lines
still said DRAFT.
 It is handed to cfd-supervisor for the
check that is theirs personally and may not be delegated: pre-registration
committed **before** compute. **Nothing builds until the supervisor has
committed this document and said so.** The lane that wrote it does not start on
its own word — that was the process correction accepted on PRISM-A1, where the
freeze was real and early but the check ran as an audit instead of as a gate.

Predecessor: `PPTC_PRISM_A1_PREREGISTRATION.md`, frozen `c184c477`, addendum
`8994143c`. A1's three predictions are **PENDING** — its test bed died at mesh
construction for a reason the crash control convicted the mesh of, not the
change. A2 is a **new rung with its own registered cap**, not a new budget for
an overrun: A1 did not overrun, it stopped.

---

## 1. THE CAUSE, CARRIED FORWARD (measured, not re-argued)

`relativeSizes true` scales exactly four layer fields by
`edgeLen = level0EdgeLength()/2^pointLevel`
(`snappyLayerDriver.C:1564-1567`, `:1622-1625`).
`hexRef8::getLevel0EdgeLength()` returns the **global minimum** level-0 edge —
its own comment: *"Note minimum so if cells are not cubic we use the smallest
edge side"*. Here that is the azimuthal chord on the r = 2 mm axis rod,
`2·0.002·sin(pi/60) = 2.09343825e-04 m`, against `constant/polyMesh/level0Edge`
= **2.0934383e-04**. Eight significant figures.

## 2. A CORRECTION THIS LANE OWES, BEFORE ANY PREDICTION IS BUILT ON IT

A1 §2 said the collapsed prisms "give 5,613,625 faces with pyramid volume below
`minVol 1e-13`". That count is measured and stands
(`F360_coarse/log.snappyHexMesh:3252`). **The mechanism behind it, as this lane
first reasoned it, was wrong, and the error made the case look stronger than it
is.** The reasoning shrank the face AREA by the same 95.5x as the thickness.
Only the thickness is scaled by `edgeLen`; the face area is set by the real
mesh. Redone:

| patch | real face w | collapsed t | side-face pyramid w²t/6 | vs `minVol` 1e-13 |
|---|---|---|---|---|
| blades (lvl 5) | 6.250e-04 | 1.3145e-06 | **8.558e-14** | **FAILS by 1.17x** |
| hub / cap (lvl 4) | 1.250e-03 | 2.629e-06 | 6.847e-13 | clears by 6.85x |
| shaft (lvl 3) | 2.500e-03 | 5.258e-06 | 5.477e-12 | clears by 54.8x |

The wall face of a blade prism is `w²t/3 = 1.712e-13` and **marginally clears**.
It is the **side faces** that fail, and **only on the blades**. The corroboration
is arithmetic: blades carry 382,233 × 6 = **2,293,398** prism cells, and
5,613,625 / 2,293,398 = **2.448 sub-`minVol` faces per blade prism cell** — the
right number for a stacked hex prism whose side faces are shared laterally.

**So the honest statement is not "the prisms are thousands of times below
`minVol`". It is: the collapsed thickness puts the blade prisms' side faces a
factor 1.17 BELOW the floor — a margin of order one — while the registered
thickness clears the same floor by 81.8x.** A margin of one is exactly why the
failure is total rather than patchy: every point that smoothing thins below
nominal fails, and the medial-axis mover reported `displacement scaling min:0`.
This sharpens P4 below into a real test instead of a restatement.

## 3. THE TWO ROUTES, MEASURED, AND THE ONE RECOMMENDED

**Route 1 — `relativeSizes false`, absolute thicknesses. RECOMMENDED.**
**Route 2 — raise the base-mesh minimum edge by enlarging the axis rod.**

Route 2 was measured before it was declined, as instructed:

| rod radius | `level0Edge` | blades first layer | vs registered 1.2559e-04 | side-pyr vs `minVol` |
|---|---|---|---|---|
| 2.0 mm (as built) | 2.0934e-04 | 1.3145e-06 | **95.5x too thin** | fails 1.17x |
| 20.0 mm (shaftExtension radius, the largest admissible) | 2.0934e-03 | 1.3145e-05 | **9.55x too thin** | clears 11.7x |
| **191.1 mm (required to reproduce the registered thickness)** | 2.0000e-02 | 1.2559e-04 | 1.00x | clears 81.8x |

**The decisive number is 191.1 mm.** The rod must sit inside the shaft extension
(r = 20.0 mm); the blade tip is at 125.0 mm. **There is no admissible radius at
which route 2 reproduces the registered layer specification.** At its best
admissible value it yields layers that EXIST and are 9.55x thinner than
registered — it converts a loud zero-layer failure into a quiet
wrong-thickness success that violates the §6.3 y+ 30–60 specification while
producing a mesh that looks right. **That is the worse failure mode, and it is
why route 2 is declined on physics rather than on cost.**

Cost also declines it, secondarily: route 2 rebuilds the base mesh
(`Mesh snapped in = 8591.65 s`, `F360_coarse/log.snappyHexMesh:2895`) and spends
the analytic-volume closure that is this act's cleanest artifact (7.063061 m³
predicted against 7.063061 measured).

**Route 1's honest cost, which this lane measured and will not hide.**
`snappyLayerDriver.C:3789` guards `handleWarpedFaces` with
`if (!layerParams.relativeSizes().found(false))`, and `relativeSizes()` is a
`boolList` (`layerParameters.H:107`, `:222-224`). `found(false)` is true as soon
as **any** patch is absolute, so **setting `relativeSizes false` on one patch
disables the warped-face guard for the whole mesh.** That guard currently zeroes
56,953 faces (`log.snappyHexMesh:3075`). Mitigation, also measured: the guard's
own threshold is `edge0Len/(1<<ownLevel)` (`snappyLayerDriver.C:854`) — the same poisoned length —
so it has been firing against a threshold 95.5x too small and is **over**-firing.
It is nonetheless a guard removed, and it is registered below as a **watched**
quantity, not a gated one.

## 4. THE SINGLE REGISTERED CHANGE

Applied to `system/snappyHexMeshDict` only. Per-patch values are
0.5 x and 0.05 x each patch's own registered surface cell (`log.makeSnappy:3-6`).

    relativeSizes   false;                      // was true
    finalLayerThickness 3.125e-4;               // m, global default = blades
    minThickness        3.125e-5;               // m  (MUST convert: 0.05 absolute = 50 mm)
    expansionRatio      1.2;                    // UNCHANGED
    layers
    {
        blades { nSurfaceLayers 6; finalLayerThickness 3.125e-4; minThickness 3.125e-5; }
        hub    { nSurfaceLayers 6; finalLayerThickness 6.250e-4; minThickness 6.250e-5; }
        cap    { nSurfaceLayers 6; finalLayerThickness 6.250e-4; minThickness 6.250e-5; }
        shaft  { nSurfaceLayers 6; finalLayerThickness 1.250e-3; minThickness 1.250e-4; }
    }

Per-patch `finalLayerThickness` and `minThickness` are honoured under the global
`FINAL_AND_EXPANSION` model — verified in `layerParameters.C:616-627` (the
`FINAL_AND_EXPANSION` case of the override switch) and `:660-664`
(`minThickness` read after the switch, outside the `thicknessModel` branch). A dictionary comment in
`T26_mesh_dev/L1ABS` asserts these are silently ignored; that is true of their
`FIRST_AND_EXPANSION` model and not of this one.

## 5. PREDICTIONS — PARTIAL COVERAGE IS PREDICTED AND MAY NOT BE UPGRADED LATER

Run: `snappyHexMesh -overwrite`, `castellatedMesh false; snap false;
addLayers true;` on a **copy** of `F360_coarse`, dictionary otherwise
byte-identical. Read with
`cases/PPTC_VP1304/mesh/read_layer_achievement.py`.

| id | quantity | threshold | gated |
|---|---|---|---|
| P1 | blades near-wall in snappy's request table | **>= 1.00e-04 m** (now 1.79e-06) | yes |
| P2 | final extruded faces / 724,711 | **> 25%** | yes |
| P3 | achievement route == `table` | present | yes |
| P4 | layer-iteration-0 `faces with face pyramid volume < 1e-13` | **< 561,363** (one tenth of 5,613,625) | yes |
| W1 | faces excluded by `handleWarpedFaces` | expected **0** (guard disabled) | **watched, not gated** |

**COVERAGE IS PREDICTED AT 40% TO 90%, NOT 100%, AND THAT IS REGISTERED HERE SO
IT CANNOT BE UPGRADED AFTERWARDS.** The base mesh carries 91,876 illegal faces
and 316 negative-volume cells before any layer
(`F360_coarse/log.snappyHexMesh:3057`, `log.checkMesh:113`), and a sister lane
has placed those negative cells on the 4-to-3 refinement transition with 31.2x
enrichment and none at the blade level. Those will suppress extrusion locally
whatever the thickness. **A result above 90% is as much a surprise as one below
40% and is to be reported as one, not celebrated.**

- P1 ∧ P2 ∧ P3 ∧ P4 → **GATE REACHED**: the length scale was the dominant cause
  and one registered change obtains prism layers at the registered thickness.
- P1 ∧ P3 but P2 in (0, 25%] → **GATE FAIL on P2**, refuting nothing in §1;
  the reading is that the length scale is necessary but not sufficient, and
  whether a second change follows is the **supervisor's** call.
- P1 failed → §1 is refuted for this mesh and the rung is **NOT A RESULT**.

## 6. COST

| item | basis | estimate |
|---|---|---|
| copy of `F360_coarse` (7.3 GB) | I/O, 1 rank | 5 core-min |
| `snappyHexMesh -overwrite`, layers only, 1 rank | **measured**: the same phase cost 2114.26 s serial at `relativeSizes true` (`F360_coarse/log.snappyHexMesh:3326`) = 35.2 core-min, and a run that extrudes does more work than one that discards — `T26 L1ABS` needed 9 layer iterations where this needed 2 | 140 core-min |
| `checkMesh` on the result | 1 rank | 10 core-min |
| **cap** | measured-basis anchor 35.2 core-min, margin x4 stated as margin | **180 core-min** |

Ranks 1, of the 16 allocated to PPTC. **Sanaa's directive #17 (2026-09-12) means
no run is stopped by a cap; it does not mean a cap goes unwritten — a cost
nobody wrote down is what disqualifies a proposal.** Rate c7a.4xlarge
$0.0513/core-h, **reported-by-owner, not measured**: 180 core-min = 3.0 core-h =
**$0.154 derived**.

Run directory: `/home/ubuntu/certonomous-runs/PPTC_VP1304/PRISM_A2_absthick`
— **it must not exist when this is committed.** That is the freeze check, and
it is the supervisor's to make.

## 7. WHAT THIS RUNG MAY NOT DO

No solver. No queue entry. No edit to any frozen pre-registration. No write into
`F360_coarse/`, which another lane holds — the run works on a copy. No build
before the supervisor's committed word.
