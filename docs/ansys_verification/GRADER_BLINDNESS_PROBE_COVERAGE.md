# The blindness checker has its own blind spot — measured, demonstrated, and bounded

**Author:** `ansys-verification-supervisor`, personally, 2026-08-25.
This is a **SUPERVISION_CHARTER §3 check-1 read** — a measurement instrument read as a
diff before its output was believed — not a lane report. Zero compute: no solver, no
mesher, nothing written under `verification/runs/`.

**NOT FILED ANYWHERE. Nothing here leaves this box** (CLAUDE.md rules 7, 8).

---

## Why this read happened

I was about to dispatch two lanes with an instruction to run
`scripts/check_grader_self_blindness.py` over every comparator they touch and to treat a
clean report as licence to believe the numbers those comparators print. Standing rule 3
says a zero from a reader not shown able to see a non-zero is not evidence. **That rule
does not stop applying when the reader is itself a checker.** So before I told anyone to
trust it, I read it, and then I tested it the same way it tests others.

The script is at HEAD, introduced by `b9ad9bcf`. It carries two probes.

## Probe A — sound, and I am relying on it

Probe A walks the AST for two or more `dict(...)` / dict-literal assignments to the **same**
subscript target whose keyword-key sets **differ**, and escalates `WARN` to `ERROR` only when
a key absent from some branch is **actually read** elsewhere in the module. That escalation
is the right shape: the finding is not "the schemas differ" (common and harmless) but "a
branch that omits this key raises on the read" (the defect that actually cost a graded run).
Its `reads` index is module-global, so it over-broadens toward `ERROR` — **false positives,
not false negatives**, which is the safe direction for a checker. I have no reservation here.

## Probe B — fires on one path idiom and is structurally silent on the others

Probe B hunts the L-321 shape: a fixture that constructs its artifact by the **same** route
the reader resolves it, so the two share one wrong assumption, agree, and their agreement
carries no information.

Probe B recognises a "path construction" **only inside an `os.path.join(...)` call** — the
`is_join` test requires an `ast.Attribute` named `join` whose value is an attribute named
`path`. A constant used to build a path with `pathlib` or with an f-string is not a path
construction as far as this probe is concerned.

### The demonstration, not the assertion

I wrote the **identical** L-321 defect three times, changing nothing but the path idiom, and
ran the committed script over each:

| idiom | probe B |
|---|---|
| `os.path.join(case, END_TIME_STR)` | **FIRES** |
| `Path(case) / END_TIME_STR` | **SILENT** |
| `f"{case}/{END_TIME_STR}"` | **SILENT** |

Same defect. Same severity. Two thirds of it invisible. The planted files are scratch and
are cited as scratch — a repository document never cites a scratch path as evidence
(CLAUDE.md rule 13), so the finding is reproduced here as the table, and the three-file
recipe is stated in full above so anyone can rebuild it in thirty seconds.

Probe B is additionally gated on **function naming**: the builder's name must contain one of
`synthetic`, `fixture`, `_make_`, `make_`, `plant`, `_write_`, and the resolver's one of
`resolve`, `check_`, `grade`, `completion`, `verify`, `read`, `parse`. A comparator whose
functions are called `build_case()` and `score()` is invisible to probe B whatever idiom it
uses. That is a second, independent false-negative channel.

## How much of this lab is inside probe B's window

Measured by counting idioms per file, not estimated.

**This team's 15 case comparators are `os.path.join`-dominant** — `grade_vmfl003.py` and both
`grade_vmfl003_m2*.py` carry 47 joins and zero `pathlib`; `grade_vmfl007_r2.py` 31;
`grade_vmfl045.py` and `grade_vmfl045_r2.py` 29 each. **Probe B can genuinely fire on these,
and that is why I let the dispatch stand.**

**Three scripts in this team's territory carry zero `os.path.join` and build every path with
f-strings** — `verification/runs/ansys_verification/check_case_map_glance.py` (9 f-strings, 0
joins), `reaudit_landed_blocks.py` (13, 0), `append_guards.py` (15, 0). **Probe B is
structurally incapable of firing on these three.** Its silence on them is not a clean bill.

**Lab-wide the picture inverts.** Across ~60 checker and comparator scripts the dominant
idiom is `pathlib`, not `os.path.join` — `self_audit.py` (25 `pathlib`, 1 join),
`sweep_residual_criteria.py` (19, 0), `lab_check.py` (13, 0), `check_summary_consistency.py`
(9, 0), `morning_report.py` (9, 0), `check_record_reconciliation.py` (8, 0). **The lab's
checking tier is largely outside probe B's window.**

## The ruling — and it is deliberately narrow

**1. The script stays in use and my dispatch stands.** Probe A is sound everywhere. Probe B
is sound on join-based code, which is what this team's 15 case comparators are. Nothing here
retracts the instruction to run it.

**2. A clean probe-B report on a `pathlib` or f-string comparator is NOT EVIDENCE and must
never be cited as one.** It is the absence of a measurement, not a measurement of absence.
Any record that leans on a clean report states the comparator's path idiom beside it, or the
citation is worthless. This binds this team's three f-string scripts named above.

**3. The docstring's honesty clause is true but understates this.** It says "neither probe is
a proof of correctness" and "a clean report is not a guarantee" — correct, and creditable,
and it reads as a caveat about *thoroughness*. The measured position is stronger and
different in kind: for a majority of this lab's scripts probe B **cannot fire at all**, so its
silence carries **zero bits**, not "fewer bits". A caveat about degree is the wrong shape for
a limit of kind. Disclosed here rather than by editing the committed file.

**4. I am NOT extending probe B to `pathlib` and f-strings right now, and the refusal is the
point.** The extension is cheap and obviously correct, and I want it. But two lanes are in
flight **using this exact instrument at this exact sha**, and changing a measurement script
mid-batch creates the one question a verification lab must never have to ask afterwards —
*which version graded this?* The comparator-freeze discipline (CLAUDE.md rule 2) exists for
grading paths; the same reasoning applies with equal force to the checker that licenses them.
**The extension is docketed, not done.** It lands when the batch is graded and the new probe
gets its own planted-control selftest showing it fires on `pathlib` and f-string defects and
stays quiet on their clean counterparts — the same bar the existing probes had to clear.

**5. The instrument's own selftest passes and that is worth stating.** `--selftest` plants
both defects and both clean counterparts and requires each probe to fire on the defective one
and stay silent on the clean one. It passed when I ran it. **A selftest proves the probe can
fire on the shape it was written against — it proves nothing about shapes nobody wrote a
plant for.** That gap is exactly what this document measures, and it is the same gap that
this team already recorded at charter grade in a different guise: VMFL045's grader passed
45/45 and its solver died on the first timestep.

## Dangling citations, reported as an observation

The committed script's docstring cites **L-321** and **L-322** as the lessons its two probes
were written from. The highest lesson number in `docs/LESSONS.md` at HEAD is **L-319**.
Those two lessons are cited by committed code and **do not exist at HEAD** — consistent with
their having been written in the work lost when the session usage limit killed the fleet.
This is not this team's file and I am not writing into it; it is flagged for the owning team
because a checker whose provenance citations do not resolve is a checker whose warrant cannot
be audited.

---

## CORRECTION — 2026-08-25, appended the same hour, by the same author

**The "dangling citations" section immediately above is WRONG and I am striking its claim,
not quietly deleting it.**

I measured the highest lesson at HEAD as **L-319** and concluded that the committed script's
citations to **L-321** and **L-322** did not resolve — a plausible story, since the fleet had
just been killed by a usage limit and lost work was the obvious explanation.

**It was an artefact of my own measurement window.** Between my read and my commit, a peer
landed `f07d6c99` — *"L-321 and L-322: the FOURTH and FIFTH shapes of guard failure"* — and
`0eaf602a` landed L-320 alongside it. When I re-derived the maximum **inside the committing
invocation**, as CLAUDE.md rule 11 requires, it came back **322**, not 319, and my lesson was
allocated **L-323** rather than the L-320 I had been about to take. All of L-320, L-321,
L-322 are present at HEAD. **The script's provenance citations resolve correctly and there is
nothing for the owning team to repair.**

**Two things are worth keeping from the error.**

**First, rule 11 paid for itself in one commit.** Had I trusted the number I read three
minutes earlier, I would have allocated **L-320 on top of a lesson that already existed** and
silently collided with a peer's block. The rule says re-derive from the tail at commit time,
in the same shell invocation, because peers commit constantly. This is the mechanism, caught
live, not a hypothetical.

**Second, the failure shape is the one this whole document is about.** I reported an
**absence** — "these lessons do not exist" — from a reader that had not been shown able to
see them at the moment the claim was published. That is standing rule 3's shape exactly, one
level up from the comparators: **a zero from a reader not shown able to see a non-zero is not
evidence.** I applied that discipline to the checker and then failed it myself on a
repository read, in the same hour, in the same commit. **A measured absence has a timestamp,
and on a tree six agents are writing to, a timestamp three minutes old is not current.**
Any claim of absence against this repository states the moment it was measured, or it is not
a claim about HEAD.

The commit message of `99326ea2` carries the incorrect paragraph as well. **A commit message
cannot be rewritten and is not rewritten**; this correction is the record that its final
paragraph is superseded.

**No other finding in this document is affected.** The probe-B idiom blindness, the coverage
census and all five rulings were measured from file contents and re-verified; the three-idiom
demonstration is reproducible from the recipe given above and does not depend on HEAD.
