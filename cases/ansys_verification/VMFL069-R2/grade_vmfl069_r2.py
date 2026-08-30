#!/usr/bin/env python3
# =============================================================================
# VMFL069-R2 COMPARATOR -- Two Phase Poiseuille Flow
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 205.
#
# R2 SUCCESSOR to the CLOSED registration cases/ansys_verification/VMFL069/,
# whose interFoam died SIGFPE (rc 136) at t=69 under an uncontrolled Courant
# number (deltaT 1 s, adjustTimeStep no; Courant 1802 -> 2.87e9). R2 runs the
# SAME case with adjustTimeStep yes and a registered maxCo. THE GATE FUNCTIONALS
# ARE INHERITED BYTE-UNCHANGED FROM R1: the reference (derive_reference), the
# limbs (layer_means, l2_profile_error), the band (TOL = 0.01), the ceilings
# (TIER_CEILING all PASS), the Roache triple (roache, FS, RATIO, P_MIN) and the
# verdict path (verdict_for_limb) are identical to R1's -- they do not depend on
# the time-stepping. What R2 changes is confined to time-stepping run controls
# and the ONE completion clause that the adaptive step forces (see completion()).
#
# FROZEN INSTRUMENT (CLAUDE.md rule 2). Once the pre-registration commit exists
# this file is never edited; a departure is a NEW registration and a NEW row.
#
# WHAT IT GRADES -- three limbs, all of one class:
#   CONTINUUM-EXACT. The reference is the EXACT solution of the SAME continuum
#   model interFoam discretises: steady incompressible Navier-Stokes with a
#   piecewise-constant viscosity and a flat, non-deforming interface, which is
#   the model the manual itself declares ("The flow is steady", "Deformation of
#   the interface is not modeled", p.205). Model-form error is therefore ZERO BY
#   CONSTRUCTION and the residual is discretisation error.
#     limb A -- volume-mean u_x over the LOWER layer (nu = 0.1) vs 10 m/s exactly
#     limb B -- volume-mean u_x over the UPPER layer (nu = 0.02) vs 50/3 m/s
#     limb C -- normalised L2 error of the whole cell-centre profile vs the exact
#               solution, against a frozen band
#   Each limb carries a CONVERGING three-level r = 2 Roache triple (rule 5).
#   CEILING `PASS` for all three -- see PREREGISTRATION sec.3 for the ground and
#   for the two register precedents (rows #2 and #3). Rule 5 is ONE-WAY: a triple
#   that is not CONVERGING turns any limb into `NOT A RESULT` whatever its value.
#
# NO `assert` STATEMENT APPEARS IN THIS FILE. `python3 -O` deletes every assert,
# so a control written as an assert is not a control (L-332). `_ast_guard()`
# walks this file's own AST and REFUSES if the ast.Assert count is not 0.
#
# EVERY file read goes through `one_match()`, which REFUSES unless the pattern
# matches EXACTLY ONE path. No `sorted(glob.glob(...))[-1]` appears anywhere:
# this case WRITES time directories 500 and 1000, whose LEXICOGRAPHIC maximum is
# `500` (since "1000" < "500" lexicographically) and whose NUMERIC maximum is
# `1000` -- the 19-site hazard of this territory, still live in this very case.
# `numeric_latest_time_dir()` sorts with key=float AND is cross-checked against
# the solver log's own last Time.
# =============================================================================

import os, re, sys, json, math, glob, shutil, tempfile, ast, hashlib

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL069-R2")

# ----------------------------------------------------------- FROZEN CONSTANTS --
# Manual p.205, Materials/Geometry/Boundary Conditions table.
LX        = 2.0             # streamwise extent, m  (CYCLIC pair)
H         = 4.0             # channel height, m
Y_IFACE   = 2.0             # interface, "half of the height of the channel"
NU_LOWER  = 0.1             # manual "Kinematic Viscosity Fluid-1 = 0.1"
NU_UPPER  = 0.02            # manual "Fluid-2 = 0.02"
RHO       = 1.0             # manual: "same density"; VALUE NOT PRINTED -> declared
GRAD      = 0.5             # -dp/dx, Pa/m, manual "Pressure Gradient = -0.5 Pa/m"

MU_LOWER  = RHO * NU_LOWER
MU_UPPER  = RHO * NU_UPPER

# The exact solution's derived constants, to double precision. `derive_reference()`
# re-derives all of these from the stated problem WITHOUT using them, and the
# selftest requires agreement to 1e-12 -- so these numbers are checked, not trusted.
REF_LOWER = 10.0                      # volume mean of u_x over 0 <= y < 2, m/s
REF_UPPER = 50.0 / 3.0                # volume mean of u_x over 2 < y <= 4, m/s
REF_WHOLE = 40.0 / 3.0                # volume mean over the whole channel, m/s
REF_UIFACE = 50.0 / 3.0               # u_x at the interface, m/s (diagnostic)
REF_TAU_LOWER_WALL =  4.0 / 3.0       # mu du/dy at y = 0,  Pa (diagnostic)
REF_TAU_UPPER_WALL = -2.0 / 3.0       # mu du/dy at y = H,  Pa (diagnostic)

TOL       = 0.01            # THE FROZEN BAND, relative, SAME for all three limbs

FS        = 1.25            # Roache safety factor
RATIO     = 2.0             # grid refinement ratio, BOTH directions
P_MIN     = 0.05            # observed-order floor (FINDING_p_floor.md sec.4)

ENDTIME       = 1000        # s (R1 was 2000). Under adjustTimeStep yes the STEP
                            # COUNT no longer equals this number; completion()
                            # checks last Time == ENDTIME plus log self-consistency
                            # (ExecutionTime count == Time-line count). See the
                            # rule-4 clause-5 ADAPTATION in completion().
PLATEAU_TIME  = 500         # s, the previous written time (R1 was 1500)
MAXCO         = 1.0         # registered Courant ceiling (R1 ran adjustTimeStep no,
                            # so its maxCo limited nothing and it blew up)
MAXALPHACO    = 1.0         # registered interface Courant ceiling
PLATEAU_TOL   = 1.0e-6      # rule 5 limb (1): the solve must have PLATEAUED
ALPHA_TOL     = 1.0e-9      # the interface must not have moved at all
XINVAR_TOL    = 1.0e-6      # the solution must be streamwise-invariant

K_PLANT_U     = 0.05        # plant size as a fraction of REF_WHOLE
K_PLANT_ALPHA = 0.05        # plant size on the alpha channel
PLANT_MIN_ABS = 1.0e-12

LEVELS = ["L1", "L2", "L3"]
NX = {"L1": 8,  "L2": 16, "L3": 32}
NY = {"L1": 32, "L2": 64, "L3": 128}

FIELDS      = ("U", "p_rgh", "alpha.fluid1", "Cx", "Cy")
AGE_DATUM   = "0/U"
ALPHA_FIELD = "alpha.fluid1"

# The class and the ceiling, declared here and enforced by verdict_for_limb().
LIMB_CLASS   = "CONTINUUM-EXACT (exact solution of the SAME continuum model)"
TIER_CEILING = {"A": "PASS", "B": "PASS", "C": "PASS"}

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT")
ORDER = {"NOT A RESULT": 0, "GATE FAIL": 1, "GATE REACHED": 2, "PASS": 3}

# The line fvOptions.C:86-91 prints ONLY when the file was actually read. If
# neither constant/fvOptions nor system/fvOptions exists the solver applies
# NOTHING and does NOT error (fvOptions.C:50-93, read at source). A silently
# unforced run would be a quiet zero-velocity case that looks like physics.
FVOPT_MARKS = ("Creating finite-volume options from",
               "constant/fvOptions",
               "Source: streamwisePressureGradient",
               "State: active")

FIELD_CLASSES = {
    "physics_critical": ["log.interFoam", "U", "p_rgh", ALPHA_FIELD, "Cx", "Cy",
                         "system/controlDict"],
    "infrastructure":   ["RUN_RC.<level>"],
}


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSING (exit 2): %s\n" % msg)
        SystemExit.__init__(self, 2)


# ------------------------------------------------- THE CARDINALITY GUARD -------
def one_match(pattern, what):
    """THE ONLY WAY THIS COMPARATOR OPENS A FILE. Returns the single path matching
    `pattern` and REFUSES (exit 2) on any other cardinality."""
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
    This case writes 500/1000/1500/2000, whose lexicographic maximum is `500`."""
    names = []
    for d in glob.glob(os.path.join(level_dir, "*")):
        if not os.path.isdir(d):
            continue
        b = os.path.basename(d)
        if re.match(r"^[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$", b):
            names.append((float(b), b))
    if not names:
        return None, None, None
    names.sort(key=lambda t: t[0])
    lexi = sorted(n for _v, n in names)[-1]
    return names[-1][1], names[-1][0], lexi


# --------------------------------------------------------------- OF readers ----
_INT_VEC_RE = re.compile(
    r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", re.S)
_INT_SCA_RE = re.compile(
    r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", re.S)


def read_internal_scalar(pattern, what):
    p, txt = read_text(pattern, what)
    m = _INT_SCA_RE.search(txt)
    if not m:
        raise SystemExit2("no nonuniform internalField scalar list in %s (%s)" % (p, what))
    vals = [float(v) for v in m.group(2).split()]
    if len(vals) != int(m.group(1)):
        raise SystemExit2("scalar count mismatch in %s: header %s, parsed %d"
                          % (p, m.group(1), len(vals)))
    return vals


def read_internal_vector_x(pattern, what):
    p, txt = read_text(pattern, what)
    m = _INT_VEC_RE.search(txt)
    if not m:
        raise SystemExit2("no nonuniform internalField vector list in %s (%s)" % (p, what))
    trip = re.findall(r"\(([^()]*)\)", m.group(2))
    if len(trip) != int(m.group(1)):
        raise SystemExit2("vector count mismatch in %s: header %s, parsed %d"
                          % (p, m.group(1), len(trip)))
    return [float(t.split()[0]) for t in trip]


# --------------------------------------------- in-place planting on REAL bytes --
def _plant_internal_vector_x(path, delta):
    """Add `delta` to the x-component of EVERY internal cell, in place, on the real
    file bytes -- not on a parsed copy in memory."""
    fh = open(path, errors="replace")
    try:
        txt = fh.read()
    finally:
        fh.close()
    m = _INT_VEC_RE.search(txt)
    if not m:
        raise SystemExit2("plant: no internalField vector list in %s" % path)
    body = m.group(2)

    def bump(mo):
        c = mo.group(1).split()
        c[0] = repr(float(c[0]) + delta)
        return "(" + " ".join(c) + ")"

    new = re.sub(r"\(([^()]*)\)", bump, body)
    out = txt[:m.start(2)] + new + txt[m.end(2):]
    fh = open(path, "w")
    try:
        fh.write(out)
    finally:
        fh.close()


def _plant_internal_scalar(path, delta):
    fh = open(path, errors="replace")
    try:
        txt = fh.read()
    finally:
        fh.close()
    m = _INT_SCA_RE.search(txt)
    if not m:
        raise SystemExit2("plant: no internalField scalar list in %s" % path)
    new = " ".join(repr(float(v) + delta) for v in m.group(2).split())
    out = txt[:m.start(2)] + "\n" + new + "\n" + txt[m.end(2):]
    fh = open(path, "w")
    try:
        fh.write(out)
    finally:
        fh.close()


def _blind_plant_vector_x(path, delta):
    """A WRITER THAT DOES NOT WRITE. The negative control for the planted-zero
    control itself: if the plant never reaches disk, the control MUST refuse.
    L-314: a guard is not adopted until it has been shown to fire on known-bad
    input AND to stay quiet on known-good."""
    return None


def _blind_plant_scalar(path, delta):
    return None


# ---------------------------------------------------- THE EXACT SOLUTION -------
def _solve3(A, b):
    """Gaussian elimination with partial pivoting. Pure Python: this comparator
    has NO third-party dependency, so the reference cannot silently depend on a
    library version."""
    n = 3
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1.0e-300:
            raise SystemExit2("reference derivation: singular system at column %d" % c)
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def derive_reference():
    """Re-derive the exact solution FROM THE STATED PROBLEM, using none of the
    frozen REF_* constants. The selftest compares the two and refuses on any
    disagreement above 1e-12, so the frozen numbers are CHECKED, not asserted.

        mu_i u_i'' = dp/dx = -GRAD                        in each layer
        u_lower(0) = 0 ; u_upper(H) = 0                   no slip
        u_lower(Y) = u_upper(Y)                           velocity continuity
        mu_lo u_lower'(Y) = mu_up u_upper'(Y)             stress continuity

    with u_lower = -(G/(2 mu_lo)) y^2 + aL y  and
         u_upper = -(G/(2 mu_up)) y^2 + aU y + bU."""
    G, Y = GRAD, Y_IFACE
    kL, kU = G / (2.0 * MU_LOWER), G / (2.0 * MU_UPPER)
    # unknowns (aL, aU, bU)
    A = [[Y,        -Y,   -1.0],          # continuity
         [MU_LOWER, -MU_UPPER, 0.0],      # stress continuity (the -G*Y terms cancel)
         [0.0,       H,    1.0]]          # u_upper(H) = 0
    b = [kL * Y * Y - kU * Y * Y,
         0.0,
         kU * H * H]
    aL, aU, bU = _solve3(A, b)

    def u_lo(y):
        return -kL * y * y + aL * y

    def u_up(y):
        return -kU * y * y + aU * y + bU

    mean_lo = (-kL * Y ** 3 / 3.0 + aL * Y ** 2 / 2.0) / Y
    IU_hi = -kU * H ** 3 / 3.0 + aU * H ** 2 / 2.0 + bU * H
    IU_lo = -kU * Y ** 3 / 3.0 + aU * Y ** 2 / 2.0 + bU * Y
    mean_up = (IU_hi - IU_lo) / (H - Y)
    mean_all = (Y * mean_lo + (H - Y) * mean_up) / H
    tau_bot = MU_LOWER * (-2.0 * kL * 0.0 + aL)
    tau_top = MU_UPPER * (-2.0 * kU * H + aU)
    return {"aL": aL, "aU": aU, "bU": bU,
            "u_lower": u_lo, "u_upper": u_up,
            "mean_lower": mean_lo, "mean_upper": mean_up, "mean_whole": mean_all,
            "u_interface_lower": u_lo(Y), "u_interface_upper": u_up(Y),
            "tau_interface_lower": MU_LOWER * (-2.0 * kL * Y + aL),
            "tau_interface_upper": MU_UPPER * (-2.0 * kU * Y + aU),
            "tau_bottom_wall": tau_bot, "tau_top_wall": tau_top}


_REF = derive_reference()


def exact_u(y):
    """u_x of the exact solution at height y."""
    return _REF["u_lower"](y) if y <= Y_IFACE else _REF["u_upper"](y)


# --------------------------------------------------------- the gate functionals
def layer_means(cy, ux):
    """Volume means over the two layers. The mesh is UNIFORM at every level and
    the interface lies on a cell FACE, so every cell has the same volume and the
    arithmetic mean over a layer's cells IS its volume mean, exactly."""
    lo = [u for y, u in zip(cy, ux) if y < Y_IFACE]
    hi = [u for y, u in zip(cy, ux) if y > Y_IFACE]
    if not lo or not hi:
        raise SystemExit2("layer_means: one layer holds no cells (lower %d, upper %d) -- "
                          "the interface is not inside the mesh" % (len(lo), len(hi)))
    if len(lo) + len(hi) != len(cy):
        raise SystemExit2("layer_means: %d of %d cell centres lie EXACTLY on the "
                          "interface y = %g; the split is ambiguous"
                          % (len(cy) - len(lo) - len(hi), len(cy), Y_IFACE))
    return sum(lo) / len(lo), sum(hi) / len(hi), sum(ux) / len(ux)


def l2_profile_error(cy, ux):
    """Normalised L2 error of the whole cell-centre profile against the exact
    solution. EVERY cell enters, which is what makes an all-cell plant visible to
    it (L-340: an averaging reader dilutes a single-point plant by ~1/sqrt(N))."""
    s = 0.0
    for y, u in zip(cy, ux):
        d = u - exact_u(y)
        s += d * d
    return math.sqrt(s / len(ux)) / abs(REF_WHOLE)


def check_alpha_stationary(cy, alpha):
    """The interface must not have moved AT ALL. With equal densities, zero
    surface tension and a flat interface parallel to U, the alpha field is an
    EXACT steady state of the VOF system and its interface Courant number is
    identically zero. If MULES moved it, the case that ran is not the case that
    was registered."""
    worst, where = 0.0, None
    for y, a in zip(cy, alpha):
        want = 1.0 if y < Y_IFACE else 0.0
        d = abs(a - want)
        if d > worst:
            worst, where = d, y
    if worst > ALPHA_TOL:
        raise SystemExit2("INTERFACE MOVED: max |alpha - alpha_0| = %.12g at y = %s, above "
                          "the frozen %g. The registered case has a NON-DEFORMING interface "
                          "(manual p.205); a run whose interface moved did not solve it."
                          % (worst, where, ALPHA_TOL))
    return worst


def check_x_invariance(cx, cy, ux):
    """The exact solution is streamwise-invariant. Cyclic streamwise patches plus
    a uniform body force admit nothing else, so any x-variation is a defect (a
    broken cyclic pair, a transitional instability, a misapplied source)."""
    rows = {}
    for y, u in zip(cy, ux):
        rows.setdefault(round(y, 12), []).append(u)
    worst, where = 0.0, None
    for y, us in rows.items():
        d = (max(us) - min(us)) / abs(REF_WHOLE)
        if d > worst:
            worst, where = d, y
    if worst > XINVAR_TOL:
        raise SystemExit2("STREAMWISE INVARIANCE BROKEN: the widest spread of u_x within a "
                          "single y-row is %.12g of the reference mean (at y = %s), above the "
                          "frozen %g. The registered solution is x-invariant."
                          % (worst, where, XINVAR_TOL))
    return worst, len(rows)


def check_mesh_structure(cx, cy, level):
    """The mesh must be the registered one: NX x NY uniform, interface on a FACE."""
    nrows = len(set(round(y, 12) for y in cy))
    ncols = len(set(round(x, 12) for x in cx))
    if nrows != NY[level] or ncols != NX[level]:
        raise SystemExit2("MESH IS NOT THE REGISTERED ONE at %s: %d distinct y-rows and %d "
                          "distinct x-columns, registered %d x %d"
                          % (level, nrows, ncols, NX[level], NY[level]))
    if len(cy) != NX[level] * NY[level]:
        raise SystemExit2("MESH CELL COUNT at %s is %d, registered %d"
                          % (level, len(cy), NX[level] * NY[level]))
    for y in cy:
        if abs(y - Y_IFACE) < 1.0e-9:
            raise SystemExit2("a cell CENTRE lies on the interface y = %g at %s -- the "
                              "interface must lie on a cell FACE (NY must be even)"
                              % (Y_IFACE, level))
    nlo = sum(1 for y in cy if y < Y_IFACE)
    if nlo * 2 != len(cy):
        raise SystemExit2("the interface does not halve the mesh at %s: %d of %d cells below"
                          % (level, nlo, len(cy)))
    return {"rows": nrows, "cols": ncols, "cells": len(cy), "cells_below": nlo}


def read_state(level_dir, t, level):
    """Read one written time and return everything the limbs need."""
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"), "Cx at %s/%s" % (level, t))
    cy = read_internal_scalar(os.path.join(level_dir, t, "Cy"), "Cy at %s/%s" % (level, t))
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"), "U at %s/%s" % (level, t))
    if not (len(cx) == len(cy) == len(ux)):
        raise SystemExit2("field length mismatch at %s/%s: Cx %d, Cy %d, U %d"
                          % (level, t, len(cx), len(cy), len(ux)))
    return cx, cy, ux


# ---------------------------------------------------- planted-zero (rule 3) ----
def planted_zero_u(level_dir, t, level, cy_ref, writer=_plant_internal_vector_x):
    """CLAUDE.md rule 3 on the VELOCITY channel, in the two-stage form this
    territory's two lost rungs demand.

    P1a -- READER SENSITIVITY. A SIZED plant is applied to the x-component of
           EVERY internal cell of a COPY of the real solver file, on the real
           bytes, and read back FROM DISK through the real reader. Sized, because
           an averaging reader dilutes a fixed single-point plant by ~1/sqrt(N)
           (L-340, register row #26). Every cell, because a correctly sized point
           plant can land outside the reader's support (L-347, row #31).

    P1b -- GATE-FUNCTIONAL SENSITIVITY. The SAME planted file is pushed through
           the FULL gate functional. The planted lower-layer mean must move by
           exactly the plant AND must fall OUTSIDE the frozen band, and the
           planted L2 profile error must RISE. A plant the raw reader sees but
           the gate does not is exactly the row-#31 failure and it refuses here."""
    src = one_match(os.path.join(level_dir, t, "U"), "plant source U at %s" % level)
    tmp = tempfile.mkdtemp(prefix="vmfl069_plant_u_")
    try:
        dst = os.path.join(tmp, "U")
        shutil.copy(src, dst)
        base = read_internal_vector_x(dst, "planted-copy baseline U")
        plant = K_PLANT_U * abs(REF_WHOLE)
        if plant <= PLANT_MIN_ABS:
            raise SystemExit2("planted-zero: the sized plant %.12g is below the floor" % plant)
        writer(dst, plant)
        seen = read_internal_vector_x(dst, "planted-copy read-back U")
        if len(seen) != len(base):
            raise SystemExit2("planted-zero: internal cell count changed across the U plant")
        worst = max(abs((seen[i] - base[i]) - plant) for i in range(len(base)))
        if not (worst <= 1.0e-9 * max(abs(plant), 1.0)):
            raise SystemExit2(
                "planted-zero control FAILED (P1a, reader sensitivity) on the VELOCITY "
                "channel: planted %.12g into EVERY internal cell of %s and the worst "
                "read-back discrepancy is %.12g. A reader not shown able to see a non-zero "
                "cannot certify a zero (CLAUDE.md rule 3)." % (plant, src, worst))
        # P1b -- the FULL gate functional, not the raw reader
        m_lo_0, m_up_0, _w0 = layer_means(cy_ref, base)
        m_lo_1, m_up_1, _w1 = layer_means(cy_ref, seen)
        e0 = l2_profile_error(cy_ref, base)
        e1 = l2_profile_error(cy_ref, seen)
        moved = abs((m_lo_1 - m_lo_0) - plant) <= 1.0e-9 * max(abs(plant), 1.0)
        inside_0 = abs(m_lo_0 - REF_LOWER) / abs(REF_LOWER) <= TOL
        inside_1 = abs(m_lo_1 - REF_LOWER) / abs(REF_LOWER) <= TOL
        if not moved:
            raise SystemExit2(
                "planted-zero control FAILED (P1b) on the VELOCITY channel: the raw reader "
                "saw the plant but the LIMB-A FUNCTIONAL did not move by it (%.12g -> %.12g, "
                "plant %.12g)." % (m_lo_0, m_lo_1, plant))
        if inside_1:
            raise SystemExit2(
                "planted-zero control FAILED (P1b) on the VELOCITY channel: the planted "
                "lower-layer mean %.12g is STILL inside the frozen %.4g band about %.12g. A "
                "plant that cannot move the gate across its own threshold does not show the "
                "gate can see one." % (m_lo_1, TOL, REF_LOWER))
        if not (e1 > e0 + PLANT_MIN_ABS):
            raise SystemExit2(
                "planted-zero control FAILED (P1b) on the VELOCITY channel: the L2 profile "
                "error did not rise under the plant (%.12g -> %.12g)." % (e0, e1))
        return {"channel": "U_x", "passed": True, "plant": plant, "file": src,
                "n_cells": len(base), "worst_readback_error": worst,
                "mean_lower_unplanted": m_lo_0, "mean_lower_planted": m_lo_1,
                "mean_upper_unplanted": m_up_0, "mean_upper_planted": m_up_1,
                "band_inside_unplanted": inside_0, "band_inside_planted": inside_1,
                "l2_unplanted": e0, "l2_planted": e1,
                "gate_response": "limb A moved by exactly the plant and left the band; "
                                 "limb C rose"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def planted_zero_alpha(level_dir, t, level, cy_ref, writer=_plant_internal_scalar):
    """The same two-stage control on the INDEPENDENT alpha channel, whose gate
    functional is the interface-stationarity clause. P1b here is: the planted file
    must make check_alpha_stationary REFUSE."""
    src = one_match(os.path.join(level_dir, t, ALPHA_FIELD), "plant source alpha at %s" % level)
    tmp = tempfile.mkdtemp(prefix="vmfl069_plant_a_")
    try:
        dst = os.path.join(tmp, ALPHA_FIELD)
        shutil.copy(src, dst)
        base = read_internal_scalar(dst, "planted-copy baseline alpha")
        plant = K_PLANT_ALPHA
        writer(dst, plant)
        seen = read_internal_scalar(dst, "planted-copy read-back alpha")
        if len(seen) != len(base):
            raise SystemExit2("planted-zero: cell count changed across the alpha plant")
        worst = max(abs((seen[i] - base[i]) - plant) for i in range(len(base)))
        if not (worst <= 1.0e-9 * max(abs(plant), 1.0)):
            raise SystemExit2(
                "planted-zero control FAILED (P1a) on the ALPHA channel: planted %.12g into "
                "EVERY cell of %s, worst read-back discrepancy %.12g (CLAUDE.md rule 3)."
                % (plant, src, worst))
        fired = False
        try:
            check_alpha_stationary(cy_ref, seen)
        except SystemExit as e:
            fired = (getattr(e, "code", None) == 2)
        if not fired:
            raise SystemExit2(
                "planted-zero control FAILED (P1b) on the ALPHA channel: the raw reader saw "
                "the plant but the INTERFACE-STATIONARITY CLAUSE did not refuse. A plant the "
                "raw reader sees and the deciding clause does not is L-347's failure.")
        return {"channel": ALPHA_FIELD, "passed": True, "plant": plant, "file": src,
                "n_cells": len(base), "worst_readback_error": worst,
                "gate_response": "the interface-stationarity clause REFUSED on the planted file"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------- strict completion --
def completion(run_root, level):
    """CLAUDE.md rule 4 IN FULL for a TRANSIENT run, plus this case's own clauses.

    PHYSICS-CRITICAL -- each gates, any failure REFUSES (exit 2):
      * an `End` line in log.interFoam                    (exact name, one_match)
      * the fvOptions markers                             (the source WAS read)
      * the controlDict carries adjustTimeStep yes and the registered maxCo /
        maxAlphaCo (R1's adjustTimeStep-no run blew up; R2 REQUIRES the control)
      * last Time == endTime                              (literal rule 4, UNCHANGED)
      * ExecutionTime count == the Time-line count        (RULE-4 CLAUSE-5
        ADAPTATION: R1 required "ExecutionTime count == endTime", which held only
        because R1 fixed deltaT = 1 s so #steps == the numeric endTime. Under
        adjustTimeStep yes the step count is VARIABLE and does not equal endTime,
        so that numeric identity is unsatisfiable and is ADAPTED -- NOT waived --
        to log self-consistency: the count of ExecutionTime lines must equal the
        count of Time lines, so no advanced step went untimed or was truncated.
        Combined with "last Time == endTime" this is strictly stronger than the
        deltaT=1 artefact it replaces. Declared BEFORE compute in
        PREREGISTRATION-R2 sec.6, per VMFL063 sec.6 clause 4.)
      * every declared field present at endTime
      * the NUMERICALLY-latest time directory (key=float) == the log's last Time
      * AGE GUARD: every field at endTime strictly NEWER than the case's own 0/U,
        which the launcher touches LAST, immediately before the solver
      * PLATEAU: the limb quantities at t = 500 and t = 1000 agree (rule 5 limb 1)
      * the interface has not moved; the solution is x-invariant; the mesh is the
        registered one

    INFRASTRUCTURE (L-342): RUN_RC.<level>. ABSENT -> rc NOT MEASURED, disclosed,
    grade PROCEEDS on the physics artefacts. PRESENT AND non-zero -> REFUSE."""
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
                                  "non-zero rc is evidence about the SOLVER and refuses "
                                  "(L-342)." % (out["rc"], level))
        for key in ("wall_s", "core_min", "timeout_s"):
            mm = re.search(r"^\s*%s\s*=\s*([0-9.eE+-]+)" % key, rct, re.M)
            out[key] = float(mm.group(1)) if mm else None

    logp, lt = read_text(os.path.join(level_dir, "log.interFoam"), "solver log for %s" % level)
    out["log"] = logp
    out["end_lines"] = len(re.findall(r"^End\s*$", lt, re.M))
    if out["end_lines"] < 1:
        raise SystemExit2("no End line in %s" % logp)

    missing = [m for m in FVOPT_MARKS if m not in lt]
    if missing:
        raise SystemExit2(
            "fvOptions WAS NOT APPLIED at %s: the solver log is missing %r. OpenFOAM v2606 "
            "reads constant/fvOptions if present, system/fvOptions if not, and applies "
            "NOTHING WITHOUT AN ERROR if neither exists (fvOptions.C:50-93). The driving "
            "pressure gradient is the ONLY forcing in this case, so an unforced run is a "
            "quiet zero-velocity case that looks like physics." % (level, missing))
    out["fvOptions_markers"] = list(FVOPT_MARKS)

    times = [float(x) for x in re.findall(r"^Time = ([0-9.eE+-]+)", lt, re.M)]
    if not times:
        raise SystemExit2("no Time lines in %s" % logp)
    out["last_time"] = times[-1]
    out["n_steps_in_log"] = len(times)
    out["n_exec"] = lt.count("ExecutionTime")

    cdp, ctl = read_text(os.path.join(level_dir, "system", "controlDict"),
                         "controlDict for %s" % level)
    mE = re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    if not mE:
        raise SystemExit2("no endTime in %s" % cdp)
    out["endTime"] = float(mE.group(1))
    # deltaT is read for the record only: under adjustTimeStep yes it is the
    # INITIAL step, not a fixed step, and is NOT gated.
    mD = re.search(r"^deltaT\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    out["deltaT_initial"] = float(mD.group(1)) if mD else None
    # THE COURANT CONTROL IS REQUIRED. R1 ran adjustTimeStep no and its maxCo
    # limited nothing; it blew up. R2's completion refuses a run whose controlDict
    # does not carry the registered Courant control.
    mA = re.search(r"^adjustTimeStep\s+(\w+)\s*;", ctl, re.M)
    mC = re.search(r"^maxCo\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    mAC = re.search(r"^maxAlphaCo\s+([0-9.eE+-]+)\s*;", ctl, re.M)
    if not mA or mA.group(1) != "yes":
        raise SystemExit2("%s: adjustTimeStep is %r, not 'yes'. R1 died with adjustTimeStep "
                          "no and an uncontrolled Courant number; R2 REQUIRES the control."
                          % (cdp, None if not mA else mA.group(1)))
    if not mC or not mAC:
        raise SystemExit2("%s: maxCo/maxAlphaCo not both present" % cdp)
    out["adjustTimeStep"], out["maxCo"], out["maxAlphaCo"] = "yes", float(mC.group(1)), float(mAC.group(1))
    if out["endTime"] != float(ENDTIME):
        raise SystemExit2("%s carries endTime %g; the registered endTime is %g"
                          % (cdp, out["endTime"], float(ENDTIME)))
    if out["maxCo"] != float(MAXCO) or out["maxAlphaCo"] != float(MAXALPHACO):
        raise SystemExit2("%s carries maxCo %g maxAlphaCo %g; the registered pair is %g / %g"
                          % (cdp, out["maxCo"], out["maxAlphaCo"], float(MAXCO), float(MAXALPHACO)))
    if out["last_time"] != out["endTime"]:
        raise SystemExit2("%s: last Time %g != endTime %g -- the run did not reach the "
                          "registered end (CLAUDE.md rule 4)"
                          % (logp, out["last_time"], out["endTime"]))
    if out["n_exec"] != out["n_steps_in_log"]:
        raise SystemExit2("%s: ExecutionTime count %d != Time-line count %d. RULE-4 CLAUSE-5 "
                          "ADAPTATION for adjustTimeStep yes (PREREGISTRATION-R2 sec.6): the "
                          "step count is variable and no longer equals endTime, so the "
                          "completion condition is log self-consistency -- every advanced step "
                          "was timed and none was lost -- combined with last Time == endTime."
                          % (logp, out["n_exec"], out["n_steps_in_log"]))

    t = str(int(out["endTime"]))
    out["time_dir"] = t
    nm, nv, lexi = numeric_latest_time_dir(level_dir)
    out["numeric_latest_time_dir"] = nm
    out["lexicographic_latest_time_dir"] = lexi
    out["lexicographic_would_have_misread"] = (lexi != nm)
    if nm is None or abs(nv - float(t)) > 1e-9:
        raise SystemExit2("time-directory disagreement at %s: the log's last Time is %s, the "
                          "numerically-latest directory (key=float) is %r, the LEXICOGRAPHIC "
                          "maximum is %r. A grader that takes sorted(glob())[-1] here reads "
                          "the wrong artefact." % (level_dir, t, nm, lexi))
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

    cx, cy, ux = read_state(level_dir, t, level)
    out["mesh"] = check_mesh_structure(cx, cy, level)
    alpha = read_internal_scalar(os.path.join(level_dir, t, ALPHA_FIELD),
                                 "alpha at %s/%s" % (level, t))
    out["alpha_max_drift"] = check_alpha_stationary(cy, alpha)
    out["x_invariance"], out["y_rows"] = check_x_invariance(cx, cy, ux)

    m_lo, m_up, m_all = layer_means(cy, ux)
    out["mean_lower"], out["mean_upper"], out["mean_whole"] = m_lo, m_up, m_all
    out["l2_error"] = l2_profile_error(cy, ux)

    # PLATEAU (rule 5 limb 1) -- against the previous written time
    tp = str(int(PLATEAU_TIME))
    # Only U is required at the plateau time: the mesh is static, so the cell
    # centres read at endTime are the SAME cell centres, and requiring Cx/Cy at a
    # second time would force a second writeCellCentres pass in the launcher for
    # no information. The length check below is what makes the reuse safe.
    uxp = read_internal_vector_x(os.path.join(level_dir, tp, "U"),
                                 "U at %s/%s (plateau time)" % (level, tp))
    if len(uxp) != len(cy):
        raise SystemExit2("plateau: U at %s/%s has %d cells, U at %s/%s has %d -- the mesh "
                          "changed between the two written times"
                          % (level, tp, len(uxp), level, t, len(cy)))
    p_lo, p_up, _p_all = layer_means(cy, uxp)
    d_lo = abs(m_lo - p_lo) / abs(m_lo)
    d_up = abs(m_up - p_up) / abs(m_up)
    out["plateau"] = {"time_a": tp, "time_b": t, "rel_change_lower": d_lo,
                      "rel_change_upper": d_up, "tol": PLATEAU_TOL}
    if d_lo > PLATEAU_TOL or d_up > PLATEAU_TOL:
        raise SystemExit2("NOT PLATEAUED at %s: the layer means changed by %.12g (lower) and "
                          "%.12g (upper) between t = %s and t = %s, above the frozen %g. Rule 5 "
                          "limb (1) makes a level that has not plateaued NOT A RESULT and it "
                          "is refused here rather than graded."
                          % (level, d_lo, d_up, tp, t, PLATEAU_TOL))
    out["cx"], out["cy"], out["ux"] = cx, cy, ux
    out["state"] = "COMPLETE"
    return out


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """CLAUDE.md rule 5. f1 coarse, f2 medium, f3 fine. A GCI is quoted ONLY on a
    CONVERGING (hence monotone) triple whose observed order clears P_MIN."""
    d32, d21 = f3 - f2, f2 - f1
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
    if f3 != 0.0:
        out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


# ------------------------------------------------------------------ verdicts ---
def verdict_for_limb(limb, tri, inside):
    """THE ONE verdict path for every limb. The planted controls DRIVE it, so they
    exercise the code that actually decides.

    Rule 5 is ONE-WAY: a non-CONVERGING triple can only turn a verdict INTO
    `NOT A RESULT`, never the reverse. The DECLARED CEILING is enforced: if this
    function ever emits a verdict ABOVE the ceiling the limb was registered with,
    it REFUSES rather than publish it."""
    ceiling = TIER_CEILING[limb]
    if ceiling not in VOCAB:
        raise SystemExit2("limb %s carries ceiling %r, outside the fixed vocabulary" % (limb, ceiling))
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
        v, why = ("PASS",
                  "inside the frozen %.4g band on a CONVERGING triple, against the EXACT "
                  "solution of the SAME continuum model the solver discretises -- model-form "
                  "error is zero by construction, so the residual is discretisation error and "
                  "rule 5 step 3 makes PASS available (PREREGISTRATION sec.3)." % TOL)
    else:
        v, why = ("GATE FAIL", "outside the frozen %.4g band on a CONVERGING triple" % TOL)
    if v not in VOCAB:
        raise SystemExit2("verdict %r is outside the fixed vocabulary (CLAUDE.md rule 1)" % v)
    if ORDER[v] > ORDER[ceiling]:
        raise SystemExit2("TIER CEILING VIOLATED: limb %s emitted %r, above the ceiling %r "
                          "declared for it in the frozen pre-registration" % (limb, v, ceiling))
    return v, why


def row_verdict(limbs):
    """The ROW verdict is the WORST limb, over the fixed ordering
    NOT A RESULT < GATE FAIL < GATE REACHED < PASS."""
    return min(limbs, key=lambda kv: ORDER[kv[1]])[1]


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


# ------------------------------------------------------------- the AST guard ---
def _ast_guard():
    """Walk THIS FILE's own AST and refuse if it contains any `assert`. `python3 -O`
    deletes every assert statement, so a control written as an assert exists under
    one interpreter and not the other, and a control that vanishes is not a
    control (L-332). The count is measured from the SOURCE, so it is the same
    under both interpreters -- which is the point."""
    src = open(os.path.abspath(__file__), errors="replace").read()
    n = sum(1 for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Assert))
    if n != 0:
        raise SystemExit2("AST GUARD: this comparator contains %d `assert` statement(s). "
                          "`python3 -O` deletes them, so they are not controls (L-332)." % n)
    return n


# --------------------------------------------- constructed-field writers -------
# Module level, so the selftest and the controls exercise the SAME builders and
# the SAME readers that grade a real run.
_HDR = ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        "    class       %s;\n    object      %s;\n}\n"
        "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")


def _write_scalar(path, obj, vals):
    fh = open(path, "w")
    try:
        fh.write(_HDR % ("volScalarField", obj))
        fh.write("dimensions      [0 0 0 0 0 0 0];\n\n")
        fh.write("internalField   nonuniform List<scalar> \n%d\n(\n" % len(vals))
        fh.write("\n".join(repr(float(v)) for v in vals))
        fh.write("\n)\n;\n\nboundaryField\n{\n}\n")
    finally:
        fh.close()


def _write_vector_x(path, obj, xs):
    fh = open(path, "w")
    try:
        fh.write(_HDR % ("volVectorField", obj))
        fh.write("dimensions      [0 1 -1 0 0 0 0];\n\n")
        fh.write("internalField   nonuniform List<vector> \n%d\n(\n" % len(xs))
        fh.write("\n".join("(%s 0 0)" % repr(float(v)) for v in xs))
        fh.write("\n)\n;\n\nboundaryField\n{\n}\n")
    finally:
        fh.close()


def _centres(level):
    nx, ny = NX[level], NY[level]
    dx, dy = LX / nx, H / ny
    cx, cy = [], []
    for j in range(ny):
        for i in range(nx):
            cx.append((i + 0.5) * dx)
            cy.append((j + 0.5) * dy)
    return cx, cy


def _log_text(endtime, nexec=None, lasttime=None, end_line=True, fvopt=True, exec_drop=0):
    # `nexec` sets the number of Time lines (a compressed stand-in for the many
    # thousands an adjustTimeStep-yes run really writes); each is normally paired
    # with one ExecutionTime line. `exec_drop` removes that many ExecutionTime
    # lines so the selftest can drive the RULE-4 CLAUSE-5 ADAPTATION guard
    # (ExecutionTime count == Time-line count) to a REFUSAL.
    n = int(endtime) if nexec is None else int(nexec)
    last = endtime if lasttime is None else lasttime
    L = ["Create time\n", "Create mesh for time = 0\n"]
    if fvopt:
        L.append('Creating finite-volume options from "constant/fvOptions"\n')
        L.append("Selecting finite volume options type vectorSemiImplicitSource\n")
        L.append("    Source: streamwisePressureGradient\n")
        L.append("    State: active\n")
    L.append("Starting time loop\n")
    exec_line = "ExecutionTime = 0.01 s  ClockTime = 0 s\n"
    for k in range(1, n):
        L.append("Time = %g\n" % k)
        L.append(exec_line)
    L.append("Time = %g\n" % last)
    L.append(exec_line)
    if exec_drop:
        removed = 0
        for i in range(len(L) - 1, -1, -1):
            if L[i] == exec_line:
                del L[i]
                removed += 1
                if removed >= exec_drop:
                    break
    if end_line:
        L.append("End\n")
    return "".join(L)


def _write_level(root, level, err=0.0, endtime=ENDTIME, nexec=None, lasttime=None,
                 end_line=True, fvopt=True, alpha_shift=0.0, xperturb=0.0,
                 plateau_shift=0.0, fields=FIELDS, times=(500, 1000),
                 age_ok=True, deltat=0.001, cells_override=None, exec_drop=0,
                 adjust="yes", maxco=MAXCO, maxalphaco=MAXALPHACO):
    """Build a synthetic level tree in OpenFOAM's own on-disk format. `err` scales a
    smooth perturbation added to the exact profile, so a selftest can drive the
    gate to either side of its band without ever touching a real run. The synthetic
    controlDict carries adjustTimeStep yes and the registered maxCo/maxAlphaCo, and
    the parameters `adjust`, `maxco`, `maxalphaco`, `exec_drop` let the selftest
    drive R2's new completion guards to REFUSALS."""
    d = os.path.join(root, level)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    fh = open(os.path.join(d, "0", "U"), "w")
    try:
        fh.write("age datum\n")
    finally:
        fh.close()
    fh = open(os.path.join(d, "system", "controlDict"), "w")
    try:
        fh.write("application     interFoam;\nendTime         %g;\ndeltaT          %g;\n"
                 "adjustTimeStep  %s;\nmaxCo           %g;\nmaxAlphaCo      %g;\nmaxDeltaT       1.0;\n"
                 % (endtime, deltat, adjust, maxco, maxalphaco))
    finally:
        fh.close()
    fh = open(os.path.join(d, "log.interFoam"), "w")
    try:
        fh.write(_log_text(endtime, nexec, lasttime, end_line, fvopt, exec_drop))
    finally:
        fh.close()

    cx, cy = _centres(level)
    if cells_override is not None:
        cx, cy = cells_override
    for t in times:
        td = os.path.join(d, str(t))
        os.makedirs(td, exist_ok=True)
        if t not in (PLATEAU_TIME, int(endtime)):
            continue
        shift = plateau_shift if t == PLATEAU_TIME else 0.0
        ux = [exact_u(y) * (1.0 + err + shift) for y in cy]
        if xperturb:
            ux = [u + (xperturb * abs(REF_WHOLE) if (i % NX[level]) == 0 else 0.0)
                  for i, u in enumerate(ux)]
        al = [(1.0 if y < Y_IFACE else 0.0) + alpha_shift for y in cy]
        if "U" in fields:
            _write_vector_x(os.path.join(td, "U"), "U", ux)
        if "Cx" in fields:
            _write_scalar(os.path.join(td, "Cx"), "Cx", cx)
        if "Cy" in fields:
            _write_scalar(os.path.join(td, "Cy"), "Cy", cy)
        if ALPHA_FIELD in fields:
            _write_scalar(os.path.join(td, ALPHA_FIELD), ALPHA_FIELD, al)
        if "p_rgh" in fields:
            _write_scalar(os.path.join(td, "p_rgh"), "p_rgh", [0.0] * len(cy))
        if not age_ok:
            old = os.path.getmtime(os.path.join(d, "0", "U")) - 100.0
            for f in os.listdir(td):
                os.utime(os.path.join(td, f), (old, old))
    return d


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


def _refusal_text(fn, *a, **k):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        try:
            fn(*a, **k)
        except SystemExit:
            pass
        except Exception:
            pass
    return buf.getvalue()


def selftest():
    print("SELFTEST VMFL069-R2 -- Two Phase Poiseuille Flow (VM2026R1 p.205)")

    ck("AST guard: ast.Assert count is 0 in this file", _ast_guard() == 0)

    tmp = tempfile.mkdtemp(prefix="vmfl069_selftest_")
    try:
        # ---- cardinality guard -----------------------------------------------
        os.makedirs(os.path.join(tmp, "card"))
        for n in ("only.txt",):
            fh = open(os.path.join(tmp, "card", n), "w"); fh.write("x"); fh.close()
        ck("one_match returns the single match",
           one_match(os.path.join(tmp, "card", "only.txt"), "t")
           == os.path.join(tmp, "card", "only.txt"))
        ck("one_match REFUSES on zero matches",
           _refuses(one_match, os.path.join(tmp, "card", "missing.txt"), "t"))
        fh = open(os.path.join(tmp, "card", "twin.txt"), "w"); fh.write("y"); fh.close()
        ck("one_match REFUSES on two matches",
           _refuses(one_match, os.path.join(tmp, "card", "*.txt"), "t"))

        # ---- the lexicographic hazard, DRIVEN on 0 / 950 / 2000 ---------------
        lx = os.path.join(tmp, "lexi")
        for n in ("0", "950", "2000", "notatime"):
            os.makedirs(os.path.join(lx, n))
        nm, nv, lexi = numeric_latest_time_dir(lx)
        ck("time dirs sort NUMERICALLY: 0/950/2000 -> 2000", nm == "2000" and nv == 2000.0)
        ck("the LEXICOGRAPHIC maximum of 0/950/2000 really is 950 (the live hazard)",
           lexi == "950")
        ck("non-numeric directory names are ignored by the time-dir reader",
           nm == "2000")

        # ---- the reference, re-derived and cross-checked ----------------------
        R = derive_reference()
        ck("derived lower-layer mean matches the frozen REF_LOWER to 1e-12",
           abs(R["mean_lower"] - REF_LOWER) <= 1e-12 * max(1.0, abs(REF_LOWER)))
        ck("derived upper-layer mean matches the frozen REF_UPPER to 1e-12",
           abs(R["mean_upper"] - REF_UPPER) <= 1e-12 * max(1.0, abs(REF_UPPER)))
        ck("derived whole-channel mean matches the frozen REF_WHOLE to 1e-12",
           abs(R["mean_whole"] - REF_WHOLE) <= 1e-12 * max(1.0, abs(REF_WHOLE)))
        ck("exact solution satisfies no-slip at BOTH walls",
           abs(R["u_lower"](0.0)) <= 1e-12 and abs(R["u_upper"](H)) <= 1e-12)
        ck("exact solution is CONTINUOUS across the interface",
           abs(R["u_interface_lower"] - R["u_interface_upper"]) <= 1e-12 * abs(REF_WHOLE))
        ck("exact solution has CONTINUOUS shear stress across the interface",
           abs(R["tau_interface_lower"] - R["tau_interface_upper"]) <= 1e-12)
        ck("global force balance: |tau_bottom| + |tau_top| == GRAD * H",
           abs(abs(R["tau_bottom_wall"]) + abs(R["tau_top_wall"]) - GRAD * H) <= 1e-12)
        ck("frozen wall stresses match the derived ones to 1e-12",
           abs(R["tau_bottom_wall"] - REF_TAU_LOWER_WALL) <= 1e-12
           and abs(R["tau_top_wall"] - REF_TAU_UPPER_WALL) <= 1e-12)
        ck("frozen interface velocity matches the derived one to 1e-12",
           abs(R["u_interface_lower"] - REF_UIFACE) <= 1e-12 * abs(REF_UIFACE))

        # ---- the gate functionals on an EXACT profile -------------------------
        cxe, cye = _centres("L3")
        uxe = [exact_u(y) for y in cye]
        ck("l2_profile_error is ZERO on the exact profile",
           l2_profile_error(cye, uxe) <= 1e-14)
        ck("layer_means REFUSES when a cell centre lies ON the interface",
           _refuses(layer_means, [Y_IFACE, 1.0, 3.0], [1.0, 1.0, 1.0]))
        ck("layer_means REFUSES when one layer holds no cells",
           _refuses(layer_means, [1.0, 1.5], [1.0, 1.0]))

        # ---- the clause-level guards, driven to BOTH outcomes -----------------
        al_ok = [(1.0 if y < Y_IFACE else 0.0) for y in cye]
        ck("interface-stationarity clause is QUIET on an unmoved interface",
           check_alpha_stationary(cye, al_ok) == 0.0)
        ck("interface-stationarity clause REFUSES on a moved interface",
           _refuses(check_alpha_stationary, cye, [a + 1e-6 for a in al_ok]))
        ck("x-invariance clause is QUIET on an x-invariant field",
           check_x_invariance(cxe, cye, uxe)[0] <= 1e-15)
        bad = list(uxe); bad[0] += 1e-3 * abs(REF_WHOLE)
        ck("x-invariance clause REFUSES on a streamwise-varying field",
           _refuses(check_x_invariance, cxe, cye, bad))
        ck("mesh-structure clause is QUIET on the registered L3 mesh",
           check_mesh_structure(cxe, cye, "L3")["cells"] == NX["L3"] * NY["L3"])
        ck("mesh-structure clause REFUSES on the wrong cell count",
           _refuses(check_mesh_structure, cxe[:-1], cye[:-1], "L3"))
        ck("mesh-structure clause REFUSES when a cell CENTRE sits on the interface",
           _refuses(check_mesh_structure,
                    [0.0] * NX["L3"] * NY["L3"],
                    [Y_IFACE] * NX["L3"] * NY["L3"], "L3"))

        # ---- strict completion: one good tree, then one defect at a time ------
        good = os.path.join(tmp, "good")
        for lv in LEVELS:
            _write_level(good, lv)
        c = completion(good, "L1")
        ck("completion() is GREEN on a complete, plateaued, forced, aged run",
           c["state"] == "COMPLETE")
        ck("completion() records that the LEXICOGRAPHIC latest dir would have misread",
           c["lexicographic_would_have_misread"] is True
           and c["numeric_latest_time_dir"] == "1000")
        ck("completion() records the registered Courant control from the controlDict",
           c["adjustTimeStep"] == "yes" and c["maxCo"] == MAXCO
           and c["maxAlphaCo"] == MAXALPHACO)
        ck("completion() reports rc NOT MEASURED when RUN_RC is absent (L-342)",
           c["rc_status"] == "NOT MEASURED")

        def one_bad(name, **kw):
            r = os.path.join(tmp, "bad_" + name)
            _write_level(r, "L1", **kw)
            return _refuses(completion, r, "L1")

        ck("completion REFUSES with no End line", one_bad("noend", end_line=False))
        ck("completion REFUSES when the fvOptions markers are ABSENT "
           "(the silent-forcing hazard)", one_bad("nofvopt", fvopt=False))
        ck("completion REFUSES when last Time != endTime", one_bad("shorttime", lasttime=999))
        ck("completion REFUSES when the ExecutionTime count != the Time-line count "
           "(rule-4 clause-5 adaptation for adjustTimeStep yes)",
           one_bad("execcount", exec_drop=1))
        ck("completion REFUSES when adjustTimeStep is not yes (R1's fatal setting)",
           one_bad("adjno", adjust="no"))
        ck("completion REFUSES when maxCo is not the registered value",
           one_bad("wrongco", maxco=5.0))
        ck("completion REFUSES on a missing field at endTime",
           one_bad("nofield", fields=("U", "p_rgh", ALPHA_FIELD, "Cx")))
        ck("completion REFUSES on an AGE-GUARD violation", one_bad("age", age_ok=False))
        ck("completion REFUSES when the interface moved", one_bad("alpha", alpha_shift=1e-6))
        ck("completion REFUSES when the field is not x-invariant",
           one_bad("xvar", xperturb=1e-3))
        ck("completion REFUSES when the solve has NOT PLATEAUED",
           one_bad("plateau", plateau_shift=1e-3))
        ck("completion REFUSES when controlDict carries an unregistered endTime",
           one_bad("wrongend", endtime=900, times=(500, 900)))

        rr = os.path.join(tmp, "bad_rc")
        _write_level(rr, "L1")
        fh = open(os.path.join(rr, "RUN_RC.L1"), "w")
        try:
            fh.write("rc = 124\nwall_s = 1\ncore_min = 1\ntimeout_s = 1\n")
        finally:
            fh.close()
        ck("completion REFUSES on a RECORDED non-zero rc (124 == the cap fired)",
           _refuses(completion, rr, "L1"))

        td = os.path.join(good, "L2")
        os.makedirs(os.path.join(td, "9999"), exist_ok=True)
        ck("completion REFUSES when the numerically-latest time dir != the log's last Time",
           _refuses(completion, good, "L2"))
        os.rmdir(os.path.join(td, "9999"))

        # ---- the planted-zero control, two stages, two channels ---------------
        c1 = completion(good, "L1")
        pu = planted_zero_u(c1["level_dir"], c1["time_dir"], "L1", c1["cy"])
        ck("planted zero P1a: the VELOCITY reader SEES a sized all-cell plant",
           pu["worst_readback_error"] <= 1e-9 * max(pu["plant"], 1.0))
        ck("planted zero P1b: the plant MOVES limb A by exactly the plant and pushes it "
           "OUT of the frozen band",
           pu["band_inside_unplanted"] is True and pu["band_inside_planted"] is False)
        ck("planted zero P1b: the plant RAISES the limb C profile error",
           pu["l2_planted"] > pu["l2_unplanted"])
        ck("planted zero REFUSES against a BLIND writer on the VELOCITY channel",
           _refuses(planted_zero_u, c1["level_dir"], c1["time_dir"], "L1", c1["cy"],
                    _blind_plant_vector_x))
        pa = planted_zero_alpha(c1["level_dir"], c1["time_dir"], "L1", c1["cy"])
        ck("planted zero P1a: the ALPHA reader SEES a sized all-cell plant",
           pa["worst_readback_error"] <= 1e-9)
        ck("planted zero P1b: the ALPHA plant makes the STATIONARITY CLAUSE refuse",
           pa["passed"] is True)
        ck("planted zero REFUSES against a BLIND writer on the ALPHA channel",
           _refuses(planted_zero_alpha, c1["level_dir"], c1["time_dir"], "L1", c1["cy"],
                    _blind_plant_scalar))
        t1 = _refusal_text(planted_zero_u, c1["level_dir"], c1["time_dir"], "L1", c1["cy"],
                           _blind_plant_vector_x)
        t2 = _refusal_text(one_match, os.path.join(tmp, "card", "missing.txt"), "t")
        ck("the blind-writer arm and the cardinality arm refuse for DIFFERENT reasons "
           "(L-314 addendum 2: two arms failing with the same message are one arm)",
           ("P1a" in t1) and ("CARDINALITY GUARD" in t2) and (t1 != t2))

        # ---- Roache, every state ---------------------------------------------
        ck("roache EXACT on three equal values", roache(1.0, 1.0, 1.0)["state"] == "EXACT")
        ck("roache STAGNANT when one difference is zero",
           roache(1.0, 2.0, 2.0)["state"] == "STAGNANT")
        ck("roache OSCILLATORY when the differences change sign",
           roache(1.0, 2.0, 1.5)["state"] == "OSCILLATORY")
        ck("roache DIVERGENT when |d32| >= |d21|", roache(1.0, 2.0, 4.0)["state"] == "DIVERGENT")
        tc = roache(1.0, 1.25, 1.3125)
        ck("roache CONVERGING with p = 2 on an exactly second-order triple",
           tc["state"] == "CONVERGING" and abs(tc["p"] - 2.0) < 1e-9)
        ck("roache quotes a GCI ONLY on a CONVERGING triple",
           tc["gci_fine"] is not None
           and roache(1.0, 2.0, 4.0)["gci_fine"] is None
           and roache(1.0, 2.0, 1.5)["gci_fine"] is None
           and roache(1.0, 1.0, 1.0)["gci_fine"] is None)
        tf = roache(1.0, 1.5, 1.5 + 0.5 * (2.0 ** -0.01))
        ck("roache calls a triple below the observed-order floor STAGNANT, not CONVERGING",
           tf["state"] == "STAGNANT" and tf.get("p_below_floor") is True)

        # ---- verdicts: rule 5 one-way, and the ceiling guard ------------------
        conv = roache(1.0, 1.25, 1.3125)
        ck("rule 5 is ONE-WAY: every non-CONVERGING state gives NOT A RESULT whatever "
           "the band says",
           all(verdict_for_limb("A", roache(*t), True)[0] == "NOT A RESULT"
               for t in [(1.0, 1.0, 1.0), (1.0, 2.0, 2.0), (1.0, 2.0, 1.5), (1.0, 2.0, 4.0)]))
        ck("a CONVERGING triple inside the band gives PASS (the declared ceiling)",
           verdict_for_limb("A", conv, True)[0] == "PASS")
        ck("a CONVERGING triple outside the band gives GATE FAIL",
           verdict_for_limb("A", conv, False)[0] == "GATE FAIL")
        saved = TIER_CEILING["A"]
        TIER_CEILING["A"] = "GATE REACHED"
        ck("the CEILING GUARD REFUSES when a limb would emit a verdict above its "
           "declared ceiling",
           _refuses(verdict_for_limb, "A", conv, True))
        TIER_CEILING["A"] = saved
        ck("the CEILING GUARD is QUIET again once the declared ceiling is PASS",
           verdict_for_limb("A", conv, True)[0] == "PASS")
        ck("every verdict this comparator can emit is inside the fixed vocabulary",
           all(verdict_for_limb("A", conv, b)[0] in VOCAB for b in (True, False)))
        ck("ROW verdict is the WORST limb",
           row_verdict([("A", "PASS"), ("B", "GATE FAIL"), ("C", "PASS")]) == "GATE FAIL"
           and row_verdict([("A", "PASS"), ("B", "PASS"), ("C", "NOT A RESULT")])
               == "NOT A RESULT"
           and row_verdict([("A", "PASS"), ("B", "PASS"), ("C", "PASS")]) == "PASS")

        # ---- end to end on the synthetic tree ---------------------------------
        rc_e2e = main(["--run-root", good, "--out", os.path.join(tmp, "e2e.json")])
        ck("end-to-end grade of a synthetic EXACT run returns 0", rc_e2e == 0)
        rec = json.load(open(os.path.join(tmp, "e2e.json")))
        ck("end-to-end record carries three limbs, each with its declared ceiling",
           all(rec["limbs"][k]["ceiling"] == TIER_CEILING[k] for k in ("A", "B", "C")))

        # A synthetic run carrying a SECOND-ORDER error sequence: every triple is
        # CONVERGING and every limb is inside its band, so the ROW must read PASS.
        conv_root = os.path.join(tmp, "e2e_conv")
        for lv, e in zip(LEVELS, (4.0e-3, 1.0e-3, 2.5e-4)):
            _write_level(conv_root, lv, err=e)
        rc_c = main(["--run-root", conv_root, "--out", os.path.join(tmp, "conv.json")])
        recc = json.load(open(os.path.join(tmp, "conv.json")))
        ck("end-to-end: a CONVERGING, in-band synthetic run gives ROW VERDICT PASS",
           rc_c == 0 and recc["verdict"] == "PASS"
           and all(recc["limbs"][k]["triple"]["state"] == "CONVERGING"
                   for k in ("A", "B", "C")))

        # The same shape, but the finest level sits OUTSIDE the frozen band: the
        # row must read GATE FAIL. A gate that cannot fail is not a gate.
        fail_root = os.path.join(tmp, "e2e_fail")
        for lv, e in zip(LEVELS, (0.16, 0.08, 0.04)):
            _write_level(fail_root, lv, err=e)
        rc_f = main(["--run-root", fail_root, "--out", os.path.join(tmp, "fail.json")])
        recf = json.load(open(os.path.join(tmp, "fail.json")))
        ck("end-to-end: a CONVERGING but OUT-OF-BAND synthetic run gives ROW VERDICT "
           "GATE FAIL -- the gate can fail",
           rc_f == 0 and recf["verdict"] == "GATE FAIL"
           and all(recf["limbs"][k]["triple"]["state"] == "CONVERGING"
                   for k in ("A", "B", "C")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    nfail = sum(1 for _n, ok in _RESULTS if not ok)
    print("SELFTEST: %d checks, %d PASS, %d FAIL" % (len(_RESULTS),
                                                     len(_RESULTS) - nfail, nfail))
    if nfail:
        for n, ok in _RESULTS:
            if not ok:
                print("  FAILED: %s" % n)
        return 1
    print("SELFTEST: all checks passed")
    return 0


# -------------------------------------------------------------------- main -----
def verify_frozen():
    """Hash this file and the pre-registration on disk against their HEAD blobs.
    The repository root is derived from `git rev-parse --show-toplevel`, which is
    depth-independent -- NOT from counting dirname()s (L-314 addendum 2)."""
    import subprocess
    repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if not repo:
        raise SystemExit2("--verify-frozen: not inside a git repository")
    rc = 0
    for rel in ("cases/ansys_verification/VMFL069-R2/PREREGISTRATION.md",
                "cases/ansys_verification/VMFL069-R2/grade_vmfl069_r2.py"):
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

    run_root, out_path = RUN_ROOT, None
    for i, a in enumerate(argv):
        if a == "--run-root" and i + 1 < len(argv):
            run_root = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out_path = argv[i + 1]
    run_root = os.path.abspath(run_root)

    R = {"case": "VMFL069-R2", "manual_page": 205,
         "title": "Two Phase Poiseuille Flow",
         "reference": {
             "kind": "EXACT SOLUTION OF THE SAME CONTINUUM MODEL",
             "derivation": "steady incompressible Navier-Stokes, piecewise-constant "
                           "viscosity, flat non-deforming interface -- the model the "
                           "manual declares on p.205; derived in derive_reference() and "
                           "cross-checked against the frozen constants in --selftest",
             "mean_lower_m_s": REF_LOWER, "mean_upper_m_s": REF_UPPER,
             "mean_whole_m_s": REF_WHOLE, "u_interface_m_s": REF_UIFACE,
             "tau_bottom_wall_Pa": REF_TAU_LOWER_WALL,
             "tau_top_wall_Pa": REF_TAU_UPPER_WALL,
             "manual_printed_target": None,
             "manual_note": "VM2026R1 p.205 prints Figure .69.2 only -- NO numeric Target "
                            "table. The gate is against the exact solution derived here, "
                            "NOT against any digitised curve."},
         "case_constants": {"Lx_m": LX, "H_m": H, "y_interface_m": Y_IFACE,
                            "nu_lower_m2_s": NU_LOWER, "nu_upper_m2_s": NU_UPPER,
                            "rho_kg_m3": RHO, "minus_dpdx_Pa_m": GRAD},
         "band": TOL, "limb_class": LIMB_CLASS, "tier_ceilings": dict(TIER_CEILING),
         "field_classes": FIELD_CLASSES, "run_root": run_root, "levels": {}}

    # The AST guard runs on the grading path too, not only in --selftest.
    R["ast_assert_count"] = _ast_guard()

    for lv in LEVELS:
        R["levels"][lv] = completion(run_root, lv)

    # ---- the controls fire BEFORE any value is believed -----------------------
    l1 = R["levels"]["L1"]
    R["planted_zero"] = [
        planted_zero_u(l1["level_dir"], l1["time_dir"], "L1", l1["cy"]),
        planted_zero_alpha(l1["level_dir"], l1["time_dir"], "L1", l1["cy"]),
    ]

    vals = {"A": {}, "B": {}, "C": {}}
    for lv in LEVELS:
        c = R["levels"][lv]
        vals["A"][lv] = c["mean_lower"]
        vals["B"][lv] = c["mean_upper"]
        vals["C"][lv] = c["l2_error"]
        for k in ("cx", "cy", "ux"):
            c.pop(k, None)          # keep the JSON record readable

    spec = {"A": ("volume-mean u_x, LOWER layer (nu = %g)" % NU_LOWER, REF_LOWER, "m/s"),
            "B": ("volume-mean u_x, UPPER layer (nu = %g)" % NU_UPPER, REF_UPPER, "m/s"),
            "C": ("normalised L2 error of the cell-centre profile", 0.0, "-")}

    R["limbs"] = {}
    order = []
    for k in ("A", "B", "C"):
        tri = roache(vals[k]["L1"], vals[k]["L2"], vals[k]["L3"])
        fine = vals[k]["L3"]
        if k == "C":
            dev, inside = fine, (fine <= TOL)      # the norm IS the deviation
        else:
            dev = abs(fine - spec[k][1]) / abs(spec[k][1])
            inside = dev <= TOL
        v, why = verdict_for_limb(k, tri, inside)
        R["limbs"][k] = {"quantity": spec[k][0], "unit": spec[k][2],
                         "class": LIMB_CLASS, "ceiling": TIER_CEILING[k],
                         "per_level": vals[k], "finest": fine,
                         "reference": spec[k][1], "deviation_rel": dev,
                         "band": TOL, "inside": inside, "triple": tri,
                         "verdict": v, "why": why}
        order.append((k, v))

    R["verdict"] = row_verdict(order)
    R["verdict_note"] = ("the ROW verdict is the WORST limb. All three limbs carry ceiling "
                         "PASS because the reference is the EXACT solution of the SAME "
                         "continuum model, so this row CAN be a credential -- and only if "
                         "every triple is CONVERGING and every limb is inside its band.")

    print("VMFL069-R2  (VM2026R1 p.205)  ROW VERDICT: %s" % R["verdict"])
    for k in ("A", "B", "C"):
        L = R["limbs"][k]
        t = L["triple"]
        print("  limb %s  %s" % (k, L["quantity"]))
        print("          L1/L2/L3 = %.9g / %.9g / %.9g"
              % (L["per_level"]["L1"], L["per_level"]["L2"], L["per_level"]["L3"]))
        print("          finest %.9g vs reference %.9g, deviation %.6f %%, band %.4f %% -> %s"
              % (L["finest"], L["reference"], 100.0 * L["deviation_rel"],
                 100.0 * L["band"], L["verdict"]))
        print("          triple %s, p = %s, GCI_fine = %s"
              % (t["state"], "n/a" if t["p"] is None else "%.6f" % t["p"],
                 "n/a" if t["gci_fine"] is None else "%.6f" % t["gci_fine"]))
    for lv in LEVELS:
        c = R["levels"][lv]
        print("  %s: cells %d, alpha drift %.3g, x-spread %.3g, plateau %.3g / %.3g, "
              "numeric latest dir %s (lexicographic would have read %s)"
              % (lv, c["mesh"]["cells"], c["alpha_max_drift"], c["x_invariance"],
                 c["plateau"]["rel_change_lower"], c["plateau"]["rel_change_upper"],
                 c["numeric_latest_time_dir"], c["lexicographic_latest_time_dir"]))
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
