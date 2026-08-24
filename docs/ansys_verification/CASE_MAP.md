# CASE_MAP — Ansys Fluid Dynamics Verification Manual (VM2026R1) → lab reproducibility map

**NOT FILED ANYWHERE. Nothing in this document leaves this box** (CLAUDE.md rules 7, 8).
The manual is proprietary Ansys documentation; the archives are Ansys project files
uploaded by Sanaa for this lab's private use.

**Zero compute.** This is a reading of the manual index and every case's Overview /
Test Case / Results-Comparison page — no solver was started to produce it.

- **Source (title-page verified by the supervisor):** *Ansys Fluid Dynamics
  Verification Manual*, ANSYS, Inc., Release 2026 R1, March 2026, 290 pp.
  Sidecar `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
  (6992 lines) checked against the PDF beside it.
- **Manual page** = the manual's own printed page number (from the Table of Contents,
  lines 66–169 of the sidecar), not the PDF page.
- **Archive home (D-6 ruling):** `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`
  (canonical, outside git). At the time of writing a haiku lane had already MOVED the
  set: the repo-root copy `VM2026R1_Fluids/` reads 0 files, the canonical home holds
  the archives. Both paths were inspected read-only; nothing was touched.
- **Lab solver** = OpenFOAM v2606 at `/usr/lib/openfoam/openfoam2606`. Applications
  confirmed present on this box were enumerated from
  `platforms/*/bin/`. `NONE` / `BLOCKED` is stated honestly where the box has no
  application for the physics.
- Drafted by `ansys-lane-opus48` (running as **claude-opus-4-8[1m]**) for the
  `ansys-verification-supervisor`, 2026-08-24. Draft for the supervisor's read; not a
  register and not a verdict.

---

## Legend

**Dimension** (manual §1.8 key): `2` = 2D · `3` = 3D · `A` = 2D axisymmetric.

**Reference type** (from the `Reference` line + Test-Case text):
- `AN` — analytical / closed-form or textbook correlation (exact target).
- `EXP` — experimental data (journal / conference measurements).
- `NUM` — other code / numerical benchmark (spectral, FEM, CFD reference solution).

**Quantity & N targets** — `discrete(N)` means the manual prints an N-row
Target/Ansys/Ratio table (gate-able against a number directly). `profile` means the
comparison is a plotted curve (figure) with no discrete target row — a lab PASS needs
a digitized profile or a scalar functional (peak, reattachment length, integral).

**Cost class** (order-of-magnitude, single grid level, CPU): `trivial` <5 core-min ·
`small` <60 · `medium` <600 · `large` ≥600. Multiply by ~3 for a full Roache triple.

**Ladder** — is a 3-level systematically-refined grid triple feasible for a Roache
`CONVERGING` verdict? `Y`/`N` + one-line reason. `Y*` = feasible but with a stated
caveat (wall-function y+ band, transient time-step coupling, or gate on a scalar
functional rather than a whole profile).

**Archive column** — `F` = Fluent `.wbpz` present in the canonical home · `+C` = CFX
`.def` archive also present · `Forte` = Forte archive present · `ABSENT` = no archive
for this case anywhere in the set.

**The index X-column headers could not be recovered** — in the PDF (§1.8, pp. 7–9) they
are rotated 90° and pdftotext extracts them as empty. Regime/physics below is taken
instead from each case's own `Physics/Models` line, which is authoritative.

---

## Table A — Ansys Fluent & CFX cases (VMFL001–078)

| Case | Pg | Title | Dim | Regime / physics (Physics-Models line) | Ref | Quantity & N targets | Lab solver (OpenFOAM v2606) | Arch | Cost | Ladder |
|---|---|---|---|---|---|---|---|---|---|---|
| VMFL001 | 15 | Flow between rotating & stationary concentric cylinders | 2 | Laminar, rotating wall | AN | Tangential velocity at r=20/25/30/35 mm — **discrete(4)** | simpleFoam / icoFoam (rotatingWallVelocity) | F+C | trivial | Y — structured annulus, monotone |
| VMFL002 | 17 | Laminar flow through pipe, uniform heat flux | A | Laminar + heat transfer (Mercury) | AN | Pressure drop + centreline outlet T — **discrete(2)** | simpleFoam + energy / buoyantSimpleFoam | F+C | trivial | Y — axisym wedge, monotone |
| VMFL003 | 19 | Pressure drop, turbulent pipe flow | A | Turbulent, standard k-ε | AN | Pressure drop — **discrete(1)** | simpleFoam (kEpsilon) | F+C | trivial | Y* — hold y+ band across levels |
| VMFL004 | 21 | Plain Couette flow with pressure gradient | 2 | Laminar, moving wall, periodic | AN | X-velocity profile at X=0.75 m — **profile** | pimpleFoam/simpleFoam (cyclic + pressureGradient) | F+C | trivial | Y* — gate on profile / centre value |
| VMFL005 | 25 | Poiseuille flow in a pipe | A | Steady laminar | AN | Pressure drop (Hagen-Poiseuille) — **discrete(1)** | icoFoam / simpleFoam | F+C | trivial | Y — axisym, exact analytic |
| VMFL006 | 27 | Multicomponent species transport in pipe flow | A | Laminar, species transport | AN | Mass fraction of species A along axis — **profile** | reactingFoam (inert) / scalarTransportFoam | F+C | small | Y* — gate on profile |
| VMFL007 | 29 | Non-Newtonian flow in a pipe | A | Laminar, power-law viscosity | AN | Pressure drop — **discrete(1)** | nonNewtonianIcoFoam (powerLaw) | F+C | trivial | Y — axisym, analytic |
| VMFL008 | 31 | Flow inside a rotating cavity | A | Laminar, rotating reference frame | NUM | Radial & swirl velocity at X=0.6 m — **profile** | SRFSimpleFoam | F+C | small | Y* — gate on profile |
| VMFL009 | 35 | Natural convection in concentric annulus | 2 | Natural convection, laminar, heat | EXP | Wall static-temperature distribution — **profile** | buoyantSimpleFoam / buoyantBoussinesqSimpleFoam | F+C | small | Y* — gate on profile |
| VMFL010 | 39 | Laminar flow in a 90° tee-junction | 2 | Laminar | NUM | Flow split (fractional flow) — **discrete(1)** | simpleFoam / icoFoam | F+C | trivial | Y — 2D, monotone |
| VMFL011 | 41 | Laminar flow in a triangular cavity | 2 | Laminar (driven) | NUM | Normalized X-velocity on bisector — **profile** | icoFoam / simpleFoam | F+C | small | Y* — gate on profile |
| VMFL012 | 45 | Turbulent flow in a wavy channel | 2 | Turbulent, separation, periodic | EXP | Normalized X-velocity at crest/trough — **profile** | simpleFoam/pimpleFoam (kEpsilon) | F+C | small | Y* — y+ band |
| VMFL013 | 51 | Turbulent flow + heat, backward-facing step | 2 | Incompressible turbulent, heat, reattachment | EXP | Local Nusselt number along heated wall — **profile** | rhoSimpleFoam / simpleFoam + energy | F+C | small | Y* — y+ band + profile |
| VMFL014 | 55 | Species mixing in co-axial turbulent jets | A | Multi-species, turbulent, jet mixing | EXP | Propane & X-velocity along jet axis — **profile** | reactingFoam (inert) / simpleFoam+scalarTransport | F+C | small | Y* — profile |
| VMFL015 | 61 | Flow through an engine inlet valve | 3 | 3D turbulent | EXP | Z-velocity at Z=−5/+10 mm — **profile** | simpleFoam (kEpsilon) | F+C | large | Y* — 3D, y+; costly |
| VMFL016 | 65 | Turbulent flow in a transition duct | 3 | 3D turbulent, Reynolds stress model | EXP | Pressure coefficient (station 5, centreline) — **profile** | simpleFoam (RSM: LRR/SSG) | F+C | large | Y* — 3D RSM; costly |
| VMFL017 | 69 | Transonic flow over an RAE 2822 airfoil | 2 | Compressible, turbulent | EXP | Drag & lift coefficient — **discrete(2)** | rhoSimpleFoam (SST) | F+C | small | Y* — y+ + shock capture |
| VMFL018 | 71 | Shock reflection in supersonic flow | 2 | Reflecting shocks, compressible turbulent | EXP | Afterbody static pressure & heat flux — **profile** | sonicFoam / rhoCentralFoam | F+C | small | Y* — shock capture |
| VMFL019 | 77 | Transient flow near a wall set in motion | 2 | Unsteady, moving wall (Stokes 1st problem) | AN | Near-wall velocity profile at outlet — **profile** | pimpleFoam / icoFoam (transient) | F+C | trivial | Y* — space+time refinement |
| VMFL020 | 79 | Adiabatic compression of air by a piston | 2 | Dynamic mesh, transient, ideal gas | AN | Static T & p vs time — **profile** | rhoPimpleFoam (dynamicMesh) | F+C | small | Y* — mesh-motion + time |
| VMFL021 | 85 | Cavitation over a sharp-edged orifice A (high p) | A | Turbulent multiphase, cavitation, phase change | EXP | Discharge coefficient — **discrete(1)** | **BLOCKED** — no cavitation solver (interPhaseChangeFoam absent) | F+C | — | N — no solver |
| VMFL022 | 87 | Cavitation over a sharp-edged orifice B (low p) | A | Turbulent multiphase, cavitation, phase change | EXP | Discharge coefficient — **discrete(1)** | **BLOCKED** — no cavitation solver | F | — | N — no solver |
| VMFL023 | 89 | Oscillating laminar flow around a circular cylinder | 2 | Laminar, transient (vortex shedding) | AN | Strouhal / drag (from table) — **discrete(1)** | pimpleFoam / icoFoam | F+C | small | Y* — time-accurate |
| VMFL024 | 91 | Interface of two immiscible liquids in rotating cylinder | A | Multiphase (VOF), transient, body force | EXP | Non-dim swirl velocity at 3 radii (t=80 s) — **discrete(3)** | interFoam (SRF/MRF) | F | small | Y* — VOF interface |
| VMFL025 | 93 | Turbulent non-premixed methane combustion, swirling air | A | Turbulent swirl, non-premixed combustion | EXP | Axial/swirl velocity, T, CO at X=40 mm — **profile** | reactingFoam (hard — combustion model) | F | medium | Y* — hard physics |
| VMFL026 | 99 | Supersonic real-gas flow inside a shock tube | 3 | Transient compressible, real gas, shock | NUM | Centreline static T & p — **profile** | sonicFoam/rhoCentralFoam (perfect-gas; **real-gas EOS BLOCKED**) | F+C | medium | Y* — perfect-gas only |
| VMFL027 | 103 | Turbulent flow over a backward-facing step | 2 | 2D turbulent, realizable k-ε | EXP | Skin-friction coefficient along wall — **profile** | simpleFoam (realizableKE) | F+C | small | Y* — y+ + reattachment |
| VMFL028 | 107 | Turbulent heat transfer in a pipe expansion | A | Heat transfer, turbulent, recirculation | EXP | Nusselt number along heated wall — **profile** | rhoSimpleFoam / simpleFoam + energy | F | small | Y* — y+ band |
| VMFL029 | 109 | Anisotropic conduction heat transfer | 2 | Heat conduction, anisotropic conductivity | AN | Normalized T at X=0.5 m — **profile** | laplacianFoam (isotropic only; **anisotropic tensor DT not native** → custom) | F | trivial | Y* — needs tensor diffusivity |
| VMFL030 | 111 | Turbulent flow in a 90° pipe-bend | 3 | 3D turbulent, RNG k-ε, non-equilibrium wall fns | EXP | Velocity magnitude at 75° along bend — **profile** | simpleFoam (RNGkEpsilon) | F | medium | Y* — 3D, half-domain, y+ |
| VMFL031 | 113 | Turbulent flow behind an open-slit V-gutter | 2 | Turbulent | EXP | X-velocity 22 mm downstream — **profile** | simpleFoam / pimpleFoam | F | small | Y* — profile |
| VMFL032 | 115 | Turbulent separated flow along axisymmetric afterbody | A | Turbulent, separation | EXP | Pressure & skin-friction along afterbody — **profile** | simpleFoam (kOmegaSST) | F+C | small | Y* — y+ + separation |
| VMFL033 | 119 | Viscous heating in an annulus | 2 | Viscous flow + heating, moving wall (dissipation) | AN | Velocity & temperature profiles — **profile** | rhoSimpleFoam / chtMultiRegion (viscous dissipation) | F | trivial | Y* — profile |
| VMFL034 | 121 | Particle aggregation inside a turbulent stirred tank | 2 | Multiphase, population balance, turbulent | AN | Moments m0–m5 of PBE — **discrete(6)** | reactingMultiphaseEulerFoam (PBM, hard) / **NONE (native PBM limited)** | F | medium | N — no clean PBM solver |
| VMFL035 | 123 | 3-D single-stage axial compressor | 3 | Compressible transonic, turbulent, moving ref frame | NUM | Stator-outlet pressure & mass-flow — **discrete(2)** | rhoSimpleFoam (MRF) | F | large | Y* — 3D turbomachinery; costly |
| VMFL036 | 125 | Laminar flow past a sphere | A | Laminar | NUM | Drag coefficient (Re≈50) — **discrete(1)** | simpleFoam (axisym) | F | small | Y — axisym, monotone (large far-field) |
| VMFL037 | 127 | Turbulent flow over a forward-facing step | 2 | SST, turbulent, separation/reattachment | EXP | Pressure coefficient along wall — **profile** | simpleFoam (kOmegaSST) | F+C | small | Y* — y+ band |
| VMFL038 | 131 | Falling film over an inclined plane | 2 | Laminar, free-surface (VOF) | AN | Velocity profile at outlet — **profile** | interFoam | F | small | Y* — VOF interface |
| VMFL039 | 133 | Boiling in a pipe with heated wall | A | Multiphase, phase change, RPI wall boiling | EXP | Temperature along pipe wall — **profile** | reactingTwoPhaseEulerFoam (wall boiling, hard) | F+C | medium | N* — RPI boiling hard/partial |
| VMFL040 | 137 | Separated turbulent flow in a diffuser | A | SST, adverse pressure gradient, separation | EXP | (profile) — **profile** | simpleFoam (kOmegaSST) | F+C | small | Y* — separation |
| VMFL041 | 141 | Transonic flow over an airfoil | 2 | Transonic, shock, SST | EXP | Pressure coefficient on airfoil — **profile** | rhoSimpleFoam (SST) | F | small | Y* — shock + y+ |
| VMFL042 | 143 | Turbulent mixing of two streams, different densities | 2 | SST, mixing layer, density diff, buoyancy | EXP | Salt-water mass fraction at x=10 m — **profile** | simpleFoam + energy / buoyantSimpleFoam | F+C | small | Y* — profile |
| VMFL043 | 147 | Laminar→turbulent transition of BL over flat plate | 2 | SST, transitional | EXP | Skin-friction coefficient on plate — **profile** | simpleFoam (kOmegaSSTLM transition) | F | small | Y* — transition model |
| VMFL044 | 149 | Supersonic nozzle flow | A | Compressible supersonic, SST | EXP | Pressure ratio along nozzle wall — **profile** | rhoSimpleFoam / sonicFoam | F+C | small | Y* — shock capture |
| VMFL045 | 153 | Oblique shock over an inclined ramp | 2 | Compressible supersonic, oblique shock | AN | Mach, T, density downstream — **discrete(3)** | rhoCentralFoam / sonicFoam | F+C | trivial | Y — inviscid, monotone |
| VMFL046 | 155 | Normal shock in a converging-diverging nozzle | 2 | Compressible supersonic, normal shock | AN | Mach along centreline (vs analytic) — **profile** | rhoCentralFoam / sonicFoam | F | small | Y* — shock capture |
| VMFL047 | 157 | Turbulent separated flow in an asymmetric diffuser | 2 | Turbulent separation, standard k-ω | EXP | X-velocity at X=24 (profile) — **profile** | simpleFoam (kOmega) | F+C | small | Y* — separation |
| VMFL048 | 159 | Turbulent flow in a 180° pipe bend | 3 | SST, turbulent, separation/reattachment | EXP | Axial velocity at a section — **profile** | simpleFoam (kOmegaSST) | F | medium | Y* — 3D, y+ |
| VMFL049 | 161 | Combustion in axisymmetric natural-gas furnace | A | Turbulent non-premixed combustion, EDM, k-ε | EXP | Mole fraction of CH4 along axis — **profile** | reactingFoam (EDM, hard) | F | medium | Y* — hard physics |
| VMFL050 | 163 | Transient heat conduction in a semi-infinite slab | 2 | Transient heat transfer, conduction | AN | Wall T & T at 150 mm, t=120 s — **discrete(2)** | laplacianFoam | F | trivial | Y* — space + time refinement |
| VMFL051 | 165 | Isentropic expansion over a convex corner | 2 | Compressible inviscid (Prandtl-Meyer) | AN | Mach after expansion — **discrete(1)** | rhoCentralFoam / sonicFoam | F+C | trivial | Y — inviscid, monotone |
| VMFL052 | 167 | Turbulent natural convection inside a tall cavity | 2 | Turbulent, buoyancy, Boussinesq | EXP | Vertical velocity at Y/h — **profile** | buoyantBoussinesqSimpleFoam / buoyantSimpleFoam | F+C | small | Y* — y+ + buoyancy |
| VMFL053 | 171 | Compressible turbulent mixing layer | 2 | RNG k-ε, compressible, energy | EXP | (profile) — **profile** | rhoSimpleFoam (RNGkEpsilon) | F | small | Y* — profile |
| VMFL054 | 173 | Laminar flow in a trapezoidal cavity | 2 | Viscous, driven by moving walls | NUM | X-velocity (profile) — **profile** | icoFoam / simpleFoam | F+C | small | Y* — gate on profile |
| VMFL055 | 177 | Transitional recirculatory flow in ventilation enclosure | 2 | Transitional (k-kl model) | EXP | X-velocity at Y=2 — **profile** | simpleFoam (kkLOmega) | F | small | Y* — transition model |
| VMFL056 | 179 | Combined conduction & radiation in a square cavity | 2 | Radiation (discrete-ordinate), conduction | NUM | Non-dim T at X=0 — **profile** | chtMultiRegionSimpleFoam + fvDOM | F | small | Y* — radiation model |
| VMFL057 | 181 | Radiation & conduction in composite solid layers | 2 | Radiation (DO), participating medium, conduction | NUM | (profile) — **profile** | chtMultiRegion + fvDOM | F | small | Y* — radiation model |
| VMFL058 | 183 | Turbulent flow in an axisymmetric diffuser | A | Turbulent, adverse pressure gradient | EXP | Pressure coefficient along diffuser — **profile** | simpleFoam (kOmegaSST) | F | small | Y* — separation |
| VMFL059 | 185 | Conduction in a composite solid block | 2 | Conduction with heat source | AN | Side-wall temperatures — **discrete(2)** | chtMultiRegionSimpleFoam / laplacianFoam | F+C | trivial | Y — pure conduction, monotone |
| VMFL060 | 187 | Transitional supersonic flow over rearward-facing step | 2 | Compressible, transitional (Transition SST) | EXP | Non-dim static pressure on stepped wall — **profile** | rhoSimpleFoam / sonicFoam (transition SST) | F | small | Y* — shock + transition |
| VMFL061 | 189 | Surface-to-surface radiation between two concentric cylinders | 2 | Radiation modeling (S2S) | AN | Temperature along radius — **profile** | chtMultiRegion + viewFactor (S2S) radiation | F | trivial | Y* — radiation only |
| VMFL062 | 191 | Fully developed turbulent flow over a "hill" | 2 | Low-Re k-ε turbulent | EXP | Skin-friction along wall — **profile** | simpleFoam (low-Re kEpsilon) | F | small | Y* — low-Re mesh |
| VMFL063 | 193 | Separated laminar flow over a blunt plate | 2 | Laminar, high-resolution schemes | EXP | Non-dim reattachment length (LR/2t) — **discrete(1)** | icoFoam / simpleFoam | F+C | small | Y — laminar, gate on LR |
| VMFL064 | 195 | Low-Re flow in a channel with sudden asymmetric expansion | 2 | Laminar, separation, reattachment | EXP | Non-dim reattachment length — **discrete(1)** | icoFoam / simpleFoam | F | small | Y — laminar, gate on LR |
| VMFL065 | 197 | Swirling turbulent flow inside a diffuser | A | Turbulent, swirl, Reynolds stress model | EXP | Swirl velocity at X=0 — **profile** | simpleFoam (RSM) | F | small | Y* — RSM, swirl |
| VMFL066 | 199 | Radiative heat transfer in enclosure, participating medium | 2 | Radiation (discrete-ordinate) | NUM | Non-dim heat flux along hot wall — **profile** | fireFoam / chtMultiRegion + fvDOM | F | small | Y* — radiation model |
| VMFL067 | 201 | Boiling in a pipe — critical heat flux | A | Multiphase, heat & mass transfer, boiling | NUM | Wall temperature — **profile** | reactingTwoPhaseEulerFoam (boiling, hard) | F | medium | N* — boiling hard/partial |
| VMFL068 | 203 | Axial flow in an eccentric annulus | 3 | Steady, periodic, turbulent, RSM | EXP | Normalized axial velocity at plane 2 — **profile** | simpleFoam (RSM) | **ABSENT** | medium | Y* — 3D RSM; **no archive** |
| VMFL069 | 205 | Two-phase Poiseuille flow | 3 | Steady, laminar, two-phase | NUM | Velocity profile (two-phase) — **profile** | interFoam (or viscosity-stratified simpleFoam) | F | small | Y* — 3D, laminar, interface fixed |
| VMFL070 | 207 | Radiation between two parallel surfaces | 2 | Heat transfer, radiation | AN | Normalized T (vs analytic) — **profile** | chtMultiRegion + fvDOM / viewFactor | F | trivial | Y* — radiation only |
| VMFL071 | 209 | Mid-span flow over a Goldman stator blade | 2 | Turbomachinery (transonic cascade) | EXP | Pressure ratio (vs experiment) — **profile** | rhoSimpleFoam (cascade) | F | small | Y* — transonic cascade |
| VMFL072 | 211 | Liquid water flow over flat plate under gravity | 3 | Eulerian wall film | EXP | Film thickness — **discrete(1)** | **NONE** — no Eulerian wall-film solver on box | F | small | N — no solver |
| VMFL073 | 213 | Turbulent separated flow in axisymmetric diffuser | A | Turbulence, separation | EXP | Skin-friction along diffuser wall — **profile** | simpleFoam (kOmegaSST) | F | small | Y* — separation |
| VMFL074 | 215 | Modeling of a plug-flow atomizer | 2 | Multiphase, population balance, turbulence | NUM | Number density of bin-2 fraction — **profile** | reactingParcelFoam / **NONE (native PBM limited)** | F | medium | N — no clean PBM solver |
| VMFL075 | 217 | Supersonic flow over a circular-arc bump | 2 | Inviscid, compressible, supersonic | NUM | Mach along lower wall (vs reference) — **profile** | rhoCentralFoam / sonicFoam | F | small | Y* — shock capture |
| VMFL076 | 219 | Forced convection over a flat plate | 2 | Laminar, convection (low Prandtl) | AN | Normalized T (vs analytic) — **profile** | simpleFoam + energy / rhoSimpleFoam | F | trivial | Y* — Blasius/low-Pr, profile |
| VMFL077 | 221 | Free-surface flow around a ship | 3 | Turbulent, free surface (VOF) | EXP | Water level on hull — **profile** | interFoam | F | large | Y* — 3D VOF; costly |
| VMFL078 | 223 | Polyhedral mesh accuracy (3D lid-driven cubic cavity, Re=1000) | 3 | Laminar, driven by moving wall | NUM | X-velocity on vertical centreline (symmetry plane) — **profile** | icoFoam / simpleFoam | F | medium | Y — structured hex triple, benchmark |

## Table B — Ansys Fluent GPU cases (VMFLGPU001–010)

The GPU cases are the **same physics as a Fluent parent**, re-run on the Fluent GPU
solver. The lab has **no GPU attached** (a GPU is a separate us-east-2 instance,
launched per run — CLAUDE.md rule 12); every GPU case runs on the **same OpenFOAM CPU
application** as its parent. **No GPU `.wbpz` archive exists in the set** (all ABSENT).

| Case | Pg | Title | Dim | Parent | Ref | Quantity & N targets | Lab solver | Arch | Cost | Ladder |
|---|---|---|---|---|---|---|---|---|---|---|
| VMFLGPU001 | 225 | Rotating & stationary concentric cylinders | 2 | VMFL001 | AN | Tangential velocity, 4 radii — **discrete(4)** | simpleFoam / icoFoam | ABSENT | trivial | Y |
| VMFLGPU002 | 227 | Laminar flow in a 90° tee-junction | 2 | VMFL010 | NUM | Flow split — **discrete(1)** | simpleFoam / icoFoam | ABSENT | trivial | Y |
| VMFLGPU003 | 229 | Laminar flow in a triangular cavity | 2 | VMFL011 | NUM | Normalized X-velocity on bisector — **profile** | icoFoam / simpleFoam | ABSENT | small | Y* |
| VMFLGPU004 | 233 | Anisotropic conduction heat transfer | 2 | VMFL029 | AN | Normalized T at X=0 — **profile** | laplacianFoam (anisotropic → custom) | ABSENT | trivial | Y* |
| VMFLGPU005 | 235 | Turbulent natural convection in a tall cavity | 2 | VMFL052 | EXP | Vertical velocity at Y/h — **profile** | buoyantBoussinesqSimpleFoam | ABSENT | small | Y* |
| VMFLGPU006 | 239 | Mid-span flow over a Goldman stator blade | 2 | VMFL071 | EXP | Pressure ratio (vs experiment) — **profile** | rhoSimpleFoam (cascade) | ABSENT | small | Y* |
| VMFLGPU007 | 243 | Turbulent flow + heat, backward-facing step | 2 | VMFL013 | EXP | Surface Nusselt number — **profile** | rhoSimpleFoam / simpleFoam + energy | ABSENT | small | Y* |
| VMFLGPU008 | 247 | Radiative heat transfer, participating medium | 2 | VMFL066 | NUM | Non-dim heat flux vs x* (vs analytic) — **profile** | chtMultiRegion + fvDOM | ABSENT | small | Y* |
| VMFLGPU009 | 249 | Two-phase Poiseuille flow | 3 | VMFL069 | NUM | Velocity magnitude vs position — **profile** | interFoam | ABSENT | small | Y* |
| VMFLGPU010 | 251 | Surface-to-surface radiation, concentric cylinders | 2 | VMFL061 | AN | Non-dim T vs normalized radius — **profile** | chtMultiRegion + viewFactor (S2S) | ABSENT | trivial | Y* |

## Table C — Ansys Forte cases (VMFRT001–007)

All are **Ansys Forte** engine / spray / combustion cases. The lab has **no Forte
solver and no engine-combustion CFD application** on the box; most are `NONE`. Forte
archives ARE present in the canonical home (`VMFRT_v261/`).

| Case | Pg | Title | Dim | Regime / physics | Ref | Quantity & N targets | Lab solver | Arch | Cost | Ladder |
|---|---|---|---|---|---|---|---|---|---|---|
| VMFRT001 | 255 | LES in an internal-combustion engine | 3 | LES, IC engine, reacting | EXP | (validation profiles) — **profile** | **NONE** — no LES engine-combustion solver | Forte | large | N — no solver |
| VMFRT002 | 259 | ECN nonreacting flow — bklraAL4 | 3 | Non-reacting spray, gas-phase | EXP | (spray/gas profiles) — **profile** | reactingParcelFoam (spray, no reaction) — partial / **NONE** | Forte | large | N* — engine spray hard |
| VMFRT003 | 261 | ECN nonreacting flow — bklfaAL4 | 3 | ECN non-reacting spray | EXP | (spray/gas profiles) — **profile** | reactingParcelFoam — partial / **NONE** | Forte | large | N* |
| VMFRT004 | 263 | ECN nonreacting flow — bkldaAL4 | 3 | ECN non-reacting spray | EXP | (spray/gas profiles) — **profile** | reactingParcelFoam — partial / **NONE** | Forte | large | N* |
| VMFRT005 | 265 | ECN reacting flow — jkldaAL4 | 3 | ECN reacting spray combustion | EXP | (combustion profiles) — **profile** | sprayFoam / reactingParcelFoam (hard) / **NONE** | Forte | large | N — no clean solver |
| VMFRT006 | 269 | Adiabatic compression of air by a reciprocating piston | 3 | Dynamic mesh, transient, ideal gas (no reaction) | AN | Static T & p vs crank angle — **profile/discrete** | rhoPimpleFoam (dynamicMesh) — **feasible** | Forte | small | Y* — mesh-motion + time |
| VMFRT007 | 273 | Small-bore direct-injection diesel engine | 3 | Engine combustion (light-duty diesel) | EXP | (engine profiles) — **profile** | **NONE** — no engine-combustion solver | Forte | large | N — no solver |

---

## 1. Counts

**By dimension (all 95 cases):**

| Dim | VMFL (78) | GPU (10) | RT (7) | Total |
|---|---|---|---|---|
| 2 (2D) | 45 | 9 | 0 | **54** |
| A (2D axisymmetric) | 22 | 0 | 0 | **22** |
| 3 (3D) | 11 | 1 | 7 | **19** |

**By reference type (all 95):** `AN` (analytical) = **26** · `EXP` (experimental) =
**50** · `NUM` (other code / numerical benchmark) = **19**.
- VMFL78: AN 22, EXP 41, NUM 15. · GPU10: AN 3, EXP 3, NUM 4. · RT7: AN 1, EXP 6.

**By regime (VMFL78 `Physics/Models` keyword flags — these overlap):**
- Turbulent (RANS: k-ε / k-ω / SST / RSM / RNG / k-kl): **38**
- Laminar (keyword): **17**
- Heat transfer / conduction / convection / radiation / thermal: **17**
  - of which radiation: **5** (VMFL056, 057, 061, 066, 070) · pure conduction: **3**
    (VMFL029, 050, 059)
- Compressible / supersonic / transonic / shock / inviscid: **13**
- Rotating / MRF / SRF / swirl / moving-wall: **12**
- Multiphase / two-phase / VOF / cavitation / boiling / free-surface / wall-film /
  population-balance: **10**
- Transient / unsteady / dynamic-mesh: **6**
- Species / combustion / reacting: **4**
- Transitional-turbulence: **3**

**Result-comparison form (VMFL78):** discrete Target/Ansys/Ratio tables exist for **21**
cases (001, 002, 003, 005, 007, 010, 017, 021, 022, 024, 034, 035, 036, 045, 050, 051,
059, 063, 064, 072 — plus 006 is a *tabulated profile*). The remaining ~57 compare via
plotted profiles (figures) only — a lab PASS on those needs a digitized profile or a
scalar functional.

**Lab-solver coverage (honest):** cases the box has **NO solver** for, or only a
`BLOCKED`/`NONE` path: **VMFL021, VMFL022** (cavitation — no `interPhaseChangeFoam`),
**VMFL034, VMFL074** (population-balance — no clean native PBM solver), **VMFL072**
(Eulerian wall film — no solver), and **VMFRT001, VMFRT002, VMFRT003, VMFRT004,
VMFRT005, VMFRT007** (Forte engine spray/combustion — no engine-combustion CFD app).
That is **11 cases with no usable lab solver.** A further band is *partial / hard*
(a solver exists but the physics is incomplete or difficult): VMFL025, VMFL049
(combustion via reactingFoam), VMFL026 (real-gas EOS unavailable — perfect-gas only),
VMFL029/GPU004 (anisotropic conduction needs a tensor diffusivity, not native to
laplacianFoam), VMFL039, VMFL067 (RPI wall boiling). Everything else maps to a
first-class OpenFOAM application.

**Archive presence:** Fluent `.wbpz` present for **77 of 78** VMFL cases — **VMFL068 is
the sole missing Fluent archive**. CFX `.def` present for the **37**-case CFX-supported
subset. Forte archives present for all **7** VMFRT. **All 10 VMFLGPU archives are
ABSENT** — no GPU project files were shipped in this set.

---

## 2. First tranche — cheap pipeline-proving cases (VMFL001 fixed as case 1)

Selection rule (from the brief): cheap, an existing lab solver reproduces it, prefer
**analytical** references and a **feasible 3-level ladder**, prefer a **discrete
target** so the gate is a number not a digitized curve. The supervisor has already
chosen **VMFL001** (concentric rotating cylinders, exact White solution) as case 1.
The next four, ranked, deliberately exercise **four different OpenFOAM solver
families** so passing them proves the whole pipeline end to end:

1. **VMFL005 — Poiseuille flow in a pipe** (p. 25, A, laminar, `AN`). Reference
   Hagen-Poiseuille is *exact*; one discrete target (ΔP = 10.24 Pa, Fluent ratio
   0.998); `icoFoam`/`simpleFoam`; trivial cost; axisymmetric wedge refines cleanly
   for a monotone triple. The canonical laminar pipeline test — **strongest #2.**
2. **VMFL003 — Pressure drop, turbulent pipe** (p. 19, A, k-ε, `AN`). One discrete
   target (ΔP = 21744 Pa, Fluent ratio 0.988) against the Moody/friction-factor
   analytic; `simpleFoam` + `kEpsilon`. Extends the pipeline to **turbulence** while
   the target stays a single scalar. Ladder feasible with the y+ band held across
   levels.
3. **VMFL007 — Non-Newtonian flow in a pipe** (p. 29, A, power-law, `AN`). One discrete
   target (ΔP = 60.52 kPa, Fluent ratio 0.998) against Schaum's analytic; exercises
   **`nonNewtonianIcoFoam` (powerLaw viscosity)** — a distinct solver/model — trivially
   cheap, monotone ladder.
4. **VMFL050 — Transient heat conduction in a semi-infinite slab** (p. 163, 2D,
   `AN`). Two discrete targets (wall T = 393 K, T at 150 mm = 318.4 K at t = 120 s)
   against the error-function analytic; exercises **`laplacianFoam`** and the
   **transient/conduction** path — a third solver family with an exact reference.
   Ladder feasible on space; note the transient case couples spatial and temporal
   refinement (refine Δt with Δx).

*Alternates if any of the above stalls:* **VMFL010** (2D laminar tee, discrete flow
split 0.887, `simpleFoam`, `NUM` reference), **VMFL036** (axisymmetric laminar sphere
drag, discrete Cd = 1.0895, `NUM`), **VMFL002** (adds the coupled energy equation —
2 targets, `AN`). VMFL004 (Couette) is analytical but its comparison is a *profile*, so
it is a weaker clean-gate candidate and is ranked below the discrete-target four.

Net: the tranche VMFL001→005→003→007→050 proves **icoFoam, simpleFoam(kEpsilon),
nonNewtonianIcoFoam, and laplacianFoam** all end to end, every one against an
analytical reference with a discrete numeric target and a feasible Roache triple.

## 3. Cheapest 3D cases to close the lab's 3D gap (second tranche)

The lab today has **no 3D case with a CONVERGING Roache triple and no 3D PASS against
experiment with a prereg on disk** (`docs/inventory/2026-08-24/LAB_INVENTORY.md`
§2, §7). The cheapest 3D cases with a feasible triple and an experimental **or**
analytical/benchmark reference, ranked:

1. **VMFL078 — 3D lid-driven cubic cavity, Re=1000** (p. 223, 3D, laminar, `NUM`).
   `icoFoam`/`simpleFoam`; a structured hex mesh refines uniformly for the cleanest
   possible 3D triple; the reference (Wang & Wan 2011 FEM benchmark) provides tabulated
   centreline velocities, so the profile reduces to gate-able values. Laminar and
   well-conditioned — **best first 3D.** (The manual runs it on a 279,894-cell
   polyhedral mesh to demonstrate poly accuracy; the lab would use hex.)
2. **VMFL030 — Turbulent flow in a 90° pipe-bend** (p. 111, 3D, RNG k-ε, `EXP`).
   `simpleFoam` (RNGkEpsilon), half-domain by symmetry, structured mesh ladder
   feasible; the Enayet 1982 LDA data is the experimental target (velocity magnitude at
   75° along the bend). Medium cost. **This is the case that most directly closes the
   "3D PASS vs experiment" gap.**
3. **VMFL069 — Two-phase Poiseuille flow** (p. 205, 3D, laminar, `NUM`). `interFoam`
   (interface undeformed — can even be a viscosity-stratified single fluid); analytical/
   FEM reference (Marchandise 2006); laminar and cheap. A lower-risk 3D alternate that
   also feeds VMFLGPU009.

*Heavier 3D options (deferred):* VMFL048 (180° bend, turbulent, EXP), VMFL016
(transition duct, RSM, EXP), VMFL068 (eccentric annulus, RSM, EXP — **but its archive
is ABSENT**), VMFL035/077 (compressor / ship — large). **Caveat for the whole 3D
tranche:** VMFL078/030/069 all compare via *profile plots*, not discrete tables, so
each needs a digitized profile or an agreed scalar functional pinned in the
pre-registration before compute.

---

## 4. Candidate numerics facts for the lab to record (draft N-AV rows — do NOT edit NUMERICS_KNOWLEDGE.md)

Drafted as bullets for the supervisor's read; each cites the manual page.

- **N-AV (Ansys' own accuracy target):** the manual states its goal is *"results
  accuracy within 3% of the target solution"* and reports target and Ansys values to a
  *"consistent number of significant digits"* (§1.3, p. 5; §1.2, p. 4). This is the
  natural default band for a lab reproduction gate on these cases — a lab tolerance
  tighter than 3% would be stricter than Ansys' own stated goal.
- **N-AV (single-instance, not grid-independent):** Ansys explicitly warns these are
  *"single instance simulations using one mesh, one turbulence model, and one
  scenario"* and are *"not validation cases"*; where results are not grid-independent
  it is *"due to the need to limit run time"* (§1.2, p. 4; §1.4, p. 5). Consequence for
  us: **the lab's Roache triple is doing something the manual does not** — the manual
  reports a single grid, so a lab CONVERGING triple is genuinely new information, not a
  reproduction of an Ansys result.
- **N-AV (machine-dependent digits):** the manual notes non-linear/iterative solutions
  *"are among the most likely to exhibit machine-dependent numerical differences"* and
  that a value printed as 0.01234 may appear as 0.012335271 elsewhere (§1.2, pp. 4–5).
  A lab gate should compare at the manual's reported precision, not to spurious extra
  digits.
- **N-AV (ratios far from 1.000 — where even Ansys' own codes disagree):** worth
  recording as the realistic reproduction envelope:
  - **VMFL001** (p. 15): Fluent tangential-velocity ratios fall to **0.978** at r=35 mm
    and CFX to **0.976** — the outermost radius is the hardest point (both codes lose
    ~2–2.5%); Fluent CFX also split (0.991/0.998/0.988/0.976).
  - **VMFL017** RAE 2822 (p. 69): Fluent **drag ratio 0.952**, CFX **lift ratio 0.934**
    — a transonic airfoil is ~5–7% off even for Ansys; a demanding reproduction target.
  - **VMFL035** compressor (p. 123): Fluent **mass-flow ratio 1.026**.
  - **VMFL045** oblique shock (p. 153): Fluent **Mach ratio 1.015, density 0.981**.
  - **VMFL063/064** reattachment length (pp. 193/195): ratios **1.04 / 0.982** — a
    length-scale functional is intrinsically noisier than a point value.
  - **VMFL007** CFX (p. 29): **1.0165**; **VMFL005** CFX **1.024** — the CFX column is
    routinely looser than Fluent on the same case.
- **N-AV (turbulence-model inventory used by Ansys):** across VMFL78 the manual uses
  standard/realizable/RNG **k-ε**, standard **k-ω** and **SST**, **Reynolds-stress
  (RSM)**, and transition models **k-kl** and **Transition SST** — the lab must match
  the *stated model per case* (§1.2's single-model warning), not substitute a default.
- **N-AV (index / page anomaly to flag):** the §1.8 index table (PDF pp. 7–9) lists
  **VMFL036 at "p. 141"**, but the Table of Contents and the case body place VMFL036 at
  **p. 125** (p. 141 is VMFL041). Use the TOC page; the index cell is a manual typo.
  Also the index table's **X-column physics headers are rotated text and are not
  machine-extractable** — regime must be read from each case's `Physics/Models` line.
- **N-AV (mesh statement worth capturing):** VMFL078 discloses its mesh size
  (**279,894 polyhedral cells**, p. 223) — a rare explicit cell count, useful as the
  order-of-magnitude anchor for the lab's 3D lid-cavity ladder sizing.
