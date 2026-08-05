# Closure Challenge — methods comparison and evidence audit

Audit record, 2026-08-04. Brief: proof-check the closure-challenge line
end-to-end — our own evidence first (assume the records overstate until
verified), then the other four entrants from their own documents, then the
honest comparison. **TEST-BLIND throughout: no scored-test ground truth was
read by this audit; the in-sample leakage guards stay armed. Read-only on the
web; nothing was posted; nothing was submitted.**

Companion records this audit checked rather than inherited:
`CLOSURE_CHALLENGE_STATUS.md`, `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`,
`closure_challenge_trained_entry{,_round2,_round3_gated,_round4_duct}.json`,
`closure_challenge_C1_error_estimator.{md,json}`,
`closure_challenge_C2_error_decomposition.md`,
`closure_challenge_C6_hump_decision.md`,
`closure_challenge_duct_reynolds_transfer.json`,
`closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md`,
`sdk/scripts/closure_*.py`, `sdk/scripts/train_closure_*.py`,
the benchmark clone at `deb91557`, and the evaluation package at `1c4e22c8`.

---

## Part 1 — our own evidence, prediction by prediction

### 1.0 The metric, defined from the benchmark's own eval code (not our prose)

Read directly from
`/home/ubuntu/closure-challenge-pkg/src/closure_challenge/eval.py` by this
audit:

- **Per-case** (`evaluate_individual_case`):
  `mean(||U_pred − U_true||₂)` over the case's 1000 fixed evaluation points,
  divided by `mean(||U_true||₂)` — a scaled MAE of the **velocity vector
  magnitude of the error**, not component-wise.
- **Overall** (`score`): `np.mean` of the 8 per-case values, **unweighted**.
  Lower is better.
- Consequence worth keeping in view: one case's improvement of Δ moves the
  overall by Δ/8, and the two PH `alpha_15` cases (floors 0.1320/0.2049)
  dominate the floor while contributing the same 1/8 weight as everything
  else.

Our records state this metric correctly (`closure_challenge_trained_entry.json`
`metric_definition`; `CLOSURE_CHALLENGE_STATUS.md` §1). **Confirmed, no
discrepancy.**

### 1.1 The eight predictions of the round-4 entry of record (0.0654)

What each submitted field actually is, per the entry of record
(`closure_challenge_trained_entry_round4_duct.json`, commit `4c2f3562`; CSVs
at `closure_challenge_submission_round4/test/`, re-verified by this audit:
all eight are 1000×3, all-finite, comma-delimited):

| # | Case | Score | Submitted field | Model behind it |
|---|------|-------|-----------------|-----------------|
| 1 | `alpha_15_13929_4048` | 0.0501 | corrected | round-1 PH model (gate: APPLY) |
| 2 | `alpha_15_13929_2024` | 0.1011 | corrected | round-1 PH model (gate: APPLY) |
| 3 | `alpha_05_4071_4048` | 0.0461 | **unmodified RANS** | none (C1 gate: DECLINE) |
| 4 | `alpha_05_4071_2024` | 0.0719 | **unmodified RANS** | none (C1 gate: DECLINE) |
| 5 | `AR_1_Ret_360` | 0.0811 | corrected | Variant D duct model (round 4) |
| 6 | `AR_3_Ret_360` | 0.0775 | corrected | Variant D duct model (round 4) |
| 7 | `AR_14_Ret_180` | 0.0325 | corrected | Variant D duct model (round 4) |
| 8 | `NASA_2DWMH` | 0.0632 | corrected | round-1 PH model (pre-registered; worse than floor by +0.0011, not reverted) |

Two model objects therefore stand behind all six corrected predictions:

- **PH model** (predictions 1, 2, 8): `HistGradientBoostingRegressor` ×3,
  `max_iter=300, max_depth=6, learning_rate=0.05, l2_regularization=1.0,
  random_state=0`, 7 features, trained on 21 PH cases, **327,600 cells**
  (`train_closure_periodic_hill_correction.py`).
- **Duct Variant D** (predictions 5–7): same architecture, 8 features
  (adds `d/d_max`), velocity-scale-normalised target, trained on 4 ducts,
  **41,971 cells** (`closure_round4_duct_rescale.py`).

Plus the **C1 decline gate** (predictions 3, 4): top-3-feature Ridge
(alpha 0.7499, threshold 0.1263), fit on the 21 PH training cases only
(`closure_baseline_error_gate.py`).

### 1.2 The audit table

Column (a) is settled above and identical for all 8. The remaining columns,
with the verdict per column stated once where it is common:

| # | Case | (b) baseline-RANS convergence evidence | (c) training convergence / seed & HP sensitivity | (d) a-posteriori physicality of submitted field | (e) provenance chain |
|---|------|------|------|------|------|
| 1 | `alpha_15_13929_4048` | **Nowhere in our records.** Exists unexamined in benchmark data: `Parm_PH_29/.../postProcessing/residuals/0/residuals.dat`, 20,000 iterations, final residuals Ux/Uy/k/omega ≈ 1e-10, p ≈ 1e-6 (sampled by this audit) | Single seed (`random_state=0`), never varied. **Seed genuinely matters here**: 327,600 training cells > sklearn 1.9.0's 200,000-row binning subsample threshold, so bin edges are seed-dependent (verified against the `closure-venv` sklearn source). No HP sweep ("nothing tuned" — clean against tuning-leakage, silent on sensitivity). No training-loss curve recorded. Train 0.0620 / val 0.0876 pooled MAE, overfit flag false — the only stability evidence | **No physics check.** Corrected `U = U_RANS + δU` predicted cell-wise; continuity (∇·U ≈ 0) never audited; only finiteness + shape + "mean-|U| inside the band of the four accepted submissions" were checked | Strong: round-1 record commit `c95e2109`; round-3 gate application `cb0694d1`; CSV SHA-256 in round-3 `MANIFEST.json`; carried byte-identical into round 4 (hash re-verified) |
| 2 | `alpha_15_13929_2024` | same as #1 | same as #1 | same as #1 | same as #1 |
| 3 | `alpha_05_4071_4048` | same family evidence as #1; **more load-bearing here** — the submitted field IS the baseline, so the baseline's convergence record is the entire convergence story of this prediction | n/a for the field (no model applied). Gate: RidgeCV is deterministic (no seed question); threshold from train-LOO median; validated AUC 1.0, 4/4 — on **n=4 with 1 positive** (≈1-in-4 by luck, stated in C1) | Field is the organisers' own converged solve — physicality inherited, and the strongest of the 8 on this column. Byte-equivalence to shipped RANS verified to 5e-10 write precision (`closure_challenge_decline_gate_audit.json`) | Strong: C1 `5719374e`; refit reproduces alpha/threshold byte-for-byte; decline audit re-derived the field independently |
| 4 | `alpha_05_4071_2024` | same as #3 | same as #3 | same as #3 | same as #3 |
| 5 | `AR_1_Ret_360` | **Nowhere in our records.** Exists in benchmark data: `DUCT/AR_1_Ret_360/log.run` — `SIMPLE solution converged in 405 iterations` under `residualControl` (k 5e-6, omega 1e-10); Ux initial residual 1.8e-6 at the last iteration. (The O(0.4) Uy/Uz initial residuals are a normalisation artifact on a ~1e-15 transverse field — checked by this audit so nobody later mistakes it for a divergent solve) | Single seed, but **bin-deterministic**: 41,971 cells < 200,000 subsample threshold, so `random_state` is inert for Variant D — seed sensitivity is a non-issue here *by construction, not by measurement*. Model-form sensitivity was measured (variants A vs D on AR_7, leave-one-duct-out, PH Reynolds sweep — `closure_challenge_duct_reynolds_transfer.json`, commit `d0992da2`); HP sensitivity was not | **No physics check**, and weakest here: the round-4 script asserts shape (1000,3) but has **no finiteness check** of its own (this audit ran one: all finite). Corrected duct field's continuity never audited | **Gap**: the three new round-4 duct CSVs have **no recorded SHA-256** and the round-4 submission dir has **no MANIFEST.json** — the manifest discipline covers only the 5 copied cases. Otherwise strong: entry `4c2f3562`, pre-registration committed before scoring |
| 6 | `AR_3_Ret_360` | same as #5 (own `log.run`, converged) | same as #5 | same as #5 | same as #5 |
| 7 | `AR_14_Ret_180` | same as #5 (own `log.run`, 98k-line history, converged) | same as #5 | same as #5; the 0.00003 board lead makes any unmeasured numerical slop on this case material | same as #5 |
| 8 | `NASA_2DWMH` | **Nowhere in our records.** Exists in benchmark data: `NASA_2DWMH/log.run`, final initial-residuals ≈ 1e-8–1e-10 (sampled by this audit) | same PH model as #1 → same live seed question | same as #1, plus `gradU` here is our own Green-Gauss reconstruction (validated on PH training cases only — r 0.9997–1.0000) | Strong: round-2 record `6efc468c`, pre-registered model choice; C6 partial withdrawal honestly recorded (`closure_challenge_C6_hump_decision.md`) |

### 1.3 Findings (the deliverable), ranked and costed

Ranked by how much the entry's credibility or score rests on the unverified
assumption. Each is phrased as a proposal candidate.

**G1 — Seed sensitivity of the PH model is real, live, and unmeasured.**
`random_state=0` everywhere; no model was ever retrained under a different
seed (grepped: zero hits for any seed sweep). This is not pedantry for the PH
model: at 327,600 training cells it crosses sklearn's 200,000-row binning
subsample, so the bin edges — hence the trees, hence predictions 1, 2 and 8 —
depend on the seed. The gap to rank 2 is 0.0030; nobody knows whether seed
variance on our side is 0.0001 or 0.005.
*Proposal*: retrain the PH model at 5–10 seeds, score on the 4 PH
**validation** cases only (no scoring call, test-blind by construction),
report the validation-MAE spread and the per-case prediction spread at the
test features. If validation spread ≳ 0.003, the leaderboard-gap language in
`closure.html` must carry an uncertainty. **Cost: ~10–20 min wall on the
2-core cap (round-1 training was minutes), zero scoring calls.** Cheapest
high-value item here.

**G2 — No a-posteriori physicality check on any corrected field.**
The corrected `U` is a cell-wise ML output added to a solenoidal RANS field;
it does not satisfy continuity by construction and nobody has measured how
far it departs. No realizability question arises (we predict velocity, not
Reynolds stresses — stated as N/A, not as a pass), but ∇·U is checkable
today with machinery we already have (Green-Gauss operator in
`closure_mesh_recon.py`, validated to r ≥ 0.9997 on shipped gradU).
*Proposal*: compute cell-wise ∇·(U_RANS + δU) vs ∇·U_RANS on the 6 corrected
cases' meshes; report distribution shift. Test-blind (needs no ground truth).
A large divergence penalty would not change the score — the metric never sees
it — but it is exactly what a referee of the description document will ask,
and "we measured it and here is the number" beats silence. **Cost: ~1 session,
minutes of compute, zero scoring calls.**

**G3 — Baseline-RANS convergence evidence exists but is uncited, for all 8
predictions.** Every number we publish is relative to the benchmark's shipped
k-ω SST solves, and our provenance chain (otherwise meticulous — hashes,
pinned commits, scoring ledger) never once records that those solves
converged. The evidence is on disk and is good: PH `residuals.dat` (20,000
iters, ~1e-10 finals), duct `log.run` (`SIMPLE solution converged` under
explicit `residualControl`), NASA/CBFS logs (~1e-8–1e-9). It matters twice
over for predictions 3–4, where the shipped solve IS our submission.
*Proposal*: a ~100-line script parsing final residuals + iteration counts for
the 25 PH train/val, 5 ducts, CBFS, and the 8 test cases into
`closure_challenge_baseline_convergence.json`, cited from STATUS §4. Solver
logs contain no LES truth — test-blind. **Cost: <1 hr, seconds of compute,
zero scoring calls.**

**G4 — Round-4 manifest gap: the three new duct CSVs are unhashed.**
`unchanged_cases_sha256` covers the 5 copied files; the 3 files that changed
— the entire point of round 4 — have no recorded hash and no MANIFEST.json.
Anyone regenerating them cannot verify byte-identity the way rounds 1–3
allow. (This audit recorded `AR_1_Ret_360.csv` =
`c007e120…ce1d` as an interim anchor.)
*Proposal*: extend `closure_round4_duct_rescale.py`'s manifest block to hash
all 8 files + add the missing `isfinite` assert; write
`closure_challenge_submission_round4/test/MANIFEST.json`. **Cost: ~30 min,
zero scoring calls.** Should land before Katie's sign-off, since the
submission draft §5.1 points at these files.

**G5 — Gate statistical power is thin and already at its stated limit.**
Known and disclosed (C1: AUC 1.0 on n=4 with one positive ≈ 1-in-4 by luck;
4/4 on the PH test features matched it) — restated here because Part 2 shows
the gate is our sharpest differentiator, and it currently rests on 8 binary
decisions total. *Proposal*: enlarge the gate's validation set with
leave-one-out over all 25 PH cases (25 binary decisions instead of 4),
train-only refits per fold — no new data category, no scoring call. **Cost:
~1 session, minutes of compute.**

**G6 — No training-convergence curve for either GBM.** `max_iter=300` fixed;
whether the loss had plateaued (or validation error had begun rising) at 300
was never recorded. Subsumed by G1's retraining runs if staged validation
loss is logged there. **Cost: free if folded into G1.**

---

## Part 2 — the other four entrants, from their own documents

Sources tagged: **[SUB]** the entrant's own submission document in the
benchmark clone; **[PAPER]** a fetched primary publication; **[CHALLENGE]**
the challenge preprint (arXiv 2603.28884); **[LAB]** our own prior notes
(`CLOSURE_CHALLENGE_PRIOR_ART.md`, `docs/research/CLOSURE_METHODS.md`),
cited as ours, never as theirs. One naming note: the local `submissions/`
directory holds `montoya`, `reissmann`, `wang`, `wu`; the `wang/` directory
carries no description document and is most plausibly the Liu/**Wang**/Zhao/
Xiao entry's CSVs (the benchmark HEAD commit is literally "add wang
submission") — treated as unconfirmed.

### 2.1 Reissmann, Fang & Sandberg — rank 1, 0.0595

- **Method**: gene-expression-programming symbolic regression of an
  **anisotropic Reynolds-stress correction**, fitted *concurrently* with a
  differential-evolution refit of the **k–ω SST closure coefficients** under
  "a newly designed cost-function" [SUB: `reissman_info.txt`]. No paper on
  the entry exists yet ("we are currently drafting up the approach" [SUB]).
  Lineage: Weatheritt & Sandberg, *J. Comput. Phys.* 325 (2016) 22–37;
  implementation Reissmann, Fang, Ooi & Sandberg, *GPEM* 26(1):12 (2025),
  DOI 10.1007/s10710-025-09510-z, `GeneExpressionProgramming.jl`.
- **Training data** [SUB: `score_eval.ipynb`, verbatim]: "8 training cases
  in three stages: FlatPlate, SubsonicJet, High-Re Channel (LogLaw-loss),
  Periodic Hill 10595, AR_1_Ret_180, AR_3_Ret_180, AR_5_Ret_180,
  AR_10_Ret_180" — their own multi-stage set: canonical calibration flows
  plus the benchmark's duct *training* family and the Breuer hill.
- **Model form**: inside the PDE, twice (stress correction + coefficient
  set). The corrected quantities re-enter the governing equations;
  producing velocity fields from them implies a re-solve (stated as an
  inference — their two documents never explicitly say they re-ran RANS on
  the test cases, and cite **no convergence or stability evidence**).
  Point extraction via ParaView "Resample With DataSet" [SUB].
- **In-sample exposure**: none of the 8 scored cases in their stated
  training list. Nearest variants: ducts AR 1/3/5/10 at Re_τ=180 trained,
  scored ducts are AR_1/AR_3 at **Re_τ=360** and AR_14 — genuine Reynolds-
  and aspect-ratio extrapolation, the same transfer axis our Variant D
  pre-registration identified.
- **No mention** of a decline/do-no-harm gate. **No mention** of
  pre-registration. No UQ, no realizability statement, no solver-stability
  evidence in their documents.

### 2.2 Wu & Zhang — rank 2, 0.0624 (SST-QCRC)

- **Method**: "The Training of the SST-QCRC Model" [SUB:
  `submissions/wu/description_document.pdf`, read in full]. Two changes to
  Menter SST: a **fixed, untrained QCR-style quadratic Reynolds-stress
  term** (c_r = 0.3 "directly adopted... No data-driven techniques are used
  to train the parameters of the correction term") and a **learned
  multiplicative field β_CND on the ω-destruction term**, from conditioned
  field inversion (DAFoam adjoint) + PySR symbolic regression. Backing
  paper: Wu, Zhang & Zhang, *AIAA J.* 63(2):687–706 (2025),
  DOI 10.2514/1.J064416 / arXiv:2402.16355.
- **Training data**: **one flow** — CBFS (a benchmark training case):
  "the data obtained in Ref. [3] using the conditioned field inversion is
  directly used" [SUB §2]. Final learned law is three local features
  collapsed to `β_CND = max(−0.1157, 0.0058525 λ₂)·λ₂` [SUB Eq. 3].
- **Model form**: inside the PDE; the learned expression "is integrated
  back to Eq. (2)" and the modified model is **re-solved** (a-posteriori;
  results shown are solutions of the modified model).
- **In-sample exposure**: zero of the 8 scored cases; ducts and hump never
  mentioned in the document — their duct scores are genuinely zero-shot.
- **Stability**: an explicit hand-set bound — "we choose to bound the value
  of β_CND to be lower than 4 to keep the computation stable" [SUB p.2].
  No residual/convergence plots.
- **Nearest thing to a gate among all four entrants**: the shielding
  function f_d "deactivate[s] the correction term β_CND in the boundary
  layer to preserve the baseline SST model's accuracy in simple
  wall-attached flows" [SUB p.1], validated on a flat plate. That is
  **region-level, hand-designed, physics-keyed** — not a learned,
  case-level decline, and its "off" state still ships a corrected solve.
  **No mention** of pre-registration, UQ, or realizability.

### 2.3 Liu, Wang, Zhao & Xiao — rank 3, 0.0737

- **Method**: "Toward a unified data-driven turbulence model through
  multi-objective learning," arXiv:2509.17189 (accepted, *National Science
  Review*) [PAPER, read incl. Methods + Supplement]. Parallel-TBNN
  tensor-basis anisotropy (b = Σ g⁽ⁱ⁾T⁽ⁱ⁾) **and** k–ω transport
  coefficients learned **jointly**, trained a-posteriori (model-consistent)
  via regularized ensemble-Kalman updates with multi-objective
  Frank–Wolfe weighting over 9 training flows. OpenFOAM-integrated;
  every prediction is a re-solve. Note: this is a *paper*, not a
  submission document — no description document exists in the clone, and
  the paper never mentions this leaderboard.
- **Training data**: 9 cases auto-selected from a 36-case library by
  Wasserstein-distance clustering — CBFS, periodic hill α=1.0/Re 10595
  (from the same xiaoh parameterized-hills dataset our PH cases come
  from), bump, **NASA wall-mounted hump (Re 9.36×10⁵)**, S809 airfoil,
  two square ducts, a rectangular duct, round jet; sparse velocity /
  force observations. A "specialist" secondary-flow model additionally
  fine-tunes on rectangular ducts **AR = 3 and AR = 10**.
- **In-sample exposure — the audit's sharpest external finding**: per
  their own paper (main-text Table 1), **the NASA wall-mounted hump — the
  same flow as the scored `NASA_2DWMH` test case — is one of the nine
  training flows** (sparse velocity observations at three streamwise
  stations). The specialist model's AR = 3 duct is the scored geometry
  family (Re_τ match not established from the pages read). **Caveat
  stated plainly**: the paper is not the submission; whether the
  leaderboard entry retrained excluding the hump is not determinable from
  public sources. Stated as an observation from their own Table 1, not as
  an accusation.
- **Stability**: candid hand-patches — the quadratic term g⁽²⁾ "is
  explicitly set to zero to ensure numerical stability" on two hard cases
  [Supp.]. Baseline-regularization "ensures stable behavior outside this
  regime" [PAPER p.4]. **No mention** of a decline gate, pre-registration,
  predictive UQ, or eigenvalue realizability (their constraints are
  canonical-limit consistencies).

### 2.4 Montoya, Oulghelou & Cinnella — rank 4, 0.0779

- **Method**: the entry runs Oulghelou, Cherroud, Merle & Cinnella,
  "Machine-Learning-Assisted Blending of Data-Driven Turbulence Models,"
  *Flow Turbul. Combust.* (2025), DOI 10.1007/s10494-025-00661-8 =
  arXiv:2410.14431 [PAPER]. Three SBL-SpaRTA symbolic "experts" (baseline
  SST with zero correction; a jet-trained model; a separation model
  trained on PH 10595 + converging-diverging channel + CBFS) blended by a
  Random-Forest weighting field on 11 local baseline-RANS features, with
  convex weights (Σw=1). Corrections are tensor-basis b^Δ plus a
  production-like R_k term in the k/ω equations — inside the PDE, then
  "Solve the augmented RANS equations... until convergence" [PAPER,
  Alg. 2]. Attribution note: Montoya is on the leaderboard row, not the
  paper.
- **In-sample exposure**: none; the hump appears in the paper as an
  *evaluation* case only, and the challenge preprint itself notes their
  leaderboard result is the "Pretrained model... only, without fine-tuning
  on the challenge datasets" [CHALLENGE, Table 1 note] — the strongest
  no-adaptation statement of any entrant, though it comes from the
  organisers, not the entrants.
- **Structurally the closest relative to our gate**: the baseline SST is
  itself one of the experts, so where the Random Forest favours it the
  blend **locally reverts to the uncorrected baseline** — a learned,
  region-level fallback. Not case-level, and never a refusal to submit a
  correction. **No mention** of pre-registration. UQ explicitly
  sacrificed ("does not deliver estimates of the predictive uncertainty as
  naturally as the external model aggregation" [PAPER p.4]). No
  realizability statement; stability addressed structurally (additive
  correction "has the benefit of enhanced numerical stability").

---

## Part 3 — the comparison, and the honest gaps

### 3.1 Dimension by dimension

| Dimension | **Us (round 4)** | Reissmann | Wu & Zhang | Liu/Wang/Zhao/Xiao | Montoya/Oulghelou |
|---|---|---|---|---|---|
| Corrected object | **velocity field, post-hoc** (δU per cell; nothing re-enters the PDE) | anisotropy correction + SST coefficients | β field on ω-destruction + fixed QCR | TBNN anisotropy + k–ω coefficients, coupled | blended tensor-basis + R_k corrections |
| Re-solved with correction | **no — unique among the five** | yes (inferred) | yes (explicit) | yes (explicit) | yes (explicit) |
| Conservation satisfied by submitted field | **not guaranteed, never measured (G2)** | yes, by construction (RANS solution) | yes | yes | yes — their paper says so in as many words |
| Training data | benchmark suggested split only (21+4 PH; 4+1 ducts; CBFS unused) | own 8-case set incl. benchmark duct family | CBFS only | own 9-case set **incl. the scored hump** | own jet/PH/CD/CBFS set |
| Trains on a scored case | no — enforced by executable asserts + `closure_in_sample_gate.py` | no | no | **yes per their own paper** (entry-level status unverifiable) | no ("pretrained... without fine-tuning") |
| Case-level do-no-harm gate | **yes — C1, fit train-only, its "off" state submits the uncorrected field** | absent from their documents | region shield f_d (hand-designed) — not case-level | absent from their documents | baseline-as-expert local fallback — not case-level |
| Pre-registration of choices before scoring | **yes** (NASA model choice; Variant D on AR_7; R5 written and *failed by its own gate*) | absent from their documents | absent from their documents | absent from their documents | absent from their documents |
| Stability / physicality evidence | n/a for solves (nothing re-solved); **no field-physicality check (G2)** | none cited | β ≤ 4 bound | g⁽²⁾ zeroed by hand on 2 cases | additive form + convexity |
| Scoring-call ledger | **yes, 5 calls, self-imposed** | none visible (notebook scores locally) | none visible | none visible | none visible |

**On the two claims Katie asked verified by absence**: across all four
entrant documents there is **no mention of a case-level decline gate and no
mention of pre-registration** — both stated here as absences in the sources
read (two submission documents, one notebook + info file, two full papers),
not as proof about their labs' unpublished practice. The nearest relatives
are Wu's f_d shield and Montoya's baseline-expert fallback, both
region-level within a corrected solve; neither ever declines a whole case
and submits the baseline. And the uniqueness claim stays scoped exactly as
`CLOSURE_CHALLENGE_PRIOR_ART.md` §7.4 requires: unique **among the five
entries on this board**, not in the literature — ~~Ling & Templeton 2015,
Steiner et al. 2022, Buchanan et al. 2025 (RITA; co-authored by the
challenge's own authors) are established prior art for
classifier-controlled corrections~~, and our surviving distinctions are
case-level granularity, predicting the *baseline's* error, and "off"
meaning the uncorrected field *is the submission*.

**Correction 2026-08-05 — the struck clause credited two papers with a
mechanism they did not report.** The method-priority review
(`CLOSURE_METHOD_PRIORITY_REVIEW.md` §4.2, commit `d84b649f`) re-fetched Ling
& Templeton's abstract at the OSTI record and found it describes classifying
"RANS results on a point-by-point basis as having either high or low
uncertainty" — it flags; it gates, withholds and controls nothing. Wu, Wang,
Xiao & Ling 2017 likewise supplies an *a priori* confidence measure, not a
control. Grouping all four under "classifier-controlled corrections" is the
exact failure `docs/charters/LITERATURE_CHARTER.md` §7 names (attributing a
mechanism to a source that reported a correlation).
`CLOSURE_CHALLENGE_PRIOR_ART.md` §2.1 had it right; this document lost it when
it compressed the list. **The list, split:**

> Classifiers on RANS-only inputs that ***identify*** where the baseline is
> unreliable are established — **Ling & Templeton 2015** (*Phys. Fluids* 27,
> 085103) and **Wu, Wang, Xiao & Ling 2017** (*Flow Turbul. Combust.* 99, 25,
> DOI 10.1007/s10494-017-9807-0). ***Using such a classifier to control where
> a data-driven correction is fitted and applied*** is established
> separately — **Steiner, Dwight & Viré 2022** (DOI
> 10.1007/s10494-022-00346-6) and **Buchanan, Lăcătuş, West & Dwight 2025**
> (RITA, *Computers and Fluids* 305, 106899, arXiv:2504.06758; co-authored by
> the challenge's own authors).

This makes our position **more** defensible, not less: it shows we know which
paper did which thing. Nothing about our surviving distinctions changes.

### 3.2 What each method could and could not have learned

- **Ours**: a scalar-feature, tree-based post-hoc map can interpolate rich
  corrections inside a trained family (PH: −62% on the worst case) but
  provably cannot extrapolate (`Re_y` at 1.85–2.07× trained max on the two
  ducts we trail) and is structurally starved on ducts: the baseline's
  exact unidirectionality collapses 5 of 7 features to one degree of
  freedom (`closure_challenge_duct_feature_degeneracy.json`) — effective
  input dimension 3–4 where the physics is three-dimensional.
- **Reissmann**: an algebraic stress correction inside the PDE *can
  generate* Prandtl's secondary flow of the second kind and carries it
  across Reynolds number through the re-solve — exactly the two axes
  (duct anisotropy, Re transfer) where they beat us worst.
- **Wu**: a three-feature symbolic β with a fixed QCR term is the most
  parsimonious model on the board; generalization by parsimony plus
  physics-keyed shielding. QCR supplies duct secondary flow they never
  trained for.
- **Liu**: the broadest hypothesis space (full tensor basis + transport
  coefficients) — and the entry whose training set, per its own paper,
  overlaps the scored cases.
- **Montoya**: bounded by the convex hull of three experts; it cannot
  express a correction none of its experts contains, which is a safety
  property and a ceiling at once.

### 3.3 What the two entries above us do that we do not

**vs Reissmann (0.0595, gap 0.0059).** They model the missing physics
inside the equations and re-solve; we post-process a field whose duct
baseline has *exactly zero* secondary flow, and at least 76% of our duct
error is streamwise-profile error we bound but cannot recover post-hoc
(STATUS §6). The score gap lives almost entirely in the ducts (they hold
0.0387/0.0341 vs our 0.0811/0.0775 — worth ~0.011 of overall, more than the
whole 0.0059 gap) plus the hump (0.0412 vs 0.0632). They also train on the
duct family across AR 1–10 where we train AR 1–10 too — the difference is
not data, it is **model form**. Where we beat them: both `alpha_15` cases
(0.0501/0.1011 vs 0.0592/0.1339) and both declined `alpha_05` cases —
i.e., our in-family correction and our knowing-when-to-stop.

**vs Wu & Zhang (0.0624, gap 0.0030).** One training flow, a
five-constant symbolic law, and a re-solve beat our 21-case gradient-boosted
model everywhere outside the PH family (ducts 0.0455/0.0399; hump 0.0364,
best on board). What they do that we do not: correct *causes* (the ω
equation) rather than *symptoms* (the velocity field), and buy
generalization from compactness. The lab's own route to exactly this method
class — Ladder B3 discrete-adjoint field inversion on CBFS, reproducing
Wu's pipeline — is real and currently blocked on the DAFoam/PETSc GMRES
NaN/Inf failure (STATUS §7). Where we beat them: both `alpha_15` cases,
both declined `alpha_05` cases, and nominally AR_14.

**The honest headline this document must keep**: our two `alpha_05`
"board-leading" rows are the organisers' baseline, not our model
(STATUS §8.2); our only model-attributable clear leads are the two
`alpha_15` cases; AR_14's lead is 0.00003 and nominal. Every entrant above
us ships a method whose output satisfies the governing equations; ours does
not and has not measured how far it departs (G2).

### 3.4 Closing ranked list — audit gap findings as proposal candidates

Full statements and costs in §1.3; ranked order restated as the deliverable:

1. **G1** — PH-model seed sensitivity (real: 327,600 cells > 200k binning
   subsample; 3 of 8 predictions; unknown vs a 0.0030 rank-2 gap).
   ~10–20 min compute, zero scoring calls.
2. **G2** — continuity/physicality audit of the six corrected fields
   (∇·U before/after; the one dimension every other entrant gets by
   construction). ~1 session, zero scoring calls.
3. **G3** — record the shipped baselines' convergence evidence (exists on
   disk, uncited; load-bearing twice over for the two declined cases).
   <1 hr, zero scoring calls.
4. **G4** — hash the three round-4 duct CSVs + MANIFEST + isfinite assert
   (close before Katie's sign-off). ~30 min.
5. **G5** — widen the gate's statistical base from 4 to 25 held-out
   decisions (LOO over all PH cases, train-only refits). ~1 session.
6. **G6** — staged-loss curves for both GBMs (fold into G1). Free.

None requires a scoring call; none touches test ground truth; all six keep
the leakage guards armed.

