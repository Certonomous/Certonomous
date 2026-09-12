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
