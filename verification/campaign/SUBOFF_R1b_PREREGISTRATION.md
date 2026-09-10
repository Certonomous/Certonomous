# SUBOFF R1b — DARPA SUBOFF bare hull, zero incidence, total-drag parity — PRE-REGISTRATION

**STATUS: DRAFT — NOT FROZEN.** Drafted by a cfd lab-lane, 2026-09-10. The freeze (sha),
the queue drop and the graded launch are the cfd-supervisor's `SUPERVISION_CHARTER` §3
check-4, taken personally and not delegated. **No compute has run for R1b**; §4a below
names the three run roots that **do not exist**, which is the rule-2 form of the
pre-compute condition. Nothing here is graded and no number here is a result.

**R1b is a §2bc fix-until-runs SUCCESSOR to `SUBOFF_R1_PREREGISTRATION.md`.** It is not
an edit of R1 (rule 6 — R1 is frozen and is not touched) and it is not a blind retry.
R1 closed **NOT A RESULT** on a cap-stop; R1b diagnoses that stop, repairs **exactly the
diagnosed thing**, and changes nothing else. The pattern is SUP_BOOSTER E2 succeeding E1.

---

## 0. WHAT MOVES, AND WHAT DOES NOT — read this before anything else

**INHERITED FROM R1 UNCHANGED. NO GATE, THRESHOLD, BAND OR LABEL MOVES.**

| inherited item | value, transcribed from `SUBOFF_R1_PREREGISTRATION.md` |
|---|---|
| **Gate D1** | `CT = R_T / (½ρU²S_wetted)` at `Re_L = 1.2×10⁷`, from the finest grid of a **CONVERGING** Roache triple |
| **Band** | **PASS iff `\|CT_cfd − CT_ref\| ≤ 0.10·CT_ref` (±10%)**, else **GATE FAIL**; non-CONVERGING triple ⇒ **NOT A RESULT** (rule 5) |
| **`CT_ref` anchor** | **3.6×10⁻³** on wetted area — **MANIFEST / engineering** (ITTC-1957 + form factor), tier **BOUNDED-AGREEMENT at best**, **NOT experiment-validated**, and it **stays** so until a title-verified SUBOFF report PDF lands (rule 15) |
| **`reference.Aref`** | **0.0831703362813915 m²** (5° sector = analytic / 72), pinned, ONE value at every level |
| **analytic wetted area** | **5.988264212260189 m²** (Groves/Huang/Chang 1989, title-page verified; re-derived by `derive_wetted_area.py`) |
| **Mesh family** | **39,904 / 89,784 / 202,014** cells, exactly **2.25×** per level, `dim = 2` wedge |
| **Admission gates** | max non-orthogonality **≤ 70°**, max skewness **≤ 4** (cleared at 57.405 / 63.602 / 68.706 and 1.654 / 1.900 / 2.123) |
| **Grader** | `cases/navier_class/SUBOFF/grade_suboff.py`, with both planted-zero controls (rule 3) and refuse-not-degrade |
| **Solver length** | `endTime 2500`, `deltaT 1`, `writeInterval 2500`, `purgeWrite 0`, **no `residualControl`** |
| **Ranks** | **1** |
| Reference constants | `magUInf 2.893`, `lRef 4.356`, `rhoInf 1000` |
| Reference tier / registry | unchanged; registry action still deferred to the 3-D rung |

**WHAT CHANGES — and it is one thing plus two forced consequences of it.**

1. **THE COMPUTE BUDGET (§7).** The cap and the per-level sub-caps are re-derived from
   the **MEASURED CONTENDED** rate instead of the single-tenant smoke rate. **This is the
   whole of the substantive change. R1b is a RESOURCE re-registration.**
2. *(forced by 1, §4a)* **New run roots.** R1's `reg_coarse` / `reg_medium` hold the
   cap-stop evidence that IS §7's measured basis; the launcher refuses a dirty root and
   never clears one, so R1b runs in `r1b_coarse` / `r1b_medium` / `r1b_fine`.
3. *(directed repair, §9)* **The launch path now grades unconditionally.** R1's launcher
   graded only under `--grade` and the R1 queue entry did not pass it: a clean R1 would
   have completed and produced **no verdict at all**. That defect is owned and closed here.

---

## 1. WHAT HAPPENED TO R1 — the measured record, not a narrative

R1 was FROZEN at commit `94d7afb7` with `endTime 2500`, a **150 core-min** whole-rung cap
and per-level sub-caps **15 / 33 / 74** core-min ⇒ wall timeouts **900 / 1980 / 4440 s** at
ranks 1. On disk, in `verification/runs/navier_class/SUBOFF/`:

| level | artifact | what it says |
|---|---|---|
| coarse | `reg_coarse/rc`, `reg_coarse/STATUS.R1_coarse` | `rc=124`, `wall_s=900`, `core_min=15.000` — the 900 s timeout fired |
| coarse | `reg_coarse/log.simpleFoam` | last `Time = 1445` of 2500; 1444 `ExecutionTime` lines; **0 `End` lines** |
| medium | `reg_medium/log.simpleFoam` | reached `Time = 311`; the chain was stopped deliberately by the supervisor |
| fine | `reg_fine/` | never launched — no `0/`, no `log.simpleFoam` |

**The stop was correct and is recorded as such.** Coarse is not rule-4 complete, so under
rule 5 clause 1 **no Roache triple can exist whatever the other two levels did**;
continuing would have spent ~107 further core-minutes on a guaranteed NOT A RESULT.
**R1's verdict is NOT A RESULT (cap-stop).** That verdict is not revisited here.

---

## 2. THE DIAGNOSIS — measured, re-derived independently, with the disagreement named

Throughput is normalised per cell so levels of different size are comparable. Every figure
below is read from **one named log file** (`log.simpleFoam`), never a glob — `grep` on this
box is **ugrep 7.8.4** (re-verified 2026-09-10), which interleaves multi-file output.

Rates are **incremental**: the difference between the first and last `ExecutionTime` line,
over the iterations between them, so solver start-up is excluded from the *rate* and
accounted separately as a setup term.

| run | cells | iters | ΔCPU (`ExecutionTime`) | Δwall (`ClockTime`) | CPU share | **s per cell-iteration, wall** |
|---|---|---|---|---|---|---|
| `smoke_coarse` (single-tenant) | 7,600 | 49 | 2.12 s | 2 s | — | 5.69e-6 *(CPU basis)* |
| `reg_coarse` **CONTENDED** | 39,904 | 1,443 | 861.60 s | 896 s | **0.9616** | **1.556056e-05** |
| `reg_medium` **CONTENDED** | 89,784 | 309 | 428.51 s | 433 s | **0.9896** | **1.560740e-05** |

**Throughput, the two contended points:**
- `reg_coarse`: **6.4265e4 cell-iterations/s** (wall) — 6.6831e4 on a CPU basis.
- `reg_medium`: **6.4072e4 cell-iterations/s** (wall) — 6.4744e4 on a CPU basis.

**FINDING 1 — the two contended points AGREE, and that is the load-bearing result.**
Per-cell-iteration wall cost, medium ÷ coarse = **1.0030**. Across a **2.25× increase in
cell count** the per-cell cost is **flat to 0.3%**. Extrapolating to the 202,014-cell fine
level by cell count is therefore **measured-supported, not assumed** — which is exactly
what a budget for an unrun level needs and what a single data point could not have given.

**FINDING 2 — the headline contention factor is CONFIRMED.** Against the single-tenant
smoke on a CPU basis: coarse **2.628×**, medium **2.713×**; on the supervisor's simpler
whole-run basis (7,600×50/2.21 vs 39,904×1445/900) **2.684×**. The supervisor's **2.68×**
is reproduced. *(The smoke's `ClockTime` is 0→2 s at 1-second granularity and is
under-resolved; its `ExecutionTime` 0.09→2.21 s is not. The smoke reference rate is
therefore taken on the CPU basis. A wall-basis smoke comparison would read 2.90× and
would be an artifact of that granularity, not a finding.)*

**FINDING 3 — the attribution is confirmed, and the MECHANISM is narrowed.** The loss is
**not** scheduler starvation: the solver held **96.2%** (coarse) and **99.0%** (medium) of
one core of CPU while running. A `ps` snapshot at 2026-09-10T05:14Z measured **10
processes at ≥96% CPU on `nproc` = 16**, i.e. the box is **not CPU-oversubscribed**; the
load average of 35.5 is inflated by uninterruptible-sleep tasks, which do not compete for
core time. The degradation shows up as **more CPU-seconds per cell-iteration**, which is
the signature of shared memory-bandwidth / last-level-cache contention among ten
concurrently streaming solvers. **[INFERRED — the bandwidth mechanism is an inference from
the CPU-share and per-cell-cost measurements; no bandwidth counter was read.]**
The attribution stands as the supervisor stated it: **CONTENTION**, not a misprediction of
the physics and not a defect in the rate methodology. The rate was correctly measured
within-configuration — on a lightly-loaded box, and then applied to a contended one.

**FINDING 4 — ONE SUB-CLAIM IS REFUTED, and it matters for how §7 is worded.** The
supervisor argued 2.68× is a **floor** on the contention effect because per-cell cost
should *fall* on larger meshes as fixed overheads amortise. Two things cut against it:
(a) the rates above are already incremental, so per-iteration fixed overhead is largely
excluded and there is little left to amortise; and (b) working-set size runs the other
way — 7,600 cells is a few MB and plausibly last-level-cache resident, while 39,904 cells
is not, so part of the 2.68× is a **mesh-size effect that would also appear on an idle
box**. The two contended points bound this: coarse and medium have the same per-cell cost,
so whatever transition occurs, it occurs **below 39,904 cells** and both regression-scale
meshes sit on the same flat plateau. **Consequence: 2.68× is a floor on the smoke→regression
rate degradation, NOT cleanly a floor on the contention component alone, and the split
between contention and cache-exit CANNOT be separated from these artifacts.** This changes
nothing about the repair — either way the smoke rate is the wrong budgeting basis and the
measured contended rate at regression cell counts is the right one — but §7 is therefore
built on the **directly measured contended rate**, and never on a contention *factor*
applied to the smoke rate.

**Consequence for R1's cap, arithmetic below in §7:** coarse alone needs **26.0 core-min**
to reach 2500 against its **15** allocated, and the triple needs **216.2 core-min** against
the frozen **150** cap. **R1's cap could not deliver R1's own registered `endTime`. That is
the defect R1b repairs.**

---

## 3. GATE, REFERENCE TIER, MESH PLAN, GRADER — INHERITED, NOT RESTATED

§2, §3, §4, §5 of `SUBOFF_R1_PREREGISTRATION.md` are **inherited verbatim and unchanged**,
and are incorporated here by reference rather than re-typed, so that no transcription
error can move a gate. The summary table in §0 above is a convenience index, not a
redefinition: **where §0 and the R1 original differ in any particular, the R1 original
governs.** In particular the ±10% band, the 3.6e-3 MANIFEST anchor, the
BOUNDED-AGREEMENT / NOT-experiment-validated tier, the pinned `Aref`, the ≤70°/≤4
admission gates and every clause of the grader contract are **frozen as R1 froze them**.

### 4a. THE THREE REGISTERED GRADED RUN ROOTS (pre-compute registration, 2026-09-10)

**The R1b graded triple runs in exactly these three directories, coarse → fine, and in no
others.** A number taken from any other directory under
`verification/runs/navier_class/SUBOFF/` is not a graded R1b number.

| level | registered R1b run root | mesh staged from | cells |
|---|---|---|---|
| coarse | `verification/runs/navier_class/SUBOFF/r1b_coarse` | `reg_coarse` | 39,904 |
| medium | `verification/runs/navier_class/SUBOFF/r1b_medium` | `reg_medium` | 89,784 |
| fine   | `verification/runs/navier_class/SUBOFF/r1b_fine`   | `reg_fine`   | 202,014 |

**PRE-COMPUTE CONDITION, and how it was checked (rule 2).** Checked 2026-09-10 by a cfd
lab-lane, directly on disk with `ls -la` of the parent: **`r1b_coarse`, `r1b_medium` and
`r1b_fine` DO NOT EXIST.** Those are the directories that do not exist. No compute has run
for R1b, so §4a and §7 are legal pre-compute registrations and not post-hoc addenda.

**WHY NEW ROOTS RATHER THAN R1's.** `reg_coarse` and `reg_medium` now hold R1's cap-stop
evidence — `0/`, `log.simpleFoam`, `rc`, `STATUS.R1_*`, `CAP_BREACH.txt`,
`postProcessing/`. That evidence is the **measured basis of §2 and §7** and the launcher
rule "a dirty directory is a REFUSAL, never a clearing" forbids reusing them. The R1 roots
are **not touched, not cleared and not edited** by anything in R1b.

**MESH PIN — the new failure mode this forced change opens, and its guard.** Staging a
root introduces a way to be wrong that R1 did not have: copying the **wrong mesh**. The
mesh family is therefore pinned by **sha256 of the staged file, asserted after the copy**,
by the launcher, which refuses on any mismatch. This pins the family **harder** than R1 did
and moves no gate.

| level | `points` | `faces` | `owner` | `neighbour` | `boundary` |
|---|---|---|---|---|---|
| coarse | `88803d7a…30512e` | `117b09b3…9bfd7b8` | `424790aa…7ba84957` | `3721a504…6e64795c4` | `7def99e6…16464c2a74` |
| medium | `125f7f6e…679f88e4` | `11a86ed8…9185f485d08` | `2f3a7df3…6e13f0faee` | `d2b913b7…b5819c3688` | `9d7352bf…a408942596ef5` |
| fine   | `fd720d27…544ef0f49` | `d945be9f…c468f32330e` | `f261ace8…5393b89c26acdc` | `b21bebd3…88b9aa2baf9d` | `957e432b…21905cc906f49` |

*(Full 64-character values are in the launcher's `PIN` table, which is the executable
copy; the abbreviations above are for reading, and the launcher's values govern.)*
`system/controlDict`, `system/fvSolution` and `system/fvSchemes` are **byte-identical
across all three levels** — sha256 `f002ab4a…5649c8`, `f9a35242…5c1aa997`,
`62fc76f7…5d40d0bef4` — and are pinned once. **That single-blob identity is the mechanical
proof that every level normalises on the same `Aref` and runs the same `endTime 2500`.**

---

## 5a. THE REGISTERED SOLVER LENGTH — `endTime` STAYS 2500, and why the new cap does not move it

**REGISTERED, unchanged from R1, one-way:**

```
endTime         2500;   // SIMPLE iterations; HARD stop
deltaT          1;      // unit step, so rule-4 clause 5 reads ExecutionTime count == 2500
writeInterval   2500;   // one field write, at endTime
purgeWrite      0;
```

R1's §5a gave **four** bases for 2500. Three of them are untouched by anything in R1b:

2. **Lab precedent for this solver pattern.** `MRF_R1_PREREGISTRATION.md` registered
   **4000** fixed iterations for a *harder* steady segregated-SIMPLE incompressible RANS
   case; `W1_HUMP` registered **5000** for a *separating* hump. SUBOFF R1 is fully
   attached, zero-incidence, axisymmetric — a number of the same order but **below** MRF's
   is the precedent-consistent choice.
3. **The nearest measured convergence count, on a harder case.** F6a's kOmegaSST
   `simpleFoam` leg converged in **1772** iterations on a 51,626-cell separating hump
   (`verification/campaign/F6a_epistemic_band.md:254`). 2500 is **1.41×** that.
4. **The grader's own test decides convergence, not this number.** `endTime` is a HARD
   STOP; `read_iterative_state` judges convergence against `RES_TOL = 1e-4` on the final
   **Initial** residuals. 2500 is sized so a `NOT_CONVERGED` is a *finding* rather than a
   *truncation*.

Basis **1** was "the registered cap binds it from above" — the 150 cap admitted at most
`N = 2892` with a fine rerun reserved. **That ceiling has moved.** It is recorded here, in
advance, exactly what that does and does not license:

- **It does NOT license raising `endTime`.** Basis 1 was a **ceiling**, never a floor; it
  bounded 2500 from above and never argued *for* it. Bases 2–4 argue for 2500 and none of
  them mentions cost. **`endTime` stays 2500.**
- **Nor could it be raised.** Raising it after R1's residuals exist on disk would be
  choosing a number after seeing the answer — the precise thing rule 2 forbids, and the
  thing R1's own freeze block promised would never happen ("**never** by extending this
  `endTime` after seeing residuals"). **No residual from `reg_coarse` or `reg_medium` was
  read while drafting this document, and none is cited anywhere in it.**
- **Nor lowered.** Lowering 2500 to fit a budget would be choosing the physics to fit the
  resource — the inverse of the same error, and the reason §7 sizes the cap to the
  `endTime` rather than the `endTime` to the cap.

**The rejected alternative, revisited honestly.** R1's §5a considered and rejected a
per-level `endTime` scaled by the 1.5 refinement ratio (1600 / 2400 / 3600) for **two**
reasons: it did not fit the 150 cap, and it introduced a degree of freedom the MRF
precedent does not have. **The first reason is now void** — the new cap would admit it.
**The second stands**, and a third now joins it: R1b's mandate is to fix exactly the
diagnosed thing, and the diagnosed thing is the budget. Changing the solver length in the
same successor would confound the repair with a numerics change. **Rejected again, and
recorded so the choice is visible rather than silent.**

**NAMED RISK, carried over unchanged.** The fine level is the one most at risk of not
reaching `RES_TOL` by 2500 [INFERRED, standard segregated-solver behaviour]. If it returns
`NOT_CONVERGED` at 2500 with residuals still falling, that is **NOT A RESULT** reported as
a truncation finding, answered by a re-registered successor — **never** by extending this
`endTime`.

---

## 7. COST AND CAPS (rule 12) — **the one thing that changes**

### 7.1 What a cap is for, here

Sanaa has **lifted cost constraints**: *no team stops anything in the name of saving
compute*. A cap in this lab is therefore a **runaway guard that reports**, not a budget
ceiling to be admired for its thrift. **A cap that cannot deliver its own registered
`endTime` is not a guard — it is a scheduled NOT A RESULT.** That is the defect R1b
repairs, and §7 is sized so that **2500 iterations at all three levels is REACHABLE WITH
MARGIN under the contention actually measured**, not sized to look cheap.

### 7.2 The design rate — measured, contended, and the slower of the two points

```
D = 1.560740e-05 s per cell-iteration, wall, ranks 1, CONTENDED
```
`D` is `reg_medium`'s measured incremental wall cost (§2). It is chosen over `reg_coarse`'s
1.556056e-05 because it is the **slower of the two**, i.e. conservative, and because it is
the point at the larger cell count and so the nearer neighbour of the unrun fine level.
Finding 1 (flat to 0.3% across 2.25× in cells) is what licenses applying it to 202,014
cells at all.

### 7.3 Projection to the registered `endTime`

`wall_s = cells × 2500 × D + setup_s`. Setup is the `ClockTime` at the first iteration:
**4 s** measured (coarse), **8 s** measured (medium), **18 s** for fine
**[INFERRED by cell-count scaling from the two measured values; it is 0.2% of that level's
projection, so the inference is immaterial to the cap]**.

| level | cells | cells × 2500 × D | + setup | wall s | **core-min** |
|---|---|---|---|---|---|
| coarse | 39,904 | 1557.0 s | 4 | 1561.0 | **26.02** |
| medium | 89,784 | 3503.2 s | 8 | 3511.2 | **58.52** |
| fine | 202,014 | 7882.3 s | 18 | 7900.3 | **131.67** |
| | | | | | **TRIPLE = 216.2 core-min** |

Against R1's frozen 150 cap and its 15 / 33 / 74 sub-caps. **The supervisor's ~26.0 and
~216 are reproduced to three figures.**

### 7.4 The margin, and its stated basis

**Margin factor `M = 1.75`**, applied to every level. It is **not** a prediction; it is
what the cap must absorb before it fires. Its basis, stated in advance:

- **1.60 — a bound on further bandwidth contention.** The loss channel is per-cell CPU
  cost under shared memory bandwidth (§2 Finding 3), and the number of concurrently
  streaming CPU-bound solvers on this box cannot exceed `nproc` = **16**. It was measured
  at **10** when R1 ran. Going 10 → 16 is **1.60× more consumers**; if the memory-bound
  fraction degraded in strict proportion — a worst case, since bandwidth contention
  saturates sub-linearly — that is a 1.60× bound. **[INFERRED: the strict proportionality
  is an upper-bound assumption, not a measurement.]**
- **× 1.09 — the write and bookkeeping term that the rate does not contain.** `D` is
  incremental between `ExecutionTime` lines and therefore excludes the **single field
  write at `endTime`** (`writeFormat ascii`, `writePrecision 16`, five fields ×
  202,014 cells at the fine level), the log flush, and the launcher's per-level sidecar
  writes. **That write cost is UNMEASURED — `reg_coarse` stopped at 1445 and never
  reached `writeInterval 2500`, so no SUBOFF field write exists on disk to measure.** The
  1.09 term reserves **711 s** for it at the fine level, which is ample for a write of that
  size and is named here rather than absorbed silently.
- `1.60 × 1.09 = 1.744` → **`M = 1.75`**.

### 7.5 REGISTERED CAPS — frozen at this document's freeze

| level | projection | × 1.75 | **registered sub-cap** | **wall timeout `= sub_cap × 60 / ranks`** | headroom over projection | `N` reachable at the sub-cap |
|---|---|---|---|---|---|---|
| coarse | 26.02 | 45.53 | **46 core-min** | **2,760 s** | 1.768× | 4,431 |
| medium | 58.52 | 102.41 | **103 core-min** | **6,180 s** | 1.760× | 4,410 |
| fine | 131.67 | 230.42 | **231 core-min** | **13,860 s** | 1.754× | 4,395 |
| | **216.2** | | **Σ = 380 core-min** | Σ = 22,800 s = 6.33 h | | |

> **REGISTERED WHOLE-RUNG CAP: 400 core-minutes.** `= 380` (the sum of the sub-caps)
> `+ 20` core-min of accounting reserve, so that the **global** guard can never pre-empt a
> level whose own sub-cap admits it. The per-level sub-caps are the operative guards; the
> whole-rung cap is the runaway guard of last resort.
>
> **NO RERUN ALLOWANCE IS RESERVED, deliberately.** R1 reserved one and it bought nothing —
> a level that stops is not rule-4 complete, and the honest answer to a stop is a
> **re-registered successor**, not a second helping from the same cap. **An overrun stops
> the run; it does not get a new budget.**

**Every registered sub-cap admits `N ≈ 4,400`, i.e. 1.76× the registered `endTime 2500`.**
That ratio, not the absolute figure, is the repair: R1's coarse sub-cap admitted `N = 1445`
against a registered 2500, which is **0.58×**, and that is why R1 could not finish.

### 7.6 Cost

- **400 core-minutes registered cap** = 6.667 core-h.
- Dollars at the recorded rate: `400/60 × $0.0513` = **$0.3420 — DERIVED, NOT MEASURED.**
  The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5, rule 12), and the
  $0.0513/core-h rate is **reported-by-owner**, not measured here.
- Expected spend if nothing degrades further: **216.2 core-min = $0.1849 DERIVED.**
- CPU only; **no GPU**, so the 2026-08-21 blanket applies and the figure is far under the
  $25 pre-authorised tier. **The cap is 2.67× R1's and costs 21 cents more. That price
  difference is the entire reason R1's thrift was worth nothing.**
- **Rule-12 estimate-vs-actual calibration is OWED at completion**: a row in
  `docs/COST_CALIBRATION.md` comparing the 216.2 core-min projection against the actual
  core-seconds in the `STATUS.R1b_<level>` sidecars, stating actual/predicted, attributing
  the gap (contention, waste, misprediction named **separately**), and deriving dollars at
  $0.0513/core-h labelled DERIVED NOT MEASURED.

### 7.7 Wall time, and why the levels run SEQUENTIALLY at ranks 1

At the registered caps the chain is **6.33 h wall** in the worst case, ~3.6 h at the
projection. Two choices are registered in advance so neither can be revisited to fit an
outcome:

- **Ranks stays 1.** Not for thrift (`core-min = wall_s × ranks`, so ranks > 1 costs
  strictly more in the lab's unit) but because the diagnosed bottleneck is **shared memory
  bandwidth**: extra ranks on this box add bandwidth consumers and would return
  sub-linear speedup. Changing ranks would also change the decomposition, which is a
  numerics change, not the diagnosed repair.
- **The three levels run SEQUENTIALLY, never in parallel with each other.** Running them
  concurrently would shorten the chain and would **manufacture more of the exact
  contention this rung is being re-registered because of**. Self-inflicted contention is
  not an acceptable way to fit a wall clock.

---

## 8. THE CONTENTION RISK — REGISTERED BEFORE COMPUTE

Stated plainly, in advance, so that if it happens it is reported as a **result** and not
discovered as a surprise:

1. **The rate this cap is built on is MEASURED UNDER CONTENTION** (§2), on a box carrying
   ~10 concurrent CPU-bound solvers at 2026-09-10T05:05–05:13Z. It is **not** a
   single-tenant rate and **must not** be quoted as one.
2. **Box load is NOT CONTROLLED BY THIS RUNG.** Five other teams and a detached queue
   daemon launch compute on the same box. R1b neither reserves cores nor waits for a quiet
   box, and it will not: idle compute is itself a failure in this lab.
3. **The margin is bounded and it is stated:** `M = 1.75`, covering the 1.60× bandwidth-
   consumer bound to full 16-way occupancy plus the 1.09 write/bookkeeping term. If load
   rises **beyond** what that absorbs — most plausibly if runnable CPU-bound tasks exceed
   `nproc` = 16, at which point the scheduler-share channel opens and wall stretches
   directly, a channel measured **CLOSED** at 0.96–0.99 core-share while R1 ran — then a
   level will hit its wall timeout.
4. **WHAT HAPPENS THEN, registered now:** `rc = 124`, a `CAP_BREACH.txt`, and the level is
   **NOT rule-4 complete**. No Roache triple can exist (rule 5 clause 1), so the rung is
   **NOT A RESULT** — reported with the measured throughput of the failing level beside it,
   which makes the next re-registration cheap.
5. **AND WHAT DOES NOT HAPPEN:** the cap is **NEVER extended mid-run**, and no level is
   ever restarted into its own directory. The answer to a cap-stop is a **new
   pre-registration with a new cap**, frozen before it runs, exactly as R1b is to R1. **An
   overrun stops the run; it does not get a new budget.**
6. **A cap-stop under this cap would be a different finding from R1's**, and that
   distinction is registered now: R1's cap could not reach `endTime` even at the *measured*
   rate; R1b's can, at 1.76× margin. A stop here would mean load rose past the §7.4 bound —
   a fact about the box, reportable as such, and not another arithmetic error.

---

## 9. LAUNCH MUST GRADE — the second defect, and how it is closed structurally

**The defect, owned:** `run_suboff_r1_triple.sh` grades only under `--grade`, and the R1
queue entry deliberately did not pass it. Had R1 completed cleanly with the fleet dead,
**it would have produced no verdict at all** — a finished solve and an empty verdict
column. Rule: a run whose verdict depends on somebody being alive to ask for it is not an
unattended run.

**The repair, in `cases/navier_class/SUBOFF/run_suboff_r1b_triple.sh`:**

1. **There is no grade flag.** Not `--grade`, not `--no-grade`. The launcher takes **no
   arguments**; any argument other than `--help` is a refusal. Grading at the end of a
   clean triple is unconditional. **A non-grading run is not merely discouraged — it is
   not expressible.**
2. **A verdict artifact is guaranteed by an EXIT trap.** `write_verdict()` is the only
   writer of `verification/runs/navier_class/SUBOFF/VERDICT.R1b_triple.txt` and latches so
   it writes at most once. An `EXIT` trap (with `TERM`/`INT`/`HUP` routed into it) fires on
   **every** termination path — clean exit, preflight refusal, cap-stop, crash, kill — and
   writes **NOT A RESULT** if nothing got there first. **If that file is absent, the script
   never started.**
3. **The vocabulary is the fixed one** (rule 1): a preflight refusal writes **BLOCKED**; a
   cap-stop, a non-zero rc, or a trap-fired termination writes **NOT A RESULT** with the
   reason; a clean triple runs the pinned grader and the **grader's** verdict is the one
   that counts, in `grade.R1b_triple.out`, with the launcher artifact recording only that
   grading ran.
4. **The queue entry needs no flag to remember**, because there is none: `launch_cmd` is
   the launcher and nothing else.

**THE GUARANTEE WAS EXERCISED, NOT ASSERTED** (2026-09-10, on a scratch copy with `RUNS_DIR`
redirected; the real tree was not written to). A guarantee not shown to fire is not a
guarantee:

| arm | what was done | result |
|---|---|---|
| **A** | launcher invoked with `--grade` (an argument it must now refuse) | rc=2, verdict file written, **`verdict=BLOCKED`** |
| **B** | `SIGTERM` delivered mid-preflight | rc=143, verdict file written, **`verdict=NOT A RESULT`**, reason "written by the EXIT trap" |
| **C** — **the negative control** | identical to B with **`trap on_exit EXIT` removed** | **no verdict file** — which is what proves arm B's verdict came *from the trap* and not from some other path |

Arm C is the planted control the rule-3 principle demands in this setting: a mechanism
not shown able to *fail* has not been shown to *work*.

---

## 10. WHAT THIS PRE-REGISTRATION DOES NOT CLAIM

1. **That `endTime 2500` is enough.** It is defensible on its stated prior basis (§5a) and
   is **not** a prediction that convergence happens by 2500. A `NOT_CONVERGED` at 2500 is a
   finding, reported, never fixed by adding iterations after the fact.
2. **That 400 core-min is enough.** It is 1.85× the measured projection and reaches `N ≈
   4,400` per level against a registered 2,500. It is **not** a promise about a box whose
   load this rung does not control (§8).
3. **That the contention/cache-exit split is known.** §2 Finding 4 says explicitly it is
   not separable from these artifacts. The cap does not depend on the split.
4. **That D1 is experiment-validated.** The `CT_ref` anchor 3.6e-3 is a **MANIFEST /
   engineering** value; the rung is **CODE-VERIFIED / BOUNDED-AGREEMENT** and stays so
   until a title-verified SUBOFF report lands (rule 15).
5. **That anything here is authorised.** This document is **NOT FROZEN**. The freeze sha,
   the queue drop and the launch are the cfd-supervisor's check-4, taken personally. **No
   agent message is Sanaa's consent** (rule 9). **Nothing is sent, filed, uploaded or
   posted** (rule 7).

---

## 11. FREEZE BLOCK — *empty; to be completed by the cfd-supervisor at check-4*

**NOT YET FROZEN.** At freeze the supervisor pins the grading path by blob sha, verifies
`disk == HEAD` for each, and records the freeze commit. The paths that must be pinned:

| blob sha | path |
|---|---|
| *(to be pinned at freeze)* | `cases/navier_class/SUBOFF/grade_suboff.py` |
| *(to be pinned at freeze)* | `cases/navier_class/SUBOFF/build_suboff.py` |
| *(to be pinned at freeze)* | `cases/navier_class/SUBOFF/run_suboff_r1b_triple.sh` |
| *(to be pinned at freeze)* | `verification/runs/navier_class/SUBOFF/suboff_reference_ReL1p2e7.json` |

**FREEZE PRECONDITIONS for the supervisor to verify first-hand, not relayed:**

| precondition | how to check it |
|---|---|
| §4a run roots still do not exist | `ls verification/runs/navier_class/SUBOFF/` shows no `r1b_*` |
| §4a mesh pins still match the R1 source roots | `sha256sum` the fifteen mesh files against the launcher's `PIN` table |
| the three `system/` dictionaries are still one blob each | `sha256sum` `controlDict`/`fvSolution`/`fvSchemes` across `reg_*`, all three equal |
| `endTime 2500`, `deltaT 1`, no `residualControl` | on disk in each source root; the launcher re-checks and refuses |
| the launcher cannot be run without grading | `bash run_suboff_r1b_triple.sh --grade` must exit 2; §9 arms A/B/C re-run on a scratch copy |
| the queue entry carries `grading_freeze` and the real freeze sha | `scripts/queue_entry_check.py` on the queued copy with `--require-binding` |
| §7 caps transcribed into the launcher without drift | `SUBCAP_COREMIN` = 46/103/231, `TIMEOUT_S` = 2760/6180/13860, `CAP_COREMIN_REGISTERED` = 400 |

*Results, when they exist, land in `verification/campaign/SUBOFF_R1b_RESULTS.md` citing
this file by commit hash. Once frozen this file is never edited, only appended to as dated
addenda that cannot alter a gate, threshold, cap or label.*
