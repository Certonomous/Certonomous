# Certonomous Supervision Charter

Version 1.4, dated 2026-08-22. Governs who supervises what, which checks a
supervisor performs with their own eyes, and which model each kind of agent
runs on. It binds the fleet's org chart the way the case-selection charter
binds the queue: the structure holds when nobody is watching, and a check that
was delegated when this charter says it may not be is a violation whether or
not the delegate got it right.

Everything here traces to the owner's instruction of 2026-08-07, which
extended her standing delegation doctrine of 2026-07-26 ("the chief session is
the global supervisor; everything else goes to designated agents even when she
does not say so; a liaison answers her commands-and-prompts requests") from
one supervisor over a flat fleet to one supervisor over four standing family
supervisors. Nothing in the 2026-07-26 doctrine is weakened; section 4 carries
it forward whole.

## 1. The line

> **Every big task family has a standing supervisor, and four kinds of check
> are done by a supervisor personally or they have not been done.**

The test is answerable after the fact: for any measurement-script change,
crash, big claim or compute launch in the last week, name the supervisor who
checked it and the record of the check. "An agent reported it clean" is not an
answer to that question. It is the thing the question exists to catch.

## 2. The four families

Each of these gets a standing family supervisor agent. The list is the
owner's. Adding or merging a family is hers, not an argument. The scope
column's wording is the lab's rendering of what each family already contains
on the record, and it is the one thing in this charter that is not her
instruction verbatim; redrawing a boundary is a one-line edit and hers to
order.

| family | scope |
| --- | --- |
| DAFoam and adjoint | the gradient ladders, FD verification, the defect arcs, mesh warping, anything whose product is a derivative |
| Closure and UQ | the closure challenge, field inversion, model-form studies, the three uncertainty channels and their machinery |
| Cases and campaigns | case families, refinement ladders, campaign records, the gate table, the wall's evidence |
| Infrastructure and standards | the harness, the monitors, the audits, the standards documents, the fleet's own operations |

**A family supervisor does three things, and the order is the priority
order.**

1. **Issues family guidelines.** Standing written rules for how work in the
   family is staged, measured and recorded, in the family's own records,
   iterated the way the charters are: on incident, with a date, never
   weakened without naming the decision that forced it.
2. **Personally performs the four checks of section 3.** These are the
   reason the role exists and they may not be delegated downward, for the
   same reason the chief's rulings were not: a check whose result is relayed
   is a summary, and section 10 of the verification charter is about what
   summaries do.
3. **Reports to the chief supervisor.** Findings, verdict-shaped questions,
   and anything on the chief's retained list in section 4, escalated per the
   escalation charter rather than settled in the family.

A family supervisor supervises. It does not run the family's solves, write
its GUI, or fetch its papers; those go to the family's working agents exactly
as the delegation doctrine already routes them.

## 3. The four personal checks

"Checked personally" has a worked pattern already on the record: the chief's
rulings in `SUPERVISOR_RULINGS.md`. R11 adopted the shipped-vs-patched
grading policy only after two supervisor sweeps (the rotation patch, the A4
decomposition) had verified the regrades produced under it with the
supervisor's own reads. R4 regenerated the wall only after re-deriving the
contested row through the builder's own function. R10 was corrected the same
day it was written because its author checked the stake and found it false.
That is the standard: the supervisor opens the artifact, and the ruling cites
what was opened. The four checks below are that standard made a duty.

1. **Code diffs on measurement scripts.** Any change to a script that
   produces, grades or aggregates a measured number is read as a diff by the
   family supervisor before its output is believed. A measurement script is
   an instrument, and an instrument change without a supervisor's read is an
   uncalibrated instrument.
2. **Crash triage: a crash is guilty until shown to be a mere bug.** A
   crash, a divergence or a refused solve is treated as a finding about the
   case, the method or the toolchain until triage demonstrates otherwise.
   The two exemplars are both from F8. The init-arm divergence read like a
   crashed run (forces to 1e99 behind a 1.4e-8 residual, a live S10
   specimen), and triage of it produced the hurricane: potentialFoam's
   makeAbsolute had baked the frame's solid-body sweep into the whole-domain
   MRF zone, roughly 150 m/s against a 7 m/s inflow, a real mechanism with
   source-line citations, not a bug to be rerun past
   (`demo-output/website/campaign/F8_MRF_HAND2001_GATE.md` sections 14 and
   15). And S10 itself, divergence behind a converged residual, entered the
   monitor standard because one such crash was read instead of shrugged at.
   A crash written off without triage is a discarded measurement.
3. **Big-claim verification before belief.** Any conclusion large enough to
   change a family's direction gets a supervisor's code sweep and an
   independent diagnostic before it is repeated upward. This is the standing
   adversarial-verification discipline: the claim is assumed wrong until it
   has been defended against its own evidence.
4. **Pre-registration presence before compute.** No family compute launches
   without its pre-registration committed. The escalation charter's OPS
   section measured this rule across three fleet deaths in 46 hours: the
   reason scientific loss was zero every time was that the pre-registrations
   were committed before the compute was. The family supervisor checks the
   commit exists, not that somebody meant to write one.

## 3a. Withdrawal duty attaches to the ROLE, not to the session that wrote it (Katie, 2026-08-11)

> **A superseded entry whose author is gone is withdrawn by the current family
> supervisor, within the cycle. A weekly sweep asserts zero unowned supersessions.**

**The standing rule was that a superseded entry is withdrawn by its author.** That was right
in spirit, because the author knows what they meant, and **structurally broken**, because
authors here are sessions and sessions end. When the author is gone the rule names nobody,
and a rule that names nobody is not enforcement; it is a refuted claim staying published
with a note explaining that someone ought to remove it.

**The instance, 2026-08-11.** A peer session published a correction, a second session
refuted it by execution, and the correction's dependent gate had already been re-based on
the strength of it. The peer session then ended. Under the author rule the withdrawal had
no owner at all, so a claim known to be false and a gate known to be uninformative both sat
live in the record, not through disagreement or backlog, but because the rule pointed at
a ghost.

**Why the role and not "whoever finds it".** Discovery is not duty. Anyone may notice; if
noticing were the assignment, the item would be everybody's and therefore nobody's, which
is the failure this rule exists to close. The **family supervisor for the record's family**
owns the withdrawal, and the chief owns it where no family does.

**What "within the cycle" means.** Before the family's next reporting cycle closes. Not
"soon": a superseded claim's cost is exactly the time it spends readable, and a reader
cannot tell a claim awaiting withdrawal from a claim in force.

**The sweep is the enforcement, and it is the part that must not be skipped.** Weekly,
assert **zero unowned supersessions**: every withdrawn, retracted or superseded entry has a
named current owner, and every refutation filed against a live claim has a withdrawal
either done or assigned. A rule without a sweep is a preference. Anything the sweep finds
unowned is assigned by the chief on the spot, and the assignment is the deliverable, not a
plan to assign.

**The sweep, as of `94d6510b`, is `scripts/withdrawal_sweep.py`.** Run it weekly with no
arguments. Between this clause landing (2026-08-11) and that commit (2026-08-14) the rule
had no executable form, which is the state this clause's own last paragraph describes. The
script states its definitions, its frame and its reach in its own output, returns
PASS / FAIL / **UNKNOWN** (an empty candidate set is UNKNOWN, never PASS), and plants both
halves of L-84's control on every run. Its first executed result, at `94d6510b`, was
**FAIL on one**, `campaign/F5bc_unsteady_statistics.md:48`, filed as docket **C4**.

Two things the sweep does not do, so nobody reads a PASS as more than it is. It gates on
this clause's own three words (*withdrawn, retracted, superseded*) and reports
`[AMENDED` / `[CORRECTED` separately; and it can only see supersessions that carry a
marker, so a silent edit or a deletion is invisible to it. The script's `REACH` block
enumerates six such classes.

## 4. What the chief supervisor retains

The chief supervises the supervisors. Retained, and not delegable to a family
supervisor:

- **Scoring-call authorization.** No agent at any level makes a scoring call
  on the challenge; the chief authorizes, and the outward act stays the
  owner's per ruling R9.
- **Cross-family arbitration.** A conflict between two families' guidelines,
  or a case that two families both claim, is the chief's, and an unresolvable
  one goes to the docket.
- **Negative-verdict reviews.** Every gate FAIL, NO-GO, no-verdict and
  refuted prediction gets the review the verification charter's section 16
  now requires, conducted at chief level. The inaugural instance is
  `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`.
- **List and board custody.** The daily list and the research board are
  written by the chief, per the owner's standing list protocol: cross off
  only what is fully done, add one item per cross-off, end-of-day list to
  her.
- **Everything the 2026-07-26 delegation doctrine already assigns.**
  Research direction, trust verifications, new models, dispatch, synthesis.
  The liaison still answers her commands-and-prompts requests; that route is
  unchanged by this charter.

## 5. Model designation

The rule is one sentence and it is the owner's:

> **Family supervisors and adversarial verifiers run on Fable. Solver,
> bookkeeping and liaison agents inherit the session default.**
> ~~**Long-form technical writing goes to Opus.**~~
>
> **[THIRD SENTENCE STRUCK 2026-08-12, in place and kept, per
> `docs/MEMORY_ARCHITECTURE.md` §8.1. It is superseded for the execution of
> Katie's order of 2026-08-12 only. The standing rule is undecided and hers to
> set: see §5a, which states the two options and does not choose between them.
> The first two sentences are NOT struck and remain in force.]**

The Opus clause has a precedent rather than a theory: the two LaTeX reports
she asked for on 2026-08-05, the closure-challenge campaign and the DAFoam
defect case, were dispatched to Opus agents and that is the pattern
(`docs/PRODUCT_LIST.md`, 2026-08-05 changelog). The Fable clause exists
because the four personal checks of section 3 are judgment work, and putting
them on the strongest available model is the same decision as putting the
chief there. The inherit clause exists so the designation rule costs nothing
on the work that does not need it.

*[This paragraph is retained unstruck although the clause it explains is
struck. It is the recorded reason the Opus clause existed, and that reason is
a direct input to the ruling §5a leaves open; deleting it would remove the
evidence on one side of a decision that has not been made yet.]*

A dispatch that overrides this rule says so in the brief and says why. A
silent override is a violation, in either direction: an adversarial verifier
quietly downgraded is the obvious failure, and a solver agent quietly
upgraded is a spend nobody approved.

## 5a. The Opus clause is struck for one order; the standing rule is Katie's (amendment 2026-08-12)

> **Katie's order of 2026-08-12 assigns the drafting of standing records to
> [FABLE]. That order governs the execution of that order. It does not settle
> what §5 requires from tomorrow, and neither does this amendment.**

**(a) What the struck clause required.** *"Long-form technical writing goes to
Opus."* On its face that covers charter, conventions and LESSONS drafting,
which is long-form and technical. It is not a preference in this charter; §5
states the whole designation rule is the owner's.

**(b) What the 2026-08-12 order assigns.** The order's role class for [FABLE]
is recorded as *"research / scientific writing"*, and its item H6 reads
*"[FABLE] drafts / [HAIKU] files: LESSONS, conventions, charters"*
(`docs/HANDSHAKE.md` at `33f36365`). Both cannot be honoured at once, which is
the contradiction a grader raised at `10cf7f21` and the H4 allocation audit
recorded as item 4 before any of it executed, flagged before dispatch and not
after, which is why nothing has to be undone.

**(c) Which one governs today.** The order does. Katie is the principal; §5's
rule is hers, and a later instruction of hers outranks this charter's rendering
of an earlier one. The dates are worth stating exactly, since they are the
whole basis of that sentence. The designation rule is hers and dated
**2026-08-07** (`docs/charters/PROPOSALS_OPEN.md:1105`: *"the model
designation rule. Hers, 2026-08-07"*). The 2026-08-05 LaTeX reports are the
precedent the Opus clause cites, not its authority. 2026-08-11 is only the
date of the v1.1 bump that carried the rule forward. The order is dated
**2026-08-12** and is the latest of them. Chief ruling at
`33f36365`. Note that §5's last
paragraph is unstruck and live: *"A dispatch that overrides this rule says so
in the brief and says why."* On that reading the order is not a violation of
§5 at all but a declared override of the kind §5 already provides for. **What
§5 has no mechanism for is making a declared override standing.** That is the
actual gap, and it is the thing the options below are about.

**(d) The standing rule is Katie's to set, and it is still open.** The two
options, with the honest consideration on each side and no recommendation:

**Option A. Keep the clause, treat the order as a dated override.** §5's third
sentence is restored; Katie's order of 2026-08-12 stands as a declared,
order-scoped override under §5's existing override paragraph, on the record
with its date and reason.
- *For:* the designation rule keeps one testable line, and it survives changes
  in which model is strongest or available: it names the task class, not the
  fleet roster. The recorded reason for the clause is a decision Katie made on
  evidence: the two LaTeX reports of 2026-08-05 (`docs/PRODUCT_LIST.md`,
  2026-08-05 changelog). Overrides stay individually visible and auditable.
- *Against:* if writing-goes-to-Fable is the intended norm, every future day's
  order must re-declare the override, and a rule overridden by default is
  scenery, which is exactly what `docs/charters/README.md` says disqualifies a
  clause from this directory. §7 already admits nothing mechanical checks model
  designation, so "declared in the brief" is worth only what the brief is worth.

**Option B. Re-designate: long-form technical writing goes to Fable.** §5's
third sentence is replaced rather than restored; Opus keeps engineering,
execution and launches.
- *For:* it matches the fleet's role classes as the 2026-08-12 order states
  them, and it settles the conflict once instead of re-litigating it every day.
  It also makes §5 internally coherent: the Fable clause already exists because
  the §3 checks are judgment work, and composing a charter or a lesson is the
  same judgment work rather than a different kind of task.
- *Against:* it discards the evidence the Opus clause was built on without
  replacing it with evidence of the same kind. The 2026-08-05 precedent is
  about 24- and 27-page submission-grade LaTeX reports; the 2026-08-12 order is
  about standing-records drafting. Generalising the second over the first
  decides something the order did not visibly consider.

**The rider, which attaches either way.** "Long-form technical writing" is one
phrase covering two jobs that this conflict has now shown apart: submission-grade
reports for outside readers, and the lab's own standing records. Katie may rule
them together or split them, and a split is a coherent third shape of either
option rather than an argument against it.

**(e) Why an Opus agent drafted this, and why that is not incidental.** This
amendment was written under §5 as it stood *before* the strike, by an [OPUS]
agent dispatched for that reason (`33f36365`). Had the disputed clause been
suspended first and the amendment drafted under the new assignment, the clause
would have been used to adjudicate the dispute about itself, and the resulting
document would be evidence of nothing. The ordering is the load-bearing part
of this record: the pre-amendment rule was obeyed exactly up to the moment it
was amended.

**What is not on the record, stated rather than papered over.** The 2026-08-12
order exists in this repo, as of `41e813df`, only as `docs/HANDSHAKE.md`'s
rendering of it (`33f36365`) and the copy of that rendering in
`docs/H4_ALLOCATION_AUDIT.md`. A tracked-file search at that commit for the
order's own wording returned nothing: there is no verbatim artifact of the
order itself. Every quotation of it above
is from the rendering, and the rendering is the lab's own words for what she
said. If the rendering is wrong about the role classes, this amendment inherits
that error, and Katie's ruling on (d) supersedes it either way.

**Downstream, not fixed here.** As of `41e813df`, four surfaces quote §5 or its
version literal and read stale against this amendment:
`docs/charters/PROPOSALS_OPEN.md:37`,
`docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md:113`,
`docs/PRODUCT_LIST.md:512` (all three already docketed as D37, which caught
them still citing v1.0 after the v1.1 bump) and
`demo-output/website/AGENT_MODEL_DISTRIBUTION.md:7`, which quotes the struck
sentence in full as a live standing rule and is *not* in D37's list. They are
left untouched deliberately: this amendment's scope is §5, and a drafting agent
propagating a rule that is still open would be spreading a decision Katie has
not made. They are named here so the gap is a known gap.

## 6. Worked examples

**The pattern, before the charter.** R11: a grading convention was already
load-bearing across every regrade since 2026-08-01, and it was adopted as law
only after two supervisor sweeps had personally verified regrades produced
under it. The convention did not become policy by being used; it became
policy by being checked.

**Crash triage paying for itself.** F8's steady-MRF line closed three ways
(geometry exonerated to the millimeter, frame terms audited to source lines,
initialization tested single-variable), because every crash and every
diverged arm was triaged as a suspect rather than rerun as a nuisance. The
hurricane finding, which killed a borrowed "cure" that was actively toxic in
a whole-domain MRF zone, exists only because the divergence was treated as
guilty.

**What the charter forbids.** A family supervisor who receives "the
measurement script change is fine, I tested it" from the agent who wrote it,
and files the family report on that sentence, has violated check 1 even if
the change was fine. The delegate's test is evidence; it is not the
supervisor's read.

## 7. Enforcement

- Section 3 check 4 is partially mechanized already: `scripts/launch_solve.sh`
  is the only sanctioned way to start a long solve, and the pre-registration
  commit is checkable in the git log after the fact by anyone.
- The negative-verdict review has a named artifact per instance, so its
  absence is a findable gap: a FAIL or NO-GO on the record with no review
  citing it fails the section 1 question.
- The rest is review discipline today, and this charter says so rather than
  pretending: nothing mechanical verifies that a measurement-script diff was
  read by a supervisor, that a crash was triaged before dismissal, or that a
  dispatch used the designated model. Those are checked by asking the
  section 1 question, and the honest state is recorded here so that the gap
  is a known gap.

## Related

- `docs/charters/VERIFICATION_CHARTER.md`. Section 16, the negative-verdict
  review this charter's section 4 assigns to the chief.
- `docs/charters/ESCALATION_CHARTER.md`. Section 6 on constraints not
  propagating; section 9 OPS, whose pre-registration rule section 3 check 4
  enforces at family level.
- `docs/charters/SUPERVISOR_RULINGS.md`. R1 through R11, the worked pattern
  for what a personal check looks like on the record.
- `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`.
  The inaugural negative-verdict review.
- `docs/PRODUCT_LIST.md`. The 2026-08-05 changelog entry that is the Opus
  precedent.

## Amendment record

**Version 1.3, dated 2026-08-17. A style amendment, measured at frame `101079fd`.**
The sections above were brought to the owner's standard for a durable
record: em dashes and en dashes replaced by ordinary punctuation, and the
result of each replacement read back against the clause it sits in.

| what the amendment did | figure |
| --- | --- |
| em dashes replaced in the live sections | 18 |
| en dashes replaced in the live sections | 0 |
| em dashes left standing inside dated records | 0 |
| en dashes left standing inside dated records | 0 |
| clauses opened and declined, listed below | 3 |
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
1. §3a's rule turns on the three words *withdrawn, retracted, superseded*, and `scripts/withdrawal_sweep.py` gates on exactly those three. Altering the framing would change the set the sweep matches.
2. §5 and §5a name the principal eleven times, and every one of those names decides whose ruling settles an open question or which order governs today. A role noun would not carry the same answer while two humans give instructions to this lab, so the names were left in place.
3. §5a(e) records which model drafted the amendment and in what order. That is process narrative by shape and evidence by function: it is what shows the disputed clause was not used to adjudicate the dispute about itself.
---

## 8. Team formation is the harness's, and the board is the handoff (added 2026-08-22, Sanaa's harness order)

**A standing team is re-formed from disk, never from memory. The roster lives in
`harness/teams.yaml`, the definitions it generates live in `.claude/agents/`, the
lab's situation lives in `docs/LAB_STATE.md`, and a supervisor updates its own
section of that board AT EVERY COMMIT AND AT EVERY VERDICT. A brief written by
hand is not team formation and does not discharge this clause.**

**The incident that forced it.** Agent teams do not survive a compaction, a
session switch, a crashed terminal or a hit context limit. Nothing about a live
agent is persisted: not its brief, not what it had read, not what it was part-way
through. Re-forming the lab therefore meant a human writing five briefs from
memory, every time, and each retelling silently dropped something — a charter
clause, a rung's real verdict, the fact that a solver was still running. The drift
was invisible because a hand-written brief is checked against nothing. This clause
does not make teams survive; **nothing in the tooling can.** It makes re-formation
one command and, through the board, lossless.

**What is required.**

1. **Formation is `/form-teams`**, which reads `docs/LAB_STATE.md` and spawns every
   standing supervisor in one parallel call, handing each its own board section and
   the standing directives **verbatim**. A supervisor briefed any other way is
   briefed from memory, which is the failure this clause exists to end.
2. **The board is the only handoff channel between sessions.** The session
   scratchpad is not (L-186). What is not on the board is lost.
3. **The board is updated at every commit and at every verdict**, not at the end of
   a turn — the end of a turn may never arrive. Each section carries: last commit,
   live jobs with pid, cwd and ETA, rungs lacking verdicts, next actions, what is on
   the owner's desk, and what is blocked. **Anything the writer did not confirm is
   marked `VERIFY`.** A confident wrong line on the board is worse than a blank one.
4. **The roster is data.** `.claude/agents/*.md` are generated output and are not
   hand-edited; `python3 harness/generate_agents.py --check` is the regression test
   and fails on drift, on an orphaned agent file, and on frontmatter that does not
   parse.
5. **A live reading outranks the board.** `/form-teams` and `/lab-state` both take
   one (`git log`, `ps aux`, `readlink /proc/<pid>/cwd`), and where the two
   disagree the reading wins and the correction goes to the supervisor who owns
   that section — not to whoever noticed.

**§5's model designation is what the harness encodes.** The five supervisors are
generated with `model: fable` because §5 says so in terms; the worker type,
`lab-lane`, inherits nothing and is pinned to Opus as a solver agent. The `tools`
key is deliberately omitted from every generated definition, which is how all tools
are granted — an explicit list drops the agent-spawning tool, and that failure
presents not as an error but as a supervisor quietly doing the family's own work,
which §2 forbids.

**Two things this clause ADDS rather than records, named so nobody reads them back
as the owner's standing policy.**

- **A lane cap: at most three lanes live per supervisor.** No numeric cap existed
  in this charter before today. It is written into every generated definition and
  **checked by nobody**, so by this directory's own standard it is a preference
  until something enforces it. Its nearest existing cognate is
  `ESCALATION_CHARTER.md` §9 rule 4 — *prefer resuming the incumbent over spawning
  a rival* — which is a reason and not a number.
- **Five teams against §2's four families.** The roster splits *cases and
  campaigns* into `heat-transfer` and `cfd`, and maps *infrastructure and
  standards* onto `verification`. §2 states plainly that **adding or merging a
  family is the owner's, not an argument**, so this is recorded as an OPERATIONAL
  SPLIT of the four for dispatch purposes and **not** as a redefinition of them.
  The four families stand as §2 lists them until she rules otherwise.

**Enforcement.** `harness/generate_agents.py --check` gates the roster's
round-trip. **Nothing gates the board's freshness, the lane cap, or the update
duty** — the same honest gap §7 already states about the four personal checks. What
the harness guarantees is that every supervisor is *told*, every time, without a
human remembering to.

---

## Amendment record, continued: version 1.4 (2026-08-22)

**Version 1.4, dated 2026-08-22. One clause added, §8, recording the team harness
as the law of team formation and the `docs/LAB_STATE.md` update duty, measured at
frame `f0e33aee`.**

| what the amendment did | figure |
| --- | --- |
| clauses added | 1 (§8) |
| clauses altered, widened or narrowed | 0 |
| rules ADDED that are not the owner's prior instruction, and say so inline | 2 (the lane cap; the five-team operational split) |
| lines whose number changed above this section | 0 |
| content changes above this section | 1 (line 3's version and date) |

**No existing clause was added to, removed, widened or narrowed, and no modal,
scope or tense inside a clause was altered.** §2's four families are untouched and
still read as the owner set them; §5's model designation is untouched and is
quoted rather than restated; §3's four personal checks are untouched and are
carried verbatim into every generated supervisor definition.

**The clause is filed at the foot, and the line numbering above it was held fixed
on purpose** — for the reason v1.3's record already gives: other records cite this
directory by line and one of those citations sits inside an executable check. The
only content change above this section is line 3's version and date, verified by
comparing `grep -n '^## '` either side of the edit and by asserting the file's line
count was unchanged by the version edit.

**What was opened and left alone.**
1. **§2's family list.** The harness runs five teams and §2 names four. Redrawing
   that boundary is the owner's one-line order, so §2 was not edited; §8 records the
   split as operational and points at §2 as the standing definition.
2. **§5's struck third sentence.** §5a leaves the Opus clause open and hers. The
   harness pins `lab-lane` to Opus as a *solver* agent under §5's second sentence,
   which is in force, and takes no position on the struck third.
3. **§7's enforcement gap.** It was tempting to claim the harness closes it. It
   does not — it distributes the rules reliably, which is a different thing — and
   §8's enforcement paragraph says so rather than letting the new machinery read as
   a check.
