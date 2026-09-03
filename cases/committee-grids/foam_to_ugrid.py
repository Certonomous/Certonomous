#!/usr/bin/env python3
"""foam_to_ugrid.py -- THE WRITER LIMB of RUNG 0. OpenFOAM polyMesh -> AFLR3 UGRID + .mapbc.

Registered at verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md section 9
("writer (does not exist; to be written)"), frozen d127d83d. It is the export half of
the round trip whose import half is `ugrid_to_foam.py` and whose independent reader is
`read_ugrid_identity.py`.

THE GATE THIS FILE IS BUILT AGAINST, QUOTED FROM THE FROZEN REGISTRATION SECTION 4 SO
THAT WHAT WAS IMPLEMENTED CAN BE CHECKED AGAINST WHAT WAS FROZEN:

    ### R0-G2b -- round-trip, writer limb (reading (ii) of section 2.2)

    `foam_to_ugrid.py` (**to be written; it does not exist**) writes the imported mesh
    back to UGRID + `.mapbc`; the **same** independent reader of R0-G2a re-reads the
    written file. The three quantities must be **exactly equal** to R0-G2a's
    source-side values.

    **R0-G2b grades the ROUND TRIP, not the geometry.** It makes no claim that node
    coordinates survive losslessly; that is not one of the three quantities Sanaa
    named and is not claimed here.

The three quantities are section 4's R0-G2a list and nothing else: **cell count**
(exact integer equality), **patch names** (exact set equality) and **per-patch face
counts** (exact integer equality on every patch). NO TOLERANCE IS IMPLEMENTED, because
the registration implements none: "These are integers; a tolerance on an integer
identity is an invitation." The gate is not widened here and it is not narrowed: no
fourth quantity is added to it, and in particular the `.mapbc` GROUP COUNT is NOT
compared -- see "WHAT THE ROUND TRIP CANNOT PRESERVE" below, where the reason is a
measured property of the mesh rather than a convenience.

Section 7's seventh planted control is implemented here and is the only thing that
makes a reported "no differences" mean anything:

    | `foam_to_ugrid.py` round trip | drop one face from the written file in a scratch
      copy | R0-G2b reports **unequal** |

RULE 3, AND IT IS NOT DECORATION. `--roundtrip` refuses to report an equality until it
has FIRST dropped one boundary face from a scratch copy of its own output and SEEN the
comparison go unequal. A zero from a reader not shown able to see a non-zero is not
evidence, so the zero is not printed until the non-zero has been.

WHAT THE ROUND TRIP CANNOT PRESERVE, SAID HERE RATHER THAN DISCOVERED LATER.
`ugrid_to_foam.py` merges the source `.mapbc` groups BY NAME: DPW5's eighteen tags
collapse to three named patches and HLPW6's seventy-three collapse to fourteen. The
per-tag multiplicity IS NOT IN THE polyMesh AT ALL -- `constant/polyMesh/boundary`
carries one AFLR3 code per patch (`ugrid_to_foam.py` writes `bc[tags[0]][0]`), not the
tag list. IT CANNOT BE RECOVERED, so this writer emits ONE `.mapbc` GROUP PER PATCH:
three groups for DPW5 against the source's eighteen, fourteen for HLPW6 against
seventy-three. THE GROUP COUNT THEREFORE DOES NOT ROUND-TRIP AND THIS FILE DOES NOT
CLAIM IT DOES. It is not one of the three quantities section 4 names, and the honest
statement is that the merge is lossy in a dimension the registered gate does not grade
-- not that the round trip is lossless.

WHAT IS RECONSTRUCTED, AND HOW IT IS PROVED RATHER THAN ASSUMED. A polyMesh stores
faces, not elements, so the four AFLR3 volume-element blocks have to be rebuilt. Cells
are classified by their own face signature (4 tri = tet; 4 tri + 1 quad = pyramid;
2 tri + 3 quad = prism; 6 quad = hex) and any other signature REFUSES by cell id. The
node lists are then rebuilt in AFLR3 positional order -- and NOT TRUSTED: every element
written is REGENERATED into its faces through the AFLR3 templates and compared, as
sorted node sets, against that cell's ACTUAL faces from the polyMesh. A single element
whose regenerated faces do not reproduce the mesh's own faces REFUSES the whole export.
That check is what turns "I believe I got the node ordering convention right" into a
measured condition, and it is the same discipline as `ugrid_to_foam.py`'s own
boundary-face validation rather than a new idea.

FORMAT VARIANTS -- SUPPORTED AND REFUSED, EXPLICITLY, NEVER GUESSED (see `--layout`):

    SUPPORTED  .b8.ugrid    big-endian    8-byte reals  raw C stream       (AFLR3/HLPW6)
    SUPPORTED  .lb8.ugrid   little-endian 8-byte reals  raw C stream       (NASA GeoLab)
    SUPPORTED  .r8.ugrid    big-endian    8-byte reals  Fortran unformatted (DPW5)
    SUPPORTED  .lr8.ugrid   little-endian 8-byte reals  Fortran unformatted (symmetry)
    REFUSED    .b4/.lb4/.r4/.lr4          4-byte reals  -- `read_ugrid_identity.py`'s
               `_NODE = 24` hardcodes 8-byte reals, so a 4-byte file is unreadable by
               the registered reader and would be written into a dead end.
    REFUSED    ASCII `.ugrid` with no endian prefix, and any 8-byte-label variant.

The variant is taken from the OUTPUT FILENAME and REFUSED if the name does not name
one. It is never defaulted silently: a UGRID stream carries no self-description, so a
file written little-endian and named `.b8` is unreadable by everything downstream and
nothing in the bytes says so.

L-459 IS HONOURED BY NOT BEING REACHED HERE. This file reads no `checkMesh` log at all:
it takes every count from the mesh's own lists. Where a count could have come from a
tool's summary it comes from `len(owner)` and `len(neighbour)` instead, which is the
same principle one step further back -- do not read a tool's report of a number when
the number itself is on disk.

NO `assert` ANYWHERE (L-332): `python3 -O` deletes them, and a guard that vanishes under
an interpreter flag is not a guard. Every refusal here is a `raise` or a `sys.exit(2)`,
and `_ast_self_check()` PARSES THIS FILE'S OWN SOURCE at every invocation and refuses if
an `assert` statement has appeared in it. The lesson is not applied until every call
site asserts it (L-221/L-222); the call site here is `main()`, unconditionally.

USAGE
    foam_to_ugrid.py --case <case_dir> --out <file.b8.ugrid> [--mapbc <file.mapbc>]
    foam_to_ugrid.py --roundtrip --case <case_dir> --source <src.ugrid> <src.mapbc>
                     --out <written.b8.ugrid>
    foam_to_ugrid.py --selftest
Exit 0 = written / equal; 2 = REFUSED, NOT A RESULT, or R0-G2b unequal.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np

EXIT_REFUSE = 2

# UGRID byte strides at 4-byte labels and 8-byte reals. Stated here rather than
# imported: this file must not become a mirror of the reader it is checked against.
_NODE = 24
_TRI, _QUAD, _TAG = 12, 16, 4
_TET, _PYR, _PRI, _HEX = 16, 20, 24, 32

# AFLR3 element -> face templates, in node-LOCAL indices. These are the inverse of the
# templates `ugrid_to_foam.py` uses on import; sharing the convention with the importer
# is correct here (this file is that importer's inverse) and is NOT the independence
# the registration requires -- section 4 requires independence of the READER, and the
# reader `read_ugrid_identity.py` shares nothing with either.
TET_T = ((0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3))
# ⚠ THE PYRAMID TEMPLATES ARE NOT `ugrid_to_foam.py`'s `PYR_T` / `PYR_Q`, AND COPYING
# THOSE IS THE FIRST DEFECT THIS FILE SHIPPED. Those two names are DEAD CODE in the
# importer: they are defined at its :150-151 and never passed to `add()`. The importer's
# LIVE pyramid path is :203-214 -- apex at local 2 (a MEASURED convention, asserted
# there as the modal outcome of a geometric apex detection) and base wound
# `pyr[:, [0, 3, 4, 1]]`, with the four triangles built as
# `(base[i], base[i+1 mod 4], apex)`. Expanded into local indices that is the quad
# (0,3,4,1) and the triangles below. The dead templates put the apex at local 4 and
# would have written a DIFFERENT ELEMENT wearing the right counts.
# HOW IT WAS CAUGHT, AND IT IS THE THIRD TIME THIS RUNG HAS BEEN BITTEN THE SAME WAY:
# `verify_elements` REFUSED on 962,824 regenerated triangle rows -- and it refused on
# HLPW6 ALONE, because HLPW6 IS THE ONLY ONE OF THE FOUR GRIDS THAT CONTAINS PYRAMIDS
# (DPW5 hex is 638,976 hexes, prism is 1,277,952 prisms, hybrid is 2,555,904 tets plus
# 425,984 prisms, and NOT ONE PYRAMID AMONG THEM). A writer validated on the three DPW5
# grids would have shipped this, exactly as the nCells lower-bound defect and the
# Fortran-offset defect before it. The population, not the single case, is the test.
PYR_T = ((0, 3, 2), (3, 4, 2), (4, 1, 2), (1, 0, 2))
PYR_Q = ((0, 3, 4, 1),)
PRI_T = ((0, 1, 2), (3, 4, 5))
PRI_Q = ((0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))
HEX_Q = ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))

#: (endian struct prefix, fortran) by output-filename variant. THE ONLY FOUR.
LAYOUTS = {
    "b8": (">", False),
    "lb8": ("<", False),
    "r8": (">", True),
    "lr8": ("<", True),
}
#: Named so a refusal can say WHY rather than "unrecognised".
REFUSED_VARIANTS = {
    "b4": "4-byte reals", "lb4": "4-byte reals",
    "r4": "4-byte reals", "lr4": "4-byte reals",
}

_TRANS = bytes.maketrans(b"()", b"  ")
_BOUNDARY_ENTRY = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_.\-]*)\s*$\s*\{(.*?)\}", re.MULTILINE | re.DOTALL)
_NFACES = re.compile(r"\bnFaces\s+(\d+)\s*;")
_START = re.compile(r"\bstartFace\s+(\d+)\s*;")
_CODE = re.compile(r"//\s*AFLR3 mapbc code\s+(\d+)")


class Refusal(Exception):
    """A condition that must stop this writer under any interpreter flag."""


# ------------------------------------------------------------------- L-332 self-check
def _ast_self_check(path: Path | None = None) -> int:
    """REFUSE if this file's own source contains an `assert` statement (L-332).

    Parses the source rather than grepping it, because a grep matches the word inside a
    docstring -- this file's own header contains it four times -- and a check that
    cannot be run on the file it guards is not a check.
    """
    path = Path(path or __file__).resolve()
    try:
        tree = ast.parse(path.read_text(errors="replace"), filename=str(path))
    except SyntaxError as exc:
        raise Refusal(f"L-332 SELF-CHECK: cannot parse {path}: {exc}")
    bad = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if bad:
        raise Refusal(
            f"L-332: {path} contains `assert` at line(s) {bad}. `python3 -O` deletes "
            f"every one of them, so a refusal written as an assert is a refusal OFFER "
            f"the runner accepts or declines by an interpreter flag. Use `raise`.")
    return 0


# ------------------------------------------------------------------ polyMesh readers
def _body_bytes(path: Path) -> bytes:
    """The list body of an OpenFOAM ASCII list file, between its `\\n(` and its last `)`."""
    raw = path.read_bytes()
    op = raw.find(b"\n(")
    if op < 0:
        raise Refusal(f"POLYMESH: {path} has no list body. ABSENT NEVER READS CLEAN.")
    body = raw[op + 2:]
    cl = body.rfind(b")")
    if cl < 0:
        raise Refusal(f"POLYMESH: {path} list body is unterminated.")
    return body[:cl]


def _declared_count(path: Path) -> int:
    """The bare integer standing alone before the list body."""
    raw = path.read_bytes()
    op = raw.find(b"\n(")
    if op < 0:
        raise Refusal(f"POLYMESH: {path} has no list body.")
    nums = [ln.strip() for ln in raw[:op].decode("latin-1").splitlines()
            if ln.strip().isdigit()]
    if not nums:
        raise Refusal(f"POLYMESH: {path} declares no list count before its body.")
    return int(nums[-1])


def _tokens(body: bytes, dtype) -> np.ndarray:
    """Numeric tokens of a list body. AN EMPTY BODY IS EMPTY, never one stray value.

    `np.fromstring` on whitespace-only input does not return an empty array; it returns
    a single element and a warning. A legitimately empty list -- `neighbour` on a
    single-cell mesh -- would then read as one entry and the declared-count check would
    refuse a file that is perfectly correct. Refusing the right file is as bad as
    accepting the wrong one, so the empty case is handled rather than caught.
    """
    if not body.strip():
        return np.zeros(0, dtype=dtype)
    return np.fromstring(body, dtype=dtype, sep=" ")


def read_labels(path: Path) -> np.ndarray:
    """One label per line (`owner`, `neighbour`), with the declared count ENFORCED."""
    n = _declared_count(path)
    v = _tokens(_body_bytes(path), np.int64)
    if len(v) != n:
        raise Refusal(
            f"POLYMESH: {path} declares {n} entries and holds {len(v)}. REFUSED -- a "
            f"list whose own count is wrong cannot be the source of anything.")
    return v


def read_points(path: Path) -> np.ndarray:
    """The (nPoints, 3) coordinate array, with the declared count ENFORCED."""
    n = _declared_count(path)
    v = _tokens(_body_bytes(path).translate(_TRANS), np.float64)
    if len(v) != 3 * n:
        raise Refusal(
            f"POLYMESH: {path} declares {n} points and holds {len(v)} coordinates "
            f"({len(v) / 3:.3f} points). REFUSED.")
    return v.reshape(n, 3)


def read_faces(path: Path):
    """(widths, fbuf) for `constant/polyMesh/faces`. Widths 3 and 4 ONLY.

    `fbuf` is (nFaces, 4) with -1 padding in the fourth column of a triangle, so a
    single array indexes every face and a stray -1 reaching a node list is visible
    rather than silently plausible.

    THE WIDTH IS READ FROM THE FIRST BYTE OF EACH LINE AND THEN CROSS-CHECKED AGAINST
    THE PARSED TOKEN AT THAT RECORD'S OFFSET. Two independent readings of the same
    quantity that must agree; a disagreement REFUSES. Reading the widths only from the
    line starts would believe the file's formatting, and reading them only from the
    token stream requires already knowing where each record begins.
    """
    n = _declared_count(path)
    body = _body_bytes(path)
    arr = np.frombuffer(body, dtype=np.uint8)
    starts = np.flatnonzero(arr == 10) + 1
    starts = starts[starts < len(body)]
    first = arr[starts]
    keep = (first == ord("3")) | (first == ord("4"))
    if int(keep.sum()) != n:
        others = sorted({chr(c) for c in np.unique(first[~keep])})
        raise Refusal(
            f"FACES: {path} declares {n} faces and {int(keep.sum())} lines begin with "
            f"'3' or '4'. Other line-initial characters seen: {others}. REFUSED -- this "
            f"writer supports TRIANGLE and QUAD faces only, which is what the four AFLR3 "
            f"volume-element types produce; a polygonal face means the mesh is not an "
            f"AFLR3 mesh and must not be written back out as one.")
    widths = (first[keep] - ord("0")).astype(np.int64)

    tok = _tokens(body.translate(_TRANS), np.int64)
    if len(tok) != n + int(widths.sum()):
        raise Refusal(
            f"FACES: {path} token count {len(tok)} != {n} widths + {int(widths.sum())} "
            f"nodes. REFUSED -- the record structure is not what the line scan implies.")
    offs = np.concatenate(([0], np.cumsum(widths + 1)[:-1]))
    if not np.array_equal(tok[offs], widths):
        bad = int(np.flatnonzero(tok[offs] != widths)[0])
        raise Refusal(
            f"FACES: {path} face {bad}: the line-initial width and the width token at "
            f"the computed record offset DISAGREE ({widths[bad]} vs {tok[offs][bad]}). "
            f"REFUSED -- never choose between two readings of the same number.")

    fbuf = np.full((n, 4), -1, dtype=np.int64)
    for w in (3, 4):
        sel = np.flatnonzero(widths == w)
        if len(sel) == 0:
            continue
        o = offs[sel]
        for j in range(w):
            fbuf[sel, j] = tok[o + 1 + j]
    return widths, fbuf


def read_boundary(path: Path):
    """[(name, nFaces, startFace, aflr3_code)] in file order.

    The AFLR3 code is recovered from the `// AFLR3 mapbc code <n>` comment that
    `ugrid_to_foam.py` writes into each patch block. IT IS THE ONLY PLACE THE SOURCE
    BC TYPE SURVIVES THE IMPORT, and without it no honest `.mapbc` can be written back,
    so its ABSENCE REFUSES rather than defaulting to a plausible code.
    """
    txt = path.read_text(errors="replace")
    body = txt.split("// * * *", 1)[-1]
    out = []
    for name, block in _BOUNDARY_ENTRY.findall(body):
        nf, st, cd = _NFACES.search(block), _START.search(block), _CODE.search(block)
        if nf is None or st is None:
            continue
        if cd is None:
            raise Refusal(
                f"BOUNDARY: patch '{name}' in {path} carries no `// AFLR3 mapbc code` "
                f"comment. REFUSED -- that comment is the only surviving record of the "
                f"source BC type, and inventing a code would write a .mapbc that looks "
                f"like the source's and is not.")
        out.append((name, int(nf.group(1)), int(st.group(1)), int(cd.group(1))))
    if not out:
        raise Refusal(f"BOUNDARY: no patch entries parsed from {path}.")
    return out


# ------------------------------------------------------------ element reconstruction
def _sorted_rows_by_cell(cell: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """`rows` (m, w) reordered into a canonical order within each cell.

    Nodes are sorted within a row, then the rows are lexsorted by (cell, node0..nodeW-1).
    Exact, never hashed: a hash comparison would trade a refusal for a collision.
    """
    r = np.sort(rows, axis=1)
    keys = [r[:, j] for j in range(r.shape[1] - 1, -1, -1)] + [cell]
    return r[np.lexsort(keys)]


def _partners(quads: list, cap_a: np.ndarray, n_side: int):
    """For each node of `cap_a`, the node on the opposite cap joined to it by a side face.

    A side quad of a prism or a hex is wound so that its two cap-A nodes are cyclically
    adjacent and each is cyclically adjacent to its own partner on cap B. So the vertical
    edges are exactly the cyclically adjacent pairs with one endpoint in cap A and one
    not. Every partner is found twice (once per side face touching it) and the two
    findings must agree -- a disagreement REFUSES rather than taking the last write.
    """
    m, k = cap_a.shape
    part = np.full((m, k), -1, dtype=np.int64)
    for q in quads:
        in_a = (q[:, :, None] == cap_a[:, None, :]).any(axis=2)
        for j in range(4):
            u, v = q[:, j], q[:, (j + 1) % 4]
            au, av = in_a[:, j], in_a[:, (j + 1) % 4]
            for a_node, b_node, sel in ((u, v, au & ~av), (v, u, av & ~au)):
                idx = np.flatnonzero(sel)
                if len(idx) == 0:
                    continue
                slot = (cap_a[idx] == a_node[idx, None]).argmax(axis=1)
                prev = part[idx, slot]
                clash = (prev >= 0) & (prev != b_node[idx])
                if clash.any():
                    raise Refusal(
                        f"ELEMENT: {int(clash.sum())} cell(s) give TWO DIFFERENT "
                        f"partners for the same cap node across their side faces. "
                        f"REFUSED -- the element is not the topology it was classified "
                        f"as, and writing it would emit a lie in AFLR3 order.")
                part[idx, slot] = b_node[idx]
    if (part < 0).any():
        raise Refusal(
            f"ELEMENT: {int((part < 0).sum())} cap node(s) across {n_side}-sided "
            f"elements have NO partner on the opposite cap. REFUSED.")
    return part


def build_elements(widths, fbuf, own, nbr, n_cells):
    """The four AFLR3 volume-element node arrays, 0-based, in AFLR3 positional order.

    Returns (tet, pyr, pri, hexa, cell_faces, n_per_cell) so the caller can verify.
    """
    n_faces = len(widths)
    n_int = len(nbr)
    cells = np.concatenate([own, nbr])
    faces = np.concatenate([np.arange(n_faces, dtype=np.int64),
                            np.arange(n_int, dtype=np.int64)])
    order = np.argsort(cells, kind="stable")
    cells, faces = cells[order], faces[order]

    n_per = np.bincount(cells, minlength=n_cells)
    if n_per.max() > 6 or n_per.min() < 4:
        bad = int(np.argmax((n_per > 6) | (n_per < 4)))
        raise Refusal(
            f"CELL {bad} has {n_per[bad]} faces. The four AFLR3 volume elements have 4 "
            f"(tet), 5 (pyramid, prism) or 6 (hex). REFUSED -- an arbitrary polyhedron "
            f"has no AFLR3 representation and must not be written as if it had one.")
    start = np.concatenate(([0], np.cumsum(n_per)[:-1]))
    slot = np.arange(len(cells)) - start[cells]
    cell_faces = np.full((n_cells, 6), -1, dtype=np.int64)
    cell_faces[cells, slot] = faces

    w_of = np.where(cell_faces >= 0, widths[np.maximum(cell_faces, 0)], 0)
    n3 = (w_of == 3).sum(axis=1)
    n4 = (w_of == 4).sum(axis=1)

    is_tet = (n3 == 4) & (n4 == 0)
    is_pyr = (n3 == 4) & (n4 == 1)
    is_pri = (n3 == 2) & (n4 == 3)
    is_hex = (n3 == 0) & (n4 == 6)
    known = is_tet | is_pyr | is_pri | is_hex
    if not known.all():
        bad = int(np.flatnonzero(~known)[0])
        raise Refusal(
            f"CELL {bad} has a face signature of {int(n3[bad])} triangles and "
            f"{int(n4[bad])} quads, which is none of tet (4,0), pyramid (4,1), prism "
            f"(2,3) or hex (0,6). {int((~known).sum())} cell(s) are like it. REFUSED -- "
            f"classified by the mesh's OWN faces, never by a count that merely fits.")

    def tri_of(mask, k):
        """The k triangle faces of each masked cell, as (m, k, 3)."""
        cf = cell_faces[mask]
        wo = np.where(cf >= 0, widths[np.maximum(cf, 0)], 0)
        sel = np.argsort(np.where(wo == 3, 0, 1), axis=1, kind="stable")[:, :k]
        ids = np.take_along_axis(cf, sel, axis=1)
        return fbuf[ids][:, :, :3], ids

    def quad_of(mask, k):
        cf = cell_faces[mask]
        wo = np.where(cf >= 0, widths[np.maximum(cf, 0)], 0)
        sel = np.argsort(np.where(wo == 4, 0, 1), axis=1, kind="stable")[:, :k]
        ids = np.take_along_axis(cf, sel, axis=1)
        return fbuf[ids], ids

    # ---- TET: face 0 gives local nodes 0,1,2; the fourth is face 1's odd node out.
    tet = np.zeros((int(is_tet.sum()), 4), dtype=np.int64)
    if len(tet):
        T, _ = tri_of(is_tet, 4)
        tet[:, :3] = T[:, 0, :]
        inface0 = (T[:, 1, :, None] == T[:, 0, None, :]).any(axis=2)
        if not ((~inface0).sum(axis=1) == 1).all():
            raise Refusal(
                "TET: a cell's second triangular face does not share exactly two nodes "
                "with its first. REFUSED -- that is not a tetrahedron.")
        tet[:, 3] = T[:, 1, :][np.arange(len(tet)), (~inface0).argmax(axis=1)]

    # ---- PYRAMID: base = the quad, apex = the tri node not on the base. AFLR3 order
    # is recovered from `ugrid_to_foam.py`'s measured convention (apex at local 2, base
    # wound (0,3,4,1)), and the face regeneration below is what proves it.
    pyr = np.zeros((int(is_pyr.sum()), 5), dtype=np.int64)
    if len(pyr):
        Q, _ = quad_of(is_pyr, 1)
        base = Q[:, 0, :]
        T, _ = tri_of(is_pyr, 4)
        onbase = (T[:, 0, :, None] == base[:, None, :]).any(axis=2)
        if not ((~onbase).sum(axis=1) == 1).all():
            raise Refusal(
                "PYRAMID: a triangular face does not have exactly one node off the "
                "quad base. REFUSED -- that is not a pyramid.")
        apex = T[:, 0, :][np.arange(len(pyr)), (~onbase).argmax(axis=1)]
        pyr[:, 0], pyr[:, 3], pyr[:, 4], pyr[:, 1] = (
            base[:, 0], base[:, 1], base[:, 2], base[:, 3])
        pyr[:, 2] = apex

    # ---- PRISM: cap A = first triangle, cap B via the side quads' vertical edges.
    pri = np.zeros((int(is_pri.sum()), 6), dtype=np.int64)
    if len(pri):
        T, _ = tri_of(is_pri, 2)
        Q, _ = quad_of(is_pri, 3)
        cap_a = T[:, 0, :]
        part = _partners([Q[:, i, :] for i in range(3)], cap_a, 3)
        pri[:, :3], pri[:, 3:] = cap_a, part

    # ---- HEX: bottom = first quad, top = the quad sharing NO node with it.
    hexa = np.zeros((int(is_hex.sum()), 8), dtype=np.int64)
    if len(hexa):
        Q, _ = quad_of(is_hex, 6)
        bottom = Q[:, 0, :]
        shared = (Q[:, 1:, :, None] == bottom[:, None, None, :]).any(axis=3).sum(axis=2)
        if not ((shared == 0).sum(axis=1) == 1).all():
            raise Refusal(
                "HEX: a cell does not have exactly one quad face disjoint from its "
                "first. REFUSED -- that is not a hexahedron.")
        top_j = (shared == 0).argmax(axis=1) + 1
        is_side = np.ones((len(hexa), 5), dtype=bool)
        is_side[np.arange(len(hexa)), top_j - 1] = False
        pick_order = np.argsort(~is_side, axis=1, kind="stable")[:, :4] + 1
        sides = [Q[np.arange(len(hexa)), pick_order[:, s], :] for s in range(4)]
        part = _partners(sides, bottom, 4)
        hexa[:, :4], hexa[:, 4:] = bottom, part

    return tet, pyr, pri, hexa, cell_faces, dict(
        is_tet=is_tet, is_pyr=is_pyr, is_pri=is_pri, is_hex=is_hex)


def verify_elements(widths, fbuf, cell_faces, masks, tet, pyr, pri, hexa):
    """REGENERATE every written element's faces and require them to BE the mesh's faces.

    This is the whole warrant for the reconstruction above. The templates are applied to
    the node lists this file is about to write; the resulting face node-SETS are compared,
    per cell and in a canonical order, against the cell's ACTUAL faces read from
    `constant/polyMesh/faces`. One mismatched element REFUSES the export.

    It is not a tautology: the node lists were built from the faces by a topological
    argument (odd node out, disjoint face, vertical edges) that is independent of the
    templates, and a wrong positional convention regenerates a DIFFERENT set of faces
    from the same nodes.
    """
    report = {}
    for tag, mask, elems, tri_t, quad_t in (
            ("tet", masks["is_tet"], tet, TET_T, ()),
            ("pyr", masks["is_pyr"], pyr, PYR_T, PYR_Q),
            ("pri", masks["is_pri"], pri, PRI_T, PRI_Q),
            ("hex", masks["is_hex"], hexa, (), HEX_Q)):
        if len(elems) == 0:
            report[tag] = 0
            continue
        cf = cell_faces[mask]
        wo = np.where(cf >= 0, widths[np.maximum(cf, 0)], 0)
        cid = np.repeat(np.arange(len(elems), dtype=np.int64), 1)
        for templ, w in ((tri_t, 3), (quad_t, 4)):
            if not templ:
                continue
            gen = np.concatenate(
                [elems[:, list(t)] for t in templ], axis=0)
            gen_cell = np.tile(cid, len(templ))
            sel = np.argsort(np.where(wo == w, 0, 1), axis=1,
                             kind="stable")[:, :len(templ)]
            ids = np.take_along_axis(cf, sel, axis=1)
            act = fbuf[ids.reshape(-1)][:, :w]
            act_cell = np.repeat(np.arange(len(elems), dtype=np.int64), len(templ))
            g = _sorted_rows_by_cell(gen_cell, gen)
            a = _sorted_rows_by_cell(act_cell, act)
            if not np.array_equal(g, a):
                n_bad = int((g != a).any(axis=1).sum())
                raise Refusal(
                    f"ELEMENT VERIFY [{tag}, {w}-node faces]: {n_bad} regenerated face "
                    f"row(s) do not reproduce the mesh's own faces. REFUSED -- the "
                    f"reconstructed AFLR3 node ordering is wrong and the written file "
                    f"would be a different mesh wearing the right counts.")
        report[tag] = int(len(elems))
    return report


# ------------------------------------------------------------------------- the write
def variant_of(out: Path) -> str:
    """The UGRID variant named by the output filename. REFUSES rather than defaulting."""
    name = out.name.lower()
    for v in sorted(LAYOUTS, key=len, reverse=True):
        if name.endswith(f".{v}.ugrid"):
            return v
    for v in sorted(REFUSED_VARIANTS, key=len, reverse=True):
        if name.endswith(f".{v}.ugrid"):
            raise Refusal(
                f"LAYOUT: {out.name} names the '{v}' variant ({REFUSED_VARIANTS[v]}). "
                f"REFUSED, NOT DEGRADED: `read_ugrid_identity.py` hardcodes 8-byte "
                f"reals (`_NODE = 24`), so this file would be unreadable by the "
                f"registered reader of R0-G2a and the round trip could never be graded.")
    raise Refusal(
        f"LAYOUT: {out.name} names no UGRID variant. Supported: "
        f"{sorted(LAYOUTS)} as `<name>.<variant>.ugrid`. REFUSED rather than defaulted "
        f"-- a UGRID stream carries NO self-description, so a file written "
        f"little-endian and named `.b8` is unreadable downstream and nothing in the "
        f"bytes says so.")


def expected_size(counts, fortran: bool) -> int:
    """The EXACT byte length the written file must have. Own arithmetic, not imported."""
    nN, nT, nQ, nTet, nPyr, nPri, nHex = counts
    payload = (nN * _NODE + nT * _TRI + nQ * _QUAD + (nT + nQ) * _TAG
               + nTet * _TET + nPyr * _PYR + nPri * _PRI + nHex * _HEX)
    return 28 + payload + (16 if fortran else 0)


def write_ugrid(out: Path, endian: str, fortran: bool, pts, tri, quad,
                ttag, qtag, tet, pyr, pri, hexa) -> int:
    """Write the UGRID stream. Connectivity is written 1-BASED, as AFLR3 requires."""
    counts = (len(pts), len(tri), len(quad), len(tet), len(pyr), len(pri), len(hexa))
    want = expected_size(counts, fortran)
    hdr = struct.pack(endian + "7i", *counts)
    i4, f8 = endian + "i4", endian + "f8"
    blocks = [(pts, f8, 0), (tri, i4, 1), (quad, i4, 1), (ttag, i4, 0), (qtag, i4, 0),
              (tet, i4, 1), (pyr, i4, 1), (pri, i4, 1), (hexa, i4, 1)]
    bulk = want - 28 - (16 if fortran else 0)
    with open(out, "wb") as f:
        if fortran:
            f.write(struct.pack(endian + "i", 28))
        f.write(hdr)
        if fortran:
            f.write(struct.pack(endian + "i", 28))
            f.write(struct.pack(endian + "i", bulk))
        for arr, dt, base in blocks:
            if arr is None or len(arr) == 0:
                continue
            f.write(np.ascontiguousarray(arr + base if base else arr).astype(dt).tobytes())
        if fortran:
            f.write(struct.pack(endian + "i", bulk))
    got = out.stat().st_size
    if got != want:
        raise Refusal(
            f"WRITE: {out} is {got} bytes and the header's own counts require exactly "
            f"{want}. REFUSED -- a UGRID whose size does not match its header cannot be "
            f"sniffed by any reader and the round trip would report BLOCKED, not a "
            f"verdict. The file is left on disk for inspection.")
    return got


def write_mapbc(path: Path, groups) -> int:
    """`<count>` then `<tag> <aflr3 code> <name>` per group. ONE GROUP PER PATCH."""
    lines = [f"{len(groups)}"]
    for tag, code, name in groups:
        lines.append(f"{tag} {code} {name}")
    path.write_text("\n".join(lines) + "\n")
    return len(groups)


def export(case: Path, out: Path, mapbc_out: Path | None = None,
           overwrite: bool = False) -> dict:
    """polyMesh -> UGRID + .mapbc. Every refusal above is live on this path."""
    case, out = Path(case), Path(out)
    variant = variant_of(out)
    endian, fortran = LAYOUTS[variant]
    pm = case / "constant" / "polyMesh"
    need = {k: pm / k for k in ("points", "faces", "owner", "neighbour", "boundary")}
    missing = [str(p) for p in need.values() if not p.is_file()]
    if missing:
        raise Refusal(
            f"POLYMESH: absent input(s) {missing}. ABSENT NEVER READS CLEAN -- this "
            f"REFUSES rather than exporting a mesh it could not fully read.")
    mapbc_out = Path(mapbc_out) if mapbc_out else out.with_suffix(".mapbc")
    for p in (out, mapbc_out):
        if p.exists() and not overwrite:
            raise Refusal(f"WRITE: {p} already exists. REFUSED -- no clobber guard.")

    pts = read_points(need["points"])
    widths, fbuf = read_faces(need["faces"])
    own = read_labels(need["owner"])
    nbr = read_labels(need["neighbour"])
    if len(own) != len(widths):
        raise Refusal(
            f"POLYMESH: owner holds {len(own)} entries and faces holds {len(widths)}. "
            f"REFUSED -- `nFaces` is len(owner) BY DEFINITION and the two must agree.")
    if len(nbr) > len(own):
        raise Refusal("POLYMESH: neighbour is longer than owner. REFUSED.")
    n_cells = int(max(own.max(), nbr.max() if len(nbr) else -1)) + 1
    lo = min(int(own.min()), int(nbr.min()) if len(nbr) else 0)
    if lo < 0:
        raise Refusal(f"POLYMESH: a negative cell label ({lo}) is present. REFUSED.")
    if fbuf[:, :3].min() < 0 or fbuf.max() >= len(pts):
        raise Refusal(
            f"FACES: a node index is out of range for {len(pts)} points "
            f"(min {int(fbuf[:, :3].min())}, max {int(fbuf.max())}). REFUSED.")

    tet, pyr, pri, hexa, cell_faces, masks = build_elements(
        widths, fbuf, own, nbr, n_cells)
    verified = verify_elements(widths, fbuf, cell_faces, masks, tet, pyr, pri, hexa)
    n_elem = len(tet) + len(pyr) + len(pri) + len(hexa)
    if n_elem != n_cells:
        raise Refusal(
            f"ELEMENT: {n_elem} elements classified against {n_cells} cells. REFUSED -- "
            f"the cell count is the FIRST of the three quantities R0-G2b grades and it "
            f"must come out of the classification exactly, never by adjustment.")

    patches = read_boundary(need["boundary"])
    tri_rows, quad_rows, tri_tags, quad_tags, groups = [], [], [], [], []
    n_int = len(nbr)
    for i, (name, nf, st, code) in enumerate(patches, start=1):
        if st < n_int or st + nf > len(widths):
            raise Refusal(
                f"BOUNDARY: patch '{name}' spans faces [{st}, {st + nf}) which is not "
                f"inside the boundary range [{n_int}, {len(widths)}). REFUSED.")
        idx = np.arange(st, st + nf)
        w = widths[idx]
        for want_w, rows, tags in ((3, tri_rows, tri_tags), (4, quad_rows, quad_tags)):
            sel = idx[w == want_w]
            if len(sel) == 0:
                continue
            rows.append(fbuf[sel][:, :want_w])
            tags.append(np.full(len(sel), i, dtype=np.int64))
        groups.append((i, code, name))

    tri = np.concatenate(tri_rows) if tri_rows else np.zeros((0, 3), dtype=np.int64)
    quad = np.concatenate(quad_rows) if quad_rows else np.zeros((0, 4), dtype=np.int64)
    ttag = np.concatenate(tri_tags) if tri_tags else np.zeros(0, dtype=np.int64)
    qtag = np.concatenate(quad_tags) if quad_tags else np.zeros(0, dtype=np.int64)
    n_bnd = len(tri) + len(quad)
    if n_bnd != len(widths) - n_int:
        raise Refusal(
            f"BOUNDARY: patches cover {n_bnd} faces and the mesh has "
            f"{len(widths) - n_int} boundary faces. REFUSED -- an uncovered boundary "
            f"face would silently drop out of the per-patch counts R0-G2b grades.")

    size = write_ugrid(out, endian, fortran, pts, tri, quad, ttag, qtag,
                       tet, pyr, pri, hexa)
    n_groups = write_mapbc(mapbc_out, groups)
    return dict(
        case=str(case), ugrid=str(out), mapbc=str(mapbc_out), bytes=size,
        variant=variant, endian=("big" if endian == ">" else "little"), fortran=fortran,
        nodes=len(pts), cells=n_cells, boundary_faces=n_bnd,
        tet=len(tet), pyr=len(pyr), prism=len(pri), hex=len(hexa),
        elements_verified=verified,
        patches={name: nf for name, nf, _, _ in patches},
        mapbc_groups=n_groups,
        mapbc_group_note=(
            "ONE GROUP PER PATCH. The source's per-tag multiplicity is NOT in the "
            "polyMesh and cannot be recovered; the group count therefore does NOT "
            "round-trip and is NOT one of the three quantities section 4 grades."),
    )


# --------------------------------------------------------- the plant (rule 3 / C9)
def drop_one_boundary_face(src: Path, dst: Path) -> dict:
    """Copy `src` to `dst` with exactly ONE boundary face removed. Section 7, row 7.

    Rewrites the header count, drops the face's connectivity bytes AND its tag, and
    recomputes both Fortran markers where present. IT CHECKS ITS OWN BYTE ARITHMETIC:
    a plant that quietly does nothing certifies a comparator that can see nothing, which
    is exactly how `analyse_rung0.py`'s C2 plant was caught deleting a triangle from a
    grid whose every boundary face is a quad.
    """
    variant = variant_of(src)
    endian, fortran = LAYOUTS[variant]
    raw = src.read_bytes()
    off = 4 if fortran else 0
    nN, nT, nQ, nTet, nPyr, nPri, nHex = struct.unpack(endian + "7i",
                                                       raw[off:off + 28])
    if nT > 0:
        kind, conn = "tri", _TRI
    elif nQ > 0:
        kind, conn = "quad", _QUAD
    else:
        raise Refusal(f"PLANT: {src} has no boundary faces at all to delete.")

    start = (4 + 28 + 8) if fortran else 28
    off_tri = start + nN * _NODE
    off_quad = off_tri + nT * _TRI
    off_ttag = off_quad + nQ * _QUAD
    off_qtag = off_ttag + nT * _TAG
    rest = off_qtag + nQ * _TAG
    tail = raw[rest:len(raw) - (4 if fortran else 0)]

    if kind == "tri":
        body = b"".join([raw[start:off_tri], raw[off_tri + conn:off_quad],
                         raw[off_quad:off_ttag], raw[off_ttag + _TAG:off_qtag],
                         raw[off_qtag:rest], tail])
        counts = (nN, nT - 1, nQ, nTet, nPyr, nPri, nHex)
    else:
        body = b"".join([raw[start:off_tri], raw[off_tri:off_quad],
                         raw[off_quad + conn:off_ttag], raw[off_ttag:off_qtag],
                         raw[off_qtag + _TAG:rest], tail])
        counts = (nN, nT, nQ - 1, nTet, nPyr, nPri, nHex)

    want = expected_size(counts, fortran)
    with open(dst, "wb") as f:
        if fortran:
            f.write(struct.pack(endian + "i", 28))
        f.write(struct.pack(endian + "7i", *counts))
        if fortran:
            f.write(struct.pack(endian + "i", 28))
            f.write(struct.pack(endian + "i", len(body)))
        f.write(body)
        if fortran:
            f.write(struct.pack(endian + "i", len(body)))
    got = dst.stat().st_size
    shrank = len(raw) - got
    if got != want or shrank != conn + _TAG:
        raise Refusal(
            f"PLANT DID NOT PLANT: {dst} is {got} bytes, arithmetic requires {want}, "
            f"and the file shrank by {shrank} where one {kind} face is "
            f"{conn + _TAG} bytes. REFUSED -- a control that quietly does nothing "
            f"certifies a reader that can see nothing (rule 3).")
    return dict(kind=kind, bytes_removed=shrank, before=len(raw), after=got)


# ------------------------------------------------------------------- the round trip
def _reader():
    """`read_ugrid_identity`, imported the way `analyse_rung0.py` imports it."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import read_ugrid_identity as R  # noqa: PLC0415
    return R


def compare_three(src_reading: dict, out_reading: dict) -> dict:
    """R0-G2b's three quantities and NOTHING ELSE. Exact integers, no tolerance."""
    s_p, o_p = src_reading["patches"], out_reading["patches"]
    mism = {k: (s_p.get(k), o_p.get(k)) for k in set(s_p) | set(o_p)
            if s_p.get(k) != o_p.get(k)}
    checks = {
        "cell_count_exact": src_reading["cells"] == out_reading["cells"],
        "patch_names_set_equal": set(s_p) == set(o_p),
        "per_patch_face_counts_exact": not mism,
    }
    return dict(checks=checks, per_patch_mismatches=mism,
                source_cells=src_reading["cells"], written_cells=out_reading["cells"],
                equal=all(checks.values()))


def roundtrip(case: Path, source: Path, source_mapbc: Path, out: Path,
              overwrite: bool = False) -> dict:
    """Export, re-read with the R0-G2a reader, and REFUSE to report equality unplanted.

    THE ORDER IS THE POINT. The plant runs BEFORE the equality is believed: a scratch
    copy of this run's OWN OUTPUT loses one boundary face and the SAME comparison must
    go unequal. If it does not, the equality is `NOT A RESULT` at exit 2 and no number
    from this function may be quoted.
    """
    R = _reader()
    written = export(case, out, overwrite=overwrite)
    mapbc_out = Path(written["mapbc"])
    src = R.read_source_identity(source, source_mapbc)
    got = R.read_source_identity(out, mapbc_out)
    cmp_clean = compare_three(src, got)

    scratch = Path(tempfile.mkdtemp(prefix="r0g2b_plant_"))
    try:
        planted_path = scratch / out.name
        plant = drop_one_boundary_face(Path(out), planted_path)
        planted_reading = R.read_source_identity(planted_path, mapbc_out)
        cmp_planted = compare_three(src, planted_reading)
        control_fired = not cmp_planted["equal"]
    finally:
        for p in sorted(scratch.rglob("*"), reverse=True):
            p.unlink()
        scratch.rmdir()

    return dict(
        grid=case.name, written=written,
        source_reading=src, written_reading=got,
        R0_G2b=dict(
            checks=cmp_clean["checks"],
            per_patch_mismatches=cmp_clean["per_patch_mismatches"],
            source_cells=cmp_clean["source_cells"],
            written_cells=cmp_clean["written_cells"],
            verdict=("PASS" if (cmp_clean["equal"] and control_fired)
                     else "NOT A RESULT" if not control_fired else "GATE FAIL")),
        C9=dict(
            control="C9 foam_to_ugrid round trip (registration section 7, row 7)",
            fired=control_fired,
            expected="drop one face from the written file -> R0-G2b reports unequal",
            plant=plant,
            saw=(f"planted per-patch mismatches "
                 f"{cmp_planted['per_patch_mismatches']}, cells "
                 f"{cmp_planted['source_cells']} vs {cmp_planted['written_cells']}")),
    )


# ---------------------------------------------------------------------- the selftest
#: One hand-built single-element polyMesh per AFLR3 volume-element type.
#: (name, points, faces as (kind, node tuple), patch split, expected element key).
#: ALL FOUR TYPES ARE HERE BECAUSE THREE OF THEM WERE NOT, AND THE MISSING ONE SHIPPED
#: A DEFECT. The first version of this selftest built a hex only; the pyramid templates
#: were wrong and nothing in the suite could see it, because none of the three DPW5
#: grids contains a pyramid either. A selftest whose population omits an element type
#: certifies a writer that cannot write it.
#:
#: ⚠ THE MUTATION IS PER TYPE, AND THE REASON IS A MEASURED PROPERTY OF THE ELEMENTS
#: RATHER THAN A CONVENIENCE. Two of the four types have SYMMETRIES that a node SWAP
#: cannot see, and the first version of this suite chose swaps that landed on both:
#:   * TET -- `TET_T` is all four 3-subsets of {0,1,2,3}, so EVERY ONE of the 24
#:     permutations of a tetrahedron's node list regenerates the SAME four face sets.
#:     A tet's positional convention is entirely unconstrained by its own faces. The
#:     mutation is therefore a SUBSTITUTION (node 3 overwritten with node 0), which the
#:     verification limb can and must catch. Swapping two tet nodes is undetectable and
#:     that is CORRECT, not a hole -- but a control that cannot fire is worse than none.
#:   * PYRAMID -- swapping the two DIAGONAL base nodes is a 180-degree rotation of the
#:     element and leaves every face set unchanged. The mutation moves the APEX into a
#:     base slot instead, which no symmetry can absorb.
#: Prism and hex have no such symmetry on the chosen pair, so both use a plain swap.
_SYNTH = {
    "tet1": dict(
        pts=[(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
        faces=[(0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3)],
        key="tet", split=(1, 3), mut=("dup", 3, 0)),
    "pyr1": dict(
        pts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0.5, 0.5, 1)],
        faces=[(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
        key="pyr", split=(1, 4), mut=("swap", 2, 0)),
    "pri1": dict(
        pts=[(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1)],
        faces=[(0, 1, 2), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)],
        key="prism", split=(2, 3), mut=("swap", 0, 5)),
    "hex1": dict(
        pts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
             (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
        faces=[(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
               (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
        key="hex", split=(2, 4), mut=("swap", 0, 7)),
}


def _build_synth(root: Path, name: str, spec: dict) -> Path:
    """Write one single-element polyMesh by hand. Every face is a boundary face."""
    pm = root / name / "constant" / "polyMesh"
    pm.mkdir(parents=True)
    nf = len(spec["faces"])
    a, b = spec["split"]
    (pm / "points").write_text("FoamFile{}\n\n%d\n(\n%s\n)\n" % (
        len(spec["pts"]), "\n".join("(%g %g %g)" % p for p in spec["pts"])))
    (pm / "faces").write_text("FoamFile{}\n\n%d\n(\n%s\n)\n" % (
        nf, "\n".join("%d(%s)" % (len(f), " ".join(map(str, f)))
                      for f in spec["faces"])))
    (pm / "owner").write_text(
        "FoamFile{}\n// note: nCells:1 nFaces:%d nInternalFaces:0\n\n%d\n(\n%s\n)\n"
        % (nf, nf, "\n".join(["0"] * nf)))
    (pm / "neighbour").write_text("FoamFile{}\n\n0\n(\n\n)\n")
    (pm / "boundary").write_text(
        "FoamFile{}\n// * * *\n2\n(\n"
        "    lid\n    {\n        type wall;\n        nFaces %d;\n"
        "        startFace 0;\n        // AFLR3 mapbc code 4000\n    }\n"
        "    sides\n    {\n        type patch;\n        nFaces %d;\n"
        "        startFace %d;\n        // AFLR3 mapbc code 5000\n    }\n)\n"
        % (a, b, a))
    return root / name


def selftest() -> int:
    """ABSOLUTE controls on hand-built meshes whose answers are known independently.

    Every other check in this file is DIFFERENTIAL, and a writer producing a constant
    WRONG answer moves correctly around all of them. This builds ONE TETRAHEDRON, ONE
    PYRAMID, ONE PRISM and ONE HEXAHEDRON as OpenFOAM polyMeshes by hand, exports each,
    exports the hex in all four layout variants, and requires the R0-G2a reader to
    return the counts written on this page. Each type also carries a MUTATION control:
    two nodes of the written element are swapped and `verify_elements` MUST refuse, so
    the verification limb is shown to be live for every element type rather than for
    the one that happened to be tested.
    """
    R = _reader()
    results, ok = [], True
    scratch = Path(tempfile.mkdtemp(prefix="foam_to_ugrid_selftest_"))
    try:
        for name, spec in _SYNTH.items():
            case = _build_synth(scratch, name, spec)
            a, b = spec["split"]
            variants = sorted(LAYOUTS) if name == "hex1" else ["b8"]
            for variant in variants:
                out = scratch / f"{name}.{variant}.ugrid"
                info = export(case, out)
                back = R.read_source_identity(out, Path(info["mapbc"]))
                want = {"lid": a, "sides": b}
                good = (back["cells"] == 1 and back["patches"] == want
                        and info[spec["key"]] == 1
                        and back["boundary_faces"] == a + b)
                ok &= good
                results.append(dict(
                    control=f"ABSOLUTE one-{spec['key']} export, {variant} variant",
                    fired=good,
                    expected=f"cells 1, {spec['key']} 1, {want}, bnd {a + b}",
                    saw=(f"cells {back['cells']}, {spec['key']} {info[spec['key']]}, "
                         f"{back['patches']}, bnd {back['boundary_faces']}, "
                         f"endian {back['endian']}, fortran {back['fortran']}")))

                plant_dir = scratch / f"plant_{name}_{variant}"
                plant_dir.mkdir()
                planted = plant_dir / out.name
                pl = drop_one_boundary_face(out, planted)
                after = R.read_source_identity(planted, Path(info["mapbc"]))
                fired = (sum(after["patches"].values()) == a + b - 1
                         and after["patches"] != want)
                ok &= fired
                results.append(dict(
                    control=f"C9 PLANT, one-{spec['key']} {variant}: drop one face",
                    fired=fired,
                    expected=f"the comparison goes UNEQUAL; bnd {a + b} -> {a + b - 1}",
                    saw=f"{after['patches']}, removed {pl['bytes_removed']} bytes"))

            # --- MUTATION: swap two nodes of the written element; verify must REFUSE.
            pm = case / "constant" / "polyMesh"
            widths, fbuf = read_faces(pm / "faces")
            own, nbr = read_labels(pm / "owner"), read_labels(pm / "neighbour")
            tet, pyr, pri, hexa, cf, masks = build_elements(widths, fbuf, own, nbr, 1)
            slot = {"tet": 0, "pyr": 1, "prism": 2, "hex": 3}[spec["key"]]
            arrs = [tet, pyr, pri, hexa]
            arrs[slot] = arrs[slot].copy()
            kind, i, j = spec["mut"]
            if kind == "swap":
                arrs[slot][0, [i, j]] = arrs[slot][0, [j, i]]
                what = f"swap local nodes {i} and {j}"
            else:
                arrs[slot][0, i] = arrs[slot][0, j]
                what = f"overwrite local node {i} with node {j}"
            try:
                verify_elements(widths, fbuf, cf, masks, *arrs)
                fired, saw = False, f"a corrupted {spec['key']} node list PASSED verify"
            except Refusal as exc:
                fired, saw = "ELEMENT VERIFY" in str(exc), str(exc)[:140]
            ok &= bool(fired)
            results.append(dict(
                control=(f"MUTATION [{spec['key']}]: {what} -> verify must REFUSE"),
                fired=bool(fired),
                expected="Refusal from verify_elements; the limb is not inert",
                saw=saw))

        # --- a refusal control: the writer must REFUSE a variant it cannot honour.
        for name, why in (("x.b4.ugrid", "4-byte reals"),
                          ("x.ugrid", "no variant named")):
            try:
                variant_of(scratch / name)
                fired, saw = False, "ACCEPTED a variant it must refuse"
            except Refusal as exc:
                fired, saw = True, str(exc)[:120]
            ok &= fired
            results.append(dict(control=f"REFUSAL on {name} ({why})", fired=fired,
                                expected="Refusal, never a silent default", saw=saw))

        # --- a refusal control: an absent input must never read clean.
        try:
            export(scratch / "does_not_exist", scratch / "z.b8.ugrid")
            fired, saw = False, "an ABSENT case exported without refusing"
        except Refusal as exc:
            fired, saw = "ABSENT NEVER READS CLEAN" in str(exc), str(exc)[:120]
        ok &= bool(fired)
        results.append(dict(control="REFUSAL on an absent case directory", fired=bool(fired),
                            expected="Refusal naming ABSENT NEVER READS CLEAN", saw=saw))

    finally:
        for p in sorted(scratch.rglob("*"), reverse=True):
            (p.rmdir() if p.is_dir() else p.unlink())
        scratch.rmdir()

    print("=== foam_to_ugrid.py SELFTEST (standing rule 3) ===")
    for r in results:
        print(f"  [{'FIRED' if r['fired'] else 'DID NOT FIRE':>12}] {r['control']}")
        print(f"                 expected: {r['expected']}")
        print(f"                 saw     : {r['saw']}")
    if not ok:
        print("\nNOT A RESULT: a control did not fire. Nothing this writer produces "
              "may be quoted until they all do (standing rule 3). REFUSED at exit 2.")
        return EXIT_REFUSE
    print(f"\nALL {len(results)} CONTROLS FIRED.")
    return 0


# ------------------------------------------------------------------------------ CLI
def main(argv):
    _ast_self_check()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--case", help="OpenFOAM case directory holding constant/polyMesh")
    ap.add_argument("--out", help="output UGRID, named <name>.<b8|lb8|r8|lr8>.ugrid")
    ap.add_argument("--mapbc", help="output .mapbc (default: <out> with .mapbc)")
    ap.add_argument("--source", nargs=2, metavar=("UGRID", "MAPBC"),
                    help="the SOURCE grid, for --roundtrip")
    ap.add_argument("--roundtrip", action="store_true",
                    help="export, re-read with the R0-G2a reader, and grade R0-G2b")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    try:
        if a.selftest:
            return selftest()
        if not a.case or not a.out:
            raise Refusal("--case and --out are required (or --selftest).")
        if a.roundtrip:
            if not a.source:
                raise Refusal("--roundtrip requires --source <UGRID> <MAPBC>.")
            res = roundtrip(Path(a.case), Path(a.source[0]), Path(a.source[1]),
                            Path(a.out), overwrite=a.overwrite)
            print(json.dumps(res, indent=2, sort_keys=True, default=str))
            if not res["C9"]["fired"]:
                return EXIT_REFUSE
            return 0 if res["R0_G2b"]["verdict"] == "PASS" else EXIT_REFUSE
        res = export(Path(a.case), Path(a.out), a.mapbc, overwrite=a.overwrite)
        print(json.dumps(res, indent=2, sort_keys=True, default=str))
        return 0
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
