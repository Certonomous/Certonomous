# ACT B — asset manifest (INTERNAL; not a customer surface)

Purpose: the control room grabs files from this directory during filming. Two
figures answer to the name "the pressure figure" and only one of them is the
act's asset. This file says which. It is internal, so it names files plainly.

Last reviewed 2026-09-01, and every asset below was REGENERATED that day after
the settling column was changed from a constant into a measurement. Regenerate
any asset by running its generator; the generators are listed beside each
entry.

## WHAT CHANGED ON 2026-09-01, AND WHY TWO DIFFERENT THINGS HAPPENED

Both are about the same quantity, "movement": how much the lift was still
shifting when a calculation stopped. Do not read them as one event.

**The result sheet's Movement column was DEFECTIVE and is fixed.** It was a
hard-coded dictionary carrying a caption that described a measurement. Four of
its five values were smaller than the quantity the caption defined; at
Cμ = 0.20 it printed 9e-06 against a measured 3.383e-05, understating by 3.8x.
The values also failed the caption's own "rounded up" rule, and they matched
neither the 4,000-iteration window nor the 1,000-iteration one, so they cannot
be explained as the shorter window. The column is now computed at render time
from each case's force history. The dictionary was NOT replaced with better
constants: a constant wearing a measured caption is the defect, and better
constants would have left it in place for the next person who changes a run.

**The lift figure was NOT wrong and moved anyway.** Asset 5 always computed its
error bars at render time and they were honest for the window it used, the
final 1,000 iterations. It now uses the final 4,000, so its bars are LARGER.
That is a convention the lab tightened on itself, not a defect being repaired:
where two defensible definitions exist and one flatters the result, take the
one that reports more movement. The range over the longer window is also the
only choice that cannot hide an excursion inside it.

**One reader, not three.** The sheet's column, the panel embedded in the sheet,
and the standalone lift figure are the same quantity and now come from one
implementation, `verification/runs/JF1_jet_flap/jf1_display_numbers.py`. Two of
them previously carried separate copies of the same dictionary, which is how
one number becomes two numbers that disagree.

**The clipping percentages rounded an adverse figure DOWN, and now widen
outward.** The sheet stated the turbulence-clipping range under a plain `:.0f`,
which printed the worst row's measured 97.325% as "97" — the same flattering
shape as the Movement column repaired above, one significant figure further
down. The printed pair is a BOUND, not two measurements, so it is now widened
outward: the low end floors and the high end ceilings, giving "81 to 98%". A
bound looser outward is always a true statement about the runs; one tighter
inward is a claim the measurements do not support. The companion-mesh figure is
a POINT value, not a bound, so ceiling it would have overstated 99.41% as 100%;
it carries the digit instead and reads "99.4%". Page count and the page-two word
count were re-measured after the change and are unmoved at 2 and 428.

**Wall spacing on the sweep grid now reports the worst of the five, not the
one rendered.** Asset 3 stated "largest 0.256", which is the Cμ = 0.10
calculation, on a page captioned as the grid all five ran on. The sweep
maximum is 0.398, at the strongest blowing, and the page now states the rise
from 0.191 with the slot closed to 0.398 at the strongest jet. The claim that
every wall cell is below the wall-resolved limit was true before and is true
now; what was wrong was the number offered as evidence for it, and it was
wrong in the flattering direction. Anywhere 0.19 appears as this grid's
resolution it is to be read as 0.398.

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
9. `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts_actB/blown_trailing_edge_result_sheet.pdf` — the result sheet, **2 pages** (measured 2026-09-01: `pdfinfo` reports 2; page two carries 428 words). It grew from 1 page to 2 by ADDING candour, not padding: page two is the disclosure — the turbulence-clipping census on all five conditions, the "not checked" statement, and the figure notes. **Do not cut disclosure to restore a 1-page sheet.** Check `pdfinfo` after any edit to `make_actB_sheet.py` and expect 2; a jump to 3 is the thing to catch (generator `artefacts_actB/make_actB_sheet.py`, then `pdflatex` twice).

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
