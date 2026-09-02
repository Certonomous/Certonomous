#!/usr/bin/env python3
"""THE LIVE MESHER OF THE TWO THERMAL DEMO ACTS (motor duct, battery module).

Sanaa's demo standard requires the meshing stage to run a REAL mesher rather
than speak the word. Both thermal source runs were meshed by ``blockMesh``
from a ``system/blockMeshDict`` that still sits, frozen, inside each solved
case. This script reruns that exact dictionary in a throwaway case UNDER the
scratch output directory, then moves only ``constant/polyMesh`` up into the
scratch root and deletes the throwaway case.

WHY THE DANCE. ``demo_sequencer._unsafe_work_dir`` refuses to mesh into any
directory holding ``system/controlDict`` (a mesher writing a fresh mesh into
a landed case destroys the age-guard provenance of a result that cannot be
re-solved). ``blockMesh`` cannot run without a ``system/controlDict``. So the
controlDict lives only inside a temporary subdirectory that is deleted before
this script exits, and the scratch root the sequencer inspects afterwards
holds ``constant/polyMesh`` and nothing that marks a case.

WHAT IS REPRODUCED IS CHECKABLE, NOT ASSERTED. The sequencer reads the cell
count back off the mesh just written (``constant/polyMesh/owner``) and
refuses to show a grid that does not match the solved case's own count. This
script additionally takes ``--expect-cells`` and refuses on a mismatch, so a
drifted dictionary fails HERE, with a sentence, rather than at stage time.

The dictionary is READ from the solved case and never written back; nothing
under ``--case`` is modified. Everything written lands under ``--out``.

    python3 scripts/build_conjugate_demo_mesh.py \
        --case verification/runs/T-family/T23_runs/T23_P305_U20 \
        --out  verification/runs/T-family/T23_runs/demo_mesh_work \
        --expect-cells 39680
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

MINIMAL_CONTROL_DICT = """\
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
application     blockMesh;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
"""


def count_cells(poly: Path) -> int:
    """Cells of a polyMesh, read off ``owner``: highest label plus one."""
    owner = poly / "owner"
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
        raise SystemExit(f"could not read a cell count from {owner}")
    return top + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True,
                        help="The SOLVED case whose system/blockMeshDict is "
                             "rerun. Read only; never written.")
    parser.add_argument("--out", required=True,
                        help="Scratch root. Receives constant/polyMesh and "
                             "nothing that marks a case.")
    parser.add_argument("--expect-cells", type=int, default=None,
                        help="Refuse unless the written mesh holds exactly "
                             "this many cells.")
    args = parser.parse_args()

    case = Path(args.case).resolve()
    out = Path(args.out).resolve()
    if out == case or case in out.parents:
        raise SystemExit("the scratch root may not be the solved case")
    source_dict = case / "system" / "blockMeshDict"
    if not source_dict.is_file():
        raise SystemExit(f"{source_dict} is not on disk; nothing to rerun")
    if not Path(FOAM_BASHRC).is_file():
        raise SystemExit(f"OpenFOAM environment not found at {FOAM_BASHRC}")

    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_blockMesh_tmp_case"
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / "system").mkdir(parents=True)
    (tmp / "constant").mkdir(parents=True)
    shutil.copy2(source_dict, tmp / "system" / "blockMeshDict")
    (tmp / "system" / "controlDict").write_text(MINIMAL_CONTROL_DICT,
                                                encoding="utf-8")
    try:
        done = subprocess.run(
            ["bash", "-c",
             f"set +u; source {FOAM_BASHRC} >/dev/null 2>&1 || true; set -u; "
             f"command -v blockMesh >/dev/null || exit 3; "
             f"blockMesh -case {tmp}"],
            capture_output=True, text=True, timeout=300)
        if done.returncode == 3:
            raise SystemExit("blockMesh is not on this machine after sourcing "
                             "the OpenFOAM environment")
        if done.returncode != 0:
            sys.stderr.write(done.stdout[-2000:] + done.stderr[-2000:])
            raise SystemExit(f"blockMesh exited {done.returncode}")

        written = tmp / "constant" / "polyMesh"
        if not written.is_dir():
            raise SystemExit("blockMesh exited 0 and wrote no mesh")
        cells = count_cells(written)
        if args.expect_cells is not None and cells != args.expect_cells:
            raise SystemExit(
                f"the rebuilt mesh holds {cells} cells where the solved grid "
                f"holds {args.expect_cells}; the dictionary and the solved "
                f"case have diverged and this mesh will not be shown")

        target = out / "constant" / "polyMesh"
        if target.exists():
            shutil.rmtree(target)
        (out / "constant").mkdir(exist_ok=True)
        shutil.move(str(written), str(target))
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)

    print(f"wrote {out / 'constant' / 'polyMesh'}: {cells} cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
