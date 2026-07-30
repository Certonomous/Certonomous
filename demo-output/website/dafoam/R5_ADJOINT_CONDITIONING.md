# R5 — transonic adjoint conditioning: the catastrophic failure mode is fixable, actual convergence is not (yet)

Date: 2026-07-30 (UTC). Docket entry `r5-convergence-wall-not-memory`, approved
2026-07-29. Follows directly from `ADJOINT_MEMORY_ENVELOPE.md`'s headline finding:
the ONERA-M6-family (compressible, transonic, `DARhoSimpleCFoam`) discrete adjoint
returns `PetscConvergedReason -5` (`DIVERGED_BREAKDOWN`) at every mesh size tested
— 21,840, 42,120, 79,560, 99,840 cells — while an incompressible sail-family case
converges cleanly at a larger mesh (63,920 cells). Memory is not the constraint
(smallest failing case peaks at 5.9 GB with >20 GB free). This document is the
measured record of the conditioning investigation itself.

**Reproducer used throughout:** `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840`
(21,840 cells, 4 ranks, ~7 min/attempt).

**Everything below is read from raw solver logs and, where noted, DAFoam's own
printed settings echo (`DALinearEqn.C`'s `printInfo` block) — never from an exit
code or a collector summary alone, per this project's own L-14/L-15/L-16.**

---

## 1. The measurement, first: row/column/diagonal scale spread of the assembled operator

The discrete adjoint's true operator (`dRdWTMF_`, the transpose-Jacobian GMRES
sees) is created via `MatCreateShell` in `DASolver::initializedRdWTMatrixFree`
(`DASolver.C:1345`) with only `MATOP_MULT` registered — it is genuinely
matrix-free (reverse-mode AD product), has no explicit entries, and does not
implement `MatGetDiagonal`. This closes two things at once: there is no way to
inspect the true operator's row/column scale directly, and PETSc's own automatic
equilibration (`-ksp_diagonal_scale`) cannot act on it even if requested, since it
requires `MatGetDiagonal` and the shell doesn't provide one. Alternative PC
families remain compiled-in-only, confirmed again this session directly from
`DALinearEqn.C` (`PCSetType(MLRGlobalPC, PCASM)` / `PCSetType(MLRsubpc, PCILU)`
are hard-coded after `KSPSetFromOptions`, so no `daOptions` lever or PETSc runtime
option can change the PC family without recompiling `libDASolver.so`).

The **preconditioner** matrix (`dRdWTPC`, the reduced-connectivity approximation
ILU actually factors) *is* a real assembled AIJ matrix. Dumped via
`PETSC_OPTIONS="-ksp_view_pmat binary:<path>"` (a standard, unmodified PETSc
runtime flag — no source change) on the unmodified baseline config, then analyzed
offline with `petsc4py`/`scipy` (script: `analyze_scaling.py`, scratchpad):

| quantity | min | max | ratio | log10(ratio) |
|---|---|---|---|---|
| row max-abs | 5.24e-02 | 1.48e+11 | 2.82e+12 | 12.45 |
| col max-abs | 4.42e-02 | 1.48e+11 | 3.34e+12 | 12.52 |
| **diagonal** abs | 9.98e-04 | 1.48e+11 | **1.48e+14** | **14.17** |

200,360×200,360 matrix, 22,017,324 nonzeros, all rows/cols nonzero. A
14.5-order-of-magnitude diagonal spread is essentially the full dynamic range of a
double — exactly the scale of pathology that produces catastrophic cancellation
during ILU factorization and GMRES's own residual recomputation.

## 2. The fix for the catastrophic (denormal-collapse) failure mode: `normalizeResiduals`

`normalizeResiduals` (default ON for `URes/pRes/TRes/nuTildaRes/phiRes/...`,
`pyDAFoam.py` `DAOPTION`) divides each residual row by that cell's volume
(`DASolver::calcPCMatWithFvMatrix`). This mesh family's `checkMesh` output
(already on record in `ADJOINT_MEMORY_ENVELOPE.md`, Option 4) flags 20-28% of
cells for "small determinant" concentrated in one near-wall/tip region — exactly
where a `1/V` row scaling would blow up hardest.

**Setting `"normalizeResiduals": ["None"]`, everything else at the established
baseline, changes the failure signature:**

| config | CD result | CL result |
|---|---|---|
| baseline (`normalizeResiduals` default) | `-5`, residual → `6.6e-310` (denormal) | `-5`, residual → `3.9e-308` (denormal) |
| `normalizeResiduals=None` | `-3`, residual stagnates sanely at ~2.0e-2 | `-3` (isolated run), residual stagnates sanely at ~1.78e-1 |

This is a real, reproduced, independently-verified result — confirmed **three
times**, on both objectives separately (CD alone with default GMRES orthog, CD
alone with `useMGSO=True`, and CL alone in isolation via a
`compute_totals(of=["...CL"])` call added specifically to get this data point).
All three: residual history smooth and sane from iteration 0, never denormal,
genuinely exhausts the full configured iteration budget (`Total iterations: 2000`
matching `GMRES Max Iterations: 2000` from the printed settings echo, not less).
`useMGSO` (modified vs. classical Gram-Schmidt) made no measurable difference —
residual histories agree to 5-6 significant figures with and without it, ruling
out orthogonality loss as the stagnation mechanism specifically.

**Why the two-vs-one-objective count is a red herring, verified from source.**
`DALinearEqn::solveLinearEqn` gates success on
`relResRatio = finalResNorm/initResNorm/gmresRelTol` vs. `gmresTolDiff` (100).
When the residual denormal-collapses toward `0.0`, `relResRatio→0`, trivially
passes the gate, and the code prints **"Residual tolerance satisfied, solution
finished!"** — a false positive — letting OpenMDAO continue to the next
objective. This is the exact L-15 pattern, caught live and mechanistically this
session: every `-5` run prints "satisfied" (denormal-fooled) and reports two
objectives; every `-3` run prints "not satisfied" (honest) and correctly aborts
via `AnalysisError` before the second objective is ever attempted. A genuinely
truncated run (killed, OOM'd) looks nothing like either — it stops mid-print with
no `**Completed**!` line at all (observed directly, once, in an early attempt
this session that was killed before this distinction was understood).

## 3. No preconditioner strengthening tried has produced actual convergence

Starting from the confirmed-sane `normalizeResiduals=None, pcFillLevel=0`
baseline (which stagnates, never converges, never collapses):

| variant | result |
|---|---|
| `pcFillLevel: 0→1` (stronger local ILU) | `-5` on **both** CD and CL, collapsing to exactly `0.0` **precisely at iteration 1000 — the GMRES restart boundary** |
| `globalPCIters=3, localPCIters=3` (nested-Richardson-wrapped ASM+ILU, the literature-precedented lever from Kenway et al. 2019, previously unused in this codebase; settings confirmed via printed echo) | Identical signature: `-5` on **both** CD and CL, collapsing to exactly `0.0` at iteration 1000, the restart boundary |

Four independent solves (fill1×2, Richardson×2) now show the identical
signature: smooth, sane residual decay right up to the restart boundary, then
exact collapse at the restart recomputation itself. Both attempts to strengthen
the preconditioner beyond the "sane but stagnant" baseline reintroduced the
catastrophic failure rather than fixing the stagnation. Raising `gmresMaxIters`
alone (2x budget, full restart length 1000) does not help either — the baseline
residual is flat, not slowly converging (iter 1000→2000: 2.0138e-2→2.0136e-2 for
CD; near-identical for the MGSO variant).

## 4. Jacobian colouring count: checked, does not discriminate

Retrieved directly from each case's `dRdWColoring_N.bin` (loaded via `petsc4py`,
`nJacConColors = max(color)+1`; cross-validated against the `dRdWTPC: k of N`
runtime progress line, which matches exactly):

| case | cells | family | colours | outcome |
|---|---|---|---|---|
| A1 naca0012 | 4,032 | incompressible | 373–380 (2/4/8 ranks) | converges |
| naca0015 sail_coarse | 63,920 | incompressible | **1,999** | converges |
| A3 M6 n15 | 21,840 | compressible/transonic | 1,233 | diverges |
| A3 M6 n28 | 42,120 | compressible/transonic | 1,315 | diverges |
| A3 M6 probe80k | 79,560 | compressible/transonic | 1,355 | diverges |
| A3 M6 coarse (4 rank) | 99,840 | compressible/transonic | 1,391 | diverges |
| A3 M6 coarse (8 rank) | 99,840 | compressible/transonic | 1,325 | diverges |
| A2 mach wing | — | compressible/transonic | 1,323 | (not adjoint-verified) |
| A4 Ahmed coarse | 2,777 | incompressible | 1,343 | (converges per Group 1 register) |

The converging incompressible sail case needs **more** colours (1,999) than any
diverging compressible case (1,233–1,391); the converging A1 case needs far
fewer. Colour count does not separate working from breaking cases in this data.
DAFoam's colouring cost being high in absolute terms relative to the literature
reference (Kenway et al. 2019: 945 for DAFoam vs. 162 for ADflow, on a much
larger mesh) is a real, separate architectural finding — it is not, on this
evidence, the mechanism behind this specific breakdown.

## 5. Conclusion, stated at the precision the evidence supports

- **The catastrophic failure mode (residual collapsing to denormal range,
  `PetscConvergedReason -5`) is conditionable.** `normalizeResiduals=None` fixes
  it, reproducibly, on both objectives independently, with and without MGSO.
  This is real progress: the earlier framing ("every M6-family adjoint attempted
  ends in breakdown, no exceptions") is now known to be a fixable numerical
  artifact of a specific, identified scaling choice, not an unconditional
  property of the case.
- **No configuration tried converges.** The confirmed-sane baseline stagnates
  (flat residual, ~4 orders of magnitude from the 1e-4 relative tolerance, no
  further progress across a restart cycle); every attempt to strengthen the
  preconditioner enough to make progress (raise ILU fill, or wrap it in
  literature-precedented nested Richardson iterations) reintroduces the exact
  same collapse, specifically at the GMRES restart recomputation.
- **No gradient has been obtained or verified at this mesh size**, under any
  configuration. The finite-difference verification rule this investigation was
  bound by (never claim a gradient without checking it) was never reached
  because nothing converged to check.
- **What is now a sharper, more specific open question than "is this
  conditionable at all":** why does strengthening the local preconditioner
  reintroduce collapse specifically at the restart boundary? That is a
  narrower, more mechanistically pointed question than the one this docket
  entry opened with, and it is the natural next thread — candidates include:
  the restart's residual recomputation (`r = b - Ax`) suffering catastrophic
  cancellation against a now-much-closer-to-exact iterate under a stronger PC,
  or a genuine remaining ill-conditioning (the diagonal spread measured in §1
  was on the *default* preconditioner matrix, before `normalizeResiduals` was
  removed — that matrix has not been re-measured under the fixed configuration
  and is the next cheap, high-value measurement queued here).

## Raw logs

Registry (survive session interruptions):
`demo-output/website/solve_registry/r5_measure_scaling_n15_*`,
`r5_noresnorm_n15_*`, `r5_noresnorm_bigbudget_n15_*`, `r5_noresnorm_fill1_n15_*`,
`r5_noresnorm_mgso_n15_*`, `r5_noresnorm_cl_only_n15_*`,
`r5_noresnorm_richardson_n15_*`. Matrix dumps and analysis script under
`/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7/scratchpad/`
(`analyze_scaling.py`, `count_colors.py`, scratch only, not committed). Case
scripts (committed, in the reproducer case dir): `runScript_noresnorm.py`,
`runScript_noresnorm_bigbudget.py`, `runScript_noresnorm_fill1.py`,
`runScript_noresnorm_mgso.py`, `runScript_noresnorm_cl_only.py`,
`runScript_noresnorm_richardson.py`, `runScript_mgso.py`,
`runScript_mgso_restart1000.py`, `runScript_mgso_sparsify.py`.

## A tooling note, disclosed because it produced a real false signal mid-session

`scripts/launch_solve.sh`'s completion collector wrote one `.done` record
claiming a job had finished in the same second it started, while `ps`/`docker
ps` directly showed the container and its process tree still alive and actively
computing several minutes later (root cause not fully pinned down — a direct
`kill -0` against the same PID, tested manually moments later, succeeded
normally). Worked around for the rest of this session with a thin, ubuntu-owned
wrapper script (`docker_wrap.sh`, scratchpad) around `sudo docker run`, and by
independently verifying every job's real completion via `ps`/`docker ps` rather
than trusting the `.done` file alone. Flagged here rather than silently worked
around because it is the same class of error (trusting a derived completion
signal over the primary process state) this project has already named twice
(L-15, L-16).
