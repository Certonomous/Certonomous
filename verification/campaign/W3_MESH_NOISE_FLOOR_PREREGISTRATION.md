# W3 — where the mesh-generation noise floor bites: pre-registration

**Written 2026-08-02 06:06 UTC, before any replicate mesh below was built and
before any of them was solved.** The two replicates that already exist — the
r4b controls on both wings — are stated here as the motivation, and nothing
below rests on them being repeated.

Follows `w3-a-ladder-refined-below-its-own-mesh-noise` (proposed tonight) and
`W3_WING_VALID_FAMILY_RESULTS.md` §3.

---

## 1. The question

Two independently generated snappyHexMesh meshes at the same nominal
resolution give different drag. At 525 692 vs 534 106 cells on the NACA 0012
the difference is 1.799 × 10⁻⁴, and at 518 748 vs 561 528 on the NACA 4412 it
is 3.251 × 10⁻³. Both exceed the refinement increment at that rung. **What is
not known is whether that scatter is a property of fine meshes or a property
of this mesh generator at every resolution.**

Those are different worlds. If the scatter is roughly constant in absolute Cd,
then every ladder in this lab has a fixed floor and the only question is how
far above it a rung sits — and the coarse rungs, whose increments are large,
are fine. If the scatter grows with cell count, the lab has a hard ceiling on
refinement and finer is actively worse.

## 2. What is being run

For each of the two wings, one **replicate mesh at each of r1, r2 and r3** —
the same nominal resolution, reached by a different background division triple
— solved identically to its twin at 4 MPI ranks with `residualControl` 1e-4.

| rung | original divisions | replicate divisions |
| --- | --- | --- |
| r1 | (33 60 20) | (34 59 21) |
| r2 | 0012 (43 78 26) / 4412 (42 77 26) | 0012 (44 77 27) / 4412 (43 76 27) |
| r3 | (54 98 33) | (55 97 34) |
| r4 | (64 116 39) | (65 115 40) — **already run**, §1 |

Every other file in each case is copied byte-for-byte from its twin: the same
STL, the same `snappyHexMeshDict`, `fvSchemes`, `fvSolution`, `controlDict`,
`transportProperties`, `turbulenceProperties`, and the same `0.orig`. The
replicate divisions perturb the triple by one cell in each direction, up-down-
up, so the nominal resolution is held and the generated mesh is different.

Six solves. Both wings converge on `residualControl` in 117–156 iterations at
these sizes, so this is cheap: estimated **20–25 core-minutes at 4 ranks**,
priced from the eight rungs measured tonight at 22.44 and 16.98 core-minutes
per four-rung family.

## 3. Predictions, on the record before any of the six is meshed

**P1 — the scatter is not constant in absolute Cd. It grows with cell count.**
Reasoning stated so it can be judged: snapping is where two meshes at the same
nominal resolution diverge, and the number of snapped surface cells grows with
refinement, so the number of independent small decisions that can go
differently grows too. **Predicted: on each wing, |Cd(r4b) − Cd(r4)| is the
largest of the four scatters, and |Cd(r1b) − Cd(r1)| the smallest.**

**P2 — the scatter at r1 and r2 is well below those rungs' increments.** The
0012's r1→r2 increment is 1.646 × 10⁻³ and the 4412's is 1.173 × 10⁻³.
**Predicted: the r1 and r2 scatters are each below 20% of the increment
spanning them**, which is what it would take for the coarse half of each
ladder to be real. If this fails, the ladders were never measuring
discretization at any rung and the whole refinement programme on these bodies
needs rethinking rather than extending.

**P3 — the crossing point is between r3 and r4 on both bodies.** The 0012's
r2→r3 increment is 1.927 × 10⁻³ against a measured r4 scatter of
1.799 × 10⁻⁴, a factor of 10.7. **Predicted: the r3 scatter is below the
r2→r3 increment on both wings, so the floor crosses the signal between
358 430 and 525 692 cells on the 0012 and between 340 996 and 518 748 on the
4412.**

## 4. What will not be claimed

Six replicates on two bodies is a measurement of *this* generator on *these*
two geometries at four resolutions. It is not a law, it will not be stated as
one, and n = 2 per resolution is a scatter estimate with no error bar of its
own — the honest form is a range, not a fitted curve. Nothing here refits any
study's `numerical` block or rebuilds any wall row.

*Nothing below this line existed when the meshes were built.*
