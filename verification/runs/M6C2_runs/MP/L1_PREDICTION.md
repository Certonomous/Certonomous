# M6C2 ROUTE (c) L1 — PREDICTION, FIXED AND COMMITTED **BEFORE** `checkMesh` IS RUN

**Written 2026-09-11 by the cfd `lab-lane` while the L1 extrusion is still marching.
No volume has been converted and no `checkMesh` has been run on it.** This file exists
because the sibling `ROUTE_PROBE` criterion was written in advance and **never committed**,
so its freeze rests on mtime and its label cannot be banked. **That failure is not
repeated here: this commit precedes the measurement.**

Condition, checkable: `verification/runs/M6C2_runs/MP/L1/` contains no `*.cgns`, no
`foam/` directory and no `log.checkMesh` at the moment this is committed.

## WHAT IS BEING TESTED

The probe measured, on A3's body, that **100 % of 11,571 over-gate faces lay in the far
field** — r 3.335–6.181 m, 3.5–7.5 root chords downstream, hugging the root symmetry
plane — and **ZERO lay within r < 2.0 m of the body or on the multi-patch cap**. If that
is the mechanism, it is a property of **marching a wing O-mesh to `marchDist` 12 m in 33
layers**, not of whose wing it is or how the tip is capped. Route (c) uses the same
`N = 33`, `marchDist = 12.0`, different body, different cap, `s0 = 2.4271e-04`.

**PREDICTION: L1 fails the non-orthogonality gate in the SAME far-field location, and its
tip cap contributes no over-gate face.**

## THE THREE OUTCOMES, FIXED NOW

Localisation is by face centroid from `constant/polyMesh/sets/nonOrthoFaces`, the same
method as the probe. The body occupies r < 1.5 m (semispan 1.1963 m, root chord 0.8059 m).

| outcome | reading |
|---|---|
| max non-orth **> 70** and **≥ 90 %** of over-gate faces at **r ≥ 2.0 m** | **PREDICTION HOLDS.** The defect is the far-field march — body-independent and cap-independent. Route (c)'s cap is vindicated and M6's blocker is a march-parameter question, not a topology question. |
| max non-orth **> 70** and **> 10 %** of over-gate faces at **r < 2.0 m** | **PREDICTION FAILS.** Route (c) carries a body- or cap-local defect of its own, distinct from the probe's, and the cap is NOT vindicated. |
| max non-orth **≤ 70** with skewness ≤ 4 | **PREDICTION FAILS, in the useful direction.** The probe's far-field failure is then specific to A3's surface and not intrinsic to the march, and route (c) clears at L1 where the probe failed. **L1 alone would still settle nothing** — topology 1 cleared at L1 and crossed the gate at L2, so L2 and L3 must be measured before any `PASS` is spoken. |

## WHAT THIS FILE MAY NOT BE USED FOR

**It changes no gate, threshold, cap, band or label, and it grades no M6 result.** M6C1's
verdict stays `BLOCKED`; §A2.3's outcome table is untouched and is the supervisor's to
apply. This registers one mechanism prediction and its three readings, nothing more.

**Cost of the measurement it precedes: CGNS→PLOT3D→`plot3dToFoam`→`checkMesh`, serial and
niced, ≈ 4 core-min, derived $0.003 at $0.0513/core-h — DERIVED, NOT MEASURED. Inside the
300 core-min cap registered in M6C1 Addendum 4 §A4.4.**
