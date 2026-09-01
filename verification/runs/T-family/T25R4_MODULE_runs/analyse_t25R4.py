#!/usr/bin/env python3
"""T25R3 COMPARATOR -- the only file in this rung that reaches a verdict.

Registration: docs/campaigns/T-family/T25R3_PREREGISTRATION.md, v1.1
(Amendment A1).  The grading path is fixed at that document's commit and
`freeze_check` hashes the document against the committed blob and REFUSES on a
mismatch (CLAUDE.md rule 2).

WHAT THIS FILE IS FOR, IN ONE LINE: it decides G-I, then the Roache
classification, then G-S and G-T, then C1-C3, in that order, and it WITHHOLDS
every physics number until the gates ahead of it have been decided.

THREE THINGS INHERITED DELIBERATELY FROM analyse_t25R2.py, WHICH IS FROZEN AND
IS NOT IMPORTED (rule 6 -- a frozen file is not a library for its successor):
  * the polyMesh reader, exact on axis-aligned hexahedra and REFUSING on
    anything else rather than approximating;
  * the structural field-list locator -- every list is delimited from the
    FIELD'S OWN HEADER (keyword, count, opening parenthesis), never by a regex
    sweep and NEVER BY VALUE;
  * the nine-clause planted-zero control.

AND ONE THING DELIBERATELY REPAIRED -- THE §10.2 MUST-FIX.  T25R2's
`read_patch_T` accepted ONLY a `nonuniform List<scalar>` patch entry and refused
everything else.  The real staged coolant inlet is written by OpenFOAM as
`inlet { type fixedValue; value uniform 293; }`, so that reader REFUSED at every
written time and C3 would have been NOT A RESULT on an INSTRUMENT REFUSAL even
if every physics gate had passed.  Root cause: its selftest forged the patch
WITH a nonuniform list, so the reader was never exercised against the form
OpenFOAM actually writes.  THE FIXTURE DID NOT RESEMBLE THE SITUATION.

Here the reader accepts BOTH forms, and `--selftest` drives the repair BOTH
WAYS: the new reader must READ a real `uniform` entry copied from a staged
0.orig, and the LEGACY reader -- carried verbatim below for exactly this
purpose -- must still REFUSE on the same bytes.  A fix whose selftest cannot
show the old code failing is not a demonstrated fix.

  python3 analyse_t25R3.py --selftest
  python3 analyse_t25R3.py --grade <runs-root>

NOTHING HERE LAUNCHES A SOLVER.
"""

import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FROZEN_DOC = "docs/campaigns/T-family/T25R4_PREREGISTRATION.md"
EXIT_REFUSE = 2

# ==========================================================================
# REGISTERED CONSTANTS.  Every one of these is in the frozen document and none
# is a choice made here.  A value that disagrees with the document is a defect
# in THIS file, not a tuning knob.
# ==========================================================================

PLANT = 1.234e-03                 # §10.1, inherited
PLANT_REL_SLACK = 1e-9            # the ONLY sizing tolerance, and it is relative
LADDER = (1.234e-06, 1.234e-05, 1.234e-04, PLANT, 1.234e-02)

TAU = 1.000e-01                   # §7.2 THE GATE
TIER2 = 1.234e-02                 # §7.2 REPORTED ALWAYS, GATES NOTHING
GI_RATIO = 0.10                   # §7.3, Sanaa's §0.2 "at least 10x smaller"

P_LO, P_HI = 0.5, 1.5             # §4.2/§8 -- Euler in time, upwind in space
FS = 1.25                         # §8, Roache GCI factor of safety

N_CELLS = 8
CELL_LX, CELL_LY, GAP, DEPTH = 0.100, 0.030, 0.003, 1.000
PITCH = CELL_LY + GAP             # 0.033 m
T_INIT = 293.0
RHO_S, CP_S = 2500.0, 1000.0
RHO_AIR, CP_AIR = 1.2, 1005.0
MDOT_IN = 0.20160                 # kg/s, §3.1
E_GEN = 647700.0                  # J over 900 s, THE RAMPED figure (§5.2)
T_END = 900.0
WRITE_INTERVAL = 5.0
WRITE_TIMES = tuple(i * WRITE_INTERVAL
                    for i in range(int(T_END / WRITE_INTERVAL) + 1))   # 181

C1_TOL = 0.02                     # energy ledger, gating
C2_TOL = 1e-3                     # mass balance, gating

CELLS = {"L1": 16608, "L2": 37368, "L3": 84078}

# §2 -- the closed run set.  (mesh level, leg-A steps, leg-B steps, nOuterCorr)
RUNS = {
    "S1":  ("L1", 3500,  8300,  15),
    "S2":  ("L2", 3500,  8300,  15),
    "S3":  ("L3", 3500,  8300,  15),
    "T2":  ("L2", 7000,  16600, 15),
    "T4":  ("L2", 14000, 33200, 15),
    "W30": ("L2", 3500,  8300,  30),
}
SPACE_TRIPLE = ("S1", "S2", "S3")     # coarse -> fine
TIME_TRIPLE = ("S2", "T2", "T4")      # coarse -> fine
R_SPACE = 1.5                         # §3.3, (2.25)^(1/2), EXACT
R_TIME = 2.0                          # §6.1, EXACT


def refuse(msg):
    """REFUSES (exit 2) rather than degrades.  There is no soft path out."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def clear_pycache():
    """A stale bytecode cache INVERTS a mutation control -- the clean arm fails
    and the mutated arm passes -- and PYTHONDONTWRITEBYTECODE does NOT fix it."""
    for d in (HERE, os.path.join(REPO, "scripts")):
        p = os.path.join(d, "__pycache__")
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)


# ==========================================================================
# THE FREEZE CHECK.  Rule 2: verify the frozen file IS the file that ran.
# ==========================================================================

def freeze_check(repo=None):
    repo = REPO if repo is None else repo
    p = os.path.join(repo, FROZEN_DOC)
    if not os.path.isfile(p):
        refuse("the frozen document %s is not on disk -- there is nothing to "
               "grade against" % FROZEN_DOC)
    r = subprocess.run(["git", "-C", repo, "hash-object", p],
                       capture_output=True, text=True)
    if r.returncode != 0:
        refuse("git hash-object failed on %s" % FROZEN_DOC)
    worktree = r.stdout.strip()
    r = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD:" + FROZEN_DOC],
                       capture_output=True, text=True)
    if r.returncode != 0:
        refuse("%s is NOT COMMITTED at HEAD. The gate, threshold, cap and label "
               "must be committed BEFORE compute and the grading path is fixed "
               "at that commit. An uncommitted pre-registration has no "
               "evidentiary content whatever." % FROZEN_DOC)
    committed = r.stdout.strip()
    if worktree != committed:
        refuse("THE FROZEN DOCUMENT HAS BEEN EDITED SINCE ITS COMMIT.\n"
               "  working tree blob : %s\n  HEAD blob         : %s\n"
               "Frozen files are never edited (rule 6). A departure lands as a "
               "DATED AMENDMENT APPENDED AT THE FOOT with a version bump, never "
               "as an in-place edit." % (worktree, committed))
    return committed


# ==========================================================================
# polyMesh.  Every cell of this mesh is an AXIS-ALIGNED BOX, so a centroid is
# the mean of the bounding corners and a volume is the product of the extents,
# EXACTLY.  That boxness is CHECKED, not assumed: a cell whose vertex set is not
# the 8 corners of its bounding box is a REFUSAL, because every geometric number
# below would then be wrong in a way no threshold would catch.
# ==========================================================================

def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    return re.sub(r"//[^\n]*", " ", txt)


def _body(path):
    if not os.path.isfile(path):
        refuse("no %s -- the mesh this reader needs is not on disk" % path)
    txt = _strip(open(path).read())
    end = txt.find("}")
    if end < 0:
        refuse("%s has no FoamFile header" % path)
    rest = txt[end + 1:]
    m = re.search(r"(\d+)\s*\(", rest)
    if not m:
        refuse("%s carries no `<count> (` list header -- a structural locator "
               "will not guess one" % path)
    return int(m.group(1)), rest[m.end():]


def read_points(path):
    n, rest = _body(path)
    pts = re.findall(
        r"\(\s*(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s*\)", rest)
    if len(pts) < n:
        refuse("%s claims %d points, found %d" % (path, n, len(pts)))
    return [(float(a), float(b), float(c)) for a, b, c in pts[:n]]


def read_faces(path):
    n, rest = _body(path)
    out = []
    for m in re.finditer(r"(\d+)\s*\(([^)]*)\)", rest):
        k = int(m.group(1))
        v = m.group(2).split()
        if len(v) != k:
            refuse("%s: a face declares %d labels and lists %d"
                   % (path, k, len(v)))
        out.append([int(x) for x in v])
        if len(out) == n:
            break
    if len(out) != n:
        refuse("%s claims %d faces, found %d" % (path, n, len(out)))
    return out


def read_labels(path):
    n, rest = _body(path)
    v = re.findall(r"-?\d+", rest)
    if len(v) < n:
        refuse("%s claims %d labels, found %d" % (path, n, len(v)))
    return [int(x) for x in v[:n]]


def read_boundary(path):
    n, rest = _body(path)
    out = {}
    for m in re.finditer(r"([A-Za-z_][\w.:-]*)\s*\{([^{}]*)\}", rest):
        blk = m.group(2)
        s = re.search(r"startFace\s+(\d+)\s*;", blk)
        f = re.search(r"nFaces\s+(\d+)\s*;", blk)
        if s and f:
            out[m.group(1)] = (int(s.group(1)), int(f.group(1)))
    if len(out) != n:
        refuse("%s declares %d patches and %d were parsed" % (path, n, len(out)))
    return out


class Mesh(object):
    """Cell boxes and patch face geometry for ONE region of ONE case."""

    def __init__(self, case_dir, region):
        pm = os.path.join(case_dir, "constant", region, "polyMesh")
        self.points = read_points(os.path.join(pm, "points"))
        self.faces = read_faces(os.path.join(pm, "faces"))
        self.owner = read_labels(os.path.join(pm, "owner"))
        nb = os.path.join(pm, "neighbour")
        self.neigh = read_labels(nb) if os.path.isfile(nb) else []
        self.bnd = read_boundary(os.path.join(pm, "boundary"))
        self.n = max(max(self.owner), max(self.neigh) if self.neigh else -1) + 1

        cellpts = [set() for _ in range(self.n)]
        for fi, c in enumerate(self.owner):
            cellpts[c].update(self.faces[fi])
        for fi, c in enumerate(self.neigh):
            cellpts[c].update(self.faces[fi])

        self.vol, self.cx, self.cy = [], [], []
        for c in range(self.n):
            ps = [self.points[i] for i in cellpts[c]]
            if len(ps) != 8:
                refuse("%s cell %d has %d distinct vertices, not 8 -- this "
                       "reader is exact ONLY on hexahedra and REFUSES rather "
                       "than approximate" % (region, c, len(ps)))
            lo = [min(p[k] for p in ps) for k in range(3)]
            hi = [max(p[k] for p in ps) for k in range(3)]
            for p in ps:
                for k in range(3):
                    if abs(p[k] - lo[k]) > 1e-12 and abs(p[k] - hi[k]) > 1e-12:
                        refuse("%s cell %d is NOT an axis-aligned box -- the "
                               "exact centroid/volume path does not apply and "
                               "this reader REFUSES" % (region, c))
            d = [hi[k] - lo[k] for k in range(3)]
            if min(d) <= 0.0:
                refuse("%s cell %d has a non-positive extent %r" % (region, c, d))
            self.vol.append(d[0] * d[1] * d[2])
            self.cx.append(0.5 * (lo[0] + hi[0]))
            self.cy.append(0.5 * (lo[1] + hi[1]))

    def patch_face_areas(self, patch):
        if patch not in self.bnd:
            refuse("patch %r absent; the region carries %s"
                   % (patch, ",".join(sorted(self.bnd))))
        s, k = self.bnd[patch]
        out = []
        for fi in range(s, s + k):
            ps = [self.points[i] for i in self.faces[fi]]
            d = [max(p[j] for p in ps) - min(p[j] for p in ps) for j in range(3)]
            nz = [x for x in d if x > 1e-14]
            if len(nz) != 2:
                refuse("patch %s face %d is not a planar axis-aligned quad "
                       "(extents %r)" % (patch, fi, d))
            out.append(nz[0] * nz[1])
        return out


# ==========================================================================
# FIELD FILES.  Every list is delimited from the FIELD'S OWN HEADER -- keyword,
# count, opening parenthesis -- never by a regex sweep and NEVER BY VALUE.
# ==========================================================================

def _list_window(lines, key_idx, path):
    i = key_idx + 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or not re.fullmatch(r"\d+", lines[i].strip()):
        refuse("%s: list at line %d carries no element count -- the structural "
               "locator will not guess one" % (path, key_idx))
    n = int(lines[i].strip())
    i += 1
    if i >= len(lines) or lines[i].strip() != "(":
        refuse("%s: list at line %d has no opening parenthesis after its count"
               % (path, key_idx))
    if i + 1 + n > len(lines):
        refuse("%s: list at line %d claims %d elements the file does not hold"
               % (path, key_idx, n))
    return i + 1, n


def internal_window(path):
    if not os.path.isfile(path):
        refuse("no %s" % path)
    lines = open(path).read().split("\n")
    idx = [k for k, l in enumerate(lines)
           if re.match(r"\s*internalField\s+nonuniform\s+List<scalar>", l)]
    if len(idx) != 1:
        refuse("%s has %d internalField scalar-list headers, expected exactly 1. "
               "A UNIFORM internalField here would mean the solver wrote a "
               "constant field, which is a FINDING, not a parse problem"
               % (path, len(idx)))
    first, n = _list_window(lines, idx[0], path)
    return lines, first, n


def _patch_block(lines, path, patch):
    """(start, end) line indices of ONE boundaryField patch's brace block."""
    bidx = [k for k, l in enumerate(lines) if re.match(r"^boundaryField\s*$", l)]
    if len(bidx) != 1:
        refuse("%s has %d boundaryField headers, expected exactly 1"
               % (path, len(bidx)))
    pidx = [k for k, l in enumerate(lines) if k > bidx[0] and l.strip() == patch]
    if len(pidx) != 1:
        refuse("%s has %d `%s` blocks in boundaryField, expected exactly 1"
               % (path, len(pidx), patch))
    k, depth, opened = pidx[0], 0, False
    while k < len(lines):
        depth += lines[k].count("{") - lines[k].count("}")
        if lines[k].count("{"):
            opened = True
        if opened and depth == 0:
            return pidx[0], k
        k += 1
    refuse("%s: patch `%s` brace block never closes" % (path, patch))


# ==========================================================================
# ⚠ THE §10.2 MUST-FIX LIVES HERE.
#
# `patch_value_spec` accepts BOTH forms OpenFOAM actually writes for a `value`
# entry, and says which it found:
#
#     value           nonuniform List<scalar>   -> ("nonuniform", first, n)
#     value           uniform 293;              -> ("uniform", line_index, 1)
#
# IT STILL REFUSES TO FALL BACK TO `refValue`.  That refusal was never the
# defect and is retained verbatim in spirit: `value` and `refValue` are
# different quantities, and a silent fallback is how a coupled-patch reader ends
# up reporting the neighbour's guess instead of the answer.
#
# WHAT WAS THE DEFECT: refusing `uniform`, which is not a different quantity at
# all -- it is the SAME quantity, written in the compact form OpenFOAM uses when
# every face carries the same value, which is exactly what a `fixedValue` inlet
# does at every written time.
# ==========================================================================

_UNIFORM_RE = re.compile(r"^\s+value\s+uniform\s+(-?[\d.eE+-]+)\s*;\s*$")
_NONUNIFORM_RE = re.compile(r"\s+value\s+nonuniform\s+List<scalar>")


def patch_value_spec(path, patch):
    """-> (lines, kind, first, n).  `first` indexes the first VALUE line."""
    if not os.path.isfile(path):
        refuse("no %s" % path)
    lines = open(path).read().split("\n")
    lo, hi = _patch_block(lines, path, patch)
    nun = [k for k in range(lo, hi + 1) if _NONUNIFORM_RE.match(lines[k])]
    uni = [k for k in range(lo, hi + 1) if _UNIFORM_RE.match(lines[k])]
    if len(nun) + len(uni) != 1:
        refuse("patch `%s` in %s carries %d nonuniform and %d uniform `value` "
               "entries; exactly one is required. This reader will NOT fall "
               "back to `refValue`, which is a DIFFERENT QUANTITY -- that "
               "refusal is deliberate and is not the defect §10.2 repairs"
               % (patch, path, len(nun), len(uni)))
    if nun:
        first, n = _list_window(lines, nun[0], path)
        return lines, "nonuniform", first, n
    return lines, "uniform", uni[0], 1


def patch_values(path, patch, nfaces):
    """The per-face values of `patch`, expanded to `nfaces` for either form."""
    lines, kind, first, n = patch_value_spec(path, patch)
    if kind == "uniform":
        m = _UNIFORM_RE.match(lines[first])
        if m is None:
            refuse("%s patch %s: patch_value_spec classified line %d as the "
                   "uniform form and _UNIFORM_RE then failed to match it. This "
                   "is unreachable if the two agree, and it REFUSES rather than "
                   "raising AttributeError, because this family's comparators "
                   "must exit 2 rather than traceback -- an exit code that is "
                   "ambiguous between `graded non-PASS` and `uncaught crash` is "
                   "worse than no exit code." % (path, patch, first))
        v = float(m.group(1))
        return [v] * nfaces
    if n != nfaces:
        refuse("patch %s in %s: %d boundary values against %d mesh faces"
               % (patch, path, n, nfaces))
    return [float(lines[first + i]) for i in range(n)]


def _legacy_patch_value_window(path, patch):
    """⚠ analyse_t25R2.py's reader, CARRIED VERBATIM AND NEVER CALLED IN
    GRADING.  It exists so `--selftest` can drive the §10.2 repair in the
    NEGATIVE direction: on the real `uniform` inlet OpenFOAM writes, THIS
    function must still refuse.  A fix whose selftest cannot show the old code
    failing on the same bytes is not a demonstrated fix -- it is an assertion.
    """
    if not os.path.isfile(path):
        refuse("no %s" % path)
    lines = open(path).read().split("\n")
    bidx = [k for k, l in enumerate(lines) if re.match(r"^boundaryField\s*$", l)]
    if len(bidx) != 1:
        refuse("%s has %d boundaryField headers, expected exactly 1"
               % (path, len(bidx)))
    pidx = [k for k, l in enumerate(lines) if k > bidx[0] and l.strip() == patch]
    if len(pidx) != 1:
        refuse("%s has %d `%s` blocks in boundaryField, expected exactly 1"
               % (path, len(pidx), patch))
    k, depth, opened, vidx = pidx[0], 0, False, None
    while k < len(lines):
        depth += lines[k].count("{") - lines[k].count("}")
        if lines[k].count("{"):
            opened = True
        if opened and depth == 1 and re.match(
                r"\s+value\s+nonuniform\s+List<scalar>", lines[k]):
            vidx = k
        if opened and depth == 0:
            break
        k += 1
    if vidx is None:
        refuse("patch `%s` in %s carries no nonuniform `value` list. This "
               "reader will NOT fall back to refValue" % (patch, path))
    first, n = _list_window(lines, vidx, path)
    return lines, first, n


TIME_NAME_TOL = 1.0e-6          # s.  See the note below; measured drift is 1.4e-10.


def tdir(case_dir, t):
    """The written time directory for `t`, located BY NUMERIC VALUE.

    *** THIS IS A REPAIR FORCED BY MEASUREMENT, AND THE T25R3 REGISTRATION WAS
    WRONG ABOUT IT. ***  T25R3 §6.2 argued that `deltaT 0.02` was safe because
    Time.C:1120 guards the write INDEX with `+ 0.5*deltaT`.  That part is true
    and the writes did land on the right steps.  What §6.2 got wrong is the
    directory NAME: OpenFOAM accumulates `value_ += deltaT_`, and on T25R3's S1
    the drift reached **1.39e-10 s at t = 900**, so `Time::setControls()`
    (Time.C:245) AUTOMATICALLY RAISED timePrecision from 12 to 17 and the
    directories are named `900.00000000013904`, `70.00000000000321`,
    `45.000000000001`.  **172 of 181 names were drifted.**

    A name-formatting lookup (`"%g" % 900` -> "900") therefore finds NOTHING,
    and S1 -- a physically complete, correct run with every field on disk --
    was marked NOT DONE by its own instrument.  **The run was fine; the reader
    was broken.**

    The fix is to locate by VALUE with a tolerance far above the drift
    (1e-6 s against 1.4e-10 s measured, four orders of margin) and far below
    the 5 s write interval (seven orders), so it can never select a neighbour.
    An AMBIGUOUS match REFUSES rather than picking one."""
    hits = []
    for e in os.listdir(case_dir):
        if not os.path.isdir(os.path.join(case_dir, e)):
            continue
        try:
            v = float(e)
        except ValueError:
            continue          # `0.orig` lives here and is NOT a time directory
        if abs(v - t) <= TIME_NAME_TOL:
            hits.append((abs(v - t), e))
    if not hits:
        refuse("case %s has no time directory within %g s of t = %g -- §9 "
               "registers writes every 5 s, so this time was registered and is "
               "ABSENT" % (case_dir, TIME_NAME_TOL, t))
    if len(hits) > 1:
        refuse("case %s has %d time directories within %g s of t = %g (%s) -- "
               "AMBIGUOUS, and this reader refuses rather than choosing one"
               % (case_dir, len(hits), TIME_NAME_TOL, t,
                  ", ".join(h[1] for h in hits)))
    return os.path.join(case_dir, hits[0][1])


def fld(case_dir, t, region, name):
    return os.path.join(tdir(case_dir, t), region, name)


# ==========================================================================
# THE READERS.  Each is paired with a planter that writes into EXACTLY the
# artifact that reader reads.
# ==========================================================================

_MESH_CACHE = {}


def _mesh(case_dir, region):
    k = (os.path.realpath(case_dir), region)
    if k not in _MESH_CACHE:
        _MESH_CACHE[k] = Mesh(case_dir, region)
    return _MESH_CACHE[k]


def _cell_of(mesh, i):
    """Which of the 8 module cells cell-index i belongs to, by its y centre."""
    j = int(math.floor(mesh.cy[i] / PITCH))
    if j < 0 or j >= N_CELLS:
        refuse("module cell %d has y centre %.6g, outside the 8 registered "
               "cell bands" % (i, mesh.cy[i]))
    lo = j * PITCH
    if not (lo - 1e-12 <= mesh.cy[i] <= lo + CELL_LY + 1e-12):
        refuse("module cell %d has y centre %.6g, which lies in the CHANNEL GAP "
               "above cell %d -- the module region must carry no fluid cells"
               % (i, mesh.cy[i], j + 1))
    return j


def read_cell_T(case_dir, t, mesh=None):
    """Q2's primitive: volume-averaged solid T of each of the 8 cells, K."""
    mesh = _mesh(case_dir, "module") if mesh is None else mesh
    p = fld(case_dir, t, "module", "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("module/T at t=%g holds %d values against %d mesh cells"
               % (t, n, mesh.n))
    num = [0.0] * N_CELLS
    den = [0.0] * N_CELLS
    for i in range(n):
        j = _cell_of(mesh, i)
        num[j] += mesh.vol[i] * float(lines[first + i])
        den[j] += mesh.vol[i]
    if min(den) <= 0.0:
        refuse("a registered module cell received no mesh cells at all")
    return [num[j] / den[j] for j in range(N_CELLS)]


def read_patch_T(case_dir, t, patch, mesh=None):
    """Q1's primitive: AREA-WEIGHTED mean coolant T on `patch`, K.

    Area-weighted, not arithmetic: the channel is graded, so the outlet faces
    differ in area by the block expansion (4.6 to 4.7 across the levels) and an
    unweighted mean would be a different quantity on every mesh level -- which
    is precisely the quantity a mesh-convergence gate must not use."""
    mesh = _mesh(case_dir, "coolant") if mesh is None else mesh
    a = mesh.patch_face_areas(patch)
    v = patch_values(fld(case_dir, t, "coolant", "T"), patch, len(a))
    return sum(ai * vi for ai, vi in zip(a, v)) / sum(a)


def read_stored(case_dir, t, region, mesh=None):
    """Stored sensible energy above T_INIT in `region`, J."""
    mesh = _mesh(case_dir, region) if mesh is None else mesh
    p = fld(case_dir, t, region, "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("%s/T at t=%g holds %d values against %d mesh cells"
               % (region, t, n, mesh.n))
    rc = RHO_S * CP_S if region == "module" else RHO_AIR * CP_AIR
    return sum(mesh.vol[i] * rc * (float(lines[first + i]) - T_INIT)
               for i in range(n))


# -------- the function-object .dat readers (Q0, and the mass balance) --------

def _dat_path(case_dir, name):
    """Locate ONE function-object .dat across BOTH legs.

    §6.3 registered this: leg B restarts at t = 70 and OpenFOAM writes its
    output into postProcessing/<fo>/70/.  The comparator reads BOTH and REFUSES
    if their union does not cover [0, 900] without a gap."""
    root = os.path.join(case_dir, "postProcessing", name)
    if not os.path.isdir(root):
        refuse("no postProcessing/%s in %s -- the registered instrument did not "
               "run and its quantity cannot be reconstructed" % (name, case_dir))
    out = []
    for sub in sorted(os.listdir(root), key=lambda s: float(s)):
        d = os.path.join(root, sub)
        dats = [f for f in sorted(os.listdir(d)) if f.endswith(".dat")]
        if len(dats) != 1:
            refuse("postProcessing/%s/%s holds %d .dat files, expected exactly "
                   "1 -- a restart collision renames these and a reader that "
                   "globs will silently take the wrong one" % (name, sub, len(dats)))
        out.append(os.path.join(d, dats[0]))
    if not out:
        refuse("postProcessing/%s carries no time directory" % name)
    return out


def _read_dat(paths):
    """-> [(t, value)], concatenated across legs, strictly increasing in t."""
    rows = []
    for p in paths:
        for line in open(p):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            f = s.split()
            if len(f) < 2:
                refuse("%s: a data row carries %d columns, expected >= 2"
                       % (p, len(f)))
            rows.append((float(f[0]), float(f[1])))
    rows.sort(key=lambda r: r[0])
    ded = []
    for t, v in rows:
        if ded and t == ded[-1][0]:
            ded[-1] = (t, v)          # leg B's first row repeats leg A's last
        else:
            ded.append((t, v))
    if not ded:
        refuse("no data rows in %r" % (paths,))
    return ded


def _leg_coverage_check(rows, label):
    if abs(rows[-1][0] - T_END) > 1e-6:
        refuse("%s: the instrument's last sample is t = %.6g, not the "
               "registered endTime %g -- the two legs do not cover the run"
               % (label, rows[-1][0], T_END))
    gaps = [(rows[i + 1][0] - rows[i][0]) for i in range(len(rows) - 1)]
    if gaps and max(gaps) > 0.2 + 1e-9:
        refuse("%s: a %.6g s gap between consecutive samples. §6.3 registers "
               "that the union of the two legs covers [0, 900] WITHOUT A GAP, "
               "and a gap here means one leg's postProcessing is missing"
               % (label, max(gaps)))


def read_hflux_point(case_dir, idx=-1):
    """The outlet_hflux instrument's value at ONE row.  This is the reader the
    Q0 planted control drives, so the plant and the read are in the SAME UNITS
    -- planting into an integral and reading a rate is how a sizing predicate
    ends up testing arithmetic instead of sight."""
    rows = _read_dat(_dat_path(case_dir, "outlet_hflux"))
    return rows[idx][1]


def read_Q0(case_dir):
    """Q0, the SMOOTH order quantity: the time integral of c_p * sum(phi_f T_f)
    over the outlet across the whole run, J per metre of depth.  §7.1.

    Trapezoid on each run's OWN step series -- the ladder levels have different
    step counts by construction and a common grid would resample them."""
    rows = _read_dat(_dat_path(case_dir, "outlet_hflux"))
    _leg_coverage_check(rows, "%s outlet_hflux" % os.path.basename(case_dir))
    s = 0.0
    for i in range(len(rows) - 1):
        s += 0.5 * (rows[i][1] + rows[i + 1][1]) * (rows[i + 1][0] - rows[i][0])
    return CP_AIR * s


def read_Q1_history(case_dir):
    """Q1: the outlet area-mean T at every one of the 181 written times."""
    m = _mesh(case_dir, "coolant")
    return [read_patch_T(case_dir, t, "outlet", m) for t in WRITE_TIMES]


def read_Q2_peaks(case_dir):
    """Q2: for each of the 8 solid cells, the PEAK over the 181 written times of
    its volume-averaged T."""
    m = _mesh(case_dir, "module")
    peak = [-1e30] * N_CELLS
    for t in WRITE_TIMES:
        v = read_cell_T(case_dir, t, m)
        peak = [max(peak[j], v[j]) for j in range(N_CELLS)]
    return peak


def read_inlet_T(case_dir, t):
    """C3's primitive, and THE READER §10.2 REPAIRS.  The staged inlet is
    `fixedValue; value uniform 293;` and this must READ it, not refuse it."""
    return read_patch_T(case_dir, t, "inlet")


# ==========================================================================
# THE PLANTERS.  BY LINE INDEX, inside a window taken from the artifact's own
# header.  Nothing is ever located by value.  Each returns the count planted.
# ==========================================================================

def _plant_patch_all(path, patch, mag, nfaces):
    """EVERY face, so the expected shift in an area-weighted mean is EXACTLY
    `mag`, never mag/N.  Handles BOTH `value` forms, because the reader does."""
    lines, kind, first, n = patch_value_spec(path, patch)
    if kind == "uniform":
        m = _UNIFORM_RE.match(lines[first])
        if m is None:
            refuse("%s patch %s: the planter cannot re-match the uniform value "
                   "line it was handed; REFUSING rather than raising" % (path, patch))
        v = float(m.group(1))
        lines[first] = re.sub(r"uniform\s+-?[\d.eE+-]+",
                              "uniform %.12g" % (v + mag), lines[first])
        open(path, "w").write("\n".join(lines))
        return nfaces
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(path, "w").write("\n".join(lines))
    return n


def _plant_hottest_module_cell(case_dir, t, mag):
    """Plant into EVERY mesh cell of the HOTTEST of the 8 module cells.

    Every solid reader returns a VOLUME AVERAGE over one module cell. Planting a
    single mesh cell would shift that average by mag*V_i/V_cell -- by mag/N --
    and the control would then fail its sizing clause for a reason that has
    nothing to do with whether the reader can SEE the plant.  Planting the whole
    module cell makes the expected shift EXACTLY `mag`.  The cell is chosen by
    its VOLUME-AVERAGE RANK, never by locating a value in the file."""
    mesh = _mesh(case_dir, "module")
    p = fld(case_dir, t, "module", "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("module/T holds %d values against %d mesh cells" % (n, mesh.n))
    num = [0.0] * N_CELLS
    den = [0.0] * N_CELLS
    for i in range(n):
        j = _cell_of(mesh, i)
        num[j] += mesh.vol[i] * float(lines[first + i])
        den[j] += mesh.vol[i]
    hot = max(range(N_CELLS), key=lambda j: num[j] / den[j])
    cnt = 0
    for i in range(n):
        if _cell_of(mesh, i) == hot:
            lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
            cnt += 1
    open(p, "w").write("\n".join(lines))
    return cnt


def _plant_internal_one(path, mag):
    """ONE internal cell.  Used ONLY as the NEGATIVE ARM of the selftest, to
    prove the mag/N failure mode is LIVE and that clause 5 would catch it."""
    lines, first, n = internal_window(path)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)
    open(path, "w").write("\n".join(lines))
    return 1


def _plant_dat_all(path, mag):
    """Add `mag` to the value column of EVERY data row, by line index."""
    lines = open(path).read().split("\n")
    cnt = 0
    for k, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        f = line.split()
        f[1] = "%.12g" % (float(f[1]) + mag)
        lines[k] = "\t".join(f)
        cnt += 1
    open(path, "w").write("\n".join(lines))
    return cnt


# ==========================================================================
# THE PLANTED-ZERO CONTROL.  REFUSES rather than degrades.
# A zero from a reader not shown able to see a non-zero is not evidence.
# ==========================================================================

def planted_zero_control(case_dir, label, reader, planter, target_rel):
    clear_pycache()                                        # clause 9
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="t25R3ctl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    tgt = lambda d: os.path.join(d, target_rel)            # noqa: E731
    try:
        # CLAUSE 1: COPY FIRST, NEVER WRITE INTO THE CASE.
        if os.path.realpath(scratch) == case_real \
           or os.path.realpath(scratch).startswith(case_real + os.sep):
            refuse("control scratch %s resolves INSIDE the case %s -- clause 1 "
                   "forbids writing into the case under any circumstance"
                   % (scratch, case_real))
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.*", "*.py",
                                                      "processor*"))
        if not os.path.isfile(tgt(dest)):
            refuse("%s: the control target %s is not in the copy"
                   % (label, target_rel))
        pristine = open(tgt(dest)).read()
        _MESH_CACHE.pop((os.path.realpath(dest), "module"), None)
        _MESH_CACHE.pop((os.path.realpath(dest), "coolant"), None)

        # CLAUSE 2: NEGATIVE ARM, THRESHOLD EXACTLY ZERO, NO TOLERANCE.
        a = reader(dest)
        b = reader(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r, and the threshold is bitwise "
                   "0.0 with NO tolerance" % (label, b - a))
        base = a

        # CLAUSE 3: POSITIVE ARM, a MEASURED ladder, exact and epsilon-free.
        rungs, floor, at_plant, n_planted = [], None, None, None
        for mag in LADDER:
            open(tgt(dest), "w").write(pristine)
            cnt = planter(dest, mag)
            got = reader(dest) - base
            rungs.append((mag, got, cnt))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, n_planted = got, cnt
        open(tgt(dest), "w").write(pristine)

        # CLAUSE 4: REFUSE IF BLIND.
        if floor is None:
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in the "
                   "registered ladder produced a non-zero read. An instrument "
                   "that cannot see a planted perturbation is not entitled to "
                   "certify anything" % label)

        # CLAUSE 5: THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE.
        #
        # TWO-SIDED, AND DELIBERATELY SO.  analyse_t25R2's clause 5 bounded the
        # read only from BELOW, so a reader that reported a planted 1.234e-03 K
        # as 1.234e-01 K -- a hundredfold over-read, e.g. an area weight applied
        # twice -- would have passed it.  Seeing the plant is necessary and not
        # sufficient; seeing it AT ITS SIZE is the claim.  The slack stays
        # RELATIVE at 1e-9: the read is a difference of two numbers near 293 K,
        # so cancellation costs about eps*293/PLANT ~ 5e-11 of relative
        # precision, and 1e-9 sits two decades above that floor rather than
        # being an unexamined round number.
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("%s: read at PLANT is %.6e, below the registered RELATIVE "
                   "predicate PLANT*(1-1e-9) = %.6e"
                   % (label, at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))
        if not (at_plant <= PLANT * (1.0 + PLANT_REL_SLACK)):
            refuse("%s: read at PLANT is %.6e, ABOVE PLANT*(1+1e-9) = %.6e. The "
                   "reader sees the plant and MIS-SIZES it, which is a "
                   "calibration defect and not a sighting"
                   % (label, at_plant, PLANT * (1.0 + PLANT_REL_SLACK)))

        # CLAUSE 8: the case was never written to, and that is CHECKED.
        if open(tgt(case_dir)).read() != open(tgt(dest)).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)
        return dict(passed=True, base=base, floor=floor, at_plant=at_plant,
                    n_planted=n_planted, rungs=rungs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)         # clause 8, in finally


# ==========================================================================
# ROACHE.  Rule 5, and the ORDER of its clauses is not negotiable.
# ==========================================================================

def roache(f1, f2, f3, r):
    """(classification, p, gci_fine).  f1 coarse -> f3 fine.

    The classification is decided BEFORE any order is computed, because an order
    read off a non-monotone triple is a number with no meaning that a reader
    will nonetheless remember."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0.0 and e32 == 0.0:
        return "EXACT", None, None
    if e21 == 0.0 or e32 == 0.0:
        return "STAGNANT", None, None
    s = e32 / e21
    if s < 0.0:
        return "OSCILLATORY", None, None
    if s >= 1.0:
        return "DIVERGENT", None, None
    p = math.log(abs(e21 / e32)) / math.log(r)
    gci = FS * abs(e32 / f3) / (r ** p - 1.0) if f3 != 0.0 else None
    return "CONVERGING", p, gci


# ==========================================================================
# THE FORGE -- used ONLY by --selftest.  It writes a synthetic case that
# RESEMBLES THE SITUATION: the module region carries 8 stacked solid cells at
# the registered pitch, the coolant carries an `outlet` and an `inlet`, and the
# inlet is written in the EXACT form OpenFOAM writes for a fixedValue patch --
# copied from a staged 0.orig when one is on disk, so the fixture cannot drift
# away from the artifact.
# ==========================================================================

HDR = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
       "    object %s;\n}\n")


def _write_boxmesh(pm, boxes, patches):
    """A polyMesh of DISCONNECTED axis-aligned hexes: 8 points and 6 faces each,
    every face on a boundary.  `patches` maps name -> predicate(cell, face_key).
    """
    os.makedirs(pm, exist_ok=True)
    pts, faces, owner = [], [], []
    keyed = []
    for c, (lo, hi) in enumerate(boxes):
        base = len(pts)
        for k in range(8):
            pts.append((lo[0] if not (k & 1) else hi[0],
                        lo[1] if not (k & 2) else hi[1],
                        lo[2] if not (k & 4) else hi[2]))
        quads = (("xlo", (0, 2, 6, 4)), ("xhi", (1, 5, 7, 3)),
                 ("ylo", (0, 4, 5, 1)), ("yhi", (2, 3, 7, 6)),
                 ("zlo", (0, 1, 3, 2)), ("zhi", (4, 6, 7, 5)))
        for key, q in quads:
            keyed.append((c, key, [base + i for i in q]))
    order = []
    for name, pred in patches:
        sel = [i for i, (c, key, _) in enumerate(keyed) if pred(c, key)]
        order.append((name, sel))
    seen = set()
    for _, sel in order:
        for i in sel:
            if i in seen:
                raise AssertionError("forge: face %d in two patches" % i)
            seen.add(i)
    if len(seen) != len(keyed):
        raise AssertionError("forge: %d faces unassigned" % (len(keyed) - len(seen)))
    bnd, start = [], 0
    for name, sel in order:
        for i in sel:
            c, _, f = keyed[i]
            faces.append(f)
            owner.append(c)
        bnd.append((name, start, len(sel)))
        start += len(sel)
    with open(os.path.join(pm, "points"), "w") as fh:
        fh.write(HDR % ("vectorField", "points"))
        fh.write("%d\n(\n" % len(pts))
        for p in pts:
            fh.write("(%.12g %.12g %.12g)\n" % p)
        fh.write(")\n")
    with open(os.path.join(pm, "faces"), "w") as fh:
        fh.write(HDR % ("faceList", "faces"))
        fh.write("%d\n(\n" % len(faces))
        for f in faces:
            fh.write("4(%d %d %d %d)\n" % tuple(f))
        fh.write(")\n")
    with open(os.path.join(pm, "owner"), "w") as fh:
        fh.write(HDR % ("labelList", "owner"))
        fh.write("%d\n(\n%s\n)\n" % (len(owner), "\n".join(map(str, owner))))
    with open(os.path.join(pm, "boundary"), "w") as fh:
        fh.write(HDR % ("polyBoundaryMesh", "boundary"))
        fh.write("%d\n(\n" % len(bnd))
        for name, s, k in bnd:
            fh.write("    %s\n    {\n        type patch;\n"
                     "        nFaces %d;\n        startFace %d;\n    }\n"
                     % (name, k, s))
        fh.write(")\n")


def _write_scalar_field(path, obj, vals, patch_specs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HDR % ("volScalarField", obj))
        fh.write("dimensions      [0 0 0 1 0 0 0];\n\n")
        fh.write("internalField   nonuniform List<scalar>\n")
        fh.write("%d\n(\n" % len(vals))
        fh.write("\n".join("%.12g" % v for v in vals))
        fh.write("\n)\n;\n\nboundaryField\n{\n")
        for name, spec in patch_specs:
            fh.write("    %s\n    {\n        type            fixedValue;\n"
                     % name)
            if isinstance(spec, list):
                fh.write("        value           nonuniform List<scalar>\n")
                fh.write("%d\n(\n" % len(spec))
                fh.write("\n".join("%.12g" % v for v in spec))
                fh.write("\n)\n;\n")
            else:
                fh.write("        value           uniform %.12g;\n" % spec)
            fh.write("    }\n")
        fh.write("}\n")


NX_F, NY_F = 2, 2                 # forge: sub-cells per solid cell


def forge_case(root, name, out_offset=0.0, peak_offset=0.0, hflux_scale=1.0,
               uniform_inlet=True, times=WRITE_TIMES, legs=(0.0, 70.0)):
    """Write a synthetic but STRUCTURALLY REAL case.  Returns its path."""
    case = os.path.join(root, name)
    mboxes, cboxes = [], []
    for j in range(N_CELLS):
        y0 = j * PITCH
        for a in range(NX_F):
            for b in range(NY_F):
                mboxes.append(((CELL_LX * a / NX_F, y0 + CELL_LY * b / NY_F, 0.0),
                               (CELL_LX * (a + 1) / NX_F,
                                y0 + CELL_LY * (b + 1) / NY_F, DEPTH)))
        if j < N_CELLS - 1:
            for a in range(NX_F):
                cboxes.append(((CELL_LX * a / NX_F, y0 + CELL_LY, 0.0),
                               (CELL_LX * (a + 1) / NX_F,
                                y0 + CELL_LY + GAP, DEPTH)))
    _write_boxmesh(os.path.join(case, "constant", "module", "polyMesh"),
                   mboxes, [("module_to_coolant", lambda c, k: k == "yhi"),
                            ("walls", lambda c, k: k != "yhi")])
    ncool = len(cboxes)

    def _is_out(c, k):
        lo, hi = cboxes[c]
        return k == "xhi" and abs(hi[0] - CELL_LX) < 1e-12

    def _is_in(c, k):
        lo, hi = cboxes[c]
        return k == "xlo" and abs(lo[0]) < 1e-12
    _write_boxmesh(os.path.join(case, "constant", "coolant", "polyMesh"),
                   cboxes, [("outlet", _is_out), ("inlet", _is_in),
                            ("coolant_to_module",
                             lambda c, k: not _is_out(c, k) and not _is_in(c, k))])
    nout = sum(1 for c in range(ncool) for k in ("xhi",) if _is_out(c, k))
    nin = sum(1 for c in range(ncool) for k in ("xlo",) if _is_in(c, k))

    for t in times:
        frac = t / T_END
        mvals, cvals = [], []
        for i, (lo, hi) in enumerate(mboxes):
            j = int(math.floor(0.5 * (lo[1] + hi[1]) / PITCH))
            mvals.append(T_INIT + 8.0 * frac + 0.10 * j
                         + (peak_offset if j == N_CELLS - 1 else 0.0))
        for _ in cboxes:
            cvals.append(T_INIT + 2.0 * frac)
        _write_scalar_field(os.path.join(case, "%g" % t, "module", "T"), "T",
                            mvals, [("module_to_coolant", T_INIT + 8.0 * frac),
                                    ("walls", T_INIT)])
        outv = [T_INIT + 2.0 * frac + out_offset + 0.001 * i
                for i in range(nout)]
        inspec = T_INIT if uniform_inlet else [T_INIT] * nin
        _write_scalar_field(os.path.join(case, "%g" % t, "coolant", "T"), "T",
                            cvals, [("outlet", outv), ("inlet", inspec),
                                    ("coolant_to_module", T_INIT + 2.0 * frac)])
    for lo in legs:
        d = os.path.join(case, "postProcessing", "outlet_hflux", "%g" % lo)
        os.makedirs(d, exist_ok=True)
        hi = T_END if lo == max(legs) else min(x for x in legs if x > lo)
        step = 0.1 if lo > 0 else 0.02
        with open(os.path.join(d, "surfaceFieldValue.dat"), "w") as fh:
            fh.write("# Region type : patch outlet\n# Time\tweightedSum(T)\n")
            k, tt = 0, lo
            while tt <= hi + 1e-9:
                fh.write("%.6g\t%.10g\n"
                         % (tt, hflux_scale * (MDOT_IN * (2.0 + 6.0 * tt / T_END))))
                k += 1
                tt = lo + k * step
    return case


# ==========================================================================
# GRADING
# ==========================================================================

def _fmt(x, w=".6e"):
    return "n/a" if x is None else format(x, w)


def grade(root, repo=None):
    sha = freeze_check(repo)
    out = []
    out.append("=" * 74)
    out.append("T25R3 -- COMPARATOR.  Registration blob %s" % sha)
    out.append("Gate tau = %.6e K.  Reported second tier = %.6e K "
               "(GATES NOTHING)." % (TAU, TIER2))
    out.append("Composed binding iterative requirement (Amendment A1.2): "
               "%.6e K" % (GI_RATIO * TAU))
    out.append("=" * 74)

    dirs = {}
    for r in RUNS:
        d = os.path.join(root, r)
        if not os.path.isdir(d):
            refuse("run directory %s is absent. The registered run set of §2 is "
                   "CLOSED at six runs and this comparator grades nothing from a "
                   "partial set." % d)
        dirs[r] = d

    # ---- instrument admission FIRST.  No physics number before this. ----
    out.append("\nINSTRUMENT ADMISSION -- planted controls (rule 3)")
    ctl = {}
    ref = dirs["S2"]
    ctl["Q1_outlet"] = planted_zero_control(
        ref, "Q1 outlet area-mean T",
        lambda d: read_patch_T(d, T_END, "outlet"),
        lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"), "outlet", m,
                                      len(_mesh(d, "coolant")
                                          .patch_face_areas("outlet"))),
        os.path.join("%g" % T_END, "coolant", "T"))
    ctl["Q2_cell"] = planted_zero_control(
        ref, "Q2 per-cell volume average",
        lambda d: max(read_cell_T(d, T_END)),
        lambda d, m: _plant_hottest_module_cell(d, T_END, m),
        os.path.join("%g" % T_END, "module", "T"))
    ctl["C3_inlet"] = planted_zero_control(
        ref, "C3 inlet patch T (the §10.2 reader)",
        lambda d: read_inlet_T(d, T_END),
        lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"), "inlet", m,
                                      len(_mesh(d, "coolant")
                                          .patch_face_areas("inlet"))),
        os.path.join("%g" % T_END, "coolant", "T"))
    dat = _dat_path(ref, "outlet_hflux")[-1]
    ctl["Q0_hflux"] = planted_zero_control(
        ref, "Q0 outlet enthalpy-flux instrument",
        lambda d: read_hflux_point(d),
        lambda d, m: _plant_dat_all(
            os.path.join(d, os.path.relpath(dat, ref)), m),
        os.path.relpath(dat, ref))
    for k, v in ctl.items():
        out.append("  %-12s SEEN.  floor %.6e   read at PLANT %.6e   "
                   "planted into %d locations"
                   % (k, v["floor"], v["at_plant"], v["n_planted"]))

    # ---- the quantities ----
    Q0 = {r: read_Q0(dirs[r]) for r in RUNS}
    Q1 = {r: read_Q1_history(dirs[r]) for r in RUNS}
    Q2 = {r: read_Q2_peaks(dirs[r]) for r in RUNS}

    def d1(a, b):
        return max(abs(x - y) for x, y in zip(Q1[a], Q1[b]))

    def d2(a, b):
        return max(abs(x - y) for x, y in zip(Q2[a], Q2[b]))

    def d0(a, b):
        return abs(Q0[a] - Q0[b])

    # ---- G-I, BEFORE any order is read (§7.3, §7.6 clause 1) ----
    out.append("\nG-I -- the prerequisite (Sanaa §0.2 as a gate)")
    gi = {}
    for lad, (a, b) in (("space", ("S3", "S2")), ("time", ("T4", "T2"))):
        rows, ok = [], True
        for nm, f in (("Q1", d1), ("Q2", d2), ("Q0", d0)):
            it, mesh_d = f("W30", "S2"), f(a, b)
            lim = GI_RATIO * mesh_d
            good = it <= lim
            ok = ok and good
            rows.append((nm, it, mesh_d, lim, good))
        gi[lad] = ok
        out.append("  %s ladder: %s" % (lad, "PASS" if ok else "FAIL"))
        for nm, it, md, lim, good in rows:
            out.append("    %-3s iterative |W30-S2| = %.6e   level gap = %.6e   "
                       "limit = %.6e   %s"
                       % (nm, it, md, lim, "ok" if good else "OVER"))

    # ---- Roache, on Q0 alone (§7.1, §8) ----
    out.append("\nROACHE -- classification decided BEFORE any order is read")
    tri = {}
    for lad, ids, r in (("space", SPACE_TRIPLE, R_SPACE),
                        ("time", TIME_TRIPLE, R_TIME)):
        cls, p, gci = roache(*[Q0[i] for i in ids], r)
        tri[lad] = (cls, p, gci)
        out.append("  %-5s %s  Q0 = %s  r = %.4f  class = %s  p = %s  GCI = %s"
                   % (lad, "/".join(ids),
                      ", ".join("%.9e" % Q0[i] for i in ids), r, cls,
                      _fmt(p, ".4f"), _fmt(gci, ".4e")))
        if cls == "CONVERGING":
            out.append("        p band [%.1f, %.1f] (formal order 1: Euler in "
                       "time, upwind in space, §4.2): %s"
                       % (P_LO, P_HI,
                          "IN BAND" if P_LO <= p <= P_HI else "OUT OF BAND"))
        else:
            out.append("        NO GCI IS QUOTED: the three values are not "
                       "monotone and an order read off them has no meaning.")

    # ---- G-S and G-T (§7.4) ----
    out.append("\nG-S / G-T -- Sanaa's gate, the two finest levels of each ladder")
    gates = {}
    for lad, a, b in (("G-S", "S3", "S2"), ("G-T", "T4", "T2")):
        v1, v2 = d1(a, b), d2(a, b)
        ok = v1 <= TAU and v2 <= TAU
        gates[lad] = ok
        out.append("  %s (%s vs %s): Q1 %.6e   Q2 %.6e   tau %.6e  -> %s"
                   % (lad, a, b, v1, v2, TAU, "PASS" if ok else "GATE FAIL"))
        out.append("      second tier %.6e (REPORTED, GATES NOTHING): "
                   "Q1 %s, Q2 %s" % (TIER2,
                                     "under" if v1 <= TIER2 else "OVER",
                                     "under" if v2 <= TIER2 else "OVER"))

    # ---- C1, C2, C3 ----
    out.append("\nSUPPORTING CHECKS")
    c_ok = True
    for r in RUNS:
        stored = read_stored(dirs[r], T_END, "module") \
            + read_stored(dirs[r], T_END, "coolant")
        conv = Q0[r] - CP_AIR * MDOT_IN * T_INIT * T_END
        res = abs(stored + conv - E_GEN) / E_GEN
        good = res <= C1_TOL
        c_ok = c_ok and good
        out.append("  C1 %-4s |stored + convected - E_gen|/E_gen = %.4e "
                   "(<= %.2e, E_gen = %.1f J RAMPED)  %s"
                   % (r, res, C1_TOL, E_GEN, "ok" if good else "FAIL"))
    for r in RUNS:
        bad = [t for t in WRITE_TIMES[1:]
               if read_patch_T(dirs[r], t, "outlet")
               <= read_inlet_T(dirs[r], t)]
        good = not bad
        c_ok = c_ok and good
        out.append("  C3 %-4s outlet > inlet at every written t > 0: %s%s"
                   % (r, "ok" if good else "FAIL",
                      "" if good else " (first failure t = %g)" % bad[0]))

    # ---- THE VERDICT, in the registered order (§7.6) ----
    out.append("\n" + "=" * 74)
    out.append("VERDICT")
    for lad, gate in (("space", "G-S"), ("time", "G-T")):
        cls = tri[lad][0]
        if not gi[lad]:
            v = "NOT A RESULT -- G-I failed on the %s ladder (§7.6 clause 1). " \
                "The observed order is noise, not discretisation." % lad
        elif cls != "CONVERGING":
            v = "NOT A RESULT -- the %s triple is %s (rule 5 clause 2). The " \
                "value is printed above and gates nothing." % (lad, cls)
        elif not c_ok:
            v = "NOT A RESULT -- a supporting check failed (§7.6 clause 3)."
        else:
            v = "PASS" if gates[gate] else "GATE FAIL"
        out.append("  %-5s ladder (%s): %s" % (lad, gate, v))
    out.append("=" * 74)
    print("\n".join(out))
    return 0


# ==========================================================================
# SELFTEST
# ==========================================================================

def _refuses(fn):
    try:
        fn()
    except SystemExit as e:
        return e.code == EXIT_REFUSE
    return False


REAL_ORIG_T = os.path.join(
    HERE, "..", "T25R2_MODULE_runs", "T25R2_L2", "0.orig", "coolant", "T")


def selftest():
    clear_pycache()
    fails = [0]

    def chk(name, cond):
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails[0] += 1

    tmp = tempfile.mkdtemp(prefix="t25R3self_")
    try:
        print("--- §10.2 THE MUST-FIX, DRIVEN BOTH WAYS ---")
        # The fixture is COPIED FROM THE REAL STAGED 0.orig, never hand-written.
        real = os.path.abspath(REAL_ORIG_T)
        chk("the real staged 0.orig/coolant/T is on disk to copy from",
            os.path.isfile(real))
        fix = os.path.join(tmp, "T_real")
        shutil.copyfile(real, fix)
        txt = open(fix).read()
        chk("the copied fixture carries `value uniform 293` on `inlet` -- the "
            "EXACT form OpenFOAM writes for a fixedValue patch",
            re.search(r"inlet\s*\{[^}]*value\s+uniform\s+293", txt) is not None)
        chk("the copied fixture carries NO nonuniform list on `inlet` "
            "(the forged fixture that hid the T25R2 defect did)",
            re.search(r"inlet\s*\{[^}]*nonuniform", txt) is None)

        # DIRECTION 1 -- the repaired reader SEES it.
        lines, kind, first, n = patch_value_spec(fix, "inlet")
        chk("DIRECTION 1: the repaired reader parses the uniform form "
            "(kind=%r)" % kind, kind == "uniform")
        vals = patch_values(fix, "inlet", 7)
        chk("DIRECTION 1: it expands to the face count and reads 293.0 "
            "(got %r)" % (vals[:1],), vals == [293.0] * 7)

        # DIRECTION 2 -- the LEGACY reader still REFUSES on the same bytes.
        chk("DIRECTION 2: analyse_t25R2's reader, carried verbatim, still "
            "REFUSES these exact bytes -- the defect was real and this is what "
            "removes it",
            _refuses(lambda: _legacy_patch_value_window(fix, "inlet")))
        # The DIRECTION 2 control is deferred to after the forge, because it
        # needs a patch written in the NONUNIFORM form and the real staged
        # 0.orig writes EVERY patch uniform -- which is itself the measurement
        # that says how wide the T25R2 defect was.
        # SCOPE, MEASURED ON THE ARTIFACT GRADING ACTUALLY READS -- a written
        # time directory, not 0.orig.  An earlier draft of this check measured
        # 0.orig and concluded the defect hit every patch; that was TRUE of
        # 0.orig and FALSE of the graded artifact, because 0.orig writes
        # `$internalField` on the outlet and the coupled patch while the solver
        # writes real nonuniform lists there.  T25R2 §10's scope claim was
        # exactly right and this check now says so instead of inflating it.
        real_t = os.path.join(HERE, "..", "T25R2_MODULE_runs", "T25R2_L1",
                              "900", "coolant", "T")
        if os.path.isfile(real_t):
            rt = os.path.join(tmp, "T_written")
            shutil.copyfile(real_t, rt)
            chk("SCOPE, measured on a REAL WRITTEN TIME (T25R2_L1/900): the "
                "legacy reader refuses ONLY `inlet` and reads `outlet` and "
                "`coolant_to_module` -- T25R2 §10's scope was right, and this "
                "check does not inflate it",
                _refuses(lambda: _legacy_patch_value_window(rt, "inlet"))
                and not _refuses(lambda: _legacy_patch_value_window(rt, "outlet"))
                and not _refuses(lambda: _legacy_patch_value_window(
                    rt, "coolant_to_module")))
            chk("and the REPAIRED reader reads all three on that same file",
                patch_value_spec(rt, "inlet")[1] == "uniform"
                and patch_value_spec(rt, "outlet")[1] == "nonuniform"
                and patch_value_spec(rt, "coolant_to_module")[1] == "nonuniform")
            chk("C3 IS THE CHECK THAT WOULD HAVE DIED: the inlet is uniform at "
                "a written time, so the legacy reader refused at EVERY t and "
                "C3 was NOT A RESULT on an instrument refusal",
                _refuses(lambda: _legacy_patch_value_window(rt, "inlet")))
        else:
            chk("the real written-time artifact is on disk to measure scope on",
                False)

        print("\n--- THE PLANTED CONTROL, DRIVEN BOTH WAYS ---")
        c_uni = forge_case(tmp, "UNI", uniform_inlet=True, times=(0.0, T_END))
        c_non = forge_case(tmp, "NON", uniform_inlet=False, times=(0.0, T_END))
        nin = len(_mesh(c_uni, "coolant").patch_face_areas("inlet"))
        nout = len(_mesh(c_uni, "coolant").patch_face_areas("outlet"))

        r = planted_zero_control(
            c_uni, "inlet(uniform)", lambda d: read_inlet_T(d, T_END),
            lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"),
                                          "inlet", m, nin),
            os.path.join("%g" % T_END, "coolant", "T"))
        chk("POSITIVE: the control SEES the plant through a UNIFORM inlet "
            "(read at PLANT = %.6e, floor %.6e; relative error %.2e against "
            "the registered 1e-9 slack)"
            % (r["at_plant"], r["floor"], abs(r["at_plant"] / PLANT - 1.0)),
            r["passed"] and abs(r["at_plant"] / PLANT - 1.0) <= PLANT_REL_SLACK)
        r = planted_zero_control(
            c_non, "inlet(nonuniform)", lambda d: read_inlet_T(d, T_END),
            lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"),
                                          "inlet", m, nin),
            os.path.join("%g" % T_END, "coolant", "T"))
        chk("POSITIVE: the same control SEES the plant through a NONUNIFORM "
            "inlet -- both forms, one reader", r["passed"])
        chk("DIRECTION 2 control: on a patch written NONUNIFORM the legacy "
            "reader does NOT refuse -- so its refusal above is about the FORM, "
            "not about the file or the patch name",
            not _refuses(lambda: _legacy_patch_value_window(
                fld(c_non, T_END, "coolant", "T"), "inlet")))
        chk("DIRECTION 1 control: the repaired reader reads BOTH forms to the "
            "same value on the same physical patch",
            read_inlet_T(c_uni, T_END) == read_inlet_T(c_non, T_END))

        r = planted_zero_control(
            c_uni, "outlet", lambda d: read_patch_T(d, T_END, "outlet"),
            lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"),
                                          "outlet", m, nout),
            os.path.join("%g" % T_END, "coolant", "T"))
        chk("POSITIVE: the Q1 outlet reader sees its plant", r["passed"])
        r = planted_zero_control(
            c_uni, "Q2", lambda d: max(read_cell_T(d, T_END)),
            lambda d, m: _plant_hottest_module_cell(d, T_END, m),
            os.path.join("%g" % T_END, "module", "T"))
        chk("POSITIVE: the Q2 per-cell reader sees its plant", r["passed"])

        # NEGATIVE ARM 1: a BLIND reader must make the control REFUSE.
        chk("NEGATIVE: a BLIND reader (returns a constant) makes the control "
            "REFUSE -- the control is not vacuous",
            _refuses(lambda: planted_zero_control(
                c_uni, "blind", lambda d: 1.0,
                lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"),
                                              "outlet", m, nout),
                os.path.join("%g" % T_END, "coolant", "T"))))
        # NEGATIVE ARM 2: the mag/N failure mode is LIVE and clause 5 catches it.
        chk("NEGATIVE: planting ONE mesh cell instead of the whole module cell "
            "under-shifts the volume average and clause 5 REFUSES it -- the "
            "mag/N failure mode is live, not theoretical",
            _refuses(lambda: planted_zero_control(
                c_uni, "one-cell", lambda d: max(read_cell_T(d, T_END)),
                lambda d, m: _plant_internal_one(
                    fld(d, T_END, "module", "T"), m),
                os.path.join("%g" % T_END, "module", "T"))))
        # NEGATIVE ARM 3: an OVER-READING reader must REFUSE under the newly
        # two-sided clause 5.  analyse_t25R2's one-sided clause would have
        # PASSED this reader, which is why the bound was made two-sided.
        chk("NEGATIVE: a reader that OVER-reports the plant 100x REFUSES under "
            "the two-sided clause 5 (T25R2's one-sided clause passed it)",
            _refuses(lambda: planted_zero_control(
                c_uni, "over", lambda d: 100.0 * read_patch_T(d, T_END, "outlet"),
                lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"),
                                              "outlet", m, nout),
                os.path.join("%g" % T_END, "coolant", "T"))))
        # NEGATIVE ARM 4: a NOISY reader must make the control REFUSE.
        st = [0.0]
        NOISE = 1e-9          # representable: eps*293 is ~6.5e-14, so this
        #                       perturbation SURVIVES the addition.  The first
        #                       draft used 1e-18, which did not, so the
        #                       "noisy" reader was bit-identical and the
        #                       negative arm was vacuous.
        chk("the noise fixture is actually representable at 293 K "
            "(a fixture that does not resemble the situation proves nothing)",
            (293.0 + NOISE) != 293.0)

        def noisy(d):
            st[0] += NOISE
            return read_patch_T(d, T_END, "outlet") + st[0]
        chk("NEGATIVE: a NOISY reader (two reads of identical bytes differ) "
            "makes the control REFUSE at bitwise zero",
            _refuses(lambda: planted_zero_control(
                c_uni, "noisy", noisy,
                lambda d, m: _plant_patch_all(fld(d, T_END, "coolant", "T"),
                                              "outlet", m, nout),
                os.path.join("%g" % T_END, "coolant", "T"))))

        print("\n--- ROACHE, DRIVEN BOTH WAYS ---")
        chk("CONVERGING triple at r=1.5 recovers p=2 exactly "
            "(1.0, 1.0+1/2.25, 1.0+1/2.25/2.25 is r^-p with p=2)",
            abs(roache(0.0, 1.0, 1.0 + 1.0 / 2.25, 1.5)[1] - 2.0) < 1e-9)
        chk("a DIVERGENT triple is classified DIVERGENT and yields NO p",
            roache(0.0, 1.0, 3.0, 1.5)[0] == "DIVERGENT"
            and roache(0.0, 1.0, 3.0, 1.5)[1] is None)
        chk("an OSCILLATORY triple is classified OSCILLATORY and yields NO p",
            roache(0.0, 1.0, 0.5, 1.5)[0] == "OSCILLATORY")
        chk("a STAGNANT triple is classified STAGNANT and yields NO p",
            roache(0.0, 1.0, 1.0, 1.5)[0] == "STAGNANT")
        chk("an EXACT triple is classified EXACT", roache(1.0, 1.0, 1.0, 1.5)[0]
            == "EXACT")
        chk("first-order convergence at r=1.5 gives p=1, INSIDE the registered "
            "band [0.5, 1.5]",
            abs(roache(0.0, 1.0, 1.0 + 1.0 / 1.5, 1.5)[1] - 1.0) < 1e-9)
        chk("second-order convergence gives p=2, OUTSIDE the band this rung "
            "registers -- the band would catch a scheme that is not what "
            "fvSchemes says it is",
            not (P_LO <= roache(0.0, 1.0, 1.0 + 1.0 / 2.25, 1.5)[1] <= P_HI))

        print("\n--- THE COMPOSED BINDING CONSTRAINT (Amendment A1.2) ---")
        chk("G-I ratio x tau = 1.000e-02 K, which is TIGHTER than the "
            "2.315190e-02 K that failed T25R2",
            abs(GI_RATIO * TAU - 1.0e-02) < 1e-15
            and GI_RATIO * TAU < 2.315190e-02)
        chk("and tighter than the predecessor's own 1.234e-02 K threshold",
            GI_RATIO * TAU < TIER2)

        print("\n--- STRUCTURAL REFUSALS ---")
        chk("a missing time directory REFUSES rather than interpolating",
            _refuses(lambda: tdir(c_uni, 12345.0)))
        chk("a postProcessing directory with two .dat files REFUSES (a restart "
            "collision renames these and a glob would take the wrong one)",
            _refuses(lambda: (_touch2(c_uni), _dat_path(c_uni, "outlet_hflux"))))
        chk("freeze_check REFUSES when the frozen document is not committed",
            _refuses(lambda: freeze_check(tmp)))

        print("\n--- LEG COVERAGE (§6.3) ---")
        rows = _read_dat(_dat_path(c_non, "outlet_hflux"))
        chk("the two legs' .dat files concatenate to cover [0, 900] with no gap",
            abs(rows[-1][0] - T_END) < 1e-6
            and max(rows[i + 1][0] - rows[i][0]
                    for i in range(len(rows) - 1)) <= 0.1 + 1e-9)
        chk("a gap between legs REFUSES",
            _refuses(lambda: _leg_coverage_check(
                [(0.0, 1.0), (0.5, 1.0), (900.0, 1.0)], "forged")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL",
                                         fails[0]))
    return 0 if not fails[0] else 1


def _touch2(case):
    d = os.path.join(case, "postProcessing", "outlet_hflux", "0")
    open(os.path.join(d, "surfaceFieldValue_0.dat"), "w").write("# x\n")


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--grade" in argv:
        return grade(argv[argv.index("--grade") + 1])
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
