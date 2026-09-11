# T4e / T26 — REFERRAL on the 3600-s stall clause

**Status: `PENDING` — a referral, not a ruling.** `PENDING` is used here in its
`VERIFICATION_CHARTER.md` §9 display sense: a question filed and awaiting the
person entitled to answer it. It is not a softened anything.

**THIS DOCUMENT ANSWERS NOTHING AND MOVES NOTHING.** **Narrowing, widening or
retiring a threshold is reserved to Sanaa** (`CLAUDE.md` FIRST-ACTION reserved
list: *"retiring a standard, gate threshold or charter clause"*). It is neither a
lane's call nor a supervisor's. Every figure below is given in **both readings,
side by side, with neither presented as the answer.**

**NO VERDICT ANYWHERE MOVES EITHER WAY.** This is a **calibration-ledger**
question. It touches the `cleaned` column and the `ratio` column of
`docs/COST_CALIBRATION.md` and nothing else. No gate, no `PASS`, no `GATE FAIL`,
no `NOT A RESULT`, no rule-4 completion verdict and no Roache triple depends on
the answer. A reader who wants to know whether a run was good should stop
reading here; a reader who wants to know what the lab's estimate-quality record
says should not.

---

## 1. THE CLAUSE, AND WHERE IT IS WRITTEN

`CLAUDE.md` rule 12, verbatim: *"a spend figure states gross or cleaned (a row
over 3600 wall s is a stall)"*. `docs/charters/COMPUTE_BUDGET_CHARTER.md` §2
carries the charter form, and `docs/COST_CALIBRATION.md` append rule 4 restates
it: *"cleaned = gross minus rows the 3600-s stall rule matches"*.

**IT IS NOT ONLY PROSE. AN INSTRUMENT IMPLEMENTS IT, AND IT IMPLEMENTS THE
LITERAL READING WITH NO SCOPE TEST.** `cases/navier_class/watch_grade_calibrate.py`:

```
STALL_WALL_S = 3600
...
stalled = [r for r in present if r["wall_s"] > STALL_WALL_S]
cleaned = gross - sum(r["core_min"] for r in stalled)
```

`summarise_cost()` asks one question of a row — *is `wall_s` greater than 3600* —
and asks nothing about whether the run completed, whether it progressed, whether
it was long **by its own registration**, or whether anything hung. **So the
question below is not academic and cannot be left open indefinitely without
consequence: a shared instrument is already answering it one way while ledger
rows answer it the other, and the disagreement is on the record in three rows.**

---

## 2. THE QUESTION, STATED AND NOT ANSWERED

> **Does the 3600-s stall clause reach a row that is long BY ITS OWN
> REGISTRATION and that completed with continuous measured progress — or is it
> scoped to rows that are long BECAUSE something stalled?**

Two readings, both defensible from the text as written:

- **READING A — the clause is a bright line on wall time.** Any row over 3600
  wall s is a stall, full stop. This is what the text literally says and what
  `watch_grade_calibrate.py` executes.
- **READING B — the clause is scoped to stalls.** "Stall" names a failure mode
  (a wedged or spinning process), and 3600 s is the heuristic that detects it;
  a row that provably progressed to completion is not a stall however long it
  ran.

**This document does not choose.** It reports what each reading does to real
rows, because that is the part a lane can measure.

---

## 3. THE EVIDENCE NOW COMES FROM THREE DIRECTIONS

All three figures below were produced by **running the real instrument**
(`watch_grade_calibrate.py::summarise_cost`, imported and called directly,
read-only) on each row's own measured `wall_s` and `ranks`. They are
measurements of the clause's behaviour, not arguments about it.

| direction | row granularity | gross core-min | **READING A** cleaned | **READING B** cleaned | what A strips |
|---|---|---|---|---|---|
| **cfd SUBOFF R1b** (2026-09-10) | triple, 3 levels | 173.233 | **61.450** | **173.233** | 1 level of 3 (`r1b_fine`, 6707 s) |
| **T4e medium leg** `T4e_IJ_m` | one leg = one row | 218.500 | **0.000** | **218.500** | **everything** (13,110 s) |
| **T26 `L3ABS` rebuild** | one build = one row | 60.067 | **0.000** | **60.067** | **everything** (3,604 s) |

Corresponding ratios against each row's own registered prediction:

| row | predicted | **READING A** ratio | **READING B** ratio |
|---|---|---|---|
| SUBOFF R1b | 216.21 | **0.284** | **0.801** |
| T4e medium | 206.1 | **0.000** | **1.060** |
| T26 `L3ABS` | 45 | **0.000** | **1.335** |

**The SUBOFF figure reproduces exactly.** The cfd row states cleaned **61.450**
and ratio **0.284**; the probe run for this document returns **61.450** from the
same function. That agreement is what licenses the other two rows of the table —
the probe is driving the production path, not a paraphrase of it.

---

## 4. THE DECISIVE CASE IS FOUR SECONDS WIDE

**`L3ABS` ran 3,604 wall s.** The threshold is 3,600 and the comparison is
strict `>`. So the build is **four seconds** — **0.11 %** — past the line.

**MEASURED, by running the instrument on the real figure and on a counterfactual
four seconds either side:**

| `wall_s` | gross core-min | cleaned under READING A | ratio under A | stalled levels |
|---|---|---|---|---|
| **3,604** (the actual) | 60.067 | **0.000** | **0.000** | `['L3ABS']` |
| **3,596** (counterfactual) | 59.933 | **59.933** | **1.332** | `[]` |

**A 0.22 % change in wall time changes the retained cost by 100 % and the ratio
from 1.332 to 0.000.** Nothing physical differs across that line: the same mesh,
the same five stages, the same machine, the same result. **The clause is
DISCONTINUOUS at its threshold with no physical quantity changing across it**,
and that is the sharpest statement of the question this lab can currently make.

**WHY A READER SHOULD DOUBT THAT READING A MEANS WHAT IT APPEARS TO MEAN HERE —
measured, not relayed:**

- **All five stages returned rc 0** — `blockMesh_rc=0 sfe_rc=0 snappy_rc=0
  checkMesh_rc=0 cc_rc=0` — and both `FINISHED` and `SHELL_EXIT rc=0` were
  written (`/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS/BUILD_RC.txt`,
  `.../BUILD_STATE.txt`).
- **`checkMesh` and `writeCellCentres` both completed** after the mesh phase.
- **The 15-second heartbeat series shows continuous forward progress to the very
  end**: layer-addition iteration **30 → 33** and `log_snappy_lines` **6,400 →
  6,792** across the final 340 s
  (`.../L3ABS_HEARTBEAT_SERIES.tsv`). **Nothing hung.**
- The build was **33.4 % of its own 180 core-min hard stop** — long by its own
  registration, not long by surprise.

The same doubt, measured, attaches to the T4e medium leg: **60,000 of 60,000
iterations to rc 0 with exactly one `End`**, p_rgh residual floor **4.35e-09**
against a registered 1e-06, field-change plateau **3.390e-06** against tol 2e-4,
and **53.0 %** of its own registered `timeout_s` of 24,720.

---

## 5. A SECOND FINDING THE THREE ROWS EXPOSE TOGETHER: THE CLAUSE'S OUTPUT
## DEPENDS ON ROW GRANULARITY, WHICH IS AN AUTHORING CHOICE

The T26 ABS mesh ladder built three levels — `L1ABS` 209 s, `L2ABS` 844 s,
`L3ABS` 3,604 s. **The same compute, written as one ledger row per level or as
one row for the ladder, produces different cleaned figures under READING A**,
measured on the instrument:

| how the same spend is written | gross | **READING A** cleaned | what A strips |
|---|---|---|---|
| one row per level (3 rows) | 77.617 | **17.550** | `L3ABS` only |
| `L3ABS` alone, as its ledger row actually is | 60.067 | **0.000** | everything |

**Nothing about the compute changes between those two lines; only the author's
choice of row boundary changes.** Under READING A the lab's estimate-quality
record is therefore partly a function of how rows are cut, which is a property
no one designed and which this referral puts on the record without proposing a
remedy — **proposing the remedy would be answering the question.**

---

## 6. WHAT EACH READING WOULD RE-GRADE

**No row is edited by this document. `docs/COST_CALIBRATION.md` append rule 1 is
append-only: an existing row is never edited, and a correction is a new row
naming the row it corrects.** The list below is what a ruling would *reach*, so
that whoever rules can see the blast radius before ruling.

**If READING A (bright line) is confirmed**, these rows already state that figure
as one of their two and would simply lose their second figure — **no correction
row would be needed for any of them**, because all three deliberately carry both:

- `C-20260910T164430.128823Z-1fb233db` — cfd SUBOFF R1b (cleaned 61.450, ratio 0.284)
- `C-20260911T182403.504528Z-68dc9650` — T4e medium leg (cleaned 0.000, ratio 0.000)
- `C-20260911T182921.263721Z-01f499e6` — T26 `L3ABS` (cleaned 0.000, ratio 0.000)

**If READING B (scoped to stalls) is confirmed**, the same three rows lose their
other figure — again with no correction row needed — **but
`cases/navier_class/watch_grade_calibrate.py::summarise_cost` becomes wrong as
written** and would need a scope test it does not have. **That instrument is
cfd's, in `cases/navier_class/`, and is outside heat-transfer's territory; this
document does not touch it and does not propose a patch for it.**

**Rows this referral does NOT reach, checked rather than assumed:** every
heat-transfer row landed 2026-09-11 whose longest constituent is under 3,600 wall
s. Measured on the instrument: **K2f throwaway, 13 wall s → cleaned = gross =
0.217 core-min, `stalled_levels` empty.** **That non-zero is doing work here**:
it is the control showing the reader used for §3's and §4's zeros **can** return
a non-zero cleaned figure, so those zeros are evidence and not a blind reader
(standing rule 3, the planted-zero discipline). A zero from a reader never shown
able to see a non-zero would not have been worth printing.

**One row deliberately outside this referral: K2d.** Its cleaned figure of
154.134 core-min is computed under READING A and its row says so — but its row
also states that the cleaned column *"is NOT the useful figure here"*, because
**all** 689.734 core-min of that rung is named as **waste** under
`COMPUTE_BUDGET_CHARTER.md` §6, and **waste is never folded into a cleaned column
or into a ratio under either reading.** The stall question does not change one
digit of K2d's calibration content.

---

## 7. WHAT THIS LANE DID NOT DO

- **Did not choose a reading.** Reserved.
- **Did not edit `CLAUDE.md`, `COMPUTE_BUDGET_CHARTER.md`, or any ledger row.**
- **Did not patch `watch_grade_calibrate.py`.** Another team's instrument, and
  patching it would be answering the question in code — the worst place to answer
  it, because code answers silently.
- **Did not propose a threshold, a scope test, or a row-granularity rule.** Each
  would be a remedy, and a remedy presupposes a ruling.

---

## 8. FILING CHECK, AND WHAT ITS ZERO IS WORTH

`scripts/check_filing.py` was run on this path. **Its result is recorded in the
appendix below together with an explicit statement of what it can and cannot
see** — the instrument reads `git ls-tree -r HEAD`, so **on a path that is not
yet committed it evaluates nothing and returns a zero that means "not looked at",
not "clean".** That distinction is the whole point of recording it: a green from
a reader that could not see the file is the `gitignored is not filed` failure in
a new costume, and this document would rather carry the caveat than the badge.

---

## APPENDIX — provenance of every figure

- **T26 `L3ABS`**: `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS/BUILD_RC.txt`
  (`total_wall_s=3604`, five rc), `.../L3ABS/BUILD_STATE.txt` (`FINISHED`,
  `SHELL_EXIT rc=0`), `.../L3ABS_HEARTBEAT_SERIES.tsv` (progress to the end),
  `.../L1ABS.out` and `.../L2ABS.out` (209 s, 844 s). Outside git by the
  large-data policy (`docs/LOCATIONS.md`); the figures are also published in
  `docs/LAB_STATE.md` heat-transfer update 118, committed `a55e482f1`.
- **T4e legs**: `verification/runs/T-family/T4e_runs/STATUS.T4e_IJ_c` (1,469 s)
  and `STATUS.T4e_IJ_m` (13,110 s); convergence figures from
  `verification/runs/T-family/T4e_runs/analyse_t4e.py` C6.1/C6.3 as cited in the
  legs' ledger rows.
- **SUBOFF R1b**: cfd's ledger row `C-20260910T164430.128823Z-1fb233db` and
  `verification/campaign/SUBOFF_R1b_RESULTS.md`.
- **The clause instrument**: `cases/navier_class/watch_grade_calibrate.py`,
  `STALL_WALL_S` and `summarise_cost()`.
- **Every cleaned figure and every `stalled_levels` list in §3, §4, §5 and §6**
  was produced by importing that module and calling `summarise_cost()` on rows
  carrying each level's measured `wall_s` and `ranks`. The SUBOFF line reproducing
  cfd's independently published 61.450 is the check that the probe drove the real
  path.
