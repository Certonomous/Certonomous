# CFD — DRAFT CLAUSE FOR `docs/standards/MESH_STANDARD.md`: a fixed ABSOLUTE tolerance on `checkMesh`'s printed wedge angle is unsafe at any refinement

**STATUS: DRAFT. NOT LANDED. NOT A STANDARD.** This file is a lane's draft for the cfd
supervisor's read. **`docs/standards/MESH_STANDARD.md` is NOT edited by this file and was
not edited by this lane.** That document is at **v1.7** (highest section version, §12,
2026-08-27; its header still reads `Version 1.2` by the deliberate convention recorded at
its §11 and §12). Landing this text requires rule 6's dated-amendment form — appended at
the foot, a version bump to **v1.8**, and the assertion `lines whose number changed above
this section: 0` — **which is the supervisor's act, not this lane's.**

**Nothing here is sent, filed, uploaded, posted or submitted (rule 7).**

Provenance of every number below: `verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md`
§4.1–§4.4, measured on F23's own retained meshes at
`verification/runs/F23_HP_WEDGE_runs/{coarse,medium,fine}/constant/polyMesh` under
`OPENFOAM=2606`, build `_481094f-20260618`, on this box.

---

## PROPOSED § 13 — THE `checkMesh` WEDGE ANGLE IS NOT A GEOMETRY READING, AND MUST NOT BE GATED ABSOLUTELY (v1.8, draft)

### 13.1 The occasion, measured

`F23_HP_WEDGE` graded **`NOT A RESULT`**. Its fine level never reached the solver because
the case's builder refused the built mesh on a **fixed absolute 1e-6 degree** tolerance
between `checkMesh`'s printed wedge angle and the registered half angle of 0.04°:

| level | wedge faces per patch | printed angle | deviation | vs the 1e-6 gate | `checkMesh` verdict |
|---|---|---|---|---|---|
| coarse | 131,072 | 0.0400002766821 | 2.766821e−07 | 0.28× | **`Mesh OK.`** |
| medium | 524,288 | 0.0400007984975 | 7.984975e−07 | **0.80×** | **`Mesh OK.`** |
| fine | 2,097,152 | 0.0400027202903 | 2.720290e−06 | **2.72× — REFUSED** | **`Mesh OK.`** |

**OpenFOAM's own checker passed all three meshes, fine included.** The lab's guard refused
a mesh that is correct. The medium level already sat at **80 % of its tolerance budget**,
so the ladder was one refinement level from refusal at registration time and nothing
computed that.

### 13.2 WHY — the printed angle carries a floor that GROWS WITH THE MESH

`wedgePolyPatch` stores `cosAngle_ = centreNormal_ & n_`, where `n_` is the **arithmetic
mean of the unit face normals of the patch and is never renormalised**, and `checkMesh`
prints `acos` of it. Summing N nearly-identical unit vectors accumulates floating-point
rounding, so |n̄| lands **below 1**; and because `d(acos)/dc = −1/sin(a)`, that deficit is
amplified by **1/sin(0.04°) = 1432** on its way to an angle:

    printed deviation  ≈  ( 1 − |n̄| ) / sin(a)        [radians]

**This was verified three ways, and one of them is a control that changes nothing else.**

1. **Reproduction.** An independent reimplementation of the OpenFOAM face-area-vector
   construction, the unnormalised mean and the snapped `centreNormal_`, run from
   `constant/polyMesh` alone, reproduced the printed value **to its last printed digit at
   all three levels** (0.04000027668213 / 0.04000079849752 / 0.04000272029028).
2. **The `math.fsum` control.** Replacing only the summation with exact accumulation —
   **same points, same faces, same geometry, nothing else touched** — drives
   `1 − |n̄|` from **3.371303e−12 / 9.729550e−12 / 3.314704e−11** to **exactly 0.0** at all
   three levels, and the reported angle to **0.03999999999967**. The deviation is
   arithmetic, not geometry.
3. **The prediction closes.** `(1 − |n̄|)/sin(a)` predicts **2.766834e−07 / 7.985058e−07 /
   2.720383e−06** against the printed **2.766821e−07 / 7.984975e−07 / 2.720290e−06** —
   three digits at every level.

**The growth law.** `1 − |n̄|` is bounded by `N·ε` for sequential summation
(ε = 2.220446049250313e−16); measured, `(1 − |n̄|)/(N·ε)` is **0.1158 / 0.0836 / 0.0712** —
a falling fraction of that bound. **The floor therefore grows approximately linearly in
the wedge-patch face count and inversely with sin(a).** A fixed absolute tolerance is
crossed at some level of any ladder; only the level is in question.

**The one hypothesis that is EXCLUDED, and it is the intuitive one.** Catastrophic
cancellation in the cells near the axis, where the azimuthal thickness collapses, is
**false here and was excluded by measurement, not by argument**: across coarse's 131,072
wedge faces there are **3 distinct `n_z` values and 10 distinct `n_x` values**, with
`Var(n_z) = 8.45e−32`; binned by radius decile the per-face deviation is **flat**, and the
innermost faces' normals are bit-identical to the outermost faces'. **A standard that told
a lane to look near the axis would send it to the wrong place.**

### 13.3 THE CLAUSE

**A mesh guard MUST NOT gate `checkMesh`'s printed wedge angle against a tolerance that is
fixed and absolute.** A guard on wedge geometry must take one of two forms, and a case
that gates wedge angle must say in its pre-registration which it took:

**(a) READ THE GEOMETRY DIRECTLY — preferred, and the sharp one.** Compute the angle for
**every face of every wedge patch** from `constant/polyMesh`, in a form that never
evaluates `acos` near 1 — `degrees(atan2(hypot(n_x, n_y), |n_z|))` against the
componentwise-snapped cardinal normal — and gate the **relative** deviation
`max |angle/HALF_ANGLE − 1|`. This quantity is a reading of the mesh: measured over F23's
three meshes it is **1.895413e−10 / 2.449031e−10 / 7.569059e−10**, ten orders below any
physically meaningful mis-build, and it grows only as an extreme value over more faces.

**(b) IF THE PRINTED ANGLE IS GATED AT ALL, its tolerance MUST carry the summation floor
explicitly**, as a term in the mesh's own face count:

    TOL(level) [deg] = HALF_ANGLE x TOL_REL(level)
                     + K x N_wedge_faces(level) x EPS_MACH / sin(HALF_ANGLE) x 180/pi

with `K ≥ 1` frozen at registration (`K = 1` is the worst-case sequential-summation bound
and sits 8.6–14× above what was measured). Applied to F23's ladder this gives tolerances
**2.874681e−06 / 9.674350e−06 / 3.824547e−05 deg** and budget occupancies
**0.096 / 0.083 / 0.071 — falling with refinement, where the fixed absolute tolerance's
occupancy rose 0.28 / 0.80 / 2.72.**

**In either form the relative tolerance MUST be derived per level, not inherited**, and
the standard's existing L-346 discipline is the derivation this clause requires: tie it to
a fraction of **that level's own predicted discretisation error**, with a registered
absolute floor so it cannot fall below what floating point can deliver.

**AND IT MUST STILL REFUSE A MIS-BUILT WEDGE — SHOWN, NOT ASSERTED.** Any guard landed
under this clause ships a **two-direction** control (rule 3, and L-396's mirror): a planted
mis-built wedge it MUST refuse, and a real correct mesh at the ladder's FINEST level it
MUST NOT. F23b's, driven on F23's real meshes, is the worked example — a plant at 3× the
tolerance refused at 3.000× (coarse) and 3.001× (fine), a gross ×1.10 plant refused at
8,228× and 140,013×, and the real unplanted fine mesh accepted at 0.001× of tolerance.
**A guard relaxed after a refusal, with no control showing it can still refuse, is a
rubber stamp and this clause does not authorise one.**

### 13.4 What this clause does NOT do

- It **sets no threshold** of its own. `TOL_REL`, `K` and the absolute floor are
  registered per case, at that case's freeze, from that case's own predicted error.
- It **does not amend §3's gates** (non-orthogonality 70°, skewness 4, aspect ratio
  advisory at 1000), §8, §9, §11 or §12, and it retires nothing.
- It **makes no claim about other OpenFOAM versions.** Every reading is `OPENFOAM=2606`,
  build `_481094f-20260618`, on this box.
- It **is not an upstream defect report and is not a defect claim against OpenFOAM.**
  `checkMesh` printed `Mesh OK.` and was right to; the printed angle is a diagnostic and
  the lab gated it as if it were a measurement. **The defect was ours.**
- It **names no other case.** See §S below.

---

## § S — WHAT A LAB-WIDE SWEEP WOULD HAVE TO LOOK FOR (for the chief to route; NOT commissioned here)

**This lane checked no case other than F23/F23b and makes no claim about any other.** The
supervisor is escalating the sweep to the chief because it crosses team boundaries —
`VMFL005` is the ansys team's case and F23's `blockMeshDict.template` descends from it.
**The exact predicate a sweep must apply:** a case is EXPOSED if it (1) builds a mesh
carrying at least one patch of `type wedge`, and (2) anywhere in its build, launch or
grading path compares a wedge angle **parsed from `checkMesh` output** — the
`Wedge <name> with angle <X> degrees` line — against a registered half angle using a
tolerance that is **absolute and does not scale with the wedge-patch face count**, whether
written as a literal (`> 1e-6`), as a named constant, or as a relative tolerance on a
quantity whose own floor grows (a relative test on the printed angle is exposed too,
because the floor grows while the angle does not). For each exposed case the sweep reports
three numbers per level and nothing else is needed to rule on it: the wedge-patch face
count `N`, the printed deviation, and its occupancy of that case's tolerance — with
`occupancy ≈ K·N·ε/(sin(a)·TOL)` giving the level at which it will cross. **Occupancy
RISING across a ladder is the signature; a case whose finest built level already exceeds
0.5 is one refinement from refusal.** Exposure is **latent** where the case's finest level
has already built successfully — it is armed by the next finer level, not realised — and
**realised** where a build has already refused. Cases using a wedge but never parsing the
printed angle are NOT exposed and should be reported as such, so the zero is evidence.
