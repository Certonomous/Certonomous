"""Generate a watertight NACA 0015 submarine-sail surface as binary STL.

The sail is a straight-lofted finite-span fin: NACA 0015 section, chord
1.2 m along +X (leading edge at x=0), thickness along Y, span 1.8 m along
+Z with a flat root cap at z=0 and a flat tip cap at z=1.8 m. The closed
trailing-edge thickness polynomial (-0.1036 x^4 term) is used so the loop
closes to a single TE point and the surface is watertight by construction.

    python scripts/make_naca0015.py [out.stl ...]

With no arguments it writes the three staged copies:
    sdk/geometry/naca0015_sail.stl
    the operator copy set (`lab_paths.DEMO_SURFACES`)
    models/curriculum/naca0015_sail/naca0015_sail.stl
"""

from __future__ import annotations

import math
import struct
import sys
from pathlib import Path

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2] / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

CHORD = 1.2          # m
SPAN = 1.8           # m
N_CHORD = 110        # stations LE -> TE per side (cosine spaced)
N_SPAN = 48          # spanwise stations root -> tip

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUTS = [
    REPO / "sdk" / "geometry" / "naca0015_sail.stl",
    # R5 sends `demo-surfaces/` to `cases/demo-surfaces/` in MOVE_MAP batch 6.
    # THIS IS A GENERATOR AND THE CONSTANT IS ITS OUTPUT PATH: a literal here
    # would re-create the old directory on the next run and leave the copy set
    # the server actually reads frozen at its last build.
    lab_paths.DEMO_SURFACES / "naca0015_sail.stl",
    REPO / "models" / "curriculum" / "naca0015_sail" / "naca0015_sail.stl",
]


def thickness(xc: float, t: float = 0.15) -> float:
    """NACA half-thickness, closed trailing edge (-0.1036 quartic term)."""
    return 5.0 * t * (0.2969 * math.sqrt(xc) - 0.1260 * xc
                      - 0.3516 * xc ** 2 + 0.2843 * xc ** 3
                      - 0.1036 * xc ** 4)


def section_loop(chord: float) -> list[tuple[float, float]]:
    """Airfoil outline as one closed CCW loop (viewed from +Z).

    TE -> upper surface -> LE -> lower surface -> (back to TE). The LE and
    TE points appear once each, so the loop has 2*N_CHORD - 2 points.
    """
    xs = [0.5 * (1.0 - math.cos(math.pi * i / (N_CHORD - 1)))
          for i in range(N_CHORD)]                     # cosine spacing, 0..1
    upper = [(x * chord, thickness(x) * chord) for x in xs]
    lower = [(x * chord, -thickness(x) * chord) for x in xs]
    loop = list(reversed(upper))          # TE -> LE over the top
    loop += lower[1:-1]                   # LE -> TE underneath, ends dropped
    return loop


def build_triangles() -> list[tuple[tuple[float, float, float], ...]]:
    loop = section_loop(CHORD)
    ring = len(loop)
    zs = [SPAN * k / (N_SPAN - 1) for k in range(N_SPAN)]

    tris: list[tuple[tuple[float, float, float], ...]] = []

    def pt(i: int, k: int) -> tuple[float, float, float]:
        x, y = loop[i % ring]
        return (x, y, zs[k])

    # Side walls: CCW loop + outward normals from the (a, b, c) ordering.
    for k in range(N_SPAN - 1):
        for i in range(ring):
            a, b = pt(i, k), pt(i + 1, k)
            c, d = pt(i + 1, k + 1), pt(i, k + 1)
            tris.append((a, b, c))
            tris.append((a, c, d))

    # Flat caps: pair the upper/lower points of each chordwise station.
    xs = [0.5 * (1.0 - math.cos(math.pi * i / (N_CHORD - 1)))
          for i in range(N_CHORD)]
    for z, want_up in ((0.0, False), (SPAN, True)):   # root -Z, tip +Z
        for j in range(N_CHORD - 1):
            x0, x1 = xs[j] * CHORD, xs[j + 1] * CHORD
            y0 = thickness(xs[j]) * CHORD
            y1 = thickness(xs[j + 1]) * CHORD
            quad = [(x0, y0, z), (x1, y1, z), (x1, -y1, z), (x0, -y0, z)]
            for tri in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
                (ax, ay, _), (bx, by, _), (cx, cy, _) = tri
                cross_z = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
                if abs(cross_z) < 1e-14:
                    continue                              # degenerate at LE/TE
                if (cross_z > 0) != want_up:
                    tri = (tri[0], tri[2], tri[1])
                tris.append(tri)
    return tris


def write_stl(path: Path, tris) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"naca0015_sail chord 1.2m span 1.8m".ljust(80, b"\0"))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
            vx = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
            n = (ux[1] * vx[2] - ux[2] * vx[1],
                 ux[2] * vx[0] - ux[0] * vx[2],
                 ux[0] * vx[1] - ux[1] * vx[0])
            mag = math.sqrt(sum(v * v for v in n)) or 1.0
            fh.write(struct.pack("<3f", *(v / mag for v in n)))
            for p in (a, b, c):
                fh.write(struct.pack("<3f", *p))
            fh.write(struct.pack("<H", 0))


def main(argv: list[str]) -> int:
    outputs = [Path(a) for a in argv] or DEFAULT_OUTPUTS
    tris = build_triangles()
    for out in outputs:
        write_stl(out, tris)
        print(f"wrote {out} ({len(tris)} triangles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
