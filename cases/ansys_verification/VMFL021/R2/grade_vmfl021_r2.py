#!/usr/bin/env python3
"""VMFL021 comparator -- Cavitation over a sharp-edged orifice, Case A (high P1).

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 85.
Reference: W.H. Nurick, "Orifice Cavitation and Its Effects on Spray Mixing",
J. Fluids Engineering 98, 681-687, 1976  (experimental; the manual's target
0.620 coincides with Nurick's cavitating-orifice correlation Cd = Cc*sqrt(K),
Cc=0.62, K=(P1-Pv)/(P1-P2) -- see PREREGISTRATION.md line 3 for the ref-kind
nuance).  THIS FILE IS THE GRADING PATH.  Committed with the pre-registration
that cites it by sha, before any graded solver runs (CLAUDE.md rule 2).
REFUSES (exit 2) rather than degrading; every refusal names its clause.
Structure/controls adapted from the frozen VMFL050 comparator (planted-zero,
strict completion, Roache triple, selftest, --dryrun-reader).

GATE QUANTITY: coefficient of discharge
    Cd = mdot_actual / mdot_theoretical_max
       = (rho_l * |Q_inlet|) / (rho_l * A2 * V_theo)
       = |Q_inlet| / (A2 * V_theo)                  [rho_l cancels]
  Q_inlet  = sum(phi) over the inlet patch [m3/s], time-averaged over the final
             steady window.  The inlet is pure liquid (alpha.water=1), so the
             mixture mass flow there is rho_l*Q_inlet exactly -- this is WHY the
             flux is read at the inlet, not the (possibly two-phase) outlet.
  A2       = orifice throat area = the outlet-patch area of the 5deg wedge,
             READ from the FO header and cross-checked against the geometric
             flat-wedge sector 0.5*r2^2*sin(5deg).
  V_theo   = sqrt(2*(P1-P2)/rho_l).

  python3 grade_vmfl021_r2.py            # grade the run tree
  python3 grade_vmfl021_r2.py --selftest # synthetic, no solver
  python3 grade_vmfl021_r2.py --dryrun-reader <surfaceFieldValue.dat>
"""

import glob, json, math, os, re, shutil, sys, tempfile

CASE = "VMFL021-R2"
MANUAL_PAGE = "85"

# --- manual inputs (p.87) ----------------------------------------------------
P1 = 250000000.0   # Pa, inlet pressure (HIGH, Case A)
P2 = 95000.0       # Pa, outlet (back) pressure
PSAT = 3540.0      # Pa, vapour pressure
RHO_L = 1000.0     # kg/m3, liquid density
R2 = 0.004         # m, orifice radius
WEDGE_DEG = 5.0    # total wedge angle
A2_GEOM = 0.5 * R2 * R2 * math.sin(math.radians(WEDGE_DEG))  # flat-wedge sector
V_THEO = math.sqrt(2.0 * (P1 - P2) / RHO_L)
K_CAV = (P1 - PSAT) / (P1 - P2)          # Nurick cavitation number
CC_NURICK = 0.62                         # sharp-edge contraction coefficient

# manual Table .22.1
CD_REF = 0.620         # THE GATE reference (Nurick)
CD_ANSYS = 0.631       # context only, never the gate

TOL_GATE = 0.05        # |Cd_lab-Cd_ref|/Cd_ref <= 5% at the finest level.
                       # Justified in PREREGISTRATION.md line 6: manual's own 3%
                       # accuracy goal (p.609) + ~2% for the SchnerrSauer-vs-ZGB
                       # cavitation-model substitution (OpenFOAM has no ZGB).
                       # NOT chosen from any run.

# steady window: time-average Cd over the final fraction of physical time
ENDTIME = 0.003
WINDOW_FRAC = 0.30     # plateau/average window: the last 30% of the run.

# --- VMFL021-R2 PLATEAU CLAUSE (PREREG_TEMPLATE Amendment 4, all five items) --
# Attempt 1 (and VMFL022) used a windowed COEFFICIENT OF VARIATION alone, which
# Amendment 4 classes "Weakest": a monotonically rising series can have a small
# CoV, so CoV cannot distinguish a settled series from a slowly climbing one.
# R2 replaces it with the required artifact, modelled on the VMFL007 reference:
#  (1) FRACTIONAL window (WINDOW_FRAC) WITH an explicit minimum-sample floor;
#  (2) a REFUSAL below that floor -> CANNOT_TELL, never a pass;
#  (3) a GROWING-SERIES-REJECTING statistic: window peak-to-peak of |Q| as a
#      fraction of the WHOLE-RUN range (a still-climbing final window is a large
#      fraction) -- CoV is kept only BESIDE this, never instead of it;
#  (4) a NULL-RANGE refusal: a |Q| series that never resolvably moved is refused
#      (a dead field and a converged one are identical to a tolerance);
#  (5) the realised sample count is recorded in the grading JSON (n_window).
PLATEAU_MIN_SAMPLES = 20      # fractional-window floor; the FO writes every
                             # timestep (writeInterval 1) at dt~1e-6 to 0.003,
                             # so hundreds of samples are expected -- a window
                             # below 20 means the run barely integrated: CANNOT_TELL.
PLATEAU_PTP_FRAC_OF_RANGE = 0.03  # final-window |Q| peak-to-peak must be <=3% of
                             # the range the series traversed over the whole run.
                             # Justified from the manual's 3% goal, NOT a run; a
                             # still-climbing series has a large final-window ptp.
PLATEAU_NULL_RANGE = 1.0e-7  # m3/s: if the whole-run |Q| range is below this the
                             # discharge never resolvably moved -> CANNOT_TELL
                             # (steady |Q| ~ 3e-4 m3/s, so this is ~0.03% of it).
PLATEAU_COV = 0.03           # CoV kept BESIDE the ptp statistic (Amendment 4
                             # item 3: never instead of it), also gated at 3%.

FS = 1.25
RATIO = 2.0
PLANT = 1.234e-06      # m3/s, planted-zero perturbation on Q
PLANT_TOL = 1e-12
EPS_ABS = 1e-6         # Cd level-to-level difference below this counts as zero
STAG_TOL = 1e-3        # |R-1| <= STAG_TOL => STAGNANT
A2_XCHECK_TOL = 0.005  # FO-header area vs geometric area agree to 0.5%

# --- VMFL021-R2 NEW: REGIME PRECONDITION ON THE TRIPLE (rule 5 precondition) --
# VMFL022 graded NOT A RESULT because its COARSE level never cavitated
# (Min alpha.water = 1) while the finer two did -- the three levels were not
# solving the SAME problem, and the Roache triple came out OSCILLATORY
# (R = -0.104878).  A level with no vapour is NOT in the cavitating regime and
# must NOT be differenced into an observed order.  This comparator reads
# min(alpha.water) at endTime for every level and REFUSES the triple if any
# level is not cavitating -- BEFORE it is differenced.  A level is CAVITATING
# iff min(alpha.water) <= REGIME_ALPHA_MAX (>=1% vapour fraction somewhere).
# For Case A (deep cavitation, K->1) every level should reach alpha~0 at the
# vena contracta; this guard is registered regardless (it bites Case B harder).
REGIME_ALPHA_MAX = 0.99

# name -> orifice-radial cell count (coarse->fine, ratio 2)
LEVELS = (("L1", 12), ("L2", 24), ("L3", 48))

RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL021/R2"
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL021_R2.json")
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    print("REFUSE: " + msg, file=sys.stderr)
    sys.exit(2)


# --- reader: a surfaceFieldValue .dat (header lines '#', then 'time  value') --
def read_area_from_header(path):
    if not os.path.isfile(path):
        refuse("series file does not exist: " + path)
    for line in open(path, errors="replace"):
        m = re.match(r"#\s*Area\s*:\s*([0-9eE.+-]+)", line)
        if m:
            return float(m.group(1))
        if not line.startswith("#"):
            break
    refuse("no '# Area' header line in " + path)


def read_series(path):
    if not os.path.isfile(path):
        refuse("series file does not exist: " + path)
    rows = []
    for line in open(path, errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            refuse("data row has %d cols, expected >=2 (time value) in %s: %r"
                   % (len(parts), path, s))
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            refuse("unparseable data row in %s: %r" % (path, s))
    if not rows:
        refuse("no data rows in " + path)
    return rows


def inlet_dat(level_dir):
    pat = os.path.join(level_dir, "postProcessing", "inletMassFlow", "*", "surfaceFieldValue.dat")
    hits = sorted(glob.glob(pat))
    if not hits:
        refuse("no inlet surfaceFieldValue.dat under " + level_dir)
    return hits[-1]   # last FO start-time dir


def outlet_dat(level_dir):
    pat = os.path.join(level_dir, "postProcessing", "outletMassFlow", "*", "surfaceFieldValue.dat")
    hits = sorted(glob.glob(pat))
    if not hits:
        refuse("no outlet surfaceFieldValue.dat under " + level_dir)
    return hits[-1]


def window_stats(rows):
    """Return (mean_Q_abs, cov, n, t0, t1) over the final WINDOW_FRAC of time."""
    tmax = rows[-1][0]
    if abs(tmax - ENDTIME) > 1e-6:
        refuse("series last time %g != endTime %g" % (tmax, ENDTIME))
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win = [abs(v) for (t, v) in rows if t >= tcut - 1e-12]
    if len(win) < 5:
        refuse("only %d rows in the final %.0f%% window -- too few to average"
               % (len(win), WINDOW_FRAC * 100))
    mean = sum(win) / len(win)
    var = sum((x - mean) ** 2 for x in win) / len(win)
    cov = math.sqrt(var) / mean if mean > 0 else float("inf")
    return mean, cov, len(win), tcut, tmax


def plateau_stat(rows, label):
    """PREREG_TEMPLATE Amendment 4 plateau clause for the |Q| series.  REFUSES
    (CANNOT_TELL) below the sample floor or on a null-range series; returns the
    peak-to-peak-over-whole-range statistic (rejects a growing series) with CoV
    reported beside it, and the realised sample count.  Does NOT itself decide
    the verdict for a still-moving series -- that stays a graceful NOT A RESULT
    in main() so the numbers are printed."""
    allq = [abs(v) for (t, v) in rows]
    whole_range = max(allq) - min(allq)
    tmax = rows[-1][0]
    if abs(tmax - ENDTIME) > 1e-6:
        refuse("%s: series last time %g != endTime %g" % (label, tmax, ENDTIME))
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win = [abs(v) for (t, v) in rows if t >= tcut - 1e-12]
    n = len(win)
    # Amendment 4 item 2: minimum-sample REFUSAL -> CANNOT_TELL, never a pass.
    if n < PLATEAU_MIN_SAMPLES:
        refuse("%s: %d plateau samples in the final %.0f%% window < %d -- CANNOT_TELL, "
               "never a pass (Amendment 4 item 2)" % (label, n, WINDOW_FRAC * 100, PLATEAU_MIN_SAMPLES))
    # Amendment 4 item 4: null-range REFUSAL -> CANNOT_TELL.
    if whole_range < PLATEAU_NULL_RANGE:
        refuse("%s: the |Q| series spanned only %.6e m3/s over the whole run -- it never "
               "resolvably moved; a dead field and a converged one are identical to a "
               "tolerance; CANNOT_TELL, never a pass (Amendment 4 item 4)" % (label, whole_range))
    ptp = max(win) - min(win)
    ptp_frac = ptp / whole_range
    mean = sum(win) / n
    var = sum((x - mean) ** 2 for x in win) / n
    cov = math.sqrt(var) / mean if mean > 0 else float("inf")
    # Amendment 4 item 3: growing-series-rejecting statistic is the PRIMARY gate;
    # CoV is carried BESIDE it and also gated, never instead of it.
    plateaued = bool(ptp_frac <= PLATEAU_PTP_FRAC_OF_RANGE and cov <= PLATEAU_COV)
    return dict(mean=mean, cov=cov, ptp=ptp, whole_range=whole_range,
                ptp_frac=ptp_frac, n_window=n, plateaued=plateaued,
                t_window=(tcut, tmax))


def cd_of_level(level_dir):
    idat = inlet_dat(level_dir)
    odat = outlet_dat(level_dir)
    a2_fo = read_area_from_header(odat)
    if abs(a2_fo - A2_GEOM) / A2_GEOM > A2_XCHECK_TOL:
        refuse("outlet FO area %.6e disagrees with geometric flat-wedge A2 %.6e "
               "by >%.1f%% -- mesh/geometry mismatch" % (a2_fo, A2_GEOM, A2_XCHECK_TOL * 100))
    ps = plateau_stat(read_series(idat), os.path.basename(level_dir))
    q_mean = ps["mean"]
    cd = q_mean / (a2_fo * V_THEO)
    return dict(cd=cd, q_mean=q_mean, cov=ps["cov"], ptp=ps["ptp"],
                whole_range=ps["whole_range"], ptp_frac=ps["ptp_frac"],
                plateaued=ps["plateaued"], n_window=ps["n_window"], a2_fo=a2_fo,
                t_window=ps["t_window"], inlet_src=os.path.relpath(idat, RUN_ROOT),
                outlet_src=os.path.relpath(odat, RUN_ROOT))


# --- VMFL021-R2 NEW: regime precondition reader (rule 5 precondition) ---------
def read_alpha_min(level_dir):
    """Min of the alpha.water FIELD at endTime, parsed from OpenFOAM's own
    written field (uniform or nonuniform internalField).  This is a SOLUTION
    field, not a geometric quantity, so it is read directly (the geometry-read
    rule is about radii/areas, which this comparator reads from mesh/FO output
    elsewhere).  REFUSES if the field is absent or unparseable."""
    times = _time_dirs(level_dir)
    if not times or abs(float(times[-1]) - ENDTIME) > 1e-6:
        refuse("%s: no endTime dir for alpha regime read" % os.path.basename(level_dir))
    apath = os.path.join(level_dir, times[-1], "alpha.water")
    if not os.path.isfile(apath):
        refuse("%s: alpha.water missing at endTime -- cannot check regime" % os.path.basename(level_dir))
    text = open(apath, errors="replace").read()
    m = re.search(r"internalField\s+(\w+)", text)
    if not m:
        refuse("%s: no internalField in alpha.water" % os.path.basename(level_dir))
    kind = m.group(1)
    if kind == "uniform":
        mu = re.search(r"internalField\s+uniform\s+([0-9eE.+-]+)\s*;", text)
        if not mu:
            refuse("%s: unparseable uniform alpha.water" % os.path.basename(level_dir))
        return float(mu.group(1))
    if kind == "nonuniform":
        # nonuniform List<scalar> N ( v1 v2 ... );
        ml = re.search(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)", text, re.S)
        if not ml:
            refuse("%s: unparseable nonuniform alpha.water list" % os.path.basename(level_dir))
        vals = [float(x) for x in ml.group(2).split()]
        if not vals:
            refuse("%s: empty nonuniform alpha.water list" % os.path.basename(level_dir))
        return min(vals)
    refuse("%s: unknown internalField kind %r in alpha.water" % (os.path.basename(level_dir), kind))


def regime_of_level(level_dir):
    amin = read_alpha_min(level_dir)
    return dict(alpha_min=amin, cavitating=bool(amin <= REGIME_ALPHA_MAX),
                threshold=REGIME_ALPHA_MAX)


# --- planted-zero control (rule 3) -------------------------------------------
def planted_zero_control(level_dir):
    src = inlet_dat(level_dir)
    a2_fo = read_area_from_header(outlet_dat(level_dir))
    rows = read_series(src)
    base_mean, _, _, _, _ = window_stats(rows)
    tmp = tempfile.mkdtemp(prefix="vmfl022plant_")
    try:
        work = os.path.join(tmp, "surfaceFieldValue.dat")
        # copy header + rows, adding PLANT to every windowed value's magnitude
        tmax = rows[-1][0]; tcut = tmax * (1.0 - WINDOW_FRAC)
        with open(src) as fh, open(work, "w") as out:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("#"):
                    out.write(line); continue
                parts = s.split()
                t = float(parts[0]); v = float(parts[1])
                if t >= tcut - 1e-12:
                    # push magnitude up by PLANT, preserving sign
                    v = math.copysign(abs(v) + PLANT, v)
                out.write("%s\t%r\n" % (parts[0], v))
        seen_mean, _, _, _, _ = window_stats(read_series(work))
        moved = seen_mean - base_mean
        return dict(passed=abs(moved - PLANT) <= PLANT_TOL, planted=PLANT,
                    reader_delta=moved, file=os.path.basename(src))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- strict completion (rule 4; adapted for adaptive-dt transient) -----------
def _time_dirs(level_dir):
    out = []
    for d in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, d)) and re.fullmatch(r"\d+(\.\d+)?", d):
            out.append(d)
    return sorted(out, key=float)


def strict_completion(level_dir):
    name = os.path.basename(level_dir)
    if not os.path.isdir(level_dir):
        refuse("%s: run directory does not exist" % name)
    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("%s: no RUN_RC.txt -- the run did not finish this level" % name)
    m = re.search(r"^rc=(-?\d+)$", open(rc_path).read(), re.M)
    if not m:
        refuse("%s: RUN_RC.txt carries no rc" % name)
    rc = int(m.group(1))
    if rc != 0:
        refuse("%s: rc = %d (strict completion clause 1)" % (name, rc))
    log = os.path.join(level_dir, "log.interPhaseChangeFoam")
    if not os.path.isfile(log):
        refuse("%s: no log.interPhaseChangeFoam" % name)
    text = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", text, re.M):
        refuse("%s: no 'End' line in log (clause 2)" % name)
    times = _time_dirs(level_dir)
    if not times or abs(float(times[-1]) - ENDTIME) > 1e-6:
        refuse("%s: last time is %r, endTime is %g (clause 3)"
               % (name, times[-1] if times else None, ENDTIME))
    tdir = os.path.join(level_dir, times[-1])
    for fld in ("U", "p_rgh", "alpha.water"):
        if not os.path.isfile(os.path.join(tdir, fld)):
            refuse("%s: field %s missing at endTime (clause 4)" % (name, fld))
    # adaptive dt: ExecutionTime lines are variable, so we require >0 (a real
    # integration happened) and defer the "endTime reached" proof to clause 3.
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec < 10:
        refuse("%s: only %d ExecutionTime lines -- run too short (clause 5, adaptive-dt form)"
               % (name, n_exec))
    marker = os.path.join(level_dir, "0", "U")
    if not os.path.isfile(marker):
        refuse("%s: no 0/U age-guard marker (clause 6)" % name)
    t_marker = os.path.getmtime(marker)
    t_f = os.path.getmtime(os.path.join(tdir, "U"))
    if not t_f > t_marker:
        refuse("%s: endTime/U (%.3f) is NOT newer than 0/U (%.3f) -- AGE GUARD (clause 6)"
               % (name, t_f, t_marker))
    return dict(rc=rc, endTime=float(times[-1]), n_exec=n_exec,
                fields_at_endTime=["U", "p_rgh", "alpha.water"],
                age_guard="U newer than 0/U")


# --- Roache triple (rule 5) --------------------------------------------------
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine, d21=d21, d32=d32,
               ratio=ratio, fs=fs, p=None, R=None, gci_fine=None, f_extrapolated=None)
    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"; return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"; out["why"] = "d32 below EPS_ABS while d21 is not"; return out
    R_ = d21 / d32
    out["R"] = R_
    if R_ < 0:
        out["state"] = "OSCILLATORY"; return out
    if abs(R_ - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"; return out
    if R_ > 1.0:
        out["state"] = "DIVERGENT"; return out
    p = math.log(1.0 / R_) / math.log(ratio)
    out["p"] = p; out["state"] = "CONVERGING"
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"; out["why"] = "r^p-1<=0"; return out
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


def main():
    print("=" * 78)
    print("%s -- Cavitation over a sharp-edged orifice, Case A (high P1)" % CASE)
    print("Ansys FD Verification Manual 2026 R1, p. %s" % MANUAL_PAGE)
    print("reference: Nurick 1976 (experimental); target Cd = %.3f" % CD_REF)
    print("=" * 78)
    print("  V_theo = sqrt(2*(P1-P2)/rho) = %.4f m/s" % V_THEO)
    print("  A2 (flat-wedge orifice)      = %.6e m2" % A2_GEOM)
    print("  Nurick K = (P1-Pv)/(P1-P2)   = %.5f ; Cc*sqrt(K) = %.4f (physics check)"
          % (K_CAV, CC_NURICK * math.sqrt(K_CAV)))

    completion, levels, regimes = {}, {}, {}
    for name, nx in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        completion[name] = strict_completion(d)
        levels[name] = cd_of_level(d)
        regimes[name] = regime_of_level(d)          # VMFL021-R2 regime precondition

    # REGIME PRECONDITION (rule 5 precondition, VMFL021-R2): a level with no
    # vapour is not in the cavitating regime and must NOT be differenced.
    non_cavitating = [n for n, _ in LEVELS if not regimes[n]["cavitating"]]

    # plateau gate (Amendment 4): a level whose final-window ptp/range or CoV
    # exceeds threshold is NOT plateaued -> NOT A RESULT (rule 5, L1). The
    # too-few-samples and null-range cases already REFUSED inside plateau_stat.
    not_plateaued = [n for n, _ in LEVELS if not levels[n]["plateaued"]]

    fine = LEVELS[-1][0]
    pz = planted_zero_control(os.path.join(RUN_ROOT, fine))
    print("\nplanted-zero control on %s: %s" % (fine, json.dumps(pz)))
    if not pz["passed"]:
        refuse("planted-zero control failed: the reader cannot see a %g m3/s planted "
               "difference; its numbers mean nothing" % PLANT)

    cds = [levels[n]["cd"] for n, _ in LEVELS]
    cd_fine = cds[-1]
    rel = abs(cd_fine - CD_REF) / abs(CD_REF)
    gate_ok = rel <= TOL_GATE

    # REGIME PRECONDITION FIRST: if any level is not cavitating, the three
    # levels are not solving the same problem -- the triple is NOT differenced
    # (that is exactly the VMFL022 OSCILLATORY-from-mixed-regime trap).
    if non_cavitating:
        tr = dict(state="REGIME_BLOCKED", R=None, p=None, gci_fine=None,
                  f_extrapolated=None,
                  why="not differenced: levels %s not cavitating" % non_cavitating)
    else:
        tr = roache(cds[0], cds[1], cds[2])

    if non_cavitating:
        verdict = "NOT A RESULT"
        why = ("levels %s NOT in the cavitating regime (min alpha.water > %.2f) "
               "-- not solving the same problem as the finer levels, NOT differenced "
               "(rule 5 regime precondition; VMFL022 pattern)"
               % (non_cavitating, REGIME_ALPHA_MAX))
    elif not_plateaued:
        verdict = "NOT A RESULT"
        why = ("levels %s not plateaued (final-window |Q| ptp/range > %.1f%% or CoV > %.1f%%) "
               "(Amendment 4; rule 5, L1)" % (not_plateaued, PLATEAU_PTP_FRAC_OF_RANGE * 100, PLATEAU_COV * 100))
    elif tr["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = "grid triple %s, not CONVERGING (rule 5)" % tr["state"]
    else:
        verdict = "GATE REACHED" if gate_ok else "GATE FAIL"
        why = ("Cd_fine %.4f within %.0f%% of Nurick %.3f (rel %.3f%%)"
               % (cd_fine, TOL_GATE * 100, CD_REF, rel * 100) if gate_ok else
               "Cd_fine %.4f is %.3f%% off Nurick %.3f, outside the %.0f%% gate"
               % (cd_fine, rel * 100, CD_REF, TOL_GATE * 100))
    assert verdict in VERDICTS

    print("\n--- per level: Cd, window CoV, regime ---")
    for n, _ in LEVELS:
        L = levels[n]; R = regimes[n]
        print("  %-3s Cd=%.5f  Q=%.6e m3/s  ptp/range=%.3f%% CoV=%.3f%% n=%d %s  "
              "alpha_min=%.4f %s"
              % (n, L["cd"], L["q_mean"], L["ptp_frac"] * 100, L["cov"] * 100,
                 L["n_window"], "PLATEAU" if L["plateaued"] else "MOVING",
                 R["alpha_min"], "CAVITATING" if R["cavitating"] else "NOT-CAVITATING"))
    print("  Roache: state %s  R %s  p %s  GCI_fine %s  Cd_extrap %s" % (
        tr["state"],
        "n/a" if tr["R"] is None else "%.4f" % tr["R"],
        "n/a" if tr["p"] is None else "%.4f" % tr["p"],
        "n/a" if tr["gci_fine"] is None else "%.4e" % tr["gci_fine"],
        "n/a" if tr["f_extrapolated"] is None else "%.5f" % tr["f_extrapolated"]))
    print("\n  GATE: |Cd_fine - %.3f|/%.3f = %.4f  (tol %.2f)  -> %s"
          % (CD_REF, CD_REF, rel, TOL_GATE, "ok" if gate_ok else "OUT"))
    print("\nVERDICT: %s -- %s" % (verdict, why))
    print("  (context only, never the gate: Ansys Fluent Cd = %.3f)" % CD_ANSYS)

    payload = dict(case=CASE, manual_page=MANUAL_PAGE, verdict=verdict, why=why,
                   reference=dict(source="Nurick 1976", cd_ref=CD_REF, kind="experimental/correlation"),
                   physics_check=dict(K=K_CAV, cc=CC_NURICK, cd_from_correlation=CC_NURICK * math.sqrt(K_CAV)),
                   gate=dict(tol=TOL_GATE, cd_fine=cd_fine, rel=rel, ok=gate_ok),
                   V_theo=V_THEO, A2_geom=A2_GEOM,
                   ansys_context=dict(fluent_cd=CD_ANSYS),
                   triple=tr, levels=levels, completion=completion, planted_zero=pz,
                   regimes=regimes, non_cavitating=non_cavitating,
                   regime_threshold=REGIME_ALPHA_MAX,
                   not_plateaued=not_plateaued, comparator=os.path.abspath(__file__))
    os.makedirs(RUN_ROOT, exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    print("grading written to %s" % OUT_JSON)
    return 0


# --- selftest ----------------------------------------------------------------
def _write_alpha(level_dir, values, endt=ENDTIME):
    """Write a synthetic OpenFOAM alpha.water field into <level_dir>/<endt>/ so
    read_alpha_min can be exercised end to end.  `values`: a float (uniform) or
    a list (nonuniform).  This is a SOLUTION field, not a geometric quantity, so
    a synthetic fixture is legitimate (the real-mesh-only rule is for radii/areas)."""
    td = os.path.join(level_dir, ("%g" % endt))
    os.makedirs(td, exist_ok=True)
    hdr = ("FoamFile { version 2.0; format ascii; class volScalarField; "
           "object alpha.water; }\ndimensions [0 0 0 0 0 0 0];\n")
    with open(os.path.join(td, "alpha.water"), "w") as fh:
        fh.write(hdr)
        if isinstance(values, (list, tuple)):
            fh.write("internalField   nonuniform List<scalar>\n%d\n(\n" % len(values))
            for v in values:
                fh.write("%r\n" % v)
            fh.write(")\n;\n")
        else:
            fh.write("internalField   uniform %r;\n" % values)
        fh.write("boundaryField { }\n")


def _write_dat(path, qmag, n=40, endt=ENDTIME, area=A2_GEOM, jitter=0.0):
    with open(path, "w") as fh:
        fh.write("# Region type : patch inlet\n# Faces : 22\n")
        fh.write("# Area          : %r\n" % area)
        fh.write("# Scale factor  : 1\n# Time           \tsum(phi)\n")
        for i in range(1, n + 1):
            t = endt * i / n
            q = -(qmag * (1.0 + jitter * ((i % 2) * 2 - 1)))   # negative = inflow
            fh.write("%r\t%r\n" % (t, q))


def selftest():
    ok = True
    def check(label, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label, "" if not detail else "  <- " + str(detail)))
        ok = ok and bool(cond)

    print("--- physics: manual target vs Nurick correlation Cc*sqrt(K) ---")
    cd_corr = CC_NURICK * math.sqrt(K_CAV)
    check("K = 1.0004 (deep cavitation) to 4 d.p.", abs(K_CAV - 1.00037) < 1e-4, K_CAV)
    check("Cc*sqrt(K) == target 0.620 to 2 d.p.", abs(cd_corr - CD_REF) < 0.01, cd_corr)
    check("V_theo == 707.0 m/s", abs(V_THEO - 706.972) < 0.1, V_THEO)
    check("A2 flat-wedge == 6.9725e-7 m2", abs(A2_GEOM - 6.97246e-7) < 1e-11, A2_GEOM)

    tmp = tempfile.mkdtemp(prefix="vmfl022self_")
    try:
        print("--- reader: Cd recovered from a synthetic steady series ---")
        # choose qmag so Cd == 0.620 exactly:  q = Cd*A2*V_theo
        qtarget = CD_REF * A2_GEOM * V_THEO
        f = os.path.join(tmp, "surfaceFieldValue.dat"); _write_dat(f, qtarget)
        area = read_area_from_header(f)
        check("area header parsed", abs(area - A2_GEOM) < 1e-12, area)
        qm, cov, n, t0, t1 = window_stats(read_series(f))
        cd = qm / (area * V_THEO)
        check("Cd recovered == 0.620", abs(cd - CD_REF) < 1e-6, cd)
        check("steady series CoV ~ 0", cov < 1e-9, cov)

        print("--- reader REFUSES a one-column row (exit 2) ---")
        def refuses(fn):
            pid = os.fork()
            if pid == 0:
                os.dup2(os.open(os.devnull, os.O_WRONLY), 2)
                try: fn()
                except SystemExit as e: os._exit(e.code if isinstance(e.code, int) else 1)
                os._exit(0)
            _, st = os.waitpid(pid, 0)
            return os.WIFEXITED(st) and os.WEXITSTATUS(st) == 2
        bad = os.path.join(tmp, "bad.dat")
        open(bad, "w").write("# h\n0.06\n")
        check("one-column row REFUSED exit 2", refuses(lambda: read_series(bad)))

        print("--- planted-zero: reader sees +PLANT, unplanted copy unchanged ---")
        # emulate planted_zero_control's arithmetic directly on the window mean
        rows = read_series(f); base, _, _, _, _ = window_stats(rows)
        tmax = rows[-1][0]; tcut = tmax * (1.0 - WINDOW_FRAC)
        planted = [(t, math.copysign(abs(v) + PLANT, v)) for (t, v) in rows]
        pmean = sum(abs(v) for (t, v) in planted if t >= tcut - 1e-12) / \
                len([1 for (t, _) in planted if t >= tcut - 1e-12])
        check("planted window mean moves by PLANT", abs((pmean - base) - PLANT) <= PLANT_TOL, pmean - base)

        print("--- plateau gate: a noisy level is flagged not-plateaued ---")
        fn = os.path.join(tmp, "noisy.dat"); _write_dat(fn, qtarget, jitter=0.10)
        _, cov2, _, _, _ = window_stats(read_series(fn))
        check("10%% jitter -> CoV > plateau threshold", cov2 > PLATEAU_COV, cov2)

        print("--- Amendment 4 plateau: ptp/range REJECTS a trend that CoV misses ---")
        N = 200
        # settled: ramps 0->3e-4 in the first half, then flat with tiny jitter
        settled = []
        for i in range(N + 1):
            t = ENDTIME * i / N
            v = -3e-4 * (i / (N // 2)) if i < N // 2 else -3e-4 * (1.0 + 1e-4 * ((i % 2) * 2 - 1))
            settled.append((t, v))
        ps = plateau_stat(settled, "settled")
        check("settled series -> PLATEAU", ps["plateaued"], (ps["ptp_frac"], ps["cov"]))
        # growing: climbs the WHOLE run 3e-4 -> 3.3e-4; final window still climbing
        growing = [(ENDTIME * i / N, -(3e-4 + 0.3e-4 * (i / N))) for i in range(N + 1)]
        pg = plateau_stat(growing, "growing")
        check("growing series -> NOT plateaued (ptp/range catches it)", not pg["plateaued"], pg["ptp_frac"])
        check("growing series final-window CoV is SMALL (the trap CoV alone misses)", pg["cov"] < PLATEAU_COV, pg["cov"])
        # too-few-samples -> REFUSE (CANNOT_TELL)
        few = [(ENDTIME * i / 10, -3e-4) for i in range(11)]
        check("<%d window samples REFUSED (CANNOT_TELL)" % PLATEAU_MIN_SAMPLES,
              refuses(lambda: plateau_stat(few, "few")))
        # null-range (dead flat) -> REFUSE (CANNOT_TELL)
        flat = [(ENDTIME * i / N, -3e-4) for i in range(N + 1)]
        check("null-range dead-flat series REFUSED (CANNOT_TELL)",
              refuses(lambda: plateau_stat(flat, "flat")))

        print("--- regime precondition: alpha.water field read + classify ---")
        Lcav = os.path.join(tmp, "cav"); _write_alpha(Lcav, [1.0, 0.8, 0.2, 0.02, 1.0])
        rc = regime_of_level(Lcav)
        check("nonuniform min alpha 0.02 -> CAVITATING", rc["cavitating"] and abs(rc["alpha_min"] - 0.02) < 1e-9, rc)
        Lnon = os.path.join(tmp, "noncav"); _write_alpha(Lnon, 1.0)
        rn = regime_of_level(Lnon)
        check("uniform alpha 1.0 -> NOT-CAVITATING (the VMFL022 trap)", (not rn["cavitating"]) and abs(rn["alpha_min"] - 1.0) < 1e-9, rn)
        Lmiss = os.path.join(tmp, "miss"); os.makedirs(os.path.join(Lmiss, "%g" % ENDTIME))
        def refuses2(fn):
            pid = os.fork()
            if pid == 0:
                os.dup2(os.open(os.devnull, os.O_WRONLY), 2)
                try: fn()
                except SystemExit as e: os._exit(e.code if isinstance(e.code, int) else 1)
                os._exit(0)
            _, st = os.waitpid(pid, 0)
            return os.WIFEXITED(st) and os.WEXITSTATUS(st) == 2
        check("missing alpha.water at endTime REFUSED exit 2", refuses2(lambda: read_alpha_min(Lmiss)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("--- Roache classifier ---")
    fex, C = 0.620, 0.01
    t1 = roache(fex + C * 4, fex + C * 2, fex + C * 1)
    check("first-order family -> CONVERGING, p==1", t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9, t1["p"])
    check("Richardson recovers f_exact", abs(t1["f_extrapolated"] - fex) < 1e-6, t1["f_extrapolated"])
    t2 = roache(fex + C * 16, fex + C * 4, fex + C * 1)
    check("second-order family -> CONVERGING, p==2", t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9, t2["p"])
    check("divergent -> DIVERGENT", roache(0.70, 0.74, 0.80)["state"] == "DIVERGENT")
    check("oscillatory -> OSCILLATORY", roache(0.78, 0.80, 0.78)["state"] == "OSCILLATORY")
    check("identical -> EXACT", roache(0.78, 0.78, 0.78)["state"] == "EXACT")

    print("--- gate can pass and can fail ---")
    check("+3%% is inside the 5%% gate", abs((CD_REF * 1.03) - CD_REF) / CD_REF <= TOL_GATE)
    check("+7%% is outside the 5%% gate", abs((CD_REF * 1.07) - CD_REF) / CD_REF > TOL_GATE)

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def dryrun_reader(path):
    rows = read_series(path)
    qm, cov, n, t0, t1 = window_stats(rows)
    print("dryrun-reader: %d rows; window mean|Q|=%.6e CoV=%.3f%% n=%d Cd=%.5f"
          % (len(rows), qm, cov * 100, n, qm / (A2_GEOM * V_THEO)))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--dryrun-reader" in sys.argv:
        i = sys.argv.index("--dryrun-reader")
        sys.exit(dryrun_reader(sys.argv[i + 1]))
    sys.exit(main())
