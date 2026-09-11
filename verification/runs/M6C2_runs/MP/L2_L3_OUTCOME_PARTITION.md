# M6C2 ROUTE (c) — L2 AND L3. **AN OUTCOME PARTITION, NOT A LIST OF EXPECTED CASES.**

Committed **before either extrusion is built.** Condition, checkable: `MP/L2/` and `MP/L3/`
do not exist at this commit.

**WHY A PARTITION.** My `L1_PREDICTION.md` named three anticipated cases and the case that
occurred — clears non-orthogonality, fails skewness — **fell in the gap between them**.
§A2.3's table decided the same measurement instantly because it **partitions** the outcome
space (clears both / fails either / never completes) instead of enumerating points in it.
**Every possible measurement below lands in exactly one row. A table that has to be
reinterpreted afterwards does none of the work it was written for.**

## THE MARCH FAMILY — A REGISTERED CHOICE, BECAUSE NONE WAS EVER REGISTERED

No march family exists in `M6C1_PREREGISTRATION.md` or anywhere in this campaign. **I am
choosing one and registering it rather than inheriting L1's numbers by default.** The
surface family is exactly ×1.5, so the volume family refines at ×1.5 in the marching
direction too, and the physical domain is held fixed:

| level | N | s0 (m) | marchDist (m) |
|---|---:|---:|---:|
| L1 (done) | 33 | 2.4271e-04 | 12.0 |
| L2 | 49 | 1.61807e-04 | 12.0 |
| L3 | 73 | 1.07871e-04 | 12.0 |

`marchDist` is **constant** — a refinement family whose domain changes is not a refinement
family. N is ×1.5 rounded; s0 is ÷1.5 so near-wall resolution refines with everything else.

**🔴 THE CONFOUND, STATED BEFORE THE RUN AND NOT AFTER.** Because all three directions
refine together, **a skewness trend below is a property of the FAMILY, not of surface
refinement alone** — surface density, marching count and first-cell height all move at
once. **No row below may be read as "the surface refinement did it."** Isolating that would
need a one-variable-at-a-time family, which is a different and unregistered experiment.

## ROW 0 — THE NON-COMPLETION GAP, CLOSED FIRST

**If either extrusion does not complete** — no CGNS written, or `plot3dToFoam`/`checkMesh`
cannot read what was written — **that level is `NOT A RESULT` and the partition below is NOT
READ AT ALL.** rc is not the verdict at any level; the `checkMesh` report text is read.
This is the row the probe's criterion needed and my L1 table omitted.

## THE PARTITION — TWO EXHAUSTIVE AXES, CROSSED

`S1 = 4.90021` (L1 max skewness, measured, committed at `9572e4f42`). `S2`, `S3` are max
skewness at L2, L3. Gate 4, inherited from `MESH_STANDARD` §3.

**AXIS A — the gate.** Mutually exclusive and exhaustive over (S2, S3):
- **A1**: `S2 ≤ 4` **and** `S3 ≤ 4`
- **A2**: exactly one of `S2`, `S3` is `≤ 4`
- **A3**: `S2 > 4` **and** `S3 > 4`

**AXIS B — the trend.** Numeric, with the hold band fixed **now** at `H = 0.10` skewness
units (2.5 % of the gate). Mutually exclusive and exhaustive over the reals:
- **B1 GROWS**: `S3 − S1 > +0.10`
- **B2 HOLDS**: `|S3 − S1| ≤ 0.10`
- **B3 SHRINKS**: `S3 − S1 < −0.10`

**Every (S2, S3) in ℝ² falls in exactly one A and exactly one B. Nine cells, no gap.**

| cell | reading |
|---|---|
| **A3·B1** | **The tip-TE corner defect WORSENS under refinement — topology 1's class exactly.** The crown's blunt-trailing-edge corner is a genuine topology defect and **route (c) is dead as a gate route.** A route-kill, and the most valuable outcome here. |
| **A3·B2** | **A fixed geometric corner defect, refinement-invariant.** Not curable by refining; curable only by local treatment of the TE point distribution at the crown. Route (c) survives as a *geometry* problem, not a topology one. |
| **A3·B3** | Converging toward the gate but not through it. **No `PASS` may be spoken and no L4 may be inferred** — an L4 is a new pre-registration, not an extrapolation. |
| **A2·B1 / A2·B2 / A2·B3** | **Split family.** Report which level clears and which does not, with both numbers; **no family verdict is available** and none will be invented. |
| **A1·B1 / A1·B2 / A1·B3** | L2 and L3 clear while **L1 fails** — so the family still does not clear at **every** level and **M6 stays `BLOCKED`**; the finding is that **L1 is the outlier**, which is the opposite of topology 1 and must be investigated, not celebrated. |

**AXIS C — non-orthogonality, reported alongside and separately.** L1 cleared at 66.4228
with **zero** over-gate faces. Exhaustive:
- **C1**: `N2 ≤ 70` and `N3 ≤ 70` — the L1 clearance holds across the family.
- **C2**: otherwise — **new information**, and it would mean the far-field mechanism the
  probe exhibited returns at finer marching.

## DIAGNOSTICS — REPORTED, NEVER GATED

Skew-face **count** and **location** at each level, by centroid from `sets/skewFaces` via
`MP/locate_over_gate_faces.py`. At L1 it was **exactly 2 faces at x = 1.1400, y = 1.1963
(the semispan, i.e. the crown plane), z = ±0.0003.** Whether the count and the location
stay put is informative and **is not part of any row above.**

## COST — REGISTERED BEFORE THE RUN, AND HONESTLY RE-SCALED

L1's registered estimate was 15.4 core-min; it actually cost **17.47** (`EXTRUDE_WALL_S
1048.43`, 1 rank). **Ratio actual/predicted = 1.134**, so Addendum 4's L2/L3 estimates are
scaled by it rather than re-quoted:

| item | core-min |
|---|---:|
| L2 extrusion (39 × 1.134) | 44 |
| L3 extrusion (77 × 1.134) | 87 |
| conversion + `checkMesh` + localisation, both levels | 9 |
| **this rung** | **140** |

**≈ 45 core-min already spent on this route, so ≈ 185 of the 300 core-min cap registered in
M6C1 Addendum 4 §A4.4. Derived $0.120 at $0.0513/core-h — DERIVED, NOT MEASURED.**
**Overrun stops the rung; it does not get a new budget.**

**This file changes no gate, threshold, cap, band or label.** M6C1 stays `BLOCKED` and
§A2.3 is already applied by the supervisor on L1; nothing here reopens it.
