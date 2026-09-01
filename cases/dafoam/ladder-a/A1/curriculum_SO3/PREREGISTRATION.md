# CURRICULUM SO-3 — NACA0012 ALPHA-MULTIPOINT WEIGHTED-OBJECTIVE **OPTIMISATION**, INCOMPRESSIBLE, BOTH TOOLCHAIN ROWS, np = 1. PRE-REGISTRATION (FROZEN)

**Item id:** `CURRICULUM-SO3`
**Run root (registered, and ABSENT at the freeze):** `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation`
**Case directory (this document's own home):** `cases/dafoam/ladder-a/A1/curriculum_SO3/`
**Instrument commit:** `e1b760d9` — 19 files, 11,014 insertions.
**Freeze:** this document's own commit. Rule 2: the gate, threshold, cap and label below are committed **before** the solver starts, and §11 states the condition and how it was checked.

**Status: `PENDING`.** No arm of this item has run. Nothing here is a result.

---

## 0. WHAT IS NEW, AND THE ONE THING A READER MUST NOT TAKE FROM THIS ITEM

**New.** The predecessor rung, `CURRICULUM-SO3aR2`, FD-verified the **gradient** of the weighted multipoint objective `J = Σᵢ wᵢ·CDᵢ(αᵢ)` over one shared `shape` vector, at np = 1, on both toolchain rows. SO-3 spends that gradient: it **drives an optimiser** with it, on both rows, and then re-verifies the gradient **at the final design point** — which `DAFOAM_CHARTER.md` §9 requires and which no item in this family has ever done.

The multipoint adjoint here **runs one `DASolver` instance per operating point behind ONE SHARED `OM_DVGEOCOMP` and sums through an `om.ExecComp`** — a registered divergence from D6, which builds `geometry_<pt>` per scenario. One shared geometry is what makes the summed objective a statement about one design vector rather than three.

**THE ONE THING A READER MUST NOT TAKE FROM THIS ITEM.** Whatever drag reduction SO-3 reaches on the PATCHED row, **this item cannot support the sentence "DAFoam reduces weighted drag by X".** The admitting gradient is `GATE FAIL` on the shipped toolchain and every link of the provenance chain is `GATE FAIL` at item level (§2). The only sentence this item can license is **"on the patched toolchain `dafoam-idwarp-rot:v1`, ..."**. That restriction is enforced in code, not merely asked for: `so3_grade.py:G-PROV` **REFUSES** (exit 2) if the travelling provenance block is absent, if any chain link is not `GATE FAIL` at item level, if any link's SHIPPED row is not `GATE FAIL`, if any link has no basis, or if the composed verdict line is not byte-identical to the one function that composes it.

---

## THE TEN LINES

The ten registered choices, each one a decision that could have gone otherwise, stated where a reader will find them.

1. **The quantity graded is the weighted multipoint objective `J = Σᵢ wᵢ·CDᵢ(αᵢ)`** and the three per-scenario `CL`, on ONE shared `shape` vector — not a per-scenario `CD` and not a trimmed `CL`.
2. **Two rows, always.** SHIPPED (`dafoam/opt-packages:latest`) and PATCHED (`dafoam-idwarp-rot:v1`). A worse or failed SHIPPED optimisation **is the result**, not waste. `DAFOAM_CHARTER.md` §6.
3. **The registered DV subset is four `shape` components** — `shape` indices **0, 3, 6, 7** — SO-1a's and SO-2a's own, so the three items' readings sit on the same components. `patchV` is **not** here; line 4 removes it.
4. **Three operating points, α = 3.13918623195176 / 5.13918623195176 / 7.13918623195176 degrees, EQUAL weights 1/3.** The centre is a **quotation** from `curriculum_SO2a/so2a_runScript.py:35` — the tutorial's own trimmed angle at `CL_target = 0.5`. The ±2° bracket and the equal weights are **lane-chosen and registered as lane-chosen**, not defaults. α is this item's **operating point**, which is why `patchV` is not a design variable.
5. **np = 1 on every arm, and it is a CONDITION ON THE INHERITANCE, not a setting.** SO-3aR2's FD table — the whole reason this optimisation is admissible — was measured at np = 1, and `DAFOAM_CHARTER.md` §5 forbids carrying an FD reference across np. A4 measured a **16,600×** spread between two decompositions of one mesh (np=4 scotch 8.95 % against np=4 simple 4×1×1 0.00054 %), which is exactly what any np ≠ 1 arm would readmit. Enforced in three independent places: `so3_run_arm.sh:ranks_of`, an `MPI.Abort` in `so3_runScript.py`, and `so3_grade.py:ARM_RANKS`.
6. **`CL` is UNCONSTRAINED.** A registered choice, and the reason is that SO-3aR2 verified the gradient **at fixed α**; adding a `CL` equality would add N constraints and N extra DVs and change the quantity whose gradient was verified. The only constraints are geometric (`thickcon` ∈ [0.5, 3.0], `volcon` ≥ 1.0, `rcon` ≥ 0.8), unchanged from `so2a_runScript.py:151-155`. **Consequence, registered here so no reader has to ask for it: the `CL` baseline/final pair travels with EVERY drag number this item publishes** (`so3_runScript.py:619` writes `CL_baseline` and `CL_final` into `so3_O.json`). A weighted-drag reduction at an unstated `CL` is not a reportable number.
7. **Band D = 5.0 % per graded PAIR; band E = 5.0 % aggregate vector-relative PER ROW; plateau tolerance 10.0 %, proved PER PAIR and never asserted once for the item; MIN_GRADED_PAIRS = 3** — a row with fewer than three graded pairs is `NOT A RESULT`. These are **inherited by citation** from SO-3aR2, never re-derived by a lane that has seen an answer.
8. **The optimiser is IPOPT, `MAX_MAJORS = 50`, `OPT_TOL = 1.0e-5`.** 50 is derived from measurement: the nearest sibling on this exact case, `CURRICULUM-SO1bR-a1-naca0012-dragmin-opt`, converged in **12 majors** on both rows with `EXIT: Optimal Solution Found.`, and `CURRICULUM-D1-a1-constrained-opt/armO` in **12**. `MAX_MAJORS` is a **budget, not a settle criterion**; reaching it is `GATE REACHED`, never `PASS`.
9. **Seven declared arms** — `MESH`, `O-S`, `XE-S`, `FE-S`, `O-P`, `XE-P`, `FE-P` — with the §9 endpoint FD **built into the chain**, not deferred to a successor item.
10. **The planted-zero control is sized RELATIVE to the band it must cross**, `PLANT_K = 3.0`, and is proved sufficient by being driven **insufficient** at `PLANT_K_INSUFF = 0.2`. §4.

---

## 1. THE ITEM, AND WHAT MAKES IT ADMISSIBLE

Seven arms, in chain order, all at np = 1, all in a 12 GiB cgroup on cpuset 14.

| arm | row | kind | what it does | artefact | terminal statement |
|---|---|---|---|---|---|
| `MESH` | SHIPPED | SCRIPT | `preProcessing.sh && checkMesh` — mesh generation. No solve, no optimiser, no adjoint. | `checkMesh.log` | — |
| `O-S` | SHIPPED | SOLVER | the IPOPT multipoint optimisation | `so3_O.json` | `SO3_O_WRITTEN` |
| `XE-S` | SHIPPED | SOLVER | the **adjoint** gradient at the SHIPPED optimum | `so3_X.json` | `SO3_X_WRITTEN` |
| `FE-S` | SHIPPED | SOLVER | the **finite-difference** table at the SHIPPED optimum | `so3_F.json` | `SO3_F_WRITTEN` |
| `O-P` | PATCHED | SOLVER | the IPOPT multipoint optimisation | `so3_O.json` | `SO3_O_WRITTEN` |
| `XE-P` | PATCHED | SOLVER | the **adjoint** gradient at the PATCHED optimum | `so3_X.json` | `SO3_X_WRITTEN` |
| `FE-P` | PATCHED | SOLVER | the **finite-difference** table at the PATCHED optimum | `so3_F.json` | `SO3_F_WRITTEN` |

**Why the endpoint arms exist, in the charter's own reason and not a generic one.** `DAFOAM_CHARTER.md` §9: *"a gradient verified at iteration 0 is not verified at iteration 47"*, and the stated mechanism is this toolchain — the IDWarp `getRotationMatrix3d` degenerate-rotation branch is **guaranteed to fire at the undeformed baseline** (`axisMag = 1e-15 < tol = sqrt(eps)`), and its second regime D-A2 behaves differently just **above** the threshold. SO-3aR2's PATCHED `PASS` was **measured at iteration 0 only**. `XE-*` and `FE-*` are what close that gap, and closing it is the point of the item.

**`BOTH ROWS RUN.** On SO-3aR2's measured arm costs the shipped side is the cheaper one, so the charter's two-row verdict is close to free. A worse or failed SHIPPED optimisation IS the result. Registered here so that nobody later reads a shipped-row failure as a wasted arm.

---

## 2. `G-PROV` — THE TRAVELLING SHIPPED `GATE FAIL`

**Limb 1 — the chain, and every link travels.**

| link | relation | item verdict | SHIPPED row | PATCHED row | basis |
|---|---|---|---|---|---|
| `CURRICULUM-SO3aR2` | **DIRECT** — SO-3's optimisation is admissible only because SO-3aR2 FD-verified the multipoint objective's gradient at np = 1 | **`GATE FAIL`** | **`GATE FAIL`**, `G5J` aggregate **31.498325840045588 %**, 2 of 4 pairs `GATE FAIL` | `PASS`, `G5J` aggregate **2.6779490823450605 %** | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/SO3aR2_grade_20260831T230221Z.json` → `gates.G5J.SHIPPED.G5J_objective` |
| `CURRICULUM-SO1a` | **INHERITED** — carried in SO-3aR2's own `upstream_provenance` | **`GATE FAIL`** | **`GATE FAIL`** on the FD band at a single point on this very case | `PASS` | `cases/dafoam/ladder-a/A1/curriculum_SO1a/RESULTS.md` §1 |

Both basis paths were **read on disk at this freeze** and both exist. The SO-3aR2 grade artefact was opened and its verdict, rows and both aggregates re-read from it; the values in the table above are those bytes, not a recollection.

**On the SHIPPED toolchain the multipoint objective gradient missed the 5 % band by more than 6× on this very case.** That is what travels.

**Why it travels, and it is not a formality.** The two-row structure exists so the PATCHED row can carry work the SHIPPED row cannot. **It does not erase the SHIPPED reading.** `so3_grade.py` refuses to publish a verdict at all unless the chain is present, complete, and every link's item verdict and SHIPPED row read `GATE FAIL`; and the human-readable provenance line is compared **byte for byte** against the single function that composes it, so a line mangled in transit is a refusal and not a silently shortened sentence.

**Limb 2 — this item's duty to ITS successor: the stop marker.** `so3_stop_marker.sh` is written on **every** exit path, including refusal and abort, and is read by the successor **by absolute path**. It carries the item verdict, the row verdicts and the literal `G5J` key. An item that stops without telling its successor why has made its successor re-buy the finding.

### 2a. THE HARNESS FLOOR IS PUBLISHED, NEVER GATED — AND IT IS ON THIS DOCUMENT'S FACE

`VERIFICATION_CHARTER.md` §7 step 4, verbatim: *"The harness-sound floor on this stack, for a case with no flagged components, is 2.5 to 5 percent vector-norm relative error. A number below that is a claim about the harness."*

**SO-3aR2's PATCHED `G5J` aggregate is 2.6779490823450605 % against a 5.0 % band.** Its margin to the floor's **lower** edge is **+0.177949 percentage points**; it sits at **1.0712×** that lower edge; its label is **`INSIDE_HARNESS_FLOOR_INTERVAL`**.

**In plain words, on the face of this registration: the patched gradient this item spends passes essentially ON the harness floor.** It must **never** be described as a sub-percent verification, a 0.1 % verification, or a tight one. The margin, the fraction and the label are computed and published beside **every** aggregate this item produces (`so3_grade.py:floor_margin`), and the reading is **REPORTED, NEVER GATED** — turning it into a gate would convert an honest caveat into a `GATE FAIL` the charter does not authorise.

---

## 3. GATES, THRESHOLDS AND LABELS — FROZEN NOW

**The vocabulary is the six tokens and nothing else:** `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`. `so3_grade.py` refuses on any composed verdict outside that set.

| gate | what it reads | threshold | verdict on miss |
|---|---|---|---|
| `G1_completion` | rc = 0, terminal statement present, no fatal token, **age guard** | all of it, per arm | `GATE FAIL` |
| `G-M2_mesh_identity` | mesh cell count | **4032** exactly | `GATE FAIL` |
| `G-ALPHA_operating_points` | the three α read back through the scenario groups | equal to the registered α to `1.0e-12` absolute | `GATE FAIL` |
| `G5J_objective` (per row) | aggregate vector-relative FD error on `J`, plateau proved per pair | **band E ≤ 5.0 %**, **≥ 3 graded pairs** | `GATE FAIL`; fewer than 3 pairs → `NOT A RESULT` |
| `G5C_lift_per_scenario` | the three `CL` per scenario, same rule | **band D ≤ 5.0 %** per pair | `GATE FAIL` |
| `G_MP_STRUCT_assembly_identity` | that `∂J/∂x` equals `Σᵢ wᵢ ∂CDᵢ/∂x` from the artefact's own components | relative `1.0e-10` | `GATE FAIL` |
| `G_TB_trivial_baseline` | the **same** probe at a deliberately wrong step, `h = 1e-8` | `PASS` iff **at most 1** of the 4 components passes band D there | ≥ 2 passing → that row's `G5J` is **WITHDRAWN to `NOT A RESULT`** |
| `G-NOOPT-ENDPOINT` | that no optimiser ran in `XE-*`/`FE-*` | zero optimiser evidence | `GATE FAIL` |
| `G-DESIGNPOINT` | that the endpoint arms were evaluated **at the optimum**, from `so3_xopt.json` | exact | `GATE FAIL` |
| `G-OPT9` (per row) | §9 — see §9 below | — | see §9 |
| `G-STAGES_declared_vs_executed` | **DECLARED = 7** against EXECUTED = n | — | short > 0 is a **gate input**, not a footnote |
| `G-EVALFAIL_evaluation_census` | that every declared evaluation was **written**, failures included | `EVALS_DECLARED = 34` per F arm | see §6 |
| `G9_toolchain` | image digest **and** `libidwarp.so` md5, from inside the container | exact match to §7 | `GATE FAIL` |
| `G10_caps` | per-arm core-min against its cap, and the item total against the ceiling | §4 | `GATE FAIL` |
| `G12_placement` | cpuset equals `14` | exact | `GATE FAIL` |
| `G-PROV` | the travelling chain, §2 | all limbs | **REFUSAL, exit 2** |
| `G6_dot_product_duality` | — | **NOT MEASURED** — AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on **both** images. Named, never composed. |

**`GCI` / Roache triple gating.** No grid triple is registered for this item; it is a single-grid optimisation. `CLAUDE.md` rule 5 therefore has no row to act on here, and this document says so rather than leaving a reader to infer it.

**Two readings that are REPORTED and NEVER GATED**, each with its number:
* **Primal convergence.** The real statement is `Minimal residual <r> satisfied the prescribed tolerance <tol>`. OpenFOAM's `SIMPLE: no convergence criteria found` banner is **counted separately and is not evidence** — it appears **4×** in `reference/REAL_SO1a_X-S_arm.log` on a run that **converged**, because DAFoam applies its own `primalMinResTol`. The same reference log carries **5×** `Time step continuity errors` and **1×** the real convergence statement. `trapFpe:` is an **enablement notice**, not a crash. All three exclusions are counted and named on the `PASS` record; a suppression a reader cannot see is the same defect wearing the other hat.
* **Shipped-versus-patched adjoint divergence**, worst per-component percentage and the top 20 non-zero pairs. **A divergence of 0.000 % on some component is reported with its number and is never read as "the defect is absent".**

**The age-guard datum is resolved BY EXISTENCE, never by name.** `0.orig/U` or `0.orig/U.gz` for `MESH`; `0/U` or `0/U.gz` for every solver arm. Every field at the end state must be **newer** than that datum. A guard that resolves a datum by name silently passes when the name is wrong.

**`G12`'s delivered-cores floor (1.5) is NOT COMPOSED at np = 1** and is registered here as not composed, so that nobody later reads its absence as an oversight. At np = 1 an overlapping cpuset costs wall time and could not fail `G12`; the sampler's reading is still **published as a number**.

**Item verdict composition, registered here and implemented at `so3_grade.py:2526`, in this order:**
1. `G-STAGES` = `NOT A RESULT`, or any row verdict `NOT A RESULT` → **`NOT A RESULT`**
2. `G-STAGES` = `BLOCKED` → **`BLOCKED`**
3. any row's optimiser verdict `NOT A RESULT` → **`NOT A RESULT`** (a row whose optimiser is `NOT A RESULT` cannot be rescued by any other gate)
4. `GATE FAIL` in any row verdict or in `{G-M2, G-ALPHA, G-NOOPT, G-DESIGNPOINT, G9, G10, G12}` → **`GATE FAIL`**
5. any row verdict `NOT_MEASURED` → **`NOT A RESULT`**
6. `GATE REACHED` in any row or optimiser verdict → **`GATE REACHED`**
7. otherwise → **`PASS`**

**The endpoint FD can only make things worse, never better.** An endpoint `PASS` **never** upgrades a `GATE REACHED` optimiser to `PASS`. Registered before the run so it cannot be argued after one.

---

## 4. THE REGISTERED CAP TABLE, THE EVALUATION CENSUS, AND THE PLANTED CONTROL

### 4.1 Caps are CEILINGS. Predictions are ESTIMATES. They are different numbers.

The ratio `CLAUDE.md` rule 12 asks for is taken against the **prediction**, never the cap. `MESH`'s cap is 5.0 core-min while its prediction is 0.19; conflating them would report every arm as a 26× underspend.

| arm | ranks | **cap, core-min** | in-container wall | memory cap |
|---|---|---|---|---|
| `MESH` | 1 | **5.0** | 120 s | 12g |
| `O-S` | 1 | **240.0** | 14220 s | 12g |
| `O-P` | 1 | **240.0** | 14220 s | 12g |
| `XE-S` | 1 | **15.0** | 720 s | 12g |
| `XE-P` | 1 | **15.0** | 720 s | 12g |
| `FE-S` | 1 | **40.0** | 2220 s | 12g |
| `FE-P` | 1 | **40.0** | 2220 s | 12g |

**ITEM CEILING = 595.0 core-min**, and it is `Σ(caps)` **asserted in code**, not restated by hand (`so3_grade.py:3431`, `:3519`).

**The wall column is the REPAIRED one, and the repair is the C-188 cap frame.** Every in-container wall is `floor(cap × 60 / ranks) − CAP_MARGIN_S` with `CAP_MARGIN_S = 180 s`, **not** `cap × 60 / ranks`. The 180 s host-frame margin is charged to the ceiling here so the ledger cannot record `core_min > cap` on an arm that reaches its own deadline. Under the ancestor's form `MESH`'s enforced wall would have been 300 s and a deadline-reaching arm would have recorded `(300 + 60 + 8)/60 = 6.13` core-min against a 5.0 cap — a `GATE FAIL` manufactured by the frame rather than by the run. The comment table above and the code are **both parsed** by `so3_run_arm_selftest.sh` leg (r2), which refuses if they diverge, because a comment table that contradicts its own code is what a reviewer in a hurry reads.

**An overrun STOPS the run and does not get a new budget.** `so3_run_arm.sh` reports at the cap (`D4S_CAP_CROSSED`, run continues, supervisor decides) and **hard-stops** at `CEILING = 4 × cap` (`D4S_CEILING_HIT`). Crossing a per-arm cap or the item ceiling is `G10 GATE FAIL`.

### 4.2 The evaluation census

Computed from the registered constants rather than copied as a literal, so a step or component added cannot leave a stale count in the artefact:

```
EVALS_DECLARED = 2 baselines
               + 4 components × 3 steps × 2 signs   = 24
               + 4 components × 1 wrong step × 2 signs =  8
               = 34 EVALUATIONS per F arm
```
Each evaluation is **3 primals** (three scenarios) → **102 primals per F arm**. Registered steps for `shape`: `1.0e-2, 1.0e-3, 1.0e-4`. Trivial-baseline step: `1.0e-8`. Control step: `1.0e-3`.

### 4.3 The planted-zero control, sized RELATIVE to the band it must cross

`CLAUDE.md` rule 3 is a **precondition** of the gates, not a footnote beside them. Three gates here can pass on a small or zero number — `G5J`, `G5C` and `G-MP-STRUCT` — so each is shown, at grade time, on the real artefacts, **flipping to `GATE FAIL`** under a plant read back **from disk through the same reader**.

**The form, registered at the freeze:**
```
plant_i = PLANT_K × (FD_BAND_PCT / 100) × |d_ref_i|
```
where `d_ref_i` is the **same reference the gate divides by**. The planted relative error is therefore `PLANT_K × FD_BAND_PCT` **by construction**, whatever the quantity's scale — and this comparator grades four quantities (`J` and three `CL`) whose scales differ by more than an order of magnitude.

**`PLANT_K = 3.0`**, registered here before any compute: 15 % against a 5 % band, clear of it by 3×, so a control that fails to flip is telling us about the **gate** and not about a marginal plant.

**Why this is not fitting the control to the data.** Fitting would be choosing a **threshold, a band or a label** after seeing an answer. None of those moves: band D stays 5.0 %, band E stays 5.0 %, the plateau tolerance stays 10.0 %, every label is unchanged. What is sized is the **perturbation in a negative control**, whose one job is to demonstrate the gate can fail. **The plant never touches the graded artefact** — it is written to a separate copy under `grader_controls/`, the real reading is taken from the real bytes, and the item's verdict is composed from the unplanted artefact alone.

**And it is proved sufficient by being driven INSUFFICIENT.** `PLANT_K_INSUFF = 0.2` reproduces SO-2M's geometry exactly — a plant **below** the band — and the selftest requires the flip to **fail to happen** at that K. SO-2M was lost because it inherited an absolute `PLANT = 1.234e-03` sized on a CD-scale item and applied it to a `CMZ` reference: 2.48 % of that reference against a 5 % band. **The plant could not cross its own band**, the control reported itself exercised, and it demonstrated nothing.

**The charter-4 trivial baseline** is separately registered (§3, `G-TB`): the same probe at `h = 1e-8`, five orders below the registered middle step. On a derivative of order 1e-2 the FD numerator there is ~1e-10, at or below the primal repeatability (D15 measured `eta_F = 1.30e-10` on this mesh), so the estimate is noise and **must** fail band D. **A probe that errored counts as failing the baseline** — an unevaluable estimate is not a pass.

---

## 5. RESOURCES — np, MEMORY, PLACEMENT, AND THE DECLARED PROGRAM

**Requirement 4 — the declared program is SEVEN arms**, `N_DECLARED = 7`. `G-STAGES` reads `DECLARED = 7` against `EXECUTED = n` **as a gate input**, because W3 logged 20 blocked stages of 33 perfectly, in two agreeing artefacts, and nothing read them.

**np = 1 on every arm** — line 5, and it is the condition on the inheritance.

**Memory: 12 GiB per arm**, raised from the family's 4 g convention with the arithmetic shown. D13 **measured** peak RSS **1.70 GiB** for this 4,032-cell 2-D case at np = 1; three `DASolver` instances in one process is bounded crudely above by `3 × 1.70 ≈ 5.1 GiB` plus one shared mesh/FFD/IDWarp footprint. **That bound is `[EXTRAPOLATED]` and is not a measurement — no multipoint arm has ever run on this case** — so 12 g carries better than 2× headroom over it, and **the item's own first solver arm MEASURES it**.

**Aggregate memory ceiling 30.6 GiB**, poll 30 s, bound 14400 s, in the **waiting** form: every wait is a line in `STATUS.<arm>`; at the bound the chain **stops** and names the series file. A block DISCARDS the arm's remaining budget and buys nothing, and this document says so where the guard is registered.

### 5b. REGISTERED CPU PLACEMENT — cpuset **14**, fixed at Stage 2 and disclosed here against every live sibling's registered set

`mpirun` inside a `--cpus=N` container binds rank 0 to the **first core of the host topology**. Concurrent containers then land on the same host core and throughput collapses as `1/N` **while the box reports itself idle** — measured by the D13 lane 2026-08-25: affinity = 0 on all three concurrent arms, **0.250 cores delivered against a 1.0-core quota**, host 61 % idle, throughput moved **4×** on a control that changed only the sibling count. `--cpus=4` does not hand out four distinct cores. So: **pin, and MEASURE the placement rather than infer it from the flag that was passed.**

**Registered: cpuset `14`. One core, because every arm runs at np = 1. NOT core 0.**

**The disclosure, read rather than recalled, on this 16-core box:** SO-1c holds `10` (MESH) and `10,11,12,13` (solver arms) [`so1c_run_arm.sh:172-178`]; SO-2a held `9` [`so2a_run_arm.sh:178`]. **14 is disjoint from both**, so SO-3 does not inherit the parent's disclosed overlap with D4-SHIPPED's registered `5,6,7,9`. `G12` compares the launcher's value against `so3_grade.py:CPUSET_REGISTERED`, so the two cannot drift apart silently.

---

## 6. A FAILED EVALUATION IS A GRADABLE STATE, NOT A REFUSAL — AND THE ARM LOOP IS A CENSUS

**D6 registered a chain stop as a meaningful outcome and its grader refused, exit 2, with ZERO gate readings, because an arm carried no ledger row. 2,257.933 core-min of real optimisation sat behind an instrument that could not read it (L-322).**

**SO-3's comparator prints `RAN` / `NOT RUN` per arm, grades every arm that ran, and REFUSES ONLY ON A MALFORMED ARTEFACT, NEVER ON AN ABSENT ONE.** An absent arm is a **census reading** that `G-STAGES` gates on; a malformed artefact is a refusal.

**`G-EVALFAIL`: a failed evaluation is WRITTEN, not omitted.** An evaluation that raises, times out, or returns a non-finite value is recorded as a failed evaluation with its reason and **counted against `EVALS_DECLARED = 34`**. An F arm that silently writes 33 rows and calls itself complete is the failure this gate exists to catch.

**Registered expectation, before the run: at least one evaluation failure per F arm is EXPECTED** (`P8`). At `h = 1e-8` on a primal with `eta_F ≈ 1.3e-10` some probes will not evaluate, and a census that reports zero failures is more likely to be a census that is not looking than a run that had none.

**Exit 2 on any refusal. A refusal is `NOT A RESULT`, never a degraded verdict.** And no `assert` statement appears in the comparator: `python3 -O` strips them, so an assert is not a guard (L-332). `count_asserts()` proves it, and is itself proved against a planted assert.

---

## 7. THE FROZEN INSTRUMENT TABLE — NINE ROWS, IN §18.3's ORDER

`DAFOAM_CHARTER.md` §18.3: an instrument table enumerates **every file the item EXECUTES or IMPORTS**, and **existence is asserted before any md5**. Existence and md5-agreement are different questions and the second cannot be inferred from the first at any level of agreement — not at 8 of 8, not at 800 of 800. SO-2a's §7 table read *"eight of eight AGREE"* while `so2a_aggregate_memory.py`, which its frozen driver executes by name, was **absent from the freeze commit**.

**Every md5 below was recomputed on disk at this freeze AND independently recomputed from the file's committed blob at `HEAD`; all three values — declared, on-disk, and committed — AGREE on all nine rows.**

| row | file | md5 | role |
|---|---|---|---|
| 1 | `so3_chain_driver.sh` | *(the driver itself; it holds the pins below and is not self-pinned)* | drives the seven arms in order; asserts existence of all nine **before any md5**, then every md5, before staging |
| 2 | `so3_run_arm.sh` | `e8839a2fb445239609718feed9b0aeed` | the launcher — §8 |
| 3 | `so3_xf.py` | `58fd0e2600ce6836ddd039beb8677477` | the instrument: writes every X and F record; its writers build every positive-path fixture |
| 4 | `so3_runScript.py` | `0c026d72047b605099125258e3152f93` | the producer — the in-container OpenMDAO/DAFoam model |
| 5 | `so3_grade.py` | `d786e10d81d99233610fe8c636c3a47e` | **THE GRADING PATH** — §10 |
| 6 | `so3_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | the aggregate-memory reader the driver executes inside its poll loop — **the exact file SO-2a's table omitted** |
| 7 | `so3_stall.py` | `c0719b7fad530a34391280139fe7aa6c` | the stall detector — §9 |
| 8 | `so3_age_guard.py` | `1bcbe57cb708d8e6a7a89ceb2235a35c` | the age guard |
| 9 | `so3_stop_marker.sh` | `4809ff569def1927e516685bb218e7bc` | the stop marker — §2 limb 2 |

Plus `so3_decomposeParDict`, md5 `e6f1b0060944bc86d6dff56480ad2bd4` (an OpenFOAM dictionary, not a program).

**The order is stated honestly.** The pins were set **once, at the Stage-2 amendment, for all nine together**, and not before — even though several files existed earlier and their md5s could have been written down. A pin table filled in for the files that happen to exist, inside the executable that stages every arm, would read agreement on every pin it holds while a file that launcher copies is still missing. The fail-closed sentinel `MD5_UNSET` was **deleted, not left defined**: its former value (32 zeros) is a **well-formed** md5, so a dead sentinel would be counted as a real pin by the completeness leg and would be a fail-open waiting to be re-used.

**Toolchain identity, by digest, never by tag** (`DAFOAM_CHARTER.md` §11). **Both digests were read from this box's own `docker inspect` at this freeze and match.**

| row | image | image digest | `libidwarp.so` md5 |
|---|---|---|---|
| PATCHED | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |
| SHIPPED | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |

**The row is read from the toolchain's own identity, never from a flag.** `so3_runScript.py` computes the md5 of the `libidwarp.so` **this interpreter actually imported**, from inside the container, and maps it to a row. **An md5 matching neither registered toolchain REFUSES**: this producer will not stamp a row it cannot prove. A `-row PATCHED` flag would let a mislabelled launch stamp the wrong row into the artefact the endpoint arm then reads, and that is the SO-1c failure in its most expensive position.

### 7.1 THE §18.3 EXTRACTION, RUN AT THIS FREEZE

The charter's §18.3 call site — *extract every `$HERE/`-style path reference and every local import from the frozen file set and resolve each against the item directory* — **is declared NOT BUILT in the charter.** It was run by hand at this freeze. **24 local dependency names appear in the frozen code. All nine pinned files, plus `so3_decomposeParDict`, exist on disk and in the freeze tree. Four referenced names do not exist, and all four are accounted for:**

* `so3_cmd.sh` — written **at runtime** by the launcher into the arm's work directory. Not an instrument.
* `so3_xf_mut.py` — a mutant written **at runtime** into a temp directory by `so3_xf_selftest.py`. Not an instrument.
* `so3_groot5_selftest.sh` and `so3_collision_leg.py` — **DELIBERATELY NOT DERIVED**, and declared as such with reasons in `so3_pin_census.py:149-161`. See §15 residual R4 for the one thing wrong with that, stated at its true size.

**No registered gate's implementing file is absent.**

---

## 8. THE LAUNCHER'S OWN PIN

`so3_run_arm.sh`, md5 **`e8839a2fb445239609718feed9b0aeed`**, frozen here and asserted by `so3_chain_driver.sh` before staging.

**`G-ROOT.1`:** `BASE` must resolve — through `realpath -m`, so a trailing slash, a `.`, a `..` or a symlink cannot walk around it — to **this item's registered run root**. Anything else aborts at rc = 3 **before any staging**. The launcher's staging path begins `rm -rf "$WORK"`; `d4_run_arm.sh` hardcoded another item's root and would have deleted **5,085 files, 384 MB, holding `OptView.hst` and `opt_IPOPT.txt` — the artefacts D4's accepted `GATE REACHED` rests on**.

**`G-ROOT.2`** names, explicitly, the roots this file must never write, so the abort says **whose** evidence it just protected. `so3_run_arm_selftest.sh` leg (r6) drives every entry against the disk and prints `GHOST` beside the ones that are not there, so the next derivation inherits a **measurement** instead of a claim. The honest size of `G-ROOT.2` is stated in the launcher itself and is repeated here: **every one of those roots is already refused at `G-ROOT.1`; `G-ROOT.2` is a second line of defence that cannot fire while `G-ROOT.1` stands, and none of it closed a live hole.** What a stale list costs is real but smaller — a refusal message naming a directory that does not exist says the wrong thing on the day `G-ROOT.1` is weakened.

**`ALREADY_BOUGHT`.** A second invocation against an arm already bought is refused at rc = 3. Two records for one run is the defect, and this guard stops it. It is not a theoretical guard: it **fired** during the incident in §16.

---

## 9. THE OPTIMISER MAPPING AND THE STALL ABORT

### 9.1 The mapping — `DAFOAM_CHARTER.md` §9, per row

> `PASS` **only** where the optimiser itself printed a convergence statement against its **own** tolerance.

* Optimiser printed its own convergence statement → eligible for **`PASS`**.
* Stopped by a wall clock, an iteration cap, a budget, or the registered stall abort → **`GATE REACHED`** where the registered intermediate threshold was met, **`NOT A RESULT`** otherwise.
* **Never `PASS`, and never described by the size of the improvement it reached.**

**The registered intermediate threshold: ≥ 5.0 % weighted-drag reduction against the run's own baseline, over at least 5 majors.** A run of fewer than 5 majors has not searched.

**The standing example this rule is made of.** A2's `opt_IPOPT.txt`: a genuine IPOPT 3.13.5 / MUMPS / L-BFGS run, `tol = 1e-5`, `max_iter = 100`, **47 majors in a 60-minute box**, drag reduced **28.275488 %** at matched `CL ≈ 0.5`. **IPOPT printed no `EXIT` line and no convergence statement anywhere in the log; the table simply stops after iteration 47.** The 28 % is `GATE REACHED`. **A row whose optimiser is `NOT A RESULT` cannot be rescued by any other gate**, and that is checked directly in the composition (§3 step 3) as a belt to the row composition's braces.

### 9.2 The stall abort — TWO conditions, calibrated on 33 real IPOPT logs, and ONE OF THEM HAS NEVER FIRED

**Condition A** — **8 consecutive majors** with `alpha_pr < 1.0e-3`.
**Condition B** — dual infeasibility (`inf_du`) **non-decreasing** over **8 consecutive majors**, with a relative tolerance of `1.0e-12` against the window's first value so that floating-point noise in a genuinely decreasing series cannot read as "non-decreasing".

**Calibration, MEASURED over 33 gradable IPOPT logs on this box:**

* **Condition A fires on exactly 2** — both the known D6 stalls — **and on NONE of the 7 that ended `Maximum Number of Iterations Exceeded`. A cap is not a stall**, and the detector distinguishes them.
* **Condition B fires on 0 of 33 and is registered `NOT EXERCISED`.** It is **never** reported as a passing control. This registration corrects the brief it was built from: *"dual infeasibility worsening"* was assumed to be a monotone claim and **it is not** — on C-188's own artefact `inf_du` goes `5.71e-03 → 1.14e-03`, a **5× improvement**, on a run that genuinely stalled. **Condition A carries the entire load.** A control that has never been able to fire is reported as not exercised, following the shape of `DAFOAM_CHARTER.md` §18.5 — and §18.5 is a **PROPOSAL, NOT ENACTED**, which is stated here rather than cited as though it were law.

### 9.3 THE STALL STOP IS THE **FIRST REACH** OF THE WINDOW, AND THE DEFINITION IS REGISTERED EXPLICITLY

The abort fires at the **first** major at which an 8-major window is complete — **not** at the end of the longest run of stalled majors.

**Measured at this freeze on `/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint/O_mp/opt_IPOPT.txt`:**

| reading | value |
|---|---|
| table rows parsed | **65** (IPOPT `iter` labels `0`–`64`) |
| **first reach** of the 8-major window | closes at the **35th row**, IPOPT `iter` label **34** |
| end of the **longest** stalled run (17 majors) | the **61st row**, IPOPT `iter` label **60** |
| majors saved by stopping at first reach | **30 of 65 = 46.2 %** by row count; **31 of 65 = 47.7 %** by `iter` label |
| majors saved by stopping at the longest run's end | **4 of 65 = 6.2 %** by row count; **5 of 65 = 7.7 %** by `iter` label |

**A watchdog built on "the longest run" would not have stopped until major 60 and would have saved 6 %, not 46 %.** The two readings in each row differ only by IPOPT's 0-based `iter` labelling against a 1-based row count; **both are given because a single number here would be the ambiguity this section exists to remove.**

**Registered cost of the stall branch:** a stalled O arm costs `≈ 34 × 2.061 = 70.1` core-min, **below** the converging prediction of 103.0 — so **the stall branch is a floor on the saving, not an extra cost**, and the cap is sized on the converging branch (§12).

### 9.4 A CORRECTION TO THE RECORD: THE CUTBACK COUNT, WITH ITS DEFINITION

`so3_stall.py:12,41,71` quotes **"545 line-search cutbacks"** from `C-188`. **That figure does not reproduce, and this document supplies the correct one WITH its definition, which the original quotation lacked.**

**Measured at this freeze, by `so3_stall.py`'s own parser, on `CURRICULUM-D6-a2-wing-multipoint/O_mp/opt_IPOPT.txt`:**

| definition | value |
|---|---|
| majors parsed | **65** |
| restoration majors | **7** — reproduces **exactly** |
| `Σ(ls)` over all majors | **611** |
| **`Σ max(0, ls − 1)` over all majors** | **547** ← the module's own `cumulative_line_search_cutbacks` |
| `Σ max(0, ls − 1)` over non-restoration majors only | **450** |
| `Σ(ls)` over non-restoration majors only | **507** |
| count of majors with `ls > 1`, all / non-restoration | **48** / **44** |

**The correct figure under the module's own definition is 547, not 545, and 545 is not reachable under any of the six definitions above.** `so3_stall.py:71` already records that the count does not reproduce; this document supplies the number.

**The deeper defect, and it is the transferable one: the record quotes a cutback COUNT WITH NO DEFINITION, and six plausible definitions give six different numbers.** Wherever this figure is cited in future, **it is cited with its definition or it is not cited.** The frozen `C-188` row is **not edited**; the correction lives here.

---

## 10. THE GRADING PATH

**`so3_grade.py`, md5 `d786e10d81d99233610fe8c636c3a47e`.**

**Verified three ways at this freeze**, because a pin that was not verified is a pin that is being guessed at, and this family lost SO-2MR's first arm to md5 pins that were stale the instant a rename ran:

1. recomputed on disk → `d786e10d81d99233610fe8c636c3a47e`
2. recomputed from the **committed blob at `HEAD`** → `d786e10d81d99233610fe8c636c3a47e`
3. recomputed from the **committed blob at the instrument commit `e1b760d9`** → `d786e10d81d99233610fe8c636c3a47e`

**All three agree**, and `so3_chain_driver.sh:MD5_GRADER` asserts the same value with `md5sum -c` before staging any arm.

**The freeze sha is deliberately not written into the comparator.** SO-3a's copy of that line cited its own Stage-1 freeze commit because there the document was frozen **before** its instruments existed. SO-3 freezes the document **after** the instruments, so no sha exists at the moment the comparator is written and a sha written there could only be wrong or back-dated. **The binding runs the other way and is checkable today: this section pins the file by md5, and the driver asserts it.**

**The schema contract with the already-frozen consumers is checkable and is DRIVEN.** On 2026-08-31 SO-1c refused because its consumer read `gates` at the top level while its producer wrote them at `grade.gates`, and a 51-leg suite could not see it **because the suite's fixtures were hand-built from the consumer's own expectations** — a tautology on schema. Here `--out` is **mandatory** (the frozen driver invokes `--out $GRADE_OUT`; the parent comparator composes its own stamped path and would have written to an address the driver never looks at), and `verdict` and `rows` sit at the **top level** with the **literal** key `gates["G5J"]`, because `so3_stop_marker.sh:97,101,105` reads them there. The selftest **runs the real stop marker on a real grade artefact this comparator wrote**, then **renames the key** and requires the marker to report it absent. **A schema contract that cannot fail is not a contract.**

**No key is ever found by a recursive hunt.** Every nested location is an explicit tuple path; a reader that goes looking until it finds something will always find something.

---

## 11. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED — WITH A POSITIVE CONTROL

**The condition: this item's registered run root does not exist, and no arm of this item has run.**

**How it was checked at this freeze, and the check was shown able to see the other answer** (rule 3 applied to the checker, not to a comparator):

| probe | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation` | positive control: `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient` |
|---|---|---|
| existence test | **ABSENT** | **EXISTS** |
| `ls -d` on the literal path | `No such file or directory` | resolved and listed |
| `ls -d` on the glob `CURRICULUM-SO3-*` | `No such file or directory` | — |

**The same reader, in the same invocation, returned `EXISTS` for a directory that does exist and `ABSENT` for this one.** A zero from a reader not shown able to see a non-zero is not evidence, and that applies to an absence check as much as to a comparator.

**Every path, directory and artefact name cited in this document was verified to exist on disk at this freeze**, except those explicitly named as run outputs that must **not** yet exist (`so3_O.json`, `so3_X.json`, `so3_F.json`, `so3_xopt.json`, `checkMesh.log`, `ledger.txt`, `SO3_grade_*.json`, `SO3_STOP_MARKER.json`) and those explicitly named as ghosts (§7.1, §15 R4). Every inherited name was treated as guilty until checked — this family found a falsified citation **three generations deep** on 2026-09-01, a run root that no ancestor ever protected while a comment described it as one of *"four roots that DO exist, and hold real evidence"*.

**The cold-start requirement, registered explicitly.** The item's own guard must **refuse a run root that is not absent**. The run root is free (§16), and it must still be free when the first arm launches. A directory left in place from any source — including the quarantined accident of §16 — makes the age guard's datum older than the run that is supposed to have produced the answer, which is the exact failure mode `CLAUDE.md` rule 4's age guard exists to catch.

---

## 12. COST

**Unit: core-minutes** (wall s × ranks ÷ 60). Not wall time and not dollars.

### 12.1 The point prediction, and how much of it is measured

| arm | predicted, core-min | basis |
|---|---|---|
| `MESH` | **0.19** | MEASURED — family precedent on this case |
| `O-S` | **103.0** | **EXTRAPOLATED — see 12.2** |
| `O-P` | **103.0** | **EXTRAPOLATED — see 12.2** |
| `XE-S` | **3.7** | MEASURED — SO-3aR2's own X arm |
| `XE-P` | **3.7** | MEASURED — SO-3aR2's own X arm |
| `FE-S` | **7.5** | MEASURED — SO-3aR2's own F arm |
| `FE-P` | **7.5** | MEASURED — SO-3aR2's own F arm |
| **item point** | **228.59** | |
| **item, both O arms stalled** | **162.79** | the stall branch is a **floor on the saving** |
| **ITEM HARD CEILING** | **595.0** | `Σ(caps)`, asserted in code |

**Dollars are DERIVED, NOT MEASURED**, at **c7a.4xlarge $0.0513/core-h**, **reported-by-owner** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Point **$0.19544**; ceiling **$0.50872**. Both under the $25 pre-authorisation, **and the item is still costed here, because a blanket is not a per-item reading** (`CLAUDE.md` rule 9).

### 12.2 THE O-ARM FIGURE IS AN EXTRAPOLATION, AND IT IS LABELLED ONE

```
0.42127          core-min/major   [MEASURED]  C-24, D1 arm O, on THIS A1 case at np = 1, over 11 majors
      × 3        scenarios        [MODEL]     the naive multipoint multiplier
      × 1.6308                    [MEASURED]  C-188, D6, 3-scenario multipoint at np = 4:
                                              31.258 core-min/major measured against 19.167 registered
                                              — the row's own conclusion: "the ×3 model is short by 63 %"
= 2.0610         core-min/major   [EXTRAPOLATED]
× MAX_MAJORS 50
= 103.05 → 103.0 core-min/arm     [EXTRAPOLATED]
```

**Both anchors are measured; the PRODUCT IS AN EXTRAPOLATION and is tagged `[EXTRAPOLATED]`, not `[MEASURED]`.** The two anchors come from different cases, different dimensionalities and different rank counts — `C-24` is A1 2-D at np = 1, `C-188` is A2 3-D at np = 4 — and the `1.6308` factor is being carried across that gap. `C-188`'s own calibration lesson is that **the anchor is the predictor, not the factor**, and D6R re-anchored on the measured multipoint major and came in inside 1.1 %. **No measured multipoint-major anchor exists for A1 at np = 1, and this item's own O arm is the first thing that would produce one.** The registered cap of 240.0 core-min carries **2.33×** over the extrapolated point precisely because the point is an extrapolation.

**An overrun STOPS the run and does not get a new budget** (`CLAUDE.md` rule 12).

### 12.3 Calibration at completion is owed, and this is where it goes

At this item's completion — every arm graded, verdict composed — the comparison of predicted against actual lands as a row in **`docs/COST_CALIBRATION.md`** under that file's append rules and the rule-10 private-index protocol. `so3_grade.py:g_caps` computes `ratio_actual_over_predicted` **per arm against `PREDICTED_CORE_MIN`, never against the cap**, and publishes the `cost_basis` string and the derived dollar figure with its not-measured label. **The report is incomplete without that row.** The **0.167 core-min of §16 is WASTE, named separately, and is NEVER folded into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

---

## 13. PREDICTIONS — SCORED `HIT`/`MISS` BY THE COMPARATOR, NEVER ADJUSTED

**A prediction token's name must not imply a narrower claim than the token scores.** That rule is registered here because this family has already been bitten by its violation, and — see 13.2 — **it is violated by this item's own frozen comparator, which this document declares rather than conceals.**

| token | **everything it scores** | registered prediction |
|---|---|---|
| `P1_cells_4032` | `G-M2` verdict is `PASS` | **HIT** |
| `P2_CL_at_alpha0_in_band` | baseline `CL` at α₀ = 5.13918623195176° lies in **[0.45, 0.55]** | **HIT** |
| `P3_CD_monotone_increasing_in_alpha` | baseline `CD` strictly increasing across the three α | **HIT** |
| `P4_G_MP_STRUCT_PASS_all_components` | `G-MP-STRUCT` is `PASS` on **every row that ran** | **HIT** |
| `P5_PATCHED_G5J_PASS_4_of_4` | **THREE conjuncts:** (i) PATCHED `G5J` verdict `PASS`, **AND** (ii) `n_graded_pairs == 4`, **AND** (iii) aggregate **≤ 1.0 %** | **MISS** — see 13.1 |
| `P6_SHIPPED_G5J_GATE_FAIL` | SHIPPED `G5J` verdict is `GATE FAIL` | **HIT** |
| `P7_G_TB_PASS_at_the_wrong_step` | PATCHED `G-TB` is `PASS`, i.e. **at most 1** of 4 components passes band D at `h = 1e-8` | **HIT** |
| `P8_P_EVAL_at_least_one_evaluation_fails_per_F_arm` | per F arm: `evaluations_failed ≥ 1` | **HIT** on both F arms |
| `P9_plateau_holds_at_the_WING_angles` | per row, at scenarios 0 and 2: **≥ 3** pairs are not `NO_PLATEAU` | **HIT** |
| `P_COST_total_core_min_in_band` | item total core-min lies in **[14.0, 60.0]** | **MISS BY CONSTRUCTION — see 13.3** |

**The registered outcome, written before any container starts.** The **SHIPPED** row is expected to reach `GATE REACHED` or `GATE FAIL`; the **PATCHED** row is expected to reach **`GATE REACHED`** (IPOPT is expected to converge in well under 50 majors on the single-point precedent of 12, but §9's bar is the optimiser's own printed statement and this lane does not predict that it will print one on a multipoint problem it has never run); and the **item verdict is registered as `GATE REACHED`**, with `GATE FAIL` fully admissible. **A predicted `GATE REACHED` is REGISTERED, not avoided.**

### 13.1 `P5` — RECONCILED, AND THE NAMING DEFECT IS NAMED

SO-3aR2's §13 states `P5` as **three conjuncts** — *"PATCHED row `G5J` `PASS`, 4 of 4 pairs inside band D, aggregate ≤ 1.0 %"* — and its grader scores all three. Its measured outcome: verdict `PASS`, **4 of 4 pairs**, aggregate **2.6779 %**. **The third conjunct missed. `P5` is a `MISS`, and the grader is correct — there is no grader defect.**

**But the token name `P5_PATCHED_G5J_PASS_4_of_4` reads as though it scores only the pair count, and it does not.** Two readings are therefore forbidden, in both directions:

* **Nobody may quote "4 of 4 as predicted" off a `MISS`.** The pair count is one conjunct of three.
* **Nobody may read "`P5` MISS" as meaning the pairs failed.** They did not; **4 of 4** passed band D.

### 13.2 THE NAMING DEFECT IS REPRODUCED IN THIS ITEM'S OWN FROZEN COMPARATOR, AND IT IS DECLARED HERE

`so3_grade.py` carries the token under the **same name**, `P5_PATCHED_G5J_PASS_4_of_4`, scoring the **same three conjuncts** against `PRED["P5_patched_agg_max_pct"] = 1.0`. The comparator's md5 is pinned (§10) and cannot be edited without breaking that pin and the driver's assertion, so **the name is frozen as it stands**. The mitigation registered here is the table in §13: **every token is registered with EVERYTHING it scores, spelled out, so that no reader has to infer the conjuncts from the name.** That is a documentation mitigation, not a repair, and it is labelled as one.

### 13.3 `P_COST` CANNOT HIT ON THE FULL-CHAIN PATH, AND THAT IS REGISTERED BEFORE COMPUTE RATHER THAN EXPLAINED AFTERWARDS

`so3_grade.py:PRED["P_COST_band"] = (14.0, 60.0)` core-min. **This band is byte-identical to SO-3aR2's**, whose predicted total was **21.99** core-min and whose measured total was **14.318** — squarely inside it, `HIT`. **It was carried across a derivation that added two 103.0-core-min optimiser arms and was not re-derived.**

**This item's own registered point prediction is 228.59 core-min — 3.81× the band's upper edge.** On the intended path, where all seven arms run and `G-STAGES` reports no shortfall, `P_COST_total_core_min_in_band` therefore reads **`MISS` with certainty**, and it reads `NOT MEASURED` on any path where an arm does not run or does not report a `core_min`. **There is no reachable path on which it reads `HIT`.**

**Registered consequences, before any compute:**

1. `P_COST` is a **KNOWN-MISS token**. Its `MISS` **carries no information about this item's cost** and may never be reported as a cost overrun, a misprediction, or a calibration signal.
2. **`P_COST` gates nothing.** Predictions are scored, never composed into the verdict (§3). The item verdict is unaffected.
3. **This item's real estimate-versus-actual comparison is §12.3's** — `g_caps`'s per-arm `ratio_actual_over_predicted` against `PREDICTED_CORE_MIN`, which is correct and is the number that reaches `docs/COST_CALIBRATION.md`.
4. **The cap gate is unaffected**: `G10` compares against `CAPS` and `ITEM_CEILING_CORE_MIN = 595.0`, not against this band.

**This is registered as a defect found at the freeze, not as a design choice.** It is the `P5` shape one layer down — a token whose name reads as a live cost check while it is, on this item, decided in advance. Repairing it means editing `so3_grade.py`, which changes its md5 and requires re-pinning `so3_chain_driver.sh` and re-issuing §7 and §10 — legal under rule 2 **only while no compute has happened**, which is the state at this freeze. **That decision is the supervisor's, and it must be taken before the first arm launches.** If it is taken, this document is superseded by a new freeze, not amended after a run.

---

## 14. WHAT THIS ITEM WILL NOT ESTABLISH

* **It will not establish that "DAFoam reduces weighted drag by X".** §2. Only *"on the patched toolchain `dafoam-idwarp-rot:v1`, ..."*.
* **It will not establish a sub-percent gradient verification.** §2a. The admitting aggregate sits inside the harness floor.
* **It will not establish anything at np ≠ 1.** Line 5. A4 measured a 16,600× decomposition spread; nothing here speaks to np > 1.
* **It will not establish a dot-product duality check.** `G6` is **NOT MEASURED**: AV-2 measured that seeding forward mode makes the primal **FAIL** on this exact case on **both** images. Named, never composed.
* **It will not establish that the IDWarp defect is absent from any component.** A shipped-vs-patched divergence of 0.000 % is reported with its number and is never read as absence.
* **It will not establish a grid-converged optimum.** No grid triple; no GCI.
* **It will not establish a trimmed-`CL` result.** `CL` is unconstrained (line 6); the `CL` pair travels with every drag number precisely so that this limit is visible on every surface.
* **It will not re-establish anything SO-3aR2 already graded.** `P-COLL` and the per-point `run_directory` repair are inherited unchanged and are not re-proved.

---

## 15. NAMED RESIDUALS — WHAT COULD NOT BE VERIFIED AT THIS FREEZE

Each is named rather than papered over. None is a reason not to freeze; each is a reason not to over-claim.

* **R1 — NO ARM HAS RUN.** Every gate in this document is driven against **fixtures plus four real IPOPT logs and two real OpenFOAM reference logs**. **Nothing in the suite is validated against a real SO-3 artefact**, because none exists. The fixtures are built by the instrument's **own writers** (`so3_xf.build_X_record`, `build_F_record`, `build_fd_row`, `build_ctrl_row`) rather than from a reader's expectations, which removes the SO-1c tautology but does **not** substitute for a real artefact.
* **R2 — THE PRODUCER CANNOT BE EXECUTED ON THIS HOST.** `so3_runScript.py` needs `mphys`, `dafoam`, `pygeo` and `idwarp`, none of which are importable outside the containers. Its selftest drives the **header exec-path** and the **AST**; **it does NOT prove the model builds in-container.** Consequently **the `O` record is the one artefact in the suite not written by its own producer's code** during the drive. The first `O-S` arm is the first real test of the producer.
* **R3 — `so3_repin.sh` WAS NOT ITSELF RE-DRIVEN AFTER IT RAN.** The pins it wrote were independently re-verified at this freeze against disk **and** against the committed blobs (§7, §10) — nine of nine agree — but the **script** has not been re-driven since its own execution.
* **R4 — THREE COMMENT SITES CITE A DRIVER THAT DOES NOT EXIST HERE, AND THE FINDING IS SMALLER THAN IT LOOKS.** `so3_run_arm.sh:440` (*"`so3_groot5_selftest.sh` **now** parses both and refuses if they diverge"*), `so3_xf.py:125-126` and `so3_chain_driver.sh:83` name `so3_groot5_selftest.sh` in the present tense. **That file is deliberately NOT derived** and is declared so, with a reason, in `so3_pin_census.py:149`. **The work those sentences describe IS driven — by other files**: the cap-table comment-versus-code parse by `so3_run_arm_selftest.sh` leg **(r2)**, the producer-pin check by `so3_xf_selftest.py` leg **(A5)**, and the `RUN_DIRS` totality invariant by `so3_runScript_selftest.py` leg **(p3)**. **No registered gate is unimplemented and no check is missing; three comments name the wrong driver.** Stated at its true size rather than its most alarming one — which is the same discipline `G-ROOT.2` applies to itself.
* **R5 — `G-ROOT.2` NAMES FIVE DIRECTORIES THAT DO NOT EXIST; THE LAUNCHER'S PROSE ENUMERATES THREE OF THEM.** Measured at this freeze: `CURRICULUM-SO3F-…`, `CURRICULUM-SO1b-a1-naca0012-dragmin-opt` and `CURRICULUM-SO1c-a1-naca0012-postopt` are named as ghosts in the launcher's own comment and are confirmed absent. **`CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin` and `CURRICULUM-D14-a2-wing-remesh` are ALSO absent and are NOT named as ghosts in that comment.** Leg (r6) drives every entry against the disk and will print `GHOST` beside all five, so the measurement is available; the prose is two entries behind it. **Cost: none to safety** — `G-ROOT.1` refuses all of them first — **and the same to the refusal message as the three already named.**
* **R6 — `DAFOAM_CHARTER.md` §18.5 IS A PROPOSAL, NOT ENACTED.** The `NOT EXERCISED` handling of stall condition B (§9.2) follows its **shape**. This document does not cite it as binding law and does not claim compliance with a clause that is not in force.
* **R7 — THE SUITE'S "327 DRIVEN CHECKS" DOES NOT REPRODUCE, AND THIS DOCUMENT DOES NOT REPEAT IT.** No file in the suite prints a total, and no counting rule tried at this freeze yields 327. **What was measured, each with its definition:** `unit(` call sites = **154** (`so3_grade.py` 98 + `so3_grade_selftest.py` 56); `chk(` call sites = **35**; shell `ok` legs = **24** (12 + 12); `ok(`-style calls inside `so3_stall.py` and `so3_age_guard.py` = **45**; **all five forms summed = 261**; distinct `U`-numbered ids across the suite = **86**, highest `U`-id = **102**. **This is precisely the §9.4 defect — a count quoted without its definition — so the counts above are given only with theirs, and no headline figure is adopted.**

---

## 16. A FENCE BREACH THAT TOUCHED THIS ITEM'S RUN ROOT, REGISTERED HONESTLY

**What happened, self-reported by the instrument lane.** `so3_chain_driver_selftest.sh` leg (c8) drives the chain driver to prove the md5 assertion refuses at rc = 4. It was written and driven while every pin still held the fail-closed sentinel, so the driver aborted **above** `mkdir -p "$BASE"`, and the leg's docstring said so. **Then `so3_repin.sh` set the pins.** The same leg, unchanged, sailed past the md5 gate, staged **this item's real run root**, and executed the `MESH` arm inside the SHIPPED container.

**The claim was true when it was written and was not re-checked after the thing it described changed** — the same failure class this item is built to catch, committed in a test file, an hour after the census that exists to catch it.

**What actually ran, from the ledger row:** `ARM=MESH ROW=SHIPPED rc=0 wall_s=10 ranks=1 core_min=0.167 cap_core_min=5.0`, SHIPPED digest, SHIPPED `libidwarp.so` md5. **`MESH` is `preProcessing.sh && checkMesh` — no solver, no optimiser, no adjoint. NO SOLVER ARM RAN.**

**THE RULING, REGISTERED:**

1. **The output is QUARANTINED, NOT DELETED**, at `/home/ubuntu/certonomous-runs/QUARANTINE-SO3-selftest-accidental-launch-20260901T0242Z/`, with a `WHAT_THIS_IS.txt` naming exactly what it is. Nothing was destroyed.
2. **Its two grade objects — `SO3_grade_20260901T024251Z.json` and `SO3_grade_20260901T024259Z.json` — read `NOT A RESULT`** (declared = 7, executed = 1 and 0). **They are NOT this item's verdict and may NEVER be cited as one.** They are the comparator behaving correctly on a truncated program, and they are evidence of that and of nothing else.
3. **The run root is FREE**, verified absent at this freeze against a positive control (§11), **so the item can still cold-start** — and §11's cold-start requirement is registered so that it must still be free at launch.
4. **The 0.167 core-min is WASTE.** It is named separately, priced at **$0.00014 DERIVED, not measured**, and **is never folded into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). It is **not** part of this item's 228.59 core-min prediction and **not** part of any actual/predicted figure this item reports.

**Two things the accident MEASURED**, reported because they are measurements and not consolations: (i) the **C-188 cap-frame repair is now measured in production**, not only in a selftest — the ledger row reads `cap_core_min=5.0 enforced_wall_s=120 enforced_core_min=5.000000`, where the ancestor's form would have given 300 s and recorded 6.13 core-min against a 5.0 cap; and (ii) **the `ALREADY_BOUGHT` guard FIRED** — the second invocation was refused at rc = 3 with `chain=REFUSED_ALREADY_BOUGHT arm=MESH`. Two records for one run is the defect, and the guard stopped it.

---

## 17. FREEZE

**Frozen at this document's own commit.** From this commit forward:

* **Before first compute**, amendments are legal and **must state the condition and how it was checked**, naming the run directory that does not exist — as §11 does.
* **After first compute**, the gates, thresholds, caps and labels above are **closed**. Changes land only as **dated addenda** that cannot alter a gate, a threshold, a cap or a label. Originals are **struck, never rewritten**.
* **The grading path is fixed at this commit**: `so3_grade.py`, md5 `d786e10d81d99233610fe8c636c3a47e`, verified against its committed blob at both `HEAD` and `e1b760d9` (§10).
* **Nothing is filed, sent, posted, uploaded, registered or commented upstream by any agent, ever.** `CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10. **SUBMISSIONS ARE PARKED.**

**Not cleared to launch by this document.** This is a freeze, not an authorisation. The supervisor's pre-registration-committed check and instrument-diff check come first, and §13.3 puts one decision in front of the first arm.

---

## AMENDMENT 1 — 2026-09-01, BEFORE FIRST COMPUTE. R8: THE DRIVEN REFERENCE BYTES ARE NOT IN THE FREEZE TREE, AND `.gitignore` IS WHY

**lines whose number changed above this section: 0.** This section is appended at the foot; nothing above it is edited.

**The rule-2 condition, and how it was checked, at the moment of this amendment.** No compute has happened. The registered run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation` **does not exist** — re-asserted in the same shell invocation as this amendment's commit, against the same positive control as §11. **No gate, threshold, cap or label is altered by this amendment**; it adds a named residual, which §15 exists to hold.

**What was measured, after this document's first commit, by comparing the case directory on disk against the freeze tree rather than by reading a manifest:**

| file | on disk | in the freeze tree | why |
|---|---|---|---|
| `reference/REAL_SO1a_X-S_arm.log` | **yes** | **NO** | excluded by `.gitignore:270`, pattern `cases/dafoam/**/*.log` |
| `reference/REAL_SO1a_MESH_checkMesh.log` | **yes** | **NO** | same pattern |
| `so3_xf_drive_evidence.txt` | **yes** | **NO** | not ignored — simply never committed |

**R8 — THE HONEST SIZE, AND IT IS SMALLER THAN IT LOOKS IN ONE DIRECTION AND EXACTLY AS LARGE AS IT LOOKS IN THE OTHER.**

**It does not block the run, and that was checked in the code rather than assumed.** `REFDIR`, `REAL_CHECKMESH` and `REAL_ARMLOG` are module-level **path joins** at `so3_grade.py:2648-2650`; they open nothing. The only three sites that **open** those files are `_fix()` at `:2815` and `:2820` and `selftest()` at `:3304`, all reachable only under `--selftest` (`:3527`). **The grading path — `main()` against a real run root — never reads `reference/`.** The item can cold-start, run and grade from a clean checkout of the freeze commit. **No registered gate is unimplemented and §7.1's finding stands unchanged.**

**What it does cost, and this half is not smaller than it looks.** **`--selftest` cannot be re-driven from a clean checkout of the freeze commit**, because the bytes it drives against are excluded from version control by a repository-wide pattern. And the banner-discriminator readings this document publishes as measurements in §3 — **4×** `SIMPLE: no convergence criteria found`, **5×** `Time step continuity errors`, **1×** the real `Minimal residual … satisfied the prescribed tolerance` statement, all on a run that **converged** — cite `reference/REAL_SO1a_X-S_arm.log`, **an artefact that lives only on this box's disk with nothing in git protecting it.** A number whose artefact is gone is not a result, and these two artefacts are one `rm` from gone.

**This is `gitignored is not filed` in its exact form:** a completeness check that asks git is blind to precisely the files the ignore rule hides, and §7.1's §18.3 extraction — which resolved every dependency **against the freeze tree** — reported `HEAD=N` for `reference` and this lane did not chase it until after the freeze. **Recording that the check saw it and the reader did not is the point.**

**Registered disposition, and no part of it is taken by this lane:**
1. **The two reference logs and `so3_xf_drive_evidence.txt` are NOT swept into this document's commit.** They are the instrument lane's artefacts, and committing another lane's uncommitted work under cover of one's own path is the L-423 failure. **Landing them is a dispatch, not a side effect**, and it needs a decision about `.gitignore:270` that is above this lane.
2. **Until they are in a tree, §3's banner counts are labelled here as `MEASURED, ARTEFACT NOT IN THE FREEZE TREE`** — they are true readings of real bytes and they are not reproducible from the freeze commit alone.
3. **Nothing about the launch decision changes.** The item was not cleared to launch before this amendment and is not cleared by it.

---

## AMENDMENT 2 — 2026-09-01, BEFORE FIRST COMPUTE. `P_COST`'s BAND IS RE-DERIVED, AND THE GRADING PATH IS RE-PINNED TO md5 `0ac111ef144a62111e36f676e8114af1`

**lines whose number changed above this section: 0.** Appended at the foot; nothing above is edited.

**THE RULE-2 CONDITION, AND HOW IT WAS CHECKED.** No compute has happened. **The registered run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation` DOES NOT EXIST** — re-asserted in the same shell invocation as this amendment's commit, against the same positive control as §11 (`CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient`, which the same reader returns as **EXISTS**). The freeze window is open and **closes at the first arm**.

**Authority.** Supervisor ruling, 2026-09-01, on §13.3's finding.

### A2.1 WHAT MOVED, AND THE PROOF THAT NOTHING ELSE DID

**One value: `so3_grade.py:PRED["P_COST_band"]`, from `(14.0, 60.0)` to `(60.0, 300.0)`.**

**PROVED, not asserted.** The full diff of `so3_grade.py` against its previous committed blob, filtered to **non-comment, non-blank lines**, is exactly two lines — one removed, one added:

```
<         "P_COST_band": (14.0, 60.0)}
>         "P_COST_band": (60.0, 300.0)}
```

Re-read from the amended module after the edit: `CAPS` unchanged and `ITEM_CEILING_CORE_MIN = 595.0 = Σ(CAPS)`; `FD_BAND_PCT = 5.0`, `AGG_BAND_PCT = 5.0`, `PLATEAU_TOL_PCT = 10.0`, `MIN_GRADED_PAIRS = 3`, `PLANT_K = 3.0`, `TB_MAX_PASSING = 1`, `CPUSET_REGISTERED = "14"`, `Σ PREDICTED_CORE_MIN = 228.59` — **all unchanged. NO GATE, THRESHOLD, CAP OR LABEL MOVES.** `P_COST` gates nothing: predictions are scored, never composed into the verdict (§3).

### A2.2 THE NEW BAND, DERIVED FROM THE COST MODEL RATHER THAN DRAWN AROUND THE POINT

**A band that cannot MISS is exactly as useless as one that cannot HIT, and it is the easier mistake to make once the point estimate is known.** The band is therefore derived from the cost model's own uncertainty and its edges are placed **between** named scenarios, not on top of any.

The five non-O arms are **MEASURED** and total **22.59** core-min (`MESH` 0.19 + `XE` 3.7×2 + `FE` 7.5×2). The entire uncertainty is `2 × (majors × per-major rate)`:

| scenario | majors/arm | rate, core-min/major | **item total** | in band? |
|---|---|---|---|---|
| **S1** — C-24 × 3 only, **without** C-188's 1.6308 transfer factor | 12 | 1.2638 | **52.92** | **OUT (low)** |
| **S2** — registered rate; SO1bR **and** D1 `armO` both converged in **12** majors on this very case | 12 | 2.0610 | **72.05** | in |
| **S3** — twice the single-point precedent | 24 | 2.0610 | **121.52** | in |
| **S4** — the stall abort's **first reach** (§9.3) | 34 | 2.0610 | **162.74** | in |
| **S5** — `MAX_MAJORS`; **THE REGISTERED POINT** | 50 | 2.0610 | **228.69** | in |
| **S6** — the 1.6308 transfer factor is **itself** short by its own margin (D6 is A2/3-D/np=4; this is A1/2-D/np=1, and C-188's own lesson is that **the anchor is the predictor, not the factor**) | 50 | 3.3611 | **358.70** | **OUT (high)** |
| **S7** — both O arms stopped at their 240.0 cap | — | — | **502.59** | **OUT (high)** |

**REGISTERED BAND: `P_COST_total_core_min_in_band` = [60.0, 300.0] core-min.** It contains S2–S5 and excludes S1 below and S6/S7 above. The registered point 228.69 sits at 70 % of the band's width — **not centred, deliberately**, because the downside (an optimiser converging at the single-point precedent of 12 majors) is the better-evidenced tail. The item ceiling of 595.0 lies outside the band, **as it must: a cap is not a prediction.**

**WHAT FALSIFIES IT, REGISTERED BEFORE THE RUN.** A graded item total **below 60.0** core-min — both optimisers converging in far fewer majors than the single-point precedent, or a per-major rate well under the C-24 anchor — **or above 300.0** — the multipoint penalty failing to transfer from D6 and being short again. **Both are plausible outcomes of this run**, which is precisely the property `(14.0, 60.0)` lacked.

**What the token scores, spelled out (the P5 lesson applied).** `P_COST_total_core_min_in_band` scores **ONE conjunct** — `60.0 ≤ g10["total_core_min"] ≤ 300.0` — behind **one measurability guard**: it reads `NOT MEASURED` if any run arm reported no `core_min` or if `G-STAGES` reports a shortfall. **The name claims exactly that and nothing narrower or wider**, so no reader has to infer a hidden conjunct from it. The frozen comparator's `P5_PATCHED_G5J_PASS_4_of_4` **cannot** be given the same treatment — renaming it breaks its own md5 pin — so that one remains the **documentation mitigation** of §13.2, still labelled as one.

**§13.3 IS SUPERSEDED BY THIS SECTION.** Its finding stands as the record of why the repair happened; its registration of `P_COST` as a KNOWN-MISS token is **STRUCK** and replaced by the band above.

### A2.3 THE RE-PIN — AND THE OLD PIN IS SHOWN TO FAIL CLOSED

Editing `so3_grade.py` **rewrote the very bytes every declaration of its md5 pins**, so every such declaration was stale the instant the file was saved. That is what cost SO-2MR its first arm.

**Sites audited, by `git grep` over tracked files:** the literal `d786e10d81d99233610fe8c636c3a47e` appears in **one** executable pin site — `so3_chain_driver.sh:85`, `MD5_GRADER` — and nowhere else in code. `so3_pin_census.py:196` declares the pin **by role** (`"so3_chain_driver.sh:MD5_GRADER": ("LOCAL", "so3_grade.py")`) and holds no literal, so it re-derives at arming time and needed no edit. **That is the census working as designed.**

| | value |
|---|---|
| **STRUCK** | `d786e10d81d99233610fe8c636c3a47e` |
| **NEW GRADING PATH md5** | **`0ac111ef144a62111e36f676e8114af1`** |

**Verified three ways, as §10's original pin was:** recomputed **on disk**; recomputed from the **committed blob at `HEAD`**; recomputed from the **committed blob at this amendment's own freeze commit**. All three agree — the readings are in this amendment's commit message and were taken in the commit's own shell invocation.

**And the assertion was exercised in both directions, on the real bytes, through the driver's own mechanism** (`echo "$MD5_GRADER  $GRADER" | md5sum -c -`):
* the **new** pin → `so3_grade.py: OK`
* the **struck** pin → `WARNING: 1 computed checksum did NOT match` — **it fails closed, as it must.** A pin shown able to pass but never shown able to fail is not a control.
* the **other eight** pins → all `OK`, unaffected.

**§7 row 5 and §10 are SUPERSEDED as to the md5 value only.** Everything else those sections state — the role, the driver's assertion, the deliberate absence of a freeze sha inside the comparator, the schema contract — stands unchanged. **A reader of §7 or §10 must carry the value from this section, not from there.**

### A2.4 THE REFERENCE EVIDENCE IS NOW BACKED BY A COMMITTED ARTEFACT

Residual **R8** (Amendment 1) is **partly closed**, and the part that is not closed is named.

**`.gitignore:270` (`cases/dafoam/**/*.log`) IS NOT CHANGED.** It is a lab-wide rule and this family does not widen it for its own convenience — that call is above this item.

**`cases/dafoam/ladder-a/A1/curriculum_SO3/reference/REFERENCE_EVIDENCE_MANIFEST.md` is committed** and carries each reference log's path, byte count, line count, md5 and sha256, plus **every extracted value §3 relies on**, measured by `so3_grade.py`'s own compiled regexes and reader functions — imported and called, never re-implemented, because a manifest that re-implements the reader it documents can agree with itself while disagreeing with the instrument.

**What that does and does not achieve.** It does **not** preserve the logs; if they were lost, `--selftest` would still be un-drivable. What it achieves is that the loss becomes **detectable** and the affected published numbers become **nameable**. That is smaller than preservation and is described as such rather than as a fix.

**A third finding came out of measuring for it, and it is registered here.** `so3_grade.py`'s docstring (III) presents **three** benign per-line exclusions as measured against these reference bytes. **`trapFpe:` appears ZERO times in `REAL_SO1a_X-S_arm.log`.** Two of the three are demonstrated on those bytes; **the third is not.** Nothing depends on it having fired — `trapFpe:` genuinely is an enablement notice, not a report that the handler fired — and what is corrected is the impression that all three counts came from the same file. **§3's `trapFpe:` exclusion is therefore registered as IMPLEMENTED AND REGISTERED, NOT DEMONSTRATED ON THE REFERENCE BYTES.**

### A2.5 STATUS AFTER THIS AMENDMENT

**Still not cleared to launch.** This amendment repairs a prediction and re-pins a hash; it authorises nothing. The run root is absent, the freeze window is open, and it closes at the first arm.

### A2.6 SUPERSEDED-HASH INDEX — EVERY LINE IN THIS DOCUMENT THAT STILL CARRIES THE STRUCK md5

**Why this exists.** Rule 6 forbids editing above an amendment, so §7 row 5, §10 and §17 still **spell** the superseded grading-path hash in the body, with the correction here at the foot. **A heading is not enough, because the realistic reader is a `grep`.** This index makes any grep of the struck value land on the correction.

**THE STRUCK VALUE, SPELLED ONCE:** `d786e10d81d99233610fe8c636c3a47e`
**THE GRADING PATH IS:** **`0ac111ef144a62111e36f676e8114af1`** (§A2.3)

**Swept, not assumed.** The supervisor's instruction was to sweep rather than assume two sites. **There are EIGHT occurrences, not two** — a flat reading of "§7 row 5 and §10" would have missed four of the six stale ones.

| line | section | occurrence | status |
|---|---|---|---|
| **234** | §7, instrument table **row 5** | the pinned value in the table a reader takes the pin from | **SUPERSEDED — read `0ac111ef…`** |
| **343** | §10 opening | *"`so3_grade.py`, md5 …"* — the single most load-bearing statement in the document | **SUPERSEDED — read `0ac111ef…`** |
| **347** | §10 verification list, item 1 | *recomputed on disk* | **SUPERSEDED** — a true record of the check performed at the **original** freeze, and no longer the current value |
| **348** | §10 verification list, item 2 | *from the committed blob at `HEAD`* | **SUPERSEDED** — same |
| **349** | §10 verification list, item 3 | *from the committed blob at `e1b760d9`* | **SUPERSEDED** — same |
| **526** | §17 FREEZE | *"the grading path is fixed at this commit"* | **SUPERSEDED — read `0ac111ef…`** |
| **611** | §A2.3 | the literal quoted as the object of the pin-site audit | **CORRECT IN CONTEXT** — this is the amendment describing the struck value |
| **615** | §A2.3 | the `STRUCK` table row | **CORRECT IN CONTEXT** |
| **this section** | §A2.6 | the struck value spelled once, above | **CORRECT IN CONTEXT** — the landing point |

**SIX SITES ARE SUPERSEDED (234, 343, 347, 348, 349, 526). TWO ARE CORRECT IN CONTEXT (611, 615), plus this section's own.**

**Why the line numbers stay true, and it is checked rather than asserted.** Every amendment to this document is **appended at the foot**, which shifts no line above it; and rule 6 forbids editing above an amendment at all. So these numbers are stable by the same rule that created the problem they index. **They were re-swept AFTER this section was appended and all eight are unchanged** — because the failure this whole item is built to catch is a claim that was true when written and was never re-checked after the thing it described changed (§16), and an index of line numbers is exactly the kind of claim that rots silently.

**Two occurrences outside this document, for a reader grepping the repository rather than the file:**
* `so3_chain_driver.sh:88` — the `STRUCK:` comment beside the live pin. **CORRECT IN CONTEXT**; the live assignment is at `:91` and carries `0ac111ef144a62111e36f676e8114af1`. **No executable path can reach the struck value.**
* `docs/LAB_STATE.md:4807` — **SUPERSEDED and outside this item's territory.** It is the supervisor's board and the cross-session handoff channel; a lane does not edit it. Flagged to the supervisor, because a stale grading-path pin on the only channel other sessions inherit from is precisely what gets re-inherited.
