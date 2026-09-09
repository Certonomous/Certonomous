# F15-OSR29-R3 — oblique shock reflection, M∞ = 2.9, `rhoCentralFoam` — RESULTS

**Team cfd.** Run under `verification/campaign/F15_OSR29_PREREGISTRATION.md` frozen at
`2aea29d97c74f54183c1d99a28d86568ee254815`; comparator lineage R2 at
`893cdeaf107771072d3b21fb592b49e8faac9742`; **R3 registered at
`f3f92a89e8b5581c85321421d21bc2d73d34c82d`** (ADDENDUM R3 at the foot of
`verification/campaign/F15_OSR29_R2_PREREGISTRATION.md`; grader `grade_f15_r3.py`
blob `3cedc19978a34889081778e165cacf9474a6d3cb`). R3 is the **third grader
registration** under L-342 — the series is windowed to t ≥ T_ARRIVAL = 2/(u₁ sin 2σ)
= 0.813226 from the frozen geometry. **Zero new compute**; nothing was repaired
inside R3, the registered command ran once as registered. Check-1 (grader diff) and
check-3 (verdict) cleared by the cfd-supervisor before filing.

## 0. VERDICTS — fixed vocabulary

| gate | fine value | registered band (inherited, unchanged) | triple / plateau | verdict |
|---|---|---|---|---|
| G-F15-1 `E1_pressure_L1_y0.5` | **7.512993e−03** | [9.711165e−04, 7.768932e−03]; ref 0 | triple CONVERGING, monotone, p = 1.4882 (**printed, value voided by rule 5 clause (1)**); series NOT stationary — coarse NOT_PLATEAUED_TREND (drift 8.26e−03 > 2.0e−03), medium/fine NOT_STATIONARY_MEAN (two-half split 1.018e−03 / 1.340e−03 > 1.0e−03) | **NOT A RESULT** |
| G-F15-2 `x_wall_impingement` | **−0.194168900** | [−0.215952245, −0.175952245]; exact −0.195952245 | **CONVERGING**, monotone, **p = 1.5627**, GCI 0.3714 % = 7.21e−04 absolute at Fs = 1.25; PLATEAUED × 3 | **PASS** |

**Reading, not softening (rule 1).** G-F15-1's fine value lies *inside* its band and
its triple is CONVERGING at p ≈ 1.49, but the graded functional's own series is not
stationary at the registered tolerance on any level — the registered gate rules that
a value read from a non-plateaued series is **NOT A RESULT**, and it is; the value,
both triples and the order are printed beside it per rule 5 clause (1). This is not
"nearly plateaued." The y = 0.5 line crosses both shocks and carries the slow drift
of the reflected-shock foot and the outflow. Registered prediction p ≈ 1: G-F15-2
read 1.56, G-F15-1 1.49 (voided). The whole-field volAvg-p monitor is
PLATEAUED/CONVERGED at all three levels for both gates.

## 1. PROVENANCE RECONCILIATION

The 2026-08-26 `F15_F16_LAUNCH_RECORD_2026-08-26.md` (`BLOCKED`, 0 core-min)
documents a denied *direct* launch of `run_f16.sh` — it names no F15 launch. F15's
own launcher ran: `STATUS.F15.attempt1` = `rc=1 end=2026-08-26T16:12:33Z` (died at
the L-339 bashrc `set -u` face before any solver ran — waste 0), then **`STATUS.F15`
= `rc=0 end=2026-08-26T17:35:22Z`**. `verification/runs/F15_runs/launcher.out` shows
all three levels COMPLETE, 81.5167 core-min of cap 200; committed "RUN COMPLETE" at
`3c21d87c`. Grading history: R1 `grade_f15.py` (`2aea29d9`) read 0 `Time` lines (the
non-MULTILINE `TIME_RE`, rc 0 → PENDING); R2 `grade_f15_r2.py` (`893cdeaf`) REFUSED
rc 2 on a pre-arrival sample; **R3 windows the series to t ≥ T_ARRIVAL and grades the
preserved artefacts** (commit `c012a8bd`, 21:20Z).

**Disclosed provenance gap — flagged, completions sound:** F15 has **no
`LAUNCH_LOG.tsv` row and no queue entry** (unlike F16b, which was queue-launched via
pid 189904). Its launch went through a direct `run_f15.sh` invocation that executed
and completed cleanly. The runs are legitimate completions — rc 0, `End`, last Time
== endTime, and the age guard hold at every level (§3) — so this is a
**launch-authorization documentation gap, not a completion defect.** Surfaced here
for the record.

## 2. FROZEN FILES — disk == blob at the grading

| file | blob on disk | at registration commit |
|---|---|---|
| `cases/F15_oblique_shock_reflection/grade_f15_r3.py` | `3cedc199` | `3cedc199` at `f3f92a89` — SAME |
| `grade_f15_r2.py` (R3's parent) | `133820b3` | `133820b3` at `893cdeaf` — SAME |
| `grade_f15.py` (grandparent) | `e4076c03` | `e4076c03` at `2aea29d9` — SAME |
| `exact_osr.py` | `074d18c2` | `074d18c2` at `2aea29d9` — SAME |

The grader `grade_f15_r3.py` is tracked and byte-identical to HEAD (check-1 clear).
Gated by `scripts/roache_triple.py::grade_ladder`, 0 `assert` nodes across 2 files,
run under plain `python3` (exits 2 under `-O`). **Independently reproduced live** by
this lane (re-graded with the frozen `grade_f15_r3.py`, rc 0; verdicts and values
identical to `F15_R3_GRADED.json`).

## 3. RULE 4 — strict completion, re-read at the run root

| level | cells | `RC.txt` | `End` | last Time == endTime | fields at `10/` | age guard: `0/T` → `10/T` (UTC 2026-08-26) |
|---|---|---|---|---|---|---|
| coarse | 10000 | 0 | 1 | 10 == 10 | T U p | 16:13:47.919 → 16:14:55.573 — **NEWER-OK** |
| medium | 40000 | 0 | 1 | 10 == 10 | T U p | 16:14:56.526 → 16:23:40.367 — **NEWER-OK** |
| fine | 160000 | 0 | 1 | 10 == 10 | T U p | 16:23:43.560 → 17:35:22.660 — **NEWER-OK** |

Age guard PASSES at every level: each field at `endTime` (T, U, p) is strictly newer
than that case's own `0/T`. Adaptive Δt (`n_times` 9233 / 18760 / 37851;
`latest + dt_final > 10`). Infrastructure census (L-342, reported not gated):
ClockTime 68 / 524 / 4,299 s, total **81.5167 core-min of the 200 cap**.

## 4. RULE 5 / gate demonstration

The R3 window admitted **184 of 200 samples per level (t = 0.85 … 10.00)**; Class C
read its registered last-60-sample window (t ∈ [7.05, 10.00], span 2.95).
G-F15-2: triple −0.189711013 / −0.193041503 / −0.194168900, CONVERGING, monotone,
p = 1.5627, GCI 0.3714 % = 7.21e−04 abs, PLATEAUED × 3 → **PASS** (1.78e−03 from the
reference, 8.9 % of the half-width). G-F15-1: triple 3.155165e−02 / 1.383011e−02 /
7.512993e−03, CONVERGING p = 1.4882, but Class C not stationary → **NOT A RESULT**.

**Planted-zero control (rule 3): PASS**, both readers on the fine artefacts
(`verification/runs/F15_runs/fine/postProcessing/{lineY05,lineWall}/10/`):
`e1_from_xy` planted 9.845301e−04 / read back 9.845301e−04; `x_wall_from_xy` planted
1.234e−03 / read back 1.234e−03. Gate demonstration passed both ways (E1 1.168e−03
inside / 5.827e−02 outside; x_w −0.195952 inside / +0.154048 outside). Nine controls
green, including the two R3 controls (window guard flips to the post-arrival crossing
only, refuses on the no-crossing sample; gate blocks AST-identical to R2, diff EMPTY,
planted cap change seen).

## 5. WHAT R3 CHANGED — and what it did not

Only the sample window (t ≥ T_ARRIVAL = 0.813226; first admitted sample 0.85). The
window drops samples the plateau test and the graded value never read, so the
verdicts above are what R2 would have printed had its detector not refused on the
pre-arrival sample — the third reader defect voided a *grade*, never the physics.
Gates, bands, thresholds, cap and labels are byte-identical to R2 and to `2aea29d9`
(enforced by `control_gate_blocks_identical_to_r2`, 24 definitions, diff EMPTY).

## 6. COST — rule 12 (calibration row C-133 already landed; unchanged)

| item | value |
|---|---|
| R3 grading, registered (ADDENDUM R3 §R3.5) | **0 core-min, $0** |
| R3 grading, actual | **0 solver core-min**; grader ≈ 0.063 core-min reader time (not solver compute); ratio 0/0 as registered |
| the run's own compute cost | **row C-133** (81.5167 core-min gross MEASURED; ratio 0.667 vs 122.2 predicted — inviscid `mu 0` vs a viscous rate basis; waste 0) |

The run's estimate-vs-actual comparison is `docs/COST_CALIBRATION.md` **row C-133**
(already landed). R3 is a zero-compute re-grade: registered 0 = actual 0 has nothing
to calibrate, and the run's process row is unchanged. **No new calibration row is
written for this filing** — adding one would duplicate in an append-only ledger.

## 7. NOT SENT

Gates, bands, thresholds, cap and labels unchanged. **Nothing is sent, filed,
uploaded or submitted outside the box** (rule 7). Field data stays on disk under
`verification/runs/F15_runs/`.

**Artifacts (absolute under `/home/ubuntu/Certonomous`):**
`verification/runs/F15_runs/{coarse,medium,fine}`;
`verification/runs/F15_runs/{F15_R3_GRADED.json,GRADE_F15_R3.out,RESULTS_R3.md,launcher.out,STATUS.F15,STATUS.F15.attempt1}`;
`cases/F15_oblique_shock_reflection/{grade_f15_r3.py,grade_f15_r2.py,grade_f15.py,exact_osr.py}`;
`verification/campaign/{F15_OSR29_PREREGISTRATION.md,F15_OSR29_R2_PREREGISTRATION.md}` (R3 addendum, frozen `f3f92a89`);
`docs/COST_CALIBRATION.md` row C-133.
