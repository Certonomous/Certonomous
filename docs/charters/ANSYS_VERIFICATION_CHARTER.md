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

---

## Amendment — v1.8, 2026-09-02 — **§11.4's CWD RULING SURVIVES INTACT; ITS THREE `queue_runner.py` CITATIONS AND ONE FILENAME DO NOT. AND A LANE FOUND IT, NOT THE SUPERVISOR WHO WROTE IT.**

### §13.1 THE CORRECTED CITATIONS

`§11.4` justifies its `cwd`-points-at-the-run-root ruling by naming three places where
`scripts/queue_runner.py` writes into `cwd`. **All three line numbers have moved and one of
the FILENAMES has changed.** Read at source by the supervisor personally, at HEAD, on
2026-09-02:

| §11.4 says | at source today |
|---|---|
| `STATUS.<case_id>` at `:496` | **`STATUS.queue.<case_id>` at `:509`** — the *name* changed too |
| wrapper stdout at `:522-523` | **`launcher.queue.out` at `:510`** |
| `CAP_OVERRUN.txt` at `:611` | **`CAP_OVERRUN.txt` at `:639`** |

Line 496 is now the opening line of the R5 explanatory comment (496–508); `:522-523` is a
`raise ValueError` refusal; `:611` is the cap-watch glob.

**The rename is not cosmetic and it is the substantive half of this amendment.** The runner
now writes `STATUS.queue.<case_id>` — a namespace **it owns** — precisely so it can never
occupy the launcher's `STATUS.<case_id>`. Per the R5 pre-registration quoted in that comment
(`verification/campaign/R5_RUNNER_STATUS_COLLISION_PREREGISTRATION.md`, frozen at `52632a2d`,
candidate (a) of its §3.2), the collision is now **impossible by construction rather than
policed by an `exists()` test** — §3.1 refused the `exists()` design on the measured fact that
**117 of 134 entries already had a file at the old target**, so that guard would have refused
**87 %** of the lab's queue on the day it landed.

### §13.2 WHAT DOES NOT CHANGE, AND WHY THAT IS THE POINT

**`§11.4`'s RULING IS UNTOUCHED: `cwd` points at the RUN ROOT, never at the case directory,
and the validator's contrary suggestion remains a suggestion and not a ruling.** The runner
still writes runtime artefacts into `cwd`; only the addresses of the proof moved. Nothing
here alters a gate, threshold, band, cap, label, verdict or register byte, and no row is
promoted, demoted or re-graded.

### §13.3 ⚠ THE FINDING IS ABOUT THIS SUPERVISOR

`§12.5.3` closed with the sentence *"a cited number is not a checked number"*, and recorded
that this team found a citation defect in another charter and then mis-cited that very
clause hours later. **Today the same supervisor sent a lane a brief repeating `§11.4`'s three
line numbers as fact, from a charter this team OWNS, without re-reading the source — and the
lane opened its report by correcting all three.** The brief also asserted a "free win" case
that had in fact run and been graded five days earlier, and a box load of 3.0 that was 11.0
four minutes later.

> **THE RULE THIS FIXES IN PRACTICE: A CITATION IN A CHARTER THIS TEAM OWNS DECAYS EXACTLY
> LIKE ONE IN A CHARTER IT DOES NOT.** Ownership is not freshness. Line numbers into a file
> under other teams' active development are a **perishable** form of evidence, and `§11.4`'s
> were nine days old. Where the ruling is what matters, the charter now states the ruling and
> names the *behaviour* — the runner writes `STATUS.queue.*`, `launcher.queue.out` and
> `CAP_OVERRUN.txt` into `cwd` — with line numbers offered as a **finding aid, dated, not as
> the ground of the ruling.**

**And the standing dispatch practice earned its keep a third time.** Every brief this team
issues ends by ordering the lane to open with what in the brief is wrong. Three of the four
corrections above came back in a lane's first paragraph. **A brief that cannot be contradicted
returns only its own assumptions** — that instruction is why this amendment exists rather than
a wrong line number sitting in an owned charter for another nine days.

| amendment | v1.8 |
|---|---|
| clause added | **`§13`** (`§13.1`–`§13.3`) |
| citations corrected | **3 line numbers + 1 filename**, all in `§11.4` |
| rulings changed | **0** — `§11.4`'s `cwd` ruling is reaffirmed verbatim |
| lines whose number changed above this section | **0** |
| verdicts changed | **0** · gates | **0** · bands | **0** · caps | **0** · re-grades | **0** |
| register bytes changed | **0** |

---

## Amendment — v1.9, 2026-09-02 — **§14: CLAUSE B SAID WHERE A SMOKE TEST RUNS AND NEVER SAID IN WHAT SHELL. A SMOKE THAT SOURCES AN ENVIRONMENT THE LAUNCH DOES NOT GET HAS PROVED NOTHING ABOUT THE LAUNCH.**

### §14.1 THE FAILURE THAT PAID FOR THIS CLAUSE

**VMFL054 R1**, frozen at `05ec949e` after a full §3 check-4 read, was launched by the queue
daemon at **2026-09-02T21:43:57Z** and **aborted at L1 with `blockMesh` rc 127 — command not
found — at ZERO physics compute.** Its driver never sourced the OpenFOAM environment. **The
daemon runs a driver in a bare shell**; the lane's pre-flight smoke had sourced `etc/bashrc`
by hand, so the smoke executed in an environment **the real launch never receives**.

The frozen comparator **REFUSED, exit 2** — *"RUN_RC absent … cannot confirm solver rc==0
(rule 4)"* — and that limb existed only because the supervisor's §3 check-1 diff read had
found, hours earlier, that the comparator's header **claimed** an `rc` check the code did not
perform. **The check paid for itself on the very next run.**

### §14.2 WHY CLAUSE B DID NOT CATCH IT, STATED PRECISELY

CLAUSE B (Amendment 1.4) is sound and is **not** weakened here. But read it again: it fixes
**WHERE** a smoke runs — *"a scratch directory OUTSIDE `verification/runs/ansys_verification/`"*
so it cannot create a `0/` and disarm rule 4's age guard — **and it says nothing whatever about
the SHELL the smoke runs in.**

Its two-specimen warrant (VMFL045, VMFL003) prices one failure: **a green comparator
`--selftest` alongside a broken case.** This is a **third** failure and the warrant did not
reach it:

| specimen | what passed | what failed |
|---|---|---|
| VMFL045 run 1 | comparator `--selftest`, 45 checks | solver died on the first timestep |
| VMFL003 run 1 | comparator `--selftest`, 60 checks | the case was unrunnable |
| **VMFL054 R1** | **comparator selftest AND a full L1/L2/L3 smoke, rc 0, `End`** | **the DRIVER, under the launcher's own shell** |

> **The smoke genuinely EXECUTED and still proved nothing, because it executed in a different
> world.** `INFRA_FAMILY_SUPERVISION_GUIDELINES.md` §1.8 — *"evidence is derived from what
> EXECUTED, never from what was DECLARED"* — is necessary and **not sufficient**: it is
> silent on **whether the thing that executed was executed under the conditions of the thing
> it stands as evidence for.**

### §14.3 THE CLAUSE (appends to CLAUSE B, rewriting none of it)

> **A pre-flight smoke test is evidence about the launch ONLY IF it runs under the SAME
> ENVIRONMENT the launcher gives the driver: a bare shell, with nothing sourced, exported or
> inherited by the agent conducting the smoke. If the driver needs an environment, THE DRIVER
> SOURCES IT — never the operator, never the brief, never the interactive session.**

Operationally, binding on every driver this team files:
- The driver **sources its own environment unconditionally** and then **asserts the tools are
  on `PATH`** — `command -v blockMesh` / `command -v <solver>`, each aborting with a named
  message. Sourcing without asserting is a declaration; the assert is what executes.
- The smoke is run in a **deliberately stripped shell**. An agent that must source something
  to make a smoke pass has just proved the driver is defective, and reports that as the
  finding.
- **This team's reference drivers already did it right** — `VMFL063:177-178` and
  `VMFL064-R2:158-159` both source the bashrc and assert the solver on `PATH`. R1 dropped
  exactly those two lines. **The pattern existed and was not followed**, which makes this a
  charter clause and not merely a lane's error.

**HONEST LIMIT, disclosed as CLAUSE B disclosed its own.** This clause has a **one-specimen**
warrant and no corpus replay (`MONITOR_STANDARD.md` standing rule 6). It is adopted anyway on
the same reasoning CLAUSE B gave: **it is not a DETECTOR.** It classifies no archived log,
returns no verdict on past work, and cannot produce a false positive against anything already
recorded. It costs three lines in a driver and one stripped shell.

### §14.4 CARRIED FORWARD, DISCLOSED AND NOT FIXED BY THIS TEAM

The launcher's input-integrity check **pins to current `HEAD`, not to `prereg_commit`**: it
verified R1 against `5c536341` rather than against the `05ec949e` freeze it was launched
under, and **HEAD moves under us constantly** as other teams commit. `CLAUDE.md` rule 2
requires the frozen file to be verified against **the committed blob at the pre-registration
commit**. Rule 6 is the backstop and the R2 driver carries the caveat inline. **This is another
team's tooling: REFERRED, not touched.**

| amendment | v1.9 |
|---|---|
| clause added | **`§14`** (`§14.1`–`§14.4`) |
| clause modified | **none** — CLAUSE B is appended to, not rewritten, and its warrant stands |
| rulings changed | **0** · gates | **0** · bands | **0** · caps | **0** · re-grades | **0** |
| register bytes changed | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.10, 2026-09-02 — **§15: §14.3's "STRIPPED SHELL" IS SHARPENED TO THE LAUNCHER'S ACTUAL ENVIRONMENT, BECAUSE `env -i` TESTS A WORLD THAT NEVER OCCURS**

### §15.1 THE PRECISION

`§14.3` requires a pre-flight smoke to run in a *"deliberately stripped shell"*. Read
literally that suggests `env -i`, and the drafting lane objected — correctly — that **`env -i`
is STRICTER THAN REALITY**. The queue daemon does not hand a driver an empty environment; it
hands it the daemon's own. Testing against `env -i` would force drivers to survive a world
that never occurs, and a guard that fires on conditions the system never produces trains its
reader to ignore it (`L-315`, already cited in this team's instruments).

> **The standard is the LAUNCHER'S ACTUAL ENVIRONMENT — the environment the queue daemon
> really gives the driver — and not an idealised empty one. The smoke reproduces the
> launcher's environment; it does not invent a harsher one.** Where the two differ, the
> launcher's wins, because the launcher is the thing the smoke stands as evidence for.

`§14.3`'s substance is untouched: the driver still sources its own environment
unconditionally and still asserts its tools on `PATH`, and an operator who must source
something by hand to make a smoke pass has still proved the driver defective. **Only the
target environment is named more precisely.**

### §15.2 WHY THIS IS RECORDED RATHER THAN QUIETLY REWORDED

`§14` is four hours old and already needed a correction — from the same lane whose failure
paid for it. **Under `CLAUDE.md` rule 6 the fix is a dated amendment at the foot, never an
edit to `§14.3` in place**, however small and however recent the clause. A charter whose
young clauses may be quietly tuned is a charter with no fixed text at all, and the whole
apparatus of freezing rests on the opposite habit.

| amendment | v1.10 |
|---|---|
| clause added | **`§15`** (`§15.1`–`§15.2`) |
| clause modified | **none** — `§14.3` is sharpened by a later clause, not rewritten |
| rulings changed | **0** · gates | **0** · bands | **0** · caps | **0** · re-grades | **0** |
| register bytes changed | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.11, 2026-09-02 — **§16: A PLATEAU CRITERION IS FROZEN BEFORE COMPUTE OR IT IS NOT A CRITERION. VMFL007-R3's L3 IS RULED NOT PLATEAUED. AND A DOMAIN MAX IS A REDUCTION WHOSE ARGMAX CAN MOVE.**

### §16.1 THE RULING ON VMFL007-R3's L3 — and it goes against the case

L3 (100×100, SIMPLEC) was extended to **90000 iterations** to settle whether its near-axis
viscosity swing decays. **It does not.** Peak-to-peak of `max(nu)` over the last 5000
iterations: **0.4269 at 30000, 0.4349 at 90000**, flat from iteration 25000 on; fitted slope
of `ln(ptp)` **+1.18e-07 per iteration, r² = 0.17**. There is no settling iteration, because
there is no decay. **`Δp` likewise has a FLOOR, not a convergence** — its ptp falls to
**1.5e-03 Pa** by iteration 40000 and stops improving through 90000 (2.4e-08 relative).

> **THE RULING: A BOUNDED LIMIT CYCLE WHOSE PEAK-TO-PEAK LIES BELOW A THRESHOLD FIXED BEFORE
> COMPUTE *IS* A PLATEAU. A LIMIT CYCLE WITH NO SUCH PRE-FIXED THRESHOLD IS NOT.** For
> VMFL007-R3 **no such threshold was pre-fixed**, and I will not fix one now: I know the floor
> is 1.5e-03 Pa, so any threshold I choose today is a threshold chosen knowing it passes.
> **Therefore L3 is NOT PLATEAUED for grading purposes, and any triple graded on it is
> `NOT A RESULT` under `CLAUDE.md` rule 5 step 1.** VMFL007-R3 **cannot be frozen and graded on
> this triple.** The remedy is a fresh registration, not an amendment.

This is the third time in one session this team has been offered a gate it knew the answer to
and declined it — VMFL054's GCI-primary switch, VMFL007-R3's plateau channel, and now the
threshold itself. **Declining the first two would have been worthless if we took the third.**

### §16.2 WHY "RUN IT LONGER AND SEE" WAS THE WRONG INSTRUCTION — a supervisor's reasoning defect

The supervisor's brief said: *"If `max(nu)` settles, the plateau question dissolves and no
ruling is needed."* **That is wrong on its own terms, and the lane said so first.** A graded
run must freeze **an `endTime` AND a plateau criterion** before compute. Learning that a swing
settles at iteration N does not remove the need for a criterion — **and an `endTime` read off
that measurement is an `endTime` CHOSEN KNOWING THE ANSWER**, the same gate-fitting refused
hours earlier on VMFL054.

> **THE CONSTRUCTION THIS TEAM USES FROM NOW ON: freeze a CRITERION — a stated peak-to-peak
> threshold on a stated window, on a NAMED channel — together with an `endTime` GENEROUS ENOUGH
> THAT THE CRITERION, NOT THE CLOCK, DECIDES.** A criterion written as `ptp → 0` is
> unsatisfiable against a limit cycle and must never be written; the threshold is a number, and
> it is justified from the **gate tolerance** (iteration noise must not be able to move the
> verdict), never from an observed floor.

### §16.3 A DOMAIN MAX IS A REDUCTION WHOSE ARGMAX CAN MOVE — the instrument was wrong, not just the reading

The supervisor specified `max(nu)` as the plateau instrument. **A domain max is a REDUCTION, and
its argmax cell can move between samples, so a "wandering max" may be an artifact of the
reduction rather than a property of any cell.** That is not hypothetical here: the argmax moved
from **cell 17 at r = 8.33e-06 m** at iteration 30000 to **cell 217 at r = 3.17e-05 m** at 90000.

The lane added fixed-point `probes`, **and the finding's character changed completely**:

| channel | ptp, last 5000 iters |
|---|---|
| entry-region axis cell | **0.448** — the entire oscillation |
| mid-pipe axis cell | 8.28e-09 |
| near-outlet axis cell | 9.07e-09 |
| mid-radius | 2.6e-14 |

**Nine to sixteen decades quieter.** So the honest statement is **not** *"the near-axis field
does not reach steady state at this refinement"* but *"the field is converged everywhere except
a single localised entry-region cell on the axis, which sits in a persistent limit cycle."*
**Every reduced quantity used as a convergence instrument is paired with a fixed-point probe.**

### §16.4 A NULL RESULT NEEDS ITS OWN PLANTED CONTROL — rule 3, extended

*"It does not decay"* is a **null**, and `CLAUDE.md` rule 3's logic applies with full force: **a
fit that cannot detect decay proves nothing by failing to detect it.** The lane planted known
exponential decays into the real series and re-ran the same fit: a planted half-life of **20000
iterations was recovered as 20967** (r² 0.992) and **60000 as 64472** (r² 0.990). The plant also
fired on all three quiet probes.

> **A zero, a null, or a "no trend" is reported ONLY from a reader shown able to see the
> non-zero, the trend, or the decay.** Rule 3 names the zero case; this team reads it as
> covering every negative finding.

### §16.5 CORRECTION TO THE §12.2 SCOPING NUMBER — 2.45× IS A SNAPSHOT; THE HONEST FIGURE IS 1.56×

`§12.2`'s ruling (**`SAME`**, this session) is **NOT disturbed and is in fact strengthened**:
across all 90000 iterations the `nuMax` clip is touched **18 times, all at iterations 1–18, last
touch at iteration 18** — far stronger evidence than the 30000-iteration record it was ruled on.

**But its scoping number was a snapshot and is corrected here.** L3 headroom to `nuMax` reads
**2.45× at t = 30000** and **4.34× at t = 90000**, while the **limit-cycle peak gives 1.56×**. A
single snapshot understates the exposure by up to **2.8×** depending on when it is taken.
**The honest L3 headroom figure is 1.56×, taken over the cycle**, and any record quoting 2.45×
must either use 1.56× or say explicitly that it is a snapshot. The ruling's *scoped-to-this-triple*
qualifier and its warning that a 200×200 level would likely clip both stand, and both are
sharpened by this.

### §16.6 DISCLOSED — what remains unknown, and two instrument defects carried

**Unknown:** whether the limit cycle is physical or a discretisation artifact of the wedge axis
in the entry region; whether it persists at 200×200; and `d21/ptp`, **still unmeasured with its
evidence destroyed**. The mechanism was not diagnosed — the question asked was whether it
settles, and it does not.

**Two instrument defects, flagged and NOT fixed**, both in `analyse_L3_plateau.py`, both read by
the supervisor as a diff: it **hardcodes the ρ = 1000 conversion** in its `Δp` rather than
reading it (the same class as `read_nu_clip.py`'s hardcoded `NUMIN`/`NUMAX`, also still open),
and `leg()` takes **`sorted(g)[0]`** — the *earliest* `postProcessing` directory — **which is the
same stale-directory trap found and fixed in the VMFL054 comparator this session, recurring in a
second instrument.** Neither affects the reported numbers (the legs are explicitly stitched), and
both are recorded rather than silently repaired.

| amendment | v1.11 |
|---|---|
| clause added | **`§16`** (`§16.1`–`§16.6`) |
| rulings made | **1** — VMFL007-R3's L3 is NOT PLATEAUED; the case cannot be graded on this triple |
| citations corrected | **1** — `§12.2`'s L3 headroom, 2.45× (snapshot) → **1.56×** (over the cycle) |
| gates | **0** · bands | **0** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.12, 2026-09-02 — **§17: §16.6's DESCRIPTION OF THE `leg()` DEFECT IS WRONG, AND THE WRONG FIX FOLLOWS FROM IT. §16.1's SCOPE IS CORRECT BUT ITS FRAMING OVERREACHED.**

### §17.1 THE MISDESCRIBED DEFECT — and why a wrong diagnosis is worse than none

`§16.6` says `analyse_L3_plateau.py`'s `leg()` *"takes `sorted(g)[0]` — the earliest `postProcessing` directory."* **It does not take the earliest. It takes the LEXICOGRAPHICALLY FIRST, and on numeric directory names that bears no reliable relation to time order at all.** Verified by the supervisor:

```
sorted(['0','10000','30000','5000']) == ['0','10000','30000','5000']
  [0]  -> '0'      NOT dependably the earliest
  [-1] -> '5000'   NOT the latest; the true latest is 30000
```

> **THE DANGER IS THE REPAIR THE WRONG DIAGNOSIS IMPLIES.** "It takes the earliest" invites the fix *swap the index to `[-1]`* — **and that fix is still broken**, silently selecting `5000` over `30000`. **The directory names must be compared as INTEGERS.** A misdiagnosis that points at a plausible wrong repair is worse than no diagnosis, because it will be acted on.

The `§16.6` identification of the trap, and its kinship to the VMFL054 comparator's hardcoded `centreProbe/0/`, **both stand**; only the mechanism was misdescribed. `N-AV15`'s provenance block carries the corrected form, and it was corrected there *before* it was corrected here — **by the lane, against the supervisor's own text.**

### §17.2 §16.1's SCOPE IS RIGHT; THE FRAMING AROUND IT WAS NOT

`§16.1` rules only that **L3 is not plateaued and a triple graded ON THIS TRIPLE is `NOT A RESULT`.** That scope is correct and is unchanged. **But the surrounding framing — that the case has "three independent problems" — read as though the case were dead, and the evidence does not say that.**

**Measured, and it cuts the other way:** 25×25 and 50×50 plateau to **3.69e-12** and **4.55e-10** with final residuals at **2.42e-14** and **6.45e-14** — machine precision — and **the limit cycle is ABSENT at both.** Whether a triple that excludes 100×100 sits in the asymptotic range is **unanswered and is not being recommended here**; the point is narrower and sharper:

> **A CASE IS CLOSED BY EVIDENCE OR IT IS NOT CLOSED. It is never closed by TONE.** The stand-down on VMFL007 stands as an allocation decision — there is better work available — and it is recorded as that, **not as a finding that the case cannot be verified.**

| amendment | v1.12 |
|---|---|
| clause added | **`§17`** (`§17.1`–`§17.2`) |
| citations corrected | **1** — `§16.6`'s `leg()` mechanism: "earliest" → **lexicographically first**, with the implied `[-1]` repair named as ALSO broken |
| rulings changed | **0** — `§16.1`'s scope is reaffirmed; only its surrounding framing is narrowed |
| gates | **0** · bands | **0** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.13, 2026-09-02 — **§18: A LAB-GENERATED REFERENCE MUST NAME ITS INDEPENDENT PATH IN THE REGISTRATION, BEFORE THE FREEZE. ALGEBRA HAS ONE. A SOLVER DOES NOT GET ONE BY BEING RUN AGAIN ON A FINER MESH.**

### §18.1 THE ASYMMETRY THIS CLAUSE EXISTS FOR

This team increasingly grades against references **it generates itself**, because the manual states many of its own references only as plotted curves. `§12.2` already governs whether the *model* is the same. **`§18` governs whether the REFERENCE ITSELF can be checked**, and the two lab-generated references this team now holds behave completely differently:

| case | lab-generated reference | is there an independent path? |
|---|---|---|
| **VMFL007** | Rabinowitsch–Mooney closed form, **60 521.969384 Pa** | **YES — ALGEBRA RE-DERIVES.** A second party evaluated it from the manual's own stated inputs **without reading the first derivation** and reproduced it. |
| **VMFL046** *(pending)* | quasi-1D + shock **solver** output | **UNANSWERED — and it must be answered before the freeze.** |

> **A REFERENCE SOLVER ADMITS NO SELF-CHECK. Re-running it reproduces its own errors EXACTLY**, so *"I ran it again and it agrees"* is worth nothing. **A grid triple on the reference solver bounds its DISCRETISATION error and says NOTHING about its MODEL-FORM or IMPLEMENTATION error — and it is precisely that error which passes straight into the gate as though it were truth.**

### §18.2 THE RULING

> **Where the reference is generated by this lab rather than printed in the manual, the pre-registration MUST NAME THE INDEPENDENT PATH TO THE REFERENCE'S ANSWER, in the frozen bytes, before compute. Independence means a DIFFERENT DISCRETISATION OR A DIFFERENT DERIVATION — never the same code on a finer mesh, and never the same author re-reading their own working.**

Three forms that qualify, in descending strength: **(a)** closed-form algebra a second party evaluates from the manual's stated inputs without sight of the first derivation; **(b)** an independent implementation on a different discretisation, written against the governing equations rather than against the first code; **(c)** an external published value for the same configuration. **A grid triple on the reference solver qualifies as NONE of these** — it is a useful error bar on one limb of an error the gate cannot see the rest of.

**IF NO INDEPENDENT PATH EXISTS, THAT IS A `§12.2`-SHAPED ANSWER ARRIVING BEFORE COMPUTE**, and it is worth far more then than at grading: the case is **capped below `PASS`** and says so in its frozen bytes, rather than producing a credential resting on an unfalsifiable reference.

### §18.3 WHY THE FAILURE MODE IS THE WORST ONE AVAILABLE TO THIS TEAM

Every other failure this team has recorded produces a `GATE FAIL` or a `NOT A RESULT` — **a wrong self-generated reference is the only one that produces a `PASS`.** It converts an error in our own instrument into a credential, and the register's whole claim is that `PASS` rows are credentials. **A false `NOT A RESULT` costs us a case; a false `PASS` costs us the register.**

**Raised by `ansys-lane-opus` before the VMFL046 freeze rather than at its grading**, from the observation that VMFL007's lab-generated reference survived scrutiny **only because algebra can be re-derived**, and that the same latitude must not be extended to a solver by analogy.

| amendment | v1.13 |
|---|---|
| clause added | **`§18`** (`§18.1`–`§18.3`) |
| binds | every registration whose reference is lab-generated, **VMFL046 first**, before its freeze |
| rulings changed | **0** — `§12.2` is unaffected; `§18` asks a different question |
| gates | **0** · bands | **0** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.14, 2026-09-02 — **§19: verification's §2p.5 REFUTATION IS HALF RIGHT AND I ACCEPT THAT HALF. ITS FACT IS CORRECT; ITS INFERENCE IS NOT, AND MY OWN COMMIT MESSAGE IS THE COUNTER-EVIDENCE. ITS DISCRIMINATOR IS BETTER THAN MINE AND REPLACES IT.**

### §19.1 WHAT I ACCEPT, AND IT CORRECTS `§16.6`/`§17.1`'s PREMISE

verification (`VERIFICATION_CHARTER` §2p.5, `7d27061f`) verified at source that `grade_vmfl054.py` has **ONE commit in its entire history**, and that this single version **already refuses when more than one `centreProbe` subdirectory exists**, reaching the index only with exactly one member. **Confirmed independently by me.** So my *"the same trap, twice in one day — a pattern, not an accident"* **cannot be supported from the committed history**, and `§16.6`/`§17.1` should not have implied a repair was made to a committed file. That framing is withdrawn.

### §19.2 WHAT I DO NOT ACCEPT — AND THE EVIDENCE IS IN MY OWN FREEZE COMMIT

The sweep's *inference* — **"there was never anything to repair there"** — is **FALSE**, and the counter-evidence is `05ec949e`'s own message, quoted verbatim:

> *"**D3** a silent-wrong-answer path: the gate reader hardcoded `centreProbe/0/U`, so a restart would have graded stale pre-restart data with no complaint. It now enumerates the subdirs and REFUSES on ambiguity rather than guessing."*

**The defect was real, it was in the UNCOMMITTED draft, and I found it in the §3 check-1 diff read and had it repaired BEFORE the freeze.** That is precisely why the file's history shows one commit carrying the repaired version — **a defect caught pre-freeze leaves no defective commit behind.**

> **THE METHODOLOGICAL POINT, offered to verification rather than scored against it: A SWEEP THAT READS ONLY COMMITTED HISTORY IS STRUCTURALLY BLIND TO EVERY DEFECT A PRE-FREEZE CHECK CATCHES — which is to say, blind to the check WORKING.** It will read a clean history and conclude nothing was ever wrong, when what actually happened is that the guard fired early. **Absence from git history is not absence from the record**; the record here is the commit message, and this lab writes those messages precisely so that work leaves a trace when the artifact does not. The `analyse_L3_plateau.py` instance was genuine and committed, so the sweep saw one of two instances and could not have seen the other.

### §19.3 THEIR DISCRIMINATOR IS BETTER THAN MINE AND REPLACES `§17.1`'s REPAIR

`§17.1` concluded *"the names must be compared as INTEGERS."* **That is not the right discriminator.**

> **THE DISCRIMINATOR IS GUARDED vs UNGUARDED, NOT WHICH INDEX.** Under refuse-unless-exactly-one, `[0]`, `[-1]` and an integer-keyed max are **ALL IDENTICAL and all safe** — the index stops mattering the moment ambiguity is refused instead of resolved. Ranked: **anchoring by the time actually needed beats ordering; REFUSING beats both.** Exemplar in this team's own code: `grade_vmflgpu003.py:364-400`.

`§17.1`'s narrower finding stands — `[0]` is not the earliest and `[-1]` is not the latest under a lexicographic sort — but as a *repair* it is superseded: integer comparison merely picks correctly among an ambiguity that should have been refused.

### §19.4 A SCRIPT THAT "GRADES NOTHING" IS ON THE RECORD PATH IF ITS NUMBERS ARE RECORDED

Also verification's, also adopted: `analyse_L3_plateau.py` opens by declaring it *"grades nothing."* **Its outputs are quoted as lab facts in `NUMERICS_KNOWLEDGE` `N-AV15` and in `§16` of this charter.**

> **AN INSTRUMENT WHOSE NUMBERS ENTER A RECORD IS ON THE RECORD PATH AND OWES FULL GRADING-PATH HYGIENE. "It only diagnoses" buys no latitude once a record quotes it.**

**REPAIRED THIS SESSION, and the repair was verified rather than asserted:** both call sites now refuse on ambiguity; the bare `1000.0` is a named `RHO` with its derivation (`k_manual 10 / k_kinematic 0.01`) and a self-consistency assert, since density is genuinely absent from an incompressible case's files and a magic number in a record-path instrument is a number nobody can check. **Two verifications, both required: a PLANTED SECOND TIME DIRECTORY makes the guard REFUSE (rc 2), and the good-path output is BYTE-IDENTICAL to the run whose numbers `N-AV15` quotes — so no recorded number moved.**

**AND A DEFECT I INTRODUCED AND CAUGHT IN THE SAME MINUTE, recorded because it is the session's own lesson biting its author:** my first version of the guard used `raise SystemExit("REFUSE (exit 2): ...")`, which prints the string and **exits 1**. **A refusal that announces one code and returns another is the "evidence annotated as non-binding" defect** — and it survived only because the planted-failure test reported the actual rc instead of trusting the message. Corrected to `SystemExit(2)`; re-verified at rc 2.

| amendment | v1.14 |
|---|---|
| clause added | **`§19`** (`§19.1`–`§19.4`) |
| withdrawn | `§16.6`/`§17.1`'s *"twice in one day, a pattern"* framing — unsupportable from committed history |
| superseded | `§17.1`'s *"compare as integers"* repair → **guarded vs unguarded** |
| adopted from `VERIFICATION_CHARTER` §2p.5 | the discriminator, and the record-path rule |
| instrument repaired | `analyse_L3_plateau.py` — guard planted and fired; recorded numbers byte-identical |
| gates | **0** · bands | **0** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.15, 2026-09-02 — **§20: STEADY-SOLVE LIMIT CYCLES ARE NOW A DOCTRINE, NOT THREE PER-CASE PATCHES. A RESIDUAL FLOOR IS A PROXY, AND FOR A HUNTING DISCRETE STRUCTURE THE PROXY IS INVALID. VMFL046: OPTION (a) REFUSED, OPTION (b) PERMITTED ONLY IN ITS MECHANICAL FORM.**

### §20.1 THE DOCTRINE — three steady-solve limit cycles in one day, across two teams

Within one session this lab has met the same phenomenon three times: **VMFL007's entry-region axis cell** (`N-AV15`, a persistent single-cell limit cycle at 100×100 while every other axis cell converges to 1e-09); **VMFL007's `Δp`**, which has a **floor and not a plateau**; and now **VMFL046's steady shock, where the discrete shock HUNTS BETWEEN CELLS** and holds L2/L3 at ~3e-04. Three instances is a doctrine, not three patches.

> **A RESIDUAL FLOOR IS A PROXY FOR "THE ANSWER HAS STOPPED CHANGING." For a smooth steady solve it is a good proxy. FOR A SOLVE WHOSE DISCRETE STRUCTURE HUNTS — a shock oscillating between cells, a limiter-adjacent cell cycling — THE PROXY IS NOT MERELY TOO TIGHT, IT IS MEASURING THE WRONG THING: it measures the ITERATION'S OWN MOTION, not the ANSWER'S convergence.** The gate quantity can be perfectly settled while the residual bounces forever, and no amount of further iteration closes the gap.

The correct convergence question for such a solve is therefore **on the gate quantity**: has the quantity the gate reads stopped changing, to within the precision the gate needs? **`§16.2` already fixes the construction** — a stated threshold on a stated window on a NAMED channel, with the threshold **justified from the gate tolerance and never from an observed floor.**

### §20.2 THE RULING ON VMFL046 — and the three options are not equivalent

**OPTION (a) — loosen the residual floor to ~1e-03 — IS REFUSED.** Having measured ~3e-04, a floor set at 1e-03 is a threshold chosen knowing it passes, whatever physics is recited alongside it. This is the **fourth** gate this session whose answer we already knew; the first three were declined and this one is no different.

**OPTION (b) — a gate-quantity plateau criterion — IS PERMITTED, BUT ONLY IN ITS MECHANICAL FORM**, and the distinction is the whole ruling:

> **The criterion is on the gate quantity, and its threshold is DERIVED FROM THE GATE TOLERANCE BY A STATED RULE FIXED IN ADVANCE — never from the observed 3e-04. The derivation is shown in the frozen bytes, and WHATEVER NUMBER FALLS OUT IS BINDING, INCLUDING IF IT FAILS.**

**Why this is not the VMFL054 move I refused.** There I was asked to swap **which gate the answer must satisfy**, converting `GATE FAIL` to `GATE REACHED` directly. Here the **gate is untouched** — agreement with the analytical reference at its tolerance — and what changes is the **precondition that decides whether a level yields a measurement at all.** And decisively: **`§16.2` was committed at 22:11:11Z, on VMFL007 evidence, BEFORE VMFL046's smoke ran.** A registration adopting it is applying **standing doctrine adopted prospectively on a different case**, not inventing a criterion to fit its own answer.

**The safeguard that makes it non-steerable:** the threshold falls out of the gate tolerance mechanically (iteration noise must not be able to move the verdict), so knowing the observed value confers no ability to steer. **I do not get to check whether the derived number clears 3e-04 before committing to the derivation.** If it does not clear, the case grades `NOT A RESULT` on those levels and that is the answer.

**OPTION (c) — LTS / transient-to-steady — IS UNCONTAMINATED AND REMAINS AVAILABLE.** It moves no threshold at all; it changes the METHOD so the existing criterion is met. **Where a methodology change and a criterion change would both work, the methodology change is always the cleaner instrument**, because it cannot be steered by knowledge of the answer. It is the fallback if (b)'s derived threshold is not met.

### §20.3 ⚠ THE PROCESS DEFECT UNDERNEATH ALL OF THIS, AND IT IS THE SUPERVISOR'S

**Twice now a pre-freeze "smoke" has told this team the answer before the freeze** — VMFL054 (p = 3.438 and GCI 0.011 % seen pre-freeze) and VMFL046 (the L2/L3 plateau seen pre-freeze). Both times the result was a contaminated decision that had to be refused or narrowly constructed around.

**These are not CLAUSE B smokes.** CLAUSE B specifies **ONE timestep, or one iteration, on the COARSEST mesh of the family** — a test that CANNOT reveal a plateau, an observed order or a GCI, because it produces no converged answer at any level. What this team has twice run instead is a **full pre-freeze production triple**, which by construction reveals exactly the quantities the freeze exists to protect.

> **A SMOKE TEST THAT CAN REVEAL THE ANSWER IS NOT A SMOKE TEST. It is a pre-freeze production run, and it burns the freeze's evidentiary value before the freeze is written.** From now on a pre-freeze feasibility run of this team either (i) obeys CLAUSE B — one iteration, coarsest mesh — or (ii) is declared in the registration as a **PRE-FREEZE PRODUCTION RUN**, with every quantity it revealed named explicitly, so a reader can price which decisions were taken with the answer in hand. **Silence about a revealing smoke is the defect; the smoke itself is only sometimes one.**

This is mine, not the lanes'. **Both lanes disclosed their smokes fully and refused to fit thresholds to them** — the failure was that the supervisor kept authorising full triples under a clause that permits one iteration.

| amendment | v1.15 |
|---|---|
| clause added | **`§20`** (`§20.1`–`§20.3`) |
| rulings made | VMFL046 option **(a) REFUSED**; **(b) PERMITTED in mechanical form only**; **(c) uncontaminated fallback** |
| doctrine | steady-solve limit cycles: a residual floor is an INVALID PROXY where the discrete structure hunts |
| process defect named | pre-freeze "smokes" that are production triples — **the supervisor's**, twice |
| gates | **0** · bands | **0** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.16, 2026-09-02 — **§21: `§20.2` ATTACHED THE PLATEAU TO "THE GATE QUANTITY" AS THOUGH THERE WERE ONE. VMFL046 HAS TWO WITH OPPOSITE EXPOSURE. AND THE MODEL-SAMENESS RULING GOES AGAINST THE CASE.**

### §21.1 THE REFINEMENT — a plateau criterion attaches PER QUANTITY, and some quantities need none

`§20.2` says *"the criterion is on the gate quantity"*. **VMFL046 has TWO gate quantities with OPPOSITE exposure to the limit cycle**, and applying one rule to both is wrong in both directions — **it either kills the case or silently certifies it while the shock moves.** Raised by the lane against my clause; **arithmetic re-verified by me at source:**

| gate quantity | exposure to the hunt | plateau criterion |
|---|---|---|
| **`M(0.9)`** — pre-shock, smooth, supersonic centreline | **exposed**; it is what the residual floor cannot certify | **REQUIRED** |
| **shock location** — discretely located, tolerance ±5 % | tolerance band = **±0.0625 m = 20.0 CELLS**; hunt = ±1 cell = **5.0 % of the band** | **NONE — and one would be UNREACHABLE** |

A derived plateau on the shock would be `τ·x/K = 0.05 × 1.250 / 50 = 0.00125 m` against a cell of `0.003125 m` — **0.400 CELLS. Sub-cell, and therefore unsatisfiable by construction** for a quantity that can only move in cell-sized steps.

> **A PLATEAU CRITERION ATTACHES PER QUANTITY, NOT PER CASE. A quantity whose own gate tolerance DWARFS the limit-cycle amplitude needs NO plateau — and imposing one on a discretely-located quantity can demand a precision finer than the mesh can express, which is a criterion that fails for reasons having nothing to do with the answer.** The test is a-priori arithmetic: **tolerance band in CELLS against hunt amplitude in CELLS**, computable before any run.

### §21.2 MODEL-SAMENESS FOR VMFL046 — **RULED `DIFFERENT`. THE CASE IS CAPPED AT `GATE REACHED`.**

The reference is **inviscid quasi-1D Euler + Rankine–Hugoniot**; the solve is **viscous 2-D Navier–Stokes with wall heat transfer**. The argument for sameness is that they coincide on the centreline away from walls and shock, sharing γ = 1.4 and the conservation laws. **I do not accept it.**

A viscous nozzle carries a **boundary-layer displacement thickness that reduces the EFFECTIVE AREA**, and the area–Mach relation is exactly what sets centreline Mach at a station. That is a **systematic model-form difference**, not a numerical one, and it does not vanish on the centreline — it enters through the area the core flow actually sees.

> **SAMENESS OF MODEL IS NOT ASYMPTOTIC AGREEMENT OF SOLUTIONS.** If *"they coincide in this region"* counted as sameness, `§12.2` would collapse into the gate it is supposed to qualify — the gate already measures agreement; `§12.2` asks the prior question of whether the two objects are the same KIND of thing. **A viscous NS model and an inviscid Euler model are not the same model, however close their solutions run.**

**Consequence, taken openly: VMFL046 is CAPPED AT `GATE REACHED` and cannot be a credential this round.** The route to a `PASS` candidate is an **inviscid (Euler) 2-D solve**, where the remaining difference is dimensional rather than model-form — that is a VMFL046-R2, not an amendment here.

### §21.3 THE TWO CONTAMINATED SECONDARY TOLERANCES — retained, but **DEMOTE-ONLY**

The lane disclosed against itself that building the case exposed coarse-smoke Mach numbers (max Mach ≈ 2.0, ~9 % pre-shock deviation at L1) **before** the secondary bands (GCI ≤ 15 %, Mach dev ≤ 10 %) were fixed. Its defence — 10 % is *looser* than the 9 % it saw, so they are not fitted-to-pass — is sound as far as it goes, and **it does not go far enough: a reader cannot distinguish "a-priori" from "convenient" once the numbers are seen.**

**I cannot reset them cleanly either — I now know 9 % too.** So neither striking them (which LOOSENS the gate, the direction rule 5 forbids) nor re-choosing them is available. The ruling:

> **The two secondary limbs are RETAINED but are DEMOTE-ONLY: they may turn a `PASS` into a `GATE FAIL`, and they may NEVER license a `PASS`.** A contaminated threshold is dangerous only when it can permit; one that can only demote has its contamination working AGAINST the case. **And because they are contaminated-loose, a secondary limb that does NOT fire is NOT evidence of quality** — that must be printed beside the verdict, or the silence will be read as a pass.

The primary gate (`CONVERGING` triple on `M(0.9)` + shock location within 5 %) is a-priori-clean and carries the verdict alone.

### §21.4 THE REMAINING ITEMS

**Operating pressure 101.325 kPa and the frozen contour: RATIFIED** — the contour plus back-pressure reproduces analytical max Mach **2.197** and shock at **x = 1.250** a-priori, which is a real check and not a restatement. **First-order scheme: ACCEPTED AS DISCLOSED**, with its consequence named — it forces Roache order ≈ 1 and a grid-smeared shock, and that is already reflected in the a-priori band; a higher-order R2 is future work, not a defect concealed. **`§18`: CLEARED** — the reference is closed-form algebra with the independent path **PERFORMED, not asserted**: an independent Newton path reproducing `M(0.9) = 1.882125` **to the digit** (difference 0) and NACA-1135 published tables at **1.8817** (difference 4.3e-04). That is form (a) of `§18.2`, the strongest available.

| amendment | v1.16 |
|---|---|
| clause added | **`§21`** (`§21.1`–`§21.4`) |
| refined | `§20.2` — a plateau attaches **per quantity**; a quantity whose tolerance dwarfs the hunt needs none |
| rulings made | model-sameness **`DIFFERENT`** → VMFL046 **capped at `GATE REACHED`**; secondaries **demote-only**; contour/pressure ratified; first-order accepted as disclosed |
| gates | **0 moved** · bands | **0 moved** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.17, 2026-09-02 — **§22: I RULED `§21.2` BEFORE THE MEASUREMENT I HAD MYSELF DEMANDED ARRIVED. THE BOUND IS GOOD AND IT IS ON THE WRONG QUANTITY. THE CAP STANDS FOR A CORRECTED REASON.**

### §22.1 A PROCESS ERROR OF MINE, FIRST

My brief to the lane said, of model-sameness: *"Give me the measurement… Facts only; no ruling."* **I then ruled `§21.2` `DIFFERENT` before that measurement arrived**, on a general principle and an unquantified assertion that displacement thickness *"does not vanish on the centreline"*. **Asking for a measurement and ruling before reading it is the same defect as accepting a summary in place of a check** — and it is worse here, because I had already named the requirement myself.

### §22.2 THE MEASUREMENT IS ACCEPTED, AND IT NARROWS `§21.2`'s PRINCIPLE

A-priori at the gate station `x = 0.9` (from the ANALYTICAL state, not the production run): Blasius laminar `δ* = 2.44e-04 m` on `h = 0.1533 m` → **`dA/A = 0.159 %`**; through the supersonic area–Mach sensitivity `dM/M = (dA/A)/[(M²−1)/(1+½(γ−1)M²)]` with denominator **1.4881**, this bounds the centreline model-form difference at **`dM/M = 0.107 %`** — **93× below the 10 % band.** *Recomputed by me from the stated inputs; it reproduces.*

> **`§21.2` SAID "SAMENESS OF MODEL IS NOT ASYMPTOTIC AGREEMENT OF SOLUTIONS", AND THAT STANDS AS A GUARD AGAINST HAND-WAVING — BUT IT OVER-REACHED. A QUANTIFIED, A-PRIORI, PHYSICALLY-DERIVED BOUND ON A MODEL-FORM DIFFERENCE IS NOT ASYMPTOTIC HAND-WAVING: IT IS EXACTLY THE ERROR-BUDGET TREATMENT `Amendment 1.4 CLAUSE A` ALREADY PRESCRIBES** for the axisymmetric wedge's modelling bias. A bounded model-form difference is **budgeted, not disqualifying.** `§21.2` is narrowed accordingly: a model difference disqualifies when its effect on the gate quantity is **unbounded, or bounded only comparably to the gate band** — not merely because the two models are different equations.

### §22.3 BUT THE BOUND IS ON THE WRONG QUANTITY, AND THE CAP THEREFORE STANDS

**The bound is on `M(0.9)`. `M(0.9)` is NOT the primary gate's agreement limb.** Read `§7`: the primary gate is a **`CONVERGING` Roache triple on `M(0.9)`** — a grid-convergence condition that compares nothing to the reference — **plus SHOCK LOCATION within 5 % of analytical**, which is the *only* a-priori-clean limb that actually compares this solve to the reference. (The Mach-agreement limb is a **secondary**, and `§21.3` has already made it demote-only for contamination.)

> **NO A-PRIORI BOUND HAS BEEN GIVEN FOR THE MODEL-FORM EFFECT ON SHOCK LOCATION — and shock position in a nozzle is precisely the quantity known to be SENSITIVE to small effective-area and back-pressure perturbations, because it sits where the pressure-matching condition is stiff.** A 0.16 % effective-area deficit that moves `M(0.9)` by 0.107 % need not move the shock by anything like 0.107 %; the sensitivity is a different derivative and it has not been computed.

**RULING: `§12.2` for VMFL046 remains `DIFFERENT`, and the case remains CAPPED AT `GATE REACHED` — but for the corrected reason above, not for `§21.2`'s over-broad one.** The `M(0.9)` bound is **accepted, credited and recorded**; it simply does not reach the limb that carries the comparison.

### §22.4 THE TWO ROUTES OUT, both R2 work and neither available by amendment

**(i)** Bound the model-form sensitivity of **shock location** a-priori — `dx_shock/x` per unit `dA/A` from the back-pressure matching condition — and if that bound is likewise orders below the 5 % band, `§12.2` can be re-ruled `SAME` for the primary limb on the `§22.2` error-budget principle. **(ii)** Run **inviscid 2-D Euler**, where the remaining difference is dimensional rather than model-form. **(i) is cheap, is pure analysis, and needs no compute** — it is the better next move.

### §22.5 `δ_M` IS DERIVED FROM `§18`'s REFERENCE SPREAD, NOT FROM THE CONTAMINATED BAND

The lane's proposed `δ_M = τ_M · M_ref / K` inherits `τ_M` from the **secondary Mach band, which `§21.3` has ruled CONTAMINATED.** Deriving a convergence criterion from a contaminated tolerance **propagates the contamination into the criterion**, which is precisely what the mechanical-form requirement exists to prevent.

> **`δ_M` IS SET FROM `§18`'s OWN MEASURED REFERENCE-REPRODUCTION SPREAD: `|1.882125 − 1.8817| = 4.25e-04` Mach (0.0226 %). THE RULE, a-priori: ITERATION NOISE SMALLER THAN THE UNCERTAINTY IN THE REFERENCE VALUE ITSELF CANNOT MOVE ANY VERDICT THAT COMPARES TO THAT REFERENCE.** `W = 500` iterations as proposed. This spread was measured for `§18` **before** the production run and is independent of it, so it is uncontaminated by construction.

**`δ_M = 4.25e-04` Mach over 500 iterations. NEITHER I NOR THE LANE CHECKED WHETHER THE RUN MEETS IT BEFORE THIS WAS FIXED**, and it is **binding including if it fails** — in which case **option (c), LTS / transient-to-steady, is the PRE-COMMITTED BINDING FALLBACK, and no loosened floor is available at that point.** It is ~8.9× tighter than the `τ_M`-derived 3.76e-03 it replaces, so this ruling makes the criterion **harder, not easier**.

| amendment | v1.17 |
|---|---|
| clause added | **`§22`** (`§22.1`–`§22.5`) |
| narrowed | `§21.2` — a **bounded** model-form difference is budgeted (CLAUSE A), not disqualifying |
| ruling | `§12.2` VMFL046 **`DIFFERENT`, cap STANDS**, on the corrected shock-location reason |
| fixed a-priori | **`δ_M = 4.25e-04` Mach / `W = 500`**, from `§18`'s reference spread; (c) pre-committed fallback |
| gates | **0 moved** · bands | **0 moved** · caps | **0** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.18, 2026-09-02 — **§23: THE SHOCK-LOCATION BOUND CAME IN, I VERIFIED IT ON AN INDEPENDENT PATH, AND IT OVERTURNS MY OWN CAP. §12.2 FOR VMFL046 IS RE-RULED `SAME` FOR THE PRIMARY LIMB. THE CASE IS THIS TEAM'S FIRST GENUINE `PASS` CANDIDATE FROM THE NEVER-RUN SET.**

### §23.1 THE BOUND, AND MY INDEPENDENT CHECK OF IT (§3 CHECK 3)

`§22.3` held the cap open on one unbounded channel: the model-form effect on **shock location**, which I asserted was *"precisely the quantity sensitive to small effective-area perturbations"* because it *"sits where the pressure-matching condition is stiff."* **The lane computed the sensitivity a-priori, and because a claim that overturns a cap is a direction-changing claim (`SUPERVISION` §3 check 3), I re-derived it on an INDEPENDENT PATH — a quasi-1D isentropic + normal-shock + back-pressure-matching solve written from the governing relations, not read from `quasi1d_reference.py`.**

| quantity | lane | my independent solve | agree? |
|---|---|---|---|
| `dx_shock/x` per unit `dA/A` | ~0.99 | ~0.62 (locally-linear area model) | **both O(1), neither amplifying** |
| shock shift, laminar BL | Δx/x 0.183 % (27× below 5 %) | 0.119 % (42× below) | same conclusion |
| shock shift, turbulent BL (conservative) | 0.631 % (8× below) | 0.418 % (12× below) | same conclusion |

> **THE TWO DERIVATIONS DISAGREE ON THE SENSITIVITY BY A FACTOR OF ~1.6 — AND THE CONCLUSION SURVIVES THE DISAGREEMENT, WHICH IS THE POINT.** Under the WORST combination (lane's higher 0.99 sensitivity × conservative turbulent BL) the shock shift is still **8× below** the 5 % band. A conclusion that holds across a factor-1.6 spread in its own key derivative and across two BL models is robust; had the margin been ~2×, the 1.6 disagreement would have decided the ruling and neither number could have been trusted without reconciling them.

### §23.2 TWO OF MY OWN CLAIMS WERE WRONG, AND THE MEASUREMENT REFUTES BOTH

1. **My MECHANISM was inverted.** I said stiff pressure-matching → sensitive shock. **Backwards: a stiff matching means a WELL-ANCHORED, INSENSITIVE shock.** The computed sensitivity is moderate (~1:1), consistent with a matching that is neither stiff nor slack.
2. **My implied DIRECTION was wrong.** `§22.3` implied *shock likely too sensitive → cap correct*. The derivative is ~1:1, not amplifying, and the tiny BL driver (0.16–0.7 % area) makes the effect small regardless. **The cap does not survive its own demanded computation.**

### §23.3 THE RULING

> **`§12.2` FOR VMFL046 IS RE-RULED `SAME` FOR THE PRIMARY GATE LIMB (`CONVERGING` triple on `M(0.9)` + shock location within 5 %).** Both comparison channels now carry an a-priori, physically-derived model-form bound one to two orders below their bands — `dM/M ≈ 0.107 %` vs 10 % (§22.2) and `dx_shock/x ≤ 0.63 %` vs 5 % (§23.1) — **budgetable exactly as `CLAUSE A`'s wedge modelling bias is.** Per the criterion I fixed in `§22.4(i)` before the number was known, that lifts the cap.

**VMFL046 IS PROMOTED FROM `GATE REACHED`-CAPPED TO A GENUINE `PASS` CANDIDATE — the first this team has built from the manual's never-run set.** This does NOT make it a `PASS`: it remains subject to (a) the graded run meeting the frozen primary gate; (b) the frozen convergence criterion `δ_M = 4.25e-04` / `W = 500` (§22.5), binding including if it fails, with LTS the pre-committed fallback; and (c) the secondary tolerances' **demote-only** status (§21.3) — they can still turn this `PASS` candidate into a `GATE FAIL`, never license it.

### §23.4 THE ONE CHANNEL STILL NOT BOUNDED, NAMED SO THE `SAME` RULING IS HONEST

The `SAME` ruling covers the two channels that are bounded. **It does NOT cover the shock-CAPTURED-vs-JUMP structural difference AT THE SHOCK ITSELF** — the reference has a discontinuous Rankine–Hugoniot jump, the first-order solve has a grid-smeared captured shock over several cells. **The gate is constructed to avoid this channel rather than to bound it:** it reads shock LOCATION (the smear is symmetric to first order, so its centroid is unbiased) and PRE-shock `M(0.9)` (upstream of the smear), and **never a quantity evaluated THROUGH the jump.** That is a gate-design mitigation, not a bound, and it is named here so a reader does not read `SAME` as covering a channel it does not. If a future R2 gates on a through-jump quantity, this channel reopens and needs its own bound.

| amendment | v1.18 |
|---|---|
| clause added | **`§23`** (`§23.1`–`§23.4`) |
| ruling | `§12.2` VMFL046 **re-ruled `SAME` for the primary limb**; cap of `§21.2`/`§22.3` **LIFTED** |
| status change | VMFL046 **`GATE REACHED`-capped → genuine `PASS` candidate**, this team's first from the never-run set |
| my claims refuted | mechanism (stiff→sensitive) inverted; implied direction (cap correct) wrong — both by measurement I verified independently |
| still open | shock-captured-vs-jump channel — mitigated by gate design (§23.4), not bounded |
| gates | **0 moved** · bands | **0 moved** · caps | **1 LIFTED** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.19, 2026-09-03 — **§24: THE RUN REFUTED `§23`'s BOUND BY 20.5×. THE ARITHMETIC IS NOT THE CASUALTY — THE METHOD IS. A SENSITIVITY ARGUMENT OVER ENUMERATED PERTURBATIONS IS NOT AN UPPER BOUND ON A TOTAL DISCREPANCY, AND THIS TEAM WILL STOP TREATING IT AS ONE.**

### §24.1 THE REFUTATION, STATED AS A NUMBER BEFORE ANYTHING IS SAID ABOUT IT

`§23.3` lifted VMFL046's `GATE REACHED` cap on a bound I re-derived personally on an independent path (`§3` check 3): the model-form effect on shock location is **`dx_shock/x ≤ 0.63 %`**, worst case, *"8× below the 5 % band"*. The graded run's grid-converged answer is now on the record:

| quantity | value |
|---|---|
| Richardson limit of `x_shock` over the CONVERGING triple (R = 0.6154, p = 0.700) | **1.0885** |
| analytical reference `x_shock` | **1.250** |
| grid-converged discrepancy | **−12.92 %** |
| `§23.1`'s worst-case bound on the same quantity | **≤ 0.63 %** |
| **refutation factor** | **20.5×** |

**The bound is refuted.** Not strained, not at its edge — exceeded by more than an order of magnitude, in the one place it was load-bearing.

### §24.2 TWO QUALIFICATIONS, IN BOTH DIRECTIONS, BEFORE THE RULING

**(a) The refuted bound did not change the verdict.** The primary limb failed on its own terms at 7.79 % against a 5 % band; under the un-lifted cap the outcome would still have been `GATE FAIL`. **The cap-lift was not self-serving in outcome**, and I record that because the opposite pattern — a bound that lifts a cap and then delivers the `PASS` it enabled — is the one that should end a method permanently.

**(b) That is no defence of the reasoning, and it is not offered as one.** A bound wrong by 20.5× that happened not to matter is a bound wrong by 20.5×. **The next case is where it costs something.**

### §24.3 WHAT ACTUALLY FAILED — and it is not arithmetic

Both derivations in `§23.1` were, so far as I can tell, correctly executed. They computed the same thing: **the shock displacement produced by ONE ENUMERATED PERTURBATION — boundary-layer displacement thickness acting through effective area** — as `sensitivity × perturbation`, and both got an O(1) sensitivity and a sub-percent answer. That number may well still be right *for that channel*.

> **THE DEFECT IS THAT I PRESENTED IT AS A BOUND ON THE TOTAL DISCREPANCY BETWEEN THE TWO MODELS. IT IS NOT. IT IS A BOUND ON THE CHANNELS I HAPPENED TO ENUMERATE.** Every mechanism not on the list — here, viscous total-pressure loss through the diverging section setting the downstream matching state, which is not a displacement-thickness effect at all — sits **outside** the bound and is unconstrained by it. A sensitivity calculation tells you how hard one lever pushes. **It tells you nothing about how many levers there are.**

This is why the factor-1.6 robustness check in `§23.1` gave false comfort. Two derivations agreeing across a 1.6× spread in the *derivative* confirms the derivative. **Both were computing the same incomplete quantity, so agreement between them could never have surfaced the missing channel** — the check was independent in path and identical in scope, and only scope was wrong. *An independent check of the wrong quantity is not an independent check.*

### §24.4 THE RULING — `§22.2`'s NARROWING IS ITSELF NARROWED

`§22.2` established that a **quantified** model-form difference is budgeted rather than disqualifying (`CLAUSE A`). That principle stands. **The evidence that qualifies as a quantification does not.**

> **A model-form difference may be BUDGETED under `CLAUSE A`, and may lift a `GATE REACHED` cap, ONLY where the bound is one of:**
> **(i) a bound on the TOTAL discrepancy between the two models** — a closed-form or limiting-case argument that constrains everything the two models can differ by, not a sum over named channels; or
> **(ii) an ENUMERATED-CHANNEL bound that has been VALIDATED against at least one MEASURED comparison of the same two models** on a comparable configuration — the enumeration tested, not asserted; or
> **(iii) an enumerated-channel bound carrying an explicit, pre-registered COMPLETENESS ARGUMENT** naming why no unenumerated channel can contribute at the band's scale — and that argument is itself frozen and is itself falsifiable by the run.
>
> **An enumerated-channel bound with none of these is UNVALIDATED. It is recorded in the frozen bytes as unvalidated, it may be reported as a diagnostic expectation, and IT DOES NOT LIFT A CAP.** The case stays capped at `GATE REACHED`.

`§23.1`'s bound was form (iii) without the completeness argument — I never asked *what else could move this shock*, and the question is one sentence long. **Had I asked it, viscous stagnation-pressure loss would have been named in the first minute**, and VMFL046 would have been registered honestly as `GATE REACHED`-capped, which is what it turned out to deserve.

### §24.5 THE ADDENDUM `§23.4` WAS PROMISED, NOW OWED AND PAID — and it SURVIVES

`§23.4` argued the shock-captured-vs-jump channel away with *"the smear is symmetric to first order, so its centroid is unbiased."* Before the freeze the lane corrected me: **first-order upwind is dissipative, so smear symmetry is not safe to assume; the discretisation bias in locating a captured shock is instead bounded by the numerical shock WIDTH (a few cells) — ≪ the 5 % band (≈20 cells at L3) — and it REFINES with the mesh.** I accepted it then and record it now as the operative text of `§23.4`, the original argument **struck, not rewritten**.

**And unlike `§24.1`'s casualty, this one is CORROBORATED by the run.** The measured shock location moved monotonically *away* from the analytical reference under refinement (L1 1.25763 → L2 1.19260 → L3 1.15258) and the triple is `CONVERGING` toward 1.0885. A discretisation bias that refines away cannot produce that: **the coarse-grid agreement was the artefact and the fine-grid disagreement is the physics.** The width-based bound is on discretisation bias, it is small, and it is not what the 12.92 % is made of.

### §24.6 THE LESSON THAT GENERALISES BEYOND THIS TEAM

> **THE COARSE MESH AGREED WITH THE REFERENCE AND THE FINE MESH DID NOT.** At L1 the shock sat **0.61 %** from analytical; a single-level submission would have passed this limb outright, and the pre-freeze smoke's *"<1 % shock agreement"* — cited in the registration as evidence this was a `PASS` candidate — **was that coarse-grid reading.** The grid triple is the only reason it was caught.
>
> **An agreement obtained at the coarsest level is the least trustworthy number in the set, and it is the one that looks most like success.** This team will not cite a coarse-level agreement as candidacy evidence again; a pre-freeze smoke establishes that the case RUNS, never that it AGREES.

### §24.7 WHAT THIS DOES NOT DO, AND THE AUDIT IT OPENS

It does **not** re-grade row #54: VMFL046's `GATE FAIL` was reached on the primary limb's own terms, is permanent, and no amendment touches it. It does **not** retract `§22.2`'s principle, only the evidence standard under it. It does **not** claim the −12.92 % is established as viscous model-form: the decisive inviscid/Euler comparison **has not been run**, and the reading in the register row is stated there as an open hypothesis.

**AUDIT OPENED, and it is on me:** every registration in this territory that budgeted a model-form difference by an enumerated-channel sensitivity argument is now suspect under `§24.4` and must be re-read against (i)/(ii)/(iii). `CLAUSE A`'s wedge modelling bias is the first to re-read. **No `PASS` row is retracted on suspicion** — the audit reports per row, and any row it cannot defend is escalated rather than quietly re-labelled.

| amendment | v1.19 |
|---|---|
| clause added | **`§24`** (`§24.1`–`§24.7`) |
| narrowed | **`§22.2`** — a quantified model-form difference lifts a cap only under `§24.4`(i)/(ii)/(iii) |
| struck & replaced | **`§23.4`**'s smear-symmetry argument → the shock-WIDTH bound (the lane's correction, promised at the freeze) |
| my ruling refuted | **`§23.3`**'s cap-lift rests on a bound the run exceeded by **20.5×**; the cap-lift is recorded as **wrongly reasoned, and outcome-neutral for row #54** |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved (a FUTURE cap-lift standard is TIGHTENED)** · re-grades | **0** · register bytes | **0** |
| audit opened | every `CLAUSE A` model-form budget in this territory, re-read against `§24.4` |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.20, 2026-09-03 — **§25: THE DIGITIZED-REFERENCE INSTRUMENT STANDARD. SANAA APPROVED DIGITIZATION AS ITS OWN INSTRUMENTED TASK; THIS IS THE INSTRUMENT, AND ITS HARDEST CLAUSE EXISTS BECAUSE THE FIRST FIGURE WE WANT TO READ BELONGS TO A CASE WHOSE ANSWER WE ALREADY KNOW.**

### §25.0 THE AUTHORITY

Sanaa, 2026-09-03 (~16:00Z), verbatim, recorded at `etc/sessions/2026-09-03T1600Z_sanaa_five_rulings.md`:

> *"Digitization approved as its own instrumented task; digitized references carry stated read-off uncertainty, folded into the gate band."*

That is the whole authority and it is also the whole specification's spine: **instrumented**, **stated uncertainty**, **folded into the band**. `§25` is this team's operationalisation. It authorises **building and calibrating** the instrument; it authorises **no gate** until `§25.7`'s conditions are met per case.

### §25.1 WHAT A DIGITIZED REFERENCE IS

A value read off a printed plot is a **measurement of a figure**, not a reference value. It carries `u_read`, an uncertainty of the reading, which is **additional to** and **independent of** whatever uncertainty the plotted quantity itself carries. **A digitized number never becomes exact by being the manual's own.** Every register row, results record and charter citation that uses one states it as `value ± u_read (digitized, Fig. N, p. P)` — the bare number is not a citable form in this territory.

### §25.2 ⚠ THE ORDER OF OPERATIONS — the clause the rest of the standard exists to protect

The first plate this team wants is **VM2026R1 Fig. .46.2**, which plots Ansys's own centreline Mach against their analytical solution — i.e. it yields **Ansys's own shock location**, the exact comparison `§24.7` records as unrun. **I already know our answer is 1.0885.**

> **A reference selected, or an uncertainty band sized, AFTER our own answer is known is gate-fitting wearing a new instrument.** It is the same move this team refused three times (VMFL054, VMFL007, and the `δ_M` derivation at `§22.5`), and a digitizer makes it *easier*, because a read-off has a dozen defensible knobs and every one of them moves the answer.

**BINDING, and it binds hardest where we already have a number:**

1. **The predicted value is frozen before the read-off.** The registration states, in the frozen bytes, what we expect the digitized value to be **and why** — before the plate is read.
2. **`u_read` and its full derivation are frozen before the read-off**, and are derived from `§25.3`'s synthetic controls — **never from the target plate**, and never from any statistic computed on it.
3. **The band arithmetic (`§25.6`) is frozen before the read-off.**
4. **The read-off is executed by the frozen script**, whose inputs are the extracted plate and the axis calibration and nothing else, and whose output lands in a file the frozen registration already commits to consuming.
5. **A digitized-reference gate is ALWAYS A NEW REGISTRATION, NEVER A RE-GRADE.** Row #54's `GATE FAIL` is permanent whatever any R2 finds.

### §25.3 `u_read` IS CALIBRATED ON SYNTHETIC PLATES WHERE TRUTH IS KNOWN BY CONSTRUCTION — with a planted-failure arm

The instrument is calibrated on figures **this lab renders**, of curves whose true values are known exactly, matched to the target plate's DPI, axis ranges, line width, marker style, gridline density and aspect ratio. Digitize `N ≥ 20` such plates; the error distribution over them is the calibration.

**Rule 3 extended to figures — and a null needs its own plant (`§16.4`):**

- **PLANT-DETECT (positive control).** A synthetic plate whose curve is displaced by a known offset `≥ 3 u_read` **must be read back as displaced, within the calibration**. If the digitizer cannot see a planted displacement, its agreement with an undisplaced plate is worthless and the instrument **REFUSES (exit 2)**, never degrades.
- **PLANT-NULL (negative control).** An undisplaced synthetic plate must read back at zero offset within `u_read`. A digitizer that reports displacement on a clean plate is equally disqualified.
- **AXIS PLANT.** The axis calibration is fitted on a subset of ticks and **verified against a held-out tick** not used in the fit. Disagreement beyond the pixel floor **refuses**. Log axes are declared explicitly in the frozen bytes; a log axis fitted as linear is a silent order-of-magnitude error and is exactly the class this clause catches.

### §25.4 `u_read` IS THE MAXIMUM OF THREE FLOORS, never the smallest defensible number

`u_read = max(` synthetic-control RMS error (`§25.3`), half the spread of **two independent read-offs of the target plate** performed without sight of each other's numbers, the **pixel floor** — one plate pixel converted to data units at the frozen extraction DPI `)`.

The two-independent-read-offs term reuses the `§18`/`§22.5` construction that set `δ_M`: **a measured reproduction spread is the empirical floor on a quantity's own uncertainty, and it is uncontaminated only if it is measured before the comparison it will feed.** The pixel floor is stated because no processing recovers information the raster does not carry.

### §25.5 THE FIGURE IS IDENTIFIED AGAINST THE PDF, NEVER THE SIDECAR (rule 15)

A plate is identified by its **printed caption text AND page number, verified in the PDF itself**. The `.txt` sidecar cannot carry a plot and must never be the identification path — a sidecar can be internally consistent and externally false (L-144). The extracted raster is written to the case directory at a stated DPI and **its hash is frozen into the registration**, so the plate that was read is provably the plate that was registered.

### §25.6 HOW `u_read` ENTERS THE GATE — folded in, and capable of capping the case

Per Sanaa's ruling the read-off uncertainty is **folded into the gate band**, not reported beside it:

- The comparison is `|CFD − ref_digitized| ≤ sqrt( tol² + u_read² )`, with `tol` the pre-registered physical tolerance and both terms in the same units, stated in the frozen bytes.
- **THE CAP.** If `u_read ≥ tol / 3`, the instrument — not the physics — is materially deciding the verdict, and **the case is CAPPED at `GATE REACHED`**: it may reach its gate, it may not become a `PASS` credential. The ratio is computed and printed by the comparator on every run, whatever the verdict.
- **`u_read` never shrinks a band.** Folding is quadrature-widening only; a digitized reference can never make a gate easier to pass than the physical tolerance alone would.
- A `GATE FAIL` against a digitized reference is a `GATE FAIL` and is registered as one. Widening applies to the band, never to the vocabulary.

### §25.7 WHAT AUTHORISES A DIGITIZED GATE

No case gates on a digitized reference until, in this order: the instrument passes `§25.3`'s three plants on the calibration set; `u_read` is derived per `§25.4` and **committed**; the case's registration freezes prediction, `u_read`, band arithmetic and plate hash per `§25.2`; and `§3` check 4 (pre-registration committed before compute) is done by me personally. **The instrument is built and calibrated as its own pre-registered, costed task**, and its calibration is a `PASS`/`GATE FAIL`/`NOT A RESULT` of its own — an instrument that fails its plants is a `NOT A RESULT` and unlocks nothing.

### §25.8 WHAT IT UNLOCKS, STATED WITHOUT INFLATION

Roughly **48 figure-heavy cases** in the manual's never-run set have no printed scalar this team can gate against and have been blocked on exactly that. `§25` is what makes them addressable. It does **not** make them `PASS` candidates: `§25.6`'s cap will bind on any case whose printed tolerance is tight relative to a plate's readable resolution, and **a large fraction of the 48 will be `GATE REACHED` by construction.** That is the honest ceiling of reading numbers off pictures, and it is stated here so no later report presents it as a disappointment.

| amendment | v1.20 |
|---|---|
| clause added | **`§25`** (`§25.0`–`§25.8`) |
| authority | Sanaa 2026-09-03, verbatim at `§25.0` |
| authorises | **building and calibrating** the digitizer as a pre-registered, costed task |
| authorises NOT | **no gate on any digitized reference** until `§25.7`'s conditions are met per case |
| new cap | `u_read ≥ tol/3` → case **capped at `GATE REACHED`** |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved (one NEW cap defined)** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.21, 2026-09-03 — **§26: SANAA'S COMPUTE-ENVELOPE LAW REGISTERED. THIS TEAM DRAWS NOTHING FROM THE ENVELOPE AND ADOPTS ALL OF ITS CAP DISCIPLINE — AND THE ~3× CAP RULE MAKES THE ESTIMATE LOAD-BEARING IN A DIRECTION THAT KILLS RUNS RATHER THAN OVERSPENDING THEM.**

### §26.1 THE LAW, AND WHAT PART OF IT REACHES THIS TERRITORY

Sanaa, 2026-09-03 (~18:00Z), recorded verbatim at
`etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`. The operative clauses,
in her words:

> *"1. The per-case dollar approval loop is abolished. I set one standing envelope: $1,000 for the benchmark ladder (Rungs 0–3), spendable without returning to me. […] 2. What does not change: every run still registers its cost estimate before launch, still carries a hard per-run cap (set by the team at ~3× its own estimate, not by me), still reports predicted-vs-actual, and still names waste. **The estimate is an instrument, not a permission slip.** […] 4. Escalation to me only for: a single run projected over $150, the envelope reaching 80 %, or a rerun of something that already failed twice […]. However before escalating this to me check that you didn't make bugs/errors in how you estimated this exceedance"*

**THE ENVELOPE IS THE INDUSTRIAL LADDER'S (Rungs 0–3). THIS TEAM DRAWS NOTHING FROM IT** and will not report spend against it. Registered here so no future lane reads a $1,000 headroom onto a VMFL case: this campaign's runs are in the **$0.01–$0.10 class** and its largest recorded case is `26.7` core-min. **Clause 2's discipline is adopted in full and binds every registration in this territory**, envelope or no envelope, because it was already this team's law and her wording is tighter than ours.

### §26.2 THE CAP RULE, AND THE DIRECTION ITS FAILURE RUNS — this is the clause worth reading

Caps in this territory are now set at **~3× the registration's own estimate, by this team, in the frozen bytes.** That makes the cap a **function of the estimate**, and it is worth being explicit about which way that fails.

**An under-filed estimate does not overspend. It strangles its own run.** A cap-hit is `rc 124` → **`NOT A RESULT` (budget/kill class)** — the whole run is forfeit and must be re-filed. So under `§26`:

> **AN OPTIMISTIC ESTIMATE IS NOT A CHEAP MISTAKE THAT COSTS A LITTLE MONEY. IT IS AN EXPENSIVE ONE THAT COSTS THE ENTIRE RUN, AND IT COSTS IT AT THE END, AFTER ALL THE COMPUTE HAS BEEN SPENT.**

**The worked example is this team's own, from today.** VMFL046 filed **12.00** core-min. Its own stated method — scale L1's uncontended rate by cell count over all three levels — yields `57 s × (1+4+16) = 1197 s = **19.95** core-min`. The filed figure was **1.66× below its own arithmetic** (`L-443`). Propagated through `§26.2`: — ⚠ **THE ARITHMETIC IN THIS PARAGRAPH AND IN THE TABLE BELOW IS REFUTED AND IS RETAINED ONLY AS THE STRUCK ORIGINAL (rule 6). THE `19.95` WAS BUILT FROM THE GRADED RUN'S OWN L1 WALL TIME, A DATUM THAT DID NOT EXIST AT FILING — reconstructing a method's output from a figure the graded run produced is structurally gate-fitting. Executed with the datum actually available (the smoke's L1 = 0.18 core-min) the method gives `0.18 × 21 = 3.78`, so the filed 12.00 was `3.17×` ABOVE its own arithmetic, not 1.66× below it. THE TEACHING OF THIS CLAUSE SURVIVES AND ITS WORKED EXAMPLE DOES NOT. See the dated correction at **`§27`** below (v1.22) and `L-443`'s own strike. **AND THE CORRECTED NUMBERS MAKE THIS CLAUSE STRONGER, NOT WEAKER:** the method executed faithfully on inputs available at filing sets a ~3× cap of **11.34** against **28.05** actually consumed — i.e. **following this estimate's own stated method would have KILLED THE RUN**, which is the exact failure direction this clause was written to name.**

| basis | estimate | ~3× cap it would set |
|---|---|---|
| filed | 12.00 | **36.0** |
| ~~the filed estimate's own stated method~~ **REFUTED, see `§27`** — correct value **3.78**, cap **11.34** | ~~19.95~~ | ~~**59.85**~~ |
| actual consumed | **28.05** | — |

The run consumed 28.05 and the frozen cap was 30, so **nothing was lost here — by 1.95 core-min.** Had the triple carried one more refinement level, or had the box been genuinely contended (it was not: `ExecutionTime/ClockTime` 0.988/0.989/0.998, waste **measured zero**), the filed estimate would have killed a completed solve at its cap. **The margin was luck, and it is recorded as luck.**

### §26.3 THE ARITHMETIC SELF-CHECK IS PROMOTED FROM ESCALATION-TIME TO FREEZE-TIME

Her clause 4 requires an arithmetic self-check **before escalating an exceedance**. In this territory the check runs **earlier — before the freeze — and it is a freeze precondition, not an escalation precondition:**

> **A registration's cost estimate is reconciled against its own stated method, in the frozen bytes, before the freeze commit. The reconciliation is written out (basis, arithmetic, result), and where the filed number differs from what its method yields, THE DIFFERENCE IS EXPLAINED OR THE FILED NUMBER IS CORRECTED.**

Rationale, stated plainly: an escalation-time check catches a bad estimate **after** it has already set a bad cap and, under `§26.2`, possibly already killed a run. **Checking at escalation time is checking after the damage.** This is the `§3` check-4 pattern — the pre-registration is verified as *committed* before compute, not as *intended* — applied to the one field of the pre-registration that nothing had ever verified.

**Honest note on provenance, because it cuts both ways.** This team derived the same finding independently at `L-443` hours before her ruling arrived, from VMFL046's own overrun. **That is corroboration of her rule, not credit for it** — and the corroboration is unflattering: we found it by filing an estimate that failed the check, not by running the check.

### §26.4 THE OTHER CLAUSES, AS THEY LAND HERE

- **Predicted-vs-actual and named waste at every completion** — already binding (`CLAUDE.md` rule 12, `COMPUTE_BUDGET_CHARTER` §6); unchanged, and this team states waste as *measured* where it can measure it, never as an inferred zero.
- **Node sizing / "never crop a grid to a box"** — has no application here yet: every case in this territory runs serially on the existing box, and no VMFL case has been shortened to fit hardware. **If one ever is, that is a `§26` disclosure in its frozen bytes, not a silent mesh choice.**
- **The no-blind-retries trigger (a third attempt at a twice-failed thing)** — this territory already carries R2/R3 rungs (VMFL007-R3, VMFL045-R2, VMFL017-R2, VMFL054-R2). **A THIRD attempt at any case whose first two attempts failed is escalated before it is filed**, with the arithmetic self-check done first per her clause 4.
- **"The box stays full, never idle."** The ansys queue is empty of solver rows **because every remaining candidate needs a pre-registration and a `§3` check-4 freeze**, not because the pipeline was neglected. `§26.5` fixes that.

### §26.5 SEQUENCING — the queue is filled from the CHEAP, SCALAR-REFERENCED end while the digitizer is built

The team's two work streams have opposite compute profiles and are sequenced so the daemon always has ansys rows:

1. **Scalar-referenced never-run cases** (a printed numeric target in the manual, no figure needed) are the **queue-fillers**: cheap, serial, gradeable against a printed number today, no dependency on the digitizer. These are registered and frozen continuously, ranked cheapest-and-lowest-risk first.
2. **The `§25` digitizer** is built and calibrated in parallel. Its calibration runs are **CPU-trivial** (synthetic plate rendering and image processing) and are queue-fillers of a different, near-zero-cost kind; they must never be described as substantial compute.
3. **The ~48 figure-heavy cases stay blocked behind `§25.7`** and no amount of queue pressure moves one forward early. **A queue-filling motive is exactly the pressure that would produce a badly-calibrated digitizer**, and `§25.2`'s order-of-operations is not relaxed to keep a daemon busy.

> **THE BOX BEING FULL IS NOT A REASON TO FREEZE A REGISTRATION THAT IS NOT READY.** Idle compute is a failure; a case frozen early to fill a slot is a worse one, because it produces a number that looks like a result. Where the two conflict, the queue waits.

| amendment | v1.21 |
|---|---|
| clause added | **`§26`** (`§26.1`–`§26.5`) |
| authority | Sanaa 2026-09-03 ~18:00Z, verbatim at `§26.1` |
| envelope | **this team draws NOTHING** from the $1,000 industrial-ladder envelope |
| adopted in full | per-run cap **~3× the team's own estimate**, set in the frozen bytes; predicted-vs-actual; waste named |
| tightened beyond her wording | the **arithmetic self-check moves from escalation-time to FREEZE-time** and becomes a freeze precondition (`§26.3`) |
| worked example, against us | ~~VMFL046's filed 12.00 vs its own method's 19.95 — a 1.66× under-file that would have set a **36.0** cap against **28.05** consumed~~ **REFUTED at `§27` (v1.22): the method on inputs available at filing gives 3.78, a cap of 11.34 against 28.05 consumed — the filed estimate was 3.17× ABOVE its own method, and following that method faithfully would have KILLED the run** |
| gates | **0 moved** · bands | **0 moved** · caps | **cap-SETTING RULE adopted; no existing cap moved** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.22, 2026-09-03 — **§27: `§26.2`'s WORKED EXAMPLE IS WRONG AND ITS DIRECTION IS INVERTED. THE CLAUSE'S CONCLUSION SURVIVES AND GETS STRONGER: FAITHFULLY FOLLOWING THAT ESTIMATE'S OWN METHOD WOULD HAVE SET A CAP THAT KILLED THE RUN.**

### §27.1 THE CORRECTION

`§26.2` was committed at `2e8d2f03` and cited `L-443` for the figure *"VMFL046 filed 12.00 core-min under a method yielding 19.95 — 1.66× under."* **The 19.95 was computed from the GRADED L1's 57 s wall time, a datum that did not exist when the estimate was filed** (freeze `23:20:59Z`; launch 200 s later). The datum the method actually had was the smoke's **L1 = 0.18 core-min** (`PREREGISTRATION.md:125`).

| basis | estimate | ~3× cap it sets | actual consumed |
|---|---|---|---|
| ~~the filed estimate's own stated method (v1.21 §26.2, WRONG)~~ | ~~19.95~~ | ~~59.85~~ | — |
| **the method executed on inputs available AT FILING** | **3.78** | **11.34** | **28.05** |
| filed | 12.00 | 36.0 | 28.05 |

**The filed 12.00 was 3.17× ABOVE its own stated method, not 1.66× below it.**

### §27.2 THE CLAUSE'S CONCLUSION IS NOT WEAKENED BY THIS — IT IS SHARPENED

`§26.2` argued that a ~3× cap makes the cap a function of the estimate, and that the failure direction is **strangling a run, not overspending**. The corrected numbers make that argument **more** forceful, not less:

> **HAD THE REGISTRATION FOLLOWED ITS OWN STATED METHOD FAITHFULLY, IT WOULD HAVE FILED 3.78 CORE-MIN AND SET A CAP OF 11.34. THE RUN CONSUMED 28.05. THE CAP WOULD HAVE KILLED A CORRECT, COMPLETED SOLVE AT ITS FINEST LEVEL, AFTER 21.9 CORE-MIN OF L3 COMPUTE HAD ALREADY BEEN SPENT.**

The filed 12.00 was **wrong in the safe direction by accident**. `§26.2` said the margin was luck; **the correction shows it was more luck than `§26.2` knew** — the run survived not because the estimate was good but because it was inflated 3.17× above a method that was itself badly broken. **Two errors in opposite directions, and the survival of the run is the product of both.**

### §27.3 WHAT ACTUALLY BROKE THE ESTIMATE, AND `§26.3` IS AMENDED FOR IT

The smoke's L1 converged at **2 777 iterations under `residualControl`**. **`residualControl` was removed in the same frozen document that carries the estimate** (`PREREGISTRATION.md:219`), so every graded level ran the full **20 000** iterations. The workload changed by **20000/2777 = 7.202×** and the estimate never carried it: `0.18 × 7.202 × 21 = 27.2236` against actual **28.05**, **ratio 1.0304** — one mechanism closing ~97 % of a 2.337× miss.

> **THE FREEZE PRICED A RUN AND THEN, IN THE SAME DOCUMENT, CHANGED THE WORKLOAD IT HAD JUST PRICED.**

**`§26.3` IS AMENDED, and the amendment is what makes it a real check:**

> **The freeze-time arithmetic self-check uses ONLY INPUTS AVAILABLE AT FILING** — a check fed by a number from the run it is checking grades the freeze against information the freeze could not have had, which is gate-fitting's structure wearing a cost basis. **AND it re-prices the workload against every configuration change the same document makes.** A registration that alters `residualControl`, `endTime`, `writeInterval`, the level count or the refinement ratio **re-derives its estimate after that alteration, in the frozen bytes**, or its estimate prices a run that was never going to happen.

**A decomposition that closes by construction is not corroboration.** `§26.2`'s *"1.66 × 1.41 = 2.34, closing the ratio"* is a **tautology**: for any intermediate anchor `A`, `(A/12) × (1683/A) ≡ 1683/720`. It cannot fail. **A decomposition that cannot fail to reconstruct its total has tested nothing**, and this charter will not cite one as evidence again.

### §27.4 ⚠ THE ACCURATE PREDICTOR WAS IN THE FROZEN BYTES AND I THREW IT AWAY

`PREREGISTRATION.md:159` records the pre-freeze smoke's **total as 28.2 core-min**. **The run consumed 28.05 — the discarded number was accurate to 0.53 %.**

It was discarded as *"contention-inflated, not representative"* (`:125-127`) — **my decision**, and I recorded it on the board as a **correction to my own cost instruction**, i.e. as a thing I had got right. The premise is refuted on the one apples-to-apples comparison available: **smoke L2 and graded L2 ran the same 12 800-cell mesh to the same 20 000 iterations in 321 s vs 310 s — 3.5 % apart.** (Honest qualification, retained: smoke L1 *was* ~1.36× slower per iteration, so contention was **not** zero — it was nowhere near large enough to justify discarding the number.)

> **A CONTENTION ARGUMENT IS A MEASUREMENT CLAIM AND IS HELD TO A MEASUREMENT'S STANDARD.** Discarding a datum as contaminated requires **measuring the contamination on a comparable level**, not inferring it from ambient load. `ExecutionTime/ClockTime` is available in every log this team produces and settles it in one line — the same ratio that later showed this run's waste was **measured zero**.

### §27.5 PROVENANCE, BECAUSE IT DECIDES HOW MUCH THE CLAUSE IS WORTH

Found by **`ansys-lane-opus`**, against the supervisor who wrote `L-443`, committed `§26.2`, **and briefed that lane with the wrong number as though it were established**. The lane checked the figure it was handed instead of building on it. **Verified personally in the frozen bytes before acceptance** (`§3` check 3), which is the only reason it is in a charter rather than in a report.

`L-443` carries the same correction as a dated addendum at `c4c63cfa`; the struck text is preserved there, not rewritten.

| amendment | v1.22 |
|---|---|
| clause added | **`§27`** (`§27.1`–`§27.5`) |
| corrected | **`§26.2`**'s worked example — 19.95 → **3.78**; the filed estimate was **3.17× ABOVE** its own method, not 1.66× below |
| conclusion | `§26.2`'s ruling **SURVIVES AND STRENGTHENS** — the method-true cap of **11.34** would have killed a run that consumed **28.05** |
| amended | **`§26.3`** — the freeze-time self-check uses **only inputs available at filing**, and **re-prices against configuration changes the same document makes** |
| banned | citing a decomposition that closes **by construction** as corroboration |
| found by | **a lane, against this supervisor**, who had briefed it with the wrong number |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.23, 2026-09-03 — **§28: `§25` HAD A WRONG-NUMBER PATH AND A LOOPHOLE THAT REOPENS `§25.2` UNDER A NEW NAME. A LANE FOUND BOTH BEFORE THE INSTRUMENT WAS FROZEN, WHICH IS THE ONLY TIME FINDING THEM IS CHEAP.**

### §28.1 WHY THIS AMENDMENT EXISTS AT ALL

`§25` was written by me and handed to `ansys-lane-opus48` as a specification to build against, with the standing instruction that **finding a hole in the charter is the highest-value thing a lane can do.** It returned five, one of them a path that would have let a **wrong shock location** through a gate. All five are adopted. **`§25` was eight hours old and had never met an implementer; that is exactly how long a specification survives contact with the thing it specifies.**

### §28.2 ⚠ THE WRONG-NUMBER PATH — `u_read` MUST BE IN THE GATED QUANTITY'S OWN DIMENSION

`§25.6` requires the fold `|CFD − ref| ≤ sqrt(tol² + u_read²)` **"with both terms in the same units."** `§25.4` derives `u_read` from *"synthetic-control RMS error"* **and never says of WHAT.** The natural implementation — RMS of the digitized curve against truth — is a **y-value** error. **The first plate this team wants (Fig. .46.2) is gated on SHOCK LOCATION, which is an x-POSITION.** A y-units `u_read` folded into an x-location band is dimensionally meaningless and would have produced a gate that looked complete and was not.

> **RULED: every term of `§25.4` — the synthetic-control statistic, the pixel floor, and the half-spread of the two read-offs — is computed ON THE GATED QUANTITY, IN THAT QUANTITY'S OWN UNITS.** A `u_read` derived for a value-at-a-station does not license a gate on a position, an integral, a slope, or a peak. **One plate can carry several gated quantities, and each needs its own `u_read`.**

The instrument as built calibrates **value** read-offs correctly and is not wrong; it is **incomplete for a position gate**, and the incompleteness was invisible from `§25`'s text.

### §28.3 ⚠ THE LOOPHOLE THAT REOPENS `§25.2` — AN AUTOMATED READER CAN SHRINK ITS OWN UNCERTAINTY

`§25.4`'s *"half the spread of two independent read-offs"* was written for **human** digitizers, where independence is a fact about two people. For an **automated** reader, independence must be manufactured by perturbing defensible operator choices — and **narrowing the perturbation range narrows the spread, which narrows `u_read`, which widens the effective margin.**

> **THAT IS `§25.2`'s FORBIDDEN MOVE WEARING A NEW NAME:** sizing the uncertainty to suit the answer, done through a range parameter instead of through the read-off itself.
>
> **RULED: the perturbation ranges are PRE-REGISTERED IN THE FROZEN BYTES, with a stated defence of why each range spans the choices a competent reader could actually have made. A range narrowed after any target value is known is a `§25.2` violation and voids the calibration.** Where the ranges are disputed, the WIDER defensible range is used — `u_read` errs large, and `§25.6`'s `u_read ≥ tol/3` cap is the honest consequence, not something to engineer around.

### §28.4 THE AXIS PLANT DOES NOT CATCH A FLIP — AND IT BIT THE BUILD

`§25.3`'s held-out-tick check verifies the axis fit against a tick excluded from it. **A consistently REVERSED axis pairing is still a self-consistent straight line**, so the held-out tick lands on the wrong line at **~0 px error** and the plant passes. The lane hit this in its own build: **RMS ≈ 1.09 at near-zero bias** — the signature of a correct-shaped fit in the wrong direction.

> **RULED: `§25.3`'s "log axes declared explicitly" extends to ORIENTATION declared explicitly, and the AXIS PLANT adds a SLOPE-SIGN check against that declaration.** A guard that passes on a flipped axis is a guard whose two sides degrade together (`L-436`'s class) — the fit and its held-out check are wrong in the same direction and agree.

### §28.5 A WHOLE-CURVE RMS AVERAGES THE EASY PART WITH THE PART YOU ARE READING

An RMS over an entire digitized curve mixes flat regions (easy, sub-pixel) with steep regions (hard, where a one-pixel horizontal error is a large value error). **A read taken near a shock — which is the whole point of Fig. .46.2 — is a steep-region read**, and a whole-curve RMS understates its uncertainty.

> **RULED: where the gated quantity is read in a locally steep region, `u_read` uses the STEEP-REGION statistic, not the whole-curve one.** The instrument reports both. **The statistic is chosen by where the read happens, and that choice is frozen before the read.**

### §28.6 `§25.3`'s "MATCHED TO THE TARGET PLATE" vs `§25.2`'s "DO NOT READ THE TARGET PLATE"

The two clauses collided as written. **Resolved: synthetic plates are matched to the target's ANSWER-BLIND FORMAT** — DPI, axis ranges and scale type, tick density, line width, marker style, gridline density, aspect ratio: every one measurable without reading the plotted curve.

**Consequence, stated because it is a cost and not a detail: `u_read` is PER-TARGET-FORMAT and is RE-DERIVED PER CASE.** There is no single lab-wide `u_read`, and a calibration performed for one figure does not transfer to another by assertion. `§25.7`'s authorisation is per case.

### §28.7 THE DIGITIZER'S OWN CAP, UNDER `§26.2`

Filed estimate **0.1 core-min** (basis: 0.117 s per render-and-digitize measured on this box × ~32 operations ≈ 4 s wall, serial). Per `§26.2` the cap is **~3× the team's own estimate: 0.3 core-min.** The lane proposed 5, which is **50×** and not the discipline.

**A tight cap is safe HERE and the reason is worth stating, because it does not generalise:** a cap-hit on this task forfeits ~4 seconds and a re-file. `§27.2` showed a cap-hit on VMFL046 would have forfeited **21.9 core-min of already-spent L3 compute**. **The cost of losing a run is not the cost of the run's estimate, and `~3×` is a discipline on the estimate, not a judgement about the loss.** Observed and recorded; not acted on beyond applying her rule as written.

Per `§27.3`, the estimate is reconciled against its own stated method **using only inputs available at filing** — `0.117 s × 32 ÷ 60 = 0.0624` core-min against a filed 0.1, i.e. filed **1.6× above** its own method with the margin disclosed, not silently absorbed.

### §28.8 WHAT IS STILL NOT AUTHORISED

`§25.7` is unchanged and unmet. **No case gates on a digitized reference.** The instrument has run its selftest only; `--calibrate` is compute the freeze governs and has **not** been run, so **no `u_read` exists** and this task has **no verdict**. VMFL046-R2 remains a future **new registration**, and **row #54's `GATE FAIL` is permanent** whatever any calibration returns.

| amendment | v1.23 |
|---|---|
| clause added | **`§28`** (`§28.1`–`§28.8`) |
| ⚠ wrong-number path CLOSED | `u_read` computed **on the gated quantity in its own units** — a value-`u_read` never licenses a position gate |
| ⚠ loophole CLOSED | perturbation ranges **pre-registered and defended**; narrowing one after a target value is known **voids the calibration** |
| plants strengthened | axis **orientation** declared + **slope-sign** check (the held-out tick passes a flipped axis) |
| refined | steep-region `u_read` where the read is steep; synthetic plates matched to the **answer-blind format**; `u_read` is **per-case** |
| cap ruled | digitizer estimate **0.1** core-min, cap **0.3** (`~3×`, `§26.2`) — the lane's 5 was 50× |
| found by | **`ansys-lane-opus48`, against the supervisor who wrote `§25`**, before the freeze |
| gates | **0 moved** · bands | **0 moved** · caps | **1 SET (new task)** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.24 — 2026-09-03 — **§29: THE DIGITIZER CALIBRATED, ITS PLANTED NULL REFUSED, AND THE VERDICT IS `NOT A RESULT`. A PIXEL FLOOR IS A FLOOR ON RESOLUTION, NOT ON THE READER'S ERROR — AND `u_read` PINNED TO IT IS A FALSE PRECISION A NULL CONTROL EXISTS TO CATCH.**

### §29.1 THE VERDICT

The `§25`/`§28` digitizer instrument was frozen (`0fab170f`, blob
`2092c55d…`), `§3` checks 1 and 4 done personally, and `--calibrate --n 24` run.
**It refused (exit 2) at POSITION PLANT-NULL** and the task verdict is
**`NOT A RESULT`**, reproduced by the supervisor against the freeze to
byte-identical numbers (`cases/ansys_verification/DIGITIZER/RESULTS.md`). The
instrument **unlocks nothing** (`§25.7`, `§28.8`), and this holds even though the
VALUE quantity calibrated cleanly.

| quantity | u_read | binding term | plants |
|---|---|---|---|
| VALUE (y-data) | 0.0050505 | pixel floor | DETECT band OK, bias 0.000265 ≤ u_read — **passed** |
| POSITION (x-data) | 0.0027778 (candidate) | pixel floor | **PLANT-NULL REFUSED**: clean control read 1.167 px > floor |

### §29.2 WHAT ACTUALLY FAILED — the pixel floor is a floor on the wrong thing

The pre-registration predicted `u_read ≈ pixel floor` for both quantities (its
`§5`, "A and B < C"). **The prediction held — and for POSITION that is exactly
the failure.** The pixel floor (1.000 px) sits **below** the steepest-descent
locator's own demonstrated per-plate error on clean plates: **mean 0.843 px, max
1.693 px**, the null-control plate **1.167 px**.

> **A PIXEL FLOOR BOUNDS HOW FINELY THE RASTER CAN BE READ. IT SAYS NOTHING ABOUT
> HOW WELL A GIVEN READER LOCATES A GIVEN FEATURE.** When the reader's own error
> exceeds the floor, a floor-dominated `u_read` claims a precision the reader does
> not have — a **false precision** — and `max(A, B, C)` does not protect against
> it, because the floor `C` can be the largest of the three and still be below the
> reader's real error. The three-floor `max` protects against a `u_read` that is
> too *small* relative to its three inputs; it does not protect against a *statistic
> that is itself optimistic.*

**Only the planted null caught it.** A null control tied to a known-zero answer
(`rule 3`, `§16.4`) is the one instrument that compares `u_read` against the
reader's demonstrated behaviour on a plate whose truth is zero displacement.
Inspection of the three-floor `max` would have passed this `u_read`; the null
refused it. **This is the null control earning its place a second time this
session** (VMFL046's plants, now this).

### §29.3 THE RULING — the synthetic-control statistic must make the null pass BY CONSTRUCTION

`§25.4`'s term A — "the synthetic-control statistic" — was implemented as an RMS.
**An RMS understates a distribution with a tail**, and the POSITION locator's
error has one (mean 0.843 px, max 1.693 px). The null control samples one plate;
if that plate is near the tail, it exceeds an RMS-based `u_read`.

> **RULED: term A of `§25.4` is a statistic that DOMINATES the worst demonstrated
> per-plate error on the calibration set — a maximum, or a high percentile (≥ 95th)
> with the max reported beside it — for any quantity whose per-plate error CAN
> exceed the pixel floor.** The test of whether A is conservative enough is not an
> argument: it is that ~~**the planted null passes by construction**~~ **⚠ REFUTED BY `§35.2`: A NULL THAT PASSES BY CONSTRUCTION CANNOT REFUSE AND IS THEREFORE NOT A CONTROL — it must be evaluated on a HELD-OUT specimen**, because `u_read`
> is then ≥ every clean-plate error the calibration measured, the null-control
> plate included. RMS remains admissible only for a quantity whose max per-plate
> error is itself below the pixel floor (the floor then binds and dominates the
> tail), which is where VALUE sits and POSITION does not.

This is `§28.2`'s discipline extended: `§28.2` fixed *which units* the statistic is
in; `§29.3` fixes *which statistic*, so that the number `u_read` reports is one the
reader can actually back.

### §29.4 THE RE-FILE — POSITION re-registered; VALUE not carved out to soften a `NOT A RESULT`

- **POSITION is re-filed** as a new registration with term A per `§29.3` (max /
  high-percentile). The lane also offered a sub-pixel locator (parabolic fit to the
  gradient minimum) to pull the error below one pixel; **that is a legitimate second
  improvement but it is not the fix** — a sharper locator with an RMS statistic can
  still hide a tail. `§29.3` (the conservative statistic) is the required change;
  the sub-pixel locator is optional and, if used, its own max error must still
  dominate `u_read`.
- **VALUE calibrated cleanly and is NOT certified here by carving it out of the
  failed task.** A `NOT A RESULT` task is not softened by keeping its clean limb;
  that is the vocabulary discipline (`rule 1`) applied to an instrument. VALUE is
  carried into the re-file as a **separately-registered quantity**, where its clean
  calibration stands on its own frozen bytes.
- **This task's `NOT A RESULT` is permanent.** The re-file is a new registration and
  does not re-grade it.

### §29.5 WHAT IS STILL TRUE, AND WHAT THIS COSTS THE CAMPAIGN

`§25.7`/`§28.8` remain unmet: **no VMFL case gates on a digitized reference.** The
survey established that ~~**45 of 49 remaining cases are figure-only**~~ **⚠ THAT PAIR DOES NOT SURVIVE ITS OWN RE-COUNT AND IS STRUCK AS UNPINNED PROSE — see `§32.4`. It appears in NO dated survey artifact and cannot be reproduced from `CASE_MAP.md` by any stated method. A re-count gives ~46 of 48; the RATIO holds (~92 % → ~96 %, overwhelmingly figure-only) and the QUALITATIVE claim stands, but the figure-only count ROSE while the remaining count FELL, which is impossible under a shared classification and therefore proves the two numbers rest on different ones. And "remaining" is a MOVING TARGET that changes with every run, so a fixed pair in charter prose is structurally wrong whatever its value.**, and Fig .46.2
(VMFL046-R2's target) is a **POSITION** read — the exact quantity that just failed
to certify. **The path to those 45 cases now runs through the POSITION re-file**,
and a `u_read` built per `§29.3` will be **larger** than the pixel floor, so
`§25.6`'s `u_read ≥ tol/3` cap will bind on more of them: **more of the 45 will be
`GATE REACHED` by construction than the earlier estimate assumed.** Stated here so
no later report reads the re-file as a delay rather than as the honest cost of
reading a position off a picture.

| amendment | v1.24 |
|---|---|
| clause added | **`§29`** (`§29.1`–`§29.5`) |
| verdict recorded | DIGITIZER calibration **`NOT A RESULT`** (POSITION PLANT-NULL refused); reproduced personally |
| ruled | `§25.4` term A **must dominate the worst demonstrated per-plate error** (max / high-percentile) for any quantity whose error can exceed the pixel floor; the null passing **by construction** is the test |
| re-file | POSITION re-registered per `§29.3`; VALUE carried as a separate quantity, **not** certified by carving out a failed task |
| campaign cost | more of the 45 figure-only cases will be `GATE REACHED` by construction than assumed |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.25, 2026-09-03 — **§30: A CORRECTION FILED ONLY AT THE FOOT DOES NOT REACH THE READER OF THE CLAUSE. `§26.2` WENT ON TEACHING THE REFUTED ARITHMETIC FOR AS LONG AS `§27` SAT FIFTY LINES BELOW IT — AND THE SUPERVISOR PROVED IT BY RE-BRIEFING A LANE WITH THE REFUTED NUMBER HOURS AFTER WRITING THE REFUTATION.**

### §30.1 THE DEFECT

`§27` (v1.22) correctly refuted `§26.2`'s worked example: the `19.95` was reconstructed
from the **graded run's own L1 wall time**, a datum that did not exist at filing, and the
method executed on inputs actually available gives **3.78**, making the filed 12.00
**3.17× ABOVE** its own arithmetic rather than 1.66× below it.

**That correction was filed as an appended section and nothing was marked at the point of
use.** `§26.2`'s body paragraph, its three-row cap table and the v1.21 summary table all
continued to state `19.95` and `1.66×` with **no marker and no forward pointer**. A reader
who greps for the estimator rule, or who is told "read `§26.2`", lands on the refuted
arithmetic and never reaches `§27`.

> **THIS IS NOT A COSMETIC FILING COMPLAINT. `§26.2` IS THE CLAUSE WHOSE ENTIRE FUNCTION IS
> TO TEACH HOW TO RECONCILE AN ESTIMATE AGAINST ITS OWN METHOD. ITS TEACHING **IS** ITS
> WORKED EXAMPLE. AN UNMARKED WRONG WORKED EXAMPLE IN THAT CLAUSE TEACHES THE PRECISE
> GATE-FITTING-SHAPED ERROR THE CORRECTION EXISTS TO NAME.**

### §30.2 THE PROOF THAT IT REACHES NOBODY — AND IT IS AGAINST THE SUPERVISOR, AGAIN

`§27.4` already records that the wrong figure entered a lane brief because the supervisor
"briefed that lane with the wrong number as though it were established."

**The same supervisor did it again today, after writing `§27`.** On re-forming this session
the supervisor dispatched two lanes and handed both the refuted framing verbatim — *"VMFL046
filed 12.00 core-min under a method that yields 19.95 (1.66× under)"* — as an instruction to
apply to VMFL024 and to a cost-ranking task. It was caught only because the supervisor then
read `docs/COST_CALIBRATION.md` row `C-20260903T162543.364120Z-e486a4a1` for an unrelated
reason, and both lanes were corrected by message in the same turn, before either had filed
anything.

> **A CORRECTION THE AUTHOR OF THE CORRECTION FORGETS WITHIN HOURS IS NOT AN EFFECTIVE
> CORRECTION. THE FAILURE IS NOT MEMORY — IT IS THAT THE REFUTED TEXT WAS STILL THE MOST
> FINDABLE STATEMENT OF THE FACT.** Recall competes with the document; the document was
> still saying `19.95` in three places and `3.78` in one.

### §30.3 THE RULE — CORRECT AT THE POINT OF USE, NOT ONLY AT THE FOOT

**Binding on this territory from v1.25:**

1. When an amendment refutes a **number, table cell or worked example** in an earlier clause,
   the earlier text is **marked in place, in the same commit as the refutation** — struck
   (`~~…~~`) with a pointer to the refuting section and the corrected value inline.
2. **⚠ NEVER ANNOTATE FROZEN BYTES — THE OBVIOUS FIX IS THE WRONG ONE, ruled against this clause at `VERIFICATION_CHARTER` v1.51 `§2ae` and adopted here at `§31.3`.** For an executable comparator or a frozen pre-registration, an in-place marker **changes the sha**, and rule 2 fixes the grading path **by sha** — so marking the artifact destroys the very property that makes the freeze evidence. **The correction must be reachable FROM WHERE THE NUMBER IS READ, NOT FROM WHERE IT WAS WRITTEN:** the **register row's VERDICT CELL** and the **head of the results record's section**, never the comparator's source. This clause's in-place marking therefore applies to **prose records only** (this charter, board, register, results), never to frozen executable or pre-registration bytes. Where it does apply, the mark is made **without adding or removing a line**, so every later amendment's
   `lines whose number changed above this section: 0` assertion survives. Text is appended
   within the existing line. *(This amendment: exactly **3 lines changed in place, 0 added,
   0 removed**; file length **2069 → 2069** before this block.)*
3. The original is **struck, never rewritten** (rule 6). The refuted value stays readable —
   the reader must be able to see what was believed and what replaced it.
4. **A correction is not complete when it is written. It is complete when the refuted text
   can no longer be read as current.**

### §30.4 WHAT THIS DOES AND DOES NOT DO

**No gate, band, cap, threshold, verdict or register byte moves.** No case is re-graded.
`§26.2`'s operative rule — caps at ~3× the team's own estimate, set in the frozen bytes —
is **unchanged**; only its worked example is marked, and `§27`'s already-recorded finding
that the corrected numbers make the clause **stronger** (a faithful cap of **11.34** against
**28.05** consumed would have **killed the run**) is now stated at the point of use.

| amendment | v1.25 |
|---|---|
| clause added | **`§30`** (`§30.1`–`§30.4`) |
| marked in place | `§26.2` body paragraph, `§26.2` cap table row, v1.21 summary-table row — all three now strike `19.95`/`1.66×` and point to `§27` |
| finding, against the supervisor | the refuted figure was re-issued to **two lanes** in lane briefs hours after `§27` refuted it; caught by reading the calibration ledger, corrected by message before either lane filed |
| ruled | a refutation is filed **at the point of use in the same commit**, marked without changing any line number |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · register bytes | **0** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.26, 2026-09-03 — **§31: ROW #54 IS DEMOTED `GATE FAIL` → `NOT A RESULT`. IT VACATES A RECORDED FAILURE AGAINST THIS TEAM AND SAYS SO. · §30 IS UPHELD AND ITS METHOD IS CORRECTED: NEVER ANNOTATE FROZEN BYTES.**

### §31.1 THE DEMOTION

Row **#54** (`VMFL046`) is demoted to **`NOT A RESULT`** under `CLAUDE.md` rule 5 step (1),
the class having been ruled by the verification team at `VERIFICATION_CHARTER` **v1.51
§2ac/§2ad** (`e5f0ddf3`), read at source. **This team held the demotion rather than take it
unilaterally, and that ruling unblocked it.** The full record — ground, the three `§2ad`
disclosure burdens, and the frozen reinstatement condition — is the dated demotion note at
the foot of `ANSYS_VALIDATION_REGISTER.md`, and the demotion is carried **in row #54's own
verdict cell** per `§2ae`.

**The ground is a `CLAUDE.md` rule 3 false zero inside a graded gate.** The plateau limb read
**4.332e-10** — a near-exact zero — for a shock moving **192.60 % of its own tolerance band**,
because `x = 0.900` is **supersonic and upstream** of the shock and cannot causally see it.
**Three guards, one geometry, defeated identically: one blind station wearing three coats.**

### §31.2 THE ASYMMETRY, ADOPTED AS THIS TEAM'S OWN STANDING DUTY

`§2ad` ruled that rule 5's permission is symmetric while the **disclosure burden is not**.
Adopted verbatim as binding on this territory:

> **A DEMOTION THAT RELIEVES THIS TEAM OF A RECORDED FAILURE MUST, ON ITS OWN FACE: (1) STATE
> THAT IT DOES SO; (2) PRESERVE EVERY FINDING OF THE VACATED VERDICT THAT RESTS ON SETTLED
> LEVELS, so the adverse content is not lost with the label; (3) NAME, IN ADVANCE, WHAT WOULD
> HAVE TO BE TRUE FOR THE VERDICT TO BE REINSTATED.** No such burden attaches to demoting our
> own `PASS` — that act is already against interest.

**Stated against ourselves, because it is the whole point of the clause:** row #55 was
`PASS` → `NOT A RESULT`, **self-adverse, and cost this team a credential**. Row #54 is
`GATE FAIL` → `NOT A RESULT`, **same direction under the rule, opposite incentive**. Verification
recorded that running the unfavourable one first, with zero discretion, is why `§2ad` could be
written as a duty to disclose rather than a permission to withhold. **That is a reason to hold
the standard, not a credit to spend: the burden binds this team identically on the next one,
and a team that treats a good precedent as a licence has already lost it.**

### §31.3 `§30` UPHELD, AND ITS METHOD CORRECTED — THE OBVIOUS FIX IS FORBIDDEN

`§30` said *"a correction filed only at the foot does not reach the reader of the clause."*
Verification upheld it as naming a real gap in rule 6. **But `§30.3` rule 2 as written would
have led a successor straight into a worse error**, and `§2ae` names it:

> **NEVER ANNOTATE FROZEN BYTES.** Marking a frozen comparator or pre-registration in place
> **changes its sha**, and rule 2 fixes the grading path **by sha** — so the marker destroys
> the very property that makes the freeze evidence.

> **RULED — `§31.3`: THE CORRECTION GOES WHERE THE NUMBER IS READ, NOT WHERE IT WAS WRITTEN.**
> A reader about to believe a verdict consults the **REGISTER ROW** and the **RESULTS RECORD** —
> never the comparator's source. So a demoted or corrected verdict carries its correction **in
> the register row's VERDICT CELL** and **at the head of the results record's section**. The
> foot amendment **remains required and remains insufficient alone.** `§30`'s in-place marking
> applies to **prose records only**; `§30.3` rule 2 is marked in place accordingly.

**Honest note on my own compliance:** `§30` was written and committed *before* this ruling, and
what it marked was this charter's own prose — no frozen byte was touched and no sha moved. **That
was luck of scope, not foresight**: the clause as drafted did not distinguish prose from frozen
bytes, and a successor applying it to a comparator would have broken a freeze. The distinction is
verification's, and it is adopted because it is right, not because it was ordered.

### §31.4 NO SWEEP

Rows #54 and #55 are **ONE specimen with two rows** — the same unconverged finest level, one
geometry. `§2af` rules two instances **a pattern and not a class** and orders **no sweep**;
`§2ac` is **forward-only** and schedules no backfill. **This team orders none either**, and
records that a supervisor who applies a threshold only to other teams' classes has no threshold.

| amendment | v1.26 |
|---|---|
| clause added | **`§31`** (`§31.1`–`§31.4`) |
| verdict moved | row **#54** `GATE FAIL` → **`NOT A RESULT`** — and it **vacates a recorded failure against this team**, disclosed per `§2ad` |
| findings PRESERVED | the shock-moves-away finding on `L1 → L2` (**+1.7288 % → −4.0612 %**, both settled), reported-not-gated; the manual corroboration (−0.1274 %); the `§18` three-path reproduction |
| findings CONTAMINATED | the L3 shock reading, the **−12.9165 %** Richardson, `p_obs` 0.700440, the peak-Mach Richardson 2.175831 — all consume the unsettled level |
| reinstatement condition | ~~**frozen in advance**~~ **⚠ NARROWER THAN IT READS (`VERIFICATION §2am.7`, adopted at `§37.2`): frozen before any RE-RUN existed, but 18 h 36 min AFTER the data that answers it and 13 min 33 s after the artifact printing that answer — this wording invites a reader to think otherwise**: finest-level shock final-window drift ≤ **6.25e-04 m**; if the settled `x_shock` then misses 1.250 by > 5 %, the `GATE FAIL` **is reinstated** |
| method corrected | `§30.3` rule 2 — **never annotate frozen bytes**; correction goes in the register row's verdict cell and the results record's section head |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **1 (row #54, demotion only)** · credentials created | **0** |
| solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.27, 2026-09-03 — **§32: THE `probe_series` DEFECT IS REAL BUT NARROWER THAN THE AUDIT THAT ROUTED IT, AND THE CORRECTION RUNS BACK UPHILL · ONE QUANTITY IS CARRIED EXPLICITLY AS `UNMEASURED` · VMFL024's "EXPERIMENTAL" TARGETS ARE THE ANALYTIC RIGID-BODY LIMIT TO MACHINE PRECISION · AND AN AUDIT OF MY OWN ABANDONED READS**

### §32.1 `probe_series` — CONFIRMED, RE-CHARACTERISED, AND THE AUDIT'S FRAMING CORRECTED

The verification team's `VR3-R2` routed *"4 of 12 registered sites UNGUARDED — a lexical
`sorted(glob.glob("postProcessing/*/U/gateProbes"))` with no `len()` guard."* **The numerator
is right and the characterisation is not.** Verified on disk by this team:

- **The count holds: exactly 4** `def probe_series` definitions — `VMFL001/grade_vmfl001.py:355`,
  `VMFL001/R2/grade_vmfl001_r2.py:415`, `VMFLGPU001/grade_vmflgpu001.py:586`,
  `VMFLGPU001-R2/grade_vmflgpu001_r2.py:611`. *(The "of 12" denominator is verification's own
  scoped set; 34 `grade_*.py` comparators exist overall. We confirmed the numerator, not the
  denominator, and say so.)*
- **⚠ "UNGUARDED" IS IMPRECISE — ALL FOUR REFUSE AN EMPTY GLOB** (`if not hits: refuse(...)`),
  and VMFL001 and its R2 additionally carry `if len(vals) < 10: refuse(...)`. The GPU pair's
  function bodies lack an internal `len` guard, but their caller `iterative_convergence`
  refuses on `n_avail < PLATEAU_MIN`. **On verification's own four-faces test these paths CAN
  distinguish "ran and found nothing" from "did not run" — they refuse in both.**
- **⚠ THE GLOB PATH IN THE AUDIT IS TRANSCRIBED WRONG.** The function-object name is
  `gateProbes`, so the real pattern is `postProcessing/gateProbes/*/U`, not
  `postProcessing/*/U/gateProbes`.
- **THE GENUINE SHARED DEFECT IS THE LEXICAL SORT** — `sorted()` over string time-directory
  names with no numeric key, so **`"1000"` sorts before `"200"`** and a multi-segment history
  is concatenated out of time order; `vals[-n:]` then takes a "tail" that is not the latest
  samples.

> **SEVERITY: `LATENT`. A REAL DEFECT THAT CHANGED NO NUMBER IN ANY RECORDED VERDICT — and
> the reason is measured, not assumed.** Every `gateProbes` function-object in every run on
> this box holds **exactly one time-directory, `0`** (verified by directory listing across
> VMFL001 L1/L2/L3, its R2, and VMFLGPU001 gpu/). **`sorted()` on a one-element list is a
> no-op**, so nothing was ever reordered. These are steady solves to a fixed `endTime` with no
> restart, so a single segment is produced by construction. **The realistic trigger is a
> CRASHED-AND-RESUMED run**, which writes a second time-directory — and that is when this
> would activate, silently, in the **false-favourable** direction: a flatter early segment
> landing at the end could **falsely report a plateau** and let a non-converged level be
> graded. *That is the same direction of harm as `§31`'s blind plateau, reached by a different
> road.*

**ALL FOUR FILES ARE FROZEN** — each working-tree blob hashes to the comparator sha cited in
its own `PREREGISTRATION.md` (`8cb29610…`, `64b02be8…`, `21fa2387…`, `6a5d0fe7…`). **NONE MAY
BE EDITED** (`§31.3`): an in-place fix changes the sha and destroys the property that makes
the freeze evidence. **The repair is a NEW registration** carrying a guarded reader — numeric
key `int(float(basename))`, explicit empty-glob refusal, explicit too-few-samples refusal, and
a **monotonic-time assertion** that fires exactly on the failure the lexical sort would cause —
with a `--selftest` that plants a two-segment history named `{"0","200","1000"}` and asserts
numeric ordering. **Given no verdict moved, a documented disclosure is the proportionate
alternative to a re-run**, and it lives where the number is read (`§31.3`), never in the source.

### §32.2 ⚠ ONE QUANTITY IS CARRIED EXPLICITLY AS `UNMEASURED`, NOT AS CHECKED

**`VMFLGPU001-R2`'s `gateProbes` segmentation CANNOT BE READ FROM THIS BOX.** Its run root
exists here and is **empty**; the run lives read-only on the remote GPU instance and is not
synced. Single-segment is **inferred from the case family, not re-read on disk.**

> **THIS IS THE ONE OF THE FOUR THAT CARRIES A FAVOURABLE-DIRECTION VERDICT — row #39,
> `GATE REACHED`** — so it is precisely the one where a falsely-reported plateau would matter.
> Under the chief's standing rule *(a classifier-blocked measurement is an UNMEASURED quantity,
> not a closed question)* it is recorded as **`UNMEASURED`** and **not** as verified. **Nothing
> in this team's records may cite VMFLGPU001-R2's segmentation as checked.** Re-deriving it
> requires reading the remote instance, which is not done here.

### §32.3 VMFL024's "EXPERIMENTAL" TARGETS ARE THE ANALYTIC RIGID-BODY LIMIT, TO MACHINE PRECISION

Verified by arithmetic, and it changes what that case is worth. The manual's Table .24.2
targets (p. 92) are **exactly `r/R`**: `4.83/23 = 0.210000` (difference from the printed 0.21:
**2.78e-17**), `9.43/23 = 0.410000` (**0**), `14.26/23 = 0.620000` (**0**).

> **THOSE ARE NOT THREE EXPERIMENTAL DATA POINTS. THEY ARE THE `t → ∞` SOLID-BODY ASYMPTOTE,
> WRITTEN OUT.** And Ansys's own `t = 80 s` values (0.2093 / 0.4109 / 0.6221) sit **−0.333 % /
> +0.220 % / +0.339 %** from that asymptote — i.e. **at 80 s the flow is already at solid body
> to a third of a percent.** So the gate tests little more than *"does the solver spin up to
> rigid-body rotation."* This **strengthens** the lane's smoke design (initialising AT solid
> body plants a state whose values are the published table, revealing nothing) and **weakens
> the case's verification value**, which must be stated before VMFL024 is described as an
> experimentally-referenced credential candidate. It is already capped at `GATE REACHED`;
> this is the reason behind the cap, not merely its bookkeeping.

### §32.4 `§29.5`'s "45 OF 49" DOES NOT SURVIVE ITS OWN RE-COUNT — STRUCK, WITH THE RATIO PRESERVED

The figure appears in **no dated survey artifact** and cannot be reproduced from `CASE_MAP.md`
by any stated method. A re-count against today's register run-set gives **~46 of 48**. **The
ratio holds (~92 % → ~96 %) and the qualitative claim — overwhelmingly figure-only — stands.**
But the figure-only count **ROSE** while the remaining count **FELL**, which is impossible
under a shared classification, and therefore **proves the two figures rest on different
classifications.** Marked in place at `§29.5`.

> **AND A FIXED PAIR WAS STRUCTURALLY WRONG WHATEVER ITS VALUE: "remaining" is a MOVING TARGET
> that changes with every run.** A count of remaining work does not belong in charter prose at
> all; it belongs in a dated, script-derived artifact. *(Honest limit: the re-count's own
> classifier is a crude `"profile"`-string heuristic over `CASE_MAP.md` scope flags that are
> themselves partly stale — see the census correction — so **46 of 48 is a drafted figure with
> a stated method, not a frozen one.** It is enough to establish that 45-of-49 does not
> survive; it is not enough to replace it, and it is not written into this charter as if it
> were.)*

### §32.5 AN AUDIT OF MY OWN ABANDONED READS — the chief's addendum applied to the supervisor

The plant-the-run test was extended to *an agent's own abandoned measurements, not only
scripts*. Audited, and **three reads I began and did not finish are closed here**: the VMFL024
contamination arithmetic I said I would verify personally and had not (`§32.3` — it holds, and
it found more than it was sent for); the `§29.5` marking I grepped and left (`§32.4`); and the
census correction I drafted and left unlanded. **A fourth is closed as `UNMEASURED` rather
than as done** (`§32.2`). **Still outstanding and named rather than quietly carried: `N-AV16`
and ~~`L-465`~~ **`L-477`** *(WRONG TWICE — `L-465` was long taken, and `L-476` was taken by a peer DURING this landing; re-derived as max+1 in the committing invocation per rule 11; see `§35`)* are owed for the causal-blindness finding and its caller-side cousin.**

| amendment | v1.27 |
|---|---|
| clause added | **`§32`** (`§32.1`–`§32.5`) |
| corrected UPHILL | `VR3-R2`'s *"UNGUARDED"* — all four **do** refuse an empty glob; its glob path is transcribed wrong; the real defect is the **lexical sort** |
| severity ruled | **`LATENT`** — measured single-segment everywhere on this box, so no recorded number moved; trigger is a crashed-and-resumed run, in the **false-favourable** direction |
| repair route | **NEW registration only — all four are FROZEN and none may be edited** (`§31.3`) |
| carried `UNMEASURED` | **VMFLGPU001-R2's segmentation** — unreadable from this box, and it is the one favourable-direction verdict of the four |
| struck | `§29.5`'s **45 of 49**, unpinned and unreproducible; ratio preserved, pair struck |
| found en route | VMFL024's printed targets are `r/R` to **2.78e-17** — the analytic asymptote, not experimental points |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · credentials | **0** · solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.28, 2026-09-03 — **§33: `u_read` DOES NOT TRANSFER BETWEEN PLATES, AND MY OWN LANE BRIEF INSTRUCTED A LANE TO TRANSFER IT · CODE-TO-CODE REFERENCES ARE RULED, AND THE DISTINCTION IS INDEPENDENCE, NOT NUMERICAL-VS-ANALYTICAL**

### §33.1 ⚠ `u_read` IS PER-PLATE AND MY BRIEF WAS WRONG — CAUGHT BY THE LANE, NOT BY ME

Register row #56 records the R2 calibration's **`VALUE u_read = 0.00505051 y-data`**. That
number is correct **as the calibration's output on its synthetic plate format**. **My lane
brief then instructed that it be folded into VMFL008's band. That instruction was wrong and
would have been a charter violation** — `§28.6` and the instrument's own frozen bytes at
`digitize_calibrate.py:79-81` state that **`u_read` is PER-TARGET-FORMAT and is RE-DERIVED PER
CASE; it does not transfer to another by assertion.**

**The lane refused the instruction and showed the arithmetic, which is the part that makes it
undeniable:** inverting the pixel floor over the 495-px interior box, `0.00505051 × 495 =
2.5000` — **the number is one pixel on a plate whose y-axis spans 2.5 units.** It is a
**format constant of a plate that is not VMFL008's**, and it carries no information whatever
about how large a swirl velocity is.

> **RULED — `§33.1`: WHAT TRANSFERS BETWEEN PLATES IS THE READER'S ERROR IN PIXELS, WHICH IS
> FORMAT-INDEPENDENT. WHAT NEVER TRANSFERS IS `u_read` IN DATA UNITS.** The portable
> quantities are `term_A = 0.135594 px`, `p95 = 0.200851 px`, `MAX = 0.220671 px`,
> half-spread `0.003465 px`, floor `1.000000 px`. Per case, `u_read = S_y / 495` in that
> case's own units, where `S_y` is the target plate's axis span — **an answer-blind format
> datum**. *(And the brief's loose "nearly 5×" is properly `1.000/0.220671 = 4.5316×`, which
> is exactly why `§29.3` leaves `rms` admissible for VALUE and compels `max` for POSITION.)*

**Recorded against me, and it is the second time in this session a lane has corrected my
brief** — the first was the superseded VMFL046 cost arithmetic. **Both times the lane checked
the figure it was handed instead of building on it, which is the only reason neither reached a
frozen document.** A supervisor's brief is not evidence, and a lane that treats it as evidence
is not doing the job.

### §33.2 CODE-TO-CODE REFERENCES — RULED, AND THE LINE IS INDEPENDENCE

Two cases raised this in one session and were being read inconsistently: **VMFL035**, whose
reference is **Ansys's own density-based solver**, was read as capped at `GATE REACHED` and
never a credential; **VMFL008**, whose reference is **Michelsen (AFM 86-05, DTU, 1986)**, was
read as `PASS`-capable. **Both are "code-to-code". The readings differ, so the distinction
must be stated or one of them is wrong.**

> **RULED — `§33.2`: THE CAP TURNS ON INDEPENDENCE OF THE REFERENCE, NOT ON WHETHER IT IS
> NUMERICAL.** This charter's standing test is **sameness of model, never exactness of
> algebra** (Amendment 1.6), so a numerical reference is not disqualified merely for being
> numerical.
> - **A reference produced by the CODE UNDER COMPARISON, or by its vendor, is CIRCULAR** and
>   caps the case at **`GATE REACHED`**. Agreeing with Ansys's own solver tells us that two
>   runs of one vendor's code agree. **VMFL035 stays capped.**
> - **A reference produced INDEPENDENTLY — a third party, a different code, a different
>   decade — is a legitimate CODE-VERIFICATION comparator** and a `PASS` is available.
>   **VMFL008 is `PASS`-capable**, its reference being a 1986 DTU solution owing nothing to
>   Fluent or to this lab.

> **BUT THE CREDENTIAL'S SCOPE IS NARROWER THAN THE WORD `PASS` SUGGESTS, AND THE ROW MUST SAY
> SO ON ITS FACE.** A `PASS` against Michelsen certifies **agreement with an independent
> numerical solution of the same equations**. It is **NOT** validation against nature, and it
> is **NOT** verification against exact algebra. If Michelsen is wrong, we agree with him and
> both are wrong — **a shared-error mode that an analytical reference does not have.** Every
> code-to-code row carries that sentence in its reference cell. *(VMFL046's analytical
> reference, by contrast, was checkable against the manual's own printed number — which is why
> that corroboration was worth doing and why this class cannot offer its equivalent.)*

### §33.3 VMFL008 — WHAT IS SETTLED AND WHAT IS NOT

**Settled, answer-blind, and decided before any plate was opened:** `§25.6` does **not** cap
it. The cap needs `S_y >= 8.25 m/s` while swirl is bounded by the lid at `V_theta <= ΩR =
1.000 m/s`, so **the trigger would require a plotted axis 8.25× the entire physical range of
the quantity**; `u_read/tol = 0.040404` against a trigger of `0.333333`. **This is not a
forecast for the other ~44** — `§25.8` and the struck `§29.5` stand.

**Not settled, and named rather than assumed:** `S_y` and the meaning of the plate's "X"
coordinate are undetermined **by design** (opening the plate to size a band is `§25.2`'s
forbidden move); the swirl-component multiplier `SW = 1.35` is **unmeasured**, bounded
`[1.15, 1.50]`, and its measurement is **binding before the freeze** — outside that interval
the estimate and cap are re-filed. The comparator **refuses to grade** until its
`UREAD_JSON_SHA256` is filled at the freeze, which is the state I will diff under `§3` check 1.

| amendment | v1.28 |
|---|---|
| clause added | **`§33`** (`§33.1`–`§33.3`) |
| corrected, against the supervisor | **my lane brief instructed a cross-plate `u_read` transfer that `§28.6` forbids**; the lane refused it and showed `0.00505051 × 495 = 2.5000` |
| ruled | portable quantity is the reader's error **in pixels**; `u_read` in data units is **per-plate, re-derived, never transferred** |
| ruled | code-to-code caps on **INDEPENDENCE**: vendor's-own-code → `GATE REACHED` (VMFL035); independent third party → `PASS` available (VMFL008), **with the shared-error scope stated in the row** |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · credentials | **0** · solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.29, 2026-09-03 — **§34: VERIFICATION'S CONCATENATION POINT IS RIGHT AND SHARPER THAN OUR OWN; THEIR ILLUSTRATIVE PAIR IS WRONG, AND IT IS WRONG IN THE DIRECTION THAT WOULD MAKE THE REPAIR'S TEST PASS BY CONSTRUCTION**

### §34.1 ACCEPTED — CONCATENATION, NOT MERELY SELECTION

Verification accepted `§32` on every count and added one finding. **Their addition is correct
and improves on our own characterisation:** `§32.1` described the lexical sort as taking *"a
tail that is not the latest samples"*. **Their reading is sharper — the reader CONCATENATES
two series in directory order**, so a second time-directory does not merely mis-select, it
**interleaves two histories into one sequence that never existed.** Adopted; `§32.1`'s
"selects a wrong tail" is the weaker statement of the same defect.

### §34.2 ⚠ BUT THE PAIR THEY ILLUSTRATE IT WITH DOES NOT BREAK — VERIFIED AT SOURCE

Their example is *"`0.1` before `0.05`"*. **Measured:** `sorted(['0.1','0.05'])` returns
**`['0.05','0.1']`** — which **is** the correct numeric order. **Lexical sort does not
misorder that pair, or any decimal pair sharing a prefix**: `['0.5','0.45']` → OK,
`['0.9','0.10']` → OK.

**Lexical order breaks on INTEGER-LIKE names OF DIFFERING DIGIT COUNT**, and only there:
`['0','200','1000']` → `['0','1000','200']` **BREAKS**; `['9','10']` → `['10','9']`
**BREAKS**; `['100','20','3']` → `['100','20','3']` **BREAKS**.

**And that is precisely the regime VMFL001 is in.** Its `controlDict` sets `deltaT 1`,
`endTime 3000`, `writeControl timeStep`, `writeInterval 3000` — **integer time-directory
names**. A resumed run writing `3000` then `12000` misorders; one writing `3000` then `6000`
(equal digit count) does not.

> **WHY THIS IS WORTH CORRECTING RATHER THAN LETTING PASS OUT OF RECIPROCITY.** A repair
> designed against the decimal example would be **tested with decimal directory names — which
> never misorder — and would PASS while the real integer hazard survived untouched.** That is
> a control that passes **by construction on the wrong specimen**, which is the exact failure
> class this week has been spent on, and it would have been introduced by the repair meant to
> close it. **`§32.1`'s drafted `--selftest` already plants `{"0","200","1000"}`** — integer,
> differing digit count — **and is therefore the correct specimen. It stays as drafted, and
> any repair registration must use integer names of differing digit count, never decimals.**

**Stated plainly about the incentive:** this correction runs back to a team that had just
accepted ours in full and commended us in the same message. **That is exactly when a check
gets skipped**, and it is why it was run.

### §34.3 THE `§28.4` CARRY, AND WHAT IT DOES NOT EARN

Verification recorded our `VMFLGPU001-R2` `UNMEASURED` carry as the first application by
another team of their `§28.4`, applied to our own favourable row. **Recorded, and it changes
nothing about that row:** VMFLGPU001-R2's segmentation is **still unread**, still `UNMEASURED`,
and still the one of the four carrying a favourable verdict. **A commendation for declaring a
gap is not a step toward closing it**, and no record of this team may cite `§34.3` as though
the quantity had since been measured. It is closed only by reading the remote instance.

| amendment | v1.29 |
|---|---|
| clause added | **`§34`** (`§34.1`–`§34.3`) |
| adopted from verification | **CONCATENATION**, not mere mis-selection — sharper than `§32.1`'s own wording |
| corrected back | their `"0.1 before 0.05"` **does not misorder**; the hazard is **integers of differing digit count**, which is VMFL001's actual regime (`deltaT 1`, integer time-dirs) |
| consequence | a repair tested on decimals would **pass by construction**; `§32.1`'s `{"0","200","1000"}` specimen stands and is **binding** on any repair registration |
| unchanged | VMFLGPU001-R2 stays **`UNMEASURED`** |
| gates · bands · caps · re-grades · credentials | **0 · 0 · 0 · 0 · 0** · solver compute **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.30, 2026-09-03 — **§35: A CONTROL THAT CANNOT FAIL IS NOT A CONTROL, AND I WROTE ONE INTO `§29.3` MYSELF · `§31`'s REINSTATEMENT CONDITION IS 8.004× BELOW ITS READER'S QUANTUM AND IS UNFALSIFIABLE AS WRITTEN · ONE ALARM OF MINE WITHDRAWN**

### §35.1 `§31`'s REINSTATEMENT CONDITION CANNOT BE RESOLVED BY ANY INSTRUMENT THIS TEAM OWNS

`§31` froze, in advance and correctly in spirit: a re-run's finest level must reach a
**measured shock plateau — final-window drift ≤ 6.25e-04 m** — before `VMFL046`'s
`GATE FAIL` may be reinstated. **The threshold is unresolvable by the frozen bytes it
would be applied to.**

- The centreline sampler is **`nPoints 400`, hard-coded in `system/controlDict` at EVERY
  level**, giving a uniform spacing of **5.002506e-03 m, identical at L1, L2 and L3**.
- `grade_vmfl046.py:251` locates the shock at the largest Mach drop between **adjacent
  samples** — it **snaps to a sample node**, so it can only ever return **0 or a multiple
  of 5.0e-03 m**. The frozen threshold is **8.004× below that quantum.**
- Measured on the real viscous L3 data with a faithful reimplementation of that frozen
  reader: final-window drift **exactly 0.0000e+00 m — which SATISFIES the condition.**
  The interpolating diagnostic (`diagnostic_shock_steadiness.py:82`, last downward
  `M = 1` crossing) reads **2.3265e-03 m** on the same bytes and **fails it by 3.72×.**

> **RULED — `§35.1`: A THRESHOLD IS NOT SPECIFIED UNTIL ITS READER IS SPECIFIED.** A
> threshold below its reader's quantum is not strict; it is **unfalsifiable**, and it fails
> in the direction that flatters whoever wrote it. **Binding from v1.30: every gate,
> plateau, band and reinstatement threshold registered in this territory NAMES ITS READER
> AND STATES THAT READER'S RESOLUTION, in the frozen bytes, at freeze time.** A threshold
> whose reader cannot resolve it is refused at the freeze, not discovered at grading.

**⚠ THE INCENTIVE IS DISCLOSED BECAUSE IT RUNS TOWARD US, and `§31.2` obliges it.** §31's
condition, if met, **reinstates a recorded `GATE FAIL` against this team**. Declaring it
unresolvable therefore **blocks a failure from returning** — an outcome in our favour
reached by a finding against our own clause. **NO READER IS SELECTED HERE.** Both readers
exist on disk, they straddle the threshold, and **choosing one now, knowing which answer
each gives, is precisely the gate-fitting this charter has refused four times.**

> **OPERATIVE: NO REINSTATEMENT MAY BE CLAIMED UNDER `§31` IN EITHER DIRECTION** until a
> reader is named by a party **not choosing with the answers in hand**. **ESCALATED to the
> chief and not self-applied** — ~~naming the reader alters a frozen condition~~ **⚠ WRONG, and ruled so at `VERIFICATION §2am.8`: naming the reader THE DOCUMENT ITSELF ALREADY USED is INTERPRETATION, not alteration. The escalation was right; this reason for it was not. See `§37.3`** — which
> `ESCALATION_CHARTER` reserves. `§31`'s demotion of row #54 is **untouched and stands**;
> only its reinstatement limb is suspended.

### §35.2 ⚠ `§29.3` SPECIFIED A CONTROL THAT CANNOT FAIL — AND I WROTE IT

`§29.3` ruled that term A must dominate the worst demonstrated per-plate error, and gave
as **the test** that *"the planted null passes **by construction**"*. **That sentence names
the defect and calls it the goal.** Verified by me in the frozen bytes of
`DIGITIZER/R2/digitize_calibrate_r2.py` (sha `e51518…bc3130`), not taken on a lane's report:

1. **`:88` IS AN ASSERTION THAT CANNOT FIRE.** `:84` sets `u_read = max(term_A,
   half_spread, pixel_floor)` and `:80` sets `term_A = mx` for `statistic == "max"`, so
   `u_read >= mx` holds **identically**; `:88` then refuses only if
   `not (u_read >= mx - 1e-15)`, which is **never true for any finite input the instrument
   generates**. Its own comment calls it *"a self-check, refuses if violated."*
2. **THE `POSITION` PLANT-NULL CANNOT REFUSE.** `control_render(0.0)` is a **re-render of
   calibration plate #0** (`:172-173, :180-182`) — a **member of the very population whose
   maximum defines `u_read`** — so `|null_err| <= mx <= u_read` holds identically. **All
   discrimination in that instrument rests on `PLANT-DETECT` alone.**
3. **`plant_null.passes_by_construction` IS SET AT `:106` FROM THE STATISTIC LABEL**
   (`statistic == "max"`), **never from measured membership.** Today the asserted value is
   correct by accident of construction; **a flag that asserts a property rather than
   measuring it is not evidence**, and repointing `control_render` at a held-out plate
   would leave the flag reading `true` while the property had gone.

> **RULED — `§35.2`: A PLANTED NULL MUST BE EVALUATED ON A HELD-OUT SPECIMEN, NEVER ON A
> MEMBER OF THE POPULATION THAT DEFINED THE TOLERANCE IT IS TESTED AGAINST.** `§29.3`'s
> requirement that term A dominate the **calibration set** is **correct and stands**; what
> is struck is its *test* — the null's passing proves nothing when passing is arithmetically
> guaranteed. **The null's job is to ask whether `u_read` covers a plate the calibration
> DID NOT SEE**, and only a held-out plate can be asked that. `§29.3` is marked in place.
>
> **AND THE GENERAL FORM, WHICH IS THE PART THAT TRAVELS: EVERY CONTROL IN THIS TERRITORY
> MUST BE SHOWN ABLE TO FAIL, BY PLANTING THE FAILURE — not shown to pass on good input.**
> `CLAUDE.md` rule 3 plants a value to prove a READER can see a non-zero; this is its
> mirror, and the lab has been running without it. A control demonstrated only on the
> favourable case is an untested control wearing a green light.

**Neither finding reaches `VALUE`, and that is stated so the disclosure is not read as
wider than it is.** `:88` is gated on `statistic == "max"` and `VALUE` is graded `rms`;
`VALUE`'s null is also a population member but passes because the **pixel floor genuinely
dominates** (`syn_max` 0.0011145 < floor 0.0050505), so it retains real power, and its
`passes_by_construction` correctly reads `false`. **`VMFL008` gates on `VALUE`.**

**These are FROZEN files and NONE IS EDITED** (`§31.3`). The repair is a **new
registration**; the disclosure lives where the number is read.

### §35.3 ⚠ AN ALARM OF MINE, RAISED HARD AND NOW WITHDRAWN

I put it to a lane that register **row #56**'s `PASS` might be a verdict with **no evidence
on disk** — this team's own recorded failure class (`L-444`) — reasoning that the R2
instrument crashed inside `print(json.dumps(rep, …))` at `:196`, so `json.dumps` raised
**before** `print` emitted and the report was never written; which would leave
`GRADE_R2.json` a lane's `verbose=False` re-execution with nothing frozen behind it.

**The premise is true of `:196` and IRRELEVANT.** The per-quantity blocks print at
`:108-111`, the header at `:174`, the axis negatives at `:194` and **both verdict words at
`:195`** — all **before** the crash. `GRADE_R2.out` carries both `u_read` values, every
term, and **both `PASS` verdicts**. And decisively: **the reconstruction ran
`verbose=False`, which emits nothing at all**, so that stdout **could only have come from
the frozen run.**

> **ROW #56's `PASS` IS NOT EVIDENCE-FREE AND THE ALARM IS WITHDRAWN.** What genuinely rests
> on the reconstruction alone is a set of **auxiliary** fields — `plant_detect.delta_3u`,
> `.recovered`, `.recovery_err`, `bias_ok`, and `passes_by_construction`. The last is
> **doubly weak** (reconstruction-only *and* asserted-not-measured, `§35.2`), which is worth
> knowing but is not what I alleged. **A disclosure that OVERSTATES a defect is still a
> wrong record** — this team's own words, `L-314` Addendum 3 — and this one would have been.

~~**Forward flag, on the record now rather than at the freeze:**~~ **⚠ REFUTED BY `§36.1` — THE R2 INSTRUMENT PERSISTS NOTHING (`json` occurs only at its `import` and one `print`); it CANNOT produce this artifact and D5 is a NEW instrument. The row-#56 withdrawal above STANDS; only this flag falls.** `D5` will produce VMFL008's
per-case artifact **through this same R2 code path**, so it will hit the same `:196` crash
and face the identical provenance question. Its load-bearing values will be corroborable
from pre-crash stdout; its JSON-only fields will not.

### §35.4 VMFL008 IS `NOT FREEZE-READY`, AND THE CAMPAIGN'S CEILING IS FOUR CASES, NOT FORTY-FIVE

**`NOT FREEZE-READY`.** Binding blocker: **`D5` — VMFL008's OWN per-case `VALUE`
calibration, never run** (`reference/` empty; `UREAD_JSON_SHA256 = ""` at
`grade_vmfl008.py:165`; the comparator **refuses, exit 2**, at `:204-217` rather than grade
against an unpinned instrument — **verified in the code by me**). Co-binding: **`D6`, `SW`
unmeasured**. `D1`–`D4` open. **The digitizer is NOT the blocker** — row #56 is `PASS` on
both quantities and the R1 `NOT A RESULT` is superseded. **Cost reconciles CLEANLY under
`§26.3`: filed 16.53 vs its own method's 16.5312, ratio 1.0000**, against VMFL046's
1.66×/3.17× miss.

**Three errors in my own lane brief, corrected by the lane and recorded here:** `SW` is the
**swirl-component COST multiplier**, not a shockwave (a Re = 1800 laminar rotating cavity
has no shock — contamination from VMFL046); the digitizer's `NOT A RESULT` framing was too
coarse; and I pointed the lane only as far as `§27` of a charter that runs to `§34`.

**THE CEILING, MEASURED.** The printed-scalar **never-run** pool — the only pool gradeable
without the digitizer — is exactly **`VMFL024`, `VMFL034`, `VMFL072`, `VMFRT005`**. It is
**soft downward**: VMFL024 is capped at `GATE REACHED` on two grounds and `§32.3` showed its
"experimental" targets are the analytic rigid-body asymptote to **2.78e-17**; `VMFRT005` is
a **Forte combustion** case this box's solvers may not reproduce at all. **Honest count of
genuinely useful non-digitizer cases: about two.** Recorded as a **dated finding with its
method stated**, not as charter prose — `§32.4` established that a count of remaining work
does not belong in a clause at all, because "remaining" moves with every run.

| amendment | v1.30 |
|---|---|
| clause added | **`§35`** (`§35.1`–`§35.4`) |
| marked in place | `§29.3`'s *"the planted null passes by construction"* — struck, pointer to `§35.2`; `§32.5`'s `L-465` corrected to `L-477` at `7e14c5b9` |
| ruled | a threshold **names its reader and that reader's resolution** in the frozen bytes, at freeze time |
| ruled | a planted null is evaluated on a **HELD-OUT specimen**; **every control must be shown able to FAIL, by planting the failure** |
| suspended | **`§31`'s reinstatement limb** — unresolvable as written; **no reinstatement claimable in either direction**; ESCALATED, incentive disclosed as running toward us |
| withdrawn | my `L-444` alarm against **row #56** — its `PASS` **is** backed by frozen-run stdout |
| verdict recorded | **VMFL008 `NOT FREEZE-READY`**, binding blocker `D5` |
| records landed | **`N-AV16`**, **`L-477`** (`7e14c5b9`); FAMILY INDEX repaired (`f2aad5af`) |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · credentials | **0** · register bytes | **0** |
| solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.31, 2026-09-03 — **§36: `§35.3`'s FORWARD FLAG IS REFUTED IN THE SAME SESSION THAT WROTE IT — THE R2 INSTRUMENT PERSISTS NOTHING AND CANNOT PRODUCE D5's ARTIFACT AT ALL · D5 MAY NOT RUN UNDER VMFL008's AUTHORITY · `SW` IS NOT A MEASURABLE QUANTITY · AND A REAL CHARTER GAP IS NAMED RATHER THAN PAPERED**

### §36.1 ⚠ `§35.3`'s FORWARD FLAG IS WRONG, AND I WROTE IT NINETY MINUTES AGO

`§35.3` closed with: *"`D5` will produce VMFL008's per-case artifact **through this same R2
code path**, so it will hit the same `:196` crash and face the identical provenance
question."* **Both halves are false, and the second is false because the first is.**

- **THE R2 INSTRUMENT PERSISTS NOTHING.** `json` occurs at exactly two lines of
  `DIGITIZER/R2/digitize_calibrate_r2.py` — the `import` at `:42` and the
  `print(json.dumps(...))` at `:196`. **There is no `open(...,"w")` and no `json.dump`
  anywhere in the file**; `__main__` (`:273-281`) writes only PNGs. The frozen R1 file is
  the same (`digitize_calibrate.py:519` is also a `print`). **No code path in either frozen
  instrument can produce `reference/UREAD_VMFL008.json`.**
- **AND IT IS HARD-WIRED TO A PLATE THAT IS NOT VMFL008's.** `calibrate_r2:161` calls
  `dc.default_spec()`, fixed at `y_range = (0.0, 2.5)` (`digitize_calibrate.py:417-422`),
  and builds VALUE on the single frozen abscissa `dc.X_STATION = 0.517` (`:428`). Running
  it reproduces **the R2 plate's `S_y = 2.5` format constant** — the very number `§33.1`
  ruled non-transferable — at one station where VMFL008 gates at nine.

> **THE PART THAT IS WORST IS THAT THIS TEAM ALREADY KNEW.** `DIGITIZER/R2/RESULTS.md:60-62`
> records *"`GRADE_R2.json` is a **reconstruction** by the lane … not the CLI's own
> emission"*, and `:52-55` had already assigned the encoder fix to *"the **first per-case
> registration's instrument**"*. **I wrote `§35.3`'s forward flag without reading our own
> results record**, and it drifted the plan off a route already chosen and written down.
> `§35.3`'s **withdrawal of the row-#56 alarm stands and is unaffected** — that rests on
> `GRADE_R2.out`'s pre-crash stdout, which I verified. **Only the forward flag falls.**
> Marked in place at `§35.3` per `§30.3`, in this commit.

**D5 IS A NEW PER-CASE INSTRUMENT, NOT A RE-RUN.** It imports both frozen files **read-only
with their hashes asserted** — as R2 already imports R1 at `:152-160` — and edits neither
(rule 6, `§31.3`).

### §36.2 RULED — D5 MAY NOT RUN UNDER VMFL008's AUTHORITY, AND NEEDS ITS OWN FREEZE

I asked whether pre-freeze D5/D6 compute is legitimate **and named "it needs its own
pre-registration first" as an acceptable answer in advance**, so that the lane could not
read my expectation off the shape of the question. **That is the answer, and the authority
is quoted rather than assumed:**

- **Clause B does not reach D5 on any limb** (`§5`): the smoke is *"**After** the
  pre-registration is committed and **BEFORE** the graded run starts … ONE timestep (or one
  iteration) on the COARSEST mesh"*, and *"is never the graded artifact and **is never cited
  by a record**."* D5 is not a timestep, is not on a mesh, is not after a commit — **and its
  output IS cited, by the frozen bytes at `grade_vmfl008.py:165`.**
- **`§25.7`:** *"the instrument is built and calibrated as its **own pre-registered, costed
  task**, and its calibration is a `PASS`/`GATE FAIL`/`NOT A RESULT` of its own."*
- **`§28.8`:** *"`--calibrate` is compute the freeze governs and has **not** been run."*
- **The frozen bytes instruct it themselves** (`digitize_calibrate_r2.py:37-38`): *"do NOT
  run `--calibrate` (it produces the committed `u_read`, **which waits for the freeze**)."*
- **Precedent, twice:** `DIGITIZER` froze at `0fab170f` before `--calibrate`; `DIGITIZER/R2`
  froze at `5714f2c7` before `--calibrate`.

> **RULED — `§36.2`: D5 AND D6 RUN UNDER ONE PRE-REGISTRATION OF THEIR OWN,
> `cases/ansys_verification/VMFL008/D5D6_PREREGISTRATION.md`, FROZEN BY THE SUPERVISOR'S
> `§3` CHECK 4 BEFORE EITHER RUNS.** It carries the answer-blind format determinations
> (so `S_y` is frozen **before** D5 runs — `§25.2` point 2's literal demand), the held-out
> design, the planted-failure obligations, both estimates and both caps, and the
> instrument's own verdict per `§25.7`. **Two freezes, in order: D5D6 first, VMFL008's own
> second, once the artifact sha can be written into `grade_vmfl008.py:165`.**

**The consequence is stated plainly rather than softened: this team does NOT launch at the
~03:48Z window as the chief's disposition anticipated.** A freeze must land first. **An idle
box is a failure; a case that computes a committed number before freezing it is a worse
one**, and `§26.5` already ruled which way that conflict resolves.

### §36.3 A REAL GAP IN THIS CHARTER, NAMED AND NOT PAPERED

`§33.3` and `§11.2` make D6's measurement **binding before the freeze** — it sets the
**cap**, and "cap" is in `§11.2`'s enumerated list. `§26.3` demands the input **pre-freeze**.
**But Clause B, the only pre-flight authority in this charter, is positioned POST-freeze and
forbids its output being cited by any record.** So the charter simultaneously requires a
pre-freeze measurement and provides no clause under which one may run.

> **`§36.2`'s own-pre-registration route CLOSES the gap for this case and does NOT repeal
> it.** The general defect stands recorded and unrepaired: **a charter that mandates a
> measurement it authorises no mechanism to take.** Naming it is the point; a convenient
> reading of Clause B would have hidden it.

### §36.4 ⚠ `SW` IS NOT A MEASURABLE QUANTITY — RETIRED, AND ITS INTERVAL DOES NOT SURVIVE THE RENAME

`§33.3` and `PREREGISTRATION.md:425-426` define `SW` as *"the cost of solving **three**
momentum components (swirl) instead of **two**."* **That counterfactual does not exist.**
`simpleFoam` solves a 3-component `volVectorField U` unconditionally — there is no
2-component mode — and **in this cavity the swirl is the only momentum source**, so
suppressing it leaves no flow at all: the "2-component" arm converges instantly on a zero
field, and the ratio of a real solve to a null solve is an artifact, not a multiplier.

What `§7.4`'s stated procedure actually computes is an **aggregate rate ratio** folding in
mesh topology (5° sector with `cyclic` patches vs the datum's), the closed domain and its
pressure reference cell, cell aspect ratios and pressure-solver sweep counts.

> **RULED — `§36.4`: `SW` IS RETIRED AND REPLACED BY `RATE_RATIO`** — VMFL008-L1's directly
> measured `s/(cell·iteration)` over the datum's `1.0000e-06`. This **removes the only
> unmeasured multiplier in `§7`** and substitutes a measurement of the actual case, so
> `§26.3` is better served, not worse. **Legal because VMFL008 has no run directory and no
> compute has been spent** — before first compute, amendments are legal and must state the
> condition and how it was checked (`CLAUDE.md` rule 2): *checked by the absence of any run
> root for VMFL008 under `verification/runs/ansys_verification/`, and by both case files
> being untracked.*
>
> **AND THE INTERVAL DOES NOT COME ALONG FOR FREE.** `[1.15, 1.50]` was defended as a
> **swirl-component** range; **an aggregate rate ratio does not inherit that defence.**
> The interval must be **RE-DERIVED AND RE-DEFENDED on aggregate-ratio grounds in the D5D6
> pre-registration, or it is not a registered decision rule at all.** Keeping the numbers
> and swapping the quantity beneath them is exactly the move this charter refuses.

### §36.5 THE COMPARATOR IS STILL AN UNTRACKED DRAFT, SO TWO DEFECTS ARE REPAIRABLE **NOW** AND NEVER AGAIN

`grade_vmfl008.py:221-222` requires **eight** top-level keys (`dim`, `units`, `u_read`,
`statistic`, `verdict`, `terms`, `plate_interior_px_h`, `y_span_data_units`) — **my brief
said four.** Two defects found in that check:

1. **`units` is presence-checked and NEVER value-checked.** An artifact declaring
   `"units": "ft/s"` passes `_load_uread` intact. `dim` is checked at `:225`; `units` is
   checked nowhere. **`§28.2` requires every term computed in the quantity's own units —
   this is the guard for that clause, and it is absent.**
2. **`terms` sub-keys are dereferenced without being in the presence loop** —
   `t["term_A"]`/`t["half_spread"]` at `:246`, `t["pixel_floor"]` at `:250`, `t["max"]` at
   `:257`. A missing one raises `KeyError` → traceback → **exit 1**, not `refuse` → **exit
   2**. It fails loudly **wearing the wrong exit code**, and a launcher that distinguishes
   refusal from crash misclassifies it.

> **RULED: both are repaired BEFORE the freeze, under the supervisor's `§3` check 1 read of
> the diff.** After the freeze neither may be touched (`§31.3`) and the wrong-exit-code path
> would be permanent. **A defect found while the bytes are still a draft and left there
> becomes a frozen defect by inaction**, and inaction is a choice this charter does not
> excuse.

### §36.6 TWO CONSTRUCTIONS RULED, BOTH BEFORE ANY PLATE IS OPENED

1. **`PLATE_INTERIOR_PX_H = 495` is a STATED, DEFENDED CHOICE or it is a latent refusal.**
   `grade_vmfl008.py:170` hard-codes it and `:232-235` refuses on mismatch; 495 is the **R2
   format's** interior height. If D3 finds Fig .08.3's aspect ratio is not 4:3, then
   *"matched to the target's format"* and *"same 495 px interior"* are **incompatible and the
   comparator refuses its own artifact** — yet `PREREGISTRATION.md:200-201` asserts both.
   **RULED: fixing the interior height and matching the data ranges is legitimate** (`§33.1`
   makes the reader's error format-independent **in pixels**) **but it must be written and
   defended in the frozen bytes, and D3 must report the measured aspect ratio before the
   freeze.** A threshold that depends on an unmeasured format is `§35.1`'s defect again.
2. **NINE STATIONS, ONE `u_read`, IS A `§33.1`-SHAPED TRANSFER — ACROSS ABSCISSAE INSTEAD OF
   ACROSS PLATES.** The gate reads at `r/R ∈ {0.1 … 0.9}` (`:125`) while `dc.ValueQuantity`
   is single-station; the local curve slope, and hence the value error from a one-pixel
   horizontal misread, differs station to station (`§28.5`). **RULED: D5 instantiates all
   nine stations on the same digitized read, takes the statistic over the POOLED per-plate
   error set, and reports the per-station breakdown beside it.** Measurement is a cheap
   interpolation, so this adds no image operations — **and it completes D4, whose
   steep-region determination becomes per-station and observable rather than a single
   yes/no.**

### §36.7 COST — FILED AT OR ABOVE ITS OWN METHOD, IN BOTH DIRECTIONS, AND THE CAPS ARE SEPARATE

Method: two already-recorded data available now — `DIGITIZER/R2/RESULTS.md:66` (the
authorised `--calibrate --n 24` measured **4.032 s = 0.0672 core-min** over ≈ 66
render-or-digitize operations → **0.061091 s/op**) and `§28.7`'s independently measured
**0.117 s/pair = 0.0585 s/op** — **4.4 % apart**, and the larger is used because it also
carries interpreter start-up that will not scale.

| | filed | its own method | ratio | cap | worst pessimistic arm |
|---|---|---|---|---|---|
| **D5** | **0.15** core-min | 0.146619 (144 ops) | **1.0231** | **0.45** | 61.1 % of cap |
| **D6** | **0.10** core-min | 0.079413 | **1.2592** | **0.30** | 45.2 % of cap |
| **total** | **0.25** core-min | — | — | **0.75, SEPARATE not pooled** | — |

**$0.00021 DERIVED, NOT MEASURED** ($0.0513/core-h, owner-stated; the box cannot read its
own billing). **Both filed figures sit ABOVE their own method's output** (1.02×, 1.26×) —
the direction `§27` showed VMFL046 got right only by accident — and **the D6 excess is
explained, not absorbed: its method's own multiplier is the quantity D6 exists to measure.**
**Caps are separate so a D5 overrun cannot kill D6.** And the asymmetry that makes a tight
cap safe *here* and does not generalise: **a cap-hit on D5 forfeits ~9 seconds; `§27.2`
showed a cap-hit on VMFL046 would have forfeited 21.9 core-min of already-spent L3 compute.
The cost of losing a run is not the cost of the run's estimate.**

**Two soft inputs named rather than buried:** the 144-op count is *a count of a design not
yet written*, not a measurement; and `blockMesh + checkMesh ≈ 2.0 s` is **assumed** and is
42 % of D6's filed estimate.

| amendment | v1.31 |
|---|---|
| clause added | **`§36`** (`§36.1`–`§36.7`) |
| marked in place | **`§35.3`'s forward flag** — struck, pointer to `§36.1`; `§35.3`'s withdrawal of the row-#56 alarm **stands** |
| refuted, against me | the R2 instrument **persists nothing** and is hard-wired to a foreign plate format; **our own `RESULTS.md` said so and I had not read it** |
| ruled | D5+D6 run under **their own pre-registration and freeze**; **no launch at the ~03:48Z window** |
| named, unrepaired | a **charter gap** — a pre-freeze measurement mandated with no clause authorising it |
| retired | **`SW`** → **`RATE_RATIO`**; **the `[1.15, 1.50]` interval must be RE-DEFENDED or it is not a registered rule** |
| repaired before freeze | `grade_vmfl008.py` — `units` never value-checked; `terms` sub-keys `KeyError`→**exit 1** instead of refuse→**exit 2** |
| gates | **0 moved** · bands | **0 moved** · caps | **0 moved** · re-grades | **0** · credentials | **0** |
| solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.32, 2026-09-03 — **§37: VERIFICATION'S `§2am` IS ADOPTED IN FULL — READ AT SOURCE, NOT FROM THE RELAY. THE SUSPENSION LIFTS AND THE RULING FAVOURS US; SO I RECORD THE TWO PARTS THAT DO NOT — A FINDING AGAINST `§31`'s FRAMING, AND A RE-RUN THIS TEAM NOW OWES.**

### §37.1 THE RULING, AND HOW IT WAS TAKEN

`VERIFICATION_CHARTER` **v1.57 §2am** (`d4a50b47`, 105 lines, verified to exist and to touch
that file alone). **Read at source, in full, not from the relay that announced it** — the
discipline `§31.1` set for the previous verification ruling, and the reason it matters is
visible here: **the relay carried the favourable disposition and neither of the two adverse
findings below.** A relayed ruling is a summary, and a summary of a ruling about one's own
conduct is the least trustworthy kind.

**DISPOSITION ADOPTED:** the reader `§31`'s condition means is the **INTERPOLATING** reader,
`diagnostic_shock_steadiness.py:82-95`. **`§35.1`'s suspension is LIFTED**; reinstatement may
be claimed under `§31` under that reader. Applied to existing L3 data: drift **2.3265e-03 m
> 6.25e-04 m → admissibility NOT MET → NO REINSTATEMENT TODAY.** **Row #54 stays
`NOT A RESULT`, untouched.** Gates, thresholds, bands, caps, labels: **0 moved** — the
condition is unchanged; only its reader is named.

**Three grounds, and I record that the strongest is the one I did not make.** Ground one is
textual (the demotion note defines *"final-window drift"* by filename at `:855`, above the
condition at `:881`). Ground three is the decisive one: `nPoints 400` gives the snapping
reader a quantum of 5.0025e-03 m, so **its output set is `{0} ∪ {k·5.0025e-03}` and it has
NO output in `(0, 6.25e-04]` at all** — a **binary indicator** for which *every* threshold
across a 4,000-fold range yields byte-identical verdicts. **Under that reader the frozen
number recorded NOTHING, and rule 2 does not permit a frozen number to be construed as
having recorded nothing.** I had measured the 8.004× ratio and stopped at *"unresolvable"*;
**verification carried the same arithmetic one step further and got a ruling out of it.**

### §37.2 ⚠ THE FINDING AGAINST `§31`'s FRAMING — ADOPTED, AND THE RELAY DID NOT CARRY IT

`§2am.7` establishes an ordering I did not put in `§31`:

| when (UTC) | what |
|---|---|
| 2026-09-02 23:51–23:52 | the L3 samples both readings consume are **written** |
| 2026-09-03 18:15:25 | the audit artifact **printing the interpolated drift, 3.722 % of band** |
| 2026-09-03 **18:28:58** | `c53a1a67` — **the condition frozen** at 1 % of band |

**The condition was frozen 18 h 36 min after the data existed and 13 min 33 s after the
artifact printing that data's answer.** `§31`'s claim — *"frozen before any such run
exists"* — is **true as written** (no re-run root existed) **and is a far narrower claim
than "frozen before the data that could answer it".**

Verification ruled it **does not defeat the condition**, on the `§2d.7` direction analysis:
`6.25e-04` is **1 % of the 0.0625 m band** — a principled round fraction, not a value
reverse-engineered from 3.722 % — and **a stricter admissibility bar forecloses this team's
BEST outcome as thoroughly as its worst**, since it blocks the `GATE FAIL` returning *and*
blocks the case ever becoming a live `PASS` candidate. **A team fitting a gate to its own
advantage sets the bar loose and argues the second limb.**

> **BUT THE HAZARD IS ADOPTED, NOT BANKED:** *"a threshold frozen after its data existed
> carries less evidentiary weight than one frozen before, and `§31`'s wording invites a
> reader to think otherwise."* **That is a finding against my drafting and it is marked in
> place at `§31`'s own table row**, where a reader meets the claim. **RULED for this
> territory: a freeze claim states what it was frozen BEFORE — the run, the data, or the
> reading — and never leaves a reader to supply the most flattering of the three.**

### §37.3 ⚠ MY STATED REASON FOR ESCALATING WAS WRONG, THOUGH ESCALATING WAS RIGHT

`§35.1` escalated because *"naming the reader alters a frozen condition, which
`ESCALATION_CHARTER` reserves."* `§2am.8`: *"They were right to escalate and they are wrong
that this alters it."*

> **ADOPTED: naming the reader THE DOCUMENT ITSELF ALREADY USED, for a term THE DOCUMENT
> ITSELF ALREADY DEFINED, is INTERPRETATION and is available to a cross-team auditor.
> SELECTING A READER THE DOCUMENT NEVER USED WOULD BE ALTERATION and goes to Sanaa.**

**Marked in place at `§35.1`.** The distinction is worth more than the correction: I had
collapsed *"I must not decide this"* into *"this cannot be decided"*, and **those are
different claims — the first is about my conflict, the second about the document.** My
conflict was real and disqualifying; the document was never silent. **`§35.1`'s general rule
— every threshold names its reader and states that reader's resolution — is ENDORSED by
verification for this territory and stands unchanged.** Its lab-wide generalisation was
**DECLINED**, and correctly: *a met precondition permits a clause, it does not compel one.*

### §37.4 THE ANTI-SHELTER CLAUSE — A RE-RUN THIS TEAM OWES, ALSO ABSENT FROM THE RELAY

`§2am.10` declines to leave the outcome comfortable, and it is binding on us:

> *"A CASE THAT CANNOT BE RESOLVED TODAY IS NOT A CASE THAT IS CLOSED. `NOT A RESULT` is a
> statement that the question is OPEN, never that it is settled, and it may not be cited as
> an absence of failure. **The obligation to re-run VMFL046 under a registration whose
> finest level reaches a measured plateau SURVIVES this ruling and is owed by
> ansys-verification.**"*

**ACCEPTED AS A STANDING OBLIGATION OF THIS TEAM, entered on the board as a rung without a
verdict.** VMFL046 is **`PENDING A RUN`** — not closed, not settled, and **no record of this
team may cite row #54's `NOT A RESULT` as an absence of failure.** The condition is **live
and reachable**: a re-run driven to a measured plateau can meet it, and if its settled
`x_shock` then misses 1.250 by more than 5 %, **the `GATE FAIL` returns.** *We do not predict
which way it falls: settled L1 (+1.73 %) and L2 (−4.06 %) still bracket the threshold.*

**AND THE REOPENING CONDITION, RECORDED SO IT CANNOT BE FITTED LATER:** *"if a
drift-computing reader is ever brought INSIDE a frozen grading path for this family,
`§2am.3`'s textual ground yields to it"* — rule 2 prefers an instrument inside the grading
path to one outside it. **This bears directly on `§35.1`'s own repair**, which would put a
drift limb on the gated quantity inside future frozen comparators: **doing that is right,
and it will move the interpretive ground under `§31`.** Named now, in advance, by us.

*(One immaterial discrepancy, recorded because unrecorded discrepancies compound: `§2am`'s
section heading reads "TWENTY LINES ABOVE" while its body and the relay both read
"twenty-six". The body's figure matches the cited line numbers `:855` and `:881`. Nothing
turns on it.)*

| amendment | v1.32 |
|---|---|
| clause added | **`§37`** (`§37.1`–`§37.4`) |
| adopted | `VERIFICATION` **v1.57 `§2am`** in full, **read at source** — the relay carried the favourable disposition and **neither adverse finding** |
| suspension | **`§35.1`'s LIFTED.** Reader named: **interpolating**, `diagnostic_shock_steadiness.py:82-95` |
| applied | drift **2.3265e-03 > 6.25e-04** → **admissibility NOT MET, NO REINSTATEMENT**; row #54 `NOT A RESULT`, **untouched** |
| marked in place, against me | `§31`'s *"frozen in advance"* (18 h 36 min after the data); `§35.1`'s *"alters a frozen condition"* (it is interpretation, not alteration) |
| ruled | a **freeze claim states what it was frozen BEFORE** — run, data, or reading — never leaving a reader to supply the most flattering |
| **OBLIGATION ACCEPTED** | **VMFL046 must be RE-RUN** to a measured plateau. **`PENDING A RUN`, not closed.** `NOT A RESULT` may **not** be cited as an absence of failure |
| endorsed | `§35.1`'s general rule, **for this territory**; lab-wide generalisation **declined** |
| gates · thresholds · bands · caps · labels · re-grades | **0 · 0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |

---

## Amendment — v1.33, 2026-09-04 — **§38: EIGHT OF `§36`'s CLAIMS ARE REFUTED BY THE LANE I SENT TO BUILD ON THEM, AND THE WORST OF THEM PUT AN 18 % READER BIAS INTO MY OWN REPLACEMENT FOR THE CLAUSE ABOUT UNNAMED READERS · VMFL072 IS FROZEN AND I FROZE A LAUNCHER THAT CANNOT RUN**

### §38.1 THE FREEZE, AND THE DEFECT I PUT INSIDE IT

**VMFL072 is FROZEN at `e8cbe305`** — `PREREGISTRATION.md` (`e1f522c7`), `compare_vmfl072.py`
(`f22b74b4`), `launch_vmfl072.sh` (`2fd2becc`), one commit, so the grading path is fixed there
(`§5.1`). This team's **first freeze from Sanaa's mandatory never-run pool.** `§3` check 4 was
taken personally: the `§0` conditions were checked, not asserted — no run root, zero VMFL072
matches under `verification/runs/`, no grading artifact — so the claim *frozen before the run,
before the data, and before the reading* is `§37.2`-compliant in all three limbs.

> **⚠ AND I FROZE A LAUNCHER THAT CANNOT RUN.** `launch_vmfl072.sh:66,68` copies
> `cases/ansys_verification/VMFL072/base/.` and executes `apply_level.sh`. **Neither exists.**
> The case directory held exactly the three frozen files. I read the launcher's *guards* — the
> freeze gate, the pre-existing-time-dir refusal, the `0/U` age-guard assertion — and ran
> `bash -n`, **which checks SYNTAX and never checks that a referenced path exists.** A launcher's
> **dependencies** are part of what a freeze must verify, and I verified its logic instead.
>
> **RULED — `§38.1`: a freeze checklist must include, as its own line, THAT EVERY PATH THE
> LAUNCHER READS OR EXECUTES EXISTS AT THE FREEZE COMMIT.** `§10` of VMFL072's own registration
> lists the comparator and the prereg and does not list the case inputs; VMFL024's `§14` blocker 2
> *does* name an incomplete case directory, so this team already knew the failure mode and did not
> generalise it into a checklist.
>
> **What is NOT damaged, stated so the defect is not inflated:** no gate, band, threshold, cap or
> label is affected; no compute occurred; the run root still does not exist. And the failure mode
> is **safe and loud** — `set -euo pipefail` makes the missing `cp -r` source abort before the
> solver is reached, so it cannot produce a wrong number, only no number. **No queue row was filed
> against it.** Case inputs are being built to the frozen specification, which is completion of a
> case, not an amendment to a frozen document.

### §38.2 `§36.5`'s TWO REPAIRS — READ AS A DIFF BY ME, ACCEPTED

`grade_vmfl008.py`, still untracked. `§36.5`'s line numbers were **all exact**. Repair (a) adds
`UREAD_UNITS = "m/s"` and refuses an artifact whose `units` differs; repair (b) adds
`UREAD_TERM_KEYS` with a presence loop and an `isinstance(t, dict)` check **before** the first
dereference, so a missing sub-key **refuses (exit 2)** instead of raising `KeyError` → exit 1.
**Neither touches a gate, band, threshold, cap or label. ACCEPTED under `§3` check 1** — read by
me in the file, not taken on the lane's report.

> **AND REPAIR (a) HAS MORE TEETH THAN `§36.5` KNEW.** The frozen instrument's own
> `ValueQuantity.units` is the **dimensionless placeholder `"y-data"`**
> (`digitize_calibrate.py:337`). So the guard does not merely exclude `"ft/s"` — **it refuses any
> D5 that reuses the frozen class verbatim**, and thereby converts an abstract clause into a
> binding design constraint on the instrument D5 must build. `§36.5` argued the guard was absent;
> it did not know the absent guard was load-bearing.

### §38.3 ⚠ THE REFUTATION THAT MATTERS MOST — `§36.4` NAMES NO READER, AND THE OBVIOUS ONE IS BIASED **+18 %** IN OUR FAVOUR

`§36.4` retired `SW` for `RATE_RATIO`, defined against the datum's `1.0000e-06`. **That datum is a
whole-run WALL rate.** Measured from the archived datum log, the `[200, 2000]` **CPU-time** window
rate is **`1.1805556e-06`** — **1.19701× the whole-run rate**, because early SIMPLE iterations cost
more. **A short-window D6 divided by `1.0000e-06` therefore reads `RATE_RATIO` about 18 % high
before any physics enters.**

> **THAT IS `§35.1`'s DEFECT, COMMITTED INSIDE MY OWN REPLACEMENT FOR THE CLAUSE `§35.1` WAS ABOUT
> — every threshold names its reader and that reader's resolution.** `§36.4` named a number and no
> reader, and the two readers available straddle it, exactly as `§31`'s two shock readers did.
> **AND THE DIRECTION IS THE DAMNING PART: the bias is ~18 %, nearly half the width of the retired
> `[1.15, 1.50]`, and it runs toward landing the measurement INSIDE that interval — for a reason
> that is an artifact of the reader.** A team that wanted its retired interval vindicated could not
> have chosen better. **RULED: a symmetric CPU-time reader on BOTH sides, its resolution stated
> (0.0019 arm B / 0.017 arm A against a 4.5-wide refusal band).** Adopted from the lane; I did not
> find this.

### §38.4 FIVE MORE OF MY CLAIMS, REFUTED AND CORRECTED IN PLACE

1. **`§36.4` attacked a counterfactual the registration never made.** I argued about suppressing
   swirl *in VMFL008*. `PREREGISTRATION.md:425-426` defines `SW` inside a `§7.2` that scales
   **VMFL011-R3's** rate — **the "two" is the DATUM's two, and that counterfactual is real and on
   disk**: the datum's `blockMeshDict.template` sets `frontAndBack { type empty; }`, and
   `fvMatrixSolve.C:163` reads `if (validComponents[cmpt] == -1) continue;`, so with `empty`
   patches the z-momentum component is **skipped entirely**. The datum solves two; VMFL008's
   cyclic sector solves three. **The ruling survives; my reasoning for it was wrong.**
2. **Two of `§36.4`'s four named channels are not differences at all.** VMFL011-R3 is *also* a
   closed pure-Neumann cavity (`0/p` all `zeroGradient`, `pRefCell 0`), so "the closed domain and
   its pressure reference cell" contributes nothing; "pressure-solver sweep counts" is a
   consequence of a free knob, not an intrinsic difference.
3. **`§36.4`'s headline claim is FALSE under `§36.7`'s own cheap arm.** Retiring `SW` does not
   *"remove the only unmeasured multiplier in `§7`"* — a windowed ratio applied to whole-run rates
   needs a **`SHAPE_FACTOR`**, measured for the datum (`0.835412`) and **unmeasured for VMFL008**.
   `SW` would be swapped for something equally unbacked. **Only a whole-run D6 delivers the state
   I claimed.**
4. **`§36.6` point 1 names the wrong datum.** `PLATE_INTERIOR_PX_H` depends on the interior
   **height in pixels**, not the aspect ratio, so fixing 495 *and* matching the aspect ratio is
   perfectly self-consistent and **the incompatibility I asserted does not exist.** The real defect
   is sharper and invisible from the aspect ratio: if the raster's interior height ≠ 495 at the
   frozen DPI, a floor calibrated at one raster resolution is applied to a read at another —
   `§33.1`'s error in a new dress. **D3 reports `H_INT_PX` and `PLATE_INTERIOR_PX_H` is set from
   it.**
5. **`§36.6` point 2's unqualified pooling is `§28.5`'s defect at the nine-station scale.** The
   gate is a **conjunction** over nine stations, and **a pooled RMS sits below the worst station's
   own RMS by construction** — so pooling alone would have understated the tolerance the gate is
   judged against. **RULED: `term_A = max(pooled, worst-of-nine)`**, pooling preserved as the
   reported population but not necessarily the binding number.
6. **`§36` never invokes `§20.3`.** Neither D6 arm obeys Clause B, so each is a **pre-freeze
   production run** and must be **declared as one with every revealed quantity named** —
   *"silence about a revealing smoke is the defect."* Declared.

### §38.5 RULED — D6 TAKES **ARM B**, AND VMFL008 ADOPTS VMFL011-R3's NUMERICS VERBATIM

**`§11.2` forbids a deferred cap, so the arm is chosen here, not left open.**

> **ARM B (whole-run), filed 0.55 core-min, cap 1.65 (method 0.451799, ratio 1.2174).** It costs
> **0.45 core-min more than arm A** and buys three things arm A cannot: it **removes
> `SHAPE_FACTOR`** rather than renaming `SW` into it (`§38.4` item 3); it **measures whether
> `endTime = 20000` is sufficient for the frozen plateau criterion** — an assumption adopted for
> *cost-datum validity* and nowhere shown adequate, where a non-plateauing L1 forfeits **16.53
> core-min**; and it makes the contention guard **sound**, since `ClockTime`'s integer-second
> resolution is weak on a 4 s run and adequate on a 27 s one. **Buying a measured answer to a
> 16.53 core-min risk for 0.45 core-min is not a close call.**

**`RATE_RATIO` carries a point value 1.30 and NO decision load, deliberately.** The enumerated
channel table behind `[1.00, 1.80]` **is exactly the move `§24.6` forbids** — *a sensitivity
argument over enumerated perturbations is not an upper bound on a total discrepancy.* **The cap is
set from the MEASURED value, always; a measurement outside the interval is a recorded finding, not
a re-file.** What *is* registered as a rule is a **refusal**: D6 refuses (exit 2) if
`RATE_RATIO ∉ [0.5, 5.0]` — a claim about the instrument, not about the answer.

**RULED (blocker B3): VMFL008 adopts VMFL011-R3's `fvSolution`/`fvSchemes` VERBATIM** — PCG/DIC
`relTol 0.01`, PBiCGStab/DILU `relTol 0.1`, `nNonOrthogonalCorrectors 3`, `consistent yes`,
relaxation 0.7/0.7, `bounded Gauss linear`. Without this the ratio is undefendable: **a
GAMG-vs-PCG choice moves it by more than the whole interval.** Same discipline `§7.1` already
applied to the stopping criterion.

### §38.6 THE HELD-OUT NULL, AND A LATENT GEOMETRY HAZARD IN VMFL008's OWN COMPARATOR

**The held-out null satisfies `§35.2`**: `CAL_IDX = range(0,24)` defines `u_read`;
`HELD_IDX = range(100,106)` is a **disjoint seed block, with disjointness asserted at run time and
refused if violated** — answering `§35.2`'s own complaint that a flag which asserts rather than
measures is not evidence. D5 refuses if `null_max > u_read`. **It can fail because
`null_max ≤ u_read` is a contingent claim about a population the tolerance never saw** — it fails
if the calibration family under-samples the shape space, or if `term_A` is an `rms` over a tailed
distribution, **which is the R1 failure exactly.** *Honest limit carried: for VALUE the floor
dominates by 4.53×, so this null is expected to pass with room; its power is real but modest.*
**Anti-gaming frozen: a refusal may not be answered by shrinking `N_HELD`, re-rolling the seed
block or widening `NULL_K`** — a held-out control with a re-drawable held-out set is a control that
cannot fail, one indirection further out.

> **⚠ CARRIED FORWARD AS A BLOCKER ON VMFL008's OWN FREEZE (C1): the comparator's frozen geometry
> PRESUMES D1's answer.** `STATIONS` are `r/R`, `X_SECTION = 0.6`, and `read_sample_file` maps the
> abscissa to `r` with `V_θ = U_y` at θ = 0. **If D1 finds `X` is the radial coordinate, the
> section at X = 0.6 m is an axial line at r = 0.6 and the abscissa is `z` — the comparator would
> be gating the wrong geometry entirely.** `§36.6` makes this argument about
> `PLATE_INTERIOR_PX_H` and does not make it about D1, where it has more force. **D5 is immune**
> (its nine stations are fractions of the plotted x-axis span, not physical `r/R`), so D5 does not
> serialise behind D1.

### §38.7 COST — THE RATE CONFIRMED, ONE BASIS REPLACED, TWO FIGURES OF MINE REFUTED

**Confirmed:** `4.032/66 = 0.06109091 s/op`; `0.117/2 = 0.0585`; **4.43 % apart**, larger used.
**Replaced:** `§36.7`'s **144-op count was soft and is now 119** on a written design (nine-station
measurement adds **zero** image ops, verifying `§36.6`'s claim); **filed 0.15 and cap 0.45 both
survive** on a shown method. *I could not reproduce 144 from any reading of `§36`.*
**Refuted, twice:** `blockMesh + checkMesh ≈ 2.0 s` **never had to stay assumed** — `log.checkMesh`
is **0.036 s** after `log.blockMesh` — and *"42 % of D6's filed estimate"* has **the wrong
referent**: `2.0/6.0 = 33.3 %` of the filed, `41.97 %` of its method's output. **Also
unreproducible: `§36.7`'s "61.1 %" and "45.2 % of cap" columns — no method is stated for either.**

| amendment | v1.33 |
|---|---|
| clause added | **`§38`** (`§38.1`–`§38.7`) |
| **frozen** | **VMFL072 at `e8cbe305`** — first freeze from the mandatory never-run pool |
| ⚠ against me | I froze a **launcher that cannot run**; `bash -n` checks syntax, never path existence |
| ruled | a freeze checklist must verify **every path the launcher reads or executes exists at the freeze commit** |
| accepted (`§3` check 1) | `grade_vmfl008.py`'s two `§36.5` repairs — read by me as a diff |
| ⚠ refuted, against me | **`§36.4` names no reader and the obvious one is +18 % biased TOWARD vindicating the interval I retired**; the `SW` counterfactual is the DATUM's; 2 of 4 channels are not differences; the "only unmeasured multiplier" claim is **false**; `§36.6` point 1 names the wrong datum; pooling alone understates the tolerance |
| ruled | **D6 arm B**; `RATE_RATIO` carries **no decision load** (`§24.6`); VMFL008 adopts **VMFL011-R3's numerics verbatim** |
| gates · thresholds · bands · caps · labels · re-grades | **0 · 0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| lines whose number changed above this section | **0** |
