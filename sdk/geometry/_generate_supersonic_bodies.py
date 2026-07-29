"""One-off generator for the five bodies STEP 4 asks for: the vortex-shedding
cylinder (D=1), the compression wedge (theta=15deg ramp, Lramp=1), the
Taylor-Maccoll cone (theta_c=10deg half-angle, axial length 1), the diamond
airfoil (eps=7.125deg half-angle, chord 1), and the hypersonic blunt cylinder
(R=1). Dimensions match exactly what F3/F4/mega-batch's case builders solved
(see sdk/workflows/supersonic_wedge.py etc.) -- these STL files are the
control-room viewport's display asset for those bodies, not the CFD mesh
itself (the acts mesh their own parametric blockMeshDict, as the F3/F4
campaigns did).

Run once: ``python3 _generate_supersonic_bodies.py``. Not imported by the acts.
"""
import math
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write_binary_stl(path: Path, triangles: list[tuple]) -> None:
    """triangles: list of ((x1,y1,z1),(x2,y2,z2),(x3,y3,z3))."""
    with path.open("wb") as f:
        f.write(b"\x00" * 80)
        f.write(struct.pack("<I", len(triangles)))
        for a, b, c in triangles:
            ux, uy, uz = _normal(a, b, c)
            f.write(struct.pack("<3f", ux, uy, uz))
            for v in (a, b, c):
                f.write(struct.pack("<3f", *v))
            f.write(struct.pack("<H", 0))


def _normal(a, b, c):
    ux, uy, uz = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    vx, vy, vz = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / n, ny / n, nz / n


def cylinder(radius: float, span: float, n: int = 48) -> list:
    """Circular cylinder, axis along z, cross-section circle in x-y, centred
    at the origin, extruded from z=-span/2 to z=+span/2."""
    tris = []
    z0, z1 = -span / 2, span / 2
    pts = [(radius * math.cos(2 * math.pi * i / n),
            radius * math.sin(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        tris.append(((x0, y0, z0), (x1, y1, z0), (x1, y1, z1)))
        tris.append(((x0, y0, z0), (x1, y1, z1), (x0, y0, z1)))
        tris.append(((0.0, 0.0, z0), (x1, y1, z0), (x0, y0, z0)))
        tris.append(((0.0, 0.0, z1), (x0, y0, z1), (x1, y1, z1)))
    return tris


def wedge(lramp: float, theta_deg: float, span: float, flat_ahead: float = 0.15) -> list:
    """Right-triangle compression ramp: flat plate from x=-flat_ahead to x=0
    at y=0, then a ramp inclined at theta from x=0 to x=lramp rising to
    y=lramp*tan(theta); the solved oblique-shock surface. Extruded along z."""
    theta = math.radians(theta_deg)
    h = lramp * math.tan(theta)
    z0, z1 = -span / 2, span / 2
    profile = [(-flat_ahead, 0.0), (0.0, 0.0), (lramp, h)]
    tris = []
    for (x0, y0), (x1, y1) in zip(profile, profile[1:]):
        tris.append(((x0, y0, z0), (x1, y1, z0), (x1, y1, z1)))
        tris.append(((x0, y0, z0), (x1, y1, z1), (x0, y0, z1)))
    # base (underside) and end caps so the body reads as solid in the viewport
    tris.append(((-flat_ahead, 0.0, z0), (lramp, h, z0), (lramp, 0.0, z0)))
    tris.append(((-flat_ahead, 0.0, z0), (-flat_ahead, 0.0, z1), (lramp, 0.0, z1)))
    tris.append(((-flat_ahead, 0.0, z0), (lramp, 0.0, z1), (lramp, 0.0, z0)))
    return tris


def cone(x_max: float, theta_c_deg: float, n: int = 48) -> list:
    """Axisymmetric cone, apex at the origin, axis along +x, half-angle
    theta_c, base at x=x_max."""
    theta_c = math.radians(theta_c_deg)
    r_max = x_max * math.tan(theta_c)
    apex = (0.0, 0.0, 0.0)
    base_pts = [(x_max, r_max * math.cos(2 * math.pi * i / n),
                r_max * math.sin(2 * math.pi * i / n)) for i in range(n)]
    tris = []
    for i in range(n):
        p0, p1 = base_pts[i], base_pts[(i + 1) % n]
        tris.append((apex, p0, p1))
        tris.append(((x_max, 0.0, 0.0), p1, p0))
    return tris


def diamond_airfoil(chord: float, eps_deg: float, span: float) -> list:
    """Symmetric double-wedge (diamond) airfoil: LE at (0,0), max thickness at
    mid-chord y=+-chord*tan(eps), TE at (chord,0). Extruded along z."""
    eps = math.radians(eps_deg)
    half_t = (chord / 2) * math.tan(eps)
    top = [(0.0, 0.0), (chord / 2, half_t), (chord, 0.0)]
    bot = [(0.0, 0.0), (chord / 2, -half_t), (chord, 0.0)]
    z0, z1 = -span / 2, span / 2
    tris = []
    for profile in (top, bot):
        for (x0, y0), (x1, y1) in zip(profile, profile[1:]):
            tris.append(((x0, y0, z0), (x1, y1, z0), (x1, y1, z1)))
            tris.append(((x0, y0, z0), (x1, y1, z1), (x0, y0, z1)))
    for z in (z0, z1):
        tris.append(((0.0, 0.0, z), (chord / 2, half_t, z), (chord, 0.0, z)))
        tris.append(((0.0, 0.0, z), (chord, 0.0, z), (chord / 2, -half_t, z)))
    return tris


if __name__ == "__main__":
    write_binary_stl(HERE / "cylinder_shedding.stl", cylinder(radius=0.5, span=0.1))
    write_binary_stl(HERE / "supersonic_wedge.stl", wedge(lramp=1.0, theta_deg=15.0, span=0.2))
    write_binary_stl(HERE / "supersonic_cone.stl", cone(x_max=1.0, theta_c_deg=10.0))
    write_binary_stl(HERE / "diamond_airfoil.stl", diamond_airfoil(chord=1.0, eps_deg=7.125, span=0.2))
    write_binary_stl(HERE / "hypersonic_cylinder.stl", cylinder(radius=1.0, span=0.1))
    print("wrote 5 STL bodies")
