#!/usr/bin/env python3
# =============================================================================
# VMFL063 COMPARATOR -- Separated Laminar Flow Over a Blunt Plate
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 193 (Table .63.1).
#
# FROZEN INSTRUMENT (CLAUDE.md rule 2). Once the pre-registration commit exists,
# this file is never edited; a departure is a NEW registration and a NEW row.
#
# WHAT IT GRADES
#   LIMB A -- CONTINUUM: LR/(2t) at the finest level against the manual's Target
#             4.0 (EXPERIMENTAL: Lane & Loehrke 1980), band 10 % relative, on a
#             three-level r = 2 Roache triple. CEILING `GATE REACHED`; this
#             function CANNOT emit `PASS` and refuses if it ever would.
#   LIMB B -- SAME-DISCRETE-PROBLEM IDENTITY (VERIFICATION_CHARTER sec.2f.3):
#             serial determinism. L1 and its twin L1D are the SAME discrete
#             problem solved twice; the claim is identity, not accuracy, so a
#             triple is irrelevant to it and `PASS` is available.
#
# THE ROW verdict is the WORST limb. Limb A's ceiling is `GATE REACHED`, so the
# ROW can never read `PASS` and this registration produces NO credential.
#
# NO `assert` STATEMENT APPEARS IN THIS FILE. `python3 -O` deletes every assert,
# so a control written as an assert is not a control (L-332). `_ast_guard()`
# walks this file's own AST and REFUSES if the ast.Assert count is not 0.
#
# EVERY file read goes through `one_match()`, which REFUSES unless the pattern
# matches EXACTLY ONE path. No `sorted(glob.glob(...))[-1]` appears anywhere:
# lexicographic sorting of numeric directory names puts `950` after `2000`, and
# that shape has 19 measured hazard sites in this territory. Where a numeric
# order is genuinely needed, `numeric_latest_time_dir()` sorts with key=float
# AND is cross-checked against the solver log's own last Time.
# =============================================================================

import os, re, sys, json, math, glob, shutil, tempfile, ast, hashlib

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL063")

# ----------------------------------------------------------- FROZEN CONSTANTS --
# Geometry and fluid, VM2026R1 p.193, verbatim from the manual's table.
TWO_T     = 0.090           # plate thickness 2t, m
T_HALF    = 0.045           # plate half-thickness, m (the plate top surface y)
PLATE_L   = 1.500           # plate length, m
U_INF     = 0.0517          # free-stream velocity, m/s
NU        = 1.7894e-05      # kinematic viscosity, m2/s (mu/rho, rho = 1)
RE_2T     = 260.0           # manual's stated Reynolds number on plate thickness

# THE GATE (limb A). Reference is EXPERIMENTAL -- Lane & Loehrke, Trans. ASME
# Vol.102 pp.494-496 (1980), the manual's own cited Reference.
REF_LR2T  = 4.0             # Target, non-dimensionalised reattachment LR/(2t)
TOL       = 0.10            # frozen band, relative. Justified in PREREGISTRATION
                            # sec.5 from the manual's OWN agreement class and the
                            # register's existing band for this quantity class
                            # (row #30, VMFL064-R2). NEVER from a run.
ANSYS_FLUENT_LR2T = 4.16    # manual Table .63.1 -- CONTEXT ONLY, never the gate
ANSYS_CFX_LR2T    = 4.05    # manual Table .63.2 -- CONTEXT ONLY, never the gate

# THE REGISTERED SEARCH WINDOW for the primary reattachment, metres from the
# blunt leading-edge face (x = 0), frozen before any compute.
#   lower 0.0  -- OPEN at the lower end: a crossing exactly at x = 0 is the
#                 separation point, not a reattachment.
#   upper 1.2 m = 13.33*2t = 3.33 * the expected LR (4.0*0.09 = 0.36 m), and it
#                 stops 0.3 m short of the outlet. It spans more than three times
#                 the reference, so it cannot be read as tuned to an answer, and
#                 it excludes any outlet-region artefact.
X_WIN_LO  = 0.0
X_WIN_HI  = 1.2
# The sign convention of the reported wallShearStress is NOT assumed. It is fixed
# at run time from the sampled face nearest X_SIGN_REF, which sits OUTSIDE the
# search window, deep in the attached boundary layer, 0.15 m short of the outlet.
X_SIGN_REF = 1.35
TAU_EPS    = 1.0e-14        # below this the reference face carries no sign

FS        = 1.25            # Roache safety factor
RATIO     = 2.0             # grid refinement ratio, all four directions
P_MIN     = 0.05            # observed-order floor (FINDING_p_floor.md sec.4)

# PLANTED-ZERO control (CLAUDE.md rule 3), sized to the reader (L-340) and
# applied to EVERY face so it can never land outside the reader's support (L-347).
K_PLANT       = 0.05        # plant magnitude as a fraction of max|tau| in-window
K_PLANT_U     = 0.05        # same, as a fraction of U_INF, for the u_x channel
PLANT_MIN_ABS = 1.0e-12     # a reader that moves by less than this has not moved

# Cross-instrument agreement: wall shear vs near-wall u_x, in local cell widths.
CROSS_TOL_CELLS = 3.0

LEVELS     = ["L1", "L2", "L3"]
DET_TWIN   = "L1D"          # limb B: the determinism twin of L1, same inputs
FIELDS     = ("U", "p", "wallShearStress", "Cx", "Cy")
AGE_DATUM  = "0/U"

TIER_CEILING_A = "GATE REACHED"     # hard ceiling, limb A -- PASS unavailable
TIER_CEILING_B = "PASS"             # limb B is an identity claim (sec.2f.3)
VOCAB      = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT")
ORDER      = {"NOT A RESULT": 0, "GATE FAIL": 1, "GATE REACHED": 2, "PASS": 3}

# L-342 field classes (Sanaa 2026-08-26): a bookkeeping failure invalidates the
# bookkeeping, never the physics artefacts.
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
    """THE ONLY WAY THIS COMPARATOR OPENS A FILE.

    Returns the single path matching `pattern`, and REFUSES (exit 2) on any other
    cardinality. `sorted(glob.glob(p))[-1]` is banned in this file: it sorts
    numeric directory names LEXICOGRAPHICALLY, so `950` beats `2000` and the
    grader silently reads the wrong artefact. 19 such sites are measured in this
    territory. A guard that refuses on ambiguity cannot misread; a `[-1]` can."""
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
    """Latest numeric time directory, sorted by key=float -- NEVER lexicographic.
    Returns (name, float) or (None, None). Used ONLY as a cross-check against the
    solver log's own last Time; a disagreement REFUSES."""
    names = []
    for d in glob.glob(os.path.join(level_dir, "*")):
        if not os.path.isdir(d):
            continue
        b = os.path.basename(d)
        if re.match(r"^[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$", b):
            names.append((float(b), b))
    if not names:
        return None, None
    names.sort(key=lambda t: t[0])           # NUMERIC, key=float
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
    """Add `delta` to the x-component of EVERY face value of `patch`, in place,
    on a COPY of the real solver output. The file's header, dimensions and every
    other patch are left byte-untouched: this perturbs the real bytes, it does
    not rebuild a synthetic file."""
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


def _plant_internal_vector_x(path, delta):
    p, txt = read_text(path, "plant target internalField")
    m = _INT_VEC_RE.search(txt)
    if not m:
        raise SystemExit2("plant: no internalField vector list in %s" % p)
    body = m.group(2)
    def _bump(mo):
        parts = mo.group(1).split()
        return "(%.12g %s %s)" % (float(parts[0]) + delta, parts[1], parts[2])
    newbody = re.sub(r"\(([^()]*)\)", _bump, body)
    fh = open(p, "w")
    try:
        fh.write(txt.replace(body, newbody, 1))
    finally:
        fh.close()


# ------------------------------------------------------------ the locators -----
def orient_from_reference(xs, tau_reported):
    """Fix the reported wallShearStress sign convention FROM THE DATA, at the
    registered abscissa X_SIGN_REF, which lies OUTSIDE the search window in the
    unambiguously attached boundary layer. Returns +1 or -1 such that
    ORIENT*tau_reported is POSITIVE where the flow is attached. Nothing about
    OpenFOAM's convention is assumed; a near-zero reference face REFUSES."""
    if not xs:
        raise SystemExit2("orientation: no plateTop faces sampled")
    i = min(range(len(xs)), key=lambda k: abs(xs[k] - X_SIGN_REF))
    tref = tau_reported[i]
    if abs(tref) < TAU_EPS:
        raise SystemExit2("orientation: reference face x=%.6g carries tau=%.6g, "
                          "below TAU_EPS=%g -- the attached-flow sign cannot be "
                          "fixed and the reader will not guess it" % (xs[i], tref, TAU_EPS))
    return (1.0 if tref > 0.0 else -1.0), xs[i], tref


def last_sign_change_in_window(xs, vals, x_lo=X_WIN_LO, x_hi=X_WIN_HI):
    """THE GATE FUNCTIONAL. The primary reattachment is the LAST reversed-to-
    attached crossing of the PHYSICAL wall shear inside the frozen window, found
    by linear interpolation between the bracketing samples.

    WHY THE LAST, NOT THE FIRST. A secondary counter-rotating eddy can sit at the
    foot of the blunt leading edge, INSIDE the primary bubble, and it is resolved
    only on a fine enough mesh. It adds crossings UPSTREAM of the primary
    reattachment and can flip the sign the profile STARTS with -- which is exactly
    what voided VMFL064 attempt 1 (register row #29). It can never add a crossing
    DOWNSTREAM of reattachment, because there the near-wall flow is attached and
    forward. The last crossing in the window is therefore the same number on a
    coarse mesh that never sees the eddy and on a fine mesh that does.

    Returns None when there is NO reversed-to-attached crossing in the window;
    the caller REFUSES on None rather than degrading."""
    pairs = sorted(zip(xs, vals))
    win = [q for q in pairs if x_lo < q[0] <= x_hi]
    if len(win) < 2:
        return None
    xw = [q[0] for q in win]
    vw = [q[1] for q in win]
    found = None
    for i in range(1, len(vw)):
        if vw[i - 1] < 0.0 <= vw[i]:
            f = -vw[i - 1] / (vw[i] - vw[i - 1])
            found = xw[i - 1] + f * (xw[i] - xw[i - 1])
    return found


def first_sign_change_in_window(xs, vals, x_lo=X_WIN_LO, x_hi=X_WIN_HI):
    """OFF THE GRADING PATH. The FIRST-crossing locator, kept so the corner-eddy
    control can drive it on the SAME constructed bytes and show that it returns a
    different (wrong) number where the gate reader returns the primary length.
    Never called by main()'s grading path."""
    pairs = sorted(zip(xs, vals))
    win = [q for q in pairs if x_lo < q[0] <= x_hi]
    if len(win) < 2:
        return None
    xw = [q[0] for q in win]
    vw = [q[1] for q in win]
    for i in range(1, len(vw)):
        if vw[i - 1] < 0.0 <= vw[i]:
            f = -vw[i - 1] / (vw[i] - vw[i - 1])
            return xw[i - 1] + f * (xw[i] - xw[i - 1])
    return None


def count_sign_changes_in_window(xs, vals, x_lo=X_WIN_LO, x_hi=X_WIN_HI):
    """DIAGNOSTIC ONLY -- printed beside every level so the corner eddy is visible
    in the record (2 reversed->attached crossings = it is resolved, 1 = it is not).
    It gates nothing."""
    pairs = sorted(zip(xs, vals))
    win = [q for q in pairs if x_lo < q[0] <= x_hi]
    vw = [q[1] for q in win]
    return {"neg_to_pos": sum(1 for i in range(1, len(vw)) if vw[i - 1] < 0.0 <= vw[i]),
            "pos_to_neg": sum(1 for i in range(1, len(vw)) if vw[i - 1] >= 0.0 > vw[i]),
            "n_in_window": len(vw),
            "starts_attached": bool(vw and vw[0] >= 0.0)}


def local_dx_at(xs, x0):
    """Width of the sample interval bracketing x0 -- the resolution with which the
    crossing location is known. Used for the cross-instrument tolerance."""
    s = sorted(xs)
    for i in range(1, len(s)):
        if s[i - 1] <= x0 <= s[i]:
            return s[i] - s[i - 1]
    return max(s[i] - s[i - 1] for i in range(1, len(s))) if len(s) > 1 else float("nan")


# ---------------------------------------------------------------- profiles -----
def wallshear_profile(level_dir, t):
    """(x, tau_physical, orientation record) on the plate top surface at time t."""
    tau_rep = read_patch_vector_x(os.path.join(level_dir, t, "wallShearStress"), "plateTop")
    x       = read_patch_scalar(os.path.join(level_dir, t, "Cx"), "plateTop")
    if len(x) != len(tau_rep):
        raise SystemExit2("plateTop face count mismatch at %s/%s: Cx %d, wallShearStress %d"
                          % (level_dir, t, len(x), len(tau_rep)))
    orient, xref, tref = orient_from_reference(x, tau_rep)
    return x, [orient * v for v in tau_rep], {"orient": orient, "x_ref": xref, "tau_ref": tref}


def nearwall_u_profile(level_dir, t):
    """INDEPENDENT INSTRUMENT: streamwise velocity in the first cell row above the
    plate. Different field, different discretisation, same physical event. In this
    mesh every cell with x > 0 lies above the plate, so the minimum-y row of that
    set is the first row off plateTop."""
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"))
    cy = read_internal_scalar(os.path.join(level_dir, t, "Cy"))
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"))
    if not (len(cx) == len(cy) == len(ux)):
        raise SystemExit2("internal field length mismatch at %s/%s: Cx %d Cy %d U %d"
                          % (level_dir, t, len(cx), len(cy), len(ux)))
    cand = [(cy[i], cx[i], ux[i]) for i in range(len(cx)) if cx[i] > 0.0]
    if not cand:
        raise SystemExit2("no internal cells with x > 0 at %s/%s" % (level_dir, t))
    ymin = min(c[0] for c in cand)
    row = [(c[1], c[2]) for c in cand if abs(c[0] - ymin) < 1e-12]
    return [r[0] for r in row], [r[1] for r in row]


# ---------------------------------------------------- planted-zero (rule 3) ----
def planted_zero_tau(level_dir, t):
    """CLAUDE.md rule 3, in the form this territory's two recorded failures demand.

    P1a -- READER SENSITIVITY. Plant a SIZED offset into the x-component of EVERY
           plateTop face of a COPY of the real solver file, read it back FROM
           DISK through the real reader, and require every value to have moved by
           exactly the plant. Sized, because an averaging reader dilutes a fixed
           single-point plant by ~1/sqrt(N) (L-340, register row #26). Every face,
           because a correctly sized point plant can still land on a row OUTSIDE
           the reader's support (L-347, register row #31).

    P1b -- GATE-FUNCTIONAL SENSITIVITY. The SAME planted file is run through the
           FULL gate functional. Shifting the physical wall shear UP by a positive
           constant must move the last reversed-to-attached crossing UPSTREAM, or
           push it out of the window entirely. A plant the raw reader sees but the
           GATE does not is exactly the row-#31 failure and it REFUSES here.

    Either check failing REFUSES (exit 2). The only way this function returns is
    to have seen the plant on both."""
    src = one_match(os.path.join(level_dir, t, "wallShearStress"), "plant source wallShearStress")
    tmp = tempfile.mkdtemp(prefix="vmfl063_plant_tau_")
    try:
        dst = os.path.join(tmp, "wallShearStress")
        shutil.copy(src, dst)
        base_rep = read_patch_vector_x(dst, "plateTop")
        x, tau_phys, orec = wallshear_profile(level_dir, t)
        inwin = [abs(v) for xi, v in zip(x, tau_phys) if X_WIN_LO < xi <= X_WIN_HI]
        if not inwin or max(inwin) <= 0.0:
            raise SystemExit2("planted-zero: the plateTop wall shear is identically zero "
                              "in the window -- there is nothing for a plant to be sized to")
        plant_phys = K_PLANT * max(inwin)
        delta_rep = orec["orient"] * plant_phys        # plant in the PHYSICAL sense
        _plant_patch_vector_x(dst, "plateTop", delta_rep)
        seen_rep = read_patch_vector_x(dst, "plateTop")
        if len(seen_rep) != len(base_rep):
            raise SystemExit2("planted-zero: face count changed across the plant")
        worst = max(abs((seen_rep[i] - base_rep[i]) - delta_rep) for i in range(len(base_rep)))
        scale = max(abs(delta_rep), 1.0)
        if not (worst <= 1.0e-9 * scale):
            raise SystemExit2(
                "planted-zero control FAILED (P1a, reader sensitivity) for the wall-shear "
                "channel: planted %.12g into EVERY plateTop face of %s, the worst read-back "
                "discrepancy is %.12g. A reader not shown able to see a non-zero cannot "
                "certify a zero (CLAUDE.md rule 3)." % (delta_rep, src, worst))
        lr_base = last_sign_change_in_window(x, tau_phys)
        seen_phys = [orec["orient"] * v for v in seen_rep]
        lr_plant = last_sign_change_in_window(x, seen_phys)
        if lr_base is None:
            raise SystemExit2("planted-zero: no reversed-to-attached crossing in the window "
                              "on the UNPLANTED profile -- there is no gate value to perturb")
        if lr_plant is None:
            moved, how = True, "the plant pushed the crossing OUT of the window"
        else:
            moved = (lr_base - lr_plant) > PLANT_MIN_ABS
            how = "crossing moved upstream by %.12g m" % (lr_base - lr_plant)
        if not moved:
            raise SystemExit2(
                "planted-zero control FAILED (P1b, gate-functional sensitivity) for the "
                "wall-shear channel: the raw reader saw the plant but the GATE FUNCTIONAL "
                "did not move upstream (LR %.12g -> %.12g). A plant the gate cannot see is "
                "the register row #31 failure mode (L-347)."
                % (lr_base, -1.0 if lr_plant is None else lr_plant))
        return {"channel": "wall_shear", "passed": True, "plant_physical": plant_phys,
                "plant_reported": delta_rep, "worst_readback_error": worst,
                "lr_unplanted": lr_base, "lr_planted": lr_plant, "gate_response": how,
                "file": src, "patch": "plateTop", "n_faces": len(base_rep)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def planted_zero_u(level_dir, t):
    """The same two-stage control on the INDEPENDENT near-wall u_x instrument."""
    src = one_match(os.path.join(level_dir, t, "U"), "plant source U")
    tmp = tempfile.mkdtemp(prefix="vmfl063_plant_u_")
    try:
        dst = os.path.join(tmp, "U")
        shutil.copy(src, dst)
        base = read_internal_vector_x(dst)
        plant = K_PLANT_U * U_INF
        _plant_internal_vector_x(dst, plant)
        seen = read_internal_vector_x(dst)
        if len(seen) != len(base):
            raise SystemExit2("planted-zero: internal cell count changed across the U plant")
        worst = max(abs((seen[i] - base[i]) - plant) for i in range(len(base)))
        if not (worst <= 1.0e-9 * max(abs(plant), 1.0)):
            raise SystemExit2(
                "planted-zero control FAILED (P1a) for the near-wall u_x channel: planted "
                "%.12g into EVERY internal cell of %s, worst read-back discrepancy %.12g "
                "(CLAUDE.md rule 3)." % (plant, src, worst))
        xs, us = nearwall_u_profile(level_dir, t)
        lr_base = last_sign_change_in_window(xs, us)
        lr_plant = last_sign_change_in_window(xs, [u + plant for u in us])
        if lr_base is None:
            raise SystemExit2("planted-zero: no u_x reversal in the window on the UNPLANTED "
                              "near-wall row -- there is no cross-instrument value to perturb")
        if lr_plant is None:
            moved, how = True, "the plant pushed the u_x crossing OUT of the window"
        else:
            moved = (lr_base - lr_plant) > PLANT_MIN_ABS
            how = "u_x crossing moved upstream by %.12g m" % (lr_base - lr_plant)
        if not moved:
            raise SystemExit2("planted-zero control FAILED (P1b) for the near-wall u_x "
                              "channel: the gate functional did not move (LR %.12g)" % lr_base)
        return {"channel": "nearwall_ux", "passed": True, "plant": plant,
                "worst_readback_error": worst, "lr_unplanted": lr_base,
                "lr_planted": lr_plant, "gate_response": how, "file": src}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------- strict completion --
def completion(run_root, level):
    """CLAUDE.md rule 4 IN FULL, adapted for a residualControl-terminated STEADY
    solve and DECLARED THAT WAY IN THE FROZEN PRE-REGISTRATION (sec.6), not
    improvised here, and split into L-342 field classes.

    PHYSICS-CRITICAL (each gates; any failure REFUSES exit 2):
      * an 'End' line in log.simpleFoam                (EXACT name, one_match)
      * 'SIMPLE solution converged' present            (stopped on its own criterion)
      * last Time  <  endTime                          (did NOT run out of clock: for
                                                        a steady solve 'last == endTime'
                                                        means it never converged)
      * ExecutionTime count == the iteration count
      * every declared field present at that time
      * the numerically-latest time directory (key=float) EQUALS the log's last Time
      * AGE GUARD: every field at endTime strictly NEWER than the case's own 0/T
        datum -- here 0/U, which the launcher touches LAST, immediately before the
        solver, so it dates the run allowed to produce the answer

    INFRASTRUCTURE (L-342): RUN_RC.<level>. ABSENT -> rc NOT MEASURED, disclosed,
    grade PROCEEDS on the physics artefacts. PRESENT AND non-zero -> REFUSE."""
    level_dir = os.path.join(run_root, level)
    out = {"level": level, "level_dir": level_dir}

    rcf = os.path.join(run_root, "RUN_RC.%s" % level)
    out["rc_source"] = rcf
    if not os.path.exists(rcf):
        out["rc"] = None
        out["rc_status"] = "NOT MEASURED"
        out["rc_note"] = ("RUN_RC.%s absent -- INFRASTRUCTURE field (L-342); the grade "
                          "proceeds on the physics-critical clauses." % level)
    else:
        _p, rct = read_text(rcf, "RUN_RC.%s" % level)
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)", rct, re.M)
        if not m:
            out["rc"] = None
            out["rc_status"] = "NOT MEASURED"
            out["rc_note"] = "RUN_RC.%s present but carries no rc= line (L-342)." % level
        else:
            out["rc"] = int(m.group(1))
            out["rc_status"] = "MEASURED"
            if out["rc"] != 0:
                raise SystemExit2("rc=%d recorded for %s (124 == the cap fired). A RECORDED "
                                  "non-zero rc is evidence about the SOLVER and refuses (L-342)."
                                  % (out["rc"], level))
        for key in ("wall_s", "core_min", "timeout_s"):
            mm = re.search(r"^\s*%s\s*=\s*([0-9.eE+-]+)" % key, rct, re.M)
            out[key] = float(mm.group(1)) if mm else None

    logp, lt = read_text(os.path.join(level_dir, "log.simpleFoam"),
                         "solver log for %s" % level)
    out["log"] = logp
    out["end_lines"] = len(re.findall(r"^End\s*$", lt, re.M))
    if out["end_lines"] < 1:
        raise SystemExit2("no End line in %s" % logp)
    out["converged"] = ("SIMPLE solution converged" in lt)
    if not out["converged"]:
        raise SystemExit2("%s never reported 'SIMPLE solution converged' -- a steady solve "
                          "that did not meet its own residualControl is not a completed run"
                          % logp)
    times = [int(x) for x in re.findall(r"^Time = (\d+)", lt, re.M)]
    if not times:
        raise SystemExit2("no Time lines in %s" % logp)
    out["last_time"] = times[-1]
    out["n_exec"] = lt.count("ExecutionTime")
    if out["n_exec"] != out["last_time"]:
        raise SystemExit2("%s: ExecutionTime count %d != last Time %d"
                          % (logp, out["n_exec"], out["last_time"]))

    cdp, ctl = read_text(os.path.join(level_dir, "system", "controlDict"),
                         "controlDict for %s" % level)
    mE = re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    if not mE:
        raise SystemExit2("no endTime in %s" % cdp)
    out["endTime"] = float(mE.group(1))
    if not (out["last_time"] < out["endTime"]):
        raise SystemExit2("%s reached endTime %g -- it ran out of clock and did NOT converge"
                          % (level_dir, out["endTime"]))

    t = str(out["last_time"])
    out["time_dir"] = t
    nm, nv = numeric_latest_time_dir(level_dir)
    out["numeric_latest_time_dir"] = nm
    if nm is None or abs(nv - float(t)) > 1e-9:
        raise SystemExit2("time-directory disagreement at %s: the log's last Time is %s, the "
                          "numerically-latest directory (key=float) is %r. A grader that picks "
                          "one of these without checking the other is the lexicographic-sort "
                          "hazard in another costume." % (level_dir, t, nm))
    for f in FIELDS:
        one_match(os.path.join(level_dir, t, f), "field %s at %s/%s" % (f, level, t))
    zpath = one_match(os.path.join(level_dir, AGE_DATUM), "age-guard datum %s" % AGE_DATUM)
    z = os.path.getmtime(zpath)
    for f in FIELDS:
        fp = os.path.join(level_dir, t, f)
        if not os.path.getmtime(fp) > z:
            raise SystemExit2("AGE GUARD: %s is not strictly newer than %s -- the field at "
                              "endTime does not post-date the launch that was allowed to "
                              "produce it (CLAUDE.md rule 4)" % (fp, zpath))
    out["age_guard"] = "all %d fields at %s newer than %s" % (len(FIELDS), t, AGE_DATUM)
    out["state"] = "COMPLETE"
    return out


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """CLAUDE.md rule 5. f1 coarse, f2 medium, f3 fine. A GCI is quoted ONLY on a
    CONVERGING (hence monotone) triple whose observed order clears P_MIN."""
    d32 = f3 - f2
    d21 = f2 - f1
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "ratio": r, "fs": fs,
           "d21": d21, "d32": d32, "p": None, "gci_fine": None, "f_extrapolated": None}
    if d21 == 0.0 and d32 == 0.0:
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
        out["p_floor"] = P_MIN
        out["p_below_floor"] = True
        return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


# ------------------------------------------------------------------ verdicts ---
def verdict_for_limb_a(tri, inside):
    """LIMB A -- the ONE verdict path for the continuum limb. The planted controls
    DRIVE this function, so they exercise the code that actually decides.

    Rule 5 is ONE-WAY: a non-CONVERGING triple can only turn a verdict INTO
    `NOT A RESULT`, never the reverse. `PASS` is UNREACHABLE here by construction
    and the function refuses if it ever produces one."""
    if tri["state"] != "CONVERGING":
        if tri.get("p_below_floor"):
            v, why = ("NOT A RESULT",
                      "observed order p = %.6g is below the frozen floor P_MIN = %.3g; the "
                      "triple is %s and NO GCI is quoted" % (tri["p"], P_MIN, tri["state"]))
        else:
            v, why = ("NOT A RESULT",
                      "grid triple is %s, not CONVERGING (CLAUDE.md rule 5 step 2) -- "
                      "NOT A RESULT whatever the value" % tri["state"])
    elif inside:
        v, why = ("GATE REACHED",
                  "LR/(2t) is inside the frozen %.3g band about the experimental Target "
                  "%.4g on a CONVERGING triple. The ceiling is GATE REACHED, not PASS: the "
                  "reference is EXPERIMENTAL, so the limb makes a CONTINUUM claim and "
                  "VERIFICATION_CHARTER sec.2f.3 puts PASS out of reach "
                  "(PREREGISTRATION.md sec.3)." % (TOL, REF_LR2T))
    else:
        v, why = ("GATE FAIL",
                  "LR/(2t) is outside the frozen %.3g band about %.4g" % (TOL, REF_LR2T))
    if v == "PASS":
        raise SystemExit2("TIER CEILING VIOLATED: limb A emitted PASS, whose ceiling is "
                          "declared %r in the frozen pre-registration" % TIER_CEILING_A)
    if v not in VOCAB:
        raise SystemExit2("verdict %r is outside the fixed vocabulary (CLAUDE.md rule 1)" % v)
    return v, why


def verdict_for_limb_b(identical, detail):
    """LIMB B -- serial determinism, a SAME-DISCRETE-PROBLEM IDENTITY claim. Both
    sides carry the same discretisation error on the same mesh, it cancels
    exactly, and the claim is identity, not accuracy -- so a grid triple is
    irrelevant to it and `PASS` is available (VERIFICATION_CHARTER sec.2f.3).
    Rule 5 limb (1) still applies: both runs must pass strict completion, which
    completion() enforces before this is ever called."""
    v = "PASS" if identical else "GATE FAIL"
    if v not in VOCAB:
        raise SystemExit2("verdict %r is outside the fixed vocabulary" % v)
    return v, detail


def row_verdict(limbs):
    """The ROW verdict is the WORST limb. Limb A's ceiling is GATE REACHED, so the
    ROW can never read PASS and this registration produces NO credential -- stated
    in the pre-registration before compute and enforced here."""
    worst = min(limbs, key=lambda kv: ORDER[kv[1]])
    return worst[1]


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


# --------------------------------------------------- constructed-field writers -
# Module level, so the selftest and the controls use the SAME builders.
def _wss(patch, trips):
    body = "\n".join("(%.12g %.12g %.12g)" % t for t in trips)
    return ("FoamFile { version 2.0; format ascii; class volVectorField; object wallShearStress; }\n"
            "dimensions [0 2 -2 0 0 0 0];\ninternalField uniform (0 0 0);\n"
            "boundaryField {\n    %s { type calculated; value nonuniform List<vector> %d (\n%s\n); }\n}\n"
            % (patch, len(trips), body))


def _cx_patch(patch, xs, obj="Cx"):
    vv = " ".join("%.12g" % v for v in xs)
    return ("FoamFile { version 2.0; format ascii; class volScalarField; object %s; }\n"
            "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
            "boundaryField {\n    %s { type calculated; value nonuniform List<scalar> %d ( %s ); }\n}\n"
            % (obj, len(xs), vv, patch, len(xs), vv))


def _Ufield(trips):
    body = "\n".join("(%.12g %.12g %.12g)" % t for t in trips)
    return ("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
            "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> %d (\n%s\n);\n"
            "boundaryField {\n    plateTop { type noSlip; }\n}\n" % (len(trips), body))


def _pfield(n):
    return ("FoamFile { version 2.0; format ascii; class volScalarField; object p; }\n"
            "dimensions [0 2 -2 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
            "boundaryField {\n    plateTop { type zeroGradient; }\n}\n"
            % (n, " ".join(["0"] * n)))


def _bubble_tau(lr, n=181, x_hi=1.4):
    """A single-bubble physical wall-shear profile: reversed for x < lr, attached
    beyond, smooth through the crossing, and a realistic decay downstream."""
    xs, tau = [], []
    for i in range(n):
        x = x_hi * i / (n - 1.0)
        tau.append(1.0e-4 * math.tanh((x - lr) / (0.25 * lr)))
        xs.append(x)
    return xs, tau


def _corner_eddy_tau(lr, x_eddy=0.02, n=181, x_hi=1.4):
    """The SAME bubble with a secondary counter-rotating eddy at the leading-edge
    foot: an extra reversed->attached crossing UPSTREAM of the primary one."""
    xs, tau = _bubble_tau(lr, n, x_hi)
    out = []
    for x, t in zip(xs, tau):
        if x < 2.0 * x_eddy:
            out.append(1.0e-4 * math.sin(math.pi * (x - x_eddy) / x_eddy) * 0.5)
        else:
            out.append(t)
    return xs, out


def _write_level(root, level, lr, endtime=30000, iters=1234, converged=True,
                 end_line=True, exec_count=None, orient=1.0, fields=FIELDS,
                 age_ok=True, rc="0", write_rc=True, tau_scale=1.0):
    """Build a complete synthetic level directory that completion() and the whole
    grading path can run on."""
    d = os.path.join(root, level)
    os.makedirs(os.path.join(d, "system"))
    os.makedirs(os.path.join(d, "0"))
    t = str(iters)
    os.makedirs(os.path.join(d, t))
    xs, tau = _bubble_tau(lr)
    tau = [tau_scale * v for v in tau]
    trips = [(orient * v, 0.0, 0.0) for v in tau]
    # near-wall u_x mirrors the wall shear (same physical event, different field)
    ux = [1.0e-3 * math.tanh((x - lr) / (0.25 * lr)) for x in xs]
    fh = open(os.path.join(d, "0", "U"), "w"); fh.write(_Ufield([(0.0, 0.0, 0.0)] * len(xs))); fh.close()
    body = []
    for i in range(1, iters + 1):
        body.append("Time = %d\n" % i)
        body.append("ExecutionTime = %.2f s  ClockTime = %d s\n" % (0.01 * i, i))
    if converged:
        body.append("SIMPLE solution converged in %d iterations\n" % iters)
    if end_line:
        body.append("End\n")
    txt = "".join(body)
    if exec_count is not None:
        txt = txt.replace("ExecutionTime", "ExecTime", 1) if exec_count < iters else txt
    fh = open(os.path.join(d, "log.simpleFoam"), "w"); fh.write(txt); fh.close()
    fh = open(os.path.join(d, "system", "controlDict"), "w")
    fh.write("application simpleFoam;\nendTime         %d;\n" % endtime); fh.close()
    present = set(fields)
    if "wallShearStress" in present:
        fh = open(os.path.join(d, t, "wallShearStress"), "w"); fh.write(_wss("plateTop", trips)); fh.close()
    if "Cx" in present:
        fh = open(os.path.join(d, t, "Cx"), "w"); fh.write(_cx_patch("plateTop", xs, "Cx")); fh.close()
    if "Cy" in present:
        fh = open(os.path.join(d, t, "Cy"), "w"); fh.write(_cx_patch("plateTop", [T_HALF + 5e-4] * len(xs), "Cy")); fh.close()
    if "U" in present:
        fh = open(os.path.join(d, t, "U"), "w"); fh.write(_Ufield([(u, 0.0, 0.0) for u in ux])); fh.close()
    if "p" in present:
        fh = open(os.path.join(d, t, "p"), "w"); fh.write(_pfield(len(xs))); fh.close()
    old = os.path.getmtime(os.path.join(d, "0", "U"))
    for f in os.listdir(os.path.join(d, t)):
        os.utime(os.path.join(d, t, f), (old + (100 if age_ok else -100),
                                         old + (100 if age_ok else -100)))
    if write_rc:
        fh = open(os.path.join(root, "RUN_RC.%s" % level), "w")
        fh.write("rc = %s\nlevel = %s\nwall_s = 10\nranks = 1\ncore_min = 0.1667\ntimeout_s = 5400\n"
                 % (rc, level)); fh.close()
    return d, t


# ------------------------------------------------------------- the AST guard ---
def _ast_guard():
    """Walk THIS FILE's own AST and refuse if it contains any `assert`. `python3 -O`
    deletes every assert statement, so a control written as an assert exists under
    one interpreter and not the other, and a control that vanishes is not a
    control (L-332). The count is measured from the SOURCE, so it is the same
    under both interpreters -- which is the point."""
    src = open(os.path.abspath(__file__), errors="replace").read()
    tree = ast.parse(src)
    n = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
    if n != 0:
        raise SystemExit2("AST GUARD: this comparator contains %d `assert` statement(s). "
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
    print("SELFTEST VMFL063 -- Separated Laminar Flow Over a Blunt Plate (VM2026R1 p.193)")

    ck("AST guard: ast.Assert count is 0 in this file", _ast_guard() == 0)

    tmp = tempfile.mkdtemp(prefix="vmfl063_selftest_")
    try:
        # ---- cardinality guard ------------------------------------------------
        os.makedirs(os.path.join(tmp, "card"))
        fh = open(os.path.join(tmp, "card", "only.txt"), "w"); fh.write("x"); fh.close()
        ck("one_match returns the single match",
           one_match(os.path.join(tmp, "card", "only.txt"), "t") ==
           os.path.join(tmp, "card", "only.txt"))
        ck("one_match REFUSES on zero matches",
           _refuses(one_match, os.path.join(tmp, "card", "missing.txt"), "t"))
        fh = open(os.path.join(tmp, "card", "twin.txt"), "w"); fh.write("y"); fh.close()
        ck("one_match REFUSES on two matches",
           _refuses(one_match, os.path.join(tmp, "card", "*.txt"), "t"))

        # ---- numeric, never lexicographic, time-dir ordering -------------------
        os.makedirs(os.path.join(tmp, "tord"))
        for nm in ("0", "950", "2000"):
            os.makedirs(os.path.join(tmp, "tord", nm))
        nm, nv = numeric_latest_time_dir(os.path.join(tmp, "tord"))
        ck("time dirs sort NUMERICALLY: 2000 beats 950 (lexicographic would say 950)",
           nm == "2000" and nv == 2000.0)
        ck("the lexicographic answer is demonstrably different here",
           sorted(["0", "950", "2000"])[-1] == "950")

        # ---- locators ---------------------------------------------------------
        xs, tau = _bubble_tau(0.36)
        lr = last_sign_change_in_window(xs, tau)
        ck("single-bubble profile: last-crossing locator recovers LR to 1e-5 m "
           "(the residual is the linear interpolation of tanh across one sample interval)",
           lr is not None and abs(lr - 0.36) < 1.0e-5)
        xe, te = _corner_eddy_tau(0.36)
        lr_last = last_sign_change_in_window(xe, te)
        lr_first = first_sign_change_in_window(xe, te)
        ck("corner-eddy control: the GATE reader (last crossing) still returns the primary LR",
           lr_last is not None and abs(lr_last - 0.36) < 5.0e-3)
        ck("corner-eddy control: the FIRST-crossing locator returns a DIFFERENT, wrong number "
           "on the SAME bytes (register row #29's defect, driven not described)",
           lr_first is not None and abs(lr_first - 0.36) > 0.1)
        cnt = count_sign_changes_in_window(xe, te)
        ck("crossing census sees the eddy (2 reversed->attached crossings)",
           cnt["neg_to_pos"] == 2)
        xo = xs + [1.25, 1.30]
        to = tau + [-1.0e-4, 1.0e-4]
        ck("a spurious crossing beyond X_WIN_HI is EXCLUDED by the frozen window",
           abs(last_sign_change_in_window(xo, to) - 0.36) < 1.0e-5)
        ck("local_dx_at returns the bracketing sample interval",
           abs(local_dx_at(xs, 0.36) - (1.4 / 180.0)) < 1.0e-9)

        # ---- orientation is taken FROM THE DATA, both conventions ------------
        o_p = orient_from_reference(xs, tau)[0]
        o_m = orient_from_reference(xs, [-v for v in tau])[0]
        ck("orientation from the reference face: +1 for the positive convention", o_p == 1.0)
        ck("orientation from the reference face: -1 for the inverted convention", o_m == -1.0)
        ck("both conventions yield the SAME LR (the reader assumes no sign convention)",
           abs(last_sign_change_in_window(xs, [o_p * v for v in tau]) -
               last_sign_change_in_window(xs, [o_m * -v for v in tau])) < 1.0e-12)
        ck("a reference face with |tau| below TAU_EPS REFUSES rather than guessing",
           _refuses(orient_from_reference, xs, [0.0] * len(xs)))

        # ---- strict completion, every clause -----------------------------------
        good = os.path.join(tmp, "good")
        os.makedirs(good)
        _write_level(good, "L1", 0.36)
        c = completion(good, "L1")
        ck("completion: a clean level is COMPLETE with rc MEASURED = 0",
           c["state"] == "COMPLETE" and c["rc"] == 0 and c["rc_status"] == "MEASURED")
        ck("completion: age guard reported", "newer than" in c["age_guard"])

        for tag, kw in (("no End line", {"end_line": False}),
                        ("no SIMPLE convergence", {"converged": False}),
                        ("age guard violated", {"age_ok": False})):
            r = os.path.join(tmp, "bad_" + tag.replace(" ", "_"))
            os.makedirs(r); _write_level(r, "L1", 0.36, **kw)
            ck("completion REFUSES: %s" % tag, _refuses(completion, r, "L1"))

        r = os.path.join(tmp, "bad_clock"); os.makedirs(r)
        _write_level(r, "L1", 0.36, endtime=1234, iters=1234)
        ck("completion REFUSES: last Time == endTime (ran out of clock, never converged)",
           _refuses(completion, r, "L1"))

        r = os.path.join(tmp, "bad_field"); os.makedirs(r)
        _write_level(r, "L1", 0.36, fields=("U", "p", "Cx", "Cy"))
        ck("completion REFUSES: a declared field missing at endTime",
           _refuses(completion, r, "L1"))

        r = os.path.join(tmp, "bad_rc"); os.makedirs(r)
        _write_level(r, "L1", 0.36, rc="124")
        ck("completion REFUSES: a RECORDED non-zero rc (the cap fired)",
           _refuses(completion, r, "L1"))

        r = os.path.join(tmp, "no_rc"); os.makedirs(r)
        _write_level(r, "L1", 0.36, write_rc=False)
        c2 = completion(r, "L1")
        ck("completion PROCEEDS with rc NOT MEASURED when RUN_RC is absent (L-342)",
           c2["state"] == "COMPLETE" and c2["rc_status"] == "NOT MEASURED")

        r = os.path.join(tmp, "bad_exec"); os.makedirs(r)
        d, t = _write_level(r, "L1", 0.36)
        lp = os.path.join(d, "log.simpleFoam")
        fh = open(lp); s = fh.read(); fh.close()
        fh = open(lp, "w"); fh.write(s + "ExecutionTime = 9 s\n"); fh.close()
        ck("completion REFUSES: ExecutionTime count != iteration count",
           _refuses(completion, r, "L1"))

        r = os.path.join(tmp, "bad_tdir"); os.makedirs(r)
        d, t = _write_level(r, "L1", 0.36)
        os.makedirs(os.path.join(d, "9999"))
        ck("completion REFUSES: numerically-latest time dir disagrees with the log's last Time",
           _refuses(completion, r, "L1"))

        # ---- planted zero, both stages, both channels --------------------------
        pz = planted_zero_tau(good + "/L1", "1234")
        ck("planted zero P1a: the wall-shear reader SEES a sized all-face plant",
           pz["passed"] and pz["worst_readback_error"] < 1e-12)
        ck("planted zero P1b: the plant MOVES the gate functional upstream",
           pz["lr_planted"] is None or pz["lr_planted"] < pz["lr_unplanted"])
        pu = planted_zero_u(good + "/L1", "1234")
        ck("planted zero: the independent near-wall u_x channel sees its plant too",
           pu["passed"])

        blind = os.path.join(tmp, "blind"); os.makedirs(blind)
        _write_level(blind, "L1", 0.36, tau_scale=0.0)
        ck("planted zero REFUSES when the channel it must size against is identically zero",
           _refuses(planted_zero_tau, blind + "/L1", "1234"))

        saved = globals()["_plant_patch_vector_x"]
        globals()["_plant_patch_vector_x"] = lambda path, patch, delta: None
        ck("planted zero REFUSES against a BLIND writer (the plant never reaches disk) -- "
           "the control is shown able to fail",
           _refuses(planted_zero_tau, good + "/L1", "1234"))
        globals()["_plant_patch_vector_x"] = saved

        # ---- Roache, every state ----------------------------------------------
        ck("roache CONVERGING on a 2nd-order sequence",
           roache(4.40, 4.10, 4.025)["state"] == "CONVERGING")
        ck("roache DIVERGENT", roache(4.0, 4.1, 4.3)["state"] == "DIVERGENT")
        ck("roache OSCILLATORY", roache(4.0, 4.2, 4.1)["state"] == "OSCILLATORY")
        ck("roache STAGNANT (one difference exactly zero)",
           roache(4.0, 4.0, 4.1)["state"] == "STAGNANT")
        ck("roache EXACT (both differences zero)",
           roache(4.0, 4.0, 4.0)["state"] == "EXACT")
        tri_pf = roache(4.0, 4.10, 4.199)      # R = 0.99 -> p = 0.0145, below P_MIN = 0.05
        ck("roache: observed order below P_MIN is STAGNANT with NO GCI quoted",
           tri_pf["state"] == "STAGNANT" and tri_pf["gci_fine"] is None)
        tri_c = roache(4.40, 4.10, 4.025)
        ck("roache: p = 2 recovered on an exactly-2nd-order sequence",
           abs(tri_c["p"] - 2.0) < 1e-9)
        ck("roache: GCI at Fs=1.25 on that triple",
           abs(tri_c["gci_fine"] - (1.25 * abs(-0.075 / 4.025) / 3.0)) < 1e-12)
        for st in ("EXACT", "STAGNANT", "OSCILLATORY", "DIVERGENT"):
            ck("NO GCI is quoted when the triple is %s" % st,
               roache(*{"EXACT": (4.0, 4.0, 4.0), "STAGNANT": (4.0, 4.0, 4.1),
                        "OSCILLATORY": (4.0, 4.2, 4.1),
                        "DIVERGENT": (4.0, 4.1, 4.3)}[st])["gci_fine"] is None)

        # ---- verdicts ----------------------------------------------------------
        ck("limb A: CONVERGING + inside band -> GATE REACHED (never PASS)",
           verdict_for_limb_a(tri_c, True)[0] == "GATE REACHED")
        ck("limb A: CONVERGING + outside band -> GATE FAIL",
           verdict_for_limb_a(tri_c, False)[0] == "GATE FAIL")
        ck("limb A: rule 5 is ONE-WAY -- a non-CONVERGING triple is NOT A RESULT even when "
           "the value sits inside the band",
           verdict_for_limb_a(roache(4.0, 4.2, 4.1), True)[0] == "NOT A RESULT")
        ck("limb A can never emit PASS on any triple state",
           all(verdict_for_limb_a(roache(*trp), ins)[0] != "PASS"
               for trp in ((4.40, 4.10, 4.025), (4.0, 4.2, 4.1), (4.0, 4.0, 4.0),
                           (4.0, 4.1, 4.3), (4.0, 4.0, 4.1))
               for ins in (True, False)))
        ck("limb B: identical twin -> PASS (a SAME-DISCRETE-PROBLEM identity claim)",
           verdict_for_limb_b(True, "d")[0] == "PASS")
        ck("limb B: any difference -> GATE FAIL",
           verdict_for_limb_b(False, "d")[0] == "GATE FAIL")
        ck("ROW verdict is the WORST limb: GATE REACHED + PASS -> GATE REACHED",
           row_verdict([("A", "GATE REACHED"), ("B", "PASS")]) == "GATE REACHED")
        ck("ROW verdict: NOT A RESULT dominates a PASS limb",
           row_verdict([("A", "NOT A RESULT"), ("B", "PASS")]) == "NOT A RESULT")
        ck("ROW verdict can NEVER be PASS while limb A is capped at GATE REACHED",
           all(row_verdict([("A", a), ("B", b)]) != "PASS"
               for a in ("GATE REACHED", "GATE FAIL", "NOT A RESULT")
               for b in ("PASS", "GATE FAIL")))

        # ---- determinism limb --------------------------------------------------
        det = os.path.join(tmp, "det"); os.makedirs(det)
        _write_level(det, "L1", 0.36)
        _write_level(det, "L1D", 0.36)
        _p1, h1 = sha256_file(os.path.join(det, "L1", "1234", "wallShearStress"), "a")
        _p2, h2 = sha256_file(os.path.join(det, "L1D", "1234", "wallShearStress"), "b")
        ck("determinism limb: byte-identical twins hash the same", h1 == h2)
        det2 = os.path.join(tmp, "det2"); os.makedirs(det2)
        _write_level(det2, "L1", 0.36)
        _write_level(det2, "L1D", 0.3600001)
        _p3, h3 = sha256_file(os.path.join(det2, "L1D", "1234", "wallShearStress"), "c")
        ck("determinism limb: a ONE-PART-IN-3.6e6 difference is DETECTED (the limb can fail)",
           h3 != h1)

        # ---- cross-instrument agreement ---------------------------------------
        lr_t = last_sign_change_in_window(xs, tau)
        lr_u = last_sign_change_in_window(xs, [1.0e-3 * math.tanh((x - 0.36) / 0.09) for x in xs])
        ck("cross-instrument: wall shear and near-wall u_x agree well inside 3 cell widths",
           abs(lr_t - lr_u) < CROSS_TOL_CELLS * local_dx_at(xs, lr_t))
        ck("cross-instrument: a 10-cell displacement would be REJECTED",
           not (10.0 * local_dx_at(xs, lr_t) < CROSS_TOL_CELLS * local_dx_at(xs, lr_t)))

        # ---- the frozen reference and band are what the manual says ------------
        ck("reference is the manual's Target 4.0 (Lane & Loehrke 1980, EXPERIMENTAL)",
           REF_LR2T == 4.0)
        ck("band is the frozen 10 %", TOL == 0.10)
        ck("Ansys's own numbers are carried as CONTEXT and are not the gate",
           ANSYS_FLUENT_LR2T == 4.16 and ANSYS_CFX_LR2T == 4.05 and
           ANSYS_FLUENT_LR2T != REF_LR2T)
        ck("Re_2t from the frozen constants reproduces the manual's stated 260",
           abs(U_INF * TWO_T / NU - RE_2T) / RE_2T < 2.0e-4)
        ck("tier ceilings are declared: limb A GATE REACHED, limb B PASS",
           TIER_CEILING_A == "GATE REACHED" and TIER_CEILING_B == "PASS")
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
    """Hash this file and the pre-registration on disk against their HEAD blobs."""
    import subprocess
    repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if not repo:
        raise SystemExit2("--verify-frozen: not inside a git repository")
    rc = 0
    for rel in ("cases/ansys_verification/VMFL063/PREREGISTRATION.md",
                "cases/ansys_verification/VMFL063/grade_vmfl063.py"):
        disk = subprocess.run(["git", "-C", repo, "hash-object", os.path.join(repo, rel)],
                              capture_output=True, text=True).stdout.strip()
        head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD:" + rel],
                              capture_output=True, text=True).stdout.strip()
        # `git rev-parse` echoes its argument when the path is not at HEAD, so a
        # non-40-hex answer is NOT a blob and must not be printed as one.
        if not re.match(r"^[0-9a-f]{40}$", head):
            head = ""
        same = bool(disk) and disk == head
        print("%-64s disk=%s head=%s %s" % (rel, disk or "?", head or "?",
                                            "OK" if same else "MISMATCH"))
        if not same:
            rc = 2
    return rc


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify-frozen" in argv:
        return verify_frozen()

    run_root = RUN_ROOT
    out_path = None
    for i, a in enumerate(argv):
        if a == "--run-root" and i + 1 < len(argv):
            run_root = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out_path = argv[i + 1]
    run_root = os.path.abspath(run_root)

    R = {"case": "VMFL063", "manual_page": 193,
         "title": "Separated Laminar Flow Over a Blunt Plate",
         "reference": {"quantity": "LR/(2t), non-dimensionalised reattachment length",
                       "value": REF_LR2T, "kind": "EXPERIMENTAL",
                       "source": "J.C. Lane, R.I. Loehrke, Transactions of ASME Vol.102 "
                                 "pp.494-496 (1980), via VM2026R1 Table .63.1",
                       "ansys_fluent_context_only": ANSYS_FLUENT_LR2T,
                       "ansys_cfx_context_only": ANSYS_CFX_LR2T},
         "band": TOL, "window": [X_WIN_LO, X_WIN_HI], "x_sign_ref": X_SIGN_REF,
         "tier_ceiling_limb_a": TIER_CEILING_A, "tier_ceiling_limb_b": TIER_CEILING_B,
         "field_classes": FIELD_CLASSES, "run_root": run_root, "levels": {}}

    # AST guard runs on the grading path too, not only in --selftest.
    R["ast_assert_count"] = _ast_guard()

    # ---- strict completion at every level, twin included ----------------------
    for lv in LEVELS + [DET_TWIN]:
        R["levels"][lv] = completion(run_root, lv)

    # ---- controls fire BEFORE any value is believed ---------------------------
    l1 = R["levels"]["L1"]
    R["planted_zero"] = [planted_zero_tau(l1["level_dir"], l1["time_dir"]),
                         planted_zero_u(l1["level_dir"], l1["time_dir"])]

    # ---- LIMB A: the physics ---------------------------------------------------
    vals = {}
    for lv in LEVELS:
        c = R["levels"][lv]
        x, tau, orec = wallshear_profile(c["level_dir"], c["time_dir"])
        lr = last_sign_change_in_window(x, tau)
        if lr is None:
            raise SystemExit2("%s: the plate-top wall shear has NO reversed-to-attached "
                              "crossing inside the frozen window (%g, %g] m -- the bubble "
                              "does not close in the window and there is no reattachment "
                              "length to grade" % (lv, X_WIN_LO, X_WIN_HI))
        lr_u = last_sign_change_in_window(*nearwall_u_profile(c["level_dir"], c["time_dir"]))
        if lr_u is None:
            raise SystemExit2("%s: the INDEPENDENT near-wall u_x instrument finds no "
                              "reversal in the window; the two instruments cannot be "
                              "compared and the value is not certified" % lv)
        dx = local_dx_at(x, lr)
        if not (abs(lr - lr_u) <= CROSS_TOL_CELLS * dx):
            raise SystemExit2("%s: CROSS-INSTRUMENT DISAGREEMENT -- wall shear gives LR = "
                              "%.9g m, near-wall u_x gives %.9g m, apart by %.9g m against a "
                              "tolerance of %g local cell widths (%.9g m)"
                              % (lv, lr, lr_u, abs(lr - lr_u), CROSS_TOL_CELLS,
                                 CROSS_TOL_CELLS * dx))
        c.update({"orientation": orec, "LR_m": lr, "LR_over_2t": lr / TWO_T,
                  "LR_nearwall_u_m": lr_u, "cross_instrument_gap_m": abs(lr - lr_u),
                  "cross_instrument_tol_m": CROSS_TOL_CELLS * dx,
                  "local_dx_m": dx, "n_plateTop_faces": len(x),
                  "crossing_census": count_sign_changes_in_window(x, tau)})
        vals[lv] = lr / TWO_T

    tri = roache(vals["L1"], vals["L2"], vals["L3"])
    R["triple"] = tri
    fine = vals["L3"]
    dev = abs(fine - REF_LR2T) / abs(REF_LR2T)
    inside = dev <= TOL
    R["limb_A"] = {"class": "CONTINUUM (VERIFICATION_CHARTER sec.2f.3)",
                   "LR_over_2t": {lv: vals[lv] for lv in LEVELS},
                   "finest": fine, "reference": REF_LR2T, "deviation_rel": dev,
                   "band": TOL, "inside": inside, "ceiling": TIER_CEILING_A}
    va, wa = verdict_for_limb_a(tri, inside)
    R["limb_A"]["verdict"], R["limb_A"]["why"] = va, wa

    # ---- LIMB B: serial determinism -------------------------------------------
    a, b = R["levels"]["L1"], R["levels"][DET_TWIN]
    same_time = (a["time_dir"] == b["time_dir"])
    hashes, ident = {}, same_time
    for f in ("wallShearStress", "U", "p"):
        _pa, ha = sha256_file(os.path.join(a["level_dir"], a["time_dir"], f), "L1 %s" % f)
        _pb, hb = sha256_file(os.path.join(b["level_dir"], b["time_dir"], f), "L1D %s" % f)
        hashes[f] = {"L1": ha, "L1D": hb, "identical": ha == hb}
        ident = ident and (ha == hb)
    xb, taub, _ob = wallshear_profile(b["level_dir"], b["time_dir"])
    lrb = last_sign_change_in_window(xb, taub)
    lr_equal = (lrb is not None and lrb == a["LR_m"])
    ident = ident and lr_equal
    detail = ("same converged iteration count: %s; sha256 identical on %s; LR bitwise equal: %s"
              % (same_time, ", ".join(f for f in hashes if hashes[f]["identical"]), lr_equal))
    R["limb_B"] = {"class": "SAME-DISCRETE-PROBLEM IDENTITY (VERIFICATION_CHARTER sec.2f.3)",
                   "twin": DET_TWIN, "same_iteration_count": same_time,
                   "sha256": hashes, "LR_L1_m": a["LR_m"], "LR_L1D_m": lrb,
                   "LR_bitwise_equal": lr_equal, "identical": ident,
                   "ceiling": TIER_CEILING_B}
    vb, wb = verdict_for_limb_b(ident, detail)
    R["limb_B"]["verdict"], R["limb_B"]["why"] = vb, wb

    R["verdict"] = row_verdict([("A", va), ("B", vb)])
    R["verdict_note"] = ("the ROW verdict is the WORST limb; limb A's ceiling is GATE "
                         "REACHED, so this row can never read PASS and is NOT a credential")

    print("VMFL063  (VM2026R1 p.193)  ROW VERDICT: %s" % R["verdict"])
    print("  limb A  CONTINUUM  LR/(2t) L1/L2/L3 = %.6f / %.6f / %.6f"
          % (vals["L1"], vals["L2"], vals["L3"]))
    print("          finest %.6f vs Target %.4g, deviation %.4f %% , band %.1f %%  -> %s"
          % (fine, REF_LR2T, 100.0 * dev, 100.0 * TOL, va))
    print("          triple %s, p = %s, GCI_fine = %s"
          % (tri["state"],
             "n/a" if tri["p"] is None else "%.6f" % tri["p"],
             "n/a" if tri["gci_fine"] is None else "%.6f" % tri["gci_fine"]))
    print("  limb B  IDENTITY   determinism L1 vs %s -> %s  (%s)" % (DET_TWIN, vb, detail))
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
