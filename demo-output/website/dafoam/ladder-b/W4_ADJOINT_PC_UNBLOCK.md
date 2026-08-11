# W4 — the adjoint conditioning blocker: located to the sub-block factorization, fixed by a one-word PC change, and measured end to end

Date: 2026-08-04 (UTC). Docket item `fiml-adjoint-conditioning-unblock` (W4, approved
2026-07-31, 240 core-min). Claimed on the docket at 15:04Z before any work ran.
All container runs `dafoam/opt-packages:latest` (DAFoam v5.0.0, OpenFOAM v2506,
PETSc 3.15.5) or the locally patched image `dafoam-subpclu:v1` built from it (section 4).
Working copies and logs: `/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/`.
Provenance inputs: `S1_FIML_FIELD_INVERSION.md` (the `-9` blocker and the mechanism
ladder), `PROOF.md` §25.2–25.3 (the ordering sweep and the singular-ILU dump analysis),
`R5_ADJOINT_CONDITIONING.md`, and the liaison memo
`LIAISON_RESEARCH_adjoint_conditioning.md` (2026-08-04), which arrived mid-session
and is answered point by point in section 6.

## Headline

1. **The CBFS adjoint converges — `PetscConvergedReason: 2`, 667 iterations — on B3's
   exact `-9` configuration, changed only by switching the ASM sub-block preconditioner
   from incomplete LU to complete LU.** First converged adjoint linear solve on any
   closure-relevant blocked case in this lab.
2. **The CBFS field-inversion (beta) gradient exists** — same converged solve
   (reason 2, 667 iterations, identical operator; only the objective's RHS use
   changes with the design variable), 21,000 beta components, FD verification in
   section 5c.
3. **On the hump, the same one-word change moves the failure from catastrophic to
   honest: `-9` NaN at iteration 0 becomes a factorization that completes and a
   residual that descends monotonically (1.094 → 0.954 over 900 iterations) —
   but does not converge**, and the run was stopped deliberately at ~iteration 900
   when host MemAvailable fell to 1.6 GB on a shared box. The singular-factor
   mechanism is cured in-solver; what remains on the hump is slow Krylov
   convergence against a memory envelope, which is a different, honestly-named
   problem (section 5b).

   > **Correction, dated 2026-08-11 (hump-adjoint attempt audit).** The last sentence of
   > headline 3 overstates what this session measured, and the standing programme account
   > it seeded — *"the hump is blocked on convergence rate, not singularity"* — is
   > withdrawn as a causal claim. The measurements stand exactly as written: the `-9` is
   > gone, the residual descends 1.094138002900e+00 → 9.544468674795e-01 over 900
   > iterations, the run was killed by `docker stop` at MemAvailable 1.62 GB. What does
   > not follow is *what remains*. **No `KSPConvergedReason` was ever produced** (verified
   > 2026-08-11: `hump_sublu_computetotals.log`, 2,279 lines, contains the string
   > `ConvergedReason` zero times and ends at the iteration-900 residual line), so the
   > convergence rate was never measured to completion; and the run was stopped by an
   > operator on a shared box rather than by an allocation failure, so the memory envelope
   > was never shown to be *binding*. "We observed no convergence in the 900 iterations we
   > ran" is true. "The blocker is convergence rate rather than singularity" is a causal
   > claim requiring evidence that does not exist. The opposite is not asserted either —
   > nothing here shows the operator *is* singular or near-singular; curing a singular ASM
   > *sub-block* factorization says nothing about the matrix-free global operator GMRES is
   > actually applying (the operator/PC mismatch this same document names in §5a). **The
   > hump adjoint boundary is uncharacterised.** The specific missing measurements are
   > named and priced in §5b.1.

4. **The runtime-options escape hatch exists but is empty.** Contrary to the standing
   belief (R5, PROOF §25.3, and the liaison memo's Lead 1.3) that no PETSc runtime option
   reaches the sub-PC, `sub_`-prefixed *factor* options ARE consumed — measured, not
   argued: `-sub_pc_factor_zeropivot 1e-8` visibly lands in the deployed factor
   ("tolerance for zero pivot 1e-08" in `PCView`). They are read because
   `KSPSetFromOptions(ksp)` at `DALinearEqn.C:138` marks the PC, and PETSc's
   `PCSetUp_ASM` then calls `KSPSetFromOptions` on each newly created sub-KSP during
   `KSPSetUp` (line 230) — *before* DAFoam's hard-coded per-block overrides run. What
   survives is exactly the set DAFoam never touches afterward: `nonzeros_along_diagonal`,
   `zeropivot`, `diagonal_fill`, `mat_solver_type`. **Every one of them was tested and
   none fixes the failure** (section 2), so the rebuild was justified by measurement,
   not convenience.
5. **The liaison memo's fixedPoint bypass (Lead 1.4) is structurally unavailable for
   FIML, refuted at zero compute** (section 6).

## 1. The offline reproducer: DAFoam's exact PC stack, rebuilt in petsc4py on the dumped system

PROOF §25.3's dumped CBFS system (`dRdWTPC` 210,592², nnz 13,710,468, plus the RHS
whose norm matches the printed iteration-0 residual to 13 digits) was solved with a
petsc4py harness (`pc_ladder.py`) that replicates `DALinearEqn::createMLRKSP`'s call
sequence *in order* — `KSPSetFromOptions` first, hard-coded GMRES/ASM/sub-ILU settings
second — under `mpirun -np 4`, the real layout. Control run, zero deviations:

```
RESULT reason -9 its 0 finalres 7.091590452305e-04 wall 7.01s
```

Bit-for-bit DAFoam's failure — same reason, same iteration count, same residual —
with `PCView` confirming full parity (ILU fill 1, ordering rcm, shift NONZERO,
pivot-in-blocks, zeropivot 2.22e-14). This harness makes every candidate an ~10-second
experiment instead of an 8-core-minute solver launch, and it measures *reachability*
(what the deployed factor actually contains) at the same time as *mechanism*.

## 2. Route 1 — runtime options: reachable, measured, and empty

| variant (all runtime-reachable via `PETSC_OPTIONS`) | deployed-factor evidence | result |
|---|---|---|
| control (parity with DAFoam) | zeropivot 2.22e-14, rcm, shift NONZERO | **-9**, iter 0 |
| `-sub_pc_factor_nonzeros_along_diagonal` | (diagonal already has no zeros — PROOF §25.3) | **-9**, iter 0 |
| `-sub_pc_factor_zeropivot 1e-8` | "tolerance for zero pivot 1e-08" in PCView — **the option reached the factor** | **-9**, iter 0 |
| `-sub_pc_factor_diagonal_fill` | applied | **-9**, iter 0 |

Two conclusions, one per column. **Reachability:** the factor options land, so the
"compiled-in, nothing reachable" statement in R5/PROOF §25.3 is too strong and is
corrected in section 6. **Mechanism:** a 1e-8 zero-pivot threshold with
`MAT_SHIFT_NONZERO` active still produces the NaN — so this is *not* a
small-pivot-below-threshold event the shift machinery could catch. Combined with the
liaison memo's PETSc-developer quote (the NaN can arise "in the first attempt to do a
triangular solve"), the failure is factor growth: enormous elements in L/U that
overflow when applied, which no shift and no diagonal permutation fixes — only
pivoting or completeness does. This also explains, mechanically, why the record's
`spilu` said "exactly singular" at every drop tolerance while `splu` at every pivot
threshold succeeded (PROOF §25.3's table).

## 3. Route 3 mechanism test, offline: complete LU in the sub-blocks

Same harness, one change — `PCSetType(subpc, PCLU)` where DAFoam hard-codes `PCILU`:

| sub-PC | ordering | reason | iterations | wall | per-block factor size |
|---|---|---|---|---|---|
| ILU(1) (DAFoam) | rcm | **-9** | 0 | 7.0 s | 6,963,844 nnz (before NaN) |
| **LU** | rcm | **2 (converged)** | 347 | 68.0 s | 100,311,134 nnz (~0.8 GB) |
| LU | nd | did not finish | — | killed at 600 s | — |

The `nd` row is an operational finding worth keeping: PETSc's native LU under its own
nested-dissection ordering is pathologically slow on these blocks — `rcm` is the
ordering that works with complete LU here, the exact reverse of its role under ILU,
where rcm is the ordering that surfaces the NaN.

## 4. The rebuild: `DAFOAM_SUBPC_TYPE=lu`, off by default, regression-controlled

`PCSetType(MLRsubpc, PCILU)` is hard-coded (`DALinearEqn.C:266–267`), so complete LU
needs a recompile. The patch adds an environment-variable switch at that line — when
`DAFOAM_SUBPC_TYPE=lu` is set, `localPCType` becomes `PCLU`; otherwise not one line of
behavior changes. Recipe (also in `run_dir/` as scripts, ~40 s of compile):

```
docker run -d --name dafoam-build dafoam/opt-packages:latest sleep infinity
# patch src/adjoint/DALinearEqn/DALinearEqn.C (see repo diff in this commit)
# then, inside the container, for each of the three AD modes:
source /home/dafoamuser/dafoam/loadDAFoam.sh          # original
cd repos/dafoam && wmakeLnInclude src/adjoint && (cd src/adjoint && wmake -j 8)
# ADR and ADF: sed WM_AD_MODE in OpenFOAM-AD/etc/bashrc, re-source, wmake again
docker commit dafoam-build dafoam-subpclu:v1
```

(Caution from a lost first attempt: `set -e` before sourcing the OpenFOAM environment
kills the shell — source first.) All three `libDASolver*.so` relink in seconds; the
image is local only, nothing pushed.

**Regression control, run before the treatment:** the patched image with the env var
*unset* reproduces the CBFS `-9` at iteration 0 exactly (92 s wall, rc=1). The rebuild
is behavior-neutral by default.

## 5. The measurement that matters

### CBFS (21,000 cells, B3's exact runScript: rcm, pcFillLevel 1, varianceU/patchV)

```
DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU
Main iteration 0    KSP Residual norm 7.091590452305e-04
Main iteration 400  KSP Residual norm 6.488778512831e-04
Main iteration 500  KSP Residual norm 1.778417281485e-05
Main iteration 667  KSP Residual norm 6.922418564747e-10
**Completed**! Total iterations: 667. PetscConvergedReason: 2. 232.2 s
```

Objective 0.01527928, totals d(varianceU)/d(patchV) = [-0.12000398, -0.00013987].
243 s wall, 4 ranks, 16.2 core-min. The residual history is the operator-vs-PC caveat
of PROOF §25.3 made visible: the first 400 iterations crawl (the assembled `dRdWTPC`
the LU inverts is not the matrix-free `dRdWTMF` GMRES applies), then the Krylov space
catches the dominant cluster and the residual falls six decades in 267 iterations.
The offline solve — same PC, but operator = PC matrix — converged in 347. Slow-then-
superlinear is what a correct strong PC on a mismatched operator looks like; flat-to-
thirteen-digits is what the record's dead ILU looked like. They are not the same thing.

### 5b. NASA hump (51,626 cells, 51,626 beta DVs): signature moved, not yet converged

S1's exact `runScript_hump.py` (rcm, pcFillLevel 1, `gmresMaxIters/Restart` 2000),
only the env var added. Two staging faults first, both recorded: the pristine copy
needs the case-root `caseDef`/`fieldDef` include files (`decomposePar` fails with a
clean IO error without them), and the case's `#calc` entries make OpenFOAM refuse to
run as root ("administrator rights ... dlopen") — the container must run as
`-u 1002:1002`, which is what S1's own `dfrun.sh` always did.

The run itself:

```
OBJ cfVar: 1.6263651522923017e-01        <- bit-identical to S1's baseline objective
DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU
Main iteration 0   KSP Residual norm 1.094138002900e+00   <- S1's exact initial residual
Main iteration 300 KSP Residual norm 1.032648117246e+00
Main iteration 600 KSP Residual norm 9.926576665760e-01
Main iteration 900 KSP Residual norm 9.544468674795e-01
```

**The `-9` is gone from the hump too: the complete-LU factorization of the same
blocks that ILU cannot factor completes, and GMRES iterates with a monotonically
descending residual.** It descends slowly — 12.8% in 900 iterations, accelerating
(0.75%, 1.1%, 1.2%, 1.6% per successive 100) but far from the 1e-6 relative target.
The run was **stopped by this session at ~iteration 900** (`docker stop`, rc=1 —
the rc is the kill, not a KSP verdict; no KSPConvergedReason was reached): host
MemAvailable had fallen from 30.5 GB to a low-water **1.62 GB** (`hump_sublu_mem.log`,
5 s cadence) under the ~19 GB of LU factors plus a 2000-vector restart space still
filling, on a box other sessions were using. 819 s wall, 54.6 core-min.

Stated for whoever picks this up: the hump blocker is **no longer the singular
factorization — it is Krylov convergence rate against a memory envelope.** The
prepared next config (`runScript_hump_rich.py`, staged but not run, budget) wraps
the exact sub-solve in Richardson (`globalPCIters: 3`) and caps `gmresRestart` at
500 so the basis stops growing; whether that converges is an open measurement.

> **Correction, dated 2026-08-11 (hump-adjoint attempt audit).** The "stated for whoever
> picks this up" sentence immediately above is withdrawn as written, and with it the
> programme account it seeded. Everything else in §5b is measurement and stands; this
> paragraph alone was inference presented in the voice of a result.
>
> What the log supports, re-verified against `hump_sublu_computetotals.log` on 2026-08-11:
> the `-9` does not appear, the residual descends monotonically to 9.544468674795e-01 at
> iteration 900, and the log ends there. It contains the string `ConvergedReason` **zero
> times** in 2,279 lines. Therefore:
>
> - **The convergence rate was never measured to completion.** 12.8% in 900 iterations
>   against a 1e-6 relative target is a rate *over the interval we ran*; extrapolating it
>   to "the blocker" requires a solve that terminated on its own criterion, and none did.
> - **The memory envelope was never shown to be binding.** The run ended in a `docker stop`
>   issued by this session because a shared box was down to 1.62 GB — that is where we
>   chose to stop, not where the case fails. No allocation failure, no OOM kill, no
>   PETSc memory error is on the record for this run.
> - **"Not singularity" does not follow from the sub-LU repair.** What sub-LU repaired is a
>   singular *ASM sub-block incomplete* factorization. GMRES here applies the matrix-free
>   `dRdWTMF`, not the assembled `dRdWTPC` the LU inverts — the operator/PC mismatch §5a
>   makes visible on CBFS. A well-behaved preconditioner says nothing about the rank or
>   conditioning of the operator being preconditioned.
> - **The opposite claim is equally unsupported.** No rank, condition-number, or
>   singular-value measurement exists on the hump operator. Nothing here shows it *is*
>   singular. The unexplained flat-to-13-digits stagnations of the `normalizeResiduals`
>   and `natural`-ordering arms (2026-07-31, `hump_nrn_run1.log` at 2000 iterations and
>   `hump_nat_run1.log` at 1000) were superseded by this run and never explained, and they
>   are the one piece of evidence that bears on the question in either direction.
>
> **The honest position: the NASA-hump adjoint boundary is uncharacterised.** It is not a
> measured capability boundary, and it should not be cited as one. §5b.1 names the
> measurements that would make it one and prices them.

### 5b.1 What would convert the assumed boundary into a measured one (work item, added 2026-08-11)

Nothing below has been run. This section authorises no compute; the director does. Every
price is anchored on this run's own measured numbers: 819 s wall at np=4 = 54.60 core-min
total; iteration 0 printed at 174.97 s and iteration 900 at 728.48 s, i.e. **0.615 s per
iteration wall = 0.041 core-min per iteration at np=4**; primal 10.583 s; the pre-solve
segment (stage, primal, coloring, factorization, to the iteration-0 print) ≈ 175 s wall
≈ 11.7 core-min.

| # | measurement | what it converts | price (core-min) | basis |
|---|---|---|---|---|
| **M1** | Dump the hump's `dRdWTPC` and RHS and run the **existing** offline `pc_ladder.py` harness on them (exact LU solve of the assembled system, pivot and condition statistics), exactly as PROOF §25.3 did for CBFS | Decides **singular vs ill-conditioned vs merely slow** offline, without a single long solve. This is the measurement whose absence makes the boundary an assumption | **25** (one assembly-to-dump run ≈ the pre-solve segment plus write-out); each offline variant thereafter ~10 s at np=4, **<1 each** | §1 built and validated this harness on CBFS at ~10 s per experiment |
| **M2** | **The negative control that has never been run on this case**: A6's exact configuration with `DAFOAM_SUBPC_TYPE` unset, same image, cold case dir | Makes the `-9` → sub-LU attribution reproducible **on the hump** instead of inherited from CBFS. The programme has an env-off control on CBFS and **none** on the hump | **15** (returns at iteration 0) | pre-solve segment 11.7 + teardown |
| **M3** | Deliberate reproduction of A6 itself, switch on, to iteration 900 | The **first deliberate reproduction of any hump adjoint attempt** in the programme (11 attempts, 0 reproduced). Gate: residual reproduces to 13 digits at iterations 0/300/600/900 | **55** | A6's own measured spend, 54.60 |
| **M4** | Run to a reason code: same configuration, `gmresMaxIters` 2000 as already set, on a host that can hold ~19 GB of LU factors **plus** a fully-grown 2000-vector restart basis | Converts "no convergence observed in 900 iterations" into a **measured rate with a terminating `KSPConvergedReason`** (2, or -3 at the cap). Without this the rate claim cannot be made at all | **100** (54.60 + 1,100 further iterations × 0.041) | measured per-iteration cost |
| | *host caveat, itself a finding* | On the 30.5 GB box this run used, M4 stops for the same non-reason again. **M4 needs ≥64 GB**, or it does not produce the measurement it is bought for | — | MemAvailable 30.5 → 1.62 GB by iteration 900 with the basis still filling |
| **M5** | Memory-binding test: A10's staged-and-never-run `runScript_hump_rich.py` (Richardson `globalPCIters: 3`, `gmresRestart` capped at 500), with the 5 s `MemAvailable` watcher | Decides whether **memory is binding at all**. A capped basis either reaches a reason inside the envelope or dies on an allocation — and *either* outcome is a measurement, where the present record has neither | **150**, flagged: this is the one line carrying an **unmeasured multiplier** (up to 3 global PC iterations per Krylov step); 150 is the 1× figure and could be up to ~3× | 2,000 × 0.041 = 82 at 1× plus wrapper overhead |
| **M6** | Explain the A4/A5 stagnation: write `psi` at a checkpoint from M3 or M4 and apply the A4 cross-residual instrument (`DISCRIMINATORS_A4_decomposition_mechanism.md`, M1 discriminator) | The flat-to-13-digits arms are the **only** existing evidence bearing on singular-vs-slow, and they were superseded, never explained. This is the instrument that already exists for exactly this question | **20** on top of M3/M4 | the A4 discriminator's own deciding arms cost ~12.80 |

**Sequencing.** M1 + M2 first: **40 core-min buys the singular-or-not answer offline plus
the negative control the programme never ran** — and if M1 returns a singular or
catastrophically ill-conditioned assembled operator, M4 and M5 should not be bought at all.
M3 next at 55. M4/M5/M6 only after M1 has said which of them is worth its price.

**Total M1–M6: 365 core-min**, of which 40 are decisive-cheapest.

**Conditional continuation — the hump gradient that does not exist** (see the correction in
`DEFECT_REACH_decomposition_cases.md`, 2026-08-11). Only reachable if M4 returns reason 2:

| # | measurement | price (core-min) | basis |
|---|---|---|---|
| **M7** | Produce a hump beta gradient **at all**, and FD-verify it at 3 cells with A11's written-and-never-run `run_hump_fd.sh` | **20** (gradient free with the converged solve; 9 hump primals at 10.583 s each plus decompose/reconstruct) | §5d's CBFS protocol, 9 primals, scaled to the hump primal |
| **M8** | *Then* the second-decomposition re-run the reach document says is owed | **100** (a second converged solve) | = M4 |

**Total M7–M8: 120 core-min, conditional on M4.** Until M4 returns, the hump owes a
gradient, not a re-run.

### 5c. The gate case: CBFS field-inversion (beta) gradient, converged and FD-verified

The adjoint linear system depends on the objective, not the design variable, so the
converged CBFS solve carries over to the FIML design variable directly. B3's script
with `patchV` replaced by the per-cell beta field (`betaFIOmega`, 21,000 DVs — the
same `inputInfo` block as S1's hump script; the case's real nonuniform inlet is
thereby restored rather than overridden):

```
OBJ varianceU: 1.5279278906359758e-02
**Completed**! Total iterations: 667. PetscConvergedReason: 2. 231.69 s
GRAD n=21000 norm=1.4558046603e-05 min=-4.694367e-07 max=1.916019e-06
```

246 s wall, 16.4 core-min. **This is the first converged field-inversion gradient
on a closure-relevant case in this lab** — the object whose absence blocked Stage 1,
C2 and the duct line.

> **Correction, dated 2026-08-07 (S1 inversion coverage audit).** The parenthetical
> above — "the case's real nonuniform inlet is thereby restored rather than
> overridden" — is wrong. Switching the DV to beta stopped the *per-iteration*
> overwrite, but the on-disk `0/U` this case inherited had already been overwritten
> by the patchV pilot: Ux = 0.72 uniform on all 150 inlet faces, against the
> benchmark's own inlet profile (bulk 0.9149, 0.202→1.005), with the two files'
> Uz noise columns identical — the mechanism fingerprint. Every objective value in
> this document (1.5279278906359758e-02 included) was computed under that
> 0.72-uniform inlet. The gate is unaffected — FD-vs-adjoint agreement is a property
> of the objective as built — but the loss itself carries a 27% inlet bulk mismatch
> against `0/UData`, with the consequences measured in
> `S1_CBFS_INVERSION_RESULT.md` §4.

### 5d. FD verification: gate met, at 13–45x the required tightness

S1's protocol: fresh process per point, cold reset of the processor dirs, central
differences. Steps sized to the gradient scale — top |g| here is 1.9e-6 against an
objective of 1.53e-2, so h=0.05 puts the objective delta at ~1e-7 absolute, the
scale S1's own campaign demonstrated resolvable. Three cells from three distinct
mesh neighborhoods, spanning the top of the |g| distribution.

**Control first:** the unperturbed FD-protocol run reproduces the adjoint run's
objective to **exactly zero difference** (1.5279278906359758e-02, all 17 digits).

| cell | h | central FD | adjoint g[i] | rel err |
|---|---|---|---|---|
| 5491 (largest) | 0.05 | 1.914384790951e-06 | 1.916018813330e-06 | **0.085%** |
| 5491 | 0.1 | 1.907246786675e-06 | 1.916018813330e-06 | 0.460% |
| 6740 | 0.05 | 1.679642395377e-06 | 1.678653382471e-06 | **0.059%** |
| 12486 | 0.05 | 1.472401682783e-06 | 1.469472928907e-06 | **0.199%** |

Zero sign flips; every component under 0.2% at h=0.05 against the gate's bar of
"the same order as S1's 2.67%". The doubling of the error from h=0.05 to h=0.1 on
cell 5491 (0.085% to 0.46%, and the FD moving *away* from the adjoint value as the
step grows) is central-difference truncation behaving exactly as O(h²) predicts —
the agreement is step-limited, not noise-limited, which is the signature of a
correct derivative measured against a resolvable objective. 9 primals, 642 s wall,
42.8 core-min.

**The docket gate — "the hump or CBFS adjoint converges and the resulting gradient
is FD-verified on at least 3 components to the same order as S1's 2.67%" — is met,
on the CBFS branch, with all evidence on disk.**

> **Caution note, dated 2026-08-08 (added by the S1 reinversion agent; caveat only,
> no conclusion above is contested).** The §5d phrase "three cells from three
> distinct mesh neighborhoods" may rest on a serial-vs-DV indexing confusion: the
> beta DV vector is NOT in serial cell order, and cell centres looked up at DV
> indices label the wrong cells. On the S1 reinversion this exact error mislabeled
> all three FD cells; the true DV→serial permutation (concatenated
> `processor*/constant/polyMesh/cellProcAddressing`, verified to 5.1e-15 against a
> written beta field) placed them all in the separated shear layer. The FD
> *measurements* are index-consistent and unaffected — perturbation and gradient
> share the DV indexing — only spatial/neighborhood labels are at risk. If §5d's
> cells 5491/6740/12486 were located via serial centres at DV indices, their
> neighborhood claims need re-derivation through the permutation. Evidence path:
> `/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/cbfs_inv/dv_to_serial_perm.npy`
> and `S1_CBFS_WEIGHTED_LOSS_VARIANT.md` §0b.

## 6. The liaison memo, answered lead by lead

- **Lead 1.1** (deployed-source shift check): done first — the deployed
  `DALinearEqn.C` carries the same three `PCFactorSet*` lines as upstream main, and
  the offline control (section 1) reproduces the failure with those exact settings.
  Confirmed, and extended: the shift is not only present, it is *demonstrated
  insufficient* at a 6-decades-larger zero-pivot threshold (section 2).
- **Lead 1.2** (`jacMatReOrdering` sweep): already complete before the memo —
  PROOF §25.2 ran all five orderings on CBFS on 2026-08-02: two produce `-9`, three
  produce `-3` flat stagnation, none converges. Not retested, per the docket's own
  launch prompt.
- **Lead 1.3** (options unreachable; `PCFactorReorderForNonzeroDiagonal` as the
  one-line patch): half-corrected, half-refuted by measurement. The sub-PC *factor*
  options ARE reachable at runtime (section 2, PCView evidence) — the unreachable set
  is only what DAFoam explicitly overrides after `KSPSetUp` (type, ordering, levels,
  shift). And the proposed one-line patch would not have worked: the nzdiag reorder
  was tested offline and still returns `-9`, consistent with the diagonal having no
  zero entries to permute away (PROOF §25.3). The one-word patch that does work is
  `PCILU` → `PCLU` (section 3).
- **Lead 1.4** (`adjEqnSolMethod: fixedPoint`): refuted at zero compute for this
  item's gate. The deployed implementation's adjoint state set is `(U, p, phi,
  nuTilda)` — `DASimpleFoam.C` looks up `nuTilda` unconditionally — and its
  turbulence leg calls `calcLduResidualTurb`, which is overridden **only** in
  `DASpalartAllmarasFv3`; `DAkOmegaSST` inherits the base-class
  `FatalError "Child class not implemented!"`. The hump and CBFS FIML cases are
  kOmegaSST with beta on the omega-equation production term: there is no omega
  adjoint in that state set, so `dR/dbeta` can never be seeded through it. Same
  structural class as the frozen-turbulence route S1 already closed.
- **Lead 1.5** (`transonicPCOption` for M6): out of this item's gate (compressible
  family, different mechanism per PROOF §25.2's postscript). Left on the record as
  the right next lever for R5's family; nothing run.

## 7. Cost

| item | wall | ranks/cores | core-min |
|---|---|---|---|
| offline petsc4py ladder (5 runs + the nd-ordering timeout at its full 600 s) | 693 s | 4 | 46.2 |
| CBFS regression control (patched image, env unset) | 92 s | 4 | 6.1 |
| CBFS sub-LU, patchV (converged, 667 iters) | 243 s | 4 | 16.2 |
| hump sub-LU attempt (stopped at ~iter 900, memory) | 819 s | 4 | 54.6 |
| two aborted hump stagings (missing includes; #calc-as-root) | ~40 s | 4 | 2.7 |
| CBFS sub-LU, beta field (converged, 667 iters, the gate gradient) | 246 s | 4 | 16.4 |
| FD sweep, 9 fresh primals | 642 s | 4 | 42.8 |

**Total: 185.0 core-min against the 240 core-min budget.** Compile time (~2 min of
container CPU across three wmake targets) is additionally noted; the solver ledger
above bills every run at full 4-core occupancy for its whole wall clock, including
the 40 core-min the nd-ordering timeout burned — nothing is billed below what the
clock shows.

## 8. Evidence

`/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/`:
`pc_ladder.py`, `{control,nzdiag,zeropivot,diagfill,sublu}_rcm.log`, `sublu_nd.log`,
`run_cbfs_sublu.sh`, `run_cbfs_generic.sh`, `cbfs_{regress,sublu,beta}_computetotals.log`,
`run_hump_sublu.sh`, `hump_sublu_computetotals.log`, `hump_sublu_mem.log` (5 s
MemAvailable trace, low-water 1.62 GB), `runScript_hump_rich.py` (staged, unrun),
`cbfs_beta/` — `runScript.py` (the beta-field variant), `cbfs_beta_grad.npy`,
`fd_plan.json`, `fd_table.json`, `fd_beta_*.npy`, `fdlogs/` (10 logs), and
`run_cbfs_fd.sh` / `cbfs_fd_summary.txt`.

The one-hunk source diff is committed at
`demo-output/website/dafoam/subpclu_patch/DALinearEqn_subpclu.patch`; the built
image is `dafoam-subpclu:v1`, local to this box (`docker commit` of the build
container, which was stopped and removed at session end after the diff was
exported — the "sleep infinity" `dafoam/opt-packages` container another session
may have observed was that build container, this item's own scratch).
