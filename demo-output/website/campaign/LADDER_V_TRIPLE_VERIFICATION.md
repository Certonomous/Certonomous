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

- **V16 (A16). The placement a guard cannot see because it is not a digit.**
  *(Chief ruling `8bdda313`, 2026-08-11, on the V8 fix round's own finding.)* V8's guard
  is **digit-anchored** — `rank 1 of 5`, `P(rank 1)`, `best overall number on the board`,
  all of them claims about *us*, all of them carrying a digit. The three defects the V8
  fix round closed on 2026-08-11 are none of those: *"The rank-3 entry, Wu & Zhang's
  SST-QCRC"* — Wu & Zhang being **rank 2** on the published board — twice, in the
  travelling document and on the lab record that seeded it, and a comparison that took a
  **position word** where the entrant's name belonged. Each states someone **else's**
  placement, and each is wrong in the direction that flatters
  us, because a wrong ordinal about a competitor is a rank claim about ourselves wearing
  a competitor's name — carrying none of the three things V8 requires, in a form V8 has
  no pattern for. Therefore: **every ordinal this lab pins on an entrant is checked
  against the published board, which is parsed from the benchmark's own README table
  rather than transcribed**, and the check runs over **whole text with whitespace
  collapsed**. *(**Corrected 2026-08-11 after the independent grade.** This clause used
  to justify whole-text matching by saying the parent instance on the lab record is
  defeated by its own reflow. **It is not**: that sentence breaks after
  `the rank-3 entry (Wu &`, which is inside the entrant's name and after the
  first-author surname the guard keys on — Wu & Zhang, **rank 2** — so a line-bounded
  reader catches it too. I found that against my own claim and it stood here uncorrected
  until the grade named it. The real instance is in
  `latex/closure_challenge_report.tex`, which reads "The published entry ranked" and then
  breaks before "second before round 5 — Wu & Zhang's SST-QCRC": there the break falls
  **between the ordinal and its rank word**, whole-text sees one placement and a
  line-bounded reader sees none.)* Guard:
  `scripts/self_audit.py::check_board_placement_words`; tests:
  `sdk/tests/test_rank_claim_surfaces.py`, whose test set **is** the three defects: the
  guard fires on all three as they were and on none as they now are. **Precision is a
  requirement of this rung, not a nicety** — a guard that cries wolf gets switched off,
  and then it guards nothing — so the rung fails if the check does not state its
  false-positive rate against a measured corpus and name the senses of the word it
  excludes. **And its stated REACH is a requirement too, added 2026-08-11 by the first
  grade of this rung**: the check must declare what its patterns cannot phrase, measured
  on held-out sentences rather than asserted, because a replacement whose stated reach is
  less honest than its predecessor's is the failure V16 exists to fix.

## WHEN THE LADDER IS GREEN — the termination rule (chief, 2026-08-10)

V15 creates a loop: every fix pass writes text, and ladder-written text must re-enter
the claims table. Without a stated terminating condition that recurses forever, and a
ladder that cannot finish is a ladder that never gates anything.

**The ladder is GREEN at a FIXED POINT, not at a clean sweep.** Specifically:

1. Every rung V1–**V16** carries a PASS. *(V16 added 2026-08-11; this line said
   V1–V15 until then, and is amended with the rung rather than left to go stale —
   which is the F2 defect the same round was closing an hour earlier.)*
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

## THE CONVERGENCE RULE — R-CONVERGE, R-DEPTH, R-VALUE (Katie, 2026-08-11)

The termination rule above says the ladder is green at a fixed point. It does not say
what stops a SINGLE RUNG. V16 is the proof that it needed to: the rung took **four grade
rounds**, each of which found something real, so none was waste — but a rung that can
always find one more thing has no stopping condition, and a gate that never closes is
not a gate. These three rules are the floor. They bind every rung from here, and they are
applied to V16 retroactively in its own record.

**R-CONVERGE.** Every rung declares, BEFORE its first grade, what CLOSED looks like: the
specific artifacts, the specific claims, the pass criterion. A grade may close exceptions
or open new ones — but a new exception **outside the declared scope** is filed as a
separate docket item, not appended to the live rung. Rungs close; the corpus of findings
grows elsewhere. The docket is `docs/DOCKET.md`.

**R-DEPTH.** Meta-depth cap. An instrument that checks an instrument that checks a claim
is depth 2, and that is the limit. Depth-3 work — auditing the auditor of the auditor —
is **filed, not executed**, unless a depth-2 finding falsified something published.

**R-VALUE.** Each grade round records what it found and what it cost. When **two
consecutive rounds return only findings that would not change an external reader's
belief**, the rung closes as **PASS WITH RESIDUALS**, and the residuals become docket
items. PASS WITH RESIDUALS is a real pass for the send gate; the residuals are real work
that is not this rung's.

These rules can end a rung. They cannot end it quietly: a rung closed under R-VALUE
names its residuals, and a finding filed under R-CONVERGE names the rung it was found in.
Nothing is dropped — the difference is only which queue it lives in.

## STRUCTURAL INDEPENDENCE — R-ISOLATE (Katie, 2026-08-11)

*"No agent verifies work it produced"* has been this ladder's rule since it was written,
and it has been enforced by **everyone being careful**. That is not enforcement. L-77 is
the proof: agents share one scratchpad, an author overwrote the grader's held-out evidence,
and no rule was broken by anyone — the paths simply collided. Independence that depends on
care fails the first time two agents pick the same filename.

**R-ISOLATE, four parts, all mechanical:**

1. **Every verification agent runs in its own worktree**, exclusive by construction. Not a
   convention about paths — a separate checkout, so a collision is impossible rather than
   discouraged. *Operationally: dispatch graders with worktree isolation, and never point
   two agents at one scratch directory.*

   > **THE CAVEAT, and it is not small: a fresh worktree does not carry gitignored files.**
   > This lab gitignores its large run archives and several evidence trees. An agent isolated
   > into a worktree to audit *text or code* is correctly isolated. An agent isolated into a
   > worktree to audit **evidence** is looking at a checkout where that evidence **does not
   > exist**, and it will report an honest, confident, empty result — the fail-open shape,
   > produced by the very mechanism adopted to make verification trustworthy. Combine that
   > with `grep` here being `ugrep --ignore-files` (L-75) and you have two independent ways
   > to get a silent zero over the same archives.
   >
   > **The rule:** worktree-isolate agents whose subject is tracked content. Agents whose
   > subject is run output, solver logs or any gitignored tree work in the main checkout,
   > with exclusive scratch paths assigned by the dispatcher instead. If you are unsure which
   > kind an agent is, have it print the count of evidence files it can see **before** it
   > reports what it found in them.
   >
   > **[AMENDED 2026-08-11, and the amendment was earned the first time this rule was used.]**
   > **The caveat above is not the only way an isolated grader ends up looking at the wrong
   > tree, and I wrote it as though it were.** The first agent dispatched under R-ISOLATE —
   > to grade V16 — found its worktree **18 commits behind the subject**: HEAD at `2c2c6a9a`,
   > with the **entire author round it had been sent to grade absent from the checkout.**
   > V16's subject being tracked content did not protect it, because the failure is not about
   > *what kind* of file is missing. **A worktree is a snapshot**, and a snapshot taken from a
   > stale base, or taken before the work landed, contains no signal that it is stale. Every
   > file the grader expected was present; they were simply the previous versions.
   >
   > It was caught only because `git log --oneline` disagreed with commit SHAs the dispatch
   > brief happened to quote. **Had the brief not quoted them, the grade would have been a
   > clean, confident, fully-evidenced assessment of the wrong code** — the fail-open shape
   > reaching the mechanism adopted to make verification trustworthy, for the second time in
   > one rule.
   >
   > **So R-ISOLATE part 1 now has two obligations, and the second is the dispatcher's:**
   >
   > - **The dispatch names the subject SHA.** Not "grade the current state" — the commit.
   > - **The agent asserts `git merge-base --is-ancestor <subject> HEAD` before executing
   >   anything**, and stops if it fails. One command, before the first finding.
   >
   > The general form, which is this lab's oldest lesson wearing new clothes: **an isolated
   > environment must prove it contains the thing it was isolated to examine.** Isolation
   > removes contamination and removes evidence by the same act, and it reports neither.
   >
   > **[AMENDED AGAIN the same day, on the assertion's FIRST use, and it caught the rule
   > rather than the tree.]** The next agent ran the ancestry assertion and it **failed** —
   > correctly, by its own terms, and **wrongly about the thing it stands for.** The subject
   > commit sat on the grader's unmerged worktree branch, so it was not an ancestor of `main`;
   > but the files under repair were **byte-identical** between `main` and that commit
   > (verified by blob hash, then behaviourally — the committed probes ran against `main`'s
   > guard at 12 disagreeing / 8 controls, zero drift). `main` reproduced the graded subject
   > exactly. What was missing was the *specification* of the work, not the *subject* of it.
   >
   > **Ancestry is a proxy for "this environment contains the subject", and the proxy fails
   > in both directions** — a branch cut from the subject's own base carries it and fails the
   > test; a merged-then-reverted path passes the test and lacks it. That is the same defect
   > as V16's own E2, where token distance proxies for the grammatical subject. **So pair the
   > ancestry check with a content check**: blob identity of the files under repair, or
   > execution of the committed probes with a drift check. The content check is what actually
   > established the position here.
   >
   > **And the gap this exposed is larger than the assertion.** R-ISOLATE gave the grader its
   > own worktree and then said **nothing about getting its output back.** The grade and its
   > twenty probes were committed to a branch nobody merged, so the author dispatched to
   > consume them could not see them, and the round stopped. **The fail-open shape is on both
   > ends of the handoff.** A grader's isolation is not complete until its findings are on
   > `main`; **merging the output branch is the dispatcher's obligation**, not an optional
   > tidy-up, and it belongs in the same breath as creating the worktree.
2. **Held-out sets are committed with positive controls BEFORE use**, and the **disjointness
   of author and grader samples is asserted by a test**, never trusted. A grader's sample
   that quietly overlaps the author's measures template reuse, which is L-66.
3. **A grader never reads the author's summary of a claim; it executes the claim.** Where a
   claim cannot be executed, the grade says **UNEXECUTABLE** — it does not pass on the prose.
   V16's fourth round is the argument: executing four inherited repairs found **two of them
   WRONG rather than unverified**, and both had summaries that read as sound.
4. **The chief's own record is never the presumed-correct side of a conflict.** When a grader
   and the chief disagree, the grader's execution wins until the chief executes something
   better. Tonight the chief was wrong four times in one reconciliation; that is data about
   which side to presume, not an apology.

**Why part 3 is the load-bearing one.** A summary is written by the person who believes the
work is done. Reading it transfers their belief, not their evidence. The two V16 repairs that
failed had comments explaining exactly why they were correct — one of them replaced a latent
false positive with a live false NEGATIVE, muting three true faults about a real entrant, and
its comment described the trade as a strict improvement. Nothing short of running it would
have found that.

## RULING — V16's E2 closes by measurement, not by a fifth discriminator (chief, 2026-08-11)

**Six grade rounds. Four discriminators for one problem. Each broke on a sentence nobody
had tried, and round 6's breaking sentence was round 5's own probe *minus one word*** —
delete the object relative `that` from *"the anisotropy tensor that Liu fits is rank 2"*
and the guard faults it again.

The grader's verdict on the pattern, which I am adopting: **a word list standing in for a
parse will keep producing a fifth sentence.** Building discriminator five is not a plan;
it is the previous four rounds with the numbers changed. R-CONVERGE exists to stop exactly
this, and it does not stop it by lowering the bar — it stops it by **changing the shape of
the claim**.

**The ruling.** E2 closes when the guard **states what it costs**, not when it stops
costing anything:

1. **Measure precision and publish it beside the four recall figures.** The guard has
   `_PLACE_REACH` (three rows) and `_PLACE_REACH_B`, all measuring *misses*. Nothing
   measures how often it binds an ordinal to an entrant in a sentence that is not a
   placement at all. That asymmetry is why six rounds of false FAULTs kept arriving as
   surprises: **the instrument had no way to report its own worst failure mode.** This is
   docket D20, and it is now E2's closing condition.
2. **Enumerate the false-FAULT classes honestly in the blind-spot list**, replacing the
   claim executed and falsified in round 6 — *"three known blind spots, none of which is a
   false FAULT"* — with the measured truth. Two of the three listed blind spots **do**
   produce false FAULTs, and there is a fourth that was not listed.
3. **A held-out set of non-placements** — linear-algebra ranks, dated history, quotations,
   cross-sentence adjacencies — committed with its inputs and recomputed like the recall
   sets, so the precision figure cannot go stale the way the reach figures did (L-79).

**What this ruling does NOT do.** It does not forgive the two regressions round 6 found,
which this rung introduced and must remove: the subject-NP fallback binding across
markdown structure (headings, list items and table cells end without punctuation, and
`_PLACE_CLAUSE` only cuts on `[.!?;:]`), and the boundary constant being unconditionally
uppercase, which turns every abbreviation-final period into a sentence boundary. Nor does
it forgive **L-76 re-opening**: the round added three absolutes and execution falsified all
three. A ruling that a claim may be *bounded* is not a ruling that a claim may be *false*.

**Why this is a closure and not a surrender.** A guard whose precision is unmeasured and
whose blind-spot list is wrong reads as more trustworthy than it is. A guard that publishes
`caught N of M, and falsely faults K of L, in these enumerated shapes` is **less impressive
and more useful**, and a reader can act on it. The four recall figures were always the
easier half to report; reporting only the easier half is what made six rounds necessary.

### 2026-08-11, later still — the closing round, by V16's author. NOT SELF-GRADED.

Executed against subject `5ef1fd1a` (ancestry OK; the two-path content diff against `HEAD`
`c12c7254` **empty**, so the subject is present unmodified). The rung is not signed off here
— its author may not — but the four deliverables are executed and the numbers are below so a
grader re-derives rather than re-reads.

**1. The precision figure exists, and it is the round's centre.**
`campaign/V16_PRECISION_SET.py`: **41 held-out non-placements**, every one a sentence in
which a rule-A pattern *does* match an expression — asserted at import, so the set cannot be
padded with sentences the guard never looks at — and in which no live placement is pinned on
a named entrant. **The guard falsely faults 20 of them (49%).** Five positive controls must
still fault and do, so the figure cannot be improved by switching the detector off. It is
recomputed from the committed sentences by the suite, like the recall rows, so it cannot go
stale the way they did (L-79), and it is interpolated into the verdict line and into BASIS
beside the four recall figures. **The set is adversarial and not representative** — it is
weighted toward the shapes that have already broken — ~~so 20 of 41 is a worst case on hard
sentences, not a corpus rate~~; the corpus rate is the live sweep in the same verdict.

> **[CHIEF RULING, 2026-08-11, commit `02e941c4` — the struck clause above is FALSIFIED, and
> it is struck rather than deleted.]** Round 8's author flagged that this sentence still read
> as a live claim and could not touch it, because I had told it not to edit this document.
> The ruling it asked for: **a falsified claim inside a dated round record is history only if
> a reader can see that it is.** This one could not — it sat in running prose with nothing on
> its face marking it, so a reader scanning the ladder would take it as current. That is the
> W-5 shape and the fact that it lives in a dated section does not cure it.
>
> **What falsified it:** an independent blind sample measured **19 of 25 (76%)** against this
> 49%. A "worst case" is a bound, and another honest adversarial set is worse, so the hedge
> written to prevent overstatement **overstated, in the optimistic direction.** It is the
> fourth absolute this rung produced.
>
> > **[AMENDED 2026-08-11 by grade round 9, commit `067caac0`. The RULING STANDS; the
> > statistic I cited for it does not, and it was mine to check.]** This paragraph originally
> > read *"27 points worse — Fisher exact p = 0.040, with the grader's lower 95% bound above
> > this point estimate."* **That comparison pairs two different admission predicates.** The
> > author's set admits a sentence on a raw pattern match; the grader's admits on
> > `len(_placements(...)) > 0`, which applies the homonym list and the subject-head
> > discriminator *after* the match and is strictly narrower. Scored under a **common** rule:
> >
> > | scored under | author | grader | spread | Fisher 2-sided |
> > |---|---|---|---|---|
> > | as published (loose / strict) | 20/41 = 49% | 19/25 = 76% | 27 pts | p = 0.040 |
> > | raw match on both | 20/41 = 49% | 19/26 = 73% | 24 pts | p = 0.075 |
> > | `_placements` on both | 20/**28** = 71% | 19/25 = 76% | **5 pts** | p = 0.763 |
> >
> > **The published pairing is the only one of the four combinations that is not internally
> > consistent, is the one that maximises the gap, and is the one that produced the p = 0.040
> > this ruling quoted.** The author's 41 lose 13 sentences under the grader's predicate — all
> > true negatives, so the numerator stays 20 and the *rate* moves from 49% to 71%.
> >
> > **Why the strike survives anyway, and this is the whole reason the ruling is not
> > withdrawn: 76% exceeds the author's rate under EVERY common rule.** "Worst case" is a
> > claim that no honest sample exceeds 49%, and one does, on any consistent scoring. What is
> > falsified is the **comparison narrative** — that the only variable was who built the set —
> > and the significance claim resting on it. The conclusion never needed the p-value.
> >
> > I quoted a statistic without checking that its two arms were scored the same way, in a
> > ruling whose subject was a claim that failed for want of checking. That is this rung's
> > **fifth** L-76 absolute and the first to sit in the reader-facing verdict rather than in a
> > comment.
>
> **Why struck and not deleted** — L-76's own discipline: keep the falsified claim, stop
> asserting it. Deleting it destroys the record of what was believed and when, which is the
> thing that makes a fix-round auditable. `_FALSIFIED` in `scripts/self_audit.py` now carries
> this sentence as its fourth entry, with a test that reddens **both** if someone reinstates
> it as a claim and if someone erases it.

**2. The falsified blind-spot claim is gone.** *"Three known blind spots, none of which is a
false FAULT"* is replaced by the four measured classes, two of them the ones that claim
denied and one of them the reduced relative that was not on the list at all — and by the nine
classes of the precision enumeration, each generated into the verdict with its count. A test
asserts the string cannot come back.

**3. Both regressions are gone, by execution, with their controls.** The subject-NP fallback
no longer binds across a heading, a list item or a table cell: `_place_flatten` preserves a
markdown structural boundary as one newline where the plain collapse wrote a space, and
`_PLACE_CLAUSE` cuts on it. Same length either way, so no offset moves. The punctuated twins
stay silent and **both round-5 false negatives still fault**, so this is not a deletion of the
fallback. The boundary constant no longer makes every abbreviation-final period a sentence
end: `_place_sentence_break` asks whether the period ends an abbreviation, the two real wrong
placements after `et al.` fault again, and the six round-5 boundary shapes stay silent.
Measured cost, stated: the exception adds exactly **one** false FAULT to the precision set
and buys back **one** missed real placement — 23 of 41 falsely faulted before, 20 after, with
controls going from 1 missed to 0.

**4. L-76 closes again.** All three absolutes the previous round added are gone as absolutes
and present as bounded claims with their executing tests named. Sweeping my *own* added lines
found two more of the same kind and both were bounded before commit.

**Probe counts.** Round 6: **12 of 24 disagreeing → 7**, all twelve controls still passing;
the seven are the E2 shapes the ruling permits to stand **knowingly accepted**, and they are
counted in the precision figure and named in the blind-spot list, which is the proviso.
Round 5: **0 of 20**, unchanged. All four recall figures unchanged. The live verdict is
unchanged — WARN on the same two known quotations of docket D3.

**What a grader should attack first**, since a rung's author naming its weakest point is
cheaper than a grader finding it: the precision denominator is *mine*, built with the pattern
list in hand, and a set built by someone else will give a different number — which is the
same criticism the reach rows already carry and the reason they name who built each one.

## CLOSE-OUT

- **V13. Ladder report in negative-verdict-review format**: every rung PASS/FAIL with evidence
  links, the claims table, the skeptic's report, and a single consolidated list of anything that
  changed during verification. No rung self-graded; the three pass-owners sign their own sections.

**The send gate**: all 16 rungs green (13 original + V14/V15, added 2026-08-10; + V16, added 2026-08-11) → Sanaa's personal checks (she re-runs V1 and V3
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
| V15 ladder-written text | **FAIL → FAIL → round 3 fixed → round 4 fixed → round 5 PENDING** | YES by construction (never its own author) |
| V16 rank-claim guard reach | opened 2026-08-11 by the fix round that found the guard blind → **BUILT the same night** (`862d2cff`), chief ruling `8bdda313` assigning it back to the finder | **NO — SELF-GRADED by construction; the builder is the finder and may not sign it off** |

**Consolidated change list: 64** — 11 to text that travels with the entry, 13 to public or shipping
surfaces, 9 to live code or generators, the remainder to the lab's own records. *That distribution
is itself the finding.*

**Round trend: 10 → 6 → unmeasured → unmeasured.** The close-out **refused to draw a four-point
line through two measured points**, and its reading is the honest one: severity fell faster than
count and the failure class migrated inward, away from the reader — but **every round so far has
produced at least one NEW-SHAPED finding, so a falling count is not the classes being exhausted.**

**GREEN REQUIRES**, per the termination rule: V8's re-verification, V10's independent confirmation,
V5's two open gaps, the six corrections that have not travelled, **V16's guard-reach rung — now
built, and owing the independent check its own builder cannot supply** — and a round of V15
returning no new failures. **The gate holds until every one of those closes.**

### 2026-08-11 — V8's fix round closed five, and opened a rung by finding the guard blind

V8's five corrections landed with the leaderboard verified at the frozen commit **and re-derived by
re-running the benchmark's own scorer**, rather than transcribed from any report. The ordinal sweep
that A15 demanded then found the wrong ordinal was **not a single stale sentence but a family**: the
travelling instance, **its parent in the sentence family that seeded it**, and a third of the same
shape carried by a **comparative rather than an ordinal** — a placement claim containing no rank
word at all, three sections from the passage that states the claim correctly.

**This is why V16 exists.** The rank-claim guard shipped earlier tonight is **digit-anchored**, and
**would not have fired on any of the three.** The fix round declined to widen it in the same pass —
correctly, since new guard patterns are unverified code entering the ladder — and raised it as a
rung instead. Recorded as **L-61**: a guard anchored to the spelling of the example that prompted it
is a regression test wearing a detector's clothes, and its green reads as coverage.

**And then the chief assigned the rung back to its finder** (ruling `8bdda313`, 2026-08-11) and it
was built the same night: `scripts/self_audit.py::check_board_placement_words`, with **22** tests in
`sdk/tests/test_rank_claim_surfaces.py`, at `862d2cff`, of which **21** fail against unmodified HEAD.
*(This sentence said 21 and 20 until the grade re-counted it;
`TheWordFormGuardIsRegisteredTests` carried five tests and I had counted four. The claim's
structure — all but one fail, and the exception is deliberate — survives; the arithmetic did
not, and a rung whose whole subject is a wrong number about someone else does not get to carry
a wrong number about itself.)* What it does: parses the leaderboard from
the benchmark's **own README table** rather than transcribing it, so a permuted table flips the same
sentence from clean to faulted; matches over **whole text with whitespace collapsed**, proven by a
control pair differing only in a line break that returns 1 fault against 0; and takes the three
defects as its **test set** — firing on all three as they were and none as they now are. Measured
before shipping rather than asserted after: **zero false positives**, against a first crude
instrument that flagged 18 of 107 with 17 artifacts. Its second rule was cut down to almost nothing
on the same evidence — the broad form returned 11 hits of which 11 were the idiom
*"in the first place"* — because **a guard that cries wolf gets switched off, and then it guards
nothing**. *(The counts behind that rate were originally quoted here as "421 expressions, 63 bound,
on a 111-file corpus". The grade could not reproduce the 111 from any recorded selection rule and
was right not to: **the number had no method written down anywhere**. The rate stood — the grader
re-derived it over a wider frame and found zero outside the declared class — but a figure without a
method is a citation to nothing. The check now prints its own denominator **and its selection rule**
in the verdict: placements counted in the surfaces that name a board entrant, with both counts
shown, so the figure reproduces from the frame line instead of from a sweep nobody recorded.)*

### 2026-08-11, later — V16 graded PASS WITH EXCEPTIONS, and the exceptions closed

`campaign/V16_GRADE.md`, by an agent that wrote none of it. The instrument was found sound and
its **label found to overstate it** — four of the six exceptions were the rung's own stated numbers
and stated reach failing to keep up with what its author already knew. Closed in order:

1. **The declared blind-spot list omitted the guard's dominant blind spot.** The verdict named
   relational comparatives and archive members and said nothing about *any placement phrased
   outside its patterns* — an admission **the digit-anchored guard it supersedes makes about
   itself**. Measured on held-out sentences pinning a wrong placement on a named entrant: the grade
   missed **40 of 45 (89%)**, and my own independent set of 46 put it at **37 (80%)**. The verdict
   now leads with it and ends with *GREEN HERE IS NOT COVERAGE*.
2. **Nine more families taken** — `ranked Nth`, the verbal placements, `Nth overall`, `the Nth
   entry`, `position N`, `top the board` — each measured for false positives before it was kept,
   and one (`No. N`) measured, found firing on a journal issue number in a bibliography, and
   **taken back out**. Precision still zero. *(**The miss rate originally published here as
   "80% → 30%" is withdrawn as a headline.** The second grade showed it pairs an* **outside**
   *measurement of the old patterns with an* **inside** *measurement of the new ones — different
   samples, unstated. On the grader's original 45, invented blind before the widening existed, the
   widened guard misses* **53%**, *not 30%. The honest headline is that one fixed set measured at
   both ends:* **89% → 53%** *(**STALE 2026-08-11: recomputes today to 89% → 44% and 91% → 93%. These were correct when written at `9f6d8a41` and the CODE MOVED UNDER THEM at `db096bb7`, when rule B widened. Not unrecomputable history — the shipped verdict generates the current figures.**)***.** *A third set built adversarially with the pattern list in hand gives
   96%. The check now generates all three, with provenance, from one table rather than carrying
   them as prose.)*
3. **The parse can no longer crash, and three more ways to mis-parse it silently are closed.**
   *(This item read "can no longer crash, mis-parse silently, or fault correct prose" and* **that
   was false when written** — *the second grade found three of fifteen adversarial READMEs still
   returning an unchecked board with no warning. The root cause was one sentence: the repair
   anchored to* a *heading and took the first table after it, and never asked whether what it read
   was a leaderboard.)* A surname with a regex metacharacter used to raise out of this check and
   take *every other check in the file* down with it; a numbered table anywhere in the README moved
   an entrant's rank; two entrants sharing a first-author surname dropped one and then faulted
   correct prose about the survivor; a numbered legend *between* the heading and the board, an
   earlier heading also saying *leaderboard*, and **a blank line inside the board table** each
   silently changed the board. **The heading now plays no part**: every block of table rows is a
   candidate, and a candidate is a leaderboard only if it has a rank-headed first column, a column
   naming the entrants, at least two rows, ranks reading exactly 1..N, and unique usable surnames —
   with exactly one qualifying, or the detector goes OFF and says why. **It can still be fooled by
   a decoy that satisfies all of that, and now says so** rather than claiming it cannot.
4. **A literal survived inside the thing built to remove literals**: the ordinal vocabulary was a
   hard-coded 1–5, so on a longer board every placement past fifth was unmatched. It is derived
   from the parsed board now, with a margin, so an ordinal naming a position the board does not
   have is itself a fault.
5. **The retracted whole-text justification** was corrected in the shipped comment and in the rung
   text above, and **the real instance found**: see below.
6. **The counts** — 22 tests and 21 failures, not 21 and 20 — and the 111-file corpus, which had no
   recorded selection rule and is replaced by one the verdict states.

**The finding the grade was not looking for, and the honest measure of this rung's reach.** A live,
committed placement pinned on a named entrant, **wrapped across a line break**, in the same sentence
family as the defect that opened V16, on the **LaTeX source of a shipping report** — and
**correct by luck**, not by any instrument. I verified it against the parsed board myself rather
than taking it from the grade: Wu & Zhang are rank 2, "ranked second before round 5" is true, and
**the text is left exactly as it is**. What changed is that the guard reaches it now — and that
sentence turns out to be the real justification for whole-text matching, because its break falls
between the ordinal and its rank word.

**Two things it still cannot do, recorded here and not only in the code.** Relational comparatives —
*ahead of*, *behind*, *trails*, *leads*, *next-best* — need both operands resolved and cannot be
checked against a single board rank. And the second rule **cannot tell use from mention**: a record
that quotes one of these defects in order to name it is flagged by it, which is why that rule is a
WARN on a lab record and a FAIL only where a surface travels — and which caught **my own test
fixtures** the minute the patterns widened, in the very file that documents why one must not write
them out.

### 2026-08-11, third pass — re-graded PASS WITH EXCEPTIONS (two, down from six), both now closed

`campaign/V16_GRADE.md` §8, by the same independent grader, **verifying each closure by breaking the
thing that holds it** rather than by reading its description. Five of six closed cleanly; the two
that remained had the same shape as the first six — *the instrument is sound and a claim about it
overstates it* — and both are closed above: the parse's three surviving silent mis-parses (§8.1/E2)
and the reach headline that paired two different samples (§8.1/E4). With them, four incidentals:
the mirror of my own particle fix (`Reissmann Jr.` keyed on `jr`); **rule B, which had not been
widened at all** while nine families went to rule A, so *"80% → 30%"* described one of two rules
and was worn as a statement about the check; the count and the miss rates **hardcoded in three
surfaces each with no test that they were still true** — the literal problem one level above the
one the previous pass had just removed, now derived from the compiled pattern and one provenance
table; and **L-75**, confirmed not to touch this guard, whose `git ls-files` frame reaches the
**6,938 tracked-but-gitignored files** a `grep -r` here cannot see (verified in this pass, not
inherited).

**A coordination hazard I caused, recorded because it is mine.** The grader's held-out set lived at
the shared scratchpad path `…/scratchpad/heldout.py`; **I overwrote it with my own set at 04:11**,
under a docstring reading *"My own held-out set"*. No evidence was lost — the grader's 45 are
recorded in §4 of the grade — but a grader's file being silently replaced by the author's, in a lab
whose whole method is independent verification, is the hazard rather than the outcome. It also
meant disjointness of the third set had to be asserted mechanically instead of trusted. My working
files now live in a uniquely-named subdirectory; **agents share that directory and can destroy each
other's evidence without either noticing.**

### 2026-08-11, fourth pass — graded a third time; both commissioned exceptions close, two new ones found

`campaign/V16_GRADE.md` §9. Both were closed and **verified by breaking them**, including four
purpose-built decoys against the parser's own concession — which held and was called *"exactly as
wide as it says… the first sentence in this rung's history that describes a limit instead of denying
one."* The two new exceptions were **neither of the things the grader was sent to check**:

1. **`_published_board` said "NEVER raises", and raised.** `read_text(encoding="utf-8")` sat inside
   `except OSError`, and **`UnicodeDecodeError` is a `ValueError`.** One non-UTF-8 byte in the
   benchmark README took down *the entire `self_audit` run* — every sibling check with it. **It is
   the second time the same crash class has been fixed in this one function**, the first being a
   regex metacharacter fixed by escaping: *a fix for one exception type, which is what invited a
   second through a different type.* So the fix is a **boundary, not another `except` clause** — the
   read and parse moved into `_parse_published_board`, free to raise, behind a wrapper nothing can
   escape. Its scope is deliberate: only the third-party file we do not control is wrapped, because
   a check that catches everything everywhere hides its own defects. Verified by planting a byte and
   running the whole audit: **PASS 13 / WARN 9 / FAIL 9, exit 0.**
2. **The reach table was stale by the commit that installed it.** Rule B was widened and the table
   shipped in the same commit, so four rule-B sentences moved from missed to caught and nothing
   re-measured — and the table then **contradicted its own rule-B row** about those same five
   sentences. Recorded 24/45 and 43/45; measured **20/45 and 42/45**. The error was **pessimistic**,
   which is why it is a defect of derivation and not of candour. *The figures had been made generated
   so they could not drift between surfaces — and generation stopped one level short of the
   measurement.*

**And the class is now closed rather than the instance.** The grader committed both its held-out
sets as a runnable file carrying no faults of its own; I committed my 46 beside it the same way.
**Every published figure now recomputes from sentences that live in the repository**, with a test
that reddens on any disagreement, a test that the adversarial set's three positive controls are
still caught, and a test that neither evidence file is itself a corpus of faults. The `before`
column is history against patterns that no longer exist, cannot be recomputed, and is marked so.
**Storing a measurement whose inputs are not in the repository is what made all three of these
stale.**

Folded in with them: the itemised failure list **read unconditionally where it is conditional** (a
qualifying decoy beside an invalidated real board yields the decoy, silently); `_BOARD_WHO_COL`
matched **unanchored**, so `Filename` and `Hostname` counted as naming the entrants; and the live
**operating margin is now printed in the verdict** — the real README has 2 table blocks and 1
qualifies, so **the guard sits one third-party edit from DISABLED where it used to sit one edit from
WRONG.** Stated rather than fixed: rule B's widening faulted **six new places on lab records,
including the grade document that commissioned it**, so *"each measured across the repository before
keeping"* did not hold for the frame the repository had. From here a measurement in that file names
the moment it was taken.

**L-76, applied as ordered and executed rather than read**: 36 absolute-shaped words across 17
surfaces — docstrings, BASIS, REMEDIES, verdict line — enumerated by regex rather than by eye and
each falsified by construction. **All hold.** The one apparent failure was my own probe using
one-letter surnames, which the parse rejects by design.

**THE L-76 PATTERN, THREE GRADES RUNNING, ONE FUNCTION.** *"Can no longer mis-parse silently"*;
*"does not return a board it is unsure of"*; *"NEVER raises"*. **The instrument was sound at every
step and a sentence about it was wrong at every step** — and the third time, the sentence was
backed by a real crash with a twenty-check blast radius. An absolute in this lab is an unverified
claim until someone executes it.

**The rung is BUILT and GRADED THREE TIMES, and every round of exceptions is closed by the same
agent that built it** — so the re-grade is owed to someone else. Under A15 no agent grades its own
work, and that applies to a fix round exactly as it applies to a build.

**The round is not scored PASS.** It fixed what it was sent to fix and it opened a new-shaped
finding, which under the termination rule is exactly what a **non**-fixed-point round looks like.
Four rounds running have now produced at least one new shape. The V15 round that audits *this*
round's output has not yet run, so the count for round 5 stands at **unmeasured**, not zero — and
the distinction is the whole content of the termination rule.

