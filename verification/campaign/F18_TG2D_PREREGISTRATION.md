# F18 — PRE-REGISTRATION: 2-D decaying Taylor–Green vortex (icoFoam, periodic box)

**Team:** cfd. **Written before any compute. ZERO CORE-MINUTES SPENT in the case
tree or any run root.** **Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** under
Sanaa's standing order that the cfd queue never empties; her silence is approval.

---

## 1. WHY THIS CASE

A **smooth, nonlinear, transient** exact solution of the incompressible
Navier–Stokes equations on a doubly periodic box: no walls, no inflow, no
boundary datum at all, so the ladder measures **only** the spatial scheme, the
`backward` time integration and PISO's pressure–velocity coupling. It sits
beside F16 (transient, linear, wall-driven) and F17 (steady, nonlinear,
inflow/outflow) so that a second-order scheme is asked to recover p ≈ 2 in three
distinct regimes. The registered prediction is **p ≈ 2**.

**Case-selection charter:** an **`instrument-check`** (`CASE_SELECTION_CHARTER.md`
§3), labelled so at registration; not a result, counts toward no challenge
column, not filmed. It is a **different case** from the proposal
`research/agenda/proposals/taylor-green-re1600-first-rung.json` (3-D, Re = 1600,
graded against a fetched workshop table): this rung is 2-D, exact, fetches
nothing and cannot block on a reference. Said here so the adjacency is disclosed
rather than discovered.

## 2. THE CASE

    u =  U0 sin x cos y e^{−2νt},   v = −U0 cos x sin y e^{−2νt},
    p =  U0² (cos 2x + cos 2y)/4 e^{−4νt}     on [0, 2π]², periodic in x and y

| item | value |
|---|---|
| ν | 0.1 (cell Reynolds U0 h/ν ≤ 0.98 at the coarse level) |
| U0 | 1 |
| T | 2.0 s → decay e^{−2νT} = 0.670; box-mean kinetic energy exact at T: U0²/4·e^{−4νT} = **0.112332241029305** |
| initial field | exact u, v **and p** at t = 0 at the built mesh's own cell centres (from `0/C`) |
| patches | `left/right`, `bottom/top` **cyclic** (blockMesh `neighbourPatch`); `frontAndBack` empty |
| solver | `icoFoam`, `backward` (BDF2), Gauss linear, orthogonal Laplacian/snGrad; PISO 2 correctors; p PCG/DIC tol 1e−9 relTol 0; `pRefCell 0` |
| output | fields at `endTime` only |

**Mesh admissibility (MESH_STANDARD §3, §8.1):** the coarse level was **BUILT
AND `checkMesh`'d** on a scratch copy before this freeze — 4,096 cells, max
non-orthogonality **0°** against the 70° gate, max skewness 3.6e−14 against 4,
`Mesh OK`; `build_f18.py` enforces both gates at every level and writes
`MESH_LINE.txt` from the built mesh.

## 3. THE REFERENCE IS **NOT A PAPER**. IT IS A SUBSTITUTION.

Rule 15 requires title-page verification of every **retrieved** paper; this case
retrieves none. `exact_f18.py --selftest` substitutes the closed form into the
**unsteady** incompressible Navier–Stokes equations symbolically: continuity,
x- and y-momentum residuals are **identically zero**. **Planted control:** the
decay rate perturbed from 2ν to 2.3ν makes the momentum residual **non-zero**.
(The substitution control earned its keep while this rung was being written: a
first draft carried the pressure sign of the other Taylor–Green convention and
was refused.)

## 4. THE LADDER — THREE LEVELS (§9.1)

Uniform square cells; **h and Δt both refine by exactly 2** at constant Courant
number U0Δt/h = 0.2 (checked; a departure refuses). `dim = 2`, r = 2.000 from
cell counts.

| level | N × N | cells | h | steps | Δt | E2(T) predicted | KE error predicted |
|---|---|---|---|---|---|---|---|
| coarse | 64 × 64 | 4,096 | 0.098175 | 100 | 0.02 | 1.504101e−04 | +7.130385e−05 |
| medium | 128 × 128 | 16,384 | 0.049087 | 200 | 0.01 | 3.771909e−05 | +1.787910e−05 |
| fine | 256 × 256 | 65,536 | 0.024544 | 400 | 0.005 | 9.459008e−06 | +4.483101e−06 |

Model orders coarse→medium: **1.9955 (E2), 1.9957 (KE)**; the fine row is
**extrapolated** from the medium with those orders (stated in the table's source
column of the selftest JSON). The predicted KE error is **positive** at every
level — the discrete Laplacian under-damps the (1,1) mode, decay rate
2ν(1 − h²/12 + …) — and sign-stable, so the KE triple is predicted monotone.

**DECOMPOSITION SEED (required field): `none`.** Every level **serial on 1
rank**; `decomposePar` never invoked; no partition, no RNG.

## 5. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to a prediction computed
from the scheme. Declared now; not measured, not fitted, not revisable.

**The derivation.** `exact_f18.py::discrete_error` evaluates icoFoam's own
uniform-Cartesian stencils on the exact field — Gauss linear convection, Gauss
linear orthogonal Laplacian, Gauss linear pressure gradient, interpolated fluxes,
and the BDF2 time-derivative residual of the exact decay — giving r(t), d(t).
The leading-order error e obeys the linearised discrete equations
∂e/∂t + C_h'(U(t))e − νL_h e + G_h q = −r(t), D_h e + RC(q) = −d(t), integrated
with the same BDF2 step the solver takes (diffusion and projection implicit
through one sparse LU; linearised convection explicit AB2; Rhie–Chow flux with a
compact pressure Laplacian) on the coarse and medium grids at their own Δt; the
fine level is extrapolated with the model's observed order, which a control
requires to lie in [1.7, 2.3]. A control also refuses if the stencil evaluator
returns a zero residual on the exact field.

**What the model omits, so the factor-3 window is an admission:** nonlinear
feedback of the error (second order in e); PISO's non-iterated splitting (its
first-order part on this flow is a gradient the projection removes); the first
`backward` step, which OpenFOAM takes as Euler implicit (one O(Δt²) local error).

**G-F18-1 — normalised L2 velocity error at t = T**

    E2(T) = √( mean over cells |U_h − U_exact(x_c, T)|² ) / U0

Prediction at the fine level: **9.459008e−06**.
**Band = [prediction/3, prediction×3] = [3.153003e−06, 2.837702e−05].**

**G-F18-2 — box-mean kinetic energy at t = T**, mean over cells of ½|U_h|²
(uniform cells). Exact **0.112332241029305**.
**Band = exact ± 3 × 4.483101e−06 = [0.112318791726, 0.112345690333].**

**Registered prediction: both triples `CONVERGING` with observed order p ≈ 2
(model 1.996); fine values inside both bands → PASS.**

## 6. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node, AST-censused;
  the text matcher driven both ways.
- **THERE IS NO PLATEAU GATE, AND IT IS SAID RATHER THAN HIDDEN.** The graded
  quantities are values at the fixed instant t = T of a decaying transient; there
  is no steady state and no period to lock to, so `plateau_states` is passed as
  `None` and recorded **ABSENT** in every row (`VERIFICATION_CHARTER` §9: an
  absent measurement is reported as absent, never as a pass). The Class C ruling
  binds convergence/plateau/steady-state gates; this rung registers none.
- **Rule 5 limb (1):** a **census over EVERY time step's final pressure residual**
  (both PISO correctors) against the solver's own `tolerance 1e-09`; the count
  above tolerance is reported; a control refuses if the grader's constant
  disagrees with `system/fvSolution` on disk.
- **Completion (rule 4):** recorded rc = 0; `End`; `latest + Δt > endTime`;
  the fixed-Δt identity **`Time` lines == endTime/Δt** (100 / 200 / 400); `U`
  and `p` present at `2/` and **each newer than the case's own `0/U`**.
- **L-342 field classes (Sanaa's universal rule, `d4d0c29d`).**
  **`PHYSICS_CRITICAL`**: log `End`/`Time` count, `RC.txt`, endTime fields + age
  guard, `0/C`, every step's p residual. **`INFRASTRUCTURE`**: `ClockTime`, box
  probes, `MESH_LINE.txt`, runner `STATUS`/`launcher.queue.out`/`LAUNCH_LOG`
  rows, calibration figures. Verdicts and refusals key on the first only; a
  missing INFRASTRUCTURE field prints **`BOOKKEEPING DEFECT`** beside the verdict
  and refuses the **cost claim only**. Driven both ways at selftest:
  infrastructure deleted → completion unchanged + defect lines + cost claim
  refused; rc corrupted or `End` deleted → **NOT A RESULT**. Absent `RC.txt` →
  PENDING.
- **Planted-zero controls (rule 3)** into a copy of the real artifact, read back
  with the real parser: a Ux offset must move E2 to its predicted value (1e−14)
  and the box-mean KE by exactly mean(Ux)·δ + δ²/2 (1e−14).
- **`assert` census: ZERO** across `grade_f18.py`, `exact_f18.py`,
  `foam_io_f18.py`, `build_f18.py` (planted assert seen by the counter). **Hard
  `-O` refusal at entry, `sys.exit(2)`.**
- **Success messages print INSIDE the passing branch.**
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/` or numeric time
  directory; neither deletes; no `rm -rf`/`rmtree` on any case directory; the
  builder refuses a destination inside the tracked case tree.
- **`set -u` is dropped around the OpenFOAM bashrc source only** (L-339; F16
  attempt 1 died silently at that line on 2026-08-26) — applied from the start,
  not by amendment.
- **`--preflight` fires nothing, including `blockMesh`**; measured this session:
  rc 0, run root reported ABSENT.
- **Dictionaries cross-checked** at every grader entry: ν == `exact_f18.NU`,
  p tolerance == 1e−9, `endTime` == 2, `ddtSchemes` == `backward`.

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real readers on files in the pinned write format
(`internalField nonuniform List<vector>` ⏎ N ⏎ `(` … `)`, pinned against real
icoFoam output on this box,
`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, parsed at selftest as a
live control). The medium level's integrated error field, scaled by the model's
medium→fine ratio, stands in for the fine field:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F18-1 | exact(T) + **1×** scaled model error field | 9.459008e−06 | [3.153e−06, 2.838e−05] | **inside** |
| G-F18-1 | exact(T) + **40×** the same | 3.783603e−04 | same | **outside** |
| G-F18-2 | exact(T) + **1×** the same | 0.1123367 | [0.1123188, 0.1123457] | **inside** |
| G-F18-2 | exact(T) + **40×** the same | 0.1125117 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned against
real output, the *values* are constructed.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.**

Cell-steps: 4,096×100 + 16,384×200 + 65,536×400 = **29.9 M**. **Rate basis: 5 µs
per cell-step, DERIVED from one lab record of a DIFFERENT case** —
`verification/runs/ansys_verification/VMFL019/L1_30/log.icoFoam` (icoFoam serial,
480 cells × 400 steps, ExecutionTime 0.38 s = 2.0 µs/cell-step, overhead-dominated
at that size; 5 µs allows PCG iteration growth with cell count). **Not measured
on this case.**

| level | projected serial s | core-min |
|---|---|---|
| coarse | 2 | 0.03 |
| medium | 17 | 0.27 |
| fine | 131 | 2.18 |
| **total** | **150** | **2.5** |

**REGISTERED CAP: 30 core-minutes** (12× headroom; the width is the admission —
PCG on 65k cells at 1e−9 with relTol 0 is the unknown). **Derived dollars at
$0.0513/core-h: $0.002 estimate, $0.026 at the cap — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation.
**`cost_basis: derived not measured.`**

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe; a crossing **HALTS at exit 3**; unlaunched
levels stay `PENDING`; launcher and grader refuse to start if their caps disagree.

**Scratch smoke arm, reported:** one real `icoFoam` step (Δt = 0.02) on a scratch
copy of the coarse level built by `build_f18.py` into the scratchpad: rc 0,
reached `Time = 0.02`, `End` written, **`Solving for Ux` initial residual
1.99e−03 (non-zero: the fields move — the check F16's `empty` ±x patches would
have failed)**, p final residual 7.6e−10, ClockTime 0 s (wall < 0.1 s) —
**≈0.01 core-min including blockMesh/checkMesh/postProcess**; not retained, not a
measured history, not a result.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F18_runs` → **absent** when
this file was written and at `--preflight`. No `RC.txt`, `log.*` or numeric time
directory exists under `cases/F18_taylor_green/` (only the tracked template
directory `case/0`).

## 10. NEVER RUN — THE EVIDENCE

- `git ls-tree -r HEAD --name-only`: **13,862** tracked paths at the start of this
  session; matches for `F18|taylor_green|taylorgreen`: **0** (planted control: a
  known tracked path is in the enumeration).
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (531) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F18*` directory.

## 11. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F18_taylor_green/run_f18.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F18_taylor_green/grade_f18.py --prereg-commit=<sha>`. The queue
entry is **held** (staged under the case directory, validated by explicit path)
until the supervisor acknowledges the freeze sha; a live queue runner fires
validated entries.

## 12. WHAT IS **NOT** REGISTERED HERE

- No turbulence claim; no claim about p beyond its role as an initial field.
- No re-grade of any row; no amendment to any standard or charter.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
