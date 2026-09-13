# DrivAer — published **OpenFOAM** setup ingest (DrivAerML, Ashton et al. 2024/2025)

Status: **INGEST COMPLETE. THIS ONE IS OPENFOAM.** It is our case, our conditions
and our wall-function class. **It is not snappyHexMesh.**
Paper-fetch-class inbound; nothing left the box (rules 7, 8). Not a
pre-registration, freezes no gate, edits no frozen file.

Companion: `PUBLISHED_SETUP_INGEST_ashton_2016.md` (the source Sanaa named —
retrieved, verified, and **STAR-CCM+**, not OpenFOAM).

Why this document exists: the cfd supervisor ruled that §G's requirement is
*"a published **OpenFOAM** setup of that case"*, that Sanaa's naming of Ashton &
Revell was a pointer to where she believed one lived, and that the pointer having
been shown by count not to reach the requirement, going to an actual published
OpenFOAM DrivAer setup satisfies her rule rather than substituting for it. The
ruling is his and is recorded as his; the question goes to Sanaa's desk either way.

---

## 1. TITLE-PAGE VERIFIED (rule 15) — read from a render of the page

| Field | As it appears ON THE PAGE |
|---|---|
| Title | **DrivAerML: High-Fidelity Computational Fluid Dynamics Dataset for Road-Car External Aerodynamics** |
| Authors | **Neil Ashton*** (Amazon Web Services, 60 Holborn Viaduct, London EC1A 2FD); **Charles Mockett, Marian Fuchs, Louis Fliessbach, Hendrik Hetmann, Thilo Knacke, Norbert Schönwald** (Upstream CFD GmbH, Bismarckstraße 10-12, 10625 Berlin); **Vangelis Skaperdas, Grigoris Fotiadis** (BETA-CAE Systems, Kato Scholari, Thessaloniki); **Astrid Walle** (Siemens Energy, Berlin); **Burkhard Hupertz** (Ford Motor Company, Cologne); **Danielle C. Maddix** (Amazon Web Services, Seattle) |
| Footnote | *Now at NVIDIA, Corresponding Author: nashton@nvidia.com, contact@caemldatasets.org |
| Venue / date | **arXiv:2408.11969v2 [physics.flu-dyn], 17 Apr 2025.** "Preprint. Under review." |
| Abstract, in part | "500 parametrically morphed variants of the widely-used DrivAer **notchback** generic vehicle. Mesh generation and scale-resolving CFD was executed using consistent and validated automatic workflows representative of the industrial state-of-the-art." CC-BY-SA. |

**Authorship caveat, stated not smoothed.** **Ashton is an author. Revell is
not.** This is therefore not "Ashton & Revell" either. It is an Ashton DrivAer
paper that *is* OpenFOAM, where the Ashton & Revell papers are not.

PDF/sidecar on disk (outside git, 30 MB, per `docs/LOCATIONS.md`), pointer at
`docs/papers/benchmark_test_cases/ashton_2024_drivaerml.POINTER.md`:
`/home/ubuntu/certonomous-runs/reference_pdfs/benchmark_test_cases/ashton_2024_drivaerml.pdf`,
sha256 `86b8b7803a3d9975acfe0261eaa93fc14c83e2648c6f9f9a32f8ec2972148fe9`.

---

## 2. IS IT OPENFOAM? YES — AND IT IS NOT SNAPPYHEXMESH

Counts over the sidecar:

| Token | Count |
|---|---|
| `OpenFOAM` | **8** |
| **`snappyHexMesh` / `snappy`** | **0** |
| `ANSA` | 12 |
| `cfMesh`, `HEXPRESS` | 0 |

- **Solver: OpenFOAM v2212.** "The open-source software library OpenFOAM (v2212)
  was used to solve the incompressible Navier–Stokes equations via the finite
  volume method" (sidecar L294-295).
- **Mesher: ANSA v24.1.0, HeXtreme algorithm**, hexa-dominant & polyhedral
  (L269-271).

**So the §G requirement is met on the solver and missed on the mesher.** This
does **not** close the gap the supervisor named — *"we have no published snappy
layer recipe for any case in this lab"*. It is the **third** case in a row where
the published setup's mesher cannot express our failure mode: STAR-CCM+'s
independently-extruded prism region (Ashton 2016), PPTC's block-structured grid
with no octree and no level-0 cell, and now ANSA HeXtreme. **The pattern is now
three-for-three and it is a finding about our workflow, not about these cases.**

**But it does something better than close the gap: it makes the gap unnecessary.**
The published layer recipe is stated in **absolute millimetres**, which transfers
into a snappy dictionary directly (§4), and absolute is exactly the mode our
defect lives outside of.

---

## 3. THE SETUP, CLAIM -> SOURCE -> OURS

### 3.1 It is our case, at our conditions

| # | Claim | Source | Ours | Agree? |
|---|---|---|---|---|
| D1 | **DrivAer notchback**, 1:1 **full scale** | Abstract; L221 | Notchback, full scale | **YES** |
| D2 | **U∞ = 38.889 m/s**, rho∞ = 1 kg/m3 | L225, L2849 | **38.889 m/s** (`0/U`), `rhoInf 1` (`system/forceCoeffs`) | **YES — identical** |
| D3 | **Re_L = 7.19e6** on wheelbase **L = 2.786 m** | L225-227 | lRef **2.79** (`forceCoeffs`), nu 1.507e-05 | **YES** |
| D4 | nu | `constant/transportProperties`, dataset | **1.51163e-05** theirs vs **1.507e-05** ours | 0.3% — immaterial, but ours is not theirs |
| D5 | Reference quantities: lref 2.786 (wheelbase), Aref 2.172, forcesCoR (1.4, 0, -0.3176); case-independent lrefRef 2.78618, ArefRef 2.17, forcesCoRRef (1.40009, 0, -0.3176) | `constant/geometryParameter.txt`, retrieved verbatim | lRef 2.79, Aref 2.298, CofR (1.402, 0, -0.3176) — the run_466 varying-ref values | **consistent** (`DATA_PROVENANCE_drivaerml.md`) |

**This is the same case at the same speed.** Ashton 2016 was Estate/Fastback,
smooth underbody, 40% scale, Re_H 1.48e6. DrivAerML is ours.

### 3.2 Mesh and layers — the recipe, verbatim

> "The models were meshed in ANSA version 24.1.0 using the HeXtreme algorithm,
> which generates hexa-dominant & polyhedral meshes. Approximately **160 million
> cells** were generated in less than an hour and satisfied OpenFOAM quality
> criteria. **The boundary layer mesh was optimised for wall functions, with 7
> layers, a first layer height of 0.75 mm, a total layer height of 12 mm and a
> variable growth rate between 1.2 and 1.4.** The choice of **high y+ mesh vs.
> resolving to the wall** was based on findings from the 2nd AutoCFD workshop,
> where direct comparisons by multiple participants found **only a minor
> difference in results**, with benefits of significantly faster run times."
> — sidecar **L269-275**

Self-consistency check, run here: 0.75 mm x sum(r^i, i=0..6) equals 12 mm at
r = 1.27, inside their stated 1.2-1.4 band. **The three published numbers agree
with each other.**

Also: refinement by **size fields following the geometry and extending
downstream** in wake, underbody and mirrors (L275-277); resolution and topology
tuned by industrial feedback across the AutoCFD series; **"a grid refinement
study is not undertaken"** — stated explicitly (L279-280), so **this recipe
carries no grid-convergence evidence and must never be cited as if it did.**

### 3.3 Wall treatment — **this is the reversal**

> "For the boundary conditions of the turbulence model at solid walls, **a
> formulation based on Spalding's law of the wall is used that is valid for
> arbitrary values of the non-dimensional near-wall spacing y+**." — L1384-1386

**That is `nutUSpaldingWallFunction`, which is what we already run** on `".*"`
in `r2c_medium_blended_R3/0/nut`. The published OpenFOAM DrivAer practice is a
**deliberately wall-functioned, high-y+ mesh**, chosen over wall-resolved on
published workshop evidence that the difference is minor.

**Our wall treatment is not the defect. Ashton 2016's y+ < 1 is not the target
for this case.** §3b of the companion ingest said their recipe reaches the
wall-resolved range and ours does not, and that stands as a true statement about
*that* paper — but the OpenFOAM practice for *our* case deliberately does not,
and it uses our exact wall function.

### 3.4 Turbulence and numerics

| Item | Published | Source | Ours |
|---|---|---|---|
| Approach | **HRLES** — Fuchs/Mockett variant of **DDES** (Spalart et al.), **Spalart-Allmaras** RANS near-wall, **sigma-model (Nicoud)** LES in separated flow, to accelerate the grey-area RANS->LES transition | L297-305 | steady RANS `kOmegaSST` |
| Shielding | **"enhanced protection" (EP)** from Deck & Renard's ZDES, to keep RANS active through the whole boundary layer and avoid **modelled stress depletion** | L305-309 | n/a |
| Solver | **derivative of `pimpleFoam`, OpenFOAM v2212, customised by Upstream CFD**; transient SIMPLE with multiple sub-iterations per step; **enhanced Rhie-Chow** for lower LES dissipation | L1374-1380 | `simpleFoam`, steady |
| Momentum convection | **Travin et al. hybrid blending**: 2nd-order **central** in resolved-turbulence regions, 2nd-order **upwind-biased** elsewhere | L1380-1383 | `bounded Gauss linearUpwind grad(U)` |
| Turbulence convection | 2nd-order upwind-biased on the nu-tilde equation | L1382-1383 | `limitedLinear 1` on k, omega |
| Time integration | **2nd-order implicit Euler** | L1383-1384 | `steadyState` |
| Precision | **double**, IntelMPI | L328-329 | to confirm at registration |

### 3.5 Transient control and the averaging window — the answer to "run transient, time-average"

**They do not fix a window. They detect one.** (L313-324, L1509-1529)

1. **Initial transient** detected from the Cd, Cl and Cs time series by the tool
   **Meancalc**, then truncated from the flow-field average using periodic
   checkpoints; **minimum 25 CTU** used in the detection to avoid premature
   termination on short series.
2. **Stop on statistical accuracy**: run until the 95% CI on Cd reaches
   **±1.5 drag counts** (1 count = ΔCd 0.001) over the transient-free portion.
3. **Hard bracket `40 <= t·U∞/L <= 60` CTU** to bound outliers; **fewer than 5%
   of the 500 cases hit it.**
4. The averaging sample is then **trimmed to the optimal transient-free length by
   a custom OpenFOAM utility** for consistency with the mean integral forces.

Validation runs: case 2a **3.0 s ≈ 42 CTU**; case 2b **3.6 s ≈ 50 CTU**, both
auto-stopped on 2σ(Cd) ≤ 0.0015.

**Time step: Δt = 2e-4 s.** *Derived, not stated directly*: the paper says
"initial tests with a **two times finer** time step of Δt = 1e-4 s showed closer
agreement to experiment" (L2125). The production value is therefore twice that.
Flagged as an inference from an explicit sentence, not a published figure.
At Δt 2e-4, 3.0 s is **15,000 time steps**. Their own caveat, on the record:
the coarser step was "deployed to limit computational cost" and the finer step
agreed better with experiment in the high-CFL underbody region (L2125-2129,
L2422-2423).

### 3.6 Validation against experiment (Hupertz et al. 2021, Ford OCDA DrivAer)

| Case | Source | Cd | Cl | Clf | Clr |
|---|---|---|---|---|---|
| 2a | **Exp.** | **0.255** | 0.087 | -0.023 | 0.111 |
| 2a | **CFD: SRS** | **0.274** | 0.033 | -0.073 | 0.106 |
| 2b | **Exp.** | **0.242** | 0.082 | -0.019 | 0.101 |
| 2b | **CFD: SRS** | **0.267** | 0.039 | -0.064 | 0.103 |
| Δ(2b-2a) | Exp. | -0.013 | -0.005 | 0.004 | -0.010 |
| Δ(2b-2a) | CFD | -0.007 | 0.006 | 0.009 | -0.003 |

Their own words: **"The predicted drag coefficient is higher than experiment by
roughly 20 counts in both simulations"** (L~1950).

**Carry this into any DrivAer gate.** The best published OpenFOAM setup for this
case, at 160 M cells and industrial HRLES, sits **+0.019 to +0.025 in Cd (+7.5%
to +10.3%) above the tunnel**, and gets the Δ between configurations only about
half right (-0.007 vs -0.013). A lab gate that demands better than that of our
own solve is demanding better than the published state of the art.

---

## 4. THE THREE ROWS, ANSWERED

### 4a. LAYERS — **the number Ashton 2016 could not give, DrivAerML gives**

Their recipe is **absolute**, so it converts. Our level-4 surface cell is
**25.0 mm** (blockMesh base 0.400 m, `r2_medium/system/blockMeshDict` hex
(30 50 30) over a 12 m x 20 m x 12 m block; surface `level (4 4)` -> 0.400/2^4).

| Quantity | **DrivAerML (published)** | **Ours (measured/derived)** | Gap |
|---|---|---|---|
| Layers requested | **7** | **5** | 1.4x |
| **First layer height** | **0.75 mm (absolute)** | **5.12 mm** (= 0.5/1.25^4 x 25 mm) | **6.83x TOO THICK** |
| **Total stack height** | **12 mm (absolute)** | **42.0 mm** (= 1.6808 x 25 mm) | **3.50x TOO THICK** |
| Growth rate | 1.2 - 1.4 (variable) | 1.25 requested; **1.265-1.281 achieved** | comparable |
| **Stack in LOCAL CELLS** | **0.480** | **1.6808** | **3.50x** |
| Specification mode | **absolute mm, uniform** | **`relativeSizes true`** — varies per patch | **the defect** |
| Achieved coverage | **not reported** (ANSA writes no post-extrusion table) | **2.50 of 5** coarse, **2.89 of 5** medium | — |

**This is the direct answer the supervisor asked for. Their recipe implies a
stack of 0.480 local cells. Ours is 1.6808 — 3.5x thicker, and thicker than the
cell it grows into. Theirs extrudes because it asks for less than half a cell.
Ours collapses because it asks for more than one.**

And the mechanism is now named precisely: **they specify in absolute
millimetres and we specify relative to the local cell.** A relative stack is
scale-free by construction, so on a level-5 patch (12.5 mm cell) ours silently
becomes a 21 mm stack with a 2.56 mm first layer while theirs stays 12 mm and
0.75 mm everywhere. **Our layer thickness is a function of our refinement level.
Theirs is not.** That is the bug, stated as a property rather than a symptom.

The transfer into snappy is mechanical and needs no invention:
`relativeSizes false; nSurfaceLayers 7; firstLayerThickness 0.00075;
thickness 0.012; expansionRatio ~1.27; minThickness` well below 0.00075.
**Registering that is the supervisor's call, not this lane's.**

### 4b. y+ AND WALL TREATMENT — **the finding reverses**

| | DrivAerML | Ours |
|---|---|---|
| Wall treatment | **wall functions, deliberately high-y+** | wall functions |
| Wall function | **Spalding's law, valid at arbitrary y+** | **`nutUSpaldingWallFunction`** |
| y+ reported | **no numeric value published** | **area-wtd median 153.1** (medium, 47 patches), mean 467.75 coarse, 0 of 47 below 30 |
| y+ **lab-derived**, not published | **≈ 22** | 153.1 (measured) |

The ≈22 is **derived here, not published**: y+ scales linearly with wall distance
at fixed flow, so their first-cell centre (0.375 mm) against ours (2.56 mm) gives
153.1 x 0.375/2.56 ≈ **22.4**. **Labelled derived. It is not a number from their
pages** and must not be re-quoted as one.

**The finding in the companion ingest is reversed for this case.** Our wall
treatment is the published one — same function, same class, chosen on published
workshop evidence. What is wrong is not that we use a wall function; it is that
our **first cell is 6.8x too thick**, which puts our y+ near 153 where the
published recipe sits near the low-to-mid log region. **That is a layer-thickness
defect presenting as a y+ defect**, and fixing 4a fixes both.

### 4c. TRANSIENT — what it costs, published and measured

**Their published cost, and it is OpenFOAM on AWS, which makes it the most
transferable cost figure this lab has ever had for this case:**

> "A typical simulation took around **40 hours on 1536 cores** using Amazon EC2
> **hpc6a.48xlarge** instances (AMD Milan, 96 cores per node)" — L326-328

| | Value |
|---|---|
| Cells | **160 M** |
| Cores x wall | **1536 x 40 h** |
| **Core-hours** | **61,440** |
| **Core-minutes** | **3,686,400** |
| **On our 96-core host** | **640 hours = 26.7 DAYS, per single run** |

Our-rate cross-check (0.13342 core-min per iteration per Mcell from
`RATE_PROBE_96C`, 160 Mcell, 15,000 steps x 5 sub-iterations) gives 1,601,065
core-min = 26,684 core-hours = **0.43x their measured 61,440.** **Our rate
under-predicts their OpenFOAM run by 2.3x**, and the honest reading is that the
shortfall is real work our steady-SIMPLE probe does not contain: a custom
low-dissipation solver, double precision, and an unstated number of PIMPLE
sub-iterations. **For registration, cost from their 61,440 core-hours, not from
our probe.** Our probe is calibrated for steady simpleFoam and is being asked
about something else.

For context, the companion ingest's Ashton 2016 STAR-CCM+ DDES was 35,200
core-hours at 100 M cells. DrivAerML is **1.75x that**, at 1.6x the cells.

---

## 5. WHAT THE DATASET SHIPS, AND WHAT IT DOES **NOT** — read this before anyone cites a dictionary

The HuggingFace dataset `neashton/drivaerml` ships per-run OpenFOAM case
directories. Retrieved at pinned revision
`7a5c0948ce27be709b1116a3a190f806e7a8f79f` (same revision as
`DATA_PROVENANCE_drivaerml.md`), read-only over HTTPS:

| File | sha256 | Bytes |
|---|---|---|
| `openfoam_meshes/run_0/system/controlDict` | `9c6adc45f74c20d2b2a75f176151262bcca5fb2c7fffe47de2d574bac7e44fe8` | 2404 |
| `openfoam_meshes/run_0/system/fvSchemes` | `0d011dfb1804db908dee52128755684dc2e455cc35b9317ea35f6dce3dc9cf4a` | 2017 |
| `openfoam_meshes/run_0/system/fvSolution` | `99c6023e3fd2d970e867b5ae03fb2088eae3781118fff59af65f5f5ccbfa196c` | 2639 |
| `openfoam_meshes/run_0/constant/momentumTransport` | `81181800161c87623a8dd13a564edd50f582f5ab1df60c31a32d807c28a58284` | 1402 |
| `openfoam_meshes/run_0/constant/transportProperties` | `35b406c4aa7ac181aa626a79e07ae5c35e1db3d507bdbb359adb040fc2407e5f` | 1398 |
| `openfoam_meshes/run_0/constant/geometryParameter.txt` | `beacca33889047ead91b664944112736f70b755343e68b57e510c90da88d1662` | 715 |
| `openfoam_meshes/run_0/0/U` | `378f8803bc6a8b922d6785c7855df68a0ab5036b2a49e2a07e075bceca0dbe91` | 5648 |

**THESE ARE A MESH-DELIVERY STUB, NOT THE PRODUCTION SETUP. DO NOT CITE THEM AS
THE PUBLISHED NUMERICS.** The evidence is on their own faces:

- `controlDict`: `application UserSolver`, `endTime 1`, **`deltaT 1`**,
  `writeInterval 1`, `adjustTimeStep off`
- `momentumTransport`: **`model laminar; turbulence off`**
- `fvSchemes`: **`ddtSchemes { default steadyState; }`**, generic
  `bounded Gauss upwind` on k/omega/epsilon/nuTilda — a steady-RANS placeholder
  set, not the Travin hybrid blending of §3.4
- `forceCoeffs`: **`patches ( )` empty**, `CofR (0 0 0)`, `lRef 1`,
  **`magUInf 40`** and `rhoInf 1.204` — all contradicting the paper's own
  38.889 m/s, rho 1, lRef 2.78618, CofR (1.40009, 0, -0.3176)
- `0/U`: 59 patches; road as **`symmetry`**, inlet
  `surfaceNormalFixedValue refValue -40`
- **no `0/nut` at all**, so the Spalding wall function of §3.3 is **not**
  confirmable from the shipped files — only from the paper's prose

**The production numerics are not published.** The solver is a **proprietary
Upstream CFD customisation** of pimpleFoam (§3.4). What the dataset genuinely
publishes is the **mesh** (`constant/polyMesh`), the **geometry reference
quantities** (`geometryParameter.txt`, which *is* authoritative and matches the
paper), and the **force/field data**. The recipe in §3.2-§3.5 comes from the
paper's pages, not from these dictionaries.

Recorded so that nobody downstream reads `deltaT 1` or `turbulence off` out of a
file whose sha256 is in a lab document and takes it for the published setup.

---

## 6. WHERE THIS LEAVES §G FOR DRIVAER

| Question | Answer |
|---|---|
| Published **OpenFOAM** setup of this case, retrieved and title-page verified? | **YES** — DrivAerML, OpenFOAM v2212 |
| Same configuration and conditions as ours? | **YES** — notchback, full scale, **U∞ 38.889 m/s identical** |
| Mesh recipe published? | **YES**, in absolute mm — but **ANSA HeXtreme, not snappyHexMesh** |
| Layer settings published? | **YES** — 7 layers, first 0.75 mm, total 12 mm, growth 1.2-1.4 |
| Wall treatment published? | **YES** — Spalding, arbitrary y+; **the same function we run** |
| Schemes published? | **YES in prose** (§3.4); **NO in any shipped dictionary** (§5) |
| Transient + averaging published? | **YES** — detect-and-trim, ±1.5 drag counts, 40-60 CTU bracket |
| Grid-convergence evidence? | **NO — explicitly not undertaken.** Never cite it as such |
| By "Ashton & Revell"? | **NO.** Ashton yes, Revell no |
| §G discharge | **Supervisor's ruling; Sanaa's to confirm.** This lane records, it does not decide |

Open items, none decidable by a lane:

1. **The layer fix is now specifiable from a published source without inventing
   anything**: absolute `firstLayerThickness 0.00075`, `thickness 0.012`,
   `nSurfaceLayers 7`, `relativeSizes false`. Registering it is the supervisor's.
2. **The wall-treatment finding reverses for this case.** Our Spalding wall
   function is published practice. The defect is the 6.83x first-cell thickness.
3. **Cost from their 61,440 core-hours, not our probe** — our probe
   under-predicts OpenFOAM HRLES by 2.3x. **26.7 days on the whole 96-core host
   per run**, which goes to Sanaa against the §A allocation table, not to the lab.
4. **Their own solve is +20 drag counts on experiment.** Any DrivAer gate must be
   honest that this is the published state of the art for this case.
5. The three-for-three mesher pattern (STAR-CCM+, block-structured, ANSA) means
   **no published source is going to warn us about a snappy relative-thickness
   defect.** That is an argument for a lab-side snappy standard, not for more
   retrieval.

---

*Written by a cfd lab-lane, 2026-09-13, on the cfd supervisor's explicit ruling.
No solver launched. No frozen file edited. `grade_drivaer.py` untouched, verified
sha256 6106cf6d...83c26d7. Retrieval only; nothing left the box.*
