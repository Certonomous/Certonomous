# PREDICTION RECORDED BEFORE L3 IS EXTRUDED

Written while `L3/volumeMesh.xyz` does not exist. Purpose: the L1->L2 trend below is the exact
signature that killed `CRM_M085` — *"every quality column worsens monotonically with refinement"* —
so it is stated as a prediction now, and graded against L3 afterwards, rather than explained after
the fact.

| quantity | L1 (144,768) | L2 (1,158,144) | direction | **L3 prediction if the trend is linear in level** |
|---|---|---|---|---|
| G-M1 max non-orthogonality | 56.7598 | **67.1105** | WORSENS +10.35 | **~77.5 — would BREACH the 70 gate** |
| G-M2 max skewness | 2.78097 | **3.30838** | WORSENS +0.527 | ~3.84 — would pass, marginally |
| G-M3 max aspect ratio (advisory) | 153.311 | 168.969 | worsens +15.7 | ~185 — far below the 1000 advisory |
| checkMesh face-tet errors | 146 | **20** | **IMPROVES** | fewer still |
| pyHyp min quality (G-M4) | -0.07180 @ layer 3 | **-0.03220 @ layer 3** | **magnitude HALVES** | negative again, smaller |

**Two columns move in OPPOSITE directions.** Non-orthogonality and skewness worsen; the face-tet
error count and the pyHyp negative-quality magnitude improve. **A single "quality degrades with
refinement" story does not fit this data**, which is why the DPW5 verdict is NOT carried over here
(§1: this rung inherits nothing).

🔴 **The honest form of the prediction: G-M1 is the gate at risk, and 77.5 > 70.** If L3 returns a
non-orthogonality above 70 that is a **`GATE FAIL` for L3**, registered in advance, not a surprise.
If it returns below 70, the trend is sub-linear and that is a finding too.

**The negative min quality at layer 3 is predicted to recur**, because it has now appeared at two
resolutions 4x apart, at the SAME layer index, and on surfaces that are exact node subsets of one
another (G-M5 deviation 0.000000e+00, planted-control verified). It is a property of the shared
geometry, not of a resolution.
