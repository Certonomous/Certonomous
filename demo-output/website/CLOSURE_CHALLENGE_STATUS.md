# Closure Challenge — status as of 2026-08-07 (round 5 is the entry of record)

Read-only status report except for the new §0 and §0b below. All figures are
quoted from already-recorded, re-derivable artifacts; sources are cited per
section. **Updated 2026-08-04**: §0e added (round 4, 2026-07-31, overall
**0.0654**, the entry of record); §2, §3 and §5 carry dated superseded notes
rather than rewritten round-3 numbers, per this file's own convention.
**Updated 2026-08-07**: §0f added (round 5, 2026-08-07, overall **0.0566**,
the entry of record, **rank 1 of 5 scored locally at benchmark commit
`deb91557`** — a local scoring, not an official placement; we remain
unsubmitted). §0e and the round-4 columns below stand unchanged as the
superseded record.

Sources: `/home/ubuntu/closure-challenge-benchmark/README.md` (benchmark
rules + public leaderboard); `demo-output/website/closure_challenge_rans_floor.json`;
`demo-output/website/closure_challenge_trained_entry.json` (round 1);
`demo-output/website/closure_challenge_trained_entry_round2.json` (round 2);
`demo-output/website/closure_challenge_trained_entry_round3_gated.json`
(round 3, *superseded as entry of record by round 4, §0e*);
`demo-output/website/closure_challenge_trained_entry_round4_duct.json`
(round 4, **entry of record**);
`demo-output/website/closure_challenge_submission_round4/test/` (the 8
round-4 submission CSVs);
`demo-output/website/closure_challenge_duct_reynolds_transfer.json`
(the round-4 pre-registration);
`demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (§7.1);
`demo-output/website/closure_challenge_C2_error_decomposition.md`;
`demo-output/website/closure_challenge_C1_error_estimator.md`;
`demo-output/website/dafoam/ladder-b/{B1_reproduction_plans,B2_duct_baseline,B3_duct_field_inversion}.md`;
`demo-output/website/campaign/F6_closure_aligned_flows.md`;
`demo-output/website/ACTIVE_RESEARCH.md`; `docs/research/CLOSURE_METHODS.md`.

---

## 0. Round 3 — the C1 gate was applied, for the first time (new this update)

Round 2's own report (§6, Term 1) identified but deliberately withheld a
recoverable 0.0066: the trained correction is worse than doing nothing on
`alpha_05_4071_4048` and `alpha_05_4071_2024` (plus a negligible amount on
`NASA_2DWMH`). C1 (already committed, prior session) built and validated a
test-blind decline-gate for exactly this — fit and its threshold set on the
21 PH **training** cases only, checked on the 4 PH **validation** cases only
(AUC 1.0, 4/4 correct) — and explicitly did not apply it to the test set,
calling that "a separate decision not yet made."

This session made that decision: `sdk/scripts/apply_closure_ph_gate.py`
reproduces the C1 gate's coefficients and threshold byte-for-byte from
train-only data (confirmed identical: alpha=0.7499, threshold=0.1263), then
evaluates the frozen gate on the 4 official PH test cases using **only**
their RANS-derived features (no `U_LES` read for any test case to build
these features), and uses the binary output to choose, per case, between two
already-existing predictions: the round-1 corrected output or the raw-RANS
floor. DUCT and NASA_2DWMH are reproduced unchanged from round 2. **One**
new official `score()` call was made on the resulting 8-case dict — the 4th
such call this lab has made on this benchmark's test ground truth (after the
floor, round 1, and round 2).

**Result: overall 0.0741 → 0.0676** (Δ −0.0065, matching the 0.0066 predicted
in round 2 almost exactly). The gate correctly declined both `alpha_05`
cases (predicted baseline 0.0420 and 0.0034, both below the 0.1263
threshold) and correctly kept applying the correction on both `alpha_15`
cases (predicted 0.1503 and 0.1525, both above threshold) — 4/4 correct on
cases the gate had never been evaluated on before, matching its validation
performance exactly.

**A finding earned by this, not designed for it**: on both declined cases
the raw RANS floor (0.0461, 0.0719) is lower than every entry on the public
leaderboard for that case (best published 0.0569 and 0.0760 respectively).
**We now lead the public board on 5 of 8 cases**, not 3 — two of the five
by simply not having broken what RANS already got right.

**Leakage discipline, stated plainly**: the gate's parameters (feature
screening, RidgeCV alpha, standardization, final coefficients, decision
threshold) depend on zero test-case data — computed only from the 21 PH
training cases, exactly as in C1. The motivating observation that led to
building the gate came from round 2's own official scoring call (legitimate:
this lab treats an official call's outcome the same way it treats the public
leaderboard — usable to target research effort, never to fit or select a
model). The gate itself was validated for generalization on the 4 PH
validation cases, which are not test cases. Its evaluation on the 4 test
cases used only RANS/mesh-derived features, never their ground truth. No
test case's own outcome influenced its own decision, and the gate's
parameters were fixed before this run touched any test data.

**Compute**: 83 s wall time on a 2-core cap, peak RSS 356 MB (measured with
`/usr/bin/time -v`) — model-fitting and inference on already-solved fields,
no CFD solve.

Round 3 record: `demo-output/website/closure_challenge_trained_entry_round3_gated.json`.
Script: `sdk/scripts/apply_closure_ph_gate.py`.

---

## 0b. Feature-expressivity audit: is the DUCT feature set blind to secondary flow?

**One-sentence answer**: not fully blind, but two of its seven features are
*provably, always* zero on this entire flow family, and of what remains, the
component that most drives secondary-flow generation is only unreliably
predictable — so more model capacity on these same seven features is not the
fix; the fix, if there is a cheap one, is different features.

**Why this was asked, and why it does not touch Ladder B3**: Term 2 (the
duct streamwise/anisotropy deficit) is blocked on a real DAFoam/PETSc GMRES
failure, and another agent is actively working that blocker right now — not
duplicated here. Before spending another adjoint-debugging session, the
cheaper prior question is whether the *existing* feature set could ever
express the missing correction at all, even with unlimited model capacity.
Answered by projecting the 7 Pope-invariant features (I1_S2, I2_W2, I3_S3,
I4_W2S, I5_W2S2, Re_y, tke_ratio) against the true LES Reynolds-stress
anisotropy tensor on a Lumley/barycentric map, using **only the 4 DUCT
training cases** (`AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`,
`AR_10_Ret_180`) — never the DUCT validation case, never any of the 3 DUCT
test cases, no `score()` call. Script: `sdk/scripts/closure_duct_anisotropy_expressivity.py`.
Record: `demo-output/website/closure_challenge_duct_anisotropy_expressivity.json`.

**Finding 1 — a proven structural degeneracy, not a statistical one.** RANS
produces exactly zero secondary flow on every DUCT training case (streamwise
fraction of mean |U| = 1.0000 on all 4), so the RANS mean field has the form
U=(u(y,z), 0, 0). For *any* gradient of that form, `I3_S3 = tr(S_hat^3)` and
`I4_W2S = tr(W_hat^2 S_hat)` vanish identically — verified both on this run's
actual data (max |value| ~1e-14, machine epsilon) and independently over
50,000 random shear-rate pairs (exact zero, analytically). **Two of the
seven features carry zero information for the entire DUCT family, by
mathematical necessity — not fixable by more data or more model capacity.**

**Finding 2 — the strong-looking barycentric R² is mostly a red herring.**
Held-out R² (leave-one-training-case-out, 4-fold) predicting barycentric
position from the remaining 5 features reaches 0.97 on `y_b` — but `y_b`
correlates 0.9843 with wall distance (`Re_y`) alone. Near-wall turbulence
approaching the two-component limit is universal wall-bounded-flow physics,
present in every RANS/LES comparison; recovering it says nothing about the
duct's corner-driven secondary flow specifically.

**Finding 3 — the components that actually matter are weak and one is
unreliable.** Isolating the two anisotropy components directly implicated in
the secondary-flow generation mechanism (Prandtl's secondary flow of the
second kind): `b_yz` (cross-plane shear) reaches held-out R²=0.27, positive
and consistent across all 4 folds (0.16–0.36) — a real but modest signal.
`b_yy − b_zz` (normal-stress difference) reaches held-out R²=0.04, with one
fold strongly **negative** (−0.69) — not a reliable, generalizing signal.

**Consequence for where effort should go next**: this is a genuine negative
result for the current feature pipeline, stated plainly rather than
papered over. It does not redirect effort toward Ladder B3 (already in
progress elsewhere) or away from it — it explains, mechanistically, *why*
a scalar-velocity-correction model on this feature set has a structural
ceiling on the DUCT cases regardless of tuning, and points at what a
cheap feature-side fix would need to supply: information that breaks the
parallel-shear degeneracy (something RANS's own zero-secondary-flow mean
field structurally cannot provide on its own).

**Compute**: 17.5 s wall time on a 2-core cap, peak RSS 170 MB.

---

## 0c. A cross-family generalization-failure criterion

**One-sentence answer, stated in the asymmetric form it was actually
measured in (coordinator correction — this is not a symmetric criterion)**:
a model blind to a dimension (trained where two of its seven input
dimensions are algebraically forced to zero) fails on cases that need that
dimension — catastrophically, 3.9×–10.4× the baseline error, every one of
the 6 times this specific direction was tested; the analogous
purely-statistical criterion (how many input features fall outside the
training range) turned out to be a proxy for nothing but the base rate and
is rejected. **What was NOT established**: the reverse direction (a model
with real information about a dimension receiving a case where that
dimension collapses to near-zero) has only one measured instance, so no
claim is made that the criterion is symmetric. A symmetric test would need
several more probe cases whose RANS field is genuinely near-degenerate
(near-zero I3_S3/I4_W2S, i.e. duct-like) fed to the PH model specifically,
to build a comparable n≥5 sample in that direction — not yet done.

**Why this was asked, and how it stays inside the leakage rule**: round 3
showed a family-specific gate recovers real score. The general question —
what property of a case predicts, without its ground truth, that a
correction trained elsewhere will hurt — needed genuinely new evidence, not
reanalysis. Built by cross-applying the two already-fitted models (PH,
DUCT — unchanged, reproduced deterministically) to NON-TEST probe cases only:
the 4 PH validation cases, the 1 DUCT validation case (`AR_7_Ret_180`), and
the benchmark's own two single-variation, all-training cases per its README
(`CBFS`, `PH_Breuer`, i.e. `PHLL10595`). **None of the 8 official test cases
is touched** — checked by an explicit assertion in the script, not just
prose — and no `closure_challenge.score()` call is made. Ground truth is
read only for these four non-test case families, exactly the same category
of access round 1/2/C1 already use for their own train/validation scores.
Script: `sdk/scripts/closure_generalization_criterion.py`. Record:
`demo-output/website/closure_challenge_generalization_criterion.json`.
Does not touch Ladder B3.

**The proven half.** The DUCT model was trained exclusively on RANS fields
where `I3_S3` and `I4_W2S` are identically zero (§0b's algebraic result), so
by construction it has learned zero dependence on those two dimensions —
literally nothing to fall back on. Any case with non-negligible `I3_S3`/
`I4_W2S` is a genuine, provable extrapolation for that model, not a fitted
correlation. Measured: applying the DUCT model to the 4 PH validation cases,
`CBFS`, and `PH_Breuer` (6 out-of-family applications) broke catastrophically
in all 6 — corrected error 3.9×–10.4× the baseline, versus ordinary
generalization-quality variation (−0.077 to +0.054) on every instance where
the mismatch does not fire.

**Evidence it is not a proxy — the checks the coordinator asked for by
name**:
- *Not a viscosity proxy*: `CBFS` and `PH_Breuer` were each scored under
  **both** models — same case, same `nu`, only the model differs — and the
  label flips (False for PH, True for DUCT) while `nu` does not. A
  viscosity-driven proxy cannot produce that.
- *Not just "source model == DUCT"*: the DUCT model's own validation case
  (`AR_7_Ret_180`) correctly reads no-mismatch — the label tracks the
  target case's own regime relative to the model's training regime, not
  which model is asking.
- *The naive statistical analogue was tested and rejected as a proxy*: a
  "how many of 15 features fall outside the training range ≥ 3" criterion
  scored a superficially higher accuracy (0.889 vs 0.778) — but it fires on
  **9 of 9** out-of-family instances, including the one that actually
  helped (a false positive), meaning zero true negatives. Its accuracy is
  just restating the 8-of-9 base rate. This is exactly the barycentric-map
  failure mode flagged after §0b, caught and rejected on the same evidence
  standard.

**What it cannot predict, stated plainly**:
- It says nothing about the PH model's own out-of-family behavior — PH's
  training data spans a real range of `I3_S3`/`I4_W2S`, so there is no
  equivalent proof for it, only weak statistics (n=3 probe cases) with no
  criterion that survived the proxy check.
- It cannot rank or size the ordinary (non-catastrophic) generalization
  variation at all — outcomes there ranged from clearly helped (−0.077) to
  clearly hurt (+0.054) with no criterion tested that separates them; that
  remains the job of a family-specific gate like C1/round 3, not this one.
- The evidence is asymmetric by direction: 6 instances test "a model with a
  proven blind spot receives a case outside it" (all correctly flagged);
  only 1 instance tests the reverse direction ("a model with real
  information receives a degenerate-regime case," PH on `AR_7_Ret_180`,
  correctly near-neutral). One point is not a second proof.
- This has been tested on exactly two model families. Whether the principle
  ("a model has no defense against inputs that were constant in its
  training data") generalizes beyond these two specific models is not yet
  known and would need a third, independently trained model to say.
- Not applied to any test case, and no decision about applying it has been
  made — exactly the round-3 precedent: build and validate first, apply
  later as a separate, explicit decision.

**Compute**: 268 s (4.5 min) wall time on a 2-core cap, peak RSS 289 MB.

---

## 0d. What the criterion says about the 8 official test cases — a table, not a decision

Ordered by the coordinator, deliberately bounded: compute the §0c criterion
on the 8 official test cases' RANS-derived features only (no ground truth,
no `score()` call), against the model **currently applied** to each in the
round-3 gated entry. This changes nothing by itself — it is a decision
table for the coordinator to act on or not, exactly the same discipline as
round 3's own build-then-decide sequence. Script:
`sdk/scripts/closure_criterion_on_test_features.py`. Record:
`demo-output/website/closure_challenge_criterion_test_case_table.json`.

**Bottom line: the proven mechanism flags zero of the 8 cases.** All 3 duct
test cases sit comfortably inside the DUCT model's own training regime
(expected — same physical class). Both PH-corrected test cases, and both
cases the round-3 gate already declined, sit comfortably inside the PH
model's training regime. Nothing here suggests changing the current entry.

| Case | Currently applied | Flagged (proven mechanism)? | Known actual delta (round 2, legitimate) |
|---|---|---|---|
| alpha_15_13929_4048 | PH | No | −0.0819 |
| alpha_15_13929_2024 | PH | No | −0.1038 |
| alpha_05_4071_4048 | none (gate declined) | n/a — no model applied | n/a |
| alpha_05_4071_2024 | none (gate declined) | n/a — no model applied | n/a |
| AR_1_Ret_360 | DUCT | No | −0.0369 |
| AR_3_Ret_360 | DUCT | No | −0.0381 |
| AR_14_Ret_180 | DUCT | No | −0.0287 |
| NASA_2DWMH | PH | **Flagged, but see below** | +0.0011 |

**A due-diligence catch made while building this table, kept in the record
rather than quietly fixed.** The first pass used `mean_I3_S3` (the same
statistic §0c used) and got NASA_2DWMH = +2.1e8 — absurd against PH's
training range of [−4.7e-4, +3.7e-5]. Investigated rather than reported at
face value. Confirmed real (not a bug) with the more robust `p90` statistic
(matching C1's own established preference) and with a full 15-feature
domain-coverage check: **NASA_2DWMH is out of the PH model's training range
on all 15 features simultaneously**, not selectively on `I3_S3`/`I4_W2S`.
Traced to a different, real mechanism: NASA_2DWMH has a large
low-turbulence, near-freestream region where RANS `omega` stays at a
non-negligible background value while `k` collapses toward zero, and the
shared `tau = 1/(Cmu·omega)` normalization behind every one of the 5 Pope
invariants (not just I3/I4) explodes there once `k` no longer represents a
meaningful turbulence timescale relative to the mean strain rate.

**This is NOT the proven DUCT mechanism, and treating it as equivalent
evidence would overclaim.** The proven mechanism (algebraically-zero
training dimension) exists only for the DUCT model on `I3_S3`/`I4_W2S`
specifically, and in its 6 confirmed instances it predicted 3.9×–10.4×
catastrophic breakdown every time. NASA_2DWMH's global covariate-shift flag
does not fit that pattern: its already-known actual outcome (round 2's
single legitimate official call) is a **mild** +0.0011 regression, not
catastrophic. ~~**No action is available for NASA_2DWMH regardless of this
flag**: no alternative training-family model exists for it,~~ its correction
choice was pre-registered before its test score was ever seen (round 2),
and revisiting that choice now — having already seen the outcome — would
itself be exactly the test-truth-informed model selection the leakage rule
forbids.

> **PARTIAL WITHDRAWAL, 2026-08-02** (`c6-nasa-hump-the-only-last-place`).
> **"No alternative training-family model exists for it" is false and is
> withdrawn.** `CBFS13700` — the curved backward-facing step, a
> two-dimensional smooth-wall flow that separates and reattaches, which is the
> nearest flow in this benchmark to a wall-mounted hump — is shipped by the
> benchmark as **training** data, with `0/U_LES`, `0/k_LES`, `0/p_LES` and
> `0/tauij_LES`, and it is legal to fit on
> (`closure-challenge-benchmark/README.md` lines 63 to 77; and the challenge
> preprint, §2.1, verified verbatim on 2026-08-02: *"You can train on similar
> flows to the test cases"*). The pre-registered argument that picked the
> periodic-hill model
> (`sdk/scripts/train_closure_extended_correction.py` lines 27 to 40) is a
> **two-way** comparison of periodic hills against ducts. **CBFS is not named,
> not rejected and not mentioned.** The choice was defended against the worse
> of two candidates while the better third sat in the training set unused.
>
> **The rest of the sentence stands, and it is the only thing keeping the case
> shut.** What is constrained is *who* may choose between the two routes and
> *when* — anyone choosing today has seen round 2's 0.0632 — not whether a
> candidate exists. Taking the CBFS route legally requires a pre-registration
> written and frozen before anything is scored.
>
> **Nothing about the entry of record changes and no scoring call was made.**
> The verdict below — that the criterion identifies no available leakage-clean
> action *without a pre-registration first*, and that zero cases warrant a 5th
> scoring call on this evidence — survives intact. Full reasoning, both routes
> priced, neither taken: `closure_challenge_C6_hump_decision.md`. The same
> withdrawal is applied at
> `closure_challenge_criterion_test_case_table.json` (`verdict.
> statement_correction_2026_08_02`) and in the generator
> `sdk/scripts/closure_criterion_on_test_features.py`, so that the sentence is
> not left standing on a surface this one does not reach.

**Answer to the bounded question asked**: the criterion changes nothing
about the current entry. There is no case for which it identifies an
available, leakage-clean action. **Zero cases warrant a 5th official
scoring call on this evidence** — a negative result, reported as such,
costing nothing to have checked.

**Compute**: 52.9 s wall time on a 2-core cap, peak RSS 179 MB — no model
fitting at all, feature extraction on 8 cases only.

---

## 0e. Round 4 (2026-07-31) — a duct-only change; the entry of record is now 0.0654 *(superseded as entry of record by round 5, §0f, 2026-08-07)*

**Result: overall 0.0676 → 0.0654** (Δ −0.0022; full-precision
0.06543140783850523). Round 3 (§0) is superseded as the entry of record; its
numbers above stand unchanged as the record of what round 3 was.

**What changed — one family, nothing else.** Variant D replaces the
round-2/3 duct model: a Reynolds-invariant `d/d_max` feature and a
velocity-scale-normalised target (`(U_LES − U_RANS) / mean|U_RANS|` per
case, 8 features, 41,971 training cells), trained on the 4 DUCT training
cases (`AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`, `AR_10_Ret_180`) and
**pre-registered** on the benchmark's own suggested duct validation case
`AR_7_Ret_180` (`closure_challenge_duct_reynolds_transfer.json`, committed
before any test score for it existed — no test outcome influenced the
selection). This is the fix aimed at the mechanism §7.1 of the submission
draft identified when it corrected the published duct diagnosis: `I3_S3`/
`I4_W2S` are algebraically zero on *every* duct including the one we win, so
they discriminate nothing; what discriminates is that `Re_y` reaches 1.85×
and 2.07× its trained maximum on the two ducts we were losing (0.90× on the
one we win), and a gradient-boosted tree cannot extrapolate.

**The five non-duct predictions are byte-identical to round 3**, copied, not
regenerated, and SHA-256-verified against the entry manifest (all five
hashes recorded in `closure_challenge_trained_entry_round4_duct.json`,
`unchanged_cases_sha256`, and re-verified against the CSVs on disk while
writing this section). The entire delta is attributable to the duct family;
the round-3 gate's behaviour is untouched.

**Per-case movement** (round 3 → round 4):

| Case | Round 3 | Round 4 | Δ | Board rank |
|---|---|---|---|---|
| `AR_1_Ret_360` | 0.0919 | **0.0811** | −0.0108 | 5 of 5 → 3 of 5 |
| `AR_3_Ret_360` | 0.0862 | **0.0775** | −0.0087 | 4 of 5 → 3 of 5 |
| `AR_14_Ret_180` | 0.0303 | **0.0325** | **+0.0022** | 1 of 5 → 1 of 5, margin collapsed |

**The `AR_14_Ret_180` regression is deliberately NOT reverted**, for the
same reason the NASA hump's +0.0011 was not reverted in round 2/3: choosing
per-case between two models *after* seeing their per-case test scores is
selection on test outcomes — exactly what the benchmark's one strict rule
exists to prevent. Variant D was frozen on validation evidence and applied
to all three ducts or none. It was applied to all three.

**Margin warning, stated so it cannot be misquoted**: `AR_14_Ret_180`'s
best-on-board lead over Reissmann collapsed from 0.0022 to **0.00003** (ours
0.0324698 against the published four-decimal 0.0325). That is a nominal
lead, not a meaningful one, and it must not be reported as a comfortable
win.

**Sign-pattern check**: the pre-registered diagnosis predicted improvement
concentrated on the two cases where `Re_y` leaves the trained range and
little or none where it does not. Measured: −0.0108 and −0.0087 on
`AR_1_Ret_360` and `AR_3_Ret_360`, +0.0022 on `AR_14_Ret_180` — the sign
pattern matches on all three.

**Standings** (public board re-scored locally at benchmark commit
`deb91557`; all four entrants reproduce their published values exactly):
**rank 3 of 5**, gap to rank 2 (Wu & Zhang, 0.0624) cut **0.0052 → 0.0030**.
Best-on-board count **5 of 8, unchanged** (AR_14 now nominally, per the
warning above). We are no longer last on any duct; last on the board only on
`NASA_2DWMH` (0.0632 vs best 0.0364).

**Seed-stability qualifier (added 2026-08-05, audit finding G1 — the
pre-registered consequence of a material finding)**: the PH model behind 3
of the 8 predictions was trained at a single seed, and at 327,600 training
cells its histogram bins are seed-dependent (sklearn 1.9.0 subsamples
200,000 rows for binning). Retraining at 8 seeds, test-blind: the
validation-proxied overall-equivalent seed spread is **~0.0003**, and a
truth-free prediction-spread bound at the test points cannot rule out
per-case movement up to ~0.0099 (overall-equivalent **0.0024**) without a
scoring call — i.e. the one-seed uncertainty on 0.0654 is an estimated
tenth of, and cannot be *bounded* tighter than about, the 0.0030 gap to
rank 2. The gap language above therefore carries this qualifier. Full
record: `closure_challenge_stability_physicality_audit.md`,
`closure_challenge_seed_sensitivity.json`.

**Scoring-call ledger**: this was **1** new official scoring call — the
**5th** cumulative distinct prediction set scored (after the floor, rounds
1, 2 and 3; see §5's superseded note). The ledger is a self-imposed
discipline: the benchmark imposes **no** scoring-call limit and instructs
submitters to preview their score. §0d's verdict — that zero cases warranted
a 5th call *on the criterion's evidence* — is not contradicted: the 5th call
was made on new, different evidence (the §7.1 `Re_y`-extrapolation diagnosis
and the pre-registered Variant D), not on §0d's table.

**Provenance**: entry of record
`demo-output/website/closure_challenge_trained_entry_round4_duct.json`
(committed `4c2f3562`); submission CSVs
`demo-output/website/closure_challenge_submission_round4/test/` (8 files);
script `sdk/scripts/closure_round4_duct_rescale.py`; pre-registration
`demo-output/website/closure_challenge_duct_reynolds_transfer.json`; full
disclosure discussion `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §7.1; board
entry `demo-output/website/ACTIVE_RESEARCH.md`, Ladder C (commit
`ede04f5f`).

---

## 0f. Round 5 (2026-08-07) — the untrained QCR term takes the ducts; the entry of record is now 0.0566, rank 1 scored locally

**One sentence**: replacing the round-4 ML duct correction with a converged
forward solve of the untrained QCR2000 constitutive term (`kOmegaSSTQCR`,
`Ccr1 = 0.3`, nothing fitted to anything) on the three test ducts — all
other five CSVs byte-identical to round 4 — moved the overall **0.0654 →
0.0566** (−0.0088), which is **below Reissmann's published 0.059525**:
**rank 1 of 5, scored locally at benchmark commit `deb91557`**, dated
2026-08-07, not an official leaderboard placement; we remain unsubmitted.

**The pre-registration was honoured to the letter.** Accept criterion,
expectation band and the AR_14 risk statement were all frozen in
`campaign/R5_PREREGISTRATION.md` (commit `e865076b`) before the call; the
all-or-none application rule was frozen earlier still
(`campaign/R5_RULE_FREEZE.md`, commit `0bade54a`, before the first
validation iteration existed) and passed ALL on the validation duct
(`campaign/R5_validation_AR7.json`: ratio 0.4770 ≤ 0.70, r 0.9284 ≥ 0.85,
both arms converged on `residualControl`).

**Independent pre-score verification** (run fresh by the scoring agent, not
trusted from the producing session): (a) the 5 unchanged CSVs SHA-256-match
the round-4 manifest; (b) all 8 CSVs are 1000×3 finite; (c)
`closure_round5_points_order_check.py` re-run fresh — ordering verified, max
row-wise deviation 4.9e-8; (d) the pre-registration's §3 hash table matches
the bytes on disk for all 8 files. All four checks passed before the call.

**The one call** (the 6th cumulative — see ledger below) through the
benchmark's own unmodified scorer (eval package commit `1c4e22c8`, the
identical local-scoring path rounds 1–4 used):

| Case | Floor | Round 4 | **Round 5** | Δ | Board rank (at `deb91557`) |
|---|---|---|---|---|---|
| alpha_15_13929_4048 | 0.1320 | 0.0501 | **0.0501** (unchanged) | 0 | **1 of 5** |
| alpha_15_13929_2024 | 0.2049 | 0.1011 | **0.1011** (unchanged) | 0 | **1 of 5** |
| alpha_05_4071_4048 | 0.0461 | 0.0461 | **0.0461** (unchanged) | 0 | **1 of 5** |
| alpha_05_4071_2024 | 0.0719 | 0.0719 | **0.0719** (unchanged) | 0 | **1 of 5** |
| AR_1_Ret_360 | 0.1288 | 0.0811 | **0.0455** | **−0.0356** | 2 of 5 nominally (0.045470 vs Wu & Zhang's published 0.0455 — a tie at published precision) |
| AR_3_Ret_360 | 0.1243 | 0.0775 | **0.0400** | **−0.0375** | 3 of 5 nominally (0.039982 vs Wu & Zhang's published 0.0399) |
| AR_14_Ret_180 | 0.0590 | 0.0325 | **0.0353** | **+0.0029** | 3 of 5 — **the nominal best-on-board tie is lost** (see below) |
| NASA_2DWMH | 0.0621 | 0.0632 | **0.0632** (unchanged) | 0 | 5 of 5 (unchanged, still our only last-place case) |
| **OVERALL** | 0.1036 | 0.0654 | **0.0566** (0.056647) | **−0.0088** | **1 of 5, scored locally** |

The five unchanged cases scored **identically** to round 4, as their
byte-identity requires; the entire delta is the duct family.

**Verdict, mechanically, per the pre-registered criterion**: 0.056647 <
0.065438 → **ACCEPT. Round 5 is the entry of record**; round 4 is
superseded. The result landed *below* the pre-stated expectation band
(0.059–0.0666) — the campaign's central arithmetic ("matching rank 2's duct
scores gives ≈ 0.056288") was nearly exact at 0.056647, and the band itself
was mis-centred pessimistic. Recorded, not celebrated.

**The AR_14 risk statement, scored against its outcome**: the
pre-registration said, before the call, that round 4's 0.00003-level
best-on-board tie on `AR_14_Ret_180` was put at risk and the possible loss
accepted in writing. **The risk materialised**: AR_14 regressed 0.0324698 →
0.0353386 (+0.0029), the tie with Reissmann (published 0.0325) is lost, and
the case falls to 3 of 5 (behind Reissmann and Wu & Zhang's 0.0350).
Best-on-board count drops **5 of 8 → 4 of 8**. Per the pre-registration's
own terms the regression is reported exactly as the round-2 NASA regression
was — **not reverted**: a post-hoc revert of any single duct after seeing
its score would be per-case selection on test outcomes. The bundle was
judged as a bundle, and the bundle wins by 12× (−0.0731 combined on the two
Ret_360 ducts against +0.0029 on AR_14). The pre-stated risk-side signal
(AR_10's weakest training ratio, AR_14 extending that trend axis) pointed
the right way: AR_14 is the one duct QCR made worse.

**Standings** (every number quoted from the benchmark README at commit
`deb91557`; ours scored locally through the unmodified eval package at
`1c4e22c8`):

| Rank | Entry | Overall | alpha_15 _4048 | alpha_15 _2024 | alpha_05 _4048 | alpha_05 _2024 | AR_1 | AR_3 | AR_14 | NASA |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **ours, round 5 (UNSUBMITTED, scored locally)** | **0.0566** | **0.0501** | **0.1011** | **0.0461** | **0.0719** | 0.0455 | 0.0400 | 0.0353 | 0.0632 |
| 2 | Reissmann, Fang, and Sandberg | 0.0595 | 0.0592 | 0.1339 | 0.0606 | 0.0760 | 0.0387 | 0.0341 | 0.0325 | 0.0412 |
| 3 | Wu and Zhang | 0.0624 | 0.0813 | 0.1195 | 0.0569 | 0.0848 | 0.0455 | 0.0399 | 0.0350 | 0.0364 |
| 4 | Liu, Wang, Zhao, and Xiao | 0.0737 | 0.0600 | 0.1308 | 0.0613 | 0.0769 | 0.0875 | 0.0805 | 0.0548 | 0.0377 |
| 5 | Montoya, Oulghelou, and Cinnella | 0.0779 | 0.0680 | 0.1364 | 0.0591 | 0.0882 | 0.0895 | 0.0866 | 0.0487 | 0.0464 |

**RANK 1, stated plainly and with its caveat in the same breath**: as of
benchmark commit `deb91557`, scored locally on 2026-08-07 through the
benchmark's own unmodified scorer, our round-5 entry's 0.056647 is the best
overall number on the board, 0.002878 below Reissmann's published 0.059525.
This is a **local scoring, not an official leaderboard placement** — nothing
has been submitted, and if the steward's own scoring differs from ours, the
steward's number is the number.

**Rank-1 companion (MANDATORY, 2026-08-10 — chief ruling).** Any statement of
rank 1 or of the 0.056647 headline, on any surface, carries these four clauses.
**P(rank 1) = 68%** — a case-level bootstrap over the eight scored cases puts the
probability that this ordering survives a comparable set of cases at 68%, and an
eight-case sample cannot pin it tighter than 2–100% at 95%. **The leads over
Reissmann and Wu & Zhang are not statistically decided** (paired per-case
differences t = −0.50 and t = −0.95, against a per-case dispersion five times the
0.002878 margin); the leads over Liu and Montoya are (98.7%, 99.8%). **The
standing is two cases wide** — delete `alpha_15_13929_2024` and the point ranking
falls to rank 2 (P(rank 1) 38%); delete `NASA_2DWMH` and P(rank 1) rises to 91%.
**`AR_1_Ret_360` and `AR_3_Ret_360` are ties below published precision** (0.00003
and 0.00008) and are not per-case wins or losses. Source:
`campaign/PROBABILITY_OF_RANK_2026-08-10.md` — SUPERSEDED 2026-08-10 — the internal-only restriction was WITHDRAWN by chief ruling; the 68% figure
now TRAVELS with the entry, and may never appear without its interval (2-100% at 95%) and the not-decided pairs.

**Seed qualifier on that margin (added 2026-08-07, family supervision
review F1 — the §0e qualifier, carried forward because the three
seed-dependent predictions ship in round 5 byte-identical)**: the PH model
behind `alpha_15_13929_4048`, `alpha_15_13929_2024` and `NASA_2DWMH` was
trained at a single seed, and the truth-free seed-spread bound on the
overall is **0.0024** (estimated effect ~0.0003; bound not tightenable
without a scoring call — `closure_challenge_stability_physicality_audit.md`
§1). **0.0024 is comparable to the 0.002878 rank-1 margin, and the rank-1
reading carries that uncertainty**; the three duct predictions contribute
zero seed variance (nothing in them was trained at all).

**A measured consistency check, not designed for**: the rank-3 entry (Wu &
Zhang) runs SST-QCRC, which carries the same untrained QCR2000 term. Our
three QCR duct scores land within 0.0004 of theirs on all three ducts
(0.0455/0.0455, 0.0400/0.0399, 0.0353/0.0350) — independent solves, same
constitutive term, same answer. The duct signal is the QCR term itself.

**What the result confirms**: the route's claim was structural — an
untrained in-PDE term has no training range, so round 4's demonstrated
`Re_y`-extrapolation failure cannot recur by the same mechanism.
Improvement concentrated exactly where that mechanism said it would: the two
Ret_360 ducts (−0.0356, −0.0375), with a small loss where round 4 was
already nearly optimal (+0.0029 on AR_14). Also closed here: audit finding
G2 for the duct family — the submitted duct fields now come from a converged
SIMPLE solve (rms ∇·U cut 27–63× against the fields they replace;
pre-registration §6).

**Scoring-call ledger**: this was **1** new official scoring call — the
**6th** cumulative distinct prediction set scored (floor, rounds 1–5). The
ledger is a self-imposed discipline: the benchmark imposes **no**
scoring-call limit and instructs submitters to preview their score. The call
was made by the supervisor's designated scoring agent, as the
pre-registration reserved.

**Compute**: solver total 37.0 core-min measured against the item's 95
core-min budget (per-arm ledger, pre-registration §7); the scoring itself
ran seconds at a 2-core cap with no solver call.

**Provenance**: entry of record
`demo-output/website/closure_challenge_round5_qcr.json`; submission CSVs +
manifest `demo-output/website/closure_challenge_submission_round5/`
(8 files, all hashes recorded and cross-asserted); pre-registration
`campaign/R5_PREREGISTRATION.md` (@ `e865076b`); rule freeze
`campaign/R5_RULE_FREEZE.md` (@ `0bade54a`); validation record
`campaign/R5_validation_AR7.json`; forward-solve machine record
`closure_challenge_round5_qcr_forward.json`; solver scripts
`sdk/scripts/closure_round5_qcr_forward.py`,
`sdk/scripts/closure_round5_points_order_check.py`; run tree
`/home/ubuntu/certonomous-runs/w3-qcr-rank1/`.

---

## 1. The metric, precisely

- **Per-case score**: scaled MAE = `mean(||U_pred − U_true||)` over the
  case's **1000 fixed evaluation points**, divided by `mean(||U_true||)`.
  Source: `closure_challenge/eval.py`, `evaluate_individual_case()`.
- **Overall score**: the plain (unweighted) mean of the 8 per-case scaled
  MAE values. Lower is better. Source: `closure_challenge/eval.py`, `score()`.
- Scoring is done exclusively through the benchmark's own unmodified scorer
  (`closure_challenge.score()`/`evaluate_by_case()`) — this project never
  reimplements the metric.

## 2. All 8 test cases — floor, our score, rank-2, and best on the board

> **Superseded 2026-08-07, see §0f.** The entry of record is now **round 5:
> overall 0.0566**, and the three duct rows and both "lead the board"
> columns below have moved (AR_1 0.0811 → 0.0455, AR_3 0.0775 → 0.0400,
> AR_14 0.0325 → 0.0353 with its nominal best-on-board tie lost;
> best-on-board 5 of 8 → 4 of 8). §0f carries the full per-case and
> standings tables at benchmark commit `deb91557`. The table below stands
> unchanged as the round-3/round-4 record.

*(Round-4 column added 2026-08-04; the round-3 column stands unchanged as
the superseded record. The five non-duct rows are byte-identical between the
two rounds — §0e.)*

| Case | RANS-identity floor | Our score (round 3, gated) | **Our score (round 4, entry of record)** | Rank-2 (Wu & Zhang, 0.0624) | Best anywhere on leaderboard | We lead the board? |
|---|---|---|---|---|---|---|
| alpha_15_13929_4048 | 0.1320 | 0.0501 | **0.0501** (unchanged) | 0.0813 | 0.0592 (Reissmann) | **YES** |
| alpha_15_13929_2024 | 0.2049 | 0.1011 | **0.1011** (unchanged) | 0.1195 | 0.1195 (Wu & Zhang) | **YES** |
| alpha_05_4071_4048 | 0.0461 | 0.0461 (gate: raw RANS) | **0.0461** (unchanged) | 0.0569 | 0.0569 (Wu & Zhang) | **YES** |
| alpha_05_4071_2024 | 0.0719 | 0.0719 (gate: raw RANS) | **0.0719** (unchanged) | 0.0848 | 0.0760 (Reissmann) | **YES** |
| AR_1_Ret_360 | 0.1288 | 0.0919 | **0.0811** | 0.0455 | 0.0387 (Reissmann) | no (3 of 5, was 5 of 5) |
| AR_3_Ret_360 | 0.1243 | 0.0862 | **0.0775** | 0.0399 | 0.0341 (Reissmann) | no (3 of 5, was 4 of 5) |
| AR_14_Ret_180 | 0.0590 | 0.0303 | **0.0325** (regressed; not reverted, §0e) | 0.0350 | 0.0325 (Reissmann) | **YES — by 0.00003, nominal only (§0e)** |
| NASA_2DWMH | 0.0621 | 0.0632 | **0.0632** (unchanged) | 0.0364 | 0.0364 (Wu & Zhang) | no |

**We hold the best score on the entire public leaderboard on 5 of 8 cases**:
both `alpha_15_13929` cases, both `alpha_05_4071` cases (now that the gate
withholds the correction and reports raw RANS, which itself beats every
published entry there), and `AR_14_Ret_180` — the last of these now by a
0.00003 margin that must not be reported as a comfortable win (§0e).

Full public leaderboard (`closure-challenge-benchmark/README.md`; round-5
row added 2026-08-07 per §0f — ours is a local scoring, not an official
placement):

| Rank | Authors | Overall |
|---|---|---|
| — | **ours (unsubmitted, round 5, entry of record — locally rank 1, §0f)** | **0.0566** |
| 1 | Reissmann, Fang, and Sandberg | 0.0595 |
| 2 | Wu and Zhang | 0.0624 |
| — | ours (unsubmitted, round 4, superseded 2026-08-07) | 0.0654 |
| — | ours (unsubmitted, round 3, superseded) | 0.0676 |
| 3 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| 4 | Montoya, Oulghelou, and Cinnella | 0.0779 |

## 3. Our overall number and position

> **Superseded again 2026-08-07, see §0f.** The entry of record is now
> **round 5: overall 0.0566** (`closure_challenge_round5_qcr.json`),
> **rank 1 of 5 scored locally at benchmark commit `deb91557`** — 0.002878
> below Reissmann's published 0.059525. Still unsubmitted; local scoring,
> not an official placement. The notes below stand as the superseded
> round-3/round-4 record.

> **Superseded 2026-07-31 (recorded 2026-08-04), see §0e.** The entry of
> record is now **round 4: overall 0.0654**
> (`closure_challenge_trained_entry_round4_duct.json`,
> `official_test_harness_result.round4_overall`). Against the floor:
> −0.0382 (36.9% below 0.1036). Against the board: still between rank 2
> (0.0624, gap 0.0030) and rank 3 (0.0737, better by −0.0083); rank 3 of 5;
> still unsubmitted. The bullets below are the round-3 record, kept
> unchanged.

- **Overall: 0.0676** (`closure_challenge_trained_entry_round3_gated.json`,
  `official_test_harness_result.round3_gated_overall`).
- RANS-identity floor: **0.1036**. We beat it by **−0.0360** (34.7% below).
- Docket-recorded rank-4 target (Montoya, Oulghelou, Cinnella): **0.0779**.
  We beat it by **−0.0103**.
- Against the full public board: we now sit **between rank 2 (0.0624) and
  rank 3 (0.0737)** — genuinely better than rank 3 by −0.0061, not merely
  tied with it as round 2 was.
- We are **unsubmitted** — this is our internally measured position against
  the public board, not an official ranking. No entry has been sent to the
  benchmark steward.

## 4. How each number was obtained

**Method class, stated precisely**: our correction is a **post-hoc velocity
field correction**, target `delta_U = U_LES − U_RANS` per mesh cell, applied
once to an already-converged RANS field as a final post-processing step. It
is **not** a modification to the turbulence model — nothing re-enters the
governing PDE and nothing is re-solved with the correction folded in. In the
Duraisamy–Iaccarino–Xiao taxonomy this is the "correct the answer" family,
structurally distinct from FIML/TBNN/SpaRTA/eigenvalue-perturbation, all of
which correct something inside the equations before re-solving
(`docs/research/CLOSURE_METHODS.md`).

**Correction, 2026-08-05 — the taxonomy and the family both get their
citations.** The paragraph above named a taxonomy with no reference and placed
our method in a family with no prior work cited for it, which the
method-priority review (`CLOSURE_METHOD_PRIORITY_REVIEW.md` §4.1, commit
`d84b649f`) names as origination by omission. Both are paid here at their
honest tiers, and neither retracts anything above:

- **The taxonomy**: Duraisamy, Iaccarino & Xiao, *Turbulence Modeling in the
  Age of Data*, **Annu. Rev. Fluid Mech. 51 (2019) 357–377**. **[METADATA
  ONLY — not read in this lab.]** The phrase "correct the answer" is
  therefore *our* paraphrase of the family, carried from
  `docs/research/CLOSURE_METHODS.md`, and is not quoted from the review.
- **The family**: Hanna, Dinh, Youngblood & Bolotnov, *Coarse-Grid
  Computational Fluid Dynamic (CG-CFD) Error Prediction using Machine
  Learning*, **arXiv:1710.09105 (2017)**; journal version *Progress in
  Nuclear Energy* **118** (2019) 103140, DOI 10.1016/j.pnucene.2019.103140
  (journal record **[METADATA ONLY]**). **[READ IN FULL, 2026-08-05** — arXiv
  text fetched and held at
  `docs/papers/hanna_dinh_youngblood_bolotnov_1710.09105.pdf`.**]** A surrogate
  trained on high-fidelity data predicts a cheap solve's *local error* from
  that same solve's own *local features* and adds it back to the variable of
  interest; nothing is re-solved. That is our architecture with the error
  source swapped. **The delta, stated so it cannot be over-read**: their cheap
  solve is a coarse-grid *no-model* Navier–Stokes solve of a lid-driven cubic
  cavity, their features are the cell Reynolds number plus scaled first and
  second velocity derivatives (37 in all — grid-resolution quantities, not
  physics invariants), and the error they correct is **grid-coarsening
  (discretisation) error**, tested across unseen Reynolds numbers and grid
  sizes. Ours is a converged k-ω SST solve corrected for **closure error** on
  separated and secondary flows, on Pope-invariant features. Their §4.3 open
  issues state, in their own words, that velocity components are "corrected
  separately, without enforcing conservation and Galilean invariance" — the
  founding CFD paper of this class names the physicality gap our own G2 audit
  later measured on us (`closure_challenge_stability_physicality_audit.md`
  §2). It explains the cost; it does not excuse it.
- **The statistical lineage**: Kennedy & O'Hagan, *Bayesian Calibration of
  Computer Models*, **J. R. Statist. Soc. B 63(3) (2001) 425–464**.
  **[METADATA ONLY — not read in this lab; nothing is quoted from it.]** Cited
  only for the shape of the idea: add a learned discrepancy term to a
  simulator's output rather than change the simulator.

**What survives, and it is the stronger statement**: the review's sweep of the
data-driven RANS-closure literature (27 searches, 13 counted negatives) found
*every* located correction that produces a velocity field re-enters the
equations and re-solves. No other post-hoc **velocity-field** correction was
located in turbulence closure. The class is not ours; the application here is.

**And one prior argues *for* the target we chose**: Wu, Xiao, Sun & Wang,
*RANS equations with explicit data-driven Reynolds stress closure can be
ill-conditioned*, **J. Fluid Mech. 869 (2019) 553–586**, arXiv:1803.05581.
**[ABSTRACT READ.]** Propagating a learned stress correction through the RANS
equations is a published conditioning hazard — the arXiv record's own summary
gives stress errors below 0.5% amplifying to velocity errors up to 35%, quoted
at that tier and not read off the paper's tables — which correcting velocity
directly sidesteps. It defends the choice of target; it says nothing about our
continuity gap (G2) and must not be used to soften it.

- **Features (7, per cell)**: Pope's 5 scalar invariants of the normalized
  strain/rotation tensors (`I1_S2`, `I2_W2`, `I3_S3`, `I4_W2S`, `I5_W2S2`), a
  wall-distance turbulent Reynolds number `Re_y`, and a turbulent/mean-KE
  ratio `tke_ratio`.
- **Model class**: `HistGradientBoostingRegressor` × 3 (one per velocity
  component), `max_iter=300, max_depth=6, learning_rate=0.05`.

**Round 1** (`closure_challenge_trained_entry.json`, overall **0.0869**):
- Trained on 21 periodic-hill (PH) cases, validated on 4 held-out PH cases,
  applied to the 4 official PH test cases.
- **Corrected**: the 4 PH test cases only.
- **Passed through unmodified raw RANS** (identical to the floor): all 4
  non-PH test cases (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`,
  `NASA_2DWMH`) — because the benchmark does not ship `gradU`/`walldist` in
  solved time directories for DUCT/CBFS, and reconstructing those fields was
  out of scope for round 1.

**What unlocked round 2** (`closure_challenge_trained_entry_round2.json`,
overall **0.0741**, delta vs round 1 **−0.0128**):
- A new **mesh-reconstructed `gradU`/`walldist` feature pipeline** (Green-Gauss
  `gradU` from mesh + RANS `U` + BCs; `walldist` via nearest wall-patch-face
  centre), validated against shipped fields on **PH training cases only**:
  cell centres/volumes vs. shipped `C`/`V` — PASS (max abs err ~1e-13/1e-22);
  `gradU` vs. shipped `gradU` — PASS (pooled relative Frobenius error
  0.0012–0.0029, Pearson r 0.9997–1.0000, on 3 different PH training cases);
  `walldist` vs. shipped — PASS (r 1.0000, mean rel. error <0.1%).
- **Corrected** with this new pipeline:
  - DUCT (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`) — a **new,
    DUCT-specific model**, trained on `AR_1/3/5/10_Ret_180`, validated on
    `AR_7_Ret_180` (held out).
  - `NASA_2DWMH` — corrected using the **existing round-1 PH-trained model**
    (pre-registered choice, made before test scoring; no matching-family
    training data exists for NASA_2DWMH in this benchmark release).
- `NASA_2DWMH` **regressed slightly** under this model (0.0621 → 0.0632,
  +0.0011 worse) — reported honestly, not reverted, because reverting after
  seeing the per-case result would itself be a second, test-truth-informed
  scoring decision, which the leakage rule forbids.

## 4b. Provenance of the shipped baseline solves (added 2026-08-05, audit finding G3)

Every number in this file is measured relative to the benchmark's shipped
k-ω SST solves, and until this section the provenance chain (hashes, pinned
commits, scoring ledger) never once cited the evidence that those solves
converged. The evidence exists on disk in the benchmark clone (`deb91557`)
and was sampled directly for this section; it matters **twice over for the
two declined `alpha_05` cases, whose submitted field IS the shipped solve** —
their baseline's convergence record is the entire convergence story of those
two predictions.

- **Periodic hills (all 29 `Parm_PH_29` cases, incl. the 4 official test
  cases)**: `<case>/postProcessing/residuals/0/residuals.dat`, 20,000
  iterations each. Final residuals for the 4 test cases (iteration 20000,
  read 2026-08-04):
  `alpha_15_13929_4048` Ux 2.6e-10, Uy 8.4e-10, p 1.0e-6, k 8.3e-10, ω 7.4e-10;
  `alpha_15_13929_2024` Ux 1.1e-10, Uy 9.7e-10, p 2.3e-7, k 9.7e-10, ω 7.4e-10;
  `alpha_05_4071_4048` Ux 1.0e-9, Uy 6.2e-9, p 2.9e-6, k 1.2e-9, ω 8.1e-10;
  `alpha_05_4071_2024` Ux 3.5e-10, Uy 1.7e-9, p 8.5e-7, k 9.3e-10, ω 4.5e-10.
  A sweep of all 29 cases' final lines (2026-08-05) shows the same pattern
  on **28 of 29**: iteration 20000, U/k/ω finals ~1e-9 to 1e-10 throughout,
  worst p final 2.9e-6 (which is `alpha_05_4071_4048` itself). **The one
  exception is honestly recorded**: `alpha_075` (a training case) ships a
  `residuals.dat` truncated at iteration 76 (O(0.2–0.8) residuals at the
  truncation point) alongside a solved `20000/` directory and no solver
  log — its convergence is plausible but *not evidenced* by the shipped
  residual file. It is 1 of 21 training cases and serves no prediction
  directly.
- **Ducts (3 test cases)**: `data/DUCT/<case>/log.run` terminates with
  `SIMPLE solution converged in 405 / 1540 / 7009 iterations`
  (`AR_1_Ret_360` / `AR_3_Ret_360` / `AR_14_Ret_180`) under an explicit
  `residualControl` (k 5e-6, ω 1e-10; `system/fvSolution`). Last-iteration
  Ux initial residuals: 1.8e-6, 5.3e-6, 7.8e-6. **The O(0.4)–O(0.7)
  last-iteration Uy/Uz initial residuals are a normalization artifact, not
  divergence**: the duct RANS transverse velocity is machine zero
  (max |Uy| = 2.1e-15, max |Uz| = 2.7e-15 m/s on `AR_1_Ret_360` against
  Ux up to 108 m/s, verified 2026-08-04 from the solved `405/U` field —
  the linear Boussinesq closure produces exactly zero secondary flow, §6
  Term 2), and OpenFOAM's per-field residual normalization is meaningless
  on a ~1e-15 field. Recorded here, per the methods audit, so nobody later
  mistakes those lines for a divergent solve. The 4 duct training cases and
  the `AR_7_Ret_180` validation case carry the same
  `SIMPLE solution converged` line in their own `log.run`.
- **NASA_2DWMH**: `data/NASA_2DWMH/log.run`, final iteration (Time = 2000)
  initial residuals Ux 1.7e-8, Uz 3.3e-8, p 3.0e-8, ω 2.4e-10, k 4.4e-8.

Source of the finding: `CLOSURE_METHODS_COMPARISON.md` (commit `ac2f37ee`),
Part 1 column (b) and finding G3. Companion stability/physicality evidence:
`closure_challenge_stability_physicality_audit.md`.

## 5. Validation and leakage guards actually in place

- **Train/val/test disjointness** checked and recorded explicitly for both
  the PH split (round 1) and the DUCT split (round 2): `train_val_test_disjoint: true`.
- **NASA_2DWMH model choice pre-registered** before the round-2 test scoring
  call (`nasa_2dwmh_model_choice_preregistered_before_test_scoring: true`) —
  chosen because no other option existed, not selected by trying alternatives
  against test scores.
- **Mesh-reconstruction validation was performed exclusively on training-family
  cases** (PH training cases for `gradU`/`walldist`; DUCT test-mesh cell
  centres/volumes only, no field values) — never against validation or test
  ground truth.
- **Ground truth (`U_LES`) reads**: legitimate for the 21+4 PH train/validation
  cases (needed to compute per-case training/validation error) and for CBFS
  (explicitly a non-scored training case in the benchmark's own split) — never
  for any of the 8 official test cases outside the single official scoring calls.
- **Official scoring calls made, total: 4** — each a single call to
  `closure_challenge.score()`/`evaluate_by_case()` that touches the 8 official
  test cases' ground truth: (1) the RANS-identity floor, (2) the round-1
  trained entry, (3) the round-2 trained entry, (4) round-3, the gate applied
  to the PH test cases for the first time. No fifth call has been made.
  **Superseded 2026-07-31 (recorded 2026-08-04):** a 5th call was made to
  score the round-4 entry (§0e) — cumulative distinct prediction sets
  scored: **5**. The ledger remains a self-imposed discipline: the benchmark
  imposes no scoring-call limit and instructs submitters to preview their
  score (`closure_challenge_trained_entry_round4_duct.json`,
  `scoring_calls`).
  **Superseded again 2026-08-07 (recorded same day, family supervision
  review F2):** a 6th call was made to score the round-5 entry (§0f), by
  the supervisor's designated scoring agent as the round-5
  pre-registration reserved — cumulative distinct prediction sets scored:
  **6** (floor, rounds 1–5; `closure_challenge_round5_qcr.json`,
  `scoring_calls`).
  **Priced in its own literature's terms (added 2026-08-05, method-priority
  review `CLOSURE_METHOD_PRIORITY_REVIEW.md` §2.3, commit `d84b649f`):** the
  problem this ledger addresses is adaptive overfitting of a holdout under
  repeated queries, named and analysed in Blum & Hardt, *The Ladder: A
  Reliable Leaderboard for Machine Learning Competitions*, **arXiv:1502.04585
  (2015); ICML 2015, PMLR 37** — **[ABSTRACT READ, 2026-08-05]**, verbatim:
  existing approaches "resort to poorly understood heuristics such as limiting
  the bit precision of answers and **the rate of re-submission**." **Our
  ledger is that heuristic, self-imposed.** It is harm reduction, not a
  guarantee; Blum & Hardt build a principled alternative and we do not
  implement it. Saying so before a reviewer does costs nothing we were
  entitled to keep, and it sits beside the cross-round adaptive-leakage
  qualification already carried at `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`
  §5.3. Freezing a plan before results likewise has an established venue in
  this field: the **NeurIPS Workshop on Pre-registration in Machine
  Learning**, PMLR **148** (2020) and **181** (2021) — **[METADATA ONLY]**, no
  paper from either volume read here.
- **C1 (the test-blind error/trust gate) made zero scoring calls of its own**
  and opened no test-case file of any kind when it was built — it was fit
  and validated entirely on the 21 training / 4 validation PH cases. Round 3
  (§0 above) later evaluated that same frozen gate on the 4 PH test cases'
  RANS-derived features (never their ground truth) as the input to call (4).

## 6. What is recoverable, and what remains blocked

**Term 1 — the "decline-where-it-hurts" gating term — TAKEN in round 3.**
- On 3 of 8 cases round 2's correction was worse than doing nothing:
  `alpha_05_4071_4048` (+0.0262), `alpha_05_4071_2024` (+0.0255), `NASA_2DWMH`
  (+0.0011). The C1 gate covers only the PH family; round 3 applied it to
  the 2 PH cases and recovered **0.0065** on the 8-case mean (0.0741 → 0.0676),
  matching the 0.0066 predicted almost exactly. `NASA_2DWMH`'s much smaller
  +0.0011 remains untouched: no matching-family gate exists for it, and its
  round-2 prediction is a pre-registered choice that cannot be revisited now
  without a test-truth-informed second look, which the rules forbid.
- **Why taking it now was legitimate, stated again**: the gate's parameters
  (feature screening, RidgeCV alpha, standardization, coefficients,
  threshold) were computed exclusively from the 21 PH training cases in C1,
  before round 3 ever ran. Round 3's only new action was evaluating that
  frozen model on the 4 PH test cases' RANS-derived features — never their
  ground truth — and using the binary output to choose between two
  already-legitimate predictions. No test-case data shaped the gate itself.
  See §0 for the full account and the compute ledger.

**Term 2 — the duct streamwise-profile term (a BOUND, not a measurement). Still blocked.**
- F6c measured that uncorrected RANS produces **exactly zero** secondary flow
  on the ducts (RMS ~1e-15% of bulk velocity) against a real DNS secondary
  flow of 2.07–2.22% of bulk velocity — the textbook consequence of the linear
  Boussinesq closure having no mechanism for Prandtl's secondary flow of the
  second kind.
- Since the missing secondary flow is entirely absent, it can explain **at
  most its own magnitude** of our duct error: on `AR_1_Ret_360` (our error
  9.19%) and `AR_3_Ret_360` (8.62%), the missing secondary flow bounds the
  explainable share at **≤24%** in both cases (`ACTIVE_RESEARCH.md`,
  "Supervisor analysis," building on C2 + F6c). **This is a bound, stated
  explicitly as such — "scaled MAE does not decompose exactly," so this is
  not an exact error budget** — not a measured decomposition.
- Consequence: **at least 76% of the duct error is streamwise-profile error**,
  and rank 2's total duct error (4.55%, 3.99%) is already smaller than our
  streamwise-only remainder (~7.0%, ~6.6%) — meaning a scalar
  eddy-viscosity-style correction (exactly what FIML/Ladder-B targets) is
  well-aimed at the dominant term, not a wasted effort against an
  anisotropy-only gap.
- **Not banked** because the recovery route (Ladder B3, DAFoam discrete-adjoint
  field inversion reproducing Wu, Zhang & Zhang's rank-2 method) hit a real,
  reproducible numerical blocker before completing a single field-inversion
  iteration (§7) — nothing was withheld by choice here, the compute path is
  currently stopped.

## 7. What is blocked

- **Ladder B3, Stage 3 (timed adjoint pilot on CBFS): BLOCKED.** The
  DAFoam/PETSc discrete-adjoint GMRES linear solve diverges at the very first
  iteration: `PetscConvergedReason = -9` (`KSP_DIVERGED_NANORINF`), i.e. PETSc
  detects NaN/Inf before any GMRES progress. Reproduced **identically across
  four independent configuration changes**: two primal convergence
  tolerances (`primalMinResTol` 1e-4 and 1e-6, nearly identical residual norms
  7.092e-4 vs 7.099e-4), two objective-function types (a custom
  `DAFunctionVariance` field-loss against CBFS's own LES `U_LES`, and a
  standard force objective already known to work on this lab's naca0012
  case), and two ILU preconditioner fill levels (1 and 4).
- Ruled out: mesh quality (`DACheckMesh` reports max aspect ratio 14.76, max
  non-orthogonality 33.3°, max skewness 0.26 — all "OK" against DAFoam's own
  thresholds); the primal itself (Stage 2 primal reproduces B2's baseline to
  0.087–1.41% across U/p/k/omega and is not the source).
- Because the GMRES solve never completes a single iteration, its cost —
  the dominant, scaling-critical unknown Ladder B1 flagged for the full
  140–420 core-minute field-inversion estimate — **could not be measured**;
  any further extrapolation would be a fabricated number.
- **Stage 4 (the full CBFS field inversion) correctly did not run**, gated by
  the unresolved Stage 3 blocker, per the docket's own instruction that an
  honest "does not fit" result is a valid outcome.
- Separately, **F6b (periodic hills gate)** was not attempted this session —
  time-boxed, explicitly conditional on time remaining after F6a/F6c, not a
  blocker. **Superseded 2026-07-29:** F6b was subsequently opened and gated
  (`demo-output/website/solve_registry/f6b_gate_20260729T035745Z.log`, 511 s,
  4 ranks, GATE REACHED, reattachment over-predicted by +63% to +66%). Record:
  `demo-output/website/dafoam/f6b_periodic_hills/F6b_periodic_hills.md`.

## The closure metric moved: 0.0741 → 0.0676 → 0.0654 → 0.0566

**Round 5 (§0f, the entry of record) took the ducts again, this time with
physics instead of a fit**: the untrained QCR2000 constitutive term, forward
solved to convergence on the three test ducts under a rule frozen before any
solve, moved the metric **−0.0088, from 0.0654 to 0.0566** — below
Reissmann's published 0.059525, **rank 1 of 5 scored locally at benchmark
commit `deb91557`** (local scoring, not an official placement; still
unsubmitted). Cost: AR_14's nominal 0.00003 best-on-board tie, put at risk
in writing before the call and lost as the pre-registration said it might
be (+0.0029 there against −0.0731 on the two Ret_360 ducts). The 6th
cumulative scoring call.

**Round 4 (§0e, superseded 2026-08-07) took the duct family**: Variant D
(Reynolds-invariant `d/d_max` feature, velocity-scale-normalised target,
pre-registered on `AR_7_Ret_180`) moved the metric **−0.0022, from 0.0676 to
0.0654**, cutting the gap to rank 2 from 0.0052 to 0.0030. The improvement
landed exactly where the pre-registered diagnosis said it would — the two
ducts where `Re_y` leaves the trained range — at the cost of a +0.0022
regression on `AR_14_Ret_180` that was deliberately not reverted (reverting
after seeing per-case test scores is selection on test outcomes), leaving
that case's board lead nominal at 0.00003.

**Round 3 recovered Term 1** (§0, §6): a test-blind gate, fit and validated
only on non-test PH data in a prior session, was evaluated on the 4 official
PH test cases for the first time and correctly withheld the correction on
the 2 cases it was hurting. Movement: **−0.0065**, from 0.0741 to **0.0676**,
now genuinely better than public rank 3 (0.0737), between rank 2 (0.0624)
and rank 3. We lead the public board on 5 of 8 cases, not 3.

**Term 2 (the duct streamwise-profile deficit, §6) remains blocked** on the
same real, unresolved DAFoam/PETSc GMRES numerical failure (§7) — nothing
new attempted there this round; it needs a CFD-solving budget this round's
compute allocation (2 cores / 3 GB, shared with other jobs on this box) does
not fit. It is the larger of the two terms and the next place to spend a
solving-budget session.
