# M6C2 ROUTE (c) L2 — VOLUME RESULT. **AXIS C2: THE FAR-FIELD MECHANISM RETURNS ON OUR OWN BODY. SKEWNESS IMPROVES AND STAYS TWO FACES AT THE SAME CORNER.**

Graded against `MP/L2_L3_OUTCOME_PARTITION.md`, committed at `9651f6cc4` (17:16:48Z)
**before `MP/L2/` existed** (created 17:17Z). Read by `MP/read_level_gates.py`.
**`checkMesh`'s rc is not the verdict at any level; the report text is read.**

Artifacts: `MP/L2/log.extrude`, `rc.extrude`, `time.extrude`, `log.vol2p3d`,
`log.plot3dToFoam`, `log.checkMesh`, `log.locate`, `RC_CHECK.txt`.

## ROW 0 — COMPLETION. **PASSED, SO THE PARTITION IS READ.**

`EXTRUSION COMPLETE` present; wrapper rc = 0 **captured inside the container wrapper**,
not from `docker run`, which exits 0 regardless. CGNS 38,883,328 bytes written;
`plot3dToFoam` rc = 0 with an `End` line; `checkMesh` rc = 0.

## THE DELIVERED MESH — AS `checkMesh` REPORTS IT, NOT AS PLANNED

| quantity | value |
|---|---|
| cells | **1,527,552** |
| hexahedra | 1,527,552 — **100 %** |
| points | 1,566,775 |
| faces | 4,621,680 |
| geometric (non-empty) directions | **3** |

**The `geometric` line is the one read.** `checkMesh` prints a `solution (non-empty)
directions` line one line below it which also reads 3 here; matching on `(non-empty)`
selects the wrong line, because the geometric line reads `(non-empty/wedge)`.

**`r21` RE-DERIVED FROM THE DELIVERED MESH:** 1,527,552 / 452,608 = **3.3750**, so
**r21 = 3.3750^(1/3) = 1.500000**. The march family registered `N` = 33/49/73 as
**node** counts giving **32/48/72 cell layers**, ×1.5 exactly; the surface files carry
14,144 / 31,824 faces, ×2.25 exactly. **The plan's exact 1.5 is now MEASURED and no
longer assumed.**

## AXIS A — SKEWNESS, GATE 4

| | L1 (committed `9572e4f42`) | L2 |
|---|---|---|
| max skewness | 4.90021 | **4.15016** |
| highly skew faces | 2 | **2** |
| verdict | FAILS | **FAILS** |

`S2 = 4.15016 > 4`, so **A1 is excluded** — A1 requires `S2 ≤ 4` **and** `S3 ≤ 4`.
**Axis A is A2 or A3 and is not determined without L3.**

## AXIS B — **`PENDING`, AND NOT READABLE FROM THIS LEVEL**

Axis B is defined **entirely on `S3 − S1`**; `S2` appears only in Axis A. With L3
unbuilt, **not one of the nine cells can be named.**

**`S2 − S1` = 4.15016 − 4.90021 = −0.75005. THIS IS A DIAGNOSTIC AND IS NOT AXIS B.**
Reporting it as Axis B would reinterpret a partition after the fact to answer a question
it did not ask — the defect that killed `L1_PREDICTION.md` and the reason this file exists.

## 🔴 AXIS C — NON-ORTHOGONALITY, GATE 70. **C2.**

| | L1 | L2 |
|---|---|---|
| max non-orthogonality | 66.4228 | **74.6431** |
| average | 13.6843 | 13.8085 |
| severely non-orthogonal faces (> 70) | **ZERO** | **1,019** |
| verdict | CLEARS | **FAILS** |

**C2 is the "otherwise" branch and the partition names in advance what it would mean:
*new information, and it would mean the far-field mechanism the probe exhibited returns
at finer marching.* It does.**

**WHERE THE 1,019 FACES ARE** (`MP/L2/log.locate`, centroid classifier with its planted
near/far control passing — one synthetic face at r = 0.583 placed inside, one at
r = 4.001 placed outside, through the same code path):

- **1,013 of 1,019 — 99.41 % — beyond r ≥ 2.0 m: the far field.** 6 faces (0.59 %) within r < 2.
- r: min 1.5741, **median 3.4078**, max 4.0523. x: 1.1188 → 3.7356. |z| up to 2.55.

**This refutes the reading L1 supported.** `L1_RESULT.md` concluded that the probe's
far-field sheet at 80.3435° was *"specific to A3's surface, not intrinsic to marching a
wing O-mesh at N = 33 / marchDist = 12"*, on the evidence of **zero** over-gate faces.
**That conclusion was true of L1 and false of the family: the mechanism is present on our
own body and needed a finer march to appear.** One level settled nothing, exactly as
`L1_RESULT.md` itself warned.

## WHERE THE TWO SKEW FACES ARE — **THE SAME PHYSICAL CORNER, AT BOTH LEVELS**

Different meshes and different faces: L1 set `(1373808 1373823)` of 1,375,168 faces;
L2 set `(4618632 4618655)` of 4,621,680. Centroids at full precision:

| | x | y | z | r |
|---|---|---|---|---|
| L1 | 1.1399695687 | **1.1963000000** | ±0.0003026292 | 1.6524722083 |
| L2 | 1.1400078420 | **1.1963000000** | ±0.0003048750 | 1.6524986120 |

**Δx = 3.83e−05 m, Δz = 2.25e−06 m; `y` is bit-identical at the semispan.** The defect is
pinned to the same geometric point to **3.2e−05 of the semispan** while the mesh refines
×1.5 — it converges to a fixed location rather than moving with the grid.

**⚠️ A PRECISION TRAP, RECORDED BECAUSE IT NEARLY LANDED IN THIS FILE.**
`locate_over_gate_faces.py` prints 4 decimals, at which L1 and L2 read **identically** —
`x = 1.1400, y = 1.1963, z = ±0.0003, r = 1.6525`. A *converging* pair printed as an
*identical* pair, which is a stronger and different claim. The digits above were
recomputed at full precision through the same loader before anything was written.

## THE ZERO CONTROL

`checkMesh` wrote **six non-empty sets** in this run: `cellDeterminant` (139,093),
`lowQualityTetFaces` (12), `lowWeightFaces` (6), `nonOrthoFaces` (**1,019**),
`shortEdges` (4,603), `skewFaces` (2). **No zero needs controlling at L2** — the
quantity that was zero at L1 is non-zero here. The L1 zero remains controlled on its own
four non-empty siblings.

## OTHER REPORTED QUANTITIES

Boundary openness 1.45e−16; max cell openness 1.65e−15; face pyramids OK; concave cells
OK; **max aspect ratio 508.377** (L1: 391.235); min face area 1.80e−09; min volume
2.47e−12. `shortEdges` grew 294 → 4,603 (×15.7, against a cell ratio of ×3.375) and
`lowQualityTetFaces` appears at L2 where L1 had none — **reported, gated by nothing.**

`plot3dToFoam` added 78,048 undefined faces to `defaultFaces` and `vol2plot3d` reported
`smallest |dx| = 0`; **both appear identically at L1** (34,688 faces, ×2.25 = the face
ratio exactly), so neither is an L2 anomaly.

## COST

`EXTRUDE_WALL_S 4738.16` × 1 rank = **78.97 core-min** against **44 registered**
(ratio **1.795**). Conversion + `checkMesh` + localisation **85 s = 1.41 core-min**
(`VOL2P3D_WALL_S 48.38` measured within it). **L2 total ≈ 80.4 core-min, derived $0.069
at $0.0513/core-h — DERIVED, NOT MEASURED.**

**The route's registered 300 core-min cap (`M6C1_PREREGISTRATION.md` §A4.4) is not
breached by L2 and cannot accommodate L3** — see `MP/L3_COST_FIT.md`.

## THE M6 MESH LINE

**Still `BLOCKED`.** L2 fails both hard gates. §A2.3's outcome table is the supervisor's
to apply, not this lane's. The CGNS, PLOT3D and polyMesh are not committed.
