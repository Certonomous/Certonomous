# Curriculum D19 — 2-D COMPRESSIBLE SINGLE-POINT CONSTRAINED DRAG MINIMISATION, on D15's ground, on TWO TOOLCHAIN ROWS, with the FD PLATEAU ESTABLISHED FIRST — PRE-REGISTRATION

**Frozen 2026-08-31 by the dafoam team's D19 lane, BEFORE any run root exists. FREEZE ONLY: not enqueued, zero solver core-minutes spent by this document.**

**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box. SUBMISSIONS ARE PARKED and sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Authority.** Sanaa's directive 2026-08-31, verbatim, at `etc/sessions/2026-08-31T2037Z_sanaa_dafoam_compressible_multipoint.md`: *"yes so the dafoam team can do the compressible using the patched gradients, and we need to find a solution for multipoint optmization (both compresisble and incompressible"*. **This item is the FIRST half only — compressible, on the patched gradients, SINGLE POINT.** The multipoint half is not touched here; see §12.

---

## ⚠ 0. WHAT THIS ITEM IS **NOT** — read before anything else

> **D19 IS SINGLE-POINT. IT IS NOT SO-3b AND IT DOES NOT RELEASE SO-3b's GATE.**

SO-3b is Mach multipoint on the compressible path, and Sanaa's 2026-08-31 ruling gates it behind the **`SHIPPED`** compressible gradient gate **passing** (`cases/dafoam/ladder-a/A1/SO3b_STUB.md` §3: *"SO-3b does not start until the SHIPPED gradient gate on the compressible path PASSES … No such item exists on this box today."*). Registered here, before compute, so it cannot be read the other way later:

1. **D19 registers exactly ONE operating point** — M 0.288, the D15 ground. No second Mach number. No second Reynolds number. No weighted objective over operating points.
2. **`alpha` is a DESIGN VARIABLE trimming to a single `CL` target. That is a trim, not a multipoint**, and this document will not be cited as one.
3. **D19 produces no `SHIPPED`-row `G5` `PASS` and claims none.** Its `SHIPPED` row is expected to fail and is registered to be reported as a failure if it does (§7 P7). **SO-3b's gate is untouched and remains closed after D19 whatever D19 returns.**
4. **If the design work of this item ever drifts toward a second operating point, the item STOPS and the question goes to the `dafoam-supervisor`.** It is not amended into a multipoint after compute; rule 2 forbids it and §0 is the pre-registered tripwire.

---

## 1. THE GROUND, AND WHY THIS ONE

**Chosen: D15's ground.** A1 NACA0012, **4,032 cells**, `DARhoSimpleFoam`, **M 0.288** (`U0 = 100.0` m/s, `p0 = 101325.0` Pa, `T0 = 300.0` K, `nuTilda0 = 4.5e-5`, Spalart-Allmaras via `nuTilda`), baseline `aoa0 = 4.0` deg, `CL_target = 0.5`, all read from `cases/dafoam/ladder-a/A1/curriculum_D15/d15_runScript.py:31-35,44-50,178-179`.

**The genuine gap this fills, stated from the grid and not from the lab's stale story.** `docs/capability/dafoam_GRID.md` records the 2-D · steady · subsonic-compressible and 2-D · steady · transonic cells as `CAN NOT DO — not attempted` in **both** columns. The **first** column is stale — D15 and D16 have run and their `PATCHED` rows are `PASS`. The **second** column, *"optimization converged"*, is **correct and is the real gap**: *"D15 runs no optimiser"*, *"D16 runs no optimiser"*. **No 2-D compressible optimisation has ever been attempted in this lab.** That is what D19 attempts, and the staleness finding is recorded in `D15_D16_FD_STEP_TABLE.md` §4 rather than relied on here.

**Not a re-run of something already passed.** `curriculum_D8R/RESULTS.md` is an item `PASS`, two rows, on **A6 CRM wing-alone at M 0.85** with `DARhoSimpleCFoam`, both rows printing `EXIT: Optimal Solution Found.` at 8 and 12 majors of 30. **3-D compressible optimisation is done.** D19 is the 2-D cell, which is a different cell and is empty.

### 1.1 Why D15's ground and not D16's — the four reasons, and the risk being bought

The companion record `D15_D16_FD_STEP_TABLE.md` §1 measures, from both items' frozen artefacts, that **neither** ground has a fully proved plateau on the `PATCHED` row, and that the failures sit on **opposite functions**: D15 fails on `CD` (`shape[7]`, one-sided, 21.6299 % fine-side), D16 fails on `CL` (`shape[6]`, one-sided, 14.0978 % coarse-side). A lift-constrained drag minimisation follows both functions.

1. **The plateau evidence does NOT select the ground, and is not pretended to.** One one-sided component each, one extra decade to close each, the same cost either way. Choosing D16 "because its objective gradient is proved" would ignore that its constraint gradient is not.
2. **§9 decides it.** `DAFOAM_CHARTER.md` §9: an optimiser stopped by a cap is `GATE REACHED` or `NOT A RESULT`, **never** `PASS`. The strongest result available for a first-ever cell is a *converged* optimisation. D15 at M 0.288 is shock-free, so the objective landscape is smooth and the line search well-conditioned. D16 at M 0.685 on a section at ~4-5 deg incidence carries a supersonic pocket, and shock motion under design change is the classic cause of a stalled line search. **D15 maximises the probability of a `PASS`-eligible first result.**
3. **The two-row provenance is far sharper on D15.** On D15 the `SHIPPED` adjoint misses FD by **44.8738 %** on `shape[6]`, where `PATCHED` misses by **0.0072 %** — and `shape[6]` carries **76.414 %** of the `CD` gradient's norm, i.e. the shipped optimiser would follow a ~45 %-wrong *dominant* search direction. On D16 the `SHIPPED` `CD` aggregate is **1.9648 %**, which **passes** band E, and the row fails band D on one component at **5.1511 %**, barely over the line. A rung whose verdict must travel with "the shipped toolchain fails on this ground" is served by the 44.87 % ground, not the 5.15 % one.
4. **The transonic risk is already banked and is not this cell's novelty.** D8R took it in 3-D and won. Taking it again in 2-D buys a harder landscape without buying a cell that D19 would not otherwise fill.

> **THE RISK BOUGHT, NAMED RATHER THAN ARGUED AWAY.** At M 0.288 the flow is only weakly compressible — density varies by roughly 4 % — so a fair critic says the 2-D compressible cell is being filled by a case that is compressible in its solver and its state equation but not dramatically so in its physics. **That objection is accepted, not rebutted.** The capability is nonetheless real: `DARhoSimpleFoam` carries density as a state with a full energy equation, and the adjoint tapes that compressible system, which is what the cell asks. **D20 — this same design on D16's transonic ground — is named here as the immediate successor so the family does not stop at the weakly-compressible case.** D20 is not registered by this document and no gate here reaches it.

---

## 2. THE TWO PHASES, AND WHY PHASE 2 IS GATED

**Phase 1 — `PLATEAU`.** An FD step-sweep that establishes, on the `PATCHED` row, a step whose plateau is **two-sided** on **all five** registered components and on **both** functions. No optimiser runs.

**Phase 2 — `OPTIMISE`.** The two-row optimisation with its §9 endpoint FD tables. **Phase 2 launches only if phase 1's gates pass.**

**Why gated.** `DAFOAM_CHARTER.md` §2 bars an unverified gradient from entering an optimisation, and §3 requires the step *proved* to lie in the plateau, forbidding *"Quoting an FD number from a single step"* and *"Selecting the step after seeing which one agrees"*. `D15_D16_FD_STEP_TABLE.md` §1 establishes that the proof does not exist yet on this ground, and §1.3(a) that the 21.6299 % excursion is measured at 1e-4 — a step `VERIFICATION_CHARTER.md` §7 step 5 does not sanction for grading — but that 1e-3 sits at an **edge** of §7's range with its only in-range neighbour on one side, which bounds a flat without bracketing one. **Launching an optimiser on that is exactly what §2 forbids.**

**The branch is mechanical, not a person reading a page.** `d19_chain_driver.sh` evaluates phase 1's gates and launches phase 2's arms **only** on `G19-1a PASS` and `G19-1b PASS` and `G19-1d PASS`; on any other outcome it writes `STATUS.D19_chain` = `PHASE2_NOT_LAUNCHED_BY_REGISTERED_BRANCH` and exits 0. Precedent: `curriculum_D12R2` — *"PHASE 2 WAS NOT"* launched, by its registered branch.

---

## 3. THE ARMS

All arms run in the container images of §8. `MESH` is a script arm; all others are solver arms and are subject to the strict completion rule of §6.

### Phase 1 (`PATCHED` image only — nothing is proposed to stand on the shipped gradient)

| arm | np | what it does | cap (core-min) | predicted (core-min) |
|---|---|---|---|---|
| `MESH` | 1 | builds the 4,032-cell mesh; asserts cell count and md5-identity against D15's mesh | 5.0 | 0.2 |
| `X2` | 2 | patched adjoint, `CD` and `CL`, all DVs | 20.0 | 1.8 |
| `S2` | 2 | the **five-step** sweep, 5 components, `CD` and `CL` | 90.0 | 5.7 |
| `S1` | 1 | the **selected step only**, 5 components, `CD` and `CL` | 25.0 | 1.0 |
| | | **phase 1 total** | **140.0** | **8.7** |

**The sweep, frozen.** `shape`: **{3e-2, 1e-2, 1e-3, 1e-4, 1e-5}**. `patchV`: **{3e-1, 1e-1, 1e-2, 1e-3, 1e-4}**. Central differences, `step_calc="abs"` (`VERIFICATION_CHARTER.md` §7 step 5). Three of the five are D15's own registered steps and are the reproduction control; the two new ones — one decade coarser and one decade finer — are what bracket the flat.

**Components, frozen — identical to D15's** (`d15_grade.py:78`): `shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`.

**Primal tolerance, frozen: `primalMinResTol = 1.0e-8`**, the value D15's graded run used (`d15_runScript.py:45`). `DAFOAM_CHARTER.md` §3 requires the sweep be run at the tolerance the graded run uses, on the S1-CBFS incident where a loose primal moved a cell from 25.9 % to 0.032 %.

### Phase 2 (both rows)

| arm | row | np | what it does | cap (core-min) | predicted (core-min) |
|---|---|---|---|---|---|
| `O-P` | PATCHED | 2 | IPOPT `run_driver`, trim then optimise | 55.0 | 14.4 |
| `O-S` | SHIPPED | 2 | IPOPT `run_driver`, trim then optimise | 55.0 | 14.4 |
| `F-P` | PATCHED | 1 | endpoint FD at `O-P`'s final design, 3 steps | 15.0 | 4.0 |
| `F-S` | SHIPPED | 1 | endpoint FD at `O-S`'s final design, 3 steps | 15.0 | 4.0 |
| | | | **phase 2 total** | **140.0** | **36.8** |

**Decomposition, disclosed as `DAFOAM_CHARTER.md` §5 requires it to be, in the same table as every number.** np = 2 uses `d15_decomposeParDict` verbatim — method **`simple`**, subdivision as that file states, `numberOfSubdomains 2`. np = 1 is serial, no decomposition. **§5 forbids carrying an FD reference across np**, which is why `S1` exists: it re-measures the selected step serially and `G19-1d` gates the two against each other before any parallel figure is carried into phase 2.

**Endpoint FD steps, frozen as a rule not a value:** the phase-1-selected step **`s*`**, plus `s*×10` and `s*÷10`. This makes each endpoint table carry **its own three-point plateau reading** rather than inheriting phase 1's — which matters here more than usual, because §5.1 records that the optimiser's own starting point is not the point phase 1 measures.

---

## 4. THE OPTIMISATION, FROZEN

Read from `d15_runScript.py`, which already carries a complete optimisation setup that D15 never executed.

| item | registered value | source |
|---|---|---|
| objective | minimise `scenario1.aero_post.CD` | `d15_runScript.py:178` |
| constraint | `scenario1.aero_post.CL` **equals `CL_target = 0.5`** | `:179`, `:35` |
| design variables | `shape` (8, `nom_addShapeFunctionDV`, bounds ±1.0, scaler 10.0) + `patchV` (`U0` **fixed at 100.0**, `aoa` free in **[0, 10] deg**, scaler 0.1) — **9 DVs** | `:154`, `:173-175` |
| geometry | `FFD/wingFFD.xyz`, LE/TE shape functions coupling j=0 and j=1 in opposite directions | `:115`, `:152-153` |
| trim | `optFuncs.findFeasibleDesign(["…CL"], ["patchV"], targets=[0.5], designVarsComp=[1])` **before** `run_driver` | `:239` |
| optimiser | **IPOPT** via `om.pyOptSparseDriver()` | `:196-197`, `:210` |
| `tol` / `constr_viol_tol` | **1.0e-5** / **1.0e-5** | `:211-212` |
| **`max_iter`** | **40 — RE-REGISTERED HERE**, not the script's 100 | this document |
| other IPOPT options | `print_level 5`, `output_file opt_IPOPT.txt`, `mu_strategy adaptive`, `limited_memory_max_history 10`, `nlp_scaling_method none`, `alpha_for_y full`, `recalc_y yes` | `:213-219` |
| adjoint options | `gmresRelTol 1.0e-6`, `pcFillLevel 1`, `jacMatReOrdering rcm` | `:71` |

**`max_iter = 40` is a BUDGET, not a settle criterion** (`VERIFICATION_CHARTER.md` §4; `DAFOAM_CHARTER.md` §9). Its basis is measured, not guessed: D8R converged at 8 and 12 majors of 30 on 3-D twist; D13 converged in 9-11 majors on 4 incompressible DVs; D2 terminated `Inform = 0` on both IPOPT and SLSQP. 40 gives roughly 3× the observed need for a 9-DV problem. **Reaching it is a failure to converge and is graded as one.**

### 4.1 The improvement is measured from the TRIMMED start, and this is registered because it is the easy place to inflate a number

`findFeasibleDesign` raises `aoa` from 4.0 deg until `CL = 0.5`, and raising `aoa` **raises `CD`**. D15's frozen baseline is `CD = 0.014600274376560973` at `CL = 0.4228845159564578` — i.e. at `aoa = 4.0`, **not** at the trimmed start. **Measuring the reduction from D15's untrimmed baseline would count the trim's drag penalty as an optimiser achievement.** Frozen:

> **`CD_0` is the objective at major 0 of `opt_IPOPT.txt` — the trimmed feasible start. `CD_f` is the objective at the final major of the same file. The drag reduction is `(CD_0 − CD_f)/CD_0`, both values read from the optimiser's own history file and from nowhere else.** This is D4's instrument (`curriculum_D4/RESULTS.md:128`: `CD₀` major 0 → `CD_f` major 80, both from `O/opt_IPOPT.txt`).

---

## 5. THE GATES

Verdicts come from the fixed vocabulary and from nothing else: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

### Phase 1

**`G19-1a` REPRODUCTION.** For each of the three steps shared with D15, and each of the five components, and both `CD` and `CL`: `S2`'s value reproduces D15's frozen `F-P/d15_F.json` value to **≤ 0.5 %** relative. And `X2`'s adjoint reproduces D15's frozen `X-P/d15_X.json` adjoint to **≤ 0.1 %** relative on every component. → `PASS` / **`NOT A RESULT`**. A miss means this is not the same instrument D15 ran and nothing downstream may be compared to D15.

**`G19-1b` PLATEAU — the gate the whole item turns on.** Among the candidate steps **`{1e-2, 1e-3}` for `shape` and `{1e-1, 1e-2}` for `patchV`** — i.e. those inside `VERIFICATION_CHARTER.md` §7 step 5's sanctioned range `[1e-3, 1e-2]` **and** possessing both neighbours in the five-step sweep — the **selector** (§5.1) chooses `s*`. `G19-1b` is **`PASS`** iff, at `s*`, **every one of the five components on BOTH `CD` and `CL` has both neighbour deviations ≤ 10.0 %** — a **two-sided** plateau, `max`, not the `min` that D15's own rule used. Otherwise **`GATE FAIL`**, and phase 2 launches nothing.

**`G19-1c` PLANTED CONTROL.** `PLANT = 1.234e-03`, D15's own value, injected into the on-disk FD table and read back by the grading reader; the reader **refuses (exit 2)** if it cannot see it. `CLAUDE.md` rule 3. Not a graded gate — a refusal condition on every reader in the item.

**`G19-1d` DECOMPOSITION (§5).** At `s*`, `S1` (np = 1) and `S2` (np = 2) agree to **≤ 2.0 %** on every component and both functions. → `PASS` / **`GATE FAIL`**. A miss means A4's decomposition defect — measured at a factor of **16,600** between two decompositions of one mesh — reaches this ground, and phase 2 does not launch on a carried reference.

### 5.1 THE SELECTOR, AND WHY IT IS NOT "SELECTING THE STEP AFTER SEEING WHICH ONE AGREES"

`DAFOAM_CHARTER.md` §3 forbids *"Selecting the step after seeing which one agrees."* **What it forbids is selecting by agreement with the ADJOINT.** §7 step 1 *requires* selecting by flatness of the FD curve. The distinction is the whole defensibility of this item, so it is made mechanical:

> **THE SELECTOR RULE, FROZEN.** Among candidate steps, `s*` is the one minimising `max` over components and over both functions of the two neighbour deviations. Ties break to the **larger** step. **The selector reads only `rows[].fd`. It is handed no adjoint. `d19_select_step.py` asserts, at entry, that no adjoint array is present in its input, and refuses if one is** — so the prohibition is enforced by the code and not by the author's intention.

The selector's outcome is **not** free: §7 P1 predicts it in advance, before the sweep runs, and a miss is a `GATE FAIL`, not a re-selection.

### Phase 2, per row

**`G19-2a` COMPLETION — all of it or none of it** (`CLAUDE.md` rule 4). `rc = 0`; an `End` line; **last time == `endTime`**; fields present; `ExecutionTime` count == `endTime`; and **every field at `endTime` newer than the case's own `0/T`** — the age guard. The launch guard refuses a case where `0` or a time directory already exists. Any clause failing → the arm is **`NOT A RESULT`**.

**`G19-2b` TERMINUS (§9).** Read twice and independently, as D8R read it: from the grader's own output, and directly from the named arm log. `EXIT: Optimal Solution Found.` within 40 majors → **`PASS`**-eligible. `EXIT: Maximum Number of Iterations Exceeded.` → **`GATE REACHED`** if `G19-2c` is met, else **`NOT A RESULT`**. **No other outcome is `PASS`, and the size of the improvement never converts a cap-stop into one.**

**`G19-2c` IMPROVEMENT, band + trim.** Drag reduction `(CD_0 − CD_f)/CD_0` in **[3, 35] %**, with the trim held: `|CL_f − 0.5| ≤ 5.0e-3` (D8R's registered trim tolerance). → `PASS` / `GATE FAIL`.

**The band is wide and that is a disclosure, not an oversight.** This lane has never optimised on this ground, and no prior in this lab bounds a 2-D compressible NACA0012 shape optimisation at M 0.288 with 9 DVs. A narrow band would be a claim about physics for which no evidence is held. **A wide band is a weak prediction and is registered as one**; the falsifiable weight of this item sits on P1 and P7, not on P6.

**`G19-2d` ENDPOINT FD (§9) — at the FINAL design point, not the baseline.** At `s*`, on the five components, on both `CD` and `CL`: **band D 5.0 % per component**, **band E 5.0 % on the aggregate `‖J_an − J_fd‖ / ‖J_fd‖`**, **zero sign flips**, and **a two-sided plateau at `s*` from the endpoint's own three-step sweep**. → `PASS` / `GATE FAIL` / `NOT A RESULT` (no plateau). §9's reason, quoted because it is not a nicety: *"A gradient verified at iteration 0 is not verified at iteration 47"*, and the IDWarp branch that fires at the undeformed baseline behaves differently just above its threshold.

**`G19-2e` TOOLCHAIN (§6).** Per row: container image digest **and** the `.so` md5, both as **printed by the run** and as read from the **artefact**, matching §8's table. Any mismatch → **`GATE FAIL`** on that row. Toolchain identity is an image ID and a library hash, never a version string.

**`G19-2f` CAPS (rule 12).** Every arm within its §3 cap; item within **280.0 core-min**. An overrun **stops the run**; it does not get a new budget.

**`G19-2g` TRIVIAL BASELINES.** §6 below.

**`G19-2h` TRAVELLING PROVENANCE.** §9 below.

### 5.2 Composition

**Phase 1 failing → the item closes at phase 1**, its verdict is phase 1's, phase 2 launches nothing, and the record says so in those words.

**Phase 2 row verdict** = `PASS` only if `G19-2a`, `G19-2b` (`Optimal Solution Found.`), `G19-2c`, `G19-2d`, `G19-2e` and `G19-2g` all pass. Cap-stopped with `G19-2c` met → `GATE REACHED`. Cap-stopped without → `NOT A RESULT`.

**Item verdict** = the worse of the two rows. **Both rows are always reported and a patched row never replaces a shipped row** (`DAFOAM_CHARTER.md` §6).

---

## 6. THE TRIVIAL BASELINES, REGISTERED BEFORE THEIR OWN RUNS

`VERIFICATION_CHARTER.md` §2c and `DAFOAM_CHARTER.md` §4. §4 fixes the judgement for a DAFoam FD gate so no registration re-derives it: *"that baseline is the same probe at a step chosen to be wrong — an order of magnitude off the registered one. If the wrong step also passes, the gate is not measuring what it claims and the verdict it produced is withdrawn."*

**`TB-1` — the FD gate's trivial baseline.** The endpoint probe at **`s*÷10`**, already computed as part of `G19-2d`'s three-step sweep. **Registered prediction (P8):** the wrong step's aggregate is **≥ 5×** the aggregate at `s*`. **Consequence if it is not:** `G19-2d` is not discriminating on step placement and **the endpoint FD verdict is WITHDRAWN** — not softened, withdrawn, per §4's own sentence. The 5× threshold is calibrated on a measurement, not chosen: at D15's baseline the same one-decade move degrades the `PATCHED` `CD` aggregate from **0.0474 % to 0.5087 %**, a factor of **10.7**.

**`TB-2` — the optimisation gate's trivial baseline.** The **untouched trimmed start** scored by the same improvement reader that produces `G19-2c`. **Registered prediction (P9): exactly `0.000 %`.** **Consequence if not:** the improvement reader is measuring something other than the design change and **`G19-2c` is WITHDRAWN**.

**A control that does not FIRE is reported `NOT EXERCISED`**, never as a pass (`DAFOAM_CHARTER.md` §18.5's form).

---

## 7. THE REGISTERED PREDICTIONS — falsifiable, and frozen before any compute

| # | prediction | what a MISS means |
|---|---|---|
| **P1** | **`shape[7]` on `PATCHED` `CD` gains a TWO-SIDED plateau at 1e-2 once 3e-2 is measured: `\|FD(3e-2) − FD(1e-2)\|/\|FD(1e-2)\| ≤ 10.0 %` on all five components and both functions, so the selector picks `s* = 1e-2` (`shape`) / `1e-1` (`patchV`).** | **`G19-1b` `GATE FAIL`; phase 2 launches nothing.** The finding is then that **no step in §7's sanctioned range brackets D15's smallest `CD` component**, which is a real result about the ground and is reported as one. |
| **P2** | **The cancellation mechanism: `\|FD(1e-5) − FD(1e-2)\|/\|FD(1e-2)\|` for `shape[7]` on `CD` exceeds 21.63 %** — the deviation keeps growing as the step shrinks. | Cancellation is **refuted**; the 1e-4 excursion is something else and is named as undiagnosed. **This alone does not stop phase 2 if P1 hit** — P1 is the gate, P2 is the explanation. |
| **P3** | `G19-1a` holds: shared steps to ≤ 0.5 %, adjoint to ≤ 0.1 %. | Phase 1 `NOT A RESULT`; the instrument is not D15's. |
| **P4** | `G19-1d` holds: np = 1 and np = 2 agree at `s*` to ≤ 2.0 %. | A4's decomposition defect reaches this ground. Phase 2 does not launch. *(A4 measured 16,600× between two decompositions of one mesh, so this can genuinely miss.)* |
| **P5** | `O-P` prints `EXIT: Optimal Solution Found.` within 40 majors. | The `PATCHED` row is `GATE REACHED` or `NOT A RESULT` per §5.2, and the cell is filled with a cap-stopped result, labelled as one. |
| **P6** | `PATCHED` drag reduction in **[3, 35] %** at `\|CL_f − 0.5\| ≤ 5.0e-3`. | Reported as measured. Weak by construction — see §5's `G19-2c` note. |
| **P7** | **THE DISCRIMINATING ONE. The `SHIPPED` row does NOT reproduce the `PATCHED` design: `‖x_S − x_P‖/‖x_P‖ > 5 %` on the 8 `shape` DVs, OR the `SHIPPED` endpoint FD `GATE FAIL`s.** Basis: the shipped adjoint misses FD by **44.8738 %** on `shape[6]`, which carries **76.414 %** of the `CD` gradient norm. | **A MISS IS THE FINDING, not a disappointment** — it would mean the rotation defect does not reach a 2-D shape problem at its optimum, exactly as D8R's P2/P4 MISS meant it did not reach a twist-only problem. Reported in those words, **never averaged**. |
| **P8** | `TB-1`: the wrong-step aggregate ≥ 5× the aggregate at `s*`. | `G19-2d`'s verdict is **withdrawn** (§6). |
| **P9** | `TB-2`: the untouched trimmed start reads exactly `0.000 %`. | `G19-2c` is **withdrawn** (§6). |
| **P10** | Cost: phase 1 in **[4, 140]**, phase 2 in **[15, 140]**, item **≤ 280** core-min. | Reported as an overrun and attributed, per §10; the run **stops**, it does not get a new budget. |

**Predicted outcome, stated so it can be wrong.** P1, P2, P3, P4, P5, P7, P8, P9, P10 HIT and P6 HIT → `PATCHED` row **`PASS`**, `SHIPPED` row **`GATE FAIL`** on `G19-2d`, **item `GATE FAIL`**, with the `PATCHED` row's `PASS` carried into the grid's *"optimization converged"* column for **2-D · steady · subsonic-compressible** as *"1 converged to tolerance (patched), endpoint FD-verified; shipped gradient fails the FD gate on this ground"* → **`CAN DO, CAVEATS`**.

---

## 8. TOOLCHAIN IDENTITY (§6) — an image ID and a library hash, never a version string

| row | container image digest | `libidwarp.so` md5 |
|---|---|---|
| `SHIPPED` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |
| `PATCHED` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |

Source: `d15_grade.py:82-85`, and the `PATCHED` `.so` md5 is corroborated independently in D15's own frozen `F-P/d15_F.json` `identity.libidwarp_so_md5`. Each is checked **as printed by the run** and **as read from the artefact** (`G19-2e`).

---

## 9. THE TRAVELLING PROVENANCE, IN CODE (`G19-2h`)

`SO3b_STUB.md` §3 states the condition on which a patched-row result may be built: *"legitimate only with the SHIPPED `GATE FAIL` travelling attached to every downstream claim, in code (the `curriculum_SO1bR/so1br_precondition.py` `require_travelling_provenance()` form)."* **D19 takes that route and registers it as a gate.**

`d19_precondition.py` pins D15's graded output **by absolute path and by md5** — never by glob, which is the defect that closed SO-1b at `rc = 7` on 2026-08-28:

- path: `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/D15_grade_20260827T114315Z.json`
- asserts `rows.SHIPPED == "GATE FAIL"` and `rows.PATCHED == "PASS"` and `verdict == "GATE FAIL"`
- asserts `gates.G5_SHIPPED.G5_CD.aggregate_rel_err_pct > 5.0` (measured 34.680703) and `gates.G5_PATCHED.G5_CD.aggregate_rel_err_pct <= 5.0` (measured 0.047405)
- **refuses to emit ANY D19 verdict** if it cannot read them, and the md5 is captured into the record

**Every D19 verdict string carries the suffix** — frozen wording: *"on the PATCHED toolchain; the SHIPPED toolchain FAILS the gradient gate on this exact ground (D15 shipped worst 44.8738 % on `shape[6]`, aggregate 34.6807 %)"*. **A D19 number quoted without it is quoted wrongly.**

---

## 10. COST (rule 12; `DAFOAM_CHARTER.md` §12)

| | predicted (core-min) | cap (core-min) |
|---|---|---|
| phase 1 | **8.7** | **140.0** |
| phase 2 | **36.8** | **140.0** |
| **item** | **45.5** | **280.0** |

**Basis, measured not guessed.** D15's own frozen ledger (`D15_grade_20260827T114315Z.json`, `gates.G10_caps.per_arm`): `MESH` 0.167, `X-S` 1.367, `F-S` 3.433, `X-P` 1.733, `F-P` 3.400 core-min, item total **10.100**. From it: **≈ 0.113 core-min per perturbed primal** at np = 2 (3.433 over 30 primals), **≈ 1.7 core-min** for a cold primal plus both adjoints. Phase 1's `S2` is 50 perturbed primals → 5.7. Phase 2's optimiser is priced at **1.2 core-min per major** (a warm-started primal plus two adjoint solves) × 12 expected majors × 2 rows → 28.8, and the caps price the full 40-major budget on both rows.

**Dollars are DERIVED, NOT MEASURED.** At the owner-stated **c7a.4xlarge $0.0513/core-h**: predicted **$0.039**, cap **$0.239**. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so no figure here is a measurement. Both are far under the $25 pre-authorisation, and the item is costed regardless because a blanket is not a per-item read (rule 9).

**Stop rule.** An arm exceeding its cap **stops**. The item exceeding 280.0 core-min **stops** and closes on what it has, labelled by what was actually reached. Waste is named separately and never absorbed into the ratio (`COMPUTE_BUDGET_CHARTER.md` §6). **At completion the estimate-versus-actual comparison is computed and appended as a row to `docs/COST_CALIBRATION.md`** — the ratio actual/predicted, with the gap attributed to contention, waste or misprediction. **A completion report without that comparison is incomplete** (rule 12, Sanaa's 2026-08-23 directive).

---

## 11. WHAT THIS ITEM DECLARES IT DOES NOT DO

**No Roache triple, and rule 5 is UNREACHABLE rather than waived.** Single mesh, 4,032 cells, no grid family, **no GCI is quoted anywhere in this item**, and no claim is made about the continuum. Registered pre-compute per `VERIFICATION_CHARTER.md` §2f.

**No forward-AD or complex-step reference, and §2 requires saying why.** Both images ship `libDASolverADF.so`, a forward-AD build (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a), so a non-FD reference **is** reachable on this box and this item does **not** reach for it. The reason is scope: D19 exists to close the optimisation column of a capability cell, and a forward-AD verification is a different instrument on a different rung. **It is named here so the omission is on the face of the document.** It would settle the undiagnosed mechanism of `D15_D16_FD_STEP_TABLE.md` §1.2 outright, because it has no step at all, and it is the strongest single follow-on this ground admits.

**No dot-product / duality check.** D15 and D16 both recorded `G6` as not measured; nothing here changes that.

**No edit to D15 or D16.** Both are frozen. A dated addendum at the foot of either `RESULTS.md` is the `dafoam-supervisor`'s call.

**No edit to `docs/capability/dafoam_GRID.md`.** The staleness finding is reported in `D15_D16_FD_STEP_TABLE.md` §4; correcting the grid is the supervisor's call, and this item does not depend on the stale half.

---

## 12. THE MULTIPOINT HALF OF SANAA'S DIRECTIVE — WHERE IT IS, AND WHY IT IS NOT HERE

Sanaa's 2026-08-31 directive has two halves and D19 answers only the first. The second — *"we need to find a solution for multipoint optmization (both compresisble and incompressible"* — is carried by `SO3_MULTIPOINT_SCOPE_MEMO.md` (incompressible scope) and `SO3b_STUB.md` (compressible, gated). **D19 neither answers it, advances it, nor changes its gate**, and §0 is the tripwire that keeps this document from being read as though it did.

---

## 13. INSTRUMENT TABLE (§18.3) — every file this item EXECUTES or IMPORTS

Existence is asserted by `test -e` **before** any md5 is taken, inside the asserting invocation, under a planted control confirming the reader can return non-ABSENT.

| file | role | status at freeze |
|---|---|---|
| `cases/dafoam/ladder-a/A1/curriculum_D19/d19_step_table.py` | phase-0 precondition reader (this record's companion) | **PRESENT**, committed with this document |
| `cases/dafoam/ladder-a/A1/curriculum_D19/d19_chain_driver.sh` | arm sequencing and the phase-2 branch | **ABSENT — to be written and committed BEFORE any launch** |
| `cases/dafoam/ladder-a/A1/curriculum_D19/d19_runScript.py` | the solver/optimiser producer | **ABSENT — to be written and committed BEFORE any launch** |
| `cases/dafoam/ladder-a/A1/curriculum_D19/d19_select_step.py` | the §5.1 selector, adjoint-blind by assertion | **ABSENT — to be written and committed BEFORE any launch** |
| `cases/dafoam/ladder-a/A1/curriculum_D19/d19_precondition.py` | the §9 travelling-provenance guard | **ABSENT — to be written and committed BEFORE any launch** |
| `cases/dafoam/ladder-a/A1/curriculum_D19/d19_grade.py` | the grading path, frozen at its own commit before compute | **ABSENT — to be written and committed BEFORE any launch** |
| `cases/dafoam/ladder-a/A1/curriculum_D15/d15_runScript.py` | the configuration this item inherits | **PRESENT** |
| `cases/dafoam/ladder-a/A1/curriculum_D15/d15_decomposeParDict` | the np = 2 decomposition | **PRESENT** |

**The five ABSENT files are gates on the launch, not omissions from the freeze.** This document freezes the **gates, thresholds, bands, caps, labels, predictions and costs**, which is rule 2's entire subject. The grading path must itself be frozen at its own commit before compute, and hashed against the committed blob at grading time, per rule 2's third clause.

**Run root, registered and asserted ABSENT at freeze:** `/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt`. It does not exist at the time of this freeze, which is the condition rule 2 requires a pre-compute amendment to be able to state, and it is stated here.

---

## 14. STATUS

**`PENDING`.** Frozen, **not enqueued**, no run root, **zero solver core-minutes spent**. Launching is the `dafoam-supervisor`'s call and requires the five §13 files committed first.
