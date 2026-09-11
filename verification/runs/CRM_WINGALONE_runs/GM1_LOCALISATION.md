# WHERE G-M1 FAILS AT L3 — ALL 8 FACES ARE ONE GEOMETRIC FEATURE

**This does not change L3's verdict.** G-M1 is registered on the **max**, the max is **79.3672 deg**,
and the gate is **<= 70**: **`GATE FAIL`** stands. This section says *where*, because a gate that fails
on 8 faces at one corner is a different engineering problem from one that fails everywhere.

## Measured

`checkMesh` wrote the breaching faces to `L3/foam/constant/polyMesh/sets/nonOrthoFaces`:
**8 faces out of 27,868,288.** Their centres, computed from the mesh itself:

| face id | centre (mesh-units) | \|r\| | % of farfield | location |
|---|---|---|---|---|
| **0 (CONTROL)** | (0.017, 0.012, -0.021) | 0.029 | 0.0 % | near-wall — *a face known to exist, proving the lookup works* |
| 15457192 | (3.247, 3.760, 0.344) | 4.980 | 5.9 % | NEAR-WALL |
| 15457195 | (3.247, 3.761, 0.344) | 4.980 | 5.9 % | NEAR-WALL |
| 15457198 | (3.247, 3.761, 0.345) | 4.981 | 5.9 % | NEAR-WALL |
| 15457486 | (3.247, 3.761, 0.345) | 4.981 | 5.9 % | NEAR-WALL |
| 15457517 | (3.247, 3.761, 0.345) | 4.980 | 5.9 % | NEAR-WALL |
| 15457563 | (3.247, 3.761, 0.344) | 4.981 | 5.9 % | NEAR-WALL |
| 15457566 | (3.247, 3.761, 0.344) | 4.981 | 5.9 % | NEAR-WALL |
| 15457885 | (3.247, 3.761, 0.345) | 4.980 | 5.9 % | NEAR-WALL |

**All eight are at the same point, to three decimals.**

## What that point is — identified from the surface census, not guessed

The surface bounding box measured by this lane on **all three** levels:
**x_max = 3.2473504071, y_max = 3.7666681523, z_max = 0.3461330920.**

The cluster sits at **(3.247, 3.761, 0.345) — the x_max / y_max / z_max corner: the WING-TIP
TRAILING EDGE.** That is the sharpest geometric feature on the body, and the one place where a
hyperbolic extrusion must turn a normal through the largest angle.

## 🔴 WHAT THIS IS **NOT** — SAID EXPLICITLY SO IT IS NOT MISREAD AS THE M6 FINDING

The cfd team terminated M6 route (c) on a **far-field** mechanism intrinsic to pyHyp hyperbolic
extrusion on an O-mesh, reproduced on two bodies. **This is not that.** These faces are at
**5.9 % of the farfield radius** — against a farfield half-extent of **84.893 mesh-units**, they sit
at **4.98**. They are **near-wall, at a surface singularity.**

**A tempting and wrong move would have been to file this as a third body confirming the M6
far-field mechanism.** The radius measurement refutes that, and it was taken before the connection
was drawn rather than after.

## Reader control (rule 3)

The lookup was run on **face 0 first** — a face known to exist — and returned a sensible near-wall
centre at the geometric origin. The 8 results are therefore evidence, not a blind read.
**Resolution stated:** this is measured at **L3 only** (9,265,152 cells). L1 and L2 wrote **no
`nonOrthoFaces` set at all**, because neither has any face above 70 deg — **their maxima are 56.7118
and 68.2589, both printed in their own logs**, so the absence of a set at those levels is a measured
absence and not a missing instrument.

**Artifacts:** `L3/nonortho_faces_raw.txt`, `L3/nonortho_points_raw.txt`,
`L3/foam/constant/polyMesh/sets/nonOrthoFaces`, `locate_nonortho.py`.
