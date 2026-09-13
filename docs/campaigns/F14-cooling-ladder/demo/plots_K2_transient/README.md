# K2 transient, supply ride-through — demo plot folder

Built 2026-09-13 from the K2h and K2b run trees with **zero solver compute**,
under plot library **v2**: math only on the figures, one limit line `T_lim = 27 °C`,
and ParaView panels that are white-ground, triad-free and carry no text at all.
Regenerate with `python3 build_plots.py`,
`xvfb-run -a pvpython render_extra_panels.py` and
`xvfb-run -a pvpython ../render_K2_field_panels.py`.

| File | Verdict of its source |
|---|---|
| `k2t_dp_history.png` | `K2h_L3` — **PASS** (`DPbar` 27.981013 in [27.9699, 28.0901]) |
| `k2t_TMean_field.png` | `K2h_L3` — **PASS** |
| `k2t_p_rghMean_field.png` | `K2h_L3` — **PASS** (this is the graded field) |
| `k2t_UMean_field.png` | `K2h_L3` — **PASS** |
| `k2t_ride_through.png` | `K2bU3R3_D59` — **GATE REACHED** |
| `k2t_2d_vs_3d.png` | `K2bU3R3_D59` **GATE REACHED** against `K2bU3_L025`, the 2-D slice |
| `k2t_mesh.png` | `K2f_L1` mesh — the coarse level, per the ParaView rule |
| `k2t_plane_mid.png`, `k2t_plane_mid_velocity.png` | `K2h_L3` — **PASS** (time-averaged, window on the caption) |
| `k2t_plane_t110.png` | `K2h_L3` — **PASS** (instantaneous, t = 110 s on the caption) |
| `k2t_plane_hot`-class aisle panels | re-rendered here caption-free, replacing the committed copies |
| `k2t_hot_cloud.png`, `k2t_temporal_family.png` | **PENDING — the series and the second time-step run do not exist.** Placeholders, marked "run in progress". Do not show as results. |

**There is no GCI and no observed order in this folder**: `K2h_L1` and `K2h_L2` do
not exist and the pre-registration forbids a mixed steady / time-averaged triple.
The graded mean covers 42 → 110 s, **97.1 %** of the registered window.

`SIDECAR.md` carries the full provenance and says why the ride-through is drawn
from the K2b room rather than from K2h; `PROVENANCE.tsv` carries the artifact, time
directory and sha256 behind every figure.
