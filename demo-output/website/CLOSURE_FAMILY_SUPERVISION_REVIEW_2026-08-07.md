# Closure-family supervision review — first pass, 2026-08-07

Family supervisor's state review under the SUPERVISION_CHARTER structure.
Scope: cross-document consistency after round 5, leakage-guard chain
integrity across the round-5 tooling, and two personal code checks — the
round-5 scoring path and `uncertainty_band.py`'s composition logic. **Zero
scoring calls were made by this review; no test ground truth was read; no
prediction file was created or altered.** Findings are recorded here BEFORE
any fix; the fix commit follows this record and names it.

Companion (deliverable 2): `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md`.

---

## 1. Cross-document consistency after round 5

Sweep coverage: `CLOSURE_CHALLENGE_STATUS.md` (all of §0–§7 including §0f),
`closure_challenge_round5_qcr.json`, both submission MANIFESTs,
`campaign/R5_{PREREGISTRATION,RULE_FREEZE}.md`, `R5_validation_AR7.json`,
`CLOSURE_METHODS_COMPARISON.md`, `CLOSURE_EVALUATION_PROTOCOL.md`,
`closure_challenge_stability_physicality_audit.md`,
`CLOSURE_METHOD_PRIORITY_REVIEW.md`, `closure.html`, `ACTIVE_RESEARCH.md`,
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (§10 addendum + §5.3),
`benchmarks.json`, `latex/closure_challenge_report.tex`,
`agenda/CHALLENGE_LANDSCAPE.md`, `agenda/docket.json`,
`closure_eval/closure_eval_master_table.md`.

### What is right, verified rather than assumed

- **Rank-1-with-caveat discipline holds on the live surfaces.** STATUS §0f,
  the round-5 entry JSON, both §2/§3 superseded notes, `ACTIVE_RESEARCH.md`
  (header + Ladder C), `benchmarks.json`, the submission draft §10 addendum,
  the docket outcome, and the LaTeX report's abstract/front box all state
  rank 1 **with** "scored locally at `deb91557`, unsubmitted, not an
  official placement" in the same breath. No surface was found claiming an
  official rank.
- **`closure.html` is the model surface**: the stability note is explicitly
  re-scoped for round 5 and puts the truth-free seed bound (0.0024) beside
  the 0.0029 rank-1 margin — "the rank-1 reading above must carry that
  uncertainty."
- The AR_14 loss (+0.0029, tie lost, 4-of-8 best-on-board) is carried
  consistently on every surface that reports per-case standing.
- Round-5 hash chain is closed: entry JSON ↔ round-5 MANIFEST ↔ CSVs on
  disk ↔ pre-registration §3 table ↔ round-4 manifest for the five
  unchanged cases — re-verified independently by this review (all pass;
  §3 below).

### F1 — MEDIUM. The seed-stability qualifier did not survive into §0f or the round-5 records beside the rank-1 margin.

The audit's pre-registered consequence (G1) was that "the leaderboard-gap
language must carry a seed-uncertainty qualifier." Round 5's gap language
is now the **0.002878 rank-1 margin**, and the truth-free seed bound is
**S_bound = 0.0024** — the bound is 83% of the margin, and the three
seed-dependent PH-model predictions ship in round 5 byte-identical. The
qualifier is present in `closure.html` (re-scoped, exemplary) and in the
submission draft §5.3 item 9 (still phrased against the round-4 0.0030 gap),
but:

- `CLOSURE_CHALLENGE_STATUS.md` §0f states the 0.002878 margin three times
  with no seed qualifier; the qualifier lives only in §0e, a section §0f
  supersedes — a reader of the entry-of-record section alone never meets
  the bound.
- `closure_challenge_round5_qcr.json` (`our_rank_overall`) and the round-5
  MANIFEST state the margin with no seed qualifier. These are immutable
  scoring records produced under the pre-registration; they are NOT edited
  post-hoc — the qualifier is owed on the prose surfaces that cite them.
- `ACTIVE_RESEARCH.md` Ladder C states "margin 0.002878" with no qualifier.
- `latex/closure_challenge_report.tex` abstract states the margin; the seed
  section (S_bound 0.00242) still says "a tenth of the gap to rank 2" —
  round-4 scoping.

**Consequence executed (fix commit): the qualifier is added to STATUS §0f
and ACTIVE_RESEARCH Ladder C.** The LaTeX re-scope and the draft §5.3 item-9
re-scope are Katie's-package edits, flagged for the pre-send quotation audit
that §9.4/§10 of the draft already mandates.

### F2 — MEDIUM. STATUS §5's scoring-call ledger stops at 5 calls.

§5 carries the round-4 superseded note ("cumulative … **5**") and no
round-5 note; §0f states the 6th call. The file's own convention is a dated
superseded note per event. **Fixed in the fix commit** (dated note, 6 calls,
pointing at §0f).

### F3 — LOW-MEDIUM. Stale entry-of-record statements on dated surfaces.

Per the family convention these are dated records and stand unchanged, but
three of them present round 4 as the *current* entry with no superseded
note, which the STATUS file's own idiom requires:

- `latex/closure_challenge_report.tex`: interior §"Five rounds" item
  ("Round 4 — 0.0654 …, the entry of record"), the per-case table caption
  ("Round-4 values are the entry of record"), and the NO-GO section's
  closing "Round 4 stands as the entry of record" — all contradict the
  updated abstract/leaderboard of the same document. **Dated superseded
  notes added in the fix commit** (text-only, no number rewritten).
- `agenda/CHALLENGE_LANDSCAPE.md` §1 row and §5 ("The entry of record is
  0.0654") — a document whose §5 exists to police exactly this staleness.
  **Dated note added.**
- `closure_eval/closure_eval_master_table.md` — machine-generated
  (`build_master_table.py`); its round-4 row is correctly labelled as our
  recorded result, but "the entry of record's own models" now reads stale.
  NOT hand-edited (generated artifact); regeneration is queued for the
  battery owner. Recorded here so the gap is a decision, not an oversight.

### F4 — LOW. "R5" naming collision.

`closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md` (the alpha_05
regime retraining, pre-registered and **NO-GO**, never scored) and
`campaign/R5_PREREGISTRATION.md` (round 5, the QCR entry of record) share
the "R5" name. `CLOSURE_METHOD_PRIORITY_REVIEW.md` §2.4 and the LaTeX
report's "pre-registration that said no" both say "R5" meaning the former.
No document was found actually conflating them, but the collision is a
standing hazard. Guideline written (guidelines §4): the alpha_05 item is
referred to as "R5-alpha05 (NO-GO)" in all new text; "round 5" is reserved
for the QCR entry.

### F5 — INFO. Round-4 full-precision per-case values were never recorded.

`closure_challenge_trained_entry_round4_duct.json` stores per-case scores
at 4 decimals (only the overall at full precision), so round 5's "the five
unchanged cases scored identically" is verifiable at 4 dp and by overall
arithmetic, not at full precision. Round 5 fixed this
(`round5_per_case_full`). Guideline: every future scoring record carries
full-precision per-case values.

---

## 2. Leakage-guard chain across the round-5 tooling

- `closure_round5_qcr_forward.py`: the raising stub covers all nine entry
  points (`score`, `score_from_csv`, `evaluate_by_case`,
  `evaluate_from_csv_by_case`, `evaluate_individual_case`,
  `_velocity_field`, `_ground_truth`, `_load_csv_predictions`,
  `evaluation_points`) across all three reachable namespaces (`cc`, `du`,
  `ev` — covering the `from .dataset_utils import` aliasing), and proves
  itself armed by catching the refusal before any case is touched.
  Evaluation coordinates come from the shipped convenience CSVs, strictly
  cleaner than round 4's `evaluation_points()` route. Truth files were
  never copied into the run tree. **Sound.**
- `closure_round5_points_order_check.py`: no `closure_challenge` import at
  all; truth read only for the four training ducts; verified. **Sound at
  the call site** — but see F6.

### F6 — MEDIUM-HIGH (guard gap, not a breach). `_load_duct_ground_truth_U` has no whitelist assert, and the test ducts ship `0/U_LES` on disk.

`train_closure_extended_correction.py::_load_duct_ground_truth_U` opens
`<case>/0/U_LES` for **any** case name passed. The benchmark clone ships
`0/U_LES` for the test ducts too (verified: `AR_1_Ret_360/0/U_LES` exists),
so the only thing preventing a future editing mistake from reading test
truth through this loader is call-site discipline — exactly the failure
mode `CLOSURE_EVALUATION_PROTOCOL.md` §3.1 names when it made loader-level
whitelists the standard ("asserts its case against a train/validation
whitelist **before opening a file**"). `battery_common.py` meets the
standard; this older loader, imported by round-5 tooling, does not.
**No breach occurred** — every call site sweeps only `_DUCT_TRAIN` — but
the double guard is single on this path. **Fixed in the fix commit**: a
whitelist assert (train ducts + `AR_7_Ret_180`) added to the loader. This
is a strengthening-only guard change, recorded here per the guidelines'
escalation rule (loosening would have required chief authorization;
strengthening is recorded and reported).

---

## 3. Personal check (a) — the round-5 scoring path

The question: does the round-5 eval invocation match rounds 1–4 exactly —
any normalization drift would silently move all comparisons.

**Verified, without making any scoring call:**

1. **The eval package is pinned and clean.** `/home/ubuntu/closure-challenge-pkg`
   is at `1c4e22c8` (the identical commit in the round-3/4/5 manifests),
   `git status` empty. `eval.py` read in full: per-case =
   `mean(||U_pred − U_true||₂) / mean(||U_true||₂)` over the case's 1000
   points; overall = unweighted `np.mean` over 8 — the normalization is
   inside `evaluate_individual_case`, so any invocation through this
   package at this commit computes the identical metric. There is no
   local reimplementation anywhere in the round-5 chain.
2. **Behavioral invariant.** The five unchanged CSVs are byte-identical to
   round 4 (hashes re-verified on disk by this review, all 8 files, against
   the round-5 manifest, the round-4 manifest, the entry JSON and the
   pre-registration §3 table — all pass), and their round-5 per-case scores
   equal round 4's at recorded precision. A normalization drift cannot
   reproduce five per-case scores on unchanged inputs.
3. **Arithmetic.** mean(`round5_per_case_full`) = 0.056647191704213645 =
   the recorded overall (exact); `delta_vs_round4_full` exact; the five
   unchanged cases' full-precision sum is consistent with round 4's
   full-precision overall within the 4-dp resolution of round 4's per-case
   record (residual 3.5e-5 < 1.5e-4 tolerance).

### F7 — LOW-MEDIUM (provenance). The round-5 scoring invocation is not on the record as code.

Commit `07a7fe9e` (the 6th call) carries the records and manifests but no
scoring script; the invocation exists as prose ("the identical local-scoring
path rounds 1–4 used"). Rounds 3 and 4 committed their invoking scripts.
The verification above makes drift effectively impossible for round 5, but
the next scoring session must commit its invocation (guidelines §1). No fix
possible retroactively; recorded.

---

## 4. Personal check (b) — `uncertainty_band.py` composition logic, line by line

Reviewed with its arithmetic delegate `uq.combine_expanded` and its two
production consumers (`scripts/coefficient_uq_plate_analysis.py`; tests).

**What holds:**

- Rule 1 (unquantified ≠ zero) holds for `None`, for Mappings without
  `band_abs`, and end-to-end through `combine_expanded` (`missing` list,
  `covers_all_channels` false, coverage sentence says the total covers less
  than the budget). Tested (`test_unquantified_is_not_zero`).
- Rule 2 (shared evaluation withheld): correct; withheld channels are
  dropped from the quadrature with the reason carried. One cosmetic
  asymmetry: a withheld channel also appears in `missing` (it is counted
  once in the sum — conservative, display-only duplication). LOW, noted.
- Rule 3 (coefficient interval alongside, never inside): correct;
  `in_quadrature: False` is forced even on caller-supplied bands.
- Rule 4 (breakdown and total from one call): correct by construction.
- **The GP's error bars are inert, as required.** `pce_surrogate.GPFit`
  exposes posterior σ only via `predict(with_std=True)`; the plate study
  uses it solely for the calibration diagnostic (`holdout_z_rms`, with the
  honest "well above 1 → too narrow" note) and plot error bars. Nothing
  routes GP σ into `compose` or `combine_expanded`; the plate study's
  composed band passes all three channels as `None` and carries the
  Schaefer-box envelope as a coefficient interval alongside. The
  known-too-narrow bars cannot reach any displayed total. **Verified.**
- `MODEL_FORM_BAND` honors converged-cells-only: unconverged members are
  excluded and named per group (five groups currently band-less rather
  than padded), and the one reference not contained (FUN3D at P_re5e6) is
  reported as NOT contained.

### F8 — MEDIUM. `compose` accepts a bare `0.0` as a quantified channel — the exact anti-pattern its docstring exists to stop.

`_figure(0.0)` → `0.0` → the channel is marked `quantified: true`,
contributes zero to the RSS, is absent from `missing`, and
`covers_all_channels` comes back **true**. The module's own header names
"a channel that is unquantified gets passed as 0.0 because 0.0 is easier to
type than None" as the failure it enforces against — and a bare 0.0 sails
through, silently converting "never measured" into "measured, zero, full
coverage." No production caller currently does this (the single caller
passes `None`s), and no test covers it. **Fixed in the fix commit**: a bare
scalar `0.0` now raises with instructions (pass `None` for unquantified; a
Mapping with `band_abs: 0.0` plus a stated `method` remains legal for a
genuinely measured zero). Test added.

### F9 — LOW. Two truthiness edges in `compose`/`coefficient_interval`.

`working_value=0.0` disables the `band_rel` conversion and the
`working_value`/`width_pct_of_working` blocks (`if working:` truthiness).
Harmless for every current quantity (none has a legitimate zero working
value); recorded so the next caller with a signed delta QoI knows. Not
fixed — a fix would change behavior for no live caller; revisit when a
zero-crossing QoI arrives.

---

## 5. Disposition

| # | Severity | Finding | Disposition |
|---|---|---|---|
| F1 | MEDIUM | Seed qualifier missing beside rank-1 margin on §0f / ACTIVE_RESEARCH / (LaTeX, draft re-scope) | STATUS §0f + ACTIVE_RESEARCH fixed; LaTeX/draft flagged for pre-send audit |
| F2 | MEDIUM | STATUS §5 ledger stops at 5 calls | Fixed (dated note) |
| F3 | LOW-MED | Stale "round 4 = entry of record" on LaTeX interior, CHALLENGE_LANDSCAPE; master table (generated) | Dated notes added; master-table regen queued |
| F4 | LOW | "R5" naming collision (alpha05 NO-GO vs round-5 QCR) | Guideline §4 naming rule |
| F5 | INFO | Round-4 per-case full precision never recorded | Guideline §1 (fixed from round 5 onward) |
| F6 | MED-HIGH | Duct truth loader lacks whitelist; test ducts ship U_LES | Fixed (strengthening-only assert), recorded here first |
| F7 | LOW-MED | 6th call's invocation not committed as code | Guideline §1; behavioral verification recorded |
| F8 | MEDIUM | `compose` accepts bare 0.0 as quantified | Fixed + test, recorded here first |
| F9 | LOW | `working_value=0.0` truthiness edges | Recorded, deliberately not fixed |

Nothing in this review changes the entry of record. The scoring-call ledger
stands at 6; this review made no call and opened no test ground truth.
