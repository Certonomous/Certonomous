# SIDECAR — K2 STEADY demo plot folder (`plots_K2_steady`)

Built 2026-09-13 from REAL fields on disk by `build_plots.py` in this folder.
**Zero solver compute.** Figure names follow `docs/plot_orders/README_PLOT_ORDERS.md`
section B. Arrays are beside each figure as `.csv`; `PROVENANCE.tsv` carries the
path, time directory and sha256 of every artifact each figure read.

**No verdict word and no band annotation is printed on any matplotlib image**
(owner correction, 2026-09-13). The three ParaView panels carry the caption their
own committed instrument mandates — see the note at the foot.

## The verdict of every source

| Source | Verdict | Where it is recorded | sha256 |
|---|---|---|---|
| `K2f_L1` 58,368 cells, t = 3000 | comparator **REFUSED (exit 2)** — the planted-cycle control failed, so nothing was graded | `verification/runs/F14-cooling-ladder/K2f_runs/K2f_STAGE2_GATE.json` | `a36805169793bde68158fd10965fa0b91a46b8196a07e8e1986c3a258dad65a2` |
| `K2f_L2` 196,992 cells, t = 3000 | same comparator, same refusal | (same file) | (same) |
| `K2f_L3` 664,848 cells, **t = 803 of a registered endTime 2000** | **NOT A RESULT** — rule 4 clause 3 and clause 5 both fail | `verification/runs/F14-cooling-ladder/K2g_runs/autograde.K2f_L3.out` | `0156e9906f69b40d64ec98a03e5f781f6e493a6aae556975a9bb96ce65bcdabd` |
| `K2bU3R3_D59` 137,000 cells, 3-D room, t = 80 | **GATE REACHED** — DAMPS, ratio **0.420 ≤ 0.5** | `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59/K2bU3R3_GRADE.txt` | `2491254f2b1d799f9273eaf28158bbfec165ecb74e45690a67a9dcd02330e23b` |
| `K2bP_C3b_noplant` 46,400 cells, 2-D module, t = 5000 | pilot control twin, **ungraded** (`K2b_PILOT_RESULTS.md`) | — | — |

**The thing this folder must not be allowed to imply.** `K2f_L3`'s `DP_module` at
t = 803 is **28.052139 m²/s², which happens to lie inside the registered band**, and
that is exactly what makes a picture of it dangerous. It is **NOT A RESULT**: the
level stopped at 803 of 2000 on its own registered stop rule R4 and its frozen
comparator refused it at exit 2. Nothing in this folder calls it a PASS.

## The band on `k2_family.png`, stated plainly

**There is no GCI and no observed order on this figure.** The green region is the
**registered `G-DP` band [27.9699, 28.0901] m²/s²**, fixed in
`docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md` §5 before compute and
derived there from p ∈ [1.0, 2.0] on the fixed f1, f2 and r = 1.5. A GCI would need
a CONVERGING triple and there is no graded fine level, so none is computed, quoted
or implied, and no numeric GCI appears anywhere in this folder. The band is drawn
by `act_plots_lib.grid_family(band=…)`.

Plotted values, read through the **frozen** `K2g_runs/foam_patch_reader.area_average`
— the one reader every level of this family is graded through — as
`areaAvg(p_rgh, tile) − areaAvg(p_rgh, return)`:

| level | cells | time | `DP_module` [m²/s²] |
|---|---|---|---|
| L1 | 58,368 | 3000 | 27.189119361484373 |
| L2 | 196,992 | 3000 | 27.729679615659716 |
| L3 | 664,848 | **803** | 28.052139279822118 — **NOT A RESULT** |

L1 and L2 reproduce `K2g_PREREGISTRATION.md` §7's f1 and f2 exactly.

## Per figure

| Figure | What it is | Source |
|---|---|---|
| `k2_family.png` | module Δp on three levels, registered band drawn | the three `p_rgh` files above |
| `k2_residuals.png` | initial residuals Ux, Uz, T, p_rgh on the fine level, target 1e-5 | `K2g_runs/K2f_L3/log.solve`, 803 iterations |
| `k2_indices.png` | RCI high, RTI, capture index, recirculation, per rack, in **%** | `K2bU3R3_D59` rack inlet series + `80/T` on the rack outlet, tile and return patches |
| `k2_plane_hot.png` | temperature on the vertical y–z plane at x = 1.5 m: cold aisle left, rack row centre, hot aisle plume right | `K2f_L3` at t = 803, committed render |
| `k2_streamlines.png` | recirculation over the rack row | `K2f_L3` at t = 803, committed render |
| `k2_mesh.png` | the **coarse** level's mesh, per the owner's ParaView rule | `K2f_L1`, 58,368 cells, committed render |
| `k2_plane_mid.png` | temperature on the **horizontal** plane at rack mid-height, z = 1.0 m | `K2f_L3` at t = 803 |
| `k2_plane_mid_velocity.png` | velocity magnitude on the same plane | `K2f_L3` at t = 803 |
| `k2_hot_cloud.png` | oblique 3-D view, the **300.15 K (27 °C) iso-surface** above the rack row, with the rack block and the room outline | `K2f_L3` at t = 803, 25,228 triangles |

The last three were drawn by `../render_K2_field_panels.py`, which renders BOTH K2
folders in one run so that the colour windows really are shared: measured at the
2nd and 98th percentile over both cases' mid-height planes, **T 289.00 to 301.00 K**
and **U 0.0378 to 0.9820 m/s**, printed on every caption with the words *ends
clamped*. Planted colour controls measured **87.6x** (T) and **68.7x** (U) against a
constant array, on a floor of 8x. `k2_hot_cloud.png` carries an **ink guard**
instead of a colour control, and the reason is structural rather than convenient:
an iso-surface is single-valued in the field that defines it, so a colour control
on it could never pass; what matters there is that the surface is not EMPTY, and
25,228 triangles over 268,672 non-background pixels is what the guard measured.

### `k2_indices.png` — DERIVED, NOT GRADED

These four indices are **not registered quantities and carry no verdict.** They are
computed in `build_plots.py` from measured patch values and stated here so the
arithmetic can be checked:

* supply `T` = area average of `T` on `tile` at t = 80 = **289.000 K (15.85 °C)**
* return `T` = area average of `T` on `return` at t = 80 = **305.579 K (32.43 °C)**
* rack inlet `T` = the last sample of `postProcessing/T_rack<i>_in_mdot` (a
  mass-flow-weighted patch average written by the run's own function object)
* rack outlet `T` = area average of `T` on `rack<i>_out` at t = 80
* **recirculation %** = 100 (T_in − T_supply) / (T_out − T_supply)
* **capture index %** = 100 − recirculation %
* **RCI high %** = 100 [1 − max(T_in − 27 °C, 0) / 5] — the 5 K denominator is the
  index's own definition and is NOT drawn as a second limit anywhere
* **RTI %** = 100 (T_return − T_supply) / mean(T_out − T_in) — one room value,
  drawn on every rack group because it is a room index, not a rack index

Every inlet is well below the 27 °C limit, so RCI high is 100 % on all four racks.
RTI is 138.3 %, i.e. bypass-free and recirculating — consistent with the
recirculation bars of 22–34 %.

*(`k2_plane_mid.png` and `k2_hot_cloud.png` were on this list until 2026-09-13 and
are now rendered — see the table above.)*

## Ordered figures that could NOT be produced from disk

* **`k2_map_setpoint.png`, `k2_map_airflow.png`, `k2_envelope.png`, `k2_cost.png`** —
  the orders' **eight sweep solves (five setpoints, three airflows) DO NOT EXIST in
  the run tree.** No sweep was ever run on this module. Rather than invent curves,
  each file is drawn through the library's own registered `pending=True` path: the
  ordered axes and labels with a **"run in progress"** mark and no data. **These four
  are placeholders and must not be shown as results.**
* **`k2_geometry.png`** — the rack row is `blockMesh`-generated from
  `build_k2f.py`; there is no admitted surface file to show. `k2_mesh.png` is the
  geometry the solver actually saw.

## A note on the ParaView captions, and a finding

`k2_plane_hot.png`, `k2_streamlines.png` and `k2_mesh.png` are the **committed**
output of
`docs/campaigns/F14-cooling-ladder/demo/render_K2f_rackset_paraview/render_k2f_rackset.py`,
copied here unmodified. They carry an in-image caption naming the case, the cell
count and the verdict `NOT A RESULT`. That caption is a **hard guard**
(`demo3d_render_common.assert_stamp` refuses to render a `PASS` or `GATE REACHED`
stamp on either case) and removing it would defeat the guard, so it stays.

**FINDING, reported and not worked around.**
`verification/runs/F14-cooling-ladder/K2h_runs/render_k2h_l3.py:325` writes the
caption fragment *"mean over simulated 42 to <t> s ; S-WINDOW registered 42 to 112"*
as a **constant**, not as a property of the field it was handed. Driving that
function on a steady case or on an instantaneous field therefore produces a picture
whose caption claims a time average that was never taken. Two panels this lane
re-rendered that way from `K2f_L3` (a temperature plane and a velocity plane) were
**deleted rather than shipped**, and an instantaneous-`T` panel for the transient
folder was dropped for the same reason. The `k2_plane_hot.png` that IS shipped here
is the committed `render_k2f_rackset.py` output, whose caption is correct:
*"fields NOT rule-4 complete ; no graded verdict ; NOT A RESULT"*.

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

* **THE MODULE IS THE FOUR-RACK ROW, NOT ONE CABINET — measured, not assumed.**
  `constant/polyMesh/boundary` of BOTH `K2f_L1` and `K2h_L3` carries
  `rack0_in/out … rack3_in/out`: **four racks**, on a 0.6 m pitch, the row spanning
  x = 0.6 → 3.0 m of a 3.6 × 3.5 × 2.7 m room. The y–z aisle panels
  (`k2_plane_hot`, `k2t_*_field`) are a **cross-section THROUGH the row at x = 1.5 m**,
  which is why one cabinet face is what a viewer sees; the whole row is visible in the
  mid-height horizontal planes (`k2_plane_mid`, `k2t_plane_mid`) and in the
  streamline and mesh panels. Nothing needed re-rendering over a wider extent — the
  act should be worded as a four-rack row cut through its middle.
* **ONE LIMIT, and it is the user's: `T_lim = 27 °C`.** Every "recommended",
  "allowable" and every 32 °C line is gone from the figures and from this page.
* **`k2_plane_hot`, `k2_streamlines` and `k2_mesh` are no longer the committed
  `render_k2f_rackset.py` copies.** They are re-rendered here caption-free, which
  also retires the mis-captioned-constant finding for these panels: nothing is
  written on them at all.
