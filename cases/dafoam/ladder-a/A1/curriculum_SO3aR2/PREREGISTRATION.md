# CURRICULUM SO-3aR2 — NACA0012 ALPHA-MULTIPOINT WEIGHTED OBJECTIVE, INCOMPRESSIBLE: the FD-VERIFIED MULTIPOINT GRADIENT RUNG. SECOND SUCCESSOR TO SO-3a, FIRST TO SO-3aR. PRE-REGISTRATION (FROZEN)

**Version 1.0. FROZEN.** Dated **2026-08-31**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or on completion** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

**NOT LAUNCHED. NOT ENQUEUED. NOT ARMED. NO QUEUE ENTRY IS FILED BY THIS COMMIT.** This document is a rule-2 freeze. Zero solver core-minutes have been spent by the lane that wrote it and no container of any kind has been started. The pre-compute gate is the `dafoam-supervisor`'s (`SUPERVISION_CHARTER.md` §3 check 4) and is **not** discharged here. **In-place validation of the queue entry is ARMING and arming is the supervisor's, not this lane's.**

---

## 0. THE SUCCESSOR ID IS DERIVED FROM PRECEDENT ON DISK, NOT GUESSED

`SO-3a` and `SO-3aR` have both had first compute. **Their gates are CLOSED, their item verdicts — `NOT A RESULT` and `NOT A RESULT` — STAND, and their frozen documents and instruments are NEVER rewritten by this item** (`CLAUDE.md` rule 6). `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception is **DELIBERATELY NOT REACHED FOR**: the re-run costs 22.1 core-min (~$0.019 derived) and **a clause reached for when the cheap path is open is a clause being softened.**

**The id.** This family's FIRST successor appends `R`: `SO-1a`→`SO-1aR`, `SO-1b`→`SO-1bR`, `SO-1c`→`SO-1cR`, `SO-2M`→`SO-2MR`, `SO-3a`→`SO-3aR` — all present as directories under `cases/dafoam/ladder-a/A1/`. **`SO-3aR` is taken, so this is a SECOND successor**, and the second-successor precedent in this tree is **`D12` → `D12R` → `D12R2`**: `cases/dafoam/curriculum_D12R2/PREREGISTRATION.md` §0 states in terms that it *"SUPERSEDES `cases/dafoam/curriculum_D12R/PREREGISTRATION.md`, which itself superseded `curriculum_D12`"* and that both are *"CITED, NEVER REWRITTEN"*. **Appending `2` to the R-form is therefore the precedent followed, and the id is `SO-3aR2`.** The alternative reading — that `D6R`→`D6RG` licenses a letter suffix — was checked and rejected: `D6RG` is a **regrade** of D6R's existing artefacts, not a re-run, and this item is a re-run.

**THE ID WAS VERIFIED FREE BEFORE IT WAS USED, WITH A LIVE PLANTED CONTROL** (`CLAUDE.md` rule 3), because a lane on this box recently pre-assigned a docket number another team already held:

| probe | reader | reading |
|---|---|---|
| `SO3aR2` / `SO-3aR2` anywhere in the repository | `grep -rl` over `*.md *.py *.sh *.json` | **0 files** |
| `*SO3aR2*` under `cases/dafoam/` | `find -maxdepth 6 -iname` | **0 hits** |
| `*SO3aR2*` under `/home/ubuntu/certonomous-runs` | `find -maxdepth 2 -iname` | **0 hits** |
| **PLANTED CONTROL, same readers, same invocation** — `SO3aR` | the same three readers | **5 run-root hits, 5 repository files** |

**All three readers are demonstrably able to report a non-zero and all three report zero for `SO3aR2`.** The absence is a reading, not a blind reader.

---

## 0a. WHY SO-3aR2 EXISTS — SO-3aR's DEATH, AND IT IS A LAB REGRESSION

SO-3aR launched and **DIED AT ITS SECOND ARM**. `chain_rc = 1`, **1.800 core-min**, **2 of 5 declared arms executed**, item verdict **`NOT A RESULT`**, cause class **`NAMING/PLUMBING`** — recorded in `cases/dafoam/ladder-a/A1/curriculum_SO3aR/RESULTS.md`, whose §6 is the governing account and whose every citation below was re-verified against the two source files at write time rather than taken from a brief.

The container log's own words, at line 1868:

> `pyDAFoam Error: /mnt/X-S/0.0001 already exists, moving failed!`

raised at `.../dafoam/pyDAFoam.py:1543` in `renameSolution`, reached from `.../dafoam/mphys/mphys_dafoam.py:483` in `solve_linear`, under `prob.compute_totals(of=of, wrt=["shape"])`. Line **1827** `Moving time 443 to 0.0001` — `point0`'s adjoint, **succeeded**. Line **1865** `Moving time 436 to 0.0001` — `point1`'s adjoint, **collided**.

**ROOT CAUSE, VERIFIED AT SOURCE.** `curriculum_SO3aR/so3ar_runScript.py:245` constructs a `DAFoamBuilder` per operating point inside a loop over `SCENARIOS` and passes **NO `run_directory` to any of them**; `grep -n run_directory` over that file returns **nothing** [MEASURED]. Three independent `DASolver`s therefore shared one case directory, each carrying its own `solution_counter`, and each renamed its converged solution to the same `0.0001`. The second to arrive collided by construction. **The script's own docstring said "own builder, own mesh" and stopped there; the missing third noun is what killed it.**

**THE CURE ALREADY EXISTED IN THIS LAB, ON THE SIBLING LADDER.** `cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_opt_runScript.py` carries it at three lines — `:59` `RUN_DIRS = {"cl04": "mp04", "cl05": "mp05", "cl06": "mp06"}`, `:120` `"gridFile": os.path.join(os.getcwd(), RUN_DIRS[point])`, `:138` `run_directory=RUN_DIRS[pt]` — and `d6r_run_arm.sh:313` stages the three case copies to match. **A1 never carried A2's isolation forward.** That is a **LAB REGRESSION** inside this repository, cause class **BOOKKEEPING/INSTRUMENT** — **not an upstream defect and not physics** — and calling it anything else would be false.

**THE UPSTREAM QUESTION IS OPEN AND UNTESTED AND IS NOT A DEFECT REPORT.** Upstream's own multipoint tutorial at `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/multipoint/runScript.py` adds two scenarios sharing one directory with no `run_directory` anywhere. **But it passes ONE shared `dafoam_builder` to both scenarios where this item constructs THREE**, so a single `DASolver` and a single `solution_counter` may mean the collision cannot arise there at all. That is a reading of source, **not a test**; nobody has run it. **Recorded OPEN/UNTESTED. NOT FILED ANYWHERE** (`CLAUDE.md` rule 7). This item's own instrument distinguishes the two shapes explicitly rather than eliding them — see §3 `G-COLL` limb L1's `how` field, which reports `ONE_SHARED_BUILDER` and `PER_SCENARIO (n DASolvers)` as different readings.

**WHAT SO-3aR ALREADY BOUGHT, CARRIED FORWARD RATHER THAN RE-DERIVED.** All three multipoint primals **CONVERGED** (final residuals 9.671227e-09 / 9.665481e-09 / 9.907086e-09 against tol 1e-08, stopping at 1514/1644/1774 cumulative iterations, `satisfied the prescribed tolerance` ×3, `^End$` ×3), giving `CD = [0.01723938072177922, 0.020910510045267394, 0.027268054119716875]`, `CL = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]`, `J = 0.02180598162892116`, `"non_finite": []`, and the alphas read back equal to the registered values. **`point0`'s multipoint ADJOINT COMPLETED** — `Main iteration 157 KSP Residual norm 1.007293914605e-08`, `PetscConvergedReason: 2`, `Moving time 443 to 0.0001` [MEASURED, `curriculum_SO3aR/RESULTS.md` §5]. **The feasibility of the bracket and of the multipoint assembly's primal side is not in question. Only the directory collision is.** Those figures carry **no verdict**: SO-3aR is `NOT A RESULT`, its gates were never evaluated, and no number above may be quoted as a `PASS`.

---

## 0b. WHAT SO-3aR2 CARRIES UNCHANGED, AND WHAT IS NEW

**CARRIED UNCHANGED IN SUBSTANCE** from SO-3aR's frozen registration, re-frozen here because SO-3aR2 asks the SAME QUESTION: band D **5.0 %** per graded pair; band E **5.0 %** aggregate per row; plateau tolerance **10.0 %** proved PER PAIR; `NEAR_ZERO` **1e-14**; `MIN_GRADED_PAIRS` **3**; `MP_STRUCT_TOL` **1e-10** relative; `ALPHA_TOL_ABS` **1e-12**; `TB_MAX_PASSING` **1**; `CELLS_EXPECTED` **4032**; arms **MESH X-S F-S X-P F-P**, DECLARED **5**; caps MESH 5.0 / X-S 15.0 / X-P 15.0 / F-S 40.0 / F-P 40.0 → **ceiling 115.0**; placement **cpuset 14**; three α `{3.13918623195176, 5.13918623195176, 7.13918623195176}`°; equal weights `{1/3,1/3,1/3}` written `1.0/3.0`; `EVALS_DECLARED = 34` per F arm; **TWO ROWS** `SHIPPED`/`PATCHED`; **NO OPTIMISER** — the parent's driver block stays REMOVED, not merely unreached.

**WHAT IS NEW — five things, and nothing else:**

1. **THE PER-POINT `run_directory` FIX**, ported from D6R (§1).
2. **`G-COLL` — A RED-THEN-GREEN COLLISION LEG** that reproduces the death before it certifies the repair (§3, §1).
3. **THE RULE-3 PLANT IS SIZED RELATIVE TO THE BAND IT MUST CROSS**, with a sufficiency leg driven RED on a shrunken plant (§4).
4. **`G-IC0` — the D19 initial-condition question, MEASURED and REPORTED, never gated** (§5).
5. **`P-PLAT2` — the two-sided plateau reading, registered as a scored prediction beside the one-sided GATE** (§6).

The by-role pin census, the producer pin, the rule-14 row-label sweep, the stop marker, `G-PROV`, the resource guards in the WAIT form and every other instrument are **SO-3aR's, carried and re-driven, not rebuilt.**

---

## THE TEN LINES

| # | field | value |
|---|---|---|
| **1** | **Case** | NACA0012, **4,032 cells**, `DASimpleFoam` (INCOMPRESSIBLE — there is no Mach number on this ground and none is claimed), Spalart–Allmaras with wall functions, `U0 = 10.0 m/s`. **THREE operating points differing ONLY in angle of attack, each in ITS OWN staged case copy `mp0/ mp1/ mp2/`.** Objective **`J = Σᵢ wᵢ·CDᵢ`**, **one shared `shape` design-variable vector of 8 components across all three scenarios, ONE SHARED GEOMETRY COMPONENT.** Task: **`compute_totals` of `J` and of each `CLᵢ` wrt `shape`, and a CENTRAL-FD table beside them at a step PROVED to lie in the plateau PER PAIR.** **NO OPTIMISER RUNS.** `patchV` is **NOT a design variable in this item.** |
| **2** | **Reference** | **No external reference exists**, so **the gate is the lab's own FD table and nothing else** (`DAFOAM_CHARTER.md` §1, §2). Central differences at three registered steps; the reference is the **middle step**; the plateau is proved **PER PAIR**. Reported and never gated: SO-1a's single-point PATCHED `dCD/dx` aggregate **0.0474 %** [MEASURED, `curriculum_D15/RESULTS.md:57`]. |
| **3** | **Quantities** | `CDᵢ`, `CLᵢ` for i = 1,2,3; `J`; `J_adj[J, shape[k]]` and `J_adj[CLᵢ, shape[k]]` for **k ∈ {0, 3, 6, 7}**; `d_fd[k, h]` at **h ∈ {1e-2, 1e-3, 1e-4}**, both signs, per pair; `d_ref` = the middle step; `plateau_neighbour_pct` (**both** entries printed); `rel_err_pct`; `sign_flip`; the per-scenario decomposition `Σᵢ wᵢ·J_adj[CDᵢ, shape[k]]` for **G-MP-STRUCT**; the primal repeatability **η** from two baseline evaluations, measured **before any FD step is sized**; the trivial-baseline table at **h = 1e-8**; the `CTRL` planted row; the `G-IC0` per-point initial-condition census; **DECLARED and EXECUTED stage counts**; `evaluations_declared` and `evaluations_failed` per arm. |
| **4** | **Multipoint angles and weights** | **THREE α: `{3.13918623195176, 5.13918623195176, 7.13918623195176}` degrees.** α₀ is a **QUOTATION** [REGISTERED, `curriculum_SO2a/so2a_runScript.py:35`]; the **±2° bracket is lane-chosen** [REGISTERED, lane-chosen]. **WEIGHTS `w = {1/3,1/3,1/3}`, equal** [REGISTERED, lane-chosen] — a choice, not a default. **THE BRACKET IS FEASIBLE ON MEASURED EVIDENCE AND THE EVIDENCE IS NOW THIS FAMILY'S OWN MULTIPOINT ASSEMBLY, NOT ONLY THE FEASIBILITY RUNG**: SO-3aR's X-S arm ran the real three-scenario model to convergence and returned the `CD`/`CL`/`J` vector quoted in §0a [MEASURED]. `CD` is monotone `0.01723938 < 0.02091051 < 0.02726805` and `CL(α₀) = 0.49876526` against target 0.5. **MEASURED CAVEAT, unchanged in force**: the top angle sits on a flatter part of the curve, slope ratio upper/lower **0.8841**, which is a MEASURED reason to prove the FD plateau **PER PAIR AT THE BRACKET ENDS** rather than inherit it from α₀. |
| **5** | **Ladder** | **A1**, ladder **SO-3**. **SO-3aR2 is the gradient rung and it is the WHOLE of this registration.** SO-3's optimisation rung is a SEPARATE, LATER, UNWRITTEN item; writing its gates now would be fitting them to an answer this item has not produced. Predecessors: SO-1a (`GATE FAIL` / PATCHED `PASS`), SO-2a (**`PASS`**), SO-3a (`NOT A RESULT`, producer pin unset), **SO-3aR (`NOT A RESULT`, per-point run directories absent)**. |
| **6** | **Decomposition method AND seed** | **`np = 1` on every arm** (`DAFOAM_CHARTER.md` §5, serial before parallel). `system/decomposeParDict` overlaid with `numberOfSubdomains 1`, scotch — **NOT EXERCISED** at np = 1. **Seed:** `PYTHONHASHSEED=0` pinned into every container; **no stochastic component exists in this chain** and no RNG seed is claimed. **Registered consequence:** a gradient verified at one np is a statement about that np and **is never carried to another**. |
| **7** | **Criteria** | The gate table in §3. **Item verdict = the composition registered in §3 and nowhere else.** Bands, all frozen now: **band D = per-pair `\|d_ref − J_adj\| / \|d_ref\| ≤ 5.0 %` with the same sign**; **band E = aggregate vector-relative error ≤ 5.0 %**; **plateau tolerance 10.0 %, proved PER PAIR, ONE-SIDED — see §6, where the choice is registered and argued rather than inherited silently**; `NEAR_ZERO` at `\|d_ref\| < 1e-14`; **fewer than 3 graded pairs on a row → that row is `NOT A RESULT`**; **G-MP-STRUCT tolerance 1e-10 relative**; **G-TB `PASS` iff AT MOST 1 of the 4 registered components passes band D at h = 1e-8**. Bands D and E are **by citation, not re-derived by a lane that has seen an answer**: `curriculum_D4/PREREGISTRATION.md:82` and `curriculum_D7FR/PREREGISTRATION.md:228-229`. |
| **8** | **Cap** | **REGISTERED CAP: 115.0 core-min**, cumulative over every container, = Σ of the per-arm caps in §7 and asserted as that sum in the comparator's `main()`. **An overrun stops the run; it does not get a new budget** (`CLAUDE.md` rule 12). Per-arm caps: MESH 5.0; X-S 15.0; X-P 15.0; F-S 40.0; F-P 40.0. **Memory cap 12 GiB per arm.** |
| **9** | **Cost** | **Point 22.1 core-min, band [14.0, 60.0], ceiling 115.0.** Dollars **DERIVED, not measured**: point **$0.01890**, ceiling **$0.09833**. **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **GPU: 0 GPU-h.** SO-3a's 0.334 and SO-3aR's 1.800 core-min are carried in §7 **AS SPENT AND NAMED AS WASTE** and are **NEVER absorbed into SO-3aR2's actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). A calibration row in `docs/COST_CALIBRATION.md` is **owed at completion** (rule 12). |
| **10** | **Verdict labels** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and no others. **No grid family exists here, so standing rule 5 has no row and NO GCI IS QUOTED.** `NOT_MEASURED` and `NOT EXERCISED` fields are printed **beside** the verdict, never inside it. |

---

## 1. THE FIX, AND THE LEG THAT PROVES IT BY FAILING FIRST

### 1.1 The fix

`so3ar2_runScript.py` now carries, derived from `SCENARIOS` and never hand-written:

    RUN_DIRS = {sc: "mp%d" % i for i, sc in enumerate(SCENARIOS)}

`mesh_options_for(point)` sets `"gridFile": os.path.join(os.getcwd(), RUN_DIRS[point])`, and each builder is constructed as `DAFoamBuilder(daOptions, mesh_options_for(sc), scenario="aerodynamic", run_directory=RUN_DIRS[sc])`. **The keys are derived rather than spelled out because a hand-written map is one more call site of the scenario label, and a scenario added with no row would fall back silently to the shared directory — which is exactly the failure being repaired.**

`so3ar2_run_arm.sh` stages **one full case copy per point** from the MESH arm's output — `for mp in mp0 mp1 mp2; do cp -a "$BASE/MESH" "$WORK/$mp" …` — each with its own cold-start guard (no `processor*`, no time directory, `0/U` or `0/U.gz` present) and its own age-guard datum touched last. The FFD and the instruments stay at the arm directory, which is the container's working directory. **This is D6R's shape (`d6r_run_arm.sh:313`), not a new invention.** The copies happen on the host BEFORE `T0`, so they are not billed to the arm's core-minutes.

### 1.2 `G-COLL` — the leg, and what it fired red on

**A FIX WITHOUT A LEG THAT FAILS ON THE UNFIXED STATE IS NOT PROVED.** `so3ar2_collision_leg.py` does not assert the repair; it **drives the failure first** and refuses to report green unless it has seen red in the same invocation. Five limbs, **one mutation each**, because a compound mutant cannot attribute a detection:

| limb | what it does | required reading |
|---|---|---|
| **L1** | the frozen `so3ar2_runScript.py`: resolve each builder's `run_directory` from the AST, make the directories, perform **real `os.rename` calls on a real filesystem** | GREEN — three distinct destinations |
| **L2** | the SAME bytes with **ONE** mutation: the `run_directory=` keyword **argument** deleted | **RED** — must raise |
| **L3** | **SO-3aR's OWN FROZEN `so3ar_runScript.py`**, read READ-ONLY and never written | **RED** — must raise, carrying the literal `already exists, moving failed!` |
| **L4/L4b** | every value of `RUN_DIRS` must appear in the launcher's **staging loop**; a copy with that one entry removed must be caught | L4 ok, **L4b NOT ok** |
| **L5** | **rule 3**: blind the leg's own AST extractor | **exit 2, REFUSE** — the absence of a reading, neither green nor red |

**THE EXACT EVIDENCE IT FIRED RED ON THE UNFIXED STATE**, from the leg's own stdout in the run that also reports `rc=0` [MEASURED, `so3ar2_collision_leg_evidence.txt`]:

* **L3, on SO-3aR's real frozen bytes** (md5 `53ba67c95461f86a585cb7ec7cdc2b39` — the file that actually died in production): `'how': 'PER_SCENARIO (3 DASolvers): CWD_FALLBACK -- no run_directory keyword; …'`, `'run_directories': ['.', '.', '.']`, `'distinct_parents': False`, `'collided': True`, `'message': "pyDAFoam Error: …/L3_parent_real_bytes/0.0001 already exists, moving failed!"`.
* **L2, on this item's own bytes with one mutation**: the identical structure and the identical message.
* **L1, on the frozen fix**: `'run_directories': ['mp0','mp1','mp2']`, `'distinct_parents': True`, `'collided': False`, `'destinations': ['mp0/0.0001','mp1/0.0001','mp2/0.0001']`.

**AND THE LEG IS ITSELF DRIVEN FROM OUTSIDE**, in `so3ar2_groot5_selftest.sh` legs `(c0)`–`(c6)`, in a temp tree that mirrors the real layout: `(c1)` green; `(c1b)` the red limbs are present **inside** the green run; `(c2)` a mutated producer → **exit 2**; **`(c3)` the leg goes RED (`rc = 1`, `L1 THE FIX DID NOT HOLD -- the frozen producer collided`) when the `run_directory` keyword is removed from the producer and the leg's pin is re-pointed at the mutant** — this is the load-bearing leg; `(c3b)` restore proved by hash; `(c4)` the launcher limb goes RED when one directory leaves the staging loop; `(c5)` the blinding control; `(c6)` **SO-3aR's frozen producer is byte-identical after every leg above**, re-asserted rather than assumed.

**TWO DEFECTS IN THIS LANE'S OWN FIRST DRAFT, FOUND BY DRIVING AND RECORDED BECAUSE THEY ARE THE SAME SHAPE AS THE ITEM'S SUBJECT.**
1. **The leg counted `DAFoamBuilder(` CALL SITES and read "1" for a construction inside `for i, sc in enumerate(SCENARIOS):`**, then labelled the result `ONE_SHARED_BUILDER`. It reached the right destinations by luck and the label was false. It matters because "one call site executed three times" (three `DASolver`s, three counters, collision) and "one builder object passed to three scenarios" (one `DASolver`, no collision) is **exactly** the structural difference between this item and upstream's tutorial, and it is the reason this record does not call upstream broken. The loop is now detected, not assumed.
2. **L2's mutation deleted the whole source LINE**, which in this file also carries the call's closing paren, so the mutant did not **parse** — and a mutant that does not parse tests the reader's error handling, not the repair. The keyword argument is now deleted, comma and all.
3. **L4 asked whether the string `mp1` appeared ANYWHERE in the launcher.** It does — the launcher also iterates `mp0 mp1 mp2` in the `G-IC0` block — so deleting `mp1` from the **staging** loop left the check GREEN. **A check that reads green on the mutation it exists to catch is worth less than no check.** The staging loop is now identified by the copy it performs.

**WHAT `G-COLL` DOES NOT ESTABLISH, stated here and in the instrument's own docstring rather than in a footnote.** `pyDAFoam.py` **is not on this host** (`find / -name pyDAFoam.py` returns nothing [MEASURED]); it lives inside the container image. The destination **name** the model computes — `"%g" % (1e-4 × counter)`, counter starting at 1 — is **RECONSTRUCTED FROM THE MEASURED LOG STRINGS** of SO-3aR's death, not read from upstream source, and is labelled a model. **What is not modelled is the load-bearing part**: the collision is a real one, made with real directories and the real `os.rename`, and the structural claim does not depend on the naming rule at all — three solvers whose counters start at the same value produce the same basename whatever it is, so they collide **iff** they share a parent. It establishes **nothing** about whether three `DASimpleFoam` `DASolver`s co-exist correctly once isolated; that is a runtime question only the X-S arm answers, and `P-EVAL` is registered against it.

---

## 2. THE GRADIENT RUNG RUNS FIRST AND STANDS ALONE — AND WHAT ENFORCES IT

**LIMB 1 — WITHIN SO-3aR2: ENFORCED BY CONSTRUCTION.** The registered arm set is **`MESH, X-S, F-S, X-P, F-P`** and **contains no optimiser arm**. There is no `run_driver`, no `pyOptSparse` invocation, no `max_iter` and no majors anywhere in the registered program — the parent's optimiser driver block is **REMOVED, not merely unreached**. The comparator refuses any artefact carrying an optimiser history (`G-NOOPT`). This is not a promise about behaviour; it is the absence of the capability, checkable against the arm table today.

**LIMB 2 — ACROSS ITEMS: ⚠ NOTHING ENFORCES THIS.** In those words. The successor does not exist, so no file gates it, and **a requirement in prose has no call sites.** SO-3aR2's completion writes a **stop marker** naming its item verdict and `G5J` reading into its run root on **every** exit path; SO-3aR proved that writer works on the worst path, firing on a truncated chain and writing `verdict: PENDING`, `verdict_source: NO READABLE COMPARATOR VERDICT AT THIS ADDRESS`, `truncated: true`.

**G-PROV — THE TRAVELLING SHIPPED `GATE FAIL`, ENFORCED IN CODE**, carried unchanged: the comparator refuses to emit any verdict unless a structured `upstream_provenance` block is present, its SHIPPED row status reads exactly `GATE FAIL`, and the `verdict_line` is byte-identical to the bytes the module composed (L-405). **`verdict` itself stays exactly one of the six tokens and is never decorated.**

---

## 3. GATES, THRESHOLDS AND LABELS — frozen now

Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

**Every gate SO-3aR registered is carried here UNCHANGED IN SUBSTANCE and is not restated at length; the operative text is SO-3aR's §3 and SO-3a's before it, and the constants are in §0b.** In brief: **G1** completion (the five rule-4 clauses printed individually per arm, age guard resolved by EXISTENCE never by name, fatal-token refusal regardless of rc); **G-M2** cells == 4032; **G-ALPHA** each scenario's α equal to line 4 to 1e-12 absolute, else REFUSE; **G5J** the bright line on `J` per row with the plateau proved PER PAIR and a sign flip a `GATE FAIL` whatever the magnitude; **G5C** the same on each `dCLᵢ/dx`; **G-MP-STRUCT** the assembly identity at 1e-10; **G-TB** the trivial baseline at h = 1e-8 (`DAFOAM_CHARTER.md` §4's registered trivial baseline for an FD gate — the same probe at a deliberately wrong step), `PASS` iff at most 1 of 4 passes band D, else that row's `G5J` is **WITHDRAWN to `NOT A RESULT`**; **G-NOOPT**; **G-STAGES**; **G-EVALFAIL** — a chain stop and a failed evaluation are BOTH GRADABLE STATES and the comparator refuses only on a MALFORMED artefact, never on an ABSENT one; **G9** toolchain per row (image tag, image ID and `libidwarp.so` md5 — a version string is not an identity, `DAFOAM_CHARTER.md` §6); **G10** caps; **G11** OOM hard; **G12** placement.

**THE GATES THAT ARE NEW OR MOVED IN SO-3aR2:**

* **`G-COLL` — THE RED-THEN-GREEN COLLISION LEG, AN ARMING PRECONDITION.** `so3ar2_collision_leg.py` must exit **0** on the frozen tree before the item is armed, **and its stdout must carry L2 and L3 as `collided: True`** — a green that has not seen red is not a reading. §1.2 is the operative text. **Falsifier:** any limb reading the wrong way → the item is **NOT ARMED**.
* **`G-PINS` — THE BY-ROLE PIN CENSUS, AN ARMING PRECONDITION**, carried from SO-3aR and **re-driven against SO-3aR2's file set**. It enumerates every constant that FUNCTIONS as an identity pin — whatever its value's shape — by **two independent enumerators**: **E-NAME** (the identifier carries the token `MD5`, value shape ignored) and **E-SHAPE** (the value is a bare 32/64-hex or `sha256:` literal, identifier ignored). Neither is trusted alone. It then asserts **A0** source-list completeness, **A1** every constant has a disposition row, **A2** every LOCAL/TUTORIAL/CONTAINER pin holds a **real md5** — *the assertion that would have stopped SO-3a*, **A3** every resolvable pin **EQUALS** the md5 of the file it pins — *SET IS NOT CORRECT*, **A4** no dead pin, **A5** no unregistered consumer, **A6** table-versus-code target agreement, **A7** no stale row. **Rule 3: before any assertion is evaluated it plants a known perturbation into every source (limb C1) AND injects a known pin into every source (limb C2) and requires its own extractor to read both back; if it cannot it REFUSES (exit 2) and reports NOTHING.** Its six mutation legs `(x15a)`–`(x15f)` prove it able to fail in six independent directions from ONE mutation each, and `(p4)` blinds its python extractor and requires exit 2.
* **`G-IC0` — the initial-condition census. MEASURED AND REPORTED, NEVER GATED.** §5.
* **`P-PLAT2` — the two-sided plateau reading. SCORED, NOT GATED.** §6.

* **Rule-3 planted-zero control, in the instrument AND the comparator.** The instrument's `CTRL` row (identical DVs both sides plus a planted row) is written, **re-read from disk**, and the instrument **exits 2 if the read-back cannot see the plant**. The comparator's `grader_plant_F` / `grader_plant_X` / `grader_plant_cells` / `grader_plant_c5` re-read their plants through the real readers. **Every planted control reports `EXERCISED-PASS`, `EXERCISED-FAIL` or `NOT EXERCISED` BESIDE the verdict; `NOT EXERCISED` is never counted as a pass.** The **sizing** of the comparator's gate-flipping plant is §4.
* **THE CONVERGENCE LIMB IS REPORTED, NEVER GATED**, its discriminators verified against a REAL producer log on this box [MEASURED, `reference/REAL_SO1a_X-S_arm.log`]. **The FPE banner on this box reads, verbatim, `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`** — a **SAFETY NOTICE, not a crash**, and the one benign line carrying a fatal token, named as such rather than suppressed. A naive `grep -i error` limb reports five crashes per success on this case.
* **DIVERGENCE** shipped-vs-patched on the adjoint, per component, is **reported with its number**, never gated. A divergence of 0.000 % on some component is **reported with its number** and never read as "the defect is absent".

**ITEM VERDICT — the composition, registered here and nowhere else.** Any comparator refusal, any row `NOT A RESULT`, any `G-TB` withdrawal, or **`executed < declared` where the shortfall is not a registered resource block** → **`NOT A RESULT`**. Else `executed < declared` from a registered resource guard reaching its bound → **`BLOCKED`**, naming the guard and its series. Else any of `G-M2` / `G-ALPHA` / `G-MP-STRUCT` / `G9` / `G10` / `G12`, or any row `GATE FAIL` → **`GATE FAIL`**. Else **`PASS`**.

---

## 4. THE PLANTED-ZERO CONTROL IS SIZED **RELATIVE TO THE BAND IT MUST CROSS**

**THE INCIDENT.** `SO-2M` was lost because it inherited **`PLANT = 1.234e-03`** — an ABSOLUTE constant sized on a CD-scale item — and applied it to a **`CMZ`** reference. 1.234e-03 is **2.48 %** of that reference and the gate's band is **5 %**. **THE PLANT COULD NOT CROSS ITS OWN BAND.** The control ran, reported itself EXERCISED, and demonstrated **nothing**: a gate that stays `PASS` under a plant too small to fail it has not been shown able to read a violation. An absolute plant is a claim about the **scale of the quantity**, and this comparator grades four quantities (`J`, three `CL`) whose scales already differ by more than an order of magnitude.

**THE FORM, REGISTERED AT THE FREEZE:**

> **plant_i = K · (band_D / 100) · |d_ref_i|**, with **`PLANT_K = 3.0`**

where `d_ref_i` is **the same reference the gate divides by** — the middle FD step for that exact pair — so the planted relative error is **`K × band_D` = 15 % against a 5 % band, BY CONSTRUCTION, whatever the quantity's scale.** `K` is registered here, before any compute. It is not larger because a plant that dwarfs the band would also flip a gate whose band had been mis-registered by an order of magnitude, and the control would stop being able to see that. Where `d_ref` is zero or non-finite the registered absolute `PLANT` is the fallback, and **the record says which sizing was used** (`plant_sizing` field) — but such a pair is already excluded `NEAR_ZERO` before the gate sees it.

**WHY SCALING THE PLANT TO THE BAND IS NOT FITTING THE CONTROL TO THE DATA.** Fitting to the data would be choosing a **threshold**, a **band** or a **label** after seeing an answer — rule 2 — and **none of those moves here: band D stays 5.0 %, band E stays 5.0 %, the plateau tolerance stays 10.0 %, and every label is unchanged.** What is sized is the **perturbation in a negative control**, and a negative control has exactly one job: **demonstrate that the gate CAN fail.** A plant smaller than the band cannot do that job — it is a **broken control, not a strict one** — and a plant enormously larger tests only that arithmetic works. Sizing it to the band is sizing the **instrument** to the **question**, which is what an instrument is for. The plant never touches the graded artefact: it is written to a separate copy under `grader_controls/`, the real reading is taken from the real bytes, and the item's verdict is composed from the unplanted artefact alone.

**AND THE SUFFICIENCY IS PROVED BY BEING DRIVEN INSUFFICIENT.** `PLANT_K_INSUFF = 0.2` reproduces SO-2M's geometry exactly — a plant at **1 % against a 5 % band** — and units `U28f`/`U28g` require the flip **NOT** to happen at that K. **A sufficiency claim that is not driven at an insufficient K is the same shape as SO-3a's leg `A5`, which asserted a pin was a sentinel and went on passing after the pin should have been set.** The five new units are `U28c` (the plant is relative and names its `d_ref` scale), `U28d` (planted relative error = `K × band_D` to 1e-9), `U28e` (it clears the band), **`U28f` (at `PLANT_K_INSUFF` it does NOT clear the band and the gate does NOT flip)**, `U28g` (that case is SO-2M's geometry). `EXPECTED_UNITS` is bumped **92 → 97 deliberately, with its reason written beside the constant.**

**THE ABSOLUTE PLANT IS KEPT WHERE IT IS CORRECT, AND THAT IS NOT AN OVERSIGHT.** The instrument's `CTRL` row and the comparator's `grader_plant_F` are **read-back controls**: they add a known constant to every derivative and require the reader to see **exactly** that constant to a relative 1e-12. They are not graded against a percentage band, so there is no band to cross and a relative sizing there would be meaningless. **Only the plant that must flip a banded gate is sized to that band.**

---

## 5. `G-IC0` — DOES EACH POINT START FROM THE INTENDED INITIAL CONDITION? MEASURED, REPORTED, NEVER GATED

**THE MEASURED FACT THAT RAISES IT.** The `dafoam-supervisor` measured on **D19** (the compressible sibling, 2026-08-31T21:54Z) that **DAFoam REWRITES `0/U` in the case directory DURING a SERIAL (`ranks=1`) run** — `S1/0/U.gz` mtime 21:53:52, i.e. **43 s into a 51 s run**, on the only `ranks=1` arm and the only arm with a time directory. Parallel arms write into `processor*/` and do not touch `0/`.

**WHAT IS AND IS NOT NEW ABOUT IT, stated so the record is not inflated.** `DAFOAM_CHARTER.md` §6 (`:237-239`) **already** records that pyDAFoam writes the primal end state back into the time-0 directory **at run end**, so the second run of a case directory silently warm-starts, and it **already** makes the staged-copy pattern or a checked first `Time step continuity errors` value mandatory. **D19's genuine addition is dating it MID-RUN at `ranks=1` rather than at run end.**

**THE PER-POINT `run_directory` REPAIR DOES NOT CURE THIS AND IS NOT CLAIMED TO.** Isolation stops three `DASolver`s renaming into **one** destination; it says nothing about **one** `DASolver` rewriting the `0/` inside its **own** directory between evaluations. **This item runs 34 declared evaluations per F arm at `ranks = 1`, which is D19's configuration exactly, so the mechanism is LIVE here after the fix.**

**THE MEASUREMENT.** The launcher hashes every `0/` field per point at stage time — **last**, so the datum dates the intended initial condition — into `.so3ar2_ic0_md5`, and **after** the container exits re-checks them, writing `<ARM>_IC0.json` with, per point, `n_ic_fields`, `n_changed_during_run`, the stage datum epoch and the post-run `0/` mtime. The second limb is the item's **existing** primal repeatability **η**, measured from two baseline evaluations before any FD step is sized — no new instrument is invented for it.

**THE REGISTERED EXPECTATION, anchored on a measurement and not on a guess.** D19's own instrument measured **`eta_raw = 1.3011e-10` and `9.6522e-11`** across two arms, `eta_floored = false`, against `CD_baseline = 0.0146` — about **9e-9 relative**. **At that magnitude this is not a threat to a gradient number at any step in `{1e-2, 1e-3, 1e-4}`.**

**THE REGISTERED OUTCOME AND ITS FALSIFIER.** `G-IC0` is **REPORTED WITH ITS NUMBER AND NEVER GATES.** It is **not** a launch blocker: `n_changed_during_run > 0` is expected and is recorded as **MEASURED**, not as a failure. **The falsifier is magnitude, not existence**: if this item's own η comes back **orders larger than 1e-10**, that is a **FINDING**, it is reported to the supervisor immediately, and it is stated as a finding rather than absorbed. If no `<ARM>_IC0.json` is produced — no solver arm ran — the reading is **OPEN**, never a pass. **An evidence field annotated "diagnostic only" is worse than one never computed**, so the outcome is registered here with a falsifier rather than merely printed.

---

## 6. THE PLATEAU RULE IS ONE-SIDED, AND THE CHOICE IS REGISTERED RATHER THAN INHERITED

**WHAT THE CODE DOES.** `so3ar2_grade.py:_pair` computes both neighbour deviations `nb = [|d(1e-2) − d_ref|/|d_ref|, |d(1e-4) − d_ref|/|d_ref|] × 100` and excludes the pair only `if min(nb) > PLATEAU_TOL_PCT`. **`min`** — so the middle step is accepted when **ONE** neighbour agrees to 10 %.

**THIS ITEM ACCEPTS THE ONE-SIDED RULE AS THE GATE, AND SAYS WHY.**
1. **A repair must not be confounded with a threshold change.** SO-3aR2's job is to repair a directory collision. Every plateau reading in this family — SO-1a, SO-2a, SO-3a, SO-3aR — is on the one-sided rule. Moving it in the same item that moves the plumbing would make a `NOT A RESULT` unattributable between the two, which is the specific failure `DAFOAM_CHARTER.md` §5 records for A4's decomposition (a published 10.04 % that stood for two days as a gradient defect before the decomposition was varied).
2. **A tightened rule costs content, and the cost is not free.** With only three steps a decade apart, requiring both neighbours inside 10 % raises the chance of `NO_PLATEAU`, and fewer than 3 graded pairs makes the whole row `NOT A RESULT`.
3. **The one-sided rule's known weakness is real and is named**: it admits a middle step sitting on the shoulder of the truncation-dominated regime. `ladder-a/A_stepsize_study.md` is this lane's own instance — idx6's estimate crosses the adjoint's magnitude once on its way to +110 %.

**SO THE TWO-SIDED READING IS BOUGHT AND SCORED RATHER THAN DISCARDED. `P-PLAT2`, REGISTERED:**

| # | prediction | value | falsifier and consequence |
|---|---|---|---|
| **P-PLAT2** | the number of pairs that would be graded under a **TWO-SIDED** plateau rule (`max(nb) ≤ 10.0 %`) is **equal** to the number graded under the registered one-sided rule, on both rows | equal counts, ≥ 3 either way | **any pair graded one-sided but not two-sided → MISS.** A MISS does **not** move this item's gate, verdict or label. Its registered consequence is forward: **the SO-3 optimisation rung registers the two-sided rule**, and the pairs that differ are named in this item's RESULTS. |

**BOTH `plateau_neighbour_pct` ENTRIES ARE ALREADY PRINTED PER PAIR**, so this costs zero additional compute — it is a reading of numbers the comparator computes anyway. **It is registered as a scored prediction with a named consequence precisely so it is not the "diagnostic only" annotation this lab has ruled worse than no number at all.**

---

## 7. COST — AND THE PREDECESSORS' SPEND CARRIED IN AS WASTE, NEVER ABSORBED

**Every anchor names the program it prices on and asserts the match** (`DAFOAM_CHARTER.md` §18.1, §12).

| anchor | value | match |
|---|---|---|
| **A1** SO-3aR's own MESH arm, `rc = 0`, complete | **0.267 core-min MEASURED** | matches on **all four** terms — same case, same image, ranks = 1, no adjoint. It is this item's own program one generation back. |
| **A2** SO-3aR's own X-S arm, **TRUNCATED** | **1.533 core-min MEASURED** | matches on all four terms but is a **LOWER BOUND, not a complete arm**: it bought three converged primals plus `point0`'s complete adjoint plus `point1`'s adjoint up to the rename, then died. **It is used to CORROBORATE the point estimate and never as the estimate itself.** |
| **A3** SO-1a's X-S/X-P 1.017 / 1.200 core-min, ×3 for scenario count | 3.05 / 3.60 | the parent's derivation, unchanged |
| **A4** the per-primal upper bound **0.062585 core-min/primal** (warm, serial, no adjoint, no colouring) | — | matches, and is an **UPPER** bound |
| **A5** C-188's ×1.6308 multipoint correction | — | **DOES NOT MATCH on ranks (4 vs 1), geometry (3-D wing vs 2-D airfoil) or unit (per-major vs per-evaluation)** and is therefore **EXCLUDED from the point estimate**, used ONLY as a named `[EXTRAPOLATED]` contingency sizing the X-arm cap. |

| arm | point (core-min) | cap (core-min) | in-container wall (np = 1) | mem |
|---|---|---|---|---|
| MESH | **0.30** | 5.0 | 300 s | 12g |
| X-S | 3.1 | 15.0 | 900 s | 12g |
| X-P | 3.7 | 15.0 | 900 s | 12g |
| F-S | 7.5 | 40.0 | 2400 s | 12g |
| F-P | 7.5 | 40.0 | 2400 s | 12g |
| **total** | **22.1** point, band **[14.0, 60.0]** | **ceiling 115.0 = Σ caps**, asserted in `main()` | ≈ 24 min wall at the point | |

**THE ONE ANCHOR THAT MOVED, AND IT MOVED ON A MEASUREMENT.** SO-3aR predicted MESH at **0.19** and measured **0.267** — ratio **1.40**. The point is raised to **0.30**. **A prediction that lands is only evidence if the misses are on the record too**, and this is a miss being corrected rather than a range being widened after the fact: the cap is unchanged at 5.0.

**34 declared evaluations per F arm × 3 scenarios = 102 primals per F arm**; at A4's upper bound `102 × 0.062585 = 6.384` core-min plus setup bounded above by a whole X arm → point 7.5 per F arm.

**THE THREE CASE COPIES ADD NO BILLED COMPUTE**, and that is a reading of the launcher rather than an assumption: `cp -a` runs on the host **before** `T0`, and core-minutes are measured from `T0` to container exit. **UNMEASURED and named as such**: whether three `DASolver`/IDWarp instances each reading their own mesh run measurably slower than three sharing one directory is **not known**; the X-arm caps carry A5's `[EXTRAPOLATED]` contingency and this is one of the things it is there for.

**DOLLARS ARE DERIVED, NOT MEASURED.** Point `22.1 / 60 × $0.0513 = $0.01890`; ceiling `115.0 / 60 × $0.0513 = $0.09833`. **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER 2026-08-21/22, NOT MEASURED — this box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **Runs under $25 are pre-authorised and a blanket is not a per-item read** (`CLAUDE.md` rule 9) — the item is costed here regardless.

**THE PREDECESSORS' SPEND, CARRIED IN AS SPENT AND NAMED AS WASTE** (`COMPUTE_BUDGET_CHARTER.md` §6):

| what | core-min | disposition |
|---|---|---|
| SO-3a, 2 arms, died on an unset producer pin | **0.334 MEASURED** | **WASTE.** |
| SO-3aR, 2 of 5 arms, died on the directory collision | **1.800 MEASURED** | **WASTE.** Its own calibration row records the attribution honestly as **TRUNCATION at arm 2 of 5, not misprediction** — MESH 0.267 against a 5.0 cap and X-S 1.533 against a 15.0 cap, both well inside envelope. |
| **total carried** | **2.134 MEASURED** | **WASTE, NAMED SEPARATELY. It is NOT added to SO-3aR2's predicted cost and is NEVER folded into SO-3aR2's actual/predicted ratio.** It is reported beside that ratio as the cost of the defect this item repairs. |

**Cap mode.** Each arm's wall deadline is **inside the container** (`timeout -k 60` at `cap × 60 / ranks` s; the launcher asserts the enforced wall equals the registered cap to 0.02 core-min and aborts otherwise). **An overrun stops the run; it does not get a new budget.**

---

## 8. MEMORY, PLACEMENT AND THE RESOURCE GUARDS IN THE **WAITING** FORM

Carried from SO-3aR unchanged. **Memory cap 12 GiB per arm** (`DAFOAM_CHARTER.md` §7 — the envelope is predicted, stated and checked **before** the adjoint launches), against D13's measured **1.70 GiB** peak RSS for this case at np = 1 and an `[EXTRAPOLATED]` `3 × 1.70 ≈ 5.1 GiB` bound for three `DASolver` instances — better than 2× headroom, and the item's own first solver arm **measures** it. **H5** (windowed `MemAvailable` floor 16.0 GiB, 45 samples over 60 s) is a **TRANSIENT** quantity in the **WAIT** form: poll 30 s, bound `H5_BOUND_S = 3600`, expiry **STOPS** the chain at `rc = 7`. **AGGREGATE** (live sibling caps + this arm's cap + host non-container RSS < 30.6 GiB) is a **STABLE** quantity, also WAIT, bound 14400 s, expiry `rc = 6`. **SO-3aR2 REGISTERS NO BLOCK-AND-CONTINUE ANYWHERE**; every guard STOPS with a non-zero rc, so no discard fraction compounds. Discard fractions per arm: 100/80/60/40/20 %. **Placement: np = 1, cpuset 14, not core 0**; at np = 1 the delivered-cores floor does not apply and is not composed. **SO-3aR's launch measured the guards working**: H5 read min 28.58 GiB against the 16.0 floor with `samples_below_floor = 0` and `waited_s = 0`.

**THE ONE MEMORY DELTA, DISCLOSED**: three staged case copies add **disk**, not RAM — about 3× the MESH arm's case size per solver arm. It is not a memory-envelope change and is not counted as one.

---

## 9. EXPECT AN EVALUATION FAILURE — carried

Sanaa's instruction is carried unchanged. **SO-3aR2 runs no optimiser**, so D6/D6R's proximate mode (IPOPT `Invalid number in NLP function or derivative detected`) is structurally unreachable and this document does not pretend otherwise. **What IS reachable is an evaluation FAILING — by flag or by value, undetermined**, which is the honest form SO-3aR's own `ADDENDUM A-2` established: the IPOPT guard's condition `success && IsFiniteNumber(ret)` **fails disjunctively** and prints the identical string either way, and D6R's record supports the **failed-status** limb (671 `Primal solution failed!` banners against 673 alpha cutbacks) while **the non-finite-value limb is neither established nor excluded**. Multipoint amplifies a per-primal failure probability `p` to `1 − (1−p)³ ≈ 3p` across 306 primals in two F arms. This document quotes **NO D6 per-major cutback rate as measured.**

**REGISTERED PREDICTION P-EVAL:** at least one of the 34 declared evaluations per F arm fails or returns a non-finite value, most probably at 7.139° at h = 1e-2. **A MISS IS A GENUINELY USEFUL READING.**

**AND THE PART THAT IS A GATE:** a chain stop and a failed evaluation are **BOTH GRADABLE STATES**. The comparator's arm loop is a **census, not a requirement**: it prints `RAN`/`NOT RUN` per arm, grades every arm that ran, and **REFUSES ONLY on a MALFORMED artefact, NEVER on an ABSENT one** — `D6-GRADER-DEF-1` must not repeat. **SO-3aR's comparator proved this on the worst path twice**, emitting `NOT A RESULT -- the comparator REFUSED` with a structured refusal rather than degrading.

---

## 10. INSTRUMENTS — §18.3, AND THE ORDER IS STATED HONESTLY

**THE ORDER, AS IT ACTUALLY HAPPENED, BECAUSE §18.3 IS ABOUT AN ORDER AND NOT ONLY A STATE.** md5s of these files were taken **during the derivation and the re-pinning**, before any separate existence pass — the re-pinning cannot be done without them. A **separate `test -f` existence pass** was then run, at **2026-08-31T22:27:39Z**, **with live planted controls in the same invocation** (`CLAUDE.md` rule 3):

| probe | reader | reading |
|---|---|---|
| the thirteen instruments below | `test -f`, one at a time | **`present = 13 of 13`, absent = 0** |
| **PLANTED CONTROL (must read ABSENT)**, same reader, same invocation | `test -f so3ar2_NO_SUCH_FILE.py` | **ABSENT** |
| **PLANTED CONTROL (must read PRESENT)**, same reader, same invocation | `test -f ../curriculum_SO3aR/so3ar_grade.py` | **PRESENT** |

**The reader is demonstrably able to report both readings.** SO-3aR's `ADDENDUM A-1` had to correct exactly this sentence in the other direction — it claimed an order it had not performed — and writing the true order here is that correction applied rather than repeated. §18.3 exists because `SO2a-DRIVER-DEF-1` read *"eight of eight AGREE"* while the driver executed an absent file: **an md5 over a subset can read agreement on every pin it holds while a dependency is missing.**

| # | file | md5 | derived from |
|---|---|---|---|
| 1 | `so3ar2_chain_driver.sh` | `b1aedbfce566c71e27fe83663405fce1` | `so3ar_chain_driver.sh` @ `0d93f2c4abe927aa40d3e6eef3340d6a` + re-pinning |
| 2 | `so3ar2_run_arm.sh` | `ebc127f7039acc7b8422ee23442a8360` | `so3ar_run_arm.sh` @ `a2cc2da84d5ccccd93d4a121a592a3f3` **+ the three per-point case copies + G-IC0** |
| 3 | `so3ar2_xf.py` | `d6e9117d5971b56fefc5f96d366acf74` | `so3ar_xf.py` @ `aa213384d92f6e07de90c40167854ce9` + the producer pin re-set |
| 4 | `so3ar2_grade.py` — **THE GRADING PATH (§12)** | `c81a09a90950cb1610f40a91b29cdabe` | `so3ar_grade.py` @ `67c386b4548825361418f757f653b9fa` **+ the relative plant + 5 units + the 11-file sweep** |
| 5 | `so3ar2_runScript.py` — **THE PRODUCER** | `d9ac0faf5b5e49d686db74db4cdbc1aa` | `so3ar_runScript.py` @ `53ba67c95461f86a585cb7ec7cdc2b39` **+ RUN_DIRS + mesh_options_for + run_directory=** |
| 6 | `so3ar2_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | byte-identical to SO-3aR's |
| 7 | `so3ar2_groot5_selftest.sh` | `2a131d53c8f5bce678133b4bd0349498` | `so3ar_groot5_selftest.sh` @ `a579ed8399a1d945ffd52ea797ac8e0a` **+ legs (c0)–(c6)** |
| 8 | `so3ar2_decomposeParDict` | `e6f1b0060944bc86d6dff56480ad2bd4` | byte-identical |
| 9 | `so3ar2_stop_marker.sh` | `f3c9b888a4498ff81470c4bfc07db106` | `so3ar_stop_marker.sh` @ `b25ac488f91c35d636b109b765abc339` |
| 10 | `so3ar2_xf_selftest.py` | `ea468e896a235ff33beaf6f943430f82` | `so3ar_xf_selftest.py` @ `fcf6f166ad13a9133a5fd101400769af` |
| 11 | `so3ar2_pin_census.py` | `d5cc562964bccd1b6341593cba090d6a` | `so3ar_pin_census.py` @ `2eb71f4f9af1277b577448b5c93e808b` **+ 11th source + 3 disposition rows** |
| 12 | **`so3ar2_collision_leg.py` — NEW, NO PARENT** | `20b48c9a4363b136b005558d68b0bfba` | the item's own repair (§1.2) |
| 13 | `so3ar2_derive_from_so3ar.sh` — the one-shot derivation | `b5aad89d8109a025def664f86eafa59b` | new |

**⚠ A DEPENDENCY THAT IS ON DISK AND NOT IN GIT, DISCLOSED HERE RATHER THAN DISCOVERED BY THE NEXT READER.** `reference/REAL_SO1a_MESH_checkMesh.log` and `reference/REAL_SO1a_X-S_arm.log` are **REQUIRED BY `so3ar2_grade.py --selftest`** and are **GITIGNORED** by the lab's own rule `.gitignore:270` (`cases/dafoam/**/*.log`), exactly as SO-3a's and SO-3aR's copies are. They are present on this box, copied by the derivation from `curriculum_SO3aR/reference/`. **A fresh checkout of this repository cannot run the comparator's selftest until those two logs are restored from the run roots they came from.** Nothing is worked around and no rule is bent.

**⚠ TWO INSTRUMENTS ARE NOT PINNED BY THE CHAIN DRIVER, AND THAT IS A STATED LIMIT, NOT AN OVERSIGHT.** `so3ar2_pin_census.py` and `so3ar2_collision_leg.py` are **ARMING PRECONDITIONS**: they run on the frozen tree before a container starts and **do not run at run time**, so nothing in the driver has occasion to hash them. Their bytes are fixed by the table above, frozen in the same commit. **Nothing detects an edit to them between this commit and arming except the supervisor's check 4 against the sha.**

**THE DERIVATION IS MECHANICAL AND REPRODUCIBLE, NOT DESCRIBED.** `so3ar2_derive_from_so3ar.sh` reads SO-3aR's frozen files (never writes them), applies four case- and hyphen-disjoint rename rules in a fixed order, and asserts **both directions**: sixteen citation classes counted on **both** sides and required **equal** — including the **grandparent** tokens `so3a_`, `CURRICULUM-SO3a-` and `SO-3a`-not-followed-by-`R`, counted separately because a bare `SO-3a` grep would also count `SO-3aR2` — and **not one** parent token may survive, because a half-fired rename leaves a file writing into the **parent's run root**, which holds a graded, closed record. **Measured: 11 files renamed, 2 reference logs copied, 16 of 16 citation classes intact (`SO-3a`-not-R at n = 22), 0 parent tokens surviving, rc = 0.**

**WHAT WAS DRIVEN, EACH WITH ITS READING** (all on the host, **zero solver compute, no container of any kind**):

| owed | discharged |
|---|---|
| the mechanical derivation, both assertions | **11 renamed, 16/16 citations intact, 0 parent tokens, rc = 0** |
| **`G-COLL` red-then-green** | `so3ar2_collision_leg.py` **rc = 0**, with **L2 and L3 both `collided: True`** carrying the literal `already exists, moving failed!`, L4 ok / L4b not-ok, L5 refusing |
| **`G-COLL` driven from outside, RED on the unfixed state** | `(c3)`: producer unfixed by ONE mutation → **rc = 1**, `L1 THE FIX DID NOT HOLD`; `(c4)`: one directory out of the staging loop → **rc = 1**; `(c2)`: mutated producer → **exit 2**; `(c3b)`/`(c6)` restores proved by hash |
| **`G-PINS`, GREEN on the frozen tree, re-driven against the new file set** | **26 pin-like constants enumerated BY ROLE across 11 sources** (SO-3aR's 23 across 10, plus the collision leg's three); **0 undisposed, 0 not-an-md5, 0 stale, 0 dead, 0 unpinned consumers, 0 table-vs-code drift, 0 stale rows; both planted-control limbs SEEN on all 11 sources; rc = 0.** **EVERY PRODUCER PIN IS NOT MERELY SET BUT CURRENT — A3 hashes the file each pin names and compares. SET IS NOT CORRECT, and A3 is the assertion that says so.** |
| the census proved able to fail, six directions, ONE mutation each | `(x15a)`–`(x15f)`: **6 of 6 RED**, each on the expected assertion code |
| the census's own reader proved not blind | `(p4)`: python extractor blinded → **exit 2, REFUSE**, nothing reported |
| the producer pin driven both ways with a hash-proved restore | `(p1)` set and equal; `(p2)` mutated producer → **exit 2** with the refusal token; `(p3)` restore **byte-identical**; `(p3b)` real producer **not** refused |
| comparator end to end, `python3` and `python3 -O` | `so3ar2_grade.py --selftest`: **97 units / 0 failures** in both modes |
| the instrument end to end, both modes | `so3ar2_xf_selftest.py`: **34 checks / 0 failures** in both modes |
| G-ROOT.1–.5 both directions incl. must-flag, and every leg above | `so3ar2_groot5_selftest.sh`: **92 legs, 0 fail** |
| rule-14 row-label sweep over every built instrument | `U100`: **11 files swept** (SO-3aR's ten **plus the collision leg, joining in the same commit that creates it**), **0 sites, 0 not yet built** |
| rule-2 re-checked with its own planted control | §11 below |
| §18.3 existence, in the form the clause asks for | §10 above, with two planted controls |

---

## 11. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED — WITH A PLANTED CONTROL

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient` DOES NOT EXIST at this commit.**

Checked at **2026-08-31T22:27:39Z** by **running the commands, not by recalling them**, with the reader shown able to see a non-zero **in the same invocation**:

| probe | reader | reading |
|---|---|---|
| target | `test -e` on the SO-3aR2 run root | **FALSE — absent** |
| **PLANTED CONTROL, same reader, same invocation** | `test -e` on `CURRICULUM-SO1a-a1-naca0012-dragmin-gradient` | **TRUE — present** |
| target | `find /home/ubuntu/certonomous-runs -maxdepth 2 -iname '*SO3aR2*'` | **0 hits** |
| **PLANTED CONTROL, same reader, same invocation** | `find … -iname '*SO3aR*'` | **5 hits** |

**Both readers are demonstrably able to report a non-zero and both report zero for SO-3aR2. The absence is real, not a blind reader.** The run root is **named, not globbed** — a glob is not an identifier, and SO-3a's own check once matched the feasibility rung `CURRICULUM-SO3aF` by glob. This item has burned **0 core-min of solver compute** and started **no container of any kind**. After the first arm container, gates are CLOSED and changes land only as dated addenda that cannot alter a gate, threshold, cap or label.

**SO-3a's and SO-3aR's run roots are DIFFERENT PATHS and are NOT touched, read-only or otherwise written, by this item.** The only thing this item reads out of a predecessor's case directory is `curriculum_SO3aR/so3ar_runScript.py`, **read-only**, as `G-COLL`'s limb L3 subject, and leg `(c6)` re-asserts its md5 unchanged after every leg has run.

---

## 12. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing about an **optimum** — no optimiser runs. **Nothing at np ≠ 1**: a gradient verified at one np is a statement about that np and is never carried to another (`DAFOAM_CHARTER.md` §5). **Nothing about Mach**, at all: `DASimpleFoam` has no equation of state and no speed of sound, and **no number from this item may be quoted as a compressibility result**. Nothing about α outside `[3.139°, 7.139°]`, and nothing about stall. Nothing about the four unregistered `shape` components or about `patchV`. Nothing about weights beyond the equal set registered. **No dot-product test and no complex step** — AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on **both** images, which is why `DAFOAM_CHARTER.md` §2's preference for a forward-AD or complex-step reference is **reached for and found unavailable here, and that is stated rather than left silent.** **No grid family, no GCI.**

**AND IT ESTABLISHES NOTHING ABOUT ANY OTHER ITEM'S PINS OR ANY OTHER ITEM'S RUN DIRECTORIES.** The census swept SO-3aR2's eleven sources and no others; the collision leg read SO-3aR2's producer and SO-3aR's, and no others. Whether SO-1aR, SO-1bR, SO-1cR, SO-2M, SO-2MR or any other multipoint item carries an unset pin or a shared run directory **IS NOT KNOWN AND IS NOT CLAIMED HERE.** That sweep is separate work for the supervisor to dispatch, and this document names it as **owed** rather than implying it done.

---

## 13. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

SO-3aR's P1–P9 and P-COST are carried **unchanged**: **P1** cells == 4032; **P2** baseline `CL` at α₀ in [0.45, 0.55]; **P3** `CD` monotone increasing across the three α; **P4** `G-MP-STRUCT` `PASS` on all 4 components; **P5** PATCHED row `G5J` `PASS`, 4 of 4 pairs inside band D, aggregate ≤ 1.0 %; **P6** SHIPPED row `G5J` `GATE FAIL` on at least one component; **P7** `G-TB` `PASS`; **P8** P-EVAL; **P9** the plateau holds per pair at the wing angles; **P-COST** total graded core-min in [14.0, 60.0]; **P-PIN** the by-role census exits 0 at arming time with every pin equal to the file it pins.

**P2 AND P3 ARE NOW PRE-CONFIRMED BY SO-3aR's OWN X-S ARM, AND THIS IS DISCLOSED RATHER THAN LEFT TO LOOK LIKE FORESIGHT.** SO-3aR's multipoint model — the same assembly, the same angles, the same weights — measured `CL(α₀) = 0.49876526` and `CD` monotone before it died. **They remain scored**, because SO-3aR2's model is not byte-identical to SO-3aR's: three `DASolver`s now run in three directories rather than one, and **a MISS on P2 or P3 would mean the isolation changed the primal answer, which is the cheapest and most important finding this item buys.**

**THREE NEW PREDICTIONS:**

| # | prediction | value | falsifier |
|---|---|---|---|
| **P-COLL** | the X-S arm reaches `compute_totals` for **all three** scenarios without a `renameSolution` collision, and the arm log carries **three** distinct `Moving time … to 0.0001` lines under three distinct directories | 3 renames, 0 collisions | **any** `already exists, moving failed!` in any arm log → the repair is **REFUTED**, the item is `NOT A RESULT`, and `G-COLL`'s green at freeze time was a statement about a model and not about the container. **This is the prediction the whole item is bought for.** |
| **P-IC0** | `n_changed_during_run > 0` on at least one point (DAFoam rewrites `0/` at `ranks = 1`, D19's mechanism), **and** the item's own η is **≤ 1e-8 relative** | η at D19's order, ~1e-10 absolute | η **orders larger than 1e-10** → **FINDING**, reported immediately, stated and not absorbed. `n_changed_during_run == 0` on every point is **also a scored MISS** and would mean D19's mechanism does not reach this configuration. |
| **P-PLAT2** | §6 | equal graded-pair counts one-sided and two-sided | §6; consequence is forward, never retroactive |

**THE REGISTERED OUTCOME, written before any container starts:** P1, P2, P3, P4, P5, P7, P9, P-COST, P-PIN, P-COLL and P-PLAT2 **HIT**; P6 **HIT**; P8 **HIT**; P-IC0 **HIT** → **SHIPPED row `GATE FAIL`, PATCHED row `PASS`, item `GATE FAIL`**, and the `2D · steady · incompressible` capability cell gains an FD-verified multipoint objective gradient it does not have. **A predicted `GATE FAIL` is REGISTERED, not avoided.**

---

## 14. FREEZE

**Committed BEFORE any container starts** (rule 2). **The grading path is fixed at this commit** as `cases/dafoam/ladder-a/A1/curriculum_SO3aR2/so3ar2_grade.py`, **md5 `c81a09a90950cb1610f40a91b29cdabe`**, and `so3ar2_chain_driver.sh:MD5_GRADER` asserts it before staging, aborting at `rc = 4` on any drift. **The document and the instruments freeze in ONE commit**, so no freeze sha is written into any instrument — a sha written at authoring time could only be wrong or back-dated, and the binding runs the other way: this document pins the code by md5, and the code pins this document's ceiling by grep (leg `(f3)`).

**Registered consequence, stated so it is not discovered later:** every md5 pin in `so3ar2_chain_driver.sh`, `so3ar2_run_arm.sh`, `so3ar2_xf.py` and `so3ar2_collision_leg.py` names the **FINAL** bytes of the file it pins. **Any further edit to any pinned file breaks the chain at `rc = 4` and requires a re-pinning addendum.** That is the intended cost of freezing.

**NOT ENQUEUED, NOT FILED, NOT ARMED.** The queue entry stays in this case directory and is validated **OUT OF PLACE, WITHOUT `--require-binding`**. **TEAM-BINDING IS `NOT CHECKED`** — an unchecked condition, never a passing one. **In-place validation happens in the drop directory where the runner takes the entry, so IN-PLACE VALIDATION IS ARMING, and arming is the supervisor's** (`SUPERVISION_CHARTER.md` §3 check 4), discharged on the sha and not on this sentence. **SUBMISSIONS PARKED** (`CLAUDE.md` rule 7).

**A `docs/COST_CALIBRATION.md` row is OWED AT COMPLETION** (`CLAUDE.md` rule 12): estimate 22.1 core-min against the actual from `ledger.txt`, the ratio, the attribution with contention and waste **named separately and never folded into the ratio**, and dollars **derived, not measured**.

**RULE FREEZE, 14 days from 2026-08-31.** This item introduces **no new procedural or bookkeeping rule and no new general-purpose tool.** `so3ar2_collision_leg.py` is ONE ITEM'S instrument, proving ONE ITEM'S repair, built once to the fail-closed + planted-control standard. **It speaks for no other item and is not offered as a lab-wide tool.**
