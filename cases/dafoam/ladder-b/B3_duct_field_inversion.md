# Ladder B3 — CBFS field-inversion pilot: macro reader, DASimpleFoam primal, timed adjoint pilot

Date: 2026-07-28. Machine-readable companion: `B3_duct_field_inversion.json`.
Scope per docket: (1) macro-expanding reader for CBFS's `#include`-based LES
fields, verified; (2) stand up DAFoam `DASimpleFoam` on CBFS, confirm the
primal reproduces B2's converged field; (3) ONE timed adjoint solve on CBFS,
measured; (4) full field inversion, gated on (3). This rung reached a real,
measured, honest blocker at stage 3 and **stage 4 (full inversion) did not
run** — per the docket, that is the correct outcome, not a failure to
report around.

## Headline result

- **Stage 1 (macro reader): DONE, verified.** Also found and fixed a
  *second*, more dangerous bug beyond B2's "silent None" report: a
  duplicate-key shadowing issue in `0/p_LES` that a naive fix would have
  turned into a silently-wrong (not just missing) value.
- **Stage 2 (DASimpleFoam primal on CBFS): DONE.** After fixing three real
  case-setup issues (below), DAFoam's primal, warm-started from B2's
  converged field with CBFS's actual boundary conditions preserved,
  converges to `primalMinResTol=1e-6` and matches B2's independently-run
  plain-OpenFOAM baseline to **0.087% (U), 0.23% (p), 1.41% (k), 1.20%
  (omega) scaled MAE**.
- **Stage 3 (timed adjoint pilot): BLOCKED, not silently routed around.**
  The discrete-adjoint GMRES solve diverges with PETSc
  `KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at iteration 0, reproduced
  identically across two primal convergence levels (1e-4, 1e-6), two
  objective-function types (a custom field-variance loss and a standard
  force objective known to work in this lab's naca0012 case), and two
  ILU preconditioner fill levels (1, 4). The primal-phase cost and the
  adjoint's *fixed* setup cost (coloring, Jacobian partial-derivative
  matrix construction) are measured; the GMRES iteration cost itself —
  the dominant, scaling-critical unknown B1 flagged — could not be
  measured because no run completed a single GMRES iteration.
- **Stage 4 (full CBFS field inversion): DID NOT RUN.** Correctly gated by
  stage 3's unresolved blocker, per the docket's own instruction.
- **Leakage: clean.** Only CBFS ground truth was read (the paper's
  training case, explicitly not one of the 8 scored test cases). No duct
  (`AR_1_Ret_360`, `AR_3_Ret_360`) LES/DNS ground truth was opened at any
  point in this rung.

## Stage 1 — macro-expanding CBFS LES field reader

**The problem, restated precisely.** CBFS's `0/U_LES`, `0/k_LES`,
`0/tauij_LES`, `0/p_LES` use OpenFOAM's textual `#include "relpath"` splice
mechanism plus `$name` dictionary-entry substitution to assemble their
`internalField`/`boundaryField` values from separate
`interpolatedFields/{U,k,tauij,p}_{internalField,inlet,outlet,bottomWall,
topWall}` files. `Ofpp.parse_internal_field` (B2's parser) scans line-by-line
for a line starting with `internalField` that literally contains the
substring `nonuniform`/`uniform`; the on-disk line
`internalField   $U_internalField;` contains neither, so Ofpp's scan falls
through and returns `None` with no exception raised.

**Fix, implemented at**
`demo-output/website/dafoam/ladder-b/duct_baseline/macro_field_reader.py`:
recursively splice `#include` file contents into the document, build a
last-entry-wins dict of top-level `name -> value` entries (see next
paragraph for why last-wins matters), resolve `$name` references against
that dict, then hand only the single resolved entry text to Ofpp's own
`parse_internal_field_content`/`parse_boundary_content` (reusing its
already-trusted low-level array parser rather than reimplementing OpenFOAM
list parsing).

**A second bug found while building this, not in B2's original report:**
`0/p_LES` has **two** `internalField` entries — a placeholder
`internalField   uniform 0;` written *before* the `#include` block, then
legitimately overridden by `internalField   $p_internalField;` *after* it
(OpenFOAM dictionaries are last-entry-wins). A naive "expand the macros then
re-run Ofpp's scanner on the whole document" approach reproduces Ofpp's
first-match bug in a *more dangerous* form: not `None`, but a **plausible,
wrong, silently-returned value** (`uniform 0.0` instead of the real
21000-cell field). The reader avoids this by building an explicit
last-wins entries dict first and handing the caller only the resolved
`internalField` entry, never the whole flattened document.

**Verification (`verify_macro_reader.py`), run and passing:**
1. Round-trip: take CBFS's own `0/U` inlet-boundary data (150 vectors,
   already parseable by plain Ofpp with no macros involved), re-serialize it
   as a synthetic file using the *same* `#include` + `$name` structure as
   `0/U_LES`, parse it through the macro reader, and confirm
   `np.array_equal` (exact, no tolerance) against the Ofpp-parsed ground
   truth. **PASS — byte-identical.**
2. Negative control: confirm plain Ofpp, run on the *same* synthetic
   macro'd file, returns `None` — proves the test genuinely exercises the
   silent-failure mode rather than being accidentally macro-free.
   **Confirmed None.**
3. Duplicate-key regression test, modeled directly on the real `p_LES` bug:
   a placeholder `internalField uniform 0;` shadowed by a later
   `#include`'d real value. Confirms the reader returns the *real* (later)
   value, not the placeholder. **PASS.**

**What the CBFS LES fields actually contain** (macro-resolved, all 21000
cells, matching `constant/polyMesh` cell count exactly):

| Field | Shape | Min | Max | Mean |
|---|---|---|---|---|
| `U_LES` | (21000, 3) | [-0.130, -0.109, -0.0051] | [1.031, 0.063, 0.0028] | [0.832, -0.0148, -0.00002] |
| `k_LES` | (21000,) | 2.81e-08 | 0.0375 | 0.00405 |
| `tauij_LES` | (21000, 6) | (component-wise) [0, -0.0159, -0.00046, 7e-9, -0.000213, 0] | [0.0367, 0.00218, 0.00054, 0.0206, 0.00031, 0.0234] | [0.00388, -0.00062, 0.0000078, 0.0017, 0.0000003, 0.00253] |
| `p_LES` | (21000,) | -0.0910 | 0.1092 | 0.0429 (this is the one that was silently `0.0` before the duplicate-key fix) |

## Stage 2 — DASimpleFoam primal on CBFS

**Three real case-setup issues found and fixed, each documented with cause
(none are physics-changing hacks except where explicitly noted and
justified):**

1. **`transportProperties` missing `Pr`/`Prt`.** DAFoam's `DASimpleFoam`
   wrapper unconditionally reads these even for a purely hydrodynamic
   incompressible run with no energy equation active; B2's plain-OpenFOAM
   run never needed them. Added standard air values (`Pr 0.7; Prt 1.0;`,
   matching this lab's own naca0012 DAFoam case) — inert for the
   momentum/turbulence equations actually solved.
2. **2D `empty`-type `frontAndBack` patch not supported by DAFoam's mesh
   warping (IDWarp).** `DACheckMesh` fatal-errors ("Mesh geometric
   directions is less than 3 and not supported!") on a true-2D
   `empty`-patch mesh. Fixed by converting `frontAndBack` from `empty` to
   `symmetry` in `constant/polyMesh/boundary` and every `0/` field file
   (`U`, `p`, `k`, `omega`, `nut`, `phi` deleted rather than converted —
   see below), plus declaring both z-planes explicitly via
   `meshOptions["symmetryPlanes"]`. This is DAFoam's own standard,
   documented workaround for 2D cases (the exact same pattern already used
   by this lab's `naca0012` DAFoam case, which uses `symmetry1`/`symmetry2`
   patches rather than `empty`) — physically equivalent to the true-2D
   `empty` treatment for a field with no z-variation, not a physics change.
3. **`primalBC.useWallFunction: True` forcibly overrides CBFS's real wall
   BC types.** Tried first, then REJECTED after confirming via grep
   (`Setting k wall BC for bottomWall. BCType=kqRWallFunction`) that it
   silently replaces CBFS's actual low-Re near-wall treatment
   (`nutLowReWallFunction`, `k` `fixedValue 1e-15`) with high-Re wall
   functions (`nutkWallFunction`, `kqRWallFunction`) — a genuine physics
   change, not solver noise. Confirmed by measurement: with the override
   active, the converged field disagreed with B2's baseline by up to 19%
   (k). Fixed by setting `primalBC: {}` (no override), which reproduced the
   agreement in the table below.

**`0/phi` deleted rather than boundary-converted**: setting `frontAndBack`
to `type symmetry` for the face-flux field `phi` crashed `decomposePar`
("Required entry 'value' missing", since a `surfaceScalarField` on a
`symmetry` patch needs an explicit value unlike a `volField`). `phi` is a
derived quantity (`fvc::flux(U)`) that OpenFOAM recomputes from `U` at
solver start whenever it is absent from `0/` — this is standard, most
OpenFOAM cases ship no initial `phi` at all. Deleting it is not a physics
change.

**Reproduction result** — primal warm-started from B2's own converged CBFS
field (`duct_baseline/CBFS/30000/{U,p,k,omega,nut,phi}`), run serially
(1 rank) to `primalMinResTol=1e-6`, field-vs-field scaled MAE against B2's
baseline at successive iteration counts (showing genuine convergence, not
a fixed-BC-error plateau):

| Iterations | U | p | k | omega | nut |
|---|---|---|---|---|---|
| 300 | 0.82% | 5.86% | 5.18% | 1.82% | 2.93% |
| 500 | 0.149% | 0.922% | 1.80% | 1.23% | 0.725% |
| 1000 | 0.0907% | 0.284% | 1.44% | 1.198% | 0.481% |
| 1223 (converged, tol satisfied) | **0.0865%** | **0.233%** | **1.414%** | **1.198%** | **0.460%** |

For comparison, B2's own cross-fork agreement (OpenFOAM-7 original vs our
v2606 reproduction, same solver family "plain OpenFOAM", no DAFoam AD
wrapper involved) was 0.068% for CBFS. Our DAFoam-vs-plain-OpenFOAM U
agreement (0.087%) is in the same range; p/k/omega are 3-20x looser, plausibly
from the DAFoam-bundled OpenFOAM v2506 vs our plain-OpenFOAM v2606 point-release
gap (a second, smaller version gap on top of B2's already-documented
OpenFOAM-7-vs-v2606 fork gap) compounding with DAFoam's own AD-instrumented
solver internals — not further decomposed this rung, flagged rather than
asserted.

**Primal cost, measured:**

| Config | Ranks | Iterations | Wall time (solver-internal) | Cost/iteration |
|---|---|---|---|---|
| Cold IC, `run_model` | 1 | 100 | 19.79 s | 0.198 s/iter |
| Warm IC (B2 field), `run_model` | 1 | 1223 (to tol 1e-6) | 234.97 s | 0.192 s/iter |
| Warm IC + patchV-perturbed inlet | 4 | 500 | 21.06 s | 0.042 s/iter |
| Warm IC + patchV-perturbed inlet | 4 | 1580 (to tol 1e-6) | ~104 s (to adjoint start) | ~0.066 s/iter |

4-rank parallel gives roughly 3-5x speedup over serial on this 21000-cell
mesh — consistent with, not contradicting, B2's own baseline-cost figures.

## Stage 3 — timed adjoint pilot: BLOCKED

**Design variable substitution, disclosed, not hidden.** The paper's real
design variable is a spatially-varying field `beta(x)` multiplying the SST
omega equation's destruction term, requiring a custom OpenFOAM turbulence-
model library whose source is not distributed anywhere in the public
benchmark clone (documented in B2). Building that library from scratch is
out of scope for a timed pilot. This pilot instead used **inlet patch
velocity** (`patchVelocity`, magnitude+angle) as a stand-in design variable
— chosen because the discrete-adjoint linear-solve cost is dominated by one
transpose solve of the residual Jacobian (sized by the full state vector:
all cells x all state variables), which is structurally the same
regardless of which design variable's sensitivity is requested. Using
`patchV` overwrites CBFS's real nonuniform inlet profile with a uniform one
for the duration of this pilot only — documented in `runScript.py`, not
hidden. Stage 2's reproduction check (above) used a completely separate
script (`runScript_stage2.py`) with no design variable and the case's real
BCs untouched.

**Objective function, legitimate and CBFS-only (no leakage).** DAFoam's
native `DAFunctionVariance` (`type: variance, mode: field, source: allCells`)
computes a per-cell variance against a reference field named
`<varName>Data` read from `0/`. This is DAFoam's own built-in mechanism for
field-inversion-style loss functions. `0/UData` was written from CBFS's own
macro-resolved LES `U_LES` field (Stage 1) — CBFS is the paper's training
case, so this carries zero leakage exposure per the docket's rule.

**A second silent-failure trap found and fixed.** `DAFunctionVariance`
hardcodes reading its reference data from the *literal* folder `"0"`
(`DAFunctionVariance.C: checkRefDataFolder = Foam::name(0)`), independent of
the case's actual `startFrom`/`startTime`. With `startFrom=latestTime` and
many intermediate time directories left on disk from Stage 2's iterative
debugging (`2, 100, 300, ..., 1223`), DAFoam's automatic parallel
decomposition (`-np 4`) only decomposed the run's actual starting time
(`1223`) and never touched `"0"` — so `processorN/0/UData` did not exist.
`DAFunctionVariance` printed a WARNING ("Can't find data files...") and
silently fell back to `isRefData_=0`, giving a functionValue of exactly
`0.0` and a correspondingly all-zero adjoint right-hand side — GMRES
"converged" in 0 iterations with a fake, non-representative zero residual.
**Caught by checking the printed objective value (`[0.]`) and grepping for
the WARNING rather than trusting the reported "success," exactly the
failure mode this rung was told to watch for.** Fixed by forcing
`startFrom: startTime; startTime: 0;` and clearing all stray intermediate
time directories so decomposition always covers `"0"`.

**The real blocker, after that fix.** With the objective function
confirmed genuinely reading LES data (`"Find 63000 reference points for
variance of U"`, 21000 cells x 3 components), the adjoint linear solve
itself fails:

```
Solving Linear Equation...
Main iteration 0 KSP Residual norm 7.09e-04
**Completed**! Total iterations: 0. PetscConvergedReason: -9.
Residual tolerance not satisfied, solution failed!
```

`PetscConvergedReason -9` is `KSP_DIVERGED_NANORINF` — PETSc detected
NaN/Inf at the very first iteration, before any actual GMRES progress.
Reproduced identically across four independent configurations, ruling out
each as the sole cause:

| Variant | primalMinResTol | Objective | pcFillLevel | Result |
|---|---|---|---|---|
| Pilot run 5 | 1e-4 | variance (CBFS LES) | 1 | Diverged, reason -9 |
| Pilot run 6 | 1e-6 (tighter) | variance (CBFS LES) | 1 | Diverged, reason -9, nearly identical residual (7.092e-4 vs 7.099e-4) |
| Diagnostic 1 | 1e-6 | **force (CD)**, standard type used successfully in naca0012 | 1 | Diverged, reason -9 |
| Diagnostic 2 | 1e-6 | force (CD) | **4** (deeper ILU fill) | Diverged, reason -9 |

Mesh quality was checked and is not the cause: `DACheckMesh` reports max
aspect ratio 14.76, max non-orthogonality 33.3°, max skewness 0.26, all well
inside DAFoam's own thresholds (1000, 70°, 4) and printed "OK". Tightening
primal convergence 100x did not change the divergence. Switching to a
standard, previously-working objective type did not change it. Deepening
the ILU preconditioner 4x did not change it. **The root cause is not
resolved within this rung's time budget** — flagged as an open blocker, not
silently routed around or hidden behind a fabricated number.

**What WAS measured, honestly, despite the block:**

| Component | Cost (4 ranks) | Notes |
|---|---|---|
| Primal re-solve (warm start, patchV-perturbed BC, to `primalMinResTol=1e-6`) | ~104 s / 1580 iterations | Measured directly, multiple runs, consistent |
| Adjoint coloring (Jacobian sparsity pattern; one-time, cached to `dRdWColoring_4.bin` afterward) | ~25.4 s | Measured once, before the reference-data bug was found; not re-measured post-fix (time budget) |
| `dRdWTPC` (Jacobian partial-derivative matrix construction; recurs per adjoint call) | ~13.1 s | Same run |
| GMRES linear solve itself (the dominant, iteration-count-scaling cost B1 flagged as the key unknown) | **NOT MEASURED — solver never completes a single iteration** | This is the actual blocker |

**Implied total for the full inversion: cannot be honestly estimated.**
B1's 140-420 core-minute range assumed the GMRES solve executes at all; with
zero measured GMRES iterations, any extrapolation would be a fabricated
number dressed as a measurement. The fixed per-call overhead alone (coloring
+ dRdWTPC, ~13-38 s per call on 4 ranks even before any GMRES iteration)
is consistent with, but does not confirm, B1's lower bound.

## Stage 4 — NOT RUN

Correctly gated by Stage 3's unresolved blocker, per the docket's explicit
instruction ("an honest cost measurement that says 'does not fit' is a
real result and is what stage 3 exists to produce"). No field inversion was
attempted on CBFS or any other case this rung.

## Memory

`--memory=6g` (later attempts also tried with the same cap) was used for
every container this rung; **no run was OOM-killed** (`docker inspect`
exit codes seen were 0, 1, 2, 59 — application/MPI-level failures, never
137). This establishes 6 GB is sufficient for the primal + coloring +
`dRdWTPC` phases actually exercised, at up to 4 ranks, on this 21000-cell
mesh. **Gap, disclosed rather than hidden:** a `docker stats`-based
peak-memory sampler was set up to run alongside each container (per the
coordinator's explicit instruction to measure, not guess, peak RSS before
sizing any cap) but had a race-condition bug — it checked whether the named
container was already running before `docker run` had finished creating
it, so the polling loop exited immediately on every one of 6 attempts
without capturing a single data point. **Peak per-container RSS was NOT
actually measured this rung.** MemAvailable was checked and stayed above
12 GB (the 6 GB safety threshold) throughout, with 2-3 other concurrent
DAFoam agents and a mega-batch process also running on the box.

## Explicit leakage statement

**Ground truth read this rung, and why each is legitimate:**

- `duct_baseline/CBFS/0/{U_LES,k_LES,tauij_LES,p_LES}` — CBFS's own LES
  reference fields. CBFS is the paper's field-inversion **training** case,
  explicitly listed as public and non-scored in the benchmark's own
  documentation (confirmed in B1/B2). Read for: (a) Stage 1 macro-reader
  verification/demonstration, (b) writing `0/UData`, the reference field
  for the Stage 3 adjoint pilot's loss functional. **Legitimate per the
  leakage rule — CBFS is not a test case.**
- `duct_baseline/CBFS/30000/{U,p,k,omega,nut,phi}` — our own (B2-produced)
  converged plain-OpenFOAM baseline field for CBFS, used to warm-start the
  DAFoam primal in Stage 2 and as the comparison target for the
  reproduction-agreement table. Not LES ground truth, and CBFS is not a
  test case either way.

**Ground truth NOT read this rung:** `AR_1_Ret_360` and `AR_3_Ret_360`
(the two duct test cases named in the leakage rule) — no file under
`duct_baseline/AR_1_Ret_360/` or `duct_baseline/AR_3_Ret_360/` was opened,
read, or referenced by any script in this rung. No training, validation,
tuning, or selection against duct ground truth occurred, because no duct
compute was run at all this rung — Stage 4 (which would have been the first
point at which duct data could legitimately enter, for *final forward
scoring only*, per the docket) never ran.

## Lesson

Three separate silent-failure traps were found and caught in this single
rung by the same discipline (check the return value / printed message,
never trust a suspiciously round or trivially-obtained number): B2's
original `None`-on-macro'd-field bug (Stage 1), a duplicate-key
shadowing bug in `p_LES` that would have produced a *wrong, not missing*
value (Stage 1), and a decomposition-scope bug that silently zeroed the
Stage 3 objective and its gradient (Stage 3). All three were caught before
being reported as results. The adjoint `DIVERGED_NANORINF` blocker is a
fourth, still-open issue — real, reproducible across 4 independent
configuration changes, and reported as a blocker rather than worked around
with a fabricated cost number. The `primalBC.useWallFunction` physics
substitution (Stage 2) is a reminder that DAFoam's convenience options can
silently change the physics being solved, not just the numerics — always
grep the actual applied BC types, don't assume a flag named
"useWallFunction" only changes solver mechanics.

## Evidence files

- This report: `demo-output/website/dafoam/ladder-b/B3_duct_field_inversion.md`
- Machine-readable record: `demo-output/website/dafoam/ladder-b/B3_duct_field_inversion.json`
- Macro reader + verification:
  `demo-output/website/dafoam/ladder-b/duct_baseline/macro_field_reader.py`,
  `demo-output/website/dafoam/ladder-b/duct_baseline/verify_macro_reader.py`
- DAFoam case working directory (scripts, logs, dictionaries):
  `demo-output/website/dafoam/ladder-b/B3_work/CBFS/` — `runScript.py`
  (adjoint pilot, patchV DV + variance objective), `runScript_stage2.py`
  (plain primal reproduction check, no DV), `runScript_diag_force.py`
  (diagnostic: standard force objective, used to isolate the adjoint
  divergence from the custom objective), plus all `*_run*.log` files
  referenced above.
