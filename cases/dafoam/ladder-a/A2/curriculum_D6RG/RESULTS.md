# Curriculum item D6RG — D6R re-graded from its preserved run root through one repaired reader: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-30 by a lane of the DAFoam team.** The governing document is
`PREREGISTRATION.md` in this directory, frozen at commit **`5563f78533391e8ec5842db915ff70ebd7663685`**
**before** the comparator was executed. **This file does not revise the pre-registration.** No gate,
threshold, cap, band edge or label was altered by this lane, and **no frozen file of D6R was
edited** — §6 below proves that by hash.

**SOLVER COMPUTE: ZERO core-minutes.** Nothing was meshed, nothing was solved, no container was
started, no GPU was touched. Every number below was read from artefacts that already existed on
disk before this lane began.

> **A note on this record's shape, stated rather than left to be inferred.** The assigning brief
> asked for `REPORTING_CHARTER.md`'s six fixed headings. Read in full, that charter's six headings
> (`## 1. SPEND` … `## 6. WAITING LIST`, §2) are **the morning report's**, and §2 rule 1 says they
> are matched literally so that a document carrying them *is* a morning report. A curriculum record
> carrying `## 5. REFILLED QUEUE` and `## 6. WAITING LIST` would be a **malformed morning report**,
> which is the single failure that section exists to prevent. This record therefore follows the shape
> its sibling `curriculum_AVWC/RESULTS.md` uses, and honours `REPORTING_CHARTER.md` §10 and §11,
> which bind any record: no number without its artefact, no label the number did not earn, and no
> curation. **The conflict is reported to the supervisor, not resolved silently.**

---

# 1. Item verdict

| | |
|---|---|
| **D6R, verdict BEFORE (frozen instrument, unmodified)** | **`NOT A RESULT` by comparator refusal, with ZERO of eleven gate readings** — `REFUSE G-D6R-OPT no_final_objective_or_exit`, `n_obj = 0`, `n_exit = 1`, exit code 2, no verdict JSON written |
| **D6RG, verdict AFTER the repaired reader** | **`NOT A RESULT`**, composed from **eleven** gate readings |
| names rebound | **`["read_ipopt"]`** — exactly the registered set, fingerprint-audited |

Source: `cases/dafoam/ladder-a/A2/curriculum_D6RG/D6RG_regrade.json`;
`cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_selftest_evidence.txt`.

**The verdict is the FROZEN instrument's own.** D6RG re-implements no gate. It imports D6R's own
frozen comparator, proves the file on disk is byte-identical to the committed blob, rebinds exactly
one name, and runs the frozen `grade()`. Every band, threshold, cap, label, composition rule,
prediction and refusal clause that decided this verdict is literally the frozen code.

**The verdict did not improve, and that is the correct outcome.** `NOT A RESULT` before,
`NOT A RESULT` after — but the two are not the same object. Before, the item had **no readings at
all**; after, it has eleven gates, an optimiser classification, eight scored predictions and a cost
census. **A `NOT A RESULT` that stays `NOT A RESULT` is a result and is reported as one**
(`PREREGISTRATION.md` §7).

## 1a. The frozen grader was DRIVEN, not predicted

A predicted refusal is weaker than a measured one. Before a line of successor code was written, the
frozen `d6r_grade.py` was run **unmodified** against a `cp -a` copy of the preserved run root:

| | |
|---|---|
| exit code | **2** |
| stdout | `D6R_GRADE REFUSED {"REFUSE": "G-D6R-OPT", "detail": {"n_exit": 1, "n_obj": 0, "no_final_objective_or_exit": "<copy>/O_mp/opt_IPOPT.txt"}}` |
| verdict JSON written | **none**, at the `--out` path or beside the grader |
| gate readings printed | **zero of eleven** |
| `grader_controls/` created in the copy | **none** — the frozen planted-zero control never fired |
| preserved root after | md5 manifest of **14,546** files **identical** |

**The `EXIT:` line IS present and only the summary `Objective` line is missing**, so the refusal
fires on one limb of the two-limb test at `d6r_grade.py:620-621`. That refinement matters: the log
is not truncated, it is *unreadable by this reader*.

# 2. The eleven gate readings the repair bought

| gate | verdict |
|---|---|
| `G1_completion` | `NOT A RESULT` |
| `G-D6R-1_cl04` / `_cl05` / `_cl06` | `NOT A RESULT` ×3 |
| `G-D6R-2_composite` | `NOT A RESULT` |
| `G-D6R-3_price` | `NOT A RESULT` |
| `G-D6R-4_fd` | `NOT A RESULT` |
| `G-D6R-OPT_optimiser` | `NOT A RESULT` |
| `G9_toolchain` | **`PASS`** |
| `G10_caps` | **`GATE FAIL`** |
| `G12_placement` | **`PASS`** |

The frozen composer's own `not_a_result_reasons`, verbatim from the artefact: *a completion clause
failed on an arm that ran*; *registered arms did not run: F_mp, REF_off*; *optimiser outcome
UNCLASSIFIED*; and one line per gate with no input.

**The arm census is correct and `D6-GRADER-DEF-1` does not recur.** `O_mp` and `ACC_mp` `RAN`;
`F_mp` and `REF_off` are named `NOT_RUN` with reason `REGISTERED_CHAIN_STOPPED_AT_FIRST_NONZERO`,
stop arm `ACC_mp`, stop rc 124. `G1` fails on `ran_clean = false` (`ACC_mp` kernel rc 124) **and**
`all_arms_ran = false`. Total spend graded: **2,282.133 core-min** against a registered item ceiling
of 3,270.0.

Source: `D6RG_regrade.json` → `grade.gates`, `grade.not_a_result_reasons`, `grade.G1`, `grade.G10`.

# 3. The three findings carried forward — registered before execution, none softened

## 3a. `G-D6R-OPT` is `UNCLASSIFIED`, not `STALLED`

| quantity | measured |
|---|---|
| exit line | `EXIT: Invalid number in NLP function or derivative detected.` |
| majors | **73** of a registered `max_iter` **80** |
| restoration majors | **7** |
| alpha cutbacks | **673** = **9.2192 / major** against a registered stall threshold of 1.0 → **S1 TRUE** |
| dual infeasibility, tail start (major 66) | **9.23e-04** |
| dual infeasibility, last (major 73) | **9.00e-04** → **S2 FALSE** — it **fell** |
| `deadline_fired` | **false** (`rc = 0`, container 33,794 s against a 43,410 s deadline) |

The registered ladder is `DEADLINE > STALLED > ITERATION_CAP > CONVERGED`, and `STALLED` requires
**both** S1 and S2. **The line search was failing badly and the dual infeasibility was still
improving**, which is neither a stall nor a cap hit nor convergence. The frozen ladder's own residual
label is `UNCLASSIFIED`, and `compose()` maps that to `NOT A RESULT` — never `PASS`.

## 3b. Predictions P1 and P8 both MISS

| prediction | registered | observed | score |
|---|---|---|---|
| **P1** | outcome in `{ITERATION_CAP, STALLED}`, **point** `STALLED` | `UNCLASSIFIED` | **`MISS`** on point **and** band |
| **P8** | *the repair's own falsifier: the chain COMPLETES — all four arms run* | `STOPPED_AT_FIRST_NONZERO`, `F_mp` and `REF_off` never ran | **`MISS`** |
| P5 | `O_mp` cost in [1900, 2900] core-min, point 2500.6 | **2,257.933** | `HIT` |
| P7 | no OOM kill at np = 4 in a 20g cgroup | `any_oom_killed = false` | `HIT` |
| P2, P3, P4, P6 | — | inputs never produced | `NOT A RESULT` ×4 |

**P8 was written as the repair's own falsifier and it fired.** D6R's registration predicted that the
optimiser's `max_iter` would bind before the container deadline so the arm would exit `rc = 0` and
the chain would continue. **It did exit `rc = 0` — and the chain still stopped**, one arm later, at
`ACC_mp`. The predicted mechanism worked and the predicted *outcome* did not.

Every score above is the **frozen** `score_predictions()`'s own; D6RG scored nothing.

## 3c. `G10 GATE FAIL` — `D6R-CAP-FRAME-2`, a third candidate defect

| arm | core-min | cap | within cap | host wall s | container wall s | frame gap s | gap ≤ 30 s |
|---|---|---|---|---|---|---|---|
| `O_mp` | 2,257.933 | 2,900.0 | **yes** | 33,869 | 33,794 | **75** | **NO** |
| `ACC_mp` | 24.200 | 30.0 | yes | 363 | 363 | 0 | yes |

`G10`'s frame limb allows `FRAME_ALLOWANCE_S(90) − KILL_GRACE_S(60) = 30 s` between the host bracket
and the container's own kernel clock. **`O_mp` used 75 s** — and it was comfortably **inside its
cap**, at 77.9 % of 2,900.0. The gate fails on **bookkeeping frame accounting, not on spend.**

**The cause is measurable and is stated as a hypothesis, not a finding:** `O_mp` wrote a **12.7 MB**
log where `ACC_mp` wrote 100 kB, and the 75 s sits in the host-side frame around a container that had
already stopped. **The 30 s allowance is under-registered for a log of that size.**

**This is reported and deliberately NOT repaired here.** Widening a registered allowance is a gate
change; it needs its own registration. Recorded as **`D6R-CAP-FRAME-2`**, successor to
`D6-CAP-FRAME-1`/L-371.

# 4. The birth requirement — both directions, on the real frozen grader

A repaired reader's entire risk is that it **launders a genuine absence into a reading**, so the
must-flag direction is the point. **All 27 units passed under `python3` and under `python3 -O`, with
`__pycache__` cleared before each.** Ten plants travelled the **real** frozen `grade()` over the
**real** preserved artefacts; none ran in a mock.

| unit | direction | plant | clause that fired |
|---|---|---|---|
| U4 | must-NOT-flag | none — D4's real complete log | **read by the ORIGINAL summary-line path**; every consumed key equal to the frozen reader's own return |
| U5 | must-NOT-flag | none — D6R's real log | recovered `2.2238800e-02` from major 73, `provenance = ITERATION_TABLE_ROW`, 8 printed figures |
| U9 | **must-FLAG** | every major row removed, tail intact | `repair_declined_no_iteration_table` |
| U10 | **must-FLAG** | truncated after major 40, tail gone | `repair_declined_no_exit_line` |
| U11 | **must-FLAG** | majors 68–73 deleted, tail still reports 73 | `repair_declined_iteration_table_torn` |
| U12 | **must-FLAG** | last objective → `nan` | `repair_declined_iteration_table_torn` — **the clause registered in advance**, see below |
| U13 | **must-FLAG** | last objective → `1e999` (floats to `inf`) | `repair_declined_recovered_objective_not_finite` |
| U14 | **must-FLAG** | `nlp_scaling_method` `none` → `gradient-based` | `repair_declined_nlp_scaling_method` |
| U15 | **must-FLAG** | `EXIT:` → an unregistered non-optimal exit | `repair_declined_exit_not_registered` |
| U16 | **must-FLAG** | `EXIT:` deleted, table intact | `repair_declined_no_exit_line` |
| U17 | **must-FLAG** | `Number of Iterations` deleted | `repair_declined_number_of_iterations_absent` |
| U18 | **must-FLAG** | hole at majors 30–35, both ends intact | `repair_declined_iteration_table_not_contiguous` |

**Every refusal is the FROZEN module's own `refuse()`**, so no new refusal vocabulary exists.

**U12's clause was named before it was run, not explained after.** The frozen `MAJOR_ROW_RE`
objective class is `[-+0-9.eE]+` and **cannot express `nan`**, so a `nan` objective makes the row
stop matching and the refusal lands on the **torn-table** clause. The requirement — *refuse, never
coerce* — holds; the clause does not. **It is U13, not U12, that proves there is no silent
coercion**, because `1e999` is expressible in that same class and floats to `inf`.

**U11 is the dangerous shape and it is the one worth reading twice.** The tail still reported 73
iterations while the table stopped at 67. A reader that trusted its last readable row would have
published **major 67's intermediate objective as the endpoint** — a wrong number wearing the right
label. It refused.

## 4a. Rule 3, driven here because the frozen grader could not drive it

The frozen `g_price` short-circuits when `F_mp` did not run, so **D6R's own planted-zero control
never fired on this data** — confirmed by the absence of any `grader_controls/` directory after the
§1a drive. D6RG therefore drove the **frozen** `planted_zero_control` **through the repaired reader**
on D4's reference (U7): the planted **1.234e-03** was **seen** to within 1e-12 and the unperturbed
negative control moved by **exactly 0.0**.

**And the control's independence is measured, not assumed** (U8): the frozen `planted_zero_control`
binds its reader in `__defaults__` at def time, so **D4's reference control still travels the
ORIGINAL frozen code after `read_ipopt` is rebound**. U8 asserts the original is in `__defaults__`
and the repaired one is not, *after* the rebind.

## 4b. What the repaired reader may not do, and what its number is worth

* It **did not invent an objective**. The endpoint was recovered from the iteration table **in the
  file**, and U6 confirms it by an **independent path** — scanning the preserved log's own lines for
  major 73 yields the same token, `2.2238800e-02`.
* **Its provenance is the iteration row and NOT the summary line, and those are different claims.**
  The table prints **8** significant figures; the summary the frozen reader wants prints **17**. The
  recovered value carries the table's precision.
* The table's single objective column was equated with the summary's *unscaled* column **only on a
  setting read from the file** — `nlp_scaling_method = none`, present at line 13 of **both** D6R's
  and D4's logs (U3). U14 proves the reader refuses when that setting is anything else.
* **The recovered number decided nothing.** `g_opt_outcome` consumes only `exit` and `optimal`; it
  never reads `objective`. The value is **reported, not gated** — stated so no later reader mistakes
  it for an input to a verdict.

# 5. The preserved roots were not mutated — read from the disk, not from git

| root | regular files | manifest before == after |
|---|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint` | **14,546** | **identical** |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O` | **5,085** | **identical** |

Every regrade ran on a `cp -a` copy. The check is an **md5 manifest of every regular file**, taken by
walking the disk. **A git-based cleanliness check would be blind to exactly the thing being
protected**, because a run root is not in git. Between plants the single file under test was restored
from a pristine byte copy and its md5 re-verified against the preserved original, so every plant
started from the real file (U27, and `PREREGISTRATION.md` §5 registers why the manifest is taken once
around the whole execution rather than around each of eleven regrades).

# 6. The frozen files were never edited — proved by hash, not asserted

| frozen file | registered md5 | on disk | `git cat-file blob HEAD:<path>` |
|---|---|---|---|
| `curriculum_D6R/d6r_grade.py` | `bc8e9fec48b3f58ce7a96f4b9549590b` | **same** | **same** |
| `curriculum_D6R/PREREGISTRATION.md` | `e525084daac50c82738170925894fbe1` | **same** | **same** |

Rule 2 taken in **both** directions on **both** files, at execution, by the comparator itself
(`check_frozen_files()`), and the blob read from the **commit** rather than from a value typed into a
document.

`bc8e9fec…` is the value **after D6R's AMENDMENT 1** — the one `D6R_chain_wait.json` carries as
`grader_md5_post_amendment`. **L-370 false-drift trap:** the pins at D6R's `PREREGISTRATION.md`
§7:414 and §8:478 are **pre-amendment**, and a check that stops there reports a false `GATE FAIL`.

D6RG's own instruments carried their frozen md5s unchanged from the freeze commit into the recorded
execution: `d6rg_grade.py` `14356162837faece73acf40b323927c9`, `d6rg_reader.py`
`61bb9dbe1adab6e9b2cdb3a13f53cff1`.

# 7. Cost — actual against the frozen estimate (rule 12)

**Solver compute: ZERO core-minutes.** No mesh, no solve, no container, no GPU.

| | |
|---|---|
| Registered estimate (`PREREGISTRATION.md` §11) | **1.50 core-min**, ranks = 1 |
| Cap | **5.00 core-min** |
| **Actual, recorded execution** | **0.320 core-min** = 9.7 s + 9.5 s at ranks 1, **MEASURED** by the instrument's own wall clock across both interpreters |
| **ratio actual / predicted** | **0.213** |
| Dollars, actual | **$0.000274 DERIVED, NOT MEASURED** (0.005333 core-h × $0.0513/core-h) |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Overrun | **none.** 6.4 % of the cap |

**Attribution of the gap, and it is not efficiency.** The estimate assumed a **cold page cache** for
four md5 manifests totalling ≈ 3 GB; a cold manifest of the D6R root measured **14.34 s**, a warm one
≈ 2 s. The cache was warm from the §1a drive, so the manifests cost about a seventh of what was
priced. **The prediction was right about the work and wrong about the cache state.** Attributed to
**misprediction**, not to contention and not to waste; **zero waste** is claimed and none was
observed.

**Lane-level compute beyond the item**, stated separately so it is not absorbed into the ratio: the
§1a frozen-grader drive (14.34 s cold manifest + 1.06 s `cp -a` + a sub-second refusal + a second
manifest ≈ 30 s) and four development runs (≈ 45 s) ≈ **1.25 core-min DERIVED** from those measured
components — **not a single measured total**, and labelled so. Lane total ≈ **1.6 core-min**, inside
the 5.00 cap.

A calibration row is owed in `docs/COST_CALIBRATION.md`, with its id re-derived at commit time from
the tail as the maximum existing number (rule 11).

# 8. What this item establishes, and what it does not

**Establishes.** `D6R-GRADER-DEF-2` is real, reproduced through the frozen code with a control, and
repairable by one reader without touching a gate. D6R's verdict is `NOT A RESULT` **with eleven gate
readings behind it** rather than none. `D6-GRADER-DEF-1` is genuinely repaired in `d6r_grade.py` and
did not recur. `O_mp`'s optimiser outcome is `UNCLASSIFIED`. `G10` fails on `O_mp`'s frame gap.
2,257.933 core-min of `O_mp` compute that had produced **no reading at all** now produces one.

**Does not establish.**

* **Nothing about WHY the primal returns non-finite values at trial geometries.** D6R's §6 declines
  that and prices it separately; **this item did not open it**, and the 673 alpha cutbacks and 7
  restoration majors are reported as *what the log says*, not as a diagnosis.
* **Nothing about `ACC_mp`, `F_mp` or `REF_off` beyond the frozen census.**
* **No new gate, threshold, band, cap or label.** All are D6R's own.
* **Nothing about the physics, the mesh or the solver.** No solver ran.
* **`D6R-CAP-FRAME-2` is named, not repaired.**

# 9. Disclosed rather than patched

1. **The shared git index carries 489 staged deletions** across every team, including
   `curriculum_D6R/d6r_grade.py` and `curriculum_D6R/PREREGISTRATION.md`. Every one of those files is
   present on disk and present in `HEAD`; **the deletion is staged only.** It was **inspected and NOT
   reverted** (rule 10: the index is the chief's call) and is reported upward. **A bare `git commit`
   by anyone would land it.** D6RG is unaffected: it commits by the private-index protocol, which
   `read-tree`s from `HEAD`, and its rule-2 check reads the **commit**, not the index.
2. **This is not an outcome-blind freeze and does not claim to be** (`PREREGISTRATION.md` §9). The
   instrument was exercised during development. What the freeze bought is the repair semantics, the
   registered non-finite exit set, the seven refusal gates, the rebind audit, the unit count, the
   both-directions controls, **the U12 clause note** and the three carried-forward findings.
3. **The `REPORTING_CHARTER` heading conflict** is stated at the head of this file and referred
   upward rather than resolved silently.

# 10. What is owed, and to whom

* **To the supervisor:** a ruling on `D6R-CAP-FRAME-2` — whether the frame allowance is re-registered
  for large logs, and by whom. Widening a registered allowance is **not** this lane's call.
* **To `docs/COST_CALIBRATION.md`:** one row, id re-derived from the tail at commit time.
* **To Sanaa, and to no agent:** nothing here is sent, filed, uploaded, registered, posted or
  commented outside this box.

# 11. Artefacts, all still on disk

| artefact | path |
|---|---|
| pre-registration (frozen `5563f785`) | `cases/dafoam/ladder-a/A2/curriculum_D6RG/PREREGISTRATION.md` |
| successor comparator | `cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_grade.py` |
| repaired reader | `cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_reader.py` |
| re-grade record | `cases/dafoam/ladder-a/A2/curriculum_D6RG/D6RG_regrade.json` |
| selftest evidence, both interpreters | `cases/dafoam/ladder-a/A2/curriculum_D6RG/d6rg_selftest_evidence.txt` |
| preserved run root (never written) | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint` |
| D4 reference root (read-only) | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O` |
| frozen predecessor | `cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_grade.py`, `.../PREREGISTRATION.md` |

**No path above is a scratch path** (L-186).
