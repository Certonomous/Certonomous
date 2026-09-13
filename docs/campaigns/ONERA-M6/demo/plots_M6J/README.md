# ONERA M6 — demo plot folder

Thirteen figures, built 2026-09-13 from the M6J run tree with **zero solver compute**.
Regenerate with `python3 build_plots.py` (matplotlib figures) and
`scripts/render_openfoam_3d_paraview.py` (mesh and surface pressure) and
`xvfb-run -a pvpython render_field_panels.py` (the seven field panels).

| File | Verdict of its source |
|---|---|
| `m6_cp_stations.png` | `M6J_L1` — **GATE FAIL** |
| `m6_family.png` | all three levels — **GATE FAIL** |
| `m6_forces.png` | `M6J_L1` — **GATE FAIL** |
| `m6_residuals.png` | `M6J_L1` — **GATE FAIL** |
| `m6_surface_pressure.png` | `M6J_L1` — **GATE FAIL** |
| `m6_mesh.png` | `M6J_L3` mesh — **GATE FAIL** (the coarse level, per the ParaView rule) |

`GATE FAIL` is the registered B1 Cp band of 0.050 being missed, not a broken run.

**There is no GCI and no observed order in this folder.** `m6_family.png` draws the
registered band; the pre-registration forbids an order or a GCI from a single-grid
validation. See `SIDECAR.md` for the full provenance, `PROVENANCE.tsv` for the
artifact, time directory and sha256 behind every figure, and the `.csv` beside each
figure for the arrays that were plotted.
