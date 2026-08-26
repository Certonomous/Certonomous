# VMFLGPU001 — Flow Between Rotating and Stationary Concentric Cylinders (GPU solver path): PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN.** This file is frozen **before any solver starts** (CLAUDE.md rule 2;
`SUPERVISION_CHARTER.md` §3 check 4). Checked, not assumed: at
**2026-08-26T17:25:25Z**, `ls -d verification/runs/ansys_verification/VMFLGPU001`
returned *No such file or directory* on the lab box. The empty run directory created
afterwards for the queue validator's AGE-GUARD contains **zero files** and no time
directory.

**Drafted 2026-08-26 by `ansys-lane-opus` (lane A) for `ansys-verification-supervisor`**,
under authority boarded at HEAD: Sanaa verbatim `bc0e687e` *"you have permission to do
anything that leads to the lab having more runs under its belts"* and `73eccb1b`
*"Why did the ansys team not launch the gpu runs already?"*. Decisions taken under that
authority without asking are marked `[lab-attributed]`. **No agent's message is Sanaa's
consent** (CLAUDE.md rule 9); launch authorisation remains the supervisor's own personal
check 4.

`RESULTS.md` is written afterwards in this directory and **does not revise this file**;
departures land as dated addenda at the foot, never by editing above (rule 6).

---

## 0. What this rung is, in four lines

1. **The object under verification is the lab's GPU SOLVER PATH** — OpenFOAM v2606 +
   petsc4Foam + PETSc-CUDA (cuSPARSE, `sm_89`) on the NVIDIA L4 of
   `ip-172-31-44-162`. It is **not** the physics: the physics is the known control,
   already exercised on the CPU as VMFL001.
2. The vehicle is the manual's concentric-cylinder Couette case (p. 225, table p. 226),
   whose reference is **closed-form** and which this comparator **evaluates itself**.
3. The gate has **three limbs** (§6). A miss on **limb A is `NOT A RESULT`** whatever
   the physics says: a CPU number that happens to match the reference verifies nothing
   about the GPU path.
4. **The verdict is a statement about this lab's GPU solver path against a closed-form
   reference. It is never a statement about Ansys** (charter §2). This box has no
   Fluent; `vt001.msh` and `vmfl001.jou` were not run and no VM2026R1 archive was opened.

---

## 1. The ten-line template form (PREREG_TEMPLATE.md, Amendments 1–6a), filled

```
1. CASE      : VMFLGPU001 -- Flow Between Rotating and Stationary Concentric Cylinders
               -- manual p.225 (results table p.226). CPU PARENT: VMFL001.
               Solver: OpenFOAM v2606 simpleFoam + petsc4Foam (PETSc-CUDA, sm_89).
               NOT YET RUN; verification/runs/ansys_verification/VMFLGPU001/ absent
               on the lab box at 2026-08-26T17:25:25Z (checked with ls -d).
2. REFERENCE : v_theta = 0.0151201 / 0.0105336 / 0.00718656 / 0.00454781 m/s at
               r = 20/25/30/35 mm -- the CLOSED-FORM annular Couette solution
               EVALUATED BY THIS LAB (formula and arithmetic in section 5), from the
               manual's own geometry and omega (F. M. White, Viscous Fluid Flow
               section 3-2.3). Manual PRINTED column 0.0151/0.0105/0.0072/0.0046 and
               Ansys Fluent GPU 0.0152/0.0105/0.0072/0.0045 are CONTEXT ONLY.
3. REF KIND  : closed-form/exact -> buys V, NEVER P.
4. CEILING   : GATE REACHED (closed-form buys V; a met band is code verification,
               NOT a validation credential -- template Amendment 1).
5. QUANTITY  : v_theta on the +x axis at the four manual radii [m/s], four DISCRETE
               point channels, point-interpolated (cellPoint) at endTime.
6. GATE      : A GPU-execution (three tells + forced-CPU discriminator, binary) ;
               B |v_GPU - v_CPU|/|v_CPU| <= 1e-4 at all 4 radii, ALL 3 levels ;
               C |v_GPU - v_exact|/|v_exact| <= 0.02 at all 4 radii, finest level.
7. LADDER    : simpleFoam laminar, rho=1, mu=2e-4 (nu=2e-4); FULL 360-deg planar
               annulus, one cell thick, empty front/back; rotatingWallVelocity inner,
               noSlip outer; every linear solve through petsc4Foam; birth-certified
               mesh at every level (MESH_STANDARD section 6, checkMesh + cell count).
8. SEED      : r = 2 triple, L1 1024 / L2 4096 / L3 16384 cells; serial (RANKS = 1),
               no decomposition and no RNG. TWO ARMS per level: GPU (aijcusparse/cuda)
               and forced-CPU (aij/standard), byte-identical otherwise.
9. RISK      : THE MIXED-MPI TOOLCHAIN (section 4). MEASURED on the instance
               2026-08-26T17:15:07Z: PETSc's CUDA build compiled and `make check`
               died in MPI_Init (opal_init failed) because the DLAMI prepends
               /opt/amazon/openmpi (AWS Open MPI 4.1.7) ahead of Ubuntu's 5.0.10 --
               SAME SONAME libmpi.so.40, so the linker substitutes it SILENTLY. A run
               on the wrong MPI is not the toolchain under verification.
10. ORDER    : p_f = 2 (all schemes central, second order); expect p_obs ~ 2;
               p_obs > 2.3 is declared SUSPICIOUSLY HIGH -- a warning, never a win.
               P_MIN = 0.05: below it the rung is NOT A RESULT and NO GCI IS PRINTED.
11. WEDGE    : N/A. A FULL 360-deg planar annulus is modelled, not an axisymmetric
               wedge, so the sin(t)/t area deficit (N-AV9) does not arise. Stated
               rather than omitted.
12. COST     : 0.40 GPU-h estimate, cap 2.0 GPU-h ENFORCED by `timeout` in the
               launcher; 24.0 core-min (12.0 CPU arm + 12.0 GPU-arm host rank),
               CPU-arm cap 40 core-min ENFORCED. Dollars DERIVED, NOT MEASURED.
13. CONTROLS : planted-zero per channel (section 10, rule 3); strict completion +
               age guard (section 9, rule 4); Roache gating with P_MIN (section 8,
               rule 5); LAUNCH-TIME FREEZE CHECK against HEAD (Amendment 2);
               cap in the executable path (Amendment 3 item 2); no `set -u`;
               launcher self-exercised (Amendment 3 item 6, section 13);
               comparator --selftest 37/37 GREEN under python3 AND python3 -O.
```

---

## 2. The case, exactly as the manual states it

**Source: Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 225 (Overview,
Test Case, Material Properties/Geometry/Boundary Conditions) and p. 226 (Table
.gpu001.1)** —
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
sidecar lines 5866–5910. **Read from the sidecar page for this case, not inherited from
the CPU parent's page.**

| what | value | where |
|---|---|---|
| reference | F. M. White, *Viscous Fluid Flow*, §3-2.3, McGraw-Hill, New York, 1991 | p. 225, Overview |
| solver Ansys used | **Ansys Fluent GPU** | p. 225 |
| physics / models | laminar flow, rotating wall | p. 225 |
| density ρ | **1 kg/m³** | p. 225, Material Properties |
| viscosity μ | **0.0002 kg/m-s** | p. 225 |
| inner radius R_i | **17.8 mm** | p. 225, Geometry |
| outer radius R_o | **46.28 mm** | p. 225 |
| angular velocity of the inner wall ω | **1 rad/s** | p. 225, Boundary Conditions |
| outer cylinder | **stationary** | p. 225, Test Case |
| domain Ansys modelled | a **180° segment**, "due to periodicity" | p. 225 |
| assumption | "The flow is steady. The tangential velocity at various sections can be calculated using analytical equations for laminar flow. These values are used for comparison with simulation results." | p. 225 |

**These are the SAME material properties, geometry and ω the CPU parent VMFL001 read
from p. 15.** Verified by reading the GPU sidecar page directly; the two pages agree.

**Derived and shown so it can be checked:** ν = μ/ρ = **2.0 × 10⁻⁴ m²/s** (what
`simpleFoam` is given); gap d = R_o − R_i = **0.02848 m**; radius ratio η = **0.384615**;
Re_gap = ω R_i d / ν = **2.5347**; Ta = ω² R_i d³ / ν² = **10.28** against a critical Ta
of order 1.7 × 10³, so **there is no Taylor–Couette instability** and the steady
axisymmetric solution is the physical one.

---

## 3. THE REFERENCE — the closed form, the formula, and the four values

**This comparator does not read the manual's printed column as its reference. It
evaluates the closed form itself** from the manual's geometry and ω. The manual names
the source and does not print the formula; it is the classical circular-Couette
solution (White §3-2.3), inner cylinder rotating, outer at rest:

> **v_θ(r) = ω R_i² (R_o² − r²) / ( r (R_o² − R_i²) )**
>
> equivalently **v_θ(r) = [ ω R_i² / (R_o² − R_i²) ] · ( R_o²/r − r )**

with **ω = 1 rad/s, R_i = 0.0178 m, R_o = 0.04628 m** (manual p. 225). Both forms were
evaluated and agree to machine precision.

### 3.1 The four gate values (the reference, frozen here before any run)

| r | **v_θ exact, m/s (6 s.f.)** | full precision | manual printed (CONTEXT) | printed − exact |
|---|---|---|---|---|
| **20 mm** | **0.0151201** | 0.015120125000000 | 0.0151 | −0.133 % |
| **25 mm** | **0.0105336** | 0.010533600000000 | 0.0105 | −0.319 % |
| **30 mm** | **0.00718656** | 0.007186564814815 | 0.0072 | +0.187 % |
| **35 mm** | **0.00454781** | 0.004547809523810 | 0.0046 | **+1.148 %** |

**The manual's printed "Target" column is this same closed form rounded to 2 s.f.** The
worst rounding is +1.148 % at r = 35 mm — which is precisely why the CPU parent had to
absorb a rounding term in its band and this rung does not (§6.3).

**Two limits are checked inside the comparator's `--selftest`, and both hold:**
v_θ(R_i) = ω R_i = 0.0178 m/s exactly, and v_θ(R_o) = 0 exactly.

**The formula contains neither μ nor ρ.** §7 registers what that costs this gate and
what is done about it.

### 3.2 Ansys's own reported values — CONTEXT ONLY, NEVER THE GATE

Manual Table .gpu001.1, column "Ansys Fluent GPU" (charter §5.1):

| r | Ansys Fluent GPU, m/s | manual's printed ratio |
|---|---|---|
| 20 mm | 0.0152 | 1.006 |
| 25 mm | 0.0105 | 1.000 |
| 30 mm | 0.0072 | 1.000 |
| 35 mm | 0.0045 | **0.978** |

**A lab number equal to Ansys's would be neither a pass nor a failure here.** These are
printed beside the verdict so a reader can see whether this lab landed inside, outside
or alongside Ansys's own agreement class. **Reproducing a solver's number is not a
verification** (template line 3).

---

## 4. THE TOOLCHAIN — and the mixed-MPI hazard, registered as a gate condition

The GPU path is built by `docs/ansys_verification/gpu/build_gpu_solver.sh` on
`ip-172-31-44-162` (4 vCPU, NVIDIA L4, Ubuntu 26.04). **This rung may not run until that
build has PROVEN the path**, and the launcher refuses at zero compute unless all three
of the following hold (`run_vmflgpu001.sh` STEP 0):

1. **`$HOME/gpu_build/STATUS.smoke` reads `smoke_rc=0`.** That rc comes from
   `smoke_test_gpu_path.sh`, whose **forced-CPU control IS the discriminator**
   (`SUPERVISOR_REVIEW.md` lines 27–44): a smoke test run without it certifies nothing.
   Absent, unreadable or any other rc **refuses (exit 2)**.
2. **`$HOME/gpu_build/TOOLCHAIN_MANIFEST.txt` exists.** A GPU-path proof whose toolchain
   cannot be *named* — which OpenFOAM, which PETSc sha, which petsc4Foam sha, which
   `libpetscFoam.so` sha256 — is not evidence about any particular toolchain. It is
   copied into the run root so a reader can check it without leaving the record.
3. **`$HOME/gpu_build/env.sh` exists and is sourced BEFORE OpenFOAM's `bashrc`.** It
   carries the MPI pin.

### 4.1 The measured defect this condition exists for

**MEASURED on the instance, 2026-08-26T17:15:07Z, reported by the supervisor:** the
PETSc CUDA build **compiled** and then `make check` **failed in `MPI_Init`** —
`opal_init failed`. **Cause, triaged and measured:** the DLAMI **prepends
`/opt/amazon/openmpi` (AWS Open MPI 4.1.7) to `PATH` and `LD_LIBRARY_PATH`, shadowing
Ubuntu's Open MPI 5.0.10 that OpenFOAM and PETSc were compiled against — and both
export the SAME soname `libmpi.so.40`**, so the dynamic linker substitutes one for the
other **silently**.

> **This is `PREREG_TEMPLATE.md` Amendment 5's shape exactly — internally perfect,
> externally false: every package installed, and nothing able to run.** It is also
> L-339's: the answer was knowable only by **resolving the real library on the real
> `LD_LIBRARY_PATH`**, never by reading an install list.

### 4.2 The gate condition, binding on limb A

**LIMB A REQUIRES THE TOOLCHAIN TO NAME AND RESOLVE ONE OPEN MPI, shared by OpenFOAM,
PETSc and petsc4Foam.** The launcher (STEP 2b) does not read a manifest line claiming
an MPI; it **resolves** the `libmpi.so` that the dynamic linker actually hands to each
consumer — `$FOAM_LIBBIN/$FOAM_MPI/libPstream.so`, `$PETSC_ARCH_PATH/lib/libpetsc.so`
and `$FOAM_USER_LIBBIN/libpetscFoam.so` — takes `readlink -f` of each, and **refuses
(exit 2) unless all three are the same file**. The `simpleFoam` binary's own resolution
is cross-checked (empty is normal, since it binds MPI through `libPstream`; a
*disagreeing* non-empty result refuses). All of them, plus `mpirun --version` and the
raw `ldd … | grep libmpi` lines, are recorded in `LAUNCH_RECORD.txt` as
**PHYSICS-CRITICAL** limb-A lines: **a run on the wrong MPI is not the toolchain under
verification.**

**What is NOT claimed here:** that the build has succeeded. At the time of this freeze
the toolchain build is still in flight and `STATUS.smoke` does not yet exist on the
instance. **This document registers the gate; it reports no toolchain result.**

---

## 5. Solver, model, mesh and schemes

**Solver: OpenFOAM v2606 `simpleFoam`**, steady incompressible,
`constant/turbulenceProperties: simulationType laminar`, **with every linear solve
routed through `petsc4Foam`** (`libs (petscFoam);` in `controlDict`).

**The case inputs are BYTE-IDENTICAL to the CPU parent's frozen case** — verified by
`diff` against `HEAD:cases/ansys_verification/VMFL001/case/…`: `0/U`, `0/p`,
`constant/transportProperties`, `constant/turbulenceProperties`, `system/fvSchemes` and
`system/blockMeshDict.template` all match, and `0/U` and `system/fvSchemes` carry the
**same blob shas** (`fd65259a…`, `b22740ae…`) as the parent's. Only `fvSolution` (the
linear solvers, now PETSc, with the arm's `mat_type`/`vec_type` templated in) and
`controlDict` (templated `endTime`) differ, and each difference is registered below.

**Geometry: a FULL 360° planar annulus**, one cell thick in z (5 mm), `empty`
front/back; four `blockMesh` blocks of 90° with `arc` edges, corners at 45°/135°/225°/
315° so the +x sampling axis lies inside a block rather than on a block corner.
*Chosen over the manual's 180° segment* because a 180° model needs a rotational cyclic
pair, and a cyclic with a wrong transform does not crash — it silently changes the
solution, in the one direction this case tests. The full annulus has **no periodic patch
at all**.

**Boundary conditions.** `innerWall`: `rotatingWallVelocity`, `origin (0 0 0)`,
`axis (0 0 1)`, `omega 1`. `outerWall`: `noSlip`. `frontAndBack`: `empty`. `p`:
`zeroGradient` both walls, `pRefCell 0`, `pRefValue 0` (the domain is closed).

**Schemes**, all central and second order: `ddtSchemes steadyState`; `gradSchemes Gauss
linear`; `divSchemes default Gauss linear` with `div(phi,U) Gauss linear`;
`laplacianSchemes Gauss linear corrected`; `snGradSchemes corrected`;
`interpolationSchemes linear`. Central convection is legitimate at cell Péclet ≈ 0.134,
and it is what makes the observed order in §8 meaningful. *Disclosed:* `default Gauss
linear` rather than `default none` — every term wanted is the same second-order scheme,
so a `default` cannot apply a *wrong* scheme; it can only fail to alert us that a term
exists. Inherited from the parent, unchanged.

**Linear solvers — THE ONE SUBSTANTIVE DIFFERENCE FROM THE PARENT, and the reason the
case exists.** `p`: `solver petsc`, `ksp_type cg`, `pc_type jacobi`; `U`: `solver
petsc`, `ksp_type bcgs`, `pc_type jacobi`. The **outer tolerances are the parent's,
unchanged** (`p` 1e-10, `U` 1e-11, `relTol` 0.01), as are the relaxation factors
(`p` 0.3, `U` 0.7) and `nNonOrthogonalCorrectors 1`. **No `residualControl`**, so both
arms take the same number of outer iterations and the strict-completion clauses "last
time == endTime" and "ExecutionTime count == endTime" are meaningful rather than
tautological.

**THE TWO ARMS ARE OTHERWISE BYTE-IDENTICAL.** `mat_type`/`vec_type` are the *only*
substitution that differs: `aijcusparse`/`cuda` for the GPU arm, `aij`/`standard` for
the forced-CPU arm. That is what makes limb B a statement about **where the linear
algebra ran** and about nothing else, and the launcher `grep`s the materialised
`fvSolution` for the expected `mat_type`/`vec_type` before every solve, refusing if the
arm is not the arm it claims to be.

**Mesh birth certificate** (`VERIFICATION_CHARTER` §9, `MESH_STANDARD` §6): the launcher
runs `checkMesh` at creation on every level of every arm, refuses unless it reports
`Mesh OK`, and refuses unless the cell count is exactly the registered value; the
comparator re-checks both from `log.checkMesh`.

---

## 6. THE GATE (frozen, three limbs)

**Verdict routing.** A miss on **limb A** is `NOT A RESULT`. A non-`CONVERGING` triple
is `NOT A RESULT` (rule 5). A miss on **limb B** or **limb C** with everything above
holding is `GATE FAIL`. Everything holding is **`GATE REACHED`** — the ceiling, because
a closed-form reference buys V and never P (template Amendment 1).

### 6.1 LIMB A — GPU EXECUTION (binary, physics-critical, non-negotiable)

All three tells of `smoke_test_gpu_path.sh` must fire **in this case's own run record**,
at **every level**:

1. PETSc `-log_view` reports **non-zero GPU flops** for `KSPSolve` in
   `log.simpleFoam`;
2. the solver PID holds **non-zero device memory during the solve**, in this level's own
   concurrent `nvidia-smi` sample `gpusample.txt`;
3. the **active PETSc matrix type is `*aijcusparse`** in `log.simpleFoam`.

**AND the forced-CPU arm of the SAME level must show GPU-ABSENT on tells 1 and 3.**
Tell 1 is deliberately loose and **cannot discriminate on its own** — PETSc's
`-log_view` prints GPU columns and `CpuToGpu`/`GpuToCpu` rows on a CUDA-configured build
**even when the solve ran on the CPU** (template Amendment 5). **The forced-CPU control
IS the discriminator.** If the forced-CPU arm reports GPU work, the tells cannot tell
GPU from CPU on this build and **the row certifies NOTHING**: the comparator refuses
(exit 2), and it is never a pass.

**Limb A also requires the one-MPI condition of §4.2**, enforced by the launcher before
any solver starts.

### 6.2 LIMB B — GPU ≡ CPU CONSISTENCY (the heart of the verification)

> **| v_GPU(r) − v_CPU(r) | / | v_CPU(r) | ≤ 1.0 × 10⁻⁴, at ALL FOUR radii and ALL
> THREE levels.**

**Derivation of 1e-4, before any run.** The two arms differ only in *where* the same
linear system is solved. They share the mesh, the schemes, the relaxation, the Krylov
method, the preconditioner, the outer iteration count, and the linear tolerances — of
which the **loosest is `relTol = 0.01` on a converged steady state whose final initial
residuals are required to be below 1e-6 (§9)**. Two solvers agreeing to their own
linear-solver relative tolerance is the tightest bound that is *derivable* rather than
hoped for; 1e-4 is that bound, and it is two orders below the `relTol` and two orders
above IEEE double round-off accumulated over ~10⁴ outer iterations. **It is the
family-wide default of `DRAFT_PREREGISTRATIONS_VMFLGPU.md`, adopted unchanged.**

**Limb B is what makes this a GPU-path verdict**, independently of limb C: a GPU result
equal to the lab's own CPU result to solver tolerance verifies the GPU linear-algebra
path even where the shared physics were to miss the reference.

### 6.3 LIMB C — PHYSICS, against the closed form THIS LAB EVALUATES

> **| v_GPU(r) − v_exact(r) | / | v_exact(r) | ≤ 0.02, at ALL FOUR radii, at the
> finest level L3.**

with `v_exact` the §3 formula evaluated by the comparator itself.

**Tolerance justification, fixed before any run** (charter §5.1: from the manual's own
agreement class and the lab's grid triple, never from a first run):

1. **The manual's own stated goal is 3 %**: *"The goal for the test cases contained in
   this manual was to have results accuracy within 3% of the target solution"* (§1.3,
   p. 5). **2 % is deliberately tighter than the manual's own goal**, so the gate is not
   a rubber stamp.
2. **This band carries NO rounding term.** The CPU parent gated against the manual's
   2-s.f. printed column and had to hold **1.148 %** of pure rounding at r = 35 mm
   inside its 2 %. Because this rung evaluates the closed form exactly, that term is
   **not in this budget at all** — so **2 % here is strictly tighter than the parent's
   2 %**, and choosing the exact reference tightens the gate rather than loosening it.
   `[lab-attributed]`
3. **Ansys's own worst reported ratio is 0.978** at r = 35 mm — i.e. a commercial GPU
   solver lands ≈ 2.2 % from the printed target there. 2 % against the *exact* value is
   inside that class, not outside it.
4. **2 % can still fail.** A mis-set `rotatingWallVelocity` (wrong ω, axis or origin), a
   wall velocity imposed as a translation, the wrong radius pair, a mesh too coarse
   across the gap, the wrong wall held fixed, or a solve stopped before the profile
   forms all move v_θ by tens of percent. The comparator's selftest drives both arms: a
   CONVERGING triple sitting 3.0 % out is `GATE FAIL`; the in-band fixture reaches the
   ceiling.

**Printed beside the verdict, and NOT the gate:** the same four ratios against the
manual's **printed** column, so a reader who prefers the manual's own number can see it;
and the manual's Fluent GPU column. **A row that meets the gate and differs from the
printed column is a `GATE REACHED` with the diagnostic printed beside it, not a softer
word.**

---

## 7. The identity test (`VERIFICATION_CHARTER` §2a)

**(1) What result would make this gate FAIL?** For limb A: any level where a tell does
not fire, or where the forced-CPU control leaks GPU work. For limb B: any GPU/CPU
divergence above 1e-4 — which is what a wrong `mat_type`, a silently-different PETSc
option set, or a numerically unstable cuSPARSE path would produce. For limb C: the
boundary-condition and mesh errors of §6.3 clause 4.

**(2) Could a wrong treatment still pass?** **Yes, and here is the one that can.** The
exact solution **contains neither μ nor ρ**, so a run with the wrong viscosity or
density reaches the same steady profile and passes limb C. **This gate is therefore not
evidence that the transport properties were right.** Registered here, not discovered
later. What is done about it:

- the case ships `nu 2e-04` in `constant/transportProperties`, byte-identical to the
  parent's frozen blob, and the launcher copies it rather than generating it;
- the **exact analytic torque per unit axial length**,
  M′ = 4π μ ω R_i² R_o² / (R_o² − R_i²) = **9.345533 × 10⁻⁷ N·m/m**, is printed by the
  comparator as a **diagnostic**, because unlike v_θ it *does* depend on μ. **It is not
  gated on**, because the manual publishes no torque reference and this rung will not
  invent one.

**A second, GPU-specific identity risk, and the answer to it.** Limb B compares two arms
that share every input. Could they agree *because* they are the same run? No: they are
separate solves in separate directories with different `mat_type`/`vec_type`, and
**limb A's forced-CPU control requires them to be DEMONSTRABLY different** — the same
artifacts that make limb B's agreement meaningful are the ones that prove the two arms
did not run on the same hardware path. **A limb-B pass with a leaking control is a
refusal, not a pass.**

**(3) Is any gated quantity an identity?** No. v_θ is produced by the discretised
momentum equation on a mesh; nothing in the comparator can derive it from its own
inputs.

---

## 8. THE GRID TRIPLE (Roache; CLAUDE.md rule 5)

**Triple quantity: v_θ at r = 35 mm on the GPU arm** — the manual's worst-agreement
point, and the radius where the solution is smallest and hardest.

| level | radial × azimuthal (full 360°) | cells | `endTime` | h ratio |
|---|---|---|---|---|
| **L1_16x64** | 16 × 64 | **1,024** | 3000 | 4 |
| **L2_32x128** | 32 × 128 | **4,096** | 3000 | 2 |
| **L3_64x256** | 64 × 256 | **16,384** | **6000** | 1 |

**Refinement ratio r = 2 exactly, both directions, uniform radial spacing.**

**The finest level gets 6000 iterations, not 3000, and this is the parent's measured
lesson, not a guess.** VMFL001 run 1 completed all three levels at `endTime = 3000` and
was `NOT A RESULT` because **L3's final initial residuals were 1.20e-06 / 1.20e-06 /
2.89e-06 — above the 1e-6 clause — and its plateau peak-to-peak was 2.77e-05, 27× the
clause** (`VMFL001/RESULTS.md` §4; L-287, N-AV5). *A single frozen `endTime` across a
grid triple is adequate at the coarse levels and inadequate at the fine one.* The repair
that document names is **a per-level `endTime` registered in advance**, and that is what
is registered here. `[lab-attributed]`

**Classification thresholds, written here and in the comparator so they cannot be chosen
later** (d21 = f_med − f_fine, d32 = f_coarse − f_med, R = d21/d32):

| condition | state |
|---|---|
| \|d21\| < 1e-12 and \|d32\| < 1e-12 | `EXACT` |
| \|d32\| < 1e-12, \|d21\| ≥ 1e-12 | `DIVERGENT` |
| **\|R − 1\| ≤ 1e-3** (tested **BEFORE** any p) | **`STAGNANT`** |
| R < 0 | `OSCILLATORY` |
| R > 1 | `DIVERGENT` |
| 0 < R < 1 otherwise, **p = ln(1/R)/ln 2 < P_MIN = 0.05** | **`BELOW_P_MIN`** |
| 0 < R < 1 otherwise, p ≥ P_MIN | `CONVERGING` |

**`FINDING_p_floor.md` §4 is adopted in full and both of its clauses are live here:**
classification is **by the RATIO FIRST**, so a stagnant triple is caught *before*
`ln(R)/ln(r)` can turn a floating-point crumb into a valid-looking near-zero order; and
**an observed order below P_MIN = 0.05 is `NOT A RESULT` with NO GCI PRINTED**, because
a GCI computed from a near-zero order is a number with no meaning.

**The floor is DRIVEN, not declared** (§4's own requirement: *"A floor nobody tests is a
floor nobody has"*). The comparator's selftest builds a whole synthetic run whose triple
has R = 0.98 → p = 0.02915, runs it **end to end through the grader under `python3 -O`**,
and requires the printed verdict to be `NOT A RESULT` **and the string `GCI_fine =` to
appear nowhere in the output**. The equally-spaced degenerate triple (R = 1 exactly) is
driven the same way. Both are checks 15–16 of §12.

**Verdict order (rule 5; the gate can only turn a PASS/GATE FAIL *into* `NOT A RESULT`,
never the reverse):** (1) any arm/level not complete, not converged or not plateaued, or
with rc `NOT MEASURED` ⇒ `NOT A RESULT`; (2) limb A missed ⇒ `NOT A RESULT`; (3) triple
not `CONVERGING` ⇒ `NOT A RESULT`, with the three values, R and both differences printed
and **no GCI**; (4) limb B missed ⇒ `GATE FAIL`; (5) limb C missed ⇒ `GATE FAIL`;
(6) otherwise **`GATE REACHED`**, with **GCI at Fs = 1.25** and the observed order
printed.

---

## 9. Completion and convergence, and the field classes (L-342)

### 9.1 Strict completion (CLAUDE.md rule 4), at EVERY level of BOTH arms

1. **rc = 0**, read from `RUN_RC.<level>.<arm>` at the run root (canonical) or
   `<level>/RUN_RC.txt` (fallback). Both are written by one statement inside the
   launcher from the `$?` it captured at the solve, so they cannot disagree.
2. an **`End`** line in `log.simpleFoam`;
3. **last time == the level's registered `endTime`** (3000 / 3000 / 6000) — meaningful
   because `fvSolution` carries no `residualControl`;
4. **`U` and `p` present at `endTime`**, resolved as `X` **or** `X.gz`
   (Amendment 5 item 4);
5. **`ExecutionTime` line count == `endTime`**;
6. **AGE GUARD: every field at `endTime` strictly newer than the case's own `0/U`**,
   which the launcher `touch`es **last, immediately before the solver** — after the
   mesh, after the sampler, after the cap arithmetic, with nothing between that line and
   the solve that writes a file.

### 9.2 Iterative convergence, registered in advance (both clauses, every level, both arms)

- **residuals**: the initial residual of `Ux`, `Uy` and `p` at the final iteration is
  **< 1e-6**;
- **plateau**: the per-iteration probe of v_θ(35 mm) has peak-to-peak **< 1e-6 m/s over
  a FIXED window of the last 600 samples**, with a **minimum-sample refusal at 600**
  (below it: `CANNOT_TELL`, never a pass) and a **null-range refusal** (peak-to-peak
  exactly zero is refused — a dead field and a perfectly converged one look identical to
  a tolerance). **The realised sample count is recorded in the grading JSON.** This is
  template Amendment 4 items 1–5; the window is **fixed, not fractional**, so its sample
  count is knowable at freeze time and cannot move when `writeInterval` does.

The plateau series comes from a `probes` function object writing every iteration. **Those
are cell values and are never the graded number** — they answer *has it stopped moving*.
The graded number is always the `gateAxis` `sets` sample at `endTime`, point-interpolated.

**A level failing either clause makes the rung `NOT A RESULT`** (rule 5 step 1), before
the triple is classified.

### 9.3 Field classes (L-342, Sanaa's universal rule of 2026-08-26T16:15Z)

**PHYSICS-CRITICAL** — a gate may read these; a failure refuses or votes `NOT A RESULT`:
the solver rc; the `End` line; last time == `endTime`; the declared fields at `endTime`;
the `ExecutionTime` count; the age guard; the residual and plateau clauses; the mesh
birth certificate; the launch-time sha freeze; **the three GPU tells, `gpusample.txt`,
the forced-CPU control and the one-MPI resolution** — for this family limb A is
physics-critical *because it is the object under verification*.

**INFRASTRUCTURE** — **never refused on, never voids a verdict**; absent or malformed is
a labelled `WARNING(INFRASTRUCTURE)` and the grade proceeds on the physics artifacts:
`COST.txt` and every GPU-hour and core-minute figure; `LAUNCH_RECORD.txt`'s non-sha
bookkeeping lines; `CAP_EXCEEDED.txt`; contention and status files; memory figures, pids,
sids and bookkeeping mtimes; the host line. **An absent infrastructure field is NOT
MEASURED and never refuses.**

**The one deliberate asymmetry, and it is the supervisor's addendum:** an **absent**
`RUN_RC` is *not* a voiding refusal. rc is physics-critical, so the level cannot be a
pass — the verdict becomes **`NOT A RESULT` and the physics is still read and PRINTED**.
A **present and non-zero** rc *is* an incomplete run and refuses. Selftest checks 2, 3
and 8 drive all three branches.

---

## 10. Planted-zero control (CLAUDE.md rule 3), SIZED PER CHANNEL (L-340)

**The gate has FOUR channels — v_θ at r = 20, 25, 30 and 35 mm — and the control is run
ONCE PER CHANNEL.** For each radius the comparator copies the finest GPU level's
`gateAxis` output to a temporary tree, **adds PLANT = 1.234 × 10⁻³ m/s to that row's
`U_y` column**, **reads the file back from disk**, and re-runs the *same* extraction. It
refuses (exit 2) unless the extracted v_θ at that radius moves by **exactly PLANT** (to
1e-15 m/s) **and no other radius moves at all**. The run tree is never modified.

**Why per channel, and the sizing checked rather than assumed.** **L-340 cost this team
a completed three-level run**: VMFL011's control planted one point into an **RMS over
401 points**, where a single-point plant is diluted by ~1/√N, and the comparator refused
a **working** reader. **Every channel here is a POINT reader** — one sampled row in, one
number out, so the plant-to-read mapping is 1:1. The sizing is stated as a number:
against the **smallest** gated value, v_exact(35 mm) = 4.5478 × 10⁻³ m/s, the plant is
**27 % of the signal** — twelve orders above the 1e-15 read-back tolerance and far above
the 0.1·plant threshold that L-340 warns about. **The comparator asserts this ratio
> 0.1 as a selftest check**, so the sizing is a reading and not a belief.

**The control's own REFUSAL PATH is driven, not assumed** (Amendment 6a item 3): the
selftest hands the control a deliberately **BLIND** reader — one that returns the
pre-plant values whatever is on disk — and requires it to **refuse with exit 2, under
`python3 -O`**. A reader not shown able to *miss* a plant is not shown able to see one.
The **negative arm** is also driven: the same reader on an *unplanted* copy must report
no movement.

---

## 11. Cost (CLAUDE.md rule 12; `COST_BASIS.md`)

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × RANKS / 60 |
| work | 6 solves = 3 levels × {GPU arm, forced-CPU arm}; 1,024 + 4,096 + 16,384 cells; 3000 / 3000 / 6000 SIMPLE iterations |
| **GPU-hour estimate** | **0.40 GPU-h** for the whole case (both arms), = wall-hours the instance is up for it |
| basis of that estimate | **DERIVED, NOT MEASURED.** The CPU parent measured 2 s / 13 s / 104 s at `endTime` 3000 on the lab box (`VMFL001/RESULTS.md` §6) ⇒ ≈ 223 s per arm here with L3 at 6000; ×2 arms = 446 s; a **3× allowance** for the instance's 4 vCPU and for petsc4Foam's per-solve setup on meshes this small ⇒ ≈ 1,340 s ≈ **0.372 h**, rounded up to 0.40 |
| **GPU-hour CAP** | **2.0 GPU-h**, **ENFORCED in the executable path** by `timeout` per solve, drawing the remaining budget down across solves (`timeout_s = remaining_core_min × 60 / RANKS`). **An overrun STOPS the run and does not get a new budget** — the launcher writes `CAP_EXCEEDED.txt` and stops. 5× the estimate: a runaway guard, not a budget gate |
| **core-minutes** | **24.0 core-min** = **12.0 (CPU arm)** + **12.0 (GPU-arm host rank)**. The GPU arm still occupies one host rank for its wall time, and that is counted rather than treated as free |
| CPU-arm cap | **40 core-min**, **ENFORCED** (the launcher stops when the CPU arm's accumulated core-minutes reach it) |
| **dollars, GPU** | **$0.32 DERIVED** (0.40 GPU-h × $0.8048/GPU-h). **NOT MEASURED** |
| **dollars, CPU-arm core-minutes** | **$0.0103 DERIVED** (12.0 core-min ÷ 60 × $0.0513/core-h). Recorded for comparability; on this instance the CPU arm's time is already inside the GPU-hour meter and is **not a separate charge** |
| `cost_basis` label | GPU-hours at the **AWS PUBLISHED PRICE LIST** $0.8048/GPU-h for `g6.xlarge` us-east-2, retrieved 2026-08-23 (`GPU_CAPABILITY_STATE.md` §9, rateCode `JRTCKXETXF`); CPU core-hours at the **owner-stated** $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22). **Dollars are DERIVED, NOT MEASURED — this box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **The CONSOLE figure is STILL OWED and supersedes.** |
| **the build's GPU-hours are a FAMILY line, not this case's** | `COST_BASIS.md` books the one-time toolchain build (order **1–3 GPU-h**, **$0.80–$2.41 derived**) as a **family-level** line amortised across all ten VMFLGPU cases, **not** charged to VMFLGPU001. Stated here so a reader adding this case's 0.40 GPU-h to the family total does not double-count it, and so nobody reads 0.40 as the cost of *reaching* a GPU verdict for the first time — **it is not**. `[lab-attributed]` |
| authorisation | GPU spend is **outside** the 2026-08-21 CPU blanket (`GPU_CAPABILITY_STATE.md` §6); this line is a per-item cost under the standing authority, **not a new ceiling** (rule 9) |
| calibration | at completion, actual GPU-hours (instance up-time, reported-by-owner) and actual core-minutes from `RUN_RC.*` / `COST.txt` against these estimates, with ratio and gap attribution (contention / waste / misprediction, **waste named separately**), one row appended to `docs/COST_CALIBRATION.md` (rule 12). **A completion report without that row is incomplete.** |

---

## 12. The grading path, frozen (`VERIFICATION_CHARTER` §2d)

| what | path (repo-relative) | blob sha |
|---|---|---|
| **comparator** | `cases/ansys_verification/VMFLGPU001/grade_vmflgpu001.py` | **`f4b07b7fc59d9facd46ad91d3ad9848d33c4f098`** |
| **launcher** | `cases/ansys_verification/VMFLGPU001/run_vmflgpu001.sh` | **`a1995abc8b3b0b0a64d107a8ff70b34041397277`** |
| `0/U` (BCs + age-guard marker) | `case/0/U` | `fd65259adff3152407a40e4decf6191d6dd2e350` |
| `0/p` | `case/0/p` | `10de59431bdcf5d7d1d27e29f219b49f32e5da1a` |
| `constant/transportProperties` | `case/constant/transportProperties` | `bd490e1105d34e8672cd5251dabd27614d4d5051` |
| `constant/turbulenceProperties` | `case/constant/turbulenceProperties` | `6d5b3af67a1fa836a5a9ac06235d34db6fbdd73e` |
| `system/fvSchemes` | `case/system/fvSchemes` | `b22740ae317a6eb5ca7e67feca94699e27e15dcf` |
| `system/fvSolution.template` | `case/system/fvSolution.template` | `9e7343a9769b70d4c7b5c2ab6e3ed3e190982010` |
| `system/controlDict.template` | `case/system/controlDict.template` | `31c985a67075a2060c46d5b1030531f35eb84295` |
| `system/blockMeshDict.template` | `case/system/blockMeshDict.template` | `45286819aa46b5df7fc0b938da1694ebdeb03068` |

**This document and all of the above are committed in ONE commit, before any compute.**
`0/U` and `system/fvSchemes` carry the **same blob shas as the CPU parent's frozen
case** — the provenance is a hash identity, not a claim.

**LAUNCH-TIME FREEZE CHECK (template Amendment 2, non-droppable).** Before any solver,
`run_vmflgpu001.sh` resolves `HEAD:<prereg>` and `HEAD:<comparator>` on the instance's
own clone, hashes both files on disk, and **aborts explicitly** (`|| { echo ABORT…;
exit 1; }`) unless each disk blob equals its HEAD blob; the four shas and the HEAD commit
are written into `LAUNCH_RECORD.txt`, and the comparator **refuses** to grade a run whose
`LAUNCH_RECORD.txt` is absent, carries no sha lines, or records a disk/HEAD mismatch.
**Driven on the lab box at 2026-08-26T17:26:10Z**: with the smoke gate satisfied by
fixtures, the launcher reached the freeze check and printed
`ABORT: cases/ansys_verification/VMFLGPU001/PREREGISTRATION.md is not committed at HEAD
-- the freeze is the evidence`, exit 1. **An unverified freeze is no freeze.**

### 12.1 Comparator `--selftest`, run at this freeze

**37 checks, ALL GREEN, IDENTICAL under both interpreters — run at the comparator blob
above, with zero solver compute:**

| interpreter | checks | result | rc |
|---|---|---|---|
| `python3` | **37** | **`SELFTEST GREEN: 37 checks, each shown able to fail.`** | **0** |
| `python3 -O` | **37** | **`SELFTEST GREEN: 37 checks, each shown able to fail.`** | **0** |

**`assert` sweep (template Amendment 6 item 4), the check that actually finds these:**
`grep -nE '^[[:space:]]*assert[[:space:]]'` over the comparator returns **zero hits**,
and the comparator's own **AST counter reports 0 `ast.Assert` nodes** while being shown
able to count a planted one. **No `assert` carries a refusal, a guard, a control or a
gate anywhere in this instrument** (L-332). Every refusal is `sys.exit(2)`; the verdict
vocabulary guard is an explicit refusal (`V0`), so rule 1's enforcement point survives
`-O`.

**What each of the 37 checks establishes**, grouped:

- **the instrument itself (2):** zero `assert` nodes; the AST counter proves it can see
  a planted one.
- **the reference arithmetic (3):** v_exact(20 mm) = 0.0151201 to 6 s.f.; v_θ(R_i) = ω R_i
  exactly; v_θ(R_o) = 0.
- **the Roache classifier (6):** the degenerate equally-spaced triple is `STAGNANT` with
  **no GCI**; a genuine second-order family is `CONVERGING` with p → 2 to 1e-3;
  `OSCILLATORY`; `DIVERGENT`; **and an order below P_MIN = 0.05 is not `CONVERGING` and
  prints no GCI**.
- **the tells (4):** tell 3 sees `seqaijcusparse` and does **not** accept `seqaij`;
  tell 2 sees a PID holding device memory and does **not** fire on an empty GPU.
- **end-to-end verdicts (5):** a clean in-band run reaches the ceiling `GATE REACHED`;
  a GPU arm differing from the forced-CPU arm is `GATE FAIL`; **a triple below P_MIN
  routes to `NOT A RESULT` end to end under `-O` with `GCI_fine =` appearing nowhere**;
  the equally-spaced triple does the same; a CONVERGING triple 3.0 % from the closed form
  is `GATE FAIL`.
- **L-342, driven both ways (3):** a **corrupt** `COST.txt` and a **missing** `COST.txt`
  each leave the verdict **unchanged**; an **absent** `RUN_RC` gives `NOT A RESULT` with
  the physics printed, **not** a voiding refusal.
- **refusals driven under `python3 -O` (8):** a missing `End` line; a missing
  `gpusample.txt` (tell 2); a forced-CPU control that reports GPU work; the vocabulary
  guard; a blind planted-zero reader; a plateau shorter than the 600-sample minimum; a
  null-range plateau; a field at `endTime` older than `0/U`; a GPU arm whose tells do not
  fire (`NOT A RESULT`, exit 2, never a pass).
- **the planted zero (4):** it fires on **all four channels**; the plant is
  supra-threshold on the smallest channel (L-340); the negative arm sees no move; the
  blind-reader refusal fires.
- **the reference identity (1):** the lab-evaluated closed form and the manual's printed
  column differ by **1.15 % at r = 35 mm**, so the two are demonstrably not
  interchangeable and the choice of reference in §6.3 is a real choice.

**What the comparator has NOT been exercised on, stated plainly.** No solver has run, so
it has never seen real `simpleFoam` + petsc4Foam output, real `-log_view` text, or a real
`nvidia-smi` sample. **Its fixtures were written by its author to its author's belief
about the writer, and that is exactly the shape that cost VMFL001 run 1 (L-286.)** Two
things reduce, and do not remove, that exposure: the sampled-file reader is written to
v2606's **measured real** layout — headerless `<setName>_<fields alphabetical>.xy`,
columns `x y z` then the fields in that order — which is the layout `VMFL001/RESULTS.md`
§3 recorded from a real run; and the three tells' regexes are **byte-equivalent to
`smoke_test_gpu_path.sh`'s**, so the comparator and the smoke test cannot disagree about
what a tell is. **If the comparator cannot parse the real output it REFUSES and the rung
is `NOT A RESULT` — it never guesses a column.**

---

## 13. The launcher, and the guards it carries (template Amendment 3, all six)

`run_vmflgpu001.sh` (blob above) runs **on the GPU instance**, never on the lab box, and
**grades nothing**.

1. **Launch-time freeze verification** of the pre-registration AND the comparator against
   `HEAD`, each gating explicitly, shas recorded — §12.
2. **Cap enforcement in the executable path**, per solve and in total, by the general
   formula with `RANKS` in it — §11.
3. **No `set -u`, with the reason named** in the header: OpenFOAM v2606's `etc/bashrc`
   dereferences `WM_PROJECT_DIR` at its line 184 before assigning it (measured rc 127),
   and two frozen launchers of this team shipped `set -u` and aborted before any compute.
   **No `set -e` either** — it does not gate at a Bash tool's top level; every step gates
   explicitly with `|| { echo "ABORT: …"; exit 1; }`.
4. **Planted-zero control** — in the comparator, §10.
5. **Mesh birth certificate** — `checkMesh` + exact cell count, both arms, every level.
6. **A pre-flight test that EXERCISES THE LAUNCHER ITSELF** — §13.2.

**Also carried:** a **driven** time-directory test (`[[ $n =~ ^[0-9]+([.][0-9]*)?…$ ]]`,
never a `[0-9]*` glob, which would match `0.orig` — L-339); **consumer-side field
completeness** enumerated from `fvSolution`'s solver blocks **intersected with the
closure named in `constant/turbulenceProperties`**, minus `phi`, with `X`/`X.gz`
resolution (Amendment 5 item 1 as refined by 5a — which matters here because `laminar`
creates no turbulence fields and a regex-surface reading would demand them);
`mat_type`/`vec_type` verified in the materialised `fvSolution` so **an arm cannot be the
wrong arm**; a refusal if any level directory of either arm already exists; and the
concurrent `nvidia-smi` sampler started **before** the solver so it cannot miss the start
of a short solve.

### 13.1 What was CHANGED in the peer lane's uncommitted draft, and why

The launcher and comparator were left uncommitted by a peer lane killed at ~16:46Z. They
were **inspected, never reverted** (rule 10). Both were good; five things were changed,
each named here because a silent repair is not a repair:

1. **The smoke gate did not exist.** Added as STEP 0: **refuses (exit 2) at zero
   compute** unless `STATUS.smoke` reads `smoke_rc=0` **and** `TOOLCHAIN_MANIFEST.txt`
   **and** `env.sh` exist. Without it the case could have run six solves on an unproven
   path and discovered it only at grading.
2. **The cap was enforced by a watchdog that REPORTED and never stopped anything.** The
   draft declined `timeout` on a recorded note that *"`setsid` and `timeout` were
   MEASURED returning 0 for every outcome (4225ef0c, 83769288)"*. **That note is about a
   backgrounded/`setsid` invocation, not about `timeout` itself.** Rather than trust
   either reading, `timeout` was **driven**: MEASURED on the lab box 2026-08-26 (GNU
   coreutils 9.4), `timeout 10 bash -c 'exit 7'` → **7**, `timeout 1 bash -c 'sleep 3'`
   → **124**, a clean child → **0**. The cap is now `timeout` with **the rc captured
   inside the script**, and **the launcher re-drives that measurement on its own host at
   STEP 0c and refuses (exit 2) if the host disagrees** — so the guard is never trusted
   on a note. CLAUDE.md rule 12 requires that an overrun **stops** the run; a file that
   says an overrun happened is not that. The **CPU-arm core-minute cap is now enforced
   too**, having previously been a number written into `COST.txt` and consulted nowhere.
3. **The rc was written to one place.** It is now written to
   **`RUN_RC.<level>.<arm>` at the run root** *and* `<level>/RUN_RC.txt`, by one
   statement, plus an `rc` line appended to `LAUNCH_RECORD.txt`; the comparator reads the
   run-root copy first. The run-root name carries the level and the arm, so a record
   cannot be attributed to the wrong arm by being moved.
4. **The one-MPI condition did not exist**, because the defect had not yet been measured
   when the draft was written. Added as STEP 2b, resolved rather than declared — §4.2.
5. **In the comparator: limb C gated against the manual's rounded printed column.** It
   now gates against **the closed form the comparator evaluates itself** (§3, §6.3), with
   the printed column demoted to a printed diagnostic; **the planted-zero control was
   single-channel** and is now **per channel** (§10, L-340); and **the P_MIN floor and
   the STAGNANT clause were checked only inside the classifier** and are now **driven end
   to end through the grader under `-O`**, with `GCI_fine =` required to be absent.

**Nothing else in either file was altered**, and neither had been committed, so no freeze
was broken by any of it.

### 13.2 The launcher's own pre-flight, DRIVEN on the lab box (zero compute)

Amendment 3 item 6 exists because *"a comparator selftest proves the GRADER; a scratch
smoke proves the CASE; the launcher is the one artifact nothing was testing."* Run at
2026-08-26T17:25:10Z against a fixture `BUILD_ROOT`, with **no solver, no `blockMesh` and
no GPU**:

| driven condition | required | **observed** |
|---|---|---|
| `STATUS.smoke` absent | refuse, exit 2 | **exit 2** |
| `STATUS.smoke` reads `smoke_rc=1` | refuse, exit 2 | **exit 2** |
| `smoke_rc=0`, `TOOLCHAIN_MANIFEST.txt` absent | refuse, exit 2 | **exit 2** |
| manifest present, `env.sh` absent | refuse, exit 2 | **exit 2** |
| all three present | pass the gate, drive `timeout`, then stop at the freeze check | **`SMOKE GATE PASSED` → `CAP MECHANISM DRIVEN: timeout passes a child rc through (7) and reports an overrun as 124 on this host` → `ABORT: …PREREGISTRATION.md is not committed at HEAD`, exit 1** |

`bash -n` is syntax-only and a blob check is content-only; **only execution could show
these**, and it did. **The fifth row is the load-bearing one: the gate opened, the cap
mechanism proved itself on a real host, and the freeze check then refused — which is the
launcher behaving exactly as registered when the pre-registration is not yet committed.**

---

## 14. What this rung will NOT claim

- **Nothing about Ansys.** Ansys Fluent GPU's numbers are context (§3.2). This box has no
  Fluent; `vt001.msh` and `vmfl001.jou` were not run, and no VM2026R1 archive was opened.
- **Nothing about the transport properties**, beyond the byte-identity of the parent's
  frozen `transportProperties` blob — the gated quantity provably cannot see μ or ρ (§7).
- **Nothing about GPU performance.** No speed-up is claimed, sought or gated. This rung
  asks whether the GPU path produces **the lab's own CPU answer**, not whether it
  produces it faster. A GPU arm slower than the CPU arm passes every limb.
- **Nothing about grid independence beyond the triple** — the verdict is a statement
  about the finest level, with GCI printed as the uncertainty channel.
- **Nothing about the toolchain build's success.** At this freeze the build is in flight
  and `STATUS.smoke` does not exist. §4 registers the gate; it reports no result.
- **Nothing about a partial-coverage case.** Here `petsc4Foam` carries **both** linear
  systems the solver has (pressure and momentum), so the GPU-path coverage of this case
  is **complete**, unlike VMFLGPU008/009/010 in the family draft. Stated because the
  family requires coverage to be labelled honestly.

## 15. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). **The ceiling is `GATE REACHED`** and that is this
team's success, not a shortfall (Sanaa: *"Anything gate reached for that team means we
reached ansys, which is good enough."*). The comparator checks its own verdict string
against that list **with an explicit refusal, not an `assert`**, so the check survives
`python3 -O`. Whatever the answer, the row lands in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`; a `GATE FAIL` is a finding
that is never removed, re-labelled or softened to `PENDING` (charter §6).
