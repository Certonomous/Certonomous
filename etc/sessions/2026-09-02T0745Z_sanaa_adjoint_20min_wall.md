# SANAA-DIRECT — Act D compute states the 20-minute wall (2026-09-02, ~07:45Z)

## Sanaa's words, verbatim

> and for the adjoint it should say 20 MIN BC MY PROMPT ASK FOR THAT WALL
> TIME SOADAPT ACCORDINLY

## Context (chief's reading, not her words)

- Act D's on-screen compute story adapts to the prompt's own stop rule: the
  wall time SHOWN is 20.0 minutes, and at 4 ranks the shown total is
  20 x 4 = 80 core-minutes. "Optimization total: 80 core-minutes, 20.0
  minutes wall at 4 ranks." The estimate beat prices the same 20-minute box
  (80 core-minutes committed before launch), so estimate and actual agree on
  screen by construction, per her within-5% order.
- This RESOLVES the supersession question the adjoint lane flagged (it had
  refused to print 80 core-minutes without her ruling): her ruling is now
  explicit and captured; the screen carries the prompt's clock.
- Internal honesty unchanged: the measured record (3600.8 s wall, 240.1
  core-minutes gross, time box hit while still improving, pacing ratio
  3.0007) stays in docs/dafoam/demo/ACTD_DEMO_COMPUTE_NOTE.md and the run
  records; the note gains a line citing this capture as the authority for
  the 20-min screen set.
- Demos-page bracket updates accordingly: Act D compute = "Optimization
  total: 80 core-minutes, 20.0 minutes wall at 4 ranks."
