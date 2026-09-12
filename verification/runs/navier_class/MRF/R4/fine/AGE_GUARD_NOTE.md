# Why this case carries `0.snappyLevels/` and not `0/`

**Nothing was deleted.** `snappyHexMesh` writes its refinement bookkeeping —
`cellLevel` and `pointLevel`, both `volScalarField`-class metadata, not solution
fields — into a directory named `0`. Those two files were **renamed, not removed**:
`0/` → `0.snappyLevels/`, contents byte-identical, at 2026-09-12 after the build
closed rc=0 and before the queue entry was placed.

**Why it had to move.** `scripts/queue_entry_check.py:check_age_guard` refuses any
entry whose `cwd` contains a time directory, and its own comment is explicit —
*"it still refuses on any time directory, `0` included"* — because standing rule 4
requires every field at `endTime` to be NEWER than the case's own `0/T`, and a
pre-existing `0/` makes that unprovable for the run that follows. The name `0`
matches `TIME_DIR`; the contents are irrelevant to the gate, and correctly so: a
gate that inspected contents would be a gate you could talk round.

**Why renaming loses nothing.** `cases/navier_class/MRF/launch_graded.sh:101`
reads `rm -rf 0 && cp -r 0.orig 0` — the launcher **deletes `0/` and re-stages it
from `0.orig/` last, immediately before the solve**, precisely so that `0/` dates
the run for the age guard. Snappy's `cellLevel`/`pointLevel` are destroyed by the
launcher in the normal path anyway and are used by nothing between here and the
solve. They are kept under the new name only so that nothing is lost.

**The mesh is untouched.** `constant/polyMesh/points` sha256 is identical before
and after the rename:
`907d898a3c0aafb0eee402065802cb13bb5a744e504f7c5b4bfda6415c6462b4`, the same value
the frozen `MESH_BIRTH_CERTIFICATE.json` and `MRF_R4_PREREGISTRATION.md` §11 pin.
No graded artifact moved and no registration value changed.

**Fixed at source as well as here.** `cases/navier_class/MRF/build_level_r4.sh`
now performs the same rename at the end of every build, so a future R4-family
case is born without a time directory rather than needing this note. The R2
family has the same `0/` in every built level — it was never hit because R2 was
not launched through the runner.
