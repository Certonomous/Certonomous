# F25 — PRE-REGISTRATION: fully developed laminar flow in a SQUARE DUCT, a GENUINE 3-D ladder (simpleFoam/SIMPLEC, streamwise cyclic, fixed body force, 4 ranks, r = 2 in all three directions)

**Team:** cfd. **Case id:** `F25_DUCT3D`. **Written before any compute in the case
tree or any run root. ZERO CORE-MINUTES SPENT there** (7.0 core-min of scratch
INSTRUMENT ARMS, none a ladder level, are disclosed in §5.1 and §7). **Status at
freeze: ARMED — never run.** Frozen by the commit that carries this file. After
first compute the gates, thresholds, cap and labels below are **closed**; changes
land only as dated addenda that cannot alter them. Decided and recorded
**`[lab-attributed]`** on the cfd supervisor's dispatch of 2026-08-26 for the
capability grid's named gap (`docs/capability/cfd_GRID.md`, 3D · steady ·
incompressible: *"never produced a CONVERGING 3D triple"*). Template in structure and rigour: F23 (`cases/F23_HP_WEDGE/`, `F23_HP_WEDGE_PREREGISTRATION.md`).

**Capability-grid cell (068c2bf0): 3D · steady · incompressible.**

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled so at registration; not a result; counts toward no challenge column; not
filmed. Its purpose: the lab's first three-level ladder refined by exactly 2 in
**all three** directions, against an exact target, graded from processor
directories on 4 ranks — the record the grid's 3D · steady · incompressible cell
has never held.

---

## 1. THE CASE, AND WHY THIS FORM OF IT

Fully developed laminar flow in a square duct of side 2A = 1 (hydraulic diameter
D_h = 1), ν = 0.01, driven by a **FIXED streamwise body force G = −dp/dx = 0.2845
per unit mass** applied to every cell. By the exact series (§2) the bulk velocity is
Ubar = 0.999854018868530, so **Re_Dh = Ubar D_h/ν = 99.985 (≈ 100)**, u_max =
2.09595000085907, and the Darcy friction-factor product is **f·Re =
2 D_h² G/(ν Ubar) = 56.908307539125** (the literature's 56.908 for aspect ratio 1).

**Fully developed by construction — streamwise `cyclic` with a FIXED body force**,
for the reasons F23 §1 gives: the series is an exact solution of the case as posed
(a developing duct has no closed form), the discrete problem is **linear**, and
**both gate quantities are readings of the velocity field**: G is imposed, Ubar_h
is READ from the field, f·Re_h = 2 D_h² G/(ν Ubar_h).

| item | value |
|---|---|
| geometry | x ∈ [0, L], **L = 8 D_h = 8.0** (cyclic; the length buys cells for the hours order, not accuracy — the physics is 2-D in the cross-section); y, z ∈ [0, 1] with the wall on all four sides; ONE hex block, no symmetry plane — the full cross-section is solved |
| patches | `inlet`/`outlet` **cyclic** pair; `wall` (noSlip; p zeroGradient) on the four sides |
| solver | `simpleFoam`, laminar, `steadyState`; **SIMPLEC** (`consistent yes`, **U 0.95 / p 1.0** — chosen from measurement, §5.1); `Gauss linear` gradients; Laplacian `Gauss linear corrected` (cubic cells: checkMesh **non-orthogonality max 0**, §1 below); **`div(phi,U) Gauss linearUpwind grad(U)`** — identically null on the solution and chosen for its diagonally dominant implicit part (§5.1); U and p by GAMG (U relTol 1e−3 / tol 1e−12); **no `residualControl`**, fixed **4000 iterations**, checkpoints every 100 |
| source | `constant/fvOptions`: `vectorSemiImplicitSource`, `selectionMode all`, `volumeMode specific`, `U ((0.2845 0 0) 0)` |
| initial field | U = (0 0 0) everywhere (from rest; nothing of the answer is seeded); 0/U written **last** by the builder |
| ranks | **4 at every level**, `decomposePar` `simple n (1 2 2)` (2 × 2 cross-section quadrants; **x is never cut**, so the cyclic pair stays whole on every rank), **never reconstructed**: the grader reads `processor*/` |

**Mesh admissibility (`docs/standards/MESH_STANDARD.md` §3).** The coarse level
(16 × 16 × 128) was **BUILT AND `checkMesh`'d** on a scratch copy by `build_f25.py`
in the writing invocation: 32,768 cells, `Mesh OK`, **max non-orthogonality 0° (§3.1
hard gate 70°)**, **max skewness 0 (§3.2 hard gate 4)**, **max aspect ratio 1 (§3.3
advisory at 1000, never a lone rejection)**. The builder enforces both hard gates at
every level and records the aspect ratio in `MESH_LINE.txt`; it also checks the
built mesh's own `0/C` and `0/V` against the model geometry (centres at
(i + ½)h, volumes h³) to 1e−9 and refuses otherwise. (OpenFOAM writes a cubic
mesh's `0/V` as `uniform h³`; the reader expands it and a control plants one.)

## 2. THE REFERENCE — A SERIES, ESTABLISHED BY SUBSTITUTION; SOURCE STATED HONESTLY

`exact_f25.py` evaluates, in duct coordinates y' = y − A, z' = z − A:

    u(y', z') = (G/2ν)(A² − y'²) − (16 A² G/π³ν) Σ_{i odd} (−1)^((i−1)/2) cosh(iπz'/2A)/cosh(iπ/2) · cos(iπy'/2A) / i³
    Ubar     = (A² G/3ν) [1 − (192/π⁵) Σ_{i odd} tanh(iπ/2)/i⁵],   f·Re = 24 / [1 − (192/π⁵) Σ_{i odd} tanh(iπ/2)/i⁵]

**Rule 15, stated plainly:** this is the classical eigenfunction solution of the
rectangular-duct Poisson problem (Shah & London 1978, *Laminar Flow Forced
Convection in Ducts*, rectangular-duct section; White, *Viscous Fluid Flow*, the
rectangular-duct solution in chapter 3). **No copy of either is on disk under
`docs/papers/`** — searched for shah / london / duct: only Pinelli et al. 2010 and
Vinuesa et al. 2014, both turbulent DNS — so **no equation number is cited from a
document on this box, and none is claimed.** The reference actually USED is the
derivation itself, established at selftest (rc 0 in the writing invocation, 2.2 s):

- **symbolic substitution (sympy):** the parabola's Poisson residual ν(u_yy + u_zz) +
  G is identically **0**; every series term cosh(kz') cos(ky') is harmonic for
  symbolic k (residual **0**); on z' = ±A the series coefficients equal the
  parabola's own Fourier cosine coefficients — checked symbolically for i = 1, 3, 5
  — so u = 0 on those walls; on y' = ±A both parts vanish (cos(iπ/2) = 0);
- **planted control:** a 1.1× curvature plant inside the parabola gives a
  **non-zero** residual (rule 3);
- **convergence control:** at every FINE-level cell centre the series with N = 400
  and 2N terms differ by **2.6e−16** (tolerance 1e−13); the y ↔ z asymmetry is
  **4.9e−15**; a 3-term series is SEEN to differ (1.5e−2); Ubar's tanh series is
  summed as (1 − 2⁻⁵) ζ(5) minus an exponentially convergent tail (the raw 1/i⁵ sum
  converges only as 1/N⁴ — measured 4e−13 short at N = 400, and refused), N vs 2N
  agree to 1e−15, and agrees with a 160 × 160 Gauss–Legendre quadrature of the field
  series to **8.8e−13** (tolerance 1e−10, stated: the corner behaviour makes the
  quadrature algebraic);
- **literature cross-check:** the series gives **f·Re = 56.908307539** against the
  tabulated **56.908** (Darcy form, square duct; from memory of the texts above,
  NOT from a document on this box) — reproduced to 4 decimals; the series is the
  reference, the tabulated number is not.

`python3 -O exact_f25.py --selftest` → **rc 2**.

## 3. THE LADDER — THREE LEVELS, `dim = 3`, r = 2 EXACTLY IN x, y AND z

Cubic cells h = 1/NR at every level; **all three directions refine by exactly 2**
(cells × 8; a control refuses otherwise). r = 2.000 from cell counts at dim = 3.

| level | NX × NR × NR | cells | h | ranks | E2n predicted (§4) | f·Re predicted (§4) |
|---|---|---|---|---|---|---|
| coarse | 128 × 16 × 16 | 32,768 | 1/16 | 4 | 1.148302732e−02 | 56.069277670 (err −8.390e−01) |
| medium | 256 × 32 × 32 | 262,144 | 1/32 | 4 | 2.947002844e−03 | 56.694995063 (err −2.133e−01) |
| fine | 512 × 64 × 64 | **2,097,152** | 1/64 | 4 | **7.421509467e−04** | **56.854737070 (err −5.357e−02)** |

Model orders across the ladder: E2n **1.962 / 1.989**, f·Re **1.976 / 1.993**.
**Registered prediction: both triples CONVERGING with observed order p ≈ 2, fine
values inside both bands → PASS × 2.**

**L-345 control — the model's OWN triples through THE grader's classifier, at
registration.** `scripts/roache_triple.py::triple_from_cells` (dim = 3, cells
32,768 / 262,144 / 2,097,152) reads the model's E2n triple **CONVERGING, order
1.953** and its f·Re triple **CONVERGING, order 1.970**; the registration REFUSES
on any other state. The classifier is shown able to say no: F19's equal-increment
x_s triple planted through the same call reads **DEGENERATE, order −0.027**.

**DECOMPOSITION SEED (required field): `none`** — `simple` geometric
decomposition from `system/decomposeParDict`, deterministic, no RNG; 4 subdomains
at every level.

## 4. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to predictions computed
from the scheme on the mesh's own geometry. Declared now; not fitted; not revisable.

**The derivation.** On the fully developed cyclic duct with cubic cells every
x-face pair cancels identically (u is x-uniform; the cyclic pair closes the
column, whatever the face interpolation), convection is null (v = w = 0, ∂/∂x = 0)
and grad p = 0, so simpleFoam's steady discrete x-momentum equation per cell
reduces **exactly** to the 5-point cross-section stencil of the `Gauss linear
corrected` Laplacian on an orthogonal mesh:

    ν h Σ_{interior faces} (u_N − u_P)  −  2 ν h u_P (per wall face)  +  G h³ = 0

with the `noSlip` wall a fixedValue face at distance h/2. `exact_f25.discrete()`
assembles and solves that sparse system on the blockMesh geometry (residual
≤ 5.1e−15 at every level; the exact profile substituted into it leaves a **non-zero**
truncation residual 3.6e−02 / 8.9e−03 / 2.2e−03 — the evaluator sees). The
prediction is therefore a function of the SCHEME and the GRID and nothing else.

**Instrument checks, scratch, disclosed (§5.1 and §7; NOT levels of the ladder;
not retained; not results):** on the registered dictionaries the real chain
`build_f25.py` → `decomposePar` → `mpirun -np 4 simpleFoam -parallel` at
8 × 8 × 32 (2,048 cells, 4000 iterations) returned **E2n = 4.190978682056e−02 and
f·Re = 53.749131609385 against the model's 4.190978682142e−02 and
53.749131609417** (differences **8.7e−13** and **3.2e−11**); at 32 × 32 × 16 the
same to 5.7e−12 / 2.8e−09 (800 iterations), and the station profile matches the
model cell by cell to **5.6e−12**. **The model IS the discretisation to round-off;**
the factor-3 window guards what the model omits (the iterative tolerance at 2.1 M
cells over 4 ranks, floating-point ordering across ranks, the plateau), not the
stencil.

**G-F25-1 — E2 of the NORMALISED axial profile at the mid-length station**
E2n = √( Σ_j V_j (u_j/Ubar_h − u_exact(y_j, z_j)/Ubar)² / Σ_j V_j ), over the one
x-slab of cells nearest x = L/2 + dx/2 (its count must equal NR²; refused
otherwise), (y_j, z_j) the mesh's own cell centres, V_j its own cell volume, Ubar_h
the station's volume-weighted bulk velocity. Normalised by the READ bulk velocity so
the gate is the profile SHAPE (the amplitude is G-F25-2's).
Prediction at fine: **7.421509467e−04**.
**Band = [prediction/3, prediction×3] = [2.473836489e−04, 2.226452840e−03].**

**G-F25-2 — f·Re from the imposed G and the READ bulk velocity**
f·Re_h = 2 D_h² G/(ν Ubar_h). Exact (series) **56.908307539125**. Predicted fine
error **−5.357047e−02**.
**Band = 56.908307539 ± 3 × 5.357047e−02 = [56.747596130, 57.069018948].**

## 5. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
  PENDING, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node
  (`grade_f25.py:894` at freeze), AST-censused; the text matcher driven both ways.
- **Class C plateau** (all four elements) on the graded quantity itself at every
  checkpoint (100 iterations apart, 40 samples; min 20; window 12 = 1200 iterations;
  trend 2e−4, stationarity 1e−4, variance ratio [0.2, 5]); element 4 exits.
- **Rule 5 limb (1) — census, with the excluded channels declared (N-AV8).** The
  solver's **`Ux` initial residual ≤ 1e−8 at every iteration of the census window
  2801–4000** (the driven component), plus a **field-level** check that the
  transverse components are zero: max|Uy|, max|Uz| ≤ 1e−10 × U_MAX at endTime. The
  normalised initial residuals of **Uy, Uz and p are PRINTED beside the verdict and
  EXCLUDED from the gate**: each is a vanishing channel (v = w = 0 exactly; p is
  uniform on the cyclic domain) whose relative residual is normalised by a vanishing
  scale — measured on the instrument run: Uy residual 7.3e−1 with max|Uy| = 3.0e−14
  in the field. Excluded at the freeze, printed anyway.
- **Completion (rule 4):** `RC.txt` = 0; `End`; latest + 1 > endTime; **`Time` lines
  == 4000**; `U` and `p` at `4000/` in **every one of the 4 processor directories**,
  each **newer than the serial `0/U`** (written last at build, before decomposePar).
- **L-342 field classes.** `PHYSICS_CRITICAL`: log `End`/`Time` count, `RC.txt`,
  processor endTime fields + age guard, `processor*/0/C` and `0/V`, checkpoint U
  files, `Ux` residuals and the transverse field maxima. `INFRASTRUCTURE`:
  `ClockTime`, box probes, `MESH_LINE.txt`, utility logs, runner
  `STATUS`/`launcher.queue.out`/`LAUNCH_LOG` rows, calibration figures. Verdicts key
  on the first only; a missing INFRASTRUCTURE field prints `BOOKKEEPING DEFECT` and
  refuses the **cost claim only**. Driven both ways at selftest.
- **Planted-zero controls (rule 3)** into copies of the real processor `U` files,
  read back with the real parser: δ = 1.234e−3 on Ux must move E2n to the value
  predicted in memory (1e−13) and f·Re to 2 D_h² G/(ν (Ubar_h + δ)) (1e−10); a plant
  that does not move a reading refuses. Exercised on the instrument run's real
  processor files: E2n moved by 5.714367e−04 and f·Re by −6.258062e−02, both read
  back exactly as predicted.
- **`assert` census: ZERO** across `grade_f25.py`, `exact_f25.py`, `foam_io_f25.py`,
  `build_f25.py`; planted assert seen. **Hard `-O` refusal at entry** — measured:
  `exact_f25.py --selftest` rc 0 (2.2 s, 106 MB RSS) / `-O` rc 2; `grade_f25.py
  --selftest` rc 0 (2.8 s, 108 MB RSS, 12 controls) / `-O` rc 2.
- **Reader fast path.** The fine level's 2.1 M-cell checkpoints are parsed by a
  numpy fast path; at selftest it must equal the entry-by-entry regex path bit for
  bit on the real solver-written file the format is pinned to
  (`verification/runs/ansys_verification/VMFL019/L1_30/5/U`) and on a synthetic
  file; a list whose declared count disagrees with its body is refused.
- **Success messages print INSIDE the passing branch.**
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/`, numeric time or
  `processor*` directory in the run root and in each level directory; neither
  deletes; the builder refuses a destination inside the tracked case tree and
  refuses to build a registered level under `--scratch`.
- **`set -u` dropped around the OpenFOAM bashrc source only** (L-339;
  `run_f25.sh:170–173`); `scripts/check_launcher_can_launch.py --worktree
  cases/F25_DUCT3D/run_f25.sh` → **rc 0** (0 time-directory globs, 0 bashrc sources
  under `set -u`).
- **`--preflight` fires nothing** (no blockMesh, no build, no decomposePar);
  measured: rc 0, instrument green, cap agrees 1400/1400, ν/G/ranks/endTime agree,
  run root reported ABSENT; no-argument invocation rc 1.
- **Dictionaries cross-checked** at every grader entry and by the launcher (ν, G,
  `volumeMode specific`/`selectionMode all`, `numberOfSubdomains 4` and `n (1 2 2)`,
  `endTime 4000`, `writeInterval 100`, no `residualControl`, **`consistent yes`,
  U 0.95 / p 1.0, `div(phi,U) Gauss linearUpwind grad(U)`, Laplacian `Gauss linear
  corrected`**, cyclic/wall declarations, the NX × NR × NR block, `noSlip`).

### 5.1 THE ITERATIVE FLOOR IS DERIVED FROM THE PREDICTED FINE-LEVEL ERROR, NOT INHERITED (L-346) — and the F23 form was found unable to converge here BEFORE registration

**The rule (L-346, from F17b's NOT A RESULT × 2 at `f2943b0b`).** The census
tolerance over the Class C window must put the integrated iterative movement at
least a decade below the model's predicted fine-level error, for BOTH gates:
window × UX_RES_TOL = 1200 × 1e−8 = **1.2e−05 ≤ 0.1 × min(E2n_fine 7.42e−04,
|f·Re err|/f·Re 9.41e−04) = 7.42e−05** — ratio **0.16**. This is a refusing control
in `grade_f25.py` (`control_iterative_floor_derived_from_fine_error`), driven both
ways: a 100× looser floor refuses, and so does a fine level 100× more accurate than
predicted under this floor.

**The F23 form does not converge on this case — measured, not assumed.** The first
design copied F23's solver settings (SIMPLE, U 0.7 / p 0.3, `div(phi,U) Gauss
linear`). On the 8 × 8 × 32 scratch duct the solver reproduced the model to 9e−14,
but `Ux` reached 1e−8 only at **iteration 1,275** and the graded quantity's
transient decayed at **0.990 per iteration** — the mean-flow (bulk-acceleration)
mode. Mechanism, read from the run and the code: `fvMatrix::relax()` enforces
diagonal dominance against the central-convection off-diagonals |φ| = u h², which
adds a pseudo-time term of step ≈ h/u_max (a CFL-1 march; measured 0.052 against
h/u = 0.06), and the mean mode of the cross-section diffusion operator
(λ₁ = 2νπ²/side² = 0.197) then needs ≈ 18.4/(λ₁ Δτ) iterations — ∝ 1/h, ≈ 12,000
at 64 cells per side. **The fine level could not have converged inside 4,000
iterations, and the ladder would have read NOT A RESULT × 2 by rule 5 limb 1 —
the F17b failure mode, found before compute instead of after.** The relaxation
factor barely matters (α_U 0.9 / 0.99 / 1.0 all ≈ 0.985 per iteration: the
dominance term, not α, sets the step); removing relaxation altogether diverges
(the central matrix is not diagonally dominant; GAMG and PBiCGStab both blow up);
SIMPLE with a dominant (upwind) matrix at α_U ≥ 0.95 diverges (p–U coupling).

**The registered form, and its measured floor.** `div(phi,U) Gauss linearUpwind
grad(U)` (implicit part upwind-dominant → `relax()` adds no pseudo-time term;
identically null on the solution, §4: the model contains no convection and the
solver reproduced it to 1e−12 under central AND linearUpwind) with **SIMPLEC**
(`consistent yes`, **U 0.95 / p 1.0**). Iterations to `Ux` ≤ 1e−8 from rest,
measured on scratch cross-sections at the registered form (x-extent shortened —
the mode is x-uniform and nx does not enter):

| arm (scratch, 4 ranks) | cells | h | iterations to Ux ≤ 1e−8 | to 1e−12 | contraction per iteration | ClockTime |
|---|---|---|---|---|---|---|
| 8 × 8 × 32, 4000 its (full grader path) | 2,048 | 1/8 | **82** | 317 | 0.915 | 17 s |
| 16 × 16 × 16, 600 its | 4,096 | 1/16 | **171** | 327 | 0.918 | 2 s |
| 32 × 32 × 16, 800 its | 16,384 | 1/32 | **430** | 718 | 0.968 | 10 s |
| 64 × 64 × 16, 1000 its (**the fine cross-section**) | 65,536 | 1/64 | **≈ 1,230** (1.16e−07 at 1000; 0.9894/it) | ≈ 2,100 (extrapolated) | 0.9894 | 40 s |

At the fine cross-section the residual at iteration 2801 (the window's first
iteration) extrapolates to ≈ 5e−16 — **2.3× the iterations the floor needs**, and
a decade below it in residual. The 8 × 8 × 32 arm run through the grader's own
path read `CONVERGED` (0 of 1,200 above tolerance; worst Ux 1.1e−12), Class C
**PLATEAUED** on both quantities (drift 8e−17 / 4e−17), max|Uy| = max|Uz| =
3.0e−14 (floor 2.1e−10). **Registered prediction on the floor: `Ux` ≤ 1e−8 at every
level from iteration ≈ 1,300 at the latest; the window 2801–4000 is clean at all
three levels.** If the 2.1 M-cell level does not hold 1e−8 inside the window the
level is **NOT A RESULT** by rule 5 limb 1 and stays so — the instrument, not a
defect of the case.

**Cost of finding this: 7.0 core-min of instrument arms** (105 ClockTime-s × 4
ranks over 24 scratch runs, itemised in §7), against the dispatch's ≤ 1 core-min
smoke-arm figure — disclosed as a departure, spent so that a 700-core-min ladder is
not registered on a floor it cannot reach.

## 6. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real readers on files in the pinned write format (`U`, `C`, `V`; pinned
against real solver output on this box,
`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, parsed at selftest by
both reader paths), on a 4-slab synthetic level at the fine cross-section carrying
the model's SOLVED fine station profile:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F25-1 | exact + 1× model error field | 7.421509467e−04 | [2.474e−04, 2.226e−03] | **inside** |
| G-F25-1 | exact + 40× the same | 1.991010626e−02 | same | **outside** |
| G-F25-2 | exact + 1× the same | 56.854737070 | [56.747596130, 57.069018948] | **inside** |
| G-F25-2 | the same with u × 1.01 | 56.291818881 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned, the
*values* are the model's.

## 7. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** Ranks = 4 at every level.

**Rate basis — DERIVED, NOT MEASURED on these levels, as the dispatch specified:**
F23's registered rate curve (`F23_HP_WEDGE_PREREGISTRATION.md` §7: F17's MEASURED
**0.59 µs per cell-iteration** at 24,576 cells,
`verification/runs/F17_runs/fine/log.simpleFoam`, grown **+30 % per doubling** of
the cell count = **1.11 / 1.88 / 3.18 µs at 131k / 524k / 2.1 M cells**), times a
**3-D face factor of 1.5** (a hex cell carries 6 faces against a 2-D slab's 4
working faces; the Laplacian, flux and GAMG work scale with faces) — so
**0.99 / 2.17 / 4.76 µs per cell-iteration** at the three levels. Without the face
factor the same curve gives 470.7 core-min; with it, the registered estimate below.

| level | cells | doublings over 24,576 | rate (µs) | core-s | core-min | wall on 4 ranks |
|---|---|---|---|---|---|---|
| coarse | 32,768 | 0.415 | 0.987 | 129 | 2.2 | 0.5 min |
| medium | 262,144 | 3.415 | 2.168 | 2,273 | 37.9 | 9.5 min |
| fine | 2,097,152 | 6.415 | 4.763 | 39,956 | **665.9** | **2.77 h** |
| **total** | | | | **42,359** | **706.0** | **≈ 2.9 h** |

**Disclosed against it — measured on THIS case, small meshes, loaded box (load
15–17 of 16):** 3.05 µs at 16,384 cells and **2.44 µs at 65,536 cells** (the 64 × 64 ×
16 arm, 4 ranks, ExecutionTime/ClockTime 0.99). Anchoring the same +30 %/doubling
curve on 2.44 µs at 65k cells projects 1.88 / 4.12 / 9.06 µs and **1,343 core-min**
for the ladder (4.1 / 72 / 1,267). The registered estimate is the dispatch's basis;
the measured anchor is the reason the cap sits at the 2× ceiling.

**REGISTERED CAP: 1,400 core-minutes** (1.98× the estimate; the admission is the
3-D per-cell cost at 2.1 M cells over 4 ranks on a shared box — the measured-anchor
projection lands at 96 % of it). **Derived dollars at $0.0513/core-h: $0.60
estimate, $1.20 at the cap — DERIVED, NOT MEASURED, reported-by-owner rate**
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation. **`cost_basis:
derived, reported-by-owner, not measured.`**

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe (`PROJ_CORE_S` = 129 / 2274 / 39948 core-s, scaled
up when fewer than 4 cores are free); a crossing **HALTS at exit 3**; unlaunched
levels stay `PENDING`; launcher and grader refuse to start if their caps disagree.

**Memory floor: 6.0 GB** (simpleFoam + GAMG at 2.1 M cells over 4 ranks; the
grader's model is a 4,096-row sparse solve, 108 MB RSS at selftest; 23 GB available
in the writing invocation). **Disk:** 40 checkpoints × (U + p + phi) at 2.1 M cells
≈ 9 GB for the fine level, ≈ 10.5 GB for the ladder (269 GB free on `/`).

**Scratch smoke arm, reported (cfd pre-freeze requirement since F16):** ONE real
`simpleFoam` iteration on a scratch copy of the **coarse level** (16 × 16 × 128 =
32,768 cells) built by `build_f25.py` into the scratchpad, decomposed and run on
**4 ranks** on the registered dictionaries: rc 0, `Time = 1`, `End`, **`Solving for
Ux` initial residual 1 → final 2.95e−04 in 5 GAMG iterations; max|Ux| after one
iteration = 3.365e−01 (NON-ZERO: the driven component moves)**, max|Uy| = 3.0e−06,
max|Uz| = 6.1e−06 (transients of the first SIMPLEC step), ExecutionTime 0.13 s,
ClockTime 0 s; checkMesh gates quoted in §1; not retained, not a measured rate, not
a result.

**Instrument arms, itemised (§5.1; all scratch, all 4 ranks, none retained, none a
level):** two 8 × 8 × 32 runs at 4000 iterations (the F23 form, 9 s; the registered
form, 17 s); four relaxation variants of the F23 form at 1000 iterations (17 s);
three no-relaxation runs that diverged within 18 iterations (1 s); four α_U ≈ 1
runs that diverged within 91 iterations (4 s); five SIMPLEC / upwind variants at
300 iterations (5 s); three h-scaling arms 16³, 32 × 32 × 16, 64 × 64 × 16 (52 s);
two 1-iteration smoke arms (0 s). **ClockTime 105 s × 4 = 7.0 core-min**, spent
before this freeze and outside every run root.

**Convergence risk, registered:** the census window is iterations 2801–4000; §5.1
measured 1e−8 at ≈ 1,230 iterations on the fine cross-section. If the 2.1 M-cell
level has not held 1e−8 inside the window the level is **NOT A RESULT** by rule 5
limb 1 and stays so.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 8. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F25_DUCT3D_runs` → **ABSENT**
at `date -u` = **2026-08-26T22:33:36Z**, and again at the `--preflight` of
22:47Z. No `RC.txt`, `log.*`, numeric time or `processor*` directory exists under
`cases/F25_DUCT3D/` (find → 0); the only numeric directory is the tracked template
`case/0` (holding `p` and `U.template`).

## 9. NEVER RUN — THE EVIDENCE (L-337 controls first)

- `git ls-tree -r HEAD --name-only`: **15,367** tracked paths at the writing
  invocation; **planted control: the known `cases/F20_ISENTROPIC_VORTEX/` paths are
  returned (15)**; matches for `F25|DUCT3D`: **0**.
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (536 entries) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F25*` directory.

## 10. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F25_DUCT3D/run_f25.sh --prereg-commit=<this file's freeze sha>

4 ranks at every level (`mpirun -np 4 simpleFoam -parallel`); grading is a separate
invocation `python3 cases/F25_DUCT3D/grade_f25.py --prereg-commit=<sha>` reading
the processor directories; the launcher prints that command and never grades. The
queue entry `cases/F25_DUCT3D/queue_entry_F25_DUCT3D.json` is **HELD in the case
directory** until the supervisor's check 1/4; the supervisor, not this lane, moves it
into `verification/queue/cfd/`; enqueueing is not authorisation.

## 11. FROZEN FILES (sha256 at this freeze, first 8 / last 4)

    cases/F25_DUCT3D/exact_f25.py    bf0fb6f5…5e8f     cases/F25_DUCT3D/grade_f25.py   9b9ba94e…13cf
    cases/F25_DUCT3D/build_f25.py    67b1d337…8140     cases/F25_DUCT3D/foam_io_f25.py f430373e…706d
    cases/F25_DUCT3D/run_f25.sh      eabee12b…2383
    cases/F25_DUCT3D/case/0/{p,U.template}
    cases/F25_DUCT3D/case/constant/{transportProperties,turbulenceProperties,fvOptions}
    cases/F25_DUCT3D/case/system/{blockMeshDict.template,controlDict,fvSchemes,fvSolution,decomposeParDict}
    verification/campaign/F25_DUCT3D_PREREGISTRATION.md   (this file)

## 12. WHAT IS **NOT** REGISTERED HERE

- No claim about developing flow, entry length or any x-dependence: the case is
  fully developed by construction and every x-slab is the same slab (the grader
  prints the all-cell vs station bulk-velocity difference as a diagnostic, ungated).
- No claim about the convection scheme's order: the term is identically null on
  the solution and the model contains none (§4, §5.1).
- No re-grade of any row; no amendment to any standard, charter, F23 or F17b.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).

---

## AMENDMENT 1 — 2026-08-26T22:56:52Z (pre-compute)

**Version 1.1. Lines whose number changed above this section: 0** (this block is
appended at the foot; the frozen text at `fc4c479b` is untouched — disk blob
`0d6ca000` == `HEAD:` blob at the writing invocation, 424 lines before this block).
Decided and recorded `[lab-attributed]` on the cfd supervisor's ruling of
2026-08-26 on §7: *"an estimate its own registration shows to be 1.9× low is not
an estimate."*

**Condition (rule 2 §2b): before first compute.** Checked in the writing
invocation, `date -u` = 2026-08-26T22:56:52Z:

- `test -e verification/runs/F25_DUCT3D_runs` → **ABSENT**.
- `find cases/F25_DUCT3D -name RC.txt -o -name 'log.*' -o -name 'processor*'` → **0**.
- `verification/queue/cfd/` holds no `F25*` entry and `launched/` holds none; the
  entry was HELD in the case directory (§10) and never dropped.
- Core-minutes spent on this case in the tree or any run root: **0** (the 7.0
  core-min of scratch instrument arms of §5.1/§7 are unchanged and outside it).

**What changes — the COST ESTIMATE and the CAP only.** §7 registered 706.0
core-min on the dispatch's derived basis and disclosed, beside it, a measurement
on this case that projected 1,343. The measurement is now the registered basis:

| level | cells | doublings over 65,536 | rate (µs) | core-s | core-min | wall on 4 ranks |
|---|---|---|---|---|---|---|
| coarse | 32,768 | −1 | 1.877 | 246 | 4.1 | 1.0 min |
| medium | 262,144 | +2 | 4.124 | 4,324 | 72.1 | 18 min |
| fine | 2,097,152 | +5 | 9.060 | 75,997 | **1,266.6** | **5.28 h** |
| **total** | | | | **80,567** | **1,342.8** | **≈ 5.6 h** |

**Basis, stated exactly:** **2.44 µs per cell-iteration MEASURED on this case** —
the 64 × 64 × 16 instrument arm, 65,536 cells, 4 ranks, ClockTime 40 s for 1000
iterations, ExecutionTime/ClockTime 0.99, box load 15–17 of 16 (§5.1 table) —
scaled to each level by **+30 % per doubling of the cell count** (F23 §7's growth
term; MODELLED, not measured on these levels: the coarse level is one halving below
the anchor, the fine level five doublings above it). `cost_basis: measured at 65k
cells on this case; growth per level modelled; derived beyond the anchor,
reported-by-owner dollars.` The §7 figure of 706.0 stands in the frozen text as
what the dispatch's basis gave and is superseded by this row.

| | registered at `fc4c479b` | this amendment |
|---|---|---|
| estimate | 706.0 core-min | **1,342.8 core-min** |
| cap | 1,400 | **2,000** (1.49× the estimate; the cap is the runaway guard, not a target) |
| launcher `PROJ_CORE_S` | 129 / 2274 / 39948 | **246 / 4324 / 75997** |
| launcher / grader `CAP_CORE_MIN` | 1400 | **2000** — the agreement control is kept; `--preflight` re-run after the edit prints `CAP AGREES … 2000` |
| dollars, DERIVED, NOT MEASURED, $0.0513/core-h | $0.60 / $1.20 at cap | **$1.15 estimate / $1.71 at cap** |

**Unchanged:** the ladder (128 × 16 × 16 / 256 × 32 × 32 / 512 × 64 × 64 — the
2.1 M-cell fine level IS the genuine 3-D triple the grid lacks), both gates, both
bands, the exact reference, the iterative floor (§5.1), the census window, the
Class C parameters, ranks, decomposition, every case dictionary, `exact_f25.py`,
`build_f25.py`, `foam_io_f25.py`. Files changed by this amendment: `run_f25.sh`
(two lines: `CAP_CORE_MIN`, `PROJ_CORE_S`) and `grade_f25.py` (one line:
`CAP_CORE_MIN`); sha256 at this re-freeze, first 8 / last 4: `run_f25.sh`
4fb36254…2920, `grade_f25.py` 31d87acb…52b4. Measured after the edit: `grade_f25.py
--selftest` rc 0, `-O` rc 2, `--preflight` rc 0 with `CAP AGREES … 2000`,
`check_launcher_can_launch.py --worktree` rc 0. Still under the $25
pre-authorisation.

**Queue entry:** `cases/F25_DUCT3D/queue_entry_F25_DUCT3D.json` is refreshed in
the FOLLOWING commit so that `prereg_commit` and the launch argv's
`--prereg-commit=` cite the sha of the commit carrying this amendment, with
`cost_core_min_estimate` 1342.8 and `cap_core_min_registered` 2000. Nothing is
sent, filed or submitted (rule 7).

---

## AMENDMENT 2 — 2026-08-27T17:00:07Z (pre-compute) — the L-349 pre-spend projector

**Version 1.2. Lines whose number changed above this section: 0** (this block is
appended at the foot; the 492 lines above it are byte-identical to their state at
Amendment 1, asserted by diffing this file against its HEAD blob over lines 1-492).

**Condition, and how it was checked.** F25 is **pre-compute**:
`test -e /home/ubuntu/Certonomous/verification/runs/F25_DUCT3D_runs` -> **ABSENT at
2026-08-27T17:00:07Z**. Zero core-minutes have been spent in any run root and no `LAUNCHED` line
exists. Rule 2 therefore still permits an amendment, and this one is nevertheless
written as a dated addendum with the original text struck nowhere and rewritten
nowhere (rule 6).

**What is amended: the PRE-SPEND projector only.** The defect is **L-349**
(`68ff1acf`). The launcher projected each level as a FROZEN constant times a
contention multiplier `max(1.0, ranks / max(free, 0.5))`, with `free` probed
inside the launcher at the moment the level starts. The queue runner fires at an
85 % busy ceiling, so `free` pins at the 0.5 floor and the multiplier pins at
**8.0x** for a 4-rank entry. F24's two completed levels refute that magnitude from
its own logs: the measured effect at `free = 0.5` was **1.86x** where the formula
applied **8.0x**, overstated about 4.3x. Worse than the magnitude is the shape — a
registered ladder whose fine level runs or not according to instantaneous box load
is **not reproducible**, and under the standing directive to keep the box busy the
guard converts a full box into a refusing box.

**The replacement**, in `cases/F25_DUCT3D/proj_f25.py` (new file, 341 lines, zero
compute, reads no clock, no `/proc` and no disk — every input is handed in):

- **No level measured yet** (the first level only): the frozen constant times
  `CONT = clamp(ranks / max(free, 0.5), 1.0, CONT_MAX)`, **CONT_MAX = 2.0**.
- **One level measured:** `rate = core_s / cell_iters` from that level — a rate that
  **already carries the load it ran under**, so no contention factor is applied on top
  (that would double-count) — times the next level's cell-iterations, times
  `D = clamp(frozen_rate[next] / frozen_rate[measured], 1.0, 2.5)`.
- **Two or more levels measured:** the same, with `D = clamp(rate[last] / rate[prev],
  1.0, 2.5)` — **this case's own measured drift**, which supersedes the frozen model
  (C-152/C-153: F21 and F22 each measured their own base rate correctly and each still
  missed, by importing another case's growth exponent).

**The two clamps, and the honest status of their magnitudes.** The floor 1.0 means an
*improving* rate is never extrapolated: F24 measured 2.519 then 1.674 core-µs per
cell-iteration as fixed overheads amortised, and that improvement saturates. The
ceiling 2.5 covers every per-doubling rate ratio the lab has measured (2.36 and 2.23
on F22 row C-153; 2.10 and 2.13 on F21 row C-152) and still bounds a runaway.
**CONT_MAX = 2.0 rests on ONE measured point — F24's 1.86x at `free = 0.5` — and that
point is an upper bound on contention alone, because it also carries base-rate
misprediction. One point is not a law, and this addendum does not dress it as one.**
The projector is a runaway guard; the **actual**-spend check is the budget.

**What this amendment does NOT change.** The registered **CAP stays 2000 core-min** —
launcher and grader both, verified equal at preflight, which still prints
`CAP AGREES between launcher and grader: 2000 core-minutes.` The **post-level
incremental check on ACTUAL spend is byte-identical to its HEAD blob** (asserted by
`diff` over the block, this session): `ClockTime × ranks / 60`, summed, HALT at
exit 3 on a crossing, cap never raised (rule 12). The halt on a projected crossing
still exits 3 with unlaunched levels PENDING. **No gate, threshold, band, label,
ladder, iterative floor, census window, Class C parameter, rank count, decomposition
or case dictionary is touched.** `exact_f25.py`, `build_f25.py`, `foam_io_f25.py`
and `grade_f25.py` are unmodified.

**Effect on this case, driven not asserted.** Replaying the registered ladder with
every level running at its Amendment 1 rate, the new projector gives coarse **8.2**,
medium **72.1** (cumulative 76.2), fine **1266.7** (cumulative **1342.9** of 2000) —
**HALT=0 at every level, the ladder proceeds**, and the cumulative projection
reproduces Amendment 1's own registered estimate of 1342.8 core-min to 0.1. The old
form on the same ladder gave fine 10132.9, cumulative **10209.1 of 2000 -> HALT=1**.

**Files changed by this amendment:** `run_f25.sh` (projector call site, the
`MEASURED` accumulator, and the `proj_f25.py` selftest gate; the actual-spend check
untouched) and the new `proj_f25.py`. sha256 at this re-freeze, first 8 / last 4:
`run_f25.sh` `1b42e8ed…e328`, `proj_f25.py` `770f259b…48b9`.

**Measured after the edit:** `proj_f25.py --selftest` rc **0**, **9 controls, 0
failures**, every box reading **INJECTED** (L-339: no control reads live `/proc`);
`python3 -O proj_f25.py` rc **2**; `ast.Assert` count **0**; `grade_f25.py`
`grade_ladder` call nodes **1** (unchanged); `grade_f25.py --selftest` rc 0 and
`-O` rc 2 (unchanged); `run_f25.sh --preflight` rc **0**;
`check_launcher_can_launch.py --worktree` rc **0**. **The halt path was driven both
ways through the launcher's own bytes** — the parse-and-branch block extracted
verbatim from `run_f25.sh` and executed with an **injected** `PROJ_OUT`: `HALT=1`
-> **rc 3** with `HALT BEFORE SPENDING`, `HALT=0` -> **rc 0** falling through to the
launch path. No box was probed in any control.

**Queue entry:** `cases/F25_DUCT3D/queue_entry_F25_DUCT3D.json` is refreshed in the
FOLLOWING commit so `prereg_commit` and the launch argv's `--prereg-commit=` cite
the sha of the commit carrying this amendment, `cost_core_min_estimate` 1342.8,
`cap_core_min_registered` 2000. It is **HELD in the case directory**; moving it into
`verification/queue/cfd/` is the supervisor's act after their own check 1/4.
Nothing is sent, filed, uploaded or submitted (rule 7).
