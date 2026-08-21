# B3 — does ILU-with-shift, set at runtime, lift the `-9`? PRE-REGISTRATION

**Written 2026-08-21, ~17:5x UTC, BEFORE any arm of this item ran.** DAFoam team Lane B,
against the supervisor's relay of Sanaa's 2026-08-21 approvals (item 1: the kspopts
runtime-shift arm, *"the one I most want answered with numbers"*). Run root
`/home/ubuntu/certonomous-runs/B3-ilu-shift-runtime/`. Cap **4 cores**
(`--cpuset-cpus 0-3`), `--memory=12g`, every container foreground and `timeout`-bounded,
`MemAvailable >= 12 GiB` checked in a bounded loop before each launch (Lane A may hold up to
14 GiB during its N=29 arm). **No background solver process; nothing needs killing.**

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

---

## 1. What is already answered, so this item does not re-buy it

`adjoint_unblock_reproduce/RESULTS.md` §5 measured **arm K** on `dafoam-kspopts:v1`, np = 4,
`PETSC_OPTIONS="-sub_pc_type lu -ksp_view"`, `DAFOAM_SUBPC_TYPE` unset:

- `**Completed**! Total iterations: 0. PetscConvergedReason: -9.`, residual `7.091590452305e-04`.
- **`PC Object: (sub_) 1 MPI processes / type: ilu`** in the same run's own `-ksp_view` dump.

**So `-sub_pc_type` is answered: it does not reach the sub-PC, even on the image built to let
runtime options through.** This item asks the remaining, sharper question: **of the factor
options, which ones reach, and does any of them lift the `-9`?**

## 2. The mechanism that fixes every prediction below, read from source

In `createMLRKSP`: `KSPSetUp(ksp)` at line ~229 is where `PCSetUp_ASM` creates the sub-KSPs and
PETSc applies `sub_`-prefixed options to them. DAFoam's `PCASMGetSubKSP` loop then runs at
232-330 and executes, per block, `PCSetType(MLRsubpc, PCILU)`, **`PCFactorSetShiftType`**,
**`PCFactorSetShiftAmount`** and **`PCFactorSetLevels`**. The kspopts patch relocates the
**outer** `KSPSetFromOptions` to line ~351, after the loop, and it acts on the parent KSP.

**Therefore the runtime-reachable set is exactly the factor options DAFoam never touches.**
Three are never touched: `nonzeros_along_diagonal`, `zeropivot`, `diagonal_fill` (and
`mat_solver_type`). Three are overwritten: shift type, shift amount, levels. **That split is
the prediction, and `-ksp_view` is the instrument that grades it.**

## 3. Arms, each with its prediction fixed now

Image **`dafoam-kspopts:v1`** (see §4 — no build is needed for this item), np = 4, `DAFOAM_SUBPC_TYPE` **unset** throughout, task
`compute_totals`, fresh staged case copy, cold `rm -rf processor*`, `-ksp_view` on every arm.

| arm | `PETSC_OPTIONS` (all with `-ksp_view`) | does it reach the sub-PC's factor? prediction | `-9` lifted? prediction |
|---|---|---|---|
| **C** — behaviour-neutral control | none beyond `-ksp_view` | n/a | **`-9`**, residual `7.091590452305e-04` to 13 digits; dump reads `type: ilu`, `1 level of fill`, `matrix ordering: rcm`, `using diagonal shift to prevent zero pivot [NONZERO]`, `tolerance for zero pivot 2.22045e-14`. **A difference here and the item stops.** This is arm K2 re-run with no `-sub_pc_type`, so it is also a reproduction check on that arm |
| **S-T** | `-sub_pc_factor_shift_type nonzero` | **NO — overwritten**, and **non-discriminating on the dump by construction**: DAFoam already sets `MAT_SHIFT_NONZERO`, so the dump reads `[NONZERO]` either way. Graded on the reason code only, and flagged here as the weak row rather than counted as evidence | **`-9`** |
| **S-A10** | `-sub_pc_factor_shift_type nonzero -sub_pc_factor_shift_amount 1e-10` | **NO — overwritten.** DAFoam calls `PCFactorSetShiftAmount(MLRsubpc, PETSC_DECIDE)` inside the block loop | **`-9`** |
| **S-A8** | `-sub_pc_factor_shift_type nonzero -sub_pc_factor_shift_amount 1e-8` | **NO — overwritten**, same line | **`-9`**, and if it *did* reach it would still fail: W4 §2 raised the **zero-pivot threshold** six decades to `1e-8`, verified it landed in the deployed factor (`tolerance for zero pivot 1e-08` visible in `PCView`), and still got `-9` |
| **L-2** | `-sub_pc_factor_levels 2` | **NO — overwritten.** DAFoam calls `PCFactorSetLevels` in the same loop; the dump is predicted to read **`1 level of fill`**, not 2. **This is the sharpest dump tell in the set**, because DAFoam's value and the requested value differ visibly | **`-9`** — and independently, `pcFillLevel` 1 **and** 4 through `daOptions` were both measured `-9` (`B3_duct_field_inversion.md`), because *"fill adds fill, not pivoting"* |

**`-sub_pc_factor_levels 1` is registered as NOT RUN, and the reason is Charter 2c.** DAFoam
already sets fill level 1, so that row returns the control's answer whether or not the option
reaches. **A row that cannot come out differently is not evidence** (`VERIFICATION_CHARTER.md`
§2c), and buying it would spend 11 core-min to learn nothing. It is named here so its absence
is a decision rather than an omission.

### The argument, from the source lines, for why the factor options are predicted not to survive

The supervisor's question is precise: these options are set on the sub-PC's **factor**, not on
its **type**, so do they survive the loop that overwrites the type? **They do not, and the
reason is ordering, not category.** `DALinearEqn.C`'s `PCASMGetSubKSP` loop executes, per
block and in this order: `PCSetType(MLRsubpc, PCILU)`, then
`PCFactorSetPivotInBlocks(MLRsubpc, PETSC_TRUE)`, `PCFactorSetShiftType(MLRsubpc,
MAT_SHIFT_NONZERO)`, `PCFactorSetShiftAmount(MLRsubpc, PETSC_DECIDE)` and
`PCFactorSetLevels(...)` — the same three factor setters this item drives from the command
line. PETSc applied the `sub_`-prefixed options earlier, at `KSPSetUp`; **these calls run
after, and last write wins.** The kspopts patch moves only the *outer* `KSPSetFromOptions`,
and re-calling it on the parent does not re-enter `PCSetUp_ASM`.

**So the predicted split is: options DAFoam sets are overwritten; options DAFoam does not set
survive.** `zeropivot` is in the second class and is already measured to land and still fail
(W4 §2). **The three factor setters above are in the first class. That is the falsifiable
claim, and `-ksp_view` grades it row by row.**

**The headline this item buys, whichever way it goes.** If the predictions hold: **no PETSc
runtime option lifts the `-9`**, one of them demonstrably *lands* and still fails, and the
upstream ask is fixed at **F1 + F2 + F3 together**. If any arm returns `reason 2`: the blocker
is reachable with **no solver-logic change at all**, the recompile this lab performed was never
necessary, and that is the bigger result. **Either way the record moves.**

**FD is not run in this item.** No arm is predicted to converge, so no gradient is predicted to
exist. **If an arm does converge, its FD table is mandatory before its number is quoted**
(`DAFOAM_CHARTER.md` §2) and is bought as a separate, re-registered item at the archived
probes — cells 5491 / 6740 / 12486 at h = 0.05, bar < 1 %, zero sign flips — against the PCLU
arm's `reason 2 / 667 iterations / 0.085 % / 0.059 % / 0.199 %`.

## 4. The image — `dafoam-kspopts:v1`, and no build is bought for this item

**`dafoam-kspopts:v1` already exposes both levers, measured rather than assumed**
(`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6e): `DALinearEqn.C` is **534 lines**, md5
`96f5762819e33efbdaad34181a214082`, carries **3 `DAFOAM_SUBPC_TYPE` occurrences** and has
`KSPSetFromOptions` at **line 351**, not 138. Its lineage is `dafoam-subpclu:v1` + the kspopts
patch. It is the image arm K2 ran on, so this item's control arm is directly comparable to a
measurement already on the record — **which is worth more here than a fresh image would be.**

**Two consequences worth stating.** (i) A `dafoam-kspopts:v2` is **not** bought for this item:
it would change the arm's lineage and not its answer, and the reproducible-provenance question
belongs to the team image below. (ii) The approval's *"single image exposing BOTH the sub-PC
type and `KSPSetFromOptions`"* **already exists as `kspopts:v1`** — what it lacks is a committed
provenance, and that is exactly what `cases/dafoam/patched_build/team/` is for. **No
`dafoam-subpclu-kspopts` layer is needed on top of it.**

**Disclosure that must travel with every number from this item:** because `kspopts:v1` is built
on `subpclu:v1`, **the image running these arms is capable of lifting the `-9`** through
`DAFOAM_SUBPC_TYPE=lu`, and does not, because the env var is unset. Every arm asserts the
**absence** of the sub-LU banner in its own log; a banner would invalidate the arm.

## 5. Cost of the arms, registered before they run

Basis: arm K2's measured **170 s at np = 4 = 11.33 core-min** on a quiet box — same image, same
case, same task, same rank count.

| line | runs | est. wall each | est. core-min |
|---|---|---|---|
| arms C, S-T, S-A10, S-A8, L-2 | 5 | ~170 s | **56.7** |
| *(`-sub_pc_factor_levels 1`, declined under Charter 2c)* | *0* | — | *0* |
| **total** | **5** | **~14 min** | **56.7** |

**56.7 core-min < the 60 core-min ceiling set for this arm, and each point is 11.33 core-min
< the 12 core-min per-point cap.** At \$0.0513/core-hour: **\$0.048**. No build is bought,
so no build cost is carried. Every arm is `timeout 2100`-bounded and by the case's own
`gmresMaxIters`. **Nothing here approaches \$25.**

**If an arm converges, the FD table is mandatory before its number is quoted**
(`DAFOAM_CHARTER.md` §2) and is bought as a separately registered item at the archived probes
— cells 5491 / 6740 / 12486 at h = 0.05, bar < 1 %, zero sign flips — reported **two rows**
against the PCLU rebuild's `reason 2 / 667 iterations / 0.085 % / 0.059 % / 0.199 %`:

| route | source change? | reason | iterations | FD agreement |
|---|---|---|---|---|
| **runtime shift**, this item | **no** | *to be measured* | *to be measured* | *to be measured, or n/a if `-9`* |
| **PCLU rebuild**, `dafoam-subpclu:v2` | **yes**, one hunk | **2** | **667** | **0.085 % / 0.059 % / 0.199 %** (2026-08-04 figures; the 2026-08-21 re-anchor is `PENDING`) |

## 6. Launch condition, and why this item had not launched when it was registered

**This item is registered and is not yet launched.** At registration the host carried **20
unpinned `simpleFoam` processes** from the T-family and a load average of **12.4**, and this
lane's four pinned cores were held by the still-running `chain3.sh` FD sweep. Under those
conditions a 4-rank DAFoam job on a shared `cpuset` degrades by a measured factor of roughly
**400** while reporting 300 % CPU, because Open MPI spin-waits
(`adjoint_unblock_reproduce/RESULTS.md` §8). **Launching into that would have bought timeouts,
not measurements, and would have charged a 26x budget overrun for them.**

**The gate: launch when `uptime` load average < 10 and `MemAvailable` >= 12 GiB, both checked
in a bounded loop, and when `chain3.sh` has released cores 0-3.** The gate is stated here so
the decision is on the record before the run rather than reconstructed after it.

## 7. What this item cannot establish

- Nothing about **closure physics** — same 0.72-uniform inlet defect, same 27 % bulk mismatch.
- Nothing about **B3 Stage 4**, which stays `BLOCKED` under R11 whatever any arm returns.
- Nothing about **`mat_solver_type`, `nonzeros_along_diagonal` or `diagonal_fill`**, the other
  three never-touched factor options. They are cheap to add and are deliberately not registered
  here: `zeropivot` is the one with a prior offline measurement to reproduce.
- Nothing about the **NASA hump**, where the same options have never been tried.

*Nothing below this line existed when this file was written. The arms launch only after it lands.*
