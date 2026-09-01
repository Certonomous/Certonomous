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
