# W2 SpaRTA step-1 pre-registration: k-corrective-frozen-RANS on CBFS13700, then PH10595

**Written 2026-08-01 (UTC), before any solver was launched on this rung.** Nothing below is
edited after the fact. If the result misses, the bands stay as written and the record says so.
Docket item: `w2-sparta-frozen-rans-cbfs` (approved, 60 core-min). Paper:
Schmelzer, Dwight & Cinnella, *Flow Turb. Combust.* 104:579-603 (2020), read in full, held at
`docs/papers/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf`.

## What is being reproduced

Table 1 of the paper, CBFS13700 row (primary) and PH10595 row (secondary): the mean-squared
error of the velocity and Reynolds-stress fields reconstructed by adding the extracted
corrections `b_ij^Delta` and `R` as static fields to a k-omega SST solver, normalised by the
baseline k-omega SST error against the same LES data:

| Case | eps(Ui)/eps(Ui_0), published | eps(tauij)/eps(tauij_0), published |
| --- | --- | --- |
| CBFS13700 | 0.22703 | 0.4949 |
| PH10595 | 0.00165 | 0.1495 |

The extraction (frozen omega solve, Eqs. 4-6 of the paper) and the propagation (static-field
corrections in the augmented SST, Eqs. 3-6) are both implemented in OpenFOAM v2606 on the
benchmark clone's own case setups (`data/CBFS`, 21,000 cells = the paper's 140x150;
`data/PH_Breuer`, 15,600 cells = the paper's 120x130), with the shipped `0/U_LES`, `0/k_LES`,
`0/tauij_LES` as the high-fidelity fields — same mesh, no interpolation.

## Comparison convention, declared now

The paper states neither its cell-weighting nor its tensor-component counting. Both variants
will be computed; the **primary** convention is fixed here before running:

- Fields compared at cell centres over the **entire internal field** (21,000 / 15,600 cells).
- **Primary:** unweighted cell average. `eps(U) = (1/N) sum_c |U_c - U_LES,c|^2` over all
  three components. `eps(tau) = (1/N) sum_c ||tau_c - tau_LES,c||_F^2`, Frobenius norm,
  off-diagonal components counted twice.
- **Secondary (reported, not graded):** cell-volume-weighted average, and the 6-unique-
  component tensor mean.
- The denominator uses the benchmark's own shipped baseline solution (`data/CBFS/30000`,
  `data/PH_Breuer/10000`), which ladder-B rung B2 reproduced on this box's v2606 install to
  0.068% scaled MAE. Baseline `tau_0 = (2/3)k I - 2 nu_t S` from those fields.
- Reconstructed `tau = (2/3)k I - 2 nu_t S + 2k b^Delta` from the propagated solution.
- Absolute eps values are reported alongside but only the ratios are graded, because the
  paper's absolute values depend on its (unstated) non-dimensionalisation.

## Tolerance, declared now

- **Binding gate (as approved on the docket):** CBFS `eps(U)/eps(U_0)` within a **factor of
  two** of 0.22703, i.e. in [0.1135, 0.4541], and below 1.0 as a hard floor. The tau ratio is
  reported against 0.4949 but not gated by the docket.
- **Tightened self-imposed bands, declared here before running** (this is what "hit" means in
  the report):
  - CBFS: HIT if `eps(U)/eps(U_0)` in **0.22703 +/- 25%** ([0.1703, 0.2838]) AND
    `eps(tau)/eps(tau_0)` in **0.4949 +/- 25%** ([0.3712, 0.6186]), primary convention.
  - PH: HIT if `eps(U)/eps(U_0)` **< 0.005** (paper claims 0.00165, a 600x error reduction;
    a ratio this small sits near the method's own convergence floor, so the band is one-sided:
    at least a 200x reduction) AND `eps(tau)/eps(tau_0)` in **0.1495 +/- 25%**
    ([0.1121, 0.1869]).
  - NEAR MISS: inside the docket factor-two band but outside the +/- 25% bands.
  - MISS: outside the docket band, or U ratio >= 1.0 anywhere.
- Why +/- 25%: different OpenFOAM lineage (theirs was a 2019-era fork, ours v2606), an
  unstated norm convention (both variants computed, primary fixed above), and an unstated
  propagation convergence level in the paper. Declared once, not revisited.

## Deviations from the paper, known in advance

1. Menter limiter placement in the omega equation: the paper's Eq. 5 applies
   `(gamma/nu_t)(P_k + R)` with `P_k` already limited by Eq. 6. Our propagation model keeps
   OpenFOAM v2606's stock omega-production limiter for the baseline part and adds
   `gamma (G_extra + R)/max(nu_t, 1e-12)` as an explicit source, so that the model reduces
   *exactly* to the stock kOmegaSST at zero corrections — the property the baseline
   normalisation depends on. The frozen solve itself uses the paper's Eq. 5 form directly.
2. The frozen solve's k-equation residual is defined against OpenFOAM's discrete steady k
   equation (including its (2/3) divU correction term), not the continuous Eq. 4, so that the
   extracted R exactly compensates the same discrete operators it is propagated through.
3. Discretisation follows the benchmark case's own `fvSchemes` (linear upwind divergence,
   2nd-order central diffusion), which is what the paper states it used.

## Convergence criteria, declared now (iteration honesty)

- **Frozen solve:** settle, not cap. Converged when the omega-equation initial residual
  < 1e-8 AND the max relative iteration change of omega < 1e-9, sustained 50 consecutive
  iterations; then 20% more iterations are run and the L2 norm of R must move < 0.01% over
  them, else "not settled" is reported. Backstop cap 5,000 iterations; hitting the cap is
  reported as NOT CONVERGED. The paper claims "a few hundred iterations"; ours is measured
  and reported next to that claim.
- **Propagation:** restarted from the shipped baseline; checkpoints every 5,000 iterations
  (CBFS) / 2,500 (PH). Settled when the graded ratio moves < 0.5% (relative) between two
  consecutive checkpoints, confirmed by one further checkpoint. Cap: 30,000 (CBFS) / 10,000
  (PH) iterations beyond restart; a cap-stop without settle is reported as such and not
  graded as a hit (this week's lesson: a cap-stopped rung read 1.05% high).

## Sign-convention experiments (LESSONS L-26), declared now

Signs are verified by controlled experiment, not by reading code:

- **E1, R in the k equation:** after the frozen solve, the k equation (with extracted R, frozen
  omega/nu_t/b) is re-solved starting from 0.5 x k_LES. Prediction: with the correct sign it
  returns to k_LES with relative L2 drift < 1%; with R scaled by -1 the drift is at least 10x
  larger. Both runs are performed and both numbers reported.
- **E2, R and b^Delta in the propagation:** two 500-iteration propagation runs with
  `RScale = -1` and `bScale = -1` respectively must show eps(U) *rising* relative to the
  correct-sign run at the same iteration count. Performed before the full propagation is
  graded.

## In-sample position

CBFS13700 and PH10595 are benchmark *training* cases; none of the eight scored test cases is
opened at any point. `sdk/scripts/closure_in_sample_gate.py` returned PASS immediately before
this work (run 2026-08-01) and will be re-run after; both outputs are quoted in the record.

## Budget

60 core-min approved. Measured basis (B2): full CBFS primal 29.5 core-min at 30,000
iterations. Plan: frozen solves ~2 min, sign experiments ~2 min, CBFS propagation <= 30 min,
PH propagation <= 15 min. PH is attempted only if CBFS lands inside the docket band.
