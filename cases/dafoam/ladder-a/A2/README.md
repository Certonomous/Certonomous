# Ladder A2 — MACH Tutorial Wing, aero-only variant

The **frozen record of this case** is `../A2_mach_tutorial_wing.md` (2026-07-28) with
`../A2_mach_tutorial_wing.json`, the extracted optimiser history `../A2_optimization_history.json`,
and the shape-frame dump `../A2_shape_frames.json`. The case is 38,304 cells, `DARhoSimpleFoam`,
run from `runScript_AeroOnly.py` (a disclosed deviation from the tutorial's headline aerostructural
script). **There is no `logs_A2/` directory in this tree** — unlike A1/A3/A4/A5/A6, A2's logs were
never copied into the ladder; they live at `/home/ubuntu/certonomous-runs/A2-mach-wing/` (published
grading, optimiser history) and `/home/ubuntu/certonomous-runs/W4-a2-provenance/` (the 2026-08-02
stock-vs-patched re-measurement). The regrade record is `../W5_GRADIENT_REGRADE.md` §3/§3a/§3b —
note that §3a's headline ("A2 could not be regraded") is **RETRACTED in place** because those runs
invoked the wrong script. **Nothing in this subdirectory edits any frozen file.**
