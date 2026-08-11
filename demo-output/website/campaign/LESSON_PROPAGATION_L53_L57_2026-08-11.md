# Cross-family lesson propagation sweep, L-53 → L-57 (2026-08-11)

Zero core-minutes. Read-only on every family's records; this file is the sweep's
only write, and the routing below is routing, not editing.

Continues the series begun at `docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md`
§9 (L-41 → L-48, 2026-08-10). **Filed as a standalone campaign record rather than
as §14 of that document**, for the reason L-57 supplies: the infra guidelines went
through sixteen versions in one day and is among the highest-traffic surfaces in
the repo, and this sweep is cross-family rather than Infrastructure's own. A
pointer belongs there; the substance belongs somewhere a concurrent editor is not
also typing.

The question asked of every cell was not *"is the lesson relevant"* but **"does a
specific instance exist there right now, and can I find it or rule it out by
measurement."**

## 0. The premise, checked before the sweep ran (L-48)

The sweep was dispatched on the understanding that *the previous propagation pass
ran when the lesson book ended at L-52, and five lessons have landed since.*
**Half of that is wrong, and the wrong half is the count.**

Measured: the only propagation-sweep record in the estate is §9, its heading reads
**"L-41 → L-48"**, and its table has exactly **8 rows**, L-41 through L-48
(`/bin/grep -c "^| \*\*L-4[1-8]\*\*"` → 8). A wrap-safe search for any record
sweeping L-49, L-50, L-51 or L-52 returns none. **L-49 through L-52 have never
been propagated either.** So the debt is **nine** lessons, not five.

This sweep covers the five it was dispatched for. **L-49, L-50, L-51 and L-52
remain unswept and are recorded here as an open gap, not as a constraint** —
they are cheap to sweep and nobody has.

## 1. The matrix

**Key:** ● instance found · ○ ruled out by measurement · ✓ compliant exemplar ·
— not applicable

| | DAFoam / adjoint | Closure + UQ | Cases / campaigns | Infrastructure |
|---|---|---|---|---|
| **L-53** concurrent passes invalidate each other | ○ 9 candidates, all 9 hand-cleared | ● 2 uncited package surfaces · ✓ exemplar predating L-53 | ● 2 known-open · ✓ the only working machinery in the lab | ● **shipped bundle one file behind** · doctrine in **0 of 17** charters |
| **L-54** artifact vs agent predictions | ● decision-gated entry, 3 decider items unowned | ● rank table fuses the two classes | ✓ exemplar (with dating caveat) | ● no template field; **0 of 45** governance surfaces |
| **L-55** a summary that drops a conditional | ● gate on **1 of 4** scripts | ● whitelist on **3 of 8** loaders | ● lever echo on **0 of 2** records | ● S6 armed on **1 of 4** named surfaces · docket still asserts the refuted claim |
| **L-56** writing a rule joins its class | ○ scopes quantify over runs/rows, not text · ✓ 5 exemplars | ● checklist omits the document carrying it | ● the enumeration destroyed what it enumerated | ● 2 — register omits 3 copies in its own file; banner misplaces its own rule |
| **L-57** pathspec isolates by file, not author | ● unattributed same-file sweep | ○ lowest exposure in the repo, 1.31 commits/day | ● 1,575-file sweep, 2-line message · hazard register 9 days stale | ● documented instance · live always-dirty canary |

**16 of 20 cells carry a live instance. Three are ○ ruled out by measurement, one
is ✓ compliant.** No cell was marked "not applicable": every family turned out
structurally capable of hosting every one of these five.

**L-55 is the only lesson with an instance in all four families**, which is the
chief's prediction confirmed — *"the whole of X is in force" is a sentence shape
this lab writes often, and it was false the last time anyone checked.*

## 2. What each row rests on, and what I re-measured myself

**Every finding below was re-verified personally before it entered this file.** The
five rows were produced by delegated agents; a delegated null is a claim about the
delegate's reach, so nothing is relayed on a subagent's word. The re-measurements
are quoted inline.

### L-55 — the row the chief said to read hardest, and it earned it

- **Infrastructure. S6 cannot fire on most of the production it is claimed to
  cover.** `MONITOR_STANDARD.md` says *"S6 is wired and now fires on production
  runs"*, with a coverage table naming **Ahmed** among the surfaces. Re-measured:
  `arm_residual_gate` has **exactly one non-test call site repo-wide**,
  `head_engineer.py:986`, and it sits **inside `stage_case`** (defined `:957`, next
  `def` at `:988`). `/bin/grep -n "stage_case" sdk/workflows/ahmed_body.py`
  returns **nothing** — **Ahmed never arms S6.** Geometry-study rungs go through
  `clone_case_from` (`geometry_study.py:1369`) and are disarmed; the motorBike
  branch (`:1819`) is the only armed one. Armed: hump (`nasa_hump.py:575`), 2 of 4
  UQ engineers, one internal path. **So of four named production surfaces, S6 is
  armed on one unconditionally, one partially, one only on a tutorial case, and
  zero for Ahmed.** The shipping commit's own subject reads *"S6 is wired and
  fires on production runs for the first time."*
  Why no test caught it: every S6 test calls `arm_residual_gate()` directly on an
  object built with `HeadEngineer.__new__`, bypassing `__init__` and `stage_case`.
  **The tests prove the gate works when armed; nothing proves it gets armed.**
- **Infrastructure, second.** `agenda/docket.json` item `r1-monitor-stall-rule` is
  `status: done` with an outcome asserting *"S6 residual stall and S8 Courant
  excursion were already running"* — **the identical false claim L-55 was written
  about.** `MONITOR_STANDARD.md` was corrected in v1.5; the docket never was. It
  survived because the correction was applied to prose and **the docket is JSON
  that no prose sweep reads.**
- **DAFoam.** *"**Every validation is now a GATE**"* (`SUPERVISOR_FAMILY_REVIEW_2026-08-07.md:196`),
  parenthetically scoped to one file. Re-measured across the runs tree: **1 of 4**
  `build_maps*` scripts carries the tolerance and the non-zero exit
  (`W4-a4-discriminators/build_maps.py` → 8 tolerance refs, 1 `sys.exit(1)`; the
  `a35`, `io` and `upw` copies → **0 and 0**). Two campaigns consume
  `psi_on_np1.npy` from ungated scripts. The record states the truth 37 lines
  later under a different item — every clause true, the summary false.
- **Closure.** *"Every function that opens a ground-truth file asserts its case
  against a train/validation whitelist"* — the sibling protocol scopes the same
  sentence correctly to *"in `battery_common.py`"*; the guidelines dropped the
  scope. **3 of 8** truth loaders carry the assert. The uncovered one is the
  most-called truth loader in the repo.
- **Cases.** *"Every record carries the mechanical `levers_verified_active`; both
  meshes carry their birth certificates."* Re-measured: both records' keys are
  `['birth_certificate','cells','core_min','generator','level','mesh','prereg','run','timestamp']`
  — **0 of 2 carry the lever field; 2 of 2 carry the certificate.** A compound
  sentence with one true clause and one false one, and **the falsifying fact is
  written eight lines above it**: the smoke solve was refused pre-launch, so no
  solve ran, so no lever echo could exist.

**The transferable finding, and it held in all four families: the falsifying fact
was already written down** — 8 lines away, 37 lines away under another item, in a
sibling document with the correct scope, in the module's own docstring. Nothing
was hidden. The failure is a summary written from the same desk as its
qualification, minutes apart, by an author who had just proved the qualification
true.

### L-53 — a live defect in the artifact that actually ships

- **Infrastructure. The shipped bundle is one file behind, and the stale file is
  the L-53 specimen itself.** A writing pass fixed the missing attribution in
  `demo-output/website/benchmarks.html` at 01:36:17; the reading rung that
  certifies bundle↔tree parity had committed *"drift check PASS at 56 of 56
  byte-for-byte"* 69 minutes earlier. Re-measured by me: source **17,885 bytes,
  3 `Spalart`**; `dist/certonomous-demo/site/benchmarks.html` **17,612 bytes,
  0 `Spalart`**; and the tracked `dist/certonomous-demo.zip` member hashes
  **`bb97cb306901308b…`, identical to the stale directory copy.** So the uncited
  sentence is live in the artifact that travels. The lab flagged it 98 seconds
  after the writer and routed it to the bundle's owner — **clause 1 working** —
  and it is still open. **Not fixed here: `dist/` is outside this task's remit.**
- **Infrastructure, structural.** L-53's three clauses appear in **0 of 17**
  charters and standards. `VERIFICATION_CHARTER.md` §14 is the natural host and
  its rules never contemplate the lab's own machinery as author.
- **Closure ●, and a ✓ that predates the lesson by three days.**
  `CLOSURE_FAMILY_SUPERVISION_REVIEW_2026-08-07.md:282` records a provenance note
  on its own commit — a verification pass verifying its own act of writing,
  arrived at independently on 2026-08-07.
- **DAFoam ○, and the null is honest about its own reach.** 45 verification
  commits, 45 adjacency pairs, 9 corpus-intersection candidates, **all 9 hand-
  inspected and cleared** (same pass's own batch ×3, one agent appending its own
  review, five glob-arm false positives). The delegate also states what it could
  still miss, including that DAFoam has the largest file scope and the fewest
  audit-named records, so sensitivity is lowest there.

**A methodological result worth more than any single cell:** raw temporal overlap
is **not** a defect signature in this lab — it is the ambient condition, at
238 adjacent verification pairs in Cases alone. A detector keyed on adjacency
returns ~830–900 "hits" and means nothing. Every number above comes from corpus
intersection or live re-measurement.

### L-54 — the org-model has no home

- **Infrastructure.** **0 of 45** governance surfaces mention L-54 or mandate a
  per-prediction class label. The one place the lab writes down what every
  prediction must carry — the filed proposal
  `agenda/proposals/pre-registrations-carry-a-confidence-line.json` — enumerates a
  five-clause mechanic and **`class:` is not among them.** Verified: the file
  exists and reads as described.
- **DAFoam.** Re-verified against `docket.json` directly: `hlpw6-testcase1-coarse-grid-entry`
  is **`approved`** at 6,390 core-min while **three separate proposals asking a
  party to decide whether the entry can ever be sent are all `proposed`**
  (`w5-decide-what-cannot-be-submitted`, `w5-decide-what-cannot-be-sent-before-it-is-run`,
  `w5-rescope-the-high-lift-entry-on-physics`). **The lab's response to a task
  needing a decider has been to file three more items asking for one.** Compute
  stays approved; the gate stays unowned. That is L-54's third consequence,
  countable.
- **Closure.** `CLOSURE_RANK1_CAMPAIGN.md:415` ranks route A2 on a fused
  criterion — "expected overall gain" (artifact) and "build risk: unpriced DAFoam
  rebuild" (agent) — in one ordinal that feeds budget. Verified by reading the
  table. The same document handles the *artifact* half exemplarily 45 lines
  earlier, with a three-column candidate-cause/consequence/how-to-tell-apart table
  and the sentence *"The lab cannot currently distinguish these, and should say so
  rather than assume (a)"* — and gives the agent half no equivalent.
- **Cases ✓ with a caveat I am obliged to state, because the exemplar is mine.**
  The only file in the repo whose prediction table has a class column is
  `F6b_RELAXATION_INVARIANCE_PREREGISTRATION.md` — **written by this same session,
  four hours after L-54 landed, citing it by name.** It is compliance with the
  lesson, **not** evidence of prior practice, and it is listed here only as a
  reference implementation for the template question.

### L-56 — three of four instances are rule documents

- **Cases, the sharpest instance in the sweep: the enumeration destroyed the
  property it enumerated.** `IMPROVEMENT_DASHBOARD_2026-08.md` declares a corpus
  of *"every `.md`, `.json` and `.jsonl` under `demo-output/website/` and `docs/`"*
  and lists **9 run directories as orphans — "no record, ledger or docket entry
  names them"**. The dashboard is itself a `.md` under `demo-output/website/`, and
  it names all nine. **I re-measured this myself rather than take it on report:**
  `/bin/grep -rl -F <name> demo-output docs` returns **exactly one file for each
  orphan, and in every case it is this dashboard.** Sole namer, 9 of 9. The record
  also aims a recomputation instruction at itself, so a faithful re-run today
  returns **0 orphans, not 9** — the instrument now reports its own improvement
  target as already met.
- **Infrastructure.** `MEMORY_ARCHITECTURE.md:507` (defect D-3, *"a fact has one
  home"*) lists two copies of the lesson-corpus size and **omits three more inside
  its own file, all created by its own commit** (`:58`, `:371`, `:393`).
  Re-measured now: `LESSONS.md` is **2,431 lines, 58 lesson blocks, running to
  L-58**, while `:58` still reads *"L-1..L-53"* undated and `:394` still reads
  *"52 distinct numbers across 53 blocks"*. **Both drifted within hours** — the
  register's own §7.3 diagnosis realised by the commit that wrote the diagnosis.
- **Infrastructure, second.** `MONITOR_STANDARD.md`'s v1.7 banner says §3.1 gains
  the reach requirement; §3.1 does not carry it — it sits below `## Sources`,
  which the memory architecture already flags as *"where readers stop."*
- **Closure.** The family guidelines' §4 surface checklist enumerates every
  surface that must move when the entry of record changes, and **omits the rule
  document that carries §4** — which two external registers both classify as a
  claim-bearing surface. Not self-excluding in effect: it went stale and was
  caught by outside sweeps **twice**, on 2026-08-10 and again on 2026-08-11.
- **DAFoam ○, with the structural reason measured:** all 7 of its universal scopes
  quantify over **runs, cells, ledger rows and logs** — classes a record cannot
  join by being written. Five compliant exemplars cited, including a ledger audit
  that names a 22nd row appended while it ran and excludes it *with the reason*.

### L-57 — history is dirtier than the live tree

- **Cases.** A **1,575-file** commit whose entire message is *"Mesh ladder reads
  coarse to middle to production, the way a refinement runs"* swept three blocks
  into `NOT_PASSING_REGISTER.md`, none about a mesh ladder, two of them
  self-attributed in-band to *"the scheduled self-audit"*. No provenance follow-up
  exists. The largest un-attributed sweep in the history.
- **Cases, and this is the cheap high-value one.** The lab already has a register
  for exactly this — `campaign/SHARED_TREE_COMMIT_HAZARD.md` — and **it is nine
  days and one instance-class behind**: it holds only the cross-file variant and
  has never recorded the same-file variant or L-57.
- **DAFoam.** `DAFOAM_CASE_STATUS.md` carries 26 lines of family-supervisor text
  under a board-update commit message, and **neither of the two existing
  provenance follow-ups covers that file** — one explicitly says it covers
  something else.
- **Closure ○** on the lowest exposure in the repo (busiest file 1.31 commits/day
  against `PRODUCT_LIST.md`'s 15.0), with the same-topic and same-model blind
  spots stated rather than hidden.
- **A measured fact that governs how the whole lesson should be read.** Author
  attribution is **unavailable as an instrument here**: all 1,335 campaign commits
  carry the single `Ubuntu` identity. The only partial substitute is the
  `Co-Authored-By` model trailer, which is **absent on 19.7% of commits** and
  cannot separate two threads on the same model. Every collision count in this
  lesson is a lower bound, by construction.
- **Live exposure at the time of the sweep was zero shared prose files dirty** —
  and that number is nearly worthless: the canonical specimen's two commits were
  **53 seconds apart**, so a snapshot a minute later would have shown a clean
  tree. Recorded so nobody reads a clean `git status` as safety.

## 3. Routing — 22 items, owner and smallest correct action

Nothing below was fixed across a family boundary. Where this sweep's own family
could have acted, it still routed, because the sweep is not the owner of another
family's record.

| # | Lesson | Instance | Owner | Smallest correct next action |
|---|---|---|---|---|
| 1 | L-53 | Shipped bundle 1-of-56 behind; stale sentence live in `dist/certonomous-demo.zip` | **Infra** | Rebuild the bundle and re-run `check_bundle_drift` to zero. Already routed by the lab itself; this is an execution, not a decision. **Untouched here — `dist/` is outside this task's remit.** |
| 2 | L-53 | Clauses 1–3 absent from all 17 charters/standards | **Infra** | One subsection beside `VERIFICATION_CHARTER.md` §14, which already owns "an attribution is a claim about a file" and needs only *"and the author may be your own machinery."* |
| 3 | L-53 | `closure_challenge_submission_round5/MANIFEST.json` and `closure_challenge_round5_qcr_forward.json` uncited | **Closure** | Add the attribution the sibling `closure_challenge_round5_qcr.json` already carries. |
| 4 | L-53 | `benchmarks.html` in **0** closure supervision corpora | **Closure** | Add it to the family's sweep-coverage list. This is the reach fix that prevents recurrence of #1 and #3. |
| 5 | L-53 | `QCR_ACTIVITY_CHECK_2026-08-08.md` (23 QCR / 0 Spalart) born 3m23s inside a sweep's blind window | **Cases** | Apply the dated citation note the sweep applied to its other five records. |
| 6 | L-53 | `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` — three passes have now defensibly declined it | **Cases** | Needs an owner ruling, not a fourth verifier (L-54 consequence 3). |
| 7 | L-54 | 1 approved compute item at 6,390 core-min vs 3 unowned decider items | **DAFoam** | Collapse the three into one decision request in front of the one party who can answer. **Do not file a fourth.** |
| 8 | L-54 | `CLOSURE_RANK1_CAMPAIGN.md:415` fuses artifact gain with agent build risk in one ordinal | **Closure** | Dated addendum marking the two columns by class, leaving every number untouched; then apply the file's own §3.C.1 discrimination format to the build-risk row. |
| 9 | L-54 | No `class:` field in the one proposal defining the per-prediction schema | **Infra** | Amend `pre-registrations-carry-a-confidence-line.json` to add `class: artifact\|agent` — same one-line-per-prediction change to the same template. Splitting it into two proposals is how one gets adopted and the other does not. |
| 10 | L-55 | **S6 armed on 1 of 4 named production surfaces; Ahmed at zero** | **Infra** | Two parts: correct the standard's coverage table to the measured reach; and call `arm_residual_gate()` from `clone_case_from` too. **The missing test is the defect** — add one asserting every non-test path that runs a solver arms the gate. |
| 11 | L-55 | Docket `r1-monitor-stall-rule` still asserts the refuted claim | **Infra** | Dated correction beside the original. **Then sweep the docket for other closures whose outcome asserts a capability the audit refuted** — it survived because the fix went to prose and the docket is JSON. |
| 12 | L-55 | Truth-loader whitelist on 3 of 8 loaders | **Closure** | Either add the assert to the 5 uncovered loaders, or restate the guideline to the scope its own evaluation protocol already uses. |
| 13 | L-55 | `CLOSURE_METHODS_COMPARISON.md:321` cites a gate script with no automated call site | **Closure** | Restate the cell to say it is run manually. |
| 14 | L-55 | `GEN_ALT_PREREGISTRATION.md:134` — 0 of 2 records carry the lever echo | **Cases** | Correct to state no solve ran, so no record could carry it. The fact is already 8 lines above. |
| 15 | L-55 | `W3_DRAW_SCATTER_RULE_REPLAY_RESULTS.md:183` "all 17 records" = 17 restatements across 15 records, 1 since retracted | **Cases** | Restate with the measured shape. |
| 16 | L-55 | "Every validation is now a GATE" — 1 of 4 scripts | **DAFoam** | Restate to name the one file; the sentence 37 lines later already says it. Re-deriving the three copies from the fixed canonical is the durable fix. |
| 17 | L-56 | Closure §4 checklist omits the document carrying §4 | **Closure** | Add one line naming the document itself — or list it and mark it self-excluded **with the reason**. |
| 18 | L-56 | `IMPROVEMENT_DASHBOARD_2026-08.md` is sole namer of its own 9 orphans | **Cases** | One sentence: *"this record now names all nine; exclude it from next month's cross-reference."* **Do not re-run or re-triage** — the number was true at measurement time and the record is dated. |
| 19 | L-56 | `MEMORY_ARCHITECTURE.md` D-3 omits 3 copies in its own file, 2 already drifted | **Infra** | Add them to D-3's Copies column; better, replace the undated `L-1..L-53` with a cross-reference, per the file's own *"a fact that can change gets a ledger, not a sentence."* |
| 20 | L-56 | `MONITOR_STANDARD.md` banner misplaces its own reach rule | **Infra** | Either move the paragraph into §3.1 where a rule-author meets it, or correct the banner. One, not both. |
| 21 | L-57 | 1,575-file sweep with a 2-line message; `SHARED_TREE_COMMIT_HAZARD.md` 9 days stale | **Cases** | Add both as instances to the hazard register, and add the same-file edge citing L-57. **Highest-value item on that row — the register exists and is simply behind.** |
| 22 | L-57 | `DAFOAM_CASE_STATUS.md` swept text with no covering provenance note | **DAFoam** | One dated in-file provenance parenthetical naming the commit. **Do not rewrite history.** |

## 4. Self-application (L-56), declared rather than left to be derived

This sweep declares a universal scope — *"every instance of these five lessons in
these four families"* — so **the sweep is itself of that kind**, and two members
are named here rather than omitted:

1. **This file is a claim-bearing campaign record written during the sweep it
   describes.** It is in scope for L-53 (a writing pass creating unverified
   material), L-55 (it makes summary claims over conditionals), L-56 (it declares a
   universal scope) and L-57 (it is a commit into a shared tree). It is **not**
   self-excluded; it is offered for the next sweep to audit, and §0's premise
   correction is an instance of exactly the class it audits.
2. **The exemplar cited in the L-54 Cases cell is this same session's own
   pre-registration**, written four hours after the lesson it complies with. That
   is marked in place as compliance rather than prior practice, because a sweep
   that quietly cited its own author's work as independent evidence would be the
   defect it is looking for.

One member is genuinely excluded, **with the reason**: the five delegated rows
were produced by subagents whose transcripts are not repo files and cannot be
audited by a later corpus sweep. **Their conclusions are therefore not relayed on
trust — every instance in §2 carries a re-measurement I ran personally**, and the
three ○ nulls are reported with the delegate's own statement of what its
instrument could not see.

## 5. What the sweep says about the sweep

Three findings generalise past their cells.

**An absence needs an instrument, and the instruments failed first.** The L-53 row
reports that its first two detector generations recovered the canonical positive
control **on the wrong surface** and would have produced a clean-looking null in
two families; only the control forced the fix that surfaced the live instance. The
L-54 row reports its first lexicon recovering **1 of 3** known specimens, and its
label detector returning **21 false positives** before hand-adjudication. The
L-56 row planted a deliberately wrapped control and confirmed `/bin/grep -c`
returns **0** on both phrases while the normalised matcher returns all four. **In
every case the positive control changed the answer rather than confirming it.**

**Wrapped text is not a hypothetical.** The L-55 row measured the canonical
positive-control sentence itself straddling a newline: `/bin/grep -c "proposals is
in force"` returns 1, the normalised matcher returns 2. **The sentence L-55 was
written about is invisible to a line-bounded grep.**

**The vocabulary trap was avoided and the counterfactual measured.** The L-55 row
derived 21 of its 24 spellings from the repo's own idiom before writing its
matcher, and then measured what the naive approach would have cost: **0 of the 4
instances it found would have been caught by the L-55 example's vocabulary.** That
is L-49 defended in the field rather than cited.
