# K2 transient, the four-rack room — demo plot folder

**Round 4, 2026-09-14.** The whole transient set now comes from **`K2bU3R3_D59`** —
the 137,000-cell three-dimensional four-rack room, `buoyantBoussinesqPimpleFoam`,
an 80 s record — with **zero solver compute**. Two figures are the exception and are
named as such below.

Regenerate in this order:

```
python3 build_plots.py                              # the seven matplotlib figures
xvfb-run -a pvpython render_k2t_panels.py           # the five ParaView panels + the mesh
```

`build_plots.py` writes `PROVENANCE.tsv`; `render_k2t_panels.py` rewrites it keeping
every row it did not draw, so the renderer must run second.

## The window, said once and repeated on every figure

The order is **50 → 80 s**. `K2bU3R3_D59` writes on `writeInterval 20` and carries
**no `fieldAverage`** — there is no `TMean`, no `UMean` and no
`uniform/fieldAveragingProperties` in the tree. So a "window mean" here is the
**mean of the two written times 60 and 80**, and it is called that everywhere. It is
not a 30 s time average and no figure implies one. `k2t_residuals.png` and
`k2t_ride_through.png` are not window means at all: they are the **whole 0 → 80 s
record**, as the order asks.

## The twelve files

| File | Source | What it is |
|---|---|---|
| `k2t_mesh.png` | `K2bU3R3_D59` mesh | surface mesh of the four cabinets, the tiles and the floor, ISO |
| `k2t_residuals.png` | `K2bU3R3_D59` solver log | initial residuals of $U_x,U_y,U_z,T,p_{rgh}$ against $t$, 995 steps |
| `k2t_dp_history.png` | **`K2h_L3`** | module Δp through the K2h record — **as pushed, not redrawn** |
| `k2t_ride_through.png` | `K2bU3R3_D59` | per-rack inlet temperature against time, `T_lim` and `T_sup` drawn |
| `k2t_inlet_profiles.png` | `K2bU3R3_D59` | window-mean inlet temperature against height, $R_1 \dots R_4$ |
| `k2t_indices.png` | **`K2h_L3`** | RCI / CI / $f_{rec}$ per rack, RTI and the 100 % line — **the existing numbers, reused as ordered** |
| `k2t_rack_dT.png` | `K2bU3R3_D59` | window-mean rack outlet minus inlet, against the 12 K line |
| `k2t_airflow_balance.png` | `K2bU3R3_D59` | tile supply, rack demand and bypass per rack from the patch fluxes |
| `k2t_plane_mid.png` | `K2bU3R3_D59` | window-mean T at rack mid-height, 27 °C contour, TOP |
| `k2t_plane_hot.png` | `K2bU3R3_D59` | window-mean T on the vertical plane through the hot aisle |
| `k2t_plane_mid_velocity.png` | `K2bU3R3_D59` | window-mean \|U\| on the mid-height plane, TOP |
| `k2t_streamlines.png` | `K2bU3R3_D59` | 60 streamlines seeded over all four tiles, coloured by T, ISO |

Each figure's plotted arrays are in the `.csv` of the same stem where the order asks
for one. `PROVENANCE.tsv` carries, per figure, the run, the artifact, the time
directory, the window, the patches, the camera, the colour range and the sha256.
`SIDECAR.md` carries the verdicts and the two disclosures that ride with this set.

## The verdict of every source

| Source | Verdict | Where it is recorded |
|---|---|---|
| `K2bU3R3_D59` — 137,000 cells, 80 s | **GATE REACHED** — DAMPS, ratio 0.420 ≤ 0.5 | `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59/K2bU3R3_GRADE.txt` |
| `K2h_L3` — 664,848 cells, t = 110 | **PASS** — `DPbar` 27.981013 in [27.9699, 28.0901] | `verification/runs/F14-cooling-ladder/K2h_runs/GRADE.K2h_L3.json` |

**There is no GCI and no observed order in this folder.** No triple is graded here.

## Figures removed in this round

`k2t_2d_vs_3d.png`, `k2t_hot_cloud.png`, `k2t_p_rghMean_field.png`,
`k2t_plane_t10.png`, `k2t_plane_t110.png`, `k2t_temporal_family.png` and their CSVs
and colour controls. The three `K2h` field panels are the ones the order calls
"K2h fields with the inlet sign wrong"; the two `pending` placeholders were never
results. `render_extra_panels.py` and `render_instant_t10.py` remain in the folder
as the record of how those panels were made — **do not run them into this folder**,
they write the removed K2h panels back.
