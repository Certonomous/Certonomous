# Certonomous Result Priority Charter

Version 0.4, dated 2026-08-05. **This is a draft for the owner to react to, not
a settled charter.** Her own note on it is "still need to think abt how to go
abt this", and this document takes that literally. The orderings below are
proposals. The open questions in section 6 are named rather than papered over,
and several of them could change the whole shape of the answer.

Version 0.2 rather than 1.0 for that reason. It becomes 1.0 when she rules.

**What changed in 0.2, and why it is still 0.x.** Nothing was settled. Three
things were sharpened so that ruling is cheaper than re-deriving. Every class
in section 4 now states the decision that would violate its ordering, because
an ordering nobody can breach is a preference with a table around it. Section
4.5 gains a rank zero, admissibility, after five acts ranked a non-conclusive
refinement band as though it were a measured interval. And section 8 is new: a
one-line decision sheet, each open question reduced to named options with the
lab's recommendation where it has one, so the answer can be "Q2: B" rather than
an essay.

**What changed in 0.3.** One clause, at the head of 4.5: a budget names its
largest term. It is measured rather than drafted, so it is not marked PROPOSAL,
and it is the only thing in this document that is not waiting on her.

**What changed in 0.4, and it is still 0.x for the same reason.** Nothing was
settled and no ordering moved. Section 8.1 is new: the six orderings of
section 4 restated as six answerable items, D8 to D13, each with its ranks on
one line, one sentence of why that order, where it came from, and the decision
that breaches it. It exists so the decision session is accept or edit rather
than compose, and so the two orderings that are hers are visibly not presented
at the same standing as the four the lab drafted. This is P-5.2 made
answerable; P-5.2 itself is unchanged and still open.

## 1. The problem, in her words

> "When method X validates quantity set A but not B, and method Y validates B
> but not A, the lab needs a declared priority ordering of quantities (which
> numbers matter most for the mission's purpose) to choose, state the trade on
> the record, and iterate."

This is not hypothetical. It is the ordinary condition of the lab's work. The
lab's own RANS model sweep predicted, before measuring, that linear Boussinesq
models cannot produce secondary flow of the second kind at any coefficient
setting, then measured five of them at 5.5e-16 to 9.2e-16, which is machine
zero, against a nonlinear model at 0.174. A quantity one family of models
cannot represent at all is the sharpest possible version of this problem, and
the choice between families cannot be made by looking at the quantity they
agree on. Something has to pick.

## 2. The line

> **When two methods validate different quantities, the ordering picks, the
> loser is named, and the trade goes on the record. A choice made without a
> stated ordering is not a choice, it is a preference.**

That much is not a draft. Whatever the orderings turn out to be, the
requirement that a trade be declared and recorded holds, because the failure it
prevents is the one the lab keeps hitting: a method gets chosen for reasons
nobody wrote down, and six weeks later the reason is reconstructed from the
result rather than recovered from the record.

## 3. The trade statement, and this part is proposed as binding

Every time the ordering picks, the record carries a block in this shape. It is
short on purpose.

    TRADE
    Question:        the quantity the mission exists to produce
    Method chosen:   X
    Validates:       the quantities X validates, with their deviations
    Does not:        the quantities X leaves unvalidated
    Method rejected: Y
    Would have:      what Y validates that X does not, with numbers if known
    Ordering used:   the mission class and the rank the decision turned on
    Cost of trade:   what the lab does not know because of this choice
    Revisit when:    the condition that would reopen it

**"Cost of trade" is the field that does the work.** It is the sentence a
future reader needs and the one that never gets written otherwise. It is not an
apology. It is an inventory of what remains unmeasured, and it feeds directly
into the next proposal.

**"Revisit when" prevents a trade becoming a convention.** A decision made
under a compute constraint that later lifts should reopen, and it will not
reopen unless somebody wrote the trigger down at the time.

## 4. Draft orderings by mission class

> **PROPOSAL throughout this section. Nobody has ruled on any of it.**

Read these as lexicographic within a class: a higher rank is settled before a
lower one is considered. Section 6 question 2 asks whether strict lexicographic
ordering is actually right, and it is a real question.

**The whole proposal on one line each, so the shape is arguable before the
detail is.** Two of these six are her own examples and are marked as such.

| Class | Rank 1, what settles first | Rank last |
| --- | --- | --- |
| External aerodynamics (hers) | Integrated forces and moments | Field detail |
| The challenge (hers) | The eight scored columns | Nothing else |
| Gradients and adjoints | Per-component sign agreement | The objective value |
| Free surface and interface | The gated front position, metric swept | Field detail |
| Uncertainty quantification | Coverage, after admissibility | The central value |
| Unsteady statistics | Stationarity, per quantity | The band |

Each class below carries a **Violated when** line. That line is the charter's
own test from `README.md`: if no decision could break the ordering, the
ordering is decoration.

### 4.1 External aerodynamics

Her stated example, expanded.

1. **Integrated forces and moments.** Drag, lift, pitching moment. These are
   what the mission is usually for and what the wall grades.
2. **The location of the dominant flow feature.** Separation, reattachment,
   shock position. This is what determines whether the forces are right for the
   right reason, and section 5 of the verification charter applies in full:
   a feature location is only admissible at a resolution its detector can
   express.
3. **Surface distributions.** Pressure and skin friction along the body.
4. **Field detail.** Everything in the volume.

**Violated when** a model or a mesh is adopted because its wake, its pressure
distribution or its picture improved, while its integrated forces moved further
from the reference, and no trade block says so. The forces do not have to win.
The trade has to be written.

### 4.2 The challenge

Her stated example, and this one is the least ambiguous because the challenge
publishes its own metric.

1. **The eight scored columns.** The overall score is the plain unweighted mean
   of eight per-case scaled mean absolute errors on velocity, so a change of d
   on one case moves the total by exactly d/8.
2. **Nothing else.** Everything else is diagnosis.

That is not a simplification, it is the literal structure of the benchmark. A
method that improves the physics and not the score has not moved the challenge,
and saying so plainly is more useful than a ranking that pretends otherwise.
The deficit decomposition already exists per case, and two duct cases carry
62.9 percent of it.

**The ordering names one entry of record, and the published number is that
entry's.** Because rank 1 is the score, the entry of record is whichever
scoring round scores best, and every published surface carries that round's
overall and its eight per-case values. This is not theory. The credentials wall
carried an overall of 0.0741 while the entry of record scored 0.0676, claimed a
single scoring call where four were made, and claimed best on three of eight
cases where round 3 records five of eight. The audit in the verification
charter's section 11 catches this class now.

**Violated when** a round is adopted, or a claim published, on a physics
argument the eight scored columns do not support, or when a surface publishes a
score that is not the entry of record's.

### 4.3 Gradients and adjoints

This one has an anchor already, which is why it is the most defensible draft
here: the FD grading standard in the verification charter fails a check on any
sign-flipped component regardless of the aggregate. That is a priority ordering
already in force. Written out:

1. **Sign agreement, per component.** A single flip is a FAIL whatever the
   aggregate says.
2. **Direction agreement of the whole vector.** Cosine similarity, or the
   difference-vector norm.
3. **Per-component magnitude.**
4. **The objective value itself.**

A gradient that points the right way with the wrong magnitude still descends. A
gradient with a flipped component climbs.

**Violated when** an adjoint is adopted, or its gradient used to drive an
optimisation, on an aggregate agreement while a component's sign is flipped.
A5 is the standing example: 46.6 percent aggregate with two sign flips.

### 4.4 Free surface and interface flows

1. **The gated interface or front position**, measured with a metric whose free
   parameter has been swept and whose spread is reported beside the number.
   F7a's two retracted root causes are why this outranks everything.
2. **Integrated forces.**
3. **Field detail.**

**Violated when** a front-position result is ranked at all before its metric's
free parameter has been swept. Rank 1 here is not "the front position", it is
"the front position measured by a metric shown to be metric-independent". An
unswept number does not enter the ordering.

### 4.5 Uncertainty quantification

**Before the ranks, a rule about where the next hour goes.** A ranking says
which quantity settles first. A budget says which term is worth working on, and
a budget that does not rank its own terms invites work on the term that has
already stopped mattering.

> **Every reported uncertainty budget names its largest term, and a proposal to
> tighten a smaller one states why.**

Measured, and this is the case that produced the rule. Multifidelity fusion cut
the race estimator's standard error from 0.02832 to 0.000863, a factor of 33,
which is a real result. The budget it produced then records
`high_fidelity_model_form: null`: the solver model-form term, never measured,
had become the largest contributor and was the one term in the budget with no
number in it. Further tightening of the estimator would have been effort spent
on the term that had already stopped dominating, and it would have looked like
progress at every point.
`demo-output/website/mfmc_error_budget.json`, docket `w8-largest-term-rule`.

Two clauses ride with it, and they are the ones that make it bite.

- **An unmeasured term is not a small term.** A budget entry of `null` is the
  loudest thing in the table, not the quietest. The verification charter's rule
  on channels is the same rule: a channel that was not quantified is stated as
  not quantified and is explicitly not counted as zero.
- **The largest term is named even when the lab cannot do anything about it.**
  Naming it is what turns "we improved the estimator" into "we improved the
  estimator and the answer is now limited by the solver", which is the sentence
  the next proposal needs.

**Violated when** a proposal tightens a term while a larger or unmeasured term
sits in the same budget and the proposal does not say so.

**Where it is enforced, 2026-08-01.** `uq.combine_expanded` is the one function
every budget in this lab routes through, and it now returns `largest` beside
`contributions` and `missing`: the largest term it was given, its value, and
its share of the total that was actually computed. The field is named
`share_of_quantified_total` and carries `ranks_only_what_was_measured`, because
a share of a total taken over the quantified channels alone is not a share of
the uncertainty. No caller has to eyeball the map, and a budget that ranks
nothing can no longer be written by accident. The race budget was re-derived
in place from its own stored contributions to carry the field:
`input` at 0.21938, **99.997 percent** of the combined figure, with the
estimator at 0.00173, **0.79 percent**, and the high-fidelity model form still
`null`.

0. **Admissibility, before any rank.** A band whose producing procedure marks
   itself non-conclusive is not a band and does not enter the ordering at any
   rank. Coverage cannot be assessed on an interval that does not exist, and a
   width comparison between a real band and a fallback is arithmetic on two
   different kinds of thing. Five acts ranked a non-conclusive Eca and Hoekstra
   fallback as though it were measured, under a caption that made it a 95
   percent confidence interval. The verification charter's section 6 governs
   the label. This clause governs the rank.
1. **Coverage.** Does the band contain the truth. A narrow band that misses is
   worse than a wide band that contains, and reporting only the width inverts
   this.
2. **Width**, at equal coverage.
3. **The central value.**

Grounded in F6d, which reported both frameworks containing the LES reference
and then compared widths, 4.041 against 0.797. And in L-24's corollary: grade
the phase-aligned waveform, the peak and the band, not just the mean, because
between two cycles of one run the mean moved 2.1 percent while the peak moved
by a factor of 18.5.

**Violated when** a framework is preferred for a narrower band with no coverage
statement, or when a non-conclusive band is compared on width at all.

### 4.6 Unsteady statistics

1. **Stationarity of the reported statistic**, per quantity and not per run.
2. **The frequency or period.**
3. **The mean.**
4. **The band.**

L-24 again. A run is not converged, a quantity is.

**Violated when** a mean or a band is reported for a quantity whose own
stationarity was never tested, on the strength of the run having converged.
F9 is the standing example: six reference runs judged stationary on the throat
differential, publishing a downstream differential with peak-to-trough bands of
39, 113 and 128 percent of its own mean.

## 5. What the ordering does not do

Two limits, stated so the charter is not read as more than it is.

**It does not decide whether a result is publishable.** That is the
verification charter. A result low on the ordering with a clean gate and a
retained artifact is a result. A result high on the ordering with neither is
not.

**It does not make an unvalidated quantity disappear.** Choosing method X
because it validates the forces does not license silence about the field. The
"Does not" and "Cost of trade" lines exist so the gap is on the record at the
moment it is created.

## 6. The open questions, named

These are the reasons this document is version 0.1. Each one is a real fork,
and the lab has an opinion on some of them and no business deciding any.

**Q1. Which ordering applies when a mission spans two classes?** An adjoint on
a free-surface case is 4.3 and 4.4 at once. A challenge case that is also a
duct flow is 4.2 and 4.1. The obvious answer is that the challenge ordering
wins whenever a case is scored, because the scored column is the mission's
purpose. The obvious answer is also how a lab ends up optimising a metric
rather than a physics, and the challenge itself forbids the most direct version
of that. Not resolved.

**Q2. Is the ordering lexicographic, or is there an exchange rate?** As drafted
it is strict: rank 1 settles before rank 2 is looked at. That is clean and it
is brittle. A method that improves the forces by 0.2 percent and destroys the
separation location beats one that improves separation by 30 percent and moves
the forces by 0.3 percent the wrong way, under strict lexicographic reading,
and that is probably wrong. The alternative, a tolerance band inside which rank
1 counts as tied so rank 2 decides, requires a number per class that nobody has
set. Not resolved, and this is the question the lab would most like answered.

**Q3. What happens when the higher-priority quantity has no reference?** The
ordering says forces first. If the case has no experimental force data and does
have surface pressure data, the only gradeable quantity is rank 3, and the wall
credential lives there. Does the ordering follow the mission's purpose or the
available reference? These are different answers and both are defensible.

**Q4. Does the ordering bind method selection, or only reporting?** Her framing
is about choosing between two methods, so it binds selection. But a strict
selection rule on 4.2 would have blocked the closure work early, because its
first rounds did not move the score. A rule that forbids the exploratory phase
of the only program the lab is competitively ranked in is a bad rule. Perhaps
selection binds at adoption and not at investigation. Not resolved.

**Q5. How does the fidelity chip interact with the rank?** A VALIDATED field
result against an UNCONVERGED force. Rank says forces, the chip says the force
number is not evidence yet. The lab's instinct is that the chip wins, because
UNCONVERGED means there is no number to prioritise, but that instinct makes the
ordering conditional on convergence in a way none of section 4 says.

**Q6. Who declares the ordering for a class that is not listed?** Rotating
machinery, conjugate heat transfer, aeroelasticity and combustion all have
obvious first ranks and none of them is written here. Does an agent draft the
ordering as part of the proposal, subject to the docket, or does the class stay
unenterable until the owner rules?

**Q7. Does a trade ever expire on its own?** "Revisit when" carries a trigger.
Nothing carries a date. A trade made under a 30 GB memory ceiling should
probably reopen when the box grows, and nothing in this draft makes that
happen.

## 7. What to do until this is settled

The interim rule, which is safe under every resolution of section 6:

1. **State the ordering you used, whatever it was.** Even an ad hoc one. A
   named ad hoc ordering is arguable. An unnamed one is invisible.
2. **Write the trade block.** Section 3 does not depend on any answer in
   section 6.
3. **When the choice is genuinely undecidable under section 4, escalate.** That
   is charter 7's job and the honest output is a question, not a coin flip.

## 8. The one-line decision sheet

Section 6 states the questions. This section states the answers she can pick
from, so ruling costs a line rather than a re-derivation. Every option is
written to be chosen by name: "Q2: B" is a complete decision.

Where the lab has a recommendation it says so and says why. Where it has none
it says that too, because a manufactured recommendation on a question this
open would be the invention this charter exists to avoid.

**D0. Does the trade block bind, whatever else is unresolved?** Section 3.

- **A. Yes.** Every ordering-driven choice carries the nine-line block.
- **B. Only above a stated cost or visibility threshold.**
- **C. No.**

Trade: A costs a paragraph per decision and produces the record's only
inventory of what the lab does not know. B needs a threshold nobody has set and
the cheap decisions are exactly the ones that accumulate unrecorded. *Lab
recommends A*, and it is the one part of this document written as binding
already, because it is safe under every resolution below.

**D1, from Q1. Which ordering governs a case in two classes?** A challenge case
that is also a duct flow, an adjoint on a free surface.

- **A. The most specific scored purpose wins.** If a case produces a scored
  column, 4.2 governs.
- **B. The physics class wins**, and the score is reported alongside.
- **C. Both orderings are stated and any disagreement escalates**, so a
  cross-class case is never decided silently.

Trade: A is the honest reading of what the mission is for, and it is also how a
lab ends up optimising a metric instead of a physics. B protects the science
and can leave the ranked entry unimproved for a quarter. C never picks wrong
and produces more dockets. *No recommendation.* This one turns on how much of
the lab's year the challenge is meant to own, which is hers.

**D2, from Q2. Strict lexicographic, or a tolerance band?** The question the
lab most wants answered.

- **A. Strict.** Rank 1 settles before rank 2 is looked at. Clean, and it lets
  a 0.2 percent force improvement beat a 30 percent separation improvement.
- **B. Banded.** Rank 1 counts as tied inside a per-class tolerance, then rank
  2 decides. Needs one number per class, and inventing six numbers is what this
  charter refuses to do without her.
- **C. Banded, with the band set once per class at the moment it first
  matters**, recorded in the trade block that needed it, rather than six
  numbers set in advance from nothing.

Trade: A is enforceable today and is probably wrong in the specific case named
in Q2. B is right in principle and blocked on six numbers. C gets the behaviour
of B while paying for each band only when a real decision needs it, and the
cost is that two decisions in the same class can be made against different
bands until the first one is recorded. *Lab recommends C*, weakly, and would
rather she picked A than left it open.

**D3, from Q3. Higher-priority quantity has no reference.** Forces first, but
only the surface pressure has experimental data.

- **A. The ordering follows the mission's purpose.** The forces still outrank,
  the case reports that rank 1 is ungradeable, and the pressure agreement is
  reported without being promoted.
- **B. The ordering follows the available reference.** The gradeable quantity
  becomes rank 1 for that case, and the record says the ordering was rewritten
  by data availability.

Trade: A keeps the ordering honest and produces cases whose top rank is blank.
B produces a gradeable verdict on every case and quietly lets the reference
catalogue set the lab's priorities. *Lab recommends A*, because B is the shape
that turns "what matters" into "what we happen to be able to measure", and the
wall credential is a reason to prefer B that should be visible rather than
structural.

**D4, from Q4. Does the ordering bind selection or only reporting?**

- **A. Selection.** A method that loses on rank 1 is not adopted.
- **B. Reporting only.** Anything may be tried; the ordering governs what the
  record claims.
- **C. Selection at adoption, reporting during investigation.** An exploratory
  round is exempt; the round that becomes the entry of record is not.

Trade: A is her framing taken literally and would have blocked the closure
work's first rounds, which did not move the score. B makes the ordering
unfalsifiable at the moment it matters most. C needs a visible line between
investigating and adopting, and the lab already has one, because a round
becomes the entry of record by an explicit act. *Lab recommends C.*

**D5, from Q5. Fidelity chip versus rank.** A VALIDATED field result against an
UNCONVERGED force.

- **A. The chip wins.** UNCONVERGED means there is no number to prioritise, so
  the ordering skips it and says it skipped it.
- **B. The rank wins.** The case is blocked at rank 1 until the force
  converges, and nothing lower is reported as the result.

Trade: A keeps work moving and makes the ordering conditional on convergence in
a way section 4 does not say. B is the hard ladder rule of the verification
charter applied to priority, and it is consistent with a failed gate blocking
every downstream rung. *Lab recommends B*, and notes it is the stricter of the
two and the one that costs more.

**D6, from Q6. Who declares an ordering for an unlisted class?** Rotating
machinery, conjugate heat transfer, aeroelasticity, combustion.

- **A. The proposal drafts it**, marked PROPOSAL, and the class is enterable
  immediately with the ordering going to the docket for ratification.
- **B. The class stays unenterable** until she rules.

Trade: A costs the risk of a class running for weeks under an ordering she
would not have chosen, and every such ordering is on the record and reversible.
B costs a night every time the lab meets a new class. *Lab recommends A*, on
the same reasoning the escalation charter uses for reversible and cheap.

**D7, from Q7. Does a trade expire?**

- **A. No.** "Revisit when" carries a trigger and that is enough.
- **B. Every trade carries a review date as well as a trigger**, and an expired
  trade is a row on the morning report's waiting list until it is renewed or
  retired.

Trade: A is what is written and it means a trade made under a memory ceiling
survives the ceiling. B costs a recurring report row per trade and is the only
version that fires without anybody remembering. *Lab recommends B*, and it is
cheap: the trigger is already written, the date is one more line.

## 8.1 The six orderings, as one accept-or-edit sheet

> **PROPOSED, 2026-08-05, under the standing charter-iteration directive.
> Nothing here is enacted and nothing here is new policy.** Section 4 already
> states these six orderings in full. This sheet restates each one so it can be
> answered in a line rather than composed from scratch: the ranks, one sentence
> of why that rank order and not another, where the ordering comes from, and
> the decision that would breach it. **"D9: accept" is a complete answer**, and
> so is "D9: accept, swap ranks 2 and 3". D8 to D13 extend section 8's sheet
> and are answered in the same session; P-5.2 in `PROPOSALS_OPEN.md` is the
> same question and this is where the text for it lives.
>
> The lab's recommendation is stated per class rather than once, because two of
> the six are hers already and it would be dishonest to present the lab's
> drafts at the same standing as her examples.

**D8. External aerodynamics** (section 4.1). Hers, expanded.

1. Integrated forces and moments → 2. dominant flow feature location →
3. surface distributions → 4. field detail.

*Why this order:* the forces are what the mission is for and what the wall
grades, and the feature location sits second because it is what decides
whether the forces are right for the right reason rather than by cancellation.
*Provenance:* her stated example; ranks 2 to 4 are the expansion.
*Violated when* a model or mesh is adopted on a better wake, pressure
distribution or picture while its integrated forces move away from the
reference, with no trade block. *Lab recommends accept as written*, because
the expansion adds nothing her example did not imply.

**D9. The challenge** (section 4.2). Hers, and the least ambiguous of the six.

1. The eight scored columns → 2. nothing else.

*Why this order:* the benchmark publishes its own metric and the overall score
is the plain mean of eight, so a change of d on one case moves the total by
exactly d/8 and everything else is diagnosis. *Provenance:* hers, and the
arithmetic is the benchmark's. *Violated when* a round is adopted or a claim
published on a physics argument the eight columns do not support, or when a
surface publishes a score that is not the entry of record's, which is a defect
the wall has actually shipped. *Lab recommends accept as written.*

**D10. Gradients and adjoints** (section 4.3). Drafted, and already in force.

1. Per-component sign agreement → 2. direction agreement of the whole vector
→ 3. per-component magnitude → 4. the objective value.

*Why this order:* a gradient that points the right way with the wrong
magnitude still descends and a gradient with a flipped component climbs, so
sign is not a tighter version of magnitude, it is a different question.
*Provenance:* not really a draft. The FD grading standard already fails any
sign-flipped component regardless of the aggregate, so ranks 1 and 3 are a
written-down description of a rule in force. *Violated when* an adjoint is
adopted, or drives an optimisation, on aggregate agreement while a component's
sign is flipped; A5 is the standing example at 46.6 percent aggregate with two
flips. *Lab recommends accept*, and notes this is the one drafted class where
rejecting the ordering means changing a standard that is already enforced.

**D11. Free surface and interface** (section 4.4). Drafted.

1. The gated front or interface position, measured with a metric whose free
parameter has been swept and whose spread is printed beside the number →
2. integrated forces → 3. field detail.

*Why this order:* the quantity the mission exists to produce is the front, and
F7a retracted two published root causes that were artefacts of an unswept
metric parameter, so rank 1 is not "the front position" but "a front position
shown to be metric-independent". *Provenance:* the lab's, with F7a as the
measured reason. *Violated when* a front-position result is ranked at all
before its metric's free parameter has been swept; an unswept number does not
enter the ordering. *No recommendation on the class, and a recommendation on
its rank 1*: whatever ordering she prefers, the admissibility condition on
rank 1 is the part the record paid for.

**D12. Uncertainty quantification** (section 4.5). Drafted, with rank zero
measured.

0. Admissibility → 1. coverage → 2. width at equal coverage → 3. the central
value.

*Why this order:* a narrow band that misses is worse than a wide band that
contains, so reporting width first inverts the question; and a band whose own
producing procedure marks itself non-conclusive is not a band, which is rank
zero and is not a preference. Five acts ranked a non-conclusive fallback as
though it were measured, under a caption that made it a 95 percent confidence
interval. *Provenance:* the lab's, grounded in F6d, which reported both
frameworks containing the reference and then compared widths of 4.041 against
0.797. The largest-term rule at the head of 4.5 is measured and is not part of
this question. *Violated when* a framework is preferred for a narrower band
with no coverage statement, or a non-conclusive band is compared on width at
all. *Lab recommends accept*, and flags that rank 0 is the only clause in the
six that refuses to rank something rather than ordering it.

**D13. Unsteady statistics** (section 4.6). Drafted.

1. Stationarity of the reported statistic, per quantity → 2. the frequency or
period → 3. the mean → 4. the band.

*Why this order:* a run is not converged, a quantity is, and stationarity is
the precondition for the other three meaning anything rather than a competitor
to them. *Provenance:* the lab's, from L-24 and F9: six reference runs judged
stationary on the throat differential published a downstream differential with
peak-to-trough bands of 39, 113 and 128 percent of its own mean. *Violated
when* a mean or a band is reported for a quantity whose own stationarity was
never tested, on the strength of the run having converged. *Lab recommends
accept.*

**What the sheet does not ask.** Whether the orderings are lexicographic is
D2 and is asked once for all six, not per class. Whether an ordering binds
selection or only reporting is D4. Whether an unlisted class may draft its own
is D6, and answering D8 to D13 does not answer it.

## Related

- `docs/charters/VERIFICATION_CHARTER.md`. What makes any of these quantities
  admissible in the first place, and the FD standard section 4.3 is built on.
- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. The three axes, which have
  the same "no invented exchange rate" problem and take the same answer.
- `docs/charters/ESCALATION_CHARTER.md`. Where an undecidable trade goes.
- `LESSONS.md` L-24, L-25, P2.
