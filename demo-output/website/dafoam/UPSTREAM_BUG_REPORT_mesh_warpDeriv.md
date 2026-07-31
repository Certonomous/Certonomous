# Bug report: `mesh.warpDeriv` disagrees with a finite difference of the actual warp it differentiates, by up to 207% and with the sign flipped, on two unrelated official tutorials

**Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been contacted, nothing
has been posted.** This document is prepared to be filed against `mdolab/idwarp` (and cross-linked
to `mdolab/dafoam`), and as of 2026-07-31 it is submission-ready in the sense set out in
"Submission readiness" immediately below. **Whether it is sent is Katie's call, not the lab's.**

## Update, 2026-07-31 (later): ROOT CAUSE LOCALIZED TO A LINE, and this is an OPEN UPSTREAM BUG ALREADY

**Read this before the rest of the report.** Two things below change how this should be filed, if it
is ever filed.

**1. There is already an open upstream issue for this, unanswered since 2021.**
`https://github.com/mdolab/idwarp/issues/57` -- "`inflate_cube` test appears to fail", opened
2021-07-14 by A-CGray, labelled `bug`, **open, zero comments, one timeline event (the label).** It
reports IDWarp's own `verifyWarpDeriv` printing **216.1%** and **217.6%** errors with sign flips on
DOFs 0 and 3 of IDWarp's own regression mesh, while DOFs 1, 2, 4 and 5 read ~4e-05%. That is this
defect, reported by the MDO Lab against itself, five years ago. **Any filing should be a comment on
#57, not a new issue.** Nothing has been sent.

**2. The "Suggested starting point for maintainers" section below is superseded.** It proposed a
multi-point indexing bug. That was already weakened by A5 (single-point variables), and it is now
wrong. The actual cause:

`getRotationMatrix3d`, `src/utils/vectorUtils.f90:31-103` (IDWarp 2.6.2), builds the rotation from
each surface node's reference normal `n0` to its current normal `n` by normalizing the cross product
and taking `acos` of the dot product. That parameterization has a **removable coordinate singularity**
at `n = n0`, guarded at line 58:

```fortran
real(kind=realType), parameter :: tol = 1.4901161193847656e-08     ! line 44 (= sqrt(eps))
...
! When axisMag is less that sqrt(eps), the acos 'arg' value will be
! exactly one which will give a nan in complex mode.
if (axisMag < tol) then                                            ! line 58
    angle = zero
```

Tapenade's reverse of that branch, `src/adjoint/outputReverse/vectorUtils_b.f90:123-128`:

```fortran
CALL POPCONTROL1B(branch)
IF (branch .EQ. 0) THEN
CALL POPREAL8ARRAY(axis, realtype*3/8)
magv2b = 0.0_8
axisb = 0.0_8
axismagb = 0.0_8
```

**zeroes the entire adjoint path back to the normals.** So `dMi/dnormals = 0` exactly. The true
derivative there is `dMi = [n0 x dn]_x`, finite and non-zero -- the map `Mi(n0, n)` is smooth at
`n = n0` even though this parameterization is not. `Mi` multiplies the lever arm `(r - Xu0_i)` from
surface node to volume node (`src/modules/kd_tree.F90:686`), so the discarded term is not small.

`getMag` regularizes with `+1e-30`, so at an undeformed baseline -- where `normals == normals0`
bit-for-bit -- `axisMag = 1e-15 < 1.49e-08` and **the guard fires with certainty.** That is the state
at which every `check_totals` and every first design iteration is evaluated.

**Proof the term was never in the analytic answer.** With `useRotations=False` the warp becomes
exactly linear in `Xs`, and:

| | `useRotations=on` | `useRotations=off` |
|---|---|---|
| `warpDeriv` output, U-bend pressure-loss | `\|\|dXs\|\|=1.495168856286067e+03` | `1.495168856286067e+03`, **bit-identical** |
| idx8 | **207.0%, SIGN-FLIPPED** | **0.0000** |
| idx17 | **121.6%, SIGN-FLIPPED** | **0.0000** |
| stock objective, worst of 27 | **80.79%** | **0.0000, all 27** |
| issue #57 `inflate_cube` DOF 0 | **210.16%** | **1.06e-05%** |

The analytic answer does not move by one bit while the function it differentiates changes sign.

**Scope, narrowed and stated honestly.** Across five IDWarp regression meshes, the cases with a
genuine shear deformation -- where the normals really rotate and the guard does *not* fire -- are
**clean at 1e-05% to 1e-06% with rotations ON**. The catastrophic failure is confined to `n ~ n0`.
This is a defect in the **degenerate-rotation branch**, not in rotation interpolation generally.

**Suggested fix.** The singularity-free form of "rotation taking `a` to `b`" needs neither `acos` nor
the normalization: with `v = a x b` and `c = a.b`, `R = I + [v]_x + [v]_x^2 / (1 + c)`. It is a
polynomial in `v` with a smooth coefficient, is correct and differentiable at `a = b` with no
threshold, and cannot NaN except at `c = -1` (exact reversal), a genuine singularity of the problem
rather than of the parameterization.

**Why upstream CI never caught it.** `tests/test_USMesh.py:86` calls `verifyWarpDeriv` and discards
the result. The only assertion made on `warpDeriv` is `Sum of dxs` at `tol=1e-8` -- and the rotation
term contributes **exactly zero to that sum** on all five meshes tested, while changing `||dXs||` by
factors of 5 to 34. `examples/structured/dotprod.py` is not in `tests/`, and a dot-product test
proves only that forward and reverse AD are mutual transposes, not that either linearizes
`warpMesh()`. And `verifyWarpDeriv` defaults to `randomSeed=314` -- the random seed under which this
defect is already known to hide.

**Not a documented approximation**, on the public record: no doc page, docstring, release note or
source comment qualifies `warpDeriv` as anything but the exact transpose Jacobian. One disclosed gap:
the primary IDWarp reference (Secco, Kenway, He, Mader & Martins, AIAA J. 59(4):1151-1168, 2021,
doi 10.2514/1.J059491) could **not** be retrieved -- 403 on every attempted URL -- so no claim is made
about what it says.

Full evidence, all seven pre-stated falsifiers, the diagnostics that pushed back, and the two
corrections they forced: `ROOTCAUSE_getRotationMatrix3d.md` and `rotation_branch/`.

---

## Submission readiness, 2026-07-31

| requirement | state |
|---|---|
| Reproducer that runs **outside this project's tree** on stock DAFoam | **Done and verified.** `upstream_repro/run_repro.sh` goes from nothing to results in ~2 minutes: fresh `git clone` of the official tutorials at a pinned commit, each case meshed by its own `preProcessing.sh`, two self-contained scripts, no tutorial file edited. Executed end-to-end in a scratch directory on 2026-07-31 08:50:03Z-08:52:11Z; every number below came out of that run. |
| Exact versions | **Done.** Image digest, OpenFOAM build string, and all ten package versions in `upstream_repro/README.md`. `idwarp 2.6.2` is the package under test. |
| Smallest case showing the sign flip | **Done, and it got smaller.** `UBend_Channel`, 4,800 cells, ~13 s for primal + adjoint + all 27 components. The airfoil variant is smaller still (4,032 cells, **no CFD solve at all**, seconds) but exercises the combination-mode DV construction rather than the plain one. |
| Second, independent case | **Done** -- see the 2026-07-31 update immediately below. |

Reproducer bundle: `upstream_repro/` (`README.md`, `run_repro.sh`,
`repro_warpderiv_ubend.py`, `repro_warpderiv_airfoil.py`, and the raw logs).

## Update, 2026-07-31: a SECOND, unrelated case reproduces this, on plain single-point design variables, WITH sign flips -- and this report's central qualification is falsified

Everything below this section was written when the defect was believed to be specific to
opposing-direction/combination FFD modes on one airfoil case. Three of this report's own claims are
now wrong and are corrected here rather than quietly edited out of the text beneath.

**1. "Opposing-direction construction is necessary for the error to be large enough to flip sign"
is FALSIFIED.** The official `DAFoam/tutorials` `UBend_Channel` case (internal 3D curved duct,
4,800-cell `blockMesh`, `DASimpleFoam`) builds its shape variables with
`nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")` -- **one FFD control point moving
along one axis per design variable, unconditionally**, with no opposing-direction, multi-point, or
combination construction anywhere in the case. Two of its 27 components are nonetheless
**sign-flipped at 207.0% and 121.6%**, measured by this report's own identity. The construction is
not the trigger.

**2. This report's statement that a second case "was tested and shown NOT to share this specific
`warpDeriv` mechanism" is RETRACTED.** That test (and a follow-up that confirmed it) seeded the
dot-product identity with an **arbitrary random vector**. Under a random seed those same two
components measure **0.32% and 1.30%** -- clean by any standard. Under the real seed they measure
207% and 122%, sign-flipped. **The analytic call is byte-identical in the two runs; only the
direction it is contracted against changes.** The random-seed clearance was wrong, and this report
had already documented the reason for it (see "Why idx6 corrupts the real gradient and idx7 does
not") without applying it to the second case.

**Methodological consequence, and the single most useful sentence in this report for anyone
verifying a fix: a random-seed dot-product test of `warpDeriv` does not clear it.** It measures
whether the error is large in a generic direction. What determines whether the error reaches a real
gradient is whether the error's location overlaps the objective's own `dF/dXv` sensitivity field.
Both reproducers therefore take `--seed real`, which captures the literal vector the framework
passes to `mesh.warpDeriv` by hooking `DAFoamWarper.compute_jacvec_product`.

**3. The defect is visible on the `UBend_Channel` tutorial with NOT ONE CHARACTER CHANGED.** No
objective substitution, no option change. Under the real seed, with the tutorial's own weighted
`scalePL*(TP1-TP2) + scaleHFX*HFX` objective, the errors span 0.5% to **80.8%**, with **13 of 27
components above 30%** (log: `upstream_repro/repro_ubend_stock_real_np4.log`). The sign flips
require one further change -- a pure total-pressure-loss objective, `val = TP1 - TP2`, a physically
ordinary thing to optimize a duct for -- which the reproducer applies via `--objective
pressure-loss` rather than by editing the tutorial.

### The U-bend numbers (`--objective pressure-loss --seed real`, `h=1e-4`, `np=4`)

| idx | FD of the warp | `warpDeriv` | rel. err | sign | FFD-nonlinearity control | same idx, **random** seed |
|---|---|---|---|---|---|---|
| 2 (control) | -4.06880154e-01 | -4.17657510e-01 | 2.65% | agree | 8.59e-07 | 0.01% |
| 3 | 7.08623060e-01 | 1.96883727e+00 | **177.8%** | agree | 1.71e-06 | 3.65% |
| **8** | 7.87898342e-01 | **-8.43372580e-01** | **207.0%** | **FLIPPED** | 1.01e-07 | **0.32%** |
| 15 | -2.42564294e+01 | -1.38604167e+01 | **42.9%** | agree | 3.83e-08 | 40.7% |
| **17** | 2.91315567e+00 | **-6.28812054e-01** | **121.6%** | **FLIPPED** | 2.98e-07 | **1.30%** |
| 26 (control) | -1.89917527e+00 | -1.95653977e+00 | 3.02% | agree | 1.25e-06 | 0.01% |

Three controls were run alongside, all in the same script:

- **The FD side does not go through the FFD parameterization.** It perturbs surface coordinates
  directly along `eta = dXs/dShape_idx` and calls `mesh.warpMesh()`; `DVGeo.update()` is never
  called on that side. The `--fd-via-dvgeo` column above runs the composed variant too: the two
  agree to `4e-8` - `2e-6`. **FFD nonlinearity is not the explanation.**
- **The analytic scalar equals the framework's own `compute_totals` column** for every component,
  to `0` - `2.1e-15` relative. The captured seed is the real one, and **OpenMDAO's assembly is
  not the problem** -- a hand-replay of the chain rule reproduces the framework exactly.
- **Step size.** Every component was also run at `h=1e-5`; relative errors move by under 0.03
  percentage points (idx8: 207.0408% vs 207.0487%). **Not a finite-difference resolution artifact.**

### Independent corroboration on the same case

The `FD of the warp` column above is a solve-free geometric quantity. It reproduces the same case's
full CFD+adjoint `check_totals` finite-difference column -- 55 primal re-solves, measured months
earlier by a different method -- to **0.07% - 1.5%** for all six components. Two independent
measurements of "the true derivative" agree; `warpDeriv` is the outlier, by the same margin, for the
same components.

The two links either side of `warpDeriv` were isolated on this case and are clean:
`dXs/dShape` (pyGeo's FFD Jacobian) agrees with a componentwise finite difference of
`DVGeo.update()` to **2.8e-12 - 6.4e-12**; `dObj/dXv` (the flow adjoint's own sensitivity to the
volume mesh) agrees with a **true re-solve-based** finite difference -- full nonlinear primal
solves at directly-set volume coordinates via `DASolver.setVolCoords`, bypassing IDWarp entirely --
to **0.17% - 2.49%** at both flagged components, across two step sizes and two solve-path
protocols. On this case the primal is reproducible to `2.8e-12` across repeated identical
re-solves, so the finite-difference noise floor is `1.4e-8` and cannot account for any of this.

### Why two cases matter

| | NACA0012 | UBend_Channel |
|---|---|---|
| flow | external, 2D airfoil | internal, 3D curved duct (half-model) |
| mesh | 4,032 cells, `pyHyp` hyperbolic C-mesh | 4,800 cells, 6-block `blockMesh` |
| objective | drag force integral | total-pressure loss / wall heat flux |
| DV API | `addShapeFunctionDV`, opposing-direction pairs | `addLocalDV`, one point, one axis |
| `meshOptions["symmetryPlanes"]` | two declared | `[]`, as the tutorial ships it |
| result | sign flips at 108-149% | sign flips at 122-207% |

Two mesh generators, two topologies, two objective types, two design-variable APIs, opposite
symmetry-plane configurations. The shared factor is `mesh.warpDeriv`.

### What is still not known

No IDWarp source has been traced. This report establishes that the function's output disagrees with
a finite difference of the function it differentiates; it does not identify the line responsible,
and the "suggested starting point" further down (an indexing/sign-accumulation bug specific to
multi-point DVs) was reasoned from the combination-mode evidence alone and **is now weakened** by
the U-bend result, where the affected DVs are single-point.

## Update, 2026-07-30: the "single-point DVs are unaffected" claim below is corrected, not merely
qualified

This report's own summary (next section) states single-point shape DVs "do not show this defect in any
of 3 independently tested cases." That is now known to be too strong, on this same NACA0012 case. Two of
A1's single-point design variables, idx0 and idx1 (the interior FFD stations nearest the leading edge,
each moving one point along one axis, no opposing-direction pairing — structurally identical in
construction to every other single-point DV in this case, A5, and A2), carry a real, previously
unattributed 11.6-11.9% `dCD/dShape` disagreement, same sign (not the dramatic sign flip idx6/idx7 show,
which is why it was originally missed and attributed to a separate, unidentified mechanism).

Traced this session (`PROOF.md` §21) to the same function, `mesh.warpDeriv`, by a test that had not been
run before: perturbing the surface coordinates `Xs` DIRECTLY along `DVGeo`'s own linear Jacobian
direction (bypassing `DVGeo.update()` entirely, so any nonlinearity in the FFD parameterization itself
cannot be the explanation) and finite-differencing the resulting warp. That direct-`Xs` finite difference
is essentially identical (matching to 7 significant figures) to the original shape-perturbation-based
finite difference, and both disagree with `warpDeriv`'s own analytic output by 11.6-11.9% for idx0/idx1
— while an identical test on a known-clean single-point control (idx4) shows only 2.65%, matching that
component's own established, much smaller gap. **`mesh.warpDeriv`'s mis-linearization is not confined to
opposing-direction/combination design variables. It is present, at a smaller (non-sign-flipping)
magnitude, on at least some single-point design variables too** — specifically the two interior stations
nearest the region (the leading edge) where the combination-mode defect is also concentrated, consistent
with a shared, curvature/location-dependent root cause rather than one specific to the opposing-direction
DV construction. The opposing-direction construction is still confirmed to be what pushes the error far
enough to flip sign (idx2-5/idx7, at other chordwise stations or the TE, remain clean at 1.5-6.4%) — but
"opposing-direction is necessary for the defect to exist" is retracted; only "necessary for it to be
large enough to flip sign, in the cases tested" survives. See `PROOF.md` §21 for the full method, tables,
and the two prior explanations (an OpenMDAO assembly/composition bug; `DVGeo`'s own nonlinearity) this
same session excluded before reaching this conclusion.

## Summary

For a shape design variable built from a pair of FFD control points moving in *opposing* directions
within a single design variable (a standard construction used to move an airfoil's leading or trailing
edge while a paired "mirror" point moves the opposite way, keeping the LE/TE position fixed),
`mesh.warpDeriv` — IDWarp's reverse-mode mesh-warp derivative, and the exact function DAFoam's real
discrete adjoint calls for its mesh sensitivity — returns a result that disagrees with a finite
difference of the actual nonlinear warp by **108–149% relative error, with the sign flipped**, verified
via the standard adjoint dot-product identity. ~~Single-point ("local") shape design variables — one FFD
point moving along one axis per DV, no opposing-direction pairing — do not show this defect in any of
3 independently tested cases (2 different tutorials, 2 different DV APIs).~~ **This sentence is struck
out and RETRACTED (2026-07-31). Single-point single-axis `addLocalDV` design variables DO show this
defect, including sign flips at 207% and 122%, on the `UBend_Channel` tutorial — see the 2026-07-31
update at the top of this document. The three cases it refers to were all cleared by random-seed tests,
which are now known not to clear this function.**

Consequence for users of `check_totals`/gradient verification on this class of design variable: the
finite-difference check is correct; the analytic (adjoint) gradient is wrong. On the official,
unmodified `DAFoam/tutorials` NACA0012 case, this produces a *sign-flipped* `dCD/dShape` component for
the leading-edge combination mode, silently, with no error or warning — `check_totals` reports a large
relative-error percentage, which is easy to attribute to "finite-difference noise on a hard case"
(the working assumption in this lab for months) rather than to a wrong analytic gradient, because the
FD-vs-adjoint mismatch is genuinely step-independent (a hallmark normally associated with an FD problem,
not an adjoint problem) — see "Why this looks like an FD problem at first" below.

## Environment

- Docker image: `dafoam/opt-packages:latest`, digest
  `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`, pulled 2026-07-26.
- `dafoam` 5.0.0, `idwarp` 2.6.2, `pygeo` 1.13.0 (`pip show`, confirmed in-container).
- OpenFOAM v2506 (build `_615aae61d7-20250627`).
- Case: `DAFoam/tutorials` (`https://github.com/DAFoam/tutorials`, commit
  `d3b7e38b058aba2a98a74092e15c41ec455c570d`, 2026-05-16), `NACA0012_Airfoil/incompressible`, unmodified
  except as noted. 4,032-cell mesh, `DASimpleFoam`, Spalart-Allmaras, wall functions
  (`nutUSpaldingWallFunction`).
- `useAD` is left at its DAFoam default in this case's `daOptions`: `{"mode": "reverse",
  "dvName": "None", "seedIndex": -9999}` (confirmed by reading `pyDAFoam.py` in the container). This
  matters: `DAFoamWarper.compute_jacvec_product` (`dafoam/mphys/mphys_dafoam.py`) calls
  `mesh.warpDeriv(dxV)` — the reverse-mode function — and explicitly does not support `mode="fwd"`.
  `mesh.warpDerivFwd` exists but is a *different* function this case's adjoint never calls; testing it
  instead (which an earlier, retracted diagnostic in this investigation did) produces 33–200% error on
  every shape component including the ones independently verified clean through the full CFD+adjoint
  chain — consistent with testing an unexercised code path, not with a shared defect.

## The design-variable construction that triggers it

From the tutorial's own `runScript.py`, unmodified, `Top.configure()`:

```python
pts = self.geometry.DVGeo.getLocalIndex(0)
dir_y = np.array([0.0, 1.0, 0.0])
shapes = []
for i in range(1, pts.shape[0] - 1):
    for j in range(pts.shape[1]):
        # single-station: one chordwise position, top+bottom move together
        shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
for i in [0, pts.shape[0] - 1]:
    # COMBINATION mode: the LE (i=0) or TE (i=pts.shape[0]-1) point and its
    # "mirror" point move in OPPOSING directions within the SAME design variable,
    # so the LE/TE position itself stays fixed while the surface pivots around it
    shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)
```

This produces 8 shape DVs: idx0–idx5 are single-station (one chordwise position, points move together),
idx6 is the leading-edge combination mode, idx7 is the trailing-edge combination mode. **Both idx6 and
idx7 share the identical opposing-direction construction.**

## The identity used to test `warpDeriv` in isolation

`mesh.warpDeriv` is a reverse-mode Jacobian-transpose-vector product: given a seed `w` in the OUTPUT
(volume-mesh coordinate, `Xv`) space, it returns `w^T (dXv/dXs)`, a vector in surface-coordinate (`Xs`)
space. It does not expose a forward Jacobian column directly, so the correct way to check a reverse-mode
VJP against a pure finite difference of the underlying nonlinear function (no derivative code involved
on the FD side at all) is the standard adjoint/dot-product identity:

```
<w, dXv/dShape_idx>_FD   ==   <warpDeriv(w), dXs/dShape_idx>_analytic
```

- LHS ("FD_scalar"): perturb `shape[idx]` by `+h` and `-h`, call `DVGeo.update()` then
  `mesh.warpMesh()` at each (the actual, nonlinear, run-it-and-see warp — the exact code path
  `check_totals`' own finite difference exercises), central-difference the resulting volume-mesh
  coordinates (`mesh.getSolverGrid()`), dot with a fixed seed `w`.
- RHS ("AN_scalar"): call `mesh.warpDeriv(w)` (exactly as `DAFoamWarper.compute_jacvec_product` does in
  the real adjoint), take `mesh.getdXs()`, dot it with `DVGeo.totalSensitivityProd`'s forward-mode
  surface sensitivity for that shape index (pyGeo's own FFD Jacobian — independently confirmed exact to
  ~1e-13 relative error against FD elsewhere in this investigation, not the function under test here).

If these two scalars disagree, `warpDeriv` is not a valid linearization of the actual warp for that
design variable, for the tested direction `w`.

## Minimal reproducer

Pure geometry: `DVGeo` + IDWarp only, **no CFD solve**. Requires only the tutorial's mesh/FFD/`0.orig`
(no primal or adjoint solve needed to reach this test). Run inside `dafoam/opt-packages:latest`, working
directory = the tutorial case dir (`NACA0012_Airfoil/incompressible` after its own `preProcessing.sh`
has generated the mesh once):

```python
#!/usr/bin/env python
import os, argparse
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder
from pygeo import DVGeometry

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True)   # 0-7
parser.add_argument("--h", type=float, default=1e-4)
parser.add_argument("--seed", type=int, default=2026)
args = parser.parse_args()

U0, p0, nuTilda0, aoa0, A0, rho0 = 10.0, 0.0, 4.5e-5, 5.13918623195176, 0.1, 1.0
daOptions = {
    "designSurfaces": ["wing"], "solverName": "DASimpleFoam", "primalMinResTol": 1.0e-8,
    "primalBC": {"U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
                 "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
                 "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
                 "useWallFunction": True},
    "function": {"CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
                         "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
                         "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)}},
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
                  "patchV": {"type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
                             "normalAxis": "y", "components": ["solver", "function"]}},
}
meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM",
               "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]]}

comm = MPI.COMM_WORLD
builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
builder.initialize(comm)
DASolver = builder.DASolver
mesh = DASolver.mesh
xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup)

DVGeo = DVGeometry(os.path.join(os.getcwd(), "FFD", "wingFFD.xyz"))
ptSetName = "x_aero0"
DVGeo.addPointSet(xs0, ptSetName)
pts = DVGeo.getLocalIndex(0)
dir_y = np.array([0.0, 1.0, 0.0])
shapes = []
for i in range(1, pts.shape[0] - 1):
    for j in range(pts.shape[1]):
        shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
for i in [0, pts.shape[0] - 1]:
    shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
nShape = len(shapes)
DVGeo.addShapeFunctionDV("shape", shapes)
idx = args.idx

def set_shape(vec):
    DVGeo.setDesignVars({"shape": np.array(vec)})

def get_warped_Xv(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()

Xv0 = get_warped_Xv(np.zeros(nShape))
nXvLocal = Xv0.size
np.random.seed(args.seed)
w = np.random.random(nXvLocal).astype("d")

h = args.h
ePlus = np.zeros(nShape); ePlus[idx] = h
eMinus = np.zeros(nShape); eMinus[idx] = -h
Xv_p = get_warped_Xv(ePlus)
Xv_m = get_warped_Xv(eMinus)
FD_dXv_idx_local = (Xv_p - Xv_m) / (2.0 * h)
FD_scalar = comm.allreduce(float(np.dot(w, FD_dXv_idx_local)), op=MPI.SUM)

set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)
seedDV = {"shape": np.zeros(nShape)}; seedDV["shape"][idx] = 1.0
AN_dXs_idx = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

set_shape(np.zeros(nShape))
xs_base = DVGeo.update(ptSetName)
DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
mesh.warpMesh()
mesh.warpDeriv(w)                      # <-- the function under test
dXs_seed = mesh.getdXs()
dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)
AN_scalar = comm.allreduce(float(np.dot(dXs_seed.flatten(), AN_dXs_idx.flatten())), op=MPI.SUM)

if comm.rank == 0:
    relerr = abs(FD_scalar - AN_scalar) / (abs(FD_scalar) + 1e-300)
    print(f"idx={idx} FD_scalar={FD_scalar:.6e} AN_scalar={AN_scalar:.6e} rel_err={relerr:.6f}")
```

Run (decomposition is handled internally by `DAFoamBuilder.initialize(comm)` — do not call
`decomposePar` manually, it will conflict with the builder's own decomposition):

```bash
sudo docker run --rm --cpus=3 --memory=3g \
  -v <case_dir>:/home/dafoamuser/mount -w /home/dafoamuser/mount \
  dafoam/opt-packages:latest \
  bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && \
            mpirun --allow-run-as-root -np 4 python repro.py --idx 6 --h 1e-4 --seed 2026'
```

(A single-rank invocation, `python repro.py --idx 6 ...` with no `mpirun`, reproduces the same
qualitative result — this is not a parallel-decomposition artifact.)

## Results

| idx | construction | seed | ranks | FD_scalar | AN_scalar (`warpDeriv`) | rel. err. | sign |
|---|---|---|---|---|---|---|---|
| 4 | single-station (control) | 2026 | 1 | 477.8887 | 477.4013 | 0.10% | agree |
| 4 | single-station (control) | 2026 | 4 | 485.2993 | 496.7999 | 2.37% | agree |
| 4 | single-station (control) | 42 | 4 | 473.8014 | 482.4881 | 1.83% | agree |
| 4 | single-station (control) | 2026 (h=1e-5) | 4 | 485.2651 | 496.7999 | 2.38% | agree |
| **6** | **combination (LE)** | 2026 | 1 | 11.8983 | -1.8153 | **115.26%** | **FLIPPED** |
| **6** | **combination (LE)** | 2026 | 4 | 13.1338 | -1.5600 | **111.88%** | **FLIPPED** |
| **6** | **combination (LE)** | 42 | 4 | 14.6722 | -1.1222 | **107.65%** | **FLIPPED** |
| **6** | **combination (LE)** | 2026 (h=1e-5) | 4 | 13.1323 | -1.5600 | **111.88%** | **FLIPPED** |
| **7** | **combination (TE)** | 2026 | 4 | -7.4350 | 1.0593 | **114.25%** | **FLIPPED** |
| **7** | **combination (TE)** | 42 | 4 | -7.6036 | 0.9709 | **112.77%** | **FLIPPED** |

`AN_scalar` (a single analytic evaluation, not a finite difference) is **bit-identical** between
`h=1e-4` and `h=1e-5` for idx6, by construction — it cannot depend on step size. `FD_scalar` itself
moves by 0.01% across that same decade of `h` — the disagreement is a fixed gap between two converged
numbers at every step size tested, not a resolution artifact on either side.

**idx4 (single-station) agrees to 0.1–2.4% in every configuration tested, sign always correct. idx6 and
idx7 (both combination-mode DVs) disagree by 108–149% and are SIGN-FLIPPED in every configuration
tested**, independent of seed, step size, and serial-vs-4-rank-parallel execution.

## Why idx6 corrupts the real gradient and idx7 does not, despite an identical generic failure -- resolved

Despite idx6 and idx7 sharing the identical construction and both failing the random-seed test above in
the same way, **only idx6 produces a wrong result in the real, full-chain `dCD/dShape` gradient**
(verified via `check_totals` against finite differences across two mesh resolutions in this
investigation — idx7 agrees to 1.5–1.8%, idx6 is sign-flipped). The seed `w` used above is an arbitrary
fixed random vector, not the real force-objective's own reverse-mode seed (`dCD/dXv`). Our hypothesis was
that `warpDeriv`'s linearization error exists in some subspace at both the LE and the TE for this
construction, but only survives contraction with the real objective's own gradient direction
(concentrated near the LE stagnation region for a drag objective at this Reynolds number/incidence) at
the LE.

**This has now been tested directly and the hypothesis is confirmed.** We captured the literal `dxV`
vector the real adjoint chain hands to `mesh.warpDeriv(dxV)` -- not a reconstruction of it -- by running
the real, unmodified `Top` model (`runScript.py`), doing one real reverse-mode CD adjoint solve
(`prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["shape"])`), and hooking
`DAFoamWarper.compute_jacvec_product` to record its `d_outputs["aero_vol_coords"]` argument at the one
point it is called. Re-running the identity above with that real seed in place of the random one:

| idx | construction | FD_scalar (real seed) | AN_scalar (real seed) | rel. err. | sign |
|---|---|---|---|---|---|
| 4 | single-station (control) | 3.9997e-02 | 3.8938e-02 | 2.65% | agree |
| **6** | **combination (LE)** | -1.0656e-03 | 5.6907e-03 | **634.0%** | **FLIPPED** |
| **7** | **combination (TE)** | 3.5281e-03 | 3.4668e-03 | **1.74%** | agree |

**With the real seed, idx6 still fails badly and is still sign-flipped; idx7 now agrees, to 1.74% --
matching, almost exactly, the 1.5–1.8% idx7's real gradient has independently shown in every direct
`check_totals` measurement.** As a cross-check (not requested by this test but a useful sanity bound):
this run's `AN_scalar` values match this lab's independently-measured real adjoint values for idx4/6/7
to all printed digits (expected, since it is the same quantity reconstructed through the same code
path), and its `FD_scalar` values match the independently-measured real FD values to 0.03–1.2%,
including reproducing idx6's sign flip and ~640% magnitude almost exactly -- strong evidence the
real-seed identity is measuring the same thing the original gradient check measured, not an unrelated
quantity.

**Conclusion for maintainers:** `mesh.warpDeriv`'s mis-linearization of opposing-direction combination
shape modes is not localized to a single design variable's own footprint in a way that always corrupts
that variable's own gradient -- it is present (measurably, via the generic random-seed test) at BOTH the
LE and TE combo modes in this case, but the specific real-world consequence for any given objective
depends on whether that objective's own adjoint sensitivity field (`dF/dXv`) overlaps the region where
`warpDeriv`'s error lives. For a drag objective, that overlap is large at the LE and negligible at the
TE, which is exactly the split observed. This does not change the recommended starting point below for
locating the bug in `warpDeriv`'s own source, but it does resolve what looked like an inconsistency in
this report's own evidence, without requiring the bug to behave differently at the LE and the TE.

## Suggested starting point for maintainers

The measured pattern — correct for a DV that perturbs one FFD point along one axis, wrong (sign-flipped,
not just numerically imprecise) for a DV that perturbs two or more FFD points with different/opposing
sign conventions within the same design variable — is consistent with an indexing, aliasing, or
sign-accumulation bug specific to the reverse-mode accumulation path for multi-point design variables in
`mesh.warpDeriv`/`mesh.getdXs()`, as opposed to a general accuracy or conditioning problem (a
conditioning problem would not produce a clean, step-independent, bit-reproducible sign flip). We have
not traced this into IDWarp's own source in this investigation and cannot point to a specific line.

## Files behind this report (this lab's internal paths, not part of the reproducer)

- `demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeWarpDeriv.py` — the exact
  script behind the idx4/idx6 numbers above (parameterized `--idx`/`--h`/`--seed` version of the
  reproducer)
- `demo-output/website/dafoam/probewarpderiv_idx{4,6,7}_*_run1.log` — raw stdout for every
  configuration in the results table
- `demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeWarpDerivRealSeed.py` — the
  real-`dCD/dXv`-seed follow-up script: builds the real `runScript.py` model, runs a real primal + CD
  adjoint solve, captures the real seed via a hook on `DAFoamWarper.compute_jacvec_product`, repeats the
  identity for idx4/idx6/idx7 with that real seed instead of a random one
- `demo-output/website/dafoam/probewarpderiv_realseed_idx4_idx6_idx7_np4_run1.log` — raw stdout behind
  the real-seed results table above
- `demo-output/website/dafoam/PROOF.md`, sections 15–21 — full investigation history on the NACA0012
  case, including 8 other mechanisms tested and refuted before this one was found (residual-tolerance
  noise, FFD/DVGeo Jacobian convention, coarse-mesh discretization error, frozen wall-distance, a
  wall-function branch-crossing hypothesis, combination-mode mesh pinching, DVGeo's own nonlinearity,
  and OpenMDAO's assembly), section 17 (the real-seed follow-up that resolved the idx6-vs-idx7
  question above) and section 21 (the hand-composition test that isolated `warpDeriv` for idx0/idx1).

  **Correction, 2026-07-31:** this bullet previously stated that the second case (A5, U-Bend Channel)
  "was tested and shown NOT to share this specific `warpDeriv` mechanism," and used that to scope the
  defect to NACA0012. **That is retracted.** The test behind it used a random seed; under the real
  seed the U-bend shares the mechanism and sign-flips two components. See the 2026-07-31 update at the
  top of this document and `demo-output/website/dafoam/ladder-a/A5_ubend_internal.md` (addendum,
  2026-07-31) for the retraction and the full link-by-link evidence.

- `demo-output/website/dafoam/upstream_repro/` — the standalone reproducer bundle referenced at the
  top: `run_repro.sh` (clone-to-result, verified 2026-07-31 08:50:03Z–08:52:11Z on a fresh clone in a
  scratch directory outside this repo), `repro_warpderiv_ubend.py`, `repro_warpderiv_airfoil.py`,
  `README.md` (exact versions), and four raw logs.
- `demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5RealSeed.py`,
  `probeA5DObjDXv.py`, `probeA5NoiseFloor.py`, `probeA5DObjDXvReset.py`, with raw logs
  `demo-output/website/dafoam/a5_realseed_np4_run1.log`, `a5_dobjdxv_np1_run1.log`,
  `a5_noisefloor_np1_run1.log`, `a5_dobjdxv_reset_np1_run1.log` — the in-repo versions of the
  U-bend work, including the two links either side of `warpDeriv` and the noise-floor and
  path-dependence controls on the probes themselves.
