# D12R2-W2 — THE CONTINGENCY WINDOW AS A REGISTERED EXPERIMENT — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-26**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

Authority: the **dafoam-supervisor's ruling (1) of 2026-08-26** — *"BUY W2 AS A NEW REGISTRATION"*,
with the condition stated in the same breath: *"REGISTER THE PREDICTION BEFORE YOU RUN IT … derive
it from your own measurements and register YOUR number, then score it HIT or MISS."*

> **A CONTINGENCY THAT BECOMES A REGISTERED PREDICTION WITH A FROZEN THRESHOLD STOPS BEING A
> CONTINGENCY AND BECOMES AN EXPERIMENT.** That is the whole purpose of this document.

---

## 0. WHY THIS RUN IS WORTH BUYING, IN ONE PARAGRAPH

D12R2 established at `W = 300` that **`h_min = 1.742838e-01` exceeds `h_max = 5.000e-02` by 3.49×,
so no admissible FD step exists** (`RESULTS.md`, `37779471`). **That finding has an innocent
explanation available to any critic: "you just needed a longer window."** W2 removes it. **Either
outcome is informative**, which is the mark of an experiment worth running:

- **the bright line is crossed at `W = 900`** — excellent, and the FD verification proceeds; or
- **it is not** — and the finding upgrades from *"cannot cross at `W = 300`"* to **"cannot cross,
  and tripling the window does not help, so the obstruction is not window noise."**

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2-cylinder-unsteady` DOES NOT EXIST.**

**`test -e` returned false at 2026-08-26T04:43:08Z**, immediately before this document was written;
state at that moment: **DOES_NOT_EXIST**. The launcher **refuses with exit 6** if it exists at
phase 1. After the first container, gates are **CLOSED**.

## 2. `W = 900` IS NOT A CHOSEN WINDOW, AND THAT DISTINCTION IS THE WHOLE VALIDITY OF THIS RUN

A diagnostic scan over the D12R2 series (§3.3) shows that `δ_window` is **jagged in `W`**, and that
`h_min` **straddles `h_max`**: at some windows an FD step would be admissible and at others it
would not. **Choosing a `W` because it yields a favourable `δ_window` would be fitting of the most
direct kind — selecting the window that gives the answer you want.**

> **`W2 = 900` WAS REGISTERED IN D12R's FROZEN §7 AT COMMIT `f9c8b9c8`, ON 2026-08-25, AND CARRIED
> UNCHANGED INTO D12R2's §6 AT `e6580910` — BOTH BEFORE ANY OF THE DATA THAT NOW MOTIVATES RUNNING
> IT EXISTED.** It is the pre-registered contingency window, not a window this lane picked after
> looking. **Had `W2` not already been frozen, this run could not honestly have been registered at
> all**, and the correct move would have been to register a `W` scan with its own gate rather than
> a single favourable window.

## 3. THE REGISTERED PREDICTIONS — DERIVED FROM THIS ITEM'S OWN MEASUREMENTS

All four are computed **from D12R2's own S2b series and graded gate values**, using the **frozen**
`d12y_grade.py` functions (`read_series`, `g3_delta_window`) rather than any new instrument.

### 3.1 THE MEASUREMENTS THE PREDICTIONS REST ON

| quantity | value | how obtained |
|---|---|---|
| `δ_window(W=900)` | **`9.879556064e-04`** | `g3_delta_window` on D12R2's 2400-sample S2b series. **A DIRECT MEASUREMENT, NOT AN EXTRAPOLATION.** |
| `\|g\|` at `W=300` | **`1.0304158599180422`** | D12R2 `G12R-4` / `step_plan.json`, component 0 |
| `EPS_NOISE_TARGET` | `0.01` | registered |
| `h_max` | `0.05` | registered |

**A HYPOTHESIS THIS LANE HELD, TESTED, AND HAD REFUTED BY ITS OWN MEASUREMENT — RECORDED BECAUSE
IT CHANGED THE DESIGN.** `δ_window` is `max − min` over block averages, an **extreme-value**
statistic, so this lane expected it to **grow with series length**, and concluded a `W = 900` study
would need S2b tripled to 7200 samples (costing **135.52** core-min instead of 121.35). **Measured,
on the real series: it does not grow — it SATURATES.** At `W = 300`, going from `N = 600` to
`N = 2400` (4× the data) moves `δ_window` by **0.4 %**; at `W = 900`, from `N = 1500` to `N = 2400`
it moves by **0.07 %**.

> **THE REASON IS PHYSICAL AND IT CORRECTS THE STATISTICAL MODEL:** the windows slide by ONE
> SAMPLE, so what the statistic explores is **phase**, not independent draws. At `W = 900` the 1501
> sliding windows cover **79 shedding periods** of phase. **The controlling quantity is phase
> coverage, not the number of non-overlapping windows** — of which there are only 2. **This lane's
> first instinct, that 2 independent windows made the measurement unresolved, was WRONG, and the
> data says so.** S2b is therefore left at **2400**, unchanged, and the run costs **14.17 core-min
> less** than the design this lane would have registered without measuring.

### 3.2 THE FOUR FROZEN PREDICTIONS

| # | prediction | value | scored |
|---|---|---|---|
| **P1** | W2's S2b series is **bit-identical** to D12R2's, so `δ_window(900)` reproduces **exactly** | **`9.879556064e-04`**, to all printed digits | **HIT / MISS** |
| **P2** | `\|g\|` at `W = 900` stays near its `W = 300` value | **`1.0304158599180422` ± 30 %**, i.e. `[0.7213, 1.3396]` | **HIT / MISS** |
| **P3** | **PRIMARY, BINARY: `h_min(900) > h_max`, so THERE IS STILL NO ADMISSIBLE FD STEP** | `admissible: false` | **HIT / MISS** |
| **P4** | point value of `h_min(900)` | **`9.587931e-02`** (**1.9176×** `h_max`), band `[7.375e-02, 1.370e-01]` from P2's ±30 % | **HIT / MISS** |

**P1 IS SHARP ON PURPOSE.** S2b runs 2400 steps from a `FIELD_B` produced by S2a, and **neither
depends on `W`**; `G12R-2` measured `δ_repeat = 0.0` across three identical runs, so this solver is
**bit-deterministic at np=1**. **If `δ_window(900)` differs from `9.879556064e-04` at all, then
something in this pipeline is non-deterministic, and THAT is a finding regardless of what happens
to the bright line.**

### 3.3 THE FALSIFICATION CONDITION, STATED AS A NUMBER

`h_min = δ_eff / (EPS_NOISE_TARGET · |g|)`, and `δ_eff` is expected to remain `δ_window` (at
`W = 300`, `δ_pert = 2.28e-06` and `δ_repeat = 0.0`, both four orders below it).

> **P3 IS FALSIFIED IF AND ONLY IF `|g|` AT `W = 900` EXCEEDS `1.9759`** — that is, if the adjoint
> gradient of the time-averaged drag **grows by 1.918× when the averaging window triples.**

**This lane predicts it does not**, on the ground that `g` is a derivative of a *time-averaged*
objective that has already converged on the limit cycle: `G12R-1` measured the mean `CD` to
`0.6563231414421499` with a p2p of only 20 % about it, and the block-average grand mean at
`W = 300` is `0.6563818081175736` — **the averaged objective is stable in `W` to four significant
figures**, so its derivative has no obvious reason to nearly double. **That is a stated argument
from measurement, not a certainty, which is why P2 carries a ±30 % band and P3 carries an explicit
falsifier.**

### 3.4 WHAT THIS RUN WILL AND WILL NOT ADD

**`δ_window(900)` is ALREADY KNOWN and saturated** (§3.1). The genuinely new measurements are
**`|g|` at `W = 900`** (S5, the adjoint over 900 steps) and **`δ_pert` at `W = 900`** (S3b, 16 runs).
**This document says so plainly rather than implying the run discovers everything it reports**: P1
is a **reproduction check**, and the experiment's real content is P2 and P3.

## 4. REGISTERED RESOURCES — BOTH ADDED UNDER THE 2026-08-26 RULING

| parameter | registered | basis |
|---|---|---|
| **`CPUSET_CPUS`** | **`12`** | **EXPLICIT PIN.** `--cpus=1` is a **quota, not a placement**: it rations CPU time without saying *where*, so two containers can be handed the same physical core and each still be "within quota". **A quota is not a placement, and only a placement is a fact.** Core 12 is outside the `5,6,7,9` a peer holds. |
| **`MEM_LIMIT`** | **`8g`** (was 20g) | **MEASURED, not habitual.** D12R2's peak RSS was **1.3461 GiB** (S5, the adjoint), and the **S4 envelope measured adjoint RAM FLAT in steps** — `1.3145 → 1.3129` GiB from `n = 20` to `n = 80` — so **tripling the window does NOT triple RAM**. 8g is **~5.9×** the measured peak. |
| **aggregate cap assert** | **`Σ(all container caps) ≤ MemTotal`**, evaluated **before every stage** | **D12R2 ran an unpinned container at a 20 GiB cap while a peer held 12 GiB on a 30.64 GiB box. Nothing OOMed, AND THAT IS THE POINT: the run was SAFE BY LUCK**, because actual use was 1.35 GiB against a cap that *promised* 20. **`MemAvailable` cannot see this** — it reports what is free **now**, not what has been **promised**. Checking free memory answers the wrong question. |
| `MEMAVAIL_FLOOR_GIB` | **`14.0`, UNCHANGED** | Carried at its registered value. **It was NOT lowered to fit this run.** If peers push `MemAvailable` below it, stages **BLOCK**, and that is the guard working — to be reported, never worked around. |

**THE AGGREGATE ASSERT IS DEMONSTRATED, NOT ASSERTED.** Measured before this document was frozen,
against the live box: at the registered **8 GiB** it **PASSES** (`12.0 + 8 = 20.0` vs `30.64`); at
**20 GiB** — *the cap D12R2 itself used* — it **REFUSES** (`32.0` vs `30.64`); at 64 GiB it
refuses. **The guard would have refused D12R2's own configuration**, which is the sharpest
demonstration available that it is not a formality.

## 5. INSTRUMENTS

| file | md5 | note |
|---|---|---|
| `d12y_grade.py` | `33f7a006e15dce2988a63b2e937cf07b` | **UNCHANGED from `e6580910`.** The comparator that graded `W = 300` grades `W = 900`. **The grading path is not re-authored for the contingency**, so a different answer cannot come from a different instrument. |
| `d12y_run_script.py` | `2790c39a09cd458d5a3263d7f1811da5` | **UNCHANGED.** Byte-identical through `d12r_`, `d12x_`, `d12y_` — four items, one file. |
| `d12y_w2_stage_and_run.sh` | `89da74b539fef8924970bf6090db68d3` | derived from the frozen `d12y_stage_and_run.sh`, which is **CITED AND UNEDITED**. Registered changes and only these: `W_STEPS 300→900`, `MEM_LIMIT 20g→8g`, `CPUSET_CPUS`, the aggregate assert, a separate run root, and self-verification against its own committed blob. |

The launcher **verifies all three against their committed HEAD blobs before every launch** and
aborts with code 4 otherwise.

**`EXPECTED_STAGE_ROWS_PHASE1 = 33` is unchanged and still correct:** W2 alters the *length* of the
window stages, **not the stage graph**. `G12R-0b` therefore binds the same 33 rows to the same 33
ledger lines.

## 6. COST

**121.35 core-min predicted**, derived stage-by-stage from D12R2's **measured** per-stage costs:

| group | D12R2 measured | in W2 |
|---|---|---|
| S0, S1a, S1b, S2a | 1.8333 | **unchanged** — none depends on `W` |
| S2b (2400 steps) | 7.0833 | **unchanged** — §3.1's saturation result |
| S4 envelope (`n ∈ {20,40,80}`) | 13.6833 | **unchanged** — `ENV_STEPS` is independent of `W` |
| S3 + S3b + S5 + S7 | 32.9168 | **× 3 = 98.75** — these are the window stages |
| **total** | **55.5167** | **121.35** |

Against the registered guard **`CAP_CORE_MIN = 600.0`**. Derived **$0.1038** at $0.0513/core-h,
c7a.4xlarge — **REPORTED-BY-OWNER, DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5).
Calibration row owed at completion, **its id re-derived by hand inside the committing invocation
and cited only after the commit produces it** (the `C-100` → `C-107` → `C-115` lesson).

## 7. CARRIED FORWARD — RECORDED, NOT IMPORTED

The `W = 300` results (`RESULTS.md`, `37779471`) are **recorded and NOT imported**. Every number
this run grades is **re-measured on its own artifacts**; a repeat is corroboration and a departure
is a finding.

**AND THE STANDING CAVEAT, IN FULL:** the period re-measured at **18.9644 steps** gives
**`St ≈ 0.5273`**, roughly **2.6× the accepted ≈0.2**. **On a 2,450-cell 2D URANS mesh with wall
functions this is a RESOLUTION ARTIFACT and is NEVER quoted as a Strouhal number.** The estimator
is **mean-crossing**, which underestimates the fundamental, so the period is a **lower** bound and
`St` an **upper** bound. **That D12R2 reproduced the prior to −0.16 % does not make it a Strouhal
measurement — it makes it a REPRODUCIBLE ARTIFACT.** It is a window-sizing diagnostic and nothing
else.

## 8. WHAT THIS RUN WILL NOT ESTABLISH

Nothing at `np > 1`; no grid family, **so rule 5 has no row to gate and NO GCI IS QUOTED**; nothing
about the physical accuracy of `CD` at `Re_D = 1.0e6` on 2,450 cells; **nothing about `St`**.
**And it does not establish that `W = 900` is the RIGHT window** — only what happens at the window
that was pre-registered as the contingency. **`G12R-6`, the bright line itself, runs only if P3
MISSES**; if P3 hits, `G12R-6` does not run and **no adjoint-versus-FD comparison is bought.**
