# SANAA-DIRECT — waiting on thermal + jet GUI capabilities (2026-09-01, ~02:00Z)

Captured verbatim from the chief session. Follows the Act B STOP order
(`2026-08-31 …_sanaa_actB_stop.md`, commit d8ddfe62) and the THERMAL ACTS full
specification (commit a3793b8f).

## Sanaa's words, verbatim

> fantastic. Then in this case I am waiting for all the heat transfer
> capabiltiies to be added to the GUI alongside the Jet one as well.

## Context (chief's reading, not her words)

- "the Jet one" = the jet-flap display mission presenting the real JF1 run tree
  (2D section, slot as jet inlet, Cμ sweep, y+≤1, 20k-iteration solutions, real
  mesh slice, Cp-vs-x/c, CL vs Cμ with the Williams–Butler–Wood line), per her
  Act B STOP order. Achievability report due to her by 09:00Z.
- "all the heat transfer capabilities" = the thermal display mission per her
  THERMAL ACTS full specification: screens A1–A9 (motor-in-duct, Act A) and
  C1–C9 (battery module, Act C), presented from landed runs.
- Both go live in ONE coordinated server restart (must carry
  `CHIEF_ADAPTER=openfoam OPENFOAM_RUN_PREFIX=openfoam2606
  CERTONOMOUS_SOLVE_RANKS=16`). No partial restarts while she is in the GUI.
- She is in waiting mode: ping her the moment either capability is live.

Routing: heat-transfer (thermal mission build, already assigned under Option 2),
cfd + GUI-edits lane (jet-flap mission + scope-down product logic).
