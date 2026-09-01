#!/usr/bin/env python3
"""THE MESHER THE SHOCK-REFLECTION SCREEN RUNS LIVE.

Sanaa's demo standard requires the meshing stage to run a REAL mesher rather
than to speak the word. This is that mesher for the double-Mach-reflection
benchmark: it writes an OpenFOAM ``constant/polyMesh`` for the pre-registered
domain, from the pre-registered numbers, and nothing else.

WHY NOT ``blockMesh``, WHICH IS WHAT SOLVED THE CASE. Two reasons, and the
first is a safety property rather than a preference.

* ``blockMesh`` needs a ``system/controlDict`` in the directory it runs in.
  The sequencer refuses to mesh into any directory holding one, because a
  mesher writing a fresh ``constant/polyMesh`` into a landed case destroys the
  provenance the strict completion rule's age guard rests on. A mesher that
  requires the very file that marks a directory unsafe can never be run by
  that stage at all: the first run would create the ``controlDict`` and every
  run after it would be skipped. So the live mesher writes the mesh directly
  and leaves no case behind, exactly as the jet-flap act's builder does.
* It needs no OpenFOAM on the path, so the stage cannot fail on camera for a
  reason that has nothing to do with the grid.

WHAT IT REPRODUCES, AND HOW THAT IS CHECKED. The graded run's own mesh, at
1/120, is 57,600 cells over 116,402 points with 114,600 internal faces and
six patches. This writes the same topology from the same domain constants; the
sequencer then reads the cell count back OFF THE MESH JUST WRITTEN and refuses
to show a grid that is not the one the numbers came from. The counts are
therefore a checkable claim, not a comment:

    python3 cases/DMR_shock_reflection/build_dmr_mesh.py \
        --out <scratch dir> --resolution 120

Domain and constants are the pre-registration's (``DMR_PREREGISTRATION.md``
§1): [0,4] x [0,1], one cell thick, the inclined shock entering through
x0 = 1/6, uniform spacing 1/N in both directions. The bottom boundary splits
at x0 into the fixed-inflow strip ahead of the shock foot and the reflecting
wall behind it -- that split is the physics of the case and is why the grid is
built here rather than taken as a plain box.

STARTS NO SOLVER, READS NO RUN TREE, WRITES ONLY UNDER ``--out``.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

#: The pre-registered domain (DMR_PREREGISTRATION.md §1). Not re-derived
#: anywhere else in this file, so a change here changes the whole mesh.
X_MAX = 4.0
Y_MAX = 1.0
Z_THICK = 0.01
X0 = 1.0 / 6.0

HEADER = """\
FoamFile
{
    version     2.0;
    format      ascii;
    class       %s;
    location    "constant/polyMesh";
    object      %s;
}
"""


def build(resolution: int):
    """Return every array the mesh is made of, for ``resolution`` cells/unit.

    Pure: it touches no disk. The writer below is the only thing that does,
    which keeps the topology testable without a directory.
    """
    nx = int(round(X_MAX * resolution))
    ny = int(round(Y_MAX * resolution))
    n_inflow = int(round(X0 * resolution))
    if abs(X0 * resolution - n_inflow) > 1e-9:
        raise SystemExit(
            f"resolution {resolution} does not put a mesh node on the shock "
            f"foot at x = 1/6; the reflecting wall would start half a cell "
            f"away from where the case says it starts")

    xs = [X_MAX * i / nx for i in range(nx + 1)]
    ys = [Y_MAX * j / ny for j in range(ny + 1)]
    zs = [0.0, Z_THICK]

    points = [(xs[i], ys[j], zs[k])
              for k in range(2) for j in range(ny + 1) for i in range(nx + 1)]

    def pt(i, j, k):
        return k * (nx + 1) * (ny + 1) + j * (nx + 1) + i

    def cell(i, j):
        return j * nx + i

    # -- internal faces, in upper-triangular order -------------------------
    # OpenFOAM requires the internal faces sorted by owner then neighbour, and
    # every face normal pointing FROM the owner TO the neighbour. Both are
    # properties of the ordering below rather than of a later sort of the
    # written file, because a file that is merely written in the right order
    # cannot be checked afterwards.
    internal = []
    for j in range(ny):
        for i in range(nx - 1):
            internal.append((cell(i, j), cell(i + 1, j),
                             (pt(i + 1, j, 0), pt(i + 1, j + 1, 0),
                              pt(i + 1, j + 1, 1), pt(i + 1, j, 1))))
    for j in range(ny - 1):
        for i in range(nx):
            internal.append((cell(i, j), cell(i, j + 1),
                             (pt(i, j + 1, 0), pt(i, j + 1, 1),
                              pt(i + 1, j + 1, 1), pt(i + 1, j + 1, 0))))
    internal.sort(key=lambda t: (t[0], t[1]))
    faces_int = [t[2] for t in internal]
    owner = [t[0] for t in internal]
    neighbour = [t[1] for t in internal]

    # -- boundary faces, outward normals -----------------------------------
    inlet = [(pt(0, j, 0), pt(0, j, 1), pt(0, j + 1, 1), pt(0, j + 1, 0))
             for j in range(ny)]
    outlet = [(pt(nx, j, 0), pt(nx, j + 1, 0), pt(nx, j + 1, 1), pt(nx, j, 1))
              for j in range(ny)]
    bottom = [(pt(i, 0, 0), pt(i + 1, 0, 0), pt(i + 1, 0, 1), pt(i, 0, 1))
              for i in range(nx)]
    top = [(pt(i, ny, 0), pt(i, ny, 1), pt(i + 1, ny, 1), pt(i + 1, ny, 0))
           for i in range(nx)]
    back = [(pt(i, j + 1, 0), pt(i + 1, j + 1, 0), pt(i + 1, j, 0), pt(i, j, 0))
            for j in range(ny) for i in range(nx)]
    front = [(pt(i, j, 1), pt(i + 1, j, 1), pt(i + 1, j + 1, 1),
              pt(i, j + 1, 1))
             for j in range(ny) for i in range(nx)]

    patches = [
        ("inlet", "patch", inlet, [cell(0, j) for j in range(ny)]),
        ("outlet", "patch", outlet, [cell(nx - 1, j) for j in range(ny)]),
        ("bottomInflow", "patch", bottom[:n_inflow],
         [cell(i, 0) for i in range(n_inflow)]),
        ("rampWall", "symmetryPlane", bottom[n_inflow:],
         [cell(i, 0) for i in range(n_inflow, nx)]),
        ("top", "patch", top, [cell(i, ny - 1) for i in range(nx)]),
        ("frontAndBack", "empty", back + front,
         [cell(i, j) for j in range(ny) for i in range(nx)]
         + [cell(i, j) for j in range(ny) for i in range(nx)]),
    ]

    owner_all = list(owner)
    for _, _, _, owners in patches:
        owner_all.extend(owners)

    return {"points": points, "faces_int": faces_int, "owner": owner_all,
            "neighbour": neighbour, "patches": patches,
            "n_cells": nx * ny, "nx": nx, "ny": ny,
            "n_internal": len(faces_int),
            "n_faces": len(faces_int) + sum(len(f) for _, _, f, _ in patches)}


def write(out_dir: Path, mesh: dict) -> Path:
    """Write the mesh under ``out_dir/constant/polyMesh`` and return that."""
    poly = Path(out_dir) / "constant" / "polyMesh"
    os.makedirs(poly, exist_ok=True)

    with open(poly / "points", "w", encoding="utf-8") as fh:
        fh.write(HEADER % ("vectorField", "points"))
        fh.write("\n%d\n(\n" % len(mesh["points"]))
        fh.write("".join("(%.10g %.10g %.10g)\n" % p for p in mesh["points"]))
        fh.write(")\n")

    with open(poly / "faces", "w", encoding="utf-8") as fh:
        fh.write(HEADER % ("faceList", "faces"))
        fh.write("\n%d\n(\n" % mesh["n_faces"])
        fh.write("".join("4(%d %d %d %d)\n" % f for f in mesh["faces_int"]))
        for _, _, faces, _ in mesh["patches"]:
            fh.write("".join("4(%d %d %d %d)\n" % f for f in faces))
        fh.write(")\n")

    for name, values in (("owner", mesh["owner"]),
                         ("neighbour", mesh["neighbour"])):
        with open(poly / name, "w", encoding="utf-8") as fh:
            fh.write(HEADER % ("labelList", name))
            fh.write("\n%d\n(\n" % len(values))
            fh.write("".join("%d\n" % v for v in values))
            fh.write(")\n")

    with open(poly / "boundary", "w", encoding="utf-8") as fh:
        fh.write(HEADER % ("polyBoundaryMesh", "boundary"))
        fh.write("\n%d\n(\n" % len(mesh["patches"]))
        start = mesh["n_internal"]
        for name, ptype, faces, _ in mesh["patches"]:
            fh.write("    %s\n    {\n        type            %s;\n"
                     % (name, ptype))
            if ptype in ("empty", "symmetryPlane", "wall"):
                fh.write("        inGroups        1(%s);\n" % ptype)
            fh.write("        nFaces          %d;\n"
                     "        startFace       %d;\n    }\n"
                     % (len(faces), start))
            start += len(faces)
        fh.write(")\n")
    return poly


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True,
                        help="directory to write constant/polyMesh into")
    parser.add_argument("--resolution", type=int, default=120,
                        help="cells per unit length (120 = the primary grid)")
    args = parser.parse_args()

    mesh = build(args.resolution)
    poly = write(Path(args.out), mesh)
    print("-- POLYMESH WRITTEN --")
    print("  %s" % poly)
    print("  cells %d (%d x %d)   points %d   internal faces %d   faces %d"
          % (mesh["n_cells"], mesh["nx"], mesh["ny"], len(mesh["points"]),
             mesh["n_internal"], mesh["n_faces"]))
    for name, ptype, faces, _ in mesh["patches"]:
        print("  patch %-13s %-14s %d" % (name, ptype, len(faces)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
