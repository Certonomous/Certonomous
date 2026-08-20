# k-omega SST baseline, quantified per case

**This file is generated.** `sst_baseline_metrics.py` computes the numbers,
`make_baselines_md.py` renders this document. Re-running either reproduces it.
Nothing here is fitted or trained.

Purpose: this is the **Charter 2c trivial baseline**. Every Phase 3 closure
reproduction in `cases/RANS_LES_closure_models/` must beat the relevant row of
these tables on the metric it claims to improve, or ship as a documented failure.

## 0. Provenance

| Item | Value |
|---|---|
| dataset | The Closure Challenge benchmark dataset |
| source URL | https://github.com/rmcconke/closure-challenge-benchmark.git |
| local clone (outside the repo) | `/home/ubuntu/closure-challenge-benchmark` |
| commit | `deb91557184af3cb95f5190494ec52d8f2c6a0d1` |
| sha256 of `git ls-files -s data` | `e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401` |
| tracked files under `data/` | 6153 |
| scorer package | https://github.com/rmcconke/closure-challenge.git at `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`, local clone `/home/ubuntu/closure-challenge-pkg` |
| challenge paper | McConkey, Buchanan, Smidt, Bodner, Dwight & Cinnella, *The Closure Challenge*, arXiv:2603.28884 |
| generated | 2026-08-20 |

No benchmark file is modified by anything in this directory; every script reads only.

## 1. Definitions

All quantities are computed **cell-by-cell on the case's own RANS mesh**, on which
the challenge has already interpolated the LES/DNS truth. `U`, `k`, `nut`, `omega`
are the shipped converged k-omega SST fields; `U_LES`, `k_LES`, `tauij_LES` are the
shipped truth.

| Symbol in tables | Definition |
|---|---|
| `U_rms` | `sqrt(mean(|U_RANS - U_LES|^2)) / mean(|U_LES|)` |
| `U_mae` | `mean(|U_RANS - U_LES|) / mean(|U_LES|)` (the challenge's own metric shape, but over all cells rather than the 1000 scored points) |
| `k_rms` | `sqrt(mean((k_RANS - k_LES)^2)) / mean(k_LES)` |
| `tau_rms` | `sqrt(mean(||tau_RANS - tau_LES||_F^2)) / (2 mean(k_LES))`, with `tau_RANS = (2/3) k I - 2 nu_t S` |
| `b_rms` | `sqrt(mean(||b_RANS - b_LES||_F^2))`, `b = tau/(2k) - I/3`; dimensionless, and `||b||_F <= sqrt(2/3) = 0.8165` for any realisable state |
| `b_med`, `b_p95` | median and 95th percentile of `||b_RANS - b_LES||_F` (robust companions to the RMS) |
| `x_sep`, `x_reatt` | abscissae where the streamwise velocity in the first cell row off the bottom wall changes sign, at the ends of the longest contiguous reversed-flow run |

Cells where either `k` falls below `1e-4 * mean(k)` are excluded from the
anisotropy statistics (`b = tau/2k` is meaningless there); the excluded count is
in the JSON as `n_cells_k_masked`. On the hills that is 7-63 cells of 15600; on
the NASA hump it is 4514 of 51626 (8.7%), all in the low-turbulence freestream.

### Two verification checks on the post-processing itself

1. **Reattachment.** On PH_Breuer the first-cell-row sign criterion gives
   `x_sep = 0.259`, `x_reatt = 7.643`. OpenFOAM's own bottom-wall
   `wallShearStress`, written by the solver into
   `postProcessing/bottomValues/10000/wallShearStress_bottomValues.raw`, changes
   sign at `x = 0.259` and `x = 7.6439`. Four-significant-figure agreement from
   an independent quantity.
2. **Velocity gradient.** The DUCT, PH_Breuer, CBFS and NASA cases ship no `gradU`,
   so `of_read.structured_gradient()` computes it by a curvilinear chain rule on
   the structured block. Against the `gradU` OpenFOAM itself wrote on three
   periodic-hill cases it agrees to **0.47-0.96% relative L2 in the interior**
   (median cellwise 0.10-0.13%), and 2.5-3.3% including the one-sided boundary
   rows. The hills use the shipped `tauij_B` and are unaffected.

## 2. The baseline in the challenge's own metric (8 test cases, 1000 points each)

Uncorrected SST velocity, nearest-neighbour interpolated to the official
evaluation points, scored by the challenge's own `closure_challenge.score()`.
This is the number a submitted method has to beat.

| Case | SST identity baseline (scaled MAE) |
|---|---|
| `alpha_15_13929_4048` | 0.1320 |
| `alpha_15_13929_2024` | 0.2049 |
| `alpha_05_4071_4048` | 0.0461 |
| `alpha_05_4071_2024` | 0.0719 |
| `AR_1_Ret_360` | 0.1288 |
| `AR_3_Ret_360` | 0.1243 |
| `AR_14_Ret_180` | 0.0590 |
| `NASA_2DWMH` | 0.0621 |
| **overall (mean of 8)** | **0.1036** |

For scale, on the live leaderboard read from the benchmark README at the commit
above: the best entry is 0.0595 (Reissmann, Fang & Sandberg) and this lab's own
round-5 entry is 0.0566. The uncorrected baseline is 0.1036. A method that does
not get below 0.1036 has not earned its complexity.

## 3. Separated 2-D flows: field errors and the separation bubble

`Lrel` is the relative error in bubble length, `(L_RANS - L_LES) / L_LES`.
Positive means SST predicts too long a recirculation.

| Case | split | Re | cells | U_rms | U_mae | k_rms | tau_rms | b_rms | b_med | b_p95 | x_sep RANS | x_sep LES | x_reatt RANS | x_reatt LES | Lrel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `CBFS13700` | train | 13700 | 21000 | 0.0516 | 0.0258 | 0.7125 | 0.5926 | 0.3051 | 0.2307 | 0.4740 | 0.741 | 0.915 | 5.891 | 4.241 | +0.55 |
| `PHLL10595` | train | 10595 | 15600 | 0.1565 | 0.1327 | 0.5723 | 0.4314 | 0.2772 | 0.1935 | 0.5547 | 0.259 | 0.190 | 7.643 | 4.566 | +0.69 |
| `alpha_05_10071_2024` | val | 5600 | 15600 | 0.1739 | 0.1368 | 0.5062 | 0.3890 | 0.2801 | 0.2010 | 0.4701 | 1.220 | 1.267 | 7.830 | 5.787 | +0.46 |
| `alpha_05_10071_3036` | train | 5600 | 15600 | 0.1079 | 0.0907 | 0.4324 | 0.3617 | 0.3021 | 0.1992 | 0.5372 | 1.206 | 1.332 | 9.440 | 6.136 | +0.71 |
| `alpha_05_10071_4048` | val | 5600 | 15600 | 0.0872 | 0.0759 | 0.3498 | 0.3252 | 0.2720 | 0.1908 | 0.5478 | 1.199 | 1.335 | 9.454 | 6.149 | +0.71 |
| `alpha_05_4071_2024` | TEST | 5600 | 15600 | 0.0831 | 0.0723 | 0.4485 | 0.4140 | 0.3202 | 0.2365 | 0.5766 | 1.329 | 1.423 | 3.783 | 3.191 | +0.39 |
| `alpha_05_4071_3036` | train | 5600 | 15600 | 0.0558 | 0.0492 | 0.3143 | 0.3694 | 0.3223 | 0.2325 | 0.6222 | 1.317 | 1.471 | 3.796 | 3.300 | +0.36 |
| `alpha_05_4071_4048` | TEST | 5600 | 15600 | 0.0562 | 0.0428 | 0.2437 | 0.3558 | 0.3498 | 0.2497 | 0.5858 | 1.301 | 1.420 | 3.799 | 3.256 | +0.36 |
| `alpha_05_7071_2024` | train | 5600 | 15600 | 0.1321 | 0.1033 | 0.5084 | 0.4076 | 0.2797 | 0.2051 | 0.4803 | 1.200 | 1.222 | 6.581 | 6.244 | +0.07 |
| `alpha_05_7071_3036` | train | 5600 | 15600 | 0.0674 | 0.0552 | 0.3936 | 0.3614 | 0.3858 | 0.2042 | 0.5681 | 1.183 | 1.272 | 6.611 | 6.277 | +0.08 |
| `alpha_05_7071_4048` | train | 5600 | 15600 | 0.0688 | 0.0583 | 0.3096 | 0.3210 | 0.2748 | 0.1947 | 0.5546 | 1.171 | 1.287 | 6.624 | 6.288 | +0.09 |
| `alpha_075` | train | 5600 | 15600 | 0.0922 | 0.0765 | 0.4610 | 0.3789 | 0.2884 | 0.1925 | 0.5648 | 1.442 | 1.440 | 7.180 | 5.462 | +0.43 |
| `alpha_10_12000_2024` | train | 5600 | 15600 | 0.2142 | 0.1853 | 0.5632 | 0.4232 | 0.2869 | 0.2101 | 0.4948 | 0.269 | -- | 7.596 | 5.002 | -- |
| `alpha_10_12000_3036` | train | 5600 | 15600 | 0.1780 | 0.1543 | 0.6178 | 0.4524 | 0.2973 | 0.1955 | 0.5367 | 0.254 | -- | 7.450 | 4.783 | -- |
| `alpha_10_12000_4048` | train | 5600 | 15600 | 0.1435 | 0.1257 | 0.5505 | 0.4158 | 0.2781 | 0.1914 | 0.5593 | 0.250 | 0.270 | 7.431 | 4.927 | +0.54 |
| `alpha_10_6000_2024` | train | 5600 | 15600 | 0.1604 | 0.1174 | 0.6672 | 0.4873 | 0.2883 | 0.2236 | 0.4873 | 0.271 | 0.275 | 5.134 | 4.344 | +0.19 |
| `alpha_10_6000_3036` | train | 5600 | 15600 | 0.0913 | 0.0641 | 0.6093 | 0.4642 | 0.2996 | 0.2325 | 0.5632 | 0.273 | 0.277 | 5.174 | 4.578 | +0.14 |
| `alpha_10_6000_4048` | train | 5600 | 15600 | 0.0686 | 0.0548 | 0.4973 | 0.4198 | 0.2924 | 0.2304 | 0.5583 | 0.276 | 0.289 | 5.190 | 4.487 | +0.17 |
| `alpha_10_9000_2024` | train | 5600 | 15600 | 0.2134 | 0.1799 | 0.5764 | 0.4292 | 0.2820 | 0.2024 | 0.4838 | 0.266 | 0.223 | 7.620 | 4.599 | +0.68 |
| `alpha_10_9000_3036` | train | 5600 | 15600 | 0.1556 | 0.1304 | 0.5858 | 0.4381 | 0.2965 | 0.1969 | 0.5448 | 0.261 | 0.156 | 7.672 | 4.663 | +0.64 |
| `alpha_10_9000_4048` | train | 5600 | 15600 | 0.1202 | 0.1016 | 0.5117 | 0.3981 | 0.2895 | 0.1836 | 0.5517 | 0.263 | 0.241 | 7.701 | 4.911 | +0.59 |
| `alpha_125` | train | 5600 | 15600 | 0.1853 | 0.1534 | 0.6383 | 0.4653 | 0.2869 | 0.1988 | 0.5463 | 0.352 | 0.324 | 8.075 | 4.351 | +0.92 |
| `alpha_15_10929_2024` | train | 5600 | 15600 | 0.2557 | 0.2085 | 0.7146 | 0.5074 | 0.3120 | 0.2287 | 0.4848 | 0.461 | 0.458 | 8.291 | 4.225 | +1.08 |
| `alpha_15_10929_3036` | train | 5600 | 15600 | 0.2051 | 0.1676 | 0.6756 | 0.4882 | 0.3121 | 0.2004 | 0.5510 | 0.449 | 0.445 | 8.350 | 4.234 | +1.09 |
| `alpha_15_10929_4048` | train | 5600 | 15600 | 0.1757 | 0.1411 | 0.6385 | 0.4686 | 0.2925 | 0.1915 | 0.5674 | 0.449 | 0.467 | 8.396 | 4.203 | +1.13 |
| `alpha_15_13929_2024` | TEST | 5600 | 15600 | 0.2455 | 0.2059 | 0.7081 | 0.5061 | 0.2989 | 0.2368 | 0.4937 | 0.455 | 0.437 | 7.756 | 4.542 | +0.78 |
| `alpha_15_13929_3036` | train | 5600 | 15600 | 0.2011 | 0.1687 | 0.6715 | 0.4903 | 0.2972 | 0.2093 | 0.5517 | 0.439 | 0.433 | 7.412 | 4.398 | +0.76 |
| `alpha_15_13929_4048` | TEST | 5600 | 15600 | 0.1548 | 0.1305 | 0.5892 | 0.4450 | 0.2885 | 0.2033 | 0.5791 | 0.432 | 0.419 | 7.300 | 4.594 | +0.64 |
| `alpha_15_7929_2024` | val | 5600 | 15600 | 0.2505 | 0.1957 | 0.7375 | 0.5172 | 0.2889 | 0.2159 | 0.4790 | 0.458 | 0.450 | 6.235 | 4.121 | +0.57 |
| `alpha_15_7929_3036` | train | 5600 | 15600 | 0.1775 | 0.1293 | 0.7081 | 0.5101 | 0.2900 | 0.2115 | 0.5558 | 0.453 | 0.494 | 6.275 | 4.237 | +0.56 |
| `alpha_15_7929_4048` | val | 5600 | 15600 | 0.1328 | 0.0916 | 0.6286 | 0.4669 | 0.3011 | 0.2095 | 0.5688 | 0.458 | 0.493 | 6.304 | 4.566 | +0.44 |
| `NASA_2DWMH` | TEST | 936k (chord) | 51626 | 0.1260 | 0.0620 | 0.9960 | 0.7663 | 0.3196 | 0.2653 | 0.5749 | 0.275 | 0.279 | 0.526 | 0.446 | +0.50 |

Headline numbers to carry forward:

* **Periodic hill, Re_H = 10595 (Breuer).** SST reattaches at `x/H = 7.64`; the LES
  reattaches at `x/H = 4.57`. Separation is nearly right (`0.26` vs `0.19`), so the
  whole error is in reattachment: the bubble is **69% too long**.
  For external corroboration, Breuer et al. report LES reattachment at `x/H ~ 4.7`;
  the value derived here from the shipped interpolated LES field is 4.57.
* **NASA wall-mounted hump.** With chord `c = 0.42 m` from the case's own `caseDef`,
  SST separates at `x/c = 0.654` against `x/c = 0.663` for the truth (essentially
  right, the separation point is geometrically fixed), and reattaches at
  `x/c = 1.253` against `x/c = 1.062`: the bubble is **50% too long**.
* **Curved backward-facing step, Re_H = 13700.** Bubble **55% too long**
  (`x_reatt` 5.89 vs 4.24), on a case whose bulk velocity field is the most
  accurate of the set (`U_rms` = 0.052). Velocity accuracy and bubble accuracy are
  not the same thing, which is exactly why the challenge's velocity-only metric
  cannot see a closure's structural error.
* **Across the 29 parametric hills** the bubble-length error ranges from
  **+7% to +113%** (n = 27 of 29 where both bubbles close inside the domain);
  it is always positive. Two cases (`alpha_10_12000_2024`, `alpha_10_12000_3036`)
  carry `--` for the truth's separation point: in the LES the near-wall row is
  already reversed at the first cell centre (x = 0.05, essentially on the crest),
  so the separation point falls upstream of the first resolvable location. Their
  LES reattachment (5.00 and 4.78) is resolved and is well upstream of the SST
  values (7.60 and 7.45).

## 4. Square and rectangular ducts: the secondary flow that a linear model cannot make

Prandtl's second kind of secondary motion is driven by the cross-plane anisotropy
gradients, specifically by `d^2(b_22 - b_33)/dy dz` and `(d^2/dy^2 - d^2/dz^2) b_23`.
A linear eddy-viscosity model gives `b_23 = -(nu_t/k) S_23` and `b_22 - b_33 =
-(nu_t/k)(S_22 - S_33)`, and in a fully developed duct the mean strain has no such
components, so the model produces **exactly zero** secondary flow. That is not an
accuracy problem, it is a structural one, and it is visible in the numbers below as
a ratio of order 1e-15, i.e. machine round-off in a converged solve.

| Case | split | AR | Re_tau | Re_b | cells | U_rms | k_rms | tau_rms | b_rms | in-plane |U| LES (% of bulk) | in-plane |U| RANS (% of bulk) | b_23 rms LES | b_23 rms RANS | (b22-b33) rms LES | (b22-b33) rms RANS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `AR_10_Ret_180` | train | 10 | 164 | 2580 | 22090 | 0.1157 | 0.5628 | 0.8222 | 0.5875 | 0.827 | 9.10e-16 | 0.0089 | 2.13e-17 | 0.1069 | 3.02e-17 |
| `AR_14_Ret_180` | TEST | 14 | 166 | 2665 | 31819 | 0.0930 | 0.5445 | 0.8027 | 0.5767 | 0.721 | 1.87e-15 | 0.0083 | 5.37e-17 | 0.1093 | 4.50e-17 |
| `AR_1_Ret_180` | train | 1 | 165 | 2500 | 2209 | 0.1716 | 0.6144 | 0.9877 | 0.6541 | 1.246 | 6.35e-16 | 0.0118 | 1.04e-17 | 0.0941 | 1.18e-17 |
| `AR_1_Ret_360` | TEST | 1 | 342 | 5693 | 3025 | 0.1985 | 0.6297 | 0.8320 | 0.5843 | 1.508 | 3.96e-16 | 0.0132 | 8.47e-18 | 0.1260 | 1.73e-17 |
| `AR_3_Ret_180` | train | 3 | 164 | 2581 | 6627 | 0.1727 | 0.6016 | 0.8595 | 0.6085 | 1.202 | 7.04e-16 | 0.0116 | 9.71e-18 | 0.1060 | 1.81e-17 |
| `AR_3_Ret_360` | TEST | 3 | 336 | 5817 | 8748 | 0.1846 | 0.5972 | 0.7383 | 0.5431 | 1.411 | 7.58e-16 | 0.0128 | 3.35e-17 | 0.1310 | 3.25e-17 |
| `AR_5_Ret_180` | train | 5 | 164 | 2592 | 11045 | 0.1513 | 0.5883 | 0.8412 | 0.5989 | 1.048 | 1.65e-15 | 0.0105 | 2.56e-17 | 0.1062 | 3.76e-17 |
| `AR_7_Ret_180` | val | 7 | 165 | 2605 | 15463 | 0.1332 | 0.5759 | 0.8285 | 0.5917 | 0.931 | 7.52e-16 | 0.0098 | 1.84e-17 | 0.1071 | 3.01e-17 |

The duct `b_rms` of 0.54-0.65 is close to the largest value the anisotropy tensor
can take at all (`||b||_F <= 0.8165`): on these flows the modelled anisotropy is
wrong in a way that is comparable in size to the anisotropy itself.

## 5. Realisability of the modelled anisotropy, and what the SST a1 limiter is doing

Realisability (Schumann 1977) requires the eigenvalues of `b` to lie in
`[-1/3, 2/3]`, equivalently the barycentric coordinates (Banerjee et al. 2007) to
be non-negative. For a linear eddy-viscosity model `b = -(nu_t/k) S`, so the
binding constraint is

        r = (nu_t / k) * lambda_max(S) <= 1/3.

Menter's SST caps `nu_t = a1 k / max(a1 omega, S F2)` with `a1 = 0.31`, which caps
`r` at `a1 = 0.31 < 1/3`. **The a1 limiter is, among other things, a realisability
constraint**, and the data show it acting as one.

`r_unlim` is the counterfactual `lambda_max(S)/omega` obtained by dropping the
limiter while **holding the converged k and omega fields fixed** -- what an
unlimited linear eddy viscosity `nu_t = C_mu k^2/eps = k/omega` would have
produced pointwise. It is a diagnostic on a frozen field, not a k-epsilon solve.

| Case | r p99 | r max | frac r > 1/3 | r_unlim p99 | r_unlim max | frac r_unlim > 1/3 | frac cells a1 limiter active | frac b_RANS non-realisable | frac TRUTH non-realisable |
|---|---|---|---|---|---|---|---|---|---|
| `AR_10_Ret_180` | 0.155 | 0.155 | 0.0000 | 0.162 | 0.16 | 0.0000 | 0.315 | 0.0000 | 0.0000 |
| `AR_14_Ret_180` | 0.155 | 0.155 | 0.0000 | 0.162 | 0.16 | 0.0000 | 0.326 | 0.0000 | 0.0000 |
| `AR_1_Ret_180` | 0.155 | 0.155 | 0.0000 | 0.162 | 0.16 | 0.0000 | 0.219 | 0.0000 | 0.0000 |
| `AR_1_Ret_360` | 0.155 | 0.155 | 0.0000 | 0.161 | 0.16 | 0.0000 | 0.177 | 0.0000 | 0.0159 |
| `AR_3_Ret_180` | 0.155 | 0.155 | 0.0000 | 0.162 | 0.16 | 0.0000 | 0.249 | 0.0000 | 0.0000 |
| `AR_3_Ret_360` | 0.155 | 0.155 | 0.0000 | 0.161 | 0.16 | 0.0000 | 0.192 | 0.0000 | 0.0042 |
| `AR_5_Ret_180` | 0.155 | 0.155 | 0.0000 | 0.162 | 0.16 | 0.0000 | 0.282 | 0.0000 | 0.0000 |
| `AR_7_Ret_180` | 0.155 | 0.155 | 0.0000 | 0.162 | 0.16 | 0.0000 | 0.300 | 0.0000 | 0.0000 |
| `CBFS13700` | 0.174 | 0.195 | 0.0000 | 0.215 | 0.47 | 0.0001 | 0.192 | 0.0000 | 0.0000 |
| `NASA_2DWMH` | 0.222 | 0.721 | 0.0026 | 59.740 | 261.70 | 0.1150 | 0.300 | 0.0026 | 0.0000 |
| `PHLL10595` | 0.169 | 0.193 | 0.0000 | 0.230 | 0.27 | 0.0000 | 0.217 | 0.0000 | 0.0000 |
| `alpha_05_10071_2024` | 0.165 | 0.195 | 0.0000 | 0.317 | 0.53 | 0.0085 | 0.183 | 0.0000 | 0.0234 |
| `alpha_05_10071_3036` | 0.162 | 0.192 | 0.0000 | 0.282 | 0.44 | 0.0041 | 0.216 | 0.0000 | 0.0155 |
| `alpha_05_10071_4048` | 0.159 | 0.190 | 0.0000 | 0.271 | 0.37 | 0.0026 | 0.237 | 0.0000 | 0.0139 |
| `alpha_05_4071_2024` | 0.180 | 0.189 | 0.0000 | 0.271 | 0.32 | 0.0000 | 0.200 | 0.0000 | 0.0246 |
| `alpha_05_4071_3036` | 0.175 | 0.190 | 0.0000 | 0.263 | 0.31 | 0.0000 | 0.220 | 0.0000 | 0.0143 |
| `alpha_05_4071_4048` | 0.171 | 0.189 | 0.0000 | 0.262 | 0.31 | 0.0000 | 0.213 | 0.0000 | 0.0141 |
| `alpha_05_7071_2024` | 0.168 | 0.190 | 0.0000 | 0.274 | 0.34 | 0.0012 | 0.187 | 0.0000 | 0.0239 |
| `alpha_05_7071_3036` | 0.163 | 0.188 | 0.0000 | 0.252 | 0.32 | 0.0000 | 0.220 | 0.0000 | 0.0148 |
| `alpha_05_7071_4048` | 0.160 | 0.188 | 0.0000 | 0.247 | 0.31 | 0.0000 | 0.227 | 0.0000 | 0.0144 |
| `alpha_075` | 0.165 | 0.191 | 0.0000 | 0.240 | 0.29 | 0.0000 | 0.230 | 0.0000 | 0.0148 |
| `alpha_10_12000_2024` | 0.172 | 0.201 | 0.0000 | 0.275 | 0.35 | 0.0010 | 0.196 | 0.0000 | 0.0236 |
| `alpha_10_12000_3036` | 0.167 | 0.198 | 0.0000 | 0.245 | 0.31 | 0.0000 | 0.230 | 0.0000 | 0.0139 |
| `alpha_10_12000_4048` | 0.163 | 0.197 | 0.0000 | 0.237 | 0.29 | 0.0000 | 0.245 | 0.0000 | 0.0135 |
| `alpha_10_6000_2024` | 0.180 | 0.195 | 0.0000 | 0.233 | 0.25 | 0.0000 | 0.214 | 0.0000 | 0.0230 |
| `alpha_10_6000_3036` | 0.172 | 0.192 | 0.0000 | 0.230 | 0.24 | 0.0000 | 0.246 | 0.0000 | 0.0132 |
| `alpha_10_6000_4048` | 0.169 | 0.189 | 0.0000 | 0.230 | 0.24 | 0.0000 | 0.244 | 0.0000 | 0.0134 |
| `alpha_10_9000_2024` | 0.174 | 0.198 | 0.0000 | 0.242 | 0.28 | 0.0000 | 0.204 | 0.0000 | 0.0224 |
| `alpha_10_9000_3036` | 0.166 | 0.194 | 0.0000 | 0.227 | 0.27 | 0.0000 | 0.233 | 0.0000 | 0.0139 |
| `alpha_10_9000_4048` | 0.164 | 0.190 | 0.0000 | 0.225 | 0.26 | 0.0000 | 0.246 | 0.0000 | 0.0131 |
| `alpha_125` | 0.168 | 0.194 | 0.0000 | 0.217 | 0.24 | 0.0000 | 0.236 | 0.0000 | 0.0139 |
| `alpha_15_10929_2024` | 0.175 | 0.198 | 0.0000 | 0.215 | 0.24 | 0.0000 | 0.211 | 0.0000 | 0.0221 |
| `alpha_15_10929_3036` | 0.170 | 0.193 | 0.0000 | 0.210 | 0.22 | 0.0000 | 0.240 | 0.0000 | 0.0135 |
| `alpha_15_10929_4048` | 0.167 | 0.188 | 0.0000 | 0.210 | 0.22 | 0.0000 | 0.253 | 0.0000 | 0.0128 |
| `alpha_15_13929_2024` | 0.175 | 0.201 | 0.0000 | 0.237 | 0.28 | 0.0000 | 0.201 | 0.0000 | 0.0230 |
| `alpha_15_13929_3036` | 0.170 | 0.200 | 0.0000 | 0.215 | 0.25 | 0.0000 | 0.233 | 0.0000 | 0.0139 |
| `alpha_15_13929_4048` | 0.168 | 0.197 | 0.0000 | 0.214 | 0.24 | 0.0000 | 0.250 | 0.0000 | 0.0128 |
| `alpha_15_7929_2024` | 0.178 | 0.194 | 0.0000 | 0.211 | 0.22 | 0.0000 | 0.217 | 0.0000 | 0.0224 |
| `alpha_15_7929_3036` | 0.171 | 0.188 | 0.0000 | 0.212 | 0.22 | 0.0000 | 0.248 | 0.0000 | 0.0127 |
| `alpha_15_7929_4048` | 0.168 | 0.183 | 0.0000 | 0.213 | 0.22 | 0.0000 | 0.250 | 0.0000 | 0.0122 |

Readings:

* The a1 limiter is active on **18-33% of cells** in every case in the set.
* With the limiter, SST's `b` is realisable in every cell of every hill, duct and
  step case here, and in 99.74% of the hump's cells. Without it, on the hump the
  ratio reaches **262** and **11.5% of cells** would be non-realisable: that is the
  stagnation-point anomaly, measured. The hump is the only case in the set with a
  genuine stagnation region, and it is the only case where the counterfactual blows
  up -- which is the expected pattern, not a coincidence.
* **1.2-2.5% of the interpolated LES/DNS truth cells on the hills are themselves
  non-realisable**, and up to 1.6% on the ducts. Any method trained to regress
  `b_LES` is being handed a small fraction of physically impossible labels. A
  reproduction that enforces realisability on its output cannot reach zero error
  against this truth, and one that reports a realisability violation rate should
  compare it against these numbers, not against zero.

## 6. DATA INVENTORY

### 6.1 Cases, sizes and splits

| Family | Cases | Re | Mesh | Cells/case | Fields shipped |
|---|---|---|---|---|---|
| `PHLL29` parametric periodic hills | 29 (`alpha_05/075/10/125/15`, x length 4.05-13.87, y height 2.02-4.04) | Re_H = 5600 (nu = 1.786e-4, H = 1, U_b = 1) | structured 120 x 130 | 15600 | `U k omega nut p phi C` + `gradU Pk Pk_bouss Pk_prop Dk k_conv k_diff tauij_B tauij_B_bouss walldist` + truth `U_LES k_LES tauij_LES epsilon` |
| `DUCT` square/rectangular ducts | 8 (AR 1,3,5,7,10,14; Re_tau 164-342) | Re_b 2500-5817, Re_tau 164-342 (from each case's own `caseDef`) | structured cross-plane, 47-55 cells per half-height | 2209-31819 | `U k omega nut p` + truth `U_LES k_LES tauij_LES`; **no gradU** |
| `PHLL10595` periodic hill (Breuer) | 1 | Re_H = 10595 (nu = 9.4384e-5) | structured 120 x 130 | 15600 | `U k omega nut p` + truth `U_LES k_LES p_LES tauij_LES`; **no gradU** |
| `CBFS13700` curved backward-facing step | 1 | Re_H = 13700 (nu = 7.2993e-5) | structured 140 x 150 | 21000 | `U k omega nut p` + truth `U_LES k_LES p_LES tauij_LES` (via `interpolatedFields/*_internalField` includes); **no gradU** |
| `NASA_2DWMH` wall-mounted hump | 1 | Re_c = 936000, c = 0.42 m, M = 0.1, U_inf = 34.6 m/s, nu = 1.5537e-5 | structured 622 x 83 | 51626 | `U k omega nut p` + truth `U_LES k_LES tauij_LES` + `bijDelta Dk walldist` (placeholders); **no gradU** |

Total cells with truth available: 29x15600 + 101026 (ducts) + 15600 + 21000 + 51626
= **641,652** across **40 cases**, of which the 21 suggested training hills alone
are 327,600 -- the
same figure this lab's own challenge entry reports for its training set
(`/home/ubuntu/Certonomous_closure_challenge/description/METHOD.md`, section 3).

### 6.2 The train / validation / test split

From the benchmark README at the pinned commit, and the figure `phll_tvt_split.png`
in the benchmark root. The **only strict rule** in the challenge is that no test
case may be trained or validated on.

| Flow | Training (suggested) | Validation (suggested) | Test (strict) |
|---|---|---|---|
| PHLL29 | the 21 remaining hills | `alpha_05_10071_4048`, `alpha_05_10071_2024`, `alpha_15_7929_4048`, `alpha_15_7929_2024` | `alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048`, `alpha_05_4071_2024` |
| DUCT | `AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`, `AR_10_Ret_180` | `AR_7_Ret_180` | `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180` |
| CBFS13700 | single case, training | -- | -- |
| PHLL10595 | single case, training | -- | -- |
| NASAHUMP | -- | -- | single case, test |

The split tests two generalisation axes the challenge names explicitly: **Reynolds
number** (`Ret_180 -> Ret_360` ducts; the hills' `alpha_15_13929` pair is the
longest domain) and **geometry** (`AR_14` is 1.4x the widest trained aspect ratio;
the hump is a different flow class altogether, with the only trained case of its
kind being the curved step).

Note for any Phase 3 preregistration: the 29 hills are *not* 29 independent flows.
They come in triples sharing `alpha` and domain length and differing only in domain
height (`2024/3036/4048`), so a random cell-level or case-level split will leak
near-duplicates between train and validation. Split by (`alpha`, length) group.

### 6.3 What is NOT in the data, and what this baseline cannot see

* `bijDelta`, `kDeficit` and `sigma` ship as `uniform 0` **placeholders** in every
  case, including the training cases. They are input slots for a corrected solve,
  not labels. Any anisotropy-discrepancy or k-deficit target has to be constructed
  from `tauij_LES`/`k_LES`, which is what `sst_baseline_metrics.py` does.
* `tauij_B` and `tauij_B_bouss` are **bitwise identical** in every hill case, as
  they must be for an uncorrected solve.
* The truth is the challenge's own interpolation of LES/DNS onto the RANS mesh.
  Near-wall rows and freestream cells carry interpolation error: 7-63 cells per
  hill and 4514 of 51626 hump cells have `k_LES` below the anisotropy floor, and a
  few hill cells have `k_LES < 0` outright (min -2.3e-4 on `alpha_15_13929_4048`).
* Every error here is an **a-priori, frozen-field** error. It says nothing about
  what happens when a modified closure is put back into the momentum equation and
  re-converged: a model that reduces `b_rms` by half may still diverge, or may
  produce a worse velocity field, because the mapping from `b` to `U` runs through
  the momentum balance and is not monotone. Any Phase 3 claim of an a-posteriori
  improvement must come from an actual solve.
* There is no uncertainty estimate on the LES/DNS truth in the release, so none of
  the errors above can be compared against a data uncertainty band.
* The 3-D cases named in the benchmark README (wing-body junction, Ahmed body,
  FAITH hill, and the 3-D duct meshes) are **not** in the local clone; they are on
  an external SURFdrive link. Nothing in this file covers them.

### 6.4 Charter-2c anisotropy baseline: the train-mean tensor

Sections 3-5 score the k-omega SST anisotropy error. **That is not a
demanding baseline.** The mean `b_LES` over the Phase-3 training cells, used
as a *constant* prediction everywhere with no inputs and nothing fitted
beyond an arithmetic mean, is:

```
b_mean =  [    0.1756   -0.0382    0.0018 ]
          [   -0.0382   -0.1479   -0.0006 ]
          [    0.0018   -0.0006   -0.0276 ]
```

mean over the **23 training cases / 341717 cells** of the Phase-3 split
(`Ling2016_TBNN/PREREGISTRATION.md` sec. 6): the benchmark's 8 strict TEST
cases and 5 suggested validation cases are held out, and so are the four
hills `alpha_05_10071_3036`, `alpha_05_4071_3036`, `alpha_15_13929_3036`, `alpha_15_7929_3036`, each of which
differs from a TEST or validation hill only in domain height and would
otherwise leak a near-duplicate into training. The constant is itself
realisable: yes.

| Case | cells | **train-mean (constant)** | k-omega SST | `b = 0` | constant beats SST? |
|---|---|---|---|---|---|
| `AR_14_Ret_180` | 31624 | **0.4036** | 0.5799 | 0.5842 | **yes** |
| `AR_1_Ret_360` | 2955 | **0.4221** | 0.5972 | 0.5996 | **yes** |
| `AR_3_Ret_360` | 8644 | **0.3866** | 0.5523 | 0.5580 | **yes** |
| `NASA_2DWMH` | 47102 | **0.2949** | 0.3318 | 0.3398 | **yes** |
| `alpha_05_4071_2024` | 15503 | **0.2586** | 0.3271 | 0.3457 | **yes** |
| `alpha_05_4071_4048` | 15543 | **0.3014** | 0.3512 | 0.3791 | **yes** |
| `alpha_15_13929_2024` | 15573 | **0.2714** | 0.3339 | 0.3355 | **yes** |
| `alpha_15_13929_4048` | 15576 | **0.2258** | 0.2889 | 0.3128 | **yes** |
| **pooled over all 8** | 152520 | **0.3183** | 0.4138 | 0.4234 | **yes** |

**The constant beats k-omega SST on 8 of 8 held-out cases.** Predicting one
fixed anisotropy tensor everywhere is a better a-priori anisotropy model than
the linear eddy-viscosity closure the benchmark ships. On the ducts the margin
is large (0.4036 against 0.5799 on `AR_14_Ret_180`), because SST's `b` there is
not merely inaccurate but structurally wrong -- section 4.

**THE RULE, for every anisotropy model in `cases/RANS_LES_closure_models/`:**

> A model that predicts `b_ij` must beat the **TRAIN-MEAN** row above, not the
> SST row. Beating SST on `b_rms` is a bar a constant clears, and reporting
> only that comparison is not an evaluation. Quote both columns, per case,
> on the same cell mask.

Cell mask: valid = k_LES above the anisotropy floor AND b_LES, b_RANS and the 17 extended features all finite; the last condition drops 567 cells that BASELINES.md sections 3-5 keep, so these SST numbers differ in the fourth decimal from those tables and are the ones a Phase-3 reproduction must quote

Generated by `trainmean_baseline.py` -> `trainmean_baseline.json`. Nothing is
fitted; re-running reproduces it.

## 7. How a Phase 3 reproduction should use this file

1. Quote the row for its case in its `PREREGISTRATION.md` as the trivial baseline,
   before training.
2. Report the same metric it beats. A method that improves `b_rms` and reports only
   `U_rms` (or the reverse) has not been evaluated; both are here.
3. Report the realisability violation fraction of its predicted `b` **next to the
   truth's own violation fraction** from section 5, not next to zero.
4. If it produces a velocity field by post-hoc correction rather than by re-solving,
   say so, and measure the continuity residual -- section 6.3, last-but-two bullet.
5. **If it predicts `b_ij`, beat section 6.4's TRAIN-MEAN constant, not the SST
   row.** The constant beats SST on all 8 held-out cases, so a method that beats
   only SST has demonstrated nothing. Report both columns on the same cell mask.

