# CRM WING-ALONE L2R — GRADED. **`GATE FAIL`.** The relaunch completed; two registered gates were breached.

**Graded 2026-09-12T20:36Z by a cfd `lab-lane` under `CRM_WINGALONE_FLOW_PREREGISTRATION.md`,
prereg commit `122398334e1a8d7cbce0b449ccbb7f5242f3b2f8`, blob
`4fa6dbf43c845ffabab1c4cd75b2a41aa797405e` — verified identical at the freeze commit and at
HEAD. This record alters no gate, threshold, cap or label.**

🔴 **GRADING ROUTE: BY HAND.** No watcher was armed in `SOLVE_L2R` — the armed watchers live in
the dead `SOLVE_L2` tree and this lane copied `GRADER/` without arming them. Stated because it
was asked. The grader used is the **frozen** `GRADER/grade_crm_l2.py`, sha256
`e02a0771237b50593bb3d61040ca3f04d9887e4d6e8778ed15470fe96e327efb`, **recomputed on disk before
use** and identical to `GRADER/FROZEN.sha256`.

🔴 **AND A RULE-2 GAP THAT STANDS PERMANENTLY ON THIS RECORD:** `GRADER-FREEZE: ABSENT-AT-FREEZE`.
`git show 122398334:cases/CRM_wingalone/grade_crm_l2.py | sha256sum` returns
`e3b0c442…` — **the sha256 of the empty string**. The registration was frozen 03:23:42Z; the
grader was first committed 06:08:06Z (`0c8d9edd2`). **The instrument post-dates the freeze by
2 h 44 min.** The **gates** are frozen; the code reading them is not. Ruled by cfd-supervisor:
the run proceeds, the flag stands beside the verdict permanently, not in a footnote.

---

## 1. RULE 4 STRICT COMPLETION — MEASURED CLAUSE BY CLAUSE

| clause | value | |
|---|---|---|
| `rc = 0` | `0` | **PASS** |
| `End` line | 1 | **PASS** |
| last time == `endTime` | 4000 == 4000 | **PASS** |
| fields at 4000 (`T U alphat k nut omega p`) | all present | **PASS** |
| `ExecutionTime` count == `round(endTime/deltaT)` | 4000 == 4000 | **PASS** |
| **age guard** — every field newer than `0/T` | none older-or-equal | **PASS** |

**COMPLETE ON ALL SIX CLAUSES.**

## 2. VERDICT — **`GATE FAIL`**

| gate | result | measured |
|---|---|---|
| **G-S1** residual floor | **`GATE FAIL`** | `Uz` **2.714887e-04** and `p` **2.409666e-03** against a 1e-4 threshold. `Ux` 1.36e-05, `Uy` 6.11e-05, `e` 2.91e-05, `k` 9.98e-07, `omega` 7.95e-07 all inside. |
| **G-S2** force plateau, max\|ΔCd\| over the last 500 iterations ≤ 1.0 count | **`GATE FAIL`** | **peak-to-peak 24.2139 counts** (the gated measure, ruled ahead of firing per `DEPARTURES.md` D3). Printed beside it: max single-step 1.4759, end-to-end 8.5843. |
| **G-S3** realizability | **PASS** | 0 negative `k`, `omega`, `T` of 1,158,144 cells at time 4000 — **with the rule-3 plant fired first on each field** (−1.234e-03 at cell 579072, reader reported it every time). |
| **G-S4** | **PASS** | |

**OVERALL: `GATE FAIL` — a RESULT, not a `NOT A RESULT`.** The run completed and registered
gates were breached.

**§5 QoI — REPORTED, NOT GATED** (no wing-alone CRM reference exists on this box):
`Cd = 2.33850199e-02` (233.850 counts), `Cl = 0.349428`, `CmPitch = 1.154665` at iteration 4000.

## 3. G-S2's FAILURE IS **NOT** THE DRIVAER SIGNATURE — TESTED, AND THE ANSWER IS NO

DrivAer's arms fail their plateau limb on a **coherent limit cycle** (r(T) ≈ +0.95,
r(T/2) ≈ −0.9, r(2T) ≈ +0.97). **The same test was run on CRM's `Cd` over iterations 2000–4000
and it does NOT show that structure:**

| | CRM wing | DrivAer (for contrast) |
|---|---|---|
| first sign reversal | lag 25 | lag 8 |
| best periodic peak | T = 52 iters | T = 33 / 30 |
| **r(T)** | **+0.508** | +0.959 / +0.936 |
| **r(T/2)** | **−0.018** | −0.845 / −0.940 |
| **r(2T)** | **+0.051** | +0.970 / +0.965 |

**r(T/2) ≈ 0 and r(2T) ≈ 0: there is no recurrence.** This is weakly-correlated wander, not a
periodic oscillation. **Sanaa's item 12 ("coherent oscillation → physics voting unsteady") is
NOT invoked for CRM**, and the convenient parallel with DrivAer is **refused on measurement**.
Amplitude by 500-iteration block: 3.78e-04, 5.12e-04, 4.82e-04, 5.43e-04 — mildly **rising**.

## 4. y⁺ — SOLVED, NOT MESH-DERIVED, AND IT SITS IN THE BUFFER LAYER

From the run's own `yPlus` functionObject at iteration 4000, `wing` patch:
**min 3.11, max 44.37, mean 18.42.**

🔴 **A MEAN y⁺ OF 18.4 IS IN THE BUFFER LAYER (5 < y⁺ < 30)** — the one region where neither a
wall-function nor an integrate-to-wall assumption holds cleanly. **This is registered here as a
finding on the mesh, not as an excuse for G-S1/G-S2**, and it is a candidate first item for
triage before any re-run is contemplated.

## 5. RULE-12 COST — CONTENTION NAMED SEPARATELY

| | value |
|---|---|
| wall × ranks | 5352 s × 6 |
| **actual gross** | **535.20 core-min** |
| registered estimate | 720 core-min |
| **actual / predicted** | **0.743** |
| registered cap | 1500 core-min — **not crossed** (0.357 of cap) |
| `ExecutionTime`/`ClockTime` | 5328.7 / 5350.0 = **0.9960** |
| **contention** | **0.4 %** |
| contention-free equivalent | 532.9 core-min |
| rate | 1.3380 s/it vs the **15.532 s/it registered basis → 11.6× faster** |
| peak RSS | 465,720 kB = **0.44 GiB** against a 6.0 GiB registered footprint |
| derived $ | **$0.458 — DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER` §5) |

**ATTRIBUTION: MISPREDICTION, NOT CONTENTION** — `exe/clk` 0.996. The registered basis was the
contended old box's 15.532 s/it. **Same defect as the DrivAer rows, on a different campaign:
estimates carried over from the contended box are systematically high.** Waste: none to name.
**The memory footprint was over-registered by 13.6×** (0.44 GiB actual against 6.0 declared) —
conservative in the safe direction, and worth tightening so gate B's headroom test means
something.

## 6. WHAT THIS VERDICT DOES NOT CERTIFY

- **No grid-convergence claim.** One admissible mesh (L1 and L3 both `GATE FAIL` on the mesh
  gates). No observed order, no GCI — the grader computes neither.
- **No validation of `Cd`, `Cl` or `Cm`.** Nothing on this box to validate against; see
  `CRM_DPW_REFERENCE_AVAILABILITY_2026-09-12.md` — **`BLOCKED`**, shared with dafoam's D8G.
- M = 0.85, Re = 5×10⁶, α = 2.0° are registered **lab choices**, not anchors.

*Graded by a cfd `lab-lane`, 2026-09-12, by hand from the frozen instrument. No gate,
threshold, cap or label altered. Submissions parked. No agent's message is Sanaa's consent.*
