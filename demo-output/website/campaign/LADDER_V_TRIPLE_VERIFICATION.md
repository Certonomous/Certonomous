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
  Wu & Zhang; Liu and Montoya are decided), fails this rung. ~~Internal surfaces carry the figure
  itself (P(rank 1) = 68%); external surfaces carry the qualitative clause only — the figure is
  internal by the item's own gate and may not be published.~~ Both wordings contain the literal
  string `not statistically decided`, which is the token V10's cross-surface sweep greps for.
  Source: `campaign/PROBABILITY_OF_RANK_2026-08-10.md`.
  **V8 amendment, 2026-08-10 (chief ruling, protocol edit — the internal/external split above is
  WITHDRAWN).** Pass 3 recomputed the figure as **0.674 from public data in about a minute**, with
  no access to the internal document. A figure an outsider reproduces trivially is not protected by
  being withheld; it only looks concealed, and it looks that way to the exact reader the disclosure
  strategy exists to convince. **The figure now travels with the entry.** Every rank claim,
  internal or external, carries P(rank 1) **and its interval** (an eight-case sample cannot pin it
  tighter than 2–100% at 95%) **and** the not-decided pairs. One new prohibition replaces the old
  split: **no surface may state the figure without the interval** — a bare 68% is a worse claim
  than none, because 68% sounds settled and eight cases do not support settled. Every other
  banned-claims rule stands unchanged.
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

## PASS 4 — STRUCTURAL (added 2026-08-10 by Katie; both rungs fix the LADDER, not the entry)

These exist because the first full run of this ladder produced three findings that
were **nobody's rung**: a tracked shipping archive carrying round-3 numbers with zero
caveats, a live self-audit guard pinned to round 3, and a public page carrying a
prior-art sentence struck five days earlier. Every one lived on a surface no
hand-maintained list had ever included.

- **V14 (A14). Mechanical surface discovery, not a maintained list.** The cross-surface
  sweep is replaced by a **repo-wide search for every score literal** — 0.0741, 0.0676,
  0.0654, 0.056647 and every case-level value — **plus every prior-art sentence
  fragment**, across **tracked files, built artifacts, and shipping archives** including
  `dist/`. The searcher must prove its own reach first (gzip, ignore-files, untracked
  trees, archives that must be opened to be read) and state what its frame structurally
  cannot contain. **A surface nobody listed is exactly where a stale claim survives**, so
  the rung fails if its method is a list rather than a search. Owner: an agent that has
  written to none of the surfaces.

- **V15 (A15). Verification-created text re-enters the claims table.** Pass 1 established
  that new disclosure prose is where unattributed claims are born, and the first run of
  this ladder had a verification rung introduce a defect a sibling rung had just cleared
  (L-53). Therefore: **any text written during the ladder — by any pass, including fix
  passes — must pass V8's claims table before the ladder goes green.** Otherwise the fix
  pass is the last unverified writer and the ladder certifies everything except its own
  output. **Owner: NOT the pass that wrote the text.** No agent verifies its own prose,
  and a fix pass is a writer like any other.

## WHEN THE LADDER IS GREEN — the termination rule (chief, 2026-08-10)

V15 creates a loop: every fix pass writes text, and ladder-written text must re-enter
the claims table. Without a stated terminating condition that recurses forever, and a
ladder that cannot finish is a ladder that never gates anything.

**The ladder is GREEN at a FIXED POINT, not at a clean sweep.** Specifically:

1. Every rung V1–V15 carries a PASS.
2. A full re-run of V8, V10, V14 and V15 **over the text written by the previous fix
   round** introduces **no new failures** — not "few", not "only cosmetic ones". Zero.
3. That zero is itself measured by an agent **that wrote none of the text in that
   round**, and it states the frame it examined.

**Round N+1 exists only if round N produced failures.** If a fix round is clean on its
own output, the loop has converged and the ladder is green. If each round keeps
producing new failures, the ladder is telling you something true about the package and
the answer is not to stop auditing — it is that the package is not ready.

**What does NOT reopen the ladder:** corrections to the ladder's own REPORTS (they do
not travel), changelog entries, and this document. What DOES: any edit to the submission
package, to a claim-bearing surface, or to a rule this ladder enforces.

## CLOSE-OUT

- **V13. Ladder report in negative-verdict-review format**: every rung PASS/FAIL with evidence
  links, the claims table, the skeptic's report, and a single consolidated list of anything that
  changed during verification. No rung self-graded; the three pass-owners sign their own sections.

**The send gate**: all 15 rungs green (13 original + V14/V15, added 2026-08-10) → Sanaa's personal checks (she re-runs V1 and V3
with her own hands, reads V12) → Sanaa + Katie proofread the cover email → Katie sends. Nothing is
automatic at any point.

## Rungs executable NOW despite the park

V7 (both defects), V10 (cross-surface sweep), and V2 (the pre-registration table) do not require a
live send and harden the record whether or not the entry ever goes out. They may be run as normal
docket items. V1/V3/V4/V5 may also be run early as record-hardening. V6/V8/V9/V11/V12 bind to a
concrete submission package and wait for unpark.


> **Filename date note (chief, 2026-08-10).** The Pass 1/2/3 reports and several sibling
> records are named `…_2026-08-11…`. They were created on **2026-08-10**: I took the date
> from a dispatch header rather than from the clock and then specified those filenames.
> The files are not renamed, because five committed reports already reference them and a
> rename would break the citations that make them checkable — but a date in a filename is
> a sort key, so the discrepancy is recorded here rather than left to be discovered.

## Status ledger (chief-maintained) — rewritten 2026-08-11 from the close-out

*Rewritten because rung V13 found this table stale: it still described six rungs as "waits for
unpark" after they had executed, and carried no rows for V14/V15 at all. Verdicts below are read
from each rung's OWN record, and the confirmation column is the one that matters — a rung graded
by its own executor is weaker than one an independent pass reproduced, and this table now says
which is which instead of showing an undifferentiated column of PASS.*

| Rung | Verdict | Independently confirmed? |
|------|---------|--------------------------|
| V1 clean-environment re-score | **PASS** (twice) | YES — reproduced cold, same 20 digits, on a *different* numpy build |
| V2 pre-registration chain | **PASS** | YES — re-derived and strengthened by a second pass |
| V3 leakage assertions | **PASS** (one leg failed on re-run; fixed) | YES, twice |
| V4 duct traced end to end | **PASS** | YES — re-derived at 0.000e+00 deviation |
| V5 QCR provenance | **PASS WITH EXCEPTIONS** | YES — its own re-run overturned an earlier PASS; **2 gaps still open** |
| V6 compliance audit vs round 5 | **PASS** (was FAIL on currency) | **PARTIAL — one commit unread by anyone but its author** |
| V7 known defects killed | **PASS** — three, not the two we knew | YES — two more stale generator strings found later |
| V8 claims table | **FAIL — 8 claims** (corrections landed; re-verification in flight) | YES — a later rung reversed one evidence line and re-graded another |
| V9 prior-art completeness | **FAIL → FIXED** | YES — the struck sentence was then found still in the shipping archive |
| V10 cross-surface / mechanical sweep | PASS → FAIL → FAIL → **closed** | **NO — SELF-GRADED at the last step; independent check ordered** |
| V11 cold reproduction | **PASS** | YES — bit-for-bit, from the package alone |
| V12 skeptic's report | **DELIVERED** | PARTIAL — two circulating figures flagged |
| V13 close-out | **DELIVERED** | N/A — stated rather than hidden |
| V14 mechanical surface discovery | **PASS as executed** | YES — one classification changed by a later pass |
| V15 ladder-written text | **FAIL → FAIL → round 3 fixed → round 4 IN FLIGHT** | YES by construction (never its own author) |

**Consolidated change list: 64** — 11 to text that travels with the entry, 13 to public or shipping
surfaces, 9 to live code or generators, the remainder to the lab's own records. *That distribution
is itself the finding.*

**Round trend: 10 → 6 → unmeasured → unmeasured.** The close-out **refused to draw a four-point
line through two measured points**, and its reading is the honest one: severity fell faster than
count and the failure class migrated inward, away from the reader — but **every round so far has
produced at least one NEW-SHAPED finding, so a falling count is not the classes being exhausted.**

**GREEN REQUIRES**, per the termination rule: V8's re-verification, V10's independent confirmation,
V5's two open gaps, the six corrections that have not travelled, and a round-4 verdict of no new
failures. **The gate holds until every one of those closes.**

