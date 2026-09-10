# VMFL072 IS NOT A 3D DEMO CASE — evidence, and why a reasonable survey said otherwise

Written 2026-09-10 by the ansys-verification supervisor, because a lab-wide survey
classified the VMFL072 liquid-film family as this territory's 3D family and a policy
decision (no budget gates for 3D cases still to run) was about to rest on it.

## The measurement

Instantiated `blockMeshDict` at the FINEST level, read from the run directory rather than
from the template:

    L3:  hex (0 1 2 3 4 5 6 7) (256 64 1) simpleGrading (1 1 1)

**One cell in z.** The family instantiates 64x16x1, 128x32x1, 256x64x1. There is no
third-dimension structure, so there is nothing to film in z: rendered, it is a flat picture.

## Why the disagreement is reasonable, and this is the useful part

The usual mesh test for two-dimensionality asks whether the case carries `empty` boundary
patches. **VMFL072 does not.** Its L3 boundary file holds 3 `patch` and 2 `wall` entries and
**zero `empty`**. On that test the case classifies as 3D, and the domain description
(500 x 100 x 100 mm) agrees.

So both readings are defensible on their own evidence:

| test | verdict | why |
|---|---|---|
| `empty` patches present? | **3D** | none present, and the domain is 500x100x100 mm |
| instantiated cell counts | **not 3D in any useful sense** | z has ONE cell at every level |

Numerically the absence of `empty` means OpenFOAM solves all three components on a
single-cell-thick slab — so calling it "2D" flatly is also imprecise. **The accurate
statement is: three-component solve, ZERO z-resolution.**

**For the question actually asked — can this be shot as a hard 3D demo — the answer is no,
and the cell counts are what decide it.** A one-cell slab has no depth to show.

## Consequence for the no-budget-gate ruling

The ruling as relayed exempts 3D cases still to run from budget gates. On this evidence
**VMFL072 is not the 3D case that ruling is for**, so it should keep its registered caps
(L1 1.5 / L2 9 / L3 65 / B2 100 / C1 9 = 184.5 core-min) unless the owner says otherwise
knowing the above. Two further facts bear on it:

- **VMFL072-R3 has already been graded `NOT A RESULT`** (2026-09-10T16:44:43Z, refused at
  C-01 on L3's `rc = 136` SIGFPE), so it is not a case "still to run" in its present form.
- It never approached its caps: **37.69 core-min actual against 184.5 registered (0.204)**,
  and L3 died at **2.77 of its 65 core-min**. A budget gate was never what constrained it.

**This territory has no case that can be shot as a hard 3D demo.** The Ansys Fluid Dynamics
Verification Manual is built from analytically-checkable 2D and axisymmetric benchmarks, so
that is a property of the source material, not a gap in the work. The 3D demos have to come
from another team's cases.
