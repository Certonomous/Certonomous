# OUR MRF RUSHTON CASE IN THE FIGURE LAYOUT OF Reid et al. (2025) — COMPLETE CHECKLIST

Every figure and every table in Reid, Rossi, Cottini & Benassi (2025),
arXiv:2508.03176, enumerated **from the paper itself, front to back**, with our
case's version beside it. **The denominator is 27 figures (1–25, A1, A2) and 3
tables — 30 items — and every one has a row below.** A row we cannot fill says so
and says why; there are no silent gaps.

**NO SOLVER RAN FOR ANY OF THIS.** It is post-processing of
`verification/runs/navier_class/MRF/R2/ET8000/{coarse,medium,fine}/8000/`, which
were on disk already. Figures: `figures/`. Scripts:
`cases/navier_class/MRF/paper_parity_{setup.sh,extract.py,figures.py,planes.py}`
and `digitise_reid2025_fig16.py`.

**Instrument check (CLAUDE.md rule 3):** a planted perturbation of `1.234e-03` was
written into the fields and recovered by all three readers used here — the
volume-average reader, the profile-`k` reader and the profile-velocity reader — to
within `1e-17`. The readers were shown able to see a non-zero before their zeros
were believed.

---

## THE TWO NUMBERS THAT GIVE THE SET ITS MEANING

> **Our fine-level `Np = 4.382` is 17.3 % to 21.8 % BELOW Reid's band of 5.3–5.6,
> and 2.6 % BELOW the thickness-corrected Beshay (2001) measurement at our own
> tank ratios, 4.50. BOTH ARE TRUE AND THEY ARE DIFFERENT TANKS.**

**And the zone is not the cause, on two independent readings**, both printed on
that same panel: Reid's own Fig. 12 has `Np` **rising** through our 1.20 D zone,
so the zone-size mechanism predicts the wrong sign; and our own turbulence
production sits on the **blade tips with no ring on the MRF interface**
(`figures/fig19_production_impeller_plane.png`), which is what their interface
artefact would look like if we had it. The two readings come by different routes —
one from their figure, one from our fields.

This sentence is printed on the power-number figure itself
(`figures/fig06_global_parameters.png`), not only here, because it is the single
thing a reader is most likely to misread. Reid's tank differs from ours in three
ratios at once — baffle width `0.100 D` against our `0.300 D`, blade thickness
`0.010 D` against our `0.0400 D`, `T/D` 2.903 against 3.000 — and reports **no
measured power number at all**. Beshay's small rig differs in **one** ratio and
was **measured with a strain-gauge torquemeter**. Full reading:
`verification/campaign/MRF_PAPER_REGISTRATION_REID2025.md`.

**The graded verdict is `NOT A RESULT`** — the fine level is not iteratively
converged and the triple is `DIVERGENT` at observed order −0.297. Every number in
this set is therefore an **ungraded** value, and none of it is an accuracy claim.

---

## Our headline numbers

| quantity | coarse | medium | fine | Reid 2025 fine (Zone 1, 1.10 D) |
|---|---|---|---|---|
| cells | 154,715 | 601,696 | 2,418,780 | 5,760,000 |
| base cell (mm) | 10.00 | 6.28 | 3.90 | 4 |
| min cell (mm) | 0.78 | 0.45 | 0.27 | 0.25 |
| **Np** | 4.194 | 4.281 | **4.382** | **5.49** |
| **agitation index Ig (%)** | 14.90 | 14.80 | **14.65** | **13.33** |
| **turbulence intensity u'/Utip (%)** | 4.63 | 5.37 | **5.83** | **6.34** |
| turbulence intensity u'/Û (%) | 31.07 | 36.28 | 39.79 | — (their definition is ambiguous; see note 3) |
| k̄/Utip² | 3.22e-03 | 4.33e-03 | 5.10e-03 | ≈6.0e-03 implied |
| mean wall y+ | 59.5 | 39.7 | **25.9** | **4.1** |
| liquid volume (m³) | 0.020936 | 0.020929 | 0.020931 | — |
| impeller torque, pressure share | 99.65 % | 99.87 % | **99.98 %** | — |

---

## THE CHECKLIST — 30 of 30 rows

| # | their item | what it shows | our status | our figure / value |
|---|---|---|---|---|
| 1 | **Fig. 1** | tank and impeller dimensions | **DONE** — ours beside theirs, both to scale | `figures/fig01_geometry_and_mrf_zone.png` |
| 2 | **Fig. 2** | example hex-dominant grid, side and top | **DONE** — cell centres in a one-cell slab, coloured by local cell size; not a rendered mesh, and labelled as such | `figures/fig02b_mesh_slabs.png` |
| 3 | **Fig. 3** | k-ω SST convergence, residuals and quantities | **DONE** | `figures/fig03_convergence_history.png` |
| 4 | **Fig. 4** | velocity profiles at 5 cm, three meshes | **DONE** at the matched station `r/D = 0.538`, and separately at their absolute 5 cm | `figures/fig04_velocity_profiles_rD0538.png`, `figures/fig04d_velocity_profiles_r5cm_absolute.png` |
| 5 | **Fig. 5** | TKE profile at 5 cm, three meshes | **DONE** | `figures/fig05_tke_profile.png`, left panel |
| 6 | **Fig. 6** | k-ε convergence | **NOT AVAILABLE** — no k-ε solve exists for this case; only k-ω SST was run, and running one is a new registration and new compute | — |
| 7 | **Fig. 7** | νt for both models, horizontal and vertical planes | **PARTIAL** — our νt on both planes, **k-ω SST only**; the k-ε half is unavailable for the reason in row 6 | `figures/fig07_nut_planes.png` |
| 8 | **Fig. 8** | radial velocity at 5 and 7 cm, both models | **PARTIAL** — both radii, three meshes, **k-ω SST only** | `figures/fig08_radial_velocity_two_radii.png` |
| 9 | **Fig. 9** | TKE at 5 cm, both models against LDA | **PARTIAL** — ours against the digitised Wu & Patterson points, **k-ω SST only** | `figures/fig09_tke_vs_lda.png` |
| 10 | **Fig. 10** | TKE on two horizontal planes | **DONE** — `k/Utip²` at `2z/W = ±0.35`, the paper's own planes | `figures/fig10_tke_horizontal_planes.png` |
| 11 | **Fig. 11** | the five MRF zone sizes | **PARTIAL** — their five drawn to scale with **our single 1.20 D × 2.00 W zone** and the blade swept volume; we have solved one zone, not five | `figures/fig11_zone_sizes.png` |
| 12 | **Fig. 12** | Np, Ig, I against MRF zone | **DONE as far as one zone allows** — ours across three meshes beside their five zones, with the two governing numbers printed on the panel | `figures/fig06_global_parameters.png` |
| 13 | **Fig. 13** | velocity profiles at 5 cm against zone | **PARTIAL** — their layout, our three meshes at `r/D = 0.538`; one zone, not five | `figures/fig13_velocity_profiles_zone.png` |
| 14 | **Fig. 14** | velocity at 6 cm against zone | **PARTIAL** — same, at `r/D = 0.645`; the third station `r/D = 0.753` is plotted too, which the paper reports in text only | `figures/fig14_velocity_profiles_6cm.png`, `figures/fig04b_velocity_profiles_rD0645.png`, `figures/fig04c_velocity_profiles_rD0753.png` |
| 15 | **Fig. 15** | velocity contours 0.3–1.5 m/s with the MRF boundary | **DONE** — both planes, their clip range, our zone boundary drawn | `figures/fig15_velocity_contours.png` |
| 16 | **Fig. 16** | TKE at 5 cm against zone, with Wu & Patterson LDA | **DONE** — ours, their Zone 1 curve and the LDA points on one axis | `figures/fig05_tke_profile.png`, right panel |
| 17 | **Fig. 17** | high turbulence intensity zones above 20 % | **DONE** — impeller-plane map with the MRF boundary and the 5, 6, 7 cm probe points | `figures/fig17_high_turbulence_intensity.png`, left |
| 18 | **Fig. 18** | I > 20 % volume against zone | **PARTIAL** — the **volume fraction** is computed for all three meshes; the zone comparison needs five zones we have not solved | `figures/fig17_high_turbulence_intensity.png`, right |
| 19 | **Fig. 19** | production term G in the impeller plane | **DONE** — `G = 2 νt S:S` built from `grad(U)`; `turbulenceFields(G)` refuses under bare `postProcess` and the substitute definition is printed on the figure | `figures/fig19_production_impeller_plane.png` |
| 20 | **Fig. 20** | MRF zone thickness effect on velocity | **NOT AVAILABLE** — one thickness solved (2.00 W); the paper compares 1.55 W against 3.1 W | — |
| 21 | **Fig. 21** | MRF zone thickness effect on TKE | **NOT AVAILABLE** — same reason | — |
| 22 | **Fig. 22** | mixing probes and initialisation sphere | **NOT AVAILABLE** — no passive-scalar study exists for this case | — |
| 23 | **Fig. 23** | concentration index Cnorm at the probes | **NOT AVAILABLE** — needs the scalar run in row 22 | — |
| 24 | **Fig. 24** | global normalised concentration Ctank | **NOT AVAILABLE** — same | — |
| 25 | **Fig. 25** | tracer volume evolution, mixing time | **NOT AVAILABLE** — same | — |
| 26 | **Fig. A1** | blade angular sensitivity, velocity | **NOT AVAILABLE** — one frozen-rotor blade position solved; the position dependence is a disclosed ungated uncertainty in `MRF_R1_PREREGISTRATION.md` §4 | — |
| 27 | **Fig. A2** | blade angular sensitivity, TKE | **NOT AVAILABLE** — same reason | — |
| 28 | **Table 1** | mesh sizes and y+ | **DONE** | `figures/fig02_mesh_and_yplus.png`, `figures/fig07_yplus_per_patch.png`, `MESH_TABLE_OURS.json` |
| 29 | **Table 2** | Np, Ig, I across the mesh family | **DONE** | headline table above, `figures/fig06_global_parameters.png` |
| 30 | **Table 3** | mixing-probe coordinates | **NOT APPLICABLE** — it is the probe list for the passive-scalar study of rows 22–25, which we have not run; there is nothing for our case to have | — |

**Tally: 30 rows. 14 DONE, 6 PARTIAL (each says what is missing and why), 9 NOT
AVAILABLE, 1 NOT APPLICABLE.**

Two figures of our own that the paper has no counterpart for, kept because they
carry the verdict: `figures/fig08_np_grid_convergence.png` (the Roache triple,
with `DIVERGENT` and `NOT A RESULT` stamped on the axes) and
`figures/fig09_zone_sensitivity.png` (their zone curve with our 1.20 D zone marked
on it, which is what refutes the zone-size explanation of our `Np`).

---

## Reading notes — these belong in text, not printed inside the images

1. **Station convention.** Their `r = 5 cm` is `r/D = 0.538`, about one blade width
   outside their blade tip. **Our blade tip is at exactly `r = 5 cm`**, so their
   absolute radius is our tip circle, not a discharge station. Every comparison
   uses the matched `r/D = 0.538` → `r = 5.38 cm`; the absolute 5 cm profile is
   plotted separately and labelled as the tip circle.
2. **Sampling.** Profiles: nearest-cell values at 36 azimuths × 101 heights,
   circumferentially averaged 0° to 350° in 10° steps, exactly as the paper does.
   Nearest-cell, **not** interpolated, which is why our curves are stepped where
   theirs are smooth. The shaded band is the **azimuthal standard deviation over
   the 36 samples** — an uncertainty channel the paper does not report. Planes:
   nearest-cell on a 420 × 420 grid with any sample further than 1.5 local cell
   sizes from a cell centre masked out, which is what draws the solid bodies.
3. **Turbulence intensity is ambiguous in the paper.** Its eq. 19 normalises by the
   mean velocity; its Table 2 values only reconcile with its own Fig. 16 if the
   normalisation is the **tip speed**. Both readings are computed and both are
   reported; the tip-speed one is used in the figures, and that choice is ours, not
   theirs.
4. **Digitisation.** The Wu & Patterson LDA points and the paper's Zone-1 curve are
   **digitised exactly from the PDF's vector path coordinates**, not from pixels
   and not by eye, with the axis calibration taken from the tick-mark coordinates
   in the same content stream. The reader's own control: every recovered error bar
   has a half-width of **15.0 ± 0.4 %** of its centre — the Wu & Patterson TKE
   uncertainty the paper states. The per-zone bar values on their Fig. 12 are
   **printed data labels** on the bars, so they are **printed, not digitised**, and
   carry rounding only, ±0.05.
5. **y+ is a design difference, not a defect.** They resolve the wall (`y+ ≈ 4.13`);
   we use wall functions targeting the log-law band. Our mean is 25.9 on the fine
   level and **falls** with refinement — the direction a wall-function mesh is not
   supposed to want. Recorded, not explained away.
6. **An observation of ours the paper would want.** Their central warning is that
   larger MRF zones **manufacture** turbulence at the interface. At our 1.20 D
   zone, `figures/fig19_production_impeller_plane.png` shows production
   concentrated at the **blade tips**, with no ring of production on the interface
   — consistent with their finding that the artefact grows with zone diameter, and
   our zone is at the small end of their range.
7. **The torque is 99.98 % pressure** at the fine level. Any explanation of the
   power-number deficit has to act through the **pressure field**; the viscous
   contribution to `Np` is 0.00078 against a deficit of about 1.1, so the `y+`
   difference in note 5 cannot be a direct cause.
