# SANAA-DIRECT — numbered list, battery 18-27 + cross-act 28-29 (2026-09-02, ~07:30Z)

Captured verbatim. Items 18-27 consolidate her 0650Z/0705Z battery batches
(already in THERMAL_ACTS_RESUME_NOTE.md); 28-29 are new.

## Sanaa's words, verbatim

> more on battery if i didnt say this already Battery
> 18. 28.7 °C (report) vs 27.8 °C (monitor endpoint) — resolve from
> fieldMinMax; one number everywhere.
> 19. Cell-to-cell spread reported as-computed (the prompt asks for it; the
> traces are on screen).
> 20. Peak wording: "occurs at t = 900 s; module has not settled within the
> record."
> 21. Uncertainty line split: single grid (no discretisation band) ≠
> sweep-check refusal (no certificate) — two separate sentences.
> 22. Units: °C everywhere (field caption says K).
> 23. Compute table, two rows (one per arm).
> 24. Mesh render: all seven channel bands visible + zoom inset (currently
> one band).
> 25. Two-arm overlay figure (10 vs 20 sweeps, 23.2 mK gap visible, pulse
> shaded).
> 26. Monitors: x-axis in seconds; pulse window shaded; figure-title dedupe.
> 27. Inlet/coolant temperature added to the set-by table.
>
> Cross-act
> 28. Shared figure-list dedupe fix actually deployed to every act.
> 29. Demos page brackets waiting on you/runs: motor compute cell, battery
> numbers or refusal-variant copy (say which), lattice objective row, Act D
> compute (item 13).

## Context (chief's reading, not her words)

- 18-27: match the resume-note queue; item 25 carries the lane's measured
  correction — the 23.2 mK gap is on the COOLANT OUTLET channel (23.15 mK),
  not the hottest-cell traces (<=1.31 mK), so the overlay is drawn on the
  outlet or it honestly shows coinciding cell traces.
- 28: the figure-list dedupe must be a SHARED fix verified deployed on all
  five acts, not per-act patches.
- 29: her demos page (where the videos go) has bracket placeholders to fill:
  motor compute cell (from landed records: 12 workers, 36.2 core-min/run
  mean, 578.8 plain-sum total, 86 min wall, two waves 30.5/39.2 min);
  battery = REFUSAL-VARIANT copy (chief's answer: the act's climax is the
  refusal; values appear as-computed beside it; the peak number follows the
  item-18 fieldMinMax resolution); Act D compute = "Optimization total:
  240.1 core-minutes, 60.0 minutes wall at 4 ranks"; "lattice objective
  row" = UNKNOWN to this session — no lattice act exists in the demo
  package; needs her clarification.
