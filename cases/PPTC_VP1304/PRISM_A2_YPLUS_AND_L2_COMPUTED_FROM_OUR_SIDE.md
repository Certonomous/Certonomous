# PRISM-A2: computed from OUR side. The y+ concern is CONFIRMED, the published 0.5 mm anchor is NOT sound, and there is a SECOND defect — the registered stack is 2.0 local cells.

**Team:** cfd. **Lane:** lab-lane under `cfd-supervisor`. **Date:** 2026-09-13.
**Computes only. Amends nothing.** Every number below is a prediction for the supervisor to rule
on. No gate, threshold, cap or label is altered; no frozen file is edited. `PRISM_A2_absthick`
does not exist — **PRISM-A2 has had no compute**, so the pre-compute amendment window of rule 2 is
open, and closes the moment anyone builds it.

**Artifact:** `cases/PPTC_VP1304/mesh/predict_yplus_from_first_layer.py` — run it to reproduce
every figure here.

---

## 0. THE INSTRUMENT IS THE REGISTERED ONE, AND ITS CONTROL PASSES

The method is **not chosen here.** It is the one frozen in the act pre-registration §A4.2:
`Cf = 0.058·Re_c^-0.2`, `Re_c = U·c(r)/ν`, `u_τ = sqrt(0.5·Cf)·U`, `y+ = y_centre·u_τ/ν`,
with ν = 1.124e-6 m²/s, ρ = 998.99 kg/m³, **n = 15 s⁻¹**, D = 0.250 m.

**The script's selftest reproduces A4.2's frozen table exactly** — that is the control that shows
it is running the registered instrument and not a new one:

| station | A4.2 published | script |
|---|---|---|
| r/R 0.30 | U 4.632, u_τ 0.2233, **y+ 62** | U 4.632, u_τ 0.2234, **y+ 62.1** |
| r/R 0.70 | U 8.773, u_τ 0.3831, **y+ 107** | U 8.773, u_τ 0.3831, **y+ 106.5** |
| r/R 0.90 | U 11.018, u_τ 0.4804, **y+ 134** | U 11.018, u_τ 0.4804, **y+ 133.6** |

**One correction found by that control, and it is worth recording.** A first attempt used `c0.7`
at every station; it reproduced r/R 0.70 and **missed the other two**. A4.2 therefore used the
**local chord**, which it does not print. The local chords were recovered from A4.2's own printed
`U` and `Re_c` as `c = Re_c·ν/U`: **0.07328 / 0.10416 / 0.08416 m**. **Control on the recovery:**
the recovered r/R 0.70 value is **0.10416 m** against the independently known **c0.7 = 0.10417 m**
(Report 3752 Table 1, Sanaa §B.2) — a 1e-5 agreement that could not arise by accident. The chords
are **used, not assumed.**

**`y_centre` is HALF the first layer.** A4.2's own layerless row fixes the convention: a 0.625 mm
surface cell with no layer has its centre at 0.3125 mm. A first *layer* of thickness `t1` puts the
first cell *centre* at `t1/2`. That is the convention used throughout below.

---

## 1. OUR PREDICTED y+ AT PRISM-A2's REGISTERED FIRST LAYER — **CONFIRMED, BUT MILDER THAN MY ESTIMATE**

PRISM-A2 registers `finalLayerThickness 3.125e-4` m, `expansionRatio 1.2`, `nSurfaceLayers 6`
(`verification/campaign/PPTC_PRISM_A2_PREREGISTRATION.md:121–126`), so

> **t1 = 3.125e-4 / 1.2⁵ = 1.2559e-4 m = 0.1256 mm**, first cell centre **0.0628 mm**.

Predicted y+ on `blades`:

| J | r/R 0.30 | r/R 0.70 | r/R 0.90 |
|---|---|---|---|
| 0.7985 (smoke) | 12.5 | 21.4 | 26.8 |
| **1.2021 (design)** | 15.1 | **22.8** | 27.9 |
| 1.4594 | 17.0 | 23.9 | 28.8 |

**Every station at every J is below the registered 30–60 window.** The highest value anywhere is
**28.8**, which is also below the **amended 30–300** lower bound.

**The supervisor's concern is CONFIRMED: PRISM-A2 as registered would miss its own window, low.**

**Correction to my own earlier figure, stated plainly.** §2.1 of the reconciliation table estimated
**y+ 6–9** by scaling KK's measurement. **That estimate was too pessimistic by roughly 2–3×.** The
registered method, run on our own conditions, gives **12–29**. The scaling assumption was the
weakness the supervisor identified, and it was the wrong number — the conclusion survives, the
magnitude does not. **The reconciliation table's §2.1 should be read as superseded by this file.**

---

## 2. THE FIRST LAYER THAT PUTS US MID-WINDOW AT y+ ≈ 45

| J | r/R 0.30 | r/R 0.70 | r/R 0.90 |
|---|---|---|---|
| 0.7985 | 0.4529 mm | 0.2640 mm | 0.2106 mm |
| **1.2021** | 0.3741 mm | **0.2482 mm** | 0.2023 mm |
| 1.4594 | 0.3332 mm | 0.2369 mm | 0.1960 mm |

> **Proposed anchor: t1 ≈ 0.25 mm** (r/R 0.70, design point J = 1.2021).
> **That is 1.98× PRISM-A2's registered 0.1256 mm, and 0.50× the published 0.5 mm.**

Because y+ varies by ~2× from root to r/R 0.90, **no single first layer puts every station at 45.**
At t1 = 0.2482 mm the blade spans roughly **y+ 30 (root) to 56 (r/R 0.90)** — which happens to fill
the 30–60 window almost exactly. That is a convenient result and should be **verified by
measurement**, not assumed.

---

## 3. IS THE PUBLISHED 0.5 mm SOUND? — **NO. AND THE ANSWER IS NOT THE ONE HOPED FOR.**

Klerebrant's **0.5 mm** first layer, evaluated at **our** n = 15 s⁻¹ — no reliance on their
rotation rate at all:

| J | r/R 0.30 | r/R 0.70 | r/R 0.90 |
|---|---|---|---|
| 0.7985 | 49.7 | 85.2 | 106.9 |
| **1.2021** | 60.1 | **90.7** | 111.2 |
| 1.4594 | 67.5 | 95.0 | 114.8 |

**At our conditions the published 0.5 mm gives y+ ≈ 85–115 over most of the blade — roughly 2×
above the top of our 30–60 window.** It is inside the amended 30–300, and it is **not** mid-window.

**So the anchor is NOT sound as a direct transplant, and it only looked sound because KK's `n` was
unknown.** The supervisor's hoped-for outcome does not hold, and I am not going to report that it
does.

**Why KK can measure y+ 25–34 from the same 0.5 mm while our arithmetic says 85–115 here** — two
candidate explanations, neither verified: **(a)** KK's open-water `n` is unstated and may be well
below 15 s⁻¹; **(b)** KK's Table 2 is most likely a **patch-averaged** figure over blades, hub and
shaft, and the hub and shaft run at far lower local speeds, which would drag an average down by
exactly this sort of factor, whereas the numbers above are **per-station blade** values. **These are
not comparable quantities**, and that — not either paper being wrong — is the likeliest reading.

**The useful consequence is the one the supervisor wanted:** the recommendation in §2 is computed
**entirely from our side** and **does not depend on KK's rotation rate, y+ convention, or averaging
domain.** t1 ≈ 0.25 mm stands whatever KK did.

---

## 4. THE SECOND DEFECT — **THE REGISTERED STACK IS 2.0 LOCAL CELLS**, AND IT IS INDEPENDENT OF y+

`MESH_STANDARD.md` §16.3 rule **L2**: a stack asking more than **one local cell** of total
thickness *"is asking the mesher for room it does not have. Above 1.0, expect collapse."* Its
measured reference pair: **DrivAerML S = 0.480 → EXTRUDED**; **Certonomous DrivAer S = 1.6808 →
COLLAPSED (2.50 of 5 layers).**

Blades local cell = 20 mm background / 2⁵ = **0.625 mm**.

| case | t1 | stack | **S [local cells]** | verdict |
|---|---|---|---|---|
| **PRISM-A2 as registered, 6 layers** | 0.1256 mm | 1.2471 mm | **1.995** | **above 1.0 — and above the 1.6808 that collapsed** |
| y+ = 45 anchor, 6 layers | 0.2482 mm | 2.4644 mm | **3.943** | far above |
| published 0.5 mm, 6 layers | 0.5000 mm | 4.9650 mm | **7.944** | far above |

*(L2's own published formula `S = t_f·Σr^-i` cross-checks the first-layer form: **1.995 vs 1.995**.)*

**PRISM-A2 may therefore fail to extrude for a reason that has nothing to do with y+** — and §16.3
warns explicitly: *"Do not expect a too-thick stack to give you fewer layers. Expect it to give you
none."* **This is a defect in PRISM-A2 that my reconciliation table did not catch and that the y+
question would not have surfaced.**

**In fairness to PRISM-A2:** §16 is **v1.11, committed today at `50ce30f5`**, *after* PRISM-A2 was
frozen at `748d26915`. **PRISM-A2 could not have complied with a rule that did not yet exist**, and
it states no L2 exception because there was none to state. This is a new constraint meeting an old
registration, not negligence.

---

## 5. THE TWO CONSTRAINTS COLLIDE. **THEY CANNOT BOTH BE MET AT 6 LAYERS, AT ANY FIRST-LAYER HEIGHT.**

Raising y+ requires a **thicker** first layer, which makes the stack **taller**, which makes L2
**worse**. Feasible set at ratio 1.2, blades local cell 0.625 mm, design point J = 1.2021, r/R 0.70:

| nSurfaceLayers | largest t1 under L2 | **y+ at that t1** | both constraints met? |
|---|---|---|---|
| 1 | 0.6250 mm | 113.3 | yes (but y+ above window) |
| **2** | **0.2841 mm** | **51.5** | **YES — mid-window** |
| **3** | **0.1717 mm** | **31.1** | **YES — just inside** |
| 4 | 0.1164 mm | 21.1 | no |
| 5 | 0.0840 mm | 15.2 | no |
| **6 (registered)** | **0.0629 mm** | **11.4** | **NO** |

> **At the registered `nSurfaceLayers 6` and `expansionRatio 1.2`, no first-layer height satisfies
> both y+ ≥ 30 and L2 ≤ 1.0.** The maximum y+ obtainable under L2 at 6 layers is **11.4**.
> **This is the DrivAer R5 collision, and it is in the registration, not waiting in a build.**

**Coarsening the blades does not rescue it either** — the stack at y+ = 45 with 6 layers is
2.464 mm regardless, so S = 3.943 at level 5, **1.971** at level 4, **0.986** at level 3. Only
**level 3** clears L2, and level 3 is a 2.5 mm blade cell, which cannot survive the registered
leading-edge gate (≥8 cells across the LE radius). **Not a viable route.**

### 5.1 What this lane proposes — **proposals only; the supervisor rules**

1. **`nSurfaceLayers` 6 → 2**, with **`finalLayerThickness` 3.41e-4 m** (t1 = 0.2841 mm, ratio 1.2)
   → **y+ ≈ 51 at r/R 0.70, S = 1.00.** Both constraints met, y+ mid-window.
2. **Or `nSurfaceLayers` 6 → 3**, `finalLayerThickness` 2.47e-4 m (t1 = 0.1717 mm)
   → **y+ ≈ 31, S = 1.00.** More layers, but y+ sits on the window edge with no margin.
3. **Either way `minThickness` must be re-derived**, since it is registered as a fraction of the
   final layer and the final layer moves.
4. **Whichever is chosen, register the predicted y+ before the build**, so the measurement can
   falsify it (the §A4.2 discipline).

**`expansionRatio` 1.2 is left alone** — it is the one layer parameter with a published source
(Klerebrant p. 2, exactly 1.2), and reducing it does not fix L2 anyway (uniform layers at 6×0.248 mm
still give S = 2.38).

---

## 6. WHAT IS NOT ESTABLISHED

- **All y+ figures are PREDICTIONS from a flat-plate correlation, not measurements.** The
  correlation ignores pressure gradient, rotation, three-dimensionality and the actual blade
  boundary layer. §A4.2 registered it as the instrument; it is used here for **consistency with the
  registration**, not because it is accurate. Only `simpleFoam -postProcess -func yPlus` through
  `scripts/yplus_reader_guard.py` measures y+.
- The root-to-tip y+ spread (§2) means "mid-window" is a statement about r/R 0.70, not the patch.
- Whether L2 collapse actually occurs at S = 1.995 is a **prediction from one measured DrivAer
  pair**, not a law. It may extrude partially.
- §3's explanation for the KK discrepancy is **two candidate readings, neither verified.**

## 7. COST

No solver. Script authoring, one failed control, one recovery, three runs. **Measured: 4.8
core-minutes**, single rank. Lane cumulative **27.5 core-minutes**, ≈ **\$0.0235** derived at the
owner-stated \$0.0513/core-h — **derived, not measured**; the box cannot read its own billing.
No pre-registered estimate for an analysis task, so no calibration ratio is claimable.
