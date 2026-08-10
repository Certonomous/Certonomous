# Certonomous Memory Architecture

Version 1.0, dated 2026-08-10. Written on Katie's dispatch of 2026-08-10, section F.

This document says what the lab remembers, where each kind of fact lives, who
writes it, what dies at session end, and the order a fresh agent reads files in
to reach correct current state. It is a map of the record, not a new record: it
adds no fact that is not already somewhere on disk, except where it says
explicitly that a fact has no home.

It answers a failure this lab has hit repeatedly and hit four times this week:
facts that live in conversation instead of files, and records that go stale
without anyone noticing.

**Scope note.** Everything below was measured against the tree at
2026-08-10 21:00-21:10 UTC. Counts drift fast here: the tree went from 17
uncommitted paths to 2 in the eight minutes it took to survey it, and 185
commits landed on 2026-08-10 alone. Every count in this document is stamped.
Treat a stamp older than a day as a claim about the past.

---

## 0. Provenance, and three premises that did not survive checking

This document was dispatched with five pieces of motivating evidence. Four
verified; the checking changed two of them, and the corrections are more useful
than the originals, so they are recorded here rather than quietly dropped.

| Premise as dispatched | Verdict | What is actually true |
|---|---|---|
| A finding proven at `fe121af2` sat unreconciled for **NINE DAYS** | **Overstated** | 7 d 15 h by the tightest anchor (`fe121af2` 2026-07-31 06:53Z to review `9d72e197` 2026-08-07 22:03Z); 7 d 19 h to the correction. Never nine. |
| An agent noted **"chat is not the record"** (`a5a28a40`) | **Not in the repo** | The phrase appears in zero files and zero commit messages. The commit's own words are *"goes into the record rather than staying in a message"*. The lab's real idiom is L-32's *"satellites are not the record"*. |
| **Eight fleet deaths** in a week, recovery worked **only because** pre-registrations preceded compute | **Count right, cause incomplete** | Eight is correct and the window is ~4 d 5 h, tighter than "a week". But recovery rested on three things, not one: pre-registration-first, out-of-process execution, and per-eval checkpoints (`demo-output/website/dafoam/ladder-b/S1_CBFS_INVERSION_RESULT.md:186`), plus transcript resume. Pre-registration is what made scientific *loss* zero; it is not what made *recovery* work. |
| **Two agents' transcripts became unreachable**, taking their working context | **False as stated** | No transcript has ever become unreachable; every fleet-kill record says agents resumed *from* transcript. The real loss is different and worse for this document's purposes: **one session scratchpad died and took two option arms' solver logs with it, unreconstructibly** (`demo-output/website/dafoam/ADJOINT_MEMORY_ENVELOPE.md:622`). Separately, two agents lost *watchers* with explicitly zero work lost (`docs/PRODUCT_LIST.md:559`). |
| A "certified" count meant something weaker than it read, and **105** records inherited the word | **True** | Exactly right. See §7, duplicate D-9. |

The nine-day number is worth one more sentence, because it is this document's
subject in miniature. It is wrong in **four files at once** — `LESSONS.md:1752`,
`demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md:207`,
`demo-output/website/campaign/F5bc_unsteady_statistics.md:104`, and
`docs/PRODUCT_LIST.md:571` ("NINE DAYS AGO") — because it was written once and
copied three times. A lesson *about* stale records propagated an unchecked
number by the exact mechanism it warns about. That is the case for §7.

---

## 1. What persists, and where each kind of fact lives

Twelve classes of durable fact. "Authority" means: when two files disagree,
this is the one that wins.

| Fact class | Home | Who writes | When | Authority |
|---|---|---|---|---|
| **Owner's instructions** | Verbatim in the record that acts on them; `docs/CAPABILITY_STRATEGY.md` for the 2026-08-08 directive | Katie writes; chief transcribes verbatim and annotates below the rule | On dispatch | Absolute. Never edited — corrections append below, per L-44 |
| **Standing rulings** | `docs/charters/SUPERVISOR_RULINGS.md` (R1-R12) | Chief supervisor, under quoted delegation | Per ruling, when a queued decision blocks work | Highest after Katie. Bounded: nothing outward-facing is ruled here |
| **Standing rules / law** | `docs/charters/` — twelve files, see §2 | Unstated in 9 of 12; chief by inference | On incident, not on schedule | Charter text wins over any restatement |
| **Charter decisions awaiting Katie** | `docs/charters/PROPOSALS_OPEN.md` (C-1..C-4, P-N.M) | The lab; explicitly flagged as proposal, never as her policy | Per charter revision | Not law until answered |
| **Lessons** | `LESSONS.md` (L-1..L-53, no L-52; plus P1-P5, D12) | Any agent, after something actually went wrong | On incident, same day | The narrative is here; charters cite by number |
| **Family standing rules** | Four files, four directories — see §2.3 | Family supervisor (`SUPERVISION_CHARTER.md` §2.1) | Per incident in the family | Binds that family only |
| **Open work / checklist** | `docs/PRODUCT_LIST.md` §4A-4I | Chief ("supervisor-maintained", line 1) | Continuously | The list is Katie's; maintenance is the chief's |
| **What happened** | `docs/PRODUCT_LIST.md` `## Changelog` | Chief, and agents appending their own entries | Per closing | The lab's narrative spine |
| **Proposed work** | `demo-output/website/agenda/proposals/*.json` (109 files) | Any agent | On filing | **Contested — see D-1.** The inbox is currently ahead of the docket |
| **Costed queue snapshot** | `demo-output/website/agenda/docket.json` (264 records) | `sdk/chief_engineer/agenda.py` | On `save_docket()` | **Stale by design failure — see D-1** |
| **Evidence: pre-registration** | `demo-output/website/campaign/*_PREREGISTRATION.md` | The agent that will run it | **Before any compute.** Frozen thereafter, per L-44 | Frozen. A retroactive edit destroys it as proof |
| **Evidence: results** | `demo-output/website/campaign/*_RESULTS.md`, `*_runs/` | The agent that ran it | On completion | Primary. Satellites are not the record (L-32) |
| **Provenance / verdicts per case** | The case's own `ladder-*` record, `.md` **and** `.json` | Case owner | **First, not last**, when a verdict moves (L-32) | The case file wins over every summary of it |
| **Prices** | `docs/charters/COMPUTE_BUDGET_CHARTER.md` (unit, defaults); `est_core_min` / `measured_core_min` per proposal | Filing agent; charter for the unit | On filing, on measurement | Charter defines the unit; the record carries the number |

### 1.1 Two record classes the charter corpus creates but never indexes

`docs/charters/README.md` lists nine charters and its "Related standing
documents" omits both of these. A fresh agent following the index will not find
them:

- **Family supervision guidelines** — created by `SUPERVISION_CHARTER.md` §2.1,
  four instances, no common home (§2.3).
- **Negative-verdict reviews** — created by `VERIFICATION_CHARTER.md` §16, one
  artifact per instance, e.g.
  `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`.

---

## 2. Who writes what

### 2.1 The three tiers of authorship

`docs/charters/PROPOSALS_OPEN.md` closes with a section called *"What is
recorded, not proposed"*. That distinction is the corpus's real spine and this
document adopts it:

1. **Hers.** Closed unless she reopens it. The six HARD criteria
   (`CASE_SELECTION_CHARTER.md` §1: *"The list is the owner's and it is closed"*),
   the six report sections and their order, the three ranking axes, the daily-list
   protocol, family membership.
2. **The lab's rendering of hers.** Always flagged as such. The five word-values
   extending `hard_criterion`, the family scope table, the reporting frame.
3. **The lab's own proposal.** Marked PROPOSAL, answerable by label, and the
   standing constraint on it is that *"the lab must never present its own
   invention as her policy."*

### 2.2 Where custody is actually stated

Only three files say who writes them. **Nine of twelve charters do not.**

- `SUPERVISION_CHARTER.md` §2.1 — family leads write family guidelines "in the
  family's own records"; §4 — "The daily list and the research board are written
  by the chief."
- `SUPERVISOR_RULINGS.md` — the chief, under a quoted delegation, with outward-facing
  acts explicitly excluded.
- `docs/CAPABILITY_STRATEGY.md` — Katie's body verbatim, chief's notes below.

For `VERIFICATION_CHARTER`, `GOALS_AND_PROPOSALS_CHARTER`, `REPORTING_CHARTER`,
`ESCALATION_CHARTER`, `COMPUTE_BUDGET_CHARTER`, `CASE_SELECTION_CHARTER`,
`RESULT_PRIORITY_CHARTER`, `LITERATURE_CHARTER` and `README.md`, custody is
inferable only from provenance sentences inside the text. **This document does
not invent it.** Recording it is the open item in §9.

### 2.3 The four families and their guidelines — four directories, four conventions

This is the single most likely thing a new agent needs and cannot find.

| Family | Guidelines file | Version convention |
|---|---|---|
| DAFoam and adjoint | `demo-output/website/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` | none |
| Closure and UQ | `demo-output/website/CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` | none |
| Cases and campaigns | `demo-output/website/campaign/CASES_FAMILY_SUPERVISION_GUIDELINES.md` | header says v1.0; **actually at v1.13** (D-2) |
| Infrastructure and standards | `docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md` | v2.6, 79 KB |

Four families, four directories, three naming shapes, two version schemes and
two files with no version at all. Nothing indexes them.

---

## 3. What is LOST at session end

Name it plainly. Everything in this section is gone the moment the session
ends, and eight fleet kills between 2026-08-04 and 2026-08-08 mean "session end"
is not hypothetical — it is roughly a twice-daily event.

**Lost, with no recovery path:**

1. **Every agent's in-flight reasoning.** What an agent had concluded but not
   yet written is gone. Not degraded — gone.
2. **Anything only said.** A finding reported in a message to a supervisor and
   not committed does not exist. This is not a figure of speech: it is why
   `a5a28a40` exists, moving a closing fact into `VERIFICATION_CHARTER.md` so
   §17's scope test would carry it.
3. **The session scratchpad, and anything in it.** This has already cost real
   evidence. `demo-output/website/dafoam/ADJOINT_MEMORY_ENVELOPE.md:622` records
   two option arms' solver logs that lived in
   `982d6244.../scratchpad/logs/` and *"died with it — they are
   unreconstructible."* Those claims now ship as unverifiable-from-logs.
   `demo-output/website/dafoam/WARMSTART_AUDIT.md:32` records the same loss for
   the D3 n15 nulls: *"NO LOGS PRESERVED"*.
4. **Uncommitted working-tree state.** At 21:00 UTC this tree held 17 dirty
   paths across six agents. At 21:08 it held 2. Work that is not committed is
   work that a kill deletes.
5. **Live agent handles.** Agent IDs, and the ability to resume a specific agent
   by message, are session state. After a kill you resume from transcript, which
   is a different and lossier operation.
6. **The dispatch itself,** until someone writes it down. The instructions that
   produced this document existed only in a message until this file was
   committed.

**Not lost, and frequently misdescribed as lost:**

- **Transcripts survive.** 502 transcript files, 1.2 GB, under
  `/home/ubuntu/.claude/projects/-home-ubuntu-Certonomous/`. Every fleet-kill
  record says agents resumed *from* transcript. The dispatch's claim that two
  transcripts became unreachable is not supported by any record.
- **Detached solves survive.** `setsid` and docker solves outlive the agent that
  launched them and keep running unowned. Inventory `sudo docker ps` before
  resuming so an agent reattaches instead of relaunching.
- **Watchers do not survive.** They die with the agent that owned them, and a
  "waiting on my monitor" completion is the dead-agent tell.

### 3.1 The store that is durable but outside version control

`/home/ubuntu/.claude/projects/-home-ubuntu-Certonomous/memory/` holds 17 files,
744 lines, and is **not a git repository and not tracked by this one**. It
survives session end. It does **not** survive a fresh clone, a new box, or
anyone who is not this user on this machine.

It is load-bearing. `ESCALATION_CHARTER.md:392` outsources part of the
fleet-death account to it: the record *"lives in `docs/PRODUCT_LIST.md`'s
changelog … and in the supervisor's own memory."* The fleet-recovery procedure
— the double-resume trap, arming both keepalives, inventorying docker before
resuming — exists in full **only** in
`memory/session-limit-kills-the-fleet.md`. A fresh clone cannot recover a fleet.

**Rule.** A fact that operations depend on may live in the auto-memory store as
a *convenience copy*, never as its only home. Anything only there is one machine
away from lost. Migrating the operational content of that store into the repo is
the open item in §9.

---

## 4. The cold-start reading order

**This is the load-bearing part of this document.** It is written to work, not
to be complete. It is ordered by *cost of not knowing*, not by importance —
which is why a commit procedure comes before the science.

A fresh agent reads these, in this order, and stops at the tier that covers what
it is about to do.

### Step 0 — before you touch git. Two minutes. Skipping this destroys other agents' work.

Read `docs/charters/ESCALATION_CHARTER.md` §9.6 and §9.6a. **They are below the
`## Related` block**, at roughly lines 475-500, which is why people miss them.

The rule, in its current form:

```
git add <paths>
git commit -m "..." -- <paths>
```

Never a bare `git commit` after staging. Six agents commonly share this tree; a
bare commit takes the entire shared index including their unfinished work.

**§3 of the same charter (line ~129) is stale and will mislead you.** It says
"Stage explicit file paths", which §9.6a measured as insufficient after four
collisions in one day. The version header was never bumped for either
amendment, so nothing signals that §3 is superseded. Read the tail, not §3.

### Step 1 — what the lab is doing, and in what order. Five minutes.

`docs/PRODUCT_LIST.md`:

- **Lines 1-8.** The item protocol and the priority order. `[x]` = fully done
  with evidence linked; `[-]` = attempted, blocked or failed with diagnosis;
  `[~]` = done in substance, pending adversarial verification (assume wrong
  until defended). Every cross-off adds a new item.
- **Lines 11-261.** Sections 4A-4I, the actual checklist. **60 items measured at
  2026-08-10 21:16 UTC: 33 `[x]`, 14 `[ ]`, 12 `[-]`, 1 `[~]`.**
  *[CORRECTED 2026-08-10 21:16 — this line first read "57 items: 32 done, 14
  open, 11 blocked", a count inherited from a survey taken twenty minutes
  earlier and not re-measured before writing. It was wrong in three of four
  figures by the time it was committed, because the product list is written
  continuously and grew by 27 lines during the survey itself. The original is
  retained here rather than overwritten, per §8.1, and it is left in place
  deliberately: it is this document's own first instance of the defect it
  documents, and a count copied without a stamp is exactly D-5's mechanism.]*
- **The last three `###` changelog entries only.** Not the whole changelog: it
  holds 53 entries of which 44 are dated 2026-08-10, disambiguated by
  parentheticals like "(closing 19)" and "(night, last)" that are not unique
  keys.

### Step 2 — who decides what. Ten minutes.

- `docs/charters/SUPERVISION_CHARTER.md` — 11 KB, read whole. The org chart and
  the only explicit statement of write-custody.
- `docs/charters/SUPERVISOR_RULINGS.md` — 12 KB, read whole. R1-R12 are standing
  decisions that bind, and four other charters defer to them by number. Highest
  authority after Katie's own instructions.

### Step 3 — your family's standing rules.

One file from the table in §2.3. If you do not know your family, you are not
ready to work; ask.

### Step 4 — before you spend any compute.

- `docs/charters/VERIFICATION_CHARTER.md` — 87 KB. **Do not read whole.** Read
  §1 (retained artifacts), §9 (lever activity — a lever is evidence only when
  the log proves it ran), §12 (enforcement), and §17 with §17a. Note §17a
  physically precedes §17 in the file.
- `docs/charters/COMPUTE_BUDGET_CHARTER.md` — 21 KB, including the trailing
  section **below** `## Related`, which carries a binding rule the header's
  version does not mention.
- `docs/charters/CASE_SELECTION_CHARTER.md` §1-§2 — the hardness floor, six
  criteria, closed.
- The pre-registration rule is not optional and not waivable for short runs:
  predictions, thresholds, caps and labels are committed **before** the first
  iteration. This is what made eight fleet kills cost zero science.

### Step 5 — before you write a conclusion.

`LESSONS.md` is 2236 lines. **Do not read it cold** — see §5 for why. Read, in
this order:

- **The eight most-cited**, which is a measured ranking, not a taste:
  L-40 (93 citations outside the file), L-42 (51), L-45 (42), L-26 (35),
  L-22 (29), L-1 (26), L-24 (24), L-6 (22).
- **The record-hygiene trio**, which is what this document exists to enforce:
  L-32 (a verdict moves in the case's own file first), L-39 (verdicts age
  silently), L-46 (a change that creates an artifact must be audited from both
  ends).

### Step 6 — the current queue.

`demo-output/website/agenda/proposals/*.json` — 109 files, the inbox.

**Do not use `docket.json` to learn what is open.** Its `generated_at` reads
2026-08-08T22:59:53Z while its mtime is 2026-08-10 18:22 and it contains a
record created 2026-08-10T17:55Z. 34 proposal files have never reached it. See
D-1.

### Step 7 — what is not in the repo at all.

`/home/ubuntu/.claude/projects/-home-ubuntu-Certonomous/memory/` — §3.1. Read
`session-limit-kills-the-fleet.md` and `agent-watchers-die-with-the-agent.md`
before you supervise anything.

### 4.1 What this order deliberately omits

`docs/charters/README.md` is **not** step 1, despite being the index, because
its description of the lesson corpus is wrong by 25 entries (D-3) and a fresh
agent who trusts it will under-read the most-cited record in the lab by half.
Read it at step 2 with that correction in hand.

`docs/HANDOFF*.md` (ten files, all dated 2026-07-25/26) are not in the reading
order at any tier. They are historical.

---

## 5. Is `LESSONS.md` usable at its current size?

Measured, 2026-08-10 21:00 UTC: **2236 lines, 135 KB, 53 lesson blocks.**

Growth, by the size of the file at each day's last commit:

| Date | Lines |
|---|---|
| 2026-07-28 | 221 |
| 2026-07-30 | 1356 |
| 2026-08-04 | 1653 |
| 2026-08-08 | 1806 |
| 2026-08-10 | **2236** |

430 lines — 24 percent — were added on 2026-08-10 alone (L-42 through L-53,
twelve lessons in one day). The file is 10x its size of thirteen days ago.

**Verdict: usable as a citation target, not usable as a cold read, and it has
no working index.** Four specific defects:

1. **No table of contents.** The file opens at line 1 and the first lesson is at
   line 9. There is no way to find a lesson without grepping.
2. **The numbering is gapped and non-monotonic.** There is **no L-52** anywhere
   in the repo — 52 distinct numbers (L-1..L-51, L-53) across 53 blocks. L-4
   appears after L-7. `L-43` has two blocks, the second titled "L-43, second
   corollary", which no numeric cross-reference can address.
3. **The only external index of it is wrong.** `docs/charters/README.md:93` says
   *"L-1 through L-28"*. It has said that through 25 further lessons, including
   L-40, L-41, L-44, L-45 and L-48 — every one of which a charter actively cites.
4. **There are two other lesson namespaces**, neither reconciled with it (D-4).

It is nonetheless the lab's most load-bearing artifact: lesson numbers are cited
**over 700 times** across the repo outside the file itself. It earns its size.
It does not earn its lack of an index. The fix is an index, not a cull —
proposed in §9, not performed here.

---

## 6. The monthly cold-start test

A fresh agent with no context must reach correct current state using **only the
durable files**. This section specifies the test so that someone who is not the
author can run it.

### 6.1 The rule that makes the test worth running

> **Whatever the test agent gets wrong is a memory defect, and it is fixed in
> the FILES. It is never fixed by explaining it to the agent.**

An explanation given to the test agent is the failure reproducing itself: a fact
transmitted in conversation instead of in a record. If the tester finds
themselves typing the answer, that is the finding — stop, and log which file
should have carried it.

### 6.2 Who runs it

Not the author of this document, and not anyone who worked the month being
tested. Anyone with prior context fails in the flattering direction: they will
read their own knowledge into an ambiguous file and score it as a pass. The
runner needs no domain knowledge — every answer below is checkable against a
cited file.

### 6.3 How it is run

1. On the first working day of the month, dispatch a fresh agent with **exactly
   one instruction**: *"Read `docs/MEMORY_ARCHITECTURE.md` §4 and follow it. Then
   answer the twelve questions in §6.4. Cite the file and line for every answer.
   Do not ask for help."*
2. The agent gets no other context, no dispatch history, and no answers.
3. It gets a normal working tree — the same clone anyone else gets.
4. Its answers are scored against §6.4 by someone holding the key.
5. **Every wrong or uncitable answer opens a defect** against a named file, with
   a fix landing in that file within the week. The defect is logged in
   `docs/PRODUCT_LIST.md`'s changelog with the tag `COLD-START DEFECT`.
6. The run and its score are committed under
   `demo-output/website/campaign/COLD_START_TEST_<YYYY-MM>.md`.

### 6.4 "Correct current state" — the checkable list

Twelve questions. Each has a single defensible answer with a file citation. An
answer that is right but uncitable **scores as wrong** — the point is whether
the files carry it, not whether the agent guessed it.

| # | Question | Answer must include |
|---|---|---|
| 1 | What is the exact command pair for committing on this shared tree, and what must you never do? | `git add <paths>` then `git commit -m "..." -- <paths>`; never a bare `git commit`. Cites `ESCALATION_CHARTER.md` §9.6a |
| 2 | What are Katie's priority orders for work, in order? | The five-item order at `docs/PRODUCT_LIST.md:1-8` |
| 3 | What do `[x]`, `[-]` and `[~]` mean on the product list? | Fully done with evidence / attempted-blocked-failed with diagnosis / done in substance pending adversarial verification |
| 4 | Name the four families and give the path to each one's standing guidelines. | The four paths in §2.3. Getting fewer than four is a defect against §2.3 |
| 5 | What must be committed before compute, and what are the three mechanisms that made fleet kills survivable? | Pre-registration (predictions, thresholds, caps, labels); pre-registration-first **plus** out-of-process execution **plus** per-eval checkpoints |
| 6 | How many fleet deaths have there been, and what is the date of the most recent? | Eight; the eighth ran 2026-08-08 late to 2026-08-10 14:48 (`PRODUCT_LIST.md:670`) |
| 7 | What does CERTIFIED mean for a mesh in the 2026-08-08 audit, and how many of the 105 carried an actual certificate? | It means a `log.checkMesh` exists, not that a certificate was written. **Zero** of 105 carried `birth_certificate.json` |
| 8 | Which is authoritative for a proposal's status: the file in `proposals/`, or `docket.json`? | **Neither is currently authoritative** — this is a known open defect (D-1). An agent that confidently picks one has failed |
| 9 | Name three standing rulings by number and what each decided. | Any three of R1-R12 from `SUPERVISOR_RULINGS.md` |
| 10 | What is the most-cited lesson in the lab, and what does it say? | L-40: the switch you set is not the switch that ran; a lever is evidence only when the log proves it was active |
| 11 | When a verdict changes, which file must be updated first, and why? | The case's own `ladder-*` record, `.md` and `.json`, **first not last** — L-32 |
| 12 | Name one thing that is lost at session end and one thing that survives. | Any item from §3's two lists. Naming transcripts as lost is **wrong** — they survive |

**Scoring.** 12/12 is the only pass. This is not harsh: every answer is a fact
the lab acts on daily, and the test exists to find the ones the files fail to
carry.

**A calibration note for the first run.** Questions 4, 7 and 8 are expected to
fail today, because §2.3, D-9 and D-1 are open defects at the time of writing.
A first run that fails exactly those three and passes the other nine is the
document working correctly — it means the map is accurate about its own gaps.

---

## 7. One home per fact

### 7.1 The rule

> **A fact has one home. Every other mention is a cross-reference to it, never a
> copy of it.**

The corpus already states this, in `CASE_SELECTION_CHARTER.md` §10, better than
this document can: *"a case detail stated in two places is already wrong in one
of them."*

Copying is not always wrong — it is wrong *silently*. Where a fact genuinely must
appear twice, the second appearance names the first as its source, so a reader
who finds a disagreement knows which one to fix. `docs/MESH_STANDARD.md` is the
model: it opens by naming its own collision with
`docs/standards/MESH_STANDARD.md` and saying which question each governs —
*"Naming collision flagged, not hidden."* That is the pattern to generalise.

### 7.2 The duplicate register, 2026-08-10

**This is a report. No edits were made.** Each row names the home this document
proposes; adopting them is a separate decision.

| # | Fact | Copies | Proposed single home | Drifted? |
|---|---|---|---|---|
| **D-1** | **Proposal status** | `docket.json` (264 records) vs `proposals/*.json` (109 files) | **Unresolved — needs a ruling.** Either files become pure intake, or the merge becomes two-way | **YES, 45%.** 34 of 75 shared ids disagree. 34 files never reached the docket; 189 docket records have no file. Cause: `refresh_docket()` at `agenda.py:1197` skips any id already on the docket, so a file is never re-read after first merge. Three records are *file-ahead* — the file says done, the docket does not: `s1-cbfs-objective-repair-and-reinversion`, `f6b-model-form-matrix-on-the-hills`, `kfamily-fpe-shared-diagnosis-bump-and-hills`. **Which is right: the file.** It carries `outcome` and `decided_at`; the docket carries a status nothing updated. |
| **D-2** | **Cases family guidelines version** | Header says `v1.0`; body line 177 says `v1.5`; commit log has amended it to **v1.13** | The file header | **YES.** The header is 12 revisions stale. **Which is right: the file's content** (it carries the amendments); its *stated version* is wrong. |
| **D-3** | **Size of the lesson corpus** | `README.md:93` says "L-1 through L-28"; `LESSONS.md` runs to L-53 | `LESSONS.md` itself, via a generated index | **YES,** by 25 entries. **Which is right: `LESSONS.md`.** Verified by counting headers. |
| **D-4** | **Lesson namespaces** | `LESSONS.md` (`L-1`..`L-53`); `sdk/chief_engineer/lessons.py` (`L-001`, one entry, 16 citations across 11 files); the out-of-repo `memory/` store (17 topic files) | `LESSONS.md` for lab lessons; rename the SDK one | **YES, and worse:** the SDK namespace cites `sdk/introspection/recipe/memory/LESSONS.md`, **a path that does not exist** — asserted in `sdk/tests/test_orchestration_stack.py:415,425` and never checked against the filesystem. `L-001` and `L-1` are different facts with confusable names. |
| **D-5** | **Fleet-death count** | `SUPERVISION_CHARTER.md:101` "three"; `ESCALATION_CHARTER.md:370` "Three … in about 46 hours" + a 3-row table; `PROPOSALS_OPEN.md:900` "three"; `CASES_..._GUIDELINES.md:18` "four"; `PRODUCT_LIST.md:665` "four"; `PRODUCT_LIST.md:670` "**EIGHTH**" | `PRODUCT_LIST.md`'s changelog, as the incrementing ledger; everything else cites it | **YES — five values for one running count.** **Which is right: `PRODUCT_LIST.md:670`, eight.** How I know: it is the only copy that is an incrementing ledger entry rather than a frozen prose summary, it is the newest, and the ordinals 3rd/4th/6th/7th all live in the same changelog. The three "three"s were true when written and were never revisited. |
| **D-6** | **The nine-day figure** | `LESSONS.md:1752`, `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md:207`, `F5bc_unsteady_statistics.md:104`, `PRODUCT_LIST.md:571` | `LESSONS.md` L-39 | **YES — all four are wrong.** Measured 7 d 15 h. Written once, copied three times, checked zero times. |
| **D-7** | **Rank-1 challenge score + mandatory caveat** | Nine files: `PRODUCT_LIST.md` 4B, `CLOSURE_CHALLENGE_STATUS.md:530`, `campaign/PROBABILITY_OF_RANK_2026-08-10.md`, `ACTIVE_RESEARCH.md`, `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`, `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`, `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md`, `campaign/CHALLENGE_SLATE_2026-08.md`, `agenda/CHALLENGE_LANDSCAPE.md:109` | `campaign/PROBABILITY_OF_RANK_2026-08-10.md` | **Not yet** — they agree modulo rounding (`t = −0.495` vs `−0.50`). This is the highest-risk row in the table: the caveat is *mandatory* wherever rank is claimed, so nine files must move in lockstep on any change. Nine-way agreement today is luck. |
| **D-8** | **`ESCALATION_CHARTER` git rule** | §3 (line ~129) "stage explicit file paths" vs §9.6a (line ~490) "that is insufficient" | §9.6a | **YES, internally.** §3 prescribes the practice §9.6a measured as failing, and the version header was bumped for neither. A reader who stops at the numbered sections gets the superseded rule. |
| **D-9** | **What CERTIFIED means / certificate coverage** | `PRODUCT_LIST.md:1353,1427,1647,1673`; `campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md:532`; `docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md:1167,1244` | `docs/standards/MESH_STANDARD.md` | **Not currently** — copies agree at "105 of 105 hold a log, 0 of 105 hold a certificate". But **105 and 95 are different facts** (105 inherited the word; 95 were later minted, 10 refused) and are easy to conflate. Any future citation must say which. |
| **D-10** | **`RESULT_PRIORITY_CHARTER` version** | Line 3 "Version 0.4"; line 9 "Version 0.2"; line 294 "version 0.1" | Line 3 | **YES, internally.** Lines 9 and 294 were carried unedited through two revisions. |
| **D-11** | **Standing costs** (3600 s stall, 26.98 core-hr, 239.259 headline, 480 core-min hold, 221 grandfathered entries, FD grading bands) | 3-4 files each across `COMPUTE_BUDGET_CHARTER`, `REPORTING_CHARTER`, `PROPOSALS_OPEN`, `SUPERVISOR_RULINGS`, `VERIFICATION_CHARTER`, `PRODUCT_LIST` | The owning charter; others cite | **No — all agree today.** Listed because they are copies, so they are drift waiting to happen, and there are six of them. |

### 7.3 The pattern behind D-5, D-6 and D-2

All three are the same defect: **a fact that changes over time was written as
prose into a file that has no reason to be revisited.** A count, a version and a
duration. Each was true when written. None was wrong at writing time; all are
wrong now.

The rule that follows: **a fact that can change gets a ledger, not a sentence.**
If prose must state it, the prose cites the ledger rather than restating the
number, so the copy cannot drift independently of the thing it copies.

---

## 8. The staleness rule

### 8.1 The rule

> **A record whose claim has been superseded is amended in place, dated, with
> the original text retained. Never a silent edit, and never a deletion.**
>
> **A commit that refutes a standing record must amend that record in the same
> commit.** "The proof exists somewhere in the repo" is indistinguishable from
> "unproven" to every future reader who starts from the record.

The second half is L-39's own corollary. It is the whole rule: the nine-day
incident was not a delay in *finding* the proof, it was that the proof and the
record it refuted were never connected.

### 8.2 The rule is already the practice — that is not the problem

Measured across tracked markdown, 2026-08-10: **36 supersession markers
(`[AMENDED`, `[CORRECTED`, `[WITHDRAWN`, `[SUPERSEDED`, `[RETRACTED`) across 27
files. 35 of 36 carry a date — 97 percent compliance.** The single exception is
`docs/PRODUCT_LIST.md:702`, which reads *"[CORRECTED SAME DAY, 5aa3a142 …]"* —
a commit hash instead of a date, which is resolvable but not readable.

So the convention is healthy and widely followed. **The gap is not compliance.
The gap is detection.** Every one of those 36 markers exists because a human or
agent already knew the record was stale. Nothing in the lab finds the ones
nobody noticed.

### 8.3 The enforcement question: how would anyone KNOW a record had gone stale?

Today: **nobody would, except by accident.** The nine-day case was found because
a zero-compute audit happened to read the case's full commit history as its
first act. That is not a detector, it is luck with good habits.

### 8.4 Two detectors, because there are two failure modes

Investigating the actual incident showed that the obvious detector would not
have caught it. Both are stated, with the honest scope of each.

**Detector A — the two-timestamp sweep. Catches records that AGED into staleness.**

For each record R that asserts a verdict about case C:

```
t_R = last commit touching R
t_C = last commit touching demo-output/website/campaign/{C}_runs/ or {C}_*
flag if t_C > t_R
```

Cost: one `git log` per pair, zero compute, no new metadata. The case-id to
directory mapping is already mechanical — `F5c` to `F5c_runs/` and `F5C_*.md`,
`DMR` to `DMR_runs/`, and so on throughout `campaign/`.

This would catch D-5 (the fleet-death count), D-3 (the L-28 range), D-2 (the
v1.0 header) and D-10. It is worth building on that alone.

**It would NOT have caught the nine-day case, and here is why.** The refuting
commit `fe121af2` landed 2026-07-31. The review that carried the dead premise
was first written 2026-08-07, *seven days later*. `t_C < t_R`. The record did
not age into staleness — **it was born stale.** A sweep comparing last-modified
times sees a record newer than its evidence and passes it.

**Detector B — the reconciliation stamp. Catches born-stale records, which is the actual incident.**

A record asserting a standing verdict about case C carries the point it
reconciled through:

```
reconciled_through: <commit-sha or ISO date>   # for case C
```

The sweep then asks, for each such record: `git log --since=<reconciled_through>
-- <C's paths>` — non-empty means evidence moved after the author last looked,
whether the record is old or new.

This *is* L-39's prescribed sweep, made mechanical and, crucially, made
**auditable after the fact**. Today an agent can perform the sweep and leave no
trace that it did; the stamp is the difference between "I checked" and "it is
checkable that I checked".

**Per L-46, the stamp is a new artifact, so: what reads it?** Nothing, today —
that is the point, and it is what makes it safe to add. Enumerated:
(a) the proposed sweep script, its only consumer; (b) no existing check's
passing condition can be satisfied by its presence, because no check parses
record front-matter; (c) no glob-based consumer discovers records by pattern in
a way a new key would perturb — it is a line inside a file, not a new file in a
directory. It disables nothing and confuses nothing.

### 8.5 The cheapest thing that would have caught it

If only one of these gets built, build **Detector B, restricted to a single
trigger**: when a record asserting a verdict is *committed*, print the last ten
commits touching that case's paths and require the author to have looked.

Rationale: the nine-day case was a *write-time* failure, not a decay failure. The
cheapest detector is the one that fires at the moment the stale premise is
written down, which is also the only moment someone is in a position to fix it
for free. Cost is one `git log` at commit time.

---

## 9. Known defects in the lab's memory, 2026-08-10

Stated as defects with owners implied, so that a later reader applies §8 to this
document rather than trusting it. **None of these were fixed by this document;
it has no mandate to edit other agents' files.**

| # | Defect | Where |
|---|---|---|
| 1 | Proposal status has no authoritative home; 45 percent drift | D-1 |
| 2 | `LESSONS.md` has no index, a gap at L-52, and an unaddressable corollary block | §5 |
| 3 | The charters index under-reports `LESSONS.md` by 25 entries | D-3 |
| 4 | Four family guideline files, four directories, no index | §2.3 |
| 5 | Write-custody is unstated for 9 of 12 charters | §2.2 |
| 6 | Operational fleet-recovery knowledge exists only outside version control | §3.1 |
| 7 | `ESCALATION_CHARTER` §3 contradicts its own §9.6a; neither bumped the version | D-8 |
| 8 | `docket.json:generated_at` lies by two days; hand edits bypass `save_docket()` | D-1 |
| 9 | An SDK test asserts a lessons path that does not exist on disk | D-4 |
| 10 | `VERIFICATION_CHARTER.md` and `COMPUTE_BUDGET_CHARTER.md` are dated **2026-08-11**, tomorrow | below |
| 11 | Two charters have grown binding clauses **below** `## Related`, where readers stop | §4 step 0, step 4 |

**On defect 10.** `VERIFICATION_CHARTER.md:3` reads *"Version 1.6, dated
2026-08-11"* and `COMPUTE_BUDGET_CHARTER.md:377` reads *"Added 2026-08-11 (D5)"*,
while `date -u` at the time of writing returns 2026-08-10 21:07 UTC and both
files' mtimes are 2026-08-10. This is the same defect `LESSONS.md` commit
`e59ae644` caught and fixed in itself hours earlier — *"my own entries took
their date from the dispatch header instead of the clock."* The lesson was
learned in one file and the two charters carrying the same error were not swept.
That is a cross-file propagation gap, not a typo, and it is the third instance
this document found of a fix that did not travel.

---

## 10. Related

- `LESSONS.md` — L-32 (satellites are not the record), L-39 (verdicts age
  silently), L-44 (a pre-registration is frozen against improvement), L-46 (audit
  a new artifact from both ends), L-49 (a search built from what you read returns
  what you read).
- `docs/charters/README.md` — the charter revision protocol this document's §8
  extends.
- `docs/charters/SUPERVISION_CHARTER.md` §2.1, §4 — write-custody.
- `docs/charters/ESCALATION_CHARTER.md` §9 — what an agent must do before it can
  be stopped without warning.
- `docs/PRODUCT_LIST.md` lines 1-8 — the item protocol and priority order.
