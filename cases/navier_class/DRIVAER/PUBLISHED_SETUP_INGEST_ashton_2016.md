# DrivAer — published-setup ingest under Sanaa's section-G rule

Status: **INGEST COMPLETE FOR THE PAPER RETRIEVED — SECTION-G DISCHARGE IS `PENDING` A SUPERVISOR RULING.**
This is a paper-fetch-class inbound (nothing left the box; rules 7 and 8 observed).
This document is **not** a pre-registration and freezes no gate. It edits no frozen file.

Governing instruction — `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
section G, byte-exact: *"For any public case, the lab starts from a published
OpenFOAM setup of that case — mesh recipe, layer settings, schemes, wall
treatment — ingested into the knowledge base before the first registration.
Inventing a setup for a case someone has already run in this solver is refused.
DrivAer: Ashton & Revell (OpenFOAM RANS/DES on DrivAer, mesh details published;
run transient, time-average)."*

---

## 0. THE HEADLINE, STATED BEFORE THE DETAIL

The named source was retrieved and title-page verified. **It contains no OpenFOAM.**
The DrivAer computations in it were run in **STAR-CCM+ v9.04**; Code_Saturne v3.0.1
appears only for the Ahmed body. Mechanical counts over the extracted sidecar:

| Token | Occurrences in the paper |
|---|---|
| `OpenFOAM` | **0** |
| `snappy` / `snappyHexMesh` | **0** |
| `STAR-CCM+` | 13 |
| `Saturne` | 12 |

So the paper discharges every clause of section G **except the one that names the
solver**: it publishes the mesh recipe, the layer count, the wall treatment, the
schemes, the time step, the averaging window, the forces against experiment and
the cost — all of it usable — but it is not "a published OpenFOAM setup of that
case". Sanaa's parenthetical "(OpenFOAM RANS/DES on DrivAer)" does not hold for
this paper. Whether it is nonetheless the setup the lab starts from is a
supervisor's call, not a lane's; it is recorded here as `PENDING`.

The two-author paper her wording most nearly names — Ashton & Revell, SAE
2015-01-1538, *Comparison of RANS and DES Methods for the DrivAer Automotive
Body* — is **closed access and was not retrieved** (§5). Its solver identity is
therefore **unverified and is not asserted anywhere in this document.**

---

## 1. THE DOCUMENT, AS VERIFIED FROM ITS OWN TITLE PAGE (rule 15)

Verified by rendering page 2 of the PDF to an image and **reading it**, not by
filename, file type, size or hash. Page 1 is the repository cover sheet; page 2
is the article's own title page. Read from the page, verbatim:

| Field | As it appears ON THE PAGE |
|---|---|
| Title | **Assessment of RANS and DES methods for realistic automotive models** |
| Authors | **N. Ashton^a, A. West^b, S. Lardeau^b, A. Revell^a** |
| Affiliation a | Modelling & Simulation Centre, School of Mechanical, Aerospace & Civil Engineering, University of Manchester, U.K |
| Affiliation b | CD-adapco, London, U.K |
| Footer | *Preprint submitted to Computers & Fluids* — **October 27, 2015** |
| Corresponding e-mail | neil.ashton@manchester.ac.uk |
| Keywords | Hybrid RANS-LES, DDES, Ahmed Body, DrivAer, RANS, Separated Flow, Automotive |

Cover sheet (page 1) citation: Ashton, N., West, A., Lardeau, S., & Revell, A.
(2016). *Assessment of RANS and DES methods for realistic automotive models.*
**Computers and Fluids, 128, 1-15.** DOI `10.1016/j.compfluid.2016.01.008`.
Document Version: **Accepted author manuscript.**

**Identity caveat, stated rather than smoothed over.** Sanaa wrote "Ashton &
Revell". This is a **four-author** paper whose author list contains both of the
names she gave, first and last. It is the correct authors and the correct case,
and it publishes a mesh recipe and run setup. It is **not** the two-author SAE
paper. A near-match is not a match, so the difference is on the record and the
ruling is the supervisor's.

### Retrieval and filing

| Field | Value |
|---|---|
| Retrieved from | `https://pure.manchester.ac.uk/ws/portalfiles/portal/45535628/CaF_Ashton_acceptedcopy.pdf` |
| Route | Green OA accepted manuscript, University of Manchester Pure repository |
| Date retrieved (UTC) | 2026-09-13 |
| PDF | `docs/papers/benchmark_test_cases/ashton_2016_rans_des_realistic_automotive_models.pdf` (16,479,535 B, 29 pages) |
| Sidecar | `docs/papers/benchmark_test_cases/ashton_2016_rans_des_realistic_automotive_models.txt` (106,406 B) |
| sha256 (PDF) | `c92964949cf6d3ae181a2b18712fae5dc432abea53704f769d9f86c4924abe62` |
| sha256 (sidecar) | `7a960589532c97df89ca2a12512fdfff78cecd61b634c9a8661821b3d57952e8` |

**The PDF hash is not reproducible by re-download, and that is expected.** The
Manchester cover sheet is generated per request and carries a "Download
date:13. Sep. 2026" line, so a later fetch yields a different byte stream and a
different sha256 for the same article. The hash above identifies **our retrieved
copy**, nothing more. This is a live instance of exactly why rule 15 forbids
verifying a paper by hash: the hash here is honest about the file and says
nothing whatever about the paper.

Retrieval note: `research.manchester.ac.uk/files/...` returns HTTP 403 behind a
Cloudflare interstitial to every non-browser client (curl with full browser
headers and a cookie jar, and WebFetch, all 403). The `pure.manchester.ac.uk`
`ws/portalfiles/portal/` path serves the identical file at HTTP 200. Recorded so
the next lane does not spend the same attempts.

---

## 2. CLAIM -> SOURCE -> OUR CURRENT VALUE

Source column cites the paper by section, table or sidecar line. "Ours" cites an
artifact on disk. Where the paper does not publish a quantity, the row says
**NOT PUBLISHED** rather than supplying a number.

### 2.1 Case, configuration and flow conditions

| # | Claim | Source | Ours | Agree? |
|---|---|---|---|---|
| C1 | Configurations computed: **Estate and Fastback**, both with side mirrors and a **smooth underbody** | §3.3.1 (sidecar L448-450) | **Notchback**, **detailed underbody** (`OCDADetailedUnderbody`, `EngineUndershield`, `ExhaustSystem1-3`, `Powertrain`), mirrors on, open wheels with rims/tyres/brake discs — 47 vehicle patches, `YPLUS_PROBE/r2c_medium_blended_R3/GROUPS_vehicle_vs_tunnel.json` | **NO** |
| C2 | Freestream **40 m/s**, Re = **1.48e6** on car height **H = 0.567 m** (40%-scale model) | §3.3.1 (L453-455) | **38.889 m/s**, full scale, nu 1.507e-05 (`r2c_medium_blended_R3/constant/transportProperties`); H = 1.418 m gives Re_H = **3.66e6** | **NO — our Re is 2.47x theirs** |
| C3 | Inlet turbulence: intensity **1%**, turbulent viscosity ratio **20**; k, eps, omega derived from these | §3.3.1 (L455-457) | to be read at registration | not compared here |
| C4 | Domain: inlet **4L** upstream, outlet **6L** downstream, top at **8H** (slip), width **11W** (slip) | §3.3.1 (L451-458) + Fig. 4(b) | to be read at registration | not compared here |
| C5 | Floor **no-slip**, **non-rotating wheels**, no rolling road — matching the experimental non-ground-simulation case | §3.3.1 (L458-460) | `floorNoSlip` type `noSlip`; `floorSlip/top/sideMinus/sidePlus` type `slip`; wheels stationary (`0/U`) | **YES** |

### 2.2 Mesh recipe, cell counts and layers — the paper's Table 4

Verbatim (sidecar L484-489):

| Mesh Name | Mesh Type | y+ | Cell Count |
|---|---|---|---|
| RANS coarse | Polyhedral+prism | **<1** | 18 x 10^6 |
| RANS Medium | Polyhedral+prism | **<1** | 37 x 10^6 |
| RANS fine | Polyhedral+prism | **<1** | 80 x 10^6 |
| DES Coarse | Polyhedral+prism | **<1** | 80 x 10^6 |
| DES Fine | Hexahedral+prism | **<1** | 100 x 10^6 |

| # | Claim | Source | Ours | Agree? |
|---|---|---|---|---|
| M1 | Five grids; RANS on polyhedral+prism, DES on hexahedral+prism | §3.3.3 (L467-469) | snappyHexMesh castellated hex + prism | partial |
| M2 | Successively refined, refinement concentrated **throughout the rear of the domain** | §3.3.3 (L469-471) | refinement boxes, `r2_*/system/snappyHexMeshDict` | to be compared at registration |
| M3 | **"a constant highly resolved near-wall mesh, with 20 prism layer cells to ensure the boundary layer was well captured"** | §3.3.3 (sidecar **L470**) | **`nSurfaceLayers 5`** on every vehicle patch, `r2_coarse/system/snappyHexMeshDict:201+` | **NO — 5 vs 20** |
| M4 | Prism-layer **expansion ratio** | — | `expansionRatio 1.25` | **NOT PUBLISHED** |
| M5 | Prism-layer **total thickness / first-layer thickness** | — | `finalLayerThickness 0.5`, `relativeSizes true`, `minThickness 0.02` | **NOT PUBLISHED** (see §3a) |
| M6 | Cell count, coarsest level | Table 4 | **186,709** cells (`r2_coarse`, `r2c_coarse_blended_R2`) vs their 18e6 | **NO — 96x fewer** |
| M7 | Cell count, second level | Table 4 | **983,106** cells (`r2_medium`, `r2c_medium_blended_R3`) vs their 37e6 | **NO — 38x fewer** |
| M8 | Cell count, finest built here | Table 4 | 5,025,587 cells (`r1_fine`) vs their 80-100e6 | **NO — 16-20x fewer** |

### 2.3 Turbulence model, wall treatment, schemes — the paper's Table 3

Verbatim (sidecar L458-463):

| Code | Method | Spatial Scheme | Temporal Scheme | Criteria |
|---|---|---|---|---|
| STAR-CCM+ | RANS | 2nd order Upwind | Steady | < 1 x 10^-5 residuals |
| STAR-CCM+ | DDES | Hybrid CDS/2nd UDS | 2nd order (dt U/L = 1 x 10^-3) | 30 flow units |

| # | Claim | Source | Ours | Agree? |
|---|---|---|---|---|
| T1 | RANS closure incl. **k-omega SST**; also SA, Realizable k-eps, k-eps B-EVM, EB-RSM | Table 1, Table 5 | `RASModel kOmegaSST` (`constant/turbulenceProperties`) | **YES** (SST) |
| T2 | **Wall treatment: wall-resolved, y+ < 1 on all five meshes**, low-Reynolds-number near-wall, **no wall functions** | Table 4 y+ column; §3.2 L390-392 contrasts [3] as a mesh that "did not resolve the near-wall region" | **Wall functions**: `nutUSpaldingWallFunction` on `".*"`, `nutkWallFunction` on the remainder (`r2c_medium_blended_R3/0/nut`) | **NO — different wall treatment** |
| T3 | RANS convection: **2nd order upwind** for momentum and turbulence | §3.3.2, Table 3 | `div(phi,U) bounded Gauss linearUpwind grad(U)`; `div(phi,k)`/`div(phi,omega)` `bounded Gauss limitedLinear 1` (`system/fvSchemes`) | **near-equivalent** |
| T4 | RANS is a **steady coupled incompressible** FV solver, AMG (V-cycle momentum, flex-cycle turbulence), Grid Sequencing Initialization | §3.3.2 (L430-438) | `ddtSchemes default steadyState`, simpleFoam (segregated SIMPLE) | partial — segregated, not coupled |
| T5 | RANS convergence: **sd(Cd), sd(Cl) < 2e-5 over 400 samples** AND residuals monotone below 1e-5; typically **2000-5000 iterations** | §3.3.2 (L438-444) | endTime 2000 (`RATE_PROBE_96C/THE_ONE_CHANGE.diff` shows the 2000 baseline) | comparable iteration count; **our convergence gate is not their two-part criterion** |
| T6 | DDES convection: **hybrid bounded-CDS / 2nd-order-upwind** switching on LES vs RANS mode; 2nd order upwind for turbulence | §3.3.3 (L445-451) | none — we have never run DrivAer transient | **N/A** |
| T7 | DDES temporal: **2nd-order Crank-Nicolson**, CFL < 1 throughout LES regions | §3.3.3 (L452-455) | none | **N/A** |

### 2.4 Forces against experiment — the paper's Table 5

Verbatim, the rows that matter (sidecar L775-790). Reference = wind-tunnel
experiment, 80e6-cell fine RANS mesh for the RANS rows.

| Model | Estate CD | Estate CL | Fastback CD | Fastback CL |
|---|---|---|---|---|
| **Exp.** | **0.294** | **-0.12** | **0.261** | **0.01** |
| Spalart Allmaras | 0.280 | 0.054 | 0.260 | 0.136 |
| Realizable k-eps | 0.260 | -0.026 | 0.244 | 0.085 |
| **k-omega SST** | **0.275** | **0.0436** | **0.260** | **0.124** |
| k-eps B-EVM | 0.253 | 0.007 | 0.2435 | 0.116 |
| EB-RSM | 0.256 | -0.029 | 0.2482 | 0.075 |
| **SST IDDES (Coarse, 80e6)** | **0.310** | **-0.096** | **0.268** | **0.011** |
| **SST IDDES (Fine, 100e6)** | **0.307** | **-0.131** | **0.2615** | **0.024** |
| SA IDDES (Fine) | 0.313 | -0.136 | n/a | n/a |
| SA DDES (Fine) | 0.307 | -0.13 | n/a | n/a |

Two readings the lab should carry forward, both the paper's own:

- **Steady RANS gets CD roughly right and CL badly wrong.** SST on the fastback
  gives CD 0.260 against 0.261 measured — a 0.4% CD error — while CL is 0.124
  against 0.01 measured, an absolute error of **0.114** on a coefficient whose
  measured value is 0.01. Every RANS model in the table shares this: CL error
  0.065 to 0.126 on the fastback.
- **Transient DDES fixes the lift and slightly worsens the drag.** SST IDDES Fine
  gives fastback CL 0.024 vs 0.01 measured (error 0.014, an **8x** reduction from
  SST RANS) and CD 0.2615 vs 0.261 (error 0.2%). This is the published
  justification for Sanaa's "run transient, time-average" instruction, and it is
  a lift argument far more than a drag argument.

The paper's own summary verdict (abstract, §5): even at the finest mesh level the
hybrid RANS-LES methods "still exhibited inaccuracies", and the under-prediction
of turbulence in the initial separated shear layer is the key deficiency of the
RANS models.

**These values are NOT our comparator.** They are Estate and Fastback with a
smooth underbody; our case is the Notchback with a detailed underbody (C1). Our
reference stays DrivAerML run_466, Cd 0.2758368 (`DATA_PROVENANCE_drivaerml.md`).

---

## 3. THE THREE ROWS THE LAB NEEDS MOST

### 3a. ACHIEVED LAYER COVERAGE, theirs against ours — **FLAGGED**

**Ours, measured.** Read from the POST-EXTRUSION table, never the request table
(`LAYERS_ACHIEVED_MEASURED.json`):

| Level | Requested | Achieved, area-weighted | Extruding faces | Added cells | Effective ratio (median) |
|---|---|---|---|---|---|
| coarse (`r2_coarse`) | 5 layers | **2.50 of 5** | 72.27% | 58,479 | 1.281 (requested 1.25) |
| medium (`r2_medium`) | 5 layers | **2.89 of 5** | 79.62% | 234,448 | 1.265 (requested 1.25) |

**Our requested stack thickness in local cells**, recomputed here from the dict
rather than quoted: `relativeSizes true`, `finalLayerThickness 0.5`,
`expansionRatio 1.25`, `nSurfaceLayers 5`, so

    S = 0.5 * sum_{i=0..4} (1/1.25)^i = 0.5 * 3.3616 = 1.6808 local cells

and `S_of_N = 3.3616` in `LAYERS_ACHIEVED_MEASURED.json` is that geometric sum.
The lab's diagnosis stands and is arithmetically confirmed: **the requested stack
is 1.6808 local cells thick — thicker than the cell it grows into.** snappy then
collapses it, which is what the 2.50 and 2.89 are.

**Theirs.** The answer to "what stack thickness in local cells does their recipe
imply?" is, honestly:

> **NOT PUBLISHED.** The paper states the layer **count** (20) and the resulting
> **y+ (<1)** and nothing else about the stack. It gives no expansion ratio, no
> first-layer thickness, no total prism thickness, and no achieved-coverage
> figure — a STAR-CCM+ prism-layer mesher reports no post-extrusion coverage
> table of the kind snappyHexMesh writes, so there is no equivalent number to
> compare against our 2.50 and 2.89. I decline to back one out, because any
> figure I produced would be an invented setup, which is the thing section G
> refuses.

What can be said without inventing anything is structural, and it is decisive.
In STAR-CCM+ the prism layer is an **extruded near-wall region with its own
total thickness**, meshed independently of the polyhedral core, so the stack is
not constrained by the local core cell at all — the failure mode our 1.6808
produces **cannot arise in their mesher**. Their 20 layers at y+<1 span a
resolved boundary layer. Our 5 layers ask for 1.68 base cells and deliver 2.50 to
2.89 of 5. The two recipes are not the same recipe at different settings; they
are different constructions.

### 3b. y+ — **FLAGGED. THIS IS THE FINDING.**

| | Theirs | Ours |
|---|---|---|
| y+ on the vehicle | **< 1, on all five meshes** (Table 4) | **area-weighted median 153.13**, mean 211.03, min 1.35, max 2210.65, over 47 vehicle patches / 64,595 faces / 33.16 m^2 — medium, `YPLUS_PROBE/r2c_medium_blended_R3/YPLUS_AREA_WEIGHTED_R3.json` |
| Coarse | — | **mean 467.75**; **0 of 47 vehicle patches below y+ 30** |
| Wall treatment | wall-resolved, low-Re, no wall functions | `nutUSpaldingWallFunction` + `nutkWallFunction` |
| Ground/tunnel | — | area-weighted median **15,668.77**, max 17,545.71 (`groups.tunnel_and_ground`) |

**Yes — their recipe reaches the wall-resolved range and ours does not. That is
the finding, and it is not marginal: their y+ is below 1 and our vehicle median
is 153, two and a half orders of magnitude apart.** They resolve the boundary
layer; we model it with a wall function, and we do so on a mesh where not one
vehicle patch of forty-seven reaches even the y+ 30 that a wall function's log-law
assumption needs. Our y+ 153 median is inside a wall function's nominal validity
band, but our coarse mean of 467.75 and our maximum of 2210 are not, and the
ground at y+ 15,669 is far outside anything.

The gap is worse than the raw numbers suggest, because of C2: **our Reynolds
number is 2.47x theirs** (Re_H 3.66e6 full-scale against their 1.48e6 at 40%
scale). Reaching y+<1 at our Reynolds needs a *finer* first cell than their
recipe used, on a mesh that today has 983,106 cells against their 37e6 at the
same rung. Adopting their wall treatment is not a settings change. It is a new
mesh family.

The measurement is trustworthy: the y+ reader carries a live planted control
(planted 867.5309 into `OCDADetailedUnderbody` face 0, read back 867.5309, 0
other patches moved) and an area-closure identity at relative residual 1.19e-14
over 3841.10 m^2 of boundary. A zero from this reader would be a zero it was
shown able to see a non-zero through (rule 3).

### 3c. TRANSIENT VS STEADY — **FLAGGED. THIS IS WHAT SANAA IS DIRECTING.**

Every DrivAer run in this lab has been steady (`ddtSchemes default steadyState`).
The published transient setup, read off §3.3.3, Table 3 and Table 6:

| Item | Published value | Source |
|---|---|---|
| Solver | **unsteady segregated incompressible finite-volume**, STAR-CCM+ v9.04 | §3.3.3 L445-446 |
| Turbulence | **SST-IDDES** (also SA-IDDES, SA-DDES on the Estate) | Table 5 |
| Convection | hybrid **bounded CDS / 2nd-order upwind**, switching on LES vs RANS mode; 2nd-order upwind for turbulence | §3.3.3 L446-451 |
| Temporal | **2nd-order Crank-Nicolson** | §3.3.3 L452 |
| Time step | **dt U/L = 1 x 10^-3** (non-dimensional), **CFL < 1 throughout the LES regions**; Table 6 gives the dimensional value **5 x 10^-5 s** | Table 3; §3.3.3 L453-454; Table 6 |
| Inner iterations | **5 per time step** (dual time stepping) | §5 cost discussion, L1263-1264 |
| **Initialisation** | **from the converged steady RANS result**, "which shortened the time to reach a suitable time for time-averaging" | §3.3.3 L455-456 |
| **Run before averaging starts** | **10 convective flow units (10 x L/U)** | §3.3.3 L456-457 |
| **Averaging window** | **a further 20 convective units** | §3.3.3 L457-458 |
| **Total** | **30 flow units = 26,000 time steps** | Table 3 "30 flow units"; Table 6 "26,000 t. steps" |

*Internal inconsistency, disclosed:* 30 flow units at dt U/L = 1e-3 is exactly
30,000 steps, but Table 6 states 26,000 (= 26 flow units). The paper does not
reconcile the two. Costs below use the published **26,000**; a registration
should cost 30,000 and note the 15% headroom.

Translated to our case (L = 4.613 m, U = 38.889 m/s from `0/U`):

    dt = 1e-3 * L/U = 1.186e-04 s      30 flow units = 3.559 s of physical time

**Their published cost** (Table 6; hardware footnote: 2.6 GHz Intel Sandy Bridge,
16 cores/node, Mellanox QDR/FDR; **144,000 cells per core**):

| Method | Cells | Cores | Temporal | Time/iteration | Compute time | Core-hours | Core-minutes | Relative cost |
|---|---|---|---|---|---|---|---|---|
| SST RANS | 80e6 | 512 | Steady | 6 s (2,500 it.) | 4 hrs | 2,048 | 122,880 | 1 |
| **SST IDDES** | **100e6** | **704** | **Transient (5e-5)** | **7 s (26,000 steps)** | **50 hrs** | **35,200** | **2,112,000** | **17** |
| SST IDDES | 100e6 | 2048 (MareNostrum, BSC) | Transient (5e-5) | 2.5 s (26,000 steps) | 18 hrs | 36,864 | 2,211,840 | 17 |

The paper's own headline: **the hybrid RANS-LES simulation is 17 times more
expensive than the RANS computation**, with a 2-day turnaround on 704 cores.

---

## 4. WHAT A TRANSIENT TIME-AVERAGED RUN COSTS AT OUR MEASURED RATE

**Rate basis — measured, not estimated.** `RATE_PROBE_96C` on this 96-core host:
186,709 cells, 4 ranks, 150 iterations, solver `ExecutionTime` 56.05 s
(`RATE_PROBE_96C/log.simpleFoam`, `RUN_META.txt` wall_s=62 including
decompose/reconstruct, `RC.txt`). Derived:

    0.3737 s per iteration  ->  3.737 core-min for 150 iterations
    **0.13342 core-min per iteration per million cells**

**Calibration of that rate against the paper**, which is the strongest check
available on it:

| | core-min per iteration per Mcell |
|---|---|
| Their SST RANS (80e6, 512 cores, 6 s/it) | 0.6400 |
| Their SST IDDES (100e6, 704 cores, 7 s/step) | 0.8213 |
| **Ours (measured)** | **0.13342** |

We are **4.8x cheaper per cell-iteration** than their steady RANS. That is the
expected direction and roughly the expected size — c7a Zen4 against 2.6 GHz Sandy
Bridge, plus a segregated SIMPLE iteration against a coupled one — so the rate
is credible rather than suspicious. It also means **every figure below is the
optimistic end**: it assumes a transient PIMPLE inner iteration costs the same as
our measured steady SIMPLE iteration, which it does not quite.

**Costed scenarios**, all at 26,000 time steps x 5 inner iterations. Dollars are
**derived at $0.0513/core-h, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so the rate is owner-stated.

| Scenario | Mcells | Steps x inner | **Core-minutes** | Core-hours | $ derived | Wall time on all 96 cores |
|---|---|---|---|---|---|---|
| **A — our existing medium mesh** (983,106) | 0.983 | 26,000 x 5 | **17,052** | 284 | $15 | **3.0 hours** |
| **B — their DES Fine recipe** (100e6) | 100.0 | 26,000 x 5 | **1,734,488** | 28,908 | $1,483 | **12.5 days** |
| C — their DES Coarse recipe (80e6) | 80.0 | 26,000 x 5 | 1,387,590 | 23,127 | $1,186 | 10.0 days |
| D — their RANS fine, steady (80e6, 2,500 it.) | 80.0 | 2,500 x 1 | 26,684 | 445 | $23 | 4.6 hours |
| E — their RANS coarse, steady (18e6, 2,500 it.) | 18.0 | 2,500 x 1 | 6,004 | 100 | $5 | 1.0 hour |

Scenario B against their published 35,200 core-hours: we predict 28,908, i.e.
0.82x — consistent, and the residual is the inner-iteration optimism just named.

**The decision this forces.** Scenario A costs almost nothing and is the cheap
answer, but it runs the transient on the mesh that is the subject of §3a and §3b:
5 layers of which 2.89 survive, y+ median 153, 38x fewer cells than the published
second rung. A DDES on that mesh has no LES content to speak of and would be
a transient run of a wall-modelled RANS mesh. Scenario B is the published recipe
and costs **1.73 million core-minutes — 12.5 days of the entire 96-core host**,
which is not a DrivAer lane, it is the box. The gap between A and B is where the
supervisor's ruling has to sit. Sanaa's directive #17 removes the cap as a reason
to stop; it does not remove the arithmetic, and 12.5 days of all 96 cores
collides with the PPTC, CRM wing-body, SUBOFF and finalisation lanes in the
section-A allocation table.

Note also that **their transient was initialised from a converged steady RANS
solution** (§3.3.3). Our steady runs are `GATE FAIL` on convergence (Cd 0.355 vs
the DrivAerML reference 0.276 —
`r2c_coarse_blended_R2/GRADE_STAGE_A_coarse.out:189`). The published recipe's
starting point is a thing we do not currently have.

---

## 5. WHAT COULD NOT BE RETRIEVED, AND WHAT WAS TRIED

**Ashton, N. & Revell, A. (2015), "Comparison of RANS and DES Methods for the
DrivAer Automotive Body", SAE Technical Paper 2015-01-1538, DOI
10.4271/2015-01-1538 — NOT RETRIEVED. `BLOCKED`: closed access.**

Attempted, all read-only fetches, nothing sent (rules 7 and 8):

| Route | Result |
|---|---|
| Unpaywall API on DOI 10.4271/2015-01-1538 | `is_oa: false`, zero OA locations |
| Semantic Scholar Graph API on the same DOI | `isOpenAccess: false`, `openAccessPdf.status: CLOSED` |
| sae.org publication page | header only; no abstract, no solver named |
| neilashton.co.uk/publications | lists the paper; the "PDF link" is the publisher DOI, i.e. the paywall |
| research.manchester.ac.uk author page | HTTP 403 (Cloudflare) |
| Search for a Manchester accepted manuscript of the SAE paper | none found; only the Computers & Fluids one has a repository copy |

A general web search returned a sentence asserting the SAE paper used OpenFOAM.
**That assertion is an unsourced search-engine summary, it is not backed by any
document I read, and it is therefore not carried into this ingest as a claim.**
If the SAE paper is the one Sanaa means, its solver identity is still unverified.

**Nothing was substituted and no recipe was reconstructed from memory.** The
setup recorded in §2 and §3 is read off pages of a document on disk, or marked
NOT PUBLISHED.

---

## 6. WHERE THIS LEAVES SECTION G FOR DRIVAER

| Question | Answer |
|---|---|
| Was a published setup for DrivAer by the named authors retrieved and title-page verified? | **Yes** — Ashton, West, Lardeau & Revell (2016), Computers & Fluids 128:1-15 |
| Does it publish mesh recipe, layer settings, schemes and wall treatment? | **Yes**, except prism expansion ratio and stack thickness (M4, M5) |
| Is it an **OpenFOAM** setup, as section G requires? | **No.** STAR-CCM+ v9.04. `OpenFOAM` appears 0 times |
| Does a published **OpenFOAM** DrivAer setup exist elsewhere on this box? | Ashton et al. (2024) DrivAerML states **OpenFOAM v2212 + UpstreamCFD mods**, pointer at `docs/papers/benchmark_test_cases/ashton_2024_drivaerml.POINTER.md`, PDF outside git. **Not assessed here** — selecting it is a supervisor's call, and this lane was told not to substitute |
| Section-G discharge for DrivAer | **`PENDING`** a supervisor ruling on which source counts |

Open items for whoever writes the registration, none of them decidable by a lane:

1. Does a STAR-CCM+ setup by the named authors discharge a rule that says
   "published **OpenFOAM** setup"? If not, the rule is presently undischargeable
   from the source Sanaa named, and that goes back to her.
2. Estate/Fastback + smooth underbody is not our Notchback + detailed underbody
   (C1). The published forces cannot be our comparator; DrivAerML run_466 stays.
3. Adopting their wall treatment (y+<1, 20 layers) is a new mesh family at
   37-100e6 cells, not a settings change, and at 2.47x their Reynolds number.
4. The transient at the published recipe costs 1.73e6 core-minutes and 12.5 days
   of the whole host; on our current mesh it costs 17,052 core-minutes and 3
   hours but is a transient on a wall-modelled mesh.

---

*Written by a cfd lab-lane, 2026-09-13. No solver was launched. No frozen file
was edited. `cases/navier_class/DRIVAER/grade_drivaer.py` was not touched and
remains hash-pinned. Nothing left the box.*
