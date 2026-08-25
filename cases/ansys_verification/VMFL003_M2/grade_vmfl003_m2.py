#!/usr/bin/env python3
"""
VMFL003-M2 -- Pressure Drop in Turbulent Flow Through a Pipe.  THE M2
COMPARATOR (epsilon family: kEpsilon / realizableKE / RNGkEpsilon).

M2 DELTAS vs the frozen run-1 comparator, all disclosed (Sanaa 2026-08-25
"try other models"; supervisor rulings 2026-08-25):
  (1) endTimes bumped 6000/8000/12000 -> 15000/18000/22000 (ladder 18000)
      so every level clears the residual floor -- run-1 Defect B. DATA only.
  (2) y+ MINIMUM clause added: min wall y+ >= YPLUS_MIN_FLOOR = 11.06, the
      nutkWallFunction yPlusLam log-law crossover.  Would have HELD in run 1
      (L3 min 23.812), so it is a tightening, not an answer-fitted band.
  (3) VERDICT CEILING is GATE REACHED, never PASS: the dominant radial/wall
      channel is unrefinable here (N-AV10, R+=408), so a grid-converged
      credential (PASS/HOLDS) is structurally unattainable and is NOT
      claimed.  gate_verdict() returns GATE REACHED in-band; the GCI is
      reported as an AXIAL-channel diagnostic, never a certification.
  (4) repo root derived with `git rev-parse --show-toplevel` (the class fix
      this team owes; run-1 used three dirnames up from __file__).
The GRADING LOGIC (readers, roache(), controls, verdict ORDER) is unchanged.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 19-20.

NOT FILED ANYWHERE.  Nothing this script produces is sent, emailed, uploaded,
filed, posted, registered or commented outside this box (CLAUDE.md rules 7, 8).

THIS FILE IS THE GRADING PATH.  It is frozen by commit BEFORE any solver runs
(CLAUDE.md rule 2; VERIFICATION_CHARTER.md sections 2b, 2d).  Every threshold,
band, reference value and plant constant below is a MODULE-LEVEL CONSTANT and
NONE of them is settable from the command line.  `--verify-frozen <commit>`
re-hashes this file's own bytes against the committed blob and REFUSES (exit 2)
unless they are byte-identical.

POSTURE (CLAUDE.md rules 3, 4, 5):
  * refuse() exits 2 -- the comparator REFUSES rather than degrades.  It never
    grades a partial run and never invents a missing number.
  * three planted-zero controls run against the REAL artifacts (on temp copies;
    the run tree is never modified) and the comparator refuses if the reader
    cannot see the plant.
  * roache() returns a STATE, and grade() implements rule 5 in its stated order:
    (1) not converged / not plateaued / wall function out of validity  ->
        NOT A RESULT; (2) triple not CONVERGING -> NOT A RESULT with NO GCI
    quoted; (3) CONVERGING -> PASS inside the band else GATE FAIL, GCI printed.
    The gate can only turn a PASS or GATE FAIL INTO NOT A RESULT, never the
    reverse.
"""

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ===========================================================================
# THE CASE, FROM THE MANUAL'S OWN MATERIAL PROPERTIES / GEOMETRY / BC BLOCKS
# (p. 19).  Nothing here is assumed; every number is quoted or derived.
# ===========================================================================
RHO   = 1.225                      # kg/m3   -- manual p. 19
MU    = 1.7894e-5                  # kg/m-s  -- manual p. 19
U_IN  = 50.0                       # m/s     -- manual p. 19 (inlet velocity)
R_PIPE = 0.002                     # m       -- manual p. 19 (radius)
D_PIPE = 2.0 * R_PIPE              # m       = 0.004
L_PIPE = 2.0                       # m       -- manual p. 19 (length)

NU    = MU / RHO                   # 1.4607346938775508e-05 m2/s
RE    = RHO * U_IN * D_PIPE / MU   # 13691.740248127866  (manual: "1.37 X 10^4")
QDYN  = 0.5 * RHO * U_IN * U_IN    # 1531.2500000000002 Pa
LOVERD = L_PIPE / D_PIPE           # 500.0

# ===========================================================================
# THE GATE.  Manual Table .03.1 (Ansys Fluent) and Table .03.2 (Ansys CFX),
# p. 20, both print "Target ... Pressure Drop, Pa ... 21744".
# ===========================================================================
TARGET_DP_PA = 21744.0             # THE GATE IS AGAINST THIS
GATE_BAND    = 0.025               # 2.5 % relative.  Derivation: PREREGISTRATION.md 3.4

# The manual's own two solvers, CONTEXT ONLY -- never a gate, never a band.
ANSYS_CONTEXT = {"Fluent": 21480.0, "CFX": 21740.0}

# ---------------------------------------------------------------------------
# THE REFERENCE, DERIVED HERE TO FULL DOUBLE PRECISION.  A DIAGNOSTIC, NEVER
# THE GATE.  The manual (p. 19) says the friction factor "can be determined for
# the given Reynolds number from Moody chart" -- so the reference correlation
# is the MOODY CHART, i.e. the smooth-pipe (Colebrook / Prandtl-von Karman)
# branch, NOT Blasius.  That reading is confirmed arithmetically: the manual's
# printed target 21744 Pa is reproduced to 6 significant figures by a
# 3-significant-figure chart read f = 0.0284
#     0.0284 * 500 * 1531.25 = 21743.750000000004  ->  21744
# whereas Blasius (f = 0.029212748500739585) gives 22366.01057087875 Pa, which
# is 2.860608 % away and cannot be what the manual used.
# ---------------------------------------------------------------------------
F_COLEBROOK   = 0.028464169573919965   # smooth-pipe Colebrook / P-vK at RE
DP_COLEBROOK  = 21792.879830032474     # Pa  = F_COLEBROOK * 500 * 1531.25
F_CHART       = 0.0284                 # the 3-s.f. chart read the target implies
F_IMPLIED     = 0.02840032653061224    # = TARGET_DP_PA / (LOVERD * QDYN)
DP_BLASIUS    = 22366.01057087875      # Pa  -- NEGATIVE CONTROL, must GATE FAIL
DP_LAMINAR    = 3578.7999999999997     # Pa  = 32 mu L U / D^2 -- must GATE FAIL

DIAG_BAND_DP  = 0.020    # exact-correlation diagnostic band, PRINTED not gated
DIAG_BAND_F   = 0.020    # developed-region friction-factor diagnostic band

# ---------------------------------------------------------------------------
# WALL-FUNCTION VALIDITY.  u_tau = U sqrt(f/8) with f = F_COLEBROOK.
# R+ = R u_tau / nu = 408.3503397076439 -- the ENTIRE pipe radius is only ~408
# wall units, which is why the radial mesh cannot be refined by 2 twice and
# stay in the log layer (PREREGISTRATION.md 4.2).
# ---------------------------------------------------------------------------
U_TAU     = 2.9824575423381954
R_PLUS    = 408.3503397076439
YPLUS_PRED = 40.835033970764385   # first cell centre, NR = 5, uniform
YPLUS_LO   = 25.0                 # one-way NOT-A-RESULT band on the AVERAGE
YPLUS_HI   = 65.0
YPLUS_MIN_FLOOR = 11.06           # nutkWallFunction yPlusLam log-law crossover;
                                  # min wall y+ below this = a face in the
                                  # sublayer where the wall function is invalid.
                                  # run-1 L3 min was 23.812, so this HELD there.

# ---------------------------------------------------------------------------
# THE DEVELOPED-REGION DIAGNOSTIC (system/topoSetDict).  NEVER THE GATE.
# ---------------------------------------------------------------------------
SLAB_XA = 1.00       # m
SLAB_XB = 1.80       # m
SLAB_DX = 0.80       # m  (= SLAB_XB - SLAB_XA, fixed here, not recomputed)

# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE, PER LEVEL, CHECKED BEFORE THE TRIPLE IS FORMED
# (CLAUDE.md rule 5 step 1; the VMFL051 lesson).
# ---------------------------------------------------------------------------
RESID_TOL   = 1.0e-8   # final INITIAL residual, each of p, Ux, k, epsilon
PLATEAU_FRAC = 0.20    # last 20 % of the iteration series
PTP_TOL      = 1.0e-2  # Pa, peak-to-peak of dp over that window

# ---------------------------------------------------------------------------
# ROACHE (CLAUDE.md rule 5).  Refinement ratio 2 BY CONSTRUCTION (axial).
# ---------------------------------------------------------------------------
RATIO    = 2.0
FS       = 1.25
EPS_ABS  = 1.0e-9      # Pa; below this a level-to-level difference is zero
STAG_TOL = 1.0e-3

# ---------------------------------------------------------------------------
# THE WALL-TREATMENT SENSITIVITY LADDER.  A DECLARED DIAGNOSTIC, NOT A ROACHE
# TRIPLE (its levels are not in ratio 2 and it is never Richardson-extrapolated).
# It measures the channel a GCI structurally cannot see -- the N-AV7 lesson.
# One-way clause: a spread beyond LADDER_SPREAD_MAX means the answer is a
# property of the wall-cell placement rather than of the case -> NOT A RESULT.
# ---------------------------------------------------------------------------
LADDER_SPREAD_MAX = 0.05   # 5 % = twice the gate band

# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  Planted into TEMP COPIES of the
# REAL artifacts; the run tree is never modified.
# ---------------------------------------------------------------------------
PLANT_DP    = 1.234    # m2/s2 into the KINEMATIC inlet pressure column
PLANT_YPLUS = 7.77     # into the yPlus `average` column
PLANT_SLAB  = 2.345    # m2/s2 into the slabA volAverage(p) column
PLANT_TOL   = 1.0e-9   # absolute agreement demanded of each control

# ---------------------------------------------------------------------------
# THE MESH FAMILY.  Refinement ratio 2 in the AXIAL direction by construction;
# the radial mesh is HELD FIXED at NR = 5 so the wall-function placement is
# IDENTICAL at every level (PREREGISTRATION.md 4.2).
# ---------------------------------------------------------------------------
LEVELS = [
    # (name,          nx,   nr, cells, endTime)
    ("L1_250x5",     250,    5,  1250, 15000),
    ("L2_500x5",     500,    5,  2500, 18000),
    ("L3_1000x5",   1000,    5,  5000, 22000),
]
LADDER = [
    ("D_500x3",      500,    3,  1500, 18000),
    ("D_500x4",      500,    4,  2000, 18000),
    ("L2_500x5",     500,    5,  2500, 18000),   # reused, not re-run
    ("D_500x6",      500,    6,  3000, 18000),
]
FIELDS_REQUIRED = ["U", "p", "k", "epsilon", "nut"]

RUNROOT_DEFAULT = "verification/runs/ansys_verification/VMFL003_M2"


# ===========================================================================
# REFUSAL
# ===========================================================================
class Refusal(Exception):
    pass


def refuse(msg):
    """Exit 2.  The comparator refuses rather than degrades."""
    raise Refusal(msg)


# ===========================================================================
# READERS.  Columns are located BY HEADER NAME, NEVER BY POSITION (N-AV4/L-286).
# ===========================================================================
_HDR_VAL = re.compile(r"^#\s*([A-Za-z][A-Za-z0-9 +()_-]*?)\s*:\s*(.*?)\s*$")


def _read_dat(path):
    """Parse an OpenFOAM functionObject .dat file.

    Returns (meta, colnames, rows) where meta maps header key -> raw string,
    colnames is the list from the '# Time ...' column line, and rows is a list
    of lists of raw string cells.
    """
    if not os.path.isfile(path):
        refuse("missing artifact: %s" % path)
    meta, colnames, rows = {}, None, []
    with open(path, "r") as fh:
        for line in fh:
            s = line.rstrip("\n")
            if not s.strip():
                continue
            if s.lstrip().startswith("#"):
                body = s.lstrip()[1:].strip()
                if body.split()[:1] == ["Time"]:
                    colnames = body.split()
                    continue
                m = _HDR_VAL.match(s.strip())
                if m:
                    meta[m.group(1).strip()] = m.group(2).strip()
                continue
            rows.append(s.split())
    if colnames is None:
        refuse("no '# Time ...' column header in %s -- reader cannot locate "
               "columns by name and REFUSES to guess by position" % path)
    if not rows:
        refuse("no data rows in %s" % path)
    return meta, colnames, rows


def _col(colnames, want, path):
    if want not in colnames:
        refuse("column %r absent from %s (header is %r)" % (want, path, colnames))
    return colnames.index(want)


def read_series(path, colname):
    """[(time, value)] from a surfaceFieldValue / volFieldValue .dat file."""
    meta, colnames, rows = _read_dat(path)
    ic = _col(colnames, colname, path)
    it = _col(colnames, "Time", path)
    out = []
    for r in rows:
        if len(r) <= max(ic, it):
            refuse("short data row in %s: %r" % (path, r))
        out.append((float(r[it]), float(r[ic])))
    return meta, out


def read_patch_series(path, colname):
    """Same, but ALSO asserts the '# Faces' control is present and non-zero."""
    meta, series = read_series(path, colname)
    if "Faces" not in meta:
        refuse("no '# Faces' header in %s -- the non-empty-patch control cannot "
               "be evaluated and the comparator REFUSES" % path)
    if int(meta["Faces"]) <= 0:
        refuse("'# Faces : %s' in %s -- the sampled patch is EMPTY" %
               (meta["Faces"], path))
    return meta, series


def read_zone_series(path, colname):
    """Same, but asserts the '# Cells' control is present and non-zero."""
    meta, series = read_series(path, colname)
    if "Cells" not in meta:
        refuse("no '# Cells' header in %s -- the non-empty-cellZone control "
               "cannot be evaluated and the comparator REFUSES" % path)
    if int(meta["Cells"]) <= 0:
        refuse("'# Cells : %s' in %s -- the sampled cellZone is EMPTY" %
               (meta["Cells"], path))
    return meta, series


def read_yplus(path, patch="walls"):
    """[(time, ymin, ymax, yavg)] for one wall patch from a yPlus .dat file."""
    meta, colnames, rows = _read_dat(path)
    it = _col(colnames, "Time", path)
    ip = _col(colnames, "patch", path)
    imn = _col(colnames, "min", path)
    imx = _col(colnames, "max", path)
    iav = _col(colnames, "average", path)
    out = []
    for r in rows:
        if len(r) <= max(it, ip, imn, imx, iav):
            refuse("short yPlus row in %s: %r" % (path, r))
        if r[ip] != patch:
            continue
        out.append((float(r[it]), float(r[imn]), float(r[imx]), float(r[iav])))
    if not out:
        refuse("no yPlus rows for patch %r in %s" % (patch, path))
    return out


# ===========================================================================
# THE GATE QUANTITY.  dp[Pa] = RHO * ( <p>_inlet - <p>_outlet ), because
# simpleFoam solves KINEMATIC pressure.  RHO is applied HERE, explicitly, and
# planted-zero control 1 proves at grade time that it was applied.
# ===========================================================================
def dp_series_pa(inlet_dat, outlet_dat):
    _, si = read_patch_series(inlet_dat, "areaAverage(p)")
    _, so = read_patch_series(outlet_dat, "areaAverage(p)")
    if len(si) != len(so):
        refuse("inlet/outlet monitor series lengths differ (%d vs %d)"
               % (len(si), len(so)))
    out = []
    for (ti, vi), (to, vo) in zip(si, so):
        if ti != to:
            refuse("inlet/outlet monitor times disagree: %r vs %r" % (ti, to))
        out.append((ti, RHO * (vi - vo)))
    return out


def f_dev_from_slabs(slabA_dat, slabB_dat):
    """Developed-region Darcy friction factor.  DIAGNOSTIC, NEVER THE GATE."""
    _, sa = read_zone_series(slabA_dat, "volAverage(p)")
    _, sb = read_zone_series(slabB_dat, "volAverage(p)")
    pa = sa[-1][1]
    pb = sb[-1][1]
    dpdx = RHO * (pa - pb) / SLAB_DX          # Pa/m
    return dpdx * D_PIPE / QDYN, dpdx


# ===========================================================================
# STRICT COMPLETION (CLAUDE.md rule 4).  Departures declared in
# PREREGISTRATION.md section 8 and repeated in the messages below.
# ===========================================================================
def check_completion(level_dir, endtime, solver_log="log.simpleFoam"):
    notes = []

    # C1  rc = 0
    rcf = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rcf):
        refuse("C1: no RUN_RC.txt in %s" % level_dir)
    rctxt = open(rcf).read()
    m = re.search(r"rc\s*=\s*(-?\d+)", rctxt)
    if not m:
        refuse("C1: RUN_RC.txt in %s has no 'rc=' line" % level_dir)
    if int(m.group(1)) != 0:
        refuse("C1: rc = %s (not 0) in %s" % (m.group(1), level_dir))
    notes.append("C1 rc=0 OK")

    # C2  an End line
    logp = os.path.join(level_dir, solver_log)
    if not os.path.isfile(logp):
        refuse("C2: no %s in %s" % (solver_log, level_dir))
    log = open(logp, errors="replace").read()
    if not re.search(r"^End\s*$", log, re.M):
        refuse("C2: no 'End' line in %s" % logp)
    notes.append("C2 End OK")

    # C3  last time == endTime  (LITERAL: no residualControl, so SIMPLE always
    #     runs to endTime; this clause is meaningful and is NOT relaxed)
    times = sorted(
        (float(d) for d in os.listdir(level_dir)
         if re.fullmatch(r"\d+(\.\d+)?", d)
         and os.path.isdir(os.path.join(level_dir, d))))
    if not times:
        refuse("C3: no time directories in %s" % level_dir)
    if abs(times[-1] - float(endtime)) > 0:
        refuse("C3: last time %r != endTime %r in %s"
               % (times[-1], endtime, level_dir))
    notes.append("C3 last time == endTime OK")

    # C4  fields present at endTime -- THIS CASE'S OWN DECLARED LIST
    tdir = os.path.join(level_dir, str(endtime))
    if not os.path.isdir(tdir):
        tdir = os.path.join(level_dir, "%g" % float(endtime))
    for f in FIELDS_REQUIRED:
        if not os.path.isfile(os.path.join(tdir, f)):
            refuse("C4: field %r absent at endTime in %s" % (f, tdir))
    notes.append("C4 fields %s OK" % " ".join(FIELDS_REQUIRED))

    # C5  ExecutionTime count == endTime  (LITERAL: steady SIMPLE, one
    #     iteration = one time unit)
    nexec = len(re.findall(r"^ExecutionTime = ", log, re.M))
    if nexec != int(endtime):
        refuse("C5: %d 'ExecutionTime' lines but endTime = %s in %s"
               % (nexec, endtime, level_dir))
    notes.append("C5 ExecutionTime count == endTime OK")

    # C6  AGE GUARD, STRICTER THAN THE RULE.  The rule dates the run from the
    #     case's own 0/T; there is no T here, and this dates it from the LATEST
    #     mtime anywhere in the case's own 0/ -- run_vmfl003.sh touches EVERY
    #     file in 0/ as its last action before the solver starts.
    zerodir = os.path.join(level_dir, "0")
    if not os.path.isdir(zerodir):
        refuse("C6: no 0/ directory in %s -- the age guard has no datum" % level_dir)
    datum = max(os.path.getmtime(os.path.join(zerodir, f))
                for f in os.listdir(zerodir)
                if os.path.isfile(os.path.join(zerodir, f)))
    for f in FIELDS_REQUIRED:
        fp = os.path.join(tdir, f)
        if os.path.getmtime(fp) <= datum:
            refuse("C6 AGE GUARD: %s is NOT strictly newer than the case's own "
                   "0/ datum -- it was not produced by the run allowed to "
                   "produce this answer" % fp)
    notes.append("C6 age guard (strictest form) OK")
    return notes


def check_residuals(level_dir, solver_log="log.simpleFoam"):
    """Final INITIAL residual of p, Ux, k, epsilon each below RESID_TOL.

    Uy / Uz are PRINTED, not gated: on a wedge the radial and azimuthal
    momentum residual normalisation is degenerate in the fully developed
    region, so gating on them would be a hair trigger rather than a check.
    """
    log = open(os.path.join(level_dir, solver_log), errors="replace").read()
    pat = re.compile(
        r"Solving for (\w+), Initial residual = ([0-9.eE+-]+),")
    last = {}
    for name, val in pat.findall(log):
        last[name] = float(val)
    gated = ["p", "Ux", "k", "epsilon"]
    for g in gated:
        if g not in last:
            refuse("no 'Solving for %s' line in %s/%s" % (g, level_dir, solver_log))
    ok = all(last[g] < RESID_TOL for g in gated)
    return ok, last


def check_plateau(dp_pa_series):
    n = len(dp_pa_series)
    if n < 10:
        refuse("dp series has only %d rows -- too short for a plateau test" % n)
    w = max(2, int(round(PLATEAU_FRAC * n)))
    tail = [v for _, v in dp_pa_series[-w:]]
    ptp = max(tail) - min(tail)
    return ptp <= PTP_TOL, ptp, w


# ===========================================================================
# ROACHE (CLAUDE.md rule 5).  Returns a STATE.
# ===========================================================================
def roache(f_coarse, f_med, f_fine, r=RATIO, fs=FS,
           eps_abs=EPS_ABS, stag_tol=STAG_TOL):
    d32 = f_med - f_coarse
    d21 = f_fine - f_med
    out = {"f_coarse": f_coarse, "f_med": f_med, "f_fine": f_fine,
           "d32": d32, "d21": d21, "R": None, "p": None,
           "gci_fine": None, "f_extrap": None, "state": None,
           "monotone": None}

    if abs(d32) < eps_abs and abs(d21) < eps_abs:
        out["state"] = "EXACT"
        return out
    if abs(d32) < eps_abs:
        out["state"] = "DIVERGENT"
        return out

    R = d21 / d32
    out["R"] = R
    out["monotone"] = (d32 > 0 and d21 > 0) or (d32 < 0 and d21 < 0)

    if R < 0:
        out["state"] = "OSCILLATORY"
        return out
    if abs(R - 1.0) <= stag_tol:
        out["state"] = "STAGNANT"
        return out
    if R > 1.0:
        out["state"] = "DIVERGENT"
        return out

    out["state"] = "CONVERGING"
    p = math.log(1.0 / R) / math.log(r)
    out["p"] = p
    denom = r ** p - 1.0
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrap"] = f_fine + d21 / denom
    return out


# ===========================================================================
# PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  Both arms; refuse if blind.
# ===========================================================================
def _plant_last_row(src, dst, colname, amount):
    """Copy src -> dst adding `amount` to the last data row's named column."""
    meta, colnames, rows = _read_dat(src)
    ic = colnames.index(colname)
    lines = open(src).read().splitlines()
    # find the last non-comment, non-blank line
    idx = None
    for i in range(len(lines) - 1, -1, -1):
        s = lines[i]
        if s.strip() and not s.lstrip().startswith("#"):
            idx = i
            break
    if idx is None:
        refuse("plant: no data line in %s" % src)
    cells = lines[idx].split()
    cells[ic] = repr(float(cells[ic]) + amount)
    lines[idx] = "\t".join(cells)
    with open(dst, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def control_dp(inlet_dat, outlet_dat):
    """Control 1 -- and a LIVE test that the RHO conversion is applied.

    PLANT_DP is planted into the KINEMATIC inlet pressure column.  The graded
    value is in Pa, so it must move by exactly PLANT_DP * RHO.  A reader that
    forgot RHO would move by PLANT_DP and the control REFUSES.
    """
    base = dp_series_pa(inlet_dat, outlet_dat)[-1][1]
    with tempfile.TemporaryDirectory() as td:
        # negative arm: an unplanted copy must give the SAME value
        c_in = os.path.join(td, "in0.dat")
        c_out = os.path.join(td, "out0.dat")
        shutil.copyfile(inlet_dat, c_in)
        shutil.copyfile(outlet_dat, c_out)
        same = dp_series_pa(c_in, c_out)[-1][1]
        if abs(same - base) > PLANT_TOL:
            refuse("control 1 NEGATIVE ARM: an unplanted copy moved the answer "
                   "by %r Pa -- the reader is not deterministic" % (same - base))
        # positive arm
        p_in = os.path.join(td, "in1.dat")
        shutil.copyfile(outlet_dat, os.path.join(td, "out1.dat"))
        _plant_last_row(inlet_dat, p_in, "areaAverage(p)", PLANT_DP)
        planted = dp_series_pa(p_in, os.path.join(td, "out1.dat"))[-1][1]
    seen = planted - base
    want = PLANT_DP * RHO
    if abs(seen - want) > PLANT_TOL:
        refuse("control 1 REFUSES: planted %r m2/s2 of KINEMATIC pressure, "
               "expected the graded value to move by PLANT*RHO = %r Pa, saw %r "
               "-- the reader is either blind to the plant or is NOT applying "
               "the rho = %r conversion" % (PLANT_DP, want, seen, RHO))
    return {"planted_kinematic": PLANT_DP, "expected_pa": want, "seen_pa": seen,
            "base_pa": base}


def control_yplus(yplus_dat):
    base = read_yplus(yplus_dat)[-1][3]
    with tempfile.TemporaryDirectory() as td:
        c0 = os.path.join(td, "y0.dat")
        shutil.copyfile(yplus_dat, c0)
        if abs(read_yplus(c0)[-1][3] - base) > PLANT_TOL:
            refuse("control 2 NEGATIVE ARM: unplanted copy moved mean y+")
        c1 = os.path.join(td, "y1.dat")
        _plant_last_row(yplus_dat, c1, "average", PLANT_YPLUS)
        planted = read_yplus(c1)[-1][3]
    seen = planted - base
    if abs(seen - PLANT_YPLUS) > PLANT_TOL:
        refuse("control 2 REFUSES: planted %r into the yPlus average column, "
               "saw %r" % (PLANT_YPLUS, seen))
    return {"planted": PLANT_YPLUS, "seen": seen, "base": base}


def control_fdev(slabA_dat, slabB_dat):
    base, _ = f_dev_from_slabs(slabA_dat, slabB_dat)
    with tempfile.TemporaryDirectory() as td:
        a0 = os.path.join(td, "a0.dat")
        b0 = os.path.join(td, "b0.dat")
        shutil.copyfile(slabA_dat, a0)
        shutil.copyfile(slabB_dat, b0)
        if abs(f_dev_from_slabs(a0, b0)[0] - base) > PLANT_TOL:
            refuse("control 3 NEGATIVE ARM: unplanted copy moved f_dev")
        a1 = os.path.join(td, "a1.dat")
        _plant_last_row(slabA_dat, a1, "volAverage(p)", PLANT_SLAB)
        planted, _ = f_dev_from_slabs(a1, b0)
    seen = planted - base
    want = PLANT_SLAB * RHO * D_PIPE / (SLAB_DX * QDYN)
    if abs(seen - want) > PLANT_TOL:
        refuse("control 3 REFUSES: planted %r m2/s2 into slabA, expected f_dev "
               "to move by %r, saw %r" % (PLANT_SLAB, want, seen))
    return {"planted_kinematic": PLANT_SLAB, "expected": want, "seen": seen,
            "base": base}


# ===========================================================================
# THE GATE AND THE VERDICT (CLAUDE.md rule 5, IN ITS STATED ORDER)
# ===========================================================================
def gate_verdict(dp_pa):
    dev = (dp_pa - TARGET_DP_PA) / TARGET_DP_PA
    # M2 CEILING: in-band is GATE REACHED, never PASS -- grid convergence of
    # dp is structurally uncertifiable here (N-AV10), so no credential is
    # claimed.  Out-of-band is GATE FAIL, exactly as run 1.
    return ("GATE REACHED" if abs(dev) <= GATE_BAND else "GATE FAIL"), dev


def grade(runroot, write_json=None):
    res = {"case": "VMFL003_M2", "runroot": runroot,
           "tier_ceiling": "GATE REACHED", "holds_attainable": False,
           "target_dp_pa": TARGET_DP_PA, "gate_band": GATE_BAND,
           "levels": {}, "ladder": {}, "not_a_result_reasons": []}

    # ---- rule 5 step 1: PER LEVEL, BEFORE the triple is formed ------------
    dp_at_end = {}
    for name, nx, nr, cells, endt in LEVELS:
        ld = os.path.join(runroot, name)
        lv = {"nx": nx, "nr": nr, "cells": cells, "endTime": endt}
        lv["completion"] = check_completion(ld, endt)

        pp = os.path.join(ld, "postProcessing")
        f_in = os.path.join(pp, "pInletMonitor", "0", "surfaceFieldValue.dat")
        f_out = os.path.join(pp, "pOutletMonitor", "0", "surfaceFieldValue.dat")
        f_ya = os.path.join(pp, "yPlusWall", "0", "yPlus.dat")

        series = dp_series_pa(f_in, f_out)
        if abs(series[-1][0] - float(endt)) > 0:
            refuse("the last dp monitor row is at time %r, not endTime %r, in %s"
                   % (series[-1][0], endt, ld))
        dp_at_end[name] = series[-1][1]
        lv["dp_pa"] = series[-1][1]

        ok_r, resid = check_residuals(ld)
        lv["final_initial_residuals"] = resid
        lv["residuals_ok"] = ok_r
        if not ok_r:
            res["not_a_result_reasons"].append(
                "%s: final initial residuals not all below %g (%s)"
                % (name, RESID_TOL,
                   ", ".join("%s=%g" % (k, resid[k])
                             for k in ("p", "Ux", "k", "epsilon"))))

        ok_p, ptp, w = check_plateau(series)
        lv["plateau_ptp_pa"] = ptp
        lv["plateau_window"] = w
        lv["plateau_ok"] = ok_p
        if not ok_p:
            res["not_a_result_reasons"].append(
                "%s: dp not plateaued -- peak-to-peak %.6g Pa over the last "
                "%d iterations exceeds %g Pa" % (name, ptp, w, PTP_TOL))

        yrows = read_yplus(f_ya)
        yavg = yrows[-1][3]
        ymin = yrows[-1][1]
        lv["yplus"] = {"min": ymin, "max": yrows[-1][2],
                       "average": yavg, "predicted": YPLUS_PRED,
                       "min_floor": YPLUS_MIN_FLOOR}
        avg_ok = (YPLUS_LO <= yavg <= YPLUS_HI)
        min_ok = (ymin >= YPLUS_MIN_FLOOR)
        lv["yplus_ok"] = avg_ok and min_ok
        if not avg_ok:
            res["not_a_result_reasons"].append(
                "%s: mean wall y+ = %.6g is outside the frozen wall-function "
                "validity band [%g, %g] -- the wall function was applied outside "
                "the log layer" % (name, yavg, YPLUS_LO, YPLUS_HI))
        if not min_ok:
            res["not_a_result_reasons"].append(
                "%s: MINIMUM wall y+ = %.6g is below the yPlusLam log-law floor "
                "%g -- a wall face sits in the sublayer where the standard wall "
                "function is invalid" % (name, ymin, YPLUS_MIN_FLOOR))

        fA = os.path.join(pp, "pSlabA", "0", "volFieldValue.dat")
        fB = os.path.join(pp, "pSlabB", "0", "volFieldValue.dat")
        fdev, dpdx = f_dev_from_slabs(fA, fB)
        lv["f_dev"] = fdev
        lv["dpdx_pa_per_m"] = dpdx
        lv["f_dev_dev_vs_colebrook"] = (fdev - F_COLEBROOK) / F_COLEBROOK
        res["levels"][name] = lv

    # ---- planted-zero controls, on the FINEST level's REAL artifacts ------
    fine = LEVELS[-1][0]
    pf = os.path.join(runroot, fine, "postProcessing")
    res["controls"] = {
        "dp_and_rho": control_dp(
            os.path.join(pf, "pInletMonitor", "0", "surfaceFieldValue.dat"),
            os.path.join(pf, "pOutletMonitor", "0", "surfaceFieldValue.dat")),
        "yplus": control_yplus(
            os.path.join(pf, "yPlusWall", "0", "yPlus.dat")),
        "f_dev": control_fdev(
            os.path.join(pf, "pSlabA", "0", "volFieldValue.dat"),
            os.path.join(pf, "pSlabB", "0", "volFieldValue.dat")),
    }

    # ---- the wall-treatment sensitivity ladder (DIAGNOSTIC, one-way) ------
    lad = {}
    for name, nx, nr, cells, endt in LADDER:
        ld = os.path.join(runroot, name)
        if not os.path.isdir(ld):
            refuse("ladder level %s missing at %s -- the ladder is part of the "
                   "frozen protocol and the comparator does not grade without it"
                   % (name, ld))
        check_completion(ld, endt)
        p2 = os.path.join(ld, "postProcessing")
        s = dp_series_pa(
            os.path.join(p2, "pInletMonitor", "0", "surfaceFieldValue.dat"),
            os.path.join(p2, "pOutletMonitor", "0", "surfaceFieldValue.dat"))
        y = read_yplus(os.path.join(p2, "yPlusWall", "0", "yPlus.dat"))
        lad[name] = {"nr": nr, "dp_pa": s[-1][1], "yplus_avg": y[-1][3]}
    vals = [v["dp_pa"] for v in lad.values()]
    spread = (max(vals) - min(vals)) / (sum(vals) / len(vals))
    res["ladder"] = {"levels": lad, "spread_rel": spread,
                     "spread_max": LADDER_SPREAD_MAX}
    if spread > LADDER_SPREAD_MAX:
        res["not_a_result_reasons"].append(
            "wall-treatment ladder spread %.4g exceeds the frozen %.4g -- the "
            "answer is a property of the wall-cell placement, not of the case"
            % (spread, LADDER_SPREAD_MAX))

    # ---- rule 5 step 2: the Roache triple ---------------------------------
    tri = roache(dp_at_end[LEVELS[0][0]],
                 dp_at_end[LEVELS[1][0]],
                 dp_at_end[LEVELS[2][0]])
    res["roache"] = tri

    dp_fine = dp_at_end[LEVELS[2][0]]
    verdict, dev = gate_verdict(dp_fine)
    res["dp_fine_pa"] = dp_fine
    res["deviation_vs_target"] = dev
    res["deviation_vs_colebrook"] = (dp_fine - DP_COLEBROOK) / DP_COLEBROOK
    res["gate_verdict_before_rule5"] = verdict

    if res["not_a_result_reasons"]:
        res["verdict"] = "NOT A RESULT"
        res["gci_quoted"] = False
        res["roache"]["gci_fine"] = None      # NEVER quote a GCI here
        res["roache"]["f_extrap"] = None
    elif tri["state"] != "CONVERGING":
        res["verdict"] = "NOT A RESULT"
        res["gci_quoted"] = False
        res["not_a_result_reasons"].append(
            "grid triple is %s (R = %s), not CONVERGING" %
            (tri["state"], "n/a" if tri["R"] is None else "%.6g" % tri["R"]))
        res["roache"]["gci_fine"] = None
        res["roache"]["f_extrap"] = None
    else:
        res["verdict"] = verdict           # GATE REACHED (in-band) or GATE FAIL
        res["gci_quoted"] = True
        res["roache"]["gci_is_certification"] = False
        res["roache"]["gci_note"] = (
            "axial channel ONLY; NOT a discretisation-uncertainty certification "
            "-- the dominant radial/wall channel is unrefinable here (N-AV10, "
            "R+ = 408), so the ceiling is GATE REACHED, never PASS/HOLDS")
        if tri.get("p") is not None and not (0.5 <= tri["p"] <= 2.5):
            res["roache"]["order_untrusted"] = True
            res["roache"]["order_note"] = (
                "observed order %.4g is outside [0.5, 2.5]; it is extracted from "
                "near-noise-floor level differences and is NOT trusted as a "
                "convergence rate (run 1 got p = 3.64 from 7.8 ppm differences)"
                % tri["p"])

    # DIAGNOSTICS -- printed, never able to change the verdict above.
    res["diagnostics"] = {
        "dp_colebrook_pa": DP_COLEBROOK,
        "diag_band_dp": DIAG_BAND_DP,
        "dp_diag_met": abs(res["deviation_vs_colebrook"]) <= DIAG_BAND_DP,
        "f_colebrook": F_COLEBROOK,
        "f_dev_fine": res["levels"][fine]["f_dev"],
        "f_diag_met": abs(res["levels"][fine]["f_dev_dev_vs_colebrook"]) <= DIAG_BAND_F,
        "ansys_context": {k: {"pa": v,
                              "dev_vs_target": (v - TARGET_DP_PA) / TARGET_DP_PA}
                          for k, v in ANSYS_CONTEXT.items()},
    }

    if write_json:
        os.makedirs(os.path.dirname(write_json), exist_ok=True)
        with open(write_json, "w") as fh:
            json.dump(res, fh, indent=2, sort_keys=True)
    return res


# ===========================================================================
# SELFTEST -- ZERO COMPUTE.  Includes NEGATIVE CONTROLS THAT PROVE THE GATE
# CAN FAIL.
# ===========================================================================
def _fx_patch(path, series, faces=5, area=1.0e-8, col="areaAverage(p)"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("# Region type : patch inlet\n")
        fh.write("# Faces       : %d\n" % faces)
        fh.write("# Area        : %r\n" % area)
        fh.write("# Scale factor : 1\n")
        fh.write("# Time        \t%s\n" % col)
        for t, v in series:
            fh.write("%g\t%r\n" % (t, v))


def _fx_zone(path, series, cells=25, vol=1.0e-9, col="volAverage(p)"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("# Region       : cellZone slabA\n")
        fh.write("# Cells        : %d\n" % cells)
        fh.write("# Volume       : %r\n" % vol)
        fh.write("# Time        \t%s\n" % col)
        for t, v in series:
            fh.write("%g\t%r\n" % (t, v))


def _fx_yplus(path, rows, patch="walls"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("# y+ ()\n")
        fh.write("# Time        \tpatch\tmin\tmax\taverage\n")
        for t, mn, mx, av in rows:
            fh.write("%g\t%s\t%r\t%r\t%r\n" % (t, patch, mn, mx, av))


def selftest():
    checks = [0]
    fails = []

    def ck(cond, what):
        checks[0] += 1
        if not cond:
            fails.append(what)

    def refuses(fn, what):
        checks[0] += 1
        try:
            fn()
        except Refusal:
            return
        fails.append("expected a REFUSAL: " + what)

    # --- the frozen arithmetic reproduces the manual ----------------------
    ck(abs(RE - 13691.740248127866) < 1e-9, "Re")
    ck(abs(NU - 1.4607346938775508e-05) < 1e-20, "nu")
    ck(abs(QDYN - 1531.2500000000002) < 1e-9, "q")
    ck(abs(F_CHART * LOVERD * QDYN - 21743.750000000004) < 1e-6,
       "f=0.0284 reproduces the manual's printed target 21744")
    ck(abs(F_IMPLIED - TARGET_DP_PA / (LOVERD * QDYN)) < 1e-15, "f implied")
    ck(abs(F_COLEBROOK * LOVERD * QDYN - DP_COLEBROOK) < 1e-6, "Colebrook dp")
    ck(abs(32 * MU * L_PIPE * U_IN / D_PIPE ** 2 - DP_LAMINAR) < 1e-9,
       "laminar dp")
    ck(abs(0.316 * RE ** -0.25 * LOVERD * QDYN - DP_BLASIUS) < 1e-6,
       "Blasius dp")
    ck(abs(R_PLUS - R_PIPE * U_TAU / NU) < 1e-9, "R+")
    ck(abs(YPLUS_PRED - (R_PIPE / 5 / 2) * U_TAU / NU) < 1e-9, "y+ at NR=5")

    # --- THE GATE IS A BAR: NEGATIVE CONTROLS THAT MUST FAIL --------------
    ck(gate_verdict(TARGET_DP_PA)[0] == "GATE REACHED", "exact target reaches the gate")
    ck(gate_verdict(DP_COLEBROOK)[0] == "GATE REACHED", "Colebrook reaches the gate")
    ck(gate_verdict(DP_LAMINAR)[0] == "GATE FAIL",
       "NEGATIVE CONTROL: a LAMINAR treatment (3578.8 Pa, -83.54 %) must FAIL")
    ck(gate_verdict(0.0)[0] == "GATE FAIL",
       "NEGATIVE CONTROL: an inviscid / zero-shear answer must FAIL")
    ck(gate_verdict(DP_BLASIUS)[0] == "GATE FAIL",
       "NEGATIVE CONTROL: a Blasius-based answer (+2.86 %) must FAIL")
    ck(gate_verdict(TARGET_DP_PA * 1.026)[0] == "GATE FAIL", "+2.6 % fails")
    ck(gate_verdict(TARGET_DP_PA * 0.974)[0] == "GATE FAIL", "-2.6 % fails")
    ck(gate_verdict(TARGET_DP_PA * 1.024)[0] == "GATE REACHED", "+2.4 % reaches the gate")
    ck(gate_verdict(TARGET_DP_PA * 0.976)[0] == "GATE REACHED", "-2.4 % reaches the gate")
    # DECLARED before any compute: this band passes both Ansys solvers.
    ck(gate_verdict(ANSYS_CONTEXT["Fluent"])[0] == "GATE REACHED",
       "DECLARED: Fluent's own 21480 Pa (-1.214 %) reaches this band")
    ck(gate_verdict(ANSYS_CONTEXT["CFX"])[0] == "GATE REACHED",
       "DECLARED: CFX's own 21740 Pa (-0.018 %) reaches this band")
    ck(abs((ANSYS_CONTEXT["CFX"] / ANSYS_CONTEXT["Fluent"] - 1) - 0.01210428)
       < 1e-6, "the manual's own two k-epsilon codes differ by 1.2104 %")

    # --- ROACHE: all six states, and NO GCI unless CONVERGING -------------
    t = roache(10.0, 10.4, 10.5)
    ck(t["state"] == "CONVERGING", "CONVERGING state")
    ck(abs(t["p"] - math.log(4.0) / math.log(2.0)) < 1e-12, "p = 2 recovered")
    ck(t["gci_fine"] is not None, "GCI quoted when CONVERGING")
    ck(t["monotone"] is True, "monotone flag")
    for args, want in [((10.0, 10.4, 10.2), "OSCILLATORY"),
                       ((10.0, 10.4, 10.8), "STAGNANT"),
                       ((10.0, 10.4, 11.2), "DIVERGENT"),
                       ((10.0, 10.0, 10.0), "EXACT")]:
        tt = roache(*args)
        ck(tt["state"] == want, "%s state" % want)
        ck(tt["gci_fine"] is None,
           "NEGATIVE CONTROL: NO GCI is computed for a %s triple" % want)
        ck(tt["p"] is None, "no order for a %s triple" % want)
    ck(roache(10.0, 10.0, 10.4)["state"] == "DIVERGENT",
       "zero-then-nonzero increment is DIVERGENT, not a division by zero")

    # --- READERS on the REAL formats, and their refusal arms --------------
    with tempfile.TemporaryDirectory() as td:
        pin = os.path.join(td, "in", "surfaceFieldValue.dat")
        pout = os.path.join(td, "out", "surfaceFieldValue.dat")
        n = 100
        kin = [(float(i), 17750.0 + 5.0 * math.exp(-i / 10.0)) for i in range(n)]
        _fx_patch(pin, kin)
        _fx_patch(pout, [(float(i), 0.0) for i in range(n)])
        s = dp_series_pa(pin, pout)
        ck(abs(s[-1][1] - RHO * kin[-1][1]) < 1e-9,
           "RHO applied to the kinematic pressure difference")

        # zero-faces refusal
        pz = os.path.join(td, "z", "surfaceFieldValue.dat")
        _fx_patch(pz, kin, faces=0)
        refuses(lambda: read_patch_series(pz, "areaAverage(p)"),
                "a '# Faces : 0' patch must be refused, not averaged")
        # missing column-header refusal
        pn = os.path.join(td, "n", "surfaceFieldValue.dat")
        os.makedirs(os.path.dirname(pn), exist_ok=True)
        open(pn, "w").write("# Faces : 5\n0\t1.0\n")
        refuses(lambda: read_series(pn, "areaAverage(p)"),
                "a file with no '# Time ...' header line must be refused, "
                "never read by column position")
        # wrong column name refusal
        refuses(lambda: read_series(pin, "areaAverage(T)"),
                "a column that is not in the header must be refused")

        za = os.path.join(td, "sa", "volFieldValue.dat")
        zb = os.path.join(td, "sb", "volFieldValue.dat")
        pA_kin = 8000.0
        pB_kin = 8000.0 - (F_COLEBROOK * QDYN / D_PIPE) * SLAB_DX / RHO
        _fx_zone(za, [(float(i), pA_kin) for i in range(n)])
        _fx_zone(zb, [(float(i), pB_kin) for i in range(n)], cells=25)
        fdev, _ = f_dev_from_slabs(za, zb)
        ck(abs(fdev - F_COLEBROOK) < 1e-12,
           "f_dev round-trips the Colebrook friction factor exactly")
        zz = os.path.join(td, "sz", "volFieldValue.dat")
        _fx_zone(zz, [(0.0, 1.0)], cells=0)
        refuses(lambda: read_zone_series(zz, "volAverage(p)"),
                "an EMPTY cellZone ('# Cells : 0') must be refused")

        yp = os.path.join(td, "y", "yPlus.dat")
        _fx_yplus(yp, [(float(i), 30.0, 55.0, YPLUS_PRED) for i in range(n)])
        ck(abs(read_yplus(yp)[-1][3] - YPLUS_PRED) < 1e-12, "yPlus reader")
        refuses(lambda: read_yplus(yp, patch="nosuch"),
                "a yPlus file with no rows for the requested patch")

        # --- THE THREE PLANTED-ZERO CONTROLS, BOTH ARMS -------------------
        c1 = control_dp(pin, pout)
        ck(abs(c1["seen_pa"] - PLANT_DP * RHO) < PLANT_TOL,
           "control 1: plant seen as PLANT*RHO")
        c2 = control_yplus(yp)
        ck(abs(c2["seen"] - PLANT_YPLUS) < PLANT_TOL, "control 2: plant seen")
        c3 = control_fdev(za, zb)
        ck(abs(c3["seen"] - PLANT_SLAB * RHO * D_PIPE / (SLAB_DX * QDYN))
           < PLANT_TOL, "control 3: plant seen")

        # NEGATIVE ARM OF CONTROL 1: a reader that forgets RHO must be caught.
        def _blind():
            base = kin[-1][1]
            planted = base + PLANT_DP
            seen = planted - base                 # 1.234, NOT 1.234*RHO
            if abs(seen - PLANT_DP * RHO) > PLANT_TOL:
                refuse("a rho-blind reader is caught by control 1")
        refuses(_blind,
                "NEGATIVE CONTROL: a reader that omits the rho conversion must "
                "be REFUSED by planted-zero control 1")

        # --- PLATEAU ------------------------------------------------------
        flat = [(float(i), 21700.0) for i in range(100)]
        ok, ptp, w = check_plateau(flat)
        ck(ok and ptp == 0.0 and w == 20, "a flat series plateaus")
        drift = [(float(i), 21700.0 + 0.5 * i) for i in range(100)]
        ok2, ptp2, _ = check_plateau(drift)
        ck(not ok2 and ptp2 > PTP_TOL,
           "NEGATIVE CONTROL: a drifting series must FAIL the plateau clause")
        refuses(lambda: check_plateau([(0.0, 1.0)] * 3),
                "too short a series must be refused, not plateaued")

    # --- the y+ validity band is a real one-way bar -----------------------
    ck(not (YPLUS_LO <= 12.7 <= YPLUS_HI),
       "NEGATIVE CONTROL: NR=16 (y+ 12.7, buffer layer) is outside the band")
    ck(not (YPLUS_LO <= 102.09 <= YPLUS_HI),
       "NEGATIVE CONTROL: NR=2 (y+ 102, wake region) is outside the band")
    ck(YPLUS_LO <= YPLUS_PRED <= YPLUS_HI, "the frozen NR=5 mesh is inside it")
    ck(YPLUS_LO <= 34.03 <= YPLUS_HI and YPLUS_LO <= 51.04 <= YPLUS_HI,
       "the ladder's NR=6 and NR=4 are inside it")

    # --- the y+ MINIMUM floor is a real one-way bar (M2 addition) ----------
    ck(abs(YPLUS_MIN_FLOOR - 11.06) < 1e-12, "yPlusLam floor is 11.06")
    ck(23.812 >= YPLUS_MIN_FLOOR,
       "run-1 L3 min y+ 23.812 CLEARS the floor -- the min clause is a\n       tightening that would have HELD in run 1, not an answer-fitted band")
    ck(not (10.0 >= YPLUS_MIN_FLOOR),
       "NEGATIVE CONTROL: a face at y+ = 10 (sublayer) is below the floor\n       and would be caught")

    # --- the wedge / N-AV9 arithmetic this case declares -------------------
    a = math.radians(2.5)
    ck(abs((1 - math.sin(2 * a) / (2 * a)) * 100 - 0.1268756046250763) < 1e-12,
       "N-AV9 area deficit 0.1268756 % reproduced")
    ck(abs((1 / math.cos(a) - 1) * 100 - 0.09526851633199218) < 1e-12,
       "the dp bias of a 5 deg wedge is sec(2.5 deg) - 1 = +0.0952685 %")

    print("VMFL003-M2 comparator --selftest: %d checks, %d failures"
          % (checks[0], len(fails)))
    for f in fails:
        print("  FAILED: " + f)
    return 0 if not fails else 1


# ===========================================================================
# FROZEN-FILE VERIFICATION AND THE STRUCTURE-ONLY READER DRYRUN
# ===========================================================================
def verify_frozen(commit):
    here = os.path.abspath(__file__)
    mine = hashlib.sha1()
    data = open(here, "rb").read()
    mine.update(b"blob %d\x00" % len(data))
    mine.update(data)
    rel = "cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py"
    try:
        # THE CLASS FIX (supervisor ruling 2): derive the repo root robustly with
        # `git rev-parse --show-toplevel` from THIS FILE's own directory, not by
        # counting dirnames up from __file__ (run-1's latent fault).
        toplevel = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=os.path.dirname(here), text=True).strip()
        want = subprocess.check_output(
            ["git", "rev-parse", "%s:%s" % (commit, rel)],
            cwd=toplevel, text=True).strip()
    except Exception as e:
        refuse("cannot read the committed blob for %s at %s: %s"
               % (rel, commit, e))
    if mine.hexdigest() != want:
        refuse("THE GRADING PATH IS NOT THE FROZEN FILE: on-disk blob %s != "
               "committed %s at %s" % (mine.hexdigest(), want, commit))
    print("frozen-file check OK: %s == %s:%s" % (mine.hexdigest(), commit, rel))
    return 0


def dryrun_reader(path):
    """Print STRUCTURE ONLY.  Never a value (the L-286 check)."""
    meta, colnames, rows = _read_dat(path)
    print("path        : %s" % path)
    print("header keys : %s" % sorted(meta.keys()))
    print("columns     : %s" % colnames)
    print("data rows   : %d" % len(rows))
    print("cells/row   : %s" % sorted({len(r) for r in rows}))
    print("(no values printed, by design)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="VMFL003 comparator")
    ap.add_argument("--runroot", default=RUNROOT_DEFAULT)
    ap.add_argument("--json", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-frozen", default=None)
    ap.add_argument("--dryrun-reader", default=None)
    args = ap.parse_args()

    try:
        if args.selftest:
            return selftest()
        if args.verify_frozen:
            return verify_frozen(args.verify_frozen)
        if args.dryrun_reader:
            return dryrun_reader(args.dryrun_reader)
        res = grade(args.runroot, args.json)
    except Refusal as e:
        sys.stderr.write("REFUSED (exit 2): %s\n" % e)
        return 2

    print(json.dumps(res, indent=2, sort_keys=True))
    print()
    print("VERDICT: %s" % res["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
