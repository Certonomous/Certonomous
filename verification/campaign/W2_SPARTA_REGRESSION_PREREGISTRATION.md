# W2 SpaRTA step-2 pre-registration: sparse symbolic regression on the frozen corrections, and velocity-only validation of the discovered models

**Written 2026-08-01 01:11 UTC, before the candidate library was evaluated and before any
regression or model-driven solve was run.** Nothing below is edited after the fact. If a
result misses, the bands stay as written and the record says so. Paper: Schmelzer, Dwight &
Cinnella, *Flow Turb. Combust.* 104:579-603 (2020), version of record, READ IN FULL, held at
`docs/papers/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf`. Previous rung:
`W2_SPARTA_FROZEN_CBFS.md` (frozen fields settle-verified; CBFS velocity docket gate PASS,
PH band HIT). In-sample gate run immediately before this file was written (01:11 UTC): PASS.

## What is being reproduced

Section 5 of the paper: the model-discovery step (Eqs. 13-21) applied to the frozen-RANS
corrections of the two training cases in the tree, and the velocity-only cross-validation
numbers of Table 2 for the resulting models. **CD12600 is not in the tree** (declared in the
reading and in the last rung's record), so of the paper's three training columns only
CBFS13700 and PH10595 are reproducible; every gate below is scoped accordingly.

Published targets, quoted from the version of record:

- **Eq. 22:** M(1): b_Delta = 0, M_R = 0.39 T(1).
- **Eq. 23:** M(2): b_Delta = 0.1 T(1) + 4.09 T(2), M_R = 1.39 T(1).
- **Eq. 24:** M(3): b_Delta = 0, M_R = 0.93 T(1).
- Section 5, ensembles: 7 distinct b_Delta forms for PH, 8 for CBFS; **1 distinct R form
  for CBFS**, 3 for PH; "We identify T(1), I1 T(1) and I2 T(1) as the relevant candidates
  to regress R."
- **Table 2** (velocity-only, so the tau-norm finding of the last rung does not touch it):
  M(1) 0.17166 (PH) / 0.30861 (CBFS); M(2) 0.32683 / 0.48244; M(3) 0.19737 / **0.32062
  (rank 1 on CBFS)**.
- Training-data attribution: the paper states the best-model-per-case expectation "holds for
  the cases CBFS13700 and CD12600" — so **M(3) (rank 1 on CBFS) is CBFS-trained** and M(2)
  (rank 1 on CD) is CD-trained. M(1)'s training case is **not identifiable from the text**
  (rank 1 on PH, but the paper says PH-trained models are outperformed on PH by the other
  two training sets); it is therefore not used as a coefficient gate, only reported against.

## Implementation conventions, declared now

The paper leaves several regression conventions unstated. Fixed here before running
(`sdk/scripts/sparta_regression.py`, committed with this file):

1. **Inputs**: the frozen fields already on disk (`cbfs_frozen/354`, `ph_frozen/1492`):
   U = U_LES, k = k_LES, omega = frozen-solve omega, targets kDeficit (R) and bijDelta.
   grad(U) computed by OpenFOAM `postProcess -func 'grad(U)'` on those directories — the
   same discrete gradient the frozen solve used. All internal cells, unweighted (K = the
   paper's "number of data points K ~ 15000"; ours 21,000 / 15,600).
2. **Basis**: paper Eqs. 10-12 taken literally, A_ij = d_j U_i, S = (tau/2)(A + A^T),
   W = (tau/2)(A - A^T), tau = 1/omega; I2 = W_mn W_nm (negative). The R candidates carry
   the 2k factor of Eq. 12 so the inferred coefficients are directly comparable to
   Eqs. 22-24. The paper's index convention for Omega only fixes the **sign of T(2)
   coefficients**; ours is declared here and used identically in the library builder and
   the propagation solver (`kOmegaSSTSparta`), so velocity results are convention-free.
3. **Stacking (primary)**: the b_Delta target and candidates stacked over all 9 tensor
   entries (= Frobenius weighting, the last rung's primary convention). **Secondary,
   reported**: 6 unique components once each. The paper says only "stacked to vectors".
4. **Selection**: elastic net exactly per Eqs. 17-19 (rho grid of Eq. 18; 100 log-spaced
   lambdas down to 1e-3 lambda_max; lambda_max = max|C^T Delta|/(K rho), which is the
   sklearn/coordinate-descent normalisation the paper's own lambda_max formula implies),
   coordinate descent, candidates standardised to unit RMS **without centring** (the
   physical model has no intercept; centring would smuggle one in). Candidates with any
   |value| > 1e5 discarded first (Section 3.1), discards reported.
5. **Inference**: Ridge per Eq. 20 **as literally written** (raw candidates, no 1/K),
   lambda_r in {0.01, 0.0316, 0.1} — the endpoints of the paper's stated admissible range
   and its geometric mid. **Primary graded coefficient: lambda_r = 0.0316.** The paper does
   not state which lambda_r produced Eqs. 22-24, nor the normalisation that makes
   lambda_r's magnitude meaningful; the spread over the range is reported. If the spread
   is negligible (expected: Eq. 20 as written makes lambda_r ~ 0.1 vanish against C^T C),
   that observation is itself reported as a finding about the published lambda_r range.

## Gates, declared now

**G1 (form, CBFS R) — binding.** The set of distinct abstract R-model forms discovered on
CBFS contains the form {T(1)} (the paper's single reported CBFS form, and the form of
M(3)). Reported alongside, not gated: the count of distinct forms (paper: 1).

**G2 (coefficient, CBFS R) — binding, the headline gate.** The Ridge-inferred coefficient
of the pure-{T(1)} CBFS form at the primary lambda_r:
  - **HIT** if within **0.93 +/- 25%**, i.e. in **[0.6975, 1.1625]**;
  - **NEAR MISS** if within a factor of two, [0.465, 1.86];
  - **MISS** otherwise.
  Context reported, not graded: the paper's three published pure-T(1) coefficients span
  [0.39, 1.39] across training cases.

**G3 (form, PH R) — binding.** Every distinct R form discovered on PH draws only from
{T(1), I1 T(1), I2 T(1)} (the paper's stated relevant candidates). Count reported vs 3.

**G4 (form, b_Delta) — binding.** The sparsest discovered b_Delta form on PH activates
T(2), and the sparsest on CBFS activates T(3) (the leading candidates of the paper's
Fig. 3a/3c model-1 rows). Candidate-union overlap with the paper's Fig. 3 axes reported.

**G5 (velocity-only validation) — binding.** The discovered CBFS model (R-only, pure
T(1), primary-lambda_r coefficient) is propagated by `kOmegaSSTSparta` (symbolic model
evaluated each iteration from the current solution — NOT the static frozen fields) on both
cases, restarting from the shipped baselines, and graded under the last rung's primary
convention (unweighted cell mean, whole internal field, 3 velocity components; ratios
against the same shipped-baseline denominators):
  - **V1, CBFS**: against published M(3)-on-CBFS = 0.32062. Binding gate factor two,
    [0.1603, 0.6412], hard floor < 1.0. Tightened band +/- 25%: [0.2405, 0.4008].
  - **V2, PH**: against published M(3)-on-PH = 0.19737. Factor two [0.0987, 0.3947],
    floor < 1.0. Tightened +/- 25%: [0.1480, 0.2467].
  Volume-weighted values reported alongside (last rung's finding: Table 1 velocity rows
  land within +/-25% under volume weighting; if the same holds for Table 2 it is reported,
  not re-graded). **Tau ratios are reported, never graded** — the tau norm convention is
  unresolved (shipped finding, last rung section 6).

**Contingency, declared now:** if the discovered CBFS coefficient differs from 0.93 by
more than 10%, the published M(3) = 0.93 T(1) **as written** is additionally propagated on
both cases and graded against the same V1/V2 bands; the discovered-model runs are still
reported. This separates a regression mismatch from a propagation mismatch.

**Reported, not graded (run in this priority order, only while the budget holds):**
published M(1) = 0.39 T(1) as written on both cases (vs 0.30861 / 0.17166); published
M(2) as written (both corrections) on both cases (vs 0.48244 / 0.32683); the sparsest
PH-discovered R model on PH. Training-MSE context: our best-form MSEs reported against the
paper's Fig. 3/4 axis scales (PH b_Delta ~ 0.008, CBFS b_Delta ~ 0.013-0.017, PH R
~ 0.00218, CBFS R ~ 1.7e-5 to 1.8e-5).

**A different sparse model is a legitimate negative result.** If the discovered forms or
coefficients sit outside every band above, the record ships them with the full
regularisation path (grid-survival counts per form) and the gates stay as written.

## Convergence and verification protocol (reused from the last rung)

- **Propagations**: restart from the shipped baselines. Checkpoints every 5,000 iterations
  (CBFS, cap 30,000) / 2,500 (PH, cap 10,000). Settled when the graded velocity ratio
  moves < 0.5% (relative) between consecutive checkpoints, confirmed by one further
  checkpoint. A cap-stop without settle is reported and not graded as a hit. A diverged
  or non-converging model run is reported under the paper's own exclusion rule
  (Section 3.3: "we exclude models, if they are not converging on a given test case").
- **IC1 (implementation cross-check, before any propagation is graded)**: the solver's
  construction-time-evaluated kDeficit and bijDelta (written via
  `writeInitialCorrections`) on the frozen input fields must match the Python library
  builder's evaluation to relative L2 < 1% on both fields. Catches component-ordering,
  exponent-mapping, 2k-factor and I2-sign slips between the two implementations.
- **E3 (sign falsifier, L-26 discipline)**: a 500-iteration CBFS mini-run of the
  discovered model against the same run with the coefficient negated: the negated run
  must show a higher eps(U) at iteration 500. Both numbers reported.

## In-sample position

CBFS13700 and PH10595 are benchmark training cases; no scored test case is opened.
`closure_in_sample_gate.py`: PASS at 01:11 UTC before this work; re-run after all data
touches and quoted in the record.

## Budget

Filed on the docket as `w2-sparta-regression-discovery`, 180 core-min, basis measured on
this box by the last rung: CBFS propagation 1,007 s per 15,500 iterations (worst case at
the 30,000 cap ~ 33 core-min), PH 505 s per 12,500 (~8.5 core-min at cap). Graded set V1
+ V2 worst case ~ 42 core-min; contingency + reported extras bounded by the remaining
budget, stopping in the declared priority order. The regression itself is claimed by the
paper to be "of the order of a minute on a standard consumer laptop" (Section 3.2);
ours is timed and reported next to that claim.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf` | `docs/papers/data_driven_rans/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
