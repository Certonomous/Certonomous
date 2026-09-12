#!/usr/bin/env python3
# ===========================================================================
# VMFL072-R5 COMPARATOR  --  DRAFT, NOT FROZEN.
#
# Grades a SINGLE-GRID kinematicSingleLayer (finite-volume surface-film) run
# driven by reactingParcelFoam, against the manual's experimental film
# thickness (Roy & Jain 1989 via Ansys VM 2026R1 Table .72.1, 0.555 mm).
# Design authority: cases/ansys_verification/VMFL072-R5/PREREGISTRATION.md.
#
# STRUCTURE (so the supervisor's check-1 is a clean diff):
#   * BLOCK A -- REUSED CORE, byte-faithful to the frozen compare_vmfl072_r4a.py.
#     Proven identical at run time by _assert_reuse_faithful() (constraint 1:
#     AST equality, not eyeball). Do not edit these -- edit fails the guard.
#   * BLOCK B -- R5 kinematicSingleLayer VERDICT. Everything the model change
#     touches: the finite-VOLUME film-region geometry reader, the deltaf field
#     read, the reactingParcelFoam observer (min/max(mag(U)), residual health),
#     completion for endTime 8.0 / 160 dirs / 8000 steps, single-run survival
#     -> retention, and the live-plant-gated number.
#
# WHY R5 DIFFERS FROM R4-A (see PREREGISTRATION.md 1-3):
#   R4-A drove a FINITE-AREA film shell (velocityFilmShell, libregionFaModels)
#   whose momentum solve crashed at DILUPreconditioner::calcReciprocalD (core
#   libOpenFOAM) on a thickness-scaled singular diagonal. R5 drives the
#   FINITE-VOLUME kinematicSingleLayer (libsurfaceFilmModels): its momentum
#   diagonal is kept strictly positive at delta=0 by the bounded wall-friction
#   Sp term (laminar.C: Cw=mu/((1/3)(delta+deltaSmall)), clamp_max 5000), and
#   its linear solver is smoothSolver/symGaussSeidel, which constructs NO
#   reciprocal-diagonal preconditioner -- so frame #3 cannot fire. THIS
#   COMPARATOR DOES NOT ASSUME THE ESCAPE: C-08b measures it at run time.
#   There is NO h0 knob (retired with the finite-area shell) and NO rung ladder
#   -- R5 is ONE case, graded single-grid (no Roache triple; that is R5-B).
# ===========================================================================

import argparse
import ast
import math
import os
import re
import shutil
import sys
import tempfile

# ===========================================================================
# FROZEN CONSTANTS.  The REUSED-VALUE group must equal the frozen r4a values
# (asserted by _assert_reuse_values); the R5 group is new and cited to the
# pre-registration section that fixes it.
# ===========================================================================

# --- REUSED VALUES (identical to compare_vmfl072_r4a.py) ------------------
D_MANUAL      = 0.555e-3          # m   R5 2  Ansys VM 2026R1 Table .72.1 target (Limb A)
D_FLUENT      = 0.5497e-3         # m   CONTEXT ONLY, never a gate
BAND_A        = 2.12e-2           # -   R5 5  Limb A tolerance
T_FLOOR       = 2.7750e-07        # m   plateau ptp / station spread floor
MON_X_LO, MON_X_HI = 0.440, 0.460 # m   monitor window, 50 mm clear of the outlet
MON_Y_LO, MON_Y_HI = 0.025, 0.075 # m   the manual's 50 mm monitor width, centred
STATION_X     = (0.300, 0.350, 0.400, 0.450, 0.480)   # m
STATION_HALF  = 0.010             # m
D_MIN_ADMISSIBLE = 1.0e-06        # m   admissibility floor (dewetted monitor -> refuse)
PLANT_P       = 1.234000e-05      # m   sized from the band, never from a result
PLANT_Y_MAX   = 0.050             # m   lower half-span -> a PROPER SUBSET by area
PLANT_TOL     = 1.0e-09           # m
PLANT_MIN_MOVE = 1.0e-09          # m
PLATE_AREA    = 0.05              # m^2  0.5 m x 0.1 m, exactly
GEOM_REL_TOL  = 1.0e-12
PLANAR_REL_TOL = 1.0e-12

# --- R5 RUN CONTROL (PREREGISTRATION.md 4), fixed by apply_level.sh --------
NX, NY            = 256, 64        # film-region resolution (= plate patch)
END_TIME          = 8.0           # s   R5 4
DELTAT            = 1.0e-03        # s   adjustTimeStep no
STEPS             = 8000          # = END_TIME / DELTAT (exact, deterministic)
EXPECTED_TIME_DIRS = 160          # writeInterval 50 steps -> write every 0.05 s
PLATEAU_WINDOW_S  = 1.6           # last 20 % of endTime
EXPECTED_PLATEAU_SAMPLES = 33     # t = 6.40, 6.45, ... 8.00 inclusive
FILM_CELLS        = NX * NY       # 16384 single-layer cells

# --- R5 model paths / observer bound (PREREGISTRATION.md 3, 5) ------------
FILM_REGION   = "wallFilmRegion"
WALL_PATCH    = "region0_to_wallFilmRegion_wallFilmFaces"   # film<->primary coupled patch
LOG_NAME      = "log.reactingParcelFoam"
DELTAF        = "deltaf"           # film thickness volScalarField (kinematicSingleLayer.C:487)
MAGUF_MAX_BOUND = 50.0             # m/s  R5 5  physical U_IN=0.537; two decades above
REQUIRED_FIELDS_PRIMARY = ("U", "p", "T")
REQUIRED_FIELDS_FILM    = ("deltaf", "Uf", "Tf")

# --- the transitive dependency of the reuse guard (check-1 finding) -------
# compare_vmfl072_r4a.py is read and ast.parse'd AT RUN TIME by
# _assert_reuse_faithful (a FILE-READ dependency an import scan cannot see, so
# the freeze must declare it). Pin its frozen git blob so the AST guard cannot
# be fooled by r4a drifting on disk AND this copy drifting identically: the
# on-disk r4a is verified to hash to this blob BEFORE the AST comparison.
R4A_BLOB_SHA = "ca2c73c70ce72a9aa12cf436a482ba83246158f1"  # git hash-object == HEAD blob

# ===========================================================================
# ============================ BLOCK A -- REUSED CORE =======================
# Copied VERBATIM from the frozen compare_vmfl072_r4a.py. _assert_reuse_faithful()
# parses that file at run time and refuses if any function/class below is not
# AST-identical to its frozen twin (constraint 1). DO NOT EDIT.
# ===========================================================================


class Refuse(Exception):
    """Instrument or completion failure -> exit 2, no number produced."""


class NotAResult(Exception):
    """One-way physics gate failed -> exit 3."""


def _body(path):
    """Return the file content after the FoamFile header block."""
    try:
        s = open(path, "r").read()
    except OSError as exc:
        raise Refuse("cannot read %s: %s" % (path, exc))
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    i = s.find("FoamFile")
    if i < 0:
        raise Refuse("%s has no FoamFile header" % path)
    j = s.find("}", i)
    if j < 0:
        raise Refuse("%s has an unterminated FoamFile header" % path)
    return re.sub(r"//[^\n]*", "", s[j + 1:])


def read_points(path):
    b = _body(path)
    m = re.search(r"(\d+)\s*\(", b)
    if not m:
        raise Refuse("%s: no point count" % path)
    n = int(m.group(1))
    v = re.findall(r"\(\s*([^\s()]+)\s+([^\s()]+)\s+([^\s()]+)\s*\)", b[m.end():])
    if len(v) < n:
        raise Refuse("%s: declared %d points, found %d" % (path, n, len(v)))
    return [tuple(float(c) for c in t) for t in v[:n]]


def read_faces(path):
    b = _body(path)
    m = re.search(r"(\d+)\s*\(", b)
    if not m:
        raise Refuse("%s: no face count" % path)
    n = int(m.group(1))
    out = []
    for mm in re.finditer(r"(\d+)\s*\(([^)]*)\)", b[m.end():]):
        out.append([int(x) for x in mm.group(2).split()])
        if len(out) == n:
            break
    if len(out) != n:
        raise Refuse("%s: declared %d faces, parsed %d" % (path, n, len(out)))
    return out


def read_labels(path):
    b = _body(path)
    m = re.search(r"(\d+)\s*\(", b)
    if not m:
        raise Refuse("%s: no label count" % path)
    n = int(m.group(1))
    v = re.findall(r"-?\d+", b[m.end():])
    if len(v) < n:
        raise Refuse("%s: declared %d labels, found %d" % (path, n, len(v)))
    return [int(x) for x in v[:n]]


def read_area_scalar(path, n):
    """Read an areaScalarField internalField, uniform or nonuniform."""
    b = _body(path)
    m = re.search(r"internalField\s+nonuniform[^;]*?(\d+)\s*\(", b, flags=re.S)
    if m:
        k = int(m.group(1))
        if k != n:
            raise Refuse("%s: internalField has %d entries, mesh has %d faces"
                         % (path, k, n))
        v = re.findall(r"[-+0-9.eE]+", b[m.end():])
        if len(v) < n:
            raise Refuse("%s: internalField truncated (%d of %d)" % (path, len(v), n))
        return [float(x) for x in v[:n]]
    m = re.search(r"internalField\s+uniform\s+([-+0-9.eE]+)\s*;", b)
    if m:
        return [float(m.group(1))] * n
    raise Refuse("%s: no readable internalField" % path)


def write_area_scalar(path, values):
    """Write an areaScalarField the SAME reader can parse (used by the plants)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                 "    class areaScalarField;\n    object hf_film;\n}\n")
        fh.write("dimensions      [0 1 0 0 0 0 0];\n\n")
        fh.write("internalField   nonuniform List<scalar>\n%d\n(\n" % len(values))
        for v in values:
            fh.write("%.15e\n" % v)
        fh.write(")\n;\n\nboundaryField\n{\n}\n")


def time_dirs(case):
    out = []
    for name in os.listdir(case):
        if re.fullmatch(r"\d+(\.\d+)?", name) and os.path.isdir(os.path.join(case, name)):
            out.append((float(name), name))
    out.sort()
    return out


def window_mask(centres, xlo, xhi, ylo, yhi):
    return [i for i, c in enumerate(centres)
            if xlo <= c[0] <= xhi and ylo <= c[1] <= yhi]


def area_mean(values, areas, idx):
    if not idx:
        raise Refuse("reduction window selects zero faces")
    num = math.fsum(values[i] * areas[i] for i in idx)
    den = math.fsum(areas[i] for i in idx)
    if den <= 0.0:
        raise Refuse("reduction window has non-positive area")
    return num / den


def monitor_mean(values, centres, areas):
    idx = window_mask(centres, MON_X_LO, MON_X_HI, MON_Y_LO, MON_Y_HI)
    return area_mean(values, areas, idx), idx


def _plant_fraction(lev, idx):
    """Area fraction of the planted PROPER SUBSET within the reduction set."""
    sub = [i for i in idx if lev.centres[i][1] < PLANT_Y_MAX]
    if not sub:
        raise Refuse("PLANT: the sub-region selects ZERO faces of the window")
    if len(sub) == len(idx):
        raise Refuse("PLANT: the sub-region is the WHOLE window -- an additive "
                     "plant over exactly the reduction set cancels identically "
                     "and the control could not fail (L-487)")
    f = math.fsum(lev.areas[i] for i in sub) / math.fsum(lev.areas[i] for i in idx)
    if not (0.0 < f < 1.0):
        raise Refuse("PLANT: area fraction f = %.15e is not a proper fraction" % f)
    return sub, f


def _replant_and_reread(lev, sub, scratch):
    """Write a planted copy, RE-PARSE it through the same reader, reduce it."""
    vals = list(lev.h_end)
    for i in sub:
        vals[i] += PLANT_P
    p = os.path.join(scratch, "%s_planted" % lev.name, "hf_film")
    write_area_scalar(p, vals)
    v = read_area_scalar(p, lev.n)
    return area_mean(v, lev.areas, lev.mon_idx)


def plant_p1(lev, scratch, report):
    """P1 -- against the MONITOR reduction (an area-weighted mean)."""
    sub, f = _plant_fraction(lev, lev.mon_idx)
    d_pl = _replant_and_reread(lev, sub, scratch)
    got = d_pl - lev.dmon
    want = PLANT_P * f
    if abs(got - want) > PLANT_TOL:
        raise Refuse("P1 %s: planted shift %.9e m, expected P*f = %.9e m "
                     "(f = %.12f) -- the reader did not integrate the right "
                     "faces with the right weights" % (lev.name, got, want, f))
    report.append("  P1 %-3s fired: shift %.9e m == P*f (f = %.12f, %d of %d faces)"
                  % (lev.name, got, f, len(sub), len(lev.mon_idx)))
    return f


# --- the AST reuse guard (constraint 1) -----------------------------------
_REUSED_NAMES = (
    "Refuse", "NotAResult", "_body", "read_points", "read_faces", "read_labels",
    "read_area_scalar", "write_area_scalar", "time_dirs", "window_mask",
    "area_mean", "monitor_mean", "_plant_fraction", "_replant_and_reread",
    "plant_p1",
)
_REUSED_VALUE_NAMES = (
    "D_MANUAL", "D_FLUENT", "BAND_A", "T_FLOOR", "MON_X_LO", "MON_X_HI",
    "MON_Y_LO", "MON_Y_HI", "STATION_X", "STATION_HALF", "D_MIN_ADMISSIBLE",
    "PLANT_P", "PLANT_Y_MAX", "PLANT_TOL", "PLANT_MIN_MOVE", "PLATE_AREA",
    "GEOM_REL_TOL", "PLANAR_REL_TOL",
)


def _r4a_path():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "VMFL072-R4-A", "compare_vmfl072_r4a.py")
    if not os.path.isfile(p):
        raise Refuse("REUSE GUARD: frozen r4a comparator not found at %s "
                     "(run from the repo so the parent is on disk)" % p)
    return p


def _defs(tree):
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            out[node.name] = ast.dump(node)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out["=" + t.id] = ast.dump(node.value)
                elif (isinstance(t, ast.Tuple)
                      and isinstance(node.value, ast.Tuple)
                      and len(t.elts) == len(node.value.elts)):
                    # unpack `A, B = a, b` so tuple-assigned constants (e.g.
                    # MON_X_LO, MON_X_HI) are captured element-wise
                    for name_node, val_node in zip(t.elts, node.value.elts):
                        if isinstance(name_node, ast.Name):
                            out["=" + name_node.id] = ast.dump(val_node)
    return out


def _git_blob_sha(path):
    """The git blob sha of a file (stdlib only -- no git, no non-stdlib import):
    sha1(b'blob <len>\\0' + content). Matches `git hash-object`."""
    import hashlib
    try:
        d = open(path, "rb").read()
    except OSError as exc:
        raise Refuse("BLOB PIN: cannot read %s: %s" % (path, exc))
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


def _assert_reuse_faithful():
    """Constraint 1: the reused core is byte-faithful to frozen r4a, proven by
    AST equality (not eyeball). Refuses (exit 2) on any drift.
    First closes the AST guard's blind spot (check-1): verify the on-disk r4a
    hashes to its FROZEN blob before comparing, so 'both drifted identically'
    cannot pass."""
    r4a = _r4a_path()
    got = _git_blob_sha(r4a)
    if got != R4A_BLOB_SHA:
        raise Refuse("BLOB PIN FIRED: on-disk r4a comparator hashes %s, frozen "
                     "blob is %s -- the transitive dependency has drifted from its "
                     "freeze; the AST guard is not trustworthy until this is "
                     "resolved" % (got, R4A_BLOB_SHA))
    here = _defs(ast.parse(open(os.path.abspath(__file__)).read()))
    parent = _defs(ast.parse(open(r4a).read()))
    drift = []
    for name in _REUSED_NAMES:
        if name not in here:
            drift.append("%s missing in R5" % name)
        elif name not in parent:
            drift.append("%s missing in frozen r4a" % name)
        elif here[name] != parent[name]:
            drift.append("%s AST != frozen r4a" % name)
    for name in _REUSED_VALUE_NAMES:
        a, b = here.get("=" + name), parent.get("=" + name)
        if a is None or b is None or a != b:
            drift.append("constant %s != frozen r4a" % name)
    if drift:
        raise Refuse("REUSE GUARD (constraint 1) FIRED -- reused core not "
                     "byte-faithful to frozen r4a: " + "; ".join(drift))


# ===========================================================================
# ==================== BLOCK B -- R5 kinematicSingleLayer VERDICT ===========
# Everything the finite-area -> finite-volume model change touches. This is
# the ONLY block the supervisor reads as new at check-1.
# ===========================================================================

# --- film-region (finite-VOLUME) geometry ---------------------------------

def read_boundary(path):
    """Parse a polyMesh/boundary file into {patchName: (nFaces, startFace)}."""
    b = _body(path)
    out = {}
    for m in re.finditer(r"([A-Za-z_][\w\-]*)\s*\{([^{}]*)\}", b):
        blk = m.group(2)
        nf = re.search(r"\bnFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"\bstartFace\s+(\d+)\s*;", blk)
        if nf and sf:
            out[m.group(1)] = (int(nf.group(1)), int(sf.group(1)))
    return out


def _quad_area_centre(p):
    """Area and centroid of a planar four-vertex parallelogram (the same
    construction load_geometry uses for the faMesh face, applied to a
    film-region wall-coupled face). Refuses non-planar/non-parallelogram."""
    d02 = [p[2][k] - p[0][k] for k in range(3)]
    d13 = [p[3][k] - p[1][k] for k in range(3)]
    nvec = [0.5 * (d02[1] * d13[2] - d02[2] * d13[1]),
            0.5 * (d02[2] * d13[0] - d02[0] * d13[2]),
            0.5 * (d02[0] * d13[1] - d02[1] * d13[0])]
    a = math.sqrt(sum(c * c for c in nvec))
    if a <= 0.0:
        raise Refuse("C-17 film wall face has zero area")
    scale = math.sqrt(a)
    e1 = [p[1][k] - p[0][k] for k in range(3)]
    e2 = [p[2][k] - p[0][k] for k in range(3)]
    e3 = [p[3][k] - p[0][k] for k in range(3)]
    cr = [e1[1] * e2[2] - e1[2] * e2[1],
          e1[2] * e2[0] - e1[0] * e2[2],
          e1[0] * e2[1] - e1[1] * e2[0]]
    crn = math.sqrt(sum(c * c for c in cr))
    if crn <= 0.0:
        raise Refuse("C-17 film wall face is degenerate")
    off = abs(sum(cr[k] * e3[k] for k in range(3))) / crn
    if off > PLANAR_REL_TOL * scale:
        raise Refuse("C-17 film wall face is not planar (offset %.3e m)" % off)
    for (ia, ib), (ic, idd) in (((0, 1), (3, 2)), ((1, 2), (0, 3))):
        la = math.sqrt(sum((p[ib][k] - p[ia][k]) ** 2 for k in range(3)))
        lb = math.sqrt(sum((p[idd][k] - p[ic][k]) ** 2 for k in range(3)))
        if abs(la - lb) > PLANAR_REL_TOL * scale:
            raise Refuse("C-17 film wall face is not a parallelogram")
    centre = tuple(sum(p[j][k] for j in range(4)) / 4.0 for k in range(3))
    return a, centre


def read_checkmesh_cells(path):
    """checkMesh's OWN printed cell count for the film region -- an independent
    OpenFOAM number (C-16). Refuses if the log or the line is absent."""
    try:
        s = open(path, "r").read()
    except OSError as exc:
        raise Refuse("C-16 cannot read %s: %s" % (path, exc))
    m = re.search(r"\bcells:\s*(\d+)", s)
    if not m:
        raise Refuse("C-16 %s: no 'cells:' line from checkMesh" % path)
    return int(m.group(1))


def load_film_geometry(case):
    """Plate-projected face centres, areas and owner-cell ids of the film
    region's wall-coupled patch. C-14..C-17, three of them against
    OpenFOAM-produced numbers (patch face count, cell count, total area)."""
    reg = os.path.join(case, "constant", FILM_REGION, "polyMesh")
    pts = read_points(os.path.join(reg, "points"))
    fcs = read_faces(os.path.join(reg, "faces"))
    own = read_labels(os.path.join(reg, "owner"))
    patches = read_boundary(os.path.join(reg, "boundary"))

    if WALL_PATCH not in patches:
        raise Refuse("C-14 film region has no '%s' patch (patches: %s)"
                     % (WALL_PATCH, ", ".join(sorted(patches)) or "none"))
    nf, sf = patches[WALL_PATCH]
    if nf != FILM_CELLS:
        raise Refuse("C-14 wall patch has %d faces, level declares %d x %d = %d"
                     % (nf, NX, NY, FILM_CELLS))

    ncells = (max(own) + 1) if own else 0
    if ncells != FILM_CELLS:
        raise Refuse("C-14 film region has %d cells (max owner+1), single-layer "
                     "expects %d" % (ncells, FILM_CELLS))

    cm_cells = read_checkmesh_cells(os.path.join(case, "log.checkMesh." + FILM_REGION))
    if cm_cells != FILM_CELLS:
        raise Refuse("C-16 checkMesh reports %d film cells, expected %d"
                     % (cm_cells, FILM_CELLS))

    centres, areas, cellids = [], [], []
    for k in range(nf):
        fi = sf + k
        if fi < 0 or fi >= len(fcs):
            raise Refuse("C-17 wall face index %d out of range" % fi)
        f = fcs[fi]
        if len(f) != 4:
            raise Refuse("C-17 wall face %d has %d vertices, not 4" % (fi, len(f)))
        a, c = _quad_area_centre([pts[v] for v in f])
        cell = own[fi]
        if cell < 0 or cell >= ncells:
            raise Refuse("C-17 owner of wall face %d is out of range (%d)" % (fi, cell))
        centres.append(c)
        areas.append(a)
        cellids.append(cell)

    tot = math.fsum(areas)
    if abs(tot - PLATE_AREA) > GEOM_REL_TOL * PLATE_AREA:
        raise Refuse("C-15 sum(wall face area) = %.15e m2, plate is %.15e m2"
                     % (tot, PLATE_AREA))

    # C-16b uniform-mesh consistency (the primary blockMesh is simpleGrading
    # 1 1 1, so every plate footprint is PLATE_AREA/FILM_CELLS). Documented as
    # an INTERNAL consistency check, not an external number (the external
    # numbers are the C-14 face/cell counts and the C-15 total area).
    a_want = PLATE_AREA / FILM_CELLS
    for a in (min(areas), max(areas)):
        if abs(a - a_want) > 1.0e-9 * a_want:
            raise Refuse("C-16b wall face area %.15e != uniform %.15e "
                         "(mesh is not the registered uniform grid)" % (a, a_want))
    return centres, areas, cellids


# --- the reactingParcelFoam / kinematicSingleLayer observer ---------------
# The film Info prints, per step:  min/max(mag(U)) = a, b   (film speed)
#                                  min/max(delta)  = a, b   (thickness, CONTEXT)
# and per film solve:  smoothSolver:  Solving for Ufx, Initial residual = X,
#                      Final residual = Y, No Iterations Z
# C-08b keys on max(mag(U)) < MAGUF_MAX_BOUND AND every residual finite (the
# postponement-disguised-as-a-number guard, PREREGISTRATION.md 3/5/7).
_RE_MAGU  = re.compile(r"min/max\(mag\(U\)\)\s*=\s*([^\s,]+)\s*,\s*([^\s,]+)")
_RE_DELTA = re.compile(r"min/max\(delta\)\s*=\s*([^\s,]+)\s*,\s*([^\s,]+)")
_RE_RESID = re.compile(
    r"Solving for (Ufx|Ufy|Ufz|deltaf),\s*Initial residual = ([^\s,]+),\s*"
    r"Final residual = ([^\s,]+)")


def _pf(tok):
    """Parse a solver-printed float; NON-FINITE (nan/inf) returns as such so
    the caller can refuse -- never silently coerced."""
    try:
        return float(tok)
    except ValueError:
        return float("nan")


def observe(logpath):
    """PASSIVE parse of the solver log. Returns (rows, max_magU, bad_resid)
    where rows = (min_delta, max_delta, min_magU, max_magU) per step, and
    bad_resid is a (field, initial, final) tuple for the FIRST non-finite film
    residual or None. ALTERS NO FIELD."""
    if not os.path.isfile(logpath):
        raise Refuse("OBSERVER: no %s at %s" % (LOG_NAME, logpath))
    text = open(logpath, "r", errors="replace").read()
    deltas = _RE_DELTA.findall(text)
    magus = _RE_MAGU.findall(text)
    rows, mx = [], 0.0
    for (mnd, mxd), (mnu, mxu) in zip(deltas, magus):
        u = _pf(mxu)
        rows.append((_pf(mnd), _pf(mxd), _pf(mnu), u))
        if math.isfinite(u) and u > mx:
            mx = u
    bad_resid = None
    for field, init, fin in _RE_RESID.findall(text):
        vi, vf = _pf(init), _pf(fin)
        if not (math.isfinite(vi) and math.isfinite(vf)):
            bad_resid = (field, init, fin)
            break
    return rows, mx, bad_resid


def write_observer(case, rows):
    """Write the observer trace as an ANALYSIS artifact (touches no solver
    field). Returns the path, or None if there is nothing."""
    if not rows:
        return None
    p = os.path.join(case, "film_observer.tsv")
    with open(p, "w") as fh:
        fh.write("# step\tmin_delta\tmax_delta\tmin_magU\tmax_magU"
                 "   (delta CONTEXT ONLY; max_magU is the C-08b gate)\n")
        for k, r in enumerate(rows):
            fh.write("%d\t%.9e\t%.9e\t%.9e\t%.9e\n" % (k, r[0], r[1], r[2], r[3]))
    return p


# --- completion (rule 4), R5 paths ----------------------------------------

def check_completion(case):
    # C-01  rc == 0, captured INSIDE the detached wrapper.  R5 NOTE: the
    #       launcher wraps the solver in NO timeout (owner no-cap directive),
    #       so rc=124 carries NO cap meaning here -- any rc != 0 is a genuine
    #       failure (rc=136 SIGFPE is the five-crash signature -> POSTPONED).
    rcp = os.path.join(case, "RC.txt")
    if not os.path.isfile(rcp):
        raise Refuse("C-01: no RC.txt (the wrapper did not record an exit code)")
    m = re.search(r"rc\s*=\s*(-?\d+)", open(rcp).read())
    if not m:
        raise Refuse("C-01: RC.txt does not contain 'rc=<n>'")
    if int(m.group(1)) != 0:
        raise Refuse("C-01: solver rc = %s (rc=136 is the five-crash SIGFPE "
                     "signature)" % m.group(1))

    logp = os.path.join(case, LOG_NAME)
    if not os.path.isfile(logp):
        raise Refuse("C-02: no %s" % LOG_NAME)
    log = open(logp, "r", errors="replace").read()
    if not re.search(r"^End\s*$", log, flags=re.M):
        raise Refuse("C-02: solver log has no 'End' line")

    tds = time_dirs(case)
    if not tds:
        raise Refuse("C-03: no time directories")
    if abs(tds[-1][0] - END_TIME) > 1e-9:
        raise Refuse("C-03: last time %s != endTime %.6f" % (tds[-1][1], END_TIME))
    end_name = tds[-1][1]

    for f in REQUIRED_FIELDS_PRIMARY:
        if not os.path.isfile(os.path.join(case, end_name, f)):
            raise Refuse("C-04: missing primary field %s at endTime" % f)
    for f in REQUIRED_FIELDS_FILM:
        if not os.path.isfile(os.path.join(case, end_name, FILM_REGION, f)):
            raise Refuse("C-04: missing film field %s/%s at endTime" % (FILM_REGION, f))

    nwritten = len([t for t, _ in tds if t > 0.0])
    if nwritten != EXPECTED_TIME_DIRS:
        raise Refuse("C-05: %d written time directories, expected %d"
                     % (nwritten, EXPECTED_TIME_DIRS))

    nexec = len(re.findall(r"^ExecutionTime = ", log, flags=re.M))
    if nexec != STEPS:
        raise Refuse("C-06: %d ExecutionTime lines, registered %d steps"
                     % (nexec, STEPS))

    ref = os.path.join(case, "0", "U")
    if not os.path.isfile(ref):
        raise Refuse("C-07: no 0/U to date the run against")
    tref = os.path.getmtime(ref)
    for f in REQUIRED_FIELDS_PRIMARY:
        if os.path.getmtime(os.path.join(case, end_name, f)) <= tref:
            raise Refuse("C-07: primary %s at endTime is not newer than 0/U" % f)
    for f in REQUIRED_FIELDS_FILM:
        if os.path.getmtime(os.path.join(case, end_name, FILM_REGION, f)) <= tref:
            raise Refuse("C-07: film %s at endTime is not newer than 0/U" % f)
    return end_name, tds


def check_c08b(case):
    """SURVIVAL conjunct 2 (PREREGISTRATION.md 5): the ESCAPED-OR-POSTPONED
    instrument. max(mag(U)) < MAGUF_MAX_BOUND at every step AND every film
    residual finite. A run that completes (rc==0) but breaches either is the
    defect postponed/disguised as a number -> NOT A RESULT (never GATE REACHED).
    Note: with FOAM_SIGFPE ON, a singular diagonal usually raises rc=136 and is
    caught by C-01; this guard covers the narrow rc==0-with-nonfinite case."""
    rows, mx, bad = observe(os.path.join(case, LOG_NAME))
    if not rows:
        raise Refuse("C-08b: no 'min/max(mag(U))' lines -- boundedness unverifiable")
    if bad is not None:
        raise Refuse("C-08b: NON-FINITE film residual (Solving for %s: initial=%s "
                     "final=%s) -- a number produced over a degenerate matrix, "
                     "postponed not escaped" % bad)
    if not (mx < MAGUF_MAX_BOUND):
        raise Refuse("C-08b: film velocity RUNAWAY max|Uf| = %.6e m/s >= %.1f m/s "
                     "bound" % (mx, MAGUF_MAX_BOUND))
    return rows, mx


# --- the single film run --------------------------------------------------

class FilmRun(object):
    def __init__(self, case):
        self.name = "R5"
        self.case = case
        if not os.path.isdir(case):
            raise Refuse("no run directory at %s" % case)
        self.end_name, self.tds = check_completion(case)
        self.centres, self.areas, self.cellids = load_film_geometry(case)
        self.n = len(self.areas)
        self.h_end = self._read_thickness(self.end_name)
        self.dmon, self.mon_idx = monitor_mean(self.h_end, self.centres, self.areas)
        # C-13 admissibility: a dewetted monitor cannot yield a film thickness.
        if not (self.dmon > D_MIN_ADMISSIBLE):
            raise Refuse("C-13: delta_mon = %.6e m is not above the %.1e m "
                         "admissibility floor (dewetted monitor)"
                         % (self.dmon, D_MIN_ADMISSIBLE))

    def _read_thickness(self, name):
        """Read the film deltaf volScalarField (per CELL) and map it onto the
        wall-coupled faces via owner (per FACE, so the area weights apply)."""
        p = os.path.join(self.case, name, FILM_REGION, DELTAF)
        cellvals = read_area_scalar(p, FILM_CELLS)
        return [cellvals[c] for c in self.cellids]

    def plateau_series(self):
        t0 = END_TIME - PLATEAU_WINDOW_S - 1e-9
        series = []
        for t, name in self.tds:
            if t >= t0 and t > 0.0:
                p = os.path.join(self.case, name, FILM_REGION, DELTAF)
                if not os.path.isfile(p):
                    raise Refuse("C-10: plateau sample %s has no %s" % (name, DELTAF))
                v = self._read_thickness(name)
                series.append(area_mean(v, self.areas, self.mon_idx))
        if len(series) != EXPECTED_PLATEAU_SAMPLES:
            raise Refuse("C-10: %d plateau samples in the last %.1f s, expected %d"
                         % (len(series), PLATEAU_WINDOW_S, EXPECTED_PLATEAU_SAMPLES))
        return series

    def station_means(self):
        out = []
        for xc in STATION_X:
            idx = window_mask(self.centres, xc - STATION_HALF, xc + STATION_HALF,
                              MON_Y_LO, MON_Y_HI)
            out.append((xc, area_mean(self.h_end, self.areas, idx)))
        return out


# --- the verdict ----------------------------------------------------------

def verdict(state):
    """Plateau and station are one-way gates (they can only turn Limb A INTO
    NOT A RESULT). Limb A is the single-grid band comparison, capped at GATE
    REACHED (experimental reference; PASS needs the R5-B triple)."""
    if not state["C-10 plateau"]:
        raise NotAResult("C-10 the film did not plateau at the monitor")
    if not state["C-11 station"]:
        raise NotAResult("C-11 the film is not developed at the monitor")
    return "GATE REACHED" if state["C-18 limbA"] else "GATE FAIL"


def grade(runroot):
    _assert_reuse_faithful()   # constraint 1, even on a real grade
    out = []
    out.append("VMFL072-R5 -- kinematicSingleLayer (reactingParcelFoam), single grid 256x64")
    out.append("run root: %s" % runroot)
    out.append("")

    # observer FIRST -- it works on a crash log too (records the tell).
    try:
        rows, mx, bad = observe(os.path.join(runroot, LOG_NAME))
        write_observer(runroot, rows)
    except Refuse:
        rows, mx, bad = [], None, None

    # SURVIVAL: physics only (completion + C-08b). An INSTRUMENT fault is NOT
    # caught here -- it HARD-REFUSES below, so it is never mis-labelled
    # "does not survive" and cannot launder a false escalation to VOF.
    try:
        check_completion(runroot)
        check_c08b(runroot)
    except (Refuse, NotAResult) as exc:
        out.append("  DOES NOT SURVIVE  (max|Uf|=%s)  %s"
                   % (("%.3e" % mx) if mx is not None else "n/a", exc))
        out.append("")
        out.append("FAMILY VERDICT / ESCALATION (PREREGISTRATION.md 7):")
        out.append("  => R5 does not survive. The kinematicSingleLayer approach is")
        out.append("     ABANDONED for VMFL072; the successor is the VOF (interFoam)")
        out.append("     re-formulation, anchored to VMFL069-R2's completed triple.")
        out.append("     (rc=136 here = the SAME crash as the five-crash chain.)")
        return 3, out

    # instrument reads on a completed run. FilmRun bundles load_film_geometry +
    # deltaf read + C-13; constructed OUTSIDE the survival try so a corrupt mesh
    # or truncated field HARD-REFUSES (exit 2) rather than being mis-recorded.
    run = FilmRun(runroot)

    # LIVE PLANT GATES THE NUMBER (constraint 3, the family's first live plant).
    # A survivor cannot emit delta_mon unless a known perturbation was injected
    # into the re-read of the REAL on-disk deltaf and SEEN. plant_p1 raises
    # Refuse -> exit 2 if the reader cannot see it, BEFORE any number is printed.
    scratch = tempfile.mkdtemp(prefix="vmfl072r5_plant_")
    try:
        out.append("PLANTED CONTROL (CLAUDE.md rule 3; L-487) -- gates the number:")
        plant_p1(run, scratch, out)   # fires or refuses; the number below is downstream
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # retention (survivor, plant fired) --------------------------------------
    st = {}
    s = run.plateau_series()
    st["C-10 plateau"] = (max(s) - min(s)) <= T_FLOOR
    stn = run.station_means()
    st["C-11 station"] = (max(v for _, v in stn) - min(v for _, v in stn)) <= T_FLOOR
    d = run.dmon
    e_a = abs(d - D_MANUAL) / D_MANUAL
    st["C-18 limbA"] = e_a <= BAND_A
    la = verdict(st)   # NotAResult -> exit 3 if not plateaued/developed

    out.append("")
    out.append("  SURVIVES  delta_mon = %.9e m = %.6f mm  (max|Uf| = %.3e m/s)"
               % (d, d * 1e3, mx))
    out.append("  Limb A: e_A = %.4f %% vs manual 0.555 mm (band +/-%.2f %%) -> %s"
               % (e_a * 100, BAND_A * 100, la))
    out.append("  ESCAPED the five-crash defect: rc=0, max|Uf| < %.0f m/s, zero "
               "non-finite film residuals across %d steps." % (MAGUF_MAX_BOUND, STEPS))
    out.append("")
    out.append("FAMILY VERDICT / ESCALATION (PREREGISTRATION.md 7):")
    if la == "GATE REACHED":
        out.append("  => R5 SURVIVES in band. Carry this setup to R5-B (256x64 ->")
        out.append("     512x128 Roache triple, a SEPARATE freeze) for grid")
        out.append("     convergence and the analytical Nusselt Limb-B verification.")
    else:
        out.append("  => R5 survives but OUT of band. NOT abandonment -- a mesh/")
        out.append("     parameter question carried to R5-B before any accuracy claim.")
    out.append("")
    out.append("WHAT THIS DOES NOT ESTABLISH: no order of accuracy, no GCI, no grid")
    out.append("convergence (single grid; that is R5-B). Limb A is capped at GATE")
    out.append("REACHED -- its reference is experimental.")
    return 0, out


# ===========================================================================
# SELFTEST.  Proves LOGIC on data it fabricates (plus real R3-L3 for a reader
# sanity where available). Proves NOTHING about the INTERFACE. Footprint-bounded
# (L-548): ONE scratch root, torn down between mutants and in the finally, with a
# ceiling that REFUSES.
# ===========================================================================

_HDR = "FoamFile\n{\n version 2.0;\n format ascii;\n class %s;\n object %s;\n}\n"


def _write_film_polymesh(case, *, break_clause=None):
    """Write a MINIMAL but reader-valid single-layer film-region polyMesh:
    the NX*NY wall-coupled quads (face i owned by cell i), a two-layer point
    set, an owner list and a boundary declaring WALL_PATCH. Not a topologically
    complete mesh -- only what load_film_geometry parses."""
    reg = os.path.join(case, "constant", FILM_REGION, "polyMesh")
    os.makedirs(reg, exist_ok=True)
    dx, dy = 0.5 / NX, 0.1 / NY
    sx = 0.9 if break_clause == "C-15" else 1.0   # shrink x -> total area wrong
    idx, pts = {}, []
    for layer, z in ((0, 0.0), (1, 5.0e-4)):
        for j in range(NY + 1):
            for i in range(NX + 1):
                idx[(i, j, layer)] = len(pts)
                pts.append((i * dx * sx, j * dy, z))
    if break_clause == "C-17":
        pts[idx[(1, 1, 0)]] = (dx * sx, dy, 1.0e-3)   # non-planar wall face
    faces, owner = [], []
    for j in range(NY):
        for i in range(NX):
            faces.append([idx[(i, j, 0)], idx[(i, j + 1, 0)],
                          idx[(i + 1, j + 1, 0)], idx[(i + 1, j, 0)]])
            owner.append(j * NX + i)
    with open(os.path.join(reg, "points"), "w") as fh:
        fh.write(_HDR % ("vectorField", "points"))
        fh.write("%d\n(\n" % len(pts))
        for p in pts:
            fh.write("(%.17g %.17g %.17g)\n" % p)
        fh.write(")\n")
    with open(os.path.join(reg, "faces"), "w") as fh:
        fh.write(_HDR % ("faceList", "faces"))
        fh.write("%d\n(\n" % len(faces))
        for f in faces:
            fh.write("4(%d %d %d %d)\n" % tuple(f))
        fh.write(")\n")
    with open(os.path.join(reg, "owner"), "w") as fh:
        fh.write(_HDR % ("labelList", "owner"))
        fh.write("%d\n(\n" % len(owner))
        for o in owner:
            fh.write("%d\n" % o)
        fh.write(")\n")
    nf = len(faces) - (1 if break_clause == "C-14" else 0)
    pname = "someOtherPatch" if break_clause == "C-14miss" else WALL_PATCH
    with open(os.path.join(reg, "boundary"), "w") as fh:
        fh.write(_HDR % ("polyBoundaryMesh", "boundary"))
        fh.write("1\n(\n%s\n{\n type mappedWall;\n nFaces %d;\n startFace 0;\n}\n)\n"
                 % (pname, nf))
    cm = FILM_CELLS + (7 if break_clause == "C-16" else 0)
    with open(os.path.join(case, "log.checkMesh." + FILM_REGION), "w") as fh:
        fh.write("Mesh stats\n    points: %d\n    faces: %d\n    cells: %d\nEnd\n"
                 % (len(pts), len(faces), cm))


def _write_deltaf(path, values_or_uniform):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(_HDR % ("volScalarField", DELTAF))
        fh.write("dimensions      [0 1 0 0 0 0 0];\n")
        if isinstance(values_or_uniform, list):
            fh.write("internalField   nonuniform List<scalar>\n%d\n(\n"
                     % len(values_or_uniform))
            for v in values_or_uniform:
                fh.write("%.15e\n" % v)
            fh.write(")\n;\n")
        else:
            fh.write("internalField   uniform %.15e;\n" % values_or_uniform)
        fh.write("boundaryField\n{\n}\n")


def _fixture(case, dmon_target, *, break_clause=None, magu_max=0.54,
             resid_nan=False):
    """A REAL, parseable R5 case tree: film polyMesh + deltaf per time dir +
    reactingParcelFoam log with the observer lines. deltaf is UNIFORM (tiny)
    everywhere except the C-10 plateau mutant, which needs per-cell drift."""
    os.makedirs(case, exist_ok=True)
    _write_film_polymesh(case, break_clause=break_clause)

    # centres for the C-10 drift need the plate x of each cell (cell i = face i)
    dx, dy = 0.5 / NX, 0.1 / NY

    def cell_xy(c):
        i, j = c % NX, c // NX
        return (i + 0.5) * dx, (j + 0.5) * dy

    skip = EXPECTED_TIME_DIRS // 2 if break_clause == "C-05" else None
    for k in range(1, EXPECTED_TIME_DIRS + 1):
        if k == skip:
            continue
        t = k * (END_TIME / EXPECTED_TIME_DIRS)
        name = ("%g" % t)
        fdir = os.path.join(case, name, FILM_REGION)
        os.makedirs(fdir, exist_ok=True)
        inwin = t >= END_TIME - PLATEAU_WINDOW_S - 1e-9
        if break_clause == "C-10" and inwin:
            vals = []
            for c in range(FILM_CELLS):
                x, y = cell_xy(c)
                drift = (3.0 * T_FLOOR * ((k % 2) - 0.5)
                         if (MON_X_LO <= x <= MON_X_HI and MON_Y_LO <= y <= MON_Y_HI)
                         else 0.0)
                vals.append(dmon_target + drift)
            _write_deltaf(os.path.join(fdir, DELTAF), vals)
        else:
            _write_deltaf(os.path.join(fdir, DELTAF), dmon_target)
        # Uf, Tf: existence + mtime only
        open(os.path.join(fdir, "Uf"), "w").write(_HDR % ("volVectorField", "Uf"))
        open(os.path.join(fdir, "Tf"), "w").write(_HDR % ("volScalarField", "Tf"))
        for f in REQUIRED_FIELDS_PRIMARY:
            open(os.path.join(case, name, f), "w").write(_HDR % ("volScalarField", f))
    if break_clause == "C-03":
        os.rename(os.path.join(case, "%g" % END_TIME), os.path.join(case, "7.999"))
    if break_clause == "C-04":
        os.remove(os.path.join(case, "%g" % END_TIME, FILM_REGION, DELTAF))

    os.makedirs(os.path.join(case, "0"), exist_ok=True)
    open(os.path.join(case, "0", "U"), "w").write("x")
    t0 = os.path.getmtime(os.path.join(case, "0", "U"))
    os.utime(os.path.join(case, "0", "U"),
             (t0 + 10000, t0 + 10000) if break_clause == "C-07" else (t0, t0))
    endd = os.path.join(case, "%g" % END_TIME)
    if os.path.isdir(endd):
        for f in REQUIRED_FIELDS_PRIMARY:
            p = os.path.join(endd, f)
            if os.path.isfile(p):
                os.utime(p, (t0 + 100, t0 + 100))
        for f in REQUIRED_FIELDS_FILM:
            p = os.path.join(endd, FILM_REGION, f)
            if os.path.isfile(p):
                os.utime(p, (t0 + 100, t0 + 100))

    nsteps = STEPS if break_clause != "C-06" else STEPS - 1
    with open(os.path.join(case, LOG_NAME), "w") as fh:
        buf = []
        for s in range(nsteps):
            umax = magu_max
            if break_clause == "C-08" and s == nsteps // 2:
                umax = 8.0e12                      # a runaway on ONE step
            fin = "1.9e-11"
            if resid_nan and s == nsteps // 2:
                fin = "nan"
            buf.append("min/max(delta)     = 0, %.9e" % dmon_target)
            buf.append("min/max(mag(U))    = 0, %.9e" % umax)
            buf.append("smoothSolver:  Solving for Ufx, Initial residual = 1, "
                       "Final residual = %s, No Iterations 1" % fin)
            buf.append("smoothSolver:  Solving for deltaf, Initial residual = 1, "
                       "Final residual = 1.9e-11, No Iterations 2")
            buf.append("ExecutionTime = %d s  ClockTime = %d s" % (s, s))
        if break_clause != "C-02":
            buf.append("End")
        fh.write("\n".join(buf) + "\n")
    open(os.path.join(case, "RC.txt"), "w").write(
        "rc=136\n" if break_clause == "C-01" else "rc=0\n")


def _du_inodes(root):
    b = n = 0
    for dp, dirs, files in os.walk(root):
        n += len(dirs) + len(files)
        for f in files:
            try:
                b += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return b, n


def _enforce_footprint(root, max_bytes, max_inodes):
    b, n = _du_inodes(root)
    if b > max_bytes:
        raise Refuse("SELFTEST FOOTPRINT ceiling FIRED: peak on-disk %.1f MiB > "
                     "%.0f MiB -- the per-mutant teardown was skipped"
                     % (b / 2 ** 20, max_bytes / 2 ** 20))
    if n > max_inodes:
        raise Refuse("SELFTEST FOOTPRINT ceiling FIRED: peak inodes %d > %d"
                     % (n, max_inodes))
    return b, n


def _io_write_bytes():
    try:
        for line in open("/proc/self/io"):
            if line.startswith("write_bytes"):
                return int(line.split(":")[1])
    except OSError:
        pass
    return -1


def selftest():
    _assert_reuse_faithful()
    ok, fail = [], []
    SCRATCH = tempfile.mkdtemp(prefix="vmfl072r5_st_")
    PEAK_BYTES_BOUND = 200 * 2 ** 20
    PEAK_INODE_BOUND = 20000
    peak = {"b": 0, "i": 0}
    w0 = _io_write_bytes()

    def mk(name):
        d = os.path.join(SCRATCH, name)
        shutil.rmtree(d, ignore_errors=True)
        return d

    def sweep():
        b, n = _enforce_footprint(SCRATCH, PEAK_BYTES_BOUND, PEAK_INODE_BOUND)
        peak["b"] = max(peak["b"], b)
        peak["i"] = max(peak["i"], n)
        for name in os.listdir(SCRATCH):
            shutil.rmtree(os.path.join(SCRATCH, name), ignore_errors=True)

    def refuses(fn):
        try:
            fn()
            return False
        except Refuse:
            return True
        except NotAResult:
            return False

    def body_of(root):
        # mirror main()'s exception handling: grade() RAISES NotAResult (e.g. a
        # survivor that does not plateau) and Refuse; main turns those into exit
        # 3 / exit 2, so the selftest must too rather than abort.
        try:
            rc, lines = grade(root)
            return rc, "\n".join(lines)
        except NotAResult as exc:
            return 3, "VERDICT: NOT A RESULT (exit 3): %s" % exc
        except Refuse as exc:
            return 2, "REFUSED (exit 2): %s" % exc

    IN_BAND = D_MANUAL          # dmon exactly on the manual value -> in band, plateaued

    try:
        # 0. BLOB PIN is load-bearing: with a wrong pinned r4a blob, the reuse
        #    guard REFUSES before any AST comparison (closes the drift-together
        #    hole). The positive path is already proven: selftest() called
        #    _assert_reuse_faithful at entry and did not refuse.
        real_sha = R4A_BLOB_SHA
        globals()["R4A_BLOB_SHA"] = "0" * 40
        try:
            pin_fires = refuses(_assert_reuse_faithful)
        finally:
            globals()["R4A_BLOB_SHA"] = real_sha
        (ok if pin_fires else fail).append(
            "blob pin is load-bearing: a wrong r4a blob REFUSES (exit 2) before "
            "the AST comparison")

        # 1. a clean, in-band, surviving run grades GATE REACHED and the plant fires
        r = mk("clean")
        _fixture(r, IN_BAND)
        rc, body = body_of(r)
        (ok if rc == 0 and "GATE REACHED" in body else fail).append(
            "clean run SURVIVES in band -> GATE REACHED (rc=%d)" % rc)
        (ok if ("P1 R5" in body and "fired:" in body) else fail).append(
            "live plant P1 FIRES on the surviving run (gates the number)")
        (ok if "Carry this setup to R5-B" in body else fail).append(
            "in-band survivor -> carry to R5-B")
        (ok if "ESCAPED the five-crash defect" in body else fail).append(
            "escaped-signature line printed for a clean survivor")
        sweep()

        # 2. physics completion mutants -> DOES NOT SURVIVE -> ABANDON/VOF (exit 3)
        for clause in ("C-01", "C-02", "C-03", "C-04", "C-05", "C-06", "C-07"):
            r = mk(clause)
            _fixture(r, IN_BAND, break_clause=clause)
            rc, body = body_of(r)
            (ok if rc == 3 and "DOES NOT SURVIVE" in body and "ABANDONED" in body else fail).append(
                "physics mutant %s -> does not survive -> VOF escalation (rc=%d)"
                % (clause, rc))
            sweep()

        # 3a. C-08b RUNAWAY: a COMPLETED run with max|Uf| >= bound does not survive
        r = mk("C-08")
        _fixture(r, IN_BAND, break_clause="C-08")
        rc, body = body_of(r)
        (ok if rc == 3 and "RUNAWAY" in body else fail).append(
            "C-08b refuses a completed run with a velocity runaway (rc=%d)" % rc)
        # mutation control: WITHOUT the max|Uf| gate the runaway run SURVIVES
        real = check_c08b
        globals()["check_c08b"] = lambda case: (observe(os.path.join(case, LOG_NAME))[0],
                                                 observe(os.path.join(case, LOG_NAME))[1])
        try:
            rc2, body2 = body_of(r)
        finally:
            globals()["check_c08b"] = real
        (ok if "SURVIVES" in body2 else fail).append(
            "mutation control: WITHOUT the max|Uf| gate the runaway SURVIVES "
            "(the C-08b bound is load-bearing)")
        sweep()

        # 3b. NaN residual on a COMPLETED run does not survive; gate is load-bearing
        r = mk("nan")
        _fixture(r, IN_BAND, resid_nan=True)
        rc, body = body_of(r)
        (ok if rc == 3 and "NON-FINITE" in body else fail).append(
            "C-08b refuses a completed run with a NON-FINITE film residual (rc=%d)" % rc)
        real = check_c08b
        globals()["check_c08b"] = lambda case: (observe(os.path.join(case, LOG_NAME))[0],
                                                 observe(os.path.join(case, LOG_NAME))[1])
        try:
            rc2, body2 = body_of(r)
        finally:
            globals()["check_c08b"] = real
        (ok if "SURVIVES" in body2 else fail).append(
            "mutation control: WITHOUT the NaN/inf guard the disguised run SURVIVES "
            "(the guard is load-bearing)")
        sweep()

        # 4. instrument mutants on a COMPLETED run HARD-REFUSE (exit 2), not "no survive"
        for clause in ("C-13z", "C-14", "C-14miss", "C-15", "C-16", "C-17"):
            r = mk(clause)
            _fixture(r, 0.0 if clause == "C-13z" else IN_BAND,
                     break_clause=None if clause == "C-13z" else clause)
            (ok if refuses(lambda r=r: grade(r)) else fail).append(
                "instrument mutant %s: completed-but-corrupt HARD-REFUSES (exit 2)" % clause)
            sweep()

        # 4b. the physics/instrument split is load-bearing (C-17 passes completion,
        #     Level-equivalent FilmRun refuses on the same case)
        r = mk("split")
        _fixture(r, IN_BAND, break_clause="C-17")
        comp_ok = True
        try:
            check_completion(r)
        except (Refuse, NotAResult):
            comp_ok = False
        (ok if comp_ok else fail).append(
            "split (i): a corrupt-geometry run PASSES check_completion (not a crash)")
        (ok if refuses(lambda: FilmRun(r)) else fail).append(
            "split (ii): FilmRun RAISES on the same run -> a broad catch would "
            "mis-record it as non-survival (the split is load-bearing)")
        sweep()

        # 5. LIVE-PLANT MUTATION CONTROLS (constraint 3). The plant round-trips
        #    a PROPER SUBSET of the real deltaf VALUES through the real writer and
        #    reader (into scratch -- it never mutates the graded run). Each mutant
        #    corrupts that writer/reader; the plant must CATCH it, i.e. grade must
        #    HARD-REFUSE (exit 2), so a survivor's number is impossible without a
        #    faithful plant. The clean run (test 1) already proved the plant FIRES.
        r = mk("plantmut")
        _fixture(r, IN_BAND)
        _real_read = read_area_scalar

        def _plant_mutant(name, target, fn, note):
            real = globals()[target]
            globals()[target] = fn
            try:
                caught = refuses(lambda: grade(r))
            finally:
                globals()[target] = real
            (ok if caught else fail).append(
                "live-plant mutant [%s]: %s -> grade HARD-REFUSES (exit 2)" % (name, note))

        # (a) neutered writer: claims success, writes nothing.
        _plant_mutant("neutered-writer", "write_area_scalar",
                      lambda path, values: None,
                      "writer writes nothing")
        # (b) reader returns a constant: the planted subset never shows up.
        _plant_mutant("constant-reader", "read_area_scalar",
                      lambda path, n: [5.0e-4] * n,
                      "reader returns a constant")
        # (c) reader leaks a phantom offset INTO the planted re-read (asymmetric,
        #     so it does NOT cancel in the P*f difference).
        _plant_mutant("phantom-offset-reader", "read_area_scalar",
                      lambda path, n: [v + 1.0e-6 for v in _real_read(path, n)]
                      if "_planted" in path else _real_read(path, n),
                      "reader leaks an asymmetric phantom offset")
        # (d) the number is DOWNSTREAM of the plant: a plant that cannot fire
        #     refuses before any delta_mon is emitted.
        _plant_mutant("neutered-plant", "plant_p1",
                      lambda lev, scratch, report: (_ for _ in ()).throw(
                          Refuse("PLANT NEUTERED: reader could not see the plant")),
                      "neutered plant gates the number")
        sweep()

        # 6. Limb A band edges: just out of band -> GATE FAIL (survives, not abandon)
        r = mk("gatefail")
        _fixture(r, D_MANUAL * (1.0 + BAND_A) + 5.0 * T_FLOOR)
        rc, body = body_of(r)
        (ok if rc == 0 and "GATE FAIL" in body and "OUT of band" in body else fail).append(
            "Limb A: an out-of-band survivor is GATE FAIL, NOT abandonment (rc=%d)" % rc)
        sweep()

        # 7. C-10 plateau conjunct: a survivor that does not plateau is NOT A RESULT
        r = mk("C-10")
        _fixture(r, IN_BAND, break_clause="C-10")
        rc, body = body_of(r)
        (ok if rc == 3 and "did not plateau" in body else fail).append(
            "conjunct C-10: a survivor that does not plateau is NOT A RESULT (rc=%d)" % rc)
        sweep()

        # 8. footprint guard is load-bearing (accumulate without teardown -> FIRE)
        ctrl = mk("_fp")
        os.makedirs(ctrl, exist_ok=True)
        fired = False
        try:
            for i in range(40):
                _fixture(os.path.join(ctrl, "f%d" % i), IN_BAND)   # NO teardown
                b, n = _du_inodes(ctrl)
                peak["b"] = max(peak["b"], b)
                peak["i"] = max(peak["i"], n)
                try:
                    _enforce_footprint(ctrl, 30 * 2 ** 20, PEAK_INODE_BOUND)
                except Refuse:
                    fired = True
                    break
        finally:
            shutil.rmtree(ctrl, ignore_errors=True)
        (ok if fired else fail).append(
            "footprint guard load-bearing: accumulating fixtures FIRE the ceiling (exit 2)")

        w1 = _io_write_bytes()
        cumulative_mib = (w1 - w0) / 2 ** 20 if (w0 >= 0 and w1 >= 0) else -1.0

        print("VMFL072-R5 comparator --selftest")
        print("=" * 78)
        print("BANNER: proves the comparator's LOGIC on fabricated data. Proves")
        print("NOTHING about the INTERFACE (no reactingParcelFoam was run).")
        print("=" * 78)
        for line in ok:
            print("  PASS  %s" % line)
        for line in fail:
            print("  FAIL  %s" % line)
        print("-" * 78)
        print("FOOTPRINT (MEASURED): peak on-disk %.1f MiB (bound %d), peak inodes "
              "%d (bound %d), cumulative write_bytes %.1f MiB (/proc/self/io)"
              % (peak["b"] / 2 ** 20, PEAK_BYTES_BOUND // 2 ** 20,
                 peak["i"], PEAK_INODE_BOUND, cumulative_mib))
        print("%d passed, %d failed" % (len(ok), len(fail)))
        return 0 if not fail else 1
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--runroot")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.runroot:
        ap.error("--runroot is required unless --selftest is given")
    try:
        rc, lines = grade(a.runroot)
    except Refuse as exc:
        print("REFUSED (exit 2): %s" % exc)
        print("NO number is produced and none may be quoted. VERDICT: NOT A RESULT.")
        return 2
    except NotAResult as exc:
        print("VERDICT: NOT A RESULT (exit 3): %s" % exc)
        return 3
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())
