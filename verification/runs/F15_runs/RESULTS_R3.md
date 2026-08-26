# F15-OSR29-R3 — oblique shock reflection, M∞ = 2.9 — GRADED BY THE R3 COMPARATOR: G-F15-2 `PASS`, G-F15-1 `NOT A RESULT`

Team cfd. Written 2026-08-26T21:20:20Z by a cfd lab-lane. Run under
`verification/campaign/F15_OSR29_PREREGISTRATION.md` frozen at
`2aea29d97c74f54183c1d99a28d86568ee254815`; comparator lineage R2 at
`893cdeaf107771072d3b21fb592b49e8faac9742`; **R3 registered at
`f3f92a89e8b5581c85321421d21bc2d73d34c82d`** (ADDENDUM R3 at the foot of
`F15_OSR29_R2_PREREGISTRATION.md`; grader `grade_f15_r3.py` blob
`3cedc19978a34889081778e165cacf9474a6d3cb`). **Zero new compute.** Nothing was
repaired inside R3; the registered command ran once, as registered.

## 0. THE GRADING, AS IT PRINTED

Command (R3 addendum §R3.5), run 2026-08-26T21:18:48Z from the repository root:
`python3 /home/ubuntu/Certonomous/cases/F15_oblique_shock_reflection/grade_f15_r3.py --prereg-commit=f3f92a89e8b5581c85321421d21bc2d73d34c82d`
— **rc 0** (2.47 s wall measured on the first run by `/usr/bin/time`; the registered command was then re-run with plain redirects so `GRADE_F15_R3.err` carries the grader's own stderr only — stdout and JSON rows byte-identical between the two runs). Stdout (`GRADE_F15_R3.out`), verbatim:

    F15-R3 -- OBLIQUE SHOCK REFLECTION M=2.9 -- TALLY (L-342 third registration; series windowed to t >= 0.813226)
    ==============================================================================
    G-F15-1_E1_pressure_L1_y0.5              NOT A RESULT
        levels coarse,fine,medium are not iteratively converged or not plateaued; no grid claim can be made from this triple
    G-F15-2_x_wall_impingement               PASS
        finest triple ('coarse', 'medium', 'fine') CONVERGING at dim = 2, observed order 1.5627, GCI 0.3714 % = 0.000721159 absolute at Fs = 1.25
    ==============================================================================
    gated by: scripts/roache_triple.py::grade_ladder
    written: /home/ubuntu/Certonomous/verification/runs/F15_runs/F15_R3_GRADED.json

Stderr (`GRADE_F15_R3.err`): empty. No refusal. `bookkeeping_defects: []`.

## 1. FROZEN FILES — disk == blob at the grading

| file | blob on disk | blob at the registration commit |
|---|---|---|
| `grade_f15_r3.py` | `3cedc199` | `3cedc199` at `f3f92a89` — SAME |
| `grade_f15_r2.py` (R3's parent) | `133820b3` | `133820b3` at `893cdeaf` — SAME |
| `grade_f15.py` (grandparent) | `e4076c03` | `e4076c03` at `2aea29d9` — SAME |
| `exact_osr.py` | `074d18c2` | `074d18c2` at `2aea29d9` — SAME |

Rule 4 completion was re-read by the grader at every level (`completion()` unchanged
from R2: `End`, latest + dt_final > 10, T U p at `10/` newer than `0/T`); the
independent re-read is RESULTS_R2.md §2 and is not repeated here. Infrastructure
census (L-342, reported not gated): ClockTime 68 / 524 / 4,299 s, `RC.txt` 0 / 0 / 0,
`STATUS.F15` `rc=0 end=2026-08-26T17:35:22Z`, total 81.5167 core-min of the 200 cap.

## 2. THE VERDICTS, WITH NUMBERS (`F15_R3_GRADED.json`)

The R3 window admitted **184 of 200 samples per level (t = 0.85 … 10.00)**; Class C
read its registered last-60-sample window, t ∈ [7.05, 10.00], span 2.95.

| gate | fine value | band (inherited, unchanged) | in band | triple (coarse, medium, fine) | Class C plateau | **verdict** |
|---|---|---|---|---|---|---|
| **G-F15-2** x_w wall impingement | **−0.194168900** | [−0.215952245, −0.175952245], ref −0.195952245 | yes (band verdict PASS; 1.78e−03 from the reference, 8.9 % of the half-width) | −0.189711013 / −0.193041503 / −0.194168900, **CONVERGING**, monotone, **p = 1.5627**, GCI 0.3714 % = 7.21e−04 abs at Fs 1.25, Richardson −0.194745827 | PLATEAUED × 3 (drift 3.4e−04 / 1.5e−04 / 2.5e−05; split 3.0e−04 / 7.6e−05 / 2.7e−05) | **`PASS`** |
| **G-F15-1** E1 normalised L1 p error, y = 0.5 | **7.512992721e−03** | [9.711165e−04, 7.768932e−03], ref 0 | yes (band verdict PASS; at 96.7 % of the upper edge) | 3.155165e−02 / 1.383011e−02 / 7.512993e−03, CONVERGING, monotone, p = 1.4882, GCI 58.2 % (value, both triples and order printed here because rule 5 clause (1) voids the row) | coarse **NOT_PLATEAUED_TREND** (relative drift over the window 8.26e−03 > 2.0e−03); medium **NOT_STATIONARY_MEAN** (two-half split 1.018e−03 > 1.0e−03); fine **NOT_STATIONARY_MEAN** (1.340e−03 > 1.0e−03) | **`NOT A RESULT`** |

Whole-field monitor (volAvg p, rule 5 limb 1): PLATEAUED → CONVERGED at all three
levels for both gates. Planted zeros (rule 3), both readers on the fine artefacts:
`e1_from_xy` planted 9.845301e−04 read back 9.845301e−04; `x_wall_from_xy`
planted 1.234e−03 read back 1.234e−03 (`fine/postProcessing/{lineY05,lineWall}/10/`).
Gate demonstration: both gates took a passing and a failing value through the real
reader (E1 1.168e−03 inside / 5.827e−02 outside; x_w −0.195952 inside / +0.154048
outside). Nine controls green, including the two R3 controls (window guard flipped:
windowed → the post-arrival crossing only; guard mutated → refusal on the
no-crossing sample, spurious +0.27 crossing first without it; gate blocks
AST-identical to R2, diff EMPTY, planted cap change seen).

**Reading, not softening.** G-F15-1's value sits inside its band and its triple is
CONVERGING at p ≈ 1.49, but the **graded functional's own series is not stationary
at the registered tolerance on any level** — the registered gate says a value read
from a series that has not plateaued is not a result, and it is not. The y = 0.5
line crosses both shocks; the L1 error there carries the slow drift of the reflected
shock's foot and of the outflow, at 1.0–1.3e−03 relative over the window against
the 1.0e−03 floor. The frozen ruling stands: `NOT A RESULT`, not "nearly plateaued".
Registered prediction **p ≈ 1** (prereg §1): G-F15-2 read **1.56**, G-F15-1 **1.49**
(voided) — both between first and second order; the F15/F16 ladder-instrument
comparison (p ≈ 1 vs p ≈ 2) is for the supervisor to read against F16b's rows, and
this record makes no claim on it.

## 3. WHAT R3 CHANGED AND WHAT IT DID NOT

Only the sample window (t ≥ T_ARRIVAL = 2/(u₁ sin 2σ) = 0.813226; formula and
two shorter stated bounds in ADDENDUM R3 §R3.2). The window drops samples the
plateau test and the graded value never read (Class C uses the last 60; the value is
the t = 10 sample), so **the verdicts above are what R2 would have printed had its
detector not refused on the pre-arrival sample** — the third reader defect voided a
grade, never the physics. Gates, bands, thresholds, cap and labels: byte-identical to
R2 and to `2aea29d9`, enforced by `control_gate_blocks_identical_to_r2` (24
definitions, diff EMPTY).

## 4. COST — rule 12 (the grading; the run is C-133)

| item | value |
|---|---|
| registered (ADDENDUM R3 §R3.5) | **0 core-min, $0** |
| actual | **0 solver core-min**; the grader itself 2.47 s wall / 3.78 CPU-s on one core (`/usr/bin/time`) = 0.063 core-min of reader time, not solver compute |
| ratio | 0 / 0 — as registered, zero-compute |
| waste | 0 |
| the run's own cost | **C-133** (81.5167 core-min gross, ratio 0.667 vs 122.2 predicted; RESULTS_R2.md §4) — unchanged by this grading |

**Calibration ledger: no new row.** `docs/COST_CALIBRATION.md`'s append rules
bind one row per completed process with figures from committed records; the run's
process row C-133 already carries the estimate-versus-actual comparison and its
figures are unchanged, and R3's registered 0 = actual 0 has nothing to calibrate. If
the supervisor reads "a rung graded" as owing a correcting row naming C-133 now that
the rung holds verdicts, that row is theirs to order; it is not written here.

## 5. NOT SENT

Nothing is sent, filed, uploaded or submitted (rule 7). Field data stays on disk
under this run root.
