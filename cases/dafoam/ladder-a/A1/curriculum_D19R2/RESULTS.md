# CURRICULUM D19R2 — GRADING ATTEMPT 1: **NOT A RESULT**. A THIRD, INDEPENDENT BLOCKER, AND IT SITS IN A REGISTERED GATE

**Verdict of the attempt: `NOT A RESULT`.** The grader **refused**, `rc = 2`, and wrote **no grade JSON**. A refusal is `NOT A RESULT`, never a degraded verdict — that is the registered behaviour and it is what happened.

| | |
|---|---|
| grading path | `d19r2_grade.py`, md5 `817698f6c5e5059fcc9f757d99caff90` (== the §4 pin; re-asserted before the run) |
| freeze | `7441f392d608a4237934f00fb8e6be7065e033df` |
| run | `2026-09-01T03:44:16Z`, `--root .../CURRICULUM-D19R-a1-naca0012-subsonic-plateau` |
| stdout artefact | `/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau/D19R2_phase1_grade_20260901T034416Z.out` |
| grade JSON | **NOT WRITTEN** — the refusal precedes the emit |
| **cost, MEASURED** | **0.00096 core-min** (0.058 s wall × 1 rank ÷ 60) against a registered ceiling of 2.0 |
| solver core-minutes | **ZERO.** No arm re-run, no run root created, no container started |

**The two provenance blockers this item was built to repair are GONE.** The refusal is not at `G-PROV`; execution reached the completion gate, which is thirty lines past where D19R died. Blockers 1 and 2 are fixed and the fix held.

---

## 1. THE REFUSAL, VERBATIM

```
D19R2_GRADE REFUSED: {"REFUSE": "G19R-1h", "detail": {"age_guard": {
  "REFUSE": "MANIFEST_ENTRY_MUTATED", "detail": {
    "on_disk_md5":  "c3f5f05d45f0b9a70d645b107a837727",
    "path":         "system/decomposeParDict",
    "recorded_md5": "68ecc827562886fb43c3aedb0627b344"}}, "arm": "X2"}}
```

## 2. TRIAGE — THE GUARD IS RIGHT. THE MANIFEST PINS A PATH THE RUN WRITES

**Measured, not inferred:**

| reading | value |
|---|---|
| `X2/.d19r_manifest.json` built at | **22:55:55** (arm launch) |
| `X2/system/decomposeParDict` written at | **22:56:01** — **six seconds later, inside the arm's own run** |
| what changed | five lines APPENDED: `kahipCoeffs { config fast; imbalance 0.01; }` |
| everything else in the file | **byte-identical** |

That block is **OpenFOAM writing its own default coefficient sub-dictionary back into the dictionary it read** — ordinary `decomposePar` behaviour, not corruption and not tampering.

**Scope, measured across every arm and every manifest entry:**

| arm | ranks | manifest entries | mismatches |
|---|---|---|---|
| `MESH` | 1 | 17 | **0** |
| `X2` | 2 | 27 | **1** — `system/decomposeParDict` |
| `S8` | 2 | 27 | **1** — `system/decomposeParDict` |
| `N2` | 2 | 27 | **1** — `system/decomposeParDict` |
| `S1` | 1 | 27 | **0** |
| `R1` | 1 | 27 | **0** |

**Exactly one file, in exactly the three np = 2 arms.** The np = 1 arms are clean. Nothing else in 152 manifest entries moved.

**The guard is doing precisely its job.** `d19r_age_guard.py:207` already carries the refusal `MANIFEST_INPUT_IS_WRITE_TARGET` with the note *"a manifest may not pin a path the solver writes — that ..."*, and `X2`'s manifest already excludes `0` by name with a measured reason (*"DAFoam rewrites `0/U` … when the `patchV` DV updates the inlet BC"*). **The mechanism exists and is used. `system/decomposeParDict` simply is not on the excluded list, and at np = 2 it is a write target.**

## 3. THIS IS A **THIRD** BLOCKER, INDEPENDENT OF THE FIRST TWO — AND IT IS DIFFERENT IN KIND

`D19R-GRADER-DEF-1` was never the only thing standing between D19R's arms and a verdict.

| # | blocker | where it lives | fixable by a successor? |
|---|---|---|---|
| 1 | the provenance **enforcer** called as the first statement of `grade()`, on a literal `{}` | **wiring** | **yes — fixed** |
| 2 | the emit object carries neither `provenance` nor `verdict_statement` | **wiring** | **yes — fixed** |
| 3 | `G19R-1h`'s manifest pins `system/decomposeParDict`, which `decomposePar` rewrites at np = 2 | **a REGISTERED GATE** | **NO** |

**Blockers 1 and 2 were wiring, and wiring is exactly what a successor may repair.** Blocker 3 is not wiring: `G19R-1h` is registered as *"the input manifest byte-identical"*, and narrowing the manifest — by excluding `system/decomposeParDict`, or by any other route — **narrows what that gate checks**. That is moving a registered goalpost, which this item's own §3 forbids and which the successor route exists to avoid.

> **Had D19R's provenance wiring been correct, D19R would have refused HERE instead.** Its `g_completion` and its age guard are the ones this item imports. **D19R phase 1 could not have produced a verdict on these arms under any repair confined to its provenance call site.**

## 4. WHAT THIS LANE DID NOT DO, AND WILL NOT

* **Did not edit `G19R-1h`, the manifest, the excluded-write-targets list, or any threshold.** `shadow_sweep()` would refuse this module if it even *defined* such a constant, and it does not.
* **Did not re-run any arm.** Zero solver core-minutes, as registered.
* **Did not write a grade JSON.** The refusal precedes the emit, and no verdict exists to publish.
* **Did not retry with a relaxed reader**, which is the shape this whole family exists to refuse.

## 5. THE DECISION IS ABOVE THIS LANE — THREE ROUTES, NONE CHOSEN HERE

1. **Rule that `system/decomposeParDict` is a WRITE TARGET, not an input, for `G19R-1h`.** This is a **gate-design** question, and D19R's own §5 already reserves gate design to **Sanaa** in terms: *"Whether that is the right gate is a GATE-DESIGN question and gate design is reserved to Sanaa."* The evidence for such a ruling is measured and complete in §2 above.
2. **Re-run the three np = 2 arms with the dictionary pre-normalised** so the manifest holds. **This is new compute** and changes the cost picture, which this item registered as a stop-and-report condition.
3. **Accept `NOT A RESULT` for D19R phase 1** and record the finding, leaving the compressible gate shut.

**This lane recommends none of the three and takes none of them.** The measurement is complete; the ruling is not this lane's.

## 6. WHAT IS NOW KNOWN THAT WAS NOT

* D19R's arms are **intact and readable** — all nine inputs exist and parse, all three preconditions hold (`selector_saw_adjoint` `False`, `N2`/`R1` `grades_nothing` `True`).
* The provenance guard is **sound and shown able to return**, and the two wiring blockers are repaired and driven.
* **151 of 152 manifest entries across six arms are byte-identical** after five days — the completion gate's premise holds everywhere except one file that OpenFOAM itself rewrites.
* The compressible single-point gradient gate is **still shut**, and now for a **named, measured, single-file reason** instead of an unexplained `rc=2`.

## 7. COST

**Grading invocation: 0.00096 core-min MEASURED** (0.058 s wall × 1 rank ÷ 60) against the registered ceiling of **2.0** — ratio **0.00048×**. Dollars **DERIVED, not measured**, at `$0.0513/core-h` reported-by-owner: **$0.0000008**. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Zero solver core-minutes.** D19R's 12.416 core-min stays charged to D19R and is not re-charged here.

**The `docs/COST_CALIBRATION.md` row is OWED AT ITEM COMPLETION, and this item is not complete** — it has no verdict. Filing a calibration row now would be filing one for a process that has not finished.
