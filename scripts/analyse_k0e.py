#!/usr/bin/env python3
"""analyse_k0e.py -- THE FROZEN GRADING PATH FOR K0e.

Campaign F14 cooling ladder, rung K0e: the forced-convection flat plate against
Bahrami (2005), NASA/TM-2005-212841.  Registered by
`docs/campaigns/F14-cooling-ladder/K0e_PREREGISTRATION.md`, which is committed
in the SAME COMMIT as this file.

WHAT THIS FILE MAY AND MAY NOT PRODUCE
--------------------------------------
Exactly ONE row is GATED: **M4b**, the SAME-SOLVER neutralisation control --
`FP_T10` against `FP_T00`, the same binary at two wall temperatures.  Its
threshold is **0 ULP** and it is stated in ULP of the operands, never as a
hardcoded "equivalent" tolerance constant.  Any non-zero ULP distance is a hard
`NOT A RESULT` for the rung.

The gating reason, in the form Sanaa's 2026-09-03 20:00Z ruling requires:
  *Without M4b, the verdict on the Stanton attribution cannot be trusted, because
  a momentum field that moved when only the wall temperature changed means beta
  and g were not actually neutralised, and the attribution of any Stanton-number
  error to the thermal closure is void.*

**M4 -- the cross-solver comparison against the recorded `simpleFoam` field -- is
REPORTED, NOT GATED, and the reason is a source finding rather than a
preference.**  `simpleFoam/UEqn.H` solves `UEqn == -fvc::grad(p)` while
`buoyantBoussinesqSimpleFoam/UEqn.H` solves
`UEqn == fvc::reconstruct((-ghf*snGrad(rhok) - snGrad(p_rgh))*magSf)`.  Those are
DIFFERENT DISCRETE OPERATORS and they differ INDEPENDENTLY of beta and g, so a
non-zero M4 conflates "beta/g leaked" with "the two operators are not identical"
and cannot separate them.  A gate that cannot answer its own gating question is
not a gate.  M4b compares one binary with itself, so the operator confound
cancels exactly, and it IS a clean test of that question.

EVERY OTHER ROW IS REPORTED, NOT GATED -- the lab default since that ruling.
In particular the Stanton comparison against equation (1) carries **NO BAND**:
the pre-registration section 3 registers that no band can be honestly armed from
the source in hand.  **This rung therefore cannot GATE FAIL and cannot PASS on
the correlation.  Its reachable verdicts are PASS or NOT A RESULT on M4, with
everything else reported beside it.**

NO ROACHE TRIPLE IS FORMED.  K0e runs two arms on ONE mesh.  Standing rule 5
does not engage, no GCI is computed and none is printed -- quoting a GCI where
no triple exists would be inventing a convergence claim.

EXIT CODES
  0  the analysis ran and printed its rows
  2  REFUSAL -- a plant unseen, the negative control fired, a completion clause
     failed, a sha mismatch, or any reader that could not be trusted
"""

import argparse
import hashlib
import os
import re
import shutil
import struct
import sys

EXIT_OK, EXIT_REFUSE = 0, 2

# ---------------------------------------------------------------------------
# THE REGISTERED CONSTANTS.  Frozen with the pre-registration.
# ---------------------------------------------------------------------------
END_TIME = 9000
RANKS = 2
NU = 2e-07              # m2/s
PR = 0.71
PRT = 0.85
U_INF = 1.0             # m/s
T_INF = 300.0           # K
T_WALL_THERMAL = 310.0  # K, arm FP_T10
DT_THERMAL = 10.0       # K
ARMS = ("FP_T10", "FP_T00")
GRADED_ARM = "FP_T10"
CONTROL_ARM = "FP_T00"
PLATE_PATCH = "plate"
REFERENCE_DEFAULT = "/home/ubuntu/certonomous-runs/tmr-flatplate-finer"

# Bahrami eq. (1), as printed on line 353 of the .txt sidecar of
# docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf
#   St = 0.0296 Re^-0.2 (Pr Tw / T_inf)^-0.4
EQ1_COEFF = 0.0296
EQ1_RE_EXP = -0.2
EQ1_PRTW_EXP = -0.4

# The reported Stanton stations, fixed here BEFORE any K0e compute.
RE_X_STATIONS = (1.0e6, 2.0e6, 3.0e6, 5.0e6, 7.0e6, 1.0e7)

# Fields the strict completion rule requires present at endTime.
REQUIRED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

# The three registered plants (standing rule 3).
PLANT_T = 1.234e-03      # K, into a COPY of the graded arm's endTime T
PLANT_U = 1.234e-03      # m/s, into the X-COMPONENT of a COPY of its U
PLANT_ZERO = 0.0         # the NEGATIVE control: a plant of exactly zero

# rule 1 vocabulary, and NOTHING ELSE may be printed as a verdict
PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
# non-verdict row states, kept deliberately distinct from the vocabulary
REPORTED, UNMEASURED = "REPORTED", "UNMEASURED"


def refuse(msg):
    """REFUSE (exit 2) rather than degrade."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ---------------------------------------------------------------------------
# THE PIN.  own_blob_sha() is the GIT BLOB SHA-1 of this file:
#     sha1(b"blob " + str(len(content)) + b"\0" + content)
# IT IS NOT A SHA-256 AND IT IS NOT A PLAIN SHA-1 OF THE BYTES.  The
# pre-registration names the hash function beside the digit string for exactly
# this reason: a pin compared against the wrong digest is not a pin.
# ---------------------------------------------------------------------------
def own_blob_sha():
    with open(os.path.abspath(__file__), "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# ULP.  THE M4 THRESHOLD IS EXPRESSED HERE AND NOWHERE ELSE, AS AN INTEGER
# COUNT OF REPRESENTABLE DOUBLES BETWEEN THE TWO OPERANDS.  There is no
# tolerance constant in this file, and there must never be one: a hardcoded
# "equivalent" epsilon is a band nobody registered.
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
# being evidence.
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
    """PRODUCTION SCALAR READER.  P1 and P3 are read back through this."""
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
    """PRODUCTION VECTOR READER.  P2 is read back through this.  It is a
    SEPARATE parser from read_scalar_field, which is why P2 exists at all: a
    scalar plant does not exercise a vector reader."""
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


# ---------------------------------------------------------------------------
# THE THREE REGISTERED PLANTS (standing rule 3).  Each writes a KNOWN
# perturbation INTO A FIELD FILE ON DISK, at a LINE INDEX, and reads it back
# through the production reader the graded path calls.
# ---------------------------------------------------------------------------
def plant_into_scalar_copy(src, dst, cell_index, value):
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: P1/P3 require a nonuniform internalField to plant into "
               f"by line index; a uniform field has no per-cell line to target")
    if not (0 <= cell_index < info["count"]):
        refuse(f"{src}: plant index {cell_index} outside 0..{info['count'] - 1}")
    li = info["first_value_line"] + cell_index
    lines[li] = repr(float(value))
    open(dst, "w").write("\n".join(lines))
    return li


def plant_into_vector_copy(src, dst, cell_index, x_value):
    lines = _read_lines(src)
    info = locate_internal_field(lines)
    if info is None or info["mode"] != "nonuniform":
        refuse(f"{src}: P2 requires a nonuniform internalField to plant into")
    if not (0 <= cell_index < info["count"]):
        refuse(f"{src}: plant index {cell_index} outside 0..{info['count'] - 1}")
    li = info["first_value_line"] + cell_index
    old = _parse_vector(lines[li])
    lines[li] = f"({float(x_value)!r} {old[1]!r} {old[2]!r})"
    open(dst, "w").write("\n".join(lines))
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
# THE STRICT COMPLETION RULE (standing rule 4).  ALL-OR-NOTHING.
# The age-guard datum is the case's OWN `0/T`.  K0e is SINGLE-REGION -- one
# mesh, one case, no regions -- so `0/T` is the correct dating file here, and
# scripts/launch_k0e.sh touches it LAST, immediately before the solver, which
# is what makes it a valid datum rather than an assumed one.
# ---------------------------------------------------------------------------
def completion(root, arm):
    case = os.path.join(root, arm)
    status = os.path.join(root, f"STATUS.{arm}")
    log = os.path.join(case, "log.solve")
    tdir = os.path.join(case, str(END_TIME))
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
        loglines = []
    else:
        loglines = _read_lines(log)
        cl[2] = "PASS End line" if any(l.strip() == "End" for l in loglines) \
            else "FAIL no End line"
        times = [float(m.group(1)) for m in
                 (re.match(r"^Time = ([0-9.eE+-]+)$", l.strip()) for l in loglines)
                 if m]
        cl[3] = (f"PASS last time == endTime {END_TIME}"
                 if times and times[-1] == float(END_TIME)
                 else f"FAIL last time {times[-1] if times else None} != {END_TIME}")
        n_exec = sum(1 for l in loglines if l.startswith("ExecutionTime"))
        cl[5] = (f"PASS ExecutionTime count == {END_TIME}"
                 if n_exec == END_TIME
                 else f"FAIL ExecutionTime count {n_exec} != {END_TIME}")
        ok = ok and all(cl[i].startswith("PASS") for i in (2, 3, 5))

    missing = [f for f in REQUIRED_FIELDS if field_path(tdir, f) is None]
    cl[4] = ("PASS all of " + " ".join(REQUIRED_FIELDS)) if not missing \
        else "FAIL missing " + " ".join(missing)
    ok = ok and not missing

    # clause 6 -- the AGE GUARD.
    if not os.path.isfile(zero_t):
        cl[6] = "FAIL no 0/T -- the age guard has no datum"
        ok = False
    else:
        t0 = os.path.getmtime(zero_t)
        older = [f for f in REQUIRED_FIELDS
                 if field_path(tdir, f) and os.path.getmtime(field_path(tdir, f)) <= t0]
        cl[6] = "PASS every endTime field newer than 0/T" if not older \
            else "FAIL not newer than 0/T: " + " ".join(older)
        ok = ok and not older
    return ok, cl


# ---------------------------------------------------------------------------
# M4 / M4b -- the ULP comparisons, on PROCESSOR-LOCAL fields.
# ---------------------------------------------------------------------------
def ulp_compare_U(case_a, case_b, label_a, label_b):
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
        pa = field_path(os.path.join(case_a, p, str(END_TIME)), "U")
        pb = field_path(os.path.join(case_b, p, str(END_TIME)), "U")
        if pa is None or pb is None:
            refuse(f"{p}: U missing at {END_TIME} in "
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


def wall_rows(case, t_wall, dt):
    """Per-plate-face wall quantities, from the reconstructed endTime fields.

    The mesh's measured max non-orthogonality is 0 (the reference's
    log.checkMesh and constant/birth_certificate.json), so the wall-normal
    gradient is EXACTLY (value_face - value_owner)/d.  That orthogonality is
    ASSERTED here rather than assumed, and the reader refuses if it fails."""
    tdir = os.path.join(case, str(END_TIME))
    n_faces, start_face = read_boundary_patch(case, PLATE_PATCH)
    owner = read_labelled_list(os.path.join(case, "constant", "polyMesh", "owner"))
    c_path = field_path(tdir, "C")
    if c_path is None:
        refuse(f"{tdir}/C missing -- the launcher's writeCellCentres step did "
               f"not run, so no wall distance can be measured.  Refusing rather "
               f"than inferring a spacing from the blockMeshDict.")
    cc = read_vector_field(c_path)
    fc = read_patch_values(c_path, PLATE_PATCH, True, n_faces)
    Uc = read_vector_field(field_path(tdir, "U"))
    # T and alphat are ABSENT from the simpleFoam reference by construction --
    # it solves no energy equation.  The thermal columns are then UNMEASURED
    # rather than zero, and only Cf is produced.  A reader that substituted
    # zeros here would manufacture a wall heat flux for a case that has none.
    t_path, at_path = field_path(tdir, "T"), field_path(tdir, "alphat")
    thermal = t_path is not None and at_path is not None
    if thermal:
        Tc = read_scalar_field(t_path)
        Tw = read_patch_values(t_path, PLATE_PATCH, False, n_faces)
        at_w = read_patch_values(at_path, PLATE_PATCH, False, n_faces)

    # THE ORTHOGONALITY EVIDENCE IS checkMesh's MEASUREMENT, NOT A RE-DERIVATION
    # FROM TWO ROUNDED NUMBERS.  A first version of this reader asserted
    # |x_cell - x_face| <= 1e-12 and REFUSED on the preflight case at plate face
    # 14, where the two coordinates read 0.007521543256 and 0.007521543255.
    # That is a difference of one unit in the TENTH significant digit -- exactly
    # the resolution of `writePrecision 10` -- so the assertion was testing ASCII
    # round-off and calling it non-orthogonality.  The mesh's actual measured
    # non-orthogonality is asserted here instead, from the figure checkMesh
    # produced, and the per-face check is reduced to what it can honestly be: a
    # consistency bound at the WRITTEN precision.
    bc_path = os.path.join(case, "constant", "birth_certificate.json")
    if not os.path.isfile(bc_path):
        refuse(f"{bc_path} missing: this reader treats the wall gradient as a "
               f"pure y-difference, which is exact only on an orthogonal mesh, "
               f"and it will not assume orthogonality it has not read.")
    import json
    with open(bc_path) as fh:
        bc = json.load(fh)
    if "max_non_orthogonality" not in bc:
        refuse(f"{bc_path} carries no max_non_orthogonality field")
    if float(bc["max_non_orthogonality"]) != 0.0:
        refuse(f"{bc_path} reports max_non_orthogonality "
               f"{bc['max_non_orthogonality']}, not 0.  The wall gradient below "
               f"is (value_face - value_owner)/d, which is EXACT only at zero "
               f"non-orthogonality; refusing rather than reporting a Stanton "
               f"number built on a correction this reader does not apply.")

    # ONE unit in the 10th significant digit, from `writePrecision 10`, doubled
    # as margin.  DERIVED from the write format, not a chosen epsilon: the two
    # coordinates are rounded INDEPENDENTLY and can round in opposite
    # directions, so their difference is bounded by a full unit in the last
    # place, which for a leading digit of 1 is 1e-9 relative.
    #
    # THE CHECK KEEPS ITS DISCRIMINATING POWER, and this was MEASURED on the
    # preflight case rather than argued: the worst |x_cell - x_face| over all
    # 208 plate faces is 1.000000e-09 (pure round-off), while the SMALLEST
    # plate cell spacing is 4.493756e-04 m.  A genuinely misaligned face would
    # show a difference of order that spacing -- FIVE ORDERS OF MAGNITUDE above
    # this bound.  The bound sits in the gap, not near either edge.
    WRITE_PRECISION_BOUND = 2e-9

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
        tau_k = NU * (Uc[o][0] - 0.0) / d                # m2/s2, kinematic
        re_x = U_INF * xf / NU
        cf = 2.0 * tau_k / (U_INF ** 2)
        row = dict(i=i, x=xf, re_x=re_x, d=d, Cf=cf, T_cell=None, T_wall=None,
                   alphat_wall=None, alpha_eff_wall=None, q_kinematic=None,
                   St=None, St_eq1=None)
        if thermal:
            alpha_eff_w = NU / PR + at_w[i]
            q_k = alpha_eff_w * (Tw[i] - Tc[o]) / d      # K m/s, kinematic
            row.update(T_cell=Tc[o], T_wall=Tw[i], alphat_wall=at_w[i],
                       alpha_eff_wall=alpha_eff_w, q_kinematic=q_k,
                       St=(q_k / (U_INF * dt)) if dt != 0.0 else None,
                       St_eq1=eq1_stanton(re_x, t_wall) if re_x > 0 else None)
        rows.append(row)
    return rows


def nearest_station(rows, re_target):
    return min((r for r in rows if r["re_x"] > 0),
               key=lambda r: abs(r["re_x"] - re_target))


def prt_eff(case):
    """M3.  Prt_eff = nut / alphat through the boundary layer.

    On the cavity, D424 measured this pinned at EXACTLY 0.8500 in every cell --
    a better stress closure forced by a constant into being a worse heat-flux
    closure.  This row asks whether the same transmission holds on a flow whose
    momentum closure is the best-validated thing this lab owns.

    WHAT A DEPARTURE FROM 0.85 HERE ACTUALLY MEASURES, and it is NOT physics.
    `buoyantBoussinesqSimpleFoam` sets `alphat = nut/Prt` in TEqn.H and then
    updates `nut` in `turbulence->correct()` LATER IN THE SAME OUTER ITERATION,
    so the two written fields are ONE TURBULENCE CORRECTION APART.  Any spread
    in this ratio is therefore the residual change in `nut` over one outer
    iteration -- a CONVERGENCE diagnostic -- and never a physical variation of
    the turbulent Prandtl number, which is a compile-time constant in this
    solver.  MEASURED on the 5-iteration preflight case: min 0.4391, max 1.5470,
    zero cells at exactly 0.85, on a field that is nowhere near converged.  A
    converged solve should drive the spread toward zero, and THAT is the honest
    reading of this row: it confirms the transmission D424 found -- alphat is
    slaved to nut by a constant, so this quantity cannot report on the physics
    at all -- rather than measuring a Prandtl number."""
    tdir = os.path.join(case, str(END_TIME))
    nut = read_scalar_field(field_path(tdir, "nut"))
    at = read_scalar_field(field_path(tdir, "alphat"))
    if len(nut) != len(at):
        refuse("nut and alphat have different cell counts")
    vals, zeros = [], 0
    for n, a in zip(nut, at):
        if a == 0.0:
            zeros += 1
        else:
            vals.append(n / a)
    if not vals:
        return dict(cells=len(nut), zero_alphat=zeros, min=None, max=None,
                    mean=None, exactly_0p85=0)
    exact = sum(1 for v in vals if ulp_distance(v, PRT) == 0)
    return dict(cells=len(nut), zero_alphat=zeros, min=min(vals), max=max(vals),
                mean=sum(vals) / len(vals), exactly_0p85=exact,
                spread=max(vals) - min(vals))


def thermal_bl(case, rows, station):
    """M5.  Thermal boundary-layer thickness at one station, plus the near-wall
    alphat profile.  The column is the set of cells sharing the station's x."""
    tdir = os.path.join(case, str(END_TIME))
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
    if tw == T_INF:
        return dict(x=xs, column_cells=len(col), delta_T_99=None,
                    near_wall_alphat=[(y, a) for y, _, a in col[:8]],
                    note="dT = 0, so a thermal thickness is undefined rather "
                         "than zero")
    delta = None
    for y, t, _ in col:
        if abs((t - T_INF) / (tw - T_INF)) <= 0.01:
            delta = y
            break
    return dict(x=xs, column_cells=len(col), delta_T_99=delta,
                near_wall_alphat=[(y, a) for y, _, a in col[:8]])


# ---------------------------------------------------------------------------
def analyse(root, reference, scratch, expect_sha=None):
    sha = own_blob_sha()
    print("=" * 78)
    print("K0e -- forced-convection flat plate, campaign F14 cooling ladder")
    print("prereg: docs/campaigns/F14-cooling-ladder/K0e_PREREGISTRATION.md")
    print(f"this file's GIT BLOB SHA-1 (sha1 of b'blob <len>\\0' + content): {sha}")
    print("=" * 78)
    if expect_sha and expect_sha != sha:
        refuse(f"GRADER PIN MISMATCH: this file's git blob sha1 is {sha}; the "
               f"committed blob was given as {expect_sha}.  The grading path is "
               f"fixed at the pre-registration commit (standing rule 2) and this "
               f"is not that file.  NOTE THE HASH FUNCTION: git blob sha1, not "
               f"sha256 and not a plain sha1 of the bytes.")

    # ---- completion, both arms ---------------------------------------
    print("\n--- STRICT COMPLETION RULE (standing rule 4, all-or-nothing) ---")
    print("age-guard datum: <case>/0/T.  K0e is SINGLE-REGION (one mesh, one")
    print("case, no regions), so 0/T is the correct dating file, and")
    print("launch_k0e.sh touches it LAST, immediately before the solver.")
    done = {}
    for arm in ARMS:
        ok, cl = completion(root, arm)
        done[arm] = ok
        print(f"  {arm}: {'DONE' if ok else 'NOT DONE'}")
        for i in sorted(cl):
            print(f"      clause {i}: {cl[i]}")
    # The GATED row is M4b, which needs BOTH arms.  A gated row that cannot be
    # measured cannot yield a PASS.
    if not (done[GRADED_ARM] and done[CONTROL_ARM]):
        missing = [a for a in ARMS if not done[a]]
        print(f"\nM4b      {NOT_A_RESULT}   NOT DONE under the strict "
              f"completion rule: {' '.join(missing)}")
        print(f"RUNG     {NOT_A_RESULT}")
        return EXIT_OK

    case_g = os.path.join(root, GRADED_ARM)
    case_c = os.path.join(root, CONTROL_ARM)
    tdir_g = os.path.join(case_g, str(END_TIME))

    # ---- planted zeros ------------------------------------------------
    print("\n--- PLANTED-ZERO CONTROLS (standing rule 3) ---")
    rec = run_planted_controls(tdir_g, scratch)
    print(f"  P1 scalar plant {PLANT_T!r} K  -> read back "
          f"{rec['P1']['read_back']!r} at line {rec['P1']['line']}   SEEN")
    print(f"  P2 VECTOR plant {PLANT_U!r} m/s (x) -> read back "
          f"{rec['P2']['read_back']!r} at line {rec['P2']['line']}   SEEN")
    print(f"  P3 negative control 0.0 -> read back {rec['P3']['read_back']!r}"
          f"   DID NOT FIRE")

    # ---- M4b, THE ONLY GATED ROW --------------------------------------
    print("\n--- M4b SAME-SOLVER NEUTRALISATION CONTROL, THE ONLY GATED ROW ---")
    print("  FP_T10 vs FP_T00: the SAME binary and the SAME discrete operators,")
    print("  differing ONLY in the wall temperature.  With beta = 0 the thermal")
    print("  field cannot enter the momentum equation at all, so the operator")
    print("  confound cancels EXACTLY and this is a clean test of whether beta")
    print("  and g were neutralised.")
    print("  threshold: 0 ULP, on every component of every cell, processor-local.")
    print("  There is no tolerance constant in this comparator.")
    m4b = ulp_compare_U(case_g, case_c, GRADED_ARM, CONTROL_ARM)
    print(f"  cells compared             {m4b['cells']} x 3 components")
    print(f"  components at non-zero ULP {m4b['components_nonzero']}")
    print(f"  worst ULP distance         {m4b['worst_ulp']}")
    if m4b["worst_ulp"]:
        print(f"  worst at                   {m4b['where']}   "
              f"|diff| {m4b['worst_abs']:.6e} m/s   (REPORTED beside the "
              f"verdict, NOT a threshold)")
    m4b_pass = (m4b["worst_ulp"] == 0)
    print(f"  M4b {PASS if m4b_pass else NOT_A_RESULT}")

    # ---- M4, REPORTED, NOT GATED --------------------------------------
    print("\n--- M4  CROSS-SOLVER MOMENTUM COMPARISON (REPORTED, NOT GATED) ---")
    print("  FP_T10 against the recorded simpleFoam field.  It is NOT gated, and")
    print("  the reason is read from the installed source rather than preferred:")
    print("    simpleFoam:                 UEqn == -fvc::grad(p)")
    print("    buoyantBoussinesqSimpleFoam: UEqn == fvc::reconstruct(")
    print("                                   (-ghf*snGrad(rhok)")
    print("                                    - snGrad(p_rgh))*magSf)")
    print("  Those are DIFFERENT DISCRETE OPERATORS and they differ INDEPENDENTLY")
    print("  of beta and g, so a non-zero M4 conflates 'beta/g leaked' with 'the")
    print("  operators are not identical' and cannot separate them.  A gate that")
    print("  cannot answer its own gating question is not a gate.")
    m4 = ulp_compare_U(case_g, reference, GRADED_ARM, "simpleFoam reference")
    print(f"  cells compared             {m4['cells']} x 3 components")
    print(f"  components at non-zero ULP {m4['components_nonzero']}")
    print(f"  worst ULP distance         {m4['worst_ulp']}")
    if m4["worst_ulp"]:
        print(f"  worst at                   {m4['where']}")
        print(f"  worst pair                 {m4['worst_pair'][0]!r} vs "
              f"{m4['worst_pair'][1]!r}   (|diff| {m4['worst_abs']:.6e} m/s)")
    print(f"  M4  {REPORTED}")
    print("  NOTE, and it is the whole point of the pair: M4b at 0 ULP with M4")
    print("  non-zero is the SIGNATURE of the operator difference and of nothing")
    print("  else.  M4b non-zero is a beta/g leak, whatever M4 reads.")

    # ---- M1 / M2, REPORTED --------------------------------------------
    rows_g = wall_rows(case_g, T_WALL_THERMAL, DT_THERMAL)
    print("\n--- M1  STANTON NUMBER vs Bahrami eq. (1)  [REPORTED, NO BAND] ---")
    print("  No band is armed.  The pre-registration section 3 registers that the")
    print("  source states no uncertainty for eq. (1), and arming a band at what")
    print("  two-equation models typically achieve would be setting the gate to")
    print("  what we expect.  This row CANNOT pass and CANNOT gate-fail.")
    print(f"  eq. (1): St = {EQ1_COEFF} Re^{EQ1_RE_EXP} (Pr Tw/T_inf)^{EQ1_PRTW_EXP}"
          f"   [Pr={PR}, Tw/T_inf={T_WALL_THERMAL/T_INF:.6f}]")
    print(f"  {'Re_x':>12} {'x [m]':>10} {'St':>13} {'St_eq1':>13} {'dev %':>9}")
    for tgt in RE_X_STATIONS:
        r = nearest_station(rows_g, tgt)
        dev = 100.0 * (r["St"] - r["St_eq1"]) / r["St_eq1"]
        print(f"  {r['re_x']:12.4e} {r['x']:10.4f} {r['St']:13.6e} "
              f"{r['St_eq1']:13.6e} {dev:+9.2f}")
    print(f"  M1  {REPORTED}")

    print("\n--- M2  SKIN FRICTION, control [REPORTED] ---")
    rows_r = None
    ref_recon = os.path.join(reference, str(END_TIME))
    if os.path.isdir(ref_recon) and field_path(ref_recon, "C") is not None:
        rows_r = wall_rows(reference, T_INF, 0.0)
    print(f"  {'Re_x':>12} {'Cf (K0e)':>13} {'Cf (ref)':>13}")
    for tgt in RE_X_STATIONS:
        r = nearest_station(rows_g, tgt)
        if rows_r:
            rr = nearest_station(rows_r, tgt)
            print(f"  {r['re_x']:12.4e} {r['Cf']:13.6e} {rr['Cf']:13.6e}")
        else:
            print(f"  {r['re_x']:12.4e} {r['Cf']:13.6e} {'unreconstructed':>13}")
    if rows_r is None:
        print("  the reference is not reconstructed at endTime, so its Cf is")
        print("  UNMEASURED here; M4 already compares the two U fields directly")
        print("  and is the stronger statement.")
    print(f"  M2  {REPORTED}")

    # ---- M3, M5, M6 ----------------------------------------------------
    print("\n--- M3  Prt_eff = nut/alphat THROUGH THE BOUNDARY LAYER [REPORTED] ---")
    p = prt_eff(case_g)
    print(f"  cells {p['cells']}, of which alphat == 0 in {p['zero_alphat']}")
    if p["min"] is not None:
        print(f"  min {p['min']!r}  max {p['max']!r}  mean {p['mean']!r}")
        print(f"  spread {p['spread']:.6e}")
        print(f"  cells at EXACTLY Prt = {PRT} (0 ULP): {p['exactly_0p85']} of "
              f"{p['cells'] - p['zero_alphat']}")
    print("  READ THIS ROW AS A CONVERGENCE DIAGNOSTIC, NOT AS PHYSICS: alphat")
    print("  is set to nut/Prt in TEqn.H and nut is updated LATER in the same")
    print("  outer iteration, so the two written fields are one turbulence")
    print("  correction apart.  Prt is a constant in this solver and cannot")
    print("  vary; the spread measures how much nut still moves per iteration.")
    print(f"  M3  {REPORTED}")

    print("\n--- M5  THERMAL BOUNDARY LAYER AND NEAR-WALL alphat [REPORTED] ---")
    st = nearest_station(rows_g, 5.0e6)
    bl = thermal_bl(case_g, rows_g, st)
    print(f"  station x = {bl['x']:.4f} m (Re_x {st['re_x']:.4e}), column cells "
          f"{bl['column_cells']}")
    print(f"  delta_T (1 % of wall excess) = {bl['delta_T_99']}")
    for y, a in bl["near_wall_alphat"]:
        print(f"      y = {y:.6e} m   alphat = {a:.6e} m2/s")
    print(f"  M5  {REPORTED}")

    print("\n--- M6  ZERO-dT CONTROL: wall heat flux must be identically zero ---")
    if not done[CONTROL_ARM]:
        print(f"  M6  {UNMEASURED}  {CONTROL_ARM} is NOT DONE")
    else:
        rows_c = wall_rows(case_c, T_INF, 0.0)
        worst = max(rows_c, key=lambda r: abs(r["q_kinematic"]))
        nz = sum(1 for r in rows_c if r["q_kinematic"] != 0.0)
        print(f"  plate faces {len(rows_c)}, non-zero kinematic wall flux on {nz}")
        print(f"  worst |q/(rho cp)| = {abs(worst['q_kinematic']):.6e} K m/s at "
              f"x = {worst['x']:.4f} m")
        print("  Stanton is UNDEFINED here, not small: dT = 0 is the denominator.")
        print(f"  M6  {REPORTED}")

    # ---- rule 5 ---------------------------------------------------------
    print("\n--- STANDING RULE 5 (Roache triple gating) ---")
    print("  NO TRIPLE IS FORMED.  K0e runs two arms on ONE mesh (52 224 cells).")
    print("  Rule 5 does not engage, no GCI is computed, and none is printed.")

    # ---- the rung verdict ------------------------------------------------
    print("\n" + "=" * 78)
    if m4b_pass:
        print(f"RUNG K0eR2 {PASS}  on M4b, the only gated row: the momentum field")
        print("           is bit-identical between the two wall temperatures, so")
        print("           beta and g ARE neutralised and a Stanton error on this")
        print("           rung is attributable to the thermal closure alone.")
        print("           Every other row is REPORTED, not gated.  No band is")
        print("           armed on the correlation, so this rung CANNOT GATE FAIL,")
        print("           and its Stanton agreement is NOT a validation of the")
        print("           thermal closure -- see the pre-registration section")
        print("           2.1.3 on circularity.")
        print(f"           M4 (cross-solver) reads {m4['worst_ulp']} ULP, REPORTED.")
    else:
        print(f"RUNG K0eR2 {NOT_A_RESULT}.  M4b is non-zero: the momentum field")
        print("           moved when ONLY the wall temperature changed, on the")
        print("           same binary and the same discrete operators.  beta and")
        print("           g were therefore NOT neutralised, and the attribution")
        print("           of any Stanton error to the thermal closure is VOID.")
        print("           The reported rows above stand as measurements and as")
        print("           NOTHING MORE.")
    print("=" * 78)
    return EXIT_OK


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True,
                    help="K0e_runs, holding FP_T10/, FP_T00/ and STATUS.*")
    ap.add_argument("--reference", default=REFERENCE_DEFAULT)
    ap.add_argument("--scratch", required=True,
                    help="a scratch directory for the three planted copies")
    ap.add_argument("--expect-sha",
                    help="the committed GIT BLOB SHA-1 of this file.  Not a "
                         "sha256.  Not a plain sha1 of the bytes.")
    a = ap.parse_args()
    return analyse(a.root, a.reference, a.scratch, a.expect_sha)


if __name__ == "__main__":
    sys.exit(main())
