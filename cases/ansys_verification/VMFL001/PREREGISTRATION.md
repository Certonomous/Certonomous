# VMFL001 — Flow Between Rotating and Stationary Concentric Cylinders: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. SUBMISSIONS PARKED.

**NOT YET RUN.** This file is frozen **before any solver starts** (CLAUDE.md rule 2;
`SUPERVISION_CHARTER.md` §3 check 4). At the moment of writing, **`verification/runs/
ansys_verification/VMFL001/` does not exist** — checked, not assumed, with `ls -d` at
2026-08-24T17:31Z, which returned *No such file or directory*. **Launch authorisation
comes from the `ansys-verification-supervisor` after its own personal freeze
verification and its own read of the comparator diff, and no agent message is Sanaa's
consent** (CLAUDE.md rule 9).

**Drafted 2026-08-24 by `ansys-lane-opus` for the `ansys-verification` team**, under
`ANSYS_VERIFICATION_CHARTER.md` §5. `RESULTS.md` is written afterwards in this
directory and **does not revise this file**; departures land as dated addenda at the
foot, never by editing above.

---

## 0. What this rung is, in three lines

1. **Reproduce VMFL001 in this lab's own solver** (OpenFOAM v2606 `simpleFoam`,
   steady laminar) and compare the tangential velocity in the annulus at
   r = 20/25/30/35 mm against **the manual's printed target**, which is an
   **analytical** reference (White, *Viscous Fluid Flow*, §3-2.3).
2. **The gate is 2 % relative at all four radii, at the finest of three meshes**, and
   the rung is `NOT A RESULT` unless the Roache triple on v_θ(35 mm) is `CONVERGING`.
3. **The verdict is a statement about this lab's solver against the manual's reference
   result. It is never a statement about Ansys** (charter §2).

---

## 1. The case, exactly as the manual states it

**Source: Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026,
pp. 15–16** (`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
sidecar lines ~896–960; title page verified per CLAUDE.md rule 15 and charter §4.2).

| what | value | where in the manual |
|---|---|---|
| reference | F. M. White, *Viscous Fluid Flow*, §3-2.3, McGraw-Hill, New York, 1991 | p. 15, Overview |
| solvers Ansys used | Ansys Fluent, Ansys CFX | p. 15 |
| physics / models | laminar flow, rotating wall | p. 15 |
| density ρ | **1 kg/m³** | p. 15, Material Properties |
| viscosity μ | **0.0002 kg/m-s** | p. 15 |
| inner radius R_i | **17.8 mm** | p. 15, Geometry |
| outer radius R_o | **46.28 mm** | p. 15 |
| angular velocity of the inner wall ω | **1 rad/s** | p. 15, Boundary Conditions |
| outer wall | stationary | p. 15, Test Case |
| domain Ansys modelled | a **180° segment**, "due to periodicity" | p. 15 |
| assumption | "The flow is steady. The tangential velocity at various sections can be calculated using analytical equations for laminar flow. These values are used for comparison with simulation results." | p. 15 |

**Derived, and stated so it can be checked:**

| quantity | value | how |
|---|---|---|
| kinematic viscosity ν | **2.0 × 10⁻⁴ m²/s** | μ/ρ = 2e-4 / 1 — this is what `simpleFoam` is given |
| gap d = R_o − R_i | **0.02848 m** | |
| radius ratio η = R_i/R_o | **0.384615** | a wide gap |
| gap Reynolds number Re_gap = ω R_i d / ν | **2.5347** | deeply laminar |
| Taylor number Ta = ω² R_i d³ / ν² | **10.28** | against a critical Ta of order 1.7 × 10³ — **no Taylor–Couette instability**, so the steady axisymmetric solution is the physical one and a steady solver is legitimate |
| momentum diffusion time d²/ν | **4.06 s** | the physical time to steady state, for context; SIMPLE iterations are not time |
| cell Péclet at the coarsest level, |u| Δr / ν | **0.134** | ≪ 2, which is why central convection is used (§6) |

## 2. The reference result — as the manual states it, and exactly

### 2.1 The manual's printed targets (this is what the gate is set against)

Manual Table .01.1 / .01.2, column **"Target, m/s"**, identical in both tables:

| location | **manual target, m/s** |
|---|---|
| r = 20 mm | **0.0151** |
| r = 25 mm | **0.0105** |
| r = 30 mm | **0.0072** |
| r = 35 mm | **0.0046** |

### 2.2 The exact analytical formula, and its values to 6 s.f.

The manual names the source but does not print the formula. It is the classical
circular Couette solution (White §3-2.3), inner cylinder rotating, outer at rest:

    v_θ(r) = ω R_i² (R_o² − r²) / ( r (R_o² − R_i²) )

evaluated at the manual's ρ, μ, R_i, R_o, ω (computed with `python3`, and re-derived
inside the comparator's `--selftest`, which was run at the comparator's commit):

| r | **exact v_θ, m/s (6 s.f.)** | manual target | target − exact | target/exact |
|---|---|---|---|---|
| 20 mm | **0.0151201** | 0.0151 | −0.133 % | 0.99867 |
| 25 mm | **0.0105336** | 0.0105 | −0.319 % | 0.99681 |
| 30 mm | **0.00718656** | 0.0072 | +0.187 % | 1.00187 |
| 35 mm | **0.00454781** | 0.0046 | **+1.148 %** | 1.01148 |

**Check demanded by the brief and met: r = 20 mm gives 0.015120 m/s.** Two limits are
also checked in the comparator's selftest: v_θ(R_i) = ω R_i exactly, and v_θ(R_o) = 0.

**The formula is viscosity-independent**, and §5 registers what that costs this gate.

### 2.3 Ansys's own reported values — CONTEXT ONLY, NOT THE GATE

Quoted from manual Tables .01.1 and .01.2 (charter §5.1: Ansys's value is quoted for
context and **never** used as the gate):

| location | Fluent, m/s | ratio | CFX, m/s | ratio |
|---|---|---|---|---|
| r = 20 mm | 0.0151 | 1.000 | 0.0150 | 0.991 |
| r = 25 mm | 0.0105 | 1.000 | 0.0105 | 0.998 |
| r = 30 mm | 0.0072 | 1.000 | 0.0071 | 0.988 |
| r = 35 mm | 0.0045 | **0.978** | 0.0045 | **0.976** |

**A lab number equal to Ansys's would be neither a pass nor a failure here.** The gate
is the manual's target; these two columns are printed beside the verdict so a reader
can see whether this lab landed inside, outside or alongside Ansys's own agreement
class.

## 3. THE GATE (frozen)

> **At the finest level (L3, 64 × 256), for ALL FOUR radii:**
>
>     | v_lab(r) − v_manual_target(r) | / | v_manual_target(r) |  ≤  0.02
>
> All four inside ⇒ the gate is met. **Any one outside ⇒ `GATE FAIL`.**

**Tolerance justification, fixed before any run (charter §5.1: from the manual's own
agreement class and the lab's grid triple, never from a first run):**

1. **The manual's printed targets are rounded to 2–3 significant figures**, and that
   rounding is worth up to **1.148 %** at r = 35 mm (§2.2). A gate tighter than that
   would fail a *perfect* solver on the manual's own rounding.
2. **Ansys's own worst reported ratio is 0.976** (CFX at 35 mm; Fluent 0.978) — i.e.
   the two commercial solvers land ≈ 2.4 % from the printed target at that radius.
3. **The manual's own stated goal is 3 %**: *"The goal for the test cases contained in
   this manual was to have results accuracy within 3% of the target solution"* (§1.3,
   p. 5). **2 % is deliberately tighter than the manual's own goal** — chosen so the
   gate is not a rubber stamp — while still holding the rounding of clause 1.
4. **2 % can still fail.** A wrong rotational boundary condition, a wrong radius
   ratio, an unconverged solve or a mesh too coarse to resolve the gap moves v_θ(35 mm)
   by tens of percent, not by 2 %. The selftest exercises both arms explicitly: +2.5 %
   is outside, +1.5 % is inside.

**Second, stricter DIAGNOSTIC, printed beside the gate and NOT the gate:**

> against the **exact formula** of §2.2: | v_lab(r) − v_exact(r) | / | v_exact(r) | ≤ **0.005**
> at all four radii.

It is a diagnostic and not the gate because the manual's printed target is the
reference this rung registered against, and at 35 mm the target and the exact value
are 1.148 % apart — a 0.5 % gate against the exact value would be a *different*
verification, and a stricter one, adopted after seeing that arithmetic. It is
reported because it is the number a reader who trusts White more than the rounding
will want. **A row that meets the gate and misses the diagnostic is a `PASS` with the
diagnostic printed beside it, not a softer word.**

## 4. THE GRID TRIPLE (Roache; CLAUDE.md rule 5)

**Triple quantity: v_θ at r = 35 mm**, the manual's worst-agreement point and the
radius where the solution is smallest and hardest.

| level | radial × azimuthal (over the full 360°) | cells | h ratio |
|---|---|---|---|
| **L1_16x64** (coarse) | 16 × 64 | 1,024 | 4 |
| **L2_32x128** (medium) | 32 × 128 | 4,096 | 2 |
| **L3_64x256** (fine) | 64 × 256 | 16,384 | 1 |

**Refinement ratio r = 2 exactly, in both directions, uniform radial spacing** (no
grading), so h₃/h₂ = h₂/h₁ = 2 with no unequal-ratio correction.

**Fixed probe procedure for the triple and the gate.** The `sets` function object in
`system/controlDict` (`type cloud`, `interpolationScheme cellPoint`, `setFormat raw`,
set name **`gateAxis`**) samples U at the four radii **on the +x axis (θ = 0)** at
mid-thickness z = 2.5 mm, at `endTime`. On the +x axis, **v_θ ≡ U_y exactly**; the
comparator nevertheless computes v_θ = −U_x sin θ + U_y cos θ from the sampled
coordinates, so the extraction is the same code for the diagnostic azimuth set.

**Verdict order (rule 5, and the gate can only turn a PASS/GATE FAIL *into* NOT A
RESULT, never the reverse):**

1. any level not iteratively converged or not plateaued ⇒ **`NOT A RESULT`**;
2. triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` ⇒ **`NOT A RESULT`**, with
   the three values, R, and both triples printed beside it;
3. triple `CONVERGING` ⇒ **`PASS`** inside the 2 % band else **`GATE FAIL`**, with
   **GCI at Fs = 1.25** printed.

**Classification thresholds, written down here and in the comparator so they cannot be
chosen later** (d21 = f_med − f_fine, d32 = f_coarse − f_med, R = d21/d32):

| condition | state |
|---|---|
| \|d21\| < 1e-12 m/s and \|d32\| < 1e-12 m/s | `EXACT` |
| \|d32\| < 1e-12 m/s, \|d21\| ≥ 1e-12 m/s | `DIVERGENT` |
| R < 0 | `OSCILLATORY` |
| \|R − 1\| ≤ 1e-3 | `STAGNANT` |
| R > 1 | `DIVERGENT` |
| 0 < R < 1 otherwise | `CONVERGING`, p = ln(1/R)/ln 2 |

with GCI_fine = Fs·|d21/f_fine| / (2^p − 1) and the Richardson value
f_ext = f_fine + (f_fine − f_med)/(2^p − 1). **No GCI is quoted when the three values
are not monotone** — that case is one of the `NOT A RESULT` states above.

## 5. The identity test (VERIFICATION_CHARTER §2a): how this gate fails, and how a wrong treatment could still pass

**(1) What result would make this gate FAIL?** Any v_θ more than 2 % from the manual's
printed target at any of the four radii: a mis-set `rotatingWallVelocity` (wrong ω,
wrong axis, wrong origin), a wall velocity imposed as a translation instead of a
rotation, the wrong radius pair, a mesh too coarse across the gap, a solve stopped
before the profile forms, or the wrong wall held fixed. All of these move the profile
by far more than 2 %.

**(2) Could a wrong treatment still PASS it?** **Yes, and here is the one that can.**
The exact solution v_θ(r) = ω R_i²(R_o² − r²) / (r(R_o² − R_i²)) **contains neither μ
nor ρ**. A run with the wrong viscosity — or the wrong density, or a turbulence model
switched on that happens to add little eddy viscosity — reaches the *same* steady
profile and passes this gate. **The gate is therefore not evidence that the transport
properties were right.** What is done about it, registered here rather than discovered
later:

- the comparator **reads `nu` back from the run's own `constant/transportProperties`**
  and **refuses** unless it is 2.0e-4 (a provenance check, not a physics check, and
  labelled as such);
- it **reads `omega` back from the run's own `0/U`** and refuses unless it is 1, and
  refuses unless the inner wall is `rotatingWallVelocity`;
- it reports whether the log proves the laminar model was **active** — and where the
  log cannot prove it either way, it says **`unverifiable-from-logs`** rather than
  silently passing (`VERIFICATION_CHARTER` §9, `ran_before_found`);
- the **exact analytic torque per unit axial length**, M′ = 4π μ ω R_i²R_o²/(R_o²−R_i²)
  = **9.345533 × 10⁻⁷ N·m/m**, is printed as a diagnostic, because unlike v_θ it *does*
  depend on μ. **It is not gated on**, because the manual publishes no torque
  reference and this rung will not invent one.

**(3) Is any gated quantity an identity?** No. v_θ is produced by the discretised
momentum equation on a mesh; nothing in the comparator can derive it from its own
inputs. The *reference* is analytical, which is the point of a verification case.

## 6. Solver, model, mesh and schemes — with the choices justified

**Solver: OpenFOAM v2606 `simpleFoam`** (`/usr/lib/openfoam/openfoam2606`), steady
incompressible, `constant/turbulenceProperties: simulationType laminar`.

*Chosen over `icoFoam`* because the manual's case **is** steady ("The flow is steady",
p. 15) and Ta = 10.3 says the steady solution is stable and unique. `icoFoam` would
integrate ≈ 4 s of physical diffusion time under a Courant limit to arrive at the same
profile; SIMPLE reaches it in a fixed iteration count that this pre-registration can
name in advance — which the strict completion rule needs. The price is that
"convergence" is an iterative statement, so §7 registers an explicit iterative
criterion instead of borrowing the solver's.

**Geometry: a FULL 360° planar annulus**, one cell thick in z (5 mm), `empty`
front/back — the standard OpenFOAM 2D planar case. Four `blockMesh` blocks of 90°
with `arc` edges, corners at 45°/135°/225°/315° so the +x sampling axis lies inside a
block rather than on a block corner.

*Chosen over the manual's 180° segment and over a small wedge, and here is why.* Both
of those need a **rotational cyclic** pair. A cyclic with a wrong transform, a wrong
`rotationAxis`, or a wrong pairing does not usually crash — it silently changes the
solution, and it would do so in the one direction this case is meant to test. The full
annulus has **no periodic patch at all**: two walls and two `empty` patches, and
nothing between the lab and the manual's boundary conditions. The cost is 2× the cells
of a 180° model, which at 16,384 cells is seconds (§8). **The azimuthal direction is
not idle in a full annulus**: the discrete circle is a polygon whose chord error falls
with azimuthal refinement, so both directions of the r = 2 refinement carry real
discretisation error into the triple.

**Boundary conditions.** `innerWall`: `rotatingWallVelocity`, `origin (0 0 0)`,
`axis (0 0 1)`, `omega 1`. `outerWall`: `noSlip`. `frontAndBack`: `empty`.
`p`: `zeroGradient` on both walls; the domain is closed, so `pRefCell 0`,
`pRefValue 0`.

**Schemes** (`system/fvSchemes`), all central and second order:
`ddtSchemes: steadyState`; `gradSchemes: Gauss linear`; `divSchemes: default Gauss
linear` with `div(phi,U) Gauss linear`; `laplacianSchemes: Gauss linear corrected`;
`snGradSchemes: corrected`; `interpolationSchemes: linear`.

*Disclosed choice:* `divSchemes` uses `default Gauss linear` rather than `default
none`. `none` aborts on an unnamed term — the disciplined default — but here **every**
term wanted is the same second-order central scheme, so a `default` that names it
cannot apply a *wrong* scheme to an unnamed term; it can only fail to alert us that a
term exists. The trade is registered here rather than found later. Central convection
is legitimate at cell Péclet 0.134 (§1) and is what makes the observed order in §4
meaningful.

**Solvers/relaxation** (`system/fvSolution`): `p` GAMG (tol 1e-10, relTol 0.01,
GaussSeidel), `U` smoothSolver symGaussSeidel (tol 1e-11, relTol 0.01),
`nNonOrthogonalCorrectors 1`, relaxation `p 0.3`, `U 0.7`.

**Mesh birth certificate** (`VERIFICATION_CHARTER` §9): `run_vmfl001.sh` runs
`checkMesh` at creation on every level, and the comparator **refuses** if the reported
cell count is not exactly radial × azimuthal for that level.

## 7. Completion and convergence — the clauses this rung will be held to

**Strict completion rule (CLAUDE.md rule 4), adapted to `simpleFoam`.** The comparator
**refuses (exit 2)** on any failed clause rather than grading a partial run:

1. `rc = 0` (from the level's own `RUN_RC.txt`, written by the run script);
2. an **`End`** line in `log.simpleFoam`;
3. **last time == `endTime` == 3000** — guaranteed meaningful because `fvSolution`
   carries **no `residualControl`**, so SIMPLE cannot stop early and leave a last time
   that is not `endTime`;
4. fields **`U` and `p` present at `endTime`** (the fields this case declares);
5. **`ExecutionTime` line count == `endTime`** (3000);
6. **age guard: every field at `endTime` strictly newer than the case's own `0/U`**,
   which `run_vmfl001.sh` touches immediately before launching the solver.

**A guard refuses a case where a run directory already exists**: `run_vmfl001.sh`
exits 2 if any level directory is present, so no level is ever run into an existing
case, and it also exits 2 if this pre-registration is not committed at `HEAD`.

**Iterative convergence, registered in advance** (both must hold, at every level):

- **residuals**: the initial residual of `Ux`, `Uy` and `p` at the final iteration is
  **< 1e-6**;
- **plateau**: the per-iteration probe of v_θ(35 mm) has peak-to-peak **< 1e-6 m/s over
  the last 20 %** of the iterations (600 of 3000).

The plateau series comes from a separate `probes` function object writing every
iteration. **Those are cell values, not point-interpolated, and are never the graded
number** — they answer *has it stopped moving*, not *what is it*. The graded number is
always the `gateAxis` `sets` sample at `endTime`.

**A level failing either clause makes the rung `NOT A RESULT`** (rule 5, step 1),
before the triple is even classified.

## 8. Cost (CLAUDE.md rule 12)

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 |
| levels | 1,024 + 4,096 + 16,384 = **21,504 cells total**, 3,000 SIMPLE iterations each |
| **estimate** | **3.0 core-minutes** for all three levels — laminar, no turbulence fields, GAMG on ≤ 16k cells; the fine level dominates |
| basis of the estimate | order-of-magnitude from cell-iterations (≈ 6.5 × 10⁷ cell-iterations at ≈ 1 µs each ≈ 65 s) — **an estimate, not a measurement** |
| **CAP** | **10 core-minutes**, enforced by `timeout` inside `run_vmfl001.sh`; **an overrun STOPS the run and it does not get a new budget** — the script writes `CAP_EXCEEDED.txt` and refuses |
| dollars at the estimate | **$0.00257** (3 core-min ÷ 60 × $0.0513/core-h) |
| dollars at the cap | **$0.00855** |
| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; **this is a per-item cost, not a new ceiling** (rule 9) |
| calibration | at completion, actual core-minutes from `RUN_RC.txt`/`COST.txt` against this estimate, ratio and attribution, one row appended to `docs/COST_CALIBRATION.md` (rule 12) |

## 9. The grading path, frozen (VERIFICATION_CHARTER §2d)

| what | path | committed blob sha |
|---|---|---|
| **comparator** | `cases/ansys_verification/VMFL001/grade_vmfl001.py` | **`8cb29610e5d6f6fa4291df503a98bc99d0ff660f`** |
| run script | `cases/ansys_verification/VMFL001/run_vmfl001.sh` | `3da645cf630ec33e178c394512089adb8c81b864` |
| controlDict (sampler + probes) | `case/system/controlDict` | `c94a72b019157b6106fafdd7ac763f5b96077134` |
| blockMesh template | `case/system/blockMeshDict.template` | `45286819aa46b5df7fc0b938da1694ebdeb03068` |
| fvSchemes | `case/system/fvSchemes` | `b22740ae317a6eb5ca7e67feca94699e27e15dcf` |
| fvSolution | `case/system/fvSolution` | `6f88ec556d6e4725986565b02f8dfea73e4d405a` |
| `0/U` (BCs + age-guard marker) | `case/0/U` | `fd65259adff3152407a40e4decf6191d6dd2e350` |

The comparator was **committed before this file** (commit `e8dd53c2`, "VMFL001 case
inputs and comparator … NO COMPUTE, prereg not yet frozen"), and both commits precede
any solver. **At analysis time the grading path is re-hashed against these shas**; a
freeze that is claimed and not checked is a claim about intent.

**Run outputs go to `verification/runs/ansys_verification/VMFL001/<level>/`**, never
beside this prose (FILING_CHARTER R6). **The grading JSON is
`verification/runs/ansys_verification/VMFL001/GRADING_VMFL001.json`.**

**What the comparator has NOT been exercised on, stated plainly.** No solver has run,
so its OpenFOAM-output parsing has never seen real `simpleFoam` output. What *has*
fired, at the comparator's own commit and with zero solver compute, is its
`--selftest`: **18 checks, all passed** — the exact formula at three points, the raw
reader on a synthetic file with the v2606 header, a **refusal (exit 2)** on a
headerless file, the planted-zero control's **positive and negative** arms, the Roache
classifier on synthetic `CONVERGING` (recovering p = 2.0 to 1e-9 and Richardson
extrapolation to f_exact) / `DIVERGENT` / `OSCILLATORY` / `STAGNANT` / `EXACT`
families, and both arms of the gate. **If the comparator cannot parse the real output,
it refuses and the rung is `NOT A RESULT`** — it never guesses a column. Any change to
the parser after the first solve is a dated addendum disclosing exactly what changed
and whether it could move a number, read by the supervisor before any re-grade.

## 10. Planted-zero control (CLAUDE.md rule 3)

The comparator copies the finest level's sampled `gateAxis` output to a temporary
tree, **adds PLANT = 1.234 × 10⁻³ m/s to the `U_y` column of the r = 35 mm row**,
**reads the file back from disk**, and re-runs the *same* extraction on the copy. The
extracted v_θ(35 mm) must move by exactly PLANT (to 1e-15 m/s), and no other radius
may move. **If it does not, the comparator refuses (exit 2)** with: *the reader cannot
see a 1.234e-03 m/s difference planted on disk; its numbers mean nothing.* The run
tree is never modified — only the temporary copy is planted.

## 11. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). The comparator asserts its own verdict string is in
that list before printing it. Whatever the answer, the row lands in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`; **only a `PASS` is a
credential**, and a `GATE FAIL` is a finding that is never removed, re-labelled or
softened to `PENDING` (charter §6).

## 12. What this rung will NOT claim

- **Nothing about Ansys.** Ansys's numbers are context (§2.3). This box has no Fluent
  and no CFX; the manual's `rot_conc_cyl.cas` and `rotating_cylinder.def` are not run.
- **Nothing about the transport properties**, beyond the provenance checks of §5 — the
  gated quantity cannot see μ or ρ.
- **Nothing about grid independence beyond the triple**: the verdict is a statement
  about the finest level, with GCI printed as the uncertainty channel.
- **No archive was read to write this file.** Every number here comes from the manual's
  sidecar or from arithmetic shown above. The VM2026R1 archive for this case lives at
  `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_CFX_ARCHIVES/VMFL001B.wbpz`
  and `…/VM2026R1_FLUENT_ARCHIVES/VMFL001_WB.wbpz` (both named in
  `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`; D-6 ruling clause g:
  archive paths are cited under that home only). **They were not opened.**
