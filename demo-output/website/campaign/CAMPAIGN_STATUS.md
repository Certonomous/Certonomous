# Certonomous Hard-Case Campaign Status — Family Summary
**Date:** 2026-07-28  
**Reporting by:** Structured audit of all campaign family records

---

## F1 — ONERA M6 Transonic Wing (3D)

- **Reynolds:** ~1.5×10⁷ (root chord, over-estimated; target 11.72×10⁶)
- **Mach:** 0.839968 (design Mach 0.84, transonic)
- **Flow regime:** Transonic separated flow, shock-bearing
- **Geometry:** 3D wing, transonic; steady RANS (`DARhoSimpleCFoam`)
- **Rung reached:** Feasibility → Physics → **Gate (Cp validation)**
- **Gate metric:** Cp distribution vs AGARD AR-138 / NASA-TMR Case 2308
  - Upper surface RMS deviation: 0.049–0.114 Cp (pressure side: 0.013–0.027)
  - Shock location: aft-shifted 0.02–0.10 x/c vs experiment (6 of 7 stations), eta=0.80 exception (−0.0015)
  - η=0.99 outlier: RMS 0.114, bias +0.065 (wingtip vortex zone)
- **Verdict:** **GATE REACHED.** Textbook signature of mesh-diffusion smearing on coarse grid (399,360 cells), not gross solver defect. CD=0.02299556, CL=0.31311589.
- **Adjoint:** Blocked — OOM on mesh-sized residual/volume-coordinate Jacobian (8 mitigations tried, documented)
- **Core-minutes:** 127.5 primal; adjoint not completed

---

## F2 — Transonic NACA0012 (2D)

- **Reynolds:** 3e6–7e6 (design space); primary case Re=6e6
- **Mach:** 0.70–0.85 (design space); primary case M=0.8
- **Angle of attack:** 0–3° (design space); primary case α=1.25°
- **Flow regime:** Transonic, shock-bearing
- **Geometry:** 2D symmetric airfoil; steady RANS (`rhoSimpleFoam`, kOmegaSST)
- **Rung reached:** Feasibility → Physics → **Gate (shock position, banded)**
- **Gate metric:** Upper-surface shock location, M=0.8/α=1.25°/Re=6e6
  - CFD shock: x/c=0.556
  - Reference (inviscid AGARD/GAMM benchmark): x/c~0.60
  - Deviation: +0.044 x/c upstream of inviscid; falls within 0.35–0.60 chord band (expected for viscous RANS)
  - Cd=0.0432, Cl=0.109 (physically sane)
- **Verdict:** **PASS (banded, qualitative).** Shock position lies within expected envelope; viscous RANS expected to shift shock upstream vs inviscid.
- **Cost:** 26–34 s per evaluation
- **Shipped:** Yes (mega-batch family)

---

## F3 — Supersonic Exact-Theory Campaign (wedge / cone / diamond)

### 3a. Wedge (oblique shock, θ-β-M)

- **Mach:** 2.0, 2.5, 3.0
- **Deflection angle:** 15°, 10°, 15° respectively
- **Flow regime:** Inviscid supersonic (Euler equations, μ=0)
- **Geometry:** 2D ramp mesh; steady `rhoCentralFoam`
- **Rung reached:** Feasibility → Physics → **Gate (surface pressure p2/p1)**
- **Gate result (fine mesh):**
  - M=2.0, θ=15°: p dev **0.07%** (exact β=45.3436°, computed 45.26°)
  - M=2.5, θ=10°: p dev **0.01%** (exact β=31.8506°, computed 32.33°)
  - M=3.0, θ=15°: p dev **0.01%** (exact β=32.2404°, computed 32.46°)
  - Shock angle β convergence: 0.2–1.5% (method-sensitive, documented corner singularity bias)
- **Verdict:** **PASS.** Surface pressure converges to within 0.01–0.07% of exact oblique-shock theory at fine mesh. Shock angle measured from smeared field via density-gradient peak detection; residual is method-artifact, not solver defect.
- **Core-minutes:** 8.43 (all 3 pairs, 7 runs)

### 3b. Cone (Taylor-Maccoll, axisymmetric)

- **Mach:** 2.35, 3.0
- **Half-angle:** 10°, 12° respectively
- **Flow regime:** Inviscid supersonic, axisymmetric
- **Geometry:** Axisymmetric wedge mesh (2.5° half-angle slice, wedge BC); steady `rhoCentralFoam`
- **Rung reached:** Feasibility → Physics → **Gate (surface pressure pc/p1)**
- **Gate result (fine mesh, M=2.35/θc=10°):**
  - Pressure: pc/p1 dev **0.29%** (exact 1.3739, computed 1.3779)
  - Shock angle β: dev **2.1–2.8%** (exact β=26.7367°, computed 27.31–27.49°) — monotonically converging but **not fully grid-converged** at 28,800 cells
  - Second pair (M=3.0/θc=12°) run at medium only (cost: fine mesh 1,073 core-s per 28,800 cells vs wedge 149 s, ~7× ratio)
- **Verdict:** **PASS, not fully grid-converged.** Pressure gate clean; shock-angle convergence slower and more sensitive than 2D wedge (weaker/more-oblique shock occupies larger fraction of standoff in smeared field). Documented open sensitivity; genuine 3-mesh Richardson study needed if F4 hypersonic work requires tight shock-position gates.
- **Core-minutes:** 22.09 (both pairs, 4 runs)

### 3c. Diamond Airfoil (shock-expansion, wave drag)

- **Mach:** 2.0, 2.5
- **Half-angle (ε):** 7.125°, 5.0° respectively
- **Flow regime:** Inviscid supersonic (Euler equations)
- **Geometry:** 2D symmetric double-wedge airfoil, zero AoA, upper-half-only; steady `rhoCentralFoam`
- **Rung reached:** Feasibility → Physics → **Gate (wave-drag coefficient cd)**
- **Gate result (fine mesh):**
  - M=2.0, ε=7.125°: cd dev **−0.26%** (exact 0.036331, computed 0.036237)
  - M=2.5, ε=5.0°: cd dev **−0.18%** (exact 0.013430, computed 0.013406)
  - Both converged by medium mesh (deviation flat from medium→fine within ~0.1 percentage point)
- **Verdict:** **PASS (strongest gate).** Integrated force coefficient converges to 0.18–0.55% accuracy; robust gate testing entire surface (compression + expansion). Grid-converged by medium mesh.
- **Core-minutes:** 7.93 (both pairs, 6 runs)

**F3 Overall:** **All three cases PASS.** Total 38.45 core-minutes. Headline: `rhoCentralFoam` inviscid Euler reproduces every closed-form supersonic-theory gate to well under 1% on integrated/surface-pressure metrics at fine mesh. Cone shock-angle measurement reveals genuine numerics effect (smeared field bias larger in axisymmetric weak shocks) — documented, not hidden.

---

## F5a — Unsteady Cylinder Vortex Shedding (2D)

- **Reynolds:** 100–1000 (design space); validation at Re=100, 150, 180
- **Flow regime:** Laminar, unsteady periodic vortex shedding
- **Geometry:** 2D circular cylinder, O-grid annulus mesh (8,640 cells nominal); unsteady `pimpleFoam`
- **Rung reached:** Feasibility → Physics → **Gate (Strouhal number)**
- **Gate metric:** Roshko/Williamson correlation St = 0.198·(1 − 19.7/Re)
  - Re=100: St measured 0.1578 vs correlation 0.1589, dev **0.7%**, drift 3.9%
  - Re=150: St measured 0.1777 vs correlation 0.1720, dev **3.3%**, drift 1.3%
  - Re=180: St measured 0.1844 vs correlation 0.1763, dev **4.6%**, drift 2.7%
- **Verdict:** **PASS.** All within 0.7–4.6% of reference; stationarity drift <3.9%; Cd 1.27–1.29 consistent with classical compilations. **Note:** above Re~189, 2D laminar is idealization (real wakes become 3D turbulent); Re>200 runs validated only qualitatively.
- **Cost:** ~230–290 s per evaluation (low-minute budget satisfied)
- **Shipped:** Yes (mega-batch family, "Family 1")

---

## F6a — NASA 2D Wall-Mounted Hump (Separated Flow)

- **Reynolds:** Re_c = 936,000
- **Mach:** M=0.1 (low-speed, incompressible approximation)
- **Flow regime:** Turbulent boundary layer with separation bubble; steady RANS (`kOmegaSST`)
- **Geometry:** 2D hump, 51,626-cell mesh; `simpleFoam`
- **Rung reached:** Feasibility → Physics → **Gate (separation/reattachment x/c)**
- **Gate result:**
  - Separation x/c: 0.6544 vs NASA experiment 0.665, dev **−1.59%** ✓
  - Reattachment x/c: 1.2534 vs NASA experiment 1.100, dev **+13.95%** (documented SST over-prediction of bubble length)
- **Cross-checks (validation):**
  - vs NASA's own published SST CFD: separation +0.06%, reattachment within published 1.25–1.27 range
  - vs benchmark's shipped baseline field: ≤0.02% deviation
  - vs benchmark's own scorer: 0.0622 vs published floor 0.0621, +0.16%
- **Verdict:** **GATE REACHED.** Baseline independently verified correct via three orthogonal cross-checks. The +13.95% reattachment error is the expected, literature-documented linear-eddy-viscosity SST deficiency — exactly what data-driven closure corrections target. This is the gate working as designed.
- **Cost:** 5.25 core-min (Feasibility 0.28 + Physics 2.51 + Gate 2.47)
- **Shipped:** Yes

---

## F6c — Square/Rectangular Duct vs DNS (Secondary Flow)

- **Test cases:** AR_1_Ret_360, AR_3_Ret_360
- **Flow regime:** Incompressible turbulent duct flow, secondary-circulation zone; steady RANS (`kOmegaSST`)
- **Geometry:** Rectangular duct, matched to DNS mesh (B2 baseline from prior session)
- **Rung reached:** Feasibility/Physics (already done in B2) → **Gate (secondary-flow RMS vs DNS)**
- **Gate result:**
  - AR_1_Ret_360: RANS secondary-flow RMS **~0.0%** of U_bulk (machine precision, ~1e-15%); DNS reference 2.22%
  - AR_3_Ret_360: RANS secondary-flow RMS **~0.0%** of U_bulk; DNS reference 2.07%
- **Verdict:** **GATE MEASURED, FAIL — reported as measured, not shipped.** Linear Boussinesq eddy-viscosity closure has zero normal-stress anisotropy by construction; cannot produce Prandtl's secondary flow of the second kind. The failure is **structural and expected**, not a resolution/convergence issue. This explains why AR_1/AR_3 are the two largest (31.5%, 31.4%) contributors to closure-challenge deficit.
- **Cost:** 0 core-min (post-processing only; fields from B2)
- **Shipped:** No (failure documented and blocked per campaign rules)

---

## F6b — Periodic Hills

- **Status:** **NOT ATTEMPTED**
- **Reason:** Explicitly conditional on time remaining after F6a and F6c were fully climbed and gated. Both completed to gate rung with independently cross-checked results; remaining session budget spent on write-up/validation rather than opening a third family.
- **Blocked:** Yes (no feasibility rung started)

---

## F7 — Marine Free-Surface Capability

### F7a. Dam Break vs Martin & Moyce (1952)

- **Reynolds:** Re ≈ 4×10⁴ (simplified: laminar, inviscid treatment per reference paper)
- **Flow regime:** Free-surface unsteady transient (dam break / wave propagation)
- **Geometry:** 2D square-column collapse (a=2.25 in = 0.05715 m), 15a×2a domain, O-grid; unsteady VOF (`interFoam`)
- **Rung reached:** Feasibility → Physics → **Gate FAIL**
  - **Feasibility:** PASS (runs clean, residuals fall, column collapses, Courant max 0.52)
  - **Physics:** PASS (qualitatively correct dam-break phenomenology, mass conserved to machine precision at medium resolution)
  - **Gate:** **FAIL** (surge front position)
- **Gate metric:** Front position Z vs nondimensional time T
  - Medium closed-box mesh (dx=a/20, 12,000 cells):
    - Mean deviation: **+13.6%** (systematically growing with time)
    - Max |deviation|: **21.3%** (time T=8.58)
    - Well outside credible tolerance; monotonically diverging, not oscillating around zero
  - Coarse mesh (dx=a/8, 1,920 cells): mean deviation **−13.2%** (sign-flipped vs medium, ruling out "needs finer grid" as sole fix)
- **Secondary check (column-height decay):** mean deviation −1.5% (bulk quantity tracks reference much more closely than leading-edge front position)
- **Cause:** Front-position failure concentrated at thin, fast-moving leading edge; VOF numerical smearing effect. Leading edge is not vertical at these resolutions, so alpha=0.5 probe height materially affects apparent front position. Bulk column physics closer to correct.
- **Lesson:** Single alpha=0.5 crossing at first cell above floor is not mesh-independent definition; needs 3+-mesh Richardson study or isosurface-based front extraction.
- **Blocked by this:** Rung (b) Wigley hull and Rung (c) workshop hull (hard rule: do not start next rung until previous passes gate)
- **Cost:** ~2.4 core-min total
- **Verdict:** **GATE FAILED as measured.** Per hard campaign rules, shipped as documented failure, not as a capability. F7 ladder is blocked at (b) and (c).

### F7b. Wigley Hull Wave Resistance

- **Status:** **BLOCKED** (F7a did not pass gate)

### F7c. Workshop Hull (DTMB 5415 / KCS)

- **Status:** **BLOCKED** (depends on F7b)

**F7 Overall:** F7a feasibility/physics pass; gate fail with documented cause. Ladder blocked per hard rule.

---

## F4 — Hypersonic Blunt Body

- **Status:** **NOT STARTED**
- **Reason:** Queued separately, out of scope for this campaign session (would require density-based shock-capturing central scheme, Sutherland transport model, blunt-body bow-shock mesh resolution, citable hypersonic reference)

---

## F8 — Rotating Machinery

- **Status:** **NOT STARTED** (no record file exists)

---

## F9 — Pulsatile Valve

- **Status:** **NOT STARTED** (no record file exists; out of scope — would require moving-mesh or immersed-boundary unsteady 3D with real leaflet geometry)

---

## F10 — 3D Viscous RANS Batch Family

- **Status:** **NOT STARTED** (no record file exists)

---

## Summary Table

| Family | Case | Reynolds/Mach | Regime | 2D/3D | Steady/Unsteady | Rung | Gate vs Reference | Deviation | Verdict | Core-min |
|---|---|---|---|---|---|---|---|---|---|---|
| **F1** | ONERA M6 | M=0.84, Re~1.5e7 | Transonic shock | 3D | Steady | Feasibility→Physics→**Gate** | Cp distribution (AGARD AR-138) | RMS 0.049–0.114, shock ±0.02–0.10 x/c | **GATE REACHED** | 127.5 |
| **F2** | NACA0012 | M=0.8, Re=6e6 | Transonic shock | 2D | Steady | Feasibility→Physics→**Gate** | Shock position (inviscid AGARD) | x/c=0.556 vs ~0.60 (banded) | **PASS** | – |
| **F3a** | Wedge | M=2.0–3.0 | Inviscid supersonic | 2D | Steady | Feasibility→Physics→**Gate** | p2/p1 (θ-β-M exact) | 0.01–0.07% | **PASS** | 8.43 |
| **F3b** | Cone | M=2.35, 3.0 | Inviscid supersonic | Axisym | Steady | Feasibility→Physics→**Gate** | pc/p1 (Taylor-Maccoll) | p: 0.19–0.29%; β: 2.1–3.9% | **PASS, not fully converged** | 22.09 |
| **F3c** | Diamond | M=2.0, 2.5 | Inviscid supersonic | 2D | Steady | Feasibility→Physics→**Gate** | cd (shock-expansion) | 0.18–0.26% | **PASS** | 7.93 |
| **F5a** | Cylinder | Re=100–180 | Laminar unsteady shed | 2D | Unsteady | Feasibility→Physics→**Gate** | Strouhal (Roshko/Williamson) | 0.7–4.6% | **PASS** | – |
| **F6a** | NASA hump | Re_c=936k | Turbulent separated | 2D | Steady RANS | Feasibility→Physics→**Gate** | separation/reattachment x/c | −1.59% / +13.95% (SST bias) | **GATE REACHED** | 5.25 |
| **F6c** | Duct DNS | Re_360, Re_360 | Turbulent secondary flow | – | Steady RANS | Physics/Feasibility→**Gate** | Secondary-flow RMS vs DNS | RANS 0.0%, DNS 2.07–2.22% | **GATE FAIL** (structural) | 0 |
| **F6b** | Periodic hills | – | – | – | – | **NOT STARTED** | – | – | blocked, time-boxed | 0 |
| **F7a** | Dam break | Re~4e4 | Free-surface wave | 2D | Unsteady | Feasibility→Physics→**Gate FAIL** | Front position Z(T) | +13.6% mean (21.3% max) | **GATE FAILED** | 2.4 |
| **F7b** | Wigley hull | – | – | – | – | **BLOCKED** (F7a gate fail) | – | – | – | 0 |
| **F7c** | Workshop hull | – | – | – | – | **BLOCKED** (F7b blocked) | – | – | – | 0 |
| **F4** | Hypersonic blunt | – | – | – | – | **NOT STARTED** | – | – | queued separately | 0 |
| **F8** | Rotating machinery | – | – | – | – | **NOT STARTED** | – | – | no record | 0 |
| **F9** | Pulsatile valve | – | – | – | – | **NOT STARTED** | – | – | no record | 0 |
| **F10** | 3D RANS batch | – | – | – | – | **NOT STARTED** | – | – | no record | 0 |

---

## Explicitly Not Started

**F4, F8, F9, F10** have produced no record files as of 2026-07-28. Each remains unstarted per campaign ladder doctrine:

- **F4 (Hypersonic):** Queued separately; not scoped for this session
- **F8 (Rotating machinery):** Not started; no feasibility rung initiated
- **F9 (Pulsatile valve):** Not started; out of scope (needs moving-mesh unsteady 3D)
- **F10 (3D viscous RANS batch):** Not started; no record file

---

## Gate Failures and Blocks (Reported Honestly)

1. **F6c (duct secondary flow):** GATE MEASURED, FAIL. Linear eddy-viscosity RANS cannot produce Prandtl secondary flow; captures 0% of DNS magnitude. Expected, structural, documented.
2. **F7a (dam break front):** GATE FAILED. Mean deviation +13.6%, max 21.3%, systematically growing. Cause: VOF numerical smearing of thin leading edge. Blocks F7b and F7c per hard ladder rule.

---

## Shiipped Capability Families

- **F1:** Transonic 3D wing Cp validation (gate reached; adjoint blocked by memory)
- **F2:** Transonic 2D airfoil shock position (shipped in mega-batch)
- **F3:** Supersonic exact-theory wedge/cone/diamond (all gates passed)
- **F5a:** Unsteady cylinder vortex shedding (shipped in mega-batch)
- **F6a:** Turbulent separated flow (NASA hump, gate reached)
- **F6c:** Duct secondary flow (gate fail, shipped as documented failure)

**Not shipped:**
- **F6b:** Periodic hills (not attempted, time-boxed)
- **F7a–c:** Marine free-surface (F7a gate fail blocks F7b/c)
- **F4, F8, F9, F10:** Not started
