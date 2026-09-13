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
| `k2t_ride_through.png` | inlet temperature of each of the four racks against time, ASHRAE A1 recommended 27 °C and allowable 32 °C drawn | `K2bU3R3_D59/postProcessing/T_rack{0..3}_in_mdot/0/surfaceFieldValue.dat` |
| `k2t_2d_vs_3d.png` | hottest rack inlet against time: the 3-D room against the 2-D slice, to the slice's own end at 44.0 s | `K2bU3R3_D59` (max over the four racks) and `K2bU3_L025/postProcessing/T_rack_in_mdot` |
| `k2t_dp_history.png` | module Δp through the whole transient record, the registered 42 → 112 s averaging window shaded | `K2h_L3/postProcessing/dp_tile/{0,10}/surfaceFieldValue.dat`, 18,950 steps, t = 0.0059 → 111.998 |
| `k2t_TMean_field.png` | time-averaged temperature on the y–z aisle plane | `K2h_L3` at t = 110, committed render |
| `k2t_p_rghMean_field.png` | time-averaged `p_rgh` — **the graded field**: `G-DPBAR` is its area average over `tile` minus over `return` | `K2h_L3` at t = 110, committed render |
| `k2t_UMean_field.png` | time-averaged velocity on the same plane, same camera | `K2h_L3/110/UMean`, rendered here by `render_extra_panels.py` |
| `k2t_mesh.png` | the **coarse** level's mesh, per the owner's ParaView rule | `K2f_L1`, 58,368 cells, committed render |

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

**FINDING, reported and not worked around.** `render_k2h_l3.py:325` writes the
caption fragment *"mean over simulated 42 to <t> s ; S-WINDOW registered 42 to 112"*
as a **constant**, not as a property of the field it was handed. It is true of
`TMean`, `p_rghMean` and `UMean` and **false of any instantaneous field or any
steady case** driven through the same function. An instantaneous `T` panel for this
folder was **deleted rather than shipped** for that reason, and so were two panels
re-rendered from the steady `K2f_L3`.
