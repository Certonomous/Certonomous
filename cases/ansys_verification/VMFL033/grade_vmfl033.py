#!/usr/bin/env python3
# ===========================================================================
# VMFL033 -- Viscous Heating in an Annulus.  FROZEN COMPARATOR.
#
# Ansys Fluid Dynamics Verification Manual VM2026R1, p.119.
# Reference: R.B. Bird, W.E. Stewart, E.N. Lightfoot, "Transport Phenomena",
# John Wiley and Sons, New York, 1960.  The manual's own page says the problem
# "can be solved analytically" and that its figures compare against "the
# analytical solution provided by Bird et al (1960)".
#
# REFERENCE KIND: CLOSED-FORM / EXACT  -> buys V, NEVER P.  TIER CEILING:
# GATE REACHED.  The manual prints NO numeric table for this case, only two
# figures; this comparator therefore does NOT digitise anything.  It EVALUATES
# the closed form at whatever radii the mesh actually has, with zero
# digitisation error, and gates POINTWISE.
#
# CONTROLS (CLAUDE.md rules 3, 4, 5; PREREG_TEMPLATE Amendments 2, 3, 4):
#   * planted-zero controls on BOTH readers (fields and geometry), which REFUSE
#     if the reader cannot be shown able to see a non-zero;
#   * strict completion, refusing (exit 2) rather than degrading;
#   * endTime % writeInterval == 0 and a field directory AT endTime;
#   * a FIXED 500-sample plateau window with a minimum-sample REFUSAL, a
#     peak-to-peak statistic (which rejects a growing series) and a null-range
#     refusal, with the realised sample count recorded;
#   * Roache triple gating in rule 5's order.
#
# EVERY RADIUS IS READ BACK FROM OpenFOAM'S OWN `C` FIELD.  Nothing geometric
# is constructed from nr, dr, (j+1/2) or any such expression.
# ===========================================================================
import math, os, re, shutil, sys, tempfile

# ---------------------------------------------------------------- the case ---
RHO, CP, K_COND, MU = 1.0, 1.0, 1.0, 300.0     # VM2026R1 p.119, verbatim
R1, R2             = 1.0, 2.0                  # m
OM1, OM2           = 0.0, 0.5                  # rad/s
T1, T2             = 273.0, 274.0              # K

RUN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", "verification", "runs",
                        "ansys_verification", "VMFL033")
RUN_ROOT = os.path.normpath(RUN_ROOT)
LEVELS   = ["L1_nr32", "L2_nr64", "L3_nr128"]
ENDTIME  = 20000
# PREREG_TEMPLATE AMENDMENT 5: the required-field list is what the CONSUMER (this
# comparator) actually needs, INTERSECTED with the closure `constant/momentumTransport`
# actually names, and EXCLUDING solver-generated `phi`.  MEASURED, not assumed: a
# laminar `buoyantSimpleFoam` writes T U p p_rgh phi and NO `alphat`, so a naive
# enumeration from the fvSolution regex "(U|h|e|k|epsilon|omega)" would demand k,
# epsilon, omega and alphat of this case and REFUSE A CORRECT RUN.
REQUIRED_FIELDS = ["T", "U", "p", "p_rgh"]
TURBULENCE_FIELDS = {"kEpsilon": ["k", "epsilon", "nut"],
                     "kOmegaSST": ["k", "omega", "nut"],
                     "laminar": []}
SOLVER_GENERATED = {"phi"}          # never demanded of a run: the solver writes it itself

# ------------------------------------------------- THE FROZEN GATE (rule 2) ---
GATE_V_TOL   = 0.01     # max_cells |v_num - v_exact| / (OM2*R2)          <= 1%
GATE_T_TOL   = 0.01     # max_cells |T_num - T_exact| / (Tpeak_ex - T1)   <= 1%
EXPECT_V_TOL = 0.001    # REGISTERED EXPECTATION, not the gate: reported either way
EXPECT_T_TOL = 0.001
PLATEAU_WINDOW = 500    # FIXED, not a fraction (Amendment 4 item 1)
PLATEAU_MIN    = 500    # refuse below this (item 2)
PLATEAU_PTP_REL = 1.0e-6   # ptp over the window / (Tpeak_ex - T1); ptp REJECTS a trend (item 3)
FS_ROACHE      = 1.25
P_FORMAL       = 2.0
P_SUSPICIOUS   = 2.5    # declared IN ADVANCE: above this is a WARNING, never a win
PLANT = 1.234e-03


class Refusal(Exception):
    """Raised by the GRADING path when it will not degrade."""
    pass


class ControlFailure(Exception):
    """Raised ONLY by a selftest control whose subject failed to behave.

    It is a DIFFERENT TYPE from Refusal on purpose.  The controls below match
    an expected refusal by substring inside `except Refusal:` blocks, and a
    fall-through written as `refuse(...)` would be caught by that very handler
    whenever the control's own message happened to contain the substring it
    matches on -- SWALLOWING the control's failure.  That hazard was
    DEMONSTRATED, not theorised (ADDENDUM 01 sec.3).  ControlFailure is never
    caught by any `except Refusal`, so a broken control CANNOT be swallowed.
    """
    pass


def control_failed(code, msg):
    raise ControlFailure("CONTROL FAILED [%s]: %s" % (code, msg))


def refuse(code, msg):
    raise Refusal("REFUSAL [%s]: %s" % (code, msg))


# =============================== THE CLOSED FORM ===========================
# theta-momentum for purely tangential, steady, constant-property flow:
#     d/dr [ (1/r) d(r v)/dr ] = 0     ->    v(r) = A r + B/r
# energy, with v_r == 0 so there is NO radial convection of heat:
#     (k/r) d/dr( r dT/dr ) + mu*Phi = 0,   Phi = [ r d(v/r)/dr ]^2 = 4 B^2 / r^4
#     ->  T(r) = -(mu B^2 / k) / r^2 + C1 ln r + C2
# Constants fixed by v(R1)=OM1*R1, v(R2)=OM2*R2, T(R1)=T1, T(R2)=T2.
A_V = (OM2 * R2 * R2 - OM1 * R1 * R1) / (R2 * R2 - R1 * R1)
B_V = (OM1 - OM2) * R1 * R1 * R2 * R2 / (R2 * R2 - R1 * R1)
Q_T = MU * B_V * B_V / K_COND
C1_T = ((T2 - T1) - Q_T * (1.0 / (R1 * R1) - 1.0 / (R2 * R2))) / math.log(R2 / R1)
C2_T = T1 + Q_T / (R1 * R1) - C1_T * math.log(R1)


def v_exact(r):
    return A_V * r + B_V / r


def T_exact(r):
    return -Q_T / (r * r) + C1_T * math.log(r) + C2_T


R_PEAK = math.sqrt(-2.0 * Q_T / C1_T)     # dT/dr = 2Q/r^3 + C1/r = 0
T_PEAK = T_exact(R_PEAK)
T_SCALE = T_PEAK - T1                     # the viscous-heating rise; the T normaliser
V_SCALE = OM2 * R2                        # the moving-wall speed; the v normaliser


def T_volavg_exact():
    """Volume-weighted mean of T over the annulus: int T r dr / int r dr.
    Cell volumes in the sector go as r dr dtheta dz, so this is exactly what
    OpenFOAM's volAverage converges to."""
    def I(r):
        return (-Q_T * math.log(r)
                + C1_T * (r * r / 2.0 * math.log(r) - r * r / 4.0)
                + C2_T * r * r / 2.0)
    return (I(R2) - I(R1)) / ((R2 * R2 - R1 * R1) / 2.0)


def q_inner_exact():
    """Inward conductive flux at r=R1: -k dT/dr."""
    return -K_COND * (2.0 * Q_T / R1 ** 3 + C1_T / R1)


# ======================= OpenFOAM ascii field readers ======================
_NUM = r"[-+0-9.eEdD]+"


def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    return re.sub(r"//[^\n]*", " ", txt)


def read_scalar_field(path):
    """internalField of an ascii volScalarField, uniform or nonuniform."""
    if not os.path.isfile(path):
        refuse("F1", "no field file at %s" % path)
    txt = _strip(open(path).read())
    m = re.search(r"internalField\s+uniform\s+(" + _NUM + r")\s*;", txt)
    if m:
        refuse("F2", "%s has a UNIFORM internalField -- a uniform field is not a "
                     "solved field and this comparator will not read one as evidence" % path)
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
    """volFieldValue.dat written by the Tmean function object: one row per iteration."""
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
    times = sorted(float(d) for d in os.listdir(level_dir)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d)
                   and os.path.isdir(os.path.join(level_dir, d)) and float(d) > 0)
    if not times:
        refuse("C3", "no time directories in %s" % level_dir)
    if abs(times[-1] - ENDTIME) > 1e-9:
        refuse("C3", "last time %g is not endTime %d in %s" % (times[-1], ENDTIME, level_dir))
    nex = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if nex != ENDTIME:
        refuse("C5", "ExecutionTime count is %d against endTime %d in %s -- rule 4's "
                     "iteration-count clause is NOT met" % (nex, ENDTIME, level_dir))
    # endTime must be an exact multiple of writeInterval, and the dir must exist
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
    tdir = os.path.join(level_dir, str(int(ENDTIME)))
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
    return max(res.values()), res


# ================================ plateau (Amendment 4) ====================
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


# ================================ one level ================================
def read_level(level_dir):
    worst, res = completion(level_dir)
    tdir = os.path.join(level_dir, str(int(ENDTIME)))
    C = read_vector_field(os.path.join(tdir, "C"))      # RADII READ BACK FROM OpenFOAM
    U = read_vector_field(os.path.join(tdir, "U"))
    T = read_scalar_field(os.path.join(tdir, "T"))
    if not (len(C) == len(U) == len(T)):
        refuse("F5", "%s: C/U/T lengths differ (%d/%d/%d)" % (level_dir, len(C), len(U), len(T)))
    ev = et = 0.0
    vr_max = 0.0
    for (x, y, _z), (ux, uy, uz), t in zip(C, U, T):
        r = math.hypot(x, y)
        if r < R1 - 1e-9 or r > R2 + 1e-9:
            refuse("G1", "%s: a cell centre sits at r=%.12g, outside [%g,%g] -- the mesh is not "
                         "the registered annulus" % (level_dir, r, R1, R2))
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
            "ptp_rel": ptp / T_SCALE,
            "Tmax": max(T), "rc": kv(os.path.join(level_dir, "RUN_RC.txt"))}


# ============================== planted controls (rule 3) ==================
def planted_controls(level_dir):
    """Plant into COPIES of the real artifacts and read them back."""
    tdir = os.path.join(level_dir, str(int(ENDTIME)))
    tmp = tempfile.mkdtemp(prefix="vmfl033_plant_")
    try:
        # ---- unplanted copy must read back as itself
        src = os.path.join(tdir, "T")
        dst = os.path.join(tmp, "T")
        shutil.copy(src, dst)
        base = read_scalar_field(dst)
        truth = read_scalar_field(src)
        if base != truth:
            refuse("P0", "the UNPLANTED copy of %s does not read back as itself" % src)
        # ---- plant a known perturbation into the FIRST value, by index
        txt = open(dst).read()
        first = "%.12g" % base[0]
        planted_val = base[0] + PLANT
        idx = txt.index("(", txt.index("internalField"))
        head, tail = txt[:idx + 1], txt[idx + 1:]
        mfirst = re.search(_NUM, tail)
        tail = tail[:mfirst.start()] + repr(planted_val) + tail[mfirst.end():]
        open(dst, "w").write(head + tail)
        got = read_scalar_field(dst)
        seen = got[0] - base[0]
        if abs(seen - PLANT) > 1e-12:
            refuse("P1", "PLANTED-ZERO CONTROL FAILED: %g was planted into a copy of %s and the "
                         "reader saw %g -- a reader not shown able to see a non-zero cannot be "
                         "trusted to report a zero" % (PLANT, src, seen))
        # ---- geometry reader: scale every cell centre by 2, radii must double
        csrc, cdst = os.path.join(tdir, "C"), os.path.join(tmp, "C")
        shutil.copy(csrc, cdst)
        C0 = read_vector_field(cdst)
        ctxt = open(cdst).read()
        m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*(\d+)?\s*\(", _strip(ctxt))
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
            refuse("P2", "PLANTED-ZERO CONTROL FAILED: every cell centre in a copy of %s was "
                         "scaled by 2 and the geometry reader read radius %.12g against a "
                         "required %.12g" % (csrc, r1f, 2.0 * r0))
        return {"plant": PLANT, "seen": seen, "r0": r0, "r_planted": r1f, "unused": first}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =================================== selftest ==============================
def selftest():
    """Every control below has EXACTLY ONE path that lets the selftest continue:
    the one where its subject behaved.  Every other path raises ControlFailure,
    which no `except Refusal` catches.  Break any control and the terminal
    SELFTEST GREEN line becomes UNREACHABLE -- verified by mutation, not by
    reading (ADDENDUM 01 sec.2)."""
    print("VMFL033 comparator --selftest   (ZERO compute; no run directory is read)")
    print("-" * 78)

    # ---- C1  closed form satisfies its own boundary conditions
    for r, want in ((R1, OM1 * R1), (R2, OM2 * R2)):
        if abs(v_exact(r) - want) > 1e-12:
            control_failed("C1", "v_exact(%g) = %g, want %g" % (r, v_exact(r), want))
    for r, want in ((R1, T1), (R2, T2)):
        if abs(T_exact(r) - want) > 1e-9:
            control_failed("C1", "T_exact(%g) = %g, want %g" % (r, T_exact(r), want))
    print("  closed form  BCs exact: v(%g)=%.1e v(%g)=%.12g  T(%g)=%.12g T(%g)=%.12g"
          % (R1, v_exact(R1), R2, v_exact(R2), R1, T_exact(R1), R2, T_exact(R2)))

    # ---- C2  an INDEPENDENT numerical BVP that never uses the closed form
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

    # ---- C3  Roache classifier must SEE every state, and be exact on a 2nd-order triple
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
    print("  roache       every state SEEN: CONVERGING, DIVERGENT, EXACT, OSCILLATORY, STAGNANT; "
          "an exact 2nd-order triple returns p=2 to 1e-9")

    # ---- C4  plateau: too few samples must REFUSE
    _ok = False
    try:
        plateau([(i, 1.0 + 1e-9 * i) for i in range(PLATEAU_MIN - 1)])
    except Refusal as e:
        if "CANNOT_TELL" in str(e):
            _ok = True
    if not _ok:
        control_failed("C4", "PLATEAU MINIMUM-SAMPLE CONTROL FAILED: a %d-sample series was NOT "
                             "refused with CANNOT_TELL" % (PLATEAU_MIN - 1))

    # ---- C5  plateau: a dead-flat series must REFUSE (null range)
    _ok = False
    try:
        plateau([(i, 5.0) for i in range(PLATEAU_MIN + 10)])
    except Refusal as e:
        if "NULL RANGE" in str(e):
            _ok = True
    if not _ok:
        control_failed("C5", "PLATEAU NULL-RANGE CONTROL FAILED: a dead-flat series was NOT "
                             "refused -- a dead field and a converged one would look identical")

    # ---- C6  plateau: a monotonically GROWING series must be REJECTED by the statistic
    ptp_g, n_g, _ = plateau([(i, 1.0 + 1e-3 * i) for i in range(PLATEAU_MIN + 10)])
    if ptp_g / T_SCALE <= PLATEAU_PTP_REL:
        control_failed("C6", "TREND-REJECTION CONTROL FAILED: a MONOTONICALLY GROWING series "
                             "passed the plateau tolerance (ptp/scale = %.3e <= %.1e)"
                       % (ptp_g / T_SCALE, PLATEAU_PTP_REL))
    print("  plateau      %d-sample floor REFUSES; a null range REFUSES; a growing series is "
          "REJECTED (ptp/scale = %.3e > %.1e)" % (PLATEAU_MIN, ptp_g / T_SCALE, PLATEAU_PTP_REL))

    tmp = tempfile.mkdtemp(prefix="vmfl033_st_")
    try:
        # ---- C7  the scalar reader must REFUSE a UNIFORM internalField
        pth = os.path.join(tmp, "T")
        open(pth, "w").write("internalField   uniform 273;\n")
        _ok = False
        try:
            read_scalar_field(pth)
        except Refusal as e:
            if "UNIFORM" in str(e):
                _ok = True
        if not _ok:
            control_failed("C7", "READER CONTROL FAILED: a UNIFORM internalField was ACCEPTED "
                                 "as evidence instead of being refused")

        # ---- C8  the scalar reader must REFUSE a count/header mismatch
        open(pth, "w").write("internalField   nonuniform List<scalar> 3 ( 1.0 2.0 );\n")
        _ok = False
        try:
            read_scalar_field(pth)
        except Refusal as e:
            if "header says" in str(e):
                _ok = True
        if not _ok:
            control_failed("C8", "READER CONTROL FAILED: a list whose count disagrees with its "
                                 "own header was ACCEPTED")

        # ---- C9  the VECTOR reader must REFUSE a missing internalField
        pth2 = os.path.join(tmp, "C")
        open(pth2, "w").write("dimensions [0 1 0 0 0 0 0];\n")
        _ok = False
        try:
            read_vector_field(pth2)
        except Refusal as e:
            if "List<vector>" in str(e):
                _ok = True
        if not _ok:
            control_failed("C9", "VECTOR READER CONTROL FAILED: a file with NO internalField was "
                                 "ACCEPTED")
        print("  readers      a UNIFORM internalField is REFUSED; a count/header mismatch is "
              "REFUSED; a headerless vector file is REFUSED")

        # ---- C10  STRICT COMPLETION must refuse an EMPTY directory.
        #      This control was MISSING from the frozen selftest, and its absence is exactly
        #      what let a mutated completion() still print SELFTEST GREEN (ADDENDUM 01 sec.2).
        empty = os.path.join(tmp, "emptylevel")
        os.makedirs(empty)
        _ok = False
        try:
            completion(empty)
        except Refusal:
            _ok = True
        if not _ok:
            control_failed("C10", "COMPLETION CONTROL FAILED: an EMPTY directory PASSED the "
                                  "strict-completion check instead of being refused -- rule 4 "
                                  "refuses (exit 2) rather than degrades")

        # ---- C11  strict completion must refuse a directory whose RUN_RC records a NON-ZERO rc
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
            control_failed("C11", "COMPLETION CONTROL FAILED: a level recording rc=1 was NOT "
                                  "refused as a finding")
        print("  completion   an EMPTY level dir is REFUSED; a level recording rc=1 is REFUSED "
              "as a FINDING (rule 4 refuses, never degrades)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

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
    h = (R2 - R1) / n
    rs = [R1 + i * h for i in range(n + 1)]
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
    h = (R2 - R1) / n
    rs = [R1 + i * h for i in range(n + 1)]
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
    if "--selftest" in argv:
        return selftest()
    print("VMFL033 -- Viscous Heating in an Annulus.  COMPARATOR OUTPUT.")
    print("manual p.119; reference Bird, Stewart & Lightfoot (1960), CLOSED FORM -> buys V, "
          "never P; TIER CEILING GATE REACHED")
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
    print("")

    rows = []
    for lv in LEVELS:
        d = os.path.join(RUN_ROOT, lv)
        if not os.path.isdir(d):
            refuse("L0", "level directory %s does not exist" % d)
        rows.append(read_level(d))

    print("=" * 78)
    print("THE GRID FAMILY  (radial refinement, r = 2; theta held FIXED at 8 cells because the")
    print("exact solution is theta-invariant and carries no azimuthal discretisation error)")
    print("=" * 78)
    for r in rows:
        print("  %-10s cells=%-5d  Tavg=%.9f  |v-v_ex|max=%.4e (%.4e of wall speed)"
              % (os.path.basename(r["dir"]), r["ncells"], r["Tavg"], r["err_v"], r["rel_v"]))
        print("             |T-T_ex|max=%.4e K (%.4e of the %.4g K rise)  max|v_r|=%.2e"
              % (r["err_T"], r["rel_T"], T_SCALE, r["vr_max"]))
        print("             worst final residual=%.2e   plateau ptp/scale=%.3e over n_window=%d "
              "(fixed, floor %d)  full-series range=%.4g K"
              % (r["worst_resid"], r["ptp_rel"], r["n_window"], PLATEAU_MIN, r["ptp_full"]))
    print("")

    # ---- planted controls, on the finest level's REAL artifacts
    pc = planted_controls(rows[-1]["dir"])
    print("  CONTROL field plant : %g planted into a COPY of the finest level's T; the reader saw "
          "%.12g.  The reader is shown able to see a NON-ZERO." % (pc["plant"], pc["seen"]))
    print("  CONTROL geom  plant : every cell centre of a COPY of the finest level's C scaled by "
          "2; radius %.9g -> %.9g (required %.9g).  The geometry reader is shown able to see a "
          "CHANGED geometry." % (pc["r0"], pc["r_planted"], 2 * pc["r0"]))
    print("")

    # ---- plateau gating, in rule 5's order: step (1) comes FIRST
    not_settled = [r for r in rows if r["ptp_rel"] > PLATEAU_PTP_REL]

    tr = roache(rows[0]["Tavg"], rows[1]["Tavg"], rows[2]["Tavg"], r=2.0)
    print("=" * 78)
    print("ROACHE TRIPLE on the volume-average temperature (rule 5)")
    print("=" * 78)
    print("  f_coarse=%.9f  f_med=%.9f  f_fine=%.9f" % (tr["f_coarse"], tr["f_med"], tr["f_fine"]))
    print("  d32=%.4e  d21=%.4e  R=%s  state=%s"
          % (tr["d32"], tr["d21"], ("%.6f" % tr["R"]) if tr["R"] is not None else "n/a",
             tr["state"]))
    if tr["state"] == "CONVERGING":
        flag = "  <-- SUSPICIOUSLY HIGH (above the formal order %g)" % P_FORMAL \
               if tr["p"] > P_SUSPICIOUS else ""
        print("  observed order p_obs = %.4f (formal p_f = %g)%s" % (tr["p"], P_FORMAL, flag))
        print("  GCI_fine at Fs = %.2f : %.6f%%   Richardson f_ex = %.9f"
              % (FS_ROACHE, 100 * tr["gci"], tr["fex"]))
        print("  exact volume-average = %.9f ; the Richardson limit is %.4e K from it"
              % (T_volavg_exact(), abs(tr["fex"] - T_volavg_exact())))
    else:
        print("  NO GCI IS QUOTED: the triple is %s, not monotone-CONVERGING." % tr["state"])
    print("")

    fine = rows[-1]
    print("=" * 78)
    print("THE GATE, frozen before compute, applied at the finest level")
    print("=" * 78)
    print("  G1 velocity    : max|v - v_ex| / (Om2*R2)      = %.6e   band %.3g   -> %s"
          % (fine["rel_v"], GATE_V_TOL, "INSIDE" if fine["rel_v"] <= GATE_V_TOL else "OUTSIDE"))
    print("  G2 temperature : max|T - T_ex| / (Tpeak - T1)  = %.6e   band %.3g   -> %s"
          % (fine["rel_T"], GATE_T_TOL, "INSIDE" if fine["rel_T"] <= GATE_T_TOL else "OUTSIDE"))
    print("  REGISTERED EXPECTATIONS (reported either way, NEVER the gate):")
    print("    E1 v within %.3g : %s      E2 T within %.3g : %s"
          % (EXPECT_V_TOL, "MET" if fine["rel_v"] <= EXPECT_V_TOL else "NOT MET",
             EXPECT_T_TOL, "MET" if fine["rel_T"] <= EXPECT_T_TOL else "NOT MET"))
    print("")

    # ---------------- rule 5's ORDER: (1) settling, (2) triple, (3) band ----
    reasons = []
    if not_settled:
        reasons.append("levels not plateaued: %s"
                       % ", ".join(os.path.basename(r["dir"]) for r in not_settled))
    if tr["state"] != "CONVERGING":
        reasons.append("Roache triple is %s, not CONVERGING" % tr["state"])
    inside = fine["rel_v"] <= GATE_V_TOL and fine["rel_T"] <= GATE_T_TOL

    if reasons:
        verdict = "NOT A RESULT"
        why = "; ".join(reasons)
    elif inside:
        verdict = "GATE REACHED"
        why = ("both pointwise bands met at the finest level; the CEILING is GATE REACHED "
               "because a closed-form reference buys V and NEVER P")
    else:
        verdict = "GATE FAIL"
        why = "the triple converges and the levels are settled, but a pointwise band is missed"

    print("=" * 78)
    print("  VMFL033 VERDICT: %s" % verdict)
    print("  %s" % why)
    print("  TIER CEILING GATE REACHED -- a closed-form reference buys V (code verification), "
          "NEVER P.  This is NOT a validation credential.")
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
