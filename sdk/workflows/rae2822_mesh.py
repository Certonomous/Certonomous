"""Structured O-mesh generator for the RAE 2822 case, written straight to a
polyMesh.

WHY THIS EXISTS RATHER THAN A blockMeshDict
-------------------------------------------
The first attempt reused ``workflows.transonic_airfoil``'s blockMesh topology
(four quarter blocks around the section plus two wake blocks, outer boundary a
circle centred on the trailing edge). It failed the lab's mesh gate at every
refinement level, and identically: max non-orthogonality 70.65 / 70.70 / 70.64
degrees on 23k / 92k / 369k cells, against a gate of 70.

Level-independent failure means topology, not resolution, so the offending
faces were located rather than guessed at. All 892 of them sat in one band,
0.049 < x/c < 0.111 on both surfaces, hard against the wall. The cause:
blockMesh fills a block by transfinite interpolation between its bounding
edges, so the radial grid lines are a straight blend from the aerofoil surface
to the far-field circle. Near the nose those two curves have radii of curvature
of 0.008 and 50 chords, and the blend fans so hard that the radial line at
x/c = 0.05 leaves the surface at 76 degrees off the surface normal, i.e. it
runs nearly ALONG the aerofoil instead of away from it. Non-orthogonality is
the departure of the grid angle from 90 degrees, so that is the 70 degrees the
gate caught. No amount of refinement fixes it; more blocks in the radial
direction would, and so does this.

WHAT THIS DOES INSTEAD
----------------------
Nodes are placed directly, by blending two exact constructions along each
radial line:

    A(s) = P + s * n          pure offset along the surface normal
    B(s) = P + s * e          straight line to this line's far-field point
    node(s) = (1 - w(s)) A(s) + w(s) B(s),    w = smoothstep(s / L_BLEND)

At the wall w and dw/ds are both zero, so the first layers are true normal
offsets and the boundary-layer cells are orthogonal by construction. By
s = L_BLEND the blend has handed over completely to the straight radial line,
so the outer boundary lands exactly on the circle and the far field is clean.
Because smoothstep has zero slope at both ends the handover introduces no
kink.

The topology is a pure O-mesh: the circumferential index wraps at the trailing
edge, so there is no branch-cut patch and no wake block, and the single outer
patch takes characteristic free-stream conditions that admit inflow and
outflow wherever the solution puts them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

CIRCLE_CENTRE = (0.5, 0.0)
L_BLEND = 0.25    # chords over which the normal offset hands over to radial


@dataclass(frozen=True)
class OGridLevel:
    name: str
    nx: int      # cells around the section (wraps)
    ny: int      # cells from wall to far field

    @property
    def cells(self) -> int:
        return self.nx * self.ny


def _arclength_tables(section, n: int = 40001):
    """Cumulative arc length along each surface, leading edge to trailing
    edge, with the x station at every sample."""
    tables = {}
    for sign, name in ((+1.0, "upper"), (-1.0, "lower")):
        # sample denser near the nose, where the surface turns fastest
        t = np.linspace(0.0, 1.0, n)
        x = t ** 2
        y = np.array([section.y(float(xi), sign) for xi in x])
        ds = np.hypot(np.diff(x), np.diff(y))
        s = np.concatenate([[0.0], np.cumsum(ds)])
        tables[name] = (s, x)
    return tables


# Surface clustering, as a ratio of local spacing to mid-chord spacing, and the
# fraction of the surface arc over which each end relaxes to mid-chord spacing.
#
# The nose and the trailing edge are deliberately NOT treated alike. A cosine
# distribution, which clusters both ends equally, was tried first and broke the
# mesh: it put a 1.5e-4 chord cell at the trailing edge on the coarse grid and
# 9.5e-6 on the fine one, at a cusp whose own thickness 1e-3 chord upstream is
# only 8e-5. Radial lines launched from cells that much finer than the local
# feature turn through nearly a right angle within a few cells of each other
# and cross, which left 1 inverted cell on the medium and fine grids and drove
# max non-orthogonality to 113 and 161 degrees. The nose needs the fine cells
# (its radius of curvature is 0.0083 chord); the cusp does not.
#
# Both ratios scale with 1/nx, so every spacing on the grid halves when the
# level refines and the ladder stays a clean factor of two.
NOSE_SPACING_RATIO = 0.02
NOSE_RELAX_FRACTION = 0.10
TE_SPACING_RATIO = 0.35
TE_RELAX_FRACTION = 0.25


def _clustered_fractions(half: int, samples: int = 20001) -> np.ndarray:
    """``half + 1`` arc-length fractions from the nose to the trailing edge,
    spaced so the local cell size follows the ratios above."""
    sigma = np.linspace(0.0, 1.0, samples)
    spacing = ((NOSE_SPACING_RATIO + (1.0 - NOSE_SPACING_RATIO)
                * _smoothstep(sigma / NOSE_RELAX_FRACTION))
               * (TE_SPACING_RATIO + (1.0 - TE_SPACING_RATIO)
                  * _smoothstep((1.0 - sigma) / TE_RELAX_FRACTION)))
    # nodes sit at equal increments of the integral of 1/spacing
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (1.0 / spacing[1:]
                                                  + 1.0 / spacing[:-1])
                                           * np.diff(sigma))])
    cdf /= cdf[-1]
    return np.interp(np.linspace(0.0, 1.0, half + 1), cdf, sigma)


def surface_nodes(section, nx: int) -> tuple[np.ndarray, np.ndarray]:
    """``nx`` points around the closed section and their outward unit normals.

    Index 0 is the trailing edge. The index then runs forward over the UPPER
    surface to the nose at nx/2 and back along the lower surface. Points are
    placed at equal increments of a cosine-clustered arc-length parameter on
    each surface, which puts the finest spacing at the nose and at the trailing
    edge, where the curvature and the pressure gradients are.
    """
    if nx % 2:
        raise ValueError("nx must be even so the nose lands on a node")
    tables = _arclength_tables(section)
    half = nx // 2
    frac_from_nose = _clustered_fractions(half)

    pts = []
    # upper surface, trailing edge -> nose: the clustering is defined from the
    # nose outward, so walk it backwards here
    s_up, x_up = tables["upper"]
    for m in range(half):
        s = (1.0 - frac_from_nose[half - m]) * s_up[-1]
        x = float(np.interp(s, s_up, x_up))
        pts.append((x, section.y(x, +1.0)))
    # lower surface, nose -> trailing edge (the trailing edge itself is index 0
    # and is not repeated)
    s_lo, x_lo = tables["lower"]
    for m in range(half):
        s = frac_from_nose[m] * s_lo[-1]
        x = float(np.interp(s, s_lo, x_lo))
        pts.append((x, section.y(x, -1.0)))

    P = np.array(pts)
    # Outward normals from the central difference of the closed polyline. At
    # the trailing edge this returns the bisector of the two surface tangents
    # with no special case, which is what a sharp trailing edge needs.
    tangent = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    normal = np.column_stack([tangent[:, 1], -tangent[:, 0]])
    # Which way is out is decided ONCE, from the sign of the closed polygon's
    # own signed area, and applied to every node.
    #
    # It was first decided per node, by asking whether the normal pointed away
    # from a centroid. That is correct on a fat section and wrong on this one:
    # over the aft 5% the section is thinner than 1e-3 chord and the vector
    # from any centroid to a surface node is almost parallel to the chord,
    # hence almost perpendicular to the true normal, so the sign of the dot
    # product was set by rounding. It inverted the normal on 16 lower-surface
    # nodes near the trailing edge and drove the wall cells there inside out.
    area = 0.5 * float(np.sum(P[:, 0] * np.roll(P, -1, axis=0)[:, 1]
                              - np.roll(P, -1, axis=0)[:, 0] * P[:, 1]))
    if area < 0.0:
        normal *= -1.0
    return P, normal


def _smoothstep(t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _radial_spacing(distance: np.ndarray, ny: int, first_cell: float) -> np.ndarray:
    """Geometric distribution, ny cells, first cell ``first_cell``, per column.

    The expansion ratio is solved per radial line so that every line puts its
    first node at the same wall distance even though the lines have slightly
    different lengths.
    """
    out = np.zeros((len(distance), ny + 1))
    for i, total in enumerate(distance):
        lo, hi = 1.0 + 1e-12, 3.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            length = first_cell * (mid ** ny - 1.0) / (mid - 1.0)
            if length > total:
                hi = mid
            else:
                lo = mid
        r = 0.5 * (lo + hi)
        steps = first_cell * (r ** np.arange(ny) )
        s = np.concatenate([[0.0], np.cumsum(steps)])
        out[i] = s * (total / s[-1])
    return out


def build_nodes(section, level: OGridLevel, *, farfield_r: float,
                first_cell: float) -> np.ndarray:
    """(nx, ny+1, 2) array of node positions."""
    P, n = surface_nodes(section, level.nx)
    centre = np.array(CIRCLE_CENTRE)

    # Far-field point for each radial line: uniformly spaced around the circle,
    # index for index, starting from the trailing edge and running the same way
    # round as the surface nodes do.
    #
    # These were first placed at the cumulative arc-length fraction of the
    # surface, so that far-field spacing followed surface spacing. That
    # propagates the nose and trailing-edge clustering all the way out to 50
    # chords, and near the trailing edge it is fatal: the nodes either side of
    # the cusp are 1.5e-4 chord apart, so their far-field targets land within
    # 0.005 chord of each other on the circle, while their wall normals point
    # in opposite directions and have already driven the lines apart. The lines
    # have to converge back and cross, which inverted 800 cells at mid radius.
    # Spacing the far field uniformly gives every line room; the wall
    # clustering is not wanted 50 chords away in any case.
    theta = 2.0 * math.pi * np.arange(level.nx) / level.nx
    outer = centre + farfield_r * np.column_stack([np.cos(theta), np.sin(theta)])

    to_far = outer - P
    length = np.linalg.norm(to_far, axis=1)
    e = to_far / length[:, None]

    s = _radial_spacing(length, level.ny, first_cell)      # (nx, ny+1)
    w = _smoothstep(s / L_BLEND)
    A = P[:, None, :] + s[:, :, None] * n[:, None, :]
    B = P[:, None, :] + s[:, :, None] * e[:, None, :]
    return (1.0 - w[:, :, None]) * A + w[:, :, None] * B


# --------------------------------------------------------------------------
# polyMesh writer
# --------------------------------------------------------------------------

_HEADER = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "constant/polyMesh";
    object      {obj};
}}

"""


def write_polymesh(case_dir: Path, nodes: np.ndarray, *, thickness: float = 1.0
                   ) -> dict[str, int]:
    """Write a one-cell-thick 2D O-mesh as an OpenFOAM polyMesh.

    Face orientation is not reasoned about, it is measured: every face is built
    in some order, its normal is compared against the vector from the owner
    cell centre to the neighbour cell centre (or out of the cell, for a
    boundary face), and the point list is reversed when the sign is wrong. That
    removes the whole class of hand-derived winding bugs.
    """
    nx, nyp1, _ = nodes.shape
    ny = nyp1 - 1
    mesh_dir = Path(case_dir) / "constant" / "polyMesh"
    mesh_dir.mkdir(parents=True, exist_ok=True)

    # ---- points, (i, j, k) with k the extruded direction
    pts = np.zeros((2, nyp1, nx, 3))
    for k, z in enumerate((0.0, thickness)):
        pts[k, :, :, 0] = nodes[:, :, 0].T
        pts[k, :, :, 1] = nodes[:, :, 1].T
        pts[k, :, :, 2] = z
    flat = pts.reshape(-1, 3)

    def pid(i: int, j: int, k: int) -> int:
        return (k * nyp1 + j) * nx + (i % nx)

    def cid(i: int, j: int) -> int:
        return j * nx + (i % nx)

    n_cells = nx * ny
    centres = np.zeros((n_cells, 3))
    for j in range(ny):
        for i in range(nx):
            ids = [pid(i, j, 0), pid(i + 1, j, 0), pid(i + 1, j + 1, 0),
                   pid(i, j + 1, 0), pid(i, j, 1), pid(i + 1, j, 1),
                   pid(i + 1, j + 1, 1), pid(i, j + 1, 1)]
            centres[cid(i, j)] = flat[ids].mean(axis=0)

    def oriented(ids: list[int], owner: int, neighbour: int | None) -> list[int]:
        p = flat[ids]
        normal = np.cross(p[1] - p[0], p[2] - p[0])
        if neighbour is None:
            reference = p.mean(axis=0) - centres[owner]
        else:
            reference = centres[neighbour] - centres[owner]
        return ids if float(np.dot(normal, reference)) > 0 else ids[::-1]

    internal: list[tuple[int, int, list[int]]] = []
    # circumferential faces: between cell (i-1, j) and (i, j); every one is
    # internal because the O-mesh wraps
    for j in range(ny):
        for i in range(nx):
            own, nei = cid(i - 1, j), cid(i, j)
            ids = [pid(i, j, 0), pid(i, j + 1, 0), pid(i, j + 1, 1), pid(i, j, 1)]
            a, b = (own, nei) if own < nei else (nei, own)
            internal.append((a, b, oriented(ids, a, b)))
    # radial faces: between cell (i, j-1) and (i, j)
    for j in range(1, ny):
        for i in range(nx):
            own, nei = cid(i, j - 1), cid(i, j)
            ids = [pid(i, j, 0), pid(i + 1, j, 0), pid(i + 1, j, 1), pid(i, j, 1)]
            internal.append((own, nei, oriented(ids, own, nei)))

    internal.sort(key=lambda r: (r[0], r[1]))

    patches: list[tuple[str, str, list[list[int]]]] = []
    aerofoil = [oriented([pid(i, 0, 0), pid(i + 1, 0, 0), pid(i + 1, 0, 1),
                          pid(i, 0, 1)], cid(i, 0), None) for i in range(nx)]
    patches.append(("aerofoil", "wall", aerofoil))
    farfield = [oriented([pid(i, ny, 0), pid(i + 1, ny, 0), pid(i + 1, ny, 1),
                          pid(i, ny, 1)], cid(i, ny - 1), None) for i in range(nx)]
    patches.append(("farfield", "patch", farfield))
    front, back = [], []
    for j in range(ny):
        for i in range(nx):
            front.append(oriented([pid(i, j, 0), pid(i + 1, j, 0),
                                   pid(i + 1, j + 1, 0), pid(i, j + 1, 0)],
                                  cid(i, j), None))
            back.append(oriented([pid(i, j, 1), pid(i + 1, j, 1),
                                  pid(i + 1, j + 1, 1), pid(i, j + 1, 1)],
                                 cid(i, j), None))
    patches.append(("frontAndBack", "empty", front + back))

    n_internal = len(internal)
    n_faces = n_internal + sum(len(f) for _, _, f in patches)

    with (mesh_dir / "points").open("w") as fh:
        fh.write(_HEADER.format(cls="vectorField", obj="points"))
        fh.write(f"{len(flat)}\n(\n")
        fh.write("".join("(%.12g %.12g %.12g)\n" % tuple(p) for p in flat))
        fh.write(")\n")

    with (mesh_dir / "faces").open("w") as fh:
        fh.write(_HEADER.format(cls="faceList", obj="faces"))
        fh.write(f"{n_faces}\n(\n")
        for _, _, ids in internal:
            fh.write("4(%d %d %d %d)\n" % tuple(ids))
        for _, _, faces in patches:
            for ids in faces:
                fh.write("4(%d %d %d %d)\n" % tuple(ids))
        fh.write(")\n")

    note = (f"nPoints:{len(flat)} nCells:{n_cells} nFaces:{n_faces} "
            f"nInternalFaces:{n_internal}")
    with (mesh_dir / "owner").open("w") as fh:
        fh.write(_HEADER.format(cls="labelList", obj="owner")
                 .replace('object      owner;', f'note        "{note}";\n    object      owner;'))
        fh.write(f"{n_faces}\n(\n")
        fh.write("".join(f"{a}\n" for a, _, _ in internal))
        for name, _, faces in patches:
            owners = {"aerofoil": [cid(i, 0) for i in range(nx)],
                      "farfield": [cid(i, ny - 1) for i in range(nx)]}.get(name)
            if owners is None:
                owners = [cid(i, j) for j in range(ny) for i in range(nx)] * 2
            fh.write("".join(f"{o}\n" for o in owners))
        fh.write(")\n")

    with (mesh_dir / "neighbour").open("w") as fh:
        fh.write(_HEADER.format(cls="labelList", obj="neighbour")
                 .replace('object      neighbour;', f'note        "{note}";\n    object      neighbour;'))
        fh.write(f"{n_internal}\n(\n")
        fh.write("".join(f"{b}\n" for _, b, _ in internal))
        fh.write(")\n")

    with (mesh_dir / "boundary").open("w") as fh:
        fh.write(_HEADER.format(cls="polyBoundaryMesh", obj="boundary"))
        fh.write(f"{len(patches)}\n(\n")
        start = n_internal
        for name, kind, faces in patches:
            fh.write(f"    {name}\n    {{\n        type            {kind};\n")
            if kind == "wall":
                fh.write("        inGroups        1(wall);\n")
            fh.write(f"        nFaces          {len(faces)};\n"
                     f"        startFace       {start};\n    }}\n")
            start += len(faces)
        fh.write(")\n")

    return {"cells": n_cells, "points": len(flat), "faces": n_faces,
            "internal_faces": n_internal}
