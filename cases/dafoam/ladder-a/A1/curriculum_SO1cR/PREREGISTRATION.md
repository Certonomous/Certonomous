# CURRICULUM SO-1cR — np-INVARIANCE OF THE A1 NACA0012 GRADIENT **AT SO-1b's OPTIMUM**, ACROSS THE DECOMPOSITION **METHOD** AT FIXED np = 4, WITH THIS CONFIGURATION'S OWN FD TABLE BESIDE IT, ON TWO TOOLCHAIN ROWS — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-31**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

<!-- SO1CR-CAP-MANIFEST v1 MESH=5.0 Ns-P=30.0 Ni-P=30.0 Ns-S=30.0 Ni-S=30.0 CEILING=125.0 RANKS_N=4 -->

**THIS IS A SUCCESSOR ITEM, NOT AN AMENDMENT.** SO-1c has had first compute. **Its gates are closed, its documents are not rewritten, and its item verdict stands as `NOT A RESULT`.** §0a below states what SO-1c returned, in this lane's own words, and carries its refusal verbatim. SO-1cR is registered fresh, before any compute of its own, and **no record here presents SO-1cR's answer as if it were SO-1c's first answer.**

**The order this item answers, verbatim from Sanaa's standing directives of 2026-08-27T16:54Z** (`git show HEAD:etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`, §4):

> ### dafoam — SHAPE-OPTIMIZATION LADDER (pull in order when queue drains)
> Pattern per case: FD-verified gradient rung -> optimization rung ->
> post-optimum verification (re-solve at optimum, constraints checked,
> np-invariance spot row) -> D7R attribution rule: no improvement % quoted
> before its mechanism is decomposed (shape vs AoA vs operating point).
> After you are done with all the current optimization cases:
> - SO-1 NACA0012 subsonic drag-min at fixed lift; then RAE2822 transonic.
> - SO-2 Constraint families on SO-1: thickness/area/volume, lift equality,
>   moment cap — one per rung.

**THIS ITEM IS RUNG 3 OF 4 FOR SO-1, AND IT IS NOT SO-2.** The scope finding SO-1c recorded is carried across unchanged: Sanaa's §4 names SO-2 as the constraint-families ladder item, and the post-optimum verification rung is a rung *within* SO-1's per-case pattern. SO-1b's own frozen document and queue entry call it **SO-1c**; this document is that item's successor and takes the name **SO-1cR** by the family's established pattern (SO-1a → SO-1aR, SO-1b → SO-1bR, AV-1 → AV-1R).

Every decision here is `[lab-attributed]`. Permission for the detached launch: Sanaa's own words boarded at **`bc0e687e`**; queue-first order `7def3c6b` / `73eccb1b` / `0b041d1a`; L-342 field classes `d4d0c29d`; R-RC approved in the directives file above (§0).

---

## 0a. WHAT SO-1c RETURNED, WHY, AND WHY THIS ITEM EXISTS — SAID FIRST AND IN THIS LANE'S OWN WORDS

**SO-1c's ITEM VERDICT IS `NOT A RESULT`. IT IS NOT RE-GRADED HERE, NOT REINTERPRETED, AND NOT CONVERTED INTO ANYTHING ELSE.** SO-1cR does not lift it, does not supersede it as a reading of what SO-1c measured, and does not claim SO-1c's compute.

SO-1c launched at **2026-08-31T17:08:42Z** (pid 177042, 4 ranks) and **stopped at its second arm 176 s later**:

* **`MESH` rc = 0.** Mesh generated in the SHIPPED image. **0.633 core-min MEASURED** at ranks = 1, wall 38 s — read from the run root's own ledger row, `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv/ledger.txt`.
* **`Ns-P` rc = 5, aborting in PREFLIGHT with NO CONTAINER STARTED.** The launcher printed, verbatim:

  > `G-OPTDEP artefact row 'P' != this arm row 'PATCHED'`
  > `ABORT G-OPTDEP the optimum artefact for row PATCHED is unparseable or is another row's. REFUSED.`

  (`.../Ns-P_launch.out`.)
* **Chain `STOPPED_AT_FIRST_NONZERO arm=Ns-P rc=5`** (`.../STATUS.chain`).
* **The frozen comparator ran and REFUSED rather than degrading**, `grader_rc = 2`, writing the item verdict **`NOT A RESULT`** with, verbatim from `.../SO1c_grade_20260831T171139Z.json`:

  > `{"REFUSE": "G1", "detail": {"arm_absent_from_ledger": "Ns-P", "inspect_record_candidates": [], "note": "exactly one surviving inspect record may stand in for a missing row.  R-RC covers the rc RECORD only: DIGEST, cpuset and core_min are PHYSICS fields and have no fallback channel here."}}`

**THAT REFUSAL IS CORRECT AND IT NAMES A DOWNSTREAM SYMPTOM.** `Ns-P` left no ledger row *because* it aborted in preflight. The refusal is honest about what the comparator could see; it is not the diagnosis. **The root cause is the row label**, and it is stated in §0b.

**SO-1cR IS THE SUCCESSOR.** It re-runs the same registered question with the row-label defect repaired at **every** call site. The re-run costs **40.6 core-min point, ceiling 125.0** (§4) — **$0.03471 DERIVED at $0.0513/core-h, reported-by-owner and NOT measured** — so nothing is bought by straining `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception, and **it is deliberately not reached for.** A successor is the family's established shape for exactly this situation.

## 0b. THE ROOT CAUSE, AND THE LANE-LEVEL FAILURE THAT LET IT THROUGH — RULE 14

**SO-1bR labels its per-row artefacts with the DIRECTORY SUFFIX.** Read from disk at registration time:

| producer artefact | `row` field |
|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/E-P/so1b_E.json` | **`'P'`** |
| `/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/E-S/so1b_E.json` | **`'S'`** |

SO-1c's consumers compared that field against **`'PATCHED'` / `'SHIPPED'`**. SO-1c's **AMENDMENT R8 repaired this in the chain driver** and registered a fence that said *"the row-label comparison"* — **SINGULAR**. **THE FENCE WAS SCOPED TO THE ONE SITE THE LANE HAD FOUND, AND NOBODY SWEPT FOR OTHERS.**

`CLAUDE.md` rule 14 is exactly this: *"a lesson is not applied until **every** call site asserts it."* **THE SWEEP WAS DONE FOR SO-1cR BEFORE ANY REPAIR, AND IT IS RECORDED IN §7a WITH EVERY CONSUMER FOUND AND ITS DISPOSITION — INCLUDING A FOURTH THAT THE POST-MORTEM DID NOT NAME.**

## 0. SCOPE — AND WHAT IS **NOT** NEW HERE, SAID SECOND

**Capability-grid cell (`docs/capability/dafoam_GRID.md`): `2D · steady · incompressible`, the np-INVARIANCE entry of "what was checked", and — because of §3d — the "gradients FD-verified" column.**

**THIS IS NOT THE FIRST np-INVARIANCE RUNG ON THIS CASE, AND THIS DOCUMENT SAYS SO ON ITS FIRST SCREEN.** Carried across from SO-1c unchanged:

* **The re-solve at the optimum and the constraint check are SO-1b's**, already registered and frozen (`curriculum_SO1b/PREREGISTRATION.md` §3c: `G-CL` at `|CL − 0.5| ≤ 1.0e-4`, `G-GEO` over 23 geometric rows at the re-solve). **SO-1cR does not re-buy either.**
* **AV-1 IS ALREADY "the family's first np-INVARIANCE rung"** on this exact case. AV-1 returned **`NOT A RESULT`** at G1 (`23dccf38`) and **AV-1R** is its frozen successor (`0c019d92`, queued at `74beec4c`), unrun.
* **AV-1's `av1_decomposeParDict_np4` has md5 `816f5ba44075fde47fa5db4269877bc8`** — **byte-identical to this item's `so1cr_decomposeParDict_scotch`.** The scotch-at-np-4 configuration is not new and is not claimed as new.

**THREE THINGS ARE NEW, AND THEY ARE THE REASON THIS RUNG EXISTS. EACH IS SOMETHING AV-1 AND AV-1R DISCLAIM IN THEIR OWN §8, IN THEIR OWN WORDS.**

1. **THE DECOMPOSITION *METHOD* IS VARIED AT FIXED np — THE OTHER HALF OF THE STANDARD'S OWN DEFINITION.** `ADJOINT_VERIFICATION_STANDARD.md` §3 defines the check as the same gradient *"at np = 1 (the serial reference) and at np > 1 **(and, at fixed np, across `scotch` / `simple` / `hierarchical`)**"*. AV-1's §8: *"nothing about the `simple` or `hierarchical` decompositions (**scotch only**)"*. **No A1 rung has ever varied the method.** A4 measured np=4 `scotch` at **8.95 %** against np=4 `simple 4×1×1` at **0.00054 %** on one mesh at one np — **a factor of 16,600** (`DAFOAM_CHARTER.md` §5; `PRIOR_WORK_INVENTORY.md:380`).
2. **THE DESIGN POINT IS AN OPTIMUM, NOT A BASELINE.** AV-1's §8: *"**nothing about an optimum**"*. `DAFOAM_CHARTER.md` §9's argument — *"a gradient verified at iteration 0 is not verified at iteration 47"* — transfers to the decomposition without a word changed, and transfers **harder**: IDWarp's defect is a **mesh-deformation** defect with two regimes either side of its `axisMag` guard, and a deformed mesh is precisely where a partition-interface interaction would be worst. **No record in this lab measures decomposition sensitivity on a deformed mesh.**
3. **AN FD TABLE AT np = 4 — WHICH IS WHAT MAKES THIS A VERDICT RATHER THAN A SPOT CHECK.** AV-1 and AV-1R state the hole in their own gate: *"A wrong treatment could still pass G-NP by producing the same wrong gradient at every np."* That is **L-38** exactly. Each SO-1cR arm therefore buys **its own** central-FD table **at its own decomposition**, because `DAFOAM_CHARTER.md` §5 makes an FD reference part of a **configuration** and never carries one across np.

**WHAT IS DELIBERATELY *NOT* RE-BOUGHT.** The **np = 1 serial reference at x\*** is **SO-1b's own `E-<row>/so1b_E.json`**, read from disk and never recomputed. **Not one np = 1 primal is re-bought.**

**The mesh is A1's, 4,032 cells**, regenerated by this item's own `MESH` arm so the item is self-contained — **and because the standard defines this comparison "on the same mesh", mesh identity is then ASSERTED (`G-MESHID`, §3c) rather than assumed.** The FFD box is 5×2×2 → 8 `shape` functions + `patchV`; the objective is `CD` and the equality constraint `CL == 0.5`.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv` DOES NOT EXIST.**

`test -e` → **false** at **2026-08-31T17:18:37Z**, printed by this lane immediately before the case directory was created and before any instrument was written, and again as the first and last legs of `so1cr_groot5_selftest.sh` (*"run root ABSENT before the test"* / *"run root ABSENT after the test (freeze condition)"*, `so1cr_groot5_selftest_evidence.txt`).

**This item has burned 0 core-min of solver compute and CREATED NO CONTAINER OF ANY KIND.** Container census on the box: **19 before this lane's guard suite and 19 after**, both read with `sudo -n docker ps -a -q | wc -l` and both printed in `so1cr_groot5_selftest_evidence.txt`. **After the first arm container, gates are CLOSED**; changes land only as dated addenda that cannot alter a gate, threshold, cap or label (`VERIFICATION_CHARTER.md` §2b).

**SO-1c's own run root is added to the launcher's `FORBIDDEN_ROOTS`** (`so1cr_run_arm.sh:117`): it holds a graded row — a `NOT A RESULT` record, a ledger and a MESH arm — and this launcher stages by removing the arm directory.

## 1a. THE DEPENDENCY ON SO-1b, ITS PRECONDITION ARTEFACT, AND THE TWO NO-LAUNCH BRANCHES

**CARRIED ACROSS FROM SO-1c UNCHANGED IN SUBSTANCE.**

**(i) The queue entry is a WAIT-WRAPPER.** `cases/dafoam/_common/dafoam_wait_then_launch.sh`, precondition:

> **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/E-S/so1b_E.json`**

**AND NOT SO-1b's `CHAIN_DONE` MARKER, THOUGH ONE EXISTS.** `CHAIN_DONE` is written on **every exit of a started chain — including a failed one**. **`E-S` is SO-1b's LAST registered arm**, so its artefact appears only if the whole chain ran to the end and both rows exist. **A last-arm artefact is a stronger precondition than a chain marker.**
**Bound: `172,800 s` (48 h), registered**, on SO-1c's own derivation, carried across. The wrapper polls every 30 s, writes every wait to `STATUS.SO1cR_chain_wait`, applies G-ROOT.5 immediately before exec, and **launches nothing at the bound**.

> **The precondition is PRESENT NOW.** It was read at SO-1c's launch (`md5=9b1a965c5108245679df87801653aae6 size=9991`, `WRAPPER.SO1c_chain_wait.log`), so on current disk this wrapper is expected to launch immediately rather than wait. The bound is registered anyway, because a precondition present at freeze is not a precondition present at exec.

**(ii) `G-SO1B`, in `so1cr_chain_driver.sh`, BEFORE the run root is created and BEFORE the first launcher call.** It reads SO-1b's newest `SO1bR_grade_*.json` **and, independently, SO-1b's own `O-<row>/so1b_O.json`**, and a disagreement between the two channels REFUSES.

**WHAT IS CHECKED IS NOT SO-1b's ITEM VERDICT.** SO-1b's own registered predicted outcome is item **`GATE FAIL`** — its SHIPPED row is predicted to fail band D at `shape[6]` at the optimum, and **that failure is SO-1b's finding**. Gating on the item verdict would kill this item in exactly the case SO-1b expects. **What SO-1cR consumes, per row, is narrower: x\*, the np = 1 gradient at x\*, and a real flow at x\*.**

**THE ACCEPTANCE IS ASYMMETRIC BY REGISTRATION, CARRIED ACROSS UNCHANGED:**

| row | `G-OPT` accepted | `G-CL` accepted | why |
|---|---|---|---|
| **PATCHED** | **`PASS` only** | `PASS` | it is the CONTROL, and "post-optimum verification" at a point that is not an optimum is a different item. D1 and D13's five restarts converged on this exact problem **six times** |
| **SHIPPED** | **`PASS` or `GATE REACHED`** | `PASS` | the shipped arms ask what a **deformed mesh** does to a **parallel** gradient. That question is meaningful at the design point the shipped toolchain reached whether or not IPOPT converged there |

**`G5E`, SO-1b's endpoint FD gate, IS DELIBERATELY NOT READ ON EITHER ROW** — SO-1cR buys its own FD table at np = 4, and `DAFOAM_CHARTER.md` §5 forbids carrying an FD reference across np. **Driven** in `so1cr_groot5_selftest.sh` leg (e7), which asserts no *executable* line of the driver reads `G5E`.

**THE TWO REGISTERED NO-LAUNCH BRANCHES, both at ZERO core-minutes, named in advance:**

| branch | trigger | mechanism | rc | item verdict | cost |
|---|---|---|---|---|---|
| **N1** | SO-1b never reaches `E-S` | the wrapper's precondition never appears; it closes at the 172,800 s bound and launches nothing | **6** | **`BLOCKED`** | **0 core-min** |
| **N2** | the precondition exists but SO-1b's rows do not meet the table above — or its grade is absent, unreadable, names no `G-OPT`/`G-CL` verdict, or the two channels disagree | `G-SO1B` in the driver, before the run root is created | **7** | **`BLOCKED`** | **0 core-min** |

Both branches are the safe direction and both are registered before compute. Driven at legs (e1)–(e5).

## 2. ARMS — five, in this order, one detached chain, TWO ROWS × TWO DECOMPOSITIONS, np = 4 ON EVERY SOLVER ARM

**TWO ROWS, `SHIPPED` and `PATCHED` (`DAFOAM_CHARTER.md` §6).**

| arm | kind (G1) | image (row) | ranks | decomposition | cpuset | mem | task | artefact | terminal marker |
|---|---|---|---|---|---|---|---|---|---|
| **MESH** | SCRIPT | SHIPPED | 1 | — | 10 | 4g | the tutorial's own `preProcessing.sh` + `checkMesh` + `sha256sum constant/polyMesh/points*` | `MESH/checkMesh.log` | `Mesh OK.` |
| **Ns-P** | SOLVER | **PATCHED** | 4 | **`scotch`** | 10,11,12,13 | 6g | `so1cr_xn.py -mode N -optimum so1b_E.json` | `Ns-P/so1cr_N.json` | `SO1CR_N_WRITTEN` |
| **Ni-P** | SOLVER | **PATCHED** | 4 | **`simple 4×1×1`** | 10,11,12,13 | 6g | as above | `Ni-P/so1cr_N.json` | `SO1CR_N_WRITTEN` |
| **Ns-S** | SOLVER | SHIPPED | 4 | **`scotch`** | 10,11,12,13 | 6g | as above | `Ns-S/so1cr_N.json` | `SO1CR_N_WRITTEN` |
| **Ni-S** | SOLVER | SHIPPED | 4 | **`simple 4×1×1`** | 10,11,12,13 | 6g | as above | `Ni-S/so1cr_N.json` | `SO1CR_N_WRITTEN` |

Chain: `so1cr_chain_driver.sh MESH Ns-P Ni-P Ns-S Ni-S`, stops at the first non-zero rc, then runs the frozen grader on whatever exists (its rc is INFRASTRUCTURE, never the verdict). **The PATCHED row runs FIRST by registration** — it is the control for the shipped row beside it. **Both rows are bought on ONE mesh generated once in the SHIPPED image.**

**np = 4 IS THIS ITEM'S ENTIRE SUBJECT.** `DAFOAM_CHARTER.md` §5 says *serial before parallel*: SO-1a bought the serial gradient and SO-1b bought the serial optimum, so **the serial half is bought and this rung is the parallel half it licenses.** DAFoam runs `decomposePar` itself at np > 1 from the arm's own `system/decomposeParDict`, which is a **frozen, md5-pinned file per decomposition**, overlaid at staging and **re-asserted on the overlaid copy**.

**THE CPU PLACEMENT IS DISJOINT BY REGISTRATION, NOT BY LUCK.** `10,11,12,13` — four distinct cores for four ranks. Checked against every registered sibling placement: **D6's `2,3,4,14`**, **D4-SHIPPED's `5,6,7,9`**, **SO-1a's and SO-1b's `9`**. `10-13` intersects none of them. **At np = 4 the grader's delivered-cores floor DOES apply.**

**THE REGISTERED FD DESIGN AT np = 4, PROVED PAIR BY PAIR** — identical components and steps to SO-1a's at the baseline and SO-1b's at the optimum, which is what makes the three comparable. Components **`shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`** plus the planted-zero control **`CTRL`**; steps **`shape`: {1e-2, 1e-3, 1e-4}**, **`patchV[1]`: {1e-1, 1e-2, 1e-3}** degrees; central differences, both signs; reference = the middle step; **the plateau is agreement with at least one NEIGHBOUR to 10 % — a PAIRWISE test between adjacent steps, never a single spread over the whole set.** Step-set justification is **by citation and not re-derived**: `A_stepsize_study.md` measured the curve flat at 2.5–3.0 % from 1e-4 to 3e-2 **on this case**.

**THE PLANTED-ZERO CONTROL (rule 3), IN BOTH DIRECTIONS, in the instrument AND in the grader, AND ON THE HEADLINE GATE ITSELF.** `CTRL` carries a synthetic row with derivative exactly `0.0` and a PLANTED row with `CD_plus = CD_optimum + 1.234e-03`; the instrument writes both, **re-reads them from disk**, and **exits 2 if the read-back cannot see them**. The grader re-checks both, re-plants `PLANT` into every physical derivative and **refuses unless every value moved by exactly `PLANT`** — **and additionally re-plants a `1 + 10 × S_G_BAND` scaling into the np = 1 reference and REFUSES unless `g_npinv` reads `GATE FAIL` on it.** The np-invariance reader is the one whose `PASS` would otherwise be the item's whole claim, so it is the one shown able to fail.

## 3. GATES, THRESHOLDS AND LABELS — `so1cr_grade.py`

All bands are frozen now. Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

### 3a. Completion, inherited whole from SO-1a

**G1** — the five rule-4 clauses **printed individually per arm**: `C1` rc VALUE (physics, from `docker inspect .State.ExitCode`), `C2` terminal marker, `C3` artefact present, `C4` age guard, `C5` no fatal token (**REFUSES REGARDLESS OF rc**). Any clause failing on any arm → **`NOT A RESULT`**, comparator exit 2. **R-RC** as Sanaa approved it. **L-342 field classes** (`d4d0c29d`). **The age-guard datum is resolved BY EXISTENCE over `0/U` and `0/U.gz`.** **`G-M2`** — `cells == 4,032` → `PASS` else `GATE FAIL`.

**AND THE AGE-CHECKED LIST CONTAINS ONLY WHAT THIS RUN PRODUCES.** `so1cr_N.json` and `so1cr_N.jsonl` are age-checked. **`so1b_E.json`, `so1cr_runScript.py`, `so1cr_xn.py` and `system/decomposeParDict` are STAGED INPUTS**, listed in the comparator's own `STAGED_INPUTS` and **excluded by name** — the `d4s_f3s_grade.py:61` defect, which made an age clause unsatisfiable by construction and forced D4S-F3S to `NOT A RESULT` with **19 of 20 gate readings passing**. Driven at grader unit **U40**.

### 3b. `G-NP` and `G-METHOD` — np-INVARIANCE AT THE OPTIMUM. **THE BAND IS NOT THIS LANE'S.**

`docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md` §3 defines the check and freezes the band. **All three numbers are INHERITED BY CITATION and are NOT re-derived here:**

| quantity | band | source |
|---|---|---|
| objective spread `s_J = \|J(np) − J(1)\| / \|J(1)\|` | **≤ 2.2e-5** | the lab's measured partition-reproducibility upper bound (`PARALLEL_GATE_DOCTRINE.md:38, :194-198`, commit `fd9bf1b6`); B3 measured 2.9e-7, inside by 75× |
| gradient spread `s_g = ‖g(np) − g(1)‖₂ / ‖g(1)‖₂` | **≤ 1.0e-3** | 6× the family's measured floor of 1.1–1.7e-4 (B3, `bb5088c4`) and **50× below band D**; A4 `simple` 5.4e-6 inside, A4 `scotch` 8.95e-2 outside by 90× |
| per-component sign agreement | **0 flips** (on components with `\|g₁,ᵢ\| ≥ 1e-14`; smaller named and skipped) | `VERIFICATION_CHARTER.md:845` |

> **⚠ THE BAND FOR THIS GATE IS NOT BAND D, AND THE DIFFERENCE IS 50×.** A lane reaching for the familiar `FD_BAND_PCT 5.0` would have registered a gate **fifty times too loose to see the effect the rung exists to find.** The `50×` relation is asserted arithmetically in grader unit **U3**.

* **`G-NP`, per arm**, against **SO-1b's np = 1 serial reference at x\***, for `CD` and `CL` separately. **The reference is read on TWO independent channels** — the copy the instrument carried into its artefact, and the comparator's own read of the same `optref/<ROW>/so1b_E.json` — and **a disagreement REFUSES** (U12). A reference whose `nprocs ≠ 1` REFUSES (U11).
* **`G-METHOD`, per row**: `scotch` against `simple 4×1×1` **at fixed np = 4**, on the same band. **`simple 4×1×1` is the REFERENCE limb and `scotch` the graded limb, fixed here before the run** because A4 measured `simple 4×1×1` at 0.00054 % against FD and `scotch` at 8.95 %.
* **`G-DECOMP`**: every arm's artefact must name the method it was registered for, the subdivision for `simple`, and an `nprocs` that agrees with the dictionary's own `numberOfSubdomains` — **cross-asserted on two sources**. Any disagreement **REFUSES** (U15, U16, U17).

### 3c. `G-MESHID` — "the same mesh" is ASSERTED, not assumed

The `points` sha256 this item's MESH arm prints must equal the one SO-1b's MESH arm printed (copied into `optref/so1b_mesh_points_sha256.txt` by the driver at staging).

* **equal** → `PASS`.
* **unequal** → **`GATE FAIL`**, and the finding is named: *mesh regeneration is not deterministic*.
* **SO-1b's fingerprint absent, unreadable, or naming MORE THAN ONE distinct sha** → **`NOT A RESULT`, `cause_class = READER_CONDITION_NOT_A_MESH_FINDING`**, never a pass and never a physics sentence (U21, U22, U61, U62, U63 — R6's repair, carried across).

### 3d. `G5N` / `G5cN` — the FD verdict at np = 4, and `G-TB`

Per arm, `grade_components` against **that arm's own np = 4 FD table**, on `CD` (`G5N`) and on `CL` (`G5cN`). **Band D `FD_BAND_PCT = 5.0` per component with sign agreement, band E `AGG_BAND_PCT = 5.0` aggregate, plateau `PLATEAU_TOL_PCT = 10.0` PAIRWISE, fewer than 3 graded → `NOT A RESULT`.** **These three are INHERITED BY CITATION from SO-1a and SO-1b, which inherit them from `curriculum_D4/PREREGISTRATION.md:82` and `D7FR:228-229`** (asserted at U4).

**`G-TB`** — the `DAFOAM_CHARTER.md` §4 trivial baseline at the deliberately wrong step (`shape` 1e-8, `patchV` 1e-6), per arm. If the WRONG step also passes band D on **2 or more** of the five components, that arm's verdict is **WITHDRAWN to `NOT A RESULT`** (U26, U27).

**THIS IS THE SUB-GATE THAT MAKES THE ITEM A VERDICT.** Unit **U23** drives exactly the state AV-1 disclaims: a 7 % FD error planted with `G-NP` still reading `PASS`, and the arm still lands `GATE FAIL`.

### 3e. `G-XSTAR` — an identity assertion, **deliberately not a gate on the design vector**, AND THE ROW LABEL IS A REGISTERED MAPPING

D13 / C-71 measured this problem's design vector **NON-UNIQUE** and its drag **UNIQUE**: **15 of 15** restart pairs `DIFFERENT` on design, **0 of 15** on drag. **No verdict in this item rests on a design vector.** `G-XSTAR` asserts only that the point each arm solved at is byte-for-byte the point SO-1b bought — a provenance check on a **consumed input** — and refuses otherwise (U19). The distinction is written into the artefact itself (U20).

**AND ITS ROW LIMB USES THE REGISTERED MAPPING (§7a):**

```
ROW_LABELS = {"PATCHED": ("PATCHED", "P"), "SHIPPED": ("SHIPPED", "S")}
```

**IT IS DELIBERATELY NOT `row[0]`.** `row[0]` agrees with the producer only by the coincidence that `PATCHED` and `SHIPPED` share first letters with `P` and `S`, and **a check that is true by coincidence has stopped being a check** — it would silently accept a row labelled `PORPOISE` under `PATCHED` (driven, **U71**). **THE TWO LABEL SETS ARE DISJOINT**, asserted arithmetically rather than trusted from prose (**U72**), because the assertion exists to catch **an artefact sitting in the wrong directory**. **BOTH SWAP DIRECTIONS REFUSE** (**U69**, **U70**).

### 3f. `G-CLOCK` and `G10` — **the cap gate and the cost claim read different frames, on purpose**

**THE DEFECT, MEASURED.** The cap is a `timeout -k 60 $TMO` **inside** the container while `core_min` is a wall bracketed around `docker run -d` **on the host**. **An arm stopped exactly at its own registered deadline therefore records a wall ABOVE its cap and trips its own cap limb — a `GATE FAIL` manufactured by the measurement frame, not by the run.** At 4 ranks the poll granularity alone is `10 × 4 ÷ 60 = 0.667` core-min.

**THE REPAIR IS NOT A WIDER CAP.** Both frames are measured from records that already exist — `.State.StartedAt` / `.State.FinishedAt`, already written into `<ARM>_<stamp>.inspect.txt` — and:

* **`G10` grades `core_min_container`**, the frame the deadline lives in;
* **the COST claim uses `core_min`**, the host frame, the frame the box is occupied in and the **larger** of the two;
* their difference is written to the ledger as `clock_frame_delta_core_min` and reported per arm;
* **an unreadable container clock is INFRASTRUCTURE**: `G10` falls back to the host frame **and names the arm in `frame_fallbacks`**.

Driven at **U28**, **U29**, **U30**, **U31**.

### 3g. `G9` / `G11` / `G12`, and the item composition

**`G9`** — ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process `libidwarp.so` md5 must all name the row's toolchain; **plus `G-ROWX` across the item boundary: the two arms of one row must share a library hash, and it must be the hash of the SO-1b artefact they read.** **A row is an image hash, never a directory name** — and the *label* is the registered mapping of §3e, which is a separate and weaker claim, made only about provenance. **`G11`** — OOM hard. **`G12`** — per-arm cpuset, and **at np = 4 the delivered-cores floor of 3.0 (0.75 × ranks) applies**.

**Composition, registered here:**
* **an ARM** is `NOT A RESULT` if `G-TB` withdraws it or any of `G-NP` / `s_J` / `G5N` / `G5cN` is `NOT A RESULT`; `GATE FAIL` if any is `GATE FAIL`; else `PASS`.
* **a ROW** is the composition of its two decomposition arms **and** that row's `G-METHOD`.
* **the ITEM** is `NOT A RESULT` if either row is or `G-MESHID` is; `GATE FAIL` if either row is or any of `G-M2` / `G-MESHID` / `G9` / `G10` / `G12` is; else `PASS`.

**No grid family exists, so standing rule 5 has no row and NO GCI IS QUOTED.** **This item quotes NO improvement percentage, so `G-D7R` has no row here — and nothing in this item lifts SO-1b's `SUPPRESSED_BY_G_D7R`.**

## 4. COST — DERIVED FROM NAMED ANCHORS, AND THE ANCHOR RISK NAMED FIRST

> **THIS FAMILY'S ESTIMATING ERROR IS IN THE ANCHOR CHOICE, NOT THE RATE (C-182).** **So both anchors are named below, with what each was measured on, and the LARGER is taken.**

| anchor | what it was MEASURED on | value |
|---|---|---|
| **A — like-for-like whole arm** | A1's own mainline rung: `run_model` + `compute_totals` + `check_totals` at **np = 2**, `DASimpleFoam`, **this exact 4,032-cell mesh** (`PRIOR_WORK_INVENTORY.md:47`) | **3.51 core-min MEASURED** |
| **B — component-built** | **C-158** AV-1 `X1-S`: setup + 1 primal + 2 adjoints + colouring, **np = 1, this exact case** → 1.017 core-min MEASURED; **C-154** D15 `F-S − X-S`: ≥ 31 primals, **np = 2, this mesh** → 2.066 core-min MEASURED | **1.017 + 2.066** |
| **MESH** | **C-154 (D15), C-156 (D16), C-158 (AV-1)** — three independent measurements | **0.167 core-min MEASURED** |
| **MESH, this item's own predecessor** | **SO-1c's own MESH arm, 2026-08-31, ranks = 1, wall 38 s** — the closest anchor that exists, and it is 3.8× the three above | **0.633 core-min MEASURED** |

**The np = 2 → np = 4 conversion assumes ZERO SPEEDUP** — at 1,008 cells per rank the solve is communication-bound. So core-minutes scale by the rank ratio:
* Anchor A: `3.51 × 2` = **7.02 core-min/arm**.
* Anchor B: `1.017 × 4` + `2.066 × 2` = **8.20 core-min/arm**.

**The larger (B) is taken and margin is added for np = 4 colouring: point 10.0 core-min per solver arm.** Cross-check: **AV-1 registered 4.0 core-min for an np = 4 `X` arm** (no FD table) at parallel efficiency 0.6; 10.0 here is that arm plus a ~33-primal FD block at a **more conservative** 0.5.

**THE MESH POINT IS RAISED TO SO-1c's OWN MEASUREMENT AND THE OLD ONE IS NOT QUIETLY KEPT.** SO-1c registered MESH at **0.167** and its MESH arm actually burned **0.633 core-min — a ratio of 3.79**. That is a live, in-family, same-mesh miss, and carrying the 0.167 forward would be registering a number this lane has already watched fail. **The MESH point becomes 0.633** and the cap stays **5.0** (7.9× the new point, so the `D5-PREREG-DEF-1` class is still excluded by arithmetic). **The item point therefore moves from 40.2 to 40.6 core-min.** **The band and the ceiling do not move.**

> **⚠ THE HONEST GAP, NAMED RATHER THAN BURIED: NEITHER SOLVER ANCHOR WAS MEASURED AT np = 4 ON THIS CASE.** The zero-speedup scaling is an **assumption**, not a measurement, and it is the single largest source of error here. Registered as prediction **P-I** so the first fire converts it into a `docs/COST_CALIBRATION.md` row whether it is right or wrong.

| arm | ranks | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| MESH | 1 | **0.633** | 5.0 | 300 s | 4g |
| Ns-P, Ni-P, Ns-S, Ni-S | 4 | **10.0** each | 30.0 each | **450 s** | 6g |
| **TOTAL** | | **40.6** | **CEILING 125.0** | | |

**THE CAP FITS THE REGISTERED WORK BY ARITHMETIC.** Each solver arm's registered work is 1 primal + `compute_totals` + 2 × (5 components × 3 steps) + 2 × (5 × 1 TB step) + 1 repeat ≈ **34 primals + 2 adjoints**. Anchor A's comparable whole arm took **105 s wall at np = 2**; at zero speedup that is ~105 s wall at np = 4, against an in-container deadline of **450 s — a 4.3× wall margin**. In core-minutes the cap is **3.1× the point**. **`G-CAP-PREREG` asserts the launcher's cap table against line 6 of this document on TWO CHANNELS — the document on disk AND `git show HEAD:<path>` — before any container starts**, and a disk/HEAD disagreement aborts rc=65. Where HEAD cannot be read the head channel records **`NOT_MEASURED`**, never a pass.

**Band `[22.0, 80.0]` core-min**, unchanged from SO-1c, set wide because the np = 4 scaling is an assumption. **Dollars DERIVED at $0.0513/core-h, REPORTED-BY-OWNER, NEVER MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5): point **$0.03471**, band top **$0.06840**, ceiling **$0.10688**.

**ALREADY SPENT ON THIS QUESTION, AND IT IS NOT HIDDEN: SO-1c burned 0.633 core-min MEASURED** (its MESH arm; **$0.00054 derived**) before dying at `Ns-P`. That spend bought a mesh SO-1cR does **not** inherit — SO-1cR regenerates its own, because the item is registered self-contained and its run root is fresh. **The 0.633 core-min is therefore WASTE, is named as waste, and is NOT absorbed into SO-1cR's ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). **SO-1cR's own already-spent figure is 0 core-min and 0 containers.**

**Memory 6g at np = 4 and the H5 floor of 8.0 GiB are AV-1's and AV-1R's registered figures for np = 4 on this exact mesh** (`av1_run_arm.sh:173`, `av1_chain_driver.sh:45`, `av1r_chain_driver.sh:103`), inherited by citation and not re-derived.

## 5. THE REGISTERED PREDICTIONS — written before they run, and falsifiable

| id | prediction | basis | what a MISS means |
|---|---|---|---|
| **P-A** | `cells == 4,032` | three prior measurements of this mesh | the mesh is not A1's |
| **P-MESHID** | this item's `points` sha256 **equals** SO-1b's | pyHyp is expected deterministic | **a mesh-regeneration-determinism finding**, and the item goes `NOT A RESULT` |
| **P-1** | the **`scotch`** arms fail `s_g ≤ 1.0e-3` on **at least one row** | A4 measured np=4-`scotch` at **8.95e-2**, 90× outside | **the effect is absent at an optimum on this case** — itself a finding, and a strong one |
| **P-2** | the **`simple 4×1×1`** arms pass `s_g ≤ 1.0e-3` on **both rows** | A4 measured `simple 4×1×1` at **5.4e-6**, inside by 185× | the clean decomposition is not clean here |
| **P-3** | `s_g` at the **optimum** exceeds `s_g` at the **baseline**, same row and decomposition — **THE RUNG'S OWN REASON** | §9's "verified at iteration 0 is not verified at iteration 47" | **decomposition error is DESIGN-INDEPENDENT**, contradicting the argument this rung is built on. **Scored `NOT_MEASURED` unless AV-1R has supplied a baseline figure — registered as `NOT_MEASURED` in the comparator NOW (U52) so an absent reference can never become a silent HIT** |
| **P-4** | `shape[6]` carries the largest per-component share of the scotch disagreement | idx6 carries **82.7 %** of A1's squared-error norm (`A_stepsize_study.md:53`) | the LE component is not the locus at np > 1 |
| **P-5** | `s_J ≤ 2.2e-5` on **every** arm | B3 measured 2.9e-7 | a converged objective that moves under decomposition — a louder finding than a gradient that does |
| **P-6** | the PATCHED `simple` arm is FD-`PASS` on ≥ 4 of 5; the PATCHED `scotch` arm is **not** | the pair that turns a spot check into a verdict | the FD table does not separate the decompositions |
| **P-7** | the SHIPPED rows fail band D at `shape[6]` at **both** decompositions | the IDWarp LE defect, `11.43 %` at A1's baseline | the defect is decomposition-dependent |
| **P-TB** | the trivial baseline fails ≥ 4 of 5 on **every** arm | h = 1e-8 is below the measured primal repeatability | the FD gate is not measuring the step |
| **P-I** | total in **[22.0, 80.0]** core-min | §4 | **the np = 2 → np = 4 zero-speedup assumption is wrong**, and the calibration row says by how much |
| **P-mesh** | MESH ≤ 1.5 core-min | **SO-1c's own MESH arm measured 0.633**, and the three older anchors measured 0.167 | the mesh arm is not reproducible in cost on the same box |
| **P-CLOCK** | the host frame exceeds the container frame on **every** arm, and the margin is reported | the host wall brackets the container start and the poll granularity | the frame model is wrong |
| **P-ROW** | **every arm's `G-OPTDEP` and `G-XSTAR` row limb PASSES against SO-1bR's real `'P'`/`'S'` labels, and NO arm aborts rc=5 in preflight** | §7a's sweep and the four-state drive in `so1cr_rowlabel_sweep_evidence.txt` | **a FIFTH row-label call site exists that this lane's sweep did not find**, and the sweep in §7a is not the class repair it claims to be |

**REGISTERED OUTCOME, so it cannot be written afterwards: P-1 and P-2 HIT → the `scotch` arms `GATE FAIL`, the `simple` arms `PASS`, BOTH ROWS `GATE FAIL`, ITEM `GATE FAIL`** — and the finding is that **SO-1's entire graded np = 1 result, SO-1a's gradient and SO-1b's optimum alike, is not carryable to np = 4 under `scotch`, which is DAFoam's own default decomposition.**

## 6. WHAT THIS ITEM WILL NOT ESTABLISH

**Nothing at np = 2 or np = 3** — AV-1R buys the np sweep and this item buys the method sweep. **Nothing about `hierarchical`**, the third method the standard names. **Nothing about a second design point or a second start.** **Nothing about SO-1b's own verdict**: SO-1cR does not re-grade SO-1b and does not lift its `SUPPRESSED_BY_G_D7R`. **NOTHING ABOUT SO-1c's VERDICT EITHER — SO-1c is `NOT A RESULT` and this item does not convert it, supersede its reading, or claim its compute.** **No improvement percentage is quoted anywhere in this item.** **Nothing about the other four `shape` functions or `patchV[0]`.** **No dot-product test and no complex step.** **No grid family, no GCI, no Roache triple** — standing rule 5 has no row here. **Nothing about a mesh other than A1's 4,032 cells**, and nothing about the transonic RAE2822 half of Sanaa's SO-1 sentence. **Nothing about the constraint FAMILIES — that is SO-2's subject.** A `scotch`-vs-`simple` divergence of 0.000 % would be reported with its number and would **not** be read as "the defect is absent".

**AND IT ESTABLISHES NOTHING ABOUT WHETHER A FIFTH ROW-LABEL CALL SITE EXISTS.** §7a's sweep is a detector over a registered consumer list; it proves those three files carry no unrepaired comparison and that a planted fourth is caught. **It cannot prove a site outside its consumer list does not exist.** That is why **P-ROW** is registered: the run itself is the test.

## 7. FROZEN INSTRUMENTS, AND EVERY GUARD DRIVEN — WITH THE ONE LEG THAT WAS NOT

**Instrument md5s (frozen at this commit; the driver asserts them before staging and again before every arm):**

| file | md5 |
|---|---|
| `so1cr_xn.py` | `1ffadf39206d5bb732dcfcf0288ba628` |
| `so1cr_grade.py` | `a13cd4e7b53c5051abe697da485c3433` |
| `so1cr_run_arm.sh` | `52d991ce80a1af30523a9f7253286e3b` |
| `so1cr_chain_driver.sh` | *(computed at freeze; nothing pins the driver — the queue entry names it by path)* |
| `so1cr_runScript.py` | `0557da51f6f179f6de865144343c499f` (byte copy of the shipped INCOMPRESSIBLE tutorial `runScript.py`) |
| `so1cr_decomposeParDict_scotch` | `816f5ba44075fde47fa5db4269877bc8` (**byte-identical to AV-1's `av1_decomposeParDict_np4`**) |
| `so1cr_decomposeParDict_simple` | `194c330803077f0ffa4341f468c09768` |
| `so1cr_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` |
| `so1cr_rowlabel_sweep.py` | `0c371040cf403477a5e67fa0c83cb7d9` — **a PRE-COMPUTE guard instrument, driven by the guard suite, deliberately NOT a chain pin**: the driver does not call it, and adding a 13th `MD5_*` would make leg (a5e)'s completeness count false |

**ALL TWELVE `MD5_*` PINS IN THE DRIVER WERE RE-DRIVEN AFTER THE EDITS, AND THE THREE THAT MOVED ARE NAMED:**

| pin | before (SO-1c) | after (SO-1cR) | why |
|---|---|---|---|
| `MD5_LAUNCHER` | `12dd18eced7b67f04348cd29363d31e1` | `52d991ce80a1af30523a9f7253286e3b` | the G-OPTDEP repair, `FORBIDDEN_ROOTS` + SO-1c's root, the cap-comment correction, the manifest-marker rename, the item rename |
| `MD5_GRADER` | `367f9fc25b3b34535cb2cddfafdc06b1` | `a13cd4e7b53c5051abe697da485c3433` | the G-XSTAR repair, the fixture repair, seven new units, `EXPECTED_UNITS` 65 → 72, the item rename |
| `MD5_XN` | `63d13c88fb915ab7695d6f1a9383a4ed` | `1ffadf39206d5bb732dcfcf0288ba628` | the item rename only (marker strings `SO1C_` → `SO1CR_`); **no logic changed** |
| the other nine | unchanged | unchanged | `MD5_RUNSCRIPT`, `MD5_DECOMP_SCOTCH`, `MD5_DECOMP_SIMPLE` and the six `MD5_TUT_*` name bytes that did not move |

> **`MD5_LAUNCHER` WAS RE-DRIVEN TWICE AND THE SECOND PASS IS WHY IT IS RIGHT.** The first pass computed it, then patched `MD5_XN` **inside `so1cr_run_arm.sh`**, which moved the launcher's own bytes again. **A pin computed before the last edit to the file it pins is a stale pin**, and a stale pin aborts the chain rc = 4 before any container — the `W3` death mode. Convergence was then asserted explicitly, pin against file, for all twelve. Driven at legs **(a5c)** (six in-repo), **(a5d)** (six out-of-tree tutorial inputs) and **(a5e)** (the completeness count: 12 pins in the driver, 12 driven).

**Toolchain, inherited by citation from SO-1a, SO-1b, AV-1 and SO-1c, and enforced at run time rather than by this document:**

| row | image | digest | library md5 |
|---|---|---|---|
| SHIPPED | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |
| PATCHED | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |

> **THE SHIPPED DIGEST AND LIBRARY md5 WERE CONFIRMED LIVE BY SO-1c's OWN MESH ARM** — its ledger row records `DIGEST=sha256:9d45679d…` and its log printed `D4S_IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663`, both matching. **THE PATCHED DIGEST WAS CONFIRMED LIVE BY SO-1c's `Ns-P` PREFLIGHT**, which printed `D4S_G_ROW_PASS row=PATCHED digest=sha256:2927768a…` before aborting. **The PATCHED library md5 is the one value in this table still unconfirmed by a container on this box**, because reading it requires starting one; it is enforced at run time by `G9` and `G-ROWX`.

**Grader selftest — `so1cr_grade_selftest_evidence.txt`: 72 units, 1 fail, under `python3` AND `python3 -O`, with `__pycache__` cleared before each run.** **The one fail is `U64`, and it is an honest NOT-DRIVEN carried across from SO-1c unchanged**: it needs a real OpenFOAM log from `CURRICULUM-D12R2W3-…` that is not on this box. **It fails identically in the unmodified predecessor** — driven as a control, so it is this lane's inheritance and not this lane's breakage. The synthetic banner plant (U54) is driven in its place.

**`EXPECTED_UNITS` 65 → 72, DELIBERATELY, AND THE GUARD CAUGHT THE ADDITION BEFORE THE BUMP.** Adding U66–U72 made the comparator exit **rc = 2** with *"unit count 72 != frozen EXPECTED_UNITS 65 (a suite that silently loses a unit is not a suite)"*. **A silent bump is the same defect as a silently lost unit**, so it is recorded here rather than absorbed.

**THE SEVEN NEW UNITS, AND WHAT EACH DRIVES:**

| unit | drives |
|---|---|
| **U66** | the PRODUCER'S OWN LABEL (`'P'`/`'S'`) → `G-XSTAR` PASS on every solver arm. **This is the exact state SO-1c died in** |
| **U67** | the gate NAMES both the artefact's label and the arm's registered row in its own record |
| **U68** | the OTHER registered label (`'PATCHED'`/`'SHIPPED'`) also PASSES — the mapping accepts both and invents neither |
| **U69** | **SWAP DIRECTION 1** — a SHIPPED artefact under `optref/PATCHED/` (and vice versa), by suffix → **REFUSES** |
| **U70** | **SWAP DIRECTION 2** — the same swap by FULL NAME → **REFUSES**. A repair that fixed only the suffix form would pass U69 and be wrong |
| **U71** | an UNREGISTERED label (`'PORPOISE'`, which shares its first letter with `PATCHED`) → **REFUSES**. A `row[0]` check would accept it |
| **U72** | the two label sets are **DISJOINT**, asserted arithmetically, not trusted from the comment beside them |

**MUTATION CONTROLS — carried across from SO-1c, plus the one this item adds:**

| mutation | units flipped |
|---|---|
| `S_G_BAND` 1e-3 → 1e-1 | U3, U5, U7, U13 |
| `S_J_BAND` 2.2e-5 → 2.2e-2 | U3, U9 |
| `G-METHOD` always `PASS` | U13 |
| `G-MESHID` always `PASS` | U21 |
| `G10` gate reads the HOST frame | U28, U31 |
| `STAGED_INPUTS` name broken | U40 |
| the np-plant control disarmed | U11 |
| **`G-XSTAR` restored to the equality form, fixture left at the PRODUCER'S label** | **the suite DIES AT UNIT 1** with `{"REFUSE": "G-XSTAR", "detail": {"arm": "Ns-P", "arm_row": "PATCHED", "staged_artefact_row": "P"}}` — **the production break, reproduced inside the grader** |
| **`SIGN_FLIP_MAX` 0 → 9** | **NONE — AN INERT MUTATION THAT PROVES NOTHING** |

**The inert mutation is not hidden; it is measured and recorded as unit U53.** A sign flip on any component above the near-zero floor **necessarily** drives `s_g` far beyond `1.0e-3` — the fixture's smallest non-zero component gives `s_g ≈ 0.13`, **130× the band** — so the sign-flip limb can never be the **sole** cause of a `GATE FAIL` and **is not independently load-bearing.** This document does not claim it as an independent gate.

**Guard selftest — `so1cr_groot5_selftest_evidence.txt`: 62 legs driven, 0 fail, 1 leg NOT DRIVEN and named (never counted). GUARD PLACEMENT PROVED BY LINE NUMBER**, because a guard placed after the destructive step is decoration and placement has been the defect five times in this family. Every guard precedes every destructive step and every spending step.

> **ONE LEG IS NOT DRIVEN, AND IT IS NAMED RATHER THAN COUNTED.** `G-ROOT.5` leg (a)'s **positive** side — *"a RUNNING container already carries this item's prefix and arm"* — can only be driven by **creating a container**, which this registration's zero-container instruction forbids. **The leg is printed as `[NOT DRIVEN]`, is excluded from the pass count, and the one-line command that drives it is printed in the evidence for the supervisor to run before first compute.** Its **negative** side is driven, and the **ordering** assertion is driven by line number at leg (b2).

**`ast.Assert` = 0** in `so1cr_grade.py` and `so1cr_xn.py`, with the counter shown counting a planted assert (U49, U50), and the comparator refuses at startup if the count is non-zero. **The `ROW_LABELS` disjointness check in the module body is a `raise SystemExit`, NOT an `assert`** — this suite runs under `python3 -O`, which **strips `assert`**, and a disjointness check that vanishes under the optimiser is not a check. **Classifier denials in this lane while building SO-1cR: none.**

## 7a. THE ROW-LABEL CALL-SITE SWEEP — RULE 14, DONE BEFORE THE REPAIR AND RECORDED IN FULL

**THE SWEEP WAS RUN BEFORE ANY REPAIR WAS WRITTEN.** Every consumer of a row label across the item, with its disposition:

| # | site | form | disposition |
|---|---|---|---|
| **1** | `so1cr_chain_driver.sh:224` | `if e["row"] not in ROW_LABELS[row]` | **ALREADY REPAIRED** by SO-1c's amendment R8; carried across unchanged |
| **2** | `so1cr_run_arm.sh:468` (SO-1c numbering) | `if d['row']!='$ROW'` | **REPAIRED HERE.** **THIS IS WHAT KILLED SO-1c** — rc = 5 in preflight, no container started |
| **3** | `so1cr_grade.py:997` (SO-1c numbering), `G-XSTAR` | `if ref.get("row") != ARM_ROW[arm]` | **REPAIRED HERE.** Would have refused at GRADING even had (2) passed |
| **4** | `so1cr_grade.py:1687` (SO-1c numbering), the **selftest FIXTURE** | wrote `"row": rowname`, the FULL name | **REPAIRED HERE. THE POST-MORTEM DID NOT NAME THIS ONE, AND IT IS THE MOST DANGEROUS OF THE FOUR.** The real producer writes `'P'`/`'S'`; the fixture wrote `'PATCHED'`/`'SHIPPED'`. **So site (3) was only ever exercised against a label the real world does not produce — it was GREEN IN FIXTURE AND WOULD HAVE REFUSED IN PRODUCTION.** A fixture that disagrees with its producer does not merely fail to catch a break; it **conceals** one, and this is why 53 green units and three amendments saw nothing |
| **5** | `so1cr_groot5_selftest.sh:366` (SO-1c numbering), leg (e13) | grepped **`$DRIVER` only** for the mapping literal | **THE NARROW FENCE ITSELF.** Not broken, but it is the reason (2), (3) and (4) survived R8. **REPLACED** by the leg group (r14) below |

**FOUR SITES SWEPT AND DISPOSITIONED AS NOT REPAIRS, so a later reader does not re-open them:**

| site | why it is not a call site |
|---|---|
| `so1cr_run_arm.sh:432` `test "$ROW" = "$WANT_ROW"` | **both sides are internal full labels** derived from `IMG` and `ARM` within the same script. It never touches a producer artefact. No cross-boundary comparison, no repair |
| `so1cr_xn.py:291` `row = opt["row"]` | a **READ that propagates**, not a comparison. `so1cr_xn.py` is never given a row label at all — it is invoked as `-mode N -optimum so1b_E.json` and guards row identity by the **library md5** (`G-ROWX`, :226-232), which is the stronger check. It carries `'P'`/`'S'` forward into the N artefact |
| `so1cr_xn.py:441` `r = rec["row"]` | **A FALSE POSITIVE OF THE SWEEP, AND WORTH NAMING.** `row` there is an **FD table row dict** (`emit({"kind": "control", "row": ctrl})`) — a different namespace entirely, nothing to do with PATCHED/SHIPPED |
| `so1cr_grade.py:737` `meta = {…, "row": j.get("row")}` | carries the propagated `'P'`/`'S'` **for display**; it is **never compared anywhere**, confirmed by enumerating every `["row"]` / `.get("row")` access in the module |

**A WIDER SWEEP ACROSS `cases/dafoam/` (excluding `curriculum_SO3a/`, which another lane owns) FOUND NO OTHER INSTANCE OF THE BROKEN FORM.**

**THE REGISTERED MAPPING, IDENTICAL IN ALL THREE CONSUMERS:**

```
ROW_LABELS = {"PATCHED": ("PATCHED", "P"), "SHIPPED": ("SHIPPED", "S")}
```

**THE LEG GROUP `(r14)` — RULE 14 MADE MECHANICAL.** `so1cr_rowlabel_sweep.py`, **ONE implementation, called by the guard suite rather than re-implemented in it** (a guard suite that runs its own copy of the logic proves nothing about the logic that ships). It:

1. requires **every** registered consumer to be **present** — a consumer renamed or deleted is reported **MISSING**, never clean (**fail closed**, leg r14e);
2. refuses on the **broken form** anywhere on an **executable** line, **carrying no whitelist of known sites** — a whitelist cannot fail on a site nobody has thought of yet;
3. refuses on any label **derived as `row[0]`**;
4. requires the **same** canonicalised mapping in all three consumers — three files each carrying a *different* mapping would satisfy a per-file check;
5. asserts call site (4) **positively**: the fixture must derive its label **from `ROW_LABELS`** and must not write the bare directory name.

**IT IS NEVER BELIEVED ON A GREEN ALONE. Its registered drive is FOUR STATES** (`so1cr_rowlabel_sweep_evidence.txt`):

| state | input | required | measured |
|---|---|---|---|
| **1** | `curriculum_SO1c`'s **own frozen instruments** — the code that actually died | **RED, naming every site** | rc = 1, naming `run_arm.sh:468`, `grade.py:997`, the concealing fixture, and both missing mappings |
| **2** | the repaired SO-1cR tree | **CLEAN** | rc = 0 |
| **3** | a **fourth call site** in the old form, planted into a copy of the repaired grader | **RED, naming file and line** | rc = 1, `so1cr_grade.py:1007` |
| **4** | a directory missing two consumers | **RED, `MISSING CONSUMER`** | rc = 1 |

**Shipped bytes proved byte-identical by md5 after all four states.**

> **THE SWEEP WAS WRONG TWICE BEFORE IT WAS RIGHT, AND BOTH WRONG TURNS ARE RECORDED IN ITS OWN DOCSTRING BECAUSE THE SECOND WOULD HAVE SHIPPED.** (i) A first version **grepped**, and fired on the word `row[0]` inside a unit *description* and on a unit asserting the grader's own *output* record — **a detector that fires on prose is a detector a reader learns to overrule.** (ii) A second version tokenized and dropped **every** `STRING` token — **which made it blind to both Python call sites, because the key it matches on IS a string**, and it **reported CLEAN ON THE BROKEN PREDECESSOR.** **That is a false clean, and a false clean is the same defect class as the fixture this item exists to repair.** It was caught only because state 1 — the known-broken positive control — is a *registered* part of the drive rather than a courtesy. Strings are now kept when identifier-like and replaced by a placeholder otherwise.

**WHAT THE SWEEP DOES NOT PROVE** is stated in §6 and registered as **P-ROW**: it is a detector over a registered consumer list, and it cannot prove a site *outside* that list does not exist. **The run is the test.**

## 8. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). The grading path is fixed at this commit: `so1cr_grade.py` md5 `a13cd4e7b53c5051abe697da485c3433`, asserted by the chain driver before staging and again before the grade.

**Queue entry `SO1cR_chain_wait.json`**, a **wait-wrapper**: `--case-id SO1cR_chain_wait`, `--precondition <SO-1bR run root>/E-S/so1b_E.json`, `--prefix so1cr_`, `--run-root <SO-1cR run root>`, `--deadline-s 172800`, `--driver-pidfile so1cr_driver.pid`, then `bash so1cr_chain_driver.sh MESH Ns-P Ni-P Ns-S Ni-S`; `cwd` = this directory; `ranks 4`; `cost_core_min_estimate 40.6`; `cap_core_min_registered 125.0`; `memory_floor_gb 8.0`; `cost_basis` derived / not measured; `permission bc0e687e`; `prereg_commit` = the full 40-hex sha of the commit introducing THIS file, **re-derived with `git log --format=%H --diff-filter=A -- <path>` and never from a commit subject line**.

**ENQUEUEING IS NOT AUTHORISATION**: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own, discharged on the sha, and is **not** discharged by this document or by the queue entry. **THIS LANE LEAVES THE ENTRY IN THE CASE DIRECTORY AND DOES NOT PLACE IT IN A QUEUE DROP DIRECTORY.** The runner polls the drop directory every 60 s, so **placing the file there IS arming**, and **arming is the supervisor's act, not this lane's**. Consequently **`TEAM-BINDING` is NOT CHECKED by this lane** — the validator can only check it on the queued copy in place, and performing that check would arm the entry. **An unchecked condition is reported as unchecked, never as passing.**

**Predicted outcome, so it cannot be written afterwards:** P-A, P-MESHID, P-1, P-2, P-4 through P-7, P-TB, P-I, P-mesh, P-CLOCK and P-ROW **HIT** (P-3 `NOT_MEASURED` pending AV-1R) → **both rows `GATE FAIL` on their `scotch` arms, both `simple` arms `PASS`, item `GATE FAIL`** — and the lab gains its first measurement of what a decomposition **method** does to a gradient **at an optimum**, with an FD table beside it.

---
