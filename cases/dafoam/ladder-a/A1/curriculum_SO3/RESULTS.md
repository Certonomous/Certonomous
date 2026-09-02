# CURRICULUM SO-3 — RESULTS. **`PASS`**, both rows, seven arms of seven, 28.900 core-min

**Item verdict: `PASS`.** Rows **`SHIPPED` `PASS`** and **`PATCHED` `PASS`** — two rows, shipped beside patched, never one in place of the other (`docs/dafoam/README.md` §3 rule R11; `DAFOAM_CHARTER.md` §6). Read from the grade artefact's own fields: `verdict: "PASS"`, `rows: {"PATCHED": "PASS", "SHIPPED": "PASS"}`, and the comparator's own `.out` line `VERDICT PASS  rows={'SHIPPED': 'PASS', 'PATCHED': 'PASS'}  declared=7 executed=7`.

| | |
|---|---|
| item | **SO-3** — NACA0012 **incompressible α-multipoint shape optimisation**, ladder A1, 4,032 cells, np = 1 on every arm |
| objective | `J = Σᵢ wᵢ·CDᵢ(αᵢ)`, three operating points **α = 3.13918623195176 / 5.13918623195176 / 7.13918623195176 deg**, equal weights ⅓, one shared `shape` vector; graded DV subset `shape[0, 3, 6, 7]` |
| grading path | `so3_grade.py`, md5 **`0ac111ef144a62111e36f676e8114af1`** (Amendment 2 §A2.3; the original §7/§10 pin `d786e10d…` is **STRUCK**) |
| freeze | `7f7d0fb1`, through **Amendment 1** `b229f0e2` and **Amendment 2** `573aae08` / `ab27dff7` — all three before first compute (chain stamp `20260901T033048Z`) |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation` |
| grade artefact | `SO3_grade_20260901T040709Z.json` (+ `.out`, + `SO3_STOP_MARKER.json`) |
| chain | `STATUS.chain` — `chain=COMPLETE declared=7 executed=7 stamp=20260901T040709Z`, all seven arms `rc=0`, `grader_rc=0` |
| **cost, MEASURED** | **28.900 core-min** against **228.59** registered (ratio **0.126×**), ceiling 595.0. **\$0.02471 DERIVED, NOT MEASURED** |

**THE CAVEAT IS THE HEADLINE AND IT TRAVELS IN EVERY CELL BELOW.** `CL` is **UNCONSTRAINED** in this item by registration (pre-registration line 6), and **it collapsed**: the three-point lift went from **[0.31190, 0.49877, 0.66398]** to **[−0.05737, 0.15241, 0.36012]** (SHIPPED) and **[−0.05676, 0.15320, 0.36119]** (PATCHED) — **negative at point 0 on both rows.** The grade artefact's own `forbidden_readings`, verbatim, at `gates.G-OPT9_optimisation_per_row.{SHIPPED,PATCHED}.forbidden_readings` (identical on both rows):

> * "grading this row from the SIZE of its improvement"
> * "using the word `converged` of a run whose optimiser printed no convergence statement"
> * **"quoting the weighted-drag reduction without CL_baseline and CL_final beside it, because CL is UNCONSTRAINED in this item"**
> * "upgrading GATE REACHED to PASS because the endpoint FD passed -- the endpoint FD validates the DESIGN, not the optimiser's convergence"

**So no drag-reduction figure appears anywhere in this document without the lift triple in the same cell or the same sentence.** A reader who takes one cell away from this record must not take away a false statement.

---

## 1. THE SEVEN ARMS

| arm | row | rc | wall s | ranks | core-min | predicted | ratio | cap |
|---|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 10 | 1 | 0.167 | 0.19 | 0.8789 | 5.0 |
| `O-S` | SHIPPED | 0 | 475 | 1 | 7.917 | 103.0 | 0.0769 | 240.0 |
| `XE-S` | SHIPPED | 0 | 141 | 1 | 2.350 | 3.7 | 0.6351 | 15.0 |
| `FE-S` | SHIPPED | 0 | 267 | 1 | 4.450 | 7.5 | 0.5933 | 40.0 |
| `O-P` | PATCHED | 0 | 417 | 1 | 6.950 | 103.0 | 0.0675 | 240.0 |
| `XE-P` | PATCHED | 0 | 152 | 1 | 2.533 | 3.7 | 0.6846 | 15.0 |
| `FE-P` | PATCHED | 0 | 272 | 1 | 4.533 | 7.5 | 0.6044 | 40.0 |
| **item** | | | | | **28.900** | **228.59** | **0.126** | **595.0 ceiling** |

Wall seconds and `core_min` are the run root's own `ledger.txt` `ARM=` rows; the per-arm `predicted` and `ratio_actual_over_predicted` columns are the grade artefact's `G10_caps.per_arm` fields, which price **against the prediction and never against the cap** (pre-registration §4.1). **Zero arms crossed a cap** (`crossed: false`, 7 of 7); the ceiling was used to 4.9 %. **No arm approaches the 3,600-wall-s stall rule** — the longest is `O-S` at 475 s — so gross and cleaned are the same 28.900 core-min.

**Gate readings, from `gates` in the grade artefact.** `G1_completion` **`PASS`**; `G-M2_mesh_identity` **`PASS`** (4,032 cells); `G-ALPHA_operating_points` **`PASS`** (all three α read back with `abs_deviation` **0.0** against a 1e-12 tolerance, on all four X and F artefacts); `G-STAGES_declared_vs_executed` **`PASS`** (declared 7, executed 7, short 0); `G-NOOPT-ENDPOINT` **`PASS`** (0 optimiser markers in the endpoint arms); `G-DESIGNPOINT` **`PASS`** (all four endpoint artefacts read `design_point: "FINAL"` from their own row's `so3_xopt.json`, sha256 `f8d48081…` SHIPPED / `ccc1bb80…` PATCHED); `G9_toolchain` **`PASS`** (7 of 7 arms, `ok: true`); `G10_caps` **`PASS`**; `G12_placement` **`PASS`** (cpuset `14` on every arm); `G5J` **`PASS`** both rows; `G-OPT9` **`PASS`** both rows. `G6_dot_product_duality` is **`NOT MEASURED`**. `G-EVALFAIL` is **REPORTED, never gated** — §6.3. `no_gci`: *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"*.

---

## 2. THE OPTIMISATION — BOTH ROWS PRINTED THEIR OWN CONVERGENCE STATEMENT, AND THE LIFT COLLAPSED

`α` is the **operating point**, not a design variable: `patchV` is removed by registration (pre-registration line 3 and line 6). **The consequence is that `CL` is UNCONSTRAINED — there is no DV to trim with — so the three-`CL` triple travels with every drag number this item publishes.**

| row | IPOPT exit statement | majors | `max_iter` | `J` baseline | `J` final | **weighted drag reduction, AND the lift triple it was bought with** |
|---|---|---|---|---|---|---|
| SHIPPED (`O-S`) | `Optimal Solution Found.` | **12** | 50 | 0.02180598162892116 | 0.018283153757420498 | **−16.155328072130235 %** — bought by driving `CL` from **[0.31190, 0.49877, 0.66398]** to **[−0.05737, 0.15241, 0.36012]**, i.e. the lift collapsing at all three points and going **NEGATIVE at point 0** |
| PATCHED (`O-P`) | `Optimal Solution Found.` | **10** | 50 | 0.02180598162892116 | 0.018283196351550565 | **−16.15513273980908 %** — bought by driving `CL` from **[0.31190, 0.49877, 0.66398]** to **[−0.05676, 0.15320, 0.36119]**, i.e. the lift collapsing at all three points and going **NEGATIVE at point 0** |

Neither row reached its iteration cap (`n_majors` 12 and 10 against `max_iter_registered` 50), so §9's `GATE REACHED` mapping does not bind; each row is eligible for `PASS` because **the optimiser printed its own convergence statement against its own tolerance** (`tol_registered` 1e-05), which is what the artefact's `why` field says in terms: *"the optimiser printed its own convergence statement against its own tolerance: 'Optimal Solution Found.'"*

### 2.1 THE DRAG TRIPLE AND THE LIFT TRIPLE, SIDE BY SIDE — NEITHER IS REPORTABLE WITHOUT THE OTHER

| | point0, α = 3.13919° | point1, α = 5.13919° | point2, α = 7.13919° |
|---|---|---|---|
| `CD` baseline | 0.01723938072177922 | 0.020910510045267394 | 0.027268054119716875 |
| `CD` final, SHIPPED | 0.016252837924302457 | 0.017470496645588345 | 0.02112612670237069 |
| `CD` final, PATCHED | 0.016254689517250072 | 0.017469887014380677 | 0.02112501252302095 |
| `CL` baseline | 0.31189588769251864 | 0.49876526085592926 | 0.6639763551107052 |
| **`CL` final, SHIPPED** | **−0.057373254725203056** | **0.15240511285598504** | **0.36011850787767585** |
| **`CL` final, PATCHED** | **−0.05675565457564216** | **0.15320276361213012** | **0.3611940124520788** |

**THE LIFT COLLAPSES AT ALL THREE POINTS AND GOES NEGATIVE AT point0, ON BOTH ROWS.** That is not a defect in the optimiser and not a surprise: with `CL` unconstrained and `α` fixed, the cheapest way to reduce `Σ wᵢ CDᵢ` is to shed lift. **A ~16 % weighted-drag reduction at unstated lift is not a reportable number**, and it is nowhere reported as one in this record.

> **`DAFOAM_CHARTER.md` §9 forbids grading an optimisation by the size of its improvement**, and the artefact's own `forbidden_readings` repeats it. The percentage grades nothing. It is an input to the registered intermediate threshold (**≥ 5.0 % weighted-drag reduction over at least 5 majors**, `intermediate_threshold_met: true` on both rows) and to nothing else; the verdict comes from IPOPT's own printed statement and then from the endpoint FD.

**The stall detector did not fire on either row.** Condition A (`alpha_pr < 1.0e-3` over 8 consecutive majors) `fired: false`, `longest_run: 0`, both rows; condition B `fired: false` and is registered **`NOT EXERCISED`**, never as a passing control (pre-registration §9.2). `cumulative_line_search_cutbacks: 0` and `n_restoration_majors: 0` on both rows. `inf_du` fell 0.0196 → 7.48e-06 (SHIPPED) and 0.0196 → 7.28e-06 (PATCHED).

---

## 3. THE ENDPOINT FD TABLE AT THE FINAL DESIGN POINT — THE THING THIS ITEM WAS BOUGHT FOR

`DAFOAM_CHARTER.md` §9 requires the FD check **at the final design point**, and its stated reason is this toolchain: *a gradient verified at iteration 0 is not verified at iteration 47.* SO-3aR2's `PASS` was measured **at iteration 0 only**. `XE-*` and `FE-*` are what close that gap, and `G-DESIGNPOINT` proves they ran at each row's own optimum rather than at the baseline.

### 3.1 `G5J` — THE MULTIPOINT OBJECTIVE `J`, PER ROW

Band D 5.0 % per graded pair, band E 5.0 % on the aggregate, plateau tolerance 10.0 % **proved per pair**, `MIN_GRADED_PAIRS = 3`. Steps `1e-2 / 1e-3 / 1e-4`.

| row | graded pairs | pairs `PASS` | **aggregate rel err** | **worst pair** | band D | band E | sign flips | `G5J` |
|---|---|---|---|---|---|---|---|---|
| SHIPPED (`FE-S`) | 4 of 4 | 4 | **0.08594454384641227 %** | **0.18905998172513677 %** | `PASS` | `PASS` | 0 | **`PASS`** |
| PATCHED (`FE-P`) | 4 of 4 | 4 | **0.06890419283803313 %** | **0.2533162674763216 %** | `PASS` | `PASS` | 0 | **`PASS`** |

Per component, `J` relative error at the registered step, PATCHED: `shape[0]` 0.14419582168200673 %, `shape[3]` 0.08493486887044153 %, `shape[6]` 0.040835009316585534 %, `shape[7]` 0.2533162674763216 % — **all four `PASS`**, `sign_flip: false` on every pair.

**BOTH AGGREGATES SIT BELOW THE HARNESS-SOUND FLOOR, AND THAT IS A CLAIM ABOUT THE HARNESS, NOT A TIGHTER VERIFICATION.** The artefact's own `G5J_harness_floor` block says so on its face, verbatim: *"BELOW_HARNESS_FLOOR -- a number below 2.5 % on this stack is a claim about the harness (VERIFICATION section 7 step 4), not a tighter verification"*, `gated: false`. SHIPPED sits **2.414055 percentage points below** the floor's lower edge, at **0.034378×** it; PATCHED **2.431096 pp below**, at **0.027562×**. **This record does not claim a sub-percent verification.**

### 3.2 `G5C` — THE THREE `CL` PER SCENARIO, SAME RULE

`PASS` on every scenario of both rows, 4 of 4 pairs graded in each, zero sign flips.

| row | | point0, α = 3.13919° | point1, α = 5.13919° | point2, α = 7.13919° |
|---|---|---|---|---|
| SHIPPED | aggregate / worst | 0.1264361369245315 % / **3.172626574275313 %** | 0.20152020295119621 % / 0.9939627664503884 % | 0.05037852099767912 % / 0.17968666750900497 % |
| PATCHED | aggregate / worst | 0.056441403675676884 % / 1.0427270736973857 % | 0.03728234282430093 % / 0.1453421294770778 % | 0.04464277589633514 % / 0.15999813431957963 % |

The single worst `CL` pair anywhere in the item is **3.1726 %** (SHIPPED, point0, `shape[7]`) against the 5.0 % band D — inside, and stated at its true size rather than behind the aggregate.

### 3.3 THE TRIVIAL-BASELINE CONTROL — THE FD INSTRUMENT IS SHOWN ABLE TO GO RED

`G-TB` re-runs the same probe at **`h = 1e-8`**, five orders below the registered middle step, where the FD numerator is at or below the primal repeatability. It **must** fail band D, and it does on every component of both rows:

| row | `shape[0]` | `shape[3]` | `shape[6]` | `shape[7]` | passing band D | `G-TB` |
|---|---|---|---|---|---|---|
| SHIPPED | **116.47208599020995 %** | **74.60703804333556 %** | **73.63292557568633 %** | **102.28403916026065 %** | **0 of 4** (max allowed 1) | **`PASS`** |
| PATCHED | **107.89395606977178 %** | **78.42964696536913 %** | **73.45007284187415 %** | **102.19809895426984 %** | **0 of 4** (max allowed 1) | **`PASS`** |

`g5j_verdict_at_the_registered_step: "PASS"` on both rows and `withdrawal_rule` did not fire. **A `PASS` on a band is worth what the instrument's demonstrated ability to `GATE FAIL` is worth**, and this is that demonstration, on the real arms. The measured primal repeatability on this run is `eta_F` **1.7455795364718085e-08** (SHIPPED) and **1.8966505671569323e-08** (PATCHED), against the 1.3e-10 reference the registration carried.

---

## 4. THE MULTIPOINT STRUCTURAL IDENTITY — `G-MP-STRUCT`

The one identity a multipoint item can violate silently: `∂J/∂x` must equal `Σᵢ wᵢ ∂CDᵢ/∂x`, component by component, from the artefact's own components. Tolerance `1e-10`.

| row | components checked | **worst relative residual** | `G-MP-STRUCT` |
|---|---|---|---|
| SHIPPED (`XE-S`) | 4 | **1.7571883834280927e-13** (`shape[3]`) | **`PASS`** |
| PATCHED (`XE-P`) | 4 | **8.864158539519277e-14** (`shape[7]`) | **`PASS`** |

`controls_precondition: "SATISFIED -- the planted control was seen in this run"`. `G-ALPHA` is the companion gate — a scenario silently wired to the wrong angle would let *every* band pass, because the FD table and the adjoint would both be taken at that same wrong angle. All three α read back at `abs_deviation` **0.0** on all four endpoint artefacts, weights ⅓ each. **`PASS`.**

---

## 5. SHIPPED-VERSUS-PATCHED DIVERGENCE — REPORTED WITH ITS NUMBER, NEVER GATED

`|dJ_SHIPPED − dJ_PATCHED| / max(|dJ_SHIPPED|, |dJ_PATCHED|) × 100` on the adjoint totals. The artefact's `status` field: **"REPORTED WITH ITS NUMBER, NEVER GATED"**, and its `note`: *"a divergence of 0.000 % on some component is REPORTED with its number and is never read as `the defect is absent`"*.

**Worst divergence: 24.172904251844518 %**, on `CD0` / `shape[3]` (`J_shipped` −0.00016988253864731186, `J_patched` −0.0001288169952394944). The next four: `CL0`/`shape[7]` **15.015034061182044 %**, `CD0`/`shape[0]` **7.262465485046317 %**, `J`/`shape[7]` **3.6678286979378374 %**, `CD2`/`shape[6]` **3.156573883169189 %**. On the graded objective `J` itself the worst is **3.6678 %** (`shape[7]`).

**Nothing more is claimed from these than that they are measured numbers.** The two rows converged to two *different* optima — their final `CD` and `CL` triples differ in the sixth and fourth decimal respectively (§2.1) — so each row's adjoint is evaluated at a different design point, and **a divergence measured across two different points cannot be separated into a toolchain term and a design-point term.** This item does not measure the IDWarp defect's reach and does not claim to.

---

## 6. CONTROLS AND INSTRUMENT INTEGRITY

### 6.1 THE BIRTH REGISTER — 8 READERS, **8 BORN, 0 NOT BORN**

Sanaa's 2026-08-28 requirement, carried verbatim in the artefact: *"no instrument grades anything until 'was this reader ever shown able to see a non-zero through the real code path?' is answered YES, demonstrated"*. `n_born: 8`, `n_not_born: 0`, `not_born: []`. The eight are `R1_read_ledger`, `R2_fatal_token_sites`, `R2b_read_primal_convergence`, `R3_read_mesh_cells`, `R4_read_X`, `R5_read_F`, `R6_read_multipoint_identity`, `R7_arm_datum` — each with the `U`-ids that bore it and the gate it feeds. **`R2`, `R4` and `R5` are readers whose zero would pass a gate**, which is the population `CLAUDE.md` rule 3 exists for.

### 6.2 THE PLANTED-ZERO CONTROLS FLIPPED, AND THEY WERE SIZED RELATIVE TO THE BAND

`PLANT_K = 3.0`, `plant_sizing: "RELATIVE -- PLANT_K*(band_D/100)*|d_ref|"`, giving a planted relative error of **15.000000000000002 %** against a 5.0 % band — clear of it by 3× by construction, at any quantity scale.

| control | reading |
|---|---|
| `grader_plant_X_SHIPPED` | `G5J` **`PASS` → `GATE FAIL`** under the plant; `G-MP-STRUCT` **`PASS` → `GATE FAIL`**; plant 0.0008596289137683019 written, **read back −0.004860395749571881** from −0.005720024663340183 |
| `grader_plant_X_PATCHED` | `G5J` **`PASS` → `GATE FAIL`**; `G-MP-STRUCT` **`PASS` → `GATE FAIL`**; plant 0.0008371714159496371, **read back −0.004752019131728713** |
| `grader_plant_F_{SHIPPED,PATCHED}` | 112 values each, `grader_plant_F_seen: true`, worst residual **1.7932703932910243e-16** |
| `grader_plant_cells` | on-disk 4,032, planted 4,039, **read back 4,039** |
| `instrument_ctrl_{SHIPPED,PATCHED}` | `both_directions: true`, 7 zero entries read per side (J + three `CD` + three `CL`), want 0.617, every one read back at 0.617 |

**The plants never touch a graded artefact.** Every one is written to a separate copy under `grader_controls/`, and the item's verdict is composed from the unplanted bytes alone.

### 6.3 `G-EVALFAIL` — THE EVALUATION CENSUS, AND THE PREDICTION IT FALSIFIED

| artefact | declared | succeeded | **failed** | failure fraction |
|---|---|---|---|---|
| `F:SHIPPED` | 34 | 34 | **0** | 0.0 |
| `F:PATCHED` | 34 | 34 | **0** | 0.0 |
| `X:SHIPPED` | 1 | 1 | **0** | 0.0 |
| `X:PATCHED` | 1 | 1 | **0** | 0.0 |

`status: "REPORTED -- a failed evaluation is a gradable state"`. **34 of 34 evaluations succeeded on both F arms and none failed**, so **`P8` reads `MISS` on both rows** — see §8, where the miss is reported as a miss and as a real finding rather than dressed up.

### 6.4 `G9_toolchain` — IDENTITY BY DIGEST AND HASH, NEVER BY VERSION STRING

SHIPPED `sha256:9d45679d…f07fc` / `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`; PATCHED `dafoam-idwarp-rot:v1` `sha256:2927768a…f6d35` / md5 `85f59e87253e0a71a813f64ca6e4c425`. `ok: true` on all seven arms, `printed_so_md5` matching `artefact_so_md5` wherever both exist. The producer computes the md5 of the `libidwarp.so` **the interpreter actually imported, from inside the container**, and maps it to a row; an md5 matching neither registered toolchain refuses.

### 6.5 WHAT WAS **NOT** MEASURED, NAMED RATHER THAN LEFT TO BE INFERRED

* **`G6_dot_product_duality`: `NOT MEASURED`**, verbatim from the artefact: *"AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on BOTH images; named, never composed."*
* **`GCI` / Roache triple: no row exists.** `no_gci`, verbatim: *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED."* Single-grid optimisation on A1's 4,032-cell mesh.
* **`G12_placement`'s delivered-cores floor: NOT COMPOSED at np = 1**, registered as not composed. The sampler's readings are published as numbers anyway: 0.9932 / 0.9978 / 0.9936 / 0.9925 / 0.9862 / 0.9957 delivered cores on the six solver arms. **`MESH` reads `NOT_MEASURED`** and is listed in the artefact's own `not_measured.G12` — it is the one arm with no sampler reading, and that absence is stated rather than filled.
* **Primal convergence: REPORTED, NEVER GATED.** `n_converged_statements` 102 per F arm against the real statement `Minimal residual <r> satisfied the prescribed tolerance <tol>`; the `SIMPLE: no convergence criteria found` banner is counted **separately** (12× per F arm) and **is not evidence** — a suppression a reader cannot see is the same defect wearing the other hat.

---

## 7. THE TRAVELLING SHIPPED `GATE FAIL` — `G-PROV`

This item's `PASS` **does not erase what it is built on**, and the chain travels with it in the artefact's `upstream_provenance` block. Its own `note`, verbatim: *"the SHIPPED GATE FAIL travels with every claim SO-3 makes; the ruling calls the incompressible ground `verified` and the record is narrower than that word"*.

| link | relation | item verdict | SHIPPED row | PATCHED row |
|---|---|---|---|---|
| `CURRICULUM-SO3aR2` | **DIRECT** — SO-3's optimisation is admissible only because SO-3aR2 FD-verified this objective's gradient at np = 1 | **`GATE FAIL`** | **`GATE FAIL`**, `G5J` aggregate **31.498325840045588 %**, 2 of 4 pairs `GATE FAIL` | `PASS`, `G5J` aggregate **2.6779490823450605 %** |
| `CURRICULUM-SO1a` | **INHERITED** — carried in SO-3aR2's own `upstream_provenance` | **`GATE FAIL`** | **`GATE FAIL`** on the FD band at a single point on this very case | `PASS` |

**On the SHIPPED toolchain the multipoint objective gradient missed the 5 % band by more than 6× on this very case.** That is what travels, and `so3_grade.py:G-PROV` refuses (exit 2) rather than publish a verdict if any link is absent, if any link's item verdict or SHIPPED row is not `GATE FAIL`, or if the composed provenance line is not byte-identical to the one function that composes it.

**And the basis carries a second caveat on its own face.** SO-3aR2's PATCHED aggregate of **2.6779490823450605 %** sits **INSIDE** `VERIFICATION_CHARTER.md` §7 step 4's 2.5–5 % harness-sound floor — the artefact's `harness_floor_caveat` says *"the patched gradient passes essentially ON the floor and must never be described as a sub-percent verification"*.

**Limb 2 — the stop marker.** `SO3_STOP_MARKER.json` was written on the exit path and carries the item verdict `PASS`, `rows: {"SHIPPED": "PASS", "PATCHED": "PASS"}`, `stages_declared: 7 / stages_executed: 7 / stages_short: 0`, `truncated: false`, `chain_rc: 0`, `verdict_source: "COPIED FROM THE COMPARATOR ARTEFACT"`, and the md5 of the grade JSON it copied from (`fd31be8d59a730d7c8eabe4a6c8a4782`).

---

## 8. PREDICTIONS — **ELEVEN REGISTERED, AND FOUR OF THEM MISSED**

Registered outcomes are pre-registration §13; measured outcomes are the grade artefact's `predictions` block, scored by the comparator and never adjusted.

| token | registered | measured | |
|---|---|---|---|
| `P1_cells_4032` | HIT | `G-M2` `PASS`, 4,032 cells | **HIT** |
| `P2_CL_at_alpha0_in_band` | HIT | — | **MISS** — see 8.1 |
| `P3_CD_monotone_increasing_in_alpha` | HIT | baseline `CD` 0.017239 < 0.020911 < 0.027268 | **HIT** |
| `P4_G_MP_STRUCT_PASS_all_components` | HIT | `PASS` on both rows, 4 of 4 components each | **HIT** |
| `P5_PATCHED_G5J_PASS_4_of_4` | **MISS** | verdict `PASS`, 4 of 4 pairs, aggregate 0.0689 % ≤ 1.0 % — all three conjuncts met | **HIT — a registered MISS that came in as a HIT** |
| `P6_SHIPPED_G5J_GATE_FAIL` | HIT | SHIPPED `G5J` is **`PASS`**, not `GATE FAIL` | **MISS** — see 8.2 |
| `P7_G_TB_PASS_at_the_wrong_step` | HIT | 0 of 4 components pass band D at `h = 1e-8`, both rows | **HIT** |
| `P8_P_EVAL_at_least_one_evaluation_fails_per_F_arm` | HIT on both F arms | **34 of 34 succeeded, 0 failed**, both F arms | **MISS on both rows** — see 8.3 |
| `P9_plateau_holds_at_the_WING_angles` | HIT | HIT at `SHIPPED_point0`, `SHIPPED_point2`, `PATCHED_point0`, `PATCHED_point2` | **HIT ×4** |
| `P_COST_total_core_min_in_band` | (band re-derived by Amendment 2 to [60.0, 300.0]) | 28.900 core-min, **below** the band's lower edge | **MISS** — see §9 |

**The registered item outcome was `GATE REACHED`**, with `GATE FAIL` declared fully admissible (§13). **The item came in `PASS`, which is better than registered — and a registration that under-called its own outcome is reported as such, not as a success of the registration.**

### 8.1 `P2` — THE PREDICTION IS TRUE OF THE BASELINE AND THE TOKEN STILL READS `MISS`, AND THE REASON IS A CHANGE OF QUANTITY

`P2` is registered as *"baseline `CL` at α₀ = 5.13918623195176° lies in [0.45, 0.55]"*. **That statement is true of the undeformed baseline**: `CL_baseline[1] = 0.49876526085592926`, inside the band.

**The token still scored `MISS`, and the comparator is not wrong.** `so3_grade.py:2512-2519` reads `X[rk]["CL_base"][1]` — the **X arm's own** scenario-1 `CL`. In SO-3aR2 the X arms ran at the undeformed baseline, so that field *was* the baseline `CL` and `P2` read `HIT` there. **In SO-3 the X arms run at the final design point by registration** (`G-DESIGNPOINT`), so that field is the `CL` **at the optimum** — `0.15320273615847435` (`XE-P/so3_X.json`) and `0.15240508504741015` (`XE-S/so3_X.json`), both far outside [0.45, 0.55].

**This is the `P5` naming defect one layer along**: a token whose name says *baseline* reading a field whose meaning moved when the item added endpoint arms. **Two readings are forbidden in both directions.** Nobody may quote *"the baseline `CL` was out of band"* off this `MISS` — it was not, it was 0.49877. And nobody may quote *"`P2` really hit"* — the frozen comparator scored what it scored, and its output is the record. The comparator is pinned by md5 and the item has had first compute, so **nothing here is repaired; it is disclosed.**

### 8.2 `P6` — THE SHIPPED ROW WAS PREDICTED TO `GATE FAIL` AND IT PASSED

The registration expected the SHIPPED toolchain's multipoint gradient to miss its band at the endpoint, as it did at SO-3aR2's baseline by more than 6× (§7). **It did not: SHIPPED `G5J` aggregate 0.08594454384641227 %, 4 of 4 pairs `PASS`.** This is a `MISS` and it is the informative one on the sheet — **the registration's expectation about the shipped toolchain was refuted at the final design point**, which is exactly the surface `DAFOAM_CHARTER.md` §9 exists to expose. It is **not** evidence that the IDWarp defect is absent (§5 and §10).

### 8.3 `P8` — THE MULTIPOINT EVALUATION PATHOLOGY DID NOT REPRODUCE, AND THAT MISS IS A REAL FINDING

The registration expected, in terms (§6): *"at least one evaluation failure per F arm is EXPECTED … a census that reports zero failures is more likely to be a census that is not looking than a run that had none."* **The census measured 34 declared, 34 succeeded, 0 failed, on both F arms — so `P8` reads `MISS` on both rows.**

**The census was looking, and this is how that is known rather than assumed.** `R5_read_F` is in the birth register as **born** against the real code path (§6.1), and the F-plant control read **112 planted values back off disk** on each row at a worst residual of 1.7932703932910243e-16 (§6.2). A reader that could not see a non-zero is excluded by measurement, not by inference.

**So the honest reading is that the pathology this registration expected did not occur** — the probes at `h = 1e-8` on a primal with `eta_F ≈ 1.75e-08` all evaluated, they simply evaluated to numbers that fail band D by 73–116 % (§3.3), which is the `G-TB` control succeeding, not an evaluation failing. **The registration was wrong about the mechanism and is recorded as wrong.** It is not a success and is not written up as one.

---

## 9. COST CALIBRATION (`CLAUDE.md` rule 12)

**28.900 core-min MEASURED against 228.59 core-min REGISTERED — ratio 0.126×, an over-prediction of very nearly 8×.** The measured figure is the grade artefact's own `G10_caps.total_core_min` (28.900000000000002), cross-checked against the seven `arm_census` rows (0.167 + 7.917 + 6.950 + 2.350 + 2.533 + 4.450 + 4.533 = 28.900). **Basis: gross — and gross equals cleaned here as a reading, not an assumption**: the longest arm is `O-S` at 475 wall s against the `COMPUTE_BUDGET_CHARTER.md` §2 3,600-s stall rule, so nothing is removed. **Ceiling 595.0 core-min, used to 4.9 %; no cap crossed on any arm.**

**\$0.02471 DERIVED, NOT MEASURED**, at c7a.4xlarge **\$0.0513/core-h**, **REPORTED-BY-OWNER** — the artefact's own `cost_basis` field says so in terms: *"the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)"*. **GPU: 0 GPU-h.**

**THE ATTRIBUTION IS MISPREDICTION, CONSERVATIVE, AND IT IS CONCENTRATED IN ONE REGISTERED QUANTITY.** The two IPOPT arms carry the whole gap: predicted 103.0 core-min each, actual **7.917** (`O-S`, ratio 0.0769) and **6.950** (`O-P`, ratio 0.0675). **The registration priced the optimiser at its registered `max_iter` of 50 majors; IPOPT converged on its own tolerance in 12 and 10.** The five non-optimiser arms were predicted well and all under — MESH 0.8789×, XE-S 0.6351×, XE-P 0.6846×, FE-S 0.5933×, FE-P 0.6044× — an ordinary ~0.6–0.9× conservatism, not a modelling error. **The forward rule this item pays for is: price an optimiser at an EXPECTED major count and keep `max_iter` as the CAP. A cap is not an estimate.**

**WASTE, NAMED SEPARATELY AND NEVER FOLDED INTO THE 0.126× RATIO** (`COMPUTE_BUDGET_CHARTER.md` §6): **0.167 core-min**, the single `MESH` arm of the accidental selftest launch of 2026-09-01T02:41:37Z, quarantined at `/home/ubuntu/certonomous-runs/QUARANTINE-SO3-selftest-accidental-launch-20260901T0242Z` with `chain=NOT A RESULT declared=7 executed=1`. Its immediate re-launch spent **zero** — the driver refused it `chain=REFUSED_ALREADY_BOUGHT arm=MESH`, the already-bought guard working. Waste is 0.58 % of the item's spend. **The two grade objects in that quarantine read `NOT A RESULT` and are NOT this item's verdict; they may never be cited as one** (pre-registration §16).

The calibration row for this item is **`docs/COST_CALIBRATION.md` row `C-20260901T041827.958337Z-26909c1d`**, and this section carries the same figures from the same artefacts.

---

## 10. WHAT THIS ITEM DOES **NOT** ESTABLISH

* **It does not establish that "DAFoam reduces weighted drag by X".** The admitting gradient is `GATE FAIL` on the shipped toolchain and every link of the provenance chain is `GATE FAIL` at item level (§7). The only sentence this item licenses is *"on the patched toolchain `dafoam-idwarp-rot:v1`, …"*, and that sentence is enforced in code, not asked for.
* **It does not establish a trimmed-`CL` result, and nothing here is a lift-neutral drag reduction.** `CL` is unconstrained; the triple collapsed and went negative at point 0 on both rows (§2, §2.1). Any drag figure lifted out of this record without its lift triple is a false statement.
* **It does not establish a sub-percent verification.** Both endpoint aggregates sit **below** the 2.5–5 % harness-sound floor and are labelled a claim about the harness (§3.1); the basis it spends passes essentially **on** that floor (§7).
* **It does not establish that the IDWarp defect is absent from any component.** A divergence of 0.000 % is reported with its number and never read as absence; the worst measured divergence is 24.17 % (§5), and the shipped row's endpoint `PASS` is a reading at one design point, not a statement about the toolchain.
* **It does not establish anything at np ≠ 1.** np = 1 is a condition on the inheritance, not a setting: A4 measured a 16,600× spread between two decompositions of one mesh.
* **It does not establish a dot-product duality check.** `G6` is `NOT MEASURED` (§6.5).
* **It does not establish a grid-converged optimum.** No grid triple, no GCI, and `CLAUDE.md` rule 5 has no row to act on here.
* **It does not re-establish anything SO-3aR2 already graded.**

---

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.** No arm, artefact, figure, defect note or verdict from SO-3 has been filed, sent, emailed, uploaded, registered, posted or commented outside this box, by any agent, at any time. **SUBMISSIONS ARE PARKED**, and sending is Sanaa's decision alone (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10; pre-registration §17).
