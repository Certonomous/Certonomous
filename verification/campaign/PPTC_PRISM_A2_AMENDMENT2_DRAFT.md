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
