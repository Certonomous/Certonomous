#!/usr/bin/env python3
"""analyse_rung0.py -- THE COMPARATOR for RUNG 0, at the path section 9 registered.

Registration: verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md, FROZEN at
commit d127d83d4ebf4caaaf0c12c39a063c5f624a03a4 (2026-09-03T17:17:27Z).

WHAT IT GRADES, AND WHAT IT CANNOT.
    R0-G1  patch identity preserved                      -- GRADED
    R0-G2a round-trip, comparison limb                   -- GRADED
    R0-G2b round-trip, writer limb                       -- CANNOT RUN. The writer
           `cases/committee-grids/foam_to_ugrid.py` DOES NOT EXIST; section 9 of the
           frozen registration says so in terms.
    R0-G3  measured quality reported, NOT gated          -- GRADED (on presence only)
    R0-G4  age guard + no-clobber guard                  -- GRADED

⚠ THEREFORE THIS COMPARATOR CANNOT EMIT `PASS` FOR THE RUNG, AND REFUSES TO.  Section
4's label is explicit: "`PASS` -- R0-G1, R0-G2a, R0-G2b hold on ALL FOUR grids and
R0-G3 is complete on all four."  The rung's verdict is the CONJUNCTION over four grids
AND over all of G1/G2a/G2b.  With one conjunct unrunnable the conjunction is not
false, it is UNEVALUATED, and the honest label from CLAUDE.md rule 1's fixed
vocabulary is `PENDING` -- the display/queue state meaning NOT YET RUN.  It is NEVER
used here to soften a failure: a gate that actually FAILS on a grid still produces
`GATE FAIL` for that grid and says so, and a failed planted control still produces
`NOT A RESULT`.  What `PENDING` covers is the one conjunct nobody has built yet.

PLANTED CONTROLS FIRST, ALWAYS (standing rule 3, registration section 7).  Every
control runs BEFORE any measurement is allowed to count, and a control that does not
fire makes the whole run `NOT A RESULT` at exit 2.  A zero from a reader not shown
able to see a non-zero is not evidence.

RULE 4, STRICT AND ALL-OR-NOTHING.  Registration section 6.  This comparator REFUSES
(exit 2) rather than degrading on any failed completion clause.  An absent
`log.checkMesh` reads `ABSENT`; IT NEVER READS CLEAN.

NO `assert` ANYWHERE (L-332).

USAGE
    python3 analyse_rung0.py --run-root <dir>
    python3 analyse_rung0.py --controls-only        # controls, zero compute, no grids
Exit 0 = graded (whatever the verdict); 2 = REFUSED / NOT A RESULT.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "cases" / "committee-grids"))
import read_ugrid_identity as R  # noqa: E402

EXIT_REFUSE = 2

FREEZE_SHA = "d127d83d4ebf4caaaf0c12c39a063c5f624a03a4"
PREREG = "verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md"

DPW5 = Path("/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid")
HLPW6 = Path("/home/ubuntu/certonomous-runs/hlpw6-memory-probe/grid")

# The four grids of section 3. THE POPULATION IS FIXED HERE, NOT DISCOVERED BY GLOB:
# a comparator that grades whatever it happens to find can be made to pass by deleting
# the grid that fails.
GRIDS = (
    ("DPW5_L1T_hex", DPW5 / "L1.T.rev01.p3d.hex.r8.ugrid", DPW5 / "dpw5_L1T.mapbc"),
    ("DPW5_L1T_prism", DPW5 / "L1.T.rev01.p3d.prism.r8.ugrid", DPW5 / "dpw5_L1T.mapbc"),
    ("DPW5_L1T_hybrid", DPW5 / "L1.T.rev01.p3d.hybrid.r8.ugrid", DPW5 / "dpw5_L1T.mapbc"),
    ("HLPW6_h6c1_rans_3a_1", HLPW6 / "h6c1_rans_3a_1.b8.ugrid",
     HLPW6 / "h6c1_rans_3a_1.mapbc"),
)

# Two real logs on this box, one per checkMesh label form. Section 7's fifth control.
LOG_COLON = REPO / "cases/committee-grids/logs/DPW5_hex_checkMesh.log"
LOG_EQ = REPO / "verification/runs/F24_PRANDTL_MEYER_runs/coarse/log.checkMesh"

# Every field section 4's R0-G3 requires on the birth certificate, NON-NULL.
G3_FIELDS = (
    "cells", "faces", "max_non_orthogonality", "severe_non_ortho_faces",
    "max_skewness", "max_aspect_ratio", "aspect_ratio_flagged", "min_cell_volume",
    "max_cell_volume", "cell_volume_ratio", "geometric_directions", "checkMesh_log",
    "points_sha256", "generator", "created_at", "grid_provenance",
)


# ====================================================================== the controls
def _write_ugrid(path, counts, tri_tags, quad_tags, endian=">", fortran=True):
    """A minimal but STRUCTURALLY EXACT UGRID file, built byte by byte.

    Used by the synthetic controls so the reader's answer can be checked against a
    number that is KNOWN A PRIORI rather than against another reader's opinion.
    """
    nN, nT, nQ, nTet, nPyr, nPri, nHex = counts
    body = b"".join([
        struct.pack(endian + f"{nN * 3}d", *([0.0] * (nN * 3))),
        struct.pack(endian + f"{nT * 3}i", *([1] * (nT * 3))),
        struct.pack(endian + f"{nQ * 4}i", *([1] * (nQ * 4))),
        struct.pack(endian + f"{nT}i", *tri_tags),
        struct.pack(endian + f"{nQ}i", *quad_tags),
        struct.pack(endian + f"{nTet * 4}i", *([1] * (nTet * 4))),
        struct.pack(endian + f"{nPyr * 5}i", *([1] * (nPyr * 5))),
        struct.pack(endian + f"{nPri * 6}i", *([1] * (nPri * 6))),
        struct.pack(endian + f"{nHex * 8}i", *([1] * (nHex * 8))),
    ])
    hdr = struct.pack(endian + "7i", *counts)
    with open(path, "wb") as f:
        if fortran:
            f.write(struct.pack(endian + "i", 28) + hdr
                    + struct.pack(endian + "i", 28))
            f.write(struct.pack(endian + "i", len(body)) + body
                    + struct.pack(endian + "i", len(body)))
        else:
            f.write(hdr + body)


def run_controls(scratch: Path) -> list[dict]:
    """Section 7's planted controls. Each returns fired True/False and what it saw."""
    out = []
    scratch.mkdir(parents=True, exist_ok=True)

    # ---- C0. THE ABSOLUTE CONTROL, and it comes first on purpose. -----------------
    # Every other control below is a DIFFERENTIAL: it plants a change and asks whether
    # the reader moved. A reader that returned a constant WRONG answer and moved
    # correctly around it would pass all of them. C0 checks the reader against counts
    # that are known a priori because this file wrote them.
    for lay, fort in (("r8 Fortran, big-endian", True), ("b8 raw stream, big", False)):
        g = scratch / f"c0_{int(fort)}.ugrid"
        mb = scratch / "c0.mapbc"
        # 4 nodes; 3 boundary tris tagged 1,1,2; 2 boundary quads tagged 2,3;
        # 5 tets, 0 pyr, 2 prisms, 3 hexes  => cells 10, boundary faces 5.
        _write_ugrid(g, (4, 3, 2, 5, 0, 2, 3), (1, 1, 2), (2, 3), fortran=fort)
        mb.write_text("3\n1 4000 alpha\n2 5050 beta\n3 6662 gamma\n")
        try:
            s = R.read_source_identity(g, mb)
            ok = (s["cells"] == 10 and s["boundary_faces"] == 5
                  and s["patches"] == {"alpha": 2, "beta": 2, "gamma": 1}
                  and s["fortran"] is fort)
            saw = f"cells {s['cells']}, bnd {s['boundary_faces']}, {s['patches']}"
        except R.Refusal as exc:
            ok, saw = False, f"REFUSED: {exc}"
        out.append(dict(control=f"C0 absolute, {lay}", fired=ok,
                        expected="cells 10, bnd 5, {alpha:2, beta:2, gamma:1}", saw=saw))

    # ---- C1. section 7 row 1: rename one .mapbc group in a SCRATCH COPY. ----------
    src, mapbc = GRIDS[0][1], GRIDS[0][2]
    base = None
    if src.is_file() and mapbc.is_file():
        base = R.read_source_identity(src, mapbc)
        mb2 = scratch / "c1_renamed.mapbc"
        txt = mapbc.read_text().splitlines()
        renamed = False
        for i, ln in enumerate(txt):
            p = ln.split()
            if len(p) >= 3 and p[2] == "wall":
                txt[i] = f"{p[0]} {p[1]} PLANTED_WALL_RENAME"
                renamed = True
                break
        mb2.write_text("\n".join(txt) + "\n")
        got = R.read_source_identity(src, mb2)
        fired = renamed and "PLANTED_WALL_RENAME" in got["patches"]
        out.append(dict(
            control="C1 rename one .mapbc group (scratch copy)", fired=fired,
            expected="the renamed patch appears in the emitted name set",
            saw=f"names {sorted(got['patches'])}"))

        # ---- C2. section 7 row 2: delete ONE boundary face from a scratch copy. ---
        # Implemented on the real DPW5 hex grid, rewritten byte-exactly with nT-1:
        # the header count, the dropped 12 bytes of tri connectivity, the dropped
        # 4-byte tag and BOTH Fortran record markers are all recomputed.
        g2 = scratch / "c2_minus_one_face.ugrid"
        kind = _delete_one_boundary_face(src, g2)
        got2 = R.read_source_identity(g2, mapbc)
        drop = {k: base["patches"][k] - got2["patches"].get(k, 0)
                for k in base["patches"]}
        fired2 = (sum(drop.values()) == 1
                  and got2["boundary_faces"] == base["boundary_faces"] - 1
                  and got2["cells"] == base["cells"])
        out.append(dict(
            control=f"C2 delete one boundary {kind} (scratch copy of the real grid)",
            fired=fired2,
            expected="exactly one patch's face count drops by exactly 1; cells unchanged",
            saw=f"per-patch drop {drop}, bnd {base['boundary_faces']} -> "
                f"{got2['boundary_faces']}, cells {base['cells']} -> {got2['cells']}"))
    else:
        out.append(dict(control="C1/C2", fired=False,
                        expected="source grid readable",
                        saw=f"BLOCKED: {src} or {mapbc} unreachable"))

    # ---- C3/C4. polyMesh reader: +1 on one nFaces, and a renamed patch. -----------
    # Planted into a SCRATCH COPY of a real polyMesh boundary file, so the reader is
    # exercised on production bytes rather than on a fixture it agrees with.
    donor = REPO / "verification/runs/M6I_runs/L2"
    if (donor / "constant/polyMesh/boundary").is_file():
        for tag, mutate, expect in (
            ("C3 +1 on one nFaces", lambda t: t.replace("nFaces          6912;",
                                                        "nFaces          6913;", 1),
             "R0-G2a reports UNEQUAL, not equal"),
            ("C4 rename one patch", lambda t: t.replace("    defaultFaces\n",
                                                        "    PLANTED_PATCH\n", 1),
             "R0-G2a reports a NAME-SET MISMATCH"),
        ):
            case = scratch / tag.split()[0]
            (case / "constant/polyMesh").mkdir(parents=True, exist_ok=True)
            # `neighbour` is copied too: the reader derives nInternalFaces from it
            # and REFUSES when it is absent, so a plant that omitted it would be
            # refused for the WRONG reason and would prove nothing about C3 or C4.
            for f in ("owner", "neighbour"):
                shutil.copy(donor / "constant/polyMesh" / f,
                            case / "constant/polyMesh" / f)
            b = (donor / "constant/polyMesh/boundary").read_text()
            (case / "constant/polyMesh/boundary").write_text(mutate(b))
            clean = R.read_polymesh_identity(donor)
            dirty = R.read_polymesh_identity(case)
            if tag.startswith("C3"):
                fired = (dirty["patches"] != clean["patches"]
                         and sum(dirty["patches"].values())
                         == sum(clean["patches"].values()) + 1)
                saw = f"{clean['patches']} -> {dirty['patches']}"
            else:
                fired = set(dirty["patches"]) != set(clean["patches"])
                saw = f"{sorted(clean['patches'])} -> {sorted(dirty['patches'])}"
            out.append(dict(control=tag, fired=fired, expected=expect, saw=saw))
    else:
        out.append(dict(control="C3/C4", fired=False, expected="donor polyMesh",
                        saw=f"BLOCKED: {donor} unreachable"))

    # ---- C5. section 7 row 5: BOTH checkMesh aspect-ratio label forms. ------------
    got_eq = R.read_checkmesh_quality(LOG_EQ)
    got_co = R.read_checkmesh_quality(LOG_COLON)
    out.append(dict(
        control="C5 both aspect-ratio label forms yield a NON-NULL value",
        fired=(got_eq.get("max_aspect_ratio") is not None
               and got_co.get("max_aspect_ratio") is not None
               and got_eq.get("aspect_ratio_label_form") == "="
               and got_co.get("aspect_ratio_label_form") == ":"),
        expected="'=' form and ':' form both non-null; a reader matching only '=' "
                 "silently misses exactly the pathological logs",
        saw=f"'=' {got_eq.get('max_aspect_ratio')} / ':' {got_co.get('max_aspect_ratio')}"))

    # ---- C6. section 7 row 6: Min != Max volume gives a NON-TRIVIAL ratio. --------
    out.append(dict(
        control="C6 Min volume != Max volume -> a non-trivial derived ratio, never 1",
        fired=(got_co.get("cell_volume_ratio") is not None
               and got_co["cell_volume_ratio"] > 1.0
               and got_co.get("min_cell_volume") != got_co.get("max_cell_volume")),
        expected="ratio > 1 and derived, never 1 and never null",
        saw=f"min {got_co.get('min_cell_volume')} max {got_co.get('max_cell_volume')} "
            f"ratio {got_co.get('cell_volume_ratio')}"))

    # ---- C7. THE VERDICT-LINE TRAP. Not in section 7's table; added because the ---
    # supervisor's brief names it as measured on this box and because it is the one
    # way this rung's quality numbers could be silently wrong.
    out.append(dict(
        control="C7 the verdict line is DISCARDED, the number is PARSED",
        fired=("Non-orthogonality check OK." in
               got_co.get("verdict_line_IGNORED_NEVER_A_GATE", [])
               and got_co.get("max_non_orthogonality", 0) > 70.0),
        expected="the same log that prints `Non-orthogonality check OK.` yields a "
                 "parsed maximum ABOVE 70 degrees",
        saw=f"verdict lines {got_co.get('verdict_line_IGNORED_NEVER_A_GATE')} at "
            f"{got_co.get('max_non_orthogonality')} deg"))

    # ---- C8. an ABSENT log reads ABSENT and NEVER clean. --------------------------
    miss = R.read_checkmesh_quality(scratch / "no_such_log")
    out.append(dict(
        control="C8 an absent log reads ABSENT, never clean",
        fired=(miss.get("state") == "ABSENT"
               and miss.get("max_non_orthogonality") is None),
        expected="state ABSENT and no number",
        saw=f"state {miss.get('state')}"))

    # ---- C10. THE HEADER-VERSUS-DERIVED CROSS-CHECK MUST REFUSE, NOT PREFER. -------
    # Added after that cross-check earned its keep twice in one session: it caught the
    # reader deriving nCells as max(owner)+1, which is only a LOWER BOUND and came out
    # two cells short on HLPW6 while agreeing exactly on all three DPW5 grids. A guard
    # never seen to fire is not known to be load-bearing (L-314), so it is planted here.
    #
    # ⚠ IT IS RUN ON EVERY DONOR AVAILABLE, NOT THE FIRST ONE FOUND, AND THAT IS THE
    # POINT. The defect this control guards was a LABEL-FORM defect: the counts are
    # written as a QUOTED FoamFile key by OpenFOAM's own mesh writer and as a
    # `// note:` COMMENT by ugrid_to_foam.py, and a reader that knew only the quoted
    # form called every mesh this rung imports "no note". A control planted into only
    # ONE of the two forms would certify a reader that still could not see the other.
    # So the donor list deliberately spans both writers wherever both are on disk.
    R0 = REPO / "verification/runs/RUNG0_MESH_IMPORT_runs"
    donors = []
    for name, _u, _m in GRIDS:
        for base in (R0, R0 / "ATTEMPT2_PRESERVED"):
            if (base / name / "constant/polyMesh/owner").is_file():
                donors.append(base / name)
    if (REPO / "verification/runs/M6I_runs/L2/constant/polyMesh/owner").is_file():
        donors.append(REPO / "verification/runs/M6I_runs/L2")
    if not donors:
        out.append(dict(
            control="C10 header-vs-derived count cross-check", fired=None,
            expected="a header note contradicting the mesh's own lists REFUSES",
            saw="NOT RUN -- no polyMesh is on disk to plant into. Reported, never "
                "silently skipped."))
    seen_forms = set()
    for di, donor2 in enumerate(donors):
        case = scratch / f"C10_{di}"
        (case / "constant/polyMesh").mkdir(parents=True, exist_ok=True)
        for f in ("boundary", "neighbour"):
            shutil.copy(donor2 / "constant/polyMesh" / f,
                        case / "constant/polyMesh" / f)
        own = (donor2 / "constant/polyMesh/owner").read_text(errors="replace")
        head, sep, rest = own.partition("\n(")
        clean = R.read_polymesh_identity(donor2)
        bad_head = head.replace(f"nCells:{clean['cells']}",
                                f"nCells:{clean['cells'] + 1}", 1)
        planted = (bad_head != head)
        (case / "constant/polyMesh/owner").write_text(bad_head + sep + rest)
        try:
            R.read_polymesh_identity(case)
            fired, saw = False, "the reader ACCEPTED a header contradicting the mesh"
        except R.Refusal as exc:
            fired = planted and "CONTRADICTS" in str(exc)
            saw = str(exc)[:180]
        form = clean.get("header_note_form") or "no header note"
        if form in seen_forms:
            continue          # both label forms already exercised; do not spam the log
        seen_forms.add(form)
        out.append(dict(
            control=f"C10 a header note contradicting the mesh's own lists REFUSES "
                    f"[{form} form, {donor2.name}]",
            fired=fired,
            expected=f"nCells {clean['cells']} -> {clean['cells'] + 1} in the header "
                     f"alone must REFUSE, never be preferred over the lists",
            saw=saw))

    # ---- C9. section 7 row 7: the foam_to_ugrid round trip. NOT RUN. --------------
    writer = REPO / "cases/committee-grids/foam_to_ugrid.py"
    out.append(dict(
        control="C9 foam_to_ugrid round trip (section 7 row 7)",
        fired=None,
        expected="drop one face from the written file -> R0-G2b reports unequal",
        saw=f"NOT RUN -- {writer} DOES NOT EXIST (frozen registration section 9 says "
            f"so). This control is neither passed nor failed; it is UNBUILT, and "
            f"R0-G2b is consequently PENDING, never PASS."))
    return out


def _delete_one_boundary_face(src: Path, dst: Path):
    """Copy `src` to `dst` with exactly ONE boundary face removed.

    Rewrites the header count, drops that face's connectivity bytes and its 4-byte
    tag, and recomputes both Fortran record markers. The point is that the reader must
    SEE the deletion -- if the file were merely copied, C2 would report a zero
    difference and that zero would be worthless (rule 3).

    ⚠ IT DELETES A TRIANGLE ONLY IF ONE EXISTS, AND THE FIRST DRAFT ASSUMED ONE DID.
    DPW5 L1.T **hex** has nTri = 0: every one of its 41,984 boundary faces is a QUAD,
    because a hexahedral cell has no triangular face. The tri-only version produced a
    file of IDENTICAL SIZE to the source -- it deleted nothing -- and the plant would
    have reported "no change" while looking like it had run. THE LAYOUT SNIFFER CAUGHT
    IT (the size no longer matched any layout) and the self-check below now catches it
    directly. This is the exact failure standing rule 3 exists to prevent: a control
    that quietly does nothing certifies a reader that can see nothing.
    """
    endian, fortran, c, _ = R.sniff_layout(src)
    nN, nT, nQ, nTet, nPyr, nPri, nHex = c
    if nT > 0:
        kind, conn = "tri", R._TRI
    elif nQ > 0:
        kind, conn = "quad", R._QUAD
    else:
        raise R.Refusal(f"PLANT: {src} has no boundary faces at all to delete.")

    raw = src.read_bytes()
    start = (4 + 28 + 8) if fortran else 28
    off_tri = start + nN * R._NODE
    off_quad = off_tri + nT * R._TRI
    off_ttag = off_quad + nQ * R._QUAD
    off_qtag = off_ttag + nT * R._TAG
    rest = off_qtag + nQ * R._TAG
    tail = raw[rest:len(raw) - (4 if fortran else 0)]      # volume elements

    if kind == "tri":
        body = b"".join([
            raw[start:off_tri],                    # nodes
            raw[off_tri + conn:off_quad],          # tris, MINUS THE FIRST
            raw[off_quad:off_ttag],                # quads
            raw[off_ttag + R._TAG:off_qtag],       # tri tags, MINUS THE FIRST
            raw[off_qtag:rest], tail])
        hdr = struct.pack(endian + "7i", nN, nT - 1, nQ, nTet, nPyr, nPri, nHex)
    else:
        body = b"".join([
            raw[start:off_tri],                    # nodes
            raw[off_tri:off_quad],                 # tris
            raw[off_quad + conn:off_ttag],         # quads, MINUS THE FIRST
            raw[off_ttag:off_qtag],                # tri tags
            raw[off_qtag + R._TAG:rest], tail])    # quad tags, MINUS THE FIRST
        hdr = struct.pack(endian + "7i", nN, nT, nQ - 1, nTet, nPyr, nPri, nHex)

    with open(dst, "wb") as f:
        if fortran:
            f.write(struct.pack(endian + "i", 28) + hdr
                    + struct.pack(endian + "i", 28))
            f.write(struct.pack(endian + "i", len(body)) + body
                    + struct.pack(endian + "i", len(body)))
        else:
            f.write(hdr + body)

    # THE PLANT CHECKS ITSELF BEFORE THE READER IS ASKED ANYTHING.
    want = src.stat().st_size - (conn + R._TAG)
    got = dst.stat().st_size
    if got != want:
        raise R.Refusal(
            f"PLANT: deleting one boundary {kind} from {src.name} should shrink the "
            f"file by exactly {conn + R._TAG} bytes to {want}; it is {got}. The plant "
            f"itself is wrong, so nothing may be concluded from what the reader says "
            f"about it.")
    return kind


# ======================================================================= the gates
def grade_grid(name, ugrid, mapbc, case: Path, root_epoch: float) -> dict:
    """R0-G1, R0-G2a, R0-G3 and R0-G4 for ONE grid. R0-G2b is NOT RUN."""
    g = dict(grid=name, source=str(ugrid), case=str(case))

    try:
        src = R.read_source_identity(ugrid, mapbc)
    except R.Refusal as exc:
        return dict(g, verdict="BLOCKED", why=f"source unreadable: {exc}")
    try:
        foam = R.read_polymesh_identity(case)
    except R.Refusal as exc:
        return dict(g, verdict="GATE FAIL", why=f"imported polyMesh unreadable: {exc}")

    log = case / "log.checkMesh"
    q = R.read_checkmesh_quality(log)
    g["source_reading"] = src
    g["polymesh_reading"] = foam
    g["quality_reading"] = q

    # ---- R0-G1 --------------------------------------------------------------------
    g1 = {
        "n_patches_equals_distinct_mapbc_names":
            foam["n_patches"] == src["distinct_mapbc_names"],
        "patch_names_set_equal": set(foam["patches"]) == set(src["patches"]),
        "defaultFaces_absent": not foam["default_faces_present"],
        "boundary_face_sum_equals_source":
            sum(foam["patches"].values()) == src["boundary_faces"],
    }
    g["R0_G1"] = dict(checks=g1, verdict="PASS" if all(g1.values()) else "GATE FAIL")

    # ---- R0-G2a. INTEGERS. No tolerance -- a tolerance on an integer identity is an
    # invitation (section 4).
    mism = {k: (src["patches"].get(k), foam["patches"].get(k))
            for k in set(src["patches"]) | set(foam["patches"])
            if src["patches"].get(k) != foam["patches"].get(k)}
    g2a = {
        "cell_count_exact": src["cells"] == foam["cells"],
        "patch_names_set_equal": set(foam["patches"]) == set(src["patches"]),
        "per_patch_face_counts_exact": not mism,
    }
    g["R0_G2a"] = dict(checks=g2a, per_patch_mismatches=mism,
                       source_cells=src["cells"], imported_cells=foam["cells"],
                       verdict="PASS" if all(g2a.values()) else "GATE FAIL")

    # ---- R0-G2b -------------------------------------------------------------------
    g["R0_G2b"] = dict(
        verdict="PENDING",
        why="cases/committee-grids/foam_to_ugrid.py DOES NOT EXIST. The frozen "
            "registration section 9 registers it as to-be-written. NOT RUN is not a "
            "pass and not a failure; it is the reason the rung's conjunction cannot "
            "be evaluated.")

    # ---- R0-G3. REPORTED, NOT GATED. It fails ONLY on a MISSING number. ------------
    cert = dict(q)
    cert.update(
        points_sha256=_points_sha256(case),
        generator="cases/committee-grids/ugrid_to_foam.py",
        created_at=_iso(case),
        grid_provenance="workshop committee family, quality as published",
        published_quality_comparison=(
            "no published quality figure located -- searched the grid's own "
            "distribution directory on this box (readme / g.html / l2.xml beside the "
            "grid) and no max non-orthogonality, skewness or aspect-ratio figure is "
            "published there. Section 4 gates this comparison on being MADE, not on "
            "agreeing, and this is the made comparison's honest outcome. NEVER "
            "silence, NEVER a blank."),
        non_orthogonality_gate_deg=70,
        quality_reporting_mode="REPORTED, NOT GATED (Sanaa's two-tier ruling, "
                               "condition (a); MESH_STANDARD section 11.4)",
    )
    missing = [f for f in G3_FIELDS if cert.get(f) is None]
    g["R0_G3"] = dict(missing_fields=missing,
                      verdict="PASS" if not missing else "GATE FAIL")
    g["birth_certificate"] = cert

    # ---- R0-G4. THE AGE GUARD. Every graded artifact NEWER than the run root stamp.
    stale = []
    for p in (case / "constant/polyMesh/owner", case / "constant/polyMesh/boundary",
              case / "constant/polyMesh/faces", case / "constant/polyMesh/points",
              log):
        if not p.is_file():
            stale.append(f"{p.name}: ABSENT")
        elif p.stat().st_mtime <= root_epoch:
            stale.append(f"{p.name}: mtime {p.stat().st_mtime} <= root stamp {root_epoch}")
    g["R0_G4"] = dict(root_epoch=root_epoch, stale_or_absent=stale,
                      verdict="PASS" if not stale else "GATE FAIL")

    per = [g["R0_G1"]["verdict"], g["R0_G2a"]["verdict"], g["R0_G3"]["verdict"],
           g["R0_G4"]["verdict"]]
    if "GATE FAIL" in per:
        g["verdict"] = "GATE FAIL"
    else:
        # RUNNABLE GATES ALL HELD. That is NOT the rung's PASS -- R0-G2b is unbuilt.
        g["verdict"] = "PENDING"
        g["verdict_why"] = (
            "R0-G1, R0-G2a, R0-G3 and R0-G4 all hold on this grid. The grid's own "
            "label is still PENDING because section 4 defines PASS as the conjunction "
            "INCLUDING R0-G2b, which cannot run. Reporting PASS here would be "
            "reporting a conjunction one of whose conjuncts was never evaluated.")
    return g


def _points_sha256(case: Path):
    import hashlib
    p = case / "constant/polyMesh/points"
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _iso(case: Path):
    import datetime
    p = case / "constant/polyMesh/owner"
    if not p.is_file():
        return None
    return datetime.datetime.fromtimestamp(
        p.stat().st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================================ main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-root", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--controls-only", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.run_root)

    scratch = Path(tempfile.mkdtemp(prefix="rung0_controls_"))
    try:
        controls = run_controls(scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    failed = [c for c in controls if c["fired"] is False]
    print("=== PLANTED CONTROLS (standing rule 3, registration section 7) ===")
    for c in controls:
        mark = {True: "FIRED", False: "DID NOT FIRE", None: "NOT RUN"}[c["fired"]]
        print(f"  [{mark:>12}] {c['control']}")
        print(f"                 expected: {c['expected']}")
        print(f"                 saw     : {c['saw']}")
    if failed:
        print(f"\nNOT A RESULT: {len(failed)} planted control(s) did not fire. Every "
              f"number this comparator could print is worthless until they do "
              f"(standing rule 3). REFUSED at exit 2; nothing was graded.")
        return EXIT_REFUSE

    if a.controls_only:
        print("\ncontrols-only: no grid was graded, no verdict is claimed.")
        return 0

    stamp = root / "RUN_ROOT_CREATED_EPOCH"
    if not stamp.is_file():
        print(f"REFUSED: {stamp} is absent, so R0-G4's age guard has no datum. "
              f"Rule 4: refuse, never degrade.")
        return EXIT_REFUSE
    root_epoch = float(stamp.read_text().split()[0])

    results, per_grid = [], {}
    for name, ug, mb in GRIDS:
        case = root / name
        if not case.is_dir():
            results.append(dict(grid=name, verdict="BLOCKED",
                                why=f"case directory {case} absent -- not converted"))
        else:
            results.append(grade_grid(name, ug, mb, case, root_epoch))
        per_grid[name] = results[-1]["verdict"]
        cert = results[-1].get("birth_certificate")
        if cert is not None:
            (case / "birth_certificate.json").write_text(
                json.dumps(cert, indent=2, sort_keys=True, default=str))

    print("\n=== PER-GRID READING ===")
    for r in results:
        print(f"  {r['grid']:24s} {r['verdict']}")
        for k in ("R0_G1", "R0_G2a", "R0_G2b", "R0_G3", "R0_G4"):
            if k in r:
                print(f"      {k:7s} {r[k]['verdict']}")
        q = r.get("quality_reading") or {}
        if q.get("max_non_orthogonality") is not None:
            print(f"      quality REPORTED NOT GATED: max non-orth "
                  f"{q['max_non_orthogonality']} deg (70 deg generation gate), "
                  f"severe {q['severe_non_ortho_faces']}, skew {q['max_skewness']}, "
                  f"AR {q['max_aspect_ratio']} ({q['aspect_ratio_label_form']} form), "
                  f"cell-volume ratio {q['cell_volume_ratio']:.4g} DERIVED")

    verdicts = set(per_grid.values())
    if "GATE FAIL" in verdicts:
        rung = "GATE FAIL"
    elif "BLOCKED" in verdicts:
        rung = "BLOCKED"
    else:
        rung = "PENDING"
    print(f"\n=== RUNG 0 VERDICT: {rung} ===")
    print("The rung's verdict is the CONJUNCTION of section 4's labels over all four "
          "grids. R0-G2b cannot run -- cases/committee-grids/foam_to_ugrid.py does "
          "not exist -- so NO `PASS` IS REACHABLE UNDER THIS REGISTRATION UNTIL THAT "
          "WRITER IS BUILT AND RUN. Nothing above licenses a fidelity claim, a "
          "capability-grid row, or any admissibility statement about any grid.")

    out = dict(case_id="RUNG0_MESH_IMPORT", prereg=PREREG, prereg_commit=FREEZE_SHA,
               rung_verdict=rung, per_grid=per_grid, controls=controls,
               results=results, root_epoch=root_epoch)
    (root / "RESULTS.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                  default=str))
    print(f"\nwritten: {root / 'RESULTS.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
