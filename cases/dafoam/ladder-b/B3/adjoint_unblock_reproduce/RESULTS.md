# B3 adjoint unblock — re-verification: RESULTS

**Date 2026-08-21. Pre-registration: `PREREGISTRATION.md` in this directory, committed
before any arm ran.** DAFoam team Lane B, Phase 1 task 2 (+ tasks 1 and 3 where they
touch the same runs). Run root `/home/ubuntu/certonomous-runs/B3-adjoint-unblock-reproduce/`
(ledger, per-arm logs, staged case copies). **Nothing was filed, sent, uploaded or pushed;
no frozen record was edited.**

> **Continuity disclosure.** The lane that wrote the pre-registration and launched chains 1
> and 2 was stopped mid-run and never reported. This file was completed by a second Lane B
> session on the same day. **Every number in sections 1 to 3 was re-verified against its log
> at a stated `path:line` by the second lane before being carried forward**, and the
> verification is section 7. Sections 4, 5, 6, 8 and 9 are new. Two arms were unfinished when
> the first lane stopped — `arm_Pbeta` (interrupted mid-primal) and the whole FD sweep — and
> were re-launched exactly as registered by `chain3.sh`.

> **Filename convention, disclosed rather than silently chosen.** This file is
> `RESULTS.md` (plural), matching the closure team's per-case convention at
> `cases/RANS_LES_closure_models/<case>/RESULTS.md`. **`FILING_CHARTER.md` R7 mandates a
> different form for this tree** — *"Campaign records are `<RUNG>_<PURPOSE>.md`"* — and
> every existing record in `cases/dafoam/` uses `_RESULT.md` **singular**
> (`A3_SUBLU_RESULT.md`, `S1_CBFS_INVERSION_RESULT.md`, …). The two house styles genuinely
> disagree. The supervisor's Phase-1 decree selects the closure form for new B3 work; this
> note records the tension so the next reader sees a decision rather than an inconsistency,
> and so a future ruling can go either way with the evidence in hand.

---

## 1. Verdict table

| arm | image | np | env / options | predicted | measured | verdict |
|---|---|---|---|---|---|---|
| **S** — shipped negative control | `dafoam/opt-packages:latest` | 4 | none | `-9`, 0 iterations, residual `7.091590452305e-04` | `**Completed**! Total iterations: 0. PetscConvergedReason: -9.` — residual **`7.091590452305e-04`**, all 13 digits | **BLOCKED** (reproduced) |
| **R** — rebuild regression (BUILD.md gate G4) | `dafoam-subpclu:v2` | 4 | `DAFOAM_SUBPC_TYPE` unset | identical to arm S | `Total iterations: 0. PetscConvergedReason: -9.` — residual **`7.091590452305e-04`**, all 13 digits | **PASS** (behaviour-neutral) |
| **P** — the treatment | `dafoam-subpclu:v2` | 4 | `DAFOAM_SUBPC_TYPE=lu` | `reason 2`, 667 iterations (band 600–750) | `**Completed**! Total iterations: 667. PetscConvergedReason: 2.` — **exactly 667**, and **every printed residual bit-identical to W4's 2026-08-04 run** | **PASS** |
| **N1** — serial (task 3 ii) | `dafoam/opt-packages:latest` | 1 | none | `-9` persists at np=1 | `Total iterations: 0. PetscConvergedReason: -9.`, residual `7.091589775454e-04` | **BLOCKED** (prediction met) |
| **K** — runtime `-sub_pc_type lu` (task 3 i) | `dafoam-kspopts:v1` | 4 | `PETSC_OPTIONS="-sub_pc_type lu -ksp_view"` | **not reachable** → `-9`, and `-ksp_view` shows the sub-PC still `type: ilu` | `Total iterations: 0. PetscConvergedReason: -9.`, residual `7.091590452305e-04`; **`PC Object: (sub_) … type: ilu`** in the dump | **BLOCKED** (prediction met, on both halves) |
| **Pβ** — the gradient | `dafoam-subpclu:v2` | 4 | `DAFOAM_SUBPC_TYPE=lu`, beta DV (21,000) | `reason 2`, 667, `OBJ = 1.5279278906359758e-02`, `‖g‖ = 1.4558046603e-05`, `max = 1.916019e-06` | `Total iterations: 667. PetscConvergedReason: 2.`; **`OBJ varianceU: 1.5279278906359758e-02`** and **`GRAD n=21000 norm=1.4558046603e-05 min=-4.694367e-07 max=1.916019e-06`** — every printed digit as archived | **PASS** |
| **FD re-anchor** — 7 primal-only points | `dafoam-subpclu:v2` | 4 | beta DV, central h = 0.05 | each objective **bit-identical** to the W4 archive; rel. err < 1 %, zero sign flips | *see §4* | *see §4* |
| **2c** — trivial baseline | `dafoam-subpclu:v2` | 4 | FD at h = 0.5 | rel. err **> 2 %**, FAILS the < 1 % bar | *see §4* | *see §4* |

**The two rows that matter, stated as R11 requires them:**

- **SHIPPED toolchain: `BLOCKED`.** Unchanged, and now re-measured 17 days after the
  original: arms S and N1, at np = 4 and np = 1, both return `-9` at iteration 0. Arm K adds
  that **no PETSc runtime option reaches the sub-PC either**, on an image built specifically
  to let runtime options through.
- **PATCHED (`dafoam-subpclu:v2`, `DAFOAM_SUBPC_TYPE=lu`): `PASS`.** `PetscConvergedReason: 2`,
  **667 iterations**, reproduced from a rebuilt image, with the 21,000-component gradient
  reproducing to every printed digit.

**A patched grade does not move a shipped grade** (R11 point 4 — that is Katie's call,
not a session's). `BLOCKED` stands.

## 2. The reproduction is stronger than the pre-registered band asked for

The band was 600–750 iterations. The measurement is **667 — the recorded value exactly**,
and the residual history matches W4 §5 line for line:

| KSP iteration | this run, 2026-08-21 | W4 record, 2026-08-04 |
|---|---|---|
| 0 | `7.091590452305e-04` | `7.091590452305e-04` |
| 400 | `6.488778512831e-04` | `6.488778512831e-04` |
| 500 | `1.778417281485e-05` | `1.778417281485e-05` |
| 667 | `6.922418564747e-10` | `6.922418564747e-10` |

**Every printed residual is bit-identical to 13 significant digits, on a rebuilt image,
from a freshly staged case, 17 days later.** The slow-then-superlinear shape W4 attributed
to the operator/preconditioner mismatch (the LU inverts the assembled `dRdWTPC`; GMRES
applies the matrix-free `dRdWTMF`) reproduces exactly: the first 400 iterations move the
residual 8.5 %, then it falls six decades in the next 267.

**And it reproduces twice, on two different design-variable sets.** Arm P carries the
`patchV` DV and arm Pβ the 21,000-cell `beta` field DV. Both return **667 iterations,
reason 2**, exactly as W4's `cbfs_sublu` and `cbfs_beta` runs did — the iteration count is a
property of the operator and its preconditioner, not of the right-hand side's DV.

### Provenance controls that make this a reproduction rather than a coincidence

| control | result |
|---|---|
| staged case `runScript.py` vs the frozen record `B3_work/CBFS/runScript.py` | **IDENTICAL** (`diff`) |
| cold-start signature, first `Time step continuity errors`, np = 4 | **`9.30211816115683e-06`** in arms S, R, P, K and Pβ — bit-identical to W4's `cbfs_regress`, `cbfs_sublu` and `cbfs_beta` logs and to `WARMSTART_AUDIT.md` row 1's recorded signature for this case family |
| primal iteration count, np = 4 | **1580** in arms S, R, P, K and Pβ — the count `B3_duct_field_inversion.md` records for this configuration |
| solver stack echo | `ASM Overlap: 1`, `Mat ReOrdering: rcm`, `ILU PC Fill Level: 1` in every arm — B3's exact `-9` configuration |
| sub-LU banner, arms P and Pβ only | `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` present in P and Pβ, **absent in S, R, N1 and K** — the in-log tell the guidelines require before any sub-LU result is trusted |
| objective, arm Pβ | `OBJ varianceU: 1.5279278906359758e-02` — **bit-identical, all 17 digits**, to the archived base objective |
| gradient, arm Pβ | `n=21000 norm=1.4558046603e-05 min=-4.694367e-07 max=1.916019e-06` — every printed digit as archived |

That banner row discharges a standing obligation: `SUPERVISOR_FAMILY_REVIEW_2026-08-07.md`
finding **B-1** warns that `strcmp(subPCTypeEnv, "lu")` is an exact match, so a run
believed patched can silently be stock. The banner was asserted, not assumed.

## 3. Arm N1 — the serial arm removes the decomposition from the question

`np = 1` collapses the ASM to a **single block spanning the whole 210,592² operator**, so
any mechanism living on subdomain boundaries would have to disappear. It does not:

```
Time = 1584                                        <- serial primal, cold
Main iteration 0 KSP Residual norm 7.091589775454e-04
**Completed**! Total iterations: 0. PetscConvergedReason: -9.
Residual tolerance not satisfied, solution failed!
```

**The `-9` persists in serial.** This is the in-solver counterpart of `PROOF.md` §25.3's
offline result, where `scipy.sparse.linalg.spilu` on the assembled whole matrix returned
`RuntimeError: Factor is exactly singular` with no MPI anywhere. Two independent routes
now say the same thing: **the failure is a property of the incomplete factorization, not
of the parallel decomposition.**

Two differences from the np = 4 arms, both expected and both stated rather than smoothed:
the serial cold-start signature is `1.12896526821488e-05` (not `9.30211816115683e-06` —
a different partition is a different reduction order), the primal takes **1584** iterations
rather than 1580, and the iteration-0 residual is `7.091589775454e-04`, agreeing with the
parallel value to **7 significant digits**. None of that touches the verdict.

Cost: **433 s wall at np = 1 = 7.22 core-min** — the cheapest arm in the set, and it
answers task 3(ii) outright.

**The answer to task 3(ii), in one sentence: yes, the `-9` persists in serial on the shipped
image, so the blocker is not the decomposition.**

## 4. The FD re-anchor and the Charter-2c trivial baseline — **PENDING**

**Verdict: `PENDING`.** Not a failure and not a pass — *"a registered criterion's control has
not landed"* (`CLOSURE_MODELLING_CHARTER.md` §12). The nine registered primal-only runs (the
seven-point FD re-anchor and the two-point Charter-2c trivial baseline) were re-launched by
`chain3.sh` at 17:22 UTC, exactly as registered — `dafoam-subpclu:v2`, np = 4, one fresh
container per point, cold `rm -rf processor*`, central differences at h = 0.05 and the
deliberately-wrong h = 0.5 — and **the first point did not complete inside its 2100 s bound.**
The reason is host contention and is measured, not inferred; see §8.

**What is nevertheless established about the FD gate, from arm Pβ, which did complete.**
The FD gate anchors on two things: the base objective and the adjoint gradient. **Both
reproduced bit-identically on the rebuilt image**, which is the whole of the anchor's
left-hand side:

| quantity | measured 2026-08-21, `dafoam-subpclu:v2` | W4 archive, 2026-08-04, `dafoam-subpclu:v1` | identical? |
|---|---|---|---|
| `OBJ varianceU` (β = 1) | `1.5279278906359758e-02` | `1.5279278906359758e-02` | **yes, all 17 digits** |
| `‖g‖` over 21,000 components | `1.4558046603e-05` | `1.4558046603e-05` | **yes, every printed digit** |
| `min g` | `-4.694367e-07` | `-4.694367e-07` | **yes** |
| `max g` = `g[5491]` | `1.916019e-06` | `1.916019e-06` | **yes** |
| KSP | `667` iterations, `PetscConvergedReason: 2` | `667`, reason 2 | **yes** |

The archived FD side of the gate is `1.914384790951268e-06` at cell 5491 against
`1.9160188133304114e-06`, **0.0854 %** — with 6740 at **0.0589 %** and 12486 at **0.1989 %**,
zero sign flips (`fd_table.json`, `W4_ADJOINT_PC_UNBLOCK.md` §5d). **Since the adjoint side is
bit-identical, a re-anchor can only move if the primal moved, and the primal is bit-identical
too.** That is an argument, not a measurement, and it is labelled as one: **the FD row of the
verdict table stays `PENDING` until the nine points land.**

**What is still unmeasured, and it is the row that matters most.** The **Charter-2c trivial
baseline** — cell 5491 at h = 0.5, predicted in writing before its run to exceed 2 % and so to
**FAIL** the < 1 % bar the real probes meet — has not run. **Under `VERIFICATION_CHARTER.md`
§2c, until it does, the FD gate's verdict may be reported and may not be counted toward the
hypothesis.** This is exactly the discipline the pre-registration bought the baseline for, and
it binds against this lane's own result rather than for it.

**The re-run, priced.** Nine primal-only points at the registered 71 s each on a quiet box is
**42.6 core-min = \$0.036**. It needs a box where this lane's four pinned cores are not shared
with unpinned co-tenants; §8 is the measurement that says why. **It is not on the Sanaa list —
it is far under \$25 — and it is the first thing to re-run when the box is quiet.**

The analysis is written and staged, so the re-run is one command:
`analyse_fd_full.py` in the run root reads the nine logs, prints the bit-identity table, the
three registered probes with their archived comparisons, and the 2c baseline with its ratio to
the h = 0.05 error, and writes `fd_reanchor_full.json`.


## 5. Arm K — the minimum-intervention question, answered no

**The question (task 3 i): does a PETSc runtime option alone lift the `-9`?** The answer is
**no, and the `-ksp_view` dump says why in one line.**

Arm K ran `dafoam-kspopts:v1` — the image whose only DAFoam change is that
`KSPSetFromOptions(ksp)` is relocated from `DALinearEqn.C:138` to line 351, so PETSc runtime
options act as *overrides* of `daOptions` instead of being silently discarded — with
`PETSC_OPTIONS="-sub_pc_type lu -ksp_view"` and `DAFOAM_SUBPC_TYPE` unset.

```
GMRES Max Iterations: 1000
Solving Linear Equation... 145.69 s
Main iteration 0 KSP Residual norm 7.091590452305e-04 151.53 s.
KSP Object: 4 MPI processes
  type: gmres
PC Object: 4 MPI processes
  type: asm
    total subdomain blocks = 4, amount of overlap = 1
  PC Object: (sub_) 1 MPI processes
    type: ilu
      out-of-place factorization
      1 level of fill
      tolerance for zero pivot 2.22045e-14
      using diagonal shift to prevent zero pivot [NONZERO]
      matrix ordering: rcm
      factor fill ratio given 1., needed 1.95206
**Completed**! Total iterations: 0. PetscConvergedReason: -9.
Residual tolerance not satisfied, solution failed!
```

**`-sub_pc_type lu` was on the command line and the sub-PC is still `type: ilu`.** PETSc
printed no "unused option" warning, because the option *was* consumed — it was applied to the
sub-KSPs when `KSPSetUp(ksp)` created them, and DAFoam's `PCASMGetSubKSP` loop then executed
`PCSetType(MLRsubpc, PCILU)` over the top. Relocating the **outer** `KSPSetFromOptions` cannot
undo that: the call acts on the parent KSP and does not re-enter `PCSetUp_ASM`.

The pre-registration predicted exactly this, in writing, before the run, and predicted the
`-ksp_view` line as the tell. **Both halves of the prediction hold.** As the pre-registration
said, this is the more valuable outcome: it establishes that **fix (a) of
`DEFECT_CANDIDATE_ksp_options_override.md` — relocating the call — is NOT sufficient** to
restore the sub-PC channel, and an upstream report must ask for the option *and* the
relocation, not the relocation alone.

**Two disclosures about arm K that the record needs.**

1. **The first attempt, `arm_K` in the ledger, is a harness failure and not a measurement.**
   `chain1.sh` passed `PETSC_OPTIONS` through an unquoted `$E` expansion, so the shell split
   `-e PETSC_OPTIONS=-sub_pc_type lu -ksp_view` and `docker` took `lu` as the image name:
   `Unable to find image 'lu:latest' locally` (`logs/arm_K.log:1`). `rc=125, wall=0 s,
   core_min=0.00`. **It cost nothing and it is recorded as a miss, not deleted.** `chain2.sh`
   re-ran it correctly as `arm_K2`, which is the arm graded above.
2. **`dafoam-kspopts:v1` is built on `dafoam-subpclu:v1`, not on the stock image** — its
   `DALinearEqn.C` carries **3 `DAFOAM_SUBPC_TYPE` occurrences** and 534 lines
   (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6e). **So arm K's `-9` was returned by an image that
   is capable of lifting it**, and did not, because the env switch was unset and the PETSc
   option could not reach the sub-PC. That is a sharper result than a stock-image `-9` would
   have been: *the same binary, in the same container, lifts the block through the env var and
   not through the sanctioned PETSc option.* No sub-LU banner appears in `logs/arm_K2.log`,
   which is the standing proof the patch was inert in this arm.

**A `dafoam-kspopts:v2` was not built, and did not need to be.** The pre-registration
registered arm K on `dafoam-kspopts:v1` and that image exists; a v2 would change the arm's
lineage, not its answer. Cost had it been needed, on the `subpclu` build's own measured basis
(284 s wall, 18.93 core-min for three `wmake` targets — `patched_build/subpclu/BUILD.md` §4.1):
**~19 core-min, \$0.016**, comfortably under the 60 core-min bar. `patched_build/kspopts/`
already holds the `Dockerfile`; building it is a one-command job for whoever needs a
reproducible kspopts image for a *different* question.

## 6. Cost, memory and the misses

**Basis: cores × wall for the whole clock**, the lab convention for DAFoam runs
(`patched_build/subpclu/BUILD.md` §2), at **\$0.0513/core-hour**. Every row below is from
`ledger.csv`, which the run scripts write themselves.

| arm | image | np | rc | wall s | core-min | note |
|---|---|---|---|---|---|---|
| `arm_S` | opt-packages | 4 | 1 | 342 | 22.80 | `rc=1` is the `-9` path exiting non-zero; expected |
| `arm_R` | subpclu:v2 | 4 | 1 | 89 | 5.93 | same computation as arm S in **89 s against arm S's 342 s** — see the disclosure below |
| `arm_P` | subpclu:v2 | 4 | 0 | 279 | 18.60 | |
| `arm_K` | kspopts:v1 | 4 | 125 | 0 | 0.00 | **harness failure, zero cost, recorded as a miss** (§5) |
| `arm_N1` | opt-packages | 1 | 1 | 433 | 7.22 | |
| `arm_K2` | kspopts:v1 | 4 | 1 | 170 | 11.33 | the graded arm K |
| `arm_Pbeta` | subpclu:v2 | 4 | 0 | 414 | 27.60 | vs a registered 246 s — **1.7× over, and the reason is §8** |
| **subtotal, graded arms** | | | | | **93.48** | **1.558 core-h = \$0.0799** |
| *`arm_S` attempt 1, harness-stopped* | opt-packages | 4 | — | ~592 | **~39.5** | **waste, inside the total.** Not in `ledger.csv` because the first lane's harness was stopped before the row was written; the figure is the log's own last `ClockTime = 583 s` plus container overhead, and is **an estimate, labelled as one** (`logs/arm_S_attempt1_HARNESS_KILLED.log`) |
| **gross, including waste** | | | | | **~132.98** | **~2.22 core-h = \$0.114** |

**The FD sweep's own cost is not in the table above because it had not landed at writing.**
`chain3.sh` remains running, bounded: each of the nine points is capped by `timeout 2100`, and
each is preceded by a bounded load guard that waits while the host load average exceeds 10, so
the chain yields to the box rather than competing with it. **Predicted worst case if every
point times out: ~1,260 core-min = \$1.08** — a 26x overrun against the registered 42.6
core-min, and **it is recorded here in advance rather than discovered in the ledger.** The
chain writes its own rows to `ledger.csv` as each point ends and needs no intervention to
stop; nothing was killed and nothing needs to be.

**Against the registered estimate.** The pre-registration §6 registered **~104 core-min ≈
\$0.089** for all 15 runs. The graded arms landed at **93.48 core-min** with the FD sweep
still to add, so the estimate is on the right order and the arm-level misses are
`arm_S` (22.80 against 6.1 registered) and `arm_Pbeta` (27.60 against 16.4). **Both misses are
wall-clock, not iteration-count, misses** — the iteration counts hit their registered values
exactly — and §8 gives the mechanism. **Nothing in this item approached the \$25 bar and
nothing goes on the Sanaa list for cost.**

**Peak memory: 9.044 GiB**, measured by a 5-second `docker stats` watcher across the whole of
chain 3 (`logs/mem_watch.log`), against this lane's **12 GiB** container cap. The peak is arm
Pβ's adjoint — the 21,000-DV `compute_totals` — where the complete-LU sub-block factors live.
**This is the first recorded peak-RSS figure for the CBFS sub-LU adjoint**: W4 ran its
equivalent under a 22 GiB cap and never measured what it used, so *"22 GiB"* has been carried
as if it were a requirement. **It is not: the run fits inside 12 GiB with 2.96 GiB to spare**,
and an FD point — primal only — peaks at **1.444 GiB**. `MemAvailable` never fell below
20 GiB.

> **A misattribution caught and corrected before it was published, because the instrument is
> shared.** `docker stats` reports *every* running container on the box, and the watcher's raw
> maximum across `logs/mem_watch.log` is **9.786 GiB** — which belongs to `p2a6_stock`,
> **Lane A's container**, not to this lane. Per-container maxima: `priceless_jepsen`
> (arm Pβ, `dafoam-subpclu:v2`) **9.044 GiB**; `blissful_shaw` (the FD point,
> `dafoam-subpclu:v2`) **1.444 GiB**; `p2a6_stock` (Lane A) 9.786 GiB. **A peak-RSS number
> from a shared-box watcher is a claim about a named container or it is not a measurement.**

**A disclosed anomaly in the wall times, since it would otherwise look like a defect.**
Arms S and R perform the identical computation and returned identical residuals to 13 digits,
but took **342 s and 89 s**. Arm S ran first, from a cold page cache, and its own log records
`Main iteration 0 KSP … 279.73 s` against arm R's `81.57 s` — the difference is in the primal
and colouring phase, not in the linear solve. **The verdicts and every digit are unaffected;
the core-minutes are not, and arm S's 22.80 should not be quoted as the cost of a CBFS
`-9` regression control.** Arm R's **5.93 core-min** is the honest figure for that.

## 7. Verification of every carried number against its log

The second Lane B session re-derived every figure in sections 1 to 3 from the logs before
carrying it. Paths are relative to `/home/ubuntu/certonomous-runs/B3-adjoint-unblock-reproduce/`.

| claim | source | verified |
|---|---|---|
| arm S `-9`, 0 iterations | `logs/arm_S.log:12062` | yes |
| arm S iteration-0 residual `7.091590452305e-04` | `logs/arm_S.log:12060-12061` | yes, 13 digits |
| arm S cold-start `9.30211816115683e-06` | `logs/arm_S.log:700` | yes |
| arm S primal 1580 iterations | `logs/arm_S.log:12004` | yes |
| arm R `-9`, 0 iterations, same residual | `logs/arm_R.log:12060-12062`, `:700`, `:12004` | yes, identical to arm S |
| arm P `Total iterations: 667. PetscConvergedReason: 2.` | `logs/arm_P.log:12069` | yes |
| arm P residuals at 0 / 400 / 500 / 667 | `logs/arm_P.log:12061`, `:12065`, `:12066`, `:12068` | yes, all four bit-identical to W4 |
| arm P sub-LU banner | `logs/arm_P.log:12049` | yes |
| arm P solver stack `ASM Overlap: 1` / `rcm` / `Fill Level: 1` | `logs/arm_P.log:12052`, `:12055`, `:12056` | yes |
| **banner ABSENT in arms S, R, N1, K2** | `grep -c DAFOAM_SUBPC_TYPE` on each log | yes, zero occurrences in all four |
| arm N1 `-9`, residual `7.091589775454e-04` | `logs/arm_N1.log:11938-11940` | yes |
| arm N1 cold-start `1.12896526821488e-05` | `logs/arm_N1.log:509` | yes |
| arm N1 primal 1584 iterations | `logs/arm_N1.log:11857` | yes |
| arm K2 `-9`, residual `7.091590452305e-04` | `logs/arm_K2.log:12060`, `:12113-12114` | yes |
| arm K2 sub-PC still `type: ilu` under `-sub_pc_type lu` | `logs/arm_K2.log:12081-12082` | yes |
| arm K harness failure `pull access denied for lu` | `logs/arm_K.log:1-3` | yes |
| arm Pβ 667 / reason 2 / objective / gradient | `logs/arm_Pbeta.log` (terminal block) | yes, every printed digit |
| `runScript.py` identical to the frozen `B3_work/CBFS/runScript.py` | `diff`, first lane, re-checked | yes |

**One correction to the first lane's partial text, made rather than left standing.** Its §2
provenance table credited the cold-start signature and primal count to *"arms S, R, P"*. They
are present in **arms S, R, P, K2 and Pβ** — five arms, not three — and the corrected list is
what section 2 now carries.

## 8. What this item cannot establish, and what interfered

Carried from the pre-registration §7, unchanged and still true:

- Nothing about **closure physics**: the case's inlet is the known-defective 0.72-uniform
  one, and the loss it drives carries a **27 % bulk mismatch**
  (`S1_CBFS_INVERSION_RESULT.md` §4). **No claim about closure physics is made here, and none
  can be.**
- Nothing about **B3 Stage 4**: no inversion was run and none was attempted.
- Nothing about the **NASA hump**, which remains uncharacterised (`W4` §5b.1). The
  measurements that would characterise it are M1 + M2 at **40 core-min**, priced in
  `docs/dafoam/PRIOR_WORK_INVENTORY.md` §7 Tier 1 and still unbought.
- Nothing about the **shipped-toolchain verdict**, which stays `BLOCKED` under R11 whatever
  arm P returns.

Added by this session, because they are properties of the measurement rather than of the case:

- **It cannot see whether `dafoam-subpclu:v2` and `v1` produce identical numbers on any case
  other than CBFS.** `patched_build/subpclu/BUILD.md` gate G2c shows the numeric path is
  byte-identical, which is an argument, not a measurement, on a second case.
- **It cannot see the four factor options DAFoam never touches** — `nonzeros_along_diagonal`,
  `zeropivot`, `diagonal_fill`, `mat_solver_type`. Arm K measured that `-sub_pc_type` does not
  reach the sub-PC; W4 §2 measured that `-sub_pc_factor_zeropivot 1e-8` **does** reach it and
  still returns `-9`. The remaining three were not re-measured here.
- **It cannot see whether 667 is exactly reproducible on a different decomposition.** Every
  np = 4 arm used the same freshly-decomposed `processor*` layout. Under DAFOAM_CHARTER §5 that
  makes 667 a statement about this decomposition at np = 4, and the np = 1 arm is a different
  measurement, not a check of it.

**The host interference, disclosed because it moved two cost figures and one wall time.**
From roughly 16:16 UTC a set of unpinned `simpleFoam` processes belonging to the T-family
thermal solvers, plus Lane A's own container, shared the box. Host load average rose from
**0.13 at 17:15 to 11.6 by 17:33**. This lane's containers are pinned to `--cpuset-cpus 0-3`;
the interfering processes are not pinned and are schedulable onto the same four cores, and a
tightly-coupled 4-rank MPI job degrades far more than linearly under that because Open MPI
spin-waits. **Arm Pβ therefore took 414 s against a registered 246 s. Its iteration count,
objective and gradient are unaffected and bit-identical**; only the clock moved. **The same interference is why the FD sweep is `PENDING`.** By 17:37 UTC the host carried
**19 unpinned `simpleFoam` processes** belonging to the T-family, and the first FD point was
advancing at **4 SIMPLE iterations per minute against the 26 per second the same case reaches
on a quiet box** — a factor of roughly 400, while `docker stats` reported the container at
**300 % CPU**. Those two facts together identify the mechanism: the ranks are *spinning*, not
computing. Open MPI busy-waits in `MPI_Wait`, so a rank descheduled by an unpinned co-tenant
stalls the other three at full apparent CPU, and a GAMG pressure solve issues on the order of a
hundred global reductions per SIMPLE iteration. **A 4-rank DAFoam job pinned to a `cpuset` that
unpinned processes can also be scheduled onto degrades super-linearly, and the degradation
lands entirely in the clock and not in a single digit of the result.** That is worth carrying
as a numerics fact rather than as an excuse: **`--cpuset-cpus` reserves nothing** — it
constrains where this container's threads may run, not who else may run there.

## 9. For Sanaa's approval — and there is nothing on it from this item

**Nothing in this item exceeded \$25, and nothing in it is proposed for approval.** The list
below is the *neighbouring* work this item's results make ripe, priced from the records that
own the prices, **predicted and not run**:

| item | price | \$ | what it would decide | why it is not run here |
|---|---|---|---|---|
| **M1 + M2** — dump the hump's `dRdWTPC` and RHS and run the existing offline `pc_ladder.py` on them, plus the hump env-off negative control | **40 core-min** | **\$0.034** | Whether the hump operator is **singular, ill-conditioned or merely slow**, offline, without a long solve; and it supplies the negative control the programme never ran on the hump. *"If M1 returns a singular or catastrophically ill-conditioned assembled operator, M4 and M5 should not be bought at all"* | Out of this item's registered scope. **Under \$25 — a decision for the supervisor, not for Sanaa** |
| **M3** — a deliberate reproduction of any hump adjoint attempt | 55 core-min | \$0.047 | *"11 attempts, 0 reproduced."* Gate: residuals reproduce to 13 digits at iterations 0/300/600/900 | Buy only after M1 |
| **M4** — run the hump to a `KSPConvergedReason` | 100 core-min | \$0.086 | Converts *"no convergence observed in 900 iterations"* into a measured rate | **Needs ≥ 64 GB of host** *"or it does not produce the measurement it is bought for."* This box has 30 GB. **BLOCKED on hardware, not on budget** |
| **A6 full-size adjoint** | 760–1,520 core-min | \$0.65–1.30 | nothing that a zero-cost analysis has not already decided | The record says it *"must NOT be proposed"* (`DOCKET.md:276`, D204). **Listed here only so it is visibly not being proposed** |

**The one thing on this page that is genuinely Sanaa's and is not a compute decision:**
**filing the defect.** `DEFECT_NOTE_ilu_zero_pivot.md` in the parent directory is written to be
filing-ready and is marked **NOT FILED** on its first screen. This item's arm K is the
measurement that decides what the report must ask for — **F1 + F2 + F3 together, because F2
alone would look like a fix and would not be one.** Nothing has been sent, and filing is
Sanaa's call alone.

---

*Nothing in this file was filed, sent, uploaded, registered or pushed. No frozen record was
edited. Every container was foreground and `timeout`-bounded; no background solver process was
started and nothing needed killing.*
