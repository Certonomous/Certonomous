# M6C2 ROUTE (c) L1 — VOLUME RESULT. **NON-ORTHOGONALITY CLEARS WITH ZERO OVER-GATE FACES. SKEWNESS FAILS ON TWO FACES.**

Prediction registered and committed at `aa226e440` **before** any `checkMesh`
(`MP/L1_PREDICTION.md`). Measured here. **The report text is read; rc is not the verdict.**

Artifacts: `MP/L1/log.extrude` (rc = 0), `MP/L1/m6c2_mp_L1_vol.cgns`, `MP/L1/log.checkMesh`,
`MP/L1/RC_CHECK.txt`. 452,608 cells, **100 % hexahedra**, 470,085 points.

## THE GATES

| quantity | gate | measured | |
|---|---|---|---|
| max non-orthogonality | ≤ 70 | **66.4228** (avg 13.68) | **CLEARS** |
| severely non-orthogonal faces (> 70) | — | **ZERO** | — |
| **max skewness** | **≤ 4** | **4.90021, on 2 faces** | **FAILS** |
| boundary openness | — | 3.87e-16 | OK |
| max cell openness | — | 1.62e-15 | OK |
| face pyramids | — | 0 incorrectly oriented | OK |
| concave cells | — | none | OK |
| max aspect ratio | — | 391.235 | OK |

**THE ZERO IS CONTROLLED, NOT ASSUMED.** `checkMesh` wrote no `nonOrthoFaces` set — and in
the same run, through the same mechanism, it **did** write `cellDeterminant`,
`lowWeightFaces`, `shortEdges` and `skewFaces`. **The set-writer was demonstrably able to
produce a non-empty set, so the absent one is an absence of faces, not a blind reader.**

## WHERE THE TWO SKEW FACES ARE

By face centroid from `sets/skewFaces` (`MP/locate_over_gate_faces.py`):

**x = 1.1400, y = 1.1963, z = ±0.0003, r = 1.6525 — both faces, 100 % within r < 2 m.**

**y = 1.1963 m is EXACTLY the semispan: the crown plane.** x = 1.1400 is the trailing edge
at the tip (Addendum 3 measured x_TE = 1.13424 near the tip). The two faces straddle z = 0
symmetrically. **They are the blunt-trailing-edge corner of the tip crown — a cap-local
defect of exactly two faces, 0.900 over a gate of 4.**

## 🔴 THE PREDICTION IS FALSIFIED — AND MY OUTCOME TABLE DID NOT COVER WHAT HAPPENED

The prediction was: *L1 fails the non-orthogonality gate in the SAME far-field location.*
**It does not fail it at all** — 66.4228 with zero over-gate faces. **FALSIFIED.**

**And none of the three rows I fixed in advance matches.** Rows 1 and 2 both require
max non-orth **> 70**, which is false. Row 3 requires non-orth ≤ 70 **and skewness ≤ 4**,
and skewness is 4.90. **The case that occurred — clears non-orthogonality, fails skewness —
is one I did not anticipate, so my own table is incomplete.** I am recording that against
myself rather than stretching row 3 to cover it: **an outcome table that has to be
reinterpreted after the fact is doing none of the work it was written to do.**

**What the measurement does establish, independently of the table:** the probe's far-field
sheet at 80.3435° was **specific to A3's surface, not intrinsic to marching a wing O-mesh
at N = 33 / marchDist = 12.** On our own body the same march produces **zero** over-gate
non-orthogonal faces.

## THE M6 MESH LINE

**Still `BLOCKED`, and the reason is now two faces instead of a topology.** L1 does not
clear both hard gates, so nothing here is a pass. **L2 and L3 are NOT measured** — and
topology 1 cleared at L1 and crossed at L2, so one level settles nothing in either
direction. §A2.3's outcome table is the supervisor's to apply, not this lane's.

**The progression is the finding:** topology 1 failed on 72 over-gate non-orthogonal faces
worsening under refinement; the probe failed on an 11,571-face far-field sheet; route (c)
fails on **2 skew faces at one geometric corner**, with non-orthogonality clear.

## COST

Extrusion `EXTRUDE_WALL_S 1048.43` × 1 rank = **17.47 core-min**. Conversion
`VOL2P3D_WALL_S 19.20`, plus `plot3dToFoam`, `checkMesh` and localisation, serial and
niced ≈ **4 core-min**. **Total ≈ 21.5 core-min, derived $0.018 at $0.0513/core-h —
DERIVED, NOT MEASURED.** Inside the 300 core-min cap of M6C1 Addendum 4 §A4.4.
The 11.9 MB CGNS, the PLOT3D and the polyMesh are not committed.
