# F3 conversion — **`ABSENT`: standing rule 5 clause (a) was never evaluated for these rows**

**Filed 2026-08-25 by a cfd lab-lane under cfd-supervisor, on his ruling
`verification/campaign/CFD_CONVERGENCE_CLASSIFICATION_RULING_2026-08-25.md` §4.
`[lab-attributed]`; overrulable. ZERO COMPUTE — no solver was started, no case
directory touched, nothing under `runs/` written.**

**This note GRADES NOTHING AND MOVES NO VERDICT.** It is filed *beside*
`F3_CONVERSION_GRADED.json`, not into it. **No frozen file is edited** — rule 6.
Every verdict recorded by this conversion stands exactly as published in
`RESULTS.md`.

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

**Grading path:** `verification/runs/F3_runs/conversion_2026-08-24/grade_f3.py`,
HEAD blob `6fea2e1d64cc3c377dd0e05ee4c08f6e83e1d049` — the frozen file that ran
(`F3_CONVERSION_GRADED.json` `grading_path_freeze.frozen_match: true`).

**`grade_f3.py` reimplements the Roache triple in-file and hands it no states.**
The function is `roache()` at **`grade_f3.py:357`**; its class assignment runs
**`:371–:388`** (`EXACT` `:372`, `STAGNANT` `:375`/`:380`, `OSCILLATORY` `:383`,
`DIVERGENT` `:385`, `CONVERGING` `:387`), and its single call site is
**`:523`**. *The supervisor's brief cites `:377–395`; that span lies inside this
same function, and the wider `:357–:388` is given here because it is the whole
of the reimplementation.*

**The shared instrument is never reached.** Grepping the frozen blob for
`grade_ladder|triple_from_cells|roache_triple|iterative|plateau|steady` returns
**two lines only** — `:357`, the local function's own name, and `:523`, its call.
**`scripts/roache_triple.py` is not imported and `grade_ladder` is never
called.**

**Why that is the whole exposure.** `grade_ladder`
(`scripts/roache_triple.py:536`) is the one place in this lab where rule 5
clause (a) is enforced: it evaluates `iterative_states` and `plateau_states` at
**`:581–:592`**, and at **`:585–:588`** it **refuses outright** when
`iterative_states is None` —

> *"no iterative-convergence states supplied; step (a) of rule 5 cannot be
> evaluated and an unevaluated step is not a passed one"*

**A grader that reimplements the triple bypasses that refusal.** `grade_f3.py`
is the demonstration: it computes only the triple's *class*, which is clause
(2). **Clause (a) has no code path in this conversion at all.**

## 3. THE PRE-REGISTRATION GREP — MEASURED, WITH A POSITIVE CONTROL

`verification/campaign/F3_CONVERSION_PREREGISTRATION.md` (890 lines) greps for
`plateau|iterative|steady` and returns **exactly one line, `:270`.**

**That line is NOT a clause (a) clause, and saying so precisely is the point of
this section.** `:269–:274` is a declared departure from the **rule 4 completion
rule**: it observes that rule 4's literal `ExecutionTime` count == `endTime`
clause is *"a **steady-iteration** clause"* unmeetable by an adaptive-timestep
transient solver, and substitutes one `ExecutionTime` line per `Time` line.
**It is a statement about log integrity. It is not a statement that the answer
stopped moving.**

> **So the F3 pre-registration contains no iterative-convergence clause and no
> plateau clause. The one hit is a false positive and is reported as one.**

*The control on this reading: the same reader returns 31 hits for `gate` in the
same file. A grep that finds nothing is only evidence when it has been shown
able to find something.*

## 4. THE ROWS

**Five graded rows rest on the state-less triple.** Verdicts are quoted from
`RESULTS.md` and `F3_CONVERSION_GRADED.json` and are **unchanged by this note**.

| row | verdict, as published | triple class | clause (a) | live exposure |
|---|---|---|---|---|
| **G-F3-3 cone surface pressure** | **`PASS`** | `CONVERGING` | **`ABSENT`** | **YES** |
| **G-F3-2 wedge shock angle / M2.0_th15** | **`PASS`** | `CONVERGING` | **`ABSENT`** | **YES** |
| **G-F3-5 diamond wave drag / M2.0_eps7p125** | **`PASS`** | `CONVERGING` | **`ABSENT`** | **YES** |
| **G-F3-4 cone shock angle** | **`GATE FAIL`** | `CONVERGING` | **`ABSENT`** | **YES** |
| G-F3-1 wedge surface pressure / M2.0_th15 | `NOT A RESULT` | `OSCILLATORY` | **`ABSENT`** | **none — see §4.2** |

**The exposure, in one sentence a reader cannot step over:**

> **For each of these five rows, standing rule 5 clause (a) — *any level not
> iteratively converged or not plateaued → `NOT A RESULT`* — WAS NEVER
> EVALUATED.**

### 4.1 THE SUPERVISOR'S BRIEF NAMED TWO OF THESE FIVE ROWS. THE DISK CARRIES FIVE.

The ruling and the census both scope F3's exposure to *"G-F3-3 (`PASS`),
G-F3-4 (`GATE FAIL`), 3 ungraded"*. **Read from
`F3_CONVERSION_GRADED.json`, that undercounts the graded triple-bearing rows by
three, and it undercounts the LIVE `PASS` rows by two.** `G-F3-2 / M2.0_th15`
and `G-F3-5 / M2.0_eps7p125` are **graded, published, live `PASS` verdicts on
`CONVERGING` triples** — the identical exposure to G-F3-3, and neither was
named. The three rows the census called ungraded are the three **`PENDING`**
rows, which are a different set entirely (§4.3).

**This note therefore covers five rows, not two.** *The correction is in the
direction of more exposure, not less, and is recorded here rather than relayed
so that a later reader does not find it and conclude the census was quietly
wrong about F3.*

### 4.2 WHY G-F3-1 / M2.0_th15 IS `ABSENT` WITH NO LIVE EXPOSURE

Clause (a) can produce exactly one outcome: `NOT A RESULT`. **That row is
already `NOT A RESULT`**, turned there by clause (2) on an `OSCILLATORY` triple.
Rule 5 is one-directional — the gate can turn a `PASS` or `GATE FAIL` **into**
`NOT A RESULT` and never the reverse — **so no evaluation of clause (a) could
have changed it.** The state is `ABSENT`; the consequence is nil. **Both facts
are recorded, because recording only the first would overstate the finding and
recording only the second would hide it.**

### 4.3 TWO ROW CLASSES THIS NOTE DOES NOT COVER, AND WHY

- **The two band-only `PASS` rows** — `G-F3-1 / M3.0_th15` and
  `G-F3-2 / M3.0_th15`, both `triple: null`, single level. `BAND_ONLY_RULING_2026-08-25.md`
  already governs their citability. **Whether clause (a) — whose text speaks of
  *levels* in a triple — reaches a one-level band row is a scope question the
  supervisor's ruling does not decide, and this lane does not decide it either.**
  It is raised, not answered.
- **The three `PENDING` rows** — `G-F3-1 / M2.5_th10`, `G-F3-2 / M2.5_th10`,
  `G-F3-5 / M2.5_eps5`. `PENDING` is a queue state, not a graded verdict; their
  runs were never launched (`PENDING_ROWS_DISPOSITION.md`: the frozen hard cap
  fired as registered). **Nothing was graded, so nothing is owed a note.**

## 5. WHAT THIS NOTE DOES NOT CLAIM

Stated flatly, because an `ABSENT` finding is easy to over-read:

1. **No verdict moves.** All five rows keep the verdict `RESULTS.md` published.
   **A verdict is moved by a gate, not by an audit**, and this note is an audit.
2. **The values are not disputed.** Not one measured number in
   `F3_CONVERSION_GRADED.json` is challenged, recomputed or restated here.
3. **The physics is not disputed.** Nothing about oblique-shock or Taylor–Maccoll
   theory, the exact references, or the cases themselves is in question.
4. **The triple classes are not disputed.** `roache()`'s arithmetic is not
   alleged to be wrong. **The finding is about a clause that was never run, not
   about a clause that ran badly.**
5. **`grade_f3.py` is not amended, and must not be.** Its registration has
   **FIRED**; rule 2 closed its gates at first compute, and replacing an
   instrument after seeing what it graded is exactly the fit rule 2 exists to
   prevent. The repair is owed **forward**, to successor registrations —
   `verification/campaign/CFD_STEP_A_SUCCESSOR_SPECIFICATION_2026-08-25.md`.

**What a reader may take from this note:** that these five rows were graded by a
path in which one of rule 5's three clauses had no implementation, and that the
lab knew and wrote it down beside them.

## 6. COST

**ZERO COMPUTE. No `docs/COST_CALIBRATION.md` row is owed and none is filed** —
rule 12's estimate-versus-actual comparison attaches to a process completion
with a solver spend. This is a records item with no solver run, and **saying so
is more honest than filing a row of zeroes.**

---

## ADDENDUM 2026-08-26 — quote-and-strike: G-F3-2 / M2.0_th15 is no longer `PASS`

Stamped `2026-08-26T17:31:34Z`. Appended at the foot; **lines whose number changed above this section: 0**; no gate, band, threshold, cap or label of this document is altered. Where this document cites **G-F3-2 / M2.0_th15** as `PASS` — line 90 (the `G-F3-2 wedge shock angle / M2.0_th15` | `PASS` | `CONVERGING` | `ABSENT` | YES row) and line 106 ("graded, published, live PASS") — that citation reads, quoted and struck: ~~`G-F3-2 / M2.0_th15 — PASS, CONVERGING, p = 0.034, GCI 169.06 %`~~ → **`NOT A RESULT` — triple `DEGENERATE`, |p| = 0.034 < P_MIN = 0.05** (`scripts/roache_triple.py`, c525c247). Re-graded under Sanaa's own authorisation ("OK for this", boarded at `e94a19ad`); the re-grade, both triples' values and the verbatim instrument output are in `verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md`, ADDENDUM 2026-08-26 (re-grade). The lines cited above are not rewritten in place.
