# Infrastructure and Standards Family Supervision Guidelines

Version 1.0, dated 2026-08-07. Issued by the standing Infrastructure/Standards
family supervisor under `docs/charters/SUPERVISION_CHARTER.md` v1.0, section 2.
The family: the sdk (chief_engineer modules, scripts, tests), the standards
documents (MESH, MONITOR, INNOVATION), the charters' enforcement code (agenda
rails, citation tier audit, self_audit, morning report), the keepalive and
resilience tooling, and the docket/proposals machinery.

Iterated the way the charters are: on incident, with a date, never weakened
without naming the decision that forced it.

## 1. Rules

### 1.1. Staging is by explicit path, and the family checks it

`ESCALATION_CHARTER.md` section 9.6 already forbids `git add -A`, `git add .`
and `git commit -a` on the shared tree. This family adds the check side:

- A commit touching sdk or standards files whose message does not describe
  every file in it is a record defect the family supervisor flags on sight.
- Enforcement idea, filed not built: a pre-commit hook that refuses a commit
  whose staged set spans more than one of {sdk, demo-output, models,
  docs} unless the message names each area. Until something mechanical
  exists, the check is the supervisor reading `git show --stat` on family
  commits, and this document says so rather than pretending.
- An agent that finds foreign hunks in a file it must commit stages its own
  hunks only (the split-patch precedent). Foreign hunks discovered in a
  family commit are reported to the chief with the commit hash, never
  quietly absorbed.

### 1.2. The suite is green before an sdk commit, and the count is stated

Any commit that touches `sdk/` runs the full suite first
(`python -m pytest tests/ -q` from `sdk/`), and the commit message or the
session record states the count. Baseline as of this document: **1153 passing
(1 was a stale pin, fixed this pass), 144 subtests**. A red suite is never
committed around: either the failure is fixed, or it is triaged as a finding
(a stale test pinning a moved contract is the recurring benign case, pattern
commit `44be9dd5`) and the fix to the test states which contract moved and
which commit moved it. A test weakened to pass without naming the contract
that moved is a rail-bypass, severity high.

### 1.3. The schema-rails pattern is the standard for new validations

Every new intake validation in family code follows the pattern P-1.1, P-1.4
and P-3.1 set in `sdk/chief_engineer/agenda.py`:

- **Refuse at intake, never rewrite.** A record that fails the rail is
  refused with a message naming the closed list it violated; it is never
  silently corrected into something its author did not file.
- **Grandfather by date.** New rules bind from a stated date
  (`SCHEMA_REQUIRED_FROM`); records created before it stand as filed and are
  never refused retroactively. The grandfather line is a migration boundary,
  not a security boundary, and the code says so where it is implemented.
- **A refusal is visible.** Anything refused or defaulted is recorded where
  a person can read it (`refused_cost_bases()`, `unscored_kinds()`,
  `refused_inbox()` from this pass). A filter nobody can see is a filter
  nobody can question.
- **Replay before adoption.** A rule that will fire on the lab's own work is
  replayed against the archive before it binds, with corpus, fire count,
  fatal count and motivating-case behaviour stated (the S12 pattern,
  `MONITOR_STANDARD.md` section 3.1; the S7 withdrawal is the reason).

### 1.4. Keepalive arming is session step zero

The first command of every working session in this family is
`bash scripts/session_keepalive.sh on`, and any session expecting long
unattended compute also arms `bash scripts/filming_keepalive.sh on <hours>`
(charter 9 OPS rule 3: hold the box twice). The supervisor verifies both at
the start of a pass with `status`, and treats a disarmed guard discovered
mid-campaign as an incident to triage, not a state to silently correct:
the 2026-07-30 mid-campaign power-off is the measured cost. Neither script
disables the auto-stop, which is the owner's cost control and stays.

### 1.5. The double-resume check

Before resuming any agent (charter 9 OPS rule 4): run
`pgrep -af 'claude --resume'`, look for fresh writes in the agent's own
files, and inventory containers. Resuming a live agent spawns a second
incarnation in the same tree. One resume per solve, and the resume message
carries the outcome the watcher already collected. A completion notice with
no result is the dead-agent tell, and the answer is reattach, not restart.

### 1.6. What escalates to the chief supervisor

Escalated on discovery, per the escalation charter, never settled inside the
family:

- **Suite regressions** that are not stale pins: any failure whose cause is
  a behaviour change in family code, or any failure in a measurement or
  grading path.
- **Docket corruption**: a docket that fails to parse, loses decisions,
  drops records silently, or carries records that bypass a declared
  invariant (the two `done`-without-`outcome` entries found this pass are
  the standing example).
- **Guard disarming**: either keepalive found off during an active session
  or campaign, the auto-stop pattern found not matching a running work
  class, or any change to auto-stop/keepalive semantics.
- **Anything touching leakage enforcement**: the closure challenge's
  test-blind rails, gate scripts, hash manifests, scoring-call machinery.
  No family-level edit to these lands without a chief-level read; scoring
  calls themselves are retained by the chief under the supervision charter
  section 4.
- **Cross-family surface changes**: any edit to agenda rails or morning
  report checks that changes what another family's filings are refused for.

## 2. Findings record, first personal-check pass (2026-08-07)

Recorded here before any fix was applied, per the supervision charter's
record-before-fixing discipline. Severities: high / medium / low / note.

### 2.1. Suite

1152 passed, 1 failed, 144 subtests at start of pass.
`test_mega_batch.py::test_research_programs_are_real_and_structured` pinned
the round-3 closure score (0.0676) after commit `07a7fe9e` moved the entry
of record to round 5 (0.0566, chief-authorized scoring call, pre-registered,
evidence in the commit). Stale pin, not a regression: severity low, fixed
this pass by moving the pin to the entry of record.

### 2.2. agenda.py rails (personal check, line-by-line)

- **A-1 (medium, fixed this pass): rail-trip on the NACA 0012 TMR drafter
  becomes a crash.** `draft_tmr_proposals` returned
  `[_draft_tmr_naca0012(bump)]` without the `None` guard its own flat-plate
  branch has; `_proposal` returns `None` on any style-rail violation, and
  `draft_all` then raises on `proposal["objective"]`. One rail-trip away
  from taking the whole docket refresh down. Fixed with a regression test.
- **A-2 (medium, fixed this pass): the `done`-requires-`outcome` invariant
  binds only in `set_status`.** An inbox file arriving with
  `status: "done"` and no `outcome` rode through intake, bypassing the
  module's declared invariant. Two such records already sit on the docket
  (`w4-decomposition-invariance-is-a-gate`,
  `w4-does-the-decomposition-defect-reach-other-cases`; both entered by
  direct docket edit, not through this reader, and both grandfathered by
  date). Fixed at intake for schema-bound records; the two grandfathered
  entries are escalated, not rewritten.
- **A-3 (medium, fixed this pass): inbox refusals were invisible.** 19 of
  56 inbox files were being silently skipped at intake, including two filed
  the same day (`s1-cbfs-field-inversion-run`,
  `s1-cbfs-objective-repair-and-reinversion`) that would never reach the
  docket and nothing anywhere said so. This contradicts the module's own
  stated principle (a filter nobody can see). Fixed: `refused_inbox()` now
  records every skipped file with its violations, same pattern as
  `refused_cost_bases()`. The refused files themselves belong to their
  authors' families and are reported upward, not edited here.
- **A-4 (note): the grandfather line is self-declared at the inbox.**
  `read_inbox` takes `created_at` from the file, so a new file claiming an
  old date evades the P-1.1/P-3.1/P-1.4 rails. The code already states the
  boundary is a migration boundary, not a security boundary; recorded here
  so the gap stays a known gap.
- **A-5 (note): `_REFUSED_COST_BASES` grows without bound.** Every docket
  refresh re-runs the drafters and appends duplicate refusal entries.
  Process-lifetime memory only; recorded, not fixed this pass.
- **A-6 (note): decision fields entered through `set_status` bypass the
  style rails.** `dismiss_reason`/`outcome` are `_clean`ed but not checked
  by `text_violations`. These are owner-entered fields, so refusal would be
  wrong; recorded for completeness.

### 2.3. Keepalive and auto-stop interaction (personal check, line-by-line)

- **K-1 (medium, fixed this pass): one bad sample permanently disarms the
  session hold.** The holder loop exited on the first sample where no
  session directory yielded a timestamp (`newest == 0`), so a transient
  `find` failure silently killed the guard with nothing re-arming it. Fixed:
  the holder now requires three consecutive empty samples before concluding
  the session is gone; the 24 h hard cap still bounds the worst case.
- **K-2 (medium, escalate): the 45-minute window can lose a quiet session
  at minute 75.** With no solver running and no session write for 45 min
  (a long Monitor wait, a fleet quiet between turns), the holder exits;
  auto-stop's marker then ages out 30 min later and the box powers off
  mid-session. The arithmetic: 45 + 30 = 75 min of pure silence. Whether
  STALE_MINUTES moves is a cost-control tradeoff and the owner's, so it is
  escalated with the numbers rather than changed.
- **K-3 (medium, escalate): the auto-stop busy pattern has work-class
  gaps.** `/usr/local/bin/auto-stop.sh` (root-owned, not editable from
  here) counts busy on a fixed pgrep list that omits, at least: `pisoFoam`,
  `foamRun`, `reconstructPar`, `decomposePar`, `checkMesh`, and anything
  under `Certonomous/scripts` (the literal it greps is `Certonomous/sdk`).
  A long reconstruction with both holds expired is indistinguishable from
  idle. Needs root to fix; escalated with the missing patterns.
- **K-4 (low): a recycled PID can fake an armed guard.** `running_pid`
  trusts the pidfile plus `kill -0`, so a PID reused by an unrelated
  process makes `on` report "already running" while nothing holds the box.
  Improbable; recorded.
- **K-5 (note): both-holds-expired during an active solve is covered** for
  every solver on the pgrep list, because auto-stop counts the solver
  itself busy. The exposure is only the K-3 work classes.

### 2.4. Docket blind-spot sweep

- `docket.json` parses clean: 235 proposals (98 done, 70 proposed, 54
  approved, 13 dismissed) after the negative-verdict review's thirteen
  landed at 22:10 UTC with five approvals; all thirteen pass the intake
  rails as they sit on the docket, and the slate's three (f5c inlet audit,
  Taylor-Green, double Mach reflection) pass and await the next refresh.
- **Orphaned claims (escalate): 2.** `w2-the-duct-zero-stated-as-a-
  structural-limit-with-a-falsifier` and
  `w3-qcr-constitutive-term-for-rank2-parity`, both claimed
  2026-08-05T16:20Z by `research-agent w3-qcr-rank2-parity (closure
  session)`, still `approved` with no release two days on; the round-5 QCR
  work that scored today overlaps the second's subject, so the claims may
  be satisfied-but-unreleased. Chief decides release or reassignment; the
  claims are another family's and are not edited here.
- **Done-without-outcome (escalate): 2**, named in A-2 above.

### 2.5. Standards version coherence

MESH v1.0 (2026-07-25), INNOVATION v1.0 (2026-07-25), MONITOR v1.3
(2026-08-02, S12 added, S7 withdrawn at v1.2). Every versioned citation
found in the charters matches: `PROPOSALS_OPEN.md` cites MONITOR section
3.1 (v1.3) and that section carries the S12 replay line;
`log_signatures.py` carries the S7 withdrawal consistently (detector
removed, withdrawal dated). No coherence defects found.

## Related

- `docs/charters/SUPERVISION_CHARTER.md`. The role, the four personal
  checks, what the chief retains.
- `docs/charters/ESCALATION_CHARTER.md`. Section 9 OPS (keepalives, resume
  discipline, pre-registration), section 9.6 (explicit-path staging).
- `docs/standards/MONITOR_STANDARD.md`. The S12 replay pattern section 1.3
  points new rules at.
- `sdk/chief_engineer/agenda.py`. The schema-rails implementation this
  document names as the pattern.
