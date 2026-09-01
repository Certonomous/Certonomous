# D12RLX — PRE-REGISTRATION v1.0, PRE-COMPUTE. Does repairing the `Final` relaxation key move the D12 unsteady numbers, or is "no admissible FD step" a property of the method?

**FROZEN BEFORE ANY COMPUTE. NOT LAUNCHED. NOT QUEUED.** No run root exists, no container has
been started, no stage has run. **0 core-minutes spent.**

**Registered by** a dafoam lane, 2026-09-01, on the dafoam supervisor's authorisation, following
`cases/dafoam/FINAL_KEY_RELAXATION_EXPOSURE.md`.

**This item hands to the supervisor for the two §3 checks before it may be queued:** the grading
path re-derived independently, and the grader read as a diff. **Nothing launches until those are
done.** SUBMISSIONS PARKED; nothing here leaves the box.

---

## 1. §2b's CONDITION, STATED AND CHECKED

Rule 2 permits amendment before first compute and requires the condition be **stated and checked**,
naming the run directory that does not exist.

**Checked 2026-09-01, by this lane, by execution and not by assertion:**
`test -e /home/ubuntu/certonomous-runs/CURRICULUM-D12RLX-relaxation-paired` → **FALSE**. No
`d12rlx_` container has ever existed. No ledger and no manifest exist. **There is no answer to tune
to.**

## 2. THE QUESTION, IN ONE SENTENCE

`cases/dafoam/FINAL_KEY_RELAXATION_EXPOSURE.md` establishes **from source** that `U`, `nuTilda`,
`T`/`e`/`h` and `p` are assembled with no relaxation on the final PIMPLE outer sweep of every
timestep in every D12-family run, because the upstream tutorial's `relaxationFactors` block carries
no `Final` form. **It does not establish what that is worth in the numbers.** This item measures it.

**And it has a second job, which is the reason it exists in this form.** L-426's closing rule is
*"exercise each key, do not read it."* The source chain is **read**. This run **drives** it, and
converts airtight-by-construction into airtight-by-measurement.

## 3. THE TWO ARMS, AND WHAT IS AND IS NOT EDITED

**NO FROZEN FILE IS EDITED. NO `fvSolution` IS DELETED, MOVED OR REWRITTEN.** The repaired
dictionary is a **new file in a new directory**. The existing D12R2 run tree is untouched evidence.

| arm | dictionary | provenance |
|---|---|---|
| **C — control** | the upstream dictionary, md5 `95ab16a9141b0928bd352a9b9d8d93b9` | **already bought.** The landed `CURRICULUM-D12R2-cylinder-unsteady` artefacts ARE this arm. |
| **R — repaired** | the same file plus the four `Final` keys, and nothing else | new, staged into the new run root |

**Arm R's dictionary is arm C's with exactly this delta and no other change:**

```
relaxationFactors
{
    fields
    {
        "(p|p_rgh|G)"                             0.3;
        "(p|p_rgh|G)Final"                        0.3;      // ADDED
    }
    equations
    {
        "(U|T|e|h|nuTilda|k|omega|epsilon)"       0.7;
        "(U|T|e|h|nuTilda|k|omega|epsilon)Final"  0.7;      // ADDED
    }
}
```

**Explicit `Final` keys, not a `default` entry.** L-426: a `default` *"catches by accident what an
explicit key states on purpose."* Registered as a two-line diff so the comparison has exactly one
independent variable.

**The delta is asserted, not trusted.** Before arm R launches, the launcher must assert that arm
R's `fvSolution` differs from arm C's by **exactly the two added lines** (`diff` producing exactly
two `>` lines and zero `<` lines) and **REFUSE** otherwise. A second variable smuggled into the
dictionary would make every number below uninterpretable and is the failure this assert exists to
prevent.

## 4. THE PLANTED CONTROL, WHICH IS LOAD-BEARING AND RUNS FIRST

`δ_repeat = 0.0` is measured in arm C, so this solver is **bit-deterministic at np=1**. That makes
a strong control available and it is **registered as a gate, not an option**:

> **`G-RLX-0` — REPRODUCTION.** Before any cross-arm number is read, arm C's `S2b` stage is
> **re-run from its own unmodified dictionary** in the new run root. Its CD series must reproduce
> the landed series **bit-for-bit** — all 2,400 samples, and `δ_window(300)` identical to
> `0.0017958478225974517`. **If it does not reproduce, the item is `NOT A RESULT` and no cross-arm
> delta is reported**, because a delta between two arms is only attributable to the dictionary if
> the harness is shown to change nothing on its own.

**A cross-arm difference measured without this leg is not evidence.** It is the same requirement as
rule 3's planted zero, in the reproduction direction: a reader that has not been shown able to
return the SAME answer cannot be trusted when it returns a DIFFERENT one.

## 5. THE QUANTITIES, DECLARED IN ADVANCE, AND THE INSTRUMENT

**Graded by the LANDED instrument, not a new one.** Grading path:
`cases/dafoam/curriculum_D12R2/d12y_grade_w3.py`, md5
**`3950d30fd09c9b56213a02f5e9864e20`**, verified **identical on disk and from the HEAD blob**
2026-09-01. Its own `read_series`, `g2_delta_repeat`, `g3_delta_window` and `g4_delta_eff` compute
every noise term for both arms. **No new comparator is written for this item.**

Producer: `cases/dafoam/curriculum_D12R2/d12y_run_script.py`, md5
`2790c39a09cd458d5a3263d7f1811da5`, disk == HEAD, **unedited**.
Image: `dafoam/opt-packages:latest`, id
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` — the SHIPPED row, by
image id and never by tag.

**Arm C's registered baselines, re-derived by this lane from the artefact through that instrument
before freezing** (all reproduce the landed `step_plan.json` exactly):

| quantity | arm C value |
|---|---|
| CD mean, 2,400 samples | `0.6563231414421499` |
| CD peak-to-peak | `0.1316244994972485` |
| shedding period | `18.964426877470355` steps |
| `δ_window(W=300)` | `1.7958478225974517e-03` |
| `δ_pert` | `2.279666841643725e-06` |
| `δ_repeat` | `0.0` |
| `δ_eff` | `1.7958478225974517e-03` |
| `|g|` (`g_component_0`) | `1.0304158599180422` |
| `h_min` | `0.1742837908900481` (vs `h_max = 0.05`) |

**Note against the board:** `docs/LAB_STATE.md` quotes `|g| = 1.13984`. That is **W2R's value at
W = 900**, not D12R2's. This item's control is D12R2 at W = 300 and its `|g|` is
`1.0304158599180422`, read from `step_plan.json` and confirmed by
`h_min = δ_eff/(0.01·|g|) = 0.17428`.

## 6. THE PREDICTION, REGISTERED IN ADVANCE AND FREE TO BE WRONG

**The direction is registered. It may be wrong, and being wrong is the informative outcome.**

| # | prediction | band |
|---|---|---|
| **P1** | `δ_repeat` stays exactly `0.0` in BOTH arms — the repair does not break determinism | exact |
| **P2** | CD mean moves, but little — the primal is near, not at, machine zero | `|Δ|/CD < 1e-2` |
| **P3** | `δ_window` barely moves — it is set by shedding amplitude and window-period mismatch, both physical | `|Δ|/δ_window < 5e-2` |
| **P4** | `|g|` moves little | `|Δ|/|g| < 5e-2` |
| **P5** | **THE HEADLINE: the repair does NOT make an admissible FD step appear.** `h_min` in arm R stays **> `h_max` = 0.05** | `h_min,R > 0.05` |

**The falsifier, stated plainly: if `h_min,R ≤ 0.05`, P5 is WRONG**, and the consequence is the
important one — *"no admissible FD step exists"* would be an artefact of the upstream tutorial's
relaxation dictionary rather than a property of the method, and
`docs/capability/dafoam_GRID.md` would be **understating** this lab. `h_min` must fall **3.49×**
for that. **I predict it will not. I am registering that prediction so it can be measured against
me.**

## 7. VERDICT MAPPING, IN THE FIXED VOCABULARY

| outcome | item verdict |
|---|---|
| `G-RLX-0` reproduces; both arms complete; all of P1–P5 hold | **`PASS`** — the exposure is real and confirmed driven, and it does not reach the binding number |
| `G-RLX-0` reproduces; both arms complete; **P5 fails** (`h_min,R ≤ 0.05`) | **`GATE FAIL`** on this item's prediction — and the finding of the campaign. `dafoam_GRID.md` goes to the supervisor, and the cell is NOT edited by this lane |
| `G-RLX-0` reproduces; P1–P4 mixed, P5 holds | **`GATE REACHED`** — the headline is settled, the magnitude bands are not; each band reported individually, never averaged |
| `G-RLX-0` does NOT reproduce bit-for-bit | **`NOT A RESULT`** — no cross-arm delta reported |
| strict completion rule fails on any stage (rc≠0, no `End`, last time ≠ `endTime`, fields absent, age guard) | **`NOT A RESULT`** |
| cap reached, `MemAvailable` floor, OOM, PETSc failure | **`BLOCKED`** |
| not yet run | **`PENDING`** |

**The gate can only turn a PASS or GATE FAIL into `NOT A RESULT`, never the reverse.**

## 8. COST, PER RULE 12

**Measured anchor, not an estimate:** the D12R2 33-stage phase-1 program cost **55.5167 core-min**
total, from its own `ledger.txt` — S0 0.05 · S1a 0.2167 · S1b 0.5833 · S2a 0.9833 · S2b 7.0833 ·
S3 ×3 3.0833 · S3b ×16 16.5835 · S4 ×6 13.6833 · S5 10.9 · S7 ×2 2.35.

**Arm C is already bought**, so this item buys arm R plus the `G-RLX-0` reproduction leg.

| line | core-min |
|---|---|
| arm R, full program | 55.52 |
| `G-RLX-0` reproduction leg (S0+S1a+S1b+S2a+S2b on arm C's dictionary) | 8.92 |
| **point estimate** | **64.44** |

**Registered caps — an overrun STOPS the run and does not get a new budget:**
`CAP_CORE_MIN = 100.0` (item, cumulative, evaluated by the launcher before every stage) ·
`CAP_ARM_R = 70.0` · `CAP_G_RLX_0 = 15.0`. Margin over point estimate: **1.55×**.

**`cost_basis`:** core-minutes are **measured** from stage logs. The dollar figure is **derived,
not measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). At the
recorded **owner-stated** rate of $0.0513/core-h, 100.0 core-min = 1.6667 core-h ≈ **$0.086
derived**. Well inside the pre-authorised ceiling; it is costed anyway, because a blanket is not a
per-item read (rule 9).

**Estimate-versus-actual calibration is owed at completion** and lands as a row in
`docs/COST_CALIBRATION.md` with the ratio actual/predicted and the gap attributed. **No row is
owed now and none is written** — nothing has run.

## 9. WHAT THIS ITEM CANNOT SETTLE, SAID IN ADVANCE

- **It is one mesh (2,450 cells), one Reynolds number, one solver, np=1.** It measures what the
  repair is worth **here**. It does not license a statement about the unsteady line in general, and
  no such statement may be drawn from it.
- **It does not test the PATCHED image row** (`dafoam-idwarp-rot:v1`). SHIPPED only.
- **It cannot attribute a difference to any ONE of the four fields.** All four `Final` keys are
  added together, so the measurement is of the repair as a whole. Per-field attribution would need
  four more arms and is **not** registered here.
- **It does not touch `docs/capability/dafoam_GRID.md`.** Whatever it measures, moving that cell is
  the supervisor's call and above this lane.

## 10. FREEZE TABLE

| item | value |
|---|---|
| run root (asserted ABSENT at freeze) | `/home/ubuntu/certonomous-runs/CURRICULUM-D12RLX-relaxation-paired` |
| grading path | `cases/dafoam/curriculum_D12R2/d12y_grade_w3.py` md5 `3950d30fd09c9b56213a02f5e9864e20`, disk == HEAD |
| producer | `cases/dafoam/curriculum_D12R2/d12y_run_script.py` md5 `2790c39a09cd458d5a3263d7f1811da5`, disk == HEAD |
| image | `dafoam/opt-packages:latest`, id `sha256:9d45679d55fd…f07fc`, by id never by tag |
| arm C dictionary | md5 `95ab16a9141b0928bd352a9b9d8d93b9` |
| gates | `G-RLX-0` (reproduction) ; P1–P5 |
| caps | 100.0 item · 70.0 arm R · 15.0 `G-RLX-0` |
| core-minutes spent at freeze | **0** |
| frozen files edited | **0** |
| `fvSolution` files deleted, moved or rewritten | **0** |
| launched | **NO** |

**Held for the supervisor's two personal checks. Not queued.**

---

## 11. AMENDMENT 1 — 2026-09-01, PRE-COMPUTE. v1.0 → v1.1. The item was NOT EXECUTABLE as frozen: it named no launcher and it named the WRONG GRADER. Both corrected here, plus a design change that makes the control stronger.

**Lines whose number changed above this section: 0.** §§1–10 are untouched; every correction below
is stated here and the original is struck in place by reference, never rewritten.

**§2b's condition, stated AND CHECKED, re-driven for this amendment and not carried over from the
freeze.** `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-D12RLX-armC-repro` and
`.../CURRICULUM-D12RLX-armR-repaired` → **both "No such file or directory", 2026-09-01T06:19Z.**
No `d12rlx` container has ever existed. No ledger, no manifest, no log. **0 core-minutes spent.
There is still no answer to tune to.**

### 11.1 THE ITEM AS FROZEN COULD NOT HAVE RUN. Two defects, both mine, found at launch.

**DEFECT 1 — §10's freeze table names no launcher.** It registers a producer, a grader and an
image, and nothing that orchestrates a stage. The item could not have been started from its own
frozen description.

**DEFECT 2, AND IT IS THE SERIOUS ONE — §5 REGISTERED THE WRONG GRADER, AND IT WOULD HAVE
REFUSED.** §5 names `d12y_grade_w3.py` (md5 `3950d30f…`). **Measured:** that comparator carries
`W_PRIMARY = 2000` (`d12y_grade_w3.py:37`) and its `W3-A2` limb **refuses** any record whose window
is not the registered 2000. The program this item runs is the D12R2 33-stage graph at
**`W_STEPS = 300`** (`d12y_stage_and_run.sh:118`). **The registered grader would have refused the
item's own artefacts at grade time**, after the compute was spent.

**The correct grading path is `cases/dafoam/curriculum_D12R2/d12y_grade.py`**, `W_PRIMARY = 300`
(`:37`), md5 **`02a9ab62fc26d963886ecd0ee97457ef`**, verified **identical on disk and from the HEAD
blob** 2026-09-01. That is the comparator that graded the control arm, which is the whole point:
**the two arms must be graded by the same instrument as each other AND as the landed baseline.**
§5's `3950d30f…` is **STRUCK**. §10's freeze-table row is **STRUCK** and replaced by §11.4.

*Why the wrong one was registered: the supervisor's board and this lane's own findings record both
discuss `d12y_grade_w3.py`, because W3 is the item that has been under repair. It is the freshest
grader in the family and it is the wrong one for a W = 300 program. **A grader chosen by salience
rather than by matching the program is exactly the error rule 2's freeze is supposed to expose, and
here the freeze did expose it — before compute, which is when it is free.***

### 11.2 THE LAUNCHER, REGISTERED AND REUSED WITHOUT A SINGLE EDIT

`cases/dafoam/curriculum_D12R2/d12y_stage_and_run.sh`, md5
**`5f5c5e9fe3224c6c2474d8d355f01073`**, disk == HEAD blob, **UNMODIFIED**. It is env-parameterised
(`BASE`, `TUT`, `SRC` at `:94-96`), so both arms run the **identical, already-proven** 33-stage
program that produced the control baselines, driven only by `BASE` (run root) and `TUT` (tutorial
source). **No launcher is written for this item and no frozen launcher is edited.**

Phase 1 is the 33 stages §8's cost anchor is measured over: S0 · S1a · S1b · S2a · S2b · S3 ×3 ·
S3b ×16 · S4 ×6 · S5 · S7 ×2. Its own asserts still fire: A1 cap-vs-registered, A2 image identity
**by id never by tag**, A3 the on-disk instruments **are** the committed blobs.

**CORRECTION OF FACT, carried from the findings record.** The dictionary the launcher actually
stages is **`$TUT/system/fvSolution_pimple`**, copied over `mesh/system/fvSolution` at
`d12y_stage_and_run.sh:596` — **not** `system/fvSolution`. The two files are byte-identical
upstream (both md5 `95ab16a9141b0928bd352a9b9d8d93b9`), **so no number anywhere changes**, but §3
named the wrong file and a reproduction attempt following §3 literally would have edited a file the
launcher overwrites. §3's file reference is **STRUCK** in favour of `system/fvSolution_pimple`.

### 11.3 DESIGN CHANGE: ARM C IS RE-RUN IN FULL. THE CONTROL GETS STRONGER AND THE HAZARD DISAPPEARS.

§3 registered arm C as the **already-bought** D12R2 tree, with `G-RLX-0` re-running only `S2b` to
test reproduction. **Changed.** Both arms now run the **full 33-stage phase 1**, from their own
tutorial copy, into their own fresh run root, back to back on the same box.

**Why this is better and not merely bigger.** Under §3, only `δ_window` and CD came from a
contemporaneous pair; `δ_pert`, `δ_repeat` and `|g|` would have been compared against artefacts
produced weeks earlier under different machine conditions. **Now every registered quantity is
measured on both arms under the same conditions by the same instrument**, and `G-RLX-0` becomes a
**whole-program** reproduction test rather than a single-stage one. It removes the weeks-apart
hazard instead of bounding it.

**`G-RLX-0`, restated and STRENGTHENED (this replaces §4's single-stage form):** arm C-REPRO must
reproduce the landed D12R2 record — the 2,400-sample CD series **bit-for-bit**, `δ_window(300)`
identical to `0.0017958478225974517`, and `h_min` identical to `0.1742837908900481`. **If it does
not reproduce, the item is `NOT A RESULT`, no cross-arm delta is reported, and the run is NOT
retried** — a failure to reproduce is the item telling us the harness moved, and that is a finding,
not a transient.

**EXECUTION IS SEQUENTIAL, ARM C FIRST, AND THE ORDER IS LOAD-BEARING.** Two reasons, both
measured. **(1)** `docs/LAB_STATE.md` records this family losing 20 of 33 stages to `BLOCKED` when
two dafoam containers ran at once and drove `MemAvailable` under a registered floor. `MemAvailable`
is **28.1813 GiB** now and the measured per-container peak RSS is 1.3461 GiB, so parallel would
almost certainly be safe — **and "almost certainly safe" is not the standard after that failure.**
**(2)** Running C first makes `G-RLX-0` an economic gate: if reproduction fails, arm R's ~55
core-min is never spent. **Idle compute is a failure, but so is a self-inflicted BLOCKED cascade;
sequential costs wall time and buys both safety and the gate.**

### 11.4 THE ARMS, BUILT AND ASSERTED BEFORE ANY LAUNCH

| arm | tutorial source | `fvSolution_pimple` md5 | run root |
|---|---|---|---|
| **C-REPRO** | `/home/ubuntu/certonomous-runs/D12RLX_arm_tutorials/Cylinder_C` | `95ab16a9141b0928bd352a9b9d8d93b9` | `.../CURRICULUM-D12RLX-armC-repro` |
| **R** | `.../D12RLX_arm_tutorials/Cylinder_R` | `50680514696bed84e8327bc03b2ef160` | `.../CURRICULUM-D12RLX-armR-repaired` |

**The one-variable asserts were DRIVEN, 2026-09-01, before any container started, and one of them
fired:**

- `diff -rq Cylinder_C Cylinder_R` → **exactly ONE file differs**, and it is `system/fvSolution_pimple`. ✓
- `diff` on that file → **exactly 2 added lines, 0 removed.** ✓
- `diff -rq` upstream vs `Cylinder_C` → **no differences; arm C is byte-identical to the upstream tutorial.** ✓

**The registered delta**, committed as `cases/dafoam/D12RLX_fvSolution_pimple_Final.diff`:

```
     fields
     {
          "(p|p_rgh|G)"                   0.3;
+         "(p|p_rgh|G)Final"              0.3;
     }
     equations
     {
         "(U|T|e|h|nuTilda|k|omega|epsilon)"                   0.7;
+        "(U|T|e|h|nuTilda|k|omega|epsilon)Final"              0.7;
     }
```

**AN HONEST NOTE ON THE ASSERT THAT FIRED, because it was the assert that was wrong and not the
tree.** The first form of the "every other file identical" check filtered `diff -r` output by
filename, which does not remove the *hunk body* of the differing file, so it counted 4 lines and
**ABORTED**. The tree was correct; the instrument was not. Rewritten to `diff -rq`, which reports
one line per differing file, and re-driven. **Recorded rather than quietly fixed: a control that
fails closed on its own defect is behaving correctly, and the version that would have passed
silently is the one worth being afraid of.**

### 11.5 CAPS — AND A WEAKNESS DISCLOSED RATHER THAN PAPERED OVER

§8's `CAP_CORE_MIN = 100.0` was sized for one arm plus a single-stage repro. Two full arms at the
measured 55.5167 core-min anchor is **111.03 core-min point estimate**, so the item cap is
**RAISED to `CAP_ITEM = 150.0`** (margin 1.35×) with **`CAP_ARM = 70.0` each** (margin 1.26× on the
anchor). Legal pre-compute under rule 2; the condition is checked in this section's opening.

**Derived, not measured:** 150.0 core-min = 2.5 core-h × $0.0513/core-h ≈ **$0.128 derived**, at the
owner-stated rate. Roughly 195× inside the pre-authorised ceiling. Costed anyway — a blanket is not
a per-item read.

> **⚠ THE CAP IS LANE-ENFORCED, NOT MACHINE-ENFORCED, AND THAT IS A REAL WEAKNESS.** The reused
> launcher asserts its **own** registered cap — `CAP_CORE_MIN_REGISTERED="600.0"` hardcoded at
> `d12y_stage_and_run.sh:97-99` — and **aborts if it is passed any other value**, which is the
> D12-E' §6.1 defect closed in the correct direction. So the launcher will enforce **600.0 per run
> root**, not this item's 70.0. **`CAP_ARM = 70.0` is enforced by this lane watching the ledger and
> stopping the arm, and by nothing else.** The alternative was editing a frozen launcher, which is
> forbidden. The risk is bounded by the anchor — the *identical* program on the *identical* image
> measured 55.5167 core-min — but bounded is not enforced, and an overrun **stops the run** rather
> than getting a new budget.

### 11.6 WHAT DID NOT MOVE

**No prediction moved. P1–P5 stand exactly as frozen**, including the headline P5 (`h_min,R > 0.05`)
and its falsifier. §7's verdict mapping is unchanged. The image is unchanged
(`dafoam/opt-packages:latest`, by id). The producer is unchanged (`d12y_run_script.py`,
`2790c39a…`, disk == HEAD). `docs/capability/dafoam_GRID.md` remains untouched.

| amendment ledger | |
|---|---|
| predictions altered | **0** |
| verdict labels altered | **0** |
| frozen files edited | **0** |
| `fvSolution` files deleted, moved or rewritten | **0** |
| grading path CORRECTED (would have refused) | **1** |
| launcher registered (was absent) | **1** |
| caps raised, pre-compute, condition checked | **1** (100.0 → 150.0 item) |
| core-minutes spent at this amendment | **0** |
| run roots asserted ABSENT by execution | **2** |

**v1.1. Cleared to launch.**
