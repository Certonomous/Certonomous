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
| `m6_surface_pressure.png` | static pressure on the **fine** level's wall patch | `M6J_L1` at t = 8000, 7,680 wall faces, guard PASS |

| `m6_p_upper_top.png` | surface pressure from above, the shock visible | `M6J_L1` at t = 8000 |
| `m6_p_oblique.png` | the same surface obliquely, FINE-level mesh edges drawn | `M6J_L1` at t = 8000 |
| `m6_geometry.png` | the imported grid's wall patch, captioned **"as meshed"** | `M6J_L1` wall patch |
| `m6_mach_eta065.png`, `m6_mach_eta090.png` | Mach on the spanwise plane through each graded station | `M6J_L1` `U` and `T` at t = 8000 |
| `m6_umag_eta065.png`, `m6_umag_eta090.png` | velocity magnitude on the same two planes | `M6J_L1` `U` at t = 8000 |

`m6_mesh.png` and `m6_surface_pressure.png` were drawn by
`scripts/render_openfoam_3d_paraview.py`, whose per-patch face-count guard PASSED
and which proved the graded tree unchanged; their own `.json` sidecars sit beside
them. The seven panels above were drawn by `render_field_panels.py` in this folder.

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
  written to disk by this family; the solver writes `p` in Pa. `m6_surface_pressure.png`
  is the same picture in the field that exists, and is named for what it shows.
* **`m6_geometry.png`** (the admitted STL) — this family is an **imported reference
  grid family**. There is no admitted surface tessellation under
  `models/onera_m6/`; the wall patch in `m6_mesh.png` is the only geometry the run
  ever saw.
* **Both surfaces on `m6_cp_stations.png`** — the panel draws the **upper** surface,
  matching the example the orders point at. The lower-surface CFD and tunnel rows
  are in `m6_cp_stations.csv` and are graded in the grade files.
* **Station η = 0.95** — the registered station is **η = 0.96**; the orders' 0.95 is
  not a station this campaign grades. η = 0.99 is registered as EXCLUDED.
