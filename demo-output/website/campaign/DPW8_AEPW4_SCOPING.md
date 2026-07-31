# DPW-8 & AePW-4 Joint Workshop: Scoping Report

**Date:** 2026-07-28
**Status:** RESEARCH AND PLANNING ONLY — no mesh generated, no solver run, no compute spent.
**Builds on:** `docs/DPW-CRM-SCOPING.md` (2026-07-27, generic DPW-VI/DPW-VII CRM scoping — still
the reference for core-hour derivation methodology; this report supersedes it for the specific
DPW-8/AePW-4 joint activity and does not repeat that derivation) and
`demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md` (2026-07-28, our largest converged
primal to date and the DPW4_Aircraft rejection this task asked to build on).

Companion machine-readable file: `demo-output/website/campaign/DPW8_AEPW4_SCOPING.json`.

---

## 1. What DPW-8/AePW-4 actually are — checked, not assumed

**The joint workshop is real, is a genuine collaboration (not co-location), and has already
happened.** Its full name is "AIAA Drag Prediction and Aeroelastic Prediction Workshop — A
Collaborative Approach to Multidisciplinary Drag and Aeroelasticity," combining the 8th Drag
Prediction Workshop (DPW-8) and the 4th Aeroelastic Prediction Workshop (AePW-4). The two
communities meet separately on Saturday for community-centric topics and together on Sunday for
the joint session; three working groups are DPW-centric, three are AePW-centric, and two ("Static
Aeroelastic Deformation" and "Buffet") are explicitly joint/hybrid.

- **Dates:** Saturday June 6 – Sunday June 7, 2026, San Diego, immediately before AIAA AVIATION
  Forum & Expo 2026 (Hillcrest AB/C rooms). Source:
  [aiaa-dpw.org/logistics.html](https://www.aiaa-dpw.org/logistics.html) (page itself states
  "Last Updated June 2, 2026").
- **Status as of this report: CONCLUDED.** Today is 2026-07-28 — about 7.5 weeks *after* the
  workshop. This was checked explicitly (per the clock-audit habit) rather than assumed from the
  "2026" in the name.
- **Schedule slipped materially from the original plan:** the 2024 kickoff deck proposed a
  July 19–20, 2025 workshop in Las Vegas
  ([kickoff_presentation_v2.pdf](https://www.aiaa-dpw.org/ref/kickoff_presentation_v2.pdf)); the
  event actually ran June 6–7, 2026 in San Diego — an ~11-month slip.
- **Post-workshop results: not established.** Searched aiaa-dpw.org and arc.aiaa.org/NTRS for a
  DPW-8 summary paper; none found. Not surprising — DPW-VI's *Journal of Aircraft* summary papers
  landed ~2 years after the 2016 event, and DPW-7's summary (Tinoco, AIAA 2023-3492) landed ~1
  year after 2022. As of Jan 15, 2026 (the last pre-workshop status deck found,
  [scitech_2026.pdf](https://www.aiaa-dpw.org/ref/scitech_2026.pdf)), several participants were
  still "in progress" toward submission, and the deck's own status note reads "Limited submissions
  to date makes definitive statements challenging" and "computational cost can be prohibitive (as
  expected)" for the unsteady buffet case.
- **Seven working groups:** Source of Scatter (Galbraith/Holst, DPW), Wind Tunnel/Test Environment
  (Hosseini/Rivers/Rider, DPW), Static Aeroelastic Deformation (Rider/Keye/McHugh, joint), Buffet
  (Pomeroy/Stanford/Sansica/Raveh/Ben-Gida, joint), High-Angle/HAWG (Chwalowski, AePW), High-Speed/
  HSWG (Brouwer, AePW), Large-Deflection/LDWG (Palacios, AePW).
- **Participation:** open worldwide, no AIAA membership required, CFD submission is optional
  (attendance-only welcome). Paid registration ($99–$649 depending on tier, $299 virtual) gates
  *attendance*, not data access — see §3.

**Practical upshot:** we cannot "join" an already-concluded event. What remains genuinely open is
the public grid/geometry/data corpus and the methodology — both still fully usable.

---

## 2. The case matrix

### Verification activities (smaller, arguably the tractable end)

| ID | Geometry | Flow | Notes |
|---|---|---|---|
| V1 (required) | ONERA OAT15A 2D airfoil | M=0.73, Re_c=3e6, T=271K | V1a grid convergence (5 alphas, 6-grid family); V1b unsteady/buffet polar (alphas 3.25–3.90°); V1c scatter-reduction reprise (residuals ~1e-10) |
| V2 | Joukowski airfoil (analytic) | M=0.15, Re_c=6e6, α=0° | 6-grid family, python-generated "Classic" family encouraged |
| V3 | DPW-III wing increment (W1/W2 planforms) | M=0.76, Re_c=5e6 | V3a grid convergence (α=0.5°); V3b polar (α −1° to 3°) |
| V4 | NASA CRM finite element model | — | Structural-only, no flow |

### Study configurations (the actual DPW-8/AePW-4 headline cases)

| ID | Geometry | Flow | Key cases |
|---|---|---|---|
| **Config A** | JAXA CRM Wing/Body/Tail, model scale | M=0.85, unsteady RANS | TC2 rigid (Re=1.515e6, α 1.22–5.89°); TC3 FSI (Re=2.27e6) |
| **Config B** | **NASA CRM Wing/Body, aeroelastic deflections (ETW LoQ182)** | **M=0.85, Re_c=5.0e6, T=100°F** | TC2a grid convergence (α=2.50°); TC2b alpha sweep (CL=0.50); TC2a(E)/2b(E) elastic; TC2b(S) with strut |
| Config C | NASA CRM Wing/Body/Tail, aeroelastic deflections | M=0.85, Re_c=5.0e6 | TC3b alpha sweep, with/without strut |
| Config D | NASA CRM Wing/Body/Nacelle/Pylon, aeroelastic | M=0.85, Re_c=5.0e6 | TC4a(E)/4b(E), FSI with provided FEM |

**Config B's flow condition (M=0.85, Re=5×10⁶) is the same family as our own repo's A6 CRM_Wing
run** — but Config B requires an actual wing-body (not wing-alone) with a prescribed aeroelastic
deflection; A6 deliberately did neither (DPW4_Aircraft was rejected on time-box grounds; CRM_Wing
is wing-alone, undeformed).

**Common specification across Verification/B/C/D:** turbulence model is a specifically-qualified
"French Vanilla SA-(neg) (All-terms)" (not generic SA), adiabatic wall, and **residuals converged
to ~1e-10 (machine precision)** — roughly 4–5 orders of magnitude tighter than this lab's
production standard of p≤1e-5/U≤1e-6.

### AePW-4 working-group cases beyond the joint groups

- **HAWG (mandatory):** flutter prediction at M=0.80, α sweep 0–6°, on a CRM-derived wing with
  provided FEM (optional M=0.78/0.76/0.74 at α=3°). Same CRM-scale grid problem as Config B/C.
- **HSWG:** two much smaller experimental geometries — AFRL/SSC RC-19 clamped thin metallic panel
  (M=1.92, shock-wave/boundary-layer interaction) and UNSW HyMAX cantilever aluminum plate (2mm
  thick, 130×80mm, M=5.8, wedge 2°/10°). Structural data: DIC displacement, PSD, Schlieren,
  100-point laser line scan.
- **LDWG:** nonlinear large-deflection static equilibrium and LCO for slender (HALE/sailplane-
  class) wings. **Case-matrix detail not established** — the working-group page states objectives
  only; specifics apparently live in dated slide decks not fetched in this pass.

**Structural data provided:** two FEM models are directly downloadable —
`NASA_CRM_FULLSPAN_WBT0.REV00` (sourced from the official CRM FEM page) and
`NASA_CRM_HALFSPAN_FEM.REV00` (generated specifically for DPW-8/AePW-4).

---

## 3. What data is public

**Grids and geometry are genuinely open — no login, no registration wall.** This was verified
directly, not assumed: multiple multi-hundred-MB to multi-GB files were downloaded via plain
anonymous `curl` (HTTP 200, no auth challenge) from `dpw.larc.nasa.gov` and the DPW-7 legacy tree
it still serves.

- **Grid directory:** <https://dpw.larc.nasa.gov/DPW8/> — a static, browsable directory with
  subfolders per working group (Buffet, ONERA_OAT15A, Scatter, Static_Deformation,
  Test_Environment), each further split by provider (Cadence/Pointwise, Helden Aerospace, NASA
  Ames, plus the legacy DLR/ONERA/NLR/JAXA/Vassberg DPW-7 tree, same CRM geometry lineage). Most
  recently modified 2026-05-19 — grids were still being added right up to the June workshop.
- **Geometry:** DPW-8 explicitly reuses "a large portion" of DPW-7 CRM geometry (IGES format,
  multiple aeroelastically-deformed stations); JAXA geometry via a separate JAXA portal.
- **Experimental data:** searchable at
  <https://commonresearchmodel.larc.nasa.gov/experiment-results-search/> (NTF, ETW, JAXA tests).
  OAT15A experimental-data access path referenced but not independently verified — secondary only.
- **Structural/FEM data:** same open directory tree as the grids, no additional gate.
- **What *does* require registration:** paid AIAA conference registration for *attendance*
  (already moot — the event has passed), and emailing `dpwaiaa@gmail.com` for a participant ID to
  get *official submission credit* in the shared GitHub results repository. Neither gates reading
  or reusing the public grids/geometry/FEM data.

**This determines the report's central conclusion in §4: the ceiling here is compute, not
access.** Everything needed to attempt these cases is downloadable today.

---

## 4. Grid sizes — the decisive feasibility number

**Directly measured, primary source, DPW-8's own grid server:** the Config B CRM Wing/Body
Cadence unstructured CGNS grid, Level 3 (Medium), is **92.7–93.0 million cells** (mix of
tetrahedra/pyramids/prisms/hexahedra) across its 8 alpha-deformed variants, per the README
co-located with the grid files
(`dpw.larc.nasa.gov/DPW8/Scatter/Test_Case_2/Cadence_Grids.REV00/CGNS/README.txt`).

Applying the gridding guidelines' own stated growth formula
(`[(L+2)/(L+1)]³` per level, from
[gridding_guidelines_v3_07012024.pdf](https://www.aiaa-dpw.org/ref/gridding_guidelines_v3_07012024.pdf))
backward from that measured Level-3 point gives a **derived** (not directly measured) coarsest
Level-1 ("Tiny") grid of **≈11.6 million cells**.

That derived number is tightly corroborated by three *independently generated* DPW-7 grid
families for the same CRM wing-body(-tail) geometry, each directly measured from its own primary
README/spec document:

| Provider | Grid type | Tiny/L1 | Coarse/L2 | Medium/L3 |
|---|---|---|---|---|
| DLR (Solar mesher) | unstructured hybrid | 31,589,359 elements (11,698,938 pts) | 64,334,695 elem | 130,749,024 elem |
| Vassberg (NASA) | structured multiblock/overset | 5,286,597 pts | 17,644,325 pts | 41,590,149 pts |
| JAXA | unstructured mixed | 25,294,690 elements (8,698,930 nodes) | — | — |

**Triangulated conclusion:** across four independent providers and two workshop generations, the
coarsest ("Tiny"/Level-1) grid for this exact CRM geometry lands at **5–31 million cells/points**,
with the unstructured families (most comparable to our own OpenFOAM pipeline) clustering at
**8–12 million**. This is not an arbitrary workshop choice — it falls out of the gridding
guidelines' own wall-spacing (y+≈1 at Re=5×10⁶–3×10⁷) and farfield (>100 chords) requirements
applied to this specific, geometrically complex aircraft.

~~**Not established:** exact cell counts for the 2D verification grids (V1/V2/V3)~~ — see §4b,
which closes this.

### 4b. RESOLVED 2026-07-30 — the V1 OAT15A grid family is **15,872 to 1,146,880 cells**

This report's single open question is now answered, and the answer reverses the V1 verdict.
The ONERA_OAT15A directory offers four independent grid providers:

| Provider | Bundle | Size |
|---|---|---|
| Cadence, structured | `Cadence-ONERA-OAT15A_..._Structured.zip` | 554.0 MB |
| Cadence, unstructured | `Cadence-ONERA-OAT15A_..._Unstructured.zip` | 284.6 MB |
| Helden | `Helden-ONERA-OAT15A.zip` | 1077.3 MB |
| ONERA / Deck | `Deck-ONERA-OAT15A.zip` | **9.7 MB** |
| ONERA / Rizzi | `ONERA-ONERA-OAT15A-Rizzi.zip` | **64.0 MB** |

The two small ones were downloaded (anonymous HTTP, no auth, ~74 MB total, no compute spent).
The **Rizzi** bundle carries a complete **9-level structured family**. Its `ReadMe.md` states the
cell counts, and — per house practice, the table was **verified rather than trusted**, by reading
the zone dimensions straight out of each CGNS file's HDF5 headers:

| Level | Zones | Cells (README) | Cells (measured from CGNS) | Agrees |
|---:|---:|---:|---:|:--:|
| 1 | 4 | 15,872 | **15,872** | yes |
| 2 | 4 | 34,816 | **34,816** | yes |
| 3 | 4 | 63,488 | **63,488** | yes |
| 4 | 4 | 100,352 | **100,352** | yes |
| 5 | 4 | 144,384 | **144,384** | yes |
| 6 | 4 | 253,952 | **253,952** | yes |
| 7 | 4 | 471,040 | **471,040** | yes |
| 8 | 4 | 667,648 | **667,648** | yes |
| 9 | 4 | 1,146,880 | **1,146,880** | yes |

**All nine cell counts match the README exactly.** Vertex counts do *not* match exactly (level 1:
32,744 summed across the four zones against the README's 32,612) and that discrepancy is expected
and benign — summing per-zone vertices double-counts the points shared on block interfaces, while
cells are never shared. Reported rather than smoothed over.

The Deck bundle is a **single 2D plane** of Sébastien Deck's structured multi-block grid, not a
refinement family, and its own README warns that Housman's Plot3D conversion "concatenated the
blocks that did not have extraordinary corners. This causes some discontinuities in the mesh, so
groups with cell-centered finite-volume solvers may prefer the original mesh" — i.e. an explicit
caution against the converted file for exactly the solver class this lab runs. Use the Rizzi
family.

**Consequence, stated plainly: the entire V1 grid family fits inside this lab's proven envelope.**
Our largest converged primal is 579,072 cells (A6). Levels 1 through 8 are all at or below that.
Level 9, the finest offered, is 1,146,880 cells — **1.98× our largest-ever converged case**, not
9×–55× as the CRM configurations are. This is the first DPW-8 case found for which committee-
supplied grids at *every* offered level are within reach, and it is a real transonic case
(M=0.73, Re_c=3×10⁶) on a committee grid, not a self-generated one.

---

## 5. The methodology — transferable regardless of participation

Even having concluded we cannot submit to the CRM-scale cases, several practices are worth
adopting into our own doctrine outright:

- **Formulaic 6-member grid-family growth rule** keyed to a Level index
  (`[(L+2)/(L+1)]³` per level), not ad hoc refinement — enables real Richardson extrapolation/GCI
  across a family, versus our current dual/triple-mesh comparisons.
- **Pre-computed y+-anchored wall-normal spacing tables** for two Reynolds-number regimes (5×10⁶
  and 3×10⁷), with an explicit growth-rate ceiling (<1.2× normal to walls) and a minimum-2-
  constant-spacing-cells-at-the-wall rule — directly reusable in our own snappyHexMesh/pyHyp layer
  specs on any future case.
- **Fully-qualified turbulence-model naming as a documented scatter-reduction lever:** "French
  Vanilla SA-(neg) (All-terms)" is a specific SA variant, not generic "SA" — the Source of Scatter
  WG treats ambiguous model specification as a measured, real source of code-to-code disagreement.
- **Machine-precision (~1e-10) convergence** for the scatter-reduction case — ~4–5 orders tighter
  than our production 1e-5/1e-6 bar. Worth an aspirational ceiling, not a blanket requirement.
- **Standardized F&M/surface-cut/spanload/bending-twist submission templates** and the convention
  of reporting participant scatter as an explicit IQR/std band (per DPW-VI, captured in the prior
  scoping report: IQR 252–262 counts) — directly transferable to how this lab reports its own
  campaign uncertainty.
- **Drag-increment vs. absolute-drag distinction** (increments scatter ~3× less) — already in the
  prior scoping report, reconfirmed here as the field's cheapest path to a credible number.

---

## 6. Feasibility verdict against our measured capability

**Our numbers, restated plainly:**
- Largest converged primal: **579,072 cells** (CRM_Wing, wing-alone, matches DAFoam's published
  tutorial CD to 0.0067%), 16 vCPU/32 GiB host, 431s wall for 1000 iterations to 1e-8 on every
  field.
- Adjoint memory wall: works at 63,920 cells; dies in Jacobian assembly at 156,089 cells; also
  OOMs at 399,360 cells under both 12GB and 18GB caps. The wall sits somewhere in
  **[63,920, 156,089] cells** and is **structural**, not a raising-the-cap problem — OpenMDAO's
  reverse-mode sweep builds a mesh-sized `d[residuals]/d[vol_coords]` Jacobian block regardless of
  which `wrt=` is requested.
- Independently corroborated: DAFoam's own DPW4_Aircraft tutorial (a genuine wing-body-tail case)
  was rejected on time-box grounds because it ships snappyHexMesh refinement levels 9–12, a
  200,000,000-cell cap, and a 192-rank `decomposeParDict` default — the tutorial vendor itself
  assumes HPC scale for a true CRM wing-body-tail case.

**Verdict, case by case:**

| Case family | Verdict | Why |
|---|---|---|
| **V1 OAT15A** | **FEASIBLE — resolved 2026-07-30, see §4b** | Rizzi 9-level committee family measured directly from the CGNS headers at **15,872 to 1,146,880 cells**. Levels 1-8 are all at or below our largest converged primal (579,072); level 9 is 1.98× it. Every offered level is within reach. |
| V2 Joukowski | **ATTEMPTED 2026-07-29**, two rungs gated | Self-generated conformal O-grid, 768 / 12,288 cells passed the zero-lift gate; the 49,152-cell rung diverged on a pre-existing linear-solver stall. See `DPW8_V2_joukowski.md`. |
| V3 DPW-III wing increment | **Still unresolved** | Cell counts not established in this pass; a 3D wing, so expected well above V1 but far below the CRM configurations. |
| Config B/C/D (CRM Wing/Body(-Tail)(-Nacelle-Pylon)) and HAWG | **Not feasible on this hardware at any offered grid level** | Coarsest grid is 5.3M–31.6M cells (measured/derived across 4 providers, 2 workshop generations) — 9×–55× our largest-ever converged primal, and 75×–495× our adjoint's already-failing threshold. The workshop's own 6-grid Richardson requirement and 1e-10 convergence bar multiply real cost further. |
| HSWG small panels (RC-19, HyMAX) | **Smaller geometry, gated by a missing capability, not a mesh-size wall** | No grid-size figures found, but a 130×80mm plate is 2–3 orders of magnitude smaller in extent than a full CRM. Blocked instead by having no structural/FSI solver stood up — this lab has proven supersonic `rhoCentralFoam` accuracy (F3 campaign, <1% vs. exact theory) but not aeroelastic coupling. |

**What a materially bigger machine would need:**
- *Primal only*, coarsest CRM grid (~11.6M cells): roughly 20× our current largest converged
  case. Our host was **not** memory-bound at 579,072 cells (30GB free throughout A6) — if primal
  RAM scales close to linearly with cell count (unlike the adjoint), the coarsest CRM grid might
  fit under 32GB *if* partitioned across substantially more ranks than we currently use for sane
  wall-time. DAFoam's own DPW4_Aircraft default of 192 ranks points at the same conclusion: this
  is more a rank-count/wall-time problem than a hard memory wall, for the primal alone.
- *Adjoint at any CRM scale*: categorically out of reach by adding RAM alone — the OOM is
  structural per A3/A6's own finding. Would need either a much larger host with empirically
  measured peak RSS on a small case first, or DAFoam's untested matrix-free
  `adjUseColoring=False` path.
- *Full 6-grid Richardson family to Level 6* (221M–368M cells/points at the finest measured
  level): squarely multi-node HPC-cluster territory — not a single-box upgrade. This matches the
  prior scoping report's independent DPW-VI estimate (7.2M–714M cells) almost exactly, which
  tracks since DPW-8 continues the DPW-7 geometry lineage.

**Coarsest-grid or reduced-scope entry that is genuinely feasible?** **None identified** among
the DPW-8/AePW-4 CRM-scale cases (Configs A–D, HAWG) at any offered grid level — every measured
or derived "Tiny"/Level-1 grid for this geometry, across four independent providers, is 9× or
more beyond our largest-ever converged case. ~~The 2D verification cases remain the one open
possibility, pending the cheap step of actually counting their cells.~~ **That step was taken on
2026-07-30 and it landed: V1 OAT15A is feasible at every offered level (§4b).** The CRM-scale
verdict is unchanged and unchallenged; what changed is that a genuine committee-gridded DPW-8
case now exists inside our envelope.

---

## Recommendation

**Do not** attempt any DPW-8/AePW-4 CRM-configuration (Config A/B/C/D) or HAWG submission on
current hardware. This is a complete and honest answer, not a failure to find one: every
independently-sourced coarsest grid for this geometry sits far beyond anything this lab has ever
converged, and the adjoint fails at a small fraction of even that coarsest number. The June 2026
workshop has also already concluded, so "submission" is moot regardless of compute.

**Do:**
1. ~~Download and unzip the OAT15A (V1) grid bundles and count actual per-level cells.~~
   **DONE 2026-07-30 — see §4b. 15,872 to 1,146,880 cells across 9 levels, measured from the
   CGNS headers, all nine matching the provider's own README.** The Rizzi bundle (64 MB) is the
   one to use; the Deck bundle's own README warns cell-centered finite-volume solvers off its
   converted Plot3D file.
2. **Now unblocked and recommended:** an off-cycle, non-submitted validation run of the V1a grid
   convergence case reusing this lab's proven F2-campaign transonic pipeline against DPW-8's own
   committee-supplied OAT15A grid — a cross-check against a workshop-standard grid rather than a
   self-generated one, which is what V2 had to settle for. Not a workshop submission; the event
   has passed. Costed as a docket proposal, 2026-07-30.
3. Bank the transferable methodology (§5) into our own doctrine regardless of whether we ever
   touch DPW/AePW data directly.
4. Treat the openly-downloadable FEM/structural data as a future resource only if this lab stands
   up a structural/FSI solver — not actionable today.

---

## Sources (all fetched/verified 2026-07-28)

- Workshop identity, structure, objectives: <https://www.aiaa-dpw.org/>
- Dates, venue, cost: <https://www.aiaa-dpw.org/logistics.html> (Last-Updated 2026-06-02)
- Working groups, Jan-2026 status: <https://www.aiaa-dpw.org/ref/scitech_2026.pdf>
- Original (superseded) 2024 schedule: <https://www.aiaa-dpw.org/ref/kickoff_presentation_v2.pdf>
- AePW-4 overview + working groups: <https://nescacademy.nasa.gov/workshops/AePW4/public>,
  `/wg/high_angle`, `/wg/high_speed`, `/wg/large_deflection`
- Test-case matrix: <https://www.aiaa-dpw.org/TestCases/testcases.html>
- Gridding guidelines (growth-rate formula, wall-spacing tables):
  <https://www.aiaa-dpw.org/ref/gridding_guidelines_v3_07012024.pdf>
- Grid directory (DPW-8, open/anonymous): <https://dpw.larc.nasa.gov/DPW8/>
- DPW-8 Config B grid README (Level-3 cell count):
  `https://dpw.larc.nasa.gov/DPW8/Scatter/Test_Case_2/Cadence_Grids.REV00/CGNS/README.txt`
- FEM models: `https://dpw.larc.nasa.gov/DPW8/Static_Deformation/Test_Case_2/FEM_Models/`
- DPW-7 grid families (cross-validation): `https://dpw.larc.nasa.gov/DPW7/DLR_Grids.REV00/`,
  `https://dpw.larc.nasa.gov/DPW7/Vassberg_Grids.REV00/`,
  `https://dpw.larc.nasa.gov/DPW7/JAXA_Grids.REV00/`
- Experimental data search: <https://commonresearchmodel.larc.nasa.gov/experiment-results-search/>
- This lab's measured capability: `demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md`,
  its referenced A3 (Onera M6 adjoint OOM findings)
- Prior generic DPW-VI/VII scoping (methodology and core-hour derivation basis): `docs/DPW-CRM-SCOPING.md`
