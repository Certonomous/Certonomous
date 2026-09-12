# A3GC — the registered triple is NOT deliverable under the time constraint

**[lab-attributed] dafoam-supervisor ruling, 2026-09-12T03:0xZ.**
Measured by the supervisor personally from the running and completed logs. Short by
instruction ([SANAA-DIRECT] 2026-09-12T02:5xZ: no reporting, solve and fix).

## The three levels, as they actually stand

| level | cells | ranks | state | number |
|---|---|---|---|---|
| L3 | 99,840 | 4 | complete rc=0, `End`, last `Time = 6000` == endTime | **NOT A RESULT** (committed `39e299af8`) — p initRes 2.290019532e-05, dead flat, 22.9x above the registered Sec.3.6 accept floor 1e-06 |
| L2 | 798,720 | 8 | RUNNING, `Time = 700` of 6000 at 02:48Z | CD 0.02236925, CL 0.31353679, p initRes 9.887e-04 still descending |
| L1 | 6,389,760 (target) | — | stage 1 mesh generation running; **primal NOT AUTHORISED** | four conditions registered in `5a05eda76` |

## The measurement that settles it

`A3GC-L2/primal.log` `ExecutionTime`/`ClockTime` pairs, steps 100→700:
mean **8.06 s/step** wall; the last 100-step block took **1734 s = 17.3 s/step**,
a ~3x slowdown from box contention (load 35–50, cfd and heat-transfer solving
alongside; ranks measured at ~54% CPU, and `ExecutionTime/ClockTime` = 0.587 is
that contention read directly off the solver's own two clocks).

- **L2 landing band: 12 h to 25 h from 02:48Z** — 2026-09-12T15:00Z at the mean
  rate, 2026-09-13T04:00Z at the recent rate. The spread is contention, not physics.
- **L2 vs L3 cost:** L3 0.0733 s/step (np=4), L2 4.877 s/step (np=8) — **66.5x for
  8x the cells on 2x the ranks.** Explained, not anomalous: L2's pressure GAMG runs
  13–17 iterations per step against L3's 2. The pressure solve is doing real work,
  which is consistent with L2 genuinely converging rather than stalling.
- **L1 primal at np=8, 8x L2's cells at the SAME rank count:**
  - optimistic (cost strictly O(N), GAMG iteration count saturates): 39 s/step → **2.7 days**
  - conservative (the measured 66.5x re-scaled for the lost 2x in ranks): 649 s/step → **45 days**
  - **Band 2.7 to 45 days. Every point in that band is outside the time constraint.**
    The conclusion does not depend on resolving the scaling exponent, which is why
    it is stated without first resolving it.

## Ruling

**The A3GC registered L1/L2/L3 Roache triple cannot be completed this week.** L3 is
NOT A RESULT on its own registered floor and L1's primal is weeks of np=8 compute.
Stated now, at hour 2 of L2, rather than discovered at hour 19.

**Nothing is stopped.** L2 runs to endTime; L1 stage 1 runs to completion — it costs
one core of sixteen, the mesh is a durable artifact, and Sanaa's 2026-09-11 NO-CAP
ruling means nothing dafoam owns kills on spend or clock. Killing either would
destroy work and buy nothing.

**endTime 6000 cannot be shortened.** It is registered (Sec.4.1 anchor / Sec.5 cost
basis) and standing rule 4 requires last time == endTime. A post-compute change is a
gate change and is not available to me — the gates closed at A3GC's first compute and
I put that on the record myself (AMENDMENT 6, `732a7a51e`) at a moment when it cost me
something to say it.

**Adding a fourth level and choosing the best three post hoc is REFUSED.** It moves no
threshold on its face and is still gate-fitting: the triple's composition IS the
gating structure under standing rule 5.

## What is done instead — the lawful fast route

**A successor registration, A3GC-R2, frozen before any compute.** A new registration
with a fresh freeze moves no gate on A3GC and is the standard route:

1. levels sized from the **MEASURED** L2 rate, not the estimator that missed L2 by ~19x;
2. `endTime` justified by the plateau step measured from L3's and L2's own histories,
   instead of an anchor carried over untested;
3. the residual accept floor set from what the solver demonstrably reaches on this
   geometry, with the proxy argument of `5a05eda76` made properly in the document
   rather than argued after a failure — including its counter, N-D45 in converse
   form: a flat CD history proves the INTEGRAL is stationary, not that the FIELD is
   converged, and CD/CL are surface integrals of pressure while the equation sitting
   above its floor IS p. A successor must RESOLVE field convergence, not inherit the argument;
4. a cost that fits the week, stated in core-minutes before the freeze.

Gated on two measurements already in flight: the L3 p-stall triage (if the stall is
mesh-quality-linked, regeneration costs ~9 core-min — L3 stage 1 measured rc=0,
410 wall s — and a clean coarse level is then nearly free), and L2's landing.

**This goes to the chief tonight**, because it changes the team's direction and the
owner is working to a time constraint she stated in her own words.
