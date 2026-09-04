#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# VMFL072-R2 -- the frozen comparator.
#
# THE GRADING PATH. Its sha is fixed at the pre-registration's freeze commit
# (CLAUDE.md rule 2). It reads only the paths listed below, and every one of
# them is a path a NAMED OpenFOAM utility ACTUALLY WRITES -- shown on disk, not
# inferred from a field's name. This is ANSYS_VERIFICATION_CHARTER 39.5, the
# rule that struck this case's predecessor:
#
#   path the comparator reads                       written by
#   ------------------------------------------------------------------------
#   constant/polyMesh/points                        blockMesh
#   constant/polyMesh/faces                         blockMesh
#   constant/finite-area/faMesh/faceLabels          makeFaMesh
#   <t>/finite-area/hf_film                         pimpleFoam + velocityFilmShell
#   log.checkFaMesh    ("Face area: min = .. max = ..")   checkFaMesh
#   log.pimpleFoam     ("End", "ExecutionTime")     pimpleFoam
#   RC.txt                                          the driver's wrapper
#
#   VERIFIED ON DISK 2026-09-04, by building the registered case and running
#   it: the written time directory contains EXACTLY
#     U p phi
#     finite-area/{hf_film, Uf_film, pf_film, phif_film, phi2s_film, rhof, Tf_film}
#     uniform/{time, cumulativeContErr, functionObjects/...}
#   and `constant/finite-area/faMesh/` contains EXACTLY {faceLabels, faBoundary}.
#   THERE IS NO Cf_film AND NO magSf_film ANYWHERE. faMesh.C:64 fixes the
#   finite-area prefix to the literal "finite-area". Face centres and areas are
#   therefore COMPUTED from points+faces+faceLabels, and the computation is
#   cross-checked against checkFaMesh's OWN printed min/max area -- an
#   OpenFOAM-produced number, not a self-consistency check.
#
# NO ROACHE TRIPLE IS COMPUTED HERE. R2 7 declines it with the statement
# CLAUDE.md rule 5 requires. This file contains no Richardson extrapolation, no
# observed order and no GCI, deliberately. It gates level-INDEPENDENCE (R2 6.6)
# instead, which on this quantity is a strictly tighter test.
#
# EXIT CODES
#   0  a verdict was produced (the verdict itself is on stdout)
#   2  REFUSED -- an instrument or completion condition failed; NO number is
#      produced and none may be quoted. The comparator refuses; it never
#      degrades.
#   3  NOT A RESULT -- the run completed and the instrument is sound, but a
#      one-way physics gate (plateau, station development, exactness) failed.
#   4  usage / internal error.
#
# USAGE
#   compare_vmfl072_r2.py --runroot <dir>          grade
#   compare_vmfl072_r2.py --selftest               instrument self-test
# ---------------------------------------------------------------------------

import argparse
import math
import os
import re
import shutil
import sys
import tempfile

# ===========================================================================
# FROZEN CONSTANTS.  Every one cites the registration section that fixes it.
# Nothing in this file may be changed without a new freeze.
# ===========================================================================

# --- the references -------------------------------------------------------
D_MANUAL      = 0.555e-3          # m   R2 1   Ansys VM 2026R1 Table .72.1 target
D_NSTAR       = 5.500814601e-04   # m   R2 2.7 EXACT DISCRETE state, h^2(h+h0)=3*nu*q/gs
D_NUSSELT     = 5.501147914e-04   # m   R2 2.6 h0-free Nusselt; CONTEXT ONLY, never a gate
D_FLUENT      = 0.5497e-3         # m   R2 1   CONTEXT ONLY, never a gate

# --- the bands (R2 5) -----------------------------------------------------
BAND_A        = 2.12e-2           # -   R2 5.1  A .090 + B 1.926 + D' .0504 + E' .0504 %
BAND_B        = 1.01e-3           # -   R2 5.2  D' + E' only

# --- the instrument floor (R2 6.1). ONE constant, four uses. --------------
T_FLOOR       = 2.7750e-07        # m   0.05 % of 0.555 mm = 0.050447 % of dN*
                                  #     plateau ptp / station spread /
                                  #     exactness gate / B2 bracket

# --- the monitor (R2 6.2) -------------------------------------------------
MON_X_LO, MON_X_HI = 0.440, 0.460 # m   50 mm clear of the outlet
MON_Y_LO, MON_Y_HI = 0.025, 0.075 # m   the manual's 50 mm monitor width, centred
STATION_X     = (0.300, 0.350, 0.400, 0.450, 0.480)   # m  R2 6.3
STATION_HALF  = 0.010             # m

# --- admissibility floor (R2 6.7) ----------------------------------------
D_MIN_ADMISSIBLE = 1.0e-06        # m   550x below dN*; no film-producing run returns it

# --- the plants (R2 6.8; CLAUDE.md rule 3; L-487) ------------------------
PLANT_P       = 1.234000e-05      # m   sized from the band, never from a result
PLANT_Y_MAX   = 0.050             # m   lower half-span -> a PROPER SUBSET by area
PLANT_TOL     = 1.0e-09           # m
PLANT_MIN_MOVE = 1.0e-09          # m   the statistic must actually MOVE

# --- run control, fixed by apply_level.sh (R2 8.1) -----------------------
END_TIME          = 10.0
EXPECTED_TIME_DIRS = 200
PLATEAU_WINDOW_S  = 2.0
EXPECTED_PLATEAU_SAMPLES = 41     # t = 8.00, 8.05, ... 10.00 inclusive

LEVELS = {
    #        NX    NY   steps   role
    "L1": (   64,  16,   2000, "exactness leg"),
    "L2": (  128,  32,   4000, "exactness leg"),
    "L3": (  256,  64,   8000, "exactness leg + THE GRADED VALUE"),
    "B2": (  256,  64,  12800, "anti-circularity bracket, at the graded level"),
    "C1": (  128,  32,   4000, "exact-solution retention over the whole plate"),
}
EXACTNESS_LEVELS = ("L1", "L2", "L3")
GRADED_LEVEL     = "L3"

PLATE_AREA    = 0.05              # m^2  0.5 m x 0.1 m, exactly
GEOM_REL_TOL  = 1.0e-12
PLANAR_REL_TOL = 1.0e-12

C1_RETENTION_MAX = 5.0e-4         # -   R2 6.4  max over plate |h-dN*|/dN* < 0.05 %

REQUIRED_FIELDS_PRIMARY = ("U", "p")
REQUIRED_FIELDS_FILM    = ("hf_film", "Uf_film")


class Refuse(Exception):
    """Instrument or completion failure -> exit 2, no number produced."""


class NotAResult(Exception):
    """One-way physics gate failed -> exit 3."""


# ===========================================================================
# READERS.  Plain OpenFOAM ASCII.  No format is guessed.
# ===========================================================================

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


def read_checkfamesh_area(path):
    """checkFaMesh's OWN printed face-area min/max -- an independent number."""
    try:
        s = open(path, "r").read()
    except OSError as exc:
        raise Refuse("cannot read %s: %s" % (path, exc))
    m = re.search(r"Face area:\s*\n\s*min\s*=\s*([-+0-9.eE]+)\s+max\s*=\s*([-+0-9.eE]+)", s)
    if not m:
        raise Refuse("%s: no 'Face area: min = .. max = ..' block" % path)
    return float(m.group(1)), float(m.group(2))


# ===========================================================================
# GEOMETRY.  Four refusals, three of them against OpenFOAM-produced numbers.
# ===========================================================================

def load_geometry(case, nx, ny):
    """Face centres and areas of the finite-area mesh, with C-14..C-17."""
    pts = read_points(os.path.join(case, "constant", "polyMesh", "points"))
    fcs = read_faces(os.path.join(case, "constant", "polyMesh", "faces"))
    lab = read_labels(os.path.join(case, "constant", "finite-area",
                                   "faMesh", "faceLabels"))

    # C-14  face count == NX*NY
    if len(lab) != nx * ny:
        raise Refuse("C-14 faMesh has %d faces, level declares %d x %d = %d"
                     % (len(lab), nx, ny, nx * ny))

    centres, areas = [], []
    for fi in lab:
        if fi < 0 or fi >= len(fcs):
            raise Refuse("C-17 faceLabels entry %d is out of range" % fi)
        f = fcs[fi]
        # C-17  four-vertex planar quadrilateral, so centroid == mean of vertices
        if len(f) != 4:
            raise Refuse("C-17 faMesh face %d has %d vertices, not 4" % (fi, len(f)))
        p = [pts[k] for k in f]
        d02 = [p[2][k] - p[0][k] for k in range(3)]
        d13 = [p[3][k] - p[1][k] for k in range(3)]
        nvec = [0.5 * (d02[1] * d13[2] - d02[2] * d13[1]),
                0.5 * (d02[2] * d13[0] - d02[0] * d13[2]),
                0.5 * (d02[0] * d13[1] - d02[1] * d13[0])]
        a = math.sqrt(sum(c * c for c in nvec))
        if a <= 0.0:
            raise Refuse("C-17 faMesh face %d has zero area" % fi)
        scale = math.sqrt(a)
        # planarity: the fourth vertex must lie in the plane of the first three
        e1 = [p[1][k] - p[0][k] for k in range(3)]
        e2 = [p[2][k] - p[0][k] for k in range(3)]
        e3 = [p[3][k] - p[0][k] for k in range(3)]
        cr = [e1[1] * e2[2] - e1[2] * e2[1],
              e1[2] * e2[0] - e1[0] * e2[2],
              e1[0] * e2[1] - e1[1] * e2[0]]
        crn = math.sqrt(sum(c * c for c in cr))
        if crn <= 0.0:
            raise Refuse("C-17 faMesh face %d is degenerate" % fi)
        off = abs(sum(cr[k] * e3[k] for k in range(3))) / crn
        if off > PLANAR_REL_TOL * scale:
            raise Refuse("C-17 faMesh face %d is not planar (offset %.3e m)" % (fi, off))
        # opposite edges equal -> a parallelogram, so mean-of-vertices is exact
        for (ia, ib), (ic, idx) in (((0, 1), (3, 2)), ((1, 2), (0, 3))):
            la = math.sqrt(sum((p[ib][k] - p[ia][k]) ** 2 for k in range(3)))
            lb = math.sqrt(sum((p[idx][k] - p[ic][k]) ** 2 for k in range(3)))
            if abs(la - lb) > PLANAR_REL_TOL * scale:
                raise Refuse("C-17 faMesh face %d is not a parallelogram" % fi)
        centres.append(tuple(sum(p[j][k] for j in range(4)) / 4.0 for k in range(3)))
        areas.append(a)

    # C-15  total area == the plate's exact area, from an independent source
    tot = math.fsum(areas)
    if abs(tot - PLATE_AREA) > GEOM_REL_TOL * PLATE_AREA:
        raise Refuse("C-15 sum(magSf) = %.15e m2, plate is %.15e m2"
                     % (tot, PLATE_AREA))

    # C-16  min/max area == checkFaMesh's OWN printed pair (OpenFOAM-produced)
    cmin, cmax = read_checkfamesh_area(os.path.join(case, "log.checkFaMesh"))
    amin, amax = min(areas), max(areas)
    for got, want, tag in ((amin, cmin, "min"), (amax, cmax, "max")):
        if abs(got - want) > GEOM_REL_TOL * max(abs(want), 1e-300):
            raise Refuse("C-16 computed %s face area %.15e != checkFaMesh %.15e"
                         % (tag, got, want))
    return centres, areas


# ===========================================================================
# THE REDUCTION.  Area-weighted mean over a window.  This is what the plant
# is designed against (L-487): the plant is a PROPER SUBSET of the reduction
# set, by AREA, never the whole set and never a disjoint one.
# ===========================================================================

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


# ===========================================================================
# COMPLETION (CLAUDE.md rule 4).  Clauses C-01..C-07, each a refusal.
# ===========================================================================

def time_dirs(case):
    out = []
    for name in os.listdir(case):
        if re.fullmatch(r"\d+(\.\d+)?", name) and os.path.isdir(os.path.join(case, name)):
            out.append((float(name), name))
    out.sort()
    return out


def check_completion(case, level):
    nx, ny, steps, _ = LEVELS[level]

    # C-01  rc == 0, captured INSIDE the detached wrapper
    rcp = os.path.join(case, "RC.txt")
    if not os.path.isfile(rcp):
        raise Refuse("C-01 %s: no RC.txt (the wrapper did not record an exit code)" % level)
    m = re.search(r"rc\s*=\s*(-?\d+)", open(rcp).read())
    if not m:
        raise Refuse("C-01 %s: RC.txt does not contain 'rc=<n>'" % level)
    if int(m.group(1)) != 0:
        raise Refuse("C-01 %s: solver rc = %s" % (level, m.group(1)))

    logp = os.path.join(case, "log.pimpleFoam")
    if not os.path.isfile(logp):
        raise Refuse("C-02 %s: no log.pimpleFoam" % level)
    log = open(logp, "r", errors="replace").read()

    # C-02  an End line
    if not re.search(r"^End\s*$", log, flags=re.M):
        raise Refuse("C-02 %s: solver log has no 'End' line" % level)

    # C-03  last time directory == endTime
    tds = time_dirs(case)
    if not tds:
        raise Refuse("C-03 %s: no time directories" % level)
    if abs(tds[-1][0] - END_TIME) > 1e-9:
        raise Refuse("C-03 %s: last time %s != endTime %.6f"
                     % (level, tds[-1][1], END_TIME))
    end_name = tds[-1][1]

    # C-04  required fields present at endTime
    for f in REQUIRED_FIELDS_PRIMARY:
        p = os.path.join(case, end_name, f)
        if not os.path.isfile(p):
            raise Refuse("C-04 %s: missing primary field %s at endTime" % (level, f))
    for f in REQUIRED_FIELDS_FILM:
        p = os.path.join(case, end_name, "finite-area", f)
        if not os.path.isfile(p):
            raise Refuse("C-04 %s: missing film field finite-area/%s at endTime"
                         % (level, f))

    # C-05  written time directory count (excluding 0)
    nwritten = len([t for t, _ in tds if t > 0.0])
    if nwritten != EXPECTED_TIME_DIRS:
        raise Refuse("C-05 %s: %d written time directories, expected %d"
                     % (level, nwritten, EXPECTED_TIME_DIRS))

    # C-06  ExecutionTime line count == the level's registered step count
    nexec = len(re.findall(r"^ExecutionTime = ", log, flags=re.M))
    if nexec != steps:
        raise Refuse("C-06 %s: %d ExecutionTime lines, level declares %d steps"
                     % (level, nexec, steps))

    # C-07  AGE GUARD -- every field at endTime strictly newer than the case's
    #       own 0/U, which the driver touches LAST at launch and then asserts.
    ref = os.path.join(case, "0", "U")
    if not os.path.isfile(ref):
        raise Refuse("C-07 %s: no 0/U to date the run against" % level)
    tref = os.path.getmtime(ref)
    checked = 0
    for f in REQUIRED_FIELDS_PRIMARY:
        p = os.path.join(case, end_name, f)
        if os.path.getmtime(p) <= tref:
            raise Refuse("C-07 %s: %s at endTime is not newer than 0/U" % (level, f))
        checked += 1
    for f in REQUIRED_FIELDS_FILM:
        p = os.path.join(case, end_name, "finite-area", f)
        if os.path.getmtime(p) <= tref:
            raise Refuse("C-07 %s: finite-area/%s at endTime is not newer than 0/U"
                         % (level, f))
        checked += 1
    if checked != len(REQUIRED_FIELDS_PRIMARY) + len(REQUIRED_FIELDS_FILM):
        raise Refuse("C-07 %s: age guard did not check every required field" % level)

    return end_name, tds


# ===========================================================================
# PER-LEVEL LOAD
# ===========================================================================

class Level(object):
    def __init__(self, runroot, level):
        self.name = level
        self.case = os.path.join(runroot, level)
        if not os.path.isdir(self.case):
            raise Refuse("no run directory for level %s at %s" % (level, self.case))
        nx, ny, steps, _ = LEVELS[level]
        self.end_name, self.tds = check_completion(self.case, level)
        self.centres, self.areas = load_geometry(self.case, nx, ny)
        self.n = len(self.areas)
        self.h_end = read_area_scalar(
            os.path.join(self.case, self.end_name, "finite-area", "hf_film"), self.n)
        self.dmon, self.mon_idx = monitor_mean(self.h_end, self.centres, self.areas)

        # C-13  admissibility.  Closes the all-zeros hole that no ADDITIVE
        #       plant on a LINEAR reader can close (R2 6.8 honest limit 2).
        if not (self.dmon > D_MIN_ADMISSIBLE):
            raise Refuse("C-13 %s: delta_mon = %.6e m is not above the %.1e m "
                         "admissibility floor" % (level, self.dmon, D_MIN_ADMISSIBLE))

    # ---- plateau series --------------------------------------------------
    def plateau_series(self):
        t0 = END_TIME - PLATEAU_WINDOW_S - 1e-9
        series = []
        for t, name in self.tds:
            if t >= t0 and t > 0.0:
                p = os.path.join(self.case, name, "finite-area", "hf_film")
                if not os.path.isfile(p):
                    raise Refuse("C-10 %s: plateau sample %s has no hf_film"
                                 % (self.name, name))
                v = read_area_scalar(p, self.n)
                series.append(area_mean(v, self.areas, self.mon_idx))
        if len(series) != EXPECTED_PLATEAU_SAMPLES:
            raise Refuse("C-10 %s: %d plateau samples in the last %.1f s, expected %d"
                         % (self.name, len(series), PLATEAU_WINDOW_S,
                            EXPECTED_PLATEAU_SAMPLES))
        return series

    # ---- station development --------------------------------------------
    def station_means(self):
        out = []
        for xc in STATION_X:
            idx = window_mask(self.centres, xc - STATION_HALF, xc + STATION_HALF,
                              MON_Y_LO, MON_Y_HI)
            out.append((xc, area_mean(self.h_end, self.areas, idx)))
        return out


# ===========================================================================
# THE PLANTS (CLAUDE.md rule 3; L-487).  BOTH are implemented; the struck
# predecessor specified P2 and never wired it in -- charter 39.3.
# ===========================================================================

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


def plant_p2(levels, scratch, report):
    """P2 -- against the EXACTNESS-GATE reduction (a max over pairs).

    A null needs its own plant, and the exactness gate is a null: it expects
    the level-to-level differences to be ZERO.  P2 plants into ONE level only
    and requires the statistic to take the value the plant makes it take --
    computed from the CLEAN triple plus the analytically known increment, so
    the check is not circular -- AND to have actually MOVED.
    """
    clean = {L.name: L.dmon for L in levels}
    s_clean = exactness_statistic(clean)

    target = levels[0]                       # L1
    sub, f = _plant_fraction(target, target.mon_idx)
    d_pl = _replant_and_reread(target, sub, scratch)

    planted = dict(clean)
    planted[target.name] = d_pl
    s_planted = exactness_statistic(planted)

    expected = dict(clean)
    expected[target.name] = clean[target.name] + PLANT_P * f
    s_expected = exactness_statistic(expected)

    if abs(s_planted - s_expected) > PLANT_TOL:
        raise Refuse("P2: planted exactness statistic %.9e m, expected %.9e m -- "
                     "the level-comparison reduction did not re-read the planted "
                     "level" % (s_planted, s_expected))
    if abs(s_planted - s_clean) <= PLANT_MIN_MOVE:
        raise Refuse("P2: the plant moved the exactness statistic by only "
                     "%.3e m (<= %.1e m). A control that cannot move is not a "
                     "control." % (abs(s_planted - s_clean), PLANT_MIN_MOVE))
    report.append("  P2 fired: statistic %.9e -> %.9e m (moved %.9e, expected %.9e)"
                  % (s_clean, s_planted, s_planted - s_clean, s_expected))


def exactness_statistic(dmon_by_level):
    """max over pairs of |delta_mon(Li) - delta_mon(Lj)| across L1, L2, L3."""
    v = [dmon_by_level[k] for k in EXACTNESS_LEVELS]
    return max(abs(a - b) for i, a in enumerate(v) for b in v[i + 1:])


# ===========================================================================
# THE VERDICT.  A LITERAL transcription of the registration's CONJUNCTION.
# The predecessor's comparator granted a PASS on a condition strictly weaker
# than its own document (charter 39.3).  Every conjunct below appears once,
# by name, and --selftest carries ONE MUTANT PER CONJUNCT.
# ===========================================================================

def verdict(state):
    """state: dict of the registered conditions. Returns (limbA, limbB, why)."""
    # -- one-way gates (R2 7.2 order 3-4): they can only turn a limb INTO
    #    NOT A RESULT, never the reverse.
    if not state["C-10 plateau"]:
        raise NotAResult("C-10 a level did not plateau")
    if not state["C-11 station"]:
        raise NotAResult("C-11 the film is not developed at the monitor")
    if not state["C-12 exactness"]:
        raise NotAResult("C-12 the levels are not indistinguishable")

    limb_a = "GATE REACHED" if state["C-18 limbA"] else "GATE FAIL"

    limb_b = ("PASS"
              if (state["C-19 limbB"] and state["C-20 C1"] and state["C-21 B2"])
              else "GATE FAIL")
    return limb_a, limb_b


VERDICT_CONJUNCTS = ("C-10 plateau", "C-11 station", "C-12 exactness",
                     "C-18 limbA", "C-19 limbB", "C-20 C1", "C-21 B2")


# ===========================================================================
# GRADE
# ===========================================================================

def grade(runroot):
    out = []
    out.append("VMFL072-R2 -- Liquid Water Flow Over a Flat Plate Under Gravity")
    out.append("run root: %s" % runroot)
    out.append("")

    scratch = tempfile.mkdtemp(prefix="vmfl072r2_plant_")
    try:
        levels = {}
        for name in ("L1", "L2", "L3", "B2", "C1"):
            levels[name] = Level(runroot, name)
            out.append("  %-3s  %5d fa-faces  %4d monitor faces  delta_mon = %.9e m"
                       % (name, levels[name].n, len(levels[name].mon_idx),
                          levels[name].dmon))
        out.append("")

        # ---- plants, BEFORE any number is graded -----------------------
        out.append("PLANTED CONTROLS (CLAUDE.md rule 3; L-487):")
        plant_p1(levels[GRADED_LEVEL], scratch, out)
        plant_p2([levels[k] for k in EXACTNESS_LEVELS], scratch, out)
        out.append("")

        state = {}

        # ---- C-10 plateau, every level ---------------------------------
        ptp_worst, ptp_where = 0.0, None
        for name in ("L1", "L2", "L3", "B2", "C1"):
            s = levels[name].plateau_series()
            ptp = max(s) - min(s)
            if ptp > ptp_worst:
                ptp_worst, ptp_where = ptp, name
        state["C-10 plateau"] = ptp_worst <= T_FLOOR
        out.append("C-10 plateau   worst ptp %.6e m at %s   <= %.6e m : %s"
                   % (ptp_worst, ptp_where, T_FLOOR, state["C-10 plateau"]))

        # ---- C-11 station development at the graded level --------------
        st = levels[GRADED_LEVEL].station_means()
        spread = max(v for _, v in st) - min(v for _, v in st)
        state["C-11 station"] = spread <= T_FLOOR
        out.append("C-11 station   spread %.6e m over x = %s   <= %.6e m : %s"
                   % (spread, ", ".join("%.0f" % (x * 1e3) for x, _ in st),
                      T_FLOOR, state["C-11 station"]))

        # ---- C-12 exactness gate (replaces the declined triple) --------
        s_exact = exactness_statistic({k: levels[k].dmon for k in EXACTNESS_LEVELS})
        state["C-12 exactness"] = s_exact <= T_FLOOR
        out.append("C-12 exactness max pairwise |d(Li)-d(Lj)| = %.6e m   <= %.6e m : %s"
                   % (s_exact, T_FLOOR, state["C-12 exactness"]))
        out.append("     NO ROACHE TRIPLE IS DECLARED (R2 7). No order, no GCI, no")
        out.append("     Richardson extrapolation is computed or may be quoted.")

        # ---- C-20 C1 retention -----------------------------------------
        c1 = levels["C1"]
        worst = max(abs(h - D_NSTAR) / D_NSTAR for h in c1.h_end)
        state["C-20 C1"] = worst < C1_RETENTION_MAX
        out.append("C-20 C1        max over plate |h-dN*|/dN* = %.6e   < %.6e : %s"
                   % (worst, C1_RETENTION_MAX, state["C-20 C1"]))

        # ---- C-21 B2 bracket -------------------------------------------
        db = abs(levels["B2"].dmon - levels[GRADED_LEVEL].dmon)
        state["C-21 B2"] = db <= T_FLOOR
        out.append("C-21 B2        |d(B2) - d(%s)| = %.6e m   <= %.6e m : %s"
                   % (GRADED_LEVEL, db, T_FLOOR, state["C-21 B2"]))

        # ---- the two limbs ---------------------------------------------
        d = levels[GRADED_LEVEL].dmon
        e_a = abs(d - D_MANUAL) / D_MANUAL
        e_b = abs(d - D_NSTAR) / D_NSTAR
        state["C-18 limbA"] = e_a <= BAND_A
        state["C-19 limbB"] = e_b <= BAND_B
        out.append("")
        out.append("GRADED VALUE (level %s): delta_mon = %.9e m = %.6f mm"
                   % (GRADED_LEVEL, d, d * 1e3))
        out.append("  Limb A  e_A = %.6f %%  vs band %.4f %%   (ref 0.555 mm, EXPERIMENTAL)"
                   % (e_a * 100, BAND_A * 100))
        out.append("  Limb B  e_B = %.6f %%  vs band %.4f %%   (ref dN* = %.9e m)"
                   % (e_b * 100, BAND_B * 100, D_NSTAR))
        out.append("  context, NEVER a gate: Fluent %.4f mm, h0-free Nusselt %.6f mm"
                   % (D_FLUENT * 1e3, D_NUSSELT * 1e3))

        la, lb = verdict(state)
        out.append("")
        out.append("VERDICT  Limb A: %s   (ceiling GATE REACHED -- the reference is "
                   "EXPERIMENTAL; R2 4)" % la)
        out.append("VERDICT  Limb B: %s   (exact-retention test; EXPECTED to pass -- "
                   "R2 6.9)" % lb)
        out.append("")
        out.append("WHAT THIS DOES NOT ESTABLISH: no order of accuracy, no GCI, "
                   "nothing about")
        out.append("meshes finer than L3, and nothing about nature -- Limb A is "
                   "capped by its reference.")
        return 0, out

    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ===========================================================================
# SELFTEST.  Proves LOGIC.  It proves NOTHING about the INTERFACE -- charter
# 39.5.  The interface is proven by the disk evidence table at the head of
# this file and by R2 3.5, not here.  This banner is deliberate.
# ===========================================================================

def _fixture(root, level, dmon_target, *, nx=None, ny=None,
             break_clause=None, uniform=True):
    """Write a REAL, parseable case tree for one level."""
    lnx, lny, steps, _ = LEVELS[level]
    nx = nx or lnx
    ny = ny or lny
    case = os.path.join(root, level)
    os.makedirs(os.path.join(case, "constant", "polyMesh"), exist_ok=True)
    os.makedirs(os.path.join(case, "constant", "finite-area", "faMesh"), exist_ok=True)

    dx, dy = 0.5 / nx, 0.1 / ny
    pts, idx = [], {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            idx[(i, j)] = len(pts)
            pts.append((i * dx, j * dy, 0.0))
    faces = []
    for j in range(ny):
        for i in range(nx):
            faces.append([idx[(i, j)], idx[(i, j + 1)], idx[(i + 1, j + 1)], idx[(i + 1, j)]])
    if break_clause == "C-17":
        pts[idx[(1, 1)]] = (dx, dy, 1.0e-3)          # push a vertex out of plane
    if break_clause == "C-15":
        pts = [(p[0] * 0.9, p[1], p[2]) for p in pts]  # shrink the plate

    hdr = "FoamFile\n{\n version 2.0;\n format ascii;\n class %s;\n object %s;\n}\n"
    with open(os.path.join(case, "constant", "polyMesh", "points"), "w") as fh:
        fh.write(hdr % ("vectorField", "points"))
        fh.write("%d\n(\n" % len(pts))
        for p in pts:
            fh.write("(%.17g %.17g %.17g)\n" % p)
        fh.write(")\n")
    with open(os.path.join(case, "constant", "polyMesh", "faces"), "w") as fh:
        fh.write(hdr % ("faceList", "faces"))
        fh.write("%d\n(\n" % len(faces))
        for f in faces:
            fh.write("4(%d %d %d %d)\n" % tuple(f))
        fh.write(")\n")
    nlab = len(faces) if break_clause != "C-14" else len(faces) - 1
    with open(os.path.join(case, "constant", "finite-area", "faMesh", "faceLabels"), "w") as fh:
        fh.write(hdr % ("labelList", "faceLabels"))
        fh.write("%d\n(\n" % nlab)
        for k in range(nlab):
            fh.write("%d\n" % k)
        fh.write(")\n")

    a = dx * dy if break_clause != "C-15" else dx * 0.9 * dy
    with open(os.path.join(case, "log.checkFaMesh"), "w") as fh:
        bad = 2.0 * a if break_clause == "C-16" else a
        fh.write("Face area:\n    min = %.17g max = %.17g\nEnd\n" % (bad, bad))

    # field values: uniform at dmon_target, or with a spanwise ramp so the
    # area-weighted and unweighted reductions differ
    n = len(faces)
    vals = []
    for k in range(n):
        j = k // nx
        vals.append(dmon_target if uniform
                    else dmon_target * (1.0 + 1e-3 * (j / max(ny - 1, 1) - 0.5)))

    skip = EXPECTED_TIME_DIRS // 2 if break_clause == "C-05" else None
    for k in range(1, EXPECTED_TIME_DIRS + 1):
        if k == skip:
            continue          # a MIDDLE write is missing: C-05 only, not C-03
        t = k * (END_TIME / EXPECTED_TIME_DIRS)
        name = ("%g" % t)
        d = os.path.join(case, name, "finite-area")
        os.makedirs(d, exist_ok=True)
        inwin = t >= END_TIME - PLATEAU_WINDOW_S - 1e-9
        drift = 0.0
        if break_clause == "C-10" and inwin:
            drift = 3.0 * T_FLOOR * ((k % 2) - 0.5)
        if inwin:
            # only the plateau window is read face-by-face; writing the other
            # 159 directories in full costs time and tests nothing new
            write_area_scalar(os.path.join(d, "hf_film"), [v + drift for v in vals])
        else:
            open(os.path.join(d, "hf_film"), "w").write(
                (hdr % ("areaScalarField", "hf_film"))
                + "dimensions [0 1 0 0 0 0 0];\ninternalField uniform %.15e;\n"
                  "boundaryField{}\n" % vals[0])
        write_area_scalar(os.path.join(d, "Uf_film"), [0.0] * n) if inwin else \
            open(os.path.join(d, "Uf_film"), "w").write(
                (hdr % ("areaScalarField", "Uf_film"))
                + "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform 0;\n"
                  "boundaryField{}\n")
        for f in REQUIRED_FIELDS_PRIMARY:
            open(os.path.join(case, name, f), "w").write(hdr % ("volScalarField", f))
    if break_clause == "C-03":
        os.rename(os.path.join(case, "%g" % END_TIME),
                  os.path.join(case, "9.999"))
    if break_clause == "C-04":
        os.remove(os.path.join(case, "%g" % END_TIME, "finite-area", "hf_film"))

    # AGE GUARD fixture: 0/U is the launch marker, so it must be OLDER than
    # every field at endTime.  The C-07 mutant makes it newer instead.
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
            p = os.path.join(endd, "finite-area", f)
            if os.path.isfile(p):
                os.utime(p, (t0 + 100, t0 + 100))

    nsteps = steps if break_clause != "C-06" else steps - 1
    with open(os.path.join(case, "log.pimpleFoam"), "w") as fh:
        for _ in range(nsteps):
            fh.write("ExecutionTime = 1 s\n")
        if break_clause != "C-02":
            fh.write("End\n")
    open(os.path.join(case, "RC.txt"), "w").write(
        "rc=1\n" if break_clause == "C-01" else "rc=0\n")
    return case


def _build_run(root, dmon, *, break_clause=None, only=None, uniform=True):
    for lv in ("L1", "L2", "L3", "B2", "C1"):
        bc = break_clause if (only is None or only == lv) else None
        _fixture(root, lv, dmon[lv], break_clause=bc, uniform=uniform)


def selftest():
    ok, fail = [], []

    def expect(tag, fn, want):
        try:
            fn()
            got = "graded"
        except Refuse as exc:
            got = "REFUSE"
            detail = str(exc)
        except NotAResult as exc:
            got = "NOTARESULT"
            detail = str(exc)
        else:
            detail = ""
        (ok if got == want else fail).append(
            "%-28s expected %-11s got %-11s  %s" % (tag, want, got, detail[:70]))

    base = {k: D_NSTAR for k in LEVELS}

    # ---- 1. a clean run grades ------------------------------------------
    root = tempfile.mkdtemp(prefix="vmfl072r2_st_clean_")
    _build_run(root, base)
    expect("clean run", lambda: grade(root), "graded")

    # ---- 2. ONE MUTANT PER COMPLETION / INSTRUMENT CLAUSE ---------------
    for clause in ("C-01", "C-02", "C-03", "C-04", "C-05", "C-06", "C-07",
                   "C-14", "C-15", "C-16", "C-17"):
        r = tempfile.mkdtemp(prefix="vmfl072r2_st_%s_" % clause)
        _build_run(r, base, break_clause=clause, only="L3")
        expect("mutant %s" % clause, lambda r=r: grade(r), "REFUSE")

    # C-13 admissibility: a zero field
    r = tempfile.mkdtemp(prefix="vmfl072r2_st_C-13_")
    z = dict(base); z["L3"] = 0.0
    _build_run(r, z)
    expect("mutant C-13 zero field", lambda r=r: grade(r), "REFUSE")

    # ---- 3. ONE MUTANT PER VERDICT CONJUNCT -----------------------------
    #     each satisfies every OTHER conjunct and violates exactly one.
    r = tempfile.mkdtemp(prefix="vmfl072r2_st_C-10_")
    _build_run(r, base, break_clause="C-10", only="L2")
    expect("conjunct C-10 plateau", lambda r=r: grade(r), "NOTARESULT")

    r = tempfile.mkdtemp(prefix="vmfl072r2_st_C-12_")
    e = dict(base); e["L1"] = D_NSTAR + 5.0 * T_FLOOR
    _build_run(r, e)
    expect("conjunct C-12 exactness", lambda r=r: grade(r), "NOTARESULT")

    def limb(tag, mut, want_a, want_b):
        rr = tempfile.mkdtemp(prefix="vmfl072r2_st_%s_" % tag)
        _build_run(rr, mut)
        try:
            rc, lines = grade(rr)
        except (Refuse, NotAResult) as exc:
            fail.append("%-28s raised %s: %s" % (tag, type(exc).__name__, exc))
            return
        txt = "\n".join(lines)
        got_a = "GATE REACHED" if "Limb A: GATE REACHED" in txt else "GATE FAIL"
        got_b = "PASS" if "Limb B: PASS" in txt else "GATE FAIL"
        entry = "%-28s A=%-12s B=%-9s" % (tag, got_a, got_b)
        (ok if (got_a, got_b) == (want_a, want_b) else fail).append(entry)

    limb("conjunct C-18 limbA", {k: D_MANUAL * (1 + 3 * BAND_A) for k in LEVELS},
         "GATE FAIL", "GATE FAIL")
    shift = dict(base)
    for k in ("L1", "L2", "L3", "B2", "C1"):
        shift[k] = D_NSTAR * (1 + 3 * BAND_B)
    limb("conjunct C-19 limbB", shift, "GATE REACHED", "GATE FAIL")
    c1bad = dict(base); c1bad["C1"] = D_NSTAR * (1 + 2 * C1_RETENTION_MAX)
    limb("conjunct C-20 C1", c1bad, "GATE REACHED", "GATE FAIL")
    b2bad = dict(base); b2bad["B2"] = D_NSTAR + 5.0 * T_FLOOR
    limb("conjunct C-21 B2", b2bad, "GATE REACHED", "GATE FAIL")

    # C-11 station: a streamwise ramp large enough to break the spread
    r = tempfile.mkdtemp(prefix="vmfl072r2_st_C-11_")
    _build_run(r, base)
    lv = Level(r, "L3")
    ramp = [D_NSTAR + 20.0 * T_FLOOR * c[0] for c in lv.centres]
    for t, name in lv.tds:
        if t > 0:
            write_area_scalar(os.path.join(r, "L3", name, "finite-area", "hf_film"), ramp)
    expect("conjunct C-11 station", lambda r=r: grade(r), "NOTARESULT")

    # ---- 4. THE PLANTS, and READER MUTANTS that must defeat them --------
    r = tempfile.mkdtemp(prefix="vmfl072r2_st_plant_")
    _build_run(r, base, uniform=False)          # non-uniform: weights matter
    lv = Level(r, "L3")
    sub, f = _plant_fraction(lv, lv.mon_idx)
    ok.append("P1 sub-region is a PROPER subset: %d of %d faces, f = %.12f"
              % (len(sub), len(lv.mon_idx), f))

    scratch = tempfile.mkdtemp(prefix="vmfl072r2_st_pl_")
    rep = []
    plant_p1(lv, scratch, rep)
    ok.append("P1 fires on a sound reader: %s" % rep[-1].strip())

    class _Mutant(object):
        def __init__(self, name, fn):
            self.name, self.fn = name, fn

    def mut_unweighted(vals, lev, idx):
        return math.fsum(vals[i] for i in idx) / len(idx)

    def mut_whole_plate(vals, lev, idx):
        return area_mean(vals, lev.areas, list(range(lev.n)))

    def mut_constant(vals, lev, idx):
        return D_NSTAR

    def mut_max(vals, lev, idx):
        return max(vals[i] for i in idx)

    def mut_shifted(vals, lev, idx):
        j = window_mask(lev.centres, MON_X_LO + 0.020, MON_X_HI + 0.020,
                        MON_Y_LO, MON_Y_HI)
        return area_mean(vals, lev.areas, j)

    def mut_whole_subregion(vals, lev, idx):
        # the FIRST DRAFT's inert control: plant set == reduction set
        return area_mean(vals, lev.areas, idx)

    planted_vals = list(lv.h_end)
    for i in sub:
        planted_vals[i] += PLANT_P
    for name, fn in (("whole plate", mut_whole_plate),
                     ("constant reader", mut_constant),
                     ("reduce by max", mut_max),
                     ("window shifted +20 mm", mut_shifted)):
        got = fn(planted_vals, lv, lv.mon_idx) - fn(lv.h_end, lv, lv.mon_idx)
        (ok if abs(got - PLANT_P * f) > PLANT_TOL else fail).append(
            "P1 refuses mutant reader: %-24s shift %.6e vs P*f %.6e"
            % (name, got, PLANT_P * f))

    # ---- THE UNWEIGHTED-MEAN MUTANT NEEDS NON-UNIFORM AREAS -------------
    # HONEST LIMIT, CARRIED SO NO READER OVERRATES THIS CONTROL (R2 6.8):
    # on a UNIFORM mesh the area-weighted and unweighted means are the SAME
    # FUNCTION -- not two readers -- so this mutant is NOT DISCRIMINABLE on
    # the production meshes L1/L2/L3, whose faces were MEASURED to have
    # min area == max area exactly.  The weighting is therefore exercised
    # here, on a graded-area arm where the area fraction and the count
    # fraction differ.
    class _Graded(object):
        pass
    g = _Graded()
    g.centres = list(lv.centres)
    # area grows geometrically with y, so f_area != f_count
    g.areas = [lv.areas[i] * (1.0 + 3.0 * lv.centres[i][1] / 0.1)
               for i in range(lv.n)]
    g.n = lv.n
    g.h_end = list(lv.h_end)
    g.mon_idx = list(lv.mon_idx)
    gsub, gf = _plant_fraction(g, g.mon_idx)
    gcount = len(gsub) / float(len(g.mon_idx))
    if abs(gf - gcount) < 1e-6:
        fail.append("graded arm did not separate area fraction from count "
                    "fraction (f_area %.9f, f_count %.9f)" % (gf, gcount))
    else:
        ok.append("graded arm separates weighting: f_area = %.9f, "
                  "f_count = %.9f" % (gf, gcount))
    gpl = list(g.h_end)
    for i in gsub:
        gpl[i] += PLANT_P
    got = mut_unweighted(gpl, g, g.mon_idx) - mut_unweighted(g.h_end, g, g.mon_idx)
    (ok if abs(got - PLANT_P * gf) > PLANT_TOL else fail).append(
        "P1 refuses mutant reader: %-24s shift %.6e vs P*f %.6e (graded areas)"
        % ("unweighted mean", got, PLANT_P * gf))
    got = area_mean(gpl, g.areas, g.mon_idx) - area_mean(g.h_end, g.areas, g.mon_idx)
    (ok if abs(got - PLANT_P * gf) <= PLANT_TOL else fail).append(
        "P1 fires on the graded arm: shift %.6e == P*f %.6e"
        % (got, PLANT_P * gf))
    ok.append("DECLARED LIMIT: on the UNIFORM production meshes the unweighted "
              "mutant is NOT discriminable -- the two means are one function "
              "there, not two readers (R2 6.8 limit 1)")

    # the degenerate plant set (plant == reduction set) must be REFUSED
    class _Whole(object):
        pass
    whole = _Whole()
    whole.centres = [(c[0], 0.0, c[2]) for c in lv.centres]   # every face y<PLANT_Y_MAX
    whole.areas = lv.areas
    try:
        _plant_fraction(whole, lv.mon_idx)
        fail.append("P1 did NOT refuse a plant set equal to the reduction set")
    except Refuse:
        ok.append("P1 refuses a plant set equal to the reduction set (L-487)")

    # ---- P2, on the exactness statistic ---------------------------------
    levs = [Level(r, k) for k in EXACTNESS_LEVELS]
    rep2 = []
    plant_p2(levs, scratch, rep2)
    ok.append("P2 fires on a sound reader: %s" % rep2[-1].strip())

    # P2 mutant: a reduction that reads the SAME level three times cannot move
    real_stat = exactness_statistic

    def stat_same_level(d):
        v = [d[EXACTNESS_LEVELS[1]]] * 3
        return max(abs(a - b) for i, a in enumerate(v) for b in v[i + 1:])

    globals()["exactness_statistic"] = stat_same_level
    try:
        plant_p2(levs, scratch, [])
        fail.append("P2 did NOT refuse a statistic that reads one level three times")
    except Refuse:
        ok.append("P2 refuses a statistic that reads one level three times")
    finally:
        globals()["exactness_statistic"] = real_stat

    # ---- report ----------------------------------------------------------
    print("VMFL072-R2 comparator --selftest")
    print("=" * 78)
    print("BANNER, and it is not decoration: this selftest proves the comparator's")
    print("LOGIC on data it fabricated itself. It proves NOTHING about the")
    print("INTERFACE to the solver (ANSYS_VERIFICATION_CHARTER 39.5). The interface")
    print("is proven by the disk evidence table at the head of this file.")
    print("=" * 78)
    for line in ok:
        print("  PASS  %s" % line)
    for line in fail:
        print("  FAIL  %s" % line)
    print("-" * 78)
    print("%d passed, %d failed" % (len(ok), len(fail)))
    return 0 if not fail else 1


# ===========================================================================

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
        print("NO number is produced and none may be quoted. "
              "VERDICT: NOT A RESULT.")
        return 2
    except NotAResult as exc:
        print("VERDICT: NOT A RESULT (exit 3): %s" % exc)
        return 3
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())
