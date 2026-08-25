# DRAFT PRE-REGISTRATIONS — the ten VMFLGPU cases

**DRAFT, `ansys-lane-opus48` for `ansys-verification-supervisor`, 2026-08-25. NOT
FROZEN. Frozen only when Sanaa approves; each block is marked `DRAFT` and no sha is
registered.** Zero compute; no run directory exists for any case at 2026-08-25T20:28Z.

**These follow the team's template-speed 10-line form (`PREREG_TEMPLATE.md`, with its
Amendments 1–3) PLUS a family-specific GPU-path gate.** Reference-KIND → tier-ceiling
mapping (template Amendment 1): closed-form/exact or code-to-code ⇒ ceiling **GATE
REACHED**; measured/experimental ⇒ can reach **HOLDS**.

---

## THE GPU-SOLVER-PATH GATE — common to all ten (Sanaa's ruling, 2026-08-25)

The object under verification is **the lab's GPU solver path** (OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA, `sm_89`; `GPU_BUILD_RECIPE.md` §0). Each case therefore has a
**three-limb gate**, and a miss on limb A is `NOT A RESULT` regardless of the physics:

- **Limb A — GPU EXECUTION (binary, non-negotiable).** The three tells of
  `smoke_test_gpu_path.sh` must fire in the case's own run record: PETSc `-log_view` GPU
  flops > 0 for `KSPSolve`; the solver PID holds non-zero device memory during the solve
  (`nvidia-smi`); the active PETSc matrix type is `*aijcusparse`. **If limb A fails, the
  linear solve did not run on the GPU — the number is a CPU number and the case is `NOT A
  RESULT`.** A CPU number that happens to match the reference verifies nothing about the
  GPU path.
- **Limb B — GPU≡CPU CONSISTENCY (the heart of the verification).** The GPU result must
  equal the lab's OWN CPU result for the identical discretisation:
  `|q_GPU − q_CPU| / |q_CPU| ≤ tol_consistency` (default **1e-4**, i.e. the linear-solver
  relative tolerance — the two paths differ only in where the same linear system is
  solved, so they must agree to solver tolerance). This isolates the GPU linear-algebra
  path as the thing under test. A CPU baseline run is part of each case.
- **Limb C — PHYSICS (the reference gate, same as the CPU parent).**
  `|q_GPU − q_ref| / |q_ref| ≤ tol_phys`. Limb C alone is the parent physics; limbs A+B
  are what make it a GPU-path verdict.

**Controls (all ten, non-droppable):** planted-zero in the comparator (rule 3);
strict completion + age guard (rule 4); Roache triple where a triple is run (rule 5);
launcher freeze check of prereg + comparator against HEAD (template Amendment 2);
cap enforcement in the executable path (template Amendment 3); **no `set -u`** (v2606
bashrc hazard). Cost in GPU-hours per `COST_BASIS.md` ($0.8048/GPU-h published-list,
console still owed), each case its own cap as a RUNAWAY GUARD.

**Setup honesty flag per case:** `TEMPLATE-SPEED` where the manual prints a discrete
gate-able number and the lab solver runs the physics directly; `LIKELY BESPOKE` where the
gate quantity is a digitized profile, or where the lab solver needs non-trivial setup
(anisotropic tensor conductivity, DO radiation, S2S view factors) — those need a bespoke
frozen document, not this form, and the block below is a starting draft only.

---

### DRAFT — VMFLGPU001 — Flow Between Rotating and Stationary Concentric Cylinders
```
1. CASE      : VMFLGPU001 — manual p.225. CPU PARENT: VMFL001. Solver: icoFoam/simpleFoam
               + petsc4Foam (GPU). NOT YET RUN; run dir absent 2026-08-25T20:28Z.
2. REFERENCE : tangential velocity v_theta = 0.0151/0.0105/0.0072/0.0046 m/s at
               r=20/25/30/35 mm (White, Viscous Fluid Flow §3-2.3, analytical Couette).
               Ansys Fluent GPU = 0.0152/0.0105/0.0072/0.0045 (CONTEXT ONLY).
3. REF KIND  : closed-form/exact (analytical annular Couette) -> buys V.
4. CEILING   : GATE REACHED (closed-form buys V, never P).
5. QUANTITY  : v_theta on a radial line at the four manual radii [m/s]. Discrete(4).
6. GATE      : A GPU-exec (3 tells) ; B |v_GPU-v_CPU|/|v_CPU|<=1e-4 at all 4 r ;
               C |v_GPU-v_ref|/|v_ref|<=0.03 at all 4 r (manual's 3% goal + 2 s.f. rounding).
7. LADDER    : icoFoam (laminar), rho=1, mu=2e-4; 180-deg section; birth-certified mesh.
8. SEED      : r=2 triple (annulus radial x azimuthal); serial. GPU + matched CPU baseline.
9. RISK      : the r=35mm target (0.0046, 2 s.f.) has ~2% rounding alone -> C-limb at r=35
               is rounding-dominated; carry it, do not read the ratio as physics.
10. ORDER    : p_f=2; expect p_obs~2; >2.3 SUSPICIOUS.
11. WEDGE    : if run as a wedge, carry sin(t)/t (N-AV9); a 180-deg planar section avoids it.
12. COST     : ~0.1-0.3 GPU-h (trivial 2D). $0.08-$0.24 derived @ $0.8048. Cap 1 GPU-h (guard).
13. SETUP    : TEMPLATE-SPEED. This is the smoke case; its frozen comparator still grades.
```

### DRAFT — VMFLGPU002 — Laminar Flow in a 90 deg Tee-Junction
```
1. CASE      : VMFLGPU002 — p.227. CPU PARENT: VMFL010. Solver: simpleFoam + petsc4Foam.
               NOT YET RUN; run dir absent 2026-08-25T20:28Z.
2. REFERENCE : flow split (upper branch fraction) = 0.887 (Hayes/Nandkumar/Nasr-El-Din
               1989, a NUMERICAL benchmark). Ansys Fluent GPU = 0.884 (CONTEXT ONLY).
3. REF KIND  : code-to-code / numerical benchmark -> buys NEITHER V nor P.
4. CEILING   : GATE REACHED (a benchmark reference cannot exceed GATE REACHED).
5. QUANTITY  : fractional flow in the upper branch = Q_upper/Q_inlet [-]. Discrete(1).
6. GATE      : A GPU-exec ; B |split_GPU-split_CPU|/|split_CPU|<=1e-4 ;
               C |split_GPU-0.887|/0.887 <= 0.02 (benchmark, tighter 2% since 3 s.f.).
7. LADDER    : simpleFoam (laminar, incompressible), rho=1, mu=3.333e-3; developed inlet
               profile; two exits at equal static pressure; birth-certified mesh.
8. SEED      : r=2 triple; serial. GPU + matched CPU baseline.
9. RISK      : the split depends on outlet BC symmetry; an unequal numerical exit pressure
               biases the split -> assert both exits at identical p before grading.
10. ORDER    : p_f=2; expect p_obs~2.
11. WEDGE    : N/A (2D planar).
12. COST     : ~0.2-0.4 GPU-h. $0.16-$0.32 derived. Cap 1 GPU-h (guard).
13. SETUP    : TEMPLATE-SPEED (discrete gate number). NOTE line 3: benchmark, not exact.
```

### DRAFT — VMFLGPU003 — Laminar Flow in a Triangular Cavity
```
1. CASE      : VMFLGPU003 — p.229. CPU PARENT: VMFL011. Solver: icoFoam/simpleFoam + petsc4Foam.
               NOT YET RUN; run dir absent 2026-08-25T20:28Z.
2. REFERENCE : normalized X-velocity profile along the vertical line bisecting the base
               (Jyotsna & Vanka 1995, multigrid NUMERICAL benchmark). Ansys = figure only.
3. REF KIND  : code-to-code / numerical benchmark -> buys NEITHER.
4. CEILING   : GATE REACHED.
5. QUANTITY  : u_x / U_wall along the bisector -> gate on a NAMED SCALAR from the profile
               (e.g. the profile's minimum u_x/U_wall and its y-location). Profile.
6. GATE      : A GPU-exec ; B |q_GPU-q_CPU|/|q_CPU|<=1e-4 ; C profile-scalar within the
               band set at freeze from the digitized benchmark (Jyotsna&Vanka Fig).
7. LADDER    : lid-driven triangular cavity, U_wall=2 m/s, rho=1, mu=0.01; hybrid tet/hex
               mesh (manual); birth-certified.
8. SEED      : r=2 triple; serial. GPU + matched CPU baseline.
9. RISK      : the benchmark is a FIGURE, not a table -> the digitization band, not the
               physics, may dominate C; freeze the band from the digitized curve, not a run.
10. ORDER    : p_f=2.
11. WEDGE    : N/A.
12. COST     : ~0.3-0.6 GPU-h. Cap 1.5 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE (profile gate + figure digitization). Draft only.
```

### DRAFT — VMFLGPU004 — Anisotropic Conduction Heat Transfer
```
1. CASE      : VMFLGPU004 — p.233. CPU PARENT: VMFL029. Solver: chtMultiRegion solid /
               custom anisotropic-conduction solver + petsc4Foam. NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : normalized temperature distribution at X=0.5 m; ANALYTICAL solution for
               anisotropic-conductivity conduction (manual states analytical comparison).
3. REF KIND  : closed-form/exact (analytical) -> buys V.
4. CEILING   : GATE REACHED (closed-form buys V, never P).
5. QUANTITY  : T*(y) at X=0.5 m -> gate on a named scalar (e.g. T* at the mid-height probe)
               and/or the L2 profile error. Profile.
6. GATE      : A GPU-exec ; B |T_GPU-T_CPU|/|T_CPU|<=1e-4 ; C |T*_GPU-T*_analytic| band
               set at freeze.
7. LADDER    : anisotropic solid conductivity as a TENSOR (matrix components, manual);
               two walls at 100 K / 200 K; profile BC on the other two; birth-certified mesh.
8. SEED      : r=2 triple; serial. GPU + matched CPU baseline.
9. RISK      : standard laplacianFoam is ISOTROPIC scalar DT -> the anisotropic tensor
               conductivity needs a solver that carries it; a wrong tensor mapping gives a
               plausible-but-wrong field. Verify the tensor against the analytic axes first.
10. ORDER    : p_f=2.
11. WEDGE    : N/A (1m x 1m Cartesian).
12. COST     : ~0.1-0.3 GPU-h. Cap 1 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE (anisotropic tensor conductivity is non-standard). Draft only.
```

### DRAFT — VMFLGPU005 — Turbulent Natural Convection Inside a Tall Cavity
```
1. CASE      : VMFLGPU005 — p.235. CPU PARENT: VMFL052. Solver: buoyantBoussinesqSimpleFoam
               + petsc4Foam. NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : vertical velocity and temperature at Y/h=0.05 (Betts & Bokhari 2000,
               EXPERIMENTAL). Ansys = figures only.
3. REF KIND  : measured/experimental -> CAN buy P.
4. CEILING   : HOLDS (experimental reference; a met band is a validation credential) —
               BUT for the GPU family the credential is about the GPU PATH reproducing it.
5. QUANTITY  : v_y(x) and T(x) at Y/h=0.05 -> named scalars (peak v_y; near-wall dT). Profile.
6. GATE      : A GPU-exec ; B |q_GPU-q_CPU|/|q_CPU|<=1e-4 ; C profile-scalar band from
               Betts&Bokhari data, set at freeze; carry experimental scatter in the band.
7. LADDER    : Boussinesq, cavity L=2.18 m x W=0.0762 m (L/W=28.6), hot 307.85 K / cold
               288.25 K, adiabatic top/bottom; turbulence model per parent VMFL052;
               birth-certified mesh with y+ resolved to the model's wall treatment.
8. SEED      : r=2 triple; possibly parallel (cap uses RANKS). GPU + matched CPU baseline.
9. RISK      : turbulent buoyant cavity is stiff; the Poisson solve may converge poorly on
               cuSPARSE CG -> the AmgX escalation (GPU_BUILD_RECIPE §2) may be needed; a
               different linear-solver tolerance would break limb B, so FIX tolerances equal
               between GPU and CPU baseline.
10. ORDER    : p_f=2 nominal; turbulence closure caps observed order.
11. WEDGE    : N/A.
12. COST     : ~0.5-2 GPU-h (turbulent, iterative). Cap 4 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE (turbulent, experimental profile, stiff Poisson). Draft only.
```

### DRAFT — VMFLGPU006 — Mid-Span Flow Over a Goldman Stator Blade
```
1. CASE      : VMFLGPU006 — p.239. CPU PARENT: VMFL071. Solver: rhoSimpleFoam (compressible
               cascade) + petsc4Foam. NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : blade surface pressure ratio vs experiment (Goldman & McLallin, NASA TM
               X-3224, 1977, EXPERIMENTAL). Ansys = figure only.
3. REF KIND  : measured/experimental -> CAN buy P.
4. CEILING   : HOLDS (experimental).
5. QUANTITY  : p/p0 along the blade surface -> named scalar (e.g. min p/p0 on suction side).
               Profile.
6. GATE      : A GPU-exec ; B |q_GPU-q_CPU|/|q_CPU|<=1e-4 ; C band from Goldman data at freeze.
7. LADDER    : air (ideal gas), inlet 71.75 m/s (M~0.2 subsonic), Re_chord=5e5 (turbulent);
               translational periodic top/bottom (mid-span); birth-certified cascade mesh.
8. SEED      : r=2 triple; parallel likely. GPU + matched CPU baseline.
9. RISK      : compressible cascade with periodic BCs; a small inlet-angle or periodic-map
               error moves the whole p/p0 curve -> verify periodicity and inlet angle before
               grading. Note the manual's Test-Case text for GPU006 is COPIED from GPU007
               (both say "Goldman stator blade... backward-facing step"): trust the geometry
               table, not the prose.
10. ORDER    : p_f<=2; compressible cases showed SUSPICIOUSLY-HIGH observed order (team scar).
11. WEDGE    : N/A (2.5D mid-span).
12. COST     : ~0.5-2 GPU-h. Cap 4 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE (compressible turbomachinery, periodic). Draft only.
```

### DRAFT — VMFLGPU007 — Turbulent Flow with Heat Transfer in a Backward-Facing Step
```
1. CASE      : VMFLGPU007 — p.243. CPU PARENT: VMFL013. Solver: simpleFoam+energy /
               rhoSimpleFoam + petsc4Foam. NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : surface Nusselt number downstream of the step vs experiment (Vogel & Eaton
               1985, EXPERIMENTAL). Ansys = figure only.
3. REF KIND  : measured/experimental -> CAN buy P.
4. CEILING   : HOLDS (experimental).
5. QUANTITY  : Nu(x) on the heated wall -> named scalar (peak Nu and its x/H = reattachment
               proxy). Profile.
6. GATE      : A GPU-exec ; B |q_GPU-q_CPU|/|q_CPU|<=1e-4 ; C band from Vogel&Eaton at freeze.
7. LADDER    : Re_H=28,000, standard k-epsilon + standard wall functions, q''=1000 W/m2,
               developed inlet (U,k,epsilon), incoming BL thickness 1.1H; birth-certified mesh.
8. SEED      : r=2 triple; parallel likely. GPU + matched CPU baseline.
9. RISK      : reattachment length is the classic k-epsilon under-prediction; the peak-Nu
               LOCATION is model-level, not GPU-path -> limb C may miss on MODEL, not GPU.
               Report limb C miss as MODEL if GPU==CPU (limb B holds): the GPU path is still
               VERIFIED even when the physics band is missed, since B is the object under test.
10. ORDER    : p_f<=2; turbulence caps observed order.
11. WEDGE    : N/A.
12. COST     : ~0.5-2 GPU-h. Cap 4 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE (turbulent thermal, experimental profile). Draft only.
```

### DRAFT — VMFLGPU008 — Radiative Heat Transfer in a Rectangular Enclosure, Participating Medium
```
1. CASE      : VMFLGPU008 — p.247. CPU PARENT: VMFL066. Solver: fvDOM (+ energy) + petsc4Foam.
               NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : non-dimensional wall heat flux vs x* compared to the ANALYTIC solution
               (Raithby & Chui 1990 method; manual compares to analytic). sigma_s*Ly=1.
3. REF KIND  : closed-form/exact (analytic) -> buys V.
4. CEILING   : GATE REACHED (analytic buys V).
5. QUANTITY  : q*(x*) on the hot wall -> named scalar (q* at x*=0.5). Profile.
6. GATE      : A GPU-exec ; B |q_GPU-q_CPU|/|q_CPU|<=1e-4 ; C |q*_GPU-q*_analytic| band at freeze.
7. LADDER    : discrete-ordinates (fvDOM), isotropic scattering sigma_s=0.5/m, radiative
               equilibrium, hot wall 200 K / three cold walls 100 K, 10x2x0.5 m (L/W=5);
               birth-certified mesh + angular discretization declared.
8. SEED      : r=2 triple (spatial); ALSO angular-resolution convergence declared. GPU+CPU.
9. RISK      : fvDOM's ANGULAR sweep is NOT a linear system petsc4Foam offloads the same
               way as the energy Poisson -> the GPU path covers the ENERGY/flow linear solves,
               NOT the DO angular solve. STATE this in the verdict: limb A/B pertain to the
               offloaded solves; the DO sweep runs on CPU. This case's GPU-path coverage is
               PARTIAL and must be labelled so. Strong candidate to DEFER within the family.
10. ORDER    : p_f=1 (DO is ~1st order in angle); expect low p_obs.
11. WEDGE    : N/A.
12. COST     : ~0.5-2 GPU-h. Cap 4 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE + PARTIAL GPU COVERAGE (DO angular sweep on CPU). Draft only.
```

### DRAFT — VMFLGPU009 — Two-Phase Poiseuille Flow
```
1. CASE      : VMFLGPU009 — p.249. CPU PARENT: VMFL069. Solver: interFoam (two-phase) +
               petsc4Foam. NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : velocity magnitude vs position across a stratified two-fluid channel
               (Marchandise & Remacle 2006, NUMERICAL benchmark; a two-layer Poiseuille
               profile that also has a closed form).
3. REF KIND  : code-to-code / numerical benchmark (closed form exists) -> record as NUM,
               buys NEITHER unless the closed form is adopted at freeze (then V).
4. CEILING   : GATE REACHED.
5. QUANTITY  : |U|(y) across the channel -> named scalar (interface-plane velocity and the
               two-layer slope ratio). Profile.
6. GATE      : A GPU-exec ; B |U_GPU-U_CPU|/|U_CPU|<=1e-4 ; C band at freeze (from the closed
               form if adopted, else the benchmark curve).
7. LADDER    : two fluids, SAME density, kinematic visc 0.1 / 0.02, interface at mid-height,
               periodic with dp/dx=-0.5 Pa/m, interface NOT deformed (manual); domain 2x4 m;
               birth-certified mesh. (CASE_MAP marks 3D; the manual domain reads 2D — resolve
               at freeze from the archive.)
8. SEED      : r=2 triple; GPU + matched CPU baseline.
9. RISK      : interFoam solves a phase-fraction (alpha) transport AND pressure; the alpha
               solve (MULES) is not the petsc-offloaded Poisson -> like GPU008, GPU coverage
               is PARTIAL (pressure on GPU, alpha on CPU). Label it. A fixed non-deforming
               interface simplifies alpha but the coverage caveat stands.
10. ORDER    : p_f=2 for the momentum; alpha scheme caps it.
11. WEDGE    : N/A.
12. COST     : ~0.5-2 GPU-h. Cap 4 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE + PARTIAL GPU COVERAGE (alpha on CPU). Draft only.
```

### DRAFT — VMFLGPU010 — Surface-to-Surface Radiation Between Two Concentric Cylinders
```
1. CASE      : VMFLGPU010 — p.251. CPU PARENT: VMFL061. Solver: chtMultiRegion/energy +
               S2S viewFactor + petsc4Foam. NOT YET RUN 2026-08-25T20:28Z.
2. REFERENCE : non-dimensional temperature vs normalized radius; ANALYTICAL S2S radiation
               exchange (Incropera & DeWitt, Fundamentals of Heat & Mass Transfer 4e).
3. REF KIND  : closed-form/exact (analytical view-factor exchange) -> buys V.
4. CEILING   : GATE REACHED (analytic buys V).
5. QUANTITY  : T*(r/r_out) between the cylinders -> named scalar (T* at the mid-gap radius).
               Profile.
6. GATE      : A GPU-exec ; B |T_GPU-T_CPU|/|T_CPU|<=1e-4 ; C |T*_GPU-T*_analytic| band at freeze.
7. LADDER    : NO flow, energy only; S2S radiation; r_in=0.0178 m at 700 K, r_out=0.04625 m
               at 300 K; symmetry sector modeled; birth-certified mesh + view-factor set.
8. SEED      : r=2 triple; GPU + matched CPU baseline.
9. RISK      : S2S view factors are a PREPROCESSING computation (geometric), not a linear
               solve -> the GPU path covers only the energy solve, which for a NO-FLOW pure-
               radiation case is a small part of the work. GPU-path coverage is THIN here;
               strong DEFER candidate within the family. Label coverage honestly.
10. ORDER    : p_f=2 (energy diffusion); radiation exchange is algebraic.
11. WEDGE    : N/A (symmetry sector, not an axisymmetric wedge with sin(t)/t).
12. COST     : ~0.1-0.3 GPU-h. Cap 1 GPU-h (guard).
13. SETUP    : LIKELY BESPOKE + THIN GPU COVERAGE (view factors + energy-only). Draft only.
```

---

## Honest family-level note for the supervisor

- **Genuinely template-speed:** VMFLGPU001, VMFLGPU002 (discrete gate numbers, direct
  lab solvers). These are the first two to freeze if the family proceeds.
- **Bespoke (profile gates and/or non-standard physics):** VMFLGPU003–007.
- **Partial/thin GPU coverage — flag before committing GPU-hours:** VMFLGPU008 (DO
  angular sweep on CPU), VMFLGPU009 (alpha/MULES on CPU), VMFLGPU010 (view factors +
  energy-only). For these the petsc4Foam route offloads only part of the work, so the
  "GPU solver path verified" claim is **partial** and must say so. They are honest
  DEFER candidates within the family; running them still verifies the offloaded solves,
  but the verdict must not overclaim.
- **Limb B is what makes every one a GPU-path verdict**, independent of whether the
  physics band (limb C) is met — a GPU result that equals the lab's CPU result to solver
  tolerance verifies the GPU linear-algebra path even where the shared physics misses the
  reference on a MODEL limb (e.g. k-epsilon reattachment in VMFLGPU007).
- **All bands (`tol_phys`, the profile-scalar bands) are DRAFT and MUST be frozen from the
  manual's 3% goal + target rounding + the finest grid at approval — NEVER from a first
  run** (rule 2). No band above is committed.
