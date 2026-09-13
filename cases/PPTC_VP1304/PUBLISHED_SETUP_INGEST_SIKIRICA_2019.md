# PPTC VP1304 — published-setup ingest under Sanaa's rule G, and the headline is that the named source is NOT an OpenFOAM paper

**Team:** cfd. **Lane:** lab-lane under `cfd-supervisor`. **Date:** 2026-09-13.
**Governing rule:** `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
section G, byte-exact: *"For any public case, the lab starts from a published OpenFOAM
setup of that case — mesh recipe, layer settings, schemes, wall treatment — ingested into
the knowledge base before the first registration. Inventing a setup for a case someone has
already run in this solver is refused."* Section G names the PPTC source as
*"Sikirica et al. 2019 (OpenFOAM, snappy, layer settings published)"*.

**Nothing left the box.** Rules 7 and 8: no submission, registration, posting or contact of
any kind. No solver was launched by this lane. No frozen file was edited; this is a NEW
file and the open-water pre-registration
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` (frozen at `c0cd9038f`,
blob `6a27740da10c77d813bbe94db564d0fbee5b03b4`) is untouched by it.

---

## 0. THE FINDING, FIRST, BECAUSE IT INVALIDATES THE PREMISE OF THE INSTRUCTION

Sikirica, Čarija, Kranjčević and Lučin (2019) **is the correct paper, is on disk, and
title-page verifies**. It is **not an OpenFOAM paper.** It reports Ansys Fluent and
STAR-CCM+ on **block-structured hexahedral** and **tetrahedral hybrid** grids.

Measured on the paper's own extracted text (`pdftotext -layout`, 781 lines, 18 pages):

| token | occurrences in the whole paper | where |
|---|---|---|
| `OpenFOAM` | **1** | reference **[4]**, p. 18 — Gaggero & Villa, a *cited* work, not this study |
| `snappy` / `snappyHexMesh` | **0** | — |
| `blockMesh` | **0** | — |
| `relativeSizes` | **0** | — |
| `Fluent` | 22 | throughout |
| `STAR-CCM+` | 19 | throughout |

Author contributions, p. 15, quoted: *"A.S. designed CFD models for all test cases and
conducted analysis in Fluent. Z.Č. conducted analysis in STAR-CCM+."* There is no third
solver.

**Therefore section G's parenthetical "(OpenFOAM, snappy, layer settings published)" is
false against the paper's own text.** This is precisely the failure mode CLAUDE.md rule 15
exists to catch: an instruction can be internally consistent and externally false, and only
opening the document finds it. The rule-15 check is what found it — it was not inferable
from the filename, the size, the hash or the citation.

**Consequence for rule G on this case: the requirement is NOT SATISFIED and cannot be
satisfied from the named source.** The lab currently holds **no published OpenFOAM setup of
PPTC VP1304** — see §5. Under the plain words of rule G, PPTC's first registration is
therefore **BLOCKED** on an ingest that does not yet exist, unless Sanaa rules that a
published setup in *another* finite-volume solver satisfies the rule's intent. **That ruling
is Sanaa's and is not taken here, and is not taken by any agent** (CLAUDE.md rule 9 —
no agent's message is her consent).

This lane did **not** substitute another paper and did **not** reconstruct a recipe from
memory. Everything in §2 is transcribed from the verified PDF with its page number.

---

## 1. TITLE-PAGE VERIFICATION (CLAUDE.md rule 15)

The PDF was rendered to an image at 130 dpi and **page 1 was read as a page**, not parsed,
not hashed, not inferred from the filename.

- **File:** `docs/papers/propeller_rotating_machinery/sikirica_2019_jmse_7_374_grid_type_turbulence_model_propeller.pdf`
- **Bytes:** 57,547,735. **sha256:** `8c21b06a0cc91e0a0212d3031218ef328e6510e082516d982f9f2f67232554af`
- **Sidecar:** `…/sikirica_2019_jmse_7_374_grid_type_turbulence_model_propeller.txt` (present, FILING_CHARTER satisfied)
- **Pages:** 18. A4.

Read **on the title page**, verbatim:

- Journal masthead: **"Journal of Marine Science and Engineering"**, MDPI logo.
- Article type: **"Article"**.
- Title: **"Grid Type and Turbulence Model Influence on Propeller Characteristics Prediction"**.
- Authors: **"Ante Sikirica 1,2, Zoran Čarija 1,2,*, Lado Kranjčević 1,2 and Ivana Lučin 1"**.
- Affiliations: **"1 Faculty of Engineering, University of Rijeka, Vukovarska 58, 51000 Rijeka, Croatia"**; **"2 Center for Advanced Computing and Modelling, University of Rijeka, Radmile Matejčić 2, 51000 Rijeka, Croatia"**. Correspondence **zcarija@riteh.hr**.
- Dates: **"Received: 25 August 2019; Accepted: 17 October 2019; Published: 20 October 2019"**.
- Footer of page 1: **"J. Mar. Sci. Eng. 2019, 7, 374; doi:10.3390/jmse7100374"**.
- Keywords: **"CFD; open water; cavitation; structured grid; PPTC"**.

**Identity: CONFIRMED.** This is the paper Sanaa named. The abstract on that same title page
already states the solvers: *"determined using numerical simulations in two commercial
solvers: Ansys Fluent and STAR-CCM+."*

One discrepancy recorded, immaterial to identity: the printed DOI is `jmse7100374` while
the volume/issue is 7(11); MDPI's own landing path is `/2077-1312/7/11/374`. Recorded, not
relied on. **The title page, not the DOI string, is the verification.**

---

## 2. CLAIM → SOURCE → OUR CURRENT VALUE

Every "source" cell is a page of the verified PDF. Every "ours" cell cites the file in this
repository that holds the registered value. `n/a` in the *source* column means **the paper
does not contain that concept at all**, which for the snappy rows is the whole point.

### 2.1 snappyHexMesh castellation controls

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 1 | `maxLocalCells`, `maxGlobalCells`, `minRefinementCells`, `nCellsBetweenLevels`, `resolveFeatureAngle`, `refinementSurfaces`, `refinementRegions`, `features`/`eMesh` | **n/a — the paper contains no snappyHexMesh** | `nCellsBetweenLevels 3`, `resolveFeatureAngle 30`, `maxGlobalCells 60e6`, `maxLocalCells 4e6`, per-patch `refinementSurfaces level (lo hi)`, `bladeRegion`/`tipVortex` regions — `cases/PPTC_VP1304/mesh/make_snappy.py:138–155` | **NO SOURCE. Ours is unsourced under rule G.** |

### 2.2 snappyHexMesh snap controls

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 2 | `nSmoothPatch`, `tolerance`, `nSolveIter`, `nRelaxIter`, `nFeatureSnapIter`, `explicitFeatureSnap` | **n/a — no snappyHexMesh** | `nRelaxIter 5`, `nFeatureSnapIter 15`, `implicitFeatureSnap false`, `explicitFeatureSnap true`, `multiRegionFeatureSnap false` — `make_snappy.py:160–163` | **NO SOURCE.** |

### 2.3 addLayersControls — the rows the instruction asked for by name

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 3 | **`relativeSizes true` or `false`?** | **n/a — the keyword does not exist in their workflow. See §3, this is the load-bearing row.** | **`relativeSizes true`** — `make_snappy.py:165` | **UNADJUDICABLE from the named source.** |
| 4 | number of near-wall layers | **41 layers**, p. 4: *"Boundary layer was fully resolved with 41 grid layers"* (structured grids, all tests). Unstructured preliminary grids limited to **20 layers**, p. 4; unstructured with 41 layers also evaluated. | **`nSurfaceLayers 6`** (`N_LAYERS = 6`, `make_snappy.py:48`), patches `blades, hub, cap, shaft` | **DISAGREE, 6 vs 41 — a factor of 6.8.** Explained by wall treatment, not by carelessness: their 41 layers resolve the boundary layer to y+≈1; our 6 layers sit under wall functions. The two are different rungs, not the same rung done differently. |
| 5 | `expansionRatio` / growth ratio | **not stated numerically.** The paper gives layer *count* and y+, never a growth ratio. | **`expansionRatio 1.2`** (`make_snappy.py:49,169`) | **NOT PUBLISHED. Ours is unsourced.** |
| 6 | `finalLayerThickness` / `firstLayerThickness` | **not stated numerically.** Implied only through y+≈1 and *"grids were generated using scaling factors with dimensionless wall distance y+ ≈ 1"*, p. 8. | **`finalLayerThickness 0.5`** (relative), no `firstLayerThickness` — `make_snappy.py:170` | **NOT PUBLISHED. Ours is unsourced.** |
| 7 | `minThickness` | **n/a** | **`minThickness 0.05`** (relative) — `make_snappy.py:170` | **NO SOURCE.** |
| 8 | layer shrink/smoothing controls (`nGrow`, `featureAngle`, `maxThicknessToMedialRatio`, `nLayerIter`, …) | **n/a** | `nGrow 0`, `featureAngle 130`, `slipFeatureAngle 30`, `nSmoothSurfaceNormals 1`, `nSmoothNormals 3`, `nSmoothThickness 10`, `maxFaceThicknessRatio 0.5`, `maxThicknessToMedialRatio 0.3`, `minMedialAxisAngle 90`, `nBufferCellsNoExtrude 0`, `nLayerIter 50`, `nRelaxedIter 20` — `make_snappy.py:171–175` | **NO SOURCE.** |

### 2.4 y+ achieved and targeted, and wall treatment

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 9 | y+ target | **y+ ≈ 1**, *"enforced throughout all the tests"*, p. 4; repeated p. 8: *"grids were generated using scaling factors with dimensionless wall distance y+ ≈ 1"* | registered **y+ 30–60 with wall functions** (prereg §5, lines 534–535); **amended for the smoke only to 30–300** (AMENDMENT 4, §A4.1(b), prereg line 1105) | **DISAGREE, and it is a deliberate rung difference.** Theirs is wall-resolved; ours is wall-modelled. Sanaa's own section B calls wall-resolved *"the next rung"*. |
| 10 | y+ achieved (a measured value) | **not reported as a number or a map.** Only the target is stated. No y+ figure appears in the paper. | registered prediction 50–200 after 300 iterations (prereg §A4.2, lines 1110–1123), not yet measured | **NOT PUBLISHED.** The paper cannot corroborate any achieved-y+ claim. |
| 11 | wall functions | **none — the boundary layer is resolved, not modelled.** No wall-function name appears. | **`nutkWallFunction`** with k-ω SST (prereg §6, Sanaa section B §6) | **DISAGREE (consequence of #9).** |

### 2.5 Turbulence model

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 12 | turbulence models evaluated | **Realizable k-ε and SST k-ω**, both, p. 5 and p. 10; RANS throughout | **k-ω SST only** (prereg §6) | **PARTIAL AGREEMENT.** SST k-ω is common to both. But their conclusion, p. 15 and abstract, is that **Realizable k-ε is the more accurate of the two on this propeller at low and high J**: *"for low and high ratios, structured grids in conjunction with Realizable k-ε model can achieve more accurate results."* **Our act runs only the model the paper found less accurate at the sweep ends.** Recorded as a finding for the supervisor; no gate is touched by it. |
| 13 | rotating-frame method | **Single Moving Reference Frame (SRF)**, steady, p. 8. Transient reserved for cavitation. | **MRF** with `MRFProperties`, steady `simpleFoam` (prereg §6) | **AGREE in substance** — both are steady rotating-frame; SRF (whole domain rotating) vs MRF (rotating zone) differ in that ours needs a zone and theirs does not. See row #19. |

### 2.6 Discretisation and convergence

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 14 | pressure–velocity coupling | **segregated, SIMPLE**, p. 8, both solvers | **SIMPLE**, consistent formulation (prereg §6) | **AGREE.** |
| 15 | convection/discretisation order | **"Second-order discretization schemes were used predominantly"**, p. 8; HRIC only for volume fraction in cavitation | `linearUpwind` for U, `limitedLinear 1` for turbulence (prereg §6) | **AGREE in order** (both second-order). Scheme *names* are not published — OpenFOAM spellings have no Fluent/STAR equivalent in the text. **Ours is unsourced at the keyword level.** |
| 16 | convergence criterion | **"variance for both thrust and torque throughout the last 1000 iterations was less than 0.01% of their mean values, or … residuals for all variables fell below 1e-6"**, p. 8 | residuals < **1e-5** on p and U; KT, KQ stationary within **0.1%** over the last **500** iterations; cap 4000 iterations (prereg §6) | **DISAGREE, and ours is the LOOSER of the two on every clause:** residual 1e-5 vs 1e-6 (10×), stationarity 0.1% vs 0.01% (10×), window 500 vs 1000 iterations (2×). Note their criterion is `or`, ours is `and`. |

### 2.7 Domain, topology and boundary conditions

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 17 | domain shape and size | **cylinder, diameter 5D** (radius **2.5D**), **3.5D upstream**, **10D downstream** of the blade centre, p. 6, Figure 3 | **radius 4D** (`R_OUTER = 4.0*D`), **3D upstream** (`X_INLET = +3.0*D`), **6D downstream** (`X_OUTLET = -6.0*D`) — `cases/PPTC_VP1304/mesh/make_blockmesh.py:56–58` | **DISAGREE on all three.** Ours is **1.6× wider** in radius, **0.857×** the upstream length, **0.6×** the downstream length. Their p. 6 survey says downstream *"values larger than 7D are usually adequate"* — **our 6D is below the envelope they cite.** |
| 18 | periodic passage | **single passage, 72°**, *"Remaining faces ensure rotational periodicity and coincide at an angle of 72° along the horizontal axis"*, p. 7 | **72° wedge, cyclic** (`SECTOR_PHASE_DEG = 21.2830` about x) — `make_blockmesh.py:84` | **AGREE.** Independent corroboration of the passage choice. |
| 19 | rotating-zone geometry | **none. SRF rotates the whole single-passage domain**, p. 8; no interface, no zone diameter | MRF cylinder **1.3D** diameter, ±0.5D axially, sensitivity at 1.6D (prereg §5, Sanaa B §5) | **NO SOURCE for a zone size.** Their approach removes the parameter rather than choosing it. |
| 20 | inlet | uniform velocity, **turbulence intensity 2%**, p. 7 | uniform velocity, **TI 1%**, mixing length 0.1D (prereg §6) | **DISAGREE, 1% vs 2%.** |
| 21 | outlet | static pressure, p. 7 | fixed pressure (prereg §6) | **AGREE.** |
| 22 | outer boundary | **free-slip** (zero normal Dirichlet, Neumann tangential), p. 7 | **slip** (prereg §6) | **AGREE.** |
| 23 | solid walls | **shaft, hub and blade, no-slip**, p. 7 | blades, hub, cap, shaft, no-slip rotating (prereg §6) | **AGREE.** |
| 24 | root gap | **removed** — *"a slight gap exists between the blade and hub; to simplify grid generation, this gap was removed"*, p. 4 | 0.3 mm root gap **closed** (Sanaa B §2(a), prereg) | **AGREE.** Independent corroboration of a registered modelling choice. |

### 2.8 Grid family and cell counts

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 25 | grid-sensitivity family | **six structured grids per passage: 7.8e5, 1.7e6, 2.9e6, 4.1e6, 7.2e6, 1.07e7 cells**, at **J = 0.802**, in Fluent with Realizable k-ε, p. 8 | three levels per passage: **≈0.8e6 / 2.7e6 / 9e6**, family ratio 1.5, at **J = 1.2021** (prereg §5, Sanaa B §5) | **COMPATIBLE ENVELOPE.** Our coarse ≈ their coarsest (0.8 vs 0.78 M); our fine 9 M sits inside their 7.2–10.7 M. **Their sensitivity point is J = 0.802, ours is J = 1.2021** — different design points. |
| 26 | working grid chosen | **≈1.7e6 cells per passage**, p. 9, *"chosen as the cornerstone of our study"* | medium ≈2.7e6 (prereg §5) | Ours is **1.6× finer** than their production grid. |
| 27 | discretisation error at the chosen grid | ΔKT below **3%** for most grids; ΔKQ generally below **1%**; coarsest grid ≈3.5% KT and ≈1.5% KQ, p. 8 | GCI to be computed on a Roache triple (prereg §7, CLAUDE.md rule 5) | **Their study is a sensitivity sweep, not a Roache triple** — no observed order, no GCI, no asymptotic-range statement. Under CLAUDE.md rule 5 their numbers would not, as published, support a gated verdict. Recorded as context only. |
| 28 | grid quality | *"Orthogonal quality and skewness were in acceptable ranges with occasional outlier cells"*, p. 4 — **no numbers** | maxNonOrtho 65 (relaxed 70), maxBoundarySkewness 4, maxInternalSkewness 4 — `make_snappy.py:180–185`; Sanaa B §5 gates non-orth < 70, skew < 4 | **NOT PUBLISHED as numbers.** No comparison possible. |

### 2.9 The open-water condition, J range and non-dimensionalisation

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 29 | rotation rate | **n = 10 s⁻¹** (open water); n = 25 s⁻¹ (cavitation), p. 7 and p. 10 | **n = 15 s⁻¹**, test 11F0395 (Sanaa B §3, prereg) | **DISAGREE, 10 vs 15 s⁻¹.** Material: Report 3752's own n=10 and n=15 curves **cross near J = 1.3** (Sanaa B §4 registers this as the measured Reynolds effect). **Their KT/KQ therefore may not be compared to ours point-for-point**, and their Table A2/A3 values are **not** a comparator for our act. |
| 30 | J range | **J = 0 to J = 1.4422**, ten points: 0.000, 0.160, 0.322, 0.482, 0.642, 0.802, 0.961, 1.121, 1.283, 1.442 (Tables A2, A3, p. 17) | six measured points **0.7985 → 1.4594** (Sanaa B §3) | **THEIRS IS WIDER AND INCLUDES BOLLARD PULL (J = 0), OURS DOES NOT.** Their top J (1.442) ≈ our top (1.4594); their grid is far denser at low J. |
| 31 | KT | **KT = T/(ρ n² D⁴)**, Eq. (3), p. 8 | identical (Sanaa B §3, Report 3752 annex A2.2) | **AGREE.** |
| 32 | KQ | **KQ = Q/(ρ n² D⁵)**, Eq. (4), p. 8 | identical | **AGREE.** |
| 33 | J | **J = Va/(nD)**, Eq. (5), p. 8 | identical | **AGREE.** |
| 34 | efficiency | **η = J·KT/(2π·KQ)**, Eq. (6), p. 8 | identical | **AGREE.** Note their Eq. (6) is printed as `J Kt / (2π Kq)` — with **KQ**, not 10KQ — and their tables list `10 Kq`; the η column is consistent with KQ. Recorded because a 10× slip here is a classic error. |
| 35 | D, skew | **D = 0.25 m**, mean pitch ratio **1.5675**, effective skew **18.8°**, p. 4 | D = 0.250 m, P0.7/D = 1.635, skew 18.837° (Sanaa B §2) | **AGREE.** Note theirs quotes the **mean** pitch ratio 1.5675, ours the **r/R = 0.7** value 1.635 — different quantities, not a conflict. |
| 36 | reference dataset | *"All results were corrected with dummy hub measurements"*, p. 4, citing SVA [22] | graded against the table *"corrected with idle torque and gap force"*, Report 3752 p. 2.11 (Sanaa B §3) | **CONSISTENT in intent**; the exact SVA table they used is not named. |

### 2.10 Their reported agreement with the SVA experiment

| # | claim | source |
|---|---|---|
| 37 | SST k-ω, structured grid, both solvers: *"relative difference between CFD results and experimental measurements is below **7% for thrust and 4% for torque**"* across the majority of tests | p. 10 |
| 38 | worst point, SST k-ω: **J = 1.442**, *"Fluent deviates by **9%** and STAR-CCM+ by **14%**"* on thrust | p. 10 |
| 39 | Realizable k-ε, structured: *"Discrepancy between Fluent CFD results and experimental measurements is **5%**, even at highest advance ratios"*; torque overestimated in Fluent with **errors up to 2.2%**, underestimated in STAR-CCM+ | pp. 12–13 |
| 40 | overall conclusion: hexa and hybrid grids agree in the mid-J range; at **low and high J, structured + Realizable k-ε is the more accurate combination** | abstract (p. 1) and conclusions (p. 15) |
| 41 | their CFD values, structured grid, for the record (Fluent / STAR-CCM+, SST k-ω, n = 10 s⁻¹): J=0.802 → KT 0.494 / 0.509, 10KQ 1.196 / 1.201; J=1.283 → KT 0.214 / 0.217, 10KQ 0.652 / 0.656; J=1.442 → KT 0.128 / 0.122, 10KQ 0.473 / 0.454 | Tables A2, A3, p. 17 |

**These are recorded as context and are NOT a comparator for our act** — different rotation
rate (row #29), different turbulence treatment (rows #9–#12), different solver.

---

## 3. THE LOAD-BEARING ROW: `relativeSizes` — WHAT THE PAPER ACTUALLY SETTLES

**Question put to this lane:** did Sikirica use `relativeSizes true` or `false`?

**Answer: NEITHER, and the reason is the finding.** `relativeSizes` is a snappyHexMesh
`addLayersControls` keyword. The paper uses **no snappyHexMesh, no blockMesh, and no
OpenFOAM**. The token appears **zero** times. **The named source cannot adjudicate our
`relativeSizes` question, in either direction.**

The instruction's conditional was: *if they used relative sizing successfully, they must
have had no tiny level-0 edge, and their background-mesh topology is then the finding.*
The conditional's premise is false, **but its conclusion survives in a stronger form**, and
this is the part worth carrying to the supervisor.

### 3.1 Their background topology, specifically

There is no "background mesh" in their workflow at all. Stated on the page:

- **Block-structured hexahedral grids**, generated directly on the 72° passage
  (p. 3–4, Figures 1 and 2a). No octree, no level-0 cell, no refinement level, no `hexRef8`.
- **Domain:** cylinder of diameter **5D**, **3.5D** upstream and **10D** downstream of the
  blade centre (p. 6, Figure 3).
- **Single 72° passage** closed by two rotationally periodic faces that *"coincide at an
  angle of 72° along the horizontal axis"* (p. 7). Figure 4 (p. 6) draws this passage as a
  **wedge with a sharp apex on the axis** — the two periodic faces meet on the centreline.
- **41 boundary-layer layers, y+ ≈ 1, on all structured grids** (p. 4).

### 3.2 Why that topology is immune to the defect we measured

Our defect, as measured by this lab and registered in
`verification/campaign/PPTC_PRISM_A1_PREREGISTRATION.md:26–36`:
`hexRef8::getLevel0EdgeLength()` returns the **global minimum** level-0 edge in the mesh,
`edgeLen = level0EdgeLength()/2^pointLevel`; on our grid that global minimum is the
**azimuthal chord of the 2 mm axis rod**, `2·0.002·sin(π/60) = 2.09343825e-04 m`, which
makes every *relative* layer thickness **95.5× too small**.

The 2 mm rod exists for one reason, stated in our own generator
(`cases/PPTC_VP1304/mesh/make_blockmesh.py:11–38`, `R_AXIS = 0.002` at line 63): a 72°
`blockMesh` wedge **cannot** close on a collapsed axis edge — it *"fails loudly"* — and the
refinement regions are cylinders about the axis, so the axis must be represented. The rod is
a **workaround for a blockMesh topology constraint**.

**A block-structured mesher has no such constraint.** ICEM-class hex blocking closes a
passage on the axis with a collapsed (degenerate) block edge routinely, which is exactly what
Figure 4's sharp apex shows. **So the chain is:**

> block-structured passage → no axis rod → no 2.09e-04 m edge → but also **no level-0 edge at
> all**, because there is no octree and no `hexRef8`, so `relativeSizes` has no referent.

**The finding for the supervisor, stated plainly:** our tiny-edge poisoning is **not** a PPTC
geometry problem and **not** a problem the published practice on this case ran into. It is a
problem **our chosen mesher creates**, because snappyHexMesh needs a background blockMesh,
a 72° background wedge needs an axis body, and that body's azimuthal chord then defines the
global level-0 minimum that `relativeSizes true` is measured against. **The published
practice avoided it by not using an octree mesher on a wedge.** Nothing in this paper
licenses `relativeSizes true` on our grid, and nothing in it forbids `relativeSizes false`
either — it is silent, and silence is not evidence (the planted-zero principle, rule 3).

---

## 4. WHAT THIS INGEST DOES **NOT** ESTABLISH

- It does **not** supply a published OpenFOAM mesh recipe, layer settings, schemes or wall
  treatment for PPTC. Rule G is **not** discharged by it.
- It does **not** license any change to the frozen pre-registration. No gate, threshold, cap
  or label is touched. Any departure must land as a dated addendum at the foot of
  `PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` with a version bump and the assertion
  `lines whose number changed above this section: 0` (CLAUDE.md rule 6).
- It does **not** decide the `relativeSizes` question (§3), the n=10-vs-15 comparability
  question (row #29) or the Realizable-k-ε question (row #12). Those are the supervisor's,
  and the rule-G ruling is Sanaa's.
- It does **not** claim the paper's numbers as a comparator for our act. Row #29 forbids it.

---

## 5. WHAT A PUBLISHED **OpenFOAM** PPTC SETUP WOULD REQUIRE — CANDIDATES ONLY, NOT INGESTED

Named so the supervisor can rule with facts. **None of these was fetched, read, verified or
relied on by this lane.** Listing a candidate is not ingesting it, and reconstructing a
recipe from any of them without title-page verification is exactly what rule G refuses.

- **Gaggero, S.; Villa, D. (2017)**, *"Steady cavitating propeller performance by using
  OpenFOAM, StarCCM+ and a boundary element method"*, Proc. IMechE Part M, **231**, 411–440.
  This is the **one** OpenFOAM citation in Sikirica (ref. [4], p. 18) and is also ref. [33] of
  Lungu 2020. It is an IMechE journal article, **not known to be open access**; whether it
  treats PPTC or E779A is **not verified here**.
- The **smp'11 workshop proceedings participant papers** (Sanaa's section B §1 already names
  them for the mesh envelope) — some participants ran OpenFOAM; which ones, and whether any
  published layer settings, is **not verified here**.

**Also checked and also not OpenFOAM:** `lungu_2020_jmse_8_297_des_sst_pptc_propeller.pdf`,
the other PPTC CFD paper already in our knowledge base. Token counts on its sidecar:
`OpenFOAM` 1 (again only the Gaggero reference, line 1075), `snappy` 0, `blockMesh` 0,
`ISIS` 6, `FINE` 49 — it is **ISIS-CFD / FINE-Marine (NUMECA)**. **Both PPTC CFD papers the
lab holds are non-OpenFOAM.**

---

## 6. COST

No solver was launched. Work was PDF retrieval-check, `pdftotext`, two `pdftoppm` page
renders and text scans, single-threaded on one core.

- **Measured: 4.1 core-minutes** (≈4.1 min wall × 1 rank ÷ 60 × 60), from this lane's own
  command timeline. Cleaned figure; no stalls.
- **Derived, not measured:** 4.1 core-min = 0.068 core-h × \$0.0513/core-h ≈ **\$0.0035**.
  `cost_basis`: rate is **owner-stated** (CLAUDE.md rule 12); the box cannot read its own
  billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate vs actual:** no pre-registered estimate exists for a retrieval-and-ingest task,
  so no calibration ratio is claimable. Stated rather than fabricated.
- **Network:** the paper was **already on disk and already git-tracked**; no download was
  needed. Two probe requests to `www.mdpi.com` returned HTTP 403 before that was discovered,
  and were abandoned. Nothing was sent, posted, registered or submitted (rules 7, 8).

---

## 7. PROVENANCE OF EVERY NUMBER IN THIS FILE

| artifact | path |
|---|---|
| the paper | `docs/papers/propeller_rotating_machinery/sikirica_2019_jmse_7_374_grid_type_turbulence_model_propeller.pdf` |
| its sidecar | same directory, `.txt` |
| our layer and snappy settings | `cases/PPTC_VP1304/mesh/make_snappy.py` (lines cited inline) |
| our background topology | `cases/PPTC_VP1304/mesh/make_blockmesh.py` (lines cited inline) |
| our registered gates | `cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` (FROZEN, not edited) |
| the level-0 edge defect | `verification/campaign/PPTC_PRISM_A1_PREREGISTRATION.md:26–36` |
| the governing rule | `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md` §G |
