# Certonomous charters

A charter is a standing rule the lab holds itself to when nobody is watching.
It is not a mission statement and it is not a summary of good intentions. The
test every charter here has to pass is simple.

> **If no decision could ever violate it, it is not a charter and it does not
> belong in this directory.**

That is the working standard, and it is why these documents carry numbers,
named files, bright lines and worked examples rather than principles. A clause
you cannot point at a decision and say "that broke it" is decoration, and it
gets deleted at the next revision.

## The eight

| # | Charter | The one line it turns on |
| --- | --- | --- |
| 1 | [Goals and research proposals](GOALS_AND_PROPOSALS_CHARTER.md) | A proposal that cannot come out more than one way is not a proposal. |
| 2 | [Literature review](LITERATURE_CHARTER.md) | Zero fabricated citations, and the tolerance is zero. |
| 3 | [Case selection](CASE_SELECTION_CHARTER.md) | No new family below HARD without written approval, watched or unwatched. |
| 4 | [Verification](VERIFICATION_CHARTER.md) | A result without a retained evidence record is not a result. |
| 5 | [Result priority](RESULT_PRIORITY_CHARTER.md) | When two methods validate different quantities, the declared ordering picks, and the trade goes on the record. |
| 6 | [Compute budget](COMPUTE_BUDGET_CHARTER.md) | Every budget is measured, and every hold on the box expires by itself. |
| 7 | [Escalation](ESCALATION_CHARTER.md) | The lab decides what is reversible and cheap. Everything else goes to the docket. |
| 8 | [Reporting](REPORTING_CHARTER.md) | Six sections, fixed order, every morning, including the mornings with nothing good in them. From version 2.0 the headings are fixed strings, so a missing section fails a match rather than a taste test. |

## How to read one

Every charter follows the shape of `docs/DEMO_DISCRETION_CHARTER.md`, which was
written first and set the house style:

1. A version and a date.
2. One bright testable line, stated before any of the reasoning.
3. Numbered sections working that line out, with explicit lists of what is
   required, what is allowed and what is forbidden.
4. Worked examples drawn from things this lab actually did.
5. Enforcement. What checks the clause, or an honest statement that nothing
   does yet.

Clauses cite `LESSONS.md` by number wherever the rule was learned the hard way.
A clause carrying a lesson number is a rule the lab paid for. A clause without
one is either obvious or new, and if it is new it says so.

## PROPOSAL markers

Some clauses encode a decision the owner has already made. Others are drafts
the lab wrote because the gap needed filling and nobody had ruled on it. Those
are marked inline:

> **PROPOSAL.** Nobody has ruled on this. Written so there is something to
> argue with.

Everything not marked that way traces to a recorded instruction, an existing
standards document, or a lesson. The distinction matters more than any single
clause: the lab must never present its own invention as the owner's policy.

`PROPOSALS_OPEN.md` collects every open marker across all eight in one place,
so the owner can react to the whole set without reading the whole set. From
version 2.0 it also carries the conflicts, which are rulings rather than
proposals, and the escalations the weekly audit turns up. Every item in it is
answerable by label: "P-1.1: A" is a complete decision.

## How they get revised

They are iterated like code, on the owner's instruction.

1. **A charter changes when a decision breaks it, not on a schedule.** The
   incident comes first, the clause second. This is the same discipline
   `LESSONS.md` states in its own header: rules are added after something
   actually went wrong or was actually caught, never from theory.
2. **Bump the version and date in the file.** Charters carry `Version N.M,
   dated YYYY-MM-DD` on the first line, exactly as the demo discretion charter
   does.
3. **A revision that weakens a clause must name the decision that forced it.**
   Widening a gate after a result misses it is the failure mode the demo
   charter already forbids on camera, and it is no more acceptable here.
4. **Contradictions get surfaced, not resolved locally.** If a new clause would
   conflict with a rule the owner has already set, the conflict is reported to
   her rather than settled by whoever noticed it.
5. **Deletions are fine.** A charter that has never bound anything is worse
   than no charter, because it teaches the lab that these documents are
   scenery.

## Related standing documents

- `docs/DEMO_DISCRETION_CHARTER.md`. The promotional surface. Withhold method,
  never misstate result.
- `docs/standards/INNOVATION_STANDARD.md`. How a new method enters the lab.
- `docs/standards/MESH_STANDARD.md`, `docs/standards/MONITOR_STANDARD.md`.
- `docs/UNCERTAINTY-DOCTRINE.md`. The three channels and their recipes.
- `LESSONS.md`. L-1 through L-28 plus the process doctrine P1 through P5.
- `demo-output/website/campaign/NOT_PASSING_REGISTER.md`. Where failures live.
- `scripts/self_audit.py`. The weekly re-verification of published claims
  against the artifacts they cite. It is where several of these clauses stop
  being text: a charter that is checked by something is worth more than a
  charter that is remembered. It reports and never repairs.
