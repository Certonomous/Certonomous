# Monte-Carlo convergence panel: the numbers and their sources

Website line served: orders of magnitude fewer runs, backed by theoretical
guarantees. Every number below is read from the race act's recorded
artifacts; nothing is synthesized.

## Headline numbers

| quantity | value | source |
|---|---|---|
| Monte-Carlo solver runs | 88 | mission-output/race-study/work/mc/mc-s0a0 .. mc-s7a10 (result.json, one per run) |
| reduced-order solver runs | 5 | mission-output/race-study/work/rom (4 anchors + 1 confirmation, result.json each) |
| peak L/D, ensemble mean | 18.11 | mean of the 8 per-sample peaks below |
| peak L/D, reduced-order confirmed | 18.14 at alpha 0 | work/rom/rom-confirm/result.json |
| ensemble 95% band at 88 runs | +-0.060 (published +-0.06) | 2 x stdev / sqrt(8) over the per-sample peaks; certificate C-2026-2960 |
| reduced-order envelope | +-0.084 | recorded confirmation 18.1407 vs surface prediction 18.2247 from the 4 recorded anchors; certificate says residual 0.084 |
| measured speedup, solver time | 14.8x | 422.3 s over 88 runs vs 28.6 s over 5 runs (elapsed_s in every result.json); certificate says 14.8x core-minutes |
| measured cost per run | 4.80 s | mean elapsed_s over the 88 ensemble records |
| fitted convergence slope | -0.500 | log-log fit over the root mean square curve, N = 22..88; guarantee is -1/2 |
| ensemble standard deviation | 0.0853 | stdev of the 8 per-sample peaks; anchors the guarantee line |

Per-sample peaks (L/D, samples s0..s7): 18.1407, 18.2037, 18.1367, 18.0870, 18.0130, 18.2332, 18.0936, 17.9870.
Every sample peaked at alpha 0, so each peak is that sample's recorded
alpha-0 run.

## The convergence table (resampled over 20000 member orderings)

One ensemble member costs 11 solver runs (a full angle sweep
locates its peak), so the sequential band updates every 11
runs. Root mean square is the primary curve: the prefix sample variance is
an unbiased estimate of the full-ensemble variance, so its square root per
member count is the estimator's true error scale. The median of a 2-to-7
member standard deviation is biased and noisy, which is why the median
column wanders around the guarantee instead of tracking it (slope of the
median curve: -0.341).

| members m | solver runs N | half-width, rms | half-width, median | middle 50% | guarantee 2s*sqrt(11/N) |
|---|---|---|---|---|---|
| 2 | 22 | 0.1206 | 0.1000 | 0.0497..0.1462 | 0.1206 |
| 3 | 33 | 0.0987 | 0.0890 | 0.0676..0.1275 | 0.0985 |
| 4 | 44 | 0.0855 | 0.0885 | 0.0654..0.1016 | 0.0853 |
| 5 | 55 | 0.0763 | 0.0794 | 0.0631..0.0870 | 0.0763 |
| 6 | 66 | 0.0697 | 0.0711 | 0.0649..0.0742 | 0.0696 |
| 7 | 77 | 0.0645 | 0.0690 | 0.0615..0.0692 | 0.0645 |
| 8 | 88 | 0.0603 | 0.0603 | 0.0603..0.0603 | 0.0603 |

## The reduced-order model's own convergence (drawn on the figure)

Anchor run order comes from the recorded dispatch times (job.json mtime
under mission-output/race-study/work/rom): alpha 0, 3.3, 6.7, 10, then the
confirmation at the located peak. With k anchors fitted, the model's error
is measured against the next recorded run; the final run confirms the
envelope. No 2-run point exists (a quadratic needs three anchors), so the
curve starts at 3 runs. Every value is a recorded solver result.

| solver runs | model error | measured against |
|---|---|---|
| 3 | 1.6217 | next recorded anchor (alpha 10) |
| 4 | 0.0840 | confirmation at the located peak (alpha 0) |
| 5 | 0.0840 | confirmation run lands, envelope confirmed (alpha 0) |

## Check verdicts

- PASS: convergence slope matches the 1 over sqrt N guarantee. fitted slope -0.5001 on the root mean square curve over N = 22..88, guarantee -0.5, tolerance 0.05
- PASS: N = 88 half-width reproduces the act's published band. recomputed +-0.0603; certificate C-2026-2960 publishes +-0.06 (95 percent) with input channel 0.060. The +-0.07 band belongs to the earlier race-benchmark passes (demo-output/website/race/benchmarks.md), not this act.
- PASS: reduced-order envelope comes from its recorded runs. quadratic through the 4 recorded anchors peaks at alpha 0, predicts 18.2247, recorded confirmation 18.1407, residual 0.0840; certificate says 0.084
- PASS: measured speedup reproduces the act's 14.8x. recorded solver time 422.3 s over 88 runs vs 28.6 s over 5 runs = 14.79x; certificate says 14.8x core-minutes
- PASS: per-run wall cost matches the stated 4.80 s. mean recorded elapsed over the 88 ensemble runs 4.799 s per solver run
- PASS: reduced-order convergence curve traced to its recorded runs. run order from recorded dispatch times: alphas [0.0, 3.3, 6.7, 10.0]; 3-run model tested at the next recorded run (alpha 10) misses by 1.6217, 4-run model tested by the confirmation misses by 0.0840, envelope confirmed +-0.084 at 5 runs; certificate says 0.084. No 2-run point exists (a quadratic needs 3), so the curve starts at 3.

## Provenance note on the published band

The race act's own certificate (mission-output/race-study/certificate.pdf,
C-2026-2960, issued 2026-07-26T02:01:54Z) publishes peak L/D 18.14 +- 0.06
at 95 percent with input channel 0.060, speedup 14.8x core-minutes, 88 + 5
solver runs. The +-0.07 band circulating with the value 18.14 belongs to
the earlier race-benchmark passes (demo-output/website/race/benchmarks.md:
pass1 18.10 +- 0.07, pass2 18.20 +- 0.07); this panel reproduces the race
act's records exactly, so it carries +-0.06.
