# T3 machine contract (heated backward-facing step, Vogel and Eaton 1985 conditions)

Written 2026-08-21 before any case directory existed. Every script in this run
tree (builder, mesh check, runner, marker, comparator) reads or writes exactly
what is stated here. Prose and rationale live in
docs/campaigns/T-family/T3_PREREGISTRATION.md; this file is the contract.

## Physics and numbers

| symbol | value | note |
| --- | --- | --- |
| H | 0.038 m | step height; the value in metres is a scale choice, not a primary-source number; only Re_H, Pr, geometry ratios matter |
| nu | 1.5e-5 m2/s | air |
| Pr | 0.71 | |
| Prt | 0.85 (P_m arm: 1.0) | constant/transportProperties |
| Re_H target | 28000 | based on H and the CORE velocity at x = -3.3H, as the experiment defines it |
| U_in | 10.35 m/s | uniform inlet; predicted core acceleration by displacement to about 11.05 m/s at -3.3H; ACHIEVED U_ref is measured by the comparator |
| T_in | 300 K | fixedValue; TRef in transportProperties is 300 K; beta 0; g (0 0 0) |
| dT/dn heated wall | 1.0e4 K/m | fixedGradient, positive = heating. Passive scalar: its magnitude cannot move St |
| upstream channel height | 4H (y from H to 5H) | |
| downstream channel height | 5H (y from 0 to 5H) | expansion ratio 1.25 |
| L_up | 48H (D_m: 10H) | inlet at x = -L_up; uniform inlet so delta grows naturally to about 1.07H at -3.8H (power law estimate 1.06H) |
| L_down | 30H (O_m: 45H) | outlet at x = +L_down |
| z extent | 0.1H, one cell, empty | 2D |
| endTime | 20000 | deltaT 1, steady SIMPLE |
| writeInterval | 2000 | STRICTLY less than endTime (L-140); purgeWrite 2 |
| solver | buoyantBoussinesqSimpleFoam | OpenFOAM ESI v2606, /usr/lib/openfoam/openfoam2606/etc/bashrc |
| turbulence | kOmegaSST (RAS), constant/turbulenceProperties | C_lam_m: simulationType laminar |

## Cases (8), all serial (nProcs 1)

| case | level | arm | L_up | L_down | Prt | wall treatment |
| --- | --- | --- | --- | --- | --- | --- |
| R_c | coarse | ladder | 48H | 30H | 0.85 | low-Re resolved, target first-cell-centre y+ 1.6 |
| R_m | medium | ladder | 48H | 30H | 0.85 | resolved, y+ 1.0 |
| R_f | fine | ladder | 48H | 30H | 0.85 | resolved, y+ 0.625 |
| P_m | medium | Prt discrimination | 48H | 30H | 1.0 | resolved |
| C_lam_m | medium | Charter 2c trivial baseline, laminar | 48H | 30H | 0.85 (alphat 0) | none |
| W_m | medium counts in x, wall-function wall cells | wall functions | 48H | 30H | 0.85 | nutkWallFunction, kqRWallFunction, omegaWallFunction, alphatJayatillekeWallFunction; first cell 2.10e-3 m (y+ about 30); ny_low 16, ny_up 48 (AMENDED 2026-08-21 before any case existed: the first-written 40/96 cannot fill the halves at a ratio of one or more with a 0.0553H wall cell; 16/48 gives cell-to-cell ratios 1.035 and 1.034 and keeps the core cells comparable to R_m) |
| D_m | medium | thin inlet boundary layer | 10H | 30H | 0.85 | resolved |
| O_m | medium | outlet independence | 48H | 45H | 0.85 | resolved |

## Mesh: three hex blocks, blockMesh, ASCII

Vertices (z = 0 and z = 0.1H): B1 upstream x in [-L_up, 0], y in [H, 5H];
B2 lower downstream x in [0, L_down], y in [0, H]; B3 upper downstream
x in [0, L_down], y in [H, 5H]. Shared vertices (0,H), (0,5H), (L_down,H).

Cell counts per level (coarse / medium / fine), ratio 1.6 nominal per direction:

| direction | c | m | f |
| --- | --- | --- | --- |
| nx_up (B1, 48H) | 100 | 160 | 256 |
| nx_down (B2,B3, 30H) | 200 | 320 | 512 |
| ny_low (B2, H) | 60 | 96 | 154 |
| ny_up (B1,B3, 4H) | 80 | 128 | 204 |

D_m (10H upstream): nx_up 60. O_m (45H downstream): nx_down 480. W_m: same
counts as medium in x but ny_low 16 and ny_up 48 with the wall-function first
cell (amended from 40/96 before any case existed, see the case table).
The effective refinement ratio is computed by the comparator from nCells read
from constant/polyMesh/owner, never assumed.

Gradings (blockMesh multi-grading with the reciprocal written by hand, as the
K0cS ladder does; simpleGrading ratio = LAST cell / FIRST cell along the
block's own direction, L-142):
- y in B2: two-sided, first cell first_cell_wall at y = 0 AND at y = H:
  ((0.5 0.5 r) (0.5 0.5 1/r)) where r is the last/first ratio of a geometric
  half filling 0.5H with ny_low/2 cells starting at first_cell_wall.
- y in B1 and B3: two-sided, first cell first_cell_wall at y = H and y = 5H,
  halves of 2H with ny_up/2 cells each. B1 and B3 MUST share the identical y
  distribution (same counts, same grading) so the interface at x = 0 is
  conformal.
- x in B1: single-sided, finest cell first_cell_x_step = 0.03H touching x = 0
  (so the ratio written is below one), nx_up cells filling L_up.
- x in B2 and B3: single-sided, first cell 0.03H at x = 0, growing downstream,
  nx_down cells filling L_down. B2 and B3 MUST share the x distribution.
first_cell_wall per level: c 1.1213e-4 m, m 7.0083e-5 m, f 4.3802e-5 m
(2 * yplus * nu / u_tau with u_tau = U_ref*sqrt(Cf/2), Cf = 0.003,
U_ref = 11.0526). W_m: 2.1025e-3 m.
Grading ratios are found by bisection (cell-to-cell ratio in [1+1e-9, 2]) so
N geometric cells of the given first cell exactly fill the half or block.

Patches: inlet (patch, x = -L_up), outlet (patch, x = L_down),
upstreamWall (wall, y = H, x < 0), stepWall (wall, x = 0, 0 < y < H),
heatedWall (wall, y = 0, x > 0), topWall (wall, y = 5H), frontAndBack (empty).

## Boundary conditions (0.orig, copied to 0 by the runner)

| field | inlet | outlet | heatedWall | other walls | frontAndBack |
| --- | --- | --- | --- | --- | --- |
| U | fixedValue (U_in 0 0) | inletOutlet, inletValue (0 0 0) | noSlip | noSlip | empty |
| p_rgh | zeroGradient | fixedValue 0 | zeroGradient | zeroGradient | empty |
| T | fixedValue 300 | inletOutlet, inletValue 300 | fixedGradient, gradient 1.0e4 | zeroGradient | empty |
| k | fixedValue 1.5*(0.02*U_in)^2 | inletOutlet | kLowReWallFunction (W_m: kqRWallFunction) | same | empty |
| omega | fixedValue sqrt(k_in)/(0.09^0.25 * 0.07 * 4H) | inletOutlet | omegaWallFunction | same | empty |
| nut | calculated 0 | calculated 0 | nutLowReWallFunction (W_m: nutkWallFunction) | same | empty |
| alphat | calculated 0 | calculated 0 | calculated 0 (W_m: alphatJayatillekeWallFunction, Prt) | same | empty |

C_lam_m writes the same files; k, omega, nut are still written (harmless) but
turbulenceProperties is laminar. alphat is owned by the solver and is written
regardless of model.

fvSchemes: steadyState; grad Gauss linear; div(phi,U) bounded Gauss
linearUpwind grad(U); div(phi,T) / div(phi,k) / div(phi,omega) bounded Gauss
limitedLinear 1; div((nuEff*dev2(T(grad(U))))) Gauss linear; laplacian Gauss
linear corrected; snGrad corrected; wallDist meshWave.
fvSolution: p_rgh PCG DIC tol 1e-11 relTol 0.001; U T k omega PBiCGStab DILU
tol 1e-11 relTol 0.01; SIMPLE nNonOrthogonalCorrectors 0, pRefCell 0,
pRefValue 0, NO residualControl (the case runs to endTime; convergence is
judged from written fields, L-141); relaxation p_rgh 0.3, U 0.7, T 0.7,
k 0.7, omega 0.7.
controlDict: startFrom latestTime; endTime 20000; deltaT 1; writeControl
timeStep; writeInterval 2000; purgeWrite 2; ascii; writePrecision 16;
runTimeModifiable false; no functions block.

## CASE.txt (key value per line, written by the builder, read by everything)

case rung level arm model wall_treatment target_yplus H nu Pr Prt Re_target
U_in T_in dTdn_wall L_up_H L_down_H nx_up nx_down ny_low ny_up
first_cell_wall first_cell_x_step endTime writeInterval nCells_design
predicted_core_s (nCells_design*endTime/4.0e5)

## Files and markers

- log.blockMesh, log.checkMesh (build), log.checkMesh (re-run by runner),
  log.solve, STATUS.<case> with "rc= wall= checkMesh_rc=" written by the
  runner beside the case directories, DONE.<case> written only by
  mark_done_t3.py, LAUNCH_LOCK/ inside the case written by launch_t3.sh.
- check_t3_mesh.py reads constant/polyMesh/points ONLY and asserts, per case:
  (A) the cell touching y = 0 on the heated wall equals first_cell_wall to
  0.2 %; (B) it is the SMALLEST y-cell in [0, H] and the cell touching y = H
  from below equals it; (C) the cell touching y = 5H equals first_cell_wall
  and is the smallest in [H, 5H]; (D) the y-cells sum to H and to 4H; (E) the
  x-cell touching x = 0 on both sides equals first_cell_x_step to 0.2 % and is
  the smallest x-cell on its side; (F) the per-direction ratios are geometric
  to 1e-6 relative within each graded half. It prints a table and returns 1 on
  any failure. Reads CASE.txt for the design values.
- mark_done_t3.py: six tests as mark_done_t1b.py: STATUS rc=0; an End line in
  log.solve; last time directory == endTime; fields T U p_rgh alphat phi
  present (plus nut k omega when turbulenceProperties says RAS);
  ExecutionTime line count == endTime; every field in the final directory
  newer than the case's own 0/T. Never writes a marker otherwise.
- launch_t3.sh / run_one_t3.sh: guards G1 (atomic LAUNCH_LOCK), G2 (no
  process with cwd == case dir, identified by readlink /proc/pid/exe),
  G3 (no numeric time directory other than 0); copies 0.orig to 0 (writing
  0/T last so its mtime dates the run); setsid nohup detach; checkMesh then
  solver; STATUS written at the end. Nothing here ever kills a process.
