# HANDSHAKE H — 2026-08-12

The gate for the full-day autonomous order. **No phase starts until every item
below is green.** An item without an executed check is not done; prose is not a
check. One line per item: check command, output, verdict, timestamp, executor.

Signed off by: [ORCH]. Archived at end of day; re-runs fresh tomorrow.

---

## Model mapping, recorded because the order names versions this harness aliases

| order's name | dispatched as | role class |
|---|---|---|
| claude-fable-5 | `fable` | [FABLE] research / scientific writing |
| claude-opus-4-8 | `opus` | [OPUS] engineering, execution, launches |
| claude-sonnet-4-6 | `sonnet` | [SONNET] grading, sweeps, cold reads |
| claude-haiku-4-5 | `haiku` | [HAIKU] hygiene, organization, bookkeeping |

All agents run in this session's harness and inherit one config dir. Meter note:
the weekly limit terminated a three-agent fleet at ~2026-08-12 00:00 UTC (reset
stated as Aug 14 06:00 UTC); dispatch is functioning again as of 16:0x UTC, so
capacity exists but the wall is real and slates are sized against it (C3).

---

## H1 — WORKING TREE CLEAN — **GREEN**

Two agents died mid-work on 2026-08-11 leaving work uncommitted **in the shared
main worktree** — the ESCALATION_CHARTER §9.6c hazard, live.

- **Executor:** [OPUS]. Separation established by file mtime and **corroborated
  by content**, not timestamps alone: Agent A's diff adds only `_board_pin_date()`
  and `_PLACE_ADMISSION` and says nothing about the six-entry board; Agent B's set
  contains no test or guard changes.
- **Check:** `stat -c '%y %n'` on every dirty path; `git diff` on the shared
  `docs/DOCKET.md` to confirm its diff was D48/D49 only.
- **Output:** `0c7b968d` (Agent A — V16 round 10: D49 settled on one admission
  predicate; D48 BLIND TO item 12). `5c9c63fb` (Agent B — P(rank 1) 68% → 50.2%
  on the live six-entry board; best-on-board 4 of 8 → 2 of 8).
- **Independently re-executed by the committing agent, who was not the author:**
  `probability_of_rank.py` reproduces 50.2% exactly; the best-on-board collapse
  recomputes to 2 (survivors `alpha_05_4071_4048`, `alpha_05_4071_2024`), both
  losses to Tian/Buchanan/Hickel/Dwight on the two `alpha_15` hills.
- **Residual dirty:** `sdk/.filming-keepalive` only — dated 2026-08-11 00:03,
  a full day before either agent, belongs to neither, deliberately untouched.
- **Verdict:** GREEN. 2026-08-12 ~16:00 UTC.
- **Recorded hazard:** a third agent committed `025d59a6` into the same worktree
  during H1's window. It touched none of either author's paths so nothing was
  misattributed — but the collision was real, and it is why every commit in this
  order is single-step pathspec.

## H2 — HISTORY CLEANED FOR FIRST PUSH — **BLOCKED ON A DECISION, NOT ON WORK**

**The order's ~150 MB target is not reachable.** Measured 2026-08-12 at
`dd623e33`, and the headline re-verified independently by [ORCH] after an
internal inconsistency was found in the drafting agent's arithmetic:
`du -sh .git` = **2.0 GB**, `size-pack` = **1.82 GiB**, worktree = 17 GB.

The reclaimable material is small and the rest is evidence: numpy/h5py **wheels
(21.1 MB)** and **superseded PDF drafts (~14 MB)** are safe to purge — not
evidence, redownloadable or superseded. Everything else large is cited:
**meshes 361.7 MB** (computational inputs), **solver logs 33.6 MB** (convergence
proof), **reference papers 152.4 MB** (prior-art base). A safe purge frees
**~35 MB**, landing at ~1.96 GB.

*(The draft's "removing mesh/logs/papers saves only ~395 MB" against a 547.7 MB
blob subtotal is uncompressed-blob vs packed-size accounting, not an error in the
conclusion — checked before this row was written.)*

**Secrets sweep: CLEAN, and its positive control was stated** — no `.env`,
`.pem`, `.key`, no hardcoded tokens; the one external address, `rmcconke@mit.edu`,
is the challenge steward's published contact. Absolute internal paths in docs
remain to be generalized before any push (hygiene, not security).

**The decision for Katie, and it is a real fork:** purging to the stated target
would mean deleting the reproducibility audit trail — the logs that prove
convergence and the meshes that let a result be recomputed. The three honest
options are (i) accept ~1.96 GB as the cost of a repo that carries its own
evidence, (ii) move meshes and logs to Git LFS, or (iii) **do not push this repo
at all and share curated artifacts instead** — which is what
`Certonomous_closure_challenge` already is, at **504 KB**. Option (iii) solves
the problem H2 was opened to solve, without the history surgery.

- a. [HAIKU] MOVE_MAP of blobs to purge — **DONE**, `docs/MOVE_MAP_HISTORY_PURGE.md`
- b. [OPUS] `git filter-repo` on a **fresh mirror, never the live tree** — pending
- c. [OPUS] fresh-clone verification, `.git` < ~150 MB, full suite green — pending
- d. [HAIKU] before/after sizes + clone result to docket — pending
- e. **PUSH GATE — BLOCKED.** No written pre-authorization from Sanaa exists in
  this file, so `git push` requires her one-word approval of (d). Additionally
  `gh` is **not installed** and no GitHub credentials are configured on this box,
  so no push or repo creation is technically possible from here regardless.
- f. Daily-push rule takes effect only after (e) clears.
- **Verdict:** RED (not started; gated).

## H3 — REPO SURFACE HYGIENE — **AMBER: a and c done, b deferred by design (`06a9a710`)**

- **a. Root inventory — DONE, moves deliberately deferred.** 13 directories and 19
  root files classified. Ten `mbc_retry*.err/.log` (2.2 KB total) are tracked and
  **unreferenced** — the only true strays. `badFaces` (7 bytes) is already
  untracked and ignored. Everything else at root is either source or is **cited in
  a durable record**: `uq_batch.log`/`.err` are referenced by `docs/HANDOFF-UQ.md`
  and are therefore evidence, explicitly marked DO NOT SWEEP so a later agent
  cannot undo the finding.
- **b. `.gitignore` NOT rebuilt — deferred deliberately, drafted instead** to
  `docs/GITIGNORE_PROPOSAL.md`. `grep` in this lab is `ugrep --ignore-files` and
  honours `.gitignore`, so editing it while agents sweep changes what each of them
  can see **with no error raised anywhere**. The planted-file test by [SONNET]
  runs against the proposal in the quiet window.
- **c. Root README — VERIFIED CLEAN.** Swept for stale quantitative claims against
  L-79 and specifically against the movements of 2026-08-11 (~~P(rank 1) now 50%~~
  *— struck 2026-08-14 under D59: a bare figure, and in the present tense. Measured
  at 50.2% on 2026-08-12 over a 400,000-draw case-level bootstrap, interval 0–97%
  at 95% by double bootstrap, four of six pairwise comparisons **not statistically
  decided**; re-verified unchanged against the live board at 2026-08-14T21:01Z,
  `94307129`* — board carrying six entries as of the 2026-08-11T23:33Z retrieval,
  entry NOT submitted). The README asserts none of them; its only
  numbers are a standards reference, a hash algorithm, a solver version and a port.
  Positive control stated: `grep -r "mbc_retry"` reaches tracked content and
  returns only the `.gitignore` line.

> **Trap recorded for whoever executes H2, found by cross-reading two independent
> reports.** `numpy-*.whl` (15.9 MB) and `h5py-*.whl` (5.2 MB) are the history
> purge's single largest safe reclaim AND are **tracked at HEAD**, not merely
> historical. Purging them from history without untracking them at HEAD
> reintroduces them on the next commit — a rewrite that appears to succeed, then
> silently undoes itself. Neither report could see this alone; it is only visible
> where the root inventory and the MOVE_MAP overlap.

> **[ORCH] error, recorded rather than quietly fixed.** H3's brief instructed moves
> into a gitignored `evidence/` while forbidding `.gitignore` edits — two
> instructions that cannot both be satisfied. The agent stopped and asked instead
> of improvising, which is the correct behaviour and the reason the contradiction
> surfaced as a question rather than as a bad commit.

## H4 — AGENT ALLOCATION RESPECTED — **AUDITED, `10cf7f21` — FAIL on H4a, with rulings**

[SONNET] audited by listing and execution, not memory. Full commands, outputs and
positive controls in `docs/H4_ALLOCATION_AUDIT.md`.

**H4a — FAIL, and the condition is live.** One `git worktree list` entry; multiple
agents working in it concurrently. The 2026-08-11/08-12 collision was independently
reconfirmed from `git log`/`reflog` rather than taken from this file's account.

> **[ORCH] RULING on the severity, because two readings of the same fact differ
> materially.** The grader observed two live `claude --resume` processes in the
> main worktree and called it a shared-worktree violation. Adjudicated at
> `5d3df8c6`: PIDs 1630 and 1834 are **siblings** (both PPID 1584, started 30 s
> apart), not a session and its child, and **only one transcript is being
> written** — `64b13819...jsonl` at 16:33, every other session file stale since
> 15:22. So the violation is REAL in the form that matters (agents do share one
> worktree, which is what the order forbids) but the alarming reading is NOT
> supported: **no second chief session is dispatching in parallel.** That
> distinction is worth stating because this lab has previously had two chief
> sessions issue duplicate briefs, and the remedy for that is nothing like the
> remedy for this. The actual cause here is structural — subagents inherit the
> parent's working directory — so the fix is worktree isolation at dispatch, not
> session hygiene.

**H4b — PASS on documents, UNKNOWN on rosters.** All four family guideline
documents exist. Whether every live agent has a family owner is UNKNOWN: no roster
file exists and OS processes carry no family attribute. Reported UNKNOWN rather
than converted into a PASS.

**H4c — PASS, with a live discrepancy confirmed.** 142 `.done`, 0 zero-byte, 4
`.done.INTERRUPTED`, 0 `.partial`, 0 orphan solvers — each zero backed by a stated
positive control. **D52 independently reconfirmed by two methods** (`find` and
`glob.glob`, run separately): the 146-vs-142 mismatch is live, not historical.

**H4d — tmux down as expected; meter UNKNOWN.** The weekly-limit termination has
**no corroborating on-disk artifact** beyond this file's own prose, and the grader
correctly refused to certify it. That is the right verdict: [ORCH] asserted it
from session memory, and session memory is not evidence.

**H4e — MIXED, and it caught a real contradiction before it executed.**
- The `Co-Authored-By: Claude Opus 5` trailer is **fixed harness boilerplate, not
  a per-commit model record** — so model attribution is NOT verifiable from git,
  and any future check that tries to read it would be an identity, not a control.
  This retires the method, not just the instance.
- **`SUPERVISION_CHARTER.md` §5 requires long-form technical writing to go to
  Opus. The order assigns charter/LESSONS drafting (H6) to [FABLE].** These
  cannot both be honoured.

> **[ORCH] RULING on the charter conflict.** Katie is the principal and her order
> of 2026-08-12 governs the execution of this order; [FABLE] keeps the scientific
> writing. But a standing charter is not silently overridden — it is superseded in
> place, dated, with the original struck and kept, which is this lab's own rule for
> every other falsified claim. **The amendment resolving the conflict will be
> drafted by [OPUS], per the charter's existing §5**, so that the disputed rule is
> not used to settle the dispute about itself. Katie rules on the standing version.
> H6 does not execute until that amendment lands.

- **Executor:** [SONNET], by listing rather than memory.
- e. Model-to-task conformance against the table above.
- **Verdict:** RED (not started).
- **Pre-declared for the report, so the grader does not have to catch it:**
  [ORCH] executed work directly BEFORE this order arrived — the auto-stop repair
  (`025d59a6`) and the state reconciliation of H5. Both were done in response to
  Katie's direct instruction *"first, make sure the instance stops dying"*, which
  preceded the fleet order. Under the order's allocation rule this would be an
  ORCH violation; it is recorded here rather than argued away. No ORCH execution
  has occurred since the order arrived.

## H5 — STATE RECONCILIATION CURRENT — **GREEN (executed pre-order by [ORCH])**

- **Collectors:** 142 `.done`, **zero** zero-byte, **zero** `.partial` — the
  atomic-write repair of E2 held. Newest record 2026-08-08 02:11; nothing captured
  since, and no solver process is running, consistent with compute being
  unauthorized. No solves were in flight at the outage.
- **E2's four empties** were correctly renamed `.done.INTERRUPTED` — marked, not
  deleted, as the row instructed. **Consequence nobody re-checked:**
  `scripts/dispatch_queue.py:114` globs `*.done` and now enumerates **142**, while
  `docs/PRODUCT_LIST.md` cites a **146**-record corpus in five places, including a
  measured statistic ("of 146 completion records, 3 carry a rank declaration").
  Filed for the docket — this is the D50 shape: a published denominator and a
  recomputed one that are two different samples.
- **Interrupted work:** re-queued, not restarted — both dead agents' output was
  recovered and committed under H1 rather than re-run.
- **Auto-stop marker:** touched; the gate itself was repaired (`025d59a6`).
- **Spend header:** [HAIKU] — pending.
- **Verdict:** GREEN on reconciliation; spend header outstanding.

## H6 — STANDING RECORDS CURRENT — **NOT STARTED**

- [FABLE] drafts / [HAIKU] files: LESSONS, conventions, charters through last
  night (W-1..W-5, L-74..L-79 applied); PRODUCT_LIST reflects reconciled state;
  no present-tense state claims without commit anchors (W-5).
- **Verdict:** RED (not started).

---

## Gate status: **NOT SIGNED**

Green: H1, H5. Amber: H3 (a/c done, b deferred by design), H4 (audited; H4a FAIL
recorded with rulings). Red: H6. H2 is **blocked on a Katie decision, not on work** —
its target is unreachable and the alternative is already built.

### Phase 1 — Ladder V: **GREEN at `1b982ae1`**, recorded here because the gate's
### own premise was that P1.2 could not be skipped.

Full suite **115 passed in 612.93s**, from 2 failed / 112 passed. Closed **without
moving the frozen pin and without altering the guard by one character.**

**Three claims in the chief's brief did not survive execution, and the agent
overrode all three** — which is §2's *"the chief's own record is never the presumed
-correct side of a conflict"* working as designed, not a mishap:
1. **Rule B has no proximity window at all.** The chief's "9 within ±300 characters
   vs 3 outside" implied near-misses and possible guard false-faults. `_place_unnamed`
   is a bare regex with **no adjudication clause at any distance** — a probe with the
   entrant's name one character away still faults. The ±300 split described the
   corpus, not the guard, and there was no adjudication to make. Filed as **D54**:
   the fault message claims more than the rule tests. Filed, not retuned — retuning a
   detector so the author's own prose passes is how a guard gets tuned to a number.
2. **The anonymous set was 4, not 3, and the missed one was the generator.**
   `sdk/scripts/build_benchmarks.py` WRITES `benchmarks.json` and `wall/wall.json`.
   Repairing those two copies without it buys exactly one build cycle — and the
   generator's own comment records that same trade being made at round 5 and caught
   by V7 on 2026-08-08. **The chief's measurement counted outputs and missed the
   thing that regenerates them.**
3. **Cause (b) never drove the FAIL.** The submission draft is WARN-severity and not
   travelling; the failure was three travelling rule-B faults.

**D48 was repaired in prose, through the guard's OWN adjudication clause** (naming
Reissmann's placement on both the live board and the pin), and the addendum states
outright that this **restores D48's latency rather than ending it** — the next
live-board placement faults identically. That treadmill is recorded so it is not
rediscovered. The structural fix is **filed as D55**, four options costed, behind a
gate: it must not be built until a held-out set of *live-board* sentences exists,
because every current set is defined against the very function the change would
replace (L-74).

**Mutation proof, done the hard way:** reverting only the generator literal reddened
the new test while both neighbouring assertions stayed green — proving neither
existing test could see the generator, which is precisely the gap it closes.

**Flagged, pre-existing, NOT from today's work:** `dist/certonomous-demo/site/*.html`
are stale from well before today and still read `RANK 1 OF 5` and `P(rank 1) = 68%`.
`dist/certonomous-demo.zip` is a **tracked shipping artifact**, so this is a
distributable surface carrying two figures now known false.

**Phases 1–4 do not start on this signature.** One deliberate exception is
already running and is recorded rather than hidden: Katie designated the closure
challenge **ultra priority** in the same message as the order, and two closure
items were dispatched ahead of the gate — the submission-requirements audit
(landed, `3eb6ed39`) and the assembly of a shareable closure repository. P1.2
(the two Ladder V regressions) was also dispatched, because H1's commits are what
made those regressions visible and leaving them uncommitted-and-unfixed would
have left the tree in the exact state H1 exists to prevent.
