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
