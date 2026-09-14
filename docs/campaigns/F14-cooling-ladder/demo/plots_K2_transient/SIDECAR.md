# SIDECAR — K2 TRANSIENT demo plot folder (`plots_K2_transient`)

Built 2026-09-13 from REAL series on disk by `build_plots.py` and
`render_extra_panels.py` in this folder. **Zero solver compute.** Figure names follow
`docs/plot_orders/README_PLOT_ORDERS.md` section C. Arrays are beside each figure as
`.csv`; `PROVENANCE.tsv` carries the path, time directory and sha256 of every
artifact each figure read.

**No verdict word and no band annotation is printed on any matplotlib image**
(owner correction, 2026-09-13). The ParaView panels carry the caption their own
committed instrument mandates.

## The verdict of every source

| Source | Verdict | Where it is recorded | sha256 |
|---|---|---|---|
| `K2h_L3` — 664,848 cells, transient `buoyantBoussinesqPimpleFoam`, graded at t = 110 | **PASS** — `DPbar` **27.981013405397942 m²/s²** inside the pre-registered `G-DPBAR` band **[27.9699, 28.0901]** | `verification/runs/F14-cooling-ladder/K2h_runs/GRADE.K2h_L3.json` | `e10f036942fa2d4e3e46ee757059145fb039d32bf11d89097febf5daa5834a1d` |
| `K2bU3R3_D59` — 137,000 cells, 3-D four-rack room, t = 80 | **GATE REACHED** — DAMPS, ratio **0.420 ≤ 0.5** | `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59/K2bU3R3_GRADE.txt` | `2491254f2b1d799f9273eaf28158bbfec165ecb74e45690a67a9dcd02330e23b` |
| `K2bU3_L025` — 11,600 cells, the 2-D slice of the same module | the 2-D arm of the same K2b-U3 comparison | `docs/campaigns/F14-cooling-ladder/K2bU3_RESULTS.md` | — |
| `K2f_L1` — 58,368 cells, coarse mesh (the mesh panel only) | mesh shown per the ParaView rule | — | — |

Two disclosures ride with the `PASS` and are repeated here rather than left in the
grade file: the graded mean covers **42 → 110 s, 97.1 % of the registered 70 s
window** (the solver writes only on `writeInterval` boundaries and 112 is not one);
and **there is NO triple, NO observed order and NO GCI** — `K2h_L1` and `K2h_L2` do
not exist and §3 forbids a mixed steady / time-averaged triple outright.

## Why the ride-through is drawn from `K2bU3R3_D59` and not from `K2h_L3`

The orders ask `k2t_ride_through.png` for **inlet temperature per rack against time**.
`K2h_L3` **does not emit that**: its only per-write function objects are `dp_tile`
and `dp_return`, and it writes fields at t = 0, 10 and 110 only. `K2bU3R3_D59` is the
one run in this territory that writes a **per-rack inlet temperature series**
(`T_rack0..3_in_mdot`, 400 samples over 0 → 80 s, mass-flow-weighted patch averages
from the run's own function objects), so the ordered figure is drawn from it and the
source is named on this page rather than swapped silently. `K2h_L3`'s own transient
record is `k2t_dp_history.png`.

## Per figure

| Figure | What it is | Source |
|---|---|---|
| `k2t_ride_through.png` | inlet temperature of each of the four racks against time, the single limit T_lim = 27 °C drawn | `K2bU3R3_D59/postProcessing/T_rack{0..3}_in_mdot/0/surfaceFieldValue.dat` |
| `k2t_2d_vs_3d.png` | hottest rack inlet against time: the 3-D room against the 2-D slice, to the slice's own end at 44.0 s | `K2bU3R3_D59` (max over the four racks) and `K2bU3_L025/postProcessing/T_rack_in_mdot` |
| `k2t_dp_history.png` | module Δp through the whole transient record, the registered 42 → 112 s averaging window shaded | `K2h_L3/postProcessing/dp_tile/{0,10}/surfaceFieldValue.dat`, 18,950 steps, t = 0.0059 → 111.998 |
| `k2t_TMean_field.png` | time-averaged temperature on the y–z aisle plane | `K2h_L3` at t = 110, committed render |
| `k2t_p_rghMean_field.png` | time-averaged `p_rgh` — **the graded field**: `G-DPBAR` is its area average over `tile` minus over `return` | `K2h_L3` at t = 110, committed render |
| `k2t_UMean_field.png` | time-averaged velocity on the same plane, same camera | `K2h_L3/110/UMean`, rendered here by `render_extra_panels.py` |
| `k2t_mesh.png` | the **coarse** level's mesh, per the owner's ParaView rule | `K2f_L1`, 58,368 cells, committed render |
| `k2t_plane_mid.png` | `TMean` on the **horizontal** plane at rack mid-height, z = 1.0 m, captioned with the **measured averaging window** | `K2h_L3` at t = 110 |
| `k2t_plane_mid_velocity.png` | `UMean` magnitude on the same plane, same window | `K2h_L3` at t = 110 |
| `k2t_plane_t110.png` | **INSTANTANEOUS** `T` at the last written time, captioned with that time and with the words "NOT a time average" | `K2h_L3` at t = 110 |
| `k2t_plane_t10.png` | **INSTANTANEOUS** `T` at t = 10 s, the same horizontal plane and the same colour window, so the pair with `k2t_plane_mid.png` shows what the averaging removed | `K2h_L3` **decomposed** tree at t = 10 (`processor0..3/10/T`) |
| `k2t_indices.csv` | operator indices per rack — inlet and outlet temperature, RCI high, capture index, recirculation, rack rise — recomputed on the graded transient fine level | `K2h_L3/110/TMean`, patch averages on `rack{0..3}_{in,out}` |
| `k2t_indices_room.csv` | room-level numbers — supply, return, room rise, RTI, hottest inlet and which rack, rack-to-rack spread | `K2h_L3/110/TMean`, patch averages on `tile` and `return` |

The last three were drawn by `../render_K2_field_panels.py`, which renders BOTH K2
folders in one run so the colour windows are genuinely shared with the steady
folder: **T 289.00 to 301.00 K**, **U 0.0378 to 0.9820 m/s**, 2nd/98th percentile
over both cases' planes, printed on every caption with the words *ends clamped*.
Planted colour controls measured **87.2x**, **68.7x** and **87.0x** against a
constant array, on a floor of 8x.

**The averaging window on the two mean panels is read, not typed.** It comes from
`GRADE.K2h_L3.json`'s own accumulator block: covered start **41.992 s** (measured,
earlier than the registered 42 because `fieldAverage` adds the whole `deltaT` of
the step during which it activates), covered end **110.0 s**, `totalTime`
**68.0082742316576 s** over `totalIter` **11507**. The instantaneous panel says
**t = 110 s** and says outright that it is not an average.

The 3-D room's inlets end at **19.3 / 21.9 / 21.8 / 19.4 °C** and never approach the
27 °C line; the ride-through figure shows the rise and its arrest, not a breach.

## Ordered figures that could NOT be produced from disk

* **`k2t_hot_cloud.png`** (iso-surface volume above 27 °C per write) — **no such
  series is emitted** by either run, and only three time directories exist for
  `K2h_L3`, so the volume cannot be recovered per write after the fact. Drawn
  through the library's registered `pending=True` path: ordered axes and labels with
  a **"run in progress"** mark and no data. **A placeholder, not a result.**
* **`k2t_temporal_family.png`** (crossing time at two time steps) — **the second
  time-step run does not exist.** `K2h_L1` and `K2h_L2` were never run and the K2b
  slice family varies cell size, not `deltaT`. Same registered placeholder.
* **`k2t_plane_t60.png`, `k2t_plane_t120.png`** — `K2h_L3` writes fields at
  t = 0, 10 and 110 only. There is no t = 60 and no t = 120 on disk, so neither panel
  can be rendered from the run that was actually made.

## A note on the ParaView captions, and a finding

`k2t_mesh.png`, `k2t_TMean_field.png` and `k2t_p_rghMean_field.png` are the
**committed** output of
`verification/runs/F14-cooling-ladder/K2h_runs/render_k2h_l3.py`, copied here
unmodified. `k2t_UMean_field.png` was rendered here by `render_extra_panels.py`,
which drives that file's own `fig_mean_field` — with its planted colour control
(measured spread ratio **134.7x** against a constant-array negative arm, floor 8x)
and its stamp guard — and proves the run tree unchanged afterwards.

`../render_K2_field_panels.py` builds every caption from the field's own time for
exactly this reason, which is why the instantaneous panel could be shipped from it
when it could not be shipped through `fig_mean_field`.

**FINDING, reported and not worked around.** `render_k2h_l3.py:325` writes the
caption fragment *"mean over simulated 42 to <t> s ; S-WINDOW registered 42 to 112"*
as a **constant**, not as a property of the field it was handed. It is true of
`TMean`, `p_rghMean` and `UMean` and **false of any instantaneous field or any
steady case** driven through the same function. An instantaneous `T` panel for this
folder was **deleted rather than shipped** through that function, and so were two
panels re-rendered from the steady `K2f_L3`. Both were then produced correctly by
`../render_K2_field_panels.py`, which derives its caption from the field it is
handed rather than from a constant.

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
* **`k2t_mesh`, `k2t_TMean_field`, `k2t_p_rghMean_field` and `k2t_UMean_field` are
  re-rendered here caption-free** rather than copied from `render_k2h_l3.py`. The
  constant-caption finding recorded above is therefore no longer carried by any
  image in this folder: the averaging window lives on this page, not on the
  picture, so it cannot be wrong on a panel it does not describe.
* **No residual-evolution frames exist for this folder**: `K2h_L3` writes no
  `solverInfo` series, only `dp_tile`/`dp_return`. The steady folder carries the
  residual series for this module.

### The instantaneous pair comes from two different times

`k2t_plane_mid.png` is the window mean over the registered 42 → 112 s window,
written at t = 110. `k2t_plane_t10.png` is the instantaneous field at **t = 10 s**,
which is **before** that window: it is a settling instant, not a sample of the
window the mean covers, and it is here because round 3 asks that the instantaneous
and the averaged panel not be the same instant. `k2t_plane_t110.png` remains the
instantaneous field at the last written time, inside the window. The reconstructed
tree of `K2h_L3` holds only t = 0 and t = 110, so t = 10 was read from the run's own
decomposed tree; the reader was made to prove it by the 12.16 K spread it reported
at that time (288.844 to 301.000 K) and by the planted colour control at 83.2x.

### The operator indices on the graded transient fine level

`k2t_indices.csv` and `k2t_indices_room.csv` are computed from `110/TMean` — the
mean over the registered window — by area average on the run's own patches. **This
run carries no mdot-weighted inlet function objects** (its `postProcessing` holds
`dp_tile` and `dp_return` only), so the patch average on `rack{i}_in` is the
definition used, which is the same definition the K2b table's inlet column was
cross-checked against.

Two honest caveats belong beside these numbers:

* The rack outlet patches are `fixedValue 301 K` in this case, so the per-rack rise
  is 12.000 K **by construction** and `RTI` inherits that denominator. RTI here is
  therefore a statement about the return temperature, not an independently computed
  rack rise.
* The rack inlet patches are `zeroGradient`, so the inlet temperatures ARE computed.
  They read 15.8500 to 15.8505 °C against a 15.850 °C supply: in this run essentially
  **no warm air reaches the rack inlets**. That is a measurement, not a blind zero —
  the same field spans 288.957 to 301.000 K over the room, and 223,077 of its 664,848
  cells are above 289.01 K.
