# SIDECAR — ONERA M6 demo plot folder (`plots_M6J`)

Built 2026-09-13 from REAL fields on disk by `build_plots.py` in this folder.
**Zero solver compute.** Figure names follow `docs/plot_orders/README_PLOT_ORDERS.md`
section A. Every array that was plotted is beside its figure as a `.csv`; every
artifact each figure read is in `PROVENANCE.tsv` with its path, time directory and
sha256.

**No verdict word and no band annotation is printed on any image** (owner
correction, 2026-09-13). Both live here and in `README.md`.

## The verdict of every source

| Source | Verdict | Where it is recorded | sha256 of the grade file |
|---|---|---|---|
| `M6J_L1` (983,040 cells, t = 8000) | **GATE FAIL** | `verification/runs/M6J_runs/M6J_L1/m6j_grade_M6J_L1.json` | `e2256d198b83db2784d28b7fefa6f9820cbec2b6e7b8241f46efa3249d8be233` |
| `M6J_L2` (122,880 cells, t = 5000) | **GATE FAIL** | `verification/runs/M6J_runs/M6J_L2/m6j_grade_M6J_L2.json` | `4c5c30d61f32076e6a4989b252c731ebc26e6c385ee4ed975bc5e7d2ebe1a631` |
| `M6J_L3` (15,360 cells, t = 3000) | **GATE FAIL** | `verification/runs/M6J_runs/M6J_L3/m6j_grade_M6J_L3.json` | `5cf7eac6343333831bc0d5956ce4b1ab1eb7036fd8da9a0e5f3844d2dccf2fc0` |

`GATE FAIL` is B1: the per-station, per-surface RMS Cp deviation exceeds the
registered band of 0.050 on the rows named in each grade file's `why`. The
pre-registration is
`verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md`.

## The band on `m6_family.png`, stated plainly

**There is no GCI and no observed order on this figure, and none is implied.** The
grade files' own disclosure says so: *"SINGLE GRID. This is a VALIDATION
comparison, not a verification… NO observed order and NO GCI is computed, quoted
or implied."* The green region is the **registered B1 band, 0 to 0.050**, drawn by
`act_plots_lib.grid_family(band=…)`. No numeric GCI appears anywhere on the image
or in this folder.

The plotted quantity is the **mean over the twelve graded rows of `rms_dev`**, read
from each level's grade file: **0.2355 → 0.0948 → 0.0465** on 15,360 → 122,880 →
983,040 cells.

## Readers reused, never re-derived

* **Cp extraction** — `verification/runs/M6J_runs/<level>/cp_extracted.json`, the
  file the grader itself read, written by
  `verification/runs/M6I_runs/extract_cp_m6i.py`. Nothing was re-extracted.
* **Reference table and the upper/lower split** — `scripts/grade_m6_agard_cp.py`
  `read_reference()` and `cfd_curve()`, imported as a module. The reference is
  AGARD AR-138 TABLE B1-14, TEST 2308 (M0 = 0.8395, α = 3.06°, Re = 11.72e6) at
  `models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat`, title-page verified in
  the grade file.

## Per figure

| Figure | What it is | Source |
|---|---|---|
| `m6_cp_stations.png` | Cp at the six graded stations, **upper surface**, ±0.05 band, tunnel taps as markers | `M6J_L1` cp_extracted at `M6J_L1_8000` + AGARD B1-14 |
| `m6_family.png` | mean row RMS Cp deviation on three levels, registered band drawn | the three grade files |
| `m6_forces.png` | Cd and Cl against iteration, restarts stitched (later segment wins on overlap) | `M6J_L1/postProcessing/forceCoeffs/{0,200,3800}/coefficient.dat` |
| `m6_residuals.png` | initial residuals Ux, Uy, Uz, e, p, target 1e-6 | `M6J_L1/postProcessing/residuals/{0,200,3800}/solverInfo.dat` |
| `m6_mesh.png` | the **coarse** level's wall patch, per the owner's ParaView rule | `M6J_L3` polyMesh, 480 wall faces, guard PASS |
| `m6_p_upper_top.png`, `m6_p_oblique.png` | static pressure on the **fine** level's wall patch, from above and obliquely | `M6J_L1` at t = 8000, 7,680 wall faces |

| `m6_p_upper_top.png` | surface pressure from above, the shock visible | `M6J_L1` at t = 8000 |
| `m6_p_oblique.png` | the same surface obliquely, FINE-level mesh edges drawn | `M6J_L1` at t = 8000 |
| `m6_geometry.png` | the imported grid's wall patch, captioned **"as meshed"** | `M6J_L1` wall patch |
| `m6_mach_eta065.png`, `m6_mach_eta090.png` | Mach on the spanwise plane through each graded station | `M6J_L1` `U` and `T` at t = 8000 |
| `m6_umag_eta065.png`, `m6_umag_eta090.png` | velocity magnitude on the same two planes | `M6J_L1` `U` at t = 8000 |

**Every ParaView panel in this folder is now `render_field_panels.py`'s.** The two
`scripts/render_openfoam_3d_paraview.py` panels that used to sit here — a dark
background with an orientation triad — were **deleted** when v2 fixed the look, and
`m6_surface_pressure.png` with them: `m6_p_upper_top.png` is the same field on the
same patch, white-ground and triad-free.

## The field panels: what is measured and what is chosen

* **The two station planes are not typed in.** They are `y_cut_target` for
  η = 0.65 and η = 0.90 read from `cp_extracted.json` — **the same y the family's
  own extractor cut at** to produce the Cp rows the grade file graded, so the slice
  and the graded row are the same plane.
* **Mach is computed from the case's own fields**, `mag(U)/sqrt(γ R T)`, with γ and
  R taken from that file's `freestream` block, which was written **before any
  solve** and is not re-derived from the solution.
* **One colour window per quantity, shared across both stations**, measured at the
  2nd and 98th percentile over both planes: Mach **0.0233 to 1.2302**, velocity
  **8.23 to 400.0 m/s**, surface pressure **37,677 to 147,233 Pa**. The window is a
  **display** choice and is printed on every caption with the words *ends clamped*;
  nothing is removed from the data. It exists because the full range is set by a
  handful of leading-edge stagnation cells (Mach reaches 1.527) and a bar stretched
  to those extremes paints the whole picture one colour.
* **One colour map for both station quantities** (Viridis), because a reader
  compares Mach and velocity across four panels.
* **Every coloured panel carries a planted colour control** at the DrivAer 8x
  margin: the same pipeline rendered once on a CONSTANT array, both PNGs measured
  through `render_k2h_l3._colour_spread`. Measured ratios: p 9.6x / 7.7x on the
  full-body mask and **21.5x / 16.8x on the interior**, Mach **20.9x / 18.7x**,
  velocity **19.9x / 17.9x**.

**Two measurement artefacts were found and removed from BOTH arms rather than
answered by lowering the margin.** Caption text and mesh edges are dark pixels
inside the "not the white ground" body mask and sit at a red/blue ratio of 0 while
a flat control sits near −0.71, which gave the CONSTANT arm a spread of 0.0756 that
belonged to the lettering; they are therefore added after the measurement. On a
curved surface seen obliquely the antialiased silhouette does the same, so the
surface panels are also measured on an interior-only mask at threshold 0.25 and
**both** statistics are printed. The 8x floor was never moved.

## Ordered figures this folder does NOT contain, and why

* **`m6_cp_upper.png`** (upper-surface **Cp** in ParaView) — no `Cp` field is
  written to disk by this family; the solver writes `p` in Pa. `m6_p_upper_top.png`
  is the same picture in the field that exists.
* **`m6_geometry.png`** (the admitted STL) — this family is an **imported reference
  grid family**. There is no admitted surface tessellation under
  `models/onera_m6/`; the wall patch in `m6_mesh.png` is the only geometry the run
  ever saw.
* **Both surfaces on `m6_cp_stations.png`** — the panel draws the **upper** surface,
  matching the example the orders point at. The lower-surface CFD and tunnel rows
  are in `m6_cp_stations.csv` and are graded in the grade files.
* **Station η = 0.95** — the registered station is **η = 0.96**; the orders' 0.95 is
  not a station this campaign grades. η = 0.99 is registered as EXCLUDED.

---

## v2 REGENERATION — 2026-09-13

Everything above still holds. What changed is the DRAWING, not a number.

* **Plot library v2** (`docs/plot_orders/README_PLOT_LIBRARY_V2.md`), installed by the
  owner. Math only: no English on any figure, no titles, no verdict words, no band
  named in words. **v2 already carries both library changes this lane had made** —
  `%` in place of the word, and a registered `band=(lo, hi)` on `grid_family` — in a
  better form, so neither was re-applied. **One minimal change was added:**
  `residual_history` gained `xlim`/`ylim`, because the residual-evolution frames below
  are only comparable if the axes do not move; without pinned axes each frame
  autoscales to its own data, every frame looks identical, and the descent that is the
  whole point of the series is invisible.
* **Residual evolution.** `sdk/workflows/act_residual_frames.py` cuts the run at
  **10, 25, 50, 75 and 100 %** and writes one frame per cut on ONE set of axes, so the
  act can step through them and the curves are seen to go down. The 100 % frame keeps
  the ordered file name; the others are `*_f10 … _f75`.
* **ParaView panels re-rendered to v2 §13:** white ground, **no orientation triad**,
  **one colour bar a quarter of the frame high** titled by symbol and unit, and
  **nothing written on the image**. The case, the time, the geometry and the verdict
  now live HERE and in the act beside the figure. **The verdict guard was not dropped
  with the caption**: `demo3d_render_common.assert_stamp` still runs on the stamp each
  driver WOULD have drawn, before any pixel, so a verdict word a case does not own is
  still refused. What moved is where the sentence is printed, not whether it is checked.

* **A COARSE-OR-MEDIUM MESH PANEL, per the owner's standing rule of 2026-09-13**
  (*"for all the cases we should plot the coarse or medium mesh (but show the fine
  mesh's result)"*): `m6_mesh_medium.png`, the **medium** level `M6J_L2`'s wall patch,
  **1,920 faces** of a 122,880-cell mesh. **Medium and not coarse is a measurement,
  not a default**: the rule admits either, and the boundary files say `M6J_L3` carries
  **480** wall faces against L2's 1,920 — which is exactly the "reads as a toy"
  complaint. **Every FIELD panel in this folder still comes from the FINE level**, and
  nothing is interpolated between the two meshes.
* **The nose cut stays on the FINE level.** The owner: *"the 480-face coarse
  wall patch reads as a toy"*. `m6_mesh.png` is a **cut at the η = 0.65 station**,
  framed on the leading edge, showing the cells across the nose and the wall
  layers — 28,048 cells in that plane; `m6_mesh_surface.png` is the fine level's
  own 7,680-face wall patch. The coarse level keeps a mesh figure only where a
  snappy mesh is genuinely illegible, and this structured O-grid is not.
* `m6_geometry.png` is the imported grid's wall patch, the geometry **as meshed**;
  there is no admitted STL for this family and none was invented.

---

## ROUND 4 — 2026-09-14, THE OWNER'S FIGURE-BY-FIGURE NOTE

Six of her points, executed. **No solver ran**; every panel is the same graded
solution re-drawn. `PROVENANCE_PANELS.tsv` now carries a row per ParaView panel:
case, cells, time directory, the patch or plane, the camera and the colour window
with the basis it was chosen on.

**The level, settled first, because her note and this folder name it differently.**
She writes *"L3 (983k cells)"*. The 983,040-cell level is this family's **`M6J_L1`**
— `constant/polyMesh/owner` reads `nCells:983040`, the `wing` patch **7,680 faces**;
`M6J_L3` is the **15,360**-cell coarse level with **480** wall faces. The field
panels were **already** on the 983,040-cell level and still are. What made them look
coarse was the DRAWING: `p` was painted **per cell**, so 7,680 flat facets, with the
**cell edges drawn on top**. Both are gone — `p` is interpolated to the points and
the pressure panels carry no wireframe. The mesh panels keep their edges.

| Her item | File | What changed |
|---|---|---|
| 1. surface pressure, oblique | `m6_p_oblique.png` | point-interpolated `p`, no cell edges, round five-tick bar |
| 2. upper-surface pressure, plan | `m6_p_upper_top.png` | camera **along −z**, up +y, parallel projection, whole planform with a 5 % margin; same window as item 1 |
| 3, 4. Mach at 65 % / 90 % span | `m6_mach_eta065.png`, `m6_mach_eta090.png` | **M fixed 0 to 1.4**, five ticks 0 / 0.35 / 0.70 / 1.05 / 1.40, **M = 1 drawn in black**, section outlined, window cut to the chord (−0.3 c to +1.3 c, ±0.6 c), bar lettering enlarged |
| 5. mesh convergence | `m6_family.png` | unchanged |
| 6. Cp at six stations | `m6_cp_stations.png` | **all twelve graded rows** — upper *and* lower at each station, both surfaces' taps |
| support: force / residual / nose cut / surface mesh | unchanged | unchanged |
| support: "wing surface as meshed" | `m6_geometry.png` | the **plain** surface: no field, and now no wireframe either, so it is not a second copy of `m6_mesh_surface.png` |

### The colour windows, and the rule they were chosen by

Her rule: *where the raw range is much wider than the field's 2nd–98th percentile
band on the rendered surface, use the percentile band, rounded outward to round
values with five round ticks.* "Much wider" is fixed at a quarter again as wide and
is stated in the code, not left to the eye. Measured on this solution:

* **surface `p`** — raw **37,677 to 147,233 Pa**, percentile band **43,734 to
  140,055**. The raw range is **not** much wider, so the RAW range is the window,
  rounded outward to **30,000 to 150,000 Pa**, ticks every 30,000. Shared by both
  surface panels.
* **Mach** — **FIXED 0 to 1.4 by her order**, whatever the data does. Measured for
  the record: raw **0.00096 to 1.5272**, percentile band **0.0233 to 1.2302**. The
  ends are clamped; nothing is removed from the data.
* **|U|** — raw **0.347 to 467.8 m/s**, percentile **8.23 to 400.0**; raw again not
  much wider, rounded to **0 to 500 m/s**, ticks every 125.

### What the Mach panels actually show, stated here and not on the figure

There **is** a supersonic pocket on the upper surface and the sonic line closes it.
Measured from the graded Cp rows against this case's own critical pressure
coefficient **Cp\* = −0.3282** (from γ = 1.399726, M∞ = 0.8395):

| station | CFD pocket, x/c | tunnel taps below Cp\*, x/c |
|---|---|---|
| η = 0.65 | **0.009 – 0.500** | 0.020 – 0.450 |
| η = 0.90 | **0.009 – 0.289** | 0.012 – 0.300 |

So the pocket is there and it ends roughly where the tunnel's does. **What is not
there is the lambda (double-shock) structure at η = 0.65**: the panel shows ONE
continuous pocket closed by a single, gradual sonic front, not two. That is the
solution, and the figure draws the solution. The same smearing is what the grade
file reports as `cfd_cp_rise_at_shock` **0.109** against the experiment's **0.424**
at η = 0.65.

### The Cp panel and the twelve rows — READ THIS BEFORE QUOTING THE FIGURE

The panel now draws **all twelve graded rows**: at each of the six stations the
section loop runs lower surface from the trailing edge to the nose and upper
surface back, with the tunnel taps of BOTH surfaces as markers. Nothing was
re-extracted — these are the same `cfd_curve` and `read_reference` arrays the
grader itself read, from `M6J_L1/cp_extracted.json` at `M6J_L1_8000`.

**THE TWELVE ROWS ARE NOT ALL INSIDE THE BAND, AND NO SOLUTION IN THIS LAB HAS
THEM ALL INSIDE.** Every M6 grade file on disk was re-read for this round — the
three M6J levels, the eight M6I variants and the dafoam A3 primal — and the best
any of them reaches is **7 of 12**. `m6j_grade_M6J_L1.json` is `GATE FAIL` with
**7 of 12 inside**: all six lower surfaces, and **one of six uppers** (η = 0.80).
"All twelve rows inside B1" is the **PASS RULE** written in
`A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md:197` and
`M6I_R1_SOLVE_PREREGISTRATION.md:70` — a condition registered before the run, not
an outcome any run has met. The figure therefore stands on the graded solution and
shows the upper surface where it is.

| row | RMS ΔCp | band | | row | RMS ΔCp | band | |
|---|---|---|---|---|---|---|---|
| η 0.20 lower | 0.0381 | 0.050 | inside | η 0.20 upper | 0.0708 | 0.050 | **miss** |
| η 0.44 lower | 0.0328 | 0.050 | inside | η 0.44 upper | 0.0632 | 0.050 | **miss** |
| η 0.65 lower | 0.0174 | 0.050 | inside | η 0.65 upper | 0.0686 | 0.050 | **miss** |
| η 0.80 lower | 0.0190 | 0.050 | inside | η 0.80 upper | 0.0418 | 0.050 | inside |
| η 0.90 lower | 0.0232 | 0.050 | inside | η 0.90 upper | **0.1046** | 0.050 | **miss** |
| η 0.96 lower | 0.0209 | 0.050 | inside | η 0.96 upper | 0.0575 | 0.050 | **miss** |

Worst row **η = 0.90 upper, RMS 0.1046 — 2.09× the band**, worst single orifice
**0.4821** at x/c = 0.002.

### Two renderer facts, recorded rather than worked around

* ParaView 5.11.2 draws `[` and `]` in a scalar-bar title as parentheses, and drops
  the `|` of `|U|`. The titles are written with the glyphs the orders ask for.
* `pvpython` exits **rc = 1** on `GLXBadContext` **after** the driver has returned 0,
  written every panel and proved the run tree unchanged. It is an X teardown in the
  headless server, not a render failure; every figure in this round was written
  before it.
