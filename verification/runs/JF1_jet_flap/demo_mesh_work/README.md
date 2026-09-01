# Scratch mesh target for the demo-mode meshing stage

This directory exists so that a live mesher has somewhere to write that is
**not a graded case**.

The jet-flap act's mesh stage names a real mesher. Until this directory
existed, the act pointed that mesher's working directory at
`JF1_L1_BLOWN_CMU020_A0` — a landed, complete, graded run. A mesher writing a
fresh `constant/polyMesh` into that tree would destroy the provenance of a
result that cannot be re-solved tonight: the strict completion rule's age
guard turns on every field at `endTime` being newer than the case's own `0/`,
and a rebuilt mesh breaks the chain the rows on camera rest on.

So the working directory is here. Anything written into this directory is
disposable. Nothing here is evidence, and nothing here is read by the screen:
the cell count, the wall resolution and the mesh figure are all read from the
solved case's own artifacts, by the readers in `jf1_display_numbers.py`.

The mesher named by the act is the one the run's own launcher recorded at
`cases/JF1_JET_FLAP/run_jf1_blown.sh` lines 268-270:

    python3 cases/JF1_JET_FLAP/build_jf1.py --out <dir> --level L1 --slot-type patch

It is NOT `blockMesh`. There is no `blockMeshDict` anywhere in this campaign;
the O-mesh the five force calculations ran on is emitted by `build_jf1.py`,
and the finer C-mesh by `mesh/make_jf1_mesh.py`.
