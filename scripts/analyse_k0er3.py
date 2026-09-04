#!/usr/bin/env python3
"""analyse_k0er3.py -- THE FROZEN GRADING PATH FOR K0eR3.

Campaign F14 cooling ladder, rung K0eR3: the forced-convection flat plate
against Bahrami (2005), NASA/TM-2005-212841.  Registered by
`docs/campaigns/F14-cooling-ladder/K0eR3_PREREGISTRATION.md`, whose section 9
specifies every row, every threshold and every refusal in this file, and whose
pre-compute addendum pins this file by git blob sha.

WHAT K0eR3 CHANGED, AND WHY THIS IS A NEW FILE RATHER THAN AN EDIT
------------------------------------------------------------------
K0eR2 was graded NOT A RESULT.  Its zero-dT control arm `FP_T00` is DEGENERATE
BY DESIGN: with the plate, the inlet and the internal field all at 300 K,
`T == 300` is simultaneously the initial condition and the exact steady
solution, so the residual normaliser degenerates to round-off and every T solve
runs to the smoothSolver's 1000-sweep cap.  Measured: 349 of 349 T solves at
`No Iterations 1000` against 0 of 9000 on the thermal arm; 8.99 s/it against
0.3126; ~2696 core-min needed against a 105.00 core-min cap.

That arm carried TWO JOBS and the conflation was the defect:
  JOB A  the second operand of M4b, which requires the two arms be IDENTICAL in
         every operator except the wall temperature;
  JOB B  the physical zero-heat-flux control, which requires dT be identically
         zero -- and dT == 0 is exactly what makes the solve degenerate.

K0eR3 SPLITS THEM.
  C1  M4b's second operand becomes FP_T290 (plate at 290 K, dT = -10 K).  One
      line differs from FP_T10, so the premise is preserved LITERALLY, and P7
      below makes that a BLOCKING REFUSAL rather than an expectation.  The pair
      (-10, +10) also DOUBLES the drive on any leak: the only T-to-U route in
      buoyantBoussinesqSimpleFoam v2606 is `rhok = 1 - beta*(T - TRef)`, which
      is LINEAR and therefore ODD in (T - TRef).
  C2  Job B moves to Z1/Z2/Z3 -- PLANTED ON-DISK controls at ZERO solver
      compute.  Z1 constructs the exact uniform-300 T field and requires the
      production wall-flux reader to return identically zero on all plate
      faces; Z2 plants a known non-zero at a NAMED plate-face owner cell and
      REFUSES if the reader does not move; Z3 plants at a NAMED interior cell
      and REFUSES if the plate reader DOES move.
  C3  No arm or artifact in this rung is simultaneously the operand of a
      bit-exactness comparison and the carrier of a physical null.

WHAT THIS FILE MAY AND MAY NOT PRODUCE
--------------------------------------
GATED: M4b (0 ULP, non-zero -> GATE FAIL) and Z1 (0 ULP against 0.0, non-zero
-> NOT A RESULT).  Everything else is REPORTED.  No band is armed on the
Stanton correlation, so no PASS and no GATE FAIL is reachable there.

A NON-ZERO M4b IS `GATE FAIL`, NOT `NOT A RESULT`, and that is a deliberate
departure from the predecessor registered at K0eR3 section 5.2: a non-zero ULP
distance between two COMPLETE arms is a MEASUREMENT that failed a threshold
frozen before compute, which is what GATE FAIL means.  NOT A RESULT is reserved
here for a row that could not be measured.  THE THRESHOLD IS UNCHANGED AT 0 ULP.

NO ROACHE TRIPLE IS FORMED.  Two arms on ONE mesh.  Standing rule 5 does not
engage, no GCI is computed and none is printed.

TWO PREDECESSOR TRAPS ARE CLOSED IN CODE, NOT IN PROSE
-------------------------------------------------------
1. `analyse_k0e.py` returned EXIT_OK on BOTH branches -- it exited 0 while
   printing NOT A RESULT, so a reader scripting against `$?` read success.  The
   same shape is in `analyse_t3d.py` (its main() returns EXIT_OK unconditionally
   after grading).  THIS FILE EXITS NON-ZERO ON ANY VERDICT THAT IS NOT PASS.
   The verdict of record is still taken from stdout and the landed artifact,
   never from the exit code.
2. `analyse_k0e.py:735` printed a HARD-CODED banner naming the PREDECESSOR's
   registration while running under a different one.  THIS FILE TAKES THE
   REGISTRATION PATH AS A REQUIRED ARGUMENT AND PRINTS WHAT IT WAS GIVEN.

EXIT CODES
  0  PASS -- and only PASS
  1  GATE FAIL or NOT A RESULT: a graded row was measured and failed, or could
     not be measured
  2  REFUSAL -- a plant unseen, a negative control that fired, the premise diff
     broken, a sha mismatch, or any reader that could not be trusted
"""

import sys

# No .pyc may land beside a pinned comparator.  A stale __pycache__ has been
# measured in this lab to INVERT a mutation test -- the clean control failing
# while the mutated case passed -- and PYTHONDONTWRITEBYTECODE in the
# environment is not relied on, because this file may be invoked by a harness
# that does not set it.
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
import re
import shutil
import struct

EXIT_PASS, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# ---------------------------------------------------------------------------
# THE REGISTERED CONSTANTS.  Frozen with K0eR3_PREREGISTRATION.md.
# ---------------------------------------------------------------------------
END_TIME_ARMS = 9000     # FP_T10 and FP_T290
END_TIME_D0 = 200        # the determinism twins
RANKS = 2
NU = 2e-07               # m2/s
PR = 0.71
PRT = 0.85
U_INF = 1.0              # m/s
T_INF = 300.0            # K

GRADED_ARM = "FP_T10"          # plate 310 K, dT = +10 K
CONTROL_ARM = "FP_T290"        # plate 290 K, dT = -10 K
MAIN_ARMS = (GRADED_ARM, CONTROL_ARM)
D0_TWINS = ("D0_A", "D0_B")
ARM_T_WALL = {GRADED_ARM: 310.0, CONTROL_ARM: 290.0}
ARM_DT = {GRADED_ARM: 10.0, CONTROL_ARM: -10.0}
PLATE_PATCH = "plate"
PLATE_FACES_REGISTERED = 208
CELLS_REGISTERED = 52224
REFERENCE_DEFAULT = "/home/ubuntu/certonomous-runs/tmr-flatplate-finer"

# The premise P7 protects: the two main arms differ in EXACTLY ONE FILE, in
# EXACTLY ONE LINE, and that line is the plate's fixedValue in 0/T.  K0eR2
# measured that line at index 39 (0-based 38); the index is PRINTED here and the
# refusal is on the SEMANTICS of the line, which is the stronger check -- a
# refusal keyed only on an integer would break on a header edit that changed
# nothing physical, and would pass a physical change that happened to land on
# line 39.
PREMISE_DIFF_SCOPE = ("0", "constant", "system")
PREMISE_DIFF_FILE = os.path.join("0", "T")
PREMISE_LINE_INDEX_EXPECTED_1BASED = 39

# Bahrami eq. (1), as printed on line 353 of the .txt sidecar of
# docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf
#   St = 0.0296 Re^-0.2 (Pr Tw / T_inf)^-0.4
EQ1_COEFF = 0.0296
EQ1_RE_EXP = -0.2
EQ1_PRTW_EXP = -0.4

# The reported Stanton stations, fixed in the registration BEFORE any compute.
RE_X_STATIONS = (1.0e6, 2.0e6, 3.0e6, 5.0e6, 7.0e6, 1.0e7)

# Fields the strict completion rule requires present at endTime.
REQUIRED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

# The registered plants (standing rule 3).
PLANT_T = 1.234e-03      # K, into a COPY of the graded arm's endTime T
PLANT_U = 1.234e-03      # m/s, into the X-COMPONENT of a COPY of its U
PLANT_ZERO = 0.0         # the NEGATIVE control: a plant of exactly zero
Z_BACKGROUND = 300.0     # the exact uniform field Z1 constructs

# rule 1 vocabulary, and NOTHING ELSE may be printed as a verdict
PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
# non-verdict row states, kept deliberately distinct from the vocabulary
REPORTED, UNMEASURED, NOT_REACHED = "REPORTED", "UNMEASURED", "NOT REACHED"


def refuse(msg):
    """REFUSE (exit 2) rather than degrade."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ---------------------------------------------------------------------------
# THE D-J1 CLAUSE, IN ONE PLACE.
#
# D-J1 is `rel = dmax / rng if rng > 0 else 0.0` -- a divide-by-zero guard that
# substitutes THE VALUE WHICH GRADES BEST.  K0eR3 section 5.6 registers a
# blanket clause: NO COMPARATOR IN THIS RUNG MAY SUBSTITUTE A VALUE ON A ZERO
# DENOMINATOR.  Every zero-denominator branch returns NOT A RESULT or refuses;
# none returns 0.0, none returns a pass, and none is silently skipped.
#
# THIS IS THE ONLY IMPLEMENTATION.  Three copies of a guard drift apart, and the
# copy that drifts is the one that grades.
# ---------------------------------------------------------------------------
def guarded_div(numer, denom, what):
    """Return (value, state, why).

    state is REPORTED with a value, or NOT A RESULT with value None.  It is
    NEVER a substituted number.  A NaN operand refuses outright: a NaN that
    reaches a comparator is a broken reader, not a small number."""
    fn, fd = float(numer), float(denom)
    if fn != fn or fd != fd:
        refuse(f"{what}: a NaN reached the division guard (numerator {fn!r}, "
               f"denominator {fd!r}).  Refusing rather than reporting a ratio "
               f"for a value that is not a number.")
    if fd == 0.0:
        return None, NOT_A_RESULT, (
            f"{what}: the denominator is exactly zero, so the ratio is "
            f"UNDEFINED rather than small.  Registered behaviour (K0eR3 "
            f"section 5.6): NOT A RESULT, never 0.0 and never skipped.")
    return fn / fd, REPORTED, None


def guarded_series(pairs, what):
    """Apply guarded_div over (numer, denom) pairs.  Returns
    (values, n_excluded, reasons) -- the EXCLUDED COUNT IS ALWAYS RETURNED so a
    caller can print it, because an unstated exclusion is an unstated blind
    spot."""
    vals, excluded, reasons = [], 0, []
    for i, (n, d) in enumerate(pairs):
        v, state, why = guarded_div(n, d, f"{what}[{i}]")
        if state == NOT_A_RESULT:
            excluded += 1
            if len(reasons) < 3:
                reasons.append(why)
        else:
            vals.append(v)
    return vals, excluded, reasons


# ---------------------------------------------------------------------------
# THE PIN.  own_blob_sha() is the GIT BLOB SHA-1 of this file:
#     sha1(b"blob " + str(len(content)) + b"\0" + content)
# IT IS NOT A SHA-256 AND IT IS NOT A PLAIN SHA-1 OF THE BYTES.  The
# registration names the hash function beside the digit string for exactly this
# reason: a pin compared against the wrong digest is not a pin.
#
# `--expect-sha` IS REQUIRED, not optional.  K0eR2's grader made it optional to
# argparse, so omitting it silently DISARMED the check; that is a fail-open and
# it is closed here by making argparse refuse.
# ---------------------------------------------------------------------------
def own_blob_sha():
    with open(os.path.abspath(__file__), "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# ULP.  THE M4b AND Z1 THRESHOLDS ARE EXPRESSED HERE AND NOWHERE ELSE, AS AN
# INTEGER COUNT OF REPRESENTABLE DOUBLES BETWEEN THE TWO OPERANDS.  There is no
# tolerance constant in this file and there must never be one: a hardcoded
# "equivalent" epsilon is a band nobody registered, arrived at after the fact.
# ---------------------------------------------------------------------------
def _ulp_key(x):
    """Monotone signed-magnitude ordering key for an IEEE-754 binary64.

    k(+0.0) == k(-0.0) == 0, and k is strictly increasing in x, so
    |k(a) - k(b)| is the number of representable doubles between a and b."""
    i = struct.unpack("<q", struct.pack("<d", float(x)))[0]
    return i if i >= 0 else (-0x8000000000000000 - i)


def ulp_distance(a, b):
    """Representable doubles between a and b.  0 iff the two doubles are the
    same value (with +0.0 and -0.0 treated as the same value)."""
    fa, fb = float(a), float(b)
    if fa != fa or fb != fb:
        refuse("a NaN reached the ULP comparator; refusing rather than "
               "reporting a distance for a value that is not a number")
    return abs(_ulp_key(fa) - _ulp_key(fb))


# ---------------------------------------------------------------------------
# THE PRODUCTION FIELD READERS.  The plants below are read back THROUGH THESE,
# and the graded path calls THESE.  If that stops being true the plants stop
# being evidence.  Carried across from analyse_k0e.py unchanged in behaviour.
# ---------------------------------------------------------------------------
def field_path(tdir, field):
    plain = os.path.join(tdir, field)
    if os.path.isfile(plain):
        return plain
    if os.path.isfile(plain + ".gz"):
        refuse(f"{plain}.gz is COMPRESSED.  The registration fixes writeFormat "
               f"ascii and writeCompression off; refusing rather than reading a "
               f"field the registration says should not exist in this form.")
    return None


def _read_lines(path):
    with open(path, "r") as fh:
        return fh.read().split("\n")


def locate_internal_field(lines):
    """Locate internalField, RETURNING LINE INDICES so that a plant can be made
    BY LINE INDEX and never by a regex over the value."""
    for i, ln in enumerate(lines):
        if not ln.strip().startswith("internalField"):
            continue
        m = re.match(r"\s*internalField\s+uniform\s+(.+?);\s*$", ln)
        if m:
            return dict(mode="uniform", raw=m.group(1).strip(), decl_line=i)
        if "nonuniform" in ln:
            m2 = re.search(r"nonuniform\s+List<\w+>\s+([0-9]+)", ln)
            if m2:
                count, j = int(m2.group(1)), i
            else:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines) or not re.fullmatch(r"[0-9]+", lines[j].strip()):
                    return None
                count = int(lines[j].strip())
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
        refuse(f"cannot parse {tok!r} as a scalar")


def _parse_vector(tok):
    m = re.fullmatch(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)", tok.strip())
    if not m:
        refuse(f"cannot parse {tok!r} as a vector")
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)))


def read_scalar_field(path, n_cells=None):
    """PRODUCTION SCALAR READER.  P1, P3, Z1, Z2 and Z3 read back through it."""
    lines = _read_lines(path)
    info = locate_internal_field(lines)
    if info is None:
        refuse(f"{path}: no internalField could be located")
    if info["mode"] == "uniform":
        if n_cells is None:
            refuse(f"{path}: a uniform internalField needs the cell count to "
                   f"expand and none was supplied; refusing rather than "
                   f"guessing a length")
        return [_parse_scalar(info["raw"])] * n_cells
    out, idx = [], info["first_value_line"]
    for _ in range(info["count"]):
        out.append(_parse_scalar(lines[idx].strip()))
        idx += 1
    return out


def read_vector_field(path, n_cells=None):
    """PRODUCTION VECTOR READER.  P2 reads back through this.  It is a SEPARATE
    parser from read_scalar_field, which is why P2 exists at all: a scalar plant
    does not exercise a vector reader, and M4b reads VECTORS."""
    lines = _read_lines(path)
    info = locate_internal_field(lines)
    if info is None:
        refuse(f"{path}: no internalField could be located")
    if info["mode"] == "uniform":
        if n_cells is None:
            refuse(f"{path}: a uniform vector internalField needs the cell count")
        return [_parse_vector(info["raw"])] * n_cells
    out, idx = [], info["first_value_line"]
    for _ in range(info["count"]):
        out.append(_parse_vector(lines[idx].strip()))
        idx += 1
    return out


def _patch_block(path, patch):
    lines = _read_lines(path)
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "boundaryField":
            start = i
            break
    if start is None:
        refuse(f"{path}: no boundaryField")
    for i in range(start, len(lines)):
        if lines[i].strip() == patch:
            return lines, i
    refuse(f"{path}: patch {patch!r} not present in boundaryField")


def _patch_value_line(path, patch):
    """The LINE INDEX of a patch's `value` entry, so a plant into a patch is
    made by line index like every other plant in this lab."""
    lines, i = _patch_block(path, patch)
    depth, j = 0, i
    while j < len(lines):
        s = lines[j].strip()
        if s == "{":
            depth += 1
        elif s == "}":
            depth -= 1
            if depth == 0:
                break
        elif s.startswith("value"):
            return lines, j
        j += 1
    refuse(f"{path}: patch {patch!r} carries no `value` entry")


def read_patch_values(path, patch, vector, n_faces):
    """Read one patch's `value` entry, uniform or nonuniform, through the same
    scalar / vector token parsers the internal readers use."""
    lines, i = _patch_block(path, patch)
    depth = 0
    j = i
    while j < len(lines):
        s = lines[j].strip()
        if s == "{":
            depth += 1
        elif s == "}":
            depth -= 1
            if depth == 0:
                break
        elif s.startswith("value"):
            m = re.match(r"value\s+uniform\s+(.+?);\s*$", s)
            if m:
                v = (_parse_vector(m.group(1)) if vector
                     else _parse_scalar(m.group(1)))
                return [v] * n_faces
            m2 = re.search(r"nonuniform\s+List<\w+>\s+([0-9]+)", s)
            if "nonuniform" in s:
                if m2:
                    count, k = int(m2.group(1)), j
                else:
                    k = j + 1
                    while k < len(lines) and not lines[k].strip():
                        k += 1
                    count = int(lines[k].strip())
                if count == 0:
                    # an empty patch list: this processor owns no face of the
                    # patch.  Return the empty list rather than scanning on to
                    # the next '(' in the file, which would belong to a
                    # DIFFERENT patch and would be read as this one's values.
                    return []
                while k < len(lines) and lines[k].strip() != "(":
                    k += 1
                out = []
                idx = k + 1
                for _ in range(count):
                    tok = lines[idx].strip()
                    out.append(_parse_vector(tok) if vector else _parse_scalar(tok))
                    idx += 1
                return out
            if re.match(r"value\s+nonuniform\s+0\s*\(\s*\)\s*;", s):
                return []
        j += 1
    refuse(f"{path}: patch {patch!r} carries no `value` entry, so its wall "
           f"values cannot be read; refusing rather than substituting the "
           f"internal field")


# ---------------------------------------------------------------------------
# THE MESH READERS.  Only two mesh files are read, and both are ASCII lists.
# ---------------------------------------------------------------------------
def read_boundary_patch(case, patch):
    path = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.isfile(path):
        refuse(f"{path} missing; the plate patch range cannot be read")
    txt = open(path).read()
    m = re.search(r"\n\s*" + re.escape(patch) + r"\s*\n\s*\{(.*?)\n\s*\}",
                  txt, re.S)
    if not m:
        refuse(f"{path}: patch {patch!r} not found")
    body = m.group(1)
    nf = re.search(r"nFaces\s+([0-9]+)\s*;", body)
    sf = re.search(r"startFace\s+([0-9]+)\s*;", body)
    if not nf or not sf:
        refuse(f"{path}: patch {patch!r} has no nFaces/startFace")
    return int(nf.group(1)), int(sf.group(1))


def read_labelled_list(path):
    """Read an OpenFOAM ASCII label list (constant/polyMesh/owner)."""
    if not os.path.isfile(path):
        refuse(f"{path} missing")
    lines = _read_lines(path)
    for i, ln in enumerate(lines):
        if re.fullmatch(r"[0-9]+", ln.strip()):
            k = i + 1
            while k < len(lines) and lines[k].strip() != "(":
                k += 1
            if k >= len(lines):
                continue
            count = int(lines[i].strip())
            out = []
            idx = k + 1
            for _ in range(count):
                out.append(int(lines[idx].strip()))
                idx += 1
            return out
    refuse(f"{path}: no label list could be located")


def end_time_of(case):
    """The case's OWN registered endTime, read from its own controlDict.

    Read rather than assumed, because K0eR3 runs two different endTimes (9000
    for the arms, 200 for the D0 twins) and a module constant applied to the
    wrong case would compare a completed run against the wrong target."""
    cd = os.path.join(case, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse(f"{cd} missing; this case cannot state its own endTime and the "
               f"completion rule's clause 3 has nothing to compare against.")
    m = re.search(r"(?m)^endTime\s+([0-9]+)\s*;", open(cd).read())
    if not m:
        refuse(f"{cd}: no endTime entry could be read")
    return int(m.group(1))


# ---------------------------------------------------------------------------
# P7 -- THE PREMISE REFUSAL.  M4b's entire evidentiary content is the premise
# "one binary, one operator set, two wall temperatures".  K0eR2 checked that
# AFTER THE FACT, in its results prose.  Here it is armed BEFORE and it BLOCKS.
# ---------------------------------------------------------------------------
def _hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk_rel(case, subdirs):
    out = {}
    for sub in subdirs:
        base = os.path.join(case, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in sorted(filenames):
                p = os.path.join(dirpath, fn)
                out[os.path.relpath(p, case)] = p
    return out


def premise_diff_or_refuse(case_a, case_b, label_a, label_b):
    """REFUSE unless the two arms differ in EXACTLY ONE FILE, in EXACTLY ONE
    LINE, and that line is the plate's fixedValue in 0/T carrying the two
    registered wall temperatures."""
    fa, fb = _walk_rel(case_a, PREMISE_DIFF_SCOPE), _walk_rel(case_b, PREMISE_DIFF_SCOPE)
    only_a, only_b = sorted(set(fa) - set(fb)), sorted(set(fb) - set(fa))
    if only_a or only_b:
        refuse(f"the arms do not carry the same file set over "
               f"{list(PREMISE_DIFF_SCOPE)}: only in {label_a} {only_a}; only in "
               f"{label_b} {only_b}.  M4b's premise is that the arms differ in "
               f"the wall temperature and in NOTHING ELSE; refusing.")
    differing = [rel for rel in sorted(fa)
                 if _hash_file(fa[rel]) != _hash_file(fb[rel])]
    if differing != [PREMISE_DIFF_FILE]:
        refuse(f"the arms differ in {len(differing)} file(s) over "
               f"{list(PREMISE_DIFF_SCOPE)}: {differing}.  The registration "
               f"fixes EXACTLY ONE differing file, {PREMISE_DIFF_FILE!r}.  A "
               f"second difference means M4b no longer isolates a beta/g leak; "
               f"refusing rather than grading a comparison whose premise is "
               f"false.")
    la, lb = _read_lines(fa[PREMISE_DIFF_FILE]), _read_lines(fb[PREMISE_DIFF_FILE])
    if len(la) != len(lb):
        refuse(f"{PREMISE_DIFF_FILE}: line counts differ, {len(la)} vs {len(lb)}")
    idx = [i for i in range(len(la)) if la[i] != lb[i]]
    if len(idx) != 1:
        refuse(f"{PREMISE_DIFF_FILE}: {len(idx)} differing lines at 1-based "
               f"{[i + 1 for i in idx]}; the registration fixes EXACTLY ONE.")
    i = idx[0]
    # The refusal is on the SEMANTICS of the differing line, which is stronger
    # than a line-number test in both directions.  The index is PRINTED so the
    # registration's 39 stays checkable by a reader.
    _lines_p, vline = _patch_value_line(fa[PREMISE_DIFF_FILE], PLATE_PATCH)
    if i != vline:
        refuse(f"{PREMISE_DIFF_FILE}: the single differing line is at 1-based "
               f"{i + 1}, which is NOT the {PLATE_PATCH!r} patch `value` line "
               f"(1-based {vline + 1}).  The arms differ somewhere other than "
               f"the wall temperature; refusing.")
    ma = re.match(r"\s*value\s+uniform\s+([0-9.eE+-]+)\s*;\s*$", la[i])
    mb = re.match(r"\s*value\s+uniform\s+([0-9.eE+-]+)\s*;\s*$", lb[i])
    if not ma or not mb:
        refuse(f"{PREMISE_DIFF_FILE} line {i + 1}: not a `value uniform <T>;` "
               f"entry on both sides -- {la[i]!r} / {lb[i]!r}")
    va, vb = float(ma.group(1)), float(mb.group(1))
    want_a, want_b = ARM_T_WALL[label_a], ARM_T_WALL[label_b]
    if ulp_distance(va, want_a) != 0 or ulp_distance(vb, want_b) != 0:
        refuse(f"{PREMISE_DIFF_FILE} line {i + 1}: plate wall temperatures read "
               f"{va!r} ({label_a}) and {vb!r} ({label_b}); the registration "
               f"fixes {want_a!r} and {want_b!r}.")
    return dict(files_compared=len(fa), differing_file=PREMISE_DIFF_FILE,
                line_1based=i + 1,
                line_1based_expected=PREMISE_LINE_INDEX_EXPECTED_1BASED,
                t_wall_a=va, t_wall_b=vb)


# ---------------------------------------------------------------------------
# THE STRICT COMPLETION RULE (standing rule 4).  ALL-OR-NOTHING, SIX CLAUSES.
# The age-guard datum is the case's OWN `0/T`.  K0eR3 is SINGLE-REGION -- one
# mesh, one case, no regions -- so `0/T` is the correct dating file, and
# scripts/launch_k0e.sh touches it LAST, immediately before the solver, which is
# what makes it a valid datum rather than an assumed one.
# ---------------------------------------------------------------------------
def completion(root, arm, end_time):
    case = os.path.join(root, arm)
    status = os.path.join(root, f"STATUS.{arm}")
    log = os.path.join(case, "log.solve")
    tdir = os.path.join(case, str(end_time))
    zero_t = os.path.join(case, "0", "T")
    cl, ok = {}, True

    # clause 1 -- rc = 0, from a STATUS file written by the launcher.
    if not os.path.isfile(status):
        cl[1] = f"FAIL no STATUS.{arm}"
        ok = False
    else:
        txt = open(status).read()
        cl[1] = ("PASS rc=0" if re.search(r"(^|\s)rc=0(\s|$)", txt)
                 else f"FAIL {txt.strip()[:120]}")
        ok = ok and cl[1].startswith("PASS")

    if not os.path.isfile(log):
        cl[2] = cl[3] = cl[5] = "FAIL no log.solve"
        ok = False
    else:
        loglines = _read_lines(log)
        n_end = sum(1 for l in loglines if l.strip() == "End")
        cl[2] = ("PASS exactly one End line" if n_end == 1
                 else f"FAIL {n_end} End lines, expected exactly 1")
        times = [float(m.group(1)) for m in
                 (re.match(r"^Time = ([0-9.eE+-]+)$", l.strip()) for l in loglines)
                 if m]
        cl[3] = (f"PASS last time == endTime {end_time}"
                 if times and times[-1] == float(end_time)
                 else f"FAIL last time {times[-1] if times else None} != {end_time}")
        n_exec = sum(1 for l in loglines if l.startswith("ExecutionTime"))
        cl[5] = (f"PASS ExecutionTime count == {end_time}"
                 if n_exec == end_time
                 else f"FAIL ExecutionTime count {n_exec} != {end_time}")
        ok = ok and all(cl[i].startswith("PASS") for i in (2, 3, 5))

    missing = [f for f in REQUIRED_FIELDS if field_path(tdir, f) is None]
    cl[4] = ("PASS all of " + " ".join(REQUIRED_FIELDS)) if not missing \
        else "FAIL missing " + " ".join(missing)
    ok = ok and not missing

    # clause 6 -- the AGE GUARD.
    #
    # IT PRINTS THE NUMBER OF FIELDS IT ACTUALLY COMPARED, AND A COMPARISON OVER
    # ZERO FIELDS IS REPORTED AS `VACUOUS`, NEVER AS `PASS`.  K0eR2 found this
    # the hard way (K0eR2_RESULTS.md section 2.3): with no endTime directory
    # every field_path returns None, the `older` list is EMPTY, and the clause
    # reported PASS over an empty set.  Clause 4 fails on the same missing
    # fields so the guard was never load-bearing alone -- but a future reader
    # leaning on clause 6 as an independent check must be told.
    if not os.path.isfile(zero_t):
        cl[6] = "FAIL no 0/T -- the age guard has no datum"
        ok = False
    else:
        t0 = os.path.getmtime(zero_t)
        present = [f for f in REQUIRED_FIELDS if field_path(tdir, f)]
        older = [f for f in present
                 if os.path.getmtime(field_path(tdir, f)) <= t0]
        if not present:
            cl[6] = ("VACUOUS compared 0 fields against 0/T -- NOT a pass.  No "
                     "endTime field exists to date, so the age guard has "
                     "nothing to say; see clause 4.")
            ok = False
        elif older:
            cl[6] = (f"FAIL compared {len(present)} field(s); not newer than "
                     f"0/T: " + " ".join(older))
            ok = False
        else:
            cl[6] = (f"PASS compared {len(present)} field(s), every one newer "
                     f"than 0/T")
    return ok, cl


# ---------------------------------------------------------------------------
# M4b / M4 / D0 / D2 -- the ULP comparisons, on PROCESSOR-LOCAL fields.
# ---------------------------------------------------------------------------
def ulp_compare_U(case_a, case_b, label_a, label_b, end_a, end_b):
    procs_a = sorted(d for d in os.listdir(case_a) if re.fullmatch(r"processor\d+", d))
    procs_b = sorted(d for d in os.listdir(case_b) if re.fullmatch(r"processor\d+", d))
    if not procs_a or procs_a != procs_b:
        refuse(f"processor sets differ: {label_a} has {procs_a}, {label_b} has "
               f"{procs_b}.  A cell-for-cell comparison across two different "
               f"decompositions is meaningless, and the registration fixes the "
               f"decomposition as COPIED rather than re-derived.")
    worst, worst_where, n_cells, n_nonzero = 0, None, 0, 0
    worst_abs, worst_pair = 0.0, (None, None)
    for p in procs_a:
        pa = field_path(os.path.join(case_a, p, str(end_a)), "U")
        pb = field_path(os.path.join(case_b, p, str(end_b)), "U")
        if pa is None or pb is None:
            refuse(f"{p}: U missing at endTime in "
                   f"{label_a if pa is None else label_b}")
        ua, ub = read_vector_field(pa), read_vector_field(pb)
        if len(ua) != len(ub):
            refuse(f"{p}: cell counts differ, {len(ua)} vs {len(ub)}")
        n_cells += len(ua)
        for i, (va, vb) in enumerate(zip(ua, ub)):
            for c in range(3):
                d = ulp_distance(va[c], vb[c])
                if d:
                    n_nonzero += 1
                    if d > worst:
                        worst, worst_where = d, (p, i, "xyz"[c])
                        worst_abs = abs(va[c] - vb[c])
                        worst_pair = (va[c], vb[c])
    return dict(worst_ulp=worst, where=worst_where, cells=n_cells,
                components_nonzero=n_nonzero, worst_abs=worst_abs,
                worst_pair=worst_pair)


# ---------------------------------------------------------------------------
# THE REPORTED PHYSICS ROWS.
# ---------------------------------------------------------------------------
def eq1_stanton(re_x, t_wall):
    return (EQ1_COEFF * (re_x ** EQ1_RE_EXP)
            * ((PR * t_wall / T_INF) ** EQ1_PRTW_EXP))


def assert_orthogonal_or_refuse(case):
    """The wall gradient below is (value_face - value_owner)/d, EXACT only on an
    orthogonal mesh.  The evidence is checkMesh's MEASUREMENT, carried with the
    mesh in the case's own birth certificate, and NOT a re-derivation from two
    rounded coordinates."""
    bc_path = os.path.join(case, "constant", "birth_certificate.json")
    if not os.path.isfile(bc_path):
        refuse(f"{bc_path} missing: this reader treats the wall gradient as a "
               f"pure y-difference, which is exact only on an orthogonal mesh, "
               f"and it will not assume orthogonality it has not read.")
    with open(bc_path) as fh:
        bc = json.load(fh)
    if "max_non_orthogonality" not in bc:
        refuse(f"{bc_path} carries no max_non_orthogonality field")
    if float(bc["max_non_orthogonality"]) != 0.0:
        refuse(f"{bc_path} reports max_non_orthogonality "
               f"{bc['max_non_orthogonality']}, not 0.  The wall gradient is "
               f"(value_face - value_owner)/d, which is EXACT only at zero "
               f"non-orthogonality; refusing rather than reporting a wall flux "
               f"built on a correction this reader does not apply.")
    return bc


# ONE unit in the 10th significant digit, from `writePrecision 10`, doubled as
# margin.  DERIVED from the write format, not a chosen epsilon: the two
# coordinates are rounded INDEPENDENTLY and can round in opposite directions.
#
# THE CHECK KEEPS ITS DISCRIMINATING POWER, and this was MEASURED rather than
# argued: the worst |x_cell - x_face| over all 208 plate faces is 1.000000e-09
# (pure round-off), while the SMALLEST plate cell spacing is 4.493756e-04 m -- a
# genuinely misaligned face would show a difference of order that spacing, FIVE
# ORDERS OF MAGNITUDE above this bound.  The bound sits in the gap, not near
# either edge.  IT IS NOT A GRADING TOLERANCE: no graded row divides by it and
# no verdict compares against it.
WRITE_PRECISION_BOUND = 2e-9


def wall_rows(case, end_time, t_wall, dt):
    """Per-plate-face wall quantities, from the reconstructed endTime fields.

    THIS IS THE PRODUCTION WALL-HEAT-FLUX READER.  Z1, Z2 and Z3 exercise THIS
    function -- the one the graded rows call -- and not a copy of it."""
    tdir = os.path.join(case, str(end_time))
    n_faces, start_face = read_boundary_patch(case, PLATE_PATCH)
    owner = read_labelled_list(os.path.join(case, "constant", "polyMesh", "owner"))
    c_path = field_path(tdir, "C")
    if c_path is None:
        refuse(f"{tdir}/C missing -- the launcher's writeCellCentres step did "
               f"not run, so no wall distance can be measured.  Refusing rather "
               f"than inferring a spacing from the blockMeshDict.")
    cc = read_vector_field(c_path)
    fc = read_patch_values(c_path, PLATE_PATCH, True, n_faces)
    u_path = field_path(tdir, "U")
    Uc = read_vector_field(u_path) if u_path else None
    # T and alphat are ABSENT from the simpleFoam reference by construction --
    # it solves no energy equation.  The thermal columns are then UNMEASURED
    # rather than zero, and only Cf is produced.  A reader that substituted
    # zeros here would MANUFACTURE a wall heat flux for a case that has none.
    t_path, at_path = field_path(tdir, "T"), field_path(tdir, "alphat")
    thermal = t_path is not None and at_path is not None
    if thermal:
        Tc = read_scalar_field(t_path)
        Tw = read_patch_values(t_path, PLATE_PATCH, False, n_faces)
        at_w = read_patch_values(at_path, PLATE_PATCH, False, n_faces)

    assert_orthogonal_or_refuse(case)

    rows = []
    for i in range(n_faces):
        o = owner[start_face + i]
        xf, yf, _ = fc[i]
        xc, yc, _ = cc[o]
        if abs(xc - xf) > WRITE_PRECISION_BOUND * max(1.0, abs(xf), abs(xc)):
            refuse(f"plate face {i}: owner cell centre x {xc!r} differs from "
                   f"face centre x {xf!r} by more than the written precision "
                   f"can explain.  The wall-normal direction is not +y for this "
                   f"face; refusing rather than projecting on an assumed normal.")
        d = abs(yc - yf)
        if d <= 0.0:
            refuse(f"plate face {i}: zero wall distance")
        re_x = U_INF * xf / NU
        row = dict(i=i, owner=o, x=xf, re_x=re_x, d=d, Cf=None, T_cell=None,
                   T_wall=None, alphat_wall=None, alpha_eff_wall=None,
                   q_kinematic=None, St=None, St_state=None, St_eq1=None)
        if Uc is not None:
            tau_k = NU * (Uc[o][0] - 0.0) / d              # m2/s2, kinematic
            row["Cf"] = 2.0 * tau_k / (U_INF ** 2)
        if thermal:
            alpha_eff_w = NU / PR + at_w[i]
            q_k = alpha_eff_w * (Tw[i] - Tc[o]) / d        # K m/s, kinematic
            # THE D-J1 CLAUSE, THROUGH THE SHARED HELPER.  St = q/(U dT) is
            # UNDEFINED at dT = 0, not small -- and the predecessor gate spec
            # said so in words ("the Stanton number undefined rather than
            # small") before this rung had a helper to say it in code.
            st, st_state, _why = guarded_div(q_k, U_INF * dt,
                                             f"St at plate face {i}")
            row.update(T_cell=Tc[o], T_wall=Tw[i], alphat_wall=at_w[i],
                       alpha_eff_wall=alpha_eff_w, q_kinematic=q_k,
                       St=st, St_state=st_state,
                       St_eq1=eq1_stanton(re_x, t_wall) if re_x > 0 else None)
        rows.append(row)
    return rows


def nearest_station(rows, re_target):
    return min((r for r in rows if r["re_x"] > 0),
               key=lambda r: abs(r["re_x"] - re_target))


def prt_eff(case, end_time):
    """M3.  Prt_eff = nut / alphat.

    WHAT A DEPARTURE FROM 0.85 HERE ACTUALLY MEASURES, AND IT IS NOT PHYSICS.
    `buoyantBoussinesqSimpleFoam` sets `alphat = nut/Prt` in TEqn.H and then
    updates `nut` in `turbulence->correct()` LATER IN THE SAME OUTER ITERATION,
    so the two written fields are ONE TURBULENCE CORRECTION APART.  Any spread
    is the residual change in `nut` over one outer iteration -- a CONVERGENCE
    diagnostic -- never a physical variation of the turbulent Prandtl number,
    which is a constant in this solver.

    THE DENOMINATOR CAN BE EXACTLY ZERO: alphat_wall = 0 by construction on a
    wall-resolved plate.  Those cells are EXCLUDED and their COUNT IS PRINTED;
    if every cell is excluded the row is NOT A RESULT, never 0.0."""
    tdir = os.path.join(case, str(end_time))
    nut = read_scalar_field(field_path(tdir, "nut"))
    at = read_scalar_field(field_path(tdir, "alphat"))
    if len(nut) != len(at):
        refuse("nut and alphat have different cell counts")
    vals, excluded, _reasons = guarded_series(zip(nut, at), "Prt_eff")
    if not vals:
        return dict(cells=len(nut), zero_alphat=excluded, state=NOT_A_RESULT,
                    why="every cell has alphat == 0, so Prt_eff is UNDEFINED "
                        "everywhere.  NOT A RESULT, never 0.0.",
                    min=None, max=None, mean=None, exactly_0p85=0,
                    max_dev_from_prt=None)
    exact = sum(1 for v in vals if ulp_distance(v, PRT) == 0)
    return dict(cells=len(nut), zero_alphat=excluded, state=REPORTED, why=None,
                min=min(vals), max=max(vals), mean=sum(vals) / len(vals),
                exactly_0p85=exact, spread=max(vals) - min(vals),
                max_dev_from_prt=max(abs(v - PRT) for v in vals))


def thermal_bl(case, end_time, station):
    """M5.  Thermal boundary-layer thickness at one station, plus the near-wall
    alphat profile.  The column is the set of cells sharing the station's x."""
    tdir = os.path.join(case, str(end_time))
    cc = read_vector_field(field_path(tdir, "C"))
    T = read_scalar_field(field_path(tdir, "T"))
    at = read_scalar_field(field_path(tdir, "alphat"))
    xs = station["x"]
    col = [(cc[i][1], T[i], at[i]) for i in range(len(cc))
           if abs(cc[i][0] - xs) <= 1e-9 * max(1.0, abs(xs))]
    col.sort()
    if len(col) < 5:
        return dict(x=xs, column_cells=len(col), delta_T_99=None,
                    near_wall_alphat=[])
    tw = station["T_wall"]
    # (tw - T_INF) is a denominator.  It is +10 or -10 on the registered arms
    # and can only be zero on an arm this registration does not define; the
    # shared guard is used rather than a local `if`.
    delta = None
    for y, t, _ in col:
        ratio, state, _why = guarded_div(t - T_INF, tw - T_INF,
                                         "thermal BL normalised excess")
        if state == NOT_A_RESULT:
            return dict(x=xs, column_cells=len(col), delta_T_99=None,
                        near_wall_alphat=[(y, a) for y, _, a in col[:8]],
                        note="T_wall == T_inf, so a thermal thickness is "
                             "UNDEFINED rather than zero.  NOT A RESULT.")
        if abs(ratio) <= 0.01:
            delta = y
            break
    return dict(x=xs, column_cells=len(col), delta_T_99=delta,
                near_wall_alphat=[(y, a) for y, _, a in col[:8]])


# ---------------------------------------------------------------------------
# THE PLANTS (standing rule 3).  Each writes a KNOWN perturbation INTO A FIELD
# FILE ON DISK, at a LINE INDEX, and reads it back through the production reader
# the graded path calls.
# ---------------------------------------------------------------------------
def _write_lines_atomic(dst, lines):
    """Write via a temp file and os.replace.  os.replace swings the DIRECTORY
    ENTRY and never writes through an existing inode, so a destination that
    happens to be a hard link to a run artifact cannot be truncated."""
    tmp = dst + ".ptmp"
    with open(tmp, "w") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, dst)


def plant_into_scalar_copy(src, dst, cell_index, value):
    _refuse_if_same_inode(src, dst, "scalar plant")
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: a plant by line index requires a nonuniform "
               f"internalField; a uniform field has no per-cell line to target")
    if not (0 <= cell_index < info["count"]):
        refuse(f"{src}: plant index {cell_index} outside 0..{info['count'] - 1}")
    li = info["first_value_line"] + cell_index
    lines[li] = repr(float(value))
    _write_lines_atomic(dst, lines)
    return li


def plant_into_vector_copy(src, dst, cell_index, x_value):
    _refuse_if_same_inode(src, dst, "vector plant")
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: P2 requires a nonuniform internalField")
    if not (0 <= cell_index < info["count"]):
        refuse(f"{src}: plant index {cell_index} outside 0..{info['count'] - 1}")
    li = info["first_value_line"] + cell_index
    old = _parse_vector(lines[li])
    lines[li] = f"({float(x_value)!r} {old[1]!r} {old[2]!r})"
    _write_lines_atomic(dst, lines)
    return li


def run_planted_controls(tdir, scratch, cell_index=0):
    """P1, P2, P3.  EXITS 2 if P1 or P2 is unseen, or if P3 fires."""
    os.makedirs(scratch, exist_ok=True)
    t_src, u_src = field_path(tdir, "T"), field_path(tdir, "U")
    if t_src is None:
        refuse(f"{tdir}: no T field, so P1 and P3 cannot be planted.  A "
               f"comparator that skips its planted control is not evidence.")
    if u_src is None:
        refuse(f"{tdir}: no U field, so P2 cannot be planted")

    base_t = read_scalar_field(t_src)
    base_u = read_vector_field(u_src)
    rec = {}

    # P1 -- scalar plant, must be SEEN
    d1 = os.path.join(scratch, "P1_T")
    li1 = plant_into_scalar_copy(t_src, d1, cell_index, PLANT_T)
    got = read_scalar_field(d1)[cell_index]
    if ulp_distance(got, PLANT_T) != 0:
        refuse(f"P1 UNSEEN: planted {PLANT_T!r} K into {t_src} at line {li1} "
               f"(cell {cell_index}) and the production scalar reader read back "
               f"{got!r}.  A zero from a reader not shown able to see a non-zero "
               f"is not evidence.")
    rec["P1"] = dict(line=li1, planted=PLANT_T, read_back=got, seen=True)

    # P2 -- VECTOR plant, must be SEEN.  A scalar plant does not exercise this.
    d2 = os.path.join(scratch, "P2_U")
    li2 = plant_into_vector_copy(u_src, d2, cell_index, PLANT_U)
    gotv = read_vector_field(d2)[cell_index]
    if ulp_distance(gotv[0], PLANT_U) != 0:
        refuse(f"P2 UNSEEN: planted {PLANT_U!r} m/s into the x-component of "
               f"{u_src} at line {li2} and the production VECTOR reader read "
               f"back {gotv[0]!r}")
    rec["P2"] = dict(line=li2, planted=PLANT_U, read_back=gotv[0], seen=True)

    # P3 -- NEGATIVE control.  A plant of exactly zero must NOT read as a
    # perturbation.  If this fires, the reader is inventing signal.
    d3 = os.path.join(scratch, "P3_T")
    li3 = plant_into_scalar_copy(t_src, d3, cell_index, PLANT_ZERO)
    got3 = read_scalar_field(d3)[cell_index]
    if ulp_distance(got3, PLANT_ZERO) != 0:
        refuse(f"P3 FIRED: planted exactly 0.0 at line {li3} and the reader "
               f"read back {got3!r}.  The negative control says the reader is "
               f"not reading what is on disk.")
    rec["P3"] = dict(line=li3, planted=PLANT_ZERO, read_back=got3, fired=False)
    rec["background_T0"] = base_t[cell_index]
    rec["background_U0"] = base_u[cell_index]
    return rec


# ---------------------------------------------------------------------------
# Z1 / Z2 / Z3 -- JOB B, RE-HOMED.  The physical zero-heat-flux control, at ZERO
# SOLVER COMPUTE.  K0eR2 projected ~2696 core-min to produce a field whose exact
# value is known a priori; this constructs it and runs the SAME production
# wall-flux reader on it.
#
# WHAT THESE CANNOT DETECT, registered at K0eR3 section 5.4 and repeated here so
# a reader of the code sees it too:
#   B3  Z1 tests the reader's NULL case only.  A spurious flux that needs a
#       NON-UNIFORM near-wall T field to appear -- a wrong alphat wall value, a
#       wrong face-to-cell distance, a wrong sign on one patch -- does not fire
#       on an exactly uniform field.
#   B4  Z1's zero is a statement about the reader, the mesh and the flux
#       formula, NOT about the solver.  The dT = 0 solve is not performed at
#       all, so nothing here shows the solver would hold T at 300.
# ---------------------------------------------------------------------------
def _link_readonly(src, dst):
    """Hard-link a file the Z path only ever READS.  Never used for a file the
    Z path rewrites -- see _install_writable and the inode guard below."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        os.remove(dst)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _install_writable(src, dst):
    """Put `src`'s CONTENT at `dst` by writing a temp file and os.replace-ing
    the DIRECTORY ENTRY.

    THIS IS NOT FASTIDIOUSNESS.  `dst` sits inside a scratch case that was
    populated from the real run tree, and an in-place `open(dst, 'w')` on a path
    that is a HARD LINK to a run artifact TRUNCATES THE ARTIFACT.  os.replace
    swings the directory entry and never touches the original inode, so the
    graded run's own fields cannot be damaged by a control that exists to
    protect them."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + ".ztmp"
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)


def _refuse_if_same_inode(a, b, what):
    """A writer must never be handed a destination that IS its source."""
    try:
        sa, sb = os.stat(a), os.stat(b)
    except OSError:
        return
    if (sa.st_dev, sa.st_ino) == (sb.st_dev, sb.st_ino):
        refuse(f"{what}: {a} and {b} are the SAME FILE (device {sa.st_dev}, "
               f"inode {sa.st_ino}).  Writing through that path would mutate "
               f"the source -- and where the source is a run artifact, would "
               f"destroy the evidence this control exists to protect.  "
               f"Refusing.")


def build_z_case(src_case, end_time, dst_case):
    """A scratch case carrying exactly what the production wall-flux reader
    opens: the plate patch definition, the owner list, the birth certificate,
    and the endTime C / U / T / alphat fields.

    C, U, alphat and the mesh files are READ-ONLY here and are hard-linked.
    T IS COPIED, NEVER LINKED, because the Z controls rewrite it."""
    if os.path.isdir(dst_case):
        shutil.rmtree(dst_case)
    for rel in (os.path.join("constant", "polyMesh", "boundary"),
                os.path.join("constant", "polyMesh", "owner"),
                os.path.join("constant", "birth_certificate.json")):
        src = os.path.join(src_case, rel)
        if not os.path.isfile(src):
            refuse(f"{src} missing; the Z controls cannot be constructed "
                   f"without the file the production reader opens.")
        _link_readonly(src, os.path.join(dst_case, rel))
    for f in ("C", "U", "alphat"):
        src = field_path(os.path.join(src_case, str(end_time)), f)
        if src is None:
            refuse(f"{src_case}/{end_time}/{f} missing; the Z controls cannot "
                   f"be constructed.")
        _link_readonly(src, os.path.join(dst_case, str(end_time), f))
    t_src = field_path(os.path.join(src_case, str(end_time)), "T")
    if t_src is None:
        refuse(f"{src_case}/{end_time}/T missing; the Z controls cannot be "
               f"constructed.")
    t_dst = os.path.join(dst_case, str(end_time), "T")
    os.makedirs(os.path.dirname(t_dst), exist_ok=True)
    shutil.copyfile(t_src, t_dst)
    _refuse_if_same_inode(t_src, t_dst, "build_z_case T")
    return dst_case


def write_exact_uniform_T(src, dst, value):
    """Overwrite EVERY internal value and the plate patch value with `value`,
    BY LINE INDEX, leaving every other line of the file byte-unchanged.  The
    internal field stays NONUNIFORM so the Z2/Z3 plants have a per-cell line to
    target and so the reader path is identical to the graded one."""
    _refuse_if_same_inode(src, dst, "write_exact_uniform_T")
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: Z1 requires a nonuniform internalField to construct "
               f"from; refusing rather than rewriting a field whose layout the "
               f"graded reader does not use.")
    tok = repr(float(value))
    for k in range(info["count"]):
        lines[info["first_value_line"] + k] = tok
    # the plate patch value, by line index, in the SAME in-memory buffer -- the
    # file is written ONCE, so a reader can never observe a half-built control.
    vline = None
    depth, started = 0, False
    for j in range(len(lines)):
        s = lines[j].strip()
        if not started:
            if s == PLATE_PATCH:
                started = True
            continue
        if s == "{":
            depth += 1
        elif s == "}":
            depth -= 1
            if depth == 0:
                break
        elif s.startswith("value"):
            vline = j
            break
    if vline is None:
        refuse(f"{src}: the {PLATE_PATCH!r} patch carries no `value` entry, so "
               f"Z1 cannot set the wall temperature; refusing rather than "
               f"leaving the wall at its solved value while the internal field "
               f"reads {value}.")
    m = re.match(r"(\s*value\s+uniform\s+)([0-9.eE+-]+)(\s*;\s*)$", lines[vline])
    if not m:
        refuse(f"{src}: the {PLATE_PATCH!r} patch `value` line is "
               f"{lines[vline]!r}, which Z1 cannot rewrite as a uniform scalar; "
               f"refusing.")
    lines[vline] = f"{m.group(1)}{tok};"
    tmp = dst + ".ztmp"
    with open(tmp, "w") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, dst)
    # read BACK from disk through the production readers, and refuse if the
    # construction did not land.  A control built by a writer nobody checked is
    # not a control.
    back_int = read_scalar_field(dst)
    if len(back_int) != info["count"]:
        refuse(f"{dst}: read back {len(back_int)} internal values, expected "
               f"{info['count']}")
    bad = [i for i, v in enumerate(back_int) if ulp_distance(v, value) != 0]
    if bad:
        refuse(f"{dst}: {len(bad)} internal value(s) did not land at {value!r}; "
               f"first at cell {bad[0]} reading {back_int[bad[0]]!r}")
    return info, vline


def run_z_controls(src_case, end_time, scratch):
    """Z1 (the null), Z2 (the positive plant), Z3 (the over-inclusion negative).

    Z2 AND Z3 REFUSE (exit 2).  Z1's non-zero is the REGISTERED verdict
    NOT A RESULT and is returned to the caller, which stops grading there --
    it never degrades into a warning and never lets a downstream row be
    reported as sound."""
    os.makedirs(scratch, exist_ok=True)
    n_faces, start_face = read_boundary_patch(src_case, PLATE_PATCH)
    owner = read_labelled_list(
        os.path.join(src_case, "constant", "polyMesh", "owner"))
    plate_owners = set(owner[start_face:start_face + n_faces])

    # ---- Z1: the constructed exact uniform-300 field -----------------------
    z_case = build_z_case(src_case, end_time, os.path.join(scratch, "Z_case"))
    t_case = os.path.join(z_case, str(end_time), "T")
    t_src = field_path(os.path.join(src_case, str(end_time)), "T")
    # THE PRISTINE Z1 FIELD IS KEPT OUTSIDE THE CASE and every plant is made
    # FROM IT.  Planting from the case file would stack Z3's plant on top of
    # Z2's, so Z3 would fire on Z2's perturbation and report an over-inclusive
    # reader that is nothing of the kind -- a false refusal on a sound
    # instrument.  The pristine copy is what makes Z2 and Z3 independent.
    t_pristine = os.path.join(scratch, "Z1_T_pristine")
    info, vline = write_exact_uniform_T(t_src, t_pristine, Z_BACKGROUND)
    _install_writable(t_pristine, t_case)

    rows1 = wall_rows(z_case, end_time, ARM_T_WALL[GRADED_ARM],
                      ARM_DT[GRADED_ARM])
    if len(rows1) != n_faces:
        refuse(f"Z1: wall reader returned {len(rows1)} rows for {n_faces} plate "
               f"faces")
    nonzero = [(r["i"], r["q_kinematic"]) for r in rows1
               if ulp_distance(r["q_kinematic"], 0.0) != 0]
    z1 = dict(faces=n_faces, nonzero=nonzero, cells=info["count"],
              plate_value_line_1based=vline + 1,
              passed=(not nonzero))
    if not z1["passed"]:
        # FAIL CLOSED.  A reader that manufactures flux on a field whose exact
        # flux is zero cannot be interrogated further: Z2 exists to validate a
        # ZERO that Z1 did not produce, and Z3 would fire on the manufactured
        # flux rather than on over-inclusion, which would misattribute the
        # defect.  Z2 and Z3 are returned as NOT REACHED and are NOT reported
        # as passing.
        return z1, dict(state=NOT_REACHED), dict(state=NOT_REACHED)

    # ---- Z2: the POSITIVE plant, at a NAMED plate face ---------------------
    # The registered face is the plate face of smallest x; its index, its owner
    # cell and the planted line are all printed so the control is reproducible.
    face_z2 = min(range(n_faces), key=lambda i: rows1[i]["x"])
    owner_z2 = owner[start_face + face_z2]
    t_z2 = os.path.join(scratch, "Z2_T")
    li2 = plant_into_scalar_copy(t_pristine, t_z2, owner_z2,
                                 Z_BACKGROUND + PLANT_T)
    _install_writable(t_z2, t_case)
    rows2 = wall_rows(z_case, end_time, ARM_T_WALL[GRADED_ARM],
                      ARM_DT[GRADED_ARM])
    q2 = rows2[face_z2]["q_kinematic"]
    if ulp_distance(q2, 0.0) == 0:
        refuse(f"Z2 UNSEEN: planted {PLANT_T!r} K into cell {owner_z2} -- the "
               f"owner of plate face {face_z2} (x = {rows1[face_z2]['x']!r}) -- "
               f"at line {li2} of the constructed field, and the PRODUCTION "
               f"WALL-FLUX READER still reports exactly zero flux on that face. "
               f"A zero from a reader not shown able to see a non-zero is not "
               f"evidence, so Z1's zero above means nothing.  Refusing.")
    z2 = dict(face=face_z2, owner_cell=owner_z2, line=li2, planted=PLANT_T,
              q_read=q2, x=rows1[face_z2]["x"], seen=True)

    # ---- Z3: the OVER-INCLUSION negative control ---------------------------
    # A reader can be wrong in TWO directions -- blind, or reading cells it has
    # no business reading -- and only this limb tests the second.  IT IS A
    # REFUSAL, NOT A WARNING.
    interior = next((c for c in range(info["count"]) if c not in plate_owners),
                    None)
    if interior is None:
        refuse("Z3: every cell in the field owns a plate face, so no interior "
               "cell exists to plant into; the over-inclusion control cannot be "
               "constructed and its absence is not a pass.")
    t_z3 = os.path.join(scratch, "Z3_T")
    li3 = plant_into_scalar_copy(t_pristine, t_z3, interior,
                                 Z_BACKGROUND + PLANT_T)
    _install_writable(t_z3, t_case)
    rows3 = wall_rows(z_case, end_time, ARM_T_WALL[GRADED_ARM],
                      ARM_DT[GRADED_ARM])
    fired = [(r["i"], r["q_kinematic"]) for r in rows3
             if ulp_distance(r["q_kinematic"], 0.0) != 0]
    if fired:
        refuse(f"Z3 FIRED: planted {PLANT_T!r} K into interior cell {interior} "
               f"at line {li3} -- a cell that owns NO plate face -- and the "
               f"plate wall-flux reader moved on {len(fired)} face(s), first "
               f"face {fired[0][0]} reading {fired[0][1]!r}.  The reader is "
               f"reading cells it has no business reading, so Z1's zero is "
               f"meaningless in the other direction.  Refusing.")
    z3 = dict(cell=interior, line=li3, planted=PLANT_T, fired=False,
              faces_checked=n_faces)
    return z1, z2, z3


# ---------------------------------------------------------------------------
def analyse(root, reference, scratch, prereg, expect_sha, k0er2_root=None):
    sha = own_blob_sha()
    if not os.path.isfile(prereg):
        refuse(f"--prereg {prereg} does not exist.  This grader prints the "
               f"registration path it was GIVEN rather than a hard-coded one "
               f"(K0eR2's grader printed the predecessor's), and it will not "
               f"print a path it cannot see on disk.")
    print("=" * 78)
    print("K0eR3 -- forced-convection flat plate, campaign F14 cooling ladder")
    print(f"prereg (AS GIVEN, not hard-coded): {prereg}")
    print(f"this file's GIT BLOB SHA-1 (sha1 of b'blob <len>\\0' + content): {sha}")
    print("=" * 78)
    if expect_sha != sha:
        refuse(f"GRADER PIN MISMATCH: this file's git blob sha1 is {sha}; the "
               f"committed blob was given as {expect_sha}.  The grading path is "
               f"fixed at the pre-registration commit (standing rule 2) and this "
               f"is not that file.  NOTE THE HASH FUNCTION: git blob sha1, not "
               f"sha256 and not a plain sha1 of the bytes.")

    # ---- D0: THE DETERMINISM REFUSAL GATE, BEFORE EVERYTHING ELSE ---------
    print("\n--- D0  DETERMINISM TWIN (refusal gate, armed BEFORE the arms) ---")
    print("  Two invocations of the SAME case at 200 iterations.  A non-zero")
    print("  M4b arising from solver nondeterminism would be a FALSE GATE FAIL,")
    print("  and this finds it for ~7 core-min instead of ~190.")
    d0_cases = [os.path.join(root, a) for a in D0_TWINS]
    if not all(os.path.isdir(c) for c in d0_cases):
        missing = [a for a, c in zip(D0_TWINS, d0_cases) if not os.path.isdir(c)]
        print(f"  D0       {NOT_A_RESULT}   twin case(s) absent: {' '.join(missing)}")
        print(f"\nRUNG K0eR3 {NOT_A_RESULT}.  D0 could not be measured, so the")
        print("           0-ULP design is unverified on this box and the main")
        print("           arms are not graded.")
        return EXIT_FAIL
    d0_ends = [end_time_of(c) for c in d0_cases]
    for a, e in zip(D0_TWINS, d0_ends):
        if e != END_TIME_D0:
            refuse(f"{a} carries endTime {e}; the registration fixes "
                   f"{END_TIME_D0} for the determinism twins.")
    d0_done, d0_cl = {}, {}
    for a, e in zip(D0_TWINS, d0_ends):
        d0_done[a], d0_cl[a] = completion(root, a, e)
        print(f"  {a}: {'DONE' if d0_done[a] else 'NOT DONE'}")
        for i in sorted(d0_cl[a]):
            print(f"      clause {i}: {d0_cl[a][i]}")
    if not all(d0_done.values()):
        print(f"\n  D0       {NOT_A_RESULT}   a twin did not complete")
        print(f"\nRUNG K0eR3 {NOT_A_RESULT}.  D0 could not be measured.")
        return EXIT_FAIL
    d0 = ulp_compare_U(d0_cases[0], d0_cases[1], D0_TWINS[0], D0_TWINS[1],
                       d0_ends[0], d0_ends[1])
    print(f"  cells compared             {d0['cells']} x 3 components")
    print(f"  components at non-zero ULP {d0['components_nonzero']}")
    print(f"  worst ULP distance         {d0['worst_ulp']}")
    if d0["worst_ulp"]:
        print(f"  worst at                   {d0['where']}   "
              f"|diff| {d0['worst_abs']:.6e} m/s")
        print(f"  D0       {NOT_A_RESULT}")
        print(f"\nRUNG K0eR3 {NOT_A_RESULT}.  THE SOLVER IS NOT BIT-REPRODUCIBLE")
        print("           ACROSS INVOCATIONS at this decomposition, so a 0-ULP")
        print("           gate cannot distinguish a beta/g leak from run-to-run")
        print("           nondeterminism.  The M4b design is VOID on this box")
        print("           and the main arms are not graded against it.")
        return EXIT_FAIL
    print(f"  D0       {PASS}  (0 ULP)")

    # ---- P7: THE PREMISE REFUSAL -----------------------------------------
    print("\n--- P7  THE PREMISE (blocking refusal, not an expectation) ---")
    case_g = os.path.join(root, GRADED_ARM)
    case_c = os.path.join(root, CONTROL_ARM)
    for a, c in ((GRADED_ARM, case_g), (CONTROL_ARM, case_c)):
        if not os.path.isdir(c):
            refuse(f"{c} does not exist; the arm {a} was never built.")
    p7 = premise_diff_or_refuse(case_g, case_c, GRADED_ARM, CONTROL_ARM)
    print(f"  files compared over {list(PREMISE_DIFF_SCOPE)}: {p7['files_compared']}")
    print(f"  differing files            1  ({p7['differing_file']})")
    print(f"  differing lines            1  at 1-based {p7['line_1based']}"
          f"  (registration records {p7['line_1based_expected']})")
    print(f"  plate T_wall               {GRADED_ARM} {p7['t_wall_a']!r}  "
          f"{CONTROL_ARM} {p7['t_wall_b']!r}")
    print(f"  P7       {PASS}")

    # ---- completion, both main arms --------------------------------------
    print("\n--- STRICT COMPLETION RULE (standing rule 4, all-or-nothing) ---")
    print("age-guard datum: <case>/0/T.  K0eR3 is SINGLE-REGION (one mesh, one")
    print("case, no regions), so 0/T is the correct dating file, and")
    print("launch_k0e.sh touches it LAST, immediately before the solver.")
    print("Clause 6 PRINTS the number of fields it compared; a comparison over")
    print("ZERO fields reports VACUOUS and is NOT a pass.")
    ends = {}
    done = {}
    for arm in MAIN_ARMS:
        e = end_time_of(os.path.join(root, arm))
        if e != END_TIME_ARMS:
            refuse(f"{arm} carries endTime {e}; the registration fixes "
                   f"{END_TIME_ARMS} for the main arms.")
        ends[arm] = e
        done[arm], cl = completion(root, arm, e)
        print(f"  {arm}: {'DONE' if done[arm] else 'NOT DONE'}")
        for i in sorted(cl):
            print(f"      clause {i}: {cl[i]}")

    if not all(done.values()):
        missing = [a for a in MAIN_ARMS if not done[a]]
        # K0eR2's plants were STRUCTURALLY UNREACHABLE on a NOT DONE arm and its
        # stdout carried no controls section at all, so a reader could not tell
        # they were owed.  This prints the section and says why it is empty.
        print("\n--- PLANTED CONTROLS (standing rule 3) ---")
        print(f"  P1 P2 P3 Z1 Z2 Z3   {NOT_REACHED}   the completion gate")
        print("      properly precedes the comparison, so there is nothing to")
        print("      plant into.  NO PLANTED-CONTROL EVIDENCE EXISTS FOR THIS")
        print("      GRADE AND NONE IS CLAIMED.")
        print(f"\n  M4b      {NOT_A_RESULT}   NOT DONE under the strict "
              f"completion rule: {' '.join(missing)}")
        print(f"\nRUNG K0eR3 {NOT_A_RESULT}.  A gated row that cannot be")
        print("           measured cannot yield a PASS.  The rows above stand")
        print("           as measurements and as NOTHING MORE.")
        return EXIT_FAIL

    tdir_g = os.path.join(case_g, str(ends[GRADED_ARM]))

    # ---- P1 / P2 / P3 -----------------------------------------------------
    print("\n--- P1 P2 P3  PLANTED CONTROLS ON THE ULP READERS (rule 3) ---")
    rec = run_planted_controls(tdir_g, os.path.join(scratch, "P"))
    print(f"  P1 scalar plant {PLANT_T!r} K  -> read back "
          f"{rec['P1']['read_back']!r} at line {rec['P1']['line']}   SEEN")
    print(f"  P2 VECTOR plant {PLANT_U!r} m/s (x) -> read back "
          f"{rec['P2']['read_back']!r} at line {rec['P2']['line']}   SEEN")
    print(f"  P3 negative control 0.0 -> read back {rec['P3']['read_back']!r}"
          f"   DID NOT FIRE")
    print(f"  live background: T {rec['background_T0']!r}  "
          f"U {rec['background_U0']!r}")

    # ---- Z1 / Z2 / Z3 -----------------------------------------------------
    print("\n--- Z1 Z2 Z3  THE ZERO-FLUX CONTROL, RE-HOMED (rule 3, K0eR3 5.1 C2)")
    print("  Job B at ZERO SOLVER COMPUTE.  K0eR2 projected ~2696 core-min to")
    print("  produce a field whose exact value is known a priori; this")
    print("  constructs it and runs the SAME production wall-flux reader.")
    z1, z2, z3 = run_z_controls(case_g, ends[GRADED_ARM],
                                os.path.join(scratch, "Z"))
    print(f"  Z1 constructed exact uniform {Z_BACKGROUND!r} K over "
          f"{z1['cells']} cells; plate value line 1-based "
          f"{z1['plate_value_line_1based']}")
    print(f"     plate faces read           {z1['faces']}")
    print(f"     faces at non-zero flux     {len(z1['nonzero'])}   "
          f"(threshold 0 ULP against 0.0, and there is NO tolerance constant)")
    if z1["passed"]:
        print(f"  Z2 positive plant {PLANT_T!r} K into cell {z2['owner_cell']}, "
              f"the owner of plate face {z2['face']} (x = {z2['x']!r}), line "
              f"{z2['line']}")
        print(f"     wall-flux reader moved to  {z2['q_read']!r} K m/s   SEEN")
        print(f"  Z3 plant {PLANT_T!r} K into INTERIOR cell {z3['cell']} (owns "
              f"no plate face), line {z3['line']}")
        print(f"     plate reader over {z3['faces_checked']} faces   DID NOT FIRE")
    else:
        print(f"  Z2 Z3    {NOT_REACHED}   Z1 failed, so the reader cannot be")
        print("           interrogated further: Z2 validates a zero Z1 did not")
        print("           produce, and Z3 would fire on the manufactured flux")
        print("           rather than on over-inclusion.  NEITHER IS A PASS.")
    if not z1["passed"]:
        for i, q in z1["nonzero"][:20]:
            print(f"     face {i:4d}   q = {q!r} K m/s   MANUFACTURED")
        if len(z1["nonzero"]) > 20:
            print(f"     ... and {len(z1['nonzero']) - 20} more")
        print(f"  Z1       {NOT_A_RESULT}")
        print(f"\nRUNG K0eR3 {NOT_A_RESULT}.  THE PRODUCTION WALL-FLUX READER")
        print("           MANUFACTURES A NON-ZERO HEAT FLUX ON A FIELD WHOSE")
        print("           EXACT FLUX IS ZERO.  Every Stanton figure this rung")
        print("           could report rests on that reader, so no measurement")
        print("           exists and none is reported below.")
        return EXIT_FAIL
    print(f"  Z1       {PASS}  (0 ULP against 0.0 on all {z1['faces']} faces)")

    # ---- M4b, THE GATED ROW ----------------------------------------------
    print("\n--- M4b  SAME-SOLVER NEUTRALISATION CONTROL, THE GATED ROW ---")
    print(f"  {GRADED_ARM} (plate 310 K, dT = +10) vs {CONTROL_ARM} (plate 290 K,")
    print("  dT = -10): the SAME binary and the SAME discrete operators,")
    print("  differing ONLY in the wall temperature (P7 above proves it).  The")
    print("  only T-to-U route in v2606 is rhok = 1 - beta*(T - TRef), which is")
    print("  LINEAR and therefore ODD, so this pair drives any leak at TWICE")
    print("  the amplitude of K0eR2's (0, +10) pair and with opposite sign.")
    print("  threshold: 0 ULP, every component of every cell, processor-local.")
    print("  There is no tolerance constant in this comparator.")
    print("  BLIND SPOT B1: a leak EVEN in (T - TRef) cancels exactly in this")
    print("  difference and is NOT detected.  Registered, not discovered.")
    m4b = ulp_compare_U(case_g, case_c, GRADED_ARM, CONTROL_ARM,
                        ends[GRADED_ARM], ends[CONTROL_ARM])
    print(f"  cells compared             {m4b['cells']} x 3 components")
    print(f"  components at non-zero ULP {m4b['components_nonzero']}")
    print(f"  worst ULP distance         {m4b['worst_ulp']}")
    m4b_pass = (m4b["worst_ulp"] == 0)
    if not m4b_pass:
        p, ci, comp = m4b["where"]
        print(f"  worst at                   processor {p}, cell {ci}, "
              f"component {comp}")
        print(f"  |diff|                     {m4b['worst_abs']:.6e} m/s")
        print(f"  the two values             {m4b['worst_pair'][0]!r}  "
              f"{m4b['worst_pair'][1]!r}")
    print(f"  M4b {PASS if m4b_pass else GATE_FAIL}")

    # ---- M4, REPORTED, NOT GATED -----------------------------------------
    print("\n--- M4  CROSS-SOLVER, REPORTED AND NOT GATED ---")
    print("  simpleFoam/UEqn.H solves UEqn == -fvc::grad(p) while")
    print("  buoyantBoussinesqSimpleFoam solves UEqn == fvc::reconstruct(...).")
    print("  Those are DIFFERENT DISCRETE OPERATORS and they differ")
    print("  INDEPENDENTLY of beta and g, so a non-zero M4 conflates 'beta/g")
    print("  leaked' with 'the operators are not identical'.  A row that cannot")
    print("  answer its own question is not gated.")
    m4 = None
    if os.path.isdir(reference):
        m4 = ulp_compare_U(case_g, reference, GRADED_ARM, "simpleFoam reference",
                           ends[GRADED_ARM], END_TIME_ARMS)
        print(f"  worst ULP distance         {m4['worst_ulp']}   {REPORTED}")
    else:
        print(f"  {UNMEASURED}: reference {reference} absent")

    # ---- D2, cross-epoch, REPORTED, NOT GATED ----------------------------
    print("\n--- D2  CROSS-EPOCH, REPORTED AND NOT GATED ---")
    d2 = None
    if k0er2_root and os.path.isdir(os.path.join(k0er2_root, GRADED_ARM)):
        d2 = ulp_compare_U(case_g, os.path.join(k0er2_root, GRADED_ARM),
                           GRADED_ARM, f"K0eR2 {GRADED_ARM}",
                           ends[GRADED_ARM], END_TIME_ARMS)
        print(f"  worst ULP distance         {d2['worst_ulp']}   {REPORTED}")
        print("  A non-zero here CANNOT separate solver nondeterminism from a")
        print("  change in the box between 2026-09-03 and now, so it is not")
        print("  gated.  It is why both arms were run FRESH.")
    else:
        print(f"  {UNMEASURED}: no --k0er2-root given, or the arm is absent")

    # ---- M1 / M1b / M2 / M3 / M5, REPORTED --------------------------------
    print("\n--- M1  STANTON vs eq. (1)   REPORTED, NO BAND (K0eR3 section 3) ---")
    rows = {a: wall_rows(os.path.join(root, a), ends[a], ARM_T_WALL[a],
                         ARM_DT[a]) for a in MAIN_ARMS}
    st_nar = 0
    for a in MAIN_ARMS:
        print(f"  {a}  (T_wall {ARM_T_WALL[a]} K, dT {ARM_DT[a]:+.1f} K)")
        for tgt in RE_X_STATIONS:
            r = nearest_station(rows[a], tgt)
            if r["St_state"] == NOT_A_RESULT or r["St"] is None:
                st_nar += 1
                print(f"    Re_x {tgt:9.3e}  actual {r['re_x']:11.5e}  "
                      f"St {NOT_A_RESULT}  (dT = 0 -> UNDEFINED, never 0.0)")
                continue
            dev, dstate, _w = guarded_div(r["St"] - r["St_eq1"], r["St_eq1"],
                                          f"M1 deviation at Re_x {tgt:.3e}")
            devs = f"{dev * 100.0:+8.3f} %" if dstate == REPORTED else NOT_A_RESULT
            print(f"    Re_x {tgt:9.3e}  actual {r['re_x']:11.5e}  "
                  f"St {r['St']:.6e}  eq1 {r['St_eq1']:.6e}  dev {devs}")
    print(f"  stations returned NOT A RESULT on an undefined St: {st_nar}")

    print("\n--- M1b  St(FP_T290) vs St(FP_T10) AT MATCHED Re_x   REPORTED ---")
    print("  The constant-property Boussinesq energy equation is EXACTLY LINEAR")
    print("  in (T - TRef) and at beta = 0 the momentum field is independent of")
    print("  T, so q scales linearly with dT and St is INDEPENDENT of dT and of")
    print("  its sign.  Eq. (1) instead predicts the cooled arm at 1.027036x the")
    print("  heated.  This row is impossible under K0eR2's design, whose control")
    print("  arm had no Stanton number at all.")
    m1b_nar = 0
    for tgt in RE_X_STATIONS:
        rg = nearest_station(rows[GRADED_ARM], tgt)
        rc_ = nearest_station(rows[CONTROL_ARM], tgt)
        if rg["St"] is None or rc_["St"] is None:
            m1b_nar += 1
            print(f"    Re_x {tgt:9.3e}   {NOT_A_RESULT}  (an arm's St is "
                  f"undefined)")
            continue
        rel, state, _w = guarded_div(abs(rc_["St"] - rg["St"]), rg["St"],
                                     f"M1b at Re_x {tgt:.3e}")
        if state == NOT_A_RESULT:
            m1b_nar += 1
            print(f"    Re_x {tgt:9.3e}   {NOT_A_RESULT}  (St(FP_T10) is "
                  f"exactly zero, so the ratio is UNDEFINED, never 0.0)")
            continue
        print(f"    Re_x {tgt:9.3e}   St290 {rc_['St']:.6e}  St310 "
              f"{rg['St']:.6e}  |rel| {rel:.3e}")
    print(f"  stations returned NOT A RESULT: {m1b_nar}")

    print("\n--- M2  Cf   REPORTED (control) ---")
    for tgt in RE_X_STATIONS:
        rg = nearest_station(rows[GRADED_ARM], tgt)
        print(f"    Re_x {tgt:9.3e}   Cf {rg['Cf']:.6e}")

    print("\n--- M3  Prt_eff = nut/alphat   REPORTED, A CONVERGENCE DIAGNOSTIC ---")
    for a in MAIN_ARMS:
        pe = prt_eff(os.path.join(root, a), ends[a])
        if pe["state"] == NOT_A_RESULT:
            print(f"    {a}   {NOT_A_RESULT}   {pe['why']}")
            continue
        print(f"    {a}   cells {pe['cells']}  EXCLUDED (alphat == 0) "
              f"{pe['zero_alphat']}  min {pe['min']:.6f}  max {pe['max']:.6f}  "
              f"max|dev from {PRT}| {pe['max_dev_from_prt']:.3e}  "
              f"exactly {PRT} in {pe['exactly_0p85']} cells")

    print("\n--- M5  THERMAL BL   REPORTED ---")
    for a in MAIN_ARMS:
        st = nearest_station(rows[a], RE_X_STATIONS[2])
        bl = thermal_bl(os.path.join(root, a), ends[a], st)
        print(f"    {a}   x {bl['x']:.6f}  column cells {bl['column_cells']}  "
              f"delta_T_99 {bl['delta_T_99']}"
              + (f"  note: {bl['note']}" if bl.get("note") else ""))

    # ---- rule 5 -----------------------------------------------------------
    print("\n--- STANDING RULE 5 (Roache triple gating) ---")
    print(f"  NO TRIPLE IS FORMED.  K0eR3 runs two arms on ONE mesh")
    print(f"  ({CELLS_REGISTERED} cells).  Rule 5 does not engage, NO GCI is")
    print("  computed and none is printed.  EVERY NUMBER ABOVE CARRIES NO")
    print("  DISCRETISATION BOUND AT ALL.")

    # ---- the rung verdict -------------------------------------------------
    print("\n" + "=" * 78)
    if m4b_pass:
        print(f"RUNG K0eR3 {PASS}  on M4b (0 ULP) and Z1 (0 flux, 0 ULP).  The")
        print("           momentum field is bit-identical between a plate 20 K")
        print("           apart in wall temperature, so beta and g ARE")
        print("           neutralised against an odd-mode perturbation, and a")
        print("           Stanton error on this rung is attributable to the")
        print("           thermal closure alone.  IT IS NOT A VALIDATION OF")
        print("           THAT CLOSURE -- see the registration section 2.1.3 on")
        print("           circularity -- and no band is armed on the")
        print("           correlation, so no GATE FAIL was reachable there.")
        print("           BLIND SPOTS B1..B7 of section 5.4 stand undischarged.")
        if m4 is not None:
            print(f"           M4 (cross-solver) reads {m4['worst_ulp']} ULP, REPORTED.")
        if d2 is not None:
            print(f"           D2 (cross-epoch) reads {d2['worst_ulp']} ULP, REPORTED.")
        print("=" * 78)
        return EXIT_PASS
    print(f"RUNG K0eR3 {GATE_FAIL}.  M4b is NON-ZERO: the momentum field MOVED")
    print("           when ONLY the wall temperature changed, on the same")
    print("           binary and the same discrete operators, with the premise")
    print("           proved by P7 and determinism proved by D0.  beta and g")
    print("           were therefore NOT neutralised, and the attribution of")
    print("           any Stanton error to the thermal closure is VOID.")
    print("           THIS IS A MEASURED FAILURE OF A THRESHOLD FROZEN BEFORE")
    print("           COMPUTE, AND IT IS REPORTED AS ONE.  The threshold was 0")
    print("           ULP and it is not widened.")
    print(f"           worst {m4b['worst_ulp']} ULP at {m4b['where']}, |diff| "
          f"{m4b['worst_abs']:.6e} m/s")
    print("           The reported rows above stand as measurements and as")
    print("           NOTHING MORE.")
    print("=" * 78)
    return EXIT_FAIL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True,
                    help="K0eR3_runs, holding FP_T10/, FP_T290/, D0_A/, D0_B/ "
                         "and STATUS.*")
    ap.add_argument("--reference", default=REFERENCE_DEFAULT)
    ap.add_argument("--scratch", required=True,
                    help="a scratch directory for the planted copies")
    ap.add_argument("--prereg", required=True,
                    help="the registration this grade runs under.  REQUIRED and "
                         "PRINTED AS GIVEN: K0eR2's grader hard-coded its "
                         "predecessor's path into the banner and a reader of "
                         "the verdict artifact alone would have attributed the "
                         "grade to the wrong document.")
    ap.add_argument("--expect-sha", required=True,
                    help="the committed GIT BLOB SHA-1 of this file.  Not a "
                         "sha256.  Not a plain sha1 of the bytes.  REQUIRED: "
                         "K0eR2's grader made this optional, so omitting it "
                         "silently DISARMED the pin.")
    ap.add_argument("--k0er2-root", default=None,
                    help="K0eR2_runs, for the REPORTED cross-epoch row D2")
    a = ap.parse_args()
    return analyse(a.root, a.reference, a.scratch, a.prereg, a.expect_sha,
                   a.k0er2_root)


if __name__ == "__main__":
    sys.exit(main())
