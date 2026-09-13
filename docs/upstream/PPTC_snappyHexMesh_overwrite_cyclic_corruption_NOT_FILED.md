NOT FILED — draft for Sanaa's decision

# Bug report: `snappyHexMesh -overwrite` writes back a cyclic mesh it can no longer read — `periodic0` face areas diverge by 3.95 % against a 1e-4 tolerance, after a layer phase that added zero layers and exited rc=0

**Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been
contacted, nothing has been posted, pushed or emailed.** This document is
prepared to be filed against `OpenFOAM` (ESI / openfoam.com), utility
`applications/utilities/mesh/generation/snappyHexMesh`. **Whether it is sent is
Sanaa's call, not the lab's.**

**NOT SUBMISSION-READY. No novelty search has been done.** Nobody has checked
whether this is already an open issue, already fixed on `develop`, or already
discussed on cfd-online. It must not be filed until that check exists.
Everything below is reproduced on this box; the gap is provenance, not evidence.

Surfaced as a run rather than worked around, per Sanaa's directive of
2026-09-10.

---

## The claim, in one sentence

A `snappyHexMesh` invocation with `castellatedMesh false; snap false;
addLayers true;` that adds **zero** layers, reports `Extruding 0 out of 76465
faces (0%)`, finishes with `End` and exits **rc=0**, nevertheless writes back
under `-overwrite` a `constant/polyMesh` whose `cyclic` patch pair fails
`cyclicPolyPatch::calcTransforms`, so that **`snappyHexMesh` itself — and every
other OpenFOAM application — can no longer construct the mesh it just wrote.**

## Version

    OpenFOAM: 2606
    Build   : _481094f-20260618  OPENFOAM=2606  version=2606
    Arch    : LSB;label=32;scalar=64
    Exec    : snappyHexMesh -overwrite      (serial, nProcs 1)

## The evidence, on this box

**Before.** `/home/ubuntu/certonomous-runs/PPTC_VP1304/L1_prod7s/log.snappyHexMesh.layersBladesOnly`
— a 72-degree sector of a marine propeller, 3,939,801 cells, patches
`periodic0`/`periodic1` of type `cyclic`, 21,859 faces each.

    grep -c "face ordering problem" log.snappyHexMesh.layersBladesOnly   ->  0
    grep -c '^End' log.snappyHexMesh.layersBladesOnly                   ->  1
    :430  Extruding 0 out of 76465 faces (0%). Removed extrusion at 36335 faces.
    :483  Extruding 0 out of 76465 faces (0%). Removed extrusion at 0 faces.
    :484  Added 0 out of 458790 cells (0%).
    :508  Finished meshing in = 438.91 s.

So the mesh was constructed cleanly at the start of that run, the run added
nothing, and it exited successfully. `-overwrite` then rewrote
`constant/polyMesh`.

**After.** Any OpenFOAM application on that written mesh:

    --> FOAM FATAL ERROR: (openfoam-2606)
    face 0 area does not match neighbour by 3.9502098% -- possible face ordering problem.
    patch:periodic0 my area:0.00099038143 neighbour area:0.00095201703 matching tolerance:0.0001
    Mesh face:11795467 fc:(-0.35588392 0.057145372 0.038313493)
    Neighbour fc:(-0.38232592 0.080845886 0.0098249763)
        From void Foam::cyclicPolyPatch::calcTransforms(...)
        in file meshes/polyMesh/polyPatches/constraint/cyclic/cyclicPolyPatch.C at line 214.

3.95 % against a 1e-4 tolerance is not a rounding question. The reported
neighbour face centre is **38 mm** from its partner on a mesh whose blade
surface cells are 0.625 mm.

## Reproduction, and the control that makes it a defect rather than a user error

    cp -a L1_prod7s/constant PRISM_A1_absthick/constant
    cp -a L1_prod7s/system   PRISM_A1_absthick/system
    cd PRISM_A1_absthick && snappyHexMesh -overwrite      # rc=1 in 13 s, error above

**Control — the dictionary is exonerated.** The first attempt carried a modified
`addLayersControls` (relative sizing changed to absolute), so the obvious
explanation was that the edit broke it. It did not. The **same copied mesh** was
re-run under the **original, unmodified** `snappyHexMeshDict` taken byte-for-byte
from `L1_prod7s/system/`:

    PRISM_A1_absthick/crash_control/log.control:33
      face 0 area does not match neighbour by 3.9502098% -- possible face ordering problem.

Identical failure, identical patch, identical figure to eight digits, rc=1. **The
input dictionary is not involved. The mesh on disk is the defect.**

## Why this is worth reporting

1. **The failure is silent at the moment it is created.** rc=0, an `End` line, a
   complete log. Nothing in the successful run's output says the written mesh is
   unloadable. It is discovered only by the next application to open it, which
   may be hours later and in a different session.
2. **It happens on a run that changed nothing.** Zero layers were added. The
   utility's own report is `Added 0 out of 458790 cells (0%)`. A no-op write
   should be, at worst, a no-op.
3. **`-overwrite` is destructive.** The pre-run mesh is gone; there is no
   `0/`-style time directory to fall back to. The only recovery is to re-run
   castellation and snapping, which for this case cost 8,591 s.

## What we have NOT established, and will not claim

- Whether the corruption occurs during the layer phase's face merging
  (`mergePatchFacesUndo`, which the log shows running with `Undo iteration 0..2`
  and `Masters that need to be restored:10760`) or during the write itself.
  **We have not instrumented it and we do not assert a mechanism.**
- Whether the same happens in parallel, with `-overwrite` absent, on a
  non-cyclic mesh, or with layers actually added.
- Whether it reproduces from a clean checkout on a different case. **A minimal
  reproducer does not yet exist**, and a bug report without one is a weaker
  report. Building one is the next step if Sanaa decides this is to be filed.
- Whether it is already reported. **No novelty search has been done.**

## Local consequence, recorded so the lab does not trip on it again

`L1_prod7s` is **quarantined**: nothing re-runs on that mesh. The 360-degree
mesh `F360_coarse` has **no cyclic patches at all**
(`grep -c cyclic constant/polyMesh/boundary` = 0) and still loads.
