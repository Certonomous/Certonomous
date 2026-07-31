# Open proposals across the charters

Version 2.1, dated 2026-07-31. Every point in the eight charters where the lab
is **proposing** rather than **recording**, collected so the owner can react to
the whole set without reading the whole set.

Everything listed here needs her decision. Everything not listed here traces to
a recorded instruction, an existing standards document, or a lesson. That
distinction is the reason this file exists: the lab must never present its own
invention as her policy.

**What changed in 2.0.** Two proposals closed because the thing they asked for
now exists. Every remaining one was rewritten so the answer is a word rather
than a paragraph: named options, the cost of each, and the lab's
recommendation where it has one. Three new decisions arrived from a single
day's findings. And the conflict at the top is unchanged and still unresolved,
because only she can resolve it.

**What changed in 2.1.** The charters were reviewed against a week of findings
and six proposals were filed to the docket under her standing authorization, so
they are not here. Three things are: **C-4**, a new decision, because reviewing
the monitor as a set showed that six of its rules were never held to the replay
requirement and only she can decide whether they stay in force while unmeasured.
**P-8.1**, sharpened again and split, because the checker is buildable now and
the emitter is not the urgent half. And two items at the end that need a person
rather than a ruling, one of which is a discrepancy between a briefing and the
record and is the more important of the two.

## How to answer this file

Each item carries a label like **P-1.1** or **C-1** and a set of options
labelled **A**, **B**, **C**. "P-1.1: A" is a complete answer. Anything with no
recommendation is one where the lab believes it has no standing to have a
preference, and says so rather than inventing one.

---

## Conflicts. These are not proposals, and they need a ruling

### C-1. The camera rule names shapes; two rehearsed acts are cylinders

Charter 3, section 8. Unresolved since it was raised, and nothing in this
revision moves it.

"No toy cases (sphere, cube, plate, cylinder) on any camera surface, industry
geometries only" is her rule, restated as recently as the pre-shoot round. The
rehearsed shoot contains act 1, vortex shedding behind a circular cylinder at
Re 100, PASS at 0.77 percent against Roshko-Williamson, and act 5, a hypersonic
blunt cylinder at Mach 8, PASS at 0.70 percent against Billig. Both are in
`FILMING_COMMANDS.md` and both are in the nine-act gate table.

- **A. The rule means toy regime.** Hardness is a property of the regime, not
  the shape, which is what charter 3 section 2 already says for the research
  program. Under that reading act 1 is HARD by criterion 3, unsteady
  statistics, and act 5 is HARD by criterion 2, shocks. The shoot is
  consistent, no act is replaced, and the camera rule's wording is amended to
  say regime.
- **B. The rule means toy shape.** The wording stands as written, the shoot is
  in violation twice over, and two rehearsed and passing acts need replacing
  with industry geometries before filming.

Cost of A: the ban becomes a judgement rather than a list, so somebody has to
apply it, and a cylinder at Re 40 has to be refused on regime grounds by a
person rather than by a word match. Cost of B: two acts that pass their gates
at 0.77 and 0.70 percent come off the shoot, and both are among the cleanest
numbers the lab has.

**The charters take no position.** Both readings trace to her, and picking one
would be inventing policy on the surface she cares most about.

### C-2. Rule S7 fires on two thirds of the lab's completed work

Charter 4, section 5, and `docs/standards/MONITOR_STANDARD.md`. New, and it is
a decision rather than a proposal because the rule is already in force.

Measured across every steady solver log the lab has archived, 106 of them, the
oscillatory-divergence rule fires ungated on 68 and reaches FATAL on 65. Every
one of those runs completed and its results are on the record. Four tightenings
were measured and none rescued it: residual level must stop improving still
fires on 68, full-window persistence 40, a 200 iteration growth baseline 59, a
fourfold growth factor 23. It also cannot separate the two logs of the case it
was written for.

It currently ships behind a gate that requires a residual target and stays
silent on any field that has already reached it. That gate is reasoning from
the proposal's own wording plus S6's measured behaviour. It is not a
measurement, because the archived logs do not record the residual target each
run was aiming for, so the corpus cannot be replayed with the gate in place.

- **A. Keep it gated**, and keep it labelled the weakest rule in the standard
  with the fire rate recorded next to it, which is the state today.
- **B. Withdraw the branch**, and record the four measured tightenings as the
  evidence for withdrawal.
- **C. Keep it, and buy the measurement**: start recording the residual target
  in every future log so the gate becomes replayable, and revisit in a month
  with a corpus that can answer the question.

Cost of A: one rule in the monitor is trusted on reasoning nobody can check.
Cost of B: the graceful-degradation failure family loses a detector, and the
knowledge base fact it was built on is real. Cost of C: a month of the current
state plus a small change to what the harness records. *Lab recommends C.*

### C-3. Five acts declare a worker fleet on a path that dispatches nothing

Charter 4, section 6, and `w3-hump-fleet-honesty` in the docket. New.

The hump act calls `roster.set_workers(ranks)` inside its warm-solve branch,
where the mesh and the solve are both restored from cache, nothing is
dispatched, and the elapsed time is computed across a zero-length interval and
clamped to one second before being spent to the ledger. The declaration reaches
the worker numeral, the roster and the spend line.

The first run of the weekly audit found this is not one act. It is five:
`nasa_hump.py`, `ahmed_body.py`, `crm_wingbody.py`, `geometry_study.py` and
`onera_m6.py` all declare a non-zero fleet inside a cache-restore branch.

- **A. The act performs the work it displays.** The warm path stops being warm
  for the solve stage, which costs the demo its replay time.
- **B. The act displays no fleet on a restored path.** The worker numeral shows
  zero when nothing is running, and the record says why.

Cost of A: the acts get slower on camera, and the warm cache exists precisely
so they do not. Cost of B: the fleet numeral, which is one of the more
legible things on screen, goes quiet during a warm replay. **Moving the
declaration earlier to make the timing look right is not an option**, because
it invents a fleet the run never used. *Lab recommends B*, and notes the
decision is hers because it is a camera surface.

### C-4. Six monitor rules were never held to the replay requirement

`docs/standards/MONITOR_STANDARD.md` section 3, new. A decision rather than a
proposal, because the rules are already in force and demoting them changes a
standard.

Reviewing the monitor as a set rather than rule by rule: **seven of eleven rules
have never been replayed against the archive.** S1 through S5 have no corpus, no
fire count and no fatal count behind them, S6 is measured only as a side effect
of S7's measurement, and S11 is measured differently and correctly. The three
that were replayed before adoption, S8, S9 and S10, are the three the lab can
defend. The one adopted on reasoning alone, S7, is the one that fires on 68 of
106 completed runs.

The cause is not carelessness. The six unmeasured rules shipped with the monitor
before the reading program existed, so they predate disqualifier 10, which
requires a new detection rule to state its archive behaviour before adoption.
**They were grandfathered without anybody deciding to grandfather them.**

- **A. They stay in force at their current severities**, and section 3.1 keeps
  labelling them hypotheses until somebody replays them. The replay is filed and
  approved as `w7-replay-the-grandfathered-monitor-rules`, so this option is
  "leave them alone and let the measurement arrive".
- **B. They stay in force and every unreplayed rule is demoted to WATCH** until
  it has a fire count, so an unmeasured rule cannot stop a run.
- **C. The replay is required before the next filmed session**, and any rule
  that cannot be replayed is withdrawn.

Cost of A: for however long the replay takes, a FATAL from S1 or S2 is trusted
on reasoning. Both are almost certainly sound, which is exactly the argument
that was made for S7. Cost of B: a genuine floating point exception stops
counting as fatal, which is the one rule nobody wants weakened, so B is probably
wrong in the specific case that matters most. Cost of C: a deadline on a
zero-compute afternoon.

*Lab recommends A*, and notes that the recommendation is weak and that the whole
point of the finding is that "almost certainly sound" is what was said about S7.

---

## Proposals, by charter

### Charter 1, goals and research proposals

**P-1.1. Extend the gain table, and refuse an unrecognised `source_kind`.**
Section 2, axis A. The ranking function's `_GAIN_POINTS` covers `gate`,
`capability`, `ledger` and `report`. The docket in use also carries
`measurement`, `reading` and `challenge`, and all three silently take the
default of 2.0. That is 24 of 55 proposals ranked on a default, including all
four challenge-aligned proposals, which are the ones axis C exists to promote.

Proposed values, stated so the answer is a word:

| `source_kind` | proposed points | reasoning |
| --- | --- | --- |
| `measurement` | 3.0 | It produces a number against a stated criterion, which is what `gate` scores. |
| `challenge` | 3.0 | It moves a scored column, which is the one axis with an exact metric. |
| `reading` | 1.5 | A reading that yields a proposal is worth more than a report and less than a measurement. |

- **A. Adopt the three values above, and make an unknown `source_kind` a
  proposal violation.**
- **B. Adopt the refusal only**, and leave the values to her.
- **C. Leave it.** A default that fires on 24 of 55 proposals stays the rule.

*Lab recommends A.* The refusal matters more than the numbers: a silent default
on the lab's most important cases is the failure, and any stated value is
better than an unstated one.

**P-1.2. Does axis B, wall credential value, exist at all?** Section 2. No such
term, field or formula exists in the repository today. The wall exists and its
tiers are ranked, but nothing assigns a credential a value. The 0 to 3 anchors
in the charter are the lab's draft, built on her existing wall curation rule.

- **A. The axis exists, with the drafted anchors.**
- **B. The axis exists, with anchors she sets.**
- **C. There is no such axis.** Wall value is a curation decision at display
  time and never a ranking input.

*No recommendation.* The wall is her product surface and the lab has no
standing to decide whether producing a row on it is a research objective.

**P-1.3. Dominance ordering instead of a weighted sum.** Section 3. The three
axes are in different units and combining them requires exchange rates nobody
has set.

- **A. Dominance, then her named priority, then the docket.** A proposal
  outranks another when it is at least equal on all three and strictly better
  on one; otherwise the tie goes to whichever axis she has named as current
  priority; otherwise it escalates. Deliberately produces ties.
- **B. A weighted sum**, with weights she sets.

*Lab recommends A*, on the grounds that a rule which always produces a winner
is a rule that hides the decision. Cost of A: more escalations.

**P-1.4. Disqualifier 10, the archive replay a detection rule owes.** Section
4, new in charter version 1.1. A proposal that adds a rule, signature, gate or
check which will fire on the lab's own work states what it does to the archive
before adoption: the corpus, the fire count, the fatal count, and its behaviour
on the case that motivated it. S7 is the measured reason, C-2 above.

- **A. Adopt as a disqualifier**, refused at intake.
- **B. Adopt as a required field**, reported but not refusing.
- **C. Leave it as a review discipline.**

*Lab recommends A*, on D12's precedent: writing the rule down and hoping was
tried for orphaned collectors and did not change the rate.

### Charter 2, literature review

**P-2.1. A citation audit. PARTLY CLOSED, and what remains is smaller than it
was.** Section 8. The proposal was a `scripts/audit_citations.sh` walking every
record for citation-shaped strings.

What now exists and runs weekly, in `scripts/self_audit.py`: repo-rooted
backticked paths in every website record are resolved against disk, 273 of them
across 73 records on the first run, all resolving; and the machine-readable
`report` and `report_json` fields in the campaign JSON companions are resolved
too. That covers the half of the original proposal that was about paths.

What remains open is the half that was about tiers: **should a citation-shaped
string carrying no provenance tier in the same block be a finding?**

- **A. Yes, as a WARN.** It cannot check truth, only discipline, and it will
  have false positives on prose that mentions a paper without citing it.
- **B. No.** Tier discipline stays a review discipline.

*Lab recommends A*, at WARN rather than FAIL, on the same asymmetry every other
check in that file is tuned on.

### Charter 3, case selection

**P-3.1. A required `hard_criterion` field on the proposal schema.** Section 9.
Refused at intake when absent or outside the closed list of six HARD criteria.
This moves the hardness floor out of discipline and into the harness, which is
the move D12 already made for orphaned collectors after writing the rule down
demonstrably failed to reduce the rate.

- **A. Required and refusing.**
- **B. Required and reported**, so the gap is visible without blocking.
- **C. Stays a review discipline.**

*Lab recommends A.* Cost: the drafting scripts need the field added, and a
proposal for a family that is genuinely below the floor has to say so out loud
and get written approval, which is the point.

### Charter 4, verification

**Nothing proposed, and version 1.3 added three sections without changing
that.** Every clause traces to a lesson, an existing standard, a format already
in use, or a defect whose fix is already in the code. That includes all of
section 6, the display layer: the certificate's interval guard,
`reportable_band`, and the monitor reading its governed constant are landed
code, not drafts. It also includes the three sections added in 1.3. Section
3.2, the two ways an observed order lies, is two measured ladders. Section 3.3,
a guard measures the rungs the fit used, is a landed fix in `uq.py`. Section 14,
attribution, is three findings that travelled to the wrong artifact and were
each corrected against the artifact's own file.

The live defect this file previously carried has been corrected. The
consolidated FD table in `ACTIVE_RESEARCH.md` graded A4's 10.04 percent as PASS
against the retired band while two other records graded the same number
CONDITIONAL. It now reads CONDITIONAL, the number is unchanged, and the check
that found it runs every week.

Three findings from the audit's first run are escalations rather than
proposals, and they are listed at the end of this file.

### Charter 5, result priority

**The entire charter is still a draft.** It is version 0.2 and it stays at 0.x
until she rules. Her own note on it is that she still needs to think about how
to go about it, and the document takes that literally.

**The seven open questions are now a decision sheet**, section 8 of that
charter, each reduced to named options with the trade and a recommendation
where the lab has one. They are answerable as "D2: C". Summarised here so the
shape is visible without opening the file:

| Item | The question | Lab's recommendation |
| --- | --- | --- |
| D0 | Does the trade block bind regardless? | A, yes |
| D1 | Which ordering governs a case in two classes? | none |
| D2 | Strict lexicographic, or a tolerance band? | C, banded when it first matters |
| D3 | Higher-priority quantity has no reference? | A, purpose over availability |
| D4 | Binds selection or only reporting? | C, at adoption not investigation |
| D5 | Fidelity chip versus rank? | B, rank blocks |
| D6 | Who declares an ordering for an unlisted class? | A, the proposal drafts it |
| D7 | Does a trade expire? | B, a date as well as a trigger |

**P-5.2. The six draft orderings themselves.** Section 4. External aerodynamics
and the challenge are expansions of her own two examples. Gradients and
adjoints has a real anchor, because the FD grading standard already fails on
any sign flip regardless of the aggregate, which is a priority ordering already
in force. Free surface, uncertainty quantification and unsteady statistics are
the lab's drafts. Each now carries a **Violated when** line so the ordering is
breachable rather than decorative, and 4.5 carries a new rank zero,
admissibility, after five acts ranked a non-conclusive refinement band as
though it were measured.

- **A. The six orderings as drafted.**
- **B. The two that are hers, and the other four go back to the docket.**

*No recommendation on B versus A for the four drafted classes.* The lab
recommends adopting 4.1 and 4.2 as written, because they are hers already.

### Charter 6, compute budget

**P-6.1. Spot versus on-demand policy, and it is currently blocked.** Section
5. No spot policy, no on-demand policy, no dollar figure and no cost-per-hour
convention exists anywhere in the repository, and the instance cannot read its
own billing, so no spend cap can be reported from here without fabricating it.

The unblock is small and named: a read-only instance role with
`cloudwatch:DescribeAlarms` and `ce:GetCostAndUsage`, or the numbers pasted
directly and recorded as reported-by-owner. The proposed policy is drafted so
the decision is one word once it unblocks: interruptible work on spot,
gate-deciding and unresumable work on demand, filming always on demand.

- **A. Attach the read-only role.**
- **B. Paste the numbers**, recorded as reported-by-owner.
- **C. Leave it blocked**, and the dollar line keeps saying so.

*Lab recommends A*, because it is the only option under which the number is
measured rather than transcribed.

**P-6.2. Gross or cleaned, on every published spend figure.** Section 2, new.
The published `solver_core_hours` counter re-derives exactly from the ledger,
which is the check that matters and it passes, and it still carries 26.98
core-hours of host stall inside a 239.259 core-hour headline, 11.3 percent of
it. The evidence that these are stalls and not solver cost is measured: six
rows near 16,300 seconds land in two tight wall-clock clusters and are shared
across two independent solver families, against a cylinder median of 2.4
seconds.

- **A. Every published spend figure declares itself gross or cleaned and names
  the cleaning rule.** The wall would carry both numbers.
- **B. Publish the cleaned figure only**, with the rule stated once.
- **C. Keep publishing gross**, and the audit reports the contamination every
  week, which is the state today.

*Lab recommends A.* Cost: one more line on the wall. C is not dishonest, since
the figure is exactly what it says it is, but it means the lab's headline
compute number is 11 percent host stall and only the audit says so.

### Charter 7, escalation

**P-7.1. The free-spend thresholds.** Section 4. Nobody has set a number. The
proposed bands are calibrated against decisions already on the record rather
than invented: free up to 60 core-minutes per proposal, notify from 60 to 240,
docket above 240, and docket above 480 aggregated across one night. The
calibration points are the standing 60 core-minute default for a new capability
and the 480 core-minute run that was held for an explicit go.

- **A. The table as drafted, with both riding rules.**
- **B. The table with numbers she sets, both riding rules kept.**
- **C. No thresholds.** Everything above trivial escalates.

Two rules ride with the table and need her assent as much as the numbers do: an
estimate that turns out wrong crosses the threshold too, so a job estimated at
50 that reaches 240 is stopped and escalated rather than finished quietly; and
the aggregate band is per night rather than per agent, because several agents
each staying under their own limit is how a night's spend escapes attention.

*Lab recommends A*, and notes that the riding rules matter more than the
numbers: without the first one, the threshold prices optimism.

### Charter 8, reporting

**P-8.1. A morning report generator. SPLIT IN TWO, and the small half is
already approved.** Charter 8 section 12. The proposal was a
`scripts/morning_report.py` emitting all six sections from their named sources.

Two of the three behaviours that were the point of it now exist in
`scripts/self_audit.py` and run weekly: a cited artifact that is missing from
disk is a finding, which is what would have caught the F2 headline two days
earlier, and FD grades are recomputed against the current standard rather than
copied forward, which is what found A4.

Charter 8 version 2.0 changed what is left. Section 2 now freezes the frame:
six heading strings matched literally in order, a section count computed rather
than typed, a `Source:` line under every section carrying content, and two
reserved words, `nothing` for an empty section and `PENDING: <path>` for one
whose artifact could not be read. That makes a **checker** possible
independently of an emitter, because it runs over a report a human wrote by hand
this morning. The checker is filed and approved as
`w8-morning-report-frame-checker`.

What is left for her is the emitter.

- **A. Build the emitter too**, reading the audit's JSON output for the parts
  that already exist rather than reimplementing them.
- **B. Keep assembling by hand and let the checker police it.** Sections 1, 2, 4
  and 6 are hand-assembled today and the checker would catch a malformed one
  either way.

*Lab recommends A*, weakly. Cost of A: a zero-compute afternoon. Cost of B: the
frame is enforced and the assembly still depends on somebody remembering all six
sources, which is the failure charter 8 section 3 was written to name.

---

## Escalations from the audit's first run

Not proposals. Findings that need a person, listed here because this is the
file she reads. Full output is in the audit's own report.

1. **The credentials wall would change materially on a rebuild.** Re-deriving
   each credential from its own result file through the same function the
   builder uses, `ahmed_25` moves from VALIDATED to SOLVER-BACKED, its measured
   figure from 0.3219 to 0.3041, and its envelope from a settling band to
   plus or minus 0.02 across a three-mesh refinement study that came back
   inconclusive. `naca0012_wing` moves from 0.02229 to 0.01205, which changes
   its stated deviation from 148 percent to 34 percent. `ahmed_25` is the
   wall's only VALIDATED row. Nothing has been changed. This needs a decision
   about which mesh the wall displays, and it is the same reconciliation
   `campaign/AHMED_BODY_RECONCILIATION.md` already documents.
2. **The nine-act gate table's Ahmed row no longer re-derives from the
   transcript it cites.** The transcript still carries Cd 0.3041 and 6.7
   percent, but under a different row shape than `gate_table.py` parses, so a
   regeneration would replace a correct row with PENDING and the footer's "9 of
   9 carry a graded number" would become 8. The generator, not the record, is
   the stale half.
3. **The shipped demo bundle still manufactures confidence intervals.**
   `dist/certonomous-demo/sdk/chief_engineer/certificate.py` carries the
   pre-fix caption with no interval test, so any certificate produced from the
   bundle seals a statistical claim the run never made. The tracked copy is
   fixed. The bundle is a separate artifact and was not rebuilt.

---

## Escalations from the charter review, 2026-07-31

Not proposals and not rulings. Two things that need a person.

1. **A briefing describes a git incident the repository has no record of, and
   the charter was written from the record instead.** The charter revision was
   briefed with the account that three agents destroyed each other's uncommitted
   work with `git reset --hard`, `git stash` and a repo-wide `git add`. Escalation
   charter section 3 now carries the standing rules against all four commands,
   because they are right whatever the history is. **The incident as described is
   not in the record**, and this is recorded rather than written up as though it
   were, per the fabrication rule this file exists under. What the record does
   hold: `LESSONS.md` L-12, where `git add -A <path>` staged 1,187 files and 25
   million insertions, twice, **by one author who explicitly records that two
   agents had misfiled it as a shared index race and that it was not one**;
   `LESSONS.md` L-9, where an agent was wrongly accused of destroying shared work
   on the strength of a directory count; commit `ba47307a`, where two studies
   another session left uncommitted were verified and committed rather than
   discarded; and commit `5675eb6b`, whose own message notes it carries another
   agent's in-flight work edited in the same tree at the same time. A repo-wide
   search finds no `git reset --hard` and one benign `git stash` reference.
   **Either there is an incident outside this repository's records, or the
   account has drifted, and the second is the failure L-9 and section 14 of the
   verification charter both describe.** The clause stands either way. What needs
   a person is which of the two it is, and if it is the first, where that record
   lives so the clause can cite it.
2. **S9 assesses a third of a second as FATAL, and no floor has been approved.**
   The wall-time rule is purely relative, so a solver whose 99th percentile is 3
   milliseconds gets a threshold of 30. Five reduced-order rows of 0.30 to 0.43 s
   are assessed FATAL on that basis. The detection is arguably right, since those
   runs really were hundreds of times slower than their own baseline, which is
   what host contention looks like, and the severity is out of proportion to the
   wall time. **An absolute floor would fix it and is deliberately not added**,
   because no such floor was in the approved proposal and inventing a threshold
   is how a rule stops meaning what it says. Recorded in the monitor standard as
   an observation and repeated here because this is the file she reads.

---

## What is recorded, not proposed

Listed so the boundary is visible. None of the following is the lab's
invention:

- The three axes themselves, and their names. Hers.
- The knowledge-gain-per-core-minute formula. Already implemented and tested.
- Zero fabricated citations. Hers, and the standing record.
- The provenance tiers. Already in force in the literature review.
- The six HARD criteria. Hers.
- The toy-geometry camera ban. Hers.
- The FD grading standard and the retirement of the old band. Already in force.
- The `NOT_PASSING_REGISTER.md` failure format. Already in force.
- The core-minute unit and the cost-honesty rule. Already in force.
- The auto-stop contract, in every detail. Read off the installed script.
- The keep-alive expiry. Already in force.
- "Initiative comes from the lab, the veto stays with the human." Already the
  agenda's governing statement.
- The six morning-report sections and their order. Hers. The frame in charter 8
  section 2 is the lab's rendering of them into strings a checker can match, and
  it adds no section, removes none, and reorders nothing.
- The whole of charter 4 section 6, the display layer. Every clause is a fix
  that is already landed in code: the certificate's interval guard,
  `reportable_band` and `not_conclusive_reason` in `uq.py`, and the monitor
  reading `FLAG_MULTIPLE` rather than a literal.
