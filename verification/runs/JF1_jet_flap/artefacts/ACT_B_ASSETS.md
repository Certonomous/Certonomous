# ACT B — asset manifest (INTERNAL; not a customer surface)

Purpose: the control room grabs files from this directory during filming. Two
figures answer to the name "the pressure figure" and only one of them is the
act's asset. This file says which. It is internal, so it names files plainly.

Last reviewed 2026-09-01. Regenerate any asset by running its generator; the
generators are listed beside each entry.

---

## THE ACT'S ASSETS, IN CAPTURE ORDER

Both extensions exist for every figure (`.pdf` vector, `.png` raster). Capture
the `.pdf` unless the control room needs a raster.

1. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_5_mesh_flowfield.pdf` — the real computational grid the flow picture was solved on (generator `plot_jf1_mesh_demo.py`).
2. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_6_mesh_resolution.pdf` — slot-mouth cell count and near-wall spacing, both counted (generator `plot_jf1_mesh_demo.py`).
3. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_7_mesh_forcesweep.pdf` — the O-grid the five lift/pressure calculations ran on; carries the sweep compute line (generator `plot_jf1_mesh_demo.py`).
4. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_8_spanwise_uniformity.pdf` — confirmation that nothing varies across the span (generator `plot_jf1_actB_cp_span.py`).
5. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_1_lift_vs_blowing.pdf` — the headline result: lift against blowing, with the published theory curve (generator `plot_jf1_actB_demo.py`).
6. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_2_chordwise_pressure.pdf` — THE PRESSURE FIGURE. Cp vs x/c, full scale, nothing clipped, upper and lower separated (generator `plot_jf1_actB_cp_span.py`).
7. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_3_flow_field.pdf` — the flow picture, finer mesh, flow-picture only (generator `plot_jf1_actB_demo.py`).
8. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_4_jet_path.pdf` — the jet trajectory (generator `plot_jf1_actB_demo.py`).
9. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts_actB/blown_trailing_edge_result_sheet.pdf` — the one-page result sheet. LENGTH-CRITICAL: it must stay at exactly 1 page; check `pdfinfo` after any edit to `make_actB_sheet.py` (generator `artefacts_actB/make_actB_sheet.py`, then `pdflatex`).

Capture order above follows the arc in the demo standard v2 §2 (geometry and
mesh, then the cheap check, then results). It is read off that arc, NOT off a
captured runbook — if a runbook exists it governs and this list should be
re-ordered to match.

---

## SUPERSEDED — DO NOT CAPTURE

- `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_2_surface_pressure.pdf` — SUPERSEDED by `jet_flap_2_chordwise_pressure.pdf`. Its Cp axis is clipped at +1.15 / −2.6, which cuts off the slot-lip suction (−6.87 at the strongest jet) and the lower-lip peak (+1.589). Kept because it is committed history; never captured.
- `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/jet_flap_2_surface_pressure.png` — same, raster.

The superseded figure was nevertheless re-generated on 2026-09-01 with the
corrected wording, so that no committed file carries the retired claim about the
five calculations differing only in blowing. Superseded is not an excuse to
leave a false sentence on disk.

---

## FILES HERE THAT ARE NOT ACT ASSETS

- `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts/plant_control_2026-08-31.txt` — the mutation/positive-control record for the completion reader. Evidence, not a figure.
- `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts_actB/fig_lift_vs_blowing.pdf` — the small lift-vs-blowing panel embedded INSIDE the result sheet. It is not captured on its own; capturing it alone would show the sheet's figure without the sheet's tables and caveat box.

---

## THE ONE THING THAT MUST NOT DRIFT BACK

The five completed calculations share one grid — the mesh geometry is
byte-identical across all five. They are NOT five settings of one case. Four
were run with the slot open, blowing at different strengths: those four are a
controlled comparison among themselves. The fifth was run with the slot CLOSED
and is a reference, never "the same case with the blowing turned down to zero".
Every asset above states this in plain English. Any regenerated figure that
folds all five into "differ only in blowing" is wrong and must not ship.
