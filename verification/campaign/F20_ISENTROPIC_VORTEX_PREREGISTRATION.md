# F20 — PRE-REGISTRATION: 2-D inviscid isentropic vortex (rhoCentralFoam, periodic box, one period)

**Team:** cfd. **Written before any compute. ZERO CORE-MINUTES SPENT in the case
tree or any run root.** **Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** under
Sanaa's standing order that the cfd queue is kept deep with pre-registered,
costed cases (chief commits `73eccb1b`, `7def3c6b`, `0b041d1a`; permission
`bc0e687e`). Template in structure and rigour: F18 (`c4f72b27`); sibling F19
(`3053d9ec`).

---

## 1. WHY THIS CASE

A **smooth, nonlinear, compressible** exact solution of the 2-D Euler equations
with no boundary datum at all (doubly periodic): the ladder measures only the
Kurganov/vanLeer spatial scheme and the solver's **explicit Euler** time
integration. It sits beside F19 (discontinuous, 1-D, same solver and schemes)
so that the same `rhoCentralFoam` line is asked for its order on a smooth
problem — where the honest expectation is **between 1 and 2**, because the time
integration is first order and Δt refines with h. **Case-selection charter:** an
**`instrument-check`** (`CASE_SELECTION_CHARTER.md` §3), labelled so at
registration; not a result, counts toward no challenge column, not filmed. It is
the largest case cfd has registered for the queue runner (≈ 60 core-min): real
hours for the box, as ordered.

## 2. THE CASE (Yee, Sandham & Djomehri 1999 / Shu 1998 form)

    free stream rho = p = T = 1, (u, v) = (1, 1), gamma = 1.4, R = 1; beta = 5 at (5, 5) on [0, 10]^2
    u = 1 − β/(2π) e^{(1−r²)/2} (y−5),   v = 1 + β/(2π) e^{(1−r²)/2} (x−5)
    T = 1 − (γ−1) β² / (8 γ π²) e^{1−r²},   rho = T^{1/(γ−1)},   p = rho T
    the pattern translates with (1, 1); at t = 10 it is back at (5, 5)

| item | value |
|---|---|
| gas | nondimensional perfect gas exactly as F19: `molWeight 8314.47006650545` (R = 1), `Cp 3.5` (γ = 1.4), `Tref 0`, `Hsref 0`, `Hf 0`, `mu 0`, `Pr 1` |
| initial field | exact vortex at t = 0 at the built mesh's own cell centres (from `0/C`): `0/p`, `0/T`, then `0/U` written **last** |
| solver | `rhoCentralFoam`, **the shipped shockTube tutorial's schemes verbatim** (`fluxScheme Kurganov`, `ddt Euler`, `reconstruct(rho) vanLeer`, `reconstruct(U) vanLeerV`, `reconstruct(T) vanLeer`, `Gauss linear`, `corrected`); `fvSolution` as the tutorial (`diagonal`) |
| time step | **fixed** (`adjustTimeStep no`), Δt/h = 0.032 at every level; the solver's own `max Courant Number` ≈ **0.10** (measured 0.0999 at step 1 on the smoke arm; model 0.102), registered census ceiling 0.25 |
| patches | `left/right`, `bottom/top` **cyclic** pairs; `frontAndBack` **empty** (2-D: the removed z-component is identically zero — the F19 argument, not F16's defect) |
| output | fields (`rho U p T`) at `endTime` = 10 only |

**The reference is the PERIODISED closed form.** The Gaussian tails make the
closed form not exactly periodic on a 10 × 10 box: the velocity jump across the
seam is **4.89e−5** and the density jump is **0 to double precision** (measured
by `seam_mismatch()`, a control requires 1e−6 < jump_v < 1e−4). The reference
and the discretisation model both use the periodised field, so the seam is
inside every prediction; it is 3 % of the predicted fine-level E2 and is noted,
not neglected.

**Mesh admissibility (MESH_STANDARD §3, §8.1):** the coarse level was **BUILT AND
`checkMesh`'d** on a scratch copy before this freeze — 16,384 cells, max
non-orthogonality **0°** against the 70° gate, max skewness 0 against 4,
`Mesh OK`; `build_f20.py` enforces both gates at every level.

## 3. THE REFERENCE IS **NOT A PAPER**. IT IS A SUBSTITUTION.

Rule 15 requires title-page verification of every **retrieved** paper; this case
retrieves none. `exact_f20.py --selftest` substitutes the closed form
symbolically into the **steady Euler equations in the frame moving with the free
stream**: continuity, x- and y-momentum residuals and p/ρ^γ − 1 are
**identically zero** (`sympy`; the entropy identity needs `powdenest(force=True)`
because sympy will not combine (T^{5/2})^{7/5} without a positivity assumption).
**Planted control:** β in T raised 10 % gives an x-momentum residual of 0.0898 at
(0.7, −0.3). **Period control:** the field at t = 10 equals the field at t = 0 at
every one of 512² centres to 0 (exactly), and differs by 0.506 at t = 5 (the
vortex on the opposite corner). Box-mean kinetic energy of the exact field
**1.005633548659** (midpoint rule, 2048² vs 4096²: 2.2e−16).

## 4. THE LADDER — THREE LEVELS (§9.1), `dim = 2`

Uniform square cells; **h and Δt both refine by exactly 2** at constant Δt/h
(checked; a departure refuses). r = 2.000 from cell counts.

| level | N × N | cells | h | steps | Δt | E2(T) predicted | KE error predicted (S + BΔt) |
|---|---|---|---|---|---|---|---|
| coarse | 128 × 128 | 16,384 | 0.078125 | 4,000 | 2.5e−3 | 3.342463e−03 (integrated) | −1.521e−05 (integrated; S −7.00e−4, BΔt +6.85e−4) |
| medium | 256 × 256 | 65,536 | 0.039063 | 8,000 | 1.25e−3 | 1.181028e−03 (extrapolated, p 1.50) | +1.245e−04 (S −2.18e−4, BΔt +3.43e−4) |
| fine | 512 × 512 | 262,144 | 0.019531 | 16,000 | 6.25e−4 | 4.173050e−04 (extrapolated) | +1.034e−04 (S −6.79e−5, BΔt +1.71e−4) |

The 64²/128² ladder was **rejected** because its fine level projects at ≈ 6
core-min, under the ~40 core-min the order asks the queue to receive; the
128²/256²/512² ladder projects ≈ 52 core-min at the fine level.

**DECOMPOSITION SEED (required field): `none`.** Every level **serial on 1
rank**; `decomposePar` never invoked; no partition, no RNG.

## 5. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to predictions computed
from the scheme. Declared now; not measured on the case, not fitted, not revisable.

**The derivation.** `exact_f20.py::knp_model` re-implements rhoCentralFoam's
discretisation in two dimensions (directed vanLeer / vanLeerV reconstruction with
OpenFOAM's `NVDTVD` / `NVDVTVDV` ratios and 1000× clamp; the Kurganov weights and
`phi`/`phiUp`/`phiEp` fluxes per face exactly as `rhoCentralFoam.C` forms them;
explicit Euler update; periodic by construction). Three registered runs at
selftest (≈ 35 s): **64² at the ladder's Δt/h, 64² at half that Δt, 128² at the
ladder's Δt/h** (the ladder's own coarse level). Controls: mass conserved to
1e−9; solver-convention max Courant 0.101/0.050/0.102 under the 0.25 ceiling.

**What was learned from the model, and registered as the prediction:**
- **E2** (a norm): observed model order 64²→128² **1.501** — between 1 and 2, as
  first-order time integration with Δt ∝ h implies. Medium and fine are
  extrapolated with that order. **The expected observed order on the real ladder
  is in [1.0, 1.6]**, drifting toward 1 as the O(Δt) part takes over; the band is
  a value band and does not depend on p.
- **KE**: at fixed h the model's KE error moves **linearly with Δt with slope B =
  +0.274** (64²: −8.79e−4 → −1.56e−3 → −1.90e−3 as Δt halves twice; 128²: slope
  0.276) — explicit Euler is anti-dissipative — while the Δt→0 spatial part is
  dissipative, **S = −2.25e−3 (64²), −7.00e−4 (128²), order 1.68**. Along the
  ladder the two parts **cancel near 128²** and the signed sum changes sign.
  **Therefore the KE band is built from the SUM OF MAGNITUDES |S| + |BΔt| at
  fine, not from the cancelling sum, and the KE triple is predicted NON-MONOTONE
  (OSCILLATORY or DEGENERATE) → NOT A RESULT, with the band verdict printed
  beside it** — a registered, expected outcome, not a defect.
- **One-off consistency integration at 256² (Python only, zero OpenFOAM
  compute, ≈ 5 min, NOT part of the registered model runs):** E2 = **1.4194e−03**
  where the extrapolation says 1.181e−03 (ratio 1.20, inside the factor-3
  window; order 128²→256² = 1.24, the predicted drift toward 1); KE error =
  **−7.06e−05** where the two-term extrapolation says +1.24e−04 — **the sign of a
  cancellation cannot be extrapolated**, which is exactly why the KE band uses
  the sum of magnitudes (5.6e−4 at 256², containing the −7.1e−5 comfortably).
  Recorded here so the reader sees the model's limit before the run, not after.

**What the model omits, so the factor-3 window is an admission:** the
extrapolation across two halvings (the 256² check bounds it at 1.2× for E2);
`vanLeerV`'s tensor form (the projection form used is OpenFOAM's definition on a
Cartesian mesh); floating-point ordering; the solver's `psi`/`p` boundary update
sequence on cyclic patches.

**G-F20-1 — L2 density error at t = 10**

    E2(T) = √( mean over cells (ρ_h − ρ_exact(x_c, y_c, T))² ),  ρ_exact(·, T) = ρ_exact(·, 0) on the box

Prediction at the fine level: **4.173050e−04** (the 256² check suggests the true
value may sit nearer 6–7e−4; still inside).
**Band = [prediction/3, prediction×3] = [1.391017e−04, 1.251915e−03].**

**G-F20-2 — box-mean kinetic energy at t = 10**, mean over cells of ½ρ_h|U_h|²
(uniform cells). Exact **1.005633548659**. Fine-level magnitude basis |S| + |BΔt|
= 6.79e−5 + 1.71e−4 = **2.3922e−04**.
**Band = exact ± 3 × 2.3922e−04 = [1.004915893, 1.006351204].**

**Registered prediction: G-F20-1 CONVERGING with observed order in [1.0, 1.6],
fine value inside the band → PASS. G-F20-2: fine value inside the band (band
verdict PASS) but the triple non-monotone → NOT A RESULT.**

## 6. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node (line 551 of
  `grade_f20.py` at freeze), AST-censused; the text matcher driven both ways.
- **THERE IS NO PLATEAU GATE, AND IT IS SAID RATHER THAN HIDDEN.** Values at the
  fixed instant t = 10 of a transient; `plateau_states` is `None`, recorded
  **ABSENT** in every row (`VERIFICATION_CHARTER` §9).
- **Rule 5 limb (1) — explicit solver, said plainly.** Inviscid `rhoCentralFoam`
  performs no linear solve and has **no iterative residual** (as F15 and F19
  record). Limb (1) is a **stability census over every time step's
  solver-reported `max Courant Number`** against the ceiling **0.25**, line count
  == step count (4000 / 8000 / 16000), `nan`/`FOAM FATAL` refusing; the basis is
  written into every row and driven both ways at selftest.
- **Completion (rule 4):** rc = 0; `End`; `latest + Δt > endTime`; **`Time` lines
  == endTime/Δt**; `rho`, `U`, `p`, `T` at `10/` and **each newer than the case's
  own `0/U`**.
- **L-342 field classes (Sanaa's universal rule, `d4d0c29d`).**
  **`PHYSICS_CRITICAL`**: log `End`/`Time` count, `RC.txt`, endTime fields + age
  guard, `0/C`, every step's Courant line. **`INFRASTRUCTURE`**: `ClockTime`, box
  probes, `MESH_LINE.txt`, runner `STATUS`/`launcher.queue.out`/`LAUNCH_LOG`
  rows, calibration figures. Verdicts key on the first only; a missing
  INFRASTRUCTURE field prints **`BOOKKEEPING DEFECT`** and refuses the **cost
  claim only**. Driven both ways at selftest.
- **Planted-zero controls (rule 3)** into a copy of the real `rho` artifact, read
  back with the real parser: δ = 1.234e−3 must move E2 **and** the box-mean KE to
  the values predicted from the in-memory perturbed array (1e−13); a plant that
  does not move the reading refuses.
- **`assert` census: ZERO** across `grade_f20.py`, `exact_f20.py`,
  `foam_io_f20.py`, `build_f20.py`. **Hard `-O` refusal at entry, `sys.exit(2)`**
  — measured: `exact_f20.py --selftest` rc 0 / `-O` rc 2; `grade_f20.py
  --selftest` rc 0 / `-O` rc 2.
- **Success messages print INSIDE the passing branch.**
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/` or numeric time
  directory in the run root and in each level directory; neither deletes; the
  builder refuses a destination inside the tracked case tree.
- **`set -u` is dropped around the OpenFOAM bashrc source only** (L-339);
  `scripts/check_launcher_can_launch.py --worktree cases/F20_ISENTROPIC_VORTEX/run_f20.sh`:
  **rc 0**.
- **`--preflight` fires nothing, including `blockMesh`**; measured: rc 0, run
  root reported ABSENT; no-argument invocation rc 1.
- **Dictionaries cross-checked** at every grader entry and by the launcher
  (`molWeight`, `Cp`, `Tref`/`Hsref`/`Hf`/`mu`, `fluxScheme`, `ddt`, the three
  `reconstruct` limiters, `endTime` == 10, `adjustTimeStep no`).

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real readers on files in the pinned write formats (scalar `rho` and
vector `U`, pinned against real rhoCentralFoam output on this box,
`verification/runs/F15_runs/coarse/4/{rho,U}`, 10,000 cells each, parsed at
selftest). The model's 128² error fields scaled by the model's 128→512 E2 ratio
stand in for the fine field:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F20-1 | exact(T) + **1×** scaled model error field | 4.173050e−04 | [1.391e−04, 1.252e−03] | **inside** |
| G-F20-1 | exact(T) + **40×** the same | 1.669220e−02 | same | **outside** |
| G-F20-2 | exact(T) + 1× the same | 1.005626175 | [1.004915893, 1.006351204] | **inside** |
| G-F20-2 | the same with **U × 1.001** | 1.007638433 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned, the
*values* are the model's.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.**

Cell-steps: 16,384×4,000 + 65,536×8,000 + 262,144×16,000 = **4.78 G**. **Rate
basis: 0.75 µs per cell-step plus 0.4 ms per step, DERIVED from the same two lab
`rhoCentralFoam` records as F19** (`verification/runs/F15_runs/{coarse,medium,fine}/log.rhoCentralFoam`:
0.74/0.70/0.69 µs/cell-step at 10k/40k/160k cells; `verification/runs/F4_runs/successor_2026-08-26/runs/cyl/M6.0/{coarse,medium,fine}/log.rhoCentralFoam`:
0.98/0.65/0.65 µs/cell-step at 1k/4k/16k cells, ≈ 0.33 ms/step fixed overhead).
**Not measured on this case.**

| level | cell-steps | projected serial s | core-min |
|---|---|---|---|
| coarse 128² | 6.55e7 | 51 | 0.85 |
| medium 256² | 5.24e8 | 396 | 6.6 |
| fine 512² | 4.19e9 | 3152 | 52.5 |
| **total** | **4.78e9** | **≈ 3600** | **≈ 60** |

**REGISTERED CAP: 240 core-minutes** (4× headroom; the launcher's projection
doubles when its box probe reads < 1 free core, and 2 × 60 = 120 still clears
the cap; the width is the admission — `rhoCentralFoam` at 262k cells on a box
running other teams' solvers is the unknown). **Derived dollars at
$0.0513/core-h: $0.05 estimate, $0.21 at the cap — DERIVED, NOT MEASURED,
reported-by-owner rate** (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
pre-authorisation. **`cost_basis: derived, reported-by-owner, not measured.`**

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe; a crossing **HALTS at exit 3**; unlaunched
levels stay `PENDING`; launcher and grader refuse to start if their caps disagree.

**Scratch smoke arm, reported (cfd pre-freeze requirement since F16):** one real
`rhoCentralFoam` step (Δt = 2.5e−3) on a scratch copy of the coarse level built
by `build_f20.py`: **rc 0**, reached `Time = 0.0025`, `End`, solver-reported
Courant 0.0702 mean / **0.0999 max**, **max |U(Δt) − U(0)| = 3.457e−03 (NON-ZERO:
the fields move), Uz = 0 exactly**, L2 density error against the translated exact
field after one step 3.48e−06 (against the untranslated field 2.30e−04: the
vortex moves the right way), box-mean KE 1.005633781 (exact 1.005633549: +2.3e−7
after one step — the Euler part's sign, already visible), corner-cell ρ read back
**exactly 1** (R = 1 verified on the solver); wall 0.18 s — **≈ 0.03 core-min
including blockMesh/checkMesh/postProcess**; not retained, not a result.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F20_ISENTROPIC_VORTEX_runs`
→ **absent** when this file was written and at `--preflight`. No `RC.txt`,
`log.*` or numeric time directory exists under `cases/F20_ISENTROPIC_VORTEX/`.

## 10. NEVER RUN — THE EVIDENCE (L-337 controls first)

- `git ls-tree -r HEAD --name-only`: **14,243** tracked paths at the start of this
  session; **planted control: the known `cases/F18_taylor_green/` paths are
  returned (12)**; case-insensitive matches for `F20|isentropic|vortex` outside
  paper filenames: **0** (the substring `caf20` in three paper filenames is the
  only hit).
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (534) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F20*` directory.

## 11. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F20_ISENTROPIC_VORTEX/run_f20.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F20_ISENTROPIC_VORTEX/grade_f20.py --prereg-commit=<sha>`. The
queue entry `cases/F20_ISENTROPIC_VORTEX/queue_entry_F20_ISENTROPIC_VORTEX.json`
is **held** under the case directory until the supervisor's check 1/4; the
supervisor moves it into `verification/queue/cfd/`; enqueueing is not authorisation.

## 12. FROZEN FILES

    cases/F20_ISENTROPIC_VORTEX/exact_f20.py     cases/F20_ISENTROPIC_VORTEX/grade_f20.py
    cases/F20_ISENTROPIC_VORTEX/build_f20.py     cases/F20_ISENTROPIC_VORTEX/foam_io_f20.py
    cases/F20_ISENTROPIC_VORTEX/run_f20.sh
    cases/F20_ISENTROPIC_VORTEX/case/0/{p,T,U}.template
    cases/F20_ISENTROPIC_VORTEX/case/constant/{thermophysicalProperties,turbulenceProperties}
    cases/F20_ISENTROPIC_VORTEX/case/system/{blockMeshDict.template,controlDict.template,fvSchemes,fvSolution}
    verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md   (this file)

## 13. WHAT IS **NOT** REGISTERED HERE

- No claim of second-order convergence: the honest range is §5's.
- No re-grade of any row; no amendment to any standard or charter.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
