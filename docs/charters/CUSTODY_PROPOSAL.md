# Who may write each charter — evidence, and the questions that need Katie

**PROPOSAL, not policy.** Chief supervisor, 2026-08-11, at commit `d433d27c`.

`docs/MEMORY_ARCHITECTURE.md` §9 has carried defect 5 since 2026-08-10: **write-custody is
unstated for most of the charter corpus.** That audit deliberately declined to fix it —
*"This document does not invent it"* — and it was right to. Custody is a governance
question. Inventing it in a document nobody ruled on would make the lab's own invention
indistinguishable from the owner's policy, which is the one thing the charter corpus
forbids itself.

**So this file does two things and stops.** It records what each charter's own text
supports, and it names the questions only Katie can answer. Nothing here is in force.

---

## 0. A frame note, because the obvious number is wrong

The memorable version of this defect is *"9 of 12 charters do not state custody"*. **Do not
quote that figure without its frame**, and I nearly published a different wrong one.

A keyword sweep for custody phrases (`written by`, `maintained by`, `custody`, `who writes`,
`amended by`) returns a clean, confident answer — and it is **wrong in at least two
directions**:

- **False negative.** `SUPERVISOR_RULINGS.md` states its custody plainly and matches no
  keyword, because it states it as a **quoted delegation**: *"Katie delegated these while
  filming: 'I'll let you decide. You are the global supervisor.'"* That is stronger evidence
  of custody than any phrase in the list, and the sweep scores it as silent.
- **Frame-dependence.** `SUPERVISION_CHARTER.md` states custody in its **body** (§2.1, §4)
  and not its header. A header sweep and a whole-file sweep therefore give different
  answers, and neither is wrong — they are **different measurements**, and comparing them is
  the mistake (L-75).

The count is therefore not the deliverable. The per-charter reading below is.

---

## 1. What each charter's own text supports

| Charter | What the text establishes | Custody |
|---|---|---|
| `SUPERVISOR_RULINGS.md` | *"Katie delegated these while filming… You are the global supervisor"*, plus an explicit exclusion: *"Anything outward-facing is NOT ruled on here."* | **STATED.** Chief, under a quoted delegation, bounded away from anything outward-facing. The model for the rest. |
| `RESULT_PRIORITY_CHARTER.md` | *"This is a draft for the owner to react to, not a settled charter… It becomes 1.0 when she rules."* | **STATED, and it is hers.** The version number is doing the work — 0.4 rather than 1.0 *because* she has not ruled. |
| `SUPERVISION_CHARTER.md` | Body, not header: §2.1 family leads write family guidelines in the family's own records; §4 the daily list and research board are written by the chief. | **STATED IN BODY.** A reader who checks headers concludes it is silent. |
| `PROPOSALS_OPEN.md` | *"Every point in the nine charters where the lab is **proposing** rather than **recording**, collected so the owner can react."* | **IMPLIED AND SOUND.** The lab writes; the owner disposes. Its own framing carries the rule. |
| `CASE_SELECTION_CHARTER.md` | §1: *"The list is the owner's and it is closed."* Scope of the six HARD criteria is hers. | **PARTIAL.** The criteria are hers; who may amend the rest is unstated. |
| `README.md` | Index. States the test a charter must pass. | **N/A** — but see §3, it has an indexing duty. |
| `COMPUTE_BUDGET_CHARTER.md` | Scope and version history only. | **UNSTATED.** |
| `ESCALATION_CHARTER.md` | Scope and version history only — though it is the charter *about* what goes to the owner. | **UNSTATED**, and the irony is worth naming. |
| `GOALS_AND_PROPOSALS_CHARTER.md` | Scope and version history only. | **UNSTATED.** |
| `LITERATURE_CHARTER.md` | Scope and version history only. | **UNSTATED.** |
| `REPORTING_CHARTER.md` | *"Freezes the morning report… its shape is fixed and its sections do not get reordered, merged or skipped."* | **UNSTATED**, but the freeze implies the shape is not the lab's to change. |
| `VERIFICATION_CHARTER.md` | Scope and version history only. **Three sections were added to it today** by the chief. | **UNSTATED**, and it is the most-amended charter in the corpus. |

## 2. What the practice actually is, stated so it can be contradicted

Every charter carries a dated version history naming what changed and why, and **in practice
the chief amends on incident and records the reason**. That is not nothing — it is a real,
auditable convention, and the corpus is measurably good at it. What it lacks is a statement
that this is *allowed*, and a statement of where it stops.

**The gap is not who has been writing. It is what nobody may write without her.**
`SUPERVISOR_RULINGS.md` is the only file in the corpus that draws that line explicitly, and
it draws it exactly where the lab's other rules draw it: **outward-facing acts stay hers.**

## 3. The questions for Katie — these are the deliverable

1. **Is the chief's amend-on-incident practice authorised for the charters generally?** It
   is what has been happening, including three amendments today. If yes, one sentence in
   `README.md` covers all twelve. If no, most of the corpus needs re-examining.
2. **Which charters, if any, are hers alone to amend?** `RESULT_PRIORITY_CHARTER.md` already
   says it is. `CASE_SELECTION_CHARTER.md` §1's criteria read that way. **Is that list closed
   at those two?**
3. **Does the `SUPERVISOR_RULINGS.md` boundary generalise** — the chief may rule on anything
   not outward-facing, and outward-facing means sending, filing upstream, or contacting a
   steward? If so it is the corpus's custody rule already written, and it needs only to be
   cited from `README.md` rather than restated.
4. **Version bumps.** Two amendments landed today without one before it was noticed, and
   `RESULT_PRIORITY_CHARTER.md` carries three different version numbers in one file
   (`MEMORY_ARCHITECTURE.md` D-10). **Should a charter amendment require a header bump?**
   This is the cheapest of the four to enforce and the easiest to forget.

## 4. What I did not do, and why

**I did not write custody into the nine charters that lack it.** Recording a practice as a
rule is how the lab's own invention becomes indistinguishable from the owner's policy, and
`PROPOSALS_OPEN.md` exists precisely to keep those apart. The 2026-08-10 audit made the same
call and I am not overturning it on my own authority.

**I did not publish a count.** See §0 — the two obvious sweeps disagree, and both are honest
measurements of different things.

**I did not treat this as urgent.** Nothing is blocked on it. It is a governance gap that has
been open since the corpus existed, and one bad ruling made quickly would be worse than the
gap.

## Related

- `docs/MEMORY_ARCHITECTURE.md` §2.2 (custody stated for three of twelve), §9 defect 5.
- `docs/charters/SUPERVISOR_RULINGS.md` — the boundary this proposal suggests generalising.
- `docs/charters/PROPOSALS_OPEN.md` — where lab proposals live so they cannot be mistaken
  for her policy.
