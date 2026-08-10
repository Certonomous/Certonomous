# Ladder V — triple verification of the round-5 entry (blocks the send)

Status: **STANDING PROTOCOL, EXECUTION PARKED.** Katie parked submissions on 2026-08-07; this
ladder is the pre-registered gate that any future send must clear. Recording it now, before any
send is live, is itself part of the anti-hindsight discipline: the gate exists before the thing
it gates.

Structural rule that makes it triple rather than the same check three times: three passes, three
different minds, three different directions of attack. Pass 1 re-derives (does everything
recompute?), Pass 2 attacks (can it be broken?), Pass 3 replicates cold (does it survive a
stranger?). No agent may verify work it produced; every rung ships an evidence record; the family
supervisors' four personal checks apply per the supervision charter.

## PASS 1 — RE-DERIVATION (owner: Closure/UQ family supervisor, personally per charter §3)

- **V1. Score re-derivation in a clean environment**: fresh venv, pinned closure-challenge package
  version recorded, benchmark at frozen commit deb9155; recompute the 8-case scores and overall
  0.056647 from the submission CSVs; byte-compare those CSVs against the prediction files the
  solves produced. Any digit that moves fails the rung.
- **V2. Pre-registration chain**: verify by commit timestamps that the acceptance criterion
  (0bade54a) predates every solve it judged, and that the 6th scoring call's record matches what
  was pre-registered. The chain is the anti-hindsight proof; print it as a table.
- **V3. Leakage assertions executed, not read**: run closure_baseline_error_gate.py's assertion
  block live; re-cite §4.1's line numbers against the current code (they were cited against an
  older revision — confirm they still hold); confirm the four test-case gate decisions reproduce
  from train-only inputs.
- **V4. One duct case traced end-to-end by hand**: config → mesh → solver log (real iterations,
  real convergence) → field → interpolation → CSV row count/shape → scored number. One complete
  unbroken chain, documented with paths.
- **V5. QCR provenance**: `git log --follow` on the QCR implementation proving in-house history;
  confirm zero fitted parameters anywhere in the duct path (the "untrained" claim is load-bearing —
  prove it by showing there is nothing that could be fitted); Spalart (2000) cited wherever QCR is
  named.

## PASS 2 — ADVERSARIAL (owner: a different agent than any Pass-1 executor; brief: assume wrong until defended)

- **V6.** Re-run the §4 adversarial audit against the ROUND-5 entry specifically — the existing
  audit predates QCR; every finding gets a round-5 verdict, and QCR gets its own compliance line
  (used at solve time only? touched no test data? stated in the description?).
- **V7. Kill the two known defects and prove it**: the false docstring sentence corrected (and a
  grep for any other count claims about scoring calls, all reconciled against actual call sites);
  the submittable artifact assembled to the accepted format (1000×3, no header, one of the two
  accepted layouts, verified against an accepted submission in submissions/).
- **V8. Claims-language audit of the cover email + description document**: every quantitative
  sentence maps to a named artifact; the banned-claims list enforced — no novelty claim on gated
  correction (§7.4), no "comfortable" AR_14 lead (0.00003), no best-on-board counts that lean on
  organizer-baseline rows (§4.7), no "official rank" language anywhere (local scoring stated
  plainly), soft-adaptive-leakage disclosure present in the lab's own words (§4.3). A claims
  table: sentence → artifact → verdict.
  **V8 strengthening, 2026-08-10 (chief ruling, protocol edit — not a rung execution):** any rank
  claim, internal or external, must carry **P(rank 1) and the not-decided pairs**. A rank claim
  that states a placement without stating the probability that the placement survives case
  resampling, and without naming which pairwise comparisons are undecided (currently Reissmann and
  Wu & Zhang; Liu and Montoya are decided), fails this rung. Internal surfaces carry the figure
  itself (P(rank 1) = 68%); external surfaces carry the qualitative clause only — the figure is
  internal by the item's own gate and may not be published. Both wordings contain the literal
  string `not statistically decided`, which is the token V10's cross-surface sweep greps for.
  Source: `campaign/PROBABILITY_OF_RANK_2026-08-10.md`.
- **V9. Prior-art completeness**: the §7.4 split carried verbatim into the description (identify
  vs control papers correctly separated); the Buchanan-coefficients firewall stated as a
  compliance fact; a final check that nothing in the entry's history warm-started from, calibrated
  against, or compared during development to that model's hump behavior.
- **V10. Cross-surface number sweep**: closure.html, the Active Research board, the wall,
  PRODUCT_LIST, and the submission package must all carry round-5 numbers with the same caveats —
  one inconsistent surface fails the rung (the board was still showing round 3 at last report;
  that class of drift is what this rung exists to catch).

## PASS 3 — COLD REPRODUCTION (owner: an agent with no prior contact with the closure line; the reviewer simulation)

- **V11. Fresh clone, no context beyond the submission package itself**: following only what the
  package says, reproduce the scoring and confirm the claims table's artifacts exist where the
  package says they are. Every question the cold agent has to ask to succeed is a defect in the
  package (the steward won't ask — he'll just doubt).
- **V12. The cold agent writes the skeptic's report**: the three weakest points of the entry as an
  outside reviewer would state them, each with the record's best answer beside it. This becomes
  Sanaa's briefing for any follow-up questions from the steward.

## CLOSE-OUT

- **V13. Ladder report in negative-verdict-review format**: every rung PASS/FAIL with evidence
  links, the claims table, the skeptic's report, and a single consolidated list of anything that
  changed during verification. No rung self-graded; the three pass-owners sign their own sections.

**The send gate, unchanged**: all 13 rungs green → Sanaa's personal checks (she re-runs V1 and V3
with her own hands, reads V12) → Sanaa + Katie proofread the cover email → Katie sends. Nothing is
automatic at any point.

## Rungs executable NOW despite the park

V7 (both defects), V10 (cross-surface sweep), and V2 (the pre-registration table) do not require a
live send and harden the record whether or not the entry ever goes out. They may be run as normal
docket items. V1/V3/V4/V5 may also be run early as record-hardening. V6/V8/V9/V11/V12 bind to a
concrete submission package and wait for unpark.

## Status ledger (chief-maintained)

| Rung | Verdict | Evidence | Date |
|------|---------|----------|------|
| V1 | **PASS** | 0.056647191704213645 reproduced to the last digit in a fresh venv (pkg 0.3.1 @ 1c4e22c8, benchmark fresh-cloned @ deb91557); duct CSVs regenerated from raw fields byte-identical — `LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md`, 9a21d65c | 2026-08-08 |
| V2 | **PASS** | criterion 0bade54a predates every solve it judged; 6th call matches its pre-registration clause by clause — `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md`, 49f71b8c | 2026-08-08 |
| V3 | **PASS** | assertion block executed live with a negative control; §4.1 citations re-anchored (+13 line shift), all claims hold; four gate decisions reproduced train-only | 2026-08-08 |
| V4 | **PASS** | AR_1_Ret_360 traced unbroken config→mesh→395-iter log→field→interpolation→CSV (sha256 bb8d61fb…)→0.04547044480564218 | 2026-08-08 |
| V5 | **PASS** | in-house authorship @ 303247bb, .so hash matches record; untrained proven structurally (only new coefficient is Spalart's published 0.3); five campaign records got dated additive citation notes | 2026-08-08 |
| V6 | waits for unpark | binds to a concrete submission package | — |
| V7 | **PASS** | docstring fix verified at call sites + three further stale count claims fixed (incl. build_benchmarks.py page-regression fossil); round-5 artifact format-verified vs accepted submissions | 2026-08-08 |
| V8, V9 | wait for unpark | bind to cover email / description document | — |
| V8 *(protocol strengthened, not executed)* | **criterion added** | any rank claim must carry P(rank 1) and the not-decided pairs; sweep token `not statistically decided`; five surfaces already compliant (CLOSURE_CHALLENGE_STATUS §0f, ACTIVE_RESEARCH, closure.html, benchmarks.html, benchmarks.json→wall.json) — `campaign/PROBABILITY_OF_RANK_2026-08-10.md` | 2026-08-10 |
| V10 | **PASS** | all surfaces round-5 consistent after two drift fixes (benchmarks.html fossil; ACTIVE_RESEARCH tense) | 2026-08-08 |
| V11, V12, V13 | wait for unpark | cold reproduction + skeptic's report + close-out bind to the send | — |

Every rung that can run before a send exists has run, and passed. What remains is exactly the set
that needs a real submission package — the record is as hard as it can get while parked.
