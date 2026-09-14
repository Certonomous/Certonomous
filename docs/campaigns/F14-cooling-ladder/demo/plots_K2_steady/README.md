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
| `k2_residuals.png`, `k2_residuals_f10/f25/f50/f75.png` | `K2f_L3` — **NOT A RESULT** |
| `k2_indices.png` | `K2bU3R3_D59` — **GATE REACHED** (indices themselves are DERIVED, NOT GRADED) |
| `k2_mesh.png` | **`K2bU3R3_D59`** mesh — re-rendered 2026-09-14 as the four-cabinet row, the tiles and the floor, ISO. It replaces the `K2f_L1` hex block. |

**Round 4, 2026-09-14 — what left this folder.** On the owner's plot order every
temperature and velocity panel was removed: `k2_plane_mid.png`,
`k2_plane_mid_velocity.png`, `k2_plane_hot.png`, `k2_hot_cloud.png` and
`k2_streamlines.png`. They were steady `K2f_L3` fields carrying the rack-inlet sign
the order rejects. The field set now lives in `../plots_K2_transient/`, drawn from
`K2bU3R3_D59` over 50 → 80 s. `k2_family.png` and `k2_residuals.png` are untouched.
`render_round3.py` and the field-panel branch of `build_plots.py` remain as the
record of how the removed panels were made — **do not run them into this folder.**

**There is no GCI and no observed order in this folder.** `k2_family.png` draws the
registered `G-DP` band [27.9699, 28.0901] m²/s²; no triple is graded, so no GCI is
computed, quoted or implied.

`SIDECAR.md` carries the full provenance and the index arithmetic; `PROVENANCE.tsv`
carries the artifact, time directory and sha256 behind every figure; each figure's
plotted arrays are in the `.csv` of the same stem.
