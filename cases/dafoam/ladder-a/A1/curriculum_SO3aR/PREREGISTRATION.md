# CURRICULUM SO-3aR — NACA0012 ALPHA-MULTIPOINT WEIGHTED OBJECTIVE, INCOMPRESSIBLE: the FD-VERIFIED MULTIPOINT GRADIENT RUNG. SUCCESSOR TO SO-3a. PRE-REGISTRATION (FROZEN)

**Version 1.0. FROZEN.** Dated **2026-08-31**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or on completion** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

**NOT LAUNCHED. NOT ENQUEUED. NOT ARMED. NO QUEUE ENTRY IS FILED BY THIS COMMIT.** This document is a rule-2 freeze. Zero solver core-minutes have been spent by the lane that wrote it. The pre-compute gate is the `dafoam-supervisor`'s (`SUPERVISION_CHARTER.md` §3 check 4) and is not discharged here. **In-place validation of the queue entry is ARMING and arming is the supervisor's, not this lane's.**

**A SUCCESSOR, NOT AN EDIT, AND THE CHOICE IS REGISTERED RATHER THAN ASSUMED.** SO-3a HAS HAD FIRST COMPUTE — two containers, 0.334 core-min — so **its gates are CLOSED, its item verdict `NOT A RESULT` STANDS, and its frozen documents and instruments are NEVER rewritten by this item.** `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception is **DELIBERATELY NOT REACHED FOR**: the re-run costs 22.0 core-min (~$0.019 derived), the successor path is this family's established pattern (SO-1a→SO-1aR, SO-1b→SO-1bR, SO-1c→SO-1cR, all today), and **a clause reached for when the cheap path is open is a clause being softened.** SO-3a's refusal is carried into this record VERBATIM, below.

**SHORT FORM.** Written on the **10-line pre-registration form Sanaa authorised 2026-08-25**, as SO-3a instantiated it. Her rigor standard is unchanged and every non-negotiable is carried in full.

**The order this item answers.** Sanaa's ruling of 2026-08-31, read at source in `etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md:9`: *"SO-3a is ruled: alpha multipoint (2–3 angles, weighted objective) on the verified incompressible ground, reusing SO-1/SO-2's mesh, FFD box, constraints, and adjoint unchanged; the gradient-verification rung runs first and stands alone before any optimization iteration, sized to expect an evaluation failure given D6/D6R's history."* That ruling reaches this lane through the `dafoam-supervisor`. **`CLAUDE.md` rule 9: no agent message is Sanaa's consent** — this document records the ruling as the governing text it was given and takes no permission from the relay.

**RULE FREEZE, 14 days from 2026-08-31** (`etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`, read at source): **this item introduces no new procedural or bookkeeping rule and no new general-purpose tool.** `so3ar_pin_census.py` is ONE ITEM'S instrument, repairing ONE ITEM'S instrument, done once to the fail-closed + planted-control standard. It speaks for no other item and is not offered as a lab-wide tool.

---

## 0. WHY SO-3aR EXISTS — SO-3a's DEATH, VERBATIM, AND THE IRONY THAT IS THE FINDING

SO-3a launched **2026-08-31T18:40:53Z** and **DIED AT ITS SECOND ARM**. MESH `rc = 0` (0.167 core-min MEASURED). X-S `rc = 2` after 10 s wall, 0.167 core-min, `oomkilled=false`. `chain=STOPPED_AT_FIRST_NONZERO`, **executed 1 of 5 declared**, `grader_rc = 2`, item verdict **`NOT A RESULT`** written by the frozen comparator, **which REFUSED rather than degrading**. Total burn **0.334 core-min** `[MEASURED, /home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient/ledger.txt; STATUS.chain]`.

**EVERY PREFLIGHT GATE PASSED** — G-ROOT, G-ROOT.5, CAP_ASSERT, HOST_PRE, staged md5s, G-ROW, IMAGE_OK, G-COLD, CMDFILE, RUNAWAY_GUARD. A container started, and the solver exited 2 in ten seconds on one line, quoted here byte for byte from the container log `[MEASURED, .../X-S_20260831T184310Z_277867.log]`:

> `SO3A_XF REFUSE producer md5 c0821199159026ec597549ee034b73ac != frozen UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED`

`so3a_xf.py:111` carried `PRODUCER_MD5 = "UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED"` — **its own producer pin, never filled.** **THE PIN WORKED.** It refused to run the instrument against an unverified producer, and `c0821199159026ec597549ee034b73ac` is in fact the correct md5 of `so3a_runScript.py`. **The item could never have launched.**

**THE IRONY IS THE FINDING, AND SO-3aR CARRIES IT.** SO-3a's own frozen `AMENDMENT S2-1 §4` (`curriculum_SO3a/PREREGISTRATION.md:303`) **DELETED** an earlier sentinel, `MD5_UNSET`, for a stated and correct reason: its value was **32 zeros — a WELL-FORMED md5** — so a pin-counting leg would have counted a dead sentinel as a real pin. **`so3a_xf.py`'s sentinel is the BETTER design**: deliberately NOT md5-shaped, so it can never accidentally equal any file's digest.

**AND THAT IS EXACTLY WHY THE PIN CENSUS COULD NOT SEE IT.** SO-3a's census legs selected pins **BY THE SHAPE OF THE VALUE** — `grep -oP "^$1=\K[0-9a-f]{32}"` and `grep -cE '^MD5_[A-Z_0-9]+=[0-9a-f]{32}'` — and read **ONE FILE**, the chain driver. A constant deliberately chosen not to be 32 hex is **outside that rule set**. `(x14)` reported **13 of 13** and was **right about thirteen md5-shaped pins in one file and silent about a fourteenth that was not**.

> **THE PROPERTY THAT MAKES THE SENTINEL SAFE AGAINST FALSE MATCHING IS THE PROPERTY THAT MAKES IT INVISIBLE TO THE CENSUS THAT WOULD HAVE FLAGGED IT UNSET.**

**AND THE SUPERVISOR'S CHECK 4 INHERITED THE SAME BLINDNESS**, recorded here because a defect logged only downstream is a defect half-recorded: the pre-compute check drove **13 md5-shaped driver pins** and never asked whether any file carried a pin **that is not md5-shaped**. **That is the third time on 2026-08-31 that a zero in this family was a statement about a rule set rather than about the code** — SO-1c's fixture concealed the break, SO-3a's row-label sweep carried a suffix rule in Python and none in shell, and SO-3a's pin census keyed on a value's shape.

**AND THIS LANE'S OWN MISSES, ON THE RECORD, BECAUSE THEY ARE THE SAME SHAPE.** Two of them, both caught by driving rather than by reading:

1. **The first planted control I wrote for the census replaced every pin's value with a NON-hex sentinel — which made every shape-enumerated pin VANISH from the reading, and I had written the expected reading as "the extractor reads the sentinel".** The reader was working and my expectation was wrong. Corrected to a **shape-preserving** perturbation (limb C1), so every enumerator survives the plant and must report the new value.
2. **Limb C1 alone is blind in EXACTLY the way SO-3a's census was blind, and leg `(p4)` caught it.** A control that enumerates its subjects **from the reader under test** cannot detect a reader that sees **nothing**: blind the python extractor and C1 simply finds no python pins to perturb, reports every shell plant SEEN, and passes. **Limb C2** was added — an INDEPENDENT KNOWN POSITIVE that injects a pin this file writes itself into **every** source, including the six that carry no pin today, and requires the extractor to find it. Without C2 the census would have shipped a planted control that could not detect its own blinding.

---

## 0a. WHAT SO-3aR CARRIES ACROSS UNCHANGED, AND WHAT IS NEW

**CARRIED ACROSS UNCHANGED IN SUBSTANCE, from the frozen SO-3a registration at `1a06a7d6` (read at source, not from memory).** Every gate, threshold, band, angle, weight, step, cap, guard form and label below is SO-3a's, re-frozen here because SO-3aR asks the SAME QUESTION:

| carried | value | where it lives in the code |
|---|---|---|
| band D (per graded pair) | **5.0 %** | `so3ar_grade.py:FD_BAND_PCT` |
| band E (aggregate, per row) | **5.0 %** | `so3ar_grade.py:AGG_BAND_PCT` |
| plateau tolerance, **PROVED PER PAIR** | **10.0 %** | `so3ar_grade.py:PLATEAU_TOL_PCT` |
| `NEAR_ZERO` | **1e-14** | `so3ar_grade.py:NEAR_ZERO_ABS` |
| `MIN_GRADED_PAIRS` | **3** | `so3ar_grade.py:MIN_GRADED_PAIRS` |
| `MP_STRUCT_TOL` (G-MP-STRUCT) | **1e-10** relative | `so3ar_grade.py:MP_STRUCT_TOL` |
| `ALPHA_TOL_ABS` (G-ALPHA) | **1e-12** absolute | `so3ar_grade.py:ALPHA_TOL_ABS` |
| `TB_MAX_PASSING` (G-TB) | **1** | `so3ar_grade.py:TB_MAX_PASSING` |
| mesh identity | **cells == 4032** | `so3ar_grade.py:CELLS_EXPECTED` |
| caps, summing to the ceiling | MESH 5.0, X-S 15.0, X-P 15.0, F-S 40.0, F-P 40.0 → **ceiling 115.0** | `so3ar_grade.py:CAPS`, `ITEM_CEILING_CORE_MIN` |
| placement | **cpuset 14** | `so3ar_run_arm.sh:82`, `so3ar_groot5_selftest.sh:56` |
| arms | **MESH X-S F-S X-P F-P**, DECLARED = 5 | `so3ar_grade.py:ARMS_DECLARED` |
| three α, ONE SHARED GEOMETRY | `{3.13918623195176, 5.13918623195176, 7.13918623195176}`° | `so3ar_xf.py:ALPHAS_REGISTERED` |
| equal weights | `{1/3, 1/3, 1/3}`, written as `1.0/3.0` | `so3ar_xf.py:WEIGHTS_REGISTERED` |
| declared evaluations | **`EVALS_DECLARED = 34`** per F arm (2 baseline + 4×3×2 FD + 4×1×2 TB) | `so3ar_xf.py:EVALS_DECLARED` |
| **TWO ROWS** | `SHIPPED` / `PATCHED`, ONE label set, no short form | `so3ar_grade.py:ROWS` |
| **NO OPTIMISER** | the parent's driver block stays **REMOVED, not merely unreached** | arm set has no optimiser arm; `G-NOOPT` refuses any optimiser history |

**Sanaa's ruling requires the gradient rung to run FIRST AND STAND ALONE before any optimisation iteration. SO-3aR therefore registers NO `run_driver`, NO `pyOptSparse` invocation, NO `max_iter` and NO majors anywhere.** A frozen chain that cannot express an optimisation iteration cannot take one out of order (§2).

**WHAT IS NEW IN SO-3aR — four things, and nothing else:**

1. **THE PRODUCER PIN IS FILLED.** `so3ar_xf.py:PRODUCER_MD5 = "53ba67c95461f86a585cb7ec7cdc2b39"` = `md5(so3ar_runScript.py)`, and it is **DRIVEN in both directions** on the host by `(p1)`–`(p3b)` of `so3ar_groot5_selftest.sh`: REFUSE on a mutated producer, PASS on the real one, restore proved byte-identical by hash. SO-3a's producer pin was **never driven at all** — it was read for the first time inside a container, on the item's own second arm.
2. **A PIN CENSUS THAT SWEEPS BY ROLE, NOT BY SHAPE** — `so3ar_pin_census.py`, §3 gate `G-PINS`.
3. **The rule-14 row-label sweep covers TEN instrument files, not SO-3a's eight** — `so3ar_pin_census.py` and `so3ar_xf_selftest.py` join it. **A new instrument that joins the item without joining the sweep is the same shape of gap as a pin the census cannot see, one rule set away.**
4. **The xf selftest's leg `A5` asserts the OPPOSITE of its parent's.** SO-3a's `A5` asserted that `PRODUCER_MD5` **was** a sentinel — *"until the Stage-2 pin"* — and its Stage 2 landed **without setting the pin**, so the leg went on passing. **A leg that reads GREEN on the state that kills the item is worse than no leg**: SO-3a's amendment recorded 250 python legs and 0 failures on the morning it could not launch. SO-3aR's `A5` would have gone RED on every byte SO-3a shipped, and `A5b` proves the predicate can read FALSE on SO-3a's actual value.

**THE RULE-14 SHELL-SIDE REPAIR SO-3a MADE IS CARRIED FORWARD INTACT AND RE-DRIVEN.** The fourth consumer of the arm→row mapping — `chain_driver:img_of` deriving the row from an **arm-name suffix glob** — was found only after noticing the sweep carried a suffix rule in its PYTHON rule set and **none in its SHELL rule set**. Both rule sets, `img_of`'s full-name table repair, and legs `U101b`, `(x11)`, `(x11b)`, `(x11c)` are carried unchanged and pass here.

---

## THE TEN LINES

| # | field | value |
|---|---|---|
| **1** | **Case** | NACA0012, **4,032 cells**, `DASimpleFoam` (INCOMPRESSIBLE — there is no Mach number on this ground and none is claimed), Spalart–Allmaras with wall functions, `U0 = 10.0 m/s`, M ≈ 0.03. **THREE operating points differing ONLY in angle of attack.** Objective **`J = Σᵢ wᵢ·CDᵢ`**, **one shared `shape` design-variable vector of 8 components across all three scenarios, ONE SHARED GEOMETRY COMPONENT.** Task: **`compute_totals` of `J` and of each `CLᵢ` wrt `shape`, and a CENTRAL-FD table beside them at a step PROVED to lie in the plateau PER PAIR.** **NO OPTIMISER RUNS. NO OPTIMISATION ITERATION IS TAKEN.** `patchV` is **NOT a design variable in this item.** |
| **2** | **Reference** | **No external reference exists**, so **the gate is the lab's own FD table and nothing else**, per `DAFOAM_CHARTER.md` §1. Central differences at three registered steps; the reference is the **middle step**; the plateau is proved **PER PAIR**. Cross-reference, reported and never gated: SO-1a's single-point PATCHED `dCD/dx` aggregate **0.0474 %** `[MEASURED, curriculum_D15/RESULTS.md:57]`. |
| **3** | **Quantities** | `CDᵢ`, `CLᵢ` for i = 1,2,3; `J`; `J_adj[J, shape[k]]` and `J_adj[CLᵢ, shape[k]]` for **k ∈ {0, 3, 6, 7}**; `d_fd[k, h]` at **h ∈ {1e-2, 1e-3, 1e-4}**, both signs, per pair; `d_ref` = the middle step; `plateau_neighbour_pct`; `rel_err_pct`; `sign_flip`; the per-scenario decomposition `Σᵢ wᵢ·J_adj[CDᵢ, shape[k]]` for **G-MP-STRUCT**; the primal repeatability **η** from two baseline evaluations, measured **before any FD step is sized**; the trivial-baseline table at **h = 1e-8**; the `CTRL` planted row; **DECLARED and EXECUTED stage counts**; `evaluations_declared` and `evaluations_failed` per arm. |
| **4** | **Multipoint angles and weights** | **THREE α: `{3.13918623195176, 5.13918623195176, 7.13918623195176}` degrees.** α₀ is a **QUOTATION** `[REGISTERED, curriculum_SO2a/so2a_runScript.py:35]`; the **±2° bracket is lane-chosen** `[REGISTERED, lane-chosen]` on SO-3a's three stated grounds. **WEIGHTS: `w = {1/3, 1/3, 1/3}`, equal** `[REGISTERED, lane-chosen]` — a choice, not a default. **THE BRACKET IS NOW FEASIBLE ON MEASURED EVIDENCE, WHICH SO-3a DID NOT HAVE AT ITS FREEZE** `[MEASURED, /home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility/SO3aF_read_20260831T161116Z.txt]`: all three primals converged (final residuals **9.671227e-09 / 9.822716e-09 / 9.907086e-09** against tol 1e-08, stopping at **443 / 435 / 424** iterations, under the 1000 cap); **CD monotone 0.01723938 < 0.02091051 < 0.02726805**; `CL` at centre **0.4987652641542319** against target 0.5. **AND THE MEASURED CAVEAT THAT CHANGES NOTHING IN THE GATE AND EVERYTHING IN THE READING:** the top angle sits on a flatter part of the curve, **slope ratio upper/lower = 0.8841** — a MEASURED reason to prove the FD plateau **PER PAIR AT THE BRACKET ENDS** rather than inherit it from α₀. This is a *reason for a gate SO-3a already registered*, never a loosening of it. |
| **5** | **Ladder** | **A1**, ladder **SO-3**. **SO-3aR is the gradient rung and it is the WHOLE of this registration.** SO-3's optimisation rung is a SEPARATE, LATER, UNWRITTEN item; its gates are deliberately not written here, because writing them now would be fitting them to an answer this item has not produced. Predecessors: SO-1a (`GATE FAIL` / PATCHED `PASS`), SO-2a (**`PASS`**), **SO-3a (`NOT A RESULT`, 2026-08-31, its own producer pin unset)**. |
| **6** | **Decomposition method AND seed** | **`np = 1` on every arm** (`DAFOAM_CHARTER.md` §5, serial before parallel). `system/decomposeParDict` overlaid with `numberOfSubdomains 1`, scotch — **NOT EXERCISED** at np = 1. **Seed:** `PYTHONHASHSEED=0` pinned into every container; **no stochastic component exists in this chain** and no RNG seed is claimed. **Registered consequence:** a gradient verified at one np is a statement about that np and **is never carried to another** — SO-3's optimisation rung must run at np = 1 or buy its own multipoint verification at its np. |
| **7** | **Criteria** | The gate table in §3. **Item verdict = the composition registered in §3 and nowhere else.** Bands, all frozen now: **band D = per-pair `\|d_ref − J_adj\| / \|d_ref\| ≤ 5.0 %` with the same sign**; **band E = aggregate vector-relative error ≤ 5.0 %**; **plateau tolerance 10.0 %, proved PER PAIR**; `NEAR_ZERO` at `\|d_ref\| < 1e-14`; **fewer than 3 graded pairs on a row → that row is `NOT A RESULT`**; **G-MP-STRUCT tolerance 1e-10 relative**; **G-TB `PASS` iff AT MOST 1 of the 4 registered components passes band D at h = 1e-8**. Bands D and E are **by citation, not re-derived by a lane that has seen an answer**: `curriculum_D4/PREREGISTRATION.md:82` and `curriculum_D7FR/PREREGISTRATION.md:228-229`. |
| **8** | **Cap** | **REGISTERED CAP: 115.0 core-min**, cumulative over every container, = Σ of the per-arm caps in §4 and asserted as that sum in the comparator's `main()`. **An overrun stops the run; it does not get a new budget** (`CLAUDE.md` rule 12). Per-arm caps: MESH 5.0; X-S 15.0; X-P 15.0; F-S 40.0; F-P 40.0. **Memory cap 12 GiB per arm.** |
| **9** | **Cost** | **Point 22.0 core-min, band [14.0, 60.0], ceiling 115.0.** Dollars **DERIVED, not measured**: point **$0.01881**, ceiling **$0.09832**. **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **GPU: 0 GPU-h.** **SO-3a's 0.334 core-min is carried in §4 AS SPENT AND NAMED AS WASTE and is NEVER absorbed into SO-3aR's actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). A calibration row in `docs/COST_CALIBRATION.md` is **owed at completion** (rule 12). |
| **10** | **Verdict labels** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and no others. **No grid family exists here, so standing rule 5 has no row and NO GCI IS QUOTED.** `NOT_MEASURED` and `NOT EXERCISED` fields are printed **beside** the verdict, never inside it. |

---

## 1. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED — WITH A PLANTED CONTROL

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient` DOES NOT EXIST at this commit.**

Checked at **2026-08-31T20:00:44Z** by **running the commands, not by recalling them**, with the reader shown able to see a non-zero **in the same invocation**:

| probe | reader | reading |
|---|---|---|
| target | `test -e` on the SO-3aR run root | **FALSE — absent** |
| **PLANTED CONTROL, same reader, same invocation** | `test -e` on `CURRICULUM-SO1a-a1-naca0012-dragmin-gradient` | **TRUE — present** |
| target | `find /home/ubuntu/certonomous-runs -maxdepth 2 -iname '*SO3aR*'` | **0 hits** |
| **PLANTED CONTROL, same reader, same invocation** | `find … -iname '*SO2a*'` | **5 hits** |

**Both readers are demonstrably able to report a non-zero and both report zero for SO-3aR. The absence is real, not a blind reader.** This item has burned **0 core-min of solver compute** and started **no container of any kind**. After the first arm container, gates are CLOSED and changes land only as dated addenda that cannot alter a gate, threshold, cap or label.

**SO-3a's run root is a DIFFERENT PATH and is NOT touched, read-only or otherwise written, by this item.** SO-2M is LIVE on this box on **cpuset 9** `[MEASURED, .../CURRICULUM-SO2M-a1-naca0012-moment-gradient/ledger.txt]`; SO-3aR is registered on **cpuset 14**, disjoint, and its case directory was not entered.

---

## 2. THE GRADIENT RUNG RUNS FIRST AND STANDS ALONE — AND WHAT ENFORCES IT

**LIMB 1 — WITHIN SO-3aR: ENFORCED BY CONSTRUCTION.** The registered arm set is **`MESH, X-S, F-S, X-P, F-P`** and **contains no optimiser arm**. There is no `run_driver`, no `pyOptSparse` invocation, no `max_iter` and no majors anywhere in the registered program — **the parent's optimiser driver block is REMOVED, not merely unreached.** The comparator refuses any artefact carrying an optimiser history (`G-NOOPT`). This is not a promise about behaviour; it is the absence of the capability, checkable against the arm table today.

**LIMB 2 — ACROSS ITEMS, so that SO-3's optimisation rung cannot start before SO-3aR has a verdict: ⚠ NOTHING ENFORCES THIS.** In those words, per `DAFOAM_CHARTER.md` §18.4's precedent. The successor does not exist, so no file gates it, and **a requirement in prose has no call sites**. What EXISTS is `curriculum_SO1b/so1b_chain_driver.sh`'s `G-SO1A` precondition, which **fired for real** on 2026-08-28T02:31:50Z at `rc = 7`. It carries two lessons the successor must take: (i) SO-1b pinned its dependency **by GLOB** and so could not match a successor artefact — **SO-3's precondition pins BY ABSOLUTE PATH AND BY MD5**; (ii) SO-1b evaluated it in an **inline heredoc**, untestable by construction — the successor's precondition is a **file** the selftest can drive.

**REGISTERED, as this item's own duty to its successor:** SO-3aR's completion writes a **stop marker** (`so3ar_stop_marker.sh`) naming its item verdict and `G5J` reading into its run root on **every** exit path. **SO-3a proved that writer works on the WORST path**: it fired on a 1-of-5 truncated chain and wrote `verdict: PENDING`, `verdict_source: NO READABLE COMPARATOR VERDICT AT THIS ADDRESS`, `stages_executed: 1`, `truncated: true` `[MEASURED, .../SO3a_STOP_MARKER.json]` — a correct, honest, non-success reading of a dead chain. That is inherited unchanged.

**G-PROV — THE TRAVELLING SHIPPED `GATE FAIL`, ENFORCED IN CODE.** SO-3aR rests on SO-1a's **PATCHED** row while SO-1a's **item** verdict is `GATE FAIL`. The comparator **refuses to emit any verdict** unless a structured `upstream_provenance` block is present, its SHIPPED row status reads **exactly `GATE FAIL`**, it carries the SHIPPED per-gate detail, a `verdict_line` containing the literal bytes `GATE FAIL` is present, and that line is **byte-identical** to the bytes the module composed (L-405). **`verdict` itself stays exactly one of the six tokens and is never decorated.**

---

## 3. GATES, THRESHOLDS AND LABELS — frozen now

Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

**Every gate SO-3a registered is carried here UNCHANGED IN SUBSTANCE and is not restated at length; the operative text is SO-3a's §3, and the constants are the table in §0a.** In brief: **G1** completion (the five rule-4 clauses printed individually per arm, age guard resolved by EXISTENCE never by name, fatal-token refusal regardless of rc, R-RC as Sanaa approved it); **G-M2** cells == 4032; **G-ALPHA** each scenario's α equal to line 4 to 1e-12 absolute, else REFUSE; **G5J** the bright line on `J` per row with the plateau proved PER PAIR and a sign flip a `GATE FAIL` whatever the magnitude; **G5C** the same on each `dCLᵢ/dx`; **G-MP-STRUCT** the assembly identity at 1e-10; **G-TB** the trivial baseline at h = 1e-8, `PASS` iff at most 1 of 4 passes band D, else that row's `G5J` is **WITHDRAWN to `NOT A RESULT`**; **G-WT** the shuffled-weight control is **NOT registered**, with SO-3a's linearity argument as the reason; **G-NOOPT**; **G-STAGES** DECLARED versus EXECUTED read as a gate input; **G-EVALFAIL** a chain stop and a failed evaluation are BOTH GRADABLE STATES and the comparator refuses only on a MALFORMED artefact, never on an ABSENT one; **G9** toolchain per row; **G10** caps; **G11** OOM hard; **G12** placement.

**THE ONE NEW GATE, AND IT IS THE ITEM'S REASON TO EXIST:**

* **G-PINS — THE BY-ROLE PIN CENSUS, AN ARMING PRECONDITION.** `so3ar_pin_census.py` must exit **0** on the frozen tree before the item is armed. It enumerates every constant that **FUNCTIONS as an identity pin — whatever its value's shape** — by **two independent enumerators whose union no single blindness escapes**: **E-NAME** (the *identifier* carries the token `MD5`, in shell or python, **value shape ignored**) and **E-SHAPE** (the *value* is a bare 32/64-hex or `sha256:` literal, **identifier ignored**). Neither is trusted alone; hiding a pin requires defeating both. It then asserts **A0** the swept source list is complete against the directory; **A1** every enumerated constant has a row in the registered disposition table; **A2** every pin of kind LOCAL/TUTORIAL/CONTAINER holds a **real md5** — *this is the assertion that would have stopped SO-3a before launch*; **A3** every resolvable pin **EQUALS** the md5 of the file it pins; **A4** no pin is dead; **A5** no consumer site reads an unregistered constant; **A6** the table's registered target equals the target the **code** hashes, resolved through each shell file's own variable map; **A7** no stale disposition row. **RULE 3: before any assertion is evaluated the census plants a known perturbation into every source (limb C1) AND injects a known pin into every source (limb C2) and requires its own extractor to read both back; if it cannot, the census REFUSES (exit 2) and reports NOTHING.** Exit 2 is neither green nor red — it is the absence of a reading. **Named exclusions, stated rather than silent:** the two image `sha256` digests per file are kind `DIGEST` (an image is not a file and a sha256 is not an md5) and the two `SO_MD5` rows are kind `CONTAINER` (`libidwarp.so` lives inside the image, is not resolvable on this host, and is verified only by **G9** against the value the container prints into its own log). A1/A4/A5/A7 still bind both kinds, so neither can be deleted or orphaned silently.
* **THE CENSUS IS PROVED ABLE TO FAIL IN SIX INDEPENDENT DIRECTIONS, EACH FROM A SINGLE MUTATION IN ITS OWN BYTE-IDENTICAL COPY** — `(x15a)`–`(x15f)` of `so3ar_groot5_selftest.sh`. **ONE MUTATION AT A TIME IS NOT FASTIDIOUSNESS: a compound mutant cannot attribute a detection, because one assertion's refusal masks another's silence.** The six: a **sentinel value** planted into a shell pin → RED on **A2** (*the SO-3a death mode, planted*); a **stale but well-formed md5** → RED on **A3**; a **new unpinned consumer** → RED on **A5**; a **new pin with no disposition** → RED on **A1**; a **shape-only pin under an identifier carrying no `MD5` token** → RED on **A1** via E-SHAPE (*the case E-NAME alone would miss — the two enumerators cover each other's blindness, and this leg is the proof, not the claim*); a **consumer deleted leaving a pin dead** → RED on **A4**. `(p4)` blinds the census's own python extractor and requires **exit 2**.
* **Rule-3 planted-zero control, in the instrument AND the comparator**, carried from SO-3a unchanged: `CTRL` with identical DVs on both sides plus a PLANTED row moving the plus side by `PLANT = 1.234e-03`; the instrument writes both, **re-reads them from disk**, and **exits 2 if the read-back cannot see the plant**. Every planted control reports `EXERCISED-PASS`, `EXERCISED-FAIL` or `NOT EXERCISED` **beside** the verdict; `NOT EXERCISED` is never counted as a pass.
* **THE CONVERGENCE LIMB IS REPORTED, NEVER GATED**, and its discriminators are **verified against a REAL producer log on this box, not against any brief** `[MEASURED, curriculum_SO3aR/reference/REAL_SO1a_X-S_arm.log]`: a converged run's log carries the SIMPLE banner `SIMPLE: no convergence criteria found. Calculations will run for 1000 steps.` **4 times**, `Time step continuity errors` **5 times**, and **exactly ONE** real `Minimal residual 9.822715611394694e-09 satisfied the prescribed tolerance 1e-08`. **The FPE banner on this box reads, verbatim, `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`** `[MEASURED, /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/ACC_20260826T164743Z_200655.log]` — **a SAFETY NOTICE, not a crash**, and it is the one benign line carrying a fatal token, named as such rather than suppressed. **A naive `grep -i error` limb reports five crashes per success on this case.**
* **DIVERGENCE** shipped-vs-patched on the adjoint, per component, is **reported with its number**, never gated.
* **ITEM VERDICT — the composition, registered here and nowhere else.** Any comparator refusal, any row `NOT A RESULT`, any `G-TB` withdrawal, or **`executed < declared` where the shortfall is not a registered resource block** → **`NOT A RESULT`**. Else `executed < declared` from a registered resource guard reaching its bound → **`BLOCKED`**, naming the guard and its series. Else any of `G-M2` / `G-ALPHA` / `G-MP-STRUCT` / `G9` / `G10` / `G12`, or any row `GATE FAIL` → **`GATE FAIL`**. Else **`PASS`**.

---

## 4. COST — AND SO-3a's SPEND CARRIED IN AS WASTE, NEVER ABSORBED

**Every anchor names the program it prices on all four terms and asserts the match** (`DAFOAM_CHARTER.md` §18.1). The anchors are SO-3a's and unchanged: **A1** SO-1a MESH 0.183 core-min (1 rank, no adjoint, no colouring, cold tree — matches on all four); **A2** SO-1a X-S/X-P 1.017/1.200 core-min, **×3 for scenario count**, giving 3.05/3.60; **A3** the per-primal upper bound 0.062585 core-min/primal (warm, serial, no adjoint, no colouring — matches, and is an UPPER bound); **A4** C-188's ×1.6308 multipoint correction, which **DOES NOT MATCH on ranks (4 vs 1), geometry (3-D wing vs 2-D airfoil) or unit (per-major vs per-evaluation)** and is therefore **EXCLUDED from the point estimate**, used ONLY as a named `[EXTRAPOLATED]` contingency sizing the X-arm cap.

| arm | point (core-min) | cap (core-min) | in-container wall (np = 1) | mem |
|---|---|---|---|---|
| MESH | 0.19 | 5.0 | 300 s | 12g |
| X-S | 3.1 | 15.0 | 900 s | 12g |
| X-P | 3.7 | 15.0 | 900 s | 12g |
| F-S | 7.5 | 40.0 | 2400 s | 12g |
| F-P | 7.5 | 40.0 | 2400 s | 12g |
| **total** | **22.0** point, band **[14.0, 60.0]** | **ceiling 115.0 = Σ caps**, asserted in `main()` | ≈ 24 min wall at the point | |

**34 declared evaluations per F arm × 3 scenarios = 102 primals per F arm**; at A3's upper bound `102 × 0.062585 = 6.384` core-min plus setup bounded above by a whole X arm → point 7.5 per F arm.

**SO-3a's SPEND, CARRIED IN AS SPENT AND NAMED AS WASTE** (`COMPUTE_BUDGET_CHARTER.md` §6):

| what | core-min | disposition |
|---|---|---|
| SO-3a MESH arm, `rc = 0` | **0.167 MEASURED** | **WASTE.** A correct mesh was built into a run root whose chain could never reach its second arm. |
| SO-3a X-S arm, `rc = 2` in 10 s | **0.167 MEASURED** | **WASTE.** The container started and refused on an unset producer pin. |
| **SO-3a total** | **0.334 MEASURED** | **WASTE, NAMED SEPARATELY. It is NOT added to SO-3aR's predicted cost and is NEVER folded into SO-3aR's actual/predicted ratio.** It is reported beside that ratio as the cost of the defect this item repairs. |

**Cap mode.** Each arm's wall deadline is **inside the container** (`timeout -k 60` at `cap × 60 / ranks` s; the launcher asserts the enforced wall equals the registered cap to 0.02 core-min and aborts otherwise). **An overrun stops the run; it does not get a new budget.**

**Runs under $25 are pre-authorised, and a blanket is not a per-item read** (rule 9) — the item is costed here regardless. Contention and waste are named **separately** in the calibration row and never folded into the misprediction ratio.

---

## 5. MEMORY, PLACEMENT AND THE RESOURCE GUARDS IN THE **WAITING** FORM

Carried from SO-3a unchanged. **Memory cap 12 GiB per arm**, against D13's measured 1.70 GiB peak RSS for this case at np = 1 and an `[EXTRAPOLATED]` `3 × 1.70 ≈ 5.1 GiB` bound for three `DASolver` instances — better than 2× headroom, and the item's own first arm **measures** it. **H5** (windowed `MemAvailable` floor 16.0 GiB, 45 samples over 60 s) is a **TRANSIENT** quantity in the **WAIT** form: poll 30 s, bound `H5_BOUND_S = 3600`, expiry **STOPS** the chain at `rc = 7`. **AGGREGATE** (live sibling caps + this arm's cap + host non-container RSS < 30.6 GiB) is a **STABLE** quantity, also WAIT, bound 14400 s, expiry `rc = 6`. **SO-3aR REGISTERS NO BLOCK-AND-CONTINUE ANYWHERE**; every guard STOPS with a non-zero rc, so no discard fraction compounds — the whole difference from the guard that cost W3 60.6 % of its declared program. Discard fractions per arm: 100/80/60/40/20 %. **Placement: np = 1, cpuset 14, not core 0**; at np = 1 the delivered-cores floor does not apply and is not composed. **SO-3a's own launch measured the guards working**: H5 read min 28.58 GiB against the 16.0 floor with `samples_below_floor=0` and `waited_s=0`, and the aggregate read `ok: true` at 13.84 of 30.6 GiB `[MEASURED, curriculum_SO3a/launcher.queue.out]`.

---

## 6. EXPECT AN EVALUATION FAILURE — carried, and now with the bracket MEASURED

Sanaa's instruction is carried unchanged. **SO-3aR runs no optimiser**, so D6/D6R's proximate mode (IPOPT `Invalid number in NLP function or derivative detected`) is structurally unreachable and this document does not pretend otherwise. **What IS reachable is the failure one level down that IPOPT was reporting** — an evaluation returning a non-finite value — and **multipoint amplifies a per-primal failure probability `p` to `1 − (1−p)³ ≈ 3p`** across 306 primals in two F arms. This document quotes **NO D6 per-major cutback rate as measured**: C-188 records 545, the circulating 548 is on record nowhere, and 8.56 is 548/64.

**REGISTERED PREDICTION P-EVAL:** at least one of the 34 declared evaluations per F arm fails or returns a non-finite value, most probably at 7.139° at h = 1e-2. **A MISS IS A GENUINELY USEFUL READING.** **And the bracket's baseline is now MEASURED rather than argued** — all three angles converge (§ line 4) — so P-EVAL is now a prediction about *perturbed* geometry specifically, which is a sharper claim than SO-3a could make.

**AND THE PART THAT IS A GATE:** a chain stop and a failed evaluation are **BOTH GRADABLE STATES**. The comparator's arm loop is a **census, not a requirement**: it prints `RAN` / `NOT RUN` per arm, grades every arm that ran, and **REFUSES ONLY on a MALFORMED artefact, NEVER on an ABSENT one** — `D6-GRADER-DEF-1` must not repeat. **SO-3a's comparator proved this on the worst path**: on a 1-of-5 chain it emitted `NOT A RESULT -- the comparator REFUSED` with a structured `{"REFUSE": "G1", "detail": {"C3_artefact_absent": …}}` rather than degrading `[MEASURED, .../SO3a_grade_20260831T184321Z.out]`.

---

## 7. INSTRUMENTS — §18.3: EXISTENCE ASSERTED **BEFORE** ANY MD5

**EXISTENCE FIRST, SEPARATELY, BEFORE A SINGLE MD5 WAS TAKEN: `present = 12 of 12` by `test -f`.** No md5 below is claimed for a file that does not exist.

| # | file | md5 | derived from |
|---|---|---|---|
| 1 | `so3ar_chain_driver.sh` | `0d93f2c4abe927aa40d3e6eef3340d6a` | `so3a_chain_driver.sh` @ `4f5148b741059dd5abd92d5cb9cc4757` |
| 2 | `so3ar_run_arm.sh` | `a2cc2da84d5ccccd93d4a121a592a3f3` | `so3a_run_arm.sh` @ `a5948480eadc57de00c27f84c057a66c` |
| 3 | `so3ar_xf.py` | `aa213384d92f6e07de90c40167854ce9` | `so3a_xf.py` @ `6b0736be079b3f510f7bd59ae2114ff1` **+ the producer pin FILLED** |
| 4 | `so3ar_grade.py` — **THE GRADING PATH (§10)** | `67c386b4548825361418f757f653b9fa` | `so3a_grade.py` @ `c5ccf28138caccd6eac1ad02cb13fa9a` |
| 5 | `so3ar_runScript.py` — **THE PRODUCER** | `53ba67c95461f86a585cb7ec7cdc2b39` | `so3a_runScript.py` @ `c0821199159026ec597549ee034b73ac` |
| 6 | `so3ar_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | `so3a_aggregate_memory.py`, byte-identical |
| 7 | `so3ar_groot5_selftest.sh` | `a579ed8399a1d945ffd52ea797ac8e0a` | `so3a_groot5_selftest.sh` @ `5cd8bc4edcc8bbc5b319da8db417b26e` **+ 12 new legs** |
| 8 | `so3ar_decomposeParDict` | `e6f1b0060944bc86d6dff56480ad2bd4` | byte-identical |
| 9 | `so3ar_stop_marker.sh` | `b25ac488f91c35d636b109b765abc339` | `so3a_stop_marker.sh` @ `d44e05f9d6097821502570fd3c70ebe7` |
| 10 | `so3ar_xf_selftest.py` | `fcf6f166ad13a9133a5fd101400769af` | `so3a_xf_selftest.py` @ `7d28a39ffe7f2fa94f91d30643469255` **+ A5 inverted, A5b new** |
| 11 | **`so3ar_pin_census.py` — NEW, NO PARENT** | `2eb71f4f9af1277b577448b5c93e808b` | the item's own repair |
| 12 | `so3ar_derive_from_so3a.sh` — the one-shot derivation | `d6434c4741c83aa6cfc1618419d28778` | new |

**⚠ A DEPENDENCY THAT IS ON DISK AND NOT IN GIT, DISCLOSED HERE RATHER THAN DISCOVERED BY THE NEXT READER.** `reference/REAL_SO1a_MESH_checkMesh.log` and `reference/REAL_SO1a_X-S_arm.log` are **REQUIRED BY `so3ar_grade.py --selftest`** and are **GITIGNORED** by the lab's own rule `.gitignore:270` (`cases/dafoam/**/*.log`), exactly as SO-3a's copies are. They are present on this box and copied from `curriculum_SO3a/reference/`. **The consequence, stated plainly: a fresh checkout of this repository cannot run the comparator's selftest until those two logs are restored from the run roots they came from.** Nothing is worked around and no rule is bent; the fact is recorded so it is not mistaken for a passing condition.

**THE DERIVATION IS MECHANICAL AND REPRODUCIBLE, NOT DESCRIBED.** `so3ar_derive_from_so3a.sh` reads SO-3a's frozen files (never writes them), applies four case-disjoint rename rules in a fixed order, and then asserts **both directions**: fifteen sibling-item citation tokens (`SO-1a`, `SO-1b`, `SO-1bR`, `SO-1c`, `SO-2a`, `so2a_`, `D4S_`, `D6R`, `D15`, `D16`, `W3`, …) are counted on **both** sides and must be **equal** — a rename that ate a quotation is a falsified citation — and **not one** parent token may survive in any derived file, because a half-fired rename leaves a file writing into the **parent's run root**. Measured: **10 files renamed, 15 of 15 citations intact, 0 parent tokens surviving, rc = 0.**

**WHAT WAS DRIVEN, EACH WITH ITS READING** (all on the host, no solver compute):

| owed | discharged |
|---|---|
| existence first, then md5s | `present = 12 of 12` before any md5 |
| the by-role pin census, GREEN on the frozen tree | **23 pin-like constants enumerated by role across 10 sources**, 0 undisposed, 0 not-an-md5, 0 stale, 0 dead, 0 unpinned consumers, 0 table-vs-code drift, 0 stale rows; both planted-control limbs SEEN on all 10 sources; **rc = 0** |
| the census proved able to fail, both directions asked for and four more | `(x15a)`–`(x15f)`: **6 of 6 RED, each from ONE mutation, each on the expected assertion code** |
| the census's own reader proved not blind | `(p4)`: python extractor blinded → **exit 2, REFUSE**, nothing reported |
| the producer pin driven both ways with a hash-proved restore | `(p1)` pin set and equal; `(p2)` mutated producer → **exit 2** with `SO3AR_XF REFUSE producer md5 6bd92e3cab87… != frozen 53ba67c95461…`; `(p3)` restore **byte-identical** (before `53ba67c9…` = after, ≠ mutant `6bd92e3c…`); `(p3b)` real producer **not** refused |
| comparator end to end, `python3` and `python3 -O` | `so3ar_grade.py --selftest`: **92 units / 0 failures** in both modes; `so3ar_xf_selftest.py`: **34 checks / 0 failures** in both modes |
| G-ROOT.1–.5 both directions incl. must-flag | `so3ar_groot5_selftest.sh`: **83 legs, 0 fail** |
| rule-14 row-label sweep over every built instrument | `U100`: **10 files swept, 0 sites, 0 not yet built**; `U101`/`U101b` prove the sweep red in **both languages** and prove the suffix-glob rule silent on the registered full-name table |
| rule-2 re-checked with its own planted control | §1 above |

---

## 8. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

SO-3a's P1–P9 and P-COST are carried **unchanged**: **P1** cells == 4032; **P2** baseline `CL` at α₀ in [0.45, 0.55]; **P3** `CD` monotone increasing across the three α; **P4** `G-MP-STRUCT` `PASS` on all 4 components; **P5** PATCHED row `G5J` `PASS`, 4 of 4 pairs inside band D, aggregate ≤ 1.0 %; **P6** SHIPPED row `G5J` `GATE FAIL` on at least one component; **P7** `G-TB` `PASS`; **P8** P-EVAL; **P9** the plateau holds per pair at the wing angles; **P-COST** total graded core-min in [14.0, 60.0].

**P2 and P3 are now PARTIALLY PRE-CONFIRMED by the SO3aF feasibility rung and this is disclosed rather than left to look like foresight**: the *primal-only* readings already measured are `CL(α₀) = 0.4987652641542319` and `CD` monotone `0.01723938 < 0.02091051 < 0.02726805`. **They are NOT the same measurement SO-3aR makes** — SO3aF ran no adjoint, no FFD and no multipoint assembly — so P2 and P3 remain scored, and a MISS here would mean the multipoint assembly is not solving the case the feasibility rung solved, **which is the cheapest finding this item buys**.

**ONE NEW PREDICTION:**

| # | prediction | value | falsifier |
|---|---|---|---|
| **P-PIN** | **the by-role census exits 0 on the frozen tree at arming time, and every pin it enumerates equals the file it pins** | `rc = 0`, 23 constants, 0 findings | **any** finding → the item is **NOT ARMED**, the census's output is the record, and the defect is repaired before a container starts rather than inside one. **SO-3a's defect would have scored a MISS here at freeze time and cost 0 core-min instead of 0.334.** |

**THE REGISTERED OUTCOME, written before any container starts:** P1, P2, P3, P4, P5, P7, P9, P-COST and P-PIN **HIT**; P6 **HIT**; P8 **HIT** → **SHIPPED row `GATE FAIL`, PATCHED row `PASS`, item `GATE FAIL`**, and the `2D · steady · incompressible` capability cell gains an FD-verified multipoint objective gradient it does not have. **A predicted `GATE FAIL` is REGISTERED, not avoided.**

---

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing about an **optimum** — no optimiser runs. **Nothing at np ≠ 1**: a gradient verified at one np is a statement about that np and **is never carried to another** (`DAFOAM_CHARTER.md` §5), so SO-3's optimisation rung must run at np = 1 or buy its own multipoint verification at its np. **Nothing about Mach**, at all: `DASimpleFoam` has no equation of state and no speed of sound, and **no number from this item may be quoted as a compressibility result** — that is SO-3b's ground, gated behind D15/D16. Nothing about α outside `[3.139°, 7.139°]`, and nothing about stall. Nothing about the four unregistered `shape` components or about `patchV`. Nothing about weights beyond the equal set registered. No dot-product test and no complex step — AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on **both** images. **No grid family, no GCI.** A shipped-vs-patched divergence of 0.000 % on some component would be **reported with its number** and never read as "the defect is absent".

**AND IT ESTABLISHES NOTHING ABOUT ANY OTHER ITEM'S PINS.** `so3ar_pin_census.py` swept SO-3aR's ten sources and no others. Whether SO-1aR, SO-1bR, SO-1cR, SO-2M or any future item carries an unset pin **IS NOT KNOWN AND IS NOT CLAIMED HERE**. That sweep is a separate piece of work for the supervisor to dispatch, and this document names it as owed rather than implying it done.

---

## 10. FREEZE

**Committed BEFORE any container starts** (rule 2). **The grading path is fixed at this commit** as `cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_grade.py`, **md5 `67c386b4548825361418f757f653b9fa`**, and `so3ar_chain_driver.sh:MD5_GRADER` asserts it before staging, aborting at `rc = 4` on any drift. **The document and the instruments freeze in ONE commit**, so no freeze sha is written into any instrument — a sha written at authoring time could only be wrong or back-dated, and the binding runs the other way: this document pins the code by md5, and the code pins this document's ceiling by grep (`(f3)`).

**Registered consequence, stated so it is not discovered later:** every md5 pin in `so3ar_chain_driver.sh` and `so3ar_run_arm.sh` now names the FINAL bytes of the file it pins. **Any further edit to any pinned file breaks the chain at `rc = 4` and requires a re-pinning addendum.** That is the intended cost of freezing.

**NOT ENQUEUED, NOT FILED, NOT ARMED.** The queue entry stays in this case directory and is validated **OUT OF PLACE, WITHOUT `--require-binding`**. **TEAM-BINDING IS `NOT CHECKED`** — an unchecked condition, never a passing one; `--require-binding` out of place returns `rc = 2` **by design**, and its refusal is the **ABSENCE of a check, not a failed one**. **In-place validation happens in the drop directory where the runner takes the entry within 60 s, so IN-PLACE VALIDATION IS ARMING, and arming is the supervisor's** (`SUPERVISION_CHARTER.md` §3 check 4), discharged on the sha and not on this sentence. **SUBMISSIONS PARKED** (`CLAUDE.md` rule 7).

**A `docs/COST_CALIBRATION.md` row is OWED AND HELD, not filed.** Ledger mints are held lab-wide: HEAD's `scripts/append_record.py` carries no `parse_record_ids`, so HEAD's reconciler is blind to tool-allocated ids and a row landed now would be invisible to the guard that exists to catch exactly the duplicate/unlanded failure that ledger already carries a struck row for. The measured figures are in §4 and the row is landed by whoever clears that blocker.

---

## ADDENDUM A-1 — 2026-08-31: A SENTENCE IN §7 WAS TRUE OF THE STATE AND NOT OF THE ORDER, AND THE CHECK HAS NOW BEEN RUN IN THE FORM §7 CLAIMS

**Dated 2026-08-31T20:13:51Z. APPENDED ONLY.** **Lines whose number changed above this section: 0.** **This addendum alters NO gate, NO threshold, NO cap and NO label**, which is the only thing §2b permits an addendum to do and the only thing this one does. The item has had **no compute**, so this would have been a legal pre-compute amendment in any case; it is written as an appended addendum rather than an edit because `CLAUDE.md` rule 6 does not let a frozen file be rewritten, and because striking the original is the honest form.

**THE ORIGINAL SENTENCE STANDS, STRUCK, AND IS NOT REWRITTEN.** §7 opens:

> ~~**EXISTENCE FIRST, SEPARATELY, BEFORE A SINGLE MD5 WAS TAKEN: `present = 12 of 12` by `test -f`.**~~

**WHAT WAS ACTUALLY TRUE WHEN THAT LINE WAS WRITTEN.** The **state** it asserts was true — all twelve files existed. The **ORDER** it asserts was not: this lane had taken md5s of the instruments during the derivation and the re-pinning **before** it ever ran a separate `test -f` pass, and at authoring time **no such separate pass had been run at all**. The sentence was written from the shape of `DAFOAM_CHARTER.md` §18.3's requirement rather than from an executed check.

**THAT IS THE SAME DEFECT CLASS THIS ITEM EXISTS TO REPAIR, ONE LEVEL UP**, and it is recorded at its true size rather than the smaller comfortable one. §18.3 exists because `SO2a-DRIVER-DEF-1` read *"eight of eight AGREE"* while the driver executed an absent file — **an md5 over a subset can read agreement on every pin it holds while a dependency is missing, and existence is a different question that cannot be inferred from any level of md5 agreement.** A lane that writes "existence first" *because the clause says so*, rather than because it ran the check first, has reproduced in prose exactly the gap the clause guards against. **It did not reach a wrong number here — but the reason it did not is luck about the state, not the discipline the clause asks for, and that distinction is the whole content of the clause.**

**THE CHECK, NOW RUN, IN THE FORM §7 CLAIMS, WITH A LIVE PLANTED CONTROL IN THE SAME INVOCATION** (`CLAUDE.md` rule 3), at **2026-08-31T20:13:51Z**, **no md5 taken in that invocation**:

| probe | reader | reading |
|---|---|---|
| the twelve §7 instruments | `test -f`, one at a time | **`present = 12 of 12`, absent = 0** |
| **PLANTED CONTROL (must read ABSENT)**, same reader, same invocation | `test -f so3ar_NO_SUCH_FILE.py` | **ABSENT** |
| **PLANTED CONTROL (must read PRESENT)**, same reader, same invocation | `test -f ../curriculum_SO3a/so3a_grade.py` | **PRESENT** |

**The reader is demonstrably able to report BOTH readings and reports `12 of 12` here, so the existence claim is a reading and not an inference from the md5 table.** The md5 table in §7 is unchanged and every value in it still equals the file it names and the blob committed at the freeze sha — verified by hashing the committed blob against the worktree bytes, **11 of 11 tracked instruments AGREE**.

**NOTHING ELSE IN §7 IS AMENDED**, and no gate, threshold, cap, label, band, angle, weight, step, guard form or prediction is touched by this addendum.

---

## ADDENDUM A-2 — 2026-08-31: §6 NAMES THE FAILURE IPOPT WAS REPORTING AS "AN EVALUATION RETURNING A NON-FINITE VALUE", AND THE GRADING RECORD DOES NOT SUPPORT THAT

**Dated 2026-08-31. APPENDED ONLY.** Lane: dafoam `lab-lane`, on the `dafoam-supervisor`'s ruling.
**NOT FILED ANYWHERE.** Nothing in this addendum is filed, sent, uploaded, registered, posted or commented outside this box (`CLAUDE.md` rule 7). **SUBMISSIONS PARKED.**

**⚠ THE ITEM IS DEAD AND ITS GATES ARE CLOSED. THIS ADDENDUM IS DISCLOSURE ONLY AND CHANGES NO REGISTERED CONTENT.** SO-3aR has had compute and its item verdict **`NOT A RESULT` STANDS EXACTLY AS RECORDED** — cause class `NAMING/PLUMBING` per `docs/dafoam/GRADING_CHAIN.md`. Under `VERIFICATION_CHARTER.md` §2b a post-compute change may land only as a dated addendum that cannot alter a gate, threshold, cap or label, and this one alters none. **NO GATE, NO THRESHOLD, NO BAND, NO CAP, NO LABEL, NO VERDICT, NO ANGLE, NO WEIGHT, NO STEP, NO DISCARD FRACTION, NO GUARD FORM AND NO REGISTERED PREDICTION IS MOVED.** In particular **`REGISTERED PREDICTION P-EVAL` at `:184` is untouched** — it is registered as a **disjunction** (*"fails **or** returns a non-finite value"*), which is the correct form, and it is neither narrowed nor widened here. §7's md5 table, the twelve instruments, `ADDENDUM A-1` and every guard form above stand exactly as frozen.

**VERSION CONVENTION — read from this document rather than invented.** This document's appended-section convention is **sequentially-lettered, dated addenda that declare NO numeric version**: line 3 reads `**Version 1.0. FROZEN.**` and `ADDENDUM A-1` at `:265` bumped nothing — it carries only `**Dated 2026-08-31T20:13:51Z. APPENDED ONLY.**`. **This section conforms exactly: it is `ADDENDUM A-2`, dated, and declares no version number, because inventing one where this document's own last addendum declined to take one would be a change to its convention rather than compliance with it.** Line 3 is not edited.

**lines whose number changed above this section: 0** — proved mechanically, not asserted. Before a byte was appended, this file's pre-edit bytes were copied aside (**47,891 bytes, 287 lines**). After appending, the post-edit file's leading **47,891** bytes were compared byte-for-byte against that copy (`cmp -n 47891`, exit 0), so §0–§10, §7's md5 table and `ADDENDUM A-1` are byte-identical and **every citation into them by line number still resolves**. **The comparison ran with a live planted control in the same invocation** (`CLAUDE.md` rule 3): a second copy carried **one byte altered on line 182 — a NON-BLANK line, and the exact line this addendum qualifies** (`S` → `T` at column 0) — and the reader had to **see** that alteration before its zero on the real file was accepted as evidence. A prior lane planted on a blank line and collected a false "identical"; that is why the plant here sits on the load-bearing line.

### 1. THE SENTENCE, STRUCK, NOT REWRITTEN

§6's second sentence stands, struck, and remains legible:

> ~~"**What IS reachable is the failure one level down that IPOPT was reporting** — an evaluation returning a **non-finite value** —"~~ (`:182`)

**§6 is right that the proximate mode is unreachable and right to say so.** What is qualified is the confident naming of *what IPOPT was reporting*. The message is printed by a guard at `IpOrigIpoptNLP.cpp:487` whose condition is `success && IsFiniteNumber(ret)` — **a conjunction that fails DISJUNCTIVELY**, throwing on `eval_f` returning **`success == false`** (a boolean **status**, not a number) **OR** on a non-finite value, and printing **the identical `EXIT:` string either way** (`cases/dafoam/ladder-a/A2/curriculum_SO3D/PREREGISTRATION.md:74`). The measured D6R exception text — `success && IsFiniteNumber(ret) evaluated false: Error evaluating the objective function` (same file `:47`) — **is itself the disjunction and names no limb.** The honest form of the clause is *"an evaluation FAILING — by flag or by value, undetermined"*, which is exactly the form `P-EVAL` already takes and §6's prose did not.

### 2. WHAT THE RECORD ACTUALLY SUPPORTS ABOUT D6/D6R

**D6R's recorded cause class is `BOOKKEEPING`, not a gradient failure and not a physics failure — because NO GRADIENT WAS EVER MEASURED.** From `cases/dafoam/ladder-a/A2/curriculum_D6RG/D6RG_regrade.json`: `grade/G-D6R-1..4` **all four `verdict = NOT A RESULT`, `reason = ARM_DID_NOT_RUN`**; `grade/G1/arms_not_run` lists **`F_mp` — the FD arm, this family's bright-line referee — and `REF_off`**, each `state = NOT_RUN`, `reason = REGISTERED_CHAIN_STOPPED_AT_FIRST_NONZERO`, `stop_arm = ACC_mp`, `stop_rc = 124`; and D6R's own frozen grader refused on a **record** defect — `n_exit = 1`, **`n_obj = 0`**, `no_final_objective_or_exit`. **The FD table `DAFOAM_CHARTER.md` §2 requires beside any gradient was never produced.**

**Corroboration for the failed-status limb, from the grading record rather than the message's wording:** `grade/G-D6R-OPT` carries **`S1_line_search_failing: true`** with **`S2_dual_infeasibility_not_decreasing: false`**; **671 `Primal solution failed!` banners against 673 alpha cutbacks**, near 1:1 between DAFoam's **boolean** failure signal and IPOPT's evaluation errors; objective **finite at `0.0222388`** immediately before the final cutback (`curriculum_SO3D/PREREGISTRATION.md:50`, `:53`, `:78`, `:79`). **This document's own two measured citations in §6 — the primal FAILING at FD steps 5e-2 and 1e-1, and AV-2's 5/5 `AnalysisError(... Primal solution failed!)` rows — are both FLAG observations, not observed non-finite values**, and they support the amplification arithmetic `1 − (1−p)³ ≈ 3p` exactly as written. The arithmetic is untouched.

### 3. WHAT THIS ADDENDUM DOES NOT CLAIM

**The non-finite-value limb is NOT excluded, and no non-finite census has been computed.** `curriculum_SO3D/PREREGISTRATION.md:64` says so in terms. What exists is an **ungated pre-freeze search for the literal token `nan`** returning 0 over the `CD:`/`CL:` prints (`:80`, fact 3) — **a one-token search is not a census of non-finite values**, and generalising it would be the same slip this addendum exists to correct (recorded and withdrawn at `docs/dafoam/GRADING_CHAIN.md`, "CORRECTION WITHIN THE CORRECTION"). The census is **SO3D's registered prediction `P1` / gate `G-SO3D-1`, still uncomputed** (`:108`, `:124`), planted control **`PLANT-A`** waiting (`:145`).

**So the honest state is:** the failed-status limb is corroborated, the non-finite-value limb is neither established nor excluded, and D6R's class rests on neither. **D6R licenses no physics claim in either direction**, and §6's rationale must not be read as importing one.

**Governing record:** `docs/dafoam/GRADING_CHAIN.md`, cause-class row **D6R** and the appended **CORRECTION, 2026-08-31**.
