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

## 6. REFINEMENT RECIPE FOR THE EVENTUAL ROACHE TRIPLE (r = 2, all three directions)

The base level (L2, §3) is the deliverable of this brief. The triple below is laid out
for a later GCI; **generating L1/L3 is optional and NOT done here.** The design is
RUNG1_M6_R2's INTENDED r=2 triple, **repaired** for the two execution faults that sank it.

| level | surface faces | pyHyp `N` (layers) | expected cells | state |
|---|---|---|---|---|
| **L3** coarse | ~390 (÷4 of L2) | 24 (23) | ~8,970 | **NOT built here.** RUNG1 L3 DEGENERATED: negative-volume cells, non-orth 109°. Repair needed (see below). |
| **L2** medium — **BASE, BUILT** | **1,560** | **47 (46)** | **71,760** | **BUILT & CLEARS gates (§3).** |
| **L1** fine | 6,240 (×4 of L2) | 93 (92) | ~574,080 | **NOT built here.** RUNG1 L1 used the WRONG surface (`m6_surfaceMesh_fine.cgns`, 99,840 faces = ×16, not ×4); its march stopped at 54/93. Repair: use a correctly ×4-refined 6,240-face surface. |

**r = 2 in all three directions** (surface ×4 faces per level = r=2 in the two surface
directions; layers ×2 per level = r=2 wall-normal) → a genuine observed order and family
band (the §4.1 deliverable), not a lower bound.

**Repairs required before the triple is a family:**
1. **L1 surface:** produce a 6,240-face surface by ×4 refinement of the coarse surface
   (or ×4 coarsen of a correct fine surface) — NOT the 99,840-face `..._fine.cgns` that
   over-resolved RUNG1 L1 by 16×.
2. **L3 coarse marching:** the ~390-face / N=24 coarse level collapsed at the farfield
   (negative volumes at `marchDist = 50`). Tune the coarse-level march (smaller effective
   `marchDist`, or more `volSmoothIter`, or a gentler `cMax`) until L3 checkMesh CLEARS
   and shows 0 negative-volume cells — this is a mesh-gen iteration to be recorded as a
   lesson when done, not a gate change.
3. **A5-class family identity:** the three `constant/polyMesh/points` sha256 must be
   distinct and the cell-count ratios must be 8.00 (r³). "A family that is not a family
   is worse than no band" (`RUNG1_M6_R2:390`).

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

### 7.2 Full-triple mesh-gen — ESTIMATE
Base 0.82 (measured) + L1 fine (574k-cell N=93 march, heavier) + L3 coarse (light).
**ESTIMATE ~5–15 core-min** for the three levels (L1 dominates). Labelled ESTIMATE.

### 7.3 Eventual SOLVE — ESTIMATE (from a measured rate)
Rate **3.40e-8 core-min / cell / iteration**, MEASURED on this exact geometry and solver
class (`A3-onera-m6-transonic/run_model_run3.log`; `M6SR_PREREGISTRATION.md:462`), at
~6,000 iterations:
- Base L2 (71,760 cells): 71,760 × 6,000 × 3.40e-8 ≈ **14.6 core-min/solve**.
- L1 fine (~574,080): ≈ **117.1 core-min**. L3 coarse (~8,970): ≈ **1.8 core-min**.
- **Full triple solve ESTIMATE ≈ 133.6 core-min** (single α). Derived dollars: 133.6 /
  60 × $0.0513 ≈ **$0.114** (derived, not measured).

**Envelope:** the full own-family build+solve estimate (mesh-gen ~5–15 + solve ~134
core-min ≈ 2.5 core-h ≈ **$0.13 derived**, even with a generous ×5 restart allowance
under a few dollars) sits **far inside the $1,000 IBL ladder envelope**. Each solve is
under the $25 pre-authorised ceiling; the eventual-solve budget is still costed in the
frozen registration at the supervisor's freeze (rule 12).

---

## 8. WHAT IS AND IS NOT DONE

- **DONE:** own-family run root created; base-level own mesh GENERATED and SCREENED —
  CLEARS both hard gates (non-orth 61.46°, skew 2.06, 0 negative cells, 71,760 cells);
  planted control fired; solve-ready patches; AR-138 title page verified by sight; span
  stations and eventual-solve gate transcribed byte-identical from the existing M6 gate;
  this DRAFT registration.
- **NOT DONE (deliberately STOPPED here):** no flow solve; L1/L3 of the triple not built;
  this document not frozen. The solve is sequenced behind the box drain and takes the
  supervisor's check-4 and the rule-2 freeze then.
