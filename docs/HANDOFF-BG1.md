# HANDOFF — BG-1 (race benchmark, feat/race-benchmark)

## Status: DONE — both passes measured, all assets committed

Subject corrected mid-night per orchestrator: **NACA 4412 finite wing**
(curriculum body: chord 1 m, span 3 m, Re_c 1e6), not the cylinder.

## Measured results (real VSPAERO solves, every point)

| pass | full MC (88 solves) | reduced-order (5 solves) | speedup (core-min) |
|---|---|---|---|
| pass1 | peak L/D 18.10 ± 0.07 @ 0°, 45.4 core-min, wall 116 s | 18.14 @ 0°, 2.1 core-min, wall 32 s | **21.5×** |
| pass2 | peak L/D 18.20 ± 0.07 @ 0°, 60.8 core-min, wall 153 s | 18.14 @ 0°, 2.0 core-min, wall 31 s | **29.8×** |

The two paths agree to 0.2% — "same answer, certified" is the honest story.
Load context recorded per pass in benchmarks.md (the box was heavily shared:
load 9–13, mega-batch + acts running). Headline = pass1.

**For the website N2 speed-benchmark panel (website agent, from my measured
runs only): full MC 45.4 core-min · reduced 2.1 core-min · speedup 21.5×.**
Core-minutes = solve wall-time × 4 solver OpenMP threads (stated on the card).

## Assets (committed on feat/race-benchmark)

- `demo-output/website/race/pass{1,2}/` — polar_LD.png (publication style,
  mathtext, peak annotated), race_candidates.png, speedup_card.png,
  mc_{start,mid,finish}.png + rom_{start,mid,finish}.png (split-screen
  staging stills), race.json (full per-solve data incl. per-solve seconds).
- `demo-output/website/race/benchmarks.md` — full table, both passes,
  envelope-semantics note, time-compression labeling rule.
- Harness: `sdk/workflows/race_benchmark.py` (+ tests, CI-safe).

## Two shared-file edits the orchestrator must carry at merge

1. `sdk/chief_engineer/vspaero.py` — **real bug fixed**: the case tag only
   used span/area/sweep, so any parallel batch of same-planform designs
   (differing alpha/Re) clobbered ONE case directory → garbage results.
   Tag now includes alpha/Re/camber and accepts `tag_hint`. The aircraft
   act's finalists differ in span/area so they never tripped it, but this
   fix matters for anything sweeping alpha in parallel. MERGE THIS FIRST.
2. `sdk/chief_engineer/vspaero_worker.py` — additive: optional four-series
   airfoil keys (camber/camber_loc/thick_chord) + single-alpha direct-solve
   mode (`alpha_npts=1` → no interpolated cruise point, `matched: null`).

## Notes / non-blocking

- Peak sits at the α=0 boundary of the swept range (physically right for a
  cambered AR-3 wing: induced drag dominates fast). If the video wants an
  interior peak, sweep from −4°: one-line change (`ALPHAS`), ~2 min rerun.
- Split-screen video assembly (actual screen recording) needs a human or
  the website agent's pipeline; my stills + per-solve timings in race.json
  are sufficient to cut the ~45–60 s "Speed, certified" video with labeled
  time-compression.
- One transient VSPAERO failure observed pre-fix (empty result.json under
  directory clobbering); zero failures post-fix with per-design isolation
  plus one-retry.
- v3-N5: no GUI missions were needed for these assets; if live-GUI race
  captures are wanted, both missions will show SOLVER / VSPAERO as intended.
