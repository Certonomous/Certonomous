# Numerics draft - Wu 2018 a-posteriori lane (Lane 2). Supervisor appends from here.

Moved out of the scratchpad 2026-08-21 after that path was cleared and
repopulated by another workstream for the third time. This file is the live copy.

**N-B22. Injecting an anisotropy made the duct solve converge ~60x faster in
iterations, and that is not evidence of accuracy.** Same solver, same mesh, same
start field, same stopping rule (all of U, p, k, omega initial residuals < 1e-6),
`AR_1_Ret_360` (3,025 cells):

| configuration | iterations to the same stopping rule | wall s |
|---|---|---|
| NULL (zero correction) | **> 30,000** (still running at cap check) | -- |
| TRUTH (`b_LES - b_RANS`) | **528** | 7 |
| MEAN (constant tensor) | 1,427 | 17 |
| ML seed 0 / 1 / 2 | **523 / 527 / 522** | 8 / 8 / 7 |

Mechanism, and the reason it is not a quality signal: a linear eddy-viscosity
model produces a secondary flow that is identically zero to machine precision
(`BASELINES.md` sec. 4), so in the NULL run OpenFOAM normalises the cross-plane
momentum residuals by a field of magnitude ~1e-16 and the normalised `Uy`/`Uz`
residuals sit at O(0.3) with nothing to converge *to*. Any non-zero `bijDelta`
gives the cross-plane equations a real source, a real scale, and therefore a
real residual that can fall below 1e-6.

**What cannot be concluded:** that the corrected model is better conditioned, more
accurate, or cheaper in general. TRUTH and ML converge in nearly the same number
of iterations (528 vs 523) while being very different fields, so iteration count
here measures *whether the residual normaliser is non-degenerate*, not solution
quality. Report iteration counts per configuration, and never let "converged
faster" stand in for "converged to something better" - the `U_rms` column is the
only one that answers that.

**N-B23. Quote both comparators for an a-posteriori row: the shipped baseline and
your own zero-correction run.** They are not the same number. The shipped duct
fields stopped on a `residualControl` listing only `k` and `omega`
(`k 5e-6; omega 1e-10;`), leaving streamwise momentum at an initial residual of
1.6e-3 (`AR_1_Ret_360`) and 9.3e-4 (`AR_3_Ret_360`) - one to three orders short of
the 1e-6 used for every configuration here. Scoring an injected run against the
shipped field silently credits (or debits) the model with the benchmark's own
convergence gap. Fix: run NULL under the identical solver, mesh copy and stopping
rule, use it as the comparator, and report `NULL - BASE` once as a named quantity.

**N-B24. Injecting an anisotropy correction with no k-correction collapses the
transported turbulent kinetic energy, and the velocity field gets worse even when
the anisotropy is exactly right.** Measured, `kOmegaSSTCorrected` with
`bijDelta = b_LES - b_RANS` and `kDeficit = 0`:

| Case | `k` mean, baseline SST | `k` mean, truth-injected | ratio to baseline | ratio to `k_LES` |
|---|---|---|---|---|
| `AR_1_Ret_360` (duct) | 26.68 | **8.74** | **0.33** | 0.20 |
| `CBFS13700` | 0.00302 | 0.00275 | 0.91 | 0.68 |

Mechanism: the model realises `tau = 2k(b_lin + b^Delta)` with `k` from the
current iterate, and the `k`-equation production is
`P_k = -2k(b_lin + b^Delta):grad(U)`. Injecting `b^Delta` changes production with
nothing to balance it, so `k` finds a new and much lower equilibrium; the
realised stress is then scaled by that factor no matter how good `b^Delta` is.
Consequence measured on all three cases: `b_rms` against the LES improves by a
factor of **23** (0.5833 -> 0.0251 on the duct) while `U_rms` **worsens by
57-63%**.

The control that isolates it: the same solver and the same injection path, given
**both** corrections (`b^Delta` and `R`), reaches `eps(U)/eps(U_0) = 0.0017` on
PH10595 (`verification/campaign/W2_SPARTA_FROZEN_CBFS.md`). The path is sound;
the `b`-only configuration is what fails - and `b`-only is all a model that
predicts `b_ij` alone can supply. **Any a-posteriori plan for a `b_ij`-only
closure must either carry a k-correction or freeze `k`, and must say which.**

**N-B25. The duct secondary flow is recovered from a structural zero, and that is
independent of the velocity getting worse.** Injecting `b^Delta` moves the duct
in-plane velocity from **0.0000%** of bulk (machine zero, as a linear
eddy-viscosity model requires) to **0.365%** with the true anisotropy and
**0.330-0.356%** with the learned one, against a DNS **1.508%** - about 24% of
the true magnitude, from nothing. Reported because it is the one thing in this
lane that worked exactly as the literature promises, and because it shows the
injection path is wired correctly: a bug would not produce a physically-shaped
secondary flow of the right sign and order.
