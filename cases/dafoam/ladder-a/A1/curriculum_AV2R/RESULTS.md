# Curriculum item AV-2R — forward-AD versus reverse-AD duality on A1's NACA0012: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-30 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** AV-2R never landed one — `curriculum_AV2RG/RESULTS.md` §9 records the fact:
*"AV2R's `RESULTS.md` does not exist — that item never landed one."* Its verdict has until today
lived only in a successor's file and in a preserved run root outside git.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no artefact was written, no preserved run root was touched, and **zero solver
> core-minutes were spent.** Every verdict, gate reading, band, hash, count and refusal string below
> is **copied verbatim from an existing frozen artefact and cited to it by path and by JSON key or
> line.** Where a figure a reader might want is **not** on record, this document says so and says
> where a reader would have to go — it does not supply one.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the morning
> report's**, matched literally so that a document carrying them *is* a morning report; a curriculum
> record wearing `## 5. REFILLED QUEUE` would be a malformed one. This record follows the family's
> own convention — `curriculum_AV2RG/RESULTS.md`, `curriculum_AVWC/RESULTS.md`,
> `curriculum_AV1/RESULTS.md`.

---

# 1. Item verdict

| | |
|---|---|
| **ORIGINAL, by this item's own frozen grader** | ~~**`NOT A RESULT`**~~ — **struck as superseded for the run, and NOT struck as a fact about this item's own frozen path** |
| **CURRENT, by the successor `AV2RG`** | **`BLOCKED`** |
| **rows** | **`SHIPPED` `BLOCKED`** and **`PATCHED` `BLOCKED`** |

**`BLOCKED` here is a statement about DAFoam, not about a missing field.** The word is quoted from
`curriculum_AV2RG/RESULTS.md` §1: *"Both items previously died at a **refusal** — the comparator
stopped and no gate returned a reading. Both now produce a **composed verdict** from gates that all
ran … the forward-mode AD channel does not produce a tangent on this case."*

## 1.1 THE ORIGINAL REFUSAL, QUOTED IN FULL — this item refused first, and on what

AV-2R's own in-chain grading on 2026-08-28 returned `NOT A RESULT` and evaluated no `G-DP` reading.
Verbatim from
`/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality/AV2R_grade_20260828T024400Z.json`
(keys `verdict`, `refusal`):

    "verdict": "NOT A RESULT"
    "refusal": "{\"REFUSE\": \"G-DP\", \"detail\": {\"gmresRelTol_in_artefact\": null,
                 \"note\": \"the band is 10 x the adjoint solve tolerance; a different
                 tolerance is a different band\", \"registered\": 1e-06, \"row\": \"S\"}}"

**The cause, as the successor recorded it and NOT as this lane diagnosed it:**
`AV2RG_regrade.json` → `AV2R.defect_lines` reads verbatim
*"`av2r_xf.py:56-63` `idwarp_identity()` (THE PRODUCER); the grader (`av2r_grade.py:321, :511-513`) is
NOT defective"*. `docs/COST_CALIBRATION.md` row `C-216` states the same and adds that the same
function is **byte-identical** in `curriculum_AV2/av2_xf.py`: the identity dict returns only
`{"idwarp_file", "libidwarp_so_md5"}`, while `:152-156` emits `gmresRelTol` into the JSONL sidecar one
statement earlier. **The tolerance was on disk, at `1e-06`, on every arm; it was never carried into
the `.json` artefact the grader reads.**

## 1.2 THE CURRENT VERDICT AND WHAT PRODUCED IT — a SUCCESSOR, and the frozen grader was NOT edited

| | |
|---|---|
| successor item | **`AV2RG`** — `cases/dafoam/ladder-a/A1/curriculum_AV2RG/` |
| pre-registration freeze | **`2f827746`** (v1.0), **2026-08-30T22:54:01Z** |
| pre-compute amendment | **`42a3c988`** (v1.1, Amendment 1 — AV2 added), **2026-08-30T23:06:30Z** |
| post-compute amendment | **`cb9adb7f`** (v1.2, Amendment 2 — two unit assertions), **2026-08-30T23:18:18Z**, under `VERIFICATION_CHARTER.md` §2d.1 |
| AV-2R's frozen grader | `av2r_grade.py`, md5 **`8a2dcebd954f56d9970601fc7761787a`** — verified disk == `HEAD` blob (`curriculum_AV2RG/RESULTS.md` §9) |
| AV-2R's frozen producer | `av2r_xf.py`, md5 **`32a755bc9fa84bc0e03ab02bb6ec3c3c`** — verified disk == `HEAD` blob (same) |
| repairs applied | **`["GMRES"]`** (`AV2RG_regrade.json` → `AV2R.repairs_applied`) |
| **names rebound** | **`[]` — AV-2R rebinds NOTHING** (`AV2RG_regrade.json` → `AV2R.names_rebound`) |

**No frozen file of AV-2R was edited.** The successor imports AV-2R's own frozen comparator, proves it
byte-identical to the committed blob at every invocation (`FROZEN_GRADER_MD5` and
`FROZEN_PRODUCER_MD5` are **refusal clauses, not comments**), rebinds no name at all, and runs the
frozen `grade()`. **Every band, threshold and composition rule that produced this `BLOCKED` is AV-2R's
own frozen code, unedited on disk.**

> **The §2d.1 post-compute amendment is disclosed rather than left to be found.**
> `curriculum_AV2RG/RESULTS.md` §10.2 records that v1.1's selftest **FAILED, 24/26**, on two unit
> assertions naming a clause the reader cannot raise on that path; the repair was taken only under the
> four §2d.1 conditions with **`VERDICTS MOVED: 0, BANDS MOVED: 0, THRESHOLDS MOVED: 0, REFUSAL
> CLAUSES OF THE FROZEN GRADER MOVED: 0`**, and **the exception was granted by this family's own
> supervisor on this family's own item**. That grant is **routed to `verification-supervisor` for
> independent audit and the audit is NOT yet on record.** If verification overturns it, the repair is
> withdrawn — and this verdict is downstream of that ruling.

# 2. TWO ROWS, AND BOTH OF THEM ARE STATED

A DAFoam verdict is `SHIPPED` and `PATCHED` or it is not a verdict about DAFoam.

| row | verdict | source |
|---|---|---|
| **`SHIPPED`** | **`BLOCKED`** | `AV2RG_full_grades.json` → `AV2R.grade.rows.SHIPPED` |
| **`PATCHED`** | **`BLOCKED`** | `AV2RG_full_grades.json` → `AV2R.grade.rows.PATCHED` |

**Both rows are `BLOCKED`, so no row carries a friendlier reading than the item.** There is no
favourable arm here that a reader could lift away from the item verdict.

# 3. The gate readings, copied

From `AV2RG_full_grades.json` → `AV2R.grade.gates`, and `curriculum_AV2RG/RESULTS.md` §2 where named.

| gate | verdict | number on record |
|---|---|---|
| **G1** completion (all five arms) | reached, **no refusal** | — |
| **G-M2** mesh identity | **`PASS`** | cells **4032** |
| **G9** toolchain (3-source) | **`PASS`** | — |
| **G10** caps | **`PASS`** | total **20.766** core-min against ceiling **75.0**, `not_measured: []` |
| **G12** placement | **`PASS`** | — |
| **G-DP** SHIPPED (CD and CL) | **`BLOCKED`** | `n_graded 0`, `n_blocked 5`, `worst_eps null` |
| **G-DP** PATCHED (CD and CL) | **`BLOCKED`** | `n_graded 0`, `n_blocked 5`, `worst_eps null` |
| GCI | **NOT QUOTED** | *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"* (`no_gci`) |

**Registered bands, from `AV2R.grade.bands`:** `eps_per_component` **1e-05**,
`gmresRelTol_registered` **1e-06**, `near_zero` **1e-14**; provenance field reads
*"ADJOINT_VERIFICATION_STANDARD.md sec.2 (10 x gmresRelTol); v1.0a forward-channel controls"*.

**The recovered field:** `gmresRelTol` = **`1e-06`** (dimensionless), on **all four repaired arms of
both items**, from all three registered sources in exact agreement, with **`mtime_preserved: true`**
on every one — so the rule-4 age guard still dates the solver's write and not the instrument's
(`curriculum_AV2RG/RESULTS.md` §2).

## 3.1 WHY `BLOCKED` — one failure, twenty times

`curriculum_AV2RG/RESULTS.md` §3 records **5 of 5 registered components `blocked` on `CD` and on `CL`,
on the SHIPPED row and the PATCHED row — twenty component-readings, ZERO graded — and one distinct
reason across all of them.** The reason, verbatim from
`AV2RG_full_grades.json` → `gates.G-DP_SHIPPED.G-DP_CD.components[*].reason`:

    AnalysisError("'scenario1.coupling.solver' <class DAFoamSolver>:
                  Error calling solve_nonlinear(), Primal solution failed!")

and the gate's own summary `reason` field reads *"5 component(s) blocked in forward mode"*.

**The scope of that statement is fixed by AV-2R's own frozen text and is inherited unchanged.**
`curriculum_AV2R/PREREGISTRATION.md:156` anticipated this outcome and says nothing about forward mode
*in general* — only that **on this case, at this `endTime` and this `primalMinResTolDiff`, the primal
does not reach acceptance.**

## 3.2 TWO CONTROLS DID NOT RUN, AND THAT IS SAID RATHER THAN IMPLIED

`AV2RG_full_grades.json` → `AV2R.grade.controls`:

* `sign_flipped_XS_read_as_GATE_FAIL` → **`seen: false`**, note *"FAD-S blocked; the transpose control
  has nothing to read"*.
* `silent_zero_FADS_refused` → **`seen: false`**, same branch (`av2r_grade.py:530-532` takes its
  registered `blocked_any` branch).

**A control that had nothing to read is not a control that passed.**

What *did* fire: `forward_channel_S` and `forward_channel_P` both `forward_channel_controls_pass: true`;
`grader_plant_XS` → `grader_plant_seen: true`, **20 values**, worst residual
**1.7932703932910243e-16**. And the birth requirement: **28 of a frozen `EXPECTED_UNITS = 28`, 0
failures, `rc = 0` under `python3` AND `python3 -O`** from a proven-clean `__pycache__` state
(`av2rg_selftest_evidence_v1_2_clean.txt`; the failing predecessor run is preserved unaltered in
`av2rg_selftest_evidence.txt` at 24/26).

> **Disclosed, not hidden:** `controls.grader_plant_XS.file` in `AV2RG_full_grades.json` carries a
> **transient scratchpad path** that no longer exists, as do the `recovery.*.sources.*.path` fields.
> These are machine records of a transient working copy, left as executed. **No path in this prose
> document is a scratch path** (`CLAUDE.md` rule 13).

# 4. THE FD / BRIGHT-LINE STATUS — TWO CAVEATS, BOTH THE SUPERVISOR'S, THE SECOND A CORRECTION AGAINST HIS OWN EARLIER RULING

This is the section a reader must not skip, and neither caveat may be collapsed into a sentence
saying an FD table exists.

**The item's own `no_fd` field, verbatim** (`AV2RG_full_grades.json` → `AV2R.grade.no_fd`):

> *"this rung carries no FD table; its reference is forward-mode AD (the exact tangent), standard
> sec.2"*

## 4.1 CAVEAT ONE — `shape[0]` and `shape[6]` MAY NOT CLAIM FD CORROBORATION

**Supervisor Ruling 1, 2026-08-30**, registered before execution at
`cases/dafoam/ladder-a/A1/curriculum_AV2RG/PREREGISTRATION.md` §A1.4 and copied here as a split, per
component:

| component | FD corroboration at a step PROVED to lie in the plateau |
|---|---|
| `shape[3]`, `shape[7]`, `patchV[1]` | **MAY be claimed** — `reverify_patched_idwarp_np1/RESULTS.md` §2 @ `be35dcad`, within the five-of-eight plateau of `A_stepsize_study.md` |
| **`shape[0]`** | **MAY NOT BE CLAIMED** — excluded from the plateau (`cases/dafoam/ladder-a/A_stepsize_study.md:45-46`; flat but step-independent at −8 % to −16 % across three decades, so not a step artefact) |
| **`shape[6]`** | **MAY NOT BE CLAIMED** — excluded, and *"**there is no step at which idx6 is a trustworthy estimate**"* (`cases/dafoam/ladder-a/A_stepsize_study.md:40`, quoted verbatim) |

## 4.2 CAVEAT TWO — THE FORWARD-AD DISCHARGE OF THE BRIGHT LINE IS **WITHDRAWN ON ITS FACTS**

**This is the supervisor's own correction, dated 2026-08-30, and it is recorded here as his and not as
this lane's discovery.**

§A1.4 as frozen ruled that AV-2R is the forward-AD-versus-reverse-AD **duality** rung, whose reference
is an **exact** derivative carrying no step and no plateau question, so `DAFOAM_CHARTER.md` §2's second
clause discharges the bright line **by forward AD rather than by FD**. That ruling was made before the
item was executed.

**It does not survive the measurement, and the supervisor withdraws it on its facts.** `AV2RG` measured
that **the forward-AD primal does not converge on this case — 20 FAD readings, ZERO graded** (§3.1
above). **A reference that never produced a value cannot discharge a bright line.** So:

> **THERE IS NO FD REFERENCE FOR `shape[0]` OR `shape[6]`, AND THERE IS NO FORWARD-AD REFERENCE FOR
> ANY COMPONENT ON THIS RUN. THE BRIGHT LINE IS NOT DISCHARGED FOR THIS ITEM BY EITHER ROUTE.**

`curriculum_AV2RG/RESULTS.md` §6 states the same conclusion from the other side: *"the duality
reference itself never produced a value, so **neither** the forward-AD discharge **nor** the FD
corroboration delivers a number for any component here. AV2RG quotes no FD verdict and no duality
verdict."* **Neither does this record.**

**Consequence for the census, quoted verbatim from `AV2R.grade.capability_grid_cell`:** *"2D . steady .
incompressible — dot-product/duality evidence for the gradient column's 'what was checked'; the census
line's 'never performed' moves only on a graded row."* **There is no graded row, so the census line
does not move.**

# 5. A THIRD-INSTRUMENT CONVERGENCE — REPORTED, NEVER GATED, AND NOTHING CAUSAL IS CLAIMED

The shipped-versus-patched divergence on the **reverse** `CD` gradient is explicitly reported and not
gated (`av2r_grade.py:537-542`). Copied from
`AV2RG_full_grades.json` → `AV2R.grade.divergence_rev_shipped_vs_patched_CD`:

| component | divergence, SHIPPED vs PATCHED |
|---|---|
| `shape[0]` | **10.6497 %** |
| `shape[3]` | 4.0095 % |
| **`shape[6]`** | **118.7258 %** — and the two reverse gradients carry **opposite signs** (`+0.0056907374` shipped, `−0.0010656352` patched) |
| `shape[7]` | 1.7374 % |
| `patchV[1]` | **0.0000 %** |

Set beside the two independent readings already on record (`curriculum_AV2RG/RESULTS.md` §5):
`curriculum_SO1aR/RESULTS.md:53,:80` reads `shape[0]` **11.9330 %** and `shape[6]` **637.7570 %, SIGN
FLIPPED** on the shipped row by FD-versus-adjoint; `A_stepsize_study.md` excludes both from its
plateau. **Three instruments, three methods, one pair of design variables — and `patchV[1]`, which
cannot cross `warpDeriv`, reads exactly `0.0000 %`, which is the control that makes the other four
numbers legible.**

**NOTHING CAUSAL IS CLAIMED. This is a convergence, not a mechanism.** It gates nothing in this item
and no verdict here may be stated in terms of it.

# 6. The preserved run root was not mutated

| | value | key |
|---|---|---|
| preserved root | `/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality` | `AV2R.preserved_root` |
| files | **378** | `AV2R.preserved_root_files` |
| md5 manifest before == after | **`true`** | `AV2R.root_manifest_identical` |

`curriculum_AV2RG/RESULTS.md` §8 records an md5 manifest of every regular file taken before and after
**every** re-grade including all 15 of the selftest, `root_manifest_identical: true` throughout, and
an independent reconfirmation afterwards showing **0 entries newer than 2026-08-29**. A run root is
not in git, so a `git status` cleanliness check is blind to exactly the thing being protected.

**This lane wrote nothing into that root either**, and read from it only the original grade JSON
quoted in §1.1.

# 7. Cost — rule 12

**SOLVER COMPUTE BOUGHT BY THE RE-GRADE: ZERO core-minutes.** Nothing was meshed, solved or
containerised; no GPU was touched (`curriculum_AV2RG/RESULTS.md` header; `C-216`).

**Instrument cost of the re-grade: ≈ `0.20` core-min MEASURED at ranks 1**, against a registered
**6.00** core-min and a **15.00** cap — ratio **≈ 0.033**, **1.3 % of cap**. Dollars **$0.000171
DERIVED, NOT MEASURED** at $0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER**
(`COMPUTE_BUDGET_CHARTER.md` §5). **Waste: 0 core-min** — `C-216` and §11 of that record both hold
that the failing v1.1 battery is **not** waste, because it bought the finding that two controls were
mis-specified.

> **NOT ON RECORD, AND NOT SUPPLIED HERE: AV-2R's individual share of that ≈ 0.20 core-min.**
> The figure covers `AV2RG`'s **two-item scope** (AV2R **and** AV2) and is stated to two significant
> figures because the wall figures are at 1 s timer resolution. **No per-item split exists in any
> artefact**, and this lane will not manufacture one by division.

**Calibration row: `C-216`** in `docs/COST_CALIBRATION.md` (2026-08-30, dafoam, subject `AV2RG`).

**AV-2R's own solver spend is NOT re-charged to the re-grade.** It belongs to AV-2R's original
2026-08-28 chain; `AV2RG_full_grades.json` → `AV2R.grade.gates.G10_caps` records **total 20.766
core-min** against a **75.0** ceiling, per arm: MESH **0.183** · X-S **1.017** · FAD-S **9.4** ·
X-P **1.033** · FAD-P **9.133**. **Whether that solver spend has a calibration row of its own is not
established by this record** — `C-216` is explicitly the instrument row. A reader must check
`docs/COST_CALIBRATION.md` directly.

# 8. WHERE THE FULL READINGS LIVE — this record is a signpost, not a duplicate

1. **`cases/dafoam/ladder-a/A1/curriculum_AV2RG/AV2RG_full_grades.json`** → key `AV2R` — every
   component reading with its `g_rev` value and blocked reason, all gate payloads, controls,
   predictions, completion, divergence.
2. **`cases/dafoam/ladder-a/A1/curriculum_AV2RG/AV2RG_regrade.json`** → key `AV2R` — the verdict of
   record, repairs, rebind set, the three-source `gmresRelTol` recovery, the root manifest result.
3. **`cases/dafoam/ladder-a/A1/curriculum_AV2RG/RESULTS.md`** — §1 verdicts, §2 the repaired gates,
   §3 the `BLOCKED` mechanism, §5 the third-instrument convergence, §6 the FD position, §7 the birth
   requirement, §9 the hash table, §10 the two disclosed instrument defects, §11 cost.
4. **`cases/dafoam/ladder-a/A1/curriculum_AV2RG/PREREGISTRATION.md`** (v1.2) — §A1.4 the FD ruling,
   §A2.6 the mtime laundering incident and its closure, §8 the registered prediction.
5. **`cases/dafoam/ladder-a/A1/curriculum_AV2R/PREREGISTRATION.md`** — this item's own frozen gates,
   including `:156` fixing the scope of the forward-mode failure.
6. **`/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality/`** (378 files, outside git) —
   the preserved run root, carrying `AV2R_grade_20260828T024400Z.json` (the original refusal), the
   per-arm artefacts and the solver logs.

**If any figure in this record disagrees with the JSON, the JSON is right.**

# 9. What this record does and does not do

**It does** give AV-2R an item-level record where it had none, so that a reader who goes to this item
finds its verdict, its two rows, and both FD caveats instead of nothing.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, or add any number that was not already written down in a cited artefact.

**It does not** revise what this item's own frozen instrument produced. On AV-2R's own frozen path a
`G-DP` refusal is what the code returns, and §1.1 stands as the record of it.

**It establishes nothing about physics, mesh or solver beyond the forward-mode primal's failure on
this case at these settings** — no solver ran here. **No duality result:** the dot-product test
remains **not measured** in this family. **No FD verdict.** **A `BLOCKED` is not a `PASS` deferred** —
it is the registered mapping for a row whose forward channel returned nothing.
