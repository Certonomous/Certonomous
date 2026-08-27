# VMFLGPU005 -- PRE-REGISTRATION (prediction-first, frozen by sha before any compute)

**Case:** VMFLGPU005 -- Turbulent Natural Convection Inside a Tall Cavity. Ansys Fluid
Dynamics Verification Manual (Release 2026 R1), **manual p.235-238**. **CPU parent: VMFL052**
(manual p.167; the census records 052 = GPU005). Solver: **buoyantBoussinesqSimpleFoam +
petsc4Foam** (OpenFOAM v2606). Lane: `ansys-lane-opus48`. Date drafted: 2026-08-27.

**Object under verification: THE LAB'S GPU SOLVER PATH** (OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA on the L4), not Ansys and not the turbulence model. A verdict
here is a statement about the lab's OpenFOAM-on-GPU linear-solver path against the
manual's reference result; it is NEVER a statement about Ansys (this box has no Fluent).

**DRAFT -- NOT YET FROZEN.** No run directory exists at drafting
(`verification/runs/ansys_verification/VMFLGPU005/` absent). The freeze commit and the
queue drop are the supervisor's, personally, after §3 check 4. This file, the comparator,
the launcher, the field-completeness guard and the mesh generator are the frozen set the
launcher hashes against HEAD.

---

## 1. The manual's reference, and where the NUMBER actually comes from

**The manual page states NO numeric reference.** VMFLGPU005 (p.235-238) gives the geometry
(cavity length 2.18 m, width 0.0762 m, L/W = 28.6), the boundary conditions (cold wall
288.25 K, hot wall 307.85 K, adiabatic top/bottom) and the material properties (Boussinesq
density, cp 1005, mu 1.81e-5, MW 28.966), and presents its Results Comparison as **FIGURES
ONLY**: Figure .gpu005.2 (vertical velocity at Y/h=0.05, p.237) and Figure .gpu005.3
(temperature at Y/h=0.05, p.238), both plotted against the **Betts & Bokhari 2000**
experiment. There is no table of values on the manual page.

**The reference source, title-page verified (rule 15, verified by the supervisor
personally):** P.L. Betts, I.H. Bokhari, "Experiments on turbulent natural convection in an
enclosed tall cavity", *International Journal of Heat and Fluid Flow* **21** (2000) 675-683,
on the box at `docs/papers/buoyant_natural_convection/betts_bokhari_2000_ijhff_21.pdf`.
Reference kind: **EXPERIMENTAL**. The paper pins the driving input the manual omits: cavity
"2.18 m high by 0.076 m wide", temperature differentials 19.6 C and 39.9 C, Ra_W = 0.86e6
and 1.43e6. The manual's case (307.85 - 288.25 = **19.6 K**; 15.1 C = 288.25 K and 34.7 C =
307.85 K are the paper's Table-1 wall temperatures to the digit) is unambiguously the
paper's **Lower-Ra (Ra_W = 0.86e6, dT = 19.6 C)** configuration.

**Two numeric channels, two provenances, kept separate:**
- **C1 -- Betts & Bokhari TABLE 1 "Summary of mid-height results", p.683, LOWER-Ra column**
  (first-hand experimental digits): average Nusselt number **5.85**; max. vertical velocity
  (Av) **0.139 m/s**; centre-line dT/dx **68 C/m**. These are at MID-HEIGHT (y/H = 0.5).
- **C2 -- VMFL052 archive CSV** (Ansys's DIGITISATION of its Figure): the experimental
  Y/h=0.05 profiles Ansys plotted, embedded as plain-text CSV inside
  `VMFL052_WB.wbpz` -> `import_files/VMFL052_natural-exp1.csv` (vertical velocity, 19 rows,
  peak up +0.147826, peak down -0.081739 m/s) and `.../VMFL052_natural-exp2.csv`
  (temperature, 20 rows, core at x=W/2 = 292.246 K). Copied to `reference/` here because
  the archive path is not tracked. The `.wbpz` is a plain ZIP unzippable without HDF5;
  cited as **VMFL052** (the B suffix marks the CFX archive, not a separate case).

**No value is invented.** Every reference digit above is either from the paper (C1) or
from the archive CSV (C2). Bands are set from the manual's agreement class and the model's
documented bias (section 8), never from a first run.

## 2. Reference-KIND -> TIER CEILING (charter §2f.3, supervisor-ruled, hard-coded)

`VERIFICATION_CHARTER §2f.3` classifies a limb by what it CLAIMS:
- A **CONTINUUM** limb -- "value vs experiment, correlation, exact or manufactured
  solution" -- claims a property of the continuum solution: **"GATE REACHED maximum. PASS is
  unavailable."**
- A **SAME-DISCRETE-PROBLEM IDENTITY** limb -- GPU vs CPU -- claims two computations of the
  same discrete problem agree: **"PASS available. A triple is IRRELEVANT to it."**

`§2h.4 cond.1`'s floor-demonstration PASS exception fires ONLY where the reference is "the
EXACT or MANUFACTURED solution of the same continuum model the solver discretises. Not an
experiment...". **Betts & Bokhari is an experiment**, so §2f.3's CONTINUUM cap applies in
full to C1 and §2h cannot rescue it: a Roache triple cures DISCRETISATION error but not the
**MODEL-FORM** error the residual against an experiment still contains (§2h.3).

Therefore, hard-coded in the comparator and executed by `--selftest`:
- **`TIER_CEILING_C1 = "GATE REACHED"`** (CONTINUUM, mid-height vs experiment -- never PASS).
- **`TIER_CEILING_C2 = "GATE REACHED"`** (CONTINUUM + doubly indirect digitisation).
- **`LIMB_B_PASS_CAPABLE = True`** (SAME-DISCRETE-PROBLEM IDENTITY -- **this is where this
  case's PASS credential lives**).
- **Whole-row physics ceiling: GATE REACHED.** Limb B can earn PASS on its own limb.

**§2f.4 corollary (which case WOULD carry a PASS-capable physics limb), stated so the
ceiling does not read as a defeat:** a physics limb on this ladder is PASS-capable only when
its reference is the **EXACT or MANUFACTURED solution of the same continuum model the solver
discretises** (e.g. an analytic Couette or a method-of-manufactured-solutions field, as in
VMFLGPU001/008/010's analytic references) -- **not** an experiment. VMFLGPU005's reference
is an experiment, so its physics limbs are correctly capped at GATE REACHED; the credential
this case can carry is limb B's PASS.

## 2a. Register format -- ONE ROW, predicted before compute (supervisor ruling)

**One register row, not three.** The whole-row headline verdict is the ceiling-limited
weakest-link -- **GATE REACHED when all limbs hold** (both CONTINUUM physics limbs cap there,
§2f.3), GATE FAIL if a held-and-converging channel is out of band, NOT A RESULT if any triple
is not CONVERGING or a plateau is unreached. This follows the **VMFLGPU001-R2 (register row
#39)** precedent, where all limbs held and the triple converged and the row is GATE REACHED,
not PASS. **Limb B's identity result (GPU==CPU) is recorded PER-LIMB WITHIN the row's value
column**, as #39 did -- not as a separate row.

**THE PASS COUNT DOES NOT MOVE ON LIMB B ALONE.** A GPU==CPU identity PASS is a real result
and is recorded, but it is NOT the physics-verification credential the register's PASS
headline tracks; the register's credential count (§6 of the charter) counts physics-limb
PASS rows, and this case -- both physics limbs capped GATE REACHED -- contributes none.
Predicted here, before compute, so the register format is not decided after the answer.

## 3. Solver, model and wall treatment -- FIRST-HAND, and FROZEN

**Model identification frozen (supervisor-verified from primary evidence):** *"Turbulence
model verified by the supervisor personally from `import_files/VMFL052_natural.cas` -- active
selectors `(kw-std-on? #t)`, `(rng-ke-on? #f)`, `(kw-low-re-mod? #t)`,
`(kw-wall-omega-treatment-r13? #t)`; standard k-omega low-Re, integrate-to-wall. This
identification is frozen."*

**Reproduced as OpenFOAM `kOmega`** (standard Wilcox) on a boundary-layer-RESOLVING r=2
triple with **CONTINUOUS (tanh) wall functions** (omegaWallFunction, kLowReWallFunction;
nutLowReWallFunction for nut). **Declared modelling difference (charter §7 / Ruling 4):**
OpenFOAM's standard `kOmega` does NOT carry Fluent's exact low-Re viscous-damping terms;
`kOmega` is registered as OUR reproduction and byte-identity with Fluent's low-Re k-omega is
NOT claimed.

**The paper's own warning, quoted verbatim, as a registered modelling caveat:** *"simple
turbulence modelling of such flows, and particularly the use of standard wall laws, is
totally inappropriate."* This is exactly why Ansys integrated to the wall (low-Re, y+ ~ 1)
rather than using wall functions, and why this reproduction resolves the boundary layer.

**THE BLENDER CLAUSE (numerics-critical, comparator-enforced).** omegaWallFunction (and the
k/nut wall functions) in v2606 default to a STEPWISE blender -- the discontinuous switch at
yPlusLam ~ 11.06 between an omegaVis and an omegaLog branch
(`omegaWallFunctionFvPatchScalarField.C`, switch at lines 231-317, STEPWISE case 233-247).
A STEPWISE switch corrupts a Roache triple: as the mesh refines and near-wall y+ crosses
yPlusLam at different levels, the effective wall model changes DISCONTINUOUSLY between
levels, tangling a model change into the observed order. **This case therefore sets
`blender tanh` on omega and k at every wall patch (0/omega, 0/k), registered here, and the
comparator READS the realised 0/omega and 0/k boundaryFields and REFUSES (exit 2) if the
blender is STEPWISE or unset on any wall-function patch.** Belt-and-braces: the comparator
also refuses if any level's max y+ exceeds yPlusLam WHILE a wall function is non-continuous
-- the exact and only condition under which STEPWISE corrupts the triple.

**Materials (FIRST-HAND from `import_files/VMFL052_natural.cas`, in `constant/`):**
Boussinesq rho_ref 1.184, cp 1005, k 0.02605 W/m-K, mu 1.81e-5, MW 28.966. Derived and
recorded: nu = mu/rho = **1.528716e-5 m2/s**; Pr = cp*mu/k = **0.698292**;
beta = 1/TRef = **3.355142e-3 /K** (ideal-gas value at the operating temperature -- the
archive prints Boussinesq rho_ref but NO explicit beta, so this closure is OURS, declared);
TRef = (307.85+288.25)/2 = **298.05 K**; Prt = 0.85. g = (0 -9.81 0).

**WEDGE: N/A.** This is a planar 2D cavity (one cell in z, frontBack empty), not an
axisymmetric wedge, so Charter Amendment-1.4 Clause A's sin(t)/t bias does not apply.

## 4. The gate -- four limbs

- **LIMB A -- GPU EXECUTION (binary, physics-critical).** PETSc `-log_view` per-event
  accounting, **PARSED BY COLUMN POSITION against the table's own header**: GPU %F is the
  FINAL column, CpuToGpu Count the 5th-from-last. GPU arm must show GPU %F >=
  **`GPU_PCTF_MIN = 99.0`** and CpuToGpu Count > 0; the forced-CPU control must show GPU %F
  == 0 and CpuToGpu Count == 0. **REFUSES on GPU %F > 100** (a percentage cannot exceed 100
  -- the exact guard that would have caught VMFLGPU007's silent false pass, where a
  max()-of-trailing-tokens reader returned the CpuToGpu SIZE IN MBYTES, 210, and cleared a
  99.0 floor). An ABSENT table REFUSES, never read as zero. **The GPU-arm floor is tested on
  the MIN over the MatMult/KSPSolve events and the forced-CPU control leak on the MAX -- the
  two arms use OPPOSITE aggregations on purpose: the GPU arm must be on the device on EVERY
  event (so a GPU MatMult cannot mask a p_rgh KSPSolve that fell back to the host -- the exact
  operation GAMG-on-GPU exists to place on the device), while the control must be zero on EVERY
  event.** Driven in `--selftest` on the REAL frozen bytes of VMFLGPU007's own gpu/cpu tables
  (`reference/REAL_LOGVIEW_*`), including an arm where MatMult %F=100 and KSPSolve %F=0 must
  refuse at the floor.
- **LIMB B -- GPU == forced-CPU (PASS-CAPABLE, the credential).**
  `|q_GPU - q_CPU| / |q_CPU| <= BAND_B = 1.0e-4` at EVERY level and channel. Identical mesh,
  identical scheme, so discretisation error cancels on both sides; a triple is irrelevant to
  it (§2f.3). This is the object under verification and where a PASS is earned.
- **LIMB C1 -- MID-HEIGHT vs Betts & Bokhari Table 1 (CONTINUUM, GATE REACHED ceiling).**
  Three channels, three bands, all must hold: C1a average Nusselt vs **5.85**; C1b max mean
  vertical velocity vs **0.139 m/s**; C1c centre-line dT/dx vs **68 C/m**.
- **LIMB C2 -- Y/h=0.05 vs the VMFL052 archive CSV (CONTINUUM + doubly indirect, GATE
  REACHED ceiling).** peak up-flow vs **+0.147826 m/s**, peak down-flow vs **-0.081739 m/s**,
  core temperature vs **292.246 K**. Reproduces the manual's OWN comparison.

**PAPER-vs-CSV DISAGREEMENT CLAUSE:** the paper (C1) and the CSV (C2) are SEPARATE channels
at different heights and different provenance. Any disagreement between them is **REPORTED,
never averaged, never reconciled** (comparator prints it beside the verdict).

**"Max. vert. velocity (Av)" reading, registered as ours (charter honesty):** the paper's
nomenclature defines V,v = mean and rms vertical velocity, so "(Av)" = the maximum of the
time-MEAN vertical velocity over the mid-height traverse. C1b is read that way. **Average
Nusselt reading:** hot-wall-averaged (the driving wall; the paper reports the hot side 1.1%
above the cold at the lower Ra, within its stated +/-5% experimental accuracy). On the
resolved integrate-to-wall mesh the wall flux is conductive, so
Nu_hot = |grad(T)_x|_hot_avg * W / dT_wall (from the wall-normal T gradient; the reader smoke
proved the wallHeatFlux FO refuses for the Boussinesq solver).

## 5. The Roache r=2 triple (rule 5) -- mesh family and gating

MEASURED pre-freeze (blockMesh + checkMesh on the lab box, 2026-08-27), a GEOMETRICALLY
SIMILAR r=2 family (every cell, including the first, halves between levels):

| level | NX x NY | first cell H1 | cells (birth-cert target) | max non-orth | max skew | aspect |
|---|---|---|---|---|---|---|
| L1 | 48 x 140  | 0.600 mm | **6720**   | 0 deg | 1.1e-13 | 25.95 |
| L2 | 96 x 280  | 0.300 mm | **26880**  | 0 deg | 3.4e-13 | 25.95 |
| L3 | 192 x 560 | 0.150 mm | **107520** | 0 deg | 6.8e-13 | 25.95 |

All three Mesh OK; per-cell x-expansion ratios 1.076/1.037/1.018 (gentle), overall
last/first ratio ~5.4 (near-constant across levels = geometric similarity). Orthogonal hex
(non-orth 0, skew ~0). y+ at 5 iterations, L1: max 4.48 across all patches (< yPlusLam 11.06)
-- the resolved integrate-to-wall regime the model requires; the graded run REPORTS y+ per
level and the constraint is **y+ < yPlusLam at all three levels including the coarsest**.

**RULE 5 GATING (in the comparator, per gated physics channel on the GPU arm):**
(1) any level not iteratively converged/plateaued -> **NOT A RESULT**; (2) triple not
CONVERGING (DIVERGENT / OSCILLATORY / STAGNANT / EXACT, or observed order below
**`P_MIN = 0.05`**) -> **NOT A RESULT**, value and triple printed; (3) CONVERGING -> the
channel's ceiling (GATE REACHED) inside band else **GATE FAIL**, with **GCI at Fs = 1.25**
printed. No GCI when the three values are not monotone. The triple can only turn a result
INTO NOT A RESULT, never the reverse. **The triple is REQUIRED even though it buys no PASS
here:** rule 5 limb (1) gates iterative convergence regardless, a non-CONVERGING triple is
NOT A RESULT whatever the value, and the GCI is a real uncertainty channel.

## 6. Strict completion (rule 4) and plateau

**Completion, per arm (comparator refuses on any physics-critical clause):** rc = 0; an End
line; last Time == endTime; **`Time =` line count == endTime** (the physics-critical clause,
L-342); the fields `T U p_rgh k omega nut alphat` present at endTime; every endTime field
NEWER than the case's own `0/T` (age guard). **INFRASTRUCTURE (reported, never refuses,
L-342):** the ExecutionTime line count -- petsc4Foam prints init timing lines inside Time=1,
so ExecutionTime count = endTime + 2 is expected and is a property of what the libraries
print, not of the physics.

**PLATEAU (chosen from the physics BEFORE the run, never loosened after):** on the gate
quantity's OWN history -- `probeU` U_y at the mid-height near-hot-wall point, one row per
SIMPLE iteration. Registered: window = last 1000 iterations, peak-to-peak
**<= 2.0e-3 m/s** (~1.4% of the 0.139 m/s velocity scale), with a LIVENESS floor (the channel
must have MOVED by > 1.0e-2 m/s over its history, else a dead channel and a converged one
read alike). **The 2.0e-3 m/s tolerance could NOT be shown to sit above the channel's own
detrended noise floor pre-compute** -- that would require a converged run, which is exactly
the compute this pre-registration precedes; it is registered as-is on the physics scale
(1.4% of 0.139 m/s) and, per the supervisor, a predicted NOT A RESULT is a legitimate
registered outcome, not a failure. **HONEST PREDICTION (supervisor's 007 caution):** turbulent natural-convection
RANS to steady state is SLOW and may not reach this window within the registered endTime;
if it does not, the honest verdict is **NOT A RESULT** (plateau not reached), NOT a loosened
tolerance. VMFLGPU007 landed NOT A RESULT on exactly this failure mode; this criterion is
picked to respect that line, not to flatter the run.

endTimes (SIMPLE iterations): L1 15000, L2 20000, L3 25000. Both arms of a level take the
SAME endTime (the condition that makes limb B a statement about the linear algebra alone).

## 7. Cost (rule 12)

| item | value |
|---|---|
| unit | GPU-hours (GPU arm) and core-minutes (forced-CPU arm) |
| estimate | GPU arm ~ 1-4 GPU-h across the six solves (L3 dominant; ~1e5 cells x ~2.5e4 iters, GAMG p_rgh); forced-CPU arm ~ 60-200 core-min |
| **cap (runaway guard, frozen)** | **GPU: `CAP_GPU_H = 6.0`** per solve; **forced-CPU: `CAP_CPU_ARM_CORE_MIN = 240`**. An overrun STOPS the run (rule 12); it does not get a new budget. |
| cost_basis | DERIVED, NOT MEASURED -- the box cannot read its billing (COMPUTE_BUDGET_CHARTER §5). GPU-hours priced from the console at freeze; published-list $0.8048/GPU-h is a placeholder, console figure owed. GPU spend is OUTSIDE the 2026-08-21 CPU blanket and needs its own per-item sign-off. |
| calibration | at completion, actual vs this estimate -> one row in `docs/COST_CALIBRATION.md` (rule 12). |

## 8. BAND DECISION ORDER (bands chosen BEFORE compute, justified, NOT widened)

| band | value | justification (pre-compute) |
|---|---|---|
| **C1a Nu** | **+/- 0.20 rel** | The HARDEST channel (supervisor caution 1): an integral wall quantity that eddy-viscosity models mis-predict on natural-convection cavities, and the paper says wall laws are "totally inappropriate" here. Standard-model natural-convection Nu errors are documented at 10-25%; 20% is set from that band, and C1a is EXPECTED to be the channel that misses. **If it misses, the limb lands GATE FAIL and we let it** -- a GATE REACHED ceiling means PASS is unreachable, NOT that the gate is soft. |
| C1b Vmax | +/- 0.20 rel | Peak velocity; better predicted than Nu but still model-limited. |
| C1c dT/dx | +/- 0.30 rel | Core horizontal gradient -- the hardest of the three to resolve; wider band from that. |
| C2 vup | +/- 0.20 rel | as C1b; C2 is GATE REACHED regardless (doubly indirect). |
| C2 vdown | +/- 0.30 rel | smaller magnitude -> larger relative sensitivity. |
| C2 Tcore | +/- 1.5 K abs | the core T is near the mean, so an ABSOLUTE band is the honest form. |
| BAND_B | 1.0e-4 rel | the linear-solver relative tolerance -- the two arms differ only in where the same system is solved, so they must agree to solver tolerance. |
| GPU_PCTF_MIN | 99.0 | PETSc GPU flop fraction floor for the GPU arm. |

**Uncertainty channels REPORTED beside the gate, not gated** (paper Table 1, Lower-Ra):
mid-cavity rms temperature 0.92 C, rms v 0.10 m/s, mid-cavity dV/dx 4.8 /s, rms u 0.053 m/s,
plus the +/-5% experimental accuracy on Nu -- these tell a reader how much scatter the
experiment itself carries at the gated point.

## 9. The grading path (fixed at the freeze commit)

Grade with, exactly:

    python3 cases/ansys_verification/VMFLGPU005/grade_vmflgpu005.py --run-root <run_root>

The comparator's `--selftest` is GREEN under BOTH `python3` and `python3 -O` (**28/28**,
zero bare `assert` statements). The launcher `run_vmflgpu005.sh` verifies, before any solver,
that the on-disk bytes of this pre-registration, the comparator, itself, the
field-completeness guard and the mesh generator match their committed HEAD blobs, with the
repository DERIVED FROM THE SCRIPT'S OWN LOCATION (007 Amendment 1), and completes the case
directory before any OpenFOAM utility runs (007 Amendment 2). Both hard-won repairs are
carried and were DRIVEN in the launcher-order smoke.

## 10. Pre-drop smokes (both run, both recorded)

- **READER SMOKE** (`SMOKE_READER_PATH_RECORD.txt`): 5-iteration CPU smoke from the FROZEN
  case on the lab box; every comparator reader driven on verbatim output and shown to return
  a non-zero value. Caught and repaired PRE-FREEZE two reader defects: alphabetical `_T_U`
  column order, and wallHeatFlux's incompatibility with the Boussinesq solver (Nu re-based on
  grad(T)). limb-A reader driven on the real 007 -log_view bytes.
- **LAUNCHER-ORDER SMOKE** (`LAUNCHER_SMOKE_RECORD.txt`): the launcher's assembly bytes
  (lines 144-164) extracted verbatim and DRIVEN; the case directory is complete before the
  first utility (rc 0, birth cert 6720); the reordered anti-pattern fails with the exact 007
  Amendment-2 error. The flip is exact.

## 11. What is NOT claimed

Nothing about Ansys (this box has no Fluent; the archive was read for setup and reference
numbers only). Nothing about GPU performance (a GPU arm slower than the CPU arm passes every
limb). No PASS on any physics limb (C1/C2 are CONTINUUM, capped GATE REACHED). No
byte-identity with Fluent's low-Re k-omega. No discretisation-converged claim unless the
triple is CONVERGING.

## 12. Frozen-set inventory (the launcher hashes these against HEAD)

    cases/ansys_verification/VMFLGPU005/PREREGISTRATION.md      (this file)
    cases/ansys_verification/VMFLGPU005/grade_vmflgpu005.py     (comparator)
    cases/ansys_verification/VMFLGPU005/run_vmflgpu005.sh       (launcher)
    cases/ansys_verification/VMFLGPU005/field_completeness.py   (field guard)
    cases/ansys_verification/VMFLGPU005/resolve_blockmesh.py    (mesh generator)

Supporting (not in the launcher's freeze list, cited by the above):
`case/` (the OpenFOAM case with 0/, constant/, system/ templates), `reference/` (the two
archive CSVs, the two real 007 -log_view tables, the manual page extract).
