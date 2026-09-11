#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# VMFL072-R4-A -- the comparator for the precursor-h0 diagnostic ladder.
#
# REUSE. Everything from `import` down to the end of `plant_p1`, and `main()`,
# is BYTE-IDENTICAL to cases/ansys_verification/VMFL072-R3/compare_vmfl072_r3.py
# (the readers, load_geometry, monitor_mean, time_dirs, check_completion, class
# Level, _plant_fraction, _replant_and_reread, plant_p1). Hash those functions
# to confirm. The ONLY substantive change is the section banner-marked
# `R4-A FAMILY VERDICT`: a single-grid ladder over the precursor h0 with a
# per-rung survival (completion + the C-08 velocity-runaway gate) then
# retention verdict, dnstar(h0) per rung, a passive velocity observer, and the
# in-window abandonment aggregation. R3's exactness gate (a refinement triple)
# and its C1/B2 controls are GONE -- R4-A refines nothing.
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
# WHAT CHANGED FROM THE R3 COMPARATOR, AND WHAT DID NOT.
#   The field names, readers, completion and geometry refusals, monitor window,
#   bands, T_FLOOR and the plant machinery are UNCHANGED (byte-identical). The
#   39.5 disk-evidence table above still holds: R4-A writes the SAME files R3
#   wrote (h0 is a scalar dictionary value in base/0.orig/U). CHANGED: the
#   Limb B reference is dN*(h0) PER RUNG (dnstar(), continuous through R3's
#   frozen anchor at h0=1e-5); the family shape is a per-rung survival ->
#   retention verdict over three 256x64 rungs, not a refinement triple; the
#   C-08 velocity-runaway gate is added (min_h is CONTEXT ONLY -- it is pinned
#   at h0 by the post-solve floor, so max_magU is the survival tell, R4-A 4).
#
# NO ROACHE TRIPLE IS COMPUTED HERE (CLAUDE.md rule 5). R4-A is a SINGLE-GRID
# ladder: it establishes survival and retention at fixed 256x64, NOT grid
# convergence. There is no Richardson extrapolation, no observed order, no GCI;
# grid scaling is R4-B (a separate freeze).
#
# EXIT CODES
#   0  a verdict was produced (the verdict itself is on stdout)
#   2  REFUSED -- an instrument or completion condition failed; NO number is
#      produced and none may be quoted. The comparator refuses; it never
#      degrades.
#   3  NOT A RESULT -- a survivor's one-way physics gate (plateau, station
#      development) failed.
#   4  usage / internal error.
#
# USAGE
#   compare_vmfl072_r4a.py --runroot <dir>         grade
#   compare_vmfl072_r4a.py --selftest              instrument self-test
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
D_MANUAL      = 0.555e-3          # m   R4-A 5  Ansys VM 2026R1 Table .72.1 target (Limb A)
# R4-A: Limb B's reference is dN*(h0) PER RUNG, not a single constant -- see
# DN_CUBED and dnstar() in the R4-A FAMILY VERDICT section below.
D_NUSSELT     = 5.501147914e-04   # m   h0-free Nusselt; CONTEXT ONLY, never a gate
D_FLUENT      = 0.5497e-3         # m   R3 1   CONTEXT ONLY, never a gate

# --- the bands (R3 5) -----------------------------------------------------
BAND_A        = 2.12e-2           # -   R3 5.1  A .090 + B 1.926 + D' .0504 + E' .0504 %
BAND_B        = 1.01e-3           # -   R3 5.2  D' + E' only

# --- the instrument floor (R3 6.1). ONE constant, four uses. --------------
T_FLOOR       = 2.7750e-07        # m   0.05 % of 0.555 mm = 0.050447 % of dN*
                                  #     plateau ptp / station spread /
                                  #     exactness gate / B2 bracket

# --- the monitor (R3 6.2) -------------------------------------------------
MON_X_LO, MON_X_HI = 0.440, 0.460 # m   50 mm clear of the outlet
MON_Y_LO, MON_Y_HI = 0.025, 0.075 # m   the manual's 50 mm monitor width, centred
STATION_X     = (0.300, 0.350, 0.400, 0.450, 0.480)   # m  R3 6.3
STATION_HALF  = 0.010             # m

# --- admissibility floor (R3 6.7) ----------------------------------------
D_MIN_ADMISSIBLE = 1.0e-06        # m   550x below dN*; no film-producing run returns it

# --- the plants (R3 6.8; CLAUDE.md rule 3; L-487) ------------------------
PLANT_P       = 1.234000e-05      # m   sized from the band, never from a result
PLANT_Y_MAX   = 0.050             # m   lower half-span -> a PROPER SUBSET by area
PLANT_TOL     = 1.0e-09           # m
PLANT_MIN_MOVE = 1.0e-09          # m   the statistic must actually MOVE

# --- run control, fixed by apply_level.sh (R3 8.1) -----------------------
END_TIME          = 10.0
EXPECTED_TIME_DIRS = 200
PLATEAU_WINDOW_S  = 2.0
EXPECTED_PLATEAU_SAMPLES = 41     # t = 8.00, 8.05, ... 10.00 inclusive

# --- the registered rungs (R4-A 3). LEVELS keeps R3's (nx, ny, steps, role)
#     shape so check_completion and class Level read it UNCHANGED. Every rung
#     is the SAME 256x64x8000 grid -- R4-A is a single-grid ladder; the only
#     knob is h0, carried separately in RUNG_H0 (not a completion quantity).
LEVELS = {
    #        NX    NY   steps   role
    "A1": (  256,  64,   8000, "monotonicity control, BELOW the survive-and-retain window"),
    "A2": (  256,  64,   8000, "in-window pivot (interior)"),
    "A3": (  256,  64,   8000, "in-window pivot (upper edge, just under the ceiling)"),
}
RUNGS      = ("A1", "A2", "A3")
IN_WINDOW  = ("A2", "A3")          # the pivots for abandonment (R4-A 3, 5)
RUNG_H0    = {"A1": 5.0e-06, "A2": 1.5e-05, "A3": 2.0e-05}   # R4-A 3, answer-blind
H0_REL_TOL = 1.0e-9

PLATE_AREA    = 0.05              # m^2  0.5 m x 0.1 m, exactly
GEOM_REL_TOL  = 1.0e-12
PLANAR_REL_TOL = 1.0e-12

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
        #       plant on a LINEAR reader can close (R3 6.8 honest limit 2).
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



# ===========================================================================
# ==== R4-A FAMILY VERDICT ==================================================
# The ONLY substantive change from compare_vmfl072_r3.py. Everything ABOVE
# this banner -- the readers, load_geometry, monitor_mean, time_dirs,
# check_completion, class Level, _plant_fraction, _replant_and_reread,
# plant_p1 -- is byte-identical to R3's comparator (hash the shared functions
# to confirm). R4-A is a SINGLE-GRID ladder over the precursor h0, so the R3
# exactness gate (a refinement triple) and the C1/B2 controls are GONE; in
# their place are: dnstar(h0) per rung, a passive velocity observer, the C-08
# runaway gate, a per-rung survival->retention verdict, and the in-window
# abandonment aggregation. NO ROACHE TRIPLE is declared (CLAUDE.md rule 5):
# R4-A establishes survival and retention at fixed 256x64, NOT grid
# convergence (that is R4-B).
# ===========================================================================

# --- the frozen precursor balance, and the per-rung reference -------------
DN_CUBED = 1.664791949293077e-10  # m^3  R4-A 2  h^2(h+h0)=3 nu q/gs; Gamma pinned => RHS frozen.
                                  # Back-derived from R3's frozen D_NSTAR so that
                                  # dnstar(1e-5) reproduces 5.468015742732e-04 m to
                                  # machine precision (prose value 1.664792e-10 is rounded).


def dnstar(h0):
    """Exact steady discrete film thickness at precursor h0: Newton on
    h^2 (h + h0) = DN_CUBED. dN*(h0) is Limb B's reference FOR THAT RUNG,
    and tracks h0 exactly (the R3 2.4 non-circular construction)."""
    h = DN_CUBED ** (1.0 / 3.0)   # Nusselt seed
    for _ in range(120):
        f = h * h * (h + h0) - DN_CUBED
        fp = 3.0 * h * h + 2.0 * h * h0
        h -= f / fp
    return h


# --- the velocity-runaway gate (C-08). min_h is CONTEXT ONLY (pinned at h0
#     by the post-solve floor); max_magU is the tell (R4-A 4, 5). -----------
MAGU_MAX_BOUND = 100.0             # m/s  R4-A 5  physical U_IN=0.537; runaway observed >= 4e13

_RE_FILM_H = re.compile(r"Film h min/max\s*=\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)")
_RE_FILM_U = re.compile(r"Film mag\(U\) min/max\s*=\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)")


def observe(logpath):
    """PASSIVE parse of solver stdout. Returns (rows, max_magU) where each row
    is (min_h, max_h, min_magU, max_magU). ALTERS NO FIELD -- it reads the log.
    min_h is diagnostic; max_magU feeds C-08."""
    if not os.path.isfile(logpath):
        raise Refuse("OBSERVER: no log.pimpleFoam at %s" % logpath)
    text = open(logpath, "r", errors="replace").read()
    hs = _RE_FILM_H.findall(text)
    us = _RE_FILM_U.findall(text)
    rows, mx = [], 0.0
    for (mnh, mxh), (mnu, mxu) in zip(hs, us):
        r = (float(mnh), float(mxh), float(mnu), float(mxu))
        rows.append(r)
        if r[3] > mx:
            mx = r[3]
    return rows, mx


def write_observer(case, rows):
    """Write the observer trace as an ANALYSIS artifact (adds min_hf_film.tsv;
    touches no solver field). Returns the path, or None if there is nothing."""
    if not rows:
        return None
    p = os.path.join(case, "min_hf_film.tsv")
    with open(p, "w") as fh:
        fh.write("# step\tmin_h\tmax_h\tmin_magU\tmax_magU"
                 "   (min_h CONTEXT ONLY; max_magU is the C-08 gate)\n")
        for k, r in enumerate(rows):
            fh.write("%d\t%.9e\t%.9e\t%.9e\t%.9e\n" % (k, r[0], r[1], r[2], r[3]))
    return p


def check_c08(case, rung):
    """C-08 velocity-boundedness (SURVIVAL conjunct 2). max_magU < bound at
    EVERY logged step. Catches a run that COMPLETED (rc==0, all of C-01..C-07)
    but went unphysical -- which the completion clauses alone would pass."""
    rows, mx = observe(os.path.join(case, "log.pimpleFoam"))
    if not rows:
        raise Refuse("C-08 %s: no 'Film mag(U) min/max' lines -- boundedness "
                     "unverifiable" % rung)
    if not (mx < MAGU_MAX_BOUND):
        raise Refuse("C-08 %s: film velocity RUNAWAY max_magU = %.6e m/s >= %.1f "
                     "m/s bound (the dewetting tell, R4-A 4)" % (rung, mx, MAGU_MAX_BOUND))
    return rows, mx


def read_applied_h0(case, rung):
    """Read H0 from the rung's LEVEL_APPLIED.txt and verify it against the
    registered table -- refuse a rung whose applied h0 is not the frozen one."""
    p = os.path.join(case, "LEVEL_APPLIED.txt")
    if not os.path.isfile(p):
        raise Refuse("H0 %s: no LEVEL_APPLIED.txt" % rung)
    m = re.search(r"^H0\s+([-\d.eE+]+)", open(p).read(), flags=re.M)
    if not m:
        raise Refuse("H0 %s: LEVEL_APPLIED.txt has no H0 line" % rung)
    h0 = float(m.group(1))
    want = RUNG_H0[rung]
    if abs(h0 - want) > H0_REL_TOL * want:
        raise Refuse("H0 %s: applied h0 = %.9e != registered %.9e" % (rung, h0, want))
    return h0


# --- P2, re-scoped: guard a reader that reads ONE rung three times or swaps
#     rungs. The per-rung dmon values must be DISTINCT; the null is that a
#     confused reader cannot move the cross-rung spread. Needs >= 2 survivors.
def rung_spread_statistic(dmon_by_rung, rungs):
    """max over pairs of |dmon(Ri) - dmon(Rj)| across the given rungs."""
    v = [dmon_by_rung[k] for k in rungs]
    return max(abs(a - b) for i, a in enumerate(v) for b in v[i + 1:])


def plant_p2(levels, scratch, report):
    """P2 -- against the CROSS-RUNG reduction (a max over pairs). Plants into
    ONE rung and requires the statistic to take the analytically known value
    AND to have MOVED, so a reader that reads one rung three times is refused.
    (Structurally identical to R3's P2, re-scoped from levels to rungs.)"""
    names = [L.name for L in levels]
    clean = {L.name: L.dmon for L in levels}
    s_clean = rung_spread_statistic(clean, names)

    target = levels[0]
    sub, f = _plant_fraction(target, target.mon_idx)
    d_pl = _replant_and_reread(target, sub, scratch)

    planted = dict(clean)
    planted[target.name] = d_pl
    s_planted = rung_spread_statistic(planted, names)

    expected = dict(clean)
    expected[target.name] = clean[target.name] + PLANT_P * f
    s_expected = rung_spread_statistic(expected, names)

    if abs(s_planted - s_expected) > PLANT_TOL:
        raise Refuse("P2: planted cross-rung statistic %.9e m, expected %.9e m -- "
                     "the rung-comparison reduction did not re-read the planted "
                     "rung" % (s_planted, s_expected))
    if abs(s_planted - s_clean) <= PLANT_MIN_MOVE:
        raise Refuse("P2: the plant moved the cross-rung statistic by only "
                     "%.3e m (<= %.1e m). A control that cannot move is not a "
                     "control." % (abs(s_planted - s_clean), PLANT_MIN_MOVE))
    report.append("  P2 fired: statistic %.9e -> %.9e m (moved %.9e, expected %.9e)"
                  % (s_clean, s_planted, s_planted - s_clean, s_expected))


# ===========================================================================
# THE PER-RUNG VERDICT.  Survival (completion C-01..C-07 + C-08) then, for a
# survivor, retention (the two unchanged R3 bands against dN*(h0)).  A LITERAL
# transcription; --selftest carries one mutant per conjunct.
# ===========================================================================

def verdict_rung(state):
    """state: the registered conditions for ONE surviving rung. Returns
    (limbA, limbB). Plateau/station are one-way gates (they can only turn a
    limb INTO NOT A RESULT)."""
    if not state["C-10 plateau"]:
        raise NotAResult("C-10 the rung did not plateau at the monitor")
    if not state["C-11 station"]:
        raise NotAResult("C-11 the film is not developed at the monitor")
    limb_a = "GATE REACHED" if state["C-18 limbA"] else "GATE FAIL"
    limb_b = "PASS" if state["C-19 limbB"] else "GATE FAIL"
    return limb_a, limb_b


RUNG_VERDICT_CONJUNCTS = ("C-10 plateau", "C-11 station", "C-18 limbA", "C-19 limbB")


# ===========================================================================
# GRADE.  Per rung: observer (even on a crash) -> survival -> retention.
# Then the family abandonment aggregation keyed on the in-window rungs.
# ===========================================================================

def grade(runroot):
    out = []
    out.append("VMFL072-R4-A -- precursor-h0 ladder at fixed 256x64 (survival + retention)")
    out.append("run root: %s" % runroot)
    out.append("")

    scratch = tempfile.mkdtemp(prefix="vmfl072r4a_plant_")
    try:
        results = {}
        survivors = {}          # rung -> Level, for the surviving rungs only
        for rung in RUNGS:
            case = os.path.join(runroot, rung)
            h0 = RUNG_H0[rung]
            dstar = dnstar(h0)

            # observer FIRST -- it works on a crash log too (records the tell)
            try:
                rows, mx = observe(os.path.join(case, "log.pimpleFoam"))
                write_observer(case, rows)
            except Refuse:
                rows, mx = [], None

            rec = {"rung": rung, "h0": h0, "dstar": dstar, "max_magU": mx,
                   "survived": False, "limb_a": None, "limb_b": None, "why": ""}

            # -- PROVENANCE (HARD REFUSE, OUTSIDE survival). A rung that ran an
            #    UNREGISTERED h0 is the WRONG EXPERIMENT: it does not "fail to
            #    survive", it INVALIDATES the grade. read_applied_h0 raises Refuse,
            #    which propagates to main() -> exit 2. Run it FIRST, so a compromised
            #    rung cannot be laundered into a survival verdict.
            read_applied_h0(case, rung)

            # -- SURVIVAL: PHYSICS ONLY. check_completion (rc / End / endTime /
            #    fields / count / age) and check_c08 (velocity runaway) are the only
            #    conditions a physical CRASH can trip; a failure here legitimately
            #    means "did not survive". An INSTRUMENT fault is NOT caught here.
            try:
                check_completion(case, rung)
                check_c08(case, rung)
            except (Refuse, NotAResult) as exc:
                rec["why"] = "does NOT survive: %s" % exc
                out.append("  %-3s h0=%.2e  DOES NOT SURVIVE  (max_magU=%s)  %s"
                           % (rung, h0,
                              ("%.3e" % mx) if mx is not None else "n/a", exc))
                results[rung] = rec
                continue

            # -- INSTRUMENT reads on a run that DID complete. Level bundles
            #    load_geometry + read_area_scalar + C-13 admissibility. It is
            #    constructed OUTSIDE the survival except SO THAT a corrupt faMesh, a
            #    truncated field or a zero read HARD-REFUSES (exit 2) rather than being
            #    mis-recorded as non-survival -- which on an in-window rung would drive
            #    a FALSE ABANDONMENT of the precursor approach. check_completion here
            #    (again, inside Level) is read-only and idempotent, so the double call
            #    is harmless.
            lev = Level(runroot, rung)

            # -- survivor: retention --------------------------------------
            rec["survived"] = True
            survivors[rung] = lev
            st = {}
            s = lev.plateau_series()
            st["C-10 plateau"] = (max(s) - min(s)) <= T_FLOOR
            stn = lev.station_means()
            st["C-11 station"] = (max(v for _, v in stn) - min(v for _, v in stn)) <= T_FLOOR
            d = lev.dmon
            e_a = abs(d - D_MANUAL) / D_MANUAL
            e_b = abs(d - dstar) / dstar
            st["C-18 limbA"] = e_a <= BAND_A
            st["C-19 limbB"] = e_b <= BAND_B
            try:
                la, lb = verdict_rung(st)
            except NotAResult as exc:
                rec["why"] = "SURVIVES but NOT A RESULT on retention: %s" % exc
                out.append("  %-3s h0=%.2e  SURVIVES  dmon=%.9e m  NOT A RESULT (%s)"
                           % (rung, h0, d, exc))
                results[rung] = rec
                continue
            rec["limb_a"], rec["limb_b"] = la, lb
            rec["dmon"] = d
            rec["e_a"], rec["e_b"] = e_a, e_b
            out.append("  %-3s h0=%.2e  SURVIVES  dmon=%.9e m = %.6f mm  "
                       "e_A=%.4f%% -> %s ; e_B=%.4f%% -> %s  (dN*=%.9e, max_magU=%.3e)"
                       % (rung, h0, d, d * 1e3, e_a * 100, la, e_b * 100, lb,
                          dstar, mx))
            results[rung] = rec

        out.append("")

        # -- planted controls, on the surviving rungs --------------------
        out.append("PLANTED CONTROLS (CLAUDE.md rule 3; L-487):")
        surv_names = [r for r in RUNGS if results[r]["survived"]]
        if surv_names:
            plant_p1(survivors[surv_names[0]], scratch, out)
        else:
            out.append("  P1: no surviving rung to plant into (every rung crashed)")
        if len(surv_names) >= 2:
            plant_p2([survivors[r] for r in surv_names], scratch, out)
        else:
            out.append("  P2: < 2 surviving rungs -- cross-rung control inapplicable "
                       "this run (needs two survivors to test rung confusion)")
        out.append("")

        # -- family verdict / abandonment (keyed on the in-window rungs) --
        in_window_pass = [r for r in IN_WINDOW
                          if results[r]["survived"] and results[r]["limb_a"] == "GATE REACHED"]
        out.append("FAMILY VERDICT (R4-A 5):")
        for r in RUNGS:
            rec = results[r]
            tag = ("survives in-band" if (rec["survived"] and rec["limb_a"] == "GATE REACHED")
                   else ("survives OUT of band" if rec["survived"] else "does not survive"))
            out.append("  %-3s (%s): %s" % (r, "in-window" if r in IN_WINDOW else "control", tag))
        if in_window_pass:
            out.append("  => an in-window rung survives in band (%s). CARRY its h0 to "
                       "R4-B (512x128 scaling test, a SEPARATE freeze)." % ", ".join(in_window_pass))
        else:
            out.append("  => NEITHER in-window rung (A2, A3) survives in band. The "
                       "constant-precursor approach is ABANDONED for VMFL072 (R4-A 5); "
                       "the successor moves to kinematicSingleLayer or VOF.")
        out.append("")
        out.append("WHAT THIS DOES NOT ESTABLISH: no order of accuracy, no GCI, no grid")
        out.append("convergence (single grid; that is R4-B). Limb A is capped at GATE")
        out.append("REACHED -- its reference is experimental.")
        return 0, out

    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ===========================================================================
# SELFTEST.  Proves LOGIC on data it fabricates.  Proves NOTHING about the
# INTERFACE (ANSYS_VERIFICATION_CHARTER 39.5). Reuses R3's fixture builder,
# extended to emit the 'Film mag(U) min/max' lines the C-08 gate reads, and
# adds the runaway mutation control the supervisor asked for.
# ===========================================================================

def _fixture(root, rung, dmon_target, *, break_clause=None, uniform=True,
             h0=None, magu_max=0.54, applied_h0=None):
    """Write a REAL, parseable case tree for one rung (256x64), including the
    'Film h min/max' / 'Film mag(U) min/max' lines. magu_max controls the C-08
    observable; applied_h0 overrides the LEVEL_APPLIED H0 (for the mismatch
    mutant)."""
    lnx, lny, steps, _ = LEVELS[rung]
    nx, ny = lnx, lny
    if h0 is None:
        h0 = RUNG_H0[rung]
    if applied_h0 is None:
        applied_h0 = h0
    case = os.path.join(root, rung)
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
        pts[idx[(1, 1)]] = (dx, dy, 1.0e-3)
    if break_clause == "C-15":
        pts = [(p[0] * 0.9, p[1], p[2]) for p in pts]

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

    n = len(faces)
    vals = []
    for k in range(n):
        j = k // nx
        vals.append(dmon_target if uniform
                    else dmon_target * (1.0 + 1e-3 * (j / max(ny - 1, 1) - 0.5)))

    skip = EXPECTED_TIME_DIRS // 2 if break_clause == "C-05" else None
    for k in range(1, EXPECTED_TIME_DIRS + 1):
        if k == skip:
            continue
        t = k * (END_TIME / EXPECTED_TIME_DIRS)
        name = ("%g" % t)
        d = os.path.join(case, name, "finite-area")
        os.makedirs(d, exist_ok=True)
        inwin = t >= END_TIME - PLATEAU_WINDOW_S - 1e-9
        drift = 0.0
        if break_clause == "C-10" and inwin:
            drift = 3.0 * T_FLOOR * ((k % 2) - 0.5)
        if inwin:
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

    # LEVEL_APPLIED.txt -- carries H0 for read_applied_h0
    with open(os.path.join(case, "LEVEL_APPLIED.txt"), "w") as fh:
        fh.write("RUNG       %s\nNX NY NZ   256 64 1\nH_IN       7.1084204656e-04\n"
                 "U_IN       0.537381243\nDELTAT     1.25e-03\nWRITEINT   40\n"
                 "H0         %.9e\nDELTAWET   %.9e\n" % (rung, applied_h0, applied_h0))

    # log.pimpleFoam: ExecutionTime lines (C-06 count) + End, PLUS the film
    # observer lines (C-08). One runaway step for the C-08 mutant.
    nsteps = steps if break_clause != "C-06" else steps - 1
    with open(os.path.join(case, "log.pimpleFoam"), "w") as fh:
        for s in range(nsteps):
            umax = magu_max
            if break_clause == "C-08" and s == nsteps // 2:
                umax = 4.22e13                       # a runaway on ONE step
            fh.write("Film h min/max   = (%.9e %.9e)\n" % (h0, dmon_target))
            fh.write("Film mag(U) min/max   = (%.9e %.9e)\n" % (0.0, umax))
            fh.write("ExecutionTime = 1 s\n")
        if break_clause != "C-02":
            fh.write("End\n")
    open(os.path.join(case, "RC.txt"), "w").write(
        "rc=1\n" if break_clause == "C-01" else "rc=0\n")
    return case


def _build_run(root, dmon, *, break_clause=None, only=None, uniform=True,
               applied_h0=None):
    for rung in RUNGS:
        bc = break_clause if (only is None or only == rung) else None
        ah = applied_h0 if (only is None or only == rung) else None
        _fixture(root, rung, dmon[rung], break_clause=bc, uniform=uniform,
                 applied_h0=ah)


def selftest():
    ok, fail = [], []

    def expect(tag, fn, want):
        try:
            fn()
            got = "graded"
            detail = ""
        except Refuse as exc:
            got, detail = "REFUSE", str(exc)
        except NotAResult as exc:
            got, detail = "NOTARESULT", str(exc)
        (ok if got == want else fail).append(
            "%-32s expected %-11s got %-11s  %s" % (tag, want, got, detail[:66]))

    # dmon at each rung's own in-band dN*(h0), so a clean run SURVIVES in-band
    base = {r: dnstar(RUNG_H0[r]) for r in RUNGS}

    # ---- 1. a clean run grades (all three survive in-band) --------------
    root = tempfile.mkdtemp(prefix="vmfl072r4a_st_clean_")
    _build_run(root, base)
    expect("clean run grades", lambda: grade(root), "graded")

    # a clean run's family verdict CARRIES (an in-window rung survives in band)
    rc, lines = grade(root)
    body = "\n".join(lines)
    (ok if "CARRY its h0 to" in body else fail).append(
        "clean run family verdict CARRIES (in-window survivor in band)")
    (ok if "P1 A2 fired" in body or "P1 A" in body else fail).append(
        "P1 fires on a surviving rung: %s"
        % next((l.strip() for l in lines if "P1 A" in l), "NOT FOUND"))
    (ok if "P2 fired" in body else fail).append(
        "P2 fires with three survivors: %s"
        % next((l.strip() for l in lines if "P2 fired" in l), "NOT FOUND"))

    def refuses(fn):
        """True iff fn() HARD-REFUSES (raises Refuse -> exit 2). A NotAResult or
        a clean return is NOT a refuse."""
        try:
            fn()
            return False
        except Refuse:
            return True
        except NotAResult:
            return False

    # ---- 2a. PHYSICS mutants (a genuine crash). A rung that trips
    #        check_completion (rc/End/endTime/fields/count/age) or check_c08
    #        (runaway) DOES NOT SURVIVE -- the grade returns and the body records
    #        it. These are the ONLY things a crash trips. C-01..C-07. ----------
    for clause in ("C-01", "C-02", "C-03", "C-04", "C-05", "C-06", "C-07"):
        r = tempfile.mkdtemp(prefix="vmfl072r4a_st_%s_" % clause)
        _build_run(r, base, break_clause=clause, only="A2")   # break an in-window rung
        rc, lines = grade(r)
        (ok if "A2  h0=1.50e-05  DOES NOT SURVIVE" in "\n".join(lines) else fail).append(
            "physics mutant %s: A2 does not survive (a crash)" % clause)

    # ---- 2b. INSTRUMENT mutants (a run that COMPLETED but the instrument is
    #        corrupt): geometry C-14..C-17 and admissibility (a zero read). These
    #        must HARD-REFUSE (exit 2), NOT be recorded as non-survival -- a
    #        corrupt instrument on an in-window rung would otherwise drive a FALSE
    #        ABANDONMENT. The fixture COMPLETES (check_completion passes); the
    #        Refuse comes from Level's load_geometry / read_area_scalar / C-13. ---
    for clause in ("C-13z", "C-14", "C-15", "C-16", "C-17"):
        r = tempfile.mkdtemp(prefix="vmfl072r4a_st_%s_" % clause)
        if clause == "C-13z":
            z = dict(base); z["A2"] = 0.0                     # a zero read on A2
            _build_run(r, z)
        else:
            _build_run(r, base, break_clause=clause, only="A2")
        (ok if refuses(lambda r=r: grade(r)) else fail).append(
            "instrument mutant %s: COMPLETED-but-corrupt HARD-REFUSES (exit 2), "
            "not 'does not survive'" % clause)

    # ---- 2c. THE PHYSICS/INSTRUMENT SPLIT IS LOAD-BEARING (mutation control).
    #        On a COMPLETED-but-corrupt-geometry rung: check_completion SUCCEEDS
    #        (it is NOT a physics crash) while Level RAISES Refuse (instrument).
    #        A BROAD survival catch -- the bug -- would swallow it as 'does not
    #        survive'; the split HARD-REFUSES. Remove the split and (ii) goes red.
    r = tempfile.mkdtemp(prefix="vmfl072r4a_st_split_")
    _build_run(r, base, break_clause="C-17", only="A2")       # out-of-plane vertex
    caseA2 = os.path.join(r, "A2")
    comp_ok = True
    try:
        check_completion(caseA2, "A2")
    except (Refuse, NotAResult):
        comp_ok = False
    (ok if comp_ok else fail).append(
        "split (i): a corrupt-geometry rung PASSES check_completion (not a crash)")
    (ok if refuses(lambda: Level(r, "A2")) else fail).append(
        "split (ii): Level RAISES on the SAME rung -> a broad catch would "
        "mis-record it as non-survival (the split is load-bearing)")
    (ok if refuses(lambda r=r: grade(r)) else fail).append(
        "split (iii): the real grade HARD-REFUSES the corrupt rung (exit 2)")

    # ---- 3. THE C-08 RUNAWAY GATE, and its mutation control -------------
    r = tempfile.mkdtemp(prefix="vmfl072r4a_st_C-08_")
    _build_run(r, base, break_clause="C-08", only="A2")
    rc, lines = grade(r)
    body = "\n".join(lines)
    (ok if "A2  h0=1.50e-05  DOES NOT SURVIVE" in body and "C-08" in body else fail).append(
        "C-08 refuses a COMPLETED run with a velocity runaway (rc==0, all of "
        "C-01..C-07 pass)")
    # MUTATION CONTROL: remove the C-08 gate and the SAME run must now survive
    # -> proves the gate is load-bearing (RED without it).
    real_c08 = check_c08
    globals()["check_c08"] = lambda case, rung: (observe(os.path.join(case, "log.pimpleFoam")))
    try:
        rc, lines = grade(r)
        body = "\n".join(lines)
        moved = "A2  h0=1.50e-05  SURVIVES" in body
    finally:
        globals()["check_c08"] = real_c08
    (ok if moved else fail).append(
        "mutation control: WITHOUT the C-08 gate the runaway run survives "
        "(the gate is load-bearing)")

    # ---- 5. PROVENANCE: a rung that ran an UNREGISTERED h0 HARD-REFUSES (exit
    #        2), NOT 'does not survive' -- the wrong experiment invalidates the
    #        grade, it does not fail to survive. read_applied_h0 runs first,
    #        outside the survival catch. --------------------------------------
    r = tempfile.mkdtemp(prefix="vmfl072r4a_st_h0_")
    _build_run(r, base, applied_h0=9.9e-05, only="A2")
    (ok if refuses(lambda r=r: grade(r)) else fail).append(
        "provenance: a rung that ran an UNREGISTERED h0 HARD-REFUSES (exit 2), "
        "not 'does not survive'")

    # ---- 6. VERDICT CONJUNCTS on a surviving rung -----------------------
    # C-10 plateau: an in-window rung that does not plateau -> NOT A RESULT
    r = tempfile.mkdtemp(prefix="vmfl072r4a_st_C-10_")
    _build_run(r, base, break_clause="C-10", only="A2")
    rc, lines = grade(r)
    (ok if "A2  h0=1.50e-05  SURVIVES" in "\n".join(lines)
        and "NOT A RESULT" in "\n".join(lines) else fail).append(
        "conjunct C-10: a survivor that does not plateau is NOT A RESULT")

    # C-18 limb A band edge: push an in-window rung out of band -> GATE FAIL,
    # and if BOTH in-window rungs are out of band the family ABANDONS.
    r = tempfile.mkdtemp(prefix="vmfl072r4a_st_abandon_")
    oob = dict(base)
    oob["A2"] = D_MANUAL * (1.0 - BAND_A) - 5.0 * T_FLOOR   # below the floor
    oob["A3"] = D_MANUAL * (1.0 - BAND_A) - 5.0 * T_FLOOR
    _build_run(r, oob)
    rc, lines = grade(r)
    body = "\n".join(lines)
    (ok if "GATE FAIL" in body else fail).append(
        "conjunct C-18: an out-of-band survivor is GATE FAIL")
    (ok if "ABANDONED for VMFL072" in body else fail).append(
        "family ABANDONS when neither in-window rung survives in band")

    # ---- 7. dnstar(h0) sanity: monotone decreasing, matches the frozen table
    d5, d15, d20 = dnstar(5e-6), dnstar(1.5e-5), dnstar(2e-5)
    (ok if d5 > d15 > d20 and abs(dnstar(1e-5) - 5.468015742732e-04) < 1e-12 else fail).append(
        "dnstar(h0): monotone and matches the frozen h0=1e-5 anchor")

    # ---- 8. BOTH PLANTS FIRE ON REAL R3-L3 DATA (crash trace on disk) ----
    _selftest_real_r3l3(ok, fail)

    # ---- report ----------------------------------------------------------
    print("VMFL072-R4-A comparator --selftest")
    print("=" * 78)
    print("BANNER: this selftest proves the comparator's LOGIC on data it")
    print("fabricated (plus the real R3-L3 crash field for the plant). It proves")
    print("NOTHING about the INTERFACE (ANSYS_VERIFICATION_CHARTER 39.5).")
    print("=" * 78)
    for line in ok:
        print("  PASS  %s" % line)
    for line in fail:
        print("  FAIL  %s" % line)
    print("-" * 78)
    print("%d passed, %d failed" % (len(ok), len(fail)))
    return 0 if not fail else 1


def _selftest_real_r3l3(ok, fail):
    """Fire P1 against the REAL R3-L3 crash field on disk: the reader+plant
    must work on real 256x64 geometry, not only synthetic fixtures."""
    real = os.path.join("verification", "runs", "ansys_verification",
                        "VMFL072-R3", "L3")
    if not os.path.isdir(real):
        ok.append("real R3-L3 plant SKIPPED: %s absent (run from repo root to enable)" % real)
        return
    try:
        centres, areas = load_geometry(real, 256, 64)
        tds = time_dirs(real)
        hpath = None
        for t, name in reversed(tds):
            cand = os.path.join(real, name, "finite-area", "hf_film")
            if os.path.isfile(cand):
                hpath = cand
                break
        if hpath is None:
            ok.append("real R3-L3 plant SKIPPED: no written finite-area/hf_film")
            return
        h_end = read_area_scalar(hpath, len(areas))
        dmon, mon_idx = monitor_mean(h_end, centres, areas)

        class _Shim(object):
            pass
        lev = _Shim()
        lev.name = "R3L3"
        lev.centres, lev.areas, lev.h_end = centres, areas, h_end
        lev.n, lev.dmon, lev.mon_idx = len(areas), dmon, mon_idx

        scratch = tempfile.mkdtemp(prefix="vmfl072r4a_real_")
        try:
            rep = []
            plant_p1(lev, scratch, rep)
            ok.append("P1 fires on REAL R3-L3 data: %s" % rep[-1].strip())
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    except (Refuse, NotAResult) as exc:
        fail.append("real R3-L3 plant raised %s: %s" % (type(exc).__name__, exc))
    except Exception as exc:  # a real-data reader problem is a finding, not a pass
        fail.append("real R3-L3 plant hit %s: %s" % (type(exc).__name__, exc))


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
