# Certonomous Result Priority Charter

Version 0.1, dated 2026-07-30. **This is a draft for the owner to react to, not
a settled charter.** Her own note on it is "still need to think abt how to go
abt this", and this document takes that literally. The orderings below are
proposals. The open questions in section 6 are named rather than papered over,
and several of them could change the whole shape of the answer.

Version 0.1 rather than 1.0 for that reason. It becomes 1.0 when she rules.

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

### 4.4 Free surface and interface flows

1. **The gated interface or front position**, measured with a metric whose free
   parameter has been swept and whose spread is reported beside the number.
   F7a's two retracted root causes are why this outranks everything.
2. **Integrated forces.**
3. **Field detail.**

### 4.5 Uncertainty quantification

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

### 4.6 Unsteady statistics

1. **Stationarity of the reported statistic**, per quantity and not per run.
2. **The frequency or period.**
3. **The mean.**
4. **The band.**

L-24 again. A run is not converged, a quantity is.

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

## Related

- `docs/charters/VERIFICATION_CHARTER.md`. What makes any of these quantities
  admissible in the first place, and the FD standard section 4.3 is built on.
- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. The three axes, which have
  the same "no invented exchange rate" problem and take the same answer.
- `docs/charters/ESCALATION_CHARTER.md`. Where an undecidable trade goes.
- `LESSONS.md` L-24, L-25, P2.
