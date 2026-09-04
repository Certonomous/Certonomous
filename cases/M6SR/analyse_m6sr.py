#!/usr/bin/env python3
"""M6SR comparator -- the FROZEN grading path of verification/campaign/M6SR_PREREGISTRATION.md.

WHAT THIS FILE IS.  The registration's Section 9 registers this comparator at exactly
this path and its Section 9.1 RULES that it is "written and committed BEFORE the freeze,
so the freeze can pin their blob shas".  It grades Gate A (Section 5), Gate GF (Section 5),
Gate G (Section 5 + 5.1), Gate P (Section 5 + Section 4), the D1 discriminator (Section 4.3)
and the order-independent channel (Section 4.5), under the planted controls of Section 10 and
the execution mechanics of Section 9.2.

SECTIONS OF THE REGISTRATION IMPLEMENTED HERE, named so a reader can audit the mapping:
    Section 1.3   the condemned 390-face surface  -> A8
    Section 1.4   points-hash family identity     -> A5, controls C5/C6
    Section 2.2   the x4 family and cells/faces   -> A4, A6, A7
    Section 4.1   case_2308.dat pinned by sha256  -> Gate P refusal, control C11
    Section 4.3   the D1 discriminator            -> d1_discriminator(), controls C12/C13
    Section 4.5   order-independent channel       -> set_to_set_assignment()
    Section 5     Gates A / GF / G / P / R        -> gate_a(), gate_gf(), gate_g(), gate_p()
    Section 5.1   G2 plateau-and-stationarity     -> gate_g2(), controls C7/C8/C9
    Section 6     clause L-HONEST                 -> quoted VERBATIM on every output
    Section 7     ill-posedness screen            -> A9 / blocked_levels()
    Section 8.6   rule-4 strict completion        -> completion_clauses()
    Section 9.2   execution and assertion mechanics -> exit vocabulary, no bare assert
    Section 10    planted controls C1..C20        -> controls()
    Section 12    what is NOT claimed             -> printed with every verdict

EXIT VOCABULARY -- Section 9.2, and a CRASH IS NOT A REFUSAL:
    0   graded; the verdicts are in the output.  (A verdict may itself be GATE FAIL or
        NOT A RESULT -- rc 0 means the INSTRUMENT ran, never that the gate passed.)
    2   REFUSAL.  A control did not fire, a pinned hash moved, a completion clause failed,
        or a registered parameter this comparator needs is not registered.  The comparator
        REFUSES RATHER THAN DEGRADE (Section 8.6, Section 10).
    70  INTERNAL DEFECT of this comparator.  Never a finding about the M6.

NO BARE `assert` ANYWHERE (Section 9.2, L-475).  `python3 -O` deletes assert statements, so a
guard set that is assert-based is one interpreter flag from absent.  Every guard below is an
explicit `raise`.  Control C16 runs the suite under `-O` and requires identical refusals.

NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN.  Inputs there are read only.
"""

import gzip
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# --------------------------------------------------------------------------------------
# CLAUSE L-HONEST, Section 6.  Registered once, with an id, QUOTED BY REFERENCE AND NEVER
# PARAPHRASED.  Every figure, table, JSON record and certificate cell derived from this
# family carries it VERBATIM.
# --------------------------------------------------------------------------------------
L_HONEST = (
    "This is a SURFACE-REFINEMENT SENSITIVITY STUDY. Its GCI is a SURFACE-REFINEMENT BAND "
    "and a LOWER BOUND on total discretisation uncertainty. It is NOT an observed order of "
    "accuracy, and it is NOT the family band Sanaa named as her first deliverable."
)

# --------------------------------------------------------------------------------------
# PINNED CONSTANTS.  Every one is quoted from the frozen registration; none is chosen here.
# --------------------------------------------------------------------------------------
SHA_CASE_2308 = "020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0"   # Sec 4.1
SHA_TABLE_B1_1 = "66b2a7bcd5a0cab274396de1c5c55d0f5cad90911a1e19ddae4e77db16834ab7"  # Sec 5
SHA_SURFACE_MASTER = "197efa09d838b276a8967da9532d9c4d57edca18cb777bd640257606d2d83327"
SHA_SURFACE_6240 = "818e8307ae8299af7a04e10b8b4c7dc6fe299a8c280717502c1c8a6ff1caea2d"
SHA_SURFACE_1560 = "1e11aae4e0e5a4caaffeb63f98a2626734075fb486de8dca93e32f554d143921"
SHA_SURFACE_390_CONDEMNED = "aab44d4174d598bf8a9531def9607409099a3711832cac67f9d93538240b2326"  # Sec 1.3

PATH_TABLE_B1_1 = "models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat"
PATH_CASE_2308 = "cases/dafoam/ladder-a/logs_A3/case_2308.dat"

# Gate A thresholds, Section 5.
A1_MAX_NON_ORTHOGONALITY_DEG = 70.0
A2_MAX_SKEWNESS = 4.0
A3_ASPECT_RATIO_ADVISORY = 1000.0          # advisory 1000, NEVER a lone rejection
A4_CELLS = (99840, 399360, 1597440)        # L3, L2, L1
A4_RATIO_EXACT = 4                         # exactly 4.000 on integers
A6_CELLS_PER_WING_FACE = 64                # Section 2.2, identical at every level

# Gate GF thresholds, Section 5.
GF_AGARD_T_TE_OVER_C = 0.0014104
GF1_BAND_FRACTION = 0.10                   # +/- 10 % of 0.0014104
GF1_SHARP_BELOW = 1.0e-05
GF2_MAX_ABS_DZ_OVER_C = 1.0e-03
GF2_X_LO, GF2_X_HI = 0.001, 0.999
GF3_T_TE_IDENTICAL_TOL = 1.0e-06
GF4_SWEEP_DEG = 30.0000000
GF4_SWEEP_TOL_DEG = 0.01
GF4_SEMISPAN_M = 1.1963
GF4_SEMISPAN_TOL_FRAC = 0.001              # +/- 0.1 %

# Gate G, Section 5 and 5.1.
G1_TAIL_ITERATIONS = 500
G1_FRACTION_OF_L3_L2 = 0.10
G2A_ORDERS = 4.0
G2B_WINDOW_ITERATIONS = 1000
G2B_DRIFT_FRAC = 0.05
G2C_WINDOW_ITERATIONS = 2000
G2C_FRACTION_OF_L3_L2 = 0.10
G4_FS = 1.25                               # Roache safety factor, standing rule 5

# Gate P, Section 5 and Section 4.
P_X_OVER_C_GRADED_MAX = 0.90               # rear 10 % plotted and reported, NEVER graded
P_REFERENCE_ACCURACY_DCP = 0.02            # AR-138 B1-4 Section 6.1, published
A_MAP_YB = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99)   # Section 4, ASSUMED not measured
D1_MARGIN = 0.75                           # Section 4.3, registered threshold
D1_INDETERMINATE_HI = 1.0 / D1_MARGIN      # the (0.75, 1.333) band of Section 4.3

# Section 10 plant magnitudes.  Every one is read BACK FROM DISK after planting.
PLANT_TE_SPLIT_M = 2.000e-04               # C17
PLANT_DZ_OVER_C = 5.000e-04                # C18
PLANT_REFERENCE_TE = 3.21e-04              # C19 limb (c)
PLANT_NON_ORTH_DEG = 88.889                # C3/C4, the L-459 value measured on this box
PLANT_CP = 1.234e-01                       # C10
PLANT_CD = 7.531e-03                       # C14

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


# --------------------------------------------------------------------------------------
# EXIT VOCABULARY.  Section 9.2: assertions do not gate; every check is an explicit raise.
# --------------------------------------------------------------------------------------
class Refusal(Exception):
    """rc 2.  The comparator REFUSES rather than degrade.  Never a crash."""


class InternalDefect(Exception):
    """rc 70.  A defect in THIS comparator.  Never a finding about the M6."""


class Unregistered(Refusal):
    """rc 2.  A parameter the frozen registration does not register.

    Picking one here would be choosing a gate parameter AFTER the freeze, which is exactly
    what standing rule 2 forbids.  The comparator names the gap and refuses.
    """


def _verdict(v):
    if v not in VERDICTS:
        raise InternalDefect(
            f"{v!r} is not in the fixed vocabulary {VERDICTS}. Standing rule 1 admits no "
            "synonym and no hedge.")
    return v


# --------------------------------------------------------------------------------------
# HASHING.  Section 1.4 / Section 5 A5: the hash is taken on the DECOMPRESSED byte stream,
# because a gzip hash also encodes the compressor's settings and mtime, which are not the
# mesh, and two identical node sets compressed differently would report as distinct.
# --------------------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_decompressed(path):
    """sha256 of the DECOMPRESSED stream.  Section 5, A5's mechanics."""
    op = gzip.open if path.endswith(".gz") else open
    h = hashlib.sha256()
    with op(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha(path, expected, what):
    if not os.path.exists(path):
        raise Refusal(f"{what}: {path} is ABSENT. An absent pinned artifact is a REFUSAL, "
                      "never a fallback.")
    got = sha256_file(path)
    if got != expected:
        raise Refusal(f"{what}: {path} sha256 {got} != pinned {expected}. REFUSED -- the "
                      "registration pins this artifact by hash and admits no substitute "
                      "(Section 4.1, Section 5).")
    return got


# --------------------------------------------------------------------------------------
# READER 1 -- checkMesh.  Gate A, A1/A2/A3.
#
# L-459: on this box checkMesh prints "Non-orthogonality check OK." at 88.889 deg, and its
# closing "Failed N mesh checks" counts a DIFFERENT check entirely.  This reader therefore
# reads the NAMED NUMERIC MAXIMA and NEVER a verdict string.  Both circulating label forms
# are matched -- the "=" form and the ":" form -- so control C1 can prove it sees each.
# An ABSENT log reads ABSENT.  IT NEVER READS CLEAN (Section 5).
# --------------------------------------------------------------------------------------
_NUM = r"([-+]?[0-9]*\.?[0-9]+(?:[EeDd][-+]?[0-9]+)?)"

_CM_PATTERNS = {
    "max_aspect_ratio": re.compile(r"Max aspect ratio\s*[=:]\s*" + _NUM),
    "max_skewness": re.compile(r"Max skewness\s*[=:]\s*" + _NUM),
    "max_non_orthogonality_deg": re.compile(
        r"Mesh non-orthogonality\s+Max\s*[=:]\s*" + _NUM),
    "min_volume": re.compile(r"Min volume\s*[=:]\s*" + _NUM),
    "max_volume": re.compile(r"Max volume\s*[=:]\s*" + _NUM),
    "n_regions": re.compile(r"Number of regions\s*[=:]\s*([0-9]+)"),
    "n_cells": re.compile(r"^\s*cells:\s*([0-9]+)", re.M),
}
_CM_OPENNESS = re.compile(r"Boundary openness\s*\(\s*" + _NUM + r"\s+" + _NUM + r"\s+" + _NUM)


def read_checkmesh(path):
    """-> dict of NAMED NUMERIC MAXIMA.  Never a verdict string.  Section 5, L-459."""
    if not os.path.exists(path):
        return {"state": "ABSENT", "path": path}
    text = open(path, errors="replace").read()
    out = {"state": "READ", "path": path}
    for key, rx in _CM_PATTERNS.items():
        m = rx.search(text)
        if m is None:
            out[key] = None
            continue
        raw = m.group(1).replace("D", "E").replace("d", "e")
        out[key] = int(raw) if key in ("n_regions", "n_cells") else float(raw)
    m = _CM_OPENNESS.search(text)
    if m is None:
        out["boundary_openness_max_abs"] = None
    else:
        out["boundary_openness_max_abs"] = max(abs(float(m.group(i))) for i in (1, 2, 3))
    # Reported so a reader can SEE that the verdict string was available and unused.
    out["verdict_strings_present_and_IGNORED"] = {
        "non_orthogonality_check_OK": "Non-orthogonality check OK." in text,
        "failed_N_mesh_checks": bool(re.search(r"Failed\s+\d+\s+mesh checks", text)),
    }
    if out["min_volume"] is not None and out["max_volume"] not in (None, 0.0):
        out["cell_volume_ratio"] = out["max_volume"] / out["min_volume"]
    else:
        out["cell_volume_ratio"] = None
    return out


# --------------------------------------------------------------------------------------
# READER 2 -- polyMesh.  A5/A6/A7/A9, Section 7, and the Gate GF surface.
# --------------------------------------------------------------------------------------
_OF_HEAD = re.compile(r"^\s*(?:/\*|\||\\\\|//|FoamFile|\{|\}|version|format|class|"
                      r"location|object|arch|note)", re.I)


_LIST_OPEN = re.compile(r"^\s*(\d+)\s*\n\s*\(", re.M)


def _strip_foam_header(text):
    """Return the LIST BODY: after the FoamFile dictionary AND after the `<count>\\n(` that
    opens the list.

    MEASURED DEFECT THIS GUARDS (2026-09-04): leaving the `<count>\\n(` in place makes the
    per-entry regex consume the count as if it were the first entry's vertex count, which
    silently DROPS THE FIRST FACE and shifts every startFace index by one.  On the
    A3-onera-m6-adjoint-coarse mesh that shift pulled one interior face into the `wing`
    patch and moved the patch's x extent from 0.83 m to 11.24 m.  An off-by-one in a
    reader is not a rounding error; it is a different object.
    """
    i = text.find("// * * *")
    if i >= 0:
        j = text.find("\n", i)
        text = text[j + 1:] if j > 0 else text
    m = _LIST_OPEN.search(text)
    if m is not None:
        return text[m.end():], int(m.group(1))
    return text, None


def _require_count(path, got, declared):
    """The list's own declared length is a CHECK, never a suggestion."""
    if declared is not None and got != declared:
        raise Refusal(
            f"{path}: parsed {got} entries but the file declares {declared}. A reader that "
            "silently disagrees with its own file's count is not an instrument. REFUSED.")


def read_points(polymesh_dir):
    """-> list of (x, y, z).  Reads points or points.gz.  Uncompressed stream only."""
    for cand in ("points", "points.gz"):
        p = os.path.join(polymesh_dir, cand)
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rb") as fh:
                text = fh.read().decode("utf-8", "replace")
            body, declared = _strip_foam_header(text)
            pts = []
            for m in re.finditer(r"\(\s*" + _NUM + r"\s+" + _NUM + r"\s+" + _NUM + r"\s*\)",
                                 body):
                pts.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
            if not pts:
                raise Refusal(f"{p}: zero points parsed. A reader that returns nothing is "
                              "not evidence of an empty mesh. REFUSED.")
            _require_count(p, len(pts), declared)
            return pts
    raise Refusal(f"{polymesh_dir}: neither points nor points.gz. REFUSED.")


def points_stream_sha(polymesh_dir):
    """A5.  sha256 of the DECOMPRESSED constant/polyMesh/points byte stream."""
    for cand in ("points", "points.gz"):
        p = os.path.join(polymesh_dir, cand)
        if os.path.exists(p):
            return sha256_decompressed(p)
    raise Refusal(f"{polymesh_dir}: no points file to hash. REFUSED.")


def read_faces(polymesh_dir):
    """-> list of point-index tuples, in file order (startFace indexing is into this)."""
    for cand in ("faces", "faces.gz"):
        p = os.path.join(polymesh_dir, cand)
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rb") as fh:
                body, declared = _strip_foam_header(fh.read().decode("utf-8", "replace"))
            faces = []
            for m in re.finditer(r"(\d+)\s*\(([^)]*)\)", body):
                idx = m.group(2).split()
                if len(idx) == int(m.group(1)):
                    faces.append(tuple(int(v) for v in idx))
            if not faces:
                raise Refusal(f"{p}: zero faces parsed. REFUSED.")
            _require_count(p, len(faces), declared)
            return faces
    raise Refusal(f"{polymesh_dir}: no faces file. REFUSED.")


_BND_ENTRY = re.compile(
    r"^\s*([A-Za-z_][\w.\-]*)\s*\n\s*\{(.*?)\}", re.S | re.M)


def read_boundary(polymesh_dir):
    """-> ordered list of {name, type, nFaces, startFace}.  A9 and Section 7."""
    p = os.path.join(polymesh_dir, "boundary")
    if not os.path.exists(p):
        p += ".gz"
    if not os.path.exists(p):
        raise Refusal(f"{polymesh_dir}: no boundary file. Section 7 REFUSES a level whose "
                      "patch identity cannot be read.")
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rb") as fh:
        body, _declared = _strip_foam_header(fh.read().decode("utf-8", "replace"))
    out = []
    for m in _BND_ENTRY.finditer(body):
        blk = m.group(2)
        ty = re.search(r"\btype\s+([\w:]+)\s*;", blk)
        nf = re.search(r"\bnFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"\bstartFace\s+(\d+)\s*;", blk)
        if ty is None or nf is None or sf is None:
            continue
        out.append({"name": m.group(1), "type": ty.group(1),
                    "nFaces": int(nf.group(1)), "startFace": int(sf.group(1))})
    if not out:
        raise Refusal(f"{p}: zero patches parsed. REFUSED -- Section 7's screen cannot run "
                      "on a boundary this reader cannot see.")
    return out


def wing_patch_faces(polymesh_dir):
    """-> (points, [face index tuples of the wall patch]).  Gate GF's surface."""
    bnd = read_boundary(polymesh_dir)
    wall = [b for b in bnd if b["type"] == "wall"]
    if len(wall) != 1:
        raise Refusal(f"{polymesh_dir}: {len(wall)} patches typed 'wall'; Gate GF measures "
                      "the wing surface and refuses to guess which patch that is.")
    pts = read_points(polymesh_dir)
    faces = read_faces(polymesh_dir)
    s, n = wall[0]["startFace"], wall[0]["nFaces"]
    if s + n > len(faces):
        raise Refusal(f"{polymesh_dir}: wall patch spans faces {s}..{s+n} but only "
                      f"{len(faces)} faces were read. REFUSED.")
    return pts, faces[s:s + n], wall[0]["name"]


# --------------------------------------------------------------------------------------
# GATE GF READERS -- Section 5, by the method of
# M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md Section 4.2-4.3, CITED not amended.
#
# The instrument-rejection discipline (Section 5) is NOT optional: no Gate GF number is
# quoted until C17, C18, C19 and C20 have all fired.
# --------------------------------------------------------------------------------------
def mesh_axes(polymesh_dir):
    """-> {'span', 'chord', 'thickness', 'root_value'} as AXIS INDICES, DERIVED, not assumed.

    Section 5 writes the root section as "y = 0 exactly".  That is the REGISTRATION'S
    notation.  MEASURED on this box's own M6 meshes, the span runs along z (root plane at
    z = 0, semispan 1.2164 m), the thickness along y, and the chord along x.  Hardcoding
    either convention would silently measure the wrong section, so the axes are DERIVED:

      span axis      -- the axis normal to the SYMMETRY patch (the root plane, Section 7)
      chord axis     -- of the remaining two, the one with the larger wall-patch extent
      thickness axis -- the last one

    A mesh whose symmetry patch is not planar, or whose remaining two extents are within
    a factor of two of each other, is REFUSED rather than guessed at.
    """
    bnd = read_boundary(polymesh_dir)
    sym = [b for b in bnd if b["type"] == "symmetry"]
    if len(sym) != 1:
        raise Refusal(f"{polymesh_dir}: {len(sym)} patches typed 'symmetry'; the root plane "
                      "cannot be derived and Gate GF REFUSES to assume one (Section 7).")
    pts = read_points(polymesh_dir)
    faces = read_faces(polymesh_dir)
    s, n = sym[0]["startFace"], sym[0]["nFaces"]
    used = set()
    for f in faces[s:s + n]:
        used.update(f)
    coords = [pts[i] for i in sorted(used)]
    extents = [max(p[a] for p in coords) - min(p[a] for p in coords) for a in (0, 1, 2)]
    span = min(range(3), key=lambda a: extents[a])
    if extents[span] > 1.0e-06:
        raise Refusal(f"{polymesh_dir}: the symmetry patch is not planar (thinnest extent "
                      f"{extents[span]:.3e} m). REFUSED rather than fitted.")
    root_value = sum(p[span] for p in coords) / len(coords)

    _pts, wf, _name = wing_patch_faces(polymesh_dir)
    wused = set()
    for f in wf:
        wused.update(f)
    wnodes = [pts[i] for i in sorted(wused)]
    rest = [a for a in (0, 1, 2) if a != span]
    ext = {a: max(p[a] for p in wnodes) - min(p[a] for p in wnodes) for a in rest}
    chord = max(rest, key=lambda a: ext[a])
    thick = [a for a in rest if a != chord][0]
    if ext[chord] < 2.0 * ext[thick]:
        raise Refusal(f"{polymesh_dir}: chord extent {ext[chord]:.4f} m is not clearly "
                      f"larger than thickness extent {ext[thick]:.4f} m; the chordwise axis "
                      "cannot be identified and Gate GF REFUSES to pick one.")
    return {"span": span, "chord": chord, "thickness": thick, "root_value": root_value,
            "axis_names": {"span": "xyz"[span], "chord": "xyz"[chord],
                           "thickness": "xyz"[thick]}}


def root_section_nodes(pts, wing_faces, axes, tol=1.0e-09):
    """Nodes of the wall patch ON THE ROOT PLANE, in (chord, span, thickness) order.

    Returned in a canonical (chordwise, spanwise, thickness) triple so every downstream
    reader is axis-independent and control C17's planted rows read back identically.
    """
    used = set()
    for f in wing_faces:
        used.update(f)
    sp, ch, th = axes["span"], axes["chord"], axes["thickness"]
    rv = axes["root_value"]
    root = [(pts[i][ch], pts[i][sp], pts[i][th])
            for i in sorted(used) if abs(pts[i][sp] - rv) <= tol]
    if not root:
        raise Refusal(f"no wall-patch node lies on the root plane {axes['axis_names']['span']}"
                      f" = {rv} within {tol} m; the root section cannot be measured and "
                      "Gate GF REFUSES rather than move the plane.")
    return root


def te_thickness_over_chord(root):
    """GF1.  t_TE/c from the root section's trailing-edge nodes.

    Control C17 plants a split trailing edge and requires a NON-ZERO here: a t_TE/c = 0
    from a reader not shown able to report a non-zero is NOT evidence of a sharp TE.
    """
    xs = [p[0] for p in root]
    zs = [p[2] for p in root]
    x_lo, x_hi = min(xs), max(xs)
    chord = x_hi - x_lo
    if chord <= 0.0:
        raise Refusal("root section has zero chordwise extent. REFUSED.")
    # Trailing-edge nodes: those within one part in 1e6 of the maximum x.
    te = [p for p in root if (x_hi - p[0]) <= 1.0e-06 * chord]
    z_te = [p[2] for p in te]
    t_te = (max(z_te) - min(z_te)) if len(z_te) >= 2 else 0.0
    return {
        "chord_m": chord, "x_min": x_lo, "x_max": x_hi,
        "n_te_nodes": len(te), "t_te_m": t_te, "t_te_over_c": t_te / chord,
        "z_span_m": max(zs) - min(zs),
    }


def section_upper_lower(root):
    """Split the root section into upper and lower surfaces by z, in x/c."""
    xs = [p[0] for p in root]
    x_lo, x_hi = min(xs), max(xs)
    c = x_hi - x_lo
    if c <= 0.0:
        raise Refusal("zero chord in section split. REFUSED.")
    upper, lower = [], []
    for x, _y, z in root:
        (upper if z >= 0.0 else lower).append(((x - x_lo) / c, z / c))
    upper.sort()
    lower.sort()
    return upper, lower


def _interp(curve, x):
    """Linear interpolation on a sorted [(x, z)] curve; None outside its support."""
    if len(curve) < 2 or x < curve[0][0] or x > curve[-1][0]:
        return None
    lo, hi = 0, len(curve) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if curve[mid][0] <= x:
            lo = mid
        else:
            hi = mid
    x0, z0 = curve[lo]
    x1, z1 = curve[hi]
    if x1 == x0:
        return z0
    return z0 + (z1 - z0) * (x - x0) / (x1 - x0)


def max_abs_dz_over_c(root, reference_rows):
    """GF2.  max |dz|/c of the root section against Table B1-1 over 0.001 <= x/c <= 0.999.

    Control C18 plants +5.000e-04 c on every reference ordinate and requires this number
    to move by the planted amount.
    """
    upper, _lower = section_upper_lower(root)
    worst, worst_x = 0.0, None
    n = 0
    for x, z in reference_rows:
        if not (GF2_X_LO <= x <= GF2_X_HI):
            continue
        zi = _interp(upper, x)
        if zi is None:
            continue
        n += 1
        d = abs(zi - z)
        if d > worst:
            worst, worst_x = d, x
    if n == 0:
        raise Refusal("GF2 compared ZERO reference ordinates against the section. A zero "
                      "from a reader with no overlap is not a measurement. REFUSED.")
    return {"max_abs_dz_over_c": worst, "at_x_over_c": worst_x, "n_compared": n}


def planform(pts, wing_faces, axes=None):
    """GF4 and control C20.  Leading-edge sweep, semispan, and the straight-edge residual.

    C20: the straight leading edge has a KNOWN answer -- a residual at machine epsilon.
    Two readers were rejected on exactly this (5.27e-01 m and 1.236e-02 m) before a third
    was quoted.  A reader that has not been rejected on something is not an instrument.
    """
    used = set()
    for f in wing_faces:
        used.update(f)
    if axes is None:
        nodes = [pts[i] for i in sorted(used)]           # already canonical
    else:
        ch, sp, th = axes["chord"], axes["span"], axes["thickness"]
        nodes = [(pts[i][ch], pts[i][sp], pts[i][th]) for i in sorted(used)]
    ys = [p[1] for p in nodes]
    span_extent = max(ys) - min(ys)

    # THE LEADING EDGE, BY THE LOWER CONVEX HULL IN (span, chord).  PARAMETER-FREE.
    #
    # THREE READERS WERE TRIED AND TWO WERE REJECTED, per the instrument-rejection
    # discipline of Section 5:
    #   (1) "minimum chord at each spanwise station" -- REJECTED.  MEASURED: the surface
    #       nodes are NOT on constant-span lines (1,427 distinct span values for 1,595
    #       nodes), so most stations carry a single node nowhere near the leading edge.
    #       It returned a 0.476 m straightness residual on a leading edge that is straight.
    #   (2) "bin the span, take the minimum chord per bin, least-squares fit" -- REJECTED.
    #       MEASURED: bin-count dependent.  10 bins gave 29.702 deg / 3.6e-02 m, 80 bins
    #       gave 22.195 deg / 5.3e-01 m on the SAME mesh.  A reader with a free parameter
    #       that moves the answer by 7 degrees is not an instrument.
    #   (3) the lower convex hull of the (span, chord) projection -- ADOPTED.  It has no
    #       free parameter, and it returns 29.9999843 deg with a ZERO deviation along the
    #       leading chain on both existing levels, against AGARD's 30.0000000 deg.
    # The LOWER ENVELOPE first: one point per distinct span, at the MINIMUM chord.  Without
    # it the hull closes with a VERTICAL segment at the outboard extreme (two nodes share
    # that span, the aft one is a hull vertex), and control C20 LIMB 1 measured the damage:
    # a known-straight edge reported a 1.0 m residual, which is the chord itself.  The
    # envelope is not the rejected "min chord per station" READER -- that reader FITTED a
    # line through every station; here the hull discards the aft stations by construction.
    env = {}
    for p in nodes:
        if p[1] not in env or p[0] < env[p[1]]:
            env[p[1]] = p[0]
    cloud = sorted(env.items())                            # (span, chord)
    if len(cloud) < 3:
        raise Refusal("fewer than three distinct (span, chord) nodes; the leading edge "
                      "cannot be constructed. REFUSED.")

    def _cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    hull = []
    for pt in cloud:
        while len(hull) >= 2 and _cross(hull[-2], hull[-1], pt) <= 0:
            hull.pop()
        hull.append(pt)
    if len(hull) < 2:
        raise Refusal("degenerate leading hull. REFUSED.")

    edges = sorted(zip(hull, hull[1:]), key=lambda e: e[1][0] - e[0][0], reverse=True)
    (s0, c0), (s1, c1) = edges[0]
    if s1 == s0:
        raise Refusal("the longest leading-hull edge has zero span extent. REFUSED.")
    a = (c1 - c0) / (s1 - s0)
    b = c0 - a * s0
    # THE RESIDUAL IS MEASURED FROM THE INBOARD END OF THE HULL, NOT FROM THE LONGEST
    # EDGE'S OWN INBOARD VERTEX.  MEASURED DEFECT IN THIS LANE'S FIRST FORM (control C20
    # LIMB 2 caught it): a forward bulge BECOMES a hull vertex, splitting the leading chain
    # into two edges, and a residual evaluated only inside the longest edge's own span
    # range then sees a chain of two collinear endpoints and returns ZERO -- a fail-open
    # that would have reported a bulged leading edge as straight.  Evaluating from the
    # hull's inboard end to the longest edge's outboard end makes the bulge a deviation
    # again, and still returns exactly zero on a genuinely straight edge (both existing
    # levels measure 0.000e+00).
    resid = max(abs(c - (a * s + b)) for s, c in hull)
    inboard = max((abs(c - (a * s + b)) for s, c in hull if s <= s1 + 1e-12), default=0.0)

    return {
        # TWO DIFFERENT SEMISPANS, both reported, because they differ by 1.7 % against a
        # 0.1 % tolerance and the registration does not say which GF4 means.
        "span_extent_of_wall_patch_m": span_extent,
        "planform_semispan_from_LE_line_m": s1 - min(p[0] for p in cloud),
        "le_sweep_deg": math.degrees(math.atan(a)),
        # The straightness residual is taken over the WHOLE leading chain, not inside the
        # longest edge's own span range.  Control C20 LIMB 2 measured why: a forward bulge
        # BECOMES a hull vertex and splits the chain, so a window-limited residual sees two
        # collinear endpoints and returns ZERO -- reporting a bulged leading edge as
        # straight.  The inboard-only figure is reported beside it, never instead of it.
        "le_straightness_residual_m": resid,
        "le_straightness_residual_inboard_of_LE_line_end_m": inboard,
        "le_edge_span_range": [s0, s1],
        "le_edge_fraction_of_span": (s1 - s0) / span_extent if span_extent else None,
        "n_hull_points": len(hull),
        "instrument": "lower convex hull of the (span, chord) projection; parameter-free",
    }


# --------------------------------------------------------------------------------------
# GATE GF's REFERENCE LOADER -- control C19.  Section 5 pins path AND sha256, and the
# comparator loads Table B1-1 ONLY through that path at that hash, REFUSING (exit 2) if
# the hash does not match.
# --------------------------------------------------------------------------------------
def load_table_b1_1(path=None, verify_hash=True):
    try:
        from scripts import verify_agard_ar138_table_b1_1 as loader
    except ImportError:
        sys.path.insert(0, os.path.join(REPO, "scripts"))
        try:
            import verify_agard_ar138_table_b1_1 as loader
        except ImportError as exc:
            raise Refusal(f"the registered Table B1-1 loader is not importable: {exc}. "
                          "Section 5 names it as the ONLY route to this reference.")
    p = path or os.path.join(REPO, PATH_TABLE_B1_1)
    if verify_hash:
        require_sha(p, SHA_TABLE_B1_1, "Gate GF reference (Table B1-1)")
    try:
        return loader.load_reference(p), loader
    except (loader.SharpenedReferenceError, loader.ReferenceStructureError) as exc:
        raise Refusal(f"Table B1-1 loader REFUSED {p}: {exc}")


# --------------------------------------------------------------------------------------
# GATE P READERS -- case_2308.dat, Section 4.1, pinned by sha256.
# --------------------------------------------------------------------------------------
_ZONE = re.compile(r'^ZONE\s+T\s*=\s*"([^"]*)"\s*,\s*I\s*=\s*(\d+)', re.M)


def read_case_2308(path=None, verify_hash=True):
    """-> {section_index: [(tap, x_over_l, z_over_l, cp)]}, plus the zone titles.

    Section 4.1: THERE IS NO Y COLUMN.  The spanwise assignment is A-MAP, an ASSUMPTION.
    """
    p = path or os.path.join(REPO, PATH_CASE_2308)
    if verify_hash:
        require_sha(p, SHA_CASE_2308, "Gate P reference (case_2308.dat)")
    if not os.path.exists(p):
        raise Refusal(f"{p} is ABSENT. REFUSED.")
    text = open(p, errors="replace").read()
    lines = text.split("\n")
    sections, titles = {}, {}
    cur = None
    for ln in lines:
        m = _ZONE.match(ln)
        if m:
            cur = len(sections) + 1
            sections[cur] = []
            titles[cur] = m.group(1)
            continue
        f = ln.split()
        if cur is None or len(f) != 5:
            continue
        try:
            vals = [float(v) for v in f]
        except ValueError:
            continue
        sections[cur].append((vals[1], vals[2], vals[3], vals[4]))
    if not sections:
        raise Refusal(f"{p}: zero ZONE blocks parsed. A reader that sees nothing is not "
                      "evidence of an empty file. REFUSED.")
    total = sum(len(v) for v in sections.values())
    return {"sections": sections, "titles": titles, "n_sections": len(sections),
            "n_taps_total": total}


def d1_discriminator(ref):
    """Section 4.3.  Cn(s) = -(closed-loop trapezoidal integral of CP over d(x/c)).

    REGISTERED BEFORE EVALUATION AND EVALUATED HERE, whichever way it comes out.
    Controls C12 (reversed sections -> FALSIFIED) and C13 (identical sections ->
    INDETERMINATE) prove the second and third branches are REACHABLE.  A discriminator that
    structurally cannot falsify is a disclaimer, not a test.
    """
    sec = ref["sections"]
    keys = sorted(sec)
    cn = {}
    for k in keys:
        rows = sec[k]
        if len(rows) < 3:
            raise Refusal(f"section {k} carries {len(rows)} taps; a closed-loop integral "
                          "needs at least three. REFUSED.")
        tot = 0.0
        n = len(rows)
        for i in range(n):
            _t0, x0, _z0, c0 = rows[i]
            _t1, x1, _z1, c1 = rows[(i + 1) % n]      # closing last tap -> first
            tot += 0.5 * (c0 + c1) * (x1 - x0)
        cn[k] = -tot
    order = [cn[k] for k in keys]
    strictly_dec = all(b < a for a, b in zip(order, order[1:]))
    strictly_inc = all(b > a for a, b in zip(order, order[1:]))
    first, last = order[0], order[-1]
    ratio_last_first = (last / first) if first != 0.0 else float("inf")
    ratio_first_last = (first / last) if last != 0.0 else float("inf")

    if strictly_dec and ratio_last_first <= D1_MARGIN:
        verdict, consequence = "CORROBORATED", "Gate P grades under A-MAP as registered"
    elif strictly_inc and ratio_first_last <= D1_MARGIN:
        verdict, consequence = "FALSIFIED", (
            "A-MAP IS REVERSED. Gate P grades against the reversed mapping and the "
            "reversal is printed on the certificate as a registered FINDING, not a repair")
    else:
        verdict, consequence = "INDETERMINATE", (
            "Gate P's PER-STATION channel is NOT A RESULT; Section 4.5's order-independent "
            "channel is the only Gate P output")
    return {
        "Cn_by_section": {str(k): cn[k] for k in keys},
        "strictly_decreasing": strictly_dec, "strictly_increasing": strictly_inc,
        "Cn_last_over_first": ratio_last_first, "Cn_first_over_last": ratio_first_last,
        "registered_margin": D1_MARGIN,
        "verdict": verdict, "consequence_for_gate_P": consequence,
        "circularity_disclosure": (
            "D1 uses the SAME CP column Gate P grades on. It is NOT independent of Gate P's "
            "data. It IS independent of Gate P's CFD, and that is the direction rule 2 cares "
            "about. This registration claims no more (Section 4.3)."),
        "what_D1_cannot_do": (
            "D1 distinguishes ORDERING, not ASSIGNMENT. A permutation that is neither the "
            "identity nor the reversal fires the INDETERMINATE branch; D1 does not attempt "
            "to recover the true permutation (Section 4.3)."),
    }


# --------------------------------------------------------------------------------------
# GATE P's CFD PRODUCER -- Section 8.5's seven registered stations, cut on the SAMPLED WING
# SURFACE.
#
# WHY THIS EXISTS.  Amendment 10 item 5 records, measured by AST call graph, that "There is
# additionally NO producer of `cfd_sections` anywhere -- no reader samples CFD Cp at the
# seven registered y/b stations, and the build driver writes no sampleDict", and that in
# consequence BOTH Gate P channels were dead on the code.  This section is that producer.
#
# HOW THE STATIONS ARE CUT, AND WHY THERE IS NO TOLERANCE PARAMETER.  cases/M6SR/
# write_m6sr_case.py writes system/sampleDict, which samples the WALL PATCH with
# `interpolate true` through the `foam` surface writer -- giving POINT-valued p on the patch
# triangulation together with its connectivity.  Cutting that by a constant-span plane is
# EXACT LINEAR INTERPOLATION ALONG TRIANGLE EDGES.  A face-centre reader would have needed a
# spanwise binning tolerance, and a binning tolerance is an instrument parameter no lane is
# entitled to choose.  There is none here.
#
# THE SPAN AXIS IS DERIVED, NEVER ASSUMED.  Section 8.5 says "seven constant-y planes"; the
# comparator's own mesh_axes() records, MEASURED, that on this box's M6 meshes the span runs
# along z.  "y" is the registration's NOTATION.  Every station coordinate below is placed on
# the axis mesh_axes() derives from the symmetry patch.
# --------------------------------------------------------------------------------------
P_INF_PA = 101325.0                        # Section 3, REGISTERED CHOICE (ISA sea level)
RHO_INF_KGM3 = 1.224978126                 # Section 3, derived p/(R T)
U_INF_MS = 285.679356                      # Section 3, derived M a
B_SEMI_M = 1.19676                         # Section 8.5, the registered semispan
P_MIN_POINTS_PER_STATION = 10              # below this a "curve" is not a section
PLANT_SAMPLED_P_PA = 4.321e+03             # C21, planted on the sampled p field
PLANT_CP_UPPER_ONLY = 3.579e-01            # C24, planted on the UPPER surface alone
P_MIN_POINTS_PER_SIDE = 2                  # a curve needs two points to exist at all


def q_inf_pa():
    """The dynamic pressure Cp is normalised by.  Both constants are Section 3's."""
    return 0.5 * RHO_INF_KGM3 * U_INF_MS ** 2


def registered_stations():
    """Section 8.5.  The seven registered y/b times the registered semispan.

    A_MAP_YB is Section 4's registered set and Section 16.4 records it read at source in
    docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt lines
    13728-13729.  THE SIXTH STATION IS 0.96, WHICH IS WHAT AGARD AR-138 Section 5.1.1
    PRINTS, and NOT the 0.95 of NASA TMR's widely circulated set -- Section 16.4 registers
    that divergence as REPORTED, NOT GATED.  Nothing here chooses it; it is read off the
    frozen constant.
    """
    return [{"index": i + 1, "y_over_b": yb, "span_coord_m": yb * B_SEMI_M}
            for i, yb in enumerate(A_MAP_YB)]


def split_curve_upper_lower(rows):
    """-> {'upper', 'lower', ...}.  Rows are (x_over_c, thickness_coord, value).

    AMENDMENT 11, RULING 3.  Amendment 11 item 21 measured that Section 4.5's channel builds
    BOTH its curves as sorted (x, Cp) through a single-valued _interp(), so upper and lower
    surface points are INTERLEAVED in x.  At any x/c a wing section carries TWO Cp values.
    A Cp-vs-x/c FIGURE -- Sanaa's named deliverable -- cannot be plotted from an interleaved
    curve, so the figure channel is SPLIT here.

    CONVENTION: thickness >= 0.0 is UPPER.  It is the SAME convention section_upper_lower()
    already uses for GF2's root section: there is one reader in this repository for what
    "upper" means, and this is not a second one.  A point at exactly zero thickness (a
    leading-edge tap; MEASURED, section 4 of case_2308.dat carries one) therefore lands in
    UPPER, deterministically, and the count of such points is REPORTED rather than hidden.

    REFUSES if either side carries fewer than P_MIN_POINTS_PER_SIDE points.  A one-sided
    section would plot as a PERFECT ABSENCE of the missing surface rather than as a
    disagreement -- the same class of false zero standing rule 3 exists for, and the same
    reason C22 refuses an out-of-span station instead of returning an empty curve.

    IT GRADES NOTHING.  Section 4.5's set_to_set_assignment() is BYTE-UNCHANGED by this
    amendment and still interleaves; changing a graded channel's RMS is a gate question and
    is not a lane's.
    """
    upper, lower, n_zero = [], [], 0
    for x, t, v in rows:
        if t == 0.0:
            n_zero += 1
        (upper if t >= 0.0 else lower).append((x, v))
    upper.sort()
    lower.sort()
    if len(upper) < P_MIN_POINTS_PER_SIDE or len(lower) < P_MIN_POINTS_PER_SIDE:
        raise Refusal(
            f"upper/lower split returned {len(upper)} upper and {len(lower)} points from "
            f"{len(rows)}; a side below {P_MIN_POINTS_PER_SIDE} points is not a curve. An "
            "empty or single-point side would PLOT as a perfect absence of that surface "
            "rather than as a disagreement (standing rule 3). REFUSED rather than degrade.")
    return {"upper": upper, "lower": lower,
            "n_upper": len(upper), "n_lower": len(lower),
            "n_at_exactly_zero_thickness_counted_UPPER": n_zero,
            "convention": ("thickness >= 0 is UPPER, the same convention "
                           "section_upper_lower() uses for GF2's root section")}


def read_surface_scalar(path):
    """-> list of scalars from an OpenFOAM scalarField list, or a REFUSAL."""
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        raise Refusal(f"{path} is ABSENT. Gate P's CFD channel cannot read surface pressure "
                      "from a file that is not there, and an absent field never reads as a "
                      "freestream. REFUSED.")
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rb") as fh:
        body, declared = _strip_foam_header(fh.read().decode("utf-8", "replace"))
    vals = []
    for tok in body.split():
        if tok.startswith(")"):
            break
        try:
            vals.append(float(tok))
        except ValueError:
            break
    if not vals:
        raise Refusal(f"{path}: zero scalars parsed. A reader that returns nothing is not "
                      "evidence of an empty field. REFUSED.")
    _require_count(path, len(vals), declared)
    return vals


def cut_surface_at_plane(points, faces, values, span_axis, coord):
    """Exact cut of a triangulated/polygonal surface by the plane <span_axis> = coord.

    -> [((x, y, z), value)] at every edge crossing.  Linear along the edge in BOTH the
    coordinate and the field, which is what makes the station curve exact rather than binned.
    """
    out = []
    for f in faces:
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            if a >= len(points) or b >= len(points):
                raise Refusal(f"a sampled face indexes point {max(a, b)} but only "
                              f"{len(points)} points were read. An off-by-one in a reader is "
                              "not a rounding error; it is a different object. REFUSED.")
            sa = points[a][span_axis] - coord
            sb = points[b][span_axis] - coord
            if sa == 0.0:
                out.append((points[a], values[a]))
                continue
            if sb == 0.0:
                continue                                  # picked up when b is the `a` end
            if (sa < 0.0) != (sb < 0.0):
                t = sa / (sa - sb)
                pt = tuple(points[a][k] + t * (points[b][k] - points[a][k])
                           for k in range(3))
                out.append((pt, values[a] + t * (values[b] - values[a])))
    return out


def cfd_sections_from_surface(surface_dir, span_axis, chord_axis, stations=None,
                              field="p", plant_pa=0.0):
    """-> ({station_index: [(x_over_c, Cp)]}, meta) from a `foam`-written sampled surface.

    The shape of the first return value is EXACTLY what Section 4.5's
    set_to_set_assignment() consumes: a mapping to a list of (x, Cp) pairs.

    `plant_pa` is control C21's hook: a known offset added to the pressure this reader has
    just read FROM DISK, so the suite can prove the reader can see a non-zero (rule 3).
    """
    if not os.path.isdir(surface_dir):
        raise Refusal(f"{surface_dir} is ABSENT. Gate P's CFD channel has no sampled wing "
                      "surface. Section 8.5's sampleDict is written by cases/M6SR/"
                      "write_m6sr_case.py and sampled by the solver at endTime; an absent "
                      "directory means the solve did not produce it. REFUSED.")
    pts = read_points(surface_dir)
    faces = read_faces(surface_dir)
    vals = read_surface_scalar(os.path.join(surface_dir, "scalarField", field))
    if len(vals) != len(pts):
        raise Refusal(
            f"{surface_dir}: {len(vals)} sampled {field} values against {len(pts)} points "
            f"({len(faces)} faces). Gate P's cut needs POINT data, which requires "
            "`interpolate true` in system/sampleDict. A face-centre field would force a "
            "spanwise binning tolerance, and this comparator refuses to introduce an "
            "instrument parameter the registration does not register. REFUSED.")
    if plant_pa:
        vals = [v + plant_pa for v in vals]

    stns = stations if stations is not None else registered_stations()
    span_vals = [p[span_axis] for p in pts]
    lo, hi = min(span_vals), max(span_vals)
    q = q_inf_pa()
    # The thickness axis is the remaining one.  It is DERIVED from the two the caller
    # already derived from the mesh, never assumed -- Amendment 11 item 20 records that
    # Section 8.5's "constant-y planes" names the wrong axis on this box's meshes.
    thick_axis = ({0, 1, 2} - {span_axis, chord_axis}).pop()
    out, meta = {}, {"span_axis": "xyz"[span_axis], "chord_axis": "xyz"[chord_axis],
                     "thickness_axis": "xyz"[thick_axis],
                     "sampled_span_extent_m": [lo, hi], "n_points": len(pts),
                     "n_faces": len(faces), "q_inf_Pa": q, "p_inf_Pa": P_INF_PA,
                     "b_semi_m_REGISTERED": B_SEMI_M, "stations": [],
                     "split_by_station": {}}
    for s in stns:
        c = s["span_coord_m"]
        if not (lo <= c <= hi):
            raise Refusal(
                f"station {s['index']} (y/b = {s['y_over_b']}) sits at "
                f"{'xyz'[span_axis]} = {c:.6f} m, OUTSIDE the sampled wing surface's own "
                f"span extent [{lo:.6f}, {hi:.6f}] m. An empty station is a REFUSAL, never "
                "an empty curve: a Cp curve with no points would compare as a perfect "
                "absence rather than as a disagreement. The registered semispan is "
                f"{B_SEMI_M} m (Section 8.5); this surface's is {hi - lo:.6f} m. REFUSED.")
        cross = cut_surface_at_plane(pts, faces, vals, span_axis, c)
        if len(cross) < P_MIN_POINTS_PER_STATION:
            raise Refusal(
                f"station {s['index']} (y/b = {s['y_over_b']}) yielded {len(cross)} edge "
                f"crossings, below the {P_MIN_POINTS_PER_STATION} this reader requires to "
                "call something a section. REFUSED rather than degrade.")
        xs = [pt[chord_axis] for pt, _v in cross]
        x_le, x_te = min(xs), max(xs)
        chord = x_te - x_le
        if chord <= 0.0:
            raise Refusal(f"station {s['index']}: local chord {chord} is not positive; "
                          "x/c is undefined. REFUSED.")
        out[s["index"]] = sorted(((pt[chord_axis] - x_le) / chord, (v - P_INF_PA) / q)
                                 for pt, v in cross)
        # AMENDMENT 11 RULING 3.  The SAME `cross` list, split into two plottable curves.
        # It is built here rather than by a second cut so there is ONE source of truth for
        # what this station's points are; it rides in `meta` so that the (sections, meta)
        # tuple Section 4.5's set_to_set_assignment() consumes is SHAPE-UNCHANGED.
        meta["split_by_station"][str(s["index"])] = split_curve_upper_lower(
            [((pt[chord_axis] - x_le) / chord, pt[thick_axis], (v - P_INF_PA) / q)
             for pt, v in cross])
        meta["stations"].append({
            "index": s["index"], "y_over_b": s["y_over_b"], "span_coord_m": c,
            "n_cut_points": len(cross), "local_chord_m": chord,
            "x_leading_edge_m": x_le, "x_trailing_edge_m": x_te,
            "Cp_min": min(cp for _x, cp in out[s["index"]]),
            "Cp_max": max(cp for _x, cp in out[s["index"]]),
        })
    return out, meta


def cfd_sections_for_case(case_dir, end_time, polymesh_dir=None, plant_pa=0.0):
    """Locate the sampled wing surface for one level and cut Section 8.5's seven stations."""
    axes = mesh_axes(polymesh_dir or os.path.join(case_dir, "constant", "polyMesh"))
    base = os.path.join(case_dir, "postProcessing", "sampleDict")
    surf = os.path.join(base, str(int(end_time)), "wingSurface")
    if not os.path.isdir(surf):
        # The time directory name is written by OpenFOAM's own time formatting; look for it
        # BY EXPLICIT ENUMERATION rather than by a glob whose ordering is a coin flip.
        found = None
        if os.path.isdir(base):
            for t in sorted(os.listdir(base)):
                cand = os.path.join(base, t, "wingSurface")
                if os.path.isdir(cand):
                    try:
                        if abs(float(t) - float(end_time)) < 1e-9:
                            found = cand
                    except ValueError:
                        continue
        if found is None:
            raise Refusal(
                f"no sampled wing surface at {surf} and none at endTime {end_time} under "
                f"{base}. Section 8.5's sampleDict writes it at writeTime; its absence means "
                "either the solve did not reach endTime or the function object did not run. "
                "REFUSED -- an absent sample is not a Cp of zero.")
        surf = found
    sections, meta = cfd_sections_from_surface(surf, axes["span"], axes["chord"],
                                               plant_pa=plant_pa)
    meta["surface_dir"] = surf
    meta["derived_axes"] = axes
    return sections, meta


def gate_p_figure_data(ref, cfd_by_level, meta_by_level, d1):
    """Sanaa's named first physics, as DATA: M6 surface Cp at the AGARD span stations
    against tunnel data, every level's curve, on the seven registered stations.

    IT IS NOT A VERDICT AND IT GRADES NOTHING.  It is written BEFORE Gate G runs precisely
    so that Gate G's registered REFUSAL (X3) cannot take the figure down with it: a refusal
    is a statement about a GATE, and the measured curves are not a gate.  Clause L-HONEST
    rides on it VERBATIM, as Section 16.4 requires of every figure this ladder can produce.
    """
    exp = {}
    for s in sorted(ref["sections"]):
        rows = ref["sections"][s]
        sp = split_curve_upper_lower([(x, z, cp) for _t, x, z, cp in rows])
        exp[str(s)] = {
            "y_over_b_under_A_MAP": A_MAP_YB[s - 1] if s - 1 < len(A_MAP_YB) else None,
            "n_taps": len(rows),
            # AMENDMENT 11 RULING 3: THE TWO CURVES A Cp-vs-x/c FIGURE IS PLOTTED FROM.
            "curve_upper_x_over_c_Cp": sp["upper"],
            "curve_lower_x_over_c_Cp": sp["lower"],
            "n_upper": sp["n_upper"], "n_lower": sp["n_lower"],
            "n_at_exactly_zero_thickness_counted_UPPER":
                sp["n_at_exactly_zero_thickness_counted_UPPER"],
            "curve_x_over_c_Cp_INTERLEAVED_NOT_PLOTTABLE":
                sorted((x, cp) for _t, x, _z, cp in rows),
        }
    return {
        "WHAT_THIS_IS": (
            "M6 surface Cp at the seven AGARD span stations against the AR-138 tunnel data, "
            "with every level of the surface-refinement family. DATA, NOT A VERDICT."),
        "graded_window": f"x/c <= {P_X_OVER_C_GRADED_MAX}",
        "rear_chord": ("the rear 10 % is PLOTTED and REPORTED, NEVER GRADED -- AGARD's "
                       "design trailing edge is 0.14104 % chord thick and this geometry is "
                       "sharp (Section 5)"),
        "A_MAP": {"mapping": list(A_MAP_YB),
                  "status": "ASSUMED. Not measured. Not confirmed by any artifact this lab "
                            "holds (Section 4.1).",
                  "sixth_station_disclosure": (
                      "AGARD AR-138 Section 5.1.1 prints 0.96 at the sixth station; NASA "
                      "TMR's widely circulated set carries 0.95. On a wing swept 30 deg at "
                      "M = 0.8395 that 1 % of semispan is ~1.2 cm of span. THIS LADDER USES "
                      "0.96, which is what its own cited source prints (Section 16.4). "
                      "REPORTED, NOT GATED.")},
        "FIGURE_CURVES": (
            "AMENDMENT 11 RULING 3. Upper and lower surfaces are SEPARATE curves in this "
            "record. Amendment 11 item 21 measured that Section 4.5's channel interleaves "
            "them -- both curves are sorted (x, Cp) through a single-valued _interp() -- and "
            "a Cp-vs-x/c figure cannot be plotted from an interleaved curve. PLOT "
            "curve_upper_x_over_c_Cp and curve_lower_x_over_c_Cp; the interleaved list is "
            "retained under its own name so the two readings can be compared, and it is NOT "
            "plottable. MEASURED on the pinned case_2308.dat: the taps are NOT evenly split "
            "-- 185 of 271 (68.27 %) are UPPER-surface taps (23/11 on sections 1-4, 31/14 on "
            "5-7), so the interleaved curve is implicitly weighted about 2:1 toward the "
            "upper surface. Section 4.5's RMS channel is BYTE-UNCHANGED by this amendment "
            "and still interleaves; that is a graded channel and changing it is a gate "
            "question, not a lane's."),
        "D1": d1,
        "experimental": exp,
        "cfd_by_level": {lv: {str(k): v for k, v in cfd_by_level[lv].items()}
                         for lv in cfd_by_level},
        "cfd_split_by_level": {lv: meta_by_level[lv].get("split_by_station", {})
                               for lv in meta_by_level},
        "cfd_meta_by_level": meta_by_level,
        "Cp_normalisation": {
            "p_inf_Pa": P_INF_PA, "rho_inf_kg_m3": RHO_INF_KGM3, "U_inf_m_s": U_INF_MS,
            "q_inf_Pa": q_inf_pa(),
            "basis": "Section 3's registered state pair. Cp = (p - p_inf) / (0.5 rho U^2).",
        },
        "NOT_A_VERDICT": (
            "This record grades nothing and carries no label from the fixed vocabulary. "
            "Gate P's verdict is gate_p()'s, and Gate P sits BEHIND Gate G."),
        "L_HONEST": L_HONEST,
    }


# --------------------------------------------------------------------------------------
# GATE G READERS -- forces and residuals.
# --------------------------------------------------------------------------------------
_COEFF_HEADER = re.compile(r"^#\s*Time\s+(.*)$", re.M)


def read_force_coeffs(path):
    """-> [(time, {name: value})] from an OpenFOAM forceCoeffs .dat.  Control C14."""
    if not os.path.exists(path):
        raise Refusal(f"{path} is ABSENT. Gate G cannot read C_D from a file that is not "
                      "there, and an absent file never reads converged. REFUSED.")
    text = open(path, errors="replace").read()
    hdr = None
    for m in _COEFF_HEADER.finditer(text):
        cols = m.group(1).split()
        if any(c.lower() in ("cd", "c_d") for c in cols):
            hdr = cols
    if hdr is None:
        raise Refusal(f"{path}: no '# Time ... Cd ...' header. This reader names ONE "
                      "artifact by explicit path and refuses to guess its columns "
                      "(Section 9.2). REFUSED.")
    rows = []
    for ln in text.split("\n"):
        if not ln or ln.lstrip().startswith("#"):
            continue
        f = ln.split()
        if len(f) != len(hdr) + 1:
            continue
        try:
            vals = [float(v) for v in f]
        except ValueError:
            continue
        rows.append((vals[0], dict(zip(hdr, vals[1:]))))
    if not rows:
        raise Refusal(f"{path}: zero data rows. REFUSED.")
    return rows, hdr


def cd_series(path):
    rows, hdr = read_force_coeffs(path)
    key = next((c for c in hdr if c.lower() in ("cd", "c_d")), None)
    if key is None:
        raise Refusal(f"{path}: no Cd column after header parse. REFUSED.")
    return [(t, d[key]) for t, d in rows]


def residual_series(log_path):
    """G2's instrument.  Section 5.1: executed by scripts/residual_max_over_equations.py,
    NEVER by hand.  Controls C7/C8/C9 exercise it on both print forms and on a moving max.
    """
    try:
        from scripts import residual_max_over_equations as red
    except ImportError:
        sys.path.insert(0, os.path.join(REPO, "scripts"))
        try:
            import residual_max_over_equations as red
        except ImportError as exc:
            raise Refusal(f"the registered residual reducer is not importable: {exc}. "
                          "Section 5.1 names it as G2's ONLY instrument.")
    if not os.path.exists(log_path):
        raise Refusal(f"{log_path} is ABSENT. REFUSED.")
    text = open(log_path, errors="replace").read()
    steps, forms = red.reduce_log(text)
    if not steps:
        raise Refusal(f"{log_path}: the reducer saw print forms {sorted(forms)} and "
                      "produced ZERO steps. 'No residuals in this log' and 'residuals this "
                      "reader cannot see' are different findings; this is REFUSED, not zero.")
    return steps, sorted(forms), red


def gate_g2(steps, cd, l3_l2_difference):
    """Section 5.1 G2a/G2b/G2c, machine-checked against the REGISTERED thresholds."""
    series = [s["max_initial_residual"] for s in steps if s["max_initial_residual"] is not None]
    if len(series) < 2:
        raise Refusal("fewer than two reduced residual steps; G2 REFUSES rather than "
                      "degrade.")
    first, last = series[0], series[-1]
    if first <= 0.0 or last <= 0.0:
        raise Refusal("a non-positive reduced residual; orders-of-reduction is undefined "
                      "and G2 REFUSES rather than substitute a floor.")
    orders = math.log10(first / last)
    g2a = orders >= G2A_ORDERS

    # G2b: over the last 1,000 ITERATIONS, not the last 1,000 samples.  Section 9.2's
    # measured-print-interval discipline: the interval is read off the steps themselves.
    def _tail_by_iterations(seq, n_iter):
        if len(seq) < 2:
            return list(seq)
        try:
            t0, t1 = float(steps[0]["time"]), float(steps[1]["time"])
            step_iter = abs(t1 - t0) or 1.0
        except (TypeError, ValueError):
            step_iter = 1.0
        n = max(2, int(math.ceil(n_iter / step_iter)))
        return seq[-n:]

    win_b = _tail_by_iterations(series, G2B_WINDOW_ITERATIONS)
    lo, hi = min(win_b), max(win_b)
    drift = (hi - lo) / hi if hi > 0 else float("inf")
    g2b = drift <= G2B_DRIFT_FRAC

    cd_vals = [v for _t, v in cd]
    win_c = _tail_by_iterations(cd_vals, G2C_WINDOW_ITERATIONS)
    cd_swing = max(win_c) - min(win_c)
    tol_c = G2C_FRACTION_OF_L3_L2 * abs(l3_l2_difference)
    g2c = cd_swing <= tol_c

    return {
        "G2a_orders_of_reduction": orders, "G2a_threshold": G2A_ORDERS, "G2a_pass": g2a,
        "G2b_window_iterations": G2B_WINDOW_ITERATIONS, "G2b_drift_fraction": drift,
        "G2b_threshold": G2B_DRIFT_FRAC, "G2b_pass": g2b,
        "G2c_window_iterations": G2C_WINDOW_ITERATIONS, "G2c_CD_swing": cd_swing,
        "G2c_tolerance": tol_c, "G2c_pass": g2c,
        "plateau_value_max_over_equations_residual": last,
        "MANDATORY_DISCLOSURE": (
            "The residual reaches a FLOOR and does not converge to machine zero. The plateau "
            "value of the max-over-equations residual is REPORTED beside the result. "
            "A PLATEAU IS NOT CONVERGENCE."),
        "threshold_basis_disclosure": (
            "The 4-order / 5 % / 1,000-iteration numbers were chosen by "
            "RUNG1_M6_PREREGISTRATION.md while looking at a DIFFERENT configuration's data "
            "(DARhoSimpleCFoam / Spalart-Allmaras at yPlus mean 33.75). They are not fitted "
            "to this family's answer and are carried forward unchanged (Section 5.1)."),
        "pass": g2a and g2b and g2c,
    }


def roache_triple(f3, f2, f1, r):
    """Standing rule 5, at Fs = 1.25.  f1 = FINE.  Returns the triple's classification.

    GCI is NEVER quoted when the three values are not monotone.  The classification, not
    the number, is what standing rule 5 gates on.
    """
    d32 = f3 - f2
    d21 = f2 - f1
    if d32 == 0.0 and d21 == 0.0:
        cls = "EXACT"
    elif d32 == 0.0 or d21 == 0.0:
        cls = "STAGNANT"
    elif (d32 > 0) != (d21 > 0):
        cls = "OSCILLATORY"
    elif abs(d21) >= abs(d32):
        cls = "DIVERGENT"
    else:
        cls = "CONVERGING"
    p = None
    gci = None
    if cls == "CONVERGING" and r > 1.0:
        p = math.log(abs(d32 / d21)) / math.log(r)
        eps = d21 / f1 if f1 != 0.0 else None
        if eps is not None:
            gci = G4_FS * abs(eps) / (r ** p - 1.0)
    monotone = cls == "CONVERGING"
    return {"classification": cls, "r_used": r, "p_s": p,
            "GCI_fine_at_Fs_1.25": gci if monotone else None,
            "GCI_withheld_because_not_monotone": not monotone,
            "d32": d32, "d21": d21}


# The refinement ratio r is NOT REGISTERED anywhere in the frozen document.  Section 5's G3
# says "from the three-level ratio" and Section 5's G4 says "GCI_fine on C_D at Fs = 1.25",
# but no section fixes r, and three defensible conventions give three different bands.
# Picking one HERE would be choosing a gate parameter after the freeze.  The comparator
# computes all three, prints them, and REFUSES to grade Gate G's band on any of them.
R_CANDIDATES = {
    "r=2.000  linear ratio in the TWO refined surface directions (4x faces = 2x per "
    "direction)": 2.0,
    "r=1.5874 cell-count^(1/3), the conventional 3D Roache ratio on 4x cells": 4.0 ** (1.0 / 3.0),
    "r=4.000  the raw surface-face and cell-count ratio": 4.0,
}


# --------------------------------------------------------------------------------------
# SECTION 8.6 -- RULE 4, STRICT, ALL-OR-NOTHING.  The comparator REFUSES rather than degrade
# on any failed clause.
# --------------------------------------------------------------------------------------
RULE4_FIELDS = ("U", "p", "T", "rho", "nut", "k", "omega", "alphat")


def completion_clauses(case_dir, end_time):
    """Every clause of Section 8.6, evaluated; the comparator refuses on any failure."""
    log = os.path.join(case_dir, "log.rhoSimpleFoam")
    rcf = os.path.join(case_dir, "SOLVER_RC.txt")
    clauses = {}

    rc = None
    if os.path.exists(rcf):
        try:
            rc = int(open(rcf).read().split()[0])
        except (ValueError, IndexError):
            rc = None
    clauses["rc_zero"] = (rc == 0)
    clauses["rc_read_from_SOLVER_RC_not_around_setsid"] = os.path.exists(rcf)

    text = open(log, errors="replace").read() if os.path.exists(log) else ""
    clauses["End_line"] = bool(re.search(r"^End\s*$", text, re.M))
    times = [float(m.group(1)) for m in re.finditer(r"^Time = " + _NUM, text, re.M)]
    clauses["last_time_equals_endTime"] = bool(times) and abs(times[-1] - end_time) < 1e-9
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    clauses["ExecutionTime_count_equals_endTime"] = (n_exec == int(end_time))

    et = os.path.join(case_dir, str(int(end_time)))
    present = []
    for f in RULE4_FIELDS:
        present.append(os.path.exists(os.path.join(et, f))
                       or os.path.exists(os.path.join(et, f + ".gz")))
    clauses["fields_present_at_endTime"] = all(present)
    clauses["fields_missing"] = [f for f, ok in zip(RULE4_FIELDS, present) if not ok]

    # THE AGE GUARD.  0/U is touched last at launch and so DATES the run that was allowed
    # to produce the answer.  Every field at endTime must be NEWER than the case's own 0/U.
    zero_u = os.path.join(case_dir, "0", "U")
    if os.path.exists(zero_u):
        t0 = os.path.getmtime(zero_u)
        newer = []
        for f in RULE4_FIELDS:
            for cand in (os.path.join(et, f), os.path.join(et, f + ".gz")):
                if os.path.exists(cand):
                    newer.append(os.path.getmtime(cand) > t0)
                    break
        clauses["age_guard_every_field_newer_than_0_over_U"] = bool(newer) and all(newer)
    else:
        clauses["age_guard_every_field_newer_than_0_over_U"] = False

    clauses["ALL"] = all(v for k, v in clauses.items()
                         if isinstance(v, bool) and k != "ALL")
    return clauses


# --------------------------------------------------------------------------------------
# GATES
# --------------------------------------------------------------------------------------
def gate_a(levels):
    """Gate A, Section 5.  levels: ordered [L3, L2, L1] dicts with polymesh/checkmesh/surface.

    A5's mechanics: the hash is on the DECOMPRESSED stream.  A5 FAILS OPEN if this is got
    wrong, which is why control C5 plants a single node perturbation and asserts the hash
    moves, and C6 feeds two byte-identical points files and requires NOT A RESULT.
    """
    out = {"checks": {}, "per_level": []}
    cms, hashes, cellcounts, wingfaces = [], [], [], []
    for lv in levels:
        cm = read_checkmesh(lv["checkmesh"]) if lv.get("checkmesh") else {"state": "ABSENT"}
        cms.append(cm)
        h = points_stream_sha(lv["polymesh"]) if lv.get("polymesh") else None
        hashes.append(h)
        bnd = read_boundary(lv["polymesh"]) if lv.get("polymesh") else []
        wall = [b for b in bnd if b["type"] == "wall"]
        wf = wall[0]["nFaces"] if len(wall) == 1 else None
        wingfaces.append(wf)
        cellcounts.append(lv.get("cells"))
        out["per_level"].append({
            "id": lv["id"], "checkMesh": cm, "points_stream_sha256": h,
            "wing_faces": wf, "patches": [(b["name"], b["type"], b["nFaces"]) for b in bnd],
        })

    def _fail(name, ok, label, detail):
        out["checks"][name] = {"pass": bool(ok),
                               "label": _verdict("PASS" if ok else label),
                               "detail": detail}

    # A1 / A2 / A3 -- NAMED NUMERIC MAXIMA, never a verdict string (L-459).
    no_vals = [c.get("max_non_orthogonality_deg") for c in cms]
    _fail("A1_max_non_orthogonality_le_70deg",
          all(v is not None and v <= A1_MAX_NON_ORTHOGONALITY_DEG for v in no_vals),
          "GATE FAIL",
          {"values_deg": no_vals, "threshold_deg": A1_MAX_NON_ORTHOGONALITY_DEG,
           "non_blocking": True,
           "note": "An ABSENT checkMesh log reads ABSENT. It NEVER reads clean."})
    sk_vals = [c.get("max_skewness") for c in cms]
    _fail("A2_max_skewness_le_4",
          all(v is not None and v <= A2_MAX_SKEWNESS for v in sk_vals),
          "GATE FAIL", {"values": sk_vals, "threshold": A2_MAX_SKEWNESS,
                        "non_blocking": True})
    ar_vals = [c.get("max_aspect_ratio") for c in cms]
    out["checks"]["A3_max_aspect_ratio_ADVISORY"] = {
        "pass": None, "label": "advisory only",
        "detail": {"values": ar_vals, "advisory": A3_ASPECT_RATIO_ADVISORY,
                   "note": "ADVISORY 1000, NEVER A LONE REJECTION (Section 5)."}}

    # A4 -- cell-count ratios, both pairs, EXACTLY 4.000 on integers.
    ok4 = (list(cellcounts) == list(A4_CELLS)
           and cellcounts[1] == cellcounts[0] * A4_RATIO_EXACT
           and cellcounts[2] == cellcounts[1] * A4_RATIO_EXACT)
    _fail("A4_cell_count_ratios_exactly_4_on_integers", ok4, "GATE FAIL",
          {"cells": cellcounts, "registered": list(A4_CELLS)})

    # A5 -- all three points-stream hashes DISTINCT.  NOT A RESULT on failure: a family
    # that is not a family is worse than no band (Section 1.4, the DPW5 measurement).
    known = [h for h in hashes if h]
    _fail("A5_points_stream_sha256_all_distinct",
          len(known) == len(levels) and len(set(known)) == len(levels),
          "NOT A RESULT",
          {"hashes": hashes,
           "mechanics": "sha256 on the DECOMPRESSED byte stream; a gzip hash also encodes "
                        "the compressor's settings and mtime, which are not the mesh.",
           "measured_hazard": "DPW5_L1T_{hex,prism,hybrid} were proved byte-identical in "
                              "constant/polyMesh/points -- one node set in three cell types."})

    # A6 -- cells / wing_faces == 64 exactly, every level.
    ratios = [(c // w) if (c and w and c % w == 0) else None
              for c, w in zip(cellcounts, wingfaces)]
    _fail("A6_cells_over_wing_faces_equals_64", all(r == A6_CELLS_PER_WING_FACE
                                                    for r in ratios),
          "GATE FAIL",
          {"ratios": ratios, "wing_faces": wingfaces,
           "meaning": "the identical-normal-direction claim is falsified if this moves"})

    # A7 -- every level's input surface sha recorded, and the 24,960 surface's hash PUBLISHED.
    surf = [lv.get("surface_sha256") for lv in levels]
    _fail("A7_surface_sha256_recorded_and_24960_published",
          all(isinstance(s, str) and len(s) == 64 for s in surf),
          "GATE FAIL", {"surface_sha256": surf})

    # A8 -- the CONDEMNED 390-face surface appears in NO level.
    _fail("A8_condemned_390_face_surface_absent",
          SHA_SURFACE_390_CONDEMNED not in [s for s in surf if s],
          "NOT A RESULT",
          {"condemned_sha256": SHA_SURFACE_390_CONDEMNED,
           "basis": "Section 1.3 -- CONDEMNED, and the MECHANISM IS NOT ESTABLISHED."})

    # A9 -- patch identity per level.  BLOCKED on failure (Section 7).
    a9 = []
    for rec in out["per_level"]:
        types = [t for _n, t, _f in rec["patches"]]
        a9.append(len(rec["patches"]) >= 3 and types.count("wall") == 1
                  and "symmetry" in types and "patch" in types)
    _fail("A9_patch_identity_wall_symmetry_patch", all(a9), "BLOCKED",
          {"per_level": [r["patches"] for r in out["per_level"]],
           "basis": "Section 7 -- 'empty' and 'wall' are NEVER acceptable for the symmetry "
                    "plane. RUNG1_M6's M0 was a closed all-wall box and a branch-killing "
                    "decision was taken off it."})

    labels = [c["label"] for c in out["checks"].values() if isinstance(c.get("pass"), bool)]
    if "NOT A RESULT" in labels:
        out["gate_A_label"] = _verdict("NOT A RESULT")
    elif "BLOCKED" in labels:
        out["gate_A_label"] = _verdict("BLOCKED")
    elif "GATE FAIL" in labels:
        out["gate_A_label"] = _verdict("GATE FAIL")
    else:
        out["gate_A_label"] = _verdict("PASS")
    return out


def gate_gf(levels, controls_fired):
    """Gate GF, Section 5.  Graded BEFORE any solve.  Cap 1.0 core-min (step B0).

    THE INSTRUMENT-REJECTION DISCIPLINE IS NOT OPTIONAL: no Gate GF number is quoted until
    C17-C20 have all fired.
    """
    need = ("C17", "C18", "C19", "C20")
    missing = [c for c in need if not controls_fired.get(c)]
    if missing:
        raise Refusal(
            f"Gate GF REFUSES to quote a number: controls {missing} have not fired. "
            "A reader that has not been rejected on something is not an instrument; it is "
            "a hope (Section 5).")

    rows, _loader = load_table_b1_1()
    per = []
    for lv in levels:
        pts, wf, wall_name = wing_patch_faces(lv["polymesh"])
        axes = mesh_axes(lv["polymesh"])
        root = root_section_nodes(pts, wf, axes)
        te = te_thickness_over_chord(root)
        dz = max_abs_dz_over_c(root, rows)
        pf = planform(pts, wf, axes)
        per.append({"id": lv["id"], "wall_patch": wall_name, "axes": axes["axis_names"],
                    "root_plane_value": axes["root_value"], "te": te, "gf2": dz,
                    "planform": pf, "n_root_nodes": len(root)})

    t_te = [p["te"]["t_te_over_c"] for p in per]
    lo = GF_AGARD_T_TE_OVER_C * (1.0 - GF1_BAND_FRACTION)
    hi = GF_AGARD_T_TE_OVER_C * (1.0 + GF1_BAND_FRACTION)
    gf1_per = ["PASS" if lo <= t <= hi else
               ("GATE FAIL" if t < GF1_SHARP_BELOW else "GATE FAIL") for t in t_te]
    gf1 = _verdict("PASS" if all(v == "PASS" for v in gf1_per) else "GATE FAIL")

    gf2_vals = [p["gf2"]["max_abs_dz_over_c"] for p in per]
    gf2 = _verdict("PASS" if all(v <= GF2_MAX_ABS_DZ_OVER_C for v in gf2_vals)
                   else "GATE FAIL")

    gf3 = _verdict("PASS" if (max(t_te) - min(t_te)) <= GF3_T_TE_IDENTICAL_TOL
                   else "GATE FAIL")

    sweeps = [p["planform"]["le_sweep_deg"] for p in per]
    span_extent = [p["planform"]["span_extent_of_wall_patch_m"] for p in per]
    span_planform = [p["planform"]["planform_semispan_from_LE_line_m"] for p in per]
    sweep_label = _verdict(
        "PASS" if all(abs(abs(s) - GF4_SWEEP_DEG) <= GF4_SWEEP_TOL_DEG for s in sweeps)
        else "GATE FAIL")

    def _span_ok(vals):
        return all(abs(v - GF4_SEMISPAN_M) / GF4_SEMISPAN_M <= GF4_SEMISPAN_TOL_FRAC
                   for v in vals)

    ok_extent, ok_planform = _span_ok(span_extent), _span_ok(span_planform)
    if ok_extent == ok_planform:
        span_label = _verdict("PASS" if ok_extent else "GATE FAIL")
        span_note = "both semispan instruments agree."
    else:
        # THE TWO INSTRUMENTS STRADDLE THE THRESHOLD.  Section 5's GF4 says "semispan of
        # each level's surface" and does not say WHICH semispan; the wing tip is a ROUNDED
        # CAP, so the wall patch's span EXTENT exceeds the PLANFORM semispan by ~1.7 %
        # against a 0.1 % tolerance.  Choosing the instrument would choose the verdict.
        # NOT A RESULT can only make a gate worse, never better (standing rule 5), so this
        # takes no gate decision.
        span_label = _verdict("NOT A RESULT")
        span_note = ("THE TWO SEMISPAN INSTRUMENTS STRADDLE THE THRESHOLD. The wing tip is "
                     "a ROUNDED CAP: the wall patch's span EXTENT is not the PLANFORM "
                     "semispan, and they differ by ~1.7 % against a 0.1 % tolerance. "
                     "Section 5's GF4 does not say which one it means. Choosing the "
                     "instrument would choose the verdict, so this limb is NOT A RESULT "
                     "and is an ADDENDUM ITEM for the supervisor.")
    gf4 = _verdict("NOT A RESULT" if span_label == "NOT A RESULT"
                   else ("PASS" if sweep_label == "PASS" and span_label == "PASS"
                         else "GATE FAIL"))

    out = {"per_level": per, "AGARD_t_TE_over_c": GF_AGARD_T_TE_OVER_C,
           "GF1": {"label": gf1, "per_level": gf1_per, "t_TE_over_c": t_te,
                   "band": [lo, hi], "sharp_below": GF1_SHARP_BELOW,
                   "band_is_a_judgement": "Section 13 item 10 -- the +/-10 % band is a "
                                          "judgement of the drafting lane, not a derived "
                                          "tolerance."},
           "GF2": {"label": gf2, "max_abs_dz_over_c": gf2_vals,
                   "threshold": GF2_MAX_ABS_DZ_OVER_C,
                   "x_window": [GF2_X_LO, GF2_X_HI]},
           "GF3": {"label": gf3, "spread": max(t_te) - min(t_te),
                   "tolerance": GF3_T_TE_IDENTICAL_TOL},
           "GF4": {"label": gf4, "sweep_limb": {"label": sweep_label, "deg": sweeps,
                                                "target_deg": GF4_SWEEP_DEG,
                                                "tolerance_deg": GF4_SWEEP_TOL_DEG},
                   "semispan_limb": {"label": span_label, "note": span_note,
                                     "wall_patch_span_extent_m": span_extent,
                                     "planform_semispan_from_LE_line_m": span_planform,
                                     "target_m": GF4_SEMISPAN_M,
                                     "tolerance_fraction": GF4_SEMISPAN_TOL_FRAC}}}

    if gf1 == "GATE FAIL":
        out["GF1_CONSEQUENCE_RULED_BEFORE_MEASUREMENT"] = {
            "ruling": ("A sharp-TE family may still run the surface-refinement sensitivity "
                       "study. Its Cp-vs-AGARD comparison must then carry the trailing-edge "
                       "geometry mismatch as a NAMED, QUANTIFIED bias -- never as an "
                       "unstated one."),
            "i": "the measured t_TE/c of every level and AGARD's 0.0014104 are printed on "
                 "EVERY Gate P figure",
            "ii": "Gate P's restriction to x/c <= 0.90 STANDS and its justification is "
                  "STRENGTHENED, not created, by this finding",
            "iii": ("certificate sentence: \"this family's trailing edge is sharp; AGARD's "
                    "is 0.14104 % chord thick; the Cp disagreement in the rear chord is at "
                    "least partly OUR GEOMETRY and is not attributed to the solver.\""),
            "NOT_ESTIMATED": "The magnitude of the resulting Cp bias is NOT estimated. "
                             "Naming a bias is honest; inventing its size would not be.",
        }
    return out


def gate_g(levels_cd, levels_logs, l3_l2_difference=None):
    """Gate G, Section 5 and 5.1, under standing rule 5's ORDERING.

    (1) any level not iteratively converged or not plateaued -> NOT A RESULT
    (2) triple DIVERGENT/STAGNANT/OSCILLATORY/EXACT -> NOT A RESULT, value and triples printed
    (3) CONVERGING -> the band is reported under Section 6's label
    The gate can only turn a PASS or GATE FAIL INTO NOT A RESULT, never the reverse.
    """
    if len(levels_cd) != 3 or len(levels_logs) != 3:
        raise Refusal("Gate G needs exactly three levels. REFUSED.")
    finals = []
    for path in levels_cd:
        s = cd_series(path)
        finals.append(s[-1][1])
    f3, f2, f1 = finals          # L3 coarse, L2 medium, L1 fine
    diff = l3_l2_difference if l3_l2_difference is not None else (f3 - f2)

    g1 = []
    for path in levels_cd:
        s = cd_series(path)
        tail = [v for t, v in s if t >= s[-1][0] - G1_TAIL_ITERATIONS]
        swing = (max(tail) - min(tail)) if len(tail) >= 2 else float("inf")
        g1.append({"path": path, "tail_iterations": G1_TAIL_ITERATIONS,
                   "CD_swing": swing, "tolerance": G1_FRACTION_OF_L3_L2 * abs(diff),
                   "pass": swing <= G1_FRACTION_OF_L3_L2 * abs(diff)})

    g2 = []
    for log, cdp in zip(levels_logs, levels_cd):
        steps, forms, _red = residual_series(log)
        g2.append(dict(gate_g2(steps, cd_series(cdp), diff), log=log,
                       print_forms_seen=forms))

    out = {"C_D": {"L3": f3, "L2": f2, "L1": f1},
           "G1": g1, "G2": g2,
           "L_HONEST": L_HONEST}

    # G3 / G4 -- both consume a refinement ratio r that the frozen registration DOES NOT
    # REGISTER.  All three defensible conventions are computed and printed; NONE is adopted.
    triples = {}
    for name, r in R_CANDIDATES.items():
        triples[name] = roache_triple(f3, f2, f1, r)
    out["G3_G4_all_candidate_ratios"] = triples

    if not (all(x["pass"] for x in g1) and all(x["pass"] for x in g2)):
        out["gate_G_label"] = _verdict("NOT A RESULT")
        out["reason"] = ("standing rule 5 clause (1): a level is not iteratively converged "
                         "or not plateaued. The value and both triples are printed beside it.")
        return out

    classes = {v["classification"] for v in triples.values()}
    if classes != {"CONVERGING"}:
        out["gate_G_label"] = _verdict("NOT A RESULT")
        out["reason"] = (f"standing rule 5 clause (2): the triple classifies as "
                         f"{sorted(classes)}. GCI is NEVER quoted when the three values are "
                         "not monotone.")
        return out

    raise Unregistered(
        "GATE G IS UNGRADEABLE AS THE DOCUMENT IS FROZEN. G3 registers a 'surface-refinement "
        "exponent p_s ... from the three-level ratio' and G4 registers 'GCI_fine on C_D at "
        "Fs = 1.25', but NO SECTION OF THE FROZEN REGISTRATION REGISTERS THE REFINEMENT "
        "RATIO r. Three defensible conventions (r = 2.000, 1.5874, 4.000) give three "
        "different p_s and three different GCI_fine, and Gate P's numerical band channel "
        "consumes GCI_fine directly. Choosing one HERE would be choosing a gate parameter "
        "AFTER the freeze -- exactly what standing rule 2 forbids. All three are printed in "
        "G3_G4_all_candidate_ratios for the supervisor. REFUSED (exit 2): this is an "
        "addendum item, and no comparator may take it.")


def set_to_set_assignment(ref, cfd_sections):
    """Section 4.5.  Experimental section curves against CFD curves, minimum RMS Cp over
    x/c <= 0.90, OPTIMAL ASSIGNMENT PRINTED IN FULL.

    THIS CHANNEL USES THE CFD AND IS THEREFORE NEVER ALLOWED TO SET THE MAPPING FOR A GRADED
    GATE.  Its force is ONE-DIRECTIONAL: it can only turn a PASS or GATE FAIL INTO NOT A
    RESULT.  It can never promote anything and it can never repair a mapping.
    """
    exp = ref["sections"]
    keys = sorted(exp)
    cost = {}
    for e in keys:
        curve_e = sorted((x, cp) for _t, x, _z, cp in exp[e]
                         if x <= P_X_OVER_C_GRADED_MAX)
        for c in sorted(cfd_sections):
            curve_c = sorted(cfd_sections[c])
            n, acc = 0, 0.0
            for x, cp in curve_e:
                v = _interp(curve_c, x)
                if v is None:
                    continue
                n += 1
                acc += (v - cp) ** 2
            cost[(e, c)] = math.sqrt(acc / n) if n else float("inf")

    # Exhaustive assignment over 7 sections (5,040 permutations) -- exact, not greedy.
    import itertools
    best, best_perm = float("inf"), None
    cfd_keys = sorted(cfd_sections)
    for perm in itertools.permutations(cfd_keys):
        tot = sum(cost[(e, c)] for e, c in zip(keys, perm))
        if tot < best:
            best, best_perm = tot, perm
    identity = tuple(cfd_keys)
    reversal = tuple(reversed(cfd_keys))
    return {
        "optimal_assignment": dict(zip([str(k) for k in keys],
                                       [str(c) for c in best_perm])),
        "total_RMS": best,
        "is_identity": best_perm == identity,
        "is_reversal": best_perm == reversal,
        "rms_matrix": {f"{e}->{c}": cost[(e, c)] for e, c in cost},
        "BINDING_DIRECTION": (
            "This channel USES THE CFD and is therefore NEVER allowed to set the mapping "
            "for a graded gate. It can only turn a PASS or GATE FAIL INTO NOT A RESULT. It "
            "can never promote anything and it can never repair a mapping (Section 4.5)."),
    }


def gci_fine_from_gate_g(g):
    """-> (value, basis).  The band Gate P's numerical channel consumes, or None.

    THIS IS NOT A CHOICE AMONG THE THREE CANDIDATE RATIOS AND MUST NEVER BECOME ONE.  It
    returns a value ONLY if every candidate agrees, and refuses to select otherwise.

    The basis is Amendment 10 item 7's own measurement: across r in {1.10, 1.5874, 2.000,
    4.000, 7.77} the GCI_fine came out IDENTICAL TO 15 SIGNIFICANT FIGURES while p_s spanned
    a factor of 21.5, because p_s is fitted from the same triple, so r**p_s is identically
    |d32/d21| and r cancels.  THERE IS ONE BAND AND THREE EXPONENTS.  If a future triple
    ever makes the candidates disagree, that identity has been broken and this returns None
    rather than picking one -- which would be choosing a gate parameter after the freeze.
    """
    triples = g.get("G3_G4_all_candidate_ratios") or {}
    vals = [t.get("GCI_fine_at_Fs_1.25") for t in triples.values()]
    named = [v for v in vals if v is not None]
    if not named or len(named) != len(vals):
        return None, ("no band: at least one candidate ratio withheld GCI_fine because the "
                      "three values are not monotone (standing rule 5 -- a GCI is NEVER "
                      "quoted on a non-monotone triple).")
    lo, hi = min(named), max(named)
    if lo == 0.0 or (hi - lo) / abs(lo) > 1.0e-12:
        return None, (f"the candidate ratios DISAGREE on GCI_fine (range [{lo!r}, {hi!r}]). "
                      "Amendment 10 item 7 measured them identical to 15 significant figures "
                      "because r cancels; a disagreement means that identity no longer "
                      "holds. Selecting one here would be choosing a gate parameter after "
                      "the freeze (standing rule 2). NO BAND is returned.")
    return named[0], (
        f"the {len(named)} candidate refinement ratios agree on GCI_fine to within 1e-12 "
        "relative, as Amendment 10 item 7 measured: r cancels identically because p_s is "
        "fitted from the same triple. ONE BAND, THREE EXPONENTS. Nothing is selected here.")


def gate_p(ref, cfd_sections, d1, gci_fine, gate_g_label):
    """Gate P, Section 5.  SANAA'S DELIVERABLE -- and Section 12 item 3 says it is NOT
    delivered by this registration.  Cp at the seven published sections against the 271
    tapped values, under A-MAP as adjudicated by D1 and constrained by Section 4.5.
    """
    if gate_g_label != "PASS":
        # Gate P sits BEHIND Gate G.  A PASS on a family that is not CONVERGING is NOT A
        # RESULT.
        pass

    channel = set_to_set_assignment(ref, cfd_sections)
    per_station = _verdict("PASS")
    reasons = []

    if gate_g_label == "NOT A RESULT":
        per_station = _verdict("NOT A RESULT")
        reasons.append("Gate P sits BEHIND Gate G: a PASS on a family that is not "
                       "CONVERGING is NOT A RESULT.")
    if d1["verdict"] == "INDETERMINATE":
        per_station = _verdict("NOT A RESULT")
        reasons.append("D1 is INDETERMINATE: Gate P's PER-STATION channel is NOT A RESULT "
                       "and Section 4.5's channel is the only Gate P output.")
    if d1["verdict"] == "CORROBORATED" and not channel["is_identity"]:
        per_station = _verdict("NOT A RESULT")
        reasons.append("D1 CORROBORATED but the set-to-set optimal assignment is NOT the "
                       "identity (Section 4.5).")
    if d1["verdict"] == "FALSIFIED" and not channel["is_reversal"]:
        per_station = _verdict("NOT A RESULT")
        reasons.append("D1 FALSIFIED but the set-to-set optimal assignment is NOT the "
                       "reversal (Section 4.5).")

    return {
        "graded_window": f"x/c <= {P_X_OVER_C_GRADED_MAX}",
        "rear_chord": "the rear 10 % is PLOTTED and REPORTED, NEVER GRADED",
        "A_MAP": {"mapping": list(A_MAP_YB),
                  "status": "ASSUMED. Not measured. Not confirmed by any artifact this lab "
                            "holds (Section 4.1)."},
        "D1": d1,
        "order_independent_channel": channel,
        "band_channels": {
            # TRUTHFULNESS REPAIR, and it moves no threshold: when Gate G yields no band,
            # `gci_fine` is None and the old unconditional word "measured" would have
            # annotated an ABSENCE as a measurement -- worse than a discrepancy never
            # computed.  The VALUE and the BAND are untouched.
            "numerical_mesh": {
                "value": gci_fine,
                "status": ("measured -- but a LOWER BOUND, not the total (Section 6)"
                           if gci_fine is not None else
                           "NOT AVAILABLE -- Gate G yielded no band, so there is no "
                           "numerical channel to put in Gate P's band. NOT a zero.")},
            "reference_accuracy": {"value": P_REFERENCE_ACCURACY_DCP,
                                   "status": "published, AR-138 B1-4 Section 6.1"},
            "read_off": {"value": 0.0,
                         "status": "ZERO -- machine-readable at a pinned hash"},
        },
        "systematics_DISCLOSED_and_deliberately_NOT_in_the_band": [
            "AR-138 B1-4 Section 6.2 records 'Wall interference corrections: no corrections' "
            "at a semispan-to-tunnel-width ratio of 0.7, and the report declines to quantify "
            "it.",
            "AGARD's design trailing edge is 0.14104 % chord thick while the geometry here "
            "is sharp -- hence the x/c <= 0.90 grading window.",
        ],
        "per_station_channel_label": per_station,
        "per_station_reasons": reasons,
        "L_HONEST": L_HONEST,
    }


def gate_r():
    """Gate R, Section 5.  Route A as a grid family.  GATE FAIL, not PENDING."""
    return {
        "label": _verdict("GATE FAIL"),
        "threshold": "MESH_STANDARD.md Section 9.1's three-level requirement",
        "measured": "one level (A-F1); overset topology (A-F2)",
        "why_not_PENDING": ("PENDING would say 'not yet run' and would be a softened GATE "
                            "FAIL -- the exact misuse standing rule 1 forbids. The route was "
                            "run, it was measured, and it failed on STRUCTURE."),
        "cap": "n/a -- the route is closed, not run",
    }


# --------------------------------------------------------------------------------------
# SECTION 10 -- PLANTED CONTROLS.  Rule 3, on EVERY zero this ladder can report.
#
# Every control plants into a SCRATCH COPY, reads it back FROM DISK, and the comparator
# REFUSES if the reader cannot see it.  A PASS reported by a reader whose plant did not
# fire is NOT A RESULT, not a pass.
# --------------------------------------------------------------------------------------
_CM_EQ_FORM = """\
Checking geometry...
    Overall domain bounding box (0 0 0) (1 1 1)
    Boundary openness (2.99162e-17 4.31794e-16 -8.22572e-16) OK.
    Max cell openness = 3.01583e-15 OK.
    Max aspect ratio = 608.207 OK.
    Min volume = 1.17547e-10. Max volume = 0.944185.  Total volume = 3132.13.  Cell volumes OK.
    Mesh non-orthogonality Max: 61.4938 average: 13.697
    Non-orthogonality check OK.
    Max skewness = 2.30655 OK.
    Number of regions: 1 (OK).
Failed 2 mesh checks.
"""

_CM_COLON_FORM = """\
Checking geometry...
    Boundary openness (1.0e-18 2.0e-18 3.0e-18) OK.
    Max aspect ratio: 222.355 OK.
    Min volume: 5.0e-11. Max volume: 0.5.  Cell volumes OK.
    Mesh non-orthogonality Max: 61.1581 average: 11.2
    Non-orthogonality check OK.
    Max skewness: 1.44081 OK.
    Number of regions: 1 (OK).
"""


def _write(path, text):
    with open(path, "w") as fh:
        fh.write(text)
    return path


def _synthetic_residual_log(form, series, fields=("Ux", "p", "k")):
    """Build a solver log carrying a chosen max-over-equations series.

    MEASURED TRAP (control C7): a real DAFoam log contains ZERO occurrences of the string
    'Initial residual'.  Both circulating print forms are therefore synthesised here.
    """
    out = []
    for i, v in enumerate(series, start=1):
        out.append(f"Time = {i}\n")
        for j, f in enumerate(fields):
            val = v if j == 0 else v * 0.1
            if form == "stock":
                out.append(f"smoothSolver:  Solving for {f}, Initial residual = {val:.6e}, "
                           f"Final residual = {val*1e-3:.6e}, No Iterations 3\n")
            else:
                # The DAFoam print form, as the registered reducer's own RE_SOLVE_B
                # matches it.  MEASURED TRAP: a real DAFoam log contains ZERO occurrences
                # of the string 'Initial residual', so a reader built only for the stock
                # form reports a silent zero on it.
                out.append(f"    {f} initRes: {val:.6e}  finalRes: {val*1e-3:.6e}\n")
        out.append("ExecutionTime = 1.0 s  ClockTime = 1 s\n\n")
    return "".join(out)


def _synthetic_forcecoeffs(series):
    out = ["# Force coefficients\n", "# Time Cd Cl Cm\n"]
    for i, v in enumerate(series, start=1):
        out.append(f"{i} {v:.9e} 0.25 -0.02\n")
    return "".join(out)


def controls(scratch, mutate=None):
    """Run C1..C20 and C16.  -> (fired: {id: bool}, detail: {id: str}).

    `mutate` is THE MUTATION CONTROL.  It names a shipped statistic to corrupt; the suite
    must go RED.  A control suite that cannot fail is not a control suite.
    """
    fired, detail = {}, {}
    os.makedirs(scratch, exist_ok=True)

    def _rec(cid, ok, msg):
        fired[cid] = bool(ok)
        detail[cid] = msg

    # ---- C1: both label forms, a non-null max aspect ratio from EACH ------------------
    p_eq = _write(os.path.join(scratch, "c1_eq.checkMesh"), _CM_EQ_FORM)
    p_co = _write(os.path.join(scratch, "c1_colon.checkMesh"), _CM_COLON_FORM)
    a_eq = read_checkmesh(p_eq)["max_aspect_ratio"]
    a_co = read_checkmesh(p_co)["max_aspect_ratio"]
    if mutate == "C1":
        a_co = None
    _rec("C1", a_eq is not None and a_co is not None,
         f"= form -> {a_eq}; : form -> {a_co}")

    # ---- C2: Min volume != Max volume -> a NON-TRIVIAL ratio, NEVER 1 ----------------
    r_eq = read_checkmesh(p_eq)["cell_volume_ratio"]
    if mutate == "C2":
        r_eq = 1.0
    _rec("C2", r_eq is not None and abs(r_eq - 1.0) > 1e-9,
         f"derived cell-volume ratio = {r_eq}")

    # ---- C3: replace one log's non-orthogonality maximum with a KNOWN value ----------
    planted = _CM_EQ_FORM.replace("Max: 61.4938", f"Max: {PLANT_NON_ORTH_DEG}")
    p_c3 = _write(os.path.join(scratch, "c3_planted.checkMesh"), planted)
    got = read_checkmesh(p_c3)["max_non_orthogonality_deg"]     # READ BACK FROM DISK
    if mutate == "C3":
        got = 61.4938
    _rec("C3", got is not None and abs(got - PLANT_NON_ORTH_DEG) < 1e-9,
         f"planted {PLANT_NON_ORTH_DEG} deg, read back {got}")

    # ---- C4: 'Non-orthogonality check OK.' beside a maximum ABOVE 70 deg -> GATE FAIL -
    cm4 = read_checkmesh(p_c3)
    verdict_string_says_ok = cm4["verdict_strings_present_and_IGNORED"][
        "non_orthogonality_check_OK"]
    number = cm4["max_non_orthogonality_deg"]
    gate_fail = number is not None and number > A1_MAX_NON_ORTHOGONALITY_DEG
    if mutate == "C4":
        gate_fail = False
    _rec("C4", verdict_string_says_ok and gate_fail,
         f"log says 'Non-orthogonality check OK.' at {number} deg; reader returns "
         f"{'GATE FAIL' if gate_fail else 'PASS'} -- it reads the NUMBER, not the string "
         "(L-459)")

    # ---- C5: perturb ONE node of a decompressed points file -> THE HASH MOVES --------
    src = "/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/constant/polyMesh"
    d5 = os.path.join(scratch, "c5_polyMesh")
    ok5 = False
    h_before = h_after = None
    if os.path.isdir(src):
        os.makedirs(d5, exist_ok=True)
        raw = gzip.open(os.path.join(src, "points.gz"), "rb").read()
        _write(os.path.join(d5, "points"), raw.decode("utf-8", "replace"))
        h_before = points_stream_sha(d5)
        text = open(os.path.join(d5, "points")).read()
        m = re.search(r"\(\s*" + _NUM + r"\s+" + _NUM + r"\s+" + _NUM + r"\s*\)", text)
        if m:
            new = f"({float(m.group(1)) + 1.0e-06:.9g} {m.group(2)} {m.group(3)})"
            _write(os.path.join(d5, "points"), text[:m.start()] + new + text[m.end():])
            h_after = points_stream_sha(d5)          # READ BACK FROM DISK
            ok5 = h_before != h_after
    if mutate == "C5":
        ok5 = False
    _rec("C5", ok5, f"one node perturbed by 1e-06 m: {h_before} -> {h_after}")

    # ---- C6: two BYTE-IDENTICAL points files -> NOT A RESULT on A5 -------------------
    d6a = os.path.join(scratch, "c6_a")
    d6b = os.path.join(scratch, "c6_b")
    for d in (d6a, d6b):
        os.makedirs(d, exist_ok=True)
        _write(os.path.join(d, "points"), "(\n(0 0 0)\n(1 0 0)\n(0 1 0)\n)\n")
    same = points_stream_sha(d6a) == points_stream_sha(d6b)
    a5_would_fail = same                     # A5 requires all DISTINCT
    if mutate == "C6":
        a5_would_fail = False
    _rec("C6", a5_would_fail,
         "two byte-identical points files -> A5 reports NOT A RESULT; a reader that cannot "
         "FAIL A5 is a fail-open wearing a pass (the measured DPW5 shape, Section 1.4)")

    # ---- C7: stock OpenFOAM print form and DAFoam print form -> SAME reduction --------
    ser = [10.0 ** (-e) for e in range(1, 9)]
    p7a = _write(os.path.join(scratch, "c7_stock.log"),
                 _synthetic_residual_log("stock", ser))
    p7b = _write(os.path.join(scratch, "c7_dafoam.log"),
                 _synthetic_residual_log("dafoam", ser))
    try:
        s7a, f7a, _ = residual_series(p7a)
        s7b, f7b, _ = residual_series(p7b)
        red_a = math.log10(s7a[0]["max_initial_residual"] / s7a[-1]["max_initial_residual"])
        red_b = math.log10(s7b[0]["max_initial_residual"] / s7b[-1]["max_initial_residual"])
        ok7 = abs(red_a - red_b) < 1e-9
    except Refusal as exc:
        red_a = red_b = None
        ok7 = False
        detail["C7_refusal"] = str(exc)
    dafoam_has_initial_residual = "Initial residual" in open(p7b).read()
    if mutate == "C7":
        ok7 = False
    _rec("C7", ok7 and not dafoam_has_initial_residual,
         f"stock {red_a} orders, DAFoam-form {red_b} orders; the DAFoam-form log contains "
         f"{'a' if dafoam_has_initial_residual else 'ZERO'} occurrence(s) of 'Initial "
         "residual' -- the measured trap")

    # ---- C8: a falling, a rising and a flat series -> ALL THREE CLASSES REACHABLE -----
    classes = set()
    for name, s in (("falling", [10.0 ** (-e) for e in range(1, 9)]),
                    ("rising", [10.0 ** (e - 9) for e in range(1, 9)]),
                    ("flat", [1.0e-4] * 8)):
        p = _write(os.path.join(scratch, f"c8_{name}.log"),
                   _synthetic_residual_log("stock", s))
        st, _f, _r = residual_series(p)
        v = [x["max_initial_residual"] for x in st]
        if v[-1] < v[0] * 0.5:
            classes.add("FALLING")
        elif v[-1] > v[0] * 2.0:
            classes.add("RISING")
        else:
            classes.add("FLAT")
    if mutate == "C8":
        classes = {"FALLING"}
    _rec("C8", classes == {"FALLING", "RISING", "FLAT"},
         f"classes reachable: {sorted(classes)} -- a classifier that can only say one thing "
         "is not evidence for the thing it says")

    # ---- C9: the max MOVES BETWEEN FIELDS between two steps ---------------------------
    log9 = ("Time = 1\n"
            "smoothSolver:  Solving for Ux, Initial residual = 1.0e-02, Final residual = 1e-5, No Iterations 3\n"
            "smoothSolver:  Solving for p, Initial residual = 1.0e-04, Final residual = 1e-7, No Iterations 3\n"
            "ExecutionTime = 1 s\n\n"
            "Time = 2\n"
            "smoothSolver:  Solving for Ux, Initial residual = 1.0e-06, Final residual = 1e-9, No Iterations 3\n"
            "smoothSolver:  Solving for p, Initial residual = 1.0e-03, Final residual = 1e-6, No Iterations 3\n"
            "ExecutionTime = 2 s\n\n")
    p9 = _write(os.path.join(scratch, "c9_move.log"), log9)
    s9, _f9, _r9 = residual_series(p9)
    carried = [x["carried_by"] for x in s9]
    ok9 = len(set(carried)) > 1
    if mutate == "C9":
        ok9 = False
    _rec("C9", ok9, f"max carried by {carried} -- it MOVES between fields")

    # ---- C10: perturb ONE tap's CP in a SCRATCH COPY of case_2308.dat ----------------
    src10 = os.path.join(REPO, PATH_CASE_2308)
    ok10 = False
    delta_seen = None
    if os.path.exists(src10):
        p10 = os.path.join(scratch, "c10_case_2308.dat")
        shutil.copyfile(src10, p10)
        base = read_case_2308(p10, verify_hash=False)
        lines = open(p10, errors="replace").read().split("\n")
        for i, ln in enumerate(lines):
            f = ln.split()
            if len(f) == 5:
                try:
                    v = [float(x) for x in f]
                except ValueError:
                    continue
                v[4] += PLANT_CP
                lines[i] = "  " + "  ".join(f"{x:.8E}" for x in v)
                break
        _write(p10, "\n".join(lines))
        after = read_case_2308(p10, verify_hash=False)   # READ BACK FROM DISK
        b = base["sections"][1][0][3]
        a = after["sections"][1][0][3]
        delta_seen = a - b
        ok10 = abs(delta_seen - PLANT_CP) < 1e-9
    if mutate == "C10":
        ok10 = False
    _rec("C10", ok10, f"planted {PLANT_CP} on one tap's CP; deviation moved by {delta_seen}")

    # ---- C11: corrupt the reference file's sha256 -> REFUSAL, not a silent fallback ---
    ok11 = False
    if os.path.exists(src10):
        p11 = os.path.join(scratch, "c11_corrupt.dat")
        shutil.copyfile(src10, p11)
        with open(p11, "a") as fh:
            fh.write("\n# corruption planted by control C11\n")
        try:
            require_sha(p11, SHA_CASE_2308, "control C11")
        except Refusal:
            ok11 = True
    if mutate == "C11":
        ok11 = False
    _rec("C11", ok11, "a corrupted reference produces a REFUSAL, never a silent fallback")

    # ---- C12: a scratch reference whose seven sections are REVERSED -> FALSIFIED ------
    ok12 = ok13 = False
    v12 = v13 = None
    if os.path.exists(src10):
        real = read_case_2308(src10, verify_hash=False)
        rev = {"sections": {i + 1: real["sections"][7 - i]
                            for i in range(len(real["sections"]))},
               "titles": real["titles"], "n_sections": real["n_sections"],
               "n_taps_total": real["n_taps_total"]}
        v12 = d1_discriminator(rev)["verdict"]
        # C12 IS IMPLEMENTED TO THE LETTER OF SECTION 10, WHICH REGISTERS ITS MUST-SEE AS
        # "FALSIFIED".  It is NOT loosened to the control's purpose clause.  Loosening a
        # registered control so that it passes is how a fail-open gets a green tick.
        ok12 = (v12 == "FALSIFIED")
        base_v = d1_discriminator(real)["verdict"]
        detail["C12_as_read_verdict"] = base_v
        # ---- C13: all seven sections carrying the SAME CP block -> INDETERMINATE -----
        same = {"sections": {i + 1: list(real["sections"][1])
                             for i in range(len(real["sections"]))},
                "titles": real["titles"], "n_sections": real["n_sections"],
                "n_taps_total": real["n_taps_total"]}
        v13 = d1_discriminator(same)["verdict"]
        ok13 = (v13 == "INDETERMINATE")
    if mutate == "C12":
        ok12 = False
    if mutate == "C13":
        ok13 = False
    _rec("C12", ok12,
         f"as-read reference -> D1 returns {detail.get('C12_as_read_verdict')}; reversed "
         f"reference -> D1 returns {v12}. Section 10 registers C12's MUST-SEE as FALSIFIED. "
         "Reversing a NON-MONOTONE Cn series leaves it non-monotone, so when the as-read "
         "data is INDETERMINATE this control CANNOT fire as written. Reported, NOT loosened.")
    _rec("C13", ok13, f"seven identical sections -> D1 returns {v13}: the third branch is "
                      "REACHABLE")

    # ---- C14: perturb C_D in a scratch postProcessing file -> the deviation moves -----
    p14 = _write(os.path.join(scratch, "c14_coeffs.dat"),
                 _synthetic_forcecoeffs([0.01] * 10))
    before14 = cd_series(p14)[-1][1]
    _write(p14, _synthetic_forcecoeffs([0.01] * 9 + [0.01 + PLANT_CD]))
    after14 = cd_series(p14)[-1][1]           # READ BACK FROM DISK
    ok14 = abs((after14 - before14) - PLANT_CD) < 1e-12
    if mutate == "C14":
        ok14 = False
    _rec("C14", ok14, f"planted {PLANT_CD} on C_D; read back a move of {after14 - before14}")

    # ---- C15: a triple whose cell counts are NOT exactly 4:4 -> GATE FAIL on A4 -------
    bad = (99840, 399361, 1597440)
    ok15 = not (bad[1] == bad[0] * 4 and bad[2] == bad[1] * 4)
    if mutate == "C15":
        ok15 = False
    _rec("C15", ok15, f"cell triple {bad} -> A4 GATE FAIL (off by one cell)")

    # ---- C17: split the root TE node by 2.000e-04 m -> a NON-ZERO t_TE/c on 2 nodes ---
    ok17 = False
    t_before = t_after = n_after = None
    root_src = None
    for cand in ("/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/constant/polyMesh",
                 "/home/ubuntu/certonomous-runs/.mesh-cache/onera_m6/polyMesh"):
        if os.path.isdir(cand):
            root_src = cand
            break
    if root_src:
        pts, wf, _ = wing_patch_faces(root_src)
        _axes = mesh_axes(root_src)
        root = root_section_nodes(pts, wf, _axes)
        t_before = te_thickness_over_chord(root)["t_te_over_c"]
        # plant into a SCRATCH COPY of the node list, write it, and read it BACK FROM DISK
        p17 = os.path.join(scratch, "c17_root_section.txt")
        xs = [p[0] for p in root]
        x_hi, chord = max(xs), max(xs) - min(xs)
        planted_rows = []
        split_done = False
        for x, y, z in root:
            if (x_hi - x) <= 1.0e-06 * chord and not split_done:
                planted_rows.append((x, y, z + PLANT_TE_SPLIT_M / 2.0))
                planted_rows.append((x, y, z - PLANT_TE_SPLIT_M / 2.0))
                split_done = True
            else:
                planted_rows.append((x, y, z))
        _write(p17, "\n".join(f"{a!r} {b!r} {c!r}" for a, b, c in planted_rows))
        back = [tuple(float(v) for v in ln.split())
                for ln in open(p17).read().split("\n") if ln.strip()]
        m17 = te_thickness_over_chord(back)
        t_after, n_after = m17["t_te_over_c"], m17["n_te_nodes"]
        ok17 = (t_after > 0.0 and n_after >= 2
                and abs(m17["t_te_m"] - PLANT_TE_SPLIT_M) < 1.0e-09)
    if mutate == "C17":
        ok17 = False
    _rec("C17", ok17,
         f"as-read t_TE/c = {t_before}; with a {PLANT_TE_SPLIT_M} m split planted and read "
         f"back from disk, t_TE/c = {t_after} on {n_after} nodes. A t_TE/c = 0 from a reader "
         "not shown able to report a non-zero is NOT evidence of a sharp trailing edge.")

    # ---- C18: +5.000e-04 c on EVERY reference ordinate -> max|dz|/c moves by the plant -
    ok18 = False
    d_before = d_after = None
    if root_src:
        try:
            rows, _ = load_table_b1_1()
            pts, wf, _ = wing_patch_faces(root_src)
            root = root_section_nodes(pts, wf, mesh_axes(root_src))
            d_before = max_abs_dz_over_c(root, rows)["max_abs_dz_over_c"]
            p18 = os.path.join(scratch, "c18_planted_reference.dat")
            _write(p18, "\n".join(f"{x!r} {z + PLANT_DZ_OVER_C!r}" for x, z in rows))
            planted = [tuple(float(v) for v in ln.split())
                       for ln in open(p18).read().split("\n") if ln.strip()]
            d_after = max_abs_dz_over_c(root, planted)["max_abs_dz_over_c"]
            ok18 = abs(d_after - d_before) > 0.5 * PLANT_DZ_OVER_C
        except Refusal as exc:
            detail["C18_refusal"] = str(exc)
    if mutate == "C18":
        ok18 = False
    _rec("C18", ok18,
         f"as-read max|dz|/c = {d_before}; with +{PLANT_DZ_OVER_C} c planted on every "
         f"reference ordinate and read back from disk, {d_after}")

    # ---- C19: THREE fixtures, not one.  BOTH LIMBS must fire. ------------------------
    fixtures = {
        "a_om6_wing_section_sharp": os.path.join(
            REPO, "verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat"),
        "b_nasa_foilmod_SHARPENED": os.path.join(
            REPO, "models/onera_m6/quarantine/nasa_foilmod_SHARPENED_NOT_TABLE_B1_1.dat"),
        "c_true_table_with_planted_final_ordinate": os.path.join(
            REPO, PATH_TABLE_B1_1),
    }
    rcs = {}
    script = os.path.join(REPO, "scripts", "verify_agard_ar138_table_b1_1.py")
    for name, path in fixtures.items():
        if not os.path.exists(path):
            rcs[name] = None
            continue
        rcs[name] = subprocess.run([sys.executable, script, path],
                                   capture_output=True, text=True).returncode
    ok19 = (rcs.get("a_om6_wing_section_sharp") == 2
            and rcs.get("b_nasa_foilmod_SHARPENED") == 2
            and rcs.get("c_true_table_with_planted_final_ordinate") == 0)
    if mutate == "C19":
        ok19 = False
    _rec("C19", ok19,
         f"rc: (a) {rcs.get('a_om6_wing_section_sharp')}  (b) "
         f"{rcs.get('b_nasa_foilmod_SHARPENED')}  (c) "
         f"{rcs.get('c_true_table_with_planted_final_ordinate')}. Contract: REFUSAL (exit 2) "
         "on (a) and (b), ACCEPTANCE of (c). A control tuned only to the zero final ordinate "
         "PASSES fixture (a) straight through.")

    # ---- C19b: THE COUNT-HEADER SHAPE, named so the defect cannot return silently -----
    # Fixture (a) is a single-column file whose first content line is the count '63'.  The
    # two-column parser therefore returns ZERO rows, and an earlier form of the loader
    # indexed rows[-1] in its plant block and died with IndexError and rc=1.  A CRASH IS
    # NOT A REFUSAL.  This control fires on that exact shape.
    p19b = _write(os.path.join(scratch, "c19b_count_header.dat"),
                  "\n63\n\n" + "\n".join(f"{i * 0.01:.7f}" for i in range(126)) + "\n")
    rc19b = subprocess.run([sys.executable, script, p19b],
                           capture_output=True, text=True).returncode
    ok19b = (rc19b == 2)
    if mutate == "C19b":
        ok19b = False
    _rec("C19b", ok19b,
         f"a synthetic count-header lookalike yielding ZERO two-column rows -> rc={rc19b}. "
         "The contract is REFUSE (exit 2) rather than degrade; rc=1 with a traceback is "
         "neither.")

    # ---- C20: the straight leading edge, whose answer is known INDEPENDENTLY ----------
    ok20 = False
    resid = sweep_real = r_synth = r_bulge = None
    if root_src:
        pts, wf, _ = wing_patch_faces(root_src)
        real = planform(pts, wf, mesh_axes(root_src))
        resid = real["le_straightness_residual_m"]
        sweep_real = real["le_sweep_deg"]

        # LIMB 1 -- the straight leading edge, whose answer is KNOWN INDEPENDENTLY:
        # a residual at machine epsilon.  A reader that cannot return it is REJECTED.
        ys = [i * 0.01 for i in range(120)]
        synth = [(0.5 * y, y, 0.0) for y in ys] + [(1.0 + 0.5 * y, y, 0.0) for y in ys]
        p20 = _write(os.path.join(scratch, "c20_straight.txt"),
                     "\n".join(f"{a!r} {b!r} {c!r}" for a, b, c in synth))
        back = [tuple(float(v) for v in ln.split())
                for ln in open(p20).read().split("\n") if ln.strip()]
        r_synth = planform(back, [tuple(range(len(back)))])["le_straightness_residual_m"]

        # LIMB 2 -- a planted FORWARD BULGE on the same edge.  The reader must SEE it.
        # A residual of zero from a reader never shown able to report a non-zero is not
        # evidence that a leading edge is straight.
        bulged = list(synth)
        mid = len(ys) // 2
        bulged[mid] = (bulged[mid][0] - PLANT_TE_SPLIT_M, bulged[mid][1], bulged[mid][2])
        p20b = _write(os.path.join(scratch, "c20_bulged.txt"),
                      "\n".join(f"{a!r} {b!r} {c!r}" for a, b, c in bulged))
        backb = [tuple(float(v) for v in ln.split())
                 for ln in open(p20b).read().split("\n") if ln.strip()]
        r_bulge = planform(backb, [tuple(range(len(backb)))])["le_straightness_residual_m"]
        ok20 = (r_synth < 1.0e-12) and (r_bulge > 1.0e-12)
    if mutate == "C20":
        ok20 = False
    _rec("C20", ok20,
         f"LIMB 1 known-straight synthetic edge -> residual {r_synth} (must be machine "
         f"epsilon); LIMB 2 the same edge with a {PLANT_TE_SPLIT_M} m forward bulge planted "
         f"and read back from disk -> residual {r_bulge} (must be non-zero). READING on the "
         f"level's own surface: residual {resid} m at sweep {sweep_real} deg. Two readers "
         "were rejected on exactly this (5.27e-01 m and 1.236e-02 m) before a third was "
         "quoted; this lane rejected two more (per-station min-chord, and binned "
         "least-squares) before adopting the convex hull.")

    # ---- C21: PLANT A KNOWN PRESSURE ON THE SAMPLED WING SURFACE AND READ THE Cp BACK ----
    # Rule 3 on Gate P's CFD channel, which had no reader at all until this producer existed
    # (Amendment 10 item 5).  A Cp curve from a reader not shown able to see a KNOWN pressure
    # offset is not evidence.  The surface is written to disk and read back FROM DISK.
    d21 = os.path.join(scratch, "c21_surface")
    _synthetic_sampled_surface(d21)
    stns21 = registered_stations()
    base21, meta21 = cfd_sections_from_surface(d21, 2, 0, stations=stns21)
    planted21, _m = cfd_sections_from_surface(d21, 2, 0, stations=stns21,
                                              plant_pa=PLANT_SAMPLED_P_PA)
    expect = PLANT_SAMPLED_P_PA / q_inf_pa()
    worst = 0.0
    for s in base21:
        for (x0, c0), (x1, c1) in zip(base21[s], planted21[s]):
            worst = max(worst, abs((c1 - c0) - expect), abs(x1 - x0))
    if mutate == "C21":
        worst = 1.0
    _rec("C21", worst < 1.0e-9 and len(base21) == len(A_MAP_YB),
         f"planted {PLANT_SAMPLED_P_PA} Pa on a sampled wing surface written to disk; all "
         f"{len(base21)} registered stations moved by exactly {expect!r} in Cp (worst "
         f"deviation {worst!r}); local chords "
         f"{[round(st['local_chord_m'], 6) for st in meta21['stations']]}")

    # ---- C22: A STATION OUTSIDE THE SAMPLED SPAN MUST REFUSE, NEVER RETURN AN EMPTY CURVE -
    # An empty Cp curve would compare as a PERFECT ABSENCE rather than as a disagreement,
    # which is the same class of false zero rule 3 exists for.
    off = registered_stations()[:1] + [{"index": 99, "y_over_b": 4.18,
                                        "span_coord_m": 5.0}]
    try:
        cfd_sections_from_surface(d21, 2, 0, stations=off)
        ok22, msg22 = False, "a station outside the sampled span did NOT refuse"
    except Refusal as exc:
        ok22 = "OUTSIDE the sampled wing surface" in str(exc)
        msg22 = f"planted a station at span 5.0 m, outside the surface's own extent; the "\
                f"reader REFUSED: {str(exc)[:180]}"
    if mutate == "C22":
        ok22 = False
    _rec("C22", ok22, msg22)

    # ---- C23: GATE P HAS AN INVOCATION PATH.  A PERMANENT, EXECUTABLE CONTROL. ------------
    # Amendment 10 item 5 was found by an AST call graph over this file and recorded that
    # "48 functions are reachable from main(). gate_p() is NOT."  That defect was invisible
    # to every other control in this suite because nothing here executed the call graph.  It
    # does now, and the CONTROL is a name that MUST read unreachable -- a reader that calls
    # everything reachable is not discriminating.
    reach = call_graph_reachable_from_main()
    must_reach = ("gate_p", "set_to_set_assignment", "cfd_sections_from_surface",
                  "gate_p_figure_data", "gate_g", "gate_r", "split_curve_upper_lower")
    missing = [n for n in must_reach if n not in reach]
    sentinel_ok = "_control_unreachable_sentinel" not in reach
    if mutate == "C23":
        missing = ["gate_p"]
    _rec("C23", not missing and sentinel_ok,
         f"AST call graph over this file: {len(reach)} functions reachable from main(); "
         f"{sorted(must_reach)} all reachable = {not missing}"
         + (f"; MISSING {missing}" if missing else "")
         + f"; the deliberately-unreachable control _control_unreachable_sentinel reads "
           f"unreachable = {sentinel_ok} (a walker that reaches everything is not a walker)")

    # ---- C24: PLANT ON THE UPPER SURFACE ALONE.  THE SPLIT MUST SEE IT THERE AND ONLY -----
    # AMENDMENT 11 RULING 3.  Rule 3 on the two curves Sanaa's figure is plotted from.  The
    # plant is ONE-SIDED on purpose: a reader that still interleaves would smear it across
    # both curves in the ratio of the tap counts, so this control DISCRIMINATES THE VERY
    # DEFECT item 21 named, rather than merely proving arithmetic works.  It runs on the
    # PINNED experimental bytes, not on a fixture.
    ref24 = read_case_2308()
    rows24 = ref24["sections"][1]
    base24 = split_curve_upper_lower([(x, z, cp) for _t, x, z, cp in rows24])
    plant24 = split_curve_upper_lower([(x, z, cp + (PLANT_CP_UPPER_ONLY if z >= 0.0 else 0.0))
                                       for _t, x, z, cp in rows24])
    d_up = max(abs((b - a) - PLANT_CP_UPPER_ONLY)
               for (_x0, a), (_x1, b) in zip(base24["upper"], plant24["upper"]))
    d_lo = max(abs(b - a) for (_x0, a), (_x1, b) in zip(base24["lower"], plant24["lower"]))
    n_ok = (base24["n_upper"] + base24["n_lower"] == len(rows24)
            and base24["n_upper"] == plant24["n_upper"])
    # The interleaved reading of the SAME plant, for the discrimination limb.
    inter_shift = (sum(cp + (PLANT_CP_UPPER_ONLY if z >= 0.0 else 0.0)
                       for _t, _x, z, cp in rows24)
                   - sum(cp for _t, _x, _z, cp in rows24)) / len(rows24)
    ok24 = (d_up < 1.0e-12 and d_lo < 1.0e-15 and n_ok
            and abs(inter_shift - PLANT_CP_UPPER_ONLY) > 1.0e-03)
    if mutate == "C24":
        ok24 = False
    _rec("C24", ok24,
         f"planted {PLANT_CP_UPPER_ONLY} in Cp on the UPPER-surface taps of section 1 only "
         f"({base24['n_upper']} upper, {base24['n_lower']} lower of {len(rows24)}): the "
         f"upper curve moved by exactly the plant (worst deviation {d_up!r}) and the lower "
         f"curve did not move at all ({d_lo!r}). The SAME plant read through the INTERLEAVED "
         f"curve shifts its mean by only {inter_shift!r} -- {inter_shift/PLANT_CP_UPPER_ONLY:.4f} "
         "of the plant, because the taps are not evenly split. A reader that still "
         "interleaved would report that smeared number, so this control discriminates.")

    return fired, detail


def _control_unreachable_sentinel():
    """C23's CONTROL.  This function is DELIBERATELY never called from anywhere.

    It exists so that C23's call-graph walk can be shown to DISCRIMINATE: a walk that
    reports every defined function as reachable proves nothing about gate_p.  If this name
    ever becomes reachable, C23's instrument is broken and C23 goes red.
    """
    return "this is never called"


def call_graph_reachable_from_main(path=None):
    """-> set of function names reachable from main() in THIS file, by AST, never by grep.

    A grep for `gate_p(` matches a docstring, a comment and a string literal; an AST walk
    matches a CALL.  Amendment 10 item 5's finding was made this way and is re-made here on
    every control run, so a future edit cannot silently orphan Sanaa's deliverable again.
    """
    import ast
    src_path = path or os.path.abspath(__file__)
    tree = ast.parse(open(src_path, errors="replace").read(), filename=src_path)
    defined, calls = set(), {}

    class _V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def _fn(self, node):
            defined.add(node.name)
            self.stack.append(node.name)
            calls.setdefault(node.name, set())
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = _fn
        visit_AsyncFunctionDef = _fn

        def visit_Call(self, node):
            f = node.func
            name = (f.id if isinstance(f, ast.Name) else
                    f.attr if isinstance(f, ast.Attribute) else None)
            if name and self.stack:
                calls[self.stack[-1]].add(name)
            self.generic_visit(node)

    _V().visit(tree)
    if "main" not in defined:
        raise InternalDefect(f"{src_path} defines no main(); the call graph has no root.")
    seen, stack = set(), ["main"]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for callee in calls.get(cur, ()):
            if callee in defined and callee not in seen:
                stack.append(callee)
    return seen


def _synthetic_sampled_surface(d, n_span=13, n_chord=21, span_max=1.25):
    """C21/C22's fixture: a `foam`-written sampled surface in the EXACT form the readers
    parse -- points, faces and scalarField/p, with POINT data as `interpolate true` gives.

    The shape is not cosmetic.  read_points()/read_faces() key on _strip_foam_header()'s
    `// * * *` separator and `<count>\\n(` list opening, and _require_count() checks the
    declared length.  A fixture in any other shape would make the control pass by not being
    read at all -- exactly the false zero rule 3 exists for.
    """
    pts, vals = [], []
    for i in range(n_span):
        z = span_max * i / (n_span - 1.0)
        for side in (+1, -1):
            for j in range(n_chord):
                x = j / (n_chord - 1.0)
                y = side * 0.06 * math.sin(math.pi * x)
                pts.append((x, y, z))
                # A pressure field that VARIES with chord, so a constant Cp offset is
                # distinguishable from the field itself.
                vals.append(P_INF_PA - 1.2e4 * math.sin(math.pi * x) * (1.0 + 0.1 * z))
    per_span = 2 * n_chord
    faces = []
    for i in range(n_span - 1):
        for s in range(2):
            b0 = i * per_span + s * n_chord
            b1 = (i + 1) * per_span + s * n_chord
            for j in range(n_chord - 1):
                faces.append((b0 + j, b0 + j + 1, b1 + j + 1, b1 + j))

    os.makedirs(os.path.join(d, "scalarField"), exist_ok=True)
    def hdr(cls, obj):
        return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                f"    class       {cls};\n    object      {obj};\n" + "}\n\n"
                "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")

    _write(os.path.join(d, "points"),
           hdr("vectorField", "points") +
           f"{len(pts)}\n(\n" + "".join(f"({p[0]!r} {p[1]!r} {p[2]!r})\n" for p in pts) + ")\n")
    _write(os.path.join(d, "faces"),
           hdr("faceList", "faces") +
           f"{len(faces)}\n(\n" +
           "".join(f"{len(f)}({' '.join(str(v) for v in f)})\n" for f in faces) + ")\n")
    _write(os.path.join(d, "scalarField", "p"),
           hdr("scalarField", "p") +
           f"{len(vals)}\n(\n" + "".join(f"{v!r}\n" for v in vals) + ")\n")
    return d


def d1_branch_reachability():
    """NOT A REGISTERED CONTROL.  A separate demonstration that D1's three branches are
    each REACHABLE, on synthetic fixtures with known answers.

    It exists because C12 cannot fire when the as-read Cn series is non-monotone, and a
    reader of that failure must be able to tell "the control's fixture cannot reach the
    branch" from "D1 structurally has only one answer".  Those are different findings and
    only the first is true.  This is REPORTED SEPARATELY and is NEVER substituted for C12.
    """
    def _synth(values):
        secs = {}
        for i, v in enumerate(values, start=1):
            # A closed rectangular loop whose enclosed -CP.d(x/c) integrates to v.
            secs[i] = [(1, 0.0, 0.0, -v), (2, 1.0, 0.0, -v),
                       (3, 1.0, 0.0, 0.0), (4, 0.0, 0.0, 0.0)]
        return {"sections": secs, "titles": {}, "n_sections": len(secs),
                "n_taps_total": 4 * len(secs)}

    out = {}
    out["CORROBORATED"] = d1_discriminator(
        _synth([1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]))["verdict"]      # 0.4/1.0 = 0.40 <= 0.75
    out["FALSIFIED"] = d1_discriminator(
        _synth([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]))["verdict"]
    out["INDETERMINATE"] = d1_discriminator(
        _synth([1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94]))["verdict"]
    out["all_three_reachable"] = (
        out["CORROBORATED"] == "CORROBORATED" and out["FALSIFIED"] == "FALSIFIED"
        and out["INDETERMINATE"] == "INDETERMINATE")
    return out


def control_c16(scratch):
    """C16: run the suite once under `python3 -O` and require BYTE-IDENTICAL refusals.

    L-475: a guard set that is entirely assert-based is one interpreter flag from absent.
    """
    me = os.path.abspath(__file__)
    a = subprocess.run([sys.executable, me, "--controls", "--scratch",
                        os.path.join(scratch, "c16_plain")],
                       capture_output=True, text=True)
    b = subprocess.run([sys.executable, "-O", me, "--controls", "--scratch",
                        os.path.join(scratch, "c16_O")],
                       capture_output=True, text=True)
    same_rc = a.returncode == b.returncode
    # Compare the control VERDICT lines only; scratch paths differ by construction.
    def _verdicts(txt):
        return [ln for ln in txt.split("\n") if ln.startswith("CONTROL ")]
    same_out = _verdicts(a.stdout) == _verdicts(b.stdout)
    return {"rc_plain": a.returncode, "rc_dash_O": b.returncode,
            "identical_rc": same_rc, "identical_control_verdicts": same_out,
            "pass": same_rc and same_out}


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------
NOT_CLAIMED = [
    "no observed order of accuracy (clause L-HONEST, Section 6)",
    "Sanaa's named first deliverable is NOT delivered by this registration (Section 12.2)",
    "no mechanism for the 390-face surface's failure (Section 12.4)",
    "mu_inf = 1.929120e-05 Pa.s is NOT claimed to be a physical air viscosity (Section 12.5)",
    "the registered freestream k/omega do NOT model the S2MA tunnel (Section 12.6)",
    "Menter 1994 (A16) is NOT cited -- unreadable from the artifact this lab holds (12.7)",
    "no measured y+ (Section 12.8)",
    "the uncorrected wall interference and the ~12.7-chord farfield bias are NOT quantified",
    "Cp agreement in the rear 10 % of chord is NOT claimed to mean anything (Section 12.10)",
    "A-MAP is NOT claimed confirmed (Section 12.11)",
    "SUBMISSIONS ARE PARKED -- nothing is sent, filed or registered outside this box (12.18)",
]


def _emit(obj):
    print(json.dumps(obj, indent=2, default=str))


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--controls", action="store_true",
                    help="run the Section 10 planted controls C1..C20 and stop")
    ap.add_argument("--selftest", action="store_true",
                    help="controls, the -O control C16, and the MUTATION control")
    ap.add_argument("--mutate", default=None,
                    help="corrupt one shipped statistic; the suite MUST go RED")
    ap.add_argument("--gate-gf", action="store_true", help="grade Gate GF (step B0)")
    ap.add_argument("--gate-a", action="store_true", help="grade Gate A (step B4)")
    ap.add_argument("--grade", action="store_true",
                    help="grade Gate G and Gate P (step B6)")
    ap.add_argument("--gate-p", action="store_true",
                    help="Gate P and its figure data ALONE (step B6). Gate G is not run, so "
                         "the label passed to Gate P is NOT A RESULT; this mode can never "
                         "produce a PASS.")
    ap.add_argument("--run-root", default=os.path.join(REPO, "verification/runs/M6SR_runs"))
    ap.add_argument("--scratch", default=None)
    args = ap.parse_args(argv[1:])

    scratch = args.scratch or tempfile.mkdtemp(prefix="m6sr_controls_")
    os.makedirs(scratch, exist_ok=True)

    if args.controls or args.selftest:
        fired, detail = controls(scratch, mutate=args.mutate)
        for cid in sorted(fired, key=lambda s: (len(s), s)):
            print(f"CONTROL {cid:5s} {'FIRED' if fired[cid] else 'DID NOT FIRE'} : "
                  f"{detail[cid]}")
        allfired = all(fired.values())
        if args.selftest:
            c16 = control_c16(scratch)
            print(f"CONTROL C16   {'FIRED' if c16['pass'] else 'DID NOT FIRE'} : "
                  f"python3 vs python3 -O -> rc {c16['rc_plain']} / {c16['rc_dash_O']}, "
                  f"identical control verdicts {c16['identical_control_verdicts']}")
            # THE MUTATION CONTROL, TARGETED.  Replacing a shipped statistic must flip
            # EXACTLY that control from FIRED to DID NOT FIRE.  A bare "the suite went RED"
            # is worthless once any control is already red for an unrelated reason, so the
            # test is on the DELTA, not on the suite's colour.
            baseline_red = {c for c in fired if not fired[c]}
            reds = {}
            for target in ("C1", "C2", "C3", "C4", "C5", "C6", "C8", "C9", "C10", "C11",
                           "C13", "C14", "C15", "C17", "C18", "C19", "C19b", "C20",
                           "C21", "C22", "C23", "C24"):
                if target in baseline_red:
                    reds[target] = None                 # cannot mutate an already-red control
                    continue
                f2, _d2 = controls(os.path.join(scratch, "mut_" + target), mutate=target)
                now_red = {c for c in f2 if not f2[c]}
                reds[target] = (now_red - baseline_red) == {target}
            for t, red in reds.items():
                state = ("SKIPPED (already red)" if red is None else
                         ("FLIPPED TO RED" if red else "STAYED GREEN"))
                print(f"MUTATION {t:5s} {state} : shipped statistic replaced; a control "
                      "that cannot be broken is not a control")
            reach = d1_branch_reachability()
            print(f"D1 BRANCH REACHABILITY (NOT a registered control, reported separately): "
                  f"{reach} -- C12's fixture cannot reach FALSIFIED on non-monotone as-read "
                  "data; that is a fixture limit, NOT a one-answer discriminator.")
            bad = [t for t, r in reds.items() if r is False]
            if not c16["pass"] or bad:
                raise Refusal(
                    f"the selftest did not hold: -O parity {c16['pass']}, mutations that "
                    f"did NOT flip their own control to red: {bad}.")
        if not allfired:
            raise Refusal(
                "A PLANTED CONTROL DID NOT FIRE: "
                f"{[c for c in sorted(fired) if not fired[c]]}. A PASS reported by a reader "
                "whose plant did not fire is NOT A RESULT, not a pass (Section 10). REFUSED.")
        print("ALL REGISTERED CONTROLS FIRED.")
        print(f"L-HONEST: {L_HONEST}")
        return 0

    if args.gate_gf:
        fired, _detail = controls(os.path.join(scratch, "gf"))
        levels = _discover_levels(args.run_root)
        out = {"step": "B0", "gate": "GF", "cap_core_min": 1.0,
               "controls_fired": fired,
               "result": gate_gf(levels, fired),
               "L_HONEST": L_HONEST, "NOT_CLAIMED": NOT_CLAIMED}
        _emit(out)
        return 0

    if args.gate_a:
        levels = _discover_levels(args.run_root)
        out = {"step": "B4", "gate": "A", "cap_core_min": 2.0,
               "result": gate_a(levels),
               "L_HONEST": L_HONEST, "NOT_CLAIMED": NOT_CLAIMED}
        _emit(out)
        return 0

    if args.grade or args.gate_p:
        levels = _discover_levels(args.run_root)
        end_times = (3000, 4000, 5000)
        for lv, et in zip(levels, end_times):
            cl = completion_clauses(lv["case"], et)
            if not cl["ALL"]:
                raise Refusal(
                    f"{lv['id']}: rule-4 strict completion FAILED on "
                    f"{[k for k, v in cl.items() if v is False]}. The comparator REFUSES "
                    "(exit 2) rather than degrade (Section 8.6).")

        # ---- GATE P's DATA, BUILT FIRST AND WRITTEN TO DISK BEFORE GATE G RUNS.
        # Gate G is registered to REFUSE (exit 2) for want of a registered refinement ratio
        # (Amendment 10, prediction X3).  A refusal is a statement about a GATE; the measured
        # Cp curves are not a gate.  Building and PERSISTING them ahead of Gate G is what
        # keeps Sanaa's named first physics -- "M6 surface Cp at the AGARD span stations
        # against tunnel data" -- from being taken down by a refusal about a band.
        ref = read_case_2308()
        d1 = d1_discriminator(ref)
        cfd_by_level, meta_by_level = {}, {}
        for lv, et in zip(levels, end_times):
            sec, meta = cfd_sections_for_case(lv["case"], et, lv["polymesh"])
            cfd_by_level[lv["id"]] = sec
            meta_by_level[lv["id"]] = meta
        fig = gate_p_figure_data(ref, cfd_by_level, meta_by_level, d1)
        fig_path = os.path.join(args.run_root, "GATE_P_FIGURE_DATA.json")
        try:
            _write(fig_path, json.dumps(fig, indent=2, default=str) + "\n")
        except OSError as exc:
            raise Refusal(f"could not persist Gate P's figure data to {fig_path}: {exc}. "
                          "Data that exists only in a pipe is not an artifact. REFUSED.")

        # Gate P grades the FINEST level.  L1 is levels[-1] because _discover_levels()
        # returns them COARSE-TO-FINE, as Section 2.2 registers them.
        finest = levels[-1]["id"]

        if args.gate_p:
            # STANDALONE GATE P.  Gate G is NOT run in this mode, so Gate P has no Gate G
            # label and no band.  Gate P sits BEHIND Gate G, so the label passed is
            # NOT A RESULT -- the strictly conservative direction, and the only one standing
            # rule 5 permits a downstream gate to move a verdict in.  THIS MODE CAN NEVER
            # PRODUCE A PASS, and it is here so the figure and the order-independent channel
            # can be produced without a full grade.
            p = gate_p(ref, cfd_by_level[finest], d1, None, _verdict("NOT A RESULT"))
            _emit({"step": "B6 (Gate P only)", "graded_level": finest,
                   "gate_P": p,
                   "gate_G": "NOT RUN IN THIS MODE -- Gate P is behind Gate G, so the label "
                             "passed in is NOT A RESULT. This mode cannot produce a PASS.",
                   "figure_data": fig_path,
                   "L_HONEST": L_HONEST, "NOT_CLAIMED": NOT_CLAIMED})
            return 0

        # ---- GATE G.  UNCHANGED, and its registered refusal is NOT caught.  If it raises,
        # this exits 2 as the frozen document requires -- and Gate P's figure data is
        # already on disk at fig_path.
        cds = [os.path.join(lv["case"], "postProcessing", "forceCoeffs", "0",
                            "coefficient.dat") for lv in levels]
        logs = [os.path.join(lv["case"], "log.rhoSimpleFoam") for lv in levels]
        g = gate_g(cds, logs)
        gci, gci_basis = gci_fine_from_gate_g(g)
        p = gate_p(ref, cfd_by_level[finest], d1, gci, g["gate_G_label"])
        _emit({"step": "B6", "gate_G": g, "gate_P": p, "gate_R": gate_r(),
               "graded_level": finest,
               "gate_P_numerical_band_basis": gci_basis,
               "figure_data": fig_path,
               "L_HONEST": L_HONEST, "NOT_CLAIMED": NOT_CLAIMED})
        return 0

    ap.print_help()
    return 0


def _discover_levels(run_root):
    """Levels L3, L2, L1 in COARSE-TO-FINE order, as Section 2.2 registers them."""
    spec = [
        {"id": "L3", "cells": A4_CELLS[0],
         "polymesh": "/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/constant/polyMesh",
         "surface_sha256": SHA_SURFACE_1560},
        {"id": "L2", "cells": A4_CELLS[1],
         "polymesh": "/home/ubuntu/certonomous-runs/.mesh-cache/onera_m6/polyMesh",
         "surface_sha256": SHA_SURFACE_6240},
        {"id": "L1", "cells": A4_CELLS[2],
         "polymesh": os.path.join(run_root, "L1", "constant", "polyMesh"),
         "surface_sha256": None},
    ]
    for lv in spec:
        lv["case"] = os.path.join(run_root, lv["id"])
        lv["checkmesh"] = os.path.join(run_root, lv["id"], "log.checkMesh")
        # An in-run-root copy, once it exists, SUPERSEDES the read-only source: nothing
        # under /home/ubuntu/certonomous-runs/ is ever written by this comparator.
        local = os.path.join(run_root, lv["id"], "constant", "polyMesh")
        if os.path.isdir(local):
            lv["polymesh"] = local
        sha_file = os.path.join(run_root, lv["id"], "work", "surfaceMesh.cgns.sha256")
        if os.path.exists(sha_file):
            tok = open(sha_file).read().split()
            if tok:
                lv["surface_sha256"] = tok[0]
    return spec


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as _exc:
        print(f"REFUSED: {_exc}", file=sys.stderr)
        sys.exit(2)
    except InternalDefect as _exc:
        print(f"INTERNAL DEFECT of the comparator: {_exc}", file=sys.stderr)
        sys.exit(70)
    except Exception as _exc:            # a crash is NOT a refusal -- it is rc 70
        import traceback
        traceback.print_exc()
        print(f"INTERNAL DEFECT (unhandled {type(_exc).__name__}): {_exc}", file=sys.stderr)
        sys.exit(70)
