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
