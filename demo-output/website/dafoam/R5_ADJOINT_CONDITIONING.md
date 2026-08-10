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

**No finite-difference gradient verification was performed, on any
configuration, at any point in this investigation.** This project's own rule
(stated in the directive this work follows) is that a converged solve must be
checked against a finite difference before its gradient is trusted. Nothing
converged — every configuration tried returned either `DIVERGED_BREAKDOWN` or
`DIVERGED_ITS` — so there was never a converged gradient to check. Read no
claim below as a statement about gradient correctness; none was tested.

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

## 5. The queued measurement, closed: the scale spread does NOT collapse under `normalizeResiduals=None`

The first `normalizeResiduals=None` attempt this session (`r5_noresnorm_n15`,
the run whose collector record was initially misread as truncated — see the
tooling note below) had `-ksp_view_pmat binary:...` enabled and produced a
complete, valid 265 MB dump before anything else happened to it (PC-matrix
assembly and the binary write both complete before GMRES iteration begins, so
this data is unaffected by anything that happened later in that run). Analyzed
with the same `analyze_scaling.py`, same matrix dimensions (200,360×200,360)
and identical nonzero count (22,017,324 — same sparsity pattern as the
baseline, values only differ):

| quantity | baseline (`normalizeResiduals` default) | `normalizeResiduals=None` |
|---|---|---|
| row max-abs ratio | 2.82e+12 (log10 12.45) | 1.06e+12 (log10 **12.02**) |
| col max-abs ratio | 3.34e+12 (log10 12.52) | 1.37e+16 (log10 **16.14**) |
| **diagonal** abs ratio | 1.48e+14 (log10 14.17) | 1.37e+16 (log10 **16.14**) |

**The spread did not collapse — the diagonal spread got worse (14.17 → 16.14
orders of magnitude), not better.** `normalizeResiduals=None` fixes the
specific arithmetic pathway that produced denormal collapse (§2) without
improving, and by this measure slightly worsening, the underlying matrix's own
conditioning. This directly answers the question this document left open:
**there is a second, still-live layer of ill-conditioning**, separate from the
1/cell-volume residual scaling. The most likely remaining candidate,
un-investigated here: `normalizeStates` applies one global scalar per field
(`U:291.6, p:101325, nuTilda:4.5e-4, phi:1.0, T:300`) uniformly across all
21,840 cells; it cannot compensate for the same near-degenerate,
concentrated-region cells (checkMesh's "small determinant" flag) the way the
now-removed volume normalization was — over-compensating, per this
measurement — doing locally. This is consistent with, and gives a concrete
mechanism for, why strengthening the preconditioner (§3) reintroduces
collapse: a more accurate local solve is more able to resolve — and therefore
more exposed to — a genuinely still-enormous matrix-scale disparity that a
weaker preconditioner simply never gets close enough to to trigger.

Per instruction, no further lever was tried after this measurement.

## 6. Conclusion, stated at the precision the evidence supports

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
- **The follow-up measurement (§5) closes the question §1-4 left open, and
  the answer is that residual scaling was never the whole story.** Under
  `normalizeResiduals=None`, the assembled preconditioner matrix's diagonal
  spread is 16.14 orders of magnitude — *worse* than the 14.17 measured on
  the default-normalized baseline, not better. Fixing the denormal-collapse
  arithmetic did not touch the underlying matrix conditioning. There is a
  second, still-live, un-fixed layer of ill-conditioning, and the leading
  candidate is `normalizeStates`' single global per-field scalar failing to
  compensate for the same concentrated near-degenerate region that
  `checkMesh` already flags. This also supplies a concrete mechanism for §3:
  a weaker preconditioner (fill=0) never resolves the operator accurately
  enough to expose that remaining disparity and merely stagnates; a stronger
  one (fill=1, Richardson) gets close enough to trigger the same catastrophic
  cancellation the residual-scaling fix already eliminated once, at a
  different arithmetic site.
- **Per instruction, no fifth lever was attempted.** The natural next thread
  — a per-cell or per-region state normalization that targets the specific
  mesh region `checkMesh` flags, rather than one global scalar per field —
  is a real candidate but is not started here.

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

## 2026-08-08 retroactive dead-lever annotation (ordered by the chief; dead-lever audit `DEAD_LEVER_AUDIT_2026-08-08.md`, 946e4a26)

Every M6-family run this record measures echoed `transonicPCOption 2;` in its
daOptions dump (all seven `r5_*` campaign logs at `:489`;
`run_opt5_onera_n15_21840.log:410`). **That value is dead code for
`DARhoSimpleCFoam`: `DAResidualRhoSimpleCFoam.C:173` accepts only `== 1`;
`== 2` exists only in `DAResidualTurboFoam.C:176`. No archived M6 adjoint —
here or anywhere — ran with an active transonic preconditioner** (finding:
`A3_SUBLU_PREREGISTRATION.md` §2, 12d3a7a3; entry-8 outcome blocks 08a87cc7,
5f0c328e). Nothing in this record's conclusions is altered: the record never
claimed the transonic PC had been tried, and the `-5`/`-3` characterization,
the `normalizeResiduals` finding, and the fill/Richardson/budget arms stand as
measured — measured, as now stated explicitly, with the transonic PC OFF.
Whether an ACTIVE transonic PC moves the M6 wall is an open question; the
PC-alone arm now running is the live test of exactly that.

## 2026-08-10 RETRACTION — §3's central conclusion was produced by the dead lever (ordered by the chief; lever triage `A3_TRIAGE_LEVERS_PREREGISTRATION.md` §8, 3ac8257e)

The 2026-08-08 annotation above established that the transonic preconditioner was
INACTIVE in every run this record measures. It did not say **which of this
record's conclusions that inactivity produced.** It is now measured, and the
answer is §3's headline.

**RETRACTED: "every attempt to strengthen the preconditioner reintroduces the
exact catastrophic collapse" (§3; restated at §§179, 197–199, 217).** That
statement is true of the runs that were made and FALSE as a property of this
solver family. It is an artifact of the dead lever.

**The measurement that retracts it.** On the same 21,840-cell reproducer this
record uses, with one token changed (`transonicPCOption` 2 → 1, i.e. the PC
actually ON) and nothing else, both strengthening levers this record indicts
converge — and they are the two largest iteration cuts on the board:

| lever (this record's own settings) | R5 result (PC dead) | 2026-08-10 result (PC active) |
| --- | --- | --- |
| `pcFillLevel: 1` | `-5`, collapse to 0.0 at the restart boundary | **reason 2**, CD 236 / CL 250 iterations (−35.9% / −34.7% vs the PC-active baseline 368/383), wall −4.5% |
| `globalPCIters=3, localPCIters=3` (nested Richardson) | `-5`, identical collapse signature | **reason 2**, CD 209 / CL 211 iterations (−43.2% / −44.9%), wall +20.9% |

Four solves that collapsed with the PC dead; four that converge with it active,
each with `transonicPCOption 1;` and the lever's own echo verified in the log
(`ILU PC Fill Level: 1`; `Global PC Iters: 3` / `Local PC Iters: 3`), cold-start
signature `0.5969274433533561`, and no sub-LU (env unset).

**Why the old result happened, stated as mechanism rather than apology.**
`transonicPCOption 1` drops `fvm::div(phid, p)` from the PC-matrix pressure
equation (`DAResidualRhoSimpleCFoam.C:172–176`) — the MDO-lab lineage's
deliberate *weakening* of the transonic PC toward diagonal dominance. With that
term wrongly retained, the PC matrix is a bad approximation to begin with, and
strengthening its factorization (more fill, more Richardson sweeps) resolves the
wrong operator harder — which is exactly how §3's collapse was manufactured.
With the term correctly dropped, ordinary numerical-linear-algebra intuition
returns: a stronger preconditioner takes fewer Krylov iterations. **This
retraction therefore removes an anomaly from the record rather than adding one**
— §3's §179/§197 "no mechanism for why strengthening reintroduces collapse" no
longer requires a mechanism, because the phenomenon was configuration-induced.

**What still stands, unchanged:** the `-5`/`-3` characterization of the runs as
made; the `normalizeResiduals` finding; the matrix-scale and diagonal-spread
measurements (order-of-magnitude readings, robust to the state drift the
warm-start audit flagged, `WARMSTART_AUDIT.md` row 7); the L-14/L-15/L-16
process findings; and this record's own disclosure that no FD verification was
performed here. What is retracted is one causal conclusion — that preconditioner
strengthening cannot work on this family — and the two headline claims that rest
on it.

**Superseding evidence:** the transonic-PC finding (`A3_SUBLU_PREREGISTRATION.md`
§2, 12d3a7a3), the negative control reproducing the record `-5` bit-for-bit while
the flipped token converges (551a7ba5), two converged and FD-verified rungs
(11b90d25 at 21,840 cells; 4e982b4a at 42,120 cells, FD 0.0077%/0.2740%/0.0172%),
and the lever triage above (3ac8257e). This is the **second** standing conclusion
the dead lever corrupted — the first being the conditioning wall itself. Routed
by the chief to the defect report's owner.

### 2026-08-10, SAME DAY — CORRECTION TO THE RETRACTION ABOVE. I over-corrected; §3's phenomenon is REAL, and mesh-dependent.

The retraction above was written at 15:41Z from three converged rung-1 arms. At
15:44Z the rung-3 stage-0 transfer arm returned, and it falsifies part of what I
had just written. Recording it with the same prominence as the claim, per this
family's own rule, and before the retraction travels any further.

**The measurement.** L3 Richardson (`globalPCIters=3, localPCIters=3`) at
**42,120 cells with the transonic PC ACTIVE** (`transonicPCOption 1;` verified in
the DAOption dump; cold signature `0.6833296303785072`; no sub-LU; the ONLY
change from the arm that converged at CD 987 / CL 1171 is the Richardson lever):

```
**Completed**! Total iterations: 200. PetscConvergedReason: -5.  152.66 s   (CD)
Main iteration 200 KSP Residual norm 9.490658670647e-154
**Completed**! Total iterations: 200. PetscConvergedReason: -5.  228.32 s   (CL)
Main iteration 200 KSP Residual norm 0.000000000000e+00
```

**Collapse to exactly 0.0 at iteration 200 — which is `gmresRestart`, the first
restart boundary.** That is §3's signature reproduced verbatim ("collapsing to
exactly `0.0` … at the restart recomputation itself"), on a live preconditioner.

**What is therefore withdrawn from my own retraction:** the sentence "that
statement is true of the runs that were made and FALSE as a property of this
solver family", and the framing of §3's collapse as "configuration-induced". The
collapse is **not** an artifact of the dead lever. It is real, and the dead lever
was not its cause.

**What survives, and what the pair of measurements actually establishes.** The
two results are not in conflict once mesh size is admitted as the variable:

| mesh | PC | fill1 | Richardson |
| --- | --- | --- | --- |
| 21,840 (rung 1) | ACTIVE | reason 2, 236/250 iters | reason 2, 209/211 iters |
| 42,120 (rung 2) | ACTIVE | not tested | **`-5`, collapse at iteration 200** |
| 21,840 (R5, as recorded) | DEAD | `-5`, collapse | `-5`, collapse |

**Refined mechanism, offered as the hypothesis the data supports and not more.**
Both rung-1 strengthened arms converged in 209–250 iterations — i.e. within
roughly ONE restart cycle of the 200-iteration `gmresRestart`, meeting their
first restart with an already-tiny residual. The rung-2 Richardson arm met its
first restart with the residual still at ~1.4e−01 and collapsed there. So the
candidate rule is: **a strengthened preconditioner destabilises the GMRES restart
recomputation, and whether that bites depends on whether convergence completes
before the restart matters — which is a function of mesh size.** On that reading
R5 saw collapse at 21,840 cells because the dead PC left it far from convergence
at its restart, while an active PC at the same size finishes first. This is a
hypothesis with two supporting points and one prediction (fill1 should also
collapse at 42,120 cells, untested); it is not established, and it is labelled so.

**Net effect on §3.** Its *observation* stands, reproduced. Its *scope* was too
broad: "every attempt to strengthen reintroduces collapse" is false at
21,840 cells with the PC active, true at 42,120 cells with the PC active. Its
"no mechanism" caveat (§§179, 197) stands as honestly as before — the restart
hypothesis above is the first candidate mechanism this record has, and it is
mine, unproven.

**Consequence for the ladder, recorded here because it is where the reasoning
lives:** the pre-registered plan to adopt Richardson for rung 3 is VOID. Rung 3
runs the baseline configuration (`A3_RUNG3_N52_PREREGISTRATION.md` §3's own
stage-0 failure branch), which is what was launched.
