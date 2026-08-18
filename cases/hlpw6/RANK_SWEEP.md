# HLPW6 test case 1: the rank sweep, on the real grid

Second pass over `hlpw6-testcase1-coarse-grid-entry`, 2026-08-01 04:51Z to
05:07Z. Corrects one number in `FEASIBILITY_PROBE.md` section 6 and adds the
measurement that number was standing in for.

Raw rows: `rank_sweep.jsonl` in this directory (also in `measurements.jsonl`);
driver `rank_sweep.sh`; solver logs
`/home/ubuntu/certonomous-runs/hlpw6-memory-probe/logs/HLPW6_ranksweep_np*.log`.

---

## What was wrong

`FEASIBILITY_PROBE.md` section 6 prices the rank sensitivity of this item from
the **structured proxy ladder**, not from the workshop grid:

> | ranks | s per iteration | core-min per iteration | relative |
> | 1 | 13.37 | 0.223 | 1.00 |
> | 14 | 2.13 | 0.498 | 2.23 |
>
> Fourteen ranks buys 6.3x the wall speed for 2.23x the core-minutes...
> Parallel efficiency is about 45%.

and from that concludes the item could be had for **4,014 core-min serial over
67 hours of wall time**. That was a reasonable inference from the data then in
hand, and it is wrong. Both the efficiency figure and the recommendation to run
it serially are artifacts of the proxy.

## The measurement

Same case, same hardened configuration, same 40 SIMPLE iterations, alpha 10,
the real 2,661,338-cell committee grid, one rank count at a time on an
otherwise quiet box:

| ranks | wall s | s/iteration | core-min/iteration | wall speedup | parallel eff. | peak RSS MiB |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 632.50 | 15.812 | 0.2635 | 1.00 | — | 3,292 |
| **4** | **134.40** | **3.360** | **0.2240** | **4.71** | **118%** | **3,889** |
| 8 | 75.12 | 1.878 | 0.2504 | 8.42 | 105% | 4,034 |
| 14 | 59.58 | 1.490 | 0.3476 | 10.62 | 76% | 4,411 |

Two things fall out, and they point the opposite way to the proxy.

**Parallel efficiency at 14 ranks is 76%, not 45%.** The proxy is a structured
hex mesh with 3.06 faces per cell and near-perfect memory locality; the
workshop grid is unstructured with 2.446 faces per cell and scattered
addressing, so it is far more latency-bound per cell and far less
bandwidth-bound. It parallelises better, not worse. Measuring scaling on a
convenient mesh and applying it to the real one is the same class of error as
measuring memory on one point and extrapolating.

**Serial is the worst option available, not the cheapest.** Four ranks is
**15% cheaper in core-minutes than one rank and 4.71 times faster in wall
time** — a superlinear 118%, which is the working set per rank dropping into
cache. The core-minute optimum is at 4 ranks and the curve is shallow through
8; only past 8 does the charge start climbing steeply.

> The recommendation to run this item serially would have cost **more**
> core-minutes and **79 hours** of wall time to save nothing.

## What the item costs, by how it is scheduled

Carrying the docket's own assumption of 3,000 iterations per angle across six
angles, 18,000 iterations:

| configuration | core-min | wall time | vs filed 3,600 |
|---|---:|---:|---|
| 1 rank | 4,743 | 79.1 h | 1.32x |
| **4 ranks — core-minute optimum** | **4,032** | **16.8 h** | **1.12x** |
| 8 ranks | 4,507 | 9.4 h | 1.25x |
| 14 ranks | 6,257 | 7.4 h | 1.74x |

The docket carries **6,390**, from the 120-iteration run at 14 ranks. That
figure is measured and it is kept, because it is the conservative end and
because the iteration count above it is still an assumption. But the spread in
this table is the point:

> **The same item is 4,032 or 6,390 core-minutes depending on nothing but the
> rank count, a 1.58x range with no physics in it at all.** More than half the
> gap between the filed estimate and the corrected one is a scheduling choice,
> not a mispricing.

At 4 ranks the filed 3,600 was only 1.12x low. The docket's estimate was not
badly wrong about the work; the lab was about to run it in the most expensive
way available.

## Consequences

1. **Run this item at 4 ranks, not 14 and not serially.** 4,032 core-min and
   16.8 hours of wall time, against 6,257 and 7.4 hours. On a box whose
   measured sustained occupancy is 1.40 of 14 cores, wall time is not the
   scarce thing.
2. **Three or four of these can run at once.** Four ranks and 3.9 GiB each
   means the box holds three concurrent angles inside 12 GiB with cores to
   spare — which turns six angles into two passes of 8.4 hours rather than one
   serial queue.
3. **The charter's core-minute is a scheduling metric, not a work metric, and
   nothing in the docket says so.** Every estimate on it that quotes core-min
   without quoting a rank count is under-specified by up to 1.58x on this
   evidence. That is a docket-wide finding, not an HLPW6 one.
4. **Scaling measured on a proxy mesh does not transfer.** It was wrong here by
   31 efficiency points and it pointed at the opposite conclusion.

## What this does not change

Memory: unchanged, and still not the wall. Peak across the sweep is 4,411 MiB
at 14 ranks and 3,292 MiB serial, against 30.6 GiB of host.

The iteration count: still nobody's measurement, still the live uncertainty,
still the reason this item is not bounded until one angle is run to its own
convergence.
