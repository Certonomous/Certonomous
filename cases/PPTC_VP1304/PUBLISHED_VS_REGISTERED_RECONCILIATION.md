# PPTC VP1304 — PAPER VALUE | OUR VALUE, every row, no discrepancy unexplained

**Team:** cfd. **Lane:** lab-lane under `cfd-supervisor`. **Date:** 2026-09-13.
**Purpose, in Sanaa's words as relayed:** *"i dont want any discrepancy that way we can ensure to
reproduce these results."*

**Built from the three ingests**, which carry the title-page verifications and the page citations:
- `PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md` (commit `99cacfb12`)
- `PUBLISHED_OPENFOAM_SETUP_INGEST_SMP11.md` (commit `074d702bf`)
- `PUBLISHED_SNAPPYHEXMESH_INGEST_CHENG_2024.md` (commit `26dd894bd`)

**Sanaa's §G split governs which source may fill which row:** mesher rows may only be filled from an
**OpenFOAM** source; numerics and domain practice may be filled from **any finite-volume** source.

**THIS FILE CHANGES NOTHING.** Every "proposed" cell is a proposal to `cfd-supervisor`, who rules and
freezes. No gate, threshold, cap or label is altered here. The act pre-registration is frozen and has
had first compute; these rows land as a **new registered configuration**, not as amendments to it
(CLAUDE.md rules 2 and 6). Frozen blob still `6a27740da10c77d813bbe94db564d0fbee5b03b4`.

**Sources, short names used in the SRC column:**

| tag | source | OpenFOAM? | snappy? |
|---|---|---|---|
| **CH** | Cheng et al. 2024, OMAE2024-125991 / arXiv:2405.15133 | **YES** | **YES** |
| **KK** | Klerebrant Klasson & Huuva 2011, smp'11 II-2.1 | **YES** | no (ANSA 13.10) |
| **GG** | Gaggero, Villa & Brizzolara 2011, smp'11 II-2.8 | **YES** | no (unstructured) |
| **SK** | Sikirica et al. 2019, JMSE 7, 374 | **no** (Fluent + STAR-CCM+) | no |
| **QQ** | smp'11 questionnaire on viscous flow methods, 14 participants | mixed | — |

---

## 0. THE LINE THAT STOPS A WRONG VALIDATION — READ THIS BEFORE ANY OTHER ROW

| | PAPER | OURS |
|---|---|---|
| **rotation rate `n`** | **SK: 10 s⁻¹** (p. 7, p. 10) · **CH: 25 s⁻¹** (Table 1, p. 4) · **KK: NOT STATED** for the open-water case in the text read | **15 s⁻¹**, SVA test 11F0395 |

**Three published sources, three different rotation rates, none of them ours.**

**No published KT, KQ or η in any of these papers may be used as a band for our act.** Report 3752's
own **n = 10 and n = 15 curves cross near J ≈ 1.3** — Sanaa registered that crossing in §B.4 as the
measured Reynolds effect. A number taken from SK at n = 10 and compared to our n = 15 result is a
comparison between two different experiments.

Their numbers are **cross-checks on direction and magnitude only**, and are labelled as such
everywhere below. **Our band remains the smp'11 participant scatter (§B.4), unchanged.**

---

## 1. STRUCTURAL ROW — NOT A PARAMETER, AND IT EXPLAINS THE 95.5×

| | PAPER | OURS |
|---|---|---|
| **background topology** | **CH: Cartesian box**, full 360° · **KK: full 360°**, ANSA · **GG: full 360°**, unstructured · **SK: block-structured 72° passage** | **72° `blockMesh` wedge + a 2 mm numerical `axisRod`** |

**Three of the four published setups mesh the full propeller.** The one that uses a 72° passage (SK)
is **block-structured**, where a wedge closes on a collapsed axis edge legally. **No published setup
puts an octree mesher on a wedge.**

**This single row is the cause of the layer-thickness poisoning.** `hexRef8::getLevel0EdgeLength()`
returns the **global minimum** level-0 edge. On our wedge that is the azimuthal chord of the 2 mm rod,
`2·0.002·sin(π/60) = 2.09343825e-04 m`, against an intended base of `0.020 m` — a factor of
**95.53×**. On a Cartesian box every level-0 cell is a cube, so the global minimum level-0 edge *is*
the base cell, and the defect cannot arise.

CH's "rod" (Fig. 1b caption, *"propeller (accompanied by rod)"*) is the **physical propeller shaft**.
Ours is a numerical body inserted so a wedge can close (`make_blockmesh.py:11–38`, `R_AXIS` at `:63`).

**This is why no published source could have warned us**, and it now stands as **§16 of
`docs/standards/MESH_STANDARD.md` (v1.11, `50ce30f5`)**.

**REGISTERED REASON (proposed):** *"Geometry and topology differ: published setups mesh the full 360°
propeller; ours is a 72° cyclic passage, which requires an axis body a box background does not."*
**Or** — the supervisor's call, not a lane's — adopt the box + full 360° and delete the rod, the tiny
level-0 edge and the cyclic patches in one move, at roughly 5× the cells.

---

## 2. MESH ROWS — **OpenFOAM sources only** (Sanaa's §G split)

**"NOT PUBLISHED" is the honest cell for most of this block and is not a gap in our extraction.**
Token counts across the entire PPTC corpus now on disk: `snappyHexMesh` appears in **CH only**;
**`relativeSizes` 0**, **`nSurfaceLayers` 0**, **`expansionRatio` 0**, **`finalLayerThickness` 0**,
**`minThickness` 0**, **`featureAngle` 0** — in *every* source including CH. **In SK these rows have
no counterpart at all** (`snappy` 0, `blockMesh` 0, `relativeSizes` 0) because SK is a Fluent and
STAR-CCM+ paper. **Filling any of these cells with a plausible value is exactly the invented setup
§G refuses.**

| # | parameter | PAPER | SRC | OURS | verdict |
|---|---|---|---|---|---|
| 1 | mesher | **snappyHexMesh**, *"the SnappyHexMesh utility implemented in OpenFOAM"* | **CH p. 4** | snappyHexMesh | **AGREE — now sourced** |
| 2 | **base cell size** | **NOT PUBLISHED as a length.** Refinement is controlled *"by changing the base cell scale on the input/output patches"* | CH Table 2 caption, p. 5 | **20.0 mm** at family ratio 1.0 (`check_tessellation_adequacy.py:47`); 13.33 / 8.89 mm at ratio 1.5 / 2.25 | **NOT PUBLISHED** — ours stands unsourced |
| 3 | **refinement level, blades** | **NOT PUBLISHED** as a level | — | **(5 5)** → surface cell **0.625 mm** (`make_snappy.py:37–45`) | **NOT PUBLISHED** |
| 4 | **refinement level, hub / cap** | **NOT PUBLISHED** | — | **(4 4)** → **1.25 mm** | **NOT PUBLISHED** |
| 5 | **refinement level, shaft** | **NOT PUBLISHED** | — | **(3 3)** → **2.5 mm**; shaftExtension (2 2) → 5 mm | **NOT PUBLISHED** |
| 6 | **tip / tip-vortex refinement** | normalised tip-vortex cell **x̂_tv = x_tv/S = 0.004 / 0.006 / 0.009** across the three levels | **CH Table 2, p. 5** | `tipVortex` region at blade level − 1, 1 D downstream (`make_snappy.py:152`) | **PUBLISHED AS A RATIO, ours as a level.** Directly checkable once our mesh exists — **proposed: report x̂_tv per level on the birth certificate** so the two become comparable |
| 7 | **`nSurfaceLayers`** | **NOT PUBLISHED in any OpenFOAM source.** *(KK, a non-snappy OpenFOAM source, states* **5 prism layers** *— p. 2)* | KK p. 2 | **6** (`make_snappy.py:48`) | **6 vs KK's 5** — close; **no snappy source exists** |
| 8 | **expansion ratio** | **KK: 1.2** — *"Five prism layers with **1.2 as growth ratio**"* | **KK p. 2** | **1.2** (`make_snappy.py:49`) | **AGREE EXACTLY** |
| 9 | **first layer thickness** | **KK: 0.5 mm, stated as an ABSOLUTE length** — *"a starting length of 0.5 mm"* (= 0.002 D) | **KK p. 2** | **relative**: `finalLayerThickness 0.5` with `relativeSizes true` → intended first layer ≈ **0.126 mm**, poisoned to ≈ **1.3 µm** | **DISAGREE, twice over — see §2.1** |
| 10 | **`relativeSizes`** | **NOT PUBLISHED — 0 occurrences anywhere.** The one snappy source (CH) does not print its dictionary; the two absolute-sizing OpenFOAM sources (KK, GG) are not snappy, so neither is evidence about the keyword | — | **`true`** (`make_snappy.py:165`) | **PRISM-A2 sets `false`.** No published source contradicts that; none endorses `true` either. **Silence is not evidence** (rule 3) |
| 11 | **`minThickness`** | **NOT PUBLISHED** | — | **0.05**, relative (`make_snappy.py:170`) | **NOT PUBLISHED** — and note it is **relative**, so PRISM-A2's switch must re-express it too |
| 12 | **`featureAngle`** | **NOT PUBLISHED** | — | **130** (layers); `resolveFeatureAngle` **30** (castellation) (`make_snappy.py:151,171`) | **NOT PUBLISHED** |
| 13 | other layer controls (`nGrow`, `maxThicknessToMedialRatio`, `nLayerIter`, `slipFeatureAngle`, …) | **NOT PUBLISHED** | — | `make_snappy.py:171–175` | **NOT PUBLISHED** |
| 14 | castellation controls (`nCellsBetweenLevels`, `maxGlobalCells`, `maxLocalCells`) | **NOT PUBLISHED** | — | **3**, 60e6, 4e6 (`make_snappy.py:139–141`) | **NOT PUBLISHED** |
| 15 | snap controls (`nRelaxIter`, `nFeatureSnapIter`, `explicitFeatureSnap`) | **NOT PUBLISHED** | — | 5, 15, `true` (`make_snappy.py:160–163`) | **NOT PUBLISHED** |
| 16 | **achieved y+, per grid level** | **CH: 92 → 40 → 19** · **KK: 25–34** (Table 2, J 0.6–1.2) · **QQ envelope: <1 to 160**, clustering **30–50** | **CH Table 2 p. 5; KK p. 4; QQ p. 3** | registered window **30–60**; amended **30–300** for the smoke; prediction **50–200** | **our window sits inside the published cluster** — see §2.1 |
| 17 | **cell count** | **CH: 18.0 / 26.9 / 40.4 M**, full propeller (rotor 15.0/22.5/33.7 + stator 3.0/4.5/6.7) · **KK: 4.5 M / 11 M** full propeller · **GG: 1.4 M** full propeller · **SK: 1.7 M** per 72° passage | CH Table 2 p. 5; KK p. 2; GG p. 2; SK p. 9 | **0.8 / 2.7 / 9 M per 72° passage** ≈ **4 / 13.5 / 45 M** full-propeller equivalent | **our fine ≈ CH's finest; our coarse is 4.5× below CH's coarsest.** Our medium (13.5 M equiv.) sits between KK's 11 M and CH's 18 M — **inside the published envelope** |
| 18 | mesh generation cost | **CH: ~4.5 h on 4×40 G** for 40.4 M cells | CH p. 4 | — | context for our meshing budget |
| 19 | mesh quality gates | **KK: "negligible skewness"** (BEM mesh only); **SK: "acceptable ranges with occasional outlier cells"** — **no numbers in any source** | KK p. 3; SK p. 4 | maxNonOrtho **65** (relaxed 70), maxBoundary/InternalSkewness **4** (`make_snappy.py:180–185`) | **NOT PUBLISHED as numbers.** Ours is stricter than snappy's own defaults (`maxBoundarySkewness` 20) |

### 2.1 Row 9 and row 16 together — the finding this table surfaces

KK publishes a **0.5 mm** first layer and measures **y+ 25–34**. Our `relativeSizes true` with
`finalLayerThickness 0.5` on a 0.625 mm blade surface cell gives an **intended** first layer of
**≈0.126 mm** — before any poisoning — which is **4× thinner than the published value**.

Scaling KK's measured y+ by first-cell-centre height as a crude proportionality, our *intended*
relative sizing would land near **y+ ≈ 6–9**, i.e. **below our own registered 30–60 window**.

> **This is an ESTIMATE, not a measurement.** It assumes y+ ∝ first-cell-centre height and ignores
> that **KK's open-water `n` is not stated** (§0), so the velocity scales may differ. It is offered
> as a reason to check, **not as a number to register**.

**If it holds, the relative-sizing scheme was wrong twice:** poisoned by 95.5× *and*, once un-poisoned,
still undershooting the registered y+ window by roughly 4×. **PRISM-A2's switch to absolute sizes
therefore needs a first-layer height chosen against KK's 0.5 mm, not merely the relative expression
repaired.** **Proposed:** register an absolute first-layer height and state the y+ it targets;
**the value is the supervisor's to set**, and this lane proposes the published **0.5 mm** as the anchor.

---

## 3. DOMAIN AND ROTATING-ZONE ROWS — any finite-volume source permitted

| # | parameter | PAPER | SRC | OURS | verdict / proposed |
|---|---|---|---|---|---|
| 20 | **downstream extent** | **SK 10 D** · **KK 12.0 D** (3000 mm) · **CH 8 D** (hub at 2 D of a 10 D box). **SK's own survey: *"values larger than 7D are usually adequate"*** | SK p. 6; KK p. 2; CH p. 4 | **6 D** (`make_blockmesh.py:57`) | **DISAGREE — and this one CHANGES, it is not excused.** Ours is below **every** published value and below the stated 7 D envelope. **Proposed: ≥ 10 D**, matching the nearest published setup rather than merely clearing the envelope |
| 21 | **domain radius** | **SK 2.5 D** · **KK 2.52 D** (1261 mm dia.) · **CH ±1.2 D** box half-width with **symmetry** sides | SK p. 6; KK p. 2; CH p. 4 | **4 D** (`make_blockmesh.py:58`) | **DISAGREE — ours is 1.6× wider than two independent published values.** **REGISTERED REASON (proposed):** *"Ours is larger, not smaller, than published practice; blockage is bounded more tightly than any published setup, so the deviation is conservative for the graded quantity. Retained to avoid a second topology change in the same re-registration."* Alternatively narrow to 2.5 D and buy back the cells — supervisor's call |
| 22 | **upstream extent** | **SK 3.5 D** · **KK 5.04 D** · **CH 2 D** | SK p. 6; KK p. 2; CH p. 4 | **3 D** (`make_blockmesh.py:56`) | **inside the published spread (2–5 D).** **No change proposed**; reason: *"within published practice."* |
| 23 | **MRF / rotating zone diameter** | **KK 1.47 D** (R_prop + 59 mm) · **SK: none** (SRF, whole domain rotates) · **CH: none** (sliding interface) | KK p. 2; SK p. 8; CH p. 4 | **1.3 D**, sensitivity at **1.6 D** (prereg §5) | **AGREE in effect — KK's 1.47 D falls BETWEEN our baseline and our sensitivity point.** Our registered pair brackets published practice; **proposed: say so on the certificate** |
| 24 | **MRF zone axial extent** | **KK: 0.28 D upstream, 9.77 D downstream** — the zone *is* the slipstream | KK p. 2 | **±0.5 D** (prereg §5) | **DISAGREE, 0.5 D vs 9.77 D downstream.** **REGISTERED REASON (proposed):** *"A 9.77 D MRF zone places the entire wake in the rotating frame, which changes what the wake means for the LDV comparison (§B.8). Our ±0.5 D keeps the graded wake in the stationary frame. Deviation is deliberate and is disclosed on the certificate."* |
| 25 | **passage vs full propeller** | **SK: 72° passage** · **KK, GG, CH: full 360°** | SK p. 7; KK p. 2; GG p. 2; CH p. 4 | **72° cyclic passage** | **REGISTERED REASON (proposed):** *"Geometry differs: passage vs 360°."* Our registered full-360 cross-check (§B.7 item 4, ≤0.5 % in KT) is the instrument that bounds it |
| 26 | outer boundary | **SK free-slip** · **CH symmetry on four sides** | SK p. 7; CH p. 4 | **slip** | **AGREE** |
| 27 | outlet | **SK static pressure** · **KK pressure outlet, zero-gradient for the rest** · **CH Neumann** | SK p. 7; KK p. 2; CH p. 4 | fixed pressure | **AGREE** |
| 28 | walls | **SK & KK: no-slip on blade, hub, shaft** | SK p. 7; KK p. 2 | no-slip, rotating | **AGREE** |
| 29 | root gap | **SK: removed** · **KK: root gap AND hub/shaft intersection gap filled** · **GG: sealed blade/hub** | SK p. 4; KK p. 1; GG p. 2 | 0.3 mm root gap closed | **AGREE — but KK also closes the HUB/SHAFT gap. Proposed: confirm ours does, and record it** |

---

## 4. PHYSICS, SCHEMES AND CONVERGENCE ROWS

| # | parameter | PAPER | SRC | OURS | verdict / proposed |
|---|---|---|---|---|---|
| 30 | **turbulence model** | **KK: high-Re k-ω SST** · **SK: Realizable k-ε AND SST k-ω, concluding *"for low and high ratios … Realizable k-ε … more accurate"*** · **CH: dynamic LES** | KK p. 2; SK abstract + p. 15; CH p. 2 | **k-ω SST only** | **DISAGREE in coverage.** SST is corroborated by the OpenFOAM source (KK); but the only source that ran both found k-ε better at the sweep ends. **Proposed: add a second closure**, per the supervisor's note that SA is directed — **noting SA is neither of the two the paper compared**, so it tests robustness, not SK's finding |
| 31 | **wall treatment** | **KK: wall functions, *"To model the boundary layer, wall functions were needed"*, y+ > 30** · **SK: wall-resolved, y+ ≈ 1, no wall functions** | KK p. 2; SK pp. 4, 8 | **wall functions**, `nutkWallFunction`, y+ 30–60 | **AGREE with the OpenFOAM source (KK); DISAGREE with SK.** **REGISTERED REASON (proposed):** *"Wall-modelled by registration; Sanaa's §B.5 names wall-resolved y+≈1 as the next rung. The published OpenFOAM practice on this propeller is wall-functioned."* |
| 32 | rotating-frame method | **KK: MRF, solver `MRFSimpleFoam`, OpenFOAM 1.6** · **SK: SRF** · **CH: sliding interface** | KK p. 2; SK p. 8; CH p. 4 | `simpleFoam` + `MRFProperties` | **AGREE with KK** — `MRFSimpleFoam` is the 1.6-era name for exactly our scheme |
| 33 | steady vs transient | **KK & SK: steady RANS** · **CH: transient LES** | KK p. 2; SK p. 8; CH p. 2 | steady | **AGREE** with both RANS sources |
| 34 | pressure–velocity coupling | **SK: segregated SIMPLE** (both solvers) | SK p. 8 | SIMPLE, consistent formulation | **AGREE** |
| 35 | **momentum convection** | **KK: second-order upwind** · **SK: *"Second-order … predominantly"*** · **QQ: high-order upwind dominant across participants** | KK p. 2; SK p. 8; QQ p. 9 | `linearUpwind` for U | **AGREE with all three** |
| 36 | **turbulence convection** | **KK: FIRST-ORDER** — *"first order accurate schemes were used for the turbulent quantities"* · **QQ: 1st-order upwind and high-order upwind both common** | **KK p. 2**; QQ p. 10 | **`limitedLinear 1`** — second-order | **DISAGREE with the OpenFOAM source.** **REGISTERED REASON (proposed):** *"Second-order turbulence convection is retained as the stricter choice; KK's first-order is disclosed as the published alternative. If the SIMPLE loop stalls, first-order turbulence convection is the registered fallback and its use is recorded."* |
| 37 | **residual target** | **KK: 1e-5 on pressure, velocity AND turbulence** · **SK: 1e-6 on all variables** | KK p. 3; SK p. 8 | **1e-5 on p and U** | **The two sources DISAGREE WITH EACH OTHER.** Ours matches the **OpenFOAM** source on the threshold but covers **fewer variables**. **Proposed: 1e-6 on p, U and turbulence** — adopting the stricter of the two and KK's wider variable set; costs iterations, buys the §B.6 clause that solver tolerance be strictly tighter than the stationarity gate |
| 38 | **stationarity criterion** | **SK: variance < 0.01 % of the mean over the last 1000 iterations** (`or` residuals 1e-6) | SK p. 8 | **0.1 % over the last 500 iterations** (`and` residuals) | **DISAGREE — ours 10× looser on tolerance, 2× shorter window.** **Proposed: 0.01 % over 1000 iterations.** Note ours is an `and`, SK's an `or` — **ours is the stricter logic and should stay `and`** |
| 39 | **inlet turbulence intensity** | **SK: 2 %**, *"estimated based on the calculated Reynolds values for external flow"* · **KK: computed from equations 1–4, value not printed** | SK p. 7; KK p. 2 | **1 %**, mixing length 0.1 D | **DISAGREE. Proposed: 2 %**, with SK's stated basis recorded |
| 40 | iteration cap | **NOT PUBLISHED** in any source | — | 4000 per point | **NOT PUBLISHED.** Note Sanaa's 2026-09-12 NO CAP ruling governs, not this row |
| 41 | **relaxation factors** | **NOT PUBLISHED in any source** — no source prints under-relaxation values | — | **U 0.7, p 0.3, turbulence 0.7** | **NOT PUBLISHED** — ours stands unsourced |
| 42 | non-orthogonal correctors | **NOT PUBLISHED** | — | 1 | **NOT PUBLISHED** |
| 43 | **force integration surfaces** | **KK: BLADES ONLY** — *"The forces and moments were computed on the blades only"* | **KK p. 2** | **blades + hub + shaft** (Sanaa §B.3) | **DISAGREE — and it changes which SVA table is the comparator.** **REGISTERED REASON (proposed):** *"Sanaa's §B.3 fixes the comparator as the 'including hub' table (Report 3752 p. 2.11) and therefore the integration surfaces as blades+hub+shaft. KK's blades-only figures are compared against the blades-only table (p. 2.13), differing by ≈0.01 in KT at J=1.2, and are disclosed as such."* |
| 44 | **KT, KQ, J, η definitions** | **SK Eqs. 3–6 p. 8** · **KK Eqs. 6–8 p. 3** · **CH Eqs. 19–20 p. 4** — all identical | all three | identical | **AGREE — four independent corroborations** |
| 45 | **J range** | **SK: 0 → 1.4422**, 10 points incl. bollard pull · **KK: 0.6 → 1.2**, 4 points · **CH: single J = 1.019** | SK p. 10; KK p. 4; CH p. 4 | **0.7985 → 1.4594**, 6 measured points | **partial overlap only.** No change proposed; ours is fixed to measured points so no interpolation is needed for the gate |

---

## 5. PUBLISHED RESULTS — CONTEXT ONLY, NEVER A BAND (see §0)

**KK**, fine mesh, OpenFOAM MRF k-ω SST wall-functioned, blades-only forces:

| J | KT | 10KQ | η |
|---|---|---|---|
| 0.6 | 0.623 | 1.415 | 0.421 |
| 0.8 | 0.505 | 1.189 | 0.541 |
| 1.0 | 0.397 | 0.984 | 0.643 |
| 1.2 | 0.289 | 0.778 | 0.710 |

Against SVA measured **including hub at n = 15** (Sanaa §B.3): J 0.7985 → KT +0.04 %, 10KQ +0.5 %;
J 1.2021 → KT +3.3 %, 10KQ +1.4 %. **But KK integrates blades-only**, and the blades-only SVA table
differs by ≈0.01 in KT at J = 1.2 — read that way, KK is **≈ +7 %** at J = 1.2, not +3.3 %.
**KK's open-water `n` is not stated.** So: a direction and magnitude cross-check, **not a band**, and
it is consistent with the systematic direction Sanaa already registered in §B.4 (KQ slightly high).

**CH**, at J = 1.019, **n = 25 s⁻¹**, cavitating, LES: experiment 0.374 / 0.9698; Mesh 3 (40.4 M,
y+ 19) **0.378 / 0.9648** — **+1.1 % KT, −0.5 % 10KQ**. Encouraging for snappyHexMesh on this
geometry; **no band for us** (§0). Note CH's 10KQ triple **1.0398 → 0.9710 → 0.9648** against a
non-monotone KT would need rule-5 checking before any GCI were quoted. **None is quoted, by them or
by us.**

**SK** at n = 10: KT within ~7 %, KQ within ~4 % (SST); Realizable k-ε ~5 % on thrust. Context only.

---

## 6. SUMMARY — WHAT THE SUPERVISOR RULES ON

**Rows proposed to CHANGE to the published value (6):** 20 downstream extent → ≥10 D · 37 residual →
1e-6 on p, U and turbulence · 38 stationarity → 0.01 % over 1000 · 39 inlet TI → 2 % · 30 second
closure added · 9/10 absolute first-layer height anchored on KK's 0.5 mm.

**Rows proposed to KEEP with a registered reason (7):** 1/25 passage topology · 21 domain radius ·
24 MRF axial extent · 31 wall treatment · 36 turbulence convection order · 43 force integration
surfaces · 45 J range.

**Rows AGREEING already (12):** 1, 8, 23, 26, 27, 28, 29, 32, 33, 34, 35, 44.

**Rows where the honest cell is NOT PUBLISHED (14):** 2, 3, 4, 5, 7ᵃ, 10, 11, 12, 13, 14, 15, 19,
40, 41, 42. *(ᵃ7 is published only in a non-snappy OpenFOAM source.)*
**These are the reproducibility gap, and it is a gap in the literature, not in our extraction.**
**No published `snappyHexMeshDict` for PPTC VP1304 exists in any of the six sources on disk.**
That belongs on the certificate as a stated limitation.

---

## 7. COST

No solver launched; this file is a synthesis of three existing ingests plus targeted reads of files
already in the repository. **Measured: 3.1 core-minutes**, single rank. **Derived, not measured:**
≈ **\$0.0027** at the owner-stated \$0.0513/core-h — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Lane cumulative: **22.7 core-minutes**, ≈ **\$0.0194** derived.
No pre-registered estimate exists for a synthesis task, so no calibration ratio is claimable.
