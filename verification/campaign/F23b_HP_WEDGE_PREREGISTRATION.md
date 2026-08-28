# F23b — PRE-REGISTRATION: Hagen–Poiseuille pipe flow on an OpenFOAM axisymmetric WEDGE, re-registered after F23's `NOT A RESULT` (simpleFoam, streamwise cyclic, fixed body force, 4 ranks)

**Team:** cfd. **Case id:** `F23b_HP_WEDGE`. **Successor to `F23_HP_WEDGE`, which
stands `NOT A RESULT` on its own record and is neither re-graded nor amended by this
file.** **Written before any compute on this rung. ZERO CORE-MINUTES SPENT** in
`cases/F23b_HP_WEDGE/` or in `verification/runs/F23b_HP_WEDGE_runs/` (§10).
**Status at drafting: DRAFT, UNCOMMITTED, NOT FROZEN.** The freeze commit is the
supervisor's act under `SUPERVISION_CHARTER.md` §3 check 1; this lane wrote the file
and launched nothing. **Every arm this rung runs — the pre-ladder arms of §5.5 as well
as the three ladder levels — runs UNDER the freeze sha, and every one of them is costed
and capped here, in §9.0 and §9.3, before it starts (rule 2, rule 12).** After first compute the gates, thresholds, cap and labels below
are closed; changes land only as dated addenda that cannot alter them.

Templates in structure and rigour: **F17c**
(`verification/campaign/F17c_KV40_FLOOR_PREREGISTRATION.md`) for §4/§5/§9, F23 itself
for the case, the model and the bands.

**Capability-grid cell (068c2bf0): axisym · steady · incompressible. CPU-only; no GPU
arm exists on this rung and `BLOCKED-GPU` is not used.**

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled so at registration; not a result; counts toward no challenge column; not filmed.

---

## 1. WHY F23b EXISTS, AND WHY A RE-REGISTRATION RATHER THAN A PATCH

F23 graded **`NOT A RESULT`**. Its coarse and medium levels completed on every rule-4
clause; its fine level never reached the solver, because `build_f23.py:129–130`
refused the built mesh:

    ABORT (build_f23): checkMesh wedge angle 0.0400027202903 is not the registered half angle 0.04

Two levels are not a Roache triple. **`checkMesh` itself printed `Mesh OK.` at all
three levels, fine included** — verified in this invocation by reading
`verification/runs/F23_HP_WEDGE_runs/fine/log.checkMesh` (its geometry block ends
`Mesh OK.` / `End`). The lab's guard refused a mesh OpenFOAM's own checker passed.

**A patch is not available.** `VERIFICATION_CHARTER.md:2158` (Amendment v1.11, point
3): *"A mesh repair applied to one level of a graded refinement family makes the three
values incommensurable; the standard's §2.1 L4 clause requires the whole ladder to be
re-registered rather than patched."* And `VERIFICATION_CHARTER.md:2153` (same
amendment, point 1) confines §2d.1's four-condition repair exception to *"the
comparator, never the gate, the threshold, the cap or the label."* The wedge tolerance
lives in the **mesh** path, upstream of the comparator, so that route is not on offer
either. **Both quotations were read from that file at those line numbers in this
invocation.** The whole ladder is therefore re-registered.

**F23b carries TWO changes, not one, because triage found TWO independent fatal
defects.** §4 is the wedge guard the supervisor's brief named. §5 is a defect the
brief did not name and this lane measured: **F23's iterative floor was inadequate at
every level, by four orders of magnitude, and F23's ladder was not runnable as
registered at any cap.** Fixing the tolerance alone would have bought a completed
three-level ladder that graded `NOT A RESULT` on the plateau limb — the F17c outcome,
for the F17c reason. **This is flagged for the supervisor under §2c (`one change per
run` is a discrimination requirement): F23 produced no graded value at all, so there
is no result for a second change to confound. The supervisor may rule otherwise and
split F23b into two rungs; this lane does not decide it (§14, Q1).**

---

## 2. THE CASE — CARRIED FORWARD FROM F23 §1, UNCHANGED

Fully developed laminar pipe flow, **Re_D = 100**: R = 0.5 (D = 1), ν = 0.01,
Ubar = 1, u(r) = 2 Ubar (1 − r²/R²), −dp/dx = **G = 0.32**, u_max = 2, **f·Re = 64**.
Streamwise `cyclic` with a **fixed** `vectorSemiImplicitSource` (not the adaptive
`meanVelocityForce`), so the parabola is an exact solution of the case as posed, the
discrete problem is linear, and both gate quantities are readings of the velocity
field. **L = 16 D = 16.0**, r ∈ [0, R] along +y, wedge symmetric about z = 0, **half
angle a = 0.04°**, wall vertices at EXACT radius R.

**Kept BYTE-FOR-BYTE from F23** (no change is registered to any of these):

- **The patch names and types**: `inlet`/`outlet` (cyclic pair), `wall` (wall,
  `noSlip`), `wedge1`/`wedge2` (type `wedge`), `defaultFaces` (empty). **Unchanged. This
  lane has no independent reason to rename any patch on this case**, and records that a
  patch-naming recommendation reaching it from elsewhere concerned a different case
  (F3S) and is not applied here.
- `case/system/blockMeshDict.template`, `case/constant/fvOptions` (`U ((0.32 0 0) 0)`,
  `volumeMode specific`, `selectionMode all`), `case/constant/transportProperties`
  (`nu 0.01`), `case/constant/turbulenceProperties`, `case/0/p`, `case/0/U.template`,
  `case/system/fvSchemes`, `case/system/decomposeParDict` (`numberOfSubdomains 4`,
  `simple n (1 4 1)`).
- **`HALF_ANGLE_DEG = 0.04`**, and its N-AV9 justification. The deviation §4 measures
  scales as 1/sin(a), so a larger half angle would ease the guard — **and it is not
  changed**, because (i) the N-AV9 O(a²) sectional bias is the reason 0.04° was chosen
  (at 1° the bias exceeds every level's discretisation error and the ladder is
  degenerate by construction), and (ii) §4's replacement guard removes the need.
- The exact solution, the discrete model `exact_f23.discrete()`, and every predicted
  value and band in §6.

**Changed, and only these two files:** `case/system/fvSolution` and
`case/system/controlDict` (§5.3), plus the new builder's wedge guard (§4.3).

---

## 3. THE LADDER — THREE LEVELS (§9.1), `dim = 2`, r = 2.000 EXACTLY

Square cells dx = dr = R/NR at every level; both directions refine by exactly 2.

| level | NR × NX | cells | wedge faces per patch | h = dr | ranks |
|---|---|---|---|---|---|
| coarse | 64 × 2048 | 131,072 | 131,072 | 1/128 | 4 |
| medium | 128 × 4096 | 524,288 | 524,288 | 1/256 | 4 |
| fine | 256 × 8192 | 2,097,152 | 2,097,152 | 1/512 | 4 |

**DECOMPOSITION SEED (required field): `none`** — `simple` geometric decomposition,
deterministic, no RNG; 4 subdomains at every level; never reconstructed (the grader
reads `processor*/`).

---

## 4. THE WEDGE GUARD — WHAT F23 DIED ON, MEASURED, AND ITS REPLACEMENT

### 4.1 The measurement, and what it cost

**Cost: 0.000 solver core-minutes.** Every reading below is a read-only diagnostic
over artifacts F23 already wrote. No solver ran; no run root was written to; nothing
was written into `verification/runs/F23_HP_WEDGE_runs/`. Wall cost ≈ 6 min of one
core in Python, charged to INFRASTRUCTURE and folded into no case ratio
(`COMPUTE_BUDGET_CHARTER.md` §6).

The three levels' own `log.checkMesh` files (one named file read per check) report:

| level | wedge1 = wedge2 angle | deviation from 0.04° | vs F23's fixed 1e-6 tol | `Mesh OK.` |
|---|---|---|---|---|
| coarse | 0.0400002766821 | 2.766821e−07 | 0.28× | yes |
| medium | 0.0400007984975 | 7.984975e−07 | **0.80×** | yes |
| fine | 0.0400027202903 | 2.720290e−06 | **2.72× — REFUSED** | **yes** |

**Medium already sat at 80 % of the tolerance budget. The ladder was one refinement
level from refusal at registration time, and nothing in F23 computed that.**

This lane then reimplemented, from `constant/polyMesh` alone, exactly what
`wedgePolyPatch` computes and `checkMesh` prints — the OpenFOAM face-area-vector
construction, the arithmetic mean of the unit face normals, the componentwise-snapped
`centreNormal_`, and `acos` of their dot product — and **reproduced checkMesh's printed
value to its last printed digit at all three levels**:

| level | reimplementation | `log.checkMesh` |
|---|---|---|
| coarse | 0.04000027668213 | 0.0400002766821 |
| medium | 0.04000079849752 | 0.0400007984975 |
| fine | 0.04000272029028 | 0.0400027202903 |

### 4.2 WHAT THE MEASUREMENT SAYS — the mechanism, measured, not guessed

The supervisor's brief offered three candidates. **The answer is (i), an averaging
artifact — but it is not an extreme-value artifact, and it is not geometry at all.**

**The mesh is correct at every face, at every level.** Computing each wedge face's
angle to the cardinal normal in a **well-conditioned** small-angle form —
`atan2(hypot(n_x, n_y), |n_z|)`, which never evaluates `acos` near 1 — gives:

| level | max over faces of \|angle/0.04 − 1\| |
|---|---|
| coarse | 1.895413e−10 |
| medium | 2.449031e−10 |
| fine | **7.569059e−10** |

Ten orders of magnitude below any physically meaningful mis-build, at every level.

**The deviation is floating-point summation error in `gAverage(faceNormals)`,
amplified by the ill-conditioning of `acos` near 1.** `wedgePolyPatch` stores
`cosAngle_ = centreNormal_ & n_` where `n_` is the **arithmetic mean of the unit face
normals and is never renormalised**. Summing N ≈ NX·NR nearly-identical unit vectors
accumulates rounding, so |n̄| lands **below 1**, and `d(acos)/dc = −1/sin(a) = −1432`
turns that deficit into an angle. Replacing the summation with `math.fsum` — **the same
points, the same faces, the same geometry, nothing else changed** — collapses it:

| level | 1 − \|n̄\| (naive sum) | 1 − \|n̄\| (`math.fsum`) | acos, naive | acos, fsum |
|---|---|---|---|---|
| coarse | 3.371303e−12 | **0.0** | 0.04000027668213 | 0.03999999999967 |
| medium | 9.729550e−12 | **0.0** | 0.04000079849752 | 0.03999999999967 |
| fine | 3.314704e−11 | **0.0** | 0.04000272029028 | 0.03999999999967 |

And the deficit predicts the deviation to three digits through
`Δa = (1 − |n̄|)/sin(a)`: 2.766834e−07 vs 2.766821e−07 (coarse), 7.985058e−07 vs
7.984975e−07 (medium), 2.720383e−06 vs 2.720290e−06 (fine).

**Candidate (ii) — catastrophic cancellation near the axis — is EXCLUDED by
measurement, not by argument.** Across coarse's 131,072 wedge faces there are **3
distinct `u_z` values and 10 distinct `u_x` values**, with `Var(u_z) = 8.45e−32`; the
per-face deviation binned by radius decile is **flat**, and if anything smaller in the
inner deciles than at the wall. The innermost faces' normals are bit-identical to the
outermost faces'. **The supervisor was right not to want (ii) adopted on a hunch: it is
false.**

**The growth law.** 1 − |n̄| is bounded by N·ε for sequential summation
(ε = 2.220446049250313e−16). Measured, the ratio (1 − |n̄|)/(N·ε) is **0.1158 /
0.0836 / 0.0712** across the ladder — a fraction of the bound, falling slowly. So the
deviation grows **asymptotically linearly in the cell count and inversely with
sin(a)**; the brief's "~3× per level" is the observed 2.886 / 3.407, which is this law
with partial cancellation, not a rule.

**Therefore F23's guard was measuring machine arithmetic inside checkMesh's averaging
loop, not mesh geometry.** A fixed absolute tolerance on a quantity whose floor grows
with N was guaranteed to fail at some level; the only question was which.

### 4.3 THE REGISTERED GUARD — `G-WEDGE`, three limbs

**Limb 1 — PRIMARY, well-conditioned, refinement-aware.** From the level's own
`constant/polyMesh`, for **every face of both `wedge1` and `wedge2`**, compute the
angle to the componentwise-snapped cardinal normal as
`degrees(atan2(hypot(n_x, n_y), |n_z|))` and require

    max over faces of | angle / HALF_ANGLE_DEG − 1 |  <=  TOL_REL_WEDGE(level)

`acos` is never called. **The tolerance is derived by the L-346 discipline the F17
family uses**: a wedge half-angle relative error `eps` perturbs the cell volumes, and
hence the graded solution, at order `eps`; require that contribution to sit an order
below **that level's own predicted discretisation error** in `f·Re` (from §6, F23's
model, carried forward):

    TOL_REL_WEDGE(level) = max( 0.1 × |E_pred_fRe(level)| / 64 ,  FLOOR_REL )
    FLOOR_REL = 1.0e-08   (frozen)

| level | E_pred_fRe | **TOL_REL_WEDGE** | measured (§4.2) | occupancy | margin |
|---|---|---|---|---|---|
| coarse | −7.778e−03 | **1.215313e−05** | 1.895413e−10 | 1.56e−05 | ×64,100 |
| medium | −1.922e−03 | **3.003125e−06** | 2.449031e−10 | 8.16e−05 | ×12,300 |
| fine | −4.571e−04 | **7.142188e−07** | 7.569059e−10 | 1.06e−03 | **×943** |

`FLOOR_REL` never binds on this ladder (the smallest level tolerance is 7.14e−07,
714× above it). It is registered anyway, as the stop for any future extension, and it
is **13.2× the worst value measured here**. **Stated openly: this tolerance falls 4×
per level while the measured max rises slowly, so two levels finer than `fine` the
floor would bind. That is the floor's purpose and it is not hidden.**

**Limb 2 — the `checkMesh` cross-check, with a tolerance that follows the measured
amplification law.** checkMesh's printed angle is retained as an independent check on
the mesher, at its own (much blunter) resolution:

    TOL_CM(level) [deg] = HALF_ANGLE_DEG × TOL_REL_WEDGE(level)
                        + K_CM × N_wedge_faces(level) × EPS_MACH / sin(a) × 180/pi
    K_CM = 1.0 (frozen)   EPS_MACH = 2.220446049250313e-16

| level | **TOL_CM (deg)** | measured deviation | occupancy | F23's occupancy |
|---|---|---|---|---|
| coarse | **2.874681e−06** | 2.766821e−07 | **0.096** | 0.28 |
| medium | **9.674350e−06** | 7.984975e−07 | **0.083** | 0.80 |
| fine | **3.824547e−05** | 2.720290e−06 | **0.071** | **2.72 (REFUSED)** |

**The design criterion is met: occupancy now FALLS with refinement where F23's rose.**
`K_CM = 1.0` is the textbook worst-case sequential-summation bound and sits 8.6×/12.0×/
14.0× above what was measured. **Limb 2 is ~1,340× blunter than limb 1 (it can only
resolve a mis-build of ≈0.1 % at fine, against 7.1e−07 for limb 1); it is registered as
a cross-check on the mesher, NOT as the sharp guard, and this is stated now so no
results record can later present it as the guard that did the work.**

**Limb 3 — the MESH_STANDARD §3 gates, unchanged from F23, byte-for-byte:** `Mesh OK`
present; max non-orthogonality ≤ 70°; max skewness ≤ 4; aspect ratio recorded at the
1000 advisory; built cell count == NR·NX; both wedge patches present and reported.
All recorded to `<level>/MESH_LINE.txt`, now also carrying limb 1's max relative
deviation and limb 2's occupancy.

### 4.4 THE NEGATIVE CONTROL, DRIVEN IN THIS INVOCATION — the guard is not a rubber stamp

Rule 3, both directions, through the **real reader from disk**, on **real F23 meshes**:
a mis-built wedge is planted by scaling every point's z by (1 + p) — which is exactly a
wedge built at half angle a(1+p) — into a **copy** written to the scratchpad and **read
back through the same reader**. Nothing was written into any run root.

| level | artifact | limb 1 | vs TOL_REL | limb 2 | vs TOL_CM | required | got |
|---|---|---|---|---|---|---|---|
| coarse | **unplanted, real** | 1.895413e−10 | 0.000× | 2.766821e−07 | 0.096× | **accept** | accept |
| coarse | plant p = 3×TOL_REL | 3.645948e−05 | **3.000×** | 1.544453e−06 | 0.537× | **limb 1 REFUSE** | **REFUSE** |
| coarse | plant p = 0.10 | 9.999996e−02 | 8,228× | 3.999894e−03 | 1,391× | **both REFUSE** | **both REFUSE** |
| **fine** | **unplanted, real** | 7.569059e−10 | 0.001× | 2.720290e−06 | 0.071× | **accept** | accept |
| **fine** | plant p = 3×TOL_REL | 2.143442e−06 | **3.001×** | 2.721183e−06 | 0.071× | **limb 1 REFUSE** | **REFUSE** |
| **fine** | plant p = 0.10 | 9.999996e−02 | 140,013× | 3.996375e−03 | 104× | **both REFUSE** | **both REFUSE** |

This satisfies the supervisor's mandatory controls **(a)** a planted mis-built wedge
the tolerance must refuse — at both coarse **and fine** — and **(b)** a planted correct
wedge at **fine** resolution it must not refuse. The sharp plant is deliberately sized
at 3× the tolerance: it is refused by limb 1 and **accepted by limb 2**, which is the
registered expectation and is the evidence that limb 1, not limb 2, is doing the work.

The plant's round trip through the file is itself measured: max |Δz| = 4.94e−16
(writePrecision 12), ten orders below the smallest plant. **A guard whose plant cannot
survive its own file format is not a guard, and this one's does.**

**Production form of the control, registered as items A4–A7 of §9.0 and run UNDER THIS
SHA, before any ladder level:** the same two directions driven through **`blockMesh`
itself** — a scratch build with
`__HALF_ANGLE_DEG__` perturbed by 3×TOL_REL must be refused, an unperturbed scratch
build must not — so the control exercises the real builder, not only the real reader.
The points-level plant above is the reader control and is not a substitute for it.

---

## 5. THE ITERATIVE FLOOR — A SECOND FATAL DEFECT, MEASURED HERE (L-346 **and** L-396)

### 5.1 The measurement

F23's completed coarse and medium levels were read at all 40 checkpoints
(`processor*/{100..4000}/U`, volume-weighted with each rank's own `processor*/0/V`) and
the bulk velocity converted to `f·Re = 2 D² G/(ν Ubar)`. **F23's own §12 records that
station and all-cell bulk velocity agreed to 1e−15 on its instrument run, so this is a
faithful proxy for gate G-F23-2.** Zero solver core-minutes; read-only.

| level | Ubar at iteration 4000 | f·Re at 4000 | exact | Ux initial residual at 4000 | registered floor |
|---|---|---|---|---|---|
| coarse | 0.963749067 | **66.407** | 64 | 2.540863e−05 | ≤ **1e−08** |
| medium | 0.579085973 | **110.519** | 64 | 1.494733e−04 | ≤ **1e−08** |

F23's registered rule-5 limb 1 required `Ux` initial residual ≤ 1e−8 at **every**
iteration of the census window 2801–4000. The worst value **inside that window** is
**7.325343e−05 at coarse (7,300× the floor) and 2.648540e−04 at medium (26,000×)**.
Driving F23's own Class C plateau parameters (window 12 checkpoints, trend 2e−4,
stationarity 1e−4, variance ratio [0.2, 5]) over the f·Re series:

| level | relative drift across window | tol | stationarity | tol | variance ratio | verdict |
|---|---|---|---|---|---|---|
| coarse | **5.598771e−02** | 2e−04 | 3.037498e−02 | 1e−04 | 0.332 | **NOT_PLATEAUED** |
| medium | **2.055168e−01** | 2e−04 | 1.117737e−01 | 1e−04 | 0.494 | **NOT_PLATEAUED** |

**F23 was 280× and 1,030× outside its own plateau tolerance at the two levels it
completed.** The flow was still accelerating from rest at the last checkpoint.

### 5.2 What it says — the mechanism, measured

The outer SIMPLE loop, not the linear solver, is the bottleneck. GAMG reports
`No Iterations 1` for `Ux` at every iteration: the inner solve reaches its `relTol 1e-3`
in one V-cycle and is doing its job. The **relaxed Picard** iteration is what crawls.
Measured per-iteration convergence factors of the bulk-velocity error 1 − Ubar over
iterations 3600→4000:

| level | 1 − (per-iteration factor) | ratio to coarse |
|---|---|---|
| coarse (NR = 64) | 8.190e−04 | — |
| medium (NR = 128) | 2.065e−04 | **3.96 ≈ 4 = h⁻²** |

Implicit under-relaxation at α = 0.7 adds `((1−α)/α)·diag(A_P) = 0.4286·diag(A_P)` to
the matrix. For the smoothest mode of a diffusion operator that added diagonal dominates
the eigenvalue by O((h/R)²), so the outer loop converges at `1 − O((h/R)²/β)` **no
matter how well GAMG solves the inner system**, and the iteration count scales as h⁻².
A fourth, independent confirmation is F23's own §4 instrument run: a 16 × 64 scratch
wedge, same solver, same α, reached `Ux` 2.3e−16 inside 4000 iterations — at NR = 16 the
predicted rate is 16× coarse's, i.e. ≈1,600 iterations, and it converged. **F23's floor
was tuned on a mesh 128× smaller than its own fine level. That is L-346's exact shape.**

**Honest caveat on one number.** Read from the residual limb instead of the
bulk-velocity limb, medium's factor is 4.309e−04, not 2.065e−04 — a 2.1× disagreement,
because at iteration 4000 medium's residual is still shedding a faster-decaying
component while the bulk error is already on the slow mode. **The bulk-velocity limb is
the graded quantity's own error and is the one quoted. The disagreement is recorded
rather than averaged away, and it means the extrapolations below are OPTIMISTIC.**

Extrapolated iterations needed to converge `f·Re` at α = 0.7, from the bulk limb:
**coarse ≈ 25,000; medium ≈ 100,000; fine ≈ 395,000.** At the rates measured in §9.1,
F23's fine level alone would have cost **≈ 80,700 core-minutes**. **F23's ladder was
not runnable at 4,000 iterations, and was not runnable at any cap the lab would grant.
The wedge guard is the defect that stopped it; the iterative floor is the defect that
would have made it worthless.**

### 5.3 THE REGISTERED SOLVE AND THE REGISTERED COUNTS

**`case/system/fvSolution` — changed. The one substantive dictionary change:**

    SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; pRefCell 0; pRefValue 0; }
    relaxationFactors { fields { p 1.0; } equations { U 1.0; } }
    solvers { U { solver GAMG; smoother GaussSeidel; tolerance 1e-14; relTol 1e-4; }
              p { solver GAMG; smoother GaussSeidel; tolerance 1e-12; relTol 1e-4; } }

`consistent yes` is **SIMPLEC**, whose whole purpose is to allow α_U → 1; at α_U = 1 the
added diagonal β vanishes and the outer loop converges at the inner solve's own rate
(relTol 1e−4 per outer iteration), i.e. in a handful of iterations rather than 10⁵.

**What this lane did NOT verify, stated plainly.** This lane launched nothing, so the
SIMPLEC/α = 1 convergence is **predicted, not measured**. It is not risk-free: the
pressure field is small but **not identically zero** — measured max|p| = 2.170126e−06
(coarse) and 9.029890e−06 (medium) at iteration 4000, three to four orders below the
velocity scale and itself still moving — so this lane does **not** claim the
pressure–velocity coupling is inert, and does not rest α_U = 1 on that claim.

So the arms below are **registered here and RUN UNDER THIS SHA** — see §5.5 for the
frozen branch rule and §9.0 for their cost and their cap.

**`case/system/controlDict` — changed, in exactly two fields:**

    endTime         400      (was 4000)
    writeInterval   10       (was 100)

**The checkpoint COUNT is 40, byte-for-byte F23's, and the Class C window stays 12
checkpoints** — F17c §8.4's warning is that changing `writeInterval` silently changes a
criterion defined in checkpoints, so the count and the window are held fixed and the
**span** is registered explicitly: **12 checkpoints = 120 iterations** (F23: 1,200).
`purgeWrite 0`, `writeFormat ascii`, `writePrecision 12`, `timePrecision 6`,
`runTimeModifiable false`, **no `residualControl`** — all unchanged; the run goes to
`endTime` and the plateau gate decides.

### 5.5 THE PRE-LADDER ARMS AND THE FROZEN BRANCH RULE — INSIDE the freeze, not ahead of it

**The sequencing defect this section repairs, named.** An earlier draft made the smoke
arm a **pre-freeze** condition and wrote *"the registration does not freeze until the arm
and the counts agree."* That puts compute before the pre-registration commit, and **a
smoke arm is a solver start.** Rule 2 requires the gate, threshold, cap and label
committed **before** the solver starts, and rule 12 requires every run costed in its
pre-registration — that arm was costed nowhere. **The defect was found by the supervisor
reading this document under `SUPERVISION_CHARTER.md` §3 check 4, and it is recorded here
rather than silently corrected.** The arms now run **under the sha**, with their own
cost, their own cap and a **frozen** branch rule.

**Why running them under the sha is legitimate, and this is the load-bearing paragraph.**
The arms' result may move **ONLY** a registered **COUNT** — `N_ITER`, the derived
`writeInterval = N_ITER/40`, and the core-minute, cap and wall-allowance figures that
§9.3's **frozen arithmetic** computes from it. It may move **NO gate, NO band, NO
threshold, NO tolerance, NO label, NO verdict word, NO level, NO rank count and NO
plateau tolerance.** §4.3's `TOL_REL_WEDGE` and `TOL_CM`, §5.4's `PLATEAU_TOL`, §6's
bands, predicted values and predicted verdict, and §7's criteria are fixed at this sha
and are **not functions of any arm's outcome**. **Because no gate can follow the answer,
no arm can be used to choose a gate that fits it — which is the entire evidentiary
content of the freeze.** And the count the arm does move is an iteration budget, which is
the one quantity the ladder already polices from the other side: an `N_ITER` chosen too
small is **caught by §5.4's plateau gate**, not hidden by it.

**ARM-P (primary), registered.** Coarse resolution (131,072 cells), 4 ranks, the real
chain `build_f23b.py` → `decomposePar` → `mpirun -np 4 simpleFoam -parallel`, under the
§5.3 dictionary: `consistent yes`, α_U = 1.0, p 1.0.
**Acceptance:** relative bulk-velocity error |1 − Ubar| ≤ **1e−10** by iteration
**n ≤ 80**, with `Ux` initial residual ≤ **1e−12** there, rc 0, no divergence.

**ARM-F (fallback), registered.** Identical in every respect except α_U = **0.9**.
Fires **only** if ARM-P fails its acceptance. Same acceptance test.

**THE BRANCH RULE — frozen at this sha, and it is the whole of it:**

1. **ARM-P accepts at n ≤ 80** → `N_ITER = 400` stands; §9.3 stands unchanged.
2. **ARM-P accepts at 80 < n ≤ 400** → `N_ITER := max(400, 40 × ceil(5n/40))`, so
   `writeInterval = N_ITER/40` stays an integer, the checkpoint count stays **40** and
   the Class C window stays **12 checkpoints**. §9.3's estimate, cap and every wall
   allowance are then recomputed by **§9.3's own frozen arithmetic** with the new
   `N_ITER`. **The formula is frozen; only its input count moves.**
3. **ARM-P does not accept by iteration 400, or diverges** → **ARM-F fires**, and rules
   1–2 apply to it unchanged.
4. **ARM-F also fails** → **HALT.** The rung is **`BLOCKED`**, escalated to the cfd
   supervisor **with BOTH arms' measured records**. The outcome of that escalation is a
   **NEW registration under a NEW sha, never a third arm under this one.** A third
   setting chosen after watching two fail is a parameter hunt, and a parameter hunt is
   not a registration.
5. **BOTH ARMS ARE REPORTED, INCLUDING A FAILING ONE.** Sanaa's §3 anti-gaming clause
   (`docs/standards/NONCONVERGENCE_STANDARD.md`; her directive of 2026-08-27T16:54Z) is
   explicit that every arm run is reported, and that **a single reported arm out of
   several run is the signature the clause exists to catch. A smoke arm is an arm.**
   The results record carries ARM-P and ARM-F both, whether or not ARM-F fired and
   whether or not either passed.

**What the arms do NOT decide.** They do not decide whether F23b runs, whether any gate
is met, or what any verdict word is. They decide one integer.

### 5.4 THE PLATEAU TOLERANCE, DERIVED AND CHECKED AT **EVERY** LEVEL (the L-396 half)

L-346 says derive the floor from the predicted **fine**-level error. **F17c did exactly
that and still graded `NOT A RESULT`, because the level that missed its plateau limb was
MEDIUM** — `F17c_KV40_FLOOR_RESULTS.md:233` records medium `NOT_PLATEAUED_TREND` at
drift 3.7548e−04 against 2.0e−04, **1.877× tolerance**, on a level registered with a
claimed ×1.51 iteration margin (`:357–359`); and the measured drift was **non-monotone
across the ladder** — 0.009× / 1.877× / 0.199× of tolerance (`:364`). **A margin
computed at one level is not evidence about another.** So F23b registers a plateau gate
on **every graded quantity at every level**, with a tolerance derived from **that
level's own** predicted error:

    PLATEAU_TOL(gate, level) = min( 2.0e-04 ,  0.1 × |E_pred(gate, level)| / scale )

| level | **G-F23b-1 (E2n)** | **G-F23b-2 (f·Re)** | L-346 bound on f·Re | which binds |
|---|---|---|---|---|
| coarse | **2.000000e−04** | **1.215313e−05** | 1.215313e−05 | L-346 |
| medium | **2.000000e−04** | **3.003125e−06** | 3.003125e−06 | L-346 |
| fine | **2.000000e−04** | **7.142188e−07** | 7.142188e−07 | L-346 |

For `E2n` the L-346 bound is 0.1 relative (the gate quantity **is** an error norm, so
"an order below the predicted error" is "10 % relative movement"), which is looser than
F23's registered 2e−04; **the minimum is taken, so this can only tighten F23's value,
never loosen it.** For `f·Re` the L-346 bound is 164× to 280× tighter than F23's and
binds at every level. Stationarity tolerance = PLATEAU_TOL/2; variance ratio [0.2, 5],
unchanged.

**The L-396 mirror, applied to the plateau detector.** A converged F23b series will sit
at the machine floor, where a variance-ratio test on two all-but-identical half-windows
is meaningless and can fire on nothing. So: **if both half-window variances are below
(16 ε × scale)², the variance element is declared satisfied and the reason is
PRINTED beside the verdict**, never silently. That clause is driven **both ways** in the
controls (§8, C-7) — a detector that has never been shown able to stay silent is a
constant, not a reader.

---

## 6. THE GATES, THEIR BANDS, AND THE REGISTERED PREDICTION

**Kept BYTE-FOR-BYTE from F23 §3 and §4 — every predicted value, every band, the
declared `BAND_FACTOR = 3`, and the discrete model that produced them.** They are
properties of the **converged discrete** problem on the mesh's own geometry
(`exact_f23.discrete()` solves the tridiagonal system directly) and are therefore
**independent of the relaxation factor, the linear-solver tolerance and the iteration
count**. Nothing in §4 or §5 touches them. This is the single strongest reason F23b is
a re-registration rather than a new case.

| level | E2n predicted | f·Re predicted | f·Re error |
|---|---|---|---|
| coarse | 1.149980e−04 | 63.992221588 | −7.778e−03 |
| medium | 2.869164e−05 | 63.998078262 | −1.922e−03 |
| fine | 7.128682e−06 | 63.999542924 | −4.571e−04 |

**G-F23b-1 — E2 of the NORMALISED axial profile at the station.** Definition
byte-for-byte F23's G-F23-1 (the x-column of cells nearest x = L/2 + dx/2, count must
equal NR or the grader refuses; mesh's own `0/C` radii and `0/V` volumes; normalised by
the READ bulk velocity). Prediction at fine **7.128682e−06**.
**Band = [2.376227e−06, 2.138605e−05]** — byte-for-byte F23's.

**G-F23b-2 — f·Re from the imposed G and the READ bulk velocity.** `f·Re_h =
2 D² G/(ν Ubar_h)`. Exact 64. Predicted fine error −4.571e−04.
**Band = [63.998628773, 64.001371227]** — byte-for-byte F23's.

**THE REGISTERED PREDICTION — stated before compute, falsifiable, and it changes no
gate if it is wrong.**

| what is predicted | value |
|---|---|
| per-level E2n | 1.149980e−04 / 2.869164e−05 / 7.128682e−06 |
| per-level f·Re | 63.992221588 / 63.998078262 / 63.999542924 |
| triple state, both gates | **CONVERGING** |
| observed order, E2n | p ∈ [1.85, 2.20] (model 2.003 / 2.009) |
| observed order, f·Re | p ∈ [1.85, 2.20] (model 2.017 / 2.072) |
| fine value inside its band | **yes, both gates** |
| plateau at every level, both gates | **PASSED** at the §5.4 tolerances |
| wedge guard at every level | **ACCEPT**, limb 1 occupancy ≤ 1.1e−03 |
| **verdict** | **PASS × 2** |
| ladder spend | 202.4 core-min against a 293.0 cap |

**A wrong prediction changes no gate, no threshold, no band and no label. It is
recorded in the results file beside what happened, and it is not hidden.**

---

## 7. CRITERIA — how the verdict is reached, in rule 5's order

- **Verdict vocabulary:** `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
  `BLOCKED` / `PENDING`, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node, AST-censused at
  freeze; the text matcher driven both ways.
- **Rule 5 limb (1), per level:** (a) `Ux` initial residual ≤ **1e−12** at every
  iteration of the census window (the last 120 iterations); (b) the §5.4 **plateau gate
  on the graded quantity itself, at that level's own tolerance**; (c) field-level
  transverse check max|Uy|, max|Uz| ≤ 1e−10 × U_MAX at endTime. **Any level failing any
  of (a)(b)(c) → the ROW is `NOT A RESULT`.** The normalised initial residuals of Uy,
  Uz and p are **PRINTED beside the verdict and EXCLUDED from the gate** (N-AV8:
  vanishing channels normalised by a vanishing scale), exclusion declared here, at the
  freeze, and printed anyway.
- **Rule 5 limb (2):** triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` →
  `NOT A RESULT`, with value, both triples and both orders printed beside it.
- **Rule 5 limb (3):** `CONVERGING` → `PASS` inside the pre-registered band, else
  `GATE FAIL`; **GCI at Fs = 1.25**, and never quoted when the three values are not
  monotone. The gate may only turn a PASS or GATE FAIL **into** `NOT A RESULT`.
- **`G-WEDGE` (§4.3) is a BUILD gate, not a grading gate.** A level whose mesh fails any
  limb is never solved; the level is `NOT A RESULT` and the ladder is `NOT A RESULT`.
  **The builder refuses; it does not repair, and it deletes nothing.**
- **Completion (rule 4), all clauses or none:** `RC.txt` = 0; an `End` line; last time
  == `endTime` = 400; `Time` line count == 400; `U` and `p` at `400/` in **every one of
  the 4 processor directories**; **every such field NEWER than the serial `0/U`**, which
  the builder writes last (the age guard). A guard refuses a level directory already
  holding `0/`, a numeric time directory or `processor*`.
- **L-342 field classes.** `PHYSICS_CRITICAL`: log `End` / `Time` count, `RC.txt`,
  processor endTime fields + age guard, `processor*/0/C` and `0/V`, checkpoint `U`
  files, `Ux` residuals, transverse field maxima, `constant/polyMesh` (G-WEDGE's input).
  `INFRASTRUCTURE`: `ClockTime`, box probes, `MESH_LINE.txt`, `CAP_ALLOWANCE.txt`,
  utility logs, runner `STATUS` / `launcher.queue.out` rows, calibration figures.
  Verdicts key on the first only; a missing INFRASTRUCTURE field prints
  `BOOKKEEPING DEFECT` and refuses the **cost claim only** — bookkeeping never voids
  physics. Driven both ways at selftest.
- **`assert` census: ZERO** across every case file; a planted assert must be seen.
  **Hard `-O` refusal at entry** on every module (`python3 -O <mod>` → rc 2).
- **Success messages print INSIDE the passing branch.**
- **`set -u` dropped around the OpenFOAM bashrc source only** (L-339);
  `scripts/check_launcher_can_launch.py --worktree cases/F23b_HP_WEDGE/run_f23b.sh`
  → rc 0 required at freeze.
- **`--preflight` fires nothing** (no blockMesh, no build, no decomposePar) and must
  print: cap agrees launcher/grader, ν / G / ranks / endTime / writeInterval agree,
  `consistent yes` present, relaxation factors as registered, run root ABSENT.
- **Dictionaries cross-checked** at every grader entry and by the launcher.

---

## 8. CONTROLS — each with its exact assertion, each shown able to REFUSE

| id | control | exact assertion |
|---|---|---|
| **C-1** | **Mis-built wedge, sharp** (§4.4) | scratch `blockMesh` at `HALF_ANGLE_DEG × (1 + 3·TOL_REL_WEDGE)`, read through the real reader from disk → **limb 1 REFUSES**, ratio to tolerance ∈ [2.9, 3.1]. **Measured already at coarse (3.000×) and fine (3.001×) via the points-level plant.** |
| **C-2** | **Mis-built wedge, gross** | the same at ×1.10 → **limb 1 AND limb 2 both REFUSE**. Measured: 8,228× / 1,391× (coarse), 140,013× / 104× (fine). |
| **C-3** | **Correct wedge at FINE, must NOT refuse** | F23's real fine `constant/polyMesh`, unmodified, read-only → **ACCEPT**, limb 1 = 7.569059e−10 (0.001× tol), limb 2 = 2.720290e−06 (0.071× tol). **Measured.** |
| **C-4** | **Plant round-trip** | the plant's max \|Δz\| through the file format is **printed** and asserted ≤ 1e−14 absolute; **measured 4.94e−16**. A plant that cannot survive its own file format is not a plant. |
| **C-5** | **G-F23b-1 both ways** through `demonstrate()` | exact + 1× model error → **7.128682e−06, INSIDE** [2.376e−06, 2.139e−05]; exact + 40× → **1.916700e−04, OUTSIDE**. Real reader, pinned write format. |
| **C-6** | **G-F23b-2 both ways** through `demonstrate()` | exact + 1× → **63.999542924, INSIDE** [63.998628773, 64.001371227]; u × 1.001 → **63.935607317, OUTSIDE**. |
| **C-7** | **Plateau detector, both ways, at EVERY level** | **must FIRE:** F23's own retained `coarse` and `medium` processor checkpoints — measured drift 5.598771e−02 and 2.055168e−01 against 1.215313e−05 and 3.003125e−06, i.e. **4,606×** and **68,435×** tolerance. **must STAY SILENT:** a machine-floor series at each level's scale → PLATEAUED, with the §5.4 machine-floor variance clause printed. Read-only on F23's run root; nothing written there. **This is L-396's mirror on a detector, and the must-fire artifacts are real solver output, not synthetic.** |
| **C-8** | **Planted-zero on the field readers (rule 3)** | δ = 1.234e−03 on `Ux`, planted into copies of the real processor `U` files and read back with the real parser → E2n moves to its in-memory prediction (1e−13) and f·Re to `2D²G/(ν(Ubar_h+δ))` (1e−10). **A plant that does not move a reading REFUSES (exit 2).** |
| **C-9** | **Completion, driven both ways** | infra deleted → completion unchanged, cost claim refused. `RC.txt` corrupted / `End` deleted / one in-window `Ux` above tolerance / a transverse max above floor / one rank's `400/U` missing / one `400/U` older than `0/U` → **the level flips to NOT A RESULT**, each independently. |
| **C-10** | **`fatal` / alarm channel (L-396)** | must flag a log carrying a real `FOAM FATAL`; must **NOT** flag a clean log carrying OpenFOAM's `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).` banner, which is present at line 18 of **every** log this case produces (verified in `verification/runs/F23_HP_WEDGE_runs/coarse/log.checkMesh`). |
| **C-11** | **Cap halt, driven through the launcher's own bytes** | the parse-and-branch block extracted verbatim and run with an injected projector output: `HALT=1` → **rc 3**, `HALT=0` → rc 0 falling through. No box probed. |
| **C-12** | **In-level `timeout` kill** | a scratch level killed by its `CAP_ALLOWANCE` leaves an incomplete level that rule 4 **refuses**, graded `NOT A RESULT` — the correct outcome of an overrun, not a defect. |
| **C-13** | **Rule-5 order census** | exactly one `grade_ladder` call node (AST); the text matcher driven both ways. |
| **C-14** | **`-O` refusal / zero-assert census** | every module: `python3 -O` → rc 2; `ast.Assert` count 0; a planted assert is seen by the census. |

---

## 9. COST — COSTED BEFORE THE RUN, RULE 12

### 9.0 THE PRE-LADDER ARM BUDGET — costed and capped, BESIDE the ladder cap

Every arm of §5.5 and every production control build of §4.4 runs under this sha, so
each is costed here. Basis: §9.1's measured coarse rate × the §9.2 stiffness factor
(8.60596 core-µs/cell-iteration) for the solves; **measured serial wall times from F23's
own build logs** for the mesh builds — coarse `box_before.txt` 07:03:58 → `log.build`
07:04:04 = **6 wall s at 1 rank**; fine 07:53:21 → 07:54:26 = **65 wall s at 1 rank**
(that build stopped at the wedge refusal, so a completed fine build carries the
`writeCellCentres`/`writeCellVolumes` steps on top and is registered at 2.0 core-min).

| id | item | ranks | expected | **worst registered** |
|---|---|---|---|---|
| A1 | ARM-P mesh build, coarse (blockMesh + checkMesh + postProcess) | 1 | 0.100 | 0.100 |
| A2 | **ARM-P solve**, coarse — expected: accepts at n ≤ 80; worst: runs 400 out | 4 | 1.504 | **7.520** |
| A3 | **ARM-F solve**, coarse — expected: does not fire | 4 | 0.000 | **7.520** |
| A4 | §4.4 control build, coarse, UNPERTURBED (must accept) | 1 | 0.100 | 0.100 |
| A5 | §4.4 control build, coarse, PERTURBED at 3×TOL_REL (must refuse) | 1 | 0.100 | 0.100 |
| A6 | §4.4 control build, **fine**, UNPERTURBED (must accept) | 1 | 2.000 | 2.000 |
| A7 | §4.4 control build, **fine**, PERTURBED at 3×TOL_REL (must refuse) | 1 | 2.000 | 2.000 |
| | **TOTAL** | | **5.804** | **19.340** |

**REGISTERED PRE-LADDER CAP: 20.0 core-minutes** = **×1.034 the worst registered case**
(the ratio the 1.50 ceiling applies to, because the cap must cover the branch this
document registers as possible) and **×3.446 the expected path** (because the fallback
arm is registered and expected not to fire). **Both ratios are stated; neither is the
other in disguise.** Dollars **$0.0050 expected, $0.0171 at the cap — DERIVED, NOT
MEASURED**.

**IT SITS BESIDE THE 293.0, NOT INSIDE IT, AND THE LADDER CAP IS UNCHANGED.** Stated
plainly because the supervisor asked for it to be, and for two reasons that are not
presentational:

1. **§9.3's in-level wall allowances are derived from the REMAINING LADDER cap.** Folding
   a branch-dependent pre-ladder spend into 293.0 would make the fine level's `timeout`
   kill threshold a function of **whether ARM-F fired** — an earlier arm's outcome
   silently moving a later level's kill point. That is exactly the kind of coupling a
   frozen cap exists to prevent.
2. **`COMPUTE_BUDGET_CHARTER.md` §6** keeps separately-named spend separately named and
   never absorbed.

**TOTAL RUNG CAP = 293.0 (ladder) + 20.0 (pre-ladder) = 313.0 core-minutes**,
**$0.2676 at the total cap — DERIVED, NOT MEASURED**. Total expected spend
**208.17 core-min, $0.1780**. Under the $25 pre-authorisation; this paragraph and §9.3's
are the per-item read a blanket does not supply (rule 9).

**ALL THREE CAPS ARE ASSERTED BY THE LAUNCHER BEFORE ANY COMPUTE, AND PRINTED BY
`--preflight`** — a gap in the previous draft, which asserted the ladder cap only:

    run_f23b.sh::PRELADDER_CAP_CORE_MIN == grade_f23b.py::PRELADDER_CAP_CORE_MIN == 20.0
    run_f23b.sh::CAP_CORE_MIN           == grade_f23b.py::CAP_CORE_MIN           == CAP(N_ITER)
    run_f23b.sh::TOTAL_RUNG_CAP_CORE_MIN == PRELADDER_CAP + CAP  == 313.0 at N_ITER = 400

The launcher **refuses to start** if any of the three disagrees across launcher and
grader, or if the total is not the sum of its two parts. **The two caps are enforced
against SEPARATE running totals** — pre-ladder spend never draws down the ladder cap and
never moves a `CAP_ALLOWANCE`, which is the whole reason they are registered beside each
other rather than as one number. **The total is asserted so that nothing is spent outside
a cap; it is not a third budget anything may draw on.**

**Enforced the same way as §9.3, inside each arm.** The remaining pre-ladder cap,
converted to wall seconds at the arm's rank count, is handed to `timeout` and written to
`<arm>/ARM_ALLOWANCE.txt` **before the solver starts**:

| arm | remaining pre-ladder cap | **wall allowance** | projected wall if it runs out | headroom |
|---|---|---|---|---|
| ARM-P | 19.900 | 298 s | 112.8 s | ×2.642 |
| ARM-F | 12.380 | 185 s | 112.8 s | ×1.640 |

A kill leaves an arm that did not reach its acceptance, which branch rule 3 or 4 handles
exactly as a failure — **an overrun stops the run and does not get a new budget**, and
the pre-ladder cap is never raised.

### 9.1 The rate basis — MEASURED ON THESE EXACT MESHES, ON THIS BOX

From F23's own completed logs, `ClockTime × ranks ÷ 60`, 4 ranks, 4,000 iterations:

| level | cells | ClockTime (s) | core-min | cell-iterations | **core-µs / cell-iteration** |
|---|---|---|---|---|---|
| coarse | 131,072 | 564 | **37.600** | 524,288,000 | **4.30298** |
| medium | 524,288 | 2,357 | **157.133** | 2,097,152,000 | **4.49564** |

Two-level actual **194.73 core-min**. F23 registered 9.7 / 65.7 / 75.4 for the same
work — **×3.88, ×2.39, ×2.58**. Both readings above are from
`verification/runs/F23_HP_WEDGE_runs/<level>/log.simpleFoam`, same meshes, same solver,
same box, same rank count. **This is a base-rate measurement, not a transfer.**

**A correction to the brief this lane owes upward.** The brief projects the measured
over-run onto F23's registered fine estimate (444.0 × 2.58) and lands near 1,265
core-min, above F23's 1,100 cap. **That double-counts.** The over-run *is* the rate
misprediction; the registered fine estimate already contains the wrong rate, so the
ratio must not be applied to it again. Built from the measured rate with the frozen
ratio below, F23's fine level at 4,000 iterations is **817 core-min** and its ladder
**1,012 core-min** — **under** its 1,100 cap, though only by 8 %. **The cap was not
F23's binding problem. §5 was.** The brief's conclusion — that a tolerance fix alone
buys a run that dies — is nevertheless correct, and for a stronger reason: at 4,000
iterations that ladder does not converge at any level.

### 9.2 The growth basis — a FROZEN PER-LEVEL RATIO, and it is an EXTRAPOLATION

F17c §8.2's finding is that base rates are right to 7–10 % and imported growth
exponents are wrong by +110 to +137 %, and that this box's measured rate is **not
monotone** in problem size. F17c therefore registered frozen per-level ratios and its
fine projection came in **0.18 % accurate on the level carrying 94.9 % of the spend**.
F23b follows that method and registers **no exponent**.

    RATE[coarse] = 4.30298 core-µs   MEASURED
    RATE[medium] = 4.49564 core-µs   MEASURED       (drift medium/coarse = 1.044776)
    RATE[fine]   = RATE[medium] × D_fine,  D_fine = 1.30   FROZEN, EXTRAPOLATED
    STIFFNESS    S = 2.0                                    FROZEN, EXTRAPOLATED

**`D_fine = 1.30` is NOT a measurement and is not dressed as one.** The one measured
drift on this ladder is 1.044776; 1.30 is that rounded up with a 24 % margin, on three
stated grounds: (i) **one point is not a law** — F23's own Amendment 1 says exactly this
about `CONT_MAX`; (ii) the 2.1 M-cell working set straddles this box's L3 (F17c §8.2's
own reading of the AMD EPYC 9R14's 64 MiB in 2 instances), where F17c measured the rate
turning **non-monotone**; (iii) the box is shared. **At the measured drift the ladder
would be 170.28 core-min; the registered estimate is 202.37, i.e. 18.8 % above the
no-margin figure. Both are printed so the calibration row can attribute the gap.**

**`S = 2.0` is the solver-stiffness factor for §5.3's dictionary change** and is also an
extrapolation: the measured rates were taken under F23's `fvSolution`, where GAMG
reported `No Iterations 1` for `Ux`; SIMPLEC at α = 1 with `relTol 1e-4` will need more
V-cycles per outer iteration. `S = 2.0` covers up to two. **`S` is FROZEN at this sha
and no arm may move it** — §9.3's cap arithmetic admits exactly one movable input,
`N_ITER`, and §5.5 is the only rule that may move it. ARM-P's own measured
core-µs/cell-iteration **is reported** and lands in §9.5's calibration row as the first
real reading of `S` on this dictionary; **it is a calibration input for the successor,
not a cap adjustment for this rung.** If `S` proves to have been under-registered the
run is stopped by its cap, which is what a cap is for.

**Contention multiplier = 1.0**, on this rung's own reading: F23's two levels ran at
ClockTime/ExecutionTime = 564/559.51 = **1.0080** and 2357/2356.39 = **1.0003** on a
session-busy box. Contention on this exact work is bounded below 1 %. **This also
retires L-349 for this rung: the projector reads no clock, no `/proc` and no disk, takes
every input as an argument, and cannot refuse work because the box is full.**

### 9.3 THE ESTIMATE, THE CAP, AND HOW THE CAP IS ENFORCED

`N_ITER = 400`, 4 ranks at every level.

| level | cell-iterations | rate × S (core-µs) | core-s | **core-min** | wall s on 4 ranks |
|---|---|---|---|---|---|
| coarse | 52,428,800 | 8.60596 | 451.2 | **7.520** | 112.8 |
| medium | 209,715,200 | 8.99128 | 1,885.6 | **31.427** | 471.4 |
| fine | 838,860,800 | 11.68866 | 9,805.2 | **163.419** | 2,451.3 |
| **ladder** | 1,101,004,800 | — | **12,142.0** | **202.366** | **3,035.5** |

**REGISTERED ESTIMATE: 202.37 core-minutes** (= 3.373 core-h), all at 4 ranks.
**REGISTERED CAP: 293.0 core-minutes = ×1.4479 the estimate** (the lab's ceiling is
1.50; F17c used 1.4942). `grade_f23b.py::CAP_CORE_MIN == run_f23b.sh::CAP_CORE_MIN`,
asserted by the launcher **before any compute** and printed by `--preflight`.

**THE CAP IS FROZEN AS ARITHMETIC, NOT ONLY AS A NUMBER**, because §5.5's branch rule
may move `N_ITER`. Frozen at this sha:

    ESTIMATE(N_ITER) = SUM over levels of  cells x N_ITER x RATE[level] x S / 60e6     [core-min]
    CAP_RATIO        = 1.4479                                              FROZEN
    CAP(N_ITER)      = floor( CAP_RATIO x ESTIMATE(N_ITER) , 0.1 )         [core-min]
    ALLOW_S(level)   = floor( (CAP - SPENT_so_far) x 60 / RANKS )          [wall s]

At `N_ITER = 400` this returns **ESTIMATE 202.366 → CAP 293.0** and the allowances
tabulated below, which is how those numbers were obtained. `RATE[]`, `S`, `CAP_RATIO`,
`cells` and `RANKS` are all fixed at this sha; **`N_ITER` is the only input any arm can
move, and §5.5 is the only rule that may move it.** The cap is never raised by any other
route, and no arm's outcome may raise `CAP_RATIO`.

**Dollars: $0.1730 at the estimate, $0.2505 at the cap — DERIVED, NOT MEASURED**
($0.0513/core-h, c7a.4xlarge, owner-stated and reported-by-owner; **this box cannot read
its own billing**, `COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation, and
this paragraph is the per-item read a blanket does not supply (rule 9).
**`cost_basis: rates MEASURED on this case's own meshes; D_fine and S EXTRAPOLATED;
dollars derived, reported-by-owner, not measured.`**

**THE CAP IS ENFORCED INSIDE A LEVEL, NOT ONLY BETWEEN LEVELS** — adopted from F17c
§8.3, and it is not optional here: **the fine level carries 80.75 % of the ladder's
spend.** A between-levels check would let it overrun by any factor before anything
noticed. The whole remaining cap, converted to wall seconds at that level's rank count,
is handed to `timeout` and written to `<level>/CAP_ALLOWANCE.txt` **before the solver
starts**:

| level | remaining cap at launch | **wall allowance** | projected wall | headroom |
|---|---|---|---|---|
| coarse | 293.000 | 4,395 s | 112.8 s | ×38.96 |
| medium | 285.480 | 4,282 s | 471.4 s | ×9.08 |
| fine | 254.053 | **3,810 s** | 2,451.3 s | **×1.554** |

A kill leaves an **incomplete** level, which rule 4 refuses and the grader reports as
`NOT A RESULT` — the correct outcome of an overrun, not a defect (C-12). **The cap is
never raised.** The pre-spend projection (exit 3 = HALT) still runs before every level,
and the post-level incremental check on **actual** `ClockTime × ranks ÷ 60` still HALTs
at exit 3 on a crossing.

### 9.4 WALL TIME, DISK AND MEMORY

- **Wall time ≈ 50.6 min at the estimate, 73.2 min at the cap**, at 4 ranks of 16. No
  level is projected over 3,600 wall s, so `COMPUTE_BUDGET_CHARTER` §6's stall
  heuristic is not expected to fire; the fine level's **3,810 s allowance** exceeds it,
  and if the allowance is ever reached that is a cap kill, not a stall.
- **Disk:** measured from F23's own retained levels — `coarse` **859 MB**, `medium`
  **3.4 GB** for 40 checkpoints each; scaling ×4 gives fine **≈ 13.6 GB**, ladder
  **≈ 17.9 GB**. Free space measured **217 GB** on `/` at 2026-08-28T16:41:37Z; the
  ladder needs **8.2 %** of it. Run output stays under
  `verification/runs/F23b_HP_WEDGE_runs/` and is **not committed**. **F23's own
  4.26 GB run root is retained untouched — it is C-7's must-fire control artifact and
  deleting it would delete the evidence.**
- **Memory floor 4.0 GB** (F23's figure, same solver, same meshes). Measured available
  at drafting: **25 GB** of 30 GB.
- **Grading wall time ≈ 3–5 min**, zero solver compute (40 checkpoints × 3 levels ×
  4 ranks). Registered so a long grade is not mistaken for a hang.

### 9.5 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion the results record **must** carry the estimate-versus-actual comparison:
actual in core-minutes from the logs' `ClockTime × ranks ÷ 60`, **gross and cleaned
stated separately**, waste named separately and **never absorbed into the ratio**, the
ratio actual/predicted, the gap attributed to contention / waste / misprediction, and
dollars **derived, not measured**. **`D_fine` and `S` are reported separately from the
base rate**, since they are the two extrapolated factors and the whole point of §9.2 is
to find out whether they were right. A row lands in **`docs/COST_CALIBRATION.md`**.
**A completion report without this comparison is incomplete.**

---

## 10. RULE-2 ABSENCE CONDITION AND ZERO SPEND, CHECKED IN THIS INVOCATION

**0.000 core-minutes have been spent on this rung.** No solver has run for F23b; no
`LAUNCHED` line exists; the diagnostics of §4 and §5 are read-only over F23's existing
artifacts and are charged to INFRASTRUCTURE, folded into no case ratio.

**The run root is ABSENT.** Checked at 2026-08-28T16:41Z:

| path | check | reading |
|---|---|---|
| `verification/runs/F23b_HP_WEDGE_runs` | `test -e` | **ABSENT** |
| `verification/runs/F23b_runs` | `test -e` | **ABSENT** |
| `cases/F23b_HP_WEDGE` | `test -e` | **ABSENT** |
| `verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md` | `test -e` before writing | ABSENT |

**PLANTED CONTROLS ON THE ABSENCE READER (rule 3 — a zero from a reader not shown able
to see a non-zero is not evidence):** the same `test -e` loop returned **PRESENT** for
`verification/runs/F23_HP_WEDGE_runs` and for `cases/F17c_kovasznay_floor`. The reader
can see a non-zero; its ABSENT readings are therefore evidence.

**Never run — the tracked-tree evidence.** `git ls-tree -r HEAD --name-only`: **16,844**
tracked paths; matches for `F23b`: **0**; **planted control: matches for
`F23_HP_WEDGE`: 20** — the same matcher on the same listing returns a non-zero, so the
zero is evidence. Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs`
(552 entries) **0**; `/home/ubuntu/closure-data` (25) **0**;
`/home/ubuntu/closure-challenge-benchmark` (7) **0**.

---

## 11. LAUNCH SHAPE — for the supervisor's check 4. **NOT an authorisation.**

**This section describes the shape of a launch. It is NOT an authorisation, it is not a
request for one, and this lane has launched nothing and enqueued nothing.** The freeze
commit and the enqueue are the supervisor's own acts under `SUPERVISION_CHARTER.md` §3
checks 1 and 4. **Enqueueing is not authorisation either.**

    bash /home/ubuntu/Certonomous/cases/F23b_HP_WEDGE/run_f23b.sh --prereg-commit=<this file's freeze sha>

**One launcher invocation carries the whole rung under the one sha**, in this fixed
order: **(1)** the §4.4 production wedge controls (A4–A7) — a refusal here stops the rung
before any solver runs; **(2)** **ARM-P**, and **ARM-F** only if §5.5's branch rule fires,
each wrapped in `timeout` at its `ARM_ALLOWANCE` (§9.0); **(3)** §5.5's branch rule sets
`N_ITER` and §9.3's frozen arithmetic recomputes the cap and the allowances; **(4)** the
three ladder levels, 4 ranks each (`mpirun -np 4 simpleFoam -parallel`), each solver
wrapped in `timeout` at its `CAP_ALLOWANCE` (§9.3). Grading is a **separate**
invocation:

    python3 /home/ubuntu/Certonomous/cases/F23b_HP_WEDGE/grade_f23b.py --prereg-commit=<sha>

reading the processor directories. The queue entry
`cases/F23b_HP_WEDGE/queue_entry_F23b_HP_WEDGE.json` is **HELD in the case directory**
until the supervisor's checks; **the supervisor, not this lane, moves it into
`verification/queue/cfd/`.**

**Order of operations — CORRECTED, and the correction is the point.** This registration
first → the supervisor reads it → the supervisor commissions the case code **against
it** → **the supervisor FREEZES** → and only then does **anything** start a solver:
the §4.4 controls, then ARM-P (and ARM-F if the branch rule fires), then the three ladder
levels, **all under the one sha**. An earlier draft of this document put the arms
**ahead** of the freeze; that was a rule-2 defect, it was caught by the supervisor's
check 4, and §5.5 records it rather than quietly repairing it. **No case code exists yet
and none was written by this lane, by instruction.**

---

## 12. FROZEN FILES AT THE FREEZE (to be completed by the supervisor)

    cases/F23b_HP_WEDGE/exact_f23b.py      <sha256 first8…last4>
    cases/F23b_HP_WEDGE/build_f23b.py      <sha256>     <- carries G-WEDGE (section 4.3)
    cases/F23b_HP_WEDGE/foam_io_f23b.py    <sha256>
    cases/F23b_HP_WEDGE/grade_f23b.py      <sha256>
    cases/F23b_HP_WEDGE/proj_f23b.py       <sha256>
    cases/F23b_HP_WEDGE/run_f23b.sh        <sha256>
    cases/F23b_HP_WEDGE/case/0/{p,U.template}
    cases/F23b_HP_WEDGE/case/constant/{transportProperties,turbulenceProperties,fvOptions}
    cases/F23b_HP_WEDGE/case/system/{blockMeshDict.template,controlDict,fvSchemes,fvSolution,decomposeParDict}
    verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md   (this file)

The grading path is fixed at the pre-registration commit; the frozen file that ran is
verified by hashing it against the committed blob
(`scripts/check_comparator_freeze.py`). **The pre-ladder arms of §5.5 and the controls of
§4.4 run against these same frozen bytes, under this same sha** — there is no arm outside
the freeze and no file that changes between an arm and a ladder level.

---

## 13. WHAT IS **NOT** REGISTERED HERE

- **F23's record is untouched.** It stands `NOT A RESULT` on its own record. This file
  does not re-grade it, does not amend it, and does not reach any of its frozen files.
  Its run root is retained read-only as C-7's control artifact.
- **No claim about F23's deviation beyond what §4.2 measured.** The mechanism is stated
  because it was measured on all three meshes and confirmed by a `math.fsum`
  substitution that changed nothing else. Candidate (ii) is excluded by measurement.
  **No claim is made about how any OTHER OpenFOAM version computes the wedge angle**;
  the readings are from `OPENFOAM=2606`, build `_481094f-20260618`, on this box.
- **No claim that SIMPLEC/α = 1 converges as §5.3 predicts.** That is registered as a
  prediction, with §5.5's ARM-P, its registered fallback ARM-F and a frozen branch rule —
  all **under this sha and costed in §9.0** — because this lane launched nothing and
  measured nothing about it.
- **No amendment to any standard, charter, N-AV9, or to `MESH_STANDARD.md`.** §4.2 is a
  finding about `checkMesh`'s printed wedge angle; whether it earns an `N-*` entry or a
  MESH_STANDARD clause is the verification team's call, not this lane's (§14, Q3).
- **No upstream defect report is filed, sent, drafted for sending, or prepared for
  anyone outside this box.** SUBMISSIONS ARE PARKED (rule 7).
- **No GPU arm and no `BLOCKED-GPU`.** CPU-only.
- **Nothing is sent, filed, uploaded, posted or submitted** (rule 7).

---

## 14. SUPERVISOR RULINGS, RECORDED — with the reasoning, not only the outcome

The four questions this lane raised were ruled by the cfd supervisor on 2026-08-28. The
**reasoning** is recorded here because a ruling recorded as an outcome alone cannot be
audited, and because two of these rulings turn on a distinction the next wedge rung will
need.

**R1 — TWO REPAIRS IN ONE RUNG (§4 and §5): ACCEPTED, both.** §2c's *"one change per
run"* binds arms whose purpose is **attributing an effect to a cause**. F23b is a
verification ladder measuring an order of accuracy, not a probe arm, and F23 produced no
graded value for a second change to confound. **The load-bearing reason is that these are
not two dials on one outcome and their failures write DIFFERENT ARTIFACTS.** The wedge
guard decides whether a level **BUILDS**: its failure leaves `log.build` carrying the
refusal and **no solver log at all**. The iterative floor decides whether a level
**PLATEAUS**: its failure leaves a complete solver log and a per-level plateau state.
**Attribution is therefore available from the artifacts without splitting the rung, which
is what §2c actually wants.** Splitting would cost a second ladder (≈202 core-min) and
buy nothing the artifacts do not already give.

**R2 — THE FALLBACK LADDER: UPHELD, and tightened in two ways**, both now registered in
§5.5's branch rule: **(a)** escalation on a double failure goes to the cfd supervisor
with **both** measured arms, and its outcome is a **new registration under a new sha,
never a third arm under this one**; **(b)** **both arms are reported, including a failing
one** — Sanaa's §3 anti-gaming clause is explicit that every arm run is reported, and
that a single reported arm out of several run is the signature the clause exists to
catch. **A smoke arm is an arm.**

**R3 — THE LAB-WIDE ARTIFACT: SPLIT, because the two halves have different owners.**
- **The CLAUSE is cfd's.** `docs/standards/MESH_STANDARD.md` is at v1.7, and an amendment
  there needs rule 6's dated-amendment form with its own `lines whose number changed above
  this section: 0` assertion, which is the supervisor's to land. **This lane therefore
  drafted the clause as a SEPARATE file and did NOT edit `MESH_STANDARD.md`:**
  `verification/campaign/CFD_MESH_STANDARD_WEDGE_ANGLE_CLAUSE_DRAFT_2026-08-28.md`.
- **The SWEEP is not cfd's to commission.** `VMFL005` is the ansys team's case and this
  reaches every wedge case in the lab. It is escalated to the chief with the mechanism
  named. **This lane checked no other case and makes no claim about any of them.**
- **Whether it also earns an `N-*` numerics entry** is left to the supervisor, who will
  check family ownership before claiming a number. This lane claims none.

**R4 — F23'S CALIBRATION ROW: dispatched elsewhere, and confirmed on both counts.** It is
F23's row, not F23b's; **F23's 194.73 core-min is NOT folded into F23b's ratio** and is
written as **WASTE, separately named**, with the registration defect attributed distinctly
from the rate misprediction (`COMPUTE_BUDGET_CHARTER.md` §6).

**R5 — THE CHECK-4 BLOCKER, found by the supervisor reading this document.** An earlier
draft made the smoke arm a **pre-freeze** condition — compute ahead of the
pre-registration commit (rule 2) — and costed it **nowhere** (rule 12). **§5.5, §9.0,
§9.3, §11 and §12 are the repair**, and the defect is recorded in §5.5 and §11 rather
than silently corrected. **Neither the ladder cap nor any gate, band, threshold, tolerance
or label moved: the ladder cap is 293.0 core-minutes exactly as before, and the
pre-ladder arms are capped separately at 20.0.**

---

## AMENDMENT 1 — 2026-08-28T17:08Z (PRE-COMPUTE) — Sanaa's control-birth directive: the `blockMesh`-path wedge control becomes **GATING**, and the arm-acceptance reader gets its own birth control

**Version 1.1. Lines whose number changed above this section: 0 — MEASURED, not recited.**
This block is appended at the foot. The 990 lines above it are byte-identical to their
state at the freeze commit `57d31dde`, asserted by taking the **md5 of the frozen blob**
(`git show 57d31dde:verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md`) and the
**md5 of the first 990 lines of this file after the append**, and requiring them equal.
The two digests are printed in the amendment record at the foot of this block. **The
assertion is measured because F23b's frozen sha is cited elsewhere and a line shift above
this point would break those citations.**

### A1.1 THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

Rule 2: *"Before first compute, amendments are legal and must state the condition and how
it was checked (name the run directory that does not exist)."*

**The run directory that does not exist is `verification/runs/F23b_HP_WEDGE_runs`.**
Checked by this lane at **2026-08-28T17:07:38Z**, `test -e` on the path: **ABSENT**. So
were `cases/F23b_HP_WEDGE` and `verification/runs/F23b_runs`. `find verification/runs
-maxdepth 1 -name 'F23b*'` returned **0** entries. The frozen commit `57d31dde` itself
tracks **0** paths under `cases/F23b/`. Out-of-tree run roots by name:
`/home/ubuntu/certonomous-runs` (553 entries) **0**, `/home/ubuntu/closure-data` (25)
**0**, `/home/ubuntu/closure-challenge-benchmark` (7) **0**.

**PLANTED CONTROLS ON BOTH READERS (rule 3).** The same `test -e` loop returned
**PRESENT** for `verification/runs/F23_HP_WEDGE_runs` and for this file's own path; the
same tracked-path matcher returned **20** for `F23_HP_WEDGE` at commit `57d31dde`. Both
readers can return a non-zero, so their zeros are evidence.

**0.000 core-minutes have been spent on this rung. No `LAUNCHED` line exists. F23b is
pre-compute and this amendment is legal.**

### A1.2 THE DIRECTIVE, VERBATIM

Sanaa, 2026-08-28T17:01Z
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`):

> A control defined in terms of the thing it controls is not a control. A planted control
> must travel the real production path — written by the real producer's code, read through
> the real reader — and prove the instrument sees a non-zero the same way reality would
> deliver one. A control that empties the tuple it tests, or writes a schema the producer
> never emits, tests nothing and certifies blindness. Companion rule canonized: rule 3's
> question — "was this reader ever shown able to see a non-zero through the real code
> path?" — is now the birth requirement for every reader/comparator: no instrument grades
> anything until that answer is yes, demonstrated.

### A1.3 WHY IT REACHES F23b — the gap was this lane's own disclosure

§4.4 registered the points-level plant as **driven** and the `blockMesh`-path plant as
*"required of the code lane"*, and this lane's report said in terms: *"The wedge control
is driven at the POINTS level; the production control through `blockMesh` with a
perturbed `__HALF_ANGLE_DEG__` is specified for the code lane, not driven by me."*

**A points-level plant is not written by the real producer's code.** In production the
wedge geometry is emitted by **`blockMesh`** from `blockMeshDict`, and `G-WEDGE` reads
what `blockMesh` produced. A perturbation injected downstream of `blockMesh` proves the
**reader** sees it; it does not prove the guard sees a perturbation **the way reality
would deliver one** — through a mis-set `__HALF_ANGLE_DEG__` flowing through the
builder's `math.cos`/`math.sin` into `__YW__`/`__ZW__` and then through `blockMesh`'s own
vertex arithmetic, which may round, snap or renormalise where a direct z-scale does not.

### A1.4 WHAT CHANGES — the `blockMesh`-path control becomes GATING (§4.4, §8)

**`G-WEDGE` MAY NOT GRADE ANYTHING UNTIL THE `blockMesh`-PATH CONTROL HAS BEEN DRIVEN,
BOTH DIRECTIONS, AND PASSED.** Items **A4–A7** of §9.0 — already registered and already
costed as real `blockMesh` builds — are hereby **gating controls**, not preparatory work.

**The refusal condition on the instrument.** The driven control writes a receipt
`cases/F23b_HP_WEDGE/GWEDGE_CONTROL_RECEIPT.txt` carrying, per level: the plant
magnitude, the limb-1 reading on the **perturbed** mesh, the limb-1 reading on the
**unperturbed** mesh, the `blockMesh` and `checkMesh` log paths, the UTC timestamp, and
the `--prereg-commit` sha it ran under. **`build_f23b.py` and `grade_f23b.py` both read
that receipt at entry and REFUSE (exit 2)** if it is absent, if any reading falls outside
the bands below, or if its recorded sha is not this document's freeze sha. **The guard
refuses rather than passing — an undriven control certifies blindness, and a guard that
cannot show it was born does not grade.**

**Both directions, through that same real path, stated numerically so a later reader can
check the control FIRED rather than take "control passed" on trust:**

| level | direction | `__HALF_ANGLE_DEG__` written into `blockMeshDict` | required limb-1 reading `max\|angle/a − 1\|` | required outcome |
|---|---|---|---|---|
| coarse | **MUST REFUSE** | `0.04 × (1 + 3×1.215313e−05)` = **0.0400014584** | **3.645948e−05**, accepted in `[2.9, 3.1] ×` `TOL_REL_WEDGE` | **REFUSE** |
| coarse | **MUST ACCEPT** | **0.04** exactly | **≤ 1.0e−08**; measured on the real mesh **1.895413e−10** | **ACCEPT** |
| fine | **MUST REFUSE** | `0.04 × (1 + 3×7.142188e−07)` = **0.0400000857** | **2.143442e−06**, accepted in `[2.9, 3.1] ×` `TOL_REL_WEDGE` | **REFUSE** |
| fine | **MUST ACCEPT** | **0.04** exactly | **≤ 1.0e−08**; measured on the real mesh **7.569059e−10** | **ACCEPT** |

**Separation margin between the two directions: ×1.924e+05 at coarse and ×2.832e+03 at
fine.** The must-accept limb is what stops this being a guard that refuses everything.

**Why the band is `[2.9, 3.1]×` and not "exactly 3.000×".** The points-level plant scales
z linearly and returned 3.000× (coarse) and 3.001× (fine). The `blockMesh`-path plant
enters through the trigonometry instead — `tan(a(1+p))/tan(a) = 1 + p + O(a²p)` — so the
two paths agree only to `O(a²)` of the plant. **The band is registered wide enough to
admit that difference and narrow enough that a control which silently failed to plant
cannot pass through it.** A reading below 2.9× is a plant that did not travel; a reading
above 3.1× is a plant that travelled differently than registered. Both refuse.

**The points-level control is RETAINED, and it is the WEAKER limb.** §4.4's table stands
unaltered. It is retained because two controls at different depths are worth more than
one, and it is **explicitly the weaker of the two**: it exercises the real reader on a
real mesh but **not the real producer**, so it can certify that the reader sees a
perturbation while remaining silent about whether the builder can deliver one.
**The `blockMesh`-path control of this amendment is the load-bearing one; the
points-level control is corroboration and may not substitute for it.**

### A1.5 THE ARM-ACCEPTANCE READER GETS THE SAME BIRTH REQUIREMENT (§5.5)

The reader that decides ARM-P/ARM-F — the `|1 − Ubar|` and `Ux` initial-residual readings
of §5.5's acceptance test — is an instrument that decides an outcome, so the directive
binds it too.

**The REJECT direction is ALREADY DEMONSTRATED, through the real production path, on real
artifacts.** This lane drove that reader over F23's own completed levels: real
`log.simpleFoam`, real `processor*/<time>/U`, real `processor*/0/V`, no synthesis
anywhere. It read `|1 − Ubar| = 3.6251e−02` (coarse) and `4.2091e−01` (medium) at
`endTime`, and `Ux` initial residual `2.540863e−05` and `1.494733e−04` — every one of them
orders above the acceptance thresholds of 1e−10 and 1e−12. **The reader sees a non-zero
the way reality delivers one, and rejects.** Recorded in §5.1.

**The ACCEPT direction is NOT yet demonstrated, and is hereby registered as gating —
item A0.** A reader shown only able to reject is L-396's constant in its other costume.

| id | item | ranks | registered cost |
|---|---|---|---|
| **A0** | **arm-acceptance reader birth control** — 16 × 64 wedge (1,024 cells), the real chain `build_f23b.py` → `decomposePar` → `mpirun -np 4 simpleFoam -parallel`, 4,000 iterations, **under F23's α_U = 0.7 dictionary, deliberately** | 4 (+1 for the build) | **0.350 core-min** (build 0.050 + solve 0.294 at §9.1's measured coarse rate, **no `S` factor**, because that rate was measured under exactly that dictionary) |

**Acceptance:** A0's real artifacts must drive the same reader to `|1 − Ubar| ≤ 1e−10` and
`Ux` initial residual `≤ 1e−12`, and the reader must **ACCEPT**. **If A0 does not produce
an accepting artifact the arm-acceptance reader is NOT BORN: ARM-P and ARM-F then REFUSE
rather than accept-or-reject, and the rung is `BLOCKED`.**

**Why A0 runs under the OLD dictionary, which is the point of it.** The accept side must
not depend on the very thing ARM-P is testing. Were A0 run under §5.3's SIMPLEC settings
and SIMPLEC failed, no accepting artifact could ever exist and the reader could never be
born — **a control defined in terms of the thing it controls, which is the first sentence
of the directive.** F23's §7 records that exact 16 × 64 configuration converging (`Ux`
2.3e−16 by iteration 4,000), so it is the one configuration on this box already known to
deliver a converged artifact. **The deviation is disclosed rather than buried: A0's
relaxation factor differs from the ladder's. The producer, the file schema and the reader
path are identical; only the relaxation differs, and it differs in the direction that
makes the control independent of what it certifies.**

### A1.6 COST — IT FITS INSIDE THE UNCHANGED PRE-LADDER CAP, AND HERE IS THE ARITHMETIC

**A4–A7 add nothing: they were already registered and already costed in §9.0** (0.200
core-min at coarse, 4.000 at fine). Making them gating changes their status, not their
price. **A0 is the only new spend.**

| | before this amendment | **after** |
|---|---|---|
| expected path | 5.804 | **6.154** |
| **worst registered case** | 19.340 | **19.690** |
| **REGISTERED PRE-LADDER CAP** | **20.0** | **20.0 — UNCHANGED** |
| cap ÷ worst registered | ×1.034 | **×1.016** |
| ladder cap / total rung cap | 293.0 / 313.0 | **293.0 / 313.0 — UNCHANGED** |

**19.690 ≤ 20.0, so the cap is not raised and is not approached.** The wall allowances of
§9.0's table are **outputs of §9.3's frozen formula**, and inserting a registered item
ahead of ARM-P changes that formula's `SPENT_so_far` input exactly as the formula says it
should — **this is the frozen arithmetic operating, not an alteration of it**:

| arm | remaining pre-ladder cap | wall allowance | projected wall | headroom |
|---|---|---|---|---|
| **A0** | 20.000 | 300 s | 4.4 s | ×68.1 |
| ARM-P | 19.550 | **293 s** (was 298) | 112.8 s | ×2.598 |
| ARM-F | 12.030 | **180 s** (was 185) | 112.8 s | ×1.596 |

Dollars **$0.0053 expected, $0.0171 at the unchanged cap — DERIVED, NOT MEASURED**.

### A1.7 WHAT THIS AMENDMENT DOES **NOT** TOUCH — enumerated, not summarised

**It makes one existing control gating and adds one control. It alters nothing else.**

- **No gate.** `G-F23b-1`, `G-F23b-2` and `G-WEDGE`'s three limbs are unchanged in
  definition, in quantity and in which artifact they read.
- **No band.** `[2.376227e−06, 2.138605e−05]` and `[63.998628773, 64.001371227]` stand.
- **No threshold and no tolerance.** `TOL_REL_WEDGE` (1.215313e−05 / 3.003125e−06 /
  7.142188e−07), `TOL_CM`, `K_CM = 1.0`, `FLOOR_REL = 1e−08`, `PLATEAU_TOL`, the residual
  floor 1e−12, the transverse floor 1e−10 × U_MAX and the arm acceptance thresholds
  (1e−10, 1e−12, n ≤ 80) are all unchanged. **The `[2.9, 3.1]×` band of §A1.4 is a band on
  a CONTROL's reading, not a gate on a graded quantity, and it did not exist before.**
- **No cap.** Ladder **293.0**, pre-ladder **20.0**, total **313.0**, `CAP_RATIO = 1.4479`,
  all unchanged. No cap is raised by any route.
- **No label and no verdict word.** The vocabulary is untouched.
- **No level, no rank count, no `N_ITER`, no `writeInterval`, no decomposition, no
  dictionary value** in `fvSolution`, `controlDict`, `fvOptions`, `transportProperties` or
  `blockMeshDict.template` — A0's relaxation is a **control's** setting, not the ladder's.
- **No rate, no `D_fine`, no `S`.**
- **No change to §6's registered prediction**, including the predicted verdict `PASS × 2`.
- **No re-grade of F23**, whose record stands `NOT A RESULT`, and whose run root is read
  **read-only** as C-7's and §A1.5's control artifact.
- **Nothing is sent, filed, uploaded, posted or submitted** (rule 7).

| amendment record | **v1.1** |
|---|---|
| gates / bands / thresholds / tolerances / caps / labels altered | **0** |
| existing controls made GATING | **4** (A4–A7, the `blockMesh`-path wedge control, both levels, both directions) |
| controls added | **1** (A0, the arm-acceptance reader's accept-side birth control) |
| new spend registered | **0.350 core-min**, inside the unchanged 20.0 pre-ladder cap |
| lines whose number changed above this section | **0** |
| md5 of the frozen blob at `57d31dde` | `4074e8981e9ae34a5f03f49b2d4b21ed` |
| md5 of this file's first 990 lines after the append | `4074e8981e9ae34a5f03f49b2d4b21ed` |
| the two digests | `**EQUAL — the assertion holds, MEASURED**` |
