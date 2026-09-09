#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL007-R3 -- Non-Newtonian (power-law) Flow in a Pipe.
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 29.

NEW three-level Roache triple (ANSYS_VERIFICATION_CHARTER sec.6) that cites, and
never overwrites, register row #8 (VMFL007 run 1, DIVERGED) and row #37
(VMFL007-R2 single-grid solver slate, NOT A RESULT). The R2 slate existed to find
a stable solver arm for THIS triple; the finer meshes were then made to CONVERGE by
the SINGLE answer-blind lever SIMPLE -> SIMPLEC (system/fvSolution), the root cause
being the SIMPLE velocity-correction inconsistency, not the bounded nuMin floor
(ARM_SELECTION.md sec.3; verified: under-relaxation only postpones the blow-up, a
stronger Krylov U solve worsens it, SIMPLEC removes it). Fluid inputs and fvSchemes
are byte-identical to run 1 -- no lower-order scheme, no fluid change.

THE GATE QUANTITY is a SINGLE SCALAR per level:
    dp = RHO * ( <p>_inlet - <p>_outlet )    (kinematic p area-averaged on each end
    patch by the frozen surfaceFieldValue monitors, RHO = 1000), read at the run's
    MAX iteration -- one scalar, so the planted-zero plant lands on the exact value
    the gate reads with NO averaging dilution (L-340).

GATE (carried BYTE-IDENTICAL from VMFL007 run-1's freeze; PREREGISTRATION.md sec.6;
never re-derived from any number):
    |dp - 60520| / 60520 <= 0.005      band [60217.40, 60822.60] Pa
    AND a CONVERGING Roache triple on dp (CLAUDE.md rule 5).
CEILING: PASS. The supervisor ruled sec.12.2 = SAME / PASS-capable
    (VERIFICATION_CHARTER sec.2h.8.1 exact-PDE rule; precedent VMFL004-R2 row #28):
    under the frozen fully-developed inlet BC the convective term vanishes
    IDENTICALLY, so the full incompressible power-law NS system the solver
    discretises reduces EXACTLY to the 1-D ODE the Hughes-Brighton closed form
    solves. The comparator can therefore print PASS; a flat inlet would be DIFFERENT
    and this is machine-checked (UmaxInlet peak 3.1429, QInlet mean 2, below).

CONVERGENCE CLAUSE (rule 5 limb 1, one-way; ANSYS sec.16.4; N-AV15). The L3
100x100 field carries a DISCLOSED single-cell entry-region max(nu) limit cycle, so
a plateau written as "ptp -> 0" is unsatisfiable and is NEVER written. A level is
convergent iff BOTH, each VALUE-BLIND (never referencing the reference or the band):
   (a) FUNCTIONAL PLATEAU: peak-to-peak of dp over the last W_PLATEAU = 5000
       iterations is below PLATEAU_THRESH_PA = 1e-2 Pa (1.65e-7 relative -- it
       cannot backdoor-widen the 0.5%% gate; it references the convergence NOISE
       FLOOR, not the reference).
   (b) RESIDUALS SETTLED, NOT STILL FALLING: over the same window the Ux and p
       initial residuals have not dropped by more than RESID_FALL_FACTOR = 3x
       (median first half / median last half). This is NOT a hard 1e-8 (the limit
       cycle floors p at ~1.5e-8 and prevents it); a STILL-FALLING residual ->
       NOT A RESULT.
A level failing either -> the verdict is NOT A RESULT, all dp values printed, via
the SINGLE verdict path, which can never turn NOT A RESULT into PASS.

CONTROLS (CLAUDE.md rules 3, 4, 5):
  * planted-zero -- a known perturbation is planted into a COPY of the pInlet
    monitor's MAX-iteration value, read back FROM DISK, and the reader REFUSES
    (exit 2) if dp does not move by exactly RHO*PLANT. Single scalar into single
    scalar (no 1/sqrt(N) dilution, L-340). A blind reader is shown to REFUSE.
  * plateau + residual-settled controls -- constructed series drive the real
    clause: a series with ptp above threshold is NOT plateaued; a still-falling
    residual is NOT settled; the flat/floored cases pass.
  * Roache triple + observed-order floor P_MIN with its own planted control.
  * strict completion (rule 4, FIXED-endTime variant: last time == endTime, not
    "< endTime" -- this run does NOT stop on residualControl, it runs the budget)
    with L-342 field classes (absent infrastructure -> NOT MEASURED, grade
    proceeds; a bad/absent PHYSICS field REFUSES); age guard.

NO `assert` ANYWHERE (`python3 -O` deletes every assert, L-332): every refusal is
SystemExit2. `--selftest` is IDENTICAL under `python3` and `python3 -O`.
`--verify-frozen <commit>` confirms this file and the prereg equal their blobs at
<commit> (rule 2). Verdict vocabulary only:
PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
"""
import os, re, sys, json, glob, math, shutil, tempfile, subprocess

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL007-R3")
LEVELS   = ["L1", "L2", "L3"]

GRADER_REL = "cases/ansys_verification/VMFL007-R3/grade_vmfl007_r3.py"
PREREG_REL = "cases/ansys_verification/VMFL007-R3/PREREGISTRATION.md"

# --- FROZEN GATE, carried BYTE-IDENTICAL from run 1 (never re-derived) --------
REF_PA   = 60520.0          # manual printed target 60.52 kPa; the gate centre
TOL      = 0.005            # 0.5 % relative band
BAND_LO  = 60217.40         # = REF_PA * (1 - TOL); byte-identical to run 1
BAND_HI  = 60822.60         # = REF_PA * (1 + TOL)
RHO      = 1000.0           # kg/m3; kinematic p -> Pa. Derivation below.
_K_MANUAL, _K_KINEMATIC = 10.0, 0.01     # manual k = 10 Pa.s^n; case runs 0.01 kinematic
# CONTEXT ONLY, never the gate:
CLOSED_FORM_PA = 60521.969  # Rabinowitsch-Mooney / Hughes-Brighton exact (inside band)
ANSYS_FLUENT_PA = 60410.0   # manual Table .07.1 (60.41 kPa, ratio 0.998)
ANSYS_CFX_PA    = 61520.0   # manual Table .07.2 (61.52 kPa, ratio 1.0165)

# --- Roache / convergence constants (frozen) ----------------------------------
FS        = 1.25            # GCI safety factor
RATIO     = 2.0             # r = 2 isotropic refinement
P_MIN     = 0.05            # observed-order floor
W_PLATEAU = 5000            # fixed ABSOLUTE plateau window (iterations), not a fraction
PLATEAU_THRESH_PA  = 1.0e-2 # functional-plateau ceiling on dp ptp; value-blind
RESID_FALL_FACTOR  = 3.0    # residual "still falling" threshold over the window

# --- machine-checked SAME precondition + viscosity class (answer-blind) -------
UMAX_DEV_PROFILE = 3.142857 # developed power-law centreline peak (mean 2 m/s)
UMAX_TOL         = 0.02     # a flat 2 m/s slug would read 2.0, not 3.1429
QMEAN_NOMINAL    = 2.0      # mean inlet velocity, m/s
QMEAN_TOL        = 0.02
NUMIN, NUMAX     = 1e-8, 1.0

# --- planted-zero perturbation ------------------------------------------------
PLANT     = 1.234e-03       # kinematic m2/s2 planted into pInlet -> dp moves RHO*PLANT

FIELD_CLASSES = {
    "physics_critical": [
        "log.simpleFoam (End line; exact name, never a log* glob)",
        "log.simpleFoam Time / ExecutionTime counts (== endTime, ran the budget)",
        "log.simpleFoam ZERO 'Courant Number' lines (steady solve)",
        "system/controlDict endTime (last time == endTime)",
        "postProcessing/{pInlet,pOutlet} surfaceFieldValue.dat (the gate series)",
        "<endTime>/U, <endTime>/p (fields present)",
        "0/U (the age-guard datum)",
    ],
    "infrastructure": [
        "RUN_RC.<level> rc / wall_s / core_min (launcher bookkeeping, L-342)",
        "COST.txt (run-root cost roll-up)",
    ],
}


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSED (exit 2): %s\n" % msg)
        SystemExit.__init__(self, 2)


# --------------------------------------------------------------- RHO sanity ----
def _rho_ok():
    # NAMED with its derivation rather than left as a bare literal: an incompressible
    # case stores only kinematic transport, so RHO = k_manual / k_kinematic = 1000.
    return abs(RHO - _K_MANUAL / _K_KINEMATIC) < 1e-9


# ------------------------------------------------------------------- readers ---
def one_or_refuse(paths, what):
    """Return the single matching path, or REFUSE (exit 2). Ambiguity (a restart,
    a stale directory) is refused, never resolved by a hidden convention."""
    ps = sorted(paths)
    if len(ps) != 1:
        raise SystemExit2("%s matched %d paths %r -- ambiguous (restart or stale dir); "
                          "REFUSING rather than guessing which is current" % (what, len(ps), ps))
    return ps[0]


def _monitor_path(level_dir, name):
    return one_or_refuse(
        glob.glob(os.path.join(level_dir, "postProcessing", name, "*", "surfaceFieldValue.dat")),
        "%s/postProcessing/%s" % (level_dir, name))


def read_scalar_series(level_dir, name):
    """[(iter, scalar)] from an OpenFOAM surfaceFieldValue .dat (last column)."""
    out = []
    for ln in open(_monitor_path(level_dir, name)):
        if ln.startswith("#"):
            continue
        q = ln.split()
        if len(q) >= 2:
            out.append((int(float(q[0])), float(q[-1])))
    return out


def read_vector_x_series(level_dir, name):
    """[(iter, x_component)] from a vector surfaceFieldValue .dat: 'iter (x y z)'."""
    out = []
    for ln in open(_monitor_path(level_dir, name)):
        if ln.startswith("#"):
            continue
        m = re.match(r"\s*(\d+)\s+\(([^()]*)\)", ln)
        if m:
            out.append((int(m.group(1)), float(m.group(2).split()[0])))
    return out


def read_area(level_dir, name):
    """The '# Area' header of a surfaceFieldValue .dat (m2), or None."""
    for ln in open(_monitor_path(level_dir, name)):
        if not ln.startswith("#"):
            break
        m = re.search(r"Area\s*:\s*([0-9.eE+-]+)", ln)
        if m:
            return float(m.group(1))
    return None


def dp_series(level_dir):
    """dp(iter) = RHO*(pInlet - pOutlet) aligned on common iterations."""
    din = dict(read_scalar_series(level_dir, "pInlet"))
    dout = dict(read_scalar_series(level_dir, "pOutlet"))
    ks = sorted(set(din) & set(dout))
    if not ks:
        raise SystemExit2("%s: pInlet and pOutlet share no iterations" % level_dir)
    return [(k, RHO * (din[k] - dout[k])) for k in ks]


def dp_at_endtime(dp):
    """The gate value: the SINGLE dp scalar at the maximum iteration."""
    return dp[-1][1], dp[-1][0]


def dp_plateau_ptp(dp, w=W_PLATEAU):
    tail = [v for _, v in dp[-w:]]
    return max(tail) - min(tail), len(tail)


# ------------------------------------------------------- residual settling -----
def read_initial_residuals(level_dir, field):
    """[float] per-iteration initial residual for `field` (Ux or p)."""
    log = os.path.join(level_dir, "log.simpleFoam")
    pat = re.compile(r"Solving for %s,\s*Initial residual = ([0-9.eE+-]+)" % re.escape(field))
    return [float(m.group(1)) for m in pat.finditer(open(log, errors="replace").read())]


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def residual_fall_ratio(res, w=W_PLATEAU):
    """median(first half of the last w) / median(last half). >1 means still
    falling; ~1 means settled/floored. Value-blind (the residual's own trend)."""
    tail = res[-w:]
    if len(tail) < 4:
        return None
    half = len(tail) // 2
    lo = _median([max(x, 1e-300) for x in tail[:half]])
    hi = _median([max(x, 1e-300) for x in tail[half:]])
    return lo / max(hi, 1e-300)


def convergence(level_dir):
    """The rule-5-limb-1 convergence evidence for one level. Returns a dict with
    `plateaued`, `residuals_settled` and the numbers; it does NOT itself decide the
    verdict -- verdict_for() does, on all levels at once, so there is ONE path."""
    dp = dp_series(level_dir)
    ptp, nwin = dp_plateau_ptp(dp)
    end_val, end_it = dp_at_endtime(dp)
    ux = read_initial_residuals(level_dir, "Ux")
    pr = read_initial_residuals(level_dir, "p")
    fux = residual_fall_ratio(ux)
    fpr = residual_fall_ratio(pr)
    settled = (fux is not None and fpr is not None
               and fux <= RESID_FALL_FACTOR and fpr <= RESID_FALL_FACTOR)
    return {"dp_endtime_pa": end_val, "endtime_iter": end_it,
            "plateau_ptp_pa": ptp, "plateau_window": nwin,
            "plateaued": ptp < PLATEAU_THRESH_PA,
            "resid_fall_Ux": fux, "resid_fall_p": fpr,
            "resid_endtime_Ux": (ux[-1] if ux else None),
            "resid_endtime_p": (pr[-1] if pr else None),
            "residuals_settled": settled}


# -------------------------------------- SAME precondition + viscosity class ----
def same_precondition(level_dir):
    """Machine-check the frozen developed inlet BC at grade time (the load-bearing
    sec.12.2 SAME precondition): peak U = 3.1429 (not a flat 2.0 slug) and mean
    U = 2.0. Answer-blind: about the BC, never about dp or the reference."""
    umax = read_vector_x_series(level_dir, "UmaxInlet")[-1][1]
    q = read_scalar_series(level_dir, "QInlet")[-1][1]
    area = read_area(level_dir, "pInlet")
    if area is None or area <= 0.0:
        raise SystemExit2("%s: cannot read inlet Area from the pInlet monitor header" % level_dir)
    mean_u = abs(q) / area
    if abs(umax - UMAX_DEV_PROFILE) > UMAX_TOL:
        raise SystemExit2("%s: inlet peak U = %.6f, not the developed %.6f (+/- %.3g) -- a flat "
                          "slug would be 2.0 and the sec.12.2 SAME precondition would FAIL"
                          % (level_dir, umax, UMAX_DEV_PROFILE, UMAX_TOL))
    if abs(mean_u - QMEAN_NOMINAL) > QMEAN_TOL:
        raise SystemExit2("%s: inlet mean U = %.6f, not %.4g (+/- %.3g)"
                          % (level_dir, mean_u, QMEAN_NOMINAL, QMEAN_TOL))
    return {"inlet_peak_U": umax, "inlet_mean_U": mean_u, "inlet_area_m2": area}


def viscosity_class(level_dir):
    """Prove the powerLaw clips never bind at endTime (nuMin/nuMax headroom) --
    the run-1/R2 nuMin floor was the divergence killer, so its non-binding must be
    a READING, not an assumption. Answer-blind."""
    numin = read_scalar_series(level_dir, "nuMinAll")[-1][1]
    numax = read_scalar_series(level_dir, "nuMaxAll")[-1][1]
    if numax >= 0.999 * NUMAX:
        raise SystemExit2("%s: nuMax clip BINDS at endTime (max nu = %.6g >= %.6g)"
                          % (level_dir, numax, 0.999 * NUMAX))
    if numin <= 1.001 * NUMIN:
        raise SystemExit2("%s: nuMin clip BINDS at endTime (min nu = %.6g <= %.6g)"
                          % (level_dir, numin, 1.001 * NUMIN))
    return {"nu_min_endtime": numin, "nu_max_endtime": numax,
            "nuMax_headroom_x": NUMAX / numax}


# ------------------------------------------------------ strict completion ------
def completion(run_root, level):
    """CLAUDE.md rule 4, FIXED-endTime variant (declared in PREREGISTRATION.md
    sec.6): this run does NOT stop on residualControl, it runs the whole budget, so
    'last time == endTime' -- NOT '< endTime'. A capped run (rc 124) has
    last_time < endTime and is refused. L-342 field classes: an ABSENT
    infrastructure field -> NOT MEASURED and the grade PROCEEDS; a recorded rc != 0
    or an absent PHYSICS field REFUSES."""
    level_dir = os.path.join(run_root, level)
    out = {"level": level, "level_dir": level_dir}

    # ---- infrastructure (never voids the run by its absence) ----
    rcf = os.path.join(run_root, "RUN_RC.%s" % level)
    out["rc_source"] = rcf
    if not os.path.exists(rcf):
        out["rc"], out["rc_status"] = None, "NOT MEASURED"
        out["rc_note"] = ("RUN_RC.%s absent -- INFRASTRUCTURE (L-342); grade proceeds on the "
                          "physics-critical clauses." % level)
    else:
        rct = open(rcf).read()
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)", rct, re.M)
        if not m:
            out["rc"], out["rc_status"] = None, "NOT MEASURED"
            out["rc_note"] = "RUN_RC.%s present but no rc= line -- INFRASTRUCTURE, grade proceeds." % level
        else:
            out["rc"], out["rc_status"] = int(m.group(1)), "MEASURED"
            if out["rc"] != 0:
                raise SystemExit2("rc=%d recorded for %s (124 == the per-level cap fired). A "
                                  "recorded non-zero rc is evidence about the SOLVER (L-342)."
                                  % (out["rc"], level))
        for key in ("wall_s", "core_min", "timeout_s"):
            mm = re.search(r"^\s*%s\s*=\s*([0-9.eE+-]+)" % key, rct, re.M)
            out[key] = float(mm.group(1)) if mm else None

    # ---- physics-critical (these gate) ----
    log = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.exists(log):
        raise SystemExit2("PHYSICS-CRITICAL field missing: no log.simpleFoam in %s" % level_dir)
    lt = open(log, errors="replace").read()
    out["end_lines"] = lt.count("\nEnd")
    if out["end_lines"] < 1:
        raise SystemExit2("no End line in %s/log.simpleFoam" % level_dir)
    if "Courant Number" in lt:
        raise SystemExit2("%s: 'Courant Number' present -- this is a STEADY solve and must carry "
                          "none (MONITOR_STANDARD S8 exemption is read off the artifact)" % level_dir)
    times = [int(t) for t in re.findall(r"^Time = (\d+)", lt, re.M)]
    if not times:
        raise SystemExit2("no Time lines in %s/log.simpleFoam" % level_dir)
    out["last_time"] = times[-1]
    out["n_exec"] = lt.count("ExecutionTime")
    if out["n_exec"] != out["last_time"]:
        raise SystemExit2("%s ExecutionTime count %d != last time %d"
                          % (level_dir, out["n_exec"], out["last_time"]))
    cdp = os.path.join(level_dir, "system", "controlDict")
    if not os.path.exists(cdp):
        raise SystemExit2("PHYSICS-CRITICAL field missing: no system/controlDict in %s" % level_dir)
    ctl = open(cdp).read()
    m = re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    if not m:
        raise SystemExit2("%s: no endTime in controlDict" % level_dir)
    out["endTime"] = int(float(m.group(1)))
    if out["last_time"] != out["endTime"]:
        raise SystemExit2("%s: last time %d != endTime %d -- did NOT run the budget (rc 124 == "
                          "the cap stopped it; endTime is never shrunk to fit, rule 12)"
                          % (level_dir, out["last_time"], out["endTime"]))
    t = str(out["last_time"])
    out["time_dir"] = t
    for f in ("U", "p"):
        if not os.path.exists(os.path.join(level_dir, t, f)):
            raise SystemExit2("PHYSICS-CRITICAL field %s missing at %s/%s" % (f, level_dir, t))
    z = os.path.getmtime(os.path.join(level_dir, "0", "U"))
    for f in ("U", "p"):
        if not os.path.getmtime(os.path.join(level_dir, t, f)) > z:
            raise SystemExit2("AGE GUARD: %s/%s/%s is not newer than 0/U" % (level_dir, t, f))
    out["age_guard"] = "fields at endTime newer than 0/U"
    return out


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine."""
    d32 = f3 - f2
    d21 = f2 - f1
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "ratio": r, "fs": fs,
           "d21": d21, "d32": d32}
    if d21 == 0.0 and d32 == 0.0:
        out["state"] = "EXACT"; out["p"] = None; out["gci_fine"] = None; return out
    if d21 == 0.0 or d32 == 0.0:
        out["state"] = "STAGNANT"; out["p"] = None; out["gci_fine"] = None; return out
    R = d32 / d21
    out["R"] = R
    if R < 0.0:
        out["state"] = "OSCILLATORY"; out["p"] = None; out["gci_fine"] = None; return out
    if R >= 1.0:
        out["state"] = "DIVERGENT"; out["p"] = None; out["gci_fine"] = None; return out
    p = math.log(abs(d21 / d32)) / math.log(r)
    out["p"] = p
    if p < P_MIN:
        out["state"] = "STAGNANT"; out["p_floor"] = P_MIN; out["p_below_floor"] = True
        out["gci_fine"] = None; out["f_extrapolated"] = None; return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


# ------------------------------------------ THE ONE VERDICT PATH (shared) ------
def verdict_for(level_conv, tri, inside):
    """The ONLY place a verdict string is produced. It can never turn NOT A RESULT
    into PASS. Order: rule 5 limb 1 (any level not plateaued / residuals still
    falling) -> NOT A RESULT; limb 2 (triple not CONVERGING) -> NOT A RESULT; limb 3
    -> PASS inside the band (ceiling PASS, sec.12.2 SAME ruled) else GATE FAIL."""
    bad = [lv for lv, c in level_conv.items()
           if not (c["plateaued"] and c["residuals_settled"])]
    if bad:
        why = "; ".join(
            "%s: plateaued=%s (ptp %.4g Pa vs %.3g), residuals_settled=%s (fall Ux %s / p %s vs %.3g)"
            % (lv, level_conv[lv]["plateaued"], level_conv[lv]["plateau_ptp_pa"], PLATEAU_THRESH_PA,
               level_conv[lv]["residuals_settled"], level_conv[lv]["resid_fall_Ux"],
               level_conv[lv]["resid_fall_p"], RESID_FALL_FACTOR)
            for lv in bad)
        return ("NOT A RESULT",
                "convergence clause (rule 5 limb 1) failed at %s -- NOT A RESULT whatever the "
                "value: %s" % (", ".join(bad), why))
    if tri["state"] != "CONVERGING":
        if tri.get("p_below_floor"):
            return ("NOT A RESULT",
                    "observed order p = %.6g below the frozen floor P_MIN = %.3g; triple %s, "
                    "NO GCI quoted" % (tri["p"], P_MIN, tri["state"]))
        return ("NOT A RESULT",
                "grid triple is %s, not CONVERGING (rule 5 limb 2) -- NOT A RESULT whatever the "
                "value" % tri["state"])
    if inside:
        return ("PASS",
                "finest-level dp inside the frozen band [%.2f, %.2f] Pa, triple CONVERGING; "
                "ceiling PASS -- sec.12.2 ruled SAME/PASS-capable (VERIFICATION_CHARTER "
                "sec.2h.8.1)" % (BAND_LO, BAND_HI))
    return ("GATE FAIL",
            "finest-level dp OUTSIDE the frozen band [%.2f, %.2f] Pa (triple CONVERGING) -- no "
            "gate-fitting" % (BAND_LO, BAND_HI))


# ------------------------------------------------------- planted-zero control --
def planted_zero(level_dir):
    """Plant a known perturbation into a COPY of the pInlet monitor, overwriting the
    MAX-iteration value the gate reads, read it back FROM DISK, and prove dp moves by
    exactly RHO*PLANT (CLAUDE.md rule 3). SINGLE scalar into SINGLE scalar -- no
    averaging dilution (L-340), and it lands on the exact value the gate consumes."""
    src = _monitor_path(level_dir, "pInlet")
    base_end = dp_at_endtime(dp_series(level_dir))[0]
    tmp = tempfile.mkdtemp(prefix="vmfl007r3_plant_")
    try:
        # Build a scratch level tree that reuses the real pOutlet and a PLANTED pInlet.
        pin_dir = os.path.join(tmp, "postProcessing", "pInlet", "0")
        pout_dir = os.path.join(tmp, "postProcessing", "pOutlet", "0")
        os.makedirs(pin_dir); os.makedirs(pout_dir)
        shutil.copy(_monitor_path(level_dir, "pOutlet"), os.path.join(pout_dir, "surfaceFieldValue.dat"))
        lines = open(src).read().splitlines()
        # overwrite the LAST data line's value (the max-iteration scalar the gate reads)
        last_i = max(i for i, ln in enumerate(lines) if ln and not ln.startswith("#"))
        q = lines[last_i].split()
        it = q[0]
        planted_val = float(q[-1]) + PLANT
        lines[last_i] = "%s\t%.12e" % (it, planted_val)
        open(os.path.join(pin_dir, "surfaceFieldValue.dat"), "w").write("\n".join(lines) + "\n")
        seen_end = dp_at_endtime(dp_series(tmp))[0]
        delta = seen_end - base_end
        ok = abs(delta - RHO * PLANT) < 1e-6
        if not ok:
            raise SystemExit2("planted-zero control FAILED: planted %g kinematic into the pInlet "
                              "max-iteration value; dp moved by %g Pa, expected %g -- a reader not "
                              "shown able to see a non-zero cannot certify a zero (rule 3)"
                              % (PLANT, delta, RHO * PLANT))
        return {"passed": True, "planted_kinematic": PLANT, "expected_dp_shift_pa": RHO * PLANT,
                "reader_dp_shift_pa": delta, "file": "pInlet/surfaceFieldValue.dat"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------- observed-order floor control ------
def p_floor_control():
    """A floor nobody tests is a floor nobody has. Plants three triples into the
    comparator's OWN roache()+verdict_for() and REFUSES if any grades wrong."""
    def refuse(tag, detail):
        raise SystemExit2("P-FLOOR PLANTED CONTROL FAILED [%s]: %s (P_MIN = %.3g)"
                          % (tag, detail, P_MIN))
    conv_ok = {lv: {"plateaued": True, "residuals_settled": True, "plateau_ptp_pa": 0.0,
                    "resid_fall_Ux": 1.0, "resid_fall_p": 1.0} for lv in LEVELS}
    out = {"P_MIN": P_MIN, "probes": {}}

    tri_a = roache(1.0, 1.1, 1.2)                 # R = 1, equally spaced -> not converging
    v_a, _ = verdict_for(conv_ok, tri_a, True)
    out["probes"]["equally_spaced"] = {"state": tri_a["state"], "verdict": v_a,
                                       "gci_fine": tri_a.get("gci_fine")}
    if v_a != "NOT A RESULT" or tri_a.get("gci_fine") is not None:
        refuse("equally-spaced", "graded %r / gci %r, expected NOT A RESULT and no GCI"
               % (v_a, tri_a.get("gci_fine")))

    p_lo = 0.01
    tri_b = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_lo)))
    v_b, _ = verdict_for(conv_ok, tri_b, True)
    out["probes"]["below_floor"] = {"p": tri_b.get("p"), "verdict": v_b,
                                    "gci_fine": tri_b.get("gci_fine")}
    if tri_b.get("p") is None or abs(tri_b["p"] - p_lo) > 1e-9:
        refuse("below-floor", "constructed p = %.4g not recovered (got %r)" % (p_lo, tri_b.get("p")))
    if not tri_b.get("p_below_floor") or v_b != "NOT A RESULT" or tri_b.get("gci_fine") is not None:
        refuse("below-floor", "p below floor but verdict %r / gci %r" % (v_b, tri_b.get("gci_fine")))

    p_hi = 0.5
    tri_c = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_hi)))
    v_c, _ = verdict_for(conv_ok, tri_c, True)
    out["probes"]["above_floor"] = {"p": tri_c.get("p"), "verdict": v_c,
                                    "gci_fine": tri_c.get("gci_fine")}
    if tri_c["state"] != "CONVERGING" or tri_c.get("gci_fine") is None or v_c != "PASS":
        refuse("above-floor", "p above floor but state %s / gci %r / verdict %r"
               % (tri_c["state"], tri_c.get("gci_fine"), v_c))
    out["passed"] = True
    return out


# ------------------------------------------------------------------- selftest --
def _write_monitor(d, name, rows, vector=False):
    md = os.path.join(d, "postProcessing", name, "0")
    os.makedirs(md, exist_ok=True)
    body = ["# Region type :     patch inlet", "# Faces             : 25",
            "# Area              : 1.363469252911e-08", "# Scale factor      : 1.0",
            "# Time              \tvalue"]
    for it, v in rows:
        if vector:
            body.append("%d\t(%.12e 0 0)" % (it, v))
        else:
            body.append("%d\t%.12e" % (it, v))
    open(os.path.join(md, "surfaceFieldValue.dat"), "w").write("\n".join(body) + "\n")


def _write_level(root, lvl, dp_end_pa, ptp_pa, resid_fall, endtime=60000, rc=0,
                 write_rc=True, umax=UMAX_DEV_PROFILE, qmean=2.0, numax=0.4, numin=4.3e-5,
                 last_time=None, drop_field=None, courant=False):
    """Construct a level tree the REAL readers/completion parse. dp is built so its
    last-W ptp equals ptp_pa and its endTime value equals dp_end_pa; residuals are
    built so the median fall over the window equals resid_fall."""
    ld = os.path.join(root, lvl)
    os.makedirs(os.path.join(ld, "system"), exist_ok=True)
    os.makedirs(os.path.join(ld, "0"), exist_ok=True)
    lastt = last_time if last_time is not None else endtime
    os.makedirs(os.path.join(ld, str(lastt)), exist_ok=True)
    # monitors: pInlet carries dp/RHO, pOutlet is 0. Build W_PLATEAU+... rows.
    npts = W_PLATEAU + 10
    pin_rows, pout_rows, ux_rows, p_rows, nmin_rows, nmax_rows, q_rows, umax_rows = ([] for _ in range(8))
    area = 1.363469252911e-08
    for j in range(npts):
        it = lastt - npts + 1 + j
        # dp flat at dp_end_pa except the FIRST window point sits ptp_pa below,
        # so max-min over the last W is exactly ptp_pa and the endTime value is dp_end_pa.
        val = dp_end_pa
        if j == npts - W_PLATEAU:
            val = dp_end_pa - ptp_pa
        pin_rows.append((it, val / RHO))
        pout_rows.append((it, 0.0))
        q_rows.append((it, -qmean * area))
        umax_rows.append((it, umax))
        nmin_rows.append((it, numin)); nmax_rows.append((it, numax))
    _write_monitor(ld, "pInlet", pin_rows)
    _write_monitor(ld, "pOutlet", pout_rows)
    _write_monitor(ld, "QInlet", q_rows)
    _write_monitor(ld, "UmaxInlet", umax_rows, vector=True)
    _write_monitor(ld, "nuMinAll", nmin_rows)
    _write_monitor(ld, "nuMaxAll", nmax_rows)
    # log: Time/ExecutionTime per iteration + residual lines whose window fall == resid_fall
    lines = []
    for i in range(1, lastt + 1):
        lines.append("Time = %d" % i)
        # residual: within the last window, first half high, last half = high/resid_fall
        pos = i - (lastt - W_PLATEAU)
        if pos <= 0:
            ux = pr = 1e-3
        elif pos <= W_PLATEAU // 2:
            ux = pr = 1e-6 * resid_fall
        else:
            ux = pr = 1e-6
        lines.append("smoothSolver:  Solving for Ux, Initial residual = %.6e, Final residual = 1e-12, No Iterations 2" % ux)
        lines.append("PBiCGStab:  Solving for p, Initial residual = %.6e, Final residual = 1e-12, No Iterations 5" % pr)
        lines.append("ExecutionTime = %d s  ClockTime = %d s" % (i, i))
    if courant:
        lines.append("Courant Number mean: 0.1 max: 0.5")
    lines.append("")
    lines.append("End")
    open(os.path.join(ld, "log.simpleFoam"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(ld, "system", "controlDict"), "w").write("endTime %d;\n" % endtime)
    for f in ("U", "p"):
        if drop_field == f:
            continue
        open(os.path.join(ld, str(lastt), f), "w").write("%s field\n" % f)
    zt = os.path.getmtime(os.path.join(ld, str(lastt), "p" if drop_field != "p" else "U")) - 10
    open(os.path.join(ld, "0", "U"), "w").write("U0\n")
    os.utime(os.path.join(ld, "0", "U"), (zt, zt))
    if write_rc:
        open(os.path.join(root, "RUN_RC.%s" % lvl), "w").write(
            "rc = %d\nlevel = %s\nwall_s = 100\nranks = 1\ncore_min = 1.7\ntimeout_s = 2400\n" % (rc, lvl))


def selftest():
    ok = True
    def chk(c, name, got=""):
        nonlocal ok
        print("  [%s] %s  %s" % ("PASS" if c else "FAIL", name, got))
        ok = ok and c

    print("=== VMFL007-R3 comparator selftest ===")
    print("--- selftest: frozen gate is byte-identical arithmetic ---")
    chk(_rho_ok(), "RHO = k_manual / k_kinematic = 1000")
    chk(abs(BAND_LO - REF_PA * (1 - TOL)) < 1e-6 and abs(BAND_HI - REF_PA * (1 + TOL)) < 1e-6,
        "band [%.2f, %.2f] == 60520 +/- 0.5%%" % (BAND_LO, BAND_HI))
    chk(BAND_LO < CLOSED_FORM_PA < BAND_HI, "closed form 60521.969 is inside the band (context)")

    print("--- selftest: Roache classifier ---")
    chk(roache(1.0, 1.5, 1.75)["state"] == "CONVERGING" and abs(roache(1.0, 1.5, 1.75)["p"] - 1.0) < 1e-9,
        "first-order family -> CONVERGING, p == 1")
    chk(roache(1.0, 1.25, 1.3125)["state"] == "CONVERGING" and abs(roache(1.0, 1.25, 1.3125)["p"] - 2.0) < 1e-9,
        "second-order family -> p == 2")
    chk(roache(1.0, 2.0, 4.0)["state"] == "DIVERGENT", "divergent -> DIVERGENT")
    chk(roache(1.0, 2.0, 1.5)["state"] == "OSCILLATORY", "oscillatory -> OSCILLATORY")
    chk(roache(2.0, 2.0, 2.0)["state"] == "EXACT", "identical -> EXACT")

    print("--- selftest: the DIAG-measured triple is a CONVERGING family (values are the ---")
    print("    prior lane's diagnostic B2 monitors; the GRADED run reproduces them, not these) ---")
    tri_diag = roache(60432.628, 60498.982, 60517.072)
    chk(tri_diag["state"] == "CONVERGING", "60432.6/60499.0/60517.1 -> CONVERGING", tri_diag["state"])
    chk(1.7 < tri_diag["p"] < 2.0, "observed order p ~ 1.875", "%.4f" % tri_diag["p"])

    print("--- selftest: THE ONE VERDICT PATH (ceiling PASS; NOT A RESULT cannot become PASS) ---")
    conv_ok = {lv: {"plateaued": True, "residuals_settled": True, "plateau_ptp_pa": 1e-3,
                    "resid_fall_Ux": 1.1, "resid_fall_p": 1.1} for lv in LEVELS}
    conv_bad = dict(conv_ok); conv_bad["L3"] = {"plateaued": False, "residuals_settled": True,
        "plateau_ptp_pa": 5.0, "resid_fall_Ux": 1.1, "resid_fall_p": 1.1}
    tri_conv = roache(60432.628, 60498.982, 60517.072)
    chk(verdict_for(conv_ok, tri_conv, True)[0] == "PASS", "converging + inside band -> PASS")
    chk(verdict_for(conv_ok, tri_conv, False)[0] == "GATE FAIL", "converging + outside band -> GATE FAIL")
    chk(verdict_for(conv_ok, roache(1.0, 2.0, 4.0), True)[0] == "NOT A RESULT",
        "DIVERGENT triple inside band -> NOT A RESULT (gate cannot rescue it)")
    chk(verdict_for(conv_bad, tri_conv, True)[0] == "NOT A RESULT",
        "a level not plateaued -> NOT A RESULT even inside band (rule 5 limb 1)")

    print("--- selftest: observed-order floor P_MIN planted control ---")
    pf = p_floor_control()
    chk(pf["passed"] and pf["probes"]["equally_spaced"]["verdict"] == "NOT A RESULT",
        "(1.0,1.1,1.2) -> NOT A RESULT, no GCI")
    chk(pf["probes"]["below_floor"]["verdict"] == "NOT A RESULT"
        and pf["probes"]["below_floor"]["gci_fine"] is None, "p=0.01 below floor -> NOT A RESULT")
    chk(pf["probes"]["above_floor"]["verdict"] == "PASS", "p=0.5 above floor -> graded (PASS here)")

    print("--- selftest: convergence clause on CONSTRUCTED monitors (plateau + residual) ---")
    d = tempfile.mkdtemp(prefix="st007r3_conv_")
    _cwd = os.getcwd()
    try:
        os.chdir(d)
        _write_level(".", "P", dp_end_pa=60517.0, ptp_pa=1.45e-3, resid_fall=1.0)
        cP = convergence(os.path.join(".", "P"))
        chk(cP["plateaued"] and cP["residuals_settled"],
            "flat dp (ptp 1.45e-3 < 1e-2) + flat residual -> plateaued & settled",
            "ptp=%.3g fallUx=%.3g" % (cP["plateau_ptp_pa"], cP["resid_fall_Ux"]))
        chk(abs(cP["dp_endtime_pa"] - 60517.0) < 1e-6, "endTime dp read as the single scalar",
            cP["dp_endtime_pa"])
        _write_level(".", "Q", dp_end_pa=60517.0, ptp_pa=5.0, resid_fall=1.0)
        cQ = convergence(os.path.join(".", "Q"))
        chk(not cQ["plateaued"], "dp ptp 5 Pa > 1e-2 -> NOT plateaued", cQ["plateau_ptp_pa"])
        _write_level(".", "S", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=100.0)
        cS = convergence(os.path.join(".", "S"))
        chk(not cS["residuals_settled"], "residual falling 100x over window -> NOT settled",
            "fallUx=%.3g" % cS["resid_fall_Ux"])
    finally:
        os.chdir(_cwd); shutil.rmtree(d, ignore_errors=True)

    print("--- selftest: planted-zero on the pInlet max-iteration value (no dilution, L-340) ---")
    d = tempfile.mkdtemp(prefix="st007r3_plant_")
    _cwd = os.getcwd()
    try:
        os.chdir(d)
        _write_level(".", "L1", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0)
        pz = planted_zero(os.path.join(".", "L1"))
        chk(pz["passed"] and abs(pz["reader_dp_shift_pa"] - RHO * PLANT) < 1e-6,
            "planted %g kinematic -> dp moved %g Pa == RHO*PLANT" % (PLANT, RHO * PLANT),
            pz["reader_dp_shift_pa"])
        # blind reader: monkeypatch the scalar reader to ignore the plant -> REFUSE
        global read_scalar_series
        _orig = read_scalar_series
        try:
            read_scalar_series = lambda ld, nm: [(i, 60.517 if nm == "pInlet" else 0.0)
                                                 for i in range(1, 6)]
            blind = False
            try:
                planted_zero(os.path.join(".", "L1"))
            except SystemExit as ex:
                blind = (ex.code == 2)
            chk(blind, "planted-zero REFUSES (exit 2) a reader that cannot see the plant")
        finally:
            read_scalar_series = _orig
    finally:
        os.chdir(_cwd); shutil.rmtree(d, ignore_errors=True)

    print("--- selftest: SAME precondition + viscosity class on constructed monitors ---")
    d = tempfile.mkdtemp(prefix="st007r3_same_")
    _cwd = os.getcwd()
    try:
        os.chdir(d)
        _write_level(".", "L1", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0)
        sp = same_precondition(os.path.join(".", "L1"))
        chk(abs(sp["inlet_peak_U"] - UMAX_DEV_PROFILE) < UMAX_TOL and abs(sp["inlet_mean_U"] - 2.0) < QMEAN_TOL,
            "developed inlet: peak %.4f, mean %.4f" % (sp["inlet_peak_U"], sp["inlet_mean_U"]))
        vc = viscosity_class(os.path.join(".", "L1"))
        chk(vc["nu_max_endtime"] < NUMAX and vc["nu_min_endtime"] > NUMIN, "nuMin/nuMax do not bind")
        # a FLAT slug (peak 2.0) must REFUSE the SAME precondition
        _write_level(".", "FLAT", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, umax=2.0)
        flat_ref = False
        try:
            same_precondition(os.path.join(".", "FLAT"))
        except SystemExit as ex:
            flat_ref = (ex.code == 2)
        chk(flat_ref, "a flat 2.0 slug REFUSES (exit 2) the SAME precondition -> would be DIFFERENT")
    finally:
        os.chdir(_cwd); shutil.rmtree(d, ignore_errors=True)

    print("--- selftest: strict completion (FIXED-endTime; L-342 field classes; age guard) ---")
    d = tempfile.mkdtemp(prefix="st007r3_comp_")
    _cwd = os.getcwd()
    try:
        os.chdir(d)
        _write_level(".", "L1", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, rc=0)
        c = completion(".", "L1")
        chk(c["rc"] == 0 and c["rc_status"] == "MEASURED" and c["last_time"] == c["endTime"],
            "parses `rc = 0`; last time == endTime (ran the budget)")
        _write_level(".", "L2", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, rc=124)
        r124 = False
        try:
            completion(".", "L2")
        except SystemExit as ex:
            r124 = (ex.code == 2)
        chk(r124, "a recorded rc = 124 (cap fired) REFUSES (exit 2)")
        _write_level(".", "L3", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, rc=0,
                     last_time=30000, endtime=60000)
        short = False
        try:
            completion(".", "L3")
        except SystemExit as ex:
            short = (ex.code == 2)
        chk(short, "last time 30000 != endTime 60000 REFUSES (did not run the budget)")
        _write_level(".", "L4", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, write_rc=False)
        c4 = completion(".", "L4")
        chk(c4["rc"] is None and c4["rc_status"] == "NOT MEASURED",
            "L-342: absent RUN_RC -> NOT MEASURED, grade proceeds")
        _write_level(".", "L5", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, courant=True)
        cour = False
        try:
            completion(".", "L5")
        except SystemExit as ex:
            cour = (ex.code == 2)
        chk(cour, "a 'Courant Number' line in a STEADY solve REFUSES")
        _write_level(".", "L6", dp_end_pa=60517.0, ptp_pa=1e-3, resid_fall=1.0, drop_field="p")
        misf = False
        try:
            completion(".", "L6")
        except SystemExit as ex:
            misf = (ex.code == 2)
        chk(misf, "an absent PHYSICS-CRITICAL field (p) REFUSES")
    finally:
        os.chdir(_cwd); shutil.rmtree(d, ignore_errors=True)

    print("\nchecks run: see the PASS/FAIL lines above")
    print("SELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


# --------------------------------------------------------------- verify-frozen --
def verify_frozen(commit):
    try:
        repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception as e:
        raise SystemExit2("--verify-frozen: not inside a git repo (%s)" % e)
    for rel in (GRADER_REL, PREREG_REL):
        try:
            head = subprocess.run(["git", "-C", repo, "rev-parse", "%s:%s" % (commit, rel)],
                                  capture_output=True, text=True, check=True).stdout.strip()
            disk = subprocess.run(["git", "-C", repo, "hash-object", os.path.join(repo, rel)],
                                  capture_output=True, text=True, check=True).stdout.strip()
        except Exception as e:
            raise SystemExit2("--verify-frozen: cannot hash %s at %s (%s)" % (rel, commit, e))
        if head != disk:
            raise SystemExit2("--verify-frozen: %s on disk (%s) != blob at %s (%s) -- the file "
                              "that would run is NOT the frozen file (rule 2)" % (rel, disk, commit, head))
        print("  frozen OK  %s  %s" % (rel, disk))
    print("VERIFY-FROZEN: comparator and prereg match their blobs at %s" % commit)
    return 0


# ----------------------------------------------------------------------- main --
def main(argv):
    if not _rho_ok():
        raise SystemExit2("RHO is inconsistent with its own derivation")
    root = os.path.normpath(RUN_ROOT)
    if "--run-root" in argv:
        root = os.path.normpath(argv[argv.index("--run-root") + 1])

    res = {"case": "VMFL007-R3", "manual_page": "29",
           "cites": "register rows #8 (VMFL007 run 1, DIVERGED) and #37 (VMFL007-R2, NOT A RESULT) "
                    "-- neither re-graded or overwritten",
           "reference_pa": REF_PA, "reference_kind": "closed-form (Hughes-Brighton / Rabinowitsch-Mooney)",
           "closed_form_pa": CLOSED_FORM_PA, "band_pa": [BAND_LO, BAND_HI], "tol": TOL,
           "ansys_context_only_pa": {"fluent": ANSYS_FLUENT_PA, "cfx": ANSYS_CFX_PA},
           "ceiling": "PASS (sec.12.2 ruled SAME; VERIFICATION_CHARTER sec.2h.8.1)",
           "field_classes": FIELD_CLASSES, "comparator": os.path.abspath(__file__),
           "run_root": root, "completion": {}, "convergence": {}, "levels": {}}

    print("=" * 78)
    print("VMFL007-R3 -- Non-Newtonian (power-law) Flow in a Pipe")
    print("Ansys FD Verification Manual 2026 R1, p. 29.  reference dp = %.3f Pa" % REF_PA)
    print("gate |dp - %.0f|/%.0f <= %.3g  band [%.2f, %.2f] Pa  AND a CONVERGING triple"
          % (REF_PA, REF_PA, TOL, BAND_LO, BAND_HI))
    print("ceiling PASS (sec.12.2 SAME).  Fluent %.0f / CFX %.0f Pa = CONTEXT ONLY"
          % (ANSYS_FLUENT_PA, ANSYS_CFX_PA))
    print("=" * 78)

    # planted controls driven BEFORE any level is read
    res["p_floor_control"] = p_floor_control()
    print("p-floor planted control OK (P_MIN = %.3g): equally-spaced -> NOT A RESULT, no GCI" % P_MIN)

    dps = []
    level_conv = {}
    not_measured = []
    for lv in LEVELS:
        d = os.path.join(root, lv)
        c = completion(root, lv)
        res["completion"][lv] = c
        if c["rc_status"] != "MEASURED":
            not_measured.append("%s rc (%s)" % (lv, c["rc_source"]))
        sp = same_precondition(d)
        vc = viscosity_class(d)
        conv = convergence(d)
        conv.update(sp); conv.update(vc)
        res["convergence"][lv] = conv
        level_conv[lv] = conv
        dp_end = conv["dp_endtime_pa"]
        dps.append(dp_end)
        res["levels"][lv] = {"dp_endtime_pa": dp_end, "plateau_ptp_pa": conv["plateau_ptp_pa"],
                             "plateaued": conv["plateaued"], "residuals_settled": conv["residuals_settled"],
                             "inlet_peak_U": sp["inlet_peak_U"], "inlet_mean_U": sp["inlet_mean_U"],
                             "nuMax_headroom_x": vc["nuMax_headroom_x"], "time_dir": c["time_dir"]}
        print("  %-3s  dp = %.4f Pa   plateau ptp %.4g Pa (%s)   residuals %s "
              "(fall Ux %s / p %s)   inlet peak %.4f mean %.4f"
              % (lv, dp_end, conv["plateau_ptp_pa"], "PLATEAUED" if conv["plateaued"] else "NOT PLATEAUED",
                 "SETTLED" if conv["residuals_settled"] else "STILL FALLING",
                 conv["resid_fall_Ux"], conv["resid_fall_p"], sp["inlet_peak_U"], sp["inlet_mean_U"]))

    if not_measured:
        print("\nNOT MEASURED (L-342 infrastructure, disclosed, grade proceeds): %s"
              % "; ".join(not_measured))
        res["not_measured"] = not_measured

    # planted-zero on the finest level's monitor, on the exact value the gate reads
    res["planted_zero"] = planted_zero(os.path.join(root, LEVELS[-1]))
    print("\nplanted-zero control on %s: %s" % (LEVELS[-1], json.dumps(res["planted_zero"])))

    tri = roache(dps[0], dps[1], dps[2])
    res["triple"] = tri
    fine = dps[-1]
    res["lab_value_pa"] = fine
    rel = abs(fine - REF_PA) / abs(REF_PA)
    res["rel_dev"] = rel
    inside = BAND_LO <= fine <= BAND_HI

    print("\n--- Roache triple on dp (r = %.1f) ---" % RATIO)
    print("  %.4f / %.4f / %.4f Pa  -> %s" % (dps[0], dps[1], dps[2], tri["state"]))
    if tri["state"] == "CONVERGING":
        print("  observed order p = %.4f   GCI_fine (Fs = %.2f) = %.4f %%"
              % (tri["p"], FS, 100.0 * tri["gci_fine"]))
    elif tri.get("p_below_floor"):
        print("  observed order p = %.6g below the floor P_MIN = %.3g -- %s, NO GCI"
              % (tri["p"], P_MIN, tri["state"]))
    else:
        print("  observed order undefined for a %s triple; NO GCI" % tri["state"])

    print("\n--- gate: |dp - %.0f| / %.0f <= %.3g ---" % (REF_PA, REF_PA, TOL))
    print("  lab dp = %.4f Pa   reference %.3f   rel dev %.4f %%   %s"
          % (fine, REF_PA, 100.0 * rel, "inside band" if inside else "OUTSIDE band"))

    verdict, why = verdict_for(level_conv, tri, inside)
    res["verdict"] = verdict
    res["why"] = why
    print("\nVERDICT: %s -- %s" % (verdict, why))

    out = os.path.join(root, "GRADING_VMFL007_R3.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
    print("grading written to %s" % out)
    return 0


# =============================================================================
# DATED AMENDMENT -- 2026-09-08 -- grade_vmfl007_r3.py  v1.0 -> v1.1
# VERIFICATION_CHARTER SS2d.1 VALUE-INVARIANT REPAIR of an OFF-GATE reader bug
# (nuMinAll / nuMaxAll).  Audited and signed off by the verification team as
# V-129 (byte-for-byte value-invariance confirmed).  Chief's two landing
# conditions satisfied: in-place SS2d.1 addendum + a volFieldValue selftest arm.
# lines whose number changed above this section: 0
#
# DEMONSTRABLE ERROR (SS2d.1 cond 1):
#   The frozen _monitor_path (lines 152-155) globs
#       postProcessing/<name>/*/surfaceFieldValue.dat
#   for EVERY monitor.  But the driver's controlDict declares nuMinAll/nuMaxAll
#   as `type volFieldValue`, so OpenFOAM wrote
#       postProcessing/<name>/0/volFieldValue.dat
#   (a whole-domain min/max of nu, NOT a surface integral).  The
#   surfaceFieldValue glob matches ZERO paths, so one_or_refuse (line 147)
#   raises SystemExit2 "matched 0 paths [] -- ambiguous" from viscosity_class
#   (line 290), aborting the OFF-GATE viscosity-clip precondition BEFORE the
#   gate (line 883) and before the pInlet planted-zero (line 861).  Proven by
#   file existence: the surfaceFieldValue path does NOT exist; volFieldValue.dat
#   DOES (all six nu monitors across L1/L2/L3).
#
# THE ONLY CHANGE (SS2d.1 cond 3, value-invariance -- gate byte-identical):
#   This block is a PURE INSERTION.  Frozen lines 1-898 are unchanged: REF_PA
#   60520, BAND_LO/HI [60217.40, 60822.60], TOL 0.005, verdict_for, roache,
#   dp_series, BOTH planted controls, and the gate's own _monitor_path (which
#   still globs surfaceFieldValue for the pInlet/pOutlet gate series) are all
#   byte-identical.  This block (a) re-binds viscosity_class to read the nu
#   monitors via _visc_monitor_path, which resolves whichever single file
#   OpenFOAM wrote (volFieldValue in a real run, surfaceFieldValue in the frozen
#   selftest fixtures) under the SAME one_or_refuse "exactly one, else REFUSE"
#   discipline; the parse and the clip-binding thresholds (0.999*NUMAX,
#   1.001*NUMIN) are the frozen ones, byte for byte.  And (b) wraps selftest to
#   add a regression arm that builds a volFieldValue.dat fixture (the driver's
#   real function-object filename) and proves the repaired reader resolves it
#   while the frozen surfaceFieldValue-only glob REFUSES it -- closing the
#   fixture blindness that let this class through the freeze (row #64 triage).
#   NO gate quantity, threshold, band, label or verdict-cascade node is
#   referenced or altered here; this block only lets the comparator REACH the
#   frozen gate.  Any PASS is produced by the byte-identical gate on the
#   already-computed answer-blind triple, not by this repair.
# =============================================================================

def _visc_monitor_path(level_dir, name):
    """OFF-GATE nu-clip monitors are volFieldValue (volume min/max), not
    surfaceFieldValue.  Resolve whichever single file OpenFOAM wrote, keeping
    the frozen one_or_refuse ambiguity discipline (exactly one, else REFUSE)."""
    hits = (glob.glob(os.path.join(level_dir, "postProcessing", name, "*", "volFieldValue.dat"))
            + glob.glob(os.path.join(level_dir, "postProcessing", name, "*", "surfaceFieldValue.dat")))
    return one_or_refuse(hits, "%s/postProcessing/%s (vol/surfaceFieldValue)" % (level_dir, name))


def _visc_read_scalar_series(level_dir, name):
    """Identical parse to the frozen read_scalar_series (last column), on the
    file _visc_monitor_path resolves."""
    out = []
    for ln in open(_visc_monitor_path(level_dir, name)):
        if ln.startswith("#"):
            continue
        q = ln.split()
        if len(q) >= 2:
            out.append((int(float(q[0])), float(q[-1])))
    return out


def viscosity_class(level_dir):   # OVERRIDES the frozen def (line 286): OFF-GATE reader only
    numin = _visc_read_scalar_series(level_dir, "nuMinAll")[-1][1]
    numax = _visc_read_scalar_series(level_dir, "nuMaxAll")[-1][1]
    if numax >= 0.999 * NUMAX:
        raise SystemExit2("%s: nuMax clip BINDS at endTime (max nu = %.6g >= %.6g)"
                          % (level_dir, numax, 0.999 * NUMAX))
    if numin <= 1.001 * NUMIN:
        raise SystemExit2("%s: nuMin clip BINDS at endTime (min nu = %.6g <= %.6g)"
                          % (level_dir, numin, 1.001 * NUMIN))
    return {"nu_min_endtime": numin, "nu_max_endtime": numax,
            "nuMax_headroom_x": NUMAX / numax}


_frozen_selftest_v10 = selftest   # capture the v1.0 selftest object before rebinding


def selftest():
    """v1.1: run every frozen v1.0 arm, then a volFieldValue regression arm that
    catches the off-gate filename-path class going forward.  No bare asserts
    (survives python3 -O), matching the frozen selftest's discipline."""
    rc0 = _frozen_selftest_v10()
    ok = True
    def chk(c, name, got=""):
        nonlocal ok
        print("  [%s] %s  %s" % ("PASS" if c else "FAIL", name, got))
        ok = ok and c
    print("--- selftest (v1.1 SS2d.1 arm): OFF-GATE nu monitor written as volFieldValue.dat ---")
    d = tempfile.mkdtemp(prefix="st007r3_volfield_")
    try:
        for nm, val in (("nuMinAll", 4.3e-05), ("nuMaxAll", 0.4)):
            md = os.path.join(d, "postProcessing", nm, "0")
            os.makedirs(md, exist_ok=True)
            open(os.path.join(md, "volFieldValue.dat"), "w").write(
                "# Cells             : 100\n# Volume            : 1e-09\n"
                "# Time              \tmin(nu)\n60000              \t%.12e\n" % val)
        gmin = _visc_read_scalar_series(d, "nuMinAll")[-1][1]
        gmax = _visc_read_scalar_series(d, "nuMaxAll")[-1][1]
        chk(abs(gmin - 4.3e-05) < 1e-12 and abs(gmax - 0.4) < 1e-12,
            "repaired reader resolves volFieldValue.dat", "min=%.4g max=%.4g" % (gmin, gmax))
        refused = False
        try:
            _monitor_path(d, "nuMinAll")   # frozen reader globs surfaceFieldValue.dat only
        except SystemExit as ex:
            refused = (getattr(ex, "code", None) == 2)
        chk(refused, "frozen surfaceFieldValue-only glob REFUSES the volFieldValue tree (the bug this repairs)")
        vc = viscosity_class(d)
        chk(vc["nu_min_endtime"] > NUMIN and vc["nu_max_endtime"] < NUMAX,
            "viscosity_class reads volFieldValue; clips do not bind",
            "min=%.4g max=%.4g" % (vc["nu_min_endtime"], vc["nu_max_endtime"]))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("v1.1 SS2d.1 regression arm: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    print("SELFTEST (v1.1): %s" % ("all checks passed" if (rc0 == 0 and ok) else "FAILURES PRESENT"))
    return 0 if (rc0 == 0 and ok) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--verify-frozen" in sys.argv:
        sys.exit(verify_frozen(sys.argv[sys.argv.index("--verify-frozen") + 1]))
    sys.exit(main(sys.argv))
