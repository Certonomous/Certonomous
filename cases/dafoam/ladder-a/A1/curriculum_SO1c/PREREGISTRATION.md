# CURRICULUM SO-1c — np-INVARIANCE OF THE A1 NACA0012 GRADIENT **AT SO-1b's OPTIMUM**, ACROSS THE DECOMPOSITION **METHOD** AT FIXED np = 4, WITH THIS CONFIGURATION'S OWN FD TABLE BESIDE IT, ON TWO TOOLCHAIN ROWS — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (H). Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

<!-- SO1C-CAP-MANIFEST v1 MESH=5.0 Ns-P=30.0 Ni-P=30.0 Ns-S=30.0 Ni-S=30.0 CEILING=125.0 RANKS_N=4 -->

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

**THIS ITEM IS RUNG 3 OF 4 FOR SO-1, AND IT IS NOT SO-2.** The lane's brief named the post-optimum verification rung "SO-2". **Sanaa's own §4 names SO-2 as something else entirely — the constraint-families ladder item — and her words govern.** The post-optimum verification rung is a rung *within* SO-1's per-case pattern, and SO-1b's own frozen document and queue entry already call it **SO-1c** (`curriculum_SO1b/PREREGISTRATION.md`, §0: *"SO-1c (post-optimum verification proper — the np-invariance spot row Sanaa's pattern names, and a second design point) is NOT frozen here"*; `SO1b_chain_wait.json`, `ladder`: *"SO-1c is a separate registration and is deliberately NOT frozen"*). The name is taken from those two documents rather than invented here. **The correction is reported to the supervisor and is not worked around.**

Every decision here is `[lab-attributed]`. Permission for the detached launch: Sanaa's own words boarded at **`bc0e687e`**; queue-first order `7def3c6b` / `73eccb1b` / `0b041d1a`; L-342 field classes `d4d0c29d`; R-RC approved in the directives file above (§0).

---

## 0. SCOPE — AND WHAT IS **NOT** NEW HERE, SAID FIRST

**Capability-grid cell (`docs/capability/dafoam_GRID.md`): `2D · steady · incompressible`, the np-INVARIANCE entry of "what was checked", and — because of §3d — the "gradients FD-verified" column.**

**SO-1c IS NOT THE FIRST np-INVARIANCE RUNG ON THIS CASE, AND THIS DOCUMENT SAYS SO ON ITS FIRST SCREEN.** The lane looked before it registered, and what it found is that **two thirds of the sub-items Sanaa's step 3 names are already bought and the third has a sibling**:

* **The re-solve at the optimum and the constraint check are SO-1b's**, already registered and frozen (`curriculum_SO1b/PREREGISTRATION.md` §3c: `G-CL` at `|CL − 0.5| ≤ 1.0e-4`, `G-GEO` over 23 geometric rows at the re-solve). **SO-1c does not re-buy either.**
* **AV-1 IS ALREADY "the family's first np-INVARIANCE rung"** on this exact case — `av1_run_arm.sh:3-4`: *"gradient at np = 1 / 2 / 4 (`scotch`), TWO ROWS (shipped + patched): the family's first np-INVARIANCE rung (`ADJOINT_VERIFICATION_STANDARD.md` §3)"*. AV-1 returned **`NOT A RESULT`** at G1 (`23dccf38`) and **AV-1R** is its frozen successor (`0c019d92`, queued at `74beec4c`), unrun.
* **AV-1's `av1_decomposeParDict_np4` has md5 `816f5ba44075fde47fa5db4269877bc8`** — **byte-identical to this item's `so1c_decomposeParDict_scotch`.** The scotch-at-np-4 configuration is not new and is not claimed as new.

**THREE THINGS ARE NEW, AND THEY ARE THE REASON THIS RUNG EXISTS. EACH IS SOMETHING AV-1 AND AV-1R DISCLAIM IN THEIR OWN §8, IN THEIR OWN WORDS.**

1. **THE DECOMPOSITION *METHOD* IS VARIED AT FIXED np — THE OTHER HALF OF THE STANDARD'S OWN DEFINITION.** `ADJOINT_VERIFICATION_STANDARD.md` §3 defines the check as the same gradient *"at np = 1 (the serial reference) and at np > 1 **(and, at fixed np, across `scotch` / `simple` / `hierarchical`)**"*. AV-1's §8: *"nothing about the `simple` or `hierarchical` decompositions (**scotch only**)"*. **No A1 rung has ever varied the method.** And the method axis is where this family's largest measured decomposition effect lives: A4 measured np=4 `scotch` at **8.95 %** against np=4 `simple 4×1×1` at **0.00054 %** on one mesh at one np — **a factor of 16,600** (`DAFOAM_CHARTER.md` §5; `PRIOR_WORK_INVENTORY.md:380`).
2. **THE DESIGN POINT IS AN OPTIMUM, NOT A BASELINE.** AV-1's §8: *"**nothing about an optimum**"*. `DAFOAM_CHARTER.md` §9's own argument for the final-design-point FD check — *"a gradient verified at iteration 0 is not verified at iteration 47"* — transfers to the decomposition without a word changed, and transfers **harder**: IDWarp's defect is a **mesh-deformation** defect with two regimes either side of its `axisMag` guard, and a deformed mesh is precisely where a partition-interface interaction would be worst. **No record in this lab measures decomposition sensitivity on a deformed mesh.**
3. **AN FD TABLE AT np = 4 — WHICH IS WHAT MAKES THIS A VERDICT RATHER THAN A SPOT CHECK.** AV-1 and AV-1R state the hole in their own gate: *"It carries **no FD table**, so it moves **no capability-grid verdict** on its own… **A wrong treatment could still pass G-NP by producing the same wrong gradient at every np** — which is why this rung is not an FD verdict, and the frozen text says so before the run."* That is **L-38** exactly (*"Decomposition-invariance is not correctness"* — A1's own serial-limiter arm agreed to `3.9e-04` across np while **both** analytics were **92.8 % wrong together**). Each SO-1c arm therefore buys **its own** central-FD table **at its own decomposition**, because `DAFOAM_CHARTER.md` §5 makes an FD reference part of a **configuration** and never carries one across np — the `W4_IDX16` carrying failure §5 names by name.

**WHAT IS DELIBERATELY *NOT* RE-BOUGHT.** The **np = 1 serial reference at x\*** is **SO-1b's own `E-<row>/so1b_E.json`**, read from disk and never recomputed. That artefact carries `design_point` (x\*), `adjoint` (the np = 1 gradient at x\*) and `identity` (the row's library hash) in one file, and it is **SO-1b's LAST ARM's artefact**, so it exists only if SO-1b's chain reached and completed the arm that produced what SO-1c reads. **Not one np = 1 primal is re-bought.**

**The mesh is A1's, 4,032 cells**, regenerated by this item's own `MESH` arm so the item is self-contained — **and because the standard defines this comparison "on the same mesh", mesh identity is then ASSERTED (`G-MESHID`, §3c) rather than assumed.** The FFD box is 5×2×2 → 8 `shape` functions + `patchV`; the objective is `CD` and the equality constraint `CL == 0.5`, exactly as SO-1a and SO-1b.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv` DOES NOT EXIST.**

`test -e` → **false** at **2026-08-27T21:40:44Z** (this lane, immediately after the case directory was created and before any instrument was written), and again as the first and last legs of `so1c_groot5_selftest.sh` (*"run root ABSENT before the test"* / *"run root ABSENT after the test (freeze condition)"*, `so1c_groot5_selftest_evidence.txt`).

**This item has burned 0 core-min of solver compute and CREATED NO CONTAINER OF ANY KIND.** Container census on the box: **16 before this lane's work and 16 after**, both read with `sudo -n docker ps -a -q | wc -l` and both printed in `so1c_groot5_selftest_evidence.txt`. Unlike SO-1a and SO-1b, whose guard suites each started a sacrificial `sleep` container, **this suite starts none** — the one leg that would have required one is named **NOT DRIVEN** in §7 rather than counted. **After the first arm container, gates are CLOSED**; changes land only as dated addenda that cannot alter a gate, threshold, cap or label (`VERIFICATION_CHARTER.md` §2b).

## 1a. THE DEPENDENCY ON SO-1b, ITS PRECONDITION ARTEFACT, AND THE TWO NO-LAUNCH BRANCHES

**(i) The queue entry is a WAIT-WRAPPER.** `cases/dafoam/_common/dafoam_wait_then_launch.sh`, precondition:

> **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt/E-S/so1b_E.json`**

**AND NOT SO-1b's `CHAIN_DONE` MARKER, THOUGH ONE EXISTS.** `so1b_chain_driver.sh:196` writes `CHAIN_DONE` on **every exit of a started chain — including a failed one** — so it fires on a chain that stopped at `O-P` and produced nothing SO-1c can read. **`E-S` is SO-1b's LAST registered arm**, so its artefact appears only if the whole chain ran to the end and both rows exist. **A last-arm artefact is a stronger precondition than a chain marker, and where both exist the artefact is registered.** (SO-1b had to use a last-arm artefact because SO-1a has no marker at all; here the choice is made on the merits.)
**Bound: `172,800 s` (48 h), registered.** Derivation: SO-1c waits behind **two** unrun items, not one. D6's live `O_mp` arm (started 14:09:24Z, 2,000 core-min cap at 4 ranks ≈ 8.3 h wall, so ≤ 8 h from this freeze) **+** SO-1a's ceiling wall (75.0 core-min at 1 rank = 75 min) **+** SO-1a's five H5 windows and its bounded aggregate wait (at most one 4 h wait precedes an outcome) **+** SO-1b's own 86,400 s wrapper bound is *not* additive here because SO-1b's wrapper and SO-1c's poll concurrently, but SO-1b's **ceiling wall** is (115.0 core-min at 1 rank = 115 min) **+** SO-1b's own five H5 windows and one bounded 4 h aggregate wait ≈ **8 + 1.25 + 4 + 1.92 + 4 ≈ 19.2 h**, doubled to **48 h** because the box is at 89 % CPU against an 85 % runner ceiling and every one of those figures is a *floor*. The wrapper polls every 30 s, writes every wait to `STATUS.SO1c_chain_wait`, applies G-ROOT.5 immediately before exec, and **launches nothing at the bound**.

**(ii) `G-SO1B`, in `so1c_chain_driver.sh`, BEFORE the run root is created and BEFORE the first launcher call.** It reads SO-1b's newest `SO1b_grade_*.json` **and, independently, SO-1b's own `O-<row>/so1b_O.json`**, and a disagreement between the two channels REFUSES.

**WHAT IS CHECKED IS NOT SO-1b's ITEM VERDICT, AND THAT DISTINCTION IS INHERITED RATHER THAN RE-LEARNED.** SO-1b's own registered predicted outcome is item **`GATE FAIL`** — its SHIPPED row is predicted to fail band D at `shape[6]` at the optimum, and **that failure is SO-1b's finding**. Gating on the item verdict would kill SO-1c in exactly the case SO-1b expects. The same defect was caught one rung earlier, in SO-1b's own brief, against SO-1a. **What SO-1c consumes, per row, is narrower: x\*, the np = 1 gradient at x\*, and a real flow at x\*.**

**THE ACCEPTANCE IS ASYMMETRIC BY REGISTRATION, WITH ITS REASON GIVEN BEFORE THE RUN:**

| row | `G-OPT` accepted | `G-CL` accepted | why |
|---|---|---|---|
| **PATCHED** | **`PASS` only** | `PASS` | it is the CONTROL, and "post-optimum verification" at a point that is not an optimum is a different item. D1 and D13's five restarts converged on this exact problem **six times**, so this is a band the problem has cleared six times |
| **SHIPPED** | **`PASS` or `GATE REACHED`** | `PASS` | SO-1c's shipped arms ask what a **deformed mesh** does to a **parallel** gradient. That question is meaningful at the design point the shipped toolchain reached whether or not IPOPT converged there: an iterate-30 design still carries a deformed mesh and a real flow |

**`G5E`, SO-1b's endpoint FD gate, IS DELIBERATELY NOT READ ON EITHER ROW** — SO-1c buys its own FD table at np = 4, and `DAFOAM_CHARTER.md` §5 forbids carrying an FD reference across np, so SO-1b's band-D verdict at np = 1 is not a precondition of anything here. **Driven** in `so1c_groot5_selftest.sh` leg (e7).

**THE TWO REGISTERED NO-LAUNCH BRANCHES, both at ZERO core-minutes, named in advance:**

| branch | trigger | mechanism | rc | SO-1c item verdict | cost |
|---|---|---|---|---|---|
| **N1** | SO-1b never reaches `E-S` (any earlier arm stops, or SO-1b is `BLOCKED` by its own N1/N2) | the wrapper's precondition never appears; it closes at the 172,800 s bound and launches nothing | **6** | **`BLOCKED`** | **0 core-min** |
| **N2** | the precondition exists but SO-1b's rows do not meet the table above — or its grade is absent, unreadable, names no `G-OPT`/`G-CL` verdict, or the two channels disagree | `G-SO1B` in the driver, before the run root is created | **7** | **`BLOCKED`** | **0 core-min** |

Both branches are the safe direction and both are registered before compute. Driven at legs (e1)–(e5).

## 2. ARMS — five, in this order, one detached chain, TWO ROWS × TWO DECOMPOSITIONS, np = 4 ON EVERY SOLVER ARM

| arm | kind (G1) | image (row) | ranks | decomposition | cpuset | mem | task | artefact | terminal marker |
|---|---|---|---|---|---|---|---|---|---|
| **MESH** | SCRIPT | SHIPPED | 1 | — | 10 | 4g | the tutorial's own `preProcessing.sh` + `checkMesh` + `sha256sum constant/polyMesh/points*` | `MESH/checkMesh.log` | `Mesh OK.` |
| **Ns-P** | SOLVER | **PATCHED** | 4 | **`scotch`** | 10,11,12,13 | 6g | `so1c_xn.py -mode N -optimum so1b_E.json` | `Ns-P/so1c_N.json` | `SO1C_N_WRITTEN` |
| **Ni-P** | SOLVER | **PATCHED** | 4 | **`simple 4×1×1`** | 10,11,12,13 | 6g | as above | `Ni-P/so1c_N.json` | `SO1C_N_WRITTEN` |
| **Ns-S** | SOLVER | SHIPPED | 4 | **`scotch`** | 10,11,12,13 | 6g | as above | `Ns-S/so1c_N.json` | `SO1C_N_WRITTEN` |
| **Ni-S** | SOLVER | SHIPPED | 4 | **`simple 4×1×1`** | 10,11,12,13 | 6g | as above | `Ni-S/so1c_N.json` | `SO1C_N_WRITTEN` |

Chain: `so1c_chain_driver.sh MESH Ns-P Ni-P Ns-S Ni-S`, stops at the first non-zero rc, then runs the frozen grader on whatever exists (its rc is INFRASTRUCTURE, never the verdict). **The PATCHED row runs FIRST by registration** — it is the control for the shipped row beside it. **Both rows are bought on ONE mesh generated once in the SHIPPED image** (`DAFOAM_CHARTER.md` **§6** — *"Shipped and patched are always two rows, and toolchain identity is an image ID and a library hash, never a version string"*; **§11 is the lessons-numbering clause**, and the "§11" mis-citation carried by `so1a_run_arm.sh:184` and `SO1a_chain.json` is inherited by **no** file in this item).

**np = 4 IS A DEPARTURE FROM SO-1a AND SO-1b AND IT IS THIS ITEM'S ENTIRE SUBJECT.** `DAFOAM_CHARTER.md` §5 says *serial before parallel*: SO-1a bought the serial gradient and SO-1b bought the serial optimum, so **the serial half is bought and this rung is the parallel half it licenses.** MESH stays at np = 1 because mesh generation is not a decomposition question. DAFoam runs `decomposePar` itself at np > 1 (`pyDAFoam.py:1454 runDecomposePar`) from the arm's own `system/decomposeParDict`, which is a **frozen, md5-pinned file per decomposition**, overlaid at staging and **re-asserted on the overlaid copy** — a copy that silently failed would otherwise leave the tutorial's own dict in place and the arm would run a decomposition nobody registered.

**THE CPU PLACEMENT IS DISJOINT BY REGISTRATION, NOT BY LUCK.** `10,11,12,13` — four distinct cores for four ranks, because `--cpus=4` does not hand out four distinct cores (the D13 lane measured 0.250 cores delivered against a 1.0-core quota with the box 61 % idle). Checked against every registered sibling placement: **D6's `2,3,4,14`**, **D4-SHIPPED's `5,6,7,9`**, **SO-1a's and SO-1b's `9`**. `10-13` intersects none of them. **At np = 4 the grader's delivered-cores floor DOES apply** (it does not at np = 1, which is why SO-1a and SO-1b could disclose an overlap and this item cannot).

**THE REGISTERED FD DESIGN AT np = 4** — identical components and steps to SO-1a's at the baseline and SO-1b's at the optimum, which is what makes the three comparable. Components **`shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`** plus the planted-zero control **`CTRL`**; steps **`shape`: {1e-2, 1e-3, 1e-4}**, **`patchV[1]`: {1e-1, 1e-2, 1e-3}** degrees; central differences, both signs; reference = the middle step; plateau = agreement with at least one neighbour to 10 %. Step-set justification is **by citation and not re-derived**: `A_stepsize_study.md` measured the curve flat at 2.5–3.0 % from 1e-4 to 3e-2 **on this case**.

**THE PLANTED-ZERO CONTROL (rule 3), in the instrument AND in the grader, AND ON THE HEADLINE GATE ITSELF.** `CTRL` carries a synthetic row with derivative exactly `0.0` and a PLANTED row with `CD_plus = CD_optimum + 1.234e-03`; the instrument writes both, **re-reads them from disk**, and exits 2 if the read-back cannot see them. The grader re-checks both, re-plants `PLANT` into every physical derivative and refuses unless every value moved by exactly `PLANT` — **and additionally re-plants a `1 + 10 × S_G_BAND` scaling into the np = 1 reference and REFUSES unless `g_npinv` reads `GATE FAIL` on it.** The np-invariance reader is the one whose `PASS` would otherwise be the item's whole claim, so it is the one shown able to fail.

## 3. GATES, THRESHOLDS AND LABELS — `so1c_grade.py`

All bands are frozen now. Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

### 3a. Completion, inherited whole from SO-1a

**G1** — the five rule-4 clauses **printed individually per arm**: `C1` rc VALUE (physics, from `docker inspect .State.ExitCode`), `C2` terminal marker, `C3` artefact present, `C4` age guard, `C5` no fatal token (**REFUSES REGARDLESS OF rc**). Any clause failing on any arm → **`NOT A RESULT`**, comparator exit 2. **R-RC** as Sanaa approved it (directives §0). **L-342 field classes** (`d4d0c29d`). **The age-guard datum is resolved BY EXISTENCE over `0/U` and `0/U.gz`**, the AV-1/AV-2 lesson. **`G-M2`** — `cells == 4,032` → `PASS` else `GATE FAIL`.

**AND THE AGE-CHECKED LIST CONTAINS ONLY WHAT THIS RUN PRODUCES.** `so1c_N.json` and `so1c_N.jsonl` are age-checked. **`so1b_E.json`, `so1c_runScript.py`, `so1c_xn.py` and `system/decomposeParDict` are STAGED INPUTS**, listed in the comparator's own `STAGED_INPUTS` and **excluded by name**. `d4s_f3s_grade.py:61` listed the staged `OptView.hst` among its age-checked ARTEFACTS, making that clause **unsatisfiable by construction** and forcing D4S-F3S to `NOT A RESULT` with **19 of 20 gate readings passing**. The launcher `cp -a`s the staged input **before** touching the age datum, so a staged input is provably OLDER than the datum — and the exclusion is **driven** at grader unit **U40**, which asserts the staleness *and* the item's `PASS` together, rather than trusting the comment.

### 3b. `G-NP` and `G-METHOD` — np-INVARIANCE AT THE OPTIMUM. **THE BAND IS NOT THIS LANE'S.**

`docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md` §3 defines the check and freezes the band. **All three numbers are INHERITED BY CITATION and are NOT re-derived here:**

| quantity | band | source (verbatim from the standard's own table) |
|---|---|---|
| objective spread `s_J = \|J(np) − J(1)\| / \|J(1)\|` | **≤ 2.2e-5** | the lab's measured partition-reproducibility upper bound (`PARALLEL_GATE_DOCTRINE.md:38, :194-198`, commit `fd9bf1b6`); B3 measured 2.9e-7, inside by 75× |
| gradient spread `s_g = ‖g(np) − g(1)‖₂ / ‖g(1)‖₂` | **≤ 1.0e-3** | 6× the family's measured floor of 1.1–1.7e-4 (B3, commit `bb5088c4`) and **50× below band D**; A4 `simple` 5.4e-6 sits inside, A4 `scotch` 8.95e-2 outside by 90× |
| per-component sign agreement | **0 flips** (on components with `\|g₁,ᵢ\| ≥ 1e-14`; smaller named and skipped) | `VERIFICATION_CHARTER.md:845` |

> **⚠ THE BAND FOR THIS GATE IS NOT BAND D, AND THE DIFFERENCE IS 50×.** A lane that reached for the familiar `FD_BAND_PCT 5.0` here would have registered a gate **fifty times too loose to see the effect the rung exists to find** — A4's measured `scotch` disagreement of 8.95e-2 is 90× outside `1.0e-3` but only 1.8× outside 5.0e-2. The `50×` relation is asserted arithmetically in grader unit **U3**.

* **`G-NP`, per arm**, against **SO-1b's np = 1 serial reference at x\***, for `CD` and `CL` separately. **The reference is read on TWO independent channels** — the copy the instrument carried into its artefact, and the comparator's own read of the same `optref/<ROW>/so1b_E.json` — and **a disagreement REFUSES** (driven, U12). A reference whose `nprocs ≠ 1` REFUSES (U11): the basis must be the serial arm, never another parallel one.
* **`G-METHOD`, per row**: `scotch` against `simple 4×1×1` **at fixed np = 4**, on the same band. **`simple 4×1×1` is the REFERENCE limb and `scotch` the graded limb, fixed here before the run** because A4 measured `simple 4×1×1` at 0.00054 % against FD and `scotch` at 8.95 % — the cleaner limb is the reference, and the convention is registered rather than chosen after the numbers arrive.
* **`G-DECOMP`**: every arm's artefact must name the method it was registered for, the subdivision for `simple`, and an `nprocs` that agrees with the dictionary's own `numberOfSubdomains` — **cross-asserted on two sources**, because two numbers from one source can both be wrong. Any disagreement **REFUSES** (U15, U16, U17). *A parallel gradient table with no decomposition column is what `DAFOAM_CHARTER.md` §5 forbids; here the column is a gate.*

### 3c. `G-MESHID` — "the same mesh" is ASSERTED, not assumed

The standard defines np-invariance as the same gradient at the same design point **"on the same mesh and image"**. This item regenerates its own mesh rather than reading one across a run root, **so mesh identity is not free.** The `points` sha256 this item's MESH arm prints must equal the one SO-1b's MESH arm printed (copied into `optref/so1b_mesh_points_sha256.txt` by the driver at staging).

* **equal** → `PASS`.
* **unequal** → **`GATE FAIL`**, and the finding is named: *mesh regeneration is not deterministic*, so "the same mesh" does not hold and the comparison is not the one the standard defines.
* **SO-1b's fingerprint absent or unreadable** → **`NOT A RESULT`**, never a pass. Mesh identity is a **physics precondition** of this comparison, so an unknown reference is not a bookkeeping gap (U21, U22).

### 3d. `G5N` / `G5cN` — the FD verdict at np = 4, and `G-TB`

Per arm, `grade_components` against **that arm's own np = 4 FD table**, on `CD` (`G5N`) and on `CL` (`G5cN`). **Band D `FD_BAND_PCT = 5.0` per component with sign agreement, band E `AGG_BAND_PCT = 5.0` aggregate, plateau `PLATEAU_TOL_PCT = 10.0`, fewer than 3 graded → `NOT A RESULT`.** **These three are INHERITED BY CITATION from SO-1a and SO-1b, which inherit them from `curriculum_D4/PREREGISTRATION.md:82` and `D7FR:228-229`; they are byte-identical to SO-1a's and are not re-derived** (asserted at U4).

**`G-TB`** — the `DAFOAM_CHARTER.md` §4 trivial baseline at the deliberately wrong step (`shape` 1e-8, `patchV` 1e-6), per arm. If the WRONG step also passes band D on **2 or more** of the five components, that arm's verdict is **WITHDRAWN to `NOT A RESULT`** — the standing-rule-5 direction, applied to the trivial baseline (U26, U27).

**THIS IS THE SUB-GATE THAT MAKES THE ITEM A VERDICT.** AV-1 and AV-1R carry no FD table and say in their own frozen text that a wrong treatment could pass `G-NP` by being equally wrong at every np. Unit **U23** drives exactly that state: a 7 % FD error planted with `G-NP` still reading `PASS`, and the arm still lands `GATE FAIL`.

### 3e. `G-XSTAR` — an identity assertion, **deliberately not a gate on the design vector**

D13 / C-71 measured this problem's design vector **NON-UNIQUE** and its drag **UNIQUE**: **15 of 15** restart pairs `DIFFERENT` on design, **0 of 15** on drag. **No verdict in this item rests on a design vector.** `G-XSTAR` asserts only that the point each arm solved at is byte-for-byte the point SO-1b bought — a provenance check on a **consumed input**, not a physical claim — and refuses otherwise (U19). The distinction is written into the artefact itself (U20).

### 3f. `G-CLOCK` and `G10` — **the cap gate and the cost claim read different frames, on purpose**

**THE DEFECT, MEASURED.** A peer lane found on D6 2026-08-27, and this lane confirmed present in **both SO-1a and SO-1b**, that the cap is a `timeout -k 60 $TMO` **inside** the container while `core_min` is a wall bracketed around `docker run -d` **on the host** (`so1b_run_arm.sh`: `T0` at :495 before `docker run` at :505, `T1` at :544 after a `sleep 10` poll, `WALL=T1-T0` at :545, `CORE_MIN` at :568; `so1b_grade.py:1003-1010` then grades that host figure against the cap, and its own unit U46 drives it). **An arm stopped exactly at its own registered deadline therefore records a wall ABOVE its cap and trips its own cap limb — a `GATE FAIL` manufactured by the measurement frame, not by the run.** At 4 ranks the poll granularity alone is `10 × 4 ÷ 60 = 0.667` core-min.

**THE REPAIR IS NOT A WIDER CAP.** Silently widening a cap to absorb a frame error hides the error and spends the difference. Instead **both frames are measured from records that already exist** — `.State.StartedAt` / `.State.FinishedAt`, the kernel's own container clock, already written into `<ARM>_<stamp>.inspect.txt` — and:

* **`G10` grades `core_min_container`**, the frame the deadline lives in;
* **the COST claim uses `core_min`**, the host frame, which is the frame the box is occupied in and is the **larger** of the two;
* their difference is written to the ledger as `clock_frame_delta_core_min` and reported per arm — **this family's first measurement of the gap rather than an estimate of it**;
* **an unreadable container clock is INFRASTRUCTURE**: `G10` falls back to the host frame **and names the arm in `frame_fallbacks`** — a limb that could not be evaluated in its own frame is reported, never silently passed.

Driven at **U28** (host 30.4 above a 30.0 cap, container 29.9 inside → `PASS`), **U29** (container 30.8 above the cap → `GATE FAIL`; the frame was corrected, the cap was not widened), **U30** (unreadable clock → fallback named), **U31** (both totals reported). The container clock survives on the `inspect.txt` fallback channel too, so it is available even when the ledger row is lost.

### 3g. `G9` / `G11` / `G12`, and the item composition

**`G9`** — ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process `libidwarp.so` md5 must all name the row's toolchain; **plus `G-ROWX` across the item boundary: the two arms of one row must share a library hash, and it must be the hash of the SO-1b artefact they read.** A row is an image hash, never a directory name. **`G11`** — OOM hard. **`G12`** — per-arm cpuset, and **at np = 4 the delivered-cores floor of 3.0 (0.75 × ranks) applies**.

**Composition, registered here:**
* **an ARM** is `NOT A RESULT` if `G-TB` withdraws it or any of `G-NP` / `s_J` / `G5N` / `G5cN` is `NOT A RESULT`; `GATE FAIL` if any is `GATE FAIL`; else `PASS`.
* **a ROW** is the composition of its two decomposition arms **and** that row's `G-METHOD`.
* **the ITEM** is `NOT A RESULT` if either row is or `G-MESHID` is; `GATE FAIL` if either row is or any of `G-M2` / `G-MESHID` / `G9` / `G10` / `G12` is; else `PASS`.

**No grid family exists, so standing rule 5 has no row and NO GCI IS QUOTED.** **This item quotes NO improvement percentage, so `G-D7R` has no row here — and nothing in this item lifts SO-1b's `SUPPRESSED_BY_G_D7R`; only SO-1b's own attribution artefact can.**

## 4. COST — DERIVED FROM NAMED ANCHORS, AND THE ANCHOR RISK NAMED FIRST

> **THIS FAMILY'S ESTIMATING ERROR IS IN THE ANCHOR CHOICE, NOT THE RATE (C-182).** A 709 s arm-total anchor carried 32.2 s/primal of overhead where the true rate was 25.5 s/primal. Live evidence that the risk is current: **C-183** measured D5's `O48` at ratio **1.0714, 97.8 % of its band's upper edge**; and a peer lane measured D6's `O_mp` at **31.46 core-min/major against a registered anchor that projects 1.57× its cap at `max_iter`**. **So both anchors are named below, with what each was measured on, and the LARGER is taken.**

| anchor | what it was MEASURED on | value |
|---|---|---|
| **A — like-for-like whole arm** | A1's own mainline rung: `run_model` + `compute_totals` + `check_totals` at **np = 2**, `DASimpleFoam`, **this exact 4,032-cell mesh** (`PRIOR_WORK_INVENTORY.md:47`, citing `ladder-a/A1_naca0012_incompressible.md` stage table) | **3.51 core-min MEASURED** |
| **B — component-built** | **C-158** AV-1 `X1-S`: setup + 1 primal + 2 adjoints + colouring, **np = 1, this exact case** → 1.017 core-min MEASURED; **C-154** D15 `F-S − X-S`: ≥ 31 primals, **np = 2, this mesh** → 2.066 core-min MEASURED | **1.017 + 2.066** |
| **MESH** | **C-154 (D15), C-156 (D16), C-158 (AV-1)** — the same 4,032-cell pyHyp mesh at 1 rank, three independent measurements | **0.167 core-min MEASURED** |

**The np = 2 → np = 4 conversion assumes ZERO SPEEDUP** — at 1,008 cells per rank the solve is communication-bound, and A4's own 2,777-cell case showed no useful scaling. So core-minutes scale by the rank ratio:
* Anchor A: `3.51 × 2` = **7.02 core-min/arm**.
* Anchor B: `1.017 × 4` + `2.066 × 2` = `4.068 + 4.132` = **8.20 core-min/arm**.

**The larger (B) is taken and margin is added for np = 4 colouring, which is partition-dependent and is where A3 OOM'd: point 10.0 core-min per solver arm.** Cross-check against the family's own np = 4 registration: **AV-1 registered 4.0 core-min for an np = 4 `X` arm** (primal + 2 adjoints, **no FD table**) at an assumed parallel efficiency of 0.6; 10.0 here is that arm plus a ~33-primal FD block, at a **more conservative** efficiency assumption (0.5).

> **⚠ THE HONEST GAP, NAMED RATHER THAN BURIED: NEITHER ANCHOR WAS MEASURED AT np = 4 ON THIS CASE.** The zero-speedup scaling is an **assumption**, not a measurement, and it is the single largest source of error in this estimate. It is registered as prediction **P-I** so the first fire converts it into a `docs/COST_CALIBRATION.md` row whether it is right or wrong.

| arm | ranks | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| MESH | 1 | **0.167** | 5.0 | 300 s | 4g |
| Ns-P, Ni-P, Ns-S, Ni-S | 4 | **10.0** each | 30.0 each | **450 s** | 6g |
| **TOTAL** | | **40.2** | **CEILING 125.0** | | |

**THE CAP FITS THE REGISTERED WORK BY ARITHMETIC** — the `D5-PREREG-DEF-1` class (a deadline that cuts before the registered work completes) is named and excluded. Each solver arm's registered work is 1 primal + `compute_totals` + 2 × (5 components × 3 steps) + 2 × (5 × 1 TB step) + 1 repeat ≈ **34 primals + 2 adjoints**. Anchor A's comparable whole arm took **105 s wall at np = 2**; at zero speedup that is ~105 s wall at np = 4, against an in-container deadline of **450 s — a 4.3× wall margin**. In core-minutes the cap is **3.0× the point**. `G-CAP-PREREG` asserts the launcher's cap table against line 6 of this document on two channels before any container starts.

**Band `[22.0, 80.0]` core-min**, set wide because the np = 4 scaling is an assumption. **Dollars DERIVED at $0.0513/core-h, REPORTED-BY-OWNER, never measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5): point **$0.03437**, band top **$0.06840**, ceiling **$0.10688**. **Already spent: 0 core-min of solver compute, and 0 containers created.**

**Memory 6g at np = 4 and the H5 floor of 8.0 GiB are AV-1's and AV-1R's registered figures for np = 4 on this exact mesh** (`av1_run_arm.sh:173`, `av1_chain_driver.sh:45`, `av1r_chain_driver.sh:103`), inherited by citation and not re-derived by a lane that has not measured them.

## 5. THE REGISTERED PREDICTIONS — written before they run, and falsifiable

| id | prediction | basis | what a MISS means |
|---|---|---|---|
| **P-A** | `cells == 4,032` | three prior measurements of this mesh | the mesh is not A1's |
| **P-MESHID** | this item's `points` sha256 **equals** SO-1b's | pyHyp is expected deterministic | **a mesh-regeneration-determinism finding**, and the item goes `NOT A RESULT` — registered so it cannot be reinterpreted afterwards |
| **P-1** | the **`scotch`** arms fail `s_g ≤ 1.0e-3` on **at least one row** | A4 measured np=4-`scotch` at **8.95e-2**, 90× outside, on 2,777 cells with the patched toolchain; A1's mesh is the same order and carries the same `cellLimited` scheme A4's mechanism is gated by | **the effect is absent at an optimum on this case** — itself a finding, and a strong one |
| **P-2** | the **`simple 4×1×1`** arms pass `s_g ≤ 1.0e-3` on **both rows** | A4 measured `simple 4×1×1` at **5.4e-6**, inside by 185× | the clean decomposition is not clean here |
| **P-3** | `s_g` at the **optimum** exceeds `s_g` at the **baseline**, same row and decomposition — **THE RUNG'S OWN REASON** | §9's "verified at iteration 0 is not verified at iteration 47", transferred to the decomposition; IDWarp's defect is a mesh-deformation defect | **decomposition error is DESIGN-INDEPENDENT**, which contradicts the argument this rung is built on and would itself be the finding. **Scored `NOT_MEASURED` unless AV-1R has supplied a baseline figure — registered as `NOT_MEASURED` in the comparator NOW (U52) so an absent reference can never become a silent HIT** |
| **P-4** | `shape[6]` carries the largest per-component share of the scotch disagreement | idx6 carries **82.7 %** of A1's squared-error norm (`A_stepsize_study.md:53`) | the LE component is not the locus at np > 1 |
| **P-5** | `s_J ≤ 2.2e-5` on **every** arm | B3 measured 2.9e-7; the objective is far more robust than the gradient | a converged objective that moves under decomposition — a louder finding than a gradient that does |
| **P-6** | the PATCHED `simple` arm is FD-`PASS` on ≥ 4 of 5; the PATCHED `scotch` arm is **not** | the pair that turns a spot check into a verdict | the FD table does not separate the decompositions |
| **P-7** | the SHIPPED rows fail band D at `shape[6]` at **both** decompositions | the IDWarp LE defect, `11.43 %` at A1's baseline | the defect is decomposition-dependent |
| **P-TB** | the trivial baseline fails ≥ 4 of 5 on **every** arm | h = 1e-8 is below the measured primal repeatability | the FD gate is not measuring the step |
| **P-I** | total in **[22.0, 80.0]** core-min | §4 | **the np = 2 → np = 4 zero-speedup assumption is wrong**, and the calibration row says by how much |
| **P-mesh** | MESH wall ≤ 120 s | three prior measurements | — |
| **P-CLOCK** | the host frame exceeds the container frame on **every** arm, and the margin is reported | the host wall brackets the container start and the poll granularity | the frame model is wrong |

**REGISTERED OUTCOME, so it cannot be written afterwards: P-1 and P-2 HIT → the `scotch` arms `GATE FAIL`, the `simple` arms `PASS`, BOTH ROWS `GATE FAIL`, ITEM `GATE FAIL`** — and the finding is that **SO-1's entire graded np = 1 result, SO-1a's gradient and SO-1b's optimum alike, is not carryable to np = 4 under `scotch`, which is DAFoam's own default decomposition.** That is a large, useful negative, and it is exactly the shape of finding SO-1a and SO-1b also registered in advance.

## 6. WHAT THIS ITEM WILL NOT ESTABLISH

**Nothing at np = 2 or np = 3** — AV-1R buys the np sweep and this item buys the method sweep; A4's np=3 6.05 % point is not re-measured. **Nothing about `hierarchical`**, the third method the standard names. **Nothing about a second design point or a second start** — D13 already measured the basin on this problem and this item does not re-open it. **Nothing about SO-1b's own verdict**: SO-1c does not re-grade SO-1b, does not convert any SO-1b label into anything else, and does not lift its `SUPPRESSED_BY_G_D7R`. **No improvement percentage is quoted anywhere in this item.** **Nothing about the other four `shape` functions or `patchV[0]`.** **No dot-product test and no complex step.** **No grid family, no GCI, no Roache triple** — standing rule 5 has no row here. **Nothing about a mesh other than A1's 4,032 cells**, and nothing about the transonic RAE2822 half of Sanaa's SO-1 sentence. **Nothing about the constraint FAMILIES — that is SO-2's subject**, and §0 records what this lane established about its scope. A `scotch`-vs-`simple` divergence of 0.000 % would be reported with its number and would **not** be read as "the defect is absent"; P-1 names the arms where a difference is expected and P-3 names the consequence looked for.

## 7. FROZEN INSTRUMENTS, AND EVERY GUARD DRIVEN — WITH THE ONE LEG THAT WAS NOT

**Instrument md5s (frozen at this commit; the driver asserts them before staging and again before every arm):**

| file | md5 |
|---|---|
| `so1c_xn.py` | `63d13c88fb915ab7695d6f1a9383a4ed` |
| `so1c_grade.py` | `32af1c494db6884144151c7e7d7e81af` |
| `so1c_run_arm.sh` | `777c33117dd65d882a9be04d27c07526` |
| `so1c_chain_driver.sh` | `55614d4aa953fee29ceccbc7c1785baf` |
| `so1c_runScript.py` | `0557da51f6f179f6de865144343c499f` (byte copy of the shipped INCOMPRESSIBLE tutorial `runScript.py`) |
| `so1c_decomposeParDict_scotch` | `816f5ba44075fde47fa5db4269877bc8` (**byte-identical to AV-1's `av1_decomposeParDict_np4`**) |
| `so1c_decomposeParDict_simple` | `194c330803077f0ffa4341f468c09768` |
| `so1c_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` |

**Toolchain, RE-VERIFIED LIVE at 2026-08-27T22:05Z against `sudo -n docker image inspect --format '{{index .RepoDigests 0}}'`, not read from a stale inventory** (`TOOLCHAIN_INVENTORY.md` §3's list was stale by its own Amendment A1.2):

| row | image | digest, READ LIVE | library md5 |
|---|---|---|---|
| SHIPPED | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` ✓ | `f0fcb488e0e98156575cd19548e91663` |
| PATCHED | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` ✓ | `85f59e87253e0a71a813f64ca6e4c425` |

> **THE LIBRARY md5s WERE *NOT* RE-VERIFIED LIVE, AND THAT IS STATED RATHER THAN GLOSSED.** Reading `libidwarp.so` inside an image requires **starting a container**, and this registration is made under an explicit zero-containers instruction. The two values are inherited by citation from SO-1a, SO-1b and AV-1, all three of which register the same pair. **They are enforced at run time by `G9` and `G-ROWX`, which read the value the container itself prints and the value the artefact records** — so the claim is checked by the run, not by this document.

**Grader selftest — `so1c_grade_selftest_evidence.txt`: 53 units, 0 fail, under `python3` AND `python3 -O`, with `__pycache__` cleared before each run.** Every new gate carries a planted fixture that drives it to fire, and the band is driven on **both sides** (U6 inside, U7 outside) so it is a threshold and not a direction.

**MUTATION CONTROLS — seven of eight flip units, AND THE ONE THAT DOES NOT IS REPORTED AS PROVING NOTHING:**

| mutation | units flipped |
|---|---|
| `S_G_BAND` 1e-3 → 1e-1 | U3, U5, U7, U13 |
| `S_J_BAND` 2.2e-5 → 2.2e-2 | U3, U9 |
| `G-METHOD` always `PASS` | U13 |
| `G-MESHID` always `PASS` | U21 |
| `G10` gate reads the HOST frame | U28, U31 |
| `STAGED_INPUTS` name broken | U40 |
| the np-plant control disarmed | U11 |
| **`SIGN_FLIP_MAX` 0 → 9** | **NONE — AN INERT MUTATION THAT PROVES NOTHING** |

**The inert mutation is not hidden; it is measured and recorded as unit U53.** A sign flip on any component above the near-zero floor **necessarily** drives `s_g` far beyond `1.0e-3` — the fixture's smallest non-zero component, `shape[6] = 0.007` against a reference norm of ~0.107, gives `s_g ≈ 0.13`, **130× the band** — so the sign-flip limb can never be the **sole** cause of a `GATE FAIL` and **is not independently load-bearing**. It is kept because the standard registers it and because it **names** the failure mode in the record (a reader sees *"sign flip at index 6"*, not only *"s_g = 0.13"*), and this document does not claim it as an independent gate. *(This is the fourth instance in two days of "a mutant that changes no verdict is not evidence".)*

**Guard selftest — `so1c_groot5_selftest_evidence.txt`. GUARD PLACEMENT PROVED BY LINE NUMBER, because a guard placed after the destructive step is decoration and placement has been the defect five times in this family:**

`so1c_run_arm.sh`: G-ROOT.1/.2/.3 pass **:145**; **G-ROOT.5 pass :304**; **G-CAP-PREREG pass :369**; **G-ROW pass :435**; **G-OPTDEP pass :469**; **the FIRST destructive `sudo -n rm -rf "$WORK"` :482** (MESH) and **:501** (solver); `docker run -d` **:614**; G-CLOCK **:735**.
`so1c_chain_driver.sh`: **G-SO1B refuses :100 / passes :162**; **the run root is created :180**; the optref is staged **:207**; **the first launcher call :288**.
**Every guard precedes every destructive step and every spending step.**

> **ONE LEG IS NOT DRIVEN, AND IT IS NAMED RATHER THAN COUNTED.** `G-ROOT.5` leg (a)'s **positive** side — *"a RUNNING container already carries this item's prefix and arm"* — can only be driven by **creating a container**, which this registration's zero-container instruction forbids. SO-1a and SO-1b each started a sacrificial `sleep` for it; this suite starts none. **The leg is printed as `[NOT DRIVEN]`, is excluded from the pass count, and the one-line command that drives it is printed in the evidence for the supervisor to run before first compute.** Its **negative** side is driven (no `so1c_` container exists and the guard passes), and the **ordering** assertion — G-ROOT.5 before the first `rm -rf`, before `docker run` — is driven by line number at leg (b2).

**`ast.Assert` = 0** in `so1c_grade.py` and `so1c_xn.py`, with the counter shown counting a planted assert (U49, U50). **Classifier denials in this lane while building SO-1c: none.**

## 8. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). The grading path is fixed at this commit: `so1c_grade.py` md5 `32af1c494db6884144151c7e7d7e81af`, asserted by the chain driver before staging and again before the grade.

**Queue entry `verification/queue/dafoam/SO1c_chain_wait.json`**, a **wait-wrapper**: `--case-id SO1c_chain_wait`, `--precondition <SO-1b run root>/E-S/so1b_E.json`, `--prefix so1c_`, `--run-root <SO-1c run root>`, `--deadline-s 172800`, `--driver-pidfile so1c_driver.pid`, then `bash so1c_chain_driver.sh MESH Ns-P Ni-P Ns-S Ni-S`; `cwd` = this directory; `ranks 4`; `cost_core_min_estimate 40.2`; `cap_core_min_registered 125.0`; `memory_floor_gb 8.0`; `cost_basis` derived / not measured; `permission bc0e687e`; `prereg_commit` = the full 40-hex sha of the commit introducing THIS file, **re-derived with `git log --format=%H --diff-filter=A -- <path>` and never from a commit subject line** (`VERIFICATION_CHARTER.md` v1.12 — two commits in this family shared one subject 52 s apart, and the wrong one resolves to a real commit and fails only at the path check).

**ENQUEUEING IS NOT AUTHORISATION**: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own, discharged on the sha, and is not discharged by this document or by the queue entry.

**Predicted outcome, so it cannot be written afterwards:** P-A, P-MESHID, P-1, P-2, P-4 through P-7, P-TB, P-I, P-mesh and P-CLOCK **HIT** (P-3 `NOT_MEASURED` pending AV-1R) → **both rows `GATE FAIL` on their `scotch` arms, both `simple` arms `PASS`, item `GATE FAIL`** — and the lab gains its first measurement of what a decomposition **method** does to a gradient **at an optimum**, with an FD table beside it.

---

## AMENDMENT R6 — 2026-08-28, TWO READER DEFECTS CLOSED PRE-COMPUTE. **The document is v1.1.** No gate, threshold, band, cap, label, cost or prediction moves.

Lane: dafoam `lab-lane` (V). Supervisor: `dafoam-supervisor`. **This amendment is a repair to two INSTRUMENTS; it repairs nothing in the text above, which is not edited.**

### R6.0 `lines whose number changed above this section: 0`

Not a claim — a byte comparison, made in the same shell invocation that appended this section. The **288 lines / 43971 bytes** above the horizontal rule that opens this section are **byte-identical** to `PREREGISTRATION.md` at the v1.0 freeze commit `bd7f68d67f3de225eac6425650f2fd4cda1dd579`, and byte-identical to the same path at `d87e4a7ffaa96f43ee91e53493f286348ea3b84c`. Nothing above was struck, rewritten or renumbered. The header still reads **Version 1.0. FROZEN.** deliberately: that line is a true statement about the frozen document, and rewriting it is exactly the edit rule 6 forbids. The version bump is carried here.

The cap-manifest comment on **line 6 is untouched**, so `G-CAP-PREREG` channel (a) reads the same caps from disk and channel (b) reads the same line from `git show HEAD:` — both channels of that guard read exactly as they did at the freeze, and this section deliberately does not reproduce that comment's token so nothing here can be mistaken for a second manifest.

### R6.1 The rule-2 condition, in `VERIFICATION_CHARTER.md` §2b's own terms

**Before first compute, amendments are legal and must state the condition and how it was checked, naming the run directory that does not exist.** Re-verified by this lane, in one shell invocation, at **2026-08-28T16:44:46Z**:

* `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv` — **DOES NOT EXIST** (`test -e` false). This is the registered run root, named in `so1c_chain_driver.sh:29` and in §8 above.
* `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-gradient` — **DOES NOT EXIST.**
* `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c` — **DOES NOT EXIST.**
* `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012` — **DOES NOT EXIST.**
* `find /home/ubuntu/certonomous-runs -maxdepth 1 -iname '*so1c*'` returns **nothing**, and the same command **shown working on a known positive** returns SO-1a's root — a zero from a finder never shown able to find is not evidence (rule 3's logic applied to the check itself).
* `verification/queue/LAUNCH_LOG.tsv` carries **0 rows matching `so1c`** against **1 matching `so1a`** — the same grep proving it can see one.

> **ONE CHECK IS RETIRED AND WAS NOT USED.** `sudo -n docker ps -a --filter name=so1c` returning empty **is not evidence**: the identical filter returns empty for `so1a`, which demonstrably ran five containers, because Docker history is pruned after inspect. A zero from that reader is blind to exactly the class being asked about.

**0 core-min of solver compute has been spent on SO-1c, and no container of any kind has been created by this lane.** The amendment's own cost is local `python3`/`bash` on the head node: two grader suites and one guard suite, **0 solver core-minutes, 0 GPU-hours**, against a pre-registered item estimate of 40.2 core-min that is **unchanged and still unspent**.

### R6.2 DEFECT 1 — the C5 banner false positive. **CONFIRMED at every link.**

The frozen v1.0 comparator, by line:

| site | frozen text |
|---|---|
| `so1c_grade.py:155–157` | `FATAL_TOKENS = (…, "Floating point exception")` — a **bare substring** |
| `so1c_grade.py:449` | `return [t for t in FATAL_TOKENS if t in text]` — whole-file substring test |
| `so1c_grade.py:137` | `ARTEFACT["MESH"] = "checkMesh.log"` |
| `so1c_grade.py:516` | `hay = text + (open(art).read() if kind == "SCRIPT" else "")` |
| `so1c_grade.py:517–520` | the refusal, whose `"log"` field names the **arm** log |

**Measured, not inferred.** Line 18 of `/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/MESH/checkMesh.log` reads

> `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`

count **1** in that file; count **0** in the MESH arm log the refusal cites; count **0** in all four of SO-1a's solver arm logs. SO-1a's grade artefact `SO1a_grade_20260828T023132Z.json` records `verdict: NOT A RESULT` with `C5_fatal_token_in_arm_output: ["Floating point exception"], arm: MESH, log: MESH_20260828T021739Z_1709267.log` — **a refusal citing a file in which the token appears zero times**, on a run whose five arms were all `rc = 0`. **Zero gates were evaluated.**

**The base rate is not marginal.** Closure measured the banner on **63 of 70** archived logs, **57** of them cleanly completed. The supervisor independently stopped a live run over the same defect at 16:33:52Z today: `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/S0_20260828T162848Z_1898005.log` is 339 lines with **4 banner hits, 0 real fatal tokens and 5 `End` lines**. A scanner that refuses on this line refuses on almost every log the lab holds.

### R6.3 DEFECT 2 — the G-MESHID selection defect. **CONFIRMED, and one framing corrected.**

| site | frozen text |
|---|---|
| `so1c_grade.py:907–908` | `for cand in sorted(glob.glob(root/"MESH_*.log")): mine_src = cand` — **LAST-WINS** |
| `so1c_grade.py:934` | the `GATE FAIL` reason **pre-written** as `MESH_REGENERATION_IS_NOT_DETERMINISTIC …` |
| `so1c_chain_driver.sh:206` | `grep -ah … "$SO1B_BASE"/MESH_*.log … | head -4` |
| `so1c_chain_driver.sh:97` | `so1b_grade_file() { ls -1t … | head -1; }` — an **mtime** pick |

**CORRECTION OF FACT I OWE UPWARD, and it makes the defect more interesting rather than less.** The two sides are not two selections from *one* candidate set. The grader globs **SO-1c's own** run root (the **subject**); the driver globs **SO-1b's** run root (the **reference**). They are the two *sides of one equality test*, each independently reducing its own multi-member set. And `head -4` is not reliably "first": `grep` on this box is **ugrep 7.8.4**, where multi-file output order is a **race** — so the frozen reference is not merely mis-ordered, it is **non-deterministic**.

**The `:934` defect is not hypothetical; it was driven and measured.** Against the **frozen v1.0 comparator**, a reference file carrying two sha256 lines — exactly what `head -4` produces from a two-log root — returned **`GATE FAIL`, `MESH_REGENERATION_IS_NOT_DETERMINISTIC`, item `GATE FAIL`.** A reader defect published as a fluent, quotable physics finding about mesh non-determinism. And two `MESH_*.log` in the subject root returned **item `PASS`** — an ambiguity silently resolved in favour of a pass.

### R6.4 THE REPAIRS, AND WHY THESE SHAPES

**C5 — the token is NOT deleted.** Deleting `"Floating point exception"` would blind C5 to a real SIGFPE crash, and a missed crash laundered into a result is strictly worse than a false refusal. The scan is **line-by-line and per source file** (`so1c_grade.py:510` `benign_reason`, `:519` `fatal_token_sites`, `:616` the C5 site), with a narrow, named **exclusion list** at `:214` `BENIGN_LINE_PATTERNS` — one entry, `^\s*trapFpe:\s`, because `trapFpe:` is the diagnostic prefix of OpenFOAM's FPE-trapping **setup** code and a crash never prefixes itself with it. **Every exclusion is counted and named on the PASS record**; a suppression a reader cannot see is the same defect wearing the other hat.

> **TWO LAB IMPLEMENTATIONS WERE READ BEFORE THIS ONE WAS WRITTEN.** `sdk/chief_engineer/mesh_certificate.py:73` **deletes** the FPE and segfault tokens and leans on a required `^End` marker, calibrated on 105 real checkMesh logs — **right for its scope, rejected for this one**, because it certifies checkMesh only, where a crash cannot be an MPI abort, while C5 here also scans four np = 4 solver logs. `sdk/chief_engineer/head_engineer.py:188` matches `Foam::sigFpe::sigHandler|^Floating point exception`. **Its handler symbol is ADOPTED** as a tenth `FATAL_TOKENS` entry — a strictly *additional* refusal on a genuine crash signature, which strengthens detection. **Its line anchor is NOT adopted, and the reason is this item's own regime:** at np = 4 the realistic FPE report is OpenMPI's — `mpirun noticed that process rank 2 exited on signal 8 (Floating point exception).` — which is neither line-initial nor accompanied by the handler symbol, and `^Floating point exception` would miss it. An exclusion list costs a false refusal where it is too narrow; a positive anchor costs a **missed crash** where it is too narrow.

**The refusal now names its own evidence.** `token_sites` carries the **file and line** of every hit and `files_scanned` lists what was read; the note states in the artefact that `log` is the arm's log and is *not necessarily* the file carrying the hit.

**G-MESHID — uniqueness refusal on both sides, not a better sort.** Grader `so1c_grade.py:1037` enumerates candidates and **refuses on more than one**; it also refuses when either side resolves to more than one distinct sha256. Driver `so1c_chain_driver.sh:97–125` (`G-SO1B-SELECT`) and `:226–256` (`G-MESHREF-SELECT`) apply the **same rule** so the two sides cannot disagree about what "the" mesh or "the" grade is; each reads **one named file** and each **records the selection** — the chosen file, the candidate count and the full candidate list, printed and written beside the reference as `optref/so1b_mesh_points_sha256.SELECTION.txt`. The R5 `ls -1t | head -1` pick gets the identical treatment: **zero** grade artefacts is the pre-existing `BLOCKED` branch, byte-preserved with `reason=no_grade`; **more than one** is a new refusal with `reason=grade_selection_ambiguous` naming every candidate.

**`:934` — a refusal now reads as a refusal.** Every reader-condition outcome is `NOT A RESULT` carrying `cause_class: READER_CONDITION_NOT_A_MESH_FINDING`, and **does not contain the mesh-regeneration-determinism sentence at all — not even to explain itself**, because a downstream reader greps the reason string. That sentence is emitted only where the comparison actually ran on one unambiguous sha per side, and then carries `cause_class: MESH_FINDING`. *(The unit enforcing this caught my own first draft, which quoted the forbidden sentence inside the new reason text.)*

### R6.5 BOTH DIRECTIONS, DRIVEN THROUGH THE REAL CODE PATH, WITH THE PLANT ON DISK

The fixture is built by the comparator's **own** `_fix()` — the builder all registered units use — the plant is written **into the artefact on disk**, and `grade()` reads it back off disk. The benign-banner plant is **byte-copied from line 18 of SO-1a's real `checkMesh.log`**, and unit U54 cross-asserts that copy against the file. `__pycache__` was cleared before every run.

| planted input | **BEFORE** (v1.0, frozen) | **AFTER** (R6) |
|---|---|---|
| benign `trapFpe:` banner alone | **REFUSED**, 0 gates evaluated | item **PASS** |
| real `FOAM FATAL ERROR` block in the artefact | REFUSED | **REFUSED** |
| real SIGFPE crash **beside** the banner, same file | REFUSED | **REFUSED**, 2 tokens named |
| clean control, no plant | item PASS | item **PASS** |
| **two** `MESH_*.log` in the run root | item **PASS** (silent pick) | **NOT A RESULT**, reader condition |
| reference carrying **two** sha256s | **GATE FAIL**, physics sentence | **NOT A RESULT**, reader condition |
| one each, **mismatched** | GATE FAIL, physics sentence | **GATE FAIL**, physics sentence |
| one each, **matching** | item PASS | item **PASS** |

**The contrast is the evidence.** Rows 1, 5 and 6 are the defect firing on the frozen instrument; rows 2, 3, 7 and 8 are the proof the repair did not blunt anything.

**Suites — before and after, both interpreters, `__pycache__` cleared before each run:**

| suite | v1.0 | R6 | verdict |
|---|---|---|---|
| `so1c_grade.py --selftest`, `python3` | 53 units, 0 fail | **65 units, 0 fail** | rc 0 |
| `so1c_grade.py --selftest`, `python3 -O` | 53 units, 0 fail | **65 units, 0 fail** | rc 0 |
| `so1c_groot5_selftest.sh` | 35 legs, 0 fail | **49 legs, 0 fail** | rc 0 |

**`EXPECTED_UNITS` 53 → 65 is a DELIBERATE bump**, carried at `so1c_grade.py:210` with the reason in the constant's own comment. The twelve units are **U54** benign banner passes (plant cross-asserted against SO-1a's file), **U55** the exclusion is counted, named and attributed to `checkMesh.log`, **U56** a real FOAM FATAL in the artefact still refuses, **U57** a real SIGFPE *beside* the banner still refuses (the exclusion is per line, not per file), **U58** the refusal names file and line and the named file is `checkMesh.log`, **U59** every registered token still refuses when planted alone (the line split loses nothing), **U60** two candidates → reader `NOT A RESULT`, **U61** a two-sha reference → reader `NOT A RESULT`, **U62** a genuine mismatch still `GATE FAIL` with the physics sentence, **U63** a genuine match still `PASS` with its selection on the record, **U64** a **real, unconstructed** 339-line OpenFOAM log driven whole through the comparator, **U65** the adopted handler symbol is independently load-bearing. The guard suite gains **h0–h8**: both driver blocks are **extracted verbatim from the frozen driver between their own markers and executed** — never re-implemented — and h8 asserts the defect shape is gone from executable lines **with its sweep pattern proven on a planted known positive first**.

**FOUR R6 MUTATION CONTROLS, AND THE ONE THAT MEASURED INERT IS REPORTED, NOT HIDDEN:**

| mutation | effect |
|---|---|
| `BENIGN_LINE_PATTERNS = ()` | **the suite ABORTS at U54** with an uncaught `Refusal` naming `checkMesh.log:1` and the banner, rc 1 — the mutation **reproduces the original defect** |
| the `> 1` candidate refusal removed | flips **U60** |
| the multi-sha reference refusal removed | flips **U61** |
| `"Foam::sigFpe::sigHandler"` removed from `FATAL_TOKENS` | **MEASURED INERT ON FIRST DRIVE.** U59 is defined *in terms of* the tuple, so emptying the tuple also empties U59's loop. **U65 was then written with the token hard-coded and the mutation re-driven: it now flips U65.** A mutant that changes no verdict is not evidence |

### R6.6 EVERY md5 RE-DERIVED, AND EVERY SITE UPDATED

Re-derived in the invocation that wrote this section. **§7's table above is frozen prose and is NOT edited in place; it is superseded here, and this is the table a reader must use.**

| file | md5 at the v1.0 freeze | **md5 now** | |
|---|---|---|---|
| `so1c_grade.py` | `32af1c494db6884144151c7e7d7e81af` | **`367f9fc25b3b34535cb2cddfafdc06b1`** | **CHANGED** |
| `so1c_chain_driver.sh` | `55614d4aa953fee29ceccbc7c1785baf` | **`fce4a92f2a1cb07c98c4c8327e0e5dd0`** | **CHANGED** |
| `so1c_run_arm.sh` | `777c33117dd65d882a9be04d27c07526` | `777c33117dd65d882a9be04d27c07526` | unchanged |
| `so1c_xn.py` | `63d13c88fb915ab7695d6f1a9383a4ed` | `63d13c88fb915ab7695d6f1a9383a4ed` | unchanged |
| `so1c_runScript.py` | `0557da51f6f179f6de865144343c499f` | `0557da51f6f179f6de865144343c499f` | unchanged |
| `so1c_decomposeParDict_scotch` | `816f5ba44075fde47fa5db4269877bc8` | `816f5ba44075fde47fa5db4269877bc8` | unchanged |
| `so1c_decomposeParDict_simple` | `194c330803077f0ffa4341f468c09768` | `194c330803077f0ffa4341f468c09768` | unchanged |
| `so1c_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | `709ab0b98ef0302a3a3a318588f9493f` | unchanged |
| `so1c_groot5_selftest.sh` *(not a pinned file)* | `225a608db2f2196737ccf8599d3f7423` | `1a4d25987cd2a1a2e17a6ec7ce455eeb` | changed |

**PIN SITES SWEPT AND UPDATED — how the sweep was run:** `grep -rn` for each of the four instrument md5 literals across the case directory, `docs/LAB_STATE.md`, `docs/dafoam/` and `verification/queue/`, each pattern first shown finding a known positive. Four sites carry the grader hash and two carry the driver hash:

* **`so1c_chain_driver.sh:38` `367f9fc25b3b34535cb2cddfafdc06b1R` — THE ONLY EXECUTABLE PIN. RE-PINNED.** The driver asserts it before staging and again at the grade; a stale pin aborts the chain at run time, which is how W3 lost a launch this morning. Verified in the same invocation: the pin **equals** the grader's md5 on disk.
* **§7's table and §8's sentence above** — frozen prose, **not edited**, **superseded by the table here.**
* **`QUEUE_ENTRY_DRAFT.json`** — a draft, **not enqueued**, updated in place: new hashes, the supersession stated rather than the old values quietly overwritten, and the unit/leg counts corrected to 65 and 49.
* **Both selftest evidence files** — the v1.0 captures are **left intact** and a dated R6 capture is **appended beside** them.

**The launcher's `0557da51f6f179f6de865144343c499fCRIPT` / `63d13c88fb915ab7695d6f1a9383a4ed` / `MD5_DECOMP_*` and the driver's tutorial-input hashes are untouched**, because none of those files moved.

### R6.7 WHAT MOVED, WHAT DID NOT, AND ONE §7 LINE-NUMBER CORRECTION

**NO GATE, THRESHOLD, BAND, CAP, LABEL, COST, PREDICTION OR ARM MOVES.** `S_G_BAND`, `S_J_BAND`, band D, band E, the plateau tolerance, `MIN_GRADED`, `CAPS`, `ITEM_CEILING_CORE_MIN`, `PREDICTED_CORE_MIN`, `CELLS_EXPECTED`, `REGISTERED_NPROCS`, the cpuset, the deadlines, `cost_core_min_estimate 40.2`, `cap_core_min_registered 125.0` and every registered prediction P-A … P-CLOCK are **byte-unchanged**. This amendment adds **refusals on ambiguous or misread inputs** and **removes a refusal on a benign one**; on any well-formed input it changes no comparison and no verdict — which is exactly what the eight-row before/after table above measures.

**§7's guard-placement line numbers for `so1c_chain_driver.sh` have SHIFTED and are corrected here** — the driver gained two blocks above them. §7 above is not edited; these are the numbers to use:

| guard | §7 (v1.0) | **now** |
|---|---|---|
| `G-SO1B` refuses | :100 | **:109** |
| `G-SO1B` passes | :162 | **:183** |
| the run root is created | :180 | **:200** |
| the optref is staged | :207 | **:247** |
| the first launcher call | :288 | **:338** |
| **new** `G-SO1B-SELECT` | — | **:97–125** |
| **new** `G-MESHREF-SELECT` | — | **:226–256** |

**Every guard still precedes every destructive step and every spending step**, re-measured and strictly increasing: 97 < 109 < 125 < 183 < 200 < 226 < 247 < 338. **`so1c_run_arm.sh` is byte-unchanged and §7's launcher numbers are INTACT** — re-confirmed by the suite's own legs (b2) `G-ROOT.5 pass :304 < rm -rf :482 < docker run :614` and (d2) `G-CAP-PREREG :369 < G-OPTDEP :469 < rm -rf :482`.

> **A CORRECTION AGAINST MYSELF, RECORDED BECAUSE IT IS THE LESSON.** My first probe of the launcher's placement used a looser pattern than the suite's and reported `G-ROOT.5` at `:282` against §7's `:304` — a discrepancy that did not exist. The suite anchors on `D4S_G_ROOT5_PASS`; I anchored on `G-ROOT.5`, which matches an earlier line. **A sweep that disagrees with ground truth is measuring its own pattern until proven otherwise**, and I very nearly reported a defect in a file I had not touched.

### R6.8 WHAT THIS AMENDMENT DOES NOT DO

It **does not enqueue SO-1c** — that is the supervisor's call, and `SUPERVISION_CHARTER.md` §3 check 4 is discharged by the supervisor on the sha, not by this document. It lands **nothing** on SO-1a or on W3, whose gates are **CLOSED** — SO-1a's defect is recorded here as evidence and is **not repaired in its frozen instrument**. It files, sends, uploads, registers, posts and comments **nothing** (rule 7; SUBMISSIONS PARKED). It repairs no other item's copy of this defect: `so1a_grade.py:122–125` still carries the bare token, and that is a **finding for the supervisor**, not a change this lane may make post-compute.
---

## AMENDMENT R7 — 2026-08-31, PRE-COMPUTE. **THE PRECONDITION POINTED AT A RUN ROOT THAT DOES NOT EXIST AND NEVER WILL.** The document is **v1.2**. No gate, threshold, band, cap, label, cost or prediction moves.

### R7.0 RULE 6 — NOTHING ABOVE THIS LINE MOVED, PROVED BY BYTE COMPARISON

**Lines whose number changed above this section: 0.** The **445 lines / 63,764 bytes** above the
horizontal rule that opens this section are **byte-identical** to `PREREGISTRATION.md` at HEAD
immediately before this amendment — compared against the **HEAD blob** with `git show`, never
against `git diff`, which reads the shared index and is unreliable under concurrency. Nothing
above was struck, rewritten or renumbered. **The header still reads `Version 1.0. FROZEN.`
deliberately** — that line is a true statement about the frozen document, and rewriting it is
exactly the edit rule 6 forbids. The version bump is carried here, as R6 carried its own.

### R7.1 THE RULE-2 CONDITION, AND HOW IT WAS CHECKED — WITH A CONTROL, NOT AN ASSERTION

`CLAUDE.md` rule 2 makes amendments legal **before first compute** and requires the condition be
stated **and how it was checked** — naming the run directory that does not exist.

| check | result |
|---|---|
| `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv` | **No such file or directory** |
| `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt` | **No such file or directory** |
| **CONTROL — the same lister, on a root that DOES exist** | returns `CURRICULUM-SO1bR-a1-naca0012-dragmin-opt` |

**The control is not decoration.** A "does not exist" from a reader not shown able to see an
existing directory is not evidence (`CLAUDE.md` rule 3). **SO-1c has burned ZERO core-minutes,
started no container and created no run root.** Gates are open; this amendment is the ordinary
path and **`VERIFICATION_CHARTER.md` §2d.1 is NOT reached for and is not needed.**

### R7.2 WHAT WAS BROKEN — FOUR THINGS, NOT ONE, AND THE FOURTH IS THE DANGEROUS ONE

SO-1b aborted at `rc=7` **before staging** and was re-registered as **SO-1bR**, which completed:
`chain=COMPLETE`, five arms `rc=0`, verdict `PASS`, 17.934 core-min. **Its run root has a
different name, and four things in this item pinned the old one.**

| # | break | where | class |
|---|---|---|---|
| **1** | the precondition **root** | `so1c_chain_driver.sh:30` (`SO1B_BASE=`) — one line, and every downstream use at `:106`, `:216`, `:217`, `:236`, `:247` goes through `$SO1B_BASE` | run-time abort |
| **2** | the **grade-json glob** `SO1b_grade_*.json` vs SO1bR's `SO1bR_grade_*.json` | `so1c_chain_driver.sh:106`, messages `:109`, `:116` | run-time BLOCK |
| **3** | **the suite's own fixtures** | `so1c_groot5_selftest.sh` — the `G-SO1B-SELECT` fixtures | **A GREEN THAT TESTS NOTHING** |
| **4** | the **(a2) negative fixture** | `so1c_groot5_selftest.sh:55` | control **degradation** |

**BREAK 3 IS WHY THIS AMENDMENT TOUCHES THE SUITE AT ALL, AND IT IS NOT A COSMETIC GAP.** Leg
`(h0)` asserts the suite **extracts the `G-SO1B-SELECT` block from the frozen driver** rather than
running its own copy — which is the right design and is exactly what makes Break 3 bite. Repairing
Break 2 alone leaves the fixtures matching nothing, and **`(h3)` — the R5 uniqueness repair, the
whole reason `G-SO1B-SELECT` exists — still returns `rc=7`, but on the `no_grade` branch instead
of the ambiguity branch. Right code, wrong reason.** A control that cannot fail is not a control.

**Break 4:** `(a2)` used SO-1b's root to prove the launcher refuses *"the root this item READS"*.
That root no longer exists, so the leg had degraded to proving refusal of a **nonexistent**
directory — strictly weaker than registered.

### R7.3 A FIFTH ITEM, CAUSED BY THE REPAIR ITSELF, AND IT IS THE `W3` DEATH MODE

Adding SO-1bR's root to `FORBIDDEN_ROOTS` **changed `so1c_run_arm.sh`, and the driver PINS that
file** (`MD5_LAUNCHER`, asserted at `:53` before staging and again at `:293` before every arm).

**MEASURED, by driving the driver's own assertion:** pinned `777c33117dd65d882a9be04d27c07526`
against actual `12dd18eced7b67f04348cd29363d31e1` → `md5sum -c` **FAILED, rc=1**. The chain would
have aborted **`exit 4`, `ABORT launcher md5 drifted before staging`, before any container** —
precisely the failure that cost `W3` a launch on 2026-08-28.

**AND THE 50-LEG SUITE PASSED ANYWAY.** Nothing in this item drove the driver's md5 pins against
the files they pin. `MD5_LAUNCHER` is **RE-PINNED** to `12dd18eced7b67f04348cd29363d31e1` and a
new leg `(a5c)` now drives **all four** pins.

**`(a5c)` IS PROVED ABLE TO FAIL, ON THE REAL FILE, BEFORE ITS PASS IS BELIEVED** (§2j): a
one-byte mutation of `so1c_run_arm.sh` drove it to **`[BAD]`, naming the mismatch**
(`pinned=12dd18ec… actual=a9636fe1…`); the file was restored byte-identically and the leg returned
`[OK]`. **A control that has only ever passed is not shown to be a control.**

### R7.4 THE EVIDENCE, IN THREE STATES — THE KNOWN POSITIVE CAME FIRST

**Editing a test fixture is the one move in this repair that could be used to make a failing test
pass, so the burden is on the repair to show it did not.**

| state | suite | legs | fail |
|---|---|---|---|
| **A — BASELINE**, before any change | as frozen | **49** | **0** |
| **B — KNOWN POSITIVE**, driver glob repaired, fixtures NOT yet | Break 2 only | **49** | **3** — `(h2)`, `(h2b)`, `(h3b)`; **and `(h3)` GREEN ON THE WRONG BRANCH** |
| **C — AFTER**, all repairs | this amendment | **51** | **0** |

**State B is the whole argument.** The fix was **shown failing before it was shown fixed**. In
state C, `(h3b)` asserts the literal string **`reason=grade_selection_ambiguous`** — not merely
`rc=7` — so the ambiguity branch is proved reachable and proved taken.

**Legs whose status changed, in either direction:** `(h2)`, `(h2b)`, `(h3b)` B→C `[BAD]`→`[OK]`;
`(h3)` B→C `[OK]`→`[OK]` **but on a different branch, which is the point**; `(a2)` now fires on a
root that exists. **Legs added: `(a5b)`, `(a5c)`. Legs removed: none. Legs weakened: none.**

### R7.5 WHAT MOVED, AND WHAT EXPLICITLY DID NOT

**MOVED — five call sites and two documents:**

1. `so1c_chain_driver.sh:30` — `SO1B_BASE` → SO-1bR's run root.
2. `so1c_chain_driver.sh:106/:109/:116` — the glob and its two operator-facing messages → `SO1bR_grade_*.json`.
3. `so1c_chain_driver.sh:37` — `MD5_LAUNCHER` re-pinned (§R7.3).
4. `so1c_run_arm.sh` — SO-1bR's root **ADDED** to `FORBIDDEN_ROOTS`.
5. `so1c_groot5_selftest.sh` — fixtures → `SO1bR_grade_*`; the `(a2)` fixture → SO-1bR's root; legs `(a5b)`, `(a5c)` added.
6. `PREREGISTRATION.md` — this section only.
7. `QUEUE_ENTRY_DRAFT.json` — precondition path, plus the **md5 pin** of §R7.6.

**DID NOT MOVE — and this is the part a future auditor should check first, because *"we edited
the test"* is exactly the sentence that should attract suspicion:**

* **NO GATE, THRESHOLD, BAND, CAP, LABEL, COST OR PREDICTION.** `np = 4`, the cpuset, the memory
  floor, `G-NP`, `G-XSTAR`, `G-MESHID`, `G-COLD`, `G-SO1B`'s decision logic, every band and every
  registered outcome are untouched.
* **THE CONTROL ITSELF IS UNTOUCHED. ONLY THE FIXTURES MOVED.** `G-SO1B-SELECT`'s logic —
  enumerate, refuse on zero, refuse on more than one, record the selection — is byte-unchanged.
  **The fixtures changed so that an EXISTING control can fire against the artefact names that now
  exist.** No assertion was weakened, none was deleted, and no `[BAD]` was turned green by
  lowering a bar.
* **`so1c_grade.py` IS NOT TOUCHED.** md5 `367f9fc25b3b34535cb2cddfafdc06b1`, unchanged from R6.
  **It is THE GRADING PATH, fixed at the pre-registration commit, and it is not churned by this
  amendment.**
* **`FORBIDDEN_ROOTS` was ADDED TO, NEVER SUBSTITUTED.** SO-1b's dead root **stays**, because leg
  `(a4)` asserts that literal string is present in the launcher and a substitution would fail it —
  and because forbidding a root that no longer exists costs nothing. **Both entries are asserted
  present afterwards**, by `(a4)` and the new `(a5b)`. The addition is purely protective:
  SO-1bR's root is now a root this item **READS**, and it must never be written into.
* **The E/O artefact filenames DID NOT MOVE.** SO-1bR still writes `so1b_E.json` and
  `so1b_O.json`; **only the root and the grade prefix changed**, and nothing was renamed to
  "match" the R convention.

### R7.6 THE md5 PIN — the repair for the class, not just the instance

`QUEUE_ENTRY_DRAFT.json` now carries **`precondition_artifact_md5`
= `9b1a965c5108245679df87801653aae6`** (`E-S/so1b_E.json`, 9,991 bytes), **independently verified
by two readers** on 2026-08-31.

**PINNING BY PATH ALONE IS WHAT LET A PATH CHANGE BECOME A SILENT SEMANTIC BREAK.** A path pin
answers *"is something there?"*; a content pin answers *"is it the thing I registered?"* With the
hash, a substituted, truncated or regenerated artefact **REFUSES** instead of resolving to the
wrong file.

### R7.7 THREE DISCLOSURES, NONE OF WHICH THIS AMENDMENT REPAIRS

1. **`so1c_grade.py:124` carries a DEAD CONSTANT** — `SO1B_BASE = "…CURRICULUM-SO1b-…"`, **defined
   once and referenced zero times** (measured). It names a root that no longer exists. **It is
   left in place deliberately**, on the supervisor's ruling: the grading path's md5 is not churned
   to delete a constant with no references. **It is recorded here so the next reader is not misled
   by it.**
2. **`PREREGISTRATION.md:416` carries a typographic defect in R6's prose** — the grader md5 is
   written `367f9fc25b3b34535cb2cddfafdc06b1R`, with a stray trailing `R`. **The executable pin at
   `so1c_chain_driver.sh:38` is correct** and was verified against the file. Prose only; nothing
   executes it; **not corrected, because R6 is frozen and this is disclosure, not repair.**
3. **The suite did not drive the driver's md5 pins before this amendment** (§R7.3). That gap is
   now closed by `(a5c)`, and it is named rather than quietly filled.

### R7.8 THE PATTERN, RECORDED WHERE IT IS LOAD-BEARING AND NOWHERE ELSE

**SO-1b broke because it globbed `SO1a_grade_*.json` when SO-1aR wrote `SO1aR_grade_*.json`.
SO-1c broke because it globs `SO1b_grade_*.json` when SO-1bR writes `SO1bR_grade_*.json`.** The
`R`-suffix re-registration convention **systematically breaks every downstream consumer that pins
by name, and the repair of each rung is precisely what breaks the next.**

**Break 3 is that shape a THIRD time and is the strongest instance, because it is
self-referential: the fix to the driver broke the suite that guards the driver.**

**No `L-` number is taken here and no naming rule is proposed** — the 2026-08-31 plumbing freeze
forbids new procedural rules, and the first two instances are already recorded at `L-412`. This
paragraph sits in this amendment because it is **the reason `§R7.6`'s content pin exists**, which
is load-bearing, and for no other reason.

### R7.9 INSTRUMENTS — the three whose md5 moved, and the reason each moved

| instrument | md5 BEFORE | md5 AFTER | why |
|---|---|---|---|
| `so1c_chain_driver.sh` | `55614d4aa953fee29ceccbc7c1785baf` | **`3870a8d4c58861fce5a7e9437f89474a`** | Breaks 1 + 2, and the `MD5_LAUNCHER` re-pin |
| `so1c_run_arm.sh` | `777c33117dd65d882a9be04d27c07526` | **`12dd18eced7b67f04348cd29363d31e1`** | one line ADDED to `FORBIDDEN_ROOTS` |
| `so1c_groot5_selftest.sh` | *(not previously tabled)* | **`ca79882b8933a8502da96063ad2119da`** | Breaks 3 + 4, legs `(a5b)`/`(a5c)` |
| `so1c_grade.py` | `367f9fc25b3b34535cb2cddfafdc06b1` | **unchanged** | the grading path is not churned |
| `so1c_xn.py` | `63d13c88fb915ab7695d6f1a9383a4ed` | **unchanged** | |

**All four of the driver's pins were verified to equal the files they pin, in the same invocation
that produced this table**, and leg `(a5c)` now re-verifies them on every drive.

### R7.10 WHAT THIS AMENDMENT DOES NOT DO

**It does not launch, enqueue, or authorise anything.** No queue entry is filed; the
`QUEUE_ENTRY_DRAFT.json` is a draft and remains one. **Enqueueing is not authorisation** and the
pre-compute gate is the supervisor's. **SO-1c has spent 0 core-minutes and this amendment spends
none.** It moves no gate, threshold, band, cap, label, cost or prediction; it retires nothing; and
it makes **more** things refuse and **nothing** pass that could previously have been refused.
