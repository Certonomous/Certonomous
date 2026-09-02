# Thermal demo acts — resume note (2026-09-02, updated ~10:3xZ)

State is MEASURED, not recalled. The two acts are
`sdk/workflows/motor_thermal_act.py` and
`sdk/workflows/battery_module_act.py`; both drive 9 of 9 stages offline via
`run_act` at this note's commit (motor 3,353 events, battery 793;
`scripts/check_demo_acts.py`: 5 of 5 can start, 0 checklist failures,
checklist selftest 60/60 plants fired).

## LANDED (committed, verified by offline drives and PNG inspection)

Earlier (pre-kill): wave convention, predicted wall = core-min/workers,
motor compute table via shared `compute_table`, one-panel monitor
declaration with 16 in-panel labels, sentence shortening, ParaView-only
geometry (zero `geometry.ready` on both streams).

This session (commits `cff0b770`, `05419de5`, `f930b7b3`, `fab34302`):

- **No-tessellation GATE (Sanaa 0930Z relayed).** New `no_tessellation`
  checklist line in `scripts/check_demo_acts.py`: an act serving a rendered
  geometry panel fails if a `geometry.ready` rides its stream at ANY index;
  a declared panel that never publishes is refused. Structural plant added,
  selftest fires. Measured ordering on both thermal streams: the ParaView
  `mesh.panel` (surface.png) is event 1, before the first `stage.begin`;
  `geometry.ready` count is 0. The one remaining window is PAGE-owned: the
  pre-mission upload preview (`control_room.html` `loadGeometry` /
  `paraviewOwned`) may paint the plain surface before any act event exists
  — display lane, reported to the chief.
- **Mesh composites (0610Z motor render defect 1; 0650Z battery item 24).**
  `scripts/render_thermal_paraview.py` mesh mode writes the served
  `<case>_mesh.png` as ONE 1920x1080 composite: fit-to-extents section at
  content aspect + wall zoom inset bottom-right + locator rectangle drawn
  with `make_view`'s own world-to-pixel map + leader line. Re-rendered and
  inspected for `T25R2_L1` (all SEVEN channel bands + one-channel wall-layer
  inset; 16,608 slice polygons asserted == cells) and `T23_P305_U20`
  (full duct + housing-wall inset; 39,680). Diagnosis of her "one refined
  band" frame: the standalone `_mesh_zoom.png` (one channel BY DESIGN) was
  filmed as if it were the main; the main panel now carries both views.
- **Battery items 18-27 (0730Z list), act-side complete:**
  - 18: stream is one source; every 28.7 derives from
    `T25R2_L1 postProcessing/module/module_minmax/0/fieldMinMax.dat` max at
    t=900 (301.8008 K); endpoint additionally PINNED on `solve.end`
    (`final_monitors`, `final_time_s`). Every "27.8" in the stream is the
    trace passing t=755-765; the filmed 27.8 axis top is a PAGE surface.
  - 19/20: results table answers peak/spread/settle in the prompt's order;
    peak row "occurs at t = 900 s"; settle row is the finding ("not settled
    within the record", measured warming rate as standing); spread rows
    named "hottest to coolest point" with the no-per-cell-monitor
    limitation stated (none exists on disk — measured, module_minmax
    extrema only).
  - 21: closing uncertainty carries her sentence verbatim ("Single grid, so
    no discretisation band; and the sweep convergence check refused
    certification of the values themselves.").
  - 22: Celsius everywhere — the ParaView field render converts via a
    Calculator (range asserted == kelvin range - 273.15), bar "T (C)" with
    plain-decimal min/max ends; caption, spread rows, feasibility rise in C.
  - 23: compute table two rows, one per arm, shared four-column shape; each
    row's ranks/clock/sweeps read from that arm's own records; one-worker
    wave sentence speaks in the results beat.
  - 24: see mesh composites above.
  - 25: `actC_outlet_overlay.png` is the money shot, drawn where the gap
    LIVES: the COOLANT OUTLET area-mean (O3, `analyse_t25R2.py:326`),
    both arms' own monitors, pulse shaded, 40-90 s inset where the curves
    visibly separate; annotation "23.2 mK apart, 12.3 allowed" computed
    from the plotted rows / read from `OC_GATE.json`. The hottest-cell
    overlay stays as the companion, inset stating the measured coincidence
    ("traces within 1.3 mK"). Both + module history are in `Results.plots`.
  - 26 act-side: monitor panel declares `x_label "t (s)"`,
    `x_series: time_s`, `pulse_window_s: [0, 60]` (breakpoint read from
    fvOptions). Page must consume these — display lane.
  - 27: set-by table row "Coolant inlet temperature, the rise reference,
    19.9 C, the lab" (the case's own 0.orig value, 293 K).
- **Motor 0630Z figure polish, all three items**
  (`figures_actA/render_fields_actA.py`, figures regenerated + inspected):
  round colour-bar ticks (20/40/60/80/100 C; 10/20/30/40 m/s) with true
  min/max at the ends; legend moved below the panels off the first panel's
  field; velocity whole-model panels carry per-panel range corner boxes
  ("0.2-10.5 m s-1" style, each panel's own array). Bundle records the
  0630Z amendment to the extremes-nowhere-else clause.

## PAGE-SIDE NEEDS (control_room.html — display/JF1 lane, NOT this lane)

1. **Figure-strip dedupe (item 26 tail / cross-act item 28).** Both thermal
   streams emit each `plot.ready` exactly ONCE (measured; titles all
   distinct). The Report tab (`renderMemo`) already de-dupes by URL; the
   STRIP does not: `addPlot` (~control_room.html:3386) pushes to
   `state.plots` and appends a `<figure>` unconditionally, so a re-delivered
   event (reconnect/replay) duplicates the on-screen figure list. The
   shared fix is a URL de-dupe in `addPlot` — one edit, deployed to every
   act by construction.
2. **Monitor strip x-axis/shading**: consume `x_series` ("time_s") and
   `pulse_window_s` from the act's `monitor_panels` declaration.
3. **2x8 monitor wrap (0610Z motor)**: sixteen cells as two rows of eight,
   label inside each panel, no shared header, caption once (`drawGSweep`).
4. **27.8 axis top (item 18's defective surface)**: the act stream's
   endpoint is 28.7 with `final_monitors` now pinned on `solve.end`;
   verify the live strip after a bounce reaches t=900 and autoscales past
   28.7, or pin its endpoint from `final_monitors`.
5. **Pre-mission upload preview** may paint the tessellated STL before any
   act event (see gate note above); Sanaa 0930Z wants it never shown at all.

## STILL OPEN, THIS LANE

- Nothing from the 0610Z-0745Z captures. Watch for her read of the new
  composites/figures after the next filming pass.
- "replay" appears in one motor figure FILENAME only
  (`actA_monitor_replay.pdf`, its URL on the wire); title/caption prose are
  clean and the language gate passes. Rename only if ruled.
- Geometry nose/tail question (0610Z): unchanged — the solved T23 body IS
  the full-length constant-radius centrebody; a re-read as a stub is a view
  change question, never a re-export of the retired shape.
- Shared compute-table workers column (0610Z): still referred upward.

## STANDING MEASURED FACTS (do not re-derive blind)

- Battery peak: 301.8008 K = 28.7 C at t=900 (fieldMinMax final row);
  module min there 296.9896 K = 23.8 C; spread 4.8 C; outlet 21.9 C.
- The 23.2 mK gap is the COOLANT OUTLET (23.15 mK at t=60 between arms'
  outlet monitors, max 24.95 mK at t=10); hottest-cell traces differ
  <= 1.31 mK. O3_tol = 12.3 mK (OC_GATE.json).
- No per-cell monitors on disk; per-cell traces would need the 181 written
  module/T fields grouped by cell block.
- Arms: T25R2_L1 (10 sweeps, 7.1 core-min) and T25R2_L1_OC20 (20 sweeps,
  12.6 core-min), 1 rank each; total 19.76 vs scripted estimate 20.5.
