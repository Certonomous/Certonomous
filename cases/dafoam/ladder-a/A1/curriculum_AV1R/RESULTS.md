# Curriculum item AV-1R — np-invariance of the DAFoam adjoint at np = 1/2/4: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-30 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** AV-1R never landed one: its own chain grading returned a refusal, and a
refusal wrote no record — so the verdict that now stands for this item has until today lived only in
a successor's file and a preserved run root outside git.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no artefact was written, no preserved run root was touched, and **zero solver
> core-minutes were spent.** Every verdict, gate reading, band, hash, count and refusal string below
> is **copied verbatim from an existing frozen artefact and cited to it by path and by JSON key or
> line.** Where a figure a reader might want is **not** on record, this document says so and says
> where a reader would have to go — it does not supply one. A results record that quietly derives a
> fresh figure is a second grading of the same item wearing a scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings
> (`## 1. SPEND` … `## 6. WAITING LIST`) are **the morning report's**, matched literally so that a
> document carrying them *is* a morning report; a curriculum record wearing `## 5. REFILLED QUEUE`
> would be a malformed one. This record follows the family's own convention for a curriculum item —
> `curriculum_AV1/RESULTS.md`, `curriculum_AVWC/RESULTS.md`, `curriculum_AV2RG/RESULTS.md`.

---

# 1. Item verdict

| | |
|---|---|
| **ORIGINAL, by this item's own frozen grader** | ~~**`NOT A RESULT`**~~ — **struck as superseded for the run, and NOT struck as a fact about this item's own frozen path** |
| **CURRENT, by the successor `AVWC`** | **`PASS`** |
| **rows** | **`SHIPPED` `PASS`** and **`PATCHED` `PASS`** |

## 1.1 THE ORIGINAL REFUSAL, QUOTED IN FULL — this item refused first, and a reader is entitled to see on what

AV-1R's own in-chain grading on 2026-08-28 returned `NOT A RESULT` and evaluated no `G-NP` reading.
The refusal, verbatim from
`/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv/AV1R_grade_20260828T071352Z.json`
(keys `verdict`, `refusal`):

    "verdict": "NOT A RESULT"
    "refusal": "{\"REFUSE\": \"G-NP\", \"detail\": {\"mesh_cells\": 4032,
                 \"partition_cells\": [null, null], \"sum\": 0}}"

**The cause, as the successor recorded it and NOT as this lane diagnosed it:**
`AVWC_regrade.json` → `AV1R.defect_lines` reads verbatim
*"`av1r_x.py:75-87` (THE PRODUCER; the grader is not defective)"*. The NACA0012 incompressible
tutorial runs with `writeCompression on`, so the producer stats an uncompressed
`processorN/constant/polyMesh/owner` where the file on disk is `owner.gz`, and every `nCells` read
back `null`. **`AV1R`'s grader was never defective**, and this record does not treat it as though it
were.

## 1.2 THE CURRENT VERDICT AND WHAT PRODUCED IT — a SUCCESSOR, and the frozen grader was NOT edited

| | |
|---|---|
| successor item | **`AVWC`** — `cases/dafoam/ladder-a/A1/curriculum_AVWC/` |
| its pre-registration freeze | **`c85eb4df`**, committed **2026-08-28T17:47:02Z**, **before** the comparator was executed |
| AV-1R's frozen grader | `av1r_grade.py`, md5 **`b5c1d0092c6d2a2608ad3cc0899ed0fd`** — verified disk == `HEAD` blob (`curriculum_AVWC/RESULTS.md` §6, row 7 of 10) |
| AV-1R's frozen producer | `av1r_x.py`, md5 **`7313bab8b15629c9d872a39d0654aa08`** — verified disk == `HEAD` blob (same table, row 8) |
| repairs applied | **`["PARTITION"]`** (`AVWC_regrade.json` → `AV1R.repairs_applied`) |
| **names rebound** | **`[]` — AV-1R rebinds NOTHING AT ALL** (`AVWC_regrade.json` → `AV1R.names_rebound`) |

**No frozen file of AV-1R was edited.** `curriculum_AVWC/RESULTS.md` §1 states it for all three items
of that cluster: *"Every one of these three verdicts is the FROZEN instrument's own. The successor
re-implements no gate."* For AV-1R that statement is at its strongest — the successor rebinds no
name whatsoever, so **every band, threshold, composition rule and refusal clause that produced this
`PASS` is AV-1R's own frozen code, unedited on disk.**

# 2. TWO ROWS, AND BOTH OF THEM ARE STATED

A DAFoam verdict is `SHIPPED` and `PATCHED` or it is not a verdict about DAFoam.

| row | verdict |
|---|---|
| **`SHIPPED`** | **`PASS`** |
| **`PATCHED`** | **`PASS`** |

Source: `AVWC_full_grades.json` → `AV1R.grade.rows` = `{"SHIPPED": "PASS", "PATCHED": "PASS"}`.

**Here both rows pass, so the item verdict is carried by both and not by one.** That is worth saying
explicitly because it is *not* true of every item in this family — `curriculum_SO1a`'s verdict is a
split in which one row fails and the failing row carries it.

# 3. The gate readings, copied

All from `AVWC_full_grades.json` → `AV1R.grade.gates` unless another key is named.

| gate | verdict | number on record | key |
|---|---|---|---|
| **G1** completion | **`PASS`** | — | `gates.G1_completion` |
| **G-M2** mesh identity | **`PASS`** | `mesh_cells` **4032** | `gates.G-M2_mesh_identity`, `mesh_cells` |
| **G-NP** SHIPPED | reference arm `X1-S`, per-`np` readings | max objective spread **7.0775e-09** against band **2.2e-05** | `gates.G-NP_SHIPPED` |
| **G-NP** PATCHED | reference arm `X1-P`, per-`np` readings | same band | `gates.G-NP_PATCHED` |
| **G9** toolchain | **`PASS`** | per-arm image digest + printed `.so` md5 | `gates.G9_toolchain` |
| **G10** caps | **`PASS`** | total **9.069** core-min against ceiling **95.0**, `not_measured: []` | `gates.G10_caps.total_core_min` |
| **G12** placement | **`PASS`** | per-arm `cpuset` == registered on every arm | `gates.G12_placement` |
| GCI | **NOT QUOTED** | *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"* | `no_gci` |

**Registered bands, quoted from `AV1R.grade.bands`:** `objective_spread_rel` **2.2e-05**,
`gradient_spread_rel` **1.0e-03**, `sign_flips` **0**; provenance field reads
*"ADJOINT_VERIFICATION_STANDARD.md sec.3; PARALLEL_GATE_DOCTRINE.md:38; B3 bb5088c4:16-25;
VERIFICATION_CHARTER.md:845"*.

**Baselines on record, identical to every printed digit between AV1 and AV1R:**
`CD = 0.02091051000679216`, `CL = 0.49876526415423195`. `curriculum_AVWC/RESULTS.md` §4a checked that
agreement adversarially and reports it as **a determinism reading and nothing more** — two different
files in two different preserved roots, written 2026-08-27T13:41:26Z and 2026-08-28T07:04:50Z by the
same producer.

**Predictions, scored by the frozen code and copied unadjusted** (`AV1R.grade.predictions`):

| prediction | outcome |
|---|---|
| `P1_patched_row_np_invariance_PASS` | **HIT** |
| `P2_shipped_row_np_invariance_PASS` | **HIT** |
| `P3_objective_not_bit_identical_but_inside_band` | **HIT** — `P3_max_objective_spread_rel` **7.077477422391519e-09** |
| `P4_cost_ratio_np4_over_np1_shipped` | **HIT** — `P4_ratio_value` **2.0324483775811215** |
| **`P5_total_core_min_band`** | **MISS** |
| `P6_mesh_wall_le_120s` | **HIT** |
| `P7_cells_4032` | **HIT** |

**`P5` is a MISS and is printed here rather than omitted.** A record that prints only the hits is a
curated record (`curriculum_AVWC/RESULTS.md` §4a says the same of the same prediction).

# 4. THE FD / BRIGHT-LINE STATUS OF THIS ITEM — stated honestly, and it is "no FD table at all"

Quoted verbatim from `AVWC_full_grades.json` → `AV1R.grade.no_fd`:

> *"this rung carries no FD table; it is an np-invariance check of the adjoint against itself
> (standard sec.3), and moves no capability-grid verdict on its own"*

**So this item's `PASS` is NOT a bright-line result and must never be read as one.** It compares the
adjoint against **itself** across rank counts. It says nothing about whether the gradient is right —
only that it does not change when the decomposition does. The capability-grid cell it touches is
quoted verbatim as *"2D . steady . incompressible — np-invariance evidence for the gradient column's
'what was checked'"*, and the `no_fd` field says the item **moves no capability-grid verdict on its
own**.

**Where the bright line IS carried on A1, for a reader who came here looking for it:**
`curriculum_SO1aR/RESULTS.md` §3.2 (FD vs adjoint on SO-1a's preserved root) and
`reverify_patched_idwarp_np1/RESULTS.md` §2. Neither is this item's and neither is restated here.

**No Roache triple, no GCI.** `no_gci` verbatim: *"no grid family; standing rule 5 has no row; NO GCI
IS QUOTED"*.

# 5. THE `PASS` WAS NOT ACCEPTED UNTIL THE READER WAS PROVED ABLE TO REFUSE

A repaired reader that moves a verdict in the flattering direction is exactly where a genuine absence
gets laundered into a pass. `curriculum_AVWC/RESULTS.md` §4 records five must-flag plants travelling
the real preserved files, the real adopted reader and the real frozen grader; **five of five fired,
in two independent readings.** Two of the five plant directly into AV-1R's own preserved root:

* **`owner.gz` deleted from `X2-S/processor0`** → the FROZEN grader refused, `G-NP`,
  `partition_cells [null, 2016]`, `sum 2016` against `mesh_cells 4032`.
* **`nCells` rewritten INSIDE the real gzip on `X4-S`** → refused, `G-NP`,
  `partition_cells [1007, 1008, 1008, 1008]`, `sum 4031`.

**The plant is non-vacuous, checked on the preserved root itself** (§4 of that record):
`…CURRICULUM-AV1R…/X2-S/processor0/constant/polyMesh/owner` is **ABSENT** while `owner.gz` is
**PRESENT at 8,312 bytes**, so deleting it removes the only readable name and creates a real absence.
The registered `EXPECTED_UNITS` is **20**; units run were **20** under `python3` and **20** under
`python3 -O`, **0 failures** in each.

**The frozen grader's own two controls fired inside the graded run** (`AV1R.grade.controls`):
`grader_plant_X2S` → `grader_plant_seen: true`, **20 values**, worst residual **1.7932703932910243e-16**;
`sign_flipped_X4S_read_as_GATE_FAIL` → `seen: true`, **20 flips of 20 expected**. That is
`CLAUDE.md` rule 3 satisfied inside the instrument that issued this verdict.

> **Disclosed, not hidden:** the `controls.grader_plant_X2S.file` field in
> `AVWC_full_grades.json` carries a **transient scratchpad path** that no longer exists.
> `curriculum_AVWC/RESULTS.md` §9.1 discloses this as a defect of the machine record and leaves it
> **as executed**, on the reasoning that editing an instrument's own output after the fact would be
> worse than the defect. **No path in this prose document is a scratch path** (`CLAUDE.md` rule 13).

# 6. The preserved run root was not mutated

| | value | key |
|---|---|---|
| preserved root | `/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv` | `AV1R.preserved_root` |
| files | **755** | `AV1R.preserved_root_files` |
| md5 manifest before == after | **`true`** | `AV1R.root_manifest_identical` |

`curriculum_AVWC/RESULTS.md` §3 records that `root_manifest_identical` was `true` in the recorded run,
true again in an independent re-run, and true on every one of the seven planted runs; the refusal
clause `PRESERVED_ROOT_MUTATED` never fired on any invocation. The 755th file is
`grader_controls/X_X2S_planted.json`, left by **AV-1R's own** in-chain grading on 2026-08-28, present
before `AVWC` existed and unchanged by it.

**This lane wrote nothing into that root either**, and read from it only the original grade JSON
quoted in §1.1.

# 7. Cost — rule 12

**SOLVER COMPUTE BOUGHT BY THE RE-GRADE: ZERO core-minutes.** Nothing was meshed, solved or
containerised; no GPU was touched; `verification/queue/` was not opened
(`curriculum_AVWC/RESULTS.md` header and §8).

**Instrument cost of the re-grade: `1.33353` core-min MEASURED at ranks 1**, against a registered
**3.00** core-min and a **10.00** cap — ratio **0.4445**, **13.3 % of cap**. Dollars **$0.0011402
DERIVED, NOT MEASURED** at $0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER**
(`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing).

> **NOT ON RECORD, AND NOT SUPPLIED HERE: AV-1R's individual share of that 1.33353 core-min.**
> The figure is `AVWC`'s **registered scope total across all three of its items** (AV1, AV1R, AV2),
> summed from three `/usr/bin/time -v` invocations that each covered the whole cluster. **No per-item
> split exists in any artefact**, and this lane will not manufacture one by division. A reader who
> needs a per-item cost must go to `curriculum_AVWC/RESULTS.md` §7 and see that the measurement was
> not taken that way.

**Calibration row: `C-212`** in `docs/COST_CALIBRATION.md` (dated 2026-08-30, team dafoam, subject
`AVWC`).

> **⚠ A DISCREPANCY IN AN EXISTING RECORD, REPORTED AND NOT REPAIRED BY THIS LANE.**
> `curriculum_AVWC/RESULTS.md` §7 closes with *"The calibration row is `C-211`"*. **In
> `docs/COST_CALIBRATION.md` as it stands, `C-211` is an `ansys-verification` row (VMFL063), and the
> `AVWC` row is `C-212`.** The most likely explanation is rule-11 drift — the id was written from a
> tail read before a concurrent peer commit took `C-211` — but that is an inference, not a
> measurement, and correcting another item's record is not this lane's call. **It is flagged to the
> supervisor.**

**AV-1R's own solver spend is NOT re-charged to the re-grade.** It belongs to AV-1R's original 2026-08-28
chain; `AVWC_full_grades.json` → `AV1R.grade.gates.G10_caps` records **total 9.069 core-min** against
a **95.0** ceiling with per-arm figures beside it. **Whether that spend has a calibration row of its
own is not established by this record** — a reader must check `docs/COST_CALIBRATION.md` directly.

# 8. WHERE THE FULL READINGS LIVE — this record is a signpost, not a duplicate

A record that restates every number drifts from its source the first time the source is corrected.
The authorities, in order of precedence:

1. **`cases/dafoam/ladder-a/A1/curriculum_AVWC/AVWC_full_grades.json`** → key `AV1R` — the complete
   payload: every per-`np` objective and gradient reading, every arm's completion fields, `G9`
   digests, `G10` per-arm caps, `G12` placement, controls, predictions.
2. **`cases/dafoam/ladder-a/A1/curriculum_AVWC/AVWC_regrade.json`** → key `AV1R` — the verdict of
   record, the repairs set, the rebind set, the partition repair per arm, the root manifest result.
3. **`cases/dafoam/ladder-a/A1/curriculum_AVWC/RESULTS.md`** — §1 the verdict table, §3 the root
   manifest, §4 and §4a the controls and the gate readings behind the pass, §6 the hash table, §7 the
   cost, §9 the two disclosed defects.
4. **`cases/dafoam/ladder-a/A1/curriculum_AVWC/PREREGISTRATION.md`**, frozen `c85eb4df` — the gates,
   the repair semantics, the rebind audit and the registered branches.
5. **`cases/dafoam/ladder-a/A1/curriculum_AV1R/PREREGISTRATION.md`** — this item's own frozen gates.
6. **`/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv/`** (755 files, outside git) —
   the preserved run root, carrying `AV1R_grade_20260828T071352Z.json` (the original refusal), the
   per-arm artefacts, the age datums, the solver logs and the memory windows.

**If any figure in this record disagrees with the JSON, the JSON is right.**

# 9. What this record does and does not do

**It does** give AV-1R an item-level record where it had none, so that a reader who goes to this item
finds its verdict instead of nothing. `curriculum_AVWC/RESULTS.md` §10 flagged the gap explicitly —
*"AV1R has no `RESULTS.md`, neither on disk nor at HEAD … This lane has not created one: writing a
first `RESULTS.md` for an item it did not grade is a supervisor's call, not a lane's."* **The
supervisor has since made that call, and this document is its execution.**

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, or add any number that was not already written down in a cited artefact.

**It does not** revise what this item's own frozen instrument produced. On AV-1R's own frozen path a
`G-NP` refusal is what the code returns, and §1.1 stands as the record of it. The `PASS` in §1 is the
verdict on the **preserved artefacts**, reached by a successor that ran AV-1R's own unedited
`grade()`.

**It establishes nothing about the physics, the mesh or the solver.** No solver ran for the re-grade.
