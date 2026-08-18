# C4 — TMR NACA 0012 closure attempt: time-accurate averaging is not affordable inside the scoped budget

Night-queue item C4. Full figures in `demo-output/website/tmr/C4_naca0012_closure.json`.
Source case state: `demo-output/website/tmr/naca0012_status.json` (untouched by this
session -- its measured block is not re-derived or overwritten). Scoping proposal:
`demo-output/website/agenda/proposals/tmr-naca0012-complete-ladders.json`.

**Budget note.** This work is owner-approved. The spend cap itself cannot be
verified from this instance -- no IAM role, no AWS credentials, no CLI (see
`demo-output/website/agenda/BLOCKERS.md`, item B-1). Nothing below implies the
spend was checked against a limit; the actual core-minutes are reported
precisely because that is the number that matters.

---

## Headline: the ~480 core-minute estimate is short by 1-3 orders of magnitude, for ONE rung

| Quantity | Value |
| --- | --- |
| Proposal estimate (whole ladder: 225x65 and 449x129 at alpha 10, then alpha 0 and 15) | 480 core-minutes |
| Core-minutes needed for medium/alpha10 to reach 30 convective units (already shown insufficient on the coarse rung) | **11,700 - 30,300** |
| Core-minutes needed for medium/alpha10 to reach "hundreds of convective units" (the proposal's own stated requirement) | **~117,000 - 303,000** |
| Actual core-minutes spent this session | **5.0** |
| Actual core-minutes spent in the prior (2026-07-26) session on the same (grid, alpha) pair | 419.4 |

The estimate did not hold. It is not close.

## What ran this session

One bounded, foreground, single-rank confirmatory burst (well under the 4-rank
cap):

- Medium rung (TMR 225x65 grid, 14,336 cells: (225-1)x(65-1), the same
  node-to-cell arithmetic that reproduces the coarse rung's own measured 3,584
  cells), alpha 10, pimpleFoam, cold start, maxCo 1.5, adjustTimeStep yes.
- Reused the already-staged mesh/fields/dictionaries from a 2026-07-26 case
  (`~/certonomous-runs/tmr-naca-t-a10-medium`) to avoid redundant meshing
  cost, reset to t=0, ran under `timeout 300`.
- **Result: 300 s wall (5.0 core-minutes, 1 rank) reached Time = 0.0049518293
  convective units in 165 steps.** deltaT grew from 4.06e-7 at the impulsive
  start and plateaued (not still shrinking) around 3.7e-5, with Courant
  pinned at the 1.5 ceiling.
- Rate: 9.90e-4 convective units per core-minute.

## Prior-session evidence, cited not re-run

Two 2026-07-26 attempts on the exact same (medium, alpha 10) pair, already on
disk, checked but not repeated:

- **Cold start** (`~/certonomous-runs/tmr-naca-t-a10-medium/log.pimpleFoam`):
  ExecutionTime 21,568.94 s = **359.5 core-minutes**, reached Time =
  0.9254526 units. Rate 4.29e-5 units/s, same order as this session's fresh
  measurement -- independent confirmation, not a fluke.
- **Seeded from the developed steady field**, maxCo raised to 5.0
  (`~/certonomous-runs/tmr-naca-t-a10-medium-seeded/log.pimpleFoam`):
  ExecutionTime 3,593.13 s = **59.9 core-minutes**, reached Time = 0.018
  units, Cl still reading ~1.42 (not converged). Slower than the cold start,
  not faster: the impulsive adjustment from the steady seed has not settled.
  Same failure mode already documented in `naca0012_status.json` for the
  coarse/alpha0 rung -- now confirmed on medium/alpha10 too.

## Stationarity gate: not reached, not a drift-fail

`halves_drift()` (the stationarity gate in `sdk/workflows/tmr_verification.py`,
~line 2733) was **not invoked** -- the run never approaches the averaging
window start (0.4 x end_time). There is no mean to check for drift. This is a
different, upstream failure mode from the coarse/alpha0 case already
documented (which DID reach a window and drifted 31.6% between halves). No
coefficient is quoted for the medium rung. None should be.

## Cause, not just symptom

1. **Courant-limited timestep collapse.** maxCo 1.5 forces deltaT to plateau
   at ~3.7e-5 on the medium grid, versus an effective ~0.041 units/step the
   coarse grid's own transient run achieved (30 units / 735 steps) -- about a
   1,100x smaller step. Combined with 4x the cell count per step, this
   produces the measured ~9,700x slower wall-clock rate per convective unit
   versus the coarse rung.
2. **Independent, measured mesh-quality cost.** checkMesh on this same
   converted mesh (`demo-output/website/tmr/runs/naca-a10-medium/log.checkMesh`)
   reports max aspect ratio 26,446,226.94 on 1,822 cells, 170 severely
   non-orthogonal faces (>70 degrees), and "Failed 1 mesh checks." Consistent
   with that, the confirmatory log shows the pressure PCG solve repeatedly
   hitting its 1,000-iteration cap without full convergence ("No Iterations
   1000" on both p and pFinal). Each of the already-too-few affordable
   timesteps is itself expensive.
3. **Seeding does not rescue it.** The steady-field seed crawls slower than
   cold start (5.0e-6 vs 4.3e-5 units/s), working through an impulsive
   adjustment shock rather than skipping it.

MPI parallelism would not close this gap either: the constraint is timestep
**count** under a geometry-set Courant limit, not per-step throughput.
Adding ranks (even within the 4-rank cap) raises core-minute cost without
cutting the number of steps needed.

## Fine rung: not attempted, 0 core-minutes

Fine (449x129, 57,344 cells) is the next TMR family doubling, with finer
near-wall and leading-edge spacing that would only compound the collapse
already measured on medium. Extrapolating the coarse-to-medium trend, a fine
attempt is certain to be less affordable than medium's already 24x-630x
over-budget result. Spending foreground core-minutes to confirm a near-certain
outcome was judged not worthwhile. This is a documented, reasoned stop.

## Per-rung summary

| Rung | Grid | Status | Coefficients | vs CFL3D | Core-min (this session) |
| --- | --- | --- | --- | --- | --- |
| Coarse | 113x33, 3,584 cells | Measured (established, untouched) | cl 1.1164357439, cd 0.0044948532678 | No claim made; single coarse rung, no convergence claim per existing status.json | 0 |
| Medium | 225x65, 14,336 cells | Attempted, not affordable, documented and stopped | None quotable (0.005 convective units reached) | None computed | 5.0 |
| Fine | 449x129, 57,344 cells | Not attempted | n/a | n/a | 0 |

**Total actual core-minutes this session: 5.0.**
**Total actual core-minutes across both sessions on this blocker: 424.4** (5.0
this session + 359.5 + 59.9 prior), already 88% of the entire 480-minute
estimate, spent on less than 1 convective unit combined, on one rung.

## The lesson

The coarse rung is still the only trustworthy NACA 0012 number this project
has. The medium/fine blocker (an undecaying wake oscillation under the steady
solver) is real, but the proposed fix -- a time-accurate solve with averaged
coefficients inside a 480-core-minute budget -- is not viable: the honest,
now twice-independently-measured rate says that budget is short by 1-3 orders
of magnitude for a single (grid, alpha) pair. Closing this needs either a
materially cheaper numerical approach (a fixed, larger implicit step with its
own stability study rather than an adaptive Courant-limited one, or a
compressible/preconditioned solver closer to CFL3D's own numerics) or an
honest budget reset that names tens of thousands of core-minutes per rung, not
hundreds. Proposing either is future scoping work, not this session's job;
this session's job was to get a trustworthy number or stop honestly, and it
stopped honestly.
