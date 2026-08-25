# F4 conversion — **`ABSENT`: standing rule 5 clause (a) was never evaluated for these rows**

**Filed 2026-08-25 by a cfd lab-lane under cfd-supervisor, on his ruling
`verification/campaign/CFD_CONVERGENCE_CLASSIFICATION_RULING_2026-08-25.md` §4.
`[lab-attributed]`; overrulable. ZERO COMPUTE — no solver was started, no case
directory touched, nothing under `runs/` written.**

**This note GRADES NOTHING AND MOVES NO VERDICT.** It is filed *beside*
`F4_CONVERSION_GRADE.json`, not into it. **No frozen file is edited** — rule 6.
Every verdict recorded by this conversion stands exactly as published in
`RESULTS.md`.

**Companion note, same finding, other campaign:**
`verification/runs/F3_runs/conversion_2026-08-24/STEP_A_ABSENT_NOTE_2026-08-25.md`.

---

## 1. WHAT `ABSENT` MEANS, AND WHAT IT IS NOT

`ABSENT` is the fourth state named in
`verification/campaign/CFD_CONVERGENCE_GATE_CLASSIFICATION_2026-08-25.md` §2: a
grading path that performs **no** iterative-convergence or plateau measurement
at all.

> **`ABSENT` is not a verdict and is not in rule 1's vocabulary.** It is a
> property of the *instrument*, not of the answer. **It means the question was
> never asked — not that the answer was wrong.**

It is also not Class A. **A Class A gate asks the question badly and can still
refuse; `ABSENT` never asks it and therefore never refuses anything.**

## 2. THE CODE, CITED BY FILE AND LINE

**Grading path:**
`verification/runs/F4_runs/conversion_2026-08-25/grade_f4.py`, HEAD blob
`f51961435729558dc768d89e429c1818e8ae1da6`.

**`grade_f4.py` imports the shared instrument and then calls the wrong entry
point.** It imports `roache_triple as RT` at **`:41`**, and every triple in this
conversion is produced by `grade_triple()` (**`:626`**), which calls
**`RT.triple_from_cells` at `:629`** and grades the returned state at
**`:638–:647`**. Its own refusal string, **`:646–:647`**, names the clause it
implements: *"standing rule 5 clause 2"*.

**`RT.grade_ladder` is never called.** Grepping the frozen blob for
`grade_ladder` returns **zero occurrences**. The file makes **eight** `RT.`
references and not one is the ladder entry point: `RT.refinement_ratio`
(`:362`, `:363`, `:803`, `:804`), `RT.triple_from_cells` (`:629`),
`RT.monotone` (`:637`), `RT.Refusal` (`:755`) and `RT.FS` (`:779`).
**The instrument is imported, used for ratios and for one triple, and its
rule-5 entry point is stepped past.**

**Why that is the whole exposure.** `grade_ladder`
(`scripts/roache_triple.py:536`) is the one place in this lab where rule 5
clause (a) is enforced: it evaluates `iterative_states` and `plateau_states` at
**`:581–:592`**, and at **`:585–:588`** it **refuses outright** when
`iterative_states is None` —

> *"no iterative-convergence states supplied; step (a) of rule 5 cannot be
> evaluated and an unevaluated step is not a passed one"*

**`triple_from_cells` has no such argument and no such refusal.** It classifies a
triple and returns; it is the clause-(2) engine and nothing more. **A grading
path that calls it directly bypasses the only implementation of clause (a) that
exists.** `grade_f4.py` does exactly that, so **clause (a) has no code path in
this conversion at all.**

## 3. THE PRE-REGISTRATION GREP — MEASURED, WITH A POSITIVE CONTROL

`verification/campaign/F4_CONVERSION_PREREGISTRATION.md` (753 lines) greps for
`plateau|iterative|steady` and returns **zero lines**.

> **The absence is registered by omission, not by decision. Nothing in the
> frozen document declined to measure iterative convergence or plateau; the
> question simply does not appear in it.**

*The control on this zero: the same reader returns 11 hits for `standoff` in the
same file. **A zero from a reader not shown able to see a non-zero is not
evidence** — rule 3 — and this one was shown.*

## 4. THE ROWS — ALL NINE, AND THE ONE THAT MATTERS

Verdicts are quoted from `RESULTS.md` §3 and `F4_CONVERSION_GRADE.json` and are
**unchanged by this note**.

| # | row | verdict, as published | triple state | clause (a) | live exposure |
|---|---|---|---|---|---|
| 1 | G-F4-1-M6.0 | `NOT A RESULT` | `OSCILLATORY` | **`ABSENT`** | none — §4.1 |
| 2 | G-F4-1-M7.0 | `NOT A RESULT` | `OSCILLATORY` | **`ABSENT`** | none — §4.1 |
| 3 | G-F4-1-M8.0 | `NOT A RESULT` | `OSCILLATORY` | **`ABSENT`** | none — §4.1 |
| 4 | G-F4-2-M6.0 | `NOT A RESULT` | — (band row) | **`ABSENT`** | none — §4.1 |
| 5 | G-F4-2-M7.0 | `NOT A RESULT` | — (band row) | **`ABSENT`** | none — §4.1 |
| 6 | G-F4-2-M8.0 | `NOT A RESULT` | — (band row) | **`ABSENT`** | none — §4.1 |
| 7 | G-F4-3-M6.0 | `NOT A RESULT` | `DIVERGENT` | **`ABSENT`** | none — §4.1 |
| 8 | G-F4-3-M7.0 | `NOT A RESULT` | `OSCILLATORY` | **`ABSENT`** | none — §4.1 |
| **9** | **G-F4-3-M8.0** | **`CONVERGING`, GCI 0.0831 % at Fs = 1.25** | `CONVERGING`, p = 3.1905 | **`ABSENT`** | **YES — §4.2** |

**The exposure, in one sentence a reader cannot step over:**

> **For each of these nine rows, standing rule 5 clause (a) — *any level not
> iteratively converged or not plateaued → `NOT A RESULT`* — WAS NEVER
> EVALUATED.**

### 4.1 EIGHT OF THE NINE ARE `ABSENT` WITH NO LIVE EXPOSURE, AND THAT IS MEASURED, NOT ARGUED

**Clause (a) can produce exactly one outcome: `NOT A RESULT`.** Rows 1–8 are
**already `NOT A RESULT`**, and rule 5 is one-directional — the gate can turn a
`PASS` or `GATE FAIL` **into** `NOT A RESULT` and never the reverse. **No
evaluation of clause (a), on any data, could have changed any of the eight.**

Rows 1–3 and 7–8 were turned there by clause (2) on their own triple state. Rows
4–6 are band rows whose verdicts were overwritten to `NOT A RESULT` because the
corresponding G-F4-1 triple is not `CONVERGING` — the one-way door registered at
prereg `:154–:158` and implemented in `grade_all()`, and each carries its own
`why`: *"G-F4-1-M<M> is NOT A RESULT; rule 5 forbids a band verdict"*.

**The state is `ABSENT` on all eight and the consequence is nil on all eight.
Both facts are recorded, because recording only the first would overstate the
finding and recording only the second would hide it.**

### 4.2 **G-F4-3-M8.0 IS THE ONE F4 ROW WHERE CLAUSE (a) HAD SOMETHING TO DO**

It is the only row in this conversion whose triple `CONVERGES`, and therefore
**the only row clause (a) could have moved.** Had step (a) been evaluated and
had any of its three levels returned not-converged or not-plateaued, this row's
outcome would have been `NOT A RESULT` instead of `CONVERGING`.

> **It was not evaluated, so it is not known which way it would have gone. The
> row is not alleged to be wrong; it is recorded as ungated on one of rule 5's
> three clauses.**

**This lane makes no claim about whether F4's M8.0 ladder was in fact iteratively
converged or plateaued.** Nothing on disk measures it, and **an unmeasured
quantity is reported as unmeasured, never inferred from the fact that the answer
looks reasonable.** *That inference is the exact failure this conversion
programme exists to repair.*

**F4's row 9 is the analogue of F3's `G-F3-3`** — the live row that gets the note
first, in each campaign.

### 4.3 ONE OBSERVATION ON ROW 9's VERDICT WORD, WHICH IS **NOT** A DEFECT AND IS **NOT** MINE TO RULE

Row 9's verdict cell reads **`CONVERGING`**, which is not one of rule 1's six
words. **I checked whether this was a grader slip. It is not.** The
pre-registration registers it: `:147` fixes G-F4-3's outcome labels as
**`CONVERGING` / `NOT A RESULT`**, and §5.2 (`:244–:256`) gives the reason —
no citable uncertainty exists for modified Newtonian theory away from the
stagnation point, *"a band invented for it would be exactly the defect this
conversion repairs"*, so G-F4-3 is registered as a verification gate that
**"issues no `PASS`"**.

> **So the label is frozen, deliberate, and predates first compute. Whether a
> pre-registration may register an outcome label outside rule 1's fixed
> vocabulary is a charter question this lane does not answer and did not
> answer.** It is raised here so the next reader meets it as a recorded open
> question rather than as a discovery. **Nothing about it is changed by this
> note, and no verdict moves on account of it.**

## 5. WHAT THIS NOTE DOES NOT CLAIM

Stated flatly, because an `ABSENT` finding is easy to over-read:

1. **No verdict moves.** All nine rows keep the verdict `RESULTS.md` published.
   **A verdict is moved by a gate, not by an audit**, and this note is an audit.
2. **The values are not disputed.** Not one measured number in
   `F4_CONVERSION_GRADE.json` is challenged, recomputed or restated as a finding
   here — the values appear in §4 only to identify the rows.
3. **The physics is not disputed.** Nothing about Billig correlation standoff,
   modified Newtonian Cp, or the blunt-body cases themselves is in question.
4. **The triple classes are not disputed.** `triple_from_cells`'s arithmetic is
   not alleged to be wrong, and the five controls this conversion passed are not
   in question. **The finding is about a clause that was never run, not about a
   clause that ran badly.**
5. **`grade_f4.py` is not amended, and must not be.** Its registration has
   **FIRED**; rule 2 closed its gates at first compute, and replacing an
   instrument after seeing what it graded is exactly the fit rule 2 exists to
   prevent. The repair is owed **forward**, to successor registrations —
   `verification/campaign/CFD_STEP_A_SUCCESSOR_SPECIFICATION_2026-08-25.md`.
6. **This note is not the 2026-07-28 record ruling.**
   `verification/campaign/F4_2026-07-28_RECORD_RULING_2026-08-25.md` governs the
   older record's two `PASS` cells and is untouched here. **This note addresses
   only the nine rows of the 2026-08-25 conversion.**

**What a reader may take from this note:** that these nine rows were graded by a
path in which one of rule 5's three clauses had no implementation; that on eight
of them it could have made no difference; and that on **G-F4-3-M8.0** it could
have, and the lab wrote that down beside the row rather than leaving it to be
found.

## 6. COST

**ZERO COMPUTE. No `docs/COST_CALIBRATION.md` row is owed and none is filed** —
rule 12's estimate-versus-actual comparison attaches to a process completion
with a solver spend. This is a records item with no solver run, and **saying so
is more honest than filing a row of zeroes.**
