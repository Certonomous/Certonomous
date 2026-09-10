#!/usr/bin/env python3
"""generate_geometry.py -- MRF_R1 Rushton stirred-tank geometry generator.

Emits ASCII-STL surfaces (one file per snappyHexMesh patch) STRICTLY from the
MRF_R1 pre-registration section 4 parametric spec.  No external report is
needed: the tank is a standard fully-baffled vessel with a 6-blade Rushton disc
turbine, all dimensions fixed below.  Coordinates: SI metres, z up, tank axis =
z through the origin, tank bottom at z=0, flat rigid lid at z=H.

    python3 generate_geometry.py <out_triSurface_dir>

Written for the MRF_R1 exercise-smoke build; geometry is parametric and
regenerable.  A wetted-area / cell-count read-back is done at checkMesh, never
from these requested values (MESH_STANDARD sec.9.2 read-back clause).
"""
import math
import os
import sys

# ---- pre-registration section 4 parametric spec (metres) ------------------
T      = 0.300     # tank diameter
H      = 0.300     # liquid height (= T)
D      = 0.100     # impeller diameter
C      = 0.100     # impeller off-bottom clearance (disc mid-plane height)
Rtank  = T / 2.0   # 0.150
Rimp   = D / 2.0   # 0.050  (blade outer radius)
BAF_W  = T / 10.0  # 0.030  baffle radial width
N_BAF  = 4
DISC_R = 0.75 * D / 2.0  # disc radius = 0.75*D diameter -> 0.0375
BLADE_L = D / 4.0  # 0.025  blade radial length
BLADE_H = D / 5.0  # 0.020  blade vertical height
N_BLADE = 6
SHAFT_R = 0.010    # shaft radius (dia ~0.02)
# thin-feature thicknesses (mesh-friendly finite thickness; "thin" relative to
# each feature's extent -- disclosed in the prereg build note)
BAF_T   = 0.004
BLADE_T = 0.004
DISC_T  = 0.004

NSEG = 64          # circumferential facets for round surfaces


def _norm(ax, ay, az, bx, by, bz):
    nx, ny, nz = (ay * bz - az * by), (az * bx - ax * bz), (ax * by - ay * bx)
    m = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / m, ny / m, nz / m


class Stl:
    def __init__(self, name):
        self.name = name
        self.tris = []  # list of 3 (x,y,z) tuples

    def tri(self, p1, p2, p3):
        self.tris.append((p1, p2, p3))

    def quad(self, p1, p2, p3, p4):
        self.tri(p1, p2, p3)
        self.tri(p1, p3, p4)

    def write(self, path):
        with open(path, "w") as f:
            f.write(f"solid {self.name}\n")
            for a, b, c in self.tris:
                nx, ny, nz = _norm(b[0] - a[0], b[1] - a[1], b[2] - a[2],
                                   c[0] - a[0], c[1] - a[1], c[2] - a[2])
                f.write(f" facet normal {nx:.6e} {ny:.6e} {nz:.6e}\n")
                f.write("  outer loop\n")
                for p in (a, b, c):
                    f.write(f"   vertex {p[0]:.6e} {p[1]:.6e} {p[2]:.6e}\n")
                f.write("  endloop\n endfacet\n")
            f.write(f"endsolid {self.name}\n")


def cyl_side(s, R, z0, z1, nseg=NSEG):
    for i in range(nseg):
        t0 = 2 * math.pi * i / nseg
        t1 = 2 * math.pi * (i + 1) / nseg
        a = (R * math.cos(t0), R * math.sin(t0), z0)
        b = (R * math.cos(t1), R * math.sin(t1), z0)
        c = (R * math.cos(t1), R * math.sin(t1), z1)
        d = (R * math.cos(t0), R * math.sin(t0), z1)
        s.quad(a, b, c, d)


def disc_cap(s, R, zc, nseg=NSEG):
    ctr = (0.0, 0.0, zc)
    for i in range(nseg):
        t0 = 2 * math.pi * i / nseg
        t1 = 2 * math.pi * (i + 1) / nseg
        p0 = (R * math.cos(t0), R * math.sin(t0), zc)
        p1 = (R * math.cos(t1), R * math.sin(t1), zc)
        s.tri(ctr, p0, p1)


def closed_cyl(s, R, z0, z1):
    cyl_side(s, R, z0, z1)
    disc_cap(s, R, z0)
    disc_cap(s, R, z1)


def box(s, corners):
    # corners: 0-3 bottom (ccw), 4-7 top (ccw), matching indices
    c = corners
    s.quad(c[0], c[1], c[2], c[3])  # bottom
    s.quad(c[4], c[5], c[6], c[7])  # top
    s.quad(c[0], c[1], c[5], c[4])
    s.quad(c[1], c[2], c[6], c[5])
    s.quad(c[2], c[3], c[7], c[6])
    s.quad(c[3], c[0], c[4], c[7])


def radial_box(s, r0, r1, half_t, z0, z1, theta):
    """A thin plate spanning radius [r0,r1], vertical [z0,z1], tangential
    half-thickness half_t, centred on the radial ray at angle theta."""
    ct, st = math.cos(theta), math.sin(theta)
    # local (u=radial, v=tangential) -> global (x,y)
    def g(u, v, z):
        return (u * ct - v * st, u * st + v * ct, z)
    b = [g(r0, -half_t, z0), g(r1, -half_t, z0), g(r1, half_t, z0), g(r0, half_t, z0),
         g(r0, -half_t, z1), g(r1, -half_t, z1), g(r1, half_t, z1), g(r0, half_t, z1)]
    box(s, b)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)

    # tank: wall + bottom + lid (three separately-named patches)
    wall = Stl("tankWall"); cyl_side(wall, Rtank, 0.0, H)
    bottom = Stl("tankBottom"); disc_cap(bottom, Rtank, 0.0)
    lid = Stl("tankLid"); disc_cap(lid, Rtank, H)

    # baffles: 4 thin radial plates against the wall, full height, one patch
    baffles = Stl("baffles")
    for k in range(N_BAF):
        theta = math.radians(45.0 + k * 90.0)
        radial_box(baffles, Rtank - BAF_W, Rtank + 0.002, BAF_T / 2.0, 0.0, H, theta)

    # shaft: closed cylinder poking through the lid
    shaft = Stl("shaft"); closed_cyl(shaft, SHAFT_R, 0.070, 0.320)

    # impeller: disc puck + 6 radial blades (one patch)
    imp = Stl("impeller")
    closed_cyl(imp, DISC_R, C - DISC_T / 2.0, C + DISC_T / 2.0)
    for k in range(N_BLADE):
        theta = math.radians(k * 60.0)
        radial_box(imp, Rimp - BLADE_L, Rimp, BLADE_T / 2.0,
                   C - BLADE_H / 2.0, C + BLADE_H / 2.0, theta)

    for s in (wall, bottom, lid, baffles, shaft, imp):
        s.write(os.path.join(outdir, s.name + ".stl"))
        print(f"wrote {s.name}.stl  ({len(s.tris)} facets)")

    # report analytic reference quantities (recorded, cross-checked at build)
    tank_wetted = 2 * math.pi * Rtank * H + math.pi * Rtank ** 2  # wall + bottom (lid is slip)
    print(f"# analytic tank wall+bottom area = {tank_wetted:.6f} m^2")
    print(f"# impeller: disc R={DISC_R}, blades r[{Rimp-BLADE_L},{Rimp}] z[{C-BLADE_H/2},{C+BLADE_H/2}]")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: generate_geometry.py <out_triSurface_dir>")
    main(sys.argv[1])
