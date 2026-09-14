# SIDECAR — K2 TRANSIENT demo plot folder (`plots_K2_transient`)

Round 4, 2026-09-14. Built from REAL series and REAL written fields on disk by
`build_plots.py` and `render_k2t_panels.py` in this folder. **Zero solver compute.**
No verdict word, no band annotation, no caption, no cell count and no English is
drawn on any image (plot library v2; owner corrections 2026-09-13 and the order of
2026-09-14). Everything a reader needs to interpret a figure is on this page.

## The run

`verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59` —
**137,000 cells** (`log.checkMesh`, `COST.txt` `cells 137000`),
`buoyantBoussinesqPimpleFoam`, `endTime 80.0`, **995 time steps**, `End` in the log.
Written time directories: **0, 20, 40, 60, 80**. Room 3.6 × 3.5 × 2.7 m; a row of
four 0.6 m cabinets spanning x = 0.6 → 3.0 m with **open row ends**; floor tiles in
the cold aisle at y = 0.6 → 1.2 m; ceiling return at y = 2.6 → 3.2 m.
Verdict **GATE REACHED** (`K2bU3R3_GRADE.txt`).

## The window, and how the mean is taken

The ordered window is **50 → 80 s**. This run carries **no `fieldAverage`**: there is
no `TMean`, no `UMean` and no `uniform/fieldAveragingProperties` anywhere in the
tree, so no solver-side window average exists to be used. The window mean on every
figure that has one is therefore the **arithmetic mean of the TWO written time
directories inside the window, 60 s and 80 s** — two snapshots, not a 30 s average,
and every such figure's `PROVENANCE.tsv` row says so in its `window` column.

`k2t_residuals.png` and `k2t_ride_through.png` are **not** window means: they show the
whole 0 → 80 s record.

## The two checks printed with this set

Both are computed by `k2t_window.py` from the run's own patch data, over the window:

| Check | Measured | Expected in the order |
|---|---|---|
| window-mean room rise | **16.1641 K** (flux-weighted `return` temperature 305.1641 K minus the area-weighted `tile` supply 289.0000 K) | ~16.6 K |
| total tile flow | **0.980000 m³/s** (Σ\|φ\| over the 400 `tile` faces; 0.2450 m³/s under each of the four racks) | 0.98 m³/s |

The tile flow matches exactly. The room rise is **0.44 K below** the order's figure
and **is not adjusted**: the room is still warming through the window — the same
number is 15.7958 K at t = 60 and 16.4786 K at t = 80, and the fully-mixed steady
value the design implies, 4 × 0.35 × 12 ÷ 0.98 = 17.14 K, has not been reached by
t = 80 s.

## The planted control

`k2t_window.plant_check()` runs before any figure is drawn. It copies `80/T` into a
scratch tree, plants **1.234e-03 K** on the `tile` patch (`value` entry) and on one
`rack0_in` owner cell (the zeroGradient path), and re-reads both through the same
functions the figures use. Both came back **1.234e-03 K, tolerance 1e-09**. Nothing
is written into the graded run tree, and `demo3d_render_common.assert_run_tree_untouched`
proves the tree unchanged after every render.

Each coloured ParaView panel additionally carries the folder's colour control at the
8× margin, both arms in `_control/`: measured **76.6×** (`k2t_plane_mid`),
**25.9×** (`k2t_plane_mid_velocity`) and **264.9×** (`k2t_plane_hot`) against a
constant array, over 0.73 M, 0.73 M and 1.19 M painted pixels.

## Why `T` on a rack inlet is read from the owner cell

`T` on `rack{i}_in` is `zeroGradient` — the rack inlet is an **outflow of the room**,
so the patch entry carries no `value` and the frozen `foam_patch_reader` refuses it,
correctly. A zeroGradient face carries its owner cell's value by definition, so
`k2t_window.Case.patch` falls back to `constant/polyMesh/owner` and the internal
field. Which path produced a number is returned beside it, and the planted control
above exercises **both** paths.

## Per figure

| Figure | Source | Window | Camera / colour range | Note |
|---|---|---|---|---|
| `k2t_mesh.png` | `K2bU3R3_D59` mesh | — | ISO from the cold-aisle side | patches `floor`, `tile`, `rack{0..3}_{in,out}`, `rack_top`, `rack_end`; 7,552 faces with their cell edges. The four cabinets are **voids** in this mesh, so their surface *is* the rack patch set; the cabinet outlines separate the four. Tile and floor outlines are lifted 12 mm so they do not z-fight with the floor patch. |
| `k2t_residuals.png` | `log.buoyantBoussinesqPimpleFoam` | 0 → 80 s | — | first outer corrector of each of the 995 steps, $t$ in seconds |
| `k2t_dp_history.png` | **`K2h_L3`** | 42 → 112 s registered | — | **as pushed; not redrawn this round** (`REDRAW_DP = False` in `build_plots.py`) |
| `k2t_ride_through.png` | `K2bU3R3_D59` `T_rack{0..3}_in_mdot` | 0 → 80 s | — | 400 mass-flow-weighted samples per rack. **Both limit lines are drawn**: `T_lim = 27 °C` and the supply line. The supply line carries the run's OWN supply temperature, 289.0 K = **15.85 °C** (`build_k2b.T_SUP`), not the order's rounded 16 °C — a line labelled with a number the case does not carry would be a false reading. The `T_sup` line was **added this round**; the figure previously drew `T_lim` alone. |
| `k2t_inlet_profiles.png` | `60/T`, `80/T` on `rack{0..3}_in` | 50 → 80 s (2 times) | — | mean over the rack's width at each of the 34 face-centre heights. The inlets are below 27 °C over most of their height and **cross it in the top ~0.2 m** — the recirculation this room actually has. |
| `k2t_indices.png` | **`K2h_L3` `110/TMean`** | 42 → 110 s | — | **the existing numbers, reused unchanged as the order directs.** They are `K2h_L3`'s, not `K2bU3R3`'s, and are the only numbers in this folder that are not from `K2bU3R3_D59`. They read capture ≈ 100 % and $f_{rec}$ ≈ 0.004 %; the same quantities computed on `K2bU3R3` over this window would not agree, and RTI on `K2bU3R3` would be ≈ 135 %, not the 28.25 % drawn. Nothing is recomputed here. |
| `k2t_rack_dT.png` | `60/T`, `80/T` on `rack{0..3}_{in,out}` | 50 → 80 s (2 times) | — | **11.9361, 12.0067, 11.9973, 11.8745 K** against the 12 K line. The rack outlet is an `outletMappedUniformInlet` at **+12 K on the mass-averaged inlet**, so this figure shows that the boundary condition is being enforced to within 0.13 K; it is not an independently computed rise. 12 K at 0.35 m³/s is 4.91 kW on the lab property pair. |
| `k2t_airflow_balance.png` | `60/phi`, `80/phi` on `tile` and `rack{0..3}_in` | 50 → 80 s (2 times) | — | tile supply **0.2450** m³/s per rack, rack demand **0.3500** m³/s, bypass **−0.1050** m³/s. Bypass is defined here as **tile supply minus rack demand**; it is negative because the room is provisioned at 70 %, and the deficit is made up from recirculated room air. `k2t_airflow_balance.csv` carries **SHI = 0.27895** and **RHI = 0.72105** as its last two rows. |
| `k2t_plane_mid.png` | `60/T`, `80/T` | 50 → 80 s (2 times) | TOP, T 16 → 33 °C | 27 °C contour drawn, 320 segments |
| `k2t_plane_hot.png` | `60/T`, `80/T` | 50 → 80 s (2 times) | hot-aisle plane normal, T 16 → 33 °C | the vertical cut at y = 2.90 m, the mid hot aisle, spanning the row; 27 °C contour, 256 segments |
| `k2t_plane_mid_velocity.png` | `60/U`, `80/U` | 50 → 80 s (2 times) | TOP, \|U\| 0 → 1.5 m/s | the 1.5 m/s top clamps a measured room maximum of 1.599 m/s at t = 80 (`Tspan`) |
| `k2t_streamlines.png` | `60/U`,`80/U`,`60/T`,`80/T` | 50 → 80 s (2 times) | ISO, T 16 → 33 °C | 60 seed points on a 10 × 6 grid over the four tiles; the count is asserted before integration |

## Two things drawn as projections, and said so

* **On the TOP panels** the cut is at z = 1.0 m and the tiles are at z = 0, so in an
  orthographic view looking down the cut sits between the camera and the tiles and
  hides them completely. The floor and tile outlines are therefore drawn **in the
  cut's own plane, as a plan projection of their footprint**. They mark where the
  tile is in x and y, which is what they mark at z = 0. The ceiling return sits
  above the cut and is drawn at its true height.
* **On `k2t_plane_hot.png`** the cut is at y = 2.90 m and the cabinets at
  y = 1.2 → 2.3 m, i.e. behind the field. The row is drawn as an **elevation outline
  2 mm in front of the cut** — four cabinet footprints, the room outline, the four
  tile footprints and the four return openings, each at its true x and z. Painting
  grey blocks there would cover the hot aisle, which is exactly where this panel's
  physics is.

## The camera set

TOP is orthographic looking down with **+y up in the frame**, which puts the cold
aisle at the foot and the hot aisle at the head — and **which side is cold is read
from the mesh, not assumed**: `render_k2t_panels.assert_cold_aisle_is_low_y` reads
the `tile` and `return` patch face centres (measured: `tile` y 0.63 → 1.17,
`return` y 2.63 → 3.17, rack row y 1.20 → 2.30) and refuses before any camera is
pointed if the cold side is not the low-y side. ISO is the three-quarter view from
the cold-aisle side. The order's **FRONT** camera is not used: none of the twelve
figures is an along-the-row view, and the hot-aisle cut seen from the end of the row
would be edge-on and blank.

## Colour bar titles

`T (degC)` and `U (m/s)`. The degree sign and the vertical bar are **not in the
measured-renderable glyph set** of this box's ParaView 5.11.2 font
(`demo3d_render_common.SAFE_CAPTION_CHARS`, `KNOWN_DROPPED_GLYPHS`), so `°C` is
spelled `degC` and `|U|` is spelled `U`, rather than shipping a bar whose title has
silently lost characters.
