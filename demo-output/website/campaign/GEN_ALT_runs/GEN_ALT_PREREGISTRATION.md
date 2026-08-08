# Entry 10 — alternative-generator arm for the pyHyp aspect-ratio pathology: pre-registration

Written 2026-08-08 by the Cases family supervisor, **before any mesh of this
arm is built**. Review entry 10 diagnostic, chief-approved (~20 core-min;
priority raised when the A3 vcoarse mesh made the pyHyp pathology
cross-geometry). Standing finding under test:
`dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md` — `genAirFoilMesh.py`'s
pyHyp hyperbolic extrusion lets **max cell aspect ratio worsen under
refinement** (coarse 4,032 cells: 97.87 → refined 14,720 cells: **167.50**,
×1.71, concentrated at the leading-edge nose band ×1.92; max
non-orthogonality also worsens 22.7° → 27.0°) because its smoothing
parameters are not scaled with resolution. Driver:
`GEN_ALT_runs/run_gen_alt.py` (committed with this file).

**CAPABILITY_STRATEGY §2 linkage, stated per the approval:** this arm is the
"alternative-generator matrix" half of the mesh-generation-science proof
("pyHyp pathology characterized + alternative-generator matrix") — the
characterization exists; this supplies the controlled comparison.

## The alternative generator and the matched pair

Generator: the lab's own analytic-NACA0012 **blockMesh C-grid**
(`sdk/workflows/transonic_airfoil.transonic_blockmesh_dict` — the F2/F5b
proven topology; "blockMesh C-grid per the TMR recipe" in entry 10's own
words). Two meshes at **exactly** the pyHyp pair's cell counts, applying the
**same user-facing refinement moves** pyHyp received (≈2× surface points, 2×
wall-normal layers, ½ first wall spacing):

| | pyHyp (measured, on the record) | blockMesh C-grid (this arm) |
| --- | --- | --- |
| coarse | 4,032 cells, yWall 4e-3 | ns=21, nw=21, ny=32 → 126×32 = **4,032 cells**, first_cell 4e-3 |
| refined | 14,720 cells, yWall 2e-3 | ns=38, nw=39, ny=64 → 230×64 = **14,720 cells**, first_cell 2e-3 |

Farfield 25 chords + 25 wake (module defaults). Both meshes get their birth
certificate at creation (`checkMesh` before anything else — the rule now).

## The question and the verdict rule, pre-declared

**Primary (entry 10's question): the TREND, not the level.** Measure max
aspect ratio, max non-orthogonality, max skewness on both alternative
meshes. The pathology under test is *refinement making the worst cell
worse*:

- **GENERATOR-OWNED** (the family unblocks): the alternative pair's max-AR
  refinement factor ≤ 1.0 (flat or improving) while pyHyp's measured ×1.71
  stands — the same refinement moves on a generator whose spacing is
  enforced by construction rather than by an unscaled smoothing PDE do not
  reproduce the pathology.
- **RECIPE/GEOMETRY-OWNED** (the finding generalizes beyond the tool): the
  alternative pair's max AR also worsens by a comparable factor (≥ 1.3) —
  then the LE-curvature-under-refinement mechanism is not pyHyp's alone and
  the generator finding must be re-scoped.
- Between 1.0 and 1.3: reported as measured, verdict PARTIAL, no unblock
  claimed.

**Stated to keep the verdict honest: the AR *level* is out of scope.** A
C-grid to 25 chords carries large far-field in-plane stretching (the 4G
analysis measured the NASA-distributed grids at 2.1e7 on exactly this
topology class, and showed it is real stretching, not a 2D artifact). The
alternative meshes' global max AR may exceed pyHyp's LEVEL without touching
the verdict — only the refinement FACTOR and, informationally, the near-wall
band (within 1 chord, the 4G convention) are compared.

**Secondary (usability smoke test):** one short solve on the REFINED
alternative mesh through the module's own proven harness
(`transonic_airfoil.build_case`, rhoSimpleFoam at the module's F2-class
conditions M 0.5 / alpha 1.25 / Re 6e6, 500 iterations — the measured
S9 envelope prices this at ~1–2 core-min). Success = runs without S1/S2
fatal and force coefficients finite and settling; this is a smoke test, not
a validation, and no credential or band claim follows.

## Predictions, put at risk

- **G1:** the blockMesh pair's max-AR refinement factor is ≤ 1.0 —
  refinement does not worsen the worst cell (structured grading halves all
  spacings together by construction) → verdict GENERATOR-OWNED.
- **G2:** the near-wall (≤1 chord) max AR of the alternative meshes is
  within a factor ~3 of pyHyp's same-band values (87.6-class, the 4G
  measurement) — i.e. comparable wall-region quality at matched counts.
- **G3:** the smoke solve completes its 500 iterations clean.
- **Named risk:** blockMesh grading interacts with the fixed E_LE/E_TE
  edge ratios so that halving first_cell at doubled ny changes the LE cell
  shape non-uniformly — if max AR worsens (>1.3), the honest verdict is
  RECIPE/GEOMETRY-OWNED as mapped above, and the generator finding's scope
  claim shrinks rather than the verdict bending.

## Budget

Meshing + checkMesh ≈ 0.3 core-min; smoke solve ≈ 1–2; **expected ≈ 2.5 of
the ~20 approved.** Serial, setsid-detached driver with records in
`GEN_ALT_runs/<mesh>/record.json`; watch handoff: driver process +
`GEN_ALT_runs/driver.log`. Solver logs carry the mechanical lever echo;
records carry `levers_verified_active`.

*Nothing below this line existed when the arm was launched.*
