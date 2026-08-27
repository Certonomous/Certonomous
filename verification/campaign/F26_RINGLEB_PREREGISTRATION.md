# F26 — PRE-REGISTRATION (DRAFT — NOT FROZEN, NOT LAUNCHABLE): Ringleb flow, 2-D steady subsonic-compressible, exact hodograph solution on an orthogonal flow-net mesh

**STATUS 2026-08-26T23:30Z: DRAFT — NOT FROZEN, NOT LAUNCHABLE. No queue entry exists and none may be written from this state.
Committed as an IN-PROGRESS record under Sanaa's order (verbatim via the chief): "EVERYBODY commits everything before we run out
of credits". Nothing below is a gate, threshold, cap or label; every number is a registration-time instrument reading, not a result.**

**Team:** cfd. **Case id:** `F26_RINGLEB`. Zero core-minutes spent in any run root; `verification/runs/F26_RINGLEB_runs` is ABSENT.
Decided and recorded **`[lab-attributed]`** (chief addenda `73eccb1b`, `7def3c6b`, `3c3ef86c`; permission `bc0e687e`).

**Capability-grid cell (068c2bf0): 2D · steady · subsonic-compressible.** (`docs/capability/cfd_GRID.md` row: *not attempted*.)

## 1. What exists at this commit (all under `cases/F26_RINGLEB/`)

- `exact_f26.py` — the exact solution in its standard hodograph form (no Ringleb reference exists on this box: `docs/papers/`
  and `docs/standards/` searched; `High_order_grid_convergence.pdf` is Ekaterinaris 2005 and carries no Ringleb section).
  `--selftest` rc 0, 6.4 s: the closed form substituted into the steady Euler equations through the hodograph Jacobian
  gives continuity **simplified symbolically to 0** and continuity / x-momentum / y-momentum / vorticity residuals
  **< 1e-40 at 40 digits** at 60 random points; a planted 1.1 gamma in rho breaks them (residuals O(1e-2)); the
  hodograph inversion (x, y) -> (V, theta) **round-trips 10^4 random (V, psi) points to 2.9e-15** (registered tolerance
  1e-12); the analytic grad V agrees with a finite difference of the inversion to 6e-10.
  Domain: streamlines psi = 1/0.5 (outer wall) and 1/0.8 (inner wall), equipotential ends phi = -/+ 2.4 (flow NORMAL to the
  ends). **Max Mach in the domain 0.8567** (inner wall at the turn); inflow M 0.334–0.399. ENTIRELY SUBSONIC.
- `knp_f26.py` — a numpy re-implementation of rhoCentralFoam's Kurganov/vanLeer/vanLeerV/Euler step on the general
  owner–neighbour mesh. **Matches rhoCentralFoam's first step on the 48x8 scratch mesh to 1.1e-12 in rho, 1.2e-12 in u,
  2.1e-12 in v, 1.1e-12 in p, 7.5e-13 in T** (the solver's 12-digit ascii write). Provides the mesh geometry the builder
  cross-checks against `0/C`, `0/V`.
- `build_f26.py`, `foam_io_f26.py`, `case/` — blockMesh builds the unit-square TOPOLOGY, the builder REMAPS
  `constant/polyMesh/points` through the exact flow-net map (every node snapped to `exact_f26.lattice`), checkMesh gates.
  Scratch 48x8 (384 cells, NOT a level): **`Mesh OK`, max non-orthogonality 0.0168 deg (gate 70), max skewness 0.0129
  (gate 4), max aspect ratio 1.27**; `0/C` and `0/V` equal the model geometry to 5.0e-12 / 5.0e-14.
  **The case dictionaries at this commit are the rhoCentralFoam set and are SUPERSEDED by §2's finding.**

## 2. Registration-time FINDING — rhoCentralFoam cannot be pseudo-time-marched to this steady subsonic state

Real solver, scratch 48x8, exact initial field, exact-Dirichlet inflow/outflow (p, T, U), `slip` walls, fixed dt at
solver-convention max Co 0.200: **floating-point exception at step 648 (t = 13.8), 1.7 s wall (≈ 0.03 core-min, the only
solver compute spent; not retained; not a result).** The model reproduces it (NaN at t = 13.8 at Co 0.2 AND at Co 0.05;
t = 14.2 on 96x16): the blow-up time is the convective transit time, independent of resolution and dt. Mechanism (fields
rendered from the checkpoints): the slip / zeroGradient-p wall on the strongly curved inner streamline generates an O(h)
entropy (loss) layer that convects to the outflow corner; a fully fixed outflow is over-specified by one characteristic
and diverges there. With the correctly-counted set (inflow U, T fixed / p zeroGradient; outflow p fixed / U, T
zeroGradient) nothing diverges but nothing converges: the checkpoint residual stays 2e-3–4e-2 and E2(rho) drifts to
0.12 by t = 640 (48x8). An exact fixedGradient wall pressure does not change either behaviour. **Straight-channel control:**
a 1 % isentropic pulse in a uniform M 0.52 channel with the correctly-counted reflective ends **does not decay at all over
20 acoustic transits** (RMS 1.5e-3–2.5e-3 at Nx = 48, 96, 192): the central scheme provides no damping of trapped smooth
acoustic energy and every local Dirichlet/Neumann end is reflective. rhoCentralFoam (explicit, time-accurate, no
non-reflecting boundary for a non-uniform state, no local time stepping) is therefore NOT the tool for this cell.

**Decision `[lab-attributed]`:** register F26 on **`rhoSimpleFoam`** (pressure-based steady SIMPLE; real `Ux/Uy/e/p`
initial residuals for a rule-5 limb-1 census as F23; `bounded Gauss linearUpwind` convection), inflow U, T fixedValue exact
/ p zeroGradient, outflow p fixedValue exact / U, T zeroGradient, walls `slip` / zeroGradient. The capability grid's own row
names rhoSimpleFoam/rhoPimpleFoam as the missing solvers for this cell. NOT DONE at this commit.

## 3. What is NOT done (this is why the state is a DRAFT)

rhoSimpleFoam dictionaries and templates; the prediction model for the SIMPLE discretisation (planned: the same solver on
sub-ladder instrument grids 48x8 / 96x16 / 192x32 inside the ≤ 1 core-min smoke budget, extrapolated with the observed
order; a DEGENERATE prediction is a registration defect); ladder sizing (planned 384x64 / 768x128 / 1536x256, 4 ranks,
fine ≥ 300 core-min, cap ≤ 1500, iteration count sized from the measured convergence rate so the fine level's iterative
floor sits well below its predicted discretisation error — F17b's lesson); `grade_f26.py` (one `RT.grade_ladder` call,
0 asserts, planted-zero controls both ways, Class C plateau, gate demonstration), `run_f26.sh` (`set +u` around the bashrc,
`--preflight`, cap projected/checked, HALT exit 3), the queue entry. Gates planned: G-F26-1 L2 density error vs exact over
the domain; G-F26-2 L2 entropy error against the absolute reference 0 (homentropic exact flow).

## 4. Absence condition and never-run evidence

`test -e /home/ubuntu/Certonomous/verification/runs/F26_RINGLEB_runs` -> ABSENT at 2026-08-26T23:30Z. No `RC.txt`, `log.*` or
numeric time directory exists under `cases/F26_RINGLEB/`. Nothing is sent, filed, uploaded or submitted (rule 7).

---

## 5. DATED SECTION 2026-08-27T16:48:42Z — §2's rhoSimpleFoam decision was TESTED and DID NOT SURVIVE. STATUS: BLOCKED.

**This document remains a DRAFT. It was never frozen, it is not frozen now, and it is NOT LAUNCHABLE.
No gate, threshold, cap or label has ever been set in it, so nothing here can be an amendment to one.
No queue entry exists and none may be written from this state.** Nothing is sent (rule 7).

§2 above decided `[lab-attributed]` to register F26 on **`rhoSimpleFoam`**. That decision was
implemented in full — dictionaries, characteristically-counted boundary set, builder converted to the
SIMPLE iteration axis, ladder moved to 384x64 / 768x128 / 1536x256 — and then **tested before freezing**,
as CLAUDE.md rule 2 and L-346 require. It failed. The complete evidence, with every number and its
artifact, is **`cases/F26_RINGLEB/SOLVER_ADMISSION_ARM_2026-08-27.md`**; the three findings that
decide the matter are:

1. **The mesh and the exact solution are sound and are not the problem.** The exact Euler fluxes summed
   over each cell of the built mesh give an L2 cell residual that falls by exactly 4.00 per doubling
   across five grids (4.087e-05 at 48x8 to 1.612e-07 at 768x128) — clean second order.
2. **No solver configuration holds this flow at ladder resolutions.** Twenty-two configurations across
   `rhoSimpleFoam`, `rhoPimpleFoam` (including LTS and implicit pseudo-transient at acoustic CFL ~5)
   and `rhoCentralFoam` (including LTS and a non-reflecting `waveTransmissive` outlet), spanning both
   boundary sets, both convection orders and relaxation from 1.0 down to 0.05, either abort or settle
   into a limit cycle at 1-70 % density error.
3. **The stability threshold is between 600 and 864 cells, and even below it the error saturates near
   9 %.** `rhoSimpleFoam` reaches a machine-level residual (7.7e-13 to 9.8e-11) at 294 / 384 / 486 / 600
   cells and aborts at 864 and 1,536. The **L-345 pre-freeze model check** on the three converged levels
   (`scripts/roache_triple.py`, unequal form, dim 2, r21 1.125000, r32 1.142857) returns state
   **CONVERGING** for both candidate gate quantities — but their Richardson limits are **9.118e-02** for
   E2(rho) and **1.1195e-01** for E2(entropy), not zero. These are error norms against an exact
   solution; a consistent scheme drives them to zero. Read instead as a power law to zero, the apparent
   order in h wanders 0.565 / 0.799 / 1.006 and no stable order exists.

**Verdict: BLOCKED.** The registered fine level (393,216 cells) is two and a half orders of magnitude
above the stability threshold. A ladder frozen on this configuration would return NOT A RESULT at its
medium and fine levels and GATE FAIL at its coarse level. `run_f26.sh`, `grade_f26.py` and the queue
entry were deliberately **not written**: a launcher and a grader for a case that cannot produce a number
would manufacture the appearance of readiness.

The capability-grid cell **2D · steady · subsonic-compressible** (`docs/capability/cfd_GRID.md`, grid
068c2bf0) therefore remains **not attempted**.

**Absence condition, re-checked:** `test -e /home/ubuntu/Certonomous/verification/runs/F26_RINGLEB_runs`
-> **ABSENT at 2026-08-27T16:48:42Z**. Zero core-minutes have been spent in any run root. The scratch admission arm cost
**2.87 core-min of solver time** (172.17 wall s summed over 27 serial logs' own `ExecutionTime` lines)
plus about 1 core-min of meshing — roughly **3.9 core-min**, against the 5 core-min allowed, disclosed
here and in the arm record. Not a level, not retained, not a result.
