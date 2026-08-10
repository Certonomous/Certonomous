# Infrastructure and Standards Family Supervision Guidelines

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
| `tmr_verification.py:1253` `_run_settle_watched_solver` | builds `[*_run_prefix(), "simpleFoam"]` and `Popen`s it, bypassing `_foam` | **VULNERABLE.** No echo, ever. |
| `tmr_verification.py:1311` `launch_level_solver` (detached) | same bypass | **VULNERABLE** |
| `tmr_verification.py:1430` `launch_level_solver` parallel detached | same bypass, mpirun-spelled | **VULNERABLE** |
| `tmr_verification.py:3186` NACA detached branch | same bypass | **VULNERABLE** |
| `scripts/launch_solve.sh:177` | `[ -d "$CASE" ]` — a caller-supplied PATH STRING | **FIXED** 2026-08-10 night (section 4). Was the worst of the set: nothing bound `--case` to where the command runs, so a mismatch minted an echo of dictionaries that did NOT run at the head of a log of a solve that did — the set's only false-POSITIVE channel. |
| `scripts/launch_solve.sh`, same block | echo written into the registry `$LOG` | **SAFE (corrected).** v1.2 filed this as a false negative; that was wrong. The launcher redirects the launched command's own stdout/stderr into `$LOG`, so for a `launch_solve.sh` run the registry log IS the run log and the echo heads it. The note stands only for a caller who additionally redirects inside its own command. |
| `scripts/coefficient_uq_plate.py:174` | a private `_foam` copy that launches `simpleFoam` | **VULNERABLE.** No echo at all; a second runner diverged from the sanctioned one. |
| `sdk/scripts/naca4412_credential_repair.py:101` | private `foam()`, mpirun-spelled solves | **VULNERABLE.** No echo. |
| `sdk/scripts/naca4412_credential_repair.py:157` | `simpleFoam -postProcess -func yPlus` — a UTILITY spelled with a solver name | **Latent over-fire.** Harmless today because that runner has no echo; it would pollute `log.yPlus` if routed through `_foam`. The pristine-utility guard in 3.2 pins the boundary. |
| `mesh_certificate.certificate_admits` | re-hashes the points file actually present | **SAFE.** Hash-bound, not path-bound; a certificate cannot drift onto another mesh. |
| `mesh_certificate` cache write/lookup | `points_sha256` binding | **SAFE** |
| `certificate_admits` on a decomposed case | certifies `constant/polyMesh`, while an mpirun solve reads `processor*/constant/polyMesh` | **SAFE (note).** The processor meshes are derived from the certified one; recorded so the gap stays a known gap. |

The four `tmr_verification.py` bypasses and `launch_solve.sh` are family code
and are NOT fixed in this pass: two solver agents hold live uncommitted work
in this tree, and a change to how a running solve's log is written is not a
change to make underneath them. They are recorded here and escalated.
*(Superseded for `launch_solve.sh` by section 4, which landed the same night
once both arms reported. The false-negative sites remain open.)*

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

## Related

- `docs/charters/SUPERVISION_CHARTER.md`. The role, the four personal
  checks, what the chief retains.
- `docs/charters/ESCALATION_CHARTER.md`. Section 9 OPS (keepalives, resume
  discipline, pre-registration), section 9.6 (explicit-path staging).
- `docs/standards/MONITOR_STANDARD.md`. The S12 replay pattern section 1.3
  points new rules at.
- `sdk/chief_engineer/agenda.py`. The schema-rails implementation this
  document names as the pattern.
