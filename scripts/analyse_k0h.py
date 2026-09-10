#!/usr/bin/env python3
"""K0d comparator -- THE GRADER.  Written from the FROZEN registration only.

  docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md   (OPERATIVE)
  docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md  (SUPERSEDED --
      cited ONLY where the re-registration adopts it BY CITATION, which it does
      for section 7.3's ten rows, section 7.2's conversion rule and bands,
      section 7.5's five guards, and section 8.1's three planted-zero controls.)

CITE THE CAP FROM THE RE-REGISTRATION AND FROM NOWHERE ELSE.  The superseded
document's section 10.3 still reads "CAP 2 484.84" and all five of its
amendments say "No CAP moved"; the OPERATIVE cap is 2 748.64 core-min
(re-registration AMENDMENT 2 section A2.2b).  This script grades and does not
spend, so it enforces no cap -- the note is here because the trap is one line
away in a file this script cites.

WHAT THIS RUNG CAN EARN, AND THE SCRIPT PRINTS IT RATHER THAN WORKING AROUND IT
-------------------------------------------------------------------------------
Re-registration section 0 and AMENDMENT 2 section A2.4:  Blay, Mergui and
Niculae (1992) is NOT OBTAINED.  Column V is reachable, column G is reachable,
COLUMN P IS NOT.  Every graded row is BLOCKED under the section 7.4 ladder's
order 4 while that holds, the tally is 0 of 10, and

    THE RUNG VERDICT IS `GATE REACHED`, NAMING `P` AS THE UNREACHED COLUMN.
    IT CAN NEVER READ `HOLDS` IN THIS STATE.

This script prints that verdict.  It does not print a graded verdict it cannot
support, and no invocation flag makes it do so.

THE THREE REGISTERED PLANTS (superseded section 8.1, adopted by re-registration
section 7.4) -- AND WHY THEY GO WHERE THEY GO
-------------------------------------------------------------------------------
  P1  PLANT_T = 1.234e-03 K into a COPY of the GRADED TIME-AVERAGE scalar field
      GRADED_CASE/<avg2>/TMean -- i.e. the kOmegaSST L2 arm M1_m's TMean over
      the avg2 window [40, 60] s, at the time directory that window is written
      to (AVG2_TIME) -- BY LINE INDEX, never by regex over the value, read back
      THROUGH THE PRODUCTION SCALAR FIELD READER, the same call the graded path
      uses on TMean.  exit 2 if unseen.
  P2  PLANT_U = 1.234e-03 m/s into the X-COMPONENT of a copy of the GRADED
      TIME-AVERAGE vector field GRADED_CASE/<avg2>/UMean (M1_m's UMean over the
      avg2 window), read back through the production VECTOR reader.  exit 2 if
      unseen.  Registered separately because velocity rows are graded on UMean
      and A SCALAR PLANT DOES NOT EXERCISE THE VECTOR PARSER.
  P3  NEGATIVE CONTROL: a plant of exactly 0.0 into a copy of the same TMean.
      The reader must report NOT DISTINGUISHABLE FROM THE BACKGROUND.  IF P3
      "FIRES", THE CONTROL IS BROKEN and this script exits 2.

AMENDMENT 2 section A2.3 is the reason each plant names its channel out loud.
There, a planted control planted into a MODIFIED SPECIFICATION rather than a
modified mesh, and a real hole passed a green selftest.  THESE THREE PLANT INTO
A FIELD ON DISK AND ARE READ BACK THROUGH THE READER THAT PRODUCES THE GRADED
NUMBER.  A plant into a dict, a spec or a constants table would be the same
defect one layer up.

STANDING CONSEQUENCE (superseded 8.1): a graded row returning a deviation of
EXACTLY ZERO is NOT A RESULT unless P1/P2 demonstrated on the SAME READER IN
THE SAME INVOCATION that a non-zero is visible.  A zero is a result only when it
is a supported zero.

A DISCLOSED READING, FLAGGED FOR THE SUPERVISOR'S DIFF READ
-------------------------------------------------------------------------------
AMENDMENT 1 section A1.3a registers setFormat `raw`, interpolationScheme
`cellPoint` (graded) and `cell` (control), a `uniform` sample set of nPoints
2081 on each mid-plane line, and the mid-thickness cell-centre plane.  Those are
OpenFOAM `sample` parameters.  THIS COMPARATOR PERFORMS THE EXTRACTION ITSELF
from the mesh and the field files rather than reading .xy files written by
postProcess, and the reading is disclosed rather than taken silently:

  * The registered SEMANTICS are implemented exactly -- 2081 uniform points at
    5.000e-04 m spacing on the registered start/end lines; `cell` is
    piecewise-constant lookup in the containing cell; `cellPoint` is
    interpolation from vertex values formed by averaging the cells sharing each
    vertex, which is what cellPoint does on a structured hex mesh.
  * IT IS DONE THIS WAY BECAUSE SECTION 8.1 REQUIRES THE PLANT TO BE READ BACK
    "THROUGH THE PRODUCTION FIELD READER, THE SAME CALL THE GRADED PATH USES".
    If the graded number came from a .xy file written by a separate utility, a
    plant into the field would exercise a reader the graded path never calls --
    the A2.3 defect exactly.  Making the field reader the production reader is
    what gives P1 and P2 their force.
  * IT INTRODUCES NO FREE PARAMETER: every number above is registered.
  * THE MESH ORDERING IS ASSERTED, NEVER ASSUMED.  build_index() refuses (exit
    2) unless the cell count implied by the mesh equals the length of the field
    it is asked to index.

REFUSE RATHER THAN DEGRADE.  Every clause below exits 2 rather than grading
something it cannot stand behind.

Exit codes:  0  the analysis completed and its verdict is printed
             1  a graded row is GATE FAIL (unreachable while P is unreachable)
             2  REFUSAL -- a plant unseen, the negative control fired, a marker
                missing, a mesh unreadable, a field compressed, an ordering
                assertion failed, or any registered input absent

Usage:
    python3 analyse_k0h.py --root <K0h_runs dir>
    python3 analyse_k0h.py --selftest
"""

# ========================================================================
# K0h DERIVATION BLOCK -- READ THIS BEFORE THE DIFF.
#
# This file is a DERIVATION of the FROZEN K0g instrument
#     scripts/analyse_k0g.py
#     git blob 409e403d0c648b88d05ca5e06a466c11588ddd8a
# registered at docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md
# section 7.7.  THE K0g ANCESTOR IS NOT EDITED (standing rule 6); this
# file was written from its HEAD BLOB, not from the worktree.
#
# THE DERIVATION IS MECHANICALLY CHECKABLE.  Outside this block every
# byte of this file is the ancestor's bytes under the UNCONDITIONAL
# substitution
#     k0g -> k0h ,  K0g -> K0h ,  K0G -> K0H
# PLUS EXACTLY ONE FUNCTIONAL CHANGE, and it is the only functional change
# in the whole K0h grading path: section 4.5's `fieldAverage` nonuniform-patch
# resolution and its `P4` planted control.  Every hunk of it is marked
# `K0h SEC 4.5` or `K0h P4` in a comment on its first line, so the diff read
# can be done by grepping those two tokens.
#
# CONSEQUENCE OF AN UNCONDITIONAL RENAME, DISCLOSED RATHER THAN
# SMOOTHED.  A historical note below that now reads "K0h attempt 1",
# "measured on K0h" or similar describes an event that happened under
# K0g, this file's ancestor.  NO HISTORICAL CLAIM IN THIS FILE IS A K0h
# MEASUREMENT.  K0h HAS RUN NO COMPUTE: no
# verification/runs/F14-cooling-ladder/K0h_runs/ exists, and none may be
# created until the supervisor FREEZES the pre-registration by sha.
#
# PROVENANCE PINS -- DECLARATIVE AND PRINT-ONLY.  They gate nothing and
# no code branches on them.  GRADING_PATH_FREEZE_COMMIT is the DRAFT
# placeholder "PIN-AT-FREEZE"; THE SUPERVISOR SETS IT AT FREEZE and no
# lane, and no run, sets it.
# ========================================================================
GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"   # SUPERVISOR SETS THIS AT FREEZE
SELF_REL = "scripts/analyse_k0h.py"
GRADING_PATH = (
    "docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md",
    "scripts/analyse_k0h.py",
    "scripts/build_k0h.py",
    "scripts/check_k0h_mesh.py",
    "scripts/mark_done_k0h.py",
    "scripts/check_k0h_extraction_equivalence.py",
    "scripts/check_k0h_instrument_standard.py",
    "scripts/launch_k0h.sh",
    "scripts/launch_k0h_selftest.sh",
)
import argparse
import math
import os
import re
import shutil
import sys

EXIT_OK, EXIT_GATEFAIL, EXIT_REFUSE = 0, 1, 2

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS.  Every one carries the clause that fixes it.
# Nothing in this block is a choice made by this script.
# --------------------------------------------------------------------------

# superseded section 8.1, adopted by re-registration section 7.4
PLANT_T = 1.234e-03          # K
PLANT_U = 1.234e-03          # m/s, into the X-COMPONENT
PLANT_ZERO = 0.0             # P3, the negative control

# K0h pre-registration section 5: FIVE authorised arms (L1+L2, two turbulent
# closures, plus C_lam the discrimination control).  L3 and the guard/sweep arms
# (B_hi, I_hi, M1_m_seed) are DEFINED-AND-NOT-AUTHORISED and are absent here, so
# NO ROACHE TRIPLE IS FORMED (a triple needs three levels; K0h authorises two).
CASES = ["M1_c", "M1_m", "M2_c", "M2_m", "C_lam"]
GRADED_CASE = "M1_m"                        # the kOmegaSST L2 arm: plants + the
#                                            equivalence gate + the graded rows
CLOSURE_OF_CASE = {
    "M1_c": "kOmegaSST", "M1_m": "kOmegaSST",
    "M2_c": "RNGkEpsilon", "M2_m": "RNGkEpsilon",
    "C_lam": "laminar",
}
LEVEL_OF_CASE = {
    "M1_c": "L1", "M1_m": "L2",
    "M2_c": "L1", "M2_m": "L2", "C_lam": "L2",
}

# K0h GRADES THE TIME-AVERAGE, NOT THE INSTANTANEOUS FIELD.  The graded fields
# are the fieldAverage outputs of the avg2 window [40, 60] s -- TMean and UMean
# -- written by OpenFOAM at the endTime directory.  Every place K0f read `T`/`U`
# to grade, K0h reads these.
GRADED_T = "TMean"
GRADED_U = "UMean"

# re-registration section 1: geometry and fluid state
DOMAIN = 1.040               # m
H = 1.040                    # m, cavity height
U_IN = 0.57                  # m/s, section 1
DT_BAND = 20.0               # K, section 4, frozen INDEPENDENTLY of nu and beta
NU = 1.569e-5                # m2/s, section 1.1 (AMENDMENT 1 ruling)
PR = 0.71
T_REF = 298.00               # K, section 1.2

# AMENDMENT 1 section A1.3a -- the registered extraction
N_POINTS = 2081
SAMPLE_SPACING = 5.000e-04   # m, i.e. 1.04/2080
VERTICAL_X = 0.52            # vertical mid-plane set, x = 0.52
HORIZONTAL_Y = 0.52          # horizontal mid-plane set, y = 0.52
SCHEME_GRADED = "cellPoint"
SCHEME_CONTROL = "cell"

# superseded section 7.2 as REPLACED by AMENDMENT 4 section A4.5:
# THIRTEEN stations, not eleven.  0.25 and 0.75 are the two additions.
STATIONS = (0.05, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50,
            0.60, 0.70, 0.75, 0.80, 0.90, 0.95)
STATION_MATCH_TOL = 0.01     # section 7.2, the UNMEASURED rule

# superseded section 7.3, adopted byte-unchanged by re-registration section 4.
# scale: DT = 20.0 K, UIN = 0.57 m/s, HGT = 1.04 m, REF = |q_ref|
ROWS = {
    "G1":  dict(kind="profile", field="T", line="vertical",   comp=None,
                scale="DT",  R=0.05, band=1.00,   units="K"),
    "G2":  dict(kind="profile", field="T", line="horizontal", comp=None,
                scale="DT",  R=0.05, band=1.00,   units="K"),
    "G3":  dict(kind="profile", field="U", line="vertical",   comp=0,
                scale="UIN", R=0.10, band=0.0570, units="m/s"),
    "G4":  dict(kind="profile", field="U", line="horizontal", comp=1,
                scale="UIN", R=0.10, band=0.0570, units="m/s"),
    "G5a": dict(kind="scalar",  scale="UIN", R=0.10, band=0.0570, units="m/s"),
    "G5b": dict(kind="scalar",  scale="HGT", R=0.02, band=0.0208, units="m"),
    "G6":  dict(kind="scalar",  scale="REF", R=0.10, band=None,   units="-"),
    "G7":  dict(kind="scalar",  scale="DT",  R=0.05, band=1.00,   units="K"),
    "G8":  dict(kind="scalar",  scale="HGT", R=0.10, band=0.104,  units="m"),
    "S1":  dict(kind="structural", scale=None, R=None, band=None, units="-"),
}
GRADED_ROWS = ("G1", "G2", "G3", "G4", "G5a", "G5b", "G6", "G7", "G8", "S1")
# REPORTED, NEVER GRADED (superseded 7.3): R1 (tke) and M0 (Boussinesq floor)
REPORTED_ROWS = ("R1", "M0")
M0_VELOCITY_PCT = 1.65       # AMENDMENT 2: reported beside every velocity row
M0_NUSSELT_PCT = 0.031       # and beside G6.  NEVER SUBTRACTED from a deviation.

# AMENDMENT 1 section A1.3b -- the dual-scheme control
DUAL_SCHEME_ROWS = ("G1", "G2", "G3", "G4", "G5b", "G8")

# re-registration section 4 -- the y+ windows
YPLUS_WINDOW = {"L1": 5.0, "L2": 3.3, "L3": 3.3}

# superseded section 7.5 -- the five guards
HEAT_BALANCE_TOL_PCT = 0.5   # docs/physics_rules.yaml:324
DISCRIMINATION_PCT = 25.0    # guard DC, Charter 2c
GUARD_B_TOL_K = 1.00         # guard B

# re-registration section 5 -- the ladder, UNEQUAL ratios (T3 section 7.1 form)
R21 = 1.400000               # sqrt(50176/25600)
R32 = 1.401786               # sqrt(98596/50176)
GCI_FS = 1.25                # standing rule 5: Fs = 1.25, always

# K0h pre-registration section 7.1' -- STATIONARITY, not steady convergence.
# The instrument is the drift of the running TIME-AVERAGE between two equal
# half-windows, avg1 = [20,40] s and avg2 = [40,60] s, read from the endTime
# directories the solver wrote them into.  Tolerances are PHYSICAL, frozen
# before the run, and NEVER widened: tol_T = 1e-3 * DT (0.020 K); tol_U =
# 0.005 m/s (~6e-3 * the buoyancy velocity U_b = sqrt(g*beta*DT*H) = 0.8275 m/s).
REGISTERED_END_TIME = 60.0
AVG1_TIME = "40"            # time dir holding TMean/UMean over [20,40] s (avg1)
AVG2_TIME = "60"           # time dir holding TMean/UMean over [40,60] s (avg2)
STAT_TOL_T = 0.020         # K
STAT_TOL_U = 0.005         # m/s, per component

# superseded section 7.6 -- the reference slot
REFERENCE_BASENAME = "K0d_reference_primary.json"

# rule 1 vocabulary, and NOTHING ELSE may be printed as a verdict
PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
VOCABULARY = (PASS, GATE_REACHED, GATE_FAIL, NOT_A_RESULT, BLOCKED, PENDING)
# non-verdict row states, kept distinct from the vocabulary on purpose
REPORTED, UNMEASURED = "REPORTED", "UNMEASURED"


def refuse(msg):
    """REFUSE (exit 2) rather than degrade.  Superseded 8.1, last line."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# THE PRODUCTION FIELD READER.  The plants of section 8.1 are read back
# through THESE functions, and the graded path calls THESE functions.  If that
# stops being true the plants stop being evidence (AMENDMENT 2 section A2.3).
# --------------------------------------------------------------------------
def field_path(tdir, field):
    """Path of `field` in `tdir`.  REFUSES on the compressed form.

    AMENDMENT 2 section A2.1a fixes writeFormat = ascii and section A2.1c fixes
    writeCompression = off.  A compressed field is therefore a case that did not
    honour its own registration, and this reader says so rather than silently
    coping."""
    plain = os.path.join(tdir, field)
    if os.path.isfile(plain):
        return plain
    if os.path.isfile(plain + ".gz"):
        refuse(f"{plain}.gz is COMPRESSED.  AMENDMENT 2 section A2.1c registers "
               f"writeCompression = off and section A2.1a registers writeFormat "
               f"= ascii.  Refusing rather than reading a field the registration "
               f"says should not exist in this form.")
    return None


def _read_lines(path):
    with open(path, "r") as fh:
        return fh.read().split("\n")


def locate_internal_field(lines):
    """Locate internalField and return a description INCLUDING LINE INDICES.

    The line indices are what makes planting BY LINE INDEX possible.  Section
    8.1 requires the plant to go in by line index and NEVER by a regex over the
    value -- a regex over the value can silently match the wrong occurrence, and
    a plant that lands somewhere unknown proves nothing."""
    for i, ln in enumerate(lines):
        if not ln.strip().startswith("internalField"):
            continue
        m = re.match(r"\s*internalField\s+uniform\s+(.+?);\s*$", ln)
        if m:
            return dict(mode="uniform", raw=m.group(1).strip(), decl_line=i)
        if "nonuniform" in ln:
            # <count> then "(" then the values then ")" then ";"
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines):
                return None
            cnt_line = lines[j].strip()
            if not re.fullmatch(r"[0-9]+", cnt_line):
                # count may sit on the declaration line
                m2 = re.search(r"nonuniform\s+List<\w+>\s+([0-9]+)", ln)
                if not m2:
                    return None
                count = int(m2.group(1))
                j = i
            else:
                count = int(cnt_line)
            k = j
            while k < len(lines) and lines[k].strip() != "(":
                k += 1
            if k >= len(lines):
                return None
            return dict(mode="nonuniform", count=count,
                        decl_line=i, first_value_line=k + 1)
    return None


def _parse_scalar(tok):
    try:
        return float(tok)
    except ValueError:
        refuse(f"cannot parse {tok!r} as a scalar in an internalField")


def _parse_vector(tok):
    m = re.fullmatch(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)", tok.strip())
    if not m:
        refuse(f"cannot parse {tok!r} as a vector in an internalField")
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)))


def read_scalar_field(path, n_cells=None):
    """PRODUCTION SCALAR READER.  P1 and P3 are read back through this."""
    lines = _read_lines(path)
    info = locate_internal_field(lines)
    if info is None:
        refuse(f"{path}: no internalField could be located")
    if info["mode"] == "uniform":
        if n_cells is None:
            refuse(f"{path}: a uniform internalField needs the cell count to "
                   f"expand, and none was supplied.  Refusing rather than "
                   f"guessing a length.")
        return [_parse_scalar(info["raw"])] * n_cells
    out = []
    idx = info["first_value_line"]
    for _ in range(info["count"]):
        out.append(_parse_scalar(lines[idx].strip()))
        idx += 1
    return out


def read_vector_field(path, n_cells=None):
    """PRODUCTION VECTOR READER.  P2 is read back through this.

    It is a SEPARATE parser from read_scalar_field, which is exactly why
    section 8.1 registers P2 separately: a scalar plant does not exercise it."""
    lines = _read_lines(path)
    info = locate_internal_field(lines)
    if info is None:
        refuse(f"{path}: no internalField could be located")
    if info["mode"] == "uniform":
        if n_cells is None:
            refuse(f"{path}: a uniform vector internalField needs the cell count")
        return [_parse_vector(info["raw"])] * n_cells
    out = []
    idx = info["first_value_line"]
    for _ in range(info["count"]):
        out.append(_parse_vector(lines[idx].strip()))
        idx += 1
    return out


# --------------------------------------------------------------------------
# THE THREE REGISTERED PLANTS.  Each writes a KNOWN perturbation INTO A FIELD
# ON DISK, at a LINE INDEX, and reads it back through the production reader.
# --------------------------------------------------------------------------
def plant_into_scalar_copy(src, dst, cell_index, value):
    """Copy `src` to `dst` and overwrite the value of cell `cell_index`
    BY LINE INDEX.  Returns the line index written, for the record.

    NOT a regex over the value.  NOT a plant into a spec, a dict or a constants
    table -- into the FIELD FILE the graded path reads (AMENDMENT 2 A2.3)."""
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: P1/P3 require a nonuniform internalField to plant into "
               f"by line index; a uniform field has no per-cell line to target.")
    if not (0 <= cell_index < info["count"]):
        refuse(f"{src}: plant index {cell_index} outside 0..{info['count'] - 1}")
    line_idx = info["first_value_line"] + cell_index
    lines[line_idx] = repr(float(value))
    with open(dst, "w") as fh:
        fh.write("\n".join(lines))
    return line_idx


def plant_into_vector_copy(src, dst, cell_index, x_value):
    """As above, into the X-COMPONENT of a vector field, by line index."""
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: P2 requires a nonuniform internalField to plant into")
    if not (0 <= cell_index < info["count"]):
        refuse(f"{src}: plant index {cell_index} outside 0..{info['count'] - 1}")
    line_idx = info["first_value_line"] + cell_index
    old = _parse_vector(lines[line_idx])
    lines[line_idx] = f"({float(x_value)!r} {old[1]!r} {old[2]!r})"
    with open(dst, "w") as fh:
        fh.write("\n".join(lines))
    return line_idx


def run_planted_controls(tdir, scratch, cell_index=0, verbose=True):
    """P1, P2 and P3, in one invocation, on the graded case's own fields.

    RETURNS a dict recording what each plant proved.  EXITS 2 if P1 or P2 is
    unseen, or if P3 fires.  Superseded section 8.1."""
    os.makedirs(scratch, exist_ok=True)
    rec = {}

    t_src = field_path(tdir, GRADED_T)
    u_src = field_path(tdir, GRADED_U)
    if t_src is None:
        refuse(f"{tdir}: no {GRADED_T} field, so P1 and P3 cannot be planted.  A "
               f"comparator that skips its planted control is not evidence.")
    if u_src is None:
        refuse(f"{tdir}: no {GRADED_U} field, so P2 cannot be planted.")

    background = read_scalar_field(t_src)
    if not background:
        refuse(f"{t_src}: empty internalField")

    # ---- P1: PLANT_T into a copy of T, by line index, production reader -----
    p1_dst = os.path.join(scratch, "P1_T")
    line = plant_into_scalar_copy(t_src, p1_dst, cell_index, PLANT_T)
    seen = read_scalar_field(p1_dst)[cell_index]
    if seen != PLANT_T:
        refuse(f"P1 FAILED: planted {PLANT_T!r} K into cell {cell_index} "
               f"(line {line}) of a copy of {t_src} and the PRODUCTION SCALAR "
               f"READER read back {seen!r}.  A reader not shown able to see a "
               f"non-zero is not evidence (standing rule 3).")
    rec["P1"] = dict(value=PLANT_T, cell=cell_index, line=line, seen=seen,
                     reader="read_scalar_field", ok=True)
    if verbose:
        print(f"  P1  PLANT_T {PLANT_T:.6e} K -> cell {cell_index} "
              f"(line {line}) of a COPY of T; production scalar reader SAW IT.")

    # ---- P2: PLANT_U into the X-COMPONENT, production VECTOR reader ---------
    p2_dst = os.path.join(scratch, "P2_U")
    line2 = plant_into_vector_copy(u_src, p2_dst, cell_index, PLANT_U)
    seen2 = read_vector_field(p2_dst)[cell_index][0]
    if seen2 != PLANT_U:
        refuse(f"P2 FAILED: planted {PLANT_U!r} m/s into the X-COMPONENT of "
               f"cell {cell_index} (line {line2}) of a copy of {u_src} and the "
               f"PRODUCTION VECTOR READER read back {seen2!r}.  Six of the ten "
               f"graded rows are velocity rows and a scalar plant does not "
               f"exercise this parser (superseded section 8.1).")
    rec["P2"] = dict(value=PLANT_U, cell=cell_index, line=line2, seen=seen2,
                     reader="read_vector_field", ok=True)
    if verbose:
        print(f"  P2  PLANT_U {PLANT_U:.6e} m/s -> x-component of cell "
              f"{cell_index} (line {line2}) of a COPY of U; production VECTOR "
              f"reader SAW IT.")

    # ---- P3: the NEGATIVE control.  It must NOT be distinguishable. --------
    # "a plant of exactly 0.0 ... the reader must report NOT DISTINGUISHABLE
    #  FROM THE BACKGROUND.  If P3 fires, the control is broken and the
    #  comparator exits 2."
    #
    # P3 plants 0.0 ON TOP OF a cell whose background value is already 0.0, so
    # a correct reader sees NO CHANGE.  Firing means the reader reports a
    # difference where the field did not change -- a reader that invents signal.
    p3_base = os.path.join(scratch, "P3_base")
    plant_into_scalar_copy(t_src, p3_base, cell_index, PLANT_ZERO)
    p3_dst = os.path.join(scratch, "P3_T")
    plant_into_scalar_copy(p3_base, p3_dst, cell_index, PLANT_ZERO)
    base_val = read_scalar_field(p3_base)[cell_index]
    p3_val = read_scalar_field(p3_dst)[cell_index]
    distinguishable = (p3_val != base_val)
    if distinguishable:
        refuse(f"P3 FIRED, SO THE CONTROL IS BROKEN: planting exactly "
               f"{PLANT_ZERO!r} onto a cell already holding {base_val!r} "
               f"produced {p3_val!r}, which the reader called DISTINGUISHABLE. "
               f"A negative control that fires means the positive controls P1 "
               f"and P2 prove nothing (superseded section 8.1).")
    rec["P3"] = dict(value=PLANT_ZERO, cell=cell_index, seen=p3_val,
                     distinguishable=False, ok=True)
    if verbose:
        print(f"  P3  NEGATIVE CONTROL: a 0.0 plant onto a 0.0 background is "
              f"NOT DISTINGUISHABLE FROM THE BACKGROUND, as registered.")

    # ---- P4: THE REPAIRED BOUNDARY PATH (K0h section 4.5, section 7.4) -----
    # Registered because the section 4.5 path would otherwise be THE ONE
    # CHANNEL IN THIS COMPARATOR WITH NO PLANTED-ZERO CONTROL.  It refuses.
    rec["P4"] = run_p4(tdir, t_src, scratch, verbose=verbose)

    rec["nonzero_visible"] = True   # gates the exactly-zero rule below
    return rec


# --------------------------------------------------------------------------
# K0h P4 -- THE FOURTH REGISTERED PLANT, ON THE SECTION 4.5 REPAIRED PATH.
#
# K0h_PREREGISTRATION.md section 4.5 / section 7.4:  "a 1.234e-03 K
# perturbation planted into ONE INTERIOR OUTLET-ADJACENT CELL of a COPY of
# TMean(avg2), read back through the production boundary path -- MUST BE SEEN,
# and if the reader cannot see it the comparator REFUSES.  Without P4 the
# repaired path would be the one channel in this comparator with no
# planted-zero control, which is the defect standing rule 3 exists to prevent."
#
# THE REPAIRED READER'S WHOLE JOB IS TO EMIT A VALUE READ OFF A PATCH, so an
# UNPROVEN ZERO THERE WOULD BE EXACTLY THE RULE-3 FAILURE.  P4 plants into a
# FIELD ON DISK, BY LINE INDEX, INTO A COPY -- never the real case, never a
# spec, a dict or a constants table (AMENDMENT 2 section A2.3) -- and reads it
# back through THE SAME calls the graded path makes: read_boundary_values() and
# then _vertex_value(), which is where a `None` patch is resolved from its
# adjacent cell.
#
# TWO ARMS, because one of them is exact and the other is the registered form:
#   P4a  THE REGISTERED FORM.  ONE interior outlet-adjacent cell is planted.
#        The production boundary path must return a DIFFERENT value at an
#        outlet vertex than it did on the unplanted copy.  Unseen => REFUSE.
#   P4b  THE EXACT ARM.  BOTH cells adjacent to the two outlet faces meeting at
#        that vertex are planted with the same value, so the inverse-distance
#        blend of two identical face values is EXACTLY PLANT_T whatever the
#        weights are.  The production path must return PLANT_T EXACTLY.
#        P4a alone proves "something moved"; P4b proves THE PLANTED NUMBER
#        ITSELF came out of the boundary path.
#
# ON A FIELD WHOSE OUTLET PATCH IS WRITTEN IN THE `fieldAverage` FORM (`type
# calculated` + a nonuniform list) THE PLANT ALSO GOES INTO THE MATCHING FACE
# ENTRY OF THAT LIST, BY LINE INDEX.  That is the CONSISTENT form OpenFOAM
# writes (section 4.4, measured bit-identical), so P4 plants a field that could
# have been written by the solver rather than one that could not; and it makes
# P4 exercise the section 4.5 check itself on a field whose values are NOT the
# ones measured pre-compute -- which is what stops the check from being a
# comparison that only ever succeeds because nothing ever changes.
#
# P4 IS NEVER SKIPPED.  On a field whose outlet is written `zeroGradient`
# instead, P4 still plants into the interior cell and still requires the
# production boundary path to see it; the record says which form was exercised.
# A check omitted in silence reads as a check passed (AMENDMENT 2 A2.3c item 5).
# --------------------------------------------------------------------------
def _outlet_probe(idx):
    """K0h P4: (rows, cells, jv) -- the outlet's mesh rows, the interior cells
    adjacent to them, and a mesh vertex jv whose ONLY boundary faces are outlet
    faces.  REFUSES rather than probing a vertex it cannot place."""
    pairs = _patch_face_cells(idx, "outlet")
    if not pairs or len(pairs) < 2:
        refuse(f"P4 CANNOT BE CONSTRUCTED: the registered geometry gives "
               f"{0 if not pairs else len(pairs)} outlet face(s) and P4's exact "
               f"arm needs at least two.  A comparator that skips its planted "
               f"control is not evidence (standing rule 3).")
    rows = [r for r, _ in pairs]
    if rows != list(range(len(rows))):
        refuse(f"P4 CANNOT BE CONSTRUCTED: the outlet rows are {rows[:4]}..., "
               f"not contiguous from j = 0 as the registered geometry "
               f"(section 1: outlet y in [0, 0.024]) requires.  Refusing "
               f"rather than probing a vertex this control cannot place.")
    return rows, [c for _, c in pairs], rows[1]


def plant_into_patch_list_copy(src, dst, patch, elem, value, kind):
    """K0h P4: overwrite ONE element of `patch`'s nonuniform face-value list
    BY LINE INDEX, in a COPY.  Returns the line index written, or None if the
    patch carries no such list.  NOT a regex over the value."""
    loc = _patch_list_location(src, patch)
    if loc is None:
        return None
    count, first, lines = loc
    if not (0 <= elem < count):
        refuse(f"{src}: P4 patch-list index {elem} outside 0..{count - 1}")
    line_idx = first + elem
    if kind == "vector":
        old = _parse_vector(lines[line_idx])
        lines[line_idx] = f"({float(value)!r} {old[1]!r} {old[2]!r})"
    else:
        lines[line_idx] = repr(float(value))
    with open(dst, "w") as fh:
        fh.write("\n".join(lines))
    return line_idx


def run_p4(tdir, t_src, scratch, verbose=True):
    """K0h P4, in the same invocation as P1/P2/P3 and before anything graded is
    read.  EXITS 2 if the production boundary path cannot see the plant."""
    case_dir = os.path.dirname(os.path.abspath(tdir))
    mesh = read_mesh(case_dir)
    nx = len(mesh["x_lines"]) - 1
    ny = len(mesh["y_lines"]) - 1
    base_vals = read_scalar_field(t_src, nx * ny)
    idx = build_index(mesh, len(base_vals))
    rows, cells, jv = _outlet_probe(idx)
    cell0, cell1 = cells[0], cells[1]
    base_b = read_boundary_values(t_src, "scalar")
    v_base = _vertex_value(idx, base_vals, idx["nx"], jv, base_b)
    repaired = _read_patch_list(t_src, "outlet", "scalar") is not None
    form = "fieldAverage calculated+nonuniform" if repaired else "zeroGradient"
    tname = os.path.basename(os.path.abspath(tdir))

    def _stage(tag):
        """A COPY OF THE GRADED TIME DIRECTORY IN SCRATCH, carrying the field
        UNDER ITS REGISTERED NAME, its BASE FIELD, and the case's mesh.

        MEASURED WHILE WRITING THIS FILE: a plant written to a bare scratch
        file called `P4a_TMean` REFUSED -- section 4.5 condition (a) reads the
        BASE FIELD BESIDE the field it is checking, and the reader derives the
        base name by stripping `Mean`, so a renamed copy asks for `P4a_T` in a
        directory with no mesh.  A plant that cannot be read back through the
        PRODUCTION path is not a planted control, so the copy is staged in the
        shape the production reader expects rather than the reader being
        relaxed to accept a copy."""
        cd = os.path.join(scratch, tag)
        td = os.path.join(cd, tname)
        os.makedirs(td, exist_ok=True)
        pm = os.path.join(cd, "constant", "polyMesh")
        os.makedirs(pm, exist_ok=True)
        spts = os.path.join(case_dir, "constant", "polyMesh", "points")
        if not os.path.isfile(spts):
            refuse(f"P4 CANNOT BE CONSTRUCTED: no mesh at {spts}.  A comparator "
                   f"that skips its planted control is not evidence (rule 3).")
        shutil.copyfile(spts, os.path.join(pm, "points"))
        bsrc = field_path(tdir, "T")
        if bsrc is None:
            refuse(f"P4 CANNOT BE CONSTRUCTED: no base field `T` beside "
                   f"{GRADED_T} in {tdir}, so the plant could not be read back "
                   f"through section 4.5's condition (a).  Refusing rather than "
                   f"running a control whose readback path is not the graded "
                   f"one (standing rule 3).")
        shutil.copyfile(bsrc, os.path.join(td, "T"))
        return os.path.join(td, GRADED_T), os.path.join(cd, "_tmp")

    def _plant(dst, work, which):
        """Plant PLANT_T into the cells in `which`, and -- on the repaired form
        -- into their matching outlet face entries, keeping the file in the
        CONSISTENT state OpenFOAM writes."""
        os.makedirs(work, exist_ok=True)
        src = t_src
        lidx = []
        for w in which:
            nxt = os.path.join(work, f"c{w}")
            lidx.append(plant_into_scalar_copy(src, nxt, cells[w], PLANT_T))
            src = nxt
        if repaired:
            for w in which:
                nxt = os.path.join(work, f"f{w}")
                plant_into_patch_list_copy(src, nxt, "outlet", w, PLANT_T,
                                           "scalar")
                src = nxt
        shutil.copyfile(src, dst)
        return lidx

    # ---- P4a: THE REGISTERED FORM -- ONE interior outlet-adjacent cell ------
    p4a, work_a = _stage("P4a")
    lines_a = _plant(p4a, work_a, [0])
    b_a = read_boundary_values(p4a, "scalar")      # section 4.5 runs HERE
    if b_a.get("outlet") is not None:
        refuse(f"P4a FAILED: after the plant, {p4a}'s outlet patch did not "
               f"resolve to the adjacent-cell sentinel (got "
               f"{b_a.get('outlet')!r}).  The repaired boundary path is not the "
               f"path the graded number comes out of, so P4 proves nothing "
               f"(standing rule 3).")
    vals_a = read_scalar_field(p4a, nx * ny)
    if vals_a[cell0] != PLANT_T:
        refuse(f"P4a FAILED: planted {PLANT_T!r} K into outlet-adjacent cell "
               f"{cell0} (line {lines_a[0]}) of a COPY of {t_src} and the "
               f"PRODUCTION SCALAR READER read back {vals_a[cell0]!r}.")
    if repaired:
        faces_a = _read_patch_list(p4a, "outlet", "scalar")
        if faces_a[0] != PLANT_T:
            refuse(f"P4a FAILED ON THE PATCH ITSELF: the outlet face list of "
                   f"{p4a} reads {faces_a[0]!r} at face 0 where {PLANT_T!r} was "
                   f"planted.  The reader cannot see a non-zero ON THE PATCH, "
                   f"and the repaired path's whole job is to emit a value read "
                   f"off a patch (standing rule 3).")
    v_a = _vertex_value(idx, vals_a, idx["nx"], jv, b_a)
    if v_a == v_base:
        refuse(f"P4a FAILED: a {PLANT_T!r} K plant into outlet-adjacent cell "
               f"{cell0} of a COPY of {t_src} left the PRODUCTION BOUNDARY PATH "
               f"reading {v_a!r} at the outlet vertex j={jv} -- unchanged from "
               f"the unplanted {v_base!r}.  A reader not shown able to see a "
               f"non-zero is not evidence (standing rule 3), and this is the "
               f"one channel section 4.5 repaired.")

    # ---- P4b: THE EXACT ARM -- both faces at the probe vertex ---------------
    p4b, work_b = _stage("P4b")
    lines_b = _plant(p4b, work_b, [0, 1])
    b_b = read_boundary_values(p4b, "scalar")
    vals_b = read_scalar_field(p4b, nx * ny)
    v_b = _vertex_value(idx, vals_b, idx["nx"], jv, b_b)
    if v_b != PLANT_T:
        refuse(f"P4b FAILED: with BOTH outlet faces at vertex j={jv} resolving "
               f"to a planted {PLANT_T!r} K (cells {cell0} and {cell1}, lines "
               f"{lines_b}), the production boundary path returned {v_b!r}.  An "
               f"inverse-distance blend of two IDENTICAL face values is that "
               f"value whatever the weights are, so this is not a weighting "
               f"question: the planted number did not come out of the boundary "
               f"path (standing rule 3).")

    rec = dict(value=PLANT_T, cells=[cell0, cell1], vertex=jv, form=form,
               lines=[lines_a, lines_b], v_base=v_base, v_a=v_a, v_b=v_b,
               reader="read_boundary_values+_vertex_value", ok=True)
    if verbose:
        print(f"  P4  PLANT_T {PLANT_T:.6e} K -> outlet-adjacent cell {cell0} "
              f"of a COPY of {GRADED_T} [{form}]; the PRODUCTION BOUNDARY PATH "
              f"SAW IT ({v_base!r} -> {v_a!r}), and with both faces planted it "
              f"returned the planted value EXACTLY ({v_b!r}).")
    return rec


def zero_is_supported(deviation, plant_record):
    """Superseded section 8.1's STANDING CONSEQUENCE.

    A graded row returning EXACTLY zero is NOT A RESULT unless P1/P2
    demonstrated, on the same reader in the same invocation, that a non-zero is
    visible.  A zero is a result only when it is a supported zero."""
    if deviation != 0.0:
        return True
    return bool(plant_record.get("nonzero_visible"))


# --------------------------------------------------------------------------
# THE MESH, AND THE ORDERING ASSERTION.  Nothing here is assumed; if the mesh
# and the field disagree about how many cells exist, this REFUSES.
# --------------------------------------------------------------------------
BLOCK_Y = {"A": (0.000, 0.024), "B": (0.024, 1.022), "C": (1.022, 1.040)}
BLOCK_ORDER = ("A", "B", "C")


def _strip_foam(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    return re.sub(r"//[^\n]*", " ", txt)


def read_points(polymesh):
    p = os.path.join(polymesh, "points")
    if not os.path.isfile(p):
        refuse(f"{polymesh}: no points file, so no mesh can be read")
    txt = _strip_foam(open(p).read())
    body = txt[txt.index("(") + 1: txt.rindex(")")]
    pts = []
    for m in re.finditer(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)", body):
        pts.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
    if not pts:
        refuse(f"{p}: no points could be parsed")
    return pts


def unique_axis(pts, axis, tol=1e-10):
    vals = sorted(set(round(p[axis] / tol) * tol for p in pts))
    out = [vals[0]]
    for v in vals[1:]:
        if v - out[-1] > tol * 10:
            out.append(v)
    return out


def read_mesh(case_dir):
    pm = os.path.join(case_dir, "constant", "polyMesh")
    pts = read_points(pm)
    zl = unique_axis(pts, 2)
    # THE z EXTENT IS READ, NOT ASSUMED.  `cellPoint` interpolates in THREE
    # dimensions: the distance from a mesh vertex at z = 0 to a cell centre at
    # z = t/2 carries a t/2 term that is the same order as the in-plane
    # spacing, so a 2D distance gives the wrong inverse-distance weights.
    # AMENDMENT 2 section A2.1d registers ONE cell in z; assertion A1 is
    # enforced here on the mesh actually read.
    if len(zl) != 2:
        refuse(f"{pm}: {len(zl)} z-planes, and the registration (AMENDMENT 2 "
               f"section A2.1d, assertion A1) fixes EXACTLY ONE CELL IN z. "
               f"Refusing rather than interpolating on a mesh the registration "
               f"does not describe.")
    return dict(x_lines=unique_axis(pts, 0), y_lines=unique_axis(pts, 1),
                z_lines=zl, thickness=zl[1] - zl[0], path=pm)


def build_index(mesh, n_field):
    """(i, j) -> global cell index, with the ORDERING ASSERTED.

    blockMesh writes cells block by block in the declared order A, B, C, and
    within a block i (x) fastest.  That is the ordering this map encodes.  IT
    IS NOT TAKEN ON TRUST: if Nx*Ny does not equal the number of values in the
    field this map is about to index, this REFUSES rather than producing a
    silently mis-registered profile."""
    x_lines, y_lines = mesh["x_lines"], mesh["y_lines"]
    nx = len(x_lines) - 1
    ny = len(y_lines) - 1
    if nx <= 0 or ny <= 0:
        refuse(f"{mesh['path']}: degenerate mesh, Nx={nx} Ny={ny}")
    if n_field is not None and nx * ny != n_field:
        refuse(f"ORDERING ASSERTION FAILED: the mesh at {mesh['path']} implies "
               f"Nx*Ny = {nx}*{ny} = {nx * ny} cells and the field carries "
               f"{n_field}.  Refusing rather than indexing a field with a map "
               f"that does not fit it.")
    # per-block y counts, from the mesh, in the declared block order
    jbase, order = {}, []
    for blk in BLOCK_ORDER:
        lo, hi = BLOCK_Y[blk]
        js = [j for j in range(ny)
              if y_lines[j] >= lo - 1e-9 and y_lines[j + 1] <= hi + 1e-9]
        jbase[blk] = js
        order.extend(js)
    if sorted(order) != list(range(ny)):
        refuse(f"{mesh['path']}: the three registered BLOCK_Y bands do not "
               f"partition the {ny} y-rows exactly (got {len(order)} rows). "
               f"Refusing rather than guessing the block layout.")
    cell_of = {}
    running = 0
    for blk in BLOCK_ORDER:
        for j in jbase[blk]:
            for i in range(nx):
                cell_of[(i, j)] = running + i
            running += nx
    return dict(nx=nx, ny=ny, cell_of=cell_of,
                x_lines=x_lines, y_lines=y_lines,
                z_lines=mesh["z_lines"], thickness=mesh["thickness"])


def _locate(lines, v):
    """Index of the cell whose band contains v; clamped at the ends."""
    if v <= lines[0]:
        return 0
    if v >= lines[-1]:
        return len(lines) - 2
    lo, hi = 0, len(lines) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if lines[mid] <= v:
            lo = mid
        else:
            hi = mid
    return lo


def sample_cell(idx, values, x, y, bvals=None):
    """SCHEME `cell` (AMENDMENT 1 A1.3a, the CONTROL): piecewise-constant
    lookup in the containing cell.

    `bvals` is accepted and DELIBERATELY UNUSED: OpenFOAM's `cell` scheme is a
    cell lookup and takes no boundary value, so the control must NOT acquire
    one.  It is in the signature only so the two schemes dispatch alike."""
    i = _locate(idx["x_lines"], x)
    j = _locate(idx["y_lines"], y)
    return values[idx["cell_of"][(i, j)]]


def _boundary_entries(lines):
    """Split a field file's `boundaryField { ... }` into {patch: body}.

    Brace-counted, not regex-matched over the whole block: a regex that tries
    to find the matching brace of a nested dictionary is the classic way to
    stop one entry early and silently drop the rest.
    """
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("boundaryField"):
            start = i
            break
    if start is None:
        return None
    j = start
    while j < len(lines) and "{" not in lines[j]:
        j += 1
    if j >= len(lines):
        return None
    depth, k, out, name = 0, j, {}, None
    buf = []
    while k < len(lines):
        ln = lines[k]
        opens, closes = ln.count("{"), ln.count("}")
        if depth == 1 and name is None and ln.strip() and opens == 0 and closes == 0:
            name = ln.strip()
        if depth >= 2:
            buf.append(ln)
        depth += opens - closes
        if depth == 1 and buf:
            out[name] = "\n".join(buf)
            buf, name = [], None
        if depth <= 0 and k > j:
            break
        k += 1
    return out


def _patch_names_match(found):
    """The registered patch set, asserted rather than assumed.

    A field file naming a patch this reader does not know about means the
    geometry moved under the reader, and the reader's vertex-to-patch map is
    then wrong in a way no value comparison would reveal.  It REFUSES.
    """
    known = set(REGISTERED_PATCHES)
    for name in found:
        raw = name.strip().strip('"')
        if raw.startswith("(") or "|" in raw:
            for part in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw):
                if part not in known:
                    return False, part
        elif raw not in known:
            return False, raw
    return True, None


# --------------------------------------------------------------------------
# K0h SEC 4.5 -- THE ONE REGISTERED FUNCTIONAL CHANGE IN THE K0h GRADING PATH.
#
# MEASURED FACT (K0h_PREREGISTRATION.md section 4.1, RE-MEASURED against disk
# by the lane that wrote this file, on
# K0g_runs/{M1_c,M2_c}/60/{TMean,UMean}): `fieldAverage` writes EVERY patch of
# its output field as `type calculated` WITH AN EXPLICIT `value`.  A patch whose
# base-field condition is a CONSTANT (`fixedValue uniform`, `noSlip`) averages
# to that constant and is written `uniform`.  A patch whose base-field condition
# is EVALUATED PER FACE -- here `outlet`'s `zeroGradient`, the ONLY such patch
# in this case -- averages to a per-face list and is written `nonuniform`.
#
# THE FROZEN K0g READER REFUSES ON THAT LIST AND IT IS RIGHT TO (section 4.2):
# guessing a face ORDER is exactly the assumption the K0d boundary repair exists
# to remove.  THIS FILE DOES NOT RELAX THAT REFUSAL.  It adds ONE narrow,
# CHECKED capability and refuses in every other case, as section 4.5 registers:
#
#   A patch of `type calculated` carrying a `nonuniform` value list is resolved
#   ONLY when
#     (a) the corresponding patch of the BASE FIELD at the SAME time directory
#         is `zeroGradient`, AND
#     (b) the written list is EQUAL, ELEMENT-WISE AND EXACTLY, to the
#         adjacent-cell values of the averaged field's own internal field, in
#         mesh patch face order.
#   If (a) fails, or if (b) fails BY ANY AMOUNT, this REFUSES (exit 2) exactly
#   as the frozen reader does today.  It is a CAPABILITY ADDITION GUARDED BY A
#   CHECK, not a weakening: a nonuniform patch this reader cannot place still
#   refuses.
#
# (b) IS A RUN-TIME CHECK EXECUTED ON EVERY READ, NEVER A PRE-COMPUTE BELIEF
# (CLAUDE.md rule 14: a lesson is not applied until EVERY CALL SITE checks it).
# IT IS WRITTEN AS `if ... refuse()` AND NEVER AS A PYTHON `assert`: an `assert`
# is REMOVED by `python3 -O`, and check_k0h_instrument_standard.py exists
# because that has already cost this lab a guard.  IT IS NOT DOWNGRADEABLE TO A
# WARNING AND NO INVOCATION FLAG RELAXES IT.
#
# WHEN IT SUCCEEDS THE PATCH RESOLVES TO `None` -- the SAME zeroGradient
# sentinel the frozen reader already returns for `T` and `U`, resolved by the
# caller from the ADJACENT CELL.  So the repair moves NO graded number by any
# amount: the value substituted is bit-identical to the value OpenFOAM wrote
# (section 4.4; re-measured here: max|diff| = 0.0 on both completed arms, both
# fields, all 12 faces, first cell 159 at stride 160 over a 14.72 K profile).
#
# NOTHING BELOW IS GENERALISED BEYOND THE TWO REGISTERED CONDITIONS.  In
# particular the reader does NOT special-case the patch NAME `outlet`: it
# applies (a) and (b) to whatever patch presents a nonuniform list, and a patch
# that fails either is refused.
# --------------------------------------------------------------------------
def _patch_face_cells(idx, patch):
    """K0h SEC 4.5: the cell adjacent to each face of `patch`, IN MESH FACE
    ORDER, as a list of (row_or_column_index, global_cell_index).

    The order encoded is the REGISTERED blockMesh order -- ascending i on the
    y-normal patches, ascending j on the x-normal ones, blocks A, B, C.  IT IS
    NOT TAKEN ON TRUST: condition (b) compares the written face values against
    these cells ONE BY ONE and refuses on any mismatch, so a wrong order cannot
    pass silently -- it produces a refusal, not a mis-registered profile.

    Returns None for a patch this map does not cover (`frontAndBack` is
    `empty`, a CONSTRAINT patch, and carries no face value here)."""
    nx, ny = idx["nx"], idx["ny"]
    yl, co = idx["y_lines"], idx["cell_of"]
    if patch in ("floor", "ceiling"):
        cj = 0 if patch == "floor" else ny - 1
        return [(ci, co[(ci, cj)]) for ci in range(nx)]
    if patch in ("inlet", "leftWall", "outlet", "rightWall"):
        side = "left" if patch in ("inlet", "leftWall") else "right"
        ci = 0 if side == "left" else nx - 1
        return [(cj, co[(ci, cj)]) for cj in range(ny)
                if _row_patch(side, yl[cj], yl[cj + 1]) == patch]
    return None


def _boundary_spans(lines):
    """K0h SEC 4.5: {patch: (first_body_line, last_body_line)}.

    The SAME brace walk as _boundary_entries -- deliberately, so the two agree
    by construction rather than by two regexes that might drift apart.  Line
    indices are what makes a plant into a PATCH LIST possible BY LINE INDEX
    (P4), which is the only way to plant into one that is not a regex over a
    value."""
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("boundaryField"):
            start = i
            break
    if start is None:
        return None
    j = start
    while j < len(lines) and "{" not in lines[j]:
        j += 1
    if j >= len(lines):
        return None
    depth, k, out, name, first = 0, j, {}, None, None
    while k < len(lines):
        ln = lines[k]
        opens, closes = ln.count("{"), ln.count("}")
        if depth == 1 and name is None and ln.strip() and opens == 0 and closes == 0:
            name = ln.strip()
        if depth >= 2 and first is None:
            first = k
        depth += opens - closes
        if depth == 1 and first is not None:
            out[name] = (first, k)
            first, name = None, None
        if depth <= 0 and k > j:
            break
        k += 1
    return out


def _expand_patch_name(raw):
    """K0h SEC 4.5: a boundaryField key to the patch names it covers.  The same
    grouped-name rule _patch_names_match and read_boundary_values already use."""
    raw = raw.strip().strip('"')
    if raw.startswith("(") or "|" in raw:
        return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw)
    return [raw]


def _locate_list_after(lines, i):
    """K0h SEC 4.5: given the index of a line DECLARING a `nonuniform List<..>`,
    return (count, first_value_line) -- the same shape locate_internal_field
    returns for an internalField, applied to a PATCH value list.  Returns None
    rather than guessing when the file is not in the one-value-per-line ascii
    form the registration fixes (AMENDMENT 2 A2.1a)."""
    m = re.search(r"nonuniform\s+List<\w+>\s*([0-9]*)", lines[i])
    count = int(m.group(1)) if (m and m.group(1)) else None
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if count is None:
        if j < len(lines) and re.fullmatch(r"[0-9]+", lines[j].strip()):
            count = int(lines[j].strip())
        else:
            return None
    k = j
    while k < len(lines) and lines[k].strip() != "(":
        k += 1
    if k >= len(lines):
        return None
    return count, k + 1


def _patch_list_location(path, patch):
    """K0h SEC 4.5: (count, first_value_line, lines) for `patch`'s nonuniform
    value list, or None if it carries none.  REFUSES on a list it cannot place
    rather than reading past it."""
    lines = _read_lines(path)
    spans = _boundary_spans(lines)
    if spans is None:
        refuse(f"{path}: no boundaryField could be located, so a patch value "
               f"list cannot be placed.")
    span = None
    for nm, sp in spans.items():
        if nm is not None and patch in _expand_patch_name(nm):
            span = sp
    if span is None:
        return None
    decl = None
    for k in range(span[0], span[1] + 1):
        if "nonuniform" in lines[k]:
            decl = k
            break
    if decl is None:
        return None
    loc = _locate_list_after(lines, decl)
    if loc is None:
        refuse(f"{path}: patch {patch!r} declares a `nonuniform` value list this "
               f"reader cannot place (the registration fixes ascii, one value "
               f"per line -- AMENDMENT 2 section A2.1a).  Refusing rather than "
               f"reading past a list whose extent is unknown.")
    return loc[0], loc[1], lines


def _read_patch_list(path, patch, kind):
    """K0h SEC 4.5: `patch`'s written nonuniform face values, from disk,
    through the SAME token parsers the production internal-field readers use."""
    loc = _patch_list_location(path, patch)
    if loc is None:
        return None
    count, first, lines = loc
    out = []
    for t in range(count):
        if first + t >= len(lines):
            refuse(f"{path}: patch {patch!r} declares {count} face values and "
                   f"the file ends after {t}.  Refusing rather than grading a "
                   f"truncated patch.")
        tok = lines[first + t].strip()
        out.append(_parse_vector(tok) if kind == "vector" else _parse_scalar(tok))
    return out


def _resolve_fieldaverage_nonuniform(path, kind, targets, typ, body):
    """K0h SEC 4.5: resolve a `fieldAverage` output patch written `nonuniform`,
    under conditions (a) and (b) above, or REFUSE (exit 2).

    RETURNS `None` on success -- the zeroGradient sentinel the caller already
    resolves from the adjacent cell.  It returns nothing else, ever: this
    function either establishes that the written list IS the adjacent-cell
    reading, or it refuses."""
    if len(targets) != 1:
        refuse(f"{path}: a GROUPED boundaryField key {targets!r} carries a "
               f"NONUNIFORM value.  Section 4.5 registers the resolution for a "
               f"single named patch and this reader refuses rather than "
               f"extending a registered rule on its own authority.")
    patch = targets[0]
    if typ != "calculated":
        refuse(f"{path}: patch {patch!r} is type {typ!r} with a NONUNIFORM "
               f"value.  Section 4.5 registers the resolution for `calculated` "
               f"-- what `fieldAverage` writes -- and NOTHING ELSE.  Refusing "
               f"rather than guessing the patch face ORDER.")
    tdir = os.path.dirname(os.path.abspath(path))
    fld = os.path.basename(path)
    if not fld.endswith("Mean"):
        refuse(f"{path}: patch {patch!r} carries a NONUNIFORM value on a field "
               f"that is not a `fieldAverage` output ({fld!r} does not end in "
               f"`Mean`).  Section 4.5's resolution is registered for a "
               f"fieldAverage output ONLY.  Refusing rather than guessing the "
               f"patch face ORDER.")
    base_name = fld[:-len("Mean")]
    bpath = field_path(tdir, base_name)
    if bpath is None:
        refuse(f"{path}: patch {patch!r} carries a NONUNIFORM value and the "
               f"BASE FIELD {base_name!r} is ABSENT from {tdir}, so section "
               f"4.5 condition (a) CANNOT BE CHECKED.  A check that cannot be "
               f"performed is not a check that passed -- refusing.")
    bents = _boundary_entries(_read_lines(bpath))
    if bents is None:
        refuse(f"{bpath}: no boundaryField, so section 4.5 condition (a) cannot "
               f"be checked for patch {patch!r}.  Refusing.")
    btyp = None
    for nm, bd in bents.items():
        if nm is not None and patch in _expand_patch_name(nm):
            mm = re.search(r"\btype\s+(\w+)\s*;", bd)
            btyp = mm.group(1) if mm else None
    if btyp != "zeroGradient":
        refuse(f"SECTION 4.5 CONDITION (a) FAILED: {path} patch {patch!r} is a "
               f"`calculated` NONUNIFORM list, and the corresponding patch of "
               f"the base field {bpath} is {btyp!r}, not `zeroGradient`.  The "
               f"registered resolution applies ONLY where the base condition is "
               f"evaluated per face.  Refusing rather than guessing the patch "
               f"face ORDER.")
    # ---- condition (b): THE RUN-TIME CHECK, ON EVERY READ -----------------
    case_dir = os.path.dirname(tdir)
    mesh = read_mesh(case_dir)
    nx = len(mesh["x_lines"]) - 1
    ny = len(mesh["y_lines"]) - 1
    reader = read_vector_field if kind == "vector" else read_scalar_field
    values = reader(path, nx * ny)
    idx = build_index(mesh, len(values))
    pairs = _patch_face_cells(idx, patch)
    if not pairs:
        refuse(f"SECTION 4.5 CONDITION (b) CANNOT BE CHECKED: {path} patch "
               f"{patch!r} has no adjacent-cell map in the registered geometry. "
               f"Refusing rather than guessing the patch face ORDER.")
    faces = _read_patch_list(path, patch, kind)
    if faces is None:
        refuse(f"{path}: patch {patch!r} was reported NONUNIFORM and no value "
               f"list could be read back from it.  Refusing.")
    if len(faces) != len(pairs):
        refuse(f"SECTION 4.5 CONDITION (b) FAILED: {path} patch {patch!r} "
               f"carries {len(faces)} face values and the registered geometry "
               f"gives {len(pairs)} faces on that patch.  Refusing rather than "
               f"pairing a list with a map that does not fit it.")
    mism = []
    for t, (row, cell) in enumerate(pairs):
        got, want = faces[t], values[cell]
        if kind == "vector":
            equal = (tuple(got) == tuple(want))
        else:
            equal = (got == want)
        if not equal:
            mism.append((t, row, cell, got, want))
    if mism:
        t, row, cell, got, want = mism[0]
        refuse(f"SECTION 4.5 CONDITION (b) FAILED ON {len(mism)} OF "
               f"{len(pairs)} FACES: {path} patch {patch!r} face {t} (mesh row "
               f"{row}) is written {got!r} and the adjacent cell {cell} of this "
               f"field's OWN internal field holds {want!r}.  The registered "
               f"resolution requires ELEMENT-WISE EXACT equality (section "
               f"4.5(b)); it is a run-time check on every read and it is NOT "
               f"downgradeable to a warning.  Refusing -- the affected rows are "
               f"NOT A RESULT (prediction P-K0h-5's named failure mode).")
    return None


def read_boundary_values(path, kind):
    """PRODUCTION BOUNDARY READER.  {patch_name: float or (x,y,z)}.

    THIS IS THE HALF OF THE READER THAT WAS MISSING, AND ITS ABSENCE IS THE
    DEFECT THAT MADE EVERY K0d GRADED ROW `NOT A RESULT`.  OpenFOAM's
    `cellPoint` (volPointInterpolation) OVERRIDES the point value on every
    non-constraint patch with a value interpolated from that patch's own FACE
    values; the K0d reader averaged interior cells only and so could not see a
    boundary condition at all.  Measured on `M1_c` at the floor: OpenFOAM
    308.150000 K -- exactly the registered fixedValue -- against 306.940157 K.

    Resolution, per patch type, and nothing is inferred:
      fixedValue / calculated / fixedFluxPressure  ->  the `value` entry
      noSlip                                       ->  zero, by definition
      zeroGradient                                 ->  the ADJACENT CELL value,
                                                       signalled as None here
                                                       and resolved by the
                                                       caller, which is the only
                                                       place the cell is known
      anything else                                ->  REFUSE

    K0h SEC 4.5.  A NONUNIFORM patch value REFUSES -- WITH THE ONE REGISTERED
    EXCEPTION OF SECTION 4.5.  The frozen K0g invariant read "neither `T` nor
    `U` -- the only fields the registered extraction of A1.3a samples -- can
    carry one".  THAT IS TRUE OF `T` AND `U` AND FALSE OF `TMean` AND `UMean`:
    K0g aimed a reader inherited from K0f, where the graded field WAS the
    instantaneous `T`/`U`, at a NEW CLASS OF FIELD -- `fieldAverage` output --
    whose patch representation the invariant was never written against, and it
    REFUSED on both completed arms (K0h_PREREGISTRATION.md section 4.2).

    Section 4.5 resolves a NONUNIFORM `calculated` patch -- and only that --
    when BOTH registered conditions hold, checked AT RUN TIME ON EVERY READ,
    and refuses otherwise.  See _resolve_fieldaverage_nonuniform() above.
    Guessing a face ORDER for a nonuniform list is STILL exactly the kind of
    assumption this repair exists to remove; nothing here guesses one, and a
    patch failing either condition is still refused instead of read.
    """
    ents = _boundary_entries(_read_lines(path))
    if ents is None:
        refuse(f"{path}: no boundaryField could be located.  The wall reader "
               f"cannot be run without one, and falling back to an "
               f"interior-only average is the DEFECT this reader repairs.")
    ok, bad = _patch_names_match(ents)
    if not ok:
        refuse(f"{path}: boundaryField names patch {bad!r}, which is not in the "
               f"registered patch set {sorted(REGISTERED_PATCHES)}.  The "
               f"vertex-to-patch map is registered geometry; refusing rather "
               f"than mapping a vertex onto a patch this reader cannot place.")
    out = {}
    for name, body in ents.items():
        m = re.search(r"\btype\s+(\w+)\s*;", body)
        if not m:
            refuse(f"{path}: patch {name!r} states no type")
        typ = m.group(1)
        raw = name.strip().strip('"')
        targets = ([p for p in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw)]
                   if (raw.startswith("(") or "|" in raw) else [raw])
        if typ == "empty":
            val = "EMPTY"
        elif typ == "noSlip":
            val = (0.0, 0.0, 0.0) if kind == "vector" else 0.0
        elif typ == "zeroGradient":
            val = None                      # resolved from the adjacent cell
        else:
            vm = re.search(r"\bvalue\s+uniform\s+(.+?);", body, re.S)
            if not vm:
                if re.search(r"\bvalue\s+nonuniform\b", body):
                    # K0h SEC 4.5 -- THE ONE FUNCTIONAL CHANGE IN THIS FILE.
                    # The frozen K0g reader refused here unconditionally.  It
                    # now refuses here unconditionally TOO, unless BOTH
                    # registered conditions hold; the callee returns `None` --
                    # the zeroGradient sentinel -- or exits 2.  It never
                    # returns a face value it guessed an order for.
                    val = _resolve_fieldaverage_nonuniform(path, kind, targets,
                                                           typ, body)
                else:
                    refuse(f"{path}: patch {name!r} is type {typ!r} with no "
                           f"`value` entry, so its face value cannot be read. "
                           f"Refusing rather than substituting an interior cell "
                           f"for a boundary condition -- that substitution IS "
                           f"the K0d defect.")
            else:
                tok = vm.group(1).strip()
                val = (_parse_vector(tok) if kind == "vector"
                       else _parse_scalar(tok))
        for t in targets:
            out[t] = val
    missing = [p for p in REGISTERED_PATCHES if p not in out]
    if missing:
        refuse(f"{path}: boundaryField does not cover registered patches "
               f"{missing}.  Refusing rather than leaving a wall unread.")
    return out


# --- the vertex-to-patch map, from REGISTERED geometry --------------------
# section 1: inlet  x = 0,    y in [1.022, 1.040]
#            outlet x = 1.04, y in [0, 0.024]
# The rest of x = 0 is leftWall and the rest of x = 1.04 is rightWall;
# y = 0 is floor and y = 1.04 is ceiling, both across the whole span.
# `frontAndBack` is `empty` -- a CONSTRAINT patch, which volPointInterpolation
# does NOT override -- and it never enters this 2D (i, j) map.
REGISTERED_PATCHES = ("inlet", "outlet", "floor", "ceiling",
                      "leftWall", "rightWall", "frontAndBack")
INLET_Y = (1.022, 1.040)
OUTLET_Y = (0.000, 0.024)


def _row_patch(side, y_lo, y_hi):
    """Patch owning the x-normal face spanning [y_lo, y_hi] on `side`."""
    if side == "left":
        return "inlet" if (y_lo >= INLET_Y[0] - 1e-9 and
                           y_hi <= INLET_Y[1] + 1e-9) else "leftWall"
    return "outlet" if (y_lo >= OUTLET_Y[0] - 1e-9 and
                        y_hi <= OUTLET_Y[1] + 1e-9) else "rightWall"


def boundary_faces_at_vertex(idx, i, j):
    """Boundary faces sharing vertex (i, j), as (patch, cell_ij, half_extent).

    `half_extent` is the distance from the vertex to that face's centre, which
    is what volPointInterpolation's inverse-distance weighting uses.  On a
    structured hex mesh a boundary face's centre sits at the midpoint of the
    cell edge lying in the boundary, so the distance is half that edge.
    """
    nx, ny = idx["nx"], idx["ny"]
    xl, yl = idx["x_lines"], idx["y_lines"]
    faces = []
    if j == 0 or j == ny:
        patch = "floor" if j == 0 else "ceiling"
        cj = 0 if j == 0 else ny - 1
        for ci in (i - 1, i):
            if 0 <= ci < nx:
                faces.append((patch, (ci, cj), 0.5 * (xl[ci + 1] - xl[ci])))
    if i == 0 or i == nx:
        side = "left" if i == 0 else "right"
        ci = 0 if i == 0 else nx - 1
        for cj in (j - 1, j):
            if 0 <= cj < ny:
                faces.append((_row_patch(side, yl[cj], yl[cj + 1]),
                              (ci, cj), 0.5 * (yl[cj + 1] - yl[cj])))
    return faces


def _vertex_value(idx, values, i, j, bvals=None):
    """Value at vertex (i, j), as OpenFOAM's `cellPoint` computes it.

    INTERIOR vertex: the average of the cells sharing it.
    BOUNDARY vertex: OpenFOAM's volPointInterpolation OVERRIDES the point value
    on every non-constraint patch with an inverse-distance interpolation of
    that patch's FACE values.  It does NOT blend in the interior average, which
    is why a `fixedValue` floor reads back as EXACTLY the registered BC.

    THE K0d READER TOOK THE INTERIOR BRANCH EVERYWHERE.  That is the whole
    defect: at the floor it returned 306.940157 K where OpenFOAM returns
    308.150000 K, against a 2.00e-05 K registered criterion.

    `bvals=None` selects the OLD interior-only behaviour and is retained for
    ONE purpose: the selftest drives both branches and shows the repaired one
    agrees with the boundary condition where the old one does not.  The graded
    path never passes None -- `sample_line` REFUSES without boundary values.
    """
    if bvals is not None:
        faces = boundary_faces_at_vertex(idx, i, j)
        if faces:
            acc = wsum = 0.0
            for patch, (ci, cj), d in faces:
                v = bvals.get(patch)
                if v == "EMPTY":
                    continue
                if v is None:                       # zeroGradient
                    v = values[idx["cell_of"][(ci, cj)]]
                w = 1.0 / d if d > 0 else 0.0
                acc += w * v
                wsum += w
            if wsum > 0:
                return acc / wsum
    acc, n = 0.0, 0
    for di in (-1, 0):
        for dj in (-1, 0):
            ci, cj = i + di, j + dj
            if 0 <= ci < idx["nx"] and 0 <= cj < idx["ny"]:
                acc += values[idx["cell_of"][(ci, cj)]]
                n += 1
    return acc / n if n else 0.0


# --------------------------------------------------------------------------
# `cellPoint`, AS OPENFOAM ACTUALLY COMPUTES IT.
#
# THE K0d READER WAS NOT A `cellPoint` INTERPOLANT.  It was a bilinear blend of
# four EQUALLY-weighted vertex averages, with no boundary value and no cell
# value.  OpenFOAM's `interpolationCellPoint` is a different object in THREE
# independent respects, and all three had to be repaired to reach the
# registered 2.00e-05 K criterion.  Measured on the preserved `M1_c` at
# endTime 40000, worst |diff| on the vertical mid-plane against OpenFOAM's own
# `postProcess -func sample`:
#
#     K0d, as frozen                                    1.141331     K
#     + boundary face values at wall vertices (1)       1.854106e-03 K
#     + inverse-distance point weights in 3D    (2)  }
#     + tet decomposition with the CELL value    (3)  }  3.988237e-08 K
#
# REPAIR (1) ALONE LEAVES THE READER 93x OUTSIDE ITS OWN CRITERION.  That is
# recorded because the repair was ordered as one change and is three.
#
# The three mechanisms, each traced to the installed source at
# /usr/lib/openfoam/openfoam2606/src/finiteVolume/lnInclude/ :
#
#  (1) volPointInterpolation OVERRIDES the point value on every non-constraint
#      patch with its patch FACE values -- `_vertex_value` above.
#  (2) volPointInterpolation weights cell values into a point by INVERSE
#      DISTANCE from the cell CENTRES, in three dimensions.  The mesh is one
#      cell thick, so every vertex sits a half-thickness in z away from every
#      cell centre it draws on; at the registered t = 0.010 m that offset is
#      the same order as the in-plane spacing and equal weighting is wrong by
#      up to 1.4e-03 K in the graded near-wall rows.
#  (3) interpolationCellPointI.H:
#          t  = psi_[cell]*w[0]
#            += psip_[faceVertices[0]]*w[1] + [1]*w[2] + [2]*w[3]
#      -- a barycentric blend over a TETRAHEDRON whose fourth vertex is the
#      CELL CENTRE, carrying the CELL value.  The tets come from
#      polyMeshTetDecomposition: every face is fanned about its base point and
#      each triangle closed to the cell centre.  A bilinear blend of vertex
#      values contains no cell value at all, which is why the horizontal
#      mid-plane -- graded in x across its whole length -- was the worse of
#      the two sets at 1.774491e-02 K.
# --------------------------------------------------------------------------
# A hex cell's six faces, as local (a, b, c) vertex triples in (x, y, z).  The
# fan is taken about each face's first listed vertex, which is what
# polyMeshTetDecomposition does about a face's base point.
HEX_FACES = (
    ((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)),   # x-
    ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),   # x+
    ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)),   # y-
    ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),   # y+
    ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)),   # z-
    ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)),   # z+
)
BARY_TOL = 1e-9


def cell_centre(idx, i, j):
    xl, yl = idx["x_lines"], idx["y_lines"]
    return (0.5 * (xl[i] + xl[i + 1]), 0.5 * (yl[j] + yl[j + 1]),
            0.5 * idx["thickness"])


def point_values(idx, values, bvals):
    """`volPointInterpolation`: cell values carried to every mesh vertex.

    Interior vertices: inverse-distance weighted from the CELL CENTRES, in
    THREE dimensions.  Boundary vertices: the patch face values, which
    OVERRIDE rather than blend -- which is why a `fixedValue` floor reads back
    as EXACTLY the registered boundary condition.
    """
    if bvals is None:
        refuse("point_values was called with no boundary values.  A cellPoint "
               "point field that cannot see a boundary condition is the K0d "
               "defect (1.141331 K at the floor against 2.00e-05 K).")
    nx, ny = idx["nx"], idx["ny"]
    xl, yl = idx["x_lines"], idx["y_lines"]
    cof = idx["cell_of"]
    psip = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            if boundary_faces_at_vertex(idx, i, j):
                psip[(i, j)] = _vertex_value(idx, values, i, j, bvals)
                continue
            acc = wsum = 0.0
            px, py = xl[i], yl[j]
            for di in (-1, 0):
                for dj in (-1, 0):
                    ci, cj = i + di, j + dj
                    if 0 <= ci < nx and 0 <= cj < ny:
                        cx, cy, cz = cell_centre(idx, ci, cj)
                        d = math.sqrt((px - cx) ** 2 + (py - cy) ** 2 + cz * cz)
                        w = 1.0 / d
                        acc += w * values[cof[(ci, cj)]]
                        wsum += w
            psip[(i, j)] = acc / wsum if wsum else 0.0
    return psip


def _bary_tet(P, A_, B, C, D):
    """Barycentric coordinates of P in the tet (A_, B, C, D), or None if the
    tet is degenerate.  A_ is the CELL CENTRE, so the returned w[0] is the
    weight OpenFOAM applies to the cell value."""
    ax, ay, az = A_
    c0 = (B[0] - ax, B[1] - ay, B[2] - az)
    c1 = (C[0] - ax, C[1] - ay, C[2] - az)
    c2 = (D[0] - ax, D[1] - ay, D[2] - az)
    r = (P[0] - ax, P[1] - ay, P[2] - az)

    def det3(u, v, w):
        return (u[0] * (v[1] * w[2] - v[2] * w[1])
                - v[0] * (u[1] * w[2] - u[2] * w[1])
                + w[0] * (u[1] * v[2] - u[2] * v[1]))

    det = det3(c0, c1, c2)
    if abs(det) < 1e-30:
        return None
    w1 = det3(r, c1, c2) / det
    w2 = det3(c0, r, c2) / det
    w3 = det3(c0, c1, r) / det
    return (1.0 - w1 - w2 - w3, w1, w2, w3)


def sample_cellpoint(idx, values, x, y, bvals=None, psip=None):
    """SCHEME `cellPoint` (AMENDMENT 1 section A1.3a, the GRADED scheme).

    OpenFOAM's `interpolationCellPoint`: locate the tet of the containing
    cell's decomposition that holds the sample point, then take the barycentric
    blend of the CELL value and the three vertex values of that tet's face
    triangle.  The sample plane is the mid-thickness cell-centre plane, z = t/2
    (section A1.3a), which is read from the mesh and not assumed.
    """
    if psip is None:
        psip = point_values(idx, values, bvals)
    xl, yl, t = idx["x_lines"], idx["y_lines"], idx["thickness"]
    i = _locate(xl, x)
    j = _locate(yl, y)
    P = (x, y, idx["z_lines"][0] + 0.5 * t)
    C = cell_centre(idx, i, j)
    cellv = values[idx["cell_of"][(i, j)]]

    def coord(a, b, c):
        return (xl[i + a], yl[j + b], idx["z_lines"][c])

    for face in HEX_FACES:
        for k in (1, 2):
            tri = (face[0], face[k], face[k + 1])
            pts = [coord(*v) for v in tri]
            w = _bary_tet(P, C, pts[0], pts[1], pts[2])
            if w is None:
                continue
            if all(v > -BARY_TOL for v in w):
                return (w[0] * cellv
                        + w[1] * psip[(i + tri[0][0], j + tri[0][1])]
                        + w[2] * psip[(i + tri[1][0], j + tri[1][1])]
                        + w[3] * psip[(i + tri[2][0], j + tri[2][1])])
    refuse(f"cellPoint: the sample point ({x:.6f}, {y:.6f}) fell in no tet of "
           f"cell ({i}, {j}).  Refusing rather than falling back to a scheme "
           f"the registration does not name -- a silent fallback is how the "
           f"K0d reader came to disagree with OpenFOAM unnoticed.")


SAMPLERS = {"cell": sample_cell, "cellPoint": sample_cellpoint}


def sample_line(idx, values, which, scheme, bvals=None):
    """The registered uniform sample set: 2081 points at 5.000e-04 m spacing.

    vertical   set: (0.52, 0) -> (0.52, 1.04)
    horizontal set: (0, 0.52) -> (1.04, 0.52)
    Returns (coords_normalised, values)."""
    if scheme not in SAMPLERS:
        refuse(f"extraction scheme {scheme!r} is not registered; AMENDMENT 1 "
               f"section A1.3a registers cellPoint (graded) and cell (control)")
    if scheme == "cellPoint" and bvals is None:
        refuse("sample_line was called on the GRADED `cellPoint` scheme with no "
               "boundary values.  A cellPoint reader that cannot see a boundary "
               "condition is the K0d defect that made every graded row NOT A "
               "RESULT (measured: 1.209843 K at the floor against a 2.00e-05 K "
               "criterion).  Refusing rather than reproducing it.")
    f = SAMPLERS[scheme]
    # The point field is built ONCE per line, not once per sample point: it is
    # a property of (mesh, field, boundary values) and 2081 rebuilds of it
    # would be the same answer 2081 times at (nx+1)(ny+1) cost each.
    psip = point_values(idx, values, bvals) if scheme == "cellPoint" else None
    out, coords = [], []
    for n in range(N_POINTS):
        s = n / (N_POINTS - 1)
        if which == "vertical":
            x, y = VERTICAL_X, s * DOMAIN
        elif which == "horizontal":
            x, y = s * DOMAIN, HORIZONTAL_Y
        else:
            refuse(f"sample set {which!r} is not registered")
        coords.append(s)
        out.append(f(idx, values, x, y, bvals, psip)
                   if scheme == "cellPoint" else f(idx, values, x, y, bvals))
    return coords, out


def at_station(coords, vals, station):
    """Value at a registered station, by nearest registered sample point."""
    n = int(round(station * (N_POINTS - 1)))
    n = min(max(n, 0), N_POINTS - 1)
    return vals[n]


# --------------------------------------------------------------------------
# ROACHE TRIPLE GATING.  Standing rule 5, and re-registration section 7.3.
# The UNEQUAL-RATIO fixed-point form (T3 section 7.1), because r21 = 1.400000
# and r32 = 1.401786 are NOT equal and this rung does not pretend they are.
# --------------------------------------------------------------------------
CONVERGING, DIVERGENT = "CONVERGING", "DIVERGENT"
STAGNANT, OSCILLATORY, EXACT = "STAGNANT", "OSCILLATORY", "EXACT"
BAD_TRIPLES = (DIVERGENT, STAGNANT, OSCILLATORY, EXACT)


def classify_triple(f_coarse, f_medium, f_fine):
    """Classify a grid triple.  f1 = fine, f2 = medium, f3 = coarse."""
    f1, f2, f3 = f_fine, f_medium, f_coarse
    eps21 = f2 - f1
    eps32 = f3 - f2
    if eps21 == 0.0 and eps32 == 0.0:
        return EXACT, eps21, eps32
    if eps21 == 0.0 or eps32 == 0.0:
        return STAGNANT, eps21, eps32
    R = eps21 / eps32
    if R < 0.0:
        return OSCILLATORY, eps21, eps32
    if R >= 1.0:
        return DIVERGENT, eps21, eps32
    return CONVERGING, eps21, eps32


def is_monotone(f_coarse, f_medium, f_fine):
    return ((f_coarse > f_medium > f_fine) or (f_coarse < f_medium < f_fine))


def observed_order(eps21, eps32, r21=R21, r32=R32, iters=200, tol=1e-12):
    """Observed order p by fixed-point iteration on the UNEQUAL ratios.

    p = |ln|eps32/eps21| + q(p)| / ln(r21),
    q(p) = ln((r21^p - s)/(r32^p - s)),  s = sign(eps32/eps21)

    Returns None where p is not defined -- and a None p is never printed as a
    number and never used to quote a GCI."""
    if eps21 == 0.0 or eps32 == 0.0:
        return None
    ratio = eps32 / eps21
    if ratio <= 0.0:
        return None                      # oscillatory: p is not defined
    s = 1.0
    p = abs(math.log(abs(ratio)) / math.log(r21))
    for _ in range(iters):
        try:
            q = math.log((r21 ** p - s) / (r32 ** p - s))
        except (ValueError, ZeroDivisionError):
            return None
        new = abs(math.log(abs(ratio)) + q) / math.log(r21)
        if not math.isfinite(new):
            return None
        if abs(new - p) < tol:
            return new
        p = new
    return p


def gci_fine(f_fine, f_medium, p, r21=R21, fs=GCI_FS):
    """GCI on the fine grid at Fs = 1.25.  NEVER call this when the three
    values are not monotone -- the caller enforces that, and the selftest
    proves the caller enforces it."""
    if p is None or f_fine == 0.0:
        return None
    denom = r21 ** p - 1.0
    if denom == 0.0:
        return None
    e_a21 = abs((f_fine - f_medium) / f_fine)
    return fs * e_a21 / denom


def roache(f_coarse, f_medium, f_fine):
    """Full triple record: class, eps, order, monotonicity, GCI.

    A GCI IS NEVER QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE (standing
    rule 5, last clause).  That is enforced HERE, not left to the caller."""
    cls, eps21, eps32 = classify_triple(f_coarse, f_medium, f_fine)
    mono = is_monotone(f_coarse, f_medium, f_fine)
    p = observed_order(eps21, eps32)
    g = gci_fine(f_fine, f_medium, p) if (mono and cls == CONVERGING) else None
    return dict(cls=cls, eps21=eps21, eps32=eps32, p=p, monotone=mono, gci=g,
                coarse=f_coarse, medium=f_medium, fine=f_fine)


def format_triple(tag, tr):
    """Print the triple.  A STRUCTURAL row has no numeric triple and this says
    so rather than printing zeros that a reader could mistake for values."""
    g = "NOT QUOTED (values not monotone)" if tr["gci"] is None \
        else f"{100.0 * tr['gci']:.4f} %"
    if tr.get("structural"):
        return (f"{tag}: {tr['cls']} (STRUCTURAL -- EXACT MATCH REQUIRED across "
                f"L1/L2/L3; no numeric triple, no order, no GCI)")
    p = "n/a" if tr["p"] is None else f"{tr['p']:.4f}"
    st = f" @station {tr['station']}" if "station" in tr else ""
    return (f"{tag}: {tr['cls']}{st}  "
            f"[{tr['coarse']:.6g}, {tr['medium']:.6g}, {tr['fine']:.6g}]  "
            f"p={p}  GCI={g}")


# --------------------------------------------------------------------------
# CONVERGENCE (re-registration 7.1).  The residual is NOT the instrument.
# --------------------------------------------------------------------------
def numeric_times(d):
    return sorted((x for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)


def field_range(vals):
    return (max(vals) - min(vals)) if vals else 0.0


def is_stationary(case_dir, n_cells):
    """STATIONARY (K0h section 7.1') means the running TIME-AVERAGE is not
    drifting: the largest change of any cell of TMean, and separately of any
    component of UMean, BETWEEN the avg1 window [20,40] s and the avg2 window
    [40,60] s is at most the registered physical tolerance -- tol_T for TMean,
    tol_U per component of UMean.  A case that is NOT STATIONARY makes its
    graded rows NOT A RESULT (K0h section 7.1').

    This REPLACES K0f's steady is_converged: a natural-convection cavity at
    Ra 2.14e9 has no steady fixed point for a SIMPLE solver to reach (K0f
    measured a persistent limit cycle over 60 000 iterations), so K0h grades the
    time-average and tests that the average has settled."""
    d1 = os.path.join(case_dir, AVG1_TIME)
    d2 = os.path.join(case_dir, AVG2_TIME)
    if not (os.path.isdir(d1) and os.path.isdir(d2)):
        return False, (f"missing the avg1 ({AVG1_TIME}) or avg2 ({AVG2_TIME}) "
                       f"time directory; the two-window stationarity criterion "
                       f"cannot be evaluated and is NOT assumed to hold")
    notes = []
    for fld, reader in ((GRADED_T, read_scalar_field),
                        (GRADED_U, read_vector_field)):
        p1 = field_path(d1, fld)
        p2 = field_path(d2, fld)
        if p1 is None or p2 is None:
            return False, f"{fld} missing at {AVG1_TIME} or {AVG2_TIME}"
        v1 = reader(p1, n_cells)
        v2 = reader(p2, n_cells)
        if len(v1) != len(v2):
            return False, f"{fld}: cell count changed between windows"
        if fld == GRADED_U:
            flat1 = [c for v in v1 for c in v]
            flat2 = [c for v in v2 for c in v]
            tol = STAT_TOL_U
        else:
            flat1, flat2, tol = v1, v2, STAT_TOL_T
        delta = max(abs(a - b) for a, b in zip(flat1, flat2))
        notes.append(f"{fld}: max|avg2-avg1|={delta:.6e} vs tol={tol:.6e}")
        if delta > tol:
            return False, "; ".join(notes)
    return True, "; ".join(notes)


# --------------------------------------------------------------------------
# THE REFERENCE SLOT (superseded 7.6).  Absent today, and section 0 says so.
# --------------------------------------------------------------------------
def load_reference(root):
    p = os.path.join(root, REFERENCE_BASENAME)
    if not os.path.isfile(p):
        return None, p
    import json
    try:
        with open(p) as fh:
            return json.load(fh), p
    except Exception as exc:
        refuse(f"{p}: present but unreadable ({exc}).  A reference file that "
               f"cannot be parsed is not a held primary, and this refuses "
               f"rather than grading against a partial read.")


def band_for_row(row, ref_row):
    """BAND(r) = +/- max( 2*u_val(r), R(r)*S(r) ), u_val = sqrt(u_exp^2+u_dig^2)

    Superseded section 7.2.  `max`, not `min`: a band tighter than the
    instrument that measured the reference grades measurement noise.  The
    addendum can only ever WIDEN a band, and only through a property of the
    reference.  Returns (band, widened, anti_widening_tripped)."""
    spec = ROWS[row]
    floor = spec["band"]
    if ref_row is None:
        return floor, False, False
    u_exp = float(ref_row.get("u_exp", 0.0) or 0.0)
    u_dig = float(ref_row.get("u_dig", 0.0) or 0.0)
    u_val = math.sqrt(u_exp * u_exp + u_dig * u_dig)
    if floor is None:                     # G6, the REF-scaled row
        q = abs(float(ref_row.get("value", 0.0)))
        floor = spec["R"] * q
    band = max(2.0 * u_val, floor)
    # THE ANTI-WIDENING GUARD (superseded 7.2 property 4)
    tripped = (2.0 * u_val) > (3.0 * floor)
    return band, band > floor, tripped


# --------------------------------------------------------------------------
# ROW EXTRACTION.  Every graded row of superseded section 7.3, from the
# PRODUCTION READERS above.  A row this script cannot form is named and
# refused -- never silently omitted (AMENDMENT 2 A2.3c item 5: a check omitted
# in silence reads as a check passed).
# --------------------------------------------------------------------------
def _component(bvals, k):
    """One component of a vector boundary map, preserving the two sentinels."""
    return {p: (v if v in (None, "EMPTY") else v[k]) for p, v in bvals.items()}


def _speed_boundary(bvals):
    """|U| on each patch.  A zeroGradient patch stays None: its speed is the
    ADJACENT CELL's speed, and only the sampler knows which cell that is --
    taking the magnitude of a resolved component here would resolve it against
    the wrong cell."""
    out = {}
    for p, v in bvals.items():
        if v in (None, "EMPTY"):
            out[p] = v
        else:
            out[p] = math.hypot(v[0], v[1])
    return out


def load_case_fields(case_dir):
    times = numeric_times(case_dir)
    if not times:
        refuse(f"{case_dir}: no time directories")
    tdir = os.path.join(case_dir, times[-1])
    mesh = read_mesh(case_dir)
    tp = field_path(tdir, GRADED_T)
    if tp is None:
        refuse(f"{tdir}: no {GRADED_T} field")
    T = read_scalar_field(tp)
    idx = build_index(mesh, len(T))
    up = field_path(tdir, GRADED_U)
    if up is None:
        refuse(f"{tdir}: no {GRADED_U} field")
    U = read_vector_field(up, idx["nx"] * idx["ny"])
    # THE BOUNDARY HALF OF THE READER (K0h section V).  Loaded here, beside the
    # internal field, so no caller can reach a graded number without it.
    bT = read_boundary_values(tp, "scalar")
    bU = read_boundary_values(up, "vector")
    return dict(tdir=tdir, idx=idx, T=T, U=U, times=times,
                bT=bT, bUx=_component(bU, 0), bUy=_component(bU, 1),
                bSpeed=_speed_boundary(bU))


def extract_rows(cf, scheme=SCHEME_GRADED):
    """The ten graded rows plus the reported ones, under one scheme."""
    idx = cf["idx"]
    ux = [v[0] for v in cf["U"]]
    uy = [v[1] for v in cf["U"]]
    speed = [math.hypot(v[0], v[1]) for v in cf["U"]]

    cv, Tv = sample_line(idx, cf["T"], "vertical", scheme, cf["bT"])
    ch, Th = sample_line(idx, cf["T"], "horizontal", scheme, cf["bT"])
    _, uxv = sample_line(idx, ux, "vertical", scheme, cf["bUx"])
    _, uyh = sample_line(idx, uy, "horizontal", scheme, cf["bUy"])
    _, spv = sample_line(idx, speed, "vertical", scheme, cf["bSpeed"])

    out = {
        "G1": dict(kind="profile", coords=cv, vals=Tv),
        "G2": dict(kind="profile", coords=ch, vals=Th),
        "G3": dict(kind="profile", coords=cv, vals=uxv),
        "G4": dict(kind="profile", coords=ch, vals=uyh),
    }
    # G5a / G5b: the CEILING wall-jet peak on the vertical mid-plane.  The
    # ceiling is y = 1.040, so the ceiling jet lives in the upper part of the
    # line; the registered G5b coordinate is (H - y)/H, measured FROM the
    # ceiling, which is what fixes the search to the upper half.
    upper = [n for n in range(N_POINTS) if cv[n] >= 0.5]
    n_pk = max(upper, key=lambda n: spv[n])
    out["G5a"] = dict(kind="scalar", value=spv[n_pk])
    out["G5b"] = dict(kind="scalar", value=(H - cv[n_pk] * DOMAIN))
    # G7: a difference of two GRADED STATIONS (0.75 and 0.25 -- registered as
    # stations by AMENDMENT 4 section A4.5, which is what makes this true).
    out["G7"] = dict(kind="scalar",
                     value=at_station(cv, Tv, 0.75) - at_station(cv, Tv, 0.25))
    # G6: floor-averaged Nusselt, Nu = (dT/dn)_floor * H / dT, from the mesh
    # and the T field.  dT is the REGISTERED band scale, 20.0 K (section 4),
    # which is a boundary condition and not a solution value.
    y0, y1 = idx["y_lines"][0], idx["y_lines"][1]
    dy = (y1 - y0) / 2.0
    grads = []
    for i in range(idx["nx"]):
        t_first = cf["T"][idx["cell_of"][(i, 0)]]
        grads.append((t_first - (T_REF + DT_BAND / 2.0)) / dy)
    out["G6"] = dict(kind="scalar",
                     value=abs(sum(grads) / len(grads)) * H / DT_BAND)
    # G8: jet penetration -- distance from the inlet wall along the ceiling to
    # where the ceiling-jet peak speed first falls to 0.5 * U_in.
    jrow = idx["ny"] - 1
    xs, sp = [], []
    for i in range(idx["nx"]):
        xs.append(0.5 * (idx["x_lines"][i] + idx["x_lines"][i + 1]))
        sp.append(speed[idx["cell_of"][(i, jrow)]])
    pen = xs[-1]
    for i, s in enumerate(sp):
        if s <= 0.5 * U_IN:
            pen = xs[i]
            break
    out["G8"] = dict(kind="scalar", value=pen)
    # S1: the structural row.  Number and sense of primary recirculation cells
    # from the sign pattern of u on the vertical mid-plane, and the presence of
    # an inlet-side upper-corner secondary cell.  EXACT MATCH REQUIRED, no band.
    signs = [1 if v > 0 else (-1 if v < 0 else 0) for v in uxv]
    changes = sum(1 for a, b in zip(signs, signs[1:]) if a != 0 and b != 0
                  and a != b)
    corner = speed[idx["cell_of"][(0, idx["ny"] - 1)]] > 0.0
    out["S1"] = dict(kind="structural",
                     value=dict(sign_changes=changes, n_cells=changes + 1,
                                corner_cell=bool(corner)))
    return out


def y_plus_max(cf):
    """Achieved y+ at the floor, from the mesh and U.  u_tau = sqrt(nu*|du/dy|),
    y_p = the first cell centre distance."""
    idx = cf["idx"]
    y0, y1 = idx["y_lines"][0], idx["y_lines"][1]
    yp = (y1 - y0) / 2.0
    worst = 0.0
    for i in range(idx["nx"]):
        u_first = cf["U"][idx["cell_of"][(i, 0)]][0]
        dudy = abs(u_first) / yp
        u_tau = math.sqrt(NU * dudy)
        worst = max(worst, u_tau * yp / NU)
    return worst


# --------------------------------------------------------------------------
# THE VERDICT LADDER.  Superseded section 7.4, evaluated IN THIS ORDER, and
# the order is part of the freeze.  Re-registration section 7.3 supplies the
# Roache clauses at steps 1 and 2.
#
# THE GATE CAN ONLY TURN A `PASS` OR `GATE FAIL` INTO `NOT A RESULT`, NEVER THE
# REVERSE.  That direction is asserted by gate_is_monotone() and proved by the
# selftest, not merely stated in this comment.
# --------------------------------------------------------------------------
SEVERITY = {PASS: 0, GATE_FAIL: 1, BLOCKED: 2, REPORTED: 3, NOT_A_RESULT: 4}


def gate_is_monotone(before, after):
    """True iff `after` is not a loosening of `before`."""
    return SEVERITY.get(after, 9) >= SEVERITY.get(before, 9)


def row_verdict(row, levels_converged, triple, guard_verdict,
                reference_held, inside_band, deviation, plant_record):
    """Returns (verdict, reason).  Vocabulary only (standing rule 1)."""
    # 1. the graded arm is NOT STATIONARY (K0h section 7.1' replaces K0f's
    #    steady is_converged; `levels_converged` carries the stationarity flag)
    bad = [lv for lv, ok in levels_converged.items() if not ok]
    if bad:
        return NOT_A_RESULT, f"NOT STATIONARY: {', '.join(sorted(bad))}"
    # 2. the grid triple not CONVERGING -- NOT FORMED at L1+L2 (K0h grades no
    #    triple; `triple` is always None here and this clause never fires)
    if triple is not None and triple["cls"] in BAD_TRIPLES:
        return NOT_A_RESULT, f"triple {triple['cls']}"
    # 3. y+ window or a guard, per the guard's OWN registered clause
    if guard_verdict is not None:
        return guard_verdict[0], guard_verdict[1]
    # the standing consequence of superseded 8.1: an EXACTLY-ZERO deviation
    if deviation is not None and not zero_is_supported(deviation, plant_record):
        return NOT_A_RESULT, ("deviation is EXACTLY ZERO and no plant "
                              "demonstrated a non-zero on this reader in this "
                              "invocation -- an unsupported zero")
    # 4. no primary reference on disk
    if not reference_held:
        return BLOCKED, ("Blay 1992 NOT OBTAINED -- superseded section 7.4 "
                         "order 4")
    # 5. primary held
    return (PASS, "inside band") if inside_band else (GATE_FAIL, "outside band")


# --------------------------------------------------------------------------
# THE FIVE GUARDS (superseded 7.5), the SEED control (AMENDMENT 1 A1.2b) and
# the DUAL-SCHEME control (AMENDMENT 1 A1.3b).  Each withdraws the run, never
# the hypothesis (Charter 2c).
# --------------------------------------------------------------------------
def guard_yplus(level, achieved):
    """A case outside its y+ window has its rows REPORTED, not graded
    (re-registration section 4)."""
    win = YPLUS_WINDOW[level]
    if achieved > win:
        return (REPORTED, f"y+ {achieved:.3f} outside the {level} window "
                          f"<= {win}")
    return None


def guard_B(rows_bhi, rows_m1m):
    """|Theta(B_hi) - Theta(M1_m)| at every registered station of G1, G2, G7.
    Over 1.00 K at any station -> G1, G2 and G7 are NOT A RESULT."""
    worst, where = 0.0, None
    for row in ("G1", "G2"):
        a, b = rows_bhi[row], rows_m1m[row]
        for s in STATIONS:
            d = abs(at_station(a["coords"], a["vals"], s) -
                    at_station(b["coords"], b["vals"], s))
            if d > worst:
                worst, where = d, f"{row}@{s}"
    d7 = abs(rows_bhi["G7"]["value"] - rows_m1m["G7"]["value"])
    if d7 > worst:
        worst, where = d7, "G7"
    if worst > GUARD_B_TOL_K:
        return worst, where, (NOT_A_RESULT,
                              f"guard B: |dTheta| {worst:.4f} K at {where} "
                              f"exceeds {GUARD_B_TOL_K} K; the floor "
                              f"temperature of section 3.3 awaits the primary")
    return worst, where, None


def guard_I(rows_ihi, rows_m1m):
    """|G5a(I_hi)-G5a(M1_m)| and |G8(I_hi)-G8(M1_m)|.  Either over its own band
    -> G5a, G5b and G8 are REPORTED, not graded, flagged `inlet turbulence
    unmeasured`."""
    d5 = abs(rows_ihi["G5a"]["value"] - rows_m1m["G5a"]["value"])
    d8 = abs(rows_ihi["G8"]["value"] - rows_m1m["G8"]["value"])
    if d5 > ROWS["G5a"]["band"] or d8 > ROWS["G8"]["band"]:
        return d5, d8, (REPORTED,
                        f"guard I: dG5a={d5:.5f} m/s (band "
                        f"{ROWS['G5a']['band']}), dG8={d8:.5f} m (band "
                        f"{ROWS['G8']['band']}) -- inlet turbulence unmeasured")
    return d5, d8, None


def guard_DC(rows_lam, rows_m1m, lam_stationary):
    """Charter 2c: C_lam against M1_m on G6.  MET if they differ by more than
    25 %.  Within 25 % -> G6 grades nothing and the record SAYS SO.

    K0h predicts C_lam does NOT reach stationarity (a laminar model at Ra 2.14e9
    is under-resolved and has no stationary state), in which case DC is
    UNMEASURED -- and that non-stationarity is itself the discrimination
    finding (turbulence closure is required)."""
    if not lam_stationary:
        return None, (REPORTED, "guard DC UNMEASURED: C_lam is not stationary")
    a, b = rows_lam["G6"]["value"], rows_m1m["G6"]["value"]
    if b == 0.0:
        return None, (REPORTED, "guard DC UNMEASURED: G6(M1_m) is zero")
    pct = 100.0 * abs(a - b) / abs(b)
    if pct <= DISCRIMINATION_PCT:
        return pct, (REPORTED,
                     f"guard DC NOT MET: laminar and kOmegaSST G6 differ by "
                     f"{pct:.2f} % <= {DISCRIMINATION_PCT} %, so G6 GRADES "
                     f"NOTHING (K0c F8: the set of rows kOmegaSST passed that a "
                     f"laminar solve did not also pass was EMPTY)")
    return pct, None


def guard_seed(rows_seed, rows_m1m):
    """AMENDMENT 1 A1.2b.  If ANY graded quantity differs between the two seeds
    by more than that quantity's own registered band, the rung's graded rows are
    REPORTED, NOT GRADED, and SEED-DEPENDENCE IS THE FINDING."""
    worst, where = 0.0, None
    for row in GRADED_ROWS:
        band = ROWS[row]["band"]
        if band is None or row == "S1":
            continue
        a, b = rows_seed[row], rows_m1m[row]
        if a["kind"] == "profile":
            for s in STATIONS:
                d = abs(at_station(a["coords"], a["vals"], s) -
                        at_station(b["coords"], b["vals"], s))
                if d > worst:
                    worst, where = d, f"{row}@{s}"
        else:
            d = abs(a["value"] - b["value"])
            if d > worst:
                worst, where = d, row
    for row in GRADED_ROWS:
        band = ROWS[row]["band"]
        if band is None or row == "S1":
            continue
        a, b = rows_seed[row], rows_m1m[row]
        if a["kind"] == "profile":
            hit = any(abs(at_station(a["coords"], a["vals"], s) -
                          at_station(b["coords"], b["vals"], s)) > band
                      for s in STATIONS)
        else:
            hit = abs(a["value"] - b["value"]) > band
        if hit:
            return worst, where, (REPORTED,
                                  f"SEED DEPENDENCE IS THE FINDING: {row} "
                                  f"differs between M1_m and M1_m_seed by more "
                                  f"than its registered band (worst {worst:.6g} "
                                  f"at {where})")
    return worst, where, None


def dual_scheme_control(rows_a, rows_b):
    """AMENDMENT 1 A1.3b.  Any graded row where `cell` and `cellPoint` differ by
    more than its own registered band is REPORTED, NOT GRADED -- such a number
    is an artefact of an extraction choice, not a property of the solution."""
    out = {}
    for row in DUAL_SCHEME_ROWS:
        band = ROWS[row]["band"]
        a, b = rows_a[row], rows_b[row]
        if a["kind"] == "profile":
            d = max(abs(at_station(a["coords"], a["vals"], s) -
                        at_station(b["coords"], b["vals"], s))
                    for s in STATIONS)
        else:
            d = abs(a["value"] - b["value"])
        out[row] = (d, None if (band is None or d <= band) else
                    (REPORTED, f"dual-scheme control: cell vs cellPoint differ "
                               f"by {d:.6g} > band {band}"))
    return out


# --------------------------------------------------------------------------
def own_blob_sha():
    """This file's git blob sha1, so the operator can check it against the
    committed blob (re-registration 7.5 / Charter 2d).  Printing it is not the
    freeze check; it is what makes the freeze check possible from the output."""
    import hashlib
    data = open(__file__, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def require_markers(root):
    """analyse_k0h.py refuses (exit 2) unless all TEN DONE.<case> markers are
    present.  NINE was the pre-AMENDMENT-1 count; A1.2b moved it to TEN."""
    missing = [c for c in CASES
               if not os.path.isfile(os.path.join(root, f"DONE.{c}"))]
    if missing:
        refuse(f"{len(CASES) - len(missing)} of {len(CASES)} DONE markers "
               f"present; MISSING: {', '.join(missing)}.  The comparator "
               f"refuses rather than grading a partial rung (re-registration "
               f"7.5, AMENDMENT 1 section A1.2b).")


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
SEVERITY_TRIPLE = {CONVERGING: 0, EXACT: 1, STAGNANT: 2, OSCILLATORY: 3,
                   DIVERGENT: 4}


def row_triple(row, rows_by_level):
    """The Roache triple of one row across L1/L2/L3 of one closure ladder.

    A PROFILE row is graded at THIRTEEN stations, so it has thirteen triples.
    THE ROW TAKES THE MOST SEVERE OF THEM -- a single DIVERGENT station makes
    the row NOT A RESULT.  That is a TIGHTENING and cannot loosen: it can only
    turn a PASS into NOT A RESULT, never the reverse (standing rule 5).  It is
    a disclosed reading, flagged for the diff read."""
    c, m, f = rows_by_level["L1"][row], rows_by_level["L2"][row], \
        rows_by_level["L3"][row]
    if c["kind"] == "structural":
        same = (c["value"] == m["value"] == f["value"])
        return dict(cls=CONVERGING if same else DIVERGENT, p=None, gci=None,
                    monotone=same, eps21=0.0, eps32=0.0,
                    coarse=0.0, medium=0.0, fine=0.0, structural=True)
    if c["kind"] == "profile":
        worst, worst_tr = None, None
        for s in STATIONS:
            tr = roache(at_station(c["coords"], c["vals"], s),
                        at_station(m["coords"], m["vals"], s),
                        at_station(f["coords"], f["vals"], s))
            sev = SEVERITY_TRIPLE[tr["cls"]]
            if worst is None or sev > worst:
                worst, worst_tr = sev, dict(tr, station=s)
        return worst_tr
    return roache(c["value"], m["value"], f["value"])


def assert_extraction_equivalence(root, verbose=True):
    """THE STANDING PRE-GRADING GATE (K0h section V, the tightening).

    REFUSES (exit 2) unless `check_k0h_extraction_equivalence.py` PASSES on the
    graded level IN THIS SAME INVOCATION.

    WHY IT IS A STANDING GATE AND NOT A ONE-OFF.  AD1.1 registered the
    equivalence check as something to be run once, after L1.  It was, and it
    said DISAGREE, and every K0d graded row became NOT A RESULT.  The lesson is
    not that the check was worth running once; it is that FOR THE WHOLE LIFE OF
    K0d THE GRADED PATH RESTED ON AN EQUIVALENCE NOBODY HAD MEASURED.

    A READER THAT HAS NEVER BEEN COMPARED AGAINST THE REFERENCE IMPLEMENTATION
    IS A PLANTED ZERO WITH NO CONTROL.  So the comparison is not a milestone
    that can be passed and left behind: it runs every time a number is graded,
    against the level that produces it.
    """
    import subprocess
    graded = os.path.join(root, GRADED_CASE)
    checker = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "check_k0h_extraction_equivalence.py")
    if not os.path.isfile(checker):
        refuse(f"{checker} is ABSENT.  The pre-grading equivalence gate cannot "
               f"be run, and a reader never compared against OpenFOAM's own "
               f"sampler is a planted zero with no control.  Refusing rather "
               f"than grading past a gate that is merely missing -- a check "
               f"omitted in silence reads as a check passed.")
    if verbose:
        print("\nPRE-GRADING EQUIVALENCE GATE (K0h section V) on "
              f"{GRADED_CASE}: running OpenFOAM's own postProcess -func sample "
              "against this file's reader.")
    r = subprocess.run([sys.executable, checker, "--case", graded],
                       capture_output=True, text=True)
    if verbose:
        for ln in r.stdout.rstrip().split("\n"):
            print("   | " + ln)
    if r.returncode != 0:
        refuse(f"THE PRE-GRADING EQUIVALENCE GATE DID NOT PASS on "
               f"{GRADED_CASE} (exit {r.returncode}).  Under AD1.1 the "
               f"comparator's reader is WRONG and EVERY GRADED ROW IS "
               f"`NOT A RESULT`.  Refusing to grade.")
    if verbose:
        print("   GATE PASSED -- the reader reproduces OpenFOAM's cellPoint "
              "within the registered criterion, ON THIS LEVEL, IN THIS "
              "INVOCATION.")
    return True


def analyse(root, verbose=True, expect_sha=None, scratch=None):
    """Returns (exit_code, report dict).  Refuses rather than degrading."""
    sha = own_blob_sha()
    if verbose:
        print("=" * 74)
        print("K0d COMPARATOR -- analyse_k0h.py")
        print(f"  this file's git blob sha1: {sha}")
        print("  the OPERATIVE registration is K0d_REREGISTRATION.md;")
        print("  the OPERATIVE cap is 2 748.64 core-min (AMENDMENT 2 A2.2b).")
        print("=" * 74)
    if expect_sha and expect_sha != sha:
        refuse(f"COMPARATOR FREEZE CHECK FAILED: this file hashes to {sha} and "
               f"the committed blob was given as {expect_sha}.  The grading "
               f"path is fixed at the registration commit (Charter 2d) and this "
               f"is not that file.")

    require_markers(root)
    if verbose:
        print(f"\nALL {len(CASES)} DONE markers present.")

    # THE PRE-GRADING EQUIVALENCE GATE, BEFORE ANY GRADED VALUE IS READ.
    assert_extraction_equivalence(root, verbose=verbose)

    # ---- THE THREE PLANTS, BEFORE ANYTHING THAT WILL BE GRADED IS READ -----
    if verbose:
        print("\nPLANTED-ZERO CONTROL (superseded 8.1) -- run BEFORE any graded "
              "value is read:")
    graded_dir = os.path.join(root, GRADED_CASE)
    times = numeric_times(graded_dir) if os.path.isdir(graded_dir) else []
    if not times:
        refuse(f"{graded_dir}: no time directories, so the registered plants "
               f"cannot be run.  A comparator that skips its planted control is "
               f"not evidence (standing rule 3).")
    scratch = scratch or os.path.join(root, ".analyse_k0h_plants")
    plants = run_planted_controls(os.path.join(graded_dir, times[-1]),
                                  scratch, verbose=verbose)

    # ---- load every case through the SAME readers the plants exercised -----
    # STATIONARITY replaces steady convergence (K0h section 7.1'); NO triple is
    # formed (L1+L2 only), so the graded rows are the GRADED_CASE's time-average.
    cf, stationary, yplus, rows_graded, rows_control = {}, {}, {}, {}, {}
    for c in CASES:
        d = os.path.join(root, c)
        if not os.path.isdir(d):
            refuse(f"{d}: DONE.{c} exists but the case directory does not")
        cf[c] = load_case_fields(d)
        n = cf[c]["idx"]["nx"] * cf[c]["idx"]["ny"]
        ok, note = is_stationary(d, n)
        stationary[c] = ok
        yplus[c] = y_plus_max(cf[c])
        rows_graded[c] = extract_rows(cf[c], SCHEME_GRADED)
        rows_control[c] = extract_rows(cf[c], SCHEME_CONTROL)
        if verbose:
            print(f"  {c:<10} stationary={ok}  y+max={yplus[c]:.4f}  ({note})")

    # ---- NO ROACHE TRIPLE.  L1+L2 authorised; a triple needs three levels.
    # The graded arm is GRADED_CASE (the kOmegaSST L2 arm); its stationarity is
    # clause 1 of the verdict ladder, and `triple=None` disables clause 2.
    conv_graded = {GRADED_CASE: stationary[GRADED_CASE]}

    # ---- the guards that survive the L1+L2 arm set --------------------------
    # guard_B / guard_I / guard_seed need B_hi / I_hi / M1_m_seed, which K0h does
    # NOT authorise (deferred to a K0h extension or K0h), so they are not run.
    # guard_DC (discrimination: C_lam vs the graded arm on G6), the dual-scheme
    # control and the y+ window remain.
    gDC_pct, gDC = guard_DC(rows_graded["C_lam"], rows_graded[GRADED_CASE],
                            stationary["C_lam"])
    dual = dual_scheme_control(rows_graded[GRADED_CASE], rows_control[GRADED_CASE])
    gYP = guard_yplus(LEVEL_OF_CASE[GRADED_CASE], yplus[GRADED_CASE])

    if verbose:
        print("\nGUARDS (each withdraws the run, never the hypothesis):")
        print(f"  DC  {'UNMEASURED' if gDC_pct is None else f'{gDC_pct:.2f} %'}"
              f"{'  -> ' + gDC[1] if gDC else '  MET'}")
        print(f"  y+  {yplus[GRADED_CASE]:.4f} on {GRADED_CASE}"
              f"{'  -> ' + gYP[1] if gYP else '  inside the window'}")
        print(f"  M0  REPORTED beside every velocity row: {M0_VELOCITY_PCT} % "
              f"on velocity, {M0_NUSSELT_PCT} % on Nusselt -- NEVER SUBTRACTED")
        print("  (guards B / I / SEED are DEFERRED: their arms B_hi / I_hi / "
              "M1_m_seed are not authorised in K0h)")

    # ---- the reference ------------------------------------------------------
    ref, ref_path = load_reference(root)
    held = ref is not None
    if verbose:
        print(f"\nREFERENCE: {'HELD' if held else 'NOT OBTAINED'}  ({ref_path})")

    # ---- the ten graded rows, on the time-averaged field --------------------
    verdicts, n_pass = {}, 0
    if verbose:
        print("\nTHE TEN GRADED ROWS (on the avg2 [40,60] s time-average):")
    for r in GRADED_ROWS:
        guard = None
        if r == "G6" and gDC:
            guard = gDC
        if dual.get(r) and dual[r][1] and guard is None:
            guard = dual[r][1]
        if gYP and guard is None:
            guard = gYP
        # NO triple (L1+L2 only): clause 2 is disabled by passing None.
        v, why = row_verdict(r, conv_graded, None, guard, held, False, None,
                             plants)
        verdicts[r] = (v, why)
        if v == PASS:
            n_pass += 1
        if verbose:
            band = ROWS[r]["band"]
            if r == "S1":
                bs = "EXACT MATCH, no band"
            elif band is None:
                bs = "REF-scaled (+/-10 % of |q_ref|)"
            else:
                bs = f"+/-{band:g} {ROWS[r]['units']}"
            gv = rows_graded[GRADED_CASE][r]
            val = ("profile" if gv["kind"] == "profile"
                   else (gv["value"] if gv["kind"] == "scalar" else "structural"))
            print(f"  {r:<4} {v:<12} band {bs:<18} {why}"
                  + (f"   [{GRADED_CASE} avg2 value {val:.6g}]"
                     if isinstance(val, float) else ""))

    # ---- the reported rows --------------------------------------------------
    if verbose:
        print("\nREPORTED, NEVER GRADED:")
        print(f"  R1   turbulent kinetic energy on both mid-planes -- REPORTED")
        print(f"  M0   Boussinesq model-form floor {M0_VELOCITY_PCT} % velocity,"
              f" {M0_NUSSELT_PCT} % Nusselt -- REPORTED, NEVER SUBTRACTED")

    # ---- THE RUNG VERDICT ---------------------------------------------------
    rung = GATE_REACHED if not held else (
        PASS if n_pass == len(GRADED_ROWS) else GATE_FAIL)
    if verbose:
        print("\n" + "=" * 74)
        print(f"TALLY: {n_pass} of {len(GRADED_ROWS)}")
        print(f"RUNG VERDICT: {rung}")
        if not held:
            print("  UNREACHED COLUMNS: P AND G.")
            print("  P -- Blay, Mergui and Niculae (1992) is NOT OBTAINED.")
            print("  G -- a Roache triple needs THREE levels; K0h authorises "
                  "L1+L2 only,")
            print("       so there is no triple, no observed order and no GCI.")
            print("  V is reachable: completion, extraction equivalence, the "
                  "STATIONARITY")
            print("  criterion, the achieved y+ and the discrimination control "
                  "are all measured.")
            print("  THIS RUNG CAN NEVER READ `HOLDS` IN THIS STATE, and nobody "
                  "may later read")
            print("  a completed run of it as a graded result against the "
                  "reference.")
        print("=" * 74)
    rc = EXIT_GATEFAIL if any(v == GATE_FAIL for v, _ in verdicts.values()) \
        else EXIT_OK
    return rc, dict(sha=sha, verdicts=verdicts, tally=n_pass,
                    rung=rung, plants=plants, stationary=stationary,
                    yplus=yplus, reference_held=held)


# --------------------------------------------------------------------------
# SELFTEST.  FOR EVERY PLANT AND EVERY GATING BRANCH: a positive case that must
# PASS **and a negative case that must FIRE**.  AMENDMENT 2 section A2.3 is the
# reason this file is explicit about it -- there, a green selftest exercised the
# wrong channel and a real hole went through.  A GREEN SELFTEST IS NOT A GREEN
# INSTRUMENT unless each probe was shown able to fire.
# --------------------------------------------------------------------------
_FAILS = []


def check_(name, ok, note=""):
    print(f"  {'OK  ' if ok else 'FAIL'}  {name}" + (f"   [{note}]" if note else ""))
    if not ok:
        _FAILS.append(name)


def expect_refuse(name, fn, *a, **kw):
    """The NEGATIVE half: this must exit 2.  If it returns, the probe is blind."""
    try:
        fn(*a, **kw)
    except SystemExit as exc:
        check_(name, exc.code == EXIT_REFUSE, f"exit {exc.code}")
        return
    check_(name, False, "RETURNED INSTEAD OF REFUSING -- the probe is blind")


# THE FIXTURE CARRIES A REGISTERED boundaryField.
# It used to write `boundaryField { }` -- an empty block -- and the repaired
# reader REFUSES that, correctly: a `cellPoint` reader with no boundary values
# is the K0d defect, and a fixture that hands it none would test the very
# blindness the repair removes.  The values are the registered ones (section 1):
# floor 308.15 K, ceiling / leftWall / rightWall / inlet 288.15 K, outlet
# zeroGradient; U noSlip at the four walls.
_SYNTH_FLOOR_T, _SYNTH_COLD_T = 308.15, 288.15
_SYNTH_BF_SCALAR = (
    "\nboundaryField\n{\n"
    + "".join("    %s\n    {\n        type            %s;\n%s    }\n"
              % (nm, ty, ("        value           uniform %.10g;\n" % vv)
                 if vv is not None else "")
              for nm, ty, vv in (
                  ("inlet", "fixedValue", _SYNTH_COLD_T),
                  ("outlet", "zeroGradient", None),
                  ("floor", "fixedValue", _SYNTH_FLOOR_T),
                  ("ceiling", "fixedValue", _SYNTH_COLD_T),
                  ("leftWall", "fixedValue", _SYNTH_COLD_T),
                  ("rightWall", "fixedValue", _SYNTH_COLD_T),
                  ("frontAndBack", "empty", None)))
    + "}\n")
_SYNTH_BF_VECTOR = (
    "\nboundaryField\n{\n"
    + "".join("    %s\n    {\n        type            %s;\n%s    }\n"
              % (nm, ty, ("        value           uniform (%.10g 0 0);\n" % vv)
                 if vv is not None else "")
              for nm, ty, vv in (
                  ("inlet", "fixedValue", U_IN),
                  ("outlet", "zeroGradient", None),
                  ("floor", "noSlip", None),
                  ("ceiling", "noSlip", None),
                  ("leftWall", "noSlip", None),
                  ("rightWall", "noSlip", None),
                  ("frontAndBack", "empty", None)))
    + "}\n")


def _write_scalar(path, values, uniform=None):
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                 "    class volScalarField;\n    object T;\n}\n\n"
                 "dimensions      [0 0 0 1 0 0 0];\n\n")
        if uniform is not None:
            fh.write(f"internalField   uniform {uniform!r};\n")
        else:
            fh.write("internalField   nonuniform List<scalar>\n"
                     f"{len(values)}\n(\n")
            fh.write("\n".join(repr(float(v)) for v in values))
            fh.write("\n)\n;\n")
        fh.write(_SYNTH_BF_SCALAR)


def _write_vector(path, values):
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                 "    class volVectorField;\n    object U;\n}\n\n"
                 "dimensions      [0 1 -1 0 0 0 0];\n\n"
                 "internalField   nonuniform List<vector>\n"
                 f"{len(values)}\n(\n")
        fh.write("\n".join(f"({float(a)!r} {float(b)!r} {float(c)!r})"
                           for a, b, c in values))
        fh.write("\n)\n;\n" + _SYNTH_BF_VECTOR)


def _write_fieldaverage_form(src, dst, patch, faces, kind):
    """K0h SEC 4.5 SELFTEST FIXTURE: rewrite `patch` of a field file into the
    form `fieldAverage` ACTUALLY WRITES -- `type calculated` with an explicit
    `value nonuniform List<...>` -- carrying `faces`.

    THE SYNTHETIC FIXTURE THE FROZEN SELFTEST USES WRITES `outlet` AS
    `zeroGradient`, WHICH IS THE ONE FORM THE SECTION 4.5 PATH NEVER SEES.  A
    fixture that cannot present the defect cannot test the repair (AMENDMENT 2
    section A2.3: a green selftest that exercises the wrong channel is how a
    real hole goes through).  This writes the real form, byte-shaped like the
    measured K0g artifacts (declaration line, count, `(`, ONE VALUE PER LINE,
    `)`, `;`)."""
    lines = _read_lines(src)
    spans = _boundary_spans(lines)
    span = None
    for nm, sp in spans.items():
        if nm is not None and patch in _expand_patch_name(nm):
            span = sp
    if span is None:
        refuse(f"{src}: fixture cannot find patch {patch!r}")
    tag = "vector" if kind == "vector" else "scalar"
    body = ["        type            calculated;",
            f"        value           nonuniform List<{tag}> ",
            str(len(faces)), "("]
    for v in faces:
        body.append(f"({float(v[0])!r} {float(v[1])!r} {float(v[2])!r})"
                    if kind == "vector" else repr(float(v)))
    body += [")", ";", "    }"]
    out = lines[:span[0]] + body + lines[span[1] + 1:]
    with open(dst, "w") as fh:
        fh.write("\n".join(out))
    return dst


def _synth_mesh(case_dir, nx=4, na=2, nb=4, nc=2, t=0.010):
    pm = os.path.join(case_dir, "constant", "polyMesh")
    os.makedirs(pm, exist_ok=True)
    xs = [DOMAIN * i / nx for i in range(nx + 1)]
    ys = []
    for blk, n in (("A", na), ("B", nb), ("C", nc)):
        lo, hi = BLOCK_Y[blk]
        for j in range(n):
            ys.append(lo + (hi - lo) * j / n)
    ys.append(BLOCK_Y["C"][1])
    pts = [(x, y, z) for z in (0.0, t) for y in ys for x in xs]
    with open(os.path.join(pm, "points"), "w") as fh:
        fh.write(f"FoamFile{{}}\n{len(pts)}\n(\n")
        fh.write("\n".join(f"({a!r} {b!r} {c!r})" for a, b, c in pts))
        fh.write("\n)\n")
    return nx, len(ys) - 1


def _synth_case(root, case, scale=1.0, nx=4, na=2, nb=4, nc=2,
                end=int(REGISTERED_END_TIME), stationary=True, times=True):
    """A TRANSIENT synthetic case: instantaneous T/U plus the fieldAverage
    outputs TMean/UMean at the avg1 (40) and avg2 (60) directories.  A
    `stationary` case has TMean/UMean equal across the two windows; a
    non-stationary one drifts at the avg2 window by more than the tolerance."""
    d = os.path.join(root, case)
    os.makedirs(d, exist_ok=True)
    nxx, ny = _synth_mesh(d, nx, na, nb, nc)
    n = nxx * ny
    # a smooth, non-degenerate field so profiles and peaks are well defined
    T = [T_REF + DT_BAND * (1.0 - (k // nxx) / max(ny - 1, 1)) * scale
         for k in range(n)]
    U = [(U_IN * math.sin(math.pi * (k // nxx) / max(ny - 1, 1)) * scale,
          0.01 * scale, 0.0) for k in range(n)]
    tt_list = [int(AVG1_TIME), end] if times else [end]
    for tt in tt_list:
        td = os.path.join(d, str(tt))
        os.makedirs(td, exist_ok=True)
        _write_scalar(os.path.join(td, "T"), T)
        _write_vector(os.path.join(td, "U"), U)
        # the time-averaged (graded) fields; drift ONLY at the avg2 window when
        # non-stationary, so is_stationary's avg2-vs-avg1 comparison fires
        wob = 0.0 if (stationary or tt != end) else 1.0
        _write_scalar(os.path.join(td, GRADED_T), [v + wob for v in T])
        _write_vector(os.path.join(td, GRADED_U),
                      [(a + wob, b, c) for a, b, c in U])
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    with open(os.path.join(d, "system", "controlDict"), "w") as fh:
        fh.write(f"endTime {end};\ndeltaT 0.001;\nwriteInterval {AVG1_TIME};\n")
    open(os.path.join(root, f"DONE.{case}"), "w").write("DONE\n")
    return d


def selftest():
    import tempfile
    global _FAILS
    _FAILS = []
    print("=" * 74)
    print("analyse_k0h.py -- SELFTEST.  Every probe: a POSITIVE that must stay")
    print("quiet AND a NEGATIVE that must FIRE.  A probe never shown able to")
    print("fire is not evidence (standing rule 3; AMENDMENT 2 section A2.3).")
    print("=" * 74)
    tmp = tempfile.mkdtemp(prefix="analyse_k0h_selftest_")
    root = os.path.join(tmp, "K0h_runs")
    os.makedirs(root, exist_ok=True)

    # ---------------- registered constants, re-derived --------------------
    print("\n-- REGISTERED CONSTANTS, RE-DERIVED FROM THE REGISTRATION --")
    check_("THIRTEEN graded stations (AMENDMENT 4 A4.5), not eleven",
           len(STATIONS) == 13, f"{len(STATIONS)}")
    check_("0.25 and 0.75 are among them, which is what makes G7 a difference "
           "of two GRADED stations", 0.25 in STATIONS and 0.75 in STATIONS)
    check_("FIVE authorised arms (L1+L2 + C_lam control), not ten",
           len(CASES) == 5, f"{len(CASES)}")
    check_("TEN graded rows", len(GRADED_ROWS) == 10)
    check_("stationarity tolerances are the registered PHYSICAL floors "
           "(tol_T 0.020 K = 1e-3*DT, tol_U 0.005 m/s)",
           STAT_TOL_T == 0.020 and STAT_TOL_U == 0.005)
    check_("the graded fields are the fieldAverage outputs TMean/UMean, not the "
           "instantaneous T/U", GRADED_T == "TMean" and GRADED_U == "UMean")
    check_("sample spacing 1.04/2080 = 5.000e-04 m",
           abs(DOMAIN / (N_POINTS - 1) - SAMPLE_SPACING) < 1e-12)
    check_("bands: G1/G2/G7 +/-1.00 K, G3/G4/G5a +/-0.0570 m/s, G5b +/-0.0208 m,"
           " G8 +/-0.104 m",
           ROWS["G1"]["band"] == 1.00 and ROWS["G3"]["band"] == 0.0570 and
           ROWS["G5b"]["band"] == 0.0208 and ROWS["G8"]["band"] == 0.104)
    check_("every printed verdict word is in the rule-1 vocabulary",
           all(v in VOCABULARY for v in (PASS, GATE_REACHED, GATE_FAIL,
                                         NOT_A_RESULT, BLOCKED, PENDING)))

    # ---------------- P1 / P2 / P3, positive AND negative ------------------
    print("\n-- THE THREE PLANTS: POSITIVE, THEN NEGATIVE --")
    tdir = os.path.join(tmp, "fields")
    os.makedirs(tdir, exist_ok=True)
    # K0h P4: the fixture now carries a MESH and the BASE FIELD `T` as well.
    # P4 reads a patch, so it needs the registered geometry to know which cell
    # is adjacent to which face, and section 4.5 condition (a) reads the base
    # field's patch type.  2 x 6 = 12 cells, matching the twelve values below,
    # and build_index REFUSES if they ever stop matching.
    _synth_mesh(tmp, nx=2, na=2, nb=2, nc=2)
    # a field in which the SAME value repeats, so a regex-over-value plant
    # would hit every occurrence and a line-index plant hits exactly one.
    # The plants go into the GRADED (time-averaged) fields TMean/UMean.
    _write_scalar(os.path.join(tdir, GRADED_T), [0.0] * 12)
    _write_vector(os.path.join(tdir, GRADED_U), [(0.0, 0.0, 0.0)] * 12)
    _write_scalar(os.path.join(tdir, "T"), [0.0] * 12)
    scratch = os.path.join(tmp, "scratch")
    rec = run_planted_controls(tdir, scratch, cell_index=5, verbose=False)
    check_("P1 POSITIVE: PLANT_T seen by the production SCALAR reader",
           rec["P1"]["seen"] == PLANT_T, f"{rec['P1']['seen']!r}")
    check_("P2 POSITIVE: PLANT_U seen by the production VECTOR reader",
           rec["P2"]["seen"] == PLANT_U, f"{rec['P2']['seen']!r}")
    check_("P3 POSITIVE: the 0.0 negative control is NOT DISTINGUISHABLE",
           rec["P3"]["distinguishable"] is False)
    check_("P4 POSITIVE: PLANT_T into an interior outlet-adjacent cell is SEEN "
           "by the PRODUCTION BOUNDARY PATH (read_boundary_values + the "
           "adjacent-cell resolution the graded sampler uses)",
           rec["P4"]["v_a"] != rec["P4"]["v_base"],
           f"{rec['P4']['v_base']!r} -> {rec['P4']['v_a']!r}")
    check_("P4 POSITIVE (exact): with both outlet faces at the probe vertex "
           "planted, the boundary path returns PLANT_T EXACTLY",
           rec["P4"]["v_b"] == PLANT_T, f"{rec['P4']['v_b']!r}")
    check_("P4 runs on the zeroGradient form too -- it is NEVER SKIPPED when "
           "the repaired form is absent (a check omitted in silence reads as a "
           "check passed)", rec["P4"]["form"] == "zeroGradient",
           rec["P4"]["form"])

    # the plant went into a FIELD ON DISK, at a LINE INDEX, and hit ONE cell
    after = read_scalar_field(os.path.join(scratch, "P1_T"))
    check_("P1 PLANTS INTO A FIELD ON DISK, NOT A SPEC OR A DICT",
           os.path.isfile(os.path.join(scratch, "P1_T")))
    check_("P1 plants BY LINE INDEX: exactly ONE of twelve identical values "
           "changed (a regex over the value would have hit all twelve)",
           sum(1 for v in after if v == PLANT_T) == 1 and after[5] == PLANT_T,
           f"{sum(1 for v in after if v == PLANT_T)} changed")
    uafter = read_vector_field(os.path.join(scratch, "P2_U"))
    check_("P2 plants into the X-COMPONENT ONLY, leaving y and z alone",
           uafter[5][0] == PLANT_U and uafter[5][1] == 0.0
           and uafter[5][2] == 0.0)

    # NEGATIVE halves: break the reader and the plant MUST refuse
    real_scalar, real_vector = read_scalar_field, read_vector_field

    def blind_scalar(path, n_cells=None):
        return [0.0] * len(real_scalar(path, n_cells))

    def blind_vector(path, n_cells=None):
        return [(0.0, b, c) for _, b, c in real_vector(path, n_cells)]

    g = globals()
    g["read_scalar_field"] = blind_scalar
    expect_refuse("P1 NEGATIVE: a reader BLIND to the plant is REFUSED",
                  run_planted_controls, tdir, scratch, 5, False)
    g["read_scalar_field"] = real_scalar
    g["read_vector_field"] = blind_vector
    expect_refuse("P2 NEGATIVE: a VECTOR reader blind to the x-component plant "
                  "is REFUSED (a scalar plant would not have caught this)",
                  run_planted_controls, tdir, scratch, 5, False)
    g["read_vector_field"] = real_vector

    def inventing_scalar(path, n_cells=None):
        v = real_scalar(path, n_cells)
        return [x + (1e-9 if "P3_T" in path else 0.0) for x in v]

    g["read_scalar_field"] = inventing_scalar
    expect_refuse("P3 NEGATIVE: a reader that INVENTS a difference where the "
                  "field did not change makes the control FIRE, and that is "
                  "REFUSED", run_planted_controls, tdir, scratch, 5, False)
    g["read_scalar_field"] = real_scalar
    check_("the readers were restored after the negative probes",
           read_scalar_field is real_scalar and read_vector_field is real_vector)

    # ---------------- Roache math: RETAINED, NOT USED IN K0h GRADING -------
    print("\n-- ROACHE MATH (retained; K0h forms NO triple at L1+L2) --")
    # The pure classify/order/GCI functions are kept and unit-tested so a future
    # L3 re-registration inherits proven math, but K0h's grading path forms no
    # triple (main() passes triple=None to row_verdict).
    # a triple built to a KNOWN order p, so the fixed point is checked against
    # an answer computed independently of the code under test
    p_true, A, f_exact = 2.0, 0.5, 10.0
    h1, h2, h3 = 1.0, R21, R21 * R32
    fc, fm, ff = (f_exact + A * h3 ** p_true, f_exact + A * h2 ** p_true,
                  f_exact + A * h1 ** p_true)
    tr = roache(fc, fm, ff)
    check_("CONVERGING is recognised on a monotone refining triple",
           tr["cls"] == CONVERGING, tr["cls"])
    check_("the observed order recovers a PLANTED p = 2.0 from the UNEQUAL-"
           "ratio fixed point", tr["p"] is not None and abs(tr["p"] - 2.0) < 1e-3,
           f"p={tr['p']:.6f}")
    check_("a GCI IS quoted for a monotone CONVERGING triple", tr["gci"] is not None,
           f"{100 * tr['gci']:.4f} %")
    for name, triple, want in (
            ("DIVERGENT", (10.0, 12.0, 15.0), DIVERGENT),
            ("OSCILLATORY", (10.0, 12.0, 11.0), OSCILLATORY),
            ("STAGNANT", (10.0, 12.0, 12.0), STAGNANT),
            ("EXACT", (10.0, 10.0, 10.0), EXACT)):
        t = roache(*triple)
        check_(f"{name} is recognised", t["cls"] == want, t["cls"])
        check_(f"{name}: NO GCI is quoted", t["gci"] is None)
    nm = roache(10.0, 12.0, 11.0)
    check_("NEGATIVE: a NON-MONOTONE triple NEVER gets a GCI (standing rule 5)",
           nm["gci"] is None and not nm["monotone"])

    # ---------------- the verdict ladder, in its registered ORDER ----------
    # K0h: clause 1 is STATIONARITY (not steady convergence), clause 2 (the
    # triple) is DISABLED (triple=None; K0h forms none at L1+L2).
    print("\n-- THE VERDICT LADDER, IN ITS REGISTERED ORDER --")
    stat_ok = {GRADED_CASE: True}
    stat_no = {GRADED_CASE: False}
    v, _ = row_verdict("G1", stat_no, None, None, False, False, None, rec)
    check_("ORDER 1: a NON-STATIONARY arm gives NOT A RESULT",
           v == NOT_A_RESULT, v)
    v2, _ = row_verdict("G1", stat_no, None, None, True, True, None, rec)
    check_("ORDER 1 PRECEDES the rest: non-stationary wins even with a held "
           "reference and an in-band value", v2 == NOT_A_RESULT, v2)
    v4, _ = row_verdict("G1", stat_ok, None, (REPORTED, "guard"), True, True,
                        None, rec)
    check_("ORDER 3: a guard applies its OWN registered consequence",
           v4 == REPORTED, v4)
    v5, _ = row_verdict("G1", stat_ok, None, None, False, True, None, rec)
    check_("ORDER 4: no primary on disk gives BLOCKED, not GATE FAIL and not "
           "PASS (K0h's steady state: P NOT OBTAINED)", v5 == BLOCKED, v5)
    v6, _ = row_verdict("G1", stat_ok, None, None, True, True, None, rec)
    check_("ORDER 5 POSITIVE: primary held and inside the band gives PASS",
           v6 == PASS, v6)
    v7, _ = row_verdict("G1", stat_ok, None, None, True, False, None, rec)
    check_("ORDER 5 NEGATIVE: primary held and OUTSIDE the band gives GATE FAIL",
           v7 == GATE_FAIL, v7)

    # the DIRECTION of the gate
    check_("THE GATE MAY TURN PASS INTO NOT A RESULT",
           gate_is_monotone(PASS, NOT_A_RESULT))
    check_("THE GATE MAY TURN GATE FAIL INTO NOT A RESULT",
           gate_is_monotone(GATE_FAIL, NOT_A_RESULT))
    check_("NEGATIVE: THE GATE MAY NEVER TURN NOT A RESULT INTO PASS",
           not gate_is_monotone(NOT_A_RESULT, PASS))
    check_("NEGATIVE: THE GATE MAY NEVER TURN NOT A RESULT INTO GATE FAIL",
           not gate_is_monotone(NOT_A_RESULT, GATE_FAIL))
    check_("NEGATIVE: THE GATE MAY NEVER TURN BLOCKED INTO PASS",
           not gate_is_monotone(BLOCKED, PASS))
    worst = None
    for cand in (PASS, GATE_FAIL, BLOCKED, REPORTED, NOT_A_RESULT):
        if worst is not None:
            check_(f"ladder monotone: {worst} -> {cand} is not a loosening",
                   gate_is_monotone(worst, cand))
        worst = cand

    # ---------------- the exactly-zero rule --------------------------------
    print("\n-- THE STANDING CONSEQUENCE: AN EXACTLY-ZERO DEVIATION --")
    vz, _ = row_verdict("G1", stat_ok, None, None, True, True, 0.0,
                        {"nonzero_visible": False})
    check_("NEGATIVE: an EXACTLY-ZERO deviation with NO demonstrated non-zero "
           "is NOT A RESULT -- an unsupported zero", vz == NOT_A_RESULT, vz)
    vs, _ = row_verdict("G1", stat_ok, None, None, True, True, 0.0, rec)
    check_("POSITIVE: the same zero IS a result once P1/P2 demonstrated a "
           "non-zero on the same reader in the same invocation", vs == PASS, vs)

    # ---------------- band conversion + anti-widening ----------------------
    print("\n-- THE BAND CONVERSION RULE AND ITS ANTI-WIDENING GUARD --")
    b0, w0, t0 = band_for_row("G1", None)
    check_("with no reference the band is the registered floor", b0 == 1.00
           and not w0 and not t0, f"{b0}")
    b1, w1, t1 = band_for_row("G1", {"u_exp": 0.1, "u_dig": 0.0})
    check_("a SMALL u_exp cannot NARROW the band (max, not min)", b1 == 1.00
           and not w1, f"{b1}")
    b2, w2, t2 = band_for_row("G1", {"u_exp": 0.8, "u_dig": 0.0})
    check_("a LARGE u_exp WIDENS the band, and only through a property of the "
           "reference", b2 > 1.00 and w2, f"{b2:.4f}")
    b3, w3, t3 = band_for_row("G1", {"u_exp": 2.0, "u_dig": 0.0})
    check_("NEGATIVE: the ANTI-WIDENING GUARD trips when 2*u_val > 3*R*S, so an "
           "addendum cannot turn the gate into a formality", t3, f"band {b3:.4f}")

    # ---------------- the marker refusal -----------------------------------
    print("\n-- REFUSALS: EACH SHOWN ABLE TO FIRE --")
    for c in CASES[:4]:
        open(os.path.join(root, f"DONE.{c}"), "w").write("DONE\n")
    expect_refuse("FOUR of five DONE markers is REFUSED",
                  require_markers, root)
    open(os.path.join(root, f"DONE.{CASES[4]}"), "w").write("DONE\n")
    try:
        require_markers(root)
        check_("POSITIVE: five of five markers is accepted", True)
    except SystemExit:
        check_("POSITIVE: five of five markers is accepted", False)

    # ---------------- the ordering assertion -------------------------------
    cdir = _synth_case(tmp, "ordering_case")
    m = read_mesh(cdir)
    nx = len(m["x_lines"]) - 1
    ny = len(m["y_lines"]) - 1
    try:
        build_index(m, nx * ny)
        check_("POSITIVE: build_index accepts a field whose length matches the "
               "mesh", True, f"{nx}x{ny}={nx * ny}")
    except SystemExit:
        check_("POSITIVE: build_index accepts a matching field", False)
    expect_refuse("NEGATIVE: build_index REFUSES a field whose length does not "
                  "match the mesh, rather than silently mis-registering a "
                  "profile", build_index, m, nx * ny + 1)

    # ---------------- the compressed-field refusal -------------------------
    gzdir = os.path.join(tmp, "gzcase")
    os.makedirs(gzdir, exist_ok=True)
    open(os.path.join(gzdir, "T.gz"), "wb").write(b"\x1f\x8b")
    expect_refuse("NEGATIVE: a COMPRESSED field is REFUSED -- AMENDMENT 2 "
                  "A2.1a/A2.1c register ascii and writeCompression off",
                  field_path, gzdir, "T")
    check_("POSITIVE: a plain ascii field is accepted",
           field_path(os.path.join(cdir, str(int(REGISTERED_END_TIME))), "T")
           is not None)

    # ---------------- stationarity, positive and negative ------------------
    print("\n-- STATIONARITY (the time-average's drift is the instrument) --")
    okc = _synth_case(tmp, "stat_ok", stationary=True)
    n_ok = (len(read_mesh(okc)["x_lines"]) - 1) * (len(read_mesh(okc)["y_lines"]) - 1)
    ok1, note1 = is_stationary(okc, n_ok)
    check_("POSITIVE: TMean/UMean unchanged between avg1 and avg2 is STATIONARY",
           ok1, note1[:70])
    badc = _synth_case(tmp, "stat_bad", stationary=False)
    ok2, note2 = is_stationary(badc, n_ok)
    check_("NEGATIVE: a time-average drifting between [20,40] and [40,60] by "
           "more than tol is NOT STATIONARY", not ok2, note2[:70])
    onec = _synth_case(tmp, "stat_one", times=False)
    ok3, note3 = is_stationary(onec, n_ok)
    check_("NEGATIVE: a missing avg1 window is NOT STATIONARY, and the criterion "
           "is NOT assumed to hold", not ok3, note3[:70])

    # ---------------- extraction: the two registered schemes ---------------
    print("\n-- EXTRACTION: THE TWO REGISTERED SCHEMES --")
    cfx = load_case_fields(cdir)
    rg = extract_rows(cfx, SCHEME_GRADED)
    rc_ = extract_rows(cfx, SCHEME_CONTROL)
    check_("the graded scheme is cellPoint and the control is cell "
           "(AMENDMENT 1 A1.3a)",
           SCHEME_GRADED == "cellPoint" and SCHEME_CONTROL == "cell")
    check_("both profile sets carry the registered 2081 sample points",
           len(rg["G1"]["vals"]) == N_POINTS and len(rg["G2"]["vals"]) == N_POINTS)
    check_("the two schemes give DIFFERENT numbers, which is why A1.3b "
           "registers the control at all",
           any(a != b for a, b in zip(rg["G1"]["vals"], rc_["G1"]["vals"])))
    check_("G7 is formed from the GRADED stations 0.75 and 0.25",
           abs(rg["G7"]["value"] -
               (at_station(rg["G1"]["coords"], rg["G1"]["vals"], 0.75) -
                at_station(rg["G1"]["coords"], rg["G1"]["vals"], 0.25))) < 1e-12)
    check_("all ten graded rows are produced", all(r in rg for r in GRADED_ROWS),
           ",".join(GRADED_ROWS))

    print("\n-- THE WALL READER (K0h section V), BOTH BRANCHES DRIVEN --")
    ix = cfx["idx"]
    imid = _locate(ix["x_lines"], 0.5 * (ix["x_lines"][0] + ix["x_lines"][-1]))
    v_new = _vertex_value(ix, cfx["T"], imid, 0, cfx["bT"])
    v_old = _vertex_value(ix, cfx["T"], imid, 0, None)
    check_("POSITIVE: at a FLOOR vertex the repaired reader returns EXACTLY "
           "the registered fixedValue boundary condition",
           abs(v_new - _SYNTH_FLOOR_T) < 1e-12,
           f"{v_new:.6f} K vs BC {_SYNTH_FLOOR_T} K")
    check_("NEGATIVE: the K0d interior-only branch CANNOT see that boundary "
           "condition -- this is the defect, driven rather than described",
           abs(v_old - _SYNTH_FLOOR_T) > 1e-6,
           f"interior-only {v_old:.6f} K, off by {abs(v_old - _SYNTH_FLOOR_T):.6f} K")
    check_("the boundary reader resolves every registered patch, and a "
           "zeroGradient patch stays unresolved for the sampler",
           set(cfx["bT"]) == set(REGISTERED_PATCHES)
           and cfx["bT"]["outlet"] is None
           and cfx["bT"]["frontAndBack"] == "EMPTY",
           f"floor={cfx['bT']['floor']}, outlet={cfx['bT']['outlet']!r}")
    expect_refuse("NEGATIVE: the GRADED cellPoint path REFUSES without boundary "
                  "values -- it can never silently fall back to the K0d branch",
                  sample_line, ix, cfx["T"], "vertical", "cellPoint")
    check_("POSITIVE: the `cell` CONTROL takes no boundary value, so it is "
           "unchanged by the repair",
           sample_cell(ix, cfx["T"], 0.5, 0.0, cfx["bT"])
           == sample_cell(ix, cfx["T"], 0.5, 0.0, None))

    # ---------------- K0h SEC 4.5 + P4, BOTH DIRECTIONS --------------------
    #
    # EVERY NEGATIVE BELOW CHECKS ITS REFUSAL *REASON*, NOT ONLY ITS EXIT CODE.
    # MEASURED WHILE WRITING THIS FILE, AND IT IS THE AMENDMENT 2 A2.3 DEFECT
    # EXACTLY: the first draft of these four probes wrote each variant to a
    # file named `TMean_BADFACE`, `TMean_REVERSED`, ... .  All four refused,
    # all four printed a green `exit 2` -- AND ALL FOUR REFUSED ON THE FILENAME
    # RULE ("does not end in `Mean`"), so conditions (a) and (b) were never
    # driven at all.  A negative probe that refuses for the wrong reason is a
    # green light on an untested channel.
    import io as _io
    import contextlib as _ctx

    def expect_refuse_saying(name, needle, fn, *a, **kw):
        """The NEGATIVE half, WITH ITS REASON CHECKED."""
        buf = _io.StringIO()
        try:
            with _ctx.redirect_stdout(buf):
                fn(*a, **kw)
        except SystemExit as exc:
            txt = buf.getvalue()
            hit = needle in txt
            check_(name, exc.code == EXIT_REFUSE and hit,
                   f"exit {exc.code}, reason matched" if hit
                   else f"exit {exc.code} BUT ON THE WRONG REASON: "
                        f"{txt.strip()[:150]}")
            return
        check_(name, False, "RETURNED INSTEAD OF REFUSING -- the probe is blind")

    print("\n-- K0h SEC 4.5: THE `fieldAverage` NONUNIFORM PATCH, DRIVEN BOTH WAYS --")
    fa_root = os.path.join(tmp, "fa_runs")
    # FOUR outlet faces, not the default two: an element-wise check on two
    # elements is a weak fixture, and the ORDER probe below needs a reversal
    # that is actually different from the original.
    fa_case = _synth_case(fa_root, "FA", times=False, nx=6, na=4, nb=6, nc=2)
    fa_tdir = os.path.join(fa_case, str(int(REGISTERED_END_TIME)))
    fa_t = os.path.join(fa_tdir, GRADED_T)
    fa_base = os.path.join(fa_tdir, "T")
    fa_mesh = read_mesh(fa_case)
    fa_vals = read_scalar_field(fa_t)
    fa_idx = build_index(fa_mesh, len(fa_vals))
    fa_pairs = _patch_face_cells(fa_idx, "outlet")
    fa_good = [fa_vals[c] for _, c in fa_pairs]
    _ZG = ("    outlet\n    {\n        type            zeroGradient;\n    }\n")
    _FV = ("    outlet\n    {\n        type            fixedValue;\n"
           "        value           uniform 288.15;\n    }\n")

    def _fa_variant(tag, faces, base_zg=True, base_present=True, fld=GRADED_T):
        """A variant in its OWN time directory, so the field KEEPS ITS
        REGISTERED NAME and the probe drives the condition under test rather
        than the filename rule.  The mesh is the case's, one level up, which is
        exactly where the production reader looks for it."""
        d = os.path.join(fa_case, "var_" + tag)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, fld)
        _write_fieldaverage_form(fa_t, p, "outlet", faces, "scalar")
        if base_present:
            bt = open(fa_base).read()
            open(os.path.join(d, "T"), "w").write(
                bt if base_zg else bt.replace(_ZG, _FV))
        return p

    check_("the fixture presents a NON-CONSTANT outlet profile, so an "
           "element-wise match is not a coincidence of a flat field",
           len(set(fa_good)) > 1, f"{len(set(fa_good))} distinct of {len(fa_good)}")
    check_("the fixture's base field really does carry a zeroGradient outlet, "
           "which is what condition (a) is about",
           _ZG in open(fa_base).read())

    # POSITIVE: the registered form, written exactly as fieldAverage writes it
    _write_fieldaverage_form(fa_t, fa_t, "outlet", fa_good, "scalar")
    b_fa = read_boundary_values(fa_t, "scalar")
    check_("POSITIVE: a `calculated` NONUNIFORM outlet whose list IS the "
           "adjacent-cell reading resolves to the zeroGradient sentinel -- the "
           "same `None` the frozen reader returns for `T` (section 4.5)",
           b_fa.get("outlet") is None, f"{b_fa.get('outlet')!r}")
    check_("POSITIVE: this file really does carry the form the FROZEN K0g "
           "reader refused -- the repair is exercised, not bypassed",
           _read_patch_list(fa_t, "outlet", "scalar") == fa_good,
           f"{len(fa_good)} faces")
    check_("POSITIVE: every other patch is untouched by the repair",
           b_fa["floor"] == _SYNTH_FLOOR_T and b_fa["frontAndBack"] == "EMPTY")

    # NEGATIVE (b): ONE face off by the smallest representable amount
    off = list(fa_good)
    off[2] = math.nextafter(off[2], math.inf)
    expect_refuse_saying(
        "NEGATIVE 4.5(b): ONE face off by ONE ULP -- the run-time equality "
        "check FIRES and the reader REFUSES.  It is not a tolerance and it is "
        "not downgradeable to a warning",
        "CONDITION (b) FAILED",
        read_boundary_values, _fa_variant("badface", off), "scalar")

    # NEGATIVE (b): the face ORDER reversed, values otherwise identical
    expect_refuse_saying(
        "NEGATIVE 4.5(b): the SAME values in the WRONG FACE ORDER are REFUSED "
        "-- the check is on the ORDER, which is the assumption the whole repair "
        "exists to remove",
        "CONDITION (b) FAILED",
        read_boundary_values, _fa_variant("reversed", list(reversed(fa_good))),
        "scalar")

    # NEGATIVE (b): a list of the wrong length
    expect_refuse_saying(
        "NEGATIVE 4.5(b): a face list SHORTER than the registered geometry's "
        "face count is REFUSED, never silently zipped",
        "CONDITION (b) FAILED",
        read_boundary_values, _fa_variant("short", fa_good[:-1]), "scalar")

    # NEGATIVE (a): the base field's patch is not zeroGradient
    expect_refuse_saying(
        "NEGATIVE 4.5(a): the SAME bit-exact list is REFUSED when the BASE "
        "field's patch is `fixedValue`, not `zeroGradient` -- condition (a) is "
        "load-bearing on its own",
        "CONDITION (a) FAILED",
        read_boundary_values, _fa_variant("basefv", fa_good, base_zg=False),
        "scalar")

    check_("POSITIVE: the SAME list with a zeroGradient base resolves, so the "
           "(a) probe fired on the condition and not on collateral damage",
           read_boundary_values(_fa_variant("basezg", fa_good),
                                "scalar").get("outlet") is None)

    # NEGATIVE (a): the base field is absent -- a check that cannot be
    # performed is not a check that passed
    expect_refuse_saying(
        "NEGATIVE 4.5(a): with the BASE FIELD ABSENT the condition CANNOT BE "
        "CHECKED, and an uncheckable condition REFUSES rather than reading as "
        "satisfied",
        "CANNOT BE CHECKED",
        read_boundary_values, _fa_variant("nobase", fa_good,
                                          base_present=False), "scalar")

    # NEGATIVE: not a fieldAverage output at all
    expect_refuse_saying(
        "NEGATIVE: the resolution is NOT generalised beyond a `fieldAverage` "
        "output -- a field whose name does not end in `Mean` carrying the same "
        "list is REFUSED",
        "not a `fieldAverage` output",
        read_boundary_values, _fa_variant("inst", fa_good, fld="Tinst"),
        "scalar")

    # NEGATIVE: the type is not `calculated`
    _fixed = _fa_variant("typefixed", fa_good)
    _ftxt = open(_fixed).read()          # READ FIRST: `open(p,"w")` truncates
    open(_fixed, "w").write(_ftxt.replace(
        "type            calculated;", "type            fixedValue;"))
    expect_refuse_saying(
        "NEGATIVE: a NONUNIFORM list on a patch that is not `type calculated` "
        "is REFUSED -- section 4.5 registers the resolution for what "
        "`fieldAverage` writes and nothing else",
        "Section 4.5 registers the resolution for `calculated`",
        read_boundary_values, _fixed, "scalar")

    print("\n-- K0h P4: THE PLANTED CONTROL ON THE REPAIRED PATH, BOTH WAYS --")
    fa_scratch = os.path.join(tmp, "p4_scratch")
    rec4 = run_planted_controls(fa_tdir, fa_scratch, cell_index=0, verbose=False)
    p4 = rec4["P4"]
    check_("P4 ran on the REPAIRED form, not the zeroGradient one -- the plant "
           "exercises the channel section 4.5 added",
           p4["form"].startswith("fieldAverage"), p4["form"])
    check_("P4a POSITIVE: a PLANT_T into ONE interior outlet-adjacent cell of a "
           "COPY is SEEN by the production boundary path",
           p4["v_a"] != p4["v_base"], f"{p4['v_base']!r} -> {p4['v_a']!r}")
    check_("P4b POSITIVE: with BOTH faces at the probe vertex planted, the "
           "production boundary path returns the PLANTED VALUE EXACTLY -- not "
           "merely a different one",
           p4["v_b"] == PLANT_T, f"{p4['v_b']!r}")
    check_("P4 plants into COPIES and never the real field on disk",
           read_scalar_field(fa_t)[fa_pairs[0][1]] != PLANT_T
           and os.path.isfile(os.path.join(fa_scratch, "P4a",
                                           str(int(REGISTERED_END_TIME)),
                                           GRADED_T)))
    check_("P4's planted copy is a CONSISTENT field that section 4.5 ACCEPTED, "
           "so the equality check is exercised on values that are NOT the ones "
           "measured pre-compute -- it is not a comparison that only ever "
           "succeeds because nothing ever changes",
           _read_patch_list(os.path.join(fa_scratch, "P4a",
                                         str(int(REGISTERED_END_TIME)),
                                         GRADED_T),
                            "outlet", "scalar")[0] == PLANT_T)

    g = globals()
    real_rbv = read_boundary_values

    def blind_patch(path, kind):
        out = real_rbv(path, kind)
        if "P4a" in path or "P4b" in path:
            out["outlet"] = "EMPTY"        # a reader that cannot place the patch
        return out

    g["read_boundary_values"] = blind_patch
    expect_refuse_saying(
        "P4 NEGATIVE: a boundary reader that CANNOT PLACE the outlet patch is "
        "REFUSED -- P4 is not satisfied by a graded number merely existing",
        "P4a FAILED", run_planted_controls, fa_tdir, fa_scratch, 0, False)
    g["read_boundary_values"] = real_rbv

    real_vv = _vertex_value

    def deaf_vertex(idx_, values, i, j, bvals=None):
        return 0.0                          # a path that sees nothing at all

    g["_vertex_value"] = deaf_vertex
    expect_refuse_saying(
        "P4 NEGATIVE: a boundary path DEAF to the plant (same value planted or "
        "not) is REFUSED -- a reader not shown able to see a non-zero is not "
        "evidence (standing rule 3)",
        "P4a FAILED", run_planted_controls, fa_tdir, fa_scratch, 0, False)
    g["_vertex_value"] = real_vv
    check_("the readers were restored after the P4 negative probes",
           read_boundary_values is real_rbv and _vertex_value is real_vv)

    print("\n" + "=" * 74)
    if _FAILS:
        print(f"SELFTEST FAILED: {len(_FAILS)} check(s) did not hold")
        for f in _FAILS:
            print(f"  - {f}")
    else:
        print("SELFTEST PASSED: every plant and every gating branch was shown")
        print("able to FIRE on a planted defect and to STAY QUIET on its clean")
        print("counterpart.  A probe never shown able to fire is not evidence.")
    print("=" * 74)
    shutil.rmtree(tmp, ignore_errors=True)
    return EXIT_OK if not _FAILS else EXIT_GATEFAIL


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="K0d comparator -- the grader.  Refuses rather than degrades.")
    ap.add_argument("--root", help="the K0h_runs directory")
    ap.add_argument("--expect-sha",
                    help="the committed blob sha1 of this file; the comparator "
                         "REFUSES if it does not match (Charter 2d)")
    ap.add_argument("--scratch", help="where the planted copies are written")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.root:
        ap.error("--root is required (or --selftest)")
    if not os.path.isdir(a.root):
        refuse(f"{a.root}: not a directory")
    rc, _ = analyse(a.root, verbose=True, expect_sha=a.expect_sha,
                    scratch=a.scratch)
    return rc


if __name__ == "__main__":
    sys.exit(main())
