#!/usr/bin/env python3
# =============================================================================
# VMFL038 COMPARATOR -- Falling Film Over an Inclined Plane
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.131-132.
# Reference: R.B. Bird, W.E. Stewart, E.N. Lightfoot, Transport Phenomena, p.45.
#
# FROZEN INSTRUMENT (CLAUDE.md rule 2). Once the pre-registration commit exists,
# this file is never edited; a departure is a NEW registration and a NEW row.
#
# WHAT IT GRADES -- ONE LIMB, PASS-CAPABLE.
#   The PHYSICAL wall shear stress tau_w on the inclined plane, at the finest
#   level, against the CLOSED-FORM ANALYTICAL value 39.24 Pa (an exact solution of
#   the SAME laminar constant-property Navier-Stokes the solver discretises --
#   Bird/Stewart/Lightfoot p.45), on a three-level r = 2 Roache triple that refines
#   the FILM-NORMAL direction. Band 2 % relative; GCI ceiling 2 %.
#
# WHY WALL SHEAR AND NOT VELOCITY (RULING 1). On a uniform mesh a 2nd-order FV
# scheme reproduces the exact parabolic velocity field to round-off (the discrete
# Laplacian of a quadratic is exact), so a velocity gate gives THREE IDENTICAL
# level values, triple EXACT, and CLAUDE.md rule 5 limb (2) sends EXACT straight to
# NOT A RESULT (this retired VMFL070). The wall shear is computed from a ONE-SIDED
# near-wall gradient carrying genuine O(dy) truncation error -- non-zero, monotone,
# mesh-convergent -- so it yields a REAL triple with something to refine. The
# velocity field is reported as a DIAGNOSTIC (u_max, u_bar, full-profile RMS) and
# GATES NOTHING; whether it is in fact machine-exact is recorded as the evidence
# that RULING 1 was necessary.
#
# UNITS. simpleFoam is incompressible; its wallShearStress is KINEMATIC (m2/s2).
# The comparator multiplies by RHO = 800 kg/m3 to get PHYSICAL Pa before comparing
# to 39.24 Pa. ASSUMED (PREREGISTRATION sec.9): if the reported field carried
# physical units the gate would read 800x high and GATE FAIL -- a named outcome.
#
# NO `assert` STATEMENT APPEARS IN THIS FILE. `python3 -O` deletes every assert,
# so a control written as an assert is not a control (L-332). _ast_guard() walks
# this file's own AST and REFUSES if the ast.Assert count is not 0.
#
# EVERY file read goes through one_match(), which REFUSES unless the pattern
# matches EXACTLY ONE path. No `sorted(glob.glob(...))[-1]` appears anywhere:
# lexicographic sorting of numeric directory names puts `950` after `2000` (L-339).
# Where a numeric order is needed, numeric_latest_time_dir() sorts key=float AND is
# cross-checked against the solver log's own last Time.
# =============================================================================

import os, re, sys, json, math, glob, shutil, tempfile, ast, hashlib

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL038")

# ----------------------------------------------------------- FROZEN CONSTANTS --
# Fluid and driving head, VM2026R1 p.131, verbatim from the manual's table.
RHO       = 800.0          # density, kg/m3
MU        = 1.0            # dynamic viscosity, kg/m-s
NU        = MU / RHO       # kinematic viscosity, m2/s (= 0.00125)
G_GRAV    = 9.81           # standard gravity, m/s2 (used ONLY to derive geometry)
BETA_DEG  = 30.0           # inclination, degrees
DELTA_P   = 706.32         # |driving pressure difference|, N/m2 (outlet gauge -706.32)

# GEOMETRY DERIVED FROM THE MANUAL'S OWN PRINTED NUMBERS (RULING 2). The archive
# CSV is corroboration only and is NEVER a source of any number here.
#   L     = Delta_p / (rho*g*sin(beta))   (every input printed in the manual + g)
#   delta = L / 18                        (the manual's printed 1:18 aspect ratio)
L_LEN     = 0.18           # plane length, m  (= 706.32 / (800*9.81*0.5))
DELTA     = 0.01           # film thickness, m  (= L/18)
DPDL      = DELTA_P / L_LEN            # streamwise pressure gradient, 3924 Pa/m
U_MAX     = DPDL * DELTA**2 / (2.0*MU) # free-surface velocity, 0.1962 m/s (diagnostic)
U_BAR     = (2.0/3.0) * U_MAX          # depth-mean velocity, 0.1308 m/s (diagnostic)

# THE GATE reference. ANALYTICAL, closed form (Bird/Stewart/Lightfoot p.45).
REF_TAU_W = 39.24          # PHYSICAL wall shear stress on the inclined plane, Pa
TOL       = 0.02           # frozen band, relative, A-PRIORI (boundary-gradient
                           # truncation on a resolved film). NEVER from a run.
GCI_MAX   = 0.02           # frozen GCI ceiling: a CONVERGING triple whose fine-grid
                           # GCI exceeds this cannot certify PASS (RULING 4).

# The case terminates on residualControl { p 1e-10 } (Uy's normalised residual is a
# 0/0 artifact -- feasibility: max|Uy| = 3.4e-12 m/s). Because residualControl lists
# ONLY p, the comparator INDEPENDENTLY confirms the streamwise momentum that sets the
# wall shear is iteratively settled: the FINAL Ux initial residual in the log must be
# below this floor. Feasibility L1: 7.9e-7. The floor gives ~13x margin and keeps the
# iterative wall-shear error (~ res*tau_w ~ 4e-4 Pa) far below the ~0.15 % truncation
# signal the triple measures.
ITER_RES_FLOOR = 1.0e-5

FS        = 1.25           # Roache safety factor
RATIO     = 2.0            # film-normal grid refinement ratio (Ny doubles; Nx fixed)
P_MIN     = 0.05           # observed-order floor
EXACT_REL = 1.0e-8         # round-off floor (RULING 5): if BOTH triple differences
                           # are below EXACT_REL*|f_fine| the triple is EXACT and the
                           # row is NOT A RESULT (rule 5 limb 2). Predicted differences
                           # are ~1.6e-3 relative, ~1e5x above this floor.

# The fully-developed streamwise window on the wall, where tau_w is uniform.
X_DEV_LO  = 0.09           # downstream half; well past any entrance effect
X_DEV_HI  = L_LEN          # 0.18 m
UNIFORM_TOL = 0.05         # peak-to-peak / mean of |tau_w| in the window; beyond this
                           # the flow is not developed and the single-value gate is
                           # meaningless -> REFUSE (a quality control, not the band).

# The velocity DIAGNOSTIC cross-section (fully developed, 1 delta before outlet).
X_VEL_STATION = 0.17       # m
VEL_EXACT_REL = 1.0e-6     # RMS(u - analytic)/u_max below this = machine-exact

# PLANTED-ZERO control (CLAUDE.md rule 3), sized to the reader and applied to
# EVERY wall face; FIRED AT ALL THREE LEVELS (not L1 only).
K_PLANT       = 0.05       # plant magnitude as a fraction of mean|tau_kin| in-window
PLANT_MIN_ABS = 1.0e-14

RHO_KG        = RHO        # alias, for readability at the kinematic->physical step

LEVELS     = ["L1", "L2", "L3"]
FIELDS     = ("U", "p", "wallShearStress", "Cx", "Cy")
AGE_DATUM  = "0/U"
WALL_PATCH = "wall"

TIER_CEILING = "PASS"      # analytical reference of the SAME continuum model the
                           # solver discretises -> model-form error is zero by
                           # construction and PASS is available (ANSYS_VERIFICATION
                           # _CHARTER sec.11.1; VERIFICATION_CHARTER sec.2h.4 cond.1).
VOCAB      = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT")

FIELD_CLASSES = {
    "physics_critical": [
        "log.simpleFoam End line (EXACT name, cardinality-guarded)",
        "log.simpleFoam 'SIMPLE solution converged'",
        "log.simpleFoam Time / ExecutionTime counts",
        "system/controlDict endTime",
        "<t>/U, <t>/p, <t>/wallShearStress, <t>/Cx, <t>/Cy",
        "0/U -- the age-guard datum",
    ],
    "infrastructure": [
        "RUN_RC.<level> rc / wall_s / core_min / timeout_s",
        "COST.txt run-root roll-up",
    ],
}


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSING (exit 2): %s\n" % msg)
        SystemExit.__init__(self, 2)


# ------------------------------------------------- THE CARDINALITY GUARD -------
def one_match(pattern, what):
    """THE ONLY WAY THIS COMPARATOR OPENS A FILE. Returns the single path matching
    `pattern`, REFUSES (exit 2) on any other cardinality. `sorted(glob.glob(p))[-1]`
    is banned: it sorts numeric directory names LEXICOGRAPHICALLY (950 beats 2000,
    L-339)."""
    hits = glob.glob(pattern)
    if len(hits) != 1:
        raise SystemExit2(
            "CARDINALITY GUARD: %s -- pattern %r matched %d paths (need exactly 1)%s"
            % (what, pattern, len(hits),
               ("; matches: " + ", ".join(sorted(hits))) if hits else ""))
    return hits[0]


def read_text(pattern, what):
    p = one_match(pattern, what)
    fh = open(p, errors="replace")
    try:
        return p, fh.read()
    finally:
        fh.close()


def numeric_latest_time_dir(level_dir):
    """Latest numeric time directory, sorted key=float -- NEVER lexicographic.
    Used ONLY as a cross-check against the solver log's own last Time."""
    names = []
    for d in glob.glob(os.path.join(level_dir, "*")):
        if not os.path.isdir(d):
            continue
        b = os.path.basename(d)
        if re.match(r"^[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$", b):
            names.append((float(b), b))
    if not names:
        return None, None
    names.sort(key=lambda t: t[0])
    return names[-1][1], names[-1][0]


# --------------------------------------------------------------- OF readers ----
def _patch_block(text, patch):
    i = text.find("boundaryField")
    if i < 0:
        raise ValueError("no boundaryField")
    j = text.find(patch, i)
    if j < 0:
        raise ValueError("patch %s not found" % patch)
    k = text.find("{", j)
    depth, m = 0, k
    while m < len(text):
        if text[m] == "{":
            depth += 1
        elif text[m] == "}":
            depth -= 1
            if depth == 0:
                return text[k:m]
        m += 1
    raise ValueError("unterminated patch block")


_VEC_RE = re.compile(r"nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", re.S)
_SCA_RE = re.compile(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", re.S)
_INT_VEC_RE = re.compile(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", re.S)
_INT_SCA_RE = re.compile(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", re.S)


def read_patch_scalar(path, patch):
    p, txt = read_text(path, "patch scalar %s" % patch)
    blk = _patch_block(txt, patch)
    m = _SCA_RE.search(blk)
    if not m:
        raise SystemExit2("no nonuniform scalar list on patch %s in %s" % (patch, p))
    vals = [float(v) for v in m.group(2).split()]
    if len(vals) != int(m.group(1)):
        raise SystemExit2("scalar count mismatch on %s in %s" % (patch, p))
    return vals


def read_patch_vector3(path, patch):
    p, txt = read_text(path, "patch vector %s" % patch)
    blk = _patch_block(txt, patch)
    m = _VEC_RE.search(blk)
    if not m:
        raise SystemExit2("no nonuniform vector list on patch %s in %s" % (patch, p))
    trip = re.findall(r"\(([^()]*)\)", m.group(2))
    if len(trip) != int(m.group(1)):
        raise SystemExit2("vector count mismatch on %s in %s: %d vs %d"
                          % (patch, p, len(trip), int(m.group(1))))
    return [tuple(float(v) for v in t.split()) for t in trip]


def read_patch_vector_x(path, patch):
    return [t[0] for t in read_patch_vector3(path, patch)]


def read_internal_scalar(path):
    p, txt = read_text(path, "internal scalar")
    m = _INT_SCA_RE.search(txt)
    if not m:
        raise SystemExit2("no nonuniform internalField scalar list in %s" % p)
    return [float(v) for v in m.group(2).split()]


def read_internal_vector_x(path):
    p, txt = read_text(path, "internal vector")
    m = _INT_VEC_RE.search(txt)
    if not m:
        raise SystemExit2("no nonuniform internalField vector list in %s" % p)
    return [float(t.split()[0]) for t in re.findall(r"\(([^()]*)\)", m.group(2))]


# --------------------------------------------- in-place planting on REAL bytes --
def _plant_patch_vector_x(path, patch, delta):
    """Add `delta` to the x-component of EVERY face value of `patch`, in place, on a
    COPY of the real solver output. Header, dimensions and every other patch are
    left byte-untouched."""
    p, txt = read_text(path, "plant target %s" % patch)
    blk = _patch_block(txt, patch)
    m = _VEC_RE.search(blk)
    if not m:
        raise SystemExit2("plant: no vector list on patch %s in %s" % (patch, p))
    body = m.group(2)
    def _bump(mo):
        parts = mo.group(1).split()
        return "(%.12g %s %s)" % (float(parts[0]) + delta, parts[1], parts[2])
    newbody = re.sub(r"\(([^()]*)\)", _bump, body)
    newblk = blk.replace(body, newbody, 1)
    fh = open(p, "w")
    try:
        fh.write(txt.replace(blk, newblk, 1))
    finally:
        fh.close()


# ------------------------------------------------------- the gate functional ---
def wall_shear_window(level_dir, t):
    """(mean PHYSICAL wall shear in the developed window, in Pa; peak-to-peak/mean;
    the in-window abscissae and physical magnitudes; face count). The gate reads
    the KINEMATIC x-component of wallShearStress on the `wall` patch, takes |.| and
    multiplies by RHO to get Pa. REFUSES if the window is empty or non-uniform."""
    tau_kin = read_patch_vector_x(os.path.join(level_dir, t, "wallShearStress"), WALL_PATCH)
    xs      = read_patch_scalar(os.path.join(level_dir, t, "Cx"), WALL_PATCH)
    if len(xs) != len(tau_kin):
        raise SystemExit2("wall face count mismatch at %s/%s: Cx %d, wallShearStress %d"
                          % (level_dir, t, len(xs), len(tau_kin)))
    win = [(x, abs(tk) * RHO_KG) for x, tk in zip(xs, tau_kin) if X_DEV_LO <= x <= X_DEV_HI]
    if len(win) < 2:
        raise SystemExit2("wall shear: fewer than 2 `wall` faces in the developed window "
                          "[%g, %g] m at %s/%s -- cannot form the gate value"
                          % (X_DEV_LO, X_DEV_HI, level_dir, t))
    vals = [w[1] for w in win]
    mean = sum(vals) / len(vals)
    if mean <= 0.0:
        raise SystemExit2("wall shear: the mean physical wall shear in the window is %.12g "
                          "at %s/%s -- non-positive, nothing to grade" % (mean, level_dir, t))
    p2p_rel = (max(vals) - min(vals)) / mean
    if not (p2p_rel <= UNIFORM_TOL):
        raise SystemExit2("wall shear NOT DEVELOPED: peak-to-peak/mean = %.6g in the window "
                          "[%g, %g] m exceeds UNIFORM_TOL = %g at %s/%s. The flow is not "
                          "fully developed and a single-value wall-shear gate is meaningless."
                          % (p2p_rel, X_DEV_LO, X_DEV_HI, UNIFORM_TOL, level_dir, t))
    return {"mean_phys_Pa": mean, "p2p_rel": p2p_rel, "n_faces": len(win),
            "x_window": [w[0] for w in win], "tau_phys_window": vals}


def velocity_diagnostic(level_dir, t):
    """NOT A GATE (RULING 1). Sample the streamwise velocity at the developed
    cross-section nearest X_VEL_STATION and compare to the analytic parabola
    u(y) = U_MAX*(1 - ((delta - y)/delta)^2). Reports u_max, u_bar, full-profile
    RMS and whether the field is machine-exact. Never raises the row's verdict."""
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"))
    cy = read_internal_scalar(os.path.join(level_dir, t, "Cy"))
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"))
    if not (len(cx) == len(cy) == len(ux)):
        raise SystemExit2("internal field length mismatch at %s/%s: Cx %d Cy %d U %d"
                          % (level_dir, t, len(cx), len(cy), len(ux)))
    xstar = min(cx, key=lambda x: abs(x - X_VEL_STATION))
    col = [(cy[i], ux[i]) for i in range(len(cx)) if abs(cx[i] - xstar) < 1.0e-9]
    if len(col) < 2:
        raise SystemExit2("velocity diagnostic: fewer than 2 cells in the column at x=%.6g"
                          % xstar)
    col.sort()
    ys  = [c[0] for c in col]
    us  = [c[1] for c in col]
    ana = [U_MAX * (1.0 - ((DELTA - y) / DELTA) ** 2) for y in ys]
    rms = math.sqrt(sum((u - a) ** 2 for u, a in zip(us, ana)) / len(us))
    return {"x_station_actual_m": xstar, "n_cells": len(col),
            "u_max_sampled": max(us), "u_max_analytic": U_MAX,
            "u_bar_sampled": sum(us) / len(us), "u_bar_analytic": U_BAR,
            "rms_vs_analytic": rms, "rms_over_umax": rms / U_MAX,
            "machine_exact": bool(rms / U_MAX < VEL_EXACT_REL),
            "GATED": False}


# ---------------------------------------------------- planted-zero (rule 3) ----
def planted_zero_tau(level_dir, t):
    """CLAUDE.md rule 3, two stages, on the wall-shear channel. FIRED AT EVERY LEVEL.

    P1a -- READER SENSITIVITY. Plant a SIZED offset into the x-component of EVERY
           `wall` face of a COPY of the real solver file, read it back FROM DISK
           through the real reader, require every value to move by exactly the plant.
    P1b -- GATE-FUNCTIONAL SENSITIVITY. The SAME planted file run through the FULL
           gate functional: the mean physical wall shear must move by RHO*plant_kin.

    Either check failing REFUSES (exit 2)."""
    src = one_match(os.path.join(level_dir, t, "wallShearStress"), "plant source wallShearStress")
    tmp = tempfile.mkdtemp(prefix="vmfl038_plant_tau_")
    try:
        dst_dir = os.path.join(tmp, t)
        os.makedirs(dst_dir)
        dst = os.path.join(dst_dir, "wallShearStress")
        shutil.copy(src, dst)
        # Cx must sit beside the planted file so wall_shear_window can read the copy.
        shutil.copy(one_match(os.path.join(level_dir, t, "Cx"), "plant Cx"),
                    os.path.join(dst_dir, "Cx"))
        base_rep = read_patch_vector_x(dst, WALL_PATCH)
        base_win = wall_shear_window(tmp, t)
        inwin_kin = [abs(v) for v in base_rep]
        if not inwin_kin or max(inwin_kin) <= 0.0:
            raise SystemExit2("planted-zero: the `wall` kinematic shear is identically zero "
                              "-- there is nothing for a plant to be sized to")
        plant_kin = K_PLANT * (max(inwin_kin))
        # The wall shear x-component is uniform-sign (drag opposes the flow, so it is
        # negative here); the gate reads |tau_x|. Plant in the MAGNITUDE-INCREASING
        # direction so |tau| rises by plant_kin on every face and the gate mean rises
        # by exactly RHO*plant_kin -- a positive, known move the gate MUST see.
        sgn = 1.0 if (sum(base_rep) / len(base_rep)) >= 0.0 else -1.0
        delta_kin = sgn * plant_kin
        _plant_patch_vector_x(dst, WALL_PATCH, delta_kin)
        seen_rep = read_patch_vector_x(dst, WALL_PATCH)
        if len(seen_rep) != len(base_rep):
            raise SystemExit2("planted-zero: face count changed across the plant")
        worst = max(abs((seen_rep[i] - base_rep[i]) - delta_kin) for i in range(len(base_rep)))
        scale = max(abs(delta_kin), 1.0)
        if not (worst <= 1.0e-9 * scale):
            raise SystemExit2(
                "planted-zero control FAILED (P1a, reader sensitivity): planted %.12g into "
                "EVERY `wall` face of %s, worst read-back discrepancy %.12g. A reader not "
                "shown able to see a non-zero cannot certify a zero (CLAUDE.md rule 3)."
                % (delta_kin, src, worst))
        seen_win = wall_shear_window(tmp, t)
        expected_move = RHO_KG * plant_kin
        got_move = seen_win["mean_phys_Pa"] - base_win["mean_phys_Pa"]
        if not (abs(got_move - expected_move) <= 1.0e-6 * max(abs(expected_move), 1.0)):
            raise SystemExit2(
                "planted-zero control FAILED (P1b, gate-functional sensitivity): the reader "
                "saw the plant but the GATE FUNCTIONAL (mean physical wall shear) moved by "
                "%.12g Pa, not the expected RHO*plant = %.12g Pa. A plant the gate cannot see "
                "is worthless (CLAUDE.md rule 3)." % (got_move, expected_move))
        if not (got_move > PLANT_MIN_ABS):
            raise SystemExit2("planted-zero: the gate functional did not move at all (%.3g Pa)"
                              % got_move)
        return {"level_dir": level_dir, "time": t, "passed": True,
                "plant_kinematic": delta_kin, "plant_magnitude": plant_kin,
                "worst_readback_error": worst,
                "gate_mean_unplanted_Pa": base_win["mean_phys_Pa"],
                "gate_mean_planted_Pa": seen_win["mean_phys_Pa"],
                "gate_move_Pa": got_move, "expected_move_Pa": expected_move,
                "file": src, "patch": WALL_PATCH, "n_faces": len(base_rep)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------- strict completion --
def completion(run_root, level):
    """CLAUDE.md rule 4 IN FULL, adapted for a residualControl-terminated STEADY
    solve and DECLARED THAT WAY IN THE FROZEN PRE-REGISTRATION (sec.6): last Time
    STRICTLY LESS THAN endTime, because for a steady solve last == endTime means it
    ran out of clock WITHOUT converging. Split into L-342 field classes."""
    level_dir = os.path.join(run_root, level)
    out = {"level": level, "level_dir": level_dir}

    rcf = os.path.join(run_root, "RUN_RC.%s" % level)
    out["rc_source"] = rcf
    if not os.path.exists(rcf):
        out["rc"], out["rc_status"] = None, "NOT MEASURED"
        out["rc_note"] = ("RUN_RC.%s absent -- INFRASTRUCTURE field (L-342); the grade "
                          "proceeds on the physics-critical clauses." % level)
    else:
        _p, rct = read_text(rcf, "RUN_RC.%s" % level)
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)", rct, re.M)
        if not m:
            out["rc"], out["rc_status"] = None, "NOT MEASURED"
            out["rc_note"] = "RUN_RC.%s present but carries no rc= line (L-342)." % level
        else:
            out["rc"], out["rc_status"] = int(m.group(1)), "MEASURED"
            if out["rc"] != 0:
                raise SystemExit2("rc=%d recorded for %s (124 == the cap fired). A RECORDED "
                                  "non-zero rc is evidence about the SOLVER and refuses (L-342)."
                                  % (out["rc"], level))
        for key in ("wall_s", "core_min", "timeout_s"):
            mm = re.search(r"^\s*%s\s*=\s*([0-9.eE+-]+)" % key, rct, re.M)
            out[key] = float(mm.group(1)) if mm else None

    logp, lt = read_text(os.path.join(level_dir, "log.simpleFoam"), "solver log for %s" % level)
    out["log"] = logp
    out["end_lines"] = len(re.findall(r"^End\s*$", lt, re.M))
    if out["end_lines"] < 1:
        raise SystemExit2("no End line in %s" % logp)
    out["converged"] = ("SIMPLE solution converged" in lt)
    if not out["converged"]:
        raise SystemExit2("%s never reported 'SIMPLE solution converged' -- a steady solve that "
                          "did not meet its own residualControl is not a completed run" % logp)
    # residualControl lists p ONLY (Uy's normalised residual is a 0/0 artifact); the
    # comparator confirms the STREAMWISE momentum that sets the wall shear is settled.
    uxres = re.findall(r"Solving for Ux,\s*Initial residual = ([0-9.eE+-]+)", lt)
    if not uxres:
        raise SystemExit2("%s: no 'Solving for Ux' initial-residual lines -- cannot confirm the "
                          "streamwise momentum converged (residualControl is on p only)" % logp)
    out["ux_final_initial_residual"] = float(uxres[-1])
    if not (out["ux_final_initial_residual"] < ITER_RES_FLOOR):
        raise SystemExit2("%s: final Ux initial residual %.6g is not below ITER_RES_FLOOR %.3g -- "
                          "the streamwise momentum that sets the wall shear is not iteratively "
                          "settled" % (logp, out["ux_final_initial_residual"], ITER_RES_FLOOR))
    times = [int(x) for x in re.findall(r"^Time = (\d+)", lt, re.M)]
    if not times:
        raise SystemExit2("no Time lines in %s" % logp)
    out["last_time"] = times[-1]
    out["n_exec"] = lt.count("ExecutionTime")
    if out["n_exec"] != out["last_time"]:
        raise SystemExit2("%s: ExecutionTime count %d != last Time %d"
                          % (logp, out["n_exec"], out["last_time"]))

    cdp, ctl = read_text(os.path.join(level_dir, "system", "controlDict"), "controlDict for %s" % level)
    mE = re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    if not mE:
        raise SystemExit2("no endTime in %s" % cdp)
    out["endTime"] = float(mE.group(1))
    if not (out["last_time"] < out["endTime"]):
        raise SystemExit2("%s reached endTime %g -- it ran out of clock and did NOT converge "
                          "(the declared adaptation of rule 4 for a residualControl steady solve)"
                          % (level_dir, out["endTime"]))

    t = str(out["last_time"])
    out["time_dir"] = t
    nm, nv = numeric_latest_time_dir(level_dir)
    out["numeric_latest_time_dir"] = nm
    if nm is None or abs(nv - float(t)) > 1e-9:
        raise SystemExit2("time-directory disagreement at %s: the log's last Time is %s, the "
                          "numerically-latest directory (key=float) is %r -- the lexicographic "
                          "hazard in another costume (L-339)." % (level_dir, t, nm))
    for f in FIELDS:
        one_match(os.path.join(level_dir, t, f), "field %s at %s/%s" % (f, level, t))
    zpath = one_match(os.path.join(level_dir, AGE_DATUM), "age-guard datum %s" % AGE_DATUM)
    z = os.path.getmtime(zpath)
    for f in FIELDS:
        fp = os.path.join(level_dir, t, f)
        if not os.path.getmtime(fp) > z:
            raise SystemExit2("AGE GUARD: %s is not strictly newer than %s (CLAUDE.md rule 4)"
                              % (fp, zpath))
    out["age_guard"] = "all %d fields at %s newer than %s" % (len(FIELDS), t, AGE_DATUM)
    out["state"] = "COMPLETE"
    return out


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """CLAUDE.md rule 5. f1 coarse, f2 medium, f3 fine. A GCI is quoted ONLY on a
    CONVERGING triple whose observed order clears P_MIN. A difference below the
    round-off floor EXACT_REL*|f3| is treated as zero -- so a wall shear reproduced
    to round-off across the family lands EXACT -> NOT A RESULT (RULING 5)."""
    d32 = f3 - f2
    d21 = f2 - f1
    floor = EXACT_REL * max(abs(f3), 1.0e-300)
    z21 = abs(d21) < floor
    z32 = abs(d32) < floor
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "ratio": r, "fs": fs,
           "d21": d21, "d32": d32, "roundoff_floor": floor,
           "p": None, "gci_fine": None, "f_extrapolated": None}
    if z21 and z32:
        out["state"] = "EXACT"
        return out
    if z21 or z32:
        out["state"] = "STAGNANT"
        return out
    R = d32 / d21
    out["R"] = R
    if R < 0.0:
        out["state"] = "OSCILLATORY"
        return out
    if R >= 1.0:
        out["state"] = "DIVERGENT"
        return out
    p = math.log(abs(d21 / d32)) / math.log(r)
    out["p"] = p
    if p < P_MIN:
        out["state"] = "STAGNANT"
        out["p_floor"] = P_MIN
        out["p_below_floor"] = True
        return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


# ------------------------------------------------------------------ verdict ----
def verdict_for_limb_a(tri, dev, inside):
    """The ONE verdict path. Ceiling is PASS (analytical reference). Rule 5 is
    ONE-WAY: a non-CONVERGING triple, or a GCI above GCI_MAX, can only turn a
    verdict INTO NOT A RESULT (RULING 4/5), never the reverse."""
    gci = tri.get("gci_fine")
    if tri["state"] != "CONVERGING":
        if tri.get("p_below_floor"):
            v, why = ("NOT A RESULT",
                      "observed order p = %.6g below the frozen floor P_MIN = %.3g; triple %s, "
                      "no GCI quoted" % (tri["p"], P_MIN, tri["state"]))
        elif tri["state"] == "EXACT":
            v, why = ("NOT A RESULT",
                      "the wall shear is reproduced to the round-off floor across the family: "
                      "triple EXACT (CLAUDE.md rule 5 limb 2, RULING 5) -- NOT A RESULT whatever "
                      "the value. There is nothing to refine and no GCI.")
        else:
            v, why = ("NOT A RESULT",
                      "grid triple is %s, not CONVERGING (CLAUDE.md rule 5 limb 2) -- NOT A "
                      "RESULT whatever the value" % tri["state"])
    elif not inside:
        v, why = ("GATE FAIL",
                  "tau_w deviation %.4f %% exceeds the frozen band %.1f %% about the analytical "
                  "%.4g Pa" % (100.0 * dev, 100.0 * TOL, REF_TAU_W))
    elif gci is not None and gci > GCI_MAX:
        v, why = ("NOT A RESULT",
                  "the triple is CONVERGING and the value is inside the %.1f %% band, but the "
                  "fine-grid GCI %.4f %% exceeds the frozen ceiling GCI_MAX %.1f %%: the "
                  "discretisation uncertainty is larger than the band it must sit inside, so a "
                  "PASS cannot be certified (RULING 4). A large GCI does not ride inside a PASS."
                  % (100.0 * TOL, 100.0 * gci, 100.0 * GCI_MAX))
    else:
        v, why = ("PASS",
                  "tau_w deviation %.4f %% is inside the frozen %.1f %% band about the ANALYTICAL "
                  "%.4g Pa on a CONVERGING triple with fine-grid GCI %.4f %% <= %.1f %%. The "
                  "reference is a closed-form solution of the SAME continuum model the solver "
                  "discretises (Bird/Stewart/Lightfoot p.45), so model-form error is zero by "
                  "construction and PASS is available."
                  % (100.0 * dev, 100.0 * TOL, REF_TAU_W,
                     0.0 if gci is None else 100.0 * gci, 100.0 * GCI_MAX))
    if v not in VOCAB:
        raise SystemExit2("verdict %r is outside the fixed vocabulary (CLAUDE.md rule 1)" % v)
    if v == "PASS" and TIER_CEILING != "PASS":
        raise SystemExit2("TIER CEILING VIOLATED: emitted PASS against ceiling %r" % TIER_CEILING)
    return v, why


def sha256_file(pattern, what):
    p = one_match(pattern, what)
    h = hashlib.sha256()
    fh = open(p, "rb")
    try:
        while True:
            b = fh.read(65536)
            if not b:
                break
            h.update(b)
    finally:
        fh.close()
    return p, h.hexdigest()


def derive_reference():
    """DERIVE THE GATE VALUE BY TWO INDEPENDENT ROUTES AND CROSS-CHECK (RULING 1).
    Also derives the geometry from the manual by two independent dp/L routes
    (RULING 2) and the manual's units-error factor (RULING 3). REFUSES on any
    disagreement -- a single derivation of a gate value is an unchecked derivation."""
    sin_beta = math.sin(math.radians(BETA_DEG))
    # geometry, two independent routes to the streamwise pressure gradient
    dpdl_pressure = DELTA_P / L_LEN            # from the printed Delta_p and the derived L
    dpdl_head     = RHO * G_GRAV * sin_beta    # from the physical driving head
    if abs(dpdl_pressure - dpdl_head) / dpdl_pressure > 1.0e-6:
        raise SystemExit2("derive_reference: dp/L disagreement -- pressure route %.10g vs head "
                          "route %.10g Pa/m" % (dpdl_pressure, dpdl_head))
    # tau_w, two independent routes (RULING 1)
    tau_route1 = MU * 2.0 * U_MAX / DELTA      # mu * 2 u_max / delta
    tau_route2 = DPDL * DELTA                  # (dp/L) * delta  (global force balance)
    if abs(tau_route1 - tau_route2) / tau_route1 > 1.0e-9:
        raise SystemExit2("derive_reference: tau_w routes disagree -- %.12g vs %.12g Pa"
                          % (tau_route1, tau_route2))
    if abs(tau_route1 - REF_TAU_W) / REF_TAU_W > 1.0e-6:
        raise SystemExit2("derive_reference: derived tau_w %.12g Pa != frozen REF_TAU_W %.12g Pa"
                          % (tau_route1, REF_TAU_W))
    # the manual's PRINTED geometry (1 m x 18 m as absolute) vs the derived geometry
    l_self = DELTA_P / (RHO * G_GRAV * sin_beta)   # self-consistent L; ~0.18 m
    factor = 18.0 / l_self                          # ~100, the units error (RULING 3)
    # printed "1 m X 18 m" as ABSOLUTE: delta = 1 m, L = 18 m, so the printed dp/L is
    # Delta_p / 18 = 39.24 Pa/m and u_max = (dp/L)*delta^2/(2 mu) = 19.62 m/s = 100x the
    # correct 0.1962 m/s. (Note tau_w = (dp/L)*delta = 39.24 Pa is UNCHANGED by the units
    # error -- it depends only on Delta_p and the 1:18 aspect ratio, both printed correctly.)
    umax_printed = (DELTA_P / 18.0) * (1.0 ** 2) / (2.0 * MU)   # 19.62 m/s
    return {"sin_beta": sin_beta, "dpdl_pressure": dpdl_pressure, "dpdl_head": dpdl_head,
            "tau_route1_mu2umax_over_delta": tau_route1, "tau_route2_dpdl_times_delta": tau_route2,
            "ref_tau_w_Pa": REF_TAU_W, "u_max": U_MAX, "u_bar": U_BAR,
            "L_self_consistent_m": l_self, "manual_units_error_factor": factor,
            "umax_if_printed_taken_absolute": umax_printed}


# --------------------------------------------------- constructed-field writers -
def _wss(patch, xs, tau_kin):
    body = "\n".join("(%.12g 0 0)" % v for v in tau_kin)
    return ("FoamFile { version 2.0; format ascii; class volVectorField; object wallShearStress; }\n"
            "dimensions [0 2 -2 0 0 0 0];\ninternalField uniform (0 0 0);\n"
            "boundaryField {\n    %s { type calculated; value nonuniform List<vector> %d (\n%s\n); }\n}\n"
            % (patch, len(tau_kin), body))


def _cx_patch(patch, xs, obj="Cx"):
    vv = " ".join("%.12g" % v for v in xs)
    return ("FoamFile { version 2.0; format ascii; class volScalarField; object %s; }\n"
            "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
            "boundaryField {\n    %s { type calculated; value nonuniform List<scalar> %d ( %s ); }\n}\n"
            % (obj, len(xs), vv, patch, len(xs), vv))


def _int_scalar(obj, vals):
    return ("FoamFile { version 2.0; format ascii; class volScalarField; object %s; }\n"
            "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
            "boundaryField {\n    wall { type zeroGradient; }\n}\n"
            % (obj, len(vals), " ".join("%.12g" % v for v in vals)))


def _int_U(trips):
    body = "\n".join("(%.12g %.12g %.12g)" % t for t in trips)
    return ("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
            "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> %d (\n%s\n);\n"
            "boundaryField {\n    wall { type noSlip; }\n}\n" % (len(trips), body))


def _int_p(n):
    return ("FoamFile { version 2.0; format ascii; class volScalarField; object p; }\n"
            "dimensions [0 2 -2 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
            "boundaryField {\n    wall { type zeroGradient; }\n}\n"
            % (n, " ".join(["0"] * n)))


def _write_level(root, level, tau_phys, endtime=30000, iters=1234, converged=True,
                 end_line=True, exec_mismatch=False, age_ok=True, rc="0", write_rc=True,
                 fields=FIELDS, u_scale=1.0, ux_res=1.0e-7):
    """Build a complete synthetic level directory. `tau_phys` is the PHYSICAL wall
    shear (Pa) encoded uniformly on the wall patch (as kinematic tau_phys/RHO). The
    internal velocity column at X_VEL_STATION carries the analytic parabola scaled
    by u_scale (u_scale != 1 perturbs the DIAGNOSTIC only, never the gate)."""
    d = os.path.join(root, level)
    os.makedirs(os.path.join(d, "system"))
    os.makedirs(os.path.join(d, "0"))
    t = str(iters)
    os.makedirs(os.path.join(d, t))
    # wall patch: faces across the whole plane length (so the developed window is populated)
    nx = 24
    xs_wall = [L_LEN * (i + 0.5) / nx for i in range(nx)]
    tau_kin = [-(tau_phys / RHO) for _ in xs_wall]     # negative sign -> reader takes |.|
    # internal grid: nx columns x ny rows, parabolic U_x
    ny = 8
    cxi, cyi, uxi = [], [], []
    for i in range(nx):
        for j in range(ny):
            xc = L_LEN * (i + 0.5) / nx
            yc = DELTA * (j + 0.5) / ny
            cxi.append(xc)
            cyi.append(yc)
            uxi.append(u_scale * U_MAX * (1.0 - ((DELTA - yc) / DELTA) ** 2))
    fh = open(os.path.join(d, "0", "U"), "w"); fh.write(_int_U([(0.0, 0.0, 0.0)] * len(uxi))); fh.close()
    body = []
    for i in range(1, iters + 1):
        body.append("Time = %d\n" % i)
        body.append("smoothSolver:  Solving for Ux, Initial residual = %.6g, Final residual = "
                    "%.6g, No Iterations 5\n" % (ux_res, ux_res * 0.1))
        body.append("ExecutionTime = %.2f s  ClockTime = %d s\n" % (0.01 * i, i))
    if exec_mismatch:
        body.append("ExecutionTime = 9 s\n")
    if converged:
        body.append("SIMPLE solution converged in %d iterations\n" % iters)
    if end_line:
        body.append("End\n")
    fh = open(os.path.join(d, "log.simpleFoam"), "w"); fh.write("".join(body)); fh.close()
    fh = open(os.path.join(d, "system", "controlDict"), "w")
    fh.write("application simpleFoam;\nendTime         %d;\n" % endtime); fh.close()
    present = set(fields)
    if "wallShearStress" in present:
        fh = open(os.path.join(d, t, "wallShearStress"), "w"); fh.write(_wss(WALL_PATCH, xs_wall, tau_kin)); fh.close()
    if "Cx" in present:
        fh = open(os.path.join(d, t, "Cx"), "w"); fh.write(_cx_patch(WALL_PATCH, xs_wall, "Cx")); fh.close()
        # internal Cx sits in the SAME file's internalField in OF; here the reader for
        # the velocity diagnostic reads internalField Cx, so overwrite with a file that
        # carries BOTH the internal list and the wall patch list.
        fh = open(os.path.join(d, t, "Cx"), "w")
        fh.write("FoamFile { version 2.0; format ascii; class volScalarField; object Cx; }\n"
                 "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
                 "boundaryField {\n    %s { type calculated; value nonuniform List<scalar> %d ( %s ); }\n}\n"
                 % (len(cxi), " ".join("%.12g" % v for v in cxi), WALL_PATCH, len(xs_wall),
                    " ".join("%.12g" % v for v in xs_wall)))
        fh.close()
    if "Cy" in present:
        fh = open(os.path.join(d, t, "Cy"), "w"); fh.write(_int_scalar("Cy", cyi)); fh.close()
    if "U" in present:
        fh = open(os.path.join(d, t, "U"), "w"); fh.write(_int_U([(u, 0.0, 0.0) for u in uxi])); fh.close()
    if "p" in present:
        fh = open(os.path.join(d, t, "p"), "w"); fh.write(_int_p(len(uxi))); fh.close()
    old = os.path.getmtime(os.path.join(d, "0", "U"))
    off = 100 if age_ok else -100
    for f in os.listdir(os.path.join(d, t)):
        os.utime(os.path.join(d, t, f), (old + off, old + off))
    if write_rc:
        fh = open(os.path.join(root, "RUN_RC.%s" % level), "w")
        fh.write("rc = %s\nlevel = %s\nwall_s = 10\nranks = 1\ncore_min = 0.1667\ntimeout_s = 900\n"
                 % (rc, level)); fh.close()
    return d, t


# ------------------------------------------------------------- the AST guard ---
def _ast_guard():
    """Walk THIS FILE's own AST and refuse if it contains any `assert` (L-332)."""
    src = open(os.path.abspath(__file__), errors="replace").read()
    tree = ast.parse(src)
    n = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
    if n != 0:
        raise SystemExit2("AST GUARD: this comparator contains %d `assert` statement(s); "
                          "`python3 -O` deletes them, so they are not controls (L-332)." % n)
    return n


# ---------------------------------------------------------------- SELFTEST -----
_RESULTS = []


def ck(name, ok):
    _RESULTS.append((name, bool(ok)))
    print("  [%s] %s" % ("PASS" if ok else "FAIL", name))


def _refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except SystemExit as e:
        return getattr(e, "code", None) == 2
    except Exception:
        return False
    return False


def selftest():
    print("SELFTEST VMFL038 -- Falling Film Over an Inclined Plane (VM2026R1 p.131-132)")

    ck("AST guard: ast.Assert count is 0 in this file", _ast_guard() == 0)

    # ---- the reference is DERIVED by two routes that cross-check -----------------
    ref = derive_reference()
    ck("derive_reference: tau_w route1 (mu*2*u_max/delta) == route2 ((dp/L)*delta) == 39.24 Pa",
       abs(ref["tau_route1_mu2umax_over_delta"] - 39.24) < 1e-9 and
       abs(ref["tau_route2_dpdl_times_delta"] - 39.24) < 1e-9)
    ck("derive_reference: dp/L pressure route == head route (rho*g*sin beta) = 3924 Pa/m",
       abs(ref["dpdl_pressure"] - ref["dpdl_head"]) < 1e-6 and abs(ref["dpdl_pressure"] - 3924.0) < 1e-6)
    ck("derive_reference: geometry L = 0.18 m and manual units-error factor ~ 100 (RULING 3)",
       abs(ref["L_self_consistent_m"] - 0.18) < 1e-9 and abs(ref["manual_units_error_factor"] - 100.0) < 1e-6)
    ck("derive_reference: printed 1 m film would give u_max 19.62 m/s = 100x the correct 0.1962",
       abs(ref["umax_if_printed_taken_absolute"] - 19.62) < 1e-6)
    ck("u_max 0.1962 and u_bar 0.1308 m/s from the frozen constants (diagnostics)",
       abs(U_MAX - 0.1962) < 1e-9 and abs(U_BAR - 0.1308) < 1e-6)

    tmp = tempfile.mkdtemp(prefix="vmfl038_selftest_")
    try:
        # ---- cardinality guard ------------------------------------------------
        os.makedirs(os.path.join(tmp, "card"))
        fh = open(os.path.join(tmp, "card", "only.txt"), "w"); fh.write("x"); fh.close()
        ck("one_match returns the single match",
           one_match(os.path.join(tmp, "card", "only.txt"), "t") == os.path.join(tmp, "card", "only.txt"))
        ck("one_match REFUSES on zero matches", _refuses(one_match, os.path.join(tmp, "card", "missing.txt"), "t"))
        fh = open(os.path.join(tmp, "card", "twin.txt"), "w"); fh.write("y"); fh.close()
        ck("one_match REFUSES on two matches", _refuses(one_match, os.path.join(tmp, "card", "*.txt"), "t"))

        # ---- numeric, never lexicographic, time-dir ordering ------------------
        os.makedirs(os.path.join(tmp, "tord"))
        for nm in ("0", "950", "2000"):
            os.makedirs(os.path.join(tmp, "tord", nm))
        nm, nv = numeric_latest_time_dir(os.path.join(tmp, "tord"))
        ck("time dirs sort NUMERICALLY: 2000 beats 950 (lexicographic would say 950)",
           nm == "2000" and nv == 2000.0)
        ck("the lexicographic answer is demonstrably different here",
           sorted(["0", "950", "2000"])[-1] == "950")

        # ---- strict completion, every clause ----------------------------------
        good = os.path.join(tmp, "good"); os.makedirs(good)
        _write_level(good, "L1", 39.18)
        c = completion(good, "L1")
        ck("completion: a clean level is COMPLETE with rc MEASURED = 0",
           c["state"] == "COMPLETE" and c["rc"] == 0 and c["rc_status"] == "MEASURED")
        ck("completion: age guard reported", "newer than" in c["age_guard"])
        for tag, kw in (("no End line", {"end_line": False}),
                        ("no SIMPLE convergence", {"converged": False}),
                        ("age guard violated", {"age_ok": False}),
                        ("ExecutionTime count mismatch", {"exec_mismatch": True})):
            r = os.path.join(tmp, "bad_" + tag.replace(" ", "_")); os.makedirs(r)
            _write_level(r, "L1", 39.18, **kw)
            ck("completion REFUSES: %s" % tag, _refuses(completion, r, "L1"))
        r = os.path.join(tmp, "bad_clock"); os.makedirs(r)
        _write_level(r, "L1", 39.18, endtime=1234, iters=1234)
        ck("completion REFUSES: last Time == endTime (ran out of clock, never converged)",
           _refuses(completion, r, "L1"))
        r = os.path.join(tmp, "bad_field"); os.makedirs(r)
        _write_level(r, "L1", 39.18, fields=("U", "p", "Cx", "Cy"))
        ck("completion REFUSES: a declared field (wallShearStress) missing at endTime",
           _refuses(completion, r, "L1"))
        r = os.path.join(tmp, "bad_rc"); os.makedirs(r)
        _write_level(r, "L1", 39.18, rc="124")
        ck("completion REFUSES: a RECORDED non-zero rc (the cap fired)", _refuses(completion, r, "L1"))
        r = os.path.join(tmp, "no_rc"); os.makedirs(r)
        _write_level(r, "L1", 39.18, write_rc=False)
        c2 = completion(r, "L1")
        ck("completion PROCEEDS with rc NOT MEASURED when RUN_RC is absent (L-342)",
           c2["state"] == "COMPLETE" and c2["rc_status"] == "NOT MEASURED")
        r = os.path.join(tmp, "bad_tdir"); os.makedirs(r)
        d, t = _write_level(r, "L1", 39.18); os.makedirs(os.path.join(d, "9999"))
        ck("completion REFUSES: numerically-latest time dir disagrees with the log's last Time",
           _refuses(completion, r, "L1"))
        r = os.path.join(tmp, "bad_uxres"); os.makedirs(r)
        _write_level(r, "L1", 39.18, ux_res=1.0e-3)   # streamwise momentum NOT settled
        ck("completion REFUSES: final Ux initial residual above ITER_RES_FLOOR (p-only "
           "residualControl means Ux convergence is confirmed by the comparator)",
           _refuses(completion, r, "L1"))
        gc = os.path.join(tmp, "good_ux"); os.makedirs(gc)
        _write_level(gc, "L1", 39.18)
        ck("completion: records the final Ux initial residual (below the floor) as settled",
           completion(gc, "L1")["ux_final_initial_residual"] < ITER_RES_FLOOR)

        # ---- the gate functional and its uniformity control -------------------
        w = wall_shear_window(good + "/L1", "1234")
        ck("wall-shear gate recovers the PHYSICAL Pa (kinematic x RHO): ~39.18 Pa",
           abs(w["mean_phys_Pa"] - 39.18) < 1e-6)
        ck("wall-shear window is spatially uniform (p2p/mean below UNIFORM_TOL)",
           w["p2p_rel"] < UNIFORM_TOL)
        # a non-uniform wall shear REFUSES
        nu_dir = os.path.join(tmp, "nonuni"); os.makedirs(nu_dir)
        dd, tt = _write_level(nu_dir, "L1", 39.18)
        wssf = os.path.join(dd, tt, "wallShearStress")
        s = open(wssf).read()
        old = "(%.12g 0 0)" % (-(39.18 / RHO))
        new = "(%.12g 0 0)" % (-(39.18 / RHO) * 2.0)
        s = new.join(s.rsplit(old, 1))   # spike the LAST wall face (x in the developed window)
        open(wssf, "w").write(s)
        ck("wall-shear REFUSES a non-developed (non-uniform) window", _refuses(wall_shear_window, nu_dir + "/L1", "1234"))

        # ---- velocity DIAGNOSTIC (not gated) ----------------------------------
        vd = velocity_diagnostic(good + "/L1", "1234")
        ck("velocity diagnostic recovers the analytic parabola (machine-exact) and GATES NOTHING",
           vd["machine_exact"] and vd["GATED"] is False)
        pert = os.path.join(tmp, "vpert"); os.makedirs(pert)
        _write_level(pert, "L1", 39.18, u_scale=1.05)
        vd2 = velocity_diagnostic(pert + "/L1", "1234")
        ck("velocity diagnostic: a 5%% velocity perturbation is NOT machine-exact (a real reader)",
           not vd2["machine_exact"] and vd2["rms_over_umax"] > 1e-3)

        # ---- planted zero, both stages, and shown able to FAIL ----------------
        pz = planted_zero_tau(good + "/L1", "1234")
        ck("planted zero P1a: the wall-shear reader SEES a sized all-face plant",
           pz["passed"] and pz["worst_readback_error"] < 1e-12)
        ck("planted zero P1b: the plant MOVES the gate functional by RHO*plant (Pa)",
           abs(pz["gate_move_Pa"] - pz["expected_move_Pa"]) < 1e-6 and pz["gate_move_Pa"] > 0)
        blind = os.path.join(tmp, "blind"); os.makedirs(blind)
        _write_level(blind, "L1", 0.0)      # identically-zero wall shear -> nothing to size
        ck("planted zero REFUSES when the channel it must size against is identically zero",
           _refuses(planted_zero_tau, blind + "/L1", "1234"))
        saved = globals()["_plant_patch_vector_x"]
        globals()["_plant_patch_vector_x"] = lambda path, patch, delta: None
        ck("planted zero REFUSES against a BLIND writer (the plant never reaches disk) -- "
           "the control is shown able to FAIL", _refuses(planted_zero_tau, good + "/L1", "1234"))
        globals()["_plant_patch_vector_x"] = saved

        # ---- Roache, every state, and the EXACT round-off floor (RULING 5) ----
        ck("roache CONVERGING on a first-order sequence (the wall-shear O(dy) error)",
           roache(38.9948, 39.1173, 39.1787)["state"] == "CONVERGING")
        ck("roache DIVERGENT", roache(39.0, 39.1, 39.3)["state"] == "DIVERGENT")
        ck("roache OSCILLATORY", roache(39.0, 39.2, 39.1)["state"] == "OSCILLATORY")
        ck("roache STAGNANT (one difference below the round-off floor)",
           roache(39.24, 39.24, 39.1)["state"] == "STAGNANT")
        ck("roache EXACT: a wall shear reproduced to round-off across the family -> EXACT (RULING 5)",
           roache(39.24, 39.24 + 1e-11, 39.24 - 1e-11)["state"] == "EXACT")
        tri1 = roache(38.9948, 39.1173, 39.1787)
        ck("roache: observed order p ~ 1 recovered on the first-order sequence",
           abs(tri1["p"] - 1.0) < 0.05)
        ck("roache: a GCI is quoted on the CONVERGING triple", tri1["gci_fine"] is not None)
        for st, tr in (("EXACT", (39.24, 39.24 + 1e-11, 39.24 - 1e-11)),
                       ("STAGNANT", (39.24, 39.24, 39.1)), ("OSCILLATORY", (39.0, 39.2, 39.1)),
                       ("DIVERGENT", (39.0, 39.1, 39.3))):
            ck("NO GCI when the triple is %s" % st, roache(*tr)["gci_fine"] is None)

        # ---- the verdict: PASS, GATE FAIL, NOT A RESULT(EXACT), NOT A RESULT(GCI) ----
        tri_pass = roache(38.9948, 39.1173, 39.1787)  # fine 39.1787, dev 0.156%, GCI ~0.2%
        dev_pass = abs(tri_pass["f_fine"] - REF_TAU_W) / REF_TAU_W
        ck("verdict PASS: CONVERGING, inside 2%% band, GCI below GCI_MAX (analytical reference)",
           verdict_for_limb_a(tri_pass, dev_pass, dev_pass <= TOL)[0] == "PASS")
        tri_fail = roache(30.0, 30.5, 30.75)          # fine 30.75, dev ~21.6%
        dev_fail = abs(tri_fail["f_fine"] - REF_TAU_W) / REF_TAU_W
        ck("verdict GATE FAIL: CONVERGING but the value is OUTSIDE the band (end-to-end arm)",
           verdict_for_limb_a(tri_fail, dev_fail, dev_fail <= TOL)[0] == "GATE FAIL")
        tri_exact = roache(39.24, 39.24 + 1e-11, 39.24 - 1e-11)
        ck("verdict NOT A RESULT: EXACT triple, even with the value exactly on the reference (RULING 5)",
           verdict_for_limb_a(tri_exact, 0.0, True)[0] == "NOT A RESULT")
        # a CONVERGING triple whose GCI exceeds GCI_MAX -> NOT A RESULT (RULING 4).
        # Slow convergence (R ~ 0.91, p ~ 0.14) with the value dead on the reference:
        # CONVERGING and inside the band, yet fine-grid GCI ~ 3 % > GCI_MAX 2 %.
        tri_bigci = roache(39.03, 39.14, 39.24)
        dev_bigci = abs(tri_bigci["f_fine"] - REF_TAU_W) / REF_TAU_W
        ck("verdict NOT A RESULT: CONVERGING and inside the band but GCI > GCI_MAX (RULING 4)",
           tri_bigci["state"] == "CONVERGING" and dev_bigci <= TOL and tri_bigci["gci_fine"] > GCI_MAX and
           verdict_for_limb_a(tri_bigci, dev_bigci, True)[0] == "NOT A RESULT")
        ck("rule 5 is ONE-WAY: a non-CONVERGING triple is NOT A RESULT even inside the band",
           verdict_for_limb_a(roache(39.0, 39.2, 39.1), 0.0, True)[0] == "NOT A RESULT")

        # ---- the frozen reference and band are what the design says -----------
        ck("reference is the ANALYTICAL 39.24 Pa (Bird/Stewart/Lightfoot p.45)", REF_TAU_W == 39.24)
        ck("band is the frozen A-PRIORI 2%% and GCI ceiling is 2%%", TOL == 0.02 and GCI_MAX == 0.02)
        ck("tier ceiling is PASS (analytical reference of the solved model)", TIER_CEILING == "PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n = len(_RESULTS)
    bad = [r for r in _RESULTS if not r[1]]
    print("SELFTEST: %d checks, %d failures" % (n, len(bad)))
    if bad:
        print("SELFTEST: FAILED")
        return 1
    print("SELFTEST: all checks passed")
    return 0


# -------------------------------------------------------------------- main -----
def verify_frozen():
    import subprocess
    repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if not repo:
        raise SystemExit2("--verify-frozen: not inside a git repository")
    rc = 0
    for rel in ("cases/ansys_verification/VMFL038/PREREGISTRATION.md",
                "cases/ansys_verification/VMFL038/grade_vmfl038.py"):
        disk = subprocess.run(["git", "-C", repo, "hash-object", os.path.join(repo, rel)],
                              capture_output=True, text=True).stdout.strip()
        head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD:" + rel],
                              capture_output=True, text=True).stdout.strip()
        if not re.match(r"^[0-9a-f]{40}$", head):
            head = ""
        same = bool(disk) and disk == head
        print("%-64s disk=%s head=%s %s" % (rel, disk or "?", head or "?", "OK" if same else "MISMATCH"))
        if not same:
            rc = 2
    return rc


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify-frozen" in argv:
        return verify_frozen()

    run_root, out_path = RUN_ROOT, None
    for i, a in enumerate(argv):
        if a == "--run-root" and i + 1 < len(argv):
            run_root = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out_path = argv[i + 1]
    run_root = os.path.abspath(run_root)

    R = {"case": "VMFL038", "manual_page": "131-132",
         "title": "Falling Film Over an Inclined Plane",
         "reference": {"quantity": "tau_w, physical wall shear stress on the inclined plane, Pa",
                       "value": REF_TAU_W, "kind": "ANALYTICAL",
                       "source": "Bird, Stewart & Lightfoot, Transport Phenomena, p.45, "
                                 "closed-form falling-film solution (VM2026R1 p.131 Reference)"},
         "band": TOL, "gci_max": GCI_MAX, "developed_window_m": [X_DEV_LO, X_DEV_HI],
         "tier_ceiling": TIER_CEILING, "rho": RHO, "field_classes": FIELD_CLASSES,
         "run_root": run_root, "derivation": derive_reference(), "levels": {}}
    R["ast_assert_count"] = _ast_guard()

    for lv in LEVELS:
        R["levels"][lv] = completion(run_root, lv)

    # controls fire at ALL THREE levels before any value is believed (RULING).
    R["planted_zero"] = [planted_zero_tau(R["levels"][lv]["level_dir"], R["levels"][lv]["time_dir"])
                         for lv in LEVELS]

    vals = {}
    for lv in LEVELS:
        c = R["levels"][lv]
        w = wall_shear_window(c["level_dir"], c["time_dir"])
        vd = velocity_diagnostic(c["level_dir"], c["time_dir"])
        c["wall_shear"] = w
        c["velocity_diagnostic"] = vd
        vals[lv] = w["mean_phys_Pa"]

    tri = roache(vals["L1"], vals["L2"], vals["L3"])
    R["triple"] = tri
    fine = vals["L3"]
    dev = abs(fine - REF_TAU_W) / abs(REF_TAU_W)
    inside = dev <= TOL
    va, wa = verdict_for_limb_a(tri, dev, inside)
    R["limb_A"] = {"class": "CONTINUUM, ANALYTICAL reference (PASS-capable)",
                   "tau_w_Pa": {lv: vals[lv] for lv in LEVELS}, "finest_Pa": fine,
                   "reference_Pa": REF_TAU_W, "deviation_rel": dev, "band": TOL,
                   "gci_max": GCI_MAX, "inside": inside, "ceiling": TIER_CEILING,
                   "verdict": va, "why": wa}
    R["verdict"] = va

    print("VMFL038  (VM2026R1 p.131-132)  VERDICT: %s" % va)
    print("  tau_w L1/L2/L3 = %.6f / %.6f / %.6f Pa" % (vals["L1"], vals["L2"], vals["L3"]))
    print("  finest %.6f vs analytical %.4g Pa, deviation %.4f %% , band %.1f %%  -> %s"
          % (fine, REF_TAU_W, 100.0 * dev, 100.0 * TOL, va))
    print("  triple %s, p = %s, GCI_fine = %s (ceiling %.1f %%)"
          % (tri["state"], "n/a" if tri["p"] is None else "%.6f" % tri["p"],
             "n/a" if tri["gci_fine"] is None else "%.6f%%" % (100.0 * tri["gci_fine"]),
             100.0 * GCI_MAX))
    vdl3 = R["levels"]["L3"]["velocity_diagnostic"]
    print("  velocity DIAGNOSTIC (not gated): u_max %.6f (analytic %.4g), u_bar %.6f (analytic %.4g), "
          "RMS/u_max %.3e, machine_exact=%s"
          % (vdl3["u_max_sampled"], U_MAX, vdl3["u_bar_sampled"], U_BAR,
             vdl3["rms_over_umax"], vdl3["machine_exact"]))
    if out_path:
        fh = open(out_path, "w")
        try:
            json.dump(R, fh, indent=2, sort_keys=True, default=str)
        finally:
            fh.close()
        print("  grading record: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
