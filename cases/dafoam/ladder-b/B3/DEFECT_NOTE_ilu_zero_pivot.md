# DEFECT NOTE — DAFoam's adjoint ASM sub-block ILU hits an exact zero pivot on wall-resolved separated cases, and the sanctioned PETSc remedy is unreachable

> **NOT FILED — filing reserved to Sanaa.** No issue has been opened, no maintainer
> contacted, nothing posted, nothing pushed. This note is prepared so that filing is a
> decision rather than a drafting job. Prepared 2026-08-21 by the DAFoam team, Lane B,
> Phase 1 task 4.

**Target if filed:** `mdolab/dafoam` (v5 series). Adjacent open upstream threads that
describe the same wall from the user side: **#1002**, **#1011** (both 2026-07, open,
users exhausting the documented remedy ladder on *official tutorials*).

**Class:** numerical robustness **plus** diagnosability. The wrong answer is not a wrong
gradient — no gradient is produced at all — so this is a hard block, not a silent error.
`-9` never fools DAFoam's success gate (`S1_FIML_FIELD_INVERSION.md` §25-addendum item 5:
0 occurrences of *"Residual tolerance satisfied"* in every `-9` log), which is the one
piece of good news in the report and should be stated.

---

## 1. Summary

On wall-resolved, separated, incompressible `kOmegaSST` cases, DAFoam's discrete-adjoint
GMRES solve fails at **iteration 0** with PETSc `KSPConvergedReason = -9`
(`KSP_DIVERGED_NANORINF`) and a finite, non-zero initial residual. The cause is not
conditioning and not the right-hand side: **the ASM sub-block *incomplete* factorization
hits an exact zero pivot.** The same assembled matrix factors and solves cleanly under a
*complete* LU with partial pivoting.

`DALinearEqn.C` hard-codes `PCType localPCType = PCILU;` inside the sub-block loop, so
the remedy PETSc's own developers prescribe for exactly this signature — `-sub_pc_type lu`
— **cannot be reached from `daOptions` or from the PETSc runtime option channel**, and a
user who diagnoses their own problem correctly still cannot act on the diagnosis.

## 2. Reproduced on two independent cases

| case | cells | model | signature |
|---|---|---|---|
| CBFS (curved backward-facing step) | 21,000 | `kOmegaSST`, low-Re wall treatment | `Total iterations: 0. PetscConvergedReason: -9.`, initial residual `7.091590452305e-04` |
| NASA 2D wall-mounted hump | 51,626 | `kOmegaSST`, wall-resolved | `Total iterations: 0. PetscConvergedReason: -9.`, initial residual `1.094138002900e+00` |

Two meshes, two objectives, one signature. **Memory is not the constraint**: on the hump,
Jacobian colouring completed normally in 68.62 s and host `MemAvailable` fell only from
30.06 GB to 18.99 GB — a peak of roughly 11 GB, no OOM, no kill.

## 3. What was ruled out first, by measurement

| hypothesis | test | result |
|---|---|---|
| primal under-convergence | `primalMinResTol` tightened 100× (1e-4 → 1e-6) | identical `-9`, iteration 0 |
| the objective / RHS | swapped the field-variance loss for a standard force (CD) objective proven working on this lab's naca0012 case | identical `-9` |
| shallow preconditioner fill | `pcFillLevel` 1 **and** 4 | identical `-9` |
| mesh quality | `DACheckMesh`: max aspect ratio **14.76**, max non-orthogonality **33.3°**, max skewness **0.26** — all inside DAFoam's own gates (1000, 70°, 4), printed "OK" | not the cause |
| a poisoned primal state | every numeric token in the state and mesh files the adjoint reads scanned cell-by-cell: **886,833 tokens across 13 files, zero non-finite hits** | the NaN is generated *during* adjoint assembly or the KSP solve, not inherited |
| turbulence-model variable bounds | `primalVarBounds` floor `kMin = 1e-10` against the wall BC's `k = 1e-15` | identical `-9`, 0 iterations |
| the SST adjoint as such | a `kOmegaSST` field-inversion adjoint with 5,000 per-cell DVs on DAFoam's **own** steady field-inversion tutorial | converges: **91 iterations, `PetscConvergedReason: 2`** |
| the matrix reordering | all five `jacMatReOrdering` values on CBFS | `rcm` **-9** (0 it), `1wd` **-9** (0 it), `natural` **-3** (1000 it), `nd` **-3** (1000 it), `qmd` **-3** (1000 it). **Two of five produce the NaN, three produce flat stagnation, none converges.** The initial residual is identical (`7.091590452305e-04`) in all five |

## 4. The matrix evidence — the mechanism, reproduced with no DAFoam and no PETSc solver in the loop

The preconditioner matrix and RHS were dumped with **stock PETSc runtime flags and no
source change** (`-ksp_view_pmat binary:`, `-ksp_view_rhs binary:`) and analysed offline
with `scipy`.

**Dump identity check first:** `‖b‖₂ = 7.091590452305e-04`, equal to the printed GMRES
iteration-0 residual **to all 13 digits** (`DALinearEqn.C` sets
`KSPSetNormType(ksp, KSP_NORM_UNPRECONDITIONED)`, so the printed residual is exactly
`‖b‖`). The RHS is non-zero on 63,000 of 210,592 entries = 3 × 21,000, i.e. the `U` block
only — as a velocity-variance objective should be.

`dRdWTPC`: **210,592 × 210,592, 13,710,468 non-zeros. Zero zero-rows, zero zero-columns,
zero zero-diagonal entries.** Diagonal magnitude spread **8.67 decades** — for comparison,
this lab's transonic `DARhoSimpleCFoam` family measures **14.17** on the same metric and
fails differently, so **a diagonal-spread/conditioning story does not explain this case.**

| factorization | result |
|---|---|
| `scipy.sparse.linalg.spilu`, `drop_tol=1e-2`, `fill_factor=3` | **`RuntimeError: Factor is exactly singular`** |
| `spilu`, `drop_tol=1e-3`, `fill_factor=5` | **exactly singular** |
| `spilu`, `drop_tol=1e-4`, `fill_factor=5` | **exactly singular** |
| `spilu`, `drop_tol=1e-5`, `fill_factor=10` | **exactly singular** |
| `scipy.sparse.linalg.splu`, `diag_pivot_thresh=0` | **solves**, `‖Ax−b‖/‖b‖ = 2.3769e-10`, `nnz(L+U) = 3.22e+08` |
| `splu`, `diag_pivot_thresh=0.1` | **solves**, `6.4063e-12`, `nnz(L+U) = 3.62e+08` |
| `splu`, `diag_pivot_thresh=1` | **solves**, `2.535461e-12`, `nnz(L+U) = 3.90e+08` |

**The whole strength axis was swept: incomplete factorization never succeeds on this
matrix, and complete factorization with pivoting always does, at every pivot threshold
including the one that most prefers the diagonal.** That is the mechanism, in a second
independent implementation, with no MPI and no PETSc KSP involved.

Two corroborating controls on the same dump: unpreconditioned `scipy` GMRES reproduces the
stagnation (relative residual `1.0 → 9.999687e-01` over 1000 matvecs), which **exonerates
DAFoam's KSP/PC configuration**; and `splu` shows the system is non-singular and the RHS
consistent, so **a solution exists and Krylov cannot reach it.**

One mechanism covers both observed signatures: `rcm` and `1wd` surface the zero pivot as a
NaN (`-9` at iteration 0); `natural`, `nd` and `qmd` surface it as a dead Krylov space
(`-3`, residual flat to 13 digits). And it explains why `pcFillLevel: 4` also returned
`-9`: **fill adds fill, not pivoting.**

**Caution stated rather than buried:** `dRdWTPC` is the *assembled preconditioner*, not
the matrix-free transpose Jacobian GMRES applies. The singular-ILU finding is **direct** —
that is precisely the matrix DAFoam factors — and the GMRES-stagnation results are
corroborative, not identical to the deployed solve.

## 5. Why PETSc's own zero-pivot machinery does not catch it

`DALinearEqn.C` already calls, in the sub-block loop:

```c
PCFactorSetPivotInBlocks(MLRsubpc, PETSC_TRUE);
PCFactorSetShiftType(MLRsubpc, MAT_SHIFT_NONZERO);
PCFactorSetShiftAmount(MLRsubpc, PETSC_DECIDE);
```

These lines are present in upstream `main` and were verified present at shas `d4ccdb4e`
(2022-03-21), `cdb0ca94` (2025-01-30) and `522bada7` (2025-09-12). **The shift is switched
on and is demonstrably insufficient here:** raising the zero-pivot threshold six decades to
`1e-8` — verified to land in the deployed factor, *"tolerance for zero pivot 1e-08"*
visible in `PCView` — still returns `-9` at iteration 0. Consistent with the PETSc
developers' own reading that `DIVERGED_NANORINF` *"means it found a zero pivot either in
the factorization **or in the first attempt to do a triangular solve**"* (Barry Smith,
petsc-users) and that *"ILU is defined by having no pivoting"* (Matthew Knepley): the
failure is **factor growth**, which no shift and no diagonal permutation fixes — only
pivoting or completeness does.

## 6. Minimum reproducer

The cheapest form needs **no DAFoam at all** and is the one a maintainer can run in
seconds:

1. On any case exhibiting the signature, dump the system with stock PETSc flags — no
   source change, no rebuild:
   `PETSC_OPTIONS="-ksp_view_pmat binary:pmat.dat -ksp_view_rhs binary:rhs.dat"`.
2. Offline: `A = petsc4py`-load `pmat.dat`; then
   `scipy.sparse.linalg.spilu(A.tocsc(), drop_tol=1e-4, fill_factor=5)` →
   `RuntimeError: Factor is exactly singular`; and
   `scipy.sparse.linalg.splu(A.tocsc())` → solves to `‖Ax−b‖/‖b‖ ≈ 2.5e-12`.
3. Confirm the dump is the real system: `‖b‖₂` must equal the printed iteration-0 KSP
   residual to all printed digits.

In-solver, the reproducer is a `kOmegaSST` wall-resolved separated case with
`adjEqnOption: {jacMatReOrdering: "rcm", pcFillLevel: 1}` at `np = 4`. This lab's own
staged copy and driver are at
`cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/` (pre-registration and results), with
the case itself frozen at `cases/dafoam/ladder-b/B3_work/CBFS/`.

## 7. Fix options, with their price

| # | fix | change | price | assessment |
|---|---|---|---|---|
| **F1** | **Expose the sub-block PC type as an `adjEqnOption` key**, default `ilu` — unchanged behaviour | one option plumbed through to `PCSetType(MLRsubpc, …)` | trivial in code; **the LU factors cost 24–28× the matrix's own non-zeros — ~3 GB on a 21,000-cell case** (measured, §4's `nnz(L+U)` column) | **Recommended.** Behaviour-neutral by default, and it is the PETSc developers' own sanctioned escalation for this signature. Cost is the user's to accept, but they must be able to *choose* it |
| **F2** | Honour `KSPSetFromOptions` instead of overriding it | relocate the call from the top of `createMLRKSP` to the end | measured behaviour-neutral: ONERA M6 21,840 cells returns CD 368 / CL 383 iterations, `reason 2`, bit-identical to the unpatched image | **Necessary but, on our measurement, NOT sufficient for the sub-PC channel** — see §8 |
| **F3** | An **effective-value echo** (`KSPGetType`/`PCGetType`) after the options call | a few `Info` lines | free | **Should ship with F2.** Today `printInfo` echoes the `daOptions` values, so a user overriding `-ksp_type` still reads `Solver Type: gmres` in the log — a switch that did not run |
| **F4** | Change the default sub-PC to LU | one word | the 3 GB/21k-cell factor cost, on every user | **Not recommended.** Would break memory budgets for cases that ILU handles fine |

This lab implemented **F1 as an environment-variable switch, off by default**, in a locally
rebuilt library (`DAFOAM_SUBPC_TYPE=lu` → `PCLU`). On the CBFS case, B3's exact `-9`
configuration then converges: **`PetscConvergedReason: 2`, 667 iterations**, and the
resulting 21,000-component field-inversion gradient is finite-difference-verified at
**0.085 % / 0.059 % / 0.199 %** on three components, plus **0.0211 %** on a fourth chosen
by an independent verification agent. The patch is one hunk and is available.

## 8. What our own measurement adds, and a caveat on the obvious fix

*(This section is filled from `adjoint_unblock_reproduce/RESULTS.md`, arm K, and is the
reason F2 alone is not enough.)*

Reading `createMLRKSP` in program order: `KSPSetUp(ksp)` runs **before** the sub-block
loop — that is where `PCSetUp_ASM` creates the sub-KSPs and PETSc applies `sub_`-prefixed
options to them. DAFoam's `PCASMGetSubKSP` loop then runs and executes
`PCSetType(MLRsubpc, PCILU)`, `PCFactorSetShiftType`, `PCFactorSetShiftAmount` and
`PCFactorSetLevels` **afterwards**. So the surviving runtime-reachable set is exactly the
four factor options DAFoam never touches — `nonzeros_along_diagonal`, `zeropivot`,
`diagonal_fill`, `mat_solver_type` — **and none of them fixes this failure** (all measured,
all `-9` at iteration 0).

**Therefore an upstream fix that only relocates `KSPSetFromOptions` (F2) does not restore
the sub-PC channel.** The report should ask for **F1 + F2 + F3 together**, and should say
plainly that F2 alone would look like a fix and would not be one.

## 9. Novelty, and what upstream has already said

Under **63 recorded searches across 10 venues** (dafoam issues and discussions, idwarp,
pyofm, MACH-Aero, adflow, OpenMDAO, GitHub global, web/scholar, PETSc lists):
**no upstream doc, issue or discussion mentions ILU singularity, zero pivots, or a
direct/sub-direct factorization.** The complete documented remedy ladder is
`renumberMesh -overwrite`; `pcFillLevel` 1→2; `jacMatReOrdering` rcm→nd/natural;
`gmresRestart`/`gmresMaxIters` up; `asmOverlap` up; upwind schemes; kahip; and for
transonic cases `transonicPCOption`. **Nothing in that ladder changes the sub-PC type;
the ILU choice itself is never questioned upstream.**

The PETSc side supplies the precedent the report should lean on, verbatim:

- Barry Smith, petsc-users `msg24474` (2015-03-26): *"The default preconditioner with
  ILU(0) on each process is not appropriate for your problem and is producing overflow.
  **Try `-sub_pc_type lu`** and see if that produces a different result."*
- Hong, petsc-users `msg26973` (2015-10-27), on a zero-diagonal system: ILU with any shift
  *"does not converge"* while `-sub_pc_type lu -sub_pc_factor_shift_type nonzero` converges
  in 24 iterations.

**So the fix this report asks for is the remedy PETSc's own developers prescribe for this
exact signature, and DAFoam's architecture is what makes it unreachable.**

## 10. Suggested tone if filed

Not an accusation. The verification protocol in the method-paper corpus never reached this
configuration — all three papers were read in full, and the matrix-free reverse-AD adjoint
has **exactly one published accuracy measurement, and it is serial** (Kenway, Mader, He,
Martins, PAS 2019 §5.1). The honest framing is: *a wall-resolved separated case falls
outside the region the published protocol covers, the failure has a named mechanism, and
the remedy is one option away from being reachable.*

## 11. Measured today — 2026-08-21: which intervention lifts the `-9`, and what it costs

> **STILL NOT FILED — filing reserved to Sanaa.** Nothing below changes that. No issue has
> been opened, no maintainer contacted, nothing posted, nothing pushed. This section was
> appended by DAFoam team Lane B after the arms of
> `adjoint_unblock_reproduce/` returned; the sections above it are unchanged.

Everything in sections 1 to 10 was written from records dated 2026-07-28 to 2026-08-11. This
section is what a deliberate re-measurement on **2026-08-21** added, from a **rebuilt** image
rather than the `docker commit` one, seventeen days after the original. Full grading, arm by
arm, in `adjoint_unblock_reproduce/RESULTS.md`.

### 11.1 The ladder of interventions, cheapest first, each measured

| # | intervention | image | what it changes | result | price |
|---|---|---|---|---|---|
| **0** | nothing (negative control) | `dafoam/opt-packages:latest`, np = 4 | — | **`-9` at iteration 0**, residual `7.091590452305e-04`, all 13 digits | 5.93 core-min |
| **1** | **run serially** | `dafoam/opt-packages:latest`, np = **1** | ASM collapses to a single block over the whole 210,592² operator | **`-9` persists.** Residual `7.091589775454e-04`, primal 1584 iterations. **The decomposition is not the mechanism** | 7.22 core-min |
| **2** | **PETSc runtime option**, `-sub_pc_type lu`, on the image built to let runtime options through | `dafoam-kspopts:v1`, np = 4 | relocates the outer `KSPSetFromOptions` from `DALinearEqn.C:138` to line 351 | **`-9` persists — and `-ksp_view` prints `PC Object: (sub_) … type: ilu` in the same log.** The option was consumed and then overwritten | 11.33 core-min |
| **3** | **the source change**, `PCSetType(MLRsubpc, PCLU)` behind an env switch | `dafoam-subpclu:v2`, np = 4, `DAFOAM_SUBPC_TYPE=lu` | one hunk in the ASM sub-block loop | **`PetscConvergedReason: 2`, 667 iterations**, every printed residual bit-identical to 2026-08-04 | 18.60 core-min (`patchV`) / 27.60 (21,000-cell `beta`) |

**The minimum intervention that lifts the `-9` is number 3: the source change.** Nothing
cheaper works. Serial does not work, and the sanctioned PETSc runtime option does not work
even on a build that honours PETSc runtime options.

**Its price, measured rather than estimated.**

- **To produce the fix:** a one-hunk patch and a rebuild of three AD modes —
  **284 s wall, 18.93 core-min, \$0.016** on this box, from the reproducible `Dockerfile` at
  `cases/dafoam/patched_build/subpclu/` (`BUILD.md` §4.1). It is not a research project.
- **To run with it:** the CBFS adjoint converges in **272 s** at np = 4 against a control that
  fails in 82 s, so the fix costs roughly **3.3x the wall time of failing**, plus memory. The
  measured **peak RSS is 9.044 GiB** for the 21,000-cell beta-DV adjoint under complete LU,
  inside a **12 GiB** container cap with 2.96 GiB to spare — the first peak-RSS figure this lab
  has for this configuration, and it is **lower than the 22 GiB cap the original runs were
  given**, which had been carried as if it were a requirement. (Per-container figure, named:
  `docker stats` on a shared box also reports the other lane's containers, and the raw maximum
  in the same watcher log belongs to one of those.)
- **To the user who does not want it:** nothing. With `DAFOAM_SUBPC_TYPE` unset the rebuilt
  image reproduces the stock `-9` **to all 13 residual digits** (arm R), so the switch is
  behaviour-neutral by default — which is precisely what §7's **F1** asks upstream for.

### 11.2 What this changes in the sections above

**§8 is confirmed in-solver, and its evidence is now direct rather than inferred.** It was
written from program-order reading of `createMLRKSP` and from W4's offline harness. Arm K
measures it inside the deployed solver: `-sub_pc_type lu` on the command line, and
`type: ilu` in the same run's own `-ksp_view` dump, with no PETSc "unused option" warning
because the option **was** applied — to sub-KSPs that `PCASMGetSubKSP`'s loop then overwrote.
**The report's ask stands unchanged and is now measured: F1 + F2 + F3 together, and F2 alone
would look like a fix and would not be one.**

**§3's "not the decomposition" row is now positive evidence, not an absence.** The table above
ruled out primal convergence, the objective, fill level, mesh quality, poisoned state, variable
bounds, the SST adjoint as such and the reordering — but every one of those ran at np = 4. Arm
N1 removes MPI from the question inside the solver, and the `-9` survives. Together with
`PROOF.md` §25.3's `spilu` result on the assembled whole matrix — `RuntimeError: Factor is
exactly singular`, no MPI anywhere — **two independent routes now say the failure is a property
of the incomplete factorization.** If the report is filed, this is the sentence a maintainer
will want, because it removes the first thing they would ask about.

**§4's mechanism is untouched and needs no revision.** Nothing measured today bears on the
matrix evidence; the dump, the `spilu`/`splu` sweep and the diagonal-spread comparison stand
as written, including the caution that `dRdWTPC` is the assembled preconditioner and not the
matrix-free transpose Jacobian.

**One thing this note should say if it is filed, and could not say before.** The unblock is now
**reproduced from a rebuilt image**, not only observed once: `reason 2`, `667` iterations, and
a 21,000-component gradient whose norm, min and max reproduce to every printed digit, on an
image whose provenance is a committed `Dockerfile` rather than a `docker commit` from a scratch
tree that no longer exists. A maintainer's first question about a one-off patched result is
whether it reproduces. **It does.**

### 11.3 What is still not measured

- The **FD re-anchor** of the resulting gradient on the rebuilt image is **`PENDING`** — the
  nine registered primal-only points did not complete, for host-contention reasons recorded in
  `adjoint_unblock_reproduce/RESULTS.md` §8. **§7's "0.085 % / 0.059 % / 0.199 %" is therefore
  still the 2026-08-04 figure, on `v1`, and is quoted here as that and not as today's.**
- The **NASA hump** remains uncharacterised. §2's hump row is a `-9` signature, which is
  measured; the *boundary* of the hump adjoint is not, and M1 + M2 at **40 core-min** are the
  cheapest measurements that would settle it.
- Three of the four runtime factor options DAFoam never touches — `nonzeros_along_diagonal`,
  `diagonal_fill`, `mat_solver_type` — were not re-measured today. Only `zeropivot` has a
  direct measurement (W4 §2: reaches the factor, still `-9`).

---

---

## Provenance of every number above

| claim | record |
|---|---|
| `-9` on CBFS, 4 configurations, mesh ruled out | `cases/dafoam/ladder-b/B3_duct_field_inversion.md` §Stage 3 |
| `primalVarBounds` and `empty`-patch rungs refuted; 886,833-token scan | `cases/dafoam/ladder-b/B3_supervisor_debug.md` |
| `-9` on the hump; tutorial case converges at 91 iterations; memory measurements | `cases/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md` §4 |
| five-ordering sweep; matrix dump; `spilu`/`splu` tables; diagonal spread | `cases/dafoam/PROOF.md` §25.2–25.3 |
| runtime factor options reachable but empty; offline PC ladder; the sub-LU rebuild; FD gate | `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §1–§5d |
| independent adversarial verification, cell 6490 at 0.0211 % | `cases/dafoam/VERIFICATION_cbfs_unblock_supervisor_sweep.md` |
| upstream shift lines sha-pinned; PETSc developer quotes | `cases/dafoam/LIAISON_RESEARCH_adjoint_conditioning.md` |
| 63-search novelty negative; upstream remedy ladder; #1002/#1011 | `cases/dafoam/LIAISON_NOVELTY_SWEEP_decomposition_defect.md` §3 Target S |
| the 13 override call sites; F2/F3 framing | `cases/dafoam/DEFECT_CANDIDATE_ksp_options_override.md` |
| F2 measured behaviour-neutral (368/383, reason 2) | `cases/dafoam/A3_KSPOPTS_PATCH_PREREGISTRATION.md` §6 Gate A |
| method-paper verification protocols | `cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` |
| arm K, the F2-insufficiency measurement | `cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` |

**Nothing in this note was sent anywhere. Filing is Sanaa's call alone.**

---

## 12. chain4 scored — 2026-08-21: the runtime factor options, and why the shift axis is closed

**Appended 2026-08-21 ~19:0x UTC by the DAFoam team, Lane B.** Source of every number:
`cases/dafoam/ladder-b/B3/ilu_shift_runtime/{PREREGISTRATION.md,RESULTS.md}` and the run root
`/home/ubuntu/certonomous-runs/B3-ilu-shift-runtime/`. **Still NOT FILED; the banner at the
top of this note stands unchanged.**

§11 left one cheap hypothesis alive: that PETSc's *factor* options — as opposed to the sub-PC
*type* — might survive DAFoam's `PCASMGetSubKSP` loop, and that a diagonal shift might carry
the incomplete factorisation past the pivot. **Both halves are now measured, on
`dafoam-kspopts:v1` (`d9d2aed02e36`), the image built so that PETSc runtime options are not
silently discarded, np = 4, `DAFOAM_SUBPC_TYPE` unset, `-ksp_view` on every arm.**

| arm | `PETSC_OPTIONS` | reached the deployed factor? | iterations | reason | core-min |
|---|---|---|---|---|---|
| **C** control | `-ksp_view` only | n/a | 0 | **-9** | 125.60 *(load-contended; ~6.8 uncontended)* |
| **S-T** | `-sub_pc_factor_shift_type nonzero` | **no** | 0 | **-9** | 6.80 |
| **S-A10** | `+ shift_amount 1e-10` | **no** | 0 | **-9** | 6.60 |
| **S-A8** | `+ shift_amount 1e-8` | **no** | 0 | **-9** | 6.60 |
| **L-2** | `-sub_pc_factor_levels 2` | **no — proven** | 0 | **-9** | 6.93 |

**Every arm's `-ksp_view` dump is byte-identical to the control's, timings excepted.** The
proof that the options were overwritten rather than merely ineffective is arm **L-2**: it
requested fill level 2 and its own dump reads **`1 level of fill`**
(`logs/arm_L2.log:12084`), with DAFoam's echo reading `ILU PC Fill Level: 1` (`:12055`).
Requested value and deployed value differ visibly, and the deployed one is DAFoam's.

**A correction that belongs in this note because it would otherwise mislead a maintainer.**
These logs contain `using diagonal shift to prevent zero pivot [NONZERO]`, which reads like
evidence that the shift landed. **It is not.** That line is present in the **control arm,
which set no shift option at all** (`logs/arm_C.log:12086`); it is DAFoam's own
`PCFactorSetShiftType(MLRsubpc, MAT_SHIFT_NONZERO)` printing. The pre-registration flagged
this row as non-discriminating **before the runs**, and it is recorded here so that anyone
reading a `[NONZERO]` banner in a `-9` log does not draw the conclusion this lane briefly drew.

**What it discriminates, and it is the point of §4 of this note.** Shift type, shift amount at
two magnitudes, and extra fill are all *perturbations of an incomplete factorisation*.
`PROOF.md` §25.3 already showed `spilu` returns **`Factor is exactly singular`** at every
drop-tolerance/fill setting swept, while `splu` **always** solves. **A perturbation of a
singular factor is a different singular factor.** The runtime axis is now closed from both
ends: the one factor option DAFoam does *not* set — `zeropivot`, raised six decades to `1e-8`
and **verified landed** in the deployed factor (§11, W4 §2) — **does not help**; and the
options that might have helped **cannot land**, because the `PCASMGetSubKSP` loop rewrites them
after PETSc has applied them at `KSPSetUp`. **This is not a small-pivot perturbation problem,
and no tuning of the shift can be the remedy.**

**The minimum working intervention, restated with today's arms folded in:**

| route | source change? | reason | iterations | FD agreement | verdict |
|---|---|---|---|---|---|
| serial, np = 1, stock | no | **-9** | 0 | n/a | **BLOCKED** |
| runtime PC **type** — `-sub_pc_type lu` | no | **-9** | 0 | n/a | **BLOCKED** |
| runtime factor **options** — shift type / amount / levels | no | **-9** | 0 | n/a | **BLOCKED** (this section) |
| runtime `zeropivot 1e-8` *(does reach the factor)* | no | **-9** | 0 | n/a | **BLOCKED** |
| **`PCLU` source rebuild**, one hunk | **YES** | **2** | **667** | **0.0854 % / 0.0589 % / 0.1989 %**, zero sign flips | **PASS** |

> **Minimum working intervention = the source rebuild. Nothing cheaper works.** The upstream
> ask stays **F1 + F2 + F3 together**; **F2 alone is now measured insufficient twice over**,
> because relocating `KSPSetFromOptions` cannot help while the block loop overwrites both the
> sub-PC type *and* its factor settings downstream of it.

**Scoring.** Five predictions were registered before the runs; **five hit, zero missed.**
The registered 56.7 core-min came in at **152.53 measured**, of which arm C alone is 125.60 —
an 18.5x load-contention artefact against its own uncontended twins at 99–104 s. **The honest
computational cost of the five arms is 33.7 core-min; 152.53 is what the box charged**, and
both are reported rather than reconciled.

**Nothing in this section was sent anywhere. Filing is Sanaa's call alone.**
