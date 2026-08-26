# F17 — PRE-REGISTRATION: Kovasznay flow (steady exact Navier–Stokes, Re = 40)

**Team:** cfd. **Written before any compute. ZERO CORE-MINUTES SPENT in the case
tree or any run root.** **Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** under
Sanaa's standing order that the cfd queue never empties; her silence is approval.

---

## 1. WHY THIS CASE, AND WHY NOT THE TWO IT DISPLACES

The supervisor's slot (A) named a laminar developing Poiseuille channel or a
Blasius flat plate, gated on wall shear against an on-box reference, **with the
band derived from the discretisation**. Neither candidate can carry that band:

- **Blasius.** The reference is the boundary-layer *approximation*; a
  Navier–Stokes solve differs from it by O(Re_x^−1/2) at the graded station and
  by a leading-edge singularity the mesh cannot resolve at any level. A
  discrepancy with a model-form component cannot be banded by truncation error.
- **Fully developed Poiseuille.** The parabola is reproduced **exactly** by a
  second-order central scheme on a uniform mesh, so the triple is `EXACT` and
  rule 5 returns `NOT A RESULT` by construction. The developing-length variant
  has only empirical references (Shah–London class), not an exact one.

**Kovasznay flow** is an exact solution of the **full steady incompressible
Navier–Stokes equations**, nonlinear (Re = 40), smooth, 2-D, and periodic in y.
It exercises convection, pressure–velocity coupling and inflow/outflow boundaries
on `simpleFoam` — the lab's most-used steady solver — against a closed form
verified on this box. Its band descends from the scheme itself (§5). It is the
steady, nonlinear complement of F16 (transient, linear) and of F18 (transient,
nonlinear, periodic).

**Case-selection charter:** this is an **`instrument-check`** in the sense of
`CASE_SELECTION_CHARTER.md` §3 (a control whose answer is known independently of
the thing being tested) and is labelled so **at registration, before any
number**. It is not presented as a result, counts toward no challenge column, and
is not filmed.

## 2. THE CASE

    u = 1 − e^{λx} cos(2πy),   v = (λ/2π) e^{λx} sin(2πy),   p = ½(1 − e^{2λx})
    λ = Re/2 − √(Re²/4 + 4π²) = −0.963740544195769,   ν = 1/Re = 0.025

| item | value |
|---|---|
| domain | x ∈ [−0.5, 1], y ∈ [−0.5, 0.5] (ONE y-period), unit depth, `empty` front/back |
| top / bottom | `cyclic` (blockMesh `neighbourPatch`) |
| inlet (x = −0.5), outlet (x = 1) | `U fixedValue` = **face-averaged** exact velocity over each face's own y-span; `p fixedFluxPressure` |
| pressure level | `pRefCell 0`, `pRefValue 0` (p is not graded) |
| initial field | exact solution at the built mesh's own cell centres (from `0/C`) |
| solver | `simpleFoam`, laminar, `steadyState`, Gauss linear everywhere, `orthogonal` Laplacian/snGrad (non-orthogonality 0) |
| relaxation | U 0.7, p 0.3; **no `residualControl`** — the run goes to a fixed 4000 iterations |
| checkpoints | every 100 iterations → 40 samples of the graded quantity |

**Why face-averaged boundary data, stated because it is a choice:** with
Dirichlet velocity on every non-periodic boundary, `adjustPhi` refuses (fatal) a
net boundary flux above 1e−8 of the total. Face-centre values of the exact field
carry an O(h²) net flux; face-averaged values telescope to **zero to round-off**
(checked at every level by a control). The face-average differs from the
face-centre value by O(h²), the same order the scheme carries, and the
discretisation model in §5 imposes exactly the datum the solver sees.

**Mesh admissibility (MESH_STANDARD §3, §8.1).** Uniform Cartesian: the coarse
level was **BUILT AND `checkMesh`'d** on a scratch copy before this freeze — 1536
cells, max non-orthogonality **0°** against the 70° gate, max skewness
3.55e−15 against 4, `Mesh OK` (build_f17.py enforces both gates at every level
and writes `MESH_LINE.txt` from the built mesh, never from the request).

## 3. THE REFERENCE IS **NOT A PAPER**. IT IS A SUBSTITUTION.

Rule 15 requires title-page verification of every **retrieved** paper. This case
retrieves none. `exact_f17.py --selftest` substitutes the closed form into the
steady incompressible Navier–Stokes equations symbolically (sympy): continuity,
x-momentum and y-momentum residuals are **identically zero**. **Planted control:**
λ scaled by 1.1 makes the x-momentum residual **non-zero**, so the checker is shown
able to see a wrong solution. The module's numeric λ is required to agree with the
symbolic one to 1e−12. (Kovasznay's 1948 paper is not on this box and is not
cited as a source for any number here.)

## 4. THE LADDER — THREE LEVELS, WHICH IS THE STANDARD (§9.1)

Square cells, uniform, **h refines by exactly 2 in BOTH directions** (checked; a
departure refuses). `dim = 2`, r = 2.000 from cell counts.

| level | Nx × Ny | cells | h | E2 predicted (§5) | u(probe) error predicted |
|---|---|---|---|---|---|
| coarse | 48 × 32 | 1,536 | 1/32 | 1.785765e−03 | −9.152337e−04 |
| medium | 96 × 64 | 6,144 | 1/64 | 4.433814e−04 | −2.286448e−04 |
| fine | 192 × 128 | 24,576 | 1/128 | 1.106949e−04 | −5.708149e−05 |

Model orders across the ladder: **2.010, 2.002**. Predicted probe error is
sign-stable, so the u(probe) triple is predicted monotone (a sign change would
have refused registration of that gate).

**DECOMPOSITION SEED (required field): `none`.** Every level runs **serial on 1
rank**; `decomposePar` is not invoked at any level; there is no partition and no
RNG.

## 5. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to a prediction computed
from the scheme. Declared now; not measured, not fitted, not revisable after
first compute.

**The derivation.** The solver's discrete steady solution satisfies its stencils
exactly; the exact solution does not. `exact_f17.py::discrete_error` evaluates
simpleFoam's own uniform-Cartesian stencils on the exact field — Gauss linear
convection, Gauss linear orthogonal Laplacian, Gauss linear pressure gradient,
face-interpolated fluxes with the boundary datum of §2 — giving the momentum
residual r_h and the continuity residual d_h, both O(h²). The leading-order error
e_h solves the **linearised discrete equations** J_h e_h = −(r_h, d_h), assembled
with scipy.sparse (Rhie–Chow interpolated flux with a compact pressure Laplacian,
zero-error Dirichlet at inlet/outlet, cyclic in y, pressure level pinned by a
Lagrange multiplier) and solved to round-off (max residual ≤ 6.4e−15, a control).
The prediction is a function of the scheme and the grid and nothing else; the
model's own h² scaling (§4) is a control that refuses outside [1.7, 2.3].

**What the model omits, so the factor-3 window is a stated admission, not a
guess:** it is a linearisation; rAU in the Rhie–Chow term is the unrelaxed
central diagonal rather than the relaxed one (that term is O(h³) on a smooth
pressure); and no under-relaxation history enters. Three is the only free number
in this document.

**G-F17-1 — normalised L2 velocity error at the last checkpoint**

    E2 = √( mean over cells |U_h − U_exact(cell centre)|² ) / U0,   U0 = 1

Prediction at h_fine = 1/128: **1.106949e−04**.
**Band = [prediction/3, prediction×3] = [3.689829e−05, 3.320846e−04].**

**G-F17-2 — u/U0 at the probe (x, y) = (0.5, 0)**, bilinearly interpolated
between the four surrounding cell centres (the probe is never a cell centre at
any level; the interpolation error is O(h²) and is absorbed in the window).
Exact value **0.382372819953864** = 1 − e^{λ/2}.
**Band = exact ± 3 × 5.708149e−05 = [0.382201575482, 0.382544064426].**

**Registered prediction: both triples `CONVERGING` with observed order p ≈ 2
(the model says 2.01/2.00); fine values inside both bands → PASS.**

## 6. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING, and nothing else.
- **Rule 5 is reached through `grade_ladder` ONLY.** `grade_f17.py` carries
  **exactly one** `grade_ladder` call node, censused by AST at every entry; the
  text matcher is driven both ways on synthetic sources.
- **CONVERGENCE GATE: CLASS C**, all four elements
  (`CFD_CONVERGENCE_GATE_RULING_2026-08-25.md` §2), on the **graded quantity
  itself** sampled at every written checkpoint (100 iterations apart, 40
  samples). Sustained window **12 checkpoints = 1,200 iterations — justified,
  not inherited**: SIMPLE at α_p = 0.3 contracts the slowest relaxation mode by
  at least 1 − α_p per sweep, so 1,200 sweeps is > 400 e-foldings and a surviving
  transient cannot hide inside the window. Trend fit at 2.0e−4 relative drift;
  two-half stationarity on mean (1.0e−4) and variance ratio [0.2, 5]; **element 4:
  fewer than 20 samples EXITS 2.** All four limbs driven by a planted control.
- **Rule 5 limb (1):** a **census over every iteration inside the Class C
  window** of the solver's own initial residuals: **Ux, Uy ≤ 1e−6, p ≤ 1e−5**;
  the count above tolerance is reported. Not a two-point sample.
- **Completion (rule 4):** recorded rc = 0; an `End` line; `latest + Δt >
  endTime`; the fixed-count identity **`Time` lines == 4000**; `U` and `p`
  present at `4000/` and **each newer than the case's own `0/U`** (written last
  by the builder).
- **L-342 field classes (Sanaa's universal rule, `d4d0c29d`).** The grader
  declares **`PHYSICS_CRITICAL`** (log `End`/`Time` count, `RC.txt`, endTime
  fields + age guard, `0/C`, checkpoint `U` files, initial residuals) and
  **`INFRASTRUCTURE`** (`ClockTime`, box probes, `MESH_LINE.txt`, runner
  `STATUS`/`launcher.queue.out`/`LAUNCH_LOG` rows, calibration figures).
  **Refusals (exit 2) and verdicts key on PHYSICS_CRITICAL only.** A missing or
  inconsistent INFRASTRUCTURE field prints a **`BOOKKEEPING DEFECT`** line beside
  the verdict and **refuses the COST CLAIM only** — it can never produce NOT A
  RESULT. The selftest drives both directions: infrastructure files deleted →
  completion unchanged + defect lines + cost claim refused; rc corrupted, or
  `End` deleted with rc 0 → the level is **NOT A RESULT**. A recorded non-zero rc
  is a crash and a finding (NOT A RESULT); an absent `RC.txt` is PENDING.
- **Planted-zero controls (rule 3)**, into a copy of the **real artifact**, read
  back with the **real parser**, refusing with exit 2: a known Ux offset must move
  E2 to its predicted value to 1e−14 and u(probe) by exactly the offset (1e−12).
- **`assert` census: ZERO**, by AST parse, across `grade_f17.py`,
  `exact_f17.py`, `foam_io_f17.py`, `build_f17.py`; the counter is shown able to
  count a planted assert. **Hard `-O` refusal at entry, `sys.exit(2)`.**
- **Success messages print INSIDE the passing branch.**
- **Guards.** The launcher and the builder both **REFUSE** a pre-existing `0/` or
  numeric time directory; neither deletes. **No `rm -rf`, no `rmtree` on any case
  directory** — the grader's `rmtree` acts only on `tempfile.mkdtemp` scratch.
  The builder refuses a destination inside the tracked case tree.
- **`--preflight` fires nothing, including `blockMesh`** (and does not call the
  builder). Measured this session: rc 0, run root reported ABSENT.
- **Solver dictionaries are cross-checked** at every grader entry: ν on disk ==
  `exact_f17.NU`, `residualControl` absent, `endTime` and `writeInterval` equal
  the registered values.

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Driven at zero compute through the real readers on files in the pinned write
format (`internalField nonuniform List<vector>` ⏎ N ⏎ `(` … `)`, pinned against
real solver output on this box,
`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, which the reader parses
at selftest as a live control):

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F17-1 | exact + **1×** the model error field | 1.106949e−04 | [3.690e−05, 3.321e−04] | **inside** |
| G-F17-1 | exact + **40×** the same | 4.427796e−03 | same | **outside** |
| G-F17-2 | exact + **1×** the same | 0.382501 | [0.382202, 0.382544] | **inside** |
| G-F17-2 | exact + **40×** the same | 0.380270 | same | **outside** |

**Honest limit:** the rows are built on format-faithful synthetic files; the
*format* is pinned against real output, the *values* are constructed.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** `ClockTime`, not
`ExecutionTime`.

Cell-iterations: 1,536 + 6,144 + 24,576 cells × 4,000 = 129.0 M. **Rate basis:
3.55 µs per cell-iteration, read from ONE lab record of a DIFFERENT case**
(`verification/runs/FPE_DIAG_runs/BL1/log.simpleFoam`: 3,520 cells, 2,000
iterations, serial, ClockTime 25 s) — a measured rate applied here, so the figure
is **derived, not measured** on this case.

| level | projected serial s | core-min |
|---|---|---|
| coarse | 22 | 0.36 |
| medium | 88 | 1.46 |
| fine | 350 | 5.82 |
| **total** | **458** | **7.6** |

**REGISTERED CAP: 40 core-minutes** (5.2× headroom; the width is the admission).
**Derived dollars at $0.0513/core-h: $0.0065 estimate, $0.034 at the cap —
DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
pre-authorisation. **`cost_basis: derived not measured.`**

**The cap is checked incrementally after each level** and **projected before
each level** from this invocation's own box probe; on a crossing the launcher
**HALTS at exit 3** and unlaunched levels stay `PENDING`. Launcher and grader
carry the same cap and refuse to start if they disagree.

**Scratch smoke arm, reported:** one real `simpleFoam` iteration on a scratch copy
of the coarse level (built by `build_f17.py` into the scratchpad, never the case
tree): rc 0, reached `Time = 1`, `End` written, ClockTime 0 s (wall 0.05 s) —
**≈0.01 core-min including blockMesh/checkMesh/postProcess**, not retained, not a
measured history, not a result. It is what shows the cyclic patches,
`fixedFluxPressure`, `writeCellCentres` and the templated `0/U` are consumed by
the real solver.

**At completion** actual/predicted lands as a row in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F17_runs` → **absent** at the
time this file was written and at `--preflight` (which prints the same reading).
No `RC.txt`, `log.*` or numeric time directory exists under
`cases/F17_kovasznay/` (`find -regex` returned only the tracked template
directory `case/0`).

## 10. NEVER RUN — THE EVIDENCE

- Tracked paths enumerated with `git ls-tree -r HEAD --name-only`: **13,862**;
  matches for `F17|kovasznay`: **0** (planted control: a known tracked path is in
  the enumeration).
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (531 entries)
  **0**; `/home/ubuntu/closure-data` (22) **0**;
  `/home/ubuntu/closure-challenge-benchmark` (7) **0**.
- `verification/runs/` holds no `F17*` directory.

## 11. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F17_kovasznay/run_f17.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F17_kovasznay/grade_f17.py --prereg-commit=<sha>`. A queue entry
is **held until the supervisor acknowledges the freeze sha** (a live queue
runner fires validated entries), then dropped as a second commit citing this
commit's full sha.

## 12. WHAT IS **NOT** REGISTERED HERE

- No turbulence claim; no claim about p (not graded); no re-grade of any row.
- No amendment to any standard or charter.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).

---

## AMENDMENT 1 — 2026-08-26, PRE-FIRST-COMPUTE (version 1.0 → 1.1)

**Lines whose number changed above this section: 0.** Appended at the foot;
nothing above is edited, struck or renumbered. **This amendment changes NO
gate, NO threshold, NO band, NO cap and NO label.** Legal under rule 2 §2b
because no compute has occurred.

**Condition, and how it was checked (in the writing invocation):**
`test -e /home/ubuntu/Certonomous/verification/runs/F17_runs` → **ABSENT**;
`find cases/F17_kovasznay -name RC.txt -o -name 'log.*'` → **0** files; no
numeric time directory under the case tree.

**The defect.** `run_f17.sh` line 20 sets `set -u`, which was still in force at
the line that sources `/usr/lib/openfoam/openfoam2606/etc/bashrc`. That bashrc
reads an unbound `WM_PROJECT_DIR` at its line 184; under `-u` the sourced script
aborts and **the launcher shell dies at that line with no `ABORT` message** —
after the instrument checks, before any level. **This is the face that killed
F16 attempt 1 today** (`STATUS.F16.attempt1` rc = 1, 15:56:10Z; L-339).
`--preflight` returns 0 because it exits before the source line;
`check_launcher_can_launch.py` does not see this face. Found by the cfd
supervisor's check-1 read of `feab0ad7`. Driven, not assumed:
`bash -c 'set -u; . <bashrc>'` → `line 184: WM_PROJECT_DIR: unbound variable`;
`bash -c 'set -u; set +u; . <bashrc> || exit 1; set -u; which simpleFoam
blockMesh icoFoam'` → all three resolve, rc 0.

**The repair.** `set +u` immediately before the source line and `set -u`
immediately after it, with a dated comment in the launcher citing L-339 and
F16 attempt 1. No other line of the launcher changes; the grader, the builder,
the exact module and the case dictionaries are untouched.

**Driven after the edit:** `check_launcher_can_launch.py --worktree` on the
amended launcher → rc 0; `bash -n` parses; the launcher's `--preflight` path is
unchanged.
