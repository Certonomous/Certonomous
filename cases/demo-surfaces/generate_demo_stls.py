#!/usr/bin/env python3
"""Generate the three DEMO STANDARD v2 act surfaces as binary STL.

These are DISPLAY / UPLOAD surfaces for the GUI demo acts. They are NOT
meshing inputs and no solver case is built from them.

Dimensions, and where each one comes from:

  ACT A  motor_in_duct.stl
      verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
        duct inner diameter  D      = 0.25 m          (registered)
        duct length          L      = 0.8 D = 0.200 m (registered)
        hub diameter         D_hub  = 0.3 D = 0.075 m (registered)
        centerbody carries "a rounded nose ahead of the disk and a tail"
                                                      (registered, prose)
      Display choices, NOT registered: duct wall thickness 5 mm; hub axial
      length 0.125 m; three radial support struts.

  ACT B  airfoil_blown_slot.stl
      verification/campaign/JF1_PREREGISTRATION.md
        chord                c      = 1.0 m           (registered)
        slot / base height   h      = 0.005 m, h/c = 0.005 (registered)
        section is NACA 0012 truncated to a blunt base, slot ON the base
                                                      (registered)
      Display choices, NOT registered: 0.2 m span (JF1 is a 2D section).

  ACT C  battery_module_8cell.stl
      etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md (Case 4)
        8 prismatic cells in a row                    (registered)
        each 100 mm (flow) x 30 mm (thickness)        (registered)
        separated by 3 mm cooling channels            (registered)
      Display choice, NOT registered: the registered case is 2D at UNIT
      DEPTH; the 120 mm cell height here is a display extrusion only.
      Also a display choice: the thin base plate and two end plates.

Deterministic; numpy only; no downloads; zero solver compute.
"""

import os
import struct
import sys

import numpy as np

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- primitives


def _quad(p00, p10, p11, p01):
    """Two triangles for a quad; outward normal follows the given winding."""
    return [(p00, p10, p11), (p00, p11, p01)]


def face_grid(origin, e1, e2, n1, n2):
    """Planar quad face spanned by e1,e2 from origin, outward = cross(e1,e2)."""
    origin = np.asarray(origin, float)
    e1 = np.asarray(e1, float)
    e2 = np.asarray(e2, float)
    tris = []
    for j in range(n1):
        for k in range(n2):
            a, b = j / n1, (j + 1) / n1
            c, d = k / n2, (k + 1) / n2
            tris += _quad(
                origin + e1 * a + e2 * c,
                origin + e1 * b + e2 * c,
                origin + e1 * b + e2 * d,
                origin + e1 * a + e2 * d,
            )
    return tris


def box(lo, hi, n=1):
    """Closed axis-aligned box, outward normals, each face split n x n."""
    x0, y0, z0 = map(float, lo)
    x1, y1, z1 = map(float, hi)
    ex = np.array([x1 - x0, 0.0, 0.0])
    ey = np.array([0.0, y1 - y0, 0.0])
    ez = np.array([0.0, 0.0, z1 - z0])
    o = np.array([x0, y0, z0])
    tris = []
    tris += face_grid(o + ex, ey, ez, n, n)   # +x
    tris += face_grid(o, ez, ey, n, n)        # -x
    tris += face_grid(o + ey, ez, ex, n, n)   # +y
    tris += face_grid(o, ex, ez, n, n)        # -y
    tris += face_grid(o + ez, ex, ey, n, n)   # +z
    tris += face_grid(o, ey, ex, n, n)        # -z
    return tris


def revolve(stations, nseg):
    """Closed surface of revolution about +x.

    `stations` is [(x, r), ...] monotone in x. A station with r == 0 is a
    tip; the band beside it degenerates into a triangle fan and the
    zero-area halves are dropped, which leaves the shell closed.
    """
    th = np.linspace(0.0, 2.0 * np.pi, nseg + 1)
    cs, sn = np.cos(th), np.sin(th)
    rings = []
    for x, r in stations:
        rings.append(np.column_stack([np.full(nseg + 1, float(x)), r * cs, r * sn]))
    tris = []
    for j in range(len(rings) - 1):
        a, b = rings[j], rings[j + 1]
        for i in range(nseg):
            tris += _quad(a[i], a[i + 1], b[i + 1], b[i])
    if stations[0][1] != 0.0:  # open nose -> flat cap, normal -x
        c = np.array([float(stations[0][0]), 0.0, 0.0])
        r0 = rings[0]
        tris += [(c, r0[i + 1], r0[i]) for i in range(nseg)]
    if stations[-1][1] != 0.0:  # open tail -> flat cap, normal +x
        c = np.array([float(stations[-1][0]), 0.0, 0.0])
        rn = rings[-1]
        tris += [(c, rn[i], rn[i + 1]) for i in range(nseg)]
    return tris


def annulus_tube(r_in, r_out, x0, x1, nseg):
    """Closed thin-walled tube: inner face, outer face, two annular caps."""
    th = np.linspace(0.0, 2.0 * np.pi, nseg + 1)
    cs, sn = np.cos(th), np.sin(th)

    def ring(r, x):
        return np.column_stack([np.full(nseg + 1, float(x)), r * cs, r * sn])

    Ai, Bi = ring(r_in, x0), ring(r_out, x0)
    Ao, Bo = ring(r_in, x1), ring(r_out, x1)
    tris = []
    for i in range(nseg):
        tris += _quad(Bi[i], Bi[i + 1], Bo[i + 1], Bo[i])      # outer, +r
        tris += _quad(Ai[i], Ao[i], Ao[i + 1], Ai[i + 1])      # inner, -r
        tris += _quad(Ao[i], Bo[i], Bo[i + 1], Ao[i + 1])      # cap x1, +x
        tris += _quad(Ai[i], Ai[i + 1], Bi[i + 1], Bi[i])      # cap x0, -x
    return tris


def extrude_loop(loop_xy, z0, z1, nspan=1):
    """Extrude a CCW closed polygon in the xy-plane along +z. Closed shell."""
    pts = np.asarray(loop_xy, float)
    area2 = float(np.sum(pts[:, 0] * np.roll(pts[:, 1], -1)
                         - np.roll(pts[:, 0], -1) * pts[:, 1]))
    if area2 < 0:
        pts = pts[::-1]  # force CCW so cross(tangent, +z) points outward
    n = len(pts)
    zs = np.linspace(z0, z1, nspan + 1)
    tris = []
    for s in range(nspan):
        za, zb = zs[s], zs[s + 1]
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            tris += _quad(
                np.array([p[0], p[1], za]), np.array([q[0], q[1], za]),
                np.array([q[0], q[1], zb]), np.array([p[0], p[1], zb]),
            )
    c = pts.mean(axis=0)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        tris.append((np.array([c[0], c[1], z1]),
                     np.array([p[0], p[1], z1]), np.array([q[0], q[1], z1])))
        tris.append((np.array([c[0], c[1], z0]),
                     np.array([q[0], q[1], z0]), np.array([p[0], p[1], z0])))
    return tris


def rotate_x(tris, ang):
    c, s = np.cos(ang), np.sin(ang)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)
    return [tuple(R @ np.asarray(v, float) for v in t) for t in tris]


# ------------------------------------------------------------------- writing


def write_binary_stl(path, tris, header):
    tri = np.asarray([[list(v) for v in t] for t in tris], dtype=float)
    e1 = tri[:, 1] - tri[:, 0]
    e2 = tri[:, 2] - tri[:, 0]
    nrm = np.cross(e1, e2)
    mag = np.linalg.norm(nrm, axis=1)
    keep = mag > 1e-14                      # drop degenerate tip halves
    tri, nrm, mag = tri[keep], nrm[keep], mag[keep]
    nrm = nrm / mag[:, None]
    n = len(tri)
    with open(path, "wb") as fh:
        fh.write(header.encode("ascii", "replace")[:80].ljust(80, b" "))
        fh.write(struct.pack("<I", n))
        rec = np.zeros(n, dtype=np.dtype([("v", "<f4", (12,)), ("a", "<u2")]))
        rec["v"][:, 0:3] = nrm
        rec["v"][:, 3:12] = tri.reshape(n, 9)
        fh.write(rec.tobytes())
    return n


# ------------------------------------------------------------------- act A


def act_a():
    D, L = 0.25, 0.200                     # F28 registered
    r_in, wall = D / 2.0, 0.005            # wall thickness: display choice
    r_out = r_in + wall
    r_hub, L_hub = 0.3 * D / 2.0, 0.125    # 0.3 D registered; length display
    nseg = 96

    tris = annulus_tube(r_in, r_out, 0.0, L, nseg)

    xh0 = 0.5 * (L - L_hub)
    L_nose, L_tail = 0.025, 0.035          # rounded nose and tail (F28 prose)
    st = []
    for b in np.linspace(0.0, 1.0, 13):    # ellipsoidal nose, r = 0 at tip
        st.append((xh0 + L_nose * b, r_hub * np.sqrt(max(0.0, 1.0 - (1.0 - b) ** 2))))
    st.append((xh0 + L_hub - L_tail, r_hub))
    for b in np.linspace(0.0, 1.0, 17)[1:]:
        st.append((xh0 + L_hub - L_tail + L_tail * b,
                   r_hub * np.sqrt(max(0.0, 1.0 - b ** 2))))
    tris += revolve(st, nseg)

    xs0, xs1 = xh0 + 0.045, xh0 + 0.075    # three radial struts: display only
    half_t = 0.002
    strut = box((xs0, 0.9 * r_hub, -half_t), (xs1, r_in * 1.0005, half_t), n=2)
    for k in range(3):
        tris += rotate_x(strut, 2.0 * np.pi * k / 3.0)
    return tris, "ACT A motor-in-duct display surface (F28 D=0.25 L=0.2 Dhub=0.075)"


# ------------------------------------------------------------------- act B


def naca0012_yt(x, c=1.0, t=0.12):
    s = x / c
    return 5.0 * t * c * (0.2969 * np.sqrt(s) - 0.1260 * s - 0.3516 * s ** 2
                          + 0.2843 * s ** 3 - 0.1015 * s ** 4)


def act_b():
    c, h, span = 1.0, 0.005, 0.2           # c and h registered by JF1
    lo, hi = 0.5, 1.0                      # bisect for the truncation station
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if naca0012_yt(mid, c) > h / 2.0:
            lo = mid
        else:
            hi = mid
    x_t = 0.5 * (lo + hi)

    N = 140
    beta = np.linspace(0.0, np.pi, N)
    xs = x_t * (1.0 - np.cos(beta)) / 2.0  # cosine spacing, 0 -> x_t

    loop = [(x_t, h / 2.0)]
    for x in xs[::-1][1:-1]:               # upper surface, TE -> LE
        loop.append((x, naca0012_yt(x, c)))
    loop.append((0.0, 0.0))                # leading edge
    for x in xs[1:-1]:                     # lower surface, LE -> TE
        loop.append((x, -naca0012_yt(x, c)))
    loop.append((x_t, -h / 2.0))
    for f in np.linspace(0.0, 1.0, 9)[1:-1]:   # blunt base = the slot
        loop.append((x_t, -h / 2.0 + f * h))

    tris = extrude_loop(loop, 0.0, span, nspan=2)
    hdr = ("ACT B NACA0012 blunt-base blown slot (JF1 c=1.0 h=0.005 h/c=0.005) "
           "x_trunc=%.6f" % x_t)
    return tris, hdr, x_t


# ------------------------------------------------------------------- act C


def act_c():
    Lx, Ty, Hz = 0.100, 0.030, 0.120       # 100 x 30 mm registered; 120 mm display
    gap = 0.003                            # registered cooling channel
    ncell, pitch = 8, 0.030 + 0.003
    base_t, end_t, margin = 0.004, 0.004, 0.006

    tris = []
    y = 0.0
    for _ in range(ncell):
        tris += box((0.0, y, 0.0), (Lx, y + Ty, Hz), n=4)
        y += pitch
    y_span = ncell * Ty + (ncell - 1) * gap

    # casing: thin base plate and two end plates. Display only.
    tris += box((-margin, -margin, -base_t), (Lx + margin, y_span + margin, 0.0), n=4)
    tris += box((-margin, -margin - end_t, 0.0), (Lx + margin, -margin, Hz), n=3)
    tris += box((-margin, y_span + margin, 0.0),
                (Lx + margin, y_span + margin + end_t, Hz), n=3)
    return tris, "ACT C battery module 8 cells 100x30mm 3mm channels (display 120mm tall)"


# ------------------------------------------------------------------ verify


def verify(path, expect):
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        fh.read(80)
        n = struct.unpack("<I", fh.read(4))[0]
        rec = np.frombuffer(fh.read(n * 50),
                            dtype=np.dtype([("v", "<f4", (12,)), ("a", "<u2")]))
    assert size == 84 + 50 * n, "size %d != 84 + 50*%d" % (size, n)
    tri = rec["v"][:, 3:12].reshape(n, 3, 3).astype(float)
    lo, hi = tri.reshape(-1, 3).min(axis=0), tri.reshape(-1, 3).max(axis=0)

    # closed-shell control: every undirected edge must be used exactly twice.
    keys = np.round(tri.reshape(-1, 3), 6)
    uniq, inv = np.unique(keys, axis=0, return_inverse=True)
    idx = inv.reshape(n, 3)
    e = np.concatenate([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]])
    e = np.sort(e, axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    bad = int(np.sum(cnt != 2))

    print("  %-28s %8.1f KB  %6d tri  %6d vtx" % (os.path.basename(path),
                                                  size / 1024.0, n, len(uniq)))
    print("     bbox x [%9.5f %9.5f]  dx = %8.5f m" % (lo[0], hi[0], hi[0] - lo[0]))
    print("     bbox y [%9.5f %9.5f]  dy = %8.5f m" % (lo[1], hi[1], hi[1] - lo[1]))
    print("     bbox z [%9.5f %9.5f]  dz = %8.5f m" % (lo[2], hi[2], hi[2] - lo[2]))
    print("     non-manifold edges: %d   (0 = every shell closed)" % bad)
    ok = size > 10 * 1024 and bad == 0
    for label, got, want, tol in expect:
        good = abs(got - want) <= tol
        ok &= good
        print("     %-34s %10.6f  vs %10.6f  %s"
              % (label, got, want, "OK" if good else "MISMATCH"))
    print("     ---> %s" % ("OK" if ok else "FAILED"))
    return ok, size, n, lo, hi


def main():
    ok = True

    tris, hdr = act_a()
    p = os.path.join(OUT_DIR, "motor_in_duct.stl")
    write_binary_stl(p, tris, hdr)
    r, *_ = verify(p, [("duct outer diameter (m)", 0.260, 0.260, 1e-9),
                       ("duct length L = 0.8 D (m)", 0.200, 0.200, 1e-9)])
    ok &= r

    tris, hdr, x_t = act_b()
    p = os.path.join(OUT_DIR, "airfoil_blown_slot.stl")
    write_binary_stl(p, tris, hdr)
    # The base-height row is the load-bearing one: it proves the section was
    # truncated where the half-thickness is exactly h/2. Comparing x_t against
    # a literal would be circular (the bisection against itself), so the second
    # row instead reads the truncation station back OUT of the written file's
    # bounding box and compares it to what the solve asked for.
    r, _, _, lo, hi = verify(
        p, [("base height h = h/c * c (m)", 2.0 * naca0012_yt(x_t), 0.005, 1e-6),
            ("max thickness / c", 2.0 * naca0012_yt(0.30), 0.1199, 5e-4)])
    ok &= r
    dev = abs(hi[0] - x_t)
    good = dev <= 1e-6 and abs(lo[0]) <= 1e-9
    ok &= good
    print("     %-34s %10.6f  vs %10.6f  %s"
          % ("x_trunc/c read back from file", hi[0], x_t,
             "OK" if good else "MISMATCH"))
    print("     blunt base is the JF1 slot patch, at x/c = %.4f" % x_t)

    tris, hdr = act_c()
    p = os.path.join(OUT_DIR, "battery_module_8cell.stl")
    write_binary_stl(p, tris, hdr)
    r, *_ = verify(p, [("8 cells + 7 gaps span (m)", 8 * 0.030 + 7 * 0.003, 0.261, 1e-9),
                       ("cell flow length (m)", 0.100, 0.100, 1e-9),
                       ("cell height, display (m)", 0.120, 0.120, 1e-9)])
    ok &= r

    print("\nALL CHECKS PASSED" if ok else "\nCHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
