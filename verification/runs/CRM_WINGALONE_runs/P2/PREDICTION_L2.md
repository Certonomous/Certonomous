# P2 PREDICTED COUNTS — DERIVED FROM THE BLOCK STRUCTURE, WRITTEN DOWN BEFORE P2 RUNS

**These do NOT come from P1's achieved counts (11,908 / 11,196 / 13,312).** `p2_predict.py`
reads only the 26-block surface CGNS and the extrusion node count `N`; it never opens a P1
artifact. Registering P1's output as P2's prediction would be fitting the prediction to a known
answer, which is the one thing pre-registration exists to prevent.

| quantity | value | how it is derived |
|---|---|---|
| blocks | **26** | CGNS |
| surface cells | **11,136** | Σ (ni−1)(nj−1) over the 26 blocks |
| extrusion cell layers | **104** | N − 1, N = 105 |
| block-boundary edge sharing | **{1: 136, 2: 1028}** | every surface-block boundary edge counted by how many blocks contain it |
| free perimeter edges | **136** | edges shared by exactly ONE block |

| patch | **PREDICTED** | derivation |
|---|---|---|
| **wing** | **11,136** | one face per surface cell at k = 0 |
| **farfield** | **11,136** | one face per surface cell at k = N |
| **symmetry** | **14,144** | 136 free perimeter edges × 104 cell layers |
| **TOTAL** | **36,416** | — |

🟢 **CONSISTENCY CHECK, AND IT IS THE STRONG PART: the derived total is 36,416, which equals the
mesh's actual `defaultFaces` count exactly.** The block model accounts for every boundary face with
none left over, from a completely different route than P1 took.

🔴 **THIS INDEPENDENTLY CONFIRMS THE ORIGINAL PREDICTION AND THEREFORE INDICTS P1's CLASSIFIER, NOT
THE PREDICTION.** §2's 11,136 / 11,136 / 14,144 was first obtained as arithmetic from the surface
cell count with an assumed 136-edge perimeter. **The block structure now yields 136 free edges as a
MEASUREMENT** — so 14,144 is right, and P1's 13,312 (= 128 × 104) is the error.

**My earlier claim that "my prediction was also wrong, arithmetically, 136 assumed against a true
128" IS WITHDRAWN.** I inferred 128 from P1's own failing output — **I took the broken instrument's
number as ground truth about the geometry.** The block structure says 136. **A measurement from the
instrument under test is not evidence about the thing it failed to measure.**

## What this makes P2 a test of

If P2 assigns by topology it will produce 14,144 symmetry faces **by construction**, so the count is
not the interesting output. **The interesting output is the geometry of that patch:** P1's diagnostic
found 1,104 faces at 1e-9 ≤ max|y| < 1e-1 with offsets to **6.920e-02 mesh-units = 0.48 m physical**.
**If ~832 of those are topologically on the root plane, then pyHyp's symmetry plane IS NOT PLANAR**,
and a `symmetryPlane` BC on a non-planar patch is ill-posed. **P2 must therefore MEASURE and REPORT
max |y| over the symmetry patch it builds — that number, not the face count, is what decides whether
this mesh can carry a symmetry condition at all.**
