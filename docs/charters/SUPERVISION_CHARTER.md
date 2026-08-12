# Certonomous Supervision Charter

Version 1.2, dated 2026-08-12. Governs who supervises what, which checks a
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
   crashed run — forces to 1e99 behind a 1.4e-8 residual, a live S10
   specimen — and triage of it produced the hurricane: potentialFoam's
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

**The standing rule was that a superseded entry is withdrawn by its author** — right in
spirit, because the author knows what they meant, and **structurally broken**, because
authors here are sessions and sessions end. When the author is gone the rule names nobody,
and a rule that names nobody is not enforcement; it is a refuted claim staying published
with a note explaining that someone ought to remove it.

**The instance, 2026-08-11.** A peer session published a correction, a second session
refuted it by execution, and the correction's dependent gate had already been re-based on
the strength of it. The peer session then ended. Under the author rule the withdrawal had
no owner at all, so a claim known to be false and a gate known to be uninformative both sat
live in the record — not through disagreement or backlog, but because the rule pointed at
a ghost.

**Why the role and not "whoever finds it".** Discovery is not duty. Anyone may notice; if
noticing were the assignment, the item would be everybody's and therefore nobody's, which
is the failure this rule exists to close. The **family supervisor for the record's family**
owns the withdrawal, and the chief owns it where no family does.

**What "within the cycle" means.** Before the family's next reporting cycle closes. Not
"soon" — a superseded claim's cost is exactly the time it spends readable, and a reader
cannot tell a claim awaiting withdrawal from a claim in force.

**The sweep is the enforcement, and it is the part that must not be skipped.** Weekly,
assert **zero unowned supersessions**: every withdrawn, retracted or superseded entry has a
named current owner, and every refutation filed against a live claim has a withdrawal
either done or assigned. A rule without a sweep is a preference. Anything the sweep finds
unowned is assigned by the chief on the spot — the assignment is the deliverable, not a
plan to assign.

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
recorded as item 4 before any of it executed — flagged before dispatch, not
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
§5 has no mechanism for is making a declared override standing** — that is the
actual gap, and it is the thing the options below are about.

**(d) The standing rule is Katie's to set, and it is still open.** The two
options, with the honest consideration on each side and no recommendation:

**Option A — keep the clause, treat the order as a dated override.** §5's third
sentence is restored; Katie's order of 2026-08-12 stands as a declared,
order-scoped override under §5's existing override paragraph, on the record
with its date and reason.
- *For:* the designation rule keeps one testable line, and it survives changes
  in which model is strongest or available — it names the task class, not the
  fleet roster. The recorded reason for the clause is a decision Katie made on
  evidence: the two LaTeX reports of 2026-08-05 (`docs/PRODUCT_LIST.md`,
  2026-08-05 changelog). Overrides stay individually visible and auditable.
- *Against:* if writing-goes-to-Fable is the intended norm, every future day's
  order must re-declare the override, and a rule overridden by default is
  scenery — which is exactly what `docs/charters/README.md` says disqualifies a
  clause from this directory. §7 already admits nothing mechanical checks model
  designation, so "declared in the brief" is worth only what the brief is worth.

**Option B — re-designate: long-form technical writing goes to Fable.** §5's
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

**Crash triage paying for itself.** F8's steady-MRF line closed three ways —
geometry exonerated to the millimeter, frame terms audited to source lines,
initialization tested single-variable — because every crash and every
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
