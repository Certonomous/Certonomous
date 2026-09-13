# DrivAer R5 `r5_wallfunction` — STORED AND SET ASIDE

**STATUS: `PENDING` — not graded, by Sanaa's ruling. Nothing failed.**

Sanaa's ruling, in her own words, is that R5 *"gets stored and set aside till we look
at it and grade it later since wolf dynamics case is provenly good."* This document
discharges **stored**. It does **not** grade R5, does not evaluate any gate, and
carries **no verdict** on M1, L, L2, S1 or Y1. Every number below is a **measurement
transcribed from the build's own artifacts** or an explicitly-labelled **prediction**.
Nobody may read a PASS or a GATE FAIL out of this file: none is written here, and the
absence is deliberate.

**No solver ran.** The build produced a mesh and stopped. `Y1` cannot even be read,
because it is defined on a **solved** `yPlus` field.

- **Run tree:** `/home/ubuntu/Certonomous/verification/runs/navier_class/DRIVAER/r5_wallfunction/`
- **Pre-registration (frozen):** `verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md`,
  freeze commit `38aab8e78662d574d1b14b61da7efc5898be5c7e`
- **Build launched:** 2026-09-13T18:16:28Z (`RUN_PIN.txt`) — **stopped, stored, 2026-09-13**

---

## 0. WHY THIS DOCUMENT EXISTS AND WHAT IT MUST SURVIVE

"Stored and set aside" is only true if **a later reader can grade this run without
rebuilding it**. A 6.6 GiB mesh tree does not go into git (rule: data too large for git
lives outside it; `constant/polyMesh/` is `.gitignore`d at line 66). So the *evidence*
is committed — every log, the dictionary, the timing and return codes, ~510 KiB in
total — and the *mesh* is left on disk and **pinned by hash** below. The grader who
picks this up later reads the committed logs; if they need the mesh itself, the hashes
here prove the tree on disk is the tree this document describes.

---

## 1. COMPLETION — MEASURED

| clause | value | source |
|---|---|---|
| `blockMesh` | rc = 0, 1.13 s | `BUILD_RC` |
| `surfaceFeatureExtract` | rc = 0, 4.31 s | `BUILD_RC` |
| `decomposePar` | rc = 0, 2.36 s, **16 ranks** | `BUILD_RC`, `RUN_PIN.txt` |
| `snappyHexMesh` | rc = 0, **45:07.29** wall, peak RSS 4.15 GB | `BUILD_RC` |
| snappy's own timer | **`Finished meshing in = 2724.78 s.`** | `log.snappyHexMesh:9260` |
| illegal faces at exit | **`Finished meshing with 64 illegal faces`** (concave, zero area or negative cell pyramid volume) | `log.snappyHexMesh:9259` |
| `reconstructParMesh` | rc = 0, 3:16.05 | `BUILD_RC` |
| `checkMesh -allGeometry -allTopology` | rc = 0, 6:16.68, ends `End` | `BUILD_RC`, `log.checkMeshFull` |

**One incomplete artifact, disclosed rather than hidden:** `log.checkMeshPlain` stops at
`Create time` and `time.checkMeshPlain` is **0 bytes**. The *plain* `checkMesh` was still
starting when the fleet was killed by the session limit at ~19:10Z. It is **not** needed —
`log.checkMeshFull` is the superset, it completed, and it is what §3 reads. The stub is
left on disk unaltered.

---

## 2. CELL COUNT — MEASURED, NOT GRADED

| stage | cells | source |
|---|---|---|
| snapped mesh | **16,431,518** | `log.snappyHexMesh:3081` |
| layer mesh | **17,473,596** | `log.snappyHexMesh:9177` and `:9237` |
| `checkMesh` confirmation | **17,473,596** cells, 52,776,645 faces, 17,836,683 points | `log.checkMeshFull` |

`checkMesh` is an independent reader and it agrees with snappy to the digit. The M1 band
in the registration is 15–20 M. **This document states the number and stops there.**

### 2.1 🔴 THE QUALIFIER THAT MUST TRAVEL WITH THAT NUMBER: **INSIDE BY LUCK, NOT BY DESIGN**

The builder's sizing model, recorded in `DICT_GENERATION.txt` before the build, was:

> `layer gain is face-driven, NOT volume-driven: 80,974 wall faces x 90% x 8 = 0.58 M cells
> -> PREDICTED FINAL ~16.90 M against the 15-20 M M1 gate`

**The face-driven half of that model is right. The face count in it is wrong, and wrong by
a factor of 2.7.**

| quantity | builder's value | measured | source |
|---|---|---|---|
| extrudable faces | 80,974 (carried from `r2_medium`) | **219,926** | `log.snappyHexMesh:9179ff` |
| cells added by layers | 583,013 predicted | **1,042,078** measured | 17,473,596 − 16,431,518 |
| final cells | ~16.90 M predicted | **17,473,596** measured | `log.checkMeshFull` |

**THE CORRECTED MODEL: layers scale with WALL FACES, and volume refinement over a wall
patch CREATES wall faces.** R5's `refinementSurfaces` block is byte-identical to
`r2_medium`'s (asserted by `make_r5_dict.py`, which exits 2 otherwise), so the builder
assumed the wall-face count was identical too. It is not. The R5 volume-refinement boxes
sit **over the ground plane**, and every level of volume refinement that reaches a wall
patch subdivides that patch's faces. `floorNoSlip` alone went from **5,505** extrudable
faces at `r2_medium` (recorded in the freeze commit message of `38aab8e7`) to **155,318**
here — a 28× increase produced entirely by volume refinement, with no change to any
surface level.

**Therefore: a larger volume-refinement box would have failed M1 HIGH, and it would have
failed for a reason the builder's model could not see.** It would have raised the
castellated count *and*, through the newly created wall faces, the layer count on top of
it — a compounding the 0.58 M figure does not contain. The mesh landed 2.53 M under the
20 M ceiling; that margin was not engineered, it was inherited from a box size chosen
against the wrong face count. **This is recorded as a defect in the sizing model, not as a
gate outcome.**

### 2.2 L-590's THIRD READING, AND IT AGREES

The achievement table's own `faces × achieved layers` sums to **1,042,577** cells against
the measured cell delta of **1,042,078** — **0.048 %**. The layers in this mesh are
**real**, not a request echoed back. *(This is a CELL-COUNT reconciliation. It is not, and
must not be read as, a blended layer average — see §4.)*

---

## 3. `checkMesh` — MEASURED, NOT GRADED

`checkMesh -allGeometry -allTopology -constant`, rc = 0, 6:16.68 wall
(`log.checkMeshFull`, sha256 `b4b44f59…`):

| check | measured | line |
|---|---|---|
| **Max skewness (gate S1's quantity)** | **4.4868345**, 2 highly skew faces, written to set `skewFaces` | `:167` |
| Mesh non-orthogonality | Max **64.979419**, average **3.1952353** — *"Non-orthogonality check OK"* | `:164` |
| Max aspect ratio | 45.211636 — OK | tail |
| Max cell openness | 1.2188244e-15 — OK | tail |
| Boundary openness | (−5.54e-17, 3.65e-17, −3.82e-13) — OK | tail |
| Min / max cell volume | 1.9538716e-08 / 0.064666199 m³; total 12,473.369 m³ — OK | tail |
| Min / max face area | 2.8994606e-07 / 0.1616602 m² — OK | tail |
| Face pyramids | OK | tail |
| Cell determinant | min **0**, average 0.99140166; **1,178 cells** below 0.001 | tail |
| Concave cells (face planes) | **174,576** | tail |
| Faces with concave angles | 3,378, max concave angle 79.964079° | tail |
| Warped faces (proj/actual < 0.8) | 154; min flatness 0.34589753 | tail |
| Low interpolation weight (< 0.05) | 64 faces; min weight 0.023772884, average 0.49565605 | tail |
| Edges too small | 2; min/max edge 5.5534695e-05 / 0.40428849 m | tail |
| Face volume ratio | min 0.011540275, average 0.98163516 — OK | tail |
| **Summary line** | **`Failed 4 mesh checks.`** | tail |

Cell-type census: 17,256,933 hexahedra, 207,612 polyhedra, 8,585 prisms, 419 tet wedges,
42 tetrahedra, 5 wedges, 0 pyramids. Domain bounding box
(−14.339 −10 −0.319) → (37.661 10 11.681) m.

**S1's threshold is `< 4.0`. The measured value is `4.4868345`. THIS DOCUMENT DOES NOT
DECLARE A GATE OUTCOME** — Sanaa's ruling puts grading later, and §7 of the registration
attaches a claim cap to S1 that a grader must apply in full rather than inherit from a
one-line summary here. The number is recorded so that grading needs no rebuild.

---

## 4. LAYER COVERAGE — THE POST-EXTRUSION ACHIEVEMENT TABLE

### 4.1 WHICH TABLE THIS IS, AND WHICH ONE IT IS NOT (L-590)

`log.snappyHexMesh` contains **two** tables with a `patch / faces / layers` shape:

- **`:3257` — THE REQUEST TABLE. NOT EVIDENCE.** Its sub-header is
  `faces / layers / avg thickness[m] / near-wall / overall`, it prints **`8`** and
  **`0.0119`** for *every* patch because those are the *asked-for* values, and it sits
  **before `Outer iteration : 0` at `:3312`**. This is L-590 and it has bitten this act
  twice. **It is not quoted here.**
- **`:9179` — THE POST-EXTRUSION ACHIEVEMENT TABLE.** Its sub-header carries
  `target / mesh / [m] / [%]`, it sits **after** all 50 outer iterations and immediately
  before `Layer mesh : cells:17473596` at `:9237`. **This is the table below.**

### 4.2 `floorNoSlip` — REPORTED ON ITS OWN LINE, OUTSIDE ANY GATE POPULATION

```
floorNoSlip                  155318   8        5.77     0.00885   74.6
```

**155,318 faces, 5.77 achieved layers of 8 requested, 8.85 mm overall stack = 74.6 % of the
registered 11.86 mm.** `floorNoSlip` is a **blockMesh ground plane**: it appears nowhere in
`refinementSurfaces`, it is not one of the 49 vehicle patches, and **it contributes nothing
to Cd**. It carries **155,318 of the 219,926 extrudable faces — 70.6 %** — at more than
double the layer count the vehicle achieves.

🔴 **NO BLENDED FIGURE IS GIVEN IN THIS DOCUMENT, ANYWHERE, IN ANY FORM.** Not in a
footnote, not annotated, not "for completeness". Averaging the ground plane into the
vehicle produces a number that is arithmetically correct and physically meaningless, and
the freeze commit of `38aab8e7` records that exact confusion costing this act a
reconciliation on `r2_medium` (its ground plane flattered the global average by 35 %).
The registration's Gate L is defined on **vehicle patches only**. The two vehicle
populations are therefore reported **separately**, and the ground plane **separately
again**, and they are never combined.

### 4.3 THE TWO VEHICLE POPULATIONS, SEPARATELY

Classification is by each patch's own `level (n n)` entry in
`system/snappyHexMeshDict` (sha256 `3df22e77…`), read patch by patch — not inferred.

| population | surface cell | patches | **faces** | achieved layers, face-weighted | overall thickness, face-weighted | patches at zero layers |
|---|---|---|---|---|---|---|
| **surface level 4** | **25.0 mm** | 37 | **54,439** | **2.271** of 8 | **45.34 %** of 11.86 mm | 6 |
| **surface level 5** | **12.5 mm** | 12 | **10,169** | **2.238** of 8 | **45.53 %** of 11.86 mm | 3 |

Zero-layer patches, named rather than summarised — level 4: `BrakeDiscfront`,
`BrakeDiscrear`, `Rimsrear`, `WheelSupportfront1`, `WheelSupportfront2`, `WheelSupportrear`.
Level 5: `ExhaustSystem1`, `TirePlinthfront`, `TirePlinthrear`.
(`TirePlinthfront` and `TirePlinthrear` carry **0 faces** in the mesh at all, so their zero
is an absence, not a failure to extrude.)

**The two populations land within 1.5 % of each other on layers and within 0.5 % on
thickness.** Halving the surface cell did essentially nothing to layer coverage — which is
what §A1.5 of the registration predicted, and it is stated here as a measurement, not as a
gate reading.

### 4.4 THE TABLE VERBATIM, AS `log.snappyHexMesh:9179` PRINTS IT

```
patch                        faces        layers        overall thickness
                                      target   mesh     [m]       [%]
-----                        -----    -----    ----     ---       ---
floorNoSlip                  155318   8        5.77     0.00885   74.6    
BodyA_Pillar                 418      8        0.342    0.000842  7.1     
BodyDoorhandles              527      8        0.546    0.00117   9.84    
BodyFasciafront1             3062     8        2.02     0.00643   54.2    
BodyFasciafront2             196      8        0.673    0.00166   14      
BodyFender                   1587     8        2.52     0.0077    65      
BodyHeadlamps                807      8        3.03     0.00887   74.8    
BodyHood                     2028     8        5.53     0.0107    89.9    
BodyRear                     2343     8        1.45     0.00463   39.1    
BodyRearAccess               414      8        3.43     0.00933   78.7    
BodyRocker                   2810     8        4.92     0.0105    88.7    
BodyRoof                     587      8        4.96     0.0103    86.6    
BodySide                     5668     8        5.54     0.0105    88.9    
BodyWindowfront              1486     8        4.85     0.00986   83.1    
BodyWindowfrontframe         131      8        0.084    0.000244  2.06    
BodyWindowSide               678      8        2.77     0.00806   67.9    
BodyWindowsideframe          250      8        1.14     0.0031    26.2    
BrakeDiscfront               360      8        0        0         0       
BrakeDiscrear                372      8        0        0         0       
ClosedGrillLowerInsert       445      8        1.66     0.00527   44.4    
ClosedGrillUpperInsert       694      8        1.89     0.0059    49.7    
CTRL_SURFACE_Outlet          235      8        0.34     0.000747  6.3     
CTRL_SURFACE_Wheelhouse_LHS  66       8        3.14     0.00996   83.9    
CTRL_SURFACE_Wheelshouse_RHS 66       8        3.14     0.00996   83.9    
EngineUndershield            750      8        3.15     0.00839   70.9    
ExhaustSystem1               28       8        0        0         0       
ExhaustSystem2               3024     8        0.848    0.0021    17.7    
ExhaustSystem3               413      8        0.22     0.000452  3.81    
Mirrors1                     1179     8        0.901    0.00279   23.5    
Mirrors2                     242      8        1.79     0.00547   46.1    
NotchbackB_Pillar            216      8        1.07     0.00312   26.3    
NotchbackBodyside            696      8        2.48     0.00868   73.2    
NotchbackC_Pillar            1015     8        1.28     0.00439   37      
NotchbackRoof                1940     8        6.2      0.011     92.6    
NotchbackTrunk               1172     8        3.3      0.00869   73.3    
NotchbackWindowrear          1048     8        4.12     0.0092    77.7    
NotchbackWindowrearframe     35       8        0.171    0.000447  3.77    
NotchbackWindowside          1183     8        2.7      0.00773   65.2    
NotchbackWindowsideframe     556      8        1.16     0.00392   33.1    
OCDADetailedUnderbody        17191    8        1.33     0.00376   31.7    
Powertrain                   1290     8        0.212    0.000516  4.35    
Rimsfront                    1185     8        0.00675  7.83e-06  0.066   
Rimsrear                     1178     8        0        0         0       
TirePlinthfront              0        8        0        0         0       
TirePlinthrear               0        8        0        0         0       
Tiresfront                   2044     8        0.0455   9.61e-05  0.811   
Tiresrear                    2045     8        0.0186   4.59e-05  0.387   
WheelSupportfront1           493      8        0        0         0       
WheelSupportfront2           184      8        0        0         0       
WheelSupportrear             271      8        0        0         0       
```

Extrusion convergence, for the grader: the first outer iteration extruded
**171,932 / 219,926 faces (78.177205 %)** (`:3488`), the last **157,976 / 219,926
(71.831434 %)** (`:9170`) — a monotone 50-iteration decay removing 27,112 faces on the
first pass and 64 on the last.

---

## 5. y⁺ — **PREDICTED, NOT MEASURED. NO SOLVER RAN.**

There is no `yPlus` field in this tree and there cannot be one: the case has no time
directory beyond the mesh. Everything in this section is arithmetic from the registered
first-cell height against `r2_medium`'s **measured** anchor, and is labelled as such.

- **Anchor (MEASURED, on `r2_medium`):** area-weighted median y⁺ = **153.1** at a first
  layer of 0.2048 × 25.0 mm = **5.12 mm** (registration §4.1).
- **R5's registered first layer (absolute sizing, `relativeSizes false`):**
  `firstLayerThickness 0.0010 m`, `expansionRatio 1.11`, stack 11.86 mm = 0.474 c.

| face population | first cell | **PREDICTED** y⁺ |
|---|---|---|
| any face carrying ≥ 1 layer | 1.000 mm | **≈ 29.9** |
| level-4 face at **zero** layers | 25.0 mm surface cell | **≈ 748** |
| level-5 face at **zero** layers | 12.5 mm surface cell | **≈ 374** |

Three caveats, all of which a grader must carry:

1. **y⁺ ∝ t₁ holds at fixed `u_tau`.** This mesh is ~18× `r2_medium`'s cell count and
   better-resolved separation moves `u_tau` locally. The registration calls this a
   first-order prediction and not a guarantee, and that is why Y1 is a **gate** rather
   than a note.
2. **The prediction has no slack by construction.** §4.2 of the registration shows that
   8 layers, y⁺ ≥ 30 and a refined surface cell are **not jointly satisfiable**; the recipe
   sits at the bottom edge of the 30–100 window because the extrusion constraint puts it
   there.
3. **Nine patches carry zero layers** (§4.3) and their predicted y⁺ is one to two orders of
   magnitude above the window. Y1 is defined as an **area-weighted median over the 47
   vehicle patches of a SOLVED field**; it cannot be evaluated, estimated or anticipated
   from this document.

---

## 6. THE POINTER — HASHES THAT PIN THE TREE ON DISK

The tree is **7,042,915,434 bytes (6.6 GiB)** across 19 top-level files, 16 `processor*`
directories and a reconstructed `constant/polyMesh/`. `constant/polyMesh/` is
`.gitignore`d (`.gitignore:66`, `**/constant/polyMesh/`). **The mesh is not in git and
must not be put there.**

**Committed with this document** (the complete grading evidence, ~510 KiB):

| file | sha256 | bytes |
|---|---|---|
| `BUILD_RC` | `6a3b84bb38b0592a82b643576e7a02f0f47a8e3b32bdd344a8311777aa778e07` | 900 |
| `RUN_PIN.txt` | `ab2f2c83c89a251d50a27a297e01aabe37122fde9699333324f06e291eedb8ae` | 701 |
| `DICT_GENERATION.txt` | `2458f2f459e25d57a0b289c80e364a5fb584282e75581140258c26d56130339a` | 1117 |
| `THE_ONE_CHANGE.diff` | `871ce40be47bde9e0e2a59e2a38dcd2c7b59a08c1850643586d638bfbcd05624` | 6343 |
| `log.blockMesh` | `8ed40ade890a6068f5a9d43b3befa19b5c153d95d0a706fcf9ee5a78b66c6007` | 2869 |
| `log.surfaceFeatureExtract` | `a2bbfa687aaa889536e42be62da7d4152ba07e79693447bbb650e5c7a2659a5f` | 2853 |
| `log.decomposePar` | `b640be8caed2695e40f1ac17999e18dcc1a676a35abf0ba38d0bc5f4f9a50c51` | 10332 |
| **`log.snappyHexMesh`** | `3754dc76992b0b1b8912f1195fddc0c49d02c89f45e67ff06bd0f0a92442425f` | 460175 |
| `log.reconstructParMesh` | `903e7c6c8d8242db98c0f6aba22172d8646bb0e74d9589f0b3db630c1e8e1844` | 6602 |
| **`log.checkMeshFull`** | `b4b44f59d658821d75a5e43335b32f4acb7b29bce1768b5297ea6ff4cba51550` | 13535 |
| `log.checkMeshPlain` (stub, §1) | `a776fd8a0c2a0765e74e1dd26d10c08f9731b01e3aefca80e49c0f76ab03b82b` | 1448 |
| **`system/snappyHexMeshDict`** | `3df22e770c43941c078c94bee5666c799ab9a9960b42ab51b39c4a6a4ae8d800` | 9904 |
| `system/blockMeshDict` | `942d8ab1f0ce62b919d917ccf2da7b6ca6457c0eba71cd894a29c5cdb0d7acdc` | — |
| `system/controlDict` | `0f9d13d837c04195a093a9d4eaad17f958d835e929359cdbaa83776de416342c` | 475 |
| `system/meshQualityDict` | `04be32ed9817c2a150b73804e1a76f96300a63405e34abc09b27b00ac7439c30` | 533 |

The `snappyHexMeshDict` sha256 above **matches the value `RUN_PIN.txt` pinned at launch**
— `3df22e77…` in both — so the dictionary in this tree is the dictionary that ran.

**NOT in git, pinned by hash, left on disk** —
`verification/runs/navier_class/DRIVAER/r5_wallfunction/constant/polyMesh/`:

| file | sha256 | bytes |
|---|---|---|
| `boundary` | `fba583c2ed6c141b1333a577505baec9963be4daaa2f9b5de7dc37c92a67ec72` | 9,369 |
| `owner` | `7d3e01050d9618a9dcc0908c9e030a3f70fabc51cf62b70134e9a6d5f9356701` | 441,343,614 |
| `neighbour` | `d37e7842fbb881f4fbc0b6a472063a4f3ab1a45a43b25de8dfda8073646af11d` | 439,503,698 |
| `points` | `423005b3026454eeaa02f42a221594b68dcc379a45c676c8a15ba1a201eddf90` | 456,754,674 |
| `faces` | `5007a3cf0da5c2796ce685f6a1a5bf8875a6e9daecd810a71b8ca5f69b1633dd` | 1,929,412,424 |

The 16 `processor*/` decomposed copies are also on disk and are **not** hashed here: the
reconstructed mesh above is the authoritative artifact and `reconstructParMesh` exited 0.

---

## 7. THE NEIGHBOURING TREE THAT IS **NOT** THIS ONE

`verification/runs/navier_class/DRIVAER/r5_wallfunction_TRIAGE_STOP_perpatch5_20260913T181454Z/`
is a **different, earlier, stopped build**. It is labelled **`NOT A RESULT`** in its own
`TRIAGE_STOP.txt` and `EXTERNAL_KILL.txt` and **is left exactly as it stands — untouched,
un-relabelled, un-graded, and not merged into anything here.**

It is kept because it is the **evidence for a lesson**: *a control on the edit is not a
control on the meaning.* The edit it carried was verified to have been applied correctly;
what was not verified was what the edit **meant** for the mesh. Deleting that tree would
delete the proof.

---

## 8. COST OF THE STORED BUILD — MEASURED, WITH DOLLARS DERIVED

From `BUILD_RC`'s own `/usr/bin/time` records, at the rank counts each utility actually
used (`RUN_PIN.txt`: `ranks=16`, `build_procedure=PARALLEL np=16`):

| utility | ranks | wall s | **core-minutes** |
|---|---|---|---|
| `blockMesh` | 1 | 1.13 | 0.019 |
| `surfaceFeatureExtract` | 1 | 4.31 | 0.072 |
| `decomposePar` | 1 | 2.36 | 0.039 |
| **`snappyHexMesh`** | **16** | **2,707.29** | **721.94** |
| `reconstructParMesh` | 1 | 196.05 | 3.268 |
| `checkMesh` (full) | 1 | 376.68 | 6.278 |
| **total** | | | **731.62 core-minutes** |

🔴 **A CLOCK DISCREPANCY THIS LANE COULD NOT RESOLVE, AND STATES RATHER THAN SMOOTHS.**
`/usr/bin/time` measures snappy's elapsed wall clock as **45:07.29 = 2,707.29 s**
(`time.snappyHexMesh`, `Exit status: 0`), while snappy's own closing line reports
**`Finished meshing in = 2724.78 s.`** (`log.snappyHexMesh:9260`). The internal figure
**exceeds** the external one by **17.49 s (0.65 %)**, which cannot be true of two clocks
timing the same interval. This lane did not determine which clock the OpenFOAM line reads.
**The table above uses the externally-instrumented wall clock**, because `/usr/bin/time`'s
meaning is unambiguous; using snappy's figure instead would raise the total to 736.28
core-minutes, a 0.6 % difference that changes nothing and is recorded so nobody later has
to wonder which number was used. `/usr/bin/time` also records **user 40,884.78 s + system
1,590.56 s at 1568 % CPU**, i.e. 15.68 of 16 ranks busy — an independent confirmation that
16 ranks really ran.

**Dollars: 731.62 / 60 × $0.0513 = $0.6255 — DERIVED, NOT MEASURED.** The rate is
owner-stated for c7a.4xlarge; this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). The estimate-vs-actual calibration row for this build is
**owed at grading, not now** — grading is where the process completes, and Sanaa has put
that later.

---

## 9. WHAT THIS DOCUMENT DOES NOT DO

- It **does not grade** M1, L, L2, S1 or Y1, and records no verdict for any of them.
- It **does not report a blended layer figure**, in any form, anywhere.
- It **does not quote the request table** at `log.snappyHexMesh:3257`.
- It **does not claim any y⁺**; §5 is arithmetic, labelled predicted, from a build in which
  no solver ran.
- It **does not touch** the `TRIAGE_STOP` tree or its `NOT A RESULT` label.
- It **contains no submission and no external communication. Nothing leaves the box.**

---

*Written by a cfd `lab-lane`, 2026-09-13, at cfd-supervisor's direction, discharging
Sanaa's ruling that R5 is stored and set aside for later grading. Every measured number
above cites the artifact it came from and every artifact cited is still on disk.*
