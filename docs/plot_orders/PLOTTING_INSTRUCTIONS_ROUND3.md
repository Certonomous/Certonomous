<!-- Sanaa, 2026-09-14 ~04:35Z, recorded byte-exact by the chief; if Sanaa's own upload of this file lands later, hers replaces this copy -->
# PLOTTING INSTRUCTIONS, ROUND 3: EVERY FIGURE, EVERY TASK

Install `plot_library_v2_1.zip` first (axis labels now read `n [iteration]`, `k [design step]`, `t [s]`), then apply the items below and rebuild all six folders. Titles are set in the task, not on the image; the image carries symbols only. Every folder must carry the CSV behind each figure and the provenance line.

## Rules that apply everywhere
1. **Axes say what they count.** Solver histories: `n [iteration]`. Design histories: `k [design step]`. Time: `t [s]`. Angles: `β [deg]`, `α [deg]`. Never a bare `n`, `k` or `[deg]`.
2. **Legends name the source with a superscript, never a word.** The lab's curve is the bare symbol (`C_p`, `Y'`); the experiment is `C_p^exp`, `Y'^exp`; a published value is `^ref`. No "CFD", no "lab", no "tunnel", no "their".
3. **Reference lines carry their value**: `C_D^exp = 0.247`, `T_lim = 27 °C`, `J^ref = 0.01972`. A reference line belongs only on the quantity it refers to.
4. **ParaView panels**: white ground, no triad, one quarter-height colour bar titled by symbol and unit, camera framed on the object, nothing else on the image. Panels of the same quantity across conditions share one camera and one colour range.
5. **Section and profile plots** draw points in geometric order (by arc length or by angle about the section midpoint), never in mesh-point order.
6. **Placeholders**: a figure whose data do not exist yet is not drawn; the task shows its slot as pending.

## Data center (`plots_K2_steady`, `plots_K2_transient`)
| Figure | Fix |
|---|---|
| `k2_inlet_profiles.png` | Drawn from the pilot slice, not the row. Redraw from the four-rack row: four rack inlet profiles `T_in(z)` labelled `R_1 … R_4`, the `T_lim = 27 °C` line, no hot-aisle curve. |
| `k2_family.png` | The quantity is the module pressure drop, not "y": pass `quantity=r"$\Delta p$", unit="[m2/s2]"`; band label `[27.97, 28.09]`. |
| `k2_plane_mid.png`, `k2_plane_hot.png`, `k2_plane_mid_velocity.png` | These are vertical sections through one rack pitch; the task now titles them so. If the four-rack row fields exist, add the horizontal mid-height plane over the row as a separate figure; do not relabel these as horizontal. |
| `k2_streamlines.png` | Reads as a yellow sheet over one block. Seed 40 to 60 lines at the tiles, colour by `T`, camera showing the row and both aisles. |
| `k2_hot_cloud.png` | Fine as the iso-surface over the module; add the rack outlines of the whole row if the row fields exist. |
| `k2_map_setpoint`, `k2_map_airflow`, `k2_envelope`, `k2_cost` | Not drawn until the eight sweep solves exist. |
| `k2t_plane_mid.png`, `k2t_plane_t110.png` | Vertical sections, titled so in the task; the instantaneous and time-averaged fields must come from different times (they look identical). |
| `k2t_dp_history.png` | Good. |
| `k2t_ride_through.png`, `k2t_2d_vs_3d.png` | Good; legends `R_1 … R_4`, `3D`, `2D`. |

## ONERA M6 (`plots_M6J`)
| Figure | Fix |
|---|---|
| `m6_family.png` | Y label reads `y [[-]]`: pass `quantity=r"$\overline{|\Delta C_p|}$"`, no unit. |
| `m6_cp_stations.png` | Good. |
| `m6_p_oblique.png`, `m6_p_upper_top.png`, `m6_mach_eta065/090.png`, `m6_mesh.png`, `m6_mesh_surface.png`, `m6_geometry.png` | Good. |
| `m6_forces.png`, `m6_residuals.png` | Good; axes now `n [iteration]` after the library update. |

## DrivAer (`plots_DRIVAER`)
| Figure | Fix |
|---|---|
| `drivaer_family.png` | Drop the shaded band `[0.2426, 0.2569]` (a published interval we do not cite); keep `C_D^exp = 0.247`. |
| `drivaer_umag_wake.png` | Colour bar overlaps the field and the frame cuts the wake. Frame the whole cross-section one metre aft, car silhouette visible, colour bar outside the field. |
| `drivaer_streamlines.png` | A few faint lines on a skewed cut. Orthographic side view on the symmetry plane, body centred, 40 to 60 streamlines seeded upstream over the body height, coloured by `|U|`. |
| `drivaer_cd_history*.png`, `drivaer_p_*.png`, `drivaer_umag_symmetry.png`, `drivaer_umag_midheight.png`, `drivaer_mesh_*.png`, `drivaer_residuals.png` | Good. |

## SUBOFF (`plots_SUBOFF`)
| Figure | Fix |
|---|---|
| `suboff_yprime_vs_beta.png`, `suboff_nprime_vs_beta.png` | X label `β [deg]`; legend `Y'` for the lab and `Y'^exp` for the tow tank (currently "CFD" and a bare `Y'`), same for `N'`; the ±4 % band labelled `±4 %`. |
| `suboff_yprime_split_vs_beta.png`, `suboff_nprime_split_vs_beta.png` | X label `β [deg]`; legend `Y'^hull`, `Y'^sail`; add the total `Y'` as a third line. |
| `suboff_p_side_bp12.png`, `suboff_p_top_bp12.png` | The colour bar reads `|U|`, the title in the task says surface pressure: these are surface velocity. Re-render as wall pressure `p`, or confirm the field and the task title changes to velocity. |
| `suboff_umag_mid_bp12.png`, `suboff_wake_*.png` | Good. |
| `suboff_streamlines_bp12.png`, `suboff_q_bp12.png` | Still to come. |
| `suboff_yprime_history.png`, `suboff_nprime_history.png`, `suboff_residuals.png` | Good; axes `n [iteration]`. |

## CRM (`plots_CRM_SP`, `plots_CRM_MP`, `plots_CRM_MP_OPT`)
| Figure | Fix |
|---|---|
| `cd_history.png` | X axis `k [design step]`; legend `J`, `J^ref = 0.01972`. |
| `cd_per_condition.png` | X axis `k [design step]`; drop the dashed `C_D^ref = 0.01972` line (it is the weighted objective's reference, not a per-condition drag). |
| `section_eta20/50/80.png` | Order the section points around the profile before drawing; as pushed the polyline crosses the section. Legend `baseline`, `optimised` as symbols: `z/c` baseline solid, optimised dashed. |
| `ffd_lattice.png` | Draw the wing planform under the lattice; offset the baseline and deformed markers; label axes `x [m]`, `y [m]`. |
| `mesh_quality_through_design.png` | Good; x axis `k [design step]`; the two re-mesh markers at 7 and 22 stay. |
| `reduction_breakdown.png` | Good; bar labels as symbols: `shape`, `twist`, `trim`; `C_{D,w}`, `C_{D,i}`, `C_{D,v}`. |
| `residuals_adjoint_slow.png`, `residuals_adjoint_fast.png` | Axes `n [iteration]`; the task says the fast arm reaches 1e-7 near 220 and two decades more by 300, which is what is drawn. |
| `final_primal_drag.png` | Bar labels `J^opt`, `C_D^primal`. |
| `final_dimensions.png` | Good; x axis `η`. |
| `crm_trim_cd.png`, `crm_trim_alpha.png`, `crm_decomposition.png`, `crm_cd_history.png`, `crm_cl_history.png`, `crm_residuals.png` | Good. |
| `crm_mesh_wing.png`, `crm_mesh_symmetry.png`, `crm_p_cl0x.png`, `p_opt_cl0x.png` | Good; keep one camera and one colour range across the six pressure panels. |
