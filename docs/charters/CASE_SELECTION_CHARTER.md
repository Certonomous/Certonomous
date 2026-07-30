# Certonomous Case Selection Charter

Version 1.0, dated 2026-07-30. Governs which cases the lab starts. It binds
overnight work, unattended work and anything an agent picks up on its own
initiative, which is the whole point of writing it down.

## 1. The line

> **No new case family enters the lab below HARD without written approval, and
> the floor holds when nobody is watching.**

The floor exists because the failure it prevents is invisible. An easy case
converges, produces a clean number, fills a report row and teaches the lab
nothing. It looks exactly like progress at every point except the one where
somebody asks what was learned. Nothing in the lab's machinery flags it, no
gate fails, and the cost is a night.

Unwatched is the operative word. A rule that only holds during a review is a
preference. This one is checked by asking, of any family started in the last
week, which HARD criterion it met and where that is recorded.

## 2. What HARD means

A case is HARD when it carries at least one of these. The list is the owner's
and it is closed. Adding a criterion requires her approval, not an argument.

1. **3D separated flow.** Separation that is not two-dimensional, where the
   answer depends on structure the span cannot be assumed away.
2. **Shocks.** Transonic, supersonic or hypersonic, where a discontinuity is
   part of the solution.
3. **Unsteady statistics.** The reported quantity is a statistic of an unsteady
   field: a shedding frequency, a band, a cycle-to-cycle repeatability, a
   phase-aligned waveform.
4. **Free surface.** An interface the solver has to capture.
5. **Rotating.** Rotating frames, rotating machinery, swirl that is not a
   boundary condition.
6. **Challenge-aligned.** The case produces one of the scored columns of the
   benchmark challenge the lab is entered in. Alignment is by scored column,
   not by topic resemblance.

**Hardness is a property of the regime, not of the shape.** This is the clause
that makes the charter usable rather than a geometry blacklist. The circular
cylinder is the lab's canonical easy body and its Re 3900 three-dimensional
rung is HARD on two counts at once, criterion 1 and criterion 3, because at
that regime the mean recirculation structure and the shedding statistics are
the entire question. The same cylinder at Re 40 is a regression test. Judge the
regime and the reported quantity, then the geometry.

The converse also binds. An industrial geometry solved in an easy regime is not
HARD. A wing at low incidence in attached steady flow is a regression test with
a nice picture attached.

## 3. Cylinder-class work

**Cylinder-class** means the canonical calibration bodies: cylinder, sphere,
cube, flat plate, and any of them in an attached or steady regime. These are
the eight bodies the credentials view already collapses into a single
calibration row rather than eight headline cards.

They are permitted, and they are permitted for exactly one purpose.

**ALLOWED.**

- **Regression tests.** Run to prove the machinery still gives the number it
  gave before, after a change to the solver stack, the mesh path, the harness
  or the container. The expected value is written down before the run.
- **Instrument checks.** A control whose answer is known independently of the
  thing being tested. L-26's sign check is the model: laminar periodic-hill
  flow at Re 100 with a reference run carrying no coded source at all, so the
  comparison needs no interpretation of physics. That check cost almost nothing
  and caught a sign error that had survived a full study across eighteen copies
  of the same dictionary.
- **Ladder rungs below a HARD rung**, where the easy rung exists to establish
  the convention the hard rung inherits. F5a's Re 100 through Re 2000 laminar
  rungs are this. They are not results, they are the baseline that makes the
  Re 3900 rung interpretable, and L-11 and L-17 are both about what happens
  when a later rung silently forks away from them.

**NEVER.**

- Presented as a new result. Not in a report, not on the wall, not in the
  refilled queue, not as an act.
- Counted toward challenge deficit reduction or wall credential value. It has
  neither. Charter 1 scores it zero on both axes by construction.
- Filmed. This is the owner's standing demo rule and it predates this charter:
  no toy cases on any camera surface, industry geometries only. Nothing here
  loosens it.
- Used to fill a night. If the queue is empty the answer is escalation, not a
  cylinder.

**The connection to the demo rule is not decoration.** The camera ban and this
floor are the same rule pointed at two surfaces. The ban keeps toy geometry off
the promotional surface. The floor keeps it out of the research program, which
is upstream and is where the night actually gets spent. Banning it only on
camera would produce a lab that does easy work and hides it, which is worse
than a lab that does easy work openly.

## 4. Starting a new family

Before any compute is spent on a family the lab has not run before:

1. **Name the HARD criterion**, by number from section 2, in the proposal.
2. **Name the reference.** The published experiment, benchmark or exact
   solution the result will be graded against, with its provenance tier from
   the literature charter. A family with no reference is a family that can
   produce no wall credential, and it has to justify itself on the other two
   axes alone.
3. **State what would disqualify the family.** The regime where the intended
   method stops applying, per `docs/standards/INNOVATION_STANDARD.md` stage 4.
   Any method that cannot state what it drops does not enter.
4. **Check the detector before the physics.** State the resolution of every
   quantity the family will report, and confirm it can express the deviation
   the family exists to measure. L-28: F2's shock detector snapped to face
   centres, emitted eight distinct values across 280 solves, and could not
   express the 0.0439 chord deviation the gate was written around because its
   own increment was 0.0524 chord. That is a zero-compute check and it kills a
   family before it starts.
5. **Check the mesh can resolve the mechanism.** L-25: F7a recorded wall
   friction as refuted on a mesh where the leading film was one cell deep, and
   the mechanism was hunted for two more sessions before the same control at
   a/128 separated the cases by 5.5 percentage points. A null result is
   evidence of absence only when the instrument could have seen it. State the
   resolution the mechanism needs and compare it against the intended mesh.

Steps 4 and 5 cost nothing and both have already caught a published conclusion
after the fact. Doing them first is the only difference.

## 5. Approval, and what "explicit" means

Below HARD, a new family needs the owner's approval. Explicit means all of:

- Written, in the docket, not inferred from a conversation.
- Naming the family and what it is for.
- Predating the first core-second spent on it.

**Scaffolding on disk is not approval.** L-18. A case directory that looks
legitimate, with real scripts and a real mesh dated from earlier work, reads as
permission and is not. Half-configured scaffolding is exactly what gets left
behind when somebody abandoned a case for a reason, and the one that was picked
up ran 57 minutes producing Cd of minus 55.3 on a wing because its force
normalisation was still at placeholder values of 1.0 throughout.

**Neither is inheritance.** An agent's brief does not carry the previous
agent's approvals. Restate them.

## 6. Inheriting a case somebody else staged

A staged case is not a selected case. Two lessons cover this and they are
different failures.

- **L-11.** `case_preflight.sh` passing is necessary and not sufficient. It
  checks internal consistency and has no memory of what a sibling rung did, so
  it cannot see a silent fork in methodology. Diff the inherited case's
  `constant/turbulenceProperties` and its `0/` field list against the previous
  rung before launching. The F5a Re 3900 case was staged as kOmegaSST inside a
  deliberately laminar ladder and passed preflight cleanly.
- **L-17.** Reverting the decision is not reverting its consequences. After
  that revert the mesh was left alone as a Re-specific choice, and its
  near-wall first cell had been sized by the URANS staging's own y-plus
  formula, which disagrees with the ladder's laminar formula by 55 percent at
  that Reynolds number. Enumerate every parameter the wrong decision could have
  influenced and check each one against the sibling convention.

## 7. Worked examples

**Passes.** The three-dimensional cylinder rung at Re 3900. Criterion 1 and
criterion 3. Reference: Jiang and Cheng 2017, read in full by a prior session
with its tables reproduced in our own record. The extrusion itself produced a
transferable finding, L-13, that coarsening the spanwise cell fixes a cell
determinant failure that refining it makes worse.

**Passes.** The NASA wall-mounted hump. Criterion 1. Reference: Greenblatt et
al. experiment, with NASA's own SST result available as a second anchor. Our
converged baseline separates at x/c 0.6544 against an experimental 0.665 and
reattaches at 1.2534 against 1.100.

**Fails, and would have to be escalated.** A steady attached NACA 0012 at two
degrees to check the solver still runs. That is a regression test. It is
allowed under section 3, it is recorded as a regression test, and it never
appears as a result.

**Fails on a technicality worth naming.** A free-surface case is HARD by
criterion 4, but F7a's headline finding was a metric artifact twice over: a
coarse-mesh sign flip and a 40 percent improvement from disabling interface
compression, both retracted when the same solves were re-measured with a
depth-integrated front metric. Meeting the hardness floor buys the family a
start. It buys nothing about the result, which is the verification charter's
problem.

## 8. An unresolved conflict, flagged not settled

> **CONFLICT. Two rules the owner has set point different ways, and this
> charter does not resolve it.**

The camera rule names shapes. "No toy cases (sphere, cube, plate, cylinder) on
any camera surface, industry geometries only." Round 7, the same week, restates
it: toy cases stay banned.

The rehearsed shoot contains two cylinder acts. Act 1 is vortex shedding behind
a circular cylinder at Re 100, graded PASS against the Roshko-Williamson
correlation at 0.77 percent. Act 5 is a hypersonic blunt cylinder at Mach 8,
graded PASS against the Billig correlation at 0.70 percent. Both are in
`FILMING_COMMANDS.md` and both are in the nine-act gate table.

Section 2 of this charter would call both HARD, because it judges the regime
rather than the shape: act 1 is unsteady statistics, act 5 is a shock case.
That reading makes the shoot consistent. The camera rule as literally written
makes it a violation twice over.

Somebody has to choose. Either the camera rule means "toy regime" and its
wording should say so, or it means "toy shape" and two rehearsed acts need
replacing. This charter takes no position, because both readings trace to the
owner and picking one would be inventing policy. It goes to her.

## 9. Enforcement

- The HARD criterion number is a required field in the proposal. A proposal
  without one is disqualified under charter 1 and never reaches the queue.
- The regression-test label is written into the record at launch, not applied
  afterwards. A cylinder run that was not labelled a regression test before it
  started cannot be labelled one after it produces a number.
- `scripts/audit_transcripts.sh` and `scripts/audit_camera_discretion.sh` cover
  the camera half of the toy-geometry rule. Neither of them can see the
  research program, which is why this charter exists as text rather than as a
  test.

**PROPOSAL.** Nobody has ruled on this. The cleanest mechanical enforcement
would be a required `hard_criterion` field on the proposal JSON schema, refused
at intake when absent or when set to a value outside the closed list in section
2. That moves the floor from discipline into the harness, which is the move
D12 already made for orphaned collectors after writing the rule down
demonstrably failed to reduce the rate.

## Related

- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. Scoring, and the
  disqualifiers.
- `docs/charters/ESCALATION_CHARTER.md`. How a below-floor family gets asked
  for.
- `docs/DEMO_DISCRETION_CHARTER.md`. The camera half of the toy-geometry rule.
- `LESSONS.md` L-11, L-13, L-17, L-18, L-25, L-28.
