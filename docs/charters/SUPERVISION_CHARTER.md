# Certonomous Supervision Charter

Version 1.0, dated 2026-08-07. Governs who supervises what, which checks a
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
> bookkeeping and liaison agents inherit the session default. Long-form
> technical writing goes to Opus.**

The Opus clause has a precedent rather than a theory: the two LaTeX reports
she asked for on 2026-08-05, the closure-challenge campaign and the DAFoam
defect case, were dispatched to Opus agents and that is the pattern
(`docs/PRODUCT_LIST.md`, 2026-08-05 changelog). The Fable clause exists
because the four personal checks of section 3 are judgment work, and putting
them on the strongest available model is the same decision as putting the
chief there. The inherit clause exists so the designation rule costs nothing
on the work that does not need it.

A dispatch that overrides this rule says so in the brief and says why. A
silent override is a violation, in either direction: an adversarial verifier
quietly downgraded is the obvious failure, and a solver agent quietly
upgraded is a spend nobody approved.

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
