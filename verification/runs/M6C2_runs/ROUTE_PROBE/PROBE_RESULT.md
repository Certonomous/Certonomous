# ROUTE PROBE — RESULT. **ROW 2 OBTAINS: THE PREDICTION IS FALSIFIED.**

**STILL NOT AN M6 MESH.** Built on A3's body, which departs from AR-138. No Cp, no forces,
no solve, no M6 claim. Five mesh-quality numbers about a METHOD, as registered in
`PREDICTION_CRITERION.md` **before** the probe ran.

## THE FIVE METHOD NUMBERS

Artifact `log.checkMesh` (`checkMesh -allGeometry -allTopology`), on the volume in
`foam/constant/polyMesh`: 3,194,880 cells, **100 % hexahedra**, 3,303,729 points.
**The report text is read; rc is not the verdict — and rc was 0 while three checks failed.**

| bound-3 quantity | measured | reading |
|---|---|---|
| boundary closure | `defaultFaces` 217,088 faces, **ok (closed singly connected)** | clean |
| boundary openness | (6.7e-16, -1.2e-15, 2.7e-15) **OK** | clean |
| face pyramids | **OK**, 0 incorrectly oriented | clean |
| **max skewness (GATE 4)** | **1.44043** | **CLEARS** |
| **max non-orthogonality (GATE 70)** | **80.3435**, 11,571 severely non-orthogonal faces | **FAILS** |

Concave cell check OK, face flatness OK, all face angles OK, face interpolation weight OK,
face volume ratio OK.

## THE VERDICT THE CRITERION FIXED IN ADVANCE

`PREDICTION_CRITERION.md` row 2: *"extrusion completes and the volume fails either hard
gate … → **FALSIFIED**"*, with the weight explicitly asymmetric — *"a failure here
contradicts the prediction outright … one counter-example falsifies it."*

**The volume fails the non-orthogonality hard gate. The prediction of M6C1 Addendum 1
§A1.3 — that a hyperbolic extrusion outward from a valid capped surface clears both hard
gates — is `FALSIFIED`. The outward/inward normal asymmetry is NOT sufficient to
guarantee gate clearance.** That is worth more than the mesh, exactly as Addendum 2 said.

**The criterion is honoured as written. It carves out nothing, and neither does this.**

## 🔴 WHERE THE FAILURE IS — AND IT IS NOT WHERE THREE TOPOLOGIES DIED

Every one of the 11,571 over-gate faces was located by face centroid from
`constant/polyMesh/sets/nonOrthoFaces`:

| | |
|---|---|
| distance from origin | **min 3.335 m**, median 4.565, max 6.181 |
| x (streamwise) | 2.777 → 5.961 — **3.5 to 7.5 root chords DOWNSTREAM** |
| z (spanwise; wing occupies 0 → 1.196) | **0.013 → 0.181** — a thin sheet hugging the root symmetry plane |
| **within r < 2.0 m of the body** | **0 of 11,571 — ZERO** |
| beyond r ≥ 2.0 m | 11,571 — **100 %** |

**NOT ONE over-gate face is on the body, on the tip cap, or in the boundary layer.** They
are a far-field sheet where the marching front converges near the symmetry plane, far
downstream. **The multi-patch cap — the artefact three topologies died trying to build —
produced no over-gate face at all.**

**This does not soften the verdict and is not offered as doing so.** It says the
falsification is real and its cause is the far-field march, not the cap. The next attempt
is a march/far-field parameter question, not a cap-topology question — and any such
attempt is a new pre-registration, not a re-reading of this one.

## COST

`time.vol2p3d` 9.51 s; `plot3dToFoam` and two `checkMesh` passes, serial and niced.
**≈ 6 core-min, derived $0.005 at $0.0513/core-h — DERIVED, NOT MEASURED.**

## 🔴 A DEFECT IN THE CONVERSION TOOL, FOUND BY ITS OWN OUTPUT

`vol2plot3d.py:19-20` prints *"smallest |dx| along i over all blocks"* and reported
**0.000000e+00** — which reads as the A1.4 zero-length-edge hazard and is not.
`np.abs(np.diff(b, axis=0)).min()` minimises over the three COMPONENTS, not over edge
LENGTHS, so any patch lying in a plane of constant coordinate makes it read exactly zero.
**Demonstrated: a clean unit grid with every edge length 1.0 makes it print 0.000000e+00.**

**It reads zero unconditionally, so it can never distinguish a clean mesh from the defect
it appears to guard — a zero never shown able to be non-zero (rule 3).** It is a print,
not a gate, and nothing here rests on it; but it must not be cited by anything that does.

## 🔴 THE FREEZE IS NOT PROVABLE BY COMMIT, AND THAT LIMITS THIS VERDICT

**`PREDICTION_CRITERION.md` was never committed before the probe ran.** Nothing in this
directory was in `HEAD` until the commit that lands this file: the criterion, the probe
script, the log and the volume all arrive in one commit, **after** the outcome was known.

What exists instead is filesystem mtime: criterion **04:53:50**, `probe.py` **04:54:52**,
volume and `log.probe` **15:11:25** — the criterion predates the run by over ten hours,
and this lane read it before running `checkMesh`. **That is consistent with the claim and
it is not a freeze.** Rule 2's evidentiary content is the commit, and there was none.

**So this row is reported as a MEASURED FINDING whose criterion was fixed in advance by
mtime, NOT as a gate-frozen verdict.** The numbers stand on their artifacts regardless —
80.3435° against 70 is what `checkMesh` read — but whether the `FALSIFIED` label may be
banked against M6C1 §A2.3 is the supervisor's ruling, not this lane's. **A criterion that
cannot be proven frozen is exactly the thing this lab does not let itself grade against,
and pointing at my own is not optional.**
