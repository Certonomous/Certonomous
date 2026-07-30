# Open proposals across the charters

Version 1.0, dated 2026-07-30. Every point in the eight charters where the lab
is **proposing** rather than **recording**, collected so the owner can react to
the whole set without reading the whole set.

Everything listed here needs her decision. Everything not listed here traces to
a recorded instruction, an existing standards document, or a lesson. That
distinction is the reason this file exists: the lab must never present its own
invention as her policy.

## The one conflict, which is not a proposal

**C-1. The camera rule names shapes; two rehearsed acts are cylinders.**
Charter 3, section 8.

"No toy cases (sphere, cube, plate, cylinder) on any camera surface" is her
rule, restated as recently as the pre-shoot round. The rehearsed shoot contains
act 1, vortex shedding behind a circular cylinder at Re 100, PASS at 0.77
percent against Roshko-Williamson, and act 5, a hypersonic blunt cylinder at
Mach 8, PASS at 0.70 percent against Billig. Both are in `FILMING_COMMANDS.md`
and the nine-act gate table.

Either the rule means toy **regime** and its wording should say so, which makes
the shoot consistent, or it means toy **shape** and two acts need replacing.
Both readings trace to her. The charters take no position.

## Proposals, by charter

### Charter 1, goals and research proposals

**P-1.1. Extend the gain table, and refuse an unrecognised `source_kind`.**
Section 2, axis A. The ranking function's `_GAIN_POINTS` covers `gate`,
`capability`, `ledger` and `report`. The docket in use also carries
`measurement`, `reading` and `challenge`, and all three silently take the
default of 2.0. That is 24 of 55 proposals ranked on a default, including all
four challenge-aligned proposals, which are the ones axis C exists to promote.
Proposed: add the missing kinds with stated point values, and make an unknown
`source_kind` a proposal violation rather than a silent default.

**P-1.2. The whole of axis B, "wall credential value".** Section 2, axis B. No
such term, field or formula exists in the repository today. The wall exists and
its tiers are ranked, but nothing assigns a credential a value. The proposed 0
to 3 anchors are the lab's draft, built on her existing wall curation rule.
Needs her ruling on whether the axis exists at all, and then on the anchors.

**P-1.3. Dominance ordering instead of a weighted sum.** Section 3. The three
axes are in different units and combining them requires exchange rates nobody
has set. Proposed: a proposal outranks another when it is at least equal on all
three and strictly better on one; otherwise the tie goes to whichever axis she
has named as the current priority; otherwise it goes to the docket. Deliberately
produces ties rather than manufacturing a ranking.

### Charter 2, literature review

**P-2.1. A citation audit script.** Section 8. A
`scripts/audit_citations.sh` that walks every markdown record for
citation-shaped strings and flags any carrying no provenance tier in the same
block. It cannot check truth, only discipline, and would be a review aid with
expected false positives, in the shape of `audit_camera_discretion.sh`.

### Charter 3, case selection

**P-3.1. A required `hard_criterion` field on the proposal schema.** Section 9.
Refused at intake when absent or outside the closed list of six HARD criteria.
This moves the hardness floor out of discipline and into the harness, which is
the move D12 already made for orphaned collectors after writing the rule down
demonstrably failed to reduce the rate.

### Charter 4, verification

**Nothing proposed.** Every clause traces to a lesson, an existing standard, or
a format already in use.

One live defect is recorded rather than silently fixed: the consolidated FD
table in `ACTIVE_RESEARCH.md` grades A4's 10.04 percent as PASS against the
retired band, while two other records grade the same number CONDITIONAL under
the current standard. That is a correction, not a decision.

### Charter 5, result priority

**The entire charter is a draft.** It is version 0.1 and it stays there until
she rules. Her own note on it is that she still needs to think about how to go
about it, and the document takes that literally.

**P-5.1. The trade statement block**, proposed as binding regardless of how the
orderings resolve. Section 3.

**P-5.2. Six draft orderings**, one per mission class. Section 4. External
aerodynamics and the challenge are expansions of her own two examples. Gradients
and adjoints has a real anchor, because the FD grading standard already fails on
any sign flip regardless of the aggregate, which is a priority ordering already
in force. Free surface, uncertainty quantification and unsteady statistics are
the lab's drafts.

**P-5.3 through P-5.9. Seven open questions**, named in section 6 rather than
papered over. The two the lab most wants answered:

- **Q2.** Is the ordering strictly lexicographic, or is there a tolerance band
  inside which rank 1 counts as tied so rank 2 decides? Strict is clean and
  brittle. A band needs a number per class that nobody has set.
- **Q4.** Does the ordering bind method selection or only reporting? Her framing
  is about choosing between methods, so it binds selection. But a strict
  selection rule on the challenge ordering would have blocked the closure work
  early, because its first rounds did not move the score.

The other five: which ordering applies when a mission spans two classes, what
happens when the higher-priority quantity has no reference, how the fidelity
chip interacts with rank, who declares an ordering for an unlisted class, and
whether a trade ever expires on its own.

### Charter 6, compute budget

**P-6.1. Spot versus on-demand policy, and it is currently blocked.** Section 5.
No spot policy, no on-demand policy, no dollar figure and no cost-per-hour
convention exists anywhere in the repository, and the instance cannot read its
own billing, so no spend cap can be reported from here without fabricating it.
The unblock is small and named: a read-only instance role with
`cloudwatch:DescribeAlarms` and `ce:GetCostAndUsage`, or the numbers pasted
directly and recorded as reported-by-owner. The proposed policy is drafted so
the decision is one word once it unblocks: interruptible work on spot,
gate-deciding and unresumable work on demand, filming always on demand.

### Charter 7, escalation

**P-7.1. The free-spend thresholds.** Section 4. Nobody has set a number. The
proposed bands are calibrated against decisions already on the record rather
than invented: free up to 60 core-minutes per proposal, notify from 60 to 240,
docket above 240, and docket above 480 aggregated across one night. The
calibration points are the standing 60 core-minute default for a new capability
and the 480 core-minute run that was held for an explicit go.

Two rules ride with the table and need her assent as much as the numbers do: an
estimate that turns out wrong crosses the threshold too, so a job estimated at
50 that reaches 240 is stopped and escalated rather than finished quietly; and
the aggregate band is per night rather than per agent, because several agents
each staying under their own limit is how a night's spend escapes attention.

### Charter 8, reporting

**P-8.1. A morning report generator.** Section 10. A `scripts/morning_report.py`
emitting all six sections from their named sources, printing "nothing" for an
empty section and PENDING for an unavailable artifact. Two behaviours are the
point of it: refusing to emit a row whose cited artifact is missing from disk,
which would have caught the F2 headline two days earlier than it was caught,
and recomputing FD grades against the current standard rather than copying them
forward.

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
- The six morning-report sections and their order. Hers.
