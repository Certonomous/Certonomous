# CURRICULUM D19O — RESULTS. **`GATE REACHED`**, both rows, seven arms of seven, 16.184 core-min

**Item verdict: `GATE REACHED`.** Both rows `GATE REACHED`. **Both rows composed raw `PASS` and were capped by the registered ceiling** — `capped_by_ceiling_anywhere: true`, `rows_capped_by_ceiling: ["SHIPPED", "PATCHED"]`.

| | |
|---|---|
| grading path | `d19o_grade.py`, md5 `c55a0151dc8eab4740ee1169cb9202ae` (== the §A1.5 pin, == the driver's `MD5_GRADER`) |
| freeze | `bb0c5b08279ce9c9d7f2e3520ea17d1f64707552`; arming `239fd2ef7e906969ae9030e5c2e62258044826ab` |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation` |
| grade artefact | `D19O_grade_20260901T054304Z.json` |
| chain | `chain_rc=0`, `declared=7 executed=7`, driver pid 1297444, 05:19:31Z → 05:43:04Z |
| **cost, MEASURED** | **16.184 core-min** against **24.10** predicted (ratio **0.6715**) and a **145.0** ceiling. **$0.013837 DERIVED, NOT MEASURED** |

**THE CEILING IS THE HEADLINE.** Every gate passed. Both optimisers printed `Optimal Solution Found.` Both endpoint FD tables passed band D and band E. **And the item still cannot publish `PASS`**, because the compressible gradient it spends has no graded verdict and its plateau never closed. That is `d19o_grade.py:_apply_ceiling()` doing exactly the work it was registered to do, and it is the reason this item is reportable at all.

---

## 1. THE SEVEN ARMS

| arm | row | rc | wall s | core-min | predicted | ratio | cap |
|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 10 | 0.167 | 0.20 | 0.835 | 5.0 |
| `O-S` | SHIPPED | 0 | 324 | 5.400 | 7.57 | 0.713 | 40.0 |
| `XE-S` | SHIPPED | 0 | 51 | 0.850 | 1.40 | 0.607 | 10.0 |
| `FE-S` | SHIPPED | 0 | 141 | 2.350 | 2.98 | 0.789 | 20.0 |
| `O-P` | PATCHED | 0 | 253 | 4.217 | 7.57 | 0.557 | 40.0 |
| `XE-P` | PATCHED | 0 | 51 | 0.850 | 1.40 | 0.607 | 10.0 |
| `FE-P` | PATCHED | 0 | 141 | 2.350 | 2.98 | 0.789 | 20.0 |
| **item** | | | | **16.184** | **24.10** | **0.6715** | **145.0** |

**No arm crossed its cap; the item did not approach its ceiling.** `delivered_cores_mean` 0.9926 on `O-S`, so the box was not starving any arm. `MemAvailable` never moved below 27.80 GiB against a registered 16.0 floor.

**All gates:** `G-STAGES`, `G-M2` (4032), `G-NP`, `G9`, `G12` (cpuset 11), `G10`, `G-DESIGNPOINT`, `G-NOOPT-ENDPOINT`, `G-EVALFAIL` (42 declared, 0 failed, both FE arms) — **`PASS`**. `GCI_roache` **`NOT APPLICABLE`** (no grid triple). `G6` **`NOT MEASURED`**. `G-PLAT7` **`NOT A RESULT`**, both rows, as registered.

**The birth register: 8 readers, 8 born, 0 not born, every one against a `REAL` target on this run root.** Five of the eight pass a gate on a zero. The live control fired inside the real `FE` arms: `D19O_PLANTED_CONTROL_SEEN zero=0.0 K=5.0 moved=25.0000 pp CROSSES | K_shrunk=0.5 moved=2.5000 pp DOES NOT CROSS (band 5.0 pp)`.

---

## 2. THE OPTIMISATION — BOTH ROWS CONVERGED, TO THE SAME OPTIMUM

| row | CD baseline (trimmed) | CD final | reduction | CL final | IPOPT | rows / iters |
|---|---|---|---|---|---|---|
| SHIPPED | 0.01632675460978398 | 0.01279162168845058 | **21.6524 %** | 0.49999946 | `Optimal Solution Found.` | 13 / 12 |
| PATCHED | 0.01632675460978398 | 0.01279200193…  | **21.6501 %** | 0.50000232 | `Optimal Solution Found.` | 10 / 9 |

**The `CL` pair travels with every drag number**, as registered: both optima sit on `CL = 0.5` to better than 3e-6. The stall detector's condition A did not fire on either row.

**The design change, and it is physically coherent.** α goes 4.0° → trimmed → **0.795°** at the optimum, with positive camber on all eight `shape` components. A cambered section reaches `CL = 0.5` at far lower incidence, and lower incidence is where the drag went.

> **`DAFOAM_CHARTER.md` §9 forbids grading an optimisation by the size of its improvement, and 21.65 % grades nothing here.** It is an input to the registered intermediate threshold (≥ 2.0 % over ≥ 5 majors) and to nothing else. The verdict comes from the optimiser's own printed statement, and then from the ceiling.

---

## 3. THE ENDPOINT FD — AND THE FINDING THIS ITEM WAS BOUGHT FOR

`DAFOAM_CHARTER.md` §9 requires the FD check **at the final design point**. Every compressible FD table this lab held before today — D15's, D19's, D19R's — was measured at iteration 0. These are the first at an optimum.

| row | aggregate `CD` (excl. flagged, 4 components) | aggregate `CL` | `G5_fd` | `G-TB` |
|---|---|---|---|---|
| SHIPPED | **0.042993 %** | 0.017651 % | `PASS` | `PASS` (0 of 4 pass at `h=1e-8`) |
| PATCHED | **0.052679 %** | 0.016953 % | `PASS` | `PASS` (0 of 4 pass at `h=1e-8`) |

### 3.1 **`shape[7]`'s NEAR-NULLITY IS A PROPERTY OF THE BASELINE, NOT OF THE COMPONENT**

| | baseline (D19R) | SHIPPED optimum | PATCHED optimum |
|---|---|---|---|
| `\|dCD/dshape[7]\|` | **2.099480e−04** | **5.887300e−03** | **5.824352e−03** |
| plateau two-sided at s\* | **false** (fine side 21.0607 %) | **true** (c 0.974 % / f 1.061 %) | **true** |
| adjoint vs FD at s\* | 1.65155 % | **0.1682 %** | **0.1244 %** |

**It grew by a factor of 28.** At the undeformed baseline `shape[7]` carried 0.3351 % of ‖dCD/dshape‖ and its FD numerator sat close enough to the primal noise floor that the fine side of the decade bracket could not close. At a cambered design point it carries real sensitivity, its numerator is far above the noise, **and its plateau closes on both rows.**

**THE REGISTERED NON-RESULT HELD, AND THAT IS THE POINT.** `G-PLAT7` returns **`NOT A RESULT`** on both rows, set from the registered list and never from the measured value — exactly as frozen, and exactly as the comparator's `B3` selftest leg demanded on a planted row that passed everything. **This lane does not get to promote a component after seeing a good number.** What the measurement licenses is a *successor* registration, not a retroactive one.

### 3.2 **THE SHIPPED AND PATCHED ROWS ARE INDISTINGUISHABLE AT THE ENDPOINT — AND D15 SAYS THEY ARE NOT AT THE BASELINE**

D15 measured, on this exact ground at the baseline: the **SHIPPED** adjoint misses FD by **44.8738 %** on `shape[6]`, where **PATCHED** misses by **0.0072 %**, and `shape[6]` carries **76.414 %** of the `CD` gradient's norm.

**At the endpoint, `shape[6]` on the SHIPPED row agrees to 0.0232 %.**

**The mechanism is the one `DAFOAM_CHARTER.md` §9 already names.** The IDWarp `getRotationMatrix3d` degenerate-rotation branch fires when `axisMag = 1e-15 < tol = sqrt(eps)` — which is **certain at every non-corner surface node of an undeformed mesh**. At a deformed design point the surface nodes have moved, `axisMag` is no longer ~0, **the degenerate branch does not fire, and the shipped adjoint is correct.**

> **THE FINDING: on this ground the IDWarp defect is a BASELINE-ONLY defect.** It is not that the patch is unnecessary — it is that the configuration where the patch matters is the one every previous FD table on this ground was measured in. **An item that verified a gradient only at iteration 0 was verifying it in the single configuration where the defect is guaranteed to be present.**

**HOW FAR THIS MAY BE TAKEN, STATED AT ITS TRUE SIZE.** One case, one Mach number, one optimum per row, `np = 1`, four graded components, and **the two rows converged to nearly the same design** — so the endpoint they were each evaluated at is nearly the same point, which is a weaker test of the difference than two distant optima would have been. It does **not** show the defect absent elsewhere, and a shipped-versus-patched divergence of 0.000 % on any component is reported with its number and never read as absence.

### 3.3 **BOTH AGGREGATES SIT FAR BELOW THE HARNESS FLOOR, AND THAT IS A CLAIM ABOUT THE HARNESS**

`VERIFICATION_CHARTER.md` §7 step 4: the harness-sound floor on this stack is **2.5–5 % vector-norm relative error**, and *"a number below that is a claim about the harness."*

**0.042993 % is ~58× below the floor's lower edge; 0.052679 % is ~47× below it.** **REPORTED, NEVER GATED**, as registered in §4 of the pre-registration.

**Corroboration that this ground routinely sits there:** D19R's own `S1` arm, np = 1, at the **baseline**, on the PATCHED row, gives an aggregate of **0.055341 %** over the same five components — computed at this item's freeze from `.../S1/d19r_S1.json` against `.../X2/d19r_X.json`. So sub-0.1 % is this case's normal reading at np = 1 and is not an artefact of the endpoint. The charter's own note applies: that floor is calibrated on shape derivatives through IDWarp on a different instrument mix, and this record states which instrument it is on rather than claiming a sub-percent verification.

---

## 4. PREDICTIONS — SCORED, AND **THREE WERE WRONG**

| token | registered | measured | |
|---|---|---|---|
| `P1_cells_4032` | HIT | `G-M2` `PASS`, 4032 | **HIT** |
| `P2_shipped_optimiser_converges` | HIT | `Optimal Solution Found.` | **HIT** |
| `P3_patched_optimiser_converges` | HIT | `Optimal Solution Found.` | **HIT** |
| `P4_majors_in_band` | HIT | 13 and 10, both in [8, 20] | **HIT** |
| `P5_shipped_row_worse_than_patched` | HIT | 21.6524 % vs 21.6501 % — shipped is **not** worse | **MISS** |
| `P6_patched_endpoint_fd_PASS` | **MISS** | `PASS`, aggregate 0.0527 % ≤ 5.0 % | **the registered prediction was WRONG** |
| `P7_shipped_endpoint_fd_GATE_FAIL` | HIT | `PASS` | **MISS** |
| `P8_trivial_baseline_PASS_both_rows` | HIT | `PASS`/`PASS`, 0 of 4 passing | **HIT** |
| `P9_shape7_NOT_A_RESULT` | HIT BY CONSTRUCTION | `NOT A RESULT` both rows | **HIT, and it carries no information** |
| `P10_item_GATE_REACHED` | HIT | `GATE REACHED` | **HIT** |
| `P_COST_total_core_min_in_band` | HIT | 16.184 ∈ [15.0, 65.0] | **HIT** |

**THE THREE FAILURES ARE ONE FAILURE.** `P5`, `P6` and `P7` all predicted that the shipped and patched rows would differ — in the optimum reached, and in endpoint gradient quality. **They do not differ.** Every one of those predictions was reasoned from D15's **baseline** measurement, and §3.2 is why that reasoning does not reach the endpoint.

**`P7` is the same shape as SO-3's `P6` miss, which this document's §13.1 explicitly warned about** — *"it may miss the same way"* — and it did. Registering the warning did not make the prediction right; it made the miss legible.

**`P9` is a HIT that carries no information**, exactly as §13.2 registered: it scores a gate this document *registers* as `NOT A RESULT`. It confirms the comparator was not edited and nothing else.

---

## 5. COST CALIBRATION (`CLAUDE.md` rule 12)

**16.184 core-min actual against 24.10 predicted, ratio 0.6715.** Attribution: **misprediction, not contention** — `delivered_cores_mean` ≥ 0.9926 on the sampled arms. **Waste: none.** No arm crossed a cap; no arm was re-run; nothing was discarded.

**THE ONE TERM THAT WAS WRONG, AND IT IS THE ONE `R5` NAMED IN ADVANCE.**

| | value |
|---|---|
| registered rate | **0.63122** core-min/major `[EXTRAPOLATED]` = 0.3924 `[MEASURED]` × 1.6086 `[MEASURED]` |
| **measured, `O-S`** | 5.400 / 13 = **0.4154** core-min/major |
| **measured, `O-P`** | 4.217 / 10 = **0.4217** core-min/major |
| **compressible penalty ON A MAJOR** | **0.4154 / 0.3924 = 1.059×** |
| registered penalty, from the PRIMAL | 1.6086× |

**R5 stated the risk in exactly these words: *"the ratio is measured on the primal and carried onto a major that is primal + 2 adjoints + mesh warp."* The answer is that it does not transfer.** A compressible *primal* costs 1.61× its incompressible twin on this mesh; a compressible *major* costs **1.06×**, because the major is dominated by the two adjoint solves and the mesh warp, whose cost is far less sensitive to the extra density and energy states.

**FORWARD RULE FOR THIS FAMILY:** a compressible **optimiser major** on A1 at np = 1 prices at **≈ 0.42 core-min/major** — measured twice, on two rows, agreeing to 1.5 %. A primal-derived penalty must not be carried onto a major without saying so, and this row is the measurement that removes the need to.

The non-optimiser arms came in at 0.607–0.835 of prediction — the same 0.59–0.88 band SO-3's non-optimiser arms landed in, so that part of the model is stable.

---

## 6. WHAT THIS ITEM DOES **NOT** ESTABLISH

* **It does not establish that the compressible adjoint is verified.** The gradient it spends still has **no graded verdict**: D19R's grader refused `rc=2` and D19R2's grading attempt 1 returned `NOT A RESULT`. **That is unchanged by this run**, and it is why the ceiling exists.
* **It does not establish a `PASS` on anything.** Both rows were capped from raw `PASS`.
* **It does not establish that `shape[7]`'s gradient is verified.** §3.1 measures that its plateau closes *at the optimum*; `G-PLAT7` remains `NOT A RESULT` and this item registers no verdict on that component.
* **It does not establish a sub-percent verification.** §3.3 — both aggregates are claims about the harness.
* **It does not establish anything at np ≠ 1**, on a transonic ground, or on a grid triple.
* **It does not retire the IDWarp patch.** §3.2's limit.

---

## 7. WHAT THIS ITEM RETIRES, AND WHAT IT OPENS

**RETIRED — `R3`, the largest named residual.** `d19o_xf.py` mode `O` had never been executed in any form; it built the pyOptSparse driver itself and its writers were exercised only through fixtures. **It worked on its first execution, on both rows, producing converged optima and a well-formed `d19o_xopt.json` that both endpoint arms consumed.** `R2` (the producer unexecutable on the host) is retired with it.

**OPEN, AND THE STRONGEST FOLLOW-ON THIS GROUND ADMITS — unchanged from D19R §11 and this item's §3.4:** a **forward-AD or complex-step reference**. Both images ship `libDASolverADF.so`, so it is reachable on this box. **It would settle `shape[7]` outright, because it has no step at all and therefore no plateau to close** — and §3.1 now gives it a second, sharper target: the component's behaviour differs by a factor of 28 between the baseline and the optimum, so a non-FD reference at *both* points would separate "the defect" from "the configuration" definitively. **Neither D19R nor D19O reached for it, and both say so on their own face.**

**A SECOND ITEM THIS RUN JUSTIFIES.** §3.2's finding — that the IDWarp defect is baseline-only on this ground — is measured on two optima that turned out to be nearly the same point. A successor that evaluates the shipped adjoint at a **deliberately displaced** design point, away from both optima, would test it where this item could not.

---

## 8. A DEFECT IN THIS ITEM'S OWN DRIVER, FOUND BY RUNNING IT — `D19O-DRIVER-DEF-1`

**`d19o_chain_driver.sh` writes its pre-launch selftest output into the GIT WORKING TREE, not into the run root.** The line is `$t > "$HERE/$(echo "$t" | md5sum | cut -c1-8).selftest.out"`, and `$HERE` is the case directory. This run left four untracked files — `0a9cae03`, `23f0429f`, `24506d42`, `87185266`.`selftest.out` — sitting beside the frozen instruments.

**Size, stated honestly: small, and not zero.** It changes no verdict, breaks no pin (the driver is not self-pinned and the files it writes are not inputs to anything), and costs nothing. What it costs is **cleanliness of the shared tree** — four untracked files per launch in a directory whose whole point is that its contents are frozen and enumerated — and it is exactly the class `gitignored is not filed` warns about, arriving from the other direction: files that *are* visible to git and simply should not be there.

**NOT REPAIRED HERE, AND THE REASON IS THE FREEZE.** The driver is pinned at `d732fea8…` in §7 row 1 and the item has had first compute, so editing it now would break the pin and alter a frozen instrument after the fact. **The files are left untracked and unswept** — deleting them would remove the only on-disk evidence that the four suites were driven before staging. **The repair belongs to a successor's driver**, where the target should be `$BASE/` and not `$HERE/`.

---

**SUBMISSIONS PARKED.** Nothing in this item is filed, sent, uploaded, registered, posted or commented outside this box (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).
