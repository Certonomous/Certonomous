#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL036 -- Laminar Flow Past Sphere.  THE COMPARATOR.

FROZEN AT THE PRE-REGISTRATION COMMIT.  NO THRESHOLD, BAND, REFERENCE VALUE, AREF
OR PLANT CONSTANT IN THIS FILE IS SETTABLE FROM THE COMMAND LINE OR THE
ENVIRONMENT.  The grading path is fixed at the pre-registration commit (CLAUDE.md
rule 2) and run_vmfl036.sh verifies at launch that the copy on disk hashes equal to
HEAD's blob.

  python3 grade_vmfl036.py --selftest     # every control + classifier, ZERO compute
  python3 grade_vmfl036.py                # grade both arms from the run directories

TWO ARMS, both frozen before any compute, per the supervisor's committed pre-freeze
physics check (cases/ansys_verification/VMFL036/SUPERVISOR_PREFREEZE_CHECK.md,
blob e451ca401c1c2502d1b062f4901487dcb7e2725e):

  ARM A -- THE GATE.  nu = 0.01  ->  Re = rho*U*D/mu = 100.  Gate on the manual's
           target Cd = 1.0895.  Three-level Roache family, r = 2, GCI at Fs = 1.25.
  ARM B -- A DISCLOSED DIAGNOSTIC ABOUT THE MANUAL, NOT A GATE ON THIS SOLVER.
           nu = 0.02 EXACTLY as the manual's page states  ->  Re = 50.  The
           prediction Cd ~ 1.538 (Schiller-Naumann at Re = 50) is registered BEFORE
           the run.  Arm B landing near 1.538 and far from 1.0895 is positive
           evidence that the manual's viscosity is the error and not this lab's
           solver.  Arm B CANNOT produce a verdict on the solver and never scores.
"""

import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polymesh_area  # noqa: E402   (frozen alongside this file, same commit)

RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL036"

# ===========================================================================
# 1.  THE CASE, AS THE MANUAL STATES IT (p.125-126).  Nothing here is inferred.
# ===========================================================================
RHO = 1.0            # kg/m3            manual p.125
U_INF = 1.0          # m/s              manual p.125
D_SPHERE = 1.0       # m                manual p.125
MU_MANUAL = 0.02     # kg/m-s           manual p.125  -> Re = 50   (ARM B)
MU_ARM_A = 0.01      # kg/m-s           the repair    -> Re = 100  (ARM A)
R_FARFIELD = 50.0    # radii of D       manual p.125 "radius of 50 D"

RE_ARM_A = RHO * U_INF * D_SPHERE / MU_ARM_A       # 100.0
RE_ARM_B = RHO * U_INF * D_SPHERE / MU_MANUAL      # 50.0

# The manual's printed target.  ARM A's gate; ARM B's DISCRIMINATOR.
REF_CD = 1.0895                                    # manual Table .36.1
ANSYS_FLUENT_CD = 1.0875                           # CONTEXT ONLY -- never a gate

# ===========================================================================
# 2.  THE GATE AND THE BANDS.  Frozen before any compute; justified in
#     PREREGISTRATION.md line 6 from the manual's own acceptance practice, NEVER
#     from a first run.
# ===========================================================================
TOL_A = 0.03          # ARM A: |Cd_lab - 1.0895| / 1.0895 <= 0.03 at the FINEST level

# ARM B's registered prediction: Schiller-Naumann at Re = 50.
def schiller_naumann(re):
    """Cd(Re) = (24/Re) * (1 + 0.15 * Re^0.687).  A CORRELATION: buys V, never P."""
    return (24.0 / re) * (1.0 + 0.15 * re ** 0.687)

CD_SN_50 = schiller_naumann(RE_ARM_B)     # ~1.5381
CD_SN_100 = schiller_naumann(RE_ARM_A)    # ~1.0917
TOL_B_PREDICTION = 0.10   # Schiller-Naumann is a fit to scattered data; 10% is the
                          # honest band for agreement WITH A CORRELATION.
TOL_B_DISCRIMINATOR = 0.25  # ARM B must land at least 25% away from 1.0895 for the
                            # manual-typo reading to be positively supported.

# ===========================================================================
# 3.  THE REFERENCE AREA -- MEASURED-CONSISTENT, and the residual azimuthal bias
#     CARRIED, NOT ASSUMED ZERO (charter v1.4 / N-AV9).
#
#     The wedge maps a half-plane point (x, y) to (x, y*cos(a), +/- y*sin(a)),
#     a = 2.5 deg.  Two DIFFERENT azimuthal factors follow, and they are not the
#     same number -- which is exactly the charter's warning that the wedge term is
#     case-shaped:
#
#       WETTED area of the sector  ->  factor sin(a)/a      (chord vs arc)
#       FRONTAL PROJECTED area     ->  factor sin(a)cos(a)/a
#
#     because the projection onto the y-z plane picks up the extra cos(a) from
#     y = r*sin(theta)*cos(a).  Integrating the strip projection analytically:
#
#       A_proj = INT_0^{pi/2} 2 R sin(th) sin(a) * R cos(th) cos(a) dth
#              = R^2 sin(a) cos(a)  =  D^2 sin(a) cos(a) / 4
#
#     and polymesh_area.py reads exactly that off the L1 mesh to 1 part in 1e8.
#     AREF is therefore D^2 sin(a) cos(a)/4, which makes the PRESSURE part of the
#     drag azimuthally exact.  The VISCOUS part carries the wetted-area factor
#     instead, so it is left biased by 1/cos(a).  The two limiting normalisations
#     bracket the truth and differ by exactly cos(a):
#
#       AZIMUTHAL BIAS BRACKET = 1 - cos(2.5 deg) = 9.518e-04  (0.0952% of Cd)
#
#     The gate is taken on the AREF below; the other normalisation is PRINTED
#     beside it as the disclosed bracket.  Half-width 0.0476% of Cd -- two orders
#     under the 3% band, and NEVER silently dropped.
# ===========================================================================
WEDGE_HALF_ANGLE_DEG = 2.5
SIN_ALPHA = math.sin(math.radians(WEDGE_HALF_ANGLE_DEG))
COS_ALPHA = math.cos(math.radians(WEDGE_HALF_ANGLE_DEG))
AREF = D_SPHERE ** 2 * SIN_ALPHA * COS_ALPHA / 4.0   # frontal projected area
AREF_WETTED_FORM = D_SPHERE ** 2 * SIN_ALPHA / 4.0   # the other limit (disclosed)
AWET_ANALYTIC = D_SPHERE ** 2 * SIN_ALPHA            # wetted area of the sector
AZIMUTHAL_BIAS_BRACKET = 1.0 - COS_ALPHA             # 9.518e-04
Q_INF = 0.5 * RHO * U_INF ** 2                       # dynamic pressure

# Mesh birth certificate (MESH_STANDARD sec.6).
# The WETTED-area check is a GROSS-ERROR trap: theta-faceting can only make it
# smaller, and never by more than ~0.1% at L1.
AWET_BAND = (0.99, 1.001)
# The PROJECTED-area check is TIGHT, because the projection telescopes on the
# exact sphere endpoints and is therefore mesh-independent to round-off.  This is
# the check that actually proves the frozen AREF matches the mesh that ran.
APROJ_BAND = (0.9999, 1.0001)
TAN_ALPHA_TOL = 1e-6      # max|z|/max|y| on the mesh vs tan(2.5 deg)

# ===========================================================================
# 4.  THE LADDER.  r = 2 BY CONSTRUCTION: every level doubles NT and NR under the
#     SAME frozen radial stretching map (K = 400), so h halves EXACTLY.
# ===========================================================================
K_STRETCH = 400.0
LEVELS = [("L1_32x48", 32, 48), ("L2_64x96", 64, 96), ("L3_128x192", 128, 192)]
ENDTIME = 10000           # SIMPLE iterations, IDENTICAL at every level
RATIO = 2.0
FS = 1.25
REQUIRED_FIELDS = ["U", "p"]

# Iterative convergence (rule 5 step 1).  Not converged => NOT A RESULT.
RESID_MAX = 1.0e-6        # final-iteration INITIAL residual, p and U
PLATEAU_FRAC = 0.2        # last 20% of the Cd series
PLATEAU_PTP_REL = 1.0e-5  # peak-to-peak of Cd over that window, relative

# Roache classifier thresholds (semantics identical to VMFL045/VMFL051/VMFL005).
EPS_ABS = 1.0e-12
STAG_TOL = 1.0e-3

# ===========================================================================
# 5.  PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  None is optional.  A zero from a
#     reader not shown able to see a non-zero is not evidence.
# ===========================================================================
PLANT_FORCE = 7.7e-03     # N, planted into a COPY of force.dat's total_x
PLANT_FORCE_TOL = 1e-12
PLANT_SCALE = 2.0         # points of a COPY of the mesh scaled -> area must go x4
PLANT_SCALE_TOL = 1e-9


class Refusal(Exception):
    pass


def refuse(code, msg):
    raise Refusal("REFUSE[%s]: %s" % (code, msg))


# ===========================================================================
# force.dat reader.  Column layout is taken from the FILE'S OWN header line, never
# assumed positionally; the reader REFUSES if it cannot find total_x.
# ===========================================================================
def read_force_dat(path):
    if not os.path.isfile(path):
        refuse("F1", "no force.dat at %s" % path)
    cols = None
    rows = []
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            body = s.lstrip("#").strip()
            if "total_x" in body and body.split()[0].lower().startswith("time"):
                cols = body.replace("\t", " ").split()
            continue
        if cols is None:
            refuse("F2", "%s has data rows before any column header naming total_x "
                         "-- the reader will not guess a column layout" % path)
        parts = s.replace("\t", " ").split()
        if len(parts) != len(cols):
            refuse("F3", "%s: row has %d fields against %d header names"
                         % (path, len(parts), len(cols)))
        try:
            rows.append([float(t) for t in parts])
        except ValueError:
            refuse("F3", "%s: non-numeric field in a data row" % path)
    if cols is None:
        refuse("F2", "%s: no column header naming total_x was found" % path)
    if not rows:
        refuse("F4", "%s: header found but ZERO data rows" % path)
    if "total_x" not in cols:
        refuse("F2", "%s: header has no total_x column" % path)
    it = cols.index(cols[0])
    ix = cols.index("total_x")
    return {"cols": cols, "rows": rows, "i_time": it, "i_fx": ix,
            "time": [r[it] for r in rows], "fx": [r[ix] for r in rows]}


def cd_from_fx(fx):
    return fx / (Q_INF * AREF)


def plant_into_force_dat(src, dst, value):
    """Rewrite EVERY data row's total_x to `value`, leaving the header untouched."""
    cols = None
    out = []
    for line in open(src):
        s = line.rstrip("\n")
        t = s.strip()
        if t.startswith("#"):
            body = t.lstrip("#").strip()
            if "total_x" in body and body.split()[0].lower().startswith("time"):
                cols = body.replace("\t", " ").split()
            out.append(s)
            continue
        if not t:
            out.append(s)
            continue
        parts = t.replace("\t", " ").split()
        parts[cols.index("total_x")] = "%.8e" % value
        out.append(" ".join(parts))
    open(dst, "w").write("\n".join(out) + "\n")
    return cols


# ===========================================================================
# Roache triple (CLAUDE.md rule 5).
# ===========================================================================
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine, d21=d21, d32=d32,
               ratio=ratio, fs=fs, p=None, R=None, gci_fine=None,
               f_extrapolated=None, why=None)
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
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"
        out["why"] = "r^p - 1 <= 0"
        return out
    out["state"] = "CONVERGING"
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


# ===========================================================================
# Strict completion (CLAUDE.md rule 4).  NO DEPARTURE IS DECLARED FOR THIS CASE:
# simpleFoam runs a FIXED iteration count with residualControl deliberately absent,
# so every clause is checked LITERALLY.
# ===========================================================================
def _time_dirs(level_dir):
    out = []
    for n in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, n)):
            try:
                out.append((float(n), n))
            except ValueError:
                pass
    return sorted(out)


def completion_check(level_dir):
    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("C1", "no RUN_RC.txt in %s -- the run's own exit code is not on disk"
                     % level_dir)
    rcd = dict(re.findall(r"(\w+)=(.*)", open(rc_path).read()))
    if int(rcd.get("rc", "1")) != 0:
        refuse("C1", "%s records rc=%s -- a non-zero exit is a finding, triage it"
                     % (rc_path, rcd.get("rc")))

    log = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.isfile(log):
        refuse("C2", "no log.simpleFoam in %s" % level_dir)
    log_lines = open(log, errors="replace").read().split("\n")
    if not any(l.strip() == "End" for l in log_lines):
        refuse("C2", "no 'End' line in %s" % log)

    times = _time_dirs(level_dir)
    if not times:
        refuse("C3", "no time directories in %s" % level_dir)
    t_last, t_last_name = times[-1]
    if abs(t_last - ENDTIME) > 1e-9:
        refuse("C3", "last time %g is not endTime %d in %s (rule 4 is checked "
                     "LITERALLY here -- no departure is declared for this case)"
                     % (t_last, ENDTIME, level_dir))

    log_times = [float(l.split("=", 1)[1]) for l in log_lines
                 if l.startswith("Time = ")]
    if not log_times:
        refuse("C5", "no 'Time = ' lines in %s" % log)
    if abs(log_times[-1] - t_last) > 1e-12 * max(1.0, abs(t_last)):
        refuse("C3", "the log's final Time = %g does not match the last time "
                     "directory %s" % (log_times[-1], t_last_name))

    n_exec = sum(1 for l in log_lines if l.startswith("ExecutionTime = "))
    if n_exec != ENDTIME:
        refuse("C5", "ExecutionTime count is %d against endTime %d in %s -- rule 4's "
                     "count clause, checked literally" % (n_exec, ENDTIME, log))

    for f in REQUIRED_FIELDS:
        p = os.path.join(level_dir, t_last_name, f)
        if not os.path.isfile(p):
            refuse("C4", "field %s missing at endTime in %s" % (f, level_dir))

    zero_dir = os.path.join(level_dir, "0")
    if not os.path.isdir(zero_dir):
        refuse("C6", "no 0/ in %s -- the age guard has no datum" % level_dir)
    m0 = max(os.path.getmtime(os.path.join(zero_dir, f))
             for f in os.listdir(zero_dir)
             if os.path.isfile(os.path.join(zero_dir, f)))
    for f in REQUIRED_FIELDS:
        p = os.path.join(level_dir, t_last_name, f)
        if os.path.getmtime(p) <= m0:
            refuse("C6", "AGE GUARD: %s is not newer than the newest file in %s -- "
                         "this field was not produced by the run that was allowed to "
                         "answer" % (p, zero_dir))

    # iterative convergence, rule 5 step 1
    resid = {}
    for l in log_lines:
        m = re.search(r"Solving for (\w+), Initial residual = ([-\d.eE+]+)", l)
        if m:
            resid[m.group(1)] = float(m.group(2))
    for k in ("Ux", "Uy", "p"):
        if k not in resid:
            refuse("C7", "no '%s' residual line in %s" % (k, log))
    worst = max(resid[k] for k in ("Ux", "Uy", "p"))

    return {"rc": 0, "endtime_dir": t_last_name, "n_steps": len(log_times),
            "final_residuals": {k: resid[k] for k in ("Ux", "Uy", "p")},
            "worst_residual": worst,
            "iteratively_converged": worst <= RESID_MAX,
            "wall_s": float(rcd.get("wall_s", "nan")),
            "core_min": float(rcd.get("core_min", "nan")),
            "ranks": int(rcd.get("ranks", "1")),
            "nu": rcd.get("nu", "?")}


def plateau(series, frac=PLATEAU_FRAC):
    k = max(2, int(len(series) * frac))
    w = series[-k:]
    return max(w) - min(w), k


# ===========================================================================
# Mesh birth certificate (MESH_STANDARD sec.6) -- read from the mesh, not the log.
# ===========================================================================
def mesh_certificate(level_dir):
    md = os.path.join(level_dir, "constant", "polyMesh")
    if not os.path.isdir(md):
        refuse("M1", "no constant/polyMesh in %s" % level_dir)
    areas = polymesh_area.patch_areas(md)
    for need, want in (("sphere", "wall"), ("farField", "patch"),
                       ("axis", "empty"), ("front", "wedge"), ("back", "wedge")):
        if need not in areas:
            refuse("M2", "%s: patch %s is absent from the mesh" % (level_dir, need))
        if areas[need]["type"] != want:
            refuse("M2", "%s: patch %s has type %s, expected %s"
                         % (level_dir, need, areas[need]["type"], want))
    # blockMesh DISCARDS the fully collapsed axis faces, so nFaces is 0 and the
    # area is 0.0 -- both are the required outcome, and a NON-zero area would mean
    # the axis did not collapse.
    if areas["axis"]["area"] != 0.0:
        refuse("M3", "%s: the axis patch has NON-zero area %g -- it must be the "
                     "collapsed wedge axis" % (level_dir, areas["axis"]["area"]))
    ratio = areas["sphere"]["area"] / AWET_ANALYTIC
    if not (AWET_BAND[0] <= ratio <= AWET_BAND[1]):
        refuse("M4", "%s: the sphere patch's wetted area is %.10g, a ratio of %.6f "
                     "to the analytic wedge-sector area %.10g -- outside the frozen "
                     "gross-error band %s.  Aref cannot be trusted on this mesh."
                     % (level_dir, areas["sphere"]["area"], ratio, AWET_ANALYTIC,
                        AWET_BAND))
    aproj = areas["sphere"]["proj_x_pos"]
    pratio = aproj / AREF
    if not (APROJ_BAND[0] <= pratio <= APROJ_BAND[1]):
        refuse("M6", "%s: the sphere patch's FRONTAL PROJECTED area is %.12g, a "
                     "ratio of %.9f to the frozen AREF %.12g -- outside the frozen "
                     "band %s.  The gate quantity's denominator is not the mesh "
                     "that ran." % (level_dir, aproj, pratio, AREF, APROJ_BAND))
    pts = polymesh_area.read_points(md)
    maxy = max(p[1] for p in pts)
    maxz = max(abs(p[2]) for p in pts)
    tan_meas = maxz / maxy
    tan_want = math.tan(math.radians(WEDGE_HALF_ANGLE_DEG))
    if abs(tan_meas - tan_want) > TAN_ALPHA_TOL:
        refuse("M5", "%s: the mesh's half-angle is atan(%.10g) = %.6f deg, not the "
                     "frozen %.4f deg" % (level_dir, tan_meas,
                                          math.degrees(math.atan(tan_meas)),
                                          WEDGE_HALF_ANGLE_DEG))
    return {"sphere_area": areas["sphere"]["area"],
            "sphere_area_ratio": ratio,
            "sphere_proj_ratio": pratio,
            "sphere_proj_x": areas["sphere"]["proj_x_pos"],
            "sphere_nFaces": areas["sphere"]["nFaces"],
            "axis_nFaces": areas["axis"]["nFaces"],
            "half_angle_deg": math.degrees(math.atan(tan_meas))}


def read_level(arm, name):
    d = os.path.join(RUN_ROOT, arm, name)
    if not os.path.isdir(d):
        refuse("L0", "level directory %s does not exist" % d)
    comp = completion_check(d)
    cert = mesh_certificate(d)
    fdat = os.path.join(d, "postProcessing", "forces", "0", "force.dat")
    f = read_force_dat(fdat)
    cds = [cd_from_fx(v) for v in f["fx"]]
    if abs(f["time"][-1] - ENDTIME) > 1e-9:
        refuse("F5", "%s: the force series ends at %g, not endTime %d"
                     % (fdat, f["time"][-1], ENDTIME))
    ptp, k = plateau(cds)
    cd = cds[-1]
    return {"dir": d, "force_dat": fdat, "completion": comp, "mesh": cert,
            "Cd": cd, "Fx": f["fx"][-1], "n_rows": len(cds),
            "plateau_ptp": ptp, "plateau_rows": k,
            "plateau_ok": abs(ptp / cd) <= PLATEAU_PTP_REL if cd else False}


# ===========================================================================
# Planted-zero controls -- run against the REAL artifacts of a real level.
# ===========================================================================
def control_force_plant(level):
    src = level["force_dat"]
    tmp = tempfile.mkdtemp(prefix="vmfl036_plant_")
    try:
        base = read_force_dat(src)["fx"][-1]
        unplanted = os.path.join(tmp, "force_unplanted.dat")
        shutil.copy(src, unplanted)
        if abs(read_force_dat(unplanted)["fx"][-1] - base) > PLANT_FORCE_TOL:
            refuse("P0", "the UNPLANTED copy of %s does not read back as itself"
                         % src)
        planted = os.path.join(tmp, "force_planted.dat")
        plant_into_force_dat(src, planted, PLANT_FORCE)
        seen = read_force_dat(planted)["fx"][-1]
        if abs(seen - PLANT_FORCE) > PLANT_FORCE_TOL:
            refuse("P1", "PLANTED-ZERO CONTROL FAILED: total_x = %g was planted into "
                         "a copy of %s and the reader saw %g (delta %g).  This reader "
                         "has NOT been shown able to see a NON-ZERO force, so no zero "
                         "or any other value it reports is evidence (rule 3)."
                         % (PLANT_FORCE, src, seen, seen - PLANT_FORCE))
        return {"plant": PLANT_FORCE, "seen": seen, "base": base,
                "cd_of_plant": cd_from_fx(seen), "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_mesh_plant(level):
    md = os.path.join(level["dir"], "constant", "polyMesh")
    tmp = tempfile.mkdtemp(prefix="vmfl036_mplant_")
    try:
        dst = os.path.join(tmp, "polyMesh")
        os.makedirs(dst)
        for f in ("points", "faces", "boundary"):
            shutil.copy(os.path.join(md, f), dst)
        a0 = polymesh_area.patch_areas(dst)["sphere"]["area"]
        if abs(a0 - level["mesh"]["sphere_area"]) > PLANT_SCALE_TOL:
            refuse("P2", "the UNPLANTED copy of the mesh does not read back as itself")
        # plant: scale every point by PLANT_SCALE -> every area must go by ^2
        txt = open(os.path.join(dst, "points")).read()
        head, sep, rest = txt.partition("(\n")
        def scale(m):
            return "(%.12g %.12g %.12g)" % tuple(
                PLANT_SCALE * float(x) for x in m.groups())
        rest = re.sub(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
                      scale, rest)
        open(os.path.join(dst, "points"), "w").write(head + sep + rest)
        a1 = polymesh_area.patch_areas(dst)["sphere"]["area"]
        want = a0 * PLANT_SCALE ** 2
        if abs(a1 - want) > PLANT_SCALE_TOL * max(1.0, want):
            refuse("P3", "PLANTED-ZERO CONTROL FAILED: the mesh reader was handed a "
                         "copy with every point scaled by %g and reported area %.10g "
                         "where %.10g was required.  The geometry reader has NOT been "
                         "shown able to see a changed geometry, so its area -- and "
                         "therefore the Aref check -- is not evidence (rule 3)."
                         % (PLANT_SCALE, a1, want))
        return {"scale": PLANT_SCALE, "area_before": a0, "area_after": a1,
                "required": want, "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_roache_classifier():
    """The classifier must be shown able to see EACH state, not just CONVERGING.
    A gate that only ever returns one label is not a gate (rule 3's principle
    applied to a classifier rather than to a reader)."""
    seen = {}
    # CONVERGING: f = f_ex + C*h^2 with r = 2 -> d21/d32 = 1/4, p = 2 exactly.
    seen["CONVERGING"] = roache(1.0 + 4.0, 1.0 + 1.0, 1.0 + 0.25)
    seen["DIVERGENT"] = roache(1.0 + 0.25, 1.0 + 1.0, 1.0 + 4.0)
    seen["OSCILLATORY"] = roache(1.0 + 1.0, 1.0 - 1.0, 1.0 + 0.25)
    seen["STAGNANT"] = roache(3.0, 2.0, 1.0)
    seen["EXACT"] = roache(2.0, 2.0, 2.0)
    for want, got in seen.items():
        if got["state"] != want:
            refuse("R1", "ROACHE CLASSIFIER CONTROL FAILED: a triple constructed to "
                         "be %s was classified %s.  A classifier not shown able to "
                         "see every state cannot be trusted to have seen the state "
                         "it reports." % (want, got["state"]))
    p = seen["CONVERGING"]["p"]
    if abs(p - 2.0) > 1e-9:
        refuse("R2", "ROACHE CONTROL FAILED: an exactly-second-order triple gave "
                     "observed order %.12g, not 2" % p)
    # GCI on that triple: Fs*|d21/f_fine|/(r^p - 1) = 1.25*(0.75/1.25)/3
    want_gci = FS * abs(0.75 / 1.25) / (2.0 ** 2 - 1.0)
    if abs(seen["CONVERGING"]["gci_fine"] - want_gci) > 1e-12:
        refuse("R3", "ROACHE CONTROL FAILED: GCI %.12g against required %.12g"
                     % (seen["CONVERGING"]["gci_fine"], want_gci))
    return {k: v["state"] for k, v in seen.items()}


def control_geometry_identity():
    """AREF is an ANALYTIC number in this file.  The control proves the analytic
    form and an INDEPENDENT numerical quadrature of the same integral agree, so a
    typo in the closed form cannot pass unseen."""
    n = 200000
    a = math.radians(WEDGE_HALF_ANGLE_DEG)
    R = D_SPHERE / 2.0
    tot = 0.0
    for i in range(n):
        th = (i + 0.5) * (math.pi / 2.0) / n
        tot += 2.0 * R * math.sin(th) * math.sin(a) * R * math.cos(th) * math.cos(a)
    tot *= (math.pi / 2.0) / n
    if abs(tot - AREF) > 1e-9 * AREF:
        refuse("G1", "GEOMETRY CONTROL FAILED: the closed form AREF = %.12g "
                     "disagrees with a %d-point quadrature of the same integral "
                     "(%.12g)" % (AREF, n, tot))
    wet = 4.0 * (D_SPHERE / 2.0) ** 2 * math.sin(a)
    if abs(wet - AWET_ANALYTIC) > 1e-12:
        refuse("G2", "GEOMETRY CONTROL FAILED: AWET_ANALYTIC %.12g != 4 R^2 sin(a) "
                     "%.12g" % (AWET_ANALYTIC, wet))
    return {"aref_closed": AREF, "aref_quadrature": tot,
            "bias_bracket": AZIMUTHAL_BIAS_BRACKET}


def control_force_reader_synthetic():
    """The force reader, exercised on a SYNTHETIC force.dat with a known total_x,
    with the column order DELIBERATELY PERMUTED so a positional reader fails."""
    tmp = tempfile.mkdtemp(prefix="vmfl036_syn_")
    try:
        pth = os.path.join(tmp, "force.dat")
        with open(pth, "w") as fh:
            fh.write("# Force\n# CofR : (0 0 0)\n#\n")
            fh.write("# Time\tviscous_x viscous_y viscous_z\tpressure_x pressure_y "
                     "pressure_z\ttotal_x total_y total_z\n")
            fh.write("1 1 2 3 4 5 6 %.12e 8 9\n" % 0.0)
            fh.write("2 1 2 3 4 5 6 %.12e 8 9\n" % PLANT_FORCE)
        got = read_force_dat(pth)
        if abs(got["fx"][-1] - PLANT_FORCE) != 0.0:
            refuse("S1", "SYNTHETIC READER CONTROL FAILED: total_x sat in a "
                         "permuted column and the reader returned %.12g against the "
                         "planted %.12g -- it is reading BY POSITION, not by name"
                         % (got["fx"][-1], PLANT_FORCE))
        if got["fx"][0] != 0.0:
            refuse("S1", "SYNTHETIC READER CONTROL FAILED: a planted ZERO row read "
                         "back as %.12g" % got["fx"][0])
        # and it must REFUSE a file whose header does not name total_x
        bad = os.path.join(tmp, "bad.dat")
        open(bad, "w").write("# Time a b c\n1 2 3 4\n")
        try:
            read_force_dat(bad)
        except Refusal:
            pass
        else:
            refuse("S2", "SYNTHETIC READER CONTROL FAILED: a force.dat with NO "
                         "total_x column was accepted instead of refused")
        return {"permuted_column_seen": got["fx"][-1], "zero_seen": got["fx"][0],
                "refused_headerless": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_completion_refuses():
    """Strict completion (rule 4) must REFUSE, not degrade.  Handed a directory
    with nothing in it, the checker must raise."""
    tmp = tempfile.mkdtemp(prefix="vmfl036_comp_")
    try:
        try:
            completion_check(tmp)
        except Refusal:
            return {"refused_empty_dir": True}
        refuse("K1", "COMPLETION CONTROL FAILED: an EMPTY directory passed the "
                     "strict-completion check instead of being refused")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def selftest():
    print("VMFL036 comparator --selftest   (ZERO compute; no run directory read)")
    print("-" * 78)
    g = control_geometry_identity()
    print("  geometry     AREF closed form %.12g == quadrature %.12g"
          % (g["aref_closed"], g["aref_quadrature"]))
    print("               azimuthal bias bracket 1-cos(a) = %.6e  (%.4f%% of Cd)"
          % (g["bias_bracket"], 100.0 * g["bias_bracket"]))
    r = control_roache_classifier()
    print("  roache       every state SEEN: %s" % ", ".join(sorted(r.values())))
    s = control_force_reader_synthetic()
    print("  force reader PERMUTED-column total_x seen = %.6e; planted zero seen "
          "as %.1f; headerless file REFUSED" % (s["permuted_column_seen"],
                                                s["zero_seen"]))
    c = control_completion_refuses()
    print("  completion   an empty directory is REFUSED (rule 4 refuses, never "
          "degrades): %s" % c["refused_empty_dir"])
    print("-" * 78)
    print("SELFTEST GREEN")
    return 0


def verify_frozen(sha):
    """Prove that THIS file and polymesh_area.py on disk ARE the blobs committed at
    `sha`.  The grading path is fixed at the pre-registration commit (rule 2)."""
    import subprocess
    repo = subprocess.check_output(
        ["git", "-C", HERE, "rev-parse", "--show-toplevel"]).decode().strip()
    ok = True
    for rel in ("cases/ansys_verification/VMFL036/grade_vmfl036.py",
                "cases/ansys_verification/VMFL036/polymesh_area.py"):
        want = subprocess.check_output(
            ["git", "-C", repo, "rev-parse", "%s:%s" % (sha, rel)]).decode().strip()
        got = subprocess.check_output(
            ["git", "-C", repo, "hash-object", os.path.join(repo, rel)]).decode().strip()
        mark = "OK " if want == got else "DRIFT"
        if want != got:
            ok = False
        print("  %s %s  disk=%s frozen=%s" % (mark, rel, got[:12], want[:12]))
    return 0 if ok else 1


def dryrun_reader(path):
    """Exercise the gate-channel reader and print NOTHING NUMERIC.  Used by the
    launcher's smoke test so machinery can be proved without leaking a value
    before the freeze."""
    d = read_force_dat(path)
    print("  reader OK: %d rows, columns %s, total_x located by NAME"
          % (len(d["rows"]), ",".join(d["cols"][1:])))
    return 0


# ===========================================================================
# 7.  THE VERDICT.
# ===========================================================================
def grade_arm(arm, nu, re_num, gate):
    print("")
    print("=" * 78)
    print("ARM %s   nu = %.4g   Re = %.1f   %s"
          % (arm, nu, re_num, "THE GATE" if gate else
             "DISCLOSED DIAGNOSTIC ABOUT THE MANUAL -- NOT A GATE ON THIS SOLVER"))
    print("=" * 78)
    lv = [read_level(arm, n) for (n, _nt, _nr) in LEVELS]
    for (name, nt, nr), L_ in zip(LEVELS, lv):
        c = L_["completion"]
        print("  %-12s cells=%-7d Cd=%.6f  Fx=%.6e  worst final resid=%.2e  "
              "plateau ptp/Cd=%.2e  wall=%.0fs  %.2f core-min"
              % (name, 2 * nt * nr, L_["Cd"], L_["Fx"], c["worst_residual"],
                 L_["plateau_ptp"] / L_["Cd"], c["wall_s"], c["core_min"]))
        print("               mesh: sphere wetted ratio %.6f, PROJECTED/AREF %.9f, "
              "half-angle %.4f deg, %d sphere faces"
              % (L_["mesh"]["sphere_area_ratio"], L_["mesh"]["sphere_proj_ratio"],
                 L_["mesh"]["half_angle_deg"], L_["mesh"]["sphere_nFaces"]))

    # -- controls, fired against the REAL artifacts of the finest level ------
    cf = control_force_plant(lv[-1])
    cm = control_mesh_plant(lv[-1])
    print("  CONTROL force plant : total_x = %.6e planted into a copy of the finest "
          "level's force.dat; reader saw %.6e (Cd would be %.4f).  The reader is "
          "shown able to see a NON-ZERO." % (cf["plant"], cf["seen"], cf["cd_of_plant"]))
    print("  CONTROL mesh plant  : every point of a copy of the finest mesh scaled "
          "by %.1f; sphere area %.8g -> %.8g, required %.8g.  The geometry reader "
          "is shown able to see a CHANGED geometry."
          % (cm["scale"], cm["area_before"], cm["area_after"], cm["required"]))

    # -- rule 5 step 1: iterative convergence and plateau -------------------
    not_conv = [n for (n, _a, _b), L_ in zip(LEVELS, lv)
                if not L_["completion"]["iteratively_converged"] or not L_["plateau_ok"]]
    cds = [L_["Cd"] for L_ in lv]
    tri = roache(cds[0], cds[1], cds[2])

    print("")
    print("  ROACHE TRIPLE  f_coarse=%.6f  f_med=%.6f  f_fine=%.6f"
          % (tri["f_coarse"], tri["f_med"], tri["f_fine"]))
    print("                 d32=%.3e  d21=%.3e  R=%s  state=%s"
          % (tri["d32"], tri["d21"],
             "n/a" if tri["R"] is None else "%.6f" % tri["R"], tri["state"]))
    if tri["p"] is not None:
        flag = "  <-- SUSPICIOUSLY HIGH (above the formal order 2)" if tri["p"] > 2.3 else ""
        print("                 observed order p_obs = %.4f (formal p_f = 2)%s"
              % (tri["p"], flag))
    if tri["gci_fine"] is not None:
        print("                 GCI_fine at Fs = %.2f : %.4f%%   Richardson f_ex = %.6f"
              % (FS, 100.0 * tri["gci_fine"], tri["f_extrapolated"]))
    else:
        print("                 GCI: NOT QUOTED -- the three values are not monotone "
              "(rule 5: never quote a GCI when they are not).")

    cd_fine = cds[-1]
    cd_other_norm = lv[-1]["Fx"] / (Q_INF * AREF_WETTED_FORM)
    print("  AZIMUTHAL BIAS (N-AV9): Cd on the projected-area normalisation = %.6f; "
          "on the wetted-area normalisation = %.6f.  The bracket is %.4f%% of Cd "
          "and is NOT removed by refinement." % (cd_fine, cd_other_norm,
                                                 100.0 * AZIMUTHAL_BIAS_BRACKET))

    rel = abs(cd_fine - REF_CD) / REF_CD
    print("  Cd(finest) = %.6f   manual target = %.4f   |rel| = %.4f%%"
          % (cd_fine, REF_CD, 100.0 * rel))
    print("  (context only, never a gate: Ansys Fluent %.4f)" % ANSYS_FLUENT_CD)

    if not gate:
        # ARM B: a registered PREDICTION, not a gate.
        relb = abs(cd_fine - CD_SN_50) / CD_SN_50
        reld = abs(cd_fine - REF_CD) / REF_CD
        print("  ARM B registered prediction (frozen BEFORE the run): Schiller-"
              "Naumann at Re = %.0f gives Cd = %.4f." % (RE_ARM_B, CD_SN_50))
        print("  |Cd - SN(Re=50)|/SN = %.4f%%  (registered band %.0f%%)  -> %s"
              % (100.0 * relb, 100.0 * TOL_B_PREDICTION,
                 "AGREES" if relb <= TOL_B_PREDICTION else "DOES NOT AGREE"))
        print("  |Cd - manual target 1.0895|/1.0895 = %.4f%%  (discriminator needs "
              ">= %.0f%%)  -> %s" % (100.0 * reld, 100.0 * TOL_B_DISCRIMINATOR,
                                     "DISCRIMINATES" if reld >= TOL_B_DISCRIMINATOR
                                     else "DOES NOT DISCRIMINATE"))
        print("")
        print("  ARM B VERDICT: NOT A RESULT -- by construction and by registration.")
        print("  Arm B is evidence about the MANUAL, not a gate on this solver, and "
              "it never scores.  Its content is the DIAGNOSTIC sentence above.")
        return {"arm": arm, "verdict": "NOT A RESULT", "cd": cd_fine, "triple": tri,
                "agrees_sn": relb <= TOL_B_PREDICTION,
                "discriminates": reld >= TOL_B_DISCRIMINATOR,
                "levels": lv}

    # ---- ARM A: the gate, under rule-5 ordering ---------------------------
    print("")
    if not_conv:
        verdict = "NOT A RESULT"
        why = ("rule 5 step 1: level(s) %s are not iteratively converged or not "
               "plateaued" % ", ".join(not_conv))
    elif tri["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = ("rule 5 step 2: the grid triple is %s, not CONVERGING.  The value "
               "%.6f and both differences are printed above." % (tri["state"], cd_fine))
    elif rel <= TOL_A:
        verdict = "GATE REACHED"
        why = ("rule 5 step 3: the triple is CONVERGING and |rel| = %.4f%% is inside "
               "the frozen band %.1f%%.  The TIER CEILING is GATE REACHED: Mittal "
               "1999 and Tabata & Itakura 1998 are COMPUTED spectral solutions, so "
               "this reference is code-to-code and buys NEITHER V NOR P.  PASS is "
               "not available to this case whatever the number."
               % (100.0 * rel, 100.0 * TOL_A))
    else:
        verdict = "GATE FAIL"
        why = ("rule 5 step 3: the triple is CONVERGING and |rel| = %.4f%% is OUTSIDE "
               "the frozen band %.1f%%." % (100.0 * rel, 100.0 * TOL_A))
    print("  ARM A VERDICT: %s" % verdict)
    print("  %s" % why)
    return {"arm": arm, "verdict": verdict, "why": why, "cd": cd_fine,
            "triple": tri, "rel": rel, "levels": lv}


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify-frozen" in argv:
        return verify_frozen(argv[argv.index("--verify-frozen") + 1])
    if "--dryrun-reader" in argv:
        return dryrun_reader(argv[argv.index("--dryrun-reader") + 1])
    only = None
    if "--arm" in argv:
        only = argv[argv.index("--arm") + 1]

    print("VMFL036 -- Laminar Flow Past Sphere.  COMPARATOR OUTPUT.")
    print("manual p.125-126; target Cd = %.4f; run root %s" % (REF_CD, RUN_ROOT))
    selftest()
    out = {}
    if only in (None, "A"):
        out["A"] = grade_arm("A", MU_ARM_A, RE_ARM_A, gate=True)
    if only in (None, "B"):
        out["B"] = grade_arm("B", MU_MANUAL, RE_ARM_B, gate=False)
    print("")
    print("=" * 78)
    for k in sorted(out):
        print("  ARM %s : %s   Cd(finest) = %.6f   triple %s"
              % (k, out[k]["verdict"], out[k]["cd"], out[k]["triple"]["state"]))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as e:
        print("")
        print(str(e))
        print("The comparator REFUSES (exit 2) rather than degrade.")
        sys.exit(2)
