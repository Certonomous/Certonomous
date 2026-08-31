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

---

## Amendment 1.4 — 2026-08-25 — two standing setup obligations, and the record-update duty gets a moment attached

**Version 1.4.** Appended at the foot, below Amendment 1.3 of the same day. **Nothing above
is rewritten, reworded, widened, struck or renumbered** — not §5, not §7, not the amendment
table, not either preceding amendment. This amendment **APPENDS clauses only.** Retiring or
widening a gate, threshold or charter clause is Sanaa's alone (`CLAUDE.md`, reserved matters),
and nothing here does either.

**The version bump is declared here and no row is added to the amendment table above**, for
the reason Amendment 1.3 gives: inserting a row would renumber every line beneath it and
falsify the `lines whose number changed above this section: 0` assertion that 1.3 and the note
before it both carry.

### The directive this amendment discharges

Sanaa's ruling of 2026-08-25, her own session turn, received via the chief, **byte-exact and
unnormalised — her missing space in `That'sfine` is preserved and is not corrected**:

> That'sfine the ansys verification team should just make sure to update its charters and respective docs going forward.

It answers this team's one `NOT DONE` of 2026-08-24: **no charter was updated** with that
day's findings, against §7's record-update duty.

**Her ruling is PROSPECTIVE.** *"going forward"* attaches the duty from here. **The 2026-08-24
gap is closed by HER, not excused by this team**, and this team does not convert her
forbearance into a finding that there was nothing to find.

**She wrote "charters AND RESPECTIVE DOCS" — plural, and wider than this charter.** The duty
therefore reaches `docs/ansys_verification/README.md`, `CASE_MAP.md` and `COVERAGE_ROWS.md` as
well. The operative distinction, and the reason clauses A and B below are here rather than
only in `docs/NUMERICS_KNOWLEDGE.md`: **a numerics fact is looked up AFTER a disagreement; a
setup obligation must be met BEFORE the freeze.** A setup obligation filed only as a numerics
fact is in the wrong file, because the lane who needs it is writing a pre-registration and
will not go looking.

---

### CLAUSE A (appends to §5.1, changing nothing in it) — THE AXISYMMETRIC WEDGE CARRIES A MODELLING BIAS INTO THE ERROR BUDGET, BEFORE THE FREEZE

**Every pre-registration for a case run on an OpenFOAM axisymmetric `wedge` states the wedge's
geometric bias, with its sign and magnitude, in its error budget, BEFORE the case is frozen.**

An N-sided flat wedge does not represent a circular cross-section. **Two deficits, and they do
not cancel** (derivation and provenance: `N-AV9` in `docs/NUMERICS_KNOWLEDGE.md`, cited here
rather than restated, so the arithmetic has one home):

| quantity | flat wedge ÷ true circle | at a total wedge angle t = 5° |
|---|---|---|
| cross-sectional **AREA** | sin(t) / t | deficit **0.1268756046250763 %** |
| **WALL ARC** length | sin(t/2) / (t/2) | deficit **0.03172796079918827 %** |
| their **RATIO** | **sec(t/2)** | pressure drop biased **HIGH by +0.09526851633199218 %** |

**The number that reaches a Δp gate is the third row, not the first.** This is recorded as a
correction to how the finding was first summarised to this lane: *"sin(t)/t — 0.127 % at
t = 5°"* is exactly right for the **area** and is **not** the bias on the graded quantity.
Both figures reproduce the frozen
`cases/ansys_verification/VMFL003/case/system/blockMeshDict.template` header to full double
precision.

**Why this is a charter clause and not merely a numerics row: NO GRID REFINEMENT REMOVES IT.**
The bias is **azimuthal**. Refining axially or radially does not touch it, so it is invisible
to the Roache triple, invisible to the GCI, and invisible to every convergence check this team
runs. A case can be `CONVERGING` at a GCI of a few hundredths of a percent and still carry it
undisclosed. **It is therefore a setup obligation with a deadline — the freeze — and not a
diagnostic to be recalled afterwards.**

**Two boundaries on the clause, stated so it is not over-read:**
1. **It binds the DISCLOSURE, never the tolerance.** The clause does not widen, narrow or
   otherwise touch any gate or band. A team that discloses a +0.095 % bias against a 2.5 %
   band has discharged it; so has a team that discloses it against a 0.1 % band and says the
   band is therefore not meetable on a wedge. **What is forbidden is silence.**
2. **The sign is part of the obligation.** A bias whose direction is unstated cannot be
   subtracted from a deviation, and a reader cannot tell whether it helps or hurts. VMFL003's
   is **the wrong sign to help**: the model already under-predicts Δp, and the wedge biases Δp
   high, so the true model error is **larger** than the measured deviation.

### CLAUSE B (appends to §5, between its steps 1 and 2, and rewrites neither) — THE PRE-FLIGHT SMOKE TEST

**After the pre-registration is committed and BEFORE the graded run starts, the case is smoke
tested: ONE timestep (or one iteration) on the COARSEST mesh of the family. A failure ABORTS
the run and is a finding, not a retry.**

**Where it runs is load-bearing:** in a scratch directory **OUTSIDE
`verification/runs/ansys_verification/`**, so it cannot create a `0/` or a time directory that
would trip `CLAUDE.md` rule 4's **age guard** — the guard refuses a case where `0` or a time
directory already exists, and a smoke test run in place would either disarm the guard or
consume the run it protects. **The smoke directory is deleted or left outside the runs tree;
it is never the graded artifact and is never cited by a record.**

**The warrant is MEASURED, and it is one sentence: a comparator `--selftest` proves the
GRADER, never the CASE and never the LAUNCHER.** Two specimens from this team's own work, both
re-verified from the records before being written into this charter:

| specimen | what passed | what failed | citation |
|---|---|---|---|
| **VMFL045 run 1** | comparator `--selftest` **45 checks, 0 failures** | the **solver died on the first timestep** | `cases/ansys_verification/VMFL045/RESULTS.md`, `PREREGISTRATION.md:592` |
| **VMFL003 run 1** | launcher's comparator `--selftest` **60 checks, 0 failures** | the case was **unrunnable** | `cases/ansys_verification/VMFL003/RESULTS.md:18,179`, `PREREGISTRATION.md:18,746` |

**In both, a green selftest was on the record while the thing it was taken as evidence for was
broken.** That is `INFRA_FAMILY_SUPERVISION_GUIDELINES.md` §1.8's rule arriving in this team's
territory — *"evidence is derived from what EXECUTED, never from what was DECLARED"* — and a
selftest is a declaration about the grader.

**AN HONEST LIMIT ON THIS CLAUSE, DISCLOSED RATHER THAN LEFT TO BE ASSUMED.** The lab's
standards book requires a new rule that will fire on the lab's own work to be **replayed
against the archive before it binds, with corpus, fire count, fatal count and behaviour on the
motivating case** (`MONITOR_STANDARD.md` standing rule 6;
`INFRA_FAMILY_SUPERVISION_GUIDELINES.md` §1.3). **This clause has a two-specimen warrant, not
a corpus replay, and it is labelled as such.** The reason it is adopted anyway, stated rather
than glossed: **a pre-flight smoke test is not a DETECTOR.** It classifies no existing log,
returns no verdict on any archived run, and cannot produce a false positive against past work
— the failure mode standing rule 6 exists to price. It costs one timestep and it aborts. **If
it is ever converted into something that grades or classifies, it acquires the replay
obligation at that moment.**

**A DEPARTURE ALREADY ON DISK, DISCLOSED.**
`verification/runs/ansys_verification/VMFL003/SMOKE_ABORT_0215Z/` is a smoke directory that
sits **INSIDE** the runs tree, holding `log.blockMesh`, `log.checkMesh` and `log.topoSet`. It
predates this clause, no clause forbade it at the time, and **it is neither moved nor deleted
here** — an unexpected artifact is inspected, never reverted. It is named so that a future
reader does not mistake it for a violation of a rule that did not exist, and so that the
clause's *outside the runs tree* requirement is not silently contradicted by the tree itself.

### CLAUSE C (appends to §7, rewriting none of it) — THE RECORD-UPDATE DUTY GETS A MOMENT ATTACHED

**Every case close-out lands a CHARTER/DOC UPDATE LINE, or an explicit `NONE` with one line of
reason.** The close-out invocation already lands the verdict, the tier, the register row, the
`docs/COST_CALIBRATION.md` row and the parent aggregates together; this line joins them and is
written in the same act.

**Why a moment, and not merely a duty.** §7 already required the updates. It was still the
one thing this team did not do on 2026-08-24. **A duty with no moment attached is exactly the
duty that shows up as `NOT DONE`** — nobody decided to skip it; there was simply never a point
at which not having done it was visible. **A close-out that silently omits the line is
indistinguishable from one that forgot**, which is why the `NONE` is explicit and carries a
reason. This is the same discipline as a register row that carries its own caveat, and the
same discipline as `MONITOR_STANDARD.md`'s refusal to let an absent line and an unrecorded
value read alike.

**Scope, per Sanaa's plural:** the line names whichever of this charter,
`docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md`, `docs/ansys_verification/README.md`,
`CASE_MAP.md` or `COVERAGE_ROWS.md` the case's findings reached, or states `NONE` and why.

### A CANDIDATE REJECTED FROM THIS CHARTER, WITH ITS REASON — because one rejected silently looks like one overlooked

**The wall-function grid constraint (`N-AV10`) STAYS in `docs/NUMERICS_KNOWLEDGE.md` and does
NOT enter this charter.** `N-AV10` records that a ratio-2 **radial** grid triple cannot coexist
with a standard wall function below R⁺ ≈ 600, so a wall-function pipe case must refine
**axially** and hold N_r fixed — as VMFL003 did, holding its wall treatment identical to
1.4e−04 across all three levels.

**Why it is not charter-grade, on the same test that admitted clauses A and B:** it is a fact
about **one model's interaction with one mesh family**, not a rule about how this team works.
A lane meets it by consulting the numerics file when it designs a wall-bounded triple, which
is exactly what a numerics fact is for. **Clause A's bias, by contrast, applies to every
axisymmetric case regardless of model, and clause B's smoke test applies to every case
regardless of physics.** Generality is the line, and it is drawn here explicitly.

### DISCLOSURES CARRIED WITH THIS AMENDMENT — the standards book was read against these clauses first

`docs/standards/` was read in full before either clause was written, on Sanaa's own instruction
of the same day. **Her GitHub link to that tree was NOT fetched** — the repository is
permanently private by her ruling of 2026-08-18 and nothing leaves this box; the local path is
the authority. The reading of record is `docs/ansys_verification/STANDARDS_READ.md`.

**It turned up NO conflict with clause A, clause B or clause C.** It turned up **four against
work this team has already frozen. They are DISCLOSED here and are NOT reconciled; no frozen
file was edited and no verdict changes:**

1. **The frozen plateau clause's SHAPE.** `grade_vmfl051.py` and `grade_vmfl045_r2.py` gate on
   `PLATEAU_TOL_MA = 1.0e-3` — an **ABSOLUTE** peak-to-peak tolerance over a **20 %-OF-RUN**
   window. `MONITOR_STANDARD.md` S13 v1.12 argues against both halves: it normalises by *the
   range the quantity spanned over the run*, and it uses a **fixed** window because *"a
   fraction-of-run window silently loosens as a run is extended, so the same case passes by
   being run longer."* Measured both ways on the same series: on **VMFL051** S13's form refuses
   **all three** levels where the frozen clause refused two, so `NOT A RESULT` is **more**
   robust. On **VMFL045-R2** the **coarse** level reads **0.06100 % of its run range against
   S13's 0.02 %** — material, that case being this team's third credential. **The `PASS` is
   NOT withdrawn and is not in question**: the gate was frozen before compute and applied
   unmodified, and gates close at first compute. What it supports is the concern this team had
   **already recorded itself** — that VMFL045-R2's G column is unclean (p = 3.3862 above the
   scheme's formal order; d21 = 2.447e−04 against an L3 noise floor of 7.769e−05, ratio 3.150).
   **And the window shape bites exactly where VMFL051's obvious remedy lies:** a longer run
   makes that clause easier to pass. **A new VMFL051 registration should gate on a fixed
   window and say so.** `MONITOR_STANDARD.md` S12, applied as an independent diagnostic, fires
   on **nothing** across all six levels (drift 1.1e−06 to 1.5e−05 against a 1e−3 floor;
   monotone 0.489 to 0.592 against 0.90) — the series **wobble without travelling**, which is
   a favourable finding for both cases.
2. **Family size.** `docs/MESH_STANDARD.md` requires a **six-level** family provisioned up
   front against this team's three-level triples, citing the lab's own TMR ladder where a
   fourth rung moved the observed order from 1.0833 to 1.2587. **A tension between a standing
   rule (`CLAUDE.md` rule 5's triple) and house practice, referred and not resolved here.** It
   independently prescribes the fourth VMFL045 level this team had already named.
3. **A measurement the record did not carry.** Neither frozen comparator reads Courant at all
   (zero mentions in both). Both compressible cases run `rhoCentralFoam` under
   `adjustTimeStep`, `maxCo 0.4`. Per `docs/standards/MESH_STANDARD.md` §7.4 the figure is the
   **maximum over the run**, never the final line: **VMFL045-R2 L3 reads 0.412936 max against
   a 0.400207 final line — +3.23 %, above S8's calibrated 2 % tolerance** and 8.0× the largest
   overshoot in the archive that tolerance was calibrated on. **Level-dependent** (+1.48 %
   coarse → +3.23 % fine), which makes it a **candidate** contributor to the above-formal
   observed order — **a hypothesis for the fourth level to test, not a conclusion.** No verdict
   changes: the frozen gate has no Courant clause, and S8 is itself unwired with no replay line.
4. **Research is not publication.** `PROBLEM_RESEARCH_PROTOCOL.md` §4 obliges a **docket
   proposal, not a memo**, once this team acts on Sanaa's *"see if that's a raised issue
   online/in the litterature"* — and its own §4.4 reads *"Drafts only: … never post, comment,
   or create accounts."* **SUBMISSIONS REMAIN PARKED** (`CLAUDE.md` rule 7, §8 above). The same
   file says **nothing whatever about preconditioners**, so her rule-2 preconditioner clause
   has no standard behind it in this lab; **reported as a gap, not filled here.**

**One gap in this team's own compliance, measured and named:** `docs/standards/MESH_STANDARD.md`
§6 requires a `birth_certificate.json` beside every mesh entering a pre-registration or a
ladder rung. This team has **23 `log.checkMesh` files and zero certificates** — **CHECKED BUT
UNCERTIFIED**, the infrastructure family's own phrase for exactly this shape. Every metric the
certificate would carry is measured and on disk, and **all 23 meshes meet every enforced §3
gate with margin** (worst non-orthogonality 14.976° against 70°; worst skewness 0.39963 against
4; worst aspect ratio 40.038 against a 1000 advisory). Minting retrospective certificates is a
change to run directories and is **not done here**; it is named so it is not mistaken for a
gate that was passed.

**Lines whose number changed above this section: 0** — verified by hashing the prior file as
an exact byte prefix of this one, not merely asserted.

---

## Amendment 1.5 — 2026-08-30 — **§2f.3's SCOPE IS SETTLED FOR THIS TEAM; a registration may not reach its freeze commit with an OPEN gate question; a queue state is a READING WITH A SHELF LIFE; and every runnable item is FILED AND COMMITTED, not held in an agent's head**

**Version 1.5.** Appended at the foot, below Amendment 1.4. **Nothing above this line is
rewritten, amended or struck** — not §1's verbatim directive, not the §3 roster, not the
§5 verdict path, not the §6 register rules, not the §8 lane-cap exception, and not
Amendments 1.3 or 1.4. Every clause below is **additive**. The version bump is declared
here rather than by editing the §283 amendment table, which is the form Amendment 1.3
established for this file and which is followed unchanged.

Written by `ansys-verification-supervisor` personally under **Sanaa's directive of
2026-08-30** (verbatim at `etc/sessions/2026-08-30T2247Z_sanaa_directive_continuous_overnight.md`,
commit `4195b27b`): *"each teams updates their own charters and stanrdards … all jobs
always queued such that if any teams dies the work continues."* **Every clause here was
paid for by a specific failure in the preceding 48 hours, and each names its failure.**
**Nothing below retires, widens or narrows a gate, threshold, band, cap or charter clause
— those remain Sanaa's alone (`ESCALATION_CHARTER` §4.1, D539).**

### §11.1 `VERIFICATION_CHARTER` §2f.3 DOES NOT REACH A REGISTRATION THAT DECLARES A TRIPLE — this team's standing reading, so it is not re-litigated case by case

**Ruled 2026-08-30 on VMFL069 §3.3, full record at
`cases/ansys_verification/VMFL069/SUPERVISOR_RULING_SEC3.3.txt`, commit `b1b7cfc1`.**

> **§2f.3's CONTINUUM cap — *"`GATE REACHED` maximum. `PASS` is unavailable"* — is the
> NO-TRIPLE ceiling. It does not cap a limb of a registration that declares a Roache
> triple and whose triple returns `CONVERGING`. Such a limb is graded by `CLAUDE.md`
> rule 5 step 3.**

The scope is set by the clause's own column heading, which reads ***"ceiling WITHOUT a
triple"*** (`VERIFICATION_CHARTER.md:2419-2421`), by §2f's own title *"A REGISTRATION
THAT DECLARES NO ROACHE TRIPLE"* (`:2383`), and by the CONTINUUM row's stated ground:
*"from which discretisation error is not separable **without a triple**."* Where a
`CONVERGING` triple exists the error **is** separated and bounded by the GCI, so the
condition the cap exists to cover does not obtain. §2f.2 (`:2401-2411`) disables only
rule 5's **limb (2)**, and only for a no-triple registration; **limb (1) always fires.**

**THE LIMIT OF THIS CLAUSE, STATED SO IT IS NOT OVERREAD — and it is the half that
matters most:**

1. **This is a reading of an existing clause's SCOPE, not an amendment to it.** §2f.3's
   row is untouched. A team reading a charter clause to determine whether it reaches
   their case is doing what every registration must do; **weakening the clause would be
   Sanaa's and is not done here.**
2. **§2h.3 (`:2757-2762`) REFERS TO SANAA** the separate question of whether an
   exact-solution reference should be `PASS`-capable **in a NO-TRIPLE registration**,
   and holds §2f.3's cap untouched meanwhile. **This team does not decide that question
   and no case of ours may claim to have decided it.** §2h is the floor-demonstration
   clause for no-triple registrations; a case of ours that invokes §2h is governed by
   §2h.4's five conditions and by that referral, **not by §11.1.**
3. **The cap still binds in full wherever the ground holds**: any limb with no triple,
   any limb whose triple is not `CONVERGING`, and — per this team's own VMFL063
   registration — **any limb whose reference is EXPERIMENTAL is capped at `GATE REACHED`
   even on a converging triple**, because a triple bounds discretisation error and says
   nothing about model-form error.
4. **A limb that cannot be classified is CONTINUUM by default** (§2f.3's own words), and
   that default is not softened by anything here.

**AND THE REASON A CEILING IS NOT SIMPLY SET AS LOW AS POSSIBLE**, which is the finding
behind this clause: the amendment declined on 2026-08-30 would have **tightened** the
ceiling. It could not have been gate-fitting — it made the best available row worse.
**It was declined anyway, because an unnecessarily capped row is as inaccurate as an
overclaimed one.** §2f.3 itself declined a blanket cap for exactly this reason, as
*"punitive rather than accurate"* (`:2415-2417`). **A ceiling is the one the charter
imposes, never the most conservative one available**, and "we were being careful" is not
a defence for a wrong label in either direction.

### §11.2 A REGISTRATION MAY NOT REACH ITS FREEZE COMMIT WITH AN OPEN GATE QUESTION

**The failure:** VMFL069's pre-registration was committed at `4e4819ab` carrying a §3.3
headed *"The one interpretive call, flagged for the supervisor"* — a question whose two
answers gave **different ceilings on all three limbs** — while that same section said the
call *"must be made **before** the freeze commit, never after."* **The document went to
its own freeze in breach of its own deadline**, and the question was still open when the
2026-08-28 session limit killed the fleet, leaving a frozen registration whose gate no
reader could state.

> **A pre-registration is not freezable while any clause of it defers a gate, band,
> threshold, cap, level, ceiling or label to a later decision. The supervisor rules
> BEFORE the freeze commit, and the ruling is IN the frozen bytes or in a record
> committed no later than they are. A section that reads "flagged for the supervisor"
> is a BLOCKER on the freeze, not a note inside it.**

It damaged nothing this time — nothing had run and the frozen ceilings turned out to be
the correct ones — **and that is precisely why it is written down now rather than after
it costs a verdict.** A registration with an open gate is indistinguishable, at grading
time, from one whose gate was chosen after the answer arrived; **the freeze's entire
evidentiary content is that the gate could not have been fitted, and a deferred gate
forfeits it.**

### §11.3 A QUEUE STATE IS A READING WITH A SHELF LIFE — re-derive it, never carry it forward

**The failure, and it cost two days:** on 2026-08-28 this supervisor boarded VMFL063 as
**`PENDING`, correctly held** by the runner's 85 % busy ceiling. **That was true when
written and false forty minutes later.** The runner launched it at **17:41:41Z**; it ran
to completion at **17:55:34Z**; the fleet died to the 429 at 18:05Z, ten minutes after
it finished, and **the run sat ungraded for two days behind a board that said `PENDING`.**

This is the exact inverse of the trap this team already recorded — *occupancy read as
progress*, retracted on 2026-08-28 — and the inverse cost more, because **a wrong
"running" is caught by the next check while a wrong "held" invites no check at all.**

> **A held, queued or pending state is never carried into a new session, a new block or a
> report without being re-derived at the moment it is written. On resuming, the FIRST
> question about any queued item is "did it launch while nobody was watching", answered
> from the run root and the item's own named log — never from the board's last word.**

**And the corollary that would have caught it in seconds:** a queue entry that has left
the top-level queue directory has been **moved by the runner**, and the move is itself
evidence of launch. `verification/queue/ansys-verification/launched/` is the first place
to look, before the run root.

### §11.4 EVERYTHING RUNNABLE IS FILED AND COMMITTED IN THE QUEUE — the queue carries the plan, not the agent

**Sanaa, 2026-08-30, verbatim:** *"all jobs always queued such that if any teams dies the
work continues."* Measured at 22:48Z that night: **all six team queues held 0 pending
entries while the runner daemon (pid 881) was alive and idle** — the box sitting idle,
which the 2026-08-26 detached-runner ruling names as the failure.

> **Every case this team has frozen and can run is filed as a queue entry at
> `verification/queue/ansys-verification/` TOP LEVEL and is COMMITTED. An uncommitted
> queue entry is not filed — it dies with the working tree. The queue, not the
> supervisor's context, carries this team's plan, and it must be readable by an agent
> that has never met this team.**

Two traps are now standing requirements of any entry this team files, both already paid
for on 2026-08-28:

- **`cwd` points at the RUN ROOT, never the case directory.** `scripts/queue_runner.py`
  writes `STATUS.<case_id>` (`:496`), the wrapper stdout (`:522-523`) and
  `CAP_OVERRUN.txt` (`:611`) **into `cwd`**. Pointing `cwd` at the case directory drops
  runtime artefacts beside the frozen pre-registration, comparator and inputs. **The
  validator SUGGESTS the case directory; a validator's suggested remedy is a suggestion,
  not a ruling.**
- **`prereg_commit` names the commit the frozen files actually match**, verified by
  hashing each file on disk against its blob at that commit **before** enqueueing, so the
  launcher's own freeze check (`run_*.sh` launch-time HEAD-blob comparison) will pass.

**FREEZE-AHEAD.** Sanaa's floor of 3 frozen-and-ready items is a floor on **this team's
throughput**, not a target. **Freeze-ahead is re-derived and reported in every board
block**, and falling below the floor is named as a planning defect of the supervisor's,
never of the box's.

**AND WHEN THE ASSIGNED CASES ARE DONE** (Sanaa, same directive): the supervisor
**originates new research proposals and launches them** — still pre-registered, frozen by
sha before compute, costed in core-minutes per rule 12, graded under the strict completion
rule, the planted-zero control and the fixed vocabulary, and recorded in the register
whatever the verdict. **SUBMISSIONS REMAIN PARKED** (`CLAUDE.md` rule 7, §8 above);
originating research is not publishing it.

### §11.5 IN THIS TERRITORY, A FILE'S STATE IS ASSERTED AGAINST `git show HEAD:<path>` — NEVER AGAINST `git status` OR `git diff HEAD`

**The failure:** on 2026-08-30 the shared `.git/index` was found to have been last written
**2026-08-27T21:57:59Z**, three days behind HEAD, holding **389 staged deletions** —
**123 in this team's territory, 122 of those files still present on disk**, including the
entire frozen VMFL069 package. Because `git diff HEAD` takes tracked-ness from the index,
`git diff --stat HEAD -- cases/ansys_verification/VMFL069/` reported
**`16 files changed, 3021 deletions(-)` for files sitting intact on disk.** **A lane of
this team read that output and reported the case deleted.** It was not.

> **No agent of this team asserts that a file is missing, deleted, modified or clean on
> the evidence of `git status`, `git diff HEAD`, or any porcelain that consults the shared
> index. The comparison is against `git show HEAD:<path>` or `git hash-object` versus
> `git rev-parse HEAD:<path>`, and the disk is read with `test -e` / `find`.**

This is the same shape as the two failures already on this board — **a grep measuring its
own pattern**, and **a watcher matching the watcher**: an instrument reporting its own
stale state as a fact about the world. **The index is never repaired by this team** —
`CLAUDE.md` rule 10 makes it the chief's call — and the private-index protocol with its
**post-commit** `git diff HEAD~1 HEAD --stat` verify is what makes committing safe while
it is broken. **The post-commit verify is not optional and is not satisfied by the
pre-commit `diff-tree` assertion**: the CAS proves the parent is current and says nothing
about the tree.

---

**Lines whose number changed above this section: 0** — verified by hashing the prior file
as an exact byte prefix of this one in the same invocation as the write, not merely
asserted.

---

## Amendment 1.6 — 2026-08-31 — **§11.1's REFERRAL IS CLOSED, IN THIS TEAM'S FAVOUR, BY SANAA; THE TEST AT REGISTRATION IS SAMENESS OF MODEL AND NEVER EXACTNESS OF ALGEBRA; AND A BARE `§2h.6` CITATION IS BANNED IN THIS TERRITORY BECAUSE THE LABEL NOW DENOTES TWO DIFFERENT RULES**

**Version 1.6.** Appended at the foot, below Amendment 1.5. **Nothing above this line is
rewritten, amended or struck** — not §1's verbatim directive, not the §3 roster, not the
§5 verdict path, not the §6 register rules, not the §8 lane-cap exception, and not
Amendments 1.3, 1.4 or 1.5. **§11.1 is not edited**, including the point 2 this amendment
reports as overtaken; it stands on the page and §12.1 records what happened to it. Every
clause below is **additive**. The version bump is declared here rather than by editing the
§283 amendment table, the form Amendment 1.3 established for this file.

**Nothing below retires, widens or narrows a gate, threshold, band, cap or charter clause.**
Those remain Sanaa's alone (`ESCALATION_CHARTER` §4.1, D539). **The rule recorded here is
hers, not this team's**, and this amendment does no more than carry it into the place where
this team's registrations are written.

### §12.1 THE REFERRAL AT §11.1 POINT 2 IS CLOSED, AND THIS TEAM DID NOT CLOSE IT

**§11.1 point 2 committed this team to a silence:** *"This team does not decide that
question and no case of ours may claim to have decided it."* **That silence was correct
and is now spent.** Sanaa ruled the referral on 2026-08-31; `VERIFICATION_CHARTER` v1.27
carries it as `§2h.6.1`–`§2h.6.6` at commit `27a49bda`, on her verbatim words captured at
`5dd94f4f`.

> **`§2h.6.1`** — *"A reference that is the EXACT (or manufactured) SOLUTION OF THE SAME
> CONTINUUM PDE THE SOLVER DISCRETISES is `PASS`-capable, when §2h.4's five conditions are
> met and declared in the registration before compute. A reference drawn from a DIFFERENT
> MODEL — nozzle relations, shock tables, lumped or series-resistance paths, correlations,
> experiment — CAPS AT `GATE REACHED`, HOWEVER EXACT ITS OWN ALGEBRA."*

**THE AUTHORITY CHAIN WAS WALKED AT SOURCE, NOT TAKEN FROM THE RELAY.** This team learned
of the ruling from `verification-supervisor`, and a peer's message is not Sanaa's consent
(`CLAUDE.md` rule 9). The supervisor therefore read `27a49bda` and the amendment text
personally before writing a line of this clause. **The relay proved accurate in every
particular and nothing in it was overstated** — that is a finding about this instance, not
a licence to skip the read next time.

**THE INSTANCE.** `§2h.6.4` confirms **`VMFL038-R2` limb A STANDS AS GRADED**, and its
`PASS`-capability is **permanent law rather than the interim classification** its standing
rested on until today. **No number on that row moves and none needed to.** What changed is
that the row's ground no longer depends on a ruling that had not been made.

### §12.2 THE QUESTION THIS TEAM ASKS AT REGISTRATION, AND IT IS NOT "HOW EXACT IS THE REFERENCE"

**The discriminating question is *is this the solution of the equations my solver is
discretising?*** — never *how exact is this reference?* **Those two come apart precisely
where the cap matters**, and an Ansys verification manual is an unusually rich source of
places where they do.

**THE HAZARD IS SPECIFIC TO THIS TEAM'S SOURCE MATERIAL, WHICH IS WHY IT IS WRITTEN DOWN
HERE.** A good number of VM cases carry closed-form reference results that are exact for a
**reduced** model rather than for the PDE the lab's solver integrates. A closed-form
isentropic nozzle relation is unimpeachable algebra for quasi-1D isentropic flow while the
solver discretises 2D/3D RANS; a normal-shock table is exact for the Rankine-Hugoniot jump
conditions, which is not the system a shock-capturing scheme integrates across a smeared
numerical shock. **In both the algebra is perfect and the referent is the wrong object.**
Under `§2h.6.1` those cap at `GATE REACHED` however clean the algebra, and the residual
they leave is **model-form error**, which no grid triple bounds.

**WHERE IT IS SETTLED: IN THE REGISTRATION, BEFORE COMPUTE. NEVER AT GRADING.** This is
`§11.2` applied to the reference rather than to the gate — a registration may not reach its
freeze commit with an open gate question, and *"which model is this reference the exact
solution of?"* **is** a gate question, because its two answers give different ceilings.
Every registration from this team therefore states, on its face and before the freeze:

1. **the continuum model the lab's solver discretises for this case**, named as equations;
2. **the model the manual's reference number is the exact solution of**, named the same way;
3. **whether those are the same model**, answered `SAME` or `DIFFERENT`, with the reasoning; and
4. where `SAME` is claimed and `PASS` is sought, **`§2h.4`'s five conditions declared
   explicitly** — all five still bind and none is softened by `§2h.6`.

**A limb whose answer to (3) is `DIFFERENT`, or which cannot be classified at all, is
registered at `GATE REACHED` from the outset.** `§2f.3`'s default — unclassifiable is
`CONTINUUM` — is untouched, as is `§11.1` point 4.

**AND THE CEILING IS THE ONE THE CHARTER IMPOSES, NEVER THE MOST CONSERVATIVE AVAILABLE.**
`§11.1`'s closing finding governs this clause in both directions: an unnecessarily capped
row is as inaccurate as an overclaimed one, and *"we were being careful"* is not a defence
for a wrong label either way. `§12.2` is not an instruction to cap by reflex; it is an
instruction to **classify**, and to do it where it can still be got right.

### §12.3 A BARE `§2h.6` IS NEVER CITED IN THIS TERRITORY — THE LABEL DENOTES TWO RULES

**MEASURED, at `docs/charters/VERIFICATION_CHARTER.md` as of `27a49bda`:** the label
`§2h.6` is occupied twice.

- **v1.19, 2026-08-27, line 2882** — `§2h.6 NON-RETROACTIVITY`.
- **v1.27, 2026-08-31, line 3604ff** — `§2h.6.1`–`§2h.6.6`, the exact-PDE rule.

**Four standing citations already point at the v1.19 meaning** and on a plain reading now
resolve to the wrong clause: lines `2895`, `2974`, `3104` (*"NOT RETROACTIVE (§2h.6's
principle...)"*) and `3588` (*"the same non-retroactivity §2h.6, §2i.4 and §2j.4"*).
**The sharp edge is inside the new amendment itself:** `§2h.6.4` is headed *"IT IS
PROSPECTIVE"*, which is the doctrine of the **old** `§2h.6` — so one amendment uses the
same label for the rule it states and for the rule it relies on to bound it.

> **RULE. No pre-registration, register row, ruling or record of this team ever cites a
> bare `§2h.6`. The citation form is `VERIFICATION_CHARTER §2h.6.1 (v1.27, 2026-08-31, the
> exact-PDE rule)`** — subclause, version, date and name. It is unambiguous whichever way
> the label is later resolved, and **it survives a renumber**, which a bare label does not.

**WHY THIS IS NOT PEDANTRY, and it is the reason the rule is here rather than in a note.**
Under `§2h.6.1` a `PASS`-capable registration must declare its ground **before compute**,
which means citing the clause by number on a document that is then **frozen**. A bare
`§2h.6` in one of ours would name two rules, **one of which defeats the claim it is offered
to support**. A frozen document cannot be repaired afterwards (`CLAUDE.md` rule 6,
`VERIFICATION_CHARTER` §2d), so the citation must be unambiguous **at the freeze or not at
all.**

**THE DEFECT IS REPORTED, NOT REPAIRED, AND THE REPAIR IS NOT THIS TEAM'S.**
`VERIFICATION_CHARTER` belongs to `verification`; whether the fix is a renumber of the new
clauses, of the old, or a disambiguating note is theirs, and whether renumbering a clause
that four live citations depend on is Sanaa's under D539's logic is theirs to judge.
**This team changed nothing in their file and proposed no number.** `§12.3` binds only
this team's own citations, which is the part this team may bind.

### §12.4 WHAT THIS AMENDMENT DOES NOT DO

- **It creates no retrospective `PASS`.** `§2h.6.4` is prospective: a row capped at
  `GATE REACHED` before 2026-08-31 is **not** promoted, and **no row in the ANSYS
  VALIDATION REGISTER is promoted, demoted or re-graded by this amendment.** The
  availability of `PASS` is a property of a registration frozen **after** the rule and
  declaring `§2h.4`'s conditions before compute.
- **It does not disturb `§11.1` points 1, 3 or 4**, which stand in full. **Point 3's
  experimental cap is CONFIRMED rather than weakened** — `§2h.6.1` names experiment among
  the different-model references that cap at `GATE REACHED`, which is the same conclusion
  this team reached independently on its own `VMFL063` registration and for the same
  reason: a triple bounds discretisation error and says nothing about model-form error.
- **It does not weaken `CLAUDE.md` rule 5.** A level not iteratively converged or not
  plateaued is `NOT A RESULT` whatever the referent, and the one-way conversion is
  unchanged. `§2h.6.6` says so explicitly and `§2f.2`'s *"no triple never means no rule 5"*
  is untouched.
- **It does not license a continuum claim.** `§2h.4` condition 4 tests the registration's
  own sentence: **a floor demonstration WORDED as a continuum claim IS a continuum claim**,
  however impeccable its referent. This team's registrations are read against their own
  wording, not against their intent.
- **It does not reach `§2h.5` / `T9a-R1c`.** `§2h.6.5` flags that a series-resistance
  referent may sit on the wrong side of `§2h.6.1` and refers the question to
  **heat-transfer**. That is their rung and their registration; **this team offers no view
  and takes none.**

---

## Amendment — v1.7, 2026-08-31 — **§12.5: THE EXACT-PDE RULE MOVED TO `§2h.8.1`, AND THE TEAM THAT REPORTED THE DEFECT IS THE TEAM THAT THEN MIS-CITED IT**

**Appended at the foot. No existing line edited. Lines whose number changed above this section: 0.** `§11.1` and `§12.1`–`§12.4` stand unaltered on the page, including `§12.2`'s original citation at line 901, which this section supersedes rather than rewrites.

### §12.5.1 THE RENUMBERING, AND THE ONLY FORM PERMITTED IN THIS TERRITORY

`VERIFICATION_CHARTER` v1.28 `§2h.8.1` (line 3750) ruled that **`§2h.6` denotes NON-RETROACTIVITY (v1.19) and nothing else**, and that **the exact-PDE rule is `§2h.8`**. Its six subclauses map **one-to-one and in order** onto the v1.27 text — `§2h.6.1`→`§2h.8.1` through `§2h.6.6`→`§2h.8.6` — and **the words of each are unchanged.** `§2h.7` was not free; v1.19 gave it to the `§2g.4` narrowing.

**THE SUBSTANCE OF THE RULE DID NOT MOVE. ONLY ITS ADDRESS DID.** A reference that is the exact or manufactured solution of the **same continuum PDE the solver discretises** is `PASS`-capable under `§2h.4`'s five conditions declared before compute; a reference from a **different model** caps at `GATE REACHED`, however exact its own algebra. **The test remains sameness of model, never exactness of algebra.**

**In this territory the ONLY permitted form is:** `VERIFICATION_CHARTER §2h.8.1 (v1.28, 2026-08-31, the exact-PDE rule)`. `§12.3`'s ban on a bare `§2h.6` is **REAFFIRMED AND WIDENED**: a bare `§2h.6` was already forbidden because the label named two rules at once; it is now additionally **the wrong rule**, and citing it in a `PASS`-capable registration would name non-retroactivity in support of an exact-PDE claim.

### §12.5.2 `§12.2`'s CITATION IS UPDATED; NOTHING IT DECIDES CHANGES

`§12.2`'s registration precondition is **unchanged in every particular**: every registration still names the continuum model the solver discretises, names the model the manual's reference is the exact solution of, answers **`SAME` or `DIFFERENT`** with reasoning, and where `SAME` and `PASS` are claimed declares `§2h.4`'s five conditions — **all before the freeze.** Only the address of the governing rule is restated, from `§2h.6.1` to `§2h.8.1`.

**NO ROW IS PROMOTED, DEMOTED OR RE-GRADED. NO REGISTER BYTE CHANGES.** `§2h.8.4` expressly preserves records already frozen citing the old address; those citations stay valid and are **not** to be retro-corrected. `§11.1`'s experimental cap is **CONFIRMED**, not weakened.

### §12.5.3 ⚠ THE FINDING IS ABOUT THIS TEAM, AND IT IS NOT FLATTERING

**This renumbering exists because this team reported the defect.** On 2026-08-31 this supervisor found `§2h.6` labelling two different rules at once — v1.19's non-retroactivity at line 2882 and v1.27's exact-PDE rule at line 3604 — reported it rather than repairing another team's charter, and `verification` ruled it.

**Hours later, this supervisor issued a `§12.2` `SAME` ruling for `VMFL007-R3` citing the superseded `§2h.6.1`.** It was caught by a lane reading the charter at source, before the freeze, and corrected in the draft.

> **THE LESSON, and it is the same one this team learned twice today in different clothes: A TEAM THAT FINDS A CITATION DEFECT IS NOT THEREBY IMMUNE TO IT.** A cited number is not a checked number — that phrase was written into `REPAIR_QUEUE.md` this evening after both `§2n` class numbers in it proved wrong, and it applies with full force to the supervisor who wrote it. **The address must be re-read at source at every freeze, never recalled from the session that reported it.**

**WHY IT MATTERS OPERATIONALLY AND IS NOT MERE TIDINESS:** a `PASS`-capable registration cites its ground on a document that is then **FROZEN**, and a frozen document cannot be repaired afterwards. Had the `VMFL007-R3` freeze landed on schedule, this lab's next credential would have rested on a citation naming the wrong rule — one that decides nothing about referents and would have offered no support at all.

| amendment | v1.7 |
|---|---|
| clause added | **`§12.5`** (`§12.5.1`–`§12.5.3`) |
| lines changed above | **0** |
| verdicts changed | **0** · gates | **0** · bands | **0** · caps | **0** · re-grades | **0** |
| register bytes changed | **0** |
| citations corrected | **1**, pre-freeze, in a draft |
