# Infrastructure and Standards Family Supervision Guidelines

Version 1.15, dated 2026-08-10 (night). Adds 13.4: the evidence gating six
adopted monitor rules was selected by a filename accident, and correcting it
3x'd the corpus and reversed this family's own S6 refusal. Adds 13.5, the D4
warrant correction.

Version 1.14, dated 2026-08-10 (night). Adds section 13: a standard this
family owns claimed coverage nothing supplied, and the claim was built
entirely out of true sentences. Records the standards practice it earns.

Version 1.13, dated 2026-08-10 (night). Adds section 12: a FAIL-FALSE channel
inside the mesh gate itself -- `parse_check_log` called a crashed checkMesh
`clean` -- found by the Cases family and worse than reported. Adds the third
provenance constant.

Version 1.12, dated 2026-08-10 (night). Adds section 11: 105 meshes the
2026-08-08 audit called CERTIFIED carried the checkMesh log and none carried
the certificate, so the word named an artifact nobody had written. 95 minted
with a cell-count cross-check and a stated retrospective provenance; 10 refused
and reported, 7 of them because the audit's own cited log contradicts its own
verdict.

Version 1.11, dated 2026-08-10 (night). Adds 10.6: the retrospective the
declared-vs-observed rank fix earned. Has the channel ever fired? **No** --
zero mismatches, established with two independent recovery routes and a
planted positive control on each.

Version 1.10, dated 2026-08-10 (night). Adds 10.4, the declared-vs-observed
rank count in `launch_solve.sh` -- the tail of the section 10 work, and the
same defect on the same cost arithmetic -- and 10.5, a suite failure triaged
as a finding rather than committed around.

Version 1.9, dated 2026-08-10 (night). Adds section 10: a runner that
silently overrides a caller's declared resource limit is L-40 in the resource
dimension, and the container runner this family owns had two worse instances
than the one reported. Adds the runtime envelope, so a run records the limits
that actually BOUND it rather than the ones a document asked for.

Version 1.8, dated 2026-08-10 (night). Adds section 9, the cross-family
lesson-propagation sweep for L-41 to L-48 that strategy section 1 requires and
that eight lessons in two days had gone without. It found instances in every
family, including three in this family's own procedure documents and two in
the L-42 fix itself. Section 1.5 is corrected: it carried the resume ordering
L-41 names as WRONG for two days after the lesson landed, and the sweep found
it rather than its author.

Version 1.7, dated 2026-08-10 (night). Records the chief's two rulings on
P-4.2 in section 1.8 — evidence is judged by WHEN IT WAS CAPTURED, not when it
was written, and a claimed limit is refused unless measured (L-48) — adds the
third worked example to 5.1, which makes that a pattern of three rather than
an anecdote, and closes the pass with the queue assessment in section 8.

Version 1.6, dated 2026-08-10 (night). Adds section 7, two items routed in
from the Cases family: the echo was recording SOLUTIONS as levers (24.6 MB of
a 25.2 MB B-52 log, 97.8%), now 8.5 kB with every lever verbatim and the
replicate-equality gate closed by the same fix; and the five "shell string"
solver launches turn out not to be shell strings at all, so the permanent
unverifiable marking they were offered is refused on measurement.

Version 1.5, dated 2026-08-10 (night). Adds section 1.9 — evidence has to
survive the next run — and section 6, the L-42 enforcement pass: every launch
path in the shared runner now archives an existing log under a UTC-stamped
superseded name instead of truncating or unlinking it. Adds the worked example
in section 5.1 the chief ordered recorded: **a fix that creates the artifact a
check tests for disables the check**, from a near-miss inside this family's own
work. States the latent-finding rule in section 3.3.

Version 1.4, dated 2026-08-10 (night). Records P-4.1 as approved — option C+D
landed, option B (full consolidation) REFUSED and the refusal adopted as
policy — in section 5, and closes the six false-negative launch paths section
3.3 left open. Family code now has one launcher definition and one place that
decides what counts as a solve. A latent over-fire in 3.3 went live during the
work and was closed with it: a solver binary running `-postProcess` is not a
solve.

Version 1.3, dated 2026-08-10 (night). Closes the one false-POSITIVE channel
v1.2's sweep found: `launch_solve.sh` minted its lever echo from a
caller-supplied `--case` while the command ran under `setsid nohup "$@"` in
the launcher's inherited cwd, with nothing binding the two. The echo is now
emitted by the launched process from its own working directory, and a
`--case` that disagrees with that directory REFUSES rather than certifies
(L-45). Adds section 1.8 and section 4. Exposure was zero — every log in the
registry predates the echo's adoption by twenty hours — so this closed the
channel before it was ever exercised, and no corpus cleanup was owed.

Version 1.2, dated 2026-08-10. Amends section 1.7 and adds section 3, the
second personal-check pass, on the lever-echo parallel-launch gap: the echo's
launch test read `args[0]` only, so the block never fired on an
`mpirun -np N <solver> -parallel` launch — the shape the campaign's long
solves actually use. Found and fixed by a solver agent at `199e9d17`; this
pass verifies the fix, refutes its no-op claim, adds the regression test, and
records four further echo bypasses the same sweep turned up. Nothing in 1.1 or
1.0 is weakened; 1.7's promise is narrowed to what the code actually delivers.

Version 1.1, dated 2026-08-08. Adds section 1.7, the lever-echo convention,
on the dead-lever audit's evidence (126 lever/conclusion pairs verified from
runtime logs; all 16 unverifiable entries trace to four lever classes stock
OpenFOAM structurally never echoes). Nothing in 1.0 is weakened.

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

**Corrected v1.8 (2026-08-10) — the previous ordering was the one L-41
names as wrong, and this document carried it for two days after the lesson
landed.** Fleet agents execute inside the SDK server process, so a busy peer
is INVISIBLE to `pgrep`, `ps` and `docker ps`. A process sweep answers "is a
SOLVER running", never "is an AGENT working", and the two questions are not
the same one.

Before resuming any agent (charter 9 OPS rule 4), in this order:

1. **`git log --since=<minutes>`** — a working agent commits; a
   pre-registration appearing after your dispatch is proof of a live peer.
2. **File mtimes** in the agent's own files and run dirs
   (`find <runs> -mmin -10`) — a live solve writes constantly even when no
   process name matches your grep.
3. **The docket/inbox claim state** — a claimed item with a recent timestamp.
4. **Only then** process sweeps and `sudo docker ps`, which bound the SOLVER
   and container question and settle nothing about an agent.

Resuming a live agent spawns a second incarnation in the same tree. One
resume per solve, and the resume message carries the outcome the watcher
already collected. A completion notice with no result is the dead-agent tell,
and the answer is reattach, not restart — but it is a tell, not a proof, and
steps 1–3 are what turn it into one.

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

### 1.7. The lever prints its own banner, or the launcher echoes the dict

Verification Charter v1.5 section 9's ``levers_verified_active`` is
satisfiable at write time, never retroactively (adopted 2026-08-08):

- **Launcher echo.** Solver launches through the sanctioned paths
  (`scripts/launch_solve.sh`; the workflows' shared solver runner
  `tmr_verification._foam`) write a
  fenced LEVER-ECHO block at the head of the run log: fvSchemes,
  fvSolution, the constant/ lever dictionaries and the 0/ boundary files,
  each hash-bound by sha256 to the exact bytes that ran
  (`sdk/chief_engineer/lever_echo.py`). Utility logs stay pristine.
- **Patch banners.** Any lab-built patch that adds a lever prints an
  activation banner AND leaves a distinguishable off-state, and hard-fails
  on unrecognized values instead of falling back silently -- the sub-LU
  pattern, whose archived negative control is the exemplar.
- **Records.** A ``levers_verified_active`` entry cites either the lever's
  own banner line or the echo block's line for that file; a record built
  from a log with no echo says plainly that its dictionary levers are
  unverifiable from it. A pre-registration whose plan leans on a lever
  from the four echo-less classes names how the echo will exist.
- **The echo fires on the INVOCATION, never on the first token** (added
  v1.2, 2026-08-10). The runner's launch test was `args[0] in SOLVERS` for
  its first two days, which meant a parallel launch —
  `mpirun -np N <solver> -parallel`, how every long campaign solve launches —
  produced no echo at all, silently, with no error and no warning. Fixed at
  `199e9d17`. **A new adopter inherits two rules from that gap.** First: an
  enforcement predicate keys on the resolved invocation, not on a token
  position, a command spelling, or a caller-supplied path string. Second:
  the test that guards it asserts the block is PRESENT and its CONTENT is
  right, on the launch shape the campaign actually uses — an assertion that
  merely checks nothing raised passes against this defect, which is exactly
  why it survived adoption (`sdk/tests/test_lever_echo.py`, the four
  parallel-spelling tests).
- **The echo does not reach every solver launch, and section 3.3 lists
  which** (added v1.2). Four live paths launch solvers without it: the two
  detached/watched `subprocess.Popen` paths inside `tmr_verification.py`
  itself, `scripts/coefficient_uq_plate.py`'s private runner copy, and the
  campaign scripts that build their own `solve_args`. A record from any of
  those honestly reports `unverifiable`; nobody should read that word as
  "the levers were checked and found wanting".

### 1.8. Evidence is derived from what executed, never from what was declared

L-45, adopted 2026-08-10 (night). The family's own enforcement code broke
this rule twice in three days, in both directions, so it is written down:

- **Derive from the artifact of execution.** The resolved binary, the
  working directory the process is actually in, the file the solver opened,
  the bytes on disk at launch. A parameter a caller supplied describing what
  it INTENDED is a claim to be checked, never a source of evidence.
- **Where a caller's declaration is available, use it only to disagree
  with.** `launch_solve.sh` still takes `--case`; it now uses it solely to
  refuse when it does not resolve to the directory the launched process runs
  in. Agreement is not required for the echo to be right — it is right
  because it is read from the run directory — so disagreement means only
  that nobody can say which directory the solver will read, and that is
  enough to refuse.
- **A refused gate is stated, and it is stated in a way nothing downstream
  can mistake for a pass.** `lever_echo.refusal_block` writes a fence that
  deliberately does not contain the BEGIN marker, so `parse_echo` reads it as
  no echo and the record says `unverifiable`. Silence would have read
  identically to a pre-adoption log; a stated refusal names both paths.
- **Fix false-positive channels before false-negative ones, even smaller
  ones.** A gate that fails open costs evidence you can still go and
  collect. A gate that fails false costs the ability to tell verified from
  unverified anywhere it may have fired, and the cleanup is the whole corpus
  the gate ever touched rather than one record.
- **One implementation.** The launcher no longer carries a shell copy of the
  echo format; it calls the canonical `sdk/chief_engineer/lever_echo.py`
  through `scripts/lever_echo_emit.py`. Two implementations of an evidence
  format are two things that can disagree about what was proved.
- **The test is WHEN THE EVIDENCE WAS CAPTURED, not when it was written**
  (added v1.7, chief's ruling on P-4.2). A launcher that captures the
  dictionaries at t=0 and writes them into the log after the run finishes is
  sound: the bytes are the bytes that ran. A launcher that READS the
  dictionaries after the run and writes them then is not, because the run may
  have changed them — that is the post-hoc assembly L-45 forbids. The two look
  identical in the finished log, which is exactly why the rule has to be
  stated at the capture site rather than inferred from the artifact. It is
  what makes a `subprocess.run(..., stdout=PIPE)` path perfectly verifiable
  despite writing its log last.
- **Verify the premise that the offered options share** (L-48). A choice
  arrives with authority, and the assumption inside it is the part nobody
  re-derives. Picking well from a false menu is worse than rejecting the menu,
  because a well-argued answer to the wrong question is harder to overturn
  than no answer. And when the shared premise is a claimed LIMIT, refuse it
  unless measured: **a gap invites a fix, a constraint forbids one.** A limit
  written into a standard that measurement says is not there is inherited as
  settled, and the cheap fix nobody attempts becomes invisible forever.

### 1.9. Evidence has to survive the next run, not just get written

L-42, enforced 2026-08-10. Creating evidence and preserving it are two jobs,
and this family spent three passes on the first before starting the second.

- **A launcher archives before it overwrites.** Any run log a new run would
  destroy is moved aside first, under a UTC-stamped superseded name — the
  same supersede-don't-delete convention the records use (L-39), and the same
  stamp format `scripts/launch_solve.sh` already uses. That launcher was the
  only path in the lab that survived L-42, and it survived by accident of its
  registry naming; the accident is now the deliberate convention.
- **The archive is named, not numbered.** A timestamp collides only with
  itself; a counter suffix handles the same-second case. An archive that can
  be silently overwritten by the next archive is not an archive.
- **Empty is not evidence.** A zero-byte log is removed rather than archived,
  and the clearing of the live name is part of the contract — see 5.1 for why
  that sentence is load-bearing rather than housekeeping.
- **Unreconstructible is a different word from unsupported** (Verification
  Charter §9). When a log is gone, the record says so on its face with a
  dated amendment, and reconstructs nothing. A record that quietly agrees
  with whichever log survived is worse than one that admits the gap.

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

## 3. Findings record, second personal-check pass (2026-08-10)

The lever-echo parallel-launch gap. Recorded before any further fix was
applied, per the record-before-fixing discipline. Suite: **1214 passed, 0
failed, 149 subtests** (baseline 1210/146; the four new tests are 3.2).

### 3.1. The fix at `199e9d17` is correct, and its no-op claim is FALSE

The behaviour change is exactly right: `args[0] in lever_echo.SOLVERS`
became `any(arg in lever_echo.SOLVERS for arg in args)`, which fires on
strictly more launches and on no fewer. The predicate is monotone, so the
fix can only add echo blocks, never remove one.

Its commit message claims more than that: *"a provable no-op today since no
caller passes mpirun"*. **That claim is refuted.**
`sdk/workflows/rae2822_case9.py:946` passes
`["mpirun", "-np", str(ranks), "rhoSimpleFoam", "-parallel"]` through the
shared runner's own `step()` helper whenever `ranks > 1`. The fix therefore
changes behaviour for a real, in-tree caller: RAE2822 case 9 parallel solves
now get an echo block at the head of `log.rhoSimpleFoam` where they
previously got none.

The change is nonetheless SAFE for that caller, for a reason worth stating
rather than assuming: the echo is fenced and written at the head, and every
consumer of that log reads it from the tail
(`splitlines()[-30:]`) or by substring (`solver_converged`,
`parse_force_split`), none of which the dictionary text can satisfy. So the
verdict is **not a no-op, but harmless and strictly improving** — which is a
different animal from what the commit message asserts, and the difference is
the whole point of checking. Method: an AST sweep of all 830 `.py` files for
every string list literal placing a solver name at index >= 1 (a superset of
every value that can reach `args`), carrying its own positive control.

### 3.2. The regression test the gap earned

`sdk/tests/test_lever_echo.py`, four new cases in `FoamRunnerEchoTests`.
They assert the block's presence AND content on the parallel spelling, assert
`levers_verified_active` comes back **mechanical** rather than
`unverifiable`, cover the three solver spellings the repo launches in
parallel, and pin the other direction — a parallel UTILITY launch still
writes a pristine log. Verified against the pre-`199e9d17` predicate in a
scratch copy: 2 tests + 3 subtests fail there and pass here. A test that only
checked for the absence of an error would have passed against the defect.

### 3.3. Sweep: where enforcement still keys on spelling, position or path

| Site | Keys on | Verdict |
| --- | --- | --- |
| `tmr_verification.py:_foam` echo predicate | membership over all args | **FIXED** at `199e9d17` |
| same, residual | an exact-string NAME set | **VULNERABLE (note).** A solver spelled as a path (`/…/bin/simpleFoam`) or behind a wrapper (`foamJob`, `foamExec`) is still invisible. No caller does this today. |
| `tmr_verification.py:1253` `_run_settle_watched_solver` | builds `[*_run_prefix(), "simpleFoam"]` and `Popen`s it | **FIXED** (section 5). Echo written from the same `remote_dir` expression that becomes the process's cwd. |
| `tmr_verification.py:1311` `launch_level_solver` (detached) | same bypass | **FIXED** (section 5), via `_detached_solve_wrapper`. |
| `tmr_verification.py:1430` `launch_level_solver` parallel detached | same bypass, mpirun-spelled | **FIXED** (section 5) |
| `tmr_verification.py:3186` NACA detached branch | same bypass | **FIXED** (section 5) |
| `scripts/launch_solve.sh:177` | `[ -d "$CASE" ]` — a caller-supplied PATH STRING | **FIXED** 2026-08-10 night (section 4). Was the worst of the set: nothing bound `--case` to where the command runs, so a mismatch minted an echo of dictionaries that did NOT run at the head of a log of a solve that did — the set's only false-POSITIVE channel. |
| `scripts/launch_solve.sh`, same block | echo written into the registry `$LOG` | **SAFE (corrected).** v1.2 filed this as a false negative; that was wrong. The launcher redirects the launched command's own stdout/stderr into `$LOG`, so for a `launch_solve.sh` run the registry log IS the run log and the echo heads it. The note stands only for a caller who additionally redirects inside its own command. |
| `scripts/coefficient_uq_plate.py:174` | a private `_foam` copy that launches `simpleFoam` | **FIXED** (section 5): deleted, re-pointed at the shared runner. |
| `sdk/scripts/naca4412_credential_repair.py:101` | private `foam()`, mpirun-spelled solves | **FIXED** (section 5): private `run()` deleted, `foam()` delegates to the shared runner. |
| `sdk/scripts/naca4412_credential_repair.py:157` | `simpleFoam -postProcess -func yPlus` — a UTILITY spelled with a solver name | **FIXED** (section 5). The over-fire became live the moment that script was re-pointed at the shared runner, so `lever_echo.UTILITY_FLAGS` now excludes `-postProcess`: a solver binary that integrates nothing is not a solve. |
| `mesh_certificate.certificate_admits` | re-hashes the points file actually present | **SAFE.** Hash-bound, not path-bound; a certificate cannot drift onto another mesh. |
| `mesh_certificate` cache write/lookup | `points_sha256` binding | **SAFE** |
| `certificate_admits` on a decomposed case | certifies `constant/polyMesh`, while an mpirun solve reads `processor*/constant/polyMesh` | **SAFE (note).** The processor meshes are derived from the certified one; recorded so the gap stays a known gap. |

The four `tmr_verification.py` bypasses and `launch_solve.sh` are family code
and are NOT fixed in this pass: two solver agents hold live uncommitted work
in this tree, and a change to how a running solve's log is written is not a
change to make underneath them. They are recorded here and escalated.
*(Superseded for `launch_solve.sh` by section 4, which landed the same night
once both arms reported; the false-negative sites closed in section 5.)*

**A "latent" finding is a finding with a date on it, not a finding you can
defer** (added v1.5, chief's instruction). The `-postProcess` over-fire in the
row above was filed as *latent — harmless today* because the script carrying it
had no echo. It became live the same night, in the very pass that re-pointed
that script at the shared runner: the thing that made it harmless was the
thing the fix removed. The rule this family takes from it: when a finding is
graded latent, write down **what specifically is holding it latent**, because
that condition is a dependency, and the next change to the surrounding code is
as likely to remove it as to preserve it. "Not exploitable yet" and "not a
defect" are different verdicts.

### 3.4. Claims integrity: no affected record exists

**Every already-recorded `levers_verified_active` is sound.** 13 claims in 12
records carry a non-empty `verified` list; all 13 re-verify exactly against
the LEVER-ECHO block in the log of the run they record, file set and sha256
alike. Zero records carry the field with an empty list, so no record is
implicitly claiming a check it did not get either.

The structural reason, which matters more than the count: the gap could not
produce a false claim in this direction. `levers_verified_active()` derives
its entire `verified` list from `parse_echo(log_text)`, so a launch the echo
could not see yields an EMPTY list and a basis string that says
`unverifiable` in as many words. The args[0] defect made the gate silently
fail OPEN on parallel launches — a missing verification, never a manufactured
one. The two B-52 rung-6 replicate records, the only mpirun-spelled records
in the corpus, were written after `199e9d17` and carry genuine echoes.

Method, stated so its reach is inspectable (L-43): every `*.json` under
`demo-output/` parsed, the field found at any depth, the solver log located
beside the record or in the run root the record names (plain and `.gz`
spellings both), the block re-parsed and compared to the claim. Positive
control: a planted claim citing a sha256 the log does not carry is detected
as a mismatch — the instrument is a detector, not a rubber stamp.

## 4. The false-positive channel, closed (2026-08-10, night)

Chief's ruling on L-45: the false-positive channel outranks every
false-negative on the fix queue, prepared immediately and landed on quiet.
Suite **1222 passed, 0 failed, 152 subtests** (from 1214/149).

### 4.1. Exposure: zero, and it was checked rather than assumed

All 149 logs in `demo-output/website/solve_registry/` carry **zero**
LEVER-ECHO blocks, and the newest registry artifact of any kind stamps
`20260808T020454Z` — twenty hours BEFORE the echo landed in the launcher at
`ea0f7d9d` (2026-08-08 22:59:34 +0000). No launch has gone through that path
since the echo existed, so the channel was open and never exercised, and no
record anywhere is owed a re-check. Positive control on the search (L-43): the
same grep finds 11 LEVER-ECHO lines in a known-present specimen,
`FPE_DIAG_runs/BL1/log.simpleFoam`.

### 4.2. What the defect actually did, demonstrated rather than argued

The pre-fix launcher was run against two cases differing in one lever, from
the run directory of one while declaring the other:

```
=== which scheme did the ECHO certify?   div(phi,U) bounded Gauss upwind;
=== which scheme actually RAN?           div(phi,U) bounded Gauss linearUpwind grad(U);
```

Five files, hash-bound, `parse_echo`-passing, `levers_verified_active`
reporting them as mechanical launcher-echo verification — of a case that did
not run. That is the manufactured verification L-45 names, produced on
demand, and it is why this outranked four larger false-negative sites.

### 4.3. The fix

- `lever_echo.echo_block_for_run_dir(run_dir, declared_case=None)` — the
  canonical function. Echoes `run_dir`; refuses when `declared_case` resolves
  elsewhere; refuses when the directory holds no lever dictionaries at all
  (an empty block would otherwise parse as a verification of zero files).
- `lever_echo.refusal_block()` + `REFUSED` fence — carries no BEGIN marker,
  so a refusal is `unverifiable` downstream and can never read as a pass.
- `scripts/lever_echo_emit.py` — reads the working directory it is in, takes
  the declaration from the environment (not argv: it is invoked from inside a
  single-quoted `bash -c` string where every added quote is a way to be
  wrong), and always exits 0. A launcher must never be stopped from launching
  by its own bookkeeping: a missing block costs a verification, a failed
  launch costs the run.
- `scripts/launch_solve.sh` — the shell copy of the echo format is DELETED;
  the block is emitted by the launched process itself, in the same shell that
  then `exec`s the command. **The `exec` is load-bearing**: it replaces the
  wrapper so `$!` is still the solver's real pid, which is L-6, the exact
  trap this launcher exists to close. A test pins it.

### 4.4. The tests

Eight new cases across `RunDirectoryBindingTests` and
`LaunchSolveEchoTests` (`sdk/tests/test_lever_echo.py`), presence-and-content
throughout: the echo hashes the run directory and demonstrably *not* the
declared one; a mismatched `--case` yields `parse_echo == {}`, an empty
`verified`, an `unverifiable` basis, a visible refusal naming BOTH paths, and
neither case's hash smuggled in; a lever-less directory refuses rather than
certifying nothing; the refusal fence cannot be mistaken for an echo; the
launcher end-to-end both ways; and the pid guard for the `exec`.

Verified against the pre-fix launcher: the mismatch test fails there with the
five wrong hashes in its diff, and passes here. The fixture is a
preflight-clean laminar case, and the harness asserts the launcher did not
refuse at preflight — otherwise a preflight failure would look exactly like
an echo failure and the test would measure nothing.

### 4.5. Still open, and the question underneath them

The six false-negative sites from 3.3 (four `tmr_verification.py` `Popen`
bypasses; the private `_foam` copies in `scripts/coefficient_uq_plate.py` and
`sdk/scripts/naca4412_credential_repair.py`). They lose evidence; they cannot
fake it. Filed as a proposal rather than patched piecemeal, because a family
running solves through six launchers has an enforcement surface it cannot
reason about, and patching six is how it becomes seven —
`docs/charters/PROPOSALS_OPEN.md`, one-launcher consolidation, migration cost
priced.

## 5. P-4.1 as approved: C+D landed, B refused (2026-08-10, night)

Chief approved option C+D and **refused option B, full consolidation**, on the
reason the family filed it with, now policy: *the detached path is what every
long solve uses, its PID/exit-file protocol is the L-5/L-6/D12 failure family,
and a defect there ORPHANS SOLVES rather than losing an echo. We do not accept
a small chance of losing runs to buy a large certainty of gaining echoes.*
That is L-45's asymmetry applied to a migration instead of to a gate. Suite
**1230 passed, 0 failed, 161 subtests** (from 1222/152).

**One launcher definition now exists in family code**
(`tmr_verification._foam`), and one place decides what counts as a solve
(`lever_echo.launches_a_solver` / `echo_if_solver`).

- **The four detached/watched paths** route through
  `tmr_verification._detached_solve_wrapper`, which calls the same
  `scripts/lever_echo_emit.py` the sanctioned launcher uses. Three properties
  are load-bearing and each is one edit from being lost, so each has a test:
  the echo is emitted by that shell from its own working directory (L-45);
  `$?` is read immediately after the solver so **`solve.exit` still carries
  the SOLVER's exit code** — if the emitter's status ever leaked in, a failed
  solve would be collected as a successful one; and **the emitter creates the
  log, not Python**, so the callers' `if not log_path.exists(): raise` launch
  check still tests whether the shell ran instead of testing whether Python
  wrote a file. Pre-seeding from Python would have silently made that safety
  check vacuous, which is the shape of defect this whole pass is about.
- **The watched path** has no shell to emit from, so its echo is written from
  the same `remote_dir` expression that becomes `Popen(cwd=...)` on the next
  line — bound at the point of use, with no second path that could differ.
- **`scripts/coefficient_uq_plate.py`'s private `_foam` is deleted** and
  re-pointed at the shared runner. Behaviour verified identical: the deleted
  copy hardcoded `openfoam2606` and `_run_prefix()` resolves to exactly
  `['openfoam2606']` on this host, while additionally honouring
  `OPENFOAM_RUN_PREFIX`, which the private copy could not.
- **`naca4412_credential_repair.py`'s private `run()` is deleted** — not left
  unused, because a second launcher sitting in a file is a second launcher
  somebody adds a call to. Its `foam()` now delegates to the shared runner
  while keeping this module's raise-on-failure/return-the-text contract, so
  the change does not push error handling onto ten call sites.
- **The `-postProcess` over-fire, filed as latent in 3.3, became live** the
  moment that script was re-pointed: `simpleFoam -postProcess -func yPlus`
  would have written an echo into a utility log. `lever_echo.UTILITY_FLAGS`
  now excludes it. **A solver binary that integrates nothing is not a solve**,
  and keying on the solver NAME alone cannot see that — the same class of
  mistake as keying on `args[0]`, found by the consolidation that was fixing
  the first one.

**Reported as drift, not edited** (other families' campaign scripts, chief is
routing them): `W1_runs/run_rung.py:39`, `W1_runs/build_case.py:29`,
`F5_runs/cylinder_ladder.py:465`.

### 5.1. Worked example: a fix that creates the artifact a check tests for disables the check

Recorded by chief's order, because the near-miss is more instructive than the
fix. **This is a general rule, not a story about logs.**

While routing the detached solve paths through the canonical emitter, the
first design pre-seeded the run log from Python — write the echo, then let the
shell append the solver's output. It worked, the suite passed, and it was
wrong. The callers decide whether a detached launch actually happened with:

```python
time.sleep(3)
if not log_path.exists():
    raise RuntimeError(f"{level.name}: detached solve failed to launch")
```

That check works because, before the fix, **only the launched shell could
create that file**. Pre-seeding it from Python would have made `exists()` true
whether or not the shell ever ran — so a solve that failed to launch at all
would have been reported as launched, and the failure would surface hours
later as a run that produced nothing. Nothing would have failed at the time.
No test would have gone red. The check would simply have stopped meaning
anything.

The general form, worth applying anywhere:

> **When a fix creates, touches, or guarantees an artifact, find every check
> that tests for that artifact's existence — those checks just got weaker, and
> the weakening is invisible because everything still passes.**

The corrected design has the emitter create the log, so the check still tests
what it always tested. The property is now pinned by a test
(`test_the_log_is_created_by_the_shell_not_by_python`) and restated as a
contract in `_supersede_log`'s docstring, because it is one edit away from
being lost by someone who reasonably thinks it does not matter.

The uncomfortable part is worth stating plainly: this was the fix for a class
of defect nearly reintroducing that class, inside the pass that exists to
close it. Familiarity with a failure mode is not immunity to it.

**Third instance, and the one that makes this a pattern rather than an
anecdote** (2026-08-10, chief's instruction to record it). The elision fix in
section 7.1 shipped a first version that **failed its own test**: the marker
written to account for each dropped payload embedded that payload's byte count
and sha256, so two replicates differed *through the very marker added to
describe the difference*, and the G4 equality it was meant to repair still
failed. Nothing flagged it. It was caught by running the comparison against
the two real replicate cases instead of reasoning about whether it would work.

The three together — the vacuous launch check, the archive name caught by five
globs, and a marker that defeated its own comparison — are one failure mode
seen from three sides:

> **A change is not finished when it does what you intended; it is finished
> when you have run the check that would fail if it did not.** All three of
> these looked right, read right, and passed every existing test. Two were
> found by asking *what else reads this?* and one by refusing to reason about
> a result that could be measured on real data in under a minute.

The third is the only one where the author's own claim was the thing under
test, which is why it is the least likely to be caught by anyone else and the
most important to record.

## 6. L-42 enforced: the evidence now survives the next run (2026-08-10, night)

Chosen under the standing directive as the highest-value item this document
identified, approved by the chief, and priced at **zero core-minutes** — no
solve; the suite is the test. Suite **1239 passed, 0 failed, 167 subtests**.

**Why this and not something else.** Three passes made hash-bound lever
evidence exist; none made it survive a rerun. Every launch path in family code
destroyed the prior log — `_foam` opened it `"w"`, the three detached paths
`unlink`ed it — so the record's mechanical `levers_verified_active` basis died
with the log the moment anyone reran the case. The value of the L-40/L-45 work
was therefore capped by a defect in the same machinery, and the fix costs no
compute at all.

**Exposure at the time of the fix, measured not assumed:** 90 committed solver
logs sit in reusable case directories, **9 of them already carrying LEVER-ECHO
blocks**; 111 `study-b52-*` case directories were reusable, with a closure arm
live in that tree. `scripts/launch_solve.sh` was the sole surviving path, and
only because its registry logs are UTC-stamped and never collide.

**The fix.** `tmr_verification._supersede_log()`, called by the shared runner
and by all three detached paths. It renames an existing non-empty log to
`superseded_<UTC stamp>_log.<name>`, adds a counter on a same-second
collision, removes a zero-byte log rather than archiving it, and never raises
— a lost archive costs one run's evidence, a refused launch costs the run.
**Its contract is that the live name is free on return**, for the reason in
5.1. The live *name* is never renamed out from under a running solve: the
archive happens at the start of a new run in that directory, before anything
opens the log.

**Why the stamp is a PREFIX, which is 5.1 applied in the other direction.**
The readable name is `log.simpleFoam.superseded_<stamp>`, and it would have
been a defect. This fix CREATES artifacts, so every check that READS those
artifacts had to be re-examined: five places in the repo select a case's run
log by globbing `log.*`, `log.*Foam` or `log.simpleFoam*`, and one of them
(`sdk/scripts/replay_s12_unsettled_stop.py:114`) picks the **largest** match —
so an archive larger than the live log would have been silently classified as
the run, turning an evidence-preservation fix into an evidence-confusion bug.
The prefix form matches none of the five patterns, and a test asserts that
against all four glob shapes so a future tidy-up cannot move it back. Where
5.1 says *a fix that creates an artifact weakens the checks that test for it*,
this is the same rule reaching the consumers rather than the guard.

**The known casualty, repaired as ordered and not reconstructed.**
`MODEL_FORM_runs/H_re10595_realizableKE/record.json` gains a dated
`evidence_amendment` and **no existing value is touched** (verified
key-by-key: zero pre-existing keys changed, one added). It states the facts
established from the artifacts: the governing record describes a
30,000-iteration run written 2026-08-08T03:46:17Z; the surviving
`log.simpleFoam.gz` ends at `Time = 12000` and was written
2026-08-08T23:52:59Z, belonging to a later rerun whose own honest record is
preserved beside it. Nothing was falsified and no number is withdrawn — the
30,000-iteration fields survive under `30000/`. What is lost is the 03:46
run's runtime log and every claim only a log can settle, and it is lost
**unreconstructibly, not merely unsupported**: the launcher echo did not exist
until 22:59 that night, nineteen hours after the run. The amendment says the
cell's standing is unchanged (excluded, same two reasons) so that the two
runs' agreement is never mistaken for verification.

**Ten tests** (`SupersededLogTests`), content-first: the archived log's bytes
are still readable; the stamp matches the launcher's convention; the live name
is free afterwards for both non-empty and empty inputs; empty logs are not
archived as evidence; three same-second reruns produce three distinct
archives; the shared runner archives before overwriting; and — the one that
names the point of the whole pass — **a first run's hash-bound echo survives a
second run that changes the levers**, with the archive parsing to the original
hashes and the new log to different ones. Verified against the
destroy-in-place behaviour: the two end-to-end cases fail there.

## 7. The echo stops recording solutions (2026-08-10, night)

Two items routed in from the Cases family's campaign-script pass. Suite
**1247 passed, 0 failed, 171 subtests**. Zero core-minutes.

### 7.1. The echo was 97.8% solution data, and one fix closed two defects

**Measured before it was fixed.** On B-52 rung 6 the LEVER-ECHO block was
**24.6 MB of a 25.2 MB solver log**, `0/U` contributing 13.1 MB and `0/phi`
11.5 MB — exactly the two files `potentialFoam -writephi` writes. The same
root cause failed the B-52 arm's G4 replicate-equality clause on exactly those
two files.

**The cause.** `0/` is echoed as "the boundary-condition dictionaries", but
after an initialization pass it holds two different things: the BC
SPECIFICATION, which is lever class 3 and the reason these files are echoed at
all, and field VALUES, which are computed solution data and no kind of lever.
`0/phi` is not a boundary condition in any sense — it is a flux field the
solver wrote.

**The fix is one rule, not a list of special cases:** any `nonuniform List`
payload over 4 kB is elided wherever it appears, leaving a marker with its
element count, byte count and its own sha256. Eliding only `internalField` was
tried first and was not enough — it still left 640 kB of per-face data inside
one `boundaryField`. Result on the real case: **24.6 MB → 8.5 kB, 2896x**,
with `type freestreamVelocity;`, `freestreamValue uniform (0 0 100);`,
`noSlip`, `consistent`, `divSchemes` and `simulationType` all still verbatim.

**Two hashes now, because one cannot answer two questions.** `sha256` still
binds to the exact bytes on disk — the charter's binding, never weakened, and
a test asserts it survives elision. `lever_sha256` covers the lever content
with bulk payloads and their element counts replaced by a constant token, and
is what a same-recipe comparison uses. On the two real B-52 replicates:
whole-file hashes still differ (correctly — different meshes), **lever hashes
now match exactly**, so G4 can pass on what it meant to compare. A test pins
the other direction too: change `noSlip` to `slip` and lever equality breaks.

**The first version of this fix failed its own G4 test**, because the elision
marker embedded the payload's byte count and hash — so every replicate
differed through the very marker added to describe the difference. It was
caught by running the check against the two real cases rather than reasoning
about it. That is the third time in this campaign that a fix's own claim
needed testing rather than believing.

### 7.2. Five "shell string" launches are not shell strings

Reported as needing either a vector interface or a permanent
unverifiable marking. **Measurement refuses the second option: 24 of 24
commands across the five files contain ZERO shell metacharacters.** They are
argument vectors spelled as strings; the `bash -c` exists only to `source` the
OpenFOAM bashrc, an environment concern `_run_prefix()` already resolves. The
routing agent's PRINCIPLE — that splitting an arbitrary shell string to decide
what ran is spelling-keying, and forbidden — is correct and stays; it simply
does not bite here, because nothing needs splitting once the call sites pass
vectors.

Filed as **P-4.2** (`PROPOSALS_OPEN.md` v2.6), recommended NEXT-TOUCH rather
than as a campaign: zero core-minutes, ~1 pass, but all five are
false-negative paths on completed cases, so the migration buys nothing until
one is run again. **The "permanently unverifiable" option is recommended
against on principle**: a false constraint written into a standard is worse
than an open gap, because a gap invites a fix and a constraint forbids one.

## 8. Queue assessment, end of the enforcement arc (2026-08-10, night)

The arc is complete: evidence **exists** (the echo), **survives a rerun**
(L-42 archiving), **cannot be forged** (run-directory binding, L-45), **cannot
be missed on the launch shapes that matter** (predicate consolidation), and is
**small enough to read** (2896x elision). Recording what is left, because a
supervisor's "nothing to do" is a claim that should be auditable rather than
taken on trust.

**Nothing in this family clears the ~10 core-min bar. The queue is genuinely
empty.** What was considered and why each was not taken:

| Candidate | Verdict |
| --- | --- |
| `lever_echo.SOLVERS` is a spelling-keyed allowlist: a solver not in it gets no echo, silently | **Latent, no live gap.** Measured: every solver with evidence of ever having run (7) is in the 11-entry list; `plot3dToFoam`, the only unlisted name with a log, is a mesh converter and correctly excluded. Per 3.3, the condition holding it latent, stated: adopting a new solver is a deliberate act during which this list is the obvious thing to touch. A cheap consistency fix is available — make the predicate's silent "no" visible the way the launcher's REFUSED fence is — and is filed for next touch, not a pass of its own. |
| Superseded logs accumulate on disk (introduced by section 6) | **Not a risk, measured.** 363 GB free of 484 GB; archives are single-digit MB; and 7.1's elision cut the dominant 24 MB logs by ~97%, so the growth rate fell as this was introduced. |
| K-2, the 45+30-minute silence window that powered the box off mid-campaign | **Not the family's to rule on.** A cost-control tradeoff with a measured downside is the owner's decision; on Katie's standing list and staying there. |
| 2 orphaned claims, 2 done-without-outcome docket entries | Other families' records; escalated 2026-08-07 and still the chief's. |
| Three campaign scripts (3.3) and P-4.2's five paths | Chief routing / ruled NEXT-TOUCH. Not work now, by decision. |
| A-4, A-5, A-6 (section 2.2 notes) | Recorded with stated reasons not to act: a migration boundary that is not a security boundary; process-lifetime memory only; owner-entered fields deliberately exempt from the style rails. |

The right next work for this family is whatever the next incident produces.
This document is iterated on incident, and there is no incident.

## 9. Cross-family lesson propagation sweep, L-41 → L-48 (2026-08-10)

Strategy §1: *"a lesson learned in DAFoam must be checked against closure,
batch, marine within a week — one agent owns the sweep."* Eight lessons landed
in two days with no propagation pass, which is exactly the debt the item
exists to prevent. Zero core-minutes. The question asked of every cell was not
"is the lesson relevant" but **"does a specific instance exist there right
now, and can I find it or rule it out by measurement."**

**Verdict key:** ● instance found · ○ ruled out by measurement · — not
applicable · ✓ already compliant (exemplar).

| | CLOSURE | BATCH / model-form | CAMPAIGN / cases | MARINE | INFRA (mine) |
|---|---|---|---|---|---|
| **L-41** agent liveness | ○ | ○ | ○ | ○ | ● 3 sites |
| **L-42** rerun destroys evidence | ● 2 | ● 3 | ● 9+ | ● 2 | ● 2 (fixed) |
| **L-43** null needs a positive control | ● 1+2 | ✓ exemplar | ○ | ○ | ✓ |
| **L-44** frozen artifacts | ○ 0/50 | ○ | ○ | — | ○ |
| **L-45** evidence from what executed | ○ | ● 1 | ● (shared) | — | ✓ fixed |
| **L-46** artifact-creation audit | ○ | ○ | ● standing | ○ | ● 4th instance |
| **L-47** relaxation invariance | ● 2 | ● 36 records | ● 6 + ✓ origin | — | — |
| **L-48** premise / gap-not-constraint | ✓ exemplar | ○ | ● 1 | ○ | ✓ |

### 9.1. What each row rests on

- **L-41 — ○ everywhere but here.** Every `pgrep`/`ps`/`docker ps` use in the
  other families is correctly scoped to SOLVERS or containers. The three
  incorrect ones are all INFRA procedure docs: `ESCALATION_CHARTER.md:416`
  (OPS rule 4), **this document's own §1.5**, and
  `PROPOSALS_OPEN.md:905`. §1.5 is fixed in v1.8 above — it had carried the
  wrong ordering for two days after the lesson landed, and it was found by the
  sweep rather than by me. The charter and proposals surfaces are the chief's
  and are routed, not edited. Best existing practice, worth copying:
  `B52_RUNG6_REPLICATE_PREREGISTRATION.md:274`.
- **L-42 — the largest debt by far, in every family.** BATCH:
  `model_form_batch.py:856,1242,1183` copy logs into the committed `out_dir`
  with an unconditional `shutil.copy2` (and `gzip -f`), while `record.json`
  beside them IS superseded at line 1706 — a 460-line-apart asymmetry that is
  the exact mechanism of the H_re10595_realizableKE casualty. CASES: 9+ sites
  including `GEN_ALT`, `FPE_DIAG`, `B52`, the `R4_runs/*.sh` `rm -rf log.*`
  drivers, `head_engineer.py:877` and `openfoam.py:481,514`. MARINE:
  `F7_runs/make_dambreak.py:270` rmtree and `run_dambreak.sh` clobbering every
  log. CLOSURE: its analysis scripts launch nothing, but its R4 solve drivers
  are shell scripts under `campaign/` and are counted there.
  **Exemplar to copy: `R4_runs/run_c3_replicates.py:117` cites L-42 by name
  and skips re-staging a completed solve.**
- **L-43 — CLOSURE carries the open ones.**
  `LIAISON_NOVELTY_SWEEP_decomposition_defect.md` claims zero occurrences
  across 63 searches with an excellent reach log and **no labelled positive
  control**; `MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md` and
  `CLOSURE_METHOD_PRIORITY_REVIEW.md` have implicit controls only. The BATCH
  dead-lever audit is the exemplar (explicit reach section, demonstrated
  recovery of a known-present specimen).
- **L-44 — clean, and measured rather than assumed.** All 50 tracked
  pre-registrations and rule freezes examined by commit history: **26
  post-freeze edits add only** (compliant addenda) and **3 modify existing
  lines**, all three of which survive inspection — two are corrections made
  before any outcome existed (one of which corrects the document *against its
  own interest*, `R7_STROUHAL`, restating "written before launch" as "after
  it, not before"), and one updates a `## Status` field. Positive control: the
  detector returned a non-empty set of line-modifying edits, so it can see
  removals. Process note, not a violation: replacing a Status line loses the
  prior state to git alone.
- **L-45 — one fail-FALSE channel, in BATCH, and a second instrument missed
  it.** `model_form_batch.assert_mesh_certified_at_entry(..., fallback=)`
  satisfies the mesh gate from a **caller-supplied second directory** when the
  running case has no `log.checkMesh` of its own, with **no hash binding** —
  the file references `mesh_certificate` zero times, bypassing the hash-bound
  `certificate_admits()` that exists precisely so "a certificate cannot drift
  onto a different mesh". Today it is correct by construction (the H family
  copies mesh and log from one source), so the channel is real and
  unexercised — the same status the `launch_solve.sh` channel had. It is used
  cross-family: `GEN_ALT_runs` and `FPE_DIAG_runs` import it too.
  **The delegated sweep classified this gate SAFE**; it had not traced the
  `fallback` parameter. Its null was a claim about its reach, which is L-43
  demonstrating itself inside the sweep that was checking for L-43.
- **L-46 — a standing exposure, not a list of bugs.** Every family discovers
  results by pattern (`coefficient*.dat`, `*.raw`, `postProcessing/*`), so any
  change adding a file to a case directory edits an undeclared interface. The
  lab already has a precedent: `coefficient.dat` renamed on a restart
  collision blinds settle watchers. INFRA's fourth instance is 9.2 below.
- **L-47 — the cheapest unclaimed instrument in the lab.** MARINE is
  genuinely — (interFoam/PIMPLE, transient). Everywhere else it is available
  and unused, and one target stands out: **`F6b_ERCOFTAC_RESULTS.md:171`
  names the gap itself** — *"the relaxation factors… a 62,400-cell mesh may
  simply need tighter under-relaxation. This is cheaper still to test and
  should be tested first"* — while its reattachment claim sits **+63% to +66%
  against reference**. CLOSURE's R4 Ahmed ladder (all rungs at identical
  `U 0.9`) rests a non-monotone Cd verdict on differences comparable to
  settle noise. BATCH holds relaxation fixed **by design**
  (`MODEL_FORM_BATCH_DESIGN.md:339`), which is correct for comparing models
  and means all 36 records share one untested relaxation setting.
- **L-48 — one soft instance.** `F5bc_unsteady_statistics.md:129` says the
  SIMPLE-vs-SIMPLEC attribution "cannot be verified from any runtime log,
  **existing or possible**". The reason given — that OpenFOAM never echoes
  `consistent` — was true when written and was falsified twelve hours later by
  the lever echo; `F5C_STAGE_A_RESULTS.md:88` now says that gap "is closed
  permanently". The record carries a later amendment, so a careful reader gets
  there, but the words "or possible" are a constraint where a gap was meant.
  Exemplars in the other direction: `NOT_PASSING_REGISTER.md:732` ("cannot be
  verified from anything in the repository, which is a different, weaker
  status than checked and true") and `S1_FIML_FIELD_INVERSION.md:535`, which
  states the limit **with its measurement** (2N = 103,252 primal solves) and
  names the affordable substitute.

### 9.2. What this pass fixed, and what it routed

**Fixed (INFRA, mine):** `tmr_verification._run_simplefoam_to_settle` — the
settle-watched launch got the lever echo added and `_supersede_log` forgotten,
so it was the one launch in the module still destroying a prior log. And
`_copy_best_effort`, the shared archiver for the F5 ladders and four
workflows, now supersedes an existing `log.*` destination, which is L-42's
archive side. **Both were found by the propagation sweep, not by the pass that
wrote the fix** — the fourth instance of L-46's shared form in one campaign,
and the second where the author's own claim was the thing under test. §1.5
corrected for L-41.

**Routed, not fixed** (other families', per the chief's instruction): the
BATCH archive-side log overwrite and the `fallback=` mesh-gate channel; the
CASES and MARINE rerun-in-place sites; CLOSURE's missing positive controls;
the L-47 adoption targets, F6b first; the F5bc "or possible" wording; and the
two chief-owned procedure surfaces carrying the L-41 ordering.

## 10. Declared limits and effective limits (2026-08-10)

Routed in: a DAFoam arm pre-registered a 22 GiB container cap and the runner
applied 16 GiB. Peak was 7.0 GiB so nothing was affected, and it surfaced only
because one agent stated a number and another compared. **The defect is not
the number, it is the silence** -- the record said one thing, the execution
did another, and nothing in between raised its hand. That is the same shape as
an echo certifying dictionaries the solve did not use, so it takes the same
answer.

### 10.1. Where the reported instance actually lives

Not in code this family owns. `DEFAULT_MEM_GB` here is 12, and no
`--memory=16g` literal exists anywhere in `sdk/` or `scripts/`. The cap is in
four **untracked shell scripts in the run tree** --
`certonomous-runs/img_run.sh:7`, `triage_run.sh:14`,
`A3-rung2-n28-tpc1/run_arm_a.sh:18` and `run_arm_b.sh:18` -- each hardcoding
`--cpus=4 --memory=16g`. Routed to the DAFoam family, with a note worth more
than the instance: **those launchers' resource policy is not in version
control at all**, so no review, diff or history covers the numbers that bind
every A3 arm. (Reach: the first sweep of the 65 GB run tree hit its timeout;
per L-43's corollary a timeout null is not an absence, so it was re-run scoped
and the specimens were found.)

### 10.2. Two worse instances in the runner this family DOES own

Found while checking the routed one, and both fixed:

- **A silent rank downgrade.** `docker_dafoam` had
  `self.ranks = min(DEFAULT_RANKS, max(1, ranks))` -- ask for more ranks than
  the default and you got fewer, with nothing said, while your
  pre-registration and your core-minute figure (COMPUTE_BUDGET section 2:
  wall x ranks / 60) both went on citing the number you asked for. Worse than
  the reported case, because that one was a default and this one is an active
  clamp. Now a **stated refusal**; asking for fewer is still honoured.
- **`--cpus` was never set at all**, while DAFoam pre-registrations have
  declared `--cpus=3` / `--cpus=4` for weeks. Every one of those declarations
  was unenforced and nothing said so. Now honoured when given.

### 10.3. The rule, and the instrument

**A runner may not quietly substitute its own value for a declared one. It
honours it, or it refuses out loud -- and either way the log records what
actually bound.** `lever_echo.runtime_envelope_block()` writes a fenced
`RUNTIME-ENVELOPE` block at the head of each container step log carrying the
EFFECTIVE memory, cpus, ranks, timeout and image. A limit nobody applied is
recorded as `UNCAPPED` rather than omitted, because an absent line and an
unrecorded value are indistinguishable to whoever reads the log later -- the
same reason `launch_solve.sh` prints a field even when it is empty.

Every future arm is therefore self-documenting on this axis, which is the
point: a resource cap is a lever, and charter section 9 says a lever is
verified from the execution, never from the declaration.

**Still open, routed:** the four run-tree scripts above; and the fact that two
launchers in this lab now disagree about what they enforce (`docker_dafoam`
sets no CPU cap by default, the arm scripts set `--cpus=4`) -- a second
instance of the two-implementations problem section 1.8 names.

### 10.4. The tail: a declared rank count nobody checked

Section 10 fixed a runner that substituted its own limit. The same defect was
one level up, in this family's own launcher, on the same arithmetic.
`launch_solve.sh --ranks` is a number the CALLER declares, and the collector
multiplies by it -- core-minutes = wall x ranks / 60 -- and **nothing checked
it against the command.** That is the container's rank clamp with the clamp
removed: the cost is still wrong and still silent, and it feeds every
pre-registration, every cost grading and the calibration scorecard's measured
basis.

Now the launcher reads the rank count from the ARGUMENT VECTOR it is about to
exec (`-np N`), which is the invocation itself and not a string to be split:

- declared and observed **agree** -> nothing said, cost priced on the observed
  value;
- they **disagree** -> a loud `RANK MISMATCH` at launch, both numbers written
  into the run log's `RUNTIME-ENVELOPE` block and into the completion record
  (`ranks`, `ranks_observed`, `ranks_priced_on`), and **cost priced on what
  RAN**;
- the command **nests a shell** (`bash -c "..."`) whose contents the vector
  cannot see -> `UNVERIFIABLE`, stated, cost falling back to the declared
  value with the fallback named. A null that says so is the point; a number
  reported as checked when it was not is the whole defect.

Demonstrated: a run declaring 8 ranks while executing `-np 2` now records
`core_min: 0.5`. Before, it billed 2.0 -- **four times the truth, silently.**

### 10.6. Has it ever happened? A measured zero

10.4 showed the channel; this asks whether any historical run went through
it. It is the same question as the `levers_verified_active` sweep: **do
records exist that claim something the machinery could not have delivered?**

**Result: zero mismatches.** Of 146 completion records in the solve registry,
**3 carry a rank declaration and all 3 AGREE** -- declared 4, executed
`mpirun -np 4` -- so no core-minute figure in the registry is mis-priced, and
no cost grading, factor-3 verdict or calibration-scorecard input derived from
one is affected.

**How the executed count was recovered**, since the `.job` record never stored
the command: two independent routes, each reading what the execution itself
wrote. (a) OpenFOAM prints `nProcs : N` in every application header. (b) A
driver log echoes the commands it ran, including
`openfoam2606 mpirun -np 4 simpleFoam -parallel`. The three declared records
resolved by route (b); route (a) was the one that first returned nothing, and
**a null from one instrument is not an absence** (L-43) -- route (b) recovered
all three.

**Positive controls, one per route.** A planted `declared 8 / executed 2` pair
is detected as a mismatch by both. Neither route was trusted on a null.

**Reach.** The other 143 records carry no `ranks:` line **and no `core_min:`
line at all** -- they predate the cost fields, so no mis-priced figure can
exist from them. That number was wrong the first time I computed it: a
`cmin(...) or ""` in my own reach check made an ABSENT line read as a value,
reporting 143 priced records where there are none. Caught by refusing to
accept a surprising count. **The audit instrument having the defect it is
auditing for is now the seventh instance in this campaign.**

**One refinement, not a mismatch.** Each of the 3 agreeing launches ran serial
meshing AND several `-np 4` solves under one declared scalar rank, so its
`core_min` prices the serial phase at 4 ranks. That is a real over-count and a
different defect -- one number for a launch that ran at several rank counts --
recorded here, not fixed, and not affecting the declared-vs-executed verdict.

### 10.5. A suite failure triaged, not committed around

`test_aircraft_optimization.py::ShootRoundTests::
test_the_fleet_comes_up_once_and_goes_down_once` fails on its `_SolvedApi`
subtest: roster shape `[0, 14, 9, 0]` against an assertion of three
transitions. **Not this pass's doing, established rather than asserted** -- it
reproduces with this pass's two uncommitted files stashed, and
`aircraft_optimization` contains zero references to anything section 10
touched.

The diagnosis, for its owner: `n_slots = min(granted, len(grid))` is 14 and
`n_par = min(granted, len(finalists))` is 9, so the fleet changes size between
the screening sweep and the finalist wave. The code comment beside it states
the contract as *"it used to drop back to zero between the screening sweep and
the finalist wave and climb again"* -- and `[0, 14, 9, 0]` never returns to
zero, so it satisfies the stated intent while failing the encoded assertion
`len(shape) == 3`. Either the assertion is stricter than the contract it
documents, or the workflow has drifted from it; **that is the owner's call and
not this family's**, per 1.2's rule that a test weakened without naming the
contract that moved is a rail-bypass. Escalated under 1.6.

Also worth the owner's read: it fails standalone every time, which means the
suite-green history implies its outcome depends on test ordering.

## 11. Minting the certificates the standard already required (2026-08-10)

`certificate_admits()` requires a FILE. The 2026-08-08 audit marked 105 meshes
`CERTIFIED (pre-existing record)` on the strength of a `log.checkMesh`, and
**105 of 105 carried the log while 0 carried a certificate** -- so the standard
this family wrote quarantined every one of them, which is what happened
unprompted to two M6 members and two retrofit ladders. The evidence existed,
the artifact did not, and downstream machinery believed the word.
`scripts/mint_retrospective_certificates.py`, 0 core-min.

**Result: 95 minted, 10 refused and reported.** Verified after the fact: 95
admitted, **0 minted-but-refused**.

- **The cross-check is the load-bearing part.** A retrospective certificate
  rests on a log found later, so nothing inherently binds it to the points
  file present now. Every mint had to show **the log's cell count equals the
  mesh's own `nCells`** from the polyMesh `owner` header. Without it, this
  pass would have re-created by hand exactly the drift the `points_sha256`
  binding exists to prevent -- L-46 again: the fix for a class is where that
  class reappears.
- **7 refusals are a discrepancy in the audit itself**, not in the meshes:
  each row is marked CERTIFIED while the log it cites parses to hard errors
  under the audit's OWN verdict rule -- three with **negative-volume cells**,
  and `tmr-bump-finer` at aspect ratio 2.23e6, above the 1e6 pyHyp threshold
  and far above the 6.6e4-7.4e4 NASA-grid signature the audit documents as a
  flag. **No certificate was written for them.** Minting a `broken`
  certificate would quarantine another family's mesh on a parser's say-so, and
  an absent certificate already quarantines it, so the conservative action and
  the honest one coincide and the ruling stays with the owner.
- **3 refusals are meshes that state no cell count of their own**
  (`w1-bump-nasa-grids` coarse/medium/fine), so the cross-check cannot run and
  the mint is not attempted.
- **Provenance is recorded, not assumed.** Every minted certificate carries
  `provenance: retrospective-from-archived-log`, the log path, both mtimes and
  the cross-check result. **6 of 95 rest on a log written BEFORE the points
  file**; cell counts agree, so size is unchanged, and the ordering is
  disclosed rather than relied on. A reader can tell a birth certificate from
  a back-filled one, which keeps the mesh standard's guarantee at its actual
  width.
- **The audit takes a dated amendment, never a rewrite** (L-44). No verdict is
  revised and no mesh is impugned; a word that named a missing artifact is
  corrected to CHECKED BUT UNCERTIFIED.

**Found while fixing it, and now fixed for the three scripts this family
owns:** `scripts/launch_solve.sh` -- *"the ONLY sanctioned way to start a long
solve"* -- was tracked in git as mode `100644`, **not executable**. It has
worked only because every working tree happened to carry the bit locally; a
fresh clone could not run it. **29 tracked scripts under `scripts/` carry a
shebang and no exec bit**; the wider set is reported, not mass-chmodded,
because most belong to other families. It surfaced because rewriting the file
dropped the local bit and this family's own launcher tests went red -- the
suite catching a defect that had been latent since the file was created.

## 12. The mesh gate could mint a clean certificate from a crash (2026-08-10)

Reported by the Cases family while re-checking all 95 retrospective
certificates (95 agree, zero drift). **`parse_check_log` matched error
PATTERNS, and a log where checkMesh DIED contains none of them, so it returned
`verdict: "clean"`.** L-45's category, in the one place where a manufactured
pass admits a mesh nobody checked -- and it was in this family's own module,
gating every mesh in the lab.

**It was worse than reported, established by reproducing it.** The report said
the cell-count refusal in `write_certificate` was the only thing standing
between that and a false clean certificate. It is not even sufficient:
**checkMesh prints its mesh stats EARLY**, so a run that dies during the
geometry checks carries a cell count and passed both the parser and the guard.
That shape mints a `clean` certificate outright, with nothing in its way.

**The fix, and the design brief it came with: absence of error evidence is not
evidence of a clean mesh.** The parser now asks *did the check run* before
*what did it find*, and returns a third verdict, `unverified`, when a fatal
marker is present, when the log does not reach checkMesh's own terminating
`End`, or when no cell count appears. `unverified` is deliberately NOT
`broken`: broken means checked and found bad, unverified means we do not know,
and collapsing them would impugn a mesh whose only fault is a missing log --
the opposite error and just as wrong. `write_certificate` refuses to mint from
it, the cell-count guard is KEPT as a second line rather than the only one,
and `head_engineer`'s hand-rolled certificate path -- which does not inherit
those refusals -- states its own.

**The completion marker is calibrated, not guessed:** 105 of 105 real
checkMesh logs in the archive end with `End`, and 0 of 105 carry a fatal
marker, so requiring one and rejecting the other misclassifies none of the
corpus. Re-run over all 105 after the fix: 90 clean, 8 flagged, 7 broken, 0
newly unverified -- the corpus split is unchanged.

**Exposure: zero.** All 95 minted certificates re-checked under the fixed
parser; none rested on a log the fix reclassifies. No revocation was owed.

**And the fix broke on its own corpus first.** A draft `_FATAL` pattern
included `Floating point exception`, which appears in the STARTUP BANNER of a
healthy checkMesh log (`sigFpe : Enabling floating point exception
trapping`) -- it misread all 105 real logs as crashes. The term was added
AFTER the pattern was calibrated and before it was re-validated. Caught by
re-running the calibration rather than the one sample. That is the eighth
instance in this campaign, and the rule it earns is the one already standing:
**a change is not finished when it does what you intended.**

**Second item: the third provenance constant.** `PROVENANCE_FRESH_RECHECK =
"fresh-recheck-of-existing-mesh"` -- neither `at-creation` (the mesh predates
the check) nor `retrospective-from-archived-log` (the log is fresh) is honest
for a re-check of an existing mesh. The string matches the one the Cases
family hand-wrote exactly, so their three `w1-bump-nasa-grids` certificates --
the same three this family refused for stating no cell count of their own --
are already conformant and need no migration. Nothing branches on the value
today, which is why it was second; a provenance field that cannot express what
happened gets filled in with something false by whoever next needs it.

## 13. A standard claimed coverage nothing supplied (2026-08-10)

`MONITOR_STANDARD.md` said *"the whole of both approved monitor proposals is
in force."* **S6 (residual stall) and S8 (Courant excursion) cannot fire on
any production run**, and could not on the day that was written: both return
early without a gate, and `HeadEngineer.__init__` takes
`case_name, out_root, *, novel, on_event` -- **no parameter exists by which
either gate could be supplied.** Three `LogMonitor` construction sites exist
repo-wide: production (passes neither), the offline replay (passes
`residual_target`), and the tests. `LogMonitor.check_wall_time`, S9's entry
point, has no caller but tests.

### 13.1. The practice this earns

**When a capability is claimed IN FORCE, find its production CALL SITE** --
not its definition, not its test, not the prose. And the reason it hid is the
transferable half: **every per-rule Status line in that standard is honest.**
They say a rule fires *"when constructed with `residual_target`"*, and each is
true. The summary sentence is false and is assembled from nothing but true
ones -- a summary drops the conditionals, because that is what summaries do,
and the honest clause upstream makes the summary feel audited. A summary is
therefore the least trustworthy sentence in a document, not the most, and it
is the one a reader quotes.

Practical form for this family's own documents: **a coverage claim carries the
call site, or it is downgraded to a claim about the implementation.**

### 13.2. The wiring decision, and why the evidence refused it

Not wired, and recorded as a **gap with a price, never as a limit** (L-48).
The rules were approved and never delivered to production, so "leave it" would
enact a refusal the owner never made -- but wiring them is an ADOPTION, and
`MONITOR_STANDARD.md` section 3.1 requires a replay with a stated fire count
first. That evidence does not exist, and for S6 **the artifact that appears to
be it is not**: the 2026-08-01 replay reports 37 fires over 46 gated logs, and
**all 46 recovered targets are the same value, `p: 1e-15`**, a run-to-the-cap
sentinel from one case family that no solve reaches. The 80% is one family
judged against an unreachable number, not a fire rate -- and 80% would have
been above the two-thirds that got S7 withdrawn, so the figure that looked
like a reason to wire it was also a reason not to, and neither reading was
sound. Priced at ~1 pass each, 0 core-min, in the standard's own table.

Both derivations point the same way, which is the day's standing discipline:
**the gate comes from the case's own dictionaries** (`residualControl` in
`fvSolution`, `maxCo` in `controlDict`) -- what configures the run -- **not
from a constructor argument**, which would reproduce this very defect one
layer up, because whoever forgets it gets silence.

### 13.3. Blast radius corrected in two records

The five-day threshold defect (`MONITOR_STANDARD.md`,
`VERIFICATION_CHARTER.md`) recorded that *"every caller that took the monitor
default"* judged on an unapproved threshold. **Every caller was the test
suite.** The code defect was real and the fix was right; the exposure was not.
Both records now say so. **A record that overstates its blast radius spends
the same credibility as one that understates it**, and this family has now
corrected one of each in a day.

**U3, noted not fixed:** S9 is wired at `mega_batch.py:810` and **0 of 208,193
ledger rows carry the field**, because the rule landed after the ledger's last
row; run in memory the live detector would flag 30 historical rows. Wired,
correct, and never once exercised -- which is a third state beside reachable
and unreachable, and worth a column of its own the next time this table is
drawn.

### 13.4. The corpus behind six adopted rules was a filename accident

`MONITOR_STANDARD.md` section 3.1 makes an archive replay the gate on
adopting a detection rule. The replay tool globbed `*.log` **while OpenFOAM
writes `log.<app>`**, so that gate was discharged for S1-S6 over **449 files**
against **1,375 real run logs**. This outranked the wiring question and was
taken first.

**The fix is a derivation, not a wider glob** (L-49). Matching `*.log` AND
`log.*` still misses **96** real run logs -- `logMeshCheck.txt`,
`A5_logMeshGeneration.txt`, `A4_coarse_log.checkMesh`. A list of patterns is
the same defect with more entries. The corpus is now derived from what a run
WRITES: an OpenFOAM application prints an `Exec   :` banner that dictionary
and field files never carry. Binaries are excluded by a NUL test rather than
an extension, so **no naming rule participates at any point**. The sweep costs
about a second; the replay 8 minutes; both zero compute.

**It reversed this family's own conclusion from the previous pass.** The
earlier refusal to wire S6 rested on its replay reporting 80% fires with every
recovered target the same `1e-15` sentinel. On the corrected corpus the gated
set goes 46 -> 222 across 3 families with 8 distinct targets, and separating
the sentinel gives the number section 3.1 actually asks for:

| target class | logs | fire | rate |
|---|---|---|---|
| sentinel `1e-15`, unreachable by construction | 135 | 134 | 99% |
| **real declared targets** | 87 | 41 | **47%** |

47% is well under the two-thirds that withdrew S7, and it is not uniform --
dafoam 94%, campaign 51%, mega-batch 20% -- a spread a single global rate
hides in both directions. **The refusal was right on the evidence then
available and is no longer supported.** A published line in the standard is
also refuted: 70 logs outside the one family carry real declared targets, and
they sat in files the glob could not match.

The lesson this family takes: **a corpus is evidence, and it needs its reach
stated like any other instrument** (L-43). Six rules were adopted against a
corpus nobody had asked "what does this select, and what does it silently
drop".

### 13.5. A warrant corrected without touching its rule

S1's justification said *"every OpenFOAM log prints a trapping banner"*.
Measured: **39 of 149 registry logs carry no `trapFpe` line**, across eight
family prefixes -- the banner appears only when `FOAM_SIGFPE` is set, so it is
a fact about how a run was launched, not about OpenFOAM. **The rule is
untouched and still right**: S1 keys on the handler, i.e. the signal, which is
strictly safer whether or not the banner is universal -- and the measurement
flatters the design, since a banner-keyed detector would have been blind on 39
logs and read the other 110 healthy runs as fatal.

**Say which one moved.** The warrant moved; the rule did not. An amendment
that blurred them would spend credibility for nothing, which is the same coin
as an overstated blast radius.

## Related

- `docs/charters/SUPERVISION_CHARTER.md`. The role, the four personal
  checks, what the chief retains.
- `docs/charters/ESCALATION_CHARTER.md`. Section 9 OPS (keepalives, resume
  discipline, pre-registration), section 9.6 (explicit-path staging).
- `docs/standards/MONITOR_STANDARD.md`. The S12 replay pattern section 1.3
  points new rules at.
- `sdk/chief_engineer/agenda.py`. The schema-rails implementation this
  document names as the pattern.
