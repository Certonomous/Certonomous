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

---

# AMENDMENTS — PRE-COMPUTE, UNDER `VERIFICATION_CHARTER` §2b

**DOCUMENT VERSION: v1.1.** The frozen original above is v1.0, commit
`937e0893c9d99b7930d6658b7f34ccf1082ee550`, verified by this lane to be in `main`'s ancestry.
**Lines whose number changed above this section: 0.** Nothing above line 441 was edited,
re-ordered or re-numbered; the two amendments below are appended at the foot, and every
supersession below **strikes** the original text and restates it rather than rewriting it in
place. Other records cite this file by line and those citations still resolve.

**Author:** a `lab-lane` under `cfd-supervisor`, 2026-09-13. **Both amendments are made on
`cfd-supervisor`'s instruction, before any compute for this rung exists.** No agent's message
is Sanaa's consent (CLAUDE.md rule 9) and neither amendment claims her authority: both change a
**rung-local** parameter of CFM-1 and **neither touches the parent open-water pre-registration
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` §6.3**, which continues to govern
the solve family.

## A0 — THE §2b CONDITION, AND HOW IT WAS CHECKED

`VERIFICATION_CHARTER` §2b permits amendment of a frozen pre-registration **only before first
compute**, and requires the condition to be stated **with the check**. The check is the
non-existence of the run directory this document names:

> `/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh` **DOES NOT EXIST.**
> `ls -la` on that path returned `No such file or directory`, `rc=2`, 2026-09-13 23:18 UTC,
> in the same working session as these amendments.

Corroborated: `find` across the repository and `/home/ubuntu/certonomous-runs` for any path
matching `*CFM1*` or `*CFM-1*` returned exactly one hit, this document itself. **No
`cartesianMesh` has been launched, no `constant/polyMesh` has been written for this rung, and
no gate in §6 has a value.** The gates below are therefore still open to amendment, and the
freeze's evidentiary content — that a gate could not have been chosen to fit an answer — is
intact, because **there is no answer yet.**

If any CFM-1 mesh output had existed, both rulings below would have been illegal as amendments
and would have had to be re-thought as dated addenda unable to alter a gate, a threshold, a cap
or a label.

**Sibling state at the time of this check, disclosed because the preamble makes it a
precondition:** `PRISM_A2_absthick` is **still in flight** — its `log.snappyHexMesh` was
modified within the ten minutes before this check. The preamble's rule that **CFM-1 must not
start before PRISM-A2 reports** is untouched by these amendments and still binds.

---

## AMENDMENT 1 — 2026-09-13 — THE REGISTERED VOLUME REFINEMENT IS TRANSLATED INTO cfMesh'S OWN VOCABULARY, AND §D9(b)'s GRADING PROHIBITION IS RE-STATED

### A1.1 Why — a mesh that can never carry the coefficient is a diagnostic, not a rung

§3 and the case dictionary's **D9(b)** declined to translate the registered volume-refinement
regions, and registered the consequence in this document's own words:

> ~~"this mesh does not carry the registered volume refinement and NO `KT` or `KQ` may EVER be
> graded on it"~~ (§3, lines 116-118; repeated at §10, lines 358-361) — **STRUCK as to its
> volume-refinement limb only**, by this amendment, and **superseded by A1.5 below.**

The reason the original clause is struck rather than kept: **volume refinement is the one
deviation that cannot be repaired after the mesh exists.** A cell that was never refined cannot
be refined by post-processing, whereas the MRF **cellZone** (A1.4) can be created after meshing
by a standard `topoSet` step. Declining the irrecoverable deviation to save a rung's worth of
deviations was the wrong trade, and it is corrected **before** compute, where correcting it is
free and cannot be mistaken for fitting a result.

### A1.2 The published forms, copied not invented

cfMesh's refinement vocabulary was read out of the same ingested tree as §3's base dictionary,
`/home/ubuntu/upstream/published-openfoam-setups/integration-cfmesh`, commit
`3ff8555514827646c34cacfe5f0f691e49cdbc96`. **Exactly two shipped tutorials use
`objectRefinements`,** and both were read in full:

| tutorial dict read | sha256 | **FORM USED in D10** | forms read and NOT used |
|---|---|---|---|
| `tutorials/cartesianMesh/bunnyOctree/system/meshDict` (a **`cartesianMesh`** tutorial — the same mesher this rung runs) | `da05baa6e65267a73680ab3325336a989a9f6fe72fc07e271bc72abb1497c487` | the `objectRefinements { <name> { type cone; p0 …; radius0 …; p1 …; radius1 …; } }` block structure and every keyword spelling in D10 (`:26-69`) | `type box` with `centre`/`lengthX`/`lengthY`/`lengthZ` (`:46-54`); `type sphere` with `centre`/`radius` (`:55-61`); `type line` (`:62-68`) — read to confirm the vocabulary, **none of them used**, because both registered regions are cylinders |
| `tutorials/pMesh/bunnyPoly/system/meshDict` | `3c0b3ec5dce746a6f79acf8009a4559498f86305449520fac83dd7cc0a7e3ee0` | **nothing taken from here** — it is the **independent second witness** that the `cone` block has the spelling above (`:21-41`) | `refinementThickness` inside an object entry (`:50`) — **and that line sits inside that tutorial's commented-out `/* … */` block (`:43-70`), so it is not a live published example**; the authority for the keyword is the class, `objectRefinement.C:90`. It is deliberately **not** set in D10 either way — see inexactness item 3 |

A verbatim copy of the first is kept beside the case dictionary as
`cases/PPTC_VP1304/mesh/cfmesh/meshDict.bunnyOctree.PUBLISHED`, **copied not re-typed**, and it
re-hashes to the value above after the copy.

**A cfMesh `cone` with `radius0 == radius1` IS a cylinder, and that is confirmed against a
shipped example rather than assumed.** `bunnyOctree`'s `ear1` and `ear2` (lines 28-45) are both
`type cone` with `radius0 200; radius1 200;` — the shipped tutorial itself uses the equal-radii
cone as its cylinder. The class confirms it: `coneRefinement::intersectsObject` projects the
test point onto the axis `v = p1 - p0` and compares against a radius interpolated between `r0_`
and `r1_` (`meshLibrary/utilities/octrees/meshOctree/refinementControls/objectRefinement/coneRefinement.C:106-118`),
which for `r0_ == r1_` is a right circular cylinder of finite axial extent. **cfMesh ships no
`cylinder` type**; the equal-radii cone is the published image of one.

### A1.3 THE MAPPING, ONE LINE PER OBJECT — AND WHERE IT IS NOT EXACT

Registered source of the geometry: `cases/PPTC_VP1304/mesh/make_snappy.py:125-132` (the
`searchableCylinder` definitions) and `:151-153` (the `refinementRegions` levels).
Both regions are registered at `levels ((1e15 {LEVELS["blades"][0]-1}))` = **level 4**, against
the registered 20.00 mm background, i.e. an achieved cell of `0.02 / 2^4` = **1.25 mm**.

| registered object | registered geometric extent | cfMesh object type | cfMesh refinement spec | exact? |
|---|---|---|---|---|
| `bladeRegion` | `searchableCylinder`, axis `(-0.100 0 0)` → `(+0.060 0 0)` m, radius `1.06 R` = **0.132500 m**, snappy `levels ((1e15 4))` → 1.25 mm | **`cone`**, `p0 (-0.100 0 0)`, `radius0 0.1325`, `p1 (0.060 0 0)`, `radius1 0.1325` | **`additionalRefinementLevels 4`** | **geometry EXACT; level EXACT** |
| `tipVortex` | `searchableCylinder`, axis `(-0.250 0 0)` → `(+0.030 0 0)` m, radius `1.04 R` = **0.130000 m**, snappy `levels ((1e15 4))` → 1.25 mm | **`cone`**, `p0 (-0.250 0 0)`, `radius0 0.130`, `p1 (0.030 0 0)`, `radius1 0.130` | **`additionalRefinementLevels 4`** | **geometry EXACT; level EXACT** |
| `MRFzone` | `searchableCylinder`, 1.3 D diameter, axial `±0.5 D` — a **cellZone carrying the rotating-frame source**, NOT a `refinementRegions` entry (`make_snappy.py:133-136`, and the generator's own comment at `:154`) | **NOT TRANSLATED** — `objectRefinements` refines; it does not create a cellZone | — | **NOT TRANSLATED, see A1.4** |

**Note on the naming, because the brief that ordered this amendment called `bladeRegion` a
"blade box":** it is **not** a box. `make_snappy.py:125-128` registers it as a
`searchableCylinder`, and `cases/PPTC_VP1304/HUB_ROOT_MESH_RUNG_PREREGISTRATION.md:57-58`
records it the same way — "`bladeRegion`, radius 0.1325 m, x ∈ [−0.100, +0.060]". Both
registered regions are cylinders, both map to `cone`, and the `box` form was read from the
tutorial and **not used**. Recording this rather than quietly meshing a box.

**WHERE THE MAPPING IS NOT EXACT, STATED RATHER THAN ROUNDED INTO AGREEMENT:**

1. **`additionalRefinementLevels` is used, NOT `cellSize`, and the reason is a measured trap in
   the published source.** `objectRefinement::calculateAdditionalRefLevels`
   (`…/objectRefinement/objectRefinement.C:108-130`) converts a requested `cellSize` into an
   integer level by halving from `maxCellSize` **while `cellSize_ <= s*(1+SMALL)`** — the loop
   takes **one halving too many** when the ratio is an exact power of two. Traced numerically
   against this case's own numbers, `maxCellSize 0.02`: a request of `cellSize 1.25e-3`
   (the registered level-4 size) yields **`additionalRefinementLevels 5`**, an achieved cell of
   **6.25e-4 m — a factor 2 FINER than registered**, and roughly 8× the cells in both regions.
   `additionalRefinementLevels 4` is cfMesh's own integer vocabulary, is the same
   power-of-two counting snappy's `levels` use, is applied against the same 20.00 mm
   `maxCellSize` (`meshOctreeCreatorAdjustOctreeToSurface.C:265-274` reads `maxCellSize` as the
   base), and therefore reproduces the registered 1.25 mm **exactly**. **The deviation is
   registered as zero, and the route that would have made it a factor of 2 is named so that a
   successor does not take it.**
2. **The region boundary is resolved to one octree cube, not to the analytic surface.** snappy
   tests a cell centre against the `searchableCylinder`; cfMesh tests an octree cube against
   the `cone` (`refineBoxesContainedInObjects`, `…AdjustOctreeToSurface.C:195-247`). Both are
   cell-resolution decisions, and the sets can differ by **at most one cell layer at the region
   boundary**. No number in this document depends on the exact membership of that layer.
3. **`refinementThickness` is NOT set on either object** (default `0.0`,
   `objectRefinement.C:90`), so refinement applies **inside** the object only. This is the
   image of snappy's `mode inside; levels ((1e15 4))`, whose `1e15` distance means "everywhere
   inside, no distance falloff".
4. **No shipped tutorial combines `surfaceMeshRefinement` with `objectRefinements`** —
   `ship5415Octree` has the first and no second; `bunnyOctree` and `bunnyPoly` have the second
   and no first. **The combination is therefore not exhibited by a published example, and that
   is disclosed rather than glossed.** It is nevertheless the source's own design: both are
   read by separate, independently `found()`-guarded functions and both are called in sequence
   from `meshOctreeCreator::createOctreeBoxes()` —
   `refineBoxesIntersectingSurfaces()` at `meshOctreeCreatorCreateOctreeBoxes.C:499` and
   `refineBoxesContainedInObjects()` at `:525`. Neither excludes the other.
   **Refusal limb R2 already covers the outcome if this reading is wrong**: `cartesianMesh`
   exiting non-zero, or a cell count outside `[5e6, 8e7]`, is **BLOCKED**, not `GATE FAIL`.

### A1.4 WHAT THIS AMENDMENT DOES **NOT** FIX, AND THE PROHIBITION THAT SURVIVES

The **MRF cellZone is still not created by this dictionary.** `objectRefinements` refines
octree cubes; it does not write a `cellZone`. The rotating-frame source has no zone to act on,
so **this mesh as produced still cannot run the open-water solve.**

That gap is **recoverable after meshing** by a standard `topoSet` `cylinderToCell` +
`cellSet → cellZone` step, which is exactly why it is a different class of defect from the
volume refinement. **No such step is registered here and none is authorised by this amendment.**

### A1.5 THE RE-STATED GRADING CLAUSE — SUPERSEDING §3 (lines 116-118) AND §10 (lines 358-361)

> **No `KT`, `KQ` or any solved quantity may be graded on this mesh.** The prohibition stands.
> Its **volume-refinement ground is removed** by this amendment — the mesh now carries the
> registered `bladeRegion` and `tipVortex` refinement at the registered level 4 — and it is
> **re-grounded, unchanged in effect, on three independent limbs that this amendment does not
> touch**: (i) **no MRF cellZone exists** (A1.4); (ii) **§10's first ground stands** — the SPD
> failure (G4) and the negative-volume cells (G5) are independent of layer coverage and are
> properties of cell geometry, and **a mesh with layers and a non-SPD pressure operator still
> has no converging solver**; (iii) **this rung registers no solver, no queue entry and no
> boundary conditions** (§13), so no solved quantity can exist to grade.
>
> **The prohibition may be lifted only by a later registration that addresses (i)-(iii)
> explicitly. No reading of this amendment lifts it, and this lane does not lift it.**

### A1.6 THE CASE DICTIONARY CHANGES, AND THE FREEZE-CHECK HASH THAT THIS INVALIDATES

`cases/PPTC_VP1304/mesh/cfmesh/meshDict` gains a new numbered deviation **D10**, the
`objectRefinements` block of A1.3. Its header's "D1..D9" becomes "D1..D10", and D9(b) is struck
in the dictionary with a pointer to this amendment.

> **§14 freeze-check item 3** — ~~"`cases/PPTC_VP1304/mesh/cfmesh/meshDict` re-hashes to
> `a87860956ecfd3ee140b0202e8c2afe68372a426f3b4d4503631d2ed25a1dae8`"~~ — **STRUCK.** That
> value was the v1.0 dictionary and was verified correct at this amendment before the edit.
> **Superseded**: the file re-hashes to the value recorded in **A3.1** below, which is computed
> after **both** amendments' edits and is the only hash a successor should check.

Nothing else in §14 changes. Items 1, 2, 4 and 5 were each re-verified by this lane at this
amendment and each still holds — in particular item 4, `read_cfmesh_layers.py` at
`c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8`, **which is unchanged
because neither amendment edits the reader** (A2.6).

---

## AMENDMENT 2 — 2026-09-13 — `nSurfaceLayers` IS RULED TO **2** FOR THIS RUNG, BEFORE ANY GATE HAS A VALUE

### A2.1 The ruling, and the reason IT IS REGISTERED WITH

**`cfd-supervisor` rules, on 2026-09-13, before any result for this rung exists, that CFM-1
runs at `nLayers 2` on all four registered layer patches.** The reason is registered in the
supervisor's own terms and is a statement about **mechanism and the `y+` window**, not about a
gate outcome:

> **"cfMesh builds the entire layer stack inside one octree cell by construction
> (`refineBoundaryLayersFunctions.C:684-714`; `maxFirstLayerThickness` is a `min()` that can
> only thin). 2 layers is the count that lands inside §5's registered `y+` 30-60 wall-function
> window; 6 does not."**

**Two independent routes reach the same number and both are cited:**

1. **This rung's own arithmetic**, §5 and §12 above: at `n = 2`, `r = 1.2`,
   `Σ = (1.2² − 1)/0.2 = 2.2`, so `t_1 = s_P / 2.2 = 6.25e-4 / 2.2 =` **`2.840909e-4 m =
   0.2841 mm`**, and the stack is `t_1 · Σ = 6.25e-4 m` = **`S = 1.00` local cells exactly**.
2. **A sister lane's L2 analysis**, `cases/PPTC_VP1304/PRISM_A2_YPLUS_AND_L2_COMPUTED_FROM_OUR_SIDE.md`,
   §5 feasibility table (`:154-161`, header at `:152`: *"ratio 1.2, blades local cell 0.625 mm,
   design point J = 1.2021, r/R 0.70"*). **The `nSurfaceLayers 2` row is line `:157`** —
   *"2 | 0.2841 mm | 51.5 | YES — mid-window"*. **The registered `nSurfaceLayers 6` row is
   line `:161`** — *"6 (registered) | 0.0629 mm | 11.4 | NO"*. Both line numbers are given
   because the brief that ordered this amendment cited `:161` for the analysis as a whole, and
   `:161` is the **6**-layer row; the number the ruling rests on is at `:157`.
   That record was produced from a different starting point (MESH_STANDARD §16.3 rule L2 on
   the **snappy** PRISM-A2 registration) and arrives at **0.2841 mm to four figures**, the same
   number as route 1. **The agreement is between two derivations, not two readings of one.**

`y+ = 51.5` sits mid-window in the §6.3 wall-function band **30–60**. At 6 layers the same two
routes give `y+ = 11.4`, **below the window, at any first-layer height** — §5 above and that
record's `:163-164` both state it: *"At the registered `nSurfaceLayers 6` and
`expansionRatio 1.2`, no first-layer height satisfies both y+ ≥ 30 and L2 ≤ 1.0. The maximum
y+ obtainable under L2 at 6 layers is 11.4."*

### A2.2 THE SUSPICION THIS AMENDMENT DESERVES, SAID PLAINLY BY THE LANE THAT WROTE IT

**A registration whose predicted `GATE FAIL` is amended away, by the team that registered it,
before the run, is exactly the shape a reader should distrust.** The freeze in §2b exists to
make "we changed the gate once we saw the answer" impossible, and the honest position is that
this amendment gets the *form* of that move even though it cannot be the substance (there is no
answer — A0). Three things are offered against it, and none of them is "trust us":

- **The reason is the physics and the `y+` window, not the outcome.** The ruling in A2.1 turns
  on `S = 1.00` local cells and `y+ = 51.5`; it would be the same ruling if G3 stayed a
  predicted `GATE FAIL`.
- **The falsification is not removed, it is relocated and named.** A2.4 records that at 2
  layers G3 and P-CFM **stop being independent** — G3 becomes implied by P-CFM — and registers
  that as a **loss of falsifying power**, with the surviving falsifier identified.
- **A gate got HARDER to meet, not easier.** A2.5's re-statement of G1 replaces an
  **unmeetable** coverage definition with a meetable one, and A2.3 records that the §4
  discriminator's headroom **falls from 5.0× to 1.10×** — the reader is now a much tighter
  instrument than it was at 6 layers, and that is registered as a cost of this ruling.

### A2.3 THE §4 AND §5 ARITHMETIC, RE-STATED AT 2 LAYERS — ORIGINALS STRUCK, NOT REWRITTEN

> **§4, lines 147-150** — ~~"cfMesh at 6 layers / ratio 1.2 is predicted at `t_1/s_P = 0.1007`
> and ratios `1.200`. `FIRST_FRAC = 0.5` sits between them by 2× on one side and 5× on the
> other."~~ — **STRUCK. Superseded:** cfMesh at **2** layers / ratio 1.2 is predicted at
> **`t_1/s_P = 0.454545`** and ratios **`1.200`**. A layerless cartesian column still reads
> `t_1/s_P = 1.000`. `FIRST_FRAC = 0.5` now sits between them by **2.20× on the layerless side
> and only 1.10× on the layered side.**
>
> **THIS IS A REAL WEAKENING OF THE DISCRIMINATOR AND IS REGISTERED AS ONE.** It still holds,
> and the reason is structural rather than lucky: §5 establishes `magv ≤ s_P` (the octree can
> only thin the hair edge), so `t_1 = magv/2.2 ≤ 0.4545 s_P < 0.5 s_P` **for every face,
> unconditionally**. The 10% headroom cannot be eaten by a thicker `magv` because a thicker
> `magv` is not available. `FIRST_FRAC`, `RLO`, `RHI` and `MAXWALK` are **unchanged** at
> `0.5 / 1.10 / 1.35 / 16`; the ratio band still admits 1.200 and still excludes the 2.0 of a
> 2:1 octree transition.

> **§5, lines 172-183** — the `n = 6` table — **STRUCK IN ITS ENTIRETY. Superseded** by the
> table below at `n = 2`, `r = 1.2`, `Σ = (1.2² − 1)/0.2 = 2.200000`, `1.2¹ = 1.2`:
>
> | patch | `s_P` (m) | registered `t_1` at n=2 (m) | registered stack (m) | stack / `s_P` | **cfMesh `t_1` (m)** | ratio to registered |
> |---|---|---|---|---|---|---|
> | blades | 6.25e-4 | 2.840909e-4 | 6.250000e-4 | **1.00000** | **≤ 2.840909e-4** | **≤ 1.00000×** |
> | hub | 1.25e-3 | 5.681818e-4 | 1.250000e-3 | 1.00000 | ≤ 5.681818e-4 | ≤ 1.00000× |
> | cap | 1.25e-3 | 5.681818e-4 | 1.250000e-3 | 1.00000 | ≤ 5.681818e-4 | ≤ 1.00000× |
> | shaft | 2.5e-3 | 1.1363636e-3 | 2.500000e-3 | 1.00000 | ≤ 1.1363636e-3 | ≤ 1.00000× |
>
> At 2 layers the registered specification **is** cfMesh's structural value: `S = 1.00` is not
> a target that cfMesh happens to hit, it is the constraint cfMesh imposes, so the "registered"
> and "cfMesh" columns coincide and the ratio column is `1.00000×` by construction rather than
> by agreement. **That coincidence is the whole content of A2.4 and it is not presented as a
> result.**
>
> **A transcription defect in the struck table is disclosed rather than silently corrected.**
> Its `cfMesh t_1` column carried 4th-significant-figure slips: `6.29461e-5` for blades where
> `6.25e-4 / 9.92992 = 6.294110e-5`; `1.258922e-4` for hub/cap where the value is
> `1.258822e-4`; `2.517844e-4` for shaft where the value is `2.517644e-4`. The errors are
> ≤ 8e-5 relative, they are in a table that this amendment strikes in full, and they are named
> here so that nobody re-derives from them.

> **§5, lines 193-200** — the predicted-`GATE FAIL` paragraph, ~~"At `0.50122×` that becomes
> **≤ 14.4 anywhere**, and **11.4** at `J = 1.2021, r/R 0.70` … cfMesh at the registered
> `nSurfaceLayers 6` and the registered blade cell cannot reach the §6.3 `y+` window"~~ —
> **STRUCK.** It was true of `n = 6` and this rung no longer runs `n = 6`. **Superseded:** at
> `n = 2` the blade `t_1` is `2.840909e-4 m`, giving **`y+ ≈ 51.5` at `J = 1.2021, r/R 0.70`**,
> **inside** the §6.3 window of 30–60 (A2.1 route 2, `…:161`). `y+` remains **NOT gated and
> NOT measured** in this rung — §6's "`y+` is NOT gated" paragraph (lines 256-259) is
> **unchanged** and still binds; the figure is a **geometric proxy** from the committed
> predictor `cases/PPTC_VP1304/mesh/predict_yplus_from_first_layer.py` and is labelled a proxy
> wherever it is reported.

### A2.4 G3 AND P-CFM RE-STATED — AND THE FALSIFICATION THAT IS LOST, NAMED

> **§6 G3 table, lines 245-248** — **BOTH ROWS STRUCK:**
> ~~`G3` — `median t1 ∈ [1.13028e-4, 1.38145e-4]` m, the registered `1.255867e-4` ± 10%~~
> ~~`P-CFM` — `median t1 ∈ [5.66515e-5, 6.29461e-5]` m~~
> ~~and the sentence "**G3 is predicted `GATE FAIL` and P-CFM is predicted `PASS`.**"~~
>
> **SUPERSEDED, at `nLayers 2`.** Instrument unchanged: `read_cfmesh_layers.py`, field
> `median t1`, patch `blades`.
>
> | id | criterion | label | **registered prediction** |
> |---|---|---|---|
> | **G3** | `median t1 ∈ [2.556818e-4, 3.125000e-4]` m — the 2-layer registered `2.840909e-4` ± 10% | PASS else **GATE FAIL** | **PREDICTED `PASS`** |
> | **P-CFM** | `median t1 ∈ [2.556818e-4, 2.840909e-4]` m — the §5/A2.3 prediction, upper-bounded at `s_P/2.2` because the octree can only thin `magv` | PASS else **GATE FAIL** | **PREDICTED `PASS`** |

**G3 IS NOW A PREDICTED `PASS`, AND THE CONSEQUENCE IS STATED PLAINLY RATHER THAN ENJOYED.**
At 6 layers the two bands were **disjoint** — `[1.13e-4, 1.38e-4]` and `[5.67e-5, 6.29e-5]` —
and that disjointness was the rung's sharpest instrument: exactly one of them could pass, so
the run had to discriminate. At 2 layers the bands **overlap and share a lower limb**: both
start at `2.556818e-4`, and since `magv ≤ s_P` forces `median t1 ≤ 2.840909e-4` anyway, **G3
PASS is implied by P-CFM PASS. The two labels are no longer independent tests.**

**The surviving falsifier, named so it is not lost:** P-CFM still fails, and §5's reading of
`refineBoundaryLayersFunctions.C:684-714` is still falsified, **if `median t1` lands below
`2.556818e-4 m`** — that is the outcome where the octree thins `magv` far below `s_P`, or where
the `min()` cap binds (A2.7), or where the stack is not built inside one cell. **If `median t1`
lands outside P-CFM's band in either direction, §5 must be re-read before anything else in this
rung is believed** — that sentence of §6 (lines 252-254) is **unchanged and still binds.**

### A2.5 G1 RE-STATED — THE CLAUSE THAT HAD SILENTLY BECOME UNMEETABLE

> **§6 G1, line 219** — ~~"Instrument `read_cfmesh_layers.py` (§4), field `C_full(depth>=6)`
> for patch `blades`."~~ — **STRUCK.**
>
> **THIS IS THE FINDING THIS AMENDMENT EXISTS TO CATCH.** `C_full(depth>=m)` is the fraction of
> `blades` faces whose column is layered to depth `m`. A mesh built with **2** layers has **no
> face** at depth ≥ 6. **G1 as written would have read `0.000%` on a perfectly extruded
> 2-layer mesh, fired `C_full < 25.0%`, returned `GATE FAIL`, and fired refusal limb R1** —
> sending the act to the geometry-admission root cause **on the strength of a gate that could
> not be met by construction.** It would have looked exactly like the mesher failing. Nothing
> in the run would have shown the difference.
>
> **SUPERSEDED:** instrument `read_cfmesh_layers.py` (§4) invoked with **`--nlayers 2`**, field
> **`C_full(depth>=2)`** for patch `blades`. The bands and labels are **UNCHANGED**:
>
> | band | label |
> |---|---|
> | `C_full(depth>=2) >= 90.0%` | **GATE REACHED** |
> | `25.0% <= C_full(depth>=2) < 90.0%` | **GATE FAIL** |
> | `C_full(depth>=2) < 25.0%` | **GATE FAIL**, and refusal limb **R1** fires |
>
> **Registered prediction: `>= 90%`**, unchanged, and for the unchanged mechanistic reason
> given at lines 227-232.
>
> **`C_full(depth>=2)` and the separately-printed `C_2(depth>=2)` are the SAME QUANTITY at
> `--nlayers 2`** — the reader computes `Cfull = mean(depth >= nlayers)` and
> `C2 = mean(depth >= 2)` (`read_cfmesh_layers.py:255-259`). They will print identical values,
> and **that identity is itself a cheap arming check on the invocation**: if the two differ,
> `--nlayers 2` did not reach the reader and the reading is void.

> **§6 G2, lines 234-239** — same re-statement, same reason: `C_full(depth>=2)` per patch for
> `hub`, `cap`, `shaft`, at `--nlayers 2`. Threshold `>= 90.0%` → **GATE REACHED** for that
> patch, else **GATE FAIL** for that patch, **labelled per patch, never aggregated** —
> unchanged.

### A2.6 THE READER IS **NOT** EDITED — AND WHY IT DOES NOT NEED TO BE

`cases/PPTC_VP1304/mesh/read_cfmesh_layers.py` is **unchanged, byte for byte**, and still
re-hashes to `c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8` (§14 item 4,
which therefore stands). The layer count is **already a parameter**, not a constant: `--nlayers`
(`:436`), threaded into `measure()` and into `selftest(a.tmp, nlayers=a.nlayers)` (`:443`).
Its default of `6` (`:436`), the `selftest(..., nlayers=6)` signature default (`:335`) and the
docstring's 6-layer separation figures (`:25-26`) are **defaults and prose, overridden on every
registered invocation below**, and **they are left in place deliberately**: editing a
measurement script to move a gate, before the gate has a value, is a worse defect than a stale
default. The **invocation** is what this amendment registers.

### A2.7 THE DEFECT THIS SWEEP FOUND THAT THE RULING DID NOT NAME — `maxFirstLayerThickness` WOULD HAVE BOUND AND DEFEATED THE RULING

**Registered here because it is exactly the class of clause A2.5 is about.** The case dictionary
carries `maxFirstLayerThickness` per patch at the **6-layer** registered first-layer heights
(D6; `meshDict:93, 99, 105, 111`): blades `1.2559e-04`, hub `2.5117e-04`, cap `2.5117e-04`,
shaft `5.0235e-04` m. D6 registered the prediction that it **does not bind** — true at 6 layers,
where the computed first sub-layer is `6.294110e-5 m < 1.2559e-4 m`.

**At 2 layers it binds, and it binds hard.** The computed first sub-layer becomes
`2.840909e-4 m`, and `refineBoundaryLayersFunctions.C:684-714` applies the cap as a `min()`:
`min(2.840909e-4, 1.2559e-4) = 1.2559e-4`. **The dictionary would have thinned `t_1` straight
back to the 6-layer value**, delivering `y+ ≈ 28.8` at best — **below the 30–60 window the
ruling exists to reach** — and `median t1 = 1.2559e-4`, which is **outside P-CFM's re-stated
band and inside G3's struck 6-layer band.** The run would have returned the old prediction and
looked like a confirmation of it.

**Reconciled, as a necessary consequence of the ruling and not as a new choice.** The caps are
re-set to the **same `s_P/Σ(n=2)` arithmetic**, rounded **UP** at the fifth significant figure
so that the `min()` provably cannot bind:

| patch | exact `s_P / 2.2` (m) | registered cap (m) | cap exceeds computed by |
|---|---|---|---|
| blades | 2.8409091e-4 | **2.8410e-4** | 3.20e-5 relative |
| hub | 5.6818182e-4 | **5.6819e-4** | 1.44e-5 relative |
| cap | 5.6818182e-4 | **5.6819e-4** | 1.44e-5 relative |
| shaft | 1.1363636e-3 | **1.1364e-3** | 3.20e-5 relative |

**The rounding direction is registered, not silent:** every cap is ≥ the computed value, by at
most `3.2e-5` relative, so `min()` returns the computed value unchanged and D6's "predicted not
to bind" is restored to truth. **This is a deviation of ≤ 3.2e-5 relative and it is registered
as a deviation rather than rounded into agreement.**

### A2.8 EVERY OTHER PLACE `6` APPEARS, AND WHAT WAS DONE WITH IT — **THE COUNT, DERIVED AND RECONCILED**

A literal sweep of all 441 lines of the frozen document plus the two instruments. **The count
is stated three ways because a count that does not reconcile is itself the finding.**

- **82 lines of the frozen document contain the digit `6`** (`grep -c '6'`).
- **21 of those carry `6` as a LAYER COUNT or a 6-layer-derived figure**, and they are lines
  **53, 148, 149, 152, 172, 176, 177, 178, 179, 188, 189, 195, 196, 197, 219, 247, 248, 309,
  405, 413, 416** — enumerated so a successor can re-derive the same set.
- **The other 61 are not layer counts** and are unchanged: the registered cell **sizes**
  (`6.25e-4`, `1.25e-3`), section references to the parent registration (`§6.1`, `§6.3`),
  sha256 digests, path and file names, the `1e-6` SPD and volume tolerances, the measured cost
  `6.342 core-min`, the `##  6.` section heading, and the `6.` list item in §14.
- **THREE FURTHER SITES ARE 6-LAYER-DERIVED AND CONTAIN NO DIGIT `6`**, which is why a digit
  grep alone would have missed them and why they are named:
  **line 181** (`finalLayerThickness / 1.2^5` — the `1.2^(n-1)` of `n = 6`),
  **line 150** (the tail of §4's separation sentence), and
  **line 293** (§7's rung-label row citing G3's predicted `GATE FAIL`).

**Sites requiring reconciliation: 21 + 3 = 24 in this document, plus 2 instruments. Sites
reconciled: 24 + 2. Nothing in the sweep is unaccounted for.** Disposition:

| site | what `6` is | disposition |
|---|---|---|
| §2 line 53 — "the same registered §6.3 layer specification" | the claim that CFM-1 changes only the mesher | **STRUCK AND RE-STATED — see A2.9. This is a substantive loss and is not buried in a table.** |
| §4 lines 148, 149, 150 | the 6-layer separation figures `t_1/s_P = 0.1007`, "2× on one side and 5× on the other" | **struck and re-stated, A2.3** |
| §4 line 152 — "`C_full(depth>=6)`" | the reader's field name at `--nlayers 6` | **struck and re-stated as `C_full(depth>=2)`, A2.5** |
| §5 line 172 — `n = 6`, `Σ = 9.929920`, `1.2^5 = 2.48832` | the 6-layer series | **struck and re-stated, A2.3** |
| §5 lines 176, 177, 178, 179 — the table body | 6-layer thicknesses, all four patches | **struck in full and re-stated, A2.3** (incl. the transcription slips disclosed there) |
| §5 line 181 — "`finalLayerThickness / 1.2^5`" | the 6-layer definition of registered `t_1`; **no digit 6** | **struck** — at `n = 2` the registered `t_1` is `finalLayerThickness / 1.2¹`, `3.409091e-4 / 1.2 = 2.840909e-4 m`, the value in A2.3's table and the sister lane's §5.1 proposal |
| §5 lines 188, 189 — the L2 credit, `:161`, `0.0629 mm`, `y+ 11.4` | the 6-layer row of the sister lane's table | **struck as the operative row; the credit stands** — the same table's `nSurfaceLayers 2` row is now the operative one, and the mechanistic claim it supports ("L2 is cfMesh's structural constraint") is **unchanged and is the ruling's basis** |
| §5 lines 195, 196, 197 — `28.8`, `≤ 14.4`, `11.4`, `nSurfaceLayers 6` | the 6-layer `y+` consequence and the predicted `GATE FAIL` | **struck and re-stated, A2.3** |
| §6 line 219 — G1's `C_full(depth>=6)` | the unmeetable coverage field | **struck and re-stated, A2.5** |
| §6 lines 247, 248 — G3 and P-CFM bands | 6-layer thickness bands | **both struck and re-stated, A2.4** |
| §7 line 293 — "G3's predicted `GATE FAIL` stands beside it and does **not** downgrade it"; **no digit 6** | the rung-label table's G1-`GATE REACHED` row | **STRUCK as to G3's predicted label only.** Re-stated: *"G3 is now predicted `PASS` (A2.4); if G3 nevertheless returns `GATE FAIL` it still stands beside a `GATE REACHED` G1 and still does not downgrade it."* **The rung-label bands themselves are UNCHANGED** — every row of §7 keys on G0, the controls and G1, none on G3 |
| §8 line 309 — control **B**, "exactly 6 sub-cells at ratio 1.2" | the synthetic positive control | **NOT struck — control B is a control ON THE READER, not on the rung**, and a reader that can see a 6-sublayer column is a stronger demonstration than one that can only see 2. **STRENGTHENED, not replaced:** B is run **twice**, at `--nlayers 6` (as registered, unchanged) **and at `--nlayers 2`**, and **both must pass in both directions**. See A2.10 |
| §12 lines 405, 413, 416 — and the body of §12, lines 403-419 | the "computed but NOT AUTHORISED" successor at `nLayers 6` | **STRUCK AND SUPERSEDED — A2.9** |
| `meshDict:78` (D5 prose), `:91, 97, 103, 109` | `nLayers 6` ×4 | **edited to `2`**, D5 amended with a pointer to this amendment |
| `meshDict:80-84` (D6 prose), `:93, 99, 105, 111` | the 6-layer `maxFirstLayerThickness` caps | **edited, A2.7** |
| `read_cfmesh_layers.py:25-26, 335, 436` | docstring prose and two `nlayers` **defaults** | **NOT EDITED, A2.6** — overridden on every registered invocation |

### A2.9 §12 AND §2's SINGLE-VARIABLE CLAIM — STRUCK AND RE-STATED

> **§12, lines 403-419** — ~~"**`nSurfaceLayers` is a registered §6.3 parameter and this lane
> does not change it.** CFM-1 runs at the registered **6**. The `nLayers 2` variant … is **NOT
> AUTHORISED by this document.**"~~ — **STRUCK.** It was correct when written: the lane that
> wrote it computed the variant, declined to adopt it, and left the ruling to the supervisor
> **with the number already in hand**. §12 did its job. **The supervisor has now ruled (A2.1),
> and `nLayers 2` IS authorised for this rung by this amendment** — for the rung only, and
> **not for the parent open-water registration's §6.3**, which is untouched.

> **§2, line 53** — ~~"at the same registered per-patch cell sizes and the same registered §6.3
> layer specification"~~ — **STRUCK, and this is the honest cost of the ruling.** CFM-1 now
> differs from the snappy baseline in **two** registered respects, not one: the **mesher**, and
> **`nSurfaceLayers` 6 → 2** — alongside the dropped `axisRod` already disclosed at §2.2.
> **A `GATE REACHED` on G1 is therefore no longer a clean single-variable A/B against the
> snappy layer failure, and it is not reported as one.**
>
> **What survives the change, and why G1 is still comparable:** §5 establishes that in cfMesh
> the stack occupies **one local cell at every `n`** — the layer count sets `t_1`, not whether
> extrusion happens. `nSurfaceLayers` therefore moves **G3/P-CFM** (a thickness question) and
> leaves **G1/G2** (a coverage question) on the same footing as the snappy comparison, where
> the baseline is `0 of 724,711 faces (0%)`. **G3 is the gate that is no longer a clean
> comparison, and G3 is the one whose prediction changed.**

### A2.10 CONTROLS, AND THE STOP RULE — **STRENGTHENED, NEVER RELAXED**

§8's stop rule is **UNCHANGED and is restated here in full because this amendment adds to what
it covers**:

> **The rung STOPS unless A, B, C and D each pass IN THEIR OWN DIRECTION. A failure in EITHER
> direction stops it: an instrument that cannot see a layer and an instrument that sees layers
> everywhere are both disqualifying. If any of A–D fails, the rung is `BLOCKED`, and NEITHER a
> `PASS` NOR a `GATE FAIL` from the cfMesh mesh is admitted — the failure is a statement about
> the reader, not about cfMesh, and nothing is said about cfMesh at all.**

Added by this amendment, and **added to the stop rule**:

- **B is run twice**, at `--nlayers 6` (as registered) and at `--nlayers 2` (the count G1 now
  reads). **Both runs must pass in both directions.** A reader armed only at depth 6 is not
  armed for a gate read at depth 2.
- **A is run twice**, at `--nlayers 6` and at `--nlayers 2`, on `F360_coarse`. **Both must read
  `blades C_full == 0.000%` AND `C_2 == 0.000%`.** The 2-layer pass is the one that matters
  now: it is the direct demonstration that the reader **does not** call a plain cartesian
  column a 2-deep layer stack, which is precisely the risk created by A2.3's fall in headroom
  from 5.0× to 1.10×.
- **The arming of C and D does NOT create the registered run directory.** §14 item 1's
  assertion — that `/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh` does not
  exist — must survive the arming. The planted `points` file therefore goes to
  **`/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_READER_ARMING/`**, registered here, which
  is **not** the run directory and is not read by any gate.
- **C and D are armed on `F360_coarse`, which is a read-only borrow.** §13's prohibition on
  writing into `…/F360_coarse/` or `…/PRISM_A2_absthick/` is **unchanged and was honoured**:
  the controls open those paths read-only and every byte written goes to the arming directory.
  §8's registered order — C and D on the **produced** mesh, after the build — is **unchanged**;
  the arming below is the §4 precondition, not a substitute for it, and **C and D are run again
  on the produced mesh when it exists.**

### A2.11 COST — RE-COSTED AT 2 LAYERS, CAP UNCHANGED

Per CLAUDE.md rule 12, the change is costed rather than assumed free. **Two layers cannot cost
more than six**: the boundary-layer refinement subdivides the same near-wall cells into fewer
pieces, so both cell count and mesher time fall. **Every §11 row and the `1200 core-min` CAP
are therefore UNCHANGED** — a cap is an upper bound and this ruling can only move the actual
down. The added control runs (B and A a second time each, at `--nlayers 2`) are inside §11's
existing "reader arming, controls **B** and **A** — 45 core-min" row. **No new budget is
created by either amendment**, and the estimate-vs-actual calibration row owed to
`docs/COST_CALIBRATION.md` at completion (§11) is unchanged in obligation.

---

## A3 — WHAT THESE AMENDMENTS LEAVE ON DISK

### A3.1 The case dictionary's new hash, replacing the struck §14 item 3

`cases/PPTC_VP1304/mesh/cfmesh/meshDict`, after **both** amendments' edits (D10's
`objectRefinements` block, D5's `nLayers 2`, D6's re-set caps, D9(b) struck in the dictionary):

> **sha256 `51c669991f59087dfa28b940582e1ceece3ccb128f347012bb75f3bc7ccc2dfd`**
>
> and it parses under `foamDictionary` (v2606): **`exit 0, verified after the edits`**.

The published form it was copied from is kept beside it:
`cases/PPTC_VP1304/mesh/cfmesh/meshDict.bunnyOctree.PUBLISHED`, sha256
`da05baa6e65267a73680ab3325336a989a9f6fe72fc07e271bc72abb1497c487`, re-hashed after the copy.

### A3.2 The reader's arming — the §4 blocking precondition is DISCHARGED SEPARATELY

**This document registers the controls; it does not record their outcome.** §4 registers the
arming as a blocking precondition and §8 registers the stop rule; **the four controls' actual
outputs are recorded in `verification/runs/PPTC_VP1304_runs/CFM1_READER_ARMING.md`**, which is
a run record and not a pre-registration. §14 item 6 ("the reader is unexercised") described the
state **at the v1.0 freeze** and is left standing as the historical statement it is; the arming
record supersedes it as a description of the present.

**The rung's `BLOCKED` limb is unchanged:** if any control fails in either direction, CFM-1 is
`BLOCKED`, `cartesianMesh` does not run, and nothing is said about cfMesh at all.

### A3.3 What is still true after both amendments

- **No MESHER and no SOLVER compute for this rung has been run, and none was launched by the
  lane that wrote this.** `/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh` still
  does not exist, before and after the arming. **The reader's controls HAVE been run** — that
  is the §4 blocking precondition, it is costed in §11's own control rows, it wrote only to
  `…/CFM1_READER_ARMING/`, and its outcome is in the arming record named in A3.2, not here.
  **Stated precisely rather than as a blanket "no compute", because the two are not the same
  claim and §2b turns on the mesher one.**
- **CFM-1 still must not start before PRISM-A2 reports** (preamble), and PRISM-A2 was still in
  flight at this amendment.
- **Nothing may be sent, filed, uploaded, registered, posted or commented outside this box**
  (§13, CLAUDE.md rule 7).
- **No `KT`, `KQ` or any solved quantity may be graded on this mesh** (A1.5).

<!-- END OF AMENDMENTS v1.1 -->
