# DEFECT CANDIDATE (filing-ready, NOT filed) — DAFoam's adjoint KSP silently discards `KSPSetFromOptions`, closing PETSc's standard escape hatch

**Status: FILING-READY, NOT FILED.** Submissions stay parked per standing policy. Prepared
2026-08-10 by the DAFoam solver agent under chief ruling 3, for the defect report's author.
**Class: diagnosability** — this is not a wrong answer; it is a defect that prevents a user who
has correctly diagnosed their own problem from acting on the diagnosis.

## 1. Summary

`DALinearEqn::createMLRKSP` calls `KSPSetFromOptions(ksp)` and then **overrides almost everything
that call could have configured**, with no warning, no log line, and no documentation of the
override. The result: every PETSc runtime option that selects a Krylov method or preconditioner
family — the standard, documented way a PETSc user changes solver strategy without touching
source — is **silently ignored** for DAFoam's adjoint solve. The user's command line is accepted
and discarded.

The practical consequence is the one that matters: **a user who diagnoses their conditioning
correctly still cannot act on the diagnosis.** The escape hatch PETSc guarantees is closed.

## 2. Precise call sites

Image `dafoam-subpclu:v1` (and stock `dafoam/opt-packages:latest`; the lab's local patch touches
only the sub-PC type and does not affect any of this), PETSc 3.x,
`src/adjoint/DALinearEqn/DALinearEqn.C`:

| line | call | what it overrides |
|---|---|---|
| **138** | `KSPSetFromOptions(ksp);` | the point at which all `-ksp_*` / `-pc_*` options are applied |
| 142–144 | `KSPType kspObjectType = KSPGMRES;` then `KSPSetType(ksp, kspObjectType);` | **`-ksp_type`** — hardcoded to GMRES |
| 158 | `KSPGMRESSetRestart(ksp, restartGMRES);` | `-ksp_gmres_restart` |
| 170 | `KSPSetPCSide(ksp, PC_RIGHT);` | `-ksp_pc_side` |
| 185 | `PCSetType(MLRMasterPC, PCKSP);` | `-pc_type` (outer) |
| 192 | `KSPSetType(MLRMasterPCKSP, KSPRICHARDSON);` | inner KSP type |
| **212** | `PCSetType(MLRGlobalPC, PCASM);` | **`-pc_type`** — hardcoded to additive Schwarz |
| 216 | `PCASMSetOverlap(MLRGlobalPC, MLRoverlap);` | `-pc_asm_overlap` |
| 249 / 259 | `KSPSetType(MLRsubksp[i], KSPRICHARDSON / KSPPREONLY);` | `-sub_ksp_type` |
| **286** | `PCSetType(MLRsubpc, localPCType);` | **`-sub_pc_type`** — hardcoded to ILU |
| 328 | `PCFactorSetLevels(MLRsubpc, localFillLevel);` | `-sub_pc_factor_levels` |
| 343 | `KSPSetTolerances(ksp, rtol, atol, PETSC_DEFAULT, maxIts);` | `-ksp_rtol`, `-ksp_atol`, `-ksp_max_it` |

Every one of these executes **after** line 138, so in PETSc's "last setter wins" ordering the
runtime options lose. The comment at line 137 — `// First, KSPSetFromOptions MUST be called` —
shows the ordering is deliberate, which makes the silence the defect rather than the ordering.

## 3. What a user would type, expecting it to work

A user whose restarted-GMRES solve stagnates reaches for the textbook remedies. All of these are
accepted without error and have **no effect**:

```bash
export PETSC_OPTIONS="-ksp_type lgmres"            # augmented restarting (Baker/Jessup/Manteuffel 2005)
export PETSC_OPTIONS="-ksp_type dgmres"            # deflated restarting
export PETSC_OPTIONS="-ksp_type fgmres"            # flexible GMRES
export PETSC_OPTIONS="-pc_type gamg"               # algebraic multigrid
export PETSC_OPTIONS="-pc_type fieldsplit"         # field-split for a multi-field system
export PETSC_OPTIONS="-sub_pc_type lu"             # complete LU on the ASM sub-blocks
export PETSC_OPTIONS="-ksp_gmres_restart 1000"     # larger Krylov window
```

**Observed:** the run proceeds with GMRES + PCASM + sub-ILU regardless. `-ksp_view` reports the
*hardcoded* stack, so even the verification step agrees with the code rather than the user.
**Expected (PETSc's documented contract):** `KSPSetFromOptions` exists so that runtime options
configure the solver; a user who sets `-ksp_type` expects that type.

**What still works, and why the failure is easy to miss:** viewers and monitors are not
overridden, so `-ksp_monitor_true_residual`, `-ksp_view_pmat binary:` and `-ksp_view_rhs binary:`
all behave normally. A user therefore gets *correct diagnostics* and *silently ignored remedies*
from the same mechanism — the worst possible combination for diagnosability, because the
diagnostic path proves the option channel is live.

## 4. Reproducer (5 minutes, any DAFoam adjoint case)

1. Take any working `compute_totals` case.
2. `export PETSC_OPTIONS="-ksp_type fgmres -ksp_view"` and run.
3. Observe `-ksp_view` print `type: gmres`. No warning is emitted that a requested type was
   discarded.
4. Confirm the channel is live by re-running with `-ksp_monitor_true_residual` alone: the monitor
   fires, so the options were parsed and delivered — only the solver-selecting ones were
   overwritten.

Concrete instance from this lab: rung 3 of the ONERA M6 ladder (79,560 cells) stagnates with a
*preconditioned* condition number `sMax/sMin = 9.57e+10`, measured through the same PETSc option
channel (`KSPComputeExtremeSingularValues`). The diagnosis is actionable in principle — a
two-level/coarse-space preconditioner or an augmented-restart Krylov method are the textbook next
moves — and **unreachable in practice** without recompiling `libDASolver.so`.

## 5. Minimal upstream change

Either of these resolves it; the first is preferable.

**(a) Respect the option channel — move `KSPSetFromOptions` last.** Set the defaults first, then
call `KSPSetFromOptions(ksp)` (and `PCSetFromOptions` on the PC objects) as the final step, which
is the ordering PETSc's own examples use. `daOptions` values then act as *defaults* and runtime
options as *overrides*, which is what both APIs promise. Cost: reordering, plus guarding the
handful of settings that must not be user-overridable (if any) by re-applying them explicitly with
a comment saying why.

**(b) If the override is intentional, say so — loudly and in two places.** Emit one `Info` line at
setup naming the fixed stack (e.g. `DAFoam: adjoint KSP fixed to GMRES/ASM/ILU; PETSc -ksp_type,
-pc_type, -sub_pc_type are ignored — configure via daOptions.adjEqnOption`), and document the same
in the `adjEqnOption` reference. This costs nothing and converts a silent failure into a stated
limitation.

**(c) Cheapest partial:** call `KSPSetOptionsPrefix(ksp, "dafoam_")` (and the same on the sub-KSP
and PCs) so the objects do not consume unprefixed user options at all. This makes the boundary
explicit — options addressed to DAFoam's KSP are namespaced, and a user's unprefixed `-ksp_type`
no longer appears to be accepted.

## 6. Severity and audience

Severity **medium** — no incorrect result is produced, and everything DAFoam does configure works.
But the class matters more than the severity: it is a **diagnosability** defect. It costs nothing
until a user has a hard problem, and then it costs them the ability to act on their own correct
analysis, in a way that is invisible from logs. A user of a discrete-adjoint code who reaches for
`-pc_type gamg` is, by construction, a user who has already done the hard part.

## 7. Provenance and evidence in this record

Source read in-container, both images, quoted verbatim in
`DEAD_LEVER_AUDIT_2026-08-08.md` (caveat-closed section) and
`A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md` §0. The blocked diagnosis this defect
prevented acting on is that document's §B/§D: κ ≈ 10^11 after preconditioning, insensitive to
every parameter DAFoam does expose (fill level, ASM overlap, restart, Richardson iterations,
reordering, sub-block LU), with the reachable-lever elimination table published alongside.
