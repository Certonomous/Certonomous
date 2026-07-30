# Certonomous Escalation Charter

Version 1.0, dated 2026-07-30. Governs what the lab decides alone and what goes
to the owner. It binds unattended work, which is where the question actually
arises.

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

## 8. Enforcement

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
- `LESSONS.md` L-1, L-18, P1.
