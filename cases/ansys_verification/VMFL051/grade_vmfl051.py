#!/usr/bin/env python3
"""VMFL051 comparator -- isentropic expansion of supersonic flow over a convex
corner.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 165-166.
Reference: John Anderson, *Modern Compressible Flow: With Historical
Perspective*, McGraw-Hill, 2002 (Prandtl-Meyer expansion, CLOSED-FORM ANALYTIC).

THIS FILE IS THE GRADING PATH.  It is committed BEFORE the pre-registration that
cites it by blob sha, and before any solver runs (CLAUDE.md rule 2;
VERIFICATION_CHARTER section 2d).  Nothing in it may change once the first graded
solve has started; instrumentation that is not on the grading path may be added
later only with a dated disclosure in RESULTS.md.

It REFUSES (exit 2) rather than degrades.  Every refusal names the clause.

NO THRESHOLD, BAND, REFERENCE VALUE OR PLANT CONSTANT IN THIS FILE IS SETTABLE
FROM THE COMMAND LINE.  Every one of them is a module-level constant fixed by the
commit that freezes this file.

The gated quantity is the POST-EXPANSION MACH NUMBER, read as the volume-average
of the `Ma` field over the frozen cell zone `gateZone`, at endTime, from the
`volFieldValue` function object.  The reader is built directly against the v2606
writer source, NOT a belief about it (the lesson of VMFL001 run 1 = N-AV4 /
L-286):

  * output path  postProcessing/<foName>/<startTime>/volFieldValue.dat
    -- src/OpenFOAM/db/functionObjects/writeFile/writeFile.C baseFileDir()
       (globalPath()/"postProcessing") and baseTimeDir() (= prefix_/timeName),
       with src/functionObjects/field/fieldValues/fieldValue/fieldValue.C:56
       passing the object NAME as prefix_ and the valueType "volFieldValue" as
       the base file name; startTime dir = 0.
  * header    "# Region : cellZone gateZone", "# Cells  : N", "# Volume : V"
              from src/finiteVolume/functionObjects/volRegion/volRegion.C:133-144
              then "# Time" followed by <tab>volAverage(<field>) per requested
              field, from volFieldValue.C:106-133.
  * data      writeCurrentTime, then `file() << tab << sresult` per field --
              volFieldValueTemplates.C:314 -- at the object's writePrecision
              (12, set in controlDict; writeFile::read honours "writePrecision").

Columns are located BY HEADER NAME, never by position.

    python3 grade_vmfl051.py                       # grade the run tree
    python3 grade_vmfl051.py --selftest            # all controls, zero compute
    python3 grade_vmfl051.py --dryrun-reader FILE  # parse only; prints no value
    python3 grade_vmfl051.py --verify-frozen SHA   # hash self against a commit
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
SELF_REL = "cases/ansys_verification/VMFL051/grade_vmfl051.py"
RUN_ROOT = os.path.join(REPO, "verification/runs/ansys_verification/VMFL051")
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL051.json")

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

# THE GATE IS AGAINST THIS.  Table .51.1, "Target" column.
MANUAL_TARGET = 3.2370
# Table .51.2 (Ansys CFX) prints the same target to one digit fewer.
MANUAL_TARGET_CFX = 3.237

# CONTEXT ONLY -- never the gate, never a band, never a reference.
ANSYS_CONTEXT = {"Fluent": 3.2316, "Fluent_ratio": 0.9980,
                 "CFX": 3.2354, "CFX_ratio": 0.9995}

# The manual's own stated accuracy goal, section 1.3, p. 5:
# "The goal for the test cases contained in this manual was to have results
#  accuracy within 3% of the target solution."
MANUAL_GOAL = 0.03

# ---------------------------------------------------------------------------
# 2.  THE GAS, DERIVED FROM THE MANUAL'S OWN Cp AND MOLECULAR WEIGHT
#
# OpenFOAM v2606's universal gas constant, which is what the SOLVER will use:
#   RR = 1e3 * NA * k
#      = 1e3 * 6.0221417930e+23 * 1.38065e-23
#      = 8314.47006650545  J/(kmol K)
# NA: src/OpenFOAM/global/constants/fundamental/fundamentalConstants.C:121
# k :  etc/controlDict:1125 (SICoeffs/physicoChemical)
# RR:  src/OpenFOAM/global/constants/thermodynamic/thermodynamicConstants.C:46
#      (RR = 1e3 * physicoChemical::R.value(), and R = NA*k)
#
# The CODATA-2018 value 8314.46261815324 differs by 9.0e-7 relative and moves
# M2 by 6.6e-7 in absolute Mach = 2.0e-5 % -- four orders of magnitude inside
# the gate.  Both are printed by --selftest.
# ---------------------------------------------------------------------------
RR_OPENFOAM = 1.0e3 * 6.0221417930e23 * 1.38065e-23   # 8314.47006650545
RR_CODATA_2018 = 8314.46261815324

R_SPECIFIC = RR_OPENFOAM / MANUAL_MW                  # 287.04239682750293
GAMMA = MANUAL_CP / (MANUAL_CP - R_SPECIFIC)          # 1.3990093734749485

# Frozen literals, so a later edit to the arithmetic above cannot silently move
# the reference.  --selftest asserts the computed values equal these.
GAMMA_FROZEN = 1.3990093734749485
R_SPECIFIC_FROZEN = 287.04239682750293
M2_EXACT_GAS_FROZEN = 3.2355411372251863      # gamma from the manual's own gas
M2_EXACT_GAMMA14_FROZEN = 3.2368431056638845  # the same solve at gamma = 1.4
NU1_GAS_DEG_FROZEN = 39.160263203801104
NU1_GAMMA14_DEG_FROZEN = 39.1235638278973
U1_FROZEN = 867.7287202948199                 # m/s, = M1*sqrt(gamma*R*T1)

# Anderson, Modern Compressible Flow, Appendix C (gamma = 1.4), for --selftest.
PM_TABLE_GAMMA14 = {2.0: 26.3798, 3.0: 49.7573, 1.5: 11.9052, 5.0: 76.9202}
PM_TABLE_TOL = 5e-5   # degrees; the table is printed to 4 decimals

# ---------------------------------------------------------------------------
# 3.  THE GATE AND THE DIAGNOSTIC BANDS -- derived in PREREGISTRATION.md sec. 3
# ---------------------------------------------------------------------------
TOL_GATE = 0.005          # 0.5 % of MANUAL_TARGET.  THE GATE.
TOL_DIAG_EXACT = 0.0025   # 0.25 % of M2_EXACT_GAS.  DIAGNOSTIC, never the gate.

# ---------------------------------------------------------------------------
# 4.  ROACHE (CLAUDE.md rule 5).  Thresholds written down before any run.
# ---------------------------------------------------------------------------
FS = 1.25            # Roache factor of safety, three-grid
RATIO = 2.0          # refinement ratio, both directions, exact by construction
EPS_ABS = 1e-12      # Mach: a level-to-level difference below this is zero
STAG_TOL = 1e-3      # |R - 1| <= STAG_TOL  =>  STAGNANT

# ---------------------------------------------------------------------------
# 5.  COMPLETION (CLAUDE.md rule 4) and the plateau clause
# ---------------------------------------------------------------------------
ENDTIME = 7.0e-3         # s, IDENTICAL at every level (physical time)
WRITEINTERVAL = 3.5e-3   # s
MAXDELTAT = 1.0e-5       # s, the declared C3 tolerance
REQUIRED_FIELDS = ("T", "U", "p", "rho", "Ma")

PLATEAU_FRAC = 0.20      # last 20 % of the gate time series
PLATEAU_TOL_MA = 1.0e-3  # peak-to-peak in Mach units = 3.1e-4 relative,
                         # 16x tighter than the 0.5 % gate

# The inner-zone consistency clause (DECLARED, and it can only produce
# NOT A RESULT, never a PASS -- CLAUDE.md rule 5's one-way street).
ZONE_CONSISTENCY_TOL = 1.0e-2

# ---------------------------------------------------------------------------
# 6.  PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  None is optional; none can be
#     skipped by a flag.  The comparator EXITS 2 if any fails.
# ---------------------------------------------------------------------------
PLANT_DAT = 1.234e-03      # Mach, planted into a COPY of volFieldValue.dat
PLANT_DAT_TOL = 1e-12
PLANT_FIELD = 7.77e-02     # Mach, planted into a COPY of the endTime Ma field
PLANT_FIELD_TOL = 1e-9
PLANT_NU_DEG = 5.0         # degrees, planted into the Prandtl-Meyer solve

# ---------------------------------------------------------------------------
# 7.  THE MESH FAMILY.  Refinement ratio 2 in BOTH directions by construction:
#     every level doubles nxA, nxB and ny, so h halves exactly and RATIO is not
#     inferred from a cell count.
# ---------------------------------------------------------------------------
LEVELS = (  # name, nxA (upstream block), nxB (downstream block), ny, cells
    ("L1_120x52",   24,  96,  52,   6240),
    ("L2_240x104",  48, 192, 104,  24960),
    ("L3_480x208",  96, 384, 208,  99840),
)

GATE_FO = "gateMach"        # cellZone gateZone      -- THE GATE
DIAG_FO = "gateMachInner"   # cellZone gateZoneInner -- DIAGNOSTIC ONLY

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
            "BLOCKED", "PENDING")


# ===========================================================================
# refusal
# ===========================================================================
class Refusal(Exception):
    pass


def refuse(clause, msg):
    raise Refusal("%s :: %s" % (clause, msg))


# ===========================================================================
# The Prandtl-Meyer reference -- closed form, no CFD input of any kind
# ===========================================================================
def nu_rad(M, g):
    """Prandtl-Meyer function, radians.  M >= 1."""
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
    """Bracketed bisection on nu(M) - nu_target.  nu is strictly increasing in
    M for M > 1, so the bracket is guaranteed and the root is unique."""
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


def isentropic_M_from_p(p, p0, g):
    return math.sqrt(2.0 / (g - 1.0) * ((p0 / p) ** ((g - 1.0) / g) - 1.0))


def isentropic_M_from_T(T, T0, g):
    return math.sqrt(2.0 / (g - 1.0) * (T0 / T - 1.0))


# The frozen inlet stagnation state -- computed here from the manual's own
# inlet condition, used only for the two DIAGNOSTIC Mach re-derivations.
T0_INLET = MANUAL_T1 * (1.0 + 0.5 * (GAMMA - 1.0) * MANUAL_M1 ** 2)
P0_INLET = MANUAL_P1 * (T0_INLET / MANUAL_T1) ** (GAMMA / (GAMMA - 1.0))


# ===========================================================================
# READER 1 -- the volFieldValue.dat time series (THE GATED INSTRUMENT)
# ===========================================================================
def read_volfieldvalue(path):
    """Parse a v2606 volFieldValue.dat.  Columns are found BY HEADER NAME."""
    if not os.path.isfile(path):
        refuse("READER", "no such file: %s" % path)
    region = None
    ncells = None
    volume = None
    cols = None
    rows = []
    with open(path, "r") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                body = line.lstrip()[1:].strip()
                m = re.match(r"^Region\s*:\s*(.+)$", body)
                if m:
                    region = m.group(1).strip()
                    continue
                m = re.match(r"^Cells\s*:\s*(\d+)$", body)
                if m:
                    ncells = int(m.group(1))
                    continue
                m = re.match(r"^Volume\s*:\s*(\S+)$", body)
                if m:
                    volume = float(m.group(1))
                    continue
                toks = body.split()
                if toks and toks[0] == "Time":
                    cols = toks           # ["Time", "volAverage(Ma)", ...]
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
    if ncells is None:
        refuse("READER", "no '# Cells' header line in %s -- the region header "
                         "is what proves the zone was found" % path)
    if ncells <= 0:
        refuse("READER", "the function object reports %d cells in its region "
                         "(%s) -- an EMPTY sampling zone reads as a number and "
                         "must never be graded" % (ncells, path))
    return {"path": path, "region": region, "ncells": ncells,
            "volume": volume, "cols": cols, "rows": rows}


def column(series, name):
    if name not in series["cols"]:
        refuse("READER", "column %r not in header %r of %s"
               % (name, series["cols"], series["path"]))
    return series["cols"].index(name)


def value_at_endtime(series, name, endtime, tol):
    j = column(series, name)
    best = None
    for vals in series["rows"]:
        if abs(vals[0] - endtime) <= tol:
            best = vals
    if best is None:
        refuse("C3", "no row within %g s of endTime %g in %s (last time %g)"
               % (tol, endtime, series["path"], series["rows"][-1][0]))
    return best[j], best[0]


def plateau_ptp(series, name, frac):
    j = column(series, name)
    n = len(series["rows"])
    k = max(2, int(round(frac * n)))
    tail = [r[j] for r in series["rows"][-k:]]
    return max(tail) - min(tail), k, n


# ===========================================================================
# READER 2 -- an OpenFOAM ascii volScalarField (used by control PZ-2)
# ===========================================================================
_UNIFORM_RE = re.compile(r"internalField\s+uniform\s+([-+0-9.eE]+)\s*;")
_NONUNIFORM_RE = re.compile(
    r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\s*\(", re.M)


def read_foam_scalar_field(path):
    """Return (values, kind) where kind is 'uniform' or 'nonuniform'."""
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


def plant_into_scalar_field(src, dst, delta):
    """Write a copy of an ascii volScalarField with `delta` added to every
    internal value.  The RUN TREE IS NEVER TOUCHED -- only this copy."""
    with open(src, "r") as fh:
        text = fh.read()
    m = _NONUNIFORM_RE.search(text)
    if not m:
        refuse("PZ-2", "%s is not a nonuniform list -- cannot plant" % src)
    n = int(m.group(1))
    start = m.end()
    end = text.find(")", start)
    body = text[start:end].split()
    shifted = "\n".join("%.16g" % (float(t) + delta) for t in body)
    out = text[:start] + "\n" + shifted + "\n" + text[end:]
    with open(dst, "w") as fh:
        fh.write(out)
    return n


def plant_into_dat(src, dst, colname, delta):
    """Write a copy of a volFieldValue.dat with `delta` added to one column on
    every data row.  The RUN TREE IS NEVER TOUCHED -- only this copy."""
    cols = None
    out = []
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
            toks[j] = "%.16g" % (float(toks[j]) + delta)
            out.append("\t".join(toks))
    with open(dst, "w") as fh:
        fh.write("\n".join(out) + "\n")


# ===========================================================================
# Roache triple (CLAUDE.md rule 5).  Semantics identical to the team's
# VMFL005 comparator; thresholds fixed above.
# ===========================================================================
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine        # medium - fine
    d32 = f_coarse - f_med      # coarse - medium
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
# Strict completion (CLAUDE.md rule 4), with the two departures DECLARED on the
# face of PREREGISTRATION.md section 8 and repeated here.
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
    """Every clause is read off disk.  Any failure REFUSES; a partial run is
    never graded."""
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
    # DECLARED DEPARTURE 1: rhoCentralFoam runs adjustTimeStep, so the rule's
    # literal "last time == endTime" is replaced by |t_last - endTime| <=
    # maxDeltaT AND the log's own final "Time =" agreeing with the directory.
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

    # DECLARED DEPARTURE 2: the rule's literal "ExecutionTime count == endTime"
    # is a STEADY-ITERATION clause (one iteration = one time unit).  This solver
    # is transient with an adaptive step, so that count can never be endTime.
    # The invariant the clause protects -- the log is not truncated mid-step --
    # is checked directly: one ExecutionTime line per Time line.
    n_exec = sum(1 for l in log_lines if l.startswith("ExecutionTime = "))
    n_time = len(log_times)
    if n_exec != n_time or n_exec == 0:
        refuse("C5", "log step integrity: %d ExecutionTime lines against %d "
                     "Time lines in %s" % (n_exec, n_time, log))

    # C6 AGE GUARD, STRICTER than the rule: the rule dates the run from 0/T;
    # this dates it from the LATEST mtime anywhere in the case's own 0/.
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
# One level -> the gate value and its diagnostics
# ===========================================================================
def read_level(level_dir):
    comp = completion_check(level_dir)

    gate_dat = os.path.join(level_dir, "postProcessing", GATE_FO, "0",
                            "volFieldValue.dat")
    diag_dat = os.path.join(level_dir, "postProcessing", DIAG_FO, "0",
                            "volFieldValue.dat")

    gate = read_volfieldvalue(gate_dat)
    diag = read_volfieldvalue(diag_dat)

    ma, t_row = value_at_endtime(gate, "volAverage(Ma)", ENDTIME, MAXDELTAT)
    pa, _ = value_at_endtime(gate, "volAverage(p)", ENDTIME, MAXDELTAT)
    ta, _ = value_at_endtime(gate, "volAverage(T)", ENDTIME, MAXDELTAT)
    ma_in, _ = value_at_endtime(diag, "volAverage(Ma)", ENDTIME, MAXDELTAT)

    ptp, k, n = plateau_ptp(gate, "volAverage(Ma)", PLATEAU_FRAC)

    return {
        "completion": comp,
        "gate_dat": gate_dat, "diag_dat": diag_dat,
        "gate_ncells": gate["ncells"], "gate_volume": gate["volume"],
        "gate_region": gate["region"],
        "diag_ncells": diag["ncells"], "diag_region": diag["region"],
        "Ma": ma, "p": pa, "T": ta, "Ma_inner": ma_in,
        "t_row": t_row,
        "plateau_ptp": ptp, "plateau_rows": k, "series_rows": n,
        "M_from_p": isentropic_M_from_p(pa, P0_INLET, GAMMA),
        "M_from_T": isentropic_M_from_T(ta, T0_INLET, GAMMA),
        "endtime_dir": comp["endtime_dir"],
    }


# ===========================================================================
# PLANTED-ZERO CONTROLS (CLAUDE.md rule 3) -- run against the REAL artifacts
# ===========================================================================
def control_pz1(level_dir):
    """Plant into a COPY of the gated .dat and require the reader to see it."""
    src = os.path.join(level_dir, "postProcessing", GATE_FO, "0",
                       "volFieldValue.dat")
    base, _ = value_at_endtime(read_volfieldvalue(src), "volAverage(Ma)",
                               ENDTIME, MAXDELTAT)
    tmp = tempfile.mkdtemp(prefix="vmfl051_pz1_")
    try:
        # NEGATIVE ARM: an unplanted copy must show NO signal.
        flat = os.path.join(tmp, "flat.dat")
        shutil.copy2(src, flat)
        v_flat, _ = value_at_endtime(read_volfieldvalue(flat),
                                     "volAverage(Ma)", ENDTIME, MAXDELTAT)
        if abs(v_flat - base) > PLANT_DAT_TOL:
            refuse("PZ-1", "the unplanted copy already differs by %g -- the "
                           "reader is not deterministic" % (v_flat - base))
        # POSITIVE ARM: a planted copy must move by exactly the plant.
        planted = os.path.join(tmp, "planted.dat")
        plant_into_dat(src, planted, "volAverage(Ma)", PLANT_DAT)
        v_planted, _ = value_at_endtime(read_volfieldvalue(planted),
                                        "volAverage(Ma)", ENDTIME, MAXDELTAT)
        seen = v_planted - base
        if abs(seen - PLANT_DAT) > PLANT_DAT_TOL:
            refuse("PZ-1", "planted %g into a copy of %s, read back %g "
                           "(error %g > %g) -- THE READER CANNOT SEE A NON-ZERO "
                           "AND HAS THEREFORE PRODUCED NO NUMBER"
                   % (PLANT_DAT, src, seen, seen - PLANT_DAT, PLANT_DAT_TOL))
        return {"plant": PLANT_DAT, "seen": seen, "base": base, "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz2(level_dir, endtime_dir):
    """Plant into a COPY of the Ma FIELD ITSELF at endTime and require the
    field reader to see it.  This is the control that demonstrates the
    comparator can read a non-zero out of the Mach field on disk."""
    src = os.path.join(level_dir, endtime_dir, "Ma")
    vals, kind = read_foam_scalar_field(src)
    if kind != "nonuniform":
        refuse("PZ-2", "the Ma field at endTime in %s is '%s' -- a uniform Mach "
                       "field after an expansion fan is not a solution"
               % (level_dir, kind))
    mean0 = sum(vals) / len(vals)
    tmp = tempfile.mkdtemp(prefix="vmfl051_pz2_")
    try:
        flat = os.path.join(tmp, "Ma_flat")
        shutil.copy2(src, flat)
        v_flat, _ = read_foam_scalar_field(flat)
        if abs(sum(v_flat) / len(v_flat) - mean0) > PLANT_FIELD_TOL:
            refuse("PZ-2", "the unplanted field copy already differs -- the "
                           "field reader is not deterministic")
        planted = os.path.join(tmp, "Ma_planted")
        n = plant_into_scalar_field(src, planted, PLANT_FIELD)
        v_p, _ = read_foam_scalar_field(planted)
        if len(v_p) != n or len(v_p) != len(vals):
            refuse("PZ-2", "planted copy has %d entries, original %d"
                   % (len(v_p), len(vals)))
        seen = sum(v_p) / len(v_p) - mean0
        if abs(seen - PLANT_FIELD) > PLANT_FIELD_TOL:
            refuse("PZ-2", "planted %g into a copy of the Ma field at %s, read "
                           "back %g (error %g) -- THE FIELD READER CANNOT SEE A "
                           "NON-ZERO" % (PLANT_FIELD, src, seen, seen - PLANT_FIELD))
        return {"plant": PLANT_FIELD, "seen": seen, "n_cells": len(vals),
                "field_mean": mean0, "field_min": min(vals),
                "field_max": max(vals), "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz3():
    """Plant into the REFERENCE COMPUTATION.  A root finder that returned a
    constant would sail through every deviation test in this file."""
    M2 = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, GAMMA)
    ident = nu_deg(M2, GAMMA) - nu_deg(MANUAL_M1, GAMMA)
    if abs(ident - TURN_DEG) > 1e-9:
        refuse("PZ-3", "the solved M2 does not satisfy its own defining "
                       "identity: nu(M2) - nu(M1) = %.12f deg, expected %g"
               % (ident, TURN_DEG))
    # planted arm: a DIFFERENT turn must give a DIFFERENT, self-consistent root
    M2p = M2_prandtl_meyer(MANUAL_M1, TURN_DEG + PLANT_NU_DEG, GAMMA)
    if abs(M2p - M2) < 1e-6:
        refuse("PZ-3", "a %g deg change of turn angle moved M2 by %g -- the "
                       "root finder is returning a constant"
               % (PLANT_NU_DEG, M2p - M2))
    identp = nu_deg(M2p, GAMMA) - nu_deg(MANUAL_M1, GAMMA)
    if abs(identp - (TURN_DEG + PLANT_NU_DEG)) > 1e-9:
        refuse("PZ-3", "the planted solve is not self-consistent: %.12f deg"
               % identp)
    return {"M2": M2, "identity_deg": ident, "plant_deg": PLANT_NU_DEG,
            "M2_planted": M2p, "delta": M2p - M2, "fired": True}


# ===========================================================================
# GRADE
# ===========================================================================
def grade():
    M2_exact = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, GAMMA)
    if abs(M2_exact - M2_EXACT_GAS_FROZEN) > 1e-12:
        refuse("REFERENCE", "the in-module Prandtl-Meyer solve gives %.16f but "
                            "the frozen literal is %.16f -- the reference has "
                            "drifted" % (M2_exact, M2_EXACT_GAS_FROZEN))

    controls = {"PZ-3_reference": control_pz3()}

    per_level = {}
    for name, nxa, nxb, ny, cells in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        if not os.path.isdir(d):
            refuse("C0", "level directory %s does not exist -- nothing to grade" % d)
        per_level[name] = read_level(d)
        per_level[name]["cells"] = cells
        per_level[name]["nxA"], per_level[name]["nxB"], per_level[name]["ny"] = \
            nxa, nxb, ny

    finest = LEVELS[-1][0]
    controls["PZ-1_dat_reader"] = control_pz1(os.path.join(RUN_ROOT, finest))
    controls["PZ-2_field_reader"] = control_pz2(
        os.path.join(RUN_ROOT, finest), per_level[finest]["endtime_dir"])

    vals = [per_level[n]["Ma"] for n, _, _, _, _ in LEVELS]
    triple = roache(vals[0], vals[1], vals[2])

    M_lab = vals[-1]
    dev_target = (M_lab - MANUAL_TARGET) / MANUAL_TARGET
    dev_exact = (M_lab - M2_exact) / M2_exact

    # ---- CLAUDE.md rule 5, IN ITS STATED ORDER -------------------------
    verdict = None
    why = None

    # step 1: any level not converged / not plateaued -> NOT A RESULT
    for name, _, _, _, _ in LEVELS:
        L = per_level[name]
        if L["plateau_ptp"] > PLATEAU_TOL_MA:
            verdict = "NOT A RESULT"
            why = ("level %s has not plateaued: peak-to-peak of the gate Mach "
                   "series over its last %d of %d rows is %.3e > %.3e "
                   "(rule 5 step 1)"
                   % (name, L["plateau_rows"], L["series_rows"],
                      L["plateau_ptp"], PLATEAU_TOL_MA))
            break
    # the declared inner-zone consistency clause -- can only produce
    # NOT A RESULT, never a PASS
    if verdict is None:
        L = per_level[finest]
        zc = abs(L["Ma"] - L["Ma_inner"]) / abs(L["Ma"])
        if zc > ZONE_CONSISTENCY_TOL:
            verdict = "NOT A RESULT"
            why = ("the gate zone and its strictly-inner diagnostic zone "
                   "disagree by %.3e > %.3e at %s -- the gate zone is being "
                   "contaminated from an edge"
                   % (zc, ZONE_CONSISTENCY_TOL, finest))

    # step 2: triple not CONVERGING -> NOT A RESULT
    if verdict is None and triple["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = "grid triple is %s, not CONVERGING (rule 5 step 2)" % triple["state"]

    # step 3: CONVERGING -> PASS inside the band, else GATE FAIL
    if verdict is None:
        if abs(dev_target) <= TOL_GATE:
            verdict = "PASS"
            why = ("|M_lab - target| / target = %.6f %% <= %.4f %% "
                   "(rule 5 step 3)" % (100 * abs(dev_target), 100 * TOL_GATE))
        else:
            verdict = "GATE FAIL"
            why = ("|M_lab - target| / target = %.6f %% > %.4f %%"
                   % (100 * abs(dev_target), 100 * TOL_GATE))

    assert verdict in VERDICTS

    result = {
        "case": "VMFL051",
        "manual_page": MANUAL_PAGE,
        "verdict": verdict,
        "why": why,
        "gate": {"reference": MANUAL_TARGET,
                 "reference_class": "manual printed target, Table .51.1 "
                                    "(analytic Prandtl-Meyer)",
                 "tolerance_rel": TOL_GATE,
                 "lab_value": M_lab,
                 "deviation_rel": dev_target,
                 "deviation_pct": 100 * dev_target},
        "diagnostic_exact": {"reference": M2_exact,
                             "reference_class": "closed-form Prandtl-Meyer for "
                                                "the manual's own gas, "
                                                "gamma = %.16f" % GAMMA,
                             "tolerance_rel": TOL_DIAG_EXACT,
                             "deviation_rel": dev_exact,
                             "deviation_pct": 100 * dev_exact,
                             "inside": abs(dev_exact) <= TOL_DIAG_EXACT},
        "gamma": GAMMA, "R_specific": R_SPECIFIC, "RR_openfoam": RR_OPENFOAM,
        "M2_exact_gamma14": M2_EXACT_GAMMA14_FROZEN,
        "ansys_context_never_the_gate": ANSYS_CONTEXT,
        "triple": triple,
        "levels": per_level,
        "controls": controls,
        "endTime": ENDTIME,
        "plateau_tol_Ma": PLATEAU_TOL_MA,
    }
    return result


def report(res):
    P = print
    P("=" * 78)
    P("VMFL051 -- Isentropic Expansion of Supersonic Flow Over a Convex Corner")
    P("Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. %s"
      % res["manual_page"])
    P("=" * 78)
    P("")
    P("gamma  = %.16f   (from the manual's own Cp = %g and MW = %g;"
      % (res["gamma"], MANUAL_CP, MANUAL_MW))
    P("                              NOT 1.4 -- see PREREGISTRATION.md sec. 2)")
    P("R      = %.14f J/kg-K" % res["R_specific"])
    P("")
    P("--- controls (CLAUDE.md rule 3) ---")
    for k, v in res["controls"].items():
        P("  %-20s FIRED  %s" % (k, {kk: ("%.6g" % vv if isinstance(vv, float)
                                          else vv)
                                     for kk, vv in v.items() if kk != "fired"}))
    P("")
    P("--- levels ---")
    for name, _, _, _, cells in LEVELS:
        L = res["levels"][name]
        P("  %-14s cells %6d  zone %5d cells  Ma = %.10f  "
          "(inner %.10f)  plateau ptp %.3e over %d/%d rows"
          % (name, cells, L["gate_ncells"], L["Ma"], L["Ma_inner"],
             L["plateau_ptp"], L["plateau_rows"], L["series_rows"]))
        P("  %-14s   diagnostics: M from p = %.10f, M from T = %.10f, "
          "<p> = %.4f Pa, <T> = %.4f K"
          % ("", L["M_from_p"], L["M_from_T"], L["p"], L["T"]))
    P("")
    t = res["triple"]
    P("--- Roache triple on the post-expansion Mach number, r = %.1f, Fs = %.2f ---"
      % (t["ratio"], t["fs"]))
    P("  coarse %.10f   medium %.10f   fine %.10f" %
      (t["f_coarse"], t["f_med"], t["f_fine"]))
    P("  d32 (coarse-medium) = %.6e   d21 (medium-fine) = %.6e" %
      (t["d32"], t["d21"]))
    P("  R = %s   observed order p = %s   state = %s" %
      ("%.6f" % t["R"] if t["R"] is not None else "n/a",
       "%.4f" % t["p"] if t["p"] is not None else "n/a", t["state"]))
    if t["state"] == "CONVERGING":
        P("  GCI(fine) = %.4f %%   Richardson extrapolation = %.10f"
          % (100 * t["gci_fine"], t["f_extrapolated"]))
    else:
        P("  no GCI quoted -- the three values are not monotone convergent")
    P("")
    g = res["gate"]
    d = res["diagnostic_exact"]
    P("--- THE GATE (manual printed target, Table .51.1) ---")
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
    P("  exact at gamma = 1.4: %.16f" % res["M2_exact_gamma14"])
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
# --verify-frozen : this file must be byte-identical to the committed blob
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
    print("FREEZE VERIFIED: grade_vmfl051.py is byte-identical to %s:%s "
          "(sha256 %s)" % (commitish, SELF_REL,
                           hashlib.sha256(mine).hexdigest()[:16]))
    return 0


# ===========================================================================
# --selftest : every control and every classifier arm, with ZERO solver compute
# ===========================================================================
FIXTURE = """\
# Region : cellZone gateZone
# Cells  : 116
# Volume : 3.40820048026e-05
# Time\tvolAverage(Ma)\tvolAverage(p)\tvolAverage(T)
0.001\t3.2\t67000\t219
0.002\t3.23\t66500\t218.4
0.003\t3.2354\t66415\t218.25
0.004\t3.23551\t66414.3\t218.2479
0.005\t3.235539\t66414.19\t218.24781
0.006\t3.2355407\t66414.178\t218.247757
0.007\t3.2355411\t66414.1771\t218.2477561
"""

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

    print("VMFL051 comparator selftest -- no solver, no run tree touched")
    print("")
    print("[A] the gas, from the manual's own Cp and molecular weight")
    check("RR (OpenFOAM v2606 NA*k*1e3)", abs(RR_OPENFOAM - 8314.47006650545) < 1e-8,
          "= %.11f" % RR_OPENFOAM)
    check("R specific", abs(R_SPECIFIC - R_SPECIFIC_FROZEN) < 1e-10,
          "= %.14f J/kg-K" % R_SPECIFIC)
    check("gamma NOT 1.4", abs(GAMMA - GAMMA_FROZEN) < 1e-14 and abs(GAMMA - 1.4) > 1e-4,
          "= %.16f" % GAMMA)
    check("U1 from the manual's M1, T1", abs(MANUAL_M1 * math.sqrt(
        GAMMA * R_SPECIFIC * MANUAL_T1) - U1_FROZEN) < 1e-9,
        "= %.14f m/s" % (MANUAL_M1 * math.sqrt(GAMMA * R_SPECIFIC * MANUAL_T1)))
    rr_c = RR_CODATA_2018 / MANUAL_MW
    g_c = MANUAL_CP / (MANUAL_CP - rr_c)
    m2_c = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, g_c)
    check("CODATA-2018 variant is negligible",
          abs(m2_c - M2_EXACT_GAS_FROZEN) < 1e-5,
          "delta M2 = %.3e (%.2e %% -- gate is %.1f %%)"
          % (m2_c - M2_EXACT_GAS_FROZEN,
             100 * abs(m2_c - M2_EXACT_GAS_FROZEN) / M2_EXACT_GAS_FROZEN,
             100 * TOL_GATE))

    print("")
    print("[B] the Prandtl-Meyer function against Anderson's Appendix C (gamma=1.4)")
    for M, tab in sorted(PM_TABLE_GAMMA14.items()):
        got = nu_deg(M, 1.4)
        check("nu(%.1f) = %.4f deg" % (M, tab), abs(got - tab) <= PM_TABLE_TOL,
              "computed %.6f" % got)
    check("nu(1) = 0", abs(nu_deg(1.0, 1.4)) < 1e-12)
    check("nu is strictly increasing",
          all(nu_rad(m, 1.4) < nu_rad(m + 0.05, 1.4)
              for m in [1.1 + 0.1 * i for i in range(40)]))

    print("")
    print("[C] the frozen reference values")
    m2 = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, GAMMA)
    check("nu(2.5) for the manual's gas",
          abs(nu_deg(MANUAL_M1, GAMMA) - NU1_GAS_DEG_FROZEN) < 1e-10,
          "= %.12f deg" % nu_deg(MANUAL_M1, GAMMA))
    check("nu(2.5) at gamma = 1.4",
          abs(nu_deg(MANUAL_M1, 1.4) - NU1_GAMMA14_DEG_FROZEN) < 1e-10,
          "= %.12f deg" % nu_deg(MANUAL_M1, 1.4))
    check("M2 exact, manual's gas", abs(m2 - M2_EXACT_GAS_FROZEN) < 1e-12,
          "= %.16f" % m2)
    m2_14 = M2_prandtl_meyer(MANUAL_M1, TURN_DEG, 1.4)
    check("M2 exact, gamma = 1.4", abs(m2_14 - M2_EXACT_GAMMA14_FROZEN) < 1e-12,
          "= %.16f" % m2_14)
    check("the manual's printed 3.2370 is NOT the exact gamma=1.4 value",
          abs(MANUAL_TARGET - m2_14) > 1e-5,
          "difference %.6e (%.5f %%)"
          % (MANUAL_TARGET - m2_14, 100 * (MANUAL_TARGET - m2_14) / MANUAL_TARGET))
    check("the manual's gas sits %.5f %% below the printed target"
          % (100 * (m2 - MANUAL_TARGET) / MANUAL_TARGET),
          abs((m2 - MANUAL_TARGET) / MANUAL_TARGET) < TOL_GATE,
          "-- the declared gas-model bias fits inside the gate")

    print("")
    print("[D] the reader, on the REAL volFieldValue.dat format")
    tmp = tempfile.mkdtemp(prefix="vmfl051_selftest_")
    try:
        f = os.path.join(tmp, "volFieldValue.dat")
        open(f, "w").write(FIXTURE)
        s = read_volfieldvalue(f)
        check("region header parsed", s["region"] == "cellZone gateZone", s["region"])
        check("cell count parsed", s["ncells"] == 116, str(s["ncells"]))
        check("columns located by NAME",
              s["cols"] == ["Time", "volAverage(Ma)", "volAverage(p)",
                            "volAverage(T)"], str(s["cols"]))
        v, t = value_at_endtime(s, "volAverage(Ma)", ENDTIME, MAXDELTAT)
        check("endTime row found", abs(t - ENDTIME) < 1e-12 and abs(v - 3.2355411) < 1e-12,
              "Ma = %.7f at t = %g" % (v, t))
        ptp, k, n = plateau_ptp(s, "volAverage(Ma)", PLATEAU_FRAC)
        check("plateau over the last 20 %", k == 1 or k >= 2, "%d of %d rows, ptp %.3e" % (k, n, ptp))

        # refusal arms
        f2 = os.path.join(tmp, "short.dat")
        open(f2, "w").write(FIXTURE.replace("0.007\t3.2355411\t66414.1771\t218.2477561",
                                            "0.007\t3.2355411"))
        try:
            read_volfieldvalue(f2)
            check("a short data row REFUSES", False)
        except Refusal as e:
            check("a short data row REFUSES", "READER" in str(e))
        f3 = os.path.join(tmp, "nocells.dat")
        open(f3, "w").write(FIXTURE.replace("# Cells  : 116", "# Cells  : 0"))
        try:
            read_volfieldvalue(f3)
            check("an EMPTY sampling zone REFUSES", False)
        except Refusal as e:
            check("an EMPTY sampling zone REFUSES", "EMPTY sampling zone" in str(e))

        print("")
        print("[E] planted-zero, .dat reader (PZ-1), both arms")
        base, _ = value_at_endtime(read_volfieldvalue(f), "volAverage(Ma)",
                                   ENDTIME, MAXDELTAT)
        flat = os.path.join(tmp, "flat.dat")
        shutil.copy2(f, flat)
        vf, _ = value_at_endtime(read_volfieldvalue(flat), "volAverage(Ma)",
                                 ENDTIME, MAXDELTAT)
        check("unplanted copy shows NO signal", abs(vf - base) < PLANT_DAT_TOL,
              "delta %.3e" % (vf - base))
        pl = os.path.join(tmp, "planted.dat")
        plant_into_dat(f, pl, "volAverage(Ma)", PLANT_DAT)
        vp, _ = value_at_endtime(read_volfieldvalue(pl), "volAverage(Ma)",
                                 ENDTIME, MAXDELTAT)
        check("planted copy shows EXACTLY the plant",
              abs((vp - base) - PLANT_DAT) < PLANT_DAT_TOL,
              "planted %.6g, saw %.6g" % (PLANT_DAT, vp - base))

        print("")
        print("[F] planted-zero, Ma FIELD reader (PZ-2), both arms")
        ff = os.path.join(tmp, "Ma")
        open(ff, "w").write(FIELD_FIXTURE)
        vals, kind = read_foam_scalar_field(ff)
        check("nonuniform field parsed", kind == "nonuniform" and len(vals) == 6,
              "%d values, mean %.6f" % (len(vals), sum(vals) / len(vals)))
        m0 = sum(vals) / len(vals)
        ffl = os.path.join(tmp, "Ma_flat")
        shutil.copy2(ff, ffl)
        v2, _ = read_foam_scalar_field(ffl)
        check("unplanted field copy shows NO signal",
              abs(sum(v2) / len(v2) - m0) < PLANT_FIELD_TOL)
        ffp = os.path.join(tmp, "Ma_planted")
        n = plant_into_scalar_field(ff, ffp, PLANT_FIELD)
        v3, _ = read_foam_scalar_field(ffp)
        check("planted field copy shows EXACTLY the plant",
              n == 6 and abs((sum(v3) / len(v3) - m0) - PLANT_FIELD) < PLANT_FIELD_TOL,
              "planted %.6g, saw %.6g" % (PLANT_FIELD, sum(v3) / len(v3) - m0))
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
    t1 = roache(1.0 + 0.04, 1.0 + 0.02, 1.0 + 0.01)      # first order
    check("first-order family -> CONVERGING, p ~ 1",
          t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9,
          "p = %.6f" % t1["p"])
    t2 = roache(1.0 + 0.04, 1.0 + 0.01, 1.0 + 0.0025)    # second order
    check("second-order family -> CONVERGING, p ~ 2",
          t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9,
          "p = %.6f, GCI %.4f %%" % (t2["p"], 100 * t2["gci_fine"]))
    check("divergent family -> DIVERGENT",
          roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory family -> OSCILLATORY",
          roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("equal-step family -> STAGNANT",
          roache(1.0, 1.1, 1.2)["state"] == "STAGNANT")
    check("identical values -> EXACT",
          roache(2.5, 2.5, 2.5)["state"] == "EXACT")
    check("no GCI is quoted for a non-CONVERGING triple",
          roache(1.0, 1.2, 1.0)["gci_fine"] is None)

    print("")
    print("[I] the gate, both arms")
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
          "%.3f %% -- this is what the manual's own 'incompressible' "
          "Analysis Assumptions sentence would give"
          % (100 * (MANUAL_M1 - MANUAL_TARGET) / MANUAL_TARGET))
    check("Ansys Fluent's own reported value would PASS this gate",
          abs((ANSYS_CONTEXT["Fluent"] - MANUAL_TARGET) / MANUAL_TARGET) <= TOL_GATE,
          "%.4f %% -- the gate is not a formality: 2.5x Fluent's deviation fails it"
          % (100 * (ANSYS_CONTEXT["Fluent"] - MANUAL_TARGET) / MANUAL_TARGET))

    print("")
    print("[J] the verdict vocabulary")
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
            s = read_volfieldvalue(argv[i + 1])
        except Refusal as e:
            print("REFUSE: %s" % e, file=sys.stderr)
            return 2
        # deliberately prints NO value -- this is the pre-freeze reader check
        # L-286 names, and it must not be able to leak the answer.
        print("parsed, %d rows, %d columns %r, region %r, %d cells"
              % (len(s["rows"]), len(s["cols"]), s["cols"], s["region"],
                 s["ncells"]))
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
