# Scratch mesh directory for the adjoint wing act (Act D)

**Holds no evidence. Everything in it is rewritten on every drive of the act
and nothing here is cited by any record.**

Sibling of `verification/runs/DMR_runs/demo_mesh_work/`, and it exists for the
same reason.

## Why the act's mesher does not write where it reads

Act D's `mesh_plan().work_dir` used to be `/home/ubuntu/certonomous-runs/
A2-mach-wing` — the act's own **landed run root**, the tree its results are read
out of. `demo_sequencer.Sequencer._unsafe_work_dir` refused to mesh into it (it
holds `system/controlDict`), so the live meshing stage **skipped**, and the
screen showed a cell **count** with no grid behind it. The pre-shoot gate
`scripts/check_demo_acts.py` reported it as `adjoint-wing: CANNOT START`.

**The guard is correct and this act does not route around it.** A mesher writing
a fresh `constant/polyMesh` into a landed case destroys the provenance the strict
completion rule's age guard rests on — that guard turns on every field at
`endTime` being newer than the case's own `0/`. An absent mesh stage costs a
picture. A corrupted graded case cannot be re-solved, and A2 is the wing the
28.3 % decomposition is measured on.

So the **write** target moved here and the **read** path did not: the act still
reads its logs, its replay series and its geometry identity out of the run root,
exactly as before. Only the mesher's output moved.

## Do not put a case here

The mesher writes `constant/polyMesh` and nothing else, which is why this
directory stays usable across every drive. Add a `system/controlDict`, a
`constant/turbulenceProperties` or a solved time directory and the guard will
classify this as a real case, the meshing stage will skip again, and the screen
will go back to showing a number instead of a grid.
