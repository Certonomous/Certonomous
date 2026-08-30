# Curriculum item SO-1a — NACA0012 drag-min at fixed lift, the FD-verified gradient rung: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-30 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-1a never landed one: its own grader refused, and a refusal wrote no record.
**This is the sweep's most consequential verdict and the one routed to `verification-supervisor`, and
until today a reader who came to this item's directory found nothing at all.**

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no artefact was written, no preserved run root was touched, and **zero solver
> core-minutes were spent.** Every verdict, gate reading, band, hash, count, percentage and refusal
> string below is **copied verbatim from an existing frozen artefact and cited to it by path and by
> JSON key or line.** Where a figure a reader might want is **not** on record, this document says so
> and says where a reader would have to go — it does not supply one.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the morning
> report's**, matched literally so that a document carrying them *is* a morning report; a curriculum
> record wearing `## 5. REFILLED QUEUE` would be a malformed one. This record follows the family's own
> convention — `curriculum_SO1aR/RESULTS.md`, `curriculum_AV1/RESULTS.md`.

---

# 1. Item verdict

> # SO-1a: **`GATE FAIL`**
> ## SHIPPED row **`GATE FAIL`** · PATCHED row **`PASS`**
>
> # **THE ITEM VERDICT IS `GATE FAIL`. IT IS THE WEAKEST LINK, AND THE PATCHED `PASS` DOES NOT CARRY THE ROW.**
>
> **A reader may not take the `PASS` away without the `GATE FAIL`.** The two-row rule requires both
> rows, and the SHIPPED row — the toolchain DAFoam actually ships — is genuinely broken on this
> gradient. Any downstream claim resting on the PATCHED row must travel with the SHIPPED row's
> `GATE FAIL` attached to it.

| | |
|---|---|
| **ORIGINAL, by this item's own frozen grader** | ~~**`NOT A RESULT`**~~ — **struck as superseded for the run, and NOT struck as a fact about this item's own frozen path** |
| **CURRENT, by the successor `SO-1aR`** | **`GATE FAIL`** (split, above) |

## 1.1 THE ORIGINAL REFUSAL, QUOTED IN FULL — this item refused first, and on what

SO-1a's own in-chain grading on 2026-08-28 returned `NOT A RESULT` **with ZERO gates evaluated**.
Verbatim from
`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/SO1a_grade_20260828T023132Z.json`
(keys `verdict`, `refusal`):

    "verdict": "NOT A RESULT"
    "refusal": "{\"REFUSE\": \"G1\", \"detail\":
                 {\"C5_fatal_token_in_arm_output\": [\"Floating point exception\"],
                  \"arm\": \"MESH\",
                  \"log\": \"MESH_20260828T021739Z_1709267.log\",
                  \"note\": \"a fatal token refuses at ANY rc; R-RC never launders a crash\"}}"

**The cause, as it is already recorded and NOT as this lane diagnosed it.**
`docs/COST_CALIBRATION.md` row `C-205` states it: *"`so1a_grade.py:122-125` held the bare substring
`Floating point exception`; `:420` appended `checkMesh.log` to the C5 haystack; line 18 of that
artefact is OpenFOAM's `trapFpe:` ENABLEMENT BANNER"*. **The refusal was a false positive on a setup
banner, not a crash** — and `curriculum_SO1aR/RESULTS.md` §10 records that the single offending line
now appears in the successor's output as a **counted, reasoned exclusion**: *"MESH scanned
`MESH_20260828T021739Z_1709267.log` and `checkMesh.log`; 1 benign line excluded — `checkMesh.log:18`,
token `Floating point exception`, reason 'OpenFOAM sigFpe SETUP banner — an ENABLEMENT NOTICE, not a
crash'"*, with **0 exclusions and 0 sites on all four solver arms.**

**All five arms had run to completion.** The refusal was never about the solve.

## 1.2 THE CURRENT VERDICT AND WHAT PRODUCED IT — a SUCCESSOR, and SO-1a's frozen grader was NOT edited

| | |
|---|---|
| successor item | **`SO-1aR`** — `cases/dafoam/ladder-a/A1/curriculum_SO1aR/` |
| its pre-registration freeze | **`bf5aec13fe28a24cdd7dc6e5b72747712415ad93`**, committed **2026-08-28T17:14:07Z**, before the graded run |
| the successor's comparator | `so1ar_grade.py`, md5 **`d2051f59089f3e71ae0fbfa315c3b784`** — checked **three ways** immediately before the run (worktree, the freeze commit `bf5aec13`, `HEAD`), all identical and all equal to the md5 registered at `curriculum_SO1aR/PREREGISTRATION.md:163` |
| verdict artefact | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/SO1aR_grade_20260828T171830Z.json` |

**No frozen SO-1a file was edited.** `curriculum_SO1aR/RESULTS.md` §1 and §11 both state it, and §11
adds that no SO-1b or SO-1c frozen file was edited either.

> **AN IMPORTANT DIFFERENCE FROM THIS FAMILY'S OTHER RE-GRADES, STATED RATHER THAN GLOSSED.**
> `AVWC` and `AV2RG` ran their predecessors' **own** frozen `grade()` with at most one name rebound,
> so their verdicts are literally the frozen instruments' own. **SO-1aR is not that.** It is a
> **separate comparator**, `so1ar_grade.py`, with its own frozen pre-registration and its own registered
> C5 repair — SO-1a's `so1a_grade.py` is untouched and, on SO-1a's own frozen path, **still refuses.**
> The `GATE FAIL` above is the verdict on the **preserved artefacts**, reached by a successor
> instrument. That distinction is the reason §8 below is not optional.

# 2. THE GATE TABLE — copied from the grade JSON

All keys under `SO1aR_grade_20260828T171830Z.json` in the preserved run root.

| gate | verdict | number on record | key |
|---|---|---|---|
| **G-BIRTH** | **`BORN`** | 12 legs, 12 born, 0 unborn; **1 reader named NOT BORN and BARRED** (`B3`) | `birth` |
| **G1** completion | **`PASS`** | all five rule-4 clauses PASS on all five arms | `rule4_clauses_per_arm` |
| **G-M2** mesh identity | **`PASS`** | cells **4,032**, exactly as registered | `mesh_cells` |
| **G5_SHIPPED** (`CD`) | **`GATE FAIL`** | 5 graded, **3 PASS, 2 GATE FAIL, 1 sign flip**; aggregate **40.481353490548585 %**; `band_D` GATE FAIL, `band_E` GATE FAIL | `gates.G5_SHIPPED.G5_CD` |
| **G5c_SHIPPED** (`CL`) | **`GATE FAIL`** | 5 graded, **4 PASS, 1 GATE FAIL**, 0 sign flips; aggregate **4.326953773474209 %**; **`band_E` PASS, `band_D` GATE FAIL** | `gates.G5_SHIPPED.G5c_CL` |
| **G5_PATCHED** (`CD`) | **`PASS`** | **5 of 5**, 0 sign flips; aggregate **0.06229708524522306 %** | `gates.G5_PATCHED.G5_CD` |
| **G5c_PATCHED** (`CL`) | **`PASS`** | **5 of 5**, 0 sign flips; aggregate **0.021237769014679053 %** | `gates.G5_PATCHED.G5c_CL` |
| **G-TB** SHIPPED | **`PASS`** | **0 of 5** components pass band D at the deliberately wrong step (max allowed 1) | `gates.G_TB_SHIPPED` |
| **G-TB** PATCHED | **`PASS`** | **0 of 5** at the wrong step | `gates.G_TB_PATCHED` |
| **G6** duality | **NOT MEASURED** | the tutorial exposes no dot-product test; named, never composed | `gates.G6_dot_product_duality` |
| **G9** toolchain | **`PASS`** | both rows by DIGEST + printed `.so` md5 + in-artefact `.so` md5; **no version string** | `gates.G9_toolchain` |
| **G10** caps | **`PASS`** | every row under its cap; total **9.416** ≤ **75.0** | `gates.G10_caps` |
| **G12** placement | **`PASS`** | `cpuset = 9` on every row | `gates.G12_placement` |
| GCI | **NOT QUOTED** | *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"* | `no_gci` |

**`rc = 0`. No refusal** (`refusal` is absent from the successor's JSON). **Where SO-1a evaluated ZERO
gates, SO-1aR evaluated all of them.**

# 3. THE BRIGHT LINE, PER COMPONENT — and this is where the split lives

`rel_err_pct`, adjoint against the central-FD reference; **band D = 5.0 %** per component, band E on
the aggregate. Copied component by component from `gates.G5_SHIPPED` and `gates.G5_PATCHED`.

| component | SHIPPED `dCD/dx` | SHIPPED `dCL/dx` | PATCHED `dCD/dx` | PATCHED `dCL/dx` |
|---|---|---|---|---|
| `shape[0]` | **11.9330 % — `GATE FAIL`** | 0.3376 % `PASS` | 0.0124 % `PASS` | 0.0048 % `PASS` |
| `shape[3]` | 4.0498 % `PASS` | 0.5928 % `PASS` | 0.0420 % `PASS` | 0.0093 % `PASS` |
| `shape[6]` | **637.7570 % — `GATE FAIL`, SIGN FLIPPED** | **19.8033 % — `GATE FAIL`** | 0.6992 % `PASS` | 0.0876 % `PASS` |
| `shape[7]` | 1.8798 % `PASS` | 0.9307 % `PASS` | 0.1449 % `PASS` | 0.0171 % `PASS` |
| `patchV[1]` | 0.0144 % `PASS` | 0.0124 % `PASS` | 0.0144 % `PASS` | 0.0124 % `PASS` |
| **aggregate (band E)** | **40.4814 %** | **4.3270 %** | **0.0623 %** | **0.0212 %** |

**Baselines, identical on both rows to every printed digit:** `CD = 0.02091051000679216`,
`CL = 0.49876526415423195`; primal repeatability `eta = 3.714203840321506e-10`
(`curriculum_SO1aR/RESULTS.md` §3.2).

## 3.1 TWO HONEST CAVEATS ON THE SHIPPED ROW, carried over rather than left to be found

Both are `curriculum_SO1aR/RESULTS.md` §5.2's, quoted:

1. **`shape[3]` PASSES at 4.0498 % against a 5.0 % band — 0.95 percentage points from failing.**
   Counting it as "3 of 5 pass" without that number would flatter the shipped toolchain.
2. **`G5c_SHIPPED`'s aggregate is 4.3270 %, INSIDE band E**, yet the row is `GATE FAIL` because
   `shape[6]` breaches **band D**. **The aggregate alone would have passed this row.** Both bands are
   registered and both are printed, so the favourable aggregate could not become the story.

# 4. THE FD / BRIGHT-LINE STATUS OF THIS ITEM — stated honestly

**This item DOES carry an FD table**, unlike its AV siblings: the reference is a central finite
difference and the bright line is `G5`/`G5c`. Two things make that table load-bearing rather than
decorative, and both are copied from the record:

* **The trivial baseline earns the gate.** At the deliberately wrong step (`h = 1e-8` for `shape`,
  `1e-6` for `patchV`), **0 of 5 components pass band D on either row**, against a registered maximum
  of 1. The comparator's own words in the JSON: *"the trivial baseline FAILS as registered, so the FD
  gate is measuring the step."* **The gate can fail, so its PASS means something.**
* **`dCL/dx`, the EQUALITY-CONSTRAINT gradient, is FD-verified on A1 for the first time by this run**
  (`curriculum_SO1aR/RESULTS.md` §4). SO-1 is drag-min at fixed lift, so `CL` is an equality constraint
  (`so1a_runScript.py:174`); prior A1 records verified `dCD/dx` alone. **The PATCHED row carries
  `dCL/dx` PASS 5 of 5 at 0.0212 % aggregate, and the SHIPPED row is shown to FAIL it** at `shape[6]`,
  19.8033 %.

**Roache / GCI: none, and none is quoted.** `no_gci` verbatim: *"no grid family; standing rule 5 has no
row; NO GCI IS QUOTED"*. There is no mesh-convergence study and no grid triple for this item.

> **A CROSS-REFERENCE A READER OF THE FD TABLE IS ENTITLED TO, RECORDED AND NOT RULED HERE.**
> `cases/dafoam/ladder-a/A_stepsize_study.md` excludes **`idx0`** from its five-of-eight FD plateau
> (`:45-46`) and says of **`idx6`** that *"there is no step at which idx6 is a trustworthy estimate"*
> (`:40`). Those are exactly the two components that fail SO-1a's SHIPPED row.
> `curriculum_AV2RG/RESULTS.md` §5 already sets SO-1aR's `shape[0]` and `shape[6]` readings beside
> that study in one table.
> **What this means for SO-1a's own FD table has NOT been ruled.** The supervisor's per-component
> plateau split (`curriculum_AV2RG/PREREGISTRATION.md` §A1.4, Ruling 1 of 2026-08-30) was registered
> **for AV-2R**, and no ruling on record extends it to SO-1a. **This lane does not extend it** — it
> records the tension and leaves the ruling where it belongs. A reader weighing the SHIPPED row's
> `GATE FAIL` should know that the FD reference for those two components is itself contested
> elsewhere in this family.

# 5. THE REPAIR DID NOT FLATTER — the evidence that entitles the split verdict

The objection a repaired-reader sweep must answer: **a repaired false-negative reader can only move a
verdict in the flattering direction, and that is exactly the direction that invites bias.**

**This one did not flatter. It turned a zero-gate refusal into a `GATE FAIL`, not a `PASS`.**

And the withholding is **demonstrable rather than asserted**, because **the same instrument, on the
same run, in the same invocation, DID reach `PASS` — the PATCHED row got one, on both objective and
constraint.** So the SHIPPED row's `GATE FAIL` is not an instrument that *cannot* say PASS; it is one
that **could** say PASS and **declined to**, component by component
(`curriculum_SO1aR/RESULTS.md` §3.3).

**The birth gate opened before any gate was read:** `BORN`, **12 of 12 legs, 0 unborn** — and `B3` is
recorded in the output as **NOT BORN and BARRED**, which is a stronger statement than "unused":
*unused is a fact about this run, barred is a rule about any run*. **No graded number on this record
came through an unborn reader.**

**Rule 3, plant-the-zero, satisfied inside the instrument that issued the verdict**
(`curriculum_SO1aR/RESULTS.md` §10): grader-level plant `grader_plant_seen = true` on both rows, **15
values each**, worst residual **6.51e-19**; and the producer-written plant (birth leg B9) reads exactly
**`0.617 = PLANT/(2·ctrl_step)`** on both rows while its unplanted twin reads **`0.0`** — **the reader
was shown seeing a non-zero and a zero from the same file through the same code path.**

**The mechanism is localised, and that is what makes the claim falsifiable**
(`curriculum_SO1aR/RESULTS.md` §5.2). Shipped-versus-patched divergence on the adjoint `dCD/dx`,
**reported and never gated**: `shape[0]` 10.650 %, `shape[3]` 4.010 %, **`shape[6]` 118.726 % with the
sign opposite**, `shape[7]` 1.737 %, and **`patchV[1]` exactly 0.000 %** — `patchV` perturbs the
boundary condition, never passes through IDWarp's warping path, and agrees to every printed digit.
**The defect is localised to the mesh-warping path and is not a global adjoint error.** No optimisation
gain is claimed anywhere; no optimiser ran.

# 6. THE PREDICTIONS WERE SCORED, NEVER ADJUSTED — including one that predicted this failure in writing

`curriculum_SO1aR/RESULTS.md` §6 records **SO-1aR's own three all HIT** (`R1` completion, `R3` cost
≤ 1.0 core-min, `R4` no component refused for a missing FD plateau — **0 refusals, all 20
component-objective readings graded**), and **all ten carried by citation from SO-1a's own pre-compute
freeze of 2026-08-27 HIT**.

**The one worth naming here is `P5`:** SO-1a's frozen text, committed before the compute, predicted
that the SHIPPED row's **`shape[6]` would be outside band D or sign-flipped**. **It measured both** —
637.7570 % **and** a sign flip. **That is the inverse of a gate fitted to an answer: an answer arriving
where the gate said it would**, and the sign-flip rule was itself registered, so the 637 % is caught by
a **registered rule** and not by an ad-hoc judgement about a large number.

# 7. Cost — rule 12

**SOLVER COMPUTE BOUGHT BY THE RE-GRADE: ZERO core-minutes.** `curriculum_SO1aR/RESULTS.md` §7 records
the line *"solver compute bought by this item: 0.000 — no container started, no queue entry"*, and §11
adds that `verification/queue/` was not opened, read or written.

| line | ranks | wall | core-min | basis |
|---|---|---|---|---|
| the successor's graded run | 1 | 0.160 s | **0.0027** | **MEASURED** |
| successor instrument spend to the freeze | 1 | 1.966 s | **0.0328** | **MEASURED**, `curriculum_SO1aR/so1ar_grade_selftest_evidence.txt` |
| **SO-1aR instrument TOTAL** | | | **≈ 0.036** | against a **1.0** core-min cap — **3.6 %** |

**Dollars for the re-grade: 0.036 core-min = 0.0006 core-h × $0.0513/core-h = $0.00003 — DERIVED, NOT
MEASURED.** `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). No GPU.

**Calibration row for the instrument: `C-206`** (2026-08-28, dafoam).

**SO-1a's OWN SOLVER SPEND, which is NOT re-charged to the re-grade: 9.416 core-min** against a
predicted **7.367**, ratio **1.2781**, **calibration row `C-205`** (2026-08-28, dafoam). Per arm,
actual from `ledger.txt`: MESH **0.183** · X-S **1.017** · F-S **3.583** · X-P **1.200** · F-P
**3.433**. **Gap attributed to CONTENTION, measured not inferred** — the two overrunning arms are
exactly the two that ran beside siblings, with cgroup throttle counts **F-S 68** and **F-P 42** against
quiet **X-S's 5**, and **X-S came in UNDER estimate at 0.925**, which is the control that makes the
contention reading falsifiable. **No waste was observed and none is folded into that ratio.**

> **`C-205` states plainly why it is late, and it is a fact about this item:** SO-1a's grader refused,
> so rule 12's comparison could not be made at its own completion — there was no graded verdict to
> compare a cost against. **The defect cost this lab a verdict AND its bookkeeping.**

# 8. WHAT THIS RECORD MAY NOT BE READ TO SAY

Carried by citation from `curriculum_SO1aR/RESULTS.md` §9 and `PREREGISTRATION.md` §8, restated
against the actual outcome:

1. **NOTHING about reproducibility.** One chain, one night. The PATCHED row's `PASS` is a statement
   about **that run**.
2. **NOTHING about the mesh beyond identity.** `G-M2` checked 4,032 cells against a registered number.
   **No mesh-convergence study, no Roache triple, NO GCI** (rule 5) — the comparator says so in its own
   `no_gci` field.
3. **NOTHING about np > 1.** Every arm is np = 1. A4's measured 16,600× decomposition effect is
   *removed from the chain*, not shown absent.
4. **NOTHING about the launcher.** The artefacts came from SO-1a's infrastructure; neither item
   re-verifies or re-certifies it.
5. **SO-1a's OWN INSTRUMENT IS NOT REHABILITATED.** `curriculum_SO1aR/RESULTS.md` §9.5 puts it
   flatly: *"SO-1a is `NOT A RESULT` permanently. Two records, one run."* **On SO-1a's own frozen path
   `so1a_grade.py` refuses, and it still refuses today.** The `GATE FAIL` in §1 is the verdict on the
   **preserved artefacts** by a successor instrument. **A reader who needs to know what SO-1a's own
   code returns must read §1.1, not §1.**
6. **No optimisation gain is claimed.** No optimiser ran. §5 gives a mechanism, not an improvement
   percentage.
7. **`GATE FAIL` is the ITEM verdict and it is NOT a failure of the PATCHED toolchain.** The item fails
   because the two-row rule requires both rows and the SHIPPED row is genuinely broken. **The PATCHED
   row is `PASS` on both objective and constraint — and it does not carry the item.**
8. **The birth battery certified READERS, not PHYSICS.** `BORN` means each reader was shown seeing a
   non-zero through the real path. The gates are what speak to the gradients.

# 9. What is downstream, and whose call it is

* **`SO-1b` DOES NOT LAUNCH AS FROZEN — ruled 2026-08-28** (`curriculum_SO1aR/RESULTS.md` §11). Its
  precondition is satisfied **in substance** (`gates.G5_PATCHED` exists and reads `PASS`), but SO-1b as
  frozen reads `SO1a_grade_*.json` and **cannot see `SO1aR_grade_*.json`**. Launching it unchanged
  re-fires the same no-launch branch. **Forging the filename remains FORBIDDEN** — copying or
  symlinking the successor's output into SO-1a's filename inside a preserved run root would make a
  successor's verdict masquerade as the original's, which is artefact forgery.
* **The route is `SO1bR`**, a successor whose registered input is the SO-1aR grade JSON. **It is
  UNBUILT.** When it is built it must argue one thing explicitly rather than assume it: **SO-1b's
  precondition keys on the PATCHED row's `G5`, while the ITEM verdict is `GATE FAIL`.** Building a
  downstream rung on the `PASS` row of a `GATE FAIL` item is legitimate — the two-row structure exists
  precisely so the patched row can carry work the shipped row cannot — **but it must be stated and
  defended in that registration, and the SHIPPED row's `GATE FAIL` must travel with every downstream
  claim it makes.**
* **The `verification-supervisor` audit of the split verdict** is where this item's verdict is
  independently tested. This record does not pre-empt it.

# 10. The preserved run root was not mutated

`curriculum_SO1aR/RESULTS.md` §10 records an aggregate `md5sum` over `md5sum` of **every file** in the
run root, sorted, taken **before** the graded run and **after** it over the **identical file set**:

| | files | aggregate md5 |
|---|---|---|
| **before** 17:18:17Z | 337 | `073a520850452ad0acd6ba58aff2c4e3` |
| **after** the graded run | 337 | `073a520850452ad0acd6ba58aff2c4e3` |

> **IDENTICAL. Not one pre-existing byte changed.**

Added by SO-1aR and nothing else: `SO1aR_grade_20260828T171830Z.json`, its `.out`, and
`grader_controls_SO1aR/{F_S,F_P}_planted.json`. **No SO-1a file was opened for writing; SO-1a's own
`grader_controls/` path does not exist and was never created.**

**This lane wrote nothing into that root either**, and read from it only the two grade JSONs quoted
above.

# 11. WHERE THE FULL READINGS LIVE — this record is a signpost, not a duplicate

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/SO1aR_grade_20260828T171830Z.json`**
   — **the verdict artefact.** Every gate payload, every component `rel_err_pct` and `sign_flip`, the
   birth record, the controls, the rule-4 clauses per arm, the age-datum resolution, the predictions.
   **Note the location: this JSON is in the PRESERVED RUN ROOT, outside git — it is NOT in
   `curriculum_SO1aR/`.**
2. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/SO1a_grade_20260828T023132Z.json`**
   — the original refusal, quoted in §1.1.
3. **`cases/dafoam/ladder-a/A1/curriculum_SO1aR/RESULTS.md`** — §1 the frozen-path verification, §2 the
   birth gate, §3 the gate table and per-component bright line, §3.3 the did-not-flatter argument, §5
   the localisation, §6 the predictions, §7/§8 cost and calibration, §9 the limits, §10 the
   non-mutation proof and the C5 exclusion, §11 what is owed.
4. **`cases/dafoam/ladder-a/A1/curriculum_SO1aR/PREREGISTRATION.md`**, frozen `bf5aec13` — the gates,
   the registered C5 repair, the comparator md5 at `:163`.
5. **`cases/dafoam/ladder-a/A1/curriculum_SO1a/PREREGISTRATION.md`** — **this item's own frozen
   pre-registration, in this directory**, carrying the ten predictions of 2026-08-27 including `P5`.
6. **`docs/COST_CALIBRATION.md`** rows **`C-205`** (SO-1a, solver) and **`C-206`** (SO-1aR,
   instrument).
7. The preserved run root itself (337 files at the time of grading, outside git): `ledger.txt`, the
   five per-arm directories, solver logs, memory windows and per-arm `.inspect.txt` kernel records.

**If any figure in this record disagrees with the grade JSON, the grade JSON is right.**

# 12. What this record does and does not do

**It does** give SO-1a an item-level record where it had none, so that a reader who goes to the lab's
most consequential re-graded item finds its verdict, its split, and its original refusal instead of
nothing.

**It does not** re-grade anything, run any comparator, move any gate, threshold, band edge, cap or
label, score any prediction, or add any number that was not already written down in a cited artefact.

**It does not** revise what this item's own frozen instrument produced, and it does not let the
PATCHED `PASS` be carried away from the SHIPPED `GATE FAIL`.
