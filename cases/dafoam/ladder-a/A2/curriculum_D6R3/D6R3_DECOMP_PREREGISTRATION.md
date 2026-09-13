# D6R3 DECOMP — PRE-REGISTRATION OF THE DECOMPOSITION SWEEP

Item: **D6R3** (curriculum A2, DAFoam CRM wing, Mach 0.85)
Date: **2026-09-13**
Status: **DRAFT — nothing is sent, filed, uploaded or registered outside this box (rule 7).**
Frozen by sha at commit. **No compute may start before this file is a committed blob** (rule 2);
`d6r3_decomp_arm.sh` gate **G-PREREG** refuses the launch otherwise, by hashing this file and the
whole grading path against `HEAD`.

---

## 0. The question this sweep exists to answer

Four measured points at position 1 on the same fine mesh and the same 28-rank decomposition:

| `p` solver | position | max residual at `endTime` | × `primalMinResTol` | `CD` |
|---|---|---|---|---|
| published GAMG `relTol 0.1` | 1 | `nuTilda 1.194718885139746e-07` | **11.95** | `0.02090109066417552` |
| published GAMG `relTol 0.1` | 2 | `p 1.757696578179007e-06` | 175.77 | `0.02090262569125358` |
| GAMG `relTol 2.008e-03` | 1 | `p 7.600678874731434e-06` | 760.07 | `0.02090512806637335` |
| `PBiCGStab`+`diagonal` `0.1` | 1 | `p 7.177342318566405e-06` | 717.73 | `0.02090327575616875` |

Three of the four floor between `1.76e-06` and `7.60e-06`, all above the `1.0e-06` the gate
demands. One floors two orders lower. The gate is `primalMinResTol × primalMinResTolDiff =
1.0e-8 × 100 = 1.0e-06`, and **it is not touched by this sweep, nor is `endTime`** — loosening a
convergence criterion to pass it is the one move this family may never make.

**The hypothesis under test, named by the supervisor and NOT yet adopted:** the case's natural
floor is `O(1e-6 … 1e-5)`, the gate sits at or below it, position 2's 175.77× was never a defect,
and **position 1 at 28 ranks was simply the lucky one.**

**The experiment that decides it:** run the **published configuration, position 1, under several
decompositions**, changing nothing else.

---

## 1. What varies, and the source fact that makes it sufficient

**The only thing that differs between cells is `mpirun -np <RANKS>` and the cpuset.
There is NOT ONE staged file edit anywhere in this sweep.**

That is sufficient, and it is a source fact rather than an inference:

- `pyDAFoam.py:2228` — `f.write("numberOfSubdomains     %d;\n" % self.nProcs)`. DAFoam **rewrites**
  `system/decomposeParDict` from the MPI communicator size before calling `decomposePar`
  (`pyDAFoam.py:1456-1467`). The number written in the dictionary on disk is inert.
- Measured corroboration already on the record: the published `decomposeParDict` says
  `numberOfSubdomains 72`, and under `mpirun -np 28` the P0 log printed
  `Decomposition method scotch [28]`, three times, one per condition directory.

So the rank count **is** the decomposition, and it is read back from the runtime log by **IC-A**
rather than taken on trust (L-40: a load-bearing option is proven ACTIVE in the log, never merely
present in a dictionary).

**Why the rank count is a numerical parameter and not a scheduling one** — the mechanism this
sweep expects to see, stated before the measurement:

1. `smoothSolver` + `GaussSeidel` (the `U|T|e|h|nuTilda|k|omega|epsilon` block) is
   **processor-block** in parallel OpenFOAM: Gauss–Seidel inside each rank's cells,
   Jacobi across the processor boundaries. Its action is a function of the partition.
2. GAMG agglomerates **per processor**, so the coarse-level hierarchy — how many levels, how
   many coarse cells — changes with the rank count.
3. `pairGAMGAgglomeration.H:63` declares `static bool forward_`, initialised `true` at
   `pairGAMGAgglomeration.C:36` and toggled at `pairGAMGAgglomerate.C:333` (`forward_ =
   !forward_;`), used at lines 230/310/319 to reverse the sweep direction of pairwise
   agglomeration. It is **process-static and toggles per agglomeration level**.

**Declared before compute, so it cannot be claimed afterwards as a discovery:** item 3 couples
the two hypotheses rather than separating them. The number of agglomeration levels built by
position 1 depends on the per-rank cell count, so the *parity* of `forward_` at the start of
position 2 is itself a function of the rank count. **A `GATE REACHED` on G-MOVE therefore does
not isolate partitioning from agglomeration parity, and this sweep will not claim that it does.**
`forward_` remains **named and NOT adopted**: nothing here demonstrates it.

---

## 2. The cells

Producer: `d6r3_opt_runScript.py`, md5 `efc3e62699690edd32e4ee910aad09c8`, **untouched**.
Task: `run_model` (primal only — the cheapest path to the residual floors).
Mesh: `mesh/L2`, the published fine mesh, identical in every cell (**IC-G**).
Case: `mesh/L2/system/{controlDict,fvSchemes,fvSolution,decomposeParDict,createPatchDict}`, all
five **byte-identical** to `/home/ubuntu/dafoam-tutorials/CRM_Wing/system/` (**G-PUBLISHED**;
`fvSolution` md5 `36a8ad5cf2edd672b8aa752829647dfd`).
Disclosed lab addition, carried by every prior arm so the cells stay comparable to P0: the
`forces` function object appended to each condition's `controlDict`. It is an **observer** — it
computes and writes, it does not enter the equations.

| cell | ranks | why this count |
|---|---|---|
| `DECOMP_N28` | 28 | the count `P00` and `P0` both ran at, and the only count at which the published case has ever been seen to pass. Carries **G-DET**. |
| `DECOMP_N20` | 20 | the **production ceiling**: 96 − 48 reserved (propeller) − 20 reserved (DrivAer) leaves 28, and production will run at or below 20. Carries **G-PROD**. |
| `DECOMP_N16` | 16 | interior |
| `DECOMP_N12` | 12 | interior |
| `DECOMP_N08` | 8 | the longest lever arm on partition size that still leaves ~74k points per rank |

---

## 3. PREDICTIONS — registered before any compute, per cell

`R1(N)` = position-1 max residual over `{U0,U1,U2,he,p,nuTilda}` at `endTime = 2000`.

| cell | ranks | predicted `R1(N)` | predicted cell gate (`R1 < 1.0e-06`) | predicted step-1 `U0 finalRes` | predicted position-1 `CD` |
|---|---|---|---|---|---|
| `DECOMP_N28` | 28 | **exactly `1.194718885139746e-07`, field `nuTilda`** | **PASS** | **exactly `0.0944846591692384`** | exactly `0.02090109066417552` |
| `DECOMP_N20` | 20 | **> `1.0e-06`** | **GATE FAIL** | **≠ `0.0944846591692384`** | within `5.0e-04` rel of `0.02090109066417552` |
| `DECOMP_N16` | 16 | **> `1.0e-06`** | **GATE FAIL** | **≠ `0.0944846591692384`** | within `5.0e-04` rel |
| `DECOMP_N12` | 12 | **> `1.0e-06`** | **GATE FAIL** | **≠ `0.0944846591692384`** | within `5.0e-04` rel |
| `DECOMP_N08` | 8 | **> `1.0e-06`** | **GATE FAIL** | **≠ `0.0944846591692384`** | within `5.0e-04` rel |

The step-1 column is a **mechanism prediction, not an instrument control**. Both of its branches
are readable and both mean something: if step 1 at 20 ranks equals the 28-rank value to all
printed digits, then the processor-block `GaussSeidel` claim of §1 is **falsified** and this
record will say so loudly rather than quietly drop it.

---

## 4. GATES

Every threshold below is fixed at this commit. The grading path is
`d6r3_decomp_grade.py` (cell mode and `--rollup` mode) and nothing else.

| gate | criterion | verdict if met | verdict if not |
|---|---|---|---|
| **G-DET** | at 28 ranks, `R1` reproduces the P0 reading `nuTilda 1.194718885139746e-07` to all printed digits | `PASS` | `GATE FAIL` — **and the whole sweep is then `NOT A RESULT`**, because a case that does not reproduce itself at fixed ranks cannot be read for a rank effect |
| **G-MOVE** | `max_N R1(N) / min_N R1(N) ≥ 10.0` over cells that produced a number | `GATE REACHED` — **the floor moves with decomposition** | `GATE FAIL` — the floor is decomposition-stable |
| **G-PROD** | `R1(N) < 1.0e-06` at **every** rank count `N ≤ 20` | `PASS` — the published case passes at the production rank count | `GATE FAIL` — **the production rank count is a numerical choice that must be measured, not assigned** |
| **G-CD** | every cell's position-1 `CD` within `5.0e-04` relative of `0.02090109066417552` | `PASS` — "whatever is wrong, it is not the answer" survives a decomposition sweep | `GATE FAIL` — the reframing is wrong and the floors do reach `CD` |
| **G-ORD** (secondary) | where position 2 is reached, `R2/R1 ≥ 10` in every such cell | `PASS` | `GATE FAIL` |

`G-MOVE`, `G-PROD` and `G-CD` require **at least 3 usable cells**; fewer is `NOT A RESULT`.
`G-ORD` is readable only where position 1 passed its gate and the run went on to position 2; if
no cell reaches position 2 it is `NOT A RESULT`, never a silence.

**The gate can only turn a PASS or a GATE FAIL into NOT A RESULT, never the reverse.**

---

## 5. INSTRUMENT CONTROLS — every one designed so its failing branch is reachable

The predecessor's disclosed defect is **not** repeated here: `rc == 0` is not an instrument
control in an arm whose **predicted** outcome is `rc = 1`.

| control | what it checks | how its failing branch is reachable |
|---|---|---|
| **IC-A** | the log's `Decomposition method scotch [N]` equals this cell's rank count, three times | drive: the reader is handed the 28-rank P0 log while claiming 20 and must report MISMATCH |
| **IC-D′** | the run ended either `rc == 0`, or `rc == 1` **with** an `AnalysisError` naming the position that failed | any other `rc` (OOM 137, MPI_ABORT 59, R17 refusal 17) fails it |
| **IC-F** | `d6r3_rule17.json` says `OK` for all three conditions — the ranks read the staged mesh | a missing or non-`OK` file fails it |
| **IC-G** | `mp04/constant/polyMesh/points` md5 identical across all five cells | a cell whose file is absent or different fails it |
| **G-PUBLISHED** | all five staged `system/` dictionaries byte-identical to the published tutorial's, plus read-back of `relTol 0.1`, `endTime 2000`, `primalMinResTol 1.0e-8` | a leftover staged `fvSolution` from a previous arm fails it |
| **PLANT (rule 3)** | `--selftest` plants `9.876543210987654e-03` into the `endTime` `nuTilda` line and `[99]` into a decomposition line of a **real** log, and requires the reader to REPORT both | two blinded copies of the reader were run and both **REFUSED (exit 2)** |

**Completion rule, disclosed in advance.** These arms are **designed to abort** at the first
position whose primal fails the gate, so rule 4's all-or-nothing completion rule **does not
apply** to them and is not claimed. The artifact graded is the residual trace in the run log, and
the age datum, cold-start refusal and R17 mesh-read gate all still fire at launch.

---

## 6. COST — registered before compute, and honest about what the model is worth

Unit: **core-minutes** (wall s × ranks ÷ 60).

Model M1, anchored on **one** measured point (P0: 28 ranks, 637 s, two positions reached):

    wall(N, k) = 139 · (28/N)^0.5  +  k · 249 · (28/N)

`139 s` is P0's measured setup (three `decomposePar` + three mesh initialisations + warp + FFD);
`249 s` is P0's measured stepping time for one 2000-iteration position at 28 ranks; `k` is the
number of positions the cell reaches. The exponent `0.5` on the setup term is a **declared guess**
(decomposition is serial, mesh initialisation is not) and is fitted to nothing.

> **M1 IS FITTED AT ONE OPERATING POINT AND IS VALIDATED FOR NOTHING ELSE.** It is registered
> here so the sweep can be its **first out-of-sample test**. The completion report will state
> `actual/predicted` per cell **without re-fitting M1**, and will not present agreement at 28
> ranks — the anchor — as evidence that the model works anywhere.

| cell | ranks | predicted `k` | predicted wall s | **predicted core-min** |
|---|---|---|---|---|
| `DECOMP_N28` | 28 | 2 | 637 | **297.3** |
| `DECOMP_N20` | 20 | 1 | 513 | **171.0** |
| `DECOMP_N16` | 16 | 1 | 620 | **165.3** |
| `DECOMP_N12` | 12 | 1 | 793 | **158.6** |
| `DECOMP_N08` | 8 | 1 | 1132 | **150.9** |
| **sweep** | | | ~2 825 s wall (batched) | **943.1** |

Registered envelope, because `k` is an outcome and not a setting: **826.9 core-min** (every cell
aborts at position 1) to **1 407.8 core-min** (every cell reaches position 2).

Derived, **not measured**: 943.1 core-min = 15.72 core-h → **$0.81** at the owner-stated
c7a.4xlarge rate of **$0.0513/core-h**. Envelope **$0.71 – $1.20**. `cost_basis =
reported-by-owner; the box cannot read its own billing` (`COMPUTE_BUDGET_CHARTER` §5).

**Directive #17: no run in this sweep is stopped by a time or budget cap.** A crossing of the
envelope is **REPORTED**, and the crossing cell is graded `NOT A RESULT` on that ground.

---

## 7. COMPUTE DISCIPLINE

- Idle cores are measured **per core**, from two `/proc/stat` samples 5 s apart, at each launch;
  only cores ≥ 85 % idle are taken. Never a remembered number.
- Ceiling **28 cores**: 96 − **48 reserved for the propeller lane** − **20 reserved for the
  DrivAer lane**. The sweep never holds more than 28 and **never borrows from either reservation.**
- The propeller family takes its 48 the moment its mesh gate passes, so the sweep is **sequenced
  to finish rather than to be pre-empted**: the most load-bearing and cheapest cell first.
  - batch 1: `N28` alone — carries **G-DET**
  - batch 2: `N20` + `N08` concurrently (28 cores), `N08` excluding `N20`'s measured cpuset
  - batch 3: `N16` + `N12` concurrently (28 cores), `N12` excluding `N16`'s measured cpuset
- Wall-clock contention from work already on the box is named **separately as contention** in the
  completion report and is **never absorbed into the actual/predicted ratio**
  (`COMPUTE_BUDGET_CHARTER` §6).

---

## 8. A SOURCE CHECK RECORDED BEFORE COMPUTE: `relaxationFactors p 1.0` is NOT a defect

A previous lane named **pressure under-relaxation** as the leading remaining direction, because
`fvSolution` carries `p 1.0` in both `relaxationFactors` blocks. **That candidate is struck**, and
the reason is read out of the installed toolchain, not out of recollection:

1. The solver is **`DARhoSimpleCFoam`**. `pEqnRhoSimpleC.H:3-4` builds
   `rAU = 1/UEqn.A()` and `rAtU = 1/(1/rAU - UEqn.H1())`. The `rAtU` operator **is** the SIMPLE**C**
   consistent formulation. The trailing `C` is not decoration.
2. `pEqnRhoSimpleC.H:49-50` reads, verbatim:
   `// Relax the pressure equation to maintain diagonal dominance` / `pEqn.relax();`.
   The stated purpose of the call is the **diagonal-dominance clamp**, not under-relaxation.
3. `fvMatrix<Type>::relax(const scalar alpha)` does
   `D[celli] = max(mag(D[celli]), sumOff[celli]);` then `D /= alpha;` then
   `S += (D - D0)*psi_.primitiveField();`. **At `alpha = 1.0` the division is the identity, so
   the only surviving effect is the diagonal-dominance clamp.** `equations { p 1.0; }` is
   therefore the setting that arms that clamp with **zero** under-relaxation — it is load-bearing
   *because* it is 1.0.
4. `GeometricField::relax(alpha)` does `operator==(prevIter() + alpha*(*this - prevIter()))`.
   At `alpha = 1.0` this is **exactly** the identity, so `fields { "(p|rho)" 1.0; }` is a true
   no-op.
5. The `fvSolution` carrying these values is md5 `36a8ad5cf2edd672b8aa752829647dfd`, **byte-
   identical** to `/home/ubuntu/dafoam-tutorials/CRM_Wing/system/fvSolution`. `p 1.0` is the
   **published** value, not a lab choice.

**Conclusion: `p 1.0` is the expected SIMPLEC setting. Under-relaxing `p` would be a deviation
away from the published method, not a stabiliser.** The candidate drops to the bottom of the
list. One nuance worth keeping on the record: `p 1.0` does **not** mean the same thing in the two
blocks — in `fields` it is inert, in `equations` it arms a clamp. Lowering it in the `equations`
block would both under-relax **and** keep the clamp.

---

## 9. WHAT THIS SWEEP DECIDES, stated before the numbers exist

- **If the floor moves with decomposition and frequently sits above `1.0e-06`** (G-MOVE
  `GATE REACHED`, G-PROD `GATE FAIL`): the published case passes only at some decompositions,
  the 11.95× outlier was **luck**, and the production rank count is a **numerical** choice that
  must be measured rather than assigned.
- **If the floor is stable at ~`1.19e-07` across decompositions** (G-MOVE `GATE FAIL`): position
  2's elevation is a real **ordinal** defect, and the ordinal question must be reopened with an
  arm that actually reaches instance 2.
- Either way, **G-CD** is the reframing's own test: if the `CD` spread stays at `O(1e-4)` relative
  while the floors span two orders, the floors are not reaching the answer.

---

## 10. AMENDMENT RECORD

~~None.~~ **STRUCK 2026-09-13T21:10Z — superseded by ADDENDUM 1 at the foot of this file.**
Amendments before first compute must state the condition and how it was checked, by naming
the run directory that does not yet exist. After first compute this document is closed; changes
land only as dated addenda that cannot alter a gate, threshold, cap or label, and originals are
struck, never rewritten.

---

# ADDENDUM 1 — 2026-09-13T21:10Z — TWO REPAIRS, AND A DISCLOSED LAUNCH DEFECT THAT COST FOUR CELLS

**Version 1.1. Lines whose number changed above this section: 0.**
(The single line struck in §10 is struck in place and adds no line.)

**This addendum alters NO gate, NO threshold, NO cap and NO label.** §1–§9 stand as frozen at
`c527036b8b4f777bb5a9d468c62049d6b15c2ae4`. The five cells, the five gates, their thresholds,
the 28-core ceiling and the cost envelope are exactly as registered.

## A1.1 THE LAUNCH DEFECT — measured, self-stopped, and it cost four cells

`DECOMP_N28` launched at `2026-09-13T21:02:42Z` and is the first compute under this
registration. Within two minutes the ledger showed **five** cells up, not one.

**Cause, and it is a shell bug rather than a judgement:** `d6r3_decomp_sweep.sh` obtained each
cell's pid with `P=$(start 28 "")`. **Command substitution runs `start()` in a subshell**, so the
backgrounded arm is a **grandchild** of the driver, and `wait "$P"` is therefore not waiting on a
child at all. Driven directly, it prints `bash: wait: pid N is not a child of this shell` **and
returns 0** — a wait that is not a wait, failing silently in the permissive direction. Every
batch opened immediately.

**Measured consequence:** five cells claimed **56 distinct cores** against this registration's
**28-core ceiling** (§7), with `DECOMP_N20`'s cpuset nested inside `DECOMP_N28`'s and
`DECOMP_N08`'s inside `DECOMP_N16`'s. That reaches into the reserved **48-core propeller** and
**20-core DrivAer** lanes, which this lane may never borrow from, and it contradicts §7 of this
document.

**Correction.** `DECOMP_N20`, `DECOMP_N16`, `DECOMP_N12` and `DECOMP_N08` were **stopped** and
their arm directories **removed**. Their logs are retained, renamed
`*_ABORTED_LAUNCH_DEFECT_NOT_A_RESULT.log`. **They are `NOT A RESULT` and nothing from them is
cited anywhere.** `DECOMP_N28` — which is *exactly* registered batch 1, alone, at 28 cores, the
ceiling — **continued uninterrupted**, arm-shell pid `1725442`, container pid `1725971`, cpuset
`1,3,4,5,7,9,10,11,13,15,17,19,20,21,23,24,25,27,28,29,32,34,35,37,39,42,43,44`.

**Stopped for a disclosed launch defect, never for a cap. Directive #17 is untouched.**

**Waste, named separately and never absorbed into any `actual/predicted` ratio**
(`COMPUTE_BUDGET_CHARTER` §6): 4 cells × ~1.6 min × (20+16+12+8 = 56 ranks) =
**89.6 core-min GROSS WASTE.** Reported, not absorbed. The four cells will be re-run from cold
and their costs counted afresh.

**Disclosed honestly: `DECOMP_N28` shared 20 of its 28 cores with `DECOMP_N20` for ~96 s before
the correction.** That is **contention** and it inflates `DECOMP_N28`'s wall time only. It cannot
touch its numbers: the rank count is fixed at 28, the decomposition is read back by **IC-A**, and
nothing in the solve depends on wall-clock. `DECOMP_N28`'s `actual/predicted` ratio is reported
with this contention **named beside it**, never folded into it.

## A1.2 REPAIR 1 — IC-G's reader was BLIND. `VERIFICATION_CHARTER` §2d.1, all four conditions

**(1) A demonstrable error, not a preference.** The launcher's `STAGE_HASH` ledger line printed
`mp04_points=` **empty**, and the grader's IC-G returned `md5=None`. Both read
`mp04/constant/polyMesh/points`. **The mesh is stored gzipped**: `ls` of that directory shows
`points.gz` (13 565 959 bytes) and **no** `points`. The control read nothing.

**(2) Established by an instrument independent of the hypothesis, one that grades nothing.** The
`STAGE_HASH` ledger line is a **recorder**: it prints a hash and decides nothing, and it cannot
know which direction any verdict wants. It is what showed the empty field. The disk listing
corroborates it.

**(3) Disclosed, the instrument named, and what moved QUANTIFIED.**
- **Pre-repair:** `mp04_points_md5 = None`, ledger field `mp04_points=` (empty), IC-G **FAIL** on
  every cell.
- **Post-repair, read off the live `DECOMP_N28` arm directory:**
  `mp04_points_md5 = f958f3e9cd01fa6179b360c464e91663`, from
  `DECOMP_N28/mp04/constant/polyMesh/points.gz`, IC-G **ok**.
- **No verdict moves toward a pass.** The blindness failed **CLOSED**: `md5=None` makes IC-G
  fail, which makes the cell `NOT A RESULT`, and the rollup's `IC-G-cross` `GATE FAIL`. The
  repair can only turn a `NOT A RESULT` into a readable cell — it can never rescue a `GATE FAIL`
  into a `PASS`. **Nothing a verdict depends on is repaired on the authority of the verdict it
  produces.**

**(4) Pre-repair values recorded beside the repaired ones.** Done, immediately above.

**The repair, and it is an accept-either, never a widening:** both instruments now try `points`
then `points.gz`, **name the file they hashed** so a future silence is attributable, and the
launcher **REFUSES (exit 9)** if neither exists. Driven to both sides before being believed
(L-570): on the live `DECOMP_N28` arm directory it reports the md5 above; on a directory with an
empty `polyMesh/` it reports `md5=None` and grades `NOT A RESULT`.

## A1.3 REPAIR 2 — the driver

`d6r3_decomp_sweep.sh` now backgrounds each cell **inline** and captures `$!` in the driver's own
shell, and additionally **refuses to open a batch while any `d6r3_DECOMP_*` container is still
up**, so the 28-core ceiling is **enforced by the driver rather than merely intended by it**. It
takes an optional `FIRST_BATCH` argument so batches 2 and 3 can be resumed without disturbing the
`DECOMP_N28` cell that is already running. **This repair is not on the grading path at all** —
it is launch mechanics — so §2d does not reach it; it is disclosed here regardless.

## A1.4 WHAT IS UNCHANGED

The frozen producer is not edited (md5 `efc3e62699690edd32e4ee910aad09c8`).
`primalMinResTol`, `primalMinResTolDiff` and `endTime` are untouched.
No gradient work exists anywhere in this sweep: every cell is `run_model`, never `compute_totals`
and never `check_totals`.
**SUBMISSIONS PARKED.** Nothing is sent, filed, uploaded, registered or posted.
