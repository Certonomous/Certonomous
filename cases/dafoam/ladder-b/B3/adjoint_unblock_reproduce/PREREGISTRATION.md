# B3 adjoint unblock — re-verification: PRE-REGISTRATION

**Written 2026-08-21, ~16:1x UTC, BEFORE any solver run of this item.** Phase 1 task 2,
DAFoam team Lane B. Run root: `/home/ubuntu/certonomous-runs/B3-adjoint-unblock-reproduce/`
(outside the repository, per lab convention). Cap: **4 cores** (`--cpuset-cpus 0-3`;
Lane A holds 4–7). Every container is foreground and `timeout`-bounded; **no background
process is started and nothing needs killing.** `uptime` is checked before each launch and
the launch waits in a bounded loop if load > 10.

**Nothing is filed, sent, uploaded or pushed. No frozen record is edited.**

At this writing the only numbers that exist are the ones the frozen records already
published and the build gates of `patched_build/subpclu/BUILD.md`. **No arm of this item
has run.**

---

## 1. What this item exists to do, and what it does not

The sub-LU unblock has been **measured once**, on 2026-08-04, and adversarially verified
once (`W4_ADJOINT_PC_UNBLOCK.md`, `VERIFICATION_cbfs_unblock_supervisor_sweep.md`). What
does not exist is a **deliberate reproduction from a rebuilt image**: `dafoam-subpclu:v1`
came out of a hand-run `docker commit` in a session whose scratch tree is gone. The
warm-start audit's row 4 makes the general point in the neighbouring case —
*"'single run; no rerun existed to contaminate' is the same fact as 'never reproduced'"*.

**In scope:** does the `-9` still appear on the shipped image; does the reproducible
rebuild `dafoam-subpclu:v2` reproduce `reason 2 / 667 iterations`; does the FD gate
re-anchor; is there a cheaper intervention that also lifts the `-9`.

**Out of scope, stated so it cannot drift in:** B3 **Stage 4 (the field inversion) is NOT
attempted here.** No optimisation, no beta trajectory, no gate on a closure result. This
item measures one primal + one adjoint per arm and a finite-difference table.

## 2. Provenance of the case, established before the runs

Every arm is a **fresh staged copy** (guidelines §8) of
`certonomous-runs/W4-adjoint-pc-unblock/cbfs_regress/`, with `processor*` removed.
`diff` verified this session: that directory's `runScript.py` is **IDENTICAL** to the
frozen record `cases/dafoam/ladder-b/B3_work/CBFS/runScript.py` — B3's exact `-9`
configuration (`patchV` DV, `varianceU` objective, `jacMatReOrdering: rcm`,
`pcFillLevel: 1`, `primalMinResTol: 1e-6`). `system/controlDict` carries
`startFrom startTime; startTime 0;`, so **every arm re-solves the primal cold from `0/`**.

**Disclosure carried forward, not re-litigated:** this case's `0/U` is the
patchV-pilot-overwritten inlet — `Ux = 0.72` uniform on all 150 faces against the
benchmark's 0.202→1.005 profile, a **27 % bulk mismatch**
(`S1_CBFS_INVERSION_RESULT.md` §4). That defect is *what makes this a reproduction*: the
target numbers were produced under it. **No claim about closure physics is made here**,
and none can be.

## 3. Arms, each with its prediction fixed now

`np = 4` throughout **except arm N1**. That is what W4 ran: *"243 s wall, 4 ranks,
16.2 core-min"* (§5), and the regression control *"92 s wall, rc=1"* at 4 ranks (§4).
A serial arm **is** affordable and is registered as arm N1 below — it answers task 3(ii)
rather than being a cheaper substitute, so it runs in addition, not instead.

| arm | image | np | env / options | prediction, fixed now |
|---|---|---|---|---|
| **S** — shipped negative control | `dafoam/opt-packages:latest` | 4 | none | `Total iterations: 0. PetscConvergedReason: -9.`, iteration-0 residual **`7.091590452305e-04`** to all 13 digits. Wall ~92 s |
| **R** — rebuild regression (BUILD.md gate G4) | `dafoam-subpclu:v2` | 4 | `DAFOAM_SUBPC_TYPE` **unset** | identical to arm S in reason, iteration count and all 13 residual digits. **A difference here means the rebuild is not behaviour-neutral and the whole item stops.** |
| **P** — the treatment | `dafoam-subpclu:v2` | 4 | `DAFOAM_SUBPC_TYPE=lu` | `PetscConvergedReason: 2`; iterations **667**, registered band **600–750**; the banner `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` present in-log; iteration-0 residual `7.091590452305e-04`; wall ~243 s |
| **Pβ** — the gradient the FD gate needs | `dafoam-subpclu:v2` | 4 | `DAFOAM_SUBPC_TYPE=lu`, beta DV (21,000) | `reason 2`, **667** iterations (same band); `OBJ varianceU` = **`1.5279278906359758e-02`**; gradient `‖g‖` = **`1.4558046603e-05`**, `max` = **`1.916019e-06`** |
| **K** — the minimum intervention (task 3 i) | `dafoam-kspopts:v1` | 4 | `DAFOAM_SUBPC_TYPE` **unset**, `PETSC_OPTIONS="-sub_pc_type lu -ksp_view"` | **`-9`, iteration 0 — the option is predicted NOT to reach the sub-PC even on this image.** Reasoning in §4 |
| **N1** — serial (task 3 ii) | `dafoam/opt-packages:latest` | 1 | none | **`-9` persists at np=1.** Reasoning in §4 |
| **2c** — Charter-2c trivial baseline | `dafoam-subpclu:v2` | 4 | beta DV, FD at a **deliberately wrong step** | rel. error **> 2 %**, i.e. **fails** the < 1 % band the real probes meet |

### Why the band on arm P is 600–750 and not "exactly 667"

667 is a Krylov iteration count on a mismatched operator/preconditioner pair
(`W4` §5a: the LU inverts the assembled `dRdWTPC` while GMRES applies the matrix-free
`dRdWTMF`). It is reproducible in principle — same matrix, same seed-free algorithm — but
it is sensitive to MPI reduction order and to the ASM block boundaries, which follow the
decomposition. The staged copy carries `processor*` freshly decomposed rather than W4's
own, so a few iterations of drift are admissible and a *large* drift is the finding.
**±10 % is the band; an exact 667 is reported as the stronger result if it lands.**

### The FD re-anchor, and the bar

W4 §5d's protocol, unchanged: fresh container per point, cold `rm -rf processor*`,
**central differences, h = 0.05**, three cells from the top of the |g| distribution.
The three archived probes and their bars:

| DV index | archived adjoint `g[i]` | archived FD | archived rel. err | bar, fixed now |
|---|---|---|---|---|
| 5491 | `1.9160188133304114e-06` | `1.914384790951268e-06` | **0.0854 %** | **< 1 %**, zero sign flips |
| 6740 | `1.678653382470567e-06` | `1.6796423953774342e-06` | **0.0589 %** | **< 1 %**, zero sign flips |
| 12486 | `1.4694729289074443e-06` | `1.4724016827831476e-06` | **0.1989 %** | **< 1 %**, zero sign flips |

**Additionally, each of the seven archived FD objective values must reproduce.** The
base is `1.5279278906359758e-02`; the six perturbed values are in
`W4-adjoint-pc-unblock/cbfs_fd_summary.txt`. **Bit-identity is the prediction**, since the
FD points are primal-only `run_model` calls and the sub-PC patch touches only
`createMLRKSP`. A non-bit-identical objective would mean the rebuild changed the primal,
which nothing in the patch can do — so that outcome would be the headline, not a nuisance.

### The Charter-2c trivial baseline, and why this one is not a straw man

`VERIFICATION_CHARTER.md` §2c: *"A gate row whose verdict is counted as evidence about a
hypothesis is DISCRIMINATING or it is not evidence."* The FD gate's registered trivial
baseline here is **the same probe with a step chosen to be wrong**: cell 5491 at
**h = 0.5**, ten times the registered step. Central-difference truncation is O(h²), so a
10× step predicts ~100× the 0.0854 % error before nonlinearity, i.e. **> 2 %** and a
**clear FAIL of the < 1 % bar**. If the wrong step *passes*, the FD gate is not measuring
what it claims and the arm-P FD verdict is withdrawn.

This is a real risk and not a formality: `S1_SENSITIVITY_VS_ERROR.md` §3 already found a
*different* B3-family gate (G2) failing exactly this test — scored on the baseline
gradient alone, with no inversion in it, it returns 35.38 %.

## 4. The two reasoned predictions that could go either way

**Arm K — why `-sub_pc_type lu` is predicted NOT to reach the sub-PC.** Read from the
stock source this session (`DALinearEqn.C`, `createMLRKSP`): `KSPSetUp(ksp)` runs at
line ~229 — this is where `PCSetUp_ASM` creates the sub-KSPs and PETSc applies
`sub_`-prefixed options to them. Only *then* does DAFoam call `PCASMGetSubKSP` and loop
over the blocks, executing `PCSetType(MLRsubpc, PCILU)` at **line 286**, plus
`PCFactorSetShiftType`, `PCFactorSetShiftAmount` and `PCFactorSetLevels`. The `kspopts`
patch relocates the **outer** `KSPSetFromOptions(ksp)` from line 138 to ~line 343 — still
*before* the block loop's overrides in program order? No: the block loop is at 232–330 and
the relocated call lands at 345, i.e. **after** the loop. But it acts on the **outer** KSP,
and the sub-KSPs were already created and configured at line 229; re-calling
`KSPSetFromOptions` on the parent does not re-enter `PCSetUp_ASM`. **Prediction: `-9`
persists, `-ksp_view` shows the sub-PC still `type: ilu`.**

**If that prediction holds it is the more valuable outcome**, because it says fix (a) of
`DEFECT_CANDIDATE_ksp_options_override.md` — relocating the call — is **not sufficient**
to restore the sub-PC channel, and the upstream recommendation must be fix (a) *plus* a
sub-PC option or an env switch. **If it is refuted and the `-9` lifts, that is bigger
still**: the blocker is reachable with no solver-logic change at all, and the recompile
this lab performed was never necessary. Either way the record moves.

Note the record already **declined** this arm once, on grounds specific to a different
case: `A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md:29` — *"Not new — reachable already
through the lab's own `DAFOAM_SUBPC_TYPE=lu` patch, and tested at rung 2 where it proved
memory-infeasible."* That is about **ONERA M6**, at a mesh where the LU factors did not
fit. **It has never been run on CBFS, and the reachability question itself has never been
measured on any case.**

**Arm N1 — why serial is predicted to keep the `-9`.** At np = 1 the ASM has a single
block covering the whole 210,592² operator, so a decomposition-boundary mechanism would
have to vanish. But `PROOF.md` §25.3 factored the **assembled whole matrix** offline with
`scipy.sparse.linalg.spilu` and got `RuntimeError: Factor is exactly singular` at every
drop tolerance swept, with no MPI anywhere. **Prediction: `-9` at np = 1, i.e. the failure
is a property of the incomplete factorization, not of the decomposition.** A serial
*success* would contradict the offline result and would be the headline.

## 5. Verdict vocabulary, fixed now

`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`
(`CLOSURE_MODELLING_CHARTER.md` §12, the only place all six are defined).
**Shipped and patched are always two rows** (R11). A stop at a cap is recorded
**budget-capped, not converged** (charter §4).

## 6. Cost, registered before the runs

Basis: W4's own measured walls, billed at cores × wall (lab convention).

| arm | runs | est. wall | est. core-min |
|---|---|---|---|
| S | 1 | 92 s | 6.1 |
| R | 1 | 92 s | 6.1 |
| P | 1 | 243 s | 16.2 |
| Pβ | 1 | 246 s | 16.4 |
| K | 1 | ~150 s | 10.0 |
| N1 | 1 | ~400 s (1 core) | 6.7 |
| FD re-anchor | 7 | 7 × 71 s | 33.1 |
| 2c trivial baseline | 2 | 2 × 71 s | 9.5 |
| **total** | **15** | **~34 min** | **~104** |

**~104 core-min = 1.73 core-h × \$0.0513 = \$0.089.** Registered comparison: W4's own
ledger for the original work was **185.0 core-min ≈ \$0.16**. Both are far below the
\$25 bar; nothing in this item goes on the Sanaa list. Adjoint iteration caps are the
case's own (`gmresMaxIters` from `daOptions`); no arm is unbounded.

## 7. What this item cannot establish

- Nothing about **closure physics**: the case's inlet is the known-defective 0.72-uniform
  one, and the loss it drives carries a 27 % bulk mismatch.
- Nothing about **B3 Stage 4**: no inversion is run.
- Nothing about the **NASA hump**, which remains uncharacterised (`W4` §5b.1).
- Nothing about the **shipped-toolchain verdict**, which stays `BLOCKED` under R11
  whatever arm P returns — a patched grade replaces a shipped grade only if the fix ships
  upstream or Katie adopts a forked toolchain, and that is Katie's call.

*Nothing below this line existed when this file was committed. The arms launch only after it lands.*
