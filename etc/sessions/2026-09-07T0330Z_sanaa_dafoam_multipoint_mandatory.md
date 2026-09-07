# Sanaa directive — 2026-09-07 ~03:30Z — DAFoam multipoint optimization is mandatory

Captured verbatim by dafoam-supervisor per board convention. HEAD at capture: d003edbb.

## Verbatim

> "yes and for the dafoam: we need to have the multipoint optimizations as well"

Multi-operating-point adjoint optimization is now a MANDATORY dafoam capability
alongside the single-point gradient sweeps.

## Chief's framing accepted with this directive (relayed to supervisor)

- Corrected state already delivered: SO-3 IS an incompressible multipoint
  optimization, landed PASS with an unconstrained-CL / lift-collapse caveat;
  compressible multipoint D6R = NOT A RESULT; A3/A6 are single-point only.
- Plan accepted: MP-A1 (SO-3 with per-point CL constraints, clean incompressible
  drag-min-at-fixed-lift) + D6R2 (A2 transonic multipoint, gated behind
  D6RF5 -> SO3DR Stage-2). Proceed under standing authorization +
  mandatory-completion.

## Physics-first sequence named by chief for this session

1. Freeze D6RF5 — completes supervisor check-1 read + sizing the three FD bands
   + the representative-DV choice; clears the D6RF4 §2ay flag and unblocks D6R2.
2. Draft MP-A1's costed pre-registration (clean incompressible multipoint
   milestone, demo-grade).
3. D6R2 chain (D6RF5 -> SO3DR Stage-2 -> D6R2); freeze D9successor and register
   SO3DR Stage-2.

Each registration's costed core-min figure is brought to the chief AS IT FREEZES,
BEFORE its compute. Report on every commit and every verdict.

## Binding context (this session's standing directives)

- 2026-09-04T0050Z: all assigned cases mandatory to completion; only exemption is
  a MEASURED capability gap filed on Sanaa's desk.
- 2026-09-06T2115Z / 2026-09-06T2145Z: fix-until-runs law, ENFORCED via
  scripts/check_completion_enforcement.py (§2ay); every GATE FAIL / NOT A RESULT /
  BLOCKED carries a dated fix-successor or a measured capability-gap filing.
- 2026-09-05T2130Z: pre-run checks bounded (3 cycles OR 24h) then
  launch-with-watcher. No infinite check loops.
