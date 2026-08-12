# Closure-challenge + UQ family — supervision guidelines

Issued 2026-08-07 by the family supervisor under the SUPERVISION_CHARTER
structure. These are the family's standing rules. They restate what the
record already practices where the practice is right, and they bind where
the first-pass review (`CLOSURE_FAMILY_SUPERVISION_REVIEW_2026-08-07.md`)
found the practice thinner than the doctrine. Nothing here loosens any
existing guard; where these rules and a pre-registration conflict, the
frozen pre-registration governs the round it froze.

---

## 1. Scoring calls are chief-authorized pre-registered events. Period.

- **No agent in this family invokes `closure_challenge.score()` /
  `evaluate_by_case()` (or opens any scored test case's ground truth) except
  as the single call an approved pre-registration reserves.** The
  pre-registration must be committed — accept criterion, expectation band,
  and risk statements frozen — before the call, and the application rule
  frozen before the evidence it gates exists (the `R5_RULE_FREEZE.md`
  precedent: rule before first validation iteration).
- Wanting a score is not a reason to score. A *new scoring desire* is an
  escalation (§6), never an action. "The benchmark imposes no limit" is
  already priced (Blum & Hardt, rate-limiting heuristic) and does not
  license a call.
- **The scoring session commits its invocation as code** in the same commit
  as the record (review F7). Prose descriptions of the invocation are not
  provenance.
- **Every scoring record carries full-precision per-case values**
  (`*_per_case_full`, review F5) — the next round's "unchanged cases scored
  identically" claim must be checkable at full precision, not 4 dp.
- The scoring session performs the round-5-style **independent pre-score
  verification** fresh (hashes vs prior manifest and pre-registration,
  shape/finiteness, ordering re-check) and records it; it does not trust
  the producing session.
- The ledger is updated **in the same session** on every surface that
  carries it: STATUS §5 (dated note) and §0-series, the entry JSON, the
  MANIFEST, `ACTIVE_RESEARCH.md`, `benchmarks.json`. Review F2 is what
  missing one looks like.

## 2. Test-blind enforcement: the raising-stub + whitelist double guard is the standard

Two independent layers, both required, in every script that runs while
test-case directories are reachable:

1. **The raising stub.** Before any pipeline work: replace `score`,
   `score_from_csv`, `evaluate_by_case`, `evaluate_from_csv_by_case`,
   `evaluate_individual_case`, `_velocity_field`, `_ground_truth`,
   `_load_csv_predictions`, `evaluation_points` with raisers **in every
   namespace they are reachable from** (the package, `dataset_utils`,
   `eval` — the `from X import Y` aliases are the trap), then **prove the
   guard armed** by calling a stubbed entry point and catching the refusal.
   An unproven guard is an unarmed guard.
2. **The loader whitelist.** Every function that opens a ground-truth file
   asserts its case against a train/validation whitelist **before opening
   the file**. Call-site discipline is not a guard (review F6: the test
   ducts ship `0/U_LES` on disk; one editing mistake away is too close).
   `battery_common.py` is the pattern; no new truth loader lands without
   the assert, and legacy loaders get it when touched.

Cleaner still, when possible: keep truth files **absent** from the run tree
(the round-5 solve directories never contained `*_LES`), and read evaluation
coordinates from the shipped convenience CSVs rather than through the
package.

Reading an official call's outcome, or the public leaderboard, to *target
effort* is legitimate; using it to *fit, select, or revert per-case* is the
one forbidden thing. Post-score, the only honest fallback is the whole
pre-registered bundle judged as a bundle.

## 3. The hurt-cap discipline

- Any retraining/replacement route declares, **before its numbers exist**:
  the acceptance floor against the incumbent entry, any per-case hurt cap,
  and the all-or-none application scope. The R5-alpha05 NO-GO and the
  round-5 AR_14 risk statement are the two canonical outcomes: the gate
  binds in both directions, and a materialised pre-accepted risk is
  reported, not reverted.
- **A cap must state where it came from.** The +0.010 cap is currently
  hand-chosen and underived (priority review §2.4, proposal
  `w8-a-hurt-cap-that-states-where-it-came-from`); until that lands, any
  new pre-registration that uses a cap states in one sentence why its
  number is the number — "the same as last time" is a derivation only if
  last time had one.
- Frame caps in their literature's name (non-inferiority margin;
  high-confidence improvement) so referees meet a known discipline.

## 4. Every entry surface carries its caveats beside its claims

Katie's GUI conventions, applied family-wide:

- **Rank 1 is never stated without, in the same breath**: (a) *scored
  locally at the pinned benchmark commit, unsubmitted, not an official
  placement — the steward's number is the number*; and (b) **while the
  single-seed PH model ships**, the seed bound beside the margin: the
  truth-free bound (0.0024 overall-equivalent) is comparable to the 0.0029
  rank-1 margin, and the rank-1 reading carries that uncertainty.
  `closure.html`'s stability note is the reference wording; review F1 is
  what omission looks like. **(c) Added 2026-08-10, chief ruling — MANDATORY:
  P(rank 1) and the not-decided pairs.** **EVERY FIGURE IN (c) AND (d) IS
  SUPERSEDED 2026-08-11 — SEE (e). All of them were computed against a FOUR-entry
  board that no longer exists.** They are kept unrewritten, per this section's own
  "dated superseded notes, never rewrites" rule.
  **P(rank 1) = 68%**; an eight-case
  sample cannot pin it tighter than 2–100% at 95%; **the leads over Reissmann
  and Wu & Zhang are not statistically decided** (paired per-case differences
  t = −0.50 and t = −0.95, against a per-case dispersion five times the
  0.002878 margin), while the leads over Liu and Montoya are (98.7%, 99.8%);
  **the standing is two cases wide** — delete `alpha_15_13929_2024` and the
  point ranking falls to rank 2; **`AR_1_Ret_360` and `AR_3_Ret_360` are ties
  below published precision** (0.00003 and 0.00008) and are not per-case wins.
  A rank claim omitting this fails Ladder V rung V8. ~~**The figure is INTERNAL:
  internal surfaces carry it, public surfaces in `dist/` carry the qualitative
  clause only, and both carry the sweep token `not statistically decided`.**~~
  Source: `campaign/PROBABILITY_OF_RANK_2026-08-10.md`.
  - **(d) SUPERSEDED 2026-08-10, later the same day — the internal/external
    split struck through above was WITHDRAWN by chief ruling. Recorded here
    2026-08-11; the original wording is kept struck rather than deleted, per this
    section's own "dated superseded notes, never rewrites" rule.** Ladder V's
    cold-reproduction pass recomputed the figure as **0.674 from public data —
    the published board plus our own eight CSVs — in about a minute**, with no
    access to the internal document. A figure an outsider reproduces trivially is
    not protected by being withheld; it only reads as concealed, and it reads
    that way to exactly the reader the disclosure strategy exists to convince.
    **The figure now TRAVELS with the entry.** Every surface, internal or public
    — including anything shipping in `dist/` and the entry's own cover material —
    carries **P(rank 1) = 68%** *with its interval* (**2–100% at 95%**, double
    bootstrap; an eight-case sample cannot pin it tighter) *and* the not-decided
    pairs (Reissmann, Wu & Zhang; Liu and Montoya **are** decided). **One
    prohibition replaces the split: no surface may state the figure without its
    interval** — a bare 68% is a worse claim than no figure at all, because 68%
    sounds settled and eight cases do not support settled. The qualitative clause
    is still required everywhere and still carries the sweep token
    `not statistically decided` — **which must sit unbroken on one line**, since
    V10 greps for it literally and a line-wrapped token is invisible to that
    sweep. Sources:
    `campaign/PROBABILITY_OF_RANK_2026-08-10.md` (head banner and §"the
    propagation rule"); `campaign/LADDER_V_TRIPLE_VERIFICATION.md` (V8 amendment,
    2026-08-10).
  - **(e) RECOMPUTED 2026-08-11 — the board moved, and every figure in (c) and (d)
    is struck and kept.** The live leaderboard, fetched 2026-08-11T23:33Z by two
    independent routes, carries **six** entries and a **new leader, Yang at
    0.0580** (`campaign/BOARD_MOVED_2026-08-11.md`). The eight case columns are
    unchanged, so scores stay like-for-like. Recomputed by the same method against
    the six-entry board (`campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`,
    script `sdk/scripts/probability_of_rank.py`, which reproduces the four-entry
    figure exactly when the two new rows are removed):
    - **P(rank 1) = 50%** (50.2%, B = 400,000), which eight cases pin no tighter
      than **0–97% at 95%** — *wider* than the struck 2–100%, at the end that
      matters, and 1.55% of outer resamples give exactly zero.
    - **Four leads are not statistically decided**, not two: Yang (t = −0.19),
      Reissmann (t = −0.50), Wu & Zhang (t = −0.95), Tian/Buchanan/Hickel/Dwight
      (t = −1.03). Liu and Montoya remain decided (98.7%, 99.8%). **The new
      leader is on the undecided list**, which is the clause a rank claim most
      needs and the struck version could not contain.
    - **The standing is three deletions wide**, not two cases wide, and the
      load-bearing case has changed identity: deleting `alpha_15_13929_4048`,
      `alpha_15_13929_2024` or `alpha_05_4071_4048` drops the point rank to 2, 3
      and 2. Any sentence naming `alpha_15_13929_2024` as *the* case the standing
      rests on is frame-specific to the four-entry board.
    - **The seed bound now crosses the rank boundary.** Loaded adversely the
      overall is 0.059047 against Yang's 0.058013 — **rank 2, not rank 1.** Clause
      (b)'s "comparable to the margin" is now an understatement: the bound is
      **1.8×** the 0.001365 margin, where it was 0.83× the 0.0029 one.
    - **A THIRD prohibition joins the two above, and it is the one this incident
      bought: no surface may state the figure without its BOARD** — how many
      entries, fetched when. An interval without a board is what expired here,
      silently, across nine surfaces at once, and no check in the corpus was
      looking. Sources: `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`;
      `campaign/BOARD_MOVED_2026-08-11.md`; docket D50.
- The AR_14 loss, the 4-of-8 best-on-board count, and the "two of four
  best rows are the organisers' baseline" attribution travel together —
  none is quoted without the others where standing is summarized.
- **Superseded sections get dated superseded notes, never rewrites.** A
  document that polices staleness (CHALLENGE_LANDSCAPE §5) is itself
  subject to the convention.
- Naming (review F4): "round 5" means the QCR entry of record;
  the alpha_05 regime item is written **"R5-alpha05 (NO-GO)"** in all new
  text.
- **Surface checklist for any entry-of-record change** — all in the same
  session: STATUS (§0-series + §2/§3 superseded notes + §5 ledger), entry
  JSON + MANIFEST, `closure.html`, `ACTIVE_RESEARCH.md` (header + Ladder
  C), `benchmarks.json`, submission draft (addendum + §5.3 disclosures +
  cover email numbers), LaTeX report (abstract AND interior round ledger
  AND tables), CHALLENGE_LANDSCAPE, docket outcome, wall. Anything
  machine-generated (`closure_eval` master table) is regenerated, not
  hand-edited.

## 5. UQ band composition, per the doctrine

- **Unquantified is never zero.** A channel with no figure is `None`; it
  goes to `missing`, the total says it covers less than the budget. A bare
  scalar `0.0` is refused by `uncertainty_band.compose` (review F8); a
  genuinely measured zero is a Mapping with `band_abs: 0.0` and a stated
  `method`.
- All composition goes through `uncertainty_band.compose` /
  `uq.combine_expanded` — no act assembles its own RSS. The combined band
  is never displayed without `as_channel_table()` one level down.
- Shared evaluations are withheld with their reason
  (`independent_of_numerical: false`), not squared in.
- **Epistemic intervals travel alongside, never inside**: the
  perturbed-coefficient envelope is `coefficient_interval(...)`, reported
  next to the composed band, `in_quadrature: false` always.
- **Surrogate posterior spread never enters a quadrature.** The GP's σ is
  a calibration diagnostic (`loo_z_rms` / `holdout_z_rms`, with the
  too-narrow reading stated) and a plot ribbon — nothing else. Its
  known-too-narrow bars stay inert (verified in review §4).
- **Bands are over converged members only.** An unconverged, cap-stopped,
  or still-moving member is excluded **and named** in the record
  (`MODEL_FORM_BAND` pattern); an empty band is reported as band-less, not
  padded. A reference not contained by a band is reported as NOT contained.
- Every budget names its largest quantified term next to its `missing`
  list — a missing term is not a small term.

## 6. Escalation — to the chief supervisor, before acting

Escalate, and do not act while the escalation is open:

1. **Anything touching the entry of record**: the submission CSVs, the
   MANIFESTs, the entry JSONs, or any regeneration of them. Scoring
   records and manifests are immutable once written; a defect found in one
   is corrected beside it, never in it.
2. **Any new scoring desire** — any proposal whose closure requires a
   `score()` call or any read of scored-test ground truth, before the
   pre-registration is drafted.
3. **Any guard modification.** Loosening or removing a stub, whitelist, or
   assert requires chief authorization in advance, full stop.
   Strengthening-only changes (adding an assert) are allowed but recorded
   in a review file first and reported (review F6 is the template).
4. Anything that would touch Katie's send-package semantics (§5.3
   disclosures, cover email claims) beyond executing the already-mandated
   quotation audit.
5. A discovered breach or suspected breach of test-blindness, however
   small — report first, remediate second.

## 7. Standing verification cadence

After every round, the family runs (and records) the round-5-style checks:
full hash chain re-verification, per-case arithmetic, eval-package commit
and cleanliness, and a caveat sweep of the surface checklist in §4. Big
conclusions get the adversarial treatment the supervisor doctrine already
mandates: assumed wrong until independently re-derived.
