# T16 — developing laminar MIXED CONVECTION in a vertical parallel-plate channel with asymmetric isothermal walls, EXACT tier: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T16** — the rung that puts a graded number into the
capability grid's **`mixed convection × laminar × 2D`** cell, which at HEAD
`c9ff33d9` reads **`CAN NOT DO — not attempted`**. Verdict vocabulary fixed by
`CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING.** Written by a heat-transfer lane on the supervisor's dispatch;
decisions in it are `[lab-attributed]`. **Nothing here has been sent, filed,
submitted, uploaded, registered or posted outside this box, and nothing in it
may be (`CLAUDE.md` rule 7).**

## 0. What this rung is, what it is not, and what a killed lane left

**Laminar MIXED convection between two vertical parallel plates held at
different uniform temperatures, with a through-flow, solved with
`buoyantBoussinesqSimpleFoam` in 2-D.** Fluid enters the bottom of a channel of
gap `b` with a uniform (plug) upward velocity `U0`; the hot wall is at `x = 0`,
the cold wall at `x = b`, gravity is `(0, −g, 0)`; the flow develops and the
comparator grades **one row, at a registered station 48 gaps downstream**,
against the fully developed profile that this rung's own module **derives from
the Boussinesq equations**.

> **T16 earns a verdict for MIXED CONVECTION, LAMINAR, 2-D, EXACT tier** — the
> capability-grid cell *mixed convection × laminar × 2D*
> (`docs/capability/heat-transfer_GRID.md`). It earns **nothing turbulent**,
> **nothing 3-D**, **nothing at or past the flow-reversal threshold**, and
> nothing for the entrance region, which is solved but not graded.

**THE REFERENCE PAPER IS NOT ON DISK AND IS NOT USED.** The physics of this rung
is the one Aung & Worku (1986) are known for, and the lane was dispatched under
that name. `docs/papers/` holds no such paper — a grep for `aung` and for
`worku` across `docs/papers/` returns nothing, and
`docs/papers/buoyant_natural_convection/` holds nine papers, none of them it.
**No number in this rung is transcribed from any paper.** The referent is
DERIVED in `exact_t16.py` and re-derived there by an independent route that
refuses if the two disagree, exactly as T15's Morton–Taylor–Turner referent and
T13's Batchelor referent are. `CLAUDE.md` rule 15 (title-page verification)
therefore has nothing to bite on: **there is no retrieved artifact to verify.**
The name "Aung & Worku" appears in this rung only as the name of a
configuration, never as the source of a value; the flow-reversal threshold
`G = 72`, which is the number that configuration is most cited for, is
**derived** in `exact_t16.py` from `dU/dY|_{Y=1} = 6 − G/12 = 0` and is checked
by the module's own selftest.

**What the killed lane left, disclosed and repaired.**
`verification/runs/T-family/T16_runs/exact_t16.py` was on disk, **untracked**,
when this lane arrived (mtime 2026-08-26 22:57, sha256
`38206511a343795373ff9078f2020ae197994aa1ad2f5d594cb8a81baf5c5edb`), left by a
registration lane killed before it registered anything. It was read in full and
its derivation re-derived independently, line by line. **It failed its own Route
B — `python3 exact_t16.py --selftest` returned rc 1.** Three defects were
repaired **before any freeze, before any solver ran, and with nothing yet
frozen**; §9 states them, and the full unified diff is committed beside the
module at `verification/runs/T-family/T16_runs/exact_t16_REPAIR.diff`.

## 1. The referent — DERIVED, not transcribed (`exact_t16.py`)

Gap `b` in `x`, flow upward in `y`, gravity `(0, −g, 0)`, hot wall `T_h` at
`x = 0`, cold wall `T_c` at `x = b`. With `Y = x/b`, `U = v/U0` where `U0` is the
**mean** velocity, `theta = (T − T_c)/(T_h − T_c)`, and the single group

    G = Gr/Re = g beta (T_h - T_c) b^2 / (nu U0),
    Gr = g beta (T_h - T_c) b^3 / nu^2,   Re = U0 b / nu.

**ENERGY.** Fully developed means no `y` dependence, so `v dT/dy = alpha T''`
reduces to `T'' = 0` and `theta(Y) = 1 − Y`, LINEAR. The fact this rung leans on
is stronger: *a linear `T` with `dT/dy = 0` satisfies the energy equation for ANY
velocity field*, and it also satisfies both wall Dirichlet conditions and the
`zeroGradient` conditions this case puts on the inlet and the outlet. **The
temperature field is therefore the exact continuous solution of the whole
channel, entrance region included, and only the HYDRODYNAMIC development
remains.**

**MOMENTUM.** `0 = −dp/dy + mu v'' + rho g beta (T − T_c)` gives, dimensionless,

    U'' + G theta(Y) + P = 0,   P = -(b^2/(mu U0)) dp/dy,
    U(0) = U(1) = 0,   integral_0^1 U dY = 1   (U0 IS the mean),

whose solution is

    P = 12 - G/2
    U(Y) = 6 Y (1 - Y) - (G/12) Y (1 - Y) (2Y - 1)
    dU/dY = 6 - 12 Y + (G/12)(6 Y^2 - 6 Y + 1)
    U'(0) = 6 + G/12,   -U'(1) = 6 - G/12
    tau_hot / tau_cold = (6 + G/12) / (6 - G/12)
    FLOW REVERSAL at the cold wall begins at G = 72.

**THE REGISTERED POINT IS `G = 48`, exactly two thirds of the derived reversal
threshold**, where the closed form collapses to `U(Y) = 10Y − 18Y² + 8Y³` and

| quantity | exact value at `G = 48` |
|---|---|
| `U(0.25)` | **1.5** exactly |
| `U(0.75)` | **0.75** exactly |
| `tau_hot / tau_cold` | **5** exactly |
| `Y_max` (peak location) | `(36 − sqrt(336))/48` = **0.368118692087013** |
| `P` | `12 − 24` = **−12** |
| `integral_0^1 U dY` | **1** exactly |

`Y_max < 0.5` — the peak sits **toward the HOT wall**, which is the physics, and
which is how repair R2 below was caught.

**ROUTE B, run before any comparison** (`exact_t16.py --verify`; every failure
`sys.exit(2)`; measured values from the selftest, identical under `python3` and
`python3 -O`):

- **B1** the closed form satisfies `U'' + G theta + P = 0` — worst
  centred-difference residual **3.612e-11** at BOTH stencil widths (the
  difference is exact on a cubic, so the residual must sit at round-off at both).
- **B2** `U(0) = U(1) = 0` and Simpson's integral **0.9999999999999996**,
  `|1 − I| = 4.44e-16`.
- **B3** the tabulated values above, each to `< 1e-13`.
- **B4** an **INDEPENDENT RK4 shooting route** on `y1' = y2`,
  `y2' = −(P + G theta)`: `U'(0)` recovered **9.999999999999915** against the
  closed **10**, worst profile deviation **8.741e-14**, `|mean − 1|`
  **4.075e-14**. RK4 is exact to round-off here because the right-hand side is
  linear in `Y`.
- **B4b** the finite-volume model that GROUNDS THE BANDS is second order and
  converges ON the closed form: errors **1.200e-05 / 3.000e-06 / 7.500e-07** at
  `N = 250/500/1000`, ratios **4.0001** and **4.0000** (required in `[3.5, 4.5]`),
  Richardson remainder **−6.067e-12** against a `1e-09` floor. **This is what
  entitles the discrete model to set a pre-registered band.**
- **B5** a planted **1 %** mutation of `G` is REFUSED by B3 (worst `U` deviation
  3.750e-03, shear-ratio deviation 1.224e-01, `Y_max` deviation 8.594e-04).

## 2. The registered case (`build_t16.py`)

| quantity | value |
|---|---|
| solver | `buoyantBoussinesqSimpleFoam`, **serial, 1 rank** |
| turbulence | `laminar` |
| gap `b` | 0.02 m (`x`) |
| height `H` | **64 b** = 1.28 m (`y`) |
| depth | 0.001 m, one cell, `empty` front/back |
| `nu` | 1.5e-05 m²/s |
| `Pr` | 0.71 |
| `beta` | 1/300 K⁻¹ |
| `g` | 9.81 m/s², `(0 −9.81 0)` |
| `TRef` | **300.0 K = the COLD wall** (the referent's `theta` datum) |
| `Re = U0 b / nu` | **100** |
| `U0` | **0.075 m/s**, the mean and also the inlet plug speed |
| `G = Gr/Re` | **48**, DERIVED, margin to reversal **1.5000** |
| `dT = T_h − T_c` | **4.1284403669724767 K**, DERIVED from `G` |
| `T_hot` / `T_cold` | 304.1284403669725 / 300.0 K |
| graded station | **48 b** from the inlet (row index `48 N`) |
| witness rows | station **−8b, −4b, +4b, +8b** |
| `ddt` | `steadyState` |
| `div(phi,U)` | `bounded Gauss linearUpwind grad(U)` |
| `div(phi,T)` | `bounded Gauss limitedLinear 1` |
| `p_rgh` solver | PCG / DIC, tol 1e-10, relTol 0.01 |
| `(U\|T)` solver | PBiCGStab / DILU, tol 1e-12, relTol 0.01 |
| relaxation | `p_rgh` 0.7, `U` 0.3, `T` 0.5 |
| `residualControl` | **NONE** (L-141): the run length is `endTime` by registration and convergence is judged by the frozen comparator from the residual history |

**BOUNDARY CONDITIONS, and the one that is not obvious.** Walls: `noSlip`,
`fixedValue` `T`, `fixedFluxPressure` `p_rgh`. Inlet: `U` `fixedValue (0 U0 0)`,
`T` `zeroGradient`, `p_rgh` `fixedFluxPressure`. Outlet: `U` `zeroGradient`, `T`
`zeroGradient`, and **`p_rgh` `prghPressure` with `p uniform 0` and `rho rhok` —
NOT `fixedValue uniform 0`.** In this solver `p_rgh = p − rhok (g·h)` with
`rhok = 1 − beta (T − TRef)`, so at a fixed height `p_rgh` varies ACROSS the
channel wherever `T` does; at this outlet that variation is
`beta dT g H = (1/300)(4.1284)(9.81)(1.28) = 1.73e−01 m²/s²`. Pinning it uniform
forces that to zero. **This was MEASURED on the disclosed scratch probe (§8) as
a violent last-row disturbance carrying REVERSED cells, and as an outer residual
that stalled near 1.5e−03 and never converged.** `prghPressure` is the
consistent statement, and with it the residual collapses (§8).

**THE L-341 HAZARD DOES NOT ARISE.** Every condition here is `fixedValue` /
`zeroGradient` / `noSlip` / `fixedFluxPressure` / `prghPressure` — no `mixed`
(Robin) condition, so no coefficient contains the mesh spacing and nothing has to
be recomputed per level. `build_t16.py --check-levels` makes that executable: it
REFUSES if any `0.orig` field carries a `mixed` entry, and REFUSES unless the
three levels share every physical constant and differ ONLY in `N`. Both arms are
driven by `--selftest`.

## 3. The mesh family and the triple

`N × 64N` **SQUARE** cells, `r21 = r32 = 2` exactly in both directions:

| level | case | `N` | `Ny` | cells | `endTime` | `writeInterval` |
|---|---|---|---|---|---|---|
| c | `T16_MC_c` | 20 | 1 280 | **25 600** | 10 000 | 1 000 |
| m | `T16_MC_m` | 40 | 2 560 | **102 400** | 20 000 | 2 000 |
| f | `T16_MC_f` | 80 | 5 120 | **409 600** | 40 000 | 4 000 |

Built before the freeze (`MESH_STANDARD.md` §8.1): `blockMesh` rc 0 and
`checkMesh` **Mesh OK** on all three, non-orthogonality 0, skewness 0, aspect
ratio 1 by construction. `polyMesh` is not committed; the dictionaries and the
birth certificates (`BUILD.txt`, `log.blockMesh`, `log.checkMesh.build`) are.

**This rung HAS a grid triple and is graded under rule 5 in full.** `grid_triple`
is not disclaimed anywhere; the comparator REFUSES a registration that claims
otherwise.

## 4. Completion, and the two field classes (L-342)

`mark_done_t16.py` declares both classes in prose, in the file, in the shape
`docs/L342_GRADER_AUDIT.md` names as the model
(`T3_runs/mark_done_t3_rff.py:8-18`), and `--selftest` drives **both halves**.

**PHYSICS-CRITICAL** — each a conjunct; any failure is NOT DONE and no marker:
P1 the solver's `rc` **value** is 0; P2 `log.solve` carries an `End` line; P3 the
last written time == `endTime` from the case's own `system/controlDict`; P4 the
registered fields `T U p_rgh phi` are present at that time; **P5 the AGE GUARD —
every field at `endTime` is NEWER than the case's own `0/T`.**

**INFRASTRUCTURE** — reported NOT MEASURED, never a conjunct and never a
refusal: **the `ExecutionTime` line count**, `wall_s`, `timeout_s`, `ranks`,
`core_min`, `capped`, `checkmesh_rc`, `solver`, `solver_path`, `note`,
`started_utc`, `ended_utc`, ledger rows, pids, log presence.

**The `ExecutionTime` count is INFRASTRUCTURE here, deliberately.** That is the
misclassification the L-342 audit found in `T14_runs/mark_done_t14.py:14-16` and
in 27 other heat-transfer comparators; a solver that reached `End` at `endTime`
with every field written and newer than `0/T` produced the physics whatever its
log printing did. Both a SHORT count (39 of 40) and a LONG count (42 of 40, the
petsc4Foam shape) are driven in the selftest and both still return DONE with the
count disclosed NOT MEASURED.

**RULING R-RC applied: the `rc` VALUE is physics, the `rc` RECORD is
infrastructure.** An absent STATUS is NOT MEASURED, not an automatic refusal; the
case can still be DONE, but only on all four remaining conditions P2–P5, and
`rc = 0` is then printed **as an inference and labelled as one**. A
`FOAM FATAL ERROR`, `FOAM FATAL IO ERROR`, `Segmentation fault`,
`Floating point exception`, `Aborted` or signal token anywhere in `log.solve`
**still REFUSES**, with or without an rc record. All three arms are driven.

## 5. What is graded

Every row is read on the **station row** at `y = 48 b`.

| row | quantity | reference | band | grading |
|---|---|---|---|---|
| **G1** | `v(Y = 0.25)/U0`, 4-point Lagrange at cell centres | **1.5** exactly | **±2.4e−04 RELATIVE** | Roache triple, rule 5 |
| **G1b** | `Y_max`, the peak location from the cubic through the 4 cells around it | **0.368118692087013** | **±2.4e−04 ABSOLUTE** | Roache triple, rule 5 |
| **G3** | `tau_hot / tau_cold` from the half-cell wall gradients of `v` | **5** exactly | **±1.2e−03 RELATIVE** | Roache triple, rule 5 |
| **G2** | RMS over the row of `(T − T_lin)/dT` | **0** | **1.0e−06 ABSOLUTE FLOOR** | EXACT-class floor |

**Every band is 3.0× the DERIVED fine-level discretisation error** of the same
finite-volume model whose second-order convergence onto the closed form B4b
verifies. The ladder that grounds them, printed by the comparator's own selftest
and re-derived there rather than asserted in prose:

| row | band | derived error at c (N=20) | at m (N=40) | at f (N=80) | f INSIDE | c and m OUTSIDE |
|---|---|---|---|---|---|---|
| G1 | 2.400e−04 | 1.256e−03 | 3.129e−04 | **7.815e−05** | **True** | **True** |
| G1b | 2.400e−04 | 1.250e−03 | 3.125e−04 | **7.812e−05** | **True** | **True** |
| G3 | 1.200e−03 | 6.000e−03 | 1.500e−03 | **3.750e−04** | **True** | **True** |

**G2 is the one EXACT-class row.** The linear temperature field is an exact
solution of the continuous problem for ANY velocity field, so it lies in the null
space of the scheme's truncation error, its triple is EXACT / DEGENERATE by
construction, and rule 5 clause (2) would return NOT A RESULT for a row that
cannot be wrong by discretisation. **Its triple state is PRINTED; its verdict is
the floor, after gate (1).** G1, G1b and G3 are NOT exact-class and are graded by
rule 5 in full.

## 6. The gate — gate (1), and every control

Every level must pass every one of these, else **every row is NOT A RESULT**
under rule 5 clause (1).

| control | statement | floor |
|---|---|---|
| **C_CONV** | initial residuals of `Uy`, `T`, `p_rgh` at EVERY iteration of the final 10 % of `endTime`. `Ux` is a near-degenerate cross-channel component and is **REPORTED, never gated** (L-338) | **1e−06** — the family's floor, unweakened, registered because it was MEASURED REACHABLE (§8) |
| **C_PLAT** | `\|G1(endTime) − G1(endTime − writeInterval)\| / G1` | **1e−07** |
| **W1 (a)** | development witness, WHOLE-ROW max-norm of `v/U0` between each witness row and the station row | **2e−04** |
| **W1 (b)** | the same comparison **ON THE GRADED READER ITSELF** (the 4-point Lagrange at `Y = 0.25` that G1 is) — an order of magnitude tighter, because that is the number the verdict depends on | **2e−05** (MEASURED 2.9e−06 over the full 8 b span, §8) |
| **W1 (c)** | the same in `T/dT`, where the field is exact | **1e−06** |
| **C_MASS** | the station row's mean of `v` against `U0` — the referent normalises on the MEAN, so a row whose mean is not `U0` is not the profile the closed form describes | **1e−06** relative |
| **C_REV** | **NO REVERSED CELL** on the station row: `v > 0` in every cell | 0 cells |
| **C_G** | operand identity (L-331): `nu, Pr, beta, TRef, g, T_hot, T_cold, b, U0, N` are READ FROM THE CASE FILES, printed, and `G = Gr/Re` recomputed from them must be 48, strictly below the DERIVED 72 | 1e−09; **REFUSAL**, not a gate |
| **C_ORDER** | the station row's `T` must fall monotonically hot→cold with slope `−dT` per unit `Y`; a transposed (y-fastest) ordering shows a constant row | 1e−06; **REFUSAL** |

**W1 is what entitles this rung to compare a solve against a FULLY DEVELOPED
closed form** — the witness, not an assumed entrance-length correlation.

**THE ROACHE FLOORS ARE THE SHARED NAMES.** `STAGNANT_FLOOR = 0.5` and
`P_MIN = 0.05` are **imported by name** from `scripts/roache_triple.py`
(`MESH_STANDARD.md` §10.5, chief ruling `01967a7b`); the comparator defines
neither, the triple arithmetic is `roache_triple.gci_equal` itself, and the
comparator **REFUSES if the registered JSON and the import disagree** — driven in
the selftest by mutating the registered `P_MIN` to 0.5. `FS = 1.25`, `r = 2`,
`dim = 2`.

**PLANTED-ZERO CONTROLS (rule 3), SIZED AND SHAPED PER READER (L-340).** A
**POINT** plant for the point readers G1 / G1b / G3 / W1; an **ALL-ROW
ALTERNATING-SIGN** plant for the RMS reader G2. The alternation is the L-340
point made sharper than T13 made it: a reader that RMSs about a *fitted* line is
blind to a constant offset by construction, so the plant is shaped to what the
reader can see rather than to what is convenient to write. The registered plant
is `1.234e−03 × the reader's scale`. **Both arms**: the negative arm re-reads
identical bytes and REFUSES a reader that does not return the identical number;
the positive arm drives a descending ladder `1, 1e−1, 1e−2, 1.234e−3, 1e−4,
1e−5, 1e−6, 1e−7` through the same production reader, records the smallest
visible magnitude, and REFUSES if the registered plant is invisible. A blind
reader mutant is driven in the selftest and the control REFUSES it. The
comparator additionally DISCLOSES what a constant all-row plant does to G2 — this
reader RMSs about the REGISTERED linear profile, not about a fit, so it *does*
see a constant (measured 1.234e−03 response) — and the registered plant
alternates anyway, so the control does not depend on that property holding.

## 7. The launcher and its guard

`run_one_t16.sh`, the `run_one_t13.sh` form, unchanged in substance: the solver
runs in the wrapper's **foreground** under `timeout` so `$?` is the solver's own
status; `rc` is captured INSIDE and written to `STATUS.<case>`; `capped` is the
independent expiry witness and an INFRASTRUCTURE field; a **pre-flight refusal
writes NO STATUS**; the registered cap is READ from `T16_registered.json` and a
`--timeout` that is not EQUAL to it is REFUSED (a cap is neither widened nor
narrowed at launch); `--ranks` must equal the registered 1; time directories are
matched by a **regex with fullmatch semantics**, never a shell glob; the OpenFOAM
bashrc is sourced with `set -u` lifted; an existing `STATUS.<case>` is REFUSED;
the **lineage-aware foreign-process guard** (T10aR2 AMENDMENT 1, `9fa66065`)
excludes the launcher's own ancestors and descendants and refuses any foreign
process holding the case directory as cwd; `0/` is created from `0.orig` and
**`0/T` is touched LAST** (the age-guard datum); and `exit "$RC"` is the last
line.

## 8. Cost — MEASURED basis (`CLAUDE.md` rule 12)

**THE RATE IS MEASURED ON A SCRATCH COPY OF THIS EXACT CASE, ON THIS BOX,
OUTSIDE THE REPOSITORY.** Four scratch probes were run (all outside the
repository; `build_t16.py --probe` REFUSES a target inside it, and no registered
tree was touched):

| probe | configuration | what it measured |
|---|---|---|
| 1 | `ASPECT` 96, PCG/DIC, `fixedValue uniform 0` outlet | **development length**: `G1` settles from 32 b downstream and is flat from 40 b to 92 b; **outlet artifact**: the last ~2 b carry a violently distorted profile with `min v/U0 = −1.87` |
| 2 | `ASPECT` 64, GAMG relTol 1e−3, `p_rgh` 0.3 / `U` 0.7 | outer residual **limit-cycled near 1.1e−02 for 3 600 iterations**; NOT registered |
| 3 | `ASPECT` 64, GAMG, `prghPressure` outlet | still oscillating near 1e−02; NOT registered |
| **4** | **the registered configuration exactly** | **the registered rate, the residual collapse, and the reversal and development numbers below** |

**Probe 4, the registered configuration, `N = 20`, 25 600 cells, serial, `nice
15` on a box at load average ≈ 17:**

- **rate = 379.13 core-s / (25 600 cells × 3 804 iterations) = 3.8932e−06 core-s
  per cell-iteration**, MEASURED. This is a **contended** figure — three peer
  solvers were live throughout — and contention can only inflate it, so it is
  conservative in the safe direction.
- **the residual collapses**: `p_rgh` initial residual 5.3e−03 at 1 600
  iterations, then **2.0e−05 → 6.4e−06 → 2.7e−06 → 1.1e−06 → 4.7e−07 by ~3 400
  of the registered 10 000**. This is why C_CONV is registered at the family's
  **1e−06** and not weakened.
- **no reversal anywhere in the field**: `min v/U0 = +0.049524`.
- **mass**: the row mean of `v/U0` is **1.00000000** at every station read.
- **development**: `G1` relative error is `+1.2506e−03` at 40 b, `+1.2535e−03` at
  48 b, `+1.2546e−03` at 56 b — a spread of **2.9e−06 over the full 8 b span**,
  which is what W1 (b) is registered at 2e−05 against. **And the value itself is
  `+1.2535e−03` against the DERIVED expectation `+1.256e−03` at `N = 20` — 0.2 %
  apart, before this rung has run a single registered iteration.**

**THE REGISTERED COST.** POINT = cells × `endTime` × 3.8932e−06 / 60; CEILING
carried at T4's measured `kOmegaSST` rate 5.874e−06 on the same solver (C-119);
caps are hang guards above the ceiling.

| case | cells | `endTime` | **POINT core-min** | ceiling core-min | **CAP core-min** | `timeout_s` |
|---|---|---|---|---|---|---|
| `T16_MC_c` | 25 600 | 10 000 | **16.611** | 25.062 | **40** | 2 400 |
| `T16_MC_m` | 102 400 | 20 000 | **132.888** | 200.499 | **300** | 18 000 |
| `T16_MC_f` | 409 600 | 40 000 | **1 063.103** | 1 603.994 | **2 400** | 144 000 |
| **TOTAL** | | | **1 212.602 core-min = 20.210 core-h** | 1 829.6 | **2 740 = 45.7 core-h** | |

**USD: 20.210 core-h × $0.0513/core-h = $1.0368 — DERIVED, NOT MEASURED**
(reported-by-owner rate; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation, and costed
regardless (rule 12). **An overrun stops the run; it does not get a new budget.**
The estimate-versus-actual comparison required by rule 12 lands in
`docs/COST_CALIBRATION.md` at completion.

## 9. The three repairs to `exact_t16.py`, disclosed in full

The module was **untracked and unfrozen** when repaired, no solver had run, and
nothing in this rung was frozen — so `CLAUDE.md` rule 6 does not apply and no
amendment is owed. The full unified diff is committed at
`verification/runs/T-family/T16_runs/exact_t16_REPAIR.diff` (138 added lines,
17 removed) against the as-found sha256 recorded in §0.

- **R1 — `dUdY` carried a MINUS on the `(G/12)` group.** It returned
  `U'(0) = 6 − G/12 = 2` instead of `6 + G/12 = 10`, which **swapped the two
  walls** and put the steeper shear at the COLD wall. That is the wrong physics.
  Verified against a central difference of `U()` at `Y = 0, 0.25, 0.5, 0.75, 1`:
  `+10, +2.5, −2, −3.5, −2`.
- **R2 — `Y_max` built its quadratic from R1's wrong derivative** and returned
  **0.6319** (peak displaced toward the COLD wall) instead of **0.3681** (peak
  toward the HOT wall). Its own docstring's quadratic `24Y² − 36Y + 10` was
  right; only the code disagreed with it.
- **R3 — B4 held a SECOND-ORDER finite-volume model to a `1e−09` tolerance that
  is unreachable by construction** (the truncation error at `N = 2000` is ~1e−07),
  so `verify()` refused every call it was ever given. B4 is now the RK4 route at
  1e−12; the FV model's convergence became B4b.

**The independent confirmation that R1 and R2 are RIGHT and not merely
different:** after the repair the DISCRETE model's own `Y_max` error falls
**1.250e−03 → 3.125e−04 → 7.812e−05** at `N = 20/40/80` — exactly `h²` onto the
repaired reference. Against the as-found reference it sat at a constant
**−2.64e−01** and converged onto nothing.

## 10. Predictions and falsifiers — the freeze's entire evidentiary content

| id | prediction | falsifier |
|---|---|---|
| **P1** | G1, G1b and G3 triples **CONVERGING**, observed order `p` in `[1.5, 2.5]`; derived expectation `p = 2.000` on all three | any triple DIVERGENT / STAGNANT / OSCILLATORY / EXACT → NOT A RESULT under rule 5 (2) |
| **P2** | G1 relative deviation at `f` in **`[+5.47e−05, +1.02e−04]`** (the derived `+7.815e−05` within 30 %), **POSITIVE** sign; `c` and `m` OUTSIDE the ±2.4e−04 band | a value outside that interval, or a negative sign |
| **P2b** | `Y_max` error at `f` in **`[−1.02e−04, −5.47e−05]`** (the derived `−7.812e−05` within 30 %), **NEGATIVE** sign | as above |
| **P2c** | `tau_hot/tau_cold` relative deviation at `f` in **`[+2.63e−04, +4.88e−04]`** (the derived `+3.750e−04` within 30 %), **POSITIVE** sign | as above |
| **P3** | **NO FLOW REVERSAL** anywhere on the station row; `v > 0` in every cell and the cold-wall shear positive. `G = 48` is exactly 2/3 of the DERIVED threshold 72 | a reversed cell at the station falsifies either the derivation or the solve, and the rung reports it as such |
| **P4** | W1 under **2e−05 ON THE GRADED READER** and under 2e−04 in the row max-norm, on every level | a level that fails it is not developed and is NOT A RESULT — it is not re-graded at a further station |
| **P5** | G2 RMS `< 1e−07` at `f` — the linear temperature field is exact for any velocity field | a larger RMS means the temperature field is not the one the referent assumes |
| **P6** | all three levels meet C_CONV (1e−06) and C_PLAT (1e−07) within their registered `endTime` | if not, the rung is NOT A RESULT and says so; the run is **not** extended past its cap |

**The sharpest single number in this document:** the derived expectation for G1
at `N = 20` is `+1.256e−03`, and probe 4 measured `+1.2535e−03` at the registered
station. If the registered `f` level does not land on `+7.815e−05` within 30 %,
the derivation, the discretisation model, or the solve is wrong, and this
document was committed before any of them could be adjusted to agree.

## 11. The FREEZE SET

The grading path is fixed at this commit (rule 2). These are the git blob hashes
of the frozen instruments; `git hash-object <path>` reproduces each, and
`scripts/check_comparator_freeze.py` enforces that the file that ran is the file
that was frozen.

| file | git blob | what it fixes |
|---|---|---|
| `verification/runs/T-family/T16_runs/exact_t16.py` | `f1591a440cfddd9e7eb1a4ba87a94d30bd2f46ba` | the DERIVED referent and its Route B (B1 B2 B3 B4 B4b B5); the comparator's two point readers live here too, so the band model and the graded number come off the SAME interpolation |
| `verification/runs/T-family/T16_runs/exact_t16_REPAIR.diff` | `3b6f2803ef08e18ad8e5f80bf2eaa5bc89a14f5b` | the full unified diff of the three repairs of section 9, against the as-found untracked module |
| `verification/runs/T-family/T16_runs/build_t16.py` | `e7ed305e393356b1b76494fd5ed8f602c834fef0` | the case generator, the level guards, and the writer of T16_registered.json |
| `verification/runs/T-family/T16_runs/T16_registered.json` | `32816560e633bc300d05bf557d5ef9390a025c22` | every registered number in one machine-readable place: physics, levels, bands, floors, controls, predictions, cost, field classes |
| `verification/runs/T-family/T16_runs/analyse_t16.py` | `9054d452b43ddda60c2bb187edc762d698a595ec` | THE COMPARATOR. apply_gate() is the only function that writes a verdict |
| `verification/runs/T-family/T16_runs/mark_done_t16.py` | `2ae1605c7983e379d586467a8ffb4890d0d1b20d` | the strict completion rule with the two L-342 field classes declared in prose and ruling R-RC applied |
| `verification/runs/T-family/T16_runs/run_one_t16.sh` | `a16b9a419a6fee0c0ea906ab8232756cebccd1ce` | the launcher: rc-in-wrapper, registered-cap equality, lineage-aware foreign-process guard, 0/T touched last |

**Also frozen, in the same commit, and part of the registered case:** the three
case trees `verification/runs/T-family/T16_runs/T16_MC_{c,m,f}/` — `0.orig/`,
`constant/`, `system/`, `CASE.txt`, `log.blockMesh`, `log.checkMesh.build`, and
`BUILD.txt`.

**Selftest evidence at the freeze, all four instruments, under `python3` AND
`python3 -O` identically:** `exact_t16.py --selftest` **PASS (0 failed)**;
`build_t16.py --selftest` **PASS (0 failed)**; `mark_done_t16.py --selftest`
**PASS (0 failed)**, driving both field-class halves and all three R-RC arms;
`analyse_t16.py --selftest` **PASS (0 failed)**, driving 27 arms including the
eight rule-5 ladder cases at the STAGNANT_FLOOR, the EXACT-class pair, the value
control, the ladder claim, five gate-(1) arms, three refusal arms, the blind
reader and the live-tree refusal on both interpreters. **`ast.Assert` node count
is 0 in every one of the four files** (L-332), each counted by a counter shown to
see a planted `assert`.

## 12. Condition at freeze (`CLAUDE.md` rule 2)

Checked immediately before this commit:
`verification/runs/T-family/T16_runs/{T16_MC_c,T16_MC_m,T16_MC_f}` each hold
`0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`, `log.blockMesh`,
`log.checkMesh.build` — **no `0/`, no numeric time directory, no `log.solve`, no
`STATUS.*`, no `DONE.*`, no `gate_t16.json`. ZERO core-minutes have been spent in
the registered tree.** The launcher's own guard refuses a case where `0/` or any
numeric time directory already exists, so this condition is also enforced, not
merely asserted.

**Disclosed pre-compute:** four scratch probes (§8), all built by
`build_t16.py --probe` into `/tmp`, all outside the repository, none of them a
registered case. Their total spend is approximately **95 core-minutes** and it is
**not** part of this rung's registered cost; it is the cost of choosing the
outlet condition and the linear solvers before freezing them.

## 13. What this rung does NOT earn

It earns nothing turbulent, nothing 3-D, nothing conjugate, nothing radiative,
nothing at or past `G = 72`, and nothing for the entrance region. It is graded
against a **derived closed form**, not against an experiment, so it earns
**verification**, not validation: no experimental datum is claimed, and the `P`
(published-reference) column of this rung is empty by construction and is not
BLOCKED — there is nothing to acquire.

---

## AMENDMENT A1 — 2026-08-27, **POST-COMPUTE. FREEZE-SET UPDATE FOR THE D541 REPAIR OF `mark_done_t16.py`.** Document **v1.0 → v1.1**.

**`lines whose number changed above this section: 0`.** This amendment is
appended at the foot. Nothing in §0–§13 has been edited, struck, reworded or
renumbered; the byte prefix of this document up to the line above was asserted
identical to the pre-amendment file before this text was written.

**DISCLOSED IN THESE TERMS, WITHOUT SOFTENING: THE COMPLETION MARKER WAS
REPAIRED AFTER FIRST COMPUTE.** `T16_MC_c` had already run to `endTime` 10 000
(744 wall s, ended 2026-08-27T17:42:30Z) when the defect below was found and
repaired. That is a departure from rule 2's ordinary discipline and it is stated
plainly rather than buried. **No gate, no band, no threshold, no cap, no timeout,
no reference value and no verdict label is altered by this amendment, and none
could be:** the repaired file is the completion marker, not the comparator — it
reads no physics value, computes nothing, and writes no word from the rule-1
vocabulary. §5's bands, §6's gate, §8's costs and caps and §10's predictions are
untouched, byte for byte. **Sanaa may overrule this amendment and the repair it
records.**

### A1.1 The §11 freeze-set row, QUOTED AND STRUCK — never rewritten (rule 6)

The row as frozen at `ae20d137`, struck in place and preserved:

> ~~`| `verification/runs/T-family/T16_runs/mark_done_t16.py` | `2ae1605c7983e379d586467a8ffb4890d0d1b20d` | the strict completion rule with the two L-342 field classes declared in prose and ruling R-RC applied |`~~

**The registered blob for that path from this amendment forward:**

| file | git blob | what it fixes |
|---|---|---|
| `verification/runs/T-family/T16_runs/mark_done_t16.py` | **`efcf78524dc4f853202cf24dd08c733d7742ac67`** | the strict completion rule with the two L-342 field classes and ruling R-RC **as before, unchanged**, plus the D541 repair of the FPE crash-token limb |
| `verification/runs/T-family/T16_runs/mark_done_t16.PRE_D541.py` | `2ae1605c7983e379d586467a8ffb4890d0d1b20d` | **the frozen original, preserved and never edited and never deleted (rule 6)** — byte-identical to the blob struck above, so the struck row remains reproducible with `git hash-object` |

Applied at commit **`5bcbaf8ca19e3a9c769e2dd11c5e435fdd755b09`** on this family's
A3/A9 promotion pattern (the pattern used for T5's builder). The promoted content
is byte-identical to the PROPOSED blob `efcf78524dc4f853202cf24dd08c733d7742ac67`
committed at **`cdaf1d46`** — the exact bytes the supervisor read as a diff and
ruled on. **The applying lane added not one byte to the approved content.** The
proposal and its unified diff remain on disk beside the file as
`mark_done_t16.D541_PROPOSED.py` and `.diff`.

The other six §11 rows are **untouched and byte-identical to the freeze**;
`analyse_t16.py` was re-hashed against `9054d452b43ddda60c2bb187edc762d698a595ec`
in the same invocation that ran it (§A1.4).

### A1.2 THE SUPERVISOR'S RULING AND ITS REASONING, RECORDED VERBATIM

The supervisor read the diff personally, discharged his check 1, and ruled the
repair APPROVED and to be APPLIED. His reasoning goes into the record verbatim
because it answers the one real objection:

> The proposal at `cdaf1d46` (`verification/runs/T-family/T16_runs/mark_done_t16.D541_PROPOSED.py` + `.diff`) was measured by the supervisor directly against real artifacts. On the REAL serial FPE crashes `verification/runs/FPE_DIAG_runs/BP1/log.simpleFoam` and `HP1/log.simpleFoam`, EVERY frozen crash token reads 0 — `FOAM FATAL ERROR` 0, `FOAM FATAL IO ERROR` 0, `Segmentation fault` 0, `Aborted` 0, `signal ` 0 — except `Floating point exception`, which reads 1, and THAT ONE OCCURRENCE IS THE BANNER LINE `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)`. `Foam::sigFpe::sigHandler` reads 1 in both. On the clean `T16_MC_c/log.solve` all three new patterns read 0 and the frozen token reads 1.
>
> So: the frozen matcher refused real crashes ONLY through its own false positive; its true-positive rate on the serial FPE class by any legitimate token was ZERO. It refused every input, clean or crashed, for the same reason, and could not distinguish them at all. THE OBJECTION THAT THIS "LOOSENS A GATE" THEREFORE FAILS ON ITS OWN TERMS: you cannot loosen a gate that never discriminated — a refusal that fires identically on every input is not a gate, it is a constant. The repair is the first version of this instrument with any discriminating power on the FPE class, and it STRENGTHENS detection rather than weakening it. Legality runs through VERIFICATION_CHARTER §2d's boundary clause 1, the D419 case — an instrument that cannot run at all — and NOT through §2d.1, which is cut for a change that moves a number. This one moves no number: the marker reads no physics value, computes nothing and writes no verdict word.

### A1.3 The control on the real artifact, measured by the applying lane

On the registered clean log `verification/runs/T-family/T16_runs/T16_MC_c/log.solve`
(7 029 076 B, `End` line present, `rc = 0`):

| matcher | file | crash tokens returned on that log |
|---|---|---|
| frozen | `mark_done_t16.PRE_D541.py` | **`['Floating point exception']`** — the `trapFpe` banner, line 20 |
| repaired | `mark_done_t16.py` | **`[]` — none** |

That single false positive is the whole of what blocked this rung. It is the
mirror of rule 3: **a refusal from a guard never shown able to accept a
known-good input is worth exactly as little as a zero from a reader never shown
able to see a non-zero.** The repaired file drives that positive control, and two
negative controls built from verbatim excerpts of real FPE crashes on this box,
in its own `--selftest`.

**`--selftest` state of the registered blob, disclosed exactly and not rounded
up: 24 ok / 1 FAIL, identically under `python3` and `python3 -O`.** The single
FAIL is the D541 **frozen-contrast** arm, which loads `HERE/mark_done_t16.py`
expecting to find the defect still present in it; after promotion that path *is*
the repaired file, so the arm compares the repair against itself and reports the
defect gone. **It is a defect-presence detector reporting success, not the
failure of any completion clause.** Every substantive arm reads ok: all six
strict-rule limbs, both L-342 field-class halves, all three R-RC arms, the D541
provenance check on all three embedded excerpts, and the three FPE
positive/negative controls. AST `assert` count in the file is 0 (L-332), by a
counter shown to see a planted `assert`. Retargeting that one arm at
`mark_done_t16.PRE_D541.py` would change the approved blob, so **the applying
lane did not make that edit** — approval of a blob is not approval of a blob
edited afterwards (rule 9). It is referred to the supervisor as a second ruling
and is **not** claimed here as a passing selftest.

### A1.4 What `scripts/check_comparator_freeze.py` actually reports

Run after this repair: **`analyse_t16.py` reads `FROZEN`**, scope 1 of 1 marker
(`DONE.T16_MC_c`), comparator committed 2026-08-27T17:12:13Z, first marker
2026-08-27T19:18:24Z, **margin (last) +7 571 s** — frozen by construction, and
the T16 marking widened that margin rather than narrowing it. The tool's global
verdict is `FAIL` for **pre-existing, lab-wide, non-T16 reasons** (9 UNFROZEN and
2 AMENDED_AFTER graders out of a population of 140; none of them is a T16
instrument), and that FAIL predates this amendment.

**A correction to the record, stated because it matters for how this file is
maintained:** `check_comparator_freeze.py` does **not** police
`mark_done_t16.py`. Its population is 139 *graders* — `analyse_*` / `grade_*` —
and `mark_done` appears zero times in its output. The freeze-set mismatch this
amendment repairs is therefore a **prose-record** mismatch in §11, reproducible
only by `git hash-object` against the table, and **no automated check would have
caught it.** That is an argument for the amendment being owed, not against it.

### A1.5 What this amendment does NOT do

It does not grade anything. `T16_MC_c` is marked `DONE`; `T16_MC_m` was still
running and `T16_MC_f` still queued when this was written, so the Roache triple
is incomplete and the frozen comparator **refused the partial rung (exit 2)** —
correctly, and that refusal is recorded as correct. **Rule 5's ordering is
untouched by any of this.** The rung's verdict remains **`PENDING`**. No solver
was launched by the lane that applied this repair.

**Nothing in this rung has been sent, filed, submitted, uploaded, registered or
posted anywhere outside this box, and nothing in it may be (`CLAUDE.md` rule 7).**
