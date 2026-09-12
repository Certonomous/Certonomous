# CURRICULUM SO-3aR2 — RESULTS. **`GATE FAIL`**, two rows, five arms of five, 14.318 core-min

**Written 2026-09-12 from the frozen grade artefact and the run root's own ledger. ZERO solver
core-minutes were spent writing it, nothing was re-graded, no comparator was re-run, and no
verdict in it is new.** Every figure below carries the artefact path and the JSON key it was read
from. **SUBMISSIONS PARKED** — this record is filed in this box and sent nowhere
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Why this file exists.** The item ran and was graded on **2026-08-31**, its rows have stood in
`docs/dafoam/README.md` §3 since `36df34f0` (2026-09-02), and its cost row has stood in
`docs/COST_CALIBRATION.md` since the night of the run — **and the case directory itself carried no
results record**, so a reader who opened the case saw a pre-registration and nine instruments and
no answer. `cases/dafoam/INDEX.md` Addendum 2026-09-02 §1 names that gap in terms
(*"SO-3aR2 STILL HAS NO `RESULTS.md`, AND THIS LANE DID NOT MANUFACTURE ONE"* — it was dispatched
to SO-3). This closes it.

| | |
|---|---|
| item | **SO-3aR2** — NACA0012 **incompressible α-multipoint weighted-objective GRADIENT**, ladder A1, **4,032 cells**, **np = 1 on every arm**. The rung that makes SO-3 admissible |
| objective | `J = Σᵢ wᵢ·CDᵢ(αᵢ)`, three operating points **α = 3.13918623195176 / 5.13918623195176 / 7.13918623195176 deg**, equal weights **⅓**; graded design variables `shape[0, 3, 6, 7]` |
| registration | `PREREGISTRATION.md`, **Version 1.0 FROZEN, dated 2026-08-31** — *"NACA0012 ALPHA-MULTIPOINT WEIGHTED OBJECTIVE, INCOMPRESSIBLE: the FD-VERIFIED MULTIPOINT GRADIENT RUNG"* |
| freeze | **`181fd627924c9108000f5259dd30fd87cc0daf3f`**, 2026-08-31 22:35:37Z — document and all seventeen instruments in **one** commit. Arming `ffae7724c8f7e10ea351f467521162ae6717ece9`, 22:40:41Z. **First container started 22:42:37Z** (`ledger.txt` `STAGED stamp`), i.e. after the freeze |
| grading path | `so3ar2_grade.py`, pinned at the freeze in §14 as md5 **`c81a09a90950cb1610f40a91b29cdabe`**, asserted by `so3ar2_chain_driver.sh:MD5_GRADER` before staging (`rc = 4` on drift) |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient` |
| grade artefact | **`SO3aR2_grade_20260831T230221Z.json`** (+ `.out`, + `SO3aR2_STOP_MARKER.json`) |
| chain | `STATUS.chain` — `chain=COMPLETE declared=5 executed=5 stamp=20260831T230221Z`, all five arms `rc=0`, `grader_rc=0` |
| **ITEM VERDICT** | **`GATE FAIL`** — `verdict`; rows `{"SHIPPED": "GATE FAIL", "PATCHED": "PASS"}` — `rows`. Worst-first: the shipped row fails, so the item fails. **This outcome was REGISTERED IN ADVANCE** (§13: *"SHIPPED row `GATE FAIL`, PATCHED row `PASS`, item `GATE FAIL`"*) |
| **cost, MEASURED** | **14.318 core-min** against **22.1** registered (ratio **0.648×**), ceiling 115.0. **\$0.01224 DERIVED, NOT MEASURED** |

**Rule-2 identity, verified here rather than asserted.** `PREREGISTRATION.md` in the working tree
hashes **md5 `5a023894abf85910bb8c52464cf41a38`**, byte-identical to the blob at the freeze commit
`181fd627`; `so3ar2_grade.py` in the working tree hashes **md5 `c81a09a90950cb1610f40a91b29cdabe`**,
identical at `HEAD` and identical to the §14 pin, and `181fd627` is the only commit that has ever
touched it. **The frozen files are the files that ran.**

---

## 0. THE TWO ROWS, IN ONE TABLE — TOOLCHAIN BY HASH, NEVER BY VERSION STRING

`DAFOAM_CHARTER.md` §6: *"Toolchain identity is an image ID and a library md5 — a version string is
not an identity."* **All three lab images report DAFoam 5.0.0 / OpenFOAM v2506 / PETSc 3.15.5 /
IDWarp 2.6.2, and the two `libidwarp.so` files below are both 491,344 bytes and both report
`2.6.2`.** The version strings cannot tell these rows apart. The hashes can.

| row | image digest (`gates.G9_toolchain.per_arm.*.digest`) | `libidwarp.so` md5 (`...printed_so_md5` / `...artefact_so_md5`) | graded arms | **`G5J` aggregate rel err on `J`** | **row verdict** |
|---|---|---|---|---|---|
| **SHIPPED** `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** | `MESH`, `X-S`, `F-S` | **31.498325840045588 %** against a 5.0 % band | **`GATE FAIL`** |
| **PATCHED** `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** | `X-P`, `F-P` | **2.6779490823450605 %** against a 5.0 % band | **`PASS`** |

Source: `SO3aR2_grade_20260831T230221Z.json` → `gates.G9_toolchain` (`verdict: "PASS"`, `ok: true`
on all five arms — the md5 printed by the running container equals the md5 recorded in that arm's
own artefact) and `gates.G5J.{SHIPPED,PATCHED}.G5J_objective.aggregate_rel_err_pct`. The same two
md5s are independently in the run root's own `ledger.txt` as `D4S_IDWARP_SO_MD5` on each `ARM=` row.

**On the SHIPPED toolchain the multipoint objective gradient missed its 5 % band by more than 6×,
on this very case. That reading travels with every downstream claim, SO-3's `PASS` included**
(`upstream_provenance.verdict_line`).

**⚠ THE PATCHED `PASS` IS NOT A SUB-PERCENT VERIFICATION AND MUST NEVER BE QUOTED AS ONE.**
**2.678 % sits INSIDE the 2.5–5 % harness-sound floor** that `VERIFICATION_CHARTER.md` §7 step 4
records for this dataset — whose own establishing base is **2.5–3.0 % at 4,032 cells**, which is
exactly this mesh. The patched gradient passes essentially **on** the floor. *(Read the clause as it
now stands: its sentence "a number below that is a claim about the harness" was **STRUCK IN PLACE
2026-09-03, v1.56 `§2al`** as appearing nowhere in its source. The floor's interval, 2.5–5 %, is
unchanged, and 2.678 % is inside it, not below it — the struck sentence would not reach this figure
either way.)*

**AND IT IS A BASELINE-ONLY READING.** Every number in this item is at **iteration 0**, the
undeformed mesh. Nothing here is a statement about an optimum; closing that gap is SO-3's job.

---

## 1. THE FIVE ARMS, AND THE COST

| arm | row | rc | wall s | ranks | core-min | predicted | ratio | cap |
|---|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 10 | 1 | 0.167 | 0.19 | 0.8789 | 5.0 |
| `X-S` | SHIPPED | 0 | 151 | 1 | 2.517 | 3.1 | 0.8119 | 15.0 |
| `F-S` | SHIPPED | 0 | 262 | 1 | 4.367 | 7.5 | 0.5823 | 40.0 |
| `X-P` | PATCHED | 0 | 151 | 1 | 2.517 | 3.7 | 0.6803 | 15.0 |
| `F-P` | PATCHED | 0 | 285 | 1 | 4.750 | 7.5 | 0.6333 | 40.0 |
| **item** | | | | | **14.318** | **22.1** | **0.648** | **115.0 ceiling** |

`core_min`, `predicted`, `ratio_actual_over_predicted`, `cap` and `crossed: false` are read per arm
from `gates.G10_caps.per_arm`; `total_core_min = 14.318` and
`usd_derived_not_measured = 0.01224` from `gates.G10_caps`; `rc` and `wall_s` corroborated
independently from the run root's `ledger.txt` `ARM=` rows. `G10_caps.verdict` is **`PASS`** —
**no arm crossed its cap and `arms_not_run` is empty.**

**\$0.01224 is DERIVED, NOT MEASURED**, at c7a.4xlarge **\$0.0513/core-h**, *reported-by-owner*
(Sanaa 2026-08-21/22) — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). The
grade artefact says so itself in `gates.G10_caps.cost_basis`.

**Placement.** `gates.G12_placement.verdict` **`PASS`**: registered `cpuset` **"14"**, every arm on
it, `delivered_cores_mean` 0.9849–0.9979 at np = 1. `MESH` is `NOT_MEASURED` and is **named** as
such in `gates.G12_placement.not_measured` and `not_measured.G12`, not silently dropped.

**Cost calibration (`CLAUDE.md` rule 12) is already discharged and is NOT re-filed here.**
`docs/COST_CALIBRATION.md` row **`C-20260831T230621.613076Z-d360c175`** carries it: 22.1 registered
point / band [14.0, 60.0] / ceiling 115.0; **14.318 measured**; gross == cleaned (*the longest arm is
`F-P` at 285 wall s against the 3600-s stall rule, so nothing is removed*); ratio **0.648×** —
inside the band, **`P-COST` HIT**, and the row states that it lands only **0.318 core-min above the
band floor**. Attribution: **misprediction in the over-estimating direction on all five arms, not
contention.** **Waste 2.134 core-min from SO-3a and SO-3aR is named separately in that row and never
folded into this ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

---

## 2. COMPLETION — THE FIVE RULE-4 CLAUSES, PRINTED PER ARM

`gates.G1_completion` = **`PASS`**; `completion.verdict` = **`PASS`**; `completion.declared` = 5,
`completion.executed` = 5. Per-arm limbs from `rule4_clauses_per_arm`:

| arm | C1 `rc` | C2 terminal marker | C3 artefact | **C4 age guard** | C5 no fatal token |
|---|---|---|---|---|---|
| `MESH` | **PASS** (`rc = 0`) | **PASS** — `Mesh OK.` in `checkMesh.log` | **PASS** — `checkMesh.log` | **PASS** | **PASS** |
| `X-S` | **PASS** (`rc = 0`) | **PASS** — `SO3AR2_X_WRITTEN` | **PASS** — `so3ar2_X.json` | **PASS** | **PASS** |
| `F-S` | **PASS** (`rc = 0`) | **PASS** — `SO3AR2_F_WRITTEN` | **PASS** — `so3ar2_F.json` | **PASS** | **PASS** |
| `X-P` | **PASS** (`rc = 0`) | **PASS** — `SO3AR2_X_WRITTEN` | **PASS** — `so3ar2_X.json` | **PASS** | **PASS** |
| `F-P` | **PASS** (`rc = 0`) | **PASS** — `SO3AR2_F_WRITTEN` | **PASS** — `so3ar2_F.json` | **PASS** | **PASS** |

**25 of 25 limbs PASS. Nothing is aggregated away; every clause is printed on its own.**

**The C4 age guard, in full, because it is the clause that dates the answer.** The datum is
resolved **by existence, never by name**, and is `0/U` on the four solver arms and `0.orig/U` on
`MESH` — **not `0/T`**: this is the DAFoam family, not the thermal family, and `U` is the field the
launcher touches last. From `rule4_clauses_per_arm.*.C4_age_guard` and `age_datum_resolution`:

| arm | datum | datum mtime (epoch) | artefact mtime (epoch) | margin (s) | compressed twin? |
|---|---|---|---|---|---|
| `MESH` | `0.orig/U` | 1788216225 | 1788216228 | **+3** | false |
| `X-S` | `0/U` | 1788216298 | 1788216447 | **+149** | false |
| `F-S` | `0/U` | 1788216514 | 1788216775 | **+261** | false |
| `X-P` | `0/U` | 1788216840 | 1788216987 | **+147** | false |
| `F-P` | `0/U` | 1788217055 | 1788217321 | **+266** | false |

Every arm's artefact is newer than its own datum, every arm's `C4_age_guard.verdict` is **`PASS`**,
and `age_datum_resolution.*.ok` is `true` on all five with
`mtime_rule: "the launcher touched it: must equal the datum"`. The epochs are quoted from the
artefact; the margin column is their difference and nothing else is recomputed here.
**`is_compressed_twin` is `false` on every arm**, so no guard was satisfied by a `.gz` twin of the
field it was supposed to date.

**C5 excludes exactly one benign line and COUNTS it** (`MESH`, `checkMesh.log:18`,
`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`) — an **enablement notice that
the handler is installed, not a report that it fired**. `n_benign_lines_excluded` is 1 on `MESH` and
**0 on every other arm**; ten fatal tokens are searched on every arm and named in the artefact. *A
suppression a reader cannot see is the same defect wearing the other hat.*

**Convergence is REPORTED, NEVER GATED** (`primal_convergence.per_arm`): 102 real
`Minimal residual … satisfied the prescribed tolerance` statements on each F arm, residuals
8.95e-09–9.98e-09 against `1e-08`. OpenFOAM's `SIMPLE: no convergence criteria found` banner appears
**12×** and **is counted separately and is not evidence** — the artefact's own discriminator says
so, measured 4× on a reference log from a run that converged.

---

## 3. THE BRIGHT LINE — `G5J`, THE FD TABLE ON THE MULTIPOINT OBJECTIVE `J`

`DAFOAM_CHARTER.md` §2: *a DAFoam gradient is not a result until a finite-difference table stands
beside it at a step proved to lie in the plateau.* **Here is the table.** Gate constants, all from
`gates.G5J`: **`band_D_pct` 5.0**, **`band_E_pct` 5.0**, **`min_graded_pairs` 3**,
**`plateau_tol_pct` 10.0**, reading *"the bright line on the MULTIPOINT OBJECTIVE J, per ROW, with
the plateau proved PER PAIR"*. Central differences, **`steps: [0.01, 0.001, 0.0001]`**, `d_ref` the
middle step **1e-3** — inside the 1e-3…1e-2 that `VERIFICATION_CHARTER.md` §7 step 5 recommends for
A1's FFD control points.

### 3.1 SUMMARY — `gates.G5J.{row}.G5J_objective`

| row | candidate pairs | **graded pairs** | `PASS` | `GATE FAIL` | **aggregate rel err** | **worst pair** | band D | band E | **sign flips** | `G5J` |
|---|---|---|---|---|---|---|---|---|---|---|
| **SHIPPED** | 4 | **4** | 2 | **2** | **31.498325840045588 %** | **47.18912652536565 %** (`shape[6]`) | **`GATE FAIL`** | **`GATE FAIL`** | **0** | **`GATE FAIL`** |
| **PATCHED** | 4 | **4** | 4 | 0 | **2.6779490823450605 %** | **4.059520239796664 %** (`shape[6]`) | `PASS` | `PASS` | **0** | **`PASS`** |

**4 graded pairs on each row against a registered minimum of 3. Zero sign flips on either row** —
`DAFOAM_CHARTER.md` §2 makes any sign flip a FAIL on its own, and there is none here.

### 3.2 THE PAIRS THEMSELVES, WITH THE PLATEAU PROOF PER PAIR

`plateau_neighbour_pct` is `[|d(1e-2) − d_ref|/|d_ref|, |d(1e-4) − d_ref|/|d_ref|] × 100`; the
registered rule is **one-sided** (§6 of the registration: the pair is graded when `min` of the two is
inside 10 %), and the neighbour it was proved against is printed on every pair.

**SHIPPED** — `gates.G5J.SHIPPED.G5J_objective.pairs`:

| `shape` idx | `J_adj` (adjoint) | `d_ref` = `d_fd`(1e-3) | `d_fd` triple [1e-2, 1e-3, 1e-4] | **rel err** | plateau neighbours (%) | proved against | flip | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | −0.013365588652569602 | −0.012242673532471965 | [−0.012183257227323455, −0.012242673532471965, −0.012176733253013022] | **9.17213970559015 %** | [0.4853, 0.5386] | **the LARGER neighbour** | false | **`GATE FAIL`** |
| 3 | 0.011687209085349055 | 0.012018961329764849 | [0.012025193764356873, 0.012018961329764849, 0.012089128846991953] | 2.7602405508553627 % | [0.0519, 0.5838] | the LARGER neighbour | false | `PASS` |
| 6 | 0.02356619257919751 | 0.01601082439682544 | [0.018369567669166212, 0.01601082439682544, 0.016615252879294967] | **47.18912652536565 %** | [14.7322, 3.7751] | **the SMALLER neighbour** | false | **`GATE FAIL`** |
| 7 | 0.006114213432979058 | 0.006211670292254751 | [0.006216424960380981, 0.006211670292254751, 0.006280071392483072] | 1.5689316188789035 % | [0.0765, 1.1012] | the LARGER neighbour | false | `PASS` |

**PATCHED** — `gates.G5J.PATCHED.G5J_objective.pairs`:

| `shape` idx | `J_adj` (adjoint) | `d_ref` = `d_fd`(1e-3) | `d_fd` triple [1e-2, 1e-3, 1e-4] | **rel err** | plateau neighbours (%) | proved against | flip | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | −0.012248354486017627 | −0.012242673532471965 | [−0.012183257227323455, −0.012242673532471965, −0.012176733253013022] | **0.04640288357435872 %** | [0.4853, 0.5386] | the LARGER neighbour | false | `PASS` |
| 3 | 0.012013942626196854 | 0.012018961329764849 | [0.012025193764356873, 0.012018961329764849, 0.012089128846991953] | **0.04175654975747157 %** | [0.0519, 0.5838] | the LARGER neighbour | false | `PASS` |
| 6 | 0.01666078705377287 | 0.01601082439682544 | [0.018369567669166212, 0.01601082439682544, 0.016615252879294967] | **4.059520239796664 %** | [14.7322, 3.7751] | **the SMALLER neighbour** | false | `PASS` |
| 7 | 0.006202686046256103 | 0.006211670292254751 | [0.006216424960380981, 0.006211670292254751, 0.006280071392483072] | **0.14463494641449468 %** | [0.0765, 1.1012] | the LARGER neighbour | false | `PASS` |

### 3.3 **THE FD REFERENCE IS THE SAME ON BOTH ROWS — MEASURED, NOT ASSUMED, AND IT IS THE FINDING**

**Read the two tables above against each other: the `d_fd` triples and `d_ref` values are identical
to every printed digit. The `J_adj` column is the only one that moves.**

That is not an artefact of a shared reference. `F-S` and `F-P` are **two separate arms, on two
separate images, each with its own primals** (4.367 and 4.750 core-min; separate logs; separate
`so3ar2_F.json`, md5 `9cd370c0caa88b43811e81ad921f2d6a` vs `333fe58f3067cccbb6a1b521368b9bd3`).
Compared leaf by leaf, the two artefacts carry **510 leaves each, 510 keys in common, and exactly
THREE differing values — all three of them toolchain identity fields**:

| differing leaf | `F-S` (SHIPPED) | `F-P` (PATCHED) |
|---|---|---|
| `identity/libidwarp_so_md5` | `f0fcb488e0e98156575cd19548e91663` | `85f59e87253e0a71a813f64ca6e4c425` |
| `identity/idwarp_file` | `…/miniconda3/lib/python3.10/site-packages/…` | `/opt/idwarp_patched/idwarp/__init__.py` |
| `identity/write_compression_source` | `/mnt/F-S/system/controlDict` | `/mnt/F-P/system/controlDict` |

**507 of 507 physics leaves agree.** So the IDWarp rotation patch does not move the
finite-difference reference at all — **the entire 31.498 % → 2.678 % difference lives in the
adjoint**, which is exactly where the defect is claimed to live. *This is a reading of two frozen
artefacts, computed at zero solver cost; it is reported as a measurement and is not a gate.*

### 3.4 `G5C` — THE THREE PER-SCENARIO `CL` FAMILIES, SAME RULE

`gates.G5J.{row}.G5C_lift_per_scenario.per_scenario` — 4 candidate pairs, 4 graded, 0 sign flips in
every cell:

| row | | point0, α = 3.13919° | point1, α = 5.13919° | point2, α = 7.13919° | `G5C` |
|---|---|---|---|---|---|
| **SHIPPED** | aggregate / worst | **2.330466777119169 % / 36.89830314144139 %** | **4.332589243091313 % / 19.80431156202468 %** | **6.188830608081735 % / 11.770946565429377 %** | **`GATE FAIL`** |
| | band D / band E / `n_pass` | `GATE FAIL` / `PASS` / 3 of 4 | `GATE FAIL` / `PASS` / 3 of 4 | `GATE FAIL` / **`GATE FAIL`** / 3 of 4 | |
| **PATCHED** | aggregate / worst | 0.030192224640685418 % / 0.19636055383407064 % | 0.021048153157057107 % / 0.08676320068057473 % | 0.6204357305810368 % / 1.184818899172249 % | **`PASS`** |
| | band D / band E / `n_pass` | `PASS` / `PASS` / 4 of 4 | `PASS` / `PASS` / 4 of 4 | `PASS` / `PASS` / 4 of 4 | |

**The shipped row fails at all three operating points, and the one component it fails on is
`shape[6]` at every one of them** — the leading-edge control point A1/A5 already identified as where
the IDWarp degenerate-rotation branch bites at an undeformed baseline.

### 3.5 THE TRIVIAL BASELINE — THE FD INSTRUMENT IS SHOWN ABLE TO GO RED

`DAFOAM_CHARTER.md` §4's registered wrong-step control, **`wrong_step = 1e-8`**, five decades below
the registered middle step, in the subtractive-cancellation regime. `gates.G5J.{row}.G_TB_trivial_baseline`:

| row | `shape[0]` | `shape[3]` | `shape[6]` | `shape[7]` | passing band D at the wrong step | `G_TB` |
|---|---|---|---|---|---|---|
| SHIPPED | **107.43942352166957 %** | **94.40662650822046 %** | **118.35233186751634 %** | **97.00879611231832 %** | **0 of 4** (max allowed 1) | **`PASS`** |
| PATCHED | **106.81755954291683 %** | **94.25025532388491 %** | **112.97470060797032 %** | **96.96551341901876 %** | **0 of 4** (max allowed 1) | **`PASS`** |

The registered withdrawal rule — *"if 2 or more pass, the gate cannot fail, it is not evidence, and
this row's `G5J` verdict is WITHDRAWN to `NOT A RESULT`"* — **did not fire on either row.** So both
`G5J` verdicts above stand as verdicts.

**The opposite direction was NOT bought, and the artefact says so**: a step above the largest
registered raises an exception on this case (`A_stepsize_study.md` measured the primal failing at
5e-2 and 1e-1), and *"an errored probe is a weaker baseline than a noise-limited one"*.

---

## 4. THE MULTIPOINT STRUCTURAL IDENTITY — `G-MP-STRUCT`

`gates.G5J.{row}.G_MP_STRUCT_assembly_identity`, identity `J_adj[J,k] == Σᵢ wᵢ · J_adj[CDᵢ,k]`,
**4 components checked**, **`PASS` on both rows**, with
`controls_precondition: "SATISFIED -- the planted control was seen in this run"`.

**What it would catch** (quoted from the artefact rather than paraphrased): *a weight applied on one
side only; a scenario wired to the wrong geometry output; a scenario omitted from the sum; an
ExecComp partial that does not match its own expression.* **What it cannot catch, printed beside
it**: *a defect that corrupts every scenario IDENTICALLY cancels in the identity — which is why G5J
and G5C are bought beside it.*

**`G-ALPHA_operating_points` — `PASS`.** The three α are read back **from the artefacts** as
`3.13918623195176 / 5.13918623195176 / 7.13918623195176` with weights `⅓, ⅓, ⅓` on **all four**
artefacts (`F:SHIPPED`, `F:PATCHED`, `X:SHIPPED`, `X:PATCHED`) and
**`abs_deviation: [0.0, 0.0, 0.0]`** against a tolerance of 1e-12. The gate **REFUSES (exit 2) on a
mismatch** — *"it is not a `GATE FAIL`, it is a wrong item"*.

**Baselines, for the reader who needs the physics anchored** (`X-S/so3ar2_X.json` and
`X-P/so3ar2_X.json`, **identical on both rows to every digit**): `CL_baseline`
[0.31189588769251864, 0.49876526085592926, 0.6639763551107052], `CD_baseline`
[0.01723938072177922, 0.020910510045267394, 0.027268054119716875],
**`J_baseline` = 0.02180598162892116**.

**`G-M2_mesh_identity`** = **`PASS`**, `mesh_cells` = **4032**.
**`G-NOOPT_no_optimiser_ran`** = **`PASS`**: 11 optimiser keys searched across 4 artefacts and 5
logs, **`n_optimiser_markers: 0`** — **no optimiser ran in this item, by construction and by
measurement.** **`G-STAGES_declared_vs_executed`** = **`PASS`**: declared 5, executed 5, short 0,
`discard_fraction 0.0`.

---

## 5. SHIPPED-VERSUS-PATCHED DIVERGENCE — REPORTED WITH ITS NUMBER, NEVER GATED

`divergence_shipped_vs_patched`, `status: "REPORTED WITH ITS NUMBER, NEVER GATED"`,
**`worst_pct` = 118.72578844249743 %**, **20 non-zero pairs**. The largest six:

| quantity | `shape` idx | `J_patched` | `J_shipped` | **divergence** |
|---|---|---|---|---|
| `CD1` | 6 | −0.0010656354008230606 | 0.005690737156918013 | **118.72578844249743 %** |
| `J` | 6 | 0.01666078705377287 | 0.02356619257919751 | **29.302168783599853 %** |
| `CL0` | 6 | −0.10242646006013872 | −0.140495964444073 | **27.096510945756414 %** |
| `CL1` | 6 | −0.3856210243987129 | −0.46239179944418746 | 16.60297071396075 % |
| `CD0` | 6 | −0.0249922821980849 | −0.021076069703681036 | 15.669687399352245 % |
| `CD2` | 6 | 0.0760402787602169 | 0.08608391028434652 | 11.667257552490554 % |

**`shape[6]` is the component in every one of the top six.** The artefact's own caution travels with
this table: *"a divergence of 0.000 % on some component is REPORTED with its number and is never
read as `the defect is absent`."*

---

## 6. CONTROLS AND INSTRUMENT INTEGRITY

### 6.1 THE BIRTH REGISTER — **8 READERS, 8 BORN, 0 NOT BORN**

`birth_register`: `n_born: 8`, `n_not_born: 0`, `not_born: []`. Each reader names its **real
producer** and the units that gave birth to it — `R1_read_ledger` (→ G1/G9/G10/G12),
`R2_fatal_token_sites` (→ G1, and the register itself flags it as a reader that **reads a zero as a
PASS**), `R2b_read_primal_convergence`, `R3_read_mesh_cells` (→ G-M2), `R4_read_X` (→ G5J, G5C,
G-MP-STRUCT, flagged **ALL CAN PASS ON A SMALL NUMBER**), `R5_read_F`, and the rest.

### 6.2 THE PLANTED-ZERO CONTROLS — AND THEY WERE SIZED **RELATIVE TO THE BAND THEY MUST CROSS**

`CLAUDE.md` rule 3. The registration's §4 records why the sizing is relative: `SO-2M` was lost to an
**absolute** plant of 1.234e-03 that was only 2.48 % of its own reference against a 5 % band — *a
plant too small to fail the gate demonstrates nothing.* The registered form is
**`plant_i = K · (band_D/100) · |d_ref_i|`, `PLANT_K = 3.0`**, i.e. **15 % on a 5 % band, a margin
ratio of 3**.

| control (`controls.*`) | reading |
|---|---|
| **`grader_plant_F_PATCHED`** | `grader_plant_F_seen: true`, **112 values**, **`worst_residual` 1.7932703932910243e-16** — the reader read the plant back off disk to machine precision |
| **`grader_plant_F_SHIPPED`** | `grader_plant_F_seen: true`, **112 values**, **`worst_residual` 1.7932703932910243e-16** |
| **`grader_plant_X_PATCHED`** | `grader_plant_X_seen: true`. Plant 0.001836401029870795 written onto `d_ref` −0.012242673532471965 (**`planted_rel_err_pct` 15.000000000000002 %**), read back −0.010411953456146832. **`G5J` `PASS` → `GATE FAIL` under the plant** (`EXERCISED-PASS`); **`G-MP-STRUCT` `PASS` → `GATE FAIL`** |
| **`grader_plant_X_SHIPPED`** | `grader_plant_X_seen: true`, same plant and sizing, read back −0.011529187622698807. **`G-MP-STRUCT` `PASS` → `GATE FAIL`**; `G5J` reads `GATE FAIL` planted **and unplanted** — and the artefact states the honest version rather than claiming a flip: *"the gate read a violation on the REAL artefact (`GATE FAIL`), which is the demonstration itself"* |
| **`grader_plant_cells`** | on disk **4032**, planted **4039**, **read back 4039**, `grader_plant_cells_seen: true` |
| **`grader_plant_c5`** | `grader_plant_c5_seen: true` on the real 2,208-line `X-S` log: 1 positive site, 0 negative sites, and the convergence discriminator is shown **moved by a planted REAL statement** and **unmoved by a planted banner** — the exact confusion C5 exists to survive |
| **`instrument_ctrl_{SHIPPED,PATCHED}`** | `both_directions: true`, **7 zero entries read per side** (`J` + three `CD` + three `CL`), want **0.617**, every one read back at 0.617 (0.6169999999999994 / 0.6170000000000064 / 0.6169999999999787) |

**Every reader that produced a zero in this item was shown able to produce a non-zero, in the same
invocation, through the same reader.**

### 6.3 `G-EVALFAIL` — THE EVALUATION CENSUS, AND THE PREDICTION IT FALSIFIED

`gates.G-EVALFAIL_evaluation_census`, `status: "REPORTED -- a failed evaluation is a gradable state"`,
`both_counts_reported: true`:

| artefact | declared | **succeeded** | **failed** | failure fraction |
|---|---|---|---|---|
| `F:SHIPPED` | 34 | **34** | **0** | 0.0 |
| `F:PATCHED` | 34 | **34** | **0** | 0.0 |
| `X:SHIPPED` | 1 | 1 | 0 | 0.0 |
| `X:PATCHED` | 1 | 1 | 0 | 0.0 |

**The registration (§9) expected at least one failure per F arm and got none. `P8` MISSES on both F
arms, and it is reported as a miss** — see §7. The census is shown to have been looking: its sibling
`grader_plant_F` controls read 112 planted values back at 1.79e-16.

### 6.4 `G9_toolchain` — IDENTITY BY DIGEST AND HASH

`verdict: "PASS"`, `ok: true` on all five arms: on each arm the `libidwarp.so` md5 **printed by the
running container** equals the md5 **recorded in that arm's own artefact**. The `MESH` arm carries
`artefact_so_md5: null` (a `checkMesh` arm writes no `so3ar2_*.json`) and its `printed_so_md5` is
the shipped `f0fcb488…` — stated here rather than left for a reader to trip over.

### 6.5 WHAT WAS **NOT** MEASURED — NAMED, NOT LEFT TO BE INFERRED

* **`gates.G6_dot_product_duality` is `NOT MEASURED`** and its full text is
  *"NOT MEASURED -- AV-2 measured that seeding forward mode makes the primal FAIL on this exact case
  on BOTH images; named, never composed."* **It is a key in the artefact; it is not a passing gate,
  and nothing in this item rests on a dot-product duality check.**
* **`no_gci`**: *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED."* There is no grid
  triple in this item and **no GCI is quoted anywhere in this record.**
* **`not_measured`**: `G1` = {} (nothing missing), `G10` = [], **`G12` = ["MESH"]** — the
  delivered-cores sampler did not read the `MESH` arm.
* **`rc_inferences` = {}** — no return code anywhere in this item was inferred; all five were read.
* **`G-IC0` is REPORTED, NEVER GATED** and is **not carried in the grade artefact at all**; its
  measurements are the four `{F,X}-{S,P}_IC0.json` files in the run root, each reading
  **`n_ic_fields: 7`, `n_changed_during_run: 0` on all three points**. See §7's note on `P-IC0`.

---

## 7. PREDICTIONS — SCORED BY THE COMPARATOR, AND THE MISSES ARE REPORTED AS MISSES

`predictions`, verbatim:

| # | prediction | result |
|---|---|---|
| `P1` | cells == 4032 | **HIT** |
| `P2` | baseline `CL` at α₀ in [0.45, 0.55] | **HIT** |
| `P3` | `CD` monotone increasing across the three α | **HIT** |
| `P4` | `G-MP-STRUCT` `PASS` on all components | **HIT** |
| `P5` | PATCHED row `G5J` `PASS`, **4 of 4 pairs in band D, aggregate ≤ 1.0 %** | **MISS** |
| `P6` | SHIPPED row `G5J` `GATE FAIL` on at least one component | **HIT** |
| `P7` | `G-TB` `PASS` at the wrong step | **HIT** |
| `P8` | at least one of the 34 declared evaluations per F arm fails | **MISS** on `F:SHIPPED` **and** **MISS** on `F:PATCHED` |
| `P9` | the plateau holds per pair at the wing angles | **HIT** ×4 (`{SHIPPED,PATCHED}` × `{point0, point2}`) |
| `P-COST` | total graded core-min inside the registered band | **HIT** |

**`P5` MISSED WHILE THE PATCHED ROW STILL PASSED, AND THE DISTINCTION IS THE WHOLE POINT.** The
row's gate is band D/E at 5.0 % and the row cleared it, 4 of 4. **`P5` predicted something
stricter — an aggregate ≤ 1.0 % — and the measured aggregate is 2.6779490823450605 %, 2.7× that
prediction.** The prediction is scored against its registered value, not against the gate, and it is
**recorded as a MISS**. It is the same figure as the harness-floor caveat in §0: the patched
gradient on this baseline is a **few-percent** verification, not a sub-percent one, and the
registration guessed sub-percent.

**`P8` MISSED ON BOTH F ARMS, AND THAT MISS IS A REAL FINDING.** The registration expected the
multipoint evaluation pathology (§9, the IPOPT *"Invalid number in NLP function or derivative"*
class Sanaa named on 2026-08-31) to show itself as at least one failed evaluation per F arm.
**34 of 34 succeeded on both.** **The pathology did not reproduce in this configuration**, and that
is a bounded negative result, not an absence of looking.

### 7.1 FOUR REGISTERED PREDICTIONS ARE **NOT SCORED IN THE ARTEFACT** — AN OPEN ITEM, NOT A VERDICT

The registration registers **`P-COLL`, `P-PIN`, `P-IC0` and `P-PLAT2`** in addition to the ten
above. **None of the four strings appears anywhere in `SO3aR2_grade_20260831T230221Z.json`**
(searched: `P_COLL`, `COLL`, `P_PIN`, `P_IC0`, `IC0`, `P_PLAT2`, `PLAT2`, `two_sided` — zero
occurrences of each). **The comparator did not score them, and this record does not score them
either.** `P-COLL` and `P-PIN` are **arming preconditions** discharged before the run
(`so3ar2_collision_leg_evidence.txt`, `so3ar2_stage_evidence.txt`, arming commit `ffae7724`), so
their absence from a post-run grade is expected. The other two leave measurements on disk with no
score beside them, and both are registered **scored-not-gated** — neither can move this item's
verdict in either direction:

* **`P-IC0`.** The four `*_IC0.json` files read **`n_changed_during_run: 0` on all three points of
  all four solver arms**. The registration's own falsifier reads: *"`n_changed_during_run == 0` on
  every point is **also** a scored MISS and would mean D19's mechanism does not reach this
  configuration."* **The measured condition for that MISS is met on every arm. The token is not in
  the artefact, so this is reported as a reading of the artefacts and NOT as a comparator score.**
  Separately, the same prediction's second limb asks for the item's own **η ≤ 1e-8 relative**;
  `gates.G5J.{SHIPPED,PATCHED}.eta_F` = **1.5789870744242762e-08** on both rows, against the
  `G_TB.eta_F_reference` of **1.3e-10** measured on this mesh by D15 — i.e. **about 121× the
  reference and marginally above the 1e-8 limb.** Stated as a number with its threshold; **the
  ruling on it is the supervisor's.**
* **`P-PLAT2`.** The registration asks whether the pair counts graded under a **two-sided** plateau
  rule (`max` of the two neighbour deviations ≤ 10.0 %) equal the counts under the registered
  one-sided rule (`min` ≤ 10.0 %). Reading the `plateau_neighbour_pct` values the artefact already
  prints: **one-sided 16 pairs per row; two-sided 15 pairs per row.** The single pair that differs
  is the same on both rows — **`G5J_objective`, `shape[6]`, neighbours [14.7322, 3.7751], proved
  against the SMALLER neighbour** — and it is the pair carrying the worst error on each row
  (47.189 % shipped, 4.060 % patched). **This is arithmetic on printed values at zero compute,
  offered as a reading and explicitly NOT as a HIT/MISS score the comparator never emitted.** Its
  registered consequence was forward, never retroactive — *"the SO-3 optimisation rung registers the
  two-sided rule"* — and SO-3 has since run and passed its endpoint FD on both rows.

**Reported to the supervisor as an open bookkeeping item against the comparator, not as a defect in
the physics: `bookkeeping never voids physics`.**

---

## 8. THE TRAVELLING SHIPPED `GATE FAIL` — `upstream_provenance`

`upstream_provenance.verdict: "SATISFIED"`, 5 clauses. **This item's own ground is not clean, and
the artefact refuses to let that be forgotten**: upstream `CURRICULUM-SO1a` is itself
**`GATE FAIL`** with rows `{"PATCHED": "PASS", "SHIPPED": "GATE FAIL"}` — the shipped toolchain
failed the FD band at a single point **on this very case** (`curriculum_SO1a/RESULTS.md` §1).

> *"the two-row structure exists so the PATCHED row can carry work the SHIPPED row cannot — it does
> NOT erase the SHIPPED reading."*

And downstream, the artefact's own note: *"the SHIPPED `GATE FAIL` travels with every claim SO-3aR2
makes; the ruling calls the incompressible ground `verified` and the record is narrower than that
word."* **SO-3's `PASS` inherits this**, and SO-3's `G-PROV` refuses to publish without it.

---

## 9. WHAT THIS ITEM ESTABLISHES, AND WHAT IT DOES NOT

**`capability_grid_cell`**, quoted from the artefact:

> *"2D · steady · incompressible — gradients computed + FD-verified. This item moves ONLY that
> column, and adds the ALPHA-MULTIPOINT WEIGHTED-OBJECTIVE gradient dJ/d(shape) with J = SUM_i w_i
> CD_i, which no record in this lab had FD-verified. NOTHING about Mach, an optimum, or np != 1."*

**It does NOT establish:** anything about an **optimum** — `G-NOOPT` measured zero optimiser markers
across 4 artefacts and 5 logs, and no optimiser ran. Anything at **np ≠ 1** — a gradient verified at
one np is a statement about that np (`DAFOAM_CHARTER.md` §5). Anything about **Mach** — `DASimpleFoam`
has no equation of state and no speed of sound, and **no number in this file may be quoted as a
compressibility result.** Anything about α outside [3.139°, 7.139°], or about stall. Anything about
the four unregistered `shape` components. Anything about **any other item's pins or run
directories** — the census swept this item's eleven sources and no others, and the registration
names that wider sweep as **owed**, not done.

**And it establishes nothing about a sub-percent gradient.** §0's floor caveat is part of the
result, not a footnote to it.

---

## 10. WHERE THE RECORD LIVES

| record | path |
|---|---|
| frozen registration | `cases/dafoam/ladder-a/A1/curriculum_SO3aR2/PREREGISTRATION.md` (`181fd627`) |
| grading instrument | `cases/dafoam/ladder-a/A1/curriculum_SO3aR2/so3ar2_grade.py` (md5 `c81a09a90950cb1610f40a91b29cdabe`) |
| **grade artefact** | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/SO3aR2_grade_20260831T230221Z.json` |
| grade stdout, stop marker | same directory: `SO3aR2_grade_20260831T230221Z.out`, `SO3aR2_STOP_MARKER.json` |
| cost, rc, digests, `.so` md5s | same directory: `ledger.txt`, `STATUS.chain`, `STATUS.{MESH,X-S,F-S,X-P,F-P}` |
| planted-control artefacts | same directory: `grader_controls/` |
| initial-condition census | same directory: `{F,X}-{S,P}_IC0.json` |
| standing verdict table | `docs/dafoam/README.md` §3 — **two rows, already landed at `36df34f0`** |
| case index | `cases/dafoam/INDEX.md`, Addendum 2026-09-02 |
| cost calibration | `docs/COST_CALIBRATION.md` row `C-20260831T230621.613076Z-d360c175` |

---

*Nothing in this item has been filed, sent, emailed, uploaded, registered, posted or commented
outside this box. **SUBMISSIONS PARKED.***
