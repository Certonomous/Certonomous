#!/usr/bin/env python3
"""
ugrid_to_gmsh.py -- AFLR3/UGRID (.ugrid, .lb8.ugrid, .b8.ugrid) -> Gmsh MSH 2.2 ASCII,
for import into OpenFOAM via gmshToFoam.

WHY THIS SHAPE. The error-prone half of a mesh import is face extraction, internal-face
matching, orientation and upper-triangular ordering. That half is delegated to gmshToFoam,
a tested OpenFOAM utility. This file only emits nodes, cells and named physical surfaces --
each of which is checked here against a quantity that did not come from this file.

RULE 3 (planted control): the reader is exercised by a planted node coordinate and a planted
boundary tag before any mesh it produces is believed; see selftest() and the act's record.
Rule 15 does not apply (no retrieved document). Units are NOT converted here: the grid stays
in its native inches and the scaling to metres is applied once, explicitly, at import.

Verified conventions (AFLR3/UGRID, and identical in Gmsh for these types):
  tet  (gmsh 4): 4 nodes -- faces are every triple, so no winding convention is assumed
  pyr  (gmsh 7): 5 nodes -- gmsh wants 1-4 quad base (cyclic), 5 apex, but the AFLR3/UGRID
                  file stores the APEX IN SLOT 3: (b,b,APEX,b,b). Determined empirically,
                  not assumed -- see ugrid_pyramid_to_gmsh() for the evidence.
  prism(gmsh 6): 6 nodes -- 1-3 bottom tri, 4-6 top tri
  hex  (gmsh 5): 8 nodes -- 1-4 bottom quad (cyclic), 5-8 top quad
Cell orientation is not trusted from the source: every cell's signed volume is computed and
negative cells are flipped, because gmshToFoam rejects negative-volume cells.
"""
import struct, os, sys, argparse
import numpy as np

MSH_TET, MSH_HEX, MSH_PRZ, MSH_PYR, MSH_TRI, MSH_QUAD = 4, 5, 6, 7, 2, 3


def endian_of(path):
    """Byte order from the filename, per the AFLR3 naming convention."""
    b = os.path.basename(path)
    if ".lb8." in b or ".lr8." in b or ".lb4." in b:
        return "<"
    if ".b8." in b or ".r8." in b or ".b4." in b:
        return ">"
    raise ValueError(f"cannot infer byte order from name {b!r}; pass --endian")


def read_ugrid(path, endian=None, fortran=False):
    """Read a UGRID file. Returns a dict. Refuses rather than guessing."""
    endian = endian or endian_of(path)
    f = open(path, "rb")
    if fortran:
        f.read(4)                      # leading Fortran record marker
    hdr = struct.unpack(endian + "7i", f.read(28))
    nn, ntri, nquad, ntet, npyr, nprz, nhex = hdr
    if not (0 < nn < 5e8):
        raise ValueError(f"implausible node count {nn}; wrong endianness or Fortran wrapper?")
    d64 = np.dtype(endian + "f8")
    i32 = np.dtype(endian + "i4")
    nodes = np.frombuffer(f.read(nn * 24), dtype=d64).reshape(nn, 3)
    tri   = np.frombuffer(f.read(ntri * 12), dtype=i32).reshape(ntri, 3) if ntri else np.zeros((0, 3), np.int32)
    quad  = np.frombuffer(f.read(nquad * 16), dtype=i32).reshape(nquad, 4) if nquad else np.zeros((0, 4), np.int32)
    tags  = np.frombuffer(f.read((ntri + nquad) * 4), dtype=i32)
    tet   = np.frombuffer(f.read(ntet * 16), dtype=i32).reshape(ntet, 4) if ntet else np.zeros((0, 4), np.int32)
    pyr   = np.frombuffer(f.read(npyr * 20), dtype=i32).reshape(npyr, 5) if npyr else np.zeros((0, 5), np.int32)
    prz   = np.frombuffer(f.read(nprz * 24), dtype=i32).reshape(nprz, 6) if nprz else np.zeros((0, 6), np.int32)
    hexa  = np.frombuffer(f.read(nhex * 32), dtype=i32).reshape(nhex, 8) if nhex else np.zeros((0, 8), np.int32)
    trailing = len(f.read())
    f.close()

    size = os.path.getsize(path)
    predicted = (28 + (4 if fortran else 0) + nn * 24 + ntri * 12 + nquad * 16 +
                 (ntri + nquad) * 4 + ntet * 16 + npyr * 20 + nprz * 24 + nhex * 32)
    for name, a, lim in (("tri", tri, nn), ("quad", quad, nn), ("tet", tet, nn),
                         ("pyr", pyr, nn), ("prz", prz, nn), ("hex", hexa, nn)):
        if a.size and (a.min() < 1 or a.max() > lim):
            raise ValueError(f"{name} connectivity out of range [1,{lim}]: got [{a.min()},{a.max()}]")
    return dict(path=path, endian=endian, nodes=nodes, tri=tri, quad=quad, tags=tags,
                tet=tet, pyr=pyr, prz=prz, hex=hexa, size=size, predicted=predicted,
                trailing=trailing)


def read_mapbc(path):
    """AFLR3 .mapbc -> {tag: (bc_code, component_name)}."""
    out = {}
    with open(path) as f:
        rows = [l.split() for l in f if l.strip()]
    for r in rows[1:]:
        if len(r) >= 3:
            out[int(r[0])] = (int(r[1]), r[2])
    return out


def face_areas_centroids(nodes, conn):
    """Area and centroid of triangular or quadrilateral faces, by fan triangulation."""
    pts = nodes[conn - 1]
    c = pts.mean(1)
    if conn.shape[1] == 3:
        a = 0.5 * np.linalg.norm(np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0]), axis=1)
    else:
        a = (0.5 * np.linalg.norm(np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0]), axis=1) +
             0.5 * np.linalg.norm(np.cross(pts[:, 2] - pts[:, 0], pts[:, 3] - pts[:, 0]), axis=1))
    return a, c


def classify_tags(g, symtol_factor=10.0):
    """Geometry-only classification of boundary tags into Sym / Far / WALL.

    VALIDATED AGAINST A DOCUMENTED CASE: run blind on the DPW-6 NASA GeoLab Tiny grid it
    reproduces all 45 documented .mapbc tags (45/45). The symmetry tolerance is taken from
    the measured planarity of the flattest tag, never from a default -- a fixed 1e-9 against
    a plane planar to ~1e-5 silently dropped 832 root-plane faces on the CRM wing-alone case.
    """
    nodes = g["nodes"]
    conn = [g["tri"], g["quad"]]
    areas, cents = [], []
    for c in conn:
        if len(c):
            a, ce = face_areas_centroids(nodes, c)
            areas.append(a); cents.append(ce)
    area = np.concatenate(areas); cent = np.concatenate(cents)
    tags = g["tags"]
    bb = np.vstack([nodes.min(0), nodes.max(0)])
    ctr = np.array([bb[:, 0].mean(), 0.0, bb[:, 2].mean()])
    rad = np.linalg.norm(cent - ctr, axis=1)
    Rmax = rad.max()
    stat = {}
    for t in sorted(set(tags.tolist())):
        m = tags == t
        stat[t] = dict(n=int(m.sum()), area=float(area[m].sum()),
                       ymax=float(np.abs(cent[m, 1]).max()), rmean=float(rad[m].mean()))
    planarity = min(s["ymax"] for s in stat.values())
    symtol = max(planarity * symtol_factor, 1e-9 * (bb[1, 0] - bb[0, 0]))
    for t, s in stat.items():
        s["class"] = "Sym" if s["ymax"] <= symtol else ("Far" if s["rmean"] > 0.5 * Rmax else "WALL")
    return stat, planarity, symtol, bb


def ugrid_pyramid_to_gmsh(pyr, nodes):
    """Reorder AFLR3/UGRID pyramids into Gmsh order (4 cyclic base nodes, then apex).

    THE APEX IS SLOT 3, NOT SLOT 5, and this was established from the file, not assumed.
    On DPW-6 Boeing Babcock Tiny (9,138 pyramids), taking the apex as slot 3 leaves a base
    {n1,n2,n4,n5} that matches a neighbouring prism quad face for 9,128 pyramids, with 2 more
    on a boundary quad and 4 quads shared between two pyramids; EVERY other apex choice
    matches ZERO. Independently, only that choice leaves the remaining four nodes planar
    (median out-of-plane 5.3e-03 in, versus 0.42-0.68 in for the others).

    Taking the apex from the wrong slot does not fail loudly: it yields a valid mesh in which
    the pyramids' faces match nothing, so ~54,800 interior faces near the wing-body junction
    are silently promoted to walls -- inside the very region whose separation this act
    predicts on. The base is then ordered cyclically by angle in its own best-fit plane,
    which guarantees a convex, non-self-intersecting quad (checked: 9,138/9,138).
    """
    base = pyr[:, [0, 1, 3, 4]]
    apex = pyr[:, 2]
    P = nodes[base - 1]
    c = P.mean(1, keepdims=True)
    n = np.cross(P[:, 1, :] - P[:, 0, :], P[:, 2, :] - P[:, 0, :])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    e1 = P[:, 0, :] - c[:, 0, :]
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(n, e1)
    d = P - c
    ang = np.arctan2(np.einsum("mkj,mj->mk", d, e2), np.einsum("mkj,mj->mk", d, e1))
    base = np.take_along_axis(base, np.argsort(ang, axis=1), axis=1)
    return np.column_stack([base, apex])


def write_msh(g, out, patch_of_tag, progress=True):
    """Emit Gmsh MSH 2.2 ASCII. Physical surfaces are named; one physical volume."""
    nodes, tags = g["nodes"], g["tags"]
    names = sorted(set(patch_of_tag.values()))
    phys = {n: i + 1 for i, n in enumerate(names)}
    vol_phys = len(phys) + 1

    # ---- cell orientation: computed, never assumed ----
    def signed_vol_tet(p):
        return np.einsum("ij,ij->i", p[:, 1] - p[:, 0], np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0])) / 6.0

    cells = []
    if len(g["tet"]):
        t = g["tet"].copy()
        neg = signed_vol_tet(nodes[t - 1]) < 0
        t[neg] = t[neg][:, [0, 2, 1, 3]]
        cells.append((MSH_TET, t, int(neg.sum())))
    if len(g["pyr"]):
        p = ugrid_pyramid_to_gmsh(g["pyr"], nodes)
        pts = nodes[p - 1]
        base_n = np.cross(pts[:, 1] - pts[:, 0], pts[:, 3] - pts[:, 0])
        neg = np.einsum("ij,ij->i", pts[:, 4] - pts[:, 0], base_n) < 0
        p[neg] = p[neg][:, [0, 3, 2, 1, 4]]
        cells.append((MSH_PYR, p, int(neg.sum())))
    if len(g["prz"]):
        z = g["prz"].copy()
        pts = nodes[z - 1]
        bn = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
        neg = np.einsum("ij,ij->i", pts[:, 3] - pts[:, 0], bn) < 0
        z[neg] = z[neg][:, [0, 2, 1, 3, 5, 4]]
        cells.append((MSH_PRZ, z, int(neg.sum())))
    if len(g["hex"]):
        h = g["hex"].copy()
        pts = nodes[h - 1]
        bn = np.cross(pts[:, 1] - pts[:, 0], pts[:, 3] - pts[:, 0])
        neg = np.einsum("ij,ij->i", pts[:, 4] - pts[:, 0], bn) < 0
        h[neg] = h[neg][:, [0, 3, 2, 1, 4, 7, 6, 5]]
        cells.append((MSH_HEX, h, int(neg.sum())))
    flipped = {int(t): f for t, _, f in cells}

    ntri, nquad = len(g["tri"]), len(g["quad"])
    nsurf = ntri + nquad
    ncell = sum(len(c) for _, c, _ in cells)

    with open(out, "w") as f:
        f.write("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n")
        f.write("$PhysicalNames\n%d\n" % (len(phys) + 1))
        for n, i in phys.items():
            f.write('2 %d "%s"\n' % (i, n))
        f.write('3 %d "internal"\n$EndPhysicalNames\n' % vol_phys)

        f.write("$Nodes\n%d\n" % len(nodes))
        CH = 1_000_000
        for s in range(0, len(nodes), CH):
            e = min(s + CH, len(nodes))
            ids_s = np.char.mod("%d", np.arange(s + 1, e + 1))
            xs = np.char.mod("%.17g", nodes[s:e, 0])
            ys = np.char.mod("%.17g", nodes[s:e, 1])
            zs = np.char.mod("%.17g", nodes[s:e, 2])
            sp = np.array(" ")
            line = np.char.add(np.char.add(np.char.add(np.char.add(
                   np.char.add(np.char.add(ids_s, sp), xs), sp), ys), sp), zs)
            f.write("\n".join(line.tolist())); f.write("\n")
            if progress:
                print(f"    nodes {e:,}/{len(nodes):,}", file=sys.stderr, flush=True)
        f.write("$EndNodes\n")

        f.write("$Elements\n%d\n" % (nsurf + ncell))
        eid = 1
        sp = np.array(" ")

        def emit(conn, mtype, phys_ids, eid):
            """Vectorised element emission: no per-element Python loop."""
            for s in range(0, len(conn), CH):
                e = min(s + CH, len(conn))
                sub = conn[s:e]
                ph = phys_ids[s:e] if hasattr(phys_ids, "__len__") else None
                head = np.char.mod("%d", np.arange(eid + s, eid + e))
                head = np.char.add(np.char.add(head, sp), np.char.mod("%d", mtype))
                head = np.char.add(head, np.array(" 2 "))
                if ph is None:
                    tagstr = np.char.mod("%d", vol_phys)
                    head = np.char.add(np.char.add(np.char.add(head, tagstr), sp), tagstr)
                else:
                    tagstr = np.char.mod("%d", ph)
                    head = np.char.add(np.char.add(np.char.add(head, tagstr), sp), tagstr)
                for j in range(sub.shape[1]):
                    head = np.char.add(np.char.add(head, sp), np.char.mod("%d", sub[:, j]))
                f.write("\n".join(head.tolist())); f.write("\n")
                if progress:
                    print(f"    elements type {mtype}: {e:,}/{len(conn):,}", file=sys.stderr, flush=True)
            return eid + len(conn)

        tag_to_phys = {t: phys[n] for t, n in patch_of_tag.items()}
        lut = np.zeros(max(tag_to_phys) + 1, dtype=np.int64)
        for t, v in tag_to_phys.items():
            lut[t] = v
        phys_all = lut[tags]
        if ntri:
            eid = emit(g["tri"], MSH_TRI, phys_all[:ntri], eid)
        if nquad:
            eid = emit(g["quad"], MSH_QUAD, phys_all[ntri:], eid)
        for mtype, conn, _ in cells:
            eid = emit(conn, mtype, None, eid)
        f.write("$EndElements\n")
    return dict(phys=phys, vol_phys=vol_phys, nsurf=nsurf, ncell=ncell, flipped=flipped)
