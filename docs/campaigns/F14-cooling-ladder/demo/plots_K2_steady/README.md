# K2 steady, the four-rack row — demo plot folder

Built 2026-09-13 from the K2f / K2g / K2b run trees with **zero solver compute**,
under plot library **v2**: math only on the figures, one limit line `T_lim = 27 °C`,
and ParaView panels that are white-ground, triad-free and carry no text at all.
Regenerate the matplotlib figures with `python3 build_plots.py`; three ParaView panels are the committed output of
`../render_K2f_rackset_paraview/render_k2f_rackset.py` and three more come from
`xvfb-run -a pvpython ../render_K2_field_panels.py`.

| File | Verdict of its source |
|---|---|
| `k2_family.png` | L1/L2 comparator **REFUSED**; L3 (t = 803 of 2000) **NOT A RESULT** |
| `k2_residuals.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_inlet_profiles.png` | `K2bP_C3b_noplant` — pilot control twin, **ungraded** |
| `k2_indices.png` | `K2bU3R3_D59` — **GATE REACHED** (indices themselves are DERIVED, NOT GRADED) |
| `k2_plane_hot.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_streamlines.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_mesh.png` | `K2f_L1` mesh — the coarse level, per the ParaView rule |
| `k2_plane_mid.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_plane_mid_velocity.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_hot_cloud.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_map_setpoint.png`, `k2_map_airflow.png`, `k2_envelope.png`, `k2_cost.png` | **PENDING — the eight sweep solves do not exist.** Placeholders, marked "run in progress" on the image. Do not show as results. |

**There is no GCI and no observed order in this folder.** `k2_family.png` draws the
registered `G-DP` band [27.9699, 28.0901] m²/s²; no triple is graded, so no GCI is
computed, quoted or implied.

`SIDECAR.md` carries the full provenance and the index arithmetic; `PROVENANCE.tsv`
carries the artifact, time directory and sha256 behind every figure; each figure's
plotted arrays are in the `.csv` of the same stem.
