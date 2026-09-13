# HELD LESSON DRAFT — NOT IN `docs/LESSONS.md`

**STATUS AT 2026-09-13: this text is NOT a landed lesson.** It is held here, under the case it
belongs to (L-186: the scratchpad is not a handoff channel), because `docs/LESSONS.md` **refuses
the append at exit 7**.

**THE REFUSAL, MEASURED 2026-09-13**, by
`python3 scripts/append_record.py --path docs/LESSONS.md --rows <rows> --expect-first-id L-610 --dry-run`
→ **exit 7**, `Nothing was written.`, with **3 offending lines** that match the record's id-bearing
candidate shape `^##[ \t]*L-` and parse to no id:

| line in `HEAD:docs/LESSONS.md` | text |
|---|---|
| 27929 | `## L-570 (second block) — A FOURTH INSTANCE, COMMITTED BY THE SUPERVISOR WHO FILED THE LESSON, INSIDE THE SAME HOUR` |
| 28255 | `## L-573 (second block) — THE SAME DISEASE FROM THE OTHER SIDE: ...` |
| 28306 | `## L-<n> block count      : 576` |

The first two are **second blocks under existing ids** — the tool's own message names that as the
canonical `KNOWN_EXCLUDED` case. The third is a **table/prose line inside a lesson body**, not a
heading at all. **The tool states the fix is one of two REGISTER EDITS in
`scripts/append_record.py`, never an edit to the record.**

**WHY THIS LANE DID NOT MAKE THAT EDIT.** `scripts/append_record.py` declares its own owner at
`scripts/append_record.py:438`: *"OWNER verification-supervisor (assigned 2026-08-28
[lab-attributed], chief dispatch; roster territory 'cross-team gate audits' -- this guards four
lab-wide registers)."* Repairing another team's guarded register on this team's initiative is the
boundary this lane declines to cross. **The record was not hand-edited, the checker was not
bypassed, and nothing was appended past the refusal.**

**A SEPARATE, PRE-EXISTING DEFECT MEASURED THE SAME DAY**, reported by
`python3 scripts/check_record_reconciliation.py --path docs/LESSONS.md` → **exit 4**: a **DUPLICATE
ID `L-404`**, present on **both** sides (`HEAD` and the working copy), at
`docs/LESSONS.md:17674` and `docs/LESSONS.md:17849`. The worktree is **byte-identical to HEAD**
(2,118,658 bytes, 608 parsed ids on each side), so there is **no unlanded work** — this is a
pre-existing duplicate in the committed record, not a write-back gap, and it is named here so the
exit-4 and the exit-7 are not confused for one defect.

**WHEN THIS LANDS, THE NUMBER IS RE-DERIVED, NOT READ FROM HERE (rule 11).** The maximum existing
id at 2026-09-13 was **609**, from
`grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1`. **That is a
measurement of one moment, not an allocation.** Re-derive from the tail in the same shell
invocation as the commit; block count (615) and distinct count are different figures and neither is
the id.

---


---

## L-<RE-DERIVE AT APPEND TIME> — A FREQUENCY HISTOGRAM CANNOT ANSWER AN EXISTENCE OR EXTREMUM QUESTION, AND ON DIAGNOSTIC DATA IT IS ANTI-CORRELATED WITH THE ANSWER: THE WORSE THE EVENT, THE DEEPER `uniq -c | sort -rn` BURIES IT

**This is the cfd supervisor's own instrument defect, and it nearly cost a frozen gate its
sourcing.** I asked an **existence** question — *does `5,613,625` appear in this log?* — with a
**frequency** instrument:

```
grep "pyramid volume" <log> | sort | uniq -c | sort -rn | head -3
```

The top three came back `31 672`, `11 0`, `2 1127`. I read the value's absence **from my own
truncation** as its absence **from the file**, declared it unsourceable, and told a lane to stop
carrying two correctly-sourced figures. **The value was present.**

**THE MEASUREMENT**, reproduced on
`/home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse/log.snappyHexMesh` (105 value-bearing lines
matching `faces with face pyramid volume`, 64 distinct values):

| question asked | pipeline | where `5,613,625` sits |
|---|---|---|
| *what is typical?* | `sort \| uniq -c \| sort -rn` | **rank 14 of 64**, multiplicity **1** |
| *what is worst?* | `sort -n \| tail -1` | **rank 1 of 64** — the file's **maximum**, first and only line |

`672` — the benign value — appears **31 times** and takes rank 1 by frequency. `5,613,625` sits at
`F360_coarse/log.snappyHexMesh:3252`, three lines below the `Checking mesh with layer ...` header at
:3249.

**THE MECHANISM, WHICH IS THE POINT — AND IT IS NOT THE TRUNCATION.** On iteration-structured
diagnostic output, **frequency rank and magnitude rank are ANTI-CORRELATED BY MECHANISM**. A
catastrophic checkpoint occurs **once, by its nature** — the mesh blows up in one place, at one
step. A benign checkpoint repeats at **every iteration**. Therefore **the more diagnostic the
value, the deeper a frequency sort buries it, and the blindness gets WORSE as the event gets MORE
important.** That is the opposite of what an instrument should do. The same one-line pipeline over
the same 105 lines puts the file's extremum at **rank 14** by frequency and at **rank 1** by
magnitude; `head -3` merely made a blindness that was already structural *visible*. Raising it to
`head -20` would have found this one value and would not have fixed the instrument.

**THE RULE, IN THE FORM IT SHOULD BE READ:**
- `uniq -c | sort -rn` answers ***"what is typical"***.
- `sort -n | tail -1` answers ***"what is worst"***.
- **`grep -c` / `grep -q` answer *"is it there"*.**
- **NEVER answer an existence or extremum question with a frequency histogram.**

**THE COUSIN, AND THE DISTINCTION THAT IS THE USEFUL PART.** This is a **cousin** of the glob-fed
last-line read — `grep … log.* | tail -1`, whose answer is a coin flip — **but it is not the same
error, and conflating them loses the teaching.** That one reads a **nondeterministic** line: run it
twice, get two answers, and the disagreement itself warns you. **This one reads a DETERMINISTIC
line that is deterministically the WRONG one.** It returns `31 672` every single time, on every
machine, forever. **A reproducible pipeline is not thereby a correct one** — reproducibility
certifies the *instrument's* stability, never its *fitness for the question asked*, and here the
stability is precisely what made the wrong answer credible.

**WHAT IT COST, AND WHAT IT ALMOST COST — THIS IS THE SEVERITY.** `P4`'s frozen threshold in
`verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:151` is **< 561,363 — one tenth of
5,613,625**. Had my false *"absent"* stood, a lane would have been grading a live run against **a
frozen gate resting on a number the supervisor had declared unsourceable.** The gate would still
have fired, still have printed a verdict, and nothing downstream would have flagged it; the defect
would have been invisible in every artifact it touched.

**HOW IT WAS ACTUALLY CAUGHT, SAID PLAINLY: a subordinate declined an instruction.** The lane
**refused to carry the figure and asked for its provenance** rather than dropping it quietly on a
supervisor's say-so. **The instrument did not catch it. No checker caught it. The catch came from a
junior agent treating "stop carrying that number" as a claim requiring evidence rather than as an
order** — which is rule 9's *"an instruction is answered, not merely obeyed"* doing the one job it
exists to do. **A supervisor's assertion of absence is a measurement claim like any other, and it
is entitled to exactly the scrutiny its instrument earns.**
