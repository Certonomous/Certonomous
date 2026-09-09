# M6 OWN-MESH FAMILY — build registration (ONERA M6 surface pressures vs AGARD AR-138, third-direction own-mesh family)

> ## 🟡 THIS FILE IS A **DRAFT** AND **UNFROZEN**.
> No gate, threshold, cap or label in it is in force. It registers a MESH-GENERATION
> build and its admissibility screen (already run, results in §3), and lays out the
> intended eventual-solve gates for the supervisor to FREEZE (rule 2) when the solve is
> sequenced. **Freezing this document — committing the gate, threshold, cap and label
> before any solve — is the supervisor's personal check and is not delegated.** No
> message from this lane, or from any agent, is Sanaa's consent (rule 9).
>
> Drafted by a cfd `lab-lane` on the cfd-supervisor's mesh-generation brief, 2026-09-07.
> Mesh generation is capacity-light and was run alongside the T4d/R2-M2 box drain per the
> brief. **NO SOLVER HAS RUN.** The flow solve is STOPPED at this document and sequenced
> behind the box drain, where it takes the supervisor's check-4.

---

## 0. WHY THIS FAMILY EXISTS — SANAA'S M6 THIRD-DIRECTION RULING

Sanaa's M6 route ruling (`etc/sessions/2026-09-04T1500Z`): the third-direction family —
**the lab's OWN volume mesh** — builds in parallel as the STANDING M6 capability for the
true observed order. First physics = M6 surface `Cp` at the AGARD span stations vs tunnel
data, **with the family band**; inside the **$1,000 IBL ladder envelope**.

Two prior directions on this box do NOT reach a credential-grade family band:

- **Direction 1 — DPW / committee grids.** RULED to FAIL both hard mesh gates (max
  non-orthogonality 70°, max skewness 4.0) across all three levels (LAB_STATE board 70).
  Cannot carry a credential validated-force GCI.
- **Direction 2 — structured PLOT3D (`M6I`).** `GATE FAIL`: max non-orthogonality
  **86.46–87.75°** on all three levels, max skewness **8.30 / 5.11** on L2 / L1
  (`verification/runs/M6I_runs/R0_RESULTS.md`).

- **Direction 3 — THIS FAMILY: a pyHyp hyperbolic own-mesh.** On this box that route has
  already produced a gate-CLEARING M6 volume mesh: `RUNG1_M6_R2_runs/L2`, 71,760 cells,
  checkMesh max non-orthogonality **61.46°**, max skewness **2.06** — both inside the
  hard gates. This registration reproduces that proven recipe as the standing own-family
  BASE level in a clean own run root, with a fresh generation and a measured screen
  (§3), and lays out the finer/coarser levels of the eventual Roache triple (§6).

---

## 1. GEOMETRY PROVENANCE

**Surface (input to the volume mesh).**
`/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/surfaceMesh.cgns` —
sha256 `1e11aae4e0e5a4caaffeb63f98a2626734075fb486de8dca93e32f554d143921`, 126,976 bytes.
A held M6 surface (1,560 quad faces, 1,595 unique nodes; pyHyp's own read), the same
surface that produced the proven gate-clearing `RUNG1_M6_R2_runs/L2` mesh. The lab's own
volume mesh is CONSTRUCTED from it by hyperbolic extrusion (§2), so the volume grid is
the lab's own construction.

**Held STL of the same wing (for cross-check / an alternative snappyHexMesh route not
taken).** `sdk/geometry/onera_m6_wing.stl` — binary STL, 12,480 facets, bounding box
x∈[~0, 1.1440], y∈[−0.03943, 0.03943], z∈[0, 1.2164] m; consistent with a
roughly-true-scale ONERA M6 wing (root chord ~0.8 m order, ~9.8 % ONERA-D section,
semispan ~1.2 m). Header string "Certonomous patch-extracted STL" — its provenance is a
patch extraction, so it is recorded as a cross-check surface, not the meshed input.

### 1.1 AR-138 PRIMARY REFERENCE — TITLE-PAGE VERIFICATION (rule 15 / L-144)

The primary experimental reference is **AGARD Advisory Report No. 138**,
`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`.

**Title page SEEN BY THIS LANE, as the page-1 image (not inferred from filename or
hash).** Page 1 reads, verbatim from the rendered image: **"AGARD-AR-138"** (header);
**"NORTH ATLANTIC TREATY ORGANIZATION / ADVISORY GROUP FOR AEROSPACE RESEARCH AND
DEVELOPMENT (ORGANISATION DU TRAITE DE L'ATLANTIQUE NORD)"**; **"AGARD Advisory Report
No.138 / EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT / REPORT OF THE FLUID
DYNAMICS PANEL / WORKING GROUP 04"**. This is the AR-138 title page, verified by sight.

**The ONERA M6 case is in AR-138 as test case B1**, confirmed in the document body:
"PRESSURE DISTRIBUTIONS ON THE ONERA-M6-WING AT TRANSONIC MACH … by V. Schmitt and
F. Charpin" (sidecar line 343–345), and the case index "B 1  ONERA Wing M 6 … peaky
profil ONERA D" (line 645). Flow conditions for the graded case (test 2308):
**M∞ = 0.8395, α = 3.06°, Re = 11.72 × 10⁶ on the MAC** — transcribed from
`M6SR_PREREGISTRATION.md:527`, itself citing AR-138.

⚠ **Honest limit of this verification:** I have seen the title page and confirmed the M6
B1 case and Schmitt–Charpin authorship inside the report. I have NOT independently
re-derived the 271-tap `case_2308.dat` reference-value pipeline or the section→`y/b`
mapping; those are governed by the frozen `RUNG1_M6_R2` / `M6SR` registrations (the
`A-MAP` discriminator) and are inherited, not re-opened, here.

---

## 2. MESH RECIPE — pyHyp HYPERBOLIC EXTRUSION (the proven gate-clearing route)

Volume mesh generated in the DAFoam image `dafoam-idwarp-rot:v1`
(digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`),
pyHyp reading `surfaceMesh.cgns` and marching a hyperbolic volume outward, then
`plot3dToFoam -noBlank` → OpenFOAM polyMesh → geometric `createPatch`
(wing / symmetry / farfield) → `checkMesh`. Driver:
`verification/runs/M6_OWN_FAMILY_runs/build_m6_own_base.py` (a clean standalone
single-level driver; recipe, docker invocation and checkMesh reader lifted
verbatim-in-shape from the proven `cases/RUNG1_M6/build_r2_triple.py`).

**pyHyp options, BASE level (medium, "L2"):**
`N = 47` marched layers, `s0 = 2.0e-04` (first off-wall spacing, requested), `marchDist =
50.0`, `cMax = 0.1`, `epsE = 1.0`, `epsI = 2.0`, `theta = 3.0`, `volCoef = 0.25`,
`volBlend = 0.0005`, `volSmoothIter = 100`, `kspreltol = 1e-4`,
`outerFaceBC = farfield`, `unattachedEdgesAreSymmetry = True`, `families = wall`.

**Why this route (route selection, on cost + admissibility + gate-clearance):**
- pyHyp hyperbolic is the ONLY M6 route on this box shown to CLEAR both hard gates
  (RUNG1_M6_R2 L2: 61.46° / 2.06). The structured PLOT3D route (M6I) and the DPW grids
  both FAIL non-orthogonality by 16–18°.
- Extrusion off a body-fitted surface gives near-wall-aligned cells: low skewness and
  low non-orthogonality where it matters, buying wall resolution with aspect ratio (AR
  304.7, admissible per `MESH_STANDARD.md` §3.3 — anisotropy aligned with the flow, not
  a non-orthogonality or skew pathology).
- It is cheap (§7: base level measured **0.8204 core-min**, 1 rank).
- A blockMesh C/O-grid (`cases/F13_onera_m6/make_blockmesh_m6.py`) and a snappyHexMesh
  route off the STL were available but NOT taken: neither has a gate-clearing precedent
  on this box, and pyHyp already does.

---

## 3. ADMISSIBILITY SCREEN — BASE LEVEL, MEASURED (already run)

Run root: `verification/runs/M6_OWN_FAMILY_runs/L2/`
(case at `.../L2/case/`, checkMesh log at `.../L2/case/log.checkMesh`, machine result at
`.../L2/RESULT.json`). Generated 2026-09-07.

**Planted control (rule 3), fired BEFORE trusting the clean read:** the checkMesh reader
was pointed at a preserved BROKEN log (`RUNG1_M6_R2_runs/L3/log.checkMesh`) and REQUIRED
to see its breach; it read max non-orthogonality **109.219°** (> 70) and **2**
negative-volume cells. The reader can see a non-zero, so a zero from it is evidence.

| metric | measured (base "L2") | hard gate (`MESH_STANDARD.md`) | verdict |
|---|---|---|---|
| cells | **71,760** | (expected 71,760, match) | — |
| **max non-orthogonality** | **61.4646°** | § 3.1: hard gate **70°** | **CLEARS** |
| **max skewness** | **2.05915** | § 3.2: hard gate **4.0** | **CLEARS** |
| max aspect ratio | **304.711** | § 3.3: > 1000 needs alignment note (this is below 1000) | OK |
| negative-volume cells | **0** | 0 | OK |
| avg non-orthogonality | 13.0519 | — | — |
| checkMesh verdict line | **"Mesh OK."** | — | — |

**`screen_clears_hard_gates = true`** (`.../L2/RESULT.json`). Patches produced:
`wing` (wall, 1,560 faces), `symmetry` (symmetry, 3,128), `farfield` (patch, 1,560) —
solve-ready. **Iterations required: NONE** — the first generation cleared both gates, and
the numbers reproduce the proven RUNG1_M6_R2 L2 metrics (61.4646° / 2.05915) exactly,
confirming a faithful build.

---

## 3.2 ADMISSIBILITY SCREEN — THE TWO ENDS (L1 FINE, L3 COARSE), MEASURED 2026-09-08

Both ends were generated from the **one proven L2 parent surface**
(`A3-onera-m6-adjoint-coarse/surfaceMesh.cgns`, sha `1e11aae4…`, 1,560 faces) by
`cgns_utils`, so all three levels are exactly nested and geometrically similar by
construction — the r=2 repair sec 6 called for, done from a single parent rather than three
independent surfaces. Driver:
`verification/runs/M6_OWN_FAMILY_runs/build_m6_own_ends.py` (recipe/readers lifted
verbatim-in-shape from `build_m6_own_base.py`); results at
`.../L1/RESULT.json`, `.../L3/RESULT.json`, `.../L1_L3_SUMMARY.json`.

**Planted control (rule 3) fired on every screen**, the SAME preserved broken log the base
used (`RUNG1_M6_R2_runs/L3/log.checkMesh`): the reader saw max non-orthogonality
**109.219°** (>70) and **2** negative-volume cells before any clean read was trusted.

| level | surface op | faces | pyHyp N | cells | max non-orth | max skew | neg-vol | AR | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **L1** fine | `cgns_utils refine` L2 | **6,240** (×4 L2) | 93 (92 layers), s0 1.0e-04 | **574,080** (=8×L2) | **60.8639°** | **1.44118** | **0** | 254.372 | **CLEARS both hard gates** |
| **L3** coarse (strict r=2) | `cgns_utils coarsen` L2 | **390** (÷4 L2) | 24 (23 layers), s0 4.0e-04 | 8,970 (=L2÷8) | **109.219° / 101.798° / 168.464°** (3 recipes) | 4.2336 / 7.561 / 8.547 | 2 / 0 / 8 | — | **FAILS every recipe** |
| **L3b** coarse (layer sweep) | same 390-face surface | **390** | 47 / 41 / 35 / 31 / 27 | 17,940 → 10,140 | **101.4° / 101.8° / 102.4° / 102.9° / 103.5°** | 14.5 / 25.5 / 4.56 / 2.68 / 1.90 | 4 / 4 / 3 / 3 / 3 | ~1e95 | **FAILS at every layer count** |

- **L1 CLEARS.** 60.8639° / 1.44118 / 0 neg-vol — cleaner than L2 (61.4646° / 2.05915), as
  expected: refinement lowers non-orthogonality. Cell count 574,080 = **exactly 8×** L2 and
  wall faces 6,240 = **exactly 4×** L2; `points` sha256 `57852b6f…` distinct from L2. Cost
  **3.525 core-min** (nominal recipe, first try).
- **No admissible coarse level exists off a 390-face M6 surface — DEFINITIVELY, across 8
  attempts.** First (driver `build_m6_own_ends.py`): the strict r=2 coarse level (390 faces,
  N=24, 23 layers) failed under three smoothing recipes at FIXED `marchDist = 50.0` — nonOrth
  109.219° / 101.798° / 168.464°, the nominal case *bit-for-bit the same degeneracy RUNG1's
  independent vcoarse L3 showed*. My first hypothesis was too few layers (a steep far-field
  growth ratio); that hypothesis is **DISPROVED**. Second (driver `build_m6_own_coarse.py`,
  cfd-supervisor's 2026-09-08 course correction): the layer count was swept UP on the same
  390-face surface at fixed `marchDist = 50.0` — N = 47, 41, 35, 31, 27 (46 → 26 layers, cell
  ratios to L2 of 4.00 → 7.08). **Max non-orthogonality barely moved — 101.4° to 103.5° —
  and 3–4 negative-volume cells with aspect ratios ~1e95 appeared at EVERY layer count.**
  Adding layers does not help because the fold is not a growth-ratio problem: **the 390-face
  surface under-resolves the wing itself** (wingtip / leading-edge curvature), so the
  hyperbolic normals cross and cells invert near the tip regardless of how the wall-normal
  layers are distributed. RUNG1 blamed its L3 degeneracy on the vcoarse *surface*; this shows
  the true cause is **any ÷4 (390-face) coarsening of the M6 surface** — a real geometric
  limit, not a tuning miss. Gates 70 / 4 / 0 were **not touched** (rule: only Sanaa widens a
  gate). Cost 3.0416 (ends) + 3.38 (coarse sweep) = **6.42 core-min** across all 8 coarse
  attempts. (Lesson candidate on the supervisor's release: *r=2 coarsening of the M6 surface
  below ~1,560 faces is inadmissible for hyperbolic extrusion at any layer count.*)

**Consequence for the triple.** The own-family has an admissible **fine pair {L2, L1}** —
r=2, cell ratio exactly 8.00, `points` sha distinct — but **no admissible coarse end below
L2**, so a `{L3, L2, L1}` Roache triple is **not achievable by coarsening**. A rule-5
`CONVERGING` triple therefore does **not yet exist**, and by the sec 4.1 honest-labelling law
a {L2, L1} band is a **two-level Richardson pair (assumed order p, not observed) — a
lower-confidence band, NOT a Roache triple and NOT to be presented as one.** The route to a
genuine three-level observed order is to **shift the triple to the FINE side** — {L2, L1,
L0}, with L0 = `cgns_utils refine` of L1 (24,960 faces, N=185, ~4.59M cells) — because finer
levels clear MORE easily (L2 61.46° → L1 60.86°, non-orthogonality falls monotonically with
refinement, so L0 is predicted admissible). That is a mesh-gen + solve-sequencing decision
for the supervisor's check-4, laid out but **not built here** (sec 6); L0 mesh-gen is not
capacity-light and its solve is costed in sec 7.3.

---

## 4. THE DELIVERABLE — M6 `Cp` AT THE AGARD SPAN STATIONS, WITH THE FAMILY BAND

**Span stations (AGARD AR-138 B1), transcribed, not invented:**
**y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99** — 271 pressure orifices in 7
sections (AR-138; `RUNG1_M6_R2_PREREGISTRATION.md:231`, `M6I_PREREGISTRATION.md:199`,
identical across every M6 registration on box). The section→`y/b` mapping (`A-MAP`) and
its `Cn`-monotonicity discriminator are inherited from the frozen `M6SR` / `RUNG1_M6_R2`
registrations and are NOT re-opened here.

### 4.1 HONEST-LABELLING LAW (Sanaa's ruling, carried on every figure)

The **family band from THIS own-mesh family is the deliverable** — because the eventual
triple (§6) varies the discretisation in ALL THREE directions (surface ×4 per level AND
wall-normal layers ×2 per level), it yields a TRUE observed order and a genuine family
band. By contrast a **single-mesh surface-refinement band** (the `M6SR` route, whose
wall-normal discretisation is identical across levels) is only a **LOWER BOUND on
discretisation uncertainty**, and its `p_s` is **NOT an observed order**. **Every figure
carrying a band from a single mesh must say so, verbatim.** Until the §6 triple is built
and graded, any `Cp`-vs-AGARD comparison on the base level ALONE (§3) is a single-mesh
comparison and carries only the lower-bound label.

---

## 5. INTENDED GATES FOR THE EVENTUAL SOLVE — BYTE-IDENTICAL TO THE EXISTING M6 GATE

**These are TRANSCRIBED byte-identical from the existing frozen M6 family-band gate
(`RUNG1_M6_R2_PREREGISTRATION.md`, "Gate P", §229–246). NOTHING is invented or widened
here.** Widening a gate threshold is reserved to Sanaa (rule 9); pinning the exact frozen
literal at freeze is the supervisor's check (rule 2).

- **Solver:** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST** (`kOmegaSST`),
  fully turbulent (`RUNG1_M6_R2:144`).
- **Momentum `divSchemes`:** `bounded Gauss linearUpwind grad(U)` (`RUNG1_M6_R2:164`) —
  second order with a gradient limiter (first order would not resolve the shock position
  Gate P grades on).
- **Flow:** M∞ = 0.8395, α = 3.06°, Re = 11.72 × 10⁶ (test 2308).
- **Gate P (Sanaa's deliverable):** M6 surface `Cp` against the 271 AR-138 tapped values,
  with the grid-family band on every station.
  - **reference accuracy `ΔCp = ±0.02` at `Mo = 0.84`** — AR-138 B1-4 §6.1, published
    (`RUNG1_M6_R2:237`).
  - **Gate P graded on `x/c ≤ 0.90`;** the rear 10 % is plotted and reported, never
    graded (`RUNG1_M6_R2:244`).
  - **Gate P sits BEHIND Gate G** (the Roache triple, §6). A `PASS` on a family that is
    not `CONVERGING` is **`NOT A RESULT`** (rule 5; `RUNG1_M6_R2:246`).
- **Gate G (Roache triple):** the three-level own-mesh family (§6) must be `CONVERGING`
  for a band to exist; a non-`CONVERGING` triple is `NOT A RESULT` whatever its value
  (rule 5). GCI at Fs = 1.25.

The exact gate literal at freeze is pinned by hashing the frozen source registration; the
supervisor sets and signs it at check-4. This DRAFT sets no number of its own.

---

## 6. THE ROACHE-TRIPLE STATUS — WHAT WAS BUILT (2026-09-08) AND WHAT REMAINS

The two ends were built (§3.2). Result: the **fine** end succeeds, the **coarse** end is
inadmissible off a 390-face surface at any layer count. The current state of the family:

| level | surface faces | pyHyp `N` (layers) | cells | state |
|---|---|---|---|---|
| **L3 / L3b** coarse | 390 (÷4 of L2) | 24, then 47/41/35/31/27 swept | 8,970 → 17,940 | **BUILT & FAILS.** 8 attempts, nonOrth 101–168°, 3–8 neg-vol at every layer count. NO admissible coarse level off a 390-face surface (§3.2). |
| **L2** medium — **BASE** | **1,560** | **47 (46)** | **71,760** | **BUILT & CLEARS** (§3). `points` sha `2b0ce260…`. |
| **L1** fine | **6,240 (×4 of L2)** | **93 (92)** | **574,080** | **BUILT & CLEARS** (§3.2). nonOrth 60.86°, skew 1.44, 0 neg-vol. `points` sha `57852b6f…`. |

**Admissible family so far: the r=2 fine PAIR {L2, L1}** — cells 71,760 → 574,080, ratio
**exactly 8.00** (r=2 in all three directions: surface ×4, layers ×2), `points` sha256
distinct. This is a **two-level Richardson pair, not a Roache triple** (§4.1 honest label:
assumed order p, a lower-confidence band).

**To reach a genuine three-level observed order — supervisor's choice, NOT decided here:**
1. **Preferred — shift the triple to the FINE side: {L2, L1, L0}.** Add L0 = `cgns_utils
   refine` of L1 → 24,960 faces, N=185, ~4.59M cells; cell ratios then 8.00 and 8.00 again.
   Non-orthogonality falls monotonically with refinement (L2 61.46° → L1 60.86°), so L0 is
   **predicted admissible** — the triple lands entirely on the clean fine side. Costs: L0
   mesh-gen is NOT capacity-light (a ~4.6M-cell N=185 march), and the L0 solve is ~936
   core-min (§7.3); both are inside the $1,000 IBL envelope but need the supervisor's
   sequencing behind the box drain. **Not built here.**
2. **Accept the {L2, L1} pair** as a lower-confidence assumed-order band, labelled as such
   on every figure (§4.1), and grade Gate P against it with the honest caveat that Gate G's
   observed order is not measured. Cheapest (§7.3: ~132 core-min for the two solves).
3. Any coarser-than-L2 own-mesh route abandoned as **inadmissible** (§3.2): a ÷4 M6 surface
   cannot be hyperbolically marched within the hard gates.

**Family identity (A5-class) already proved for the built levels:** the three
`constant/polyMesh/points` sha256 (`2b0ce260…` L2, `57852b6f…` L1, and each failed coarse
attempt) are distinct, and the L2↔L1 cell ratio is exactly 8.00. "A family that is not a
family is worse than no band" (`RUNG1_M6_R2:390`) — the {L2, L1} pair IS a genuine r=2
refinement; it is simply a pair, not a triple, and is labelled so.

### 6.1 THE {L2, L1} TWO-LEVEL RICHARDSON BAND — ASSUMED ORDER, HONESTLY LABELLED

For each AGARD station the pair yields a **two-level Richardson estimate with an ASSUMED
order**, NOT an observed order:
- Grid refinement factor **r = 2** (cells ratio 8.00 = r³; 2× linear in each direction).
- **Assumed order `p = 2`** — the FORMAL order of the second-order spatial discretisation
  (`bounded Gauss linearUpwind grad(U)`, `Gauss linear limited corrected`), NOT measured
  from the data (two meshes cannot measure `p`; that needs the third level).
- Richardson estimate `f_h→0 ≈ f_L1 + (f_L1 − f_L2)/(r^p − 1) = f_L1 + (f_L1 − f_L2)/3`.
- Band per station `GCI_pair = Fs·|f_L1 − f_L2|/(r^p − 1) = 1.25·|f_L1 − f_L2|/3`, Fs = 1.25.

**HONEST LABEL, carried verbatim on every figure (mandatory, §4.1):** *"Numerical band from
a TWO-LEVEL Richardson estimate with ASSUMED order p = 2 (formal scheme order), NOT an
observed order. This is a Richardson PAIR, not a Roache CONVERGING triple; the observed
order is not measured. Three levels are required for an observed order (rule 5)."* A `PASS`
against Gate P computed on this pair may NOT be reported as GCI-with-observed-order, and the
rule-5 vocabulary term `CONVERGING` may NOT be applied to a pair.

---

## 7. COST

**Rate:** c7a.4xlarge at $0.0513/core-h (owner-stated; the box cannot read its own
billing, so any dollar figure is **derived, not measured** — `COMPUTE_BUDGET_CHARTER` §5).

### 7.1 Mesh generation — BASE level, MEASURED
From `.../L2/RESULT.json`, 1 rank, wall→core-min:
- pyHyp march: ~52 s → the dominant stage
- plot3dToFoam + createPatch + checkMesh: seconds
- **TOTAL BASE-LEVEL MESH-GEN: 0.8204 core-min (MEASURED).**
  Derived dollars: 0.8204 / 60 × $0.0513 ≈ **$0.0007** (derived, not measured).

No pre-registered estimate existed for this fresh own-family driver, so there is no
estimate/actual ratio to report for the base build itself; the 0.8204 core-min is the
first calibration point for the pyHyp-hyperbolic M6 mesh-gen class and is offered to
`docs/COST_CALIBRATION.md` on the supervisor's release.

### 7.2 Mesh-gen — MEASURED (all built levels) + estimate/actual calibration (rule 12)
From the `RESULT.json` files, 1 rank, wall→core-min:
- L2 base: **0.8204** core-min (§7.1).
- L1 fine (574k-cell N=93 march): **3.525** core-min (`.../L1/RESULT.json`).
- Coarse attempts (8 total: 3 strict-similar + 5-N sweep, all failed): 3.0416 + 3.38 =
  **6.42** core-min (`.../L3/RESULT.json`, `.../L3b/RESULT.json`).
- **TOTAL M6 own-mesh mesh-gen SPENT: 0.8204 + 3.525 + 6.42 = 10.77 core-min (MEASURED).**
  Derived dollars: 10.77 / 60 × $0.0513 ≈ **$0.0092** (derived, not measured).

**Estimate/actual (rule-12 calibration).** §7.2 pre-estimated the full-triple mesh-gen at
**5–15 core-min**; actual for the built levels (L2+L1) plus the 8 coarse attempts is **10.77
core-min** — **inside the estimate band** (ratio actual/predicted ≈ 10.77/10 ≈ 1.08 vs the
midpoint). The gap is attributable to the coarse-level *misprediction* (the pre-estimate
assumed L3 "light" and built once; it took 8 attempts to establish inadmissibility) — a
misprediction, not contention or waste; the 8 attempts are recorded work, not waste (each
produced a needed data point). Offered as a calibration row to `docs/COST_CALIBRATION.md`
on the supervisor's release: first M6 pyHyp-hyperbolic mesh-gen class, incl. the finding
that coarse-end admissibility screening costs ~6 core-min, not ~2.

### 7.3 Eventual SOLVE — ESTIMATE (from a measured rate), per family option
Rate **3.40e-8 core-min / cell / iteration**, MEASURED on this exact geometry and solver
class (`A3-onera-m6-transonic/run_model_run3.log`; `M6SR_PREREGISTRATION.md:462`), at
~6,000 iterations:
- L2 (71,760 cells): 71,760 × 6,000 × 3.40e-8 ≈ **14.6 core-min/solve**.
- L1 fine (574,080): ≈ **117.1 core-min**.
- **{L2, L1} PAIR (option 2): ≈ 131.7 core-min** (single α). Derived dollars ≈ **$0.113**.
- L0 fine (~4.59M cells, option 1): ≈ **936 core-min**.
- **{L2, L1, L0} FINE TRIPLE (option 1): ≈ 1,068 core-min** (single α). Derived dollars
  ≈ **$0.913** (derived, not measured). Each solve is under the $25 pre-auth ceiling; the
  triple total is well inside the $1,000 IBL envelope.
- The failed coarse end (~8,970–17,940 cells) has **no solve** — a mesh that fails the hard
  gates is never solved.

**Envelope:** the full own-family build+solve estimate (mesh-gen ~5–15 + solve ~134
core-min ≈ 2.5 core-h ≈ **$0.13 derived**, even with a generous ×5 restart allowance
under a few dollars) sits **far inside the $1,000 IBL ladder envelope**. Each solve is
under the $25 pre-authorised ceiling; the eventual-solve budget is still costed in the
frozen registration at the supervisor's freeze (rule 12).

---

## 8. WHAT IS AND IS NOT DONE

- **DONE:** own-family run root created; **three mesh levels built and screened** — L2 base
  (71,760, CLEARS), L1 fine (574,080, CLEARS), coarse end (8 attempts, all FAIL); planted
  control fired on every screen (saw 109.219° / 2 neg-vol first); the admissibility
  instrument (`read_checkmesh` + `clears` expr) proven **byte-identical to the L2 base
  screen**; solve-ready patches on L2/L1; AR-138 title page verified by sight; span stations
  and eventual-solve gate transcribed byte-identical from the existing M6 gate; the {L2, L1}
  two-level Richardson band defined and honestly labelled (§6.1); this DRAFT updated.
- **NOT DONE (deliberately STOPPED here):** no flow solve; no admissible coarse level exists
  (§3.2), so no rule-5 CONVERGING triple by coarsening; L0 (the fine-side third level) NOT
  built; this document NOT frozen. Freeze is the cfd-supervisor's check-4; the solve is
  sequenced behind the box drain.

---

## 9. OPEN QUESTION — FLAGGED FOR CHIEF / VERIFICATION (NOT DECIDED HERE)

The M6 own-mesh family gives an admissible **two-level pair {L2, L1}** but **no rule-5
CONVERGING triple** (§3.2, §6). Whether the first-physics M6 surface-`Cp`-vs-AGARD milestone
may stand on this pair, or requires a true three-level triple, **touches rule-5 gating, which
is verification-owned** (VERIFICATION_CHARTER). This DRAFT does not decide it. The two paths:

| path | family | numerical band | solve cost (single α) | honesty status |
|---|---|---|---|---|
| **A — pair** | {L2, L1} | two-level Richardson, **assumed** p=2 (§6.1) | **≈ 131.7 core-min** (~$0.11) | lower-confidence band; NOT `CONVERGING`; observed order unmeasured |
| **B — fine triple** | {L2, L1, L0} | Roache GCI, **observed** order, Fs=1.25 | **≈ 1,068 core-min** (~$0.91) | full rule-5 triple; L0 (~4.6M cells) mesh-gen not capacity-light |

**Question for the chief / verification-supervisor:** does the FIRST PHYSICS milestone
(Sanaa 2026-09-04T1500Z: M6 surface `Cp` at AGARD stations vs tunnel, family band) accept
path A (honestly-labelled Richardson pair) as the milestone, with path B as a later upgrade
to an observed-order triple — or does it require path B up front? Both are inside the $1,000
IBL envelope; the cost delta is ~8× (path B's L0 solve dominates). **cfd-supervisor's
check-4 + verification's rule-5 read settle this before any freeze or solve.**
