# `MP_A5R` — SUCCESSOR TO `MP_A5`. THE SAME 3D INCOMPRESSIBLE MULTIPOINT OPTIMISATION, GRADED AGAINST A TREE THAT MATCHES ITS OWN FLOOR

**Drafted 2026-09-12 by a `lab-lane` on the dafoam-supervisor's ruling that a fail is *fixed, not
closed*. Still under Sanaa's directive, her words verbatim: _"dafoam should notforget about the
multipoint optimization (both compressible and incompressible)"_.**

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed or uploaded anywhere.

**THIS LANE HAS RUN NO COMPUTE AGAINST THIS ITEM, AND THIS ITEM IS NOT LAUNCHED.** No run root
matching `/home/ubuntu/certonomous-runs/CURRICULUM-MP_A5R-a5-ubend-multipoint*` exists, verified by
`ls` at 2026-09-12 06:35:59 UTC (`No such file or directory`), and no `mpa5r_out.json` exists anywhere
on this box. **The launch is withheld pending the dafoam-supervisor's check-4 read of this freeze.**

**THE GRADING PATH IS IN THIS COMMIT**, committed together with this file. At the freeze:

| file | md5 at freeze |
|---|---|
| `cases/dafoam/ladder-a/A5/curriculum_MP_A5R/mpa5r_grade.py` | `895f2146ab203e41b2767aa9a3ed248a` |
| `cases/dafoam/ladder-a/A5/curriculum_MP_A5R/mpa5r_run_script.py` | `37e31d71c9216249cee926ed12fe4e8f` |
| `cases/dafoam/ladder-a/A5/curriculum_MP_A5R/mpa5r_stage_and_run.sh` | `c87677b9e0f575dbfe005912cd4cc83d` |

---

## 0. WHY A SUCCESSOR — ONE SENTENCE, SO THE NEXT READER CANNOT REPEAT IT

**`MP_A5` registered a `p` initRes accept floor of `1.0e-06` calibrated from A5P2's measured
`1.448577e-08`, without noticing that A5P2's tree runs `endTime 5000` while the tree `MP_A5` stages
from runs `endTime 1000` — a floor measured on a 5×-longer raw-solver run, applied to the
1000-iteration optimisation tree.**

`MP_A5`'s arm `B` duly read `1.556e-06 / 9.596e-07 / 1.026e-06` at the three operating points, two of
three above the floor, and graded `GATE FAIL`. **That `GATE FAIL` stands, is not relaxed, and is not
rewritten** (`MP_A5/PREREGISTRATION.md`, and its run root
`/home/ubuntu/certonomous-runs/CURRICULUM-MP_A5-a5-ubend-multipoint-R3-20260912T062921Z`). This item
is the fix, not the excuse.

**Nothing in `MP_A5`'s physics is in question.** Its arm `B` established, at `rc=0` in 68 s:

* the three operating points are genuinely distinct — `dP` = `30.9277891 / 52.3451388 / 79.1978365`
  at `U0` = `6.30 / 8.40 / 10.50` — so the `primalBC U0` override lands (the detection `MP_A5` §6
  item 2 registered in advance: three *equal* values would have meant a failed override);
* the departures from pure U² scaling have the right sign — low-Re **+5.0 %**, high-Re **−3.2 %** —
  the turbulent friction factor falling with Re;
* the centre scenario reproduces two independent prior measurements of the same baseline:
  **−1.49e-06** relative to D9's `52.34521691559307` and **+7.92e-07** relative to A5P2's
  `52.34509736`. Three separate harnesses, one number to six or seven digits;
* `G-NONORTHO-IDENTITY` is satisfied at the baseline with all three KS values at
  `9.86166755159669` and spread **exactly 0**.

---

## 1. WHAT CHANGES FROM `MP_A5`, AND WHAT DOES NOT

**REGISTERED endTime: 5000.** The staged primal length now equals the length the floor was measured
at. Three things change and nothing else:

| # | change | why |
|---|---|---|
| **MP_A5R-1 / MP_A5R-L1** | **`endTime 5000` and `writeInterval 5000`** are written into `system/controlDict` of the arm root **and of every per-scenario copy**, and **read back**; a tree that does not carry them aborts the chain. `writeInterval` is set to the endpoint too, because a non-endpoint interval writes **no fields at `endTime`** and the endpoint must stay filmable. | the floor and the tree it grades can no longer disagree |
| **MP_A5R-1** | a new gate **`G-ENDTIME`** reads the last `Time = ` each primal segment **actually reached** and requires it to equal `5000` | `MP_A5`'s mismatch was invisible to its grading path. **Driven RED on `MP_A5`'s own arm B log before this freeze**, it returns `GATE FAIL, reached_per_segment [1000.0, 1000.0, 1000.0]` — it catches the exact defect it exists for, on the unfixed artefact, the way `so3_collision_leg.py` drives its invariant red on the unfixed source. |
| **MP_A5R-L1** | a **three-place assertion** at launcher start-up: the launcher's `REGISTERED_END_TIME`, the literal `REGISTERED endTime: 5000` in this document, and the grader's `REGISTERED_END_TIME = 5000` must all agree, or the chain refuses to start | the predecessor's whole failure was two of these disagreeing unseen |

**THE FLOOR ITSELF DOES NOT MOVE. `P_INITRES_FLOOR = 1.0e-06`, the identical literal.** It is
deliberately *not* tightened to A5P2's `1.448577e-08`: at a matching tree length `1e-06` is two
decades of headroom above a value measured on a matching tree, and re-using the same literal keeps
this item's `G-CONV` row comparable to its predecessor's, row for row. **Moving a threshold because
we now dislike where it landed is the thing pre-registration exists to prevent**; this item changes
the *tree*, not the *gate*.

**EVERYTHING ELSE IS CARRIED BYTE-IDENTICAL FROM `MP_A5` AND IS NOT RE-DERIVED HERE:** the three
scenarios `6.30 / 8.40 / 10.50 m/s` and their weights `0.25 / 0.50 / 0.25`; the composite
`J = Σ wᵢ(TP1ᵢ−TP2ᵢ)/nᵢ` with `nᵢ` measured in arm `B` of this chain; the per-scenario
`run_directory` isolation (`mp0/mp1/mp2`, `RUN_DIRS` derived from `SCENARIOS`, total and injective);
the `P2` primal setting `nNonOrthogonalCorrectors 0→2`; `shapexUpper` as the only design variable;
`meshQualityKS ≤ 70.0` taken from `point1`; SLSQP with `MAXIT 30`; image `dafoam-idwarp-rot:v1`;
np = 1; the cold-start guard with its planted control; the arm-aware chain rc; and all three planted
readers with their **refuse-exit-2** discipline.

---

## 2. THE GATES

Identical to `MP_A5`'s eight, **plus `G-ENDTIME`** on arms `B` and `E`:

| gate | threshold | PASS means |
|---|---|---|
| **G-RULE4** (per arm) | all five clauses incl. the age guard | the arm is done |
| **G-ENDTIME** (`B`, `E`) | every primal segment reached **`Time = 5000`** | the tree is the one the floor was calibrated on |
| **G-CONV** (`B`, `E`; per scenario) | last `p` initRes **`< 1.0e-06`** | every operating point's primal reached the accept floor |
| **G-EXPR** | character-for-character | the objective assembled is the objective registered |
| **G-J0** | `\|J₀ − 1\| ≤ 1e-06` | the normalisation is the registered one |
| **G-MP1** *(headline)* | `J_end ∈ [0.94, 0.98]` | the multipoint buy landed inside its registered band |
| **G-SCEN-ALL** | every scenario's `dP` falls | one point going backwards is `GATE FAIL` even if the weighted sum falls |
| **G-MESH** | raw `maxNonOrth ≤ 70.0` | the constraint held the endpoint inside the envelope |
| **G-NONORTHO-IDENTITY** | spread `≤ 1e-09` | the three scenarios share one deformed mesh |

Verdict order unchanged: G-RULE4 first; then any gate unevaluable → `NOT A RESULT`; then any gate
outside its band → `GATE FAIL`; else `PASS`. **A failing limb is not softened by a passing headline.**

---

## 3. REGISTERED PREDICTIONS

**P-1.** `G-CONV PASS` on all three scenarios in both `B` and `E`, with `p` initRes in the **1e-08**
decade — because A5P2 measured `1.448577e-08` at this exact setting **and this exact tree length**,
reproduced independently in A5P.

**P-2.** `G-ENDTIME PASS`, all segments at `5000`.

**P-3 — carried forward UNALTERED from `MP_A5`, and it has not yet been tested.**
**`TRIVIAL_MULTIPOINT`**: the multipoint endpoint within **l2 = 0.02** of D9successor's single-point
endpoint (recorded `l2 = 0.1622`), because the three Reynolds numbers span only **1.667×** and the
regime does not change. `G-TRIV` never converts a PASS into a GATE FAIL; both outcomes are results.
**Arm B's measured Re-dependence of the friction factor (+5.0 % / −3.2 % departures from U²) is the
first evidence that could bear on this, and it cuts against my prediction** — a real Re effect is
what would make the multipoint optimum differ from the single-point one. The prediction stands as
written.

**P-4.** `J_end ∈ [0.94, 0.98]`, from D9's 3.947 % and D9successor's 4.40 % single-point reductions.

**P-5.** `G-MESH PASS`, raw `maxNonOrth ≤ 70.0`; D9successor measured 69.2937 under the identical
constraint, and `MP_A5`'s baseline KS reads 9.86.

---

## 4. COST — REPORTED, AND **NO CAP OF ANY KIND**

**NO CAP OF ANY KIND** (Sanaa's fourth NO-CAP ruling, 2026-09-12, directive #17). No `timeout`, no
deadline, no budget, no core-minute guard, no watchdog that can signal; the launcher asserts no
executable `timeout` wrapper has grown back. **Memory containment KEPT and is not a cap:**
`--memory=3g --memory-swap=3g --oom-score-adj=500`.

**The estimate, re-derived on measured bases — and the predecessor's actuals are the basis, which is
the calibration rule working as intended:**

| component | basis | core-min |
|---|---|---|
| one `endTime 1000` three-scenario `run_model` | **`MP_A5` arm B measured: 68 s wall, np=1 → 1.1333 core-min** | 1.13 |
| the same at `endTime 5000` | 5× the primal iterations | **≈ 5.7** |
| arm `B` | one such arm | **≈ 5.7** |
| arm `O` — 30 majors × 3 scenarios × (primal + adjoint) | `MP_A5` arm O is still running at this freeze and its per-major cost is **not yet measured**; scaled from D9's 1.0 core-min/major/scenario × the P2 factor 2.53 × the 5× length | **≈ 1,125, WITH LOW CONFIDENCE** |
| arm `E` | one `run_model` | **≈ 5.7** |
| **TOTAL REGISTERED ESTIMATE** | | **≈ 1,140 core-min** (19 core-h) |

**`cost_basis`: DERIVED, NOT MEASURED.** `$0.97` at the owner-stated `$0.0513/core-h`. The box cannot
read its own billing.

**Honest confidence statement.** The arm-`O` figure is the one large number here and it is **scaled,
not measured** — `MP_A5`'s arm O had not completed when this was frozen. It will be replaced by a
measured basis in the calibration row, and if `MP_A5`'s arm O lands far from the scaling, **that is a
misprediction to report, not to absorb.**

**Contention.** Load average read **48.55 on 16 cores** earlier this session. Core-minutes are
wall × ranks, so actual/predicted is expected to exceed 1; that inflation is **contention, not
misprediction**, and is attributed separately per `CLAUDE.md` rule 12.

**Ranks:** np = 1, one pinned core, placement read back from the process. No sibling reniced,
re-pinned or disturbed.

---

## 5. WHAT THIS ITEM MAY NOT DO

* It may not be launched before the dafoam-supervisor's check-4 read of this freeze.
* It may not alter, renice or disturb any sibling run, including its own predecessor `MP_A5`, whose
  arm `O` is live at this freeze.
* It may not delete an interrupted run tree; `MP_A5`'s failed and stopped run roots are **evidence**.
* It may not relax `P_INITRES_FLOOR`, or any other gate, to rescue a result.
* It may not be sent anywhere. **SUBMISSIONS PARKED.**

---

*`MP_A5R` v1.0, 2026-09-12. Frozen with its grading path in one commit.*

---

## ADDENDUM 1 — 2026-09-12, after `MP_A5`'s arm `O` was OOM-killed

**Lines whose number changed above this section: 0.** No gate, threshold, band, label, prediction,
weight or scenario is altered. `mpa5r_grade.py` is **byte-identical** to its frozen state, md5
`895f2146ab203e41b2767aa9a3ed248a`. **This item remains UNLAUNCHED.**

### A1.1 What happened to the predecessor, and why it reaches this item

`MP_A5`'s arm `O` was killed at 3556 s: `ExitCode=137`, **`OOMKilled=true`**, `Memory=3221225472`,
59.2667 core-min, after **33 function evaluations**. Composed verdict for `MP_A5`: **`NOT A RESULT`**
— arm `O` fails rule-4 clause C1 and arm `E` never ran, and the registered verdict order puts rule 4
ahead of the `GATE FAIL` that `G-CONV_B` had already earned.

**This document was frozen from `MP_A5`'s instruments *before* that kill, so it inherited both
defects**, and at `endTime 5000` would have met them sooner and harder. Both are repaired here,
before any launch.

### A1.2 `MP_A5R-2` — the container memory was sized for one solver and this runs three

| | value | source |
|---|---|---|
| `MP_A5` (and this item as first frozen) | **3g** | carried **byte-identical** from `D9successor` — a **single-point** item, one `DASolver` |
| **SO3**, the lab's own proven 3-scenario multipoint, same solver, ran to `EXIT: Optimal Solution Found.` | **12g** | every arm in its ledger |
| **this item, repaired** | **`REGISTERED memory: 12g`** | SO3's **measured** precedent, not a guess |

`MP_A5` runs three `DASolver` instances, three IDWarp instances and three meshes in one process. I
scaled the problem 3× and left the containment at the single-point number.

**SIZING A LIMIT FOR THE PROBLEM IT ACTUALLY CONTAINS IS NOT WEAKENING THE GUARD, and no later reader
should mistake this for a relaxation.** `--memory`, `--memory-swap` and `--oom-score-adj=500` remain
on every container, are not optional and are not overridable by environment. Only the **number**
changes, and it changes because it was wrong.

### A1.3 `MP_A5R-2` — the recorder was what was *growing*

`recording_options["includes"] = ["*"]`, also carried from the single-point `D9successor`, records
**every variable at every driver iteration, including full field arrays**:

| item | scenarios | history file |
|---|---|---|
| SO3 | 3 | **3.5 MB** |
| D9successor | 1 | 105 MB |
| **MP_A5** | 3 | **460 MB — 131× SO3's** |

Changed to `includes = []`. The driver's own desvars, objectives and constraints are still recorded
by their own flags, which is exactly and only what this item reads back.

**Departure from the shape suggested, recorded rather than done quietly:** SO3 uses
`prob.add_recorder(...)`, a *problem* recorder. **This item does not adopt that pattern**, because
this item's **frozen** grading path reads `om.CaseReader(...).list_cases("driver")` for its
`obj_history` field, and a problem recorder leaves `list_cases("driver")` **empty** — adopting it
would silently blank a field the frozen comparator reads, and the frozen file may not be edited to
suit it (rule 6). Dropping `["*"]` fixes the entire defect in one token and leaves every frozen
reader working.

### A1.4 The transferable half — *when* it died is the diagnosis

It survived **3556 s and 33 evaluations** before dying. **A run that dies immediately tells you the
limit is wrong; a run that dies at evaluation 33 tells you something is growing** — and the 460 MB
recorder is what was growing. Had only the limit been raised, the recorder defect would have been
**masked rather than fixed**, and would have returned at a larger mesh or a longer run. Both are
repaired.

### A1.5 `MP_A5R-3` — the launch precondition: **`MemAvailable ≥ 14 GiB`**

**THIS IS NOT A CAP.** It never signals, stops, throttles or shortens a running solver — this item's
or anyone else's. It is a refusal to **START** when starting would take memory a live sibling is
relying on. A 12g container launched into 3 GiB of `MemAvailable` does not fail politely; it pushes a
peer's solver into the OOM killer, which is the precise harm `--memory` exists to prevent.

Measured at this addendum: **30 GiB total, 27 used, 2.77 available, 8.3 GiB already in swap**, with
`d6r2_O_mp` alone holding 11.21 GiB. The launcher reads `/proc/meminfo` at start-up, refuses with
**exit 75** below the threshold, and records the live container list beside the refusal. Driven
against the box at this addendum: `MemAvailable reads 2.77 GiB; required 14 → WOULD REFUSE`, which
is the correct behaviour tonight. The threshold is a standing condition, not a judgement call at
launch time.

### A1.6 §4's arm-`O` cost estimate is replaced by a **measured** basis

§4 registered ~1,125 core-min for arm `O` as **"SCALED, NOT MEASURED, LOW CONFIDENCE"**, because
`MP_A5`'s arm O had not completed at the freeze. It now has a measured basis: **59.2667 core-min
bought 33 function evaluations at `endTime 1000`** ≈ **1.80 core-min per evaluation**, so ≈ **9.0 per
evaluation at `endTime 5000`**. That is the one good thing the kill bought. It does not change any
gate; the calibration row will keep misprediction and **infrastructure loss** named separately and
never folded together.

### A1.7 Unchanged

No cap of any kind. Memory containment kept — and now correctly sized. np = 1 on its own cpuset.
**This item is NOT launched and may not be launched until check 4 clears this addendum AND the
`MemAvailable ≥ 14 GiB` precondition passes.** Every `MP_A5` run root is kept as evidence.

*`MP_A5R` v1.1, 2026-09-12.*
