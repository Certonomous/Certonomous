# PUBLISHED OPENFOAM CASE FILES — RETRIEVAL POINTER AND HASH RECORD

Retrieved 2026-09-13 by a cfd lane under Sanaa's published-setup rule
(`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md` §G, §I, §J, §K).
Her operative words, §J: *"I KEEP saying i am on a time constraint so we need to use
other ppls files"*.

These are **case files, not papers**, so `CLAUDE.md` rule 15 (title-page verification)
does not apply. Its equivalent does, and is recorded below per source: exact URL,
retrieval timestamp, the version or commit **the source itself declares**, a sha256 of
every file, and a parse check with `foamDictionary`.

**The trees live OUTSIDE the repository** — 4.1 GB total — under
`/home/ubuntu/upstream/published-openfoam-setups/`. This file is the in-repo pointer.
Per-file sha256 manifests sit beside the trees:

| Manifest | Files |
|---|---|
| `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.openfoam-hpc-tc.txt` | 229 |
| `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.wolfdynamics-drivaer.txt` | 101 |
| `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.alletto-m6.txt` | 35 |

---

## 1. PROVENANCE

| # | Source | URL | Retrieved (UTC) | Version the source declares | Retrieved | Parses |
|---|---|---|---|---|---|---|
| 1 | OpenFOAM HPC Technical Committee repository | `https://develop.openfoam.com/committees/hpc.git` branch `develop` | 2026-09-13 17:56 | commit `84c262431117f5c921db8335e368a12d0e9fa3f0`, dated 2025-05-28, subject "B10: set total iteration number to 4000"; case dictionaries declare `Version: v2412` (occDrivAer) and `v2206` (marinePropeller) | YES | YES |
| 2 | Wolf Dynamics DrivAer, OpenFOAM 9 | `https://www.wolfdynamics.com/validations/drivAer/of9-case/drivaer_coarse.tar.gz` and `..._fine.tar.gz`; slides `https://www.wolfdynamics.com/validations/drivAer/tut_drivaer_v2.pdf` | 2026-09-13 17:58–18:01 | page and `system/blockMeshDict` declare **Version 9**; `system/snappyHexMeshDict` and `constant/*` headers declare **Version 7**; solver log declares `Build : 9-6adb71a2e61d` — **see finding F-2** | YES | YES |
| 3 | M. Alletto OneraM6 case files (the case the OpenFOAM-wiki page links to) | `https://gitlab.com/mAlletto/openfoamtutorials.git`, path `OneraM6Wing` | 2026-09-13 18:00 | commit `e72b42c5eb7baba85a138ae207b2b6a8ac2ed518`, dated 2024-01-31, subject "new omega at 0"; dictionaries declare `Version: v2006` | YES | YES |
| 4 | SUBOFF / Type 209 OpenFOAM case files | — | — | — | **NO — see §5** | — |

`foamDictionary` (OpenFOAM v2606, `/usr/lib/openfoam/openfoam2606`) returned exit 0 on
every dictionary listed in §3 and §4. The HPC-TC `constant/*` dictionaries parse only
from the case root because they `#include "${FOAM_CASE}/system/include/caseDefinition"`;
that is the case's design, not a defect.

### Access notes (nothing was sent, and no account was created)

- `develop.openfoam.com` refuses plain HTTPS GET with **403** but serves **git** normally.
  The repository was cloned; no page was scraped.
- `wiki.openfoam.com` is behind a **Cloudflare JS interstitial** ("Just a moment...")
  and returns 403 to both WebFetch and curl. The page itself was read through the
  Internet Archive snapshot `20260103131816`, which names the case files' real home as
  the author's GitLab repository. **No account was required and none was created.**
  The wiki page is therefore BLOCKED as a direct fetch; the case files are not.
- `mdpi.com` returns 403 to WebFetch (§5).

### Load-bearing dictionary hashes (sha256)

```
15c95efb0633bdb2df49c16a8f54fcbf53d745bb7bc44d816cfd15de17134593  wolfdynamics-drivaer/drivaer_coarse/system/snappyHexMeshDict
6226fc88b6cdac40789574edbd2684eb8652395364057a71a27422616bac5080  wolfdynamics-drivaer/drivaer_coarse/system/blockMeshDict
a7be7c65deccb38426e24ff9fa046ba2ed0efa1dba83dbc20e63bb02b2491e17  wolfdynamics-drivaer/drivaer_coarse/system/fvSchemes
10d8b6fa1dc07d9a0892759743940cca7c7b96db647bd648369ed60ab61a7178  wolfdynamics-drivaer/drivaer_coarse/system/fvSolution
fdd80e811c935cf11efadcce0b9571968723eed2ebd05326c01d1cf0de0aed46  wolfdynamics-drivaer/drivaer_coarse/system/controlDict
716ca7e0533b61dcc9df1b274a46e0ffdf923951ff4030091c8cd40bfcd379a7  wolfdynamics-drivaer/drivaer_coarse/constant/turbulenceProperties
917ba87a40e207c785ab06471c59d51060533d472208799d5e61d92bb352c86a  wolfdynamics-drivaer/drivaer_coarse/constant/transportProperties
bd3794109d26306e9e11f0595b53240668d4390f95b6ddc6fd73ebc80407abd0  wolfdynamics-drivaer/drivaer_fine/system/snappyHexMeshDict
2b3471e81c19ac8270eb69e8f79d6ff49ff98cd3b975bf332eb248e5b315754b  wolfdynamics-drivaer/drivaer_fine/system/blockMeshDict
9e7f435dee67694c71dd38902e5013cffe20492204d46bb2c165eb4d55615a67  wolfdynamics-drivaer/drivaer_coarse.tar.gz
6aa8e7a6ddd153733569990b95d9a391dcf982c5c36a046490f1b2a808e6e31c  wolfdynamics-drivaer/drivaer_fine.tar.gz
510569660b16416423300d85e8fd173879731863ee71de88a91a8a744bcbc734  wolfdynamics-drivaer/tut_drivaer_v2.pdf
6996401d0ee62f9b0c8b0546da684289349ad614c091ede8e250c6d200e3129e  openfoam-hpc-tc/.../occDrivAerStaticMesh/system/blockMeshDict
ee3299f4959c38719dee2992d9aa7646b385d04a378e3d4ee3d611abf2ca1857  openfoam-hpc-tc/.../occDrivAerStaticMesh/system/include/caseDefinition
6aa462bcf82ece196e75bb9e1e0f13cbce5c3b2f361a25f2fbcbe752866b72ac  openfoam-hpc-tc/.../occDrivAerRotMesh.orig/system/snappyHexMeshDict.full
cbda3f62111291ecefaf6834b11c1c6c6e2f78cc182349fee1c44fdc9816cad1  openfoam-hpc-tc/.../occDrivAerRotMesh.orig/system/blockMeshDict
d7b4c3e306c5b1f0e842b6e4b7eabba9fd34c48f89e68977eca626d61d49d9ac  openfoam-hpc-tc/.../marinePropeller/system/snappyHexMeshDict
c36623e018c77971d59a9a6b155bf611f2ba80ed2fe967477dccaa91c96f3bfe  alletto-openfoamtutorials/OneraM6Wing/system/snappyHexMeshDict
4360903469a3b2a240bb092d4f014256a6eea9097a0c38bd58ea7d39d77e992d  alletto-openfoamtutorials/OneraM6Wing/system/blockMeshDict
```

---

## 2. FINDINGS — where a source does not match what was expected of it

**F-1. The OpenFOAM HPC Challenge occDrivAer case ships NO `snappyHexMeshDict`.**
`incompressible/simpleFoam/occDrivAerStaticMesh/` contains `system/blockMeshDict`,
`fvSchemes`, `fvSolution` (×3 variants), `controlDict` (×3), `decomposeParDict`,
`constant/{transportProperties,turbulenceProperties}`, `0.orig/` and an `Allrun` —
**but no mesher dictionary of any kind**. Its own `README.md` and `constant/README.md`
say why: the meshes are distributed **pre-built**, as `polyMesh` tarballs on Zenodo
record 15012221 (`polyMesh_65M.tar.gz`, `polyMesh_110M.tar.gz`, `polyMesh_236M.tar.gz`).
The README describes the mesh only in prose. The expectation that its "dictionaries are
public" is **half right**: the *solver* dictionaries are public; the *mesh* dictionary
for the challenge meshes is not in the repository.

**F-1a (partial closure, and it is an inference, not a proof).** The sibling case
`incompressible/pimpleFoam/LES/occDrivAerRotMesh/` — same geometry, same authors
(Upstream CFD GmbH, Mockett/Hetmann/Kramer) — **does** ship
`system/snappyHexMeshDict.full` and `.rota` in full. Four independent numbers agree
between that dictionary and the static case's README prose: background cell
**1.0 m** (dict: 120×44×20 cells over 120×44×20 m; README: "cell level L0 = 1 m"),
surface level **9** → 1/512 = **1.9531 mm** (README: "major surface refinement level
L9 = 1.95 mm"), feature level **10** → 1/1024 = **0.9766 mm** (README: "maximum feature
refinement level L10 = 0.96 mm"), and **2 prism layers** (README: "There are 2 prism
layers"). The rotating-mesh dictionary is therefore the **same mesh recipe family** as
the HPC Challenge meshes. **It is not proven to be the identical file that produced
them**, and must not be cited as such.

**F-2. Wolf Dynamics DrivAer declares two OpenFOAM versions inside one tree.**
The download page and `system/blockMeshDict` say **Version 9**; `system/snappyHexMeshDict`,
`constant/transportProperties` and `constant/turbulenceProperties` carry
`Version: 7` headers. The shipped solver log
(`sol_logs/coarse/log.solver`) resolves it: `Build : 9-6adb71a2e61d`, i.e. the
distributed results **were produced with OpenFOAM 9**; the version-7 headers are stale
banners on files carried forward. Recorded, not corrected. **Nothing in the tree was
edited.**

**F-3. The Wolf Dynamics `blockMeshDict` declares all six farfield patches `type wall`**,
including `ffminy`/`ffmaxy` which bound a half-car domain (`ymin 0`, `ymax 4`) and
`ffmaxz`/`ffminx`/`ffmaxx`. The `0_org/` boundary conditions are what make them behave
as inlet/outlet/symmetry/moving ground. This looks wrong at first reading and **it has
not been changed** — Sanaa's rule: *"If a value looks wrong to you, record that it looks
wrong — do not change it."* It must be read together with `0_org/U` before any launch.

---

## 3. THE (a)–(d) ROWS — verbatim, per case

Every value below is **copied from the file named, not re-typed from memory**, and every
file carries a sha256 in §1 or in the per-tree manifests.

### (a) `relativeSizes` — the single most important line

| Case | File | `relativeSizes` |
|---|---|---|
| Wolf Dynamics DrivAer, coarse and fine | `wolfdynamics-drivaer/drivaer_{coarse,fine}/system/snappyHexMeshDict` | **`true`** |
| occDrivAer rotating-mesh (HPC-TC) | `.../occDrivAerRotMesh.orig/system/snappyHexMeshDict.full:512` | **`true`** |
| M6 Alletto | `alletto-openfoamtutorials/OneraM6Wing/system/snappyHexMeshDict` | **`true`** |
| ESI marine propeller (HPC-TC) | `.../marinePropeller/system/snappyHexMeshDict:275` | **`false`** |
| aeroacoustic DrivAer (HPC-TC) | `compressible/rhoPimpleFoam/LES/aeroacousticDrivAer/system/snappyHexMeshDict:814` | **`false`** |
| high-lift CRM ONERA (HPC-TC) | `.../highLiftCommonResearchModelONERA_LRM-LDG-HV/system/snappyHexMeshDict:2082` | **`true`** |

**The pattern, and it is the answer to the PPTC question.** Every one of these cases
meshes a body sitting in a **uniform Cartesian background block** — in which
`getLevel0EdgeLength()` returns the *actual* level-0 cell, so `relativeSizes true` is
safe and is what four of six use. The two cases that turn it **off** are the two whose
thicknesses are physically pinned: the ESI **marine propeller** and the aeroacoustic
DrivAer, both of which then state absolute metres. **No retrieved case uses
`relativeSizes true` on a non-uniform background.** This is consistent with
`docs/standards/MESH_STANDARD.md` §16 and with the lab's PPTC defect: on a 72° wedge the
global-minimum level-0 edge is the axis rod's azimuthal chord, 2.09343825e-04 m, and
relative sizing is poisoned by 95.5×. The published propeller practice is
`relativeSizes false` **plus a full-360° Cartesian box** — the two choices travel
together.

### (b) Layer parameters, as written, with units

| Case / patch | `nSurfaceLayers` | `expansionRatio` | first / final layer | `minThickness` |
|---|---|---|---|---|
| WD DrivAer **coarse** — `body2`, `ruotaant`, `ruotapost`, `ffminz` | **3** | **1.2** | `finalLayerThickness` **0.3** (relative) | **0.01** (relative) |
| WD DrivAer **fine** — same four patches | **6** | **1.2** | `finalLayerThickness` **0.3** (relative) | **0.01** (relative) |
| occDrivAerRotMesh — two patch groups | **2** | **1.2** | `finalLayerThickness` **0.5** (relative) | **1e-10** (relative) |
| M6 Alletto — `wing` | **5** | **1.5** | `finalLayerThickness` **0.5** (relative) | **0.05** (relative) |
| ESI marine propeller — `propellerTip` | **5** | **1.20** | `firstLayerThickness` **1.0e-04 m** (absolute) | **1e-06 m** (absolute) |
| ESI marine propeller — `propellerStem1/2/_outlet` | **5** | **1.20** | `firstLayerThickness` **2.0e-04 m** (absolute) | **1e-06 m** (absolute) |
| ESI marine propeller — global default | **—** | **1.2** | `firstLayerThickness` **1.2e-04 m** (absolute) | **1e-06 m** (absolute) |
| high-lift CRM ONERA | **2** | **1** | `finalLayerThickness` **0.8** (relative) | **1e-10** (relative) |
| aeroacoustic DrivAer — 33 body patches | **16** | **1.4** (four patches 1.34) | `firstLayerThickness` **5.25e-06 to 1.17e-05 m** per patch (absolute) | **1e-08 m** (absolute) |
| aeroacoustic DrivAer — ground | **6** | **1.2** | `firstLayerThickness` **1e-03 m** (absolute) | — |

### (c) Background mesh topology, base cell size, and the stack in LOCAL CELLS

This is the row the lab could not read from any paper. The lab's two measured points are
**0.480 local cells extrudes** and **1.6808 local cells collapses**.

| Case | Background block | Base cell | Surface level | Local cell at wall | **Stack, local cells** |
|---|---|---|---|---|---|
| WD DrivAer **coarse** | `hex` over x∈[-10,20], y∈[0,4], z∈[0,6.4] m, `deltax=deltay=deltaz=0.2` → 150×20×32 | **0.2 m uniform** | `body2` (3 3) | 0.025 m | **0.758333** |
| WD DrivAer **fine** | same deltas, x∈[-12,32] → 220×20×32 | **0.2 m uniform** | `body2` (4 4) | 0.0125 m | **1.197184** |
| occDrivAerRotMesh | 120×44×20 cells over x∈[-40,80], y∈[-22,22], z∈[-0.3176,19.6824] m | **1.0 m uniform** | body (6 6), regions to (9 10), plinths (11 11) | 1.9531 mm at L9 | **0.916667** |
| occDrivAer **static / HPC Challenge** | identical block, `rescale 0.5` in the shipped dict → 60×22×10 | **2.0 m** as shipped; README states **1.0 m** for the distributed meshes | L9 major / L10 feature (README prose) | 1.95 mm / 0.96 mm (README) | **0.916667** if F-1a holds — *inferred, not read from a dict* |
| M6 Alletto | 30×15×30 cells over ±18000 in x,z and [0,18000] in y (STL units, mm) | **1200 units uniform** | `wing` (8 9) | 4.6875 at L8 | **1.302469** |
| ESI marine propeller | 40×80×40 cells over x,z∈[-0.6,0.6], y∈[-1.20,1.20] m | **0.03 m uniform** | tip (4 5), stem (4 4) | 9.375e-04 m at L5 | **0.79377** (absolute 7.4416e-04 m ÷ 9.375e-04 m) |
| ESI marine propeller, stem | as above | 0.03 m | stem L4 | 1.875e-03 m | **0.79377** (absolute 1.48832e-03 m ÷ 1.875e-03 m) |
| high-lift CRM ONERA | (not extracted) | — | — | — | **1.6** |

**Every published stack lies between the lab's two measured points, 0.480 and 1.6808.**
The tightest cluster is 0.76–1.30. The ESI propeller sits at **0.794**, and it gets there
with `relativeSizes false` and absolute metres — the tip and the stem land on the *same*
0.794 because their absolute first-layer thicknesses were chosen to track their refinement
levels. The high-lift CRM case at **1.6** is the only one near the collapse point, and it
buys that with `expansionRatio 1` and `maxThicknessToMedialRatio 3` (ten times the 0.3
every other case uses).

Arithmetic, so it can be re-derived: relative-final stacks are
`finalLayerThickness × Σ_{k=0}^{n-1} r^(-k)`; absolute-first stacks are
`firstLayerThickness × (r^n − 1)/(r − 1)`.

### (d) `featureAngle`, `resolveFeatureAngle`, refinement levels per surface

| Case | `featureAngle` (layers) | `resolveFeatureAngle` | refinement levels per surface |
|---|---|---|---|
| WD DrivAer coarse | **130.0** | **30.0** | `body2` (3 3); `ruotaant` (4 4); `ruotapost` (4 4); region `vr2` inside level 2 (vr1/vr3/vr4 commented out); features `ruotaant.eMesh`/`ruotapost.eMesh` at `level 0` |
| WD DrivAer fine | **130.0** | **30.0** | `body2` (4 4); `ruotaant` (4 4); `ruotapost` (4 4); regions `vr1` 1, `vr2` 2, `vr3` 3, `vr4` 4 **all enabled**; features at `levels ((0.025 0))` |
| occDrivAerRotMesh | **120** | **20** | body (6 6) with per-region (9 10) and (9 9); `Plinths_adapted` (11 11); others (7 7), (8 8), (9 9), (10 10); boxes `box_L3`…`box_L6` inside 3…6, two more at 7 and 8; distance regions 0.02→11, 0.05→8, 0.065→8, 0.15→8, 0.2→7 |
| M6 Alletto | **60** | **30** | `wing` (8 9); boxes 0–4 inside at levels 5, 4, 3, 2, 1; explicit feature eMesh **commented out**, `implicitFeatureSnap true` instead |
| ESI marine propeller | **175** | **30** | `propellerTip` (4 5); `propellerStem1/2` (4 4); `innerCylinderSmall` (3 3); `outerSphere` (1 1); regions `innerSphere` 2, `innerCylinderSmall` 3, `outerSphere` 2 |
| high-lift CRM ONERA | **180** | **30** | (not extracted) |
| aeroacoustic DrivAer | **180** | **30** | (not extracted) |

`nCellsBetweenLevels`: WD DrivAer **5**, occDrivAerRotMesh **5**, M6 Alletto **3**.
`maxThicknessToMedialRatio`: **0.3** in WD DrivAer, occDrivAerRotMesh, M6 Alletto and the
marine propeller; **3** in high-lift CRM.

---

## 4. THE REST OF EACH CASE — solver, physics, and the validation the source itself claims

### Wolf Dynamics DrivAer (OpenFOAM 9)
- `application simpleFoam`, `endTime 1000` (comment: `1000-3000-5000`), `deltaT 1`,
  `writeInterval 100`, `purgeWrite 2`, `writeFormat binary`, `writePrecision 12`.
- `constant/turbulenceProperties`: `simulationType RAS`, `RASModel kOmegaSST`.
- `constant/transportProperties`: `nu 1.5881327800829875E-5` m²/s.
- Force coefficients: `magUInf 30` m/s, `lRef 1.0` m, `Aref 1.073476` m², `rhoInf 1.205`,
  `CofR (0 0 0)`, `liftDir (0 0 1)`, `dragDir (1 0 0)`; function objects per patch
  (`all`, `body2`, `ruotaant`, `ruotapost`) plus `yPlus` and `wallShearStress`.
- **Geometry ships with the case**: `constant/triSurface/{body2,ruotaant,ruotapost}.stl`
  plus `.eMesh` and `extendedFeatureEdgeMesh/`. **No geometry substitution is needed.**
- **Its own shipped result, coarse level** (`sol_logs/coarse/postProcessing/all/0/forceCoeffs.dat`,
  a file in the tarball, not a number of ours): at iteration 1000,
  **Cd = 2.911626517668e-01**, Cl = −4.436915663288e-03, Cm = −4.432528646428e-01.
  At iteration 999 Cd = 2.920267572678e-01 — drifting by 8.6e-04 per iteration, i.e.
  **not stationary to the lab's usual gate**, which is worth saying out loud before
  anybody treats 0.291 as a converged reference.
- **Its own shipped y+**, iteration 1000 (`postProcessing/yplus/0/yPlus.dat`):
  `body2` min 3.687, max 1976.06, **average 96.03**; `ruotaant` avg 62.50;
  `ruotapost` avg 65.21; `ffminz` avg 54.98. Wall functions throughout.
- Pre-generated Fluent meshes also ship (`mesh/mesh_coarse.msh`), with
  `run_mesh_fluent.sh` to convert; the README says SHM meshing "is time consuming so
  better use the pre-generated mesh."

### occDrivAer, OpenFOAM HPC Challenge (OHC-1)
- Authors: Mockett, Hetmann, Kramer (Upstream CFD GmbH) 2022–2023; modified for OHC-1
  by Wasserman (Huawei) and Lesnik (Wikki GmbH) 2025. CC BY-SA 4.0.
- Geometry lineage: Ford Open Cooling DrivAer notchback (Hupertz et al. 2018);
  AutoCFD2 case 2, AutoCFD3/4 case 2a.
- `system/include/caseDefinition` (the single source of the case's numbers):
  `lref 2.78618` m, `Aref 2.17` m², `Uinf (38.889 0 0)` m/s, `nu 1.507e-05` m²/s,
  `pref 0.0`, `viscRatio 5.0`, `Tu 0.0026`, `RASturbModel kOmegaSST`,
  `nCores 512`, `decompositionMethod hierarchical`, `nHierarchical (16 8 4)`.
- README: Re = 7.1899e6 on wheelbase; domain 40 m upstream, 80 m downstream, 20 m high,
  44 m wide, floor at −0.3176 m; **y+ > 30 over the major parts**; 2 prism layers,
  wall-nearest cell **0.8 mm on the roof top**; 236 M / 110 M / 65 M cells; known to run
  with **OpenFOAM-v2412**, double precision, tested to 512 ranks.
- **Meshes are a separate 3-file Zenodo download (record 15012221) and have NOT been
  retrieved** — they are polyMesh tarballs of a 65–236 M cell case. Retrieving them is a
  separate decision with its own disk and time cost; say so rather than assume.

### M6 Alletto (rhoSimpleFoam + snappyHexMesh)
- Ships `0.orig/{T,U,alphat,nuTilda,nut,p}`, `constant/thermophysicalProperties`,
  `constant/turbulenceProperties`, `constant/triSurface/AileM6_with_sharp_TE.stl`,
  `system/{blockMeshDict,snappyHexMeshDict,controlDict,fvSchemes,fvSolution,decomposeParDict,extrudeMeshDict,fvOptions,samplePwall,surfaceFeatureExtractDict}`,
  `Allrun`, `Allclean`, `plot.py`.
- **Ships the experimental comparison data**: `expy=0.2.dat`, `0.44`, `0.65`, `0.8`,
  `0.9`, `0.96`, `0.99` — the seven ONERA M6 spanwise pressure stations.
- Per §K of Sanaa's directive, **M6 keeps its current NASA-committee-grid route**; this
  tree is retrieved as the published cross-check, not as a replacement.

### ESI marine propeller (HPC-TC microbenchmark MB13) — relevant to PPTC
- 4-bladed propeller, **D = 0.224 m**, spherical farfield radius 600 m, AMI sliding
  interface, k-ω SST **DDES**, `U = 5` m/s, `J = 0.892`, `dt = 1e-4` s, 2.5 s = 62.5
  revolutions; baseline **4.07 M cells** at `nref 1`, 29.13 M at `nref 2`.
  Tested in **OpenFOAM v2206**. Reference: Sengupta, Saxena, Mendonça, GT2018-76932.
- It is **not** the PPTC VP1304 and must never be graded as if it were. Its value here is
  (a) above: a published OpenFOAM propeller that turns `relativeSizes` **off**.
- `meshQualityControls`: `maxNonOrtho 65` (relaxed 75), `maxInternalSkewness 4`
  (relaxed 8), `maxBoundarySkewness 20`.

---

## 5. SUBOFF — NOT RETRIEVED

**No SUBOFF or Type 209 OpenFOAM case files were found, and nothing was substituted.**

What was tried: a search for the OpenFOAM-v7 snappy-layer "Type 209" work and for
Robertson's validation; a search for a public SUBOFF OpenFOAM repository; a check of the
whole HPC-TC tree (no SUBOFF case exists in it); an attempt to read the identified paper,
**Numerical Flow Characterization around a Type 209 Submarine Using OpenFOAM**,
*Fluids* 6(2) 66 (2021), `https://www.mdpi.com/2311-5521/6/2/66` — MDPI returned **403**
to WebFetch.

That paper is open access and is a **paper**, not case files, so it falls under the
literature route (`CLAUDE.md` rule 15, title-page verification, `docs/papers/`) and not
under this retrieval. **Status: NOT RETRIEVED.** No SUBOFF dictionary was reconstructed
from memory and no other case was offered in its place.

---

## 6. WHAT THIS POINTER DOES NOT ESTABLISH

- That any retrieved case **runs** here. Nothing was launched; `foamDictionary` parsing is
  a syntax check, not a solve.
- That the occDrivAerRotMesh dictionary produced the HPC Challenge meshes (F-1a is an
  inference from four agreeing numbers, not a proof).
- That Wolf Dynamics' shipped `Cd = 0.2912` is converged — by its own file it is still
  drifting at iteration 1000 (§4).
- That the 65/110/236 M polyMesh tarballs are on this box. They are not.
- Any comparison between these settings and the lab's own registered settings. That
  belongs in the comparison document, not here.
