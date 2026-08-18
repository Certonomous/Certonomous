#!/usr/bin/env python3
"""
Build a structured O-grid around the symmetric Joukowski airfoil
(joukowski_theory.JoukowskiAirfoil) using the SAME conformal map used to
generate the airfoil geometry -- concentric circles in the zeta-plane, about
the same offset center zc, mapped through z=zeta+1/zeta, giving grid lines
that are near-orthogonal to the airfoil surface by construction (this is
literally how the DPW-8/HFCFDVW "Classic" family is described: "The Joukowski
conformal map is used to generate grids with nearly orthogonal grid lines",
AIAA 2023-1244 Sec. IV).

Grid-family cell counts are matched to the six levels directly measured from
AIAA 2023-1244 Table 1 (see DPW8_V2_joukowski.md Sec. 2 for the citation and
the node-count cross-check): 48x16, 96x32, 192x64, 384x128, 768x256, 1536x512
(azimuthal x radial cells).

Output: a native OpenFOAM polyMesh (points/faces/owner/neighbour/boundary),
written directly -- no blockMesh spline-edge approximation. One cell thick in
z (empty front/back patches; standard OpenFOAM "2D" convention -- the DPW-8
spec's own "periodic sidewall" is the compressible-solver-community's version
of the same 2D idealization, see DPW8_V2_joukowski.md Sec. 6 for this
documented convention difference).
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from joukowski_theory import JoukowskiAirfoil

GRID_LEVELS = [
    # (level, Ni azimuthal cells, Nj radial cells)  -- matches AIAA 2023-1244 Table 1 Grid 0..5
    (1, 48, 16),
    (2, 96, 32),
    (3, 192, 64),
    (4, 384, 128),
    (5, 768, 256),
    (6, 1536, 512),
]


def geometric_spacing(d0, n, total):
    """Solve for growth ratio r such that sum_{k=0}^{n-1} d0*r^k = total.
    Returns array of n spacings and the ratio."""
    if n * d0 >= total:
        # degenerate: uniform spacing (only relevant for tiny cheap tests)
        return np.full(n, total / n), 1.0
    lo, hi = 1.0, 8.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if abs(mid - 1.0) < 1e-14:
            s = n * d0
        else:
            try:
                s = d0 * (mid ** n - 1.0) / (mid - 1.0)
            except OverflowError:
                s = float("inf")
        if s < total:
            lo = mid
        else:
            hi = mid
    ratio = 0.5 * (lo + hi)
    spacings = d0 * ratio ** np.arange(n)
    return spacings, ratio


def build_grid_points(eps, Ni, Nj, y1_target_physical, r_outer_chords=120.0, spanwise_depth_frac=0.02):
    """Returns:
       X, Y : shape (Ni, Nj+1) physical (chord-normalized, chord=1) coordinates
       chord_raw : the raw (b=1 units) chord length used to rescale
       ratio, y1_raw : the radial-stretch diagnostics
    """
    af = JoukowskiAirfoil(eps=eps, alpha_deg=0.0)
    chord_raw, tmax_raw, tc = af.chord_and_tc()

    # Half-cell azimuthal offset: keeps a wall point close to the cusp (theta
    # near 0) WITHOUT placing a grid ray exactly on it. Near the cusp,
    # dz/dzeta ~ 2(zeta-1) -> 0 linearly (the map is locally quadratic, the
    # actual cusp behavior), so a fixed zeta-space radial step at theta=0
    # exactly maps to a near-zero PHYSICAL step for several rings inward
    # (confirmed by direct measurement while building this case: min radial
    # spacing at theta=0 was 4.2e-10 chords, ~3 orders of magnitude below the
    # y1 target, and checkMesh flagged the resulting sliver cells as
    # zero-area). The half-step offset avoids the singular ray; the point set
    # stays exactly up-down (y) mirror symmetric for even Ni (verified: index
    # k=Ni-i-1 is theta's mirror for every i), which is what the zero-lift gate
    # in DPW8_V2_joukowski.md actually needs -- not a ray at theta=0 itself.
    theta = (np.arange(Ni) + 0.5) * (2 * np.pi / Ni)
    zeta_wall = af.circle_point(theta)
    dzdz = af.dzdzeta(zeta_wall)
    mag = np.abs(dzdz)
    # floor near the cusp/LE (theta -> 0, pi) so the radial step there doesn't
    # blow up; matches the documented real-family practice of opening the wake
    # grid to cap the max cell aspect ratio near the trailing edge.
    mag_floor = np.percentile(mag, 5)
    mag_eff = np.maximum(mag, mag_floor)

    y1_target_raw = y1_target_physical * chord_raw
    d0_rho = y1_target_raw / mag_eff  # per-theta first radial step in zeta-plane rho units

    r_outer_raw = r_outer_chords * chord_raw  # target farfield distance (z-plane, approx since map->identity at large |zeta|)
    R = af.R

    X = np.zeros((Ni, Nj + 1))
    Y = np.zeros((Ni, Nj + 1))
    ratios = np.zeros(Ni)
    for i in range(Ni):
        spacings, ratio = geometric_spacing(d0_rho[i], Nj, r_outer_raw - R)
        rho = R + np.concatenate([[0.0], np.cumsum(spacings)])
        zeta_ray = af.zc + rho * np.exp(1j * theta[i])
        z_ray = zeta_ray + 1.0 / zeta_ray
        X[i, :] = z_ray.real / chord_raw
        Y[i, :] = z_ray.imag / chord_raw
        ratios[i] = ratio

    return X, Y, chord_raw, ratios, y1_target_raw, af


def write_openfoam_mesh(case_dir, X, Y, depth):
    """X, Y: shape (Ni, Nj+1). Builds a 1-cell-thick extrusion in z in [0, depth],
    O-grid topology (periodic in i, wall at j=0, farfield at j=Nj), and writes a
    native OpenFOAM polyMesh (ascii) directly into case_dir/constant/polyMesh."""
    Ni, Njp1 = X.shape
    Nj = Njp1 - 1
    poly_dir = os.path.join(case_dir, "constant", "polyMesh")
    os.makedirs(poly_dir, exist_ok=True)

    # points: index p(i,j,k) = k*(Ni*(Nj+1)) + j*Ni + i
    npts_layer = Ni * (Nj + 1)
    pts = np.zeros((2 * npts_layer, 3))

    def pidx(i, j, k):
        return k * npts_layer + j * Ni + (i % Ni)

    for k, z in enumerate((0.0, depth)):
        for j in range(Nj + 1):
            for i in range(Ni):
                pts[pidx(i, j, k)] = (X[i, j], Y[i, j], z)

    def cidx(i, j):
        return j * Ni + (i % Ni)

    ncells = Ni * Nj

    def mkface(pts4):
        # NOTE: the (i,j)=(azimuthal,radial) local index frame is orientation-
        # REVERSING relative to physical (x,y) -- standard polar (r,theta)->(x,y)
        # has positive Jacobian only with r as the FIRST parameter; here i=theta
        # is first, j=r is second, so raw "CCW-in-index-space" quads are CW in
        # physical space. Reverse every face's winding to correct it (verified
        # against checkMesh: this flips all "incorrectly oriented" face errors
        # to zero, see build log).
        return list(reversed(pts4))

    faces = []  # each: (list of 4 point indices, owner cell, neighbour cell or -1, patch name or None)
    # 1) i-normal internal faces (periodic wrap): between cell (i,j) and (i+1,j)
    for j in range(Nj):
        for i in range(Ni):
            owner = cidx(i, j)
            neigh = cidx(i + 1, j)
            # face at constant i+1 boundary between the two cells, oriented so
            # normal points from owner(i) to neighbour(i+1): vertices in the
            # (y,z) sense at the i+1 ring
            f = [pidx(i + 1, j, 0), pidx(i + 1, j, 1), pidx(i + 1, j + 1, 1), pidx(i + 1, j + 1, 0)]
            faces.append((f, owner, neigh, None))

    # 2) j-normal internal faces: between cell (i,j-1) and (i,j), j=1..Nj-1
    for j in range(1, Nj):
        for i in range(Ni):
            owner = cidx(i, j - 1)
            neigh = cidx(i, j)
            f = [pidx(i, j, 0), pidx(i + 1, j, 0), pidx(i + 1, j, 1), pidx(i, j, 1)]
            faces.append((f, owner, neigh, None))

    # boundary faces: airfoil wall (j=0), farfield (j=Nj)
    for i in range(Ni):
        owner = cidx(i, 0)
        f = [pidx(i, 0, 0), pidx(i, 0, 1), pidx(i + 1, 0, 1), pidx(i + 1, 0, 0)]
        faces.append((f, owner, -1, "airfoil"))
    for i in range(Ni):
        owner = cidx(i, Nj - 1)
        f = [pidx(i, Nj, 0), pidx(i + 1, Nj, 0), pidx(i + 1, Nj, 1), pidx(i, Nj, 1)]
        faces.append((f, owner, -1, "farfield"))

    # front/back empty patches (k=0 and k=1 faces of every cell)
    for j in range(Nj):
        for i in range(Ni):
            owner = cidx(i, j)
            f = mkface([pidx(i, j, 0), pidx(i, j + 1, 0), pidx(i + 1, j + 1, 0), pidx(i + 1, j, 0)])
            faces.append((f, owner, -1, "back"))
    for j in range(Nj):
        for i in range(Ni):
            owner = cidx(i, j)
            f = mkface([pidx(i, j, 1), pidx(i + 1, j, 1), pidx(i + 1, j + 1, 1), pidx(i, j + 1, 1)])
            faces.append((f, owner, -1, "front"))

    # sort: internal faces first (by owner), then boundary faces grouped by patch
    internal = [f for f in faces if f[3] is None]
    boundary = [f for f in faces if f[3] is not None]
    internal.sort(key=lambda t: (t[1], t[2]))

    patch_order = ["airfoil", "farfield", "back", "front"]
    boundary_by_patch = {p: [f for f in boundary if f[3] == p] for p in patch_order}
    for p in patch_order:
        boundary_by_patch[p].sort(key=lambda t: t[1])

    owner = []
    neighbour = []
    face_list = []
    for f, o, n, _ in internal:
        face_list.append(f)
        owner.append(o)
        neighbour.append(n)
    nInternal = len(face_list)
    patch_ranges = {}
    for p in patch_order:
        start = len(face_list)
        for f, o, n, _ in boundary_by_patch[p]:
            face_list.append(f)
            owner.append(o)
        patch_ranges[p] = (start, len(face_list) - start)

    def foam_header(cls, obj):
        return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    object      {obj};
}}

"""

    with open(os.path.join(poly_dir, "points"), "w") as fp:
        fp.write(foam_header("vectorField", "points"))
        fp.write(f"{len(pts)}\n(\n")
        for p in pts:
            fp.write(f"({p[0]:.10e} {p[1]:.10e} {p[2]:.10e})\n")
        fp.write(")\n")

    with open(os.path.join(poly_dir, "faces"), "w") as fp:
        fp.write(foam_header("faceList", "faces"))
        fp.write(f"{len(face_list)}\n(\n")
        for f in face_list:
            fp.write(f"4({f[0]} {f[1]} {f[2]} {f[3]})\n")
        fp.write(")\n")

    with open(os.path.join(poly_dir, "owner"), "w") as fp:
        fp.write(foam_header("labelList", "owner"))
        fp.write(f"// nPoints:{len(pts)} nCells:{ncells} nFaces:{len(face_list)} nInternalFaces:{nInternal}\n")
        fp.write(f"{len(owner)}\n(\n")
        for o in owner:
            fp.write(f"{o}\n")
        fp.write(")\n")

    with open(os.path.join(poly_dir, "neighbour"), "w") as fp:
        fp.write(foam_header("labelList", "neighbour"))
        fp.write(f"// nPoints:{len(pts)} nCells:{ncells} nFaces:{len(face_list)} nInternalFaces:{nInternal}\n")
        fp.write(f"{len(neighbour)}\n(\n")
        for n in neighbour:
            fp.write(f"{n}\n")
        fp.write(")\n")

    with open(os.path.join(poly_dir, "boundary"), "w") as fp:
        fp.write(foam_header("polyBoundaryMesh", "boundary"))
        fp.write(f"{len(patch_order)}\n(\n")
        for p in patch_order:
            start, n = patch_ranges[p]
            ptype = "wall" if p == "airfoil" else ("patch" if p == "farfield" else "empty")
            fp.write(f"    {p}\n    {{\n        type            {ptype};\n"
                     f"        nFaces          {n};\n        startFace       {start};\n    }}\n")
        fp.write(")\n")

    return dict(ncells=ncells, nfaces=len(face_list), ninternal=nInternal, npoints=len(pts))


if __name__ == "__main__":
    import json
    level = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    case_dir = sys.argv[2] if len(sys.argv) > 2 else f"level{level}"
    eps = 0.10
    _, Ni, Nj = [g for g in GRID_LEVELS if g[0] == level][0]
    X, Y, chord_raw, ratios, y1_raw, af = build_grid_points(
        eps, Ni, Nj, y1_target_physical=3.0e-6, r_outer_chords=120.0)
    info = write_openfoam_mesh(case_dir, X, Y, depth=0.02)
    print(json.dumps(dict(level=level, Ni=Ni, Nj=Nj, chord_raw=chord_raw,
                           ratio_min=float(ratios.min()), ratio_max=float(ratios.max()),
                           y1_target_raw=float(y1_raw), **info), indent=2))
