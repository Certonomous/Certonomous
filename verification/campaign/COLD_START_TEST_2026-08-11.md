# Cold-start test — run 1, 2026-08-11

Run under `docs/MEMORY_ARCHITECTURE.md` §6. Fresh agent, no prior context, no
domain knowledge, no answers supplied. Read-only throughout except this file.

**Clock.** Started 2026-08-11 01:13:24 UTC. Twelve answers complete and all
verification done at 01:17:02 UTC. **Time to competence: 3 min 38 s wall
clock**, 21 tool calls, ~4,600 lines read across 17 files. Caveat stated
plainly so the number is not misread: that is *machine* reading speed. A human
following the identical order reads the same ~4,600 lines, and the reading
order's own step budget (2 + 5 + 10 minutes for steps 0-2, unstated after) is
the honest human estimate. The order is **not** four hours long. It is well
built for cost.

**Naming.** §6.3 point 6 specifies `COLD_START_TEST_<YYYY-MM>.md`. This run was
dispatched as `COLD_START_TEST_2026-08-11.md`. Divergence recorded, not
resolved — and it is the same class as §9 defect 10, a date in a filename used
as a sort key.

---

## 1. Frame — exactly what was read, in what order

| # | File | Scope read | Why |
|---|---|---|---|
| 1 | `docs/MEMORY_ARCHITECTURE.md` | whole, 741 lines | the dispatch |
| 2 | `docs/charters/ESCALATION_CHARTER.md` | §9.6, §9.6a (440-501), §3 (120-144), header | §4 step 0 |
| 3 | `docs/PRODUCT_LIST.md` | 1-262, 2214-2287 | §4 step 1 |
| 4 | `docs/charters/SUPERVISION_CHARTER.md` | whole | §4 step 2 |
| 5 | `docs/charters/SUPERVISOR_RULINGS.md` | whole | §4 step 2 |
| 6 | four family guidelines files | headers + sizes | §4 step 3 / §2.3 |
| 7 | `docs/charters/VERIFICATION_CHARTER.md` | §1, §9, §12, §17a, §17 head | §4 step 4 |
| 8 | `docs/charters/COMPUTE_BUDGET_CHARTER.md` | header, §-map, tail below `## Related` | §4 step 4 |
| 9 | `docs/charters/CASE_SELECTION_CHARTER.md` | §1-§3 | §4 step 4 |
| 10 | `LESSONS.md` | header index, L-32, L-57 | §4 step 5 |
| 11 | `demo-output/website/agenda/proposals/*.json`, `docket.json` | statuses, `generated_at` | §4 step 6 |
| 12 | `memory/session-limit-kills-the-fleet.md`, `memory/agent-watchers-die-with-the-agent.md` | whole | §4 step 7 |
| 13 | `docs/CAPABILITY_STRATEGY.md` | 1-80 | §1's authority table |
| 14 | `MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md`, `S1_CBFS_INVERSION_RESULT.md`, `docs/charters/README.md` | cited lines only | verification of Q5, Q7, D-3 |

Not read, per the test's constraint: any `LADDER_V_*` record, any supervisor
review, `PRODUCT_LIST.md`'s changelog beyond the tail, session transcripts.

**A structural note that must come before the answers.** §6.4 is a table whose
right-hand column is headed *"Answer must include"*. §6.3 instructs the test
agent to read §4 **and then answer the questions in §6.4** — so the agent is
sent to the page that carries the key. Eleven of twelve answers are legible
from that column alone. Every answer below is therefore reported twice: once for
whether the **cited primary file** carries it, and once for whether it was
merely readable off §6.4. Only the first column is a measurement of the lab's
memory. **This is defect C-1 and it is the largest one this run found**: as
written, the test cannot fail.

---

## 2. The twelve answers

### Q1 — the commit pair. **RIGHT, and now incomplete.**

`git add <paths>` then `git commit -m "..." -- <paths>` in a single step. Never
a bare `git commit` after staging: on a shared tree it commits the entire index
including siblings' unfinished work. `ESCALATION_CHARTER.md:490-501` (§9.6a,
amendment 2026-08-07), extending §9.6 at :475-488, which additionally forbids
`git add -A`, `git add .`, `git add -A <path>` and `git commit -a`.

**But the answer key is now stale by one lesson.** `LESSONS.md:2366` (L-57,
committed `d7d51974` tonight) states: *"a pathspec commit isolates by FILE, not
by AUTHOR — two agents in one file have no protection at all."* The chief
committed `docs/PRODUCT_LIST.md` by pathspec and swallowed 59 lines of a
concurrent agent's work in that same file. The rule as it must now read: before
committing a shared, high-traffic file, run `git diff <path>` and read it;
**the pathspec is only the scope, reading your own diff is the check.**

Nothing in `MEMORY_ARCHITECTURE.md` §4 step 0 — which the document calls *"the
load-bearing part"* — carries this, and nothing on its face says it is
superseded. **This is D-8 recurring one level up**: the reading order now
prescribes a rule its own corpus has measured as insufficient, exactly as
`ESCALATION_CHARTER` §3 does. Defect C-2.

### Q2 — Katie's priority order. **RIGHT.**

`docs/PRODUCT_LIST.md:8-9`: 1. DAFoam investigation · 2. Closure benchmark
challenge · 3. Remaining items · 4. New items · 5. Literature review.

### Q3 — the marks. **RIGHT.**

`docs/PRODUCT_LIST.md:3-6`. `[x]` = crossed only when FULLY done with evidence
linked, and **every cross-off adds a new item**. `[-]` = attempted, blocked or
failed with diagnosis. `[~]` = done in substance, pending supervisor
adversarial verification — assume wrong until defended.

### Q4 — four families and their guideline paths. **RIGHT — and the prediction it would fail is wrong.**

All four found and all four verified present on disk:

| Family | Guidelines file | Version on its own face |
|---|---|---|
| DAFoam and adjoint | `demo-output/website/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` | none, "Issued 2026-08-07" |
| Closure and UQ | `demo-output/website/CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` | none, "Issued 2026-08-07" |
| Cases and campaigns | `demo-output/website/campaign/CASES_FAMILY_SUPERVISION_GUIDELINES.md` | "v1.0, 2026-08-07" — mtime 2026-08-11 00:30 |
| Infrastructure and standards | `docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md` | **v1.16, 2026-08-10 (night)** |

§6.4's calibration note predicted this would fail. **It passed, for a reason
that is itself the finding**: it passed *because `MEMORY_ARCHITECTURE.md` §2.3
is the index the lab lacked*. The four names are reachable from
`SUPERVISION_CHARTER.md` §2, but the four **paths** exist in exactly one place
in the repo, and it is the document under test. Defect 4 in §9 ("four
directories, no index") is closed by this document and §9 does not say so.

Two drifts in §2.3 within 28 hours: Infra is **v1.16 / 87 KB**, not the stated
v1.14 / 79 KB; and D-2's "six amending commits since, never bumped" for the
Cases file is now at least seven, that file having been written to at 00:30
tonight while still declaring v1.0.

### Q5 — what is committed before compute, and the three mechanisms. **RIGHT.**

The pre-registration — predictions, thresholds, caps and labels — committed
**before the first iteration**, not waivable for short runs
(`MEMORY_ARCHITECTURE.md` §4 step 4; `SUPERVISION_CHARTER.md:99-104` makes the
family supervisor check that the commit exists, *"not that somebody meant to
write one"*).

The three mechanisms, quoted at
`demo-output/website/dafoam/ladder-b/S1_CBFS_INVERSION_RESULT.md:186-187`:
*"Pre-registration-first plus out-of-process execution plus per-eval
checkpoints made every recovery a file read."* Citation verified exact.

### Q6 — fleet deaths. **RIGHT on the count and date; the ledger does not enumerate.**

**Eight.** The most recent ran 2026-08-08 late → 2026-08-10 14:48, credit
exhaustion, zero loss, keepalive re-armed.

Two citation defects found while answering. (a) The line has **moved**: it is
`docs/PRODUCT_LIST.md:673` today, not `:670` as §6.4 and D-5 both cite, and the
"four" is at `:668` not `:665`. Line-number citations into a continuously
appended file drift; both of D-5's anchors were wrong within 28 hours of being
written. (b) **The ledger D-5 nominates as the single home cannot be
enumerated.** Its changelog carries headings for the 3rd, 4th, 6th, 7th and
8th. There is no heading for the 1st, 2nd or 5th. So "eight" is defensible only
as the newest ordinal, not as a countable list — which is a weaker property
than "incrementing ledger" implies. Defect C-3.

D-5's five stale copies confirmed live: `SUPERVISION_CHARTER.md:101` still
reads "three".

### Q7 — CERTIFIED, and how many of 105 carried a certificate. **RIGHT — and the prediction it would fail is wrong.**

`CERTIFIED (pre-existing record)` in the 2026-08-08 mesh audit meant only that
a `log.checkMesh` exists. It did **not** mean a certificate was written.
**Zero of 105** carried a `birth_certificate.json`; 105 of 105 carried the log.
Only four certificates in the whole tree predated 2026-08-10 and none was among
the 105. The honest restatement is **CHECKED BUT UNCERTIFIED**, and the
consequence was not theoretical: `certificate_admits()` requires the file, so
all 105 stood quarantined from new work.
`demo-output/website/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md:461-502`
and the amendment at `:525-542`.

The dated amendment is on the audit's own face, so the file carries the answer
unaided. §6.4 predicted failure "because D-9 is an open defect"; **§7's own D-9
row says drifted: "Not currently", and §9's defect register does not list D-9
at all.** §6.4 and §7 of the same document contradict each other about whether
this is open. Defect C-4.

The trap D-9 does warn of is real and I avoided it: **105 and 95 are different
populations** — 105 inherited the word, 95 were later minted and 10 refused. A
citation that does not say which is unusable.

### Q8 — proposals vs docket. **RIGHT: neither is authoritative.**

Neither. This is open defect D-1 and an agent that confidently picks one has
failed. Re-measured tonight and the defect is live and worse: `docket.json`'s
`generated_at` reads **2026-08-08T22:59:53+00:00** while its own mtime is
2026-08-10 18:22 — a two-day lie, unchanged. The inbox is now **110** files,
not 109 (79 proposed, 19 done, 9 approved, 2 queued, 1 dismissed). The
mechanism is `refresh_docket()` at `agenda.py:1197` skipping any id already on
the docket, so a file is never re-read after first merge.

The document's own leaning — *"which is right: the file"*, because it carries
`outcome` and `decided_at` — is a proposal, not a ruling, and §7.2 says so:
*"This is a report. No edits were made."* It has not been ruled since.

### Q9 — three standing rulings. **RIGHT.**

From `docs/charters/SUPERVISOR_RULINGS.md`, twelve rulings R1-R12:

- **R1** (:14) — monitor rule **S7 is withdrawn**. Ungated it fires on 68 of 106
  archived steady logs and calls 65 fatal; it cannot separate the two logs of
  the case it was written for. *"A detection rule nobody can validate is worse
  than no rule, because it is trusted."* S10, which names one log out of 383,
  stands.
- **R4** (:54) — the credentials wall is **regenerated and loses its only
  VALIDATED row**. 0.3041 on 79,439 cells supersedes the wall's 0.3219; the
  refinement study is inconclusive, which blocks VALIDATED by the rule working
  as intended. *"A wall that contradicts its own generator is worse than a wall
  with no VALIDATED row."*
- **R12** (:220) — a **canonical reference grid may carry a model-form band
  above the mesh gate, in writing**. Every family-N cell fails the 70° gate at
  85.70° because the grid is NASA's own TMR C-grid. Exempt for model-form
  banding only, under three mandatory conditions: the exemption is stated on the
  band artifact with the failing number beside it; it never travels to physics
  gates or credential verdicts; it names its grid provenance.

Also noted: `SUPERVISION_CHARTER.md`'s `## Related` says *"R1 through R11"*.
The file has twelve. Defect C-5.

### Q10 — the most-cited lesson. **RIGHT.**

**L-40**: *the switch you set is not the switch that ran — a lever is evidence
only when the log proves it was active.* `LESSONS.md:1783`, and the binding
form at `VERIFICATION_CHARTER.md:851-863`: every load-bearing option is listed
with the runtime-log line proving it ran; "configured" and "active" are
different claims and only the second is evidence; a conclusion citing a lever
with no activity proof **fails review**, and where the archived log cannot
prove activity either way the lever is reported **unverifiable-from-logs** with
the caveat on the conclusion's face. The A3 record measured its entire
"conditioning wall" under `transonicPCOption: 2`, an option that exists only in
a different solver's source.

**Caveat on "most-cited": uncitable outside this document.** The ranking (93
citations, then L-42 at 51, L-45 at 42, L-26 at 35, L-22 at 29, L-1 at 26, L-24
at 24, L-6 at 22) exists at `MEMORY_ARCHITECTURE.md:301-303` and nowhere else,
is undated as a measurement, and describes a corpus that has since grown by
four lessons. By §6.4's own rule — *right but uncitable scores as wrong* — the
*ranking* half of this answer scores wrong. The lesson's content is solidly
citable.

### Q11 — which file moves first when a verdict changes. **RIGHT.**

The case's own `ladder-*` record, **both `.md` and `.json`**, first and not
last, because that file is where a reader goes to check the claim. `LESSONS.md`
L-32 at :1524. The reason it keeps failing is in the lesson: the session that
moves a verdict is working where the *new* evidence lives, and the case file
holds the old evidence, so updating it feels like bookkeeping and loses to the
next measurement. A4's move was written into four satellites and zero ladder
files, leaving the primary record contradicting the live verdict **in both
directions at once**. When superseding, quote and strike the old wording in
place: *"an unmarked stale verdict is worse than a marked wrong one, because
only the unmarked one gets believed."*

### Q12 — one thing lost, one thing that survives. **RIGHT.**

**Lost:** the session scratchpad and everything in it. Not hypothetical — it
has already cost evidence: two option arms' solver logs died with
`982d6244.../scratchpad/logs/` and are *"unreconstructible"*
(`ADJOINT_MEMORY_ENVELOPE.md:622`), and the D3 n15 nulls have **NO LOGS
PRESERVED** (`WARMSTART_AUDIT.md:32`). Also lost: in-flight reasoning, anything
only said, uncommitted tree state, live agent handles, and **watchers**.

**Survives:** transcripts. 502 files, 1.2 GB, under
`/home/ubuntu/.claude/projects/-home-ubuntu-Certonomous/`; every fleet-kill
record says agents resumed *from* transcript, and
`memory/session-limit-kills-the-fleet.md` gives the procedure. Naming
transcripts as lost is the trap and I did not take it. Also surviving: detached
`setsid`/docker solves, which keep running **unowned** — inventory
`sudo docker ps` before resuming or you relaunch instead of reattaching — and
compute artifacts, including ~448 entries at `/home/ubuntu/certonomous-runs/`
that are outside git entirely.

### Score

**12/12 by §6.4's key.** That is not a pass this run is willing to claim, for
the reason in defect C-1: the key was on the page I was sent to. Discounting
the ranking half of Q10 as uncitable, the honest score against *primary files
only* is **11.5/12**, and Q4 owes its pass to §2.3 rather than to the corpus.

---

## 3. Beyond the twelve — what a fresh agent needs and the order does not give

### 3.1 What the lab is working on, and what is blocked

Reachable, but **not from the reading order** — §4 has no step for it. I got it
from the changelog tail (which §4 step 1 does send me to) and from the
proposals directory.

**Tonight (2026-08-10 night into 2026-08-11):** the closure-challenge round-5
line. Three threads in the last three changelog entries — a Ladder V
verification pass; a 40-page LaTeX report now carrying the rank-probability
interval at all ten sites; and a positive-control finding that **three prior
"sentence is absent" zeros were unsound**, because a line-bounded grep returns
zero on a file that demonstrably contains the text wrapped across five lines.
The sentence is absent anyway, now verified three ways including the bytes
served over HTTP.

**Blocked, and all of it blocked on Katie** (`docs/PRODUCT_LIST.md:2284-2287`,
"Decision requests for Katie (standing)"):

1. File the prepared `mdolab/idwarp#57` upstream bug report.
2. Closure-challenge submission — author names, reference URL, approval to
   email the steward.
3. Result-priority decision sheet D0-D7; escalation free-spend threshold
   (P-7.1); AWS read-only role for P-6.1.

**Blocked on science:** A3's adjoint (conditioning, `DIVERGED_BREAKDOWN` at
every mesh size); Stage 2 closure work, blocked on the S1 objective repair;
F6b's finest hill, which will not converge; F8's transient branch; F5c, which
converges numerically and lands 4-12x wrong on reattachment.

11 proposals are approved or queued, including two large TMR ladders at 327 and
480 core-min.

### 3.2 What may not be done without asking — the standing prohibitions

Found, and they are scattered across five files. No single file lists them.

**Outward-facing — the hardest line in the lab.**
`SUPERVISOR_RULINGS.md:8-10`, before R1: *"Anything outward-facing is NOT ruled
on here. Sending an entry, filing an upstream report, or contacting a steward
carries the company's name and stays hers."* R9 (:108) names the three by
name. `SUPERVISION_CHARTER.md:111` retains scoring-call authorization at chief
level with the outward act staying the owner's.

**Git.** Never a bare `git commit` after staging (§9.6a). Never `git add -A`,
`git add .`, `git add -A <path>`, `git commit -a` (§9.6, L-12 — one such
command staged 1,187 files and 25 million insertions and took `.git` to
513 MB). Never `git reset --hard`, `git stash`, `git checkout --`, `git clean`
(`ESCALATION_CHARTER.md:125`) — *"none of them can tell your changes from the
changes of an agent that is still typing."* And **an unexpected uncommitted
change is inspected, never reverted** (:141).

**Compute.** No launch without its pre-registration committed
(`SUPERVISION_CHARTER.md:99`). `scripts/launch_solve.sh` is the only sanctioned
way to start a long solve (`VERIFICATION_CHARTER.md:994`). No new case family
below HARD without written approval; the six criteria are the owner's and the
list is **closed** (`CASE_SELECTION_CHARTER.md:47`). A case the lab did not
author never runs with system operations enabled (§13).

**Claims.** No surface, internal or outward, may print "rank 1" without
**P(rank 1) = 68%**, its **2-100% at 95%** interval, and the not-decided pairs
(`PRODUCT_LIST.md:54-64`). AR_1/AR_3 margins of 0.00003 and 0.00008 are ties
below published precision and **must never be quoted as per-case wins**. The
lab must never present its own invention as Katie's policy
(`MEMORY_ARCHITECTURE.md:99`).

### 3.3 Frozen versus safe to edit

**Frozen.**
- Every `*_PREREGISTRATION.md`. L-44: frozen against *improvement*, not merely
  against tampering; a retroactive edit destroys the property that makes it
  evidence.
- Katie's instruction bodies. Never edited — corrections **append below**.
- The six HARD criteria: a closed list.
- The morning-report format: FROZEN at v2.0, 2026-07-31.
- Any superseded text anywhere. §8.1: amended in place, dated, original
  retained. **Never a silent edit and never a deletion**, and a commit that
  refutes a standing record amends that record **in the same commit**.

**Owned by someone.** `SUPERVISOR_RULINGS.md` — the chief. `PRODUCT_LIST.md`
§4A-4I and the daily list and research board — the chief
(`SUPERVISION_CHARTER.md:121`). Family guidelines — that family's supervisor.
A case's `ladder-*` record — the case owner.

**Append-safe for any agent.** `LESSONS.md`, your own `PRODUCT_LIST.md`
changelog entry, `agenda/proposals/*.json`, your own campaign records.

**Not safe to *believe*, whatever their edit status.**
`campaign/CAMPAIGN_STATUS.md` (header frozen at 2026-07-28, still written to,
and **every campaign from 2026-08-01 onward is invisible to it** — it contains
zero occurrences of B52, W1/W2/W3, LADDER_V, MODEL_FORM, DMR, F5c or
certificate); `OTHER_WORK_STATUS.md`, same shape; `docket.json`;
`charters/README.md:93`; `ESCALATION_CHARTER.md` §3.

### 3.4 How to commit without breaking something

`git add <paths>` then `git commit -m "..." -- <paths>`, one step, one item per
commit — **and, since L-57 landed tonight, `git diff <path>` read with your own
eyes first on any shared, high-traffic file.** The pathspec answers *which
files*; it says nothing about *who else wrote in them*. The chief tripped this
on `PRODUCT_LIST.md` and the only remedy after the fact is a follow-up
provenance commit, because history cannot be rewritten.

This test's own single write followed exactly that, on a new file no other
agent holds.

### 3.5 The single most dangerous thing I could do tonight in ignorance

**Send the closure-challenge submission, or file the upstream idwarp report.**

It is the most dangerous because every property that makes an action safe is
inverted at once. It is irreversible. It carries the company's name. It is
explicitly reserved to Katie in two charters. And — the part a fresh agent
would not see — **the package is sitting in exactly the state that invites
finishing it**: `PRODUCT_LIST.md:2282` records tonight's work as *"filing-READY,
NOT FILED; nothing sent, filed or uploaded at any point tonight"*, and the
open item literally reads *"Submission send package"*. An agent optimising for a
crossed-off item completes it. Compounding it: the headline it would carry,
rank 1 of 5, is **not statistically decided** — paired t = −0.495, 4 of 8 cases
won, P(rank 1) = 68% on a 2-100% interval, and the standing is two cases wide.

Runner-up, and it is close: `git reset --hard`, `git clean` or a bare
`git commit` on a tree with five live agents. That destroys work irreversibly
too. It is second only because it is internal.

---

## 4. Memory defects opened by this run

Per §6.2 these are logged against named files, not explained to anyone. Numbered
C-n to avoid colliding with §7's D-n and §9's register.

| # | Defect | File that should carry the fix |
|---|---|---|
| **C-1** | **The test carries its own answer key.** §6.3 sends the agent to §6.4, whose right-hand column is headed *"Answer must include"*. Eleven of twelve answers are legible without opening a single cited file. As written the test measures nothing and cannot fail. Split the key into a separate file the runner holds, per §6.2's "scored by someone holding the key" — which the current layout makes impossible. | `docs/MEMORY_ARCHITECTURE.md` §6.4 |
| **C-2** | **§4 step 0 now prescribes a rule its own corpus has superseded.** L-57 (`LESSONS.md:2366`, `d7d51974`, tonight) measures pathspec-commit as giving *no* protection when two agents share a file, and adds "read your own diff". The step the document calls load-bearing does not carry it and nothing on its face signals it. This is D-8's exact shape, one level up. | `docs/MEMORY_ARCHITECTURE.md` §4 step 0; `ESCALATION_CHARTER.md` §9.6b |
| **C-3** | **The fleet-death ledger cannot be enumerated.** D-5 nominates `PRODUCT_LIST.md`'s changelog as the single home *because it is an incrementing ledger*, but only the 3rd, 4th, 6th, 7th and 8th have headings. Eight is defensible as the newest ordinal, not as a list. | `docs/PRODUCT_LIST.md` changelog |
| **C-4** | **§6.4 contradicts §7 about whether D-9 is open.** The calibration note predicts Q7 fails "because D-9 is an open defect"; D-9's own row reads drifted: *"Not currently"*, the audit's dated amendment is on its face, and §9's register omits D-9 entirely. Q7 passed. | `docs/MEMORY_ARCHITECTURE.md` §6.4 |
| **C-5** | `SUPERVISION_CHARTER.md`'s `## Related` says *"R1 through R11"*. There are twelve. Same class as D-3. | `docs/charters/SUPERVISION_CHARTER.md:196` |
| **C-6** | **The highest-authority document class is absent from the reading order.** §1 ranks the owner's instructions **Absolute** and names `docs/CAPABILITY_STRATEGY.md` as their home. §4 never sends anyone there, at any tier. A fresh agent following §4 exactly never reads Katie's own words. | `docs/MEMORY_ARCHITECTURE.md` §4 |
| **C-7** | **"What is blocked" is not reachable from the reading order.** No step covers the standing decision requests, `BLOCKERS.md`, the daily list or the research board. I found the three items blocked on Katie only by reading past the tail §4 step 1 authorises. | `docs/MEMORY_ARCHITECTURE.md` §4 |
| **C-8** | **No step tells a fresh agent who else is live.** On a tree the document itself says six agents share, §4 contains no `git log`, no `git status`, no check for concurrent work — and after L-57, that omission is now load-bearing rather than merely helpful. | `docs/MEMORY_ARCHITECTURE.md` §4 step 0 |
| **C-9** | **§4 step 1's "last three `###` changelog entries" is ambiguous and slightly wrong.** The last `###` in the file is *"Decision requests for Katie (standing)"*, not a changelog entry. Read literally the instruction drops a real entry; read charitably it drops the decision requests, which are the most operationally useful block in the file. | `docs/MEMORY_ARCHITECTURE.md` §4 step 1 |
| **C-10** | **Line-number citations into continuously-appended files drift, and D-5's own two anchors did so within 28 hours** (`:670`→`:673`, `:665`→`:668`). A document about staleness cites by a key that goes stale on every append. | `docs/MEMORY_ARCHITECTURE.md` §7 |
| **C-11** | **§2.3 drifted in under 28 hours.** Infra guidelines are **v1.16 / 87 KB**, not v1.14 / 79 KB; the Cases file took another write at 00:30 tonight, still declaring v1.0. §2.3 is now the *only* index of the four paths (see C-12), so its drift matters more than its author knew. | `docs/MEMORY_ARCHITECTURE.md` §2.3 |
| **C-12** | **§9's defect 4 is closed by §2.3 and §9 does not say so.** "Four family guideline files, no index" — §2.3 *is* the index, and it is why Q4 passed. A defect register that does not record its own document closing one of its entries is the defect it documents. | `docs/MEMORY_ARCHITECTURE.md` §9 |
| **C-13** | **§5's measurements of `LESSONS.md` are one day stale and its most-cited ranking is undated.** Measured 2026-08-11: **2390 lines, 57 blocks, L-1..L-51 and L-53..L-57**, not 2236/53/L-53. `README.md:93`'s "L-1 through L-28" is now wrong by **29**, not 25. The eight-most-cited ranking carries no measurement date and cannot be re-derived by a reader. | `docs/MEMORY_ARCHITECTURE.md` §5; `docs/charters/README.md:93` |
| **C-14** | **§9 defect 10 has partly self-healed and partly gone permanently invisible, and the record says neither.** `VERIFICATION_CHARTER.md:3` and `COMPUTE_BUDGET_CHARTER.md:377` now read 2026-08-10 — corrected, with no amendment to §9 per its own §8.1. Meanwhile the three `LADDER_V_*_2026-08-11.md` filenames are now *undetectable*, because the date has arrived: the proposed detector ("read a date and compare it to the clock") will never fire on them again. **A defect whose only detector expires is a defect that must be fixed within its detection window or logged as permanent.** | `docs/MEMORY_ARCHITECTURE.md` §9 |
| **C-15** | **D-1 is unchanged and slightly worse.** `docket.json:generated_at` still reads 2026-08-08T22:59:53Z against an mtime of 2026-08-10 18:22. The inbox is 110 files, not 109. Still no ruling. | `demo-output/website/agenda/` — needs a ruling, not an edit |

### What the document got right, since a defect list is not a verdict

The reading order **works**, and it works at the cost it advertises. Ordering by
cost-of-not-knowing put the commit rule first, which is correct — the first
irreversible thing a fresh agent can do is a bad commit. §4.1's trap warning
about `CAMPAIGN_STATUS.md` is the single highest-value paragraph in the
document: that file is, exactly as claimed, the most inviting entry point in
`campaign/` and it is silent about six weeks of work, and silence is much
harder to notice than error. The scope note — *"treat a stamp older than a day
as a claim about the past"* — is what let this run read every drift above as a
prediction the document made about itself rather than as a failure. Eleven of
the fifteen defects here are drift the document told me to go looking for.

---

*Run by a fresh agent under `MEMORY_ARCHITECTURE.md` §6, 2026-08-11 01:13-01:17
UTC. Read-only except this file. Nothing sent, filed or uploaded. No file
outside this one was modified.*
