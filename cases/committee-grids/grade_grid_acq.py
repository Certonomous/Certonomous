#!/usr/bin/env python3
"""Comparator for RUNG 2 grid-family acquisition -- DPW5 refinement triple L1.T / L2.C / L3.M (hex).

Registered by `verification/campaign/RUNG2_CRM_GRID_ACQUISITION_PREREGISTRATION.md` (v1.1, check 4
GO 2026-09-07). The grading path is fixed at that document's commit; this file is hashed against its
committed blob at grading time and the run refuses on mismatch (scripts/check_comparator_freeze.py).

THIS FILE FETCHES NOTHING AND LAUNCHES NOTHING. It admits fetched grids (title page, L-144) and
screens them against this lab's hard mesh gates. It does two things and no more:

  * §4.A TITLE PAGE (L-144). A fetched grid is admitted on the contents of its own header, NEVER on
    its filename, byte-size-alone or a hash. Byte length must equal the upstream Content-Length
    measured in the registration's §2; the ugrid r8 header node/cell counts must equal the
    2026-08-01 size survey EXACTLY; the node/cell ratio must sit in the family band. Any mismatch
    REFUSES -- a sharpened lookalike at an adjacent URL is exactly what burned this lab twice
    (L-144; ONERA M6 om6_wing_section_sharp).
  * §4.B MESH-GATE SCREEN. `checkMesh` max non-orthogonality vs 70 deg (MESH_STANDARD.md:56) and max
    skewness vs 4 (MESH_STANDARD.md:84), read NUMERICALLY off the named maxima -- the verdict line is
    discarded (on this box "Non-orthogonality check OK." prints at 89.71 deg). An ABSENT checkMesh
    log reads ABSENT; IT NEVER READS CLEAN. This screen is DIAGNOSTIC, not a credential gate: it
    answers the ruling's cheap question (would the further levels clear the gates), and its pass/fail
    is the reported finding, not a widening of any gate.

Design constraints, each from a rule/lesson and each carried by an executable control:
  * rule 3  -- planted controls. Every reader is shown able to see a WRONG value and REFUSE/FLAG it
               before it is allowed to report a right one. `--selftest` is that demonstration; it uses
               two REAL archived checkMesh logs on this box plus synthetic ugrid headers.
  * rule 5 direction -- an ABSENT/missing metric is NOT A RESULT, never a silent clear.
  * "a zero needs a live planted control" -- the header reader is shown a planted wrong node count
               and REFUSES; the metric reader is shown a planted over-gate value and FLAGS it.
  * ZERO `assert` statements -- `python3 -O` strips them; guards built on one vanish in production.
               `count_assert_nodes()` proves the absence by AST, the detector itself planted first.
  * no bytecode is written by the selftest path ("stale pycache inverts mutation tests").

Reused readers, committed and UNMODIFIED (a control on a different function is not a control):
  read_ugrid_identity.sniff_layout        -- the self-validating (byte-budget) header read
  read_ugrid_identity.read_checkmesh_quality -- the numeric checkMesh reader (verdict lines discarded)

--selftest result 2026-09-07: 10/10 controls fired in the refusing/flagging direction.

Exit codes:
    0  admitted/screened, or selftest passed
    2  REFUSED -- a control did not fire, or an input is inconsistent. Never an admission.
"""

import ast
import json
import os
import struct
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_ugrid_identity as R      # noqa: E402  committed, unmodified

EXIT_REFUSE = 2

# ---------------------------------------------------------------------------
# Registered constants. The population is FIXED HERE, not discovered by glob: a
# comparator that admits whatever it happens to find can be made to pass by
# swapping in the grid that fits. Changing any value changes the grade and is a
# freeze violation unless it lands as a dated amendment to the pre-registration.
# Sources: upstream Content-Length measured by HEAD 2026-09-07 (registration §2);
# node/cell counts from cases/committee-grids/logs/DPW5_size_survey.log (2026-08-01).
# ---------------------------------------------------------------------------

LEVELS = {
    "L1.T": dict(fname="L1.T.rev01.p3d.hex.r8.ugrid", content_length=37131204,
                 nodes=660177,  cells=638976,  hex=638976,  tet=0, pyr=0, prism=0, on_box=True),
    "L2.C": dict(fname="L2.C.rev01.p3d.hex.r8.ugrid", content_length=123796868,
                 nodes=2204089, cells=2156544, hex=2156544, tet=0, pyr=0, prism=0, on_box=False),
    "L3.M": dict(fname="L3.M.rev01.p3d.hex.r8.ugrid", content_length=291645252,
                 nodes=5196193, cells=5111808, hex=5111808, tet=0, pyr=0, prism=0, on_box=False),
}

# Family node/cell ratio band. Measured: L1.T 1.03318, L2.C 1.02204, L3.M 1.01651.
RATIO_BAND = (1.005, 1.050)

# MESH_STANDARD hard gates (diagnostic screen only -- these gates never widen).
NON_ORTHO_GATE = 70.0   # docs/standards/MESH_STANDARD.md:56
SKEW_GATE = 4.0         # docs/standards/MESH_STANDARD.md:84


class Refusal(Exception):
    """Raised instead of admitting a grid or a number the comparator cannot stand behind."""


def refuse(message):
    raise Refusal(message)


# --------------------------------------------------------------------------- §4.A title page


def read_ugrid_header(path):
    """The seven counts, via the committed self-validating sniffer. Refuses on ambiguity/short."""
    path = Path(path)
    if not path.is_file():
        refuse("ugrid file not on disk: %s -- a grid that is not present cannot be admitted" % path)
    # The committed sniffer raises its OWN Refusal type on an inconsistent/ambiguous layout; translate
    # it into this comparator's Refusal so every refusal exits 2 through the one handler below.
    try:
        endian, fortran, counts, off = R.sniff_layout(path)
    except R.Refusal as exc:
        refuse("LAYOUT (via read_ugrid_identity): %s" % exc)
    nN, nT, nQ, nTet, nPyr, nPri, nHex = counts
    return dict(nodes=nN, bnd_tri=nT, bnd_quad=nQ, tet=nTet, pyr=nPyr, prism=nPri, hex=nHex,
                cells=nTet + nPyr + nPri + nHex, file_size=path.stat().st_size,
                endian=endian, fortran=fortran)


def title_page_check(spec, path):
    """§4.A. Admit a fetched grid ONLY on its own header contents (L-144). Refuse on any mismatch."""
    size = os.path.getsize(path)
    # (1) completed-download / byte-length integrity: disk bytes == upstream Content-Length.
    if size != spec["content_length"]:
        refuse("BYTE LENGTH: %s is %d bytes, upstream Content-Length is %d. A short read or a "
               "different file -- REFUSED, never converted." % (path, size, spec["content_length"]))
    # (2) header identity (the TITLE PAGE): counts read from the grid's own header == the survey.
    h = read_ugrid_header(path)
    want = (spec["nodes"], spec["hex"], spec["tet"], spec["pyr"], spec["prism"], spec["cells"])
    got = (h["nodes"], h["hex"], h["tet"], h["pyr"], h["prism"], h["cells"])
    if got != want:
        refuse("HEADER IDENTITY: %s reads (nodes,hex,tet,pyr,prism,cells)=%s; registered %s. "
               "A lookalike or the wrong level -- REFUSED (L-144: never admit on filename/hash/type)."
               % (path, got, want))
    # (3) family node/cell ratio band -- a coarse guard against a mis-named level.
    ratio = h["nodes"] / h["cells"]
    if not (RATIO_BAND[0] <= ratio <= RATIO_BAND[1]):
        refuse("FAMILY RATIO: node/cell %.5f outside band %s for %s -- REFUSED." %
               (ratio, RATIO_BAND, path))
    return dict(title_page="VERIFIED", nodes=h["nodes"], cells=h["cells"], hex=h["hex"],
                file_size=size, node_cell_ratio=round(ratio, 5), endian=h["endian"],
                fortran=h["fortran"])


# --------------------------------------------------------------------------- §4.B mesh-gate screen


def mesh_gate_screen(level, checkmesh_log):
    """§4.B. checkMesh max non-orthogonality / max skewness vs the hard gates. Diagnostic."""
    q = R.read_checkmesh_quality(checkmesh_log)
    if q.get("state") == "ABSENT":
        refuse("checkMesh log ABSENT for %s -- an absent log NEVER reads clean (registration §4.B). "
               "NOT A RESULT for this level." % level)
    no = q.get("max_non_orthogonality")
    sk = q.get("max_skewness")
    if no is None or sk is None:
        refuse("checkMesh log present for %s but a hard-gate metric is missing "
               "(non_ortho=%r, skew=%r) -- REFUSE rather than degrade." % (level, no, sk))
    non_ortho_pass = no <= NON_ORTHO_GATE
    skew_pass = sk <= SKEW_GATE
    return dict(level=level, max_non_orthogonality=no, max_skewness=sk,
                non_ortho_gate=NON_ORTHO_GATE, skew_gate=SKEW_GATE,
                non_ortho_pass=non_ortho_pass, skew_pass=skew_pass,
                screen_clears_hard_gates=bool(non_ortho_pass and skew_pass),
                verdict_line_IGNORED=q.get("verdict_line_IGNORED_NEVER_A_GATE"))


# --------------------------------------------------------------------------- assert-freedom proof


def count_assert_nodes(source_text):
    tree = ast.parse(source_text)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))


def prove_assert_free(own_path):
    """Plant the detector, watch it fire, then read this file with it."""
    if count_assert_nodes("assert True\nx = 1\n") != 1:
        refuse("the assert-detector did not see a planted `assert`; it cannot report absence")
    if count_assert_nodes("x = 1\n") != 0:
        refuse("the assert-detector reported an assert in source that has none")
    with open(own_path, "r") as handle:
        own = count_assert_nodes(handle.read())
    if own != 0:
        refuse("this comparator contains %d `assert` statement(s); `python3 -O` strips them" % own)
    return True


# --------------------------------------------------------------------------- synthetic ugrid builder


def _write_raw_ugrid(path, nN, nHex, pad_extra=0):
    """A minimal little-endian raw-C-stream UGRID: 7-int header + zeroed payload.

    size = 28 + nN*24 + nHex*32 (+ pad_extra). pad_extra breaks the byte-budget identity on purpose.
    """
    header = struct.pack("<7i", nN, 0, 0, 0, 0, 0, nHex)
    payload = b"\x00" * (nN * 24 + nHex * 32 + pad_extra)
    Path(path).write_bytes(header + payload)


# --------------------------------------------------------------------------- real control artifacts


REPO = HERE.parents[1]
# L1.T hex checkMesh: max non-orth 89.7134, max skew 14.0594 -- BOTH over gate (real over-gate ctrl).
CTRL_OVERGATE_LOG = REPO / "cases/committee-grids/logs/DPW5_hex_checkMesh.log"
# F24 Prandtl-Meyer coarse: max non-orth 15.0, max skew 0.2679 -- BOTH under gate (real clean ctrl).
CTRL_UNDERGATE_LOG = REPO / "verification/runs/F24_PRANDTL_MEYER_runs/coarse/log.checkMesh"


def selftest():
    results = []

    # -- C0: the comparator proves its own guards survive `python3 -O`.
    prove_assert_free(os.path.abspath(__file__))
    results.append(("C0  assert-free proved, detector planted and seen", True, ""))

    with tempfile.TemporaryDirectory() as d:
        good = os.path.join(d, "good.ugrid")
        _write_raw_ugrid(good, nN=103, nHex=100)       # size 28+2472+3200 = 5700, ratio 1.03 (in band)
        spec = dict(content_length=5700, nodes=103, cells=100, hex=100, tet=0, pyr=0, prism=0)

        # -- C1 (POSITIVE title page): a correct synthetic grid + matching spec -> VERIFIED.
        c1 = title_page_check(spec, good)["title_page"] == "VERIFIED"
        results.append(("C1  correct grid (ratio 1.03) + matching spec -> title page VERIFIED",
                        c1, ""))

        # -- C2 (PLANTED WRONG NODE COUNT): spec expects 104 nodes; grid header reads 103 -> REFUSE.
        c2 = False
        try:
            title_page_check({**spec, "nodes": 104}, good)
        except Refusal:
            c2 = True
        results.append(("C2  planted wrong node count (expect 104, header 103) -> REFUSED", c2,
                        "reader read true 103, refused vs planted 104"))

        # -- C3 (PLANTED SHORT READ): spec Content-Length != actual byte count -> REFUSE.
        c3 = False
        try:
            title_page_check({**spec, "content_length": 999999}, good)
        except Refusal:
            c3 = True
        results.append(("C3  planted byte-length mismatch (999999 vs 5700) -> REFUSED", c3,
                        "byte-length guard fired"))

        # -- C4 (TAMPERED/INCONSISTENT HEADER): bytes padded so no layout reproduces size -> REFUSE.
        bad = os.path.join(d, "bad.ugrid")
        _write_raw_ugrid(bad, nN=103, nHex=100, pad_extra=7)  # size 5707, header still says 5700
        c4 = False
        try:
            read_ugrid_header(bad)
        except Refusal:
            c4 = True
        results.append(("C4  header bytes inconsistent with counts -> sniffer REFUSED", c4,
                        "byte-budget identity refused a tampered header"))

        # -- C5 (FAMILY RATIO): a grid whose header MATCHES its spec but ratio is out of band -> REFUSE.
        odd = os.path.join(d, "odd.ugrid")
        _write_raw_ugrid(odd, nN=200, nHex=100)               # size 8028, ratio 2.0 (out of band)
        odd_spec = dict(content_length=8028, nodes=200, cells=100, hex=100, tet=0, pyr=0, prism=0)
        c5 = False
        try:
            title_page_check(odd_spec, odd)
        except Refusal:
            c5 = True
        results.append(("C5  node/cell ratio 2.0 out of family band -> REFUSED", c5,
                        "header identity matched; ratio guard fired after"))

    # -- C6 (REAL OVER-GATE): the archived L1.T hex checkMesh log FLAGS both hard gates as FAILED.
    over = mesh_gate_screen("CTRL_L1T", CTRL_OVERGATE_LOG)
    c6 = (over["max_non_orthogonality"] == 89.7134 and over["max_skewness"] == 14.0594
          and over["non_ortho_pass"] is False and over["skew_pass"] is False
          and over["screen_clears_hard_gates"] is False)
    results.append(("C6  real L1.T log: 89.7134/14.0594 FLAGGED over gate, screen does NOT clear",
                    c6, "non_ortho_pass=%s skew_pass=%s" % (over["non_ortho_pass"], over["skew_pass"])))

    # -- C7 (REAL UNDER-GATE): the archived F24 log clears both gates. The reader FLIPS between two
    #    real artifacts, not merely fires on one.
    under = mesh_gate_screen("CTRL_F24", CTRL_UNDERGATE_LOG)
    c7 = (under["max_non_orthogonality"] <= NON_ORTHO_GATE and under["max_skewness"] <= SKEW_GATE
          and under["non_ortho_pass"] is True and under["skew_pass"] is True
          and under["screen_clears_hard_gates"] is True)
    results.append(("C7  real F24 log: 15.0/0.268 clears both gates (reader flips clean<->over)",
                    c7, "non_ortho=%.4f skew=%.4f" % (under["max_non_orthogonality"],
                                                      under["max_skewness"])))

    # -- C8 (PLANTED OVER-GATE): replace F24's non-orth with a planted over-gate value; screen must
    #    flip from clears to FAIL. Proves the clear is caused by the number, not incidental.
    with tempfile.TemporaryDirectory() as d:
        txt = CTRL_UNDERGATE_LOG.read_text(errors="replace")
        mutated = txt.replace("Mesh non-orthogonality Max: 15.0000000177",
                              "Mesh non-orthogonality Max: 89.9985")
        mp = os.path.join(d, "log.checkMesh")
        Path(mp).write_text(mutated)
        planted = mesh_gate_screen("MUT", mp)
        c8 = (planted["max_non_orthogonality"] == 89.9985 and planted["non_ortho_pass"] is False
              and planted["screen_clears_hard_gates"] is False)
    results.append(("C8  planted over-gate 89.9985 into a clean log -> screen flips to FAIL", c8,
                    "reader read the planted 89.9985 and flagged it"))

    # -- C9 (ABSENT LOG): a missing checkMesh log REFUSES; it never reads clean.
    c9 = False
    try:
        mesh_gate_screen("MISSING", HERE / "no_such_checkMesh.log")
    except Refusal:
        c9 = True
    results.append(("C9  ABSENT checkMesh log -> REFUSED (never reads clean)", c9, ""))

    for label, ok, note in results:
        print("%-4s %s%s" % ("PASS" if ok else "FAIL", label, ("   [%s]" % note) if note else ""))
    failed = [label for label, ok, _ in results if not ok]
    if failed:
        print("SELFTEST: NOT A RESULT -- %d control(s) did not fire." % len(failed))
        return EXIT_REFUSE
    print("SELFTEST: PASS -- %d/%d controls fired in the refusing/flagging direction." % (
        len(results), len(results)))
    return 0


# --------------------------------------------------------------------------- production --grade


def grade(level, ugrid_path, checkmesh_log, out_cert=None):
    """Admit (§4.A) and screen (§4.B) ONE fetched level. NOT reached before a fetch is authorised."""
    if level not in LEVELS:
        refuse("unknown level %r -- the population is fixed to %s" % (level, tuple(LEVELS)))
    spec = LEVELS[level]
    tp = title_page_check(spec, ugrid_path)
    screen = mesh_gate_screen(level, checkmesh_log)
    cert = dict(level=level, ugrid=str(Path(ugrid_path).resolve()),
                checkMesh_log=str(Path(checkmesh_log).resolve()),
                title_page=tp, mesh_gate_screen=screen,
                note=("G-A1 admits this grid; G-A2 has MEASURED its quality. "
                      "screen_clears_hard_gates is the reported FINDING, not a widening of any gate: "
                      "if False, the credential validated-force path stays BLOCKED "
                      "(RUNG2_CRM_M0 §15 ground (i))."))
    print("G-A1 title page: PASS -- %s admitted (nodes=%d cells=%d)." %
          (level, tp["nodes"], tp["cells"]))
    print("G-A2 mesh-gate screen: max non-orth %.4f (gate %g), max skew %.4f (gate %g) -> "
          "clears hard gates: %s" % (screen["max_non_orthogonality"], NON_ORTHO_GATE,
                                     screen["max_skewness"], SKEW_GATE,
                                     screen["screen_clears_hard_gates"]))
    if out_cert:
        Path(out_cert).write_text(json.dumps(cert, indent=2))
        print("birth certificate: %s" % out_cert)
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) >= 4 and argv[1] == "--grade":
        out = argv[5] if len(argv) >= 6 else None
        return grade(argv[2], argv[3], argv[4], out)
    print(__doc__)
    print("usage: grade_grid_acq.py --selftest | "
          "--grade <level> <ugrid> <checkMesh_log> [birth_cert.json]")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        sys.exit(EXIT_REFUSE)
