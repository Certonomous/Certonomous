# DrivAer — demo plot folder

Eighteen figures, built 2026-09-13 from the Wolf Dynamics reproduction runs with
**zero solver compute**, under plot library **v2**: math only on the figures, and
ParaView panels that are white-ground, triad-free and carry no text at all. Regenerate with `python3 build_plots.py` and
`xvfb-run -a pvpython render_field_panels.py`.

| File | Verdict of its source |
|---|---|
| `drivaer_cd_history.png`, `drivaer_forces.png`, `drivaer_residuals.png` | `coarse_R1` — **PASS** (G1, G2, G3) |
| `drivaer_p_side.png`, `drivaer_p_top.png`, `drivaer_p_rear.png` | `coarse_R1` — **PASS** |
| `drivaer_umag_symmetry.png`, `drivaer_umag_midheight.png`, `drivaer_umag_wake.png`, `drivaer_streamlines.png` | `coarse_R1` — **PASS** |
| `drivaer_mesh_coarse.png` | `coarse_R1` mesh — the coarse level, per the ParaView rule |
| `drivaer_mesh_fine.png` | `fine_R1` mesh — the solve was **STOPPED**, the mesh stands |
| `drivaer_cd_history_fine.png` | **PENDING** — axes only. Our fine solve was stopped short of `endTime` and its curve is not drawn |
| `drivaer_family.png` | our coarse **PASS** against the fine level's number |

**🔴 The fine level's number on the figures is Wolf Dynamics' published fine value,
`C_D = 0.256412`, not ours** — our own fine solve was **stopped by owner decision**
short of its `endTime` and is not drawn.
The provenance is in `SIDECAR.md`; no image says it. What our run did produce — **879
of 1000 iterations**, last `C_D` 0.2562307, last-100 mean **0.255369**, and its fields
under `processor*/700` and `processor*/800` — is kept and recorded there, marked NOT
PLOTTED. **A run stopped
short of `endTime` fails the completion rule on its face, so no grade can be built
from it however close the number looks.**

**🔴 The coarse result is a REPRODUCTION, not a validation.** Our force output is
byte-identical to Wolf Dynamics' shipped file because the case ran verbatim; that
proves fidelity and corroborates nothing. **There is no GCI and no observed order
in this folder** — two levels are not a triple, and one has not finished.

**The in-house DrivAer `r2` runs are set aside** by Sanaa's 2026-09-13 instruction
and get no panels here: for the record, `r2_coarse` and `r2_medium` both pass M1 and
M2 and both **`GATE FAIL` M3** (50.057 % and 57.907 %), with `r2_medium` the first
DrivAer level this lab has produced inside the wall-function y+ band (layered median
232.0 in [30, 300]) — a mesh-quality finding on our own snappyHexMesh family, which
is a different object from this verbatim reproduction of a published case.

`SIDECAR.md` carries the full provenance, the registered comparands, the open
discrepancy behind the band, how a live run was read without disturbing it, and
what waits on the fine solve landing.
