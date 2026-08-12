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

## H3 — REPO SURFACE HYGIENE — **NOT STARTED**

- a. Nothing generated loose at root — pending [HAIKU]
- b. `.gitignore` rebuilt; **planted-file test** proving the sanctioned sweep
  helper still sees ignored paths — pending [SONNET], grader independence
  preserved even here. This matters more than it looks: `grep` in this lab is
  `ugrep --ignore-files` and honours `.gitignore`, so a `.gitignore` change can
  silently blind every sweep in the repo.
- c. Root README current, three sentences, no stale numbers (L-79) — pending
- **Verdict:** RED (not started).

## H4 — AGENT ALLOCATION RESPECTED — **NOT STARTED**

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

Green: H1, H5. Red: H2, H3, H4, H6.

**Phases 1–4 do not start on this signature.** One deliberate exception is
already running and is recorded rather than hidden: Katie designated the closure
challenge **ultra priority** in the same message as the order, and two closure
items were dispatched ahead of the gate — the submission-requirements audit
(landed, `3eb6ed39`) and the assembly of a shareable closure repository. P1.2
(the two Ladder V regressions) was also dispatched, because H1's commits are what
made those regressions visible and leaving them uncommitted-and-unfixed would
have left the tree in the exact state H1 exists to prevent.
