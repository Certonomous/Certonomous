# [SANAA-DIRECT] 2026-09-12 ~21:40Z — 96-core allocation table; PPTC VP1304 propeller act; NASA CRM wing-body act

Recorded by the chief from Sanaa's own session turns (session identity katie@certonomous.com), byte-exact below each rule. Nothing in the quoted blocks may be corrected by any future editor. Context: the host was resized to 96 cores / 739 GiB and booted 2026-09-12 21:32:17 UTC; every solver had been stopped cleanly with checkpoints (see `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` for the run rules that remain in force). Her opening words, byte-exact: "i am back all teams reusme. We now have 96 cores. Here is the breakdown of what will go in these :" and, closing the propeller instruction: "CRM full body instructions coming shortly. While I am coming up with them all runs resume dafoam run gts launched now".

---

## A. CORE ALLOCATION — byte-exact

> [SANAA-DIRECT] Core allocation on the 96-core host, effective now
>
> Lane    Ranks    Notes
> CRM wing-body (full configuration)    32    Committee grid under the two-tier standard; DPW data retrieved and title-page verified before the first solve; trim to CL 0.5 at Mach 0.85 by alpha search; band on CL/CD/CM with the DPW scatter; node memory reserved: 200 GB. Launches the moment the grid and data are on disk.
> SUBOFF sweep    28    Seven points at 4 ranks each, one wave; L1 stall fix and blended-wall arm first (registered); L2 at the three corners follows on the same ranks.
> Real propeller / rotor    16, reserved    Held empty until the case is chosen and its instruction is written (Caradonna–Tung probe → S-76 or the marine propeller). Nothing else borrows these ranks; the probe launches the day the instruction lands.
> Finalization lane    20 M6 with nasa grid (3 levels) (4), K2 transient , D6R2 multipoint (4). Total 96. Memory guard against 768 GB per host; every lane checkpointing every 30 minutes; all as ubuntu; nothing outside this table launches without a slot freeing inside its own lane.
>
> Rules of the table: a lane's free ranks may be lent to another lane only when that lane has nothing queued, and are returned the moment its next case is registered. The propeller reserve is never lent. Disk under 80%: graded trees archived as they close. Report: one status line per lane, daily.

**Chief's reading:** four lanes — CRM wing-body 32 (cfd), SUBOFF sweep 28 (cfd), propeller reserve 16 (cfd; the PPTC instruction below is that instruction, so the reserve is now active for it), finalization 20 (M6I 3 levels at 4, K2h transient, D6R2 at 4; cfd/heat-transfer/dafoam). The runner's core gate is against nproc = 96; per-lane budgets are held by the owning supervisors from this table. Memory guard reads the host's real memory (739 GiB available), never a nominal figure.

---

## B. PPTC VP1304 PROPELLER — byte-exact

> # [SANAA-DIRECT] PPTC VP1304 PROPELLER: OPEN-WATER ACT, DETERMINISTIC RUN INSTRUCTION
>
> Purpose. The rotating-machinery credential act: a real five-bladed propeller, the industry's workshop case, open-water curve banded against the SVA Potsdam towing-tank data, wake against LDV, on a grid family. Lane: the 16-rank propeller reserve.
>
> Everything below names where each element is fetched. Nothing is chosen by an agent at run time; where a choice exists it is registered here.
>
> ---
>
> ## 1. SOURCES (fetch first, verify by title page, hash into the registration)
>
> - Geometry (CAD): SVA Potsdam PPTC page, section "CAD Geometry of PPTC Propeller": https://www.sva-potsdam.de/en/potsdam-propeller-test-case-pptc/ . Download the VP1304 propeller CAD (IGES/STEP) exactly as offered; record file name, size and sha256. Do not use any third-party STL of this propeller.
> - Open-water data and geometry table: SVA Report 3752, Barkmann, U. H. (April 2011), "Potsdam Propeller Test Case (PPTC), Open Water Tests with the Model Propeller VP1304": https://www.sva-potsdam.de/wp-content/uploads/2016/04/SVA_report_3752.pdf . Title-page verify: "Report 3752, Potsdam, April 2011, author Dipl.-Ing. U. H. Barkmann".
> - LDV wake data: SVA Report 3754, Mach, K.-P. (April 2011), "PPTC, LDV velocity measurements with the Model Propeller VP1304", same site, PPTC page downloads. Needed for section 8 only.
> - Cavitation data (later rung, not this act): SVA Report 3753, Heinke, H.-J. (April 2011).
> - Workshop case description and participant scatter: Barkmann and Heinke, "PPTC Test Case Description", smp'11 Workshop, Hamburg 2011: https://www.marinepropulsors.com/smp/files/downloads/smp11_workshop/smp11_workshop/II-1_Barkmann.pdf ; and the open-water presentation https://www.sva-potsdam.de/wp-content/uploads/2016/03/smp11_case21_pres_OWT.pdf . The participant scatter in these sets the honest band (section 4).
> - Published mesh practice on this propeller (for the mesh envelope in section 5): the smp'11 proceedings participant papers; Sikirica, Carija, Kranjcevic, Lucin (2019), "Grid type and turbulence model influence on propeller characteristics prediction", J. Mar. Sci. Eng. 7, 374 (open access); the DES-SST PPTC study, J. Mar. Sci. Eng. 8, 297 (2020, open access, includes a grid convergence study with the Eca-Hoekstra procedure).
>
> ## 2. THE PROPELLER (from Report 3752, Table 1)
>
> - Diameter D = 0.250 m. Pitch ratio at r/R = 0.7: P0.7/D = 1.635. Expanded area ratio AE/A0 = 0.77896. Chord at r/R = 0.7: c0.7 = 0.10417 m. Skew 18.837 deg. Hub ratio dh/D = 0.300 (dh = 0.075 m). Five blades. Right-handed (looking on the pressure side). Controllable-pitch propeller: a 0.3 mm gap exists between hub and blade root near leading and trailing edges.
> - Registered modelling choices: (a) the 0.3 mm root gap is closed (blade fused to hub), as most workshop participants did; stated on the certificate. (b) The hub is modelled with its cap upstream and the dynamometer shaft downstream as a cylinder of diameter 0.075 m extending to the outlet, rotating with the propeller (the test arrangement: dynamometer H39 behind the propeller, shaft downstream, Report 3752 section 5 and photographs page 4.2 to 4.3). (c) Shaft inclination 0 deg.
>
> ## 3. TEST CONDITIONS AND THE GATE DATA (Report 3752, test 11F0395, n = 15 s-1)
>
> - Fluid: fresh water at 15.6 C, kinematic viscosity 1.124e-6 m2/s, density 998.99 kg/m3.
> - Rotation rate n = 15.0 s-1 (omega = 94.248 rad/s). Advance speed V = J n D, so V = 3.75 J m/s.
> - Reynolds number definition (Report 3752 annex): Re = c0.7 sqrt(V^2 + (0.7 pi n D)^2) / nu. At J = 1.2, n = 15: Re = 0.87e6.
> - Which dataset to grade against: the CFD models blades plus hub plus shaft, so it is graded against the table "corrected with idle torque and gap force (represents the characteristics of the propeller blades including the hub)", Report 3752 page 2.11. The "blades only" table (page 2.13, additionally corrected for hub resistance) is NOT the comparator; it is recorded as a secondary reference and the difference (about 0.01 in KT at J = 1.2) is disclosed.
> - Registered sweep, six advance ratios taken from the measured points so no interpolation is needed for the gate:
>
> | J | KT (measured) | 10KQ (measured) | eta_O (measured) |
> |---|---|---|---|
> | 0.7985 | 0.5052 | 1.1836 | 0.542 |
> | 0.9314 | 0.4297 | 1.0493 | 0.607 |
> | 1.0683 | 0.3538 | 0.9096 | 0.661 |
> | 1.2021 | 0.2797 | 0.7676 | 0.697 |
> | 1.3308 | 0.2082 | 0.6300 | 0.700 |
> | 1.4594 | 0.1394 | 0.4944 | 0.655 |
>
> - Polynomials for interpolation if ever needed (page 2.11, valid 0 <= J <= 1.677): KT = 0.955438 - 0.346932 J - 0.629537 J^2 + 0.586304 J^3 - 0.175174 J^4; 10KQ = 2.076022 - 0.949651 J - 0.719299 J^2 + 0.873861 J^3 - 0.306054 J^4.
> - Design point for the grid family: J = 1.2021 (eta near maximum, the workshop's reference condition).
> - Definitions (Report 3752 annex A2.2): J = V/(nD); KT = T/(rho n^2 D^4); KQ = Q/(rho n^2 D^5); eta_O = J KT/(2 pi KQ). T is the axial force on blades plus hub plus shaft in the thrust direction; Q the torque about the shaft axis on the same surfaces.
>
> ## 4. BANDS (frozen before the first solve)
>
> - The report gives no measurement uncertainty. The band is therefore the smp'11 participant scatter at each J, read from the workshop summary (section 1 sources) and recorded with its page. Fallback if the scatter cannot be read to a number: +-3 percent on KT and +-4 percent on KQ for J <= 1.33, +-6 percent and +-8 percent at J = 1.46 (where KT is small and relative errors grow), stated as a lab judgement.
> - Gate: PASS at a J point when both KT and 10KQ lie inside their bands; the act's headline gate is the design point J = 1.2021 on the fine level of the family; the sweep is graded on the medium level with the family band inherited and disclosed.
> - Expected systematic direction, registered as a prediction: fully turbulent RANS tends to over-predict KQ slightly at these Reynolds numbers because laminar regions on the model blades are not captured; the n = 10 versus n = 15 difference in the report (curves crossing at J = 1.3) is the measured Reynolds effect. Prediction: CFD 10KQ above measured by 1 to 4 percent, KT within 2 percent, at J = 1.2.
>
> ## 5. GEOMETRY ADMISSION AND MESH
>
> - Admission: read the CAD at kernel level; units confirmed as metres by D = 0.250 m; watertight after closing the root gap; five blades tagged one patch (or five, then merged), hub, cap, shaft tagged separately; feature-resolution audit at the leading edge (curvature-based) and the tip.
> - Domain: cylinder coaxial with the shaft. Inlet 3D upstream of the propeller plane, outlet 6D downstream, outer radius 4D. Single blade passage of 72 deg with cyclic periodic boundaries (registered choice; the coarse level is also run as the full 360 deg propeller once, and the passage-versus-full difference in KT and KQ is recorded as a check, must be under 0.5 percent).
> - Rotating zone (MRF): a cylinder around the blades of diameter 1.3D and axial extent from 0.5D upstream to 0.5D downstream of the propeller plane; the interface must not cut the blade tips' wake within 0.5D. Zone diameter and extent are registered parameters (the MRF zone-size lesson from the Rushton act applies: sensitivity is checked once at 1.3D versus 1.6D on the coarse level, difference in KT recorded).
> - Mesh generator: snappyHexMesh from the admitted STL tessellated to the physics tolerance (leading-edge radius resolved by at least 8 cells across, tip resolved by at least 6 cells across the tip chord), refinement box around the blades and a cylinder along the tip-vortex path 1D downstream; prism layers on blades, hub and shaft: 6 layers, growth ratio 1.2, first-cell height for a y+ target of 30 to 60 with wall functions (registered wall treatment; a wall-resolved y+ of 1 would need tens of millions of cells and is the next rung). Quality gates: non-orthogonality below 70 deg, skewness below 4, cell-volume growth capped at 1.25.
> - Family: three levels from one script with uniform ratio 1.5 in the refinement levels and the surface size: coarse about 0.8 M cells per passage, medium about 2.7 M, fine about 9 M. Birth certificate per level: cells, y+ per patch after the design-point solve, quality metrics, resolution at leading edge and tip, hash.
> - Published envelope for comparison: workshop participants ran 2 to 20 M cells for the full propeller with wall functions or wall-resolved layers; the medium single-passage level corresponds to about 13 M full-propeller cells, inside the envelope.
>
> ## 6. SOLVER AND NUMERICS
>
> - simpleFoam (steady, incompressible) with MRFProperties for the rotating zone; k-omega SST with nutkWallFunction; second-order bounded convection (linearUpwind for U, limitedLinear 1 for turbulence); SIMPLE with consistent formulation; relaxation U 0.7, p 0.3, turbulence 0.7; non-orthogonal correctors 1.
> - Boundary conditions: inlet fixed velocity V = 3.75 J m/s along the axis with turbulence intensity 1 percent and a mixing length of 0.1 D; outlet fixed pressure; outer boundary slip; blades, hub, cap and shaft no-slip walls belonging to the rotating zone (rotating wall velocity); cyclic patches periodic.
> - Sign convention: right-handed propeller, axis and rotation direction per Report 3752 annex A3; verified by the smoke run producing positive thrust at J = 0.8 (KT about 0.5); a negative KT stops the case and flips the registered rotation sign, recorded.
> - Convergence: residuals below 1e-5 on p and U; KT and KQ stationary within 0.1 percent over the last 500 iterations; cap 4,000 iterations per point.
> - Solver tolerance strictly tighter than the 0.1 percent stationarity gate (the T23G2Rn2 rule).
>
> ## 7. RUN PLAN (on the propeller reserve: 16 ranks)
>
> 1. Bug check per the protocol: checkMesh on all three levels, dictionaries, dead-lever audit, forces functionObject reading the right patches, planted force perturbation detected.
> 2. Smoke: coarse, J = 0.7985, 300 iterations; predictions registered: KT sign positive, KT between 0.4 and 0.6 at iteration 300, cost per iteration within band.
> 3. Design point family: J = 1.2021 on coarse, medium, fine (4, 4, 8 ranks); observed order and GCI on KT and KQ; iterative error at least 10x smaller than the level differences; band attached. This is the certificate's headline.
> 4. Full-360 check on coarse at J = 1.2021 (5x the passage cells, 8 ranks, once).
> 5. MRF zone sensitivity on coarse at J = 1.2021: zone 1.6D versus 1.3D, difference recorded.
> 6. Sweep on medium: the remaining five J points, 4 ranks each, waves of four; band inherited from the family, disclosed.
> 7. Checkpoints every 30 minutes, last two kept; as ubuntu; detached under the runner; memory guard; core gate.
> 8. Stop rules: per the general run rules; the specific one here: KT oscillating with a fixed period at J = 0.8 (heavy loading, possible unsteady root separation) -> mark, time-average, disclose.
>
> ## 8. DELIVERABLES (the act)
>
> - Open-water curve: KT, 10KQ, eta_O versus J, measured points with the band, CFD points with their bands, on the report's own axes (page 3.3 layout).
> - Family figure at J = 1.2021: KT and KQ on three levels, observed order, GCI band.
> - Blade loading: pressure coefficient on the pressure and suction sides at r/R = 0.7 and 0.9 at J = 1.2021 (no measured Cp exists; shown as the physics, not a gate).
> - Blade surface pressure (both sides) at J = 0.8, 1.2, 1.46: the loading moving inboard as J rises.
> - Tip vortex: Q-criterion iso-surface coloured by pressure, the helical wake, at J = 1.2021.
> - Wake: axial and tangential velocity in the planes of Report 3754 (read the exact plane positions and radii from that report; register them before extracting), compared with the LDV data at the J closest to the LDV condition. Measured-tier gate, band from the report's stated repeatability if given, else disclosed as a comparison.
> - Convergence: residuals, KT and KQ histories with the stationarity window, per point.
> - Mesh figures: coarse level shown for legibility, captioned with the level the numbers come from; y+ map on the blade.
> - Compute table: ranks, core-minutes per point, total, wall time.
> - Certificate: reference (Report 3752, test 11F0395, table page 2.11), bands and their source, what was not checked (cavitation, transition, sliding-mesh unsteadiness, free surface, shaft inclination, the closed root gap), hashes of CAD, mesh levels, settings and comparator.
>
> ## 9. WHAT THIS ACT DOES NOT CLAIM
> Cavitation inception or extent (Report 3753 is the next rung), unsteady blade-passage effects (sliding mesh is the next rung), laminar-turbulent transition on the model blades (the measured Reynolds effect is disclosed, not modelled), behind-hull operation.
>
> ## 10. NEXT RUNGS AFTER THIS ACT
> Sliding-mesh (AMI) unsteady at J = 1.2021 for blade-passage pressure pulses; cavitating conditions from Report 3753 with a mass-transfer model; then the aero counterpart, the S-76 hover rotor from the AIAA Hover Prediction Workshop, using the same pipeline. CRM full body instructions coming shortly. While I am coming up with them all runs resume dafoam run gts launched now

---

## C. NASA CRM WING-BODY — byte-exact (her words: "crm instructions")

> # [SANAA-DIRECT] NASA CRM WING-BODY: TRANSONIC VALIDATION ACT, DETERMINISTIC RUN INSTRUCTION
>
> Purpose. The industry yardstick: the Common Research Model wing-body at cruise, on a Drag Prediction Workshop committee grid family, forces and pressures graded against the NASA wind-tunnel data with the workshop's participant scatter as the honest band. Lane: 32 ranks, up to 200 GB.
>
> Everything below names its source. Where a choice exists it is registered here. Items marked [verify] are details to confirm from the fetched document's own pages before freezing; the registration records the page.
>
> ---
>
> ## 1. SOURCES (fetch, title-page verify, hash into the registration)
>
> - The geometry and the experimental data: NASA Common Research Model site, https://commonresearchmodel.larc.nasa.gov/ . Sections: "Geometry" (CAD, IGES/STEP, wing-body and wing-body-tail configurations, full-scale inches) and "Experimental Data" (NTF and Ames force, moment and pressure data files).
> - The committee grids: AIAA Drag Prediction Workshop site, https://aiaa-dpw.larc.nasa.gov/ , DPW-6 (Workshop6) grids page: the wing-body grids for Case 2, built by the committee, provided per family (structured and unstructured) and per level.
> - The workshop reference for conditions, cases and scatter: Tinoco, E. N., et al. (2018), "Summary Data from the Sixth AIAA CFD Drag Prediction Workshop: CRM Cases", Journal of Aircraft 55(4), 1352-1379; and the DPW-6 case description on the workshop site (gridding guidelines, reference quantities, required conditions). DPW-7 summary (2023) for the latest scatter [verify citation].
> - The experiment: Rivers, M. B., Dittberner, A. (2014), "Experimental Investigations of the NASA Common Research Model", Journal of Aircraft 51(4), 1183-1193 (NTF Test 197 and Ames 11-ft Test 216); and Rivers, M. B. (2019), "NASA Common Research Model: A History and Future Plans", AIAA 2019-3725. The data files themselves are on the CRM site; the papers give the test conditions, corrections and uncertainties.
> - Aeroelastic deflection: the DPW-6 Case 2 geometries include the measured static wing deflection at each angle of attack (from the NTF test); the "deformed" wing-body geometry set and its grids are on the DPW-6 page [verify which alpha values are provided; expected 2.50 to 4.00 deg in 0.25 steps].
>
> ## 2. THE CONFIGURATION AND REFERENCE QUANTITIES (from the CRM site and the DPW-6 case description; verify each from the document page)
>
> - Configuration: wing-body (WB), no tail, half-model with a symmetry plane. Full-scale geometry in inches.
> - Reference quantities (DPW convention, full model): reference area Sref = 594,720 in2 (594,720.0 in2 full, half of that for the half-model), mean aerodynamic chord cref = 275.80 in, span b = 2313.50 in, moment reference point Xref = 1325.90 in, Yref = 468.75 in, Zref = 177.95 in [verify each against the DPW-6 case description; record the page].
> - Grid units: inches. The lab keeps the grid in inches converted by the exact factor 0.0254 to metres at import; the reference quantities are converted identically and stored with the registration.
>
> ## 3. FLOW CONDITIONS (DPW-6 Case 2 / NTF cruise point)
>
> - Mach 0.85. Reynolds number 5.0e6 based on cref. Freestream turbulence: fully turbulent computation (no transition model), matching the workshop's required practice; the tunnel model was tripped at 10 percent chord, disclosed.
> - Primary gate condition: fixed angle of attack on the deformed geometry at alpha = 2.75 deg (the DPW-6 Case 2 point nearest CL = 0.5), because the tunnel data exist at that alpha with the matching measured deflection. Secondary: the CL = 0.500 +- 0.001 trimmed point (DPW-4 style) obtained by an alpha search, reported alongside.
> - Freestream state for the compressible solver: choose T_inf = 310 K [registered], sound speed a = sqrt(gamma R T), U_inf = 0.85 a; dynamic viscosity from Sutherland at T_inf; density from Re: rho = Re mu / (U_inf cref) with cref in metres; p_inf = rho R T_inf. All four values written into the case files and read back onto the screen.
> - Half-model symmetry plane; farfield at the grid's own extent (the committee grids place it at about 100 cref [verify]).
>
> ## 4. THE GATES AND BANDS (frozen before the first solve)
>
> - Quantities: CL, CD (with pressure and viscous split), CM about the moment reference; wing pressure distributions at the NTF pressure rows (nine spanwise rows on the wing at eta = 0.131, 0.201, 0.283, 0.397, 0.502, 0.603, 0.727, 0.846, 0.950 [verify the list from the CRM site]).
> - Reference values: the NTF data at Mach 0.85, Re 5e6, alpha 2.75 deg, from the experimental data files; the corrections applied by NASA (wall, buoyancy, support) recorded from the file header; the Ames data as a secondary reference and the tunnel-to-tunnel difference disclosed.
> - Bands (the honest tolerance): the DPW-6 participant scatter at the same condition on medium-class grids, read from the summary paper: registered numerically from that paper; fallback if a number cannot be read from the pages: CL +- 0.01, CD +- 0.0006 (six drag counts), CM +- 0.01, and Cp +- 0.05 at each row away from the shock, shock position +- 0.03 c. Recorded as a lab judgement where the fallback is used.
> - Known systematic effects, registered as predictions before grading: (a) CM from CFD sits nose-down of the tunnel by roughly 0.03 because of model support interference in the NTF, unless the data are support-corrected (check the file header); (b) the wing-body junction region at the trailing edge shows a separation bubble whose size depends on the closure (SA versus SST), the known DPW controversy; (c) fully turbulent CFD gives a slightly higher viscous drag than the tripped model.
>
> ## 5. GRIDS (committee family, two-tier admissibility)
>
> - Family: the DPW-6 committee wing-body grids for the deformed alpha = 2.75 geometry, three consecutive levels: Tiny, Coarse, Medium (about 2 M, 6 M, 16 M cells for the half model [verify from the grid page]), in a format the import lane reads: UGRID with patch identity preferred; CGNS through the converter if UGRID is not provided for that family [verify which families provide which format].
> - Admissibility: two-tier standard; quality metrics reported against the grid's own documentation; the maximum non-orthogonality and skewness disclosed beside the bands; patch names, cell counts and face counts round-tripped and hashed.
> - Wall treatment: the committee grids are wall-resolved (y+ about 1); the wall treatment is therefore wall-resolved, no wall functions; y+ per patch reported after the first converged solve.
> - No in-house mesh is built for this act (the lesson from M6: reference grids first).
>
> ## 6. SOLVER AND NUMERICS
>
> - Compressible steady RANS: rhoSimpleFoam (the validation path; DAFoam's DARhoSimpleFoam only if a gradient is later required); Spalart-Allmaras (the workshop's reference closure) as primary, k-omega SST as the registered second closure for the junction-region comparison.
> - Schemes: second-order bounded convection (linearUpwind grad(U) for momentum, bounded for energy and turbulence), limited gradients; pressure-based compressible with the transonic option; relaxation from the class defaults, robust-startup ramp for the first 200 iterations.
> - Boundary conditions: freestream (characteristic-based) on the farfield with the state of section 3; symmetry plane; no-slip adiabatic walls on wing and fuselage.
> - Convergence: residuals below 1e-6 on density and momentum or five orders from the initial, CL and CD stationary within 0.0002 and 0.00002 (two tenths of a drag count) over the last 500 iterations; cap 6,000 iterations per level; solver tolerance strictly tighter than the stationarity gate.
> - Initialization: freestream on Tiny; each finer level initialized from the interpolated coarser solution (continuation), registered.
>
> ## 7. RUN PLAN (32-rank lane, memory reserved 200 GB)
>
> 1. Bug check per the protocol on all three levels: checkMesh with the two-tier disclosure, dictionaries, patch and reference quantities read back, dead-lever audit, forces functionObject reading exactly the wing and fuselage patches with the registered Sref, cref and moment centre, planted force perturbation detected.
> 2. Smoke: Tiny, alpha 2.75, 300 iterations, 8 ranks; predictions: CL rising toward 0.45 to 0.55, CD falling toward 0.02 to 0.03, no negative densities, cost per iteration in band.
> 3. Tiny to convergence (8 ranks), then Coarse (16 ranks), then Medium (32 ranks), each from the interpolated previous solution; observed order and the family band on CL, CD, CM; iterative error 10x smaller than level differences; if the order is out of range the Fine level is registered as a successor with its own cost estimate (about 45 M cells [verify]; node memory checked).
> 4. Secondary closure: SST on Coarse and Medium at alpha 2.75, the junction bubble compared, difference recorded as model-form spread.
> 5. Trim: alpha 2.5 and 3.0 on Coarse, linear interpolation to CL = 0.500, one Medium solve at the interpolated alpha; CD and CM at CL 0.5 reported with the trim disclosed.
> 6. Checkpoints every 30 minutes, last two kept; as ubuntu; detached; memory guard; core gate.
> 7. Stop rules: per the general rules; specific here: CL oscillating with a fixed period on Medium (buffet-like at this alpha is not expected; if it appears, mark, time-average, disclose); junction-region residual plateau is a known feature, not a stop, as long as CL and CD are stationary.
>
> ## 8. DELIVERABLES (the act)
>
> - Forces table: CL, CD (pressure, viscous, total), CM on three levels with the family band, against NTF (primary) and Ames (secondary), with the DPW scatter drawn as the band; the trimmed CL = 0.5 point alongside.
> - Cp overlays at the nine wing rows against the NTF taps, alpha 2.75, Medium level; shock position per row in a table with the measured value and the band.
> - The family figure: CL, CD, CM versus the grid-size measure (N^(-2/3)) with observed order and GCI.
> - Fields: Cp on the upper surface (the shock line across the span), the junction region at the trailing edge (SA versus SST side by side), skin-friction lines showing the separation extent, a symmetry-plane Mach field, the wing-tip vortex.
> - Convergence: residuals and force histories with the stationarity window on each level.
> - Mesh figures: Tiny level shown for legibility with the two-tier disclosure caption (max non-orthogonality, max skewness, leading-edge angle), y+ map on the wing.
> - Compute table: ranks, core-minutes per level, total, wall time.
> - Certificate: references (CRM site data files with their headers, DPW-6 summary page for the scatter), bands and their source, what was not checked (tail, trim by tail, transition, aeroelastic deflection at other alphas, unsteadiness, support interference beyond the header's correction), hashes of geometry, grids, settings and comparator.
>
> ## 9. WHAT THIS ACT DOES NOT CLAIM
> A trimmed aircraft (no tail), transition, flutter or buffet onset, the Fine and Extra-fine levels of the workshop, DPW-7 conditions, or agreement with any participant's result other than through the scatter band.
>
> ## 10. NEXT RUNGS
> Fine level for the band; wing-body-tail with the horizontal tail at iH = 0 for trim; the alpha sweep on the deformed geometries (Case 2 in full); then the same configuration as the adjoint optimization target (multipoint at Mach 0.85 with CM constrained), which is the act Luminary's SHIFT-Wing invites comparison with.

---

**Chief's reading of B and C:** both are cfd's, the propeller on the 16-rank reserve (the instruction has landed, so the reserve is active) and the CRM wing-body on the 32-rank lane. Retrieval into the box is permitted; nothing leaves the box (rule 8). Every fetched document is title-page verified (rule 15) and hashed into its registration before freezing. All run rules of `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` (checkpoints, ubuntu, runner-only launch, one registered change per run, her report format) apply unchanged.

---

## D. LAUNCH ORDER and agent authorisation — byte-exact, ~21:50Z

> yes, so in this order: for dafoam, it immediately launches the fixed D2R.. heat transfer immediately resumes the transient rack. SUBOOF L2 immediately resumes per the allocation above. CFD immediately launches the M6 runs with their nasa commiteee mesh. THen the team proceeds to work on crm and industry propeller, with the allocation explained above, permission to spawn as many agents as needed.

**Chief's reading:** launch order (1) dafoam D6R2 (after its resume-leg proof), (2) heat-transfer K2h transient resume, (3) cfd SUBOFF L2 resume on the 28-rank lane, (4) cfd M6I three levels; THEN cfd starts the CRM wing-body and PPTC propeller acts on their lanes. Lane caps lifted for these acts by her explicit words: "permission to spawn as many agents as needed".

---

## E. Near-gate ruling — byte-exact, ~22:35Z

> 2.2e-5 vs 1e-6 is fine

> ok then for me its a pass. And in general if we are very close to the gate its fine

**Chief's reading:** (1) The D6R2C kill-and-resume proof is PASS on the owner's word at a design-vector difference of 2.227e-05 against a registered 1.0e-06 that was not derived from the solver's tolerance; D6R2 launches. (2) In general: a value very close to its gate does not block proceeding — launching, continuing, filming. The recorded verdict word stays what the frozen gate produces (rule 1: honesty is carried by the value and the word, not by adjectives), the number is printed beside it, and the decision to proceed on a near-miss is hers and is pre-authorised by these words. A near-miss is reported to her as "GATE FAIL by <margin>, proceeding on directive E" — never rewritten as PASS by an agent; only she converts one, as she did here.

---

## F. Agent allocation — byte-exact, 2026-09-13 ~16:30Z

> CRM wing body: goood then it gets launched ASAP. What is the update on ONERA M6 with the nasa mesh ? PROPELLER: since this case has its own allocatedranks, the group of agents in charge of this case need to act ASAP and fix. As i said, since now we only have cfd and dafoam team, permission for cfd to spawn as many agents as needed.  I want at least three agents on propeller, at least three on crm wing body,at least three o drivaer and the other agents work on the rest. these cases must run asap

**Chief's reading:** cfd runs ≥ 3 lanes each on PPTC, CRM wing-body and DrivAer, the rest on M6J/SUBOFF grading; lane cap lifted by her words. DrivAer is NOT parked: its wall-layer defect is fixed and relaunched. Earlier the same hour, hers on DrivAer: "how about the coarse?" — both coarse levels also GATE FAIL on convergence (Cd 0.355 vs 0.276).

---

## G. The published-setup rule — byte-exact, 2026-09-13 ~17:05Z

> The fix, one rule:
>
> For any public case, the lab starts from a published OpenFOAM setup of that case — mesh recipe, layer settings, schemes, wall treatment — ingested into the knowledge base before the first registration. Inventing a setup for a case someone has already run in this solver is refused. DrivAer: Ashton & Revell (OpenFOAM RANS/DES on DrivAer, mesh details published; run transient, time-average). PPTC: Sikirica et al. 2019 (OpenFOAM, snappy, layer settings published). CRM: the OpenFOAM DPW studies (ENGYS/ESI reports) and, critically, the cell-centred variant of the committee grid — a node-centred DPW grid in a cell-centred code has wrong wall spacing and exactly these pyramid problems; check which variant was imported. i think this is the probelm that the lab is starting from scratch everytime where as there are openfoam setups for all of thesecase

**Chief's reading:** a standing rule for every team and every public case: before the first registration, the published OpenFOAM setup (mesh recipe, layers, schemes, wall treatment) is retrieved, title-page verified (rule 15), ingested into the knowledge base as claim → source → gate, and the registration cites it line by line; a setup invented for a case that has a published OpenFOAM setup is refused. Immediate actions: cfd checks whether the imported DPW-6 CRM grids are the node-centred or cell-centred variant (DPW publishes both; OpenFOAM is cell-centred); DrivAer restarts from Ashton & Revell's published setup, run transient and time-averaged; PPTC restarts from Sikirica et al. 2019's snappy and layer settings.

---

## H. Rank reallocation: CRM wing-body parked, propeller lane 48 — byte-exact, 2026-09-13 ~17:15Z

> for now cfd puts the crm full body aside and allocates its ranks to the PPTC. PPTC must use the reference instead of  being from scratch,  [SANAA-DIRECT] Rank reallocation, effective now. CRM wing-body is parked for the package: keep ADDENDUM 16 registered and uncommitted, record the status line "committee grid imported, mesh rung identified, in progress," launch nothing on it. Its 32 ranks move to the propeller lane, which is now 48. PPTC: the moment the mesh passes its gate (zero negative volumes, zero wrong-oriented pyramids, pressure operator SPD), run the design-point family in parallel (coarse 8, medium 16, fine 24 ranks), then the six-point sweep on medium as one wave of six at 8 ranks each, and the full-360 and MRF-zone checks on coarse in the gaps. Everything else in the lane table is unchanged. Report one line per PPTC level as each passes its smoke. but i wan tthe PPTC tonight. Its openfoam treatment is available online so no reason to fail

**Chief's reading:** CRM wing-body PARKED (status line as she wrote it; ADDENDUM 16 registered, uncommitted; nothing launched; the LTS probe is stopped if still running — it is a launch on a parked case). Propeller lane = 48 ranks. PPTC mesh gate = zero negative volumes, zero wrong-oriented pyramids, pressure operator SPD; then coarse/medium/fine design point at 8/16/24 ranks in parallel, then the six-point sweep on medium as one wave of six × 8, full-360 and MRF-zone checks on coarse in the gaps. PPTC starts from Sikirica et al. 2019's published OpenFOAM setup (§G). Deliverable tonight. One line per level as each passes its smoke.

---

## I. Published-setup pointers — byte-exact, 2026-09-13 ~17:45Z

> D6R2: good. PPT AND DRIVAER thats good. Was cfd aware of the following:
>
>
> 2. DrivAer: AutoCFD-class arm is the published practice. Same paper: simpleFoam could not converge on the 128M AutoCFD committee mesh even with first-order schemes, but a 22M snappyHexMesh mesh converged with window averaging, drag within 10% of experiment. Plus two sources with actual case files on disk: the official OpenFOAM HPC Challenge occDrivAer case (snappy, k-ω SST, 65/110/236M, dictionaries public) and Wolf Dynamics' OpenFOAM 9 DrivAer case (coarse and fine, against TUM data).
> Also in the file: the OpenFOAM-wiki M6 case with downloadable files (rhoSimpleFoam + snappy, the Alletto setup), SUBOFF in OpenFOAM v7 with snappy layers (the Type 209 paper) and Robertson's validation, the PPTC OpenFOAM set from last night with the "full 360° in a Cartesian box" consensus, and what to adopt per case.

**Chief's reading:** "the file" is the lab's published-setup research file for these cases (located by grep below, or named by her). cfd adopts per case: DrivAer → the 22 M snappy mesh with window averaging as the published practice, the occDrivAer HPC-Challenge dictionaries and the Wolf Dynamics OpenFOAM 9 case as case files on disk; M6 → the OpenFOAM-wiki Alletto rhoSimpleFoam + snappy case files; SUBOFF → the OpenFOAM v7 snappy-layer setup (Type 209 paper) and Robertson's validation; PPTC → the full-360° Cartesian-box consensus set.

---

## J. Case-file URLs — byte-exact, 2026-09-13 ~17:55Z

> CFD : openfoam hpf files https://develop.openfoam.com/committees/hpc this is openfaom driver https://www.wolfdynamics.com/tutorials.html?id=152 propeller: https://www.cfdsupport.com/potsdam-propeller-benchmark/ but propeller doesn thave a file to download

Immediately before, hers: "Then what was it running ? Ive asked so many times now not to start from scratch and use the public openfoam setups for pptc and drivaer and dafoam. So what was it using if not the publically available openfoam setups ? I KEEP saying i am on a time constraint so we need to use other ppls files"

**Chief's reading:** DrivAer case files come from the OpenFOAM HPC committee repository (develop.openfoam.com/committees/hpc — the occDrivAer case) and the Wolf Dynamics tutorial id=152; retrieved into the box, verified, hashed, and used as the registered setup verbatim. PPTC: the CFD Support Potsdam propeller benchmark page documents a setup but offers no downloadable case; its published settings are read and adopted alongside Sikirica 2019's; the mesh is still built here to those published settings, with the paper-value | our-value table.

---

## K. Per-case ruling — byte-exact, 2026-09-13 ~18:00Z

> so for drivaer, there is file to download, for pptc there is openfoam recipe, for M6 what we were doing is fine and we used nasa mehs, fpor dafoam: mach 0.85 you must use dafoam setup and file if available , and make sure the mesh is checke dduring optimization so we avoid mesh artefacts.

**Chief's reading:** DrivAer = downloaded case files (occDrivAer / Wolf Dynamics), verbatim. PPTC = the published OpenFOAM recipe (CFD Support page + Sikirica 2019), mesh built here to it. M6 = the current route stands: NASA-generator mesh, lab solve, M6J family continues to its fine-level grade. dafoam D6R3 = Mach 0.85, the published DAFoam transonic setup and its case files if available, in-run mesh checks (her rules 6–11) mandatory.

---

## L. D6R3 verbatim; occDrivAer path; PPTC OpenFOAM source — byte-exact, 2026-09-13 ~18:25Z

> 1. dafoam: perfect. Then the dafoam team uses exactly that 3D wing at that mach with those files and what that turorial has and rruns EXACTLY that. 2. Drivaer: it should all be here i thinl https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/system/fvSolution PPTC: sounds good, provided that the paper you reproduce verbatim is an openfoam case. D6R3: for now lets do the verbatim case and reproduce what they have exactl then we can redo wall resolved (but every other in optimization checks remain).

**Chief's reading:** D6R3 = the DAFoam tutorials `CRM_Wing` case run EXACTLY as published (wall functions, single-point CL 0.5 objective as the tutorial has it, its own mesh, FFD, solver settings) — Δ1 resolved as verbatim; the in-optimisation checks (her rules 6–11 as instruments) remain; wall-resolved is a later rerun. The deviation list shrinks to the in-run instruments only; the multipoint objective is NOT applied to this reproduction (she said "runs EXACTLY that"). DrivAer = the occDrivAerStaticMesh case at develop.openfoam.com/committees/hpc/-/tree/develop/incompressible/simpleFoam/occDrivAerStaticMesh (simpleFoam, static mesh), cloned and run verbatim. PPTC = verbatim reproduction only of an OpenFOAM source (Sikirica 2019 is OpenFOAM/snappy; a non-OpenFOAM paper's values are cross-checks only).

---

## M. D6R3 multipoint from the start — byte-exact, 2026-09-13 ~18:35Z

> Dafoam: no lets make itmultipoint from the start, keeping everything else verbatim/ cloned from that case. Multipiint doesnt change the setup it just allows us to look at the optimization under different constraints or conditions, and its moreinteresting.

**Chief's reading:** D6R3 = the DAFoam `CRM_Wing` tutorial cloned verbatim (mesh, extrusion, FFD, wall functions, solver, schemes, optimiser settings) with ONE registered deviation: the multipoint objective — three lift points per her D6R2 instruction (CL 0.4 / 0.5 / 0.6, weights 0.25 / 0.50 / 0.25, lift held at each) — plus the in-run artefact instruments (rules 6–11) as observers/stops and the fresh-mesh confirmation (rule 12) after. Nothing else deviates.

---

## N. DrivAer = Wolf Dynamics case verbatim — byte-exact, 2026-09-13 ~18:50Z

> About the drivaer comment: yes i know the openfoam HPC committteee rep case is steady, that case should land us within 10% of the truth,later once that finishes running and completes well move to the wake resolved one. One second about the drivaer case ill tell u what to do in a sec. And yes we are gonna move to wolf dynamics since its smaller and also gets u to 10% within truth. Ill send the link in a sec

> Here: https://www.wolfdynamics.com/tutorials.html?id=152 and it has both meshes (fine and coarse) and the steup and everythign https://www.wolfdynamics.com/validations/drivAer/tut_drivaer_v2.pdf so must be done verbatim

**Chief's reading:** DrivAer deliverable = the Wolf Dynamics DrivAer tutorial (id=152), which ships both meshes (coarse and fine) and the full setup, plus its validation document tut_drivaer_v2.pdf; run VERBATIM on their meshes with their dictionaries; expected within 10 % of experiment. Order afterwards: the OpenFOAM HPC committee steady case (when its Zenodo mesh is reachable), then the wake-resolved case.

---

## O. Reserved cores — byte-exact, 2026-09-13 ~19:05Z

> yes, and nobody touches or steals the propeller's cores or the drivaer ones. (20) bc i want them

Earlier the same exchange, hers: "the in house is the one we built us ? not the published one? and Ok thats fine if it is close to finishing. But once it finishes, it gets stored and set aside till we look at it and grade it later since wolf dynamics case is provenly good."

**Chief's reading:** the propeller lane's 48 ranks and a DrivAer lane of 20 ranks are RESERVED and never lent, to any team, for any reason; their idle ranks stay idle. The in-house DrivAer arm (R5) finishes its build, is stored and set aside ungraded; the Wolf Dynamics case is the DrivAer line. Lane table now: CRM wing-body parked (0), SUBOFF 28, propeller 48 (reserved), DrivAer 20 (reserved), finalization 20 → total 116 > 96, so the finalization lane (M6J, D6R2/D6R3) yields first when the reserved lanes need their ranks: M6J L1 finishes (~20:10Z) before the propeller family launches; D6R3 sizing must fit what remains.

---

## P. D6R3 abort-ratio deviation authorised — byte-exact, 2026-09-13 ~21:35Z

> yes multipt launches

**Chief's reading (the question she answered, verbatim from the chief's message to her):** "raise DAFoam's abort ratio to 7700 (abort bar 7.7e-05), demoted to job control only, with drag stability, a relative spread under 3e-5 over the last 500 iterations, as the real convergence gate. Hard ceiling registered, never lifted after launch; if the rank sweep shows the floor moves, that is disclosed, not used to lift it." Authorised by Sanaa in her own words. D6R3 multipoint launches at 28 ranks; a forced rank drop is a disclosed discontinuity with no gain claimed across the join.
