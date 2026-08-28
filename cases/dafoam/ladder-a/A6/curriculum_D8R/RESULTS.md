# Curriculum D8R — A6 CRM wing-alone, N=16, twist-only constrained drag minimisation **TO CONVERGENCE**, on **TWO TOOLCHAIN ROWS**, each with an **ENDPOINT FD table** — RESULTS

**Graded and closed 2026-08-28 by the DAFoam team's D8R lane R, zero compute in this record.**
Grades against `PREREGISTRATION.md`, frozen at commit `357a2648` (2026-08-26T22:45Z) **before the run root existed**, with `ADDENDUM 1` (pre-compute, `c933740d`, 22:52Z). This file does not revise that document; departures and readings land here.

**Nothing in this item is filed, sent, uploaded, posted, registered or pushed anywhere. SUBMISSIONS ARE PARKED and sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Artefacts every number below is read from** (run root `/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv`):
`D8R_grade_20260828T021329Z.json` / `.out` (the frozen grading path's own output), `ledger.txt`, `STATUS.chain`, `STATUS.O-P` / `STATUS.F-P` / `STATUS.O-S` / `STATUS.F-S`, the four arm logs named in the ledger rows, and `grader_controls/F_S_planted.json` / `F_P_planted.json`.

---

## 0. THE VERDICT

**ITEM VERDICT: `PASS`.** Two rows, per `DAFOAM_CHARTER.md` §6 — *"Every DAFoam verdict is recorded as two rows … a patched row never replaces a shipped row"*:

| row | verdict | image digest (identity, not a version string) | IDWarp `.so` md5 | arms |
|---|---|---|---|---|
| **SHIPPED** | **`PASS`** | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` | `O-S`, `F-S` |
| **PATCHED** | **`PASS`** | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | `O-P`, `F-P` |

**G9 toolchain identity, `PASS` on all four arms: `printed_so_md5 == artefact_so_md5` on every arm** — `O-P` and `F-P` both `85f59e87…`, `O-S` and `F-S` both `f0fcb488…`, each beside its row's digest (`D8R_grade_20260828T021329Z.json`, `gates.G9_toolchain.per_arm`, `verdict: PASS`). The two `.so` md5s are distinct, so the two rows are not the same toolchain wearing two labels. **No version string is quoted anywhere in this record**, per §6 of the charter.

Gate roll-up, all from the frozen grader's own output: `G1_completion` `PASS`, `G-M2_mesh_identity` `PASS` (all four arms `points_md5` `11b84f0de5fdf2d3e947fee8cea412a9`), `G-BASE` `PASS`, `G9` `PASS`, `G10` `PASS`, `G12` `PASS`; per row `G-O_terminus`, `G2_CL`, `G3_drop`, `G-BASE_cold_CD`, `G5_CD`, `G5c_CL` all `PASS`.

### 0.1 THE SCIENTIFIC FINDING — a registered MISS, reported as registered and not generalised

**`PREREGISTRATION.md:92`, verbatim, written before any container started:**

> **Predicted outcome:** P1, P3, P5, P6, P7 HIT; P2, P4 HIT → PATCHED `PASS`, SHIPPED `GATE REACHED` on G-O and `GATE FAIL` on G5 → **item `GATE FAIL`** with the PATCHED row's `PASS` carried into the grid's optimisation column as *"1 converged to tolerance (patched), endpoint FD-verified; shipped cap-stopped"* → `CAN DO, CAVEATS`. **MISS on P2 and P4** (the shipped row converges and its endpoint FD passes) would be the finding that the rotation defect does not reach this twist-only problem — reported as such, never averaged.

**P2 MISSED and P4 MISSED.** The SHIPPED row did not stop at `max_iter`: it printed `EXIT: Optimal Solution Found.` at 12 majors, and its endpoint FD passed **10 of 10** graded components (5 on `CD`, 5 on `CL`) with zero sign flips. **THE FINDING, in the words the registration fixed for it: the rotation defect does not reach this twist-only problem.**

**What that does NOT say, stated because the registration required it be reported and never averaged:** it is a statement about *this* problem — A6 CRM wing-alone, N = 16, `twist`-only, this mesh (`points_md5` `11b84f0de5fdf2d3e947fee8cea412a9`), this registered 5-component subset, at these two endpoints. It is **not** a statement about other DV types (`shape` is not graded and is `PENDING` for the family), other cases, other meshes, or the defect class in general. The A1 SHIPPED baseline's `GATE FAIL` at 11.4274 % with a sign flip on `idx6` stands on record and is not touched by this row.

---

## 1. THE BRIGHT LINE — THE FD TABLE IS THE RESULT

`VERIFICATION_CHARTER.md`'s bright line and `DAFOAM_CHARTER.md`'s: the adjoint gradient is not a result until a finite-difference table sits beside it. **Four tables, two rows × two objectives, 20 graded components in total, 20 `PASS`, 0 `GATE FAIL`, 0 `NOT A RESULT`, 0 sign flips.**

The gate arithmetic, read from the frozen grader (`d8r_grade.py`, md5 `3f6eafac2ad4897417521d00c1cc5f3e`): **band D = 5.0 % per component** (`FD_BAND_PCT`, `:101`), **band E = 5.0 % on the vector-relative aggregate** (`AGG_BAND_PCT`, `:102`), **`d_ref` is the MIDDLE of the three registered steps** (h = 0.1; `:37` *"reference is the MIDDLE step of the registered three"*), and **the plateau rule is `min(plateau_neighbour_pct) > 10.0 → NOT A RESULT / NO_PLATEAU`** (`PLATEAU_TOL_PCT`, `:103`; `:392-394`). Registered steps `[3.0e-2, 1.0e-1, 3.0e-1]` (`STEPS_REGISTERED`, `:107`); registered components `twist` `{0, 1, 3, 4, 5}` (`COMPONENTS_REGISTERED`, `:106`).

**The plateau proof is printed beside every number below — it is not asserted anywhere in this file.** Worst plateau reading across all 20 rows: `min(neighbour) = 2.2739 %` (SHIPPED `CD` `twist` idx5), a **4.40× clearance** on the 10 % tolerance; best `0.0039 %` (PATCHED `CL` `twist` idx5).


**Aggregate readings, all four tables:**

| row | objective | components | `PASS` | `GATE FAIL` | `NOT A RESULT` | sign flips | aggregate rel err % (band E 5.0) | gate |
|---|---|---|---|---|---|---|---|---|
| SHIPPED | `CD` (`G5_CD`) | 5 | 5 | 0 | 0 | 0 | **0.6458** | `PASS` |
| SHIPPED | `CL` (`G5c_CL`) | 5 | 5 | 0 | 0 | 0 | **0.0884** | `PASS` |
| PATCHED | `CD` (`G5_CD`) | 5 | 5 | 0 | 0 | 0 | **0.9015** | `PASS` |
| PATCHED | `CL` (`G5c_CL`) | 5 | 5 | 0 | 0 | 0 | **0.1068** | `PASS` |

**Worst single component in the item: PATCHED `CD` `twist` idx5 at `3.9170 %`, inside band D's 5.0 % with a 1.28× margin.** It is the only component above 2 % anywhere in the four tables, and it is on the smallest-magnitude `CD` derivative graded (`J_adj = -5.484e-04`), where the same absolute FD noise buys the largest relative error. Named, not smoothed: the registered point for P3 read *"worst ≤ 3 %"* and the measured worst is **3.9170 %**, so the prediction's point was exceeded even though P3's scored condition (`PASS` 5 of 5) HIT — see §12.


### The four tables

**SHIPPED · dCD/d(twist) — 5 of 5 `PASS`, 0 sign flips, aggregate rel err 0.6458 %, band D `PASS`, band E `PASS`, gate `PASS`.**

| DV | idx | `J_adj` | FD @ h=0.3 | FD @ h=0.1 | FD @ h=0.03 | `d_ref` (h=0.1) | plateau neighbour % (0.3 vs 0.1, 0.1 vs 0.03) | rel err % | sign flip | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `twist` | 0 | `-2.305369e-03` | `-2.312098e-03` | `-2.318377e-03` | `-2.197569e-03` | `-2.318377e-03` | 0.2708 / 5.2109 | **0.5611** | false | `PASS` |
| `twist` | 1 | `-1.961888e-03` | `-1.965961e-03` | `-1.961808e-03` | `-2.033608e-03` | `-1.961808e-03` | 0.2117 / 3.6599 | **0.0041** | false | `PASS` |
| `twist` | 3 | `-1.283982e-03` | `-1.285843e-03` | `-1.301121e-03` | `-1.266406e-03` | `-1.301121e-03` | 1.1743 / 2.6681 | **1.3173** | false | `PASS` |
| `twist` | 4 | `-8.585179e-04` | `-8.529111e-04` | `-8.603001e-04` | `-9.057449e-04` | `-8.603001e-04` | 0.8589 / 5.2824 | **0.2072** | false | `PASS` |
| `twist` | 5 | `-5.483031e-04` | `-5.549638e-04` | `-5.426249e-04` | `-5.620856e-04` | `-5.426249e-04` | 2.2739 / 3.5864 | **1.0464** | false | `PASS` |

**SHIPPED · dCL/d(twist) — 5 of 5 `PASS`, 0 sign flips, aggregate rel err 0.0884 %, band D `PASS`, band E `PASS`, gate `PASS`.**

| DV | idx | `J_adj` | FD @ h=0.3 | FD @ h=0.1 | FD @ h=0.03 | `d_ref` (h=0.1) | plateau neighbour % (0.3 vs 0.1, 0.1 vs 0.03) | rel err % | sign flip | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `twist` | 0 | `-2.395605e-02` | `-2.394759e-02` | `-2.395831e-02` | `-2.402202e-02` | `-2.395831e-02` | 0.0447 / 0.2659 | **0.0094** | false | `PASS` |
| `twist` | 1 | `-2.035596e-02` | `-2.036168e-02` | `-2.035971e-02` | `-2.036404e-02` | `-2.035971e-02` | 0.0097 / 0.0213 | **0.0184** | false | `PASS` |
| `twist` | 3 | `-1.334916e-02` | `-1.335014e-02` | `-1.334350e-02` | `-1.338597e-02` | `-1.334350e-02` | 0.0498 / 0.3183 | **0.0425** | false | `PASS` |
| `twist` | 4 | `-8.913534e-03` | `-8.913078e-03` | `-8.894889e-03` | `-8.908409e-03` | `-8.894889e-03` | 0.2045 / 0.1520 | **0.2096** | false | `PASS` |
| `twist` | 5 | `-5.688258e-03` | `-5.684398e-03` | `-5.712757e-03` | `-5.609707e-03` | `-5.712757e-03` | 0.4964 / 1.8039 | **0.4289** | false | `PASS` |

**PATCHED · dCD/d(twist) — 5 of 5 `PASS`, 0 sign flips, aggregate rel err 0.9015 %, band D `PASS`, band E `PASS`, gate `PASS`.**

| DV | idx | `J_adj` | FD @ h=0.3 | FD @ h=0.1 | FD @ h=0.03 | `d_ref` (h=0.1) | plateau neighbour % (0.3 vs 0.1, 0.1 vs 0.03) | rel err % | sign flip | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `twist` | 0 | `-2.304798e-03` | `-2.317010e-03` | `-2.311654e-03` | `-2.154617e-03` | `-2.311654e-03` | 0.2317 / 6.7933 | **0.2966** | false | `PASS` |
| `twist` | 1 | `-1.961904e-03` | `-1.959292e-03` | `-1.952088e-03` | `-1.984551e-03` | `-1.952088e-03` | 0.3690 / 1.6630 | **0.5029** | false | `PASS` |
| `twist` | 3 | `-1.284497e-03` | `-1.289938e-03` | `-1.304092e-03` | `-1.241294e-03` | `-1.304092e-03` | 1.0854 / 4.8155 | **1.5026** | false | `PASS` |
| `twist` | 4 | `-8.589860e-04` | `-8.520055e-04` | `-8.558515e-04` | `-9.224283e-04` | `-8.558515e-04` | 0.4494 / 7.7790 | **0.3662** | false | `PASS` |
| `twist` | 5 | `-5.484132e-04` | `-5.484773e-04` | `-5.277415e-04` | `-5.230701e-04` | `-5.277415e-04` | 3.9292 / 0.8852 | **3.9170** | false | `PASS` |

**PATCHED · dCL/d(twist) — 5 of 5 `PASS`, 0 sign flips, aggregate rel err 0.1068 %, band D `PASS`, band E `PASS`, gate `PASS`.**

| DV | idx | `J_adj` | FD @ h=0.3 | FD @ h=0.1 | FD @ h=0.03 | `d_ref` (h=0.1) | plateau neighbour % (0.3 vs 0.1, 0.1 vs 0.03) | rel err % | sign flip | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `twist` | 0 | `-2.395475e-02` | `-2.394982e-02` | `-2.395155e-02` | `-2.403758e-02` | `-2.395155e-02` | 0.0072 / 0.3592 | **0.0133** | false | `PASS` |
| `twist` | 1 | `-2.035833e-02` | `-2.036603e-02` | `-2.037908e-02` | `-2.037728e-02` | `-2.037908e-02` | 0.0641 / 0.0089 | **0.1018** | false | `PASS` |
| `twist` | 3 | `-1.335314e-02` | `-1.335196e-02` | `-1.332909e-02` | `-1.340013e-02` | `-1.332909e-02` | 0.1716 / 0.5330 | **0.1804** | false | `PASS` |
| `twist` | 4 | `-8.913134e-03` | `-8.910164e-03` | `-8.899913e-03` | `-8.889490e-03` | `-8.899913e-03` | 0.1152 / 0.1171 | **0.1486** | false | `PASS` |
| `twist` | 5 | `-5.689182e-03` | `-5.680783e-03` | `-5.705471e-03` | `-5.705250e-03` | `-5.705471e-03` | 0.4327 / 0.0039 | **0.2855** | false | `PASS` |

---

## 2. G-O TERMINUS — BOTH ROWS STOPPED ON THE OPTIMISER'S OWN STATEMENT

| row | arm | `EXIT` line | majors (`n_iter`) | `max_iter` | gate |
|---|---|---|---|---|---|
| SHIPPED | `O-S` | **`EXIT: Optimal Solution Found.`** | **12** | 30 | `PASS` |
| PATCHED | `O-P` | **`EXIT: Optimal Solution Found.`** | **8** | 30 | `PASS` |

Read twice, independently of each other: from the frozen grader's output (`D8R_grade_20260828T021329Z.json`, `gates.SHIPPED.G-O_terminus.exit_line` and `gates.PATCHED.G-O_terminus.exit_line`), and directly from the two named arm logs — `O-P_20260827T223101Z_1595223.log` and `O-S_20260828T000818Z_1676866.log`, each carrying `EXIT: Optimal Solution Found.` and the driver's own `D8R_IPOPT_TERMINUS '…' n_iter=8` / `n_iter=12` stamp.

**This is the first item in the D8 family to converge on the optimiser's own statement rather than stop at a cap.** D8 itself stopped at its registered 3-major cap (`EXIT: Maximum Number of Iterations Exceeded.`, `GATE REACHED`, `curriculum_D8/RESULTS.md`); D7R arm O stopped at 30 majors on `max_iter` and was `NOT A RESULT`. Neither row here reached its budget: 8 and 12 of 30.

---

## 3. G3 DRAG REDUCTION — A MARGINAL `PASS`, AND IT IS NOT HEADLINED AS A GAIN

| row | `CD_start` | `CD_final` | reduction % | registered band | gate |
|---|---|---|---|---|---|
| SHIPPED | `0.038756491279745384` | `0.03863923943624545` | **0.3025 %** | [0.29 %, 5.0 %] | `PASS` |
| PATCHED | `0.038756491279745384` | `0.0386386731443733` | **0.3040 %** | [0.29 %, 5.0 %] | `PASS` |

**STATED PLAINLY: both rows sit 4–5 % above the band's LOWER edge** (0.3025 / 0.29 = 1.0432; 0.3040 / 0.29 = 1.0483) **and nowhere near its interior.** The band's lower edge was not chosen for this item: it is **D8's own measured 3-major drop, 0.2871 %** (`PREREGISTRATION.md:49`, deriving it from `PREREGISTRATION.md:17`'s reading of D8's trajectory — trimmed start `0.03877565033718443` → major 3 `0.03866430994135252`). So the gate asks only *"did running to convergence beat D8's first three majors at all?"*, and the answer is **yes, by 5.4 % of that figure and no more** (0.3025 / 0.2871 = 1.0536; 0.3040 / 0.2871 = 1.0588).

**This is a marginal `PASS` on the improvement gate.** The registered *point* for P5 was **1.0 %**; the measured drop is roughly three-tenths of that. Twenty-nine additional majors beyond D8's three bought about 0.017 percentage points of drag. **The headline of this item is the FD table and the P2/P4 MISS (§0.1), not this number**, and no figure in this record calls 0.30 % a large gain.

---

## 4. ATTRIBUTION BEFORE THE PERCENTAGE — Sanaa's D7R rule, discharged structurally

Sanaa's standing directive of 2026-08-27 (§4): **no improvement percentage is quoted before its mechanism is decomposed.** Here the decomposition is **structural** — it is read off the frozen problem statement, not fitted after the fact — and it is stated as such.

The design vector and the constraint set, read from `d8r_runScript.py` (md5 `28c7819487a025a5f6554d38062a2b66`, byte-identical worktree and HEAD blob; a byte copy of D8's own frozen producer output):

* **`self.add_objective("scenario1.aero_post.CD", scaler=1.0)`** (`:199`) — drag alone is minimised.
* **`self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)`** (`:195`) — spanwise twist, the only *shape-side* design variable. **The local FFD `shape` DV is NOT added** (`:159`, D8 EDIT 3, twist-only).
* **`self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)`** (`:196`) — `patchV` is `[U0, aoa]`. **Its first entry has `lower == upper == U0`, so freestream speed is pinned: there is no operating-point channel.** Its second entry, angle of attack, is free in [0, 10] deg — **one free scalar.**
* **`self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)`** (`:200`) — an **equality** trim on lift. One equality constraint against the one free `patchV` scalar: **the AoA channel is consumed by the trim and has no freedom left to reduce drag.**
* **`self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0)`** and **`("geometry.volcon", lower=1.0)`** (`:201-202`) — thickness and volume are bounded, so the optimiser cannot buy drag by thinning or shrinking the wing.

**The trim held, measured:** `G2_CL` `CL_final` **`0.4999951170634741`** (SHIPPED, abs dev `4.883e-06`) and **`0.5000010836883954`** (PATCHED, abs dev `1.084e-06`) against target `0.5`, tolerance `5.0e-3` — both `PASS`, both three orders inside tolerance.

**Therefore the 0.30 % is attributable to spanwise twist redistribution at fixed lift, fixed freestream speed, and bounded thickness and volume.** No AoA trade, no operating-point trade, and no thickness/volume trade was available to it. That is the whole mechanism; there is no residual channel this record has to guess at.

**One limit on the decomposition, named:** `patchV`'s endpoint gradient is **not in the registered FD subset** and is therefore **NOT MEASURED** here (`PREREGISTRATION.md:113`). The adjoint computes it (`d8r_runScript.py:323`, `compute_totals(of=…, wrt=["twist", "patchV"])`); nothing in this item verifies it.

---

## 5. SHIPPED vs PATCHED AT THE ENDPOINT — A READING, NOT A GATE

The two rows converged to **different endpoints** (8 majors versus 12), so this comparison is not a same-point toolchain test and **no gate is attached to it**. The grader labels every row of it `"different endpoints; a reading"`.

| DV | idx | `J_adj` SHIPPED | `J_adj` PATCHED | divergence % |
|---|---|---|---|---|
| `twist` | 0 | `-2.305369e-03` | `-2.304798e-03` | 0.0248 |
| `twist` | 1 | `-1.961888e-03` | `-1.961904e-03` | **0.0008** |
| `twist` | 3 | `-1.283982e-03` | `-1.284497e-03` | 0.0401 |
| `twist` | 4 | `-8.585179e-04` | `-8.589860e-04` | **0.0545** |
| `twist` | 5 | `-5.483031e-04` | `-5.484132e-04` | 0.0201 |

Range **0.0008 % to 0.0545 %** across the five components. **It is recorded as a reading and nothing is concluded from it about toolchain equivalence** — that would require the two rows at the same design point, which this item did not buy.

---

## 6. PLANTED-ZERO CONTROL — standing rule 3, on both rows, at two levels

**A zero from a reader not shown able to see a non-zero is not evidence.** Two independent controls fired, both read from `D8R_grade_20260828T021329Z.json`, `controls`:

**(i) The instrument's own CTRL component**, computed inside each F arm by the same code path that computes every graded derivative: `instrument_ctrl_zero = 0.0` and `instrument_ctrl_planted = 0.00617` on **both** rows (`controls.S`, `controls.P`), against `want = 0.00617`. The want is **derived, not a magic constant**: `PLANT / (2.0 * CTRL_STEP)` = `1.234e-03 / 0.2` (`d8r_grade.py:332`, `PLANT` at `:110`, `CTRL_STEP` at `:109`) — the central-difference of a known planted perturbation. If the planted row does not come back at that value the grader **refuses** (`:334`).

**(ii) The grader-level plant, and what it actually does** (`d8r_grade.py:338-362`, docstring at `:339-341`): the grader **writes a COPY of each F table on disk with `PLANT = 1.234e-03` added to every physical `dCD`**, then **re-reads that copy back through the real `read_F` path** — not a mock — and **refuses unless every value moved by exactly `PLANT`**. Result on both rows: `grader_plant_seen: true`, **`n_values: 15`** each (5 components × 3 steps), **`worst_residual: 0.0`**. The two copies are on disk and named in the record: `grader_controls/F_S_planted.json` and `grader_controls/F_P_planted.json`.

**So every `0` and every "no sign flip" in §1 comes from a reader demonstrated, on this run's own data and through this run's own code path, to see a non-zero.**

---

## 7. ARM COMPLETION — G1, all four arms

| arm | row | rc | `OOMKilled` | source | wall s | ranks | artefact |
|---|---|---|---|---|---|---|---|
| `O-P` | PATCHED | 0 | false | `docker inspect ExitCode` via ledger row | 4,753 | 4 | `d8r_O.json` |
| `F-P` | PATCHED | 0 | false | same | 954 | 4 | `d8r_F.json` |
| `O-S` | SHIPPED | 0 | false | same | 6,442 | 4 | `d8r_O.json` |
| `F-S` | SHIPPED | 0 | false | same | 1,004 | 4 | `d8r_F.json` |

`STATUS.chain`: `arm=O-P rc=0 20260827T235015Z`, `arm=F-P rc=0 20260828T000713Z`, `arm=O-S rc=0 20260828T015541Z`, `arm=F-S rc=0 20260828T021329Z`, then **`chain=COMPLETE 20260828T021329Z`** and `grader_rc=0`. The chain's own note is carried forward unchanged: **`note=comparator-exit-status-NOT-the-verdict`** — `grader_rc=0` says the comparator ran, never that the item passed; the verdict is the `PASS` in §0, which is the comparator's *output*, not its exit status.

`G1_completion` `PASS`, `not_measured` empty. **`G-M2_mesh_identity` `PASS`:** all four arms report `points_md5` `11b84f0de5fdf2d3e947fee8cea412a9`, equal to the `points_md5` the driver staged at `STAGED stamp=20260827T222956Z` in `ledger.txt` — the same mesh under both toolchains.

---

## 8. PLACEMENT AND MEMORY — the registered exposure DID NOT FIRE

`G12_placement` `PASS`, cpuset `0,1,12,15` on all four arms as registered, `not_measured` empty.

**The H5 memory exposure the previous session named did not fire on any arm.** Read from the four `STATUS.<arm>` files:

| arm | `h5_min_GiB` | registered floor | `aggregate_waited_s` | `cpuset_waited_s` |
|---|---|---|---|---|
| `O-P` | **24.55** | 18.0 (O arms) | 0 | 0 |
| `F-P` | **27.49** | 10.0 (F arms) | 0 | 0 |
| `O-S` | **27.81** | 18.0 | 0 | 0 |
| `F-S` | **28.0** | 10.0 | 0 | 0 |

Every reading is far above even the higher O-arm floor; the tightest, `O-P` at 24.55 GiB, clears 18.0 by 6.55 GiB. No arm waited on the aggregate guard and no arm waited on the cpuset guard: the H5 stop condition was **never reached**.

**Consequence for `D8R-GRADER-DEF-1`, and it is not discharged.** The previous session's finding — that the H5 **stop verdict is unregistered**, so a run halted by the memory guard would have had no registered outcome to grade into — **remains a live registration defect for the successor.** It was not exercised here; a defect that is never reached is not a defect that is fixed. It stands as **UNEXERCISED**, carried forward, and this item's `PASS` is not evidence about it either way.

---

## 9. THE RUN SURVIVED THE FLEET KILL

**The whole agent fleet died at approximately 2026-08-27T23:15Z on the account's weekly usage limit** (established by the dafoam supervisor). At that moment `O-P` was still running — it finished at **23:50:15Z**, 35 minutes later.

**`F-P`, `O-S` and `F-S` all ran, and the frozen grader ran, with no agent alive.** From `STATUS.chain`: `F-P` completed 2026-08-28T00:07:13Z, `O-S` 01:55:41Z, `F-S` 02:13:29Z, `chain=COMPLETE` 02:13:29Z, `grader_rc=0` 02:13:29Z — **just under three hours of compute and the entire grading pass, after the last agent was gone.** They were carried by the **detached OS-daemon chain driver, `pid=1587601`** (`STATUS.chain` line 1; the same pid is stamped in all four `STATUS.<arm>` preflight lines as `driver_pid=1587601`).

**That is Sanaa's detached-queue-runner ruling of 2026-08-26 working exactly as designed** — queues run as OS daemons independent of agents, and idle compute is the failure. It is named here because it is the first time in this family that the ruling has been *tested by the thing it was written for*: the fleet died mid-item and the item still completed and graded on its frozen path. Nothing was re-launched by hand, and nothing needed to be.

---

## 10. COST — MEASURED FROM THE LEDGER, AND CALIBRATED

`G10_caps` `PASS`. Every figure below is read from `ledger.txt`'s four `ARM=` rows; the totals and per-arm ratios are the frozen grader's own (`gates.G10_caps`).

| arm | core-min (measured) | own cap | crossed? | registered point | ratio actual/predicted |
|---|---|---|---|---|---|
| `O-P` | **316.867** | 1,000.0 | no | 458.0 | **0.6918** |
| `F-P` | **63.600** | 120.0 | no | 61.0 | **1.0426** |
| `O-S` | **429.467** | 1,000.0 | no | 458.0 | **0.9377** |
| `F-S` | **66.933** | 120.0 | no | 61.0 | **1.0973** |
| **total** | **876.867** | **ceiling 2,240.0** | no | **1,038.0** (`PREREGISTRATION.md:66`) | **0.8447** |

**Total 876.867 core-min against a 2,240.0 ceiling — 39.1 % of it. No arm crossed its own cap.**

**WASTE: 0.000 core-min — and that is defended, not asserted bare.** Two arms have walls above the 3,600-second stall heuristic (`COMPUTE_BUDGET_CHARTER.md` §2): `O-P` at **4,753 s** and `O-S` at **6,442 s**. The heuristic is addressed rather than passed over. The cgroup sampler measured `delivered_cores_mean` of **3.9501** (`O-P`, n = 312), **3.9843** (`F-P`, n = 62), **3.9969** (`O-S`, n = 425) and **3.9826** (`F-S`, n = 65) **of the 4 ranks requested** — 98.8 % to 99.9 % of the cpuset, with `siblings_pre` and `siblings_post` empty on every arm. **The long arms were computing, not stalled**; a stall is a wall with no delivered cores behind it, and these walls have very nearly four cores behind every second of them. There is nothing to clean, so gross equals cleaned, and **no compute is named as waste under `COMPUTE_BUDGET_CHARTER.md` §6.**

**Calibration (`CLAUDE.md` rule 12).** Predicted **1,038.0** core-min point, band **[500, 1,800]**, ceiling **2,240.0** (`PREREGISTRATION.md:66`); actual **876.867** core-min MEASURED from `ledger.txt`; **ratio 0.8447 — 15.5 % UNDER the point, inside the band.** Dollars **DERIVED, NOT MEASURED**: 876.867 core-min = 14.6145 core-h × $0.0513/core-h = **$0.7497**, against the registered point **$0.8875** (`PREREGISTRATION.md:68`). **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Attribution of the gap, specifically:** the whole under-run is in the **O arms**, and it is a **major-count** effect, not a rate effect. The registration priced each O arm at 20 majors (P7's point; band [8, 30]); the optimiser converged in **8** (`O-P`) and **12** (`O-S`). `O-P` at 8 majors came in at 0.6918 of its point and `O-S` at 12 majors at 0.9377. The **F arms went slightly OVER** — 1.0426 and 1.0973 — so the primal-count model for the FD arms is a little optimistic and is the part of the estimate that wants revisiting, not the O-arm rate. The calibration row is `C-191` in `docs/COST_CALIBRATION.md`.

---

## 11. NOT MEASURED, NAMED

* **`G6` dot-product / duality test: NOT MEASURED.** The grader records it in its own words — *"the tutorial exposes no dot-product/duality test; named, never composed"* (`D8R_grade_20260828T021329Z.json`, `gates.G6_dot_product_duality`). It is named here so this record cannot be read as implying it.
* **No GCI is quoted anywhere in this item, and standing rule 5 has no row here.** The grader states the reason: **`"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"`** (`no_gci` field). One mesh, one level; there is no Roache triple to gate and none is implied.
* **`patchV`'s endpoint gradient** — computed by the adjoint, not in the registered FD subset, not verified (§4).
* **The four `twist` components outside the registered subset** — the FD subset is `twist` `{0, 1, 3, 4, 5}`, five of the nine `twist` components on record (D8's endpoint FD graded 8 of 9; `PREREGISTRATION.md:14`, `:37`). Nothing here measures the rest, and **`twist` idx6 remains `NOT A RESULT` from D8 and is not repaired.**
* **`G1`, `G10` and `G12` each report an EMPTY `not_measured` list** — no field was absent and silently skipped in any of them.

---

## 12. PREDICTIONS — scored by the frozen comparator, never adjusted

| # | prediction (`PREREGISTRATION.md` §6) | scored | the measurement |
|---|---|---|---|
| **P1** | PATCHED prints `EXIT: Optimal Solution Found.` within budget | **HIT** | 8 majors of 30 |
| **P2** | SHIPPED terminates on `Maximum Number of Iterations Exceeded.` at 30 majors | **MISS** | `Optimal Solution Found.` at 12 majors |
| **P3** | PATCHED endpoint FD `PASS` 5 of 5 (point: worst ≤ 3 %) | **HIT** | 5 of 5 `PASS`; **worst 3.9170 %, above the registered point of 3 %, inside band D's 5.0 %** |
| **P4** | SHIPPED endpoint FD `GATE FAIL` — ≥ 1 of 5 outside band D or sign-flipped | **MISS** | 5 of 5 `PASS` on `CD`, 5 of 5 on `CL`, zero flips |
| **P5** | PATCHED drag reduction in [0.29 %, 5.0 %] (point 1.0 %) | **HIT** | 0.3040 %, inside the band and 4.8 % above its lower edge; **well below the point** |
| **P6** | total graded core-min in [500, 1,800] (point 1,038) | **HIT** | 876.867 |
| **P7** | PATCHED majors in [8, 30] (point 20) | **HIT** | 8 — **at the band's lower edge exactly** |

**Five HIT, two MISS, and the two MISSes are the item's finding (§0.1), reported as the registration required and never averaged with the HITs.** Three of the five HITs are noted above as landing at or outside their registered *points* while satisfying their scored conditions — P3's worst component, P5's magnitude, P7's major count. That is recorded so the HIT column is not read as five clean confirmations.

---

## 13. SCOPE — WHAT THIS ITEM DOES NOT ESTABLISH, AND THE ONE CLAUSE THAT NOW RELEASES

`PREREGISTRATION.md` **§8** ("WHAT THIS ITEM WILL NOT ESTABLISH", `:113`) is carried here **by citation, unchanged**: D8 §12 verbatim — **no A6 N=29, no 399,360-cell A3, no D16a; `twist` idx6 not repaired; `shape` not graded and `PENDING` for the family; A6 overall `BLOCKED`, unchanged** — plus nothing about the optimum's uniqueness (one start per row; D13's basin finding stands), nothing about `patchV`'s endpoint gradient, no GCI, and nothing about np = 1 ↔ np = 4 primal agreement beyond `G-BASE`'s 10 η band.

**ONE CLAUSE OF §8 NOW RELEASES, and only one: *"nothing toolchain-independent unless **both** rows PASS".* Both rows PASSED, so it releases.**

**Precisely what that licenses:** a toolchain-independent reading of the endpoint gradient **on this problem, on this mesh, on these design variables** — A6 CRM wing-alone at N = 16, `points_md5` `11b84f0de5fdf2d3e947fee8cea412a9`, `twist`-only with the `shape` FFD DV absent, at the registered 5-component subset, on both objectives. On that footing, and on that footing alone, the FD tables of §1 may be cited without naming a toolchain row.

**What it does not license, stated so the release cannot spread:** it is not toolchain-independence at another mesh, another N, another case, another DV type, or another design point. The two rows converged to **different endpoints** (§5), so even here the independence claim is *"each toolchain, at its own converged endpoint, reproduces its own adjoint under FD"* — **not** *"the two toolchains agree at a common point"*, which this item did not buy and does not assert. Every other §8 limit stands untouched.

---

## 14. WHAT REMAINS OPEN

| item | state |
|---|---|
| `D8R-GRADER-DEF-1` — the H5 stop verdict is unregistered | **UNEXERCISED registration defect**, carried to the successor (§8) |
| `twist` idx6 | `NOT A RESULT` from D8; not repaired |
| `shape` DVs on A6 | `PENDING` for the family |
| A6 at N = 29, A3 at 399,360 cells | `BLOCKED` on memory/conditioning, unchanged |
| `G6` dot-product / duality | NOT MEASURED anywhere in the family |
| Common-point SHIPPED/PATCHED comparison | not bought by this item |
