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

# PRISM-A2 — AMENDMENT 1, DRAFTED FOR THE SUPERVISOR. **NOT YET APPENDED. NOT YET IN FORCE.**

**Drafted by:** lab-lane under `cfd-supervisor`, 2026-09-13. **Ruling by:** `cfd-supervisor`.
**This lane has NOT edited the frozen registration.** The text in §A1 below is drafted to be
appended, verbatim and unchanged, at the **foot** of
`verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md` by the supervisor, whose commit
is the freeze. Until that commit, **PRISM-A2 stands exactly as frozen at `748d26915` and this file
changes nothing.**

*(Filed under `verification/campaign/` beside the registration it amends, not in scratch — L-186:
a draft another agent must read lives under the directory it belongs to.)*

---

## 0. THE RULE-2 CONDITION, STATED AND CHECKED — with the check planted

CLAUDE.md rule 2: *"Before first compute, amendments are legal **and must state the condition and
how it was checked** (name the run directory that does not exist)."*

**The condition:** PRISM-A2 has had **no compute**.

**The run directory, as the registration itself names it** (`…_DRAFT.md:189`, §6):

> `/home/ubuntu/certonomous-runs/PPTC_VP1304/PRISM_A2_absthick`
> — *"it must not exist when this is committed."*

**Checked 2026-09-13 at that path: IT DOES NOT EXIST.**

**THE CHECK IS PLANTED** (CLAUDE.md rule 3 — a zero from a reader not shown able to see a non-zero
is not evidence). The **parent** directory `/home/ubuntu/certonomous-runs/PPTC_VP1304/` **does**
exist and lists **ten sibling run directories**: `F360_coarse`, `F360_coarse_shaft4`, `L1_cm1`,
`L1_prod7`, `L1_prod7s`, `L2_prod7s`, **`PRISM_A1_absthick`**, `SMOKE360_J0.7985`,
`SMOKE_J0.7985`, `_360bg`. The same `ls` that returns nothing for `PRISM_A2_absthick` returns ten
entries one level up, **including A1's own absolute-thickness run** — so the absence is a
measurement, not a blind reader.

**A CORRECTION THIS LANE OWES, AND IT IS THE REASON THIS SECTION IS WRITTEN IN FULL.** My earlier
report to the supervisor stated *"`PRISM_A2_absthick` does not exist — no compute"*. **That check
was run at `verification/runs/PPTC_VP1304/PRISM_A2_absthick`, which is NOT the path the
registration names.** The registration's run root is under `/home/ubuntu/certonomous-runs/`, outside
git (`docs/LOCATIONS.md`). **The earlier check was true by accident — it tested a path that never
existed for any rung.** The check above is the real one, at the real root, and it is the one this
amendment rests on. The conclusion is unchanged; the evidence for it was not.

**The window closes the moment anyone builds.** This amendment is legal only until then.

---

## A1 — TEXT DRAFTED FOR APPENDING AT THE FOOT OF THE FROZEN FILE

> ## AMENDMENT 1 — 2026-09-13, BEFORE FIRST COMPUTE. `nSurfaceLayers` 6 → 2 AND THE THICKNESSES RE-DERIVED, BECAUSE THE RUNG AS FROZEN FAILS BOTH THE y+ WINDOW AND THE ONE-LOCAL-CELL RULE
>
> **Version: v1.0 → v1.1.** *(The registration carried no explicit version; this amendment
> establishes the convention and the original is v1.0.)*
>
> **`lines whose number changed above this section: 0`** — this section is appended at the foot;
> the file was **193 lines** before it and nothing above line 194 is touched, renumbered or
> rewritten. The original text is **struck by this amendment where §A1.2 says so, never rewritten**
> (CLAUDE.md rule 6).
>
> **Legality:** pre-compute. The run directory
> `/home/ubuntu/certonomous-runs/PPTC_VP1304/PRISM_A2_absthick` did not exist when this was
> committed; the parent listed ten sibling run directories at the same moment, so the absence was
> read by a reader shown able to see a non-zero.
>
> ### A1.1 WHY — TWO INDEPENDENT FAILURES, NEITHER VISIBLE UNTIL A BUILD
>
> Computed from **our own** conditions (n = 15 s⁻¹, our J, our fluid), using the **act
> pre-registration's own frozen §A4.2 instrument** and not a new one. Artifact:
> `cases/PPTC_VP1304/mesh/predict_yplus_from_first_layer.py`; full working in
> `cases/PPTC_VP1304/PRISM_A2_YPLUS_AND_L2_COMPUTED_FROM_OUR_SIDE.md`.
>
> **(a) The y+ window is missed, low, everywhere.** At the frozen `finalLayerThickness 3.125e-4`
> with `expansionRatio 1.2` and `nSurfaceLayers 6`, the first layer is
> `3.125e-4 / 1.2⁵ = 1.2559e-4 m = 0.1256 mm` and the first cell centre is 0.0628 mm. Predicted
> `blades` y+:
>
> | J | r/R 0.30 | r/R 0.70 | r/R 0.90 |
> |---|---|---|---|
> | 0.7985 | 12.5 | 21.4 | 26.8 |
> | 1.2021 | 15.1 | 22.8 | 27.9 |
> | 1.4594 | 17.0 | 23.9 | 28.8 |
>
> **Every station at every J is below the act's registered 30–60 window, and the maximum anywhere
> (28.8) is below the amended 30–300 floor.**
>
> **(b) The layer stack asks for 2.0 local cells.** `MESH_STANDARD.md` §16.3 rule L2:
> `S = t_f · Σ_{i=0}^{N-1} r^-i`, in local cells. At `t_f = 0.5 × local cell`, `r = 1.2`, `N = 6`:
> **S = 0.5 × 3.9906 = 1.995 on all four layer patches.** §16.3's measured pair is
> DrivAerML **0.480 → EXTRUDED** and Certonomous DrivAer **1.6808 → COLLAPSED (2.50 of 5)**.
> **1.995 is above the value that collapsed**, and §16.3 warns: *"Do not expect a too-thick stack to
> give you fewer layers. Expect it to give you none."*
>
> **The two failures pull in opposite directions.** Raising y+ needs a thicker first layer, which
> makes the stack taller, which makes L2 worse. **At `nSurfaceLayers 6` and `expansionRatio 1.2`,
> no first-layer height satisfies both**; the maximum y+ obtainable under L2 at 6 layers is **11.4**.
>
> **In fairness to the original:** `MESH_STANDARD.md` §16 is **v1.11, committed `50ce30f5` at
> 17:37 on 2026-09-13**, *after* this registration froze at `748d26915` (17:05). **The original
> could not have complied with a rule that did not yet exist**, and stated no L2 exception because
> there was none to state.
>
> ### A1.2 WHAT CHANGES — the dictionary block of §4 is STRUCK and replaced
>
> **STRUCK** (original retained above, unrewritten): `nSurfaceLayers 6` on all four patches, and
> the `finalLayerThickness` / `minThickness` values paired with it.
>
> **IN FORCE from this amendment:**
>
> ```
>     relativeSizes   false;                      // UNCHANGED by this amendment
>     finalLayerThickness 3.4091e-4;              // m, global default = blades
>     minThickness        3.4091e-5;              // m, = 0.1 x finalLayerThickness, UNCHANGED RATIO
>     expansionRatio      1.2;                    // UNCHANGED — see A1.3
>     layers
>     {
>         blades { nSurfaceLayers 2; finalLayerThickness 3.4091e-4; minThickness 3.4091e-5; }
>         hub    { nSurfaceLayers 2; finalLayerThickness 6.8182e-4; minThickness 6.8182e-5; }
>         cap    { nSurfaceLayers 2; finalLayerThickness 6.8182e-4; minThickness 6.8182e-5; }
>         shaft  { nSurfaceLayers 2; finalLayerThickness 1.3636e-3; minThickness 1.3636e-4; }
>     }
> ```
>
> **Derivation, so every number is reproducible and none is chosen by hand.** For `S = 1.000`
> exactly at `N = 2`, `r = 1.2`: `Σ r^-i = 1 + 1/1.2 = 1.8333`, so
> `finalLayerThickness = local cell / 1.8333 = 0.5455 × local cell`. Local cell is the 20 mm
> background over `2^level` at each patch's registered refinement level:
>
> | patch | level | local cell | **new `finalLayerThickness`** | first layer `t_f/1.2` | **S** | **new `minThickness`** |
> |---|---|---|---|---|---|---|
> | `blades` | 5 | 0.6250 mm | **3.4091e-4 m** | 0.2841 mm | **1.000** | 3.4091e-5 m |
> | `hub` | 4 | 1.2500 mm | **6.8182e-4 m** | 0.5682 mm | **1.000** | 6.8182e-5 m |
> | `cap` | 4 | 1.2500 mm | **6.8182e-4 m** | 0.5682 mm | **1.000** | 6.8182e-5 m |
> | `shaft` | 3 | 2.5000 mm | **1.3636e-3 m** | 1.1364 mm | **1.000** | 1.3636e-4 m |
>
> `minThickness` keeps the original's ratio of **0.1 × `finalLayerThickness`** — it is re-derived,
> not re-chosen, because it is a fraction of a quantity that moved.
>
> ### A1.3 WHAT DOES NOT CHANGE, AND WHY
>
> - **`expansionRatio` stays 1.2.** It is the **only** layer parameter in this rung with a published
>   source — Klerebrant Klasson & Huuva (2011), smp'11 II-2.1, p. 2, *"Five prism layers with 1.2 as
>   growth ratio"*, an OpenFOAM PPTC setup. Reducing it does not fix L2 anyway: uniform layers
>   (`r = 1.0`) at 6 × 0.248 mm still give **S = 2.38**.
> - **`relativeSizes false` stands.** The absolute-sizing fix is unaffected by this amendment and
>   remains the rung's purpose.
> - **No gate, threshold, cap or label is altered.** This amendment changes a mesh input, not a
>   criterion. The act's y+ window, the quality gates and the cost cap are untouched.
>
> ### A1.4 REGISTERED PREDICTION, SO THE BUILD CAN FALSIFY IT
>
> **Predicted `blades` y+ at the design point J = 1.2021, r/R 0.70: ≈ 51.** Across the blade the
> predicted span is roughly **y+ 30 (root) to 56 (r/R 0.90)**. A measured patch-mean outside
> **30–60** falsifies this prediction and is recorded as a miss.
>
> **Predicted layer coverage: this is the honest limit of the choice, and it is registered as a
> prediction, not as a fix.** `S = 1.00` is **NOT in the demonstrated-safe region.** §16.3's rule
> rests on **two measured points and only two** — 0.480 extrudes, 1.6808 collapses. **1.00 is
> untested territory; it is not "safe", it is "on the right side of the only number we have."**
>
> > **REGISTERED: this rung may PARTIALLY EXTRUDE.** A coverage below 2.0 of 2 layers on `blades`
> > is **not** a surprise and is **not** a failure of the absolute-sizing fix; it is the L2 rule
> > being tested at a value it has never been tested at. **Coverage is measured post-extrusion per
> > L-590 and reported whatever it is.** Full coverage would be the first data point in the region
> > between 0.480 and 1.6808; partial coverage narrows the rule's threshold from above. **Either
> > outcome informs §16.3, and both are results.**
>
> **The y+ figures are PREDICTIONS from a flat-plate correlation** (`Cf = 0.058 Re_c^-0.2`) that
> **ignores pressure gradient, rotation and three-dimensionality.** It is used **for consistency
> with the act's registered §A4.2 instrument, not because it is accurate.** **Only
> `simpleFoam -postProcess -func yPlus`, read through `scripts/yplus_reader_guard.py`, measures
> y+** — never the generic `postProcess`, which on this build returns zero on every patch and exits
> clean.
>
> ### A1.5 THE STRUCTURAL FINDING THAT OUTLIVES THIS RUNG — RECORDED, NOT RESOLVED
>
> **The act's registered y+ window and the registered blade refinement level are in tension on this
> geometry, and no layer-dictionary edit resolves it.**
>
> To reach **y+ 30** with a wall function here the first layer must be **≈0.25 mm**, while the blade
> surface cell is **0.625 mm**. **The stack is therefore a large fraction of one local cell whatever
> `nSurfaceLayers` is** — that is a property of the geometry and the flow, not of the dictionary.
> Coarsening the blades relieves L2 but **breaks the registered ≥8-cells-across-the-leading-edge
> gate** (only level 3, a 2.5 mm blade cell, clears L2 at 6 layers); refining makes L2 worse.
>
> **This is a registration-level question, not a mesh-dictionary question**, and it is recorded here
> so it is not rediscovered at the next rung. **It is NOT decided by this amendment**, which cannot
> alter a gate.

---

## 2. WHAT THIS DRAFT DOES NOT DO

- **It does not amend anything.** The frozen file is untouched by this lane; the supervisor's commit
  is the amendment.
- It does not alter a gate, threshold, cap or label — no amendment may (rule 2).
- It does not decide §A1.5.
- It does not claim `S = 1.00` is safe. §A1.4 registers the opposite.

## 3. COST

No solver. Condition check, per-patch derivation, drafting. **Measured: 2.4 core-minutes**, single
rank. Lane cumulative **29.9 core-minutes** ≈ **\$0.0256 derived, not measured** at the owner-stated
\$0.0513/core-h — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). No
pre-registered estimate for a drafting task, so no calibration ratio is claimable.

# PRISM-A2 — AMENDMENT 2, DRAFTED FOR THE SUPERVISOR. **NOT YET APPENDED. NOT YET IN FORCE.**

**Drafted by:** lab-lane under `cfd-supervisor`, 2026-09-13. **Ruling by:** `cfd-supervisor`, who
changed their own Amendment 1 ruling on published evidence. **This lane has NOT edited the frozen
registration** — `git diff HEAD` is empty on it. The supervisor's commit is the amendment.

**Supersedes the layer values of AMENDMENT 1 (`e2e41f859` draft, ruled `ef98fc88`). Amendment 1's
everything else stands.**

---

## 0. RULE-2 CONDITION — RE-CHECKED, NOT INHERITED

An amendment's legality is a fact about **now**, not about when the last amendment was drafted.
**Re-checked at 18:18:57Z on 2026-09-13**, at the root the registration itself names
(`…_DRAFT.md:189`):

> `/home/ubuntu/certonomous-runs/PPTC_VP1304/PRISM_A2_absthick` — **DOES NOT EXIST.**

**Still planted:** the parent `/home/ubuntu/certonomous-runs/PPTC_VP1304/` now lists **56**
directories — up from the ten seen at the Amendment 1 check, so the reader is demonstrably live and
the tree is demonstrably changing while this path stays absent.

**PRISM-A2 remains pre-compute. The amendment is legal. The window closes the moment it builds.**

---

## A2 — TEXT DRAFTED FOR APPENDING AT THE FOOT OF THE FROZEN FILE

> ## AMENDMENT 2 — 2026-09-13, BEFORE FIRST COMPUTE. THE STACK TARGET MOVES FROM S = 1.000 TO **S = 0.794**, ON PUBLISHED EVIDENCE THAT DID NOT EXIST WHEN AMENDMENT 1 WAS RULED
>
> **Version: v1.1 → v1.2.**
>
> **`lines whose number changed above this section: 0`** — appended at the foot, below Amendment 1;
> nothing above is touched, renumbered or rewritten.
>
> **Legality:** pre-compute, re-checked at 18:18:57Z. `/home/ubuntu/certonomous-runs/PPTC_VP1304/
> PRISM_A2_absthick` did not exist; the parent listed 56 sibling directories at the same moment.
>
> ### A2.1 WHAT IS STRUCK, AND WHY IT IS STRUCK RATHER THAN REWRITTEN
>
> **STRUCK from Amendment 1 (its text stands above, unrewritten):** the target **S = 1.000** and the
> four `finalLayerThickness` / `minThickness` values derived from it.
>
> **Amendment 1 chose S = 1.000 under an explicitly stated hedge**: at that moment
> `MESH_STANDARD.md` §16.3 rested on **two measured points and only two** — 0.480 extrudes, 1.6808
> collapses — and Amendment 1 registered in terms that *"1.00 is untested territory; it is not
> 'safe', it is 'on the right side of the only number we have.'"*
>
> **That hedge is now superseded by evidence.** Six published OpenFOAM cases report stacks of
> **0.758, 0.794, 0.917, 1.197, 1.302, 1.600** local cells. S = 1.000 is no longer outside published
> practice — **and neither is any other value in that band**, which is what makes the choice free.
>
> **THE CHANGE IS MADE ON PUBLISHED EVIDENCE, BEFORE COMPUTE, AND THERE IS NO FITTING RISK: the
> rung has not built and no data exists to fit to.** A ruling kept after the evidence for it has
> been replaced protects the ruling, not the result.
>
> ### A2.2 WHY 0.794 RATHER THAN 1.000 — the y+ window does not discriminate, so margin decides
>
> Computed from our own conditions with the act's frozen §A4.2 instrument
> (`cases/PPTC_VP1304/mesh/predict_yplus_from_first_layer.py`), `blades` at r/R 0.70:
>
> | target S | `blades` `finalLayerThickness` | first layer | y+ at J 0.7985 / 1.2021 / 1.4594 |
> |---|---|---|---|
> | 1.000 (Amendment 1) | 3.4091e-4 m | 0.2841 mm | 48.4 / 51.5 / 54.0 |
> | 0.917 | 3.1261e-4 m | 0.2605 mm | 44.4 / 47.2 / 49.5 |
> | **0.794 (THIS AMENDMENT)** | **2.7068e-4 m** | **0.2256 mm** | **38.4 / 40.9 / 42.9** |
> | 0.758 | 2.5841e-4 m | 0.2153 mm | 36.7 / 39.0 / 40.9 |
>
> **Every value in the published band lands inside the registered 30–60 window at every point of the
> sweep.** The y+ gate therefore **cannot discriminate between them**, and the choice falls to
> extrusion margin alone. On that axis 0.794:
>
> 1. **matches the one published dictionary this lab has verified line by line** (§A2.3), exactly;
> 2. sits in the **dense part** of the published cluster rather than at its upper edge;
> 3. carries **more margin from the 1.6808 that collapsed** than 1.000 does;
> 4. lands y+ **mid-window across the whole sweep** (38–43), not near either edge.
>
> ### A2.3 THE EXTERNAL SOURCE — verified in this lab, and its limits stated
>
> `/home/ubuntu/upstream/published-openfoam-setups/openfoam-hpc-tc/compressible/rhoPimpleFoam/LES/
> marinePropeller/` (pointer commit `799c88e78`). Identity from its own README: **"MB13 MARINE
> PROPELLER", ESI-Group, 2023**, CC-BY-SA 4.0.
>
> **IT IS NOT PPTC VP1304 — four blades, D = 0.224 m.** Under Sanaa's §G it is therefore **not a
> published setup "of that case"**, and **no PPTC-specific value is taken from it.** It is admitted
> as **published OpenFOAM mesher practice for a marine propeller**, which is what it is.
>
> `system/snappyHexMeshDict`: `relativeSizes false`; `propellerTip { nSurfaceLayers 5;
> firstLayerThickness 0.0001; expansionRatio 1.20; }`; stems `firstLayerThickness 0.0002`.
> `blockMeshDict`: 1.2 × 2.4 × 1.2 m over `(40 80 40)` = a **uniform 0.03 m Cartesian background**.
> `refinementSurfaces`: tip at level **(4 5)**, stems at **(4 4)**.
>
> | patch | first layer | level | local cell | stack | **S** |
> |---|---|---|---|---|---|
> | `propellerTip` | 1.0e-4 m | 5 | 9.375e-4 m | 7.4416e-4 m | **0.794** |
> | `propellerStem*` | 2.0e-4 m | 4 | 1.875e-3 m | 1.48832e-3 m | **0.794** |
>
> **The stack ratio was derived here, not accepted.** Tip and stem land on the **same** S because
> their absolute thicknesses **track their refinement levels** — exactly 2× for one level coarser.
> **That is the per-patch pattern Amendment 1 derived independently before this dictionary was
> read**, and it is now externally corroborated.
>
> **Limit of the evidence, stated:** of the six published stack values, **this lane verified one —
> the 0.794, twice (tip and stem).** The other five are relayed from a sibling lane's record and
> **were not independently checked here.** The choice rests on the verified one; the other five
> establish only that the band is populated.
>
> ### A2.4 WHAT IS IN FORCE FROM THIS AMENDMENT
>
> ```
>     relativeSizes   false;                      // UNCHANGED
>     finalLayerThickness 2.7068e-4;               // m, global default = blades
>     minThickness        2.7068e-5;               // m, = 0.1 x finalLayerThickness, RATIO UNCHANGED
>     expansionRatio      1.2;                     // UNCHANGED
>     layers
>     {
>         blades { nSurfaceLayers 2; finalLayerThickness 2.7068e-4; minThickness 2.7068e-5; }
>         hub    { nSurfaceLayers 2; finalLayerThickness 5.4136e-4; minThickness 5.4136e-5; }
>         cap    { nSurfaceLayers 2; finalLayerThickness 5.4136e-4; minThickness 5.4136e-5; }
>         shaft  { nSurfaceLayers 2; finalLayerThickness 1.0827e-3; minThickness 1.0827e-4; }
>     }
> ```
>
> **Derivation:** `finalLayerThickness = 0.794 × local cell / Σ_{i=0}^{1} 1.2^-i = 0.794 × local
> cell / 1.8333 = 0.4331 × local cell`, with local cell = 20 mm background / 2^level.
>
> | patch | level | local cell | `finalLayerThickness` | first layer | **S** | `minThickness` |
> |---|---|---|---|---|---|---|
> | `blades` | 5 | 0.6250 mm | 2.7068e-4 m | 0.2256 mm | **0.794** | 2.7068e-5 m |
> | `hub` | 4 | 1.2500 mm | 5.4136e-4 m | 0.4511 mm | **0.794** | 5.4136e-5 m |
> | `cap` | 4 | 1.2500 mm | 5.4136e-4 m | 0.4511 mm | **0.794** | 5.4136e-5 m |
> | `shaft` | 3 | 2.5000 mm | 1.0827e-3 m | 0.9023 mm | **0.794** | 1.0827e-4 m |
>
> **`nSurfaceLayers 2` and `expansionRatio 1.2` are UNCHANGED from Amendment 1.**
>
> ### A2.5 REGISTERED PREDICTION, REPLACING AMENDMENT 1's
>
> **Predicted `blades` y+ at r/R 0.70: 38.4 / 40.9 / 42.9** at J = 0.7985 / 1.2021 / 1.4594. Across
> the blade the predicted span is roughly **y+ 25 (root) to 45 (r/R 0.90)**. **A measured patch-mean
> outside 30–60 falsifies this prediction and is recorded as a miss.**
>
> **Predicted coverage: 2.0 of 2 layers on every layer patch.** Amendment 1's "may partially
> extrude" registration is **relaxed but NOT withdrawn**: 0.794 is inside published practice, so
> full extrusion is now the expectation rather than the hope — **but §16.3's rule still has only two
> measured endpoints in this lab, and a published value working elsewhere is not a measurement
> here.** **Coverage is measured post-extrusion per L-590 and reported whatever it is.** Coverage
> below 2.0 is a finding about our geometry, **not** a failure of the absolute-sizing fix.
>
> **Every y+ figure is a PREDICTION from a flat-plate correlation** (`Cf = 0.058 Re_c^-0.2`) that
> **ignores pressure gradient, rotation and three-dimensionality.** It is used **for consistency
> with the act's registered §A4.2 instrument, not because it is accurate.** **Only
> `simpleFoam -postProcess -func yPlus` read through `scripts/yplus_reader_guard.py` measures y+.**
>
> ### A2.6 WHAT DOES NOT CHANGE
>
> Amendment 1 §A1.5's structural finding stands unaltered and undecided: **the act's registered y+
> window and the registered blade refinement level are in tension on this geometry, and no
> layer-dictionary edit resolves it.** A registration-level question, not touched here. **No gate,
> threshold, cap or label is altered by this amendment** — none may be.

---

## 2. COST

No solver. Condition re-check, dictionary verification, four derivations, drafting. **Measured: 2.1
core-minutes**, single rank. Lane cumulative **38.5 core-minutes** ≈ **\$0.0329 derived, not
measured** at the owner-stated \$0.0513/core-h — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).
