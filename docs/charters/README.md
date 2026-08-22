# Certonomous charters

A charter is a standing rule the lab holds itself to when nobody is watching. It
is not a mission statement and it is not a summary of good intentions. The test
every charter here has to pass is simple.

> **If no decision could ever violate it, it is not a charter and it does not
> belong in this directory.**

That is the working standard, and it is why these documents carry numbers, named
files, bright lines and worked examples rather than principles. A clause you
cannot point at a decision and say "that broke it" is decoration, and it gets
deleted at the next revision.

---

## 1. The twelve

Twelve files match `docs/charters/*_CHARTER.md` as of 2026-08-21. Re-derive with
`ls docs/charters/*_CHARTER.md | wc -l`; **the command is the authority and this
heading is not.** See the dated note at the foot of this section.

| # | Charter | The one line it turns on |
|---|---|---|
| 1 | [Goals and research proposals](GOALS_AND_PROPOSALS_CHARTER.md) | A proposal that cannot come out more than one way is not a proposal. |
| 2 | [Literature review](LITERATURE_CHARTER.md) | Zero fabricated citations, and the tolerance is zero. |
| 3 | [Case selection](CASE_SELECTION_CHARTER.md) | No new family below HARD without written approval, watched or unwatched. |
| 4 | [Verification](VERIFICATION_CHARTER.md) | A result without a retained evidence record is not a result. |
| 5 | [Result priority](RESULT_PRIORITY_CHARTER.md) | When two methods validate different quantities, the declared ordering picks, and the trade goes on the record. |
| 6 | [Compute budget](COMPUTE_BUDGET_CHARTER.md) | Every budget is measured, and every hold on the box expires by itself. |
| 7 | [Escalation](ESCALATION_CHARTER.md) | The lab decides what is reversible and cheap. Everything else goes to the docket. |
| 8 | [Reporting](REPORTING_CHARTER.md) | Six sections, fixed order, every morning, including the mornings with nothing good in them. From version 2.0 the headings are fixed strings, so a missing section fails a match rather than a taste test. |
| 9 | [Supervision](SUPERVISION_CHARTER.md) | Every big task family has a standing supervisor, and four kinds of check are done by a supervisor personally or they have not been done. |
| 10 | [Filing](FILING_CHARTER.md) | Respect the naming convention, and the check is the binding artifact — a rule nobody can fail is a preference. |
| 11 | [Closure modelling](CLOSURE_MODELLING_CHARTER.md) | A closure is not a result until it has been re-solved, and a score against a baseline a constant can beat is not an evaluation. |
| 12 | [DAFoam](DAFOAM_CHARTER.md) | A DAFoam gradient is not a result until a finite-difference table stands beside it at a step proved to lie in the plateau, and a DAFoam verdict is two rows — shipped and patched — or it is not a verdict about DAFoam. |

`SUPERVISOR_RULINGS.md` sits in this directory and is not a charter, but it binds
like one. `PROPOSALS_OPEN.md` and `CUSTODY_PROPOSAL.md` are proposals and bind
nothing.

**Dated note, 2026-08-20 — this count was already wrong before today.** The
heading read "The nine" and the table listed nine rows, while
`ls docs/charters/*_CHARTER.md | wc -l` returned **ten**:
`FILING_CHARTER.md` was adopted 2026-08-18 and was never added to either. Today's
`CLOSURE_MODELLING_CHARTER.md` makes it eleven, and both missing rows are added
above. **The nine-to-ten step went undisclosed for two days, and that is the
finding worth keeping**: section 5 of this file already warns, about `LESSONS.md`,
that a hand-maintained count of a growing thing "schedules its own next
correction" and gives commands instead of a figure. Section 1 carried exactly
such a count and drifted within two days of the last charter landing. The
re-derive command was correct throughout; only the prose was stale, which is why
the command is now named as the authority.

**Dated note, 2026-08-21 — twelve, and the correction took one day rather than
two.** `DAFOAM_CHARTER.md` was adopted today and row 12 is added above with the
heading. `ls docs/charters/*_CHARTER.md | wc -l` returns **12**, pasted from the
command rather than counted by hand. **The thing worth recording is that this is
the second count correction in two days**, which is the pattern yesterday's note
predicted rather than a repeat of the failure it described: yesterday's drift was
a charter adopted on 2026-08-18 and disclosed on 2026-08-20; today's is same-day,
disclosed by the charter that caused it, in its own `# 14. Changes to other
charters`. That is where an amendment to this file now goes — the new charter
carries it, and this section records it — and it is why the nine-to-ten step is
still the finding and the eleven-to-twelve step is only bookkeeping.

**Dated note, 2026-08-22 — no new charter, one amendment: `CLOSURE_MODELLING_CHARTER.md`
is at v1.1.2.** `ls docs/charters/*_CHARTER.md | wc -l` returns **12**, pasted from the
command; the count is unchanged and row 11's one line is unchanged. §22.4 (*every
prediction ships the model-form band*) now carries the **bands-vs-corrections caveat,
quoted verbatim** from `LESSONS.md` **L-220** and `DOCKET.md` **D446** — the eigenspace
band contains shape or forcing and not both, and a band is never applied as a correction —
on Sanaa's institutionalization directive of 2026-08-22. **Additive; no clause weakened.**
The amendment is recorded three ways inside the charter, which is the convention this file
asks for: the version line, a dated note at the foot of the amended section, and a row in
its own `# 24. Amendment record`. **Bookkeeping worth stating rather than fixing quietly:**
v1.1.1 (2026-08-21, §17) was recorded on the version line and in §17's note but never given
a row in §24 — the v1.1.2 row names that gap instead of back-filling another lane's entry.

**Dated note, 2026-08-22 (second entry, same day) — the caveat's other half:
`VERIFICATION_CHARTER.md` is at v1.10.** `ls docs/charters/*_CHARTER.md | wc -l` still
returns **12**, pasted from the command; no charter was added and row 4's one line is
unchanged. New clause **§2e** — *bands from a perturbation envelope (eigenspace, shelf D):
what such a band may and may not contain* — is **appended at the foot** with `LESSONS.md`
**L-219** and **L-220** quoted verbatim, on the same Sanaa directive of 2026-08-22
(**H-7**), recorded at `docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md`. **The two
notes on this date are two lanes of one directive and not a duplicate:** the closure charter
took the *prediction* side (a band ships with every prediction and is never applied as a
correction), this one takes the *grading* side (a band may not be armed on a row whose class
and measured containment fraction are unstated). **Additive; no existing clause altered, and
no line above the new clause moved** — the only content change above it is line 3's version
and date, verified by `diff` and by comparing `grep -n "^## "` either side of the edit.
**Filed at the foot rather than beside §2d for the reason §6b gives:** other records cite this
file by line and one of those citations sits inside an executable check. The v1.10 amendment
row is at the foot for the same reason, and says so.

**Dated note, 2026-08-22 (third entry, same day) — still twelve charters, and the
amendment is to the org chart rather than to a result: `SUPERVISION_CHARTER.md` is
at v1.4.** `ls docs/charters/*_CHARTER.md | wc -l` returns **12**, pasted from the
command; no charter was added and row 9's one line is unchanged. New clause **§8** —
*team formation is the harness's, and the board is the handoff* — is **appended at
the foot**, recording `harness/teams.yaml` and the generated `.claude/agents/` as
the law of team formation, and the **`docs/LAB_STATE.md` update duty at every commit
and every verdict**. **Additive; no existing clause altered, and no line number above
the new clause moved** — the only content change above it is line 3's version and
date, asserted by diffing `grep -n '^## '` either side of the edit.

**The reason it is a charter matter and not a practice note.** Teams were being
killed at every compaction and re-briefed by hand, and a hand-written brief is
checked against nothing, so the drift was invisible. That is a decision this
directory's own test can point at and say "that broke it": a supervisor briefed from
memory has not been formed under §8.

**Two things in the new clause are the lab's inventions and say so inline, which is
what §3's PROPOSAL discipline asks for even though neither carries the marker.** A
**lane cap of three** — no numeric cap existed in that charter before, and nothing
enforces this one, so it is a preference by this directory's own standard. And a
**five-team roster against §2's four families** — recorded as an operational split
for dispatch, explicitly **not** a redefinition, because §2 states that adding or
merging a family is the owner's. The four families stand as §2 lists them.

**Bookkeeping worth stating rather than fixing quietly:** this is the third
same-day note on 2026-08-22 and the second charter to move today, after
`VERIFICATION_CHARTER.md` v1.10. The two earlier notes are two lanes of one
directive (H-7); this one is unrelated to that directive and is recorded separately
so the date does not imply a common cause.

---

## 2. How to read one

Every charter follows the shape of `docs/DEMO_DISCRETION_CHARTER.md`, which was
written first and set the house style:

1. A version and a date.
2. One bright testable line, stated before any of the reasoning.
3. Numbered sections working that line out, with explicit lists of what is
   required, what is allowed and what is forbidden.
4. Worked examples drawn from things this lab actually did.
5. Enforcement: what checks the clause, or an honest statement that nothing does
   yet.

Clauses cite `LESSONS.md` by number wherever the rule was learned the hard way. A
clause carrying a lesson number is a rule the lab paid for. A clause without one
is either obvious or new, and if it is new it says so.

---

## 3. PROPOSAL markers

Some clauses encode a decision the owner has already made. Others are drafts the
lab wrote because the gap needed filling and nobody had ruled on it. Those are
marked inline:

> **PROPOSAL.** Nobody has ruled on this. Written so there is something to argue
> with.

Everything not marked that way traces to a recorded instruction, an existing
standards document, or a lesson. The distinction matters more than any single
clause: the lab must never present its own invention as the owner's policy.

`PROPOSALS_OPEN.md` collects every open marker across all nine in one place, so
the owner can react to the whole set without reading the whole set. From version
2.0 it also carries the conflicts, which are rulings rather than proposals, and
the escalations the weekly audit turns up. Every item in it is answerable by
label: "P-1.1: A" is a complete decision.

---

## 4. How they get revised

They are iterated like code, on the owner's instruction.

1. **A charter changes when a decision breaks it, not on a schedule.** The
   incident comes first, the clause second. This is the same discipline
   `LESSONS.md` states in its own header: rules are added after something
   actually went wrong or was actually caught, never from theory.
2. **Bump the version and date in the file.** Charters carry
   `Version N.M, dated YYYY-MM-DD` on the first line, exactly as the demo
   discretion charter does.
3. **A revision that weakens a clause must name the decision that forced it.**
   Widening a gate after a result misses it is the failure mode the demo charter
   already forbids on camera, and it is no more acceptable here.
4. **Contradictions get surfaced, not resolved locally.** If a new clause would
   conflict with a rule the owner has already set, the conflict is reported to
   the owner rather than settled by whoever noticed it.
5. **Deletions are fine.** A charter that has never bound anything is worse than
   no charter, because it teaches the lab that these documents are scenery.

---

## 5. Related standing documents

| Document | What it is |
|---|---|
| `docs/DEMO_DISCRETION_CHARTER.md` | The promotional surface. Withhold method, never misstate result. |
| `docs/standards/INNOVATION_STANDARD.md` | How a new method enters the lab. |
| `docs/standards/MESH_STANDARD.md`, `docs/standards/MONITOR_STANDARD.md` | The two technical standards. |
| `docs/UNCERTAINTY-DOCTRINE.md` | The three channels and their recipes. |
| `LESSONS.md` | The numbered lessons plus the process doctrine P1 through P5. |
| `demo-output/website/campaign/NOT_PASSING_REGISTER.md` | Where failures live. |
| `scripts/self_audit.py` | The weekly re-verification of published claims against the artifacts they cite. It reports and never repairs. |

`LESSONS.md` is large and grows daily. Do not read it cold, and do not carry a
count of it in any index. Take the reading instead:

| What | Command | Value at `8cefb4e9` |
|---|---|---|
| Lesson blocks | `command grep -c '^## L-' LESSONS.md` | 85 |
| Distinct lesson numbers | derived from the same list | 84 |
| Highest lesson number | `command grep -oE '^## L-[0-9]+' LESSONS.md \| sort -t- -k2 -n \| tail -1` | L-85 |

**Block count, distinct count and highest number are three different figures,
and at this frame two of them agree by coincidence.** L-43 carries a second
corollary block under the same number, and L-52 does not exist, so 85 blocks span
84 numbers reaching L-85. A count of lessons is therefore not a count of blocks
and neither is the highest number. Say which one you mean.

`docs/MEMORY_ARCHITECTURE.md` section 5 covers how to read the file. Section 8.1
records why this entry gives commands rather than a figure: a hand-maintained
count of a file that grows several times a day schedules its own next correction.
This entry is the index of the corpus; it was never the census of it.
