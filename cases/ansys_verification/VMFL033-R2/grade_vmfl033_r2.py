#!/usr/bin/env python3
# ===========================================================================
# VMFL033-R2 -- Viscous Heating in an Annulus.  FROZEN COMPARATOR.
#
# Ansys Fluid Dynamics Verification Manual VM2026R1, p.119.
# Reference: R.B. Bird, W.E. Stewart, E.N. Lightfoot, "Transport Phenomena",
# John Wiley and Sons, New York, 1960.  The manual's own page says the problem
# "can be solved analytically" and compares its figures against "the analytical
# solution provided by Bird et al (1960)".
#
# R2 SUCCEEDS VMFL033-R1 (register row #21, NOT A RESULT, 2026-08-25).  R1's
# frozen files are NEVER touched; R1's row STANDS.  R2's ONE substantive setup
# change is a LONGER endTime (20000 -> 100000, a 5x ceiling) so the finest mesh
# can converge -- R1 died because L3 ran out of iterations at endTime=20000.
# Every other setup input (mesh, schemes, thermophysics, fvOptions, relaxation,
# BCs, residualControl-empty fixed-iteration mode) is BYTE-IDENTICAL to R1.
#
# WHAT THIS COMPARATOR ADDS OVER R1 (grading-side hardening, no physics change):
#   * THE TEMPERATURE CHANNEL IS THE GATE.  The velocity channel is reported but
#     is NOT a physics discriminator: v_theta/(Om2*r2) is independent of every
#     material property, so it tests the momentum solve (code verification) and
#     NOT the viscous-heating physics.  A credential rides on temperature only.
#   * PASS-CAPABLE per ANSYS_VERIFICATION_CHARTER Sec.11.1 (2026-08-30): a limb
#     declaring a Roache triple whose triple returns CONVERGING is graded by
#     CLAUDE.md rule 5 step 3, where PASS is available -- a converging triple
#     separates and bounds the discretisation error.  R1's frozen line 33
#     ("TIER CEILING: GATE REACHED") predates Sec.11.1 by five days and is NOT
#     edited (rule 6); R2 declares the ceiling in force at ITS OWN freeze.
#   * A GCI_MAX CEILING beside the P_MIN floor: a CONVERGING triple whose GCI on
#     the Roache functional exceeds GCI_MAX, or whose observed order is below
#     P_MIN, is NOT A RESULT -- an uncertainty larger than credential quality
#     cannot ride inside a PASS.
#   * THE PLANT FIRES AT EVERY LEVEL (rule 3), to disk, through the production
#     reader -- not at the finest level alone.
#   * NUMERIC time-directory selection with a CARDINALITY REFUSAL, never
#     sorted(glob)[-1] (L-339); lexicographic_would_have_misread is recorded.
#   * ZERO `assert` statements, enforced by an AST GUARD that parses this file's
#     own source and REFUSES if any assert node exists (assert vanishes under
#     python3 -O).  Every guard is an explicit raise/exit 2.
#
# EVERY RADIUS IS READ BACK FROM OpenFOAM'S OWN `C` FIELD.  Nothing geometric is
# constructed from nr, dr, (j+1/2) or any such expression.
# ===========================================================================
import ast, math, os, re, shutil, sys, tempfile

# ---------------------------------------------------------------- the case ---
RHO, CP, K_COND, MU = 1.0, 1.0, 1.0, 300.0     # VM2026R1 p.119, verbatim
R1_r, R2_r         = 1.0, 2.0                  # m (inner, outer radius)
OM1, OM2           = 0.0, 0.5                  # rad/s
T1, T2             = 273.0, 274.0              # K

RUN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", "verification", "runs",
                        "ansys_verification", "VMFL033-R2")
RUN_ROOT = os.path.normpath(RUN_ROOT)
LEVELS   = ["L1_nr32", "L2_nr64", "L3_nr128"]
ENDTIME  = 100000       # R2's ONE substantive change: 5x R1's 20000 (fixed-iteration ceiling)

# The required-field list is what the CONSUMER (this comparator) needs, INTERSECTED
# with the closure `constant/momentumTransport` names, EXCLUDING solver-generated
# `phi`.  MEASURED in R1's pre-flight: laminar buoyantSimpleFoam writes T U p p_rgh phi
# and NO alphat, so a naive enumeration from the fvSolution regex would refuse a
# correct run.  Carried forward from R1 unchanged.
REQUIRED_FIELDS = ["T", "U", "p", "p_rgh"]
TURBULENCE_FIELDS = {"kEpsilon": ["k", "epsilon", "nut"],
                     "kOmegaSST": ["k", "omega", "nut"],
                     "laminar": []}
SOLVER_GENERATED = {"phi"}

# ------------------------------------------------- THE FROZEN GATE (rule 2) ---
GATE_T_TOL   = 0.01     # THE GATE: max_cells |T_num - T_exact| / (Tpeak_ex - T1) <= 1%
REPORT_V_TOL = 0.01     # velocity REPORTING band -- NOT the gate, NOT a discriminator
EXPECT_T_TOL = 0.001    # REGISTERED EXPECTATION, reported either way, NEVER the gate
EXPECT_V_TOL = 0.001
PLATEAU_WINDOW = 500    # FIXED, not a fraction (carried from R1 Amendment 4 item 1)
PLATEAU_MIN    = 500    # refuse below this
PLATEAU_PTP_REL = 1.0e-6   # ptp over the window / (Tpeak_ex - T1); ptp REJECTS a trend
FS_ROACHE      = 1.25
P_FORMAL       = 2.0
P_SUSPICIOUS   = 2.5    # declared IN ADVANCE: above this is a WARNING, never a win
P_MIN          = 0.05   # FLOOR on the observed order of the CONVERGING triple
GCI_MAX        = 0.10   # CEILING on the GCI of the Roache functional (10%); above -> NOT A RESULT
PLANT = 1.234e-03       # planted at EVERY level


class Refusal(Exception):
    """Raised by the GRADING path when it will not degrade."""
    pass


class ControlFailure(Exception):
    """Raised ONLY by a selftest control whose subject failed to behave.

    A DIFFERENT TYPE from Refusal on purpose: controls below match an expected
    refusal by substring inside `except Refusal:` blocks, and a fall-through
    written as `refuse(...)` would be caught by that very handler whenever the
    control's message contained the substring it matches on -- swallowing the
    control's failure.  ControlFailure is caught by NO `except Refusal`.
    """
    pass


def control_failed(code, msg):
    raise ControlFailure("CONTROL FAILED [%s]: %s" % (code, msg))


def refuse(code, msg):
    raise Refusal("REFUSAL [%s]: %s" % (code, msg))


# ============================== THE AST GUARD =============================
def ast_guard(source_path):
    """Parse a python source file and REFUSE if it contains any `assert`.

    `assert` is removed by python3 -O, so a control or gate written as an assert
    silently vanishes in an optimised interpreter.  This comparator carries ZERO
    asserts; the guard proves it, over its OWN bytes, at every invocation."""
    if not os.path.isfile(source_path):
        refuse("A0", "AST guard: no source file at %s" % source_path)
    src = open(source_path).read()
    try:
        tree = ast.parse(src, filename=source_path)
    except SyntaxError as e:
        refuse("A1", "AST guard: %s does not parse (%s)" % (source_path, e))
    hits = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if hits:
        refuse("A2", "AST guard: %d `assert` statement(s) at line(s) %s in %s -- an assert "
                     "vanishes under python3 -O, so it is not an admissible guard"
               % (len(hits), ",".join(str(x) for x in hits), source_path))
    return len(hits)


# =============================== THE CLOSED FORM ===========================
# theta-momentum for purely tangential, steady, constant-property flow:
#     d/dr [ (1/r) d(r v)/dr ] = 0     ->    v(r) = A r + B/r
# energy, with v_r == 0 so there is NO radial convection of heat:
#     (k/r) d/dr( r dT/dr ) + mu*Phi = 0,   Phi = [ r d(v/r)/dr ]^2 = 4 B^2 / r^4
#     ->  T(r) = -(mu B^2 / k) / r^2 + C1 ln r + C2
# Constants fixed by v(R1)=OM1*R1, v(R2)=OM2*R2, T(R1)=T1, T(R2)=T2.
# DERIVED IN CODE to full double precision -- NEVER transcribed from R1's page.
A_V = (OM2 * R2_r * R2_r - OM1 * R1_r * R1_r) / (R2_r * R2_r - R1_r * R1_r)
B_V = (OM1 - OM2) * R1_r * R1_r * R2_r * R2_r / (R2_r * R2_r - R1_r * R1_r)
Q_T = MU * B_V * B_V / K_COND
C1_T = ((T2 - T1) - Q_T * (1.0 / (R1_r * R1_r) - 1.0 / (R2_r * R2_r))) / math.log(R2_r / R1_r)
C2_T = T1 + Q_T / (R1_r * R1_r) - C1_T * math.log(R1_r)


def v_exact(r):
    return A_V * r + B_V / r


def T_exact(r):
    return -Q_T / (r * r) + C1_T * math.log(r) + C2_T


R_PEAK = math.sqrt(-2.0 * Q_T / C1_T)     # dT/dr = 2Q/r^3 + C1/r = 0
T_PEAK = T_exact(R_PEAK)
T_SCALE = T_PEAK - T1                      # the viscous-heating rise; the T normaliser
V_SCALE = OM2 * R2_r                       # the moving-wall speed; the v normaliser


def T_volavg_exact():
    """Volume-weighted mean of T over the annulus: int T r dr / int r dr.
    Cell volumes in the sector go as r dr dtheta dz, so this is exactly what
    OpenFOAM's volAverage converges to."""
    def I(r):
        return (-Q_T * math.log(r)
                + C1_T * (r * r / 2.0 * math.log(r) - r * r / 4.0)
                + C2_T * r * r / 2.0)
    return (I(R2_r) - I(R1_r)) / ((R2_r * R2_r - R1_r * R1_r) / 2.0)


def q_inner_exact():
    """Inward conductive flux at r=R1: -k dT/dr."""
    return -K_COND * (2.0 * Q_T / R1_r ** 3 + C1_T / R1_r)


def total_dissipation_exact():
    """INDEPENDENT ROUTE to the gate constants.  Total viscous dissipation per
    unit z in the annulus = int_{R1}^{R2} mu*Phi(r) * 2*pi*r dr, with
    Phi = 4 B^2 / r^4 (the same B as the velocity field)."""
    q = MU * 4.0 * B_V * B_V           # mu*Phi = q / r^4
    # int q/r^4 * 2 pi r dr = 2 pi q int r^-3 dr = 2 pi q [ -1/(2 r^2) ]
    def J(r):
        return -1.0 / (2.0 * r * r)
    return 2.0 * math.pi * q * (J(R2_r) - J(R1_r))


def net_wall_outflow_exact():
    """INDEPENDENT ROUTE, second half: net conductive heat leaving the annulus
    per unit z = (outward flow at R2) - (outward flow at R1), each = q_r*2*pi*r
    with q_r = -k dT/dr.  In steady state with no convection this MUST equal the
    total dissipation -- the global energy balance, an instrument that never
    touches the BVP integration used for T_volavg/T_peak/q_inner."""
    def outward(r):
        return -K_COND * (2.0 * Q_T / r ** 3 + C1_T / r) * (2.0 * math.pi * r)
    return outward(R2_r) - outward(R1_r)


# ======================= OpenFOAM ascii field readers ======================
_NUM = r"[-+0-9.eEdD]+"


def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    return re.sub(r"//[^\n]*", " ", txt)


def read_scalar_field(path):
    if not os.path.isfile(path):
        refuse("F1", "no field file at %s" % path)
    txt = _strip(open(path).read())
    m = re.search(r"internalField\s+uniform\s+(" + _NUM + r")\s*;", txt)
    if m:
        refuse("F2", "%s has a UNIFORM internalField -- a uniform field is not a solved field "
                     "and this comparator will not read one as evidence" % path)
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*(\d+)?\s*\(", txt)
    if not m:
        refuse("F2", "%s: no nonuniform List<scalar> internalField found" % path)
    start = m.end()
    depth, i = 1, start
    while i < len(txt) and depth:
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
        i += 1
    body = txt[start:i - 1]
    vals = [float(x) for x in re.findall(_NUM, body) if re.match(r"^[-+]?[0-9.]", x)]
    n = int(m.group(1)) if m.group(1) else len(vals)
    if len(vals) != n:
        refuse("F3", "%s: header says %d values, parsed %d" % (path, n, len(vals)))
    if not vals:
        refuse("F4", "%s: ZERO values parsed" % path)
    return vals


def read_vector_field(path):
    if not os.path.isfile(path):
        refuse("F1", "no field file at %s" % path)
    txt = _strip(open(path).read())
    if re.search(r"internalField\s+uniform\s*\(", txt):
        refuse("F2", "%s has a UNIFORM internalField -- refused as above" % path)
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*(\d+)?\s*\(", txt)
    if not m:
        refuse("F2", "%s: no nonuniform List<vector> internalField found" % path)
    start = m.end()
    depth, i = 1, start
    while i < len(txt) and depth:
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
        i += 1
    body = txt[start:i - 1]
    trip = re.findall(r"\(\s*(" + _NUM + r")\s+(" + _NUM + r")\s+(" + _NUM + r")\s*\)", body)
    vecs = [(float(a), float(b), float(c)) for a, b, c in trip]
    n = int(m.group(1)) if m.group(1) else len(vecs)
    if len(vecs) != n:
        refuse("F3", "%s: header says %d vectors, parsed %d" % (path, n, len(vecs)))
    if not vecs:
        refuse("F4", "%s: ZERO vectors parsed" % path)
    return vecs


def read_series(path):
    if not os.path.isfile(path):
        refuse("S1", "no settling series at %s -- the plateau clause has nothing to read" % path)
    xs = []
    for line in open(path):
        if line.startswith("#"):
            continue
        f = line.split()
        if len(f) >= 2:
            try:
                xs.append((float(f[0]), float(f[-1])))
            except ValueError:
                refuse("S2", "%s: non-numeric row" % path)
    if not xs:
        refuse("S3", "%s: header found but ZERO data rows" % path)
    return xs


# ================= NUMERIC time-directory selection (L-339) ================
def select_endtime_dir(level_dir, endtime):
    """Select the endTime directory by NUMERIC value, with a CARDINALITY REFUSAL.
    NEVER sorted(glob)[-1]: '9' sorts lexicographically after '100000'.  Records
    whether a lexicographic pick would have MISREAD, and refuses if two names map
    to the same numeric time (e.g. '100000' and '100000.0')."""
    names = [d for d in os.listdir(level_dir)
             if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d)
             and os.path.isdir(os.path.join(level_dir, d))]
    times = [(float(d), d) for d in names if float(d) > 0.0]
    if not times:
        refuse("C3", "no positive time directories in %s" % level_dir)
    # cardinality: no two distinct names may denote the same numeric time
    seen = {}
    for val, nm in times:
        if val in seen:
            refuse("C3", "%s: two directory names ('%s','%s') denote the SAME numeric time %g "
                         "-- cardinality is ambiguous, REFUSED rather than resolved arbitrarily"
                   % (level_dir, seen[val], nm, val))
        seen[val] = nm
    numeric_name = max(times, key=lambda t: t[0])[1]
    lexicographic_name = sorted(names)[-1]
    misread = (numeric_name != lexicographic_name)
    if abs(float(numeric_name) - endtime) > 1e-9:
        refuse("C3", "%s: numeric-max time directory is '%s' (%g), not endTime %d -- the finest "
                     "time on disk is not the registered endTime"
               % (level_dir, numeric_name, float(numeric_name), endtime))
    return numeric_name, misread


# =========================== strict completion (rule 4) ====================
def kv(path):
    d = {}
    if os.path.isfile(path):
        for line in open(path):
            m = re.match(r"\s*(\w+)\s*=\s*(.*)", line)
            if m:
                d[m.group(1)] = m.group(2).strip()
    return d


def completion(level_dir):
    """Strict completion (rule 4), refusing (exit 2) rather than degrading.

    R2 keeps R1's FIXED-ITERATION mode (fvSolution residualControl empty), so the
    completion signal is last == endTime and ExecutionTime count == endTime, as
    R1 -- NOT the residualControl-terminated inversion (last < endTime) of
    VMFL063 Sec.6 clause 4, which applies only when residualControl TERMINATES
    the solve.  R2's convergence refusal is carried by the PLATEAU CLAUSE, which
    refuses any level whose volume-average has not settled.  The age guard and
    every other completion clause are UNCHANGED."""
    rc = kv(os.path.join(level_dir, "RUN_RC.txt"))
    if not rc:
        refuse("C1", "no readable RUN_RC.txt in %s -- the run's own exit code is not on disk"
               % level_dir)
    if rc.get("rc") != "0":
        refuse("C1", "%s records rc=%s -- a non-zero exit is a FINDING, triage it, never grade it"
               % (level_dir, rc.get("rc")))
    log = os.path.join(level_dir, "log.buoyantSimpleFoam")
    if not os.path.isfile(log):
        refuse("C2", "no solver log in %s" % level_dir)
    txt = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", txt, re.M):
        refuse("C2", "no 'End' line in %s" % log)
    numeric_name, misread = select_endtime_dir(level_dir, ENDTIME)
    nex = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if nex != ENDTIME:
        refuse("C5", "ExecutionTime count is %d against endTime %d in %s -- rule 4's "
                     "iteration-count clause is NOT met (fixed-iteration mode)"
               % (nex, ENDTIME, level_dir))
    cd = os.path.join(level_dir, "system", "controlDict")
    ctxt = _strip(open(cd).read()) if os.path.isfile(cd) else ""
    mw = re.search(r"writeInterval\s+(" + _NUM + r")\s*;", ctxt)
    me = re.search(r"\bendTime\s+(" + _NUM + r")\s*;", ctxt)
    if not mw or not me:
        refuse("C8", "%s: cannot read endTime/writeInterval from system/controlDict" % level_dir)
    wi, et = float(mw.group(1)), float(me.group(1))
    if wi <= 0 or abs(et / wi - round(et / wi)) > 1e-9:
        refuse("C8", "%s: endTime %g is NOT an exact multiple of writeInterval %g -- a case can "
                     "run clean and write NO gradeable output" % (level_dir, et, wi))
    if abs(et - ENDTIME) > 1e-9:
        refuse("C8", "%s: system/controlDict endTime %g != registered endTime %d"
               % (level_dir, et, ENDTIME))
    tdir = os.path.join(level_dir, numeric_name)
    if not os.path.isdir(tdir):
        refuse("C8", "%s: no field directory at endTime %d" % (level_dir, ENDTIME))
    mt = os.path.join(level_dir, "constant", "momentumTransport")
    if not os.path.isfile(mt):
        refuse("C9", "%s: no constant/momentumTransport -- the closure this run actually used "
                     "cannot be read, so the required-field list cannot be intersected with it"
               % level_dir)
    mm = re.search(r"simulationType\s+(\w+)\s*;", _strip(open(mt).read()))
    if not mm:
        refuse("C9", "%s: constant/momentumTransport names no simulationType" % level_dir)
    closure = mm.group(1)
    if closure not in TURBULENCE_FIELDS:
        refuse("C9", "%s: closure '%s' is not one this comparator knows the field set of -- "
                     "REFUSED rather than guessed" % (level_dir, closure))
    need = [f for f in REQUIRED_FIELDS + TURBULENCE_FIELDS[closure] + ["C"]
            if f not in SOLVER_GENERATED]
    for f in need:
        if not os.path.isfile(os.path.join(tdir, f)):
            refuse("C4", "field %s is MISSING at endTime in %s (closure '%s' requires %s)"
                   % (f, level_dir, closure, " ".join(need)))
    zdir = os.path.join(level_dir, "0")
    if not os.path.isdir(zdir):
        refuse("C6", "no 0/ in %s -- the age guard has no datum" % level_dir)
    newest0 = max(os.path.getmtime(os.path.join(zdir, f)) for f in os.listdir(zdir))
    for f in [x for x in need if x != "C"]:
        if os.path.getmtime(os.path.join(tdir, f)) <= newest0:
            refuse("C6", "AGE GUARD: %s at endTime is NOT newer than the newest file in %s/0 -- "
                         "this field cannot have been produced by the run that was allowed to "
                         "produce it" % (f, level_dir))
    res = {}
    for k in ("Ux", "h", "p_rgh"):
        hits = re.findall(r"Solving for %s.*?Final residual = (" % re.escape(k) + _NUM + r")", txt)
        if hits:
            res[k] = float(hits[-1])
    if not res:
        refuse("C7", "no final-residual lines found in %s" % log)
    return max(res.values()), res, numeric_name, misread


# ================================ plateau ==================================
def plateau(series):
    """FIXED window; minimum-sample REFUSAL; peak-to-peak (rejects a growing
    series); null-range refusal.  Returns (ptp_window, n_window, ptp_full)."""
    vals = [v for _, v in series]
    n = len(vals)
    if n < PLATEAU_MIN:
        refuse("V1", "%d plateau samples < %d -- CANNOT_TELL, never a pass" % (n, PLATEAU_MIN))
    w = vals[-PLATEAU_WINDOW:]
    ptp_full = max(vals) - min(vals)
    if ptp_full == 0.0:
        refuse("V2", "NULL RANGE: the settling series has ZERO variation over its whole length "
                     "-- a dead field and a converged one look identical to a tolerance, so this "
                     "is REFUSED, never passed")
    return max(w) - min(w), len(w), ptp_full


# ================================= Roache (rule 5) =========================
def roache(f1, f2, f3, r=2.0):
    """f1 coarse, f2 medium, f3 fine."""
    d32, d21 = f2 - f1, f3 - f2
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "d32": d32, "d21": d21}
    if d32 == 0.0 and d21 == 0.0:
        out.update(state="EXACT", R=None, p=None, gci=None, fex=None)
        return out
    if d32 == 0.0:
        out.update(state="STAGNANT", R=None, p=None, gci=None, fex=None)
        return out
    R = d21 / d32
    out["R"] = R
    if R < 0:
        out.update(state="OSCILLATORY", p=None, gci=None, fex=None)
        return out
    if R >= 1.0:
        out.update(state="DIVERGENT", p=None, gci=None, fex=None)
        return out
    if abs(d21) < 1e-300:
        out.update(state="STAGNANT", p=None, gci=None, fex=None)
        return out
    p = math.log(abs(d32 / d21)) / math.log(r)
    fex = f3 + d21 / (r ** p - 1.0)
    denom = f3 if f3 != 0 else 1.0
    gci = FS_ROACHE * abs(d21 / denom) / (r ** p - 1.0)
    out.update(state="CONVERGING", p=p, gci=gci, fex=fex)
    return out


# =============================== THE VERDICT ===============================
def decide_verdict(rows, tr, not_settled):
    """Pure decision function -- rule 5 in its own ORDER, with the R2 guards.

    THE TEMPERATURE CHANNEL IS THE GATE (the physics discriminator).  Velocity is
    NOT consulted here: v_theta/(Om2*r2) is independent of every material property
    and so tests no viscous-heating physics.  PASS is available because the
    reference limb declares a Roache triple (charter Sec.11.1)."""
    reasons = []
    if not_settled:                                            # rule 5 step (1)
        reasons.append("levels not plateaued: %s"
                       % ", ".join(os.path.basename(r["dir"]) for r in not_settled))
    if tr["state"] != "CONVERGING":                            # rule 5 step (2)
        reasons.append("Roache triple is %s, not CONVERGING" % tr["state"])
    else:
        if tr["p"] < P_MIN:                                    # P_MIN floor
            reasons.append("observed order p=%.4f is below the floor P_MIN=%.3f -- not credibly "
                           "in the asymptotic range" % (tr["p"], P_MIN))
        if tr["gci"] > GCI_MAX:                                # GCI_MAX ceiling
            reasons.append("functional GCI=%.4f%% exceeds the ceiling GCI_MAX=%.1f%% -- an "
                           "uncertainty larger than credential quality cannot ride inside a PASS"
                           % (100 * tr["gci"], 100 * GCI_MAX))
    fine = rows[-1]
    t_inside = fine["rel_T"] <= GATE_T_TOL                     # rule 5 step (3): TEMPERATURE gate
    if reasons:
        return "NOT A RESULT", "; ".join(reasons)
    if t_inside:
        return "PASS", ("the TEMPERATURE band is met at the finest level on a CONVERGING triple "
                        "(GCI within ceiling, order above floor); a converging triple bounds the "
                        "discretisation error, so PASS is available per charter Sec.11.1")
    return "GATE FAIL", ("the triple converges and the levels are settled, but the temperature "
                         "band is missed at the finest level")


# ================================ one level ================================
def read_level(level_dir):
    worst, res, numeric_name, misread = completion(level_dir)
    tdir = os.path.join(level_dir, numeric_name)
    C = read_vector_field(os.path.join(tdir, "C"))      # RADII READ BACK FROM OpenFOAM
    U = read_vector_field(os.path.join(tdir, "U"))
    T = read_scalar_field(os.path.join(tdir, "T"))
    if not (len(C) == len(U) == len(T)):
        refuse("F5", "%s: C/U/T lengths differ (%d/%d/%d)" % (level_dir, len(C), len(U), len(T)))
    ev = et = 0.0
    vr_max = 0.0
    for (x, y, _z), (ux, uy, uz), t in zip(C, U, T):
        r = math.hypot(x, y)
        if r < R1_r - 1e-9 or r > R2_r + 1e-9:
            refuse("G1", "%s: a cell centre sits at r=%.12g, outside [%g,%g] -- the mesh is not "
                         "the registered annulus" % (level_dir, r, R1_r, R2_r))
        et_hat, er_hat = (-y / r, x / r), (x / r, y / r)
        vth = ux * et_hat[0] + uy * et_hat[1]
        vr = ux * er_hat[0] + uy * er_hat[1]
        ev = max(ev, abs(vth - v_exact(r)))
        et = max(et, abs(t - T_exact(r)))
        vr_max = max(vr_max, abs(vr))
    ser = read_series(os.path.join(level_dir, "postProcessing", "Tmean", "0", "volFieldValue.dat"))
    if abs(ser[-1][0] - ENDTIME) > 1e-6:
        refuse("S4", "%s: the settling series ends at %g, not endTime %d"
               % (level_dir, ser[-1][0], ENDTIME))
    ptp, nwin, ptp_full = plateau(ser)
    return {"dir": level_dir, "ncells": len(T), "Tavg": ser[-1][1],
            "err_v": ev, "err_T": et, "vr_max": vr_max,
            "rel_v": ev / V_SCALE, "rel_T": et / T_SCALE,
            "worst_resid": worst, "resid": res,
            "ptp": ptp, "n_window": nwin, "ptp_full": ptp_full,
            "ptp_rel": ptp / T_SCALE, "lex_misread": misread,
            "Tmax": max(T), "rc": kv(os.path.join(level_dir, "RUN_RC.txt"))}


# ============================== planted controls (rule 3) ==================
def plant_one_level(level_dir):
    """Plant into COPIES of THIS level's real artifacts and read them back.
    Runs at EVERY level (R2 requirement 2), not the finest alone."""
    numeric_name, _misread = select_endtime_dir(level_dir, ENDTIME)
    tdir = os.path.join(level_dir, numeric_name)
    tmp = tempfile.mkdtemp(prefix="vmfl033r2_plant_")
    try:
        src = os.path.join(tdir, "T")
        dst = os.path.join(tmp, "T")
        shutil.copy(src, dst)
        base = read_scalar_field(dst)
        truth = read_scalar_field(src)
        if base != truth:
            refuse("P0", "the UNPLANTED copy of %s does not read back as itself" % src)
        txt = open(dst).read()
        planted_val = base[0] + PLANT
        idx = txt.index("(", txt.index("internalField"))
        head, tail = txt[:idx + 1], txt[idx + 1:]
        mfirst = re.search(_NUM, tail)
        tail = tail[:mfirst.start()] + repr(planted_val) + tail[mfirst.end():]
        open(dst, "w").write(head + tail)
        got = read_scalar_field(dst)
        seen = got[0] - base[0]
        if abs(seen - PLANT) > 1e-12:
            refuse("P1", "PLANTED-ZERO CONTROL FAILED at %s: %g was planted into a copy of %s and "
                         "the reader saw %g -- a reader not shown able to see a non-zero cannot be "
                         "trusted to report a zero" % (os.path.basename(level_dir), PLANT, src, seen))
        csrc, cdst = os.path.join(tdir, "C"), os.path.join(tmp, "C")
        shutil.copy(csrc, cdst)
        C0 = read_vector_field(cdst)
        ctxt = open(cdst).read()
        start = ctxt.index("(", ctxt.index("List<vector>")) + 1
        depth, i = 1, start
        while i < len(ctxt) and depth:
            if ctxt[i] == "(":
                depth += 1
            elif ctxt[i] == ")":
                depth -= 1
            i += 1
        body = ctxt[start:i - 1]

        def dbl(mm):
            return "(%r %r %r)" % (2 * float(mm.group(1)), 2 * float(mm.group(2)),
                                   2 * float(mm.group(3)))
        newbody = re.sub(r"\(\s*(" + _NUM + r")\s+(" + _NUM + r")\s+(" + _NUM + r")\s*\)",
                         dbl, body)
        open(cdst, "w").write(ctxt[:start] + newbody + ctxt[i - 1:])
        C1f = read_vector_field(cdst)
        r0 = math.hypot(C0[0][0], C0[0][1])
        r1f = math.hypot(C1f[0][0], C1f[0][1])
        if abs(r1f - 2.0 * r0) > 1e-9 * max(1.0, r0):
            refuse("P2", "PLANTED-ZERO CONTROL FAILED at %s: every cell centre in a copy of %s was "
                         "scaled by 2 and the geometry reader read radius %.12g against a required "
                         "%.12g" % (os.path.basename(level_dir), csrc, r1f, 2.0 * r0))
        return {"level": os.path.basename(level_dir), "plant": PLANT, "seen": seen,
                "r0": r0, "r_planted": r1f}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =================================== selftest ==============================
def _write_min_field_scalar(path, vals):
    with open(path, "w") as f:
        f.write("FoamFile { version 2.0; format ascii; class volScalarField; object T; }\n")
        f.write("dimensions [0 0 0 1 0 0 0];\n")
        f.write("internalField   nonuniform List<scalar> %d (\n" % len(vals))
        for v in vals:
            f.write("%r\n" % v)
        f.write(");\n")


def selftest():
    """Every control has EXACTLY ONE path that lets the selftest continue: the one
    where its subject behaved.  Every other path raises ControlFailure, which no
    `except Refusal` catches.  Break any control and the terminal SELFTEST GREEN
    line becomes UNREACHABLE."""
    print("VMFL033-R2 comparator --selftest   (ZERO compute; no run directory is read)")
    print("-" * 78)

    # ---- A  the AST guard: this file must carry ZERO asserts, and the guard must FIRE on one
    n_here = ast_guard(os.path.abspath(__file__))
    print("  ast guard    this comparator carries %d assert statements (required: 0)" % n_here)
    tmpg = tempfile.mkdtemp(prefix="vmfl033r2_ast_")
    try:
        planted = os.path.join(tmpg, "has_assert.py")
        open(planted, "w").write("def f(x):\n    assert x > 0\n    return x\n")
        _ok = False
        try:
            ast_guard(planted)
        except Refusal as e:
            if "assert" in str(e):
                _ok = True
        if not _ok:
            control_failed("A", "AST-GUARD CONTROL FAILED: a file containing an `assert` was NOT "
                                "refused -- the guard cannot be trusted to have cleared this file")
    finally:
        shutil.rmtree(tmpg, ignore_errors=True)
    print("  ast guard    a file containing an `assert` is REFUSED (guard proven to FIRE)")

    # ---- C1  closed form satisfies its own boundary conditions
    for r, want in ((R1_r, OM1 * R1_r), (R2_r, OM2 * R2_r)):
        if abs(v_exact(r) - want) > 1e-12:
            control_failed("C1", "v_exact(%g) = %g, want %g" % (r, v_exact(r), want))
    for r, want in ((R1_r, T1), (R2_r, T2)):
        if abs(T_exact(r) - want) > 1e-9:
            control_failed("C1", "T_exact(%g) = %g, want %g" % (r, T_exact(r), want))
    print("  closed form  BCs exact: v(%g)=%.1e v(%g)=%.12g  T(%g)=%.12g T(%g)=%.12g"
          % (R1_r, v_exact(R1_r), R2_r, v_exact(R2_r), R1_r, T_exact(R1_r), R2_r, T_exact(R2_r)))

    # ---- C2  the INDEPENDENT numerical BVP that never uses the closed form
    errs = []
    for n in (100, 200, 400):
        rs, w = _bvp_v(n)
        _, Tn = _bvp_T(n, w)
        ev = max(abs(w[i] * rs[i] - v_exact(rs[i])) for i in range(len(rs)))
        et = max(abs(Tn[i] - T_exact(rs[i])) for i in range(len(rs)))
        errs.append((n, ev, et))
    for n, ev, et in errs:
        print("  BVP control  n=%3d  max|v_num-v_ex|=%.3e  max|T_num-T_ex|=%.3e" % (n, ev, et))
    rat = errs[1][2] / errs[2][2] if errs[2][2] else 0.0
    if not (3.0 < rat < 5.0):
        control_failed("C2", "the independent BVP does not converge at 2nd order to the closed "
                             "form (ratio %.3f) -- THE DERIVATION IS NOT CONFIRMED" % rat)
    print("  BVP control  T error falls %.2fx per doubling -> 2nd order -> DERIVATION CONFIRMED"
          % rat)

    # ---- C2b  SECOND INDEPENDENT INSTRUMENT: global energy balance closes the gate constants
    diss = total_dissipation_exact()
    outf = net_wall_outflow_exact()
    rel = abs(diss - outf) / abs(diss)
    if rel > 1e-12:
        control_failed("C2b", "ENERGY-BALANCE CONTROL FAILED: total dissipation %.9g != net wall "
                              "outflow %.9g (rel %.3e) -- the gate constants do not conserve energy"
                       % (diss, outf, rel))
    print("  energy bal   total dissipation %.9g W = net wall outflow %.9g W (rel %.2e) -- an "
          "INDEPENDENT route to C1_T/T_peak/T_avg/q_wall CLOSES" % (diss, outf, rel))

    # ---- C3  Roache classifier must SEE every state, exact on a 2nd-order triple
    for want, args in (("CONVERGING", (1.04, 1.01, 1.0025)),
                       ("DIVERGENT", (1.0, 1.1, 1.4)),
                       ("OSCILLATORY", (1.0, 1.1, 1.05)),
                       ("STAGNANT", (1.0, 1.0, 1.1)),
                       ("EXACT", (1.0, 1.0, 1.0))):
        got = roache(*args)["state"]
        if got != want:
            control_failed("C3", "the Roache classifier returned %s where %s was CONSTRUCTED"
                           % (got, want))
    ex2 = roache(1.0 + 4e-4, 1.0 + 1e-4, 1.0 + 0.25e-4)
    if ex2["p"] is None or abs(ex2["p"] - 2.0) > 1e-9:
        control_failed("C3", "an exactly-second-order triple returned p=%r" % (ex2["p"],))
    print("  roache       every state SEEN; an exact 2nd-order triple returns p=2 to 1e-9")

    # ---- C4/C5/C6  plateau: floor, null range, growing series
    _ok = False
    try:
        plateau([(i, 1.0 + 1e-9 * i) for i in range(PLATEAU_MIN - 1)])
    except Refusal as e:
        if "CANNOT_TELL" in str(e):
            _ok = True
    if not _ok:
        control_failed("C4", "PLATEAU MINIMUM-SAMPLE CONTROL FAILED: a short series was NOT refused")
    _ok = False
    try:
        plateau([(i, 5.0) for i in range(PLATEAU_MIN + 10)])
    except Refusal as e:
        if "NULL RANGE" in str(e):
            _ok = True
    if not _ok:
        control_failed("C5", "PLATEAU NULL-RANGE CONTROL FAILED: a dead-flat series was NOT refused")
    ptp_g, _n_g, _ = plateau([(i, 1.0 + 1e-3 * i) for i in range(PLATEAU_MIN + 10)])
    if ptp_g / T_SCALE <= PLATEAU_PTP_REL:
        control_failed("C6", "TREND-REJECTION CONTROL FAILED: a growing series passed the plateau "
                             "tolerance (ptp/scale = %.3e <= %.1e)" % (ptp_g / T_SCALE, PLATEAU_PTP_REL))
    print("  plateau      %d-sample floor REFUSES; a null range REFUSES; a growing series is "
          "REJECTED (ptp/scale = %.3e > %.1e)" % (PLATEAU_MIN, ptp_g / T_SCALE, PLATEAU_PTP_REL))

    # ---- C7  numeric time-dir selection with cardinality refusal (L-339)
    tmpn = tempfile.mkdtemp(prefix="vmfl033r2_td_")
    try:
        for nm in ("0", "9", str(ENDTIME)):
            os.makedirs(os.path.join(tmpn, nm))
        chosen, misread = select_endtime_dir(tmpn, ENDTIME)
        if chosen != str(ENDTIME):
            control_failed("C7", "TIME-DIR CONTROL FAILED: numeric selection chose '%s', not '%d'"
                           % (chosen, ENDTIME))
        if not misread:
            control_failed("C7", "TIME-DIR CONTROL FAILED: with dirs {0,9,%d} a lexicographic pick "
                                 "would misread ('9' > '%d'), but misread was not flagged"
                           % (ENDTIME, ENDTIME))
        # cardinality: two names for one numeric time must REFUSE
        os.makedirs(os.path.join(tmpn, "%d.0" % ENDTIME))
        _ok = False
        try:
            select_endtime_dir(tmpn, ENDTIME)
        except Refusal as e:
            if "cardinality" in str(e):
                _ok = True
        if not _ok:
            control_failed("C7", "TIME-DIR CARDINALITY CONTROL FAILED: '%d' and '%d.0' denoting the "
                                 "same time were NOT refused" % (ENDTIME, ENDTIME))
        print("  time dir     numeric-max selects '%d' (lexicographic '9' would MISREAD); two names "
              "for one time REFUSE" % ENDTIME)
    finally:
        shutil.rmtree(tmpn, ignore_errors=True)

    # ---- C8  readers refuse a uniform field, a count mismatch, a headerless vector
    tmp = tempfile.mkdtemp(prefix="vmfl033r2_rd_")
    try:
        pth = os.path.join(tmp, "T")
        open(pth, "w").write("internalField   uniform 273;\n")
        _ok = False
        try:
            read_scalar_field(pth)
        except Refusal as e:
            if "UNIFORM" in str(e):
                _ok = True
        if not _ok:
            control_failed("C8", "READER CONTROL FAILED: a UNIFORM internalField was ACCEPTED")
        open(pth, "w").write("internalField   nonuniform List<scalar> 3 ( 1.0 2.0 );\n")
        _ok = False
        try:
            read_scalar_field(pth)
        except Refusal as e:
            if "header says" in str(e):
                _ok = True
        if not _ok:
            control_failed("C8", "READER CONTROL FAILED: a count/header mismatch was ACCEPTED")
        pth2 = os.path.join(tmp, "C")
        open(pth2, "w").write("dimensions [0 1 0 0 0 0 0];\n")
        _ok = False
        try:
            read_vector_field(pth2)
        except Refusal as e:
            if "List<vector>" in str(e):
                _ok = True
        if not _ok:
            control_failed("C8", "VECTOR READER CONTROL FAILED: a headerless vector file was ACCEPTED")
        print("  readers      UNIFORM field REFUSED; count/header mismatch REFUSED; headerless "
              "vector REFUSED")

        # ---- C9  strict completion refuses an EMPTY dir and a rc!=0 dir
        empty = os.path.join(tmp, "emptylevel")
        os.makedirs(empty)
        _ok = False
        try:
            completion(empty)
        except Refusal:
            _ok = True
        if not _ok:
            control_failed("C9", "COMPLETION CONTROL FAILED: an EMPTY directory PASSED completion")
        bad = os.path.join(tmp, "badrc")
        os.makedirs(bad)
        open(os.path.join(bad, "RUN_RC.txt"), "w").write("rc = 1\n")
        _ok = False
        try:
            completion(bad)
        except Refusal as e:
            if "non-zero exit is a FINDING" in str(e):
                _ok = True
        if not _ok:
            control_failed("C9", "COMPLETION CONTROL FAILED: a level recording rc=1 was NOT refused")
        print("  completion   an EMPTY level dir is REFUSED; a level recording rc=1 is REFUSED")

        # ---- C10  planted-zero: the production reader must SEE a plant on disk
        pf = os.path.join(tmp, "T_plant")
        _write_min_field_scalar(pf, [273.0, 273.5, 274.0])
        base = read_scalar_field(pf)
        _write_min_field_scalar(pf, [273.0 + PLANT, 273.5, 274.0])
        seen = read_scalar_field(pf)[0] - base[0]
        if abs(seen - PLANT) > 1e-12:
            control_failed("C10", "PLANT CONTROL FAILED: %g planted on disk, reader saw %g"
                           % (PLANT, seen))
        print("  plant        %g planted on disk into a real field file, production reader saw %g"
              % (PLANT, seen))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- C11  THE VERDICT DECISION -- every verdict must be REACHABLE (end-to-end arms)
    good_tr = roache(284.153139, 284.138526, 284.134873)      # a clean 2nd-order triple, p~2
    if good_tr["state"] != "CONVERGING":
        control_failed("C11", "the constructed clean triple did not classify CONVERGING")
    rows_pass = [{"dir": "L1", "rel_T": 6.0e-3}, {"dir": "L2", "rel_T": 2.8e-3},
                 {"dir": "L3", "rel_T": 5.0e-3}]              # finest inside the 1% band
    v, _ = decide_verdict(rows_pass, good_tr, [])
    if v != "PASS":
        control_failed("C11", "PASS ARM FAILED: an inside-band CONVERGING family returned %s" % v)
    rows_fail = [{"dir": "L1", "rel_T": 6.0e-3}, {"dir": "L2", "rel_T": 2.8e-3},
                 {"dir": "L3", "rel_T": 3.0e-2}]              # finest OUTSIDE the 1% band
    v, _ = decide_verdict(rows_fail, good_tr, [])
    if v != "GATE FAIL":
        control_failed("C11", "GATE-FAIL ARM FAILED: an outside-band CONVERGING family returned %s "
                              "-- the gate CANNOT return GATE FAIL, so it is not a gate" % v)
    v, _ = decide_verdict(rows_pass, good_tr, [rows_pass[0]])  # a level not settled
    if v != "NOT A RESULT":
        control_failed("C11", "NOT-A-RESULT (plateau) ARM FAILED: an unsettled level returned %s" % v)
    osc = roache(1.0, 1.1, 1.05)
    v, _ = decide_verdict(rows_pass, osc, [])                  # oscillatory triple
    if v != "NOT A RESULT":
        control_failed("C11", "NOT-A-RESULT (triple) ARM FAILED: an OSCILLATORY triple returned %s" % v)
    hi_gci = dict(good_tr)
    hi_gci["gci"] = GCI_MAX + 0.5                              # GCI above the ceiling
    v, _ = decide_verdict(rows_pass, hi_gci, [])
    if v != "NOT A RESULT":
        control_failed("C11", "NOT-A-RESULT (GCI_MAX) ARM FAILED: GCI above the ceiling returned %s" % v)
    lo_p = dict(good_tr)
    lo_p["p"] = P_MIN / 2.0                                    # order below the floor
    v, _ = decide_verdict(rows_pass, lo_p, [])
    if v != "NOT A RESULT":
        control_failed("C11", "NOT-A-RESULT (P_MIN) ARM FAILED: order below the floor returned %s" % v)
    print("  verdict      PASS, GATE FAIL and every NOT-A-RESULT cause (plateau, triple, GCI_MAX, "
          "P_MIN) are all REACHABLE from decide_verdict")

    print("-" * 78)
    print("SELFTEST GREEN")
    return 0


def _gauss(M, b):
    n = len(b)
    M = [row[:] for row in M]
    b = b[:]
    for c in range(n):
        pv = max(range(c, n), key=lambda rr: abs(M[rr][c]))
        M[c], M[pv] = M[pv], M[c]
        b[c], b[pv] = b[pv], b[c]
        for rr in range(c + 1, n):
            f = M[rr][c] / M[c][c]
            if f:
                for cc in range(c, n):
                    M[rr][cc] -= f * M[c][cc]
                b[rr] -= f * b[c]
    x = [0.0] * n
    for rr in range(n - 1, -1, -1):
        s = b[rr] - sum(M[rr][cc] * x[cc] for cc in range(rr + 1, n))
        x[rr] = s / M[rr][rr]
    return x


def _bvp_v(n):
    h = (R2_r - R1_r) / n
    rs = [R1_r + i * h for i in range(n + 1)]
    N = n + 1
    M = [[0.0] * N for _ in range(N)]
    b = [0.0] * N
    M[0][0] = 1.0
    b[0] = OM1
    M[N - 1][N - 1] = 1.0
    b[N - 1] = OM2
    for i in range(1, N - 1):
        rm, rp = 0.5 * (rs[i - 1] + rs[i]), 0.5 * (rs[i] + rs[i + 1])
        M[i][i - 1] = rm ** 3 / h ** 2
        M[i][i + 1] = rp ** 3 / h ** 2
        M[i][i] = -(rm ** 3 + rp ** 3) / h ** 2
    return rs, _gauss(M, b)


def _bvp_T(n, w):
    h = (R2_r - R1_r) / n
    rs = [R1_r + i * h for i in range(n + 1)]
    N = n + 1
    M = [[0.0] * N for _ in range(N)]
    b = [0.0] * N
    M[0][0] = 1.0
    b[0] = T1
    M[N - 1][N - 1] = 1.0
    b[N - 1] = T2
    for i in range(1, N - 1):
        rm, rp = 0.5 * (rs[i - 1] + rs[i]), 0.5 * (rs[i] + rs[i + 1])
        M[i][i - 1] = K_COND * rm / h ** 2
        M[i][i + 1] = K_COND * rp / h ** 2
        M[i][i] = -K_COND * (rm + rp) / h ** 2
        dwdr = (w[i + 1] - w[i - 1]) / (2 * h)
        b[i] = -rs[i] * MU * (rs[i] * dwdr) ** 2
    return rs, _gauss(M, b)


# ==================================== main =================================
def main(argv):
    ast_guard(os.path.abspath(__file__))     # this file must carry ZERO asserts
    if "--selftest" in argv:
        return selftest()
    print("VMFL033-R2 -- Viscous Heating in an Annulus.  COMPARATOR OUTPUT.")
    print("manual p.119; reference Bird, Stewart & Lightfoot (1960), CLOSED FORM.")
    print("R2 succeeds R1 (row #21, NOT A RESULT); R1 is NOT touched.  ONE change: endTime 20000->%d."
          % ENDTIME)
    print("run root %s" % RUN_ROOT)
    print("")
    selftest()
    print("")
    print("=" * 78)
    print("THE CLOSED FORM, evaluated (no digitisation, zero reference error)")
    print("=" * 78)
    print("  v(r) = %.15g r + (%.15g)/r" % (A_V, B_V))
    print("  T(r) = -(%.15g)/r^2 + (%.15g) ln r + (%.15g)" % (Q_T, C1_T, C2_T))
    print("  interior peak  r = %.12g   T = %.12g K   (walls are %g / %g K)"
          % (R_PEAK, T_PEAK, T1, T2))
    print("  viscous-heating rise above T1, the T normaliser : %.12g K" % T_SCALE)
    print("  volume-average T (the Roache functional)        : %.12g K" % T_volavg_exact())
    print("  inner-wall conductive flux -k dT/dr|_R1         : %.12g W/m2" % q_inner_exact())
    print("  ENERGY BALANCE (independent): dissipation %.9g W == net wall outflow %.9g W"
          % (total_dissipation_exact(), net_wall_outflow_exact()))
    print("")

    rows = []
    for lv in LEVELS:
        d = os.path.join(RUN_ROOT, lv)
        if not os.path.isdir(d):
            refuse("L0", "level directory %s does not exist" % d)
        rows.append(read_level(d))

    print("=" * 78)
    print("THE GRID FAMILY  (radial refinement, r = 2; theta held FIXED at 8 cells)")
    print("=" * 78)
    for r in rows:
        print("  %-10s cells=%-5d  Tavg=%.9f  |T-T_ex|max=%.4e K (%.4e of the %.4g K rise)"
              % (os.path.basename(r["dir"]), r["ncells"], r["Tavg"], r["err_T"], r["rel_T"], T_SCALE))
        print("             worst final residual=%.2e   plateau ptp/scale=%.3e over n_window=%d "
              "(floor %d)  lexicographic_would_have_misread=%s"
              % (r["worst_resid"], r["ptp_rel"], r["n_window"], PLATEAU_MIN, r["lex_misread"]))
        print("             [DIAGNOSTIC, NOT A DISCRIMINATOR] |v-v_ex|max=%.4e (%.4e of wall speed)"
              "  max|v_r|=%.2e" % (r["err_v"], r["rel_v"], r["vr_max"]))
    print("")

    # ---- planted controls AT EVERY LEVEL (R2 requirement 2)
    print("  CONTROLS -- planted-zero (rule 3), to DISK, through the production reader, AT EVERY LEVEL:")
    for r in rows:
        pc = plant_one_level(r["dir"])
        print("    %-10s field plant %g -> reader saw %.12g ;  geom x2 -> radius %.9g -> %.9g "
              "(required %.9g)" % (pc["level"], pc["plant"], pc["seen"], pc["r0"], pc["r_planted"],
                                   2 * pc["r0"]))
    print("")

    not_settled = [r for r in rows if r["ptp_rel"] > PLATEAU_PTP_REL]

    tr = roache(rows[0]["Tavg"], rows[1]["Tavg"], rows[2]["Tavg"], r=2.0)
    print("=" * 78)
    print("ROACHE TRIPLE on the volume-average temperature (rule 5) -- THE PHYSICS DISCRIMINATOR")
    print("=" * 78)
    print("  f_coarse=%.9f  f_med=%.9f  f_fine=%.9f" % (tr["f_coarse"], tr["f_med"], tr["f_fine"]))
    print("  d32=%.4e  d21=%.4e  R=%s  state=%s"
          % (tr["d32"], tr["d21"], ("%.6f" % tr["R"]) if tr["R"] is not None else "n/a", tr["state"]))
    if tr["state"] == "CONVERGING":
        flag = "  <-- SUSPICIOUSLY HIGH (above formal order %g)" % P_FORMAL \
               if tr["p"] > P_SUSPICIOUS else ""
        print("  observed order p_obs = %.4f (formal p_f = %g; floor P_MIN = %.3f)%s"
              % (tr["p"], P_FORMAL, P_MIN, flag))
        print("  GCI_fine at Fs = %.2f : %.6f%%   (ceiling GCI_MAX = %.1f%%)   Richardson f_ex = %.9f"
              % (FS_ROACHE, 100 * tr["gci"], 100 * GCI_MAX, tr["fex"]))
        print("  exact volume-average = %.9f ; the Richardson limit is %.4e K from it"
              % (T_volavg_exact(), abs(tr["fex"] - T_volavg_exact())))
    else:
        print("  NO GCI IS QUOTED: the triple is %s, not monotone-CONVERGING." % tr["state"])
    print("")

    fine = rows[-1]
    print("=" * 78)
    print("THE GATE, frozen before compute, applied at the finest level")
    print("=" * 78)
    print("  G_T temperature (THE GATE, physics discriminator):")
    print("      max|T - T_ex| / (Tpeak - T1) = %.6e   band %.3g   -> %s"
          % (fine["rel_T"], GATE_T_TOL, "INSIDE" if fine["rel_T"] <= GATE_T_TOL else "OUTSIDE"))
    print("  velocity (REPORTED, NOT A DISCRIMINATOR -- independent of every material property):")
    print("      max|v - v_ex| / (Om2*R2) = %.6e   report band %.3g   -> %s"
          % (fine["rel_v"], REPORT_V_TOL, "within" if fine["rel_v"] <= REPORT_V_TOL else "outside"))
    print("  REGISTERED EXPECTATIONS (reported either way, NEVER the gate):")
    print("      E_T T within %.3g : %s      E_v v within %.3g : %s"
          % (EXPECT_T_TOL, "MET" if fine["rel_T"] <= EXPECT_T_TOL else "NOT MET",
             EXPECT_V_TOL, "MET" if fine["rel_v"] <= EXPECT_V_TOL else "NOT MET"))
    print("")

    verdict, why = decide_verdict(rows, tr, not_settled)
    print("=" * 78)
    print("  VMFL033-R2 VERDICT: %s" % verdict)
    print("  %s" % why)
    print("  CEILING: PASS-CAPABLE per ANSYS_VERIFICATION_CHARTER Sec.11.1 (2026-08-30) -- a limb "
          "declaring a Roache triple that returns CONVERGING is graded by rule 5 step 3.  R1's "
          "frozen line 33 (GATE REACHED) predates Sec.11.1 by five days and is NOT edited (rule 6).")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ControlFailure as e:
        print("")
        print(str(e))
        print("A CONTROL DID NOT BEHAVE.  No SELFTEST GREEN line is printed and the comparator "
              "exits 2: a selftest that cannot fail is not evidence.")
        sys.exit(2)
    except Refusal as e:
        print("")
        print(str(e))
        print("The comparator REFUSES (exit 2) rather than degrade.")
        sys.exit(2)
