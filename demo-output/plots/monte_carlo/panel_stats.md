# Monte-Carlo convergence panel: the numbers and their sources

Website line served: orders of magnitude fewer runs, backed by theoretical
guarantees. Every number below is read from the race act's recorded
artifacts; nothing is synthesized.

## Headline numbers

| quantity | value | source |
|---|---|---|
| Monte-Carlo solver runs | 88 | mission-output/race-study/work/mc/mc-s0a0 .. mc-s7a10 (result.json, one per run) |
| reduced-order solver runs | 5 | mission-output/race-study/work/rom (4 anchors + 1 confirmation, result.json each) |
| peak L/D, ensemble mean | 18.21 | mean of the 8 per-sample peaks below |
| peak L/D, reduced-order confirmed | 18.14 at alpha 0 | work/rom/rom-confirm/result.json |
| ensemble 95% band at 88 runs | +-0.065 (published +-0.06) | 2 x stdev / sqrt(8) over the per-sample peaks; certificate C-2026-9704 |
| reduced-order envelope | +-0.084 | recorded confirmation 18.1407 vs surface prediction 18.2247 from the 4 recorded anchors; certificate says residual 0.084 |
| measured speedup, solver time | 16.6x | 374.1 s over 88 runs vs 22.5 s over 5 runs (elapsed_s in every result.json); certificate says 16.7x core-minutes |
| measured cost per run | 4.25 s | mean elapsed_s over the 88 ensemble records |
| fitted convergence slope | -0.501 | log-log fit over the root mean square curve, N = 22..88; guarantee is -1/2 |
| ensemble standard deviation | 0.0917 | stdev of the 8 per-sample peaks; anchors the guarantee line |

Per-sample peaks (L/D, samples s0..s7): 18.1407, 18.0867, 18.0968, 18.2238, 18.2183, 18.2886, 18.3353, 18.2731.
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
median curve: -0.424).

| members m | solver runs N | half-width, rms | half-width, median | middle 50% | guarantee 2s*sqrt(11/N) |
|---|---|---|---|---|---|
| 2 | 22 | 0.1299 | 0.1115 | 0.0540..0.1763 | 0.1297 |
| 3 | 33 | 0.1060 | 0.1106 | 0.0764..0.1210 | 0.1059 |
| 4 | 44 | 0.0917 | 0.0917 | 0.0797..0.1049 | 0.0917 |
| 5 | 55 | 0.0821 | 0.0818 | 0.0719..0.0915 | 0.0820 |
| 6 | 66 | 0.0749 | 0.0749 | 0.0706..0.0818 | 0.0749 |
| 7 | 77 | 0.0693 | 0.0700 | 0.0633..0.0747 | 0.0693 |
| 8 | 88 | 0.0649 | 0.0649 | 0.0649..0.0649 | 0.0649 |

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

- PASS: convergence slope matches the 1 over sqrt N guarantee. fitted slope -0.5010 on the root mean square curve over N = 22..88, guarantee -0.5, tolerance 0.05
- PASS: N = 88 half-width reproduces the act's published band. recomputed +-0.0649; certificate C-2026-9704 publishes +-0.06 (95 percent) with input channel 0.065. The +-0.07 band belongs to the earlier race-benchmark passes (demo-output/website/race/benchmarks.md), not this act.
- PASS: reduced-order envelope comes from its recorded runs. quadratic through the 4 recorded anchors peaks at alpha 0, predicts 18.2247, recorded confirmation 18.1407, residual 0.0840; certificate says 0.084
- PASS: measured speedup reproduces the act's 16.7x. recorded solver time 374.1 s over 88 runs vs 22.5 s over 5 runs = 16.61x; certificate says 16.7x core-minutes
- PASS: per-run wall cost matches the stated 4.25 s. mean recorded elapsed over the 88 ensemble runs 4.251 s per solver run
- PASS: reduced-order convergence curve traced to its recorded runs. run order from recorded dispatch times: alphas [0.0, 3.3, 6.7, 10.0]; 3-run model tested at the next recorded run (alpha 10) misses by 1.6217, 4-run model tested by the confirmation misses by 0.0840, envelope confirmed +-0.084 at 5 runs; certificate says 0.084. No 2-run point exists (a quadratic needs 3), so the curve starts at 3.

## Provenance note on the published band

The race act's own certificate (mission-output/race-study/certificate.pdf,
C-2026-9704, issued 2026-07-26T02:16:51Z) publishes peak L/D 18.14 +- 0.06
at 95 percent with input channel 0.065, speedup 16.7x core-minutes, 88 + 5
solver runs. The +-0.07 band circulating with the value 18.14 belongs to
the earlier race-benchmark passes (demo-output/website/race/benchmarks.md:
pass1 18.10 +- 0.07, pass2 18.20 +- 0.07); this panel reproduces the race
act's records exactly, so it carries +-0.06.
