# D4-DEF-1 — the supervisor's acceptance, AND THE LIMIT THE ACCEPTANCE DID NOT STATE

**Written 2026-08-25 by dafoam-supervisor (TENTH session), as the non-delegable
`SUPERVISION_CHARTER.md` §3 check #1: a change to a script that produces, grades or
aggregates a measured number is read BY THE SUPERVISOR, AS A DIFF, before its output is
believed.** The diff read is `d4_grade_D4DEF1_REPAIR.diff` at HEAD `94510794`
(committed `148961aa`). Nothing here is sent, filed, uploaded, posted or commented:
**SUBMISSIONS ARE PARKED and sending is Sanaa's alone** (`CLAUDE.md` rule 7,
`DAFOAM_CHARTER.md` §10).

---

## 1. THE ACCEPTANCE STANDS — and here is what I actually verified, not what I was told

The ninth session's supervisor recorded D4-DEF-1 as **ACCEPTED**. I re-read the diff
myself rather than inheriting that judgement, and **the acceptance is correct on every
point it made.** Specifically, verified line by line:

* **The frozen grader is NOT edited.** `d4_grade.py` stays at the md5
  `f162ef69a7385e5d0586ef5f27657cbb` frozen by `PREREGISTRATION.md` §9a. The repair is a
  SEPARATE file, `d4_grade_SUPPLEMENT.py`, carrying the grading body. `CLAUDE.md` rule 6
  is honoured. The diff is **two hunks only** — a docstring addition and the selftest
  block plus the `main()` wiring — which is itself the proof that the grading body is
  unchanged.
* **The defect named is real.** In the frozen grader `--selftest` is declared at argparse
  and **never read again**; the token appears exactly once in the file. Because
  `--base/--work/--out` were `required=True`, `--selftest` alongside a full invocation
  parsed fine and **silently ran a COMPLETE GRADE, exiting clean.** A reader could have
  recorded "grader selftest passed" when no selftest ever existed.
* **The repair demonstrates rather than asserts.** Each unit builds a fixture violating
  exactly one gate, then runs **this file's own `main()` as a subprocess**
  (`os.path.abspath(__file__)`) and reads the verdict back out of the JSON `main()`
  writes. **The real mapping is exercised — a mirrored copy of the mapping would only
  have tested the mirror.** This is the correct construction and it is rare.
* **The discrimination control is present and is the right one.** `CLEAN-control`
  requires a fully consistent fixture to grade all-PASS. Without it a mutation unit that
  "failed" would not distinguish a working gate from a broken fixture.
* **The meta-control on the cap-stop rule is present.** `capstop_never_pass` asserts
  `g3 != "PASS" and g4 != "PASS"`, encoding `DAFOAM_CHARTER.md` §9 — a cap-stop is
  `GATE REACHED` or `NOT A RESULT`, **never** `PASS` — and it catches a grader mutated to
  map a cap-stop to PASS.
* **A selftest can never be mistaken for a grade.** Distinct exit code 3, used by nothing
  else in the file; **no `--out` file written**; banner `D4_SELFTEST_IS_NOT_A_GRADE`.

**That is a good instrument and I am not retracting a word of the acceptance.**

---

## 2. THE LIMIT — AND IT SITS EXACTLY ON THIS FAMILY'S BRIGHT LINE

**The acceptance was made on an incomplete reading, and I establish the gap
mechanically rather than by impression.** Comparing the gates the grader can EMIT
against the gates the 21 units EXERCISE:

| | gate families |
|---|---|
| **Emitted by the grader** | G1, G2, G3, G4, **G5_endpoint_fd / G5_fd_table**, **G6_planted_zero**, **G6b_negative_control**, **G7_count_controls / G7_count_refusal_control**, G8, G9, G10, G11, G12 |
| **Exercised by the selftest** | G1, G2, G3, G4 (via `capstop_never_pass`), G8, G9, G10, G11, G12 |
| **NEVER EXERCISED** | **G5, G6, G6b, G7** |

**G5 is the endpoint FD table — `DAFOAM_CHARTER.md` §2, the gate that IS this family's
whole line: no DAFoam gradient enters a record without a finite-difference table beside
it at a step proved to lie in the plateau. G6/G6b is the planted-zero control, standing
rule 3. G7 is the count/refusal control.**

`_st_fd()` builds an FD table that grades clean **and is never mutated**. There is no
unit for per-component relative error beyond band D, none for a sign flip, none for a
plateau violation, and **none for an empty component set on the FD side**.

**"21/21 PASS" is true, and it is 21/21 of a unit set that omits the bright line.**

### 2a. Why this is not a pedantic objection — the family has already been burned by
### precisely this, one rung along

`cases/dafoam/ladder-a/A4/curriculum_D3/d3_grade.py`, gate **G3+G4** — the same bright
line — **returned `PASS` at 0.0000 % with zero sign flips over an EMPTY COMPONENT SET.**
The refusal at `:174` tested **key presence and never non-emptiness**, so `comps` stayed
`{}`, the plateau loop ran zero times, `okall` stayed True, and `worst, flips = 0.0, 0`
survived a zero-iteration loop. That grader's other controls were real and fired
correctly — `g1_constraints` counted rows and refused; `g_eta` refused an unseen plant,
citing rule 3 **by name**. **The author knew the rule and applied it twice. G3+G4 was
left unplanted. A PARTIAL PLANT READS ON THE PAGE EXACTLY LIKE A COMPLETE ONE.** That
`PASS` was prevented from being recorded only because an unrelated `KeyError` fired first.

**D4's supplement has the same shape of hole in the same gate: every control is real,
and the one carrying the verdict is untested.**

---

## 3. RULING — operational, mine, recorded not parked

Under Sanaa's desk-item disposal rule (2026-08-25) operational questions are decided by
the team with the reasoning recorded, not referred upward. **This is operational and I
decide it:**

1. **The D4-DEF-1 acceptance STANDS.** The supplement is a strict improvement on a dead
   flag and the defect it names is genuinely repaired.
2. **D4's grade PROCEEDS**, and it may not be presented as "grader selftested" without
   this limitation stated in the same breath.
3. **Before D4's verdict is believed, mutation units are added to the SUPPLEMENT** (never
   to the frozen grader) for: G5 empty component set; G5 component set short of the
   registered set; G5 per-component error beyond band D; G5 sign flip; G5 plateau
   violation; G6 planted zero unseen. `CLEAN-control` must keep passing throughout.
   **This is case work, not meta-work — D4's verdict rests on the bright line.**
4. **If the G5 empty-component-set unit does NOT fire — if the grader returns `PASS` over
   an empty FD component set — that is D4-DEF-2, it is the D3 defect reproduced, and D4
   is `NOT A RESULT` pending repair.** Registered here **in advance of running it**, so
   that the outcome cannot be narrated either way after the fact.

**A unit that does not fire is the finding. The fixture is not tuned until it passes.**

---

## 4. The general lesson, offered to the lab and not asserted as law

**Counting a selftest's units measures the selftest's size, not its coverage.** The
honest instrument is the comparison of gates EMITTED against gates EXERCISED, and it is
mechanical, cheap and repeatable. Twice now in this family the untested gate has been the
one carrying the verdict — which is not coincidence: **the bright-line gate is the hardest
to build a fixture for, so it is the one that gets left out.**
