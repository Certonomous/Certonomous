# MB13 MARINE PROPELLER — PRE-REGISTRATION

**THIS IS A REPRODUCTION RUNG.** The published tree ships no tabulated thrust, torque,
`KT`, `KQ` or `eta_O`. Its only published quantities are two settled time-histories drawn
as raster figures and one qualitative spectral statement in its README. They are digitised
here, by eye, against their own gridlines, and frozen **before any compute** — with the
digitisation named as digitisation in every place it is used. **No comparator is invented,
and the lab's PPTC VP1304 tables are NOT used: a different propeller is not a comparator.**

**STATUS AT FREEZE: STAGE 1 COMPLETE — RETRIEVAL AND REGISTRATION ONLY. NOTHING HAS BEEN
LAUNCHED.** No mesher, no solver, no compute of any kind has run for this case. Launch
requires the cfd-supervisor's personal verification of this file at its commit (check 4,
undelegable).

- **Team / lane:** cfd. **Registered ranks: 32.**
- **Case selected by Sanaa**, byte-exact:
  > "CFD propeller case : https://develop.openfoam.com/committees/hpc/-/tree/0d06b7550061eb58b7857a6d6635cc10516707b4/compressible/rhoPimpleFoam/LES/marinePropeller everything is in there so to be cloned and repeated verbatim"

---

## 0. PROVENANCE — GATE G0, DISCHARGED IN STAGE 1

| Item | Value |
|---|---|
| Upstream | `https://develop.openfoam.com/committees/hpc` (OpenFOAM HPC Technical Committee) |
| Commit named by Sanaa | `0d06b7550061eb58b7857a6d6635cc10516707b4` |
| Commit date / subject | 2024-04-16 08:56:56 +0200 — "Remove previously relocated cavity case from root" |
| Tree path | `compressible/rhoPimpleFoam/LES/marinePropeller` |
| Subtree git object id | `ffbde3f10d781b4bae862f18d86a5c437303f50c` |
| Local clone | `/home/ubuntu/upstream/published-openfoam-setups/openfoam-hpc-tc` |
| Clone HEAD at Stage 1 | `84c262431117f5c921db8335e368a12d0e9fa3f0` (2025-05-28, "B10: set total iteration number to 4000") |
| Files in the tree | **72** |
| Manifest | `cases/navier_class/MB13_MARINE_PROPELLER/UPSTREAM_MANIFEST.sha256` (72 sha256 lines + a 13-line header) |

**HOW THE COMMIT WAS VERIFIED — stated exactly, because the clone was NOT at Sanaa's
commit.** The clone is shallow and its HEAD was `84c2624`, a later commit. `0d06b755` was
**not** in the object store (`git branch --contains` returned "no such commit"). It was
**fetched from the upstream remote** (`git fetch origin 0d06b7550061eb58b7857a6d6635cc10516707b4`,
succeeded), and is now a resolvable commit object locally. Two independent checks then ran:

1. `git rev-parse <commit>:compressible/rhoPimpleFoam/LES/marinePropeller` at **both**
   `0d06b755` and `84c2624` returns the **same subtree id `ffbde3f1…`** — the marinePropeller
   tree did not change between Sanaa's commit and the clone's HEAD.
2. `git archive 0d06b755 -- <path>` was extracted to a scratch directory and `diff -r`'d
   against the working tree on disk: **IDENTICAL, byte for byte**, 72 files, no extras.
   `git status --porcelain` for the path is empty, and a disk-side `find -type f` listing
   matches `git ls-files` exactly (72 == 72) — so the disk carries no untracked additions
   and no local edits.

**No nearby commit was substituted.** The working clone was left at its own HEAD rather than
checked out to `0d06b755`, because the tree under test is provably identical at both and the
clone is shared with other lanes. **G0: PASS.**

**README verified by reading it** (`README.md`, sha256 `10ff6171…`): title "MB13 MARINE
PROPELLER", authors ESI-Group 2023, CC-BY-SA-4.0, exaFOAM grant 956416. Its stated reference
is *Koushik Sengupta, Swati Saxena, Fred Mendonça, "NUMERICAL SIMULATION FOR MARINE PROPELLER
HYDROACOUSTICS USING OPENFOAM", GT2018-76932*. **That paper has NOT been retrieved and is NOT
title-page verified, so it is cited nowhere in this registration as evidence and contributes
nothing to any band** (rule 15). Every band below comes from files inside the hashed tree.

---

## 1. THE CASE, FROM THEIR FILES

Four-bladed marine propeller, **D = 0.224 m**, in water, run as a **compressible
hydroacoustics** problem.

| Quantity | Value | Artifact |
|---|---|---|
| Blades | 4 | `README.md` |
| Diameter D | 0.224 m | `README.md`; `system/fvSchemes.tr:34` carries 0.224 as the DEShybrid length |
| Inlet velocity U | 5 m/s, direction `(0 -5 0)` | `0.orig/U` (`Uinlet (0 -5 0);`) |
| Rotation | omega 157.14 rad/s about `(0 1 0)`, origin `(0 0 0)` = 25 rev/s = 1500 rpm | `constant/dynamicMeshDict` |
| Advance coefficient J | 0.892 — `5/(25 × 0.224)` = 0.8929 | `README.md`, consistent with the two rows above |
| Blade passage frequency BPF | **100 Hz** = 4 blades × 25 rev/s | derived from the two rows above; README states 100 Hz |
| Fluid | water as `perfectFluid`: R 7255, rho0 997, mu 8.509e-4, Cp 4195, Pr 5.2 | `constant/thermophysicalProperties` |
| Far-field pressure | 101325 Pa, `freestreamPressure` | `0.orig/p` |
| Gravity | `(0 -1.0e-16 0)` — effectively disabled | `constant/g` |
| Force patches | `propellerStem1 propellerStem2 propellerTip`, rhoInf 997, pRef 101325, CofR (0 0 0), pitchAxis (0 1 0) | `system/forces:15-21` |
| Acoustic probes | 5 points at radius 4.48 m = 20 D, field `pGauge`, every time step | `system/controlDict.tr:62-79` |

Speed of sound from `perfectFluid` at 101325 Pa, 300 K is ~1475 m/s; this is why the stack is
compressible and why acoustic damping exists at all.

### 1.1 THE ROTATION MECHANISM, NAMED EXPLICITLY — **BOTH MRF AND AMI**

This case uses **two different rotation mechanisms in two different phases**, and both are on
disk in their own files:

- **Steady precursor — MRF.** `constant/MRFProperties` defines `mrf_v_fluid_rotor` on
  `cellZone v_fluid_rotor`, axis `(0 1 0)`, `omega table ((0 0)(200 0)(300 157.14)(10000 157.14))`
  — a ramp over the first 300 SIMPLE iterations. `Allrun:62` turns it **on** for the steady
  phase and `Allrun:120` turns it **off** for the transient.
- **Transient LES — SOLID-BODY ROTATION OF THE CELL ZONE ACROSS cyclicAMI.**
  `constant/dynamicMeshDict` is `dynamicMotionSolverFvMesh` / `solver solidBody` /
  `solidBodyMotionFunction rotatingMotion` on `cellZone v_fluid_rotor`, omega 157.14 rad/s.
  The interface is four `cyclicAMI` patches — `AMI1`/`AMI1_rotor`, `AMI2`/`AMI2_rotor` — built
  by `createPatch` from `system/createPatchDict`. The README calls it "the standard sliding
  mesh implementation in OpenFOAM … interpolated through the AMI boundary".

**This is NOT the same finding as the earlier PROPELLER1 draft** (commit `bb6f87134`), which
reported "neither MRF nor AMI, and the propeller does not turn". That draft was about the
OpenFOAM **tutorial** `propeller1`, a different case entirely. MB13 turns, and it turns two
different ways in its two phases. Proven from three separate files, not inferred.

### 1.2 `nref` AND CELL COUNT

- `system/parameters:15` — **`nref 1;`**. We run their shipped value, unchanged.
- What `nref` scales, from their own comments and code: (a) `snappyHexMesh` core refinement
  via a `refineMesh` loop run `nref-1` times (`Allrun:73-79` — **at nref=1 this loop body is
  never entered**); (b) the transient time step, `deltaT #eval{ 1e-4 / $nref }`
  (`system/controlDict.tr:23`); (c) both extrusion layer counts, `36*$nref` and `150*$nref`
  (`system/extrudeMeshDict.step1:29`, `.step2:29`, and `Allrun:87,93`).
- **DECLARED cell count: 4.07 M at nref=1** — `system/parameters:6` ("nref=1 -> Baseline mesh
  ( 4.07M cells)") and the README ("As baseline, mesh about 4M cells"). **This is their
  declaration, not a measurement by this lab.**
- **BUILT cell count: unknown until `checkMesh` runs.** It is gated at G1 and it is the number
  that will be reported; the 4.07 M is the band it is graded against, labelled as declared.
- Base block, both regions: `40 × 80 × 40 = 128,000` cells over
  `1.2 × 2.4 × 1.2 m` — a uniform **0.03 m cube** (`system/blockMeshDict:33`;
  `system/v_fluid_rotor/blockMeshDict` is byte-identical, `cmp` clean).
  Finest surface refinement level 5 → 0.03/32 = **9.375e-4 m**.
- **Cells per rank at 32, on the declared count: 4.07e6 / 32 = 127,188.** See §8.

### 1.3 THEIR `decomposeParDict` — AND OUR REGISTERED RANK COUNT

`system/decomposeParDict` and `system/v_fluid_rotor/decomposeParDict` are byte-identical
(sha256 `6fd45457…` both) and read:

```
numberOfSubdomains #eval {$nCPU};
method          scotch;
```

**Their rank count is not a published number at all — it is `argv[1]` of `Allrun`**
(`Allrun:11`, `export nCPU="$1"`), resolved by `#eval` at dictionary-read time. Their README
gives only an *example*: `./Allrun 16`.

**REGISTERED RANK COUNT: 32**, invoked as `bash ./Allrun 32`, resolving
`numberOfSubdomains` to the literal **32** in both dicts. Decomposition method `scotch`,
unchanged. Because there is no published fixed rank count, **this is a resolution of a
free parameter, not a deviation from a published value** — but it is disclosed here in full
either way.

### 1.4 THEIR `controlDict` — BOTH PHASES

`Allrun` swaps `system/controlDict` between two shipped files. `system/controlDict` as
committed is byte-identical to `system/controlDict.st` (sha256 `9b799c1e…` for both), so the
steady dict is what the tree ships at rest.

| Entry | `controlDict.st` (steady) | `controlDict.tr` (transient) |
|---|---|---|
| `application` | `rhoSimpleFoam` | `rhoPimpleFoam` |
| `startFrom` | `latestTime` | `latestTime` |
| `endTime` | **5000** (iterations) | **2.5** (seconds = 62.5 revolutions) |
| `deltaT` | **1** | **`#eval{ 1e-4 / $nref }` → 1e-4 s at nref=1 → 25,000 steps** |
| `adjustTimeStep` | not set (steady) | **`no`** |
| `maxCo` | not set | **0.5** (inert: `adjustTimeStep no`) |
| `maxDeltaT` | not set | 1 (inert) |
| `writeControl` | `runTime` | `adjustableRunTime` |
| `writeInterval` | **5000 — ONE write, at the end** | **1.0e-01 s ≈ 1000 steps** |
| `purgeWrite` | 0 | 1 |
| `writeFormat` | binary | binary |
| Function objects | `fieldMinMax`; `fieldAverage1` (U, p, mean only, **`timeStart 4000`**) | `derivedPressureFields`, `readFields (pMean UMean)`, `fieldMinMax`, `probes_pGauge` (5 points, every step), `forces`, `cuttingPlane` |

**Two hard couplings in those numbers, both of which make the steady run all-or-nothing:**

1. `fieldAverage1` starts at iteration **4000** and writes only at 5000, producing `pMean`
   and `UMean`. The transient's `readFields` requires both (`controlDict.tr:48`) and
   `acousticDampingSource` uses `URef UMean` (`system/fvOptions:50`). A steady run that stops
   short of 5000 does not produce them.
2. `system/replace.sh:11` is `mv 5000 5000_steadyState` — hard-coded. The steady run must
   write a time directory named literally `5000`.

**Checkpointing — this is where the published case is inadequate for us, and the deviation is
declared, not silently applied.** See §5, deviations **D4a** and **D4b**. Nothing is changed
in Stage 1.

### 1.5 THEIR TRANSIENT LES SETTINGS

- `constant/turbulenceProperties`: `simulationType LES` (set by `Allrun:118`),
  **`LESModel kOmegaSSTDDES`**, `delta vanDriest` over `cubeRootVol` with `deltaCoeff 2`.
  The steady phase uses `RASModel kOmegaSST` (`Allrun:60`).
- `system/fvSchemes.tr`: `ddtSchemes default backward` (2nd order);
  `div(phi,U) Gauss DEShybrid linear linearUpwind grad(U) delta 0.65 5 0.224 0 1 1.0e-03`
  — the DES hybrid blend, requiring `libturbulenceModelSchemes.so`
  (`system/controlDict.tr:38`); `laplacianSchemes default Gauss linear corrected limited 0.333`.
- `system/fvSolution.tr`: PIMPLE with **`nOuterCorrectors 7`**, `nCorrectors 2`,
  `nNonOrthogonalCorrectors 1`, `momentumPredictor yes`, `transonic no`, `pMaxFactor 1.5`,
  `pMinFactor 0.8`. Pressure on GAMG (`nCellsInCoarsestLevel 200`, symGaussSeidel, relTol 0.05
  / 0.001 final); U, k, omega on PBiCGStab/DILU. Under-relaxation p 0.9, U 0.9, h/e 0.95,
  all `*Final` at 1.
- `system/fvOptions`: `damp` (velocityDampingConstraint, UMax 100); `limitT`
  (limitTemperature, 290–310 K); **`acousticDampingSource`** — `timeStart 0.01`,
  `duration 1000`, centre `(0 0 0)`, **radius1 300, radius2 450**, `frequency 50`,
  `URef UMean`. Switched on at `Allrun:119`, off at `Allrun:61/106`.
- Far-field radius **600 m**, reached by the second extrusion
  (`system/extrudeMeshDict.step2:35`, `R 600`) — matching the README.

**All of the above is verified present in this box's OpenFOAM build** (v2606): `kOmegaSSTDDES`,
`acousticDampingSource`, `DEShybrid`, `velocityDampingConstraint`, `limitTemperature`,
`flowRateOutletVelocity`, `cyclicAMI`, `rotatingMotion`, `dynamicMotionSolverFvMesh` all
resolve as defined symbols in `$FOAM_LIBBIN`, and `libturbulenceModelSchemes.so` exists.
`mergeMeshes` in v2606 accepts `-addRegion`, which `Allrun:84` requires.

### 1.6 THEIR PUBLISHED QUANTITIES — WHAT EXISTS, AND WHAT IT IS WORTH

**No table of thrust, torque, KT, KQ or efficiency is published anywhere in the 72 files.**
What is published is:

1. **`figures/Force_history.png`** (sha256 `12adfd8475a30fab110c0ea6d92ba854ce2cd93985e5cfeb4a93381731cfb137`)
   — "Force(Y) history", x-axis **Time, s, 0 to 2.5** (therefore the *transient* run, not the
   MRF precursor), y-axis Force, N, 300–400, gridlines every 20 N. The trace settles from
   t ≈ 1.2 s onward to a band lying just above the 320 N gridline.
   **Digitised centre: Fy ≈ 325 N. Read by eye against the gridlines; read uncertainty ±3 N.**
2. **`figures/Moment_history.png`** (sha256 `5951d2e48ee47822f273631a39239cf6823aa842265f9369b4a7e3ecfef99aa0`)
   — "Moment(Y) history", same x-axis, y-axis −10 to −30 N·m, gridlines every 5 N·m. Settles
   from t ≈ 0.8 s to a very tight trace between the −15 and −20 gridlines, nearer −20.
   **Digitised centre: My ≈ −18.0 N·m. Read by eye; read uncertainty ±0.4 N·m.**
3. **The README's spectral statement**, verbatim: *"Narrowband features can be seen at
   multiples of 100 Hz which correspond to the harmonics of blade passage frequency (BPF).
   The peak at 100 Hz at location (1) in the propeller wake is contaminated by the turbulence
   in the wake flow."* Five SPL figures at 1.5–2.5 s accompany it.
4. **The declared cell count 4.07 M** (§1.2) and the two shipped extrusion expansion ratios
   (§4, check C1).

**These four are the entire band. Nothing else.** Items 1 and 2 are **digitisations of raster
figures performed by this lane before any compute**, and they are labelled as digitisations at
every point of use below. They are the case's own published output at the same `nref`, the same
solver and the same operating point — which is exactly what a reproduction rung is graded
against — but they are read off a picture, and the bands in §3 are widened accordingly.

For orientation only, **never as a gate**: at rho 997, n 25 /s, D 0.224 m these digitised
values correspond to KT ≈ 0.207, 10·KQ ≈ 0.512, eta_O ≈ 0.574. **No KT/KQ gate is registered**
and no KT/KQ number will be reported as a verdict.

---

## 2. THE PIPELINE, AS IT ACTUALLY IS IN `Allrun` AT THIS COMMIT

There is **no `Allmesh`** — meshing lives inside `Allrun`. The description below is read off
`Allrun` at commit `0d06b755`; where it differs from the brief I was handed, the file wins.

| # | `Allrun` line | Stage | Ranks | **ETA (wall, 32 ranks)** |
|---|---|---|---|---|
| 1 | 64 | `blockMesh` (tunnel region) | 1 | < 1 min |
| 2 | 65 | `blockMesh -region v_fluid_rotor` | 1 | < 1 min |
| 3 | 66 | `surfaceFeatureExtract` (10 gz'd OBJ surfaces) | 1 | 2–8 min |
| 4 | 67 | `decomposePar` (scotch, 32) | 1 | 1–3 min |
| 5 | 68 | `decomposePar -region v_fluid_rotor` | 1 | 1–3 min |
| 6 | 73–79 | `refineMesh` loop, `nref-1` iterations | 32 | **0 min — at nref=1 the loop body is never entered** |
| 7 | 81 | `snappyHexMesh -overwrite` (tunnel) | 32 | 20–50 min — **RISK** |
| 8 | 82 | `snappyHexMesh -region v_fluid_rotor` | 32 | 20–50 min — **HIGHEST RISK, see D5** |
| 9 | 83 | `topoSet -region v_fluid_rotor` (makes cellZone `v_fluid_rotor`) | 32 | 1–3 min |
| 10 | 84 | `mergeMeshes ./ ./ -addRegion v_fluid_rotor -overwrite` | 32 | 5–20 min — **RISK** (v2206→v2606 CLI; `-addRegion` verified present) |
| 11 | 85 | `createPatch -overwrite` — the four `cyclicAMI` patches | 32 | 3–10 min — **RISK** (`matchTolerance 1e-4`) |
| 12 | 86–91 | expansion ratio Newton solve, then `extrudeMesh` **step1**: 36 layers to R = 0.976 | 32 | 5–20 min |
| 13 | 92–97 | Newton solve, then `extrudeMesh` **step2**: **150 layers** to R = 600 | 32 | 15–60 min — **RISK** (largest layer count) |
| 14 | 98 | `topoSet` (makes cellZone `v_fluid_tunnel` as the inverse) | 32 | 1–3 min |
| 15 | 99 | `renumberMesh -constant -overwrite` | 32 | 3–10 min |
| 16 | 100 | `checkMesh -constant` | 32 | 2–8 min → **G1, G2** |
| 17 | 109–110 | `redistributePar -constant -overwrite`; `restore0Dir -processor` | 32 | 2–5 min |
| 18 | 112 | **`rhoSimpleFoam`, 5000 iterations, MRF on, RAS kOmegaSST** | 32 | **1.3–6.3 h, central 2.5 h** → **G3** |
| 19 | 113 | `rhoSimpleFoam -postProcess -func yPlus` | 32 | 2–5 min |
| 20 | 115–122 | swap to `.tr` dicts; LES on; acoustic damping on; **MRF off**; `replace.sh` (relink 5000 → 0); `changeDictionary` (AMI `lowWeightCorrection`, stem outlet mass flow) | 32 | 2–5 min → **C6, C7** |
| 21 | 124 | **`rhoPimpleFoam`, 25,000 steps, DDES + solid-body AMI** | 32 | **2.6–13.2 days, central 5.3 days** → **G4, G5** |
| 22 | 126 | `Allrun.noise` — 5 × `noise -dict system/noiseDict-points` | 1 | 5–20 min → **G6** |
| 23 | 128 | `gnuplot plot_spectrum` | 1 | < 1 min |

**Mesh pipeline (stages 1–17) central ETA ≈ 3.0 h wall.**
**Whole act central ETA ≈ 5.5 days wall at 32 ranks.**

ETAs are lab estimates on the basis in §6. They are **estimates, not measurements**, and
they are recalibrated at the rate probe (§6.4) rather than defended.

---

## 3. GATES — THRESHOLDS, LABELS AND PREDICTIONS, FROZEN BEFORE COMPUTE

Every label below is drawn from the fixed vocabulary: `PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING`.

| Gate | What is read | Threshold, frozen | Labels | **Prediction** |
|---|---|---|---|---|
| **G0 PROVENANCE** | §0 | subtree id == `ffbde3f1…` at `0d06b755`; disk == archive byte-for-byte; 72 files | PASS / GATE FAIL | **PASS** — and it is already `PASS`, discharged in Stage 1 |
| **G1 MESH BUILT** | `checkMesh -constant` log + `constant/polyMesh/owner` header | total cells in **[3.0 M, 5.5 M]** against the **declared** 4.07 M (`system/parameters:6`); `checkMesh` must complete | PASS / GATE FAIL / BLOCKED | **PASS, 4.0–4.3 M cells** |
| **G2 ROTATING ZONE — LAUNCH PRECONDITION** | `constant/polyMesh/cellZones`, **by name and by cell count**, via reader **R1** | a zone named exactly **`v_fluid_rotor`** with **≥ 100,000 cells**, AND a zone named exactly **`v_fluid_tunnel`**, AND the two counts summing to the G1 total | PASS / GATE FAIL | **PASS**: `v_fluid_rotor` 0.5–1.5 M cells, `v_fluid_tunnel` the remainder, sum exact |
| **G3 STEADY PRECURSOR** | the `rhoSimpleFoam` log and the written time directory | strict completion rule (§7) at **iteration 5000**, a directory named literally `5000`, and `5000/pMean` + `5000/UMean` present | PASS / GATE FAIL / NOT A RESULT | **PASS** |
| **G4 THRUST** | `postProcessing/forces_all/*/force*.dat`, y-component, via reader **R2** | time-mean Fy over **t ∈ [1.5, 2.5] s** inside **325 ± 20 N** (305–345 N, ±6 %) | PASS / GATE FAIL | **318–332 N → PASS** |
| **G5 TORQUE** | `postProcessing/forces_all/*/moment*.dat`, y-component, via reader **R2** | time-mean \|My\| over **t ∈ [1.5, 2.5] s** inside **18.0 ± 1.5 N·m** (16.5–19.5, ±8 %) | PASS / GATE FAIL | **17.6–18.4 N·m → PASS** |
| **G6 BLADE PASSAGE FREQUENCY** | the five SPL spectra from `Allrun.noise`, via reader **R3** | for each probe, the largest spectral peak below 250 Hz at **100 ± 3 Hz**; graded **≥ 4 of the 5 probes** | PASS / GATE FAIL | **PASS at ≥ 4 of 5.** Probe p1 sits in the wake and the README itself says its 100 Hz peak is turbulence-contaminated; p1's outcome is recorded either way and never hidden |
| **G7 REPRODUCTION — the rung's headline** | the whole `Allrun 32` pipeline | all 23 stages complete, rc 0, with **zero** dictionary departures beyond the deviations registered in §5 | GATE REACHED / BLOCKED | **GATE REACHED**, at ~55 % confidence — see §8 |

**Band provenance for G4 and G5, stated where it is used:** the centres 325 N and 18.0 N·m are
**digitisations by eye** of `figures/Force_history.png` and `figures/Moment_history.png`, whose
sha256s are in §1.6 and in the manifest. The read uncertainties are ±3 N and ±0.4 N·m; the
registered half-widths are ±20 N and ±1.5 N·m — deliberately **much wider than the reading
error**, to absorb the v2206→v2606 version drift (§5, D3) which we have no way to bound in
advance. A `GATE FAIL` on G4 or G5 is therefore a strong statement and will be treated as one.

**Milestone, NOT a gate, no verdict attaches:** at t = 1.0 s the running Fy and \|My\| are
reported for progress only.

**A gate can only turn a PASS or GATE FAIL *into* NOT A RESULT, never the reverse**
(standing rule 5). No Roache triple is registered here: this is a single-grid reproduction at
the published `nref`, and **no GCI will be quoted** — there is no grid triple to quote one from.

---

## 4. READERS, PLANTED-ZERO CONTROLS, AND THE STOP RULE IN BOTH DIRECTIONS

Standing rule 3: a zero from a reader not shown able to see a non-zero is not evidence. Every
reader below carries **two limbs** and every plant is applied to a **COPY** of the tree — the
graded tree is never written to.

| Reader | Reads | Plant value and injection point | **Positive limb** (must SEE) | **Negative limb** (must NOT see) |
|---|---|---|---|---|
| **R1** cellZone reader | `constant/polyMesh/cellZones` | (a) in a copy, rename the zone to `v_fluid_rotor_PLANT`; (b) in a second copy, delete exactly **1234** labels from the `v_fluid_rotor` list | (a) reader reports `v_fluid_rotor` **ABSENT**; (b) reader reports a count **exactly 1234 lower** | on the untouched copy the reader reports `v_fluid_rotor` **present** at the unmodified count |
| **R2** force/moment reader | `postProcessing/forces_all/*/force*.dat`, `moment*.dat` | **`PLANT = 1.234e-03`** added to every Fy row (and, separately, every My row) of a copy, **by line index** | reader's time-mean moves by **exactly +1.234e-03** (agreement to 1e-9) | on the untouched copy the reader's mean is bit-identical to the unplanted read |
| **R3** spectrum reader | the probe `pGauge` series and the `noise` output | a pure sinusoid of amplitude 10 Pa at **137 Hz** (deliberately off-BPF and off every BPF harmonic) added to a copy of the probe series | reader reports a peak at **137 ± 1 Hz** | on the untouched copy the reader reports **no** peak at 137 ± 1 Hz |
| **R4** completion reader | solver log, time directories, field files, mtimes | in a copy, delete the `End` line; in a second copy, backdate one `endTime` field below `0/T` | reports **INCOMPLETE** for each, naming the clause that failed | on the untouched copy reports **COMPLETE** |

### THE STOP RULE — **BOTH DIRECTIONS**

> **Stop unless the control passes, in either direction.**
>
> For every reader R: if **either** the positive limb **or** the negative limb fails, the act
> **stops**, the label is **`BLOCKED`**, and **every number that reader produced is DISCARDED
> from the record — a `GATE FAIL` included.** A `GATE FAIL` from a reader that failed either
> limb is not a finding about the case; it is a finding about the reader, and it is recorded as
> such. No verdict of any kind — `PASS`, `GATE FAIL` or `NOT A RESULT` — may be issued from an
> instrument that has not passed **both** limbs on the same day, on the same tree, in the same
> invocation that produced the number.
>
> This is written in both directions deliberately. Earlier in this act a one-directional rule
> returned a `FAIL` from garbage and it was believed.

---

## 5. DEVIATIONS FROM THE PUBLISHED FILES

**Dictionaries are COPIED, NOT RE-TYPED.** The count of *applied* dictionary deviations in
Stage 1 is **ZERO**: no byte of the 72 published files has been modified, and the manifest in
§0 will re-verify at launch. Everything below is either a change of *invocation* (not of a
file), an observation, or a **proposal held for the supervisor's decision at authorisation**.

| # | Kind | What | One-line reason |
|---|---|---|---|
| **D1** | **INVOCATION — applied at launch, zero bytes changed** | run as **`bash ./Allrun 32`**, not `./Allrun 32` | `Allrun` declares `#!/bin/sh` but uses bash-only `for ((…))` (line 73), `[[ … ]]` (49) and `((nIter--))` (51); `/bin/sh` here is **dash**, and `dash -n Allrun` reports *"73: Syntax error: Bad for loop variable"* while `bash -n Allrun` is clean — so the published shebang is simply wrong and we fix the invocation, not the file |
| **D2** | **RESOLUTION of a free parameter, disclosed** | `numberOfSubdomains #eval {$nCPU}` → **32** | their rank count is `argv[1]`, not a published value; 32 is the lane's hard boundary (§8) |
| **D3** | **VERSION DRIFT, disclosed, not chosen** | case "tested in OpenFOAM v2206" (README); this box is **v2606** (`_481094f-20260618`) | we have no v2206; every required model and `mergeMeshes -addRegion` verified present in v2606, but eight releases of drift is a real and unbounded risk and the §3 bands are widened for it |
| **D4a** | **PROPOSED — NOT APPLIED. Supervisor's call at authorisation** | `system/controlDict.st`: `writeInterval 5000` → **`1000`** (one line) | their steady phase writes **once**, at iteration 5000, after ~2.5 h; a crash at 4999 loses everything and `replace.sh:11` hard-requires a directory named `5000`. `purgeWrite 0` is unchanged so `5000` still exists. **If the supervisor prefers strict verbatim, we run it as shipped and accept the restart cost** |
| **D4b** | **PROPOSED — NOT APPLIED. Supervisor's call at authorisation** | `system/controlDict.tr`: `writeInterval 1.0e-01` → **`1.0e-02`** (one line) | at the estimated ~18 s wall per step, their 0.1 s interval is ~1000 steps ≈ **5 h** between checkpoints, far outside a 30-minute policy; 0.01 s is ~100 steps ≈ 30 min. `purgeWrite 1` keeps disk flat, and the acoustic record is unaffected because `probes_pGauge` writes every step regardless |
| **D5** | **PREDICTED FAILURE with a pre-registered, single, bounded remedy** | `system/v_fluid_rotor/snappyHexMeshDict:305` reads **`minMedianAxisAngle 90;`** — misspelled; the main dict has **`minMedialAxisAngle 90;`** correctly at its line 290 | v2606 reads `minMedialAxisAngle` through `meshRefinement::get<scalar>` — a **required** lookup with no default (`src/mesh/snappyHexMesh/externalDisplacementMeshMover/medialAxisMeshMover.C:151-158`) — and `meshShrinker` is unset in both dicts so the default `displacementMedialAxis` mover applies (`layerParameters.C:389-396`). **Prediction: stage 8 (`Allrun:82`) FATALs at `addLayers` with "keyword minMedialAxisAngle is undefined".** **Remedy, authorised in advance IF AND ONLY IF that exact FATAL is observed and its log line quoted:** insert `minMedialAxisAngle 90;` into the rotor dict's `addLayersControls`, matching the main dict's own value. **No other remedy is authorised**, and if a different error appears the act stops and reports |
| **D6** | **OBSERVATION — no action** | `system/createPatchDict` spells it **`lowWeightCorection`** (missing `r`) at four places | upstream repairs its own typo at `Allrun:122` via `changeDictionaryDict`, which spells it correctly; check **C6** asserts the repair landed |
| **D7** | **OBSERVATION — no action** | `0.orig/U` puts `"propeller.*" → fixedValue (0 0 0)` **before** explicit `propellerTip` and `propellerStem1` → `movingWallVelocity` | exact-name match beats regex in OpenFOAM, so Tip and Stem1 move — but **`propellerStem2` has no explicit entry and therefore takes `fixedValue (0 0 0)`** while being one of the three force patches. Check **C7** resolves this **with `foamDictionary` on the staged case**, not by reading. Either way it is their file and it is not changed |
| **D8** | **OBSERVATION — no action** | README says the damping target is "the BPF, 100 Hz"; `system/fvOptions:49` sets `frequency 50;` | an internal inconsistency in the published case; recorded, not corrected |

**Expected applied dictionary deviations at launch: ZERO**, unless the supervisor authorises
D4a/D4b, or unless D5's exact predicted FATAL fires.

---

## 6. COST — CORE-MINUTES AT 32 RANKS, DOLLARS **DERIVED, NOT MEASURED**

Rate **$0.0513 per core-hour** (c7a.4xlarge, owner-stated 2026-08-21/22). **This box cannot
read its own billing, so every dollar figure below is DERIVED, and `cost_basis` is
reported-by-owner, not measured** (`COMPUTE_BUDGET_CHARTER.md` §5).

**Basis, named so it can be attacked:** a lab-measured anchor of **9.25 s per outer iteration
on 32 ranks at 20.66 M cells** (the CRM-WB D8G act; `docs/LAB_STATE.md:46052` for the 9.25 s,
`docs/LAB_STATE.md:45796` for the 20.66 M cells) gives
**r = 1.433e-5 core-s per cell per outer iteration**. Joining those two lines is **an
inference this lane made**, not a single recorded rate, and the whole cost estimate inherits
that weakness. A PIMPLE time step here is taken as **10 SIMPLE-equivalents** (7 outer
correctors, each carrying 2 pressure correctors plus 1 non-orthogonal pass, plus per-step mesh
motion and AMI weight recomputation). Cell count 4.07 M (declared).

### 6.1 MESH PIPELINE (stages 1–17), costed separately as required

| | Central | Range |
|---|---|---|
| Wall at 32 ranks | 3.0 h | 1.5–6.0 h |
| **Core-minutes** | **5,760** | 2,880–11,520 |
| Core-hours | 96 | 48–192 |
| **$ DERIVED** | **$4.93** | $2.46–$9.85 |

### 6.2 STEADY MRF PRECURSOR (stage 18)

5000 iterations × 4.07e6 cells × 1.433e-5 core-s = 291,600 core-s.

| | Central | Range |
|---|---|---|
| Wall at 32 ranks | 2.53 h | 1.3–6.3 h |
| **Core-minutes** | **4,860** | 2,430–12,150 |
| Core-hours | 81.0 | 40.5–202.5 |
| **$ DERIVED** | **$4.16** | $2.08–$10.39 |

### 6.3 TRANSIENT LES DDES SOLVE (stage 21) — **the dominant cost**

Per step: 4.07e6 × 1.433e-5 × 10 = **583 core-s = 9.72 core-min** (≈ 18.2 s wall at 32 ranks).
× 25,000 steps:

| | Central | Range (×0.5 – ×2.5) |
|---|---|---|
| Wall at 32 ranks | **5.3 days** (126.6 h) | 2.6–13.2 days |
| **Core-minutes** | **243,000** | 121,500–607,500 |
| Core-hours | 4,050 | 2,025–10,125 |
| **$ DERIVED** | **$207.8** | $103.9–$519.4 |

### 6.4 ACT TOTAL, AND THE RATE PROBE

| | Central | Range |
|---|---|---|
| **Core-minutes** | **253,620** | 126,810–631,170 |
| Core-hours | 4,227 | 2,114–10,520 |
| Wall at 32 ranks | **5.5 days** | 2.7–13.7 days |
| **$ DERIVED, NOT MEASURED** | **$216.9** | $108.4–$539.6 |

**Rate probe, registered now.** After the first **100** transient time steps, `ExecutionTime`
per step is measured from the log and §6.3 is recomputed from the measured rate. If the
measured rate exceeds **2×** the central estimate, the lane reports to the supervisor before
continuing. **This is a recalibration, not a cap** — Sanaa's ruling of 2026-09-12 (directive
#17) stands: **no run is stopped by a time or budget cap**, and this registration contains no
cap and no kill point. The probe exists so that progress can be reported honestly, and so that
the estimate-versus-actual row required by standing rule 12 can be filed at completion against
a real number.

**Estimate-versus-actual calibration is owed at completion** into `docs/COST_CALIBRATION.md`,
stating actual core-minutes from the logs, the ratio actual/predicted, and the attribution of
the gap — with waste named separately, never absorbed into the ratio.

---

## 7. THE COMPLETION RULE, AS IT APPLIES HERE

A run is done only if **all** of it holds (standing rule 4), via reader **R4**:
`rc = 0`; an `End` line in the log; **last written time == `endTime`** (5000 for the steady
phase, 2.5 for the transient); the expected fields present; `ExecutionTime` count consistent
with the step count (`deltaT` is 1 for the steady phase — the unit-step case — and fixed at
1e-4 for the transient since `adjustTimeStep no`, so `n_exec == steps written` applies
directly in both); and **every field at `endTime` newer than the case's own `0/T`** — the age
guard. A run failing any clause is **not done**, and R4 refuses rather than degrades.

Note for the transient: `Allrun:121` runs `system/replace.sh`, which renames the steady `5000`
directory to `5000_steadyState` and symlinks it as `0`. The age guard therefore dates against
the **relinked** `0/T`, which is the steady result — correct, because that is the field the
transient was allowed to start from.

---

## 8. HONEST DIFFICULTY — WHERE THIS WILL BREAK, AND WHETHER 32 RANKS IS ENOUGH

**This case is HARDER than PPTC VP1304, not easier.** That was the cfd-supervisor's own survey
judgement before Sanaa chose the case, and reading the 72 files has confirmed rather than
softened it:

- **Same rotating-machinery requirement**, and then more: PPTC is MRF alone; MB13 is MRF **and**
  a solid-body-rotating cellZone across four `cyclicAMI` patches, with AMI weights recomputed
  every one of 25,000 time steps.
- **A harder layer problem.** Two `extrudeMesh` stages whose expansion ratios are found by a
  **Newton iteration written in shell arithmetic** (`Allrun:34-54`), 36 then **150** layers.
  This is one of the two cases `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md:132` cites for
  pinning layer thickness in **absolute metres** — `relativeSizes false`
  (`system/snappyHexMeshDict:275`), `firstLayerThickness 1e-4 m` on the tip. We already studied
  this case *because* its layers are hard.
- **A compressible-acoustics LES stack this lab has never run**: `kOmegaSSTDDES` with a
  `vanDriest` delta, a `DEShybrid` divergence scheme from an external scheme library,
  `acousticDampingSource`, and `perfectFluid` water at c ≈ 1475 m/s.
- **Eight OpenFOAM releases of drift** (v2206 → v2606), with one concrete defect already found
  by reading (D5) and no way to bound what else moved.

**The stages most likely to fail, in order:**

1. **Stage 8 — `snappyHexMesh -region v_fluid_rotor` (`Allrun:82`).** D5: `minMedianAxisAngle`
   is misspelled and v2606's lookup is required-with-no-default. **This is a prediction, not a
   worry**, and its single remedy is pre-registered above.
2. **Stage 13 — `extrudeMesh` step2, 150 radial layers to R = 600 m.** The largest layer count
   in the pipeline, on a merged mesh, in parallel.
3. **Stage 11 — `createPatch`, the four `cyclicAMI` patches at `matchTolerance 1e-4`.** If the
   AMI weights come out poor the transient is worthless no matter how well it runs; `Allrun:122`
   exists precisely because upstream hit this (`lowWeightCorrection 0.1`).
4. **Stage 10 — `mergeMeshes -addRegion`.** The CLI is verified present in v2606, but this is
   the one stage whose interface is known to have moved between releases.
5. **Stage 21 — the transient itself**, on duration alone: 25,000 steps is the single largest
   commitment this lane has registered.

**Is 32 ranks adequate? Stated plainly: it is workable but it is NOT comfortable, and the lab
has no measured basis for it at this size.**

- **Cells per rank at 32 on the declared 4.07 M count: `4.07e6 / 32 = 127,188`.**
- That is **below the ~200,000 cells/rank floor** under which this box has **no measured
  strong-scaling basis at all**. We are therefore running in a regime where communication
  cost per rank is un-characterised here, and the §6 estimate — built from a 20.66 M-cell,
  32-rank anchor at 646k cells/rank — is being extrapolated **5× down** in cells per rank.
  **That extrapolation is the single weakest number in this registration**, which is why the
  rate probe in §6.4 exists and why the cost range spans ×0.5 to ×2.5.
- Against that: 32 ranks is 2× the README's own example invocation (`./Allrun 16`), the
  per-rank memory is trivial at this size, and the AMI interface is a per-step collective
  whose cost grows with rank count — so fewer, fatter ranks are not obviously wrong here.
- **Confidence that G7 `GATE REACHED` is achieved on the first attempt: ~55 %**, with D5
  the most likely single cause of a stop and the mesh pipeline as a whole the most likely
  phase. **A failure here is a predicted outcome, not a surprise**, and this section is the
  record that says so before the fact.

### RANKS — THE HARD BOUNDARY, AND HOW I VERIFIED IT

**32 ranks. Not 48, not DrivAer's.** Sanaa's standing words: *"nobody touches or steals the
propeller's cores or the drivaer ones."* Idle reserved ranks stay idle.

What I could verify on disk, and what I could not:

- The seven SUBOFF `L1M_SWEEP` points each carry `numberOfSubdomains 4`
  (`verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_SWEEP/BETA_{m12,m08,m04,p00,p04,p08,p12}/system/decomposeParDict`),
  **7 × 4 = 28** — which is exactly the SUBOFF sweep allocation in Sanaa's 96-core table
  (`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md` §A).
- **The 28-subdomain trap named in my brief is real**: the *older* top-level tree
  `verification/runs/navier_class/SUBOFF_A1H_DRIFT/BETA_p00/system/decomposeParDict` carries
  `numberOfSubdomains 28` on its own. Counting that file **and** the seven at 4 each would
  double-count SUBOFF's allocation. I counted **only** the `L1M_SWEEP` seven.
- Sanaa's table reserves **16 ranks** for "Real propeller / rotor", *"held empty until the case
  is chosen"*, and MB13 **is** that lane's case. Its table rule also permits a lane's free ranks
  to be lent while it has nothing queued, returnable the moment its next case registers.
- The chief's record Y (commit `a84cd8184`) states **"32 ranks free for MB13"** after SUBOFF
  and the DrivAer fine run were stopped. **I could not reconstruct the number 32 from any
  single artifact**; the nearest artifacts are the table's 16-rank propeller reserve and the
  chief's 32. My honest reading is 16 (MB13's own reserve) + 16 lent from the idle SUBOFF 28,
  returnable on SUBOFF's next registration — but **that reading is mine, and I flag it rather
  than assert it.** 32 is registered because it is the supervisor's hard boundary.
- Live check at registration: `nproc` 96, 1-minute load average 1.22, **no `mpirun`/`mpiexec`
  process running**. The box is effectively idle; that is a fact about load, not a licence to
  take more than 32.

---

## 9. REFUSAL LIMBS — WHAT SAYS THE INSTRUMENT IS WRONG, NOT THE CASE

Each of these produces **`BLOCKED`**, never `GATE FAIL`:

1. **The Newton self-check (C1) fails.** `Allrun:88` and `:94` must return expansion ratios
   matching the ratios already shipped in the dicts. This lane reproduced their algorithm
   exactly and got **1.06399012914648** (step1, dict ships `1.06399`) and
   **1.04016441327821** (step2, dict ships `1.04016`), with the geometric sums closing on
   0.976 and 600.000 to 17 significant figures. **If the pipeline's own Newton solve does not
   return those two numbers to 6 s.f. at nref=1, the harness is wrong, not the case.**
2. `checkMesh` reports **0 cells** in `v_fluid_rotor`, or `cellZones` is absent entirely —
   a meshing-instrument failure, and the transient is not launched.
3. The `forces` function object reports any of `propellerStem1`, `propellerStem2`,
   `propellerTip` **not found** — the force reader is pointed at nothing, so G4/G5 read nothing.
4. `probes_pGauge` reports any of the five locations **outside the mesh** — G6 reads nothing.
5. A required model is missing from this build (`kOmegaSSTDDES`, `acousticDampingSource`,
   `DEShybrid`, `libturbulenceModelSchemes.so`, `mergeMeshes -addRegion`). **All were verified
   present in v2606 at registration, so this limb should never fire**; if it does, the build
   changed under us.
6. **Any reader failing either limb of §4** — the stop rule, in both directions.

---

## 10. RUN-TIME CHECKS THAT ARE NOT GATES

| | Check | Where | Expected |
|---|---|---|---|
| **C1** | Newton expansion ratios at nref=1 | `Allrun` stdout, lines 89 and 95 | `1.06399…` and `1.04016…` — refusal limb 1 if not |
| **C2** | manifest re-verified at launch | `UPSTREAM_MANIFEST.sha256` vs the staged tree | 72/72 match, or the run does not start |
| **C3** | `numberOfSubdomains` resolved | staged `system/decomposeParDict` after `#eval` | literal **32**, both regions |
| **C4** | built cell count vs declared | `checkMesh` log | recorded as **built**; 4.07 M recorded as **declared** — never conflated |
| **C5** | `yPlus` after the steady phase | `Allrun:113` output | recorded per patch, no gate attached |
| **C6** | AMI repair landed | `constant/polyMesh/boundary` after `changeDictionary` | `lowWeightCorrection 0.1` on all four AMI patches (D6) |
| **C7** | `propellerStem2` velocity BC | `foamDictionary` on the **staged** case, not by reading | resolves the D7 regex-vs-exact question with the tool, not the eye |
| **C8** | AMI weight quality | solver log, first transient steps | min weights recorded; a `lowWeightCorrection` trigger is reported, not hidden |

---

## 11. WHAT IS NOT REGISTERED HERE, AND WILL NOT BE CLAIMED

- **No `KT`, `KQ` or `eta_O` verdict.** The orientation values in §1.6 are orientation only.
- **No Roache triple, no GCI, no order of convergence.** One grid, at the published `nref`.
- **No comparison to PPTC VP1304.** A different propeller is not a comparator.
- **No claim from `GT2018-76932`.** Not retrieved, not title-page verified, not used.
- **No submission of anything, anywhere** (standing rule 7). Submissions are parked; sending
  is Sanaa's decision alone.

---

## 12. FREEZE

This file is frozen at its commit. Before first compute, an amendment is legal **only** if it
states its condition and how that condition was checked by naming a run directory that does
not exist — and at the moment of this freeze **no run directory for MB13 exists anywhere on
this box**. After first compute, the gates, thresholds, caps and labels in §3, §5 and §6 are
closed; changes land only as dated addenda that cannot alter them, and originals are struck,
never rewritten. The grading path is fixed at this commit, and the frozen file will be hashed
against the committed blob to prove it is the file that ran.
