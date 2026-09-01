# Scratch mesh directory for the shock-reflection act

**Holds no evidence. Everything in it is rewritten on every drive of the act
and nothing here is cited by any record.**

The act's meshing stage runs a real mesher
(`cases/DMR_shock_reflection/build_dmr_mesh.py`) and the mesher writes here.
It has to write somewhere, and the somewhere must not be a landed case: a
mesher writing a fresh `constant/polyMesh` into one destroys the provenance
the strict completion rule's age guard rests on, because that guard turns on
every field at `endTime` being newer than the case's own `0/`. An absent mesh
stage costs a picture; a corrupted graded case cannot be re-solved.

`demo_sequencer.Sequencer._unsafe_work_dir` enforces that rather than trusting
it: it refuses to point the mesher at any directory holding a
`system/controlDict` or a `constant/turbulenceProperties` or a solved time
directory, and the pre-shoot gate `scripts/check_demo_acts.py` reports an act
whose working directory has drifted into one. **Do not put a case here.** The
mesher writes only `constant/polyMesh`, which is why this directory stays
usable across every drive; add a `system/controlDict` and the meshing stage
silently stops meshing for good.

Only this file is tracked. The mesh itself is generated output.
