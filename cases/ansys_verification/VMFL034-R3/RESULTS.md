# VMFL034-R3 — Particle Aggregation (QMOM moments on a frozen flow) — RESULTS

**Case.** VM2026R1 §.34 (p. 121–122): particle aggregation inside a turbulent
stirred tank, modelled as a QMOM population balance in a CMSMPR crystallizer.
Reference: B. Wan, T.A. Ring, K. Dhanasekharan, J. Sanyal, *"Comparison of
Analytical Solutions for CMSMPR Crystallizer with QMOM Population Balance
Modeling in Ansys Fluent"*, China Particuology **3**:213–218 (2005). The gate
reference is the **analytical** Target column of Table .34.1; the Ansys Fluent
QMOM column is context, not the gate. The manual's own modelling note — *"Moments
are solved on a frozen flow field"* — is the physical basis for R3's re-scope.

| moment | analytical target | band | role |
|---|---|---|---|
| m0 | 0.132 | ±0.76 % | CALIBRATION (demoted — setting β₀ for Da=100 *sets* m0) |
| m1 | 0.225 | ±0.76 % | gated |
| m2 | 0.547 | ±0.76 % | gated |
| m3 | 1.910 | ±0.76 % | gated |
| m4 | 9.073 | ±0.76 % | gated |
| m5 | 53.797 | ±0.76 % | gated |

**Verdict: `NOT A RESULT`** (register row #66). The frozen comparator
REFUSED (exit 2) at the CMSMPR **well-mixedness premise**, upstream of the moment
band. **No moment (m0–m5) was graded** — do not read any moment as a measured
result. This is a modeling-premise failure, not a grid artifact and not a solver
crash; the tier is not earned, and the successor VMFL034-R4 is OWED.

## The frozen-flow two-stage design (R3 re-scope)

R3 re-scopes VMFL034 to the manual's frozen-flow modelling note. **Stage 1:** a
single-phase steady k-ε carrier flow (`U φ k ε`) on the 2-D box mesh. **Stage 2:**
the QMOM moments transported on that frozen field by the frozen-flow solver
`reactingTwoPhaseEulerFoamFrozen` (frozen at `e0e3eddf`). Rescaled operating point
(§RESCALE): τ = 5 s, `endTime = 25 s = 5τ`, Da = β₀·m0_feed·τ = 100 preserved
exactly, α₂ = 1e-2, κ = π/6. A three-level size-group refinement triple S1/S2/S3
(the same Stage-1 flow mapped to all three levels; only the sizeGroups refine).
The gate conjunction is m1,m2,m3,m4,m5 with **m0 demoted to a calibration limb**.

## Why the verdict is `NOT A RESULT` — the CMSMPR premise fails, upstream of the band

The comparator MEASURES well-mixedness on the internal field and refuses if the
CMSMPR premise is not met (`CoV(m0) ≤ 0.10` and `|outlet − vol-mean|/vol-mean ≤
0.05`). All three stages fail both limbs, and the non-uniformity **increases with
refinement**:

| stage | cell-to-cell CoV(m0) | limit | \|outlet − vol-mean\|/vol-mean | limit |
|---|---|---|---|---|
| S1 (coarse) | 8.734 | 0.10 | 0.610 | 0.05 |
| S2 (medium) | 8.786 | 0.10 | 0.620 | 0.05 |
| S3 (fine) | 8.816 | 0.10 | 0.627 | 0.05 |

Both quantities RISE from S1→S2→S3, so the field is not a well-mixed CMSMPR and
refinement does not fix it: this is a **modeling-premise failure**, not a
discretisation artifact. The frozen comparator therefore refuses (exit 2) at the
premise, **before** the moment band, the Roache triple, the physical-range guard,
or any moment being computed. Verbatim:

> `WELL-MIXEDNESS REFUSAL (CMSMPR premise fails; exit 2):`
> `  well-mixedness FAIL: CoV(m0)=8.734 > 0.100`
> `  well-mixedness FAIL: |outlet-mean - vol-mean|/vol-mean = 0.610 > 0.050`
> `  -> NOT A RESULT; the successor changes the RESCALE, not the gate/target`

## Strict completion (rule 4) — all three stages COMPLETE

Each of S1/S2/S3: `RUN_RC = 0`, exactly one `End` line in
`log.reactingTwoPhaseEulerFoamFrozen`, last `Time = 25 == endTime` (5τ), fields
present at `25`, age guard met. The comparator's own `strict_completion` (with the
age guard) passed on all three stages — it reached the well-mixedness premise,
which sits downstream of completion. The run itself is complete and valid; the
`NOT A RESULT` is the measured premise refusal, not an incomplete run.

## Controls (CLAUDE.md rule 3) — FIRED

The comparator's per-case flow runs the guards and the planted control BEFORE the
well-mixedness premise (source lines 397–411):

- **Rule-3 planted-zero control** (a PLANT of 3.21e-04 added to a PROPER SUBSET of
  bins [8,9] of the moment reduction) ran on the real bytes and **PASSED** at line
  404 — the reader is shown able to see the plant — before the premise refusal at
  line 409–411.
- **D3 feed-moment guard** (sum of feed `value_i` = 1; frozen Wheeler nodes) and
  the **L-487 non-degenerate-plant guard** (`_assert_plant_nondegenerate` — refuses
  a plant spanning the whole reduction) both passed upstream.
- **Selftest 16/16** under the frozen comparator, including the planted control,
  the well-mixedness reader (`[PASS] uniform CoV within limit, gradient CoV over
  limit`) and the physical-range guard.
- The **physical-range guard and the moment band/Roache triple were NOT reached** —
  they sit downstream of the premise refusal.

## Freeze / verification chain (CLAUDE.md rule 2, §3 check 4)

- **Freeze commit `e0e3eddff79440997f293935c30922bf69bec051`** ("VMFL034-R3 FREEZE:
  frozen-flow re-scope"), which introduced the prereg, the comparator and the
  frozen-flow solver source.
- **Comparator** `cases/ansys_verification/VMFL034-R3/analyse_vmfl034_r3.py`, blob
  **`5fc867d964250b27639362e20f43b0af69c4840c`** — `git hash-object` on disk == blob
  at the freeze `e0e3eddf` == blob at HEAD. (The comparator is named
  `analyse_vmfl034_r3.py`; it has no `--verify-frozen` flag — the freeze is verified
  by hashing against the committed blob, and the launcher recorded
  `grading-path pins OK` against `FREEZE_COMMIT=e0e3eddf`.)
- **Pre-registration** `cases/ansys_verification/VMFL034-R3/PREREGISTRATION.md` and
  the frozen-flow solver `reactingTwoPhaseEulerFoamFrozen` frozen at the same
  commit. The grade was reproduced independently here (triple and per-stage
  `--case`), yielding the same exit-2 premise refusal and the same numbers.

## Cost (CLAUDE.md rule 12)

Measured core-minutes (serial, ranks = 1), from `launcher.queue.out` (cumulative
`core_min_used` differenced per stage):

| stage | core-min | ≈ wall s | Stage-2 cap | use |
|---|---|---|---|---|
| S1 | 63.55 | ~3 813 | 200 | 32 % |
| S2 | 176.55 | ~10 593 | 750 | 24 % |
| S3 | 603.87 | ~36 232 | 3000 | 20 % |
| **total** | **843.966** | — | running total 3960 | 21 % |

- **$ derived, not measured:** 843.966 core-min = 14.066 core-h × $0.0513/core-h =
  **$0.72 DERIVED** (owner-stated rate; the box cannot read its own billing,
  `COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate vs actual:** point estimate ≈ **1980 core-min (≈ 33 core-h)** →
  ratio **0.43×** (843.966 / 1980). **Over-estimate confirmed:** QMOM moment
  transport scales linearly in the number of size-group bins (N), not
  quadratically (N²), so each level came in ~2.3× cheaper than the N²-basis
  estimate. Attribution is misprediction (conservative direction), NOT contention
  (serial, single-tenant) and NOT waste.
- **No cap fired** (Stage-1 carrier 60; per-level 200/750/3000; running total 3960);
  **waste 0.000 core-min**. The three Stage-2 walls (~3.8k / 10.6k / 36.2k s)
  EXCEED the §2 3600-s stall heuristic, but each is a COMPLETE serial solve
  (`rc=0`, `End`, last `Time == endTime`), NOT a stall — reported gross == cleaned,
  disclosed not cleaned out.

## Provenance and the owed successor

- **Run root:** `verification/runs/ansys_verification/VMFL034-R3/` (S1/S2/S3, each
  `RUN_RC`, `log.reactingTwoPhaseEulerFoamFrozen`, `log.blockMesh`, `log.topoSet`,
  time dirs 0…25, `postProcessing`, `stage1`). Launcher `launcher.queue.out`
  (`core_min_used = 843.966`, `grading-path pins OK`, `FREEZE_COMMIT=e0e3eddf`).
- **VMFL034-R4 is OWED** (state (b), a numerics/config lever, not a capability
  gap): fix the flow-mixing setup ANSWER-BLIND so the CMSMPR well-mixedness premise
  is met (the successor changes the RESCALE / carrier-flow mixing, NOT the
  gate/band/target). The gate conjunction m1–m5, the ±0.76 % band, the analytical
  Wan targets and the size-group triple stand byte-identical (L-487).
- **Calibration:** `docs/COST_CALIBRATION.md` row `C-20260908T205401.737889Z-9e0402c9`.
