# FOUR NEW CASE FAMILIES — SETUP AND RUN INSTRUCTIONS
[SANAA-DIRECT — capture verbatim. Standing doctrine applies to all four:
staging (feasibility -> physics -> gate), pre-registration frozen before
any gated solve (10-line template), 3-level mesh ladder with observed order
+ GCI, deterministic decomposition, rc captured in the wrapper, STATUS at
exit, absolute solution/continuity bounds beside every residual criterion,
heat-balance closure on every thermal solve, planted-control comparators
proven through the real code path before grading, artifacts preserved.
Every theory gate below: the team pulls the PRIMARY reference, verifies
the formula and constants against it (quote page), and only then freezes —
the constants written here are to be checked, not trusted.]

Team ownership: cases 1 (primal) and 2 -> cfd; case 1 adjoint rung ->
dafoam; cases 3 and 4 -> heat-transfer; verification spot-checks all
comparators and certificates.

════════════════════════════════════════════════════════════════════
CASE 1 — JET-FLAP AIRFOIL: BLOWN HIGH-LIFT vs THIN-AIRFOIL JET-FLAP THEORY
════════════════════════════════════════════════════════════════════

## 1.1 Physics and nondimensional definition
- Baseline section: NACA 0012 (already gated on file for unblown CL-alpha
  and Cd; reuse those records as the V column).
- Jet flap: a thin tangential jet issuing at the trailing edge, deflected
  at angle tau below the chord line. The jet adds momentum (not just mass)
  and creates a "pneumatic flap": lift augmentation grows with the jet
  momentum coefficient.
- Jet momentum coefficient (2D, per unit span):
      C_mu = (rho_j * h * V_j^2) / (0.5 * rho_inf * U_inf^2 * c)
  With rho_j = rho_inf (incompressible, same fluid): C_mu = 2 (h/c)(V_j/U_inf)^2.
- Chosen nondimensionals: Re_c = U_inf c / nu = 1.0e6; chord c = 1 m;
  U_inf = 10 m/s -> nu = 1.0e-5 m^2/s (set in transportProperties).
  Slot height h/c = 0.005 (h = 5 mm). Jet angle tau = 30 deg (measured
  from the chord line, deflected toward the pressure side).
- C_mu sweep (primary): 0.0 (unblown reference), 0.05, 0.1, 0.2, 0.4.
  V_j = U_inf * sqrt(C_mu / (2 h/c)) -> for C_mu = 0.05/0.1/0.2/0.4:
  V_j = 22.4 / 31.6 / 44.7 / 63.2 m/s. All incompressible-legitimate.
- Angle of attack: alpha = 0 deg for the C_mu sweep (isolates the jet
  effect); secondary sweep alpha = 0, 4, 8 deg at C_mu = 0.1.

## 1.2 Geometry construction (cfd)
- Take the NACA 0012 surface point set already in the repo. Truncate the
  trailing edge to a blunt base of height h_base = h (5 mm) and place the
  slot on that base: the slot patch is the base segment itself, so the
  jet exits AT the trailing edge in the direction tau. (This is the
  cleanest jet-flap realisation for a meshable case; the alternative of
  a slot on the lower surface just upstream of the TE is acceptable if
  meshing the base is troublesome — record the choice.)
- Patches: airfoil (wall), jetSlot (the base segment), farfield (a
  circle/box of radius >= 25c), front/back (empty, 2D).
- Domain: C-mesh or O-mesh with farfield at 25-30 chords; record which.

## 1.3 Mesh ladder (cfd) — 3 levels, refinement ratio r >= 1.3 in every
direction, generated from ONE parametric script (never hand-edited):
- L1 ~ 40k cells, L2 ~ 75k, L3 ~ 140k (2D, one cell thick).
- Near-wall: first-cell y+ <= 1 on all three levels (resolve the
  boundary layer; no wall functions — the jet/BL interaction is the
  physics). Growth ratio <= 1.15 in the BL, >= 30 layers.
- Slot resolution: >= 12 cells across the slot height h on L1, scaled
  with r on L2/L3 (the jet must be resolved, not smeared).
- Wake refinement: a box 3c long behind the TE at BL-comparable spacing;
  the jet sheet must stay resolved for >= 1c downstream.
- checkMesh gates: max non-orthogonality < 65, max skewness < 4, no
  negative volumes; birth certificate per level (cell count, y+ histogram,
  quality stats).

## 1.4 Boundary conditions and numerics
- Solver: simpleFoam (steady, incompressible), OpenFOAM v2606.
- Turbulence: kOmegaSST, low-Re wall treatment (omegaWallFunction with
  y+ <= 1 behaves as low-Re; nutLowReWallFunction or nutkWallFunction set
  consistently — record which and keep it fixed across the ladder).
- airfoil: U noSlip; p zeroGradient; k fixedValue ~1e-10 (or kqRWallFunction
  with y+<=1 disclosed); omega omegaWallFunction; nut per wall treatment.
- jetSlot: U fixedValue = V_j (cos tau, -sin tau, 0) in the airfoil frame
  (uniform profile; DISCLOSE as "top-hat jet"); p zeroGradient;
  k = 1.5 (I V_j)^2 with I = 0.01; omega = sqrt(k)/(C_mu^0.25 * l) with
  l = 0.07 h; nut calculated.
- farfield: freestreamVelocity / freestreamPressure (or inletOutlet /
  outletInlet pair); U_inf = (10,0,0) rotated by alpha; k_inf = 1.5
  (I U_inf)^2, I = 0.001; omega_inf = k_inf^0.5/(C_mu^0.25 L) with L = 0.1c
  (or via viscosity ratio nut/nu = 3 — record).
- Schemes: gradSchemes Gauss linear (with cellLimited for k/omega if
  needed); div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k),
  div(phi,omega) bounded Gauss limitedLinear 1; laplacian Gauss linear
  corrected; second order throughout — no first-order upwind on the
  gated levels (a first-order feasibility run is allowed, labeled).
- SIMPLE: consistent yes; relaxation p 0.3 / U 0.7 / k,omega 0.7 (start);
  nNonOrthogonalCorrectors 1.
- Convergence criterion (frozen): residuals p, Ux, Uy, k, omega < 1e-6
  (ALL channels the same order — no channel 1000x tighter than siblings)
  AND absolute bounds: force-coefficient stationarity |dCL| < 1e-4 over
  the last 2000 iterations, |dCd| < 1e-5; continuity error max < 1e-8;
  max |U| < 2 V_j (blow-up guard). Iteration cap 20,000; hit cap -> NOT A
  RESULT, never "close enough".
- Force computation: forceCoeffs function object with lRef = c, Aref = c
  (per unit span), magUInf = U_inf, rhoInf = 1; CofR at quarter chord.
  IMPORTANT: the jet momentum flux through the slot is NOT a pressure/
  viscous force on the wall; CL from forceCoeffs is the aerodynamic lift
  on the airfoil surface only. Additionally compute the jet reaction
  component separately (rho h V_j^2 sin tau / (0.5 rho U_inf^2 c) = C_mu sin
  tau) and report BOTH: CL_aero (surface integration) and CL_total =
  CL_aero + C_mu sin(tau). The theory gate uses CL_total (Spence's CL
  includes the jet reaction) — state this explicitly in the prereg.

## 1.5 Gates (pre-registered before the first gated solve)
- V (existing): unblown NACA 0012 at alpha 0/4/8 reproduces the on-file
  gated CL-alpha slope and Cd within their existing bands (regression
  against our own record, same mesh family).
- G: Roache triple on CL_total at C_mu = 0.1, alpha = 0: observed order
  p in [1.3, 2.5], GCI_fine < 3% on CL, planted zero in the comparator.
- THEORY GATE (jet-flap thin-airfoil theory; PRIMARY: Spence, D.A. (1956),
  "The lift coefficient of a thin, jet-flapped wing," Proc. R. Soc. Lond.
  A 238 — pull it, verify the expansions and constants on the page):
  Spence's small-C_mu expansions, AS REMEMBERED (verify before freezing):
      dCL/dtau   = 2 sqrt(pi C_mu) (1 + 0.151 sqrt(C_mu) + 0.139 C_mu)
      dCL/dalpha = 2 pi (1 + 0.151 sqrt(C_mu) + 0.219 C_mu)
  Gate quantities: (a) CL_total(C_mu) at alpha = 0, tau = 30 deg versus
  theory CL = tau * dCL/dtau (tau in radians) for C_mu in {0.05, 0.1, 0.2};
  band: |CL_sim - CL_theory| / CL_theory <= 15% at C_mu <= 0.1 (thin-airfoil
  + inviscid + small-deflection assumptions; 30 deg is at the edge of
  "small" — DISCLOSE). Pre-registered expectation: agreement degrades
  with C_mu and tau; the C_mu = 0.4 point is reported OUTSIDE the gate as
  the theory-departure exhibit (viscous jet-sheet decay and thickness
  effects). (b) dCL/dalpha at C_mu = 0.1 from the alpha sweep vs theory
  within 15%.
- Physicality: continuity closure; realisability of k/omega bounds; jet
  mass flow through jetSlot equals rho h V_j (integrate phi on the patch;
  mismatch > 0.5% = mesh/BC defect).
- Structure metrics (report, not gate): jet-sheet trajectory (locus of
  max |U| downstream), separation on the upper surface (yes/no,
  location), Cp distribution compared unblown vs blown.

## 1.6 Cost and caps
- Per solve: L1 ~ 10 core-min, L2 ~ 25, L3 ~ 60 (estimate; calibrate).
- Program: 5 C_mu points x L1 for the map; triple at C_mu 0.1; alpha sweep
  at L2. Cap 300 core-min for the primal family.

## 1.7 ADJOINT RUNG (dafoam) — after the primal gate is frozen
- Primal: DAFoam DASimpleFoam with kOmegaSST, same BCs; the jetSlot patch
  velocity is a FIXED boundary condition (not a design variable).
- Design variables: FFD box enclosing the aft 40% of the chord (x/c in
  [0.6, 1.02]), 2D FFD 8x2 control points; DVs = vertical displacement of
  the control points; the slot geometry is NOT a DV in rung A — the
  FFD must leave slot height h and jet angle tau unchanged (constrain the
  TE control points or exclude the base segment from deformation; verify
  post-deformation h and tau to 1e-4 and record).
- Objective: maximize CL_total at fixed C_mu = 0.1 (jet BC fixed), fixed
  alpha = 0 (no AoA in the DV set — this is a pure shape rung).
- Constraints: thickness >= 0.9 x baseline at x/c = 0.65, 0.8, 0.9;
  volume >= 0.95 x baseline; Cd <= 1.10 x baseline Cd (so lift is not
  bought with a bluff-body drag rise).
- Gradient verification rung FIRST: FD-vs-adjoint on 3 DVs, step sweep
  1e-2, 1e-3, 1e-4 (report the plateau); registered band: relative error
  < 1% at the plateau; np-invariance spot row (np=1 vs np=4 gradient
  agreement to 1e-6 relative); deterministic decomposition.
- Optimizer: per OPTIMIZATION_STANDARD.md defaults (SLSQP or IPOPT as the
  standard names); max 60 iterations; feasibility tol 1e-6; opt tol 1e-5;
  the 100-iteration-cap lesson applies (declare the cap in the prereg).
- Post-optimum: re-solve the optimum from scratch on the L2 mesh (fresh
  mesh from the deformed surface, not the warped mesh), constraints
  re-checked, CL/Cd re-derived; report the improvement decomposed:
  (i) CL gain attributable to effective camber (compare the optimized
  section's unblown CL at alpha 0 vs baseline unblown) versus (ii) CL gain
  attributable to jet-sheet interaction (the remainder). No % quoted
  before this decomposition exists.
- Cap: 400 core-min for gradient verification + optimization + re-solve.

════════════════════════════════════════════════════════════════════
CASE 2 — DUCTED ACTUATOR DISK: THRUST vs AIRSPEED (STATIC AUGMENTATION
TO RAM-DRAG), AXISYMMETRIC
════════════════════════════════════════════════════════════════════

## 2.1 Physics
- A fan inside a duct is modeled as an actuator disk: a thin region
  imposing a uniform axial momentum source equivalent to a pressure jump
  delta_p across the disk. No blades, no swirl, no rotation — DISCLOSE on
  every surface: "actuator-disk representation; no rotor."
- The classic trade: at static conditions the duct augments thrust
  (the lip accelerates inflow and the exit sets the slipstream); as
  airspeed rises, ram drag on the duct and reduced disk loading erode the
  benefit. The output is the map: total thrust (disk + duct) versus
  airspeed at fixed power (or fixed delta_p), for a given exit-area ratio.

## 2.2 Geometry (axisymmetric, single wedge)
- Duct: inner diameter D = 0.25 m (eQ250-class scale; record as chosen
  for scale, not as their geometry). Duct length L = 0.8 D. Inlet lip:
  elliptical, lip radius ratio r_lip/D = 0.06 (sweep later: 0.03, 0.06,
  0.10). Exit: cylindrical exit with exit-area ratio sigma = A_exit /
  A_disk = 1.0 (primary), 1.2 and 0.85 as secondary sweep.
- Disk: cellZone "disk", thickness t = 0.02 D, located at x = 0.35 L from
  the lip highlight, spanning the full duct radius minus a tip-gap band
  of 1% D (declared, disclosed).
- Centerbody: a hub of diameter 0.3 D with a rounded nose ahead of the
  disk and a tail cone behind (represents the motor nacelle; also needed
  for Case 3 continuity). Record the profile.
- Domain: axisymmetric wedge (5 degrees, one cell thick, wedge patches
  front/back), farfield radius 15 D, upstream 10 D, downstream 25 D.
- Axis patch: type empty (2D axisymmetric convention in OpenFOAM: wedge +
  empty axis, or symmetry — use the v2606-recommended pattern and record).

## 2.3 Actuator disk implementation
- fvOptions: vectorSemiImplicitSource (or explicit momentum source) on
  cellZone disk, injectionRateSuSp = delta_p / t (N/m^3) in +x (thrust
  direction pointing upstream; sign checked by a planted control: a
  known delta_p must produce a mass-flow increase and a pressure rise
  across the disk equal to delta_p within 2% — verify on L1 before any
  gated run).
- delta_p sweep at fixed geometry: choose disk loading DL = delta_p in
  {200, 500, 1000, 2000} Pa (sensible small-EDF loadings; state that
  they are chosen for the physics, not as their operating points).
- Airspeed sweep: U_inf in {0 (static), 10, 20, 30, 40, 50} m/s.
  Static case: farfield as totalPressure/inletOutlet with p_0 = 0 and
  U inletOutlet (0 inflow), so the disk pulls flow from rest.
- Fluid: air, rho = 1.2 kg/m^3, nu = 1.5e-5 m^2/s; incompressible
  (max velocities stay < 100 m/s — check on every run; a run exceeding
  M 0.3 is disclosed).

## 2.4 Mesh ladder
- L1 ~ 30k, L2 ~ 55k, L3 ~ 100k cells (wedge). First-cell y+ <= 1 on the
  duct inner/outer surfaces and hub; lip region refined (>= 40 cells around
  the lip radius on L1); disk zone >= 4 cells thick on L1; slipstream
  refinement 5 D downstream.
- Same checkMesh gates and birth certificates as Case 1.

## 2.5 Numerics
- simpleFoam, kOmegaSST, low-Re walls; schemes as Case 1; relaxation
  p 0.3 / U 0.7 (static case may need U 0.5 — record).
- Convergence: residuals < 1e-6 all channels; absolute: thrust stationarity
  |dT| < 0.1% over last 2000 iterations; mass flow through the disk
  stationary to 0.1%; continuity error bound; iteration cap 15,000.

## 2.6 Quantities of interest (function objects + post scripts)
- T_disk = delta_p * A_disk (imposed; report as the input).
- T_duct = integrated pressure + viscous force on duct + hub surfaces in
  the thrust direction (forces function object on patches duct, hub).
- T_total = T_disk + T_duct.
- Mass flow through the disk: surfaceFieldValue on a plane at the disk.
- Exit velocity profile at the duct exit plane; far-slipstream velocity
  V_e (max axial velocity at 3 D downstream on the axis).
- Power P = mdot * (V_e^2 - U_inf^2) / 2 (ideal) and P_disk = delta_p *
  Q (volume flow) — report both.
- Lip separation flag: presence of reversed axial velocity on the inner
  lip surface (yes/no + extent).

## 2.7 Gates
- V: (a) the planted delta_p control (pressure jump across the disk
  = delta_p within 2%); (b) empty-duct pass-through: with delta_p = 0
  and U_inf = 30 m/s, T_total is drag-only and small (< 2% of the
  loaded-case thrust) — sanity that the duct does not "generate" thrust
  from nothing.
- G: Roache triple on T_total at delta_p = 1000 Pa, U_inf = 20 m/s;
  observed p in [1.3, 2.5]; GCI_fine < 3%.
- THEORY GATE (ducted-propeller momentum theory; PRIMARY: pull a textbook/
  paper treatment of ducted actuator disks — e.g., the ducted-fan momentum
  analysis in a standard propulsion text or Kuechemann & Weber, verify on
  the page before freezing): (a) STATIC: for an ideal duct of exit-area
  ratio sigma, the static thrust at equal power relative to an open
  actuator disk of the same area is (2 sigma)^(1/3) — for sigma = 1 the
  ideal augmentation is 2^(1/3) = 1.26. Gate: the simulated static
  T_total / T_open (run the open disk, same delta_p and power, same
  domain) lands BELOW the ideal 1.26 and above 1.0, and the shortfall is
  reported as duct loss; band: T_total/T_open in [1.05, 1.26]. (b) FORWARD
  FLIGHT: momentum-theory thrust T = mdot (V_e - U_inf) with mdot and V_e
  measured from the simulation must equal the integrated T_total within
  5% (this is an internal-consistency gate: forces vs momentum balance —
  if it fails, the control-volume integration is wrong before the physics
  is questioned).
- Physicality: continuity closure; no reversed flow in the farfield.
- Report (not gate): the thrust-vs-airspeed map at four loadings with GCI
  bands; the airspeed at which T_duct changes sign (duct becomes net
  drag); lip-separation onset across the map.

## 2.8 Cost and caps
- Per solve ~5-15 core-min (axisymmetric is cheap). Program: 4 loadings x
  6 airspeeds at L1 = 24 solves (~4 core-h), triple at one point, open-disk
  reference at static. Cap 320 core-min.

════════════════════════════════════════════════════════════════════
CASE 3 — MOTOR-IN-DUCT CONJUGATE HEAT TRANSFER: HOUSING TEMPERATURE vs
POWER x AIRSPEED (STEADY, AXISYMMETRIC CHT)
════════════════════════════════════════════════════════════════════

## 3.1 Physics
- An electric motor sits in the duct centerbody; its losses appear as
  heat in the housing; the fan airflow through the annulus cools it. The
  quantity an engineer needs: maximum housing temperature as a function of
  dissipated power and airspeed (annulus velocity) — the "can I hold this
  power at this airspeed" map, with bands.
- Conjugate: solid (housing + a lumped internal heat-source region)
  coupled to the fluid (air annulus) through a temperature/flux-continuous
  interface.

## 3.2 Geometry (reuse Case 2's centerbody)
- Solid region "housing": hollow aluminium cylinder, outer diameter 0.3 D
  (D = 0.25 m -> 75 mm), wall thickness 4 mm, length 0.5 D, closed by the
  nose and tail cones (solid, same aluminium). Inside: a solid "core"
  region of copper-iron equivalent properties representing windings +
  laminations (rho 7000 kg/m^3, cp 450 J/kgK, k 40 W/mK — declared as
  representative, not theirs), filling the housing interior, with a
  uniform volumetric heat source q''' = P_loss / V_core.
- Fluid region: the duct annulus of Case 2 with the actuator disk either
  (a) present, driving the flow (preferred: airspeed then means
  disk-induced annulus velocity), or (b) absent with the annulus velocity
  imposed by U_inf. Start with (b) for the ladder (simpler, one physics at
  a time), then (a) as the coupled variant. Record which.
- 2D axisymmetric wedge as Case 2; the solid regions are wedge sectors.

## 3.3 Materials and BCs
- Air: rho 1.2, cp 1005, k 0.026 W/mK, mu 1.8e-5, Pr 0.7 (constant
  properties; Boussinesq-free since forced convection dominates — verify
  Richardson number Ri = g beta dT L / U^2 < 0.1 on every run; if Ri >
  0.1 anywhere, the buoyant solver variant is required and the run is
  re-registered).
- Aluminium housing: rho 2700, cp 900, k 167.
- Fluid inlet: U = U_inf (sweep), T = 288 K; outlet: pressure outlet,
  T zeroGradient/inletOutlet; farfield/duct walls: adiabatic for the duct
  itself (only the housing is conjugate) — declare.
- Solid outer surfaces exposed to air: coupled (compressible::
  turbulentTemperatureCoupledBaffleMixed on the fluid/solid interface
  pair). Solid internal core/housing interface: coupled likewise.
  Solid ends not exposed to flow: adiabatic. Radiation: OFF and DISCLOSED
  (housing temperatures are moderate; radiation is a stated omission,
  bounded in the report by a hand estimate epsilon sigma (T^4 - T_inf^4)
  A as an upper bound on the neglected term).
- Heat source: fvOptions scalarSemiImplicitSource on cellZone core in the
  solid energy equation, injectionRate = P_loss / V_core (W/m^3).
- Sweep: P_loss in {100, 300, 600, 1000} W; U_inf (annulus) in
  {10, 20, 30, 40} m/s -> 16 points. (Loss levels chosen as representative
  of a small EDF motor class; state as assumptions.)

## 3.4 Solver and numerics
- chtMultiRegionSimpleFoam (steady), regions fluid + housing + core;
  kOmegaSST in the fluid; low-Re walls (y+ <= 1 on the housing surface —
  the heat-transfer coefficient is the physics; wall functions are NOT
  acceptable on the gated levels).
- Energy: turbulent Prandtl number Prt = 0.85 (declared).
- Convergence: fluid residuals < 1e-6; solid energy residual < 1e-8;
  absolute: max housing temperature stationary to 0.05 K over 1000
  iterations; HEAT BALANCE closure: P_loss = enthalpy flux out - in +
  neglected terms, within 1% (the mutation-tested heat-balance
  instrument); iteration cap 10,000.

## 3.5 Mesh ladder
- Fluid: L1 ~ 35k / L2 ~ 65k / L3 ~ 120k cells; y+ <= 1 on the housing;
  >= 25 BL layers; solid regions: >= 8 cells across the 4 mm wall on L1,
  scaled with r; conformal fluid/solid interface (single mesh split by
  regions via splitMeshRegions -cellZones) to avoid interpolation error at
  the coupled patch.

## 3.6 Gates
- V (exact tier): (a) with the flow OFF (pure conduction test, fluid
  replaced by a fixed-temperature boundary): the radial temperature drop
  across the aluminium wall matches the 1D cylindrical-conduction exact
  solution q ln(r_o/r_i)/(2 pi k L) within 1%; (b) energy balance with a
  planted source error (inject +10% q''' in a control run; the balance
  instrument must report a 10% imbalance — proves it sees a non-zero
  through the real path).
- V (correlation tier): the mean Nusselt number on the housing surface
  at one point (P 300 W, U 20 m/s) vs a turbulent-annulus/cylinder-in-
  axial-flow correlation (PRIMARY: pull Gnielinski or the Dittus-Boelter
  form for annular flow with hydraulic diameter D_h = D_duct - D_housing;
  verify applicability range on the page): agreement within 25% (the
  correlation's own scatter) — scores V, never P.
- G: Roache triple on max housing temperature at (300 W, 20 m/s); p in
  [1.3, 2.5]; GCI_fine < 2% of (T_max - T_inf).
- Physicality: heat balance < 1%; Ri < 0.1 verified; no negative
  temperatures; T_max < 200 C sanity (else the point is flagged as
  "beyond assumption range" — a real finding).
- Report: the 4 x 4 map of T_max with GCI band per point; the isotherm
  "T_max = 120 C" (representative winding-limit class — state as an
  assumption) traced across the map as the hold-this-power boundary;
  radiation upper-bound estimate per point.

## 3.7 Cost and caps
- Per CHT solve ~15-40 core-min (L1); 16 points ~8 core-h at L1; triple
  at one point ~2 core-h; cap 700 core-min. Run the 16-point map at L1
  with the single GCI point's uncertainty applied as the band (disclosed:
  band measured at one point, applied to all — a stated approximation
  until per-point triples are affordable).

════════════════════════════════════════════════════════════════════
CASE 4 — BATTERY MODULE TRANSIENT: COOLING CHANNEL, UNIFORMITY, THERMAL
MASS RESPONSE TO A TAKEOFF POWER PULSE (TRANSIENT CHT)
════════════════════════════════════════════════════════════════════

## 4.1 Physics
- A battery module dissipates heat (I^2 R dominated) that varies with
  the power profile: a takeoff pulse then cruise. Cells have large thermal
  mass; the cooling channel removes heat with a lag. Quantities an
  engineer needs: peak cell temperature, temperature spread across the
  module (uniformity), time-to-peak and time-to-steady after the pulse.
- Conjugate transient: solid cells (lumped effective properties) in a
  cooling channel with air or liquid coolant.

## 4.2 Geometry (2D planar to start, then 3D module as the escalation)
- Module: 8 prismatic cells in a row, each cell 100 mm (flow direction)
  x 30 mm (thickness) x unit depth (2D), separated by 3 mm cooling
  channels (air) or with cold-plate contact on one face (liquid variant,
  later). Start: AIR-COOLED channels between cells (2D planar, empty
  front/back).
- Channel inlet plenum 50 mm upstream, exit plenum 100 mm downstream.
- Cell effective properties (declared representative): rho 2500 kg/m^3,
  cp 1000 J/kgK, k_in-plane 25 W/mK, k_through-plane 1 W/mK (anisotropic —
  OpenFOAM solid thermophysical with anisotropic conductivity via
  solidThermo + tensorial kappa; if the anisotropic path is not
  available in the chosen solver at v2606, run isotropic k = 3 W/mK and
  DISCLOSE; escalate to anisotropic as a rung).
- Casing walls: adiabatic outer boundary (declared).

## 4.3 Heat generation profile (the pulse)
- q'''(t) per cell: q_takeoff for 0 <= t < 60 s, then q_cruise for
  60 <= t <= 900 s. Values: q_takeoff = P_takeoff / V_cell with P_takeoff =
  15 W per cell (heat), q_cruise = 4 W per cell. (Representative of a
  high-C-rate takeoff on small aviation cells; assumptions stated.)
  Implement via fvOptions scalarSemiImplicitSource with a time-dependent
  injection rate (Function1 table). Optional second rung: SOC-dependent
  or temperature-dependent resistance — not in rung A.
- Initial condition: uniform 293 K everywhere; coolant inlet 293 K.

## 4.4 Coolant BCs and flow
- Air: inlet velocity in the channel such that the channel Re_Dh is
  turbulent-marginal (declare): U_inlet = 8 m/s in 3 mm gaps -> Re_Dh ~
  3,200 (transitional — DISCLOSE; run kOmegaSST low-Re and report the
  sensitivity to a laminar run at one point as a model-form check);
  T_inlet = 293 K; outlet pressure.
- Fluid/solid interfaces coupled (turbulentTemperatureCoupledBaffleMixed);
  solid/solid cell-to-cell contact through the channel only (no direct
  contact in rung A).

## 4.5 Solver and numerics
- chtMultiRegionFoam (transient), PIMPLE, Courant-limited: max Co 1 in
  the fluid; fixed time step per level (dt ladder below) — no adaptive
  stepping on gated runs (reproducibility).
- Time-step ladder (the T11 machinery): dt = 0.02, 0.01, 0.005 s on the
  L2 mesh; report the temporal observed order and a temporal GCI on peak
  temperature and on time-to-peak; spatial ladder L1/L2/L3 at dt = 0.01.
- Duration 900 s simulated. Write intervals: every 5 s for fields;
  probes every time step at: center of cell 1, cell 4, cell 8; channel
  outlet temperature; solid max temperature (fieldMinMax function object
  per region).
- Convergence per time step: energy residual < 1e-8 (solid), fluid p/U
  < 1e-6 per PIMPLE loop; absolute: heat-balance closure per step
  (source energy = stored + convected within 2% cumulative over the run).

## 4.6 Gates
- V (exact tier — lumped capacitance): a control configuration with ONE
  cell, uniform q''' step, high conductivity (k set to 200 W/mK so
  Bi = h L / k < 0.1), fixed convective coefficient h imposed via a
  convective boundary condition (externalWallHeatFluxTemperature with a
  given h and T_inf) instead of the coupled fluid: the cell temperature
  must follow the analytic lumped solution
      T(t) = T_inf + (q''' V / (h A)) (1 - exp(-t/tau)),  tau = rho cp V / (h A)
  within 1% at t = tau, 2 tau, 3 tau. This is the T11-class exact gate
  for the transient machinery, independent of the fluid.
- V (energy balance): planted +10% source control as in Case 3;
  cumulative balance instrument must see it.
- G: spatial triple on peak cell temperature; temporal triple on
  time-to-peak (dt ladder); observed orders reported; GCI on both.
- Physicality: no temperature below T_inlet anywhere; monotone rise during
  the pulse in every cell (a non-monotone rise under constant source is
  a numerical artifact); cumulative heat balance within 2%.
- Report (not gate): peak temperature and its time per cell; module
  spread (T_max - T_min across cells) vs time; time-to-steady (dT/dt <
  0.01 K/s); outlet coolant temperature history; the laminar-vs-SST
  sensitivity at one point as a model-form band on the channel side.

## 4.7 Cost and caps
- Transient CHT 2D: ~30-90 core-min per 900 s run at L2/dt 0.01 (estimate;
  calibrate on L1 first). Program: lumped-capacitance control (cheap),
  spatial triple (3 runs), temporal triple (3 runs; two overlap the spatial
  set), one laminar sensitivity run: ~7-8 runs, cap 600 core-min.
- Escalation rung (not now): 3D module, liquid cold plate, SOC-dependent
  source, cell-to-cell conduction paths.

════════════════════════════════════════════════════════════════════
COMMON DELIVERABLES PER CASE (for the record; no external surfaces yet)
════════════════════════════════════════════════════════════════════
1. Frozen pre-registration (template) with commit hash BEFORE gated runs.
2. Mesh birth certificates per level; checkMesh outputs.
3. Run tree with STATUS files, rc, wall time, cost-calibration rows.
4. Comparator with planted controls proven through the real path.
5. Verdict per gate (PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
   BLOCKED) with V/G/P tiers and the matrix rows filed.
6. Result tables + plots: Case 1 CL vs C_mu with theory line and GCI band,
   Cp comparisons, adjoint before/after fields + decomposition table;
   Case 2 thrust vs airspeed map (4 loadings), T_duct sign-change airspeed,
   lip-separation onset; Case 3 T_max map (4x4) with band and the
   hold-this-power isotherm; Case 4 temperature histories per cell, spread
   vs time, time-to-peak/steady, lumped-capacitance gate plot.
7. Certificate draft per case listing WHAT WAS NOT CHECKED (2D/axisym,
   steady where steady, RANS model class, actuator-disk not rotor, no
   acoustics, radiation off, representative not proprietary properties).

[Chief's receipt note: delivered by Sanaa 2026-08-30 ~23:00Z with the
closing words "priority for cfd and heat trasfr teams". Captured verbatim
above; ownership per the header — cases 1 (primal) + 2 cfd, case 1
adjoint rung dafoam, cases 3 + 4 heat-transfer, verification spot-checks
all comparators and certificates. Priority: cfd and heat-transfer.]
