# ONERA M6 — demo plot folder

Eighteen figures, built 2026-09-13 and re-drawn 2026-09-14 from the M6J run tree with
**zero solver compute**,
under plot library **v2**: math only on the figures, and ParaView panels that are
white-ground, triad-free and carry no text at all.
Regenerate with `python3 build_plots.py` (matplotlib figures) and
`xvfb-run -a pvpython render_field_panels.py` (every ParaView panel).

| File | Verdict of its source |
|---|---|
| `m6_cp_stations.png` | `M6J_L1` — **GATE FAIL** |
| `m6_family.png` | all three levels — **GATE FAIL** |
| `m6_forces.png` | `M6J_L1` — **GATE FAIL** |
| `m6_residuals.png` | `M6J_L1` — **GATE FAIL** |
| `m6_mesh.png` | `M6J_L3` mesh — **GATE FAIL** (the coarse level, per the ParaView rule) |

`GATE FAIL` is the registered B1 Cp band of 0.050 being missed, not a broken run.

**There is no GCI and no observed order in this folder.** `m6_family.png` draws the
registered band; the pre-registration forbids an order or a GCI from a single-grid
validation. See `SIDECAR.md` for the full provenance, `PROVENANCE.tsv` for the
artifact, time directory and sha256 behind every figure, and the `.csv` beside each
figure for the arrays that were plotted.

---

## ROUND 4 — 2026-09-14

The owner's figure-by-figure note, executed. Nothing was solved and no number moved;
what changed is the drawing, and one figure now draws twice as many rows.

* **The 983,040-cell level is `M6J_L1`**, not `M6J_L3` — `M6J_L3` is the 15,360-cell
  coarse level. The field panels were already on the fine level; the banding was
  per-cell colouring plus drawn cell edges, and both are gone from the pressure
  panels.
* `m6_p_upper_top.png` is a **planform**: camera along −z, parallel, whole wing with
  a 5 % margin. `m6_p_oblique.png` shares its colour window.
* The two Mach panels carry a **fixed 0 to 1.4** scale with five round ticks and the
  **sonic line M = 1 in black**, on a frame cut to the section's own chord.
* `m6_cp_stations.png` now draws **all twelve graded rows** — upper *and* lower at
  each of the six stations. **Seven of the twelve are inside the 0.050 band and five
  are not**; the misses are upper surfaces. No solution in this lab has twelve of
  twelve, and "all 12 rows inside B1" is the registered PASS *rule*, not a result.
  `SIDECAR.md` carries the row-by-row table.
* `m6_geometry.png` is the **plain** wing surface — no field and no wireframe.
* `PROVENANCE_PANELS.tsv` is new: one row per ParaView panel with its case, cells,
  time directory, patch or plane, camera and colour window.
