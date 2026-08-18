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

Run 2026-08-04 (`sdk/scripts/closure_ph_seed_sensitivity.py`, 181 s on the
2-core cap, zero scoring calls, guard verified armed; raw numbers in
`closure_challenge_seed_sensitivity.json`). A session-limit kill and power
cycle interrupted the *write-up*, not the run — the JSON on disk is the
completed 2026-08-04 run; results were transcribed 2026-08-05.

**Validity anchors, checked before anything else was believed**:

- Seed 0 reproduces the entry of record: validation pooled scaled MAE
  0.0876 = the round-1 recorded 0.0876, and its regenerated eval-point
  predictions match the shipped round-4 CSVs to write precision
  (max abs diff 4.8e-10 / 5.0e-10 / 5.0e-9 on the three served cases —
  identical to the round-3 manifest's own roundtrip errors). The seed-0
  member of this ensemble IS the model behind the entry, so the spread
  below is about the entry, not a lookalike.

**Measured spread across 8 seeds** (all else frozen):

| Quantity | Value |
|---|---|
| Validation per-case range (max−min): `alpha_05_10071_4048` | 0.00085 |
| `alpha_05_10071_2024` | 0.00124 |
| `alpha_15_7929_4048` (proxy for served `alpha_15_13929_4048`) | **0.00057** |
| `alpha_15_7929_2024` (proxy for served `alpha_15_13929_2024`) | **0.00052** |
| Validation pooled range | 0.00028 |
| Test-side bound `B`: `alpha_15_13929_4048` | **0.00846** |
| `alpha_15_13929_2024` | **0.00989** |
| `NASA_2DWMH` | 0.00100 |
| Overall-equivalent `S_proxy` | **0.000261** |
| Overall-equivalent `S_bound` | **0.002419** |

**Verdict against the pre-registered lines (§0.1): MATERIAL.** Two of the
three trigger conditions fire: `S_bound` = 0.0024 ≥ 0.0003, and the
single-case bounds `B` on both served `alpha_15` cases (0.0085, 0.0099)
exceed the 0.0030 whole-gap line.

**The honest reading, both halves**:

- Where truth is legitimately available (the 4 held-out validation cases),
  the *metric* is stable under seed: per-case spread 0.0005–0.0012,
  overall-equivalent ~0.00026 — a tenth of the 0.0030 gap to rank 2. That
  is the best available *estimate* of the seed effect on the score, and it
  is small. The entry gains a measured (no longer assumed) stability
  property: **estimated one-seed uncertainty on the overall ≈ 0.0003**.
- But the only *truth-free* statement about the test predictions
  themselves is the spread bound, and it is not small: across seeds the
  trees move the pointwise test predictions by 0.85–0.99% of the velocity
  scale on the two served `alpha_15` cases — per-case movement up to ~3×
  the entire gap *if it failed to cancel against the truth*. On validation
  cases that pointwise wobble demonstrably cancels to the ~0.0006 level in
  the metric; expecting the same on test is reasonable but is an
  extrapolation, not a measurement, and the pre-registered rule counts the
  bound. Tightening the bound would cost a scoring call and is not taken.
- **Consequence, executed as pre-registered**: the leaderboard-gap language
  now carries the seed qualifier in `CLOSURE_CHALLENGE_STATUS.md` §0e and
  `closure.html`. Any future retraining of the PH model should either fix
  the seed and cite this record, or average seeds and re-pre-register.
- Scope check: the duct model behind predictions 5–7 is bin-deterministic
  (41,971 < 200,000 cells; `random_state` inert by construction — audit
  §1.2 column (c)), and the two declined cases are the organisers' own
  solve; the five non-PH-model predictions therefore contribute zero seed
  variance, which is why the /8 overall-equivalent conversion is exact.

## 2. G2 — results

Run 2026-08-05 (`sdk/scripts/closure_divergence_audit.py`, 310 s on the
2-core cap, zero scoring calls, guard verified armed; all 37 rows in
`closure_challenge_divergence_audit.json`). Every regenerated test field
matched its shipped round-4 CSV before its divergence number was believed
(max abs diff 4.8e-10 to 4.9e-8, all at CSV write precision) — the numbers
below are about **the submitted fields**, not a lookalike.

**Reading the table**: `‖∇·U‖` is the volume-weighted RMS divergence
through the identical validated Green-Gauss operator for both fields; the
RANS row is therefore the **operator-consistency floor** (the solver
enforces continuity on face fluxes, not on our reconstructed cell
gradients), and the honest scale-free column is `‖∇·U‖ / ‖∇U‖_F` — the
continuity error relative to the field's own velocity-gradient magnitude.

The 8 submitted predictions (full 37-case table, including all 21 PH + 4
DUCT training and 5 validation cases with the same pattern, in the JSON):

| Case | Submitted field | ‖∇·U_RANS‖ | ‖∇·U_corr‖ | ratio | rel. RANS | rel. corr |
|---|---|---|---|---|---|---|
| `alpha_15_13929_4048` | PH-corrected | 0.0029 | 0.171 | **58.0** | 0.18% | **10.5%** |
| `alpha_15_13929_2024` | PH-corrected | 0.0032 | 0.390 | **123.6** | 0.08% | **9.7%** |
| `alpha_05_4071_4048` | declined (raw RANS) | 0.0084 | 0.0084 | 1.000 | 0.47% | 0.47% |
| `alpha_05_4071_2024` | declined (raw RANS) | 0.0144 | 0.0144 | 1.000 | 0.27% | 0.27% |
| `AR_1_Ret_360` | duct-D-corrected | 9.4e-12 | 9160 | ~1e15 (÷ machine zero) | 2.4e-17 | **2.3%** |
| `AR_3_Ret_360` | duct-D-corrected | 2.2e-11 | 9749 | ~4e14 (÷ machine zero) | 6.9e-17 | **3.1%** |
| `AR_14_Ret_180` | duct-D-corrected | 4.8e-12 | 3584 | ~7e14 (÷ machine zero) | 4.6e-17 | **3.4%** |
| `NASA_2DWMH` | PH-corrected | 7.84 | 11.97 | **1.526** | 0.43% | 0.66% |

**Verdict against the pre-registered line (§0.2): MATERIAL.** 35 of 36
model-corrected cases (train + validation + test) sit at or above ratio 2;
among the six corrected submissions, five exceed it — only `NASA_2DWMH`
(1.53) stays under.

**The honest interpretation, quantified, not editorialized**:

- **The cost is real and now has a number.** The post-hoc correction takes
  fields whose measured continuity error is at the operator floor
  (0.1–0.5% of the gradient scale on PH; machine zero on the ducts, whose
  fully-developed unidirectional RANS field is *exactly* divergence-free
  cell-wise) and returns fields violating continuity at **~10% of the
  gradient scale on the two corrected hills, 2.3–3.4% on the three
  ducts**. This is far above the operator floor, so it is the field, not
  the operator. It is the structural price of the method class the
  comparison table already named: every other entrant re-solves the
  governing equations and gets `∇·U ≈ 0` by construction; our submitted
  corrected fields do not satisfy continuity, and now the departure is
  measured instead of unmentioned.
- **The scoring metric never sees this** — nothing here changes 0.0654 —
  but a referee of the description document would ask exactly this
  question, and the answer is on the record with the sign against us.
  Per the pre-registered consequence, this is carried into the submission
  draft's disclosure alongside its §7.1 discussion.
- **The two declined cases are, again, the strongest rows** — the gate's
  "off" state ships the organisers' own solve and inherits its
  physicality untouched. The decline mechanism keeps being the most
  defensible part of the entry.
- **Why NASA is mild**: the PH-trained correction is small relative to
  NASA's own gradient scale (‖∇U‖_F ≈ 1803 s⁻¹ against the hills' ~2–5),
  so the same model that barely moved NASA's score (+0.0011) also barely
  moves its continuity error (0.43% → 0.66%). Magnitude of harm tracks
  magnitude of correction — consistent with the C6 covariate-shift
  finding, and measured here from a different direction.
- **Train/validation cases show the same 8–19% (PH) and 2–3% (duct)
  corrected-field levels**, so this is a property of the method on its
  own turf, not a test-set extrapolation artifact.

**Boundary caveat, recorded**: boundary faces carry the RANS boundary
metadata for both fields (§0.2). Since the correction is cell-centred and
boundary conditions are untouched, this is the natural completion; the
measured differences are interior-driven.
