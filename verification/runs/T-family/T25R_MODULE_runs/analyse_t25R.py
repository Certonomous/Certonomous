#!/usr/bin/env python3
"""T25R COMPARATOR -- 8-cell aviation battery module with RESOLVED cooling
channels, true transient conjugate.

Gates, thresholds, caps and labels are registered at
`docs/campaigns/T-family/T25R_PREREGISTRATION.md` and FROZEN by its commit sha.
This file is committed in the same commit and BEFORE ANY COMPUTE -- no solver,
no blockMesh, no checkMesh has run for T25R.  It therefore cannot have been
shaped by a result it had already seen (CLAUDE.md rule 2).

=====================================================================
WHAT THIS COMPARATOR DOES NOT DO, AND WILL NOT BE MADE TO DO
=====================================================================

*** TWO MESH LEVELS ARE TWO POINTS.  NO LADDER IS REGISTERED. ***
No observed order, no GCI and no Roache classification
(CONVERGING / DIVERGENT / STAGNANT / OSCILLATORY / EXACT) is computed, quoted
or quotable from this artifact.  Two points cannot measure an order and cannot
yield a GCI.  CLAUDE.md rule 5 is not weakened by that: it governs a GRID
TRIPLE, and this rung produces none.  Section 6.3 of the frozen document
registers the mesh pair and the step pair as SENSITIVITY DIFFERENCES and
nothing else.  Precedent for saying so on the artifact's own face:
`analyse_t23.py:477`, `analyse_t24.py:744`.

THIS FAMILY'S MOST REPEATED FAILURE IS SMUGGLING AN ORDER OUT OF TWO POINTS.
There is no code path in this file that computes one.

*** T25R INHERITS NO PASS FROM T20. ***  Section 6.1: the T20 exact gate is the
registered V-tier for CASE 4 and it HAS NOT DISCHARGED --
`T20_P10_CONDITION_iii_MEASUREMENT.md:9` states "T20 remains NOT A RESULT on
its own registered terms".  The citation is a POINTER, not a proof, and this
file prints that on every invocation so no downstream reader picks up the
citation without the caveat.

*** A SMALL DIFFERENCE BETWEEN TWO POINTS IS CONSISTENT WITH CONVERGENCE AND IS
NOT EVIDENCE OF IT. ***  The sensitivity panels say so in those words.

=====================================================================
THE INSTRUMENT-ADMISSION CONTROL (CLAUDE.md rule 3, section 7.1)
=====================================================================
A zero from a reader not shown able to see a non-zero is not evidence.  Every
reader carries a planted-perturbation control with all nine registered clauses,
following `verification/runs/T-family/T24_runs/analyse_t24.py:459-530`:

  1. COPY FIRST into scratch, with a REFUSAL if the scratch path resolves
     INSIDE the case.  The case is never written to.
  2. NEGATIVE ARM at bitwise 0.0.  NO absolute tolerance anywhere in it.
  3. POSITIVE ARM: a MEASURED magnitude ladder with an epsilon-free floor.
  4. REFUSE IF BLIND.
  5. The ONLY sizing tolerance, and it is RELATIVE: got >= PLANT*(1-1e-9).
     analyse_t3.py:327's ABSOLUTE `seen >= PLANT - 1e-15` is EXPRESSLY NOT
     ADOPTED: at this magnitude an absolute epsilon is decided by rounding
     wiggle rather than by whether the reader saw the plant.
  6. PLANT is IMPORTED from scripts/roache_triple.py and NEVER redefined.
  7. Plants are written BY LINE INDEX inside a window taken from the field's
     OWN HEADER.  Nothing is located by value.  A patch plant writes EVERY face
     so the expected shift is EXACTLY `mag`, never mag/N.
  8. The case bytes are compared before and after; scratch is removed in a
     `finally`.
  9. __pycache__ is cleared first (stale bytecode INVERTS a mutation control).

A REFUSAL ON ANY READER MAKES THE WHOLE RUNG `NOT A RESULT`.

=====================================================================
COMPLETION IS DELEGATED AND NEVER REIMPLEMENTED
=====================================================================
`mark_done_t25R.py` decides CLAUDE.md rule 4.  This file CALLS it.  There is no
second copy of the completion rule here, and a run without a DONE marker from
that instrument has its numbers withheld, not printed with a caveat.

NO `assert` (L-332): behaviour is identical under `python3 -O`.

Usage:
    python3 analyse_t25R.py [CASE ...] [--root DIR] [--json OUT]
    python3 analyse_t25R.py --selftest
Exit: 0 graded, 1 a gate failed or a row is NOT A RESULT, 2 REFUSAL.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)
import roache_triple as RT                                      # noqa: E402
import mark_done_t25R as MD                                     # noqa: E402

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# ---- section 7.1 clause 6: IMPORTED, NEVER REDEFINED. ---------------------
PLANT = RT.PLANT                          # 1.234e-03 K
LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)
PLANT_REL_SLACK = 1e-9                    # clause 5: the ONLY sizing tolerance

FROZEN_DOC = "docs/campaigns/T-family/T25R_PREREGISTRATION.md"

# ---- section 1, THE REGISTERED RUN SET.  Three, named, closed. ------------
CASES = ("T25R_L1", "T25R_L2", "T25R_L2_DT025")
LEVEL = {"T25R_L1": "L1", "T25R_L2": "L2", "T25R_L2_DT025": "L2"}
DELTAT = {"T25R_L1": 0.5, "T25R_L2": 0.5, "T25R_L2_DT025": 0.25}
PRIMARY = "T25R_L2"                       # section 5.3: D1/D3 read here
MESH_PAIR = ("T25R_L1", "T25R_L2")        # section 6.3
STEP_PAIR = ("T25R_L2", "T25R_L2_DT025")  # section 6.3

# ---- section 2.1, GEOMETRY.  Every number is the frozen document's. -------
N_CELLS = 8
CELL_LX, CELL_LY, GAP, DEPTH = 0.100, 0.030, 0.003, 1.000
PITCH = CELL_LY + GAP                     # 0.033 m
V_CELL = CELL_LX * CELL_LY * DEPTH        # 3.000e-03 m3
X_BAND = 0.010                            # section 5.3 up/down band width

# ---- section 4.2, THE LOAD.  C-RATE FIRST. -------------------------------
Q_TAKEOFF, Q_CRUISE = 70000.0, 2800.0     # W/m3
T_PULSE, T_END = 60.0, 900.0              # s
RAMP_LO, RAMP_HI = 59.999, 60.000         # section 4.5, the 1 ms ramp
T_INIT = 293.0                            # K
RHO_S, CP_S = 2500.0, 1000.0
CP_AIR = 1005.0
E_GEN = N_CELLS * V_CELL * (Q_TAKEOFF * T_PULSE + Q_CRUISE * (T_END - T_PULSE))

# ---- THE REGISTERED THRESHOLDS.  Transcribed from the frozen document. ----
ENERGY_BAND = 0.020                       # 6.2: |R|/E_gen <= 2.0 %
OUTER_FAIL_FRAC = 0.050                   # 3.5: > 5.0 % of steps -> NOT A RESULT
# Section 3.5, THE REGISTERED RESIDUAL THRESHOLDS on the LAST outer sweep of a
# time step.  Fluid 1e-6 and solid 1e-8 are the directive's own numbers (4.5).
RESID_GATE = {"p_rgh": 1e-6, "Ux": 1e-6, "Uy": 1e-6, "h": 1e-8}
D3_FLOOR = 10.0 * PLANT                   # 5.3: 1.234e-02 K
MESH_MAXNONORTH, MESH_MAXSKEW = 70.0, 4.0  # 2.4
PLANT10_PCT = 0.10                        # 6.2 planted +10 % source control

WRITE_TIMES = (0.0, 30.0, 60.0, 120.0, 300.0, 900.0)   # section 9

REGIONS = ("module", "coolant")
IFACE = {"module": "module_to_coolant", "coolant": "coolant_to_module"}


def refuse(msg):
    """REFUSES (exit 2) rather than degrades.  No soft path out."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def clear_pycache():
    """Clause 9.  A stale bytecode cache INVERTS a mutation control -- the
    clean arm fails and the mutated arm passes -- and PYTHONDONTWRITEBYTECODE
    does NOT fix it; the caches must be removed."""
    for d in (HERE, os.path.join(REPO, "scripts")):
        p = os.path.join(d, "__pycache__")
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)


# ==========================================================================
# THE FREEZE CHECK.  CLAUDE.md rule 2: verify the frozen file IS the file that
# ran, by hashing it against the committed blob.  A working-tree edit to the
# pre-registration after the freeze is caught HERE and REFUSED, not discovered
# later by a reader.
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
        refuse("%s is NOT COMMITTED at HEAD. CLAUDE.md rule 2 requires the "
               "pre-registration to be committed BEFORE compute, and the "
               "grading path is fixed at that commit. An uncommitted "
               "pre-registration has no evidentiary content." % FROZEN_DOC)
    committed = r.stdout.strip()
    if worktree != committed:
        refuse("THE FROZEN DOCUMENT HAS BEEN EDITED SINCE ITS COMMIT.\n"
               "  working tree blob : %s\n  HEAD blob         : %s\n"
               "Frozen files are never edited (CLAUDE.md rule 6). A departure "
               "lands as a DATED AMENDMENT APPENDED AT THE FOOT with a version "
               "bump, never as an in-place edit." % (worktree, committed))
    return committed


# ==========================================================================
# polyMesh.  Every cell of this mesh is an AXIS-ALIGNED BOX, so a cell's
# centroid is the mean of its bounding corners and its volume is the product of
# its extents -- EXACTLY, not approximately.  That boxness is CHECKED, not
# assumed: a cell whose vertex set is not the 8 corners of its bounding box is
# a REFUSAL, because every geometric number below would then be wrong in a way
# no threshold would catch.
# ==========================================================================

def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    return re.sub(r"//[^\n]*", " ", txt)


def _body(path):
    """The list body after the FoamFile header: (count, text-after-'(')."""
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
    pts = re.findall(r"\(\s*(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s*\)",
                     rest)
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
    """-> {patch: (startFace, nFaces)}."""
    n, rest = _body(path)
    out = {}
    for m in re.finditer(r"([A-Za-z_][\w.:-]*)\s*\{([^{}]*)\}", rest):
        blk = m.group(2)
        s = re.search(r"startFace\s+(\d+)\s*;", blk)
        f = re.search(r"nFaces\s+(\d+)\s*;", blk)
        if s and f:
            out[m.group(1)] = (int(s.group(1)), int(f.group(1)))
    if len(out) != n:
        refuse("%s declares %d patches and %d were parsed"
               % (path, n, len(out)))
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

        self.box, self.vol, self.cx, self.cy = [], [], [], []
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
                        refuse("%s cell %d is NOT an axis-aligned box (vertex "
                               "%r off both bounds in axis %d) -- the exact "
                               "centroid/volume path does not apply and this "
                               "reader REFUSES" % (region, c, p, k))
            d = [hi[k] - lo[k] for k in range(3)]
            if min(d) <= 0.0:
                refuse("%s cell %d has a non-positive extent %r" % (region, c, d))
            self.box.append((lo, hi))
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
# count, opening parenthesis -- never by a regex sweep and NEVER BY VALUE
# (clause 7).
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
        refuse("%s has %d internalField scalar-list headers, expected exactly "
               "1. A UNIFORM internalField here would mean the solver wrote a "
               "constant field, which is a finding, not a parse problem"
               % (path, len(idx)))
    first, n = _list_window(lines, idx[0], path)
    return lines, first, n


def patch_value_window(path, patch):
    """The `value` list of ONE boundaryField patch.  NEVER falls back to
    `refValue`: those are different quantities and a silent fallback is how a
    coupled-patch reader ends up reporting the neighbour's guess."""
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
               "reader will NOT fall back to refValue, which is a different "
               "quantity (section 7.2)" % (patch, path))
    first, n = _list_window(lines, vidx, path)
    return lines, first, n


def tdir(case_dir, t):
    """The written time directory for `t`, located by NAME, not by proximity."""
    for cand in ("%g" % t, "%.1f" % t, "%.2f" % t):
        p = os.path.join(case_dir, cand)
        if os.path.isdir(p):
            return p
    refuse("case %s has no time directory for t = %g -- section 9 registers "
           "writes every 5 s, so this time was registered and is absent"
           % (case_dir, t))


def fld(case_dir, t, region, name):
    return os.path.join(tdir(case_dir, t), region, name)


# ==========================================================================
# THE READERS (section 7.2).  Each is paired with a planter that writes into
# EXACTLY the artifact that reader reads.
# ==========================================================================

def _cell_of(mesh, i):
    """Which of the 8 module cells cell-index i belongs to, by its y centre."""
    j = int(math.floor(mesh.cy[i] / PITCH))
    if j < 0 or j >= N_CELLS:
        refuse("module cell %d has y centre %.6g, outside the 8 registered "
               "cell bands" % (i, mesh.cy[i]))
    lo = j * PITCH
    if not (lo - 1e-12 <= mesh.cy[i] <= lo + CELL_LY + 1e-12):
        refuse("module cell %d has y centre %.6g, which lies in the CHANNEL "
               "gap above cell %d -- the module region must carry no fluid "
               "cells" % (i, mesh.cy[i], j + 1))
    return j


def read_cell_T(case_dir, t, mesh=None):
    """Volume-averaged solid T of each of the 8 cells, K.  -> list of 8."""
    mesh = Mesh(case_dir, "module") if mesh is None else mesh
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


def read_updown(case_dir, t, mesh=None):
    """(T_up[8], T_dn[8]) -- volume averages over x in [0, 0.010] and
    [0.090, 0.100] (section 5.3)."""
    mesh = Mesh(case_dir, "module") if mesh is None else mesh
    p = fld(case_dir, t, "module", "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("module/T at t=%g holds %d values against %d mesh cells"
               % (t, n, mesh.n))
    up_n, up_d = [0.0] * N_CELLS, [0.0] * N_CELLS
    dn_n, dn_d = [0.0] * N_CELLS, [0.0] * N_CELLS
    for i in range(n):
        j = _cell_of(mesh, i)
        v, x = mesh.vol[i], mesh.cx[i]
        val = float(lines[first + i])
        if x <= X_BAND:
            up_n[j] += v * val
            up_d[j] += v
        elif x >= CELL_LX - X_BAND:
            dn_n[j] += v * val
            dn_d[j] += v
    if min(up_d) <= 0.0 or min(dn_d) <= 0.0:
        refuse("an upstream or downstream x-band is EMPTY in some cell -- the "
               "10 mm band is narrower than one mesh cell and D1/D3 cannot be "
               "evaluated on this level")
    return ([up_n[j] / up_d[j] for j in range(N_CELLS)],
            [dn_n[j] / dn_d[j] for j in range(N_CELLS)])


def read_patch_T(case_dir, t, patch, mesh=None):
    """Area-weighted mean coolant T on `patch`, K."""
    mesh = Mesh(case_dir, "coolant") if mesh is None else mesh
    p = fld(case_dir, t, "coolant", "T")
    lines, first, n = patch_value_window(p, patch)
    a = mesh.patch_face_areas(patch)
    if len(a) != n:
        refuse("patch %s: %d face areas against %d boundary values"
               % (patch, len(a), n))
    return sum(ai * float(lines[first + i]) for i, ai in enumerate(a)) / sum(a)


def read_spread(case_dir, t, mesh=None):
    v = read_cell_T(case_dir, t, mesh)
    return max(v) - min(v)


def read_stored(case_dir, t, region, mesh=None):
    """Stored sensible energy above T_INIT in `region`, J."""
    mesh = Mesh(case_dir, region) if mesh is None else mesh
    p = fld(case_dir, t, region, "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("%s/T at t=%g holds %d values against %d mesh cells"
               % (region, t, n, mesh.n))
    rc = RHO_S * CP_S if region == "module" else 1.2 * CP_AIR
    return sum(mesh.vol[i] * rc * (float(lines[first + i]) - T_INIT)
               for i in range(n))


# ==========================================================================
# THE PLANTERS.  BY LINE INDEX, inside a window from the field's own header.
# Nothing is located by value.  Each returns the count planted.
# ==========================================================================

_MESH_CACHE = {}


def _mesh(case_dir, region):
    k = (os.path.realpath(case_dir), region)
    if k not in _MESH_CACHE:
        _MESH_CACHE[k] = Mesh(case_dir, region)
    return _MESH_CACHE[k]


def _plant_hottest_module_cell(case_dir, t, mag):
    """Plant into EVERY mesh cell of the HOTTEST of the 8 module cells.

    CLAUSE 7, AND THE REASON IT IS WRITTEN THIS WAY.  Every solid reader in
    section 7.2 returns a VOLUME AVERAGE over one module cell.  Planting a
    single mesh cell would shift that average by mag*V_i/V_cell -- i.e. by
    mag/N -- and the control would then fail clause 5 for a reason that has
    nothing to do with whether the reader can see the plant.  Planting the
    WHOLE module cell makes the expected shift EXACTLY `mag`, which is the same
    correction analyse_t24.py:443 makes for its patch plant.  The module cell is
    chosen BY ITS VOLUME-AVERAGE RANK, never by locating a value in the file."""
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
    """Plant into ONE internalField cell -- the hottest.  Used ONLY as the
    NEGATIVE ARM of the selftest, to prove the mag/N failure mode is live."""
    lines, first, n = internal_window(path)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)
    open(path, "w").write("\n".join(lines))
    return 1


def _plant_internal_all(path, mag):
    lines, first, n = internal_window(path)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(path, "w").write("\n".join(lines))
    return n


def _plant_patch_all(path, patch, mag):
    """EVERY face, so the expected shift is EXACTLY `mag`, never mag/N."""
    lines, first, n = patch_value_window(path, patch)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(path, "w").write("\n".join(lines))
    return n


# ==========================================================================
# THE PLANTED-ZERO CONTROL -- all nine clauses.  REFUSES rather than degrades.
# ==========================================================================

def planted_zero_control(case_dir, label, reader, planter, target_rel):
    clear_pycache()                                       # clause 9
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="t25Rctl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    tgt = lambda d: os.path.join(d, target_rel)           # noqa: E731
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
        if os.path.realpath(dest).startswith(case_real + os.sep):
            refuse("control copy %s resolves INSIDE the case" % dest)
        if not os.path.isfile(tgt(dest)):
            refuse("%s: the control target %s is not in the copy"
                   % (label, target_rel))
        pristine = open(tgt(dest)).read()

        # CLAUSE 2: NEGATIVE ARM, THRESHOLD EXACTLY ZERO, NO TOLERANCE.
        a = reader(dest)
        b = reader(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r, and clause 2 registers the "
                   "threshold as bitwise 0.0 with NO tolerance" % (label, b - a))
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
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in "
                   "the registered ladder produced a non-zero read. An "
                   "instrument that cannot see a planted perturbation is not "
                   "entitled to certify anything" % label)

        # CLAUSE 5: THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE.
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("%s: read at PLANT is %.6e, below the registered RELATIVE "
                   "predicate PLANT*(1-1e-9) = %.6e. The ABSOLUTE form of "
                   "analyse_t3.py:327 is expressly not adopted here"
                   % (label, at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))

        # CLAUSE 8: the case was never written to, and that is CHECKED.
        if open(tgt(case_dir)).read() != open(tgt(dest)).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)
        return dict(passed=True, base=base, floor=floor, at_plant=at_plant,
                    n_planted=n_planted, rungs=rungs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)        # clause 8, in finally


# ==========================================================================
# GATES
# ==========================================================================

def pulse_table_check(case_dir, case):
    """Section 4.5.  The Function1 table is a LINEAR interpolant, so the two
    breakpoints around the edge are the ends of a RAMP, not a step.  The
    registered condition is that NO step time on this run's deltaT falls
    STRICTLY INSIDE (59.999, 60.000).  This is CHECKED against the dictionary
    that will actually run, not asserted from the document."""
    p = os.path.join(case_dir, "constant", "module", "fvOptions")
    if not os.path.isfile(p):
        refuse("no constant/module/fvOptions -- the pulse this rung is about "
               "cannot be verified to exist")
    txt = _strip(open(p).read())
    if not re.search(r"volumeMode\s+specific\s*;", txt):
        refuse("fvOptions does not register `volumeMode specific`. volumeMode "
               "is MANDATORY at v2606 and the wrong mode is a SILENT scale "
               "error by exactly the zone volume (section 4.5)")
    if re.search(r"\bsources\b[^{]*\{\s*T\b", txt) or re.search(r"^\s*T\s*\{",
                                                                txt, re.M):
        refuse("fvOptions carries a source on field `T`. The solid energy "
               "equation is in ENTHALPY; an entry on T is NEVER APPLIED and "
               "the solid is SILENTLY UNHEATED (section 4.5). That is exactly "
               "the failure CLAUDE.md rule 3 exists for")
    if not re.search(r"\bh\b\s*\{", txt):
        refuse("fvOptions carries no source on field `h`")
    bp = re.findall(r"\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s*\)", txt)
    tab = [(float(a), float(b)) for a, b in bp]
    want = [(0.0, Q_TAKEOFF), (RAMP_LO, Q_TAKEOFF),
            (RAMP_HI, Q_CRUISE), (T_END, Q_CRUISE)]
    if len(tab) != 4 or any(abs(tab[i][0] - want[i][0]) > 1e-9
                            or abs(tab[i][1] - want[i][1]) > 1e-6
                            for i in range(4)):
        refuse("the fvOptions pulse table is %r, not the REGISTERED %r "
               "(section 4.5)" % (tab, want))
    dt = DELTAT[case]
    if dt <= (RAMP_HI - RAMP_LO):
        refuse("deltaT %g is not finer than the %g s ramp width -- section 4.5 "
               "registers that a deltaT finer than the ramp must revisit the "
               "breakpoint placement" % (dt, RAMP_HI - RAMP_LO))
    k0 = int(math.floor(RAMP_LO / dt)) - 2
    hits = [k * dt for k in range(max(k0, 0), k0 + 8)
            if RAMP_LO < k * dt < RAMP_HI]
    if hits:
        refuse("step times %r fall STRICTLY INSIDE the ramp (%g, %g) at deltaT "
               "%g. The solver would sample a value the directive does not "
               "register at those instants (section 4.5)"
               % (hits, RAMP_LO, RAMP_HI, dt))
    return dict(table=tab, ramp=(RAMP_LO, RAMP_HI), deltaT=dt, hits=0)


def outer_loop_census(case_dir, case):
    """Section 3.5.  Count time steps whose LAST outer sweep left any registered
    field above its registered residual threshold.

    WHY NOT `residualControl`.  ESTABLISHED AT SOURCE, v2606, BEFORE THIS GATE
    WAS WRITTEN: chtMultiRegionFoam does NOT use pimpleControl for its outer
    loop.  chtMultiRegionFoam.C:109 is a plain `for (oCorr=0; oCorr<nOuterCorr;
    ++oCorr)` and the per-region control headers read ONLY nCorrectors,
    nNonOrthogonalCorrectors, momentumPredictor and frozenFlow.  THERE IS NO
    residualControl ON THIS SOLVER'S OUTER LOOP and it emits no
    "PIMPLE: converged in" / "not converged within" line, ever.  Counting zero
    such lines would have reported a PLANTED ZERO as a clean pass -- CLAUDE.md
    rule 3's failure mode exactly.  This census reads what the solver DOES
    print: the linear solvers' `Initial residual` on every sweep.

    Startup steps are NOT exempted and NOT excluded; the 5 % allowance covers
    them and is registered as an allowance, not applied as a silent exclusion.
    """
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        refuse("no log.solve for %s" % case)
    body = open(log, errors="replace").read()
    steps = MD.CASES[case]

    if "Initial residual" not in body:
        refuse("log.solve for %s carries NO `Initial residual` lines at all. "
               "Section 3.5 evaluates outer-loop convergence from them; a "
               "census with no evidence is a PLANTED ZERO and is REFUSED, "
               "never reported as 0 failures" % case)

    blocks = re.split(r"^Time = ", body, flags=re.M)[1:]
    if not blocks:
        refuse("log.solve for %s carries no `Time = ` blocks -- the per-step "
               "census cannot be formed" % case)

    bad, seen_any, worst = 0, 0, {}
    for blk in blocks:
        last = {}
        for m in re.finditer(r"Solving for ([A-Za-z_.]+),\s*Initial residual "
                             r"= ([0-9.eE+-]+)", blk):
            last[m.group(1)] = float(m.group(2))
        if not last:
            continue
        seen_any += 1
        over = [f for f, thr in RESID_GATE.items()
                if f in last and last[f] >= thr]
        for f in last:
            if f in RESID_GATE:
                worst[f] = max(worst.get(f, 0.0), last[f])
        if over:
            bad += 1
    if seen_any == 0:
        refuse("no `Time = ` block in %s carries a `Solving for` line -- the "
               "census is BLIND and REFUSES rather than report 0 failures"
               % case)
    missing = [f for f in RESID_GATE if f not in worst]
    if missing:
        refuse("the registered residual fields %s never appear in log.solve. A "
               "gate that silently skips the field it was written for is not a "
               "gate (section 3.5)" % ",".join(sorted(missing)))
    frac = float(bad) / steps
    return dict(steps=steps, blocks=seen_any, over=bad, frac=frac,
                worst=worst, ok=(frac <= OUTER_FAIL_FRAC))


def mesh_quality(case_dir):
    """Section 2.4, read off log.checkMesh per region."""
    out = {}
    for region in REGIONS:
        p = os.path.join(case_dir, "log.checkMesh.%s" % region)
        if not os.path.isfile(p):
            refuse("no log.checkMesh.%s -- section 2.4 registers a mesh gate "
                   "and it is not graded on trust" % region)
        txt = open(p, errors="replace").read()
        nonorth = max([float(x) for x in
                       re.findall(r"[Mm]ax(?:imum)? non-orthogonality[^\d-]*"
                                  r"(-?[\d.eE+]+)", txt)] or [-1.0])
        skew = max([float(x) for x in
                    re.findall(r"[Mm]ax(?:imum)? skewness[^\d-]*"
                               r"(-?[\d.eE+]+)", txt)] or [-1.0])
        if nonorth < 0 or skew < 0:
            refuse("log.checkMesh.%s states no max non-orthogonality or max "
                   "skewness -- the gate cannot be evaluated" % region)
        ok = ("Mesh OK" in txt and "***" not in txt
              and nonorth < MESH_MAXNONORTH and skew < MESH_MAXSKEW)
        out[region] = dict(nonorth=nonorth, skew=skew,
                           mesh_ok=("Mesh OK" in txt), ok=ok)
    return out


def energy_balance(case_dir, mm=None, mc=None):
    """Section 6.2.  E_gen = dE_solid + dE_fluid + convected + R."""
    dEs = read_stored(case_dir, T_END, "module", mm)
    dEf = read_stored(case_dir, T_END, "coolant", mc)
    conv = convected_energy(case_dir)
    R = E_GEN - (dEs + dEf + conv)
    return dict(E_gen=E_GEN, dE_solid=dEs, dE_fluid=dEf, convected=conv,
                residual=R, rel=abs(R) / E_GEN,
                ok=(abs(R) / E_GEN <= ENERGY_BAND))


def convected_energy(case_dir):
    """Time-integral of mdot*cp*(T_out - T_in), J, from the registered
    surfaceFieldValue instruments.  `phi` is the MASS flux and is NEGATIVE on
    an inflow face, so the two weightedSum rows ADD rather than subtract."""
    tot = None
    for name in ("inlet_hflux", "outlet_hflux"):
        p = _postproc_dat(case_dir, name)
        rows = _read_dat(p)
        s = 0.0
        prev_t = 0.0
        for t, v in rows:
            s += v * (t - prev_t)
            prev_t = t
        tot = s if tot is None else tot + s
    return CP_AIR * tot


def _postproc_dat(case_dir, name):
    root = os.path.join(case_dir, "postProcessing", name)
    if not os.path.isdir(root):
        refuse("no postProcessing/%s -- section 6.2 registers this instrument "
               "and its absence is a REFUSAL, not a zero" % name)
    subs = sorted(os.listdir(root))
    if len(subs) != 1:
        refuse("postProcessing/%s holds %d start-time directories (%s). A "
               "RESTART would leave more than one and the integral would "
               "silently double-count; this reader REFUSES rather than pick "
               "one" % (name, len(subs), ",".join(subs)))
    d = os.path.join(root, subs[0])
    f = [x for x in sorted(os.listdir(d)) if x.endswith(".dat")]
    if len(f) != 1:
        refuse("postProcessing/%s/%s holds %d .dat files, expected exactly 1"
               % (name, subs[0], len(f)))
    return os.path.join(d, f[0])


def _read_dat(path):
    rows = []
    for line in open(path):
        if line.lstrip().startswith("#") or not line.strip():
            continue
        p = line.split()
        if len(p) < 2:
            refuse("%s: a data line carries fewer than 2 columns" % path)
        rows.append((float(p[0]), float(p[-1])))
    if not rows:
        refuse("%s holds no data rows -- a zero from an EMPTY instrument is "
               "not a measurement (CLAUDE.md rule 3)" % path)
    return rows


def energy_planted_control(case_dir):
    """Section 6.2's planted +10 % source control.  E_gen is recomputed with
    the TAKEOFF level scaled by +10 % and the residual must move by exactly
    that much.  AN INSTRUMENT THAT DOES NOT MOVE WHEN THE SOURCE MOVES IS
    REFUSED, not reported."""
    d = N_CELLS * V_CELL * PLANT10_PCT * Q_TAKEOFF * T_PULSE
    base = energy_balance(case_dir)
    moved = (E_GEN + d) - (base["dE_solid"] + base["dE_fluid"]
                           + base["convected"])
    got = moved - base["residual"]
    if abs(got - d) > 1e-6:
        refuse("ENERGY BALANCE PLANTED CONTROL: a +10 %% takeoff source moved "
               "the residual by %.9e J, not the expected %.9e J. The balance "
               "instrument does not respond to the source it audits" % (got, d))
    return dict(passed=True, planted_J=d, seen_J=got)


def acceptance_D(case_dir, mm=None, mc=None):
    """Section 5.3: D1, D2, D3.  Sanaa's acceptance criterion for the resolved
    channel, in the form the REGISTERED PARALLEL-CHANNEL GEOMETRY admits."""
    up, dn = read_updown(case_dir, T_PULSE, mm)
    diff = [dn[i] - up[i] for i in range(N_CELLS)]
    d1 = all(x > 0.0 for x in diff)
    d3 = min(diff) > D3_FLOOR
    outs, ins = [], []
    for t in _written_times(case_dir):
        if t <= 0.0:
            continue
        outs.append((t, read_patch_T(case_dir, t, "outlet", mc)))
        ins.append((t, read_patch_T(case_dir, t, "inlet", mc)))
    d2 = all(o[1] > i[1] for o, i in zip(outs, ins))
    return dict(up=up, dn=dn, diff=diff, D1=d1, D2=d2, D3=d3,
                D3_floor=D3_FLOOR, min_diff=min(diff),
                outlet=outs, inlet=ins)


def _written_times(case_dir):
    ts = sorted(float(x) for x in os.listdir(case_dir)
                if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x))
    if not ts:
        refuse("case %s holds no time directories" % case_dir)
    return ts


# ==========================================================================
# THE SENSITIVITY PANELS -- DIFFERENCES, AND NOTHING ELSE.
# ==========================================================================

NO_LADDER = ("TWO POINTS. NO LADDER IS REGISTERED. No observed order, no GCI "
             "and no Roache classification is computed, quoted or quotable "
             "from this artifact. A small difference between two points is "
             "CONSISTENT WITH convergence and is NOT EVIDENCE OF it.")


def sensitivity(a_dir, b_dir, a_name, b_name, kind):
    """Signed and percentage DIFFERENCES on the registered quantities.  This
    function computes NO order and NO GCI and there is no code path here that
    could."""
    out = {"kind": kind, "arms": [a_name, b_name], "no_ladder": NO_LADDER}
    ma, mb = Mesh(a_dir, "module"), Mesh(b_dir, "module")
    ca, cb = Mesh(a_dir, "coolant"), Mesh(b_dir, "coolant")
    rows = []
    for label, fa, fb in (
            ("peak cell T at t=60 s (K)",
             lambda: max(read_cell_T(a_dir, T_PULSE, ma)),
             lambda: max(read_cell_T(b_dir, T_PULSE, mb))),
            ("peak cell T at t=900 s (K)",
             lambda: max(read_cell_T(a_dir, T_END, ma)),
             lambda: max(read_cell_T(b_dir, T_END, mb))),
            ("module spread at t=60 s (K)",
             lambda: read_spread(a_dir, T_PULSE, ma),
             lambda: read_spread(b_dir, T_PULSE, mb)),
            ("coolant outlet T at t=60 s (K)",
             lambda: read_patch_T(a_dir, T_PULSE, "outlet", ca),
             lambda: read_patch_T(b_dir, T_PULSE, "outlet", cb)),
            ("coolant outlet T at t=900 s (K)",
             lambda: read_patch_T(a_dir, T_END, "outlet", ca),
             lambda: read_patch_T(b_dir, T_END, "outlet", cb)),
            ("min within-cell streamwise diff at t=60 s (K)",
             lambda: min(acceptance_D(a_dir, ma, ca)["diff"]),
             lambda: min(acceptance_D(b_dir, mb, cb)["diff"]))):
        va, vb = fa(), fb()
        rows.append(dict(quantity=label, a=va, b=vb, diff=vb - va,
                         pct=(100.0 * (vb - va) / va) if va else None))
    out["rows"] = rows
    return out


# ==========================================================================
# GRADING
# ==========================================================================

def _header(sha):
    print("T25R -- 8-CELL AVIATION BATTERY MODULE, RESOLVED COOLING CHANNELS, "
          "TRUE TRANSIENT CONJUGATE.")
    print("Gates FROZEN at %s, blob %s." % (FROZEN_DOC, sha[:12]))
    print("")
    print("*** " + NO_LADDER)
    print("*** SECTION 6.1: THE T20 EXACT GATE HAS NOT DISCHARGED. "
          "T20_P10_CONDITION_iii_MEASUREMENT.md:9 states \"T20 remains NOT A "
          "RESULT on its own registered terms\". The T20 citation is a POINTER "
          "to the registered exact tier, NOT a discharged machinery proof, and "
          "T25R INHERITS NO PASS FROM IT.")
    print("*** SECTION 3.6: with g = (0 0 0) registered, a Ri < 0.1 criterion "
          "is IDENTICALLY ZERO BY CONSTRUCTION, cannot fail and cannot inform. "
          "It is NOT reported as a passing check. Buoyancy is OFF, its neglect "
          "is a DECLARED OMISSION, and forced-convection dominance rests on "
          "Gr/Re2 = 2.51e-05 (section 3.6), not on any check run here.")
    print("*** SECTION 3.3: transient FLOW dynamics are NOT resolved. The step "
          "is derived from the 60 s pulse edge and the ~696 s lumped tau, NOT "
          "from a Courant number; Co ~ 1600 is REPORTED, not controlled.")
    print("*** SECTION 0.3: a partially converged transient is NEVER presented "
          "as complete, and the 0.4 K FEASIBILITY run stays off every screen.")
    print("PLANT = %.6e, IMPORTED from scripts/roache_triple.py and never "
          "redefined here (section 7.1 clause 6)." % PLANT)
    if PLANT != RT.PLANT:
        refuse("PLANT was redefined locally -- clause 6 forbids it")
    print("")


def grade(root, cases, repo=None):
    sha = freeze_check(repo)
    _header(sha)
    worst, out = EXIT_OK, {}

    for case in cases:
        if case not in CASES:
            refuse("%r is not a registered T25R case (section 1): %s"
                   % (case, " ".join(CASES)))
        d = os.path.join(root, case)
        print("=" * 74)
        print("%s  (mesh %s, deltaT %g s, %d registered steps)"
              % (case, LEVEL[case], DELTAT[case], MD.CASES[case]))
        print("=" * 74)

        # ---- 1. COMPLETION, DELEGATED (section 6.4).  Never reimplemented.
        fails, notes = MD.check(root, case)
        for n in notes:
            print("  NOTE  %s" % n)
        if fails:
            print("  VERDICT: NOT A RESULT -- rule 4 completion: %s"
                  % "; ".join(fails))
            print("  No number from this run is printed as a result. A "
                  "partially converged transient is NEVER presented as "
                  "complete (section 0.3).")
            out[case] = dict(verdict="NOT A RESULT", why=fails)
            worst = EXIT_FAIL
            continue

        # ---- 2. THE PULSE DICTIONARY (section 4.5).
        pt = pulse_table_check(d, case)
        print("  PULSE TABLE OK: %r; ramp (%g, %g); no step time at deltaT %g "
              "falls strictly inside it." % (pt["table"], pt["ramp"][0],
                                             pt["ramp"][1], pt["deltaT"]))

        # ---- 3. MESH QUALITY (section 2.4).
        mq = mesh_quality(d)
        for r in REGIONS:
            print("  checkMesh %-8s Mesh OK=%s  maxNonOrth=%.4g (<%g)  "
                  "maxSkew=%.4g (<%g)  -> %s"
                  % (r, mq[r]["mesh_ok"], mq[r]["nonorth"], MESH_MAXNONORTH,
                     mq[r]["skew"], MESH_MAXSKEW,
                     "OK" if mq[r]["ok"] else "FAIL"))
        if not all(mq[r]["ok"] for r in REGIONS):
            print("  VERDICT: NOT A RESULT -- section 2.4 mesh gate failed.")
            out[case] = dict(verdict="NOT A RESULT", why=["mesh gate"], mesh=mq)
            worst = EXIT_FAIL
            continue

        # ---- 4. OUTER-LOOP CONVERGENCE (section 3.5).
        oc = outer_loop_census(d, case)
        print("  OUTER-LOOP CENSUS: %d of %d steps left a registered field "
              "above its threshold at the LAST outer sweep (%.3f %%, allowance "
              "%.1f %%) -> %s"
              % (oc["over"], oc["steps"], 100 * oc["frac"],
                 100 * OUTER_FAIL_FRAC, "OK" if oc["ok"] else "FAIL"))
        for f in sorted(oc["worst"]):
            print("    worst last-sweep initial residual  %-6s %.4e "
                  "(threshold %.0e)" % (f, oc["worst"][f], RESID_GATE[f]))
        if not oc["ok"]:
            print("  VERDICT: NOT A RESULT -- section 3.5. The number of "
                  "unconverged steps is printed above and beside every "
                  "quantity this run produced.")
            out[case] = dict(verdict="NOT A RESULT", why=["outer loop"],
                             outer=oc)
            worst = EXIT_FAIL
            continue

        # ---- 5. INSTRUMENT ADMISSION (section 7.1).  BEFORE any number.
        mm, mc = Mesh(d, "module"), Mesh(d, "coolant")
        tmod = os.path.join("%g" % T_END, "module", "T")
        tcool = os.path.join("%g" % T_END, "coolant", "T")
        ctrls = {}
        for lbl, rdr, plt, tgt in (
                ("read_cell_T",
                 lambda x: max(read_cell_T(x, T_END)),
                 lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                 tmod),
                ("read_spread",
                 lambda x: read_spread(x, T_END),
                 lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                 tmod),
                ("read_updown",
                 lambda x: max(read_updown(x, T_END)[1]),
                 lambda x, m: _plant_internal_all(os.path.join(x, tmod), m),
                 tmod),
                ("read_outlet_T",
                 lambda x: read_patch_T(x, T_END, "outlet"),
                 lambda x, m: _plant_patch_all(os.path.join(x, tcool),
                                               "outlet", m),
                 tcool),
                ("read_inlet_T",
                 lambda x: read_patch_T(x, T_END, "inlet"),
                 lambda x, m: _plant_patch_all(os.path.join(x, tcool),
                                               "inlet", m),
                 tcool)):
            c = planted_zero_control(d, lbl, rdr, plt, tgt)
            ctrls[lbl] = c
            print("  PLANTED-ZERO CONTROL %-14s PASS. negative arm bitwise 0.0; "
                  "measured floor %.3e; read at PLANT %.6e against the "
                  "RELATIVE predicate PLANT*(1-1e-9) = %.6e; values planted %d"
                  % (lbl, c["floor"], c["at_plant"],
                     PLANT * (1.0 - PLANT_REL_SLACK), c["n_planted"]))

        # ---- 6. ENERGY CONSERVATION (section 6.2) + its planted control.
        epc = energy_planted_control(d)
        print("  ENERGY PLANTED CONTROL PASS: a +10 %% takeoff source moved the "
              "residual by %.6e J, the expected %.6e J."
              % (epc["seen_J"], epc["planted_J"]))
        eb = energy_balance(d, mm, mc)
        print("  ENERGY BALANCE over 900 s:  E_gen %.1f J = dE_solid %.1f + "
              "dE_fluid %.1f + convected %.1f + R %.1f"
              % (eb["E_gen"], eb["dE_solid"], eb["dE_fluid"], eb["convected"],
                 eb["residual"]))
        print("  |R|/E_gen = %.4f %% against the registered band %.1f %% -> %s"
              % (100 * eb["rel"], 100 * ENERGY_BAND,
                 "PASS" if eb["ok"] else "GATE FAIL"))

        # ---- 7. THE ACCEPTANCE CRITERION (section 5.3).
        ac = acceptance_D(d, mm, mc)
        print("  SECTION 5.2 DISCLOSURE: the 7 channels are PARALLEL and no "
              "cell is downstream of another. D1/D3 are WITHIN-CELL "
              "streamwise; D2 is outlet-above-inlet. This is disclosed, not "
              "substituted, and the framing is Sanaa's to rule.")
        for i in range(N_CELLS):
            print("    cell %d  T_up %.6f  T_dn %.6f  diff %+0.6e K"
                  % (i + 1, ac["up"][i], ac["dn"][i], ac["diff"][i]))
        print("  D1 (T_dn > T_up, all 8, t=60 s)          -> %s"
              % ("PASS" if ac["D1"] else "GATE FAIL"))
        print("  D2 (outlet > inlet at every written t>0) -> %s"
              % ("PASS" if ac["D2"] else "GATE FAIL"))
        print("  D3 (min diff %.6e K > 10*PLANT = %.6e K) -> %s"
              % (ac["min_diff"], ac["D3_floor"],
                 "PASS" if ac["D3"] else "GATE FAIL"))

        gates_ok = eb["ok"] and ac["D1"] and ac["D2"] and ac["D3"]
        verdict = "PASS" if gates_ok else "GATE FAIL"
        print("  VERDICT: %s" % verdict)
        if not gates_ok:
            worst = EXIT_FAIL

        # ---- 8. THE FEASIBILITY-TAGGED OUTPUTS (section 9).
        print("  FEASIBILITY (not gradeable; no gate exists for these and none "
              "may be invented after the fact):")
        cells_end = read_cell_T(d, T_END, mm)
        cells_60 = read_cell_T(d, T_PULSE, mm)
        for i in range(N_CELLS):
            print("    cell %d  T(60 s) %.6f K  rise %+0.6f K   T(900 s) "
                  "%.6f K  rise %+0.6f K  [FEASIBILITY]"
                  % (i + 1, cells_60[i], cells_60[i] - T_INIT,
                     cells_end[i], cells_end[i] - T_INIT))
        print("    module spread t=60 s %.6e K, t=900 s %.6e K  [FEASIBILITY]"
              % (read_spread(d, T_PULSE, mm), read_spread(d, T_END, mm)))
        print("    SECTION 4.3 REGISTERED PREDICTION: the adiabatic bound on "
              "the pulse rise is q*t/(rho*cp) = %.4f K, and the prediction "
              "registered BEFORE the run was 1.4-1.7 K, NOT tens of kelvin. "
              "The measured value above is the deliverable whatever it is."
              % (Q_TAKEOFF * T_PULSE / (RHO_S * CP_S)))

        out[case] = dict(verdict=verdict, energy=eb, acceptance=ac,
                         outer=oc, mesh=mq, pulse=pt,
                         controls={k: dict(floor=v["floor"],
                                           at_plant=v["at_plant"],
                                           n_planted=v["n_planted"])
                                   for k, v in ctrls.items()},
                         cells_60=cells_60, cells_900=cells_end)

    # ---- 9. THE TWO SENSITIVITY PANELS.  DIFFERENCES, AND NOTHING ELSE.
    for pair, kind in ((MESH_PAIR, "MESH SENSITIVITY (L1 vs L2, same deltaT)"),
                       (STEP_PAIR, "STEP SENSITIVITY (dt 0.5 vs 0.25, same "
                                   "mesh)")):
        if not all(c in out and out[c].get("verdict") != "NOT A RESULT"
                   for c in pair):
            print("\n%s: PENDING -- one or both arms is not a result." % kind)
            continue
        print("\n" + "-" * 74)
        print(kind)
        print("*** " + NO_LADDER)
        print("-" * 74)
        s = sensitivity(os.path.join(root, pair[0]),
                        os.path.join(root, pair[1]), pair[0], pair[1], kind)
        for r in s["rows"]:
            print("  %-44s %14.8g -> %14.8g  diff %+.6e (%+.4f %%)"
                  % (r["quantity"], r["a"], r["b"], r["diff"],
                     r["pct"] if r["pct"] is not None else float("nan")))
        out[kind] = s

    return worst, out


# ==========================================================================
# SELFTEST.  Forges synthetic cases in scratch and drives every clause,
# positive and negative.  No solver, no mesher, no case on disk is touched.
# ==========================================================================

def _forge_case(root, case, dt, tdn_bonus=0.05, ramp=(RAMP_LO, RAMP_HI),
                q_take=Q_TAKEOFF, nx=20, ny=2, blind=False):
    """A tiny but STRUCTURALLY REAL case: 8 module cells x (nx*ny) hexes,
    a coolant region with inlet/outlet patches, a log, a STATUS, checkMesh
    logs, an fvOptions and the two postProcessing instruments."""
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "application     chtMultiRegionFoam;\nendTime         900;\n"
        "deltaT          %g;\nadjustTimeStep  no;\n" % dt)
    open(os.path.join(d, "STATUS.%s" % case), "w").write(
        "launcher_rc=0\nnote=exit-status-of-the-launch-argv-NOT-the-solver-rc\n")
    steps = MD.CASES[case]
    lines = ["ExecutionTime = %g s  ClockTime = %d s" % (i * .1, i)
             for i in range(1, steps + 1)]
    for i in range(steps):
        lines.append("Time = %g" % ((i + 1) * dt))
        for f, v in (("Ux", 1e-9), ("Uy", 1e-9), ("p_rgh", 1e-9), ("h", 1e-9)):
            lines.append("PBiCGStab:  Solving for %s, Initial residual = %g, "
                         "Final residual = 1e-12, No Iterations 2" % (f, v))
    lines += ["End"]
    open(os.path.join(d, "log.solve"), "w").write("\n".join(lines) + "\n")
    for r in REGIONS:
        open(os.path.join(d, "log.checkMesh.%s" % r), "w").write(
            "Max skewness = 1.0e-13\nMax non-orthogonality = 0\nMesh OK.\n")

    # ---- fvOptions
    os.makedirs(os.path.join(d, "constant", "module"), exist_ok=True)
    open(os.path.join(d, "constant", "module", "fvOptions"), "w").write(
        "FoamFile{ version 2.0; }\nq{\n type scalarSemiImplicitSource;\n"
        " volumeMode      specific;\n sources { h { explicit table\n"
        " (\n ( 0.000 %.6f)\n ( %.3f %.6f)\n ( %.3f %.6f)\n ( 900.000 %.6f)\n"
        " );\n implicit none; } }\n}\n"
        % (q_take, ramp[0], q_take, ramp[1], Q_CRUISE, Q_CRUISE))

    # ---- the two meshes, written as real polyMesh files.
    def hexmesh(region, boxes):
        pm = os.path.join(d, "constant", region, "polyMesh")
        os.makedirs(pm, exist_ok=True)
        pts, pidx, faces, owner, neigh = [], {}, [], [], []
        fkey = {}

        def P(x, y, z):
            k = (round(x, 12), round(y, 12), round(z, 12))
            if k not in pidx:
                pidx[k] = len(pts)
                pts.append(k)
            return pidx[k]

        internal, bnd = [], {"inlet": [], "outlet": [], "wall": []}
        for ci, (x0, x1, y0, y1) in enumerate(boxes):
            v = [P(x0, y0, 0), P(x1, y0, 0), P(x1, y1, 0), P(x0, y1, 0),
                 P(x0, y0, 1), P(x1, y0, 1), P(x1, y1, 1), P(x0, y1, 1)]
            for nm, q in (("xlo", (v[0], v[3], v[7], v[4])),
                          ("xhi", (v[1], v[5], v[6], v[2])),
                          ("ylo", (v[0], v[4], v[5], v[1])),
                          ("yhi", (v[3], v[2], v[6], v[7])),
                          ("zlo", (v[0], v[1], v[2], v[3])),
                          ("zhi", (v[4], v[7], v[6], v[5]))):
                k = tuple(sorted(q))
                if k in fkey:
                    internal.append((fkey[k][0], ci, fkey[k][1]))
                    fkey[k] = None
                elif k is not None and fkey.get(k, 0) is None:
                    pass
                else:
                    fkey[k] = (ci, q, nm, x0, x1)
        for k, val in list(fkey.items()):
            if val is None:
                continue
            ci, q, nm, x0, x1 = val
            if region == "coolant" and nm == "xlo" and x0 <= 1e-12:
                bnd["inlet"].append((ci, q))
            elif region == "coolant" and nm == "xhi" and x1 >= CELL_LX - 1e-12:
                bnd["outlet"].append((ci, q))
            else:
                bnd["wall"].append((ci, q))
        allf, ow, ne = [], [], []
        for a, b, q in internal:
            allf.append(q)
            ow.append(min(a, b))
            ne.append(max(a, b))
        starts = {}
        for nm in ("inlet", "outlet", "wall"):
            starts[nm] = (len(allf), len(bnd[nm]))
            for ci, q in bnd[nm]:
                allf.append(q)
                ow.append(ci)
        hdr = "FoamFile{ version 2.0; }\n"
        open(os.path.join(pm, "points"), "w").write(
            hdr + "%d\n(\n" % len(pts)
            + "\n".join("(%.12g %.12g %.12g)" % p for p in pts) + "\n)\n")
        open(os.path.join(pm, "faces"), "w").write(
            hdr + "%d\n(\n" % len(allf)
            + "\n".join("4(%d %d %d %d)" % f for f in allf) + "\n)\n")
        open(os.path.join(pm, "owner"), "w").write(
            hdr + "%d\n(\n" % len(ow) + "\n".join(str(x) for x in ow) + "\n)\n")
        open(os.path.join(pm, "neighbour"), "w").write(
            hdr + "%d\n(\n" % len(ne) + "\n".join(str(x) for x in ne) + "\n)\n")
        bb = [hdr, "%d\n(" % 3]
        for nm in ("inlet", "outlet", "wall"):
            s, k = starts[nm]
            bb.append("%s\n{\n type patch;\n nFaces %d;\n startFace %d;\n}"
                      % (nm, k, s))
        bb.append(")")
        open(os.path.join(pm, "boundary"), "w").write("\n".join(bb) + "\n")
        return len(boxes)

    mboxes, cboxes = [], []
    for j in range(N_CELLS):
        y0 = j * PITCH
        for a in range(nx):
            for b in range(ny):
                mboxes.append((CELL_LX * a / nx, CELL_LX * (a + 1) / nx,
                               y0 + CELL_LY * b / ny, y0 + CELL_LY * (b + 1) / ny))
        if j < N_CELLS - 1:
            for a in range(nx):
                cboxes.append((CELL_LX * a / nx, CELL_LX * (a + 1) / nx,
                               y0 + CELL_LY, y0 + CELL_LY + GAP))
    nm = hexmesh("module", mboxes)
    nc = hexmesh("coolant", cboxes)

    # ---- fields.  A DOWNSTREAM-HOTTER solid and a warming coolant.
    def wfield(t, region, boxes, n, patchvals=None):
        td = os.path.join(d, "%g" % t, region)
        os.makedirs(td, exist_ok=True)
        vals = []
        for (x0, x1, y0, y1) in boxes:
            xc = 0.5 * (x0 + x1)
            vals.append(T_INIT + 1.4 * (t / T_END) + tdn_bonus * xc / CELL_LX)
        body = ["FoamFile{ version 2.0; }", "dimensions [0 0 0 1 0 0 0];", "",
                "internalField   nonuniform List<scalar>", str(n), "("]
        body += ["%.12g" % v for v in vals]
        body += [")", ";", "", "boundaryField", "{"]
        for nmp in ("inlet", "outlet", "wall"):
            body += ["%s" % nmp, "{", "    type            calculated;"]
            k = (patchvals or {}).get(nmp)
            if k is not None:
                body += ["    value           nonuniform List<scalar>",
                         str(len(k)), "("]
                body += ["%.12g" % v for v in k]
                body += [")", ";"]
            body += ["}"]
        body += ["}"]
        open(os.path.join(td, "T"), "w").write("\n".join(body) + "\n")
        for f in MD.NEEDED[region]:
            fp = os.path.join(td, f)
            if not os.path.exists(fp):
                open(fp, "w").write("x\n")

    nfin = nx  # inlet/outlet face counts on the forged coolant mesh
    for t in _forge_times(dt):
        wfield(t, "module", mboxes, nm)
        wfield(t, "coolant", cboxes, nc,
               {"inlet": [T_INIT] * (N_CELLS - 1),
                "outlet": [T_INIT + (0.0 if blind else 0.8 * t / T_END)]
                          * (N_CELLS - 1)})
    ref = os.path.join(d, "0", "module", "T")
    a = os.path.getmtime(ref)
    os.utime(ref, (a - 100, a - 100))

    # ---- the two convected-energy instruments.
    for nmi, sgn in (("inlet_hflux", -1.0), ("outlet_hflux", +1.0)):
        pd = os.path.join(d, "postProcessing", nmi, "0")
        os.makedirs(pd, exist_ok=True)
        rows = ["# t  weightedSum(phi,T)"]
        for k in range(1, 11):
            t = T_END * k / 10.0
            rows.append("%g %.10g" % (t, sgn * 0.2016 * (T_INIT + 0.4 * k / 10.0)))
        open(os.path.join(pd, "surfaceFieldValue.dat"),
             "w").write("\n".join(rows) + "\n")
    return d


def _forge_times(dt):
    return sorted(set(list(WRITE_TIMES)))


def selftest():
    fails = 0

    def chk(name, cond):
        nonlocal fails
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails += 1

    def refuses(fn):
        try:
            fn()
        except SystemExit as e:
            return e.code == EXIT_REFUSE
        return False

    chk("PLANT is imported from roache_triple and equals 1.234e-03",
        PLANT == RT.PLANT and abs(PLANT - 1.234e-03) < 1e-15)
    chk("LADDER exercises PLANT exactly once", LADDER.count(PLANT) == 1)
    chk("D3 floor is 10*PLANT", abs(D3_FLOOR - 10 * PLANT) < 1e-15)
    chk("E_gen matches the frozen 157248 J", abs(E_GEN - 157248.0) < 1e-6)
    chk("the adiabatic bound is 1.680 K",
        abs(Q_TAKEOFF * T_PULSE / (RHO_S * CP_S) - 1.68) < 1e-9)
    # THE STRUCTURAL PROOF THAT NO ORDER IS COMPUTED HERE.  The forbidden
    # tokens are assembled from fragments so this test does not match itself,
    # and the module DOCSTRING is excluded because it NAMES the classifications
    # in order to forbid them.  What is tested is the CODE: an observed order
    # needs a logarithm of a ratio of differences and a safety factor, and
    # neither exists anywhere in this file.
    src = open(os.path.abspath(__file__)).read()
    code = src[src.index("import json"):]
    forbidden = ["math." + "log", "log" + "10", "Fs" + " =", "1." + "25",
                 "def " + "gci", "def " + "roache",
                 "RT." + "roache", "RT." + "gci", "RT." + "observed"]
    hit = [t for t in forbidden if t in code]
    chk("no code path in this file computes a GCI or an observed order: an "
        "observed order needs a LOGARITHM of a ratio of differences and a GCI "
        "needs Roache's safety factor, and NEITHER TOKEN APPEARS ANYWHERE IN "
        "THIS FILE (forbidden tokens found: %r)" % hit, not hit)
    chk("the JSON emission pins roache_classification, gci and observed_order "
        "to None EXPLICITLY, so a downstream reader cannot mistake absence "
        "for omission",
        "roache_classification=None" in code and "gci=None" in code
        and "observed_order=None" in code)

    root = tempfile.mkdtemp(prefix="t25Rsel_")
    try:
        d = _forge_case(root, "T25R_L2", 0.5)

        # --- the mesh reader
        mm = Mesh(d, "module")
        chk("module mesh boxes: 8 cells x nx*ny hexes", mm.n == 8 * 20 * 2)
        chk("cell banding assigns exactly 8 module cells",
            len(set(_cell_of(mm, i) for i in range(mm.n))) == N_CELLS)
        chk("total module volume is 8 * V_CELL",
            abs(sum(mm.vol) - N_CELLS * V_CELL) < 1e-12)

        # --- the readers
        v = read_cell_T(d, T_END, mm)
        chk("read_cell_T returns 8 values", len(v) == N_CELLS)
        chk("a mesh too coarse for the 10 mm x-band REFUSES rather than "
            "silently average the wrong cells",
            refuses(lambda: read_updown(
                _forge_case(root, "T25R_L1", 0.5, nx=4), T_END)))
        up, dn = read_updown(d, T_END, mm)
        chk("read_updown sees the planted downstream bonus",
            all(dn[i] > up[i] for i in range(N_CELLS)))

        # --- the planted-zero controls, positive arms
        tmod = os.path.join("%g" % T_END, "module", "T")
        c = planted_zero_control(
            d, "read_cell_T", lambda x: max(read_cell_T(x, T_END)),
            lambda x, m: _plant_hottest_module_cell(x, T_END, m), tmod)
        chk("read_cell_T control PASSES and plants a WHOLE module cell so the "
            "volume-average shift is exactly mag, never mag/N",
            c["passed"] and c["n_planted"] == mm.n // N_CELLS)
        chk("read_cell_T read at PLANT equals PLANT to 1e-12, not PLANT/N",
            abs(c["at_plant"] - PLANT) < 1e-12)
        cs = planted_zero_control(
            d, "read_spread", lambda x: read_spread(x, T_END),
            lambda x, m: _plant_hottest_module_cell(x, T_END, m), tmod)
        chk("read_spread control PASSES (the spread moves by exactly mag)",
            cs["passed"] and abs(cs["at_plant"] - PLANT) < 1e-12)
        chk("read_cell_T control read at PLANT clears the RELATIVE predicate",
            c["at_plant"] >= PLANT * (1.0 - PLANT_REL_SLACK))

        tcool = os.path.join("%g" % T_END, "coolant", "T")
        c2 = planted_zero_control(
            d, "read_outlet_T", lambda x: read_patch_T(x, T_END, "outlet"),
            lambda x, m: _plant_patch_all(os.path.join(x, tcool), "outlet", m),
            tcool)
        chk("read_outlet_T control plants EVERY face so the shift is exactly "
            "mag, not mag/N", abs(c2["at_plant"] - PLANT) < 1e-12)

        # --- NEGATIVE ARM: a BLIND reader must REFUSE, not report zero.
        chk("a BLIND reader REFUSES (clause 4)",
            refuses(lambda: planted_zero_control(
                d, "blind", lambda x: 0.0,
                lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                tmod)))
        chk("a SINGLE-CELL plant under a volume-average reader REFUSES at "
            "clause 5 -- the mag/N failure mode is LIVE, not hypothetical",
            refuses(lambda: planted_zero_control(
                d, "single_cell", lambda x: max(read_cell_T(x, T_END)),
                lambda x, m: _plant_internal_one(os.path.join(x, tmod), m),
                tmod)))
        # --- NEGATIVE ARM: a NOISY reader must REFUSE at bitwise 0.0.
        st = {"k": 0}

        def noisy(x):
            st["k"] += 1
            return float(st["k"])
        chk("a NOISY reader REFUSES at bitwise 0.0 (clause 2)",
            refuses(lambda: planted_zero_control(
                d, "noisy", noisy,
                lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                tmod)))
        # --- CLAUSE 8: the case was not written to.
        chk("the case bytes are unchanged after every control",
            open(os.path.join(d, tmod)).read() ==
            open(os.path.join(d, tmod)).read())

        # --- the acceptance criterion
        ac = acceptance_D(d, mm)
        chk("D1 PASSES on a downstream-hotter forge", ac["D1"])
        chk("D2 PASSES on a warming coolant", ac["D2"])
        chk("D3 PASSES when the signal exceeds 10*PLANT", ac["D3"])

        # --- NEGATIVE ARM: a flat solid must FAIL D1 and D3, not pass.
        d2 = _forge_case(root, "T25R_L1", 0.5, tdn_bonus=0.0)
        ac2 = acceptance_D(d2)
        chk("a FLAT solid FAILS D1", not ac2["D1"])
        chk("a FLAT solid FAILS D3", not ac2["D3"])
        # --- NEGATIVE ARM: a sub-threshold signal must FAIL D3 but pass D1.
        d3 = _forge_case(root, "T25R_L2_DT025", 0.25, tdn_bonus=1e-4)
        ac3 = acceptance_D(d3)
        chk("a signal below 10*PLANT PASSES D1 but FAILS D3",
            ac3["D1"] and not ac3["D3"])
        # --- NEGATIVE ARM: an isothermal coolant must FAIL D2.
        d4 = _forge_case(root, "T25R_L1", 0.5, blind=True)
        chk("an isothermal coolant FAILS D2", not acceptance_D(d4)["D2"])

        # --- the pulse table
        chk("the registered pulse table passes",
            pulse_table_check(d, "T25R_L2")["hits"] == 0)
        d5 = _forge_case(root, "T25R_L1", 0.5, ramp=(59.75, 60.25))
        chk("a ramp straddling a step time REFUSES",
            refuses(lambda: pulse_table_check(d5, "T25R_L1")))
        d6 = _forge_case(root, "T25R_L1", 0.5, q_take=5000.0)
        chk("the FEASIBILITY rung's 5000 W/m3 table REFUSES here",
            refuses(lambda: pulse_table_check(d6, "T25R_L1")))

        # --- the energy planted control must MOVE.
        ep = energy_planted_control(d)
        chk("the +10 %% source control moves the residual by exactly 10080 J",
            abs(ep["planted_J"] - 10080.0) < 1e-6
            and abs(ep["seen_J"] - 10080.0) < 1e-6)

        # --- the outer-loop census refuses a log with NO evidence.
        d7 = _forge_case(root, "T25R_L1", 0.5)
        chk("a clean forge PASSES the outer-loop census",
            outer_loop_census(d7, "T25R_L1")["ok"])
        open(os.path.join(d7, "log.solve"), "w").write("End\n")
        chk("an outer-loop census with NO `Initial residual` lines REFUSES "
            "rather than report 0 failures -- the planted-zero trap this gate "
            "was rewritten to avoid",
            refuses(lambda: outer_loop_census(d7, "T25R_L1")))
        d7b = _forge_case(root, "T25R_L1", 0.5)
        txt = open(os.path.join(d7b, "log.solve")).read()
        open(os.path.join(d7b, "log.solve"), "w").write(
            txt.replace("Solving for h, Initial residual = 1e-09",
                        "Solving for h, Initial residual = 1e-05"))
        chk("solid h above 1e-8 on every step -> census FAILS",
            not outer_loop_census(d7b, "T25R_L1")["ok"])
        d7c = _forge_case(root, "T25R_L1", 0.5)
        txt = open(os.path.join(d7c, "log.solve")).read()
        open(os.path.join(d7c, "log.solve"), "w").write(
            re.sub(r".*Solving for p_rgh.*\n", "", txt))
        chk("a registered residual field ABSENT from the log REFUSES -- a gate "
            "that silently skips its own field is not a gate",
            refuses(lambda: outer_loop_census(d7c, "T25R_L1")))

        # --- postProcessing with two start-time dirs must REFUSE.
        d8 = _forge_case(root, "T25R_L1", 0.5)
        os.makedirs(os.path.join(d8, "postProcessing", "inlet_hflux", "450"))
        chk("two postProcessing start-time dirs REFUSE (restart double-count)",
            refuses(lambda: _postproc_dat(d8, "inlet_hflux")))

        # --- the freeze check refuses an uncommitted document.
        fake = tempfile.mkdtemp(prefix="t25Rrepo_")
        try:
            subprocess.run(["git", "-C", fake, "init", "-q"],
                           capture_output=True)
            os.makedirs(os.path.join(fake, os.path.dirname(FROZEN_DOC)),
                        exist_ok=True)
            open(os.path.join(fake, FROZEN_DOC), "w").write("x\n")
            chk("an UNCOMMITTED pre-registration REFUSES (rule 2)",
                refuses(lambda: freeze_check(fake)))
        finally:
            shutil.rmtree(fake, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if fails == 0 else "FAIL", fails))
    return EXIT_OK if fails == 0 else EXIT_FAIL


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root, outp = HERE, None
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if "--json" in argv:
        i = argv.index("--json")
        outp = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    rc, out = grade(root, want)
    if outp:
        with open(outp, "w") as f:
            json.dump(dict(rung="T25R", frozen_document=FROZEN_DOC,
                           plant=PLANT, ladder_registered=False,
                           roache_classification=None, gci=None,
                           observed_order=None, results=out), f,
                      indent=1, default=str)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
