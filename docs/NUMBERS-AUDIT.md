# Numbers validation audit (working document, not on-camera)

Every headline number each act shows on camera, cross-checked against its raw
source with an independent recomputation. Rule of the audit: any mismatch
beyond display rounding is investigated and the CODE is fixed — no number is
ever adjusted to match.

All acts were re-run headless (emit-capture drivers, solvers live via
`OPENVSP_RUN_PREFIX="wsl -d Ubuntu --"` / OpenFOAM in WSL), sequentially,
on 2026-07-23/24. Recomputation scripts live outside the repo (session
scratchpad); every check below states both values.

## Verdict summary

| # | Act | Check | Reported | Recomputed from raw source | Result |
|---|-----|-------|----------|---------------------------|--------|
| 1 | Airliner | Screened best L/D (sizing model, independent reimplementation) | 18.5 (span 64 m, AR 13.7) | 18.4964 (span 64, area 300, sweep 25) | PASS |
| 2 | Airliner | Solved winner L/D from raw polar (`cl_cruise/(cd0_nonwing+cdo_wing+cdi)`) | 19.7 (19.7377) | 19.7377 (CDi 0.005104, CDo 0.005946 interpolated at CLtot 0.4747 from `wing-area300-re_cref2.86495e+07-span64-sweep35/result.json`) | PASS |
| 3 | Airliner | Headline CI vs `winner_ci95` machinery | 1.9 | input MC 2σ = 1.0052 (independent MC reimplementation: 1.0052), RSS with model-anchors band 1.596 → 1.886 → "1.9" | PASS |
| 4 | MotorBike | Cd vs `coefficient.dat` final-window statistics | 0.4156 ± 0.00085 over 60 iters | 0.415577 ± 0.000848 over final 60 of 300 rows | PASS |
| 5 | MotorBike | Cl vs `coefficient.dat` | 0.0649 ± 0.00061 | 0.0648959 ± 0.0006065 | PASS |
| 6 | MotorBike | Mesh numbers vs `log.checkMesh` | 353,578 cells; non-ortho 65.0°; skew 8.94 | 353578; 64.9972; 8.94131 | PASS |
| 7 | MotorBike | Combined 95% CI arithmetic | 0.17 | RSS(0.0008482, 0.16528, 0.00179) = 0.16529 → "0.17" | PASS |
| 8 | B-52 | Cd vs `coefficient.dat` final window | 0.0464 ± 1.3e-05 over 60 iters | 0.0463986 ± 1.286e-05 over final 60 of 300 rows | PASS |
| 9 | B-52 | Cl vs `coefficient.dat` | 0.04283 ± 2.1e-05 | 0.0428306 ± 2.122e-05 | PASS |
| 10 | B-52 | Mesh numbers vs `log.checkMesh`; combined CI | 193,815 cells; non-ortho 57.1°; skew 5.06; CI 0.003 | 193815; 57.143823; 5.0580476; RSS(1.286e-05, 0.00303) = 0.003030 | PASS |
| 10a | NACA 4412 | Cd vs `coefficient.dat` final window; mesh | 0.01892 ± 1.9e-05 over 24 iters; 337,334 cells, non-ortho 49.9°, skew 3.32 | 0.0189223 ± 1.852e-05 over final 24 of 120 rows; 337334 / 49.921642 / 3.3231909 verbatim | PASS |
| 10b | NACA 4412 | Cd vs Abbott & von Doenhoff reference; 37%/±40% band arithmetic | rel. error 0.3693, "within 37% … band ±40%", VALIDATED | \|0.0189223 − 0.030\|/0.030 = 0.36926 → 0.3693; 0.3693 ≤ 0.40 → inside band → VALIDATED; planform basis, no rebase (verified) | PASS |
| 11 | Valve | Cycle-weighted loss vs phase-weighted sum (0.25/0.50/0.25) | was 1345 Pa — **FAIL**, fixed in code, now 1327 Pa | 1326.83 Pa (weights 0.25/0.50/0.25 × per-phase 530.7/2122.9/530.7 Pa) | PASS after fix |
| 12 | Valve | Winner angle/loss consistency | 80° at 1327 Pa | independent sweep: loss strictly decreasing with angle; widest feasible orifice (403 mm² ≥ 160 mm² floor) is 80° at 1326.8 Pa | PASS |
| 13 | Race | MC core-minutes from per-solve seconds | 30.79 core-min (88 solves) | Σ(solve_seconds)=461.9 s × 4 threads / 60 = 30.79 | PASS |
| 14 | Race | ROM core-minutes from per-solve seconds | 1.95 core-min (5 solves) | Σ(solve_seconds)=29.2 s × 4 / 60 = 1.95 | PASS |
| 15 | Race | Speedup | 15.8× | 30.79 / 1.95 = 15.8× | PASS |
| 16 | Race | Agreement % from the two peaks | 0.1% | 100·\|18.12−18.14\|/18.12 = 0.11 → 0.1% | PASS |

## Details per act

### Airliner (aircraft_optimization)

Run twice — the short demo directive (300 pax / 6000 km, `deadline_minutes=2`,
`hold_workers_back`) and a plain 300-pax request with no time language. Both
produced 9 finalist polars, tier SOLVER-BACKED, winner span 64 m / sweep 35°,
L/D 19.7 ± 1.9 (95%).

- **Screened best**: the sizing model (weights from pax count, drag polar,
  Breguet, stall limits) was re-implemented from the stated constants without
  calling `evaluate_design`; both give L/D 18.4964 at span 64 / area 300 /
  sweep 25 — the transcript's "18.5".
- **Solved winner**: interpolating the raw `result.json` polar columns
  (CDi, CDo vs CLtot) at the winner's cruise CL 0.4747 and forming
  `0.4747 / (0.013 + 0.005946 + 0.005104)` reproduces 19.7377 exactly; the
  `matched` block in the file agrees with the independent interpolation to
  6 decimals.
- **CI**: `winner_ci95` (Monte-Carlo over payload ±2.5%σ and non-wing drag
  ±4%σ through the solved polar) gives 1.0052; an independent MC
  re-implementation gives 1.0052; the displayed 1.9 is the documented RSS
  combination with the stored model-anchors band (1.596):
  √(1.0052² + 1.596²) = 1.886 → "1.9".

### MotorBike (geometry_study, familiar body)

Fresh headless run, 300 iterations, warm mesh. Checks 4–7 all pass exactly:
the reported Cd/Cl are the final-20%-window means of
`postProcessing .../coefficient.dat` (window 60 of 300 rows), the ±bands are
2× the sample standard deviation over that window, mesh numbers are verbatim
from `log.checkMesh` (display-rounded only), and the headline CI is the RSS
of the settling band with the stored refinement-study and closure-spread
bands.

### Valve (valve_study)

**One real mismatch found and fixed in code.** The act's headline "cycle-
weighted pressure loss" was `_mc_envelope`'s **mean** (1345 Pa at 80°), not
the phase-weighted sum of the per-phase losses the act itself emits
(0.25·530.7 + 0.50·2122.9 + 0.25·530.7 = 1326.8 Pa). The gap (+1.4%) is the
convexity bias of dp ~ Q²/Cd² under the input spread — a systematic shift,
not display rounding. Fix (`sdk/workflows/valve_study.py`): the objective is
now `_cycle_weighted_loss(angle, phases)` — exactly the weighted sum of the
emitted phase evaluations — and the Monte-Carlo envelope supplies only the
±band, as its notes always claimed. Re-run: winner unchanged (80°, the
ranking was never affected — the MC multiplier was angle-independent),
headline now 1327 Pa, matching the recomputation to display rounding.
The waveform-derived weights were verified analytic: (0.25, 0.50, 0.25),
summing to 1.

### Race (race_study)

Fresh headless run, seed 11, every evaluation a real solve
(`reuse_prior=False` in the race lanes). Per-solve wall seconds were captured
from the lanes' `_TimedSolver` instances:

- MC lane: 88 solves, Σ = 461.9 s × 4 OpenMP threads / 60 = **30.79** core-min
  (reported 30.79). Peak L/D 18.12 ± 0.06 at 0°.
- ROM lane: 5 solves (4 anchors + 1 confirm), Σ = 29.2 s × 4 / 60 = **1.95**
  core-min (reported 1.95). Peak L/D 18.14 at 0°.
- Speedup 30.79/1.95 = 15.79 → **15.8×** (reported 15.8×). Note the speedup is
  a measured quantity and varies run to run with solve times; the arithmetic
  is what this audit certifies.
- Agreement: 100·|18.12 − 18.14|/18.12 = 0.11% → **0.1%** (reported 0.1%).
  ("Agree to X%" reports the discrepancy X, i.e. smaller is better.)

### B-52 (geometry_study, unfamiliar body)

Fresh headless run (velocity 100 m/s, refinement 3, 50 m reference length,
300 iterations, warm mesh from cache, solve live, 399 s wall). Checks 8–10
pass exactly: Cd/Cl are the final-20%-window means of `coefficient.dat`
(60 of 300 rows), mesh numbers are verbatim from `log.checkMesh`, and the
headline CI 0.003 is RSS(settling 1.286e-05, stored refinement band 0.00303).

### NACA 4412 (geometry_study, curriculum body with experimental reference)

Fresh headless run (curriculum hints: velocity 15 m/s → Re_c ≈ 1e6,
chord-first). simpleFoam hit its residual controls and reported "SIMPLE
solution converged in 120 iterations" inside the 300-iteration budget, so the
history has 120 rows and the reported window ("final 24 iterations") matches
the actual history — the plan line quotes the budget, the result quotes the
run; no number is misstated.

- Cd 0.01892 ± 1.9e-05 = the recomputed final-window statistics of
  `coefficient.dat` (0.0189223 ± 1.852e-05 over 24 rows). Lift 0.2689 ±
  0.0002 likewise (0.268923 ± 0.0002013). Mesh verbatim from `log.checkMesh`.
- Reference-band arithmetic: the reference is planform-based
  (`area_basis: planform`), so no rebasing applies (`_rebase` verified to
  pass the measured value through). Relative error
  |0.0189223 − 0.030| / 0.030 = 0.36926, reported 0.3693 — computed from the
  unrounded window mean, correct. 0.3693 ≤ tolerance 0.40 → inside the band →
  tier VALIDATED with reason "within 37% … (band ±40%)". Both percentages are
  display-roundings of the exact values; the comparison itself is done
  unrounded. Boundary behaviour checked synthetically: a value 40.3% out
  (Cd 0.0421) correctly fails the band.

## Code fixes made during this audit

1. `sdk/workflows/valve_study.py` — headline objective changed from the MC
   envelope mean to the deterministic cycle-weighted sum of the emitted phase
   losses (check 11). The MC envelope still supplies the ±band.
2. (From the same session, Part 1 bug) `sdk/chief_engineer/vspaero.py` — the
   result-reuse path now validates a prior `result.json` carries everything a
   caller consumes (polar CLtot/CDi/CDo arrays of equal length with finite
   values, matched alpha/cdi/cdo_wing/extrapolated, matched cl equal to the
   design's `cl_target`, stl) before returning it, else the wing re-solves;
   a stale `result.json` is deleted before the worker launches so a dead
   worker can never resurrect it. `sdk/workflows/aircraft_optimization.py` —
   finalist processing treats a result without a usable `matched`/`polar` as
   unsolved instead of raising.
