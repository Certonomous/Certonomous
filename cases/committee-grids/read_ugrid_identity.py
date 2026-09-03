#!/usr/bin/env python3
"""read_ugrid_identity.py -- THE INDEPENDENT READER of RUNG 0.

Registered at verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md section 9
("independent reader (does not exist; to be written)"), frozen d127d83d.

WHAT "INDEPENDENT" MEANS HERE, AND IT IS THE WHOLE POINT.  Section 4's R0-G2a requires
"An INDEPENDENT READER -- not `ugrid_to_foam.py`, and NOT IMPORTING IT".  This file
therefore carries its OWN layout sniffer, its OWN header arithmetic and its OWN
`.mapbc` parser.  It does not `import ugrid_to_foam`, does not read that file, and
shares no constant with it.  If the converter and this reader agree, they agree from
two independent readings of the same bytes; if the converter were wrong in a way this
reader copied, the round-trip check would be a mirror rather than a test.

`inspect_ugrid.py` in this same directory DOES `from ugrid_to_foam import sniff_layout`
and is therefore NOT usable for R0-G2a.  That is why this file exists at all rather
than the existing one being wired up, and it is said here so a later reader does not
"simplify" this back into a dependency.

THE LAYOUT SNIFFER IS SELF-VALIDATING, WHICH THE ORIGINAL'S IS NOT.  A UGRID file's
header is seven int32; nothing in it says which endianness or whether the stream
carries Fortran record markers.  Rather than guess from a magnitude heuristic, this
reader computes the EXACT byte length the file must have under each of the four
candidate layouts and accepts the one that matches the actual file size to the byte.
Zero matches REFUSES.  More than one match REFUSES.  A layout that reproduces the file
size exactly across four independent element counts is not a guess.

NO `assert` ANYWHERE (L-332): `python3 -O` deletes them, and a check that vanishes
under a flag is not a check.  Every refusal here is a `raise` or a `sys.exit(2)`.

STANDING RULE 3.  Every reader below has a planted control in `planted_controls.py`'s
sense -- see analyse_rung0.py, which runs them BEFORE any measurement counts and
refuses if a plant does not fire.  A zero from a reader not shown able to see a
non-zero is not evidence.

USAGE
    python3 read_ugrid_identity.py --source <file.ugrid> <file.mapbc>
    python3 read_ugrid_identity.py --polymesh <case_dir>
    python3 read_ugrid_identity.py --checkmesh <log.checkMesh>
Each prints one JSON object on stdout.  Exit 0 = read; 2 = REFUSED.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
from pathlib import Path

EXIT_REFUSE = 2

# UGRID element strides, in BYTES per element, at 4-byte labels and 8-byte reals.
# nodes 3 x f8; boundary tri 3 x i4; boundary quad 4 x i4; one i4 tag per boundary
# face; then the volume elements by their node counts.
_NODE = 24
_TRI = 12
_QUAD = 16
_TAG = 4
_TET, _PYR, _PRI, _HEX = 16, 20, 24, 32


class Refusal(Exception):
    """A condition that must stop this reader under any flag."""


# --------------------------------------------------------------------------- layout
def _header_at(raw: bytes, endian: str, fortran: bool):
    """The seven counts, or None if the file is too short to hold a header."""
    off = 4 if fortran else 0
    if len(raw) < off + 28:
        return None
    return struct.unpack(endian + "7i", raw[off:off + 28])


def expected_size(counts, fortran: bool) -> int:
    """The EXACT byte length a UGRID file must have for these seven counts.

    Fortran unformatted adds a 4-byte length marker before AND after each record.
    The AFLR3 files this lab holds are written as TWO records -- the header, then
    everything else -- which is what `ugrid_to_foam.sniff_layout`'s `read(4)` /
    `read(8)` offsets imply, and 4 + 28 + 4 + 4 + <payload> + 4 = payload + 44.
    Raw C stream adds nothing.
    """
    nN, nT, nQ, nTet, nPyr, nPri, nHex = counts
    payload = (nN * _NODE + nT * _TRI + nQ * _QUAD + (nT + nQ) * _TAG
               + nTet * _TET + nPyr * _PYR + nPri * _PRI + nHex * _HEX)
    return 28 + payload + (16 if fortran else 0)


def sniff_layout(path):
    """(endian, fortran, counts, header_offset). SELF-VALIDATING, never a heuristic.

    Refuses on zero matches and on more than one, because an ambiguous layout read as
    a confident one is precisely how a silently-wrong cell count enters a gate.
    """
    path = Path(path)
    size = path.stat().st_size
    with open(path, "rb") as f:
        raw = f.read(64)
    hits = []
    for endian in ("<", ">"):
        for fortran in (False, True):
            c = _header_at(raw, endian, fortran)
            if c is None or any(x < 0 for x in c) or c[0] <= 0:
                continue
            if expected_size(c, fortran) == size:
                hits.append((endian, fortran, c, 4 if fortran else 0))
    if not hits:
        raise Refusal(
            f"LAYOUT: no (endian, fortran) combination reproduces the actual file size "
            f"{size} for {path}. The header was read four ways and none is consistent "
            f"with the bytes on disk. REFUSED rather than guessed -- a mis-sniffed "
            f"layout yields a cell count that is wrong and looks fine.")
    if len(hits) > 1:
        raise Refusal(
            f"LAYOUT: {len(hits)} layouts all reproduce size {size} for {path}: "
            f"{[(h[0], h[1]) for h in hits]}. Ambiguous. REFUSED -- never choose.")
    return hits[0]


# --------------------------------------------------------------------------- source
def read_mapbc(path):
    """{tag: name} from an AFLR3 `.mapbc`.

    Format: a count on line 1, then `<tag> <bc-type> <name>` per line. The BC TYPE IS
    DELIBERATELY DISCARDED: section 4's R0-G1 is about patch IDENTITY (names), and the
    DPW5 file gives eighteen tags across three names while HLPW6 gives seventy-three
    across fourteen. Merging is BY NAME, which is exactly the property Plot3D destroyed.
    """
    path = Path(path)
    txt = path.read_text(errors="replace").splitlines()
    if not txt:
        raise Refusal(f"MAPBC: {path} is empty")
    try:
        declared = int(txt[0].strip())
    except ValueError:
        raise Refusal(f"MAPBC: {path} line 1 is not a group count: {txt[0]!r}")
    tags = {}
    for ln in txt[1:]:
        parts = ln.split()
        if len(parts) < 3:
            continue
        try:
            t = int(parts[0])
        except ValueError:
            continue
        tags[t] = parts[2]
    if len(tags) != declared:
        raise Refusal(
            f"MAPBC: {path} declares {declared} groups on line 1 and {len(tags)} "
            f"parsed. REFUSED rather than read short -- a dropped group is a dropped "
            f"patch and would make a face-count identity pass for the wrong reason.")
    return tags


def read_source_identity(ugrid, mapbc):
    """(cells, {patch name -> boundary face count}) read straight from the SOURCE bytes.

    The three quantities Sanaa named, on the source side. Cells are the sum of the four
    volume-element counts in the header; the per-patch face counts come from the
    per-face tag arrays, grouped through the `.mapbc` BY NAME.
    """
    ugrid = Path(ugrid)
    endian, fortran, counts, off = sniff_layout(ugrid)
    nN, nT, nQ, nTet, nPyr, nPri, nHex = counts
    cells = nTet + nPyr + nPri + nHex
    names = read_mapbc(mapbc)

    # The tag arrays sit after the header, the nodes and the two connectivity blocks.
    #
    # THE FORTRAN OFFSET IS 8, NOT 4, AND THE FIRST DRAFT OF THIS LINE HAD IT WRONG.
    # A `.r8.ugrid` is TWO Fortran unformatted records -- the seven-int header, then
    # everything else -- so after the header come the header record's TRAILING marker
    # AND the data record's LEADING marker: 4 + 28 + 4 + 4 = 40, not 36. The four-byte
    # version read tags at [660176, 657041, 654993] on the three DPW5 grids, values
    # that are not tags at all, and the unnamed-tag refusal below is what caught it.
    # RECORDED RATHER THAN QUIETLY FIXED: this reader's refusal found its own bug
    # before any gate consumed the number, which is the entire case for refusing
    # instead of degrading. HLPW6 (`.b8`, a raw C stream) was never affected and read
    # correctly on the first attempt, so a reader tested on ONE grid would have shipped
    # this defect -- the population, not the single case, is what validated it.
    payload_start = (4 + 28 + 8) if fortran else 28
    tag_off = payload_start + nN * _NODE + nT * _TRI + nQ * _QUAD
    with open(ugrid, "rb") as f:
        f.seek(tag_off)
        tri_tags = struct.unpack(endian + f"{nT}i", f.read(nT * _TAG)) if nT else ()
        quad_tags = struct.unpack(endian + f"{nQ}i", f.read(nQ * _TAG)) if nQ else ()

    per_tag = {}
    for t in tri_tags:
        per_tag[t] = per_tag.get(t, 0) + 1
    for t in quad_tags:
        per_tag[t] = per_tag.get(t, 0) + 1

    unknown = sorted(t for t in per_tag if t not in names)
    if unknown:
        raise Refusal(
            f"TAGS: boundary tags {unknown} appear in {ugrid.name} and are NOT named in "
            f"the .mapbc. REFUSED -- an unnamed tag is a patch with no identity, and "
            f"silently dropping it would make the face-count sum agree by losing faces.")

    patches = {}
    for t, n in per_tag.items():
        patches[names[t]] = patches.get(names[t], 0) + n

    return dict(
        source=str(ugrid), mapbc=str(mapbc),
        endian=("little" if endian == "<" else "big"), fortran=fortran,
        nodes=nN, boundary_tri=nT, boundary_quad=nQ,
        tet=nTet, pyr=nPyr, prism=nPri, hex=nHex,
        cells=cells, boundary_faces=nT + nQ,
        distinct_mapbc_names=len(set(names.values())),
        mapbc_groups=len(names),
        patches=dict(sorted(patches.items())),
    )


# ------------------------------------------------------------------------- polyMesh
# BOTH HEADER FORMS, AND THE FIRST DRAFT KNEW ONLY ONE -- THE SAME DEFECT CLASS AS THE
# ASPECT-RATIO `=` / `:` TRAP THAT CONTROL C5 EXISTS FOR, COMMITTED IN THIS VERY FILE.
# OpenFOAM's own mesh writer emits a quoted FoamFile key:
#     note        "nPoints:124865  nCells:122880  nFaces:370560  nInternalFaces:363648";
# but `ugrid_to_foam.py` is a hand-rolled writer and emits a COMMENT:
#     // note: nCells:638976 nFaces:1937920 nInternalFaces:1895936
# A reader matching only the quoted form read every OpenFOAM-written mesh correctly and
# EVERY MESH THIS RUNG ACTUALLY IMPORTS as "no note" -- which the reader then refused,
# producing a GATE FAIL on all four grids from a defect in the READER while the meshes
# were entirely sound. The numbers were on disk the whole time, in the other form.
_NOTE_QUOTED = re.compile(
    r'note\s+"[^"]*nCells:\s*(\d+)\s+nFaces:\s*(\d+)\s+nInternalFaces:\s*(\d+)')
_NOTE_COMMENT = re.compile(
    r'//\s*note:\s*nCells:\s*(\d+)\s+nFaces:\s*(\d+)\s+nInternalFaces:\s*(\d+)')
_BOUNDARY_ENTRY = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_.\-]*)\s*$\s*\{(.*?)\}", re.MULTILINE | re.DOTALL)
_NFACES = re.compile(r"\bnFaces\s+(\d+)\s*;")


def _list_body(path: Path):
    """(declared count, the value tokens) of an OpenFOAM ASCII list file.

    The count is the bare integer standing alone between the FoamFile block and the
    opening `(`. Returned separately from the values so a file whose DECLARED count
    disagrees with the number of values it actually holds can be refused rather than
    silently believed.
    """
    txt = path.read_text(errors="replace")
    op = txt.find("\n(")
    if op < 0:
        raise Refusal(f"POLYMESH: {path} has no list body.")
    head, body = txt[:op], txt[op + 2:]
    nums = [ln.strip() for ln in head.splitlines()
            if ln.strip().isdigit()]
    if not nums:
        raise Refusal(f"POLYMESH: {path} declares no list count before its body.")
    cl = body.rfind(")")
    return int(nums[-1]), (body[:cl] if cl >= 0 else body).split()


def read_polymesh_identity(case):
    """(cells, {patch name -> nFaces}) read from constant/polyMesh, WITHOUT checkMesh.

    THE THREE COUNTS ARE DERIVED FROM THE MESH ITSELF, and the header note -- in
    EITHER of its two forms -- is a CROSS-CHECK on them, never the sole source:

        nFaces         = the number of entries in `owner`      (its definition)
        nInternalFaces = the number of entries in `neighbour`  (its definition)
        nCells         = max(max(owner), max(neighbour)) + 1

    ⚠ `max(owner) + 1` IS ONLY A LOWER BOUND ON nCells, AND THE FIRST DRAFT USED IT.
    OpenFOAM's `owner` always holds the LOWER of a face's two cell indices, so the
    highest-indexed cells own NOTHING WHATEVER whenever every one of their faces has a
    lower-indexed neighbour -- which is the normal condition for an interior cell late
    in the renumbering. `neighbour` must therefore be scanned too. Measured, and this
    is why the cross-check below is not decorative: on HLPW6 the owner-only derivation
    gave 2,661,336 against a header of 2,661,338 -- SHORT BY EXACTLY TWO CELLS -- while
    all three DPW5 grids agreed to the cell. A READER VALIDATED ON THREE OF THE FOUR
    GRIDS WOULD HAVE SHIPPED THIS, and it would have produced a GATE FAIL on the one
    grid whose fourteen named patches the whole ladder is being built for.

    That ordering is deliberate and it is a repair. The first draft read the counts
    ONLY from a quoted FoamFile `note` and refused when it found none -- and
    `ugrid_to_foam.py`, a hand-rolled writer, emits the note as a COMMENT instead. The
    reader therefore refused all four imported meshes and the comparator reported GATE
    FAIL on grids that were entirely sound. A reading taken from a WRITER'S OPTIONAL
    ANNOTATION is hostage to which writer produced the file; a reading taken from the
    mesh's own lists is not. The note is now believed only insofar as it AGREES, and a
    disagreement REFUSES -- a header that contradicts the mesh it describes is a worse
    condition than a header that is missing.
    """
    pm = Path(case) / "constant" / "polyMesh"
    owner, bnd, nbr = pm / "owner", pm / "boundary", pm / "neighbour"
    for p in (owner, bnd, nbr):
        if not p.is_file():
            raise Refusal(f"POLYMESH: {p} is absent. ABSENT NEVER READS CLEAN.")

    n_faces, own_vals = _list_body(owner)
    if len(own_vals) != n_faces:
        raise Refusal(
            f"POLYMESH: {owner} declares {n_faces} entries and holds {len(own_vals)}. "
            f"REFUSED -- a list whose own count is wrong cannot be the source of a "
            f"cell count.")
    n_internal, nbr_vals = _list_body(nbr)
    if len(nbr_vals) != n_internal:
        raise Refusal(
            f"POLYMESH: {nbr} declares {n_internal} entries and holds {len(nbr_vals)}.")
    n_cells = max(max(int(v) for v in own_vals),
                  max((int(v) for v in nbr_vals), default=-1)) + 1

    head = owner.read_text(errors="replace")[:4000]
    m = _NOTE_QUOTED.search(head) or _NOTE_COMMENT.search(head)
    note_form = None
    if m:
        note_form = "quoted FoamFile key" if _NOTE_QUOTED.search(head) else "// comment"
        h_cells, h_faces, h_internal = (int(x) for x in m.groups())
        disagree = [f"{k}: header {a} vs derived {b}"
                    for k, a, b in (("nCells", h_cells, n_cells),
                                    ("nFaces", h_faces, n_faces),
                                    ("nInternalFaces", h_internal, n_internal))
                    if a != b]
        if disagree:
            raise Refusal(
                f"POLYMESH: {owner}'s header note ({note_form}) CONTRADICTS the mesh's "
                f"own lists: {disagree}. REFUSED -- never choose between them.")

    text = bnd.read_text(errors="replace")
    body = text.split("// * * *", 1)[-1]
    patches = {}
    for name, block in _BOUNDARY_ENTRY.findall(body):
        f = _NFACES.search(block)
        if f:
            patches[name] = int(f.group(1))
    if not patches:
        raise Refusal(f"POLYMESH: no patch entries parsed from {bnd}.")

    return dict(
        case=str(case), cells=n_cells, faces=n_faces, internal_faces=n_internal,
        boundary_faces=n_faces - n_internal,
        n_patches=len(patches), patches=dict(sorted(patches.items())),
        default_faces_present=("defaultFaces" in patches),
        counts_basis="DERIVED from the mesh's own lists (nFaces = len(owner), "
                     "nInternalFaces = len(neighbour), nCells = max(owner)+1); the "
                     "header note is a CROSS-CHECK and a disagreement REFUSES",
        header_note_form=note_form,
    )


# ------------------------------------------------------------------------ checkMesh
# BOTH LABEL FORMS. Section 7's control, and it is not hypothetical: on this box a
# reader matching only `Max aspect ratio = ` sees the healthy logs and MISSES EXACTLY
# THE PATHOLOGICAL ONES, because checkMesh switches to `***High aspect ratio cells
# found, Max aspect ratio: <v>` when the value is high. Both are matched here.
# THE NUMBER PATTERN IS ANCHORED, NOT A CHARACTER CLASS, AND THE FIRST DRAFT WAS NOT.
# `[0-9.eE+-]+` greedily swallows the SENTENCE-ENDING PERIOD that checkMesh writes:
# `Min volume = 1.02355e-05. Max volume = ...` yielded the token '1.02355e-05.' and
# float() raised. Caught on the first real log, on BOTH label forms, before any gate
# consumed a value -- but a `try/except` around that float() would have turned the
# same defect into a silent `None`, and a missing R0-G3 field is a GATE FAIL. The
# fix is a pattern that cannot match the period, not a rescue that hides it.
_NUM = r"([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)"

_Q = {
    "faces": re.compile(r"^\s*faces:\s*(\d+)", re.MULTILINE),
    "internal_faces": re.compile(r"^\s*internal faces:\s*(\d+)", re.MULTILINE),
    "cells": re.compile(r"^\s*cells:\s*(\d+)", re.MULTILINE),
    "max_non_orthogonality": re.compile(
        r"Mesh non-orthogonality Max:\s*" + _NUM),
    "severe_non_ortho_faces": re.compile(
        r"Number of severely non-orthogonal \(> 70 degrees\) faces:\s*(\d+)"),
    "max_skewness": re.compile(r"Max skewness\s*=\s*" + _NUM),
    "min_cell_volume": re.compile(r"Min volume\s*=\s*" + _NUM),
    "max_cell_volume": re.compile(r"Max volume\s*=\s*" + _NUM),
    "regions": re.compile(r"Number of regions:\s*(\d+)"),
    "geometric_directions": re.compile(
        r"Mesh has (\d+) geometric \(non-empty/wedge\) directions"),
}
_AR_EQ = re.compile(r"Max aspect ratio\s*=\s*" + _NUM)
_AR_COLON = re.compile(r"Max aspect ratio:\s*" + _NUM)

# EVERY VERDICT STRING checkMesh CAN PRINT. Captured so it can be shown to have been
# DISCARDED, never so it can be read. Measured on this box: `Non-orthogonality check
# OK.` is printed at 89.71, 89.94 and 89.9985 degrees, and in the lab's own R1-M0 run
# it was printed TWO LINES BELOW 88.889. A reader that takes the verdict line records
# a 90-degree mesh as passing.
_VERDICT = re.compile(
    r"^.*(Non-orthogonality check OK\.|Mesh OK\.|Failed \d+ mesh check).*$",
    re.MULTILINE)


def read_checkmesh_quality(log):
    """Every R0-G3 field, PARSED NUMERICALLY. The verdict line is captured and DISCARDED.

    An ABSENT log reads ABSENT. IT NEVER READS CLEAN (registration section 6).
    """
    log = Path(log)
    if not log.is_file():
        return dict(checkMesh_log=str(log), state="ABSENT")
    txt = log.read_text(errors="replace")

    out = {"checkMesh_log": str(log.resolve()), "state": "READ"}
    for k, rx in _Q.items():
        m = rx.search(txt)
        if m is None:
            out[k] = None
        elif k in ("faces", "internal_faces", "cells", "severe_non_ortho_faces",
                   "regions", "geometric_directions"):
            out[k] = int(m.group(1))
        else:
            out[k] = float(m.group(1))

    # Aspect ratio: the `=` form first, then the `:` form. `aspect_ratio_flagged` is
    # TRUE exactly when checkMesh took the `***High aspect ratio` branch.
    eq, colon = _AR_EQ.search(txt), _AR_COLON.search(txt)
    if eq:
        out["max_aspect_ratio"] = float(eq.group(1))
        out["aspect_ratio_flagged"] = False
        out["aspect_ratio_label_form"] = "="
    elif colon:
        out["max_aspect_ratio"] = float(colon.group(1))
        out["aspect_ratio_flagged"] = True
        out["aspect_ratio_label_form"] = ":"
    else:
        out["max_aspect_ratio"] = None
        out["aspect_ratio_flagged"] = None
        out["aspect_ratio_label_form"] = None

    # DERIVED, and labelled as derived -- checkMesh prints no such quantity.
    lo, hi = out.get("min_cell_volume"), out.get("max_cell_volume")
    out["cell_volume_ratio"] = (hi / lo) if (lo and hi and lo != 0) else None
    out["cell_volume_ratio_basis"] = "DERIVED (max/min), NOT a checkMesh output"

    vs = _VERDICT.findall(txt)
    out["verdict_line_IGNORED_NEVER_A_GATE"] = vs[:4]
    out["how_the_number_is_read"] = (
        "PARSED off the named maximum lines. checkMesh's own verdict strings are "
        "captured above solely to show they were DISCARDED: on this box "
        "`Non-orthogonality check OK.` is printed at 89.71, 89.94 and 89.9985 degrees.")
    return out


# ------------------------------------------------------------------------------ CLI
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--source", nargs=2, metavar=("UGRID", "MAPBC"))
    g.add_argument("--polymesh", metavar="CASE_DIR")
    g.add_argument("--checkmesh", metavar="LOG")
    a = ap.parse_args(argv)
    try:
        if a.source:
            out = read_source_identity(a.source[0], a.source[1])
        elif a.polymesh:
            out = read_polymesh_identity(a.polymesh)
        else:
            out = read_checkmesh_quality(a.checkmesh)
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSE
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
