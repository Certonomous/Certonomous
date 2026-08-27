# F26_RINGLEB — SOLVER ADMISSION ARM, 2026-08-27 (cfd lane C)

**STATUS: F26 IS NOT FROZEN AND IS NOT LAUNCHABLE. NO QUEUE ENTRY EXISTS AND NONE MAY BE WRITTEN
FROM THIS STATE.** Nothing below is a gate, threshold, cap or label; every number is a
registration-time instrument reading on a scratch grid, not a result. `verification/runs/F26_RINGLEB_runs`
is ABSENT (checked 2026-08-27, see §6). Nothing is sent, filed, uploaded or submitted (rule 7).

This record exists because the pre-registration's §2 decision — *register F26 on `rhoSimpleFoam`* — was
tested before freezing, as CLAUDE.md rule 2 and L-346 require, and **it did not survive the test**.
It lives under the case directory, not in scratch (rule 13 / L-186).

## 1. What was completed and is sound

- **`rhoSimpleFoam` conversion of the case.** `case/system/{fvSchemes,fvSolution,controlDict.template}`
  rewritten for pressure-based steady SIMPLE; `case/0/{p,T,U}.template` rewritten to the
  characteristically-counted 2-D subsonic Euler set (subsonic inflow takes three conditions — `U` and
  `T`; subsonic outflow takes exactly one — `p`); `build_f26.py` converted so the time axis is the
  SIMPLE iteration index (`deltaT 1`, `endTime` = the level's iteration count), which makes rule 4's
  *last time == endTime* read *every registered iteration ran*. `exact_f26.LEVELS` moved to
  384x64 / 768x128 / 1536x256 (24,576 / 98,304 / 393,216 cells).
- **The mesh and the exact solution are verified consistent, independently of any solver.** The exact
  Euler fluxes were evaluated at the built mesh's own face centres and summed over each cell
  (midpoint quadrature, `knp_f26.geometry`); the volume-weighted L2 of the resulting cell residual is

  | grid | cells | L2 mass | L2 x-mom | L2 y-mom | L2 energy | ratio (mass) |
  |---|---|---|---|---|---|---|
  | 48x8    |    384 | 4.087e-05 | 6.402e-05 | 4.957e-05 | 1.022e-04 | — |
  | 96x16   |  1,536 | 1.029e-05 | 1.604e-05 | 1.242e-05 | 2.573e-05 | 3.97 |
  | 192x32  |  6,144 | 2.578e-06 | 4.012e-06 | 3.107e-06 | 6.445e-06 | 3.99 |
  | 384x64  | 24,576 | 6.448e-07 | 1.003e-06 | 7.768e-07 | 1.612e-06 | 4.00 |
  | 768x128 | 98,304 | 1.612e-07 | 2.508e-07 | 1.942e-07 | 4.030e-07 | 4.00 |

  **Exactly second order, ratio 4.00 per doubling over five levels.** The geometry is likewise clean:
  at the inflow the exact `u.n/|U|` is -1.00000 at every face and at the outflow +1.00000 at every
  face; on both streamline walls `|u.n|/|U| <= 8e-5`. checkMesh gives max non-orthogonality
  0.0168 deg (48x8) falling to 0.0011 deg (192x32), max skewness <= 0.013, max aspect ratio <= 1.31.
  **Whatever fails below, it is not the mesh and not the exact solution.**

## 2. The finding: no solver configuration holds this flow at ladder resolutions

Twenty-one configurations were driven on scratch instrument grids. Every one either aborted or
settled into a limit cycle at 1-70 % density error. `rc=136` is SIGFPE, `rc=134` a FOAM abort.

| # | solver | boundary set | convection | outcome |
|---|---|---|---|---|
| 1 | rhoCentralFoam, time-accurate | exact Dirichlet ends, slip walls | vanLeer | SIGFPE step 648 *(prereg §2, prior lane)* |
| 2 | rhoCentralFoam, time-accurate | characteristically counted | vanLeer | no divergence, no convergence; E2(rho) drifts to 0.12 *(prereg §2, prior lane)* |
| 3 | rhoSimpleFoam SIMPLEC, transonic | counted | linearUpwind | SIGFPE it. 103 (96x16); it. 166 (192x32) |
| 4 | rhoSimpleFoam SIMPLE 0.3/0.7/0.7 | counted | linearUpwind | SIGFPE it. 113 |
| 5 | rhoSimpleFoam SIMPLEC 1/0.5/0.5 | counted | linearUpwind | SIGFPE it. 191 |
| 6 | rhoSimpleFoam, transonic **no** | counted | linearUpwind | abort it. 9 |
| 7 | rhoSimpleFoam SIMPLE 0.2/0.5/0.5 | counted | linearUpwind | SIGFPE it. 244 |
| 8 | rhoSimpleFoam SIMPLE 0.05/0.2/0.2 | counted | linearUpwind | SIGFPE it. 1140 |
| 9 | rhoSimpleFoam SIMPLEC | exact Dirichlet on all four | linearUpwind | negative T it. 3356 (96x16), 2358 (192x32); residual limit-cycles 2e-3..6e-3 |
| 10 | rhoSimpleFoam | exact Dirichlet on all four | bounded upwind | rc 0, 4000 it., **E2(rho) limit-cycles 1.4e-2..1.8e-2, max abs entropy ~1.0** |
| 11 | rhoSimpleFoam | exact Dirichlet on all four | limitedLinear 1 | abort it. 111 |
| 12 | rhoSimpleFoam heavy relax | exact Dirichlet on all four | linearUpwind | abort it. 51 |
| 13 | rhoSimpleFoam | exact Dirichlet on all four | unbounded upwind | rc 0, residual limit-cycles 2e-3..1e-2 |
| 14 | rhoPimpleFoam **LTS** (localEuler) | exact Dirichlet on all four | linearUpwind | max abs rho error 1.62 by it. 200; abort it. 352 |
| 15 | rhoCentralFoam **LTS** | counted | vanLeer | SIGFPE it. 9764; E2(rho) 0.18..0.69 |
| 16 | rhoCentralFoam **LTS** | counted | upwind (1st order) | rc 0, 20,000 it., **E2(rho) limit-cycles 0.12..0.30** |
| 17 | rhoCentralFoam **LTS** | exact Dirichlet on all four | vanLeer | SIGFPE it. 270 |
| 18 | rhoCentralFoam **LTS** | exact Dirichlet on all four | upwind | SIGFPE it. 106 |
| 19 | rhoSimpleFoam, short duct (PHI_END 0.8) | counted | linearUpwind | rc 0, E2(rho) 0.22..0.70 |
| 20 | rhoSimpleFoam, short duct | counted | bounded upwind | abort it. 570 |
| 21 | rhoPimpleFoam implicit Euler, dt 0.5 (acoustic CFL ~5), 3 outer correctors | counted | upwind | rc 0, 2000 steps, **E2(rho) 0.42 and still growing** |
| 22 | rhoCentralFoam, time-accurate, **waveTransmissive** (non-reflecting) outlet | counted + NRBC | vanLeer | SIGFPE step 19,142; E2(rho) grows monotonically to 0.81 |

Three mechanisms were tested and **eliminated**: the mesh and exact solution (§1, exactly 2nd order);
the thermophysical inversion (`hConstThermo` + `perfectGas` + `sensibleInternalEnergy` gives
`Es = Cv T`, linear in T, so the Newton solve in `species::thermo::T` — relative tolerance `T0*1e-4`,
`thermo.C:33` — terminates exactly and injects no noise floor); and duct length (row 19-20: the
shortened duct is *worse*, not better).

## 3. The disqualifying measurement — the stability threshold and the error floor

Starting from the exact field at every level, `rhoSimpleFoam` with the counted boundary set and
`bounded Gauss linearUpwind` converges to a machine-level residual **only below about 600 cells**:

| grid | cells | final p initial residual | E2(rho) at 4000 it. | E2(entropy) |
|---|---|---|---|---|
| 42x7 |   294 | 7.699e-13 | 1.209380e-01 | 1.460893e-01 |
| 48x8 |   384 | 1.198e-12 | 1.057401e-01 | 1.287290e-01 |
| 54x9 |   486 | 1.178e-12 | 9.893176e-02 | 1.209176e-01 |
| 60x10 |  600 | 9.847e-11 | 9.022515e-02 | 1.106585e-01 |
| **72x12** | **864** | — | — | **ABORT at it. 794** |
| **96x16** | **1,536** | — | — | **SIGFPE at every relaxation down to p 0.05 / U 0.2 / e 0.2** |

**The stability threshold lies between 600 and 864 cells** — two and a half orders of magnitude below
the registered fine level of 393,216 cells. This is L-346's pathology in its purest form: the coarse
level converges beautifully and tells you nothing whatever about the fine level.

**The L-345 pre-freeze model check, run on the only three levels that converge** (294 / 384 / 486
cells, `scripts/roache_triple.py`, `form="unequal"`, dim 2, r21 = 1.125000, r32 = 1.142857):

- `E2(rho)`: state **CONVERGING**, monotone, apparent order 5.3544, **Richardson limit 9.118e-02**, GCI 9.79 %
- `E2(entropy)`: state **CONVERGING**, monotone, apparent order 5.3198, **Richardson limit 1.1195e-01**, GCI 9.27 %

The state word is `CONVERGING`, but read what it is converging *to*. These are ERROR norms against an
exact solution: a consistent discretisation must drive them to **zero**. The triple extrapolates them
to **9.1e-2 and 1.1e-1**. Fitted instead as a pure power law to zero, the apparent order in h wanders
0.565 (48->54), 0.799 (42->54), 1.006 (42->48) — no stable order exists. On either reading the
configuration does not converge to the exact Ringleb solution: it saturates about **9 % away in
density**. A ladder built on it would return `GATE FAIL` at every level it survived, and
`NOT A RESULT` at the two levels that matter.

## 4. Verdict

**BLOCKED.** F26_RINGLEB cannot be frozen. Freezing it would register a three-level ladder whose
medium and fine levels cannot be run at all and whose coarse level is 9 % from the exact answer —
precisely the ungradeable registration the lane brief forbids.

The capability-grid cell **2D · steady · subsonic-compressible (`docs/capability/cfd_GRID.md`, grid
068c2bf0)** remains *not attempted*. What this arm establishes about it is narrower and firmer than a
failed ladder would have been: **OpenFOAM v2606's compressible solvers, at `mu = 0`, cannot hold a
strongly-curved inviscid subsonic duct flow at verification resolutions on this box.** Which of the
three constituents — zero viscosity, strong wall curvature, or high subsonic Mach — carries the
failure is not resolved here and is the obvious next question.

## 5. Cost

Scratch arm, all serial (1 rank), summed `ExecutionTime` over 27 solver logs: **172.17 wall s =
2.87 core-min**, plus 19 blockMesh/checkMesh/postProcess builds at roughly 1 core-min, so
**about 3.9 core-min total**, against the 5 core-min the brief allowed. Not a level, not retained,
not a result. Basis: measured from the logs' own `ExecutionTime` lines. Dollars are not quoted; at
the owner-stated $0.0513/core-h this is under $0.01 and the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **No run root was created and no ladder level was ever built.**

## 6. Absence condition

`test -e /home/ubuntu/Certonomous/verification/runs/F26_RINGLEB_runs` -> **ABSENT**, checked
2026-08-27 (stamp in the commit message). No `RC.txt`, `log.*` or numeric time directory exists
anywhere under `cases/F26_RINGLEB/`. `run_f26.sh`, `grade_f26.py` and
`queue_entry_F26_RINGLEB.json` **were deliberately not written**: a launcher and a grader for a case
that cannot produce a number would manufacture the appearance of readiness.
