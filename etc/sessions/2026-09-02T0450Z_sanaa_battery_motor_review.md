# SANAA-DIRECT — battery/motor filming review + all-acts verification order (2026-09-02, ~04:50Z)

Captured verbatim from the chief session, during her filming review.

## Sanaa's words, verbatim

> also all runs should show the solver. I still see the battery one says no
> solver selected. All cases should say the solver no act says no solver
> selected. also for the battery Display-mode narration everywhere: "SOLVER /
> NONE ON THIS REQUEST," "no solver starts, no new number is produced," "the
> uploaded file is neither meshed nor solved," "screens come from the run
> that landed," and the whole "asked for and NOT AVAILABLE: A3/A4/A8/A9"
> table admitting the meshing walkthrough, feasibility beat, and assumptions
> box were never built. This act needs what JF1/Mach-10 got: live mesh on the
> uploaded STL, solving replay from logs, present tense, solver stated
> (chtMultiRegionSimpleFoam, k-ω SST).
> The battery cross-case text is STILL in the research agenda ("channels
> carry a convective coefficient… no outlet temperature") — third time
> flagged; the motor has a meshed fluid region, this sentence is from the
> battery configuration.
> Anchor table vs map table disagree on screen: anchors "expect" 38.1374 at
> 80 W/10 m/s (the old housing values) while the map now prints 39.2049
> (core). Both are fine internally — but the anchor table must be labeled
> "housing reader" or re-anchored on core values, or a reader will subtract
> the two and ask.
> Sig figs not applied: six decimals with an empty uncertainty column, and
> the "not available — single grid…" sentence repeated verbatim 16 times —
> print 0.1 °C and put the uncertainty statement once as a footnote row.
> Smaller: figure list still says "monitor, replayed" (banned word); the
> prompt is truncated mid-sentence ("…across" — finish it: "…across 80–305 W
> and 10–40 m/s against a 200 °C limit"); confidence 77% same question as
> JF1's 74%; and rotate the geometry render once to confirm the centerbody
> visibly runs the full duct length — in the screenshot it reads as a stub
> at the bottom. pls check all runs verify my requests above and conventions

## Context (chief's reading, not her words)

- The battery screen she saw is the LEGACY display scaffold (its old
  narration and NOT-AVAILABLE table), not the rebuilt battery-module act —
  the likely defect is ROUTING: her battery prompt still lands on the old
  path. Fix is to route it to the new act and retire/fence the legacy path
  so no prompt can reach it.
- Every act states its solver; "no solver selected" may appear nowhere.
- Motor items: cross-case battery sentence in the research agenda (third
  flag); anchor-vs-map coherence (label anchor table "housing reader" or
  re-anchor on core); 0.1 °C sig figs with the uncertainty sentence once as
  a footnote row, not 16 repeats; "replayed" is banned vocabulary in the
  figure list; registered motor prompt extended to "...across 80–305 W and
  10–40 m/s against a 200 °C limit"; geometry render rotated once to show
  the centerbody running the full duct length.
- Interpretation-confidence question (JF1 74%, motor 77%): treat by
  strengthening the real discrimination patterns for registered prompts
  (measured score, as DMR's 0.99), never by faking the displayed number.
- Standing order: verify ALL acts against her accumulated requests and
  conventions.
