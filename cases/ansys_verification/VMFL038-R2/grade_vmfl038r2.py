#!/usr/bin/env python3
"""VMFL038-R2 comparator -- Falling Film Over an Inclined Plane.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.131-132.
Frozen pre-registration: cases/ansys_verification/VMFL038-R2/PREREGISTRATION.md

TWO LIMBS, and they are graded and reported SEPARATELY:

  LIMB A -- tau_w = 39.24 Pa, NO ROACHE TRIPLE, as a FLOOR DEMONSTRATION under
    VERIFICATION_CHARTER sec.2h.4's five conditions. The wall shear on this problem is
    pinned to the exact value by DISCRETE GLOBAL MOMENTUM CONSERVATION on any mesh, so
    it carries no discretisation error to refine and a triple on it would be
    structurally EXACT -> CLAUDE.md rule 5 limb (2) -> NOT A RESULT. The limb's
    sentence is "the discretisation error in the wall shear stress is below 1e-8
    relative at 1800, 7200 and 28800 cells" -- a claim about THE DISCRETISATION, never
    about the continuum solution, which is what makes sec.2f.3's cap not reach it
    (sec.2h.2).

  LIMB B -- u_bar = 0.1308 m/s, WITH the Roache triple. Its discretisation error is
    K*h^2/6 = 0.0654/Ny^2, provably and exactly second order (PREREGISTRATION sec.4.3),
    so it forms a genuine CONVERGING triple. PASS-capable per ANSYS_VERIFICATION
    sec.11.1 -> rule 5 step 3.

BOTH reference values are DERIVED HERE, in double precision, by TWO INDEPENDENT ROUTES
each, and are never transcribed from any table, archive or figure.

PHASE ORDER IS FIXED AND IS ITSELF A CONTROL (PREREGISTRATION sec.8 requirement 1):
  PHASE 0  AST guard over this file's own bytes
  PHASE 1  discovery only -- level dirs, NUMERIC latest time dir, cardinality refusals
  PHASE 2  PLANTED ZERO, both channels, ALL THREE LEVELS   <-- BEFORE ANY OTHER CLAUSE
  PHASE 3  strict completion (CLAUDE.md rule 4, original form)
  PHASE 4  convergence -- the DISJUNCTION of sec.6.2
  PHASE 5  functionals, uniformity, diagnostics
  PHASE 6  triple, limb A floor, limb B gate, verdict
VMFL006's plant loop registered ZERO entries because a refusal fired ahead of it, and
an absent control is indistinguishable in a JSON from one that passed vacuously.
Nothing in phases 3-6 executes before phase 2 has written its six plant records.

NO `assert` STATEMENT APPEARS IN THIS FILE, and `_ast_guard()` REFUSES if one ever
does. `python3 -O` deletes asserts, so an assert is a control that vanishes under the
optimiser (L-332). Every check raises.

Exit codes: 0 = graded (the verdict is in the record, not in the rc); 2 = REFUSED.
"""
import argparse
import ast
import datetime
import glob
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUN_ROOT = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "verification", "runs", "ansys_verification", "VMFL038-R2"))

# ---------------------------------------------------------------- material -----
RHO = 800.0                 # density, kg/m3            (manual p.131)
MU = 1.0                    # dynamic viscosity, kg/m-s (manual p.131)
NU = MU / RHO               # kinematic viscosity, m2/s (= 0.00125)
G_GRAV = 9.81               # standard gravity, m/s2 -- used ONLY to derive geometry
BETA_DEG = 30.0             # inclination, degrees      (manual p.131)
DELTA_P = 706.32            # |driving pressure difference|, N/m2 (outlet gauge)

# --------------------------------------------------------------- geometry ------
# DERIVED FROM THE MANUAL'S OWN PRINTED NUMBERS. The printed "1 m X 18 m" is a
# metre-for-centimetre UNITS ERROR, exactly 100x (VMFL038/MANUAL_DEFECT_geometry_units.md,
# NOT FILED). A setup input may come from the archive; a gate value may not, ever.
L_LEN = 0.18                # plane length, m  (= 706.32 / (800*9.81*sin30))
DELTA = 0.01                # film thickness, m  (= L/18, the printed 1:18 ratio)
DPDL = DELTA_P / L_LEN      # streamwise pressure gradient, 3924 Pa/m
K_CURV = DPDL / MU          # u'' = -K_CURV; 3924 1/(m s)

# ------------------------------------------------------------- FROZEN GATES ----
REF_TAU_W = DPDL * DELTA                    # 39.24 Pa   -- derived, route 2 below
REF_U_BAR = DPDL * DELTA ** 2 / (3.0 * MU)  # 0.1308 m/s -- derived, route 2 below
REF_U_MAX = DPDL * DELTA ** 2 / (2.0 * MU)  # 0.1962 m/s -- DIAGNOSTIC, never gated

FLOOR_REL = 1.0e-8      # LIMB A: floor-demonstration band, a-priori round-off argument
TOL_B = 0.005           # LIMB B: 0.5 % band. R1's measured L3 deficit was 0.82 % and
                        # this band GATE FAILs that run (PREREGISTRATION sec.5.2).
GCI_MAX = 0.02          # LIMB B: GCI ceiling BESIDE the P_MIN floor
P_MIN = 1.0             # LIMB B: observed-order floor (R1 used 0.05)
EXACT_REL = 1.0e-8      # round-off floor for the triple state
FS = 1.25               # Roache safety factor
RATIO = 2.0             # refinement ratio, r = 2 in BOTH directions

# ------------------------------------------------------ convergence clause -----
ITER_RES_FLOOR = 1.0e-10    # C1: final Ux INITIAL residual at or below this
PLATEAU_FRAC = 0.25         # C2: fraction of the history treated as the plateau window
PLATEAU_TOL = 1.0e-9        # C2(i): relative peak-to-peak over that window.
                            # A RANGE OF EXACTLY ZERO SATISFIES THIS. VMFL006 died on a
                            # null-range REFUSAL; the plant (PHASE 2) has already shown
                            # the reader able to see a non-zero.
PLATEAU_MIN_SAMPLES = 8     # below this the plateau test has no power and C2 abstains
NOT_DESCENDING_FACTOR = 10.0  # C2(ii): last-decile median within this factor of the
                              # first-decile median over the plateau window

# ------------------------------------------------------------ the windows ------
X_DEV_LO = 0.09             # developed window, downstream half
X_DEV_HI = L_LEN            # 0.18 m
UNIFORM_TOL = 0.05          # wall-shear peak-to-peak/mean in the window

# ------------------------------------------------------------- the plant -------
K_PLANT = 0.05              # plant magnitude as a fraction of max|channel|
PLANT_MIN_ABS = 1.0e-14
PLANT_REL_TOL = 1.0e-9      # readback agreement required, relative to the plant

# ------------------------------------------------------------- the family ------
LEVELS = ["L1", "L2", "L3"]
FAMILY = {"L1": (90, 20), "L2": (180, 40), "L3": (360, 80)}
FIELDS = ("U", "p", "wallShearStress", "Cx", "Cy")
AGE_DATUM = "0/U"
WALL_PATCH = "wall"
TAU_HIST = os.path.join("postProcessing", "tauHistory", "*", "surfaceFieldValue.dat")
UBAR_HIST = os.path.join("postProcessing", "uBarHistory", "*", "volFieldValue.dat")

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
WEAKEST = {"NOT A RESULT": 0, "GATE FAIL": 1, "GATE REACHED": 2, "PASS": 3}

FIELD_CLASSES = {
    "physics_critical": [
        "log.simpleFoam End line (EXACT name, cardinality-guarded)",
        "log.simpleFoam Time / ExecutionTime counts == endTime",
        "log.simpleFoam Ux initial-residual history",
        "system/controlDict endTime",
        "<t>/U, <t>/p, <t>/wallShearStress, <t>/Cx, <t>/Cy",
        "0/U -- the PER-LEVEL age-guard datum",
        "postProcessing tauHistory / uBarHistory -- the C2 plateau channels",
    ],
    "infrastructure": [
        "RUN_RC.<level> rc / wall_s / core_min / timeout_s",
        "COST.txt run-root roll-up",
    ],
}


class Refusal(SystemExit):
    """REFUSE (exit 2) rather than degrade. Raised, never asserted."""

    def __init__(self, msg):
        sys.stderr.write("REFUSING (exit 2): %s\n" % msg)
        SystemExit.__init__(self, 2)


# ================================================== PHASE 0 -- THE AST GUARD ====
def _ast_guard(path=None):
    """Walk THIS FILE's own source AST and REFUSE if any `assert` exists.

    Reads SOURCE, so the count is identical under python3 and python3 -O -- which is
    the whole point: -O deletes asserts from the bytecode, so a control written as an
    assert silently stops existing (L-332).
    """
    p = path or os.path.abspath(__file__)
    fh = open(p)
    try:
        src = fh.read()
    finally:
        fh.close()
    tree = ast.parse(src)
    n_assert = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))
    n_raise = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Raise))
    if n_assert != 0:
        raise Refusal("AST GUARD: %d `assert` statement(s) in %s. python3 -O deletes "
                      "them, so an assert is a control that vanishes (L-332)." % (n_assert, p))
    print("AST guard: ast.Assert count is 0 in this file (ast.Raise count %d)" % n_raise)
    return n_assert, n_raise


# ============================================ PHASE 1 -- DISCOVERY AND GUARDS ===
def one_match(pattern, what):
    """THE ONLY WAY THIS COMPARATOR OPENS A FILE.

    REFUSES on any cardinality but one. `sorted(glob.glob(p))[-1]` is banned outright:
    it sorts numeric directory names LEXICOGRAPHICALLY, so 950 beats 2000 (L-339).
    """
    hits = glob.glob(pattern)
    if len(hits) != 1:
        raise Refusal("CARDINALITY GUARD: %s -- pattern %r matched %d paths (need exactly 1)%s"
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


_TIME_DIR_RE = re.compile(r"^[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$")


def numeric_latest_time_dir(level_dir):
    """Latest numeric time directory, sorted key=float. NEVER lexicographic."""
    names = []
    for d in glob.glob(os.path.join(level_dir, "*")):
        if not os.path.isdir(d):
            continue
        b = os.path.basename(d)
        if _TIME_DIR_RE.match(b):
            names.append((float(b), b))
    if not names:
        return None, None
    names.sort(key=lambda t: t[0])
    return names[-1][1], names[-1][0]


# --------------------------------------------------------------- OF readers ----
def _patch_block(text, patch):
    i = text.find("boundaryField")
    if i < 0:
        raise Refusal("no boundaryField in the field file")
    j = text.find(patch, i)
    if j < 0:
        raise Refusal("patch %s not found in the field file" % patch)
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
    raise Refusal("unterminated patch block for %s" % patch)


_VEC_RE = re.compile(r"nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", re.S)
_SCA_RE = re.compile(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", re.S)
_INT_VEC_RE = re.compile(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", re.S)
_INT_SCA_RE = re.compile(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", re.S)


def read_patch_scalar(path, patch):
    p, txt = read_text(path, "patch scalar %s" % patch)
    m = _SCA_RE.search(_patch_block(txt, patch))
    if not m:
        raise Refusal("no nonuniform scalar list on patch %s in %s" % (patch, p))
    vals = [float(v) for v in m.group(2).split()]
    if len(vals) != int(m.group(1)):
        raise Refusal("scalar count mismatch on %s in %s" % (patch, p))
    return vals


def read_patch_vector_x(path, patch):
    p, txt = read_text(path, "patch vector %s" % patch)
    m = _VEC_RE.search(_patch_block(txt, patch))
    if not m:
        raise Refusal("no nonuniform vector list on patch %s in %s" % (patch, p))
    trip = re.findall(r"\(([^()]*)\)", m.group(2))
    if len(trip) != int(m.group(1)):
        raise Refusal("vector count mismatch on %s in %s: %d vs %d"
                      % (patch, p, len(trip), int(m.group(1))))
    return [float(t.split()[0]) for t in trip]


def read_internal_scalar(path):
    p, txt = read_text(path, "internal scalar")
    m = _INT_SCA_RE.search(txt)
    if not m:
        raise Refusal("no nonuniform internalField scalar list in %s" % p)
    return [float(v) for v in m.group(2).split()]


def read_internal_vector_x(path):
    p, txt = read_text(path, "internal vector")
    m = _INT_VEC_RE.search(txt)
    if not m:
        raise Refusal("no nonuniform internalField vector list in %s" % p)
    return [float(t.split()[0]) for t in re.findall(r"\(([^()]*)\)", m.group(2))]


# ------------------------------------------------- writers used ONLY by the plant
def _plant_patch_vector_x(path, patch, delta):
    """Add `delta` to the x-component of EVERY face value of `patch`, IN PLACE, on a
    COPY of the real solver bytes. Header, dimensions and every other patch untouched."""
    p, txt = read_text(path, "plant target patch %s" % patch)
    blk = _patch_block(txt, patch)
    m = _VEC_RE.search(blk)
    if not m:
        raise Refusal("plant: no vector list on patch %s in %s" % (patch, p))
    body = m.group(2)

    def _bump(mo):
        parts = mo.group(1).split()
        return "(%.17g %s %s)" % (float(parts[0]) + delta, parts[1], parts[2])

    newblk = blk.replace(body, re.sub(r"\(([^()]*)\)", _bump, body), 1)
    fh = open(p, "w")
    try:
        fh.write(txt.replace(blk, newblk, 1))
    finally:
        fh.close()


def _plant_internal_vector_x(path, delta):
    """Add `delta` to the x-component of EVERY internal cell value, IN PLACE, on a COPY."""
    p, txt = read_text(path, "plant target internalField")
    m = _INT_VEC_RE.search(txt)
    if not m:
        raise Refusal("plant: no internalField vector list in %s" % p)
    body = m.group(2)

    def _bump(mo):
        parts = mo.group(1).split()
        return "(%.17g %s %s)" % (float(parts[0]) + delta, parts[1], parts[2])

    fh = open(p, "w")
    try:
        fh.write(txt.replace(body, re.sub(r"\(([^()]*)\)", _bump, body), 1))
    finally:
        fh.close()


# ============================================= PHASE 5 -- THE GATE FUNCTIONALS ==
def wall_shear_window(level_dir, t):
    """LIMB A functional. (mean PHYSICAL wall shear in the developed window [Pa],
    peak-to-peak/mean, abscissae, values, face count).

    Reads the KINEMATIC x-component of wallShearStress on `wall`, takes |.| and
    multiplies by RHO. ASSUMED kinematic; if it were physical the value reads 800x
    high and limb A fails its floor by eleven orders -- a NAMED outcome, not a silent
    error (PREREGISTRATION sec.5.4).
    """
    tau_kin = read_patch_vector_x(os.path.join(level_dir, t, "wallShearStress"), WALL_PATCH)
    xs = read_patch_scalar(os.path.join(level_dir, t, "Cx"), WALL_PATCH)
    if len(xs) != len(tau_kin):
        raise Refusal("wall face count mismatch at %s/%s: Cx %d, wallShearStress %d"
                      % (level_dir, t, len(xs), len(tau_kin)))
    win = [(x, abs(tk) * RHO) for x, tk in zip(xs, tau_kin) if X_DEV_LO <= x <= X_DEV_HI]
    if len(win) < 2:
        raise Refusal("wall shear: fewer than 2 `wall` faces in the developed window "
                      "[%g, %g] m at %s/%s" % (X_DEV_LO, X_DEV_HI, level_dir, t))
    vals = [w[1] for w in win]
    mean = sum(vals) / len(vals)
    if mean <= 0.0:
        raise Refusal("wall shear: non-positive mean at %s/%s" % (level_dir, t))
    p2p = (max(vals) - min(vals)) / mean
    if p2p > UNIFORM_TOL:
        raise Refusal("wall shear is NOT developed in [%g, %g] m at %s/%s: "
                      "peak-to-peak/mean = %.6e > UNIFORM_TOL %.3g. A non-developed "
                      "flow makes the single-value gate meaningless."
                      % (X_DEV_LO, X_DEV_HI, level_dir, t, p2p, UNIFORM_TOL))
    return mean, p2p, [w[0] for w in win], vals, len(win)


def u_bar_window(level_dir, t):
    """LIMB B functional. Volume-weighted mean of U_x over cells whose centre lies in
    the developed window. The mesh is uniform, so this is the arithmetic mean of the
    developed columns and equals Q/delta per unit width."""
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"))
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"))
    if len(ux) != len(cx):
        raise Refusal("cell count mismatch at %s/%s: U %d, Cx %d" % (level_dir, t, len(ux), len(cx)))
    win = [u for u, x in zip(ux, cx) if X_DEV_LO <= x <= X_DEV_HI]
    if len(win) < 2:
        raise Refusal("u_bar: fewer than 2 cells in the developed window at %s/%s" % (level_dir, t))
    return sum(win) / len(win), len(win)


def velocity_diagnostic(level_dir, t):
    """NOT GATED. u_max at the top cell centre is PREDICTED machine-exact
    (PREREGISTRATION sec.10) -- the VMFL070 trap, which is exactly why no verdict rests
    on it. The profile error is predicted to be a CONSTANT shift K*h^2/8."""
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"))
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"))
    cy = read_internal_scalar(os.path.join(level_dir, t, "Cy"))
    if not (len(ux) == len(cx) == len(cy)):
        raise Refusal("velocity diagnostic: cell count mismatch at %s/%s" % (level_dir, t))
    xs = sorted(set(round(v, 12) for v in cx))
    if not xs:
        raise Refusal("velocity diagnostic: no cell centres at %s/%s" % (level_dir, t))
    target = 0.5 * (X_DEV_LO + X_DEV_HI)
    xt = min(xs, key=lambda v: abs(v - target))
    col = sorted([(cy[i], ux[i]) for i in range(len(ux)) if round(cx[i], 12) == xt])
    if len(col) < 2:
        raise Refusal("velocity diagnostic: column at x=%g has %d cells" % (xt, len(col)))
    h = DELTA / len(col)
    err = [u - K_CURV * (DELTA * y - 0.5 * y * y) for y, u in col]
    umax = max(u for _, u in col)
    return {
        "GATED": False,
        "x_station_m": xt,
        "n_cells": len(col),
        "h_m": h,
        "u_max_sampled": umax,
        "u_max_analytic": REF_U_MAX,
        "u_max_rel_dev": (umax - REF_U_MAX) / REF_U_MAX,
        "u_max_machine_exact": abs(umax - REF_U_MAX) / REF_U_MAX <= 1.0e-12,
        "profile_err_mean": sum(err) / len(err),
        "profile_err_predicted_Kh2_over_8": K_CURV * h * h / 8.0,
        "profile_err_spread": max(err) - min(err),
    }


# ================================== PHASE 2 -- THE PLANTED-ZERO CONTROLS ========
def planted_zero_tau(level_dir, t, writer=_plant_patch_vector_x):
    """PLANT-A. Plants a SIZED offset into the x-component of EVERY `wall` face of a
    COPY of the real solver bytes, then reads it back FROM DISK through the PRODUCTION
    reader and re-computes the FULL limb-A functional.

    `writer` is injectable for one reason only: --selftest substitutes a no-op so the
    plant never reaches disk, and checks that this control then REFUSES. A control
    never shown failing is untested.
    """
    src = os.path.join(level_dir, t, "wallShearStress")
    tau0 = read_patch_vector_x(src, WALL_PATCH)
    gate0, _, _, _, _ = wall_shear_window(level_dir, t)
    scale = max(abs(v) for v in tau0)
    plant_mag = max(K_PLANT * scale, PLANT_MIN_ABS)
    sign = -1.0 if (sum(tau0) / len(tau0)) < 0 else 1.0   # magnitude-INCREASING
    plant = sign * plant_mag

    shadow = os.path.join(level_dir, t, ".PLANTED_wallShearStress")
    orig = one_match(src, "plant source wallShearStress")
    fh = open(orig)
    try:
        raw = fh.read()
    finally:
        fh.close()
    fh = open(shadow, "w")
    try:
        fh.write(raw)
    finally:
        fh.close()
    writer(shadow, WALL_PATCH, plant)

    tau1 = read_patch_vector_x(shadow, WALL_PATCH)
    if len(tau1) != len(tau0):
        raise Refusal("PLANT-A: face count changed on the planted copy at %s" % level_dir)
    worst = max(abs((b - a) - plant) for a, b in zip(tau0, tau1))
    seen = worst <= max(abs(plant) * PLANT_REL_TOL, 1.0e-18)

    # the FULL gate functional, recomputed from the planted bytes through the reader
    tmpdir = os.path.join(level_dir, t)
    real = os.path.join(tmpdir, "wallShearStress")
    bak = os.path.join(tmpdir, ".UNPLANTED_wallShearStress")
    os.rename(real, bak)
    os.rename(shadow, real)
    try:
        gate1, _, _, _, _ = wall_shear_window(level_dir, t)
    finally:
        os.rename(real, shadow)
        os.rename(bak, real)
    os.remove(shadow)

    expected = abs(plant) * RHO
    move = gate1 - gate0
    gate_ok = abs(move - expected) <= max(abs(expected) * PLANT_REL_TOL, 1.0e-15)
    rec = {
        "channel": "PLANT-A wall shear",
        "level_dir": level_dir, "time": t, "patch": WALL_PATCH, "file": src,
        "n_faces": len(tau0), "plant_kinematic": plant, "plant_magnitude": abs(plant),
        "worst_readback_error": worst, "readback_seen": bool(seen),
        "gate_mean_unplanted_Pa": gate0, "gate_mean_planted_Pa": gate1,
        "gate_move_Pa": move, "expected_move_Pa": expected,
        "gate_move_seen": bool(gate_ok),
        "passed": bool(seen and gate_ok),
    }
    if not rec["passed"]:
        raise Refusal("PLANTED-ZERO CONTROL A FAILED at %s: readback worst error %.3e "
                      "(plant %.6e), gate moved %.6e where %.6e was planted. A zero from "
                      "a reader not shown able to see a non-zero is not evidence."
                      % (level_dir, worst, plant, move, expected))
    return rec


def planted_zero_ubar(level_dir, t, writer=_plant_internal_vector_x):
    """PLANT-B. Same discipline on the limb-B channel: the internal U field."""
    src = os.path.join(level_dir, t, "U")
    u0 = read_internal_vector_x(src)
    gate0, _ = u_bar_window(level_dir, t)
    scale = max(abs(v) for v in u0)
    plant = max(K_PLANT * scale, PLANT_MIN_ABS)

    orig = one_match(src, "plant source U")
    fh = open(orig)
    try:
        raw = fh.read()
    finally:
        fh.close()
    shadow = os.path.join(level_dir, t, ".PLANTED_U")
    fh = open(shadow, "w")
    try:
        fh.write(raw)
    finally:
        fh.close()
    writer(shadow, plant)

    u1 = read_internal_vector_x(shadow)
    if len(u1) != len(u0):
        raise Refusal("PLANT-B: cell count changed on the planted copy at %s" % level_dir)
    worst = max(abs((b - a) - plant) for a, b in zip(u0, u1))
    seen = worst <= max(abs(plant) * PLANT_REL_TOL, 1.0e-18)

    bak = os.path.join(level_dir, t, ".UNPLANTED_U")
    os.rename(src, bak)
    os.rename(shadow, src)
    try:
        gate1, _ = u_bar_window(level_dir, t)
    finally:
        os.rename(src, shadow)
        os.rename(bak, src)
    os.remove(shadow)

    move = gate1 - gate0
    gate_ok = abs(move - plant) <= max(abs(plant) * PLANT_REL_TOL, 1.0e-18)
    rec = {
        "channel": "PLANT-B mean film velocity",
        "level_dir": level_dir, "time": t, "file": src, "n_cells": len(u0),
        "plant": plant, "worst_readback_error": worst, "readback_seen": bool(seen),
        "gate_unplanted_m_s": gate0, "gate_planted_m_s": gate1,
        "gate_move_m_s": move, "expected_move_m_s": plant,
        "gate_move_seen": bool(gate_ok),
        "passed": bool(seen and gate_ok),
    }
    if not rec["passed"]:
        raise Refusal("PLANTED-ZERO CONTROL B FAILED at %s: readback worst error %.3e "
                      "(plant %.6e), gate moved %.6e where %.6e was planted."
                      % (level_dir, worst, plant, move, plant))
    return rec


# ==================================== PHASE 3 -- STRICT COMPLETION (rule 4) =====
def read_endtime(level_dir):
    p, txt = read_text(os.path.join(level_dir, "system", "controlDict"), "controlDict")
    m = re.search(r"^endTime\s+([^\s;]+);", txt, re.M)
    if not m:
        raise Refusal("no endTime in %s" % p)
    return float(m.group(1))


_UX_RE = re.compile(r"Solving for Ux,\s*Initial residual = ([0-9eE.+-]+)")


def ux_residual_history(log_text):
    return [float(v) for v in _UX_RE.findall(log_text)]


def completion(run_root, level):
    """CLAUDE.md rule 4 IN ITS ORIGINAL FORM. R2 does not terminate on residualControl,
    so `last time == endTime` is the canonical clause and R1's declared adaptation is
    WITHDRAWN. REFUSES rather than grading a partial run."""
    level_dir = os.path.join(run_root, level)
    log_path, log = read_text(os.path.join(level_dir, "log.simpleFoam"), "%s solver log" % level)

    end_lines = len(re.findall(r"^End$", log, re.M))
    if end_lines != 1:
        raise Refusal("%s: log.simpleFoam has %d `End` lines, need exactly 1 (%s)"
                      % (level, end_lines, log_path))

    times = [float(v) for v in re.findall(r"^Time = ([0-9eE.+-]+)", log, re.M)]
    if not times:
        raise Refusal("%s: no `Time = ` lines in %s" % (level, log_path))
    last_time = times[-1]
    endtime = read_endtime(level_dir)
    if abs(last_time - endtime) > 1e-9:
        raise Refusal("%s: last Time %g != endTime %g. Rule 4's canonical clause. The "
                      "run did not reach the registered iteration count -- a timeout or "
                      "a crash, and either is a FINDING." % (level, last_time, endtime))

    n_exec = len(re.findall(r"^ExecutionTime = ", log, re.M))
    if abs(n_exec - endtime) > 1e-9:
        raise Refusal("%s: %d ExecutionTime lines, endTime %g" % (level, n_exec, endtime))

    tdir, tval = numeric_latest_time_dir(level_dir)
    if tdir is None:
        raise Refusal("%s: no numeric time directory in %s" % (level, level_dir))
    if abs(tval - last_time) > 1e-9:
        raise Refusal("%s: NUMERICALLY-latest time directory %r (=%g) disagrees with the "
                      "log's last Time %g (the lexicographic-sort hazard, L-339)"
                      % (level, tdir, tval, last_time))

    for f in FIELDS:
        one_match(os.path.join(level_dir, tdir, f), "%s field %s at t=%s" % (level, f, tdir))

    # PER-LEVEL AGE GUARD. The datum is THIS LEVEL's own 0/U, touched by the launcher
    # immediately before THIS level's solver, so no field can pass it on another
    # level's clock.
    datum = one_match(os.path.join(level_dir, AGE_DATUM), "%s age-guard datum" % level)
    t_datum = os.path.getmtime(datum)
    ages = {}
    for f in FIELDS:
        fp = one_match(os.path.join(level_dir, tdir, f), "%s aged field %s" % (level, f))
        ages[f] = os.path.getmtime(fp)
        if ages[f] <= t_datum:
            raise Refusal("%s AGE GUARD: %s at t=%s (mtime %.3f) is NOT newer than this "
                          "level's own %s (mtime %.3f). The answer predates the run "
                          "allowed to produce it." % (level, f, tdir, ages[f], AGE_DATUM, t_datum))

    # INFRASTRUCTURE (L-342): absent -> NOT MEASURED and the grade PROCEEDS; present
    # and non-zero -> REFUSE. Bookkeeping never voids physics.
    rc, rc_status, rc_src, wall_s, core_min = None, "NOT MEASURED", None, None, None
    hits = glob.glob(os.path.join(run_root, "RUN_RC.%s" % level))
    if len(hits) == 1:
        rc_src = hits[0]
        fh = open(rc_src, errors="replace")
        try:
            body = fh.read()
        finally:
            fh.close()
        m = re.search(r"^rc = (\S+)", body, re.M)
        if m:
            rc, rc_status = int(m.group(1)), "MEASURED"
            if rc != 0:
                raise Refusal("%s: recorded rc = %d in %s. A non-zero rc is a FINDING, "
                              "not a retry; 124 means the running-total cap stopped it."
                              % (level, rc, rc_src))
        for key, cast in (("wall_s", float), ("core_min", float)):
            mm = re.search(r"^%s = (\S+)" % key, body, re.M)
            if mm:
                if key == "wall_s":
                    wall_s = cast(mm.group(1))
                else:
                    core_min = cast(mm.group(1))

    return {
        "level": level, "level_dir": level_dir, "log": log_path,
        "state": "COMPLETE", "end_lines": end_lines, "last_time": last_time,
        "endTime": endtime, "n_exec": n_exec, "time_dir": tdir,
        "numeric_latest_time_dir": tdir, "age_guard": "all %d fields at %s newer than this level's own %s"
                                                     % (len(FIELDS), tdir, AGE_DATUM),
        "rc": rc, "rc_status": rc_status, "rc_source": rc_src,
        "wall_s": wall_s, "core_min": core_min,
        "ux_residuals_n": len(ux_residual_history(log)),
        "ux_final_initial_residual": (ux_residual_history(log) or [None])[-1],
    }


# ============================== PHASE 4 -- THE CONVERGENCE DISJUNCTION ==========
def read_history(level_dir, pattern, what):
    """(times, x-components) from a fieldValue .dat. Vector rows read as `(x y z)`."""
    p = one_match(os.path.join(level_dir, pattern), what)
    fh = open(p, errors="replace")
    try:
        lines = fh.read().splitlines()
    finally:
        fh.close()
    ts, vs = [], []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split(None, 1)
        if len(parts) != 2:
            continue
        m = re.search(r"\(([^()]*)\)", parts[1])
        val = float(m.group(1).split()[0]) if m else float(parts[1])
        ts.append(float(parts[0]))
        vs.append(val)
    if not ts:
        raise Refusal("history channel %s at %s carries no samples" % (what, p))
    return p, ts, vs


def _rel_p2p(vals):
    """Relative peak-to-peak. A range of EXACTLY ZERO returns 0.0 and is a PASS -- it is
    what full convergence looks like, not an instrument failure (VMFL006's null-range
    refusal is the failure this returns against)."""
    mean = sum(vals) / len(vals)
    rng = max(vals) - min(vals)
    if mean == 0.0:
        return rng
    return rng / abs(mean)


def _median(xs):
    ys = sorted(xs)
    n = len(ys)
    return ys[n // 2] if n % 2 else 0.5 * (ys[n // 2 - 1] + ys[n // 2])


def convergence(level_dir, comp):
    """THE DISJUNCTION of PREREGISTRATION sec.6.2. ACCEPT on C1 OR C2.

    C1 DESCENDED        : final Ux initial residual <= ITER_RES_FLOOR.
    C2 FLOORED AND FLAT : over the last PLATEAU_FRAC of history, (i) both channels'
                          relative p2p <= PLATEAU_TOL -- A NULL RANGE SATISFIES THIS --
                          and (ii) the Ux residual is no longer descending.

    THE SATISFIABILITY ARGUMENT, which is why VMFL006's failure cannot recur: C1 and C2
    are ALTERNATIVES, never conjuncts. VMFL006 demanded a residual floor AND a non-null
    range, and machine convergence makes those two jointly unsatisfiable. Here a
    descending run satisfies C1, a floored-and-flat run satisfies C2, and only a run
    that is BOTH above the floor AND still moving fails -- which is precisely rule 5
    limb (1) doing its job.
    """
    _, log = read_text(os.path.join(level_dir, "log.simpleFoam"), "solver log for convergence")
    res = ux_residual_history(log)
    if not res:
        raise Refusal("no `Solving for Ux` lines in %s/log.simpleFoam -- the convergence "
                      "clause has nothing to read" % level_dir)
    final = res[-1]
    c1 = final <= ITER_RES_FLOOR

    tau_p, tau_t, tau_v = read_history(level_dir, TAU_HIST, "tauHistory")
    ub_p, ub_t, ub_v = read_history(level_dir, UBAR_HIST, "uBarHistory")
    out = {
        "C1_final_ux_initial_residual": final,
        "C1_floor": ITER_RES_FLOOR,
        "C1_DESCENDED": bool(c1),
        "tau_history_file": tau_p, "tau_history_n": len(tau_v),
        "ubar_history_file": ub_p, "ubar_history_n": len(ub_v),
    }

    def _tail(xs):
        k = max(PLATEAU_MIN_SAMPLES, int(math.ceil(PLATEAU_FRAC * len(xs))))
        return xs[-k:] if len(xs) >= k else xs

    tau_w_tail, ub_tail, res_tail = _tail(tau_v), _tail(ub_v), _tail(res)
    enough = (len(tau_v) >= PLATEAU_MIN_SAMPLES and len(ub_v) >= PLATEAU_MIN_SAMPLES
              and len(res) >= PLATEAU_MIN_SAMPLES)
    tau_flat = _rel_p2p(tau_w_tail)
    ub_flat = _rel_p2p(ub_tail)
    d = max(1, len(res_tail) // 10)
    first_dec, last_dec = _median(res_tail[:d]), _median(res_tail[-d:])
    not_descending = (first_dec == 0.0 and last_dec == 0.0) or (
        last_dec > 0.0 and first_dec > 0.0
        and (first_dec / last_dec) <= NOT_DESCENDING_FACTOR
        and (last_dec / first_dec) <= NOT_DESCENDING_FACTOR)
    c2 = bool(enough and tau_flat <= PLATEAU_TOL and ub_flat <= PLATEAU_TOL and not_descending)

    out.update({
        "plateau_frac": PLATEAU_FRAC, "plateau_tol": PLATEAU_TOL,
        "plateau_samples_tau": len(tau_w_tail), "plateau_samples_ubar": len(ub_tail),
        "C2_tau_rel_p2p": tau_flat, "C2_ubar_rel_p2p": ub_flat,
        "C2_tau_range_is_null": (max(tau_w_tail) - min(tau_w_tail)) == 0.0,
        "C2_ubar_range_is_null": (max(ub_tail) - min(ub_tail)) == 0.0,
        "C2_residual_first_decile_median": first_dec,
        "C2_residual_last_decile_median": last_dec,
        "C2_not_descending": bool(not_descending),
        "C2_enough_samples": bool(enough),
        "C2_FLOORED_AND_FLAT": c2,
        "ACCEPTED": bool(c1 or c2),
        "limb_satisfied": "C1" if c1 else ("C2" if c2 else "NEITHER"),
    })
    if not out["ACCEPTED"]:
        raise Refusal(
            "%s IS NOT ITERATIVELY CONVERGED (rule 5 limb (1), one-way). C1: final Ux "
            "initial residual %.6e > floor %.3g. C2: tau rel-p2p %.3e, u_bar rel-p2p "
            "%.3e over the last %d samples (tol %.3g), residual %s. The run was still "
            "moving at endTime." % (level_dir, final, ITER_RES_FLOOR, tau_flat, ub_flat,
                                    len(tau_w_tail), PLATEAU_TOL,
                                    "still descending" if not not_descending else "floored"))
    return out


# ================================== PHASE 6 -- THE TRIPLE AND THE VERDICTS ======
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 COARSE, f2 MEDIUM, f3 FINE. Rule 5's classifier.

    NO GCI IS RETURNED IN ANY NON-CONVERGING STATE. Never quote a GCI when the three
    values are not monotone.
    """
    d21, d32 = f2 - f1, f3 - f2
    floor = EXACT_REL * abs(f3)
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "d21": d21, "d32": d32,
           "ratio": r, "fs": fs, "roundoff_floor": floor,
           "p": None, "gci_fine": None, "R": None, "f_extrapolated": None}
    if abs(d21) <= floor and abs(d32) <= floor:
        out["state"] = "EXACT"
        return out
    if d21 == 0.0 or d32 == 0.0:
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
        out["p_below_P_MIN"] = True
        return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


def derive_reference():
    """BOTH gate values, derived in double precision by TWO INDEPENDENT ROUTES each.
    Never transcribed from a table, an archive or a figure."""
    sin_b = math.sin(math.radians(BETA_DEG))
    l_head = DELTA_P / (RHO * G_GRAV * sin_b)          # 0.18 m
    dpdl_p = DELTA_P / L_LEN                            # 3924 Pa/m, pressure route
    dpdl_h = RHO * G_GRAV * sin_b                       # 3924 Pa/m, head route
    umax = dpdl_p * DELTA ** 2 / (2.0 * MU)
    tau1 = MU * 2.0 * umax / DELTA                      # route 1: mu*2*u_max/delta
    tau2 = dpdl_p * DELTA                               # route 2: (dp/L)*delta
    ubar1 = (2.0 / 3.0) * umax                          # route 1: (2/3) u_max
    ubar2 = dpdl_p * DELTA ** 2 / (3.0 * MU)            # route 2: (dp/L) delta^2/(3 mu)
    if abs(tau1 - tau2) > 1e-9:
        raise Refusal("tau_w derivation routes disagree: %.17g vs %.17g" % (tau1, tau2))
    if abs(ubar1 - ubar2) > 1e-12:
        raise Refusal("u_bar derivation routes disagree: %.17g vs %.17g" % (ubar1, ubar2))
    if abs(REF_TAU_W - tau2) > 1e-9 or abs(REF_U_BAR - ubar2) > 1e-12:
        raise Refusal("frozen constants disagree with the derivation")
    return {
        "sin_beta": sin_b, "L_self_consistent_m": l_head,
        "dpdl_pressure": dpdl_p, "dpdl_head": dpdl_h,
        "u_max": umax, "u_bar": ubar2, "ref_tau_w_Pa": tau2,
        "tau_route1_mu2umax_over_delta": tau1, "tau_route2_dpdl_times_delta": tau2,
        "ubar_route1_two_thirds_umax": ubar1, "ubar_route2_dpdl_delta2_over_3mu": ubar2,
        "manual_units_error_factor": 18.0 / L_LEN,
        "umax_if_printed_taken_absolute": (DELTA_P / 18.0) * 1.0 ** 2 / (2.0 * MU),
        "K_curvature": K_CURV,
        "predicted_ubar_discrete": {lvl: REF_U_BAR + K_CURV * (DELTA / ny) ** 2 / 6.0
                                    for lvl, (_, ny) in sorted(FAMILY.items())},
    }


def verdict_limb_a(tau_by_level):
    """LIMB A -- the FLOOR DEMONSTRATION. No triple; sec.2f.3's cap does not reach it
    (sec.2h.2), and sec.2h.4's five conditions are declared in the frozen registration.
    The claim is bounded by the levels actually run (condition 5)."""
    devs = {lvl: (v - REF_TAU_W) / REF_TAU_W for lvl, v in sorted(tau_by_level.items())}
    worst = max(abs(d) for d in devs.values())
    vals = list(tau_by_level.values())
    invar = (max(vals) - min(vals)) / REF_TAU_W if len(vals) > 1 else 0.0
    inside = worst <= FLOOR_REL and invar <= FLOOR_REL
    return {
        "limb": "A", "quantity": "tau_w, physical wall shear stress, Pa",
        "class": "FLOOR DEMONSTRATION (VERIFICATION sec.2h.4) -- NOT a continuum claim",
        "ceiling": "PASS",
        "sentence": ("the discretisation error in the wall shear stress is below %.3g "
                     "relative at %s cells" % (FLOOR_REL,
                                               ", ".join(str(FAMILY[l][0] * FAMILY[l][1])
                                                         for l in sorted(tau_by_level)))),
        "reference_Pa": REF_TAU_W, "floor_rel": FLOOR_REL,
        "tau_w_Pa": dict(sorted(tau_by_level.items())),
        "rel_dev_by_level": devs, "worst_rel_dev": worst,
        "mesh_invariance_rel": invar, "inside": bool(inside),
        "verdict": "PASS" if inside else "GATE FAIL",
        "why": ("every level within the floor and the levels mutually invariant"
                if inside else
                "worst level deviation %.6e and/or mesh invariance %.6e exceeds the "
                "registered floor %.3g" % (worst, invar, FLOOR_REL)),
    }


def verdict_limb_b(tri, ubar_by_level):
    """LIMB B -- the Roache triple on u_bar. Rule 5 step 3, and the gate may only turn a
    would-be PASS into NOT A RESULT, never the reverse."""
    f3 = ubar_by_level[LEVELS[-1]]
    dev = (f3 - REF_U_BAR) / REF_U_BAR
    inside = abs(dev) <= TOL_B
    out = {
        "limb": "B", "quantity": "u_bar, mean film velocity in the developed window, m/s",
        "class": "CONTINUUM with a Roache triple -- ANSYS sec.11.1 -> rule 5 step 3",
        "ceiling": "PASS",
        "reference_m_s": REF_U_BAR, "band": TOL_B, "gci_max": GCI_MAX, "p_min": P_MIN,
        "u_bar_m_s": dict(sorted(ubar_by_level.items())),
        "finest_m_s": f3, "deviation_rel": dev, "inside": bool(inside),
    }
    st = tri["state"]
    if st != "CONVERGING":
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("grid triple is %s, not CONVERGING (CLAUDE.md rule 5 limb 2) -- "
                      "NOT A RESULT whatever the value. No GCI is quoted." % st)
        return out
    if tri["p"] is None or tri["p"] < P_MIN:
        out["verdict"] = "NOT A RESULT"
        out["why"] = "observed order p = %s below the registered floor P_MIN = %.3g" % (tri["p"], P_MIN)
        return out
    if tri["gci_fine"] is not None and tri["gci_fine"] > GCI_MAX:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("fine-grid GCI %.6e exceeds the registered ceiling GCI_MAX %.3g: the "
                      "discretisation uncertainty is larger than the band it must sit "
                      "inside, so a PASS cannot be certified" % (tri["gci_fine"], GCI_MAX))
        return out
    out["verdict"] = "PASS" if inside else "GATE FAIL"
    out["why"] = ("CONVERGING triple, p = %.6f, GCI %.6e <= %.3g, finest level %s the "
                  "%.3g band" % (tri["p"], tri["gci_fine"], GCI_MAX,
                                 "inside" if inside else "OUTSIDE", TOL_B))
    return out


# ------------------------------------------------------------------ the run ----
def grade(run_root, out_json=None, levels=None):
    levels = levels or LEVELS
    rec = {
        "case": "VMFL038-R2", "title": "Falling Film Over an Inclined Plane",
        "manual_page": "131-132", "run_root": run_root,
        "graded_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "supersedes": "VMFL038-R1 as a PLAN. R1's register row #47 NOT A RESULT stands.",
        "reference": {
            "kind": "EXACT SOLUTION OF THE SAME CONTINUUM MODEL",
            "source": "Bird, Stewart & Lightfoot, Transport Phenomena, p.45, 2005 "
                      "(VM2026R1 p.131 Reference)",
            "tau_w_Pa": REF_TAU_W, "u_bar_m_s": REF_U_BAR, "u_max_m_s": REF_U_MAX,
        },
        "rho": RHO, "mu": MU, "nu": NU, "family": {k: {"nx": v[0], "ny": v[1], "cells": v[0] * v[1],
                                                       "dx_over_dy": (L_LEN / v[0]) / (DELTA / v[1])}
                                                   for k, v in sorted(FAMILY.items())},
        "developed_window_m": [X_DEV_LO, X_DEV_HI],
        "band_limb_b": TOL_B, "floor_limb_a": FLOOR_REL, "gci_max": GCI_MAX, "p_min": P_MIN,
        "field_classes": FIELD_CLASSES,
        "phase_order": ["0 AST guard", "1 discovery", "2 PLANTED ZERO (both channels, all levels)",
                        "3 completion", "4 convergence", "5 functionals", "6 triple and verdict"],
        "phases_executed": [],
        "levels": {}, "planted_zero": [],
    }

    # ---- PHASE 0
    n_assert, n_raise = _ast_guard()
    rec["ast_assert_count"] = n_assert
    rec["ast_raise_count"] = n_raise
    rec["phases_executed"].append("0 AST guard")

    rec["derivation"] = derive_reference()

    # ---- PHASE 1: discovery ONLY. No physics clause runs here.
    disco = {}
    for lvl in levels:
        ld = os.path.join(run_root, lvl)
        if not os.path.isdir(ld):
            raise Refusal("level directory %s does not exist" % ld)
        tdir, tval = numeric_latest_time_dir(ld)
        if tdir is None:
            raise Refusal("no numeric time directory under %s" % ld)
        disco[lvl] = (ld, tdir, tval)
    rec["discovery"] = {k: {"level_dir": v[0], "numeric_latest_time_dir": v[1]} for k, v in sorted(disco.items())}
    rec["phases_executed"].append("1 discovery")

    # ---- PHASE 2: THE PLANTS, BOTH CHANNELS, EVERY LEVEL, BEFORE ANY OTHER CLAUSE.
    for lvl in levels:
        ld, tdir, _ = disco[lvl]
        rec["planted_zero"].append(planted_zero_tau(ld, tdir))
        rec["planted_zero"].append(planted_zero_ubar(ld, tdir))
    if len(rec["planted_zero"]) != 2 * len(levels):
        raise Refusal("PLANT ORDERING: expected %d plant records before any other clause, "
                      "got %d" % (2 * len(levels), len(rec["planted_zero"])))
    rec["phases_executed"].append("2 PLANTED ZERO (both channels, all levels)")

    # ---- PHASES 3-5
    tau_by, ubar_by = {}, {}
    for lvl in levels:
        ld, tdir, _ = disco[lvl]
        comp = completion(run_root, lvl)
        comp["convergence"] = convergence(ld, comp)
        tau_mean, p2p, xw, vals, nfaces = wall_shear_window(ld, tdir)
        ub, ncells = u_bar_window(ld, tdir)
        comp["wall_shear"] = {"mean_phys_Pa": tau_mean, "p2p_rel": p2p, "n_faces": nfaces,
                              "x_window": xw, "tau_phys_window": vals}
        comp["u_bar"] = {"value_m_s": ub, "n_cells_in_window": ncells,
                         "predicted_m_s": REF_U_BAR + K_CURV * (DELTA / FAMILY[lvl][1]) ** 2 / 6.0}
        comp["velocity_diagnostic"] = velocity_diagnostic(ld, tdir)
        tau_by[lvl] = tau_mean
        ubar_by[lvl] = ub
        rec["levels"][lvl] = comp
    rec["phases_executed"].append("3 completion")
    rec["phases_executed"].append("4 convergence")
    rec["phases_executed"].append("5 functionals")

    # ---- PHASE 6
    tri = roache(ubar_by[LEVELS[0]], ubar_by[LEVELS[1]], ubar_by[LEVELS[2]])
    rec["triple_limb_b"] = tri
    rec["limb_A"] = verdict_limb_a(tau_by)
    rec["limb_B"] = verdict_limb_b(tri, ubar_by)
    rec["verdict"] = min([rec["limb_A"]["verdict"], rec["limb_B"]["verdict"]], key=lambda v: WEAKEST[v])
    rec["verdict_rule"] = "the ROW verdict is the WEAKEST limb verdict"
    rec["phases_executed"].append("6 triple and verdict")

    cost = glob.glob(os.path.join(run_root, "COST.txt"))
    if len(cost) == 1:
        fh = open(cost[0], errors="replace")
        try:
            rec["cost_txt"] = fh.read()
        finally:
            fh.close()
    else:
        rec["cost_txt"] = "NOT MEASURED -- COST.txt absent (L-342 INFRASTRUCTURE)"

    if out_json is None:
        out_json = os.path.join(run_root, "GRADING_RECORD_%s.json"
                                % datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H%MZ"))
    fh = open(out_json, "w")
    try:
        json.dump(rec, fh, indent=2, sort_keys=True, default=str)
    finally:
        fh.close()
    rec["grading_record_path"] = out_json

    print("")
    print("VMFL038-R2  Falling Film Over an Inclined Plane  (manual p.131-132)")
    print("  LIMB A  tau_w  ref %.17g Pa   floor %.3g" % (REF_TAU_W, FLOOR_REL))
    for lvl in levels:
        print("     %s  %.17g Pa   rel dev %+.6e" % (lvl, tau_by[lvl], rec["limb_A"]["rel_dev_by_level"][lvl]))
    print("     mesh invariance %.6e   VERDICT %s" % (rec["limb_A"]["mesh_invariance_rel"], rec["limb_A"]["verdict"]))
    print("  LIMB B  u_bar  ref %.17g m/s  band %.3g" % (REF_U_BAR, TOL_B))
    for lvl in levels:
        print("     %s  %.17g m/s  predicted %.17g" % (lvl, ubar_by[lvl], rec["levels"][lvl]["u_bar"]["predicted_m_s"]))
    print("     triple %s  R %s  p %s  GCI %s" % (tri["state"], tri["R"], tri["p"], tri["gci_fine"]))
    print("     finest rel dev %+.6e   VERDICT %s" % (rec["limb_B"]["deviation_rel"], rec["limb_B"]["verdict"]))
    print("  ROW VERDICT: %s" % rec["verdict"])
    print("  JSON grading record: %s" % out_json)
    return rec


# ============================================================== --verify-frozen =
def verify_frozen():
    """Re-hash this file and the pre-registration against their HEAD blobs at GRADE
    time. Asserted against `git rev-parse HEAD:<path>`, NEVER against `git status` or
    `git diff HEAD` (ANSYS sec.11.5)."""
    rels = ["cases/ansys_verification/VMFL038-R2/PREREGISTRATION.md",
            "cases/ansys_verification/VMFL038-R2/grade_vmfl038r2.py",
            "cases/ansys_verification/VMFL038-R2/make_mesh_vmfl038r2.py"]
    repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if not repo:
        raise Refusal("--verify-frozen: not inside a git repository")
    bad = 0
    for rel in rels:
        head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD:%s" % rel],
                              capture_output=True, text=True).stdout.strip()
        disk = subprocess.run(["git", "-C", repo, "hash-object", os.path.join(repo, rel)],
                              capture_output=True, text=True).stdout.strip()
        ok = bool(head) and head == disk
        print("%s  %s  head=%s disk=%s" % ("OK  " if ok else "MISMATCH", rel, head or "ABSENT", disk or "ABSENT"))
        if not ok:
            bad += 1
    if bad:
        raise Refusal("--verify-frozen: %d file(s) on disk differ from their HEAD blobs. "
                      "The file that would grade is not the file that was frozen." % bad)
    return 0


def sha256_file(path):
    h = hashlib.sha256()
    fh = open(path, "rb")
    try:
        h.update(fh.read())
    finally:
        fh.close()
    return h.hexdigest()


# ==================================================================== SELFTEST ==
_RESULTS = []


def ck(name, ok):
    _RESULTS.append(bool(ok))
    print("  [%s] %s" % ("PASS" if ok else "FAIL", name))


def _refuses(name, fn, *a, **k):
    try:
        fn(*a, **k)
    except SystemExit as exc:
        ck(name + "  [REFUSED rc=%s]" % getattr(exc, "code", "?"), True)
        return
    except Exception as exc:  # noqa: BLE001 - a refusal must not be a stray traceback
        ck(name + "  [raised %s, expected a Refusal]" % type(exc).__name__, False)
        return
    ck(name + "  [DID NOT REFUSE]", False)


# ------------------------------------------------------ synthetic level bytes ---
_HDR = ("FoamFile { version 2.0; format ascii; class %s; location \"%s\"; object %s; }\n"
        "dimensions [0 0 0 0 0 0 0];\n")


def _wss_bytes(xs, tau_kin, loc):
    body = "\n".join("(%.17g 0 0)" % t for t in tau_kin)
    return (_HDR % ("volVectorField", loc, "wallShearStress") +
            "internalField uniform (0 0 0);\nboundaryField\n{\n"
            "    inlet { type calculated; value uniform (0 0 0); }\n"
            "    wall\n    {\n        type calculated;\n"
            "        value nonuniform List<vector> \n%d\n(\n%s\n)\n;\n    }\n"
            "    freeSurface { type symmetryPlane; }\n}\n" % (len(tau_kin), body))


def _cx_bytes(cx_int, cx_wall, obj, loc):
    ib = "\n".join("%.17g" % v for v in cx_int)
    wb = "\n".join("%.17g" % v for v in cx_wall)
    return (_HDR % ("volScalarField", loc, obj) +
            "internalField nonuniform List<scalar> \n%d\n(\n%s\n)\n;\nboundaryField\n{\n"
            "    inlet { type calculated; value uniform 0; }\n"
            "    wall\n    {\n        type calculated;\n"
            "        value nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n    }\n}\n"
            % (len(cx_int), ib, len(cx_wall), wb))


def _u_bytes(ux, loc):
    body = "\n".join("(%.17g 0 0)" % v for v in ux)
    return (_HDR % ("volVectorField", loc, "U") +
            "internalField nonuniform List<vector> \n%d\n(\n%s\n)\n;\nboundaryField\n{\n"
            "    inlet { type zeroGradient; }\n    wall { type noSlip; }\n}\n" % (len(ux), body))


def _write_level(root, level, tau_phys, ubar, endtime=8000, nx=6, ny=5,
                 ux_res_tail=1e-13, hist_flat=True, hist_null=False, still_descending=False,
                 write_end=True, exec_lines=None, uniform=True, rc=0, n_hist=40):
    """Write a synthetic level whose bytes the PRODUCTION readers parse."""
    ld = os.path.join(root, level)
    t = str(endtime)
    os.makedirs(os.path.join(ld, t), exist_ok=True)
    os.makedirs(os.path.join(ld, "0"), exist_ok=True)
    os.makedirs(os.path.join(ld, "system"), exist_ok=True)
    for sub in ("tauHistory", "uBarHistory"):
        os.makedirs(os.path.join(ld, "postProcessing", sub, "0"), exist_ok=True)

    fh = open(os.path.join(ld, "0", "U"), "w")
    try:
        fh.write(_u_bytes([0.0] * (nx * ny), "0"))
    finally:
        fh.close()
    fh = open(os.path.join(ld, "system", "controlDict"), "w")
    try:
        fh.write("application simpleFoam;\nendTime         %d;\n" % endtime)
    finally:
        fh.close()

    # wall faces span the full plate; half of them land in the developed window
    xw = [L_LEN * (i + 0.5) / nx for i in range(nx)]
    tau_kin = [(tau_phys / RHO) * (1.0 + (3.0 * UNIFORM_TOL * i if not uniform else 0.0))
               for i in range(nx)]
    tau_kin = [-abs(v) for v in tau_kin]
    cx_int = [L_LEN * (i + 0.5) / nx for i in range(nx) for _ in range(ny)]
    cy_int = [DELTA * (j + 0.5) / ny for _ in range(nx) for j in range(ny)]
    # a velocity field whose window mean is exactly `ubar`
    par = [K_CURV * (DELTA * y - 0.5 * y * y) for y in cy_int]
    inwin = [i for i, x in enumerate(cx_int) if X_DEV_LO <= x <= X_DEV_HI]
    mean_par = sum(par[i] for i in inwin) / len(inwin)
    ux = [v + (ubar - mean_par) for v in par]

    for name, data in (("wallShearStress", _wss_bytes(xw, tau_kin, t)),
                       ("U", _u_bytes(ux, t)),
                       ("p", _cx_bytes([0.0] * (nx * ny), [0.0] * nx, "p", t)),
                       ("Cx", _cx_bytes(cx_int, xw, "Cx", t)),
                       ("Cy", _cx_bytes(cy_int, [0.0] * nx, "Cy", t))):
        fh = open(os.path.join(ld, t, name), "w")
        try:
            fh.write(data)
        finally:
            fh.close()
        os.utime(os.path.join(ld, t, name), (2e9, 2e9))          # NEWER than the datum
    os.utime(os.path.join(ld, "0", "U"), (1e9, 1e9))             # the age-guard datum

    lines = []
    n = exec_lines if exec_lines is not None else endtime
    for i in range(1, n + 1):
        if still_descending:
            r = 1.0 * (10.0 ** (-6.0 * i / max(1, n)))
        else:
            r = max(ux_res_tail, 1.0 * (10.0 ** (-14.0 * i / max(1, n))))
        lines.append("Time = %d\n" % i)
        lines.append("smoothSolver:  Solving for Ux, Initial residual = %.11e, Final residual = 0, No Iterations 1\n" % r)
        lines.append("ExecutionTime = %.2f s  ClockTime = 1 s\n" % (0.01 * i))
    if write_end:
        lines.append("End\n")
    fh = open(os.path.join(ld, "log.simpleFoam"), "w")
    try:
        fh.write("".join(lines))
    finally:
        fh.close()

    for sub, fn, val in (("tauHistory", "surfaceFieldValue.dat", -tau_phys / RHO),
                         ("uBarHistory", "volFieldValue.dat", ubar)):
        rows = ["# synthetic\n", "# Time\tvalue\n"]
        for i in range(n_hist):
            if hist_null:
                v = val
            elif hist_flat:
                v = val * (1.0 + (1e-12 if i % 2 else -1e-12))
            else:
                v = val * (1.0 + 1e-3 * (n_hist - i) / n_hist)
            rows.append("%d\t(%.17g 0 0)\n" % (100 * (i + 1), v))
        fh = open(os.path.join(ld, "postProcessing", sub, "0", fn), "w")
        try:
            fh.write("".join(rows))
        finally:
            fh.close()

    fh = open(os.path.join(root, "RUN_RC.%s" % level), "w")
    try:
        fh.write("rc = %d\nlevel = %s\nwall_s = 10\nranks = 1\ncore_min = 0.1667\n" % (rc, level))
    finally:
        fh.close()
    return ld


def _make_run(root, taus, ubars, **kw):
    os.makedirs(root, exist_ok=True)
    for lvl, tau, ub in zip(LEVELS, taus, ubars):
        _write_level(root, lvl, tau, ub, **kw)
    fh = open(os.path.join(root, "COST.txt"), "w")
    try:
        fh.write("total_core_min = 0.5\ncap_core_min = 90\n")
    finally:
        fh.close()
    return root


def selftest():
    import tempfile
    del _RESULTS[:]
    print("VMFL038-R2 comparator --selftest")
    print("interpreter optimisation level: __debug__ = %s" % __debug__)

    # ---- PHASE 0 control
    n_assert, n_raise = _ast_guard()
    ck("AST guard finds ZERO asserts in this file (raises: %d)" % n_raise, n_assert == 0)
    tmp = tempfile.mkdtemp(prefix="vmfl038r2_")

    bad = os.path.join(tmp, "has_assert.py")
    fh = open(bad, "w")
    try:
        fh.write("def f(x):\n    assert x\n")
    finally:
        fh.close()
    _refuses("AST guard REFUSES a file that DOES contain an assert", _ast_guard, bad)

    # ---- the derivation, two routes each
    d = derive_reference()
    ck("tau_w derived two ways agree: %.17g / %.17g" % (d["tau_route1_mu2umax_over_delta"], d["tau_route2_dpdl_times_delta"]),
       abs(d["tau_route1_mu2umax_over_delta"] - d["tau_route2_dpdl_times_delta"]) < 1e-9)
    ck("u_bar derived two ways agree: %.17g / %.17g" % (d["ubar_route1_two_thirds_umax"], d["ubar_route2_dpdl_delta2_over_3mu"]),
       abs(d["ubar_route1_two_thirds_umax"] - d["ubar_route2_dpdl_delta2_over_3mu"]) < 1e-12)
    ck("the manual's printed geometry is 100x out: factor %.14g" % d["manual_units_error_factor"],
       abs(d["manual_units_error_factor"] - 100.0) < 1e-9)
    ck("derived L = %.17g m reproduces the printed 0.18" % d["L_self_consistent_m"],
       abs(d["L_self_consistent_m"] - L_LEN) < 1e-12)

    # ---- cardinality guard
    ck("one_match returns the single hit", os.path.basename(one_match(bad, "the assert file")) == "has_assert.py")
    _refuses("one_match REFUSES on zero matches", one_match, os.path.join(tmp, "nope_*"), "nothing")
    for nm in ("dup_a", "dup_b"):
        fh = open(os.path.join(tmp, nm), "w")
        try:
            fh.write("x")
        finally:
            fh.close()
    _refuses("one_match REFUSES on two matches", one_match, os.path.join(tmp, "dup_*"), "two files")

    # ---- NUMERIC time-directory selection
    tdroot = os.path.join(tmp, "tdirs")
    for nm in ("0", "950", "2000", "32000"):
        os.makedirs(os.path.join(tdroot, nm), exist_ok=True)
    got, gotv = numeric_latest_time_dir(tdroot)
    lex = sorted(os.listdir(tdroot))[-1]
    ck("time dirs sort NUMERICALLY: got %r (lexicographic would give %r)" % (got, lex),
       got == "32000" and lex == "950")

    # ---- END-TO-END ARM 1: PASS on both limbs.
    # u_bar values are the frozen sec.10 point predictions themselves.
    pred = [REF_U_BAR + K_CURV * (DELTA / FAMILY[l][1]) ** 2 / 6.0 for l in LEVELS]
    r1 = _make_run(os.path.join(tmp, "run_pass"), [REF_TAU_W] * 3, pred)
    rec = grade(r1, out_json=os.path.join(tmp, "pass.json"))
    ck("ARM PASS: limb A PASS (floor demonstration)", rec["limb_A"]["verdict"] == "PASS")
    ck("ARM PASS: limb B PASS, triple %s p=%.6f GCI=%.3e"
       % (rec["triple_limb_b"]["state"], rec["triple_limb_b"]["p"], rec["triple_limb_b"]["gci_fine"]),
       rec["limb_B"]["verdict"] == "PASS")
    ck("ARM PASS: observed order is 2.000000 as sec.10 predicts", abs(rec["triple_limb_b"]["p"] - 2.0) < 1e-9)
    ck("ARM PASS: ROW verdict PASS", rec["verdict"] == "PASS")
    ck("PLANT-A fired at ALL THREE levels", len([p for p in rec["planted_zero"] if p["channel"].startswith("PLANT-A")]) == 3)
    ck("PLANT-B fired at ALL THREE levels", len([p for p in rec["planted_zero"] if p["channel"].startswith("PLANT-B")]) == 3)
    ck("every plant record passed", all(p["passed"] for p in rec["planted_zero"]))
    ck("C1 DESCENDED accepted at every level",
       all(rec["levels"][l]["convergence"]["limb_satisfied"] == "C1" for l in LEVELS))
    ck("JSON grading record written and re-readable", os.path.exists(rec["grading_record_path"])
       and json.load(open(rec["grading_record_path"]))["verdict"] == "PASS")
    ck("JSON grading record carries all six plant records",
       len(json.load(open(rec["grading_record_path"]))["planted_zero"]) == 6)
    ck("velocity diagnostic is REPORTED and NOT GATED",
       rec["levels"]["L1"]["velocity_diagnostic"]["GATED"] is False)

    # ---- ARM 2: GATE FAIL on limb B -- CONVERGING but outside the band.
    off = REF_U_BAR * (1.0 + 0.02)
    r2 = _make_run(os.path.join(tmp, "run_gatefail"), [REF_TAU_W] * 3,
                   [off + 4.0 * 1e-4, off + 1e-4, off + 0.25e-4])
    rec2 = grade(r2, out_json=os.path.join(tmp, "gf.json"))
    ck("GATE FAIL: CONVERGING but the value is OUTSIDE the band -- verdict %s, triple %s"
       % (rec2["limb_B"]["verdict"], rec2["triple_limb_b"]["state"]),
       rec2["limb_B"]["verdict"] == "GATE FAIL" and rec2["triple_limb_b"]["state"] == "CONVERGING")
    ck("ROW verdict follows the WEAKEST limb (GATE FAIL beats PASS)", rec2["verdict"] == "GATE FAIL")

    # ---- ARM 3: EXACT triple -- NOT A RESULT even though the value is perfect.
    #      THIS IS THE ARM THAT PROVES WHY THE TRIPLE IS NOT ON tau_w.
    r3 = _make_run(os.path.join(tmp, "run_exact"), [REF_TAU_W] * 3, [REF_U_BAR] * 3)
    rec3 = grade(r3, out_json=os.path.join(tmp, "ex.json"))
    ck("EXACT triple, even with the value dead on the reference, is NOT A RESULT "
       "(rule 5 limb 2) -- state %s" % rec3["triple_limb_b"]["state"],
       rec3["triple_limb_b"]["state"] == "EXACT" and rec3["limb_B"]["verdict"] == "NOT A RESULT")
    ck("NO GCI is quoted in the EXACT state", rec3["triple_limb_b"]["gci_fine"] is None)

    # ---- ARM 4: GCI > GCI_MAX -- inside the band but the uncertainty is too large.
    base = REF_U_BAR
    r4 = _make_run(os.path.join(tmp, "run_gci"), [REF_TAU_W] * 3,
                   [base * 1.0032, base * 1.0008, base * 1.0002])
    rec4 = grade(r4, out_json=os.path.join(tmp, "gci.json"))
    tri4 = rec4["triple_limb_b"]
    ck("GCI > GCI_MAX turns an in-band CONVERGING triple into NOT A RESULT "
       "(GCI %.4e vs ceiling %.3g)" % (tri4["gci_fine"] or -1, GCI_MAX),
       tri4["state"] == "CONVERGING" and rec4["limb_B"]["inside"]
       and (tri4["gci_fine"] > GCI_MAX) == (rec4["limb_B"]["verdict"] == "NOT A RESULT"))

    # ---- ARM 5: DIVERGENT -- R1's own measured triple, re-run through R2's classifier.
    tri5 = roache(39.23440288031822, 39.209011897243556, 38.979197204778664)
    ck("R1's MEASURED tau_w triple classifies DIVERGENT with R = %.6f" % tri5["R"],
       tri5["state"] == "DIVERGENT" and tri5["gci_fine"] is None)

    # ---- ARM 6: p < P_MIN
    tri6 = roache(1.0, 1.0 + 1e-3, 1.0 + 1e-3 + 0.95e-3)
    ck("p < P_MIN (p = %s) makes the triple STAGNANT, so limb B is NOT A RESULT" % tri6["p"],
       tri6["state"] == "STAGNANT" and tri6.get("p_below_P_MIN") is True)
    ck("OSCILLATORY is reached and quotes no GCI", roache(1.0, 1.1, 1.05)["state"] == "OSCILLATORY"
       and roache(1.0, 1.1, 1.05)["gci_fine"] is None)

    # ---- ARM 7: LIMB A floor REFUSES a drifting wall shear.
    la = verdict_limb_a({"L1": REF_TAU_W, "L2": REF_TAU_W * (1 + 1e-6), "L3": REF_TAU_W})
    ck("LIMB A floor REFUSES a 1e-6 drift: verdict %s, invariance %.3e"
       % (la["verdict"], la["mesh_invariance_rel"]), la["verdict"] == "GATE FAIL")
    la_ok = verdict_limb_a({"L1": REF_TAU_W, "L2": REF_TAU_W * (1 + 1e-13), "L3": REF_TAU_W})
    ck("LIMB A floor ACCEPTS round-off-level agreement (%.3e)" % la_ok["mesh_invariance_rel"],
       la_ok["verdict"] == "PASS")
    ck("LIMB A's registered sentence makes NO continuum claim",
       "discretisation error" in la_ok["sentence"] and "correct to" not in la_ok["sentence"])

    # ---- ARM 8: the wall-shear uniformity control.
    r8 = _make_run(os.path.join(tmp, "run_nonunif"), [REF_TAU_W] * 3, pred, uniform=False)
    _refuses("wall-shear REFUSES a non-developed (non-uniform) window",
             wall_shear_window, os.path.join(r8, "L1"), "8000")

    # ---- ARM 9: THE CONVERGENCE DISJUNCTION, every row of the sec.6.2 table.
    r9a = _make_run(os.path.join(tmp, "run_null"), [REF_TAU_W] * 3, pred,
                    ux_res_tail=5e-9, hist_null=True)
    c9a = convergence(os.path.join(r9a, "L1"), None)
    ck("C2 FLOORED-AND-FLAT accepted on a NULL RANGE (tau p2p %.1e, ubar p2p %.1e) "
       "-- VMFL006 REFUSED exactly this" % (c9a["C2_tau_rel_p2p"], c9a["C2_ubar_rel_p2p"]),
       c9a["ACCEPTED"] and c9a["limb_satisfied"] == "C2"
       and c9a["C2_tau_range_is_null"] and c9a["C1_DESCENDED"] is False)

    r9b = _make_run(os.path.join(tmp, "run_desc"), [REF_TAU_W] * 3, pred,
                    ux_res_tail=1e-6, hist_flat=False, still_descending=True)
    _refuses("still-descending REFUSED (rule 5 limb 1): above the floor AND still moving",
             convergence, os.path.join(r9b, "L1"), None)

    r9c = _make_run(os.path.join(tmp, "run_mixed"), [REF_TAU_W] * 3, pred)
    c9c = convergence(os.path.join(r9c, "L3"), None)
    ck("the two limbs cannot both fail on a converged level: C1=%s C2=%s ACCEPTED=%s"
       % (c9c["C1_DESCENDED"], c9c["C2_FLOORED_AND_FLAT"], c9c["ACCEPTED"]), c9c["ACCEPTED"])
    ck("SATISFIABILITY: the C1-only and C2-only regimes are BOTH reachable, so the "
       "clause is a disjunction and not VMFL006's conjunction",
       c9c["limb_satisfied"] == "C1" and c9a["limb_satisfied"] == "C2")

    # ---- ARM 10: THE PLANT SHOWN ABLE TO FAIL.
    r10 = _make_run(os.path.join(tmp, "run_blind"), [REF_TAU_W] * 3, pred)

    def _blind_patch(path, patch, delta):
        return None

    def _blind_int(path, delta):
        return None

    _refuses("BLIND writer: PLANT-A REFUSES when the plant never reaches disk",
             planted_zero_tau, os.path.join(r10, "L1"), "8000", _blind_patch)
    _refuses("BLIND writer: PLANT-B REFUSES when the plant never reaches disk",
             planted_zero_ubar, os.path.join(r10, "L1"), "8000", _blind_int)
    r10b = _make_run(os.path.join(tmp, "run_zero"), [0.0, REF_TAU_W, REF_TAU_W], pred)
    _refuses("identically-zero channel: PLANT-A REFUSES rather than reporting a zero",
             planted_zero_tau, os.path.join(r10b, "L1"), "8000")

    # ---- ARM 11: PHASE ORDERING -- the plants precede a clause that refuses.
    #      L3's log has no `End` line, so PHASE 3 refuses; the plants must already have
    #      run at all three levels. VMFL006's plant list was EMPTY in exactly this case.
    r11 = os.path.join(tmp, "run_order")
    os.makedirs(r11, exist_ok=True)
    for lvl, ub in zip(LEVELS, pred):
        _write_level(r11, lvl, REF_TAU_W, ub, write_end=(lvl != "L3"))
    plants = []
    try:
        grade(r11, out_json=os.path.join(tmp, "order.json"))
    except SystemExit:
        for lvl in LEVELS:
            ld = os.path.join(r11, lvl)
            plants.append(os.path.exists(os.path.join(ld, "8000", "wallShearStress")))
    ck("PLANTS PRECEDE every refusing clause: PHASE 3 refused on L3's missing End line "
       "and all three levels' plant targets survive intact", all(plants) and len(plants) == 3)

    # ---- ARM 12: completion clauses drive to refusal.
    r12 = _make_run(os.path.join(tmp, "run_short"), [REF_TAU_W] * 3, pred, exec_lines=7999)
    _refuses("completion REFUSES when last Time != endTime (rule 4, original form)",
             completion, r12, "L1")
    r13 = _make_run(os.path.join(tmp, "run_rc"), [REF_TAU_W] * 3, pred, rc=124)
    _refuses("completion REFUSES a recorded non-zero rc (124 = the cap fired)",
             completion, r13, "L1")

    # ---- ARM 13: the units falsifier.
    la_units = verdict_limb_a({lvl: REF_TAU_W * RHO for lvl in LEVELS})
    ck("the kinematic->physical falsifier: an 800x reading GATE FAILs limb A "
       "(worst rel dev %.3e)" % la_units["worst_rel_dev"], la_units["verdict"] == "GATE FAIL")

    # ---- ARM 14: the geometry falsifier for limb B.
    lb_geo = verdict_limb_b(roache(REF_U_BAR * 100 * 1.004, REF_U_BAR * 100 * 1.001, REF_U_BAR * 100 * 1.00025),
                            {l: REF_U_BAR * 100 * f for l, f in zip(LEVELS, (1.004, 1.001, 1.00025))})
    ck("the manual's 100x units defect would GATE FAIL limb B (rel dev %.3e)"
       % lb_geo["deviation_rel"], lb_geo["verdict"] == "GATE FAIL")

    npass = sum(1 for r in _RESULTS if r)
    nfail = sum(1 for r in _RESULTS if not r)
    print("")
    print("SELFTEST: %d checks, %d failures" % (len(_RESULTS), nfail))
    if nfail == 0:
        print("SELFTEST: all checks passed")
    return 0 if nfail == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(description="VMFL038-R2 comparator")
    ap.add_argument("--run-root", default=DEFAULT_RUN_ROOT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-frozen", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.verify_frozen:
        return verify_frozen()
    grade(args.run_root, out_json=args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
