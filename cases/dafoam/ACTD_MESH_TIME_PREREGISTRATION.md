# Act D live-meshing viability — mesh-time measurement, pre-registration

**Frozen before compute. dafoam lane, 2026-09-01.**
Authorised by dafoam-supervisor as the ONE run permitted under the Act D demo-mode
prep brief ("NOTHING LAUNCHES except the mesh-time measurement in deliverable 1").

## The question, in one line

Sanaa's DEMO MODE directive (`etc/sessions/2026-09-01T0340Z_sanaa_demo_mode_binding.md`)
says *"Meshing runs live (2D/axisymmetric cases mesh in seconds to a minute)"*. Act D is a
three-dimensional wing at 38,304 cells. **How long does the real mesher that built Act D's
grid actually take on this box, and is that fast enough to draw live on camera?**

## What is measured

The mesh pipeline that produced the 38,304-cell grid the act's numbers belong to, stage
by stage, as `preProcessing.sh` runs it:

1. `cgns_utils coarsen` — surface mesh coarsening (CGNS → CGNS)
2. `python genWingMesh.py` — **pyHyp hyperbolic extrusion**, 39 layers, s0 = 1e-3,
   marchDist = 300 (Plot3D volume mesh out)
3. `plot3dToFoam -noBlank` — Plot3D → OpenFOAM polyMesh
4. `autoPatch 60 -overwrite`
5. `createPatch -overwrite`
6. `renumberMesh -overwrite`

Each stage is wall-clocked separately inside the container with `date +%s.%N` written to a
stage-timing file, so no stage time is inferred from a total.

## Prediction, registered before the run

- Total mesh wall time falls in **20 s – 300 s**. Stated so the answer can falsify it.
- The pyHyp extrusion (stage 2) is the dominant stage, **> 50 %** of the total.
- **Verdict rule, fixed now:** live cell-by-cell meshing on camera is called viable only
  if total mesh wall time is **≤ 60 s** (Sanaa's own words, "seconds to a minute"). Above
  60 s the answer reported is *not viable at the stated pace*, with the number, and no
  pre-baked or staged mesh is presented as live meshing.

## Cost

- Ranks: pipeline is **serial (1 process)**; container given `--cpus=4`, matching how the
  production A2 run was containerised.
- Cap: **600 s wall**. Core-minutes at the reserved 4-core quota: **40 core-min** worst
  case; at the 1 rank actually executing, **10 core-min** worst case. Both are reported.
- Derived dollars at the recorded $0.0513/core-h rate: **≤ $0.034** (4-core basis).
  *Derived, not measured* — the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Overrun stops the run.** The `timeout` is inside the container wrapper and the rc is
  captured inside it (`setsid`/wrapper parent-returns-zero trap).

## Guards

- **Rule 4 guard:** the runner refuses outright if the run root
  `/home/ubuntu/certonomous-runs/ACTD-meshtime` already exists.
- The recorded A2 run tree `/home/ubuntu/certonomous-runs/A2-mach-wing` is **read-only to
  this measurement**; the timing runs on a fresh copy of the pristine tutorial at
  `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing`, whose
  `runScript_AeroOnly.py` md5 is asserted before the copy.
- **Identity check that makes the timing mean anything:** the mesh this measurement builds
  must be the same size as the mesh Act D's numbers belong to. The runner asserts
  `Mesh region0 size: 38304` in its own `renumberMesh` output. A different cell count makes
  the timing a timing of a different grid and the result is reported as
  **NOT A RESULT**, not as Act D's mesh time.

## Not measured, and named so it is not assumed

This pipeline does **not** mesh an STL. It extrudes a CGNS surface mesh. Whether some
*other* mesher (snappyHexMesh on `mach_tutorial_wing.stl`) could produce a comparable grid,
and how long that would take, is **outside this measurement** and no number for it is
reported.
