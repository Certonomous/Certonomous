# Certonomous Escalation Charter

Version 1.6, dated 2026-08-17. Governs what the lab decides alone and what goes
to the owner. It binds unattended work, which is where the question actually
arises.

**The git rule lives in §9.6, §9.6a, §9.6b and §9.6c, at the very end of this
file, below `## Related`.** §3 item 2 states the 2026-08-05 form and is
superseded; it now carries a dated amendment saying so. Read the tail.

Version 1.1 adds section 8, on instructions, after three acts honoured a stated
instruction without acknowledging it and a fourth found the artifact and the
stated intent disagreeing. Section 3 gains the shared working tree. Nothing in
1.0 was weakened.

Version 1.2 makes section 4 decision-ready: the free-spend thresholds are now a
single recommendation with numbers calibrated against the multi-agent record
the 1.0 draft predates, answerable as "P-7.1: A". **Nothing in section 4 is
enacted. It awaits her number**, and until she gives one the standing defaults
and the docket are the whole of the rule, exactly as before.

Version 1.3 adds section 9, OPS, after the fleet was killed three times in two
days, by three unrelated causes, and lost no science on any of them. Five
operational rules, each traced to the incident that proved it. Nothing in
section 9 needs a ruling: these are descriptions of what already worked, and
the one thing they ask for that is not yet habit, arming both keepalive holds,
costs one command.

Version 1.4 adds §9.6b — a pathspec commit isolates by FILE, not by AUTHOR, so
reading `git diff <path>` before committing a shared file is a separate and
mandatory check — and amends §3 item 2 in place to stop it handing readers the
superseded 2026-08-05 rule. Both were filed by the cold-start memory test on
2026-08-11, twice, by two agents who did not know of each other. Neither 9.6 nor
9.6a bumped this header when they landed; that omission is the other half of the
defect, and 1.4 exists partly to end it.

Version 1.5 adds §9.6c, the same day as 1.4 and against it: the considerate
response to 9.6b -- leaving a shared file uncommitted rather than sweeping a
peer's rows into your own commit -- hands your attribution to whoever commits
next, which on this tree is a matter of seconds. It happened within the hour.
9.6c carries the split-patch procedure instead of a warning.

## 1. The line

> **Initiative comes from the lab. The veto stays with the human.**

That sentence is not new here. It is the module docstring of
`sdk/chief_engineer/agenda.py`, it already governs the agenda machinery, and it
is the right line for the whole lab. The machinery enforces it literally:
nothing in that module launches compute, a proposal changes status only when
the owner approves or dismisses it in the control room, and even an approval
starts a mission only when the compute audit says the machine has room.

The working test that follows from it:

> **The lab decides what is reversible and cheap. Everything that is expensive,
> irreversible, or public goes to the docket.**

Three words, and each one is checkable. Reversible means the work can be undone
by deleting an artifact. Cheap means inside the free-spend threshold in section
4. Public means it leaves this box.

## 2. The lab decides alone

No escalation needed. Doing these without asking is the job.

- **Running an approved proposal**, at or under its stated `est_core_min`,
  inside a family that already has approval.
- **Choosing method, mesh and schemes** within an approved case, subject to the
  standards and the case selection charter.
- **Stopping a run.** Always. A run that is diverged, non-physical or outside
  its budget is stopped without asking, and the stop is recorded. The failure
  mode this prevents is L-18's: a job producing Cd of minus 55.3 on a wing ran
  57 minutes because nobody wanted to interrupt something that looked
  legitimate.
- **Writing up a failure.** `NOT_PASSING_REGISTER.md` is filled in by the lab.
  A documented failure with a named cause is a result and needs no permission.
- **Drafting proposals.** Initiative is the lab's. Drafting is not deciding.
- **Correcting the record against primary evidence.** L-1: where the docket and
  the repository disagree, the commit wins, and then the docket gets corrected.
  Report both, say which artifact each figure came from, and do not silently
  pick one.
- **Retracting one of our own numbers when the evidence retracts it.** F7a's
  two published root causes were withdrawn by the lab, and F6a's corner values
  went with the sign error that produced them. Withdrawing our own wrong number
  is not a decision that needs approval. Leaving it up would be.
- **Regression tests and instrument checks**, per the case selection charter.

## 3. The docket decides

These go to the owner. The docket is `demo-output/website/agenda/docket.json`,
worked through the control room. A decision is recorded on the proposal with
`decided_at` and a `decision_note`, so an approval is a dated artifact rather
than a recollection.

**Compute.**

- Any spend above the free-spend threshold in section 4.
- Any job whose wall time would collide with a filming day or another
  committed use of the box. Precedent: a 13 to 61 hour job was explicitly
  called the owner's decision because it landed on a demo-filming day.
- Anything requiring root, new infrastructure, or an instance change.

**Scope.**

- A new case family below HARD. Charter 3.
- A new mission class with no declared priority ordering. Charter 5, question
  6.
- Retiring or replacing a standard, a gate threshold, or a charter clause.
- An undecidable tie between proposals under charter 1 section 3, or an
  undecidable trade under charter 5.

**Anything public.**

- **Submitting to the challenge.** The standing instruction is that nothing
  goes to the challenge without her, and the submission draft says it twice:
  she proofreads and approves, and nothing moves before that.
- Anything reaching the website, the wall, the certificates or a camera
  surface, where the choice is curation rather than measurement. Precedent:
  when a register finding bore on the wall's wording, the register carried the
  finding in full and recorded that whether and when the wording changes is the
  owner's curation call, not the register's to override.
- Publishing a result with a known caveat, versus clipping a colour scale,
  versus re-meshing. That exact three-way choice was escalated rather than
  taken.
- Anything that leaves the box: a dataset, a ledger, a figure, a preprint.

**Anything irreversible.**

- Deleting or rewriting a record.
- A history-rewriting git operation.
- Anything that would cost more to undo than it cost to do.

**The working tree is shared, and an uncommitted change is somebody's
unfinished work.** Several agents run in one checkout at once. This is not a
theory about the future: commit `5675eb6b` records that the file it changed
"also carries another agent's in-flight dim preflight, edited in the same
working tree at the same time", and commit `ba47307a` exists because two
uncertainty studies were rewritten mid-session by concurrent work and left
uncommitted in the tree, where they were verified by refit and then committed
rather than discarded. Four consequences, and they are the standing rules:

1. **Never `git reset --hard`, `git stash`, `git checkout --` or `git clean`.**
   Each of them destroys uncommitted work that is not necessarily yours, and
   none of them can tell your changes from the changes of an agent that is
   still typing.
2. **Never `git add -A` or `git add .`, and never `git add -A <path>`.** L-12:
   the pathspec form looks targeted and is a directory sweep. One such command
   staged 1,187 files and 25 million insertions, taking `.git` to 513 MB in a
   repository that gets pushed. It happened twice, and two agents independently
   misfiled it as a shared index race, which it was not. Stage explicit file
   paths.

   *[AMENDED 2026-08-11 (cold-start repair). The original text of this item is
   retained above, unedited, per §8.1 of `docs/MEMORY_ARCHITECTURE.md`. Its
   closing sentence — "Stage explicit file paths" — is **superseded and, on its
   own, insufficient**, and it has been so since 2026-08-07. §9.6a measured that
   `git add <paths>` followed by a bare `git commit` still commits the entire
   shared index; §9.6b (added today) measures that even `git commit -- <paths>`
   isolates by FILE and not by AUTHOR. **Read §9.6, §9.6a and §9.6b, which are
   below the `## Related` block, before you act on this item.** This amendment
   exists because a reader who stops at the numbered sections gets the 2026-08-05
   rule and no signal that two later measurements moved it — logged as D-8 in
   `docs/MEMORY_ARCHITECTURE.md` §7.2, opened by the 2026-08-10 memory survey and
   re-filed by both cold-start runs of 2026-08-11 as still fully open.]*
3. **Commit per item.** A small commit that lands is worth more than a large one
   that is still uncommitted when the next agent touches the file. Commit-per-item
   is what survives a shared tree, and it is why every charter revision in this
   set is its own commit.
4. **An unexpected uncommitted change is inspected, never reverted.** Verify it
   against its own evidence and commit it if it stands, which is what `ba47307a`
   did. Discarding another agent's work is irreversible and lands squarely in
   this section.

## 4. How much compute may be used freely

> **PROPOSAL. Nobody has set a number.** The thresholds below are the lab's
> draft, calibrated against decisions the lab has already made rather than
> invented.

**What the record already shows.** The standing defaults for an unmeasured
proposal are 60 core-minutes for a new capability and 20 for a ladder rung. A
480 core-minute run was held for an explicit go rather than launched, and the
reasoning recorded with it is the best sentence in the repository on this
question: launching an eight-hour compute commitment on a misread of one
ambiguous sentence is not a defensible default.

**Proposed thresholds.**

| Band | Core-minutes | Handling |
| --- | --- | --- |
| Free | up to 60 per proposal | Run it. Report it in the morning spend header. |
| Notify | 60 to 240 per proposal | Run it, and name it in the report on the day it runs rather than in the weekly roll-up. |
| Ask | above 240 per proposal | Docket, before launch. |
| Ask | above 480 in one night, aggregated | Docket, before the run that would cross it. |

Two rules that ride with the table.

1. **The threshold is on the estimate, and an estimate that was wrong crosses
   it too.** A job estimated at 50 core-minutes that reaches 240 is stopped and
   escalated, not finished quietly. Otherwise the threshold prices optimism.
2. **The aggregate band is per night, not per agent.** Several agents each
   staying under their own limit is how a night's spend escapes anybody's
   attention.

**The threshold is not the only gate.** A cheap job that is irreversible or
public still escalates. Compute is one axis of three and it is the least
important of them.

### 4.1 The recommendation, made decision-ready 2026-08-05

> **PROPOSED, awaiting her number. Not enacted.** This subsection exists so
> the answer can be one word. "P-7.1: A" adopts the table below with both
> riding rules; "P-7.1: B" keeps the structure and replaces any number she
> names. Until she answers, nothing here binds anything.

**What the record measured since the 1.0 draft, which was written before the
lab ran as a fleet.** The calibration points, each one a decision or a
measurement already on the record rather than an invention:

- The standing defaults remain 60 core-minutes for an unmeasured capability
  and 20 for a rung (compute budget charter, section 3).
- The 480 core-minute TMR closure run is still held for her explicit go
  rather than launched (`BLOCKERS.md` B-3), which is the strongest existing
  precedent for where "ask first" begins.
- The 2026-08-04 working day is the first measured day of supervised
  multi-agent operation: about ten dispatches across two waves
  (`docs/PRODUCT_LIST.md`, the 2026-08-04 and 2026-08-05 entries), whose
  closed items measure roughly 245 core-minutes (185.0 on the
  adjoint-conditioning rebuild, 57.1 on the three discriminators including
  an honestly-ledgered overrun, 2.9 on the supervisor sweep, two closures at
  zero), with **zero budget incidents**: every overrun was ledgered and
  reported, nothing was finished quietly past its estimate.
- The largest single cap dispatched under her standing authorization is the
  Stage 1 CBFS inversion at a hard 600 core-minutes with checkpoint-and-stop
  (`demo-output/website/agenda/proposals/s1-cbfs-field-inversion-run.json`),
  so 600 is the measured ceiling of what she has been willing to wave
  through in one item when the gate and the cap are pre-registered.

**The proposed numbers.** Three ceilings, because the fleet made "per
proposal" insufficient on its own:

| Ceiling | Core-minutes | Derivation from the record |
| --- | --- | --- |
| Free, per proposal | 60 | The standing capability default; a dispatch at or under it has never needed a conversation. |
| Free, per agent per day | 240 | Four free-band items; also the boundary below which every routine measured item of 2026-08-04 fell (185.0 was the day's largest single closure). |
| Fleet, per day, aggregated | 480 | The B-3 precedent read as a fleet number: the spend that was held for an explicit go once is the spend a whole day must not cross silently. The measured fleet day ran at roughly half of it. |

Above any ceiling: the docket, before launch. Between 60 and 240 on a single
proposal: run it and name it in that day's report, not the weekly roll-up,
which keeps the existing notify band. A pre-registered cap she has approved in
an item, like the 600, overrides these by exactly its own amount and nothing
more: approval of an item is approval of its cap, not a new ceiling.

**Both riding rules above are part of the recommendation and matter more than
the numbers**: an estimate that turns out wrong crosses the threshold too (a
job estimated at 50 that reaches 240 is stopped and escalated, not finished
quietly, otherwise the threshold prices optimism), and the aggregate band is
per day per fleet, never per agent, because several agents each under their
own limit is how a day's spend escapes attention. The 2026-08-04 record shows
the discipline the first rule asks for is livable: the 57.1 measured against
45 filed was ledgered and reported as an overrun, item by item, rather than
absorbed into a total.

**What this does not change.** A cheap job that is irreversible or public
still escalates; the compute audit still gates launch on capacity; and the
free bands say nothing about the shared-tree rules in section 3.

## 5. The waiting list

**Blocked work lives in `demo-output/website/agenda/BLOCKERS.md`**, whose own
subtitle is the standard it holds itself to: a single source of truth for work
that cannot proceed on this box, where everything has been verified blocked
rather than assumed, and each entry names the exact unblock action.

Three requirements, all already met by the current entries.

1. **Verified blocked, not assumed.** An item goes on the list after somebody
   established it cannot proceed, not after somebody expected it could not.
   This is P1 pointed at the docket: run the cheapest control before publishing
   the doubt.
2. **Every entry names its unblock.** Not "waiting on credentials" but "attach
   an instance role with these two read-only permissions, or paste the numbers
   and they are recorded as reported-by-owner".
3. **It is a separate file for a structural reason.** `agenda.save_docket()`
   rewrites the docket's proposal list wholesale, so a blocker parked as a
   top-level key there would be silently destroyed by the next refresh. The
   separation is deliberate and the file says so.

**A blocker does not block the neighbouring work.** The B-3 precedent is the
model: the ladder it sat on proceeded, because that ladder was never gated, and
only the specific expensive run was held. Blocking a whole track on one
ambiguous item is its own failure.

## 6. Escalate rather than work around. Always

**A refusal by the permission layer is escalated, never routed around.** L-18
records an agent that tried to stop a bad job, was refused, and escalated
instead of finding another way. That was the correct behaviour and the lesson
says it is worth as much as the catch. A permission layer that can be worked
around is not a permission layer, and an agent that works around one has made
itself the last check.

**Ambiguity escalates.** If an instruction has two readings and they differ in
cost or reversibility, the lab does not pick the convenient one. B-3 again.

**Silence is not approval.** No standing instruction becomes an approval by
having gone unanswered. An item waited on stays on the waiting list.

**Scaffolding is not approval.** L-18's other half. A case directory on disk,
with real scripts and a real mesh dated from earlier work, reads as permission
and is not.

**Constraints do not propagate by themselves.** L-18's first half, and this one
belongs here because escalation is a supervisory act. An agent that can spawn
agents is a supervisor, and a supervisor who omits a constraint has removed it.
Every brief restates the budget, the no-compute status, the commit discipline
and the resource rules, however obvious they seem. The literature review that
learned this had "do not run any solver" in its own brief and never passed it
down.

## 7. What escalation looks like

A docket item, not a conversation. It carries:

- **The decision**, stated as a choice between named options, not as an
  open question. "Publish with the caveat, clip the colour scale, or re-mesh
  at a stated cost" is a decision. "What should we do about the figure" is not.
- **What each option costs**, in core-minutes and in what stays unmeasured.
- **What the lab recommends and why.** Escalating without a recommendation
  spends her attention on work the lab could have done.
- **What proceeds regardless**, so she knows the escalation is not holding
  more than it needs to.
- **The unblock action**, if it is a blocker rather than a choice.

**Escalate early and once.** An item raised before the compute is spent costs a
sentence. The same item raised after costs the compute as well.

## 8. An instruction is answered, not only obeyed

Section 6 covers the instruction the lab must not work around. This section
covers the instruction the lab did exactly as asked and never mentioned again.
It sits in this charter because acknowledging an instruction is the same act as
escalating one: both are the lab reporting back up rather than deciding
quietly.

> **A stated instruction is repeated back, and the repetition carries the
> number that shows it was honoured.**

**Three acts honoured an instruction without saying so**, and each was found by
a human reading a transcript rather than by any check. A coarse mesh was held
to, a model was picked for a stated reason, and a stopping target was met. In
all three the work was right and the record was silent. **The echo is the
product's signature, so an unechoed instruction is a missed beat every time**,
not merely an unpolished one. Docket `w7-instruction-echo-is-a-check`.

The shape that works, from the three repairs:

- **The echo waits for the measurement.** The coarse-mesh instruction is
  repeated back only once the mesh has been counted, so what comes back is a
  cell count and the channel that carries its price, rather than a promise to
  comply. Commit `6880e4f3`.
- **A number the instruction named is answered with the number that met it.** A
  stated stopping target is answered with the iteration at which it was first
  reached, not with the fact that it was reached. Commit `66bc8d9b`.
- **A threshold that is a review mark and not a gate says which it is** rather
  than being honoured silently as though it were a gate. Commit `ed4bb19d`.
- **The echo survives the transcript.** An acknowledgement made once, out loud,
  is gone when the transcript is. Where the decision matters it lands on the
  sealed page too.

**When the artifact and the stated intent disagree, both are stated and the
artifact is not silently preferred.** A request named a 15 degree configuration
and the body that arrived measures 25. The act solved what it was handed, which
is almost always right, and said so once on camera; the sealed page now carries
it as a row, "Configuration Solved: 25 degrees as measured, overriding stated
15 degrees". Commit `6880e4f3`.

The rule and its limit, and the limit is the point:

1. **The artifact wins by default**, because it is the primary evidence and
   L-16 is the standing reason to prefer it over anything derived.
2. **The lab cannot know the user did not attach the wrong file.** That is the
   one thing the artifact cannot tell it. So the disagreement is stated in the
   record at the moment it is noticed, in both terms, and the run proceeds.
   Proceeding is correct. Proceeding silently is not.
3. **A disagreement that would change what the work is for escalates instead.**
   Section 6: an instruction with two readings that differ in cost or
   reversibility does not get the convenient reading. A slant angle changes the
   answer and not the mission, so it is recorded. A body that is not the body
   she asked about changes the mission, and that is a docket item.

## 9. OPS. How a fleet survives its own death

Added 2026-08-05, from the two days on which the lab first ran several agents
at once and lost all of them three times. It is here rather than in a standard
because every rule below is about what an agent must do BEFORE it can be
stopped without warning, and stopping is this charter's territory.

**What happened, so the rules are read as measured rather than prudent. Three
fleet deaths, three different causes, in about 46 hours:**

| When | What killed it | What it took |
| --- | --- | --- |
| 2026-08-04, ~18:53Z | the account session limit | the supervisor and all four working agents at once, mid-solve; the box then auto-stopped overnight and the orphaned containers went with it |
| 2026-08-05, 15:08Z | the process itself exited | the fleet again; the detached solves survived and kept running unowned |
| 2026-08-05, ~17:20Z | the weekly limit | the fleet again, seven minutes before the credits came back |

**Scientific loss across all three: zero.** Not once, three times, which is
what makes it a rule rather than a piece of luck. The reason is rule 1 in
every case: every agent had committed its pre-registration, its predictions,
its thresholds and its caps before launching any compute (`e6321e95`,
`99f5d41d`, `73fa6a33`, all 2026-08-04). What each death cost was compute
time and collection, both of which are re-runnable, and nothing else.

**Three is also the number that settles the argument this section could
otherwise have had with itself.** One survival is an anecdote and two is a
coincidence; three deaths from three unrelated causes, all survived by the
same discipline, is a measurement of the discipline rather than of the
causes, and none of the three causes was predictable from inside the box.
That is the whole case for making rule 1 mandatory instead of advisable.

The account of all three lives in `docs/PRODUCT_LIST.md`'s changelog under
2026-08-05 and in the supervisor's own memory, and **it is not in
`LESSONS.md`**, which is a gap in the record rather than a reason to soften the
rules: the entries this section leans on are L-18 (a constraint that is not
restated is removed) and L-27 (a run that decides a gate retains its
artifacts).

1. **Pre-register before compute. Mandatory, no exceptions for short runs.**
   Predictions, thresholds, caps and labels are committed BEFORE the solver
   starts, not written up afterwards. This is what made three fleet deaths cost
   nothing but core-minutes, and it is P2 with a second job: a prediction
   committed early is also a crash-proof record of what the run was for. The
   exception a short run seems to earn is exactly the one the record refuses:
   the 15:08Z death landed mid-afternoon on a working day with no warning of
   any kind, and a run's length has nothing to do with when a limit expires.
2. **A solver runs detached and ledgers itself as it goes.** Launch through
   `setsid` (or a container), never as a foreground call, because a foreground
   solve has been killed by an external SIGTERM with no error and no OOM while
   a detached one has never been. And the run writes its own cost and progress
   rows while it runs rather than at collection, so a dead collector loses the
   summary and not the measurement.
3. **Hold the box twice during a campaign.** `scripts/session_keepalive.sh on`
   follows the session and self-expires; `scripts/filming_keepalive.sh on 24`
   survives the session dying. Arm both, because the failure they cover is
   exactly the case where the session is gone and the compute is not. Arm the
   session hold as the first command of every working day. Neither script
   disables the auto-stop, which is the owner's cost control and stays.
4. **Check before you resume, and NOT with `pgrep` first (L-41, corrected
   2026-08-10).** A completion notice with no result does not prove an agent
   is dead, and a process sweep cannot prove it either: fleet agents execute
   inside the SDK server, so a busy peer is INVISIBLE to `pgrep`/`ps | grep
   claude`. That mistake collided two agents on one rung. Ask in this order:
   (a) `git log --since=<minutes>`: a working agent commits, and a
   pre-registration appearing after your dispatch is proof of a live peer;
   (b) run-directory and case-directory mtimes (`find <runs> -mmin -10`): a
   live solve writes constantly under no matching process name; (c) the
   docket/inbox claim state. Only then process sweeps, which answer "is a
   SOLVER running", never "is an AGENT working". Prefer resuming the
   incumbent over spawning a rival: two agents on one item produce two records
   for one run. The original text follows, superseded:
   ~~Run `pgrep -af 'claude --resume'` and look for
   fresh writes in the agent's own files first: resuming a live agent spawns a
   second incarnation working the same task in the same tree, which is section
   3's shared-tree problem arriving from a direction nobody guards. And
   inventory the containers (`sudo docker ps`) before relaunching anything: a
   detached solve usually survived the death that killed its owner, so the
   agent reattaches rather than restarts.
5. **Watchers belong to the chief, not to the agent.** An agent that ends its
   turn "waiting on a monitor" has no monitor, and the completion notice is the
   proof, because it only fires once the agent has no live background children.
   Five occurrences in four days, including three after the agent was
   explicitly told to poll inline. So the supervisor arms the background watch
   on the container or the PID, lets the agent park, and resumes it with the
   outcome already in the resume message. One resume per solve.

**The one-line test for all five**: if this process died right now, what would
have to be re-run, and what would be unrecoverable? Anything in the second
category is a violation of rule 1.

## 10. Enforcement

- The agenda machinery enforces the veto structurally. Nothing in it launches
  compute, and status changes on the owner's action.
- The compute audit gates approved work on measured capacity and produces
  `approved-queued` rather than launching into a full machine.
- `BLOCKERS.md` is the waiting list and its entries carry unblock actions.

Not enforced mechanically: the free-spend thresholds, the aggregate nightly
band, and every judgement in section 3. Those are the ones that matter most and
none of them has a check, which is the honest state of it.

## Related

- `docs/charters/COMPUTE_BUDGET_CHARTER.md`. The budgets the thresholds refer
  to, and the billing blocker.
- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. Where an undecidable tie
  originates.
- `docs/charters/RESULT_PRIORITY_CHARTER.md`. Where an undecidable trade
  originates.
- `docs/charters/REPORTING_CHARTER.md`. The waiting list section of the morning
  report.
- `LESSONS.md` L-1, L-12, L-16, L-18, P1.

### 9.6. Staging is by explicit path, never by sweep (added 2026-08-05, supervisor)

Two agents' staged files were swallowed into other agents' commits in one
afternoon because concurrent workers ran `git add -A` / `git add .` on the
shared tree. Both times the content survived and the narrative did not: the
files landed under another commit's message, and a provenance note had to be
committed after the fact to keep the log auditable (`ecb5bdbe` is the pattern).

Rule: on a tree where more than one agent works, every commit stages its files
BY EXPLICIT PATH. `git add -A`, `git add .`, and `git commit -a` are forbidden.
An agent that finds foreign hunks in a file it must commit stages its own hunks
only (the split-patch precedent from the warp-carry session). A commit whose
message does not describe every file in it is a record defect, same class as a
mislabeled measurement.

#### 9.6a. Amendment, 2026-08-07: staging by path is not committing by path

Four collisions in one day proved 9.6 as written insufficient: `git add <paths>`
followed by `git commit` still commits the ENTIRE shared index, sweeping every
sibling's staged files (6cd6b5bb swallowed a 40-page report update and named
only the smaller riders; d52446e7 and 770436f9 have their own provenance
repairs). The rule sharpens to its mechanically safe form: on the shared tree,
commit with `git commit -- <paths>` (or `--only`) in a single step, so the
commit contains exactly the named paths regardless of what else sits staged.
`git add` remains fine; the bare `git commit` after it is what the rule now
forbids. Every provenance-repair commit today followed the ecb5bdbe pattern;
with this amendment they should stop being needed.

#### 9.6b. Amendment, 2026-08-11: a pathspec isolates by FILE, not by AUTHOR

9.6a made the commit contain exactly the named paths. It does not make the named
paths contain exactly your own work. On 2026-08-11 the chief committed
`docs/PRODUCT_LIST.md` by pathspec, under a message describing one finding, and
the diff also carried a concurrent agent's uncommitted work **in that same
file**. Nothing in 9.6 or 9.6a could have prevented it: both rules answer *"which
files am I committing?"* and neither answers *"who else wrote in them?"*

The rule as it must now read, in two parts:

```
git add <paths>
git commit -m "..." -- <paths>      # the SCOPE
git diff <path>                     # the CHECK, read it before you commit
```

**The check is not optional on a shared, high-traffic file**: a changelog, a
status record, a checklist, an index. Those are exactly the files a supervisor
writes most often and exactly the files everyone else is writing to at the same
time, so this is where the scope rule has least protection and most opportunity
to fire. If the diff contains hunks you did not write, stage your own hunks only
(the split-patch precedent in 9.6) rather than committing them under your
message.

The narrative and the incident are `LESSONS.md` L-57. **The line count in that
lesson was itself corrected on 2026-08-11**, first written as 59 lines, which
was the commit's total insertion count, then recounted by hunk as 34, so cite
L-57 for the rule rather than restating its figure here. That correction is the
rule applied to itself: read the diff, not the summary of it.

##### 9.6c. Do not "leave it uncommitted to be polite": that fails in the other direction

**Added 2026-08-11, same day, after the considerate response to 9.6b turned out to
be the wrong one.** An agent found another agent's rows in `docs/DOCKET.md`,
correctly declined to sweep them under its own message, and **deliberately left
the file uncommitted**. The other agent then committed the file, and swept *its*
two rows in, under a message about something else entirely. Nothing was lost; the
attribution was.

**Leaving a shared file dirty does not protect your work. It hands the decision to
whoever commits next**, and on a tree with several agents that is a matter of
seconds. The polite move and the safe move point in opposite directions, and the
polite one loses.

**The procedure, which is short and has been executed:**

```
git diff <path> > /tmp/full.patch          # everything currently uncommitted
# keep only the hunks you wrote: split the patch, do not eyeball it
git apply --cached /tmp/mine.patch         # stage YOUR hunks only
git diff --cached --stat                   # confirm what is staged
git diff --cached | grep -c '<their marker>'   # confirm theirs is NOT
git commit -m "..."                        # the index holds only your hunks
```

Two notes that make this safe rather than clever:

- **Verify the index is empty before you start** (`git diff --cached --name-only`).
  The final `git commit` has no pathspec, which is normally forbidden. It is safe
  *only* because the index was empty and you put exactly your own hunks in it.
  Check that, do not assume it.
- **Say in the commit message that you did this and why.** A commit that touches
  part of a file leaves a reader wondering what happened to the rest; one sentence
  removes the puzzle and records that a peer's work was deliberately left in place.

**The general form:** on a shared tree, *inaction is not neutral*. Declining to
commit is itself a choice about who gets to attribute your work, and the default
answer is "whoever runs `git add` next."

*Added 2026-08-11 by the cold-start memory repair, on the finding that
`docs/MEMORY_ARCHITECTURE.md` §4 step 0 sent readers to this charter for a rule
the charter did not yet carry. Two independent cold-start runs on 2026-08-11
filed it. Version header bumped to 1.4 in the same commit — not bumping it for
9.6 and 9.6a is half of why D-8 exists.*

## Amendment record

**Version 1.6, dated 2026-08-17. A style amendment, measured at frame `101079fd`.**
The sections above were brought to the owner's standard for a durable
record: em dashes and en dashes replaced by ordinary punctuation, and the
result of each replacement read back against the clause it sits in.

| what the amendment did | figure |
| --- | --- |
| em dashes replaced in the live sections | 13 |
| en dashes replaced in the live sections | 0 |
| em dashes left standing inside dated records | 6 |
| en dashes left standing inside dated records | 0 |
| clauses opened and declined, listed below | 2 |
| lines whose number changed above this section | 0 |

**No clause was added, removed, widened or narrowed, and no modal, scope or
tense inside a clause was altered.** Both the counts above and the gates were
taken in a detached worktree held at frame `101079fd`, so that a peer's
concurrent commit could not be read as part of this batch. The gates run either
side of the edit were `scripts/check_verdict_cells.py` with and without
`--selftest`, `scripts/check_absolutes.py`,
`scripts/check_normative_clauses.py`, `scripts/withdrawal_sweep.py`,
`scripts/self_audit.py` and `scripts/lab_check.py --no-tests`; the `sdk/tests`
suite was run either side in the live checkout. No gate moved its verdict. `check_absolutes.py` moved its verdict
COUNTS and not its verdict, and the movement was traced to the
sentences of this record rather than to the sections above.

**The line numbering above this section was held fixed on purpose.** Other
records cite this directory by line, and one of those citations sits inside an
executable check. An amendment that inserted its own changelog at the head of
the file would have moved the cited lines below it, so this record was appended
at the foot instead. The version-history entries above stand unedited, because their
figures describe the versions and the dates they name.

**What was opened and left alone.**
1. §3 item 2's amendment block records the 2026-08-05 rule and the two measurements that moved it. It was left byte-identical, dashes included.
2. §9.6 item 4's struck original is retained under *"the original text follows, superseded"*. The word carries the strike, so it was left in place.

## Amendment record, continued: silent-background convention (2026-08-23)

**Dated addendum, 2026-08-23, appended at the foot; append-only. One standing
convention added on the owner's directive. No clause above is altered, widened
or narrowed; no line above this section changed number; the header's version
line is deliberately left untouched, because this addendum inserts nothing and
edits nothing above itself.**

Sanaa's directive, verbatim (2026-08-23): "There needs to be added to all
the .md convention files that all agents must always act in a silent way on
the background without showing bash or ssh on the screen, the screen must
always remain clean with only discussion and results."

In force for every agent this charter binds, and recorded lab-wide as
`CLAUDE.md` rule 16: all heavy work (bash, ssh, compute, file surgery) runs
inside background lanes or subagents, never as top-level tool calls in the
user-facing session when avoidable; user-facing reports carry discussion,
numbers and verdicts only, never pasted terminal output, raw logs or command
transcripts (quote the specific value with its artifact path, not the dump it
came from); supervisors enforce this on their lanes, condensing a transcript
before relay rather than forwarding it raw. Honest caveat: the Claude Code UI
renders whatever tool calls the top-level session makes, so the convention is
kept by pushing work into background agents; that delegation, not a display
setting, is what keeps the screen clean.

| what the amendment did | figure |
| --- | --- |
| standing conventions added | 1 |
| clauses altered, widened or narrowed | 0 |
| lines whose number changed above this section | 0 |
