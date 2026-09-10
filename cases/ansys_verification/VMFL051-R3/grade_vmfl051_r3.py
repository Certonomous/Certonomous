#!/usr/bin/env python3
"""VMFL051-R3 comparator -- isentropic expansion of supersonic flow over a
convex corner.  SUCCESSOR to VMFL051-R2 (register Row #73, NOT A RESULT).

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 165-166.
Reference: John Anderson, *Modern Compressible Flow: With Historical
Perspective*, McGraw-Hill, 2002 (Prandtl-Meyer expansion, CLOSED-FORM ANALYTIC).

THIS FILE IS THE GRADING PATH.  It is committed BEFORE any GRADED solver runs
(CLAUDE.md rule 2; VERIFICATION_CHARTER section 2d).  Nothing in it may change
once the first graded R3 solve has started; any later change is a dated addendum
in RESULTS.md read by the supervisor.

It REFUSES (exit 2) rather than degrades.  Every refusal names the clause.

NO THRESHOLD, BAND, REFERENCE VALUE, PLANE LOCATION, WINDOW FRACTION OR PLANT
CONSTANT IN THIS FILE IS SETTABLE FROM THE COMMAND LINE.  Every one is a
module-level constant fixed by the commit that freezes this file.

======================================================================
WHAT CHANGED FROM VMFL051-R2, AND WHY (the ONE lever -- the SPATIAL reduction)
======================================================================
R2 changed the TEMPORAL reduction (endTime snapshot -> time-mean over a settled
window) and that fixed the temporal axis: per-level settledness came out
7.4e-5 / 8.1e-6 / 6.4e-6 against TOL_STAT = 5.0e-4.  But the SPATIAL
non-monotonicity survived: the Roache triple on R2's three volume-average
time-means was OSCILLATORY (R = -1.184), so NOT A RESULT whatever the value.

R3 keeps R2's temporal reduction UNCHANGED and changes the SPATIAL reduction:
the graded observable is the TIME-MEAN, over the same settled window, of a
MASS-FLUX-WEIGHTED (conservative) Mach on a downstream cross-plane inside the
uniform post-expansion wedge, clear of the fan.  A flux-weighted average of
conserved quantities is constrained by the governing equations and is far less
sensitive to weak dispersive waves than a pointwise-nonlinear volume average.

The GATE DOES NOT MOVE (reference 3.2370, band +/- 0.5 %; L-487).  The solver,
scheme, mesh family (r = 2), endTime (7.0e-3 s) and 0/ fields are byte-identical
to R2 / run 1; only the two SAMPLING dictionaries and this comparator change.

THE GATED OBSERVABLE (PREREGISTRATION.md section 3.3, supervisor's ruling 2 --
the isentropic p0/p Mach):
    M_lab(t) = sqrt( (2/(g-1)) * [ (<pStag>_m(t)/<p>_m(t))^((g-1)/g) - 1 ] )
where <.>_m is the mass-flux-weighted (weightField phi) average over the frozen
faceZone `postExpPlane`, written every timestep by a surfaceFieldValue FO, and
pStag is the isentropic stagnation-pressure field built at run time by the v2606
exprField FO.  M_lab(t) is formed per row and then TIME-AVERAGED over the last
WINDOW_FRAC of rows (R2's settled window).  The three-level triple is built on
those three per-level time-means.

Total pressure is the conserved quantity of isentropic flow, so p0/p is the most
physically constrained reduction available; it also cures R2's p-vs-T
inconsistency (0.0057 at L3, same order as |d32|) by construction.  DELIBERATE
property: if the KT scheme generates entropy at the corner singularity, pStag
falls and this reduction reads LOW rather than hiding it.

THE READER IS BUILT AGAINST THE v2606 surfaceFieldValue WRITER SOURCE, NOT A
BELIEF ABOUT IT (N-AV4 / L-286):
  * path   postProcessing/<foName>/<startTime>/surfaceFieldValue.dat
  * header "# Region type : faceZone postExpPlane", "# Faces  : N",
           "# Area   : A", "# Weight field : phi", then "# Time" followed by
           <tab>weightedAverage(<field>) per field (surfaceFieldValue.C
           writeFileHeader).
  * data   writeCurrentTime, then `file() << tab << sresult` per field
           (surfaceFieldValueTemplates.C:519), at this object's writePrecision.
Columns are located BY HEADER NAME, never by position.  The "# Faces" line is a
control: the comparator REFUSES (exit 2) if it is absent or reports 0.

------------------------------------------------------------------
CORRECTION TO PREREGISTRATION.md SECTION 5, DISCLOSED ON THE FACE (read by the
supervisor before the freeze -- the registration is UNFROZEN, so this is a
legal pre-first-compute correction).
------------------------------------------------------------------
Section 5 designed PZ-1 as a plant "onto a proper subset of the plane's FACES"
with the shift scaled by the "mass-flux-weighted fraction", plus a fail arm in
which a "weight-ignoring reader" recovers a different shift.  THAT IS NOT
IMPLEMENTABLE AGAINST WHAT THE COMPARATOR READS: the surfaceFieldValue FO
performs the mass-flux weighting LIVE inside OpenFOAM and writes ONE weighted
value per field PER TIMESTEP, so the .dat carries no per-face values and no
per-face fluxes.  The flux weighting therefore rests on the VERIFIED v2606
source (weight = mag(phi), gSum(mag(phi)*q)/gSum(mag(phi)); surfaceFieldValue.C
:50, surfaceFieldValueTemplates.C:182), NOT on a comparator plant.  PZ-1 here is
consequently the R2-form control on the same TEMPORAL reduction the gate reads:
it plants +PLANT_DAT onto a PROPER TIME-SUBSET of the settled-window rows of the
plane .dat's weightedAverage(Ma) column, in a COPY, reads it back from disk, and
requires the window-mean to move by plant x (planted-rows / window-rows).  It
FAILS (refuses) if the reader cannot see the plant, and the whole-window plant
is refused as the inert configuration.  The implementable fail arms replacing
the weight-ignoring mutation are: (a) a drifting series is judged NOT settled;
(b) a subsonic/absurd M triggers the gate-blind physical-range refusal; (c) an
empty faceZone (# Faces : 0) refuses -- each asserting the ACTUAL rc is 2.

Section 8's C4 field list "T U p rho Ma + phi" is corrected here too: phi is
created by rhoCentralFoam (createFields.H:90) but is NOT AUTO_WRITE, so it never
lands on disk; it is a live registry field consumed by the FO during the run.
C4 therefore requires (T U p rho Ma), exactly as R2; phi's presence is proven by
the flux-weighted columns existing in the .dat, not by a file on disk.

    python3 grade_vmfl051_r3.py                       # grade the run tree
    python3 grade_vmfl051_r3.py --selftest            # all controls, zero compute
    python3 grade_vmfl051_r3.py --dryrun-reader FILE  # parse only; prints no value
    python3 grade_vmfl051_r3.py --verify-frozen SHA   # hash self against a commit
"""

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# 0.  Where things are
# ---------------------------------------------------------------------------
REPO = "/home/ubuntu/Certonomous"
SELF_REL = "cases/ansys_verification/VMFL051-R3/grade_vmfl051_r3.py"
RUN_ROOT = os.path.join(REPO, "verification/runs/ansys_verification/VMFL051-R3")
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL051_R3.json")

# ---------------------------------------------------------------------------
# 1.  THE MANUAL'S OWN NUMBERS (manual pp. 165-166), quoted, not paraphrased
# ---------------------------------------------------------------------------
MANUAL_PAGE = "165-166"
MANUAL_CP = 1006.43          # J/kg-K, "Specific Heat = 1006.43 J/kg-K"
MANUAL_MW = 28.966           # "Molecular weight = 28.966"
MANUAL_P1 = 202636.9         # Pa,  "Pressure = 202636.9 Pa"
MANUAL_T1 = 300.0            # K,   "Static temperature = 300 K"
MANUAL_M1 = 2.5              # "Mach number = 2.5"
TURN_DEG = 15.0              # "Angle round the corner = 195 deg" -> 195-180 = 15

# THE GATE IS AGAINST THIS.  Table .51.1, "Target" column.  UNCHANGED from R2/R1.
MANUAL_TARGET = 3.2370
MANUAL_TARGET_CFX = 3.237

# CONTEXT ONLY -- never the gate, never a band, never a reference.
ANSYS_CONTEXT = {"Fluent": 3.2316, "Fluent_ratio": 0.9980,
                 "CFX": 3.2354, "CFX_ratio": 0.9995}
MANUAL_GOAL = 0.03

# ---------------------------------------------------------------------------
# 2.  THE GAS, DERIVED FROM THE MANUAL'S OWN Cp AND MOLECULAR WEIGHT (UNCHANGED)
# ---------------------------------------------------------------------------
RR_OPENFOAM = 1.0e3 * 6.0221417930e23 * 1.38065e-23   # 8314.47006650545
RR_CODATA_2018 = 8314.46261815324

R_SPECIFIC = RR_OPENFOAM / MANUAL_MW                  # 287.04239682750293
GAMMA = MANUAL_CP / (MANUAL_CP - R_SPECIFIC)          # 1.3990093734749485

GAMMA_FROZEN = 1.3990093734749485
R_SPECIFIC_FROZEN = 287.04239682750293
M2_EXACT_GAS_FROZEN = 3.2355411372251863      # gamma from the manual's own gas
M2_EXACT_GAMMA14_FROZEN = 3.2368431056638845  # the same solve at gamma = 1.4
NU1_GAS_DEG_FROZEN = 39.160263203801104
U1_FROZEN = 867.7287202948199                 # m/s, = M1*sqrt(gamma*R*T1)

# The two exprField constants BAKED INTO controlDict.template, asserted here so a
# later divergence between the dictionary and the reference gas is caught.
PSTAG_A_FROZEN = 0.19950468673747423          # 0.5*(gamma-1)
PSTAG_B_FROZEN = 3.5062067873019136           # gamma/(gamma-1)

PM_TABLE_GAMMA14 = {2.0: 26.3798, 3.0: 49.7573, 1.5: 11.9052, 5.0: 76.9202}
PM_TABLE_TOL = 5e-5

# ---------------------------------------------------------------------------
# 3.  THE GATE AND THE DIAGNOSTIC BANDS -- UNCHANGED from R2/R1 (L-487).
# ---------------------------------------------------------------------------
TOL_GATE = 0.005          # 0.5 % of MANUAL_TARGET.  THE GATE.  UNCHANGED.
TOL_DIAG_EXACT = 0.0025   # 0.25 % of M2_EXACT_GAS.  DIAGNOSTIC, never the gate.

# GATE-BLIND PHYSICAL-RANGE REFUSAL (references NEITHER the band NOR 3.2370).
PHYS_MACH_LO = 1.0
PHYS_MACH_HI = 20.0

# ---------------------------------------------------------------------------
# 4.  ROACHE (CLAUDE.md rule 5).  Thresholds written down before any run.
# ---------------------------------------------------------------------------
FS = 1.25
RATIO = 2.0
EPS_ABS = 1e-12
STAG_TOL = 1e-3

# ---------------------------------------------------------------------------
# 5.  COMPLETION (CLAUDE.md rule 4) and the TIME-MEAN reduction / settledness.
#     endTime UNCHANGED at 7.0e-3 s.  C4 = (T U p rho Ma) -- phi is a live
#     registry field, not on disk (see the header correction).
# ---------------------------------------------------------------------------
ENDTIME = 7.0e-3
WRITEINTERVAL = 3.5e-3
MAXDELTAT = 1.0e-5
REQUIRED_FIELDS = ("T", "U", "p", "rho", "Ma")

WINDOW_FRAC = 0.50          # settled window; UNCHANGED from R2
WINDOW_CHECK_FRAC = 0.25
TOL_STAT = 5.0e-4           # settledness of the GRADED observable; UNCHANGED

# Plane-consistency clause (DECLARED; can only produce NOT A RESULT, never PASS):
# if the gate plane and the strictly-downstream diagnostic plane time-means
# disagree by more than this, the post-expansion wedge is not streamwise-uniform
# where it is being read.  This mirrors R2's inner-zone clause.
PLANE_CONSISTENCY_TOL = 1.0e-2

# ---------------------------------------------------------------------------
# 6.  PLANTED-ZERO CONTROLS (CLAUDE.md rule 3; L-487).  See the header
#     correction to PREREGISTRATION.md section 5 for why PZ-1 is the temporal
#     control on the plane .dat and not a per-face flux plant.
# ---------------------------------------------------------------------------
PLANT_DAT = 1.234e-03      # Mach, planted into a PROPER TIME-SUBSET of the .dat
PLANT_DAT_TOL = 1e-12
PLANT_FIELD = 7.77e-02     # Mach, planted into a PROPER SUBSET of the Ma field
PLANT_FIELD_TOL = 1e-9
PLANT_NU_DEG = 5.0         # degrees, planted into the Prandtl-Meyer solve

# ---------------------------------------------------------------------------
# 7.  THE MESH FAMILY (r = 2 by construction).  UNCHANGED.
# ---------------------------------------------------------------------------
LEVELS = (  # name, nxA, nxB, ny, cells
    ("L1_120x52",   24,  96,  52,   6240),
    ("L2_240x104",  48, 192, 104,  24960),
    ("L3_480x208",  96, 384, 208,  99840),
)

GATE_FO = "postExpPlane"    # faceZone postExpPlane   -- THE GATE
DIAG_FO = "postExpPlane2"   # faceZone postExpPlane2  -- DIAGNOSTIC ONLY

# Single-column sanity bound: a single column of x-normal faces in the y-band
# cannot exceed ny faces.  The single-column property itself is a GEOMETRIC
# guarantee (delta = 5e-4 m < half the finest cell dx, both stations on the face
# grid); this bound only catches a gross topoSet error.
FACE_COUNT_MAX_FRAC_OF_NY = 1.0

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
            "BLOCKED", "PENDING")


# ===========================================================================
class Refusal(Exception):
    pass


def refuse(clause, msg):
    raise Refusal("%s :: %s" % (clause, msg))


# ===========================================================================
# The Prandtl-Meyer reference -- closed form, no CFD input of any kind
# ===========================================================================
def nu_rad(M, g):
    if M < 1.0:
        raise ValueError("Prandtl-Meyer is defined for M >= 1, got %r" % (M,))
    if M == 1.0:
        return 0.0
    a = math.sqrt((g + 1.0) / (g - 1.0))
    b = math.sqrt((g - 1.0) / (g + 1.0) * (M * M - 1.0))
    return a * math.atan(b) - math.atan(math.sqrt(M * M - 1.0))


def nu_deg(M, g):
    return math.degrees(nu_rad(M, g))


def solve_M_from_nu(nu_target_rad, g, lo=1.0000001, hi=60.0, tol=1e-14):
    f_lo = nu_rad(lo, g) - nu_target_rad
    f_hi = nu_rad(hi, g) - nu_target_rad
    if f_lo > 0.0:
        raise ValueError("nu_target below nu(1) -- no root")
    if f_hi < 0.0:
        raise ValueError("nu_target above nu(%g) -- widen the bracket" % hi)
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        f_mid = nu_rad(mid, g) - nu_target_rad
        if f_mid < 0.0:
            lo, f_lo = mid, f_mid
        else:
            hi, f_hi = mid, f_mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def M2_prandtl_meyer(M1, turn_deg, g):
    return solve_M_from_nu(nu_rad(M1, g) + math.radians(turn_deg), g)


def isentropic_M_from_p0_p(p0, p, g):
    """THE GATED OBSERVABLE's per-row map: Mach from a stagnation/static pressure
    ratio via the isentropic relation.  This is the definition of Mach from a
    pressure ratio, not a fit."""
    ratio = p0 / p
    if ratio < 1.0:
        # a stagnation pressure below the static pressure is unphysical; let the
        # physical-range refusal downstream catch the resulting nan/complex.
        return float("nan")
    return math.sqrt(2.0 / (g - 1.0) * (ratio ** ((g - 1.0) / g) - 1.0))


def isentropic_M_from_T(T, T0, g):
    return math.sqrt(2.0 / (g - 1.0) * (T0 / T - 1.0))


T0_INLET = MANUAL_T1 * (1.0 + 0.5 * (GAMMA - 1.0) * MANUAL_M1 ** 2)
P0_INLET = MANUAL_P1 * (T0_INLET / MANUAL_T1) ** (GAMMA / (GAMMA - 1.0))


# ===========================================================================
# READER -- the surfaceFieldValue.dat time series (THE GATED INSTRUMENT)
# ===========================================================================
def read_surfacefieldvalue(path):
    """Parse a v2606 surfaceFieldValue.dat.  Columns are found BY HEADER NAME.
    REFUSES on a missing/zero face count -- an empty plane reads as a number and
    must never be graded."""
    if not os.path.isfile(path):
        refuse("READER", "no such file: %s" % path)
    region = None
    nfaces = None
    area = None
    weight = None
    cols = None
    rows = []
    with open(path, "r") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                body = line.lstrip()[1:].strip()
                m = re.match(r"^Region type\s*:\s*(.+)$", body)
                if m:
                    region = m.group(1).strip()
                    continue
                m = re.match(r"^Faces\s*:\s*(\d+)$", body)
                if m:
                    nfaces = int(m.group(1))
                    continue
                m = re.match(r"^Area\s*:\s*(\S+)$", body)
                if m:
                    area = float(m.group(1))
                    continue
                m = re.match(r"^Weight field\s*:\s*(.+)$", body)
                if m:
                    weight = m.group(1).strip()
                    continue
                toks = body.split()
                if toks and toks[0] == "Time":
                    cols = toks
                continue
            if cols is None:
                refuse("READER", "data row before any '# Time' header in %s" % path)
            toks = line.split()
            if len(toks) != len(cols):
                refuse("READER",
                       "row has %d fields, header declares %d, in %s: %r"
                       % (len(toks), len(cols), path, line[:120]))
            try:
                vals = [float(t) for t in toks]
            except ValueError:
                refuse("READER", "non-numeric field in %s: %r" % (path, line[:120]))
            rows.append(vals)
    if cols is None:
        refuse("READER", "no '# Time' header line in %s" % path)
    if not rows:
        refuse("READER", "no data rows in %s" % path)
    if nfaces is None:
        refuse("READER", "no '# Faces' header line in %s -- the region header is "
                         "what proves the faceZone was found" % path)
    if nfaces <= 0:
        refuse("READER", "the function object reports %d faces in its region "
                         "(%s) -- an EMPTY cross-plane reads as a number and must "
                         "never be graded" % (nfaces, path))
    return {"path": path, "region": region, "nfaces": nfaces,
            "area": area, "weight": weight, "cols": cols, "rows": rows}


def column(series, name):
    if name not in series["cols"]:
        refuse("READER", "column %r not in header %r of %s"
               % (name, series["cols"], series["path"]))
    return series["cols"].index(name)


def tail_indices(nrows, frac):
    k = max(2, int(round(frac * nrows)))
    k = min(k, nrows)
    return list(range(nrows - k, nrows)), k


def window_mean_col(series, name, frac):
    """Time-mean of a .dat column over the last `frac` of rows."""
    j = column(series, name)
    idx, k = tail_indices(len(series["rows"]), frac)
    vals = [series["rows"][i][j] for i in idx]
    return sum(vals) / len(vals), k, len(series["rows"])


def mach_series(series, g):
    """THE GATED OBSERVABLE per row: M_lab(t) from weightedAverage(pStag) and
    weightedAverage(p) via the isentropic relation."""
    jp0 = column(series, "weightedAverage(pStag)")
    jp = column(series, "weightedAverage(p)")
    out = []
    for row in series["rows"]:
        out.append(isentropic_M_from_p0_p(row[jp0], row[jp], g))
    return out


def mean_of_series(values, frac):
    """THE REDUCTION applied to a DERIVED per-row series (e.g. M_lab(t))."""
    idx, k = tail_indices(len(values), frac)
    sub = [values[i] for i in idx]
    return sum(sub) / len(sub), k, len(values)


# ===========================================================================
# READER 2 -- an OpenFOAM ascii volScalarField (used by control PZ-2)
# ===========================================================================
_UNIFORM_RE = re.compile(r"internalField\s+uniform\s+([-+0-9.eE]+)\s*;")
_NONUNIFORM_RE = re.compile(
    r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\s*\(", re.M)


def read_foam_scalar_field(path):
    if not os.path.isfile(path):
        refuse("READER", "no such field file: %s" % path)
    with open(path, "r") as fh:
        text = fh.read()
    m = _NONUNIFORM_RE.search(text)
    if m:
        n = int(m.group(1))
        start = m.end()
        end = text.find(")", start)
        if end < 0:
            refuse("READER", "unterminated nonuniform list in %s" % path)
        body = text[start:end].split()
        if len(body) != n:
            refuse("READER", "nonuniform list declares %d entries, %d found in %s"
                   % (n, len(body), path))
        try:
            return [float(t) for t in body], "nonuniform"
        except ValueError:
            refuse("READER", "non-numeric entry in the list of %s" % path)
    m = _UNIFORM_RE.search(text)
    if m:
        return [float(m.group(1))], "uniform"
    refuse("READER", "no parsable internalField in %s" % path)


def plant_into_scalar_field_subset(src, dst, delta, n_planted):
    with open(src, "r") as fh:
        text = fh.read()
    m = _NONUNIFORM_RE.search(text)
    if not m:
        refuse("PZ-2", "%s is not a nonuniform list -- cannot plant" % src)
    n = int(m.group(1))
    if n_planted >= n:
        refuse("PZ-2", "the plant subset (%d) is not a PROPER subset of the "
                       "field (%d) -- a whole-set plant shifts the mean by the "
                       "plant identically and could not fail (L-487)"
               % (n_planted, n))
    start = m.end()
    end = text.find(")", start)
    body = text[start:end].split()
    shifted = "\n".join(
        "%.16g" % (float(t) + (delta if i < n_planted else 0.0))
        for i, t in enumerate(body))
    out = text[:start] + "\n" + shifted + "\n" + text[end:]
    with open(dst, "w") as fh:
        fh.write(out)
    return n, n_planted


def plant_into_dat_subset(src, dst, colname, delta, plant_row_pred):
    """Write a copy of a surfaceFieldValue.dat with `delta` added to one column on
    the data rows for which plant_row_pred(data_row_index) is True.  The RUN TREE
    IS NEVER TOUCHED -- only this copy."""
    cols = None
    out = []
    n_data = 0
    n_planted = 0
    with open(src, "r") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.lstrip().startswith("#"):
                toks = line.lstrip()[1:].strip().split()
                if toks and toks[0] == "Time":
                    cols = toks
                out.append(line)
                continue
            if not line.strip():
                out.append(line)
                continue
            if cols is None:
                refuse("PZ-1", "data before header in %s" % src)
            j = cols.index(colname)
            toks = line.split()
            if plant_row_pred(n_data):
                toks[j] = "%.16g" % (float(toks[j]) + delta)
                n_planted += 1
            out.append("\t".join(toks))
            n_data += 1
    with open(dst, "w") as fh:
        fh.write("\n".join(out) + "\n")
    return n_data, n_planted


# ===========================================================================
# Roache triple (CLAUDE.md rule 5)
# ===========================================================================
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine,
               d21=d21, d32=d32, ratio=ratio, fs=fs,
               p=None, R=None, gci_fine=None, f_extrapolated=None, why=None)
    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"
        return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"
        out["why"] = ("the coarse-medium difference is below %g while the "
                      "medium-fine difference is not" % EPS_ABS)
        return out
    R_ = d21 / d32
    out["R"] = R_
    if R_ < 0:
        out["state"] = "OSCILLATORY"
        return out
    if abs(R_ - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"
        return out
    if R_ > 1.0:
        out["state"] = "DIVERGENT"
        return out
    p = math.log(1.0 / R_) / math.log(ratio)
    out["p"] = p
    out["state"] = "CONVERGING"
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"
        out["why"] = "r^p - 1 <= 0"
        return out
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


# ===========================================================================
# Strict completion (CLAUDE.md rule 4), two declared departures (R2 section 8)
# ===========================================================================
def _time_dirs(level_dir):
    out = []
    for name in os.listdir(level_dir):
        full = os.path.join(level_dir, name)
        if not os.path.isdir(full):
            continue
        try:
            t = float(name)
        except ValueError:
            continue
        out.append((t, name))
    out.sort()
    return out


def completion_check(level_dir):
    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("C1", "no RUN_RC.txt in %s" % level_dir)
    rc_txt = open(rc_path).read()
    m = re.search(r"^rc=(-?\d+)$", rc_txt, re.M)
    if not m:
        refuse("C1", "no rc= line in %s" % rc_path)
    if int(m.group(1)) != 0:
        refuse("C1", "rc=%s in %s -- a crash is a finding, triage first"
               % (m.group(1), rc_path))

    log = os.path.join(level_dir, "log.rhoCentralFoam")
    if not os.path.isfile(log):
        refuse("C2", "no log.rhoCentralFoam in %s" % level_dir)
    with open(log, "r", errors="replace") as fh:
        log_lines = fh.read().split("\n")
    if not any(l.strip() == "End" for l in log_lines):
        refuse("C2", "no 'End' line in %s" % log)

    times = _time_dirs(level_dir)
    if not times:
        refuse("C3", "no time directories in %s" % level_dir)
    t_last, t_last_name = times[-1]
    if abs(t_last - ENDTIME) > MAXDELTAT:
        refuse("C3", "last time %g differs from endTime %g by more than "
                     "maxDeltaT %g in %s" % (t_last, ENDTIME, MAXDELTAT, level_dir))
    log_times = [float(l.split("=", 1)[1]) for l in log_lines
                 if l.startswith("Time = ")]
    if not log_times:
        refuse("C5", "no 'Time = ' lines in %s" % log)
    if abs(log_times[-1] - t_last) > 1e-12 * max(1.0, abs(t_last)):
        refuse("C3", "the log's final Time = %g does not match the last time "
                     "directory %s in %s" % (log_times[-1], t_last_name, level_dir))

    for f in REQUIRED_FIELDS:
        p = os.path.join(level_dir, t_last_name, f)
        if not os.path.isfile(p):
            refuse("C4", "field %s missing at endTime in %s" % (f, level_dir))

    n_exec = sum(1 for l in log_lines if l.startswith("ExecutionTime = "))
    n_time = len(log_times)
    if n_exec != n_time or n_exec == 0:
        refuse("C5", "log step integrity: %d ExecutionTime lines against %d "
                     "Time lines in %s" % (n_exec, n_time, log))

    zero_dir = os.path.join(level_dir, "0")
    if not os.path.isdir(zero_dir):
        refuse("C6", "no 0/ directory in %s -- the age guard has no datum" % level_dir)
    m0 = max(os.path.getmtime(os.path.join(zero_dir, f))
             for f in os.listdir(zero_dir)
             if os.path.isfile(os.path.join(zero_dir, f)))
    for f in REQUIRED_FIELDS:
        p = os.path.join(level_dir, t_last_name, f)
        if os.path.getmtime(p) <= m0:
            refuse("C6", "AGE GUARD: %s at endTime is not newer than the newest "
                         "file in %s -- this field was not produced by the run "
                         "that was allowed to answer" % (p, zero_dir))

    return {"rc": 0, "endtime_dir": t_last_name, "t_last": t_last,
            "n_steps": n_time, "wall_ok": True}


# ===========================================================================
# One level -> the gate value (flux-weighted p0/p Mach time-mean) + diagnostics
# ===========================================================================
def read_plane(level_dir, foname, ny):
    dat = os.path.join(level_dir, "postProcessing", foname, "0",
                       "surfaceFieldValue.dat")
    s = read_surfacefieldvalue(dat)
    if s["nfaces"] > FACE_COUNT_MAX_FRAC_OF_NY * ny:
        refuse("PLANE", "faceZone %s holds %d faces at ny=%d -- a single column of "
                        "x-normal faces in the y-band cannot exceed ny; topoSet may "
                        "have captured more than one column (%s)"
               % (foname, s["nfaces"], ny, dat))
    return s, dat


def read_level(level_dir, ny):
    comp = completion_check(level_dir)

    gate, gate_dat = read_plane(level_dir, GATE_FO, ny)
    diag, diag_dat = read_plane(level_dir, DIAG_FO, ny)

    # THE GATED OBSERVABLE: per-row p0/p Mach, then time-mean over the window.
    m_ser = mach_series(gate, GAMMA)
    m_lab, k, n = mean_of_series(m_ser, WINDOW_FRAC)
    m_lab_short, k_s, _ = mean_of_series(m_ser, WINDOW_CHECK_FRAC)
    stat = abs(m_lab - m_lab_short)

    # the diagnostic plane's own p0/p Mach time-mean (gates nothing)
    m_ser2 = mach_series(diag, GAMMA)
    m_lab2, _, _ = mean_of_series(m_ser2, WINDOW_FRAC)

    # DIAGNOSTICS, printed beside the gate, gating nothing.
    ma_massavg, _, _ = window_mean_col(gate, "weightedAverage(Ma)", WINDOW_FRAC)
    p_massavg, _, _ = window_mean_col(gate, "weightedAverage(p)", WINDOW_FRAC)
    t_massavg, _, _ = window_mean_col(gate, "weightedAverage(T)", WINDOW_FRAC)
    p0_massavg, _, _ = window_mean_col(gate, "weightedAverage(pStag)", WINDOW_FRAC)
    m_from_T = isentropic_M_from_T(t_massavg, T0_INLET, GAMMA)

    # GATE-BLIND physical-range refusal on the graded value and the diagnostic.
    for label, val in (("gate-plane", m_lab), ("diag-plane", m_lab2),
                       ("flux-Ma", ma_massavg)):
        if not math.isfinite(val) or not (PHYS_MACH_LO < val < PHYS_MACH_HI):
            refuse("PHYS", "the %s time-mean Mach is %r in %s -- not a physical "
                           "supersonic Mach number in (%.1f, %.1f); this "
                           "references neither the gate band nor the target"
                   % (label, val, level_dir, PHYS_MACH_LO, PHYS_MACH_HI))

    return {
        "completion": comp,
        "gate_dat": gate_dat, "diag_dat": diag_dat,
        "gate_nfaces": gate["nfaces"], "gate_area": gate["area"],
        "gate_region": gate["region"], "gate_weight": gate["weight"],
        "diag_nfaces": diag["nfaces"], "diag_region": diag["region"],
        "M_lab": m_lab, "M_lab_diag_plane": m_lab2,
        "M_lab_short_window": m_lab_short, "stationarity": stat,
        "flux_Ma": ma_massavg, "flux_p": p_massavg, "flux_T": t_massavg,
        "flux_pStag": p0_massavg, "M_from_T": m_from_T,
        "window_rows": k, "window_check_rows": k_s, "series_rows": n,
        "endtime_dir": comp["endtime_dir"],
    }


# ===========================================================================
# PLANTED-ZERO CONTROLS (CLAUDE.md rule 3; L-487)
# ===========================================================================
def control_pz1(level_dir, ny):
    """Plant into a COPY of the gate plane's .dat weightedAverage(Ma) column, on
    a PROPER TIME-SUBSET of the settled window, and require the window-mean to
    move by the plant scaled by the planted FRACTION.  This tests the reader and
    the temporal reduction the gate applies (the flux weighting itself is done by
    OpenFOAM and verified from source -- see the header correction)."""
    src = os.path.join(level_dir, "postProcessing", GATE_FO, "0",
                       "surfaceFieldValue.dat")
    series = read_surfacefieldvalue(src)
    n_rows = len(series["rows"])
    win_idx, k_win = tail_indices(n_rows, WINDOW_FRAC)
    plant_from = win_idx[len(win_idx) // 2]

    def pred(i):
        return i >= plant_from

    base, _, _ = window_mean_col(series, "weightedAverage(Ma)", WINDOW_FRAC)
    tmp = tempfile.mkdtemp(prefix="vmfl051r3_pz1_")
    try:
        flat = os.path.join(tmp, "flat.dat")
        shutil.copy2(src, flat)
        v_flat, _, _ = window_mean_col(read_surfacefieldvalue(flat),
                                       "weightedAverage(Ma)", WINDOW_FRAC)
        if abs(v_flat - base) > PLANT_DAT_TOL:
            refuse("PZ-1", "the unplanted copy already differs by %g -- the "
                           "reader is not deterministic" % (v_flat - base))
        planted = os.path.join(tmp, "planted.dat")
        plant_into_dat_subset(src, planted, "weightedAverage(Ma)", PLANT_DAT, pred)
        n_planted_in_window = sum(1 for i in win_idx if pred(i))
        if n_planted_in_window == 0 or n_planted_in_window >= k_win:
            refuse("PZ-1", "the plant selected %d of %d window rows -- it must be "
                           "a PROPER, NON-EMPTY subset (L-487)"
                   % (n_planted_in_window, k_win))
        v_planted, _, _ = window_mean_col(read_surfacefieldvalue(planted),
                                          "weightedAverage(Ma)", WINDOW_FRAC)
        seen = v_planted - base
        expected = PLANT_DAT * (n_planted_in_window / float(k_win))
        if abs(seen - expected) > PLANT_DAT_TOL:
            refuse("PZ-1", "planted %g into %d of %d window rows of a copy of %s; "
                           "expected the mean to move by %g, saw %g (error %g > "
                           "%g) -- THE READER CANNOT SEE THE PLANT IN THE REDUCTION "
                           "IT GRADES" % (PLANT_DAT, n_planted_in_window, k_win, src,
                                          expected, seen, seen - expected,
                                          PLANT_DAT_TOL))
        return {"plant": PLANT_DAT, "seen": seen, "expected": expected,
                "base": base, "n_planted_in_window": n_planted_in_window,
                "n_window": k_win, "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz2(level_dir, endtime_dir):
    """Plant into a COPY of the Ma FIELD at endTime and require the field reader
    to see the plant in the field mean.  The control that demonstrates the
    comparator can read a NON-ZERO out of the Mach field on disk."""
    src = os.path.join(level_dir, endtime_dir, "Ma")
    vals, kind = read_foam_scalar_field(src)
    if kind != "nonuniform":
        refuse("PZ-2", "the Ma field at endTime in %s is '%s' -- a uniform Mach "
                       "field after an expansion fan is not a solution"
               % (level_dir, kind))
    n_total = len(vals)
    mean0 = sum(vals) / n_total
    n_plant = n_total // 2
    tmp = tempfile.mkdtemp(prefix="vmfl051r3_pz2_")
    try:
        flat = os.path.join(tmp, "Ma_flat")
        shutil.copy2(src, flat)
        v_flat, _ = read_foam_scalar_field(flat)
        if abs(sum(v_flat) / len(v_flat) - mean0) > PLANT_FIELD_TOL:
            refuse("PZ-2", "the unplanted field copy already differs -- the field "
                           "reader is not deterministic")
        planted = os.path.join(tmp, "Ma_planted")
        n, np_ = plant_into_scalar_field_subset(src, planted, PLANT_FIELD, n_plant)
        v_p, _ = read_foam_scalar_field(planted)
        if len(v_p) != n or n != n_total:
            refuse("PZ-2", "planted copy has %d entries, original %d"
                   % (len(v_p), n_total))
        seen = sum(v_p) / len(v_p) - mean0
        expected = PLANT_FIELD * (np_ / float(n_total))
        if abs(seen - expected) > PLANT_FIELD_TOL:
            refuse("PZ-2", "planted %g into %d of %d cells of a copy of the Ma "
                           "field at %s; expected mean shift %g, saw %g (error %g) "
                           "-- THE FIELD READER CANNOT SEE A NON-ZERO"
                   % (PLANT_FIELD, np_, n_total, src, expected, seen, seen - expected))
        return {"plant": PLANT_FIELD, "seen": seen, "expected": expected,
                "n_cells": n_total, "n_planted": np_, "field_mean": mean0,
                "field_min": min(vals), "field_max": max(vals), "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz3():
    """Plant into the REFERENCE COMPUTATION.  A root finder returning a constant
    would sail through every deviation test in this file."""
    M2 = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, GAMMA)
    ident = nu_deg(M2, GAMMA) - nu_deg(MANUAL_M1, GAMMA)
    if abs(ident - TURN_DEG) > 1e-9:
        refuse("PZ-3", "the solved M2 does not satisfy its own defining identity: "
                       "nu(M2) - nu(M1) = %.12f deg, expected %g" % (ident, TURN_DEG))
    M2p = M2_prandtl_meyer(MANUAL_M1, TURN_DEG + PLANT_NU_DEG, GAMMA)
    if abs(M2p - M2) < 1e-6:
        refuse("PZ-3", "a %g deg change of turn angle moved M2 by %g -- the root "
                       "finder is returning a constant" % (PLANT_NU_DEG, M2p - M2))
    identp = nu_deg(M2p, GAMMA) - nu_deg(MANUAL_M1, GAMMA)
    if abs(identp - (TURN_DEG + PLANT_NU_DEG)) > 1e-9:
        refuse("PZ-3", "the planted solve is not self-consistent: %.12f deg" % identp)
    return {"M2": M2, "identity_deg": ident, "plant_deg": PLANT_NU_DEG,
            "M2_planted": M2p, "delta": M2p - M2, "fired": True}


# ===========================================================================
# GRADE
# ===========================================================================
def grade():
    M2_exact = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, GAMMA)
    if abs(M2_exact - M2_EXACT_GAS_FROZEN) > 1e-12:
        refuse("REFERENCE", "the in-module Prandtl-Meyer solve gives %.16f but the "
                            "frozen literal is %.16f -- the reference has drifted"
               % (M2_exact, M2_EXACT_GAS_FROZEN))
    # assert the baked exprField constants still match the reference gas
    if abs(0.5 * (GAMMA - 1.0) - PSTAG_A_FROZEN) > 1e-15 or \
       abs(GAMMA / (GAMMA - 1.0) - PSTAG_B_FROZEN) > 1e-13:
        refuse("REFERENCE", "the pStag exprField constants (A=%.17g, B=%.17g) no "
                            "longer match the reference gas -- the field the plane "
                            "FO averages would be built for a different gas"
               % (0.5 * (GAMMA - 1.0), GAMMA / (GAMMA - 1.0)))

    controls = {"PZ-3_reference": control_pz3()}

    per_level = {}
    for name, nxa, nxb, ny, cells in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        if not os.path.isdir(d):
            refuse("C0", "level directory %s does not exist -- nothing to grade" % d)
        per_level[name] = read_level(d, ny)
        per_level[name]["cells"] = cells
        per_level[name]["nxA"], per_level[name]["nxB"], per_level[name]["ny"] = \
            nxa, nxb, ny

    finest = LEVELS[-1][0]
    controls["PZ-1_plane_dat_reader"] = control_pz1(
        os.path.join(RUN_ROOT, finest), LEVELS[-1][3])
    controls["PZ-2_field_reader"] = control_pz2(
        os.path.join(RUN_ROOT, finest), per_level[finest]["endtime_dir"])

    vals = [per_level[n]["M_lab"] for n, _, _, _, _ in LEVELS]
    triple = roache(vals[0], vals[1], vals[2])

    M_lab = vals[-1]
    dev_target = (M_lab - MANUAL_TARGET) / MANUAL_TARGET
    dev_exact = (M_lab - M2_exact) / M2_exact

    verdict = None
    why = None

    # rule 5 step 1: any level not settled -> NOT A RESULT
    for name, _, _, _, _ in LEVELS:
        L = per_level[name]
        if L["stationarity"] > TOL_STAT:
            verdict = "NOT A RESULT"
            why = ("level %s time-mean is NOT settled: |mean(last %.0f%%) - "
                   "mean(last %.0f%%)| = %.3e > %.3e (rule 5 step 1)"
                   % (name, 100 * WINDOW_FRAC, 100 * WINDOW_CHECK_FRAC,
                      L["stationarity"], TOL_STAT))
            break
    # declared plane-consistency clause -- NOT A RESULT only.
    if verdict is None:
        L = per_level[finest]
        pc = abs(L["M_lab"] - L["M_lab_diag_plane"]) / abs(L["M_lab"])
        if pc > PLANE_CONSISTENCY_TOL:
            verdict = "NOT A RESULT"
            why = ("the gate plane and the strictly-downstream diagnostic plane "
                   "time-means disagree by %.3e > %.3e at %s -- the post-expansion "
                   "wedge is not streamwise-uniform where it is read"
                   % (pc, PLANE_CONSISTENCY_TOL, finest))

    # rule 5 step 2: triple not CONVERGING -> NOT A RESULT
    if verdict is None and triple["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = "grid triple is %s, not CONVERGING (rule 5 step 2)" % triple["state"]

    # rule 5 step 3: CONVERGING -> PASS inside band, else GATE FAIL
    if verdict is None:
        if abs(dev_target) <= TOL_GATE:
            verdict = "PASS"
            why = ("|M_lab - target| / target = %.6f %% <= %.4f %% (rule 5 step 3)"
                   % (100 * abs(dev_target), 100 * TOL_GATE))
        else:
            verdict = "GATE FAIL"
            why = ("|M_lab - target| / target = %.6f %% > %.4f %%"
                   % (100 * abs(dev_target), 100 * TOL_GATE))

    assert verdict in VERDICTS

    result = {
        "case": "VMFL051-R3",
        "successor_of": "VMFL051-R2 (register Row #73, NOT A RESULT -- OSCILLATORY)",
        "manual_page": MANUAL_PAGE,
        "verdict": verdict,
        "why": why,
        "lever": "SPATIAL reduction: mass-flux-weighted p0/p Mach on the frozen "
                 "cross-plane postExpPlane (R2's temporal reduction KEPT)",
        "reduction": {"kind": "time-mean of the per-row flux-weighted p0/p Mach "
                              "over the last %.0f%% of rows" % (100 * WINDOW_FRAC),
                      "endTime": ENDTIME, "window_frac": WINDOW_FRAC,
                      "settledness": "window-length insensitivity "
                                     "|mean(last %.0f%%)-mean(last %.0f%%)| <= %g"
                                     % (100 * WINDOW_FRAC, 100 * WINDOW_CHECK_FRAC,
                                        TOL_STAT)},
        "gate": {"reference": MANUAL_TARGET,
                 "reference_class": "manual printed target, Table .51.1 "
                                    "(analytic Prandtl-Meyer)",
                 "tolerance_rel": TOL_GATE, "lab_value": M_lab,
                 "deviation_rel": dev_target, "deviation_pct": 100 * dev_target},
        "diagnostic_exact": {"reference": M2_exact,
                             "reference_class": "closed-form Prandtl-Meyer for the "
                                                "manual's own gas, gamma = %.16f"
                                                % GAMMA,
                             "tolerance_rel": TOL_DIAG_EXACT,
                             "deviation_rel": dev_exact,
                             "deviation_pct": 100 * dev_exact,
                             "inside": abs(dev_exact) <= TOL_DIAG_EXACT},
        "gamma": GAMMA, "R_specific": R_SPECIFIC, "RR_openfoam": RR_OPENFOAM,
        "M2_exact_gamma14": M2_EXACT_GAMMA14_FROZEN,
        "pStag_expr_A": PSTAG_A_FROZEN, "pStag_expr_B": PSTAG_B_FROZEN,
        "ansys_context_never_the_gate": ANSYS_CONTEXT,
        "triple": triple, "levels": per_level, "controls": controls,
        "endTime": ENDTIME, "tol_stationarity": TOL_STAT,
        "plane_consistency_tol": PLANE_CONSISTENCY_TOL,
    }
    return result


def report(res):
    P = print
    P("=" * 78)
    P("VMFL051-R3 -- Isentropic Expansion of Supersonic Flow Over a Convex Corner")
    P("Successor to VMFL051-R2 (Row #73, NOT A RESULT -- OSCILLATORY triple)")
    P("Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. %s"
      % res["manual_page"])
    P("=" * 78)
    P("")
    P("LEVER: %s" % res["lever"])
    P("REDUCTION: %s" % res["reduction"]["kind"])
    P("           endTime %.4g s (UNCHANGED from R2); settledness: %s"
      % (res["reduction"]["endTime"], res["reduction"]["settledness"]))
    P("")
    P("gamma  = %.16f   (from the manual's own Cp = %g and MW = %g; NOT 1.4)"
      % (res["gamma"], MANUAL_CP, MANUAL_MW))
    P("pStag  = p*(1 + %.17g*Ma^2)^%.17g   (isentropic, frozen gas)"
      % (res["pStag_expr_A"], res["pStag_expr_B"]))
    P("")
    P("--- controls (CLAUDE.md rule 3; L-487 proper-subset plants) ---")
    for k, v in res["controls"].items():
        P("  %-24s FIRED  %s" % (k, {kk: ("%.6g" % vv if isinstance(vv, float)
                                          else vv)
                                     for kk, vv in v.items() if kk != "fired"}))
    P("")
    P("--- levels (gate value = flux-weighted p0/p Mach time-mean) ---")
    for name, _, _, _, cells in LEVELS:
        L = res["levels"][name]
        P("  %-14s cells %6d  plane %4d faces  M_lab = %.10f  (diag-plane %.10f)"
          % (name, cells, L["gate_nfaces"], L["M_lab"], L["M_lab_diag_plane"]))
        P("  %-14s   settledness |d(window)| = %.3e (tol %.1e)  (%d/%d window rows)"
          % ("", L["stationarity"], TOL_STAT, L["window_rows"], L["series_rows"]))
        P("  %-14s   diagnostics: flux <Ma> = %.10f, M from T = %.10f, "
          "flux <p> = %.4f Pa, flux <pStag> = %.4f Pa"
          % ("", L["flux_Ma"], L["M_from_T"], L["flux_p"], L["flux_pStag"]))
    P("")
    t = res["triple"]
    P("--- Roache triple on the flux-weighted p0/p Mach, r = %.1f, Fs = %.2f ---"
      % (t["ratio"], t["fs"]))
    P("  coarse %.10f   medium %.10f   fine %.10f"
      % (t["f_coarse"], t["f_med"], t["f_fine"]))
    P("  d32 (coarse-medium) = %.6e   d21 (medium-fine) = %.6e"
      % (t["d32"], t["d21"]))
    P("  R = %s   observed order p = %s   state = %s"
      % ("%.6f" % t["R"] if t["R"] is not None else "n/a",
         "%.4f" % t["p"] if t["p"] is not None else "n/a", t["state"]))
    if t["state"] == "CONVERGING":
        P("  GCI(fine) = %.4f %%   Richardson extrapolation = %.10f"
          % (100 * t["gci_fine"], t["f_extrapolated"]))
    else:
        P("  no GCI quoted -- the three values are not monotone convergent")
    P("")
    g = res["gate"]
    d = res["diagnostic_exact"]
    P("--- THE GATE (manual printed target, Table .51.1; UNCHANGED) ---")
    P("  reference   %.4f" % g["reference"])
    P("  lab value   %.10f   (finest level, %s)" % (g["lab_value"], LEVELS[-1][0]))
    P("  deviation   %+.6f %%   band +/- %.4f %%"
      % (g["deviation_pct"], 100 * g["tolerance_rel"]))
    P("")
    P("--- DIAGNOSTIC, NEVER THE GATE: the closed-form exact value ---")
    P("  exact       %.16f   (Prandtl-Meyer, gamma = %.16f)"
      % (d["reference"], res["gamma"]))
    P("  deviation   %+.6f %%   diagnostic band +/- %.4f %%   inside: %s"
      % (d["deviation_pct"], 100 * d["tolerance_rel"], d["inside"]))
    P("")
    P("--- CONTEXT ONLY, never the gate: Ansys's own reported values ---")
    P("  Fluent %.4f (ratio %.4f)   CFX %.4f (ratio %.4f)"
      % (ANSYS_CONTEXT["Fluent"], ANSYS_CONTEXT["Fluent_ratio"],
         ANSYS_CONTEXT["CFX"], ANSYS_CONTEXT["CFX_ratio"]))
    P("")
    P("VERDICT: %s" % res["verdict"])
    P("  %s" % res["why"])
    P("=" * 78)


# ===========================================================================
# --verify-frozen
# ===========================================================================
def verify_frozen(commitish):
    with open(os.path.abspath(__file__), "rb") as fh:
        mine = fh.read()
    try:
        blob = subprocess.check_output(
            ["git", "-C", REPO, "cat-file", "blob",
             "%s:%s" % (commitish, SELF_REL)])
    except subprocess.CalledProcessError as exc:
        print("REFUSE: FREEZE :: cannot read %s:%s from git (%s)"
              % (commitish, SELF_REL, exc), file=sys.stderr)
        return 2
    if mine != blob:
        print("REFUSE: FREEZE :: this file on disk (sha256 %s) is NOT the blob "
              "committed at %s (sha256 %s) -- the grading path has moved"
              % (hashlib.sha256(mine).hexdigest()[:16], commitish,
                 hashlib.sha256(blob).hexdigest()[:16]), file=sys.stderr)
        return 2
    print("FREEZE VERIFIED: grade_vmfl051_r3.py is byte-identical to %s:%s "
          "(sha256 %s)" % (commitish, SELF_REL,
                           hashlib.sha256(mine).hexdigest()[:16]))
    return 0


# ===========================================================================
# --selftest : every control and every classifier arm, ZERO solver compute
# ===========================================================================
def _surface_fixture(mean_M=3.2355411372251863, amp_M=3.0e-3, n=400, endt=ENDTIME,
                     drift=False, m0_M=3.20):
    """A stationary (or, with drift=True, ramping) fixture in the REAL v2606
    surfaceFieldValue.dat format.  pStag and p are chosen so the isentropic p0/p
    Mach equals the target row Mach exactly, so the derived-M reduction can be
    checked against a known value."""
    g = GAMMA
    p = 66500.0
    lines = ["# Region type : faceZone postExpPlane",
             "# Faces       : 22",
             "# Area        : 8.5e-04",
             "# Scale factor : 1",
             "# Weight field : phi",
             "# Time\tweightedAverage(p)\tweightedAverage(T)"
             "\tweightedAverage(Ma)\tweightedAverage(pStag)"]
    for i in range(n):
        t = endt * (i + 1) / n
        if drift:
            M = m0_M + (mean_M - m0_M) * (i / (n - 1.0))
        else:
            M = mean_M + (amp_M if (i % 2 == 0) else -amp_M)
        p0 = p * (1.0 + 0.5 * (g - 1.0) * M * M) ** (g / (g - 1.0))
        lines.append("%.8g\t%.10g\t%.6g\t%.10g\t%.10g"
                     % (t, p, 218.25, M, p0))
    return "\n".join(lines) + "\n"


FIELD_FIXTURE = """\
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      Ma;
}

dimensions      [0 0 0 0 0 0 0];

internalField   nonuniform List<scalar>
6
(
2.5
2.5
3.1
3.2355411
3.2355411
2.9
)
;

boundaryField
{
    outlet { type zeroGradient; }
}
"""


def selftest():
    ok = [0]
    bad = [0]

    def check(label, cond, extra=""):
        if cond:
            ok[0] += 1
            print("  ok    %s %s" % (label, extra))
        else:
            bad[0] += 1
            print("  FAIL  %s %s" % (label, extra))

    print("VMFL051-R3 comparator selftest -- no solver, no run tree touched")
    print("")
    print("[A] the gas, from the manual's own Cp and molecular weight")
    check("RR (OpenFOAM v2606 NA*k*1e3)", abs(RR_OPENFOAM - 8314.47006650545) < 1e-8,
          "= %.11f" % RR_OPENFOAM)
    check("R specific", abs(R_SPECIFIC - R_SPECIFIC_FROZEN) < 1e-10,
          "= %.14f J/kg-K" % R_SPECIFIC)
    check("gamma NOT 1.4", abs(GAMMA - GAMMA_FROZEN) < 1e-14 and abs(GAMMA - 1.4) > 1e-4,
          "= %.16f" % GAMMA)
    check("pStag exprField A = 0.5*(g-1)", abs(0.5 * (GAMMA - 1.0) - PSTAG_A_FROZEN) < 1e-15,
          "= %.17g" % (0.5 * (GAMMA - 1.0)))
    check("pStag exprField B = g/(g-1)", abs(GAMMA / (GAMMA - 1.0) - PSTAG_B_FROZEN) < 1e-13,
          "= %.17g" % (GAMMA / (GAMMA - 1.0)))
    check("U1 from the manual's M1, T1", abs(MANUAL_M1 * math.sqrt(
        GAMMA * R_SPECIFIC * MANUAL_T1) - U1_FROZEN) < 1e-9,
        "= %.14f m/s" % (MANUAL_M1 * math.sqrt(GAMMA * R_SPECIFIC * MANUAL_T1)))

    print("")
    print("[B] the Prandtl-Meyer function against Anderson's Appendix C (gamma=1.4)")
    for M, tab in sorted(PM_TABLE_GAMMA14.items()):
        got = nu_deg(M, 1.4)
        check("nu(%.1f) = %.4f deg" % (M, tab), abs(got - tab) <= PM_TABLE_TOL,
              "computed %.6f" % got)
    check("nu(1) = 0", abs(nu_deg(1.0, 1.4)) < 1e-12)

    print("")
    print("[C] the frozen reference values (UNCHANGED from R2/R1)")
    m2 = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, GAMMA)
    check("M2 exact, manual's gas", abs(m2 - M2_EXACT_GAS_FROZEN) < 1e-12,
          "= %.16f" % m2)
    m2_14 = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, 1.4)
    check("M2 exact, gamma = 1.4", abs(m2_14 - M2_EXACT_GAMMA14_FROZEN) < 1e-12,
          "= %.16f" % m2_14)

    print("")
    print("[C2] the isentropic p0/p Mach map inverts exactly")
    for Mtest in (2.5, 3.0, M2_EXACT_GAS_FROZEN, 3.5):
        p = 60000.0
        p0 = p * (1.0 + 0.5 * (GAMMA - 1.0) * Mtest * Mtest) ** (GAMMA / (GAMMA - 1.0))
        Mrec = isentropic_M_from_p0_p(p0, p, GAMMA)
        check("M from p0/p recovers %.6f" % Mtest, abs(Mrec - Mtest) < 1e-12,
              "recovered %.12f" % Mrec)

    print("")
    print("[D] the plane reader and the flux-weighted p0/p Mach reduction "
          "(REAL surfaceFieldValue.dat format)")
    tmp = tempfile.mkdtemp(prefix="vmfl051r3_selftest_")
    try:
        f = os.path.join(tmp, "surfaceFieldValue.dat")
        open(f, "w").write(_surface_fixture())
        s = read_surfacefieldvalue(f)
        check("region-type header parsed",
              s["region"] == "faceZone postExpPlane", s["region"])
        check("face count parsed", s["nfaces"] == 22, "nfaces = %d" % s["nfaces"])
        check("weight field parsed", s["weight"] == "phi", s["weight"])
        check("columns located by NAME",
              s["cols"] == ["Time", "weightedAverage(p)", "weightedAverage(T)",
                            "weightedAverage(Ma)", "weightedAverage(pStag)"],
              str(s["cols"]))
        m_ser = mach_series(s, GAMMA)
        m_lab, k, n = mean_of_series(m_ser, WINDOW_FRAC)
        check("flux-weighted p0/p Mach time-mean equals the fixture Mach",
              abs(m_lab - 3.2355411372251863) < 1e-6,
              "M_lab = %.10f over %d/%d rows" % (m_lab, k, n))
        m_short, _, _ = mean_of_series(m_ser, WINDOW_CHECK_FRAC)
        check("a STATIONARY series is SETTLED (window-insensitive)",
              abs(m_lab - m_short) <= TOL_STAT,
              "|d| = %.3e <= %.1e" % (abs(m_lab - m_short), TOL_STAT))

        fd = os.path.join(tmp, "drift.dat")
        open(fd, "w").write(_surface_fixture(drift=True))
        sd = read_surfacefieldvalue(fd)
        md = mach_series(sd, GAMMA)
        md_long, _, _ = mean_of_series(md, WINDOW_FRAC)
        md_short, _, _ = mean_of_series(md, WINDOW_CHECK_FRAC)
        check("a DRIFTING series is NOT settled (fail arm; the clause can say no)",
              abs(md_long - md_short) > TOL_STAT,
              "|d| = %.3e > %.1e -> NOT A RESULT" % (abs(md_long - md_short), TOL_STAT))

        # refusal arm: empty faceZone (rc must be 2 via the Refusal path)
        f2 = os.path.join(tmp, "nofaces.dat")
        open(f2, "w").write(_surface_fixture().replace("# Faces       : 22",
                                                       "# Faces       : 0"))
        try:
            read_surfacefieldvalue(f2)
            check("an EMPTY cross-plane REFUSES", False)
        except Refusal as e:
            check("an EMPTY cross-plane REFUSES", "EMPTY cross-plane" in str(e))

        print("")
        print("[E] planted-zero, plane .dat reader (PZ-1), proper time-subset (L-487)")
        base, _, _ = window_mean_col(s, "weightedAverage(Ma)", WINDOW_FRAC)
        n_rows = len(s["rows"])
        win_idx, k_win = tail_indices(n_rows, WINDOW_FRAC)
        plant_from = win_idx[len(win_idx) // 2]
        flat = os.path.join(tmp, "flat.dat")
        shutil.copy2(f, flat)
        vf, _, _ = window_mean_col(read_surfacefieldvalue(flat),
                                   "weightedAverage(Ma)", WINDOW_FRAC)
        check("unplanted copy shows NO signal", abs(vf - base) < PLANT_DAT_TOL,
              "delta %.3e" % (vf - base))
        pl = os.path.join(tmp, "planted.dat")
        plant_into_dat_subset(f, pl, "weightedAverage(Ma)", PLANT_DAT,
                              lambda i: i >= plant_from)
        n_pw = sum(1 for i in win_idx if i >= plant_from)
        vp, _, _ = window_mean_col(read_surfacefieldvalue(pl),
                                   "weightedAverage(Ma)", WINDOW_FRAC)
        expected = PLANT_DAT * (n_pw / float(k_win))
        check("proper-subset plant moves the mean by plant*fraction",
              abs((vp - base) - expected) < PLANT_DAT_TOL,
              "planted %d/%d rows, expected %.6g, saw %.6g"
              % (n_pw, k_win, expected, vp - base))
        n_all = sum(1 for _ in win_idx)
        check("a WHOLE-window plant is the INERT config the control refuses",
              n_all >= k_win, "n_planted_in_window %d >= window %d -> REFUSE"
              % (n_all, k_win))

        print("")
        print("[F] planted-zero, Ma FIELD reader (PZ-2), proper-subset (L-487)")
        ff = os.path.join(tmp, "Ma")
        open(ff, "w").write(FIELD_FIXTURE)
        vals, kind = read_foam_scalar_field(ff)
        check("nonuniform field parsed", kind == "nonuniform" and len(vals) == 6,
              "%d values, mean %.6f" % (len(vals), sum(vals) / len(vals)))
        m0 = sum(vals) / len(vals)
        ffp = os.path.join(tmp, "Ma_planted")
        n_tot, n_pl = plant_into_scalar_field_subset(ff, ffp, PLANT_FIELD, 6 // 2)
        v3, _ = read_foam_scalar_field(ffp)
        exp_field = PLANT_FIELD * (n_pl / float(n_tot))
        check("proper-subset field plant shows plant*fraction",
              abs((sum(v3) / len(v3) - m0) - exp_field) < PLANT_FIELD_TOL,
              "planted %d/%d, expected %.6g, saw %.6g"
              % (n_pl, n_tot, exp_field, sum(v3) / len(v3) - m0))
        try:
            plant_into_scalar_field_subset(ff, os.path.join(tmp, "x"),
                                           PLANT_FIELD, 6)
            check("a whole-set field plant is REFUSED (inert, L-487)", False)
        except Refusal as e:
            check("a whole-set field plant is REFUSED (inert, L-487)",
                  "PROPER subset" in str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("[G] planted-zero, the REFERENCE COMPUTATION (PZ-3)")
    try:
        pz3 = control_pz3()
        check("the solved M2 satisfies nu(M2)-nu(M1) = 15 deg",
              abs(pz3["identity_deg"] - TURN_DEG) < 1e-9,
              "%.12f deg" % pz3["identity_deg"])
        check("a planted turn moves the root", abs(pz3["delta"]) > 1e-3,
              "+%g deg -> delta M2 = %+.6f" % (PLANT_NU_DEG, pz3["delta"]))
    except Refusal as e:
        check("PZ-3", False, str(e))

    print("")
    print("[H] the Roache classifier, every state")
    t1 = roache(1.0 + 0.04, 1.0 + 0.02, 1.0 + 0.01)
    check("first-order family -> CONVERGING, p ~ 1",
          t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9,
          "p = %.6f" % t1["p"])
    t2 = roache(1.0 + 0.04, 1.0 + 0.01, 1.0 + 0.0025)
    check("second-order family -> CONVERGING, p ~ 2",
          t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9,
          "p = %.6f, GCI %.4f %%" % (t2["p"], 100 * t2["gci_fine"]))
    check("divergent family -> DIVERGENT",
          roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory family -> OSCILLATORY (R2's own state)",
          roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("equal-step family -> STAGNANT",
          roache(1.0, 1.1, 1.2)["state"] == "STAGNANT")
    check("identical values -> EXACT",
          roache(2.5, 2.5, 2.5)["state"] == "EXACT")
    check("no GCI is quoted for a non-CONVERGING triple",
          roache(1.0, 1.2, 1.0)["gci_fine"] is None)

    print("")
    print("[I] the gate, both arms (band UNCHANGED)")
    inside = M2_EXACT_GAS_FROZEN
    check("the exact value for the manual's gas PASSES the gate",
          abs((inside - MANUAL_TARGET) / MANUAL_TARGET) <= TOL_GATE,
          "%.5f %%" % (100 * (inside - MANUAL_TARGET) / MANUAL_TARGET))
    outside = MANUAL_TARGET * (1.0 + 1.5 * TOL_GATE)
    check("a value 0.75 %% off FAILS the gate",
          abs((outside - MANUAL_TARGET) / MANUAL_TARGET) > TOL_GATE,
          "%.5f %%" % (100 * (outside - MANUAL_TARGET) / MANUAL_TARGET))
    check("an INCOMPRESSIBLE treatment (M unchanged at 2.5) FAILS the gate",
          abs((MANUAL_M1 - MANUAL_TARGET) / MANUAL_TARGET) > TOL_GATE,
          "%.3f %%" % (100 * (MANUAL_M1 - MANUAL_TARGET) / MANUAL_TARGET))
    check("Ansys Fluent's own reported value would PASS this gate",
          abs((ANSYS_CONTEXT["Fluent"] - MANUAL_TARGET) / MANUAL_TARGET) <= TOL_GATE,
          "%.4f %%" % (100 * (ANSYS_CONTEXT["Fluent"] - MANUAL_TARGET) / MANUAL_TARGET))

    print("")
    print("[J] the GATE-BLIND physical-range refusal (neither band nor target)")
    check("a subsonic mean (M=0.5) is out of the physical range",
          not (PHYS_MACH_LO < 0.5 < PHYS_MACH_HI), "M=0.5 -> REFUSE")
    check("an absurd mean (M=50) is out of the physical range",
          not (PHYS_MACH_LO < 50.0 < PHYS_MACH_HI), "M=50 -> REFUSE")
    check("a physical supersonic mean (M=3.2) is in range",
          (PHYS_MACH_LO < 3.2 < PHYS_MACH_HI),
          "range (%.1f,%.1f) mentions neither 3.2370 nor 0.5%%"
          % (PHYS_MACH_LO, PHYS_MACH_HI))
    check("an unphysical p0<p ratio yields nan (caught by the range refusal)",
          not math.isfinite(isentropic_M_from_p0_p(1.0, 2.0, GAMMA)),
          "M(p0/p<1) = %r" % isentropic_M_from_p0_p(1.0, 2.0, GAMMA))

    print("")
    print("[K] the verdict vocabulary")
    check("only the six words exist", set(VERDICTS) == {
        "PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"})

    print("")
    print("selftest: %d ok, %d FAIL" % (ok[0], bad[0]))
    return 0 if bad[0] == 0 else 1


# ===========================================================================
def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify-frozen" in argv:
        i = argv.index("--verify-frozen")
        if i + 1 >= len(argv):
            print("REFUSE: --verify-frozen needs a commit-ish", file=sys.stderr)
            return 2
        return verify_frozen(argv[i + 1])
    if "--dryrun-reader" in argv:
        i = argv.index("--dryrun-reader")
        if i + 1 >= len(argv):
            print("REFUSE: --dryrun-reader needs a path", file=sys.stderr)
            return 2
        try:
            s = read_surfacefieldvalue(argv[i + 1])
        except Refusal as e:
            print("REFUSE: %s" % e, file=sys.stderr)
            return 2
        # deliberately prints NO value -- the pre-freeze reader check L-286 names.
        print("parsed, %d rows, %d columns %r, region %r, %d faces"
              % (len(s["rows"]), len(s["cols"]), s["cols"], s["region"],
                 s["nfaces"]))
        return 0
    try:
        res = grade()
    except Refusal as e:
        print("REFUSE: %s" % e, file=sys.stderr)
        return 2
    report(res)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, default=str)
    print("grading JSON: %s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
