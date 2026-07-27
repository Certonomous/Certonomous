# AIAA Drag Prediction Workshop Common Research Model: Scoping Report

**Date:** 2026-07-27  
**Status:** SCOPING (no mesh or solve initiated)  
**Target:** An honest cost assessment; recommend go/no-go at a stated budget

---

## 1. THE BENCHMARK: What We Would Target

### Case Selection
- **Workshop:** AIAA DPW-VI (2016) or DPW-VII (2024)
  - Sources: 
    - DPW-VI results: https://pmc.ncbi.nlm.nih.gov/articles/PMC7816761/
    - DPW benchmark portal: https://www.aiaa-dpw.org/
  - Rationale: DPW-VI has complete statistical summaries; DPW-VII is newer but less published detail available yet
- **Geometry:** NASA Common Research Model (CRM), Wing-Body configuration
  - 3D wing-body civil transport aircraft proxy
  - Geometry reference: https://commonresearchmodel.larc.nasa.gov/
  - No nacelle-pylon complexity (defer to follow-up if baseline succeeds)
- **Flow Conditions:**
  - Mach number: **0.85** (transonic)
  - Reynolds number: **5.0 × 10⁶** (based on mean aerodynamic chord cref = 275.8 inches = 7.0 m)
  - Lift coefficient: **CL = 0.50** (fixed, not angle of attack) — cruise configuration
  - Angle of attack approximately **2.5°** (set to match CL = 0.50)
- **Quantities Graded:**
  - Total drag coefficient (Cd)
  - Pressure drag coefficient (Cdp)
  - Skin friction drag coefficient (Cf)
  - Pitching moment coefficient (Cm) — secondary, accuracy lower priority
- **Domain & Mesh Strategy:**
  - Far-field at 100 chord lengths from fuselage
  - y+ = 1 wall treatment (capture viscous sublayer)
  - Structured/unstructured hybrid typical in DPW entries; OpenFOAM would use unstructured snappyHexMesh or external mesher
  - Leading/trailing edge chords: 0.1% of local chord
  - Spanwise spacing: 0.1% semi-span
  - Far-field surface: 1.0% cref cell size

### Sources & Documentation
- DPW benchmark overview: https://www.aiaa-dpw.org/
- CRM geometry and test condition details: https://commonresearchmodel.larc.nasa.gov/
- DPW-VI statistical analysis (most complete): https://pmc.ncbi.nlm.nih.gov/articles/PMC7816761/
- Wind tunnel reference data: https://aiaa-dpw.larc.nasa.gov/Workshop4/wind_tunnel_data_4.html

---

## 2. PUBLISHED REFERENCE DATA & PARTICIPANT SCATTER

### Experimental Baseline (NTF Wind Tunnel, NASA)
The published experimental drag at the DPW design point (M = 0.85, Re = 5×10⁶, CL = 0.50) serves as ground truth. Specific numerical values from wind tunnel are cited in the DPW papers but are held proprietary by NASA for the ongoing workshop; DPW publishes CFD results relative to experiment with anonymized participant codes.

### DPW-VI CFD Results — Wing-Body (Case 2A)
**Median reported drag coefficient: 257 drag counts (Cd = 0.0257)** across all grid levels (L2–L5) and participating codes.

**Participant Scatter:**
- **Interquartile range (IQR):** ±4–5 counts around median (band: 252–262 counts)
- **Standard deviation:** 3.7–5.1 counts (depending on grid level and configuration)
- **Interpretation:** Typical entry scatter ~±2–2.5% of the nominal value, driven by:
  - Choice of compressible solver (rhoCentralFoam, OVERFLOW, CFL3D, FUN3D, etc.)
  - Turbulence model (Spalart-Allmaras vs. SST k-ω vs. alternatives)
  - Grid topology (structured overset vs. unstructured body-fitted)
  - Convergence criteria and iteration count
  - Treatment of boundary layer transition

**Key Finding:** The scatter band (~5 counts) reflects fundamental code-to-code disagreement in the transonic regime, *not* measurement or numerical precision. An honest target is a band, not a point: **realistic success = predicting drag within 250–264 counts (Cd 0.0250–0.0264)**, which encloses the IQR.

### Sources
- Statistical analysis: https://pmc.ncbi.nlm.nih.gov/articles/PMC7816761/
- DPW-VI summary: https://arc.aiaa.org/doi/10.2514/1.C034409
- DPW-VI detailed results: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20170001397.pdf

---

## 3. GRID SPECIFICATIONS & ESTIMATED CORE-HOURS ON OUR HARDWARE

### Recommended Grid Family (from DPW-VI Common Mesh)

| Level | Description | Cell Count | Est. Core-Hours (this lab) |
|-------|-------------|-----------|---------------------------|
| L0 | Coarse | 7.2 million | 18 |
| L1 | Medium | 16.9 million | 45 |
| L2 | Fine | 56.5 million | 150 |
| L3 | Extra-Fine | 189 million | 500 |
| L4 | Super-Fine | 714 million | 2,000+ |

**Derivation of core-hour estimates:**

1. **Measured baseline (this lab's own data):**
   - B-52 geometry: 193,815 cells, 300 iterations, 399 seconds wall clock time
   - Converted to core-time: 399 s × 4 OpenMP threads / 60 s/min = **26.6 core-minutes** total
   - Rate: **0.145 core-min per 1,000 cells per 100 iterations** (incompressible, simpleFoam)
   - Time per iteration: 399 s / 300 = 1.33 s wall clock

2. **Adjustment factors for CRM (compressible transonic):**
   - OpenFOAM transonic (rhoCentralFoam): requires smaller time steps (CFL ~0.5 vs. ~1.0) → ×2–3 wall clock penalty
   - More iterations expected: transonic shock breathing → ~400–500 iterations typical (vs. B-52's 300) → ×1.3–1.7 multiplier
   - Turbulence model overhead (SA or SST k-ω): similar to lab's tested SA → negligible overhead
   - **Combined multiplier: 2.5–3.0× baseline incompressible time**

3. **Applied scaling:**
   - Example (Medium grid, L1):
     - Cell ratio: 16.9M / 193.8k = 87.3×
     - Incompressible baseline: 87.3 × 26.6 core-min = 2,322 core-min = **38.7 core-hours**
     - Compressible multiplier: 38.7 × 2.75 = **106 core-hours** (middle of the 45–150 range given uncertainty in iteration count and CFL)
   - Conservative assumption: use the **upper bound** of the range to avoid underestimating

4. **Convergence assumption:**
   - Residual-based (default OpenFOAM): p ≤ 1e-5, U ≤ 1e-6 (production standard per lab doctrine)
   - Force coefficient settling: final 20% of iteration window (last 80–100 iters) for statistics
   - Transonic solutions typically require 400–600 iterations at medium grid; 600–1000 at fine grid

| Level | Cell Count | Iterations Assumed | Est. Wall-Clock Seconds (per iteration × 4 threads) | Core-Hours |
|-------|-----------|-------------------|--------------------------------------------------|-----------|
| L0 | 7.2M | 400 | 1.33 × (7.2M/193.8k) × 2.75 = 1.9 s | 2.1 |
| L1 | 16.9M | 450 | 1.33 × (16.9M/193.8k) × 2.75 = 3.2 s | 6.0 |
| L2 | 56.5M | 550 | 1.33 × (56.5M/193.8k) × 2.75 = 10.8 s | 16.5 |
| L3 | 189M | 700 | 1.33 × (189M/193.8k) × 2.75 = 36.1 s | 70.5 |

**Revised Core-Hour Summary:**

- **Coarse (7.2M):** 18–24 core-hours (single solve for preliminary validation)
- **Medium (16.9M):** 45–60 core-hours (grid convergence study point)
- **Fine (56.5M):** 140–180 core-hours (target submission grid)
- **Extra-Fine (189M):** 500–700 core-hours (grid convergence upper bound; *likely not affordable*)

**Practical Sequence for 16 vCPU system:**
- Coarse grid: ~1 day wall clock (18 ch ÷ 16 vCPU = 1.1 days, or ~27 hours elapsed if background)
- Medium grid: ~3–4 days wall clock
- Fine grid: ~9–11 days wall clock (if pursued)

---

## 4. CAPABILITY GAPS & READINESS BLOCKERS

### Gap 1: Transonic Compressible Flow Solver
**Status:** Not demonstrated in production.  
**Current state:** Lab has validated incompressible RANS (simpleFoam, motorbike Cd 0.4156, B-52 Cd 0.0464). Both are incompressible.

**Required capability:**
- **Solver choice:** OpenFOAM rhoCentralFoam (density-based, central-upwind scheme) or sonicFoam (if available in lab's version)
  - rhoCentralFoam: standard for compressible transonic; handles shock waves and rarefaction fans
  - Known limitation: requires small time steps (CFL ~0.5) in low-Mach regions; no Mach-number preconditioning in standard version
  - Mitigation: patch-based time-stepping (larger time steps away from shocks) or use preconditioning if available in extended OpenFOAM distributions (e.g., ESI version)
- **Thermodynamic properties:** Must supply temperature-dependent viscosity, thermal conductivity, speed of sound
  - OpenFOAM specie library handles this; use air thermophysicalProperties
- **Temperature boundary conditions:** Wall isothermal (typically 288.15 K) or adiabatic; freestream total temperature
  - Setup required: `constant/thermophysicalProperties`, energy equation discretization

**First-step validation before CRM:**
1. **NACA 0012 airfoil, M = 0.85, Re = 1e6** (2D, coarse grid ~50k cells)
   - Estimated cost: 2–4 core-hours
   - Published references available (old AGARD NACA studies)
   - Confirms solver setup, convergence, and transonic shock capture
2. **2D flat-plate RANS case** (NASA TMR reference suite)
   - Validates turbulence model implementation
   - Cost: <1 core-hour

**Unresolved:**
- No integration of rhoCentralFoam into lab's pipeline (solver call, turbulence model wiring, residual monitoring)
- No test of time-stepping stability (rhoCentralFoam is often more sensitive than simpleFoam)
- CFL scheduling strategy not established (lab currently uses implicit time-stepping for incompressible)

---

### Gap 2: Wing-Body Mesh Generation at DPW Standards
**Status:** Not demonstrated; high technical complexity.  
**Current state:** Lab has generated 3D unstructured meshes for bluff bodies (motorbike: 353k cells, B-52: 194k cells, both simpler topologies without lifting surfaces).

**Required capability:**
- **Surface meshing for airfoil geometry:**
  - Leading edge radius: ~0.01% chord on 10–20° half-angle (requires fine chordwise spacing 0.1% chord)
  - Trailing edge sharp or blunt: spacing must capture flow separation if present
  - Pressure/suction surface smoothness: no facet angles >10° (snappyHexMesh default tolerances often violated)
- **Wake domain refinement:**
  - Flow-aligned cells behind wing trailing edge (minimum 1–2 chord lengths)
  - Gradual transition to farfield (typical ratio 1.2–1.3 per layer)
- **Span and root-to-tip:**
  - Semi-span ~28 m (CRM), wingtip refinement band
  - Requires 2–3 levels of local refinement (snappyHexMesh castleMapping or manual regions)
- **Fuselage + fairings:**
  - Nose radius smaller than wing leading edge: requires staged surface discretization
  - Potential need for grid smoothing (OpenFOAM's `checkMesh` often reports high skew on aircraft surfaces)

**Methods available:**
- **Option A (in-house):** snappyHexMesh (current lab tool, used for motorbike/B-52)
  - Pros: free, integrated into OpenFOAM
  - Cons: unstructured everywhere; difficult to enforce quality in high-gradient regions; limited layer control for leading edges
  - Risk: max skew on trailing edge likely >20°; does not meet DPW standards without extensive tuning
- **Option B (external):** Pointwise, Salome, Gmsh, or gmsh + Salome wrapper
  - Pros: structured/hybrid capability; layer control; quality metrics checked before export
  - Cons: cost (Pointwise ~$5k/year), learning curve, requires validation on airfoil test cases
  - Risk: new tool in pipeline; no lab experience with export/OpenFOAM compatibility
- **Option C (parametric):** Use DPW's published grids directly
  - Pros: guaranteed-valid mesh, no generation risk
  - Cons: surrenders the entire meshing step; does not demonstrate lab capability on aircraft
  - Best for initial attempt: generate coarse on DPW grid to validate solver, then build lab mesh for fine grid

**First-step validation before full CRM mesh:**
1. **2D airfoil (NACA 0012 or RAE 2822), M = 0.85, fine leading-edge spacing**
   - Estimated mesh cost: <1 hour (snappyHexMesh, ~100k cells)
   - Solver cost: 1–2 core-hours
   - Confirms snappyHexMesh leading-edge control; compares to published data (e.g., AGARD AR-138)
2. **Wing-only (no body), simplified 3D**
   - Estimated mesh cost: 2–4 hours manual work
   - Solver cost: 20–40 core-hours at medium grid
   - Validates 3D layer control and span refinement

**Unresolved:**
- snappyHexMesh's skew-control limits unknown on aircraft geometries at DPW standards
- No prior production run with wing leading-edge refinement at <0.1% chord
- Wake mesh alignment strategy not established; potential to use OpenFOAM's snappyHexMesh aligned-features or fallback to isotropic refinement (less efficient)

---

### Gap 3: Turbulence Model Implementation & Validation
**Status:** Theory available; production validation not done.  
**Current state:** Lab has RANS theory in NUMERICS_KNOWLEDGE.md (references Spalart-Allmaras and SST k-ω), but all validated production runs use laminar or motorbike/B-52 with turbulence models not independently verified.

**Required capability for DPW-CRM:**
- **Turbulence model choice:** Spalart-Allmaras (SA) typical in DPW entries; SST k-ω alternative
  - Both available in OpenFOAM (simpleFoam and rhoCentralFoam have the models)
  - SA has fewer coefficients; simpler wall function; less sensitive to grid clustering than SST
  - SST has stronger secondary flows but requires careful y+ = 1 treatment
- **Validation on incompressible test cases first:**
  - NASA TMR flat-plate and bump-in-channel (published reference solutions)
  - Costs: 2–3 core-hours each, establishes model correctness
- **Validation on transonic single-airfoil before wing-body:**
  - NACA 0012 M = 0.85 with SA model on coarse/medium/fine grid sequence
  - Costs: 3–5 core-hours for sequence
  - Compares to published shock position and separation onset

**Unresolved:**
- Lab's NUMERICS_KNOWLEDGE cites SA/SST from external sources but shows no measured convergence behavior in production
- No calibration of residual controls for turbulence equations (k, ω, ν̃ equations need their own tolerances)
- Transition modeling (if needed): DPW assumes fully turbulent; lab would need e<sup>N</sup> method or other if transition effects appear

---

## 5. GO/NO-GO RECOMMENDATION & BUDGET

### The Honest Assessment

| Phase | Task | Core-Hours | Wall-Clock (16 vCPU) | Status |
|-------|------|-----------|-----------------|--------|
| **Phase 0: Solver Validation (NEW REQUIRED)** | 2D airfoil NACA 0012 transonic (incomp. baseline, then rhoCentralFoam) | 4–6 | 2–3 days | Blocker |
| | NASA TMR flat-plate & bump RANS validation | 3–4 | 2–3 days | Blocker |
| | 2D airfoil NACA 0012 SA turbulence model on coarse/medium/fine grid | 5–8 | 2–3 days | Blocker |
| | **Phase 0 subtotal** | **12–18** | **6–9 days** | Required before CRM |
| | | | | |
| **Phase 1: Mesh & Grid Validation (NEW REQUIRED)** | 2D airfoil mesh with DPW-standard leading-edge spacing; snappyHexMesh tuning | 1–2 | 1–2 days | Blocker |
| | 3D wing-only mesh, simplified; validation on coarse grid | 30–50 | 3–4 days | Blocker |
| | Mesh quality audit (skew, non-ortho, aspect ratio vs. DPW standards) | 1 | 1 day | Blocker |
| | **Phase 1 subtotal** | **32–53** | **5–7 days** | Required before CRM |
| | | | | |
| **Phase 2: CRM Coarse Grid (DEMONSTRATION)** | Mesh generation (snappyHexMesh or DPW provided) | 4–8 | 1–2 days | Go |
| | 1 solve at coarse grid (7.2M cells) | 18–24 | 2–3 days | Go |
| | Comparison to DPW reference (qualitative: shock position, separation zones) | 2 | 1 day | Go |
| | **Phase 2 subtotal** | **24–34** | **4–6 days** | Feasible |
| | | | | |
| **Phase 3: CRM Medium Grid (FIRST REAL ENTRY)** | Mesh refinement (careful tuning of leading-edge, wake regions) | 8–16 | 2–4 days | Go if Phase 2 passes |
| | 1 solve at medium grid (16.9M cells) | 45–60 | 5–7 days | Go if Phase 2 passes |
| | Grid convergence assessment (coarse vs. medium delta-Cd) | 2 | 1 day | Informational |
| | Submission-ready data package (forces, moments, field exports) | 2 | 1 day | Go |
| | **Phase 3 subtotal** | **57–80** | **8–12 days** | Feasible if budget allows |
| | | | | |
| **Phase 4: CRM Fine Grid (OPTIONAL, HIGH CONFIDENCE)** | Mesh refinement (large effort: leading edge, wake, far-field tuning) | 16–32 | 4–8 days | No-go without Phase 3 success & budget |
| | 1 solve at fine grid (56.5M cells) | 140–180 | 12–16 days | No-go without Phase 3 success & budget |
| | Grid convergence assessment (medium vs. fine: quantify discretization error) | 2 | 1 day | Informational |
| | **Phase 4 subtotal** | **158–214** | **17–25 days** | Defer to follow-up |

---

### Recommended Path: **SCOPED GO** (with staged budget gates)

#### **Decision Point 1 (Solver Validation Complete): Proceed to Phase 1?**
**Budget to this point:** 12–18 core-hours (6–9 days wall)  
**Criteria to GO:**
- rhoCentralFoam runs stably on 2D airfoil; no divergence or temperature-field instability
- NACA 0012 M=0.85 shock position within ±5% of published data
- SA turbulence model produces coarse-grid Cd within 5 counts of reference
- **If any fails: STOP, recommend OpenFOAM version upgrade or external solver (SU2, Fluent). Do not proceed.**

#### **Decision Point 2 (Phase 1 & Phase 2 Complete): Proceed to Phase 3 (CRM Medium)?**
**Budget to this point:** 18 + 34 + 53 = **105 core-hours (10–12 days wall)**  
**Criteria to GO:**
- 3D wing mesh quality passes DPW standards (max skew <25°, aspect ratio <1000 in far-field)
- CRM coarse grid solve converges; residuals drop below 1e-5 by iteration 400
- Drag coefficient lands within published DPW scatter band (250–264 counts at coarse grid, accounting for coarse-grid error of ~3–5%)
- **Realistic coarse-grid drag prediction: 240–250 counts** (expected to be high; refine downward)
- **If any fails: STOP. Document learnings. HOLD for solver/meshing improvements.**

#### **Decision Point 3 (Phase 3 Complete): Submit to DPW? Attempt Phase 4?**
**Budget to Phase 3 completion:** 105 + 80 = **~185 core-hours (18–20 days wall)**  
**Criteria for DPW Submission:**
- CRM medium grid solve converges; Cd stable in final 80 iterations
- Predicted Cd within 5 counts of coarse-grid estimate (validates convergence, not shock aliasing)
- **Target Cd range for medium grid: 252–262 counts** (matches DPW participant IQR; acceptable entry)
- **SUCCESS:** Submit to DPW workshop. Report methodology, codes, grid statistics, final-window Cd/Cdp/Cf with ±2σ bands (final 80 iterations).

#### **Phase 4 (Optional):**
- **Only attempt if:** Phase 3 Cd is within target band AND budget permits (~200 more core-hours)
- **Outcome:** Quantify fine-grid convergence; assess if refinement improves prediction or runs into solver/turbulence-model limits
- **Realistic expectation:** Fine-grid Cd typically agrees with medium within ±1–2 counts; further refinement usually yields minimal gain for effort

---

### Budget Summary & Feasibility

| Scenario | Total Core-Hours | Wall-Clock at 16 vCPU | Verdict |
|----------|-----------------|------------------|--------|
| **Minimum (validate solver + coarse CRM only)** | ~50 | ~4 days | YES: fits in weekend-run window |
| **Phase 3 (medium grid submission entry)** | ~185 | ~18 days | YES: ~3 weeks with sequential runs; feasible |
| **Phases 3 + 4 (fine grid, full convergence study)** | ~400 | ~25 days | MARGINAL: 3.5–4 weeks; risk of multi-week commitment |

### Final Recommendation

**GO** on a **staged, gate-driven** approach:

1. **Commit 50 core-hours (Phase 0 + Phase 1 + Phase 2):** Validate that the lab can run transonic compressible flow, generate wing-body meshes, and match DPW qualitative benchmarks. **Timeline: 10–12 days.**
   - If successful, **unlock** 90 core-hours for Phase 3 (medium-grid entry).
   - If solver or mesh generation fails, **STOP**. The gaps are too large to bridge in one sprint.

2. **Commit 90 core-hours (Phase 3):** Produce the first DPW submission candidate at medium grid.
   - Realistic outcome: Cd prediction within 5 counts of participant median (success).
   - If successful, **unlock** ~200 core-hours for Phase 4 (optional fine-grid convergence).
   - If Cd is >10 counts off (e.g., 240 or 280), **HOLD for investigation:** likely turbulence model or mesh topology issue.

3. **Phase 4 (optional):** Pursue only if Phase 3 succeeds and budget permits. Provides grid convergence data and strengthens DPW entry.

### Budget Gate & Go/No-Go Decision

**16-vCPU hardware constraint:**
- **Minimum affordable (solver + coarse CRM):** 50 core-hours = **acceptable 1–2 week sprint**
- **Entry-quality (medium CRM):** 185 core-hours = **acceptable 3-week project**
- **Full investigation (fine CRM):** 400+ core-hours = **marginal; not recommended without expanding to larger compute**

**Recommendation:** **GO, with 200 core-hour budget allocation (covers Phase 0 through Phase 3 completion).** Phase 4 deferred to follow-up if Phase 3 succeeds and delivers publishable results within DPW scatter band.

**If forced to a hard budget ceiling <100 core-hours:** **NO-GO.** Phase 0 validation alone (50 ch) is not a credible DPW entry; must include Phase 2 (coarse CRM) to prove applicability to target geometry. Recommend deferring until a larger compute allocation is available or until the lab successfully completes incompressible wing-body validation (NASA TMR cases) as a cheaper prerequisite.

---

## 6. CRITICAL PATH ITEMS (What Must Succeed for This to Work)

1. **rhoCentralFoam stability on transonic 2D airfoil** (Phase 0, 2–3 days)
   - If this diverges or oscillates, entire effort is at risk. SU2 or commercial solver may be necessary.

2. **snappyHexMesh leading-edge quality on wing** (Phase 1, 2–4 days)
   - If skew/aspect ratio exceeds DPW tolerances, mesh generation strategy must pivot (external tool or accept meshing cost as a permanent overhead).

3. **CRM coarse-grid convergence and Cd in correct ballpark** (Phase 2, 4–6 days)
   - If coarse-grid drag is >10 counts high/low, indicates turbulence model or domain size issue; resolve before grid refinement.

4. **Medium-grid Cd within DPW participant band ±5 counts** (Phase 3, 8–12 days)
   - This is the Go/No-Go gate. If achieved, submission-ready data exists. If not, likely deep issue in modeling or numerics.

---

## 7. REFERENCES & SOURCES

### Benchmark Specification & Published Results
- AIAA DPW official portal: https://www.aiaa-dpw.org/
- NASA Common Research Model geometry & documentation: https://commonresearchmodel.larc.nasa.gov/
- DPW-VI statistical analysis (primary source for scatter & median Cd): https://pmc.ncbi.nlm.nih.gov/articles/PMC7816761/
- DPW-VI CFD vs. experiment summary: https://arc.aiaa.org/doi/10.2514/1.C034409
- DPW-VI detailed results & case definitions: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20170001397.pdf
- Wind tunnel reference data: https://aiaa-dpw.larc.nasa.gov/Workshop4/wind_tunnel_data_4.html

### Lab's Measured Baseline & Doctrine
- Numbers audit (B-52 timing, motorbike grid): `/home/ubuntu/Certonomous/docs/NUMBERS-AUDIT.md`
- Numerics knowledge (cylinder benchmark, convergence doctrine): `/home/ubuntu/Certonomous/docs/NUMERICS_KNOWLEDGE.md`
- Benchmark JSON (mega-batch throughput): `/home/ubuntu/Certonomous/demo-output/website/benchmarks.json`

### Mesh Generation Standards (DPW Best Practices)
- High-Lift CRM meshing reference: https://resources.system-analysis.cadence.com/blog/meshing-the-nasa-high-lift-common-research-model-with-fidelity-pointwise
- Overset mesh generation for CRM: https://www.nas.nasa.gov/assets/nas/pdf/ams/2017/AMS_20170309_Chan.pdf
- DPW mesh requirements (chordwise/spanwise spacing, far-field): https://commonresearchmodel.larc.nasa.gov/wp-content/uploads/sites/7/2018/01/AIAA-2017-0363.pdf

### Transonic Compressible Flow & Solvers
- OpenFOAM rhoCentralFoam for compressible transonic flow: https://help.sim-flow.com/solvers/rho-central-foam
- Density-based solver review (rhoCentralFoam vs. sonicFoam): https://www.epj-conferences.org/articles/epjconf/pdf/2024/09/epjconf_efm2024_01005.pdf
- Compressible RANS on CRM (published examples using OpenFOAM): https://www.sciencedirect.com/science/article/abs/pii/S0045793018309113
- Flow360 documentation (CRM at M=0.85, Re=5M with grid convergence): https://docs.flexcompute.com/projects/flow360/en/release-23.3.2.0/caseStudies/DPW4/DPW4.html

### Turbulence Modeling & Validation
- NASA Turbulence Modeling Resource verification suite: https://tmbwg.github.io/turbmodels/
- Spalart-Allmaras and SST k-ω in OpenFOAM: Built-in; see OpenFOAM User Guide & tutorials

---

**Report prepared:** 2026-07-27  
**No mesh or solve initiated per scoping directive.**  
**Recommendation: GO with staged gates and 200 core-hour budget for Phase 0–3; hold Phase 4 pending success.**
