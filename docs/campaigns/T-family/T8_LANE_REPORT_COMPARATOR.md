# T8 — lane report: the comparator, and the commit that made the freeze true

**Lane:** `lab-lane`, heat-transfer team. **Date:** 2026-08-25.
**Commit:** `96c2fe3c553dfb50498459ae44e1199687f56bd9`
**Subject:** *"T8: the pre-registration and its comparator committed in ONE
commit, so section 11's freeze assertion is TRUE at the moment it binds — and
the Roache selftest caught THREE MIS-SPECIFIED FIXTURES, not a classifier
defect"* (asserted with `git log -1 --format=%s` after the commit).
**Parent:** `94510794`. **Paths in the commit: 4, and only 4** — asserted
against an explicit expected set before `commit-tree`, and re-verified after.

**NO COMPUTE WAS FIRED.** Phase 2 is the supervisor's.

---

## 1. Completeness — `analyse_t8.py` was NOT truncated

The fleet kill landed at the words "Now writing the comparator", and
`analyse_t8.py` was the last file written (19:31). It was the first thing
checked, and it is **complete**:

| artifact | check | result |
|---|---|---|
| `verification/runs/T-family/T8_runs/analyse_t8.py` | `python3 -m py_compile` | clean; 1,727 lines at inspection, complete `main()`, complete `--selftest` |
| `verification/runs/T-family/T8_runs/build_t8.py` | `python3 -m py_compile` | clean |
| `verification/runs/T-family/T8_runs/run_one_t8.sh` | `bash -n` | clean |
| `docs/campaigns/T-family/T8_PREREGISTRATION.md` | read in full | complete, §0–§12 |

**Nothing was restarted and nothing was reconstructed.** The only edit this lane
made to the predecessor's work is the fixture correction in §3 below, which
touches the selftest and not the grading path. The file is 1,793 lines as
committed; the growth is that correction plus the canon cross-check.

## 2. Why all four had to land in one commit

`T8_PREREGISTRATION.md` §11 registers `analyse_t8.py` as **the grading path** and
asserts that file exists. Committing the document alone would have frozen a
**false assertion onto a nonexistent path** — the freeze is the document's entire
evidentiary content (rule 2), so a freeze over a file that is not there is worse
than no freeze. All four landed together, and the assertion is now true:

`analyse_t8.py --check-freeze` → **FROZEN**, rc = 0, all four blobs hashing
against the committed blob (`dd008248f60c`, `376a41da268c`, `d82c98ae2caf`,
`70a37aa634d6`).

## 3. The Roache selftest failed 3 of 49 — and the classifier was innocent

This is the finding of the task, and it is reported at length because the wrong
reading of it would have been expensive in either direction.

`--selftest` on the recovered file reported **FAIL** on three assertions:
"DIVERGENT triple classified", "STAGNANT triple classified", and "NO GCI is
quoted on a DIVERGENT triple". Taken at face value that is a defect in the
**rule-5 instrument** — the one thing that must not be broken.

It was not a defect in the classifier. The fixtures were mis-specified:

* `(1.05, 1.02, 1.00)`: `e21 = 0.02`, `e32 = 0.03`, `ratio = 1.5`, so
  `p = ln 1.5 / ln 2 = +0.5850`. That is **above** the 0.5 stagnation floor, so
  the triple **is CONVERGING, correctly**. A DIVERGENT triple needs the error to
  **grow** under refinement — `0 < ratio < 1`, `p ≤ 0`. This fixture never was
  divergent.
* `(1.06375, 1.03375, 1.0)`: `ratio = 0.8889`, `p = −0.1699` → **DIVERGENT**, not
  STAGNANT. The intended median was `1.03` (`ratio = 1.125`, `p = +0.1699`,
  which is `0 < p < 0.5`).
* The third failure was a **consequence of the first**: that triple really was
  CONVERGING, so it really did carry a GCI, and the assertion was reading a
  **correct refusal as a leak**.

*"The test is wrong, not the code"* is the exact rationalisation that waves a
real bug through, so it was **not accepted on inspection**. Before any edit,
`gci_triple` (line 800) was checked branch-for-branch against the lab canon
`scripts/roache_triple.py:gci_equal` — tracked in HEAD, written independently of
this file — and **matches it**: `EXACT` → `OSCILLATORY` on `ratio < 0` →
`DIVERGENT` on `p ≤ 0` → `STAGNANT` on `p < STAGNANT_FLOOR = 0.5` →
`CONVERGING`, carrying the same corrected Richardson sign `f_fine − e21/den`.

**Only the fixtures were changed. `gci_triple` is byte-untouched.**

So that this never again rests on one lane's reading, the selftest now carries a
**differential sweep against that canon** over 10 triples — *including both
originally mis-specified ones* — at line **1608**, and brackets the floor at
`p = 0.4` (STAGNANT) and `p = 0.6` (CONVERGING). The knife edge `p == 0.5` is
**deliberately not asserted**: constructed in floating point it lands at
`0.49999999999999872`, so an assertion there would test float noise, not the rule.

**`--selftest` now: 52 ok, 0 FAILED, rc = 0.**

## 4. The four standing instruments, with line numbers

All in `verification/runs/T-family/T8_runs/analyse_t8.py` as committed.

| instrument | lives at | refusal wired at |
|---|---:|---:|
| **Planted zero** (rule 3) — `check_planted_zero` | **925** | **1214**, `refuse(...)` → exit 2 |
| **Strict completion + age guard** (rule 4) — `check_completion` | **384** (age-guard clause **484**) | **1154**, `refuse(...)` → exit 2 |
| **Roache gating in the frozen order** (rule 5) — `grade_row` | **1009** (one-way `assert` **1053**) | `VERDICT_NAR` in-band |
| **Verdict vocabulary** | **205–207** | — |

Supporting: `gci_triple` **800**, `band_verdict` **845**, `refuse` **213**,
corrected fixtures **1570**, canon differential **1608**.

**Planted zero** — `PLANT = 1.234e-03` is written into a copy **on disk** and
read back through the **same reader** that produces the graded number, in **six
arms**. Because the registered extrapolation is `(9f₁ − f₂)/8`, planting both
axis-adjacent columns must shift the centreline by **exactly** the plant: the
expected response is **analytic, not approximate**, at all 31 stations, tol
`1e-9`. Two supplementary arms catch failures the registered arm cannot:
planting the **innermost column only** must shift by exactly `9P/8` (a reader
that had silently selected the wrong column pair would agree with the registered
arm and disagree here), and planting the **two outermost** columns must not move
the centreline at all — a zero that is admissible **only because the other arms
have already shown this same reader seeing a non-zero.**

**Strict completion** — the selftest shows the checker **able to fire on every
clause separately** (rc ≠ 0; ranks ≠ 1; no `End` line; `ExecutionTime` count ≠
`endTime`; last time ≠ `endTime`; fields not newer than the case's own `0/T`)
**and able to pass** on a complete synthetic case. A checker never shown able to
pass is as useless as one never shown able to fail; both directions are planted.

**Roache gating** — criterion (1) fires **before** the triple is classified, and
the one-way property is enforced by a structural `assert` at 1053, not by
discipline. The selftest confirms an in-band CONVERGING row is PASS, that the
**same** in-band row becomes NOT A RESULT when one level is not converged, and
that over every combination tried the verdict is either the band verdict or NOT
A RESULT — never the reverse direction.

**Vocabulary** — `PASS` / `GATE FAIL` / `NOT A RESULT` only; a synonym sweep over
the file returns nothing.

## 5. Grader self-blindness

`scripts/check_grader_self_blindness.py` on `analyse_t8.py`: **clean on both
probes**, before and after this lane's edit. The script itself states this is
**not a proof of correctness**, and it is not reported as one. **Nothing needed
fixing** — T8 is not a fourth instance of the three found lab-wide today.

## 6. Sanaa's 2026-08-25 grid ruling — satisfied as written

The registered family (§5) is **three levels**: `c`/`m`/`f` at **6,400 / 25,600 /
102,400** cells, `r = 2` exactly in both directions, no grading anywhere, GCI at
`Fs = 1.25`. **Nothing in this rung asks for a fourth level as a gate
requirement.** No flag to raise, and nothing was changed.

## 7. Cost

**Predicted 335.3 core-minutes** — `c` 7.13, `m` 42.81, `f` 285.40 — over
**3 cases** (one per level), from a lab rate of `1.196e5 cell·steps/(core·s)`.
At $0.0513/core-h that is **$0.287, derived, not measured** — the box cannot read
its own billing. **Cap 15/80/500, 595 core-min total ($0.509 derived).**

The pre-registration **names its own misprediction risk before the run** (§8,
R6): the rate is borrowed from `K2bU3_L025`, a **transient PIMPLE** case, while
T8 is a **steady SIMPLE** run, and per-step cost is not interchangeable between
solver modes. **The arithmetic is exact; the rate is the exposure.** The
direction of the error is deliberately not predicted, so the completion
calibration row can attribute the gap to misprediction rather than absorb it.

**Ranks.** The cap is enforced as `timeout = cap_core_min × 60 ÷ ranks` with
`RANKS=1` asserted **explicitly** in `run_one_t8.sh` (line 26, timeout derived at
line 34) **and** re-asserted in the comparator's selftest. A wall-clock timeout
is **not** a core-minute cap; the two coincide only at 1 rank, and the
pre-registration says so in those words. Timeouts: 900 / 4,800 / 30,000 s.

**Note, not a change:** the frozen §8 text frames an overrun as *"an overrun
stops that level; it does not get a new budget"* and labels a capped level
`PENDING`, a right-censored measurement, never `GATE FAIL`. Under the
supervisor's runaway-guard reading the stop still happens and the decision is
the supervisor's. **The frozen text was left alone**, per rule 2.

## 8. Filing

`scripts/check_filing.py` reports **26 violations, ZERO of them T8** (12
R8-PAPER-NAME, 9 R9-SIDECAR-MISSING, 4 R5-ASSET-SUBDIR, 1 R1-ROOT-CLEAN — all
pre-existing, in other territories). Run artifacts are under
`verification/runs/T-family/T8_runs/`, prose under `docs/campaigns/T-family/`;
no run output sits beside the prose describing it.

## 9. What this lane could NOT verify — named as VERIFY

* **VERIFY — the comparator has never seen a real case.** Every instrument above
  is exercised against **synthetic** cases built by the selftest. The planted
  zero, the completion checker and the mesh/`SCALE` assertions have **not** been
  run against an OpenFOAM case produced by `build_t8.py`. No compute was fired,
  so this is expected, but it means **`build_t8.py` is compile-verified only** —
  its output has never been meshed or solved.
* **VERIFY — the `SCALE` discrepancy is registered but unexercised on a mesh.**
  The selftest records that §12 S3's printed `SCALE = 72.0928` is a rounding
  error of `1.85e-5` relative against the exact `2π/sin(5°) = 72.09146648` —
  **larger than the document's own `1e-6` assertion tolerance.** The comparator
  uses the exact value and asserts it against the mesh's own total volume
  (refusing above `1e-6`), so the printed constant cannot enter a number. **But
  that assertion has never run against a real mesh**, and if the wedge angle as
  built differs from 5°, this is where it will surface. The supervisor should
  expect this refusal to be the first thing that can fire on the first case.
* **VERIFY — the plateau conjunct has no registered criterion.** §7 says "and
  plateaued"; T8 registers no separate threshold for it, and the comparator
  **declares this rather than inventing one** (`PLATEAU_MAX_EXPONENT_DRIFT is
  None`, asserted in the selftest, and the grading output says so). This is
  honest but it means criterion (1)'s plateau half is **not currently
  enforceable**. It is a gap in the frozen document, not in the code, and this
  lane did not alter a frozen criterion to close it.
* **VERIFY — the borrowed cost rate is cross-mode and untested.** Named in §8 by
  the pre-registration itself; restated here so it is not lost.
* **VERIFY — I did not read `build_t8.py` line by line as a diff.** The
  supervisor's §3 check is personal and undelegable, and this lane did not
  perform it or claim it.

---

**Nothing in this rung has been sent, filed, submitted, uploaded, registered or
posted anywhere outside this box, and nothing in it may be (`CLAUDE.md` rule 7).**
