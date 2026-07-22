"""Parametric generators for the Tier-0 geometry curriculum.

Every surface here is written from scratch, so the lab owns it outright — no
license attaches to a triangle we placed ourselves.  The bodies are the
canonical validation cases of external aerodynamics: a sphere, a finite
cylinder, a cube, a flat plate at incidence, the Ahmed automotive reference
body at two rear-slant angles, and NACA 0012 / 4412 sections extruded into
finite wings.  Each is emitted as a watertight binary STL so snappyHexMesh can
wrap a volume mesh around it without repair.

``trimesh`` is used if importable, but nothing here needs it: the generators
build indexed triangle meshes with plain ``numpy`` and a hand-written binary
STL writer.  Watertightness is a property we can prove on the indexed mesh —
every edge shared by exactly two triangles — so the tests check closure
directly rather than trusting a library.

    python generate.py            # write every body under models/curriculum/
    python generate.py --list     # name the bodies without writing anything
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np

CURRICULUM_ROOT = Path(__file__).resolve().parent

# Air at room conditions is assumed throughout the curriculum; the reference
# files carry the Reynolds number each published value was measured at.
DEG = math.pi / 180.0


# --------------------------------------------------------------------------
# Mesh utilities
# --------------------------------------------------------------------------

def _face_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tris = vertices[faces]
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    lengths[lengths == 0.0] = 1.0
    return normals / lengths[:, None]


def write_stl(path: str | Path, vertices, faces, *, name: str = "body") -> Path:
    """Write an indexed triangle mesh as a binary STL."""
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    normals = _face_normals(vertices, faces)
    tris = vertices[faces].astype(np.float32)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        header = f"certonomous curriculum: {name}".encode("ascii", "replace")
        stream.write(header[:80].ljust(80, b"\0"))
        stream.write(struct.pack("<I", len(faces)))
        for i in range(len(faces)):
            stream.write(struct.pack("<3f", *normals[i].astype(np.float32)))
            stream.write(tris[i].tobytes())
            stream.write(struct.pack("<H", 0))
    return path


def is_watertight(faces) -> bool:
    """True when every edge is shared by exactly two triangles.

    That is the topological definition of a closed manifold surface, and it is
    exactly what snappyHexMesh needs to decide inside from outside.  It is
    checked on the indexed mesh, where shared vertices give shared edges.
    """
    faces = np.asarray(faces, dtype=np.int64)
    counts: dict[tuple[int, int], int] = {}
    for tri in faces:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            key = (int(a), int(b)) if a < b else (int(b), int(a))
            counts[key] = counts.get(key, 0) + 1
    return bool(counts) and all(count == 2 for count in counts.values())


def _loft(sections, *, closed_loop: bool = True,
          cap_first: bool = True, cap_last: bool = True):
    """Skin a sequence of equal-length cross-section loops into a closed shell.

    Consecutive loops are joined by triangle strips; the open ends are closed
    by a fan to each end loop's centroid.  Every side edge is shared by two
    strip triangles and every end edge by one strip and one fan triangle, so a
    fully capped loft is watertight by construction.
    """
    verts: list[list[float]] = []
    faces: list[list[int]] = []
    index: list[list[int]] = []
    m = len(sections[0])
    for sec in sections:
        base = len(verts)
        verts.extend([list(map(float, p)) for p in sec])
        index.append(list(range(base, base + m)))

    span = m if closed_loop else m - 1
    for s in range(len(sections) - 1):
        a, b = index[s], index[s + 1]
        for j in range(span):
            k = (j + 1) % m
            faces.append([a[j], a[k], b[k]])
            faces.append([a[j], b[k], b[j]])

    if cap_first:
        loop = sections[0]
        centre = [sum(p[i] for p in loop) / m for i in range(3)]
        c = len(verts)
        verts.append(centre)
        a = index[0]
        for j in range(m):
            faces.append([c, a[(j + 1) % m], a[j]])
    if cap_last:
        loop = sections[-1]
        centre = [sum(p[i] for p in loop) / m for i in range(3)]
        c = len(verts)
        verts.append(centre)
        a = index[-1]
        for j in range(m):
            faces.append([c, a[j], a[(j + 1) % m]])
    return np.asarray(verts, dtype=np.float64), np.asarray(faces, dtype=np.int64)


# --------------------------------------------------------------------------
# Generators — each returns (vertices, faces)
# --------------------------------------------------------------------------

def sphere(diameter: float = 1.0, *, n_lat: int = 50, n_lon: int = 52):
    """A smooth UV sphere, watertight through single poles at each end."""
    radius = diameter / 2.0
    verts: list[list[float]] = []
    faces: list[list[int]] = []

    top = 0
    verts.append([0.0, 0.0, radius])
    ring_start: list[int] = []
    for i in range(1, n_lat):
        theta = math.pi * i / n_lat
        z = radius * math.cos(theta)
        r = radius * math.sin(theta)
        ring_start.append(len(verts))
        for j in range(n_lon):
            phi = 2 * math.pi * j / n_lon
            verts.append([r * math.cos(phi), r * math.sin(phi), z])
    bottom = len(verts)
    verts.append([0.0, 0.0, -radius])

    first = ring_start[0]
    for j in range(n_lon):
        faces.append([top, first + j, first + (j + 1) % n_lon])
    for i in range(len(ring_start) - 1):
        a, b = ring_start[i], ring_start[i + 1]
        for j in range(n_lon):
            k = (j + 1) % n_lon
            faces.append([a + j, b + j, b + k])
            faces.append([a + j, b + k, a + k])
    last = ring_start[-1]
    for j in range(n_lon):
        faces.append([bottom, last + (j + 1) % n_lon, last + j])
    return np.asarray(verts, dtype=np.float64), np.asarray(faces, dtype=np.int64)


def cylinder(diameter: float = 0.4, length: float = 2.0, *, segments: int = 64):
    """A finite circular cylinder (length/diameter = 5), flat-capped ends.

    The axis lies along x; the reference file orients the freestream across it
    so the body is solved in crossflow, which is the configuration its
    published drag coefficient belongs to.
    """
    radius = diameter / 2.0
    half = length / 2.0
    ring = []
    for j in range(segments):
        phi = 2 * math.pi * j / segments
        ring.append((radius * math.cos(phi), radius * math.sin(phi)))
    front = [[-half, y, z] for (y, z) in ring]
    back = [[half, y, z] for (y, z) in ring]
    return _loft([front, back], closed_loop=True, cap_first=True, cap_last=True)


def cube(side: float = 1.0):
    """An axis-aligned cube — the archetypal sharp-edged bluff body."""
    h = side / 2.0
    v = np.array([
        [-h, -h, -h], [h, -h, -h], [h, h, -h], [-h, h, -h],
        [-h, -h, h], [h, -h, h], [h, h, h], [-h, h, h],
    ], dtype=np.float64)
    quads = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3),
    ]
    faces = []
    for a, b, c, d in quads:
        faces.append([a, b, c])
        faces.append([a, c, d])
    return v, np.asarray(faces, dtype=np.int64)


def flat_plate(chord: float = 1.0, span: float = 1.0, thickness: float = 0.02,
               angle_deg: float = 5.0):
    """A thin rectangular plate pitched to a stated angle of attack.

    Built as a slender box so it stays watertight, then rotated about the
    span axis so the chord meets the oncoming flow at ``angle_deg``.
    """
    c, s, t = chord, span / 2.0, thickness / 2.0
    box = np.array([
        [-c / 2, -s, -t], [c / 2, -s, -t], [c / 2, s, -t], [-c / 2, s, -t],
        [-c / 2, -s, t], [c / 2, -s, t], [c / 2, s, t], [-c / 2, s, t],
    ], dtype=np.float64)
    a = angle_deg * DEG
    rot = np.array([
        [math.cos(a), 0.0, math.sin(a)],
        [0.0, 1.0, 0.0],
        [-math.sin(a), 0.0, math.cos(a)],
    ])
    box = box @ rot.T
    quads = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3),
    ]
    faces = []
    for p, q, r, u in quads:
        faces.append([p, q, r])
        faces.append([p, r, u])
    return box, np.asarray(faces, dtype=np.int64)


def ahmed_body(slant_deg: float = 25.0, *, length: float = 1.044,
               width: float = 0.389, height: float = 0.288,
               front_radius: float = 0.100, slant_length: float = 0.222):
    """The Ahmed reference body at a chosen rear-slant angle.

    Canonical dimensions (Ahmed, Ramm & Faltin 1984): 1044 x 389 x 288 mm,
    100 mm front-edge radius, 222 mm slant.  The stilts of the original wind-
    tunnel model are omitted so the surface is a single closed shell; the
    published drag coefficient is dominated by the rear slant and base, which
    are reproduced exactly.

    Construction is a loft of rectangular cross-sections along the length.
    Insetting the section near the nose rounds all four front edges; lowering
    the section top over the last ``slant_length*cos`` metres cuts the slant.
    """
    phi = slant_deg * DEG
    x_slant = length - slant_length * math.cos(phi)
    tan_phi = math.tan(phi)
    r = front_radius

    def inset(x: float) -> float:
        if x >= r:
            return 0.0
        d = r - x
        return r - math.sqrt(max(0.0, r * r - d * d))

    def top(x: float) -> float:
        return height if x <= x_slant else height - (x - x_slant) * tan_phi

    xs = sorted(set(
        list(np.linspace(0.0, r, 14))
        + list(np.linspace(r, x_slant, 6))
        + list(np.linspace(x_slant, length, 16))))

    sections = []
    for x in xs:
        d = inset(x)
        a = width / 2.0 - d
        zb = d
        zt = top(x) - d
        sections.append([
            [x, -a, zb], [x, a, zb], [x, a, zt], [x, -a, zt],
        ])
    return _loft(sections, closed_loop=True, cap_first=True, cap_last=True)


def _naca4(code: str, x: np.ndarray):
    """Upper/lower coordinates of a 4-digit NACA section on a closed trailing edge."""
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0
    # Closed-trailing-edge thickness distribution (last coefficient -0.1036).
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2
                  + 0.2843 * x ** 3 - 0.1036 * x ** 4)
    if m == 0.0 or p == 0.0:
        yc = np.zeros_like(x)
        dyc = np.zeros_like(x)
    else:
        yc = np.where(x < p,
                      m / p ** 2 * (2 * p * x - x ** 2),
                      m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x ** 2))
        dyc = np.where(x < p,
                       2 * m / p ** 2 * (p - x),
                       2 * m / (1 - p) ** 2 * (p - x))
    theta = np.arctan(dyc)
    xu = x - yt * np.sin(theta)
    zu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    zl = yc - yt * np.cos(theta)
    return (xu, zu), (xl, zl)


def naca_wing(code: str = "0012", *, chord: float = 1.0, span: float = 3.0,
              n_chord: int = 90):
    """A NACA 4-digit section extruded spanwise into a finite wing.

    The section is a single closed loop (upper leading edge to trailing edge,
    then lower back to the leading edge, trailing edge closed) skinned between
    the two wing tips and capped, so the wing is watertight.
    """
    beta = np.linspace(0.0, math.pi, n_chord)
    x = (1 - np.cos(beta)) / 2.0
    (xu, zu), (xl, zl) = _naca4(code, x)

    loop2d = [(xu[i], zu[i]) for i in range(n_chord)]
    loop2d += [(xl[i], zl[i]) for i in range(n_chord - 2, 0, -1)]
    loop2d = [(cx * chord, cz * chord) for (cx, cz) in loop2d]

    half = span / 2.0
    root = [[cx, -half, cz] for (cx, cz) in loop2d]
    tip = [[cx, half, cz] for (cx, cz) in loop2d]
    return _loft([root, tip], closed_loop=True, cap_first=True, cap_last=True)


# --------------------------------------------------------------------------
# Registry of bodies to write
# --------------------------------------------------------------------------

BODIES = {
    "sphere": lambda: sphere(),
    "cylinder": lambda: cylinder(),
    "cube": lambda: cube(),
    "flat_plate": lambda: flat_plate(angle_deg=5.0),
    "ahmed_25": lambda: ahmed_body(slant_deg=25.0),
    "ahmed_35": lambda: ahmed_body(slant_deg=35.0),
    "naca0012_wing": lambda: naca_wing("0012"),
    "naca4412_wing": lambda: naca_wing("4412"),
}


def generate(name: str, root: Path | None = None) -> Path:
    """Write one body's STL under ``models/curriculum/<name>/<name>.stl``."""
    if name not in BODIES:
        raise KeyError(f"unknown curriculum body: {name!r}")
    root = Path(root) if root else CURRICULUM_ROOT
    vertices, faces = BODIES[name]()
    if not is_watertight(faces):
        raise ValueError(f"generated {name} is not watertight — refusing to write it")
    return write_stl(root / name / f"{name}.stl", vertices, faces, name=name)


def generate_all(root: Path | None = None) -> dict[str, Path]:
    written = {}
    for name in BODIES:
        written[name] = generate(name, root)
    return written


if __name__ == "__main__":
    import sys

    if "--list" in sys.argv:
        for name in BODIES:
            print(name)
    else:
        for name, path in generate_all().items():
            vertices, faces = BODIES[name]()
            print(f"{name:16s} {len(faces):6d} triangles  "
                  f"watertight={is_watertight(faces)}  -> {path.relative_to(CURRICULUM_ROOT)}")
