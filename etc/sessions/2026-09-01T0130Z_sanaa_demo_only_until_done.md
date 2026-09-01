# SANAA-DIRECT — everything non-demo waits until the demos are done (2026-09-01, ~01:30Z)

Captured verbatim from the chief session, minutes after the closure/ansys
stand-down (c5edce6b). This widens that ruling lab-wide.

## Sanaa's words, verbatim

> anything not demo related waits until we are done with the demo

## Context (chief's reading, not her words)

- **Lab-wide priority freeze: demo work only**, until the demo catalogue is
  done. The demo catalogue in flight: thermal GUI capability (screens
  A1–A9/C1–C9), jet-flap display mission, Act D package, scope-down product
  logic, the coordinated GUI restart, and the two new products (transonic
  ONERA M6-class Mach 0.84 wing, double Mach reflection — b0bc866c).
- Operationally, for the active teams (cfd, heat-transfer, dafoam,
  verification): no non-demo dispatches, no non-demo queue entries, no
  non-demo launches, no non-demo drafting. In-flight non-demo work is parked
  cleanly (nothing half-committed), not cancelled.
- Verification's role narrows to demo support (audits of demo-carrying
  instruments and R5/honesty compliance), not its wider board.
- No solvers were running at capture time (live reading 01:20Z), so nothing
  in-flight needs killing; the queue daemon stays up but only demo-related
  entries are filed while this holds.
- Boards stay current; parked is not cancelled. Lifting is Sanaa's call.
