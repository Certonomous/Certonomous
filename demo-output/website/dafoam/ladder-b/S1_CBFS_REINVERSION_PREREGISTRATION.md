# S1 — CBFS objective repair and re-inversion: pre-registration

**Written 2026-08-07 ~20:3x UTC, after the inlet repair was applied to a fresh copy of
the case and BEFORE any solver run of this item.** Item
`s1-cbfs-objective-repair-and-reinversion` (claimed 2026-08-07, blanket approval,
Stage 1 milestone). Parent record: `S1_CBFS_INVERSION_RESULT.md` (the diagnosis this
item acts on). **Hard budget cap: 450 core-min, everything in this item included.**
Run root: `/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/` (own `ledger.csv`;
nothing is billed to or read from the failed run's ledger).

At this writing the only numbers that exist are (a) the failed run's record and (b) the
inlet-file diff below, which is pure file arithmetic. **No primal has run on the
repaired case. The repaired baseline varianceU is unmeasured.**

## 1. The repair, applied and verified before this commit

A fresh case copy at `S1-cbfs-reinversion/cbfs_inv/` (0/, constant/, system/,
`runScript.py`, coloring cache — coloring depends on Jacobian sparsity, not BC values).
The corrupted case is left untouched as evidence. In the copy's `0/U`, the inlet
`fixedValue` list (150 faces) was replaced by the benchmark's own list, spliced as
exact text from `/home/ubuntu/closure-challenge-benchmark/data/CBFS/0/U`:

| quantity | corrupted case (patchV write-back) | benchmark / repaired |
|---|---|---|
| Ux | **0.72 uniform, all 150 faces** | profile 0.202035889 → 1.005375, mean **0.914922** |
| Uy | 0 uniform | −1.159e-3 → +1.902e-3, mean 3.124e-4 |
| Uz | noise column | **byte-identical in both files** (max abs diff 0.0) — the overwrite fingerprint |

Verified after the splice: all 150 repaired vectors equal the benchmark's exactly;
the remainder of `0/U` (internal field, all other patches) is byte-identical to the
corrupted case's file. `0/k`, `0/omega` inlet profiles already match the benchmark
(checked value-by-value at the head; the patchV pilot touched only U); `0/nut` inlet is
`calculated`; `0/UData` (the Bentaleb LES reference) untouched. The internal field
remains the corrupted run's converged state — it is only the initial guess; the primal
runs cold from `0/` to `primalMinResTol 1e-6` as always.

**Disclosed risk, stated now:** the repaired inlet raises the inflow bulk 27% above the
internal field it starts from; if the cold primal fails to reach 1e-6 within the
endTime-2500 cap, that failure IS the result and is recorded per charter §8.

## 2. Predictions, graded against the re-baseline (the falsifiable core of the repair)

- **P1 — the loss floor collapses.** varianceU at beta = 1 on the repaired case falls
  from `1.5279278906359758e-02` by **well over half**: predicted **< 7.6e-3**.
  **If varianceU is still ~1.4e-2 or above, the inlet diagnosis was wrong and that is
  the headline of this item — recorded as such, no softening.**
- **P2 — the loss geography inverts.** The y > 2 free-channel share of the total
  Σ|U−UData|² falls from **85.1%** to **below 50%** on the repaired baseline fields
  (same audit arithmetic as the failed run's coverage audit, host-side, on the written
  fields at the baseline's write time).
- Recorded but not gated: the physics-window (0≤x/h≤6, 0≤y/h≤2) share, 3.7% before,
  is expected to rise by several-fold; its measured value feeds the G2 amendment.

## 3. Protocol, in order, with per-stage budget

| stage | what | est core-min |
|---|---|---|
| A | re-baseline: fresh container, cold `run_model` at beta = 1, fields written; then `writeCellCentres` on the written time; P1/P2 graded | ~10 |
| B | FD anchor: fresh container, cold `compute_totals` at beta = 1 (the repaired-baseline gradient; doubles as the eval-1 control reference) | ~18 |
| C | FD re-verification, 3 components (§4) | ~30 |
| D | amendment fixing lambda_QoI, G1/G2 numbers (§5–6), committed BEFORE the driver launches | 0 |
| E | inversion, out-of-process driver, eval cap 22, budget guard 435 | ≤ ~370 |
| F | final-state cold control + field/centres write-out | ~15 reserved |
| | **hard cap** | **450** |

All runs: `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE=lu`, 4 ranks, **--cpus=2** (strict
queueing: `sudo docker ps` before every launch; QCR validation and acquisition arms
have priority), `sudo rm -rf processor*` cold reset, cold start from `0/`.

## 4. FD re-verification (re-anchoring the proven machinery on the new baseline)

W4 §5d's exact protocol: fresh container per point, cold reset, **central differences,
h = 0.05**, on **3 cells chosen from the stage-B gradient by the same rule as W4** —
the largest-|g| cell plus two more from the top of the |g| distribution in distinct
mesh neighborhoods (cell ids recorded in the result doc with their |g| ranks).
**Bar, fixed now: all three relative errors < 1%, zero sign flips** (W4 achieved
0.059–0.199% at h=0.05 on the corrupted objective; the machinery is proven — this
re-anchors it on the repaired objective). A miss on any component stops the item before
the inversion spends anything, and the miss is the result.

## 5. Objective for the re-inversion

```
J(beta) = lambda_QoI * varianceU(beta) + lambda_L2 * sum_j (beta_j - 1)^2
```

- `lambda_QoI = 1 / varianceU_baseline(repaired)` — set numerically in the §6
  amendment; Wu/Zhang's J≈1-at-beta=1 convention, re-based to the repaired case.
- **`lambda_L2 = 1.0e-5`, fixed now** — the bottom of Wu/Zhang's stated 1e-5–1e-4 band,
  a 10x cut from the failed run. Reasoning, disclosed: the failed run's plateau was an
  exact penalty balance (|g_pen|/|g_QoI| = 0.998, cos = 0.9995) at rms|beta−1| = 0.0165,
  with the achieved penalty 0.057% of post-optimization QoI error against their 10–20%
  convention — the pre-declared 1e-4 was too strong for the gradient scale and too weak
  for the fraction, simultaneously, because the QoI gradient was tiny under the
  defective loss. With the floor removed the QoI gradient carries real signal; 1e-5
  keeps the prior subordinate during descent and moves any balance plateau to 10x
  larger deviations. The achieved penalty fraction is **reported** against the 10–20%
  band, as a disclosure, not a gate; iterative trial-and-error tuning (their method)
  remains unaffordable in-cap and this one-shot re-tune is the honest substitute.
- **No TV/smoothness term this run, stated as a choice:** Wu/Zhang's prior is a plain
  per-cell L2 pull to 1 with no spatial term (W2 reading, Eq. (7) row); adding a
  Dow-style smoothness/TV term would deviate further from the reproduction target and
  introduce a new, untested gradient path mid-repair. If the recovered field again
  scatters cell-by-cell instead of forming coherent regions, a TV-regularized re-run is
  the named follow-up, filed as its own proposal.
- Optimizer, bounds, driver mechanics: **unchanged from Amendment 1 of the failed run**
  — host-side SciPy L-BFGS-B, maxcor 10, maxls 8, ftol 1e-10, gtol 1e-6, bounds
  [0.2, 4.0], fresh-container cold `compute_totals` per evaluation, per-eval ledger
  line + `beta_latest.npy`, numbered checkpoint every 10th eval, accepted-iterate
  snapshots via callback. Driver deltas from the failed run, every one disclosed in the
  result doc with a diff: `BASE` path, `LQOI` (re-based), `LL2` (1e-5), `EVAL_CAP` 22,
  `BUDGET_STOP` 435, and the eval-1 control reference now the stage-B gradient of THIS
  item (W4's archived gradient belongs to the corrupted objective and is no longer the
  right control).
- eval-1 control: varianceU must reproduce the stage-B value bit-identically and the
  gradient must match the stage-B `grad` file (max abs diff reported; 0.0 expected —
  same configuration, same protocol shape).

## 6. Gates — shape fixed now, numbers fixed by dated amendment before launch

Set **fresh from the repaired baseline**, never inherited from the failed run:

- **G1 — the inversion moves the data term:** normalized
  `J_qoi = lambda_QoI * varianceU` falls to **≤ 0.70** at the last accepted iterate
  within budget — same 30% bar as before **re-based to the repaired baseline** (the
  bar is sized to a ~21-new-evaluation budget, not to Wu/Zhang's 140-iteration runs).
  The amendment states lambda_QoI numerically; the bar itself is fixed now.
- **G2 — the correction lives where the physics says the model error lives:** among the
  top-decile |beta_final − 1| cells, **> 50%** inside **0 ≤ x/h ≤ 6, 0 ≤ y/h ≤ 2**.
  The amendment confirms the window against the stage-A loss-geography audit (if the
  repaired baseline's error concentrates elsewhere than the separated-flow window, the
  window is re-stated there WITH the audit numbers as justification, before launch).
- Reported, no gate: bound-pinned cell count; penalty fraction vs 10–20%; limiter-mask
  overlap on the final field (the 49.5%/7.7% measurement re-run — the Dow-style
  parameterization question stays live); evaluation count; core-min ledger.
- A stop at plateau, cap, or budget is recorded as what it is (charter §4).

## 7. Leakage position, restated

CBFS is the benchmark's field-inversion **training** case, not one of the 8 scored test
cases. The loss reads CBFS's own LES (`0/UData`) — training-legal by the challenge's
design; nothing scored is touched. If gates pass, `beta_final` becomes Stage 2's
training input: an in-sample correction field on a training case, usable for learning
beta(features), grading **no** benchmark score and supporting **no** generalization
claim by itself. Production-term-labeled throughout; nothing here is comparable to
Wu/Zhang's destruction-term numbers (C2, R6).

*Nothing below this line existed when this file was committed. Stage A launches only
after this commit lands.*
