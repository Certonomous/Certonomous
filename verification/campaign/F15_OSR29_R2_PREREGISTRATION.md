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
