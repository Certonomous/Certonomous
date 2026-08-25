# GPU BUILD RECIPE — the lab's GPU solver path for the VMFLGPU family

**Drafted by `ansys-lane-opus48` (running as `claude-opus-4-8[1m]`) for the
`ansys-verification-supervisor`, 2026-08-25T20:28Z. DRAFT for the supervisor's and
Sanaa's offline review.**

**ZERO COMPUTE. 0.0 core-minutes, 0.0 GPU-hours. No instance was booted, started,
or contacted to produce this document. No solver was run.** This is the FIRST ARROW
of Sanaa's binding sequence — *build recipe, script and smoke test prepared and
REVIEWED OFFLINE → boot → build → smoke test → SNAPSHOT THE AMI → all 10 VMFLGPU
cases → stop instance* — and it stops at the first `→`. Nothing here authorises a
boot; the boot is Sanaa's decision after she has read this.

**NOT FILED ANYWHERE. Nothing in this document leaves the box** (`CLAUDE.md` rules
7, 8). The manual is proprietary Ansys documentation.

---

## 0. What is actually under verification (Sanaa's ruling, 2026-08-25)

Sanaa corrected this team's reading of the VMFLGPU family, verbatim as relayed by the
supervisor:

> "the ansys-verification team runs the entire Ansys verification folder, VMFLGPU
> included, meaning the GPU solver path is actually verified — not CPU physics
> re-measured on rented silicon."

**The thing under verification is THE GPU SOLVER PATH**, not the parent physics. Two
prior records that called the family low-value on the ground that it re-measures
parent physics (`docs/ansys_verification/CASE_MAP.md`, `docs/LAB_STATE.md`) are
corrected by dated foot-amendment of this date; see those files.

**Honest scoping of what "the GPU solver path" can mean in THIS lab.** The manual's
`Solver` line for every VMFLGPU case reads **`Ansys Fluent GPU`**. This box has no
Ansys licence — no `fluent`, no Fluent-GPU — so the lab **cannot** run Ansys Fluent
GPU and this team **never** makes a statement about Ansys's own solver (charter §2).
The GPU solver path this lab *can* verify is **the lab's own OpenFOAM solver with its
linear system solved on the GPU**. A VMFLGPU verdict from this team therefore reads:
*the lab's OpenFOAM-on-GPU linear-solver path reproduces the manual's reference
result within the frozen band, AND the linear solve provably executed on the GPU.*
Both halves are the gate. The first half without the second is CPU physics on rented
silicon — exactly what Sanaa ruled out.

---

## 1. The instance and its hardware (from the record, not booted)

All facts below are from `docs/GPU_CAPABILITY_STATE.md` §8 (metadata-verified over
SSH on 2026-08-23) and the haiku `GPU_TOOLCHAIN_INVENTORY.md` of 2026-08-25. The
instance is **STOPPED** (§10, stopped by Sanaa 2026-08-24) and stays stopped for the
whole of this task.

| item | value | provenance |
|---|---|---|
| instance type | `g6.xlarge` (4 vCPU) | §8 metadata-verified |
| GPU | 1× NVIDIA **L4**, 23034 MiB | §8 `nvidia-smi` |
| GPU architecture | **Ada Lovelace, compute capability 8.9 (`sm_89`)** | NVIDIA Ada compatibility guide; L4 is the sm_89 datacentre part |
| NVIDIA driver | **595.91.07** | §8 `nvidia-smi` |
| base AMI | Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.13 (Ubuntu 26.04), `ami-0dda0fd1cccbe2c28` | §8 |
| root volume | 96 GB, 83 GB free at launch | §8 `df` |
| canonical private IP | 172.31.44.162 (persists across stop/start) | §8 |
| public IP | **ephemeral — changes on stop/start; never recorded as canonical.** The task's `3.15.199.152` is a public IP and is transient | §8 rule |
| region / AZ | us-east-2 / us-east-2c | §8 |

**Two things I could NOT verify without booting, and do not pretend to have:**
1. **The CUDA toolkit version actually present on the DLAMI.** Driver 595.91.07 is
   forward-compatible with a recent CUDA major, but a Deep-Learning AMI commonly
   ships a *CUDA runtime for PyTorch* and **not necessarily the full `nvcc` toolchain**
   PETSc needs to compile device code. The build script therefore **detects `nvcc`
   and installs the CUDA toolkit if absent** rather than assuming it (§4, step 3).
2. **Whether the `petsc4Foam` module version matches OpenFOAM v2606.** Resolved at
   build time by pinning the module tag to the OpenFOAM release the box runs; if the
   pin fails to compile, the build **aborts and reports** rather than silently
   dropping to a mismatched tag (§4, step 6).

---

## 2. Route selection — SELECTED, with the rejected alternative named

### SELECTED: `petsc4Foam` (the OpenFOAM `petsc` external-solver module) + PETSc built `--with-cuda`, cuSPARSE `aijcusparse`/`cuda` backend, on the lab's own OpenFOAM v2606

The GPU solver path is: OpenFOAM v2606 assembles each linear system in its native LDU
form on the CPU exactly as it does for the CPU cases; the `petsc4Foam` module converts
LDU→CSR and hands the system to **PETSc**, which is built against CUDA so the matrix
and vectors live in **GPU device memory** (`-mat_type aijcusparse -vec_type cuda`) and
the Krylov solve + preconditioner run **on the L4**. Only the linear solve is offloaded;
the discretisation, boundary conditions, models and time-stepping are byte-for-byte the
lab's existing OpenFOAM.

**Why this route, five reasons, each load-bearing:**

1. **It verifies the GPU path without changing the physics.** The discretisation is the
   lab's own v2606 — identical to the CPU cases — and only the linear algebra moves to
   the GPU. That is precisely "the GPU solver path verified, not new physics" (Sanaa).
2. **It covers all ten cases with one build.** `petsc4Foam` is a drop-in linear-solver
   backend selected *per equation in `fvSolution`* (`solver petsc;`), not a per-solver
   GPU port. So `simpleFoam`, `icoFoam`, `buoyantBoussinesqSimpleFoam`, `laplacianFoam`,
   `rhoSimpleFoam`, `chtMultiRegion*`, `interFoam` and `fvDOM` all reach the GPU through
   the same module — no ten separate solver ports.
3. **It is maintained against modern CUDA and the exact hardware.** `petsc4Foam` is the
   OpenFOAM HPC Technical Committee's external-solver interface; PETSc's CUDA backend
   targets Ada `sm_89` under CUDA 12/13. (Cineca / 8th OpenFOAM Conference documents the
   GPU offload; the `ldu2csr` conversion and CG+AMG pressure solve are the documented
   path.)
4. **GPU execution is provable and a silent CPU fallback is detectable** — the smoke-test
   requirement (`smoke_test_gpu_path.sh`, and §5 here). PETSc's `-log_view` reports
   device flops and `GpuToCpu`/`CpuToGpu` transfer counts; `-log_view :...:ascii_info`
   and `-mat_type` echo the active types; `nvidia-smi` shows the solver PID holding
   device memory. A run that silently fell back to CPU shows **zero GPU flops** and
   **no PID on the GPU** — the smoke test fails on exactly that.
5. **It reuses the lab's own solver.** No re-validation of a foreign discretisation is
   needed; the CPU parents already exercised these solvers, so a GPU/CPU delta isolates
   the linear-algebra path, which is the object under test.

### REJECTED: RapidCFD (full-GPU OpenFOAM-2.3.1 fork)

RapidCFD runs the *entire* solver on the GPU, which is superficially a stronger "GPU
solver path." It is rejected, for reasons that are build-blocking and physics-blocking:

- **Build-blocking on this hardware.** RapidCFD's CUDA code is CUDA-7-era: it uses Thrust
  APIs removed after CUDA 10 and hardcodes `sm_20`/`sm_30` arch flags. Compiling against
  the DLAMI's CUDA 12/13 for Ada `sm_89` requires patching nvcc arch flags and rewriting
  removed Thrust calls — a porting project, not a build, and one whose success cannot be
  asserted offline.
- **Physics-blocking for this family.** RapidCFD's OpenFOAM-2.3.1 base does not carry the
  modern radiation (`fvDOM`, S2S `viewFactor`), anisotropic-conduction and CHT machinery
  that VMFLGPU004/005/008/010 need in the same form the lab's v2606 provides. Verifying a
  *different* solver's radiation is not verifying the lab's GPU path.

RapidCFD is recorded here as **considered and rejected**, so the selection is a choice on
the evidence, not an omission.

### ESCALATION WITHIN THE SELECTED ROUTE (not a second build): PETSc→AmgX for a stiff Poisson solve

If cuSPARSE CG with PETSc's GPU algebraic multigrid (`-pc_type gamg`, or `hypre` BoomerAMG
on device) converges poorly on the pressure Poisson solve for the harder cases (VMFLGPU005
turbulent buoyant, VMFLGPU008 radiation), the fallback is to route the pressure solve
through **NVIDIA AmgX** via PETSc's AmgX interface — same `petsc4Foam` module, a different
preconditioner selected in the PETSc options file. This is a runtime option, not a
separate toolchain; the build script builds PETSc `--download-amgx` (or system AmgX) so the
option exists without a second build.

---

## 3. VERDICT on route viability

**SELECTED — VIABLE, with named open items.** A defensible GPU solver route exists for
this box's L4 (`sm_89`) + driver 595.91.07 + modern CUDA: `petsc4Foam` + PETSc-CUDA on
OpenFOAM v2606. **This is NOT `BLOCKED`** — `BLOCKED` would be dishonest, because a real
route exists and is buildable by the script in `build_gpu_solver.sh`.

**But the route is not yet PROVEN on this box, and I do not claim it is.** The three
things that can only be settled by booting and building — (a) the CUDA toolkit is present
or installable, (b) PETSc builds `--with-cuda` clean for `sm_89`, (c) `petsc4Foam`
compiles against v2606 — are exactly what the build + smoke sequence *after* review is for.
Sanaa's own sequence puts the offline review first for this reason. My verdict is: the
recipe is ready to review; the proof is the build, which is the second arrow.

---

## 4. The build, step by step (mirrored exactly by `build_gpu_solver.sh`)

Assumes a **fresh** g6.xlarge from the DLAMI, user `ubuntu`, root volume with ≥ 40 GB
free. Every step logs to `~/gpu_build/build.log` and gates on failure. The script is
**idempotent**: each step checks for its own completion marker and skips if already done,
so a re-run after a partial failure resumes rather than rebuilds.

1. **Preflight & environment capture.** Record `nvidia-smi`, `nvidia-smi -L`, driver
   version, `uname -a`, `df -h`, free memory, and the DLAMI id into the log. Assert an
   L4 is visible (`nvidia-smi -L | grep -q 'NVIDIA L4'`) — abort if not: a build on the
   wrong GPU wastes the arch flags.
2. **OS build prerequisites.** `apt-get` `build-essential gfortran cmake git flex bison
   zlib1g-dev libopenmpi-dev openmpi-bin libfftw3-dev libscotch-dev libptscotch-dev
   pkg-config`.
3. **CUDA toolkit — detect, install only if absent.** If `nvcc --version` succeeds,
   record the version and use it. If not, install the CUDA toolkit matching the driver
   (network install of the toolkit only, not a driver — the DLAMI's driver stays). The
   **arch is pinned to `sm_89`** for the L4 in every device-code build below.
4. **OpenFOAM v2606 on the instance.** The lab box runs v2606 at
   `/usr/lib/openfoam/openfoam2606`. On the GPU instance, install the **same** version
   (openfoam.com apt repo `openfoam2606-default`, or build from the v2606 source pack) so
   the discretisation is identical to the CPU parents. Source its `etc/bashrc`. **No
   `set -u`** anywhere that sources the bashrc — v2606's bashrc dereferences
   `WM_PROJECT_DIR` before assigning it and dies under `set -u` (measured hazard, this
   team's Amendment 3 to `PREREG_TEMPLATE.md`).
5. **PETSc `--with-cuda`.** Clone PETSc (pinned release tag), configure with
   `--with-cuda --with-cuda-arch=89 --download-fblaslapack --download-hypre
   --download-amgx --with-mpi-dir=<openmpi> --with-precision=double`, `make`, `make
   check`. The `make check` includes a CUDA example; its pass is the first evidence the
   GPU stack compiles and runs. Record `PETSC_DIR`, `PETSC_ARCH`.
6. **`petsc4Foam` module.** Clone the OpenFOAM `modules/petsc-foam` (a.k.a.
   `petsc4Foam`) at the **tag matching v2606**; `./Allwmake`. If it fails to compile
   against v2606, **abort with the compiler error captured** — do not fall back to a
   mismatched tag. On success it produces `libpetscFoam.so` on `$FOAM_USER_LIBBIN`.
7. **Record the toolchain manifest.** Write `~/gpu_build/TOOLCHAIN_MANIFEST.txt`: driver,
   CUDA version, OpenFOAM version, PETSc git sha + PETSC_ARCH, petsc4Foam git sha,
   `sm_89`, and `sha256` of `libpetscFoam.so`. This manifest is what the AMI is snapshotted
   with (§ AMI procedure) so a restored instance can prove it carries the same toolchain.
8. **Smoke test.** Run `smoke_test_gpu_path.sh` (§5). Only a PASS here licenses the AMI
   snapshot.

**Gating discipline (measured hazard, restated because it is load-bearing).** `set -e`
does NOT gate at the top level of a Bash tool call, and `( set -e; … )` does not gate
either. Every step in `build_gpu_solver.sh` therefore ends with an explicit
`|| { echo "ABORT: <step>"; exit 1; }`. An executed script gates; a sourced one does not,
so the script must be **executed** (`bash build_gpu_solver.sh`), never `source`d.

---

## 5. The smoke test — proving the GPU SOLVER PATH ran ON THE GPU

Full script: `smoke_test_gpu_path.sh`. It runs the smallest VMFLGPU case (VMFLGPU001,
concentric-cylinder Couette, a few thousand cells) with `petsc4Foam` selected in
`fvSolution` and `-mat_type aijcusparse -vec_type cuda` in the PETSc options, and it
**must be able to FAIL**. It proves three things a mere "binary exists" or "case
completed" check cannot:

**How a GPU solve is told from a silent CPU fallback — the three independent tells,
all of which must fire, or the smoke test FAILS:**

1. **PETSc reports device work.** With `-log_view` and `-log_view_gpu_time`, the run
   prints non-zero **GPU flops** and non-zero **CpuToGpu / GpuToCpu** transfer counts for
   the `KSPSolve` stage. A CPU fallback prints **zero** GPU flops. The smoke test greps
   the log and **fails on zero**.
2. **The solver PID holds GPU memory during the solve.** A background sampler runs
   `nvidia-smi --query-compute-apps=pid,used_memory --format=csv` while the solver is
   mid-solve and asserts the solver PID appears with non-zero device memory. A CPU
   fallback leaves the GPU **idle** — no PID, no memory. The smoke test **fails on an
   empty GPU**.
3. **The active PETSc types are the CUDA types.** `-ksp_view` / `-mat_view ::ascii_info`
   echo the matrix type actually used; the test asserts it is `aijcusparse` (or `mpiaijcusparse`),
   not `seqaij`/`mpiaij`. A configuration that quietly dropped to a CPU matrix type is
   caught here even if the other two somehow passed.

**Why all three, not one.** Any single tell has a failure mode: `-log_view` can be
mis-parsed; `nvidia-smi` sampling can miss a very short solve; a type string can be set
without the kernel actually running. Requiring **all three** — device flops, a live PID
on the GPU, and CUDA matrix types — means a silent CPU fallback cannot pass, which is the
whole point. **The plant that proves the test can fail:** the smoke test is run a second
time with `-mat_type aij -vec_type standard` forced (CPU types) and MUST report FAIL on
tell 1 and tell 3 — a smoke test that "passes" the forced-CPU control is broken and
refuses to certify anything (this mirrors the lab's planted-zero discipline, rule 3: a
reader not shown able to see the negative case is not evidence).

**A second, physics tell (correctness, not execution).** After the GPU path is proven to
have run on the GPU, the smoke test checks the VMFLGPU001 tangential velocity at the four
manual radii against the manual's target (0.0151 / 0.0105 / 0.0072 / 0.0046 m/s) to a
loose 5 % — not the graded gate (that is the case's own frozen comparator), just a sanity
floor that the GPU solve produced physical numbers and not NaNs. A GPU solve that runs on
the GPU but returns garbage is still not a working path.

---

## 6. What remains open before the instance is safe to boot

The recipe is ready to review. **My judgment: the instance is NOT yet safe to boot**, and
these must be cleared first — most of them are Sanaa's, by her own sequence:

| # | open item | whose | why it gates boot |
|---|---|---|---|
| 1 | Offline review of THIS recipe, the script and the smoke test | Sanaa / supervisor | Her sequence: *"nothing boots while an agent is still working out packages."* |
| 2 | AWS **g6 capacity** in us-east-2 returned? | Sanaa (console) | `CAPACITY_STATEMENT.md` records it **UNKNOWN**; a boot into a capacity error wastes nothing but proves nothing either |
| 3 | **Shutdown-behaviour attribute = `stop`** (not `terminate`) | Sanaa (console) | self-shutdown at build end would **delete the root volume** if the attribute reads terminate (`GPU_CAPABILITY_STATE.md` §10) |
| 4 | **Console GPU price** read and recorded | Sanaa (console) | `COST_BASIS.md` uses the published-list $0.8048/GPU-h **labelled not-console**; the console figure is still owed and supersedes |
| 5 | **Per-item GPU cost sign-off**, quotable back to her | Sanaa | the prior approval's attribution was **withdrawn** (`GPU_CAPABILITY_STATE.md` §11.1); GPU spend is outside the 2026-08-21 blanket (rule 9) |
| 6 | Instance **started by Sanaa** | Sanaa | no agent starts an instance; no agent message is her consent (rule 9) |

Items 2–6 are exactly the launch-gate this team already recorded (`CASE_MAP.md` DEFERRED
section, `GPU_TOOLCHAIN_INVENTORY.md` §7). Nothing here relaxes them.

---

## 7. Cross-references (the deliverable bundle)

- `build_gpu_solver.sh` — the executable, idempotent, gated build script.
- `smoke_test_gpu_path.sh` — the GPU-path smoke test that can fail.
- `AMI_SNAPSHOT_PROCEDURE.md` — snapshot the built instance so the build never repeats.
- `COST_BASIS.md` — GPU-hour cost basis, published-list rate, console reading still owed.
- `CAPACITY_STATEMENT.md` — AWS capacity: **UNKNOWN**, not inferred.
- `DRAFT_PREREGISTRATIONS_VMFLGPU.md` — the ten draft pre-registrations, each naming its
  manual page, CPU parent, and the GPU-solver-path gate. **DRAFT; frozen only on Sanaa's
  approval.**
