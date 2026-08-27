# CURRICULUM SO-1b — NACA0012 INCOMPRESSIBLE DRAG-MIN AT FIXED LIFT: the OPTIMISATION RUNG of the shape-optimisation ladder SO-1, WITH THE MANDATORY FINAL-DESIGN-POINT FD CHECK AND THE D7R ATTRIBUTION AS A GATE, ON TWO TOOLCHAIN ROWS — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (D). Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

<!-- SO1B-CAP-MANIFEST v1 MESH=5.0 O-P=25.0 E-P=30.0 O-S=25.0 E-S=30.0 CEILING=115.0 MAX_ITER=30 RANKS=1 -->

**The order this item answers, verbatim from Sanaa's standing directives of 2026-08-27T16:54Z** (`git show HEAD:etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`, §4):

> ### dafoam — SHAPE-OPTIMIZATION LADDER (pull in order when queue drains)
> Pattern per case: FD-verified gradient rung -> optimization rung ->
> post-optimum verification (re-solve at optimum, constraints checked,
> np-invariance spot row) -> D7R attribution rule: no improvement % quoted
> before its mechanism is decomposed (shape vs AoA vs operating point).
> After you are done with all the current optimization cases:
> - SO-1 NACA0012 subsonic drag-min at fixed lift; then RAE2822 transonic.

**This item is rung 2 of 4 for SO-1 and nothing more.** SO-1a (`curriculum_SO1a/PREREGISTRATION.md`, frozen `7bd91ef98861daa90a69350c3671e50c921a4ca7`) is rung 1. SO-1c (post-optimum verification proper — the np-invariance spot row Sanaa's pattern names, and a second design point) is NOT frozen here.

> **THE ORDERING RULING, `[lab-attributed]`, ON THE RECORD SO IT CAN BE OVERRULED.** The supervisor's brief from the chief said "SO-2 next". The supervisor ruled that **SO-1b precedes SO-2**, and this lane records the reason: SO-2 is the *constraint-families* rung **on SO-1**, and stacking constraint rungs on an optimum that does not exist would register gates against an artefact nobody has bought. Sanaa's §4 fixes the pattern **per case** — gradient, then optimisation, then post-optimum verification — and this item is the second step of that pattern on the first case. **If Sanaa disagrees, this ordering is the thing to overrule; nothing else in the document depends on it.**

> **ID-NAMESPACE CHECK.** `SO-1b` was confirmed free at 2026-08-27T19:11Z: `ls cases/dafoam/ladder-a/A1/` carried no `curriculum_SO1b`, no `verification/queue/dafoam/**` entry names it, and the run root below did not exist. The item files under `ladder-a/A1/` because it IS A1's NACA0012 mesh, beside `curriculum_D1`, `_D13`, `_D15`, `_D16`, `_AV1`, `_AV2` and `_SO1a`.

Every decision here is `[lab-attributed]`. Permission for the detached launch: Sanaa's own words boarded at **`bc0e687e`**; queue-first order `7def3c6b` / `73eccb1b` / `0b041d1a`; L-342 field classes `d4d0c29d`; R-RC approved in the directives file above (§0).

---

## 0. SCOPE — AND WHAT IS **NOT** NEW HERE, SAID FIRST

**Capability-grid cell (`docs/capability/dafoam_GRID.md`): `2D · steady · incompressible`, column "optimization converged".**

**SO-1b IS NOT THE FIRST OPTIMISATION OF THIS PROBLEM, AND THIS DOCUMENT SAYS SO ON ITS FIRST SCREEN.** The lane looked before it registered:

* **D1** (`cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md`) optimised this exact problem on the **PATCHED** row: `EXIT: Optimal Solution Found.` after **11 major iterations**, `CD` from **`0.020943920630946831`** (the post-feasibility reference) to **`0.017527899854535338`**, a reduction of **`16.310321 %`**; endpoint FD on four components at worst **0.2553 %** with zero sign flips; all 23 geometric constraint rows in bound; **6.017 core-min**, 361 wall s, 11 majors of a `max_iter 40` cap.
* **D13** (`curriculum_D13/RESULTS.md`, `docs/COST_CALIBRATION.md` **C-71**) re-bought it **five times** from seeded perturbed starts, PATCHED only: five `PASS`, 9–11 majors each, `CD` spanning `0.017527829297657737`…`0.017528032918957957` — **a spread of 2.0e-7** — and the cross-start basin verdict **`GATE FAIL`**: **15 of 15 pairs `DIFFERENT` on the design vector, 0 of 15 `DIFFERENT` on drag.**

**That last measurement is load-bearing for this registration and is inherited, not re-derived: on this problem the DESIGN VECTOR is not unique and the DRAG is.** SO-1b therefore gates on the drag, the constraints and the gradient at the optimum, and **never on the design vector** — a gate on the design vector would fail on a physically identical optimum, as D13 measured 15 times.

**THREE THINGS ARE NEW, AND THEY ARE THE REASON THIS RUNG EXISTS.**

1. **THE SHIPPED ROW'S OPTIMUM HAS NEVER BEEN BOUGHT.** D1's shipped arm `armC` (`d1_endpoint_shipped`) was **`BLOCKED`** — `KeyError: 'CD_final'` in D1's own frozen G5 comparator, **before any solve**, 0.233 core-min, **named waste in D1's own ledger** (`curriculum_D1/RESULTS.md` row 4). D13 ran **PATCHED only**. So `DAFOAM_CHARTER.md` §1/§6/§10's two-row rule is **UNDISCHARGED for the A1 optimum**, and the missing row is precisely the one whose LE shape gradient SO-1a predicts `GATE FAIL` (SO-1a P5, the `idx6` class, measured at 11.43 % on this very case in `reverify_patched_idwarp_np1/RESULTS.md`). **What does a defective LE gradient do to an optimum?** No record in this lab answers that.
2. **THE FINAL-DESIGN-POINT FD CHECK ON SO-1a'S FIVE REGISTERED COMPONENTS, ON BOTH ROWS.** `DAFOAM_CHARTER.md` §9 makes it mandatory — *"Every optimisation reports a finite-difference check of the gradient at its final design point, not only at the baseline"* — and gives the reason as a measurement: IDWarp's defect has **two regimes on opposite sides of its `axisMag` guard** (`ROOTCAUSE_getRotationMatrix3d.md` §1.6, §6.4: `1e-5 rad → 4.1e-08`, `1e-6 → 6.7e-05`, `5e-8 → 1.2e-02`), branch 0 is **certain** at the undeformed baseline, and *"a gradient verified at iteration 0 is not verified at iteration 47"*. D1 graded four components (`shape[6]`, `shape[1]`, `shape[5]`, `patchV[1]`); only two are in SO-1a's registered set. **SO-1b measures SO-1a's five, so BASELINE and OPTIMUM become the SAME measurement at two design points.**
3. **THE D7R ATTRIBUTION IS A GATE WITH A REQUIRED ARTEFACT, NOT A CAVEAT.** D1 asserted the mechanism in prose — *"a cambered section … flying at 1.13° instead of 5.15° … the same `CL = 0.5` bought by section shape rather than by angle of attack"* (`curriculum_D1/RESULTS.md`:209-211). **That is a reading of the design vector, not a decomposition.** D1 never solved at `(shape = 0, aoa = 1.13°)` or at `(shape*, aoa = 5.15°)`. SO-1b buys those points (§3d) and **suppresses every improvement percentage mechanically** unless the artefact is complete.

**WHAT IS DELIBERATELY RE-BOUGHT, AND WHY IT IS NOT A DUPLICATE.** The PATCHED optimisation (`O-P`, 6.0 core-min) repeats D1's arm O. It is bought because **an optimum produced by a different frozen instrument at a different commit three days earlier is not a control for a shipped arm run beside it** — the two-row comparison in §3 is only a comparison if both rows come from the same chain, the same mesh and the same freeze. **And the repeat is itself a measurement:** P-D predicts D1's `CD` **to the digits** (§6), so a MISS is a reproducibility finding worth more than the 6.0 core-min it costs.

**The mesh is A1's, 4,032 cells**, regenerated by this item's own `MESH` arm (0.167 core-min MEASURED) rather than read across a run root, so the item is self-contained and P-A re-proves mesh identity. **np = 1 on every arm** (`DAFOAM_CHARTER.md` §5). The FFD box is 5×2×2 → **8 `shape` functions + `patchV` [|U| FIXED, aoa free]**; the objective is `CD`; the constraints are `CL == 0.5` (equality), `thickcon ∈ [0.5, 3.0]` (20 rows), `volcon ≥ 1.0` (1), `rcon ≥ 0.8` (2) — **23 geometric rows plus the lift equality**.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt` DOES NOT EXIST.**

`test -e` → **false** at **2026-08-27T19:11:25Z** (this lane, immediately after the case directory was created and before any instrument was written), and again as a leg of `so1b_groot5_selftest.sh` (*"run root ABSENT before the test"* / *"run root ABSENT after the test (freeze condition)"*, `so1b_groot5_selftest_evidence.txt`).

**This item has burned 0 core-min of solver compute and started no arm container.** The only container this lane started was the G-ROOT.5 selftest's sacrificial `sleep`, pinned `--cpus=0.1 --cpuset-cpus=9 --memory=64m` and removed with `docker rm -f` in the same script. **After the first arm container, gates are CLOSED**; changes land only as dated addenda that cannot alter a gate, threshold, cap or label (`VERIFICATION_CHARTER.md` §2b).

## 1a. THE DEPENDENCY ON SO-1a, ITS PRECONDITION ARTEFACT, AND THE TWO NO-LAUNCH BRANCHES

**SO-1b optimises using the gradients SO-1a finite-difference verifies.** The dependency is registered here and is enforced in two places, both **before any compute**.

**(i) The queue entry is a WAIT-WRAPPER.** `cases/dafoam/_common/dafoam_wait_then_launch.sh` (the D6/D8R form), precondition:

> **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/F-P/so1a_F.json`**

**AND NOT A `CHAIN_DONE` MARKER, BECAUSE SO-1a HAS NONE — this is a correction to the brief and it is stated rather than worked around.** D5 (`Addendum 3`, `b5b428bc`) and D6 (`Addendum 3`, `0aa9a82a`) each needed a dated addendum to add a fixed-name `CHAIN_DONE` trap before D6 and D8R could wait on them; `so1a_chain_driver.sh` carries no such trap — its only fixed-name files (`STATUS.chain`, `ledger.txt`, `so1a_driver.pid`) are opened at chain **start**, and its grade artefact is timestamped (`SO1a_grade_<stamp>.json`), so none of them is a `test -e` precondition for a chain **end**. **Amending SO-1a is legal (it has spent 0 core-min) and was deliberately NOT done:** `SO1a_chain.json` is live in the daemon runner's drop path, the runner may fire it at any moment, and an amendment race would leave a launched driver whose `prereg_commit` no longer names the file that ran. **`F-P/so1a_F.json` is a better precondition anyway**: `F-P` is the LAST arm of SO-1a's registered chain, so the artefact appears only if the chain reached and completed the arm that verifies **the patched constraint gradient SO-1b actually consumes**. SO-1b's own driver **does** write a fixed-name `CHAIN_DONE` on every exit of a started chain (§5), so SO-1c will not inherit this problem.
**Bound: `86,400 s` (24 h), registered.** Derivation: launch latency behind D6's live `O_mp` arm at the runner's 85 % ceiling (D6 started 14:09:24Z with a 2,000 core-min cap at 4 ranks ≈ 8.3 h wall, so ≤ 8 h from this freeze) **+** SO-1a's own ceiling wall (75.0 core-min at 1 rank = 75 min) **+** SO-1a's five H5 windows and its aggregate wait-and-retry (any one of which hitting its 4 h bound **blocks SO-1a's chain**, so at most one 4 h wait precedes an outcome) **≈ 13.3 h**, comfortably inside 24 h. The wrapper polls every 30 s, writes every wait to `STATUS.SO1b_chain_wait` and `WRAPPER.SO1b_chain_wait.log`, applies G-ROOT.5 immediately before exec, and **launches nothing at the bound**.
**A partial-write race is registered and handled:** `test -e` can fire on a `so1a_F.json` mid-write. The wrapper's job is only to stop waiting; **G-SO1A below re-reads SO-1a's own grade artefact**, which SO-1a's driver writes *after* the chain ends, and refuses on anything it cannot parse.

**(ii) `G-SO1A`, in `so1b_chain_driver.sh:140-147`, before the run root is created (`:160`) and before the first launcher call (`:250`).** It reads the newest `SO1a_grade_*.json` under SO-1a's run root on **two channels** — `gates.G5_PATCHED.{G5_CD,G5c_CL}.verdict` and the composed `rows.PATCHED` — and **a disagreement between the channels refuses**.

**WHAT IS CHECKED IS NOT SO-1a'S ITEM VERDICT, AND THAT DISTINCTION IS THE POINT.** SO-1a's own registered predicted outcome is item **`GATE FAIL`** — its SHIPPED row is predicted to fail band D at `shape[6]`, and **that failure is SO-1a's finding, not a defect**. Gating SO-1b on SO-1a's item verdict would kill SO-1b in exactly the case SO-1a expects. What a constrained optimiser consumes is narrower: **the PATCHED row's objective gradient `G5` and its constraint gradient `G5c` must BOTH read `PASS`.** SO-1a §6 P6 states the same condition from the other side: *"a MISS means SO-1b cannot be registered as a constrained optimisation on this gradient and the ladder stops at SO-1a."*

**THE TWO REGISTERED NO-LAUNCH BRANCHES, both at ZERO core-minutes, named in advance:**

| branch | trigger | mechanism | rc | SO-1b item verdict | cost |
|---|---|---|---|---|---|
| **N1** | SO-1a never reaches `F-P` (any earlier arm stops, or SO-1a itself is `BLOCKED`) | the wrapper's precondition never appears; it closes at the 86,400 s bound and launches nothing | **6** | **`BLOCKED`** | **0 core-min** |
| **N2** | `F-P/so1a_F.json` exists but SO-1a's PATCHED row is not `PASS` on **both** `G5` and `G5c` — or its grade is absent, unreadable, or the two channels disagree | `G-SO1A` in the driver, before the run root is created | **7** | **`BLOCKED`** | **0 core-min** |

**An unreadable dependency is not a licence to proceed.** Both branches are the safe direction and both are registered before compute.

## 2. ARMS — five, in this order, one detached chain, TWO ROWS, np = 1 THROUGHOUT

| arm | kind (G1) | image (row) | ranks | task | work dir | artefact | terminal marker |
|---|---|---|---|---|---|---|---|
| **MESH** | SCRIPT | SHIPPED | 1 | the tutorial's own `preProcessing.sh` + `checkMesh` | `MESH/` (cold copy of `base/`) | `MESH/checkMesh.log` | `Mesh OK.` |
| **O-P** | SOLVER | **PATCHED** | 1 | `so1b_of.py -mode O -row P`: cold primal → `findFeasibleDesign` (CL trim by aoa) → `prob.run_driver()` (IPOPT, `max_iter 30`) | `O-P/` (cold copy of `MESH/`) | `O-P/so1b_O.json` **+ `O-P/opt_IPOPT.txt`** | `SO1B_O_WRITTEN` |
| **E-P** | SOLVER | **PATCHED** | 1 | `so1b_of.py -mode E -row P`: re-solve at `x*`, the five attribution primals + `C'`, `compute_totals` at `x*`, the FD table + trivial baseline at `x*`, the CTRL control | `E-P/` (cold copy of `MESH/`) | `E-P/so1b_E.json` **+ `E-P/attribution.json`** | `SO1B_E_WRITTEN` |
| **O-S** | SOLVER | SHIPPED | 1 | as O-P, row S | `O-S/` | `O-S/so1b_O.json` + `opt_IPOPT.txt` | `SO1B_O_WRITTEN` |
| **E-S** | SOLVER | SHIPPED | 1 | as E-P, row S | `E-S/` | `E-S/so1b_E.json` + `attribution.json` | `SO1B_E_WRITTEN` |

Chain: `so1b_chain_driver.sh MESH O-P E-P O-S E-S`, stops at the first non-zero rc, then runs the frozen grader on whatever exists (its rc is INFRASTRUCTURE, never the verdict). **The PATCHED row runs FIRST by registration** — it is the control for the shipped row beside it, and if it will not stand there is no comparison to make. **The two-row rule (`DAFOAM_CHARTER.md` §1, §6, §10):** both rows are bought on ONE mesh generated once in the SHIPPED image. *(`DAFOAM_CHARTER.md`'s two-row / digest-identity clause is **§6**, "Shipped and patched are always two rows, and toolchain identity is an image ID and a library hash, never a version string". SO-1a's launcher comment and `SO1a_chain.json` both cite it as "§11"; **§11 is the lessons-numbering clause.** The mis-citation is inherited into no SO-1b text — this document cites §6 — and it is reported to the supervisor rather than repaired in a frozen file.)*

**`E` READS ITS OWN ROW'S OPTIMUM AND NO OTHER, ON TWO INDEPENDENT CHECKS.** `E-P` reads `../O-P/so1b_O.json`, `E-S` reads `../O-S/so1b_O.json`. **`G-EDEP`** (`so1b_run_arm.sh:275-287`) refuses an E arm whose own row's artefact is absent, and **`G-ROWX`** (in the instrument, and again in the grader) refuses an optimum whose in-process `libidwarp.so` md5 differs from the reading process's — **a row is an image hash, never a directory name.**

Arm commands, verbatim from the launcher's `case`, each written to `<arm>/so1b_cmd.sh` and executed **inside the container under `timeout -k 60 <cap wall>`**:
`mpirun --allow-run-as-root -np 1 --bind-to core --report-bindings -x PYTHONPATH python so1b_of.py -mode O|E -row P|S`.

**THE REGISTERED FD DESIGN AT THE OPTIMUM** — identical to SO-1a's at the baseline, which is what makes the two comparable. Components **`shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`** plus the planted-zero control **`CTRL`**; steps **`shape`: {1e-2, 1e-3, 1e-4}**, **`patchV[1]`: {1e-1, 1e-2, 1e-3}** degrees; central differences, both signs; reference = the middle step; plateau = agreement with at least one neighbour to 10 %. Step-set justification is **by citation and not re-derived**: `cases/dafoam/ladder-a/A_stepsize_study.md` measured the curve **flat at 2.5–3.0 % from 1e-4 to 3e-2 on THIS case** with the primal FAILING at 5e-2 and 1e-1, at the tolerance the graded run uses (`primalMinResTol 1.0e-8`).

**THE PLANTED-ZERO CONTROL (rule 3), in the instrument AND in the grader.** `CTRL` carries a synthetic row with derivative **exactly 0.0** and a PLANTED row with `CD_plus = CD_baseline + 1.234e-03` (derivative **exactly 0.617**); the instrument writes both, **re-reads them from disk**, and exits 2 if the read-back cannot see them. The grader re-checks both and additionally writes a copy of each endpoint table with `PLANT` added to every physical derivative, re-reads it through the same reader, and refuses unless every value moved by exactly `PLANT`. **A zero from a reader not shown able to see a non-zero is not evidence.**

## 3. GATES, THRESHOLDS AND LABELS — `so1b_grade.py`

All bands are frozen now. Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

### 3a. Completion, inherited whole from SO-1a

* **G1 — the five rule-4 clauses, PRINTED INDIVIDUALLY PER ARM**: `C1` rc VALUE (physics, from `docker inspect .State.ExitCode`), `C2` terminal marker, `C3` artefact present, `C4` age guard, `C5` no fatal token (`FOAM FATAL ERROR`, `FOAM FATAL IO ERROR`, `Segmentation fault`, `SIGSEGV`, `SIGKILL`, `MPI_ABORT`, `signal 9`, `Signal 11`, `Floating point exception` — **REFUSES REGARDLESS OF rc**). Any clause failing on any arm → **`NOT A RESULT`**, comparator exit 2.
* **R-RC, as Sanaa approved it (directives §0):** the rc VALUE is physics, the rc RECORD is infrastructure. An absent rc RECORD reads **`NOT MEASURED`** and only when `C2`–`C5` all hold; the implied `rc = 0` is written as an explicit **INFERENCE** with its basis named and **never graded as a measurement**. An absent record beside a NON-ZERO harness rc **REFUSES**: *R-RC relaxes a missing record, never a positive reading of failure.*
* **THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME** — the AV-1/AV-2 lesson (`0b3ebaa4`, `3e2cbf74`: both `NOT A RESULT` on 2026-08-27 with every arm `rc = 0` and every physics artefact intact, because a frozen grader pinned `DATUM_REF = "0/U"` while `writeCompression on` rewrites it as `0/U.gz` on a serial arm; AV-1's own numbers: datum `1787838035`, `0/U.gz` mtime `1787838086`, **51 s newer — only the reference PATH had vanished**). Both names are candidates, the one FOUND is recorded, `writeCompression` is read from the arm's own `system/controlDict`, and **refusal only when NEITHER name exists**. DRIVEN: grader `U42`/`U43`, launcher legs `f1`–`f5`.
* **L-342 field classes (`d4d0c29d`), as amended by R-RC.** Absent infrastructure → `NOT_MEASURED` named beside the verdict, never composed to PASS. Present-but-garbage → REFUSE. Absent physics → REFUSE.
* **G-M2 — mesh identity:** `cells == 4,032` → `PASS`, else `GATE FAIL`.

### 3b. G-OPT — `DAFOAM_CHARTER.md` §9, applied literally, and the ONLY route to PASS

§9, verbatim: *"An optimisation run is graded PASS only if the optimiser itself printed a convergence statement against its own tolerance. A run stopped by a wall clock, an iteration cap or a budget is `GATE REACHED` where a registered intermediate threshold was met and `NOT A RESULT` otherwise — never `PASS`, and never described by the size of the improvement it reached."*

* **`PASS`** iff `opt_IPOPT.txt` carries **`EXIT: Optimal Solution Found.`** *and* the major count is **strictly below** the registered bound.
* **`GATE REACHED`** iff no convergence statement (or the bound was reached) **and the REGISTERED INTERMEDIATE THRESHOLD held**, fixed here before any run: **`|CL − 0.5| ≤ 1.0e-3`** (100× the optimiser's own `constr_viol_tol`) **and** `CD_opt < CD_trimmed`. **`GATE REACHED` is never described by the size of its improvement.**
* **`NOT A RESULT`** otherwise, and **whenever `opt_IPOPT.txt` is absent** — the word *converged* is never used of a run whose optimiser printed no statement.
* **TWO INDEPENDENT CHANNELS, and a disagreement REFUSES.** The instrument records IPOPT's `EXIT:` line and iteration count; the grader re-reads `opt_IPOPT.txt` from disk **without going through the instrument**. Disagreement on either the EXIT line or the major count → comparator exit 2.
* **`G-ITER`:** the artefact's `max_iter_registered` must equal **30**, and its `optimizer` must equal **IPOPT**, or the comparator REFUSES. **An optimiser with a core-minute cap and no iteration bound spends the cap and produces nothing gradeable**, so the bound is registered and asserted on both sides.

### 3c. G-CL and G-GEO — the POST-OPTIMUM CONSTRAINT CHECK

* **`G-CL`:** at the **re-solve at the optimum** (an independent primal at `primalMinResTol 1.0e-8`, not the optimiser's internal value), **`|CL − 0.5| ≤ 1.0e-4`** → `PASS`; otherwise the row is **`NOT A RESULT` WHATEVER THE DRAG DID.** **A drag reduction bought by quietly shedding lift is not a result.** The tolerance is 10× the optimiser's own `constr_viol_tol = 1e-5` and ~6 orders above the measured primal repeatability (`eta` 1.30e-10 on this mesh, D15) — neither noise-limited nor slack. D1 measured `|CL − 0.5|` at `≤ 1e-5` and D13 at `4.2e-07`…`8.3e-06`, so 1e-4 is a band this problem has cleared six times.
* **`G-GEO`:** all **23** geometric rows within their producer-declared bounds at the re-solve, slack `1e-6` (D1's own slack): `thickcon ∈ [0.5, 3.0]` ×20, `volcon ≥ 1.0` ×1, `rcon ≥ 0.8` ×2. Any row out → **`GATE FAIL`**; a family absent or carrying the wrong row count → **`NOT A RESULT`**.

### 3d. G-D7R — THE ATTRIBUTION GATE, WITH A REQUIRED ARTEFACT

Sanaa's §4: *"no improvement % quoted before its mechanism is decomposed (shape vs AoA vs operating point)."* **Operationalised as a GATE:** unless `attribution.json` exists and is complete, the grader emits **`SUPPRESSED_BY_G_D7R`** in place of **every** improvement percentage and the row is **`NOT A RESULT`**. The percentage is never a gate *input* either — §9 forbids grading an optimisation by the size of its improvement.

**WHERE THE IMPROVEMENT IS MEASURED FROM, registered.** The reference is **`A` — the CL-TRIMMED baseline** `(shape = 0, aoa = aoa_T)`, converged at the same `primalMinResTol 1.0e-8` as the optimum. **Not the cold baseline.** D1 measured why: the trim *raises* drag (`CD_cold 0.020910510006792161 → CD_feasible 0.020943920630946831`, **+3.34e-5**), so a percentage measured from the cold point credits the optimiser with undoing a drag rise the trim itself caused — 16.176603 % against 16.310321 % for the same optimum. Both are reported; **`A` is the registered reference**, and the trim channel is named separately and **never netted into the improvement**.

**THE FIVE REGISTERED POINTS, plus `C'`** — all solved, none inferred:

| point | design | what it isolates |
|---|---|---|
| **A0** | `shape = 0, aoa = aoa0 = 5.13918623195176°` | the tutorial's declared cold baseline (CL ≠ 0.5) |
| **A** | `shape = 0, aoa = aoa_T` | **THE REGISTERED REFERENCE**, CL = 0.5 |
| **B** | `shape = 0, aoa = aoa*` | **AoA alone** |
| **C** | `shape = shape*, aoa = aoa_T` | **shape alone** |
| **D** | `shape = shape*, aoa = aoa*` | **the optimum** (this IS the re-solve G-CL and G-GEO read) |
| **C'** | `shape = shape*`, **re-trimmed** to CL = 0.5 | the shape channel **at matched lift**, and a feasibility check on `D` |

**EVERY POINT RECORDS ITS `CL` BESIDE ITS `CD`, AND THE GATE REQUIRES BOTH.** On a lift-constrained problem a channel's `ΔCD` is meaningless without its `ΔCL`.

**THE OPERATING-POINT CHANNEL IS ASSERTED IDENTICALLY ZERO, NEVER ASSUMED.** `patchV[0]` is `|U|`, bounded `lower == upper == U0` by the producer, so the operating point cannot move in this item — **and that is CHECKED against the optimum's own `patchV*[0]`, not inferred from the bound.** If it moved, the item's own assumption is falsified, every percentage is suppressed and the row is `NOT A RESULT`.

**THE REGISTERED READING OF THE DECOMPOSITION, WRITTEN BEFORE IT RUNS.** D1's optimum flies at **1.13°** against a baseline **5.15°**, with all eight shape modes positive. So `B` (`shape = 0` at 1.13°) will carry **far less drag and almost no lift** (CL ≈ 0.1), and `C` (the cambered section at 5.15°) **more lift and more drag**. **The naive one-factor decomposition is therefore predicted to be strongly NON-ADDITIVE, with `|ΔCD_aoa| > |ΔCD_total|` and a large interaction term** (P-H). That is not a defect of the method — **it is the finding**: at fixed `CL`, **angle of attack is a DEPENDENT variable determined by the shape**, so the matched-lift decomposition has exactly **one flow channel (shape) plus the trim**, and the naive AoA channel is an artefact of ignoring the constraint. Both decompositions are reported; the naive one is reported **to show why it is not an attribution**. `C'` is bought as the falsifier: `|CD_{C'} − CD_D| ≤ 1.0e-4` or the optimum was not feasible.

### 3e. G5E — the FINAL-DESIGN-POINT FD gate, per row, on CD **and** CL

Bands **by citation, not re-derived**: **band D = per-component `|d_FD − J_adj| / |d_FD| ≤ 5.0 %` with the same sign**, **band E = aggregate vector-relative error ≤ 5.0 %** — `curriculum_D4/PREREGISTRATION.md:82` and `curriculum_D7FR/PREREGISTRATION.md:228-229`. **A sign flip is `GATE FAIL` whatever its magnitude.** Plateau 10 %; `|d_mid| < 1e-14` → `NEAR_ZERO` → `NOT A RESULT`; **fewer than 3 graded components → the row is `NOT A RESULT`.**

* **`G-TB`** — the `DAFOAM_CHARTER.md` §4 trivial baseline **at the optimum**: the same probe at `h = 1.0e-8` (`shape`) / `1.0e-6` (`patchV`). **`PASS` iff AT MOST 1 of 5 passes band D at the wrong step; 2 or more and that row's G5E verdict is WITHDRAWN to `NOT A RESULT`.** A probe that ERRORED counts as FAILING.
* **`G6` — dot-product / duality: NOT MEASURED**, and said rather than omitted (`DAFOAM_CHARTER.md` §2). The reason is a measurement, not a preference: **AV-2 measured today** that seeding forward mode makes the primal FAIL on this exact case on BOTH images (`curriculum_AV2/RESULTS.md` §2, 5/5 rows `AnalysisError(… Primal solution failed!)`, `control_fail false`).
* **`G9`** toolchain per row by digest **and** `libidwarp.so` md5; **`G10`** every row `core_min ≤ cap`, sum ≤ **115.0**; **`G11`** OOM hard (`OOMKilled true` is a G1 refusal, never a re-fire); **`G12`** `cpuset == 9` on every arm, with the delivered-cores floor **not applied at np = 1** and reported as a number. **DIVERGENCE** shipped-vs-patched on the adjoint **at the optimum** is reported with its number, never gated.

### 3f. Composition, registered here

**Row:** `NOT A RESULT` if any of {G5E composition, G-CL, G-D7R, G-OPT, G-GEO} is `NOT A RESULT`; else `GATE FAIL` if any is `GATE FAIL`; else `GATE REACHED` if any is `GATE REACHED`; else `PASS`.
**Item:** `NOT A RESULT` if either row is; else `GATE FAIL` if either row is, or if any of G-M2 / G9 / G10 / G12 is; else `GATE REACHED` if either row is; else `PASS`.
**No grid family exists, so standing rule 5 has no row and NO GCI IS QUOTED.** `NOT_MEASURED` fields are printed beside the verdict, never inside it.

**§2a identity test, answered for the two gates that carry this item.**
*G-D7R: what would make it FAIL?* A missing or non-finite point, or an operating point that moved. *Could a wrong treatment still PASS it?* Yes, and it is named: a decomposition whose five primals were all solved at a **looser** tolerance than the optimum would reconcile arithmetically while comparing different things. The instrument solves every point through the same `prob.run_model()` at the producer's own `primalMinResTol 1.0e-8` and records each point's own `CL`, so a tolerance substitution would show as a `CL` that misses its constructed value.
*G-OPT: what would make it FAIL?* No `EXIT: Optimal Solution Found.` in `opt_IPOPT.txt`. *Could a wrong treatment still pass it?* One we can name: an optimiser that converges to a **feasible but non-optimal** point and says so. That is why G-OPT is not the row verdict on its own — G5E at the final design point and G-CL at the re-solve are bought beside it, and `C'` checks the optimum against a re-trim.

## 3g. NON-CONVERGENCE IS PRE-REGISTERED, NOT IMPROVISED

`docs/standards/NONCONVERGENCE_STANDARD.md` (commit `7ffd6c73`) L0–L7 applies to any optimiser or primal in this item that will not converge, and its **ANTI-GAMING clause is ABSOLUTE**: L1–L5 convergence aids tune freely and disclosed; **answer-changing choices (model, scheme class, formulation) are NEVER selected by agreement with the reference**; converged-but-wrong is `NOT HELD` **with a diagnosis, never a parameter hunt**; **frozen gates are never edited post-compute**. Its two standing conditions bind at every level: **one change per run**, and **every step is a pre-registered diagnostic arm with a cap**.

**OPTIMISER SETTINGS ENTER THE ANSWER-CHANGING CLASS THE MOMENT THEY ARE CHOSEN BY LOOKING AT THE ANSWER, so they are registered here and appear in exactly two places** — `so1b_of.py:OPT_SETTINGS` and `so1b_grade.py:{OPTIMIZER_REGISTERED, MAX_ITER_REGISTERED, ...}`, cross-asserted by `G-ITER`:

| setting | value | source |
|---|---|---|
| optimizer | **IPOPT** | the tutorial's own default |
| `tol` | **1.0e-5** | the tutorial's own |
| `constr_viol_tol` | **1.0e-5** | the tutorial's own |
| **`max_iter`** | **30** | **LOWERED from the tutorial's 100 by this registration** (§4: 30 majors fit inside the 25.0 core-min cap at C-71's own worst measured per-major rate) |
| `mu_strategy`, `limited_memory_max_history`, `nlp_scaling_method`, `alpha_for_y`, `recalc_y` | **the tutorial's own, unchanged** | — |

**If either row will not converge, the registered response is the L0 diagnosis and a `GATE REACHED` or `NOT A RESULT` label — NOT a settings hunt.** No L1–L7 arm is registered in this item; one would be a **new registration** with its own freeze and its own cap.

## 4. COST — DERIVED FROM **MEASURED** ANCHORS ON THIS EXACT PROBLEM

Every anchor is a MEASURED core-minute figure from a named `docs/COST_CALIBRATION.md` row, **never a sibling estimate**.

| anchor | C-row | what it measures | value |
|---|---|---|---|
| MESH on this 4,032-cell pyHyp mesh at 1 rank | **C-154 (D15), C-156 (D16), C-158 (AV-1)** — three independent items agree exactly | the same arm this item's MESH runs | **0.167 core-min MEASURED** |
| **A1 NACA0012 lift-constrained drag-min, np = 1, IPOPT, PATCHED — LITERALLY THE ARM `O-P` RUNS** | **C-71 (D13)** | five cold-started optimisations: **6.383 / 5.217 / 5.617 / 5.150 / 5.683**, mean **5.610**, at **9–11 majors** | **5.150–6.383 core-min MEASURED** |
| the same arm, one more time | **D1 arm O**, `curriculum_D1/RESULTS.md`:54 | 11 majors, 361 wall s, np = 1 | **6.017 core-min MEASURED** |
| setup + 1 primal + 2 adjoints + colouring, incompressible A1, np = 1, `compute_totals(of=[CD,CL],wrt=["shape","patchV"])` | **C-158 (AV-1 `X1-S`)** | the adjoint half of the `E` arm, like for like | **1.017 core-min MEASURED** |
| ≥ 31 compressible primals + setup at np = 2 (`F-S − X-S`) | **C-154 (D15)** | the FD-table half of the `E` arm | **2.066 core-min MEASURED** |

**The O-arm price.** C-71's six measured optimisations of this exact problem span **5.150–6.383** core-min. Point **6.0** — above the mean (5.610), just below the worst (6.383), and beside D1's independent 6.017. Cap **25.0** = 3.9× the worst measured start.
**The registered iteration bound FITS INSIDE THE CAP, and this is arithmetic, not hope.** C-71's worst start is 6.383 core-min over 9 majors = **0.709 core-min/major**, and that figure is an **upper bound on the marginal rate** because it includes the arm's fixed setup and its `findFeasibleDesign` trim. **30 majors × 0.709 = 21.3 core-min < 25.0.** *A deadline that cuts before the registered iteration bound is the `D5-PREREG-DEF-1` / `D4S-LAUNCHER-DEF-2` defect class; it is named here and excluded by the numbers.*

**The E-arm price, stated so it can be attacked.** Primals: 2 baseline (η) + 5 components × 3 steps × 2 signs (30) + the trivial baseline 5 × 2 (10) + the five attribution points + `C'`'s trim ≈ **46–50**. SO-1a §4's derivation from C-154 gives **≈ 1.5 wall s per warm incompressible primal at np = 1** (D15's `F-S − X-S = 2.066` core-min = 62 wall s at np = 2 for ≥ 31 compressible primals → ≤ 2.0 wall s/primal at np = 2; ×0.5 incompressible; ×1.5 for np = 1 wall, AV-1's measured 61 vs 41 wall s). **50 × 1.5 = 75 wall s**, plus the adjoint, colouring and setup bounded above by **AV-1's WHOLE `X1-S` arm, 1.017 core-min = 61 wall s** → **136 wall s = 2.27 core-min**. Point **4.0**, carrying ×1.76 margin for the 50 IDWarp warps at a deformed design.

| arm | derivation | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| MESH | C-154/C-156/C-158, all three read 0.167 | **0.167** | 5.0 | 300 s (1 rank) | 4g |
| O-P, O-S | **C-71**, five measured runs of this arm; D1's 6.017 beside them | **6.0** each | 25.0 each | 1500 s (1 rank) | 4g |
| E-P, E-S | derived above from **C-158** and **C-154** | **4.0** each | 30.0 each | 1800 s (1 rank) | 4g |
| grader | zero compute | 0 | — | — | — |
| **total** | | **20.2** point, band **[11.0, 58.0]** | **CEILING 115.0 = Σ caps** | ≈ 21 min wall at the point, ≈ 115 min at the caps (+ five 60-s H5 windows) | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED, not measured**: point **$0.016758**, band top **$0.049590**, ceiling **$0.098325**.
**Cap mode:** each arm's wall deadline is **inside the container** (`timeout -k 60` at cap × 60 / ranks s); the launcher asserts the enforced wall equals the registered cap to 0.02 core-min **and** asserts its own cap table against the CAP-MANIFEST line of this frozen document (`G-CAP-PREREG`, §7), aborting before any container on disagreement. The host poller reports a crossing and hard-stops at 4× cap while it lives. **An overrun stops the run; it does not get a new budget** (rule 12). A calibration row in `docs/COST_CALIBRATION.md` is owed at completion (rule 12, Sanaa's estimate-versus-actual directive), and it will state **actual/predicted per arm against C-71 and C-158**, with contention named separately and never folded into the misprediction ratio (`COMPUTE_BUDGET_CHARTER.md` §6).

**REGISTERED COST EXPOSURES, disclosed rather than absorbed.**
1. **cpuset `9` overlaps D4-SHIPPED's registered `5,6,7,9`.** At np = 1 that cannot fail G12 (the delivered-cores floor does not apply) but it CAN inflate wall time and therefore core-minutes. The band `[11.0, 58.0]` is set wide enough to absorb it; P-I grades the band, not the point.
2. **The SHIPPED optimisation may take MORE majors than the patched one**, because IPOPT is being handed a gradient SO-1a predicts wrong at `shape[6]` — line-search failures and restoration phases cost majors. `O-S` may reach `max_iter 30` or its 1500 s deadline. **That outcome is registered, not a surprise: `GATE REACHED` if the intermediate threshold holds, `NOT A RESULT` otherwise, and either is the finding.**

## 5. PLACEMENT, MEMORY AND THE DETACHED FORM

* **cpuset `9`** (`--cpuset-cpus=9`, `--cpus=1`), ONE core because every arm is np = 1. **Disclosed overlap with D4-SHIPPED's `5,6,7,9`**; the same core SO-1a registers, which by construction cannot collide because SO-1b runs only after SO-1a's last arm has produced its artefact. Not core 0. At freeze the only live container on this box was `d6_O_mp_20260827T140924Z_805560` on D6's registered `2,3,4,14` — disjoint.
* **Memory:** `--memory=4g --memory-swap=4g` every arm (D13 measured peak RSS 1.70 GiB on this mesh at np = 1); **H5 windowed gate 45 samples / 60 s, refuse on ANY sample < 8.0 GiB**; **aggregate** (live caps + 4 + host non-container RSS) **< 30.6 GiB** in the **wait-and-retry** form (poll 30 s, bound 4 h, every wait a line in `STATUS.<arm>`, refuse-and-BLOCK at the bound with the series named).
* **The detached form.** The queue runner launches the wait-wrapper under its own `setsid nohup`; the wrapper captures the driver's exit INSIDE itself; the driver writes its pid to `<run root>/so1b_driver.pid`, opens `STATUS.<arm>` at preflight and appends the final `rc=<n> … source=launcher_exit=docker_inspect_ExitCode` line **inside the detached session** — never the `$?` of a `setsid`/`timeout` line. Container `rc` is read from `docker inspect` **before** `docker rm`; **no `--rm`**; `<ARM>_<stamp>.inspect.txt` survives as the kernel record. `STATUS.chain` carries the chain state and, at the end, `grader_rc=<n> … note=comparator-exit-status-NOT-the-verdict`.
* **`CHAIN_DONE`, which SO-1a does not have.** `so1b_chain_driver.sh:193` writes one line to `<run root>/CHAIN_DONE` on **every exit of a started chain**, success or stop (a pre-chain abort writes none) — the D5-Addendum-3 / D6-Addendum-3 form. **SO-1c can wait on this chain without amending anything.**
* **G-ROOT.1–.5, G-ROW, G-EDEP and G-CAP-PREREG from birth, DRIVEN.** `BASE` must equal this item's root through `realpath -m`; the forbidden list names **SO-1a's root** and D4's, D4-SHIPPED's, D4-SHIPPED-R's, D5's, D6's, D14's, D14M's, D7R's, D7FR's, D12R's, D12R2's, D12R2W2R's, D13's, D15's, D16's, D17's, AV-1's, AV-2's, A2-mach-wing's, the tutorial checkout, `certonomous-runs` and the repository; the ledger refuses a foreign `ITEM=`; an `rc=0` row refuses a re-fire (`ALREADY_BOUGHT`); G-ROOT.5 refuses a RUNNING container carrying `so1b_<ARM>_` or a driver pidfile naming a live pid that is not an ancestor or whose cwd is the run root.
* **Run root staging** (first fire only): creates the root (mode 777, L-251), copies the INCOMPRESSIBLE tutorial's `0.orig FFD constant system profiles genAirFoilMesh.py preProcessing.sh` into `base/`, overlays the registered `so1b_decomposeParDict` (`numberOfSubdomains 1`, scotch), copies the two instruments, writes `ITEM=SO1b` alone on ledger line 1, and md5-asserts every staged file **including the six tutorial inputs** before any container starts. A second fire stages nothing.

## 6. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

| # | prediction | value / band | falsifier |
|---|---|---|---|
| **P-A** | the MESH arm reproduces A1's mesh | **cells == 4,032** | any other count → G-M2 `GATE FAIL`; a different mesh is a different item |
| **P-B** | the CL-trimmed baseline reproduces D1's `CD_feasible` | **`CD_T ∈ [0.02090, 0.02100]`** (D1's own registered band; D1 measured `0.020943920630946831`), `\|CL_T − 0.5\| ≤ 1e-4` | outside → the trim is not D1's trim and the reference is not comparable |
| **P-C** | the PATCHED optimiser converges on its own statement inside the bound | **`EXIT: Optimal Solution Found.`, majors ∈ [6, 20]** (D1 11; D13 9,9,10,10,11) | a MISS with majors ≥ 30 is a `GATE REACHED`/`NOT A RESULT` under §9 and is reported as such |
| **P-D** | **THE REPRODUCIBILITY TEST.** the PATCHED optimum reproduces D1's, three days and one instrument later | **`CD* ∈ [0.0175273, 0.0175285]`** (D1 `0.017527899854535338`; D13's five spanned `0.017527829…0.017528033`) **and improvement ∈ [16.0 %, 16.7 %]** (D1 measured `16.310321 %`) | **a MISS is a reproducibility finding on this lab's own optimum and is worth more than the 6.0 core-min it costs** |
| **P-E** | **THE POINT OF THE RUNG.** the SHIPPED row's endpoint FD disagreement at `shape[6]` **DIFFERS from its BASELINE value** (SO-1a's reading on the same component, same steps) | reported as a NUMBER (`rel_err_pct`) and a verdict; compared against SO-1a's in the record | **a MISS — the two readings agreeing — means the IDWarp defect is DESIGN-INDEPENDENT, contradicting `ROOTCAUSE_getRotationMatrix3d.md` §1.6/§6.4 and `DAFOAM_CHARTER.md` §9's own argument. THAT would be the finding.** |
| **P-F** | the SHIPPED optimum is **not better** than the PATCHED one | `CD*_shipped ≥ CD*_patched` | a MISS means a defective LE gradient costs nothing on this problem — a finding, not a defect of this item |
| **P-G** | `G-CL` holds on **both** rows at the re-solve | `\|CL − 0.5\| ≤ 1e-4` | a MISS on either row makes that row `NOT A RESULT` whatever the drag did |
| **P-H** | **the NAIVE one-factor attribution is NON-ADDITIVE, with `\|ΔCD_aoa\| ≥ \|ΔCD_shape\|`** | scored from the numbers | **a MISS would mean the constraint does NOT couple the channels on this problem, and the matched-lift argument of §3d is wrong.** Predicted HIT — and the HIT is what justifies reporting the matched-lift decomposition as the attribution |
| **P-I** | total graded core-min in **[11.0, 58.0]** (point 20.2) | scored | a MISS is a cost miss carried into the calibration row; the band is not adjusted |
| **P-J** | the trivial baseline at the OPTIMUM fails band D on **≥ 4 of 5** components on the PATCHED row | `G-TB` `PASS` | a MISS means the endpoint FD gate is not measuring the step; `G-TB` `GATE FAIL` and that row's G5E verdict is **WITHDRAWN to `NOT A RESULT`** |
| **P-K** | the age-guard datum resolves to the **COMPRESSED twin `0/U.gz`** on every solver arm | HIT if all four | a MISS means AV-1's diagnosis was incomplete — a finding worth more than this rung |
| **P-mesh** | MESH wall ≤ 120 s | scored | — |

**THE REGISTERED OUTCOME, WRITTEN BEFORE ANY CONTAINER STARTS.** P-A, P-B, P-C, P-D, P-G, P-H, P-I, P-J, P-K, P-mesh **HIT**; P-E **HIT** (the shipped endpoint reading differs from its baseline); P-F **HIT**. **PATCHED row `PASS`. SHIPPED row `GATE FAIL`** — on G5E at `shape[6]`, at the optimum, where SO-1a will have shown it failing at the baseline. **Item `GATE FAIL`.** The `2D · steady · incompressible` "optimization converged" column gains **its shipped row for the first time**, and the lab gains the first measurement it holds of what the IDWarp LE-gradient defect does to an optimum rather than to a gradient.

## 7. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | derivation, and the DELTAS file the supervisor reads |
|---|---|---|
| `so1b_run_arm.sh` | `e8b48ee0940a08e5170490da679a6b0c` | `curriculum_SO1a/so1a_run_arm.sh` (`dbe6e2b6…`) + **`so1b_run_arm_DELTAS_from_so1a.diff`**: item/root/prefix; SO-1a's root added to the forbidden list; the SO-1b cap table with the iteration-bound arithmetic in its comment; the arm command table (`-mode O\|E -row P\|S`); the G-COLD forbidden-artefact list; **`G-CAP-PREREG` (NEW)**; **`G-EDEP` (NEW)** |
| `so1b_chain_driver.sh` | `0d1180dea70d82794856598a644f8fe9` | `curriculum_SO1a/so1a_chain_driver.sh` (`48d358fa…`) + **`so1b_chain_driver_DELTAS_from_so1a.diff`**: names/root/md5s; the per-arm image map; **`G-SO1A` and its two no-launch branches (NEW)**; the selftest-variable refusal; **the `CHAIN_DONE` EXIT trap (NEW)** |
| `so1b_of.py` | `0f14244bee5fafc698e80060782a7606` | `curriculum_SO1a/so1a_xf.py` (`f34bd5bf…`) + **`so1b_of_DELTAS_from_so1a_xf.diff`**: **modes O and E replace X and F**; the registered optimiser settings; IPOPT's own `EXIT:` line read from its own file; **`G-ROWX`**; **the five-point D7R decomposition + `C'` + the operating-point assertion**; the FD table taken at `x*` |
| `so1b_grade.py` | `88157ca3c04798750e97b87ca3d02a15` | **the grading path.** `curriculum_SO1a/so1a_grade.py` (`6966d19e…`) + **`so1b_grade_DELTAS_from_so1a_grade.diff`**. **49/49 under `python3` AND `python3 -O`** (`so1b_grade_selftest_evidence.txt`), plus **five mutation controls** in which each mutated guard is shown to stop firing. `ast.Assert` = 0 in grader and instrument, with the counter shown counting a planted one |
| `so1b_groot5_selftest.sh` | `128555d15c342668cd35939e0133345c` | `curriculum_SO1a/so1a_groot5_selftest.sh` (`b8bee4d0…`) + **`so1b_groot5_selftest_DELTAS_from_so1a.diff`**: SO-1b's arms; **leg (e4) drives `G-EDEP`**; **section (g) drives `G-CAP-PREREG` with four planted disagreements** |
| `so1b_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | **byte-identical** to `so1a_aggregate_memory.py` (`cmp` silent) |
| `so1b_runScript.py` | `0557da51f6f179f6de865144343c499f` | **byte copy** of `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py`; the producer whose header the instrument execs; never modified |
| `so1b_decomposeParDict` | `e6f1b0060944bc86d6dff56480ad2bd4` | the tutorial's `system/decomposeParDict` with `numberOfSubdomains 4 → 1`, ONE line |
| tutorial inputs, md5-asserted at staging | `genAirFoilMesh.py` `681f10659eb90457fca13fc933008b93`; `preProcessing.sh` `4a9395452540705686acf94898aa33af`; `NACA0012PS.profile` `51dfed28e1bdb4cd33e0d8d7dabd586a`; `NACA0012SS.profile` `4a6b8ef4501494c7693b71e88a2eabbf`; `FFD/wingFFD.xyz` `6ddf378b028d03d8a18270488bee1759`; `system/controlDict` `46bb883cfc235d12df020bafbe3a9e78` | checkout `d3b7e38b058aba2a98a74092e15c41ec455c570d`, not frozen by this repository, so its bytes are frozen here |

**THE REGISTERED TOOLCHAIN, BY DIGEST — `DAFOAM_CHARTER.md` §6: the image DIGEST is the identity and the version string is not; there is no such thing as "the fixed toolchain".** Both digests re-read live from `docs/dafoam/TOOLCHAIN_INVENTORY.md`:409-410:

| row | image | **digest** | `libidwarp.so` md5, printed from inside the process that loaded it | arms |
|---|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`** | **`f0fcb488e0e98156575cd19548e91663`**, 491,344 B | MESH, O-S, E-S |
| **PATCHED** | `dafoam-idwarp-rot:v1` | **`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`** | **`85f59e87253e0a71a813f64ca6e4c425`**, 491,344 B | O-P, E-P |

**GUARD PLACEMENT, PROVED BY LINE NUMBER RATHER THAN CLAIMED.** A guard placed after the destructive step is decoration, and placement has been the defect five times in this family. In `so1b_run_arm.sh`:

| line | what happens there |
|---|---|
| **:272** | `SO1B_G_CAP_PREREG_PASS` — the cap-agreement preflight has passed |
| **:286** | `SO1B_G_EDEP_PASS` — the E arm's own-row optimum is present |
| **:301** | the first `G-ROOT.5` refusal |
| **:394**, **:413** | the FIRST destructive acts, `sudo -n rm -rf "$WORK"` |
| **:505** | `sudo -n docker run -d` — the first container |

**Every guard completes before every destructive step, and the selftest re-derives this ordering mechanically rather than trusting the table.** In `so1b_chain_driver.sh`: `G-SO1A` reads at **:140** and refuses at **:147**; the run root is created at **:160**; the first launcher call is at **:250**.

**THE CAP-AGREEMENT PREFLIGHT (`G-CAP-PREREG`), and why it is not the assertion SO-1a already had.** SO-1a's `D4_CAP_ASSERT` checks the launcher **against itself** — it derives the wall deadline from the cap and then inverts the arithmetic. **Two numbers that agree with each other can both be wrong.** `G-CAP-PREREG` checks the launcher **against this frozen document**, on two channels: **(a)** the `SO1B-CAP-MANIFEST v1` line on line 6 above must name exactly the caps this launcher would enforce, and a `CEILING` equal to their sum; **(b)** the same line read from `git show HEAD:<this path>` must be **byte-identical** to the one on disk, so a post-freeze worktree edit cannot move a cap under a launcher about to spend on it. Channel (b) is INFRASTRUCTURE (L-342): unreadable → `NOT_MEASURED`, **never composed to a pass it did not earn**, and channel (a) binds regardless. This is the check that caught W3's **600-against-a-registered-900** before 563 core-min were spent, and a second stale constant behind it. **Driven with four planted disagreements** — a launcher cap of 40.0 against the registered 25.0, a `CEILING` of 999.0 that is not the sum, a manifest line deleted, and the pre-registration file absent — each shown to **abort rc=65 before any container** (`so1b_groot5_selftest_evidence.txt` section g).

**The md5 agreement control ran and is part of the freeze:** the driver's five pinned values and the launcher's three were compared against the files on disk — **all AGREE**. **No `assert` carries a guard** in any python file here (AST count 0 in both, counted by the grader, with a planted assert shown counted; L-332). **Classifier denials in this lane while building SO-1b: none.**

## 8. WHAT THIS ITEM WILL NOT ESTABLISH

**Nothing at np ≠ 1.** `DAFOAM_CHARTER.md` §5: *"a gradient verified at one np is a statement about that np and is never carried to another"*. **The np-invariance spot row Sanaa's §4 pattern names is therefore SO-1c's, not this item's**, and saying so here is not a discovery made later. **Nothing about a second design point or a second start** — D13 already measured the basin on this problem (`GATE FAIL` on the design vector, indistinguishable on drag) and this item does not re-open it. **Nothing about the other four `shape` functions or `patchV[0]`.** **No dot-product test and no complex step** (§3e G6, with AV-2's measurement as the reason). **No grid family, no GCI, no Roache triple** — standing rule 5 has no row here. **Nothing about a mesh other than A1's 4,032 cells**, and nothing about the transonic RAE2822 half of Sanaa's SO-1 sentence. **Nothing about the constraint FAMILIES** — SO-2's subject; this item checks the tutorial's 23 declared geometric rows at the optimum and does not vary, add or study them. A shipped-vs-patched divergence of 0.000 % on some component would be reported with its number and would **not** be read as "the defect is absent"; P-E names the component where a difference is expected and P-F names the consequence looked for.

## 9. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). The grading path is fixed at this commit: `so1b_grade.py` md5 `88157ca3c04798750e97b87ca3d02a15`, asserted by the chain driver before staging and again before the grade.

**Queue entry `verification/queue/dafoam/SO1b_chain_wait.json`**, a **wait-wrapper** behind `cases/dafoam/_common/dafoam_wait_then_launch.sh`: `--case-id SO1b_chain_wait`, `--precondition <SO-1a run root>/F-P/so1a_F.json`, `--prefix so1b_`, `--run-root <SO-1b run root>`, `--deadline-s 86400`, `--driver-pidfile so1b_driver.pid`, then `bash so1b_chain_driver.sh MESH O-P E-P O-S E-S`; `cwd` = this directory; `ranks 1`; `cost_core_min_estimate 20.2`; `cap_core_min_registered 115.0`; `memory_floor_gb 8.0`; `cost_basis` derived / not measured; `permission bc0e687e`; `prereg_commit` = the full 40-hex sha of the commit introducing THIS file, **re-derived with `git log --oneline --diff-filter=A -- <path>` and never from a commit subject line** (`VERIFICATION_CHARTER.md` v1.12 — two commits in this family shared one subject 52 s apart, and the wrong one resolves to a real commit and fails only at the path check).

**ENQUEUEING IS NOT AUTHORISATION**: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own, discharged on the sha, and is not discharged by this document or by the queue entry.

**Predicted outcome, so it cannot be written afterwards:** P-A through P-K and P-mesh **HIT** → **PATCHED row `PASS`, SHIPPED row `GATE FAIL`, item `GATE FAIL`**, with the A1 shipped optimum bought for the first time, the final-design-point FD check discharged on both rows, and the D7R attribution decomposed rather than asserted.
