#!/usr/bin/env python3
"""Render the SO-3 grid figures from the run's OWN polyMesh.

The grid drawn here is the one the case is solved on: it is read out of
`MESH/constant/polyMesh` in the SO-3 run root, not regenerated, not decimated
and not idealised.  All 4,032 cells are drawn.

READER CONTROL (CLAUDE.md rule 3).  Before any figure is written the point
reader is PLANTED into and read back, and the cell count is checked against the
count the frozen grader published.  A reader not shown able to see a non-zero
is not evidence, so this script REFUSES (exit 2) rather than drawing a picture
it cannot vouch for.

Writes, into cases/dafoam/ladder-a/figures/:
  so3_grid.png / .pdf          the far field and the section, all cells
  so3_grid_leading_edge.png / .pdf   the leading-edge region, all cells in view
"""
import gzip
import json
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = ("/home/ubuntu/certonomous-runs/"
       "CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation")
MESH = os.path.join(RUN, "MESH", "constant", "polyMesh")
GRADE = os.path.join(RUN, "SO3_grade_20260901T040709Z.json")
FIGDIR = os.path.join(REPO, "cases", "dafoam", "ladder-a", "figures")

INK = "#1a1a1a"
GRID = "#4a6b8a"
WALL = "#0f2a47"


def refuse(token, detail):
    print("%s %s" % (token, detail))
    sys.exit(2)


def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path, "r")


def _payload(path):
    """The parenthesised list body of an OpenFOAM file, with its declared count."""
    with _open(path) as fh:
        text = fh.read()
    body = text.split("// * * *", 1)[-1]
    m = re.search(r"^\s*(\d+)\s*\n\s*\(", body, re.M)
    if not m:
        refuse("REFUSE_NO_LIST_HEADER", path)
    n = int(m.group(1))
    start = body.index("(", m.end() - 1)
    depth, i = 0, start
    while i < len(body):
        if body[i] == "(":
            depth += 1
        elif body[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return n, body[start + 1:i]


def read_points(path):
    n, body = _payload(path)
    pts = [tuple(float(v) for v in t.split())
           for t in re.findall(r"\(([^()]*)\)", body)]
    if len(pts) != n:
        refuse("REFUSE_POINT_COUNT", "declared %d, parsed %d" % (n, len(pts)))
    return pts


def read_faces(path):
    n, body = _payload(path)
    faces = [[int(v) for v in t.split()]
             for t in re.findall(r"\d+\s*\(([^()]*)\)", body)]
    if len(faces) != n:
        refuse("REFUSE_FACE_COUNT", "declared %d, parsed %d" % (n, len(faces)))
    return faces


def read_boundary(path):
    with _open(path) as fh:
        text = fh.read().split("// * * *", 1)[-1]
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", text):
        name, blk = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)", blk)
        sf = re.search(r"startFace\s+(\d+)", blk)
        if nf and sf:
            out[name] = (int(sf.group(1)), int(nf.group(1)))
    return out


def planted_point_control(path, pts):
    """Plant a known coordinate into a COPY of the file text; refuse unless the
    reader reads it back, and refuse if a truncated list is parsed anyway."""
    with _open(path) as fh:
        text = fh.read()
    plant = (-9.876543, 5.432109, 1.234567)
    first = re.search(r"\(([^()]*)\)", text.split("// * * *", 1)[-1])
    if not first:
        refuse("REFUSE_NO_PLANT_SITE", path)
    head, tail = text.split("// * * *", 1)
    planted_tail = (tail[:first.start(0)]
                    + "(%.6f %.6f %.6f)" % plant
                    + tail[first.end(0):])
    tmp = os.path.join(FIGDIR, ".so3_points_planted.tmp")
    with open(tmp, "w") as fh:
        fh.write(head + "// * * *" + planted_tail)
    try:
        back = read_points(tmp)
    finally:
        os.remove(tmp)
    if len(back) != len(pts):
        refuse("REFUSE_PLANT_CHANGED_COUNT",
               "%d before, %d after" % (len(pts), len(back)))
    if max(abs(a - b) for a, b in zip(back[0], plant)) > 1e-9:
        refuse("REFUSE_PLANT_UNSEEN",
               "planted %r, reader returned %r" % (plant, back[0]))
    if max(abs(a - b) for a, b in zip(pts[0], plant)) < 1e-9:
        refuse("REFUSE_PLANT_DEGENERATE", "the unplanted point already is the plant")
    return {"plant": plant, "read_back": back[0], "seen": True}


def cell_plan(pts, faces, boundary):
    """The 2D cell outlines: the front symmetry patch of the extruded grid.

    Every one of its faces is one cell in plan, so this is the whole grid with
    nothing dropped."""
    if "symmetry1" not in boundary:
        refuse("REFUSE_NO_FRONT_PATCH", "symmetry1 absent from the boundary file")
    start, nf = boundary["symmetry1"]
    segs = []
    for f in faces[start:start + nf]:
        ring = [(pts[i][0], pts[i][1]) for i in f]
        for a, b in zip(ring, ring[1:] + ring[:1]):
            segs.append((a, b))
    return segs, nf


def wall_loop(pts, faces, boundary):
    if "wing" not in boundary:
        refuse("REFUSE_NO_WALL_PATCH", "wing absent from the boundary file")
    start, nf = boundary["wing"]
    segs = []
    for f in faces[start:start + nf]:
        ring = [(pts[i][0], pts[i][1]) for i in f]
        zs = [pts[i][2] for i in f]
        lo = min(zs)
        edge = [p for p, z in zip(ring, zs) if abs(z - lo) < 1e-12]
        if len(edge) == 2:
            segs.append((edge[0], edge[1]))
    return segs, nf


def first_layer_height(pts, wall_segs):
    """Wall-normal spacing of the first cell layer, measured off the grid.

    For every wall node, the nearest node in the same plane that is NOT a wall
    node is its first off-wall neighbour on this structured O-grid, and the
    distance between them is the first layer thickness.  Reported as a range,
    never as a single number."""
    zs = [p[2] for p in pts]
    zlo = min(zs)
    plane = [(p[0], p[1]) for p in pts if abs(p[2] - zlo) < 1e-12]
    wallpts = set()
    for a, b in wall_segs:
        wallpts.add((round(a[0], 12), round(a[1], 12)))
        wallpts.add((round(b[0], 12), round(b[1], 12)))
    off = [q for q in plane if (round(q[0], 12), round(q[1], 12)) not in wallpts]
    if not off or not wallpts:
        refuse("REFUSE_NO_OFFWALL_NODES", "wall %d, off wall %d" % (len(wallpts), len(off)))
    hs = []
    for wx, wy in wallpts:
        best = min((wx - qx) ** 2 + (wy - qy) ** 2 for qx, qy in off)
        hs.append(best ** 0.5)
    return min(hs), max(hs), len(wallpts)


def draw(segs, wall, xlim, ylim, title, xlabel, ylabel, lw, out_base, annot=None):
    fig, ax = plt.subplots(figsize=(3.35, 2.55), dpi=320)
    ax.add_collection(LineCollection(segs, colors=GRID, linewidths=lw))
    ax.add_collection(LineCollection(wall, colors=WALL, linewidths=1.5 * lw + 0.4))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=8.2, color=INK, pad=4)
    ax.set_xlabel(xlabel, fontsize=7.2, color=INK)
    ax.set_ylabel(ylabel, fontsize=7.2, color=INK)
    ax.tick_params(labelsize=6.4, colors=INK, length=2.4, width=0.5)
    for s in ax.spines.values():
        s.set_linewidth(0.5)
        s.set_color(INK)
    if annot:
        ax.annotate(annot[0], xy=annot[1], xytext=annot[2], fontsize=6.6,
                    color=INK, ha=annot[3],
                    arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
    fig.tight_layout(pad=0.35)
    for ext in ("png", "pdf"):
        fig.savefig("%s.%s" % (out_base, ext), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def draw_pair(segs, wall, out_base):
    """Both views as ONE figure, two panels, for the one-page sheet."""
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.45), dpi=320)
    views = [((-4.5, 5.5), (-5.0, 5.0), r"Grid near the section", 0.16),
             ((-0.06, 0.34), (-0.20, 0.20), r"Grid at the leading edge", 0.30)]
    for ax, (xlim, ylim, title, lw) in zip(axes, views):
        ax.add_collection(LineCollection(segs, colors=GRID, linewidths=lw))
        ax.add_collection(LineCollection(wall, colors=WALL, linewidths=1.5 * lw + 0.4))
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title, fontsize=8.0, color=INK, pad=3)
        ax.set_xlabel(r"$x$, m", fontsize=7.0, color=INK, labelpad=1.5)
        ax.set_ylabel(r"$y$, m", fontsize=7.0, color=INK, labelpad=1.5)
        ax.tick_params(labelsize=6.2, colors=INK, length=2.2, width=0.5, pad=1.5)
        for s in ax.spines.values():
            s.set_linewidth(0.5)
            s.set_color(INK)
    axes[0].annotate(r"section, chord $1$ m", xy=(0.5, 0.0), xytext=(1.9, 3.0),
                     fontsize=6.4, color=INK, ha="left",
                     arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
    fig.tight_layout(pad=0.3, w_pad=1.4)
    for ext in ("png", "pdf"):
        fig.savefig("%s.%s" % (out_base, ext), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    for p in (os.path.join(MESH, "points.gz"), os.path.join(MESH, "faces.gz"),
              os.path.join(MESH, "boundary"), GRADE):
        if not os.path.isfile(p):
            refuse("REFUSE_MISSING_ARTEFACT", p)

    pts = read_points(os.path.join(MESH, "points.gz"))
    ctrl = planted_point_control(os.path.join(MESH, "points.gz"), pts)
    faces = read_faces(os.path.join(MESH, "faces.gz"))
    boundary = read_boundary(os.path.join(MESH, "boundary"))

    segs, ncells = cell_plan(pts, faces, boundary)
    wall, nwall = wall_loop(pts, faces, boundary)

    graded_cells = json.load(open(GRADE))["mesh_cells"]
    if ncells != graded_cells:
        refuse("REFUSE_CELL_COUNT_DISAGREES",
               "front patch %d, frozen grader %d" % (ncells, graded_cells))
    if not wall:
        refuse("REFUSE_NO_WALL_EDGES", "the wall patch yielded no in-plane edge")

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    print("planted-point control SEEN: %r read back as %r" % (ctrl["plant"], ctrl["read_back"]))
    print("cells in plan %d (frozen grader: %d); wall faces %d" % (ncells, graded_cells, nwall))
    print("extent x [%.3f, %.3f] m, y [%.3f, %.3f] m" % (min(xs), max(xs), min(ys), max(ys)))

    h_lo, h_hi, n_wall_nodes = first_layer_height(pts, wall)
    print("first layer height %.4e to %.4e m over %d wall nodes"
          % (h_lo, h_hi, n_wall_nodes))
    # FAR FIELD AS A RADIUS, NOT AS A MAX COORDINATE.  The outer boundary is a
    # circle centred near mid chord, not on the origin, so max|x| overstates it
    # (18.73 against a true 18.58).  Measured about the grid's own centre, and
    # the spread of the outermost nodes is printed so the claim that it IS a
    # circle is a reading rather than an assumption.
    cx, cy = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
    rad = sorted(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 for x, y in zip(xs, ys))
    outer = rad[int(len(rad) * 0.995):]
    print("far field radius %.3f m about centre (%.3f, %.3f); outermost nodes "
          "span %.3f to %.3f m" % (rad[-1], cx, cy, outer[0], outer[-1]))

    draw(segs, wall, (-4.5, 5.5), (-5.0, 5.0),
         r"Grid near the section",
         r"$x$, m", r"$y$, m", 0.16,
         os.path.join(FIGDIR, "so3_grid"),
         annot=(r"section, chord $1$ m", (0.5, 0.0), (2.2, 2.6), "left"))

    draw(segs, wall, (-0.06, 0.34), (-0.20, 0.20),
         r"Grid at the leading edge",
         r"$x$, m", r"$y$, m", 0.30,
         os.path.join(FIGDIR, "so3_grid_leading_edge"))

    draw_pair(segs, wall, os.path.join(FIGDIR, "so3_grid_pair"))

    print("WROTE, in %s: so3_grid, so3_grid_leading_edge, so3_grid_pair "
          "(each .png and .pdf)" % FIGDIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
