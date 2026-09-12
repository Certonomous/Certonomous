#!/usr/bin/env python3
"""analyse_t21.py -- the T21 FROZEN COMPARATOR (the CONSUMER paired with the
producer build_t21.py).  Steady radial conduction through a two-solid
axisymmetric wedge, chtMultiRegionSimpleFoam v2606, an enthalpy source in the
core solid.

REGISTERED BY docs/campaigns/T-family/T21_PREREGISTRATION.md.  This file is the
"separate act under a separate review" of S11/S9; it is written to the
specification of S3, S5, S6 and S9 and is NOT self-authorising.

SCOPE AND CEILING (S2.1, S10 omission 12).  An EXACT analytic referent scores V
and NEVER P: this rung can reach GATE REACHED at best and can NEVER reach HOLDS.
No reading of the result raises that ceiling.

WHAT IT GRADES (S1 line 3):
  Q1  dT_wall  = areaAvg(T, housing_to_core) - areaAvg(T, housing_outer),
                 read from the boundaryField of <endTime>/housing/T.  THE GATED
                 reader.  Referent EX.dT_wall(P_full)  (patch-to-patch, r_i->r_o).
  Q2  dT_cells = innermost housing cell-ring mean - outermost ring mean, read
                 from the internalField of <endTime>/housing/T, rings identified
                 from the C (cell-centre) field by radius.  Referent
                 EX.dT_cells(P_full, N_r) (a SHORTER span; S4.4 requires the
                 two residuals to DIFFER -- equality is a dead anti-degeneracy
                 control and REFUSES).
  Q3  B        = |power leaving housing_outer| / P_sector-as-REGISTERED, the
                 power taken from the wallHeatFlux integral (postProcess), NEVER
                 inferred from dT_wall through the resistance (S5.2, S9.2 forbid
                 that: it makes B == 1 by construction).

THE FIVE REGISTERED REFUSALS (exit 2), each in one place:
  * PLANTED-ZERO control (S5.4, rule 3): copy-first, NEGATIVE arm bitwise 0,
    POSITIVE magnitude ladder incl. BAND_MIN, floor-to-band clause 9, and the
    SIGNED arm clause 10 (a reader that abs()es the difference is BLIND to the
    gate inversion and REFUSES).
  * "but never used" (S3.1, S9-S9): a source named for a field never applied
    prints one line near the top of log.solve; its presence REFUSES.
  * THE WEDGE-FACTOR / theta-recompute assert (S3.4, S10): theta is recomputed
    FROM THE MESH (blockMeshDict), never hard-coded 5 deg, and the fvOptions Su
    is asserted == EX.p_sector(P_full, theta_mesh) to 1e-12 relative.  A
    hard-coded-5deg consumer REFUSES the correct Su at ~1.4e-10 (this is the
    landmine the physics lane caught, rehearsed in --selftest S10 and in the
    paired-pin rehearsal recorded in the registration).
  * THE VOLUME assert (S3.3 point 4): the solver's "selected N cell(s) with
    volume V" line is read from log.solve and asserted against the analytic
    chord-faced wedge volume to 1e-9 relative; a "but never used" or a missing
    "selected" line REFUSES (the source-not-applied trap).
  * ROACHE floors imported, never local (S9.2): STAGNANT_FLOOR, P_MIN, FS, PLANT
    come from scripts/roache_triple.py.

RULE 4 completion (S6) is gate (1): rc=0, an End line, last time == endTime,
fields present, ExecutionTime count == endTime, and the age guard.  A case that
fails any conjunct makes the rung NOT A RESULT with NO graded value; the
comparator does not read a field or form a triple for it.

NO bare `assert` (L-332): every refusal is sys.exit(2); the AST assert count is
0 and --selftest measures it.  apply_gate() is the ONLY writer of a verdict and
walks rule 5's order one way.  Exit 0 graded, 2 REFUSAL.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t21 as EX                                                  # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT   # noqa: E402

# ---- registered constants (T21_PREREGISTRATION.md) -------------------------
LEVELS = ("c", "m", "f")
TRIPLE_CASES = {"c": "T21_CYL_c", "m": "T21_CYL_m", "f": "T21_CYL_f"}
CASE_S10 = "T21_CYL_S10"      # V(b) planted-source arm (+10%)
CASE_W1 = "T21_CYL_W1"        # wedge-angle control, theta = 1 deg
CASE_P1000 = "T21_CYL_P1000"  # linearity + widest band
REFINEMENT = 2.0              # S1 line 5: r = 2 uniform in BOTH mesh directions
DIM = 2                       # 2-D axisymmetric wedge; axial contributes 0 error
EXIT_OK, EXIT_REFUSE = 0, 2

R_BORE = 0.006                # m, core bore (S8.1)
R_I = EX.R_I                  # 0.0335 m, housing inner / interface radius
R_O = EX.R_O                  # 0.0375 m, housing outer radius (the sink)
L_AX = EX.L_AX                # 0.125 m
T_OUTER = 288.0              # K, housing_outer fixedValue sink (S5.1)
END_TIME = 3000              # S8.1 registered endTime, every case
DELTA_T = 1

BAND_REL = 0.01              # S1 line 4: all Q1/Q2 bands are 1 % of the drop
REG_DT_WALL_100 = 0.0859974153  # K, the REGISTERED analytic dT_wall at P=100 W
                            # (T21_PREREGISTRATION.md S1 line 4 band anchor); an
                            # INDEPENDENTLY pinned number the imported reference
                            # is checked against, never a call compared to itself.
BAND_MIN = 8.59974e-04      # K, the tightest ABSOLUTE band (P=100 W); S5.4
FLOOR_LIMIT = 8.59974e-06   # K, one hundredth of BAND_MIN; S5.4 clause 9
WEDGE_REL_TOL = 1.0e-12     # S3.4: Su round-trip tolerance
VOL_REL_TOL = 1.0e-9        # S3.3 point 4: chord-faced wedge volume tolerance
BAL_UNPLANTED = 0.01        # S1 line 4 / S5.2: |B - 1| <= 0.01
BAL_PLANTED = (0.095, 0.105)  # S5.2: B_planted - B_unplanted in this band
ORDER_BAND = (1.6, 2.4)     # S1 line 4: observed order p in [1.6, 2.4]
GCI_FINE_MAX_PCT = 0.05     # S1 line 4: GCI_fine < 0.05 % of dT_wall
WEDGE_CTRL_FACTOR = 0.25    # S5.3: theta=1 residual < 0.25 x theta=5 residual

# The full P for each triple/graded case, from S8.1.
P_OF_CASE = {"T21_CYL_c": 100.0, "T21_CYL_m": 100.0, "T21_CYL_f": 100.0,
             CASE_S10: 110.0, CASE_W1: 100.0, CASE_P1000: 1000.0}
# Housing radial cell count per case (for Q2's per-level referent), from S8.1.
NR_HOUSING = {"T21_CYL_c": 8, "T21_CYL_m": 16, "T21_CYL_f": 32,
              CASE_S10: 32, CASE_W1: 32, CASE_P1000: 32}
# Core radial and axial cell counts per case (for the selected-volume assert), S8.1.
NR_CORE = {"T21_CYL_c": 24, "T21_CYL_m": 48, "T21_CYL_f": 96,
           CASE_S10: 96, CASE_W1: 96, CASE_P1000: 96}
NZ = {"T21_CYL_c": 20, "T21_CYL_m": 40, "T21_CYL_f": 80,
      CASE_S10: 80, CASE_W1: 80, CASE_P1000: 80}

# The precision the instrument writes a plant at -- models the case's
# writePrecision (S2.4: registered writePrecision 12 gives a ~1e-9 K quantum).
# S5 sets this to a coarse format to drive the demonstrated floor above the band.
PLANT_FMT = "%.12g"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ======================================================================= MESH
def theta_from_mesh(case_dir):
    """S3.4 -- recompute the wedge angle FROM THE MESH, never hard-coded 5 deg.

    Read system/blockMeshDict, take the outer-radius (+y) front vertex and
    return the FULL included angle 2*atan2(y, x).  This is an INDEPENDENT
    reimplementation of the producer's read-back (build_t21.theta_from_
    blockmeshdict); the two agreeing to machine precision is the paired-pin
    that the whole wedge-factor defence rests on."""
    p = os.path.join(case_dir, "system", "blockMeshDict")
    if not os.path.isfile(p):
        refuse("no system/blockMeshDict in %s -- cannot recompute theta from the mesh" % case_dir)
    txt = open(p).read()
    best = None
    for x, y, z in re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", txt):
        x, y = float(x), float(y)
        if abs(math.hypot(x, y) - R_O) < 1e-9 and y > 0.0:
            best = 2.0 * math.atan2(y, x)
    if best is None:
        refuse("no outer-radius (+y) vertex at r_o=%.4f in %s/system/blockMeshDict" % (R_O, case_dir))
    return best


def read_su_from_fvoptions(case_dir):
    """Read the enthalpy source Su out of constant/core/fvOptions, in the
    registered `sources { h (Su Sp); }` form.  A source on field T, or the
    legacy injectionRate spelling, is the SILENT-zero trap and is refused."""
    p = os.path.join(case_dir, "constant", "core", "fvOptions")
    if not os.path.isfile(p):
        refuse("no constant/core/fvOptions in %s -- the enthalpy source is absent (a silent-zero source)" % case_dir)
    txt = open(p).read()
    if "injectionRate" in txt:
        refuse("fvOptions uses injectionRate (does not exist at v2606, S3.2)")
    m = re.search(r"sources\s*\{\s*h\s*\(\s*([-\d.eE+]+)\s+[-\d.eE+]+\s*\)", txt, re.S)
    if not m:
        if re.search(r"sources\s*\{\s*T\s*\(", txt, re.S):
            refuse("fvOptions source is on field T, not h -- the SILENT-zero trap (S3.1)")
        refuse("could not read `sources { h (Su Sp); }` from %s/constant/core/fvOptions (S3.1)" % case_dir)
    return float(m.group(1))


def wedge_factor_assert(case_dir, p_full, hardcoded_theta_deg=None):
    """S3.4 -- the paired-pin.  Su written by the producer must equal
    EX.p_sector(P_full, theta) to WEDGE_REL_TOL relative.  With
    hardcoded_theta_deg=None (the REGISTERED behaviour) theta is recomputed from
    the mesh; passing a number simulates a defective hard-coded-5deg consumer,
    which REFUSES the correct Su at ~1.4e-10 > 1e-12.  Returns (Su, theta_used,
    expected) on acceptance."""
    su = read_su_from_fvoptions(case_dir)
    if hardcoded_theta_deg is None:
        theta = theta_from_mesh(case_dir)
    else:
        theta = math.radians(hardcoded_theta_deg)
    expected = EX.p_sector(p_full, theta)
    if expected == 0.0:
        refuse("wedge-factor: expected P_sector is zero -- degenerate theta or P")
    rel = abs(su - expected) / abs(expected)
    if rel > WEDGE_REL_TOL:
        refuse("wedge-factor MISMATCH in %s: fvOptions Su=%.17g, expected P_full=%g * theta/(2pi)=%.17g "
               "(theta=%.10f deg%s), rel=%.3e > %.1e -- the two files disagree (S3.4)"
               % (case_dir, su, p_full, expected, math.degrees(theta),
                  "" if hardcoded_theta_deg is None else " HARD-CODED", rel, WEDGE_REL_TOL))
    return su, theta, expected


def chord_wedge_volume(r0, r1, theta, length):
    """The chord-faced (flat radial faces) annular-sector volume OpenFOAM
    measures for a single circumferential cell of full angle theta:
        A_cross = (r1^2 - r0^2) * sin(theta)/2 ,   V = A_cross * length .
    Derived here, not transcribed."""
    return (r1 * r1 - r0 * r0) * math.sin(theta) / 2.0 * length


def read_selected_volume(case_dir):
    """S3.3 point 4 -- read the cellSetOption 'selected N cell(s) with volume V'
    line out of log.solve (the source lands on the CORE, selectionMode all).
    Returns (N, V).  Also refuses on the 'but never used' signature here so the
    source-not-applied trap cannot slip past the volume check."""
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        refuse("no log.solve in %s -- cannot read the selected-volume line" % case_dir)
    body = open(log, errors="replace").read()
    if "but never used" in body:
        refuse("log.solve contains 'but never used' -- the fvOptions source was NEVER APPLIED (S3.1)")
    m = re.search(r"selected\s+(\d+)\s+cell\(s\)\s+with\s+volume\s+([-\d.eE+]+)", body)
    if not m:
        refuse("no 'selected N cell(s) with volume V' line in %s/log.solve -- the source did not land (S3.3)" % case_dir)
    return int(m.group(1)), float(m.group(2))


def volume_assert(case_dir, theta, nr_core, nz):
    """The measured selected-cell volume must match the analytic chord-faced
    core wedge volume (r_bore -> r_i) to VOL_REL_TOL, and the cell COUNT must be
    the registered core count.  A free, independent check the source landed on
    the region it was meant to."""
    n_read, v_read = read_selected_volume(case_dir)
    n_expect = nr_core * nz
    if n_read != n_expect:
        refuse("selected cell count %d != registered core count %d (%d radial x %d axial) in %s"
               % (n_read, n_expect, nr_core, nz, case_dir))
    v_expect = chord_wedge_volume(R_BORE, R_I, theta, L_AX)
    rel = abs(v_read - v_expect) / abs(v_expect)
    if rel > VOL_REL_TOL:
        refuse("selected volume %.12g != analytic chord wedge volume %.12g (rel %.3e > %.1e) in %s (S3.3)"
               % (v_read, v_expect, rel, VOL_REL_TOL, case_dir))
    return n_read, v_read, v_expect


def grep_never_used(case_dir):
    """S3.1 / S9 -- REFUSE if any region's log carries the one-shot
    'Source <name> defined for field <f> but never used' warning."""
    for name in ("log.solve",):
        p = os.path.join(case_dir, name)
        if os.path.isfile(p) and "but never used" in open(p, errors="replace").read():
            refuse("%s/%s contains 'but never used' -- a defined source was NEVER APPLIED (S3.1)" % (case_dir, name))


# =================================================================== READERS
def _uniform_or_list(block):
    """Parse an OpenFOAM 'uniform X' or 'nonuniform List<scalar> N ( ... )'
    value body into a flat list of floats."""
    m = re.search(r"uniform\s+([-\d.eE+]+)", block)
    if m:
        return [float(m.group(1))]
    m = re.search(r"nonuniform[^(]*\(\s*(.*?)\)", block, re.S)
    if m:
        return [float(v) for v in m.group(1).split()]
    return None


def read_patch_values(field_path, patch):
    """Face values of `patch` from the boundaryField of an OpenFOAM field.
    Returns a flat list (a single value for a uniform patch).  On a cylindrical
    wedge patch every face sits at one radius and one theta and (uniform axial
    mesh) has EQUAL area, so the arithmetic mean IS the area average -- this is
    stated, not assumed (S5.1)."""
    if not os.path.isfile(field_path):
        return None
    txt = open(field_path).read()
    m = re.search(r"boundaryField\s*\{(.*)\}\s*$", txt, re.S)
    body = m.group(1) if m else txt
    pm = re.search(re.escape(patch) + r"\s*\{(.*?)\n\s*\}", body, re.S)
    if not pm:
        return None
    return _uniform_or_list(pm.group(1))


def read_internal(field_path):
    """internalField of an OpenFOAM field as a flat list of floats."""
    if not os.path.isfile(field_path):
        return None
    txt = open(field_path).read()
    m = re.search(r"internalField\s+(.*?);", txt, re.S)
    if not m:
        return None
    return _uniform_or_list(m.group(1))


def read_cell_radii(case_dir, region, time):
    """Per-cell radius from the C (cell-centre) vector field written by
    `postProcess -func writeCellCentres`.  Radius = hypot(Cx, Cy).  Order is the
    internalField cell order, so it aligns with read_internal on the same
    region."""
    p = os.path.join(case_dir, str(time), region, "C")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField(.*?);", txt, re.S)
    if not m:
        return None
    radii = []
    for vx, vy, vz in re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", m.group(1)):
        radii.append(math.hypot(float(vx), float(vy)))
    return radii


def q1_dt_wall(case_dir, time):
    """Q1 = areaAvg(T, housing_to_core) - areaAvg(T, housing_outer)."""
    fp = os.path.join(case_dir, str(time), "housing", "T")
    inner = read_patch_values(fp, "housing_to_core")
    outer = read_patch_values(fp, "housing_outer")
    if inner is None or outer is None:
        return None
    return sum(inner) / len(inner) - sum(outer) / len(outer)


def q2_dt_cells(case_dir, time):
    """Q2 = innermost housing cell-ring mean - outermost ring mean, rings
    identified from the C field by radius (min-radius group vs max-radius
    group).  A SHORTER span than Q1 (S4.4)."""
    fp = os.path.join(case_dir, str(time), "housing", "T")
    vals = read_internal(fp)
    radii = read_cell_radii(case_dir, "housing", time)
    if vals is None or radii is None or len(vals) != len(radii):
        return None
    rmin, rmax = min(radii), max(radii)
    tol = 1e-9
    inner = [v for v, r in zip(vals, radii) if abs(r - rmin) <= tol]
    outer = [v for v, r in zip(vals, radii) if abs(r - rmax) <= tol]
    if not inner or not outer:
        return None
    return sum(inner) / len(inner) - sum(outer) / len(outer)


def read_wallheatflux_integral(case_dir, patch):
    """Power crossing `patch`, from the wallHeatFlux functionObject .dat
    (postProcessing/wallHeatFlux/<t>/wallHeatFlux.dat).  Columns are
    Time  patch  min  max  integral  (verified against
    wallHeatFlux_wall.cxx:60-65,300-304 at v2606).  The integral column is the
    LAST value written for `patch`.  NEVER inferred from dT_wall (S5.2, S9.2)."""
    base = os.path.join(case_dir, "postProcessing", "wallHeatFlux")
    if not os.path.isdir(base):
        return None
    val = None
    for sub in sorted(os.listdir(base)):
        dat = os.path.join(base, sub, "wallHeatFlux.dat")
        if not os.path.isfile(dat):
            continue
        for ln in open(dat, errors="replace"):
            if ln.lstrip().startswith("#"):
                continue
            parts = ln.split()
            if len(parts) >= 5 and parts[1] == patch:
                val = float(parts[4])
    return val


def q3_balance(case_dir, p_sector_registered):
    """Q3 = |power leaving housing_outer| / P_sector-as-REGISTERED.  The
    numerator is the wallHeatFlux integral magnitude; the denominator is the
    REGISTERED sector power, never a value read from the case (S5.2)."""
    integral = read_wallheatflux_integral(case_dir, "housing_outer")
    if integral is None:
        return None
    return abs(integral) / abs(p_sector_registered)


# ================================================= rule 4 completion (gate 1)
def read_status_rc(case_dir):
    p = os.path.join(case_dir, "STATUS.%s" % os.path.basename(case_dir))
    if not os.path.isfile(p):
        return None
    m = re.search(r"^rc=(\S+)$", open(p).read(), re.M)
    return m.group(1) if m else None


def latest_time(case_dir):
    ts = [t for t in os.listdir(case_dir)
          if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0.0]
    return max(ts, key=float) if ts else None


def completion_of(case_dir):
    """S6 -- rule 4, all-or-nothing, evaluated as gate (1).  Returns (ok, why).
    Conjuncts: rc=0; exactly one End line; last time == endTime; T and p present
    in <endTime>/core and <endTime>/housing; ExecutionTime count == endTime;
    and the age guard (every endTime field newer than the case's own 0/housing/T).
    """
    case = os.path.basename(case_dir)
    # 1. rc = 0 (from STATUS.<case>)
    rc = read_status_rc(case_dir)
    if rc is None:
        return False, "no STATUS.%s or no rc line" % case
    if rc != "0":
        return False, "STATUS rc=%s (not 0)" % rc
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return False, "no log.solve"
    body = open(log, errors="replace").read()
    # 2. exactly one End line
    if len(re.findall(r"^End\s*$", body, re.M)) != 1:
        return False, "not exactly one End line"
    # 3. last time == endTime
    lt = latest_time(case_dir)
    if lt is None:
        return False, "no time directory beyond 0"
    if abs(float(lt) - END_TIME) > 0:
        return False, "last time %s != endTime %d" % (lt, END_TIME)
    # 4. fields present: T and p in both regions at endTime
    for region in ("core", "housing"):
        for fld in ("T", "p"):
            if not os.path.isfile(os.path.join(case_dir, lt, region, fld)):
                return False, "missing %s/%s/%s" % (lt, region, fld)
    # 5. ExecutionTime count == endTime
    n_exec = len(re.findall(r"^ExecutionTime\s*=", body, re.M))
    if n_exec != END_TIME:
        return False, "ExecutionTime count %d != endTime %d" % (n_exec, END_TIME)
    # 6. age guard: every endTime field newer than the case's own 0/housing/T
    zero_t = os.path.join(case_dir, "0", "housing", "T")
    if not os.path.isfile(zero_t):
        return False, "age guard: no 0/housing/T to date the launch against"
    t0 = os.stat(zero_t).st_mtime
    for region in ("core", "housing"):
        for fld in ("T", "p"):
            fp = os.path.join(case_dir, lt, region, fld)
            if os.stat(fp).st_mtime <= t0:
                return False, "age guard: %s/%s/%s not newer than 0/housing/T" % (lt, region, fld)
    return True, ""


# ============================================= rule 3: planted-zero control
def _plant_lines_patch(field_path, patch):
    """Locate, STRUCTURALLY by line index, the value lines of `patch` in the
    boundaryField -- the start index of the numeric block and its length."""
    lines = open(field_path).read().splitlines(True)
    pi = None
    for i, ln in enumerate(lines):
        if re.match(r"\s*" + re.escape(patch) + r"\s*$", ln.rstrip("\n")) or \
           re.match(r"\s*" + re.escape(patch) + r"\s*\{", ln):
            pi = i
            break
    if pi is None:
        refuse("planted-zero: could not locate patch %s STRUCTURALLY" % patch)
    # find `value uniform X` (one line) or the '(' opening a nonuniform list
    for j in range(pi, min(pi + 12, len(lines))):
        mu = re.search(r"value\s+uniform\s+([-\d.eE+]+)\s*;", lines[j])
        if mu:
            return lines, [j], "uniform"
        if lines[j].strip() == "(":
            k = j + 1
            idxs = []
            while k < len(lines) and lines[k].strip() != ")":
                if re.match(r"\s*[-\d.eE+]+\s*$", lines[k]):
                    idxs.append(k)
                k += 1
            return lines, idxs, "list"
    refuse("planted-zero: patch %s has no readable value block" % patch)


def _set_line(lines, k, kind, newval):
    if kind == "uniform":
        lines[k] = re.sub(r"(value\s+uniform\s+)[-\d.eE+]+", r"\g<1>" + (PLANT_FMT % newval), lines[k])
    else:
        lines[k] = (PLANT_FMT + "\n") % newval


def _get_line(lines, k, kind):
    if kind == "uniform":
        return float(re.search(r"value\s+uniform\s+([-\d.eE+]+)", lines[k]).group(1))
    return float(lines[k].strip())


def planted_zero_control(case_dir, time):
    """S5.4 -- copy-first, both arms, sized to the reader, the floor-to-band
    clause 9, and the SIGNED arm clause 10.  Q1 reads a DIFFERENCE of two patch
    averages, so a plant on housing_to_core must move Q1 by +PLANT and a plant
    on housing_outer by -PLANT; a reader that abs()es the difference is BLIND to
    the gate inversion and is REFUSED."""
    tmp = tempfile.mkdtemp(prefix="t21pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero: scratch copy resolved INSIDE the case tree")
        # NEGATIVE ARM: the reader on identical bytes, bitwise 0 (no tolerance)
        a = q1_dt_wall(dst, time)
        if a is None:
            refuse("planted-zero: the reader returned nothing on the unplanted copy")
        b = q1_dt_wall(dst, time)
        dneg = abs(a - b)
        if dneg != 0.0:
            refuse("planted-zero NEGATIVE ARM FAILED: %.17g on identical bytes -- the reader is NOISY" % dneg)
        fp = os.path.join(dst, str(time), "housing", "T")
        ref = q1_dt_wall(dst, time)
        out = {}
        # POSITIVE ARM + SIGNED ARM: plant each patch, expected sign per patch.
        for patch, sign in (("housing_to_core", +1.0), ("housing_outer", -1.0)):
            lines, idxs, kind = _plant_lines_patch(fp, patch)
            orig = list(lines)
            before = {k: _get_line(lines, k, kind) for k in idxs}
            seen, floor = {}, None
            ladder = (1.0, 1e-1, 1e-2, PLANT, BAND_MIN, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8)
            for mag in ladder:
                for k in idxs:
                    _set_line(lines, k, kind, before[k] + mag)
                open(fp, "w").write("".join(lines))
                got = q1_dt_wall(dst, time)
                if got is None:
                    refuse("planted-zero %s: reader returned nothing at plant %.3g" % (patch, mag))
                d = got - ref                 # SIGNED, never abs()
                seen[mag] = d
                if abs(d) > 0.0:
                    floor = mag
            open(fp, "w").write("".join(orig))
            if floor is None:
                refuse("planted-zero %s POSITIVE ARM FAILED: no plant magnitude visible -- the reader is BLIND" % patch)
            # clause 9: demonstrated floor must be at least 100x finer than the band
            if floor > FLOOR_LIMIT:
                refuse("planted-zero %s: demonstrated floor %.3g K > %.3g K (S5.4 clause 9: "
                       "resolution not 100x finer than the band)" % (patch, floor, FLOOR_LIMIT))
            # clause 5: the registered plant must move the read by >= 0.1 x PLANT
            if abs(seen[PLANT]) < 0.1 * PLANT:
                refuse("planted-zero %s: registered plant %.6g moved the read by only %.3g (< 0.1 x plant, S5.4 clause 5)"
                       % (patch, PLANT, seen[PLANT]))
            # clause 10 (SIGNED): the recovered shift must carry the derived sign
            if sign > 0 and seen[PLANT] <= 0.0:
                refuse("planted-zero SIGNED ARM FAILED: plant on %s recovered %.3g (expected +PLANT) -- "
                       "a reader that abs()es the difference is BLIND to the gate inversion (S5.4 clause 10)" % (patch, seen[PLANT]))
            if sign < 0 and seen[PLANT] >= 0.0:
                refuse("planted-zero SIGNED ARM FAILED: plant on %s recovered %.3g (expected -PLANT) -- "
                       "a reader that abs()es the difference is BLIND to the gate inversion (S5.4 clause 10)" % (patch, seen[PLANT]))
            out[patch] = dict(status="PASS", plant=PLANT, sign=sign, cells_planted=len(idxs),
                              recovered=seen[PLANT], negative_arm=dneg,
                              demonstrated_detection_floor=floor, band_min=BAND_MIN,
                              ladder={("%g" % k): v for k, v in seen.items()})
            print("planted-zero %-16s PASS: plant %.6g in %d face(s), recovered %+.6g (sign %+.0f), floor %.1g"
                  % (patch, PLANT, len(idxs), seen[PLANT], sign, floor))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ================================================= rule 5: the gate
def triple_of(vals):
    return gci_equal(vals["c"], vals["m"], vals["f"], REFINEMENT, DIM, fs=FS)


def apply_gate(value, lo, hi, tr, gate1_ok, gate1_why):
    """The ONLY writer of a verdict.  Rule 5's fixed order, one way.  `value` is
    ALWAYS the FINE value; the extrapolate is never passed in.  The gate can
    only turn a PASS/GATE FAIL INTO NOT A RESULT, never the reverse."""
    bv = "PASS" if lo <= value <= hi else "GATE FAIL"
    if not gate1_ok:
        return "NOT A RESULT", bv, "gate (1): " + gate1_why
    if tr["state"] != "CONVERGING":
        p = tr.get("order")
        return ("NOT A RESULT", bv,
                "gate (2): triple is %s%s -- rule 5 makes a non-CONVERGING triple NOT A RESULT "
                "whatever the value says (STAGNANT_FLOOR=%g, P_MIN=%g)"
                % (tr["state"], (" (p=%.3e)" % p) if p is not None else "", STAGNANT_FLOOR, P_MIN))
    return bv, bv, ""


def fmt_tr(tr):
    p, g = tr.get("order"), tr.get("GCI_pct")
    return "%s p=%s GCI=%s" % (tr["state"], ("%.4f" % p) if p is not None else "n/a",
                               ("%.4e%%" % g) if g is not None else "REFUSED")


# ================================================================== the grade
def check_referents_reproducible():
    """REAL reproducibility guard (NOT a call compared to itself -- the vacuous
    check the T3f class hit).  The imported reference must reproduce numbers
    established on an INDEPENDENT path:
      Q1: EX.dT_wall(100) == the REGISTERED anchor 0.0859974153 K (S1 line 4);
      Q2: EX.dT_cells(100,32) == a first-principles re-derivation of the ring
          drop -- 100 * ln((r_o-dr/2)/(r_i+dr/2)) / (2 pi k L), which is
          theta-invariant because P_sector's theta cancels (S4.4), computed here
          WITHOUT calling EX.dT_cells or EX.p_sector.
    Returns (ref_q1, ref_q2) on success; REFUSES on a non-reproducible reference.
    """
    ref_q1 = EX.dT_wall(100.0)
    if abs(ref_q1 - REG_DT_WALL_100) / REG_DT_WALL_100 > 1e-9:
        refuse("Q1 referent not reproducible: EX.dT_wall(100)=%.12g != registered anchor %.12g "
               "(S1 line 4)" % (ref_q1, REG_DT_WALL_100))
    nr = NR_HOUSING["T21_CYL_f"]
    dr = (R_O - R_I) / float(nr)
    ref_q2_indep = 100.0 * math.log((R_O - 0.5 * dr) / (R_I + 0.5 * dr)) / (2.0 * math.pi * EX.K_HOUSING * L_AX)
    ref_q2 = EX.dT_cells(100.0, nr)
    if abs(ref_q2 - ref_q2_indep) / ref_q2_indep > 1e-9:
        refuse("Q2 referent not reproducible: EX.dT_cells(100,%d)=%.12g != first-principles %.12g "
               "(S4.4)" % (nr, ref_q2, ref_q2_indep))
    return ref_q1, ref_q2


def grade(root, json_out):
    cases = list(TRIPLE_CASES.values())
    # --- gate (1): completion of every triple case, evaluated FIRST -----------
    comp = {}
    for lv in LEVELS:
        cdir = os.path.join(root, TRIPLE_CASES[lv])
        if not os.path.isdir(cdir):
            refuse("%s absent -- the whole rung is graded or none of it is" % TRIPLE_CASES[lv])
        comp[lv] = completion_of(cdir)
    gate1_ok = all(comp[lv][0] for lv in LEVELS)
    gate1_why = "; ".join("%s: %s" % (TRIPLE_CASES[lv], comp[lv][1]) for lv in LEVELS if not comp[lv][0])
    print("gate (1) completion (rule 4): %s%s" % (gate1_ok, "" if gate1_ok else "  [" + gate1_why + "]"))

    # --- the paired-pin refusals, per triple case: never-used, wedge-factor,
    #     and (source landed on the right region) the selected-volume assert -----
    thetas = {}
    for lv in LEVELS:
        case = TRIPLE_CASES[lv]
        cdir = os.path.join(root, case)
        grep_never_used(cdir)
        su, theta, exp = wedge_factor_assert(cdir, P_OF_CASE[case])
        thetas[lv] = theta
        n_read, v_read, v_exp = volume_assert(cdir, theta, NR_CORE[case], NZ[case])
        print("  %s wedge-factor OK: Su=%.17g == P_sector(theta=%.6f deg)=%.17g; "
              "selected %d cells vol=%.6g == chord vol %.6g"
              % (case, su, math.degrees(theta), exp, n_read, v_read, v_exp))

    # --- if completion failed, emit NOT A RESULT with NO graded value ----------
    if not gate1_ok:
        rows = []
        for rid, quant in (("Q1", "dT_wall"), ("Q2", "dT_cells")):
            rows.append(dict(row=rid, quantity=quant, verdict="NOT A RESULT",
                             note="gate (1): " + gate1_why, value_fine=None, triple=None))
            print("%-3s -> NOT A RESULT [gate (1): %s]" % (rid, gate1_why))
        out = dict(rung="T21", gate1=dict(ok=False, why=gate1_why, completion=comp),
                   rows=rows, planted_zero_controls=None, Q3=None)
        json.dump(out, open(json_out, "w"), indent=2)
        print("wrote %s" % json_out)
        return EXIT_OK

    # --- read Q1 and Q2 at every level ---------------------------------------
    times, q1, q2 = {}, {}, {}
    for lv in LEVELS:
        cdir = os.path.join(root, TRIPLE_CASES[lv])
        t = latest_time(cdir)
        times[lv] = t
        v1 = q1_dt_wall(cdir, t)
        v2 = q2_dt_cells(cdir, t)
        if v1 is None or v2 is None:
            refuse("could not read Q1/Q2 on %s -- a missing number is not a zero" % TRIPLE_CASES[lv])
        q1[lv], q2[lv] = v1, v2

    # --- referent reproducibility (real guard, not a self-comparison) + the
    #     anti-degeneracy (S4.4): Q1 and Q2 residuals MUST differ --------------
    ref_q1, ref_q2 = check_referents_reproducible()
    if q1["f"] == q2["f"]:
        refuse("anti-degeneracy: Q1 and Q2 returned the IDENTICAL fine value %.17g -- the two readers "
               "have collapsed onto one code path (S4.4)" % q1["f"])

    # --- instrument admission (gate (2)): planted-zero control on the fine case
    pz = planted_zero_control(os.path.join(root, TRIPLE_CASES["f"]), times["f"])

    # --- Q3 balance and the V(b) planted-source arm, graded BEFORE the gated rows
    q3 = grade_balance(root, thetas["f"])

    # --- the graded rows ------------------------------------------------------
    rows = []
    for rid, quant, vals, ref in (
            ("Q1", "dT_wall", q1, ref_q1),
            ("Q2", "dT_cells", q2, ref_q2)):
        tr = triple_of(vals)
        lo, hi = ref * (1 - BAND_REL), ref * (1 + BAND_REL)
        verdict, bv, note = apply_gate(vals["f"], lo, hi, tr, gate1_ok, gate1_why)
        rows.append(dict(row=rid, quantity=quant, reference=ref, band=[lo, hi],
                         value_fine=vals["f"], rel_deviation=(vals["f"] - ref) / ref,
                         triple=dict(zip(LEVELS, (vals["c"], vals["m"], vals["f"]))),
                         triple_state=tr["state"], observed_order=tr.get("order"),
                         gci_pct=tr.get("GCI_pct"), band_verdict=bv, verdict=verdict, note=note))
        print("%-3s fine=%.10f ref=%.10f dev=%+.3e band=[%.7f, %.7f] %s -> %s%s"
              % (rid, vals["f"], ref, (vals["f"] - ref) / ref, lo, hi, fmt_tr(tr),
                 verdict, (" [" + note + "]") if note else ""))

    out = dict(rung="T21",
               scope="SOLID-ONLY steady radial conduction, two solid regions, an enthalpy source; "
                     "NOTHING conjugate, no flow, no turbulence, no correlation",
               ceiling="GATE REACHED at best -- the reference is EXACT (V, never P); HOLDS is unreachable",
               refinement_ratio=REFINEMENT, dim=DIM, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, PLANT=PLANT,
                           source="scripts/roache_triple.py (imported)"),
               gate1=dict(ok=gate1_ok, why=gate1_why, completion=comp),
               anti_degeneracy=dict(q1_fine=q1["f"], q2_fine=q2["f"], differ=q1["f"] != q2["f"]),
               planted_zero_controls=pz, Q3=q3, rows=rows)
    json.dump(out, open(json_out, "w"), indent=2)
    print("wrote %s" % json_out)
    return EXIT_OK


def grade_balance(root, theta_f):
    """Q3 -- the V(b) balance, graded BEFORE the gated rows (S5.2a: an ordering
    of grading, not of launch).  Unplanted |B-1|<=0.01; the +10% planted arm
    (T21_CYL_S10) must raise B by BAL_PLANTED using the SAME registered
    denominator.  P_sector is REGISTERED, never read from the case (S5.2)."""
    fdir = os.path.join(root, TRIPLE_CASES["f"])
    p_sector_f = EX.p_sector(100.0, theta_f)
    b_un = q3_balance(fdir, p_sector_f)
    sdir = os.path.join(root, CASE_S10)
    result = dict(p_sector_registered=p_sector_f, unplanted=b_un,
                  band_unplanted=BAL_UNPLANTED, band_planted=list(BAL_PLANTED))
    if b_un is None:
        result["status"] = "OWED"
        result["note"] = "no wallHeatFlux output on T21_CYL_f -- Q3 is owed at the authorized first solve (postProcess)"
        print("Q3 balance: OWED (no wallHeatFlux output yet -- postProcess pass at first solve)")
        return result
    result["unplanted_in_band"] = abs(b_un - 1.0) <= BAL_UNPLANTED
    if os.path.isdir(sdir) and q3_balance(sdir, p_sector_f) is not None:
        b_pl = q3_balance(sdir, p_sector_f)     # SAME registered denominator
        diff = b_pl - b_un
        result.update(planted=b_pl, planted_minus_unplanted=diff,
                      planted_in_band=BAL_PLANTED[0] <= diff <= BAL_PLANTED[1],
                      status="GRADED")
        print("Q3 balance: unplanted B=%.6f (|B-1|<=%.3g: %s); planted-unplanted=%.6f (in [%.3f,%.3f]: %s)"
              % (b_un, BAL_UNPLANTED, result["unplanted_in_band"], diff,
                 BAL_PLANTED[0], BAL_PLANTED[1], result["planted_in_band"]))
    else:
        result["status"] = "PLANTED_ARM_OWED"
        print("Q3 balance: unplanted B=%.6f; V(b) planted arm (T21_CYL_S10) owed at first solve" % b_un)
    return result


# ==================================================================== selftest
# Everything below forges SYNTHETIC scratch trees only.  S11: no limb reads,
# stats, globs or asserts anything about a live run tree; the whole limb set is
# run TWICE (empty ambient run root vs a populated one) and the results are
# checked byte-identical.

def _foam(cls, obj):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
            "    object %s;\n}\n" % (cls, obj))


def _write_scalar_patchfield(vals):
    if len(vals) == 1:
        return "        type fixedValue;\n        value uniform %.17g;\n" % vals[0]
    return ("        type calculated;\n        value nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n"
            % (len(vals), "\n".join("%.17g" % v for v in vals)))


def _write_housing_T(path, inner_face, outer_val, internal):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bf = ("boundaryField\n{\n"
          "    housing_to_core\n    {\n%s    }\n"
          "    housing_outer\n    {\n%s    }\n"
          "    wedge_front\n    {\n        type wedge;\n    }\n"
          "    wedge_back\n    {\n        type wedge;\n    }\n"
          "    ends\n    {\n        type zeroGradient;\n    }\n}\n"
          % (_write_scalar_patchfield(inner_face), _write_scalar_patchfield([outer_val])))
    open(path, "w").write(
        _foam("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\n\n"
        "internalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n\n%s"
        % (len(internal), "\n".join("%.17g" % v for v in internal), bf))


def _write_C(path, centres):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(
        _foam("volVectorField", "C") + "dimensions [0 1 0 0 0 0 0];\n\n"
        "internalField   nonuniform List<vector> \n%d\n(\n%s\n)\n;\n\nboundaryField{}\n"
        % (len(centres), "\n".join("(%.17g %.17g %.17g)" % c for c in centres)))


def _forge_housing(case_dir, time, p_full, nr, nz, theta_deg, k=EX.K_HOUSING,
                   extra_err=0.0, disc_err=0.0):
    """Forge a housing region whose patch and cell fields reproduce the ANALYTIC
    solution for (p_full, theta, nr): the ring drop equals EX.dT_cells and the
    patch drop equals EX.dT_wall.  disc_err adds a SECOND-ORDER (1/nr^2) term to
    the patch drop so the Q1 triple across c/m/f is CONVERGING at p=2; extra_err
    perturbs the interface to drive GATE FAIL limbs."""
    theta = math.radians(theta_deg)
    dt_wall = EX.dT_wall(p_full, theta_deg=theta_deg, k=k)
    dr = (R_O - R_I) / float(nr)
    ps = EX.p_sector(p_full, theta)
    t_outer = T_OUTER
    t_inner = t_outer + dt_wall * (1.0 + disc_err / (nr * nr)) + extra_err
    centres, vals = [], []
    for iz in range(nz):
        zc = (iz + 0.5) * L_AX / nz
        for ir in range(nr):
            rc = R_I + (ir + 0.5) * dr
            tr = t_outer + ps * math.log(R_O / rc) / (theta * k * L_AX)  # T(r) analytic
            centres.append((rc * math.cos(theta / 2), rc * math.sin(theta / 2), zc))
            vals.append(tr)
    _write_housing_T(os.path.join(case_dir, str(time), "housing", "T"),
                     [t_inner] * nz, t_outer, vals)
    _write_C(os.path.join(case_dir, str(time), "housing", "C"), centres)


def _forge_blockmesh(case_dir, theta_deg):
    # Vertices at %.10g -- the SAME precision build_t21._vertex writes at, which
    # is the SOURCE of the ~1.4e-10 theta round-trip gap that a hard-coded-5deg
    # consumer would trip on.  Writing full precision here would hide the landmine.
    os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
    a = math.radians(theta_deg) / 2.0
    verts = []
    for sign in (-1.0, 1.0):
        for r in (R_BORE, R_I, R_O):
            for z in (0.0, L_AX):
                verts.append("    (%.10g %.10g %.10g)" % (r * math.cos(a), sign * r * math.sin(a), z))
    open(os.path.join(case_dir, "system", "blockMeshDict"), "w").write(
        _foam("dictionary", "blockMeshDict") + "\nvertices\n(\n" + "\n".join(verts) + "\n);\n")


def _forge_fvoptions(case_dir, su):
    os.makedirs(os.path.join(case_dir, "constant", "core"), exist_ok=True)
    open(os.path.join(case_dir, "constant", "core", "fvOptions"), "w").write(
        _foam("dictionary", "fvOptions")
        + "\nmotorLoss\n{\n    type scalarSemiImplicitSource;\n    selectionMode all;\n"
          "    volumeMode absolute;\n    sources\n    {\n        h (%.17g 0);\n    }\n}\n" % su)


def _forge_log(case_dir, nr_core, nz, theta_deg, endtime=END_TIME, never_used=False,
               end_line=True, exec_count=None, selected=True):
    theta = math.radians(theta_deg)
    v = chord_wedge_volume(R_BORE, R_I, theta, L_AX)
    n = nr_core * nz
    lines = []
    if selected:
        lines.append("    - selected %d cell(s) with volume %.17g\n" % (n, v))
    if never_used:
        lines.append("Source motorLoss defined for field T but never used\n")
    ec = endtime if exec_count is None else exec_count
    for _ in range(ec):
        lines.append("ExecutionTime = 1 s  ClockTime = 1 s\n")
    if end_line:
        lines.append("End\n")
    open(os.path.join(case_dir, "log.solve"), "w").write("".join(lines))


def _forge_status(case_dir, rc=0):
    case = os.path.basename(case_dir)
    open(os.path.join(case_dir, "STATUS.%s" % case), "w").write(
        "case=%s\nrc=%d\nwall_s=5\nranks=1\nnote=clean\n" % (case, rc))


def _forge_whf(case_dir, integral, time=END_TIME, patch="housing_outer"):
    d = os.path.join(case_dir, "postProcessing", "wallHeatFlux", str(time))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "wallHeatFlux.dat"), "w").write(
        "# Wall heat-flux\n# Time\tpatch\tmin\tmax\tintegral\n"
        "%d\t%s\t%.17g\t%.17g\t%.17g\n" % (time, patch, integral, integral, integral))


def _forge_complete_case(root, case, p_full, nr_h, nr_c, nz, theta_deg, k=EX.K_HOUSING,
                         extra_err=0.0, disc_err=0.0, endtime=END_TIME, never_used=False,
                         end_line=True, exec_count=None, last_time=None, rc=0, drop_field=None,
                         age_ok=True, selected=True, whf=None):
    """Forge a rule-4-complete (or, via the knobs, deliberately incomplete) case."""
    cdir = os.path.join(root, case)
    if os.path.isdir(cdir):
        shutil.rmtree(cdir)          # forge from clean: no stale time dir survives
    lt = endtime if last_time is None else last_time
    # 0/ launch marker (touched FIRST); endTime fields must be newer
    os.makedirs(os.path.join(cdir, "0", "housing"), exist_ok=True)
    open(os.path.join(cdir, "0", "housing", "T"), "w").write("0\n")
    if age_ok:
        os.utime(os.path.join(cdir, "0", "housing", "T"), (1.0, 1.0))
    _forge_blockmesh(cdir, theta_deg)
    # Su from the MESH-read-back theta, exactly as build_t21 does (theta read
    # back from the generated blockMeshDict -> X.p_sector).  This is what makes
    # the mesh-recompute consumer ACCEPT and a hard-coded-5deg consumer REFUSE.
    su = EX.p_sector(p_full, theta_from_mesh(cdir))
    _forge_fvoptions(cdir, su)
    _forge_housing(cdir, lt, p_full, nr_h, nz, theta_deg, k=k, extra_err=extra_err, disc_err=disc_err)
    # p and core T/p for the fields-present conjunct
    for region in ("core", "housing"):
        for fld in ("p", "T"):
            fp = os.path.join(cdir, str(lt), region, fld)
            if not os.path.isfile(fp):
                os.makedirs(os.path.dirname(fp), exist_ok=True)
                open(fp, "w").write(_foam("volScalarField", fld) + "internalField uniform 1;\n")
    if drop_field is not None:
        fp = os.path.join(cdir, str(lt), drop_field[0], drop_field[1])
        if os.path.isfile(fp):
            os.remove(fp)
    _forge_log(cdir, nr_c, nz, theta_deg, endtime=endtime, never_used=never_used,
               end_line=end_line, exec_count=exec_count, selected=selected)
    _forge_status(cdir, rc=rc)
    if whf is not None:
        _forge_whf(cdir, whf, time=lt)
    if not age_ok:
        os.utime(os.path.join(cdir, "0", "housing", "T"), (9e9, 9e9))  # 0/T newer than fields
    return cdir


def _run_limbs(ambient_root):
    """Run the full limb set S1-S10 against forged scratch trees, ignoring
    `ambient_root` entirely (S11: no limb reads a live tree).  Returns a
    results dict of pass/fail per limb, for the S11 byte-identity comparison."""
    global q1_dt_wall, _plant_lines_patch, PLANT_FMT
    res = {}
    tmp = tempfile.mkdtemp(prefix="t21st_")
    try:
        # S1 -- BOTH SIGNS of every drift, through apply_gate on synthetic triples
        ref = EX.dT_wall(100.0)
        lo, hi = ref * (1 - BAND_REL), ref * (1 + BAND_REL)

        def ladder(pw, ef):
            return dict(f=ref + ef, m=ref + ef * 2 ** pw, c=ref + ef * 4 ** pw)
        band = ref * BAND_REL
        s1 = []
        for label, ef, want in (("+1.5band", 1.5 * band, "GATE FAIL"),
                                 ("-1.5band", -1.5 * band, "GATE FAIL"),
                                 ("+0.5band", 0.5 * band, "PASS"),
                                 ("-0.5band", -0.5 * band, "PASS")):
            tr = triple_of(ladder(2.0, ef if ef != 0 else 1e-9))
            v, _, _ = apply_gate(ref + ef, lo, hi, tr, True, "")
            s1.append(v == want)
        res["S1_both_signs"] = all(s1)

        # S2 -- BLIND reader mutant must REFUSE
        c = _forge_complete_case(tmp, "T21_CYL_f", 100.0, 32, 96, 80, 5.0)
        real_q1 = q1_dt_wall
        frozen = real_q1(c, END_TIME)
        q1_dt_wall = lambda cd, t: frozen
        fired = False
        try:
            planted_zero_control(c, END_TIME)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        finally:
            q1_dt_wall = real_q1
        res["S2_blind_refuses"] = fired

        # S3 -- NOISY reader mutant must REFUSE (negative arm)
        real_q1 = q1_dt_wall
        _st = {"n": 0}

        def noisy(cd, t):
            _st["n"] += 1
            base = real_q1(cd, t)
            return base + (0.0 if _st["n"] % 2 == 1 else base * 2.0 ** -52)
        q1_dt_wall = noisy
        fired = False
        try:
            planted_zero_control(c, END_TIME)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        finally:
            q1_dt_wall = real_q1
        res["S3_noisy_refuses"] = fired

        # S4 -- UNDERSIZED plant: patch one face instead of all -> clause 5 fires
        real_plant = _plant_lines_patch
        def undersized(fp, patch):
            lines, idxs, kind = real_plant(fp, patch)
            return lines, idxs[:1], kind          # only the first face
        _plant_lines_patch = undersized
        fired = False
        try:
            planted_zero_control(c, END_TIME)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        finally:
            _plant_lines_patch = real_plant
        res["S4_undersized_refuses"] = fired

        # S5 -- FLOOR-tied refusal: with the plant written at writePrecision 4
        # (quantum ~0.1 K near 288 K), small plants round away, the demonstrated
        # floor rises above FLOOR_LIMIT and clause 9 REFUSES.
        c5 = _forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0)
        saved_fmt = PLANT_FMT
        PLANT_FMT = "%.4g"
        fired = False
        try:
            planted_zero_control(c5, END_TIME)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        finally:
            PLANT_FMT = saved_fmt
        res["S5_floor_refuses"] = fired

        # S6 -- SIGNED arm: a reader that abs()es the difference must REFUSE.
        real_q1 = q1_dt_wall
        base_ref = real_q1(c, END_TIME)
        def absreader(cd, t):
            return abs(real_q1(cd, t) - base_ref) + base_ref   # abs() the difference
        q1_dt_wall = absreader
        fired = False
        try:
            planted_zero_control(c, END_TIME)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        finally:
            q1_dt_wall = real_q1
        res["S6_signed_refuses"] = fired

        # S7 -- balance BOTH directions
        theta5 = math.radians(5.0)
        ps = EX.p_sector(100.0, theta5)
        # +10% source: integral 10% larger -> B_planted - B_unplanted ~ 0.10
        c_un = _forge_complete_case(tmp, "T21_CYL_f", 100.0, 32, 96, 80, 5.0, whf=-ps)
        c_pl = _forge_complete_case(tmp, CASE_S10, 110.0, 32, 96, 80, 5.0, whf=-ps * 1.10)
        b_un = q3_balance(c_un, ps)
        b_pl = q3_balance(c_pl, ps)
        s7a = abs(b_un - 1.0) <= BAL_UNPLANTED and BAL_PLANTED[0] <= (b_pl - b_un) <= BAL_PLANTED[1]
        # 0% difference must return < 0.005
        c_zero = _forge_complete_case(tmp, CASE_S10, 100.0, 32, 96, 80, 5.0, whf=-ps)
        s7b = abs(q3_balance(c_zero, ps) - b_un) < 0.005
        res["S7_balance_both"] = s7a and s7b

        # S8 -- the rule-4 completion conjuncts, one forged violation each
        s8 = []
        clean = _forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0)
        s8.append(completion_of(clean)[0] is True)                       # a clean tree passes
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_m", 100.0, 16, 48, 40, 5.0, rc=1))[0] is False)
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0, end_line=False))[0] is False)
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_m", 100.0, 16, 48, 40, 5.0, last_time=2994))[0] is False)
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0, drop_field=("housing", "T")))[0] is False)
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_m", 100.0, 16, 48, 40, 5.0, exec_count=END_TIME - 1))[0] is False)
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0, age_ok=False))[0] is False)
        # the T19b tree: last time 828 << endTime but STATUS rc=0, note=clean
        s8.append(completion_of(_forge_complete_case(tmp, "T21_CYL_m", 100.0, 16, 48, 40, 5.0, last_time=828))[0] is False)
        res["S8_completion"] = all(s8)

        # S9 -- 'but never used' drives exit 2
        c9 = _forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0, never_used=True)
        fired = False
        try:
            grep_never_used(c9)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        res["S9_never_used"] = fired

        # S10 -- wedge-factor: (a) Su=P_full (72x error) REFUSES; (b) correct Su
        # with a mesh at 1 deg while the value is for 5 deg REFUSES; (c) the
        # theta-recompute ACCEPTS the real Su while a hard-coded 5 deg on a mesh
        # that is exactly 5 deg would also accept -- the discriminator is the
        # ~1.4e-10 gap when the mesh theta != radians(5).
        c10 = _forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0)
        s10 = []
        # (a) overwrite fvOptions with the full-cylinder value P_full (72x)
        _forge_fvoptions(c10, 100.0)
        try:
            wedge_factor_assert(c10, 100.0)
            s10.append(False)
        except SystemExit as e:
            s10.append(e.code == EXIT_REFUSE)
        # (b) correct 5deg Su but the mesh rebuilt at 1 deg
        _forge_fvoptions(c10, EX.p_sector(100.0, math.radians(5.0)))
        _forge_blockmesh(c10, 1.0)
        try:
            wedge_factor_assert(c10, 100.0)
            s10.append(False)
        except SystemExit as e:
            s10.append(e.code == EXIT_REFUSE)
        # (c) THE LANDMINE, demonstrated: the real producer round-trip (Su from
        # the mesh-read-back theta, as _forge_complete_case builds it) is ACCEPTED
        # by the mesh-recompute consumer and REFUSED by a hard-coded-5deg consumer
        # at ~1.4e-10 > 1e-12.
        c10b = _forge_complete_case(tmp, "T21_CYL_c", 100.0, 8, 24, 20, 5.0)
        su_real = read_su_from_fvoptions(c10b)
        theta_mesh = theta_from_mesh(c10b)
        exp_hard = EX.p_sector(100.0, math.radians(5.0))
        gap = abs(su_real - exp_hard) / abs(exp_hard)
        res["S10c_landmine_gap"] = (1e-12 < gap < 1e-8)  # the real ~1.4e-10 gap
        try:
            wedge_factor_assert(c10b, 100.0)     # mesh-recompute ACCEPTS
            accept = True
        except SystemExit:
            accept = False
        try:
            wedge_factor_assert(c10b, 100.0, hardcoded_theta_deg=5.0)  # REFUSES
            refuse_hard = False
        except SystemExit as e:
            refuse_hard = (e.code == EXIT_REFUSE)
        s10.append(accept and refuse_hard)
        res["S10_wedge_factor"] = all(s10)

        # VC -- VALUE CONTROL, grade() end-to-end on the analytic solution.  The
        # patch drop carries a second-order 1/nr^2 term (disc_err) so the Q1
        # triple is CONVERGING at p~2 and grades PASS; Q2 (ring drop) grades PASS
        # against EX.dT_cells; the anti-degeneracy control shows Q1 != Q2.
        vroot = os.path.join(tmp, "vc")
        ps5 = EX.p_sector(100.0, math.radians(5.0))
        for case, nr_h, nr_c, nz in (("T21_CYL_c", 8, 24, 20), ("T21_CYL_m", 16, 48, 40),
                                     ("T21_CYL_f", 32, 96, 80)):
            _forge_complete_case(vroot, case, 100.0, nr_h, nr_c, nz, 5.0,
                                 disc_err=1.0, whf=(-ps5 if case == "T21_CYL_f" else None))
        vj = os.path.join(tmp, "vc_gate.json")
        vcode, vres = None, None
        try:
            vcode = grade(vroot, vj)
            vres = json.load(open(vj)) if os.path.isfile(vj) else None
        except SystemExit as e:
            vcode = e.code
        vr = {r["row"]: r for r in vres["rows"]} if vres else {}
        res["VC_value_control"] = bool(
            vcode == EXIT_OK and vres and
            vr.get("Q1", {}).get("verdict") == "PASS" and
            vr.get("Q2", {}).get("verdict") == "PASS" and
            vres["anti_degeneracy"]["differ"] is True and
            vres["planted_zero_controls"] is not None)
        # a GATE FAIL counterpart: a large extra_err at fine pushes Q1 out of band
        vroot2 = os.path.join(tmp, "vc2")
        for case, nr_h, nr_c, nz in (("T21_CYL_c", 8, 24, 20), ("T21_CYL_m", 16, 48, 40),
                                     ("T21_CYL_f", 32, 96, 80)):
            _forge_complete_case(vroot2, case, 100.0, nr_h, nr_c, nz, 5.0, disc_err=1.0,
                                 extra_err=(0.05 * EX.dT_wall(100.0) if case == "T21_CYL_f" else 0.0),
                                 whf=(-ps5 if case == "T21_CYL_f" else None))
        vj2 = os.path.join(tmp, "vc2_gate.json")
        try:
            grade(vroot2, vj2)
        except SystemExit:
            pass
        vres2 = json.load(open(vj2)) if os.path.isfile(vj2) else None
        vr2 = {r["row"]: r for r in vres2["rows"]} if vres2 else {}
        # Q1 fine perturbed by 5% -> triple broken (extra only at fine) => NOT A
        # RESULT or GATE FAIL, but NOT PASS: the clean/defect pair must differ.
        res["VC_gate_fail_counterpart"] = bool(vr2 and vr2.get("Q1", {}).get("verdict") != "PASS")

        # RG -- the REFERENT REPRODUCIBILITY guard must FIRE on a non-reproducible
        # reference and stay QUIET on the true one (proving it is not vacuous).
        real_dtw = EX.dT_wall
        EX.dT_wall = lambda *a, **k: real_dtw(*a, **k) * 1.001   # 0.1% wrong
        fired = False
        try:
            check_referents_reproducible()
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        finally:
            EX.dT_wall = real_dtw
        quiet = True
        try:
            check_referents_reproducible()
        except SystemExit:
            quiet = False
        res["RG_guard_fires_on_defect"] = fired
        res["RG_guard_quiet_on_clean"] = quiet

        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def selftest():
    import ast
    print("analyse_t21 selftest -- synthetic forged trees only (S11)")
    # S11: run the whole limb set twice, against an EMPTY ambient run root and a
    # POPULATED one, and require byte-identical results.
    a_root = tempfile.mkdtemp(prefix="t21_ambientA_")   # empty
    b_root = tempfile.mkdtemp(prefix="t21_ambientB_")   # populated
    try:
        for case in list(TRIPLE_CASES.values()) + [CASE_S10, CASE_W1, CASE_P1000]:
            _forge_complete_case(b_root, case, P_OF_CASE.get(case, 100.0),
                                 NR_HOUSING.get(case, 32), 3 * NR_HOUSING.get(case, 32),
                                 2 * NR_HOUSING.get(case, 32), 5.0, whf=-EX.p_sector(100.0, math.radians(5.0)))
        resA = _run_limbs(a_root)
        resB = _run_limbs(b_root)
    finally:
        shutil.rmtree(a_root, ignore_errors=True)
        shutil.rmtree(b_root, ignore_errors=True)
    s11 = (json.dumps(resA, sort_keys=True) == json.dumps(resB, sort_keys=True))

    order = ("S1_both_signs", "S2_blind_refuses", "S3_noisy_refuses", "S4_undersized_refuses",
             "S5_floor_refuses", "S6_signed_refuses", "S7_balance_both", "S8_completion",
             "S9_never_used", "S10_wedge_factor", "S10c_landmine_gap",
             "VC_value_control", "VC_gate_fail_counterpart",
             "RG_guard_fires_on_defect", "RG_guard_quiet_on_clean")
    fails = []
    for k in order:
        ok = bool(resA.get(k))
        print("  [%s] %s" % ("ok " if ok else "FAIL", k))
        if not ok:
            fails.append(k)
    print("  [%s] S11_invariance: limb results byte-identical, empty vs populated ambient run root"
          % ("ok " if s11 else "FAIL"))
    if not s11:
        fails.append("S11_invariance")

    # the no-assert instrument standard: 0 AST assert nodes in this file
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t21.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json)


if __name__ == "__main__":
    sys.exit(main())
