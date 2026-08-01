# W2 SpaRTA step 1 — k-corrective-frozen-RANS on CBFS13700 and PH10595

Date run: 2026-08-01 (UTC). Docket item: `w2-sparta-frozen-rans-cbfs` (approved, 60
core-min; 27.7 measured, section 8). Pre-registration: `W2_SPARTA_PREREGISTRATION.md`,
committed before any solve. Machine: the lab's 16-vCPU box, all solves serial, shared with
an IDWarp build agent (load ~2.5-3 during the propagations).

**Paper.** Schmelzer, Dwight & Cinnella, "Discovery of Algebraic Reynolds-Stress Models
Using Sparse Symbolic Regression," *Flow Turb. Combust.* 104:579-603 (2020), version of
record, READ IN FULL (see `W2_TBNN_SPARTA_READING.md` section 2). Reproduction target:
**Table 1**, the published mean-squared reconstruction errors with `b_ij^Delta` and `R`
added as static fields, normalised by the baseline k-omega SST error.

## RESULT

| Row | Published | Ours (primary, pre-registered) | Ours (secondary, volume-weighted) | Grade |
| --- | --- | --- | --- | --- |
| CBFS `eps(U)/eps(U_0)` | 0.22703 | **0.39753** | 0.27634 | **binding docket gate (factor 2, floor 1.0): PASS. Tightened +/-25% band: NEAR MISS** (75% above published, primary; 22% above, volume-weighted) |
| CBFS `eps(tau)/eps(tau_0)` | 0.4949 | **0.02617** | 0.02270 | outside the +/-25% band — **19x better than published** under the pre-registered Eq. 2-3 convention; see section 6, the convention finding |
| PH `eps(U)/eps(U_0)` | 0.00165 | **0.003331** | 0.001253 | **HIT** of the pre-registered one-sided band (< 0.005, i.e. >= 200x error reduction; measured 300x primary, 800x volume-weighted) |
| PH `eps(tau)/eps(tau_0)` | 0.1495 | **0.000337** | 0.000317 | outside the +/-25% band — **440x better than published** under the pre-registered convention; see section 6 |

**One-line verdict: the velocity reconstruction reproduces Table 1 within the approved
gate on CBFS (near miss of the tighter self-imposed band) and hits the pre-registered
band on PH; the Reynolds-stress rows land far *below* (better than) the published values
under the paper's own Eqs. 2-3, and a controlled diagnostic shows the published CBFS
stress value is only recovered if `b_ij^Delta` is *excluded* from the reconstructed
stress — the paper's tau norm convention is not identifiable from its text.**

Every number above and below traces to
`demo-output/website/campaign/W2_sparta_runs/{cbfs,ph}_{frozen,prop}/log.*` and
`score_*.json` (the numeric time directories are .gitignored run artifacts on disk).

## 1. Data and provenance

| Object | Source | Note |
| --- | --- | --- |
| CBFS case, 21,000 cells (140x150) | benchmark clone `data/CBFS` | the paper's own mesh size exactly; the clone's `log.run` traces to the authors' thesis codebase (B2 finding) |
| PH case, 15,600 cells (120x130) | benchmark clone `data/PH_Breuer` | same |
| LES fields U, k, tauij | `0/U_LES`, `0/k_LES`, `0/tauij_LES` in each case dir | consumed inside OpenFOAM, whose parser expands the `#include` macros natively — the B2 Ofpp blocker did not bite, exactly as the reading predicted; the frozen driver re-writes them plain for Python scoring |
| Baseline k-omega SST solution | shipped `data/CBFS/30000`, `data/PH_Breuer/10000` | B2 reproduced the CBFS baseline on this box's v2606 to 0.068% scaled MAE; baseline tau computed from these fields via `simpleFoam -postProcess -func "turbulenceFields(R)"` (`cbfs_baseline_post/`, `ph_baseline_post/`) |
| Consistency check | `k_LES` vs half-trace of `tauij_LES` | mean relative deviation 8.47e-5 (CBFS), 0.0 (PH) — the shipped k and tauij are mutually consistent |

Both cases are benchmark **training** cases; no scored test case was opened at any point.

## 2. Implementation

New code, committed before the first solve (`sdk/openfoam/sparta/`):

- `kOmegaSSTFrozen` — derived from stock v2606 `kOmegaSST`. Solves only the omega
  equation with U, k, b_ij frozen at the LES values (Eq. 5 form, production
  `(gamma/nu_t)(Pk + R)`, `Pk = min(-2k b_ij dUi/dxj, 10 betaStar omega k)` per Eq. 6);
  computes `R` each iteration as the residual of the steady **discrete** k equation
  (Eq. 4); `nu_t = a1 k / max(a1 omega, F23 S)` — the stock formula, identical to the
  paper's. Outputs `kDeficit` (R) and `bijDelta = b_data + (nu_t/k) S`.
- `kOmegaSSTCorrected` — stock v2606 `kOmegaSST` plus the two corrections read as static
  fields: `+R` in the k equation; `+gamma (G_extra + R)/max(nu_t, 1e-12)` in the omega
  equation with `G_extra = -2k b^Delta:grad(U)`; `G_extra` inside Menter's limiter for
  Pk; and `div(2k b^Delta)` in the momentum equation via `divDevRhoReff`. Reduces
  exactly to stock kOmegaSST at zero corrections (the property the baseline
  normalisation depends on; the omega-limiter placement deviation is declared in the
  pre-registration). Also registers the reconstructed stress
  `tauijRecon = (2/3)k I - 2 nu_t S + 2k b^Delta` (Eqs. 2-3) for scoring.
- `kCorrectiveFrozenFoam` — driver for the frozen solve; no momentum or pressure
  equation. Settle criterion, not a cap (pre-registered).
- Scoring: `sdk/scripts/sparta_frozen_score.py`; conventions pre-registered.

Discretisation: the benchmark cases' own `fvSchemes` (linear upwind divergence, central
diffusion) — which is what the paper states it used. Wall treatment: the cases' own
(wall-resolved; `omegaWallFunction` low-Re branch, `nutLowReWallFunction`, k = 1e-15 at
walls). Propagations restart from the shipped baseline solutions, as the paper specifies.

## 3. Frozen extraction — converged, fast, and settled

| Case | Converged at iteration | Settle verification | CPU |
| --- | --- | --- | --- |
| CBFS | **295** (omega initial residual < 1e-8 and max rel d(omega) < 1e-9 sustained 50 it) | L2(R) moved 0% over 59 further iterations — SETTLED | 6.2 s (`cbfs_frozen/log.frozen`, `time.frozen`) |
| PH | **1,243** (same criterion) | L2(R) moved 9.9e-6% over 249 further iterations — SETTLED | 12.0 s (`ph_frozen/log.frozen`) |

The paper claims "the solver reaches convergence after a few hundred iterations."
Measured here: CBFS yes (295); **PH took 1,243** — four times "a few hundred", still 12
seconds of CPU. The claim is qualitatively right about cost and optimistic about count.

## 4. Sign conventions verified by controlled experiment (LESSONS L-26)

**E1 — R in the k equation** (re-solve k from 0.5 x k_LES with extracted R, 500
iterations, frozen omega/nu_t; pre-registered prediction: drift < 1% with correct sign,
>= 10x worse flipped):

| Case | drift, RScale = +1 | drift, RScale = -1 | ratio |
| --- | --- | --- | --- |
| CBFS | 2.14e-5 | 507.1 | 2.4e7 |
| PH | 6.58e-2 | 0.999 | 15.2 |

CBFS passes both halves of the prediction outright. **PH violates the "< 1%" half** (6.6%
drift with the correct sign) while passing the 10x separation; the all-cyclic streamwise
boundaries leave the k level less strongly anchored than CBFS's fixed-value inlet, and
500 relaxed iterations do not fully re-converge it. Recorded as a partial miss of the E1
prediction, not smoothed over. The sign conclusion stands on the 15x separation.

**E2 — both corrections in the propagation** (500-iteration mini-runs on CBFS from the
baseline; prediction: flipped signs make eps(U) rise):

| Variant | eps(U)/eps(U_0) at iteration 500 | eps(tau)/eps(tau_0) at 500 |
| --- | --- | --- |
| correct signs | 0.448 (falling) | 0.038 |
| RScale = -1 | **16.6** | 3.82 |
| bScale = -1 | 0.889 | 2.21 |

Both flips degrade the solution; the R flip is catastrophic. Signs verified.
Logs: `cbfs_e2_plus/`, `cbfs_e2_signR/`, `cbfs_e2_signB/`.

## 5. Propagation convergence, measured (iteration honesty)

**CBFS** (`cbfs_prop/log.run`, checkpoints every 5,000 iterations, cap 30,000):

| Checkpoint | eps(U)/eps(U_0) | eps(tau)/eps(tau_0) |
| --- | --- | --- |
| 5,000 | 0.3975259863 | 0.0261696465 |
| 10,000 | 0.3975259863 | 0.0261696465 |
| 15,000 | 0.3975259863 | 0.0261696465 |

Identical to ten significant figures from the first checkpoint on: the corrected solution
was fully steady before 5,000 iterations. Settle rule (< 0.5% movement) fired at 10,000,
confirmed at 15,000; the run was **stopped at 15,000 by the pre-registered protocol, not
by a cap** (momentum initial residuals ~1e-7 at stop). Graded value: checkpoint 15,000.

**PH** (`ph_prop/log.run`, checkpoints every 2,500, cap 10,000):

| Checkpoint | eps(U)/eps(U_0) |
| --- | --- |
| 2,500 | 0.005036 |
| 5,000 | 0.003356 |
| 7,500 | 0.003332 |
| 10,000 | 0.003331 |
| 12,500 (confirmation, deliberately beyond the pre-registered cap) | 0.003331 |

Settle fired between 7,500 and 10,000 (0.03% movement), but the confirming checkpoint
would have fallen beyond the cap — so one extra 2,500-iteration segment was run *past*
the cap purely as confirmation and is labelled as such: the value did not move at the
sixth decimal. Graded value: checkpoint 10,000 (the in-cap settled value).

## 6. Grade against the pre-registered bands, and the tau-convention finding

Comparison convention (pre-registered, primary): unweighted cell mean over the entire
internal field; `eps(U)` summed over 3 components; `eps(tau)` Frobenius with
off-diagonals counted twice; denominators from the shipped baseline solutions.

- **CBFS velocity: docket gate PASS** — 0.39753 is inside [0.1135, 0.4541] and far below
  the 1.0 hard floor. **Tightened band NEAR MISS** — outside [0.1703, 0.2838]. Under the
  declared *secondary* convention (volume-weighted) the value is 0.27634, 21.7% above the
  published 0.22703 — just inside a +/-25% band. Noted, not used for grading.
- **PH velocity: HIT** — 0.003331 < 0.005 (published 0.00165; we achieve a 300x error
  reduction against the paper's 600x, within the declared one-sided band). Volume-weighted:
  0.001253, 24% *below* the published value.
- **Both tau rows: outside the +/-25% bands — in the direction of being far better than
  published** (CBFS 0.02617 vs 0.4949; PH 0.000337 vs 0.1495).

**The tau finding.** Under the paper's own Eqs. 2-3 the reconstructed stress includes
`2k b^Delta`, and once the mean flow and k are recovered this reconstructs the LES stress
almost exactly by construction — ratios of 0.026 and 0.0003, not 0.49 and 0.15. Table 1's
tau values are therefore not computable under that reading. Diagnostics run
(tau-convention variants, computed from the same graded checkpoints):

| Variant | CBFS | PH | Published |
| --- | --- | --- | --- |
| with b^Delta (pre-registered) | 0.02617 | 0.00034 | — |
| **without b^Delta, volume-weighted** | **0.47850** | 0.37560 | 0.4949 / 0.1495 |
| without b^Delta, unweighted | 0.51574 | 0.41802 | — |
| dev-only without b^Delta | 0.96768 | 1.01116 | — |

Excluding `b^Delta` from the output stress lands within 3.3% of the published CBFS value
(volume-weighted) — but does **not** recover PH's 0.1495 (0.376-0.418). The published tau
metric is consistent with a no-b^Delta convention on CBFS and with no convention we
tested on PH. **The omission stands as the finding: the paper does not state its error
norm, and its tau rows cannot be reproduced as specified.** The tau grade is recorded
exactly as pre-registered (outside band, better-than-published), with this analysis
attached rather than a post-hoc re-grade.

A second observation, worth carrying to any future Table 1 comparison: under volume
weighting *both* velocity rows land within +/-25% of the published values (0.276 vs
0.22703; 0.00125 vs 0.00165), while unweighted lands 75% high on CBFS. If Table 1 is an
integral (volume-weighted) MSE, our reproduction is within a quarter on every velocity
number. Declared here, not re-graded.

## 7. In-sample gate

`sdk/scripts/closure_in_sample_gate.py` run immediately before the work (2026-08-01
00:04 UTC) and after all data touches (00:52 UTC): **PASS** both times — "no declared
training, fitting, inversion or calibration set contains a scored case." CBFS13700 and
PH10595 are benchmark training cases; the eight scored cases were never opened.

## 8. Cost, measured

| Item | CPU |
| --- | --- |
| CBFS frozen extraction (incl. E1) | 6.2 s |
| PH frozen extraction (incl. E1) | 12.0 s |
| E2 sign mini-runs (3 x 500 it) | 120 s |
| CBFS propagation (15,000 it + 519 before stop) | 1,007 s |
| PH propagation (12,500 it) | 505 s |
| Baseline tau post-processing + volumes | ~10 s |
| **Total** | **~1,660 s = 27.7 core-min** of the 60 approved |

The extraction itself — the step the paper prices implicitly as cheap — is **18 seconds
of CPU for both training cases combined**. The paper's claim that k-corrective-frozen-RANS
is the cheap step is confirmed emphatically; the cost lives in the propagation
(and, downstream, the unpriced 184-simulation cross-validation, which this rung now
re-prices: a propagation restarting from a baseline settles by 5,000-10,000 iterations,
so the CBFS cross-validation column is nearer 12-20 core-hours than the 37 estimated
from full primals).

## 9. What the next rung (regression to symbolic model) needs

1. **Inputs are now on disk**: `kDeficit` and `bijDelta` for both training cases
   (`cbfs_frozen/354/`, `ph_frozen/1492/`), plus omega/nu_t on the same mesh — exactly
   the targets and the timescale `1/omega` needed to build the paper's 2-D library
   (T^(1..3), I1, I2, the 16-entry B vector of Eq. 13, |C_Delta| ~ 48 columns).
2. **The regression is a laptop-minute** (paper section 3.2, and our K ~ 15,600-21,000
   matches their K ~ 15,000). Elastic net over the (lambda, rho) grid of Eq. 17 plus
   Ridge inference per Eq. 20; checkable against the published models
   `M(1) = 0.39 T^(1)`, `M(2) = 0.1 T^(1) + 4.09 T^(2)` / `1.39 T^(1)`,
   `M(3) = 0.93 T^(1)` (Eqs. 22-24) — three published coefficients to hit, a cleaner
   gate than Table 1's tau rows.
3. **Cross-validation in CFD**: kOmegaSSTCorrected already takes model-generated fields;
   replacing static `kDeficit`/`bijDelta` by expressions evaluated per-iteration is the
   only solver change. Budget guidance from this rung: ~12-20 core-hours for the CBFS
   column, not 37.
4. **Blockers for a *faithful* full reproduction**: CD12600 (Laval & Marquillie) is not
   in the tree — data sourcing task; and the tau norm convention of Table 1/2 needs a
   decision *before* any tau-graded gate is pre-registered again (velocity-only gates
   sidestep it; Table 2 of the paper is velocity-only, so the model-discovery rung can
   be gated cleanly).
