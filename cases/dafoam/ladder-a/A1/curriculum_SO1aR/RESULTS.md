# CURRICULUM SO-1aR — RESULTS: the re-grade produced a verdict where zero gates had been evaluated

**Dated 2026-08-28.** Lane: dafoam `lab-lane` (X). Supervisor: `dafoam-supervisor`, who approved the run after his personal check-1 read of the diff.
Pre-registration frozen at **`bf5aec13fe28a24cdd7dc6e5b72747712415ad93`**. Subject: SO-1a's preserved run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7). SUBMISSIONS PARKED.

---

## 1. THE GRADING PATH WAS VERIFIED BEFORE IT RAN (rule 2)

`so1ar_grade.py` md5 **`d2051f59089f3e71ae0fbfa315c3b784`**, checked **three ways** immediately before the run — worktree, the freeze commit `bf5aec13`, and `HEAD` — **all identical, and all equal to the md5 registered in `PREREGISTRATION.md` §7.** **The file that ran IS the file that was frozen.** No frozen SO-1a file was edited; SO-1a's `NOT A RESULT` stands on the record.

## 2. THE BIRTH GATE OPENED — `BORN`, 12 legs, 12 born

`graded()` ran `birth(root)` before `grade()` was reached. Result on the real artefacts: **`BORN`, 12 of 12 legs, 0 unborn.** The record is embedded in the output JSON under `"birth"`.

**`B3` is recorded in the output as NOT BORN and BARRED**, exactly as registered: `inspect_file_fallback`'s producer is `docker inspect`, undriveable without a container, and all 53 `.inspect.txt` files on this box record exit 0, so no real non-zero record exists to birth it from. Its leg passed **only** by proving the fallback is never reached on this root — every one of the five arms carries a ledger row, and `completion.arms[*].source` reads `ledger_row` for all five. **No graded number on this record came through an unborn reader.**

## 3. THE VERDICT

> # SO-1aR: **`GATE FAIL`**
> **SHIPPED row `GATE FAIL` · PATCHED row `PASS`**

**`rc = 0`.** No refusal. **Where SO-1a evaluated ZERO gates, SO-1aR evaluated all of them.** A repaired reader that turns a refusal into a `GATE FAIL` has done its job exactly as well as one that turns it into a `PASS`; the value bought here is that **a verdict exists at all**, and that it is the verdict the physics supports.

### 3.1 THE GATE TABLE

| gate | verdict | number | artifact |
|---|---|---|---|
| **G-BIRTH** | **BORN** | 12 legs, 12 born, 1 reader named NOT BORN and barred | `SO1aR_grade_20260828T171830Z.json` → `birth` |
| **G1** completion | **PASS** | all five rule-4 clauses PASS on all five arms: C1 rc value, C2 terminal marker, C3 artefact present, C4 age guard, C5 no fatal token | → `rule4_clauses_per_arm` |
| **G-M2** mesh identity | **PASS** | cells = **4,032**, exactly as registered | → `mesh_cells` |
| **G5_SHIPPED** (CD) | **GATE FAIL** | 5 graded, **3 PASS, 2 GATE FAIL, 1 sign flip**; aggregate **40.4814 %** vs band E 5.0 % | → `gates.G5_SHIPPED.G5_CD` |
| **G5c_SHIPPED** (CL) | **GATE FAIL** | 5 graded, **4 PASS, 1 GATE FAIL**, 0 sign flips; aggregate **4.3270 %** — *inside* band E, and the row still fails on band D | → `gates.G5_SHIPPED.G5c_CL` |
| **G5_PATCHED** (CD) | **PASS** | **5 of 5**, 0 sign flips; aggregate **0.0623 %** | → `gates.G5_PATCHED.G5_CD` |
| **G5c_PATCHED** (CL) | **PASS** | **5 of 5**, 0 sign flips; aggregate **0.0212 %** | → `gates.G5_PATCHED.G5c_CL` |
| **G-TB** SHIPPED | **PASS** | **0 of 5** components pass band D at the deliberately wrong step (max allowed 1) | → `gates.G_TB_SHIPPED` |
| **G-TB** PATCHED | **PASS** | **0 of 5** at the wrong step | → `gates.G_TB_PATCHED` |
| **G6** duality | **NOT MEASURED** | the tutorial exposes no dot-product test; named, never composed | → `gates.G6_dot_product_duality` |
| **G9** toolchain | **PASS** | both rows by DIGEST + printed `.so` md5 + in-artefact `.so` md5. **No version string** | → `gates.G9_toolchain` |
| **G10** caps | **PASS** | every row under its cap; total **9.416** ≤ **75.0** | → `gates.G10_caps` |
| **G12** placement | **PASS** | `cpuset = 9` on every row | → `gates.G12_placement` |
| GCI | **NOT QUOTED** | *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"* | → `no_gci` |

### 3.2 THE BRIGHT LINE, PER COMPONENT (`rel_err_pct`, adjoint vs the central-FD reference; band D = 5.0 %)

| component | SHIPPED `dCD/dx` | SHIPPED `dCL/dx` | PATCHED `dCD/dx` | PATCHED `dCL/dx` |
|---|---|---|---|---|
| `shape[0]` | **11.933 % — GATE FAIL** | 0.338 % PASS | 0.012 % PASS | 0.005 % PASS |
| `shape[3]` | 4.050 % PASS | 0.593 % PASS | 0.042 % PASS | 0.009 % PASS |
| `shape[6]` | **637.757 % — GATE FAIL, SIGN FLIPPED** | **19.803 % — GATE FAIL** | 0.699 % PASS | 0.088 % PASS |
| `shape[7]` | 1.880 % PASS | 0.931 % PASS | 0.145 % PASS | 0.017 % PASS |
| `patchV[1]` | 0.014 % PASS | 0.012 % PASS | 0.014 % PASS | 0.012 % PASS |
| **aggregate (band E)** | **40.481 %** | 4.327 % | **0.062 %** | **0.021 %** |

**Baselines, identical on both rows to every printed digit:** `CD = 0.02091051000679216`, `CL = 0.49876526415423195`; primal repeatability `eta = 3.714203840321506e-10`.

## 4. WHAT THIS BUYS THAT NO A1 RECORD HELD BEFORE

**`dCL/dx` — the EQUALITY-CONSTRAINT gradient — is FD-verified on A1 for the first time.** SO-1 is drag-min at **fixed lift**; `CL` is an equality constraint (`so1a_runScript.py:174`), so `dCL/dx` is what carries the constraint into an optimiser. Prior A1 records (`reverify_patched_idwarp_np1/RESULTS.md` @ `be35dcad`, D13 @ `15767999`) verified **`dCD/dx` alone**. The PATCHED row now carries **`dCL/dx` PASS 5 of 5 at 0.0212 % aggregate**, and **the SHIPPED row is shown to fail it** (`shape[6]`, 19.803 %). **A gradient rung that verifies only the objective cannot support a constrained optimisation; that gap is now closed for the PATCHED row and demonstrated open for the SHIPPED one.**

**The trivial baseline earns the gate.** `DAFOAM_CHARTER.md` §4 requires an FD gate to name and buy a baseline chosen to be wrong. At `h = 1e-8` (`shape`) and `1e-6` (`patchV`), **0 of 5 components pass band D on either row** — errors 32.8 % to 106.2 %, three of them sign-flipped. The comparator's own words: *"the trivial baseline FAILS as registered, so the FD gate is measuring the step."* **The gate can fail, so its PASS means something.** D15, D16 and D17 named no trivial baseline at all.

## 5. THE MECHANISM, DECOMPOSED (D7R attribution: no number quoted before its mechanism is named)

Shipped-vs-patched divergence on the **adjoint** `dCD/dx`, **reported and never gated**:

| component | shipped | patched | divergence |
|---|---|---|---|
| `shape[0]` | −0.0113416458 | −0.0101337920 | 10.650 % |
| `shape[3]` | +0.0123801630 | +0.0128972850 | 4.010 % |
| `shape[6]` | **+0.0056907374** | **−0.0010656352** | **118.726 % — the sign is opposite** |
| `shape[7]` | +0.0034668080 | +0.0035281045 | 1.737 % |
| `patchV[1]` | +0.0024104814 | +0.0024104814 | **0.000 %** |

> **`patchV[1]` diverges by EXACTLY ZERO — the two toolchains agree to every printed digit — while all four `shape` components diverge.** `patchV` is the aerodynamic operating point (|U|, angle of attack); it perturbs the **boundary condition**, not the mesh, so it **never passes through IDWarp's warping path**. The `shape` DVs do. **The defect is localised to the mesh-warping path and is not a global adjoint error**, and that is shown by a control the case bought for free rather than argued from the code. This is a **mechanism**, not an improvement percentage, and no optimisation gain is claimed anywhere in this record.

**Two honest caveats on the SHIPPED row, stated rather than left to be found:**

1. **`shape[3]` PASSES at 4.0498 % against a 5.0 % band — 0.95 percentage points from failing.** Counting it as "3 of 5 pass" without that number would flatter the shipped toolchain.
2. **`G5c_SHIPPED`'s aggregate is 4.3270 %, INSIDE band E**, yet the row is `GATE FAIL` because `shape[6]` breaches **band D**. The aggregate alone would have passed this row. **Both bands are required, and this run is the demonstration of why** — a single badly wrong component can hide inside a vector norm.

## 6. PREDICTIONS — SCORED, NEVER ADJUSTED

**This item's own three (`PREREGISTRATION.md` §4):**

| # | prediction | outcome |
|---|---|---|
| **R1** | G1 completion PASSES on all five arms and the verdict is **not** `NOT A RESULT` | **HIT** — G1 `PASS`, all five arms, all five clauses; verdict `GATE FAIL`. The genuinely open part (the C2 terminal markers and C3, which this lane deliberately did not read) came out clean |
| **R3** | total instrument cost ≤ **1.0 core-min** | **HIT** — **0.036 core-min**, 3.6 % of cap. §7 |
| **R4** | no G5/G5c component refused for a missing FD plateau | **HIT** — **0 refusals**; every one of the 20 component-objective readings graded (`n_graded = 5` on all four sub-gates) |

**Carried by citation from SO-1a's pre-compute freeze of 2026-08-27 — ALL TEN HIT:** `P1` cells 4032 · `P2` CL ∈ (0.45, 0.55) · `P3` CD ∈ (0.015, 0.028) · `P4` PATCHED CD 5/5 · `P5` SHIPPED `shape[6]` outside band D or flipped (**both**) · `P6` PATCHED CL aggregate ≤ 1.0 % · `P7` trivial baseline fails ≥ 4 of 5 (**5 of 5**) · `P8` total core-min ∈ (4.0, 22.0) · `P8b` MESH wall ≤ 120 s · `P9` the age datum resolves to the compressed twin on every solver arm.

> **A ten-for-ten sweep is a claim about a document written before the compute, not about this lane's cleverness.** SO-1a's author predicted the shipped toolchain's failure and the patched one's success, and both landed. **`P2` and `P3` were read by this lane before the re-grade and are disclosed in `PREREGISTRATION.md` §2.1; their evidentiary weight comes from SO-1a's 2026-08-27 freeze, not from this record.**

## 7. COST — rule 12

| line | ranks | wall | core-min | basis |
|---|---|---|---|---|
| the graded run | 1 | 0.160 s | **0.0027** | **MEASURED** |
| the birth battery inside it | — | — | included above | measured |
| instrument spend to the freeze | 1 | 1.966 s | **0.0328** | **MEASURED**, `so1ar_grade_selftest_evidence.txt` |
| **SO-1aR TOTAL** | | | **≈ 0.036** | **against a 1.0 core-min cap — 3.6 %** |
| solver compute bought by this item | | | **0.000** | no container started, no queue entry |

**Dollars: 0.036 core-min = 0.0006 core-h × $0.0513/core-h = $0.00003 — DERIVED, NOT MEASURED.** `cost_basis`: **REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing). No GPU.

**SO-1a's 9.416 core-min is NOT re-charged here.** It was spent under SO-1a and belongs to SO-1a's ledger; double-counting it would corrupt the ladder's accounting.

**The estimate-versus-actual rows are PREPARED AND NOT WRITTEN**, pending the supervisor's ruling on whether SO-1a's missing row closes here or separately. The arithmetic is in §8 so the ruling can be made against numbers.

## 8. ESTIMATE VERSUS ACTUAL — the numbers, awaiting a ruling on where they land

**This lane's recommendation: TWO ROWS, ONE TRIGGER — not one merged row.**

**Row A — SO-1a (solver compute).** Estimate from its own frozen `PREDICTED_CORE_MIN`; actual from its ledger.

| arm | predicted | actual | ratio | `max_nr_throttled` |
|---|---|---|---|---|
| MESH | 0.167 | 0.183 | 1.096 | — |
| X-S | 1.100 | 1.017 | **0.925** | 5 |
| F-S | 2.500 | 3.583 | **1.433** | **68** |
| X-P | 1.100 | 1.200 | 1.091 | 13 |
| F-P | 2.500 | 3.433 | **1.373** | **42** |
| **TOTAL** | **7.367** | **9.416** | **1.2781** | |

**Gap attribution: CONTENTION, not misprediction, and the ledger carries the evidence.** The two overruns are the FD arms, and they are exactly the two arms that ran with siblings — `F-S` beside `av2r_FAD-S`, `F-P` beside `d18_F-S` and `av2r_FAD-S` — and their throttle counts (68 and 42) are an order of magnitude above `X-S`'s 5. **`X-S`, the least contended arm, came in UNDER estimate at 0.925.** No waste is folded into this ratio; none was observed (no stalled row, no row over 3600 wall s).

**Row B — SO-1aR (instrument, read-only).** Predicted ≤ 1.0 core-min cap; actual **0.036**; ratio **0.036**. **Gap attribution: a deliberately conservative cap on a read-only instrument**, not a mispredicted workload — the cap was sized for a graded run plus repeats and the graded run cost 0.0027.

**Why two rows and not one.** Rule 12 compares *a process's* pre-registered estimate with *its own* actual. SO-1a's 9.416 core-min of solver compute and SO-1aR's 0.036 core-min of instrument time are different work in the same unit; dividing one by the other's cap would produce a number that means nothing. **But SO-1aR's completion is the right TRIGGER for SO-1a's row**: SO-1a never "completed" in rule 12's sense — it returned `NOT A RESULT` with zero gates — so this is the first moment its 9.416 core-min has a graded verdict attached to compare against. **Trigger shared, rows separate.** *Not written to `docs/COST_CALIBRATION.md` until the supervisor rules.*

## 9. WHAT THIS RECORD MAY NOT BE READ TO SAY (`PREREGISTRATION.md` §8, restated against the actual outcome)

1. **NOTHING about reproducibility.** One chain, one night. The PATCHED row's `PASS` is a statement about **that run**.
2. **NOTHING about the mesh beyond identity.** `G-M2` checked 4,032 cells against a registered number. **No mesh-convergence study exists, no Roache triple exists, and NO GCI IS QUOTED** (rule 5) — the comparator says so itself in its `no_gci` field.
3. **NOTHING about np > 1.** Every arm is np = 1. A4's measured 16,600× decomposition effect is *removed from the chain*, not shown absent.
4. **NOTHING about the launcher.** The artefacts came from SO-1a's infrastructure; this item neither re-verifies nor re-certifies it.
5. **SO-1a's verdict is not rehabilitated.** SO-1a is `NOT A RESULT` **permanently**. Two records, one run.
6. **No optimisation gain is claimed.** No optimiser ran. §5 gives a mechanism, not an improvement percentage.
7. **`GATE FAIL` is the ITEM verdict and it is NOT a failure of the PATCHED toolchain.** The item fails because the two-row rule requires both rows, and the SHIPPED row is genuinely broken. **The PATCHED row is `PASS` on both objective and constraint.**
8. **The birth battery certified READERS, not PHYSICS.** `BORN` means each reader was shown seeing a non-zero through the real path. The gates are what speak to the gradients.

## 10. THE RUN ROOT WAS NOT MUTATED — the check, named

**Method:** an aggregate `md5sum` over `md5sum` of **every file** in the run root, sorted, computed **before** the run and **after** it over the **identical file set** (excluding only the three paths SO-1aR is registered to create).

| | files | aggregate md5 |
|---|---|---|
| **before** 17:18:17Z | 337 | `073a520850452ad0acd6ba58aff2c4e3` |
| **after** the graded run | 337 | `073a520850452ad0acd6ba58aff2c4e3` |

> **IDENTICAL. Not one pre-existing byte changed.**

Added by SO-1aR, and nothing else: `SO1aR_grade_20260828T171830Z.json`, `SO1aR_grade_20260828T171830Z.out`, and `grader_controls_SO1aR/{F_S,F_P}_planted.json`. **No SO-1a file was opened for writing; SO-1a's own `grader_controls/` path does not exist and was never created** (delta 2 doing its job).

**Grader-level plant, on the real artefacts (rule 3):** `grader_plant_seen = true` on both rows, **15 values each**, worst residual **6.51e-19**. **Producer-written plant (birth leg B9):** the CTRL row reads exactly `0.617 = PLANT/(2·ctrl_step)` on both rows while its unplanted twin reads `0.0`. **The reader was shown seeing a non-zero and a zero from the same file through the same code path.**

**C5, the repaired clause, on the record it passed:** MESH scanned `MESH_20260828T021739Z_1709267.log` **and** `checkMesh.log`; **1 benign line excluded — `checkMesh.log:18`, token `Floating point exception`, reason "OpenFOAM sigFpe SETUP banner — an ENABLEMENT NOTICE, not a crash"** — printed on the PASS record, not hidden. The four solver arms: **0 exclusions, 0 sites**. **The one line that cost SO-1a 9.416 core-min is now visible in the output as a counted, reasoned exclusion.**

## 11. WHAT IS NOT DONE, AND WHOSE CALL IT IS

- **Nothing enqueued.** `verification/queue/` was not opened, read or written. D6R was live at 4 ranks throughout and was not touched; `docker ps` read 0 containers at the pre-run check.
- **No successor to SO-1b is built.** The supervisor ruled: copying or symlinking this output into SO-1a's filename inside the preserved run root is **FORBIDDEN** — that would be artefact forgery. The only legitimate route is a successor registration for SO-1b whose registered input is this JSON, **and it is not to be built until the supervisor rules on it now that a verdict exists.**
- **`docs/COST_CALIBRATION.md` is not edited**, pending §8's ruling.
- **No SO-1a, SO-1b or SO-1c frozen file was edited.**
