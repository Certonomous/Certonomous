#!/usr/bin/env python3
"""VMFL045 comparator -- oblique shock over a 15 deg inclined ramp.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 153-154.
Reference: F. M. White, Fluid Mechanics, 3rd ed., McGraw-Hill, 1994, 560-567
(oblique-shock theory, CLOSED-FORM ANALYTIC via the theta-beta-M relation and
the normal-shock jump relations applied to the shock-normal Mach component).

THIS FILE IS THE GRADING PATH.  It is committed BEFORE the pre-registration that
cites it by blob sha, and before any solver runs (CLAUDE.md rule 2;
VERIFICATION_CHARTER section 2d).  Nothing in it may change once the first graded
solve has started; instrumentation not on the grading path may be added later
only with a dated disclosure in RESULTS.md.

It REFUSES (exit 2) rather than degrades.  Every refusal names the clause.

NO THRESHOLD, BAND, REFERENCE VALUE OR PLANT CONSTANT IN THIS FILE IS SETTABLE
FROM THE COMMAND LINE.  Every one of them is a module-level constant fixed by the
commit that freezes this file.

The GATED quantity is the POST-SHOCK MACH NUMBER, read as the volume-average of
the `Ma` field over the frozen cell zone `gateZone` at endTime, from the
`volFieldValue` function object.  The reader is built directly against the v2606
writer source, NOT a belief about it (the lesson of VMFL001 run 1 = N-AV4 /
L-286):

  * output path  postProcessing/<foName>/<startTime>/volFieldValue.dat
    -- writeFile.C baseFileDir() (globalPath()/"postProcessing") and
       baseTimeDir() (= prefix_/timeName), with fieldValue.C:56 passing the
       object NAME as prefix_ and the valueType "volFieldValue" as the base file
       name; startTime dir = 0.
  * header    "# Region : cellZone gateZone", "# Cells  : N", "# Volume : V"
              from volRegion.C:133-144, then "# Time" + <tab>volAverage(<field>)
              per requested field, from volFieldValue.C:106-133.
  * data      writeCurrentTime then `file() << tab << sresult` per field
              (volFieldValueTemplates.C:314) at the object's writePrecision (12).

Columns are located BY HEADER NAME, never by position.

    python3 grade_vmfl045_r2.py                    # grade the run tree
    python3 grade_vmfl045_r2.py --selftest         # all controls, zero compute
    python3 grade_vmfl045_r2.py --dryrun-reader FILE  # parse only; prints no value
    python3 grade_vmfl045_r2.py --verify-frozen SHA   # hash self against a commit
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
SELF_REL = "cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py"
RUN_ROOT = os.path.join(REPO, "verification/runs/ansys_verification/VMFL045/R2")
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL045_R2.json")

# ---------------------------------------------------------------------------
# 1.  THE MANUAL'S OWN NUMBERS (manual pp. 153-154), quoted, not paraphrased
# ---------------------------------------------------------------------------
MANUAL_PAGE = "153-154"
MANUAL_MW = 28.96            # "MW: 0.02896 kg/mol" -> 28.96 kg/kmol
MANUAL_P1 = 101226.4         # Pa,  "Inlet pressure = 101226.4 Pa"
MANUAL_T1 = 289.0            # K,   "Inlet temperature = 289 K"
MANUAL_U1 = 852.68           # m/s, "Inlet velocity = 852.68 m/s"  (THE BC)
MANUAL_RHO1 = 1.22           # kg/m3, "Inlet density 1.22 kg/m3"
MANUAL_MU = 1e-8             # kg/m-s, "Viscosity: 1 x 10-8"
TURN_DEG = 15.0             # "Angle of the ramp = 15 deg"

# THE GATE IS AGAINST THIS.  Table .45.1 Fluent / .45.2 CFX "Target" column.
MANUAL_TARGET_MACH = 1.874    # THE GATE.
MANUAL_TARGET_T = 382.0       # K   -- DECLARED DIAGNOSTIC, never the gate
MANUAL_TARGET_RHO = 2.277     # kg/m3 -- DECLARED DIAGNOSTIC, never the gate

# CONTEXT ONLY -- never the gate, never a band, never a reference.
# Table .45.1 (Fluent) and Table .45.2 (CFX), value + ratio columns.
ANSYS_CONTEXT = {
    "Fluent": {"Mach": 1.902, "Mach_ratio": 1.015, "T": 377.6, "T_ratio": 0.9885,
               "rho": 2.233, "rho_ratio": 0.9807},
    "CFX": {"Mach": 1.871, "Mach_ratio": 0.9984, "T": 382.8, "T_ratio": 1.002,
            "rho": 2.278, "rho_ratio": 1.000},
}

# The manual's own stated accuracy goal, section 1.3, p. 5:
# "The goal for the test cases contained in this manual was to have results
#  accuracy within 3% of the target solution."
MANUAL_GOAL = 0.03

# ---------------------------------------------------------------------------
# 2.  THE GAS.  gamma is FIXED at 1.4 (a DECLARED modelling choice -- the VMFL045
#     section gives NO Cp, so it cannot be derived as VMFL051's was; the case's
#     over-determined inlet data is consistent only with gamma = 1.4, section 2
#     of PREREGISTRATION.md).  R uses OpenFOAM v2606's own universal constant, so
#     the reference matches what the solver computes.
#       RR = 1e3 * NA * k = 1e3 * 6.0221417930e+23 * 1.38065e-23 = 8314.47006650545
#       (fundamentalConstants.C:121, etc/controlDict:1125)
#     Cp is SET to realize gamma = 1.4:  Cp = gamma*R/(gamma-1).
# ---------------------------------------------------------------------------
RR_OPENFOAM = 1.0e3 * 6.0221417930e23 * 1.38065e-23   # 8314.47006650545
RR_CODATA_2018 = 8314.46261815324

GAMMA = 1.4
R_SPECIFIC = RR_OPENFOAM / MANUAL_MW                  # 287.1018669373429
CP_DERIVED = GAMMA * R_SPECIFIC / (GAMMA - 1.0)       # 1004.8565342807003

# As-modelled inlet Mach number FROM THE VELOCITY BC (not an imposed 2.5):
#   M1 = U1 / sqrt(gamma*R*T1)
M1_MODELLED = MANUAL_U1 / math.sqrt(GAMMA * R_SPECIFIC * MANUAL_T1)

# Frozen literals so a later edit to the arithmetic cannot silently move the
# reference.  --selftest asserts the computed values equal these.
R_SPECIFIC_FROZEN = 287.1018669373429
CP_DERIVED_FROZEN = 1004.8565342807003
M1_MODELLED_FROZEN = 2.501814636762496
BETA_WEAK_DEG_FROZEN = 36.92317760072534         # weak-shock angle, as-modelled
M1N_FROZEN = 1.5029493040042183                  # shock-normal Mach = M1*sin(beta)
M2_EXACT_FROZEN = 1.8749769576810524             # post-shock Mach, as-modelled
T2_EXACT_FROZEN = 382.1100763833985              # post-shock T, as-modelled
RHO2_EXACT_FROZEN = 2.2778835945694422           # post-shock rho, as-modelled
P2_EXACT_FROZEN = 249894.17658562586             # post-shock p, as-modelled

# The same solve at M1 = 2.5 EXACTLY -- the value the manual's printed target was
# evidently computed from (it fits the three targets ~3x better than the
# velocity-implied 2.5018; PREREGISTRATION.md section 1a Defect 2).
M2_EXACT_M25_FROZEN = 1.8735260067502537
T2_EXACT_M25_FROZEN = 382.04605297112136
RHO2_EXACT_M25_FROZEN = 2.277189329162137

# Independent textbook cross-checks for --selftest (NACA Report 1135, gamma=1.4).
OBLIQUE_TABLE = {(2.0, 10.0): 39.314, (2.0, 20.0): 53.423, (3.0, 20.0): 37.764}
OBLIQUE_TOL_DEG = 0.02
# normal shock at M = 2, gamma = 1.4 (exact rationals)
NORMAL_M2 = {"rho_ratio": 8.0 / 3.0, "p_ratio": 4.5, "T_ratio": 1.6875,
             "M2": 1.0 / math.sqrt(3.0)}
NORMAL_TOL = 1e-9

# ---------------------------------------------------------------------------
# 3.  THE GATE AND THE DIAGNOSTIC BANDS -- derived in PREREGISTRATION.md sec. 3
# ---------------------------------------------------------------------------
TOL_GATE = 0.01           # 1.0 % of MANUAL_TARGET_MACH.  THE GATE.
TOL_DIAG_TARGET = 0.01    # 1.0 % on T and rho vs the manual's targets. DIAGNOSTIC.
TOL_DIAG_EXACT = 0.005    # 0.5 % of the as-modelled exact Mach.  DIAGNOSTIC.

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
PLATEAU_TOL_MA = 1.0e-3  # peak-to-peak in Mach = 5.3e-4 relative, ~19x tighter
                         # than the 1 % gate and below the expected L-to-L diff

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
PLANT_TURN_DEG = 5.0       # degrees, planted into the oblique-shock solve

# ---------------------------------------------------------------------------
# 7.  THE MESH FAMILY.  Refinement ratio 2 in BOTH directions by construction:
#     every level doubles NX and NY, so h halves exactly and RATIO is not
#     inferred from a cell count.
# ---------------------------------------------------------------------------
LEVELS = (  # name, nx, ny, cells
    ("L1_90x76",   90,  76,   6840),
    ("L2_180x152", 180, 152, 27360),
    ("L3_360x304", 360, 304, 109440),
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
# The oblique-shock reference -- closed form, no CFD input of any kind.
#
# theta-beta-M relation (deflection theta from shock angle beta and upstream M):
#   tan(theta) = 2 cot(beta) * (M^2 sin^2(beta) - 1)
#                             / (M^2 (gamma + cos 2beta) + 2)
# The WEAK-shock root is the SMALLER beta (attached shock, supersonic downstream);
# it is selected by bracketing between the Mach angle mu = asin(1/M) and the beta
# at which theta is maximum (the detachment angle).  The strong root would lie
# above beta(theta_max) and give a SUBSONIC downstream Mach; that this case's M2
# comes out > 1 is the weak-root signature and is asserted.
# ===========================================================================
def theta_from_beta(beta_deg, M, g):
    """Deflection angle (deg) for shock angle beta_deg, upstream Mach M."""
    b = math.radians(beta_deg)
    num = 2.0 / math.tan(b) * (M * M * math.sin(b) ** 2 - 1.0)
    den = M * M * (g + math.cos(2.0 * b)) + 2.0
    return math.degrees(math.atan(num / den))


def beta_at_theta_max(M, g):
    """Shock angle (deg) at which the deflection is maximum -- the boundary
    between the weak and strong roots."""
    mu = math.degrees(math.asin(1.0 / M))
    b, best_b, best_t = mu, mu, -1.0
    while b < 90.0:
        t = theta_from_beta(b, M, g)
        if t > best_t:
            best_t, best_b = t, b
        b += 0.0002
    return best_b, best_t


def solve_beta_weak(M, theta_deg, g):
    """Bracketed bisection for the WEAK-shock beta on [mu, beta(theta_max)]."""
    mu = math.degrees(math.asin(1.0 / M))
    b_tmax, theta_max = beta_at_theta_max(M, g)
    if theta_deg > theta_max + 1e-9:
        raise ValueError("shock DETACHES: theta %g > theta_max %g at M %g"
                         % (theta_deg, theta_max, M))
    lo, hi = mu + 1e-9, b_tmax
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if theta_from_beta(mid, M, g) < theta_deg:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    return 0.5 * (lo + hi), theta_max


def normal_shock(Mn, g):
    """Downstream ratios and shock-normal Mach for shock-normal upstream Mn."""
    rho_ratio = (g + 1.0) * Mn * Mn / ((g - 1.0) * Mn * Mn + 2.0)
    p_ratio = 1.0 + 2.0 * g / (g + 1.0) * (Mn * Mn - 1.0)
    T_ratio = p_ratio / rho_ratio
    M2n = math.sqrt((1.0 + 0.5 * (g - 1.0) * Mn * Mn)
                    / (g * Mn * Mn - 0.5 * (g - 1.0)))
    return rho_ratio, p_ratio, T_ratio, M2n


def oblique_shock(M1, theta_deg, g, T1=MANUAL_T1, p1=MANUAL_P1, rho1=MANUAL_RHO1):
    """Full oblique-shock solution for the WEAK root."""
    beta, theta_max = solve_beta_weak(M1, theta_deg, g)
    b = math.radians(beta)
    M1n = M1 * math.sin(b)
    rho_ratio, p_ratio, T_ratio, M2n = normal_shock(M1n, g)
    M2 = M2n / math.sin(b - math.radians(theta_deg))
    return {"beta": beta, "theta_max": theta_max, "M1n": M1n, "M2n": M2n,
            "M2": M2, "T2": T_ratio * T1, "rho2": rho_ratio * rho1,
            "p2": p_ratio * p1, "rho_ratio": rho_ratio, "p_ratio": p_ratio,
            "T_ratio": T_ratio}


# The frozen inlet stagnation state -- used only for the two DIAGNOSTIC Mach
# re-derivations from scalar averages.
T0_INLET = MANUAL_T1 * (1.0 + 0.5 * (GAMMA - 1.0) * M1_MODELLED ** 2)
P0_INLET = MANUAL_P1 * (T0_INLET / MANUAL_T1) ** (GAMMA / (GAMMA - 1.0))


def isentropic_M_from_p_stag(p, p0, g):
    return math.sqrt(2.0 / (g - 1.0) * ((p0 / p) ** ((g - 1.0) / g) - 1.0))


# ===========================================================================
# READER 1 -- the volFieldValue.dat time series (THE GATED INSTRUMENT)
# ===========================================================================
def read_volfieldvalue(path):
    """Parse a v2606 volFieldValue.dat.  Columns are found BY HEADER NAME."""
    if not os.path.isfile(path):
        refuse("READER", "no such file: %s" % path)
    region = ncells = volume = cols = None
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
                    cols = toks
                continue
            if cols is None:
                refuse("READER", "data row before any '# Time' header in %s" % path)
            toks = line.split()
            if len(toks) != len(cols):
                refuse("READER", "row has %d fields, header declares %d, in %s: %r"
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
        refuse("READER", "no '# Cells' header line in %s -- the region header is "
                         "what proves the zone was found" % path)
    if ncells <= 0:
        refuse("READER", "the function object reports %d cells in its region (%s) "
                         "-- an EMPTY sampling zone reads as a number and must "
                         "never be graded" % (ncells, path))
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
# Roache triple (CLAUDE.md rule 5).  Semantics identical to VMFL051/VMFL005;
# thresholds fixed above.
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
        refuse("C3", "last time %g differs from endTime %g by more than maxDeltaT "
                     "%g in %s" % (t_last, ENDTIME, MAXDELTAT, level_dir))
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

    # DECLARED DEPARTURE 2: the rule's literal "ExecutionTime count == endTime" is
    # a STEADY-ITERATION clause; this solver is transient with an adaptive step,
    # so that count can never be endTime.  The invariant the clause protects --
    # the log is not truncated mid-step -- is checked directly: one ExecutionTime
    # line per Time line.
    n_exec = sum(1 for l in log_lines if l.startswith("ExecutionTime = "))
    n_time = len(log_times)
    if n_exec != n_time or n_exec == 0:
        refuse("C5", "log step integrity: %d ExecutionTime lines against %d Time "
                     "lines in %s" % (n_exec, n_time, log))

    # C6 AGE GUARD, STRICTER than the rule: dated from the LATEST mtime anywhere
    # in the case's own 0/, which run_vmfl045.sh touches last before launch.
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
    ta, _ = value_at_endtime(gate, "volAverage(T)", ENDTIME, MAXDELTAT)
    ra, _ = value_at_endtime(gate, "volAverage(rho)", ENDTIME, MAXDELTAT)
    pa, _ = value_at_endtime(gate, "volAverage(p)", ENDTIME, MAXDELTAT)
    ma_in, _ = value_at_endtime(diag, "volAverage(Ma)", ENDTIME, MAXDELTAT)

    ptp, k, n = plateau_ptp(gate, "volAverage(Ma)", PLATEAU_FRAC)

    return {
        "completion": comp,
        "gate_dat": gate_dat, "diag_dat": diag_dat,
        "gate_ncells": gate["ncells"], "gate_volume": gate["volume"],
        "gate_region": gate["region"],
        "diag_ncells": diag["ncells"], "diag_region": diag["region"],
        "Ma": ma, "T": ta, "rho": ra, "p": pa, "Ma_inner": ma_in,
        "t_row": t_row,
        "plateau_ptp": ptp, "plateau_rows": k, "series_rows": n,
        "M_from_p": isentropic_M_from_p_stag(pa, P0_INLET, GAMMA),
        "endtime_dir": comp["endtime_dir"],
    }


# ===========================================================================
# PLANTED-ZERO CONTROLS (CLAUDE.md rule 3) -- run against the REAL artifacts
# ===========================================================================
def control_pz1(level_dir):
    src = os.path.join(level_dir, "postProcessing", GATE_FO, "0",
                       "volFieldValue.dat")
    base, _ = value_at_endtime(read_volfieldvalue(src), "volAverage(Ma)",
                               ENDTIME, MAXDELTAT)
    tmp = tempfile.mkdtemp(prefix="vmfl045_pz1_")
    try:
        flat = os.path.join(tmp, "flat.dat")
        shutil.copy2(src, flat)
        v_flat, _ = value_at_endtime(read_volfieldvalue(flat), "volAverage(Ma)",
                                     ENDTIME, MAXDELTAT)
        if abs(v_flat - base) > PLANT_DAT_TOL:
            refuse("PZ-1", "the unplanted copy already differs by %g -- the "
                           "reader is not deterministic" % (v_flat - base))
        planted = os.path.join(tmp, "planted.dat")
        plant_into_dat(src, planted, "volAverage(Ma)", PLANT_DAT)
        v_planted, _ = value_at_endtime(read_volfieldvalue(planted),
                                        "volAverage(Ma)", ENDTIME, MAXDELTAT)
        seen = v_planted - base
        if abs(seen - PLANT_DAT) > PLANT_DAT_TOL:
            refuse("PZ-1", "planted %g into a copy of %s, read back %g (error %g "
                           "> %g) -- THE READER CANNOT SEE A NON-ZERO AND HAS "
                           "THEREFORE PRODUCED NO NUMBER"
                   % (PLANT_DAT, src, seen, seen - PLANT_DAT, PLANT_DAT_TOL))
        return {"plant": PLANT_DAT, "seen": seen, "base": base, "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz2(level_dir, endtime_dir):
    src = os.path.join(level_dir, endtime_dir, "Ma")
    vals, kind = read_foam_scalar_field(src)
    if kind != "nonuniform":
        refuse("PZ-2", "the Ma field at endTime in %s is '%s' -- a uniform Mach "
                       "field across a shock is not a solution" % (level_dir, kind))
    mean0 = sum(vals) / len(vals)
    tmp = tempfile.mkdtemp(prefix="vmfl045_pz2_")
    try:
        flat = os.path.join(tmp, "Ma_flat")
        shutil.copy2(src, flat)
        v_flat, _ = read_foam_scalar_field(flat)
        if abs(sum(v_flat) / len(v_flat) - mean0) > PLANT_FIELD_TOL:
            refuse("PZ-2", "the unplanted field copy already differs -- the field "
                           "reader is not deterministic")
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
        # A captured oblique shock means the field must span pre- and post-shock.
        return {"plant": PLANT_FIELD, "seen": seen, "n_cells": len(vals),
                "field_mean": mean0, "field_min": min(vals),
                "field_max": max(vals), "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz3():
    """Plant into the REFERENCE COMPUTATION.  A solver that returned a constant
    beta would sail through every deviation test in this file."""
    sol = oblique_shock(M1_MODELLED, TURN_DEG, GAMMA)
    # identity: the solved beta must reproduce the deflection it was solved for
    ident = theta_from_beta(sol["beta"], M1_MODELLED, GAMMA)
    if abs(ident - TURN_DEG) > 1e-9:
        refuse("PZ-3", "the solved beta does not reproduce its own deflection: "
                       "theta(beta) = %.12f deg, expected %g" % (ident, TURN_DEG))
    # weak-root signature: downstream Mach supersonic
    if sol["M2"] <= 1.0:
        refuse("PZ-3", "the solved M2 = %g is not supersonic -- the STRONG root "
                       "was selected, not the weak root" % sol["M2"])
    # planted arm: a DIFFERENT deflection must give a DIFFERENT, self-consistent beta
    solp = oblique_shock(M1_MODELLED, TURN_DEG + PLANT_TURN_DEG, GAMMA)
    if abs(solp["beta"] - sol["beta"]) < 1e-3:
        refuse("PZ-3", "a %g deg change of deflection moved beta by %g -- the "
                       "solver is returning a constant"
               % (PLANT_TURN_DEG, solp["beta"] - sol["beta"]))
    identp = theta_from_beta(solp["beta"], M1_MODELLED, GAMMA)
    if abs(identp - (TURN_DEG + PLANT_TURN_DEG)) > 1e-9:
        refuse("PZ-3", "the planted solve is not self-consistent: theta(beta) = "
                       "%.12f deg" % identp)
    return {"beta": sol["beta"], "M2": sol["M2"], "theta_identity_deg": ident,
            "plant_deg": PLANT_TURN_DEG, "beta_planted": solp["beta"],
            "delta_beta": solp["beta"] - sol["beta"], "fired": True}


# ===========================================================================
# GRADE
# ===========================================================================
def grade():
    sol = oblique_shock(M1_MODELLED, TURN_DEG, GAMMA)
    if abs(sol["M2"] - M2_EXACT_FROZEN) > 1e-12:
        refuse("REFERENCE", "the in-module oblique-shock solve gives M2 = %.16f "
                            "but the frozen literal is %.16f -- the reference has "
                            "drifted" % (sol["M2"], M2_EXACT_FROZEN))

    controls = {"PZ-3_reference": control_pz3()}

    per_level = {}
    for name, nx, ny, cells in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        if not os.path.isdir(d):
            refuse("C0", "level directory %s does not exist -- nothing to grade" % d)
        per_level[name] = read_level(d)
        per_level[name]["cells"] = cells
        per_level[name]["nx"], per_level[name]["ny"] = nx, ny

    finest = LEVELS[-1][0]
    controls["PZ-1_dat_reader"] = control_pz1(os.path.join(RUN_ROOT, finest))
    controls["PZ-2_field_reader"] = control_pz2(
        os.path.join(RUN_ROOT, finest), per_level[finest]["endtime_dir"])

    vals = [per_level[n]["Ma"] for n, _, _, _ in LEVELS]
    triple = roache(vals[0], vals[1], vals[2])

    M_lab = vals[-1]
    T_lab = per_level[finest]["T"]
    rho_lab = per_level[finest]["rho"]
    dev_target = (M_lab - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH
    dev_exact = (M_lab - sol["M2"]) / sol["M2"]
    dev_T = (T_lab - MANUAL_TARGET_T) / MANUAL_TARGET_T
    dev_rho = (rho_lab - MANUAL_TARGET_RHO) / MANUAL_TARGET_RHO

    # ---- CLAUDE.md rule 5, IN ITS STATED ORDER -------------------------
    verdict = why = None

    # step 1: any level not plateaued -> NOT A RESULT
    for name, _, _, _ in LEVELS:
        L = per_level[name]
        if L["plateau_ptp"] > PLATEAU_TOL_MA:
            verdict = "NOT A RESULT"
            why = ("level %s has not plateaued: peak-to-peak of the gate Mach "
                   "series over its last %d of %d rows is %.3e > %.3e (rule 5 "
                   "step 1)" % (name, L["plateau_rows"], L["series_rows"],
                                L["plateau_ptp"], PLATEAU_TOL_MA))
            break
    # declared inner-zone consistency clause -- can only produce NOT A RESULT
    if verdict is None:
        L = per_level[finest]
        zc = abs(L["Ma"] - L["Ma_inner"]) / abs(L["Ma"])
        if zc > ZONE_CONSISTENCY_TOL:
            verdict = "NOT A RESULT"
            why = ("the gate zone and its strictly-inner diagnostic zone disagree "
                   "by %.3e > %.3e at %s -- the gate zone is being contaminated "
                   "from an edge" % (zc, ZONE_CONSISTENCY_TOL, finest))

    # step 2: triple not CONVERGING -> NOT A RESULT
    if verdict is None and triple["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = "grid triple is %s, not CONVERGING (rule 5 step 2)" % triple["state"]

    # step 3: CONVERGING -> PASS inside the band else GATE FAIL
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

    return {
        "case": "VMFL045",
        "manual_page": MANUAL_PAGE,
        "verdict": verdict,
        "why": why,
        "gate": {"reference": MANUAL_TARGET_MACH,
                 "reference_class": "manual printed target Mach, Tables .45.1/.45.2 "
                                    "(analytic oblique-shock, White 1994)",
                 "tolerance_rel": TOL_GATE,
                 "lab_value": M_lab,
                 "deviation_rel": dev_target,
                 "deviation_pct": 100 * dev_target},
        "diagnostic_exact_mach": {"reference": sol["M2"],
                                  "reference_class": "closed-form oblique-shock M2 "
                                  "for the as-modelled inlet (velocity BC 852.68, "
                                  "M1 = %.10f, gamma = 1.4)" % M1_MODELLED,
                                  "tolerance_rel": TOL_DIAG_EXACT,
                                  "deviation_rel": dev_exact,
                                  "deviation_pct": 100 * dev_exact,
                                  "inside": abs(dev_exact) <= TOL_DIAG_EXACT},
        "diagnostic_T": {"reference_manual": MANUAL_TARGET_T,
                         "reference_exact": sol["T2"], "lab_value": T_lab,
                         "deviation_manual_pct": 100 * dev_T,
                         "tolerance_rel": TOL_DIAG_TARGET,
                         "inside": abs(dev_T) <= TOL_DIAG_TARGET},
        "diagnostic_rho": {"reference_manual": MANUAL_TARGET_RHO,
                           "reference_exact": sol["rho2"], "lab_value": rho_lab,
                           "deviation_manual_pct": 100 * dev_rho,
                           "tolerance_rel": TOL_DIAG_TARGET,
                           "inside": abs(dev_rho) <= TOL_DIAG_TARGET},
        "gamma": GAMMA, "R_specific": R_SPECIFIC, "Cp": CP_DERIVED,
        "RR_openfoam": RR_OPENFOAM, "M1_modelled": M1_MODELLED,
        "beta_weak_deg": sol["beta"], "theta_max_deg": sol["theta_max"],
        "M2_exact_M1_2p5": M2_EXACT_M25_FROZEN,
        "ansys_context_never_the_gate": ANSYS_CONTEXT,
        "triple": triple, "levels": per_level, "controls": controls,
        "endTime": ENDTIME, "plateau_tol_Ma": PLATEAU_TOL_MA,
    }


def report(res):
    P = print
    P("=" * 78)
    P("VMFL045 -- Oblique Shock Over an Inclined Ramp")
    P("Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. %s"
      % res["manual_page"])
    P("=" * 78)
    P("")
    P("gamma  = %.4f (SET; the VMFL045 section gives NO Cp -- see "
      "PREREGISTRATION.md sec. 2)" % res["gamma"])
    P("R      = %.13f J/kg-K   Cp = %.13f J/kg-K" % (res["R_specific"], res["Cp"]))
    P("M1     = %.13f  (from the velocity BC 852.68 m/s, NOT 2.5)"
      % res["M1_modelled"])
    P("beta   = %.13f deg (weak root; theta_max = %.4f deg, deflection 15 deg)"
      % (res["beta_weak_deg"], res["theta_max_deg"]))
    P("")
    P("--- controls (CLAUDE.md rule 3) ---")
    for k, v in res["controls"].items():
        P("  %-20s FIRED  %s" % (k, {kk: ("%.6g" % vv if isinstance(vv, float)
                                          else vv)
                                     for kk, vv in v.items() if kk != "fired"}))
    P("")
    P("--- levels ---")
    for name, _, _, cells in LEVELS:
        L = res["levels"][name]
        P("  %-12s cells %6d  zone %5d cells  Ma = %.10f  (inner %.10f)  "
          "plateau ptp %.3e over %d/%d rows"
          % (name, cells, L["gate_ncells"], L["Ma"], L["Ma_inner"],
             L["plateau_ptp"], L["plateau_rows"], L["series_rows"]))
        P("  %-12s   T = %.4f K  rho = %.6f  <p> = %.2f Pa  M(from p0/p) = %.8f"
          % ("", L["T"], L["rho"], L["p"], L["M_from_p"]))
    P("")
    t = res["triple"]
    P("--- Roache triple on the post-shock Mach number, r = %.1f, Fs = %.2f ---"
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
    d = res["diagnostic_exact_mach"]
    P("--- THE GATE (manual printed target Mach, Tables .45.1/.45.2) ---")
    P("  reference   %.4f" % g["reference"])
    P("  lab value   %.10f   (finest level, %s)" % (g["lab_value"], LEVELS[-1][0]))
    P("  deviation   %+.6f %%   band +/- %.4f %%"
      % (g["deviation_pct"], 100 * g["tolerance_rel"]))
    P("")
    P("--- DIAGNOSTICS, NEVER THE GATE ---")
    P("  exact Mach (as-modelled) %.13f  dev %+.6f %%  band +/-%.3f %%  inside %s"
      % (d["reference"], d["deviation_pct"], 100 * d["tolerance_rel"], d["inside"]))
    dt, dr = res["diagnostic_T"], res["diagnostic_rho"]
    P("  T   lab %.4f K   vs manual %.1f (dev %+.4f %%, inside %s)  vs exact %.4f"
      % (dt["lab_value"], dt["reference_manual"], dt["deviation_manual_pct"],
         dt["inside"], dt["reference_exact"]))
    P("  rho lab %.6f    vs manual %.3f (dev %+.4f %%, inside %s)  vs exact %.6f"
      % (dr["lab_value"], dr["reference_manual"], dr["deviation_manual_pct"],
         dr["inside"], dr["reference_exact"]))
    P("  exact Mach at M1 = 2.5 (target basis): %.13f" % res["M2_exact_M1_2p5"])
    P("")
    P("--- CONTEXT ONLY, never the gate: Ansys's own reported values ---")
    for solver, v in res["ansys_context_never_the_gate"].items():
        P("  %-7s Mach %.4f (r %.4f)  T %.1f (r %.4f)  rho %.4f (r %.4f)"
          % (solver, v["Mach"], v["Mach_ratio"], v["T"], v["T_ratio"],
             v["rho"], v["rho_ratio"]))
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
            ["git", "-C", REPO, "cat-file", "blob", "%s:%s" % (commitish, SELF_REL)])
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
    print("FREEZE VERIFIED: %s is byte-identical to %s:%s (sha256 %s)"
          % (os.path.basename(SELF_REL), commitish, SELF_REL,
             hashlib.sha256(mine).hexdigest()[:16]))
    return 0


# ===========================================================================
# --selftest : every control and every classifier arm, with ZERO solver compute
# ===========================================================================
FIXTURE = """\
# Region : cellZone gateZone
# Cells  : 252
# Volume : 1.44e-04
# Time\tvolAverage(Ma)\tvolAverage(T)\tvolAverage(rho)\tvolAverage(p)
0.001\t1.90\t379.0\t2.25\t248000
0.003\t1.878\t381.8\t2.276\t249800
0.005\t1.8751\t382.10\t2.2779\t249890
0.006\t1.87499\t382.109\t2.27788\t249894
0.007\t1.8749770\t382.1100\t2.277884\t249894.2
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
2.5018
2.5018
2.10
1.8749770
1.8749770
1.90
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

    print("VMFL045 comparator selftest -- no solver, no run tree touched")
    print("")
    print("[A] the gas (gamma FIXED at 1.4; the manual gives no Cp)")
    check("RR (OpenFOAM v2606 NA*k*1e3)", abs(RR_OPENFOAM - 8314.47006650545) < 1e-8,
          "= %.11f" % RR_OPENFOAM)
    check("R specific", abs(R_SPECIFIC - R_SPECIFIC_FROZEN) < 1e-10,
          "= %.13f J/kg-K" % R_SPECIFIC)
    check("Cp realizes gamma = 1.4",
          abs(CP_DERIVED - CP_DERIVED_FROZEN) < 1e-9
          and abs(CP_DERIVED / (CP_DERIVED - R_SPECIFIC) - 1.4) < 1e-12,
          "Cp = %.13f -> gamma = %.13f"
          % (CP_DERIVED, CP_DERIVED / (CP_DERIVED - R_SPECIFIC)))
    check("M1 from the velocity BC is 2.5018, NOT 2.5",
          abs(M1_MODELLED - M1_MODELLED_FROZEN) < 1e-12
          and abs(M1_MODELLED - 2.5) > 1e-3,
          "M1 = %.13f" % M1_MODELLED)

    print("")
    print("[B] the oblique-shock solver vs NACA 1135 chart (gamma = 1.4)")
    for (M, th), ref in sorted(OBLIQUE_TABLE.items()):
        b, _ = solve_beta_weak(M, th, 1.4)
        check("beta_weak(M=%.1f, theta=%.0f) = %.3f deg" % (M, th, ref),
              abs(b - ref) <= OBLIQUE_TOL_DEG, "computed %.5f" % b)
    rr, pr, Tr, M2n = normal_shock(2.0, 1.4)
    check("normal shock M=2: rho2/rho1 = 8/3",
          abs(rr - NORMAL_M2["rho_ratio"]) < NORMAL_TOL, "= %.10f" % rr)
    check("normal shock M=2: p2/p1 = 4.5",
          abs(pr - NORMAL_M2["p_ratio"]) < NORMAL_TOL, "= %.10f" % pr)
    check("normal shock M=2: T2/T1 = 1.6875",
          abs(Tr - NORMAL_M2["T_ratio"]) < NORMAL_TOL, "= %.10f" % Tr)
    check("normal shock M=2: M2 = 1/sqrt(3)",
          abs(M2n - NORMAL_M2["M2"]) < NORMAL_TOL, "= %.10f" % M2n)

    print("")
    print("[C] the frozen reference values (as-modelled inlet, M1 = 2.5018)")
    sol = oblique_shock(M1_MODELLED, TURN_DEG, GAMMA)
    check("beta weak", abs(sol["beta"] - BETA_WEAK_DEG_FROZEN) < 1e-10,
          "= %.13f deg" % sol["beta"])
    check("M1n = M1 sin(beta)", abs(sol["M1n"] - M1N_FROZEN) < 1e-12,
          "= %.13f" % sol["M1n"])
    check("M2 exact", abs(sol["M2"] - M2_EXACT_FROZEN) < 1e-12, "= %.13f" % sol["M2"])
    check("T2 exact", abs(sol["T2"] - T2_EXACT_FROZEN) < 1e-9, "= %.10f K" % sol["T2"])
    check("rho2 exact", abs(sol["rho2"] - RHO2_EXACT_FROZEN) < 1e-12,
          "= %.13f" % sol["rho2"])
    check("weak root -> M2 supersonic", sol["M2"] > 1.0, "M2 = %.6f" % sol["M2"])
    sol25 = oblique_shock(2.5, TURN_DEG, GAMMA)
    check("M1 = 2.5 exactly reproduces the manual's printed target to 0.03 %",
          abs((sol25["M2"] - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH) < 3e-4
          and abs((sol25["T2"] - MANUAL_TARGET_T) / MANUAL_TARGET_T) < 3e-4
          and abs((sol25["rho2"] - MANUAL_TARGET_RHO) / MANUAL_TARGET_RHO) < 3e-4,
          "M2 %.5f T2 %.3f rho2 %.5f" % (sol25["M2"], sol25["T2"], sol25["rho2"]))
    check("the as-modelled exact Mach fits inside the 1 %% gate",
          abs((sol["M2"] - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH) < TOL_GATE,
          "dev %.5f %%" % (100 * (sol["M2"] - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH))

    print("")
    print("[D] the reader, on the REAL volFieldValue.dat format")
    tmp = tempfile.mkdtemp(prefix="vmfl045_selftest_")
    try:
        f = os.path.join(tmp, "volFieldValue.dat")
        open(f, "w").write(FIXTURE)
        s = read_volfieldvalue(f)
        check("region header parsed", s["region"] == "cellZone gateZone", s["region"])
        check("cell count parsed", s["ncells"] == 252, str(s["ncells"]))
        check("columns located by NAME",
              s["cols"] == ["Time", "volAverage(Ma)", "volAverage(T)",
                            "volAverage(rho)", "volAverage(p)"], str(s["cols"]))
        v, t = value_at_endtime(s, "volAverage(Ma)", ENDTIME, MAXDELTAT)
        check("endTime row found", abs(t - ENDTIME) < 1e-12 and abs(v - 1.8749770) < 1e-9,
              "Ma = %.7f at t = %g" % (v, t))
        f2 = os.path.join(tmp, "short.dat")
        open(f2, "w").write(FIXTURE.replace(
            "0.007\t1.8749770\t382.1100\t2.277884\t249894.2", "0.007\t1.8749770"))
        try:
            read_volfieldvalue(f2)
            check("a short data row REFUSES", False)
        except Refusal as e:
            check("a short data row REFUSES", "READER" in str(e))
        f3 = os.path.join(tmp, "nocells.dat")
        open(f3, "w").write(FIXTURE.replace("# Cells  : 252", "# Cells  : 0"))
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
        check("the solved beta reproduces theta = 15 deg",
              abs(pz3["theta_identity_deg"] - TURN_DEG) < 1e-9,
              "%.12f deg" % pz3["theta_identity_deg"])
        check("a planted deflection moves beta", abs(pz3["delta_beta"]) > 1e-1,
              "+%g deg -> delta beta = %+.6f deg" % (PLANT_TURN_DEG, pz3["delta_beta"]))
    except Refusal as e:
        check("PZ-3", False, str(e))

    print("")
    print("[H] the Roache classifier, every state")
    t1 = roache(1.0 + 0.04, 1.0 + 0.02, 1.0 + 0.01)      # first order
    check("first-order family -> CONVERGING, p ~ 1",
          t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9, "p = %.6f" % t1["p"])
    t2 = roache(1.0 + 0.04, 1.0 + 0.01, 1.0 + 0.0025)    # second order
    check("second-order family -> CONVERGING, p ~ 2",
          t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9,
          "p = %.6f, GCI %.4f %%" % (t2["p"], 100 * t2["gci_fine"]))
    check("divergent family -> DIVERGENT", roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory family -> OSCILLATORY", roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("equal-step family -> STAGNANT", roache(1.0, 1.1, 1.2)["state"] == "STAGNANT")
    check("identical values -> EXACT", roache(2.5, 2.5, 2.5)["state"] == "EXACT")
    check("no GCI is quoted for a non-CONVERGING triple",
          roache(1.0, 1.2, 1.0)["gci_fine"] is None)

    print("")
    print("[I] the gate, both arms")
    inside = M2_EXACT_FROZEN
    check("the as-modelled exact value PASSES the gate",
          abs((inside - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH) <= TOL_GATE,
          "%.5f %%" % (100 * (inside - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH))
    outside = MANUAL_TARGET_MACH * (1.0 + 1.5 * TOL_GATE)
    check("a value 1.5 %% off FAILS the gate",
          abs((outside - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH) > TOL_GATE,
          "%.5f %%" % (100 * (outside - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH))
    check("an INCOMPRESSIBLE / no-shock treatment (M unchanged at 2.5018) FAILS",
          abs((M1_MODELLED - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH) > TOL_GATE,
          "%.3f %% -- sampling the freestream instead of the post-shock zone"
          % (100 * (M1_MODELLED - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH))
    check("Ansys FLUENT's own reported Mach would FAIL this 1 %% gate",
          abs((ANSYS_CONTEXT["Fluent"]["Mach"] - MANUAL_TARGET_MACH)
              / MANUAL_TARGET_MACH) > TOL_GATE,
          "%.4f %% -- Fluent point-sampled 1.902; the frozen zone average avoids "
          "the near-shock bias (PREREGISTRATION.md sec. 3)"
          % (100 * (ANSYS_CONTEXT["Fluent"]["Mach"] - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH))
    check("Ansys CFX's own reported Mach would PASS this 1 %% gate",
          abs((ANSYS_CONTEXT["CFX"]["Mach"] - MANUAL_TARGET_MACH)
              / MANUAL_TARGET_MACH) <= TOL_GATE,
          "%.4f %%" % (100 * (ANSYS_CONTEXT["CFX"]["Mach"] - MANUAL_TARGET_MACH) / MANUAL_TARGET_MACH))

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
        # deliberately prints NO value -- the pre-freeze reader check L-286 names.
        print("parsed, %d rows, %d columns %r, region %r, %d cells"
              % (len(s["rows"]), len(s["cols"]), s["cols"], s["region"], s["ncells"]))
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
