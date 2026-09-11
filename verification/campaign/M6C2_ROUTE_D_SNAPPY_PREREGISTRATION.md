# M6C2 ROUTE (d) — snappyHexMesh MESH-ADMISSION PRE-REGISTRATION

**Status: FROZEN BEFORE FIRST COMPUTE.** For a mesh-admission gate the **mesh build IS
first compute** (cfd-supervisor ruling, 2026-09-11). No `snappyHexMesh`, `blockMesh` or
`surfaceFeatureExtract` has been run for route (d) at the time this is committed. The
run directory named in §8 **does not exist**; that is the condition, and it is checked
by `test -d` in the launcher before anything starts.

Everything below — gate, threshold, cap, label — is fixed at this commit. After first
compute it changes only by dated addendum that cannot alter a gate, threshold, cap or
label.

---

## 1. THE QUESTION, IN ONE SENTENCE

**Can snappyHexMesh produce a MESH_STANDARD-admissible volume mesh around the proven
ONERA M6 body, when pyHyp hyperbolic extrusion cannot?**

## 2. WHY THIS IS A MECHANISM CHANGE AND NOT A PARAMETER CHANGE

Route (c) is **TERMINATED** (`b0cb2f0c6`): L2 gave max non-orthogonality **74.6431**
against the gate of 70, with **1,019 severely non-orthogonal faces where L1 had ZERO**,
**99.41 % of them beyond r ≥ 2.0 m**. The defect is in the **far field** and is
**intrinsic to pyHyp hyperbolic extrusion at `marchDist` = 12 on a wing O-mesh** — it has
been produced on **two different bodies**. Another march at another `marchDist` is the
same mechanism with a different number, and three topologies plus two bodies have already
paid for that lesson.

**snappyHexMesh is admissible as a successor precisely because it DOES NOT MARCH.** It
refines and snaps a Cartesian background block; there is no hyperbolic extrusion and
therefore no far-field marching mechanism to inherit. **The far field is where route (c)
failed, and under route (d) the far field is undistorted background hexahedra.**

Sanaa authorised the latitude on 2026-09-10 20:57Z, verbatim: *the C-mesh,
snappyHexMesh, or whatever it needs.*

## 3. WHAT IS INHERITED AND IS **NOT** RE-DERIVED HERE

- **The body.** Three levels matched to the **AR-138 source table** at
  **1.887e-15 / 2.442e-15 / 1.915e-15**, with four planted controls including one that
  plants A3's exact failure mode and refuses it —
  `verification/runs/M6C2_runs/surface/BODY_PROOF_MP.txt`.
- **The triangulation, proven not to have moved that body.**
  `verification/runs/M6C2_runs/surface/plot3d_to_stl.py` converted the 9-block structured
  PLOT3D surface to multi-solid ASCII STL at
  **max |STL vertex − PLOT3D point| = 0.000e+00 at all three levels**, so the AR-138
  proof transfers unchanged:

  | level | triangles | file |
  |---|---:|---|
  | L1 | 28,288 | `verification/runs/M6C2_runs/surface/m6_mp_L1.stl` |
  | L2 | 63,648 | `verification/runs/M6C2_runs/surface/m6_mp_L2.stl` |
  | L3 | 143,208 | `verification/runs/M6C2_runs/surface/m6_mp_L3.stl` |

  Nine named solids per file — `wing_upper`, `wing_base`, `wing_lower`, `wing_nose`,
  `cap_upper`, `cap_base`, `cap_lower`, `cap_nose`, `crown` — so refinement is per
  region.

**The surface closure state, stated exactly, because it is the number a later reader is
most likely to turn into a defect:** the STL carries **200 / 300 / 450 open edges at L1 /
L2 / L3, and every one of them lies on the root plane `|y| ≤ 1e-9`.** That plane is the
**symmetry plane**; it is **legitimately open**, it is the same exception
`make_level.py` grants, and it is what OpenFOAM's own half-body meshing relies on. **Open
edges away from the symmetry plane: 0. Non-manifold edges (shared by > 2 triangles): 0.**

**THOSE ZEROS ARE STATED AT THE RESOLUTIONS THEY WERE MEASURED AT — 28,288, 63,648 and
143,208 triangles — AND AT NO OTHER.** Route (c) died because a zero at L1 became 1,019
at L2. A zero here is a statement about these three triangulations and about nothing
finer. **And each zero is planted, not assumed:** the manifoldness reader is gated by
`make_level.py`'s own 1 mm crown displacement and must report MORE open edges or the
converter refuses — it fired at every level, **200→600, 300→900, 450→1350**.

## 4. THE GATE — INHERITED, UN-FITTABLE, AND NOT NEGOTIATED HERE

`docs/standards/MESH_STANDARD.md` §3, applied to `checkMesh` on the built mesh:

| # | quantity | gate | note |
|---|---|---|---|
| §3.1 | max non-orthogonality | **≤ 70°** hard | warning band 65–70 reported, not fatal |
| §3.2 | max skewness | **≤ 4** hard | **boundary faces INCLUDED** |
| §3.3 | max aspect ratio | **advisory at 1000** | **NEVER a lone rejection**; above 1000 requires an alignment justification on the record, and is a flag only when joined by non-orth > 60 or skew > 2 |

Additionally fatal, from `checkMesh` itself: **any negative-volume cell**, **any illegal
face**, or a **non-closed mesh**.

**These thresholds are inherited from the standard. This document does not set them and
may not move them.**

## 5. THE LABELS, FIXED NOW

- **`PASS`** — mesh built, `checkMesh` rc = 0, §3.1 ≤ 70 AND §3.2 ≤ 4 AND no negative
  volumes AND no illegal faces. §3.3 reported beside it, never deciding it alone.
- **`GATE FAIL`** — mesh built but §3.1 or §3.2 over gate, or negative volumes, or
  illegal faces. **The value, the count of offending faces, and WHERE they are (radius
  from the body) are printed beside it** — route (c) was killed by the *location* of its
  defect, not its magnitude, and a successor that fails must fail legibly enough to be
  killed the same way.
- **`NOT A RESULT`** — the build did not complete, or the reader failed its plant (§7).
- **`BLOCKED`** — snappy cannot be run at all (tooling absent).

**No label here is conditional on the mesh being "good enough to proceed". The gate is
the gate.**

## 6. THE COMPLETION RULE FOR A MESH BUILD

A route (d) build is **done** only if ALL hold: `rc = 0` captured **inside** the wrapper
(never around a `setsid` line, which returns 0 for every outcome); `blockMesh`,
`surfaceFeatureExtract` and `snappyHexMesh` each produced an `End` line; a
`constant/polyMesh` exists containing `points faces owner neighbour boundary`; and
`checkMesh` ran to completion on that mesh and wrote its own log. **A build failing any
clause is `NOT A RESULT`, not a degraded PASS.**

## 7. THE PLANT — THE READER MUST BE SHOWN ABLE TO SEE A NON-ZERO

The `checkMesh` reader that reports "0 severely non-orthogonal faces" is **refused**
unless it has been shown able to report a non-zero. Before grading, the reader is run
against a **known-bad control mesh** and must report the defect it is meant to catch.
**A zero from a reader not shown able to see a non-zero is not evidence** (rule 3), and
this is the exact trap that made route (c)'s L1 zero worthless.

**Nothing in §7 may be skipped on the grounds that the mesh "obviously" passed.**

## 8. THE RUN DIRECTORY, AND THE CONDITION CHECKED BEFORE COMPUTE

`verification/runs/M6C2_runs/ROUTE_D/L1/`

**At this commit that directory DOES NOT EXIST.** The launcher runs `test -d` on it and
refuses to start if it does — a guard against grading a tree that a previous attempt
already wrote into.

## 9. SCOPE — ONE LEVEL, DELIBERATELY

Route (d) registers **ONE level (L1)** and asks only the admission question. **It does
not register a Roache triple and no grid-convergence claim may be made from it.** A
triple needs three meshes from one family and costs roughly an order of magnitude more;
committing to that before knowing whether snappy clears §3.1 on this body at all would be
spending the compute before the question is answered. **If L1 is `GATE FAIL`, route (d)
is answered and no L2 is built** — the same discipline that stopped route (c) at L2
rather than building an L3 to confirm what was already known.

## 10. COMPUTE (rule 12) — COSTED BEFORE IT RUNS

Unit is **core-minutes = wall-s × ranks ÷ 60**. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5), so **every dollar figure is derived, not measured.**

**Anchor, measured on this box and not assumed:** the MRF R2 fine `snappyHexMesh` build
is recorded at **10.6 core-min for 2,418,780 cells** (`MRF_R2_PREREGISTRATION.md` §6.1,
"fine build **measured 10.6 core-min**"), i.e. **~4.4e-06 core-min per cell**.

| stage | ranks | est. wall s | **est. core-min** |
|---|---:|---:|---:|
| `blockMesh` (background ~135 k cells) | 1 | ~20 | **~0.3** |
| `surfaceFeatureExtract` (28,288 tri) | 1 | ~30 | **~0.5** |
| `snappyHexMesh` (target ~1.0 M cells) | 1 | ~600 | **~10.0** |
| `checkMesh` | 1 | ~60 | **~1.0** |
| **total** | | | **~11.8 core-min** |

**Derived ≈ \$0.010** at \$0.0513/core-h — **derived, not measured**.

**CAP: 60 core-min.** Beyond that the build **STOPS and is reported at the core-minutes
spent**; it does not get a new budget. The cap is ~5× the estimate because the anchor is a
different body and a different refinement depth, and an anchor from another case is a
weaker basis than one from this one — **stated as the reason for the margin rather than
hidden inside the estimate.**

**Contention is named separately and never absorbed into the ratio.** Today's measured
concurrency factor on this box is **wall/ExecutionTime = 2.188** (MRF R2 coarse, 4000.0 s
execution against 8753 s wall), against the 1.19 carried from R1. The estimate above is
**solver-intrinsic**; the actual will be compared against it with contention named as its
own term, per rule 12, in `docs/COST_CALIBRATION.md` at completion.

**Disk.** The build is held until the MRF R2 medium level lands, because free space
crossed the 25 GiB alert at 21:54Z and a snappy build competes for disk and cores with a
run 899 iterations from completing. **Free space is re-read immediately before launch and
the build does not start below 20 GiB.**

## 11. WHAT WOULD FALSIFY THE PREMISE

Route (d) rests on the claim that the defect is **marching**, not **the body**. It is
falsified if snappy's non-orthogonality also concentrates **in the far field at
r ≥ 2.0 m** — because the far field under route (d) is undistorted background hexahedra,
and a far-field defect there would mean the body, not the extrusion, is the cause, and
route (c)'s refutation would need revisiting. **`checkMesh` output is therefore binned by
radius from the body, exactly as route (c)'s was, so the two are comparable.**

---

*Frozen 2026-09-11. Submissions parked; nothing in this document is sent, filed or
registered outside this box.*
