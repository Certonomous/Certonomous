# GPU SCOPE MEMO — can the dafoam team use the GPU when ansys releases it?

**Version 1.0, dated 2026-08-27. Written by dafoam `lab-lane` (D) for `dafoam-supervisor`. ZERO GPU COMPUTE: no GPU instance was launched, contacted or stopped by this memo, and no image was built.** The only compute it spent is 0.083 core-min of CPU container probes, itemised in §8.

**Nothing in this memo is filed, sent, uploaded, registered, posted or commented outside this box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED. Every judgement here is `[lab-attributed]`.

---

## 1. BOTTOM LINE

> **No. Neither DAFoam image on this box has a GPU-capable PETSc, so dafoam cannot use the GPU at all today — not slowly, not partially. A dafoam GPU rung requires a NEW IMAGE BUILD, which is a much larger item than a run. Until that build exists and is verified, the GPU should stay with ansys or go to whichever team can put it to work today; handing it to dafoam would idle it.**

And a second finding that matters more than the first, because it survives the build:

> **Even with a CUDA PETSc, the GPU would not unblock a single one of dafoam's blocked adjoint rungs.** The measured binding constraint on the DAFoam adjoint on this box is **host memory during CPU-side Jacobian assembly and colouring**, not linear-solve FLOPs — the adjoint dies *before* it reaches a Krylov solve. A 23 GiB L4 does not fix a host-RAM OOM in an OpenMDAO reverse sweep.

## 2. THE AUTHORISATION, AND WHAT IT IS NOT

Sanaa's standing directives of 2026-08-27T16:54Z, §2, verbatim (`git show HEAD:etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`):

> Whenever ansyis team is done using the Gpu, if dafoam team wants to use that instead thats allowed

**That is her authorisation for dafoam to take the GPU when ansys releases it. It is not a licence to spend without costing.** GPU spend sits **OUTSIDE** the 2026-08-21 blanket, which was given when no GPU could launch (`CLAUDE.md` rules 9 and 12); reading that blanket onto GPU-hours would be permission laundering. **Every GPU run carries its own `cost_basis` in GPU-hours priced from the console, never from recall.** No GPU is attached to this box: a GPU is a **separate instance**, launched per run and **stopped when idle**.

**The rate on the record.** `docs/GPU_CAPABILITY_STATE.md` §9 records `g6.xlarge`, Linux, on-demand, us-east-2 at **$0.8048/hr**, read from AWS's published price-list feed (payload string `"0.8048000000"`) — **a published-list figure, not a console reading and not a measurement.** The ansys team's own most recent GPU row (`docs/COST_CALIBRATION.md` C-165, VMFLGPU001) uses that same figure and states explicitly that the **console figure is still owed**. Any dafoam GPU proposal inherits that gap and must say so.

## 3. WHAT WAS PROBED, AND WHAT IT MEASURED

Both DAFoam images were probed at 2026-08-27T17:2xZ inside `--rm` containers pinned to `--cpus=0.5 --cpuset-cpus=9 --memory=2g`. **No solver ran, no mesh was generated, no GPU was touched.**

| reading | `dafoam/opt-packages:latest` (SHIPPED) | `dafoam-idwarp-rot:v1` (PATCHED) |
|---|---|---|
| PETSc | 3.15.5, `PETSC_ARCH=real-opt` | 3.15.5, `PETSC_ARCH=real-opt` |
| `PETSC_HAVE_CUDA` in `petscconf.h` | **NOT DEFINED** | **NOT DEFINED** |
| `PETSC_HAVE_{HIP, KOKKOS, SYCL, VIENNACL, CUSPARSE, OPENCL}` | **NONE DEFINED** | **NONE DEFINED** |
| `libpetsc.so` shared deps matching `cuda\|cusparse\|cublas\|hip\|rocm` | **0** of 21 total | **0** of 21 total |
| `PETSc.Mat().setType("aijcusparse")` | **REFUSED**, PETSc error 86, *"Unknown type. Check for miss-spelling or missing package"* | **REFUSED**, same error |
| `nvcc` on PATH | **ABSENT** | **ABSENT** |
| `/usr/local/cuda` | **ABSENT** | **ABSENT** |
| CUDA entries in `ldconfig -p` | **0** | **0** |
| `petsc4Foam` / `libpetscFoam.so` in `$FOAM_LIBBIN`/`$FOAM_USER_LIBBIN` | **0 entries** | (same build) |
| OpenFOAM in image | v2506 | v2506 |

**THE PLANTED CONTROL (`CLAUDE.md` rule 3): a zero from a reader not shown able to see a non-zero is not evidence, so both readers were shown a non-zero first.**

* The **same `grep`** that found no `PETSC_HAVE_CUDA` found **131 `PETSC_HAVE_` defines** in the same file, including `PETSC_HAVE_FORTRAN`, `PETSC_HAVE_METIS` and `PETSC_HAVE_PARMETIS`. The grep works; CUDA is genuinely not there.
* The **same `MatSetType` reader** that refused `aijcusparse` **accepted `aij`, `baij`, `sbaij` and `dense`** and refused `aijkokkos`. The reader works; the GPU matrix types are genuinely not registered.

**Conclusion, stated plainly because it is the answer:** the shipped PETSc was **not built with any GPU backend**. There is no flag, no environment variable and no runtime option that turns this on. `-mat_type aijcusparse` and `-vec_type cuda` are not slow here — they do not exist here.

## 4. WHAT A GPU-CAPABLE DAFOAM BUILD WOULD ACTUALLY REQUIRE

Concretely, and in the order the dependencies force:

1. **A CUDA toolkit in the image** (`nvcc`, headers, `libcusparse`, `libcublas`) matching the L4's compute capability **`sm_89`**, plus the container run with the NVIDIA runtime. None of it is present.
2. **PETSc 3.15.5 (or a newer pin) reconfigured and rebuilt with `--with-cuda=1`**, producing a `real-opt`-equivalent arch that registers `aijcusparse` / `cuda`. This is a full PETSc rebuild, not a patch.
3. **`petsc4py` rebuilt against that PETSc**, because the DAFoam adjoint reaches PETSc through it.
4. **DAFoam's own `libDASolver*.so` family relinked** against the new PETSc — DAFoam does not call PETSc through OpenFOAM's solver framework, it embeds its own KSP; `DALinearEqn.C` is the file this lab has already patched three different ways (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §3), so every patched image (`dafoam-idwarp-rot:v1`, `dafoam-subpclu:v2`, `dafoam-kspopts:v1`) would need rebuilding too — **and the two-row rule (`DAFOAM_CHARTER.md` §1) means a GPU verdict needs BOTH rows, i.e. at least two new images.**
5. **An MPI that all of it agrees on.** This is the step with a *measured* cost rather than an estimated one: the ansys team built PETSc-CUDA for the GPU path on 2026-08-26 and **`make check` FAILED in `MPI_Init`**, forcing an MPI reconciliation before anything ran (`cases/ansys_verification/VMFLGPU001/PREREGISTRATION.md`). Their build also required a new launcher gate that `readlink -f`s `libPstream.so`, `libpetsc.so` and `libpetscFoam.so` and refuses on a mismatch. That is the honest scale of the work.
6. **Re-establishing toolchain identity.** `DAFOAM_CHARTER.md` §6: *"a version string is not an identity."* A GPU image is a new image ID and a new set of `.so` md5s, and every gate in this family (`G9`) reads them. Every existing dafoam item's registered digests would be untouched, but the GPU items would start from an unverified toolchain with no prior FD-verified row behind it.

**Effort, stated as a band and labelled an ESTIMATE, not a measurement:** a first CUDA-PETSc + DAFoam image, built and *verified to reproduce a known CPU adjoint*, is a **multi-day image-and-verification item**, comparable in size to the `patched_build/subpclu` programme (which produced a `Dockerfile`, four substitute gates and a `BUILD.md` because md5 equality with the hand-built original was impossible). It is **not** a run, and it should never be scheduled as one. The lab has no measured figure for it, and this memo does not invent one.

## 5. WHICH DAFOAM RUNG WOULD BENEFIT MOST, IF THE BUILD EXISTED

**Not the airfoil.** A6/D8R-class work is the only honest candidate, and even there the case is weak.

| candidate | size | why it is or is not the candidate |
|---|---|---|
| **A1 NACA0012** (D1, D13, D15, D16, AV-1, AV-2, **SO-1a**) | **4,032 cells** | **NO.** The whole five-arm chain costs **7–16 core-min**; a single adjoint is well under one core-minute. At this size the PCIe transfer and the GPU-side setup dominate the solve, and the GPU loses to the CPU outright. Putting SO-1 on a GPU would be a slower answer with a new toolchain to verify. |
| **B3 / S1 CBFS** | 21,000 cells | No. Same argument, one order weaker. |
| **A6 ONERA M6 / D7FR** | **41,760–42,120 cells** | **The best of a weak field.** A6's rung N=16 adjoint is the largest that has ever converged in this lab — `CD` `reason 2` in **517 KSP iterations** — and the rung cost **76.653 core-min** (`docs/dafoam/README.md:100`). A Krylov solve of 517 iterations on a 42k-cell 3-D adjoint is the only place where a GPU-resident `aijcusparse` operator could plausibly repay its transfer cost. |
| **D8R / the 99,840- and 399,360-cell cases** | 99,840 / 156,089 / 399,360 cells | **The rungs that most need help, and the ones a GPU CANNOT help.** See §6. |

## 6. THE FINDING THAT MATTERS MOST: A GPU DOES NOT UNBLOCK THE BLOCKED RUNGS

`cases/dafoam/ADJOINT_MEMORY_ENVELOPE.md` measured the wall this family actually hits:

* Adjoint runs **succeed** at 4,032 and 63,920 cells.
* At **156,089 cells** it **dies mid Jacobian-colouring**.
* At **99,840 and 399,360 cells** it **OOMs**, at a 12 GB container cap **and** at 18 GB.
* **Eight mitigations already ruled out** on the 399,360-cell case: 12g and 18g caps, 4-rank and 2-rank decomposition, `gmresRestart` 1000→200, `pcFillLevel` 1→0.
* The recorded structural cause: *"OpenMDAO's reverse-mode sweep for any requested total derivative builds a mesh-sized `d[residuals]/d[vol_coords]` Jacobian block regardless of the requested `wrt=`."* And DAFoam rejects OpenFOAM `empty` patches (`DACheckGeometry.C:278`), so **every nominally-2-D DAFoam case is a true 3-D solve and both Jacobian blocks are sized for the 3-D mesh** — there is no cheaper 2-D adjoint path in this installation.

**Read together: the adjoint fails during CPU-side assembly and colouring, before a Krylov solve is ever entered.** Moving the linear solve to a GPU changes nothing about a host-memory OOM in an OpenMDAO reverse sweep, and it changes nothing about a colouring pass that dies. **The GPU addresses the part of the pipeline that is not the bottleneck.**

That is the single most important sentence in this memo, and it is the reason it recommends against the handover rather than for it.

## 7. RECOMMENDATION, AND THE DECISION RULE THAT WOULD CHANGE IT

**Recommendation: dafoam should NOT take the GPU on ansys's release.** The capability does not exist in our images today; acquiring it is an image-build programme, not a run; and even after the build the measured bottleneck is untouched. Sanaa's §2 also says *"A resource without a live runner is a boarded defect"* and *"Idle >30 min with a frozen queue = auto-boarded defect"* — **handing the GPU to a team that provably cannot execute on it would manufacture exactly that defect.** If ansys is done, the GPU should go to a team that can use it today, or be stopped.

**No costed GPU-hour proposal is offered, because the precondition fails.** `COMPUTE_BUDGET_CHARTER.md` and rule 12 require a cost per run; a run that cannot start has no honest cost, and quoting GPU-hours for a capability that does not exist would be a fabricated measurement.

**The decision rule, falsifiable and written now so it is not fitted later.** Dafoam should revisit this memo if and only if ALL FOUR of these become true:

1. **A CUDA-enabled PETSc exists in a DAFoam image on this box** — testable in one command with no GPU attached and no solver run: `PETSc.Mat().setType("aijcusparse")` returns without raising, and `grep PETSC_HAVE_CUDA petscconf.h` matches. Today both fail; §3 records the exact refusal.
2. **That image reproduces a KNOWN CPU adjoint** — the A6 rung N=16 `CD` gradient, or D15's PATCHED row — to within band D on the CPU path first, so the GPU arm has a verified toolchain behind it rather than an unverified one.
3. **A rung exists whose adjoint linear solve is large enough to repay the transfer** — concretely, the A6/D8R class at ≥ 40,000 cells with a KSP iteration count in the hundreds, not the A1 airfoil.
4. **The console $/GPU-h has been read and recorded**, closing the gap `COST_CALIBRATION.md` C-165 still carries, so the proposal's `cost_basis` is a console figure and not a published-list one.

Until all four hold, a dafoam GPU rung would be **`BLOCKED`** — and note that `BLOCKED-GPU` is retired (`CLAUDE.md` rule 12): the blocker here is **not capacity**, it is **capability in our own images**, and it should be labelled as such.

## 8. THE COST OF THIS MEMO

| item | measured |
|---|---|
| image probes, 2 images | **0.050 core-min** (3 wall s at 1 rank) |
| planted control probe | **0.033 core-min** (2 wall s at 1 rank) |
| **total** | **0.083 core-min**, np = 1, no solver, no mesh, no GPU |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED**: **$0.00007**. **GPU spend: $0.00 — no GPU instance was launched, contacted or stopped by this memo.**

## 9. WHAT THIS MEMO DOES NOT ESTABLISH

It does not establish that a CUDA-PETSc DAFoam build is impossible — only that it does not exist here, and what it would take. It does not measure how fast such a build would be; no dafoam GPU benchmark exists in this lab and none is invented here. It does not speak for the closure team, whose TBNN training is a *training* workload (`docs/GPU_CAPABILITY_STATE.md` §2 records that as the use case Sanaa's quota request named) and whose GPU case is completely different from this one — **a GPU released by ansys may well have a good home; this memo says only that it is not dafoam's home today.** It does not read the GPU instance's current state: that instance is ansys's while they hold it, and this lane did not contact it. And it does not authorise anything: **the release of the GPU, and any decision to spend GPU-hours on it, are Sanaa's.**
