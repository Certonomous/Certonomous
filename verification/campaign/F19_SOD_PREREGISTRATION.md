# F19 — PRE-REGISTRATION: Sod shock tube (rhoCentralFoam, 1-D, Toro Test 1)

**Team:** cfd. **Written before any compute. ZERO CORE-MINUTES SPENT in the case
tree or any run root.** **Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** under
Sanaa's standing order that the cfd queue is kept deep with pre-registered,
costed cases (chief commits `73eccb1b`, `7def3c6b`, `0b041d1a`; permission
`bc0e687e`). Template in structure and rigour: F18 (`c4f72b27`).

---

## 1. WHY THIS CASE

A **discontinuous** exact solution of the 1-D Euler equations: left rarefaction,
contact, right shock. It sits beside F18 (smooth, incompressible, periodic) and
F15/F4S (steady compressible) so the lab's `rhoCentralFoam` line is asked to
recover a known answer with a shock **and** the L1 order that a limited
second-order central-upwind scheme actually delivers on it — which is **not 2**.
**Case-selection charter:** an **`instrument-check`** (`CASE_SELECTION_CHARTER.md`
§3), labelled so at registration; not a result, counts toward no challenge
column, not filmed.

## 2. THE CASE

    x in [0, 1], diaphragm x0 = 0.5, gamma = 1.4, t_end = 0.2
    left  (x < 0.5): rho = 1,     u = 0, p = 1
    right (x > 0.5): rho = 0.125, u = 0, p = 0.1

| item | value |
|---|---|
| gas | nondimensional perfect gas, **R = 1** (`molWeight 8314.47006650545` = OpenFOAM v2606's `RR = 1e3·NA·k`, NA = 6.0221417930e+23, k = 1.38065e-23), **Cp = 3.5 → γ = 1.4**, `Tref 0`, `Hsref 0`, `Hf 0`, `mu 0` (inviscid), `Pr 1`; `hePsiThermo / hConst / perfectGas / sensibleInternalEnergy` |
| initial field | exact t = 0 states at the built mesh's own cell centres (from `0/C`): `0/p`, `0/T` = p/ρ, then `0/U = (0 0 0)` written **last** |
| solver | `rhoCentralFoam`, **exactly the shipped shockTube tutorial's schemes** (`/usr/lib/openfoam/openfoam2606/tutorials/compressible/rhoCentralFoam/shockTube/system/fvSchemes`): `fluxScheme Kurganov`; `ddtSchemes Euler`; `gradSchemes Gauss linear`; `div(tauMC) Gauss linear`; `laplacianSchemes Gauss linear corrected`; **`reconstruct(rho) vanLeer`, `reconstruct(U) vanLeerV`, `reconstruct(T) vanLeer`**; `snGradSchemes corrected`; `fvSolution` as the tutorial (`diagonal` for rho/rhoU/rhoE) |
| time step | **fixed** (`adjustTimeStep no`), refined with h; classical Courant S_max·Δt/h = **0.1753** at every level (S_max = 2.1916 = u* + a*_R); the solver's own `max Courant Number` is **half** that (**0.0877** developed; 0.0473 at step 1 when u = 0) because `centralCourantNo.H` sums `amaxSf = (|u|+c)/2` per face |
| mesh | uniform, **one cell in y and z** (extent 0.0025 each: aspect ratio 1 at coarse, 4 at fine); `left`/`right` **`zeroGradient`** (no wave reaches either boundary: shock at 0.8504, rarefaction head at 0.2634 at t = 0.2); the four y/z faces **`empty`** |
| output | fields (`rho U p T`) at `endTime` only |

**Why `empty` y/z faces are CORRECT here and were F16's defect there.** An
`empty` patch removes its normal velocity component from the solve. In F16 the
±x faces were `empty` and x was the component the oscillating wall **drove**, so
the driven flow was deleted (`F16b_SL2_PREREGISTRATION.md` §1). Here the removed
components are y and z, which the exact solution holds **identically zero**; the
solved component x is normal to the `zeroGradient` `left`/`right` patches, not
to an `empty` one. The smoke arm (§8) shows Ux moving and Uy = Uz = 0 exactly.

**Mesh admissibility (MESH_STANDARD §3, §8.1):** the coarse level was **BUILT AND
`checkMesh`'d** on a scratch copy before this freeze — 400 cells, max
non-orthogonality **0°** against the 70° gate, max skewness 2.7e−13 against 4,
`Mesh OK`; `build_f19.py` enforces both gates at every level and writes
`MESH_LINE.txt` from the built mesh.

## 3. THE REFERENCE IS **NOT A PAPER**. IT IS AN EXACT RIEMANN SOLVER — AND IT IS CHECKED NON-CIRCULARLY

Rule 15 requires title-page verification of every **retrieved** paper; this case
retrieves none. `exact_f19.py` implements Toro's exact Riemann solver (Newton on
f(p) = f_L + f_R + Δu from the PVRS guess). At selftest:

- **Own iteration vs textbook:** 6 Newton iterations, residual 1.1e−16; derived
  **p\* = 0.30313018, u\* = 0.92745262, ρ\*_L = 0.42631943, ρ\*_R = 0.26557371**
  against Toro, *Riemann Solvers and Numerical Methods for Fluid Dynamics*, Table
  4.3 Test 1 (**p\* = 0.30313, u\* = 0.92745, ρ\*_L = 0.42632, ρ\*_R = 0.26557** —
  the textbook's five-decimal figures), tolerance 6e−6. Shock speed **S =
  1.752155732**, exact shock position at t = 0.2: **x_s = 0.850431146**.
- **Non-circular integral identities on the four-wave profile**, which never
  touch the textbook figures: total mass **0.5625** (to 1e−12), momentum
  **0.18000000** (= (p_L − p_R)·t, to 1.5e−9), energy **1.37500000** (to 1.4e−9);
  Rankine–Hugoniot mass flux ρ(u − S) equal on both sides of the shock
  (−0.21901946650377 both, to 1e−16); p/ρ^γ constant to 2.2e−16 inside the fan;
  the analytic cell-average integrator vs a 20,000-point brute-force midpoint sum:
  8.6e−12 on every cell without a jump, 3.8e−6 on the two jump cells (the brute
  force's own limit Δρ/N_sub, stated as such).
- **Planted control:** p_R raised 10 % moves p\* to 0.311888; γ = 5/3 moves it to
  0.293945 — the solver is shown able to answer differently.

## 4. THE LADDER — THREE LEVELS (§9.1), `dim = 1`

Uniform cells; **h and Δt both refine by exactly 2** at constant Courant number
(checked; a departure refuses). r = 2.000 from cell counts.

| level | cells | h | steps | Δt | E1(T) predicted | x_s predicted | x_s error predicted |
|---|---|---|---|---|---|---|---|
| coarse | 400 | 2.5e−3 | 1000 | 2.0e−4 | 1.405768e−03 | 0.850756 | +3.251e−04 (0.13 h) |
| medium | 800 | 1.25e−3 | 2000 | 1.0e−4 | 7.593106e−04 | 0.850649 | +2.179e−04 (0.17 h) |
| fine | 1600 | 6.25e−4 | 4000 | 5.0e−5 | 4.400280e−04 | 0.850540 | +1.084e−04 (0.17 h) |

All three levels are **integrated** by the model (nothing extrapolated). Model
orders: **0.889 (coarse→medium), 0.787 (medium→fine)**.

**DECOMPOSITION SEED (required field): `none`.** Every level **serial on 1
rank**; `decomposePar` never invoked; no partition, no RNG.

## 5. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to a prediction computed
from the scheme. Declared now; not measured on the case, not fitted, not revisable.

**The derivation.** `exact_f19.py::knp_model` is a numpy re-implementation of
rhoCentralFoam's discretisation (read from
`applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C` and
`src/finiteVolume/.../NVDTVD.H`, `vanLeer.H` of the installed v2606): directed
vanLeer reconstruction of ρ, ρU, rPsi = RT, e and c to faces with OpenFOAM's ratio
r = 2(d·∇_c φ)/(φ_N − φ_P) − 1 and its 1000× clamp; the Kurganov weights `ap`,
`am`, `a_pos = ap/(ap − am)`, `aSf = am·a_pos`; the fluxes `phi`, `phiUp`,
`phiEp` exactly as formed there; explicit Euler update of ρ, ρU, ρE; primitive
update. Integrated on the **same three grids at the same Δt** the ladder runs.
Controls: the model conserves mass to 1e−10, its own solver-convention max
Courant (0.0900) agrees with the registered 0.0877 to 0.02, its L1 error is
monotone decreasing with orders in [0.5, 1.5].

**What the model omits, so the factor-3 window is an admission:** `vanLeerV`'s
projection form (identical to the scalar form in 1-D); boundary treatment (no
wave reaches a boundary); floating-point ordering; the solver's own `psi`/`p`
boundary update sequence.

**G-F19-1 — L1 density error at t = 0.2**

    E1(T) = mean over cells |ρ_h − ρ̄_exact|,  ρ̄_exact = exact CELL AVERAGE (analytic, split at the four waves)

Prediction at the fine level: **4.400280e−04**.
**Band = [prediction/3, prediction×3] = [1.466760e−04, 1.320084e−03].**
**This is a VALUE band and does not depend on the observed order.**

**G-F19-2 — shock position at t = 0.2**, from the density profile: the
midpoint crossing between ρ\*_R and ρ_R (ρ_mid = 0.195287), scanned from the
right, linearly interpolated between cell centres. Exact **0.850431146**.
**Band = exact ± 3 × |model error at fine| = 0.850431 ± 3.251e−04 =
[0.850106024, 0.850756269]** (±0.52 fine cells).

**Registered prediction, stated honestly about p.** A second-order
central-upwind scheme converges at ~first order in L1 near a shock and ~2/3
near a contact; the L1 error is contact-dominated here, so the **observed order
of G-F19-1 is expected in [0.6, 1.2] (model: 0.79–0.89)**. `roache_triple.py`
reads p < `STAGNANT_FLOOR` = 0.5 as STAGNANT = **NOT A RESULT**; the model
places p above that floor at both steps, so the registered prediction is **G-F19-1
CONVERGING with p ≈ 0.8, fine value inside the band → PASS**. For G-F19-2 the
model's three x_s values are monotone with a sign-stable error (order ≈ 0.58,
1.0), so the prediction is **CONVERGING → PASS**; **a non-monotone x_s triple is
a registered possible outcome** (a captured shock's sub-cell position need not
refine monotonically) and would read NOT A RESULT — that is the instrument
working, not a defect of the case, and no band or gate changes because of it.

## 6. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node, AST-censused;
  the text matcher driven both ways.
- **THERE IS NO PLATEAU GATE, AND IT IS SAID RATHER THAN HIDDEN.** The graded
  quantities are values at the fixed instant t = 0.2 of a transient;
  `plateau_states` is passed as `None` and recorded **ABSENT** in every row
  (`VERIFICATION_CHARTER` §9). The Class C ruling binds convergence/plateau/
  steady-state gates; this rung registers none.
- **Rule 5 limb (1) — explicit solver, said plainly.** The case is inviscid and
  `rhoCentralFoam` performs **no linear solve**; there is **no iterative residual**
  (F15's grader records the same). Limb (1) is evaluated as a **stability census
  over EVERY time step's solver-reported `max Courant Number`** against the
  registered ceiling **0.25** (= classical 0.5, the explicit KNP+Euler limit),
  with the line count required to equal the step count and any `nan` or `FOAM
  FATAL` refusing; the state is named `CONVERGED` only from that basis and the
  basis is written into every row. Driven both ways at selftest (one step above
  the ceiling, one `nan` line → not CONVERGED).
- **Completion (rule 4):** recorded rc = 0; `End`; `latest + Δt > endTime`; the
  fixed-Δt identity **`Time` lines == endTime/Δt** (1000 / 2000 / 4000); `rho`,
  `U`, `p`, `T` present at `0.2/` and **each newer than the case's own `0/U`**.
- **L-342 field classes (Sanaa's universal rule, `d4d0c29d`).**
  **`PHYSICS_CRITICAL`**: log `End`/`Time` count, `RC.txt`, endTime fields + age
  guard, `0/C`, every step's Courant line. **`INFRASTRUCTURE`**: `ClockTime`, box
  probes, `MESH_LINE.txt`, runner `STATUS`/`launcher.queue.out`/`LAUNCH_LOG`
  rows, calibration figures. Verdicts and refusals key on the first only; a
  missing INFRASTRUCTURE field prints **`BOOKKEEPING DEFECT`** beside the verdict
  and refuses the **cost claim only**. Driven both ways at selftest:
  infrastructure deleted → completion unchanged + defect lines + cost claim
  refused; rc corrupted or `End` deleted → **NOT A RESULT**. Absent `RC.txt` →
  PENDING.
- **Planted-zero controls (rule 3)** into a copy of the real `rho` artifact, read
  back with the real parser: a uniform δ = 1.234e−3 must move E1 **and** the
  shock position to the values predicted from the in-memory perturbed array
  (1e−13), and a plant that does not move the reading refuses.
- **`assert` census: ZERO** across `grade_f19.py`, `exact_f19.py`,
  `foam_io_f19.py`, `build_f19.py` (planted assert seen by the counter). **Hard
  `-O` refusal at entry, `sys.exit(2)`** — measured: `exact_f19.py --selftest`
  rc 0 / `-O` rc 2; `grade_f19.py --selftest` rc 0 / `-O` rc 2.
- **Success messages print INSIDE the passing branch.**
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/` or numeric time
  directory in the **run root** and in each **level directory**; neither deletes;
  no `rm -rf`/`rmtree` on any case directory; the builder refuses a destination
  inside the tracked case tree.
- **`set -u` is dropped around the OpenFOAM bashrc source only** (L-339);
  `scripts/check_launcher_can_launch.py --worktree cases/F19_SOD/run_f19.sh`:
  **rc 0** (0 suspect globs, 0 bashrc sources under `set -u`).
- **`--preflight` fires nothing, including `blockMesh`**; measured this session:
  rc 0, run root reported ABSENT; no-argument invocation rc 1.
- **Dictionaries cross-checked** at every grader entry and by the launcher:
  `molWeight` == `exact_f19.MOL_WEIGHT`, `Cp` == 3.5, `Tref`/`Hsref`/`Hf`/`mu`
  == 0, `fluxScheme Kurganov`, `ddt Euler`, the three `reconstruct` limiters,
  `endTime` == 0.2, `adjustTimeStep no`.

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real reader on files in the pinned write format
(`internalField nonuniform List<scalar>` ⏎ N ⏎ `(` … `)`, pinned against real
rhoCentralFoam output on this box, `verification/runs/F15_runs/coarse/4/rho`,
10,000 scalars, parsed at selftest as a live control):

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F19-1 | model fine ρ field, unshifted | 4.400280e−04 | [1.467e−04, 1.320e−03] | **inside** |
| G-F19-1 | the same shifted 32 cells (+0.02) | 1.754323e−02 | same | **outside** |
| G-F19-2 | model fine ρ field, unshifted | 0.8505395 | [0.8501060, 0.8507563] | **inside** |
| G-F19-2 | the same shifted 32 cells | 0.8705395 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned
against real output, the *values* are the model's.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.**

Cell-steps: 400×1000 + 800×2000 + 1600×4000 = **8.4 M**. **Rate basis: 0.75 µs
per cell-step plus 0.4 ms per step, DERIVED from two lab `rhoCentralFoam` records
of DIFFERENT cases on this box (serial, same Kurganov/vanLeer/Euler schemes, `mu 0`):**

| record | cells × steps | ClockTime | µs/cell-step |
|---|---|---|---|
| `verification/runs/F15_runs/coarse/log.rhoCentralFoam` | 10,000 × 9,233 | 68 s | 0.74 |
| `verification/runs/F15_runs/medium/log.rhoCentralFoam` | 40,000 × 18,760 | 524 s | 0.70 |
| `verification/runs/F15_runs/fine/log.rhoCentralFoam` | 160,000 × 18,375 | 2018 s | 0.69 |
| `verification/runs/F4_runs/successor_2026-08-26/runs/cyl/M6.0/coarse/log.rhoCentralFoam` | 1,000 × 6,095 | 5.95 s (ExecutionTime) | 0.98 → fixed overhead ≈ 0.33 ms/step |
| `…/cyl/M6.0/medium/log.rhoCentralFoam` | 4,000 × 11,096 | 29 s | 0.65 |
| `…/cyl/M6.0/fine/log.rhoCentralFoam` | 16,000 × 22,113 | 230 s | 0.65 |

**Not measured on this case.** At 400–1600 cells the per-step overhead dominates.

| level | projected serial s | core-min |
|---|---|---|
| coarse | 0.7 (launcher uses 1) | 0.012 |
| medium | 2.0 | 0.033 |
| fine | 6.4 (launcher uses 7) | 0.107 |
| **total, with blockMesh/checkMesh/postProcess** | **≈ 10** | **≈ 0.2** |

**REGISTERED CAP: 5 core-minutes** (25× headroom; the width is the admission —
per-step overhead on a loaded box is the unknown). **Derived dollars at
$0.0513/core-h: $0.0002 estimate, $0.004 at the cap — DERIVED, NOT MEASURED,
reported-by-owner rate** (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
pre-authorisation. **`cost_basis: derived, reported-by-owner, not measured.`**

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe; a crossing **HALTS at exit 3**; unlaunched
levels stay `PENDING`; launcher and grader refuse to start if their caps disagree.

**Scratch smoke arm, reported (cfd pre-freeze requirement since F16):** one real
`rhoCentralFoam` step (Δt = 2e−4) on a scratch copy of the coarse level built by
`build_f19.py`: **rc 0**, reached `Time = 0.0002`, `End` written, **max |Ux| after
one step = 2.163e−01 (NON-ZERO: the fields move), Uy = Uz = 0 exactly**, density
changed in the 2 diaphragm cells (L1 2.07e−4), solver-reported max Courant
0.0473 (= 0.5·a_L·Δt/h, u = 0 at step 1), **far-field ρ read back 1.000000000000000
and 0.125000000000000 — the R = 1 thermo is verified on the real solver**;
wall 0.05 s, ClockTime 0 s — **≈ 0.02 core-min including blockMesh/checkMesh/
postProcess**; not retained, not a measured history, not a result.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F19_SOD_runs` → **absent**
when this file was written and at `--preflight` (the launcher prints it). No
`RC.txt`, `log.*` or numeric time directory exists under `cases/F19_SOD/` (only
the tracked template directory `case/0`, holding `*.template` files).

## 10. NEVER RUN — THE EVIDENCE (L-337 controls first)

- `git ls-tree -r HEAD --name-only`: **14,243** tracked paths at the start of this
  session; **planted control: the known `cases/F18_taylor_green/` paths are
  returned (12)**; case-insensitive matches for `F19|sod_|isentropic`: **0**
  (the regex also returned 5 paper filenames containing the substring `caf20`,
  none of them this case).
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (534) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F19*` directory.

## 11. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F19_SOD/run_f19.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F19_SOD/grade_f19.py --prereg-commit=<sha>`. The queue entry
`cases/F19_SOD/queue_entry_F19_SOD.json` is **held** under the case directory,
validated by explicit path, until the supervisor's check 1/4; the supervisor
moves it into `verification/queue/cfd/`; enqueueing is not authorisation.

## 12. FROZEN FILES (the grading path is fixed at this commit)

    cases/F19_SOD/exact_f19.py        cases/F19_SOD/grade_f19.py
    cases/F19_SOD/build_f19.py        cases/F19_SOD/foam_io_f19.py
    cases/F19_SOD/run_f19.sh
    cases/F19_SOD/case/0/{p,T,U}.template
    cases/F19_SOD/case/constant/{thermophysicalProperties,turbulenceProperties}
    cases/F19_SOD/case/system/{blockMeshDict.template,controlDict.template,fvSchemes,fvSolution}
    verification/campaign/F19_SOD_PREREGISTRATION.md   (this file)

## 13. WHAT IS **NOT** REGISTERED HERE

- No claim about p beyond the honest range in §5; no claim about the contact
  discontinuity's position (not gated).
- No re-grade of any row; no amendment to any standard or charter.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
