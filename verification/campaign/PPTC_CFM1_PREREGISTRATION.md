# PPTC VP1304 — RUNG CFM-1 — PRE-REGISTRATION

**FROZEN BY THIS COMMIT.** Gates, thresholds, bands, cap, labels and refusal limbs below are
closed as of this commit. Nothing in this file may be changed afterwards except as a dated
addendum at the foot, which cannot alter a gate, a threshold, a cap or a label.

**NO COMPUTE HAS BEEN RUN FOR THIS RUNG.** The run directory this document names,
`/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh`, **does not exist** — checked in
the same working session as this freeze, `ls` returned "No such file or directory". That
absence is the freeze check, and it is `cfd-supervisor`'s to make personally, not the lane's.

**Drafted by:** a `lab-lane` under `cfd-supervisor`, 2026-09-13.
**Nothing builds until the supervisor has committed this document and said so.**

**Predecessor:** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md`, frozen `748d26915`. PRISM-A2 is
**IN FLIGHT** at this freeze — its run directory
`/home/ubuntu/certonomous-runs/PPTC_VP1304/PRISM_A2_absthick` exists and is live. CFM-1 is a
**successor with its own registered cap**, not a new budget for PRISM-A2, and **it must not
start before PRISM-A2 reports**: the two would contend for the same 16 ranks and CFM-1's cost
row would then be uninterpretable.

---

## 1. WHY THIS RUNG EXISTS

`snappyHexMesh` has failed to extrude layers on this propeller six times. The mechanism is
measured and is not re-argued here: `relativeSizes true` scales the layer specification by
`hexRef8::getLevel0EdgeLength()`, which returns the **global minimum** level-0 edge, and on
the 360° background that is the 2 mm axis rod's azimuthal chord — a factor **95.537×**,
corroborated three ways (PRISM-A2 §1).

**Layers were never the only problem, and this document is written so that a success on
layers cannot be mistaken for a runnable case.** On the same mesh, before any layer was
attempted:

| quantity | value | artifact |
|---|---|---|
| faces extruded | **0 of 724,711 (0%)**, removed at 0 | `…/F360_coarse/log.snappyHexMesh:3314` |
| illegal faces at finish | **91,876** | `…/F360_coarse/log.snappyHexMesh:3338` |
| negative-volume cells | **316**, minimum −5.7249909e-10 | `…/F360_coarse/log.checkMesh:113` |
| SPD gate | **GATE FAIL**, witness cell **1,858,792**, `A_PP` = **−3.422338033e+04** | `verification/runs/PPTC_VP1304_runs/HUB_ROOT_MESH_RUNG_RESULTS.md:80-81` |
| mesh size | cells 19,700,035 / faces 59,833,297 / points 20,507,704 | `…/F360_coarse/log.checkMesh:39-42` |

`…` is `/home/ubuntu/certonomous-runs/PPTC_VP1304` throughout this document.

**Every number above is `F360_coarse`'s and no other mesh's.** The sibling
`F360_coarse_shaft4` reads **0 of 780,220** faces, and the two have been confused once in this
act already. No number in this document is carried across meshes.

## 2. THE RUNG: A DIFFERENT MESHER, THE SAME ADMITTED CAD, THE SAME REGISTERED SIZES

Run **cfMesh `cartesianMesh`** on the same admitted geometry at the same registered per-patch
cell sizes and the same registered §6.3 layer specification. `cartesianMesh` is installed
natively on this box (`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/`,
sha256 `2290d5339163c1b7a66a2d97d2d42b3c466e69d9c548977b5f1582fea42ed3b4`). It costs nothing
to obtain and it changes one thing.

### 2.1 The two alternatives that were NOT taken, recorded so the successor sees them

- **(b) A 72° single passage.** Declined: it changes the **domain** as well as the mesher, so
  a difference in the outcome measures neither. Held as the fallback if (a) refuses, and that
  is the supervisor's call, not this lane's.
- **(c) The snap-phase illegal-face root cause.** Declined **for tonight only**: it is a
  **geometry-admission** change and therefore the slowest to register honestly. It is the
  right rung eventually — refusal limb **R1** below routes the act to it explicitly.

### 2.2 The one place the single-variable claim is qualified, and it is qualified rather than asserted

The `axisRod` — a 2 mm slip cylinder on the axis — is **dropped**. It is a `blockMesh`
topology artifact, not a modelled body: pre-registration §6.1 registers a plain cylinder with
no rod, and `cases/PPTC_VP1304/mesh/make_blockmesh_360.py:14-17` records the rod as replacing
a *collapsed axis* so that the background would be 100% hexahedral. cfMesh's octree has no
axis singularity to collapse. **Dropping it moves the mesh toward the registered §6.1 domain,
not away from it** — but it is a change, and it is named here rather than hidden inside
"same domain".

## 3. THE PUBLISHED SOURCE — SANAA'S §G IS SATISFIED BEFORE ANY REGISTRATION, NOT AFTER

Full record: `cases/PPTC_VP1304/PUBLISHED_CFMESH_SETUP_INGEST.md`.

**No cfMesh recipe was in the knowledge base.** Both places named in the standing brief were
checked first: `/home/ubuntu/upstream/published-openfoam-setups/` held three trees, all
snappyHexMesh, and `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` lists the same three and no
fourth. One was ingested for this rung.

| field | value |
|---|---|
| source | cfMesh's own tutorial tree, OpenFOAM Community integration repository |
| URL | `https://develop.openfoam.com/Community/integration-cfmesh.git` |
| commit the source declares | `3ff8555514827646c34cacfe5f0f691e49cdbc96`, 2024-12-18, "COMP: scatter v.s. broadcast" |
| local tree | `/home/ubuntu/upstream/published-openfoam-setups/integration-cfmesh` |
| manifest | `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.integration-cfmesh.txt`, 676 files |
| **base dictionary** | `tutorials/cartesianMesh/ship5415Octree/system/meshDict` |
| **its sha256** | **`d09a3c61163025b80b294a8cd9826fec3b19bc1e566357713e62271b166277f2`** |
| its `Allrun` | `b55a10ffbe0ca3f860e9ac4f10738e469806ce8a0e9c0e2a069cf0f14c0f61c2` |

`ship5415Octree` is the only external naval-hydrodynamics case in the nine `cartesianMesh`
tutorials: a hull plus a domain box in one closed surface, `surfaceFeatureEdges` into a
`.ftr`, per-body `surfaceMeshRefinement`, and a full boundary-layer block with `optimiseLayer`
and `optimisationParameters`.

**Both files are COPIED, NOT RE-TYPED**, and the copies re-hash to the values above:
`cases/PPTC_VP1304/mesh/cfmesh/meshDict.ship5415Octree.PUBLISHED` and
`…/Allrun.ship5415Octree.PUBLISHED`.

The case dictionary is `cases/PPTC_VP1304/mesh/cfmesh/meshDict`, sha256
**`a87860956ecfd3ee140b0202e8c2afe68372a426f3b4d4503631d2ed25a1dae8`**, and it parses under
`foamDictionary` (v2606, exit 0). **Every departure from the published file is numbered D1–D9
inside it with a one-line reason**, and every keyword not in the base is cited to the shipped
cfMesh tutorial it comes from (`maxFirstLayerThickness` and `renameBoundary` from
`multipleOrifices`, sha256 `0bc02a568a74ff2b83e4c2d6aa647fac69a5b45e0b7be3fddb85cfb91671045d`).
**D7 — `optimiseLayer` and every `optimisationParameters` value — is ZERO deviation.**
**D9 records two things DECLINED rather than guessed**: no `meshQualitySettings` (there is no
published mapping from cfMesh's non-orthogonality vocabulary to MESH_STANDARD §3.2's boundary
skewness, so none is invented), and **no translation of the registered volume-refinement
regions** (`bladeRegion`, `tipVortex`, the 1.3D MRF zone) — **with the consequence registered
here: this mesh does not carry the registered volume refinement and NO `KT` or `KQ` may EVER
be graded on it.**

## 4. HOW LAYER ACHIEVEMENT WILL BE READ — STATED IN ADVANCE, BECAUSE cfMesh PRINTS NO TABLE

Read out of the published source: every per-face layer report in
`meshLibrary/utilities/boundaryLayers/refineBoundaryLayers/refineBoundaryLayersFunctions.C`
sits inside `# ifdef DEBUGLayer` (`:302-304`, `:333-337`), and the per-face count
`nLayersAtBndFace_` (`:308-340`) reaches no artifact. **There is no `Extruding N out of M`
line to read.** Achievement is obtainable **only by post-processing the produced mesh**, and
that post-processing is registered here as the instrument.

**Instrument:** `cases/PPTC_VP1304/mesh/read_cfmesh_layers.py`, sha256
**`c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8`**, committed with this
document. It reads `constant/polyMesh/{points,faces,owner,neighbour,boundary}` only. Its
OpenFOAM face geometry and its content-sniffing readers and points/faces REFUSAL are **copied
from** `verification/runs/PPTC_VP1304_runs/spd_gate.py`, blob `c68c4ddb`, rather than
rewritten.

**A topological count alone would be a false instrument, and this is why the definition is
metric.** A cartesian mesh with no layers is *already* hexes stacked off the wall, so "how
deep is the hex column above this face" returns a large number on a layerless mesh and proves
nothing. The registered definition:

> A boundary face `f` on wall patch `P` is **LAYERED TO DEPTH m** iff
> `t_1 <= FIRST_FRAC * s_P` **and** `RLO <= t_{j+1}/t_j <= RHI` for `j = 1 … m-1`,
> where `t_k` is the wall-normal extent of the k-th cell in the opposite-face column above
> `f`, and `s_P` is the **registered** local surface cell size for patch `P`.

**Frozen constants, in the script and here:** `FIRST_FRAC = 0.5`, `RLO = 1.10`, `RHI = 1.35`,
`MAXWALK = 16`. Separation at the registered sizes: a layerless cartesian cell gives
`t_1/s_P = 1.000` and ratios `1.000`; cfMesh at 6 layers / ratio 1.2 is predicted at
`t_1/s_P = 0.1007` and ratios `1.200`. `FIRST_FRAC = 0.5` sits between them by 2× on one side
and 5× on the other. A 2:1 octree transition gives ratio 2.0, outside `[1.10, 1.35]`.

**Fields read, by name:** `C_full(depth>=6)` and `C_2(depth>=2)` per patch, and `median t1`
per patch, printed by `measure()`.

**Registered sizes passed to it**, from `…/F360_coarse/log.makeSnappy:3-6`:
`blades=6.25e-4, hub=1.25e-3, cap=1.25e-3, shaft=2.5e-3` m.

**THE INSTRUMENT IS UNEXERCISED AT THIS FREEZE, AND THAT IS DISCLOSED RATHER THAN GLOSSED.**
This lane was instructed to launch nothing, and it launched nothing — including the reader's
own arming. Its arming is a **blocking precondition** (§8) and it is registered here at **< 1
core-min**. If the arming fails, the rung is **BLOCKED** and any repair falls under
`VERIFICATION_CHARTER` §2d.1 and must satisfy all four of its conditions.

## 5. THE ARITHMETIC THAT IS KNOWN BEFORE THE RUN — AND ONE PREDICTED `GATE FAIL`

From `refineBoundaryLayersFunctions.C:684-714`, quoted in the ingest record §3.2: cfMesh
computes the first sub-layer as `magv / ((1-r^n)/(1-r))`, where `magv` is the **hair-edge
length** — the wall-normal extent of the **single** extruded near-wall cell — and then applies
`maxFirstLayerThickness` as `min(...)`, a **cap that can only thin**. So in cfMesh the total
stack is **one local cell by construction**, `magv <= s_P`.

With `n = 6`, `r = 1.2`: `Σ = (1.2^6 − 1)/0.2 = 9.929920`, `1.2^5 = 2.48832`.

| patch | `s_P` (m) | registered `t_1` (m) | registered stack (m) | stack / `s_P` | **cfMesh `t_1` (m)** | ratio to registered |
|---|---|---|---|---|---|---|
| blades | 6.25e-4 | 1.255867e-4 | 1.247068e-3 | **1.99531** | **≤ 6.29461e-5** | **≤ 0.50122×** |
| hub | 1.25e-3 | 2.511734e-4 | 2.494136e-3 | 1.99531 | ≤ 1.258922e-4 | ≤ 0.50122× |
| cap | 1.25e-3 | 2.511734e-4 | 2.494136e-3 | 1.99531 | ≤ 1.258922e-4 | ≤ 0.50122× |
| shaft | 2.5e-3 | 5.023468e-4 | 4.988272e-3 | 1.99531 | ≤ 2.517844e-4 | ≤ 0.50122× |

Registered `t_1` is `finalLayerThickness / 1.2^5` at the PRISM-A2 §4 absolute finals. An
inequality, not an equality, because the octree cuts cells at the surface and can only make
`magv` **smaller** than `s_P`.

**This independently reproduces a finding a sister lane already made and it is credited, not
claimed as new.** `cases/PPTC_VP1304/PRISM_A2_YPLUS_AND_L2_COMPUTED_FROM_OUR_SIDE.md:131`
measures the registered stack at **1.995 local cells** against `MESH_STANDARD.md` §16.3 rule
**L2**'s one-local-cell limit, and its §5 table at `nSurfaceLayers 6` (`:161`) reads *"largest t1 under
L2 = 0.0629 mm, y+ at that t1 = 11.4"*. **0.0629 mm is 6.29e-5 m — the same number as the
blades row above.** cfMesh does not merely satisfy L2; **L2 is cfMesh's structural
constraint**, which is the mechanistic reason to expect it to extrude where snappy did not.

**The price is registered here, in advance, as a `GATE FAIL`.** The same record's §1 (`:58-59`) states
that at the registered `t_1 = 0.1256 mm` the highest predicted blade `y+` **anywhere** is
**28.8**, already below the §6.3 window of 30–60. At `0.50122×` that becomes **≤ 14.4
anywhere**, and **11.4** at `J = 1.2021, r/R 0.70`. **cfMesh at the registered
`nSurfaceLayers 6` and the registered blade cell cannot reach the §6.3 `y+` window, and no
cfMesh setting escapes it.** Gate **G3** below is therefore registered as a predicted
`GATE FAIL` before the run, so that it cannot be presented as a surprise afterwards and cannot
be quietly softened.

## 6. THE GATES

Vocabulary is `VERIFICATION_CHARTER` §2's and nothing else: **PASS / GATE REACHED / GATE FAIL
/ NOT A RESULT / BLOCKED / PENDING.**

### G0 — SURFACE ADMISSIBILITY (blocking precondition, not a rung gate)

| id | quantity | instrument | threshold | label |
|---|---|---|---|---|
| G0a | the combined surface `PPTC-body-and-domain.stl` is watertight | `surfaceCheck` (OpenFOAM v2606) | zero open edges; "Surface is closed" | PASS else **BLOCKED** |
| G0b | the body triangles inside the combined surface are the **admitted** ones | sha256 of the sorted per-patch triangle vertex stream vs the same computed on `…/F360_coarse/constant/triSurface/<patch>.stl` | exact equality, all five patches | PASS else **BLOCKED** |

G0b exists because if the body were re-tessellated, this is no longer the **same admitted
CAD** and the single-variable claim in §2 is void.

### G1 — LAYER COVERAGE ON `blades`. THE GATE THAT MATTERS MOST.

Instrument `read_cfmesh_layers.py` (§4), field `C_full(depth>=6)` for patch `blades`.

| band | label |
|---|---|
| `C_full >= 90.0%` | **GATE REACHED** |
| `25.0% <= C_full < 90.0%` | **GATE FAIL** |
| `C_full < 25.0%` | **GATE FAIL**, and refusal limb **R1** fires |

**Registered prediction: `>= 90%`.** The bar is high deliberately, and the reason is
mechanistic: cfMesh's layers are a topological **subdivision** of an already-extruded
near-wall cell (`refineBoundaryLayersFunctions.C:684-697`), not a geometric extrusion that can
be abandoned face by face as snappy's is. **Partial coverage is not the expected mode here,
and if cfMesh returns it that is itself the finding and is reported as one, not celebrated as
a partial win.**

### G2 — LAYER COVERAGE ON `hub`, `cap`, `shaft`

Same instrument, same field, per patch. `C_full >= 90.0%` → **GATE REACHED** for that patch;
else **GATE FAIL** for that patch. Labelled per patch, never aggregated. Registered separately
from G1 because the snappy failure was total on all four: a mesher that carries the hub but
not the blades is a different finding from one that carries none.

### G3 — FIRST-LAYER THICKNESS. **PREDICTED `GATE FAIL`, REGISTERED AS SUCH BEFORE THE RUN.**

Instrument `read_cfmesh_layers.py`, field `median t1` for patch `blades`.

| id | criterion | label |
|---|---|---|
| G3 | `median t1 ∈ [1.13028e-4, 1.38145e-4]` m, i.e. the registered `1.255867e-4` ± 10% | PASS else **GATE FAIL** |
| **P-CFM** | `median t1 ∈ [5.66515e-5, 6.29461e-5]` m — the §5 prediction, upper-bounded because the octree can only thin `magv` | PASS else **GATE FAIL** |

**G3 is predicted `GATE FAIL` and P-CFM is predicted `PASS`.** They are two labels on one
number on purpose: G3 says whether the registered specification was met, P-CFM says whether
cfMesh's documented arithmetic is what actually governs. **P-CFM is the falsifiable one** — if
`median t1` lands outside its band, the §5 reading of the published source is wrong and §5
must be re-read before anything else in this rung is believed.

**`y+` is NOT gated and NOT measured here.** It requires a solve; there is no solve in this
rung. The `y+` consequence stated in §5 is a **geometric proxy** carried through the committed
predictor `cases/PPTC_VP1304/mesh/predict_yplus_from_first_layer.py`, and it is labelled a
proxy wherever it is reported.

### G4 — THE SPD GATE, CARRIED FORWARD UNCHANGED

Instrument `verification/runs/PPTC_VP1304_runs/spd_gate.py`, blob **`c68c4ddb`** — verified at
this freeze to be the blob at `HEAD` for that path, so the frozen file **is** the file that
will run.

> For every internal face, `w_f = |S_f|² / (S_f · d_f)` with `S_f` the owner's outward
> face-area vector and `d_f = C_N − C_P`; `A_PP = Σ_f w_f`.
> **GATE FAIL if any `w_f <= 0` or any `A_PP <= 0`. PASS if every `w_f > 0`.**
> **It must report the witness cell index and the value of `A_PP`, or it has not fired.**

Its own `--check-volumes` geometry control against `0/cellVolume` is **MANDATORY and
blocking**: the gate voids its own verdict, in either direction, if its geometry disagrees
with OpenFOAM's by more than 1e-6 relative or the negative-volume counts differ.

**No prediction is registered for G4, and the refusal to predict is deliberate.** The snappy
mesh fails it with witness cell 1,858,792, `A_PP` = −3.422338033e+04
(`verification/runs/PPTC_VP1304_runs/HUB_ROOT_MESH_RUNG_RESULTS.md:80-81`). cfMesh produces a
**different cell topology**, so that prior does not transfer to this mesh and carrying it
across would be exactly the error §1 warns about.

### G5 — MESH VALIDITY

`checkMesh -allGeometry -allTopology`. **Negative-volume cells == 0 → PASS, else GATE FAIL.**
Also reported, not gated: illegal-face count, max non-orthogonality, max skewness, cell count.
`F360_coarse`'s 316 negative-volume cells and 91,876 illegal faces are a **reference for the
reader, not a threshold, and not a number that travels to this mesh.**

## 7. WHAT THE WHOLE RUNG IS CALLED

| outcome | rung label |
|---|---|
| G0 PASS, controls pass, **G1 GATE REACHED** | **GATE REACHED** — a different mesher extrudes the registered layers on this geometry. G3's predicted `GATE FAIL` stands beside it and does **not** downgrade it. |
| G0 PASS, controls pass, **G1 GATE FAIL** at `>= 25%` | **GATE FAIL** — cfMesh extrudes partially; the reading is that the mesher was necessary but not sufficient, and what follows is the **supervisor's** call. |
| G0 PASS, controls pass, **G1 GATE FAIL** below 25% | **GATE FAIL**, and **R1**: the act moves to (c), the geometry-admission root cause. |
| **any control in §8 fails** | **BLOCKED.** No PASS and no GATE FAIL from this mesh is admitted. |
| G0 fails, or `cartesianMesh` refuses | **BLOCKED** (see R2). Not a GATE FAIL. |

## 8. THE CONTROLS, AND THE STOP RULE — **WRITTEN IN BOTH DIRECTIONS**

**This act has already been bitten here.** A stop rule written only as *"stop if the gate
PASSES on the known-bad mesh"* let a `GATE FAIL` returned from garbage straight through,
because a wrong instrument fails in both directions and only one of them was guarded. This one
is written both ways.

| id | control | what it does | **requirement** |
|---|---|---|---|
| **A** | **known-NO-layers**, real mesh | `read_cfmesh_layers.py --control-none …/F360_coarse --control-none-points …/F360_coarse/0/polyMesh/points` | **`blades C_full == 0.000%` AND `C_2 == 0.000%`.** That mesh's own log reads `Extruding 0 out of 724711 faces (0%)` (`…/F360_coarse/log.snappyHexMesh:3314`). A non-zero here means the reader calls a plain cartesian column a layer. |
| **B** | **known-YES-layers**, synthetic | `--selftest`: a column built with exactly 6 sub-cells at ratio 1.2 inside one local cell, and a layerless column of the same cell | **layered reads `C_full == 100.000%` AND layerless reads `0.000%`.** A reader never shown seeing a layer cannot report their absence. |
| **C** | **planted zero**, rule 3 | `--plant-dir`: **`PLANT = 1.234e-03` m** displacement along the inward normal at **5,000** `blades` faces, **written to disk as a `points` file and read back**, never perturbed in memory only | **`max |Δt1|` over planted faces `== PLANT` to 1e-9**, and contamination `<= 40 ×` the planted faces sampled |
| **D** | SPD geometry control | `spd_gate.py --check-volumes …/0/cellVolume` | max relative cell-volume difference `<= 1e-6` **and** identical negative-volume counts |

> **STOP RULE. The rung STOPS unless A, B, C and D each pass IN THEIR OWN DIRECTION. A failure
> in EITHER direction stops it: an instrument that cannot see a layer and an instrument that
> sees layers everywhere are both disqualifying. If any of A–D fails, the rung is `BLOCKED`,
> and NEITHER a `PASS` NOR a `GATE FAIL` from the cfMesh mesh is admitted — the failure is a
> statement about the reader, not about cfMesh, and nothing is said about cfMesh at all.**

The controls run **before** the cfMesh mesh is read, and the order is registered: B, then A,
then the mesh build, then C on the produced mesh, then G1–G3, then D, then G4, then G5.

**Optional strengthening, registered as optional and NOT required:** if PRISM-A2 returns a
mesh with real extruded layers, that mesh becomes a second real-mesh control B. It is not
available at this freeze — **no PPTC mesh on disk carries layers, and the count is stated
because it did not reconcile on the first pass.** `/home/ubuntu/certonomous-runs/PPTC_VP1304/`
holds **seven** `log.snappyHexMesh` files; only **two** contain an `Extruding` line at all —
`F360_coarse` (**0 of 724,711**) and `F360_coarse_shaft4` (**0 of 780,220**). The other five
(`L1_cm1`, `L1_prod7`, `L1_prod7s`, `L2_prod7s`, `PRISM_A2_absthick`) never reached the layer
phase, so they are silent rather than negative, and they are named here rather than counted in.

## 9. THE REFUSAL LIMBS — WHAT WOULD MAKE cfMesh THE WRONG INSTRUMENT RATHER THAN THE MESH WRONG

- **R1.** `G1 C_full < 25%` on `blades` **while A–D all pass and `checkMesh` reports the mesh
  otherwise valid** → cfMesh cannot carry layers on this geometry either. The instrument is
  not at fault and neither is the length scale: **the geometry is**, and the act's next rung
  is **(c)**, the snap-phase / geometry-admission root cause — **not a third mesher.**
- **R2.** `cartesianMesh` exits non-zero, or writes no `constant/polyMesh`, or writes a mesh
  whose cell count falls outside **[5e6, 8e7]** → **BLOCKED**, not GATE FAIL. cfMesh has not
  been given a well-posed problem; the fault lies in the combined surface (G0) or in the
  deviation set D1–D9, and it is reported as a defect in this registration.
- **R3.** `G1 GATE REACHED` **but** `G4 GATE FAIL` **and** `G5` negative-volume cells > 0 →
  cfMesh is a working **layer** instrument and the wrong mesher for a **runnable** case. The
  layer result stands as `GATE REACHED`; the operator question goes back to the supervisor.
  **This is the outcome §10 anticipates and it is not a contradiction.**
- **R4.** Any of A–D fails → **BLOCKED**, and **no statement about cfMesh is made at all.**

## 10. THE HONEST STATEMENT THIS RUNG IS REQUIRED TO CARRY

**A mesh with layers and a non-SPD pressure operator still has no converging solver.**

G1 can be `GATE REACHED` and this rung still not produce a runnable case. The SPD failure and
the negative-volume cells are **independent of layer coverage** and were diagnosed on the
**castellate/snap** mesh, **before any layer was attempted** — the witness cell 1,858,792 is a
property of that mesh's cell geometry, not of its prism stack. **Layers were never the only
problem**, and a `GATE REACHED` on G1 is a statement about **layer extrusion and nothing
else.**

Additionally, and independently: **§D9(b) forbids grading `KT`, `KQ` or any solved quantity on
this mesh at all**, because it does not carry the registered `bladeRegion`, `tipVortex` or MRF
volume refinement. This mesh is a **layer-extrusion experiment**, not a candidate solve mesh,
and no later reading may promote it into one.

## 11. COST — IN CORE-MINUTES, WITH THE CAP, AND DOLLARS DERIVED

| item | basis | estimate (core-min) |
|---|---|---|
| build the combined closed surface + `surfaceFeatureEdges` (G0) | Python + one OpenFOAM utility over ~651k body triangles, 1 thread | 15 |
| `surfaceCheck` + G0b hashing | 1 thread | 10 |
| reader arming, controls **B** and **A** | B is synthetic (<1 core-min); A walks 724,711 boundary faces of a 19.7M-cell mesh, 1 thread | 45 |
| **`cartesianMesh`, 16 OpenMP threads** | **NO measurement of cfMesh exists on this box.** The only anchor is a *different* algorithm on the *same* geometry at the *same* sizes: snappy's **12,538.33 s serial = 208.97 core-min** (`…/F360_coarse/log.snappyHexMesh:3339`). **That anchor bounds nothing about cfMesh and is not treated as if it did**; the figure below is 208.97 × 4 (margin, stated as margin) × ~1.1 for threading overhead. | 900 |
| `checkMesh -allGeometry -allTopology` (G5) | 8.950 core-min measured on the 19.8M-cell sibling (`docs/COST_CALIBRATION.md` row `C-20260913T222241.696370Z-8e1dd7ea`) | 15 |
| planted-zero control **C** | two reader passes + a points write, 1 thread | 60 |
| G1–G3 reading of the produced mesh | 1 thread | 40 |
| `spd_gate.py` + control **D** (G4) | **6.342 core-min measured**, same ledger row; peak RSS **46.9 GB** measured there | 20 |
| **CAP** | measured-basis anchor 208.97 core-min for the mesher stage, everything else measured or bounded; margin stated **as** margin | **1200 core-min** |

**Threads:** `cartesianMesh` is OpenMP (`meshSurfaceEngineCalculateBoundaryNodesAndFaces.C:141`
uses `omp_get_num_procs()`). Core-minutes for that stage are `wall_s × OMP_NUM_THREADS / 60`,
and the thread count **actually used** is read from the run's own record, never assumed. If
the shipped binary turns out to be serial, the stage is `wall_s × 1 / 60` and the cost row
says so.

**Ranks:** 16, of the 16 allocated to PPTC. **CFM-1 must not overlap PRISM-A2** (§ preamble).

**Dollars, DERIVED NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5), so this is reported-by-owner arithmetic: 1200 core-min =
20.0 core-h at c7a.4xlarge **$0.0513/core-h** = **$1.026 derived**.

**The cap is RECORDED, NOT A STOP.** Sanaa's NO-CAP ruling of 2026-09-12 (directive #17) means
no run of any team is stopped by a time or budget cap. It does not mean a cap goes unwritten —
**a cost nobody wrote down is what disqualifies a proposal** (rule 12).

**Memory is declared, because the last rung's calibration row found that omission:** the SPD
gate measured **46.9 GB peak RSS** on 19,829,120 cells. A cfMesh mesh of comparable size will
need the same order from `spd_gate.py` and from the reader, and **a run that is OOM-killed is
`BLOCKED`, not `GATE FAIL`.**

**At completion, a row is appended to `docs/COST_CALIBRATION.md`** per rule 12: estimate vs
actual in core-minutes, the ratio, the attribution, and waste named separately and never
absorbed into the ratio. Its id is **machine-minted, never hand-typed** — one hand-typed id
blocked every team's ledger appends at exit 7 in this act.

## 12. A SUCCESSOR THAT IS COMPUTED BUT **NOT AUTHORISED**, AND THE DECISION IS THE SUPERVISOR'S

`PRISM_A2_YPLUS_AND_L2_COMPUTED_FROM_OUR_SIDE.md:161` and its §5.1 proposes `nSurfaceLayers 6 → 2` with
`t1 = 0.2841 mm`, giving `y+ ≈ 51.5` at `r/R 0.70` and `S = 1.00` local cells — **both
constraints met, `y+` mid-window.**

**cfMesh would deliver that value exactly and for free**: at `n = 2`, `r = 1.2`, the same
arithmetic gives `t_1 = s_P / 2.2 = 6.25e-4 / 2.2 = 2.84091e-4 m = 0.2841 mm` — the sister
lane's number to four figures — **because `S = 1.00` is cfMesh's structural constraint, not a
setting.** So the cfMesh route reaches the `y+` window at `nLayers 2` and cannot reach it at
`nLayers 6`.

**`nSurfaceLayers` is a registered §6.3 parameter and this lane does not change it.** CFM-1
runs at the registered **6**. The `nLayers 2` variant is recorded here with its arithmetic so
the supervisor can rule on §5.1 with the number already in hand, and it is **NOT AUTHORISED by
this document.** Adopting it quietly would be the registration fitting itself to a wanted
answer, which is the one thing the freeze exists to prevent.

## 13. WHAT THIS RUNG MAY NOT DO

No solver. No queue entry. No `KT`, `KQ` or any solved quantity, ever, from this mesh (§10,
§D9b). No edit to any frozen pre-registration. **No write into
`…/F360_coarse/` or `…/PRISM_A2_absthick/`**, which other lanes hold — the controls read
`F360_coarse` and write nothing to it, and the planted `points` file goes to the rung's own
run directory. No start before PRISM-A2 reports and before the supervisor's committed word.
And nothing is sent, filed, uploaded, registered, posted or commented anywhere outside this
box (rule 7).

## 14. THE FREEZE CHECK, WHICH IS THE SUPERVISOR'S AND MAY NOT BE DELEGATED

1. `/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh` **does not exist.**
2. `cases/PPTC_VP1304/mesh/cfmesh/meshDict.ship5415Octree.PUBLISHED` re-hashes to
   `d09a3c61163025b80b294a8cd9826fec3b19bc1e566357713e62271b166277f2`.
3. `cases/PPTC_VP1304/mesh/cfmesh/meshDict` re-hashes to
   `a87860956ecfd3ee140b0202e8c2afe68372a426f3b4d4503631d2ed25a1dae8`.
4. `cases/PPTC_VP1304/mesh/read_cfmesh_layers.py` re-hashes to
   `c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8`.
5. `git rev-parse HEAD:verification/runs/PPTC_VP1304_runs/spd_gate.py` == `c68c4ddb…`.
6. The reader is **unexercised** (§4) and its arming is a blocking precondition.
