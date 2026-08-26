# F15-R2 — COMPARATOR RE-REGISTRATION under L-342: oblique shock reflection, M∞ = 2.9

**Team:** cfd. **Written 2026-08-26, while the fine level of run `2aea29d9` is
still running (coarse and medium complete; `STATUS.F15` not yet written).
ZERO CORE-MINUTES OF NEW COMPUTE.** Frozen by the commit that carries this file
together with `cases/F15_oblique_shock_reflection/grade_f15_r2.py`
(blob `133820b314baeae42281da26b1d1469a7e0189fb`). **Grading waits for
`verification/runs/F15_runs/STATUS.F15` with `rc=0`; nothing is graded before.**

## 1. INHERITANCE — BY REFERENCE, NOT BY COPY

This document inherits **`verification/campaign/F15_OSR29_PREREGISTRATION.md`
at commit `2aea29d97c74f54183c1d99a28d86568ee254815`** (blob `43401856`,
identical on disk and at HEAD; Amendments 1 and 2 included), in full: the case
and its source (§2), the exact solution (§3), the ladder 200×50 / 400×100 /
800×200 (§4), **the gates and their bands (§5, lines 114–143)**, the criteria
(§6), the gate demonstration (§7) and the cost basis (§8). Nothing is struck,
amended or re-stated with a different number here.

| gate | band (inherited verbatim, prereg §5) | reference |
|---|---|---|
| G-F15-1 normalised L1 pressure error along y = 0.5 | [9.711165159e−04, 7.768932127e−03] | 0 |
| G-F15-2 incident-shock wall impingement x_w | −0.195952244729 ± 0.020000000000 = [−0.215952244729, −0.175952244729] | −0.195952244729 |

**Prediction (inherited, prereg §1 line 20 and §Amendment 1 line 336): observed
order p ≈ 1** — a discontinuous solution's L1 error converges at first order
whatever the interior scheme; the F15/F16 pair exists to show the ladder
instrument distinguishes p ≈ 1 from p ≈ 2. Registered cap: 200 core-minutes
(inherited). **Cost of this registration: 0 core-minutes, $0** — the grader
opens files already on disk and launches nothing. The run's own cost is
attributed to the run `2aea29d9` itself and is reported in `RESULTS_R2.md` from
the three logs' ClockTime lines (coarse 68 s, medium 524 s measured now; fine
pending).

## 2. THE DEFECTS (measured on the preserved artefacts, not inferred)

**(i) The log regexes.** `grade_f15.py:342-344` compile `TIME_RE`, `DELTAT_RE`
and `CLOCK_RE` as `^`-anchored patterns **without `re.MULTILINE`** and apply them
with `.finditer(text)` to the whole log (lines 364–366). `^` matches at byte 0
only; a real log opens with the banner. Measured: **0 of 9233 `Time =` lines** in
`verification/runs/F15_runs/coarse/log.rhoCentralFoam` (`grep -c '^Time = '` =
9233; medium 18760). `completion()` would therefore return "no `Time =` lines in
the log" and both gates PENDING on a complete level — exactly what F16's frozen
comparator printed at `6f8048b9`. `CLOCK_RE` has a second, independent defect:
the real line is `ExecutionTime = 67.58 s  ClockTime = 68 s`, so `^ClockTime`
could match nothing even with MULTILINE; R2 drops that anchor.

**(ii) The sample reader.** `grade_f15.py:123-136` `read_xy_p` pins **4 columns
(x y z p)** and reads p from column 3. That layout was measured on F6b's
`type midPoint; axis xyz` sets. This case's sets are `type midPoint; axis x`
(`cases/F15_oblique_shock_reflection/case/system/controlDict:32,43`, on disk at
`F15_runs/coarse/system/controlDict:32,43`), and OpenFOAM's raw writer emits ONE
coordinate column for a single axis: the real
`coarse/postProcessing/lineWall/9.95/lineWall_p.xy` is **2 columns, 200 rows**
(x p; medium 400 rows), `lineY05_p.xy` likewise. The frozen reader would refuse
every sample. This is the same defect F16-R2 hit after its regex was repaired
(`verification/runs/F16_runs/RESULTS_R2.md` §3 Finding A), which is why this
registration's scope is wider than F16-R2's — cfd-supervisor's ruling of
2026-08-26, quoted in `RESULTS_R2.md` when it lands.

## 3. GROUND — L-342, and rule 2 honoured

Sanaa's universal rule (`docs/LESSONS.md` L-342; CHIEF addendum `d4d0c29d`):
*"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts
— and graders must separate physics-critical fields from infrastructure fields
so a dead poller can never void a run again."* Both defects are in the
comparator's readers — bookkeeping. The solver logs, fields and sampled lines are
physics artefacts, intact on disk. Precedent: D4-SHIPPED arm O re-graded on
preserved artefacts; F16-R2 at `ebe1b893`.

`grade_f15.py` is NOT edited. This is a NEW registration committed BEFORE it
runs, grading the preserved artefacts at zero compute.

## 4. THE PHYSICS ARTEFACTS ARE NON-TRIVIAL (checked before registering)

Unlike F16 (identically zero fields, `RESULTS_R2.md` Finding B), F15's preserved
fields carry the shock: wall pressure on `lineWall_p.xy` at t = 9.95 spans
**0.714285714285 → 3.16647879369 at coarse** and **0.714285714285 →
3.16760379247 at medium** (p1 = 0.714286 upstream; the double-shock rise is of
the exact post-reflection order), `Mean and max Courant Numbers = 0.1886
0.2011` at the last step, `diagonal: Solving for rho, rhoUx, rhoUy, rhoE` at
every step (rhoCentralFoam is explicit density-based; there are no `Solving for
Ux` lines in the inviscid setting and none are expected), 9233 / 18760 steps to
`Time = 10`, `End` present, `RC.txt` = 0 at both levels.

## 5. DIFF SCOPE — `grade_f15_r2.py` against its parent (blob `e4076c03`)

Unified diff hunks (`diff -u grade_f15.py grade_f15_r2.py`), eleven, and nothing
outside them:

| parent lines | R2 lines | content |
|---|---|---|
| 1–5 | 1–47 | header docstring: parent blob, both defects, diff scope, byte-identity statement |
| 63 | 105–162 | L-342 field-class declaration (`PHYSICS_CRITICAL`, `INFRASTRUCTURE`) and `infrastructure_census()` — prints `BOOKKEEPING DEFECT` lines, never refuses |
| 125–139 | 224–239 | `read_xy_p`: pin 4 → **2** columns, x = column 0, **p = column 1** |
| 203 | 303 | `plant_control_e1`: the p-column plant index 3 → 1 (the plant still goes into the real artefact through the real parser) |
| 316 | 416 | class-C exit-2 probe imports THIS module by basename |
| 339–347 | 439–449 | **`TIME_RE`, `DELTAT_RE` with `re.MULTILINE`; `CLOCK_RE` with `re.MULTILINE` and without the `^` anchor** |
| 410 | 512–620 | `REAL_LOG_EXCERPT`, `REAL_XY_EXCERPT` (verbatim) and the two driven controls |
| 522 | 727 | `synth_xy` writes the real 2-column shape, so the gate demonstration still passes through the real write format |
| 753 | 958–960 | the two controls appended to the controls list |
| 777–793 | 984–1005 | `rung` F15-OSR29-R2, parent blob, R2 prereg path, field classes and census in the JSON; default output `F15_R2_GRADED.json`; tally title |
| 795 | 1007–1014 | defect lines beside the tally |

**Gates, bands, thresholds, cap and labels are BYTE-IDENTICAL.** Evidence:
`diff <(grep -E 'N_CAPTURE|BAND|CAP|THRESH|band|cap|CLASS_C|END_TIME|SAMPLE_INTERVAL|grade_ladder\(' grade_f15.py) <(same on grade_f15_r2.py)`
reports **0 deleted and 0 changed lines** (additions only, all in the header and
field-class blocks; none assigns a gate constant). `N_CAPTURE_CELLS = 8`,
`END_TIME = 10.0`, `SAMPLE_INTERVAL = 0.05`, `CAP_CORE_MIN = 200.0`, `CLASS_C`,
`bands()`, `smeared_profile()`, `demonstrate()`, `grade_one()` and the single
`RT.grade_ladder(` call are unchanged lines. 0 `ast.Assert` nodes; `--selftest`
rc 0 (7 controls; the four demonstration rows land inside/outside as intended
through the 2-column writer); `python3 -O` rc 2.

**Refusals reclassified under L-342: none.** The parent keys no refusal on an
infrastructure field; `clock_time_s` was recorded as detail and never gated.
R2's census reads ClockTime, `RC.txt` and `STATUS.F15` as INFRASTRUCTURE and
prints `BOOKKEEPING DEFECT ... NOT MEASURED` beside the verdict when one is
absent; the grade proceeds.

## 6. THE DRIVEN CONTROLS THE PARENT LACKED (results at registration)

- `control_completion_reads_a_real_log`: 62 verbatim lines of
  `coarse/log.rhoCentralFoam` (`Starting time loop` through the fifth step, plus
  the last 20 lines with `Time = 10`, `ClockTime = 68 s`, `End`). Planted
  **5 `Time =`, 5 `deltaT =`, 5 ClockTime, 1 `End`**; the parent's anchored
  non-MULTILINE form counts **0**; R2 counts **5/5/5/1**; `completion()` on a
  synthetic case around the excerpt returns done=True, n_times 5, latest 10.0,
  dt_final 1.13636363636e−03, clock_time_s 68; with the `Time =` lines removed:
  done=False, "no `Time =` lines in the log".
- `control_sample_reader_on_real_xy`: 39 verbatim rows of
  `coarse/postProcessing/lineWall/9.95/lineWall_p.xy` (head, the rows around the
  shock, tail). `read_xy_p` returns 39 rows, x ∈ [−1.99, 1.99],
  p ∈ [0.714285714285, 3.16647879369]; the same rows re-written in the parent's
  4-column layout are **refused (exit 2)** in a subprocess.

## 7. THE ARTEFACTS THIS ROW WILL GRADE — blob and mtime evidence at registration

Under `verification/runs/F15_runs/` (`git hash-object`, epoch mtime, UTC):

| artefact | blob | mtime |
|---|---|---|
| coarse/0/T (launch stamp) | 8352231d | 1787760827, 16:13:47 |
| coarse/log.rhoCentralFoam (9233 Time lines, ClockTime 68 s) | 81b06dcd | 1787760895, 16:14:55 |
| coarse/10/p | 37dbfae6 | 1787760895, 16:14:55 |
| coarse/RC.txt (= 0) | 573541ac | 1787760895 |
| medium/0/T | 8352231d | 1787760896, 16:14:56 |
| medium/log.rhoCentralFoam (18760 Time lines, ClockTime 524 s) | 4e17d1ae | 1787761420, 16:23:40 |
| medium/10/p | 3f8ad165 | 1787761420, 16:23:40 |
| medium/RC.txt (= 0) | 573541ac | 1787761420 |
| fine/ | **RUNNING** at registration (lineWall samples to t = 0.85, ClockTime 419 s at 16:31Z); its blobs are recorded in `RESULTS_R2.md` when `STATUS.F15` lands |

Age guard holds at coarse and medium (`10/p` newer than the level's own `0/T`).
Field data stays on disk, not committed. **Nothing is launched by this row.**

## 8. WHAT IS REGISTERED HERE, AND WHAT IS NOT

Registered: `grade_f15_r2.py` at the blob above; outputs
`verification/runs/F15_runs/GRADE_F15_R2.out` and `F15_R2_GRADED.json`; record
`verification/runs/F15_runs/RESULTS_R2.md`; prediction p ≈ 1; cost 0; the
condition that grading waits for `STATUS.F15` with `rc=0`. Not registered: any
change to a gate, band, threshold, cap or label (none is permitted under L-342
clause 4); any new compute; any change to `grade_f15.py`, `exact_osr.py`,
`run_f15.sh` or the parent pre-registration.

## ADDENDUM R3 — 2026-08-26T21:18:33Z

**Team cfd, lab-lane on the cfd supervisor's ruling (board cd24ebea; the 17:46Z
ruling (1) in LAB_STATE). Third comparator registration under L-342. ZERO
COMPUTE. Lines above this heading changed by this addendum: 0** (the file is
rebuilt from `git show HEAD:` and this section is appended at the foot).
Frozen by the commit that carries this addendum together with
`cases/F15_oblique_shock_reflection/grade_f15_r3.py` (blob `3cedc19978a34889081778e165cacf9474a6d3cb`).

### R3.1 The defect this registration repairs (measured, RESULTS_R2.md §0(b))

R2 refused at zero compute (`GRADE_F15_R2.err`, verbatim: *"REFUSED:
.../coarse/postProcessing/lineWall/0.05/lineWall_p.xy: the wall pressure never
crosses the half-rise value 1.824133; min 0.714286 max 0.714286. The gate quantity
is ABSENT ..."*). `series_for` (`grade_f15_r2.py:832`) feeds `x_wall_from_xy`
every sampled time from t = 0.05; the run is initialised uniform at region 1
(`0/p internalField uniform 0.714285714285714`, `0/U (2.9 0 0)`) with the
post-shock state imposed on `top`, so the wall line carries no crossing until the
shock reaches it. The half-rise crossing detector is a steady-state instrument
applied to pre-arrival samples — the third reader defect of this lineage, named
in RESULTS_R2.md and repaired only here, in a new registration, never in R2.

### R3.2 The repair: the series is windowed to t ≥ T_ARRIVAL, from the frozen geometry

From `exact_osr.py` (frozen at `2aea29d9`): M₁ = u₁/a₁ = 2.9 (a₁ = 1), incident
shock angle σ = 29° from the x-axis, domain X_MIN = −2, Y ∈ [0, 1], station
x_w = X_MIN + (Y_MAX − Y_MIN)/tan σ = −0.195952244729 (prereg §3). The incident
shock enters at the top-left corner (X_MIN, Y_MAX) and its foot sits at (x_w, 0).
Path length along the shock line: L_s = (Y_MAX − Y_MIN)/sin σ = 1/sin 29° =
2.062665. The disturbance that establishes the shock is carried along that line at
the shock-tangential velocity, equal on both sides of the shock, u₁ cos σ =
2.9 × cos 29° = 2.536451. Hence

    T_ARRIVAL = L_s / (u₁ cos σ) = 1 / (u₁ sin σ cos σ) = 2 / (u₁ sin 2σ)
              = 2 / (2.9 × sin 58°) = **0.813226**

(`arrival_time(sol)`, computed from `EX.solve()` at every run; a literal appears
nowhere in the grader). At SAMPLE_INTERVAL = 0.05 the **first admitted sample is
t = 0.85**; the series then holds 184 of the 200 written samples, above Class C's
100-sample floor, and Class C's last-60-sample window (t ∈ [7.05, 10]) and the graded
value (the t = 10 sample) are untouched by the window. The window is applied in
`series_for` for both gates so the two series are built from the same samples;
G-F15-1's reader has no crossing detector, so for it the window only drops
pre-arrival samples that neither the plateau test nor the graded value ever read.

Two shorter kinematic bounds exist and are stated so the choice is on record, not
hidden: pure free-stream convection of the inlet corner to the station,
(x_w − X_MIN)/u₁ = 0.622; and the top-boundary-driven planar front descending to the
wall as a moving shock at p₂/p₁ = 2.139 (M_s = 1.406, a₁ = 1), ≈ 0.711. Neither is the
path of the incident shock; the registered window is the shock-path formula above.
**Honest note on order of knowledge:** R2's record already states that the first
sample with a crossing is t = 0.75. The formula was derived from the frozen geometry,
not fitted to that observation; its consequence is that the windowed series starts at
0.85 > 0.75. Had the formula given a window start ≤ 0.70, R3 would refuse exactly as
R2 did, and that refusal would be recorded verbatim (§R3.5).

### R3.3 Diff scope — `grade_f15_r3.py` against its R2 parent (blob `133820b3`), and nothing else

| R2 lines | R3 content |
|---|---|
| 1–5 header | R3 header block (defect (iii), the formula, diff scope); R2 header retained verbatim below it |
| 112–118 | `PHYSICS_CRITICAL` gains the window line; `T_ARRIVAL_NOTE` |
| 832–847 | `arrival_time(sol)`; `series_for(..., t_min=None)` with the guard `if t < t_min - 1e-9: continue` |
| before 617 | `control_window_guard_flips`, `GATE_BLOCK_NAMES`, `_gate_blocks`, `control_gate_blocks_identical_to_r2` |
| 962–963 | the two controls appended to the controls list |
| 988–992, 1002 | `rung` F15-OSR29-R3, parent/grandparent blobs, `t_arrival` in the JSON; default output `F15_R3_GRADED.json`; tally title |

**Gates, bands, thresholds, cap and labels are byte-identical to R2 and to the
grandparent.** Evidence in the grader itself: `control_gate_blocks_identical_to_r2`
dumps the AST of 24 gate-bearing definitions (`N_CAPTURE_CELLS`, `END_TIME`,
`SAMPLE_INTERVAL`, `CAP_CORE_MIN`, `RANKS`, `LEVELS`, `CELLS`, `DX`, `CLASS_C`,
`DIM`, `VERDICTS`, `SETS`, `bands`, `smeared_profile`, `demonstrate`, `class_c`,
`x_wall_from_xy`, `e1_from_xy`, `read_xy_p`, `grade_one`, `completion`,
`iterative_series`, `plant_control_e1`, `plant_control_x_wall`) in both files and
refuses unless the diff is **EMPTY** — at registration: `differing: []`, `diff:
EMPTY`; driven: a copy of R2 with `CAP_CORE_MIN` 200.0 → 201.0 is seen to differ in
exactly `["CAP_CORE_MIN"]`. Bands inherited unchanged: G-F15-1
[9.711165159e−04, 7.768932127e−03]; G-F15-2 −0.195952244729 ± 0.02. Prediction
p ≈ 1 inherited. Field-class split (L-342) retained; the window is PHYSICS_CRITICAL.

### R3.4 Controls at registration (`python3 grade_f15_r3.py --selftest`, rc 0, 9 controls)

- `PZ-F15-R3-WINDOW_GUARD_driven_both_ways`: synthetic `lineWall` series with a
  no-crossing sample at t = 0.05 (R2's defect), a spurious crossing at x = +0.27 at
  t = 0.5 (the shape R2 measured at t = 0.75), and the true crossing at x_w at
  t = 0.95. Windowed: returns **one** sample, t = 0.95, x = −0.195952244729. Guard
  mutated to a no-op (t_min = 0): with the no-crossing sample present the reader
  **refuses (exit 2)** as R2 did; with it absent it returns the **spurious** crossing
  first ([0.5, 0.95] → [+0.27, −0.1960]). The control flips on the guard alone.
- `PZ-F15-R3-GATE_BLOCKS_ast_identical_to_R2_plus_planted_diff`: EMPTY, planted
  cap change seen.
- The seven R2/parent controls unchanged (paper agreement, Rankine–Hugoniot,
  geometry, Class C four limbs, grade_ladder call-site AST census, real-log excerpt,
  real-xy excerpt); planted-zero controls on both readers at grade time unchanged.
- 0 `ast.Assert` nodes; `python3 -O` rc 2.

### R3.5 What is registered, and what is not

Registered: `grade_f15_r3.py` at the blob above; the command
`python3 cases/F15_oblique_shock_reflection/grade_f15_r3.py --prereg-commit=<this sha>`
on the preserved artefacts of run `2aea29d9` under `verification/runs/F15_runs/`
(`STATUS.F15` rc=0 landed 17:35:22Z; rule 4 re-read in RESULTS_R2.md §2); outputs
`GRADE_F15_R3.out`, `GRADE_F15_R3.err`, `F15_R3_GRADED.json`, record `RESULTS_R3.md`.
Verdicts from the fixed vocabulary only. **If R3 refuses, the refusal is recorded
verbatim and nothing is repaired inside R3.** Cost: **0 core-min, $0** (files already
on disk; nothing launched); the run's own cost is C-133 and no new calibration row is
owed unless `docs/COST_CALIBRATION.md`'s rules require one for a zero-compute grade.
Not registered: any change to a gate, band, threshold, cap or label; any new compute;
any change to `grade_f15.py`, `grade_f15_r2.py`, `exact_osr.py`, `run_f15.sh` or
the lines above this heading.
