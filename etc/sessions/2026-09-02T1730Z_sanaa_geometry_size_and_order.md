# SANAA-DIRECT — geometry size everywhere, runtime merge, JF1 order, battery caption, prompt revert (2026-09-02, ~17:30Z)

## Sanaa's words, verbatim

> the dafoam geometries are still so tiny at the begginign (before
> optimization starts) and in the Close view, iteration 6, 12.8% above
> untwisted baseline can you make the geometry big any time it appears ?
> also chang: Two runtime lines say the same thing: "Optimization total: 80
> core-minutes, 20.0 minutes wall at 4 ranks" and then "Runtime on the
> production configuration, with the linear solvers on GPU: 20 minutes."
> Merge: one line, "Optimization total: 80 core-minutes, 20.0 minutes wall
> at 4 ranks, adjoint linear solves on GPU.". JF1: the first geometry that
> shows is the 2D. JF1: the first thing that should appearis the STL file
> geometr, THEN the 2D plot (which you can label "NACA-class section, chord
> 1 m · jet slot at the trailing edge". Battery: remove T at the end of
> takeoff under the plot since we already have this: T (C), t = 60 s,
> module and coolant. also for dafoam i want th epormpt without the 'dont
> run convergence study' since now the script explicitely says ill get the
> convergence analysis in eta 11 min

## Context (chief's reading, not her words)

1. Act D: EVERY wing/geometry render fills the frame — including the
   pre-optimization beats and every "Close view, iteration N" frame; the
   fitted-camera work must cover all frames on all surfaces, not a subset.
2. Act D: the two runtime lines merge into her exact sentence:
   "Optimization total: 80 core-minutes, 20.0 minutes wall at 4 ranks,
   adjoint linear solves on GPU."
3. JF1: geometry order — STL surface first, then the 2D section plot,
   labeled "NACA-class section, chord 1 m · jet slot at the trailing edge".
4. Battery: drop the "T at the end of takeoff" caption under the plot
   (duplicate of "T (C), t = 60 s, module and coolant").
5. Act D registered prompt reverts to "Minimize drag at fixed lift. Stop
   after 20 mins" — the ETA-11-min script line covers the convergence
   story; the assumptions row/att attribution adapts (no longer
   request-declined; the platform schedules the study, inbox ETA stands).
