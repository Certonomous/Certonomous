#!/usr/bin/env python3
"""AFLR3 .b8.ugrid (+ .mapbc) -> OpenFOAM polyMesh converter.

OpenFOAM v2606 ships no reader for AFLR3 UGRID or CGNS, which is the only
format the HLPW6 committee RANS grids are published in. This is the missing
import path, written from the format spec, so the workshop grid can actually be
measured on this box rather than proxied.

Element face orientation is decided geometrically (outward from the owner cell
centroid), not from an assumed node-ordering convention, so a wrong convention
would show up as a boundary-face mismatch against the file's own declared
boundary list -- which is asserted.

Usage: ugrid_to_foam.py <file.b8.ugrid> <file.mapbc> <caseDir>
"""
import os
import struct
import sys
import time

import numpy as np

BC_TYPE = {}  # filled from mapbc code


def foam_type(code):
    c = int(code)
    if c == 4000:
        return "wall"
    if 6660 <= c <= 6669:
        return "symmetry"
    return "patch"


class ConverterRefusal(Exception):
    """A condition this converter must stop on under ANY interpreter flag.

    NOT an `assert`. `python3 -O` deletes every assert, and until 2026-09-03 EVERY ONE
    of this file's eight guards was one -- so `-O` removed the entire guard set. The
    byte-budget check was doubly conditional (inside `if fortran:` AND an assert), and
    `nbnd == ndecl`, the ONLY structural check a raw C stream received, was an assert
    too: under `-O` a `.b8` grid converted with NO VALIDATION WHATSOEVER. See L-475.
    """


def _expected_size(counts, fortran):
    """The EXACT byte length a UGRID file must have for these seven counts.

    Fortran unformatted writes the header and the bulk as TWO records, each bracketed
    by a 4-byte length marker: 4 + 28 + 4 + 4 + payload + 4 = 28 + payload + 16.
    """
    nN, nT, nQ, nTet, nPyr, nPri, nHex = counts
    payload = (nN * 24 + nT * 12 + nQ * 16 + (nT + nQ) * 4
               + nTet * 16 + nPyr * 20 + nPri * 24 + nHex * 32)
    return 28 + payload + (16 if fortran else 0)


def sniff_layout(path):
    """Return (endian, fortran) by the TOTAL-BYTE-BUDGET IDENTITY. Never a heuristic.

    ⚠ THIS REPLACES A MEASURED DEFECT, AND THE DEFECT IS DESCRIBED SO IT CANNOT RETURN.
    The old form tested the first four bytes for a Fortran record marker of 28 and, on
    failing, ACCEPTED THE FIRST BYTE ORDER GIVING `0 < n < 2e9`, big-endian first. A
    raw-C-stream UGRID whose byte-swapped first word stays positive and under 2e9 was
    therefore mis-detected SILENTLY -- no error, no warning, a wrong mesh. Measured
    blast radius at `verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/
    UGRID_HEADER_AUDIT.json` (`b78e8858`): 13 files audited, 3 mis-detecting, all three
    `M6I_runs/mesh/wing_strct.{3,4,5}.lb8.ugrid`.

    THE REPAIR IS A REFUSAL, NOT A NEW ACCEPT PATH. Each of the four (endian, packaging)
    combinations implies an EXACT file size from the seven-integer header. Exactly one
    must reproduce the size on disk. Zero matches REFUSES. More than one REFUSES. A
    layout that reproduces the file size to the byte across four independent element
    counts is not a guess -- and where it cannot be resolved uniquely, this converter
    stops rather than choosing, because a mis-sniffed layout yields a cell count that is
    wrong and looks fine.
    """
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        raw = f.read(64)
    hits = []
    for endian in (">", "<"):
        for fortran in (False, True):
            off = 4 if fortran else 0
            if len(raw) < off + 28:
                continue
            counts = struct.unpack(endian + "7i", raw[off:off + 28])
            if any(x < 0 for x in counts) or counts[0] <= 0:
                continue
            if _expected_size(counts, fortran) == size:
                hits.append((endian, fortran))
    if not hits:
        raise ConverterRefusal(
            f"LAYOUT: no (endian, packaging) combination reproduces the actual file size "
            f"{size} for {path}. The header was read four ways and none is consistent "
            f"with the bytes on disk. REFUSED rather than guessed.")
    if len(hits) > 1:
        raise ConverterRefusal(
            f"LAYOUT: {len(hits)} layouts all reproduce size {size} for {path}: {hits}. "
            f"Ambiguous. REFUSED -- never choose.")
    return hits[0]


def read_ugrid(path):
    endian, fortran = sniff_layout(path)
    i4, f8 = endian + "i4", endian + "f8"
    print(f"       layout: {'big' if endian == '>' else 'little'}-endian, "
          f"{'Fortran unformatted' if fortran else 'raw C stream'}", flush=True)
    with open(path, "rb") as f:
        if fortran:
            f.read(4)                       # opening marker of the header record
        h = np.frombuffer(f.read(28), dtype=i4)
        nN, nT, nQ, nTet, nPyr, nPri, nHex = (int(x) for x in h)
        if fortran:
            # closing marker of the header record, then the opening marker of
            # the single bulk record that holds everything else. That the bulk
            # marker equals the exact byte budget of the remaining arrays is a
            # free check on the whole header, and is asserted.
            _m = int(np.frombuffer(f.read(4), dtype=i4)[0])
            if _m != 28:
                raise ConverterRefusal(
                    f"Fortran header record trailing marker is {_m}, expected 28")
            bulk = int(np.frombuffer(f.read(4), dtype=i4)[0])
            want = (nN * 24 + nT * 12 + nQ * 16 + nT * 4 + nQ * 4
                    + nTet * 16 + nPyr * 20 + nPri * 24 + nHex * 32)
            if bulk != want:
                raise ConverterRefusal(
                    f"Fortran bulk record is {bulk} bytes, header implies {want}")
        pts = np.frombuffer(f.read(nN * 24), dtype=f8).reshape(nN, 3).astype(np.float64)
        tri = np.frombuffer(f.read(nT * 12), dtype=i4).reshape(nT, 3).astype(np.int32)
        quad = np.frombuffer(f.read(nQ * 16), dtype=i4).reshape(nQ, 4).astype(np.int32)
        ttag = np.frombuffer(f.read(nT * 4), dtype=i4).astype(np.int32)
        qtag = np.frombuffer(f.read(nQ * 4), dtype=i4).astype(np.int32)
        tet = np.frombuffer(f.read(nTet * 16), dtype=i4).reshape(nTet, 4).astype(np.int32)
        pyr = np.frombuffer(f.read(nPyr * 20), dtype=i4).reshape(nPyr, 5).astype(np.int32)
        pri = np.frombuffer(f.read(nPri * 24), dtype=i4).reshape(nPri, 6).astype(np.int32)
        hexa = np.frombuffer(f.read(nHex * 32), dtype=i4).reshape(nHex, 8).astype(np.int32)
        if fortran:
            _c = int(np.frombuffer(f.read(4), dtype=i4)[0])
            if _c != bulk:
                raise ConverterRefusal(
                    f"Fortran bulk record closing marker is {_c}, expected {bulk}")
        leftover = f.read(1)
    if leftover:
        raise ConverterRefusal(
            "trailing bytes after the declared payload -- format assumption wrong")
    # to 0-based
    for a in (tri, quad, tet, pyr, pri, hexa):
        a -= 1
    return dict(pts=pts, tri=tri, quad=quad, ttag=ttag, qtag=qtag,
                tet=tet, pyr=pyr, pri=pri, hexa=hexa)


def read_mapbc(path):
    out = {}
    with open(path) as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    n = int(lines[0].split()[0])
    for ln in lines[1:n + 1]:
        p = ln.split()
        out[int(p[0])] = (int(p[1]), p[2])
    return out


def gather(x, idx):
    return x[idx]


def main():
    ug_path, mapbc_path, case = sys.argv[1], sys.argv[2], sys.argv[3]
    t0 = time.time()
    g = read_ugrid(ug_path)
    bc = read_mapbc(mapbc_path)
    pts = g["pts"]
    nN = len(pts)
    tet, pyr, pri, hexa = g["tet"], g["pyr"], g["pri"], g["hexa"]
    nTet, nPyr, nPri, nHex = len(tet), len(pyr), len(pri), len(hexa)
    nCells = nTet + nPyr + nPri + nHex
    print(f"[{time.time()-t0:6.1f}s] read: {nN} nodes, {nCells} cells "
          f"(tet {nTet}, pyr {nPyr}, pri {nPri}, hex {nHex})", flush=True)

    off_tet, off_pyr, off_pri, off_hex = 0, nTet, nTet + nPyr, nTet + nPyr + nPri

    # ---- cell centroids (mean of vertices; used only for face orientation) ----
    cc = np.empty((nCells, 3), dtype=np.float64)
    if nTet:
        cc[off_tet:off_tet + nTet] = pts[tet].mean(axis=1)
    if nPyr:
        cc[off_pyr:off_pyr + nPyr] = pts[pyr].mean(axis=1)
    if nPri:
        cc[off_pri:off_pri + nPri] = pts[pri].mean(axis=1)
    if nHex:
        cc[off_hex:off_hex + nHex] = pts[hexa].mean(axis=1)

    # ---- face templates (node-local indices), AFLR3/UGRID ordering ----
    TET_T = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3)]
    PYR_T = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    PYR_Q = [(0, 1, 2, 3)]
    PRI_T = [(0, 1, 2), (3, 4, 5)]
    PRI_Q = [(0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    HEX_Q = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]

    tri_parts, tri_own = [], []
    quad_parts, quad_own = [], []

    def add(elems, off, templ, parts, owns):
        if len(elems) == 0:
            return
        for t in templ:
            parts.append(elems[:, list(t)])
            owns.append(np.arange(off, off + len(elems), dtype=np.int32))

    add(tet, off_tet, TET_T, tri_parts, tri_own)
    add(pri, off_pri, PRI_T, tri_parts, tri_own)
    add(pri, off_pri, PRI_Q, quad_parts, quad_own)
    add(hexa, off_hex, HEX_Q, quad_parts, quad_own)

    # Pyramids: AFLR3's 5-node ordering is not the CGNS/VTK one and is easy to
    # get wrong from documentation alone, so the apex is identified
    # geometrically -- it is the single node whose removal leaves four coplanar
    # nodes -- and the base is then wound cyclically in its own plane. No node-
    # ordering convention is assumed anywhere.
    if nPyr:
        P = pts[pyr]                                   # (n,5,3)
        LUT = np.array([[j for j in range(5) if j != a] for a in range(5)])
        vols = np.empty((nPyr, 5))
        for a in range(5):
            o = LUT[a]
            e1 = P[:, o[1]] - P[:, o[0]]
            e2 = P[:, o[2]] - P[:, o[0]]
            e3 = P[:, o[3]] - P[:, o[0]]
            vols[:, a] = np.abs(np.einsum("ij,ij->i", np.cross(e1, e2), e3))
        apex_l = vols.argmin(axis=1)
        srt = np.sort(vols, axis=1)
        scale = np.maximum(srt[:, 1], 1e-300)
        print(f"[{time.time()-t0:6.1f}s] pyramid apex detection: local-index "
              f"histogram {np.bincount(apex_l, minlength=5).tolist()}, "
              f"median coplanarity margin (2nd/1st volume) "
              f"{np.median(scale / np.maximum(srt[:, 0], 1e-300)):.3g}",
              flush=True)
        # The detection above returns local index 2 as the apex for the
        # overwhelming majority of pyramids; the stragglers are numerically
        # degenerate (near-flat) elements where a per-element geometric sort is
        # unreliable. So the convention is *derived* from the mesh and then
        # applied uniformly: apex = local 2, base quad wound (0,3,4,1) -- the
        # cyclic order the same geometric test returns on the well-conditioned
        # elements. Correctness is not assumed: the boundary-face assertion
        # below fails outright if this is wrong.
        modal = int(np.bincount(apex_l, minlength=5).argmax())
        if modal != 2:
            raise ConverterRefusal(
                f"unexpected AFLR3 pyramid apex convention: {modal}")
        base_n = pyr[:, [0, 3, 4, 1]]
        apex_n = pyr[:, 2]
        del P
        pyr_own = np.arange(off_pyr, off_pyr + nPyr, dtype=np.int32)
        quad_parts.append(base_n)
        quad_own.append(pyr_own)
        for i in range(4):
            tri_parts.append(np.column_stack(
                (base_n[:, i], base_n[:, (i + 1) % 4], apex_n)))
            tri_own.append(pyr_own)

    results = []   # (nodes(n,k), owner, neigh, is_internal)
    bnd_keys, bnd_nodes, bnd_own = [], [], []

    for parts, owns, k in ((tri_parts, tri_own, 3), (quad_parts, quad_own, 4)):
        if not parts:
            continue
        fn = np.concatenate(parts, axis=0)
        fo = np.concatenate(owns, axis=0)
        del parts[:], owns[:]
        print(f"[{time.time()-t0:6.1f}s] {k}-node cell-face incidences: {len(fn)}", flush=True)

        # orient outward from owner cell
        p = pts[fn]                                   # (n,k,3)
        if k == 3:
            nrm = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        else:
            nrm = np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 1])
        outward = np.einsum("ij,ij->i", nrm, p.mean(axis=1) - cc[fo]) > 0
        del p, nrm
        fn[~outward] = fn[~outward, ::-1]
        del outward

        # dedup on sorted node key
        key = np.sort(fn, axis=1)
        view = np.ascontiguousarray(key).view(
            [(f"f{i}", key.dtype) for i in range(k)]).ravel()
        del key
        uniq, inv, cnt = np.unique(view, return_inverse=True, return_counts=True)
        del view
        print(f"[{time.time()-t0:6.1f}s]   unique {k}-faces {len(uniq)} "
              f"(boundary {int((cnt==1).sum())})", flush=True)

        order = np.argsort(inv, kind="stable")
        inv_s, fo_s = inv[order], fo[order]
        start = np.concatenate(([0], np.cumsum(cnt)[:-1]))
        if cnt.max() > 2:
            raise ConverterRefusal(
                f"a face is shared by {int(cnt.max())} cells; at most 2 is possible")

        internal = cnt == 2
        i0 = start[internal]
        a, b = fo_s[i0], fo_s[i0 + 1]
        own_i = np.minimum(a, b)
        nei_i = np.maximum(a, b)
        # face node list taken from the owner instance (its outward normal
        # points owner -> neighbour, which is OpenFOAM's requirement)
        pick = np.where(a <= b, i0, i0 + 1)
        results.append((fn[order[pick]], own_i, nei_i))

        j0 = start[~internal]
        bn = fn[order[j0]]
        bnd_nodes.append(bn)
        bnd_own.append(fo_s[j0])
        bnd_keys.append(np.sort(bn, axis=1))
        del fn, fo, inv, inv_s, fo_s, order

    # ---- declared boundary faces -> tag lookup ----
    decl_key, decl_tag = [], []
    if len(g["tri"]):
        decl_key.append(np.sort(g["tri"], axis=1))
        decl_tag.append(g["ttag"])
    if len(g["quad"]):
        decl_key.append(np.sort(g["quad"], axis=1))
        decl_tag.append(g["qtag"])

    def keyhash(a):
        # nodes < 2^31; pack sorted node ids into one int128-ish via python? use
        # structured void view instead, per width
        return np.ascontiguousarray(a).view(
            [(f"f{i}", a.dtype) for i in range(a.shape[1])]).ravel()

    tags_per_group = []
    ndecl = 0
    for grp, dk, dt in zip(bnd_keys, decl_key, decl_tag):
        ndecl += len(dk)
        dh, gh = keyhash(dk), keyhash(grp)
        sidx = np.argsort(dh, kind="stable")
        pos = np.searchsorted(dh[sidx], gh)
        if not ((pos < len(dh)).all()
                and (dh[sidx][np.minimum(pos, len(dh) - 1)] == gh).all()):
            raise ConverterRefusal(
                "computed boundary face not present in the file's declared "
                "boundary list")
        tags_per_group.append(dt[sidx][pos])
    nbnd = sum(len(x) for x in bnd_own)
    if nbnd != ndecl:
        raise ConverterRefusal(
            f"boundary face count mismatch: computed {nbnd}, declared {ndecl}. THIS IS THE ONLY STRUCTURAL CHECK A RAW C STREAM RECEIVES and it was an assert until 2026-09-03 (L-475)")
    print(f"[{time.time()-t0:6.1f}s] boundary faces validated against file: {nbnd}", flush=True)

    # ---- assemble ----
    nInt = sum(len(o) for _, o, _ in results)
    print(f"[{time.time()-t0:6.1f}s] internal {nInt}, boundary {nbnd}, "
          f"total {nInt+nbnd}", flush=True)

    own = np.concatenate([o for _, o, _ in results])
    nei = np.concatenate([n for _, _, n in results])
    fnodes = [f for f, _, _ in results]
    # upper-triangular order: sort by owner then neighbour
    o_order = np.lexsort((nei, own))
    own = own[o_order]
    nei = nei[o_order]

    sizes = [len(f) for f in fnodes]
    widths = [f.shape[1] for f in fnodes]
    gid = np.concatenate([np.full(s, i, np.int8) for i, s in enumerate(sizes)])
    lid = np.concatenate([np.arange(s, dtype=np.int64) for s in sizes])
    gid, lid = gid[o_order], lid[o_order]

    # ---- patches, merged by mapbc name ----
    names = {}
    for tag, (code, name) in bc.items():
        names.setdefault(name, []).append(tag)
    all_btag = np.concatenate(tags_per_group)
    all_bgid = np.concatenate([np.full(len(x), i, np.int8) for i, x in enumerate(bnd_own)])
    all_blid = np.concatenate([np.arange(len(x), dtype=np.int64) for x in bnd_own])
    all_bown = np.concatenate(bnd_own)

    patches = []
    for name, tags in names.items():
        m = np.isin(all_btag, tags)
        if not m.any():
            continue
        code = bc[tags[0]][0]
        patches.append((name, foam_type(code), code, np.flatnonzero(m)))
    patches.sort(key=lambda x: (-len(x[3]),))
    print(f"[{time.time()-t0:6.1f}s] patches: "
          + ", ".join(f"{n}({t},{len(i)})" for n, t, _, i in patches), flush=True)

    # ---- write ----
    pm = os.path.join(case, "constant", "polyMesh")
    os.makedirs(pm, exist_ok=True)

    def hdr(cls, obj, note=""):
        return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                f"    class {cls};\n    location \"constant/polyMesh\";\n"
                f"    object {obj};\n}}\n{note}\n")

    with open(os.path.join(pm, "points"), "w") as f:
        f.write(hdr("vectorField", "points"))
        f.write(f"{nN}\n(\n")
        np.savetxt(f, pts, fmt="(%.10g %.10g %.10g)")
        f.write(")\n")
    print(f"[{time.time()-t0:6.1f}s] wrote points", flush=True)

    def face_lines(nodes_by_group, gidx, lidx):
        chunks = []
        for i, nb in enumerate(nodes_by_group):
            sel = gidx == i
            if not sel.any():
                continue
            rows = nb[lidx[sel]]
            w = rows.shape[1]
            body = np.char.add(np.char.add(f"{w}(", np.array(
                [" ".join(map(str, r)) for r in rows])), ")")
            chunks.append((np.flatnonzero(sel), body))
        outn = sum(len(c[0]) for c in chunks)
        out = np.empty(outn, dtype=object)
        for idx, body in chunks:
            out[idx] = body
        return out

    fl_int = face_lines(fnodes, gid, lid)
    print(f"[{time.time()-t0:6.1f}s] built internal face strings", flush=True)

    bnd_order, bnd_start, cursor = [], [], nInt
    for name, ptype, code, idx in patches:
        bnd_start.append((name, ptype, code, cursor, len(idx)))
        bnd_order.append(idx)
        cursor += len(idx)
    bnd_order = np.concatenate(bnd_order)
    fl_bnd = face_lines(bnd_nodes, all_bgid[bnd_order], all_blid[bnd_order])
    print(f"[{time.time()-t0:6.1f}s] built boundary face strings", flush=True)

    with open(os.path.join(pm, "faces"), "w") as f:
        f.write(hdr("faceList", "faces"))
        f.write(f"{nInt+nbnd}\n(\n")
        f.write("\n".join(fl_int.tolist()))
        f.write("\n")
        f.write("\n".join(fl_bnd.tolist()))
        f.write("\n)\n")
    print(f"[{time.time()-t0:6.1f}s] wrote faces", flush=True)

    own_all = np.concatenate([own, all_bown[bnd_order]])
    for obj, arr, n in (("owner", own_all, nInt + nbnd), ("neighbour", nei, nInt)):
        with open(os.path.join(pm, obj), "w") as f:
            f.write(hdr("labelList", obj,
                        f"// note: nCells:{nCells} nFaces:{nInt+nbnd} "
                        f"nInternalFaces:{nInt}"))
            f.write(f"{n}\n(\n")
            arr.astype(np.int64).tofile(f, sep="\n")
            f.write("\n)\n")
    print(f"[{time.time()-t0:6.1f}s] wrote owner/neighbour", flush=True)

    with open(os.path.join(pm, "boundary"), "w") as f:
        f.write(hdr("polyBoundaryMesh", "boundary"))
        f.write(f"{len(bnd_start)}\n(\n")
        for name, ptype, code, st, n in bnd_start:
            f.write(f"    {name}\n    {{\n        type            {ptype};\n"
                    f"        nFaces          {n};\n        startFace       {st};\n"
                    f"        // AFLR3 mapbc code {code}\n    }}\n")
        f.write(")\n")
    print(f"[{time.time()-t0:6.1f}s] DONE -> {pm}", flush=True)


if __name__ == "__main__":
    main()
