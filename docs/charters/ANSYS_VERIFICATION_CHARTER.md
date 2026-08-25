# ANSYS VERIFICATION CHARTER — the Ansys Fluid Dynamics Verification Manual, run as lab verdicts

**Version 1.0, dated 2026-08-24.** Drafted by the harness-build lane on Sanaa's
directive of the same day, for the `ansys-verification` team. This charter is
subordinate to `CLAUDE.md` (all sixteen standing rules bind this team without
restatement) and to `VERIFICATION_CHARTER.md` for the verdict machinery; where it
adds a rule, the rule is new and says so. It is a frozen file under CLAUDE.md
rule 6: departures land as dated amendments at the foot, never as edits above.

---

## 1. Sanaa's directive, verbatim (2026-08-24)

> "agreed with you. Let's have an ansy-verification team. That team should have
> a fable supervisor, 2 opus sub agents (5 and 4.8)and 2 haiku subagent. Fable
> handles anything research, code verification, compute allocation numerics
> checks etc related, 2 opus subagent take orders from the supervisor, anf the
> haiku ones are just in charge of pulling codes or monitoring logs. Both
> supervisor and opus subagent must read th everification manual first. As for
> the other teams, this ansys-verification team must record: 1. Every single
> case ran and successfully validated 2. As always update the lessosns,
> numerics knowledge and charters with everything they find in the verfication
> manual and also in the process of running the verification cases, and these
> verification cases are also then part of the lab's credentials bc then
> everything is validated."

Recorded character for character, spelling included; the spelling is hers and
is not corrected because the quotation is the authority. The chief's relay of
the same day adds, in her words: *"I wanted a verification team to exclusively
work on these verification cases."*

## 2. Mission

The Ansys Fluid Dynamics Verification Manual (Release 2026 R1, March 2026; 290
pages; test cases VMFL001–VMFL078 for Fluent, VMFRT001–VMFRT007 for Forte, and
the VMFLGPU set) is a catalogue of small, well-posed fluid-dynamics problems,
each with a reference result — analytical, experimental or a published
numerical benchmark — and Ansys's own reported agreement with it. This team
turns that catalogue into a ladder of **lab verdicts**: each case reproduced in
this lab's own solvers, pre-registered against the manual's reference result
with a tolerance as the gate, frozen before compute, graded under the lab's
completion and control rules, and recorded in a register whatever the answer.

**What "run" means here.** This box has no Ansys solver — no `fluent`, no
`cfx5solve`, no `forte` (checked 2026-08-24). A case is therefore reproduced in
OpenFOAM (or another solver the lab already builds and records), and the Ansys
archives (`.wbpz`, `.ftsim`) are read for geometry, setup and reference numbers
only. A verdict from this team is a statement about the lab's solver against
the manual's reference result; it is never a statement about Ansys.

**Why it is credentials.** Sanaa's directive: *"these verification cases are
also then part of the lab's credentials bc then everything is validated."* A
`PASS` row in the register — reference result met inside a tolerance that was
frozen before the solver ran — is a credential the lab can cite. Nothing else
is: a case not run is not a credential, and a `GATE FAIL` is a finding, not a
credential and not a deletion.

## 3. Roster and model assignments

| Agent (`subagent_type`) | Model | Role, from the directive |
|---|---|---|
| `ansys-verification-supervisor` | `fable` | "anything research, code verification, compute allocation numerics checks etc related". Personally does the four `SUPERVISION_CHARTER` §3 checks (measurement-script diffs read as diffs; crash triage; big-claim verification; pre-registration committed before compute) — never delegated. Spawns ONLY the three lane types below. |
| `ansys-lane-opus` | `opus` (resolves to Opus 5) | "take orders from the supervisor": drafts pre-registrations for the supervisor to freeze, builds and runs cases after the freeze is committed, grades, drafts register rows and RESULTS records, drafts LESSONS / NUMERICS / charter entries. Must read the manual first. |
| `ansys-lane-opus48` | `claude-opus-4-8` | Same role as `ansys-lane-opus`, pinned to Opus 4.8 per the directive. |
| `ansys-lane-haiku` | `haiku` | "just in charge of pulling codes or monitoring logs". Tool list restricted to `Bash, Read, Grep, Glob` — no Edit, no Write, no Agent. Drafts nothing, grades nothing, launches nothing. Two may be live at once. |

**Model-id provenance (rule 15 spirit: verified, not recalled).** Claude Code's
sub-agent frontmatter accepts an alias (`opus`, `haiku`, `fable`) or a full
model id; the alias tracks the latest model of its family, so pinning 4.8
requires the full id. `claude-opus-4-8` is the id listed on the Claude
model-ids page (`platform.claude.com/docs/en/about-claude/models/model-ids-and-versions`)
and the frontmatter's acceptance of a full id is stated on the sub-agents page
(`code.claude.com/docs/en/sub-agents`); both were fetched by a `claude-code-guide`
agent on 2026-08-24. **What is not yet verified is that this box's provider
serves that id to a spawned lane** — agent definitions load at session start, so
the first `ansys-lane-opus48` spawn of the next session is the load test. If it
fails, the supervisor reports it and the pin is amended below; nothing is
guessed.

**Lane cap — a disclosed exception.** `SUPERVISION_CHARTER.md` v1.4 §8 caps
every supervisor at **three** live lanes. Sanaa's directive specifies **four**
for this team (two opus, two haiku), so this team's cap is 4 — at most 2 opus
and 2 haiku live — **by her explicit instruction, recorded here as an exception
to §8 and not as a silent violation.** `harness/teams.yaml` carries it as
`max_live_lanes: 4` with a `lane_cap_note` naming this section;
`scripts/check_harness.py --selftest` fails any cap override that lacks such a
note. §8 itself is unchanged: amending it is Sanaa's, not this charter's.

## 4. The reading rule

1. **The manual first.** The supervisor reads
   `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
   (the sidecar of the PDF beside it) **before dispatching anything**, and every
   opus lane reads it **before anything else on its item**. This is Sanaa's
   instruction and is written into the generated agent definitions.
2. **Title-page verification (CLAUDE.md rule 15).** The sidecar is believed
   only after its title page is checked against the PDF's: "Ansys Fluid
   Dynamics Verification Manual, ANSYS, Inc., Release 2026 R1, March 2026"
   (PDF metadata: 290 pages, DocBook/XEP, `Title: Fluid Dynamics Verification
   Manual`). Never by filename, file type or hash alone.
3. **The chapter before the case.** A lane opening case `VMFLnnn` reads the
   manual's overview of the test-case format and the case's own page (the index
   at the front of the manual gives the page), and its brief from the supervisor
   names the case id, the page, the reference result and the intended tolerance.
4. **The haiku lanes** read nothing beyond their brief and the paths it names;
   they are not asked to interpret the manual.

## 5. How a case becomes a lab verdict

Every case is a rung and goes through this sequence; a rung that skips a step
produces `NOT A RESULT`, never a softer word.

1. **Pre-registration, prediction-first, frozen by sha (rule 2).** The file is
   `cases/ansys_verification/<CASE>/PREREGISTRATION.md` and carries, before any
   solver starts: the case id and manual page; the **reference result** as the
   manual states it (value, unit, source — analytical / experimental /
   benchmark); Ansys's own reported value, quoted for context and **not** used
   as the gate; the **gate**: `|lab − reference| / |reference| ≤ tol` (or an
   absolute band where the reference is zero), with `tol` chosen and justified
   from the manual's own agreement class and the lab's grid triple, never from
   a first run; the grading path (comparator script + its committed sha); the
   solver, model and mesh family; and the **cost in core-minutes** with its
   `cost_basis` (rule 12). The supervisor verifies the freeze is **committed**
   (§3 check 4) and records the prereg sha before the first solver launches.
   Amendments before first compute state the condition and how it was checked
   (name the run directory that does not exist); after first compute, dated
   addenda only.
2. **Compute.** Runs live under `verification/runs/ansys_verification/<CASE>/`,
   never beside the prose (FILING_CHARTER R6). An overrun of the pre-registered
   cap **stops the run** (rule 12). Neither VM2026R1 archive copy is written to,
   moved or deleted by a run.
3. **Strict completion (rule 4).** `rc = 0`; an `End` line; last time ==
   `endTime`; the fields the case declares present at `endTime`; ExecutionTime
   count == `endTime`; every field at `endTime` newer than the case's own `0/`
   launch marker (the age guard). The comparator **refuses (exit 2)** on any
   failed clause rather than grading a partial run.
4. **Planted-zero control (rule 3).** The comparator plants a known perturbation
   into a copy of the field it reads, reads it back from disk, and refuses if it
   cannot see it. A comparator without a fired plant has produced no number.
5. **Grid triple where the case has one (rule 5).** A case graded on a
   three-level family is `NOT A RESULT` unless the triple is `CONVERGING`; GCI at
   Fs = 1.25 is printed beside a `PASS` or `GATE FAIL`. A case run on a single
   mesh says so in its prereg and its verdict is labelled single-grid.
6. **Verdict (rule 1).** `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` /
   `PENDING`, nothing else. The value, its interval, the reference and the
   tolerance are printed beside every verdict.
7. **Cost calibration at completion (rule 12).** Actual core-minutes from the
   logs against the pre-registered estimate; ratio, attribution (contention,
   waste, misprediction; waste named separately), dollars derived at
   $0.0513/core-h and labelled **derived, not measured**; one row appended to
   `docs/COST_CALIBRATION.md` under its append rules. A case report without this
   row is incomplete.
8. **The record.** `cases/ansys_verification/<CASE>/RESULTS.md` (verdict,
   numbers, artifact paths, prereg sha, comparator sha, cost, calibration) and
   the register row of §6.

## 6. The VALIDATION REGISTER

`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` is the team's
answer to directive item 1, *"Every single case ran and successfully
validated"*, read strictly: **every case run is recorded, and the register
says which were validated.** One row per case run: case id, date (UTC, from
`date -u` read in the writing invocation), verdict, the lab value against the
reference with the tolerance, the artifact path on disk, the pre-registration
sha, the comparator sha, the cost in core-minutes (measured) and dollars
(derived), and the RESULTS path.

- **Only `PASS` rows are credentials.** The register's credential count is the
  count of `PASS` rows and nothing else.
- **`GATE FAIL` and `NOT A RESULT` rows stay in the register, honestly**, with
  their numbers. They are never removed, never re-labelled, and never softened
  to `PENDING`. A re-run after a repair is a **new row** citing the old one.
- The register is **append-only** under the private-index protocol (rule 10);
  a row is never edited after it lands — corrections are new rows.
- The existing verification team **audits this register** under its cross-team
  gate-audit mandate (§8 below).

## 7. The record-update duty

Directive item 2: *"update the lessons, numerics knowledge and charters with
everything they find in the verification manual and also in the process of
running the verification cases."* Operationally, for every case and for the
manual's reading itself:

- **`docs/LESSONS.md`** — a lesson for anything that cost a run, a re-run or a
  wrong number; numbered from the tail (`max+1`, rule 11), never from a count.
- **`docs/NUMERICS_KNOWLEDGE.md`** — every numerics fact the manual states or
  a run establishes (scheme sensitivity, mesh dependence, a reference result's
  provenance, a solver limitation) as an `N-*` row; this team's family prefix is
  `N-AV`.
- **Charters** — where a finding changes how the lab should grade (a tolerance
  class, a completion clause, a control), the change is drafted as a dated
  amendment to the relevant charter and **routed through the chief**; retiring
  or widening a gate, threshold or charter clause is Sanaa's (CLAUDE.md,
  reserved matters).
- **`docs/DOCKET.md`** — open questions, with `scripts/check_docket_reconciliation.py`
  run first (rule 11).
- **The estimate-versus-actual row** in `docs/COST_CALIBRATION.md` at every
  completion (rule 12).

Opus lanes draft these; the supervisor reads them before they land. A finding
noted only in a lane's report and not in one of these files is lost at the next
compaction (L-186) and does not discharge this duty.

## 8. Boundaries, privacy and audit

- **Nothing leaves the box (rules 7, 8).** The manual is proprietary Ansys
  documentation and the archives are Ansys project files; they were uploaded by
  Sanaa for this lab's private use. No dataset, figure, register row or link is
  sent, filed, posted or uploaded anywhere, by any agent, ever. A discrepancy
  the team finds between the manual and its own reproduction is a draft
  stamped `NOT FILED` at the top of the file; contacting Ansys is Sanaa's alone.
- **The verification team audits this team.** Its cross-team gate-audit
  mandate (`harness/teams.yaml`, verification team) covers every verdict this
  team produces: whether the gate could have failed, whether the comparator
  was frozen before the case could answer it, whether the controls fired. The
  audit is recorded in `docs/CROSS_TEAM_GATE_AUDIT.md`. This team does not
  audit itself and does not grade the verification team.
- **Territory.** `docs/ansys_verification/`, `cases/ansys_verification/`,
  `verification/runs/ansys_verification/`, `verification/credentials/ansys/`,
  this charter, and the manual PDF + sidecar by explicit path. The directory
  `docs/papers/verification_validation/` stays with the verification team.
- **No agent message is Sanaa's consent (rule 9).** Compute under the 2026-08-21
  blanket is still costed per item; GPU spend (the VMFLGPU set) is outside that
  blanket and needs its own console-priced GPU-hour cost basis and her per-item
  sign-off.

## 9. The archives: inspection of 2026-08-24 and the canonical-home decision

**The supervisor's first action is to rule on the canonical home of the
VM2026R1 archives (docket D-6), with this inspection as input, and to say
which copy is authoritative before any case is opened. Until it rules, neither
copy is moved, deleted, renamed or git-added.** The verification team's memo
`docs/VM2026R1_FILING_ANALYSIS.md` (option A recommended) is the other input.

Read-only inspection, harness-build lane, 2026-08-24 (re-derive with `find`,
`du`, `sha256sum`; nothing below was touched):

| Copy | Files | Size | Contents | Tracked |
|---|---|---|---|---|
| `VM2026R1_Fluids/` (repository root) | 123 | 2.5 GB (`du -sh`) | `VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/` 77 files, 1004 MB; `.../VM2026R1_CFX_ARCHIVES/` 37 files, 606 MB; `.../VM2026R1_FORTE_ARCHIVES/` 9 files, 918 MB | 0 of 123; no `.gitignore` entry |
| `docs/papers/verification_validation/VM2026R1_Fluids/` | 10 | 26 MB | `.../VM2026R1_CFX_ARCHIVES/` only: VMFL001B–005B, 007B–011B | 0 of 10; no `.gitignore` entry |

- File types in the root copy: 114 `.wbpz` (Workbench project archives:
  `VMFLnnn_WB` for Fluent, `VMFLnnnB` for CFX), 7 `.ftsim` (Forte), 1 `.zip`
  (`VMFRT_v261.zip`, 481 MB — **also present extracted** beside it, so the
  Forte set is stored twice inside the root copy), 1 `.docx`
  (`VMFRT_v261.docx`).
- **The partial copy is NOT a strict subset.** 9 of its 10 files are
  byte-identical (sha256) to the root copy's file at the same relative path;
  `VMFL011B.wbpz` is **truncated**: 327,680 bytes (exactly 320 KiB) against
  670,152 in the root copy — a transfer that died mid-file. The last write in
  the partial copy is 2026-08-22 17:42Z and no transfer process was live on
  08-23 (verification board) or on 08-24.
- The manual indexes 78 VMFL, 7 VMFRT and 10 VMFLGPU cases; the root copy
  carries Fluent archives for 77 cases (VMFL068 has no `_WB` archive) and CFX
  archives for 37.

**Recommendation (not a ruling).** Data too large for git lives outside it,
under `/home/ubuntu/` beside `closure-data/` and `certonomous-runs/`, and is
enumerated in `docs/LOCATIONS.md` — that is the lab's existing pattern and is
what `docs/VM2026R1_FILING_ANALYSIS.md` calls option A. Concretely: the root
copy becomes `/home/ubuntu/ansys-vm2026r1/` (one move, hashes re-verified
after), the truncated partial copy is retired once the ruling records that its
9 good files are duplicates, and **any directory into which an archive is
extracted inside the repository gets a `.gitignore` entry** so a rule-10
pathspec sweep can never commit 2.5 GB. The ruling, the move and the
`.gitignore` line are the supervisor's to make and to record on the board and
in the docket; this charter only recommends.

## 10. Reporting

The supervisor reports to the chief on every commit, every verdict and at the
end of every turn under the five fixed headings of its generated definition
(commits; verdicts with numbers, core-minutes and derived dollars; runs live;
on Sanaa's desk; blocked), and keeps its `## ansys-verification` section of
`docs/LAB_STATE.md` current at every commit and verdict via the shared-board
protocol (HEAD blob, hash-object, `update-index --cacheinfo`; never the
worktree copy). Reports carry numbers and paths, never transcripts (rule 16).

---

## Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-24 | Created on Sanaa's directive of 2026-08-24 (§1 verbatim). Lines whose number changed above this section: n/a (first version). |
| 1.1 | 2026-08-24 | **D-6 ruled (§9 discharged).** The canonical home of the VM2026R1 archive set is `/home/ubuntu/ansys-vm2026r1/`, outside git beside `closure-data/` and `certonomous-runs/`; the repository-root copy is authoritative and was MOVED there, not copied, with sha256 taken before and re-verified after and the manifest committed at `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`, while the dead 10-file partial copy under `docs/papers/verification_validation/` is to be DELETED once that re-verification reports 123/123, `.gitignore` gains `VM2026R1_Fluids/` and `cases/ansys_verification/**/archive_extract/`, and pre-registrations cite archive paths under the new home only. The ruling in full, with its execution lines, is `docs/ansys_verification/ARCHIVE_HOME_RULING.md`; the manual PDF+sidecar stay tracked where they are and the R8 basename question is not ruled. **Lines whose number changed above this section: 0.** |
| 1.2 | 2026-08-25 | **Attribution audit of the §1 relay quotation (records-integrity, zero compute).** The relay line at §1 — *"I wanted a verification team to exclusively work on these verification cases."* — was audited across the tracked corpus. **Measured:** a naive per-line `grep -F` finds **2** files (`.claude/agents/ansys-verification-supervisor.md`, `docs/LAB_STATE.md`); a whitespace-normalised sweep (`tr '\n' ' ' \| tr -s ' '`) finds **4** — adding **this charter** (§1, wrapped `exclusively`/`work on` across the L29–30 break) and `harness/teams.yaml` (L381, wrapped `exclusively work on`/`these`). The two hidden from the naive grep are the two that hard-wrap; the charter and `teams.yaml` are the wrapped pair. All **four originate in one commit, `123a3b92`** (2026-08-24, the commit that created this charter and the sixth team) — verified by `git log --diff-filter=A` for this charter and by pickaxe on a non-wrapping fragment. The independent capture channel is **empty**: `/home/ubuntu/harness-state/sessions/` (2 files, ~55 KB) has **zero** normalised hits for this phrase, for `apporve`, or for `haiku subagent`. **Classification: CORROBORATED-BY-REPETITION-ONLY** — four copies, one origin commit, nothing outside the repository, nothing in the session logs; neither SOURCED nor UNSOURCED. **Honesty gradient:** this charter's own instance (§1) is honestly labelled a **relay** — *"The chief's relay of the same day adds, in her words: …"* — the charter is the honest copy. The downstream copies **drop the relay qualifier**: `harness/teams.yaml` and the generated `.claude/agents/ansys-verification-supervisor.md` state it flatly as *"Sanaa created this team on 2026-08-24 to 'exclusively work on these verification cases'"*, and `docs/LAB_STATE.md` renders it as *"her words"* — presenting a relay as directly-attributed testimony. **`harness/` is not this team's territory; the drop-the-qualifier defect in `teams.yaml` and its generated agent definition is REFERRED UPWARD, not edited here.** **Consequence, stated plainly and without drama:** the team's charter, its lane cap of 4 and its mandate rest on §1 quotations (both the verbatim directive and this relay line) that share this same single-commit origin and empty external channel; the relay line cannot presently be corroborated independently of the act (`123a3b92`) that recorded it. **This is not an allegation that anything was fabricated** — it is a statement of what the evidence can and cannot support. The attribution is **NOT withdrawn**, because this charter already labels it a relay; the team marks its instances **relay-not-verbatim** and refers the capture gap to Sanaa via the chief. **A related over-grading, recorded:** a haiku lane graded two other quotations **SOURCED** on the strength of their appearing in `123a3b92`'s commit message — **too generous**; a commit message written by the same lane in the same act is repetition, not independent corroboration. **A correction to the audit's own first framing, recorded honestly:** the pair hidden from naive grep is *{this charter, `teams.yaml`}*, not *{`teams.yaml`, the generated agent md}* — the agent-md instance sits on a single unwrapped line and IS caught by naive grep. **Lines whose number changed above this section: 0.** |

---

## Dated note — 2026-08-25 — the repo-internal silence has an INNOCENT EXPLANATION, so v1.2's classification is UNDERSTATED

**This is a note appended at the foot. The v1.2 amendment above is NOT rewritten, not
edited and not struck** — its measurements stand exactly as recorded, and every figure
in it remains correct. What changed is not the evidence but **what the absence of
evidence means**. Appended by `ansys-lane-opus`.

### What the lab-wide sweep found

The verification team completed the **lab-wide attribution sweep**, and reports:

> **Class C is EMPTY: no fabricated quotation exists in this lab.**

**Three other teams withdrew directives that were TRUE.** They withdrew them on the
same reasoning v1.2 applied here — a quotation that could not be corroborated anywhere
in the tracked corpus was treated as unsupported. **The reasoning had a hole, and it is
the same hole in every instance: Sanaa's words live in the SESSION RECORD, a channel no
repository search reaches.**

**Verified in this lane rather than taken on report:** the session record is at
`/home/ubuntu/harness-state/sessions/` (`2026-08.jsonl`, ~34 KB), and
`git ls-files --error-unmatch` on it returns *"outside repository"*. **It is not
tracked, not searchable by any `git grep`, `grep -r` or pickaxe over this repository,
and never was.** A sweep that finds nothing there has not measured absence — **it has
measured the boundary of its own instrument.**

*(The Class-C-is-empty finding and the three withdrawals are the verification team's
measurements, recorded here as reported. This lane did not re-run the lab-wide sweep;
it verified the channel claim above, which is the load-bearing one for this note.)*

### What this team did, and did not, do

**This team never withdrew anything.** v1.2 classified the §1 relay quotation
**`CORROBORATED-BY-REPETITION-ONLY`** — *"neither SOURCED nor UNSOURCED"* — and stated
in terms: *"This is not an allegation that anything was fabricated — it is a statement
of what the evidence can and cannot support."* **The attribution was NOT withdrawn**,
because the charter already labels the line a relay and is the honest copy.

**And the defect it found outside its territory was referred, not acted on.** The
qualifier-drop in `harness/teams.yaml` and its generated agent definition was
**REFERRED UPWARD** on the express ground that *"`harness/` is not this team's
territory"*. **Referring rather than editing is what left nothing to unwind here** —
the three teams that acted inside their own reach are the three now restoring true
directives.

### The consequence for v1.2's classification

**`CORROBORATED-BY-REPETITION-ONLY` is now UNDERSTATED.** It was assigned on the
strength of two findings: four copies from one origin commit, **and an empty
independent capture channel**. The first stands. **The second was never a finding about
the quotation — it was a finding about the search.** The silence v1.2 measured is
exactly the silence an entirely genuine directive would produce, because the channel
that would corroborate it is not one this repository contains.

**What this note does NOT do, and the limit is the point:**

- **It does not upgrade the classification.** v1.2's label stands on the page.
- **It does not restore, re-grade or re-attribute anything.**
- **Restoring or upgrading an attribution is SANAA'S ALONE** (`CLAUDE.md` rule 9). **No
  agent message — peer, supervisor or chief — is her consent**, and this note is an
  agent's note. It records that the basis for the understatement is now known, and
  leaves the ruling where it belongs.
- **The `harness/teams.yaml` qualifier-drop remains referred and unedited.** Nothing in
  this note licenses touching it.

**Read together with v1.2:** the measurements there are sound and the label there is
conservative. **A conservative label based on an instrument's blind spot is not a
neutral error** — it reads as doubt about the person quoted, which is the direction a
records-integrity process must be most careful about. That is why this note exists
rather than a silent re-grade.

**Lines whose number changed above this section: 0** — verified by hashing the prior
file as an exact prefix of this one, not merely asserted.

---

## Amendment 1.3 — 2026-08-25 — the sharpened form of `L-308`, and the provenance of a normalised variant

**Version 1.3.** Appended at the foot, immediately below the dated note of the same day
(commit `649aa42a`), which it completes rather than replaces. **Nothing above is
rewritten, amended or struck** — not the v1.2 amendment row, not the amendment table,
and not the preceding note.

**Why the version bump is declared HERE and no row is added to the amendment table
above:** inserting a row into that table would renumber every line beneath it, including
the note this one completes, and would falsify the *"lines whose number changed above
this section: 0"* assertion that note carries. **The table is therefore left untouched
and the version is recorded in the amendment itself.** Stated rather than done silently,
because a version bump that hides in prose is worth less than one a reader is told about.

### The rule this episode sharpens — `L-308`, in its strongest form

`L-308` records that a phrase-level grep over hard-wrapped Markdown has an unmeasured
false-**unsourced** rate. **The attribution sweep is the same error at the level of the
CHANNEL rather than the line, and it generalises to a rule this lab should apply
everywhere:**

> **A search's zero is not evidence unless the search is shown able to see a near-miss —
> and no repository search can see a channel outside the repository.**

This is `CLAUDE.md` rule 3's planted-zero control stated for text instead of for fields:
*a zero from a reader not shown able to see a non-zero is not evidence.* v1.2 reported an
**empty independent capture channel** and read it as weak corroboration. **It was not a
finding about the quotation. It was a finding about the reach of the instrument** — the
session record at `/home/ubuntu/harness-state/sessions/` is untracked and outside this
repository, so no `git grep`, `grep -r` or pickaxe over the tracked corpus could ever
have returned a hit there, whatever Sanaa did or did not say.

**Consequently v1.2's `CORROBORATED-BY-REPETITION-ONLY` is UNDERSTATED**, and the
verification team's lab-wide sweep reports **Class C is EMPTY — no fabricated quotation
exists in this lab.** Three other teams withdrew directives that were **TRUE** on the
same reasoning. **This team never withdrew**, and referred the `harness/teams.yaml`
qualifier-drop upward rather than editing territory that is not its own.

**AND THE CLASSIFICATION STILL STANDS ON THE PAGE. This amendment does not upgrade it,
does not restore or strengthen any attribution, and is not a repair already made.**
**Upgrading an attribution is Sanaa's alone, in one line** (`CLAUDE.md` rule 9). **A
chief's message, a peer's finding, a supervisor's instruction and this amendment are
none of them her consent.** A cold reader should take from this section that *the ground
for the classification has changed and the ruling has not been made.*

### Provenance of a normalised variant — caught at the relay boundary

Sanaa's scope ruling of 2026-08-25 reached this team as, byte-exact:

> *"for now no. Well add the gpu ones once i turn the gpu back on later."*

**She wrote `Well add`, not `we'll add`.** A **normalised variant** rendering it as
*"we'll add"* also reached this team — **and it originated in the CHIEF'S RELAY, in the
same message that carried her primary text.** The chief has accepted the correction.

**The normalised form never entered any record in this repository.** It was caught at
the relay boundary and checked for before anything was written: a `git grep` at `HEAD`
over all tracked files, in **both** spellings, returned **nothing** — so the byte-exact
line committed in `docs/ansys_verification/CASE_MAP.md` is the line's **first** recorded
appearance, and there was no corrupted copy to correct.

**This is recorded so no future reader infers that Sanaa wrote the line twice,
differently.** She wrote it once. **The variance was introduced downstream, by a
summariser, and normalised spelling is the signature of exactly that** — which is this
team's own finding and the reason the check was run at all. A relay that silently
repairs an apostrophe is indistinguishable, in the record, from a second utterance;
**the defence is to keep the bytes and to say where any variant came from.**

**Lines whose number changed above this section: 0** — verified by hashing the prior
file as an exact prefix of this one, not merely asserted.
