# W3 — valid single-knob ladders for the two wings: pre-registration

**Written 2026-08-02 05:46 UTC, after meshing and before any solver was
launched.** All eight meshes exist and their cell counts are stated below;
**no drag coefficient has been computed on any of them.** Meshing produces a
cell count, not a force, so fixing the refinement ratios now is experiment
design, not tuning.

Items: `agp-e71b0542e6f9` (NACA 0012 finite wing) and `agp-64393439352d`
(NACA 4412 finite wing), each "Add a fourth refinement rung to the … grid
ladder", `est_core_min` 20.0 each, approved 2026-07-31T22:18:09Z.

---

## 1. Why this is not what the items asked for, and why it is what they need

`W3_LADDER_RECIPE_AUDIT.md` (commit cb7025c6) establishes from each rung's own
dictionaries that the stored three-rung ladders on both these wings are **two
mesh recipes with no knob moved twice**: coarse → medium refines the
background blockMesh at fixed near-body levels, medium → production refines
the near-body levels with the background blockMesh identical. A background
change is a uniform h refinement; a level change is not. **Adding a fourth
rung to that sequence returns a fourth number to fit across a step that is not
a refinement.**

So instead: **two, and here three, further rungs above the production mesh at
the production recipe, varying only the background blockMesh division triple.**
That makes a genuine four-rung single-knob family, the construction R4 proved
on the Ahmed 25°.

**Four rungs, not three, and the reason is on the record before the fact.** A
three-rung ladder can only say monotone or not. The fourth rung is what
revealed the turn on the Ahmed 25° under R4, and again on the B-52 tonight
under `agp-880b4f92bdc5` — both of this lab's genuine single-knob families
turned, and both turned at a rung a three-rung ladder would not have had.
Buying the fourth rung up front is cheaper than discovering it is needed.

## 2. The meshes

Recipe held fixed at each body's production recipe — `refinementSurfaces body
{ level (3 4) }`, eMesh feature level 3, `nearBody` region level 2, kOmegaSST,
magUInf 15, `residualControl` 1e-4 on p, U, k and omega — copied verbatim from
that body's own production case (`study-naca0012_wing-1021cb`,
`study-naca4412_wing-1af072`), STL and `transportProperties` included. **Only
the background blockMesh division triple differs between rungs.**

### NACA 0012 finite wing

| rung | divisions | cells | h-ratio | max non-orth | max skew | mesh |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | (33 60 20) | **140 545** | — | 40.55 | 1.93 | OK |
| r2 | (43 78 26) | **224 431** | 1.16884 | 39.46 | 2.08 | OK |
| r3 | (54 98 33) | **358 430** | 1.16889 | 44.04 | 2.01 | OK |
| r4 | (64 116 39) | **525 692** | 1.13617 | 36.31 | 1.98 | OK |

**Widest ratio mismatch 2.88%**, against the ≤3% this lab's constant-ratio
work holds itself to and against the existing ladder's own 5.8% (1.3518 and
1.2780). r21 and r32 agree to 0.004%.

### NACA 4412 finite wing

| rung | divisions | cells | h-ratio | max non-orth | max skew | mesh |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | (33 60 20) | **137 569** | — | 45.79 | 1.88 | OK |
| r2 | (42 77 26) | **213 918** | 1.15853 | 42.50 | 1.49 | OK |
| r3 | (54 98 33) | **340 996** | 1.16816 | 44.37 | 1.90 | OK |
| r4 | (64 116 39) | **518 748** | 1.15010 | 43.65 | 3.16 | OK |

**Widest ratio mismatch 1.57%.** Against the existing ladder's 7.1% (1.3554
and 1.2658).

Every mesh passes checkMesh. Non-orthogonality does not degrade with
refinement on either body (0012: 40.5, 39.5, 44.0, 36.3; 4412: 45.8, 42.5,
44.4, 43.7, all far below the 70° gate), so a quality cliff will not be
available as an explanation for whatever these ladders report. That is worth
stating because `agp-f493fff26990` recorded non-orthogonality **rising**
58.37 → 64.99 → 74.96 through the OLD 4412 ladder, past its own 70° gate.
**The old ladder's quality degradation was a property of raising the
refinement level, not of refining. Holding the level fixed removes it.** That
is an independent confirmation of the audit, and it is on the record before
any force is computed.

### The re-meshes, all of them, and why

No Cd existed on any mesh when any of these decisions was made.

| body | rung | discarded | reason | kept |
| --- | --- | --- | --- | --- |
| 0012 | r2 | (42 77 26) → **snappyHexMesh FATAL** | see §3 | (43 78 26), 224 431 |
| 0012 | r2 | (42 77 26) → 215 668 after the §3 fix | r32/r21 mismatch 2.71% | (43 78 26), 224 431, mismatch 0.004% |
| 0012 | r4 | (69 125 42) → 660 132 | r43 mismatch 5.0% | (64 116 39), 525 692, 2.88% |
| 4412 | r4 | (69 125 42) → 678 882 | r43 mismatch 8.0% | (64 116 39), 518 748, 1.57% |

## 3. A defect found while meshing, and the one deviation it forced

The NACA 0012's r2 mesh **failed outright**:

```
--> FOAM FATAL ERROR: (openfoam-2606)
Point (6.5 0 0) is not inside the mesh or on a face or edge.
Bounding box of the mesh:(-3 -9 -3) (7 9 3)
```

The point is well inside that box. The NACA 0012's generated domain is
**exactly symmetric** — y ∈ [−9, 9], z ∈ [−3, 3] — and `external_aero._snappy`
sets `locationInMesh` by moving the geometry centre downstream along the
streamwise axis only, leaving the other two components at the centre. So the
seed point sits **exactly on both symmetry planes**, and whether
`refinementParameters::findCells` finds a cell there depends on the
floating-point parity of the division counts. r1, r3 and r4 survived it; r2
did not. **The generated case is one division count away from a hard mesh
failure on any body whose domain is exactly symmetric.** The NACA 4412 is
immune only by accident: its STL is very slightly asymmetric, so its domain
runs z ∈ [−2.96598, 3.03582] and its seed lands at z = 0.0349165, off-plane.

Filed separately. The workaround here is to move the seed off both planes,
`locationInMesh (6.5 0 0)` → `(6.5 0.1 0.1)`, applied to **all four** NACA
0012 rungs so the family stays internally identical.

**The workaround is not free, and its cost is measured rather than asserted.**
Re-meshing r1 and r3 with the nudge and nothing else changed:

| rung | divisions | cells, seed (6.5 0 0) | cells, seed (6.5 0.1 0.1) | difference |
| --- | --- | --- | --- | --- |
| r1 | (33 60 20) | 140 580 | **140 545** | −35 cells, **0.025%** |
| r3 | (54 98 33) | 358 486 | **358 430** | −56 cells, **0.016%** |

140 580 is the stored production rung's cell count exactly, so **r1 at the
unnudged seed reproduces the production mesh to the cell**, which is the check
that the recipe was rebuilt correctly; and the nudged family sits 0.025% off
it, which is what the seed move costs. The NACA 4412's r1 needs no nudge and
reproduces **137 569 exactly**, its stored production count.

## 4. Ranks

**4 MPI ranks on every rung, scotch, identical across all eight**, including
the r1 rungs, which are re-solved rather than reused. Decomposition perturbs a
steady SIMPLE solve at the linear-solver tolerance level and the ladder's
signal is the difference between rungs, so a rung-varying rank count would put
a decomposition artefact into the increments. The stored production numbers
came from **16** ranks (`study-naca0012_wing-1021cb/system/decomposeParDict`),
which is 8 786 cells per rank — inside the regime where this lab measured 4
ranks costing 17.4% MORE core-minutes than 1 at 5 600 cells per rank. They are
not reused for that reason as well as for the recipe one.

**Cells per rank, stated because the rank count was chosen from it:**

| rung | 0012 | 4412 |
| --- | --- | --- |
| r1 | 35 136 | 34 392 |
| r2 | 56 108 | 53 480 |
| r3 | 89 608 | 85 249 |
| r4 | 131 423 | 129 687 |

All eight are 6× to 23× above the 5 600 cells-per-rank floor where four ranks
stopped paying, so four ranks is priced from the load, not assumed.

## 5. Cost, estimated before the fact

Meshing, measured: **14 core-minutes** across all attempts including the four
discarded meshes, single core each, concurrent.

Solving, estimated: the NACA 0012 production rung converged on
`residualControl` in 153 iterations at `ExecutionTime = 21.13 s` on 16 ranks
(`mission-output/geometry-study/study-naca0012_wing/log.simpleFoam`). Scaling
by cells and allowing iteration counts to grow with refinement as R4 measured
them growing (158, 212, 220, 623), the eight rungs are estimated at
**100–130 core-minutes total at 4 ranks**, against `est_core_min` 20.0 + 20.0
= 40.0 for the two items. **That is over the estimate and it is over on
purpose**: the items were priced for one extra rung on an existing ladder, and
what is being run is two four-rung ladders that do not yet exist. Measured
cost is reported whatever it turns out to be. Per the B-52 lesson tonight,
cost is taken from **ExecutionTime**, not wall clock, because these run
concurrently and wall clock will read the contention.

## 6. Gates, fixed now

**G1 — the experiment worked.** Widest h-ratio mismatch within 3% on each
body. *Already met at 2.88% (0012) and 1.57% (4412), §2. Recorded before
solving so it cannot be claimed after.*

**G2 — the increments are signal.** Each rung's Cd 2σ over its own final-20%
window must be below 10% of the smallest ladder increment on that body. If it
is not, the increments are iterative noise and nothing below is interpretable.
These cases carry `residualControl` at 1e-4 and the production rungs print
"SIMPLE solution converged", unlike the B-52, so this is expected to hold —
and if a rung fails to converge within `endTime` 300 it will be reported as
refused evidence, not quietly stored.

**G3 — the question.** Fit each family with `uq.eca_hoekstra_band(dim=3)`. The
fit takes the finest three, so it reads r2/r3/r4 on each body.

**G4 — falsifiable predictions, on the record before the solve.**

The old, invalid ladders report p = 3.173 (0012) and p = 10.467 (4412), both
outside the [0.5, 2.5] window, and the audit's claim is that those numbers are
artefacts of dividing a near-wall refinement by a farfield one. If that claim
is right, removing the mixed step should remove the absurdity.

* **P1: neither valid family returns an observed order above 2.5.** The two
  ways this can come out are an order inside the window, or no order at all
  because the family is non-monotone. Either scores P1 TRUE. **An observed
  order above 2.5 on a single-knob family scores P1 FALSE and the audit's
  central claim is wrong.**
* **P2: at least one of the two families comes back non-monotone or
  non-asymptotic.** Both of this lab's existing single-knob families turned.
  Predicting that both wings converge cleanly would be predicting against
  every case this lab has measured.
* **P3, the sharp one: the NACA 4412 moves further than the NACA 0012.** Its
  old level-step moved Cd 5.5× more than its background step, against 1.6× for
  the 0012, so the 4412 is the body whose drag is most sensitive to near-wall
  resolution. **Predicted: the 4412's total Cd change across its valid family
  exceeds the 0012's, in relative terms.**

**G5 — what will not be claimed.** No ladder is called conclusive or
asymptotic on the strength of arriving; `uq.reportable_band` and
`uq.guards_holding` are read, never `band_abs`. No credentials-wall row is
rebuilt from these numbers in this pass — the NACA 0012's published envelope
is the subject of the open ruling
`w3-a-declined-ladder-still-publishes-an-envelope`, and a number that is about
to be ruled on should move once, by the ruling, not twice.

*Nothing below this line existed when the solvers were launched.*
