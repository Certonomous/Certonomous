# M1-C — COMPLETION OF THE SIX CAPPED M1 ARMS

**STATUS: DRAFT. NOT FROZEN. NOT COMMITTED. NOT FILED. NOT LAUNCHED.**
**No compute has been spent against this document and none may be until
closure-supervisor has performed SUPERVISION_CHARTER §3 check 4 personally and
committed this file.** Every `prereg_commit` field in
`QUEUE_ENTRIES_DRAFT/` carries a deliberately invalid placeholder, so the queue
validator refuses every entry today. That refusal is the intended state.

| field | value |
|---|---|
| rung id | `M1c` |
| drafted | 2026-08-31 by a closure `lab-lane` at the supervisor's instruction |
| drafted against repo HEAD | `becd0863d98c20946ba05ab6f48c5094208869e6` |
| parent registration | `cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md`, frozen `73cd5ac578c4916a07ae05a9618e166832fdef75` |
| grading path | **`PENDING`** — see §8. This document fixes **no** grading path and computes **no** physics functional. |
| what changes vs M1 | **the cost basis, the per-entry estimate and the per-entry cap. Nothing else.** |

---

## 1. WHY THIS IS A NEW REGISTRATION AND NOT AN AMENDMENT TO M1

### 1.1 The rule, and what it actually forbids

Standing rule 12: *"An overrun **stops the run**; it does not get a new budget."*

**These six arms did not overrun.** Each was stopped **at** its registered cap,
by the mechanism the registration installed for that purpose, and each recorded
the stop from an independent witness. Read from each arm's own `STATUS`
[MEASURED]:

`rc=124`, `capped=1`, `cap_core_min_exceeded=1`,
`note=CAP_EXPIRED_wall_ge_timeout`, and `timeout_s` exactly equal to
`ceil(cap_core_min × 60 / ranks)` of the M1-registered cap.

The budget guard **worked**. It fired, it fired at the registered number, and it
recorded the firing honestly. What failed is **the cost prediction that set the
number** — M1 §9.1's single blended point rate of 3.30 µs per cell-iteration.

Rule 12 forbids handing a stopped run *more budget on the same authority*: it
forbids the move where a gate is loosened after the answer starts arriving,
because the person doing the loosening has already seen how the run is going.
That is not what M1-C is. M1-C is **a new pre-registration, with a fresh and
independently measured cost basis, its own cap, and its own freeze**, decided in
full view of what the first attempt measured. That fresh decision, taken
deliberately and frozen before compute, is precisely the thing rule 12 exists to
require in place of a quiet budget top-up.

### 1.2 The distinction stated so it cannot be blurred

* **M1 has consumed compute. Its gates are CLOSED.** Under rule 2, changes to it
  land only as dated addenda that *cannot alter a gate, threshold, cap or label*.
* **A cap is one of the four things an addendum may not alter.** So M1's caps
  cannot be raised by any instrument, and this document does not attempt it.
  M1's registered caps stand exactly as frozen at `73cd5ac5`.
* **M1-C therefore does not amend M1, does not cite M1's freeze as its own
  authority, and does not reuse M1's run roots.** It is a separate rung with a
  separate freeze, separate run roots, separate queue entries and a separate
  cost ledger row.
* **The six M1 runs remain exactly what they are: capped, incomplete, and not a
  result under standing rule 4.** M1-C does not relabel them, does not complete
  them, and does not repair them in place. It produces *new* runs.

### 1.3 What is lost if this is not done

M1 is a **paired two-arm comparison**. Post-sweep, from
`/home/ubuntu/closure-data/m1_completion_sweep_2026-08-31.json` [MEASURED]:

| pair state | cases | consequence |
|---|---|---|
| both arms complete | 35 | comparable |
| both arms capped (`PH_Breuer`, `AR_1_Ret_180`) | 2 | **symmetrically absent** — comparable in their absence |
| **kOmega capped, kOmegaSST_null complete** (`AR_14_Ret_180`, `AR_7_Ret_180`) | **2** | **ASYMMETRIC — usable for no model-to-model comparison at all** |

An asymmetric pair is the expensive failure: one arm's number exists and invites
use, and using it compares a model against nothing. Completing the four
`kOmega`-side arms restores both broken pairs; completing the two symmetric
pairs restores 39/39 on both arms.

---

## 2. WHAT IS INHERITED VERBATIM

M1-C changes the cap and the basis that sets it. **It changes no physics
setting, no band, no threshold and no label.** Everything below is inherited by
identity, not by re-derivation, and each was verified byte-identical on disk, at
HEAD `becd0863`, and at the M1 freeze `73cd5ac5` in one invocation [MEASURED]:

| inherited artefact | sha256 (identical on disk / HEAD / `73cd5ac5`) |
|---|---|
| `cases/RANS_LES_closure_models/M1_multimodel_sweep/run_m1.sh` | `3d5b59f7803878ed75af50fca555cd2197e3fccbe7dfa9c433ae13c7aa771836` |
| `cases/RANS_LES_closure_models/M1_multimodel_sweep/stage_m1.py` | `5739d0601867f01d5a721522f31556e87c32a4d49b4353e9f9035311ace5bb2c` |
| `cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md` | `e15d0df3ee960b907b50a978db864cd1a112cd4723274f7bd2876df643d87572` |

Inherited **unchanged**, all [REGISTERED]:

* iterations / `endTime` = **20000**; `deltaT` 1; `startFrom startTime`;
  `writeControl timeStep`; `writeInterval 20000`
* solver **`simpleFoam`**, OpenFOAM v2606 at
  `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/simpleFoam`
* **`ranks = 1`**, `OMP_NUM_THREADS=1`
* the two arms `kOmega` (`RASModel kOmega`) and `kOmegaSST_null`
  (`RASModel kOmegaSST`), and `run_m1.sh`'s arm/`RASModel` cross-check
* the same case definitions, staged from the same source root
  `/home/ubuntu/closure-challenge-benchmark/data` by the same `stage_m1.py`
* the age datum `0/U`, touched last, per `run_m1.sh` §5
* `fvSchemes`, `fvSolution`, `constant/`, `fieldDef` — untouched
* the driver `run_m1.sh` itself, invoked as `/bin/bash run_m1.sh …`
* **the cap margin factor ×1.458** — M1 §9.2's own registered per-entry cap
  factor (`cap = cells × 20000 × 4.010e-6 × 1.20 / 60`, giving
  `cap/estimate = 4.010 × 1.20 / 3.30 = 1.4582`). M1-C keeps that policy verbatim
  and replaces only the **estimate** it multiplies.

**Changed, and only this:** `cost_core_min_estimate`, `cap_core_min_registered`,
`--timeout-s`, `cwd`, and the run-root path. Nothing else.

---

## 3. THE SIX ARMS AND THE STATE THEY ARE IN

All [MEASURED], from `/home/ubuntu/closure-data/m1_completion_sweep_2026-08-31.json`
and from each arm's own `log.run` and `STATUS`:

| # | arm | case | cells | reached | of 20000 | wall_s | M1 cap (core-min) | `rc` | `note` | time dirs on disk |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `kOmega` | `AR_14_Ret_180` | 31,819 | 16,879 | 84.4 % | 3063 | 51.038 | 124 | `CAP_EXPIRED_wall_ge_timeout` | `0` only |
| 2 | `kOmega` | `AR_7_Ret_180` | 15,463 | 19,628 | 98.1 % | 1489 | 24.803 | 124 | `CAP_EXPIRED_wall_ge_timeout` | `0` only |
| 3 | `kOmega` | `PH_Breuer` | 15,600 | 13,301 | 66.5 % | 1502 | 25.022 | 124 | `CAP_EXPIRED_wall_ge_timeout` | `0` only |
| 4 | `kOmegaSST_null` | `PH_Breuer` | 15,600 | 13,188 | 65.9 % | 1502 | 25.022 | 124 | `CAP_EXPIRED_wall_ge_timeout` | `0` only |
| 5 | `kOmega` | `AR_1_Ret_180` | 2,209 | 18,058 | 90.3 % | 213 | 3.543 | 124 | `CAP_EXPIRED_wall_ge_timeout` | `0` only |
| 6 | `kOmegaSST_null` | `AR_1_Ret_180` | 2,209 | 14,364 | 71.8 % | 213 | 3.543 | 124 | `CAP_EXPIRED_wall_ge_timeout` | `0` only |

### 3.1 NO RESTART POINT EXISTS. M1-C RE-RUNS FROM ITERATION 0.

`system/controlDict` on every one of the six carries `writeControl timeStep;`
with `writeInterval 20000;` [MEASURED, read from
`/home/ubuntu/closure-data/multimodel_sweep/kOmega/PH_Breuer/system/controlDict`
and matching on all six]. **The only write in the whole run is at iteration
20000.** Every capped arm therefore holds `0/` and nothing else — the sweep
records `numeric_time_dirs = ["0"]` and `largest_time_dir = null` on all six
[MEASURED].

**Consequence, and it governs every number in §5:** there is nothing to restart
from. M1-C cannot "finish the remaining iterations"; it must run **0 → 20000
afresh**. Every cap below is sized for the **full 20000 iterations**, never for
the remainder. A cap sized for the remainder would be a cap that stops the run
before it reaches the point the first attempt already reached.

---

## 4. THE COST BASIS — MEASURED PER ARM, NEVER A SINGLE BLENDED RATE

### 4.1 How M1's basis failed, in both directions at once

M1 §9.1 registered **one point rate: 3.30 µs per cell-iteration**, envelope
2.387–4.010, sampled from four cases. Against the completed sweep the blended
rate was wrong in *both* directions [MEASURED, from the 72 complete arms' own
`log.run` ClockTime]:

| family | cases | measured µs per cell-iteration | vs the 3.30 µs basis |
|---|---|---|---|
| `hill` (`alpha_*`, 15,600 cells) | 29 of 39 | ≈ **1.2–1.4** | over-predicted by ≈ 2.4–2.7× |
| `DUCT` / `PH_Breuer` / `CBFS` | 10 of 39 | ≈ **4.3–24** | under-predicted by 1.3–7× |

A single rate could not be right for both, and it was not. **This is the whole
reason M1-C exists, and it is why no blended rate appears anywhere below.**

A rate is also **not scale-invariant and not condition-free**. `G2` measured
6.10e-06 / 5.22e-06 / 4.99e-06 s per cell-iteration at three grid levels of the
same case [MEASURED], and three consecutive ETAs on one chain were wrong by up
to 2.8× because they extrapolated a rate sampled under contention (C-190, C-210).
**A rate carries the load and the problem size it was measured under.** §4.2 and
§4.4 name both for every number here.

### 4.2 The basis: each arm's own partial run, on this hardware, at this size

Each of the six has a real `log.run` recording `ClockTime` against iteration
number, produced by `simpleFoam` on **this** box, at **this** cell count, at
**ranks 1**. That is the only basis M1-C uses. The projection rule:

```
r        = the ClockTime slope over a late window of THIS arm's own log   [MEASURED]
base_s   = ClockTime(last_iter) + r x (20000 - last_iter)                 [EXTRAPOLATED]
est_s    = base_s x contention_uplift                                     [EXTRAPOLATED]
estimate = est_s / 60                          core-minutes at ranks 1
cap      = estimate x 1.458                    M1's own registered margin factor
timeout_s= ceil(cap x 60 / ranks)              the form run_m1.sh enforces
```

`ClockTime(last_iter)` is a **measurement of the time this arm actually took to
get from iteration 0 to `last_iter` on this box**, so `base_s` is a projection of
the *full* 0→20000 run, which is what M1-C will execute.

**The projection is [EXTRAPOLATED], never [MEASURED].** The arithmetic is exact
and the inputs are real, but the output is an evidence claim about a run that has
not happened.

### 4.3 The late-window rule was validated against two completed siblings

The method was tested where the truth is known [MEASURED, then compared]. Two
`kOmegaSST_null` arms completed all 20000 iterations. Their logs were truncated
at the iteration counts the failed arms reached, the §4.2 rule was applied to the
truncated data alone, and the projection compared to the arm's actual total:

| complete arm | truncated at | projected total | **actual total** | pred/actual |
|---|---|---|---|---|
| `kOmegaSST_null/AR_14_Ret_180` | 13,300 | 2943.1 s | 2883.0 s | **1.021** |
| `kOmegaSST_null/AR_14_Ret_180` | 16,879 | 2892.9 s | 2883.0 s | **1.003** |
| `kOmegaSST_null/AR_7_Ret_180` | 13,300 | 1418.0 s | 1419.0 s | **0.999** |
| `kOmegaSST_null/AR_7_Ret_180` | 19,628 | 1418.2 s | 1419.0 s | **1.000** |

**Measured method error: within +2.1 % / −0.1 %** on stationary-cost cases. The
method is not assumed to work; it has been shown to work, on this family, on this
box, against known answers.

### 4.4 Contention: measured where it could be, declared unmeasured where it could not

The M1 arms ran alongside each other. Mean simultaneous single-rank solver
processes during each arm's own window, from the `started_utc`/`finished_utc`
spans of all 78 arms [MEASURED]:

| arm | mean concurrent processes | peak |
|---|---|---|
| `kOmega/AR_14_Ret_180` | 6.08 | 9 |
| `kOmega/AR_7_Ret_180` | 6.16 | 7 |
| `kOmega/PH_Breuer` | 6.06 | 7 |
| `kOmegaSST_null/PH_Breuer` | 8.99 | 11 |
| `kOmega/AR_1_Ret_180` | **1.00** | 1 |
| `kOmegaSST_null/AR_1_Ret_180` | **1.00** | 1 |

Sensitivity was measured by binning each arm's own log into ten intervals and
regressing per-iteration cost against the box concurrency during that interval
[MEASURED, on arms whose pressure-solver iteration count is flat, so the cost
variation is not physics]:

| arm | d(s/iter)/d(process) | as % of that arm's mean rate |
|---|---|---|
| `kOmegaSST_null/AR_14_Ret_180` | +0.002671 | **+1.85 %/process** |
| `kOmegaSST_null/AR_7_Ret_180` | +0.001771 | **+2.50 %/process** |
| `kOmega/AR_14_Ret_180` | +0.007921 | **+4.37 %/process** |
| `kOmega/AR_7_Ret_180` | −0.000529 | **−0.70 %/process** |

**Honest reading:** the fits are noisy and one is negative; the range
−0.70 %…+4.37 % per process is a bound, not a clean coefficient. The **two
`AR_1_Ret_180` regressions are discarded outright** — concurrency was constant at
1.00 for their whole run, so the regressor has no variance and the reported
"238 %/process" slope is an artefact of dividing by zero variance, not a
measurement. It is named here so nobody later mistakes it for one.

**How this enters the caps:**

* Arms 1–4 were measured at concurrency **6.1–9.0**. M1-C is six arms; at worst
  it runs at concurrency 6, **at or below** what their rates were measured under.
  Their rates are therefore already conservative. **Uplift ×1.000.**
* Arms 5–6 (`AR_1_Ret_180`) were measured **alone on the box**. If M1-C runs all
  six at once they see 5 extra processes. At the conservative measured
  +4.37 %/process that is **×1.2185**, applied explicitly [DERIVED from the
  measured coefficient, not measured on those arms].

### 4.5 `PH_Breuer`: the cost driver is a pressure solver pinned at `maxIter`

`PH_Breuer` is the one arm-pair whose cost is **not stationary**, and treating it
like the others would have set a cap that fails again. Binned per-iteration cost
and mean pressure-solver linear iterations, both arms [MEASURED from their own
`log.run`]:

| iteration band | `kOmega` s/iter | `kOmega` mean `p` iters | `kOmegaSST_null` s/iter | `kOmegaSST_null` mean `p` iters |
|---|---|---|---|---|
| first tenth | 0.065 | 30.6 | 0.062 | 27.6 |
| middle | 0.074–0.092 | 34–44 | 0.058–0.087 | 26–40 |
| ninth tenth | **0.169** | **93.7** | **0.241** | **141.1** |
| final tenth | **0.326** | **193.7** | **0.336** | **194.3** |

The cost rise tracks the pressure-solver iteration count exactly, it begins at
roughly iteration 10,600, and **it happens on both arms** — which ran on
different nights at different concurrency (6.06 vs 8.99). It is therefore a
property of the case, not of the box's load.

**And it has a ceiling that can be read off the case's own dictionary.**
`system/fvSolution` sets the `p` GAMG solver `maxIter 200` [MEASURED]. Over the
final **1,737 pressure solves** of `kOmega/PH_Breuer` the count is **exactly 200**
[MEASURED], and `Ux` linear iterations have fallen to a mean of 0.0 over the last
500 steps. **The per-iteration cost cannot rise further from this source: the
dominant solver is already at its maximum permitted iteration count.**

M1-C therefore prices both `PH_Breuer` arms at the **saturated slope** — the
ClockTime slope over the contiguous final window in which `p` is pinned at 200 —
rather than at the late-window slope, because the late-window slope was still
climbing when the cap fired:

| arm | pinned-at-200 window | **saturated slope** | µs per cell-iteration | (late-2000 slope, for contrast) |
|---|---|---|---|---|
| `kOmega/PH_Breuer` | iters 13,145–13,300 | **0.341935 s/iter** | 21.92 | 0.303 |
| `kOmegaSST_null/PH_Breuer` | iters 12,996–13,187 | **0.371728 s/iter** | 23.83 | 0.326 |

This is the strongest bound available: it is measured, it is an upper bound by
construction, and it was measured **under contention**, so a quieter box makes it
more conservative still.

**Flagged for the supervisor, and deliberately not acted on here.** A run whose
pressure solver sits at `maxIter 200` with `relTol 0.001` unmet for the last 13 %
of its iterations is a numerical finding. Whether it bears on any gate is the
supervisor's call and the successor grader's, **not this document's** — M1-C
computes no physics functional, changes no threshold, and takes no view. It is
recorded here only because it is what sets the cost.

---

## 5. THE REGISTERED NUMBERS

### 5.1 Per arm

`r` is the slope basis actually used; `base` is the projected full 0→20000 wall
time before any contention uplift.

| # | arm / case | reached | `ClockTime` there | **`r` used (s/iter)** | basis for `r` | µs/cell-it | `base` (s) | uplift | **estimate (core-min)** | **cap ×1.458 (core-min)** | `--timeout-s` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `kOmega/AR_14_Ret_180` | 16,878 | 3063 | **0.173000** | last-2000 slope | 5.44 | 3603 | ×1.000 | **60.052** | **87.555** | **5254** |
| 2 | `kOmega/AR_7_Ret_180` | 19,627 | 1489 | **0.080000** | last-2000 slope | 5.17 | 1519 | ×1.000 | **25.314** | **36.908** | **2215** |
| 3 | `kOmega/PH_Breuer` | 13,300 | 1502 | **0.341935** | p-saturated (`maxIter 200`) | 21.92 | 3793 | ×1.000 | **63.216** | **92.169** | **5531** |
| 4 | `kOmegaSST_null/PH_Breuer` | 13,187 | 1502 | **0.371728** | p-saturated (`maxIter 200`) | 23.83 | 4035 | ×1.000 | **67.243** | **98.040** | **5883** |
| 5 | `kOmega/AR_1_Ret_180` | 18,057 | 213 | **0.011000** | last-2000 slope | 4.98 | 234 | ×1.2185 | **4.760** | **6.940** | **417** |
| 6 | `kOmegaSST_null/AR_1_Ret_180` | 14,363 | 213 | **0.014500** | last-2000 slope | 6.56 | 295 | ×1.2185 | **5.986** | **8.727** | **524** |
| | **TOTAL** | | | | | | | | **226.570** | **330.339** | |

Every `r` is [MEASURED] from that arm's own `log.run`. Every `base`, `estimate`
and `cap` is [EXTRAPOLATED].

### 5.2 Against what M1 registered

| arm / case | M1 est | M1 cap | M1-C est | M1-C cap | est ratio |
|---|---|---|---|---|---|
| `kOmega/AR_14_Ret_180` | 35.001 | 51.038 | 60.052 | 87.555 | **×1.72** |
| `kOmega/AR_7_Ret_180` | 17.009 | 24.803 | 25.314 | 36.908 | **×1.49** |
| `kOmega/PH_Breuer` | 17.160 | 25.022 | 63.216 | 92.169 | **×3.68** |
| `kOmegaSST_null/PH_Breuer` | 17.160 | 25.022 | 67.243 | 98.040 | **×3.92** |
| `kOmega/AR_1_Ret_180` | 2.430 | 3.543 | 4.760 | 6.940 | **×1.96** |
| `kOmegaSST_null/AR_1_Ret_180` | 2.430 | 3.543 | 5.986 | 8.727 | **×2.46** |
| **sum (these six)** | **91.190** | **132.971** | **226.570** | **330.339** | **×2.48** |

### 5.3 Cost, and the honest label on the dollars

| quantity | core-min | core-h | $ at $0.0513/core-h |
|---|---|---|---|
| **M1-C registered estimate** | **226.570** | 3.7762 | **$0.1937** |
| **M1-C registered cap** | **330.339** | 5.5057 | **$0.2824** |

`ranks = 1` on every arm, so core-minutes = wall seconds ÷ 60 exactly.

**Every dollar figure is DERIVED, NOT MEASURED.** The rate **c7a.4xlarge at
$0.0513/core-h** is **owner-stated** (2026-08-21/22, corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`) and **this box cannot read its own
billing** (`COMPUTE_BUDGET_CHARTER.md` §5) — [REPORTED-BY-OWNER].

At the cap, $0.28 — far inside the pre-authorised $25/run and inside the
2026-08-21 blanket. **Costed anyway, because a blanket is not a per-item read**
(standing rule 9).

### 5.4 An overrun stops the run

Standing rule 12 applies to M1-C exactly as it applied to M1. `run_m1.sh`
enforces each cap as a wall-clock `timeout` of `ceil(cap_core_min × 60)` seconds
and records `capped` **from the wall clock, an independent witness, never from
the rc**. **If an M1-C arm hits its M1-C cap, it stops and it does not get a
third budget under this document's authority.**

### 5.5 Two things the supervisor must rule on, flagged rather than decided

1. **Three caps exceed the 3600-wall-second stall heuristic** (rule 12: *"a row
   over 3600 wall s is a stall"*): arms 1 (5254 s), 3 (5531 s) and 4 (5883 s).
   These are legitimately long runs, not stalls, but the heuristic will flag them
   in any spend review and the calibration row should say so in advance.
2. **`M1_kOmega__AR_1_Ret_180` and `M1_kOmegaSST_null__AR_1_Ret_180` are marked
   `excluded_by_supervisor: true` in the completion sweep** [MEASURED], and the
   sweep's cost actuals are computed over a 76-arm set that drops exactly those
   two. **The reason for that exclusion is not stated in M1's own
   `PREREGISTRATION.md` — its only registered exclusion is `NASA_2DWMH` (§2.2).**
   Draft entries for both are provided, but **whether they belong in M1-C is the
   supervisor's ruling, not this lane's.** If they are out, drop entries 5 and 6
   and the totals become **215.825** core-min estimate / **314.672** core-min cap.

---

## 6. THE BIRTH GUARD — SOLVED, NOT DEFEATED

Standing rule 4's guard refuses a case where `0/` or a time directory already
exists. All six M1 roots hold `0/` and a 13–24 MB `log.run`. **The guard is
correct. It is not disabled, not weakened, and nothing is deleted to get past
it.**

### 6.1 The six M1 roots are evidence and stay byte-untouched

* M1-C **writes nothing** under `/home/ubuntu/closure-data/multimodel_sweep/`.
  No file there is deleted, moved, renamed, truncated, re-run or tidied.
* Before this document was written, the drafting lane took a byte fingerprint of
  all six roots — every file's size, mtime and sha256 — and filed it at
  `cases/RANS_LES_closure_models/M1c_multimodel_sweep_completion/artefacts/m1c_evidence_untouched_manifest_2026-08-31.json`
  (50,290 bytes; 46–48 files per root). **Re-running that walk and comparing is a
  mechanical proof that the six roots were not touched**, available to any later
  reader without trusting this sentence.

### 6.2 M1-C builds fresh roots at a new path

**`/home/ubuntu/closure-data/m1c_completion/<ARM>/<CASE>/`**

The six directories exist and are **empty** — `find … -type f` returns 0
[MEASURED]. Empty is exactly the state both queue-validator clauses want:

* `check_age_guard` — the directory exists and contains **no** time directory, so
  the clause is satisfied by a positive reading, not by absence.
* `check_cwd_launchable` (`EXEC`) — the directory **exists**, so
  `queue_runner.py`'s `chdir` (`:286`) and `Popen(cwd=)` (`:293`) cannot raise
  `FileNotFoundError` behind an already-written `LAUNCHED` record. This is the
  D540 / L-353 failure and it is closed by construction, not by hope.

### 6.3 Staging is a separate, deliberate pre-launch step — deliberately not done yet

The roots are empty, so `run_m1.sh` would **REFUSE** today (`REFUSE: no 0.orig to
arm from`). That is the correct fail-closed state for a draft.

Staging needs **no new code**: `stage_m1.py` already takes `--dst-root`
(default `/home/ubuntu/closure-data/multimodel_sweep`). The M1-C launch sequence
is therefore, in order, and **all of it after the freeze**:

```
python3 cases/RANS_LES_closure_models/M1_multimodel_sweep/stage_m1.py \
    --dst-root /home/ubuntu/closure-data/m1c_completion \
    --arm <ARM> --case <CASE> --execute
```

per arm, then the queue entry. `--src-root` keeps its default
`/home/ubuntu/closure-challenge-benchmark/data` — the same read-only benchmark
tree M1 staged from — so the case definitions are identical by construction and
`multimodel_sweep` is never read from or written to.

**This lane did not run it**, so that the supervisor stages from whatever
`stage_m1.py` blob the M1-C freeze commit fixes, rather than from a working tree
that may move. `stage_m1.py`'s post-guard `R6_no_time_dirs` gives a second,
independent birth check at staging time.

### 6.4 How a reader tells an M1-C root from an M1 root

Four independent tells, any one sufficient:

1. **Path.** `…/closure-data/m1c_completion/…` vs `…/closure-data/multimodel_sweep/…`.
   Disjoint trees; neither is inside the other.
2. **`case_id`.** M1-C entries are `M1c_<ARM>__<CASE>`; M1's are `M1_<ARM>__<CASE>`.
   The `STATUS.<case_id>` sidecar `run_m1.sh` writes carries it into the run root.
3. **`STATUS`.** `cap_core_min` and `timeout_s` differ on every one of the six —
   e.g. `PH_Breuer` reads `25.022 / 1502` under M1 and `92.169 / 5531` under M1-C.
4. **Prior-art record.** `artefacts/m1c_evidence_untouched_manifest_2026-08-31.json`
   enumerates the M1 roots by name with their pre-M1-C hashes.

There is no staging manifest collision: `stage_m1.py` writes
`STAGING_MANIFEST_M1.json` **at its `--dst-root`**, so M1-C's lands under
`m1c_completion/` and M1's under `multimodel_sweep/` is not touched.

---

## 7. WHAT M1-C DOES **NOT** DO

Stated as prohibitions because each is a way this document could be misread into
authorising something it does not:

* It does **not** amend M1, reopen M1's gates, alter M1's caps, or relabel M1's
  six capped runs. Those remain capped and incomplete.
* It does **not** change a physics setting, a band, a threshold or a label.
* It does **not** fix, weaken or bypass the rule-4 birth guard.
* It does **not** define, write, touch or duplicate a grader. `grade_m1.py` is
  not read, not imported, not run and not modified by anything here.
* It does **not** compute any physics functional value, any residual verdict, any
  gate outcome, or any convergence classification.
* It does **not** grant itself authority to launch. §8 governs that.

---

## 8. GRADING PATH: **`PENDING`**

**M1-C fixes no grading path, and this is deliberate.**

`grade_m1.py` was found to contain **no fatal or crash channel at all across 988
lines** — zero occurrences of `FOAM FATAL`, `Floating point exception` or
`sigFpe` [MEASURED, reported by the supervisor]. It is recognition-controlled: it
cannot see the failure modes it does not name. A successor, `M1b`, is under
draft by a separate lane at
`cases/RANS_LES_closure_models/M1b_multimodel_sweep_regrade/grade_m1b.py`.

Naming a grading path M1-C cannot vouch for would be worse than naming none, and
inventing a second one would duplicate M1b's work and produce two records for one
run. So:

> **Grading path: `PENDING`.** M1-C's grading path is the M1b successor
> comparator, and it is fixed at the M1-C freeze commit — not before, and not by
> this lane. Until then M1-C's rows carry `PENDING`, which is a queue state and
> **never** a softened `GATE FAIL` (standing rule 1).

Under standing rule 2 the grading path is fixed at the pre-registration commit
and verified by hashing the frozen file against the committed blob. **The
supervisor must fill this section with the successor's path and sha256 before
freezing**, or M1-C is not frozen.

---

## 9. THE SIX DRAFT QUEUE ENTRIES

`QUEUE_ENTRIES_DRAFT/M1c_<ARM>__<CASE>.json`, six files. **DRAFTS. NOT FILED.**
They are not in `verification/queue/closure/` and nothing has enqueued them.

Three fields need saying out loud:

* **`prereg_commit` is a deliberately invalid placeholder**
  (`PLACEHOLDER-NOT-A-SHA-replace-at-M1c-freeze`). The M1-C freeze commit does
  not exist yet, so no true value can be written. The validator's `SCHEMA`
  clause refuses it at `queue_entry_check.py:186` for not being 40 lowercase hex
  — **an abbreviated sha would fail the same clause, and a real-looking sha for a
  commit that does not carry this document is the laundering shape
  `PREREG-AT-COMMIT` exists to catch.** A loud placeholder is the honest form.
  The supervisor replaces all six at freeze.
* **`cwd` exists.** Verified empty and present before these entries were written.
  A missing `cwd` kills an item at launch, *outside its own error handling and
  behind a `LAUNCHED` record already written* — D540 / L-353.
* **`host` is absent, deliberately.** `queue_runner.py:785` defaults it to
  `"local"` [verified by reading that line]. Writing it would add a field the
  runner would have supplied and that nothing here has authority over.

**`enqueued_by` claims nothing.** It records, in each entry, that
**SUPERVISION_CHARTER §3 check 4 has NOT been performed**. Check 4 —
pre-registration committed before compute — is the supervisor's own and may never
be delegated. A lane writing that field as done would be manufacturing the
supervisor's non-delegable act, and no lane may do that.

---

## 10. FREEZE CHECKLIST — WHAT THE SUPERVISOR MUST DO, IN ORDER

Nothing below has been done. Each is the supervisor's.

1. Read §1 and confirm the rule-12 argument holds. **If it does not, M1-C stops
   here** and the six arms stay capped.
2. Rule on §5.5 item 2: are the two `AR_1_Ret_180` arms in or out of M1-C?
3. Fill §8 with the successor grading path and its sha256. **M1-C is not frozen
   without it.**
4. Commit this document — per-item, private-index protocol, **never** a bare
   `git commit`, **never** `git add -A`. The shared index carries ~394 staged
   deletions of files present on disk and in HEAD; a bare commit would delete
   them.
5. Perform **SUPERVISION_CHARTER §3 check 4 personally**: this document committed
   before any compute; its disk sha256 equal to the committed blob; **all six
   M1-C run roots hold zero time directories and zero field files.**
6. Replace `prereg_commit` in all six entries with the real 40-hex freeze sha and
   re-run `scripts/queue_entry_check.py` — it must reach **rc 0**.
7. Rewrite `enqueued_by` in the supervisor's own words, recording check 4 as
   performed, with the date and the sha.
8. Stage the six roots (§6.3) from the frozen `stage_m1.py` blob.
9. Copy the entries into `verification/queue/closure/` and re-validate **in
   place** with `--require-binding`. That run is the validation that counts.

---

## 11. PROVENANCE OF EVERY NUMBER IN THIS DOCUMENT

| number | tag | artefact |
|---|---|---|
| the six arms' `rc`, `wall_s`, `capped`, `note`, reached iteration | [MEASURED] | each arm's `STATUS` and `log.run`; sweep at `/home/ubuntu/closure-data/m1_completion_sweep_2026-08-31.json` |
| cells per case | [MEASURED] | M1 `PREREGISTRATION.md` §2.3, re-derived from staged `polyMesh/owner` by `stage_m1.py` guard R15 |
| every `r` (s/iteration) | [MEASURED] | ClockTime slope in that arm's own `/home/ubuntu/closure-data/multimodel_sweep/<ARM>/<CASE>/log.run` |
| `p` linear-iteration counts, `maxIter 200` | [MEASURED] | the same `log.run`; `system/fvSolution` |
| concurrency (mean, peak) | [MEASURED] | `started_utc`/`finished_utc` of all 78 arms in the sweep JSON |
| contention coefficients | [MEASURED] fit, noisy | binned regression of the arms' own logs; the two `AR_1` fits **discarded**, §4.4 |
| the ×1.2185 uplift on arms 5–6 | [DERIVED] | +4.37 %/process × 5 processes |
| method error +2.1 %/−0.1 % | [MEASURED] | truncate-and-project against two completed siblings, §4.3 |
| `base`, `estimate`, `cap`, `timeout_s` | **[EXTRAPOLATED]** | §4.2 arithmetic on the measured `r` |
| margin factor ×1.458 | [REGISTERED] | M1 `PREREGISTRATION.md` §9.2, inherited verbatim |
| iterations 20000, `ranks` 1, solver, models, case definitions | [REGISTERED] | M1 `PREREGISTRATION.md`, frozen `73cd5ac5`; sha256 in §2 |
| $0.0513/core-h | [REPORTED-BY-OWNER] | Sanaa 2026-08-21/22; this box cannot read its own billing |
| all dollar figures | [DERIVED] | core-hours × the owner-stated rate |

---

## 12. CROSS-CHECKS AGAINST INDEPENDENT ARMS

Each projection was checked against a second, independent source, and **where
they disagree the larger (conservative) value was taken** — in every case that is
the arm's own self-projection.

**Where a completed sibling exists.** The measured `kOmega`/`kOmegaSST_null`
per-iteration cost ratio across all **35** case-pairs where both arms completed
is **median 1.055**, range 0.827–1.218 [MEASURED]. Scaling each completed sibling
by that median:

| arm | self-projection | sibling actual | sibling × 1.055 | agreement | taken |
|---|---|---|---|---|---|
| `kOmega/AR_7_Ret_180` | **1519 s** | 1419 s | 1497 s | **+1.5 %** — close | self (larger) |
| `kOmega/AR_14_Ret_180` | **3603 s** | 2883 s | 3040 s | **+18.5 %** — **disagrees** | self (larger) |

**The `AR_14_Ret_180` disagreement is stated, not smoothed.** The `kOmega` arm
measured 0.173 s/iter against its `kOmegaSST_null` sibling's 0.1375 — a ratio of
1.26, **outside the 0.827–1.218 range observed across all 35 completed pairs**.
The arm is a genuine outlier against its own family and the cause is not
established here. It ran at *lower* concurrency (6.08) than the sibling (7.60),
so contention does not explain it. **The conservative value is taken and the
anomaly is left visible.**

**Where no sibling exists** (`PH_Breuer` and `AR_1_Ret_180` both failed on both
arms), the two arms cross-check each other — different turbulence models, same
mesh, different nights, different concurrency:

| pair | `kOmega` base | `kOmegaSST_null` base | ratio | reading |
|---|---|---|---|---|
| `PH_Breuer` | 3793 s | 4035 s | 0.94 | **agree within 6.4 %** — independent corroboration of the saturated-ceiling method |
| `AR_1_Ret_180` | 234 s | 295 s | 0.79 | just below the measured 0.827–1.218 band; each arm keeps its own rate, so neither is scaled |

---

**END OF ORIGINAL DRAFT (2026-08-31). NOT FROZEN. NOT COMMITTED. NOT FILED. NO COMPUTE AUTHORISED.**

---

# ADDENDUM 2026-09-09 — GRADING PATH FIXED, CONVERGENCE-READING CLAUSE, CAP RE-SIZE, sec2ba DUAL-MECHANISM PLAN

**FROZEN 2026-09-09 by the closure-supervisor — see the SUPERVISOR FREEZE STAMP at
the foot of this file for the §3 checks, the topology ruling and the §5.5 rulings
that this freeze rests on.**
Added by a closure `lab-lane` on the supervisor's instruction after the chief
GO'd the M1-C completion re-run of the six cap-bound arms. This addendum resolves
the two `PENDING` items the original left to the supervisor (grading path, §8) and
adds the run-standard and completion clauses the build now requires. **Nothing
here has been checked by the supervisor; nothing launches until §3-check-4 is
performed personally and this file is committed.** Where this addendum and the
original disagree on a number (the caps of §5.1), **A.3 governs the queue rows.**

## A.1 GRADING PATH — no longer PENDING; fixed to the FROZEN grade_m1d.py

Supersedes §8. The M1-C grading path is the frozen G1-MODEL_RE-fix successor:

| | |
|---|---|
| grading script | `cases/RANS_LES_closure_models/M1d_multimodel_sweep_g1fix/grade_m1d.py` |
| pinned sha256 | `a1ee190550e94be13fb2fc678379e1c23275b9fd4f002905073776d263628790` |
| freeze commit | `13f1f4d6` |
| gates / thresholds / labels | **inherited VERBATIM from M1 §7** (grade_m1d.py inherits M1b's gate block byte-identical; G0–G4, bands, the 0.01 duct ceiling, the 1e-3 hill band — no widening, no new threshold) |
| on-disk sha256 at this write | `a1ee1905…8790` — **CONFIRMED == pin** (unchanged) |

grade_m1d.py is **re-used verbatim**: not edited, not forked, not re-frozen. The
run-time re-hash-against-pin lives in `autograde_m1c.sh` (A.4) and REFUSES on any
mismatch. Standing rule 2: the grading path is fixed at THIS pre-registration's
freeze commit and verified by hashing the frozen file against the committed blob —
the supervisor confirms `a1ee1905` at freeze.

## A.2 HOW ITERATIVE CONVERGENCE IS READ — continuity/flow-field, never the raw `p` Initial residual (N-X4)

The six arms are streamwise-periodic incompressible ducts / periodic hills with a
**floating pressure reference** (`pRefCell 0; pRefValue 0`). On this family the `p`
**Initial** residual plateaus at O(0.1–0.4) even when the flow field is fully
converged — this is a normalization/floating-reference artifact (**N-X4**), NOT
non-convergence. Verified on the completed rc=0 siblings AR_5/AR_10 (continuity
global ~1e-14, `U/k/omega` Final residuals at solver tolerance, `p` linear solve
healthy at relTol each outer iteration). Therefore, for M1-C:

* Iterative convergence, where any reader needs it, is read from the **continuity
  errors and the flow-field Final residuals**, **never** from the raw `p` Initial
  residual and **never** from a `"SIMPLE solution converged"` line.
* **`residualControl` STAYS EMPTY** (`SIMPLE { residualControl { } }`), exactly as
  in all 78 M1 runs (M1 §4.2, forced by standing rule 4). **Do NOT add a
  `residualControl` block.** With it empty, `"SIMPLE solution converged"` is
  structurally unreachable — its absence in the logs is not evidence of anything,
  and grade_m1d.py does not depend on it (it reads fields at `endTime`, not that line).
* grade_m1d.py's own convergence classifier keys on the **`k` residual sustained to
  `CAP_ITER`** and the CAP-BOUND/CONVERGING state, not on the `p` Initial residual.

## A.3 REVISED PER-ARM WALL CAPS — the MAX rule, so no arm can re-cap

The chief's binding constraint is that the arms **must not re-cap**. The original
§5.1 caps use M1's ×1.458 margin on a measured per-arm basis (with a saturated
slope for `PH_Breuer`). The build task additionally specified a `ceil(2.0 ×
projection)` margin. These two disagree per arm, and **each protects a different
failure mode**:

* **AR (stationary-cost) arms** — a whole-run-average projection is faithful, and
  `2.0×` is the larger, more protective margin (2.0 > 1.458).
* **`PH_Breuer` arms** — cost is **NON-stationary** (the GAMG `p` solver pins at
  `maxIter 200` for the last ~13 % of iterations), so a whole-run-average
  **under-projects**; the naive `2.0×` (4517/4556 s) is actually **below** the
  original draft's saturated-slope cap (5531/5883 s). Here the draft cap protects.

**Registered cap per arm = MAX(ceil(2.0 × naive-projection wall), original §5.1
cap).** This dominates both methods, so neither failure mode can re-cap:

| # | arm / case | reached | proj-to-20000 (core-min) | 2×-naive cap (s) | §5.1 draft cap (s) | **REGISTERED cap = MAX (s)** | **cap (core-min)** |
|---|---|---|---|---|---|---|---|
| 1 | `kOmega/PH_Breuer` | 13301 | 63.216 (saturated) | 4517 | 5531 | **5531** | **92.183** |
| 2 | `kOmegaSST_null/PH_Breuer` | 13188 | 67.243 (saturated) | 4556 | 5883 | **5883** | **98.050** |
| 3 | `kOmega/AR_14_Ret_180` | 16879 | 60.489 | 7259 | 5254 | **7259** | **120.983** |
| 4 | `kOmega/AR_7_Ret_180` | 19628 | 25.287 | 3035 | 2215 | **3035** | **50.583** |
| 5 | `kOmega/AR_1_Ret_180` | 18058 | 3.932 | 472 | 417 | **472** | **7.867** |
| 6 | `kOmegaSST_null/AR_1_Ret_180` | 14364 | 4.943 | 594 | 524 | **594** | **9.900** |
| | **TOTAL cap** | | | | | **22774 s** | **379.567** |

Cost (rule 12): registered **cap = 379.567 core-min = 6.326 core-h = $0.3245**;
realistic **1× projection ≈ 226.57 core-min** (measured-basis) — **$0.1937**.
`ranks = 1`, so core-min = wall s ÷ 60 exactly. **Every $ is DERIVED at the
owner-stated $0.0513/core-h, reported-by-owner, not measured** (this box cannot
read its own billing, COMPUTE_BUDGET_CHARTER §5). At the cap, $0.32 — inside the
pre-authorised $25/run; costed anyway (a blanket is not a per-item read, rule 9).
Three caps exceed the 3600-wall-s stall heuristic (arms 1/2/3): legitimately long,
not stalls — flagged for the spend review as in the original §5.5. **An overrun
stops the run; it does not get a third budget** (rule 12).

## A.4 sec2ba DUAL-MECHANISM RUN PLAN — a detached scheduler AND a live monitor, neither substituting

Per CHARTER §2ba (V-133, `fa038083`): every run needs BOTH a live monitor AND a
detached grader/scheduler that completes + grades against the FROZEN comparator
with no live agent. M1-C's two mechanisms:

1. **Detached scheduler (the SOLVE).** The standing queue daemon
   `scripts/queue_runner.py --daemon` (**pid 1887**, an OS daemon independent of
   any agent) reads the six `verification/queue/closure/M1c_*.json` rows and
   launches each `run_m1.sh` under its wall `timeout`. It is `setsid nohup`-detached
   and survives agent death. It runs the solve; **it does NOT auto-grade** (verified:
   `queue_runner.py` launches the row's argv and records STATUS; it has a
   grader-freeze *gate* that reads pins but launches no grader).
2. **Detached grader (no live agent).** `autograde_m1c.sh` (A.5, this dir),
   launched once `setsid nohup`, re-hashes grade_m1d.py against the pin, waits for
   all six arms to satisfy rule-4, then runs grade_m1d.py **once**, rc captured
   inside the wrapper. **This is the sec2ba grader half and needs no live agent.**
3. **Live monitor.** `monitor_m1c.sh` — read-only progress table of the six arms
   (last `Time`, % of 20000, wall vs cap, rc). It never grades and never writes to a
   run tree. **This is the sec2ba live-monitor half.** Neither (2) nor (3)
   substitutes for the other.

**GRADING TOPOLOGY — FLAGGED FOR THE SUPERVISOR.** grade_m1d.py grades the full
78-arm sweep from a single `--root` and gate G0 requires 78/78 complete. The six
M1-C runs live in the disjoint tree `/home/ubuntu/closure-data/m1c_completion`
(rule-4 birth guard: the M1 roots may not be reused), while the 72 complete M1 arms
stay byte-untouched in `/home/ubuntu/closure-data/multimodel_sweep`. `autograde_m1c.sh`
therefore builds a **read-only MERGED symlink root** (`…/m1c_graded`) — 72 symlinks
into `multimodel_sweep`, 6 into `m1c_completion` — and grades that. Symlinks preserve
real mtimes, so the rule-4 age guard is unaffected, and **no field file in either
evidence tree is written, moved or touched.** This is the one topology choice this
addendum makes that the supervisor should confirm at freeze; the alternative
(grading the 6 alone) yields 72 PENDING and a G0 that cannot see its rows.

## A.5 STRICT rule-4 COMPLETION + PLANTED-ZERO C1 (inherited)

An M1-C arm is **done only if all of it holds** (standing rule 4), checked by
`autograde_m1c.sh:arm_complete()` and, authoritatively, by grade_m1d.py:

* `rc = 0` in the arm's `STATUS` (rc captured **inside** `run_m1.sh`, an
  independent witness — never from `setsid`/`timeout`, which return 0 for every
  outcome);
* an `End` line in `log.run`;
* **last `Time = ` == `endTime` == 20000**;
* fields present at `20000/` (`U` at minimum; grade_m1d.py reads `U k nut`);
* **every field at `20000/` NEWER than the case's own `0/U`** — the age guard
  (`run_m1.sh` touches `0/U` last at launch); a guard refuses a case where `0/` or a
  time dir pre-exists — all six M1-C roots are confirmed empty at this write.
* **Planted-zero C1 control** is inherited via grade_m1d.py's `c1_control()`
  (`PLANT = 1.234e-03`, planted into a field and read back; the comparator REFUSES,
  exit 2, if the reader cannot see the plant). Not re-implemented here.

An overrun, a crash or a missing physics-critical field yields an **INCOMPLETE**
row that grade_m1d.py refuses to degrade into a number; a missing INFRASTRUCTURE
field (a `_launch` bookkeeping field, a cost figure) is a bookkeeping defect
reported beside the verdict and voids only the cost claim, never the physics
(L-342, Bookkeeping-never-voids-physics).

## A.6 WHAT THE SUPERVISOR STILL OWNS (updated freeze checklist)

Additions to §10, none done by any lane:

1. **Diff-read `autograde_m1c.sh`, `monitor_m1c.sh`, `stage_m1c.sh` as diffs**
   (SUPERVISION §3 check 1 — measurement code) before freeze.
2. **Confirm the A.4 merged-symlink grading topology** (or rule an alternative).
3. **Rule on §5.5 item 2** — are the two `AR_1_Ret_180` arms in M1-C? If out, drop
   rows 5 and 6; totals fall to 361.80 s-sum caps less those two.
4. Confirm grade_m1d.py on-disk sha256 `== a1ee1905` at freeze and pin it in §A.1.
5. Replace the placeholder `prereg_commit` in all six `QUEUE_ENTRIES_DRAFT/*.json`
   with the 40-hex M1-C freeze sha; re-run `scripts/queue_entry_check.py` to rc 0;
   rewrite `enqueued_by` in the supervisor's own words recording check 4 performed.
6. Stage via `stage_m1c.sh --execute` (post-freeze, from the frozen `stage_m1.py`
   blob), then copy the six rows into `verification/queue/closure/` — **PH_Breuer
   rows first** — and re-validate in place.

**END OF ADDENDUM.**

---

# SUPERVISOR FREEZE STAMP — 2026-09-09 (closure-supervisor)

This pre-registration is **FROZEN** at the commit that lands this stamp. After this
commit the gates, thresholds, caps and labels are closed; only dated addenda that
cannot alter them may follow (rule 2). I performed the following personally before
freezing (SUPERVISION §3; none delegated):

1. **§3 CHECK-1 DIFF-READ of the three measurement scripts (MINE).** Read
   `autograde_m1c.sh`, `stage_m1c.sh`, `monitor_m1c.sh` as source, not summaries.
   - `autograde_m1c.sh`: SOUND — freeze-gate re-hashes grade_m1d.py against the pin
     and REFUSES (exit 2) on mismatch; grade rc captured INSIDE the wrapper (L:
     setsid/timeout return 0 for every outcome); grades ONCE; TIMEOUT (exit 3) never
     grades a partial sweep; writes no field file in either evidence tree. Two
     cosmetic doc nits (an unused `PHYS_FIELDS` string; the poll's U-only age check)
     are backstopped by grade_m1d.py's own strict G0 — no functional defect.
   - `stage_m1c.sh`: SOUND — wraps the FROZEN `stage_m1.py` verbatim, writes only the
     disjoint `m1c_completion` tree, age-guard fail-closed before staging, DRYRUN default.
   - `monitor_m1c.sh`: SOUND — read-only; no grading, no run-tree writes.
2. **MERGED-SYMLINK GRADING TOPOLOGY (A.4): APPROVED.** Verified from frozen
   grade_m1d.py source: arms come from a constant `ARMS` list and cases from
   `bench_inventory` on the REAL bench tree (line 861); each run is read by
   CONSTRUCTED path `run_root/arm/cid` via `os.path.join`+`isfile`/`isdir`/`getmtime`
   (all symlink-following) — the grader never `os.walk`s `--root`, so a symlinked
   case dir is transparent; `getmtime` reads the real target mtime so the age guard
   is intact; and C1 plants into a tmp COPY (line 887-888), never through the symlink
   into an evidence file. The merged read-only symlink root is sound.
3. **grade_m1d.py ON-DISK sha256 == `a1ee1905…8790` == the A.1 pin — CONFIRMED by my
   own hash.** Re-used verbatim; not edited, not re-frozen (rule 6). Gates inherited
   from M1 §7 byte-identical; no widening, no new threshold.
4. **§5.5 RULINGS.** (1) The three caps exceeding the 3600-wall-s stall heuristic
   (arms 1/2/3: 5531/5883/7259 s) are legitimately long runs, NOT stalls — flagged in
   advance for the spend review. (2) The two `AR_1_Ret_180` arms are **IN M1-C**: the
   frozen grade_m1d.py counts them among the 78 (M1d's G0 named both AR_1 arms among
   the 6 incomplete), so excluding them leaves the grader permanently at 76/78 and a
   full-sweep G0 PASS unreachable; the `excluded_by_supervisor: true` flag is a
   COST-CONTENTION-calibration exclusion only (they ran solo, §4.4), not a
   sweep-membership exclusion, and M1's frozen prereg registers no AR_1 exclusion.
   All six arms stay; A.3's MAX caps govern (total 379.567 core-min, $0.3245 DERIVED).

**§2ba (CHARTER v1.72):** the run carries BOTH the detached queue daemon (pid 1887,
the solve) + the committed detached `autograde_m1c.sh` (the grader, no live agent)
AND the live `monitor_m1c.sh` — neither substitutes for the other.

**STILL NOT LAUNCHED at this commit; SUBMISSIONS PARKED.** The six queue rows'
`prereg_commit` is set to THIS freeze commit and `enqueued_by` attested by the
supervisor in a following commit; staging (`stage_m1c.sh --execute`) and the live
row-drop into `verification/queue/closure/` follow the freeze, PH_Breuer first.
Compute begins only when the daemon reads the live rows — after this prereg is
committed (rule 2 / §3 check-4).

---

# DATED AMENDMENT — 2026-09-09 — STAGING-PATH FIX (PRE-FIRST-COMPUTE; alters no gate/threshold/cap/label)

**Legality (rule 2).** M1-C has had **ZERO compute** (the first `stage_m1.py --execute`
crashed before any solver ran; no core-min spent). This amendment changes only the
**staging MECHANISM** and the **§6.2 prose** — it touches no gate, threshold, cap,
label, the grading path, or the A.3 caps. The freeze stamp above stands unchanged.

**What was wrong (found by executing the frozen `stage_m1.py`; §3 check-2 triage by
the supervisor from source — TOOLCHAIN, not physics; recorded as L-512 and a rule-6
disclosure note on `stage_m1.py`):**
* **L-512(A)** — `stage_m1.py`'s `--case` is DEAD (line 761 binds `wanted` and never
  uses it); it stages ALL enumerated cases per `--arm`. Latent because M1 staged the
  whole sweep. So `stage_m1c.sh`'s per-`--case` calls could not select the 6 arms.
* **L-512(B)** — `stage_m1.py:628 os.makedirs(dst, exist_ok=False)` crashes on a
  pre-existing dst; it conflicts with §6.2's pre-created empty scaffolding dirs.

**The fix — reuse the frozen `stage_m1.py` VERBATIM, scope by prune (NO transform
reimplementation, NO edit to the frozen `stage_m1.py`).** `stage_m1c.sh` is
SUPERSEDED by two scripts frozen at this amendment's commit, both §3-check-1'd by the
supervisor (SOUND):
* `cleanup_m1c.sh` — empties the disjoint M1-C tree, fail-closed (refuses unless the
  target is the literal `m1c_completion` path; every child realpath-checked strictly
  inside it and refused if it resolves into `*multimodel_sweep*`).
* `restage_m1c.sh` — cleanup → `stage_m1.py --arm kOmega` → `--arm kOmegaSST_null`
  (frozen transforms: `set_ras_model`, R16 planted zero, mesh copy, `0.orig`) →
  PRUNE to exactly the 6 target arms (within-ROOT-guarded) → VERIFY each. Transient
  over-stage ≈516 MB peak, ≈488 MB pruned — **disk churn only, ZERO solver core-min**
  (noted in the cost calibration).

**§6.2 CORRECTION.** §6.2 read that the six dst dirs "exist and are EMPTY" before
staging. That is STRUCK: a pre-created empty dir both trips L-512(B) AND is a state
`run_m1.sh` REFUSES (no `0.orig` to arm from). The corrected requirement: **the six
cwd dirs are CREATED BY STAGING, each holding `0.orig/` and NO time dir.** This
still satisfies the queue validator — a staged dir has `0.orig/` (letters → does NOT
match the validator's `^[0-9]+$` TIME_DIR age-guard, which a bare `0/` WOULD trip)
and its cwd exists (EXEC/launchable) — so it is strictly better, not a relaxation.

**VERIFY-SPEC CORRECTION.** The freeze checklist's stage-time check "0/U newest in
0/" was wrong: a freshly staged case has `0.orig/`, no `0/` — `run_m1.sh` arms
`0.orig`→`0` and touches `0/U` LAST at LAUNCH. The age-datum-newest check is a
post-run property and lives in the autograder's rule-4 gate
(`autograde_m1c.sh:arm_complete`, `20000/U -nt 0/U`), which is unchanged.
`restage_m1c.sh`'s stage-time verify instead checks: `0.orig/`+`0.orig/U` present,
NO `0/`, `RASModel` == the arm's model (kOmega→kOmega, kOmegaSST_null→kOmegaSST — the
same identity G1 checks), `polyMesh` present, no numeric time dir.

**Sequence after this amendment:** `restage_m1c.sh --execute` → drop the 6 rows live
(PH_Breuer first, re-validate `--require-binding`, commit) → launch the detached
autograder + live monitor → the daemon (pid 1887) solves. Grading path, A.3 caps,
§2ba plan, merged-symlink topology: all UNCHANGED.
