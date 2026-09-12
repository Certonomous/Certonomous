# THE SYMMETRY PLANE IS PLANAR. MY NON-PLANARITY ALARM IS WITHDRAWN.

## The band sweep — a PLATEAU, not a fitted threshold

Faces with |n_y| > 0.99 (root-plane candidates by NORMAL), counted within a y-band:

| band | n_faces | max\|y\| in band | physical |
|---|---|---|---|
| 1e-9 | 13,312 | 0.0 | — |
| 1e-6 | 13,728 | 4.42e-07 | 0.000 m |
| **1e-3** | **14,144** | **9.491133e-06** | **0.000066 m** |
| **1e-2** | **14,144** | 9.491133e-06 | 0.000066 m |
| **1e-1** | **14,144** | 9.491133e-06 | 0.000066 m |
| **1e+0** | **14,144** | 9.491133e-06 | 0.000066 m |
| 1e+1 | 14,231 | 3.77e+00 | 26.3 m |
| 1e+2 | 14,297 | 8.51e+01 | 594.0 m |

🟢 **14,144 is STABLE ACROSS FOUR DECADES of band, 1e-3 to 1e0 — and 14,144 is exactly the
block-topology prediction.** Below 1e-3 root-plane faces are lost; above 1e+1 far-field faces
(which also carry y-normals, at y ≈ 85) contaminate it. **The threshold is justified by a plateau,
not chosen to make a number agree** — which is the difference between a measurement and a fit.

## THREE INDEPENDENT ROUTES NOW AGREE ON 14,144

1. **Block topology** — 136 free perimeter edges × 104 layers (`{1: 136, 2: 1028}`).
2. **Face normal + band plateau** — this table.
3. **Total consistency** — 11,136 + 11,136 + 14,144 = 36,416 = the mesh's actual `defaultFaces`.

## THE ANSWER TO THE DECISIVE QUESTION

**max |y| over the root plane = 9.491133e-06 mesh-units = 6.62e-05 m = 0.066 mm.**

🟢 **PLANAR. A `symmetryPlane` BC is well posed. There is NO second pyHyp defect.** The drift is
hyperbolic-marching round-off at the 1e-6 level, not a geometric fault.

## 🔴 WITHDRAWN: MY 0.48 m NON-PLANARITY ALARM

I reported that 1,104 faces sat at 1e-9 ≤ max|y| < 1e-1 with offsets to **6.920e-02 mesh-units =
0.48 m**, and warned this might be a second pyHyp defect. **That was wrong.** P1's diagnostic binned
**all** boundary faces by max|y|, not root-plane faces — so the 272 faces in its 1e-3..1e-1 bin are
**body-surface faces near the wing root**, which legitimately have small y. They are not on the
symmetry plane at all. Restricted to actual root-plane faces, the sweep is flat at 14,144 from 1e-3
to 1e0: **no root-plane face lies between 1e-3 and 1e0.**

## AND P1's DIAGNOSIS IS CORRECTED TOO

P1's `Y_SYMM_TOL = 1e-9` was **too tight**, and that IS the whole of its symmetry shortfall: 832
root-plane faces sit between 1e-9 and 9.49e-06. **But loosening it when P1 failed would still have
been wrong** — at that moment there was no plateau, no independent count, and no way to distinguish
a tolerance error from genuine off-plane faces. **The same change is a fit before the plateau exists
and a measurement after it.** The gate stays `GATE FAIL`; what changed is that the cause is now known.

## 🔴 THE DEFECT IN THIS PROBE, WHICH ITS OWN CONTROL PASSED OVER

The first version classified by normal alone and reported **max|y| = 85.15 mesh-units = 594 m,
"NOT PLANAR"**. That is the far-field extent, not a displacement: **far-field faces at y ≈ 85 also
have y-normals.**

**Its plant tilted a root-plane face and required it to be dropped. That exercised the
"reject a tilted face" path and was structurally blind to the "admit a distant y-normal face" path
— the phenomenon arrived by a route the plant did not cover.** The control printed `CONTROL PASSED`.

**What caught it was the absurdity of 594 m, not the control.** A displacement the size of the
domain is not a displacement. **Had the contamination been 0.5 m instead of 594 m it would have read
as a plausible defect and I would have filed it.**
