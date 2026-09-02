# Thermal demo acts — resume note (2026-09-02, ~06:4xZ, pre-subscription-switch)

Written under the coordinator's commit-everything order before the fleet is
killed by the subscription switch. State is MEASURED, not recalled. The two
acts are `sdk/workflows/motor_thermal_act.py` and
`sdk/workflows/battery_module_act.py`; both drive 9 of 9 stages offline via
`run_act` at this note's commit.

## LANDED (committed, verified by offline drives)

- Sanaa 0610Z wave convention: `sweep_execution()` derives waves from the
  launch records (contiguous busy blocks); `wave_sentence()` renders her
  general form with measured values: "16 runs on 12 workers is two waves, 4
  then 12; the wall clock follows the slowest member of each wave (30.5 and
  39.2 minutes), never the 579 core-minute sum." Spoken in the results
  discussion beat, replacing the contradictory slowest-member line.
- Predicted wall = predicted core-minutes / workers, spoken at the
  restatement beat: motor "560 core-minutes over 12 workers, about 47
  minutes"; battery "20.5 core-minutes at one worker".
- Compute tables: motor consumes the shared `compute_table` as the JF1 lane
  adapted it (workers | per-run | total | wall: 12 | 36.2 (29.7 to 39.2) |
  579 | 86 minutes). Battery carries per-run 7.1 and 12.6 | total 19.8 |
  wall 20 minutes at one worker.
- Monitor declaration: ONE panel, both temperature series, sixteen point
  labels in her in-panel style ("80W · 10m/s").
- Sentence-shortening pass over both acts' discussion beats.
- Geometry: both acts serve ONLY the ParaView body render plus the mesh
  panels; the tessellated STL canvas never runs (measured: zero
  `geometry.ready` events on both streams), which is her keep-two-views
  order already satisfied act-side.

## NOT DONE — for the successor lane, verbatim from her orders

1. **Grid panel inset (0610Z, SANAA-DIRECT).** "The grid panel must draw
   the solved polyMesh section, cell by cell, horizontal, fit-to-extents,
   wall-layer grading visible, with a zoom inset at the housing wall."
   Current state: `scripts/render_thermal_paraview.py` writes a full-extent
   horizontal section (`T23_P305_U20_mesh.png`, 39,680 slice polygons
   asserted == cells) and a SEPARATE `_mesh_zoom.png`; the inset composite
   is not built. Plan sketched: render main at content aspect
   (~1920x400), zoom at ~760x430, composite one 1920x1080 canvas with the
   inset bottom-right plus a locator rectangle; PIL is available; the
   world-to-pixel map is `make_view`'s (scale = max(span_v/2,
   span_h/(2*aspect))*1.04 about the section centre). Re-render, LOOK at
   the PNG with the Read tool, keep the sidecar's cells/case fields.
2. **Page-side monitor wrap (0610Z).** Sixteen cells must render as two
   rows of eight with the label INSIDE each panel, no shared header,
   caption once. Act-side declaration is done (one panel, 16 labels); the
   wrap is `control_room.html` `drawGSweep` work, owned by the display/JF1
   lane. Flag stands.
3. **0630Z figure polish, all three items, untouched** (see
   `etc/sessions/2026-09-02T0630Z_sanaa_motor_figure_polish.md` verbatim):
   round colour-bar ticks (20/40/60/80/100 C; 10/20/30/40 m/s) with min/max
   at the ends; the temperature figure's legend box off the first panel's
   field (to the black region right of row 1 or below); the velocity
   figure's per-panel field-range corner boxes back ("0.2-10.5 m/s" style).
   These live in the Act A figure generators under
   `docs/campaigns/T-family/demo/` (`regen_actA_sheet.py`,
   `render_actA_paraview/`), heat-transfer family territory.
4. **Geometry render nose/tail question.** Her 0610Z note describes the
   solved body as "nose, heated core section, tail". The solved T23 body is
   a CONSTANT-RADIUS centrebody running the full duct: the display-surface
   guard (`display_surface/generate_t23_display_surface.py`) REFUSES a
   nose or tail, and the export with them was the retired WRONG body. The
   current ParaView render (`T23_P305_U20_geometry.png`, half-cut oblique)
   shows the full-length centrebody and passes the guard. If she still
   reads it as a stub after the bounce, the answer is a view change, never
   a re-export of the retired shape; take the question up rather than
   redrawing the solved geometry.
5. **Shared compute-table workers column.** Her 0610Z words put parallelism
   in the wall column and the wave sentence; the shared `compute_table`
   (demo_mode, JF1 lane's file) still carries a workers column. Referred
   upward, not resolved here.

## ADDENDUM — Sanaa's 0650Z battery review, landed-vs-left at the kill

Read `etc/sessions/2026-09-02T0650Z_sanaa_battery_comments.md` verbatim
before resuming. State at the kill:

1. MESH RENDER (her "one refined band amid uniform coarse cells"):
   MEASURED FACTS for the diagnosis she asked for: the renderer draws the
   PRE-SPLIT mesh and `scripts/render_thermal_paraview.py` REFUSES unless
   the section's polygon count equals 16,608, so the full-domain claim is
   asserted, not assumed; the committed `T25R2_L1_mesh.png` was inspected
   and shows the module block with all SEVEN channel bands crossing it.
   Suspect instead: (a) the ZOOM panel (`_mesh_zoom.png`, one channel by
   design) filmed as if it were the main, or (b) the main panel's vertical
   aspect crushing the channel bands to single lines. LEFT TO DO: her
   fit-to-extents-plus-zoom-inset composite (the motor mesh-page pattern,
   plan in item 1 above) applied to the battery panel too, then PNGs
   re-inspected.
2. Monitors in SECONDS with the 0-60 s pulse window shaded: frames already
   carry `time_s` beside `iteration`; the axis choice and shading are the
   page's monitor strip (display lane). Act-side nothing further needed
   unless the contract grows an `x_series` field.
3. Three quantities answered explicitly in refusal: NOT DONE. The results
   table has peak/spread rows with standing but not her exact "peak over
   the record ... occurring at t = 900 s, the module has not settled within
   the record" phrasing, and the settle row reports a warming rate rather
   than the finding sentence. Measured values to use: peak max
   301.80 K = 28.7 C at t = 900 (the record's last row, still rising);
   spread at 900 s from the same monitor; settle = not settled within the
   record (module still warming ~mK/s at the end).
4. Two-arm overlay ("money shot"): NOT BUILT. WHAT IS ON DISK, measured:
   BOTH arms carry full monitor sets - `T25R2_L1_OC20/postProcessing/
   module/module_minmax/0/fieldMinMax.dat` exists alongside L1's, so the
   overlay CAN be built honestly (hottest-cell trace, 10 vs 20 sweeps,
   pulse transient region where O3 measured 2.32e-2 K against 1.23e-2
   allowed). Build it in `scripts/make_actC_figures.py`, add to
   `Results.plots`, inspect the PNG.
5. Set-by table: ALREADY carries "Coolant inlet temperature 20.0 C, the
   lab" (from 0.orig/coolant/T = 293 K); verify it satisfies her ask or
   extend wording to name it as the rise reference.
6. Per-cell traces panel (all 8 cells, pulse shaded): NOT BUILT; the run
   writes per-region extrema only in module_minmax - check whether per-cell
   probes exist under postProcessing before promising 8 traces; if only
   min/max exist on disk, say so rather than synthesize.
7. Battery sentence-shortening: one pass done (restatement/gates beats);
   results verification lines still long, one more pass wanted.

## ADDENDUM 2 — emergency kill-order stop point (0705Z batch measured state)

Sanaa's 0705Z battery batch 2 (`etc/sessions/2026-09-02T0705Z_sanaa_battery_comments_2.md`,
read it verbatim) arrived at the kill. State:

- MONEY-SHOT CHANNEL, MEASURED (the finding the successor needs first): the
  23.2 mK O3 movement is the COOLANT OUTLET area-mean temperature at
  t = 60 s (analyse_t25R2.py:326 names O3 as exactly that; measured between
  the two arms' own outlet_Tbar monitors: 23.15 mK at t = 60, max 24.95 mK
  at t = 10). The HOTTEST-CELL traces differ by at most 1.31 mK (at
  t = 900) and only 0.04 mK at t = 60, so her "hottest-cell trace with the
  23.2 mK gap visible" CANNOT be drawn honestly from the cell traces. The
  committed `actC_two_arm_overlay.png` overlays the hottest-cell traces
  (honest, but the inset shows coincidence, not the gap). REBUILD the money
  shot as the OUTLET Tbar overlay (both arms' monitors are on disk),
  labeled as the outlet, inset on 40-90 s; keep the cell-trace overlay as
  the companion that shows the cells themselves barely move.
- 0705Z-1 (28.7 vs 27.8 fork): my act derives every 28.7 from ONE source
  (module_minmax max at t=900 = 301.80 K = 28.7 C); grep of my streams
  shows no 27.8, so the fork is on a page surface or the pre-bounce screens.
  Verify on the live page after the bounce before editing anything.
- 0705Z-2 (her uncertainty sentence, verbatim replacement), 0705Z-3
  (Celsius everywhere; the field render's colour bar is in K, add a
  Calculator T-273.15 to render_thermal_paraview.py field mode and restage
  the figure), 0705Z-4 (explicit spread/peak/settle wording; table rows
  exist, her exact phrasing not yet), 0705Z-5 (figure-list dedupe; check
  plot.ready duplicates on the live page), 0705Z-6 (two-row compute table,
  one per arm, plus the one-worker wall sentence): ALL NOT LANDED; the act
  file's current single-row compute table and limitations wording are the
  state to edit from.
- 0650Z-6 per-cell traces: MEASURED: no per-cell monitor exists on disk
  (module_minmax extrema only); per-cell traces would have to come from the
  181 written module/T fields grouped by cell block; say so on any screen
  rather than promising 8 traces from monitors.
