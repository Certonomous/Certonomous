# W2 SpaRTA step 2 — sparse symbolic regression on the frozen corrections, and velocity-only validation of the discovered models

Date run: 2026-08-01 (UTC). Docket item: `w2-sparta-regression-discovery` (filed this
session under Katie's standing authorization; 180 core-min; **137 measured**, section 9).
Pre-registration: `W2_SPARTA_REGRESSION_PREREGISTRATION.md`, committed 01:14 UTC before the
library was ever evaluated; every gate below is graded exactly as written there. Machine:
the lab's 16-vCPU box, all solves serial, nine propagations run concurrently (load ~9).

**Paper.** Schmelzer, Dwight & Cinnella, "Discovery of Algebraic Reynolds-Stress Models
Using Sparse Symbolic Regression," *Flow Turb. Combust.* 104:579-603 (2020), version of
record, READ IN FULL. Targets: the discovered models of Eqs. 22-24, the ensemble structure
of Section 5 / Figs. 3-4, and Table 2's velocity-only errors. CD12600 is not in the tree
(declared), so only the PH10595 and CBFS13700 columns are in play.

## RESULT

| Gate (pre-registered) | Published | Ours | Grade |
| --- | --- | --- | --- |
| G1: CBFS R discovery contains the form {T(1)} | the paper's single CBFS form | present, and the dominant form (181 of 891 grid survivals) | **HIT** |
| G2: CBFS {T(1)} coefficient, primary lambda_r | M(3): **0.93** (Eq. 24) | **0.5448** (lambda_r sweep 0.461-0.578; unregularised OLS 0.594) | **NEAR MISS** (inside factor two, outside +/-25%; 0.93 is unreachable from our CBFS frozen fields at any lambda_r >= 0 — see section 4) |
| (context, not a gate) PH {T(1)} coefficient | M(2)_R: **1.39** (Eq. 23) | **1.3992** (sweep 1.390-1.402) | matches the published coefficient to **0.66%** |
| G3: PH R forms drawn only from {T1, I1 T1, I2 T1} | the paper's stated relevant candidates | those subsets carry 27.5% of grid survivals (the T1-family with higher monomials, 44.7%); 190 of 206 transitional forms touch other candidates | **MISS** as worded; the *sparsest and most-surviving* form is pure {T1}, as published |
| G4: sparsest b_Delta form activates T2 (PH) / T3 (CBFS) | Fig. 3a / Fig. 3c leading candidates | PH sparsest = {T2} — hit; CBFS sparsest = {T2}, T3 enters at the *two*-term form {T2, T3}, which out-survives it (143 vs 117 hits) | **half HIT, half MISS** |
| G5-V1: discovered CBFS model propagated on CBFS, eps(U)/eps(U0) | M(3) on CBFS: **0.32062** (Table 2, rank 1) | **0.36051** (volume-weighted 0.33799) | factor-two gate **PASS**; tightened +/-25% **HIT** (12.4% above) |
| G5-V2: discovered CBFS model propagated on PH | M(3) on PH: **0.19737** | **0.14292** (volume-weighted 0.08383) | factor-two **PASS**; tightened band [0.1480, 0.2467] **NEAR MISS from the good side** (3.4% below the lower edge — the model does *better* than published) |
| Contingency (triggered): published M(3) = 0.93 T(1) as written, on PH | 0.19737 | **0.20301** | within **2.9%** |
| Contingency: published M(3) as written, on CBFS | 0.32062 | **0.47077** | 47% high — outside +/-25%, inside factor two |

**One-line verdict: the regression pipeline reproduces the paper's model FORM exactly
(pure T(1) for R, both cases) and the PH coefficient to 0.66%, and the propagation
harness reproduces Table 2's PH column to 3% for both published models as written — but
the CBFS-trained coefficient comes out 0.54, not the published 0.93, and 0.93-as-written
does not reproduce the paper's own CBFS velocity number in our harness (0.471 vs
0.32062) while our discovered 0.54 lands within the pre-registered band (0.361). The
CBFS-side discrepancy is coherent across every CBFS quantity this ladder has measured
and is shipped as the finding of this rung (section 8).**

All numbers trace to `W2_sparta_runs/regression/*.json`, `W2_sparta_runs/*/log.run`,
`*/score_*.json` and `*/time.run` (numeric time directories are .gitignored run
artifacts on disk).

## 1. Inputs and provenance

Frozen fields from the previous rung, settle-verified there (295 / 1,243 iterations):
`cbfs_frozen/354` and `ph_frozen/1492` — U = U_LES, k = k_LES, omega = frozen-solve
omega, targets kDeficit (R) and bijDelta. grad(U) computed by `postProcess -func
'grad(U)'` on those directories (same discrete gradient as the frozen solve; the reader
in `sparta_frozen_score.py` gained a 9-component tensor branch for it). All internal
cells, unweighted: K = 21,000 (CBFS) / 15,600 (PH) — the paper's "K ~ 15000".

## 2. Implementation (committed before the pre-registration ran)

- `sdk/scripts/sparta_regression.py` — the paper's Eqs. 10-15 and 17-20: 16-monomial B
  vector (Eq. 13), 48 tensor candidates for b_Delta and 48 scalar candidates for R (the
  2k of Eq. 12 carried in the candidate so coefficients compare directly to Eqs. 22-24);
  the |value| > 1e5 discard rule (**no candidate was discarded on either case** — the
  paper's "|C_Delta| ~ 48" is exactly 48 here); elastic net per Eqs. 17-19 (rho grid,
  100 log-spaced lambdas to 1e-3 lambda_max, coordinate descent on the Gram matrix,
  unit-RMS uncentred standardisation); Ridge inference per Eq. 20 as literally written,
  lambda_r in {0.01, 0.0316 (primary), 0.1}.
- `sdk/openfoam/sparta/spartaTurbulenceModels/kOmegaSSTSparta.{C,H}` — kOmegaSSTCorrected
  with the static fields replaced by the symbolic model evaluated from the *current*
  solution every iteration (terms read as (tensor, I1-exp, I2-exp, coeff) quadruples);
  reduces exactly to stock kOmegaSST at zero terms; same declared omega-limiter deviation
  as the last rung.

## 3. Model discovery — what the elastic-net path found

| Quantity | Paper | Ours (primary 9-comp stacking) |
| --- | --- | --- |
| distinct R forms, CBFS | 1 | 77 (dominant {T1}, 181/891 survivals; next {T1, I2 T1}, 94) |
| distinct R forms, PH | 3 | 206 (dominant {T1}, 231/891; the declared 3-candidate subsets carry 27.5% of survivals) |
| distinct b_Delta forms, CBFS | 8 | 196 (sparsest {T2} 117, {T2,T3} 142) |
| distinct b_Delta forms, PH | 7 | 170 (sparsest {T2}, 203 survivals) |
| R relevant candidates | T1, I1 T1, I2 T1 | same three lead; every high-survival R form is T1-led |
| b_Delta leading candidates | Fig. 3a: T2 first (PH); Fig. 3c: T3, T2 (CBFS) | PH: T2 first by survival mass; CBFS: T2 then T3 |

The form-count mismatch (77/206 vs 1/3) is a **dedup-convention finding**: with 900
(lambda, rho) grid points and warm-started paths, transitional supports proliferate;
"the set of D unique abstract model forms" (Section 3.2) evidently means something more
pruned than literal support uniqueness — most of our extra forms are one high-survival
form plus low-survival satellites whose extra Ridge coefficients infer to ~0. The paper
does not state its pruning; recorded, not smoothed over.

**Coefficients** (Ridge, primary lambda_r = 0.0316; sweep endpoints bracketed):

| Model | Published | Ours | Sweep |
| --- | --- | --- | --- |
| R on CBFS, {T1} | 0.93 (Eq. 24, M(3); the paper's best model on CBFS) | **0.5448** | [0.4614, 0.5778]; OLS 0.594; volume-weighted OLS 0.567 |
| R on PH, {T1} | 1.39 (Eq. 23, M(2)_R) | **1.3992** | [1.3899, 1.4021] |
| b_Delta on PH, {T2} | — (M(2)_bDelta has 4.09 T2, training case CD not held) | -7.996 | [-8.016, -7.930] |
| b_Delta on CBFS, {T2,T3} | — | T2 -2.06, T3 +2.70 | — |

The T2 signs are stated under this record's declared velocity-gradient convention
(A_ij = d_j U_i taken literally from the paper's Section 2.2); a transposed-gradient
convention flips them. T1 coefficients are convention-free.

**Training-MSE context** (theirs read off the Fig. 3/4 axes; convention unstated there):

| Quantity | Paper (axis) | Ours |
| --- | --- | --- |
| eps(R), PH, best forms | 0.002182-0.002187 | {T1}: **0.002167** (zero-model 0.003461) |
| eps(R), CBFS | 1.70e-5 - 1.85e-5 | {T1}: **3.75e-5** (zero-model 4.33e-5) — factor ~2 high, see section 8 |
| eps(b_Delta), PH | ~0.00795 | 6-comp {T2}: 0.00660 (zero 0.01229); 9-comp 0.00486 (zero 0.00866) |
| eps(b_Delta), CBFS | 0.013-0.017 | 6-comp {T2,T3}: **0.01458**, zero-model **0.01713** — inside the paper's axis range |

PH agrees almost exactly; CBFS is off by ~2x on R — the same side of the ledger as every
other CBFS discrepancy (section 8).

**lambda_r finding.** The paper gives 0.01 < lambda_r < 0.1 with no normalisation for
Eq. 20. As written (raw candidates), that range moves the PH coefficient by 0.9% —
regularisation-irrelevant — but the CBFS coefficient by 20% (0.461-0.578), because the
CBFS candidates' raw norms are small. A stated range whose effect spans "nothing" to
"a fifth of the coefficient" depending on the case's dimensional scale is not a usable
specification; second unstated-norm finding of this ladder.

## 4. Why 0.93 cannot come out of our CBFS data — bounded, not asserted

For a single-candidate Ridge fit the coefficient is c = x'y/(x'x + lambda_r) <= OLS.
Our CBFS OLS for {T1} is 0.594 (volume-weighted 0.567, secondary 6/9-stacking identical
for the scalar R target). No lambda_r >= 0 and neither declared weighting reaches 0.93
from these fields; the discrepancy is in the data or the paper's processing, not in a
tunable of ours. Noted as context (a colourbar reading, not a number): Fig. 4's single
CBFS R model is drawn light-red, visibly nearer +0.4-0.5 than +0.93 on its +/-1 scale —
i.e. the paper's own figure is closer to our 0.54 than to its own Eq. 24.

## 5. Implementation cross-checks (pre-registered)

- **IC1**: solver-evaluated corrections (construction-time write on the frozen inputs,
  6-term test model exercising T1/T2/T3 and I1/I2 powers) vs the Python builder:
  relative L2 **5.96e-15** (kDeficit) and **2.47e-15** (bijDelta) — bit-identical
  implementations. Gate < 1%: PASS. (`cbfs_ic1/`)
- **E3 sign falsifier** (L-26): discovered model +0.5448 vs -0.5448, 500 iterations from
  the CBFS baseline: eps(U)/eps(U0) = **0.372 vs 11.59**. Prediction (flip degrades)
  confirmed, 31x separation. (`cbfs_e3_plus/`, `cbfs_e3_minus/`)

## 6. Propagation convergence (iteration honesty)

Nine model-driven propagations (kOmegaSSTSparta, restart from shipped baselines,
checkpoints 5,000/2,500, caps 30,000/10,000). All CBFS runs were steady before the first
checkpoint (ratios identical to >= 5 significant figures at 5,000/10,000/15,000; settle
fired at 10,000, confirmed 15,000; stopped by protocol, not cap). PH runs settled with
< 0.1% movement 7,500 -> 10,000 — except **ph_m2pub (M(2) as written), which cap-stopped
UNSETTLED**, oscillating 0.432/0.410/0.421/0.409 across checkpoints; its k-equation also
logged 39 bounding events (CBFS m2: 1,745). Consistent with the paper's own statement
that b_Delta corrections "can do harm to the convergence properties"; reported, not
graded, per the pre-registered exclusion rule.

## 7. Velocity-only validation against Table 2 (graded rows in RESULT above)

| Run | Model | Case | ours eps(U)/eps(U0) | published | delta |
| --- | --- | --- | --- | --- | --- |
| cbfs_mdisc | discovered CBFS 0.5448 T1 | CBFS | **0.36051** (vw 0.33799) | 0.32062 (M3) | **+12.4%** — HIT |
| ph_mdisc_cbfs | same | PH | **0.14292** (vw 0.08383) | 0.19737 (M3) | -27.6% — NEAR MISS, better than published |
| cbfs_m3pub | 0.93 T1 as written | CBFS | 0.47077 (vw 0.46548) | 0.32062 | +47% |
| ph_m3pub | 0.93 T1 as written | PH | **0.20301** (vw 0.15516) | 0.19737 | **+2.9%** |
| cbfs_m1pub | 0.39 T1 as written | CBFS | **0.33316** (vw 0.30228) | 0.30861 (M1) | **+8.0%** |
| ph_m1pub | 0.39 T1 as written | PH | **0.16578** (vw 0.10317) | 0.17166 (M1) | **-3.4%** |
| cbfs_m2pub | M(2) as written (b_Delta + R) | CBFS | 0.73824 | 0.48244 (M2) | +53%; paper itself reports both-corrections detrimental on CBFS |
| ph_m2pub | M(2) as written | PH | 0.40912 (cap-stop, unsettled) | 0.32683 (M2) | +25% at cap |
| ph_mdisc_ph | PH-discovered 1.3992 T1 (R-only) | PH | 0.35744 | (0.32683 is M2 *with* b_Delta) | +9.4% vs that context row |

Tau ratios, **reported never graded** (norm finding stands): the discovered model gives
tauF 0.709 (CBFS) / 0.688 (PH) — better than baseline; the larger published coefficients
degrade tau while helping U (ph_m3pub 1.136, ph_mdisc_ph 2.14, m2 runs 2.2-3.4): R-only
overcorrection buys mean-flow accuracy by inflating k, exactly the mechanism the paper
identifies (its Section 5 production-multiplier reading of T(1)).

**Reading.** Table 2's PH column is reproduced to <= 3.4% by the published models as
written under the pre-registered unweighted convention — the propagation harness is
therefore validated end-to-end against the paper's own numbers. On that validated
harness, Eq. 24's 0.93 does **not** reproduce Table 2's CBFS entry (0.471 vs 0.32062),
while our CBFS-discovered 0.5448 lands 0.361 — inside the pre-registered +/-25% band of
the published value. The published CBFS coefficient and the published CBFS velocity
error appear mutually inconsistent in our harness; our discovered model satisfies the
velocity number better than the published coefficient does.

## 8. The finding: the discrepancies are all on the CBFS side, and they cohere

PH ledger: coefficient 1.3992 vs 1.39 (0.66%); training eps(R) 0.002167 vs ~0.00218;
Table 2 reproductions +2.9% and -3.4%; last rung's Table 1 band HIT. CBFS ledger:
coefficient 0.545 vs 0.93; training eps(R) 2x high; Table 1 velocity ratio 75% high
unweighted (22% volume-weighted, last rung); Table 2 via 0.93-as-written 47% high.
Every PH-side quantity this ladder has measured matches the paper tightly; every
CBFS-side quantity is off in a correlated direction. A single unstated difference in the
paper's CBFS processing (or in the benchmark clone's CBFS packaging of Bentaleb's LES)
would explain all of it; nothing on our side can, since the coefficient is
scale-invariant, both weightings were computed, IC1 is exact, and the harness reproduces
the PH column. **Shipped as this rung's finding, alongside the internal tension between
the paper's Eq. 24 and its own Table 2 CBFS entry in our harness.**

## 9. In-sample gate and cost

`closure_in_sample_gate.py`: **PASS** at 01:11 UTC (before) and re-run after all data
touches (section committed with this record): CBFS13700 and PH10595 are benchmark
training cases; no scored case was opened.

| Item | CPU (user time from /usr/bin/time; regression from `time`) |
| --- | --- |
| 4 discovery runs (2 cases x 2 stackings; selection + inference) | 917 s = 15.3 core-min (the paper's "order of a minute on a laptop" for one selection is confirmed: one case-target path is ~25-55 s) |
| grad(U) post-processing, IC1 | ~10 s |
| E3 sign mini-runs (2 x 500 it) | ~80 s |
| 9 propagations (measured per-run, sum) | 7,115.6 s = 118.6 core-min |
| scoring | ~60 s |
| **Total** | **~137 core-min** of 180 filed |

## 10. What the final rung (cross-validation in CFD) needs

1. **Re-priced budget confirmed**: a model-driven propagation costs the same as a
   static-field one (CBFS ~15-16 core-min to settle at 15,000 it under load, PH ~13);
   the paper's 75-simulation CBFS column prices at **~12-20 core-hours**, not 37. The
   ensembles to cross-validate are on disk (`regression/*_discovery_9.json`), and
   `kOmegaSSTSparta` takes any of them as a dictionary — no further solver work.
2. **A form-pruning rule must be pre-registered first** (e.g. minimum grid-survival mass
   or Ridge-coefficient floor) to get from 77/206 raw supports to a paper-sized ensemble
   (~10-20 models); otherwise the 184-simulation design explodes.
3. **CD12600 remains the missing third column** — data sourcing (Laval & Marquillie),
   unchanged.
4. **The CBFS-side coherent discrepancy** (section 8) is the open question worth a
   zero-compute pass: diff the benchmark clone's CBFS packaging against Bentaleb's
   published LES statistics before spending any further CBFS core-minutes.
