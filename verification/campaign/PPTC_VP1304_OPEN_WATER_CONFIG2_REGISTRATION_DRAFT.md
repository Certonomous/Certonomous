# PPTC VP1304 open water — **CONFIGURATION 2**, drafted for the supervisor. **NOT FROZEN. NOT IN FORCE.**

**Drafted by:** lab-lane under `cfd-supervisor`, 2026-09-13. **Freezing is the supervisor's**, and the
freeze is the commit that adopts this file.

**This is a NEW REGISTERED CONFIGURATION, not an amendment.** The act pre-registration
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` is **frozen and has had first compute**,
so its gates are closed and no amendment may alter one (CLAUDE.md rule 2). This document registers a
**different configuration** of the same case. **It does not amend, supersede or strike the act
pre-registration**, which stands exactly as frozen at blob
`6a27740da10c77d813bbe94db564d0fbee5b03b4`, untouched by this lane throughout.

**Every row cites its source and, where it departs from published practice, its one-line registered
reason. No deviation without one.**

**Nothing left the box** (rules 7, 8). No solver launched by this lane.

---

## 1. THE SIX ADOPTED CHANGES — **and the sixth is not what was relayed**

| # | parameter | CONFIG-1 (frozen act) | **CONFIG-2 (registered here)** | source | reason |
|---|---|---|---|---|---|
| 1 | **downstream extent** | 6 D | **≥ 10 D** | Sikirica 2019 p. 6 (10 D); Klerebrant 2011 p. 2 (12 D); Cheng 2024 p. 4 (8 D); Sikirica's own survey *"values larger than 7D are usually adequate"* | ours was **below every published value and below the stated envelope**; adopted, not excused |
| 2 | **residual target** | 1e-5 on p, U | **1e-6 on p, U and turbulence** | Sikirica p. 8 (1e-6, all variables); Klerebrant p. 3 (1e-5, p/U/turbulence) | the two sources disagree; **stricter threshold taken from one, wider variable set from the other** |
| 3 | **stationarity** | 0.1 % over 500 it | **0.01 % over 1000 it**, logic stays **`and`** | Sikirica p. 8 | value adopted; **our `and` kept where Sikirica's is `or`, because ours is stricter** |
| 4 | **inlet turbulence intensity** | 1 % | **2 %** | Sikirica p. 7, *"estimated based on the calculated Reynolds values for external flow"* | adopted with its stated basis |
| 5 | **second closure** | k-ω SST only | **k-ω SST + realizable k-ε** — see §3 | Sikirica abstract + p. 15 | see §3: the purpose determines the closure, and it is **not** SA |
| 6 | **layer sizing** | `relativeSizes true`, relative thicknesses | **`relativeSizes false`, absolute thicknesses** — see §2 | ESI MB13 (verified, §2.2); Klerebrant p. 2 | **adopted IN PRINCIPLE; the specific published 0.5 mm figure is REFUTED by our own measurement** |

### 1.1 Row 6 — the correction, stated in one line as required

> **Registered reason:** *An absolute first layer is adopted in principle from published practice;
> the anchor is our own computation at n = 15 s⁻¹, not the published 0.5 mm figure, because that
> figure yields **y+ 85–115** at our conditions — roughly 2× above the window top.*

**The refutation is ours and is reproducible:** `cases/PPTC_VP1304/mesh/predict_yplus_from_first_layer.py`,
working in `cases/PPTC_VP1304/PRISM_A2_YPLUS_AND_L2_COMPUTED_FROM_OUR_SIDE.md`. Computed **from our
side only** — our n, our J, our fluid — with **no dependence on any published rotation rate**.
Klerebrant's 0.5 mm looked consistent only because **their `n` is unstated**, and their y+ 25–34 is
most likely a **patch average over blades, hub and shaft** against our **per-station blade** values.
**Not comparable quantities.**

**What Sanaa adopted is the principle — absolute rather than relative sizing — and that is exactly
what CONFIG-2 carries.**

---

## 2. THE LAYER BLOCK

### 2.1 As ruled and committed by the supervisor (`ef98fc88`), carried here unchanged

`nSurfaceLayers` **2**, `expansionRatio` **1.2**, `relativeSizes` **false**, `minThickness` at the
original's **0.1 ×** ratio, all four patches at **S = 1.000**:

| patch | level | local cell | `finalLayerThickness` | first layer | **S** | `minThickness` |
|---|---|---|---|---|---|---|
| `blades` | 5 | 0.6250 mm | **3.4091e-4 m** | 0.2841 mm | **1.000** | 3.4091e-5 m |
| `hub` | 4 | 1.2500 mm | **6.8182e-4 m** | 0.5682 mm | **1.000** | 6.8182e-5 m |
| `cap` | 4 | 1.2500 mm | **6.8182e-4 m** | 0.5682 mm | **1.000** | 6.8182e-5 m |
| `shaft` | 3 | 2.5000 mm | **1.3636e-3 m** | 1.1364 mm | **1.000** | 1.3636e-4 m |

**Predicted `blades` y+ at r/R 0.70: 48.4 / 51.5 / 54.0** at J = 0.7985 / 1.2021 / 1.4594 — **inside
the 30–60 window at every point of the sweep.**

`expansionRatio` stays **1.2**: the one layer parameter with two independent published sources —
Klerebrant p. 2 (*"1.2 as growth ratio"*) and **ESI MB13, `expansionRatio 1.20` on every patch**.

### 2.2 THE EXTERNAL EVIDENCE — **verified by this lane, not relayed**

The supervisor's report of a published propeller snappy dictionary is **correct, and I checked it
rather than repeating it.** Source: `/home/ubuntu/upstream/published-openfoam-setups/openfoam-hpc-tc/
compressible/rhoPimpleFoam/LES/marinePropeller/`, pointer commit `799c88e78`.

**Identity, read from its own README:** *"## MB13 MARINE PROPELLER"*, **ESI-Group, 2023**,
CC-BY-SA 4.0. **Four blades, D = 0.224 m** — **this is NOT PPTC VP1304**, so under Sanaa's §G it is
**not a published setup "of that case"**. It is admitted here as **published OpenFOAM mesher practice
for a marine propeller**, which is what it is, and **no PPTC-specific row is taken from it.**

Read from `system/snappyHexMeshDict`:
```
relativeSizes       false;
expansionRatio      1.2;
firstLayerThickness 0.00012;      // global default
minThickness        0.000001;
featureAngle        175;
propellerTip    { nSurfaceLayers 5; firstLayerThickness 0.0001; expansionRatio 1.20; }
propellerStem1  { nSurfaceLayers 5; firstLayerThickness 0.0002; expansionRatio 1.20; }
```
README: *"There are 5 layers in the boundary layer with expansion ratio of 1.2"*, ~4 M baseline cells,
and — **a practice statement worth adopting** — *"The first cell height is frozen to keep it
unchanged during next refinement levels."*

**I derived the stack ratio myself rather than accepting 0.794:** `blockMeshDict` is
1.2 × 2.4 × 1.2 m over `(40 80 40)` = a **uniform 0.03 m Cartesian background**;
`refinementSurfaces` puts `propellerTip` at level **(4 5)** and the stems at **(4 4)**.

| patch | first layer | level | local cell | stack | **S** |
|---|---|---|---|---|---|
| `propellerTip` | 1.0e-4 m | 5 | 0.03/2⁵ = 9.375e-4 | 7.4416e-4 | **0.794** |
| `propellerStem*` | 2.0e-4 m | 4 | 0.03/2⁴ = 1.875e-3 | 1.48832e-3 | **0.794** |

> **Tip and stem land on the SAME S because their absolute thicknesses track their refinement levels
> — exactly 2× for one level coarser. That is the per-patch pattern §2.1 derives independently, and
> it is now externally corroborated.**

**A difference worth registering, not glossing:** ESI specifies **`firstLayerThickness`**; CONFIG-2
specifies **`finalLayerThickness`**. Both are valid snappy thickness models. **Registered reason for
keeping `finalLayerThickness`:** *it is the form the frozen rung already uses, so the change is one
variable (relative → absolute) rather than two.* **If the supervisor prefers to match ESI's form
exactly, the equivalent `firstLayerThickness` values are the "first layer" column of §2.1** and
nothing else moves.

**EQUIVALENCE RECORDED so no reader has to convert.** For `nSurfaceLayers 2` and
`expansionRatio 1.2`, `firstLayerThickness = finalLayerThickness / 1.2`. At the **S = 0.794** values
now ruled (Amendment 2): `blades` **2.2557e-4 m**, `hub`/`cap` **4.5114e-4 m**, `shaft`
**9.0227e-4 m**. Specifying either key reproduces the same stack; **specifying both is an error
snappy does not diagnose**, so exactly one is written.

### 2.3 The "untested territory" hedge is **superseded**, with the limit of that stated

My amendment §A1.4 registered S = 1.000 as untested, on the two measured points 0.480 and 1.6808.
**The supervisor reports six published cases at S = 0.758, 0.794, 0.917, 1.197, 1.302, 1.600** — so
**1.000 sits inside published practice**, between 0.917 and 1.197, and the hedge no longer holds.

**Honest limit: I verified ONE of those six myself — the ESI 0.794, twice (tip and stem).** The other
five are **relayed from the sibling lane's record and not independently checked by me.** The
conclusion does not rest on any single one of them.

**And the y+ gate is robust across the whole published band**, which is the useful result:

| target S | `blades` `finalLayerThickness` | first layer | y+ at J 0.7985 / 1.2021 / 1.4594 |
|---|---|---|---|
| **1.000** (ruled) | 3.4091e-4 m | 0.2841 mm | **48.4 / 51.5 / 54.0** |
| 0.917 | 3.1261e-4 m | 0.2605 mm | 44.4 / 47.2 / 49.5 |
| **0.794** (ESI) | 2.7068e-4 m | 0.2256 mm | **38.4 / 40.9 / 42.9** |
| 0.758 | 2.5841e-4 m | 0.2153 mm | 36.7 / 39.0 / 40.9 |

> **Every value in the published band keeps us inside the 30–60 window.** The choice of S within
> published practice **does not endanger the y+ gate**, which means it can be made on extrusion
> margin alone.

**OPTION OFFERED, NOT TAKEN — the supervisor's ruling stands unless changed.** **S = 0.794** would
match the one dictionary this lab has actually verified, exactly, **and still lands y+ ≈ 41
mid-window** with more extrusion margin than 1.000. Per-patch: `blades` 2.7068e-4, `hub`/`cap`
5.4136e-4, `shaft` 1.0827e-3 m; `minThickness` at the same 0.1× ratio. **I am not changing the
ruling; I am putting the alternative and its evidence in front of it.**

---

## 3. THE SECOND CLOSURE — **the purpose decides it, and it is not SA**

Sikirica ran **both** Realizable k-ε and SST k-ω and concluded (abstract, p. 15):
> *"for low and high ratios, structured grids in conjunction with Realizable k-ε model can achieve
> more accurate results."*

**That is a specific, published, testable claim about THIS propeller at the sweep ends — and our
registered sweep ends, J = 0.7985 and J = 1.4594, are exactly where it applies.**

| candidate | what the rung would then be testing |
|---|---|
| **Realizable k-ε** | **tests Sikirica's published finding directly** — does k-ε beat SST at our sweep ends, on our grid, at our n? A falsifiable external claim. |
| Spalart–Allmaras | tests **robustness** to closure choice. SA is **neither** closure Sikirica compared, so **it cannot confirm or refute their finding.** |

> **RECOMMENDED: Realizable k-ε**, with the rung's registered purpose stated as *"test Sikirica's
> published claim that realizable k-ε is more accurate than SST at low and high J on this
> propeller."* **If instead the purpose is robustness-to-closure, SA is the right pick and the
> purpose should say so.** **The two purposes are different rungs and should not be conflated;
> the supervisor picks the purpose, and the closure follows from it.**

---

## 4. THE SEVEN KEPT DEVIATIONS — reasons unchanged

| # | parameter | ours | published | **registered reason** |
|---|---|---|---|---|
| 1 | passage topology | 72° cyclic wedge | full 360° (Klerebrant, Gaggero, Cheng); 72° block-structured (Sikirica) | *"Geometry and topology differ: passage vs 360°."* Bounded by the registered full-360 cross-check (act §B.7 item 4, ≤ 0.5 % in KT) |
| 2 | domain radius | 4 D | 2.5 D, 2.52 D, 1.3 D, ±1.2 D box | *"Ours is larger, not smaller; blockage is bounded more tightly than any published setup, so the deviation is conservative for the graded quantity."* |
| 3 | MRF axial extent | ±0.5 D | 9.77 D downstream (Klerebrant); ≈4.8 D (cfdsupport) | *"A long MRF zone places the wake in the rotating frame, changing what the wake means for the LDV comparison (act §B.8). Ours keeps the graded wake in the stationary frame."* |
| 4 | wall treatment | wall functions, y+ 30–60 | wall-resolved y+≈1 (Sikirica); **wall functions (Klerebrant, Gaggero, cfdsupport)** | *"Wall-modelled by registration; the act's §B.5 names wall-resolved as the next rung, and three of four OpenFOAM-family sources are wall-functioned."* |
| 5 | turbulence convection | second-order `limitedLinear 1` | first-order (Klerebrant p. 2) | *"Second-order retained as the stricter choice; first-order is the registered fallback if the SIMPLE loop stalls, and its use is recorded."* |
| 6 | force integration | blades + hub + shaft | blades only (Klerebrant p. 2) | *"Act §B.3 fixes the comparator as the 'including hub' table (Report 3752 p. 2.11) and therefore the surfaces."* |
| 7 | J range | 6 measured points, 0.7985–1.4594 | 0–1.4422 (Sikirica); 0.5–1.6 (cfdsupport) | *"Fixed to measured points so the gate needs no interpolation."* |

**MRF zone diameter is NOT a deviation:** ours is 1.3 D with a registered sensitivity at 1.6 D, and
published values are **1.47 D** (Klerebrant) and **1.5 D** (cfdsupport) — **our registered pair
brackets both.** To be stated on the certificate.

---

## 5. WHAT THIS DRAFT DOES NOT DO

- **It freezes nothing.** The supervisor's commit is the freeze.
- It does not amend, supersede or strike the frozen act pre-registration, which is untouched.
- It does not change the PRISM-A2 amendment (`ef98fc88`); §2.1 carries that ruling unchanged and
  §2.3 offers an alternative **without taking it**.
- It does not pick the second closure — §3 puts the choice and its consequence; the purpose is the
  supervisor's to set.
- It does not re-verify five of the six published S values (§2.3).
- **It registers no result.** Every y+ figure is a **prediction** from the act's §A4.2 flat-plate
  correlation, which ignores pressure gradient, rotation and three-dimensionality; it is used for
  consistency with the registered instrument, **not because it is accurate**. **Only
  `simpleFoam -postProcess -func yPlus` through `scripts/yplus_reader_guard.py` measures y+.**

## 6. COST — REGISTERED BEFORE ANY RUN (CLAUDE.md rule 12)

**A proposal with no cost is disqualified.** This section prices CONFIG-2's own compute. **The rate
\$0.0513/core-h (c7a.4xlarge) is OWNER-STATED, NOT MEASURED — the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so **every dollar figure below is DERIVED, not measured.**

### 6.1 A CORRECTION TO THE ANCHORS I WAS HANDED

I was asked to use "the gate ran 4.6 core-min at 28.4 GB". **Neither number checks out as a mesh
gate, and I am not building an estimate on them.**

- The **4.6 core-min** is at `docs/PUBLISHED_SETUP_COMPARISON_2026-09-13.md:781`, and its own
  sentence reads *"from this lane's own elapsed tool time"* for writing a comparison document.
  **It is a documentation lane's tool time, not a mesh gate run**, and it prices nothing here.
- **"28.4 GB"** occurs in this repository only in `verification/queue/runner.out`, as
  `MemAvailable=28.4 GB` in **box-load lines dated 2026-08-30** — unrelated to PPTC meshing.

**The anchors used below are the ones I could verify.** Flagged rather than quietly substituted,
because an estimate built on a misattributed anchor is exactly the defect `C-89` recorded: *"a cost
basis that names a term without a number has not priced it."*

### 6.2 VERIFIED ANCHORS

| anchor | value | provenance | status |
|---|---|---|---|
| act §9 meshing line | **308 core-min** | `PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md:655` | **verified by this lane** |
| act §9 design-point family (coarse+medium+fine) | **160 + 540 + 1800 = 2,500 core-min** | same table, lines 650–652 | **verified** |
| act §9 post-processing line | **150 core-min** | same table | **verified** |
| snappy **layer phase**, 1 rank, serial | **2114.26 s = 35.2 core-min** | `F360_coarse/log.snappyHexMesh:3326`, cited in PRISM-A2 §6 | **measured**, and it is the phase that *discarded*; one that extrudes does more work |
| meshing phase **actual** | **1,138.3 all-in / 726.1 waste / 412.1 productive core-min**, ratio **3.70× all-in, 1.34× cleaned**, **zero admissible meshes** | `docs/COST_CALIBRATION.md` row `C-20260913T170047.541222Z-fb7e9f54` | **relayed with a provenance caveat carried in that row itself** — the actuals are a session tally not carried by any committed record; I did not re-derive them |

### 6.3 THE ESTIMATE

**Domain growth.** CONFIG-2 extends downstream 6 D → ≥ 10 D with upstream unchanged at 3 D, so the
wedge length goes 9 D → 13 D, a **volume ratio of 1.444**. The added region is **far-field and
coarsely refined**, so **cell growth is bounded above by 1.444 and will be less**; 1.444 is used as
the conservative multiplier and **labelled as a bound, not a prediction**.

| item | ranks | basis | **estimate** |
|---|---|---|---|
| mesh rebuild, 3 levels, CONFIG-2 domain | 4–8 | act §9 meshing 308 × 1.444 domain bound | **445 core-min** |
| layer extrusion at the amended dictionary | 1 | measured 35.2 core-min for the discarding phase; an extruding run does more, and PRISM-A2 registered ×4 on the same anchor | **140 core-min** |
| mesh gate — `checkMesh` + birth certificates, 3 levels | 1–4 | act §9 post-processing line 150, meshing share | **60 core-min** |
| design-point family, SST, 3 levels | 48 | act §9 2,500 × 1.444 | **3,610 core-min** |
| design-point family, **realizable k-ε** (§3) | 48 | same work, second closure | **3,610 core-min** |
| tightened convergence surcharge | — | residual 1e-5 → **1e-6** and stationarity 0.1 %/500 → **0.01 %/1000** both demand more iterations; **no measured basis exists for the extra count**, so it is carried as an explicit **+40 %** on the two families and **named as an assumption, not a measurement** | **+2,888 core-min** |
| **48-rank parallel-efficiency allowance** | 48 | the act sized the family at **4–8 ranks**; at 48 ranks per-core efficiency falls and **core-minutes rise for the same work**. **No measurement of this case at 48 ranks exists**, so **+25 %** on the solve lines is carried as a **stated assumption** | **+2,527 core-min** |
| post-processing, renders, reconstruct | — | act §9 150 | **150 core-min** |
| **TOTAL ESTIMATE** | | | **≈ 13,430 core-min ≈ 223.8 core-hours** |
| **CAP** | | ×1.5 on the total, stated as margin | **20,145 core-min** |

**Dollars: 223.8 core-h × \$0.0513/core-h = \$11.48 DERIVED, NOT MEASURED.** At the cap,
**\$17.22 derived.**

**Sanaa's directive #17 (2026-09-12) means no run is stopped by a cap. It does not mean a cap goes
unwritten — a cost nobody wrote down is what disqualifies a proposal.**

### 6.4 THE HONEST WEAKNESSES OF THIS ESTIMATE, NAMED

1. **The meshing anchor has a 3.70× all-in miss behind it and produced ZERO admissible meshes.**
   Scaling 308 core-min by a domain ratio prices *the estimate that already missed*, not the work.
   **The registered expectation is therefore that this line is low**, and the calibration row must
   say so when CONFIG-2 completes.
2. **Two lines are assumptions, not measurements** — the +40 % convergence surcharge and the +25 %
   48-rank allowance. **Neither has a measured basis in this lab.** They are named separately so
   that, per `C-89`'s rule, no term is left unpriced *and* no assumption is dressed as a measurement.
3. The act's coarse level was sized at 0.8 M cells and **measured 3.94 M** (`C-…fb7e9f54`). **If
   that discrepancy persists in CONFIG-2, every solve line is under-priced by roughly the same
   factor** — this is flagged, not absorbed.
4. **Waste will be named separately and never folded into the ratio**
   (`COMPUTE_BUDGET_CHARTER.md` §6).

### 6.5 CALIBRATION OBLIGATION

**At CONFIG-2's completion — rung graded or case closed — a row lands in `docs/COST_CALIBRATION.md`**
stating the ratio actual/predicted, attributing the gap (contention, waste, misprediction) with
**waste named separately**, actuals in core-minutes from logs and dollars derived at the recorded
rate and labelled derived. **CLAUDE.md rule 12: a completion report without this comparison is
incomplete.**

### 6.6 THE COST OF DRAFTING THIS DOCUMENT

No solver. **Measured: 3.6 + 2.4 = 6.0 core-minutes**, single rank. Lane cumulative **40.9
core-minutes** ≈ **\$0.0350 derived, not measured**.
