# OUR MRF RUSHTON CASE, PRESENTED IN THE LAYOUT OF Reid et al. (2025)

Every quantity Reid, Rossi, Cottini & Benassi (2025, arXiv:2508.03176) report,
computed **for our case from our own fields**, figure by figure and table by
table. **No solver ran**: everything here is post-processing of
`verification/runs/navier_class/MRF/R2/ET8000/{coarse,medium,fine}/8000/`.

Where the geometry matches, the paper's value sits beside ours. Where it does
not, the figure says **different dimensions, no match expected** and no band is
registered. The full reading is
`verification/campaign/MRF_PAPER_REGISTRATION_REID2025.md`.

**Instrument check (CLAUDE.md rule 3):** a planted perturbation of `1.234e-03`
was written into the fields and recovered by all three readers used here — the
volume-average reader, the profile-`k` reader and the profile-velocity reader —
to within `1e-17`. A zero from a reader not shown able to see a non-zero is not
evidence, so the readers were shown. `PAPER_PARITY_RESULTS.json` → `planted_zero`.

---

## The headline numbers

| quantity | coarse | medium | fine | Reid 2025 fine (Zone 1, 1.10 D) |
|---|---|---|---|---|
| cells | 154,715 | 601,696 | 2,418,780 | 5,760,000 |
| **Np** | 4.194 | 4.281 | **4.382** | **5.49** |
| **agitation index Ig (%)** | 14.90 | 14.80 | **14.65** | **13.33** |
| **turbulence intensity u'/Utip (%)** | 4.63 | 5.37 | **5.83** | **6.34** |
| turbulence intensity u'/Û (%) | 31.07 | 36.28 | 39.79 | — |
| k̄/Utip² | 3.22e-03 | 4.33e-03 | 5.10e-03 | ≈6.0e-03 implied |
| mean wall y+ | 59.5 | 39.7 | **25.9** | **4.1** |

**Verdict on the graded row: `NOT A RESULT`** — the fine level is not iteratively
converged and the triple is `DIVERGENT` at observed order −0.297. Under the
superseded band `[4.0, 6.0]` our 4.38 read as inside; under the band that now
stands, `[5.3, 5.6]`, it is **17.3 % to 22.0 % low and clearly outside**.

---

## Figure-by-figure, table-by-table

| their item | what it shows | our status | our figure |
|---|---|---|---|
| Fig. 1 | tank and impeller dimensions | **DONE**, ours beside theirs | `figures/fig01_geometry_and_mrf_zone.png` |
| Fig. 2 | example hex-dominant grid | **NOT AVAILABLE** — a mesh render, not a quantity; the mesh table below carries the numbers | — |
| Fig. 3 | k-ω SST convergence | **DONE** | `figures/fig03_convergence_history.png` |
| Fig. 4 | velocity profiles at 5 cm, three meshes | **DONE** at matched `r/D = 0.538`, and separately at their absolute 5 cm | `figures/fig04_velocity_profiles_rD0538.png`, `figures/fig04d_velocity_profiles_r5cm_absolute.png` |
| Fig. 5 | TKE profile at 5 cm, three meshes | **DONE** | `figures/fig05_tke_profile.png` (left panel) |
| Fig. 6, 7 | k-ε convergence and νt | **NOT AVAILABLE** — no k-ε solve exists for this case | — |
| Fig. 8, 9 | model comparison, velocity and TKE | **PARTIAL** — k-ω SST arm only, for the same reason | `figures/fig04*`, `fig05*` |
| Fig. 10 | TKE on horizontal planes | **NOT AVAILABLE** — a field render; the profiles carry the same information quantitatively | — |
| Fig. 11 | the five MRF zones | **PARTIAL** — we have one zone, 1.20 D × 2.00 W | `figures/fig01_geometry_and_mrf_zone.png` |
| **Fig. 12** | **Np, Ig, I against zone** | **DONE as far as one zone allows** — ours across three meshes beside their five zones | `figures/fig06_global_parameters.png` |
| Fig. 13, 14 | velocity vs zone at 5 and 6 cm | **PARTIAL** — one zone; our profiles at three radii | `figures/fig04b`, `fig04c` |
| Fig. 15 | velocity contours | **NOT AVAILABLE** — field render | — |
| **Fig. 16** | **TKE at 5 cm vs zone, with Wu & Patterson LDA** | **DONE** — ours, their Zone 1 and the LDA points, all three on one axis | `figures/fig05_tke_profile.png` (right panel) |
| Fig. 17, 18 | volume with I > 20 % | **PARTIAL** — the volume fraction is computed and in the JSON; the iso-surface render is not | `PAPER_PARITY_RESULTS.json` |
| Fig. 19 | interface artefact detail | **NOT AVAILABLE** — needs the zone sweep | — |
| Fig. 20, 21 | zone thickness effect | **NOT AVAILABLE** — one thickness solved | — |
| Fig. 22–25, Table 3 | passive-scalar mixing times | **NOT AVAILABLE** — no scalar transport run; needs a fresh registration and fresh compute | — |
| Fig. A1, A2 | blade angular sensitivity | **NOT AVAILABLE** — one frozen-rotor position solved | — |
| **Table 1** | **mesh sizes and y+** | **DONE** | `figures/fig02_mesh_and_yplus.png`, `figures/fig07_yplus_per_patch.png` |
| **Table 2** | **Np, Ig, I across the mesh family** | **DONE** | `figures/fig06_global_parameters.png` |
| — (ours, not theirs) | grid convergence of Np, with the Roache verdict on the figure | **DONE** | `figures/fig08_np_grid_convergence.png` |
| — (ours, not theirs) | their zone-diameter curve with our zone marked on it | **DONE** | `figures/fig09_zone_sensitivity.png` |

---

## Reading notes that belong in text, not on the images

- **Station convention.** Their `r = 5 cm` is `r/D = 0.538`, about one blade width
  outside their blade tip. **Our blade tip is at exactly `r = 5 cm`**, so their
  absolute radius is our tip circle. Comparisons use the matched station
  `r/D = 0.538` → `r = 5.38 cm`; the absolute 5 cm profile is plotted separately.
- **Sampling.** Nearest-cell values at 36 azimuths × 101 heights, circumferentially
  averaged from 0° to 350° in 10° steps exactly as the paper does. Nearest-cell,
  not interpolated — which is why our curves are stepped where theirs are smooth.
  The shaded band on each profile is the **azimuthal standard deviation over the
  36 samples**, an uncertainty channel the paper does not report.
- **Turbulence intensity.** Their eq. 19 normalises by the mean velocity; their
  Table 2 values only reconcile with their own Fig. 16 if the normalisation is the
  **tip speed**. Both readings are computed and both are reported; the tip-speed
  one is used in the figure.
- **Digitisation.** The Wu & Patterson points and the paper's Zone-1 curve are
  digitised **exactly from the PDF's vector path coordinates**, not from pixels
  and not by eye, with the axis calibration taken from the tick-mark coordinates
  in the same content stream. The reader's own control: every recovered error bar
  has a half-width of **15.0 ± 0.4 %** of its centre — the Wu & Patterson TKE
  uncertainty the paper states. The bar values on their Fig. 12 are **printed data
  labels**, so they are printed, not digitised, and carry rounding only.
- **y+ is a design difference, not a defect.** They resolve the wall (`y+ ≈ 4`);
  we use wall functions targeting the log-law band. Our mean is 25.9 on the fine
  level and falls with refinement, which is the direction a wall-function mesh is
  not supposed to want — recorded, not explained away.
