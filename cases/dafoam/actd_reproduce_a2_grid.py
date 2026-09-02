#!/usr/bin/env python3
"""WHAT THE ADJOINT-WING ACT'S MESHING STAGE ACTUALLY RUNS, AND WHY IT IS A
REPRODUCTION RATHER THAN A MESHER.

THE REAL MESHER IS NOT ON THIS HOST, AND THAT IS MEASURED, NOT ASSUMED. The
grid the A2 wing was solved on was built by ``cgns_utils`` -> ``pyHyp`` ->
``plot3dToFoam`` -> ``autoPatch`` -> ``createPatch`` -> ``renumberMesh`` -- a
hyperbolic extrusion off a CGNS surface mesh -- and every one of those tools
lives only inside the DAFoam container. Repointing the act's ``work_dir`` at
scratch without replacing the command was tried and produced a HARD refusal at
stage 5 ("the meshing stage names a mesher that is not on this machine"): 20
events, 5 of 9 stages, the act off the air entirely. The regression is recorded
in the history of ``sdk/workflows/adjoint_act.py`` (the mesh_plan comment block,
now resolved by this file).

SO THE DEMO STAGE REPRODUCES THE STORED GRID INSTEAD OF FABRICATING A RUN OF A
MESHER IT DOES NOT HAVE. Sanaa's standing ruling for the acts is that results
are stored, not run live, and that every act shows the REAL mesh. This script
copies the landed run's own ``constant/polyMesh`` -- byte-for-byte after gunzip
-- into the scratch directory the sequencer hands it. Nothing is generated,
synthesised, decimated or renumbered; the sequencer then reads the cell count
back OFF THE MESH JUST WRITTEN (``demo_sequencer._live_cell_count``) and
refuses to show a grid that does not reproduce the solved one. The count is
therefore a checkable claim about the copy, not a comment.

WHY THE COPY IS DECOMPRESSED. The landed run writes ``owner.gz`` etc.;
``_live_cell_count`` reads ``constant/polyMesh/owner`` as plain text, and the
ParaView panel guard reads the same file. The gunzip changes the container,
never the bytes of the mesh description.

SAFETY PROPERTIES, IN ORDER OF WHO ENFORCES THEM:
  * READS the landed run root, WRITES only under ``--out``. The run root is
    opened read-only and nothing in this file constructs a write path from it.
  * Writes ONLY ``<out>/constant/polyMesh``. No ``system/``, no time
    directory, no ``turbulenceProperties`` -- the sequencer's
    ``_unsafe_work_dir`` guard classifies a directory holding any of those as
    a real case and stops meshing there for good.
  * Refuses to write into a directory that already looks like a real case,
    mirroring that guard rather than trusting the caller.

    python3 cases/dafoam/actd_reproduce_a2_grid.py --out <scratch dir>

STARTS NO SOLVER, RUNS NO CONTAINER, WRITES NOTHING OUTSIDE ``--out``.
"""

from __future__ import annotations

import argparse
import gzip
import shutil
import sys
from pathlib import Path

#: The landed A2 run root the act reads everything else from
#: (``A2_optimization_history.json`` records it as ``_source_dir``). Named
#: here as a constant rather than re-read from the record so this script has
#: no dependency on the sdk package and can be run by a bare python3, which is
#: what the sequencer invokes.
SOURCE_POLYMESH = Path(
    "/home/ubuntu/certonomous-runs/A2-mach-wing/constant/polyMesh")

#: The solved grid's cell count, asserted after the copy by re-reading the
#: ``owner`` file just written. 38,304 is the count in
#: ``cases/dafoam/ladder-a/A2_mesh_time.json`` (``identity_assert``) and in
#: the run's own checkMesh record; a copy that reads back anything else exits
#: non-zero and the sequencer shows no grid.
EXPECT_CELLS = 38304

#: Directory contents that mean "this is a real case tree, not scratch" --
#: the same tells ``demo_sequencer.Sequencer._unsafe_work_dir`` uses.
CASE_TELLS = ("system/controlDict", "constant/turbulenceProperties")


def cells_from_owner(owner: Path) -> int:
    """Cell count read off ``owner``: highest owning-cell label plus one."""
    top = -1
    started = False
    for line in owner.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not started:
            if s == "(":
                started = True
            continue
        if s == ")":
            break
        if s:
            try:
                top = max(top, int(s))
            except ValueError:
                continue
    if top < 0:
        raise SystemExit(f"REFUSED: no cell labels readable in {owner}")
    return top + 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True,
                    help="scratch directory to write constant/polyMesh under")
    args = ap.parse_args()
    out = Path(args.out)

    if not SOURCE_POLYMESH.is_dir():
        print(f"REFUSED: source polyMesh not on disk: {SOURCE_POLYMESH}",
              file=sys.stderr)
        return 2
    for tell in CASE_TELLS:
        if (out / tell).exists():
            print(f"REFUSED: {out} holds {tell}; it looks like a real case "
                  f"directory and nothing may mesh into one", file=sys.stderr)
            return 2

    target = out / "constant" / "polyMesh"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    copied = 0
    for src in sorted(SOURCE_POLYMESH.iterdir()):
        if not src.is_file():
            continue
        if src.suffix == ".gz":
            with gzip.open(src, "rb") as fin, \
                    open(target / src.stem, "wb") as fout:
                shutil.copyfileobj(fin, fout)
        else:
            shutil.copyfile(src, target / src.name)
        copied += 1
    if copied == 0:
        print(f"REFUSED: nothing to copy in {SOURCE_POLYMESH}",
              file=sys.stderr)
        return 2

    got = cells_from_owner(target / "owner")
    if got != EXPECT_CELLS:
        print(f"REFUSED: reproduced grid reads {got} cells; the solved grid "
              f"holds {EXPECT_CELLS}", file=sys.stderr)
        return 2
    print(f"reproduced the solved A2 grid: {got} cells, {copied} polyMesh "
          f"files, from {SOURCE_POLYMESH} into {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
