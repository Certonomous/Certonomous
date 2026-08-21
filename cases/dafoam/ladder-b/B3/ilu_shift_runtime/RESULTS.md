# B3 — does ILU-with-shift, set at runtime, lift the `-9`? RESULTS

**Written 2026-08-21 ~19:0x UTC, DAFoam team Lane B, scoring `chain4.sh` against
`PREREGISTRATION.md` in this directory.** All five arms completed; the chain ran detached and
finished at **18:46:44 UTC** while this lane was down on a session limit, so it is scored here
from its own ledger and logs and from nothing else.

Run root `/home/ubuntu/certonomous-runs/B3-ilu-shift-runtime/`. Image `dafoam-kspopts:v1`
(`d9d2aed02e36`), np = 4, `--cpuset-cpus 0-3`, `--memory=12g`, `DAFOAM_SUBPC_TYPE` **unset**
throughout, task `compute_totals`, `-ksp_view` on every arm.

**Nothing here is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

---

## 1. Headline

**No runtime PETSc option lifts the `-9`, and the reason is not that the shift was too small —
it is that the shift never became the deployed shift.** All five arms return
`**Completed**! Total iterations: 0. PetscConvergedReason: -9.` with iteration-0 residual
`7.091590452305e-04` to all 13 digits, and — the load-bearing measurement — **every arm's
`-ksp_view` dump is byte-identical to the control's**, timings excepted.

The sharpest row proves it. Arm **L-2** requested `-sub_pc_factor_levels 2`; its own dump reads
**`1 level of fill`** (`logs/arm_L2.log:12084`) and DAFoam's own echo reads
**`ILU PC Fill Level: 1`** (`:12055`). The requested value and the deployed value differ
visibly, and the deployed one is DAFoam's. **The factor options are overwritten by the
`PCASMGetSubKSP` loop exactly as `-sub_pc_type` is** — same mechanism, same ordering, same
outcome.

**Correction to a reading that was in circulation before this scoring.** The line
`using diagonal shift to prevent zero pivot [NONZERO]` appears in these logs and was read as
evidence that the shift options reached the factorisation. **It is not evidence, and the
pre-registration said so before the runs.** That line is present in **arm C, the control, which
set no shift option at all** (`logs/arm_C.log:12086`). It is DAFoam's own
`PCFactorSetShiftType(MLRsubpc, MAT_SHIFT_NONZERO)` printing, and §3's arm S-T row registered it
in advance as *"non-discriminating on the dump by construction … flagged here as the weak row
rather than counted as evidence."* **The prereg called this trap and the trap was walked into
anyway; recording that is the point of writing predictions down.**

## 2. Per-arm table

Every cite is `logs/<arm>.log:<line>` under the run root above. The dump line numbers are
**identical in all five logs**, which is itself the finding.

| arm | `PETSC_OPTIONS` (all `+ -ksp_view`) | rc | iterations | reason | iter-0 residual | wall s | core-min | verdict |
|---|---|---|---|---|---|---|---|---|
| **C** — control | `-ksp_view` only | 1 | **0** `:12114` | **-9** `:12114` | `7.091590452305e-04` `:12113` | **1884** | **125.60** | **BLOCKED** (reproduced) |
| **S-T** | `-sub_pc_factor_shift_type nonzero` | 1 | **0** `:12114` | **-9** `:12114` | `7.091590452305e-04` `:12113` | 102 | 6.80 | **BLOCKED** |
| **S-A10** | `+ -sub_pc_factor_shift_amount 1e-10` | 1 | **0** `:12114` | **-9** `:12114` | `7.091590452305e-04` `:12113` | 99 | 6.60 | **BLOCKED** |
| **S-A8** | `+ -sub_pc_factor_shift_amount 1e-8` | 1 | **0** `:12114` | **-9** `:12114` | `7.091590452305e-04` `:12113` | 99 | 6.60 | **BLOCKED** |
| **L-2** | `-sub_pc_factor_levels 2` | 1 | **0** `:12114` | **-9** `:12114` | `7.091590452305e-04` `:12113` | 104 | 6.93 | **BLOCKED** |
| *`-sub_pc_factor_levels 1`* | *declined, Charter §2c* | — | — | — | — | — | *0* | **NOT RUN**, by decision |

`rc=1` is the `-9` path exiting non-zero and is expected on every arm; it is not a harness
failure (contrast arm K's `rc=125` in `../adjoint_unblock_reproduce/RESULTS.md` §5).

### 2b. The deployed factor, read from each arm's own dump

Identical line for line in all five logs:

| dump line | value, all five arms | line |
|---|---|---|
| sub-PC type | **`type: ilu`** — never `lu` | `:12082` |
| fill | **`1 level of fill`** — **not 2, even in arm L-2** | `:12084` |
| zero-pivot tolerance | `2.22045e-14` | `:12085` |
| shift | `using diagonal shift to prevent zero pivot [NONZERO]` — **also in the control** | `:12086` |
| ordering | `matrix ordering: rcm` | `:12087` |
| fill ratio | `given 1., needed 1.95206` | `:12088` |
| factored matrix | `rows=55159, cols=55159` `:12092`; `total: nonzeros=6963844` `:12094` | `:12092-12094` |
| outer operator | `type: shell` `:12105`, `210592 x 210592`; pmat `mpiaij`, `total: nonzeros=13710468` `:12110` | `:12105-12110` |

`diff` of the whole `-ksp_view` region (lines 12040–12115) between arm C and each of S-T,
S-A10, S-A8, L-2 returns **only the two wall-clock timestamps** and nothing else. PETSc emitted
**no** unused-option warning on any arm, which is consistent: the options were consumed at
`KSPSetUp` and then overwritten, not ignored.

### 2c. Fidelity — every arm is B3's exact configuration

| signature | value, all five arms | line |
|---|---|---|
| cold-start continuity error | `9.30211816115683e-06` | `:700` |
| primal iterations | `Time = 1580` | `:12004` |
| solver stack echo | `ASM Overlap: 1`, `Mat ReOrdering: rcm`, `ILU PC Fill Level: 1` | `:12049-12055` |
| **sub-LU banner** | **ABSENT — `grep -c DAFOAM_SUBPC_TYPE` = 0 on all five logs** | — |

The banner check is the disclosure the pre-registration §4 required: `kspopts:v1` is built on
`subpclu:v1` and **is capable of lifting the `-9`** through `DAFOAM_SUBPC_TYPE=lu`. It is unset,
and each arm asserts the banner's absence in its own log. No arm is void.

## 3. Prediction vs measured — five for five

| arm | predicted: does it reach the factor? | measured | predicted reason | measured | hit? |
|---|---|---|---|---|---|
| **C** | n/a; `-9`, residual to 13 digits, dump reads `type: ilu` / `1 level of fill` / `rcm` / `[NONZERO]` / `2.22045e-14` | **all five dump strings as predicted**, residual to 13 digits | `-9` | `-9` | **HIT** |
| **S-T** | **NO — overwritten**; registered in advance as **non-discriminating on the dump** | overwritten; dump non-discriminating exactly as registered | `-9` | `-9` | **HIT** (reason only, as registered) |
| **S-A10** | **NO — overwritten** (`PCFactorSetShiftAmount(…, PETSC_DECIDE)`) | dump identical to control | `-9` | `-9` | **HIT** |
| **S-A8** | **NO — overwritten** | dump identical to control | `-9` | `-9` | **HIT** |
| **L-2** | **NO — overwritten**; *"the dump is predicted to read `1 level of fill`, not 2 … the sharpest dump tell in the set"* | **`1 level of fill`** `:12084`, and DAFoam's echo `ILU PC Fill Level: 1` `:12055` | `-9` | `-9` | **HIT — and this is the row that carries the class** |

**Five predictions registered, five hit, zero missed.** The §2 mechanism argument — *"PETSc
applied the `sub_`-prefixed options earlier, at `KSPSetUp`; these calls run after, and last
write wins"* — is confirmed on the one row where DAFoam's value and the requested value differ
visibly. **The predicted split holds: options DAFoam sets are overwritten; options DAFoam does
not set survive.**

**No FD table is owed.** No arm converged, so no gradient exists to check
(`DAFOAM_CHARTER.md` §2 gate not triggered; prereg §3 last paragraph).

### The one miss, and it is a reading rather than a run

The pre-registration's headline framing offered two branches — predictions hold, or an arm
returns `reason 2`. Neither branch anticipated that **the intermediate reading — "it reached and
still failed" — would be asserted from the `[NONZERO]` line between the run and the scoring.**
That is recorded as a miss of the *analysis*, not of the *registration*, which had pre-emptively
disarmed it. **Cost of the miss: zero core-min, and one paragraph of §1.**

## 4. What this discriminates: exact singularity is not perturbation-fixable

**The pivot pathology is not a small-pivot perturbation problem, and this item removes the last
cheap hypothesis that it was.** A diagonal shift, a larger shift, a smaller shift and more fill
are all *perturbations of an incomplete factorisation*. The class was already refuted offline
and is now refuted in-solver as well:

| evidence | source | what it says |
|---|---|---|
| `spilu` at drop_tol `1e-2`/fill 3, `1e-3`/5, `1e-4`/5, `1e-5`/10 | `cases/dafoam/PROOF.md` §25.3 | **`RuntimeError: Factor is exactly singular`** at every setting — *"incomplete factorization never succeeds on this matrix"* |
| `splu` at `diag_pivot_thresh` 0 / 0.1 / (default) | `PROOF.md` §25.3 | **always solves**: `2.3769e-10`, `6.4063e-12`, `2.535461e-12` |
| unpreconditioned GMRES, 1000 matvecs, no DAFoam | `PROOF.md` §25.3 | `1.0 -> 9.999687e-01`. DAFoam's KSP setup exonerated |
| zero rows / cols / diagonal entries | `PROOF.md` §25.3 | **0 / 0 / 0**; diagonal spread log10 **8.67** vs M6's 14.17 — five and a half decades *better* conditioned, and still fails |
| `zeropivot` raised six decades to `1e-8`, **verified landed** in the deployed factor | `W4_ADJOINT_PC_UNBLOCK.md` §2 | still `-9` |
| **this item**: shift type, shift amount (two decades apart), fill levels | §2 above | still `-9`, **and none of them landed** |

**The two halves fit together into one statement.** `zeropivot` is the option DAFoam does *not*
set, so it **reaches** the factor — and a factorisation told to tolerate pivots six decades
larger still divides by an exact zero. The shift options DAFoam *does* set **never reach**. So
the runtime-option axis is closed from both ends: *the one that lands does not help, and the
ones that might have helped cannot land.* **`spilu` fails because the factor is exactly
singular, not nearly singular. A perturbation of a singular factor is a different singular
factor.** The only thing that has ever worked on this matrix is **complete** factorisation with
pivoting — `splu` offline, `PCLU` in-solver.

**What this does NOT establish.** Nothing about closure physics — same 0.72-uniform inlet
defect, same 27 % bulk mismatch. Nothing about B3 Stage 4, which stays **BLOCKED** under R11.
Nothing about `mat_solver_type`, `nonzeros_along_diagonal` or `diagonal_fill`, the other
never-touched factor options — they are in `zeropivot`'s reachable class and are untested.
Nothing about the NASA hump. And nothing about whether a *source* change smaller than the PCLU
hunk exists; this item bounds the **runtime** axis only.

## 5. Cost, and the control arm's disclosure

| line | registered | measured |
|---|---|---|
| arms C, S-T, S-A10, S-A8, L-2 | **56.7 core-min**, ~170 s each | **152.53 core-min** |
| dollars at \$0.0513/core-h | \$0.048 | **\$0.130** |

**2.69x over the registered estimate, and 100 % of the overrun is arm C.** The four arms that
ran on a quiet box cost **6.80 + 6.60 + 6.60 + 6.93 = 26.93 core-min** against a registered
45.3 for four — **41 % under**, at 99–104 s each versus the 170 s basis.

**Arm C's 125.60 core-min is a load-contention artefact and must not be quoted as the cost of a
CBFS `-9` control.** It ran at **1884 s wall for a computation the next four arms did in
99–104 s** — an **18.5x** inflation. The chain's load gate (`load <= 10`, bounded, 90 x 20 s)
released arm C into a host still carrying the T-family's unpinned `simpleFoam` and
`buoyantBoussinesq` processes at load average ~12–13; the 4 pinned cores were shared, and
Open MPI spin-waits. This is the same mechanism `../adjoint_unblock_reproduce/RESULTS.md` §8
measured, and the same disclosure §6 there makes about arm S's 22.80 vs arm R's 5.93.

> **The honest figure for a CBFS `-9` control at np = 4 on `kspopts:v1` is ~6.8 core-min
> (~100 s). 125.60 core-min is what the box charged, and both numbers are reported.**

The 60 core-min ceiling registered for this item was **exceeded on the ledger (152.53)** and
**met on the computation (26.93 for the four uncontended arms, 33.7 if arm C is priced at its
uncontended twin)**. That is stated as an overrun, not argued away. **Charter note for the next
chain: a load gate at `<= 10` was not tight enough on this box; arm C proves an 18.5x tail
sits just inside it.**

## 6. The two-row answer for the defect note

Minimum working intervention on the CBFS adjoint `-9`, everything cheaper having been measured:

| route | source change? | reason | iterations | FD agreement | verdict |
|---|---|---|---|---|---|
| **serial, np = 1**, stock image | **no** | **-9** | 0 | n/a | **BLOCKED** — `../adjoint_unblock_reproduce/RESULTS.md` §3, arm N1, residual `7.091589775454e-04` |
| **runtime PC *type*** — `-sub_pc_type lu`, on the image built to let options through | **no** | **-9** | 0 | n/a | **BLOCKED** — arm K, dump still `type: ilu` |
| **runtime factor *options*** — shift type, shift amount `1e-10`/`1e-8`, fill levels 2 | **no** | **-9** | 0 | n/a | **BLOCKED** — **this item**, and the options never reached the deployed factor |
| *(runtime `zeropivot 1e-8`, which does reach)* | *no* | *-9* | *0* | *n/a* | **BLOCKED** — W4 §2 |
| **PCLU source rebuild** — `DAFOAM_SUBPC_TYPE=lu`, one hunk | **YES** | **2** | **667** | **0.0854 % / 0.0589 % / 0.1989 %**, zero sign flips | **PASS** — arms P / Pβ / FD re-anchor, `dafoam-subpclu:v2` |

> **Minimum working intervention = the source rebuild. Nothing cheaper works: serial no,
> runtime PC type no, runtime factor options no, and the one runtime option that demonstrably
> lands does not help either.** The upstream ask therefore stays fixed at **F1 + F2 + F3
> together** — F2 alone (relocating `KSPSetFromOptions`) is measured insufficient twice over,
> because the `PCASMGetSubKSP` loop overwrites both the type and the factor settings after
> PETSc has applied them.

## 7. Provenance

| number | where |
|---|---|
| ledger, all five rows | `/home/ubuntu/certonomous-runs/B3-ilu-shift-runtime/ledger.csv` |
| chain script, gates and options as run | `…/chain4.sh` |
| per-arm logs (1,415,5xx B each) | `…/logs/arm_{C,ST,SA10,SA8,L2}.log` |
| memory watch, 5 s cadence | `…/logs/mem_watch.log` |
| `spilu` exactly-singular table, `splu` solves, diagonal spread | `cases/dafoam/PROOF.md` §25.3 |
| `zeropivot 1e-8` reaches and still fails | `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §2 |
| arm K, arm N1, arm P, arm Pβ, FD re-anchor | `cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` §1, §3, §5 |
| image identity `dafoam-kspopts:v1` = `d9d2aed02e36`, `DALinearEqn.C` md5 `96f5762819e33efbdaad34181a214082`, 534 lines, `KSPSetFromOptions` line 351 | `docs/dafoam/TOOLCHAIN_INVENTORY.md` §6e |

**Nothing in this file was sent anywhere. Filing is Sanaa's call alone.**
