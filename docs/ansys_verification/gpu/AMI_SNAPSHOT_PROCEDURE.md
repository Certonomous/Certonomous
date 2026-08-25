# AMI SNAPSHOT PROCEDURE — so the GPU build never repeats

**DRAFT, `ansys-lane-opus48` for `ansys-verification-supervisor`, 2026-08-25. FIRST
ARROW: reviewed offline; no instance touched.**

**Where this sits in Sanaa's binding sequence:** *build recipe … → boot → build →
smoke test → **SNAPSHOT THE AMI so the build never repeats** → all 10 VMFLGPU cases →
stop instance.* The snapshot is taken **only after `smoke_test_gpu_path.sh` PASSES** —
never snapshot an unproven build.

## Who does what — the AWS actions are Sanaa's

Creating an AMI is a console/AWS-API action on the account. This box has **no AWS
CLI** (`GPU_CAPABILITY_STATE.md` §10: *"This box has no AWS CLI and cannot read the
attribute"*), so **the snapshot is Sanaa's console action**, exactly like the launch
and the stop. This document is the runbook she follows; no agent creates or registers
an AMI (rules 7, 9 — nothing leaves the box on an agent's say-so, and no agent message
is her consent).

## Preconditions (all must hold before the snapshot)

1. `smoke_test_gpu_path.sh` exited **0** (all three GPU tells fired; forced-CPU control
   discriminated; physics sane).
2. `~/gpu_build/TOOLCHAIN_MANIFEST.txt` exists and records driver, CUDA, OpenFOAM
   v2606, PETSc sha + `PETSC_ARCH`, petsc4Foam sha, `sm_89`, and the `sha256` of
   `libpetscFoam.so`. **The manifest is the AMI's identity** — a restored instance runs
   `sha256sum` on `libpetscFoam.so` and matches it against the manifest to prove it
   carries the same toolchain.
3. The build markers under `~/gpu_build/markers/` are all present (the build is
   complete, not partial).

## The snapshot (console runbook for Sanaa)

1. **Quiesce.** No solver running; no unsaved work. The build tree
   `~/gpu_build/` and the OpenFOAM install are on the root volume, so a root-volume AMI
   captures everything.
2. **EC2 → Instances → select `gpu1` → Actions → Image and templates → Create image.**
   - Name: `certonomous-gpu-openfoam2606-petsc4foam-cuda-sm89-<YYYYMMDD>`.
   - Description: paste the one-line toolchain manifest summary (OpenFOAM v2606, PETSc
     tag+sha, petsc4Foam tag+sha, CUDA version, sm_89).
   - **No reboot** is acceptable if the tree is quiesced; a reboot-to-image is safer and
     is fine here since nothing is mid-run.
3. **Record the resulting `ami-xxxxxxxx` id** and its creation UTC into
   `docs/GPU_CAPABILITY_STATE.md` (a new dated section, foot-appended, rule 6) and into
   this team's `docs/ansys_verification/gpu/` bundle — so the next VMFLGPU session
   **launches from the built AMI and skips the entire build**.
4. **Verify the AMI is `available`** in EC2 → AMIs before terminating or stopping the
   source instance.

## What the AMI buys, and the honest limit

- **Buys:** every future GPU session launches `g6.xlarge` from
  `certonomous-gpu-openfoam2606-petsc4foam-cuda-sm89-<date>`, sources OpenFOAM, and runs
  cases immediately — the ~build cost (PETSc + petsc4Foam compile, tens of minutes of
  GPU-idle-while-compiling) is paid **once**, not per session. This directly answers the
  7.88-GPU-h idle-waste row: the build is the biggest idle-billing risk, and the AMI
  removes it from every subsequent boot.
- **Honest limit:** an AMI is tied to the driver/CUDA it was built on. If AWS updates the
  base DLAMI's driver, a restored AMI still carries the **old** driver (baked into the
  image) — which is fine and is in fact what we want (reproducibility), but means driver
  currency is a deliberate, dated decision, not an automatic one. Record the driver in the
  AMI name so drift is visible.

## Cost note

The AMI's **EBS snapshot storage** bills at the EBS snapshot rate (GB-month), separate
from the GPU-hour rate. It is small (a ~15–20 GB delta over the base AMI) but it is a
**standing** charge that continues while the instance is stopped. It is recorded in
`COST_BASIS.md` as a named, separate line — not folded into GPU-hours — and its rate is
**console-owed** like the GPU-hour rate (do not invent it).
