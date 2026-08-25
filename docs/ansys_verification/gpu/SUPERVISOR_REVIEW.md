# Supervisor review of the GPU first-arrow bundle — READ PERSONALLY, NOT RELAYED

**By `ansys-verification-supervisor`, 2026-08-25T20:50Z.** This is the
`SUPERVISION_CHARTER.md` §3 check-1 read: the build script and the smoke test are
instruments, and an instrument change without a supervisor's own read is an uncalibrated
instrument. **A lane's "I tested it, it's fine" is evidence, not this read.** I read
`build_gpu_solver.sh` and `smoke_test_gpu_path.sh` as code.

## VERDICT ON THE BUNDLE: ACCEPTED AS THE FIRST ARROW. **STILL NO BOOT.**

Sanaa's sequence is *recipe/script/smoke test prepared and REVIEWED OFFLINE → boot → build
→ smoke test → snapshot the AMI → the ten cases → stop instance.* The bundle is the first
arrow and the review is now done. **The remaining gate to a boot is not technical
readiness — it is the open items in §3 below, and Sanaa.**

## 1. THE SMOKE TEST CAN GENUINELY FAIL. Verified by reading it, not by being told.

It runs the case twice: once with `-mat_type aijcusparse -vec_type cuda`, once with
`-mat_type aij -vec_type standard` **forced**. Three tells must fire on the GPU run —
non-zero GPU flops in `-log_view`, a PID holding non-zero device memory in `nvidia-smi`,
and an active `*aijcusparse` matrix type. **If the forced-CPU control also fires the GPU
tells, the script exits 2 and certifies NOTHING** rather than reporting a pass.

**That is rule 3's planted-zero discipline transposed onto GPU detection**, and it is the
right shape: a reader not shown able to see a negative cannot be trusted on a positive.

## 2. ⚠ A FINDING THE LANE DID NOT FLAG, AND IT IS LOAD-BEARING

**`tell1_gpu_flops` is a LOOSE regex and cannot discriminate on its own.** It is
`grep -Eiq 'GPU .*[1-9][0-9]*'` conjoined with `grep -Eiq 'CpuToGpu|GpuToCpu'`. PETSc's
`-log_view` prints GPU columns and `CpuToGpu`/`GpuToCpu` event rows **on a CUDA-configured
build even when the solve ran on the CPU**, with zero counts — and `[1-9][0-9]*` will match
any incidental non-zero digit anywhere on a GPU-labelled line.

**The forced-CPU control is therefore not a nicety. It IS the discriminator.** Tell 1 alone
would certify a CPU run as a GPU run; the control is the only thing standing between this
suite and a false GPU credential.

**STANDING INSTRUCTION, binding on this team:** the forced-CPU control is **never** removed,
skipped, short-circuited or made conditional — not to save a minute of GPU billing, not to
"streamline" the suite. **A smoke test run without its control certifies nothing and its
output must be recorded `NOT A RESULT`, not `PASS`.** Anyone tempted to drop it should read
this section first. This is the same class as L-312: a matcher without a discriminator is
not an instrument.

## 3. OPEN ITEMS THAT MUST CLOSE BEFORE ANY BOOT — the lane's list, accepted, plus mine

1. **CUDA toolkit version on the DLAMI** — unknown; the script detects `nvcc` and installs
   the toolkit only if absent, never touching the driver. Acceptable.
2. **petsc4Foam ↔ OpenFOAM v2606 compatibility** — unknown; the script aborts on the
   compiler error rather than falling back to a mismatched tag. Acceptable.
3. **AWS g6 capacity in us-east-2 — UNKNOWN, written UNKNOWN.** Correct. Capacity does not
   persist from a 2026-08-23 launch and must not be inferred from one.
4. **Console GPU price still owed.** The bundle uses **$0.8048/GPU-h, labelled published
   price list, NOT console, NOT recall** (rateCode `JRTCKXETXF`), and marks the EBS-snapshot
   rate **UNPRICED** rather than inventing one. **That is the correct handling** — GPU spend
   sits outside Sanaa's 2026-08-21 blanket, which was given when no GPU could launch.
5. **A fresh per-item GPU cost sign-off is owed** — the prior approval's attribution was
   withdrawn (`GPU_CAPABILITY_STATE.md` §11.1). **Sanaa's alone.**
6. **The two `<PIN>` tags in `build_gpu_solver.sh` are UNRESOLVED BY DESIGN**, and the script
   refuses to run while they are (`*"<PIN"*) → ABORT`). **This is correct and I am not
   resolving them by guess.** A guessed version tag that happens to compile is the worst
   outcome available, because it would be believed.
7. **Shutdown-behaviour attribute must read `stop`, not `terminate`**, before any
   self-shutdown line is trusted — otherwise self-shutdown deletes the root volume and the
   AMI work with it.

## 4. RULING — where the ten VMFLGPU pre-registrations live (the lane asked)

**DRAFTS stay at `docs/ansys_verification/gpu/DRAFT_PREREGISTRATIONS_VMFLGPU.md`. A FROZEN
pre-registration migrates to `cases/ansys_verification/VMFLGPU00N/PREREGISTRATION.md`, one
per case.** `FILING_CHARTER.md` and `CLAUDE.md`'s WHERE THINGS LIVE table put case
definitions under `cases/`, and every frozen prereg this team already owns sits beside its
case that way. **A frozen document in the drafts file would be a frozen gate with no case
directory to grade against** — and the migration happens **at the freeze commit**, so the
prereg sha in the register points at the path that actually ran.

## 5. WHAT IS *NOT* BEING CLAIMED

The route is **`petsc4Foam` + PETSc `--with-cuda` (cuSPARSE, `sm_89`) on the lab's own
OpenFOAM v2606** — the discretisation stays identical to the CPU parents and only the linear
solve moves to the device. **This lab has no Ansys licence and this team never speaks for
Ansys**: what is verified is *this lab's* GPU solver path, which is exactly Sanaa's ruling
that *"the GPU solver path is actually verified — not CPU physics re-measured on rented
silicon."*

**Partial coverage is flagged honestly and must stay flagged** for VMFLGPU008 (DO angular
sweep stays on CPU), 009 (alpha/MULES on CPU) and 010 (view factors; energy-only). For those
three the phrase "GPU path verified" is **partial** and the drafts say so. A row that quietly
drops the qualifier would be a false credential.

**RapidCFD was considered and rejected**, and the rejection is recorded rather than omitted:
CUDA-7-era Thrust/`sm_2x` against CUDA-12/`sm_89` is a porting project, and its
OpenFOAM-2.3.1 base lacks the needed breadth.
