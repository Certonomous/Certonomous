# CRM WING-ALONE — BUILD PARAMETERS, AND THE ONE THE FREEZE DOES NOT PIN

Registration: `verification/campaign/CRM_WINGALONE_PREREGISTRATION.md`, frozen `d2629d326`.

## Pinned by the registration (§4) — not a lane choice

| level | surface file | surface cells | `N` (nodes) | cell layers | volume cells |
|---|---|---|---|---|---|
| L1 | `A6_coarse.cgns` | 2,784 | 53 | 52 | 144,768 |
| L2 | `A6_surfMesh.cgns` | 11,136 | 105 | 104 | 1,158,144 |
| L3 | `ACT9_CRM_surfMesh.cgns` | 44,544 | 209 | 208 | 9,265,152 |

## `marchDist` — held IDENTICAL across all three levels

`marchDist = 25 * 3.758151 = 93.9537750` mesh-units, the `59dfc5232` probe value.
**A grid family must occupy the same domain at every level.** A marchDist that changed with
level would refine the domain rather than the grid, and the volume-cell ratio of 8.000000
would no longer describe an r = 2 family.

## 🔴 `s0` — A LANE DECISION, NOT A REGISTERED QUANTITY. STATED, NOT BURIED.

**The frozen document does not pin the first-layer spacing.** It is not a gate, threshold, cap
or label, so choosing it is not an amendment — but it changes the mesh, so it is recorded here
rather than left inside a script.

§4 states refinement is **in ALL THREE directions**, *"the extrusion refines normal to the
wall."* With `marchDist` fixed and `N` doubling, that sentence is honoured only if `s0` **halves**
at each level; holding `s0` fixed would leave the near-wall spacing unrefined and the family
would not be geometrically self-similar.

| level | `N` | **`s0` (mesh-units)** | normal-direction ratio to the next level |
|---|---|---|---|
| L1 | 53 | **4.0e-4** | 2.000000 |
| L2 | 105 | **2.0e-4** | 2.000000 |
| L3 | 209 | **1.0e-4** | — |

**L3's `s0` = 1.0e-4 is exactly the probe-proven value**, and L3's surface is exactly the
probe's surface (see `PROBE_SURFACE_CORRECTION.md`), so the finest level sits on the proven
configuration and the coarser levels are strictly easier marches (larger first cell, same
distance, fewer layers -> lower growth ratio).

**`s0` is a mesh-construction parameter here and carries NO `y+` claim.** No flow condition is
registered (§2); `y+` belongs to the §10A successor.

## All other pyHyp options: IDENTICAL to the `59dfc5232` probe, unchanged

`ps0 -1.0, pGridRatio 1.1, cMax 5.0, epsE 1.0, epsI 2.0, theta 3.0, volCoef 0.16,
volBlend 0.0005, volSmoothIter 30, kspRelTol 1e-4, kspMaxIts 50, kspSubspaceSize 50,
unattachedEdgesAreSymmetry True, outerFaceBC farfield, autoConnect True, families wall`

## Conversion — NO SCALING APPLIED

`plot3dToFoam` is run at scale 1, leaving the mesh in native mesh-units. §5.3 records that the
quality gates G-M1..G-M3 are **scale-invariant**, so scaling cannot change a single graded
number, and leaving the coordinates untouched preserves the bit-for-bit nesting of §3.1.
The §8 rule-5 unit assertion is discharged by measurement in `scaling_assert.py`, not by a
conversion flag.
