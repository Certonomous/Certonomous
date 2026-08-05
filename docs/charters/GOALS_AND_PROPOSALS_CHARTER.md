# Certonomous Goals and Research Proposal Charter

Version 1.2, dated 2026-08-05. Governs what the lab optimizes for when it
drafts its own work. It applies to every proposal that reaches the agenda
inbox, and therefore to every night the lab spends unattended.

Version 1.1 adds disqualifier 10, the archive replay a detection rule owes
before it is adopted, after S7 was measured firing on two thirds of the lab's
completed steady runs.

Version 1.2 records two things that moved from proposal to harness under the
standing charter-iteration directive, both reversible by her word. P-1.1: the
gain table in section 2 now states a score for every source kind in use, and
an unrecognised kind is refused at intake instead of silently scoring the
default. P-3.1, charter 3's half: `hard_criterion` is a required field on
every proposal filed from 2026-08-05, so section 5's fourth requirement stops
being marked proposed and section 7's honesty list shrinks by one line. The
221 docket entries predating the date are grandfathered where they stand.

## 1. The line

> **A proposal that cannot come out more than one way is not a proposal.**

Everything else here is ranking. This is the gate. A study whose result is
known before it runs buys nothing at any cost, and a study whose outcomes are
all read the same way buys nothing either. The lab has already paid for both
shapes of this:

- L-24. Cycle-integrated stroke volume is the intuitive gate for a pulsatile
  solve and it is worthless for an incompressible rigid-wall case with a
  prescribed inlet flux, because mass conservation makes it identical to the
  boundary condition at every instant, in cycle 1 of a diverging run as much as
  in a converged one. **A metric that cannot fail is not a gate.**
- L-26. The first attempt at the sign check ran at Re 10, where the Stokes
  limit makes the velocity field independent of viscosity, so all four runs
  agreed by construction and both competing hypotheses passed. It was discarded
  and rebuilt at Re 100, where the answers separate. **A control that cannot
  distinguish the two answers is not a control.**

So every proposal states, before it runs, the outcomes it can produce and which
lab decision each outcome changes. That is P2, prediction-first runs, made a
condition of entry rather than a habit.

## 2. The three axes

The lab optimizes for three things. They are the owner's, and they are not
interchangeable.

### Axis A. Knowledge gain per core-minute

**This axis is already implemented and running.** It is not a proposal. The
ranking function lives in `sdk/chief_engineer/agenda.py` and the control room
surfaces it as "expected knowledge gain per core minute, deterministic".

    rank_value = gain_points(source_kind) / max(est_core_min, 1.0)

Gain points by `source_kind`, and from version 1.2 the table below is the
whole of it, because an unrecognised kind no longer scores anything:

| source_kind | points | what it buys |
| --- | --- | --- |
| `challenge` | 4.0 | Moves a scored column of the benchmark challenge, the one axis with an exact metric. |
| `measurement` | 3.0 | A number against a stated criterion, which is what `gate` scores. |
| `gate` | 3.0 | A pass or fail verdict on a stated criterion. |
| `capability` | 2.0 | Something the lab could not do before. |
| `ledger` | 2.0 | Rows the fleet learns from. |
| `reading` | 2.0 | A reading that yields a proposal; cheap, and it unblocks measured work. |
| `inbox` | 2.0 | A filed proposal naming no kind; the long-documented inbox default, now stated in the table instead of reached by falling through it. |
| `report` | 1.0 | A written finding with no new measurement. |
| anything else | refused | A proposal violation at intake from 2026-08-05, never a silent default. |

The one-core-minute floor exists so that near-zero screening costs do not
divide to infinity. Sort order is descending rank value, then the case-folded
objective, then the id, so the ordering is deterministic and two agents ranking
the same docket get the same queue. Tests pin both properties.

**The defect version 1.1 disclosed here is closed, in two dated steps.** The
disclosure was: the docket carried `measurement`, `reading` and `challenge`
and the table carried none of them, so 24 of 55 proposals ranked on a silent
default of 2.0, including every challenge-aligned proposal, which are exactly
the proposals the third axis exists to promote. The table half landed
2026-07-30 (commit `f2689232`), and its values differ from the trio P-1.1
drafted, on stated grounds rather than drift: the standing priority order puts
the challenge and the uncertainty layer first, so `challenge` scores 4.0
rather than the drafted 3.0 and `reading` 2.0 rather than 1.5, because the
drafted values would have let ladder work outrank challenge work on every tie,
which is the inversion the fix existed to remove. The refusal half landed
2026-08-05: `source_kind_violations` in `sdk/chief_engineer/agenda.py` makes
an unrecognised kind a proposal violation at intake. Docket rows created
before 2026-08-05 are grandfathered so an old docket always loads; they rank
on the default and are recorded in `unscored_kinds()` rather than silently.
Both halves are the lab's numbers carried out under the standing iteration
directive, and P-1.1 in `PROPOSALS_OPEN.md` records them for her to overturn
with a word.

**The cost estimate is a prediction and is graded.** `est_core_min` is written
before the run and compared against the measured core-minutes afterwards. A
proposal whose estimate was wrong by more than a factor of three has its
`cost_basis` corrected in the record, because the whole axis is a ratio and a
denominator nobody checks is a denominator that drifts. This is the same
discipline P2 applies to physics predictions, pointed at the budget.

### Axis B. Wall credential value

**PROPOSAL. Nobody has ruled on this axis and no such term exists in the
repository today.** The credential wall exists, its rows carry a tier, and the
tiers are ranked. Nothing assigns a credential a value. This is a draft so
there is something to argue with.

The wall is the lab's product surface: canonical and industrial bodies graded
against published experiment, each with its tier and envelope. Its curation
rule is already the owner's and is not up for negotiation here. Weak or
confusing validation numbers never go on the wall. No observed-order ladders
with implausible p values, no bands over 100 percent, no cases more than 10
percent off their reference, no regime-mismatch essays. Curate to the clean
wins and never alter a number.

Proposed scoring, 0 to 3:

| Score | Anchor |
| --- | --- |
| 3 | Produces a new VALIDATED row: a named published experiment, a deviation inside 10 percent, and all three uncertainty channels computed. |
| 2 | Produces a new SOLVER-BACKED row against a named published benchmark or exact solution, with no experimental anchor available. |
| 1 | Improves a row that already exists: narrows the envelope, adds a rung to its ladder, or replaces a transferred model channel with a direct one. |
| 0 | Produces no wall row. |

**Scoring 0 here is not a reason to refuse a proposal.** Most of the lab's best
work scores 0 on this axis. Instrument checks score 0. Negative results score
0. The F6d random-matrix study scored 0 and was worth doing, because it
measured that a probabilistic band is 5.1 times wider than the corner union it
was meant to improve on, and that is a finding the field does not have. This
axis measures one thing and it is not importance.

**A credential the wall would refuse to display scores 0, not 3.** A proposal
that will produce a 40 percent deviation against experiment is honest, is
publishable in the record, belongs in `NOT_PASSING_REGISTER.md`, and buys no
credential. Say so in the proposal rather than scoring it optimistically and
discovering it at curation.

### Axis C. Challenge deficit reduction

This axis is operational today because the challenge has a published metric and
the lab has already decomposed its own deficit against it.

**The challenge.** The Closure Challenge, a machine-learning-for-turbulence
benchmark. Eight scored test cases. Each submission is 1000 rows by 3 columns
of velocity per case. Per-case score is scaled mean absolute error: the mean
Euclidean prediction error over the case's 1000 fixed evaluation points,
divided by the mean magnitude of the truth. Overall score is the plain
unweighted mean of the eight per-case values. Lower is better.

**The arithmetic that makes this axis exact.** Because the overall score is a
plain mean of eight, a proposal that improves one case by an amount d moves the
overall by exactly d/8. That is the score on this axis, in the metric's own
units, and it requires no invented weighting. A proposal targeting a case
states the per-case improvement it expects and divides by eight. A proposal
that improves nothing on the eight scored cases scores exactly zero, however
interesting it is.

**Where the deficit actually lives.** It is decomposed per case in
`demo-output/website/closure_challenge_C2_error_decomposition.md`, as each
case's share of the gap to the rank 2 entry. Two duct cases, `AR_1_Ret_360` and
`AR_3_Ret_360`, are together 62.9 percent of it. An effort ordering that
ignores that decomposition is choosing to work on 37 percent of the problem.

**The disqualifier is absolute and comes from the challenge's own rules.** It
is strictly forbidden to train or validate on any data from the test cases. A
proposal that touches test-case data is refused outright. There is no version
of it that gets approved with a caveat, and no result derived from it enters
the record as anything other than a rules violation.

**Challenge alignment is by scored column, not by topic.** A study of duct
secondary flow that does not produce predictions on the eight cases is not
challenge-aligned. It may be excellent. It scores zero here.

## 3. How the three trade off

> **PROPOSAL. Nobody has ruled on this.** The three axes are the owner's. The
> combination rule below is the lab's draft, and it is deliberately the
> weakest thing in this charter, because a weighted sum here would be invented
> precision presented as policy.

**No weighted sum.** The axes are in different units: a ratio, an ordinal
anchor, and a value in the challenge metric. Adding them requires exchange
rates nobody has set, and once set they would be quoted as though measured.

**The rule is dominance, then a declared priority.**

1. A proposal outranks another when it is at least equal on all three axes and
   strictly better on one. Where dominance decides, it decides.
2. Where neither dominates, the tie goes to whichever axis the owner has named
   as the current priority. That naming is a single line in the docket, it has
   a date, and it holds until she changes it.
3. Where no priority is set and neither dominates, the choice goes to the
   docket rather than being made by whoever is drafting. This is charter 7's
   territory and the deliberate answer is escalation, not a coin flip.

**Ties are common and that is the point.** A rule that always produces a winner
is a rule that hides the decision. When two proposals genuinely cannot be
ordered, the honest output is a question for the owner, and this charter would
rather generate that question than manufacture a ranking.

## 4. Disqualifiers

A proposal carrying any of these does not enter the queue. These are not
tie-breakers and not deductions. They are refusals.

1. **No prediction written before the run.** P2. Confirmations and refutations
   count only if the prediction predates the data.
2. **No outcome that changes a lab decision.** Section 1. Includes the two
   specific shapes: a metric that cannot fail, and a control that cannot
   distinguish the answers.
3. **More than one variable moves per rung.** P5. Compound fixes that work
   teach nothing, because the cause stays unattributed.
4. **The method cannot state what it drops.** `INNOVATION_STANDARD.md`, stated
   once and unchanged: any method that cannot state what it drops does not
   enter.
5. **A citation that is not read.** Charter 2. Every citation carries a
   provenance tier or the proposal is refused.
6. **Below the hardness floor without written approval.** Charter 3.
7. **No retained-artifact plan.** L-27. If a run decides a gate, its log, its
   coefficient file and its case dictionaries are retained under the campaign
   and not left in scratch. F2's headline validation number cost the lab two
   days of unverifiable headline because a 34-second run's artifacts were
   thrown away with a scratch ledger.
8. **No stated cost, or a cost over the rung cap with no escalation.**
   Charter 6.
9. **Training or validating on challenge test-case data.** Section 2, axis C.
10. **A detection rule with no archive replay. PROPOSAL, nobody has ruled on
    this**, and it is written here because the gap is measured rather than
    theoretical. A proposal that adds a rule,
    a signature, a gate or a check which will fire on the lab's own work states
    what it does to the archive before it is adopted: the corpus it was replayed
    against, the number of logs it fires on, the number it calls fatal, and its
    behaviour on the case that motivated it. S7 entered without one and was
    later measured firing on 68 of 106 archived steady logs and reaching FATAL
    on 65, every one of them a completed run whose results are on the record.
    The verification charter's section 5 carries the rule; this is the intake
    refusal that makes it bite. A rule is an instrument and section 1 applies to
    it unchanged: a rule that fires on everything cannot come out more than one
    way.
11. **A premise quoted from a stored artifact that nobody opened.** A proposal
    whose rationale quotes values, counts or a verdict taken from a stored
    record cites the file that holds them. The refusal is cheap to clear, and
    clearing it is the reading that was skipped.
    Measured on the docket 2026-08-02, which is the archive replay
    disqualifier 10 requires of any new rule. Thirteen proposals quote a
    numeric sequence in their rationale, and **not one of the thirteen carries
    a citation that resolves to a file in this tree**. Four of the thirteen are
    among the twelve dismissals. Six more reached `done` only after the agent
    who took the item corrected its premise in the outcome, in the words "the
    item's premise is corrected on the way", "the item's premise is
    unreachable", and "not what the item asked for". Ten of thirteen were
    wrong on arrival.
    **None of the ten was wrong about its cost.** Eight were priced at the
    drafter's default of 20 core-minutes, and the price was never why any of
    them failed. The failure was the same shape every time: the rationale
    restated a CONCLUSION from a record, "the refinement study ended
    inconclusive", and then supplied its own DIAGNOSIS, "a further rung can
    settle the observed order", without opening the record. The real cause was
    somewhere else every time. The rungs already existed. The three rungs were
    two mesh recipes. The finest increment sat below its own iterative noise
    floor. A stored VERDICT is not the record; the file that stores the rungs
    is the record.
12. **A rationale transcribed from another document's next steps.** A sentence
    lifted from a report's next investigations is a topic, not a proposal. It
    clears this by naming the instrument that will produce the answer and
    showing that the criterion it is graded on is expressible by that
    instrument, which is `CASE_SELECTION_CHARTER.md` section 4 step 4 applied
    at drafting instead of at pickup.
    Measured on the same docket: nine proposals open with the words filed
    under next investigations by the mission report. **Six are dismissed, and
    the remaining three are approved at zero core-minutes**, repriced to
    unknown and blocked on a meshed valve and a moving-boundary solver this box
    does not have. Nine of nine failed to become runnable work. The sharpest is
    the cruise Mach trade: the criterion it would meet is transonic shocks, and
    it would be flown on a vortex-lattice method, which has no discontinuity in
    its solution space. The instrument cannot express the criterion the item
    exists to score, and that is a zero-compute check that kills a family
    before it starts.
13. **A visible field that breaks the style rails.** The agenda enforces these
    mechanically: no en dashes or em dashes, no raw URLs, no internal file
    paths or extensions, and none of the banned vocabulary, in `objective`,
    `rationale`, `expected_knowledge_gain`, `cost_basis` or `dismiss_reason`.
    A file that breaks them is skipped at intake, never rewritten.

## 5. What a proposal contains

The schema is `sdk/chief_engineer/agenda.py` and it is authoritative:

    {id, objective, rationale, citations, est_core_min, cost_basis,
     expected_knowledge_gain, source_kind, hard_criterion, status,
     created_at, decided_at?, dismiss_reason?, mission_id?, launch_prompt?}

Statuses are `proposed`, `approved`, `approved-queued`, `dismissed`, `done`.
A proposal approved when the machine has no room becomes `approved-queued`
rather than being launched or quietly dropped, and the docket says so.

This charter adds four requirements to what those fields must carry. They are
requirements on content, not new fields, except where marked.

- **`expected_knowledge_gain` names the outcomes.** Not "we will learn about
  the duct". The set of distinguishable results and the decision each one
  changes.
- **`rationale` names the axis scores.** All three, including the zeros.
- **`cost_basis` names how the estimate was reached**, so it can be graded
  afterwards.
- **A `hard_criterion` field, required from 2026-08-05** on every new
  proposal, carrying the numbered HARD criterion the case meets or one of
  the closed answers charter 3's own text allows (`existing-family`,
  `regression-test`, `instrument-check`, `no-case`, `below-floor`; the
  value set and its tracing live in `CASE_SELECTION_CHARTER.md` section 9).
  Absent or unrecognised is refused at intake. Proposals created before
  that date are grandfathered where they stand.

## 6. Worked examples

**Enters, high.** A gate-kind proposal costing 20 core-minutes that decides
whether a stated mesh criterion passes. Axis A: 3.0 divided by 20, which is
0.15, near the top of any docket. Axis B: 1, it tightens an existing row. Axis
C: 0. Dominant over anything scoring lower on all three.

**Enters despite two zeros.** The random-matrix uncertainty study. Axis B: 0,
no wall row. Axis C: 0, no scored column. Axis A: it produced a measured
negative result with a known and measured root cause, and it corrected a sign
error that had invalidated three published corner values. It entered on axis A
alone and it was right to.

**Refused, and this is the useful example.** A proposal to improve the duct
cases by fitting on the challenge's own test data. It would dominate on axis C
by construction. It is refused under disqualifier 9 without being scored,
because a disqualifier is not a large negative number, it is a different kind
of statement.

**Refused on axis-free grounds.** A proposal to re-run a diverged case because
it "looked interrupted". L-19: interrupted and diverged look identical from
outside, and the DPW8 L4 rung reproduced bit for bit on relaunch and diverged
again, costing a second 3,388 seconds to discover the first 56 minutes had also
been a diverged solve. The proposal fails disqualifier 2 until it states the
relaunch comparison that would distinguish the two, at which point it becomes a
good proposal.

## 7. Enforcement

- `agenda.proposal_violations` is the intake check, and the drafting scripts
  under `scripts/add_proposals_r*.py` refuse to write when any proposal in
  their batch reports a violation. That is the model: refuse the batch, do not
  land the good ones and warn about the rest.
- The ranking is tested for determinism and for the divide-by-nearly-zero
  floor.
- The docket is written atomically through a staging file and a replace, so a
  crash mid-write cannot leave a truncated docket. L-2's ledger backup is why
  that matters.

What is not enforced mechanically today: axis B and axis C scores, and the
prediction requirement. Both are review disciplines until somebody writes the
check, and pretending otherwise would be the exact failure this charter's own
section 2 defect disclosure exists to avoid. The hardness criterion left this
list on 2026-08-05: `hard_criterion_violations` refuses a new proposal that
does not name its floor answer, and what remains a review discipline is
whether the named value is true of the case, which no field check can read.

## Related

- `docs/charters/LITERATURE_CHARTER.md`. When a reading must produce a
  proposal, and what its citations must carry.
- `docs/charters/CASE_SELECTION_CHARTER.md`. The hardness floor.
- `docs/charters/COMPUTE_BUDGET_CHARTER.md`. The rung caps the cost estimate is
  checked against.
- `docs/charters/ESCALATION_CHARTER.md`. Where an undecidable tie goes.
- `docs/standards/INNOVATION_STANDARD.md`. The five-stage path a new method
  walks after its proposal is approved.
- `LESSONS.md` P2, P5, L-19, L-24, L-26, L-27.
