# Closure entry — seed-stability (G1) and field-physicality (G2) audit

Evidence record, 2026-08-04. Executes findings **G1** and **G2** of the methods
audit (`CLOSURE_METHODS_COMPARISON.md`, commit `ac2f37ee`, §1.3). **TEST-BLIND
throughout: no scored-test ground truth is read, no scoring call is made, the
raising-stub scoring guard of `export_closure_submission_csvs.py` is re-armed
in every run below and proven armed before any work.** Ground truth (`U_LES`)
is read only for the 21 PH + 4 DUCT **training** cases (to refit the two
frozen models exactly as rounds 1–4 did) and the 4 PH **validation** cases
(to compute validation metrics, the same category of access rounds 1–4 used).
Test cases are opened for RANS fields and mesh only.

Companions: `closure_challenge_seed_sensitivity.json` (G1 raw numbers),
`closure_challenge_divergence_audit.json` (G2 raw numbers),
`sdk/scripts/closure_ph_seed_sensitivity.py`,
`sdk/scripts/closure_divergence_audit.py`.

---

## 0. Pre-stated thresholds — written and committed BEFORE either run

This section was committed before the first retraining or divergence number
existed, so the lines below cannot have been drawn around the results.

### 0.1 G1 — seed sensitivity of the PH model

The entry of record (round 4, overall 0.0654) trails rank 2 (Wu & Zhang,
0.0624) by **0.0030**. Three of the eight submitted predictions
(`alpha_15_13929_4048`, `alpha_15_13929_2024`, `NASA_2DWMH`) come from the
round-1 PH model, whose 327,600 training cells exceed sklearn 1.9.0's
200,000-row binning subsample, making the bin edges — hence the trees, hence
those three predictions — genuinely dependent on `random_state` (audit G1).

Protocol, fixed in advance:

- Retrain the PH model at **8 seeds** (`random_state = 0..7`; seed 0 must
  reproduce the recorded round-1 model — train pooled 0.0620 / validation
  pooled 0.0876 — or the run is invalid). Everything else frozen: same 21
  training cases, same 7 features, same hyperparameters, same venv.
- Score each seed on the **4 PH validation cases only**, exactly as the
  original pipeline validates (per-case and pooled scaled MAE, the
  benchmark's own formula reimplemented cell-wise as in round 1 — no
  harness scoring call).
- Predict each seed at the three served test cases' **RANS-derived features**
  and interpolate to the official evaluation points (coordinates only) —
  no ground truth involved.

Quantities and the materiality line, fixed in advance:

- **Validation proxies for the three served predictions**:
  `alpha_15_7929_4048` for `alpha_15_13929_4048`; `alpha_15_7929_2024` for
  `alpha_15_13929_2024` (same alpha family and grid tag, held out, never
  trained on). `NASA_2DWMH` has no family validation case (recorded in
  round 2); its proxy is (a) the pooled 4-case validation metric — a weak
  proxy, stated as such — and (b) the direct test-side prediction-spread
  bound below, which needs no truth at all.
- `R_c` = (max − min across the 8 seeds) of the proxy metric for served
  prediction `c`.
- **Test-side bound** `B_c` = max over seed pairs of
  `mean(‖U_i − U_j‖)` over the case's 1000 evaluation points divided by
  `mean(‖U_RANS‖)` at the same points. By the triangle inequality this
  bounds the seed-induced change of the official per-case score up to the
  ratio `mean(‖U_RANS‖)/mean(‖U_true‖)`, which differs from 1 by at most
  the RANS floor's own scaled MAE on that case (≤ 0.20 for every case
  here). No ground truth is read to compute it.
- **Overall-equivalent induced spread**, two estimates:
  `S_proxy = (R_4048 + R_2024 + B_NASA) / 8` and
  `S_bound = (B_4048 + B_2024 + B_NASA) / 8` (the five non-PH-model
  predictions are byte-frozen files and contribute zero seed variance).

**The line, stated before running: the finding is MATERIAL if
`S_proxy ≥ 0.0003` or `S_bound ≥ 0.0003` (10% of the 0.0030 gap to rank 2),
or if any single `R_c` or `B_c` ≥ 0.0030 (a one-case spread the size of the
whole gap is material regardless of the mean). If material, the
leaderboard-gap language in `closure.html` and the status record must carry
a seed-uncertainty qualifier. If below the line, the entry gains a defended,
measured stability property — not an assumed one.**

### 0.2 G2 — a-posteriori physicality (continuity) of the corrected fields

The submitted corrected field `U = U_RANS + δU` is a cell-wise ML output
added to a solenoidal RANS solution; nothing guarantees `∇·U ≈ 0` and
nobody has measured it (audit G2). Protocol, fixed in advance:

- Divergence operator: the **already-validated** Green-Gauss machinery of
  `sdk/scripts/closure_mesh_recon.py` (gradU validated r = 0.9997–1.0000
  against shipped fields on PH training cases; cell C/V to ~1e-13):
  `∇·U = tr(∇U)` per cell. Both fields (raw RANS, corrected) go through
  the **identical** operator, so operator discretization error cancels in
  the comparison. Boundary faces carry the RANS field's own boundary
  values for both fields (the correction is cell-centred and does not
  alter boundary conditions); this is recorded, not hidden.
- Cases: every case the two frozen models serve or were selected on —
  21 PH train + 4 PH val (PH model), 4 DUCT train + `AR_7_Ret_180` val
  (Variant D) — **plus the 8 official test cases**. Test-case inclusion is
  test-blind-legal by the guard's own definition (re-checked this session:
  the stubs block ground-truth velocity reads and scoring calls; RANS
  fields, mesh, and our own model outputs are exactly what rounds 2–4
  legitimately read), and the regenerated test fields are verified against
  the shipped round-4 submission CSVs at the evaluation points before
  being trusted. The two declined `alpha_05` cases are included with
  ratio 1 by construction (their submitted field IS the RANS field).
- Metric per case: volume-weighted RMS divergence
  `‖∇·U‖ = sqrt(Σ V_i (∇·U)_i² / Σ V_i)` for `U_RANS` and `U_corrected`,
  and the **ratio**. Context column: the RANS field's volume-weighted RMS
  velocity-gradient Frobenius norm, so the divergence numbers have a scale.

**The line, stated before running: a ratio ≥ 2 on any model-corrected case
is recorded as a material physicality cost of the method class and must be
carried into the submission draft's disclosure section; a ratio < 2 is still
reported per case, quantified, with no editorializing either way.**

---

## 1. G1 — results

*(To be filled by the seed-sensitivity run; nothing below this line existed
when §0 was committed.)*

## 2. G2 — results

*(To be filled by the divergence run; nothing below this line existed when
§0 was committed.)*
