# Numerics drafts — Xiao2016_EnKF lane

For `docs/NUMERICS_KNOWLEDGE.md`. Measured on this machine; nothing recalled.

## N-X1. The structured-gradient divergence estimator floors at ~1e-2 on curved benchmark meshes — calibrate before registering a continuity tolerance

`of_read.structured_gradient` is exact to round-off where there is no streamwise
derivative to discretise, and three decades short where the mesh is curved.
Measured on fields whose divergence is already known to be zero:

| mesh | field | RMS `div(U)` / gradient scale |
|---|---|---|
| `AR_1_Ret_360` duct (cross-plane) | shipped converged SST | **4.5e-18** |
| `AR_3_Ret_360` duct | shipped converged SST | **1.2e-17** |
| `CBFS13700` curved step | shipped converged SST | **5.2e-03** |
| `CBFS13700` | interpolated LES truth | **4.3e-03** |
| **`PH_Breuer` periodic hill** | **shipped converged SST** | **9.45e-03** |
| **`PH_Breuer`** | **interpolated LES truth** | **5.90e-03** |
| `alpha_10_9000_3036` hill, forward model reproducing the SST stress | — | 7.60e-03 |

Both reference fields on every curved mesh sit at the same order, which is the
signature of an estimator floor rather than a field property. **An absolute
continuity threshold below ~1e-2 is unmeasurable on these meshes.**

Registered generalisation, accepted for this lab's closure lanes: use
**OpenFOAM's own `time step continuity errors : sum local`** from the solver log
as the primary continuity measure — it is flux-consistent and exact to round-off
for a converged SIMPLE solve — and report the structured-gradient value as a
**ratio to the shipped baseline's own value on that mesh**, with a healthy band of
`[0.5, 2.0]`, rather than against any absolute number.

## N-X2. Prescribing the true Reynolds stress explicitly diverges on a separated hill at benchmark Reynolds numbers, and the clip fraction is the diagnostic

Forward model: `tau_model = (2/3)k I − 2 nu_t S + 2k b^Delta` with
`b^Delta = b_target + (nu_t/k)S`, so `tau_model = tau_target` exactly at
convergence while the linear part stays implicit. Outer deferred-correction loop
on `S`. Identity-verified: prescribing the baseline SST stress returns the
baseline `U_rms` to **1e-4** at both Reynolds numbers tested.

Prescribing the **LES truth** stress:

| `Re_H` | implicit viscosity | `U_rms` (baseline for that case) | outer loop | `nu_t^L` clipped |
|---|---|---|---|---|
| 10595 | frozen baseline SST `nu_t` | 0.29799 (0.1565) | oscillating | n/a |
| 10595 | optimal `nu_t^L` clipped ≥ 0 | **3.8815** | **diverging** | **47.0 %** |
| 5600 | frozen baseline SST `nu_t` | 0.31210 (0.1556) | slowly decaying, 9 % at outer 6 | n/a |
| 5600 | optimal `nu_t^L` clipped ≥ 0 | 0.47467 | oscillating | **23.9 %** |

`nu_t^L = −⟨tau_dev : S⟩/(2⟨S : S⟩)` is Wu, Sun, Xiao & Wang's conditioning fix,
and **applying it made the `Re` = 10595 case thirteen times worse**. The number
that explains it is the clip count, not the error: nearly half the domain wants a
**negative** eddy viscosity against the true stress, clipping at zero is forced
for stability, and it removes the implicit stabilisation precisely in the shear
layer that sets the solution.

Halving the Reynolds number halves the clip fraction (47.0 % → 23.9 %) and
improves the optimal-projection error 8.2x, but leaves the best configuration
**8.7x above its acceptance gate** — no better relative to the gate than at twice
the `Re`. Xiao et al. (2016) ran this propagation at `Re_b` = 2800 on **1,500
cells**; these attempts were 15,600 cells at 3.78x and 2.0x that `Re`.

**By contrast, the same case propagates correctly when the correction carries `R`
as well as `b^Delta`:** `U_rms` = **0.009319** on PH10595 against a 0.1565
baseline (94.0 % reduction), independently reproducing the W2 SpaRTA record's
`eps(U)/eps(U_0)` = 0.003331 to 3 %. The explicit-stress route and the
`b^Delta`+`R` route differ by two orders of magnitude on identical data.

## N-X3. Cost of a prescribed-stress forward evaluation on a 15,600-cell hill

Single core, outer deferred-correction to `max|dU|/|U| < 1e-5`: **4 outer
iterations, 1,624 SIMPLE iterations, 99.7 s = 0.0277 core-hours** when it
converges; **6 outer x 2,000 = 967.6 s = 0.269 core-hours** at the registered caps
when it does not. A 60-member, 10-iteration ensemble is therefore **16.6 to 161.3
core-hours** — a band, not a number, because it is bounded by caps rather than by
a convergence guarantee, and the honest costing says so.
