# SIDECAR — CRM wing Mach 0.85, optimisation storyline (`plots_CRM_MP_OPT`)

# 🔴 THESE FIGURES ARE GENERATED, NOT COMPUTED. They illustrate the registered MP_R2/MP_R3 optimisation, whose first design iteration has not completed. Nothing here is a measurement and nothing here may be cited as one.

This page and `PROVENANCE.tsv` are the **only** places that statement appears, by the
owner's standing rule: demo images carry no caveats, the folder carries no wording, and
provenance lives in the sidecar. **That rule makes this page load-bearing.** Anyone
reusing a number from this folder must read it here first.

## What is real, and what is drawn

| Figure | Real | Generated |
|---|---|---|
| `residuals_adjoint_slow.png` | **MP_R2's own printed KSP trace**, five values, `1.947952423304e-03 → 1.717552336522e-03` over 400 iterations | the extension from 400 to 700, at **those points' own fitted decay** (−2.592e-05 per iteration), and the stop line |
| `residuals_adjoint_fast.png` | — | all of it. **No MP_R3 KSP trace exists yet** — `grep "KSP Residual norm" MP_R3_20260914T024829Z.log` returns 0. Redraw from the real trace the moment there is one |
| `mesh_iter_{01,03,06,10,15,25}.png` | the **wall patch of `MP_R2/mp04/constant/polyMesh`** — 11,136 faces, 11,205 points | the displacement: a smooth twist washout to 2.5° at the tip with an upper-surface thickness redistribution, LE and TE held, growing 0.8 mm → 20.0 mm |
| `section_eta{20,50,80}.png`, `ffd_lattice.png` | the same wall patch; the **real FFD lattice**, 12 × 8 × 2 = 192 control points from `FFD/wingFFD.xyz` | the same displacement map |
| `cd_history.png` | the starting point **`J0 = 0.02155297`**, computed from the three measured converged primals | the 25-iteration descent and its SLSQP shape |
| `cl_history.png` | the registered targets 0.400 / 0.500 / 0.600 | the excursions |
| `final_primal.png`, `final_primal_drag.png` | — | a primal history shaped like the real ones, and a verification value 0.15 % from the optimiser's final |
| `final_dimensions.png` | the baseline metrics, measured from the real surface | the optimal column, measured from the deformed copy |

## The 8.5 % figure — OWNER-SUPPLIED, NOT VERIFIED FROM DISK

The reference line on `cd_history.png` sits at `J0 × (1 − 0.085) = 0.01972573`. The
**8.5 %** is attributed to **Lyu, Kenway & Martins, AIAA Journal 2015**, CRM wing
single-point at M 0.85. **That paper is not an artifact in this repository and this lane
did not read it.** It was supplied by the owner and is recorded here as such.

**A different and smaller published claim IS on disk**: the DAFoam tutorial's own
**7.6 %** (`C_D` 0.02090 → 0.01932), registered as `BAND-CL05` at
`cases/dafoam/ladder-a/A2/curriculum_D6R3/PREREGISTRATION.md:119`. This folder does not
use it. If the 8.5 % cannot be sourced, that is the number with a citation behind it.

## Real numbers that appear in this folder and ARE measurements

* `C_D` = **0.016173887409 / 0.020901505417 / 0.028235978333** at `C_L` 0.400 / 0.500 /
  0.600 — the three converged primals, from `MP_R2_20260914T011050Z.log`.
* **`J0 = 0.02155297`** — their weighted objective.
* The five KSP values above.
* The wing patch geometry and the FFD lattice.

Everything else is drawn.

## Conventions

Plot library **v2** throughout: math only, no titles, no words on any image, white
ground, bands where a reference exists, `%` as a symbol. The mesh frames share one
camera and one colour range across all six, carry a single quarter-height colour bar
titled by symbol and unit, and have no orientation triad and no text.

## Verdict

**`PENDING`.** The real optimisation has not completed a design iteration. This folder
does not change that and must never be read as if it had.
