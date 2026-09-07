# F27-WOMERSLEY NUMERICS SUCCESSOR — R2 RESULTS (Roache triple, graded)

> **RECORD ONLY.** This document records a verdict the cfd supervisor took and
> independently verified. It does not re-grade and it decides nothing. The gates,
> thresholds and bands are those frozen in
> `verification/campaign/F27_NUMERICS_SUCCESSOR_R2_PREREGISTRATION.md`
> (freeze commit `6aabb3c1`); this record cites that frozen document, it does not
> rewrite it (rule 6).
>
> **Dated 2026-09-07.**

---

## 0. WHAT THIS RESOLVES

The F27 numerics successor previously HALTED lawfully on its frozen 500 core-min
cap before the fine level (`F27_NUMERICS_SUCCESSOR_RESULTS.md`, BLOCKED). The R2
re-registration corrected only the compute cap (500 → 625 core-min) on a fresh
pre-compute run, byte-identical gates/thresholds/bands. The R2 run then completed
all three levels and graded. **This RESOLVES the F27 §2ay state-(b) gap to a
runnable, graded result:** F27 now runs and grades; the GATE FAIL below is an
honest verification finding, **not** a capability gap.

- **Run root:** `verification/runs/F27_NUMERICS_SUCCESSOR_R2_runs`
- **Frozen pre-registration:** `verification/campaign/F27_NUMERICS_SUCCESSOR_R2_PREREGISTRATION.md`, freeze `6aabb3c1`
- **Grader:** `cases/F27_WOMERSLEY_PIPE/successor_numerics/grade_f27_successor_r2.py`,
  git blob `706f4a4df5143b7fda6b821c321acba5564ea1fd` at grade time (rule-2 hash
  confirmed == `HEAD:<path>` at grade time)
- **Graded artifact (cited by every number below):**
  `verification/runs/F27_NUMERICS_SUCCESSOR_R2_runs/F27_GRADED.json`, `prereg_commit 6aabb3c1`
- **Grading invocation used for the recorded grade:** the grader was run with an
  **explicit `--root=F27_NUMERICS_SUCCESSOR_R2_runs`** override, because the frozen
  grader's `--root` default pointed at the PARENT root (defect + §2d.1 repair, §4 below).

---

## 1. THE TWO GATE VERDICTS (Roache triple, rule 5)

Coarse/medium/fine = 3,840 / 30,720 / 245,760 cells, refined by exactly 2 in all
three directions (r = 2). `Fs = 1.25`, `BAND_FACTOR = 5.0`, reference 0.0. Both
triples strictly complete (§2), both planted controls green (§2).

### G-F27R-1 — `E2_velocity_locked_phase` = **PASS**

- triple state: **CONVERGING** (monotone)
- level values: coarse `7.649837768717366e-03` / medium `2.0620229128663656e-03` / fine `7.285879634110018e-04`
- observed order: `2.0671367740336732`
- GCI: `71.70268515804656 %` ( = `0.000522417` absolute at Fs = 1.25)
- band: `[6.052738753361828e-05, 0.001513184688340457]`
- **fine value `7.285879634110018e-04` is INSIDE the band → PASS.**

### G-F27R-2 — `Einf_axial_velocity_locked_phase` = **GATE FAIL**

- triple state: **CONVERGING** (monotone)
- level values: coarse `1.1936366142236239e-02` / medium `6.420554980443741e-03` / fine `4.136254537709814e-03`
- observed order: `1.2718206521583209`
- GCI: `48.7981776152905 %` ( = `0.00201842` absolute at Fs = 1.25)
- band: `[0.00011397841172247245, 0.002849460293061811]`
- **fine value `4.136254537709814e-03` is ABOVE the band upper bound → GATE FAIL.**

### Overall

Both gated triples are **CONVERGING** (monotone), so this is a **REAL graded
result — NOT `NOT A RESULT`** (rule 5). The numerics-change successor **PASSes on
E2 (RMS error)** and **GATE FAILs on Einf (max error, out of band)**. The
reported-not-gated channels (`R-F27-W` bulk mean, `R-F27-E` perp cross-flow,
`R-F27-A_z`, `R-F27-A_theta`) are recorded in the graded artifact and enter no gate.

---

## 2. STRICT COMPLETION AND PLANTED CONTROLS

- **Strict completion (rule 4):** all three levels strictly complete — rc = 0, an
  `End` line, last time == `endTime`, fields present, and each field at `endTime`
  newer than the level's own `0/`. Confirmed by the cfd supervisor at the verdict.
- **Planted-zero controls (rule 3):** all planted controls PASSED — 16 controls
  green in the grader, including the readers-see-a-zero-and-a-planted-defect control
  (both gated quantities shown able to take a passing and a failing value through the
  real reader; each of four planted defects seen by its own channel and no other).

---

## 3. COST

- **Actual: 417.667 core-min** (coarse 0.667 + medium 13.867 + fine 403.133),
  ClockTime × 4 ranks ÷ 60, from `F27_GRADED.json::cost_claim`.
- **Cap: 625 core-min** (frozen R2 cap). Spend is well under cap; no cap breach.
- **Prior projection: ~542 core-min** → ratio actual/projected = **0.771**
  (favourable over-projection).
- **Dollars DERIVED, NOT MEASURED:** at $0.0513/core-h the box cannot read its own
  billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Calibration OWED but BLOCKED:** a `docs/COST_CALIBRATION.md` row is owed
  (rule 12 estimate-vs-actual). Filing is **BLOCKED lab-wide** (append_record poison
  row, routed to verification); `append_record` was **not** run. The row is owed and
  will be filed when the block clears — **owed is not cancelled.**

---

## 4. GRADING-PATH DEFECT AND §2d.1 REPAIR (value-invariant; NOT YET FROZEN)

The frozen R2 grader's `--root` argument **defaulted to the PARENT root**
(`verification/runs/F27_NUMERICS_SUCCESSOR_runs`) at line 1126, and
`run_f27_successor_r2.sh` invokes the grader **without `--root`** (its line 376:
`python3 $GRADER --prereg-commit=...`). So the **frozen grading path, run as
written, would grade the WRONG (parent) root.** The correct R2 grade recorded above
required an **explicit `--root=F27_NUMERICS_SUCCESSOR_R2_runs` override**.

- **Defect artifact:** a stray, untracked
  `verification/runs/F27_NUMERICS_SUCCESSOR_runs/F27_GRADED.json`
  (mtime 2026-09-07T20:44:43Z) — a **PENDING** grade (both gates PENDING) produced
  by the default-root invocation over the parent root, whose fine level HALTED on
  the parent cap and is incomplete. **It is inspected, not reverted (rule 10). It is
  NOT the R2 grade** and must not be mistaken for it; the R2 grade is the R2-root
  `F27_GRADED.json` cited in §0.
- **§2d.1 repair (measurement-script change, one line):** the R2 grader's `--root`
  default is changed from the parent root to its own R2 root
  (`F27_NUMERICS_SUCCESSOR_R2_runs`), so the frozen path grades the R2 root **by
  default**. **Value-invariant:** re-running the repaired grader with the fixed
  default (no `--root` arg) produces a verdict **byte-identical** to the recorded
  grade (same PASS / GATE FAIL, same fine values). This alters **no** gate,
  threshold, band, cap, label or verdict.
- **Status:** the repair diff is a measurement-script change and is held for the cfd
  supervisor's check-1 before it is believed and frozen. Because the grader blob
  changes, the frozen pre-registration receives a dated §2d.1 addendum re-pinning
  the repaired grader by its new blob. **Neither is frozen in this record.**

---

## 5. VERDICT VOCABULARY

Verdicts stated: **PASS** (G-F27R-1), **GATE FAIL** (G-F27R-2). Calibration filing:
**BLOCKED**. No softer word is used and none is implied.
</content>
</invoke>
