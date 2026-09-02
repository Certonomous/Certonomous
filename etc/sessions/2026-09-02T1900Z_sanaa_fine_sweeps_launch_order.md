# SANAA-DIRECT — launch fine-grid sweeps now; then (Ma,AoA) both; queue-durable; parallel; lift fixed (2026-09-02, ~19:00Z)

## Sanaa's words, verbatim

> 1. dafoam team launches the 0-18 with fine grid for both now. Once that
> is launched, DAFOAM launches (Ma,AoA) sweep for both with fine as well.
> These runs must either be launched or queued, such that even if the fleet
> dies, they still run. A few things: They need to run in parallel (which i
> guess is obvious but stating it still). well look atthe results once both
> cases conclude. Also, for all of these cases, lift must be kept fixed.
>
> [Battery: caption dedupe — same message earlier block, already captured
> 1730Z; this file carries only the sweep order.]

## Context (chief's reading, not her words)

- Explicit exception to the demo freeze for these dafoam runs, by her order.
- Item 1: A1WR stages 1-2 (fine-grid 0-18 deg, both solvers) launch NOW,
  through the queue-daemon path (OS daemon survives fleet death — her
  detached-queue ruling) or an equivalently durable detached launch. Runs
  within each sweep parallelised.
- Item 2: after item 1 is launched, an (Ma, AoA) sweep at fine grid, "for
  both", queued the same durable way. NEW pre-registration required (rule
  2: frozen + costed before compute).
- "Lift must be kept fixed" — READING TO CONFIRM WITH HER BEFORE FREEZE
  (pre-compute amendments legal): at each operating point the wing is
  TRIMMED to hold the lab's fixed CL target, so the (Ma) sweep reports the
  trim angle and drag at fixed lift; a free two-axis (Ma x AoA) grid with
  lift also fixed is overdetermined. The lane drafts the prereg stating
  this interpretation; her correction lands as a pre-compute amendment.
  The plain 0-18 alpha polars (A1WR) inherently sweep lift; the fixed-lift
  clause is read as binding the (Ma,AoA) item and any optimization use of
  these results — flagged to her explicitly.
