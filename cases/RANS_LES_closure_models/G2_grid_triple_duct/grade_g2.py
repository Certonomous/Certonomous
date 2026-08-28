"""G2 comparator: the Roache triple on the AR_1_Ret_360 square-duct family.

Ordering is standing rule 5 and it is enforced structurally, not remembered:
`grade()` returns on an incomplete or iteratively-unconverged level BEFORE any
Roache arithmetic runs, and `roache()` returns before computing `p`, `f_ext` or
the GCI on any branch that is not CONVERGING.  No GCI is computed, let alone
printed, off the monotone branch.

Refusals are `raise` / `sys.exit(2)`, never `assert`: `python3 -O` deletes every
assert (L-332).  This module counts its own `ast.Assert` nodes and refuses if it
holds one, with the counter first shown able to count a planted assert so that
its zero is a reading and not a blind spot.
"""

import ast
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

# ---- FROZEN REGISTRY (PREREGISTRATION.md sections 2, 3, 4, 5) -------------
RUN_ROOT = Path("/home/ubuntu/closure-data/g2")
SRC_CASE = Path("/home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_360")

# coarse -> fine.  Roache indices: 1 = finest = L3, 2 = L2, 3 = coarsest = L1.
LEVELS = (
    ("L1", 1024, 20000),
    ("L2", 4096, 30000),
    ("L3", 16384, 40000),
)
D_SPATIAL = 2      # refinement is applied in y and z; the single streamwise cell
                   # sits between MATCHED CYCLIC patches, so d/dx is identically
                   # zero over one cell and x carries no discretisation.
R21 = 2.0          # h(L2)/h(L3) = (16384/4096)^(1/2)
R32 = 2.0          # h(L1)/h(L2) = (4096/1024)^(1/2)
FS = 1.25          # Roache factor of safety, three-grid GCI

LX = 1.0e-3
LY = 1.0e-3
LZ = 1.0e-3
DOMAIN_VOLUME = LX * LY * LZ          # 1e-09 m^3, checkMesh "Total volume"
DOMAIN_VOLUME_RTOL = 1e-6
WALL_AREA = {"wallTop": LX * LZ, "wallSide": LX * LY}   # closed form, 1e-06 m^2
WALL_AREA_RTOL = 1e-6

REQ_FIELDS = ("U", "p", "k", "omega", "nut")
GRADP_FILE = "uniform/meanVelocity1Properties"   # the fvOption is named meanVelocity1
AGE_MARKER = "0/U"

# Iterative convergence, per level.  `p`, `Uy` and `Uz` carry NO threshold and
# this is FORCED, not chosen: a linear eddy-viscosity model produces no secondary
# flow in a straight duct, so the in-plane field is machine noise, OpenFOAM
# normalises the residual by that noise, and the ratio is O(0.1-0.7) forever.
# Measured on this box (section 4.2 of the pre-registration).  They are recorded.
RES_MAX = {"Ux": 1e-6, "k": 5e-6, "omega": 5e-6}
RES_REQUIRED = ("Ux", "k", "omega")
RES_DIAGNOSTIC = ("Uy", "Uz", "p")
PLATEAU_TAIL_FRAC = 0.10
PLATEAU_RTOL = 1e-5
DISK_VS_LOG_RTOL = 1e-6

# functional registry: key -> (label, unit, p_lo, p_hi, gci_max_pct, floor_mode, floor)
FUNCTIONALS = (
    ("gradP", "PRIMARY  mean streamwise momentum source", "m/s2",
     1.0, 3.0, 5.0, "rel", 1e-5),
    ("Kint", "SECONDARY-A  volume-integrated k", "m5/s2",
     0.5, 3.0, 10.0, "rel", 1e-5),
    ("tauwint", "SECONDARY-B  integrated streamwise wall shear", "m4/s2",
     0.5, 3.0, 10.0, "rel", 1e-5),
)

# Momentum-balance identity: gradP * V should equal the integrated wall shear.
# This is an ALARM LEVEL, NOT A GATE (section 4.3.1 of the pre-registration). It
# cannot turn anything into a GATE FAIL and it changes no verdict; if it fires,
# the rung is NOT BELIEVED pending supervisor triage.
MOMENTUM_ALARM_RTOL = 0.05

# Registered in ADVANCE (section 5.3.1): a `p` outside its band has TWO candidate
# causes and the record must carry both. Naming cause 2 only after seeing a bad
# `p` would be choosing the explanation to fit the answer.
P_BAND_CANDIDATE_CAUSES = (
    "      REGISTERED CANDIDATE CAUSES (section 5.3.1, named before any value "
    "existed;\n      both are reported, and neither is the default):\n"
    "        (1) THE SCHEME -- the stretched cell-centred laplacian's degraded "
    "order,\n            the cellLimited gradient limiter on k and omega, or L1 "
    "outside the\n            asymptotic range.\n"
    "        (2) THE NON-SYSTEMATIC WALL-CELL REFINEMENT -- measured local linear "
    "ratios\n            1.9492 and 1.9748 against an ideal 2 (a 2.5 % and 1.3 % "
    "departure),\n            which the GCI's exact r = 2 does not carry.\n"
    "      Deciding which dominates needs a fourth level or a second anchor: a "
    "SEPARATE,\n      separately pre-registered rung, not a conclusion drawn here."
)

PLANT_GRADP = 1.234567e-03
PLANT_K = 9.876543e+02
PLANT_KUNIFORM = 2.0
PLANT_TAU = 3.456789e-01
PLANT_TAU_FACE = 7.654321e+00

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$")
GRADP_LOG = re.compile(r"pressure gradient = ([-+0-9.eE]+)")

# The FATAL reader used by `parse_log`, REPAIRED 2026-08-28 under the pre-compute
# amendment (PREREGISTRATION.md v1.1).  The frozen clause was
#     FOAM FATAL|Floating point exception|signal \(
# ANDed with itself, and its UNANCHORED `Floating point exception` matched
# OpenFOAM's own startup banner --
#     trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
# -- which every log this box produces carries at line 18.  A clause that fires on
# a safety notice is a constant, not a detector.  The replacement is built from
# the lab's own precedents: the FOAM-ERROR channel of
# `sdk/chief_engineer/mesh_certificate.py` (_FATAL) and the LINE-ANCHORED FPE
# channel of `sdk/chief_engineer/head_engineer.py:188`.  Anchoring is what defeats
# the banner: the banner's phrase is preceded by `trapFpe: ` and so never begins
# its line.  Five channels:
#   (1) a genuine FOAM error header, with or without ` IO`, at any MPI rank prefix
#   (2) the library's own exit line
#   (3) a signal handler that actually FIRED (sigFpe, sigSegv, sigInt, ...)
#   (4) a stack trace being printed
#   (5) a message the SHELL wrote, which always begins the line it is on
# `trapping enabled` appears in none of them.  This reader is exercised in BOTH
# directions by `planted_control_fatal` (standing rule 3).
FATAL_RE = re.compile(
    r"-->\s*FOAM FATAL(?:\s+IO)?\s+ERROR"
    r"|FOAM exiting"
    r"|Foam::sig\w+::sigHandler"
    r"|Foam::error::printStack"
    r"|^(?:Floating point exception|Segmentation fault)",
    re.MULTILINE)

# OpenFOAM's startup banner, VERBATIM from a real log on this box
# (/home/ubuntu/closure-data/g1/L1/log.run line 18).  The negative direction of
# the planted control writes this exact line to disk.
FPE_BANNER = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n"


class Refusal(Exception):
    """A condition that must stop this instrument under ANY interpreter flag."""


def refuse(msg):
    raise Refusal(msg)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------
# L-332 control
# --------------------------------------------------------------------------
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse("AST-CONTROL: the counter returned %d on a snippet holding exactly "
               "one assert; its zero here would be a blind spot, not a reading."
               % planted)
    own = count_asserts(Path(__file__).read_text())
    if own != 0:
        refuse("AST-CONTROL: this module holds %d ast.Assert node(s); python3 -O "
               "deletes every one (L-332)." % own)
    return planted, own


# --------------------------------------------------------------------------
# OpenFOAM ASCII readers.  These are THE readers the planted controls exercise.
# --------------------------------------------------------------------------
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def _read(path):
    path = Path(path)
    if not path.is_file():
        refuse("READER: %s does not exist" % path)
    return path.read_text(errors="replace")


def _strip_header(text):
    """Drop the FoamFile header block so its keywords cannot be mistaken for data."""
    m = re.search(r"(?m)^FoamFile\s*$", text)
    if m is None:
        return text
    ob = text.find("{", m.end())
    if ob < 0:
        return text
    depth = 0
    for i in range(ob, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:]
    return text


def read_gradP_disk(path):
    """The `gradient` entry of the fvOption's own uniform/<name>Properties file."""
    body = _strip_header(_read(path))
    m = re.search(r"(?m)^\s*gradient\s+(%s)\s*;" % NUM, body)
    if m is None:
        refuse("READER: %s carries no `gradient <value>;` entry" % path)
    return float(m.group(1))


def read_scalar_internal(path, ncells):
    """internalField of a volScalarField, uniform or nonuniform, length-checked."""
    body = _strip_header(_read(path))
    m = re.search(r"(?m)^\s*internalField\s+uniform\s+(%s)\s*;" % NUM, body)
    if m is not None:
        return [float(m.group(1))] * ncells
    m = re.search(r"(?m)^\s*internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)"
                  r"\s*\n\(", body)
    if m is None:
        refuse("READER: %s has neither a uniform nor a nonuniform scalar "
               "internalField" % path)
    n = int(m.group(1))
    start = m.end()
    close = body.find("\n)", start)
    if close < 0:
        refuse("READER: %s has an unterminated internalField list" % path)
    vals = [float(x) for x in re.findall(NUM, body[start:close])]
    if len(vals) != n:
        refuse("READER: %s declares %d values and holds %d" % (path, n, len(vals)))
    if n != ncells:
        refuse("READER: %s holds %d values, the mesh has %d cells" % (path, n, ncells))
    return vals


def read_patch_vector(path, patch, nfaces):
    """The `value` entry of one patch of a volVectorField's boundaryField."""
    body = _strip_header(_read(path))
    m = re.search(r"(?m)^\s*%s\s*\n\s*\{" % re.escape(patch), body)
    if m is None:
        refuse("READER: %s has no boundaryField entry for patch %r" % (path, patch))
    ob = body.index("{", m.start())
    depth, cb = 0, None
    for i in range(ob, len(body)):
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
            if depth == 0:
                cb = i
                break
    if cb is None:
        refuse("READER: %s patch %r block is unterminated" % (path, patch))
    blk = body[ob:cb]
    u = re.search(r"value\s+uniform\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (NUM, NUM, NUM), blk)
    if u is not None:
        return [(float(u.group(1)), float(u.group(2)), float(u.group(3)))] * nfaces
    nu = re.search(r"value\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n\(", blk)
    if nu is None:
        refuse("READER: %s patch %r carries neither a uniform nor a nonuniform "
               "vector `value`" % (path, patch))
    n = int(nu.group(1))
    start = nu.end()
    close = blk.find("\n)", start)
    if close < 0:
        refuse("READER: %s patch %r has an unterminated value list" % (path, patch))
    trips = [tuple(float(x) for x in t.split())
             for t in re.findall(r"\(([^)]*)\)", blk[start:close])]
    if len(trips) != n:
        refuse("READER: %s patch %r declares %d faces and holds %d"
               % (path, patch, n, len(trips)))
    if n != nfaces:
        refuse("READER: %s patch %r holds %d values, the mesh patch has %d faces"
               % (path, patch, n, nfaces))
    for t in trips:
        if len(t) != 3:
            refuse("READER: %s patch %r holds a non-3-component entry" % (path, patch))
    return trips


def _foam_list(path):
    text = _read(path)
    m = re.search(r"\n(\d+)\s*\n\(", text)
    if m is None:
        refuse("READER: %s carries no `<count>\\n(` list header" % path)
    n = int(m.group(1))
    start = m.end()
    close = text.find("\n)", start)
    if close < 0:
        refuse("READER: %s has an unterminated list" % path)
    return n, text[start:close]


def read_mesh_geometry(case):
    """points, faces, and the boundary patch table, straight from constant/polyMesh.

    Wall face areas are computed here from the mesh itself, so SECONDARY-B needs
    no post-processing artefact to define its measure -- only the shear field.
    """
    pm = Path(case) / "constant/polyMesh"
    n, body = _foam_list(pm / "points")
    pts = [tuple(float(x) for x in t.split())
           for t in re.findall(r"\(([^)]*)\)", body)]
    if len(pts) != n:
        refuse("READER: %s/points declares %d and holds %d" % (pm, n, len(pts)))
    nf, fbody = _foam_list(pm / "faces")
    faces = [[int(x) for x in t.split()]
             for t in re.findall(r"\d+\(([^)]*)\)", fbody)]
    if len(faces) != nf:
        refuse("READER: %s/faces declares %d and holds %d" % (pm, nf, len(faces)))
    btxt = _read(pm / "boundary")
    patches = {}
    for name, blk in re.findall(r"\n\s{4}(\w+)\s*\n\s{4}\{(.*?)\n\s{4}\}", btxt, re.S):
        mn = re.search(r"nFaces\s+(\d+)", blk)
        ms = re.search(r"startFace\s+(\d+)", blk)
        if mn is None or ms is None:
            refuse("READER: %s/boundary patch %r lacks nFaces or startFace" % (pm, name))
        patches[name] = (int(mn.group(1)), int(ms.group(1)))
    return pts, faces, patches


def face_areas(pts, faces, patches, patch):
    """|Sf| for every face of one patch, by the centroid-fan decomposition."""
    if patch not in patches:
        refuse("GEOMETRY: the mesh has no patch %r" % patch)
    nF, sF = patches[patch]
    out = []
    for i in range(sF, sF + nF):
        idx = faces[i]
        if len(idx) < 3:
            refuse("GEOMETRY: face %d of patch %r has %d points" % (i, patch, len(idx)))
        cx = sum(pts[j][0] for j in idx) / len(idx)
        cy = sum(pts[j][1] for j in idx) / len(idx)
        cz = sum(pts[j][2] for j in idx) / len(idx)
        sx = sy = sz = 0.0
        for k in range(len(idx)):
            a = pts[idx[k]]
            b = pts[idx[(k + 1) % len(idx)]]
            ux, uy, uz = a[0] - cx, a[1] - cy, a[2] - cz
            vx, vy, vz = b[0] - cx, b[1] - cy, b[2] - cz
            sx += uy * vz - uz * vy
            sy += uz * vx - ux * vz
            sz += ux * vy - uy * vx
        out.append(0.5 * math.sqrt(sx * sx + sy * sy + sz * sz))
    return out


# --------------------------------------------------------------------------
# log parsing
# --------------------------------------------------------------------------
def parse_log(path):
    """Parse log.run.  An ABSENT log is reported, never refused.

    A level with no solver log is an INCOMPLETE level, and standing rule 5 step 1
    already has the right answer for that: the rung is NOT A RESULT.  Refusing
    here would replace the registered verdict with an instrument error, which is
    less informative and skips the ordering the rule fixes.  (This is a
    deliberate departure from `grade_g1.py`, whose `parse_log` refuses; declared
    in section 6.3 of the pre-registration.)
    """
    path = Path(path)
    if not path.is_file():
        return {"absent": True, "end": False, "fatal": False, "libs_warning": False,
                "exec_count": -1, "n_time_blocks": 0, "gradP_hist": [],
                "final_res": {}, "final_exec_s": None}
    text = _read(path)
    blocks = [m.start() for m in re.finditer(r"(?m)^Time = ", text)]
    last = text[blocks[-1]:] if blocks else ""
    final_res = {}
    for name in tuple(RES_MAX) + RES_DIAGNOSTIC:
        m = re.search(r"Solving for %s, Initial residual = (%s)" % (re.escape(name), NUM),
                      last)
        if m is not None:
            final_res[name] = float(m.group(1))
    return {
        "absent": False,
        "end": bool(re.search(r"(?m)^End\s*$", text)),
        # REPAIRED 2026-08-28 (pre-compute amendment, PREREGISTRATION.md v1.1).
        # The frozen expression matched OpenFOAM's `trapFpe:` startup banner and
        # so returned True on any clean log; see FATAL_RE above for the reading
        # and the precedents.  `libs_warning` on the next line is a SEPARATE
        # channel and is untouched -- note that the frozen clause's
        # `--> FOAM Warning : Could not load` alternative sat only in the FIRST
        # half of the `and`, so it could never on its own make `fatal` True, and
        # dropping it here changes no behaviour.
        "fatal": bool(FATAL_RE.search(text)),
        "libs_warning": "Could not load" in text,
        "exec_count": len(re.findall(r"ExecutionTime = ", text)),
        "n_time_blocks": len(blocks),
        "gradP_hist": [float(x) for x in GRADP_LOG.findall(text)],
        "final_res": final_res,
        "final_exec_s": (float(re.findall(r"ExecutionTime = (%s) s" % NUM, text)[-1])
                         if re.findall(r"ExecutionTime = (%s) s" % NUM, text) else None),
    }


# --------------------------------------------------------------------------
# functionals
# --------------------------------------------------------------------------
def f_gradP(case, end):
    return read_gradP_disk(Path(case) / str(end) / GRADP_FILE)


def f_Kint(case, end, ncells):
    d = Path(case) / str(end)
    k = read_scalar_internal(d / "k", ncells)
    v = read_scalar_internal(d / "V", ncells)
    tot = sum(v)
    if abs(tot - DOMAIN_VOLUME) > DOMAIN_VOLUME_RTOL * DOMAIN_VOLUME:
        refuse("KINT: sum(V) = %.9e does not match the closed-form domain volume "
               "%.9e to %.0e relative; the volume field does not belong to this mesh"
               % (tot, DOMAIN_VOLUME, DOMAIN_VOLUME_RTOL))
    return sum(ki * vi for ki, vi in zip(k, v)), tot


def f_tauwint(case, end, geom):
    """sum over wallTop and wallSide of |tau_wx| * |Sf|.

    Areas come from constant/polyMesh, so the measure is exact and independent of
    every post-processing artefact; only the shear field itself is read from the
    solver's output.
    """
    pts, faces, patches = geom
    d = Path(case) / str(end)
    total, per_patch = 0.0, {}
    for patch, closed in WALL_AREA.items():
        nF = patches[patch][0] if patch in patches else 0
        areas = face_areas(pts, faces, patches, patch)
        got = sum(areas)
        if abs(got - closed) > WALL_AREA_RTOL * closed:
            refuse("TAUW: patch %r area %.9e does not match the closed-form %.9e to "
                   "%.0e relative" % (patch, got, closed, WALL_AREA_RTOL))
        tau = read_patch_vector(d / "wallShearStress", patch, nF)
        s = sum(abs(t[0]) * a for t, a in zip(tau, areas))
        per_patch[patch] = s
        total += s
    return total, per_patch


# --------------------------------------------------------------------------
# planted controls (standing rule 3).  Each writes a REAL file and reads it back
# through the SAME function used on the real data, and REFUSES on invisibility.
# --------------------------------------------------------------------------
def planted_control_gradP(real_path, tmp):
    real = Path(real_path).read_text(errors="replace")
    truth = read_gradP_disk(real_path)
    planted = re.sub(r"(?m)^(\s*gradient\s+)%s(\s*;)" % NUM,
                     lambda m: "%s%.9e%s" % (m.group(1), PLANT_GRADP, m.group(2)),
                     real, count=1)
    if planted == real:
        refuse("PLANT gradP: the substitution changed nothing; the plant was never "
               "written and its recovery would prove nothing")
    p = Path(tmp) / "planted_meanVelocity1Properties"
    p.write_text(planted)
    got = read_gradP_disk(p)
    if abs(got - PLANT_GRADP) > 1e-12 * abs(PLANT_GRADP):
        refuse("PLANT gradP: wrote %.9e to disk and read back %.9e; the reader "
               "cannot see a value it is asked to report" % (PLANT_GRADP, got))
    # the inverse: the same reader on the UNPLANTED file must not return the plant
    if abs(truth - PLANT_GRADP) <= 1e-12 * abs(PLANT_GRADP):
        refuse("PLANT gradP: the reader returns the plant on the UNPLANTED file; "
               "it is a constant, not a reader")
    return truth, got


def planted_control_Kint(case, end, ncells, tmp):
    d = Path(case) / str(end)
    v = read_scalar_internal(d / "V", ncells)
    tot = sum(v)
    work = Path(tmp) / "kint"
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(d / "V", work / "V")

    # (a) uniform k -> a CLOSED-FORM answer
    ktext = (Path(d / "k").read_text(errors="replace"))
    uni = re.sub(r"(?m)^(\s*internalField\s+)(uniform\s+%s|nonuniform\s+List<scalar>"
                 r"\s*\n?\s*\d+\s*\n\((?:[^)]|\)(?!\s*;))*\))(\s*;)" % NUM,
                 lambda m: "%suniform %.9e%s" % (m.group(1), PLANT_KUNIFORM, m.group(3)),
                 ktext, count=1, flags=re.S)
    if uni == ktext:
        refuse("PLANT Kint(a): the uniform substitution changed nothing")
    (work / "k").write_text(uni)
    got = sum(a * b for a, b in zip(read_scalar_internal(work / "k", ncells), v))
    want = PLANT_KUNIFORM * tot
    if abs(got - want) > 1e-9 * abs(want):
        refuse("PLANT Kint(a): uniform k = %.6g over sum(V) = %.9e must integrate to "
               "%.9e; the integrator returned %.9e" % (PLANT_KUNIFORM, tot, want, got))

    # (b) ONE cell at a known index -> the integral must move by exactly delta * V_i
    kvals = read_scalar_internal(d / "k", ncells)
    idx = ncells // 3
    base = sum(a * b for a, b in zip(kvals, v))
    mutated = list(kvals)
    mutated[idx] = PLANT_K
    (work / "k").write_text(_write_scalar_field(mutated))
    got = sum(a * b for a, b in zip(read_scalar_internal(work / "k", ncells), v))
    want = base + (PLANT_K - kvals[idx]) * v[idx]
    if abs(got - want) > 1e-9 * max(1.0, abs(want)):
        refuse("PLANT Kint(b): rewriting cell %d to %.6g must move the integral by "
               "exactly delta * V[%d]; expected %.9e, read %.9e. The reader is not "
               "reading per-cell values at the right index."
               % (idx, PLANT_K, idx, want, got))
    return base, tot


def _write_scalar_field(vals):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volScalarField;\n    object k;\n}\n\n"
            "dimensions      [0 2 -2 0 0 0 0];\n\n"
            "internalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n\n"
            "boundaryField\n{\n}\n"
            % (len(vals), "\n".join("%.17g" % x for x in vals)))


def _write_patch_vector(patch, trips):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volVectorField;\n    object wallShearStress;\n}\n\n"
            "dimensions      [0 2 -2 0 0 0 0];\n\n"
            "internalField   uniform (0 0 0);\n\n"
            "boundaryField\n{\n    %s\n    {\n        type            calculated;\n"
            "        value           nonuniform List<vector> \n%d\n(\n%s\n)\n;\n"
            "    }\n}\n"
            % (patch, len(trips),
               "\n".join("(%.17g %.17g %.17g)" % t for t in trips)))


def planted_control_tauw(geom, tmp):
    """Round-trip a real mesh's wall patch through the real shear reader."""
    pts, faces, patches = geom
    work = Path(tmp) / "tauw"
    work.mkdir(parents=True, exist_ok=True)
    patch = "wallTop"
    areas = face_areas(pts, faces, patches, patch)
    nF = len(areas)

    # (a) uniform shear -> a CLOSED-FORM answer against the independently
    #     computed patch area
    (work / "wallShearStress").write_text(
        _write_patch_vector(patch, [(PLANT_TAU, 0.0, 0.0)] * nF))
    tau = read_patch_vector(work / "wallShearStress", patch, nF)
    got = sum(abs(t[0]) * a for t, a in zip(tau, areas))
    want = PLANT_TAU * sum(areas)
    if abs(got - want) > 1e-9 * abs(want):
        refuse("PLANT tauw(a): uniform tau_wx = %.6g over patch area %.9e must "
               "integrate to %.9e; the integrator returned %.9e"
               % (PLANT_TAU, sum(areas), want, got))

    # (b) ONE face at a known index -> the integral must move by exactly
    #     (|new| - |old|) * A_i
    trips = [(PLANT_TAU, 0.0, 0.0)] * nF
    idx = nF // 3
    trips = list(trips)
    trips[idx] = (PLANT_TAU_FACE, 0.0, 0.0)
    (work / "wallShearStress").write_text(_write_patch_vector(patch, trips))
    tau = read_patch_vector(work / "wallShearStress", patch, nF)
    got = sum(abs(t[0]) * a for t, a in zip(tau, areas))
    want2 = want + (PLANT_TAU_FACE - PLANT_TAU) * areas[idx]
    if abs(got - want2) > 1e-9 * abs(want2):
        refuse("PLANT tauw(b): rewriting face %d to %.6g must move the integral by "
               "exactly (delta)*A[%d]; expected %.9e, read %.9e. The reader is not "
               "reading per-face values at the right index."
               % (idx, PLANT_TAU_FACE, idx, want2, got))

    # (c) a face count that does not match the mesh must REFUSE, not be padded
    (work / "wallShearStress").write_text(
        _write_patch_vector(patch, [(PLANT_TAU, 0.0, 0.0)] * (nF - 1)))
    try:
        read_patch_vector(work / "wallShearStress", patch, nF)
    except Refusal:
        return want2
    refuse("PLANT tauw(c): a shear field with %d values on a %d-face patch was "
           "accepted; the length check is not a check" % (nF - 1, nF))


def planted_control_fatal():
    """Standing rule 3 for the FATAL reader, in BOTH directions.

    A detector never shown able to return NOT-fatal is a constant, and the clause
    this control guards WAS one: measured over 70 `log.run` files across three
    families the frozen expression fired on 63, of which 57 carry a clean `End`.
    So this control writes THREE REAL files into a `tempfile.TemporaryDirectory()`
    and reads every one of them back through `parse_log` -- the SAME function the
    three registered levels go through, not a copy of its expression -- and
    REFUSES if either direction fails.  The negative direction is the point of the
    control, not a courtesy to it.

    Returns (fatal_on_FOAM_FATAL, fatal_on_sigFpe, fatal_on_clean_banner_log),
    which is (True, True, False) or this function has already refused.
    """
    prologue = ("Exec   : simpleFoam -case .\n"
                "Host   : ip-172-31-43-247\n"
                "nProcs : 1\n"
                + FPE_BANNER +
                "memory pool : not available\n"
                "fileModificationChecking : Monitoring run-time modified files\n\n")
    body = ("Time = 1\n"
            "DILUPBiCGStab:  Solving for Ux, Initial residual = 1e-14, "
            "Final residual = 1e-16, No Iterations 1\n"
            "ExecutionTime = 1 s  ClockTime = 1 s\n\n")

    with tempfile.TemporaryDirectory(prefix="g2fatal_") as td:
        td = Path(td)

        # (a) POSITIVE: a genuine FOAM FATAL ERROR block, as the library writes it.
        a_path = td / "plant_log_foam_fatal.run"
        a_path.write_text(
            prologue + body +
            "--> FOAM FATAL ERROR: (openfoam-2606)\n"
            "Maximum number of iterations exceeded: 1000\n\n"
            "    From function void Foam::PBiCGStab::solve(...)\n"
            "    in file lduMatrix/solvers/PBiCGStab/PBiCGStab.C at line 193.\n\n"
            "FOAM exiting\n\n")
        a = parse_log(a_path)
        if not a["fatal"]:
            refuse("PLANT fatal(a): a log carrying a genuine `--> FOAM FATAL ERROR` "
                   "block and `FOAM exiting` was read as NOT fatal; the reader "
                   "cannot see the failure it exists to see")

        # (b) POSITIVE: a signal handler that actually FIRED, with its stack trace
        # and the shell's own message on a line of its own.
        b_path = td / "plant_log_sigfpe.run"
        b_path.write_text(
            prologue + body +
            "#0  Foam::error::printStack(Foam::Ostream&) at ??:?\n"
            "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"
            "#2  ? in /lib/x86_64-linux-gnu/libc.so.6\n"
            "#3  Foam::divide(Foam::Field<double>&) at ??:?\n"
            "Floating point exception (core dumped)\n")
        b = parse_log(b_path)
        if not b["fatal"]:
            refuse("PLANT fatal(b): a log carrying `Foam::sigFpe::sigHandler`, a "
                   "printed stack and the shell's own `Floating point exception "
                   "(core dumped)` was read as NOT fatal")

        # (c) NEGATIVE -- the direction the frozen clause failed.  A CLEAN log
        # carrying OpenFOAM's `trapFpe:` banner VERBATIM must read NOT fatal.
        c_path = td / "control_log_clean_banner.run"
        c_path.write_text(prologue + body + "End\n")
        if FPE_BANNER not in c_path.read_text():
            refuse("PLANT fatal(c): the banner is not in the file ON DISK that the "
                   "reader was handed; the negative direction would prove nothing")
        c = parse_log(c_path)
        if c["absent"] or not c["end"]:
            refuse("PLANT fatal(c): the control file was not read as a present log "
                   "carrying an `End` line (absent=%r end=%r); the reader never saw "
                   "it, so its NOT-fatal would be a blind spot" % (c["absent"], c["end"]))
        if c["fatal"]:
            refuse("PLANT fatal(c): a CLEAN log whose only match is OpenFOAM's own "
                   "startup banner -- %r -- was read as FATAL. A detector that "
                   "cannot return NOT-fatal is a constant, and a constant grades "
                   "every level NOT A RESULT whatever the physics says."
                   % FPE_BANNER.strip())
        return a["fatal"], b["fatal"], c["fatal"]


# --------------------------------------------------------------------------
# strict completion, per level.  PHYSICS clauses refuse; INFRASTRUCTURE clauses
# are named and recorded (L-342: bookkeeping never voids physics).
# --------------------------------------------------------------------------
def completion(case, end, ncells):
    case = Path(case)
    phys, infra = [], []

    rcp = case / "rc.txt"
    if not rcp.is_file():
        phys.append("P1 rc: %s absent" % rcp)
    else:
        rc = rcp.read_text().strip()
        if rc != "0":
            phys.append("P1 rc: solver rc = %s (a non-zero rc is a finding)" % rc)

    log = parse_log(case / "log.run")
    if log["absent"]:
        phys.append("P2 End: %s does not exist; the level has no solver log, so it "
                    "is an incomplete level and rule 5 step 1 applies"
                    % (case / "log.run"))
    elif not log["end"]:
        phys.append("P2 End: log.run holds no `End` line")
    if log["fatal"]:
        phys.append("P3 fatal: log.run holds a FOAM FATAL / FPE / signal line")

    times = sorted((c.name for c in case.iterdir()
                    if c.is_dir() and TIME_DIR.match(c.name)), key=float)
    if not times:
        phys.append("P4 time dirs: none")
    elif float(times[-1]) != float(end):
        phys.append("P4 last time: %s, registered endTime %s" % (times[-1], end))

    d = case / str(end)
    need = list(REQ_FIELDS) + [GRADP_FILE]
    missing = [f for f in need if not (d / f).is_file()]
    if missing:
        phys.append("P5 fields at endTime: missing %r" % missing)

    marker = case / AGE_MARKER
    if not marker.is_file():
        phys.append("P6 age guard: marker %s absent" % marker)
    elif not missing:
        t0 = marker.stat().st_mtime
        stale = [f for f in need if (d / f).stat().st_mtime <= t0]
        if stale:
            phys.append("P6 age guard: %r at endTime are NOT strictly newer than %s; "
                        "they cannot be the answer this run produced"
                        % (stale, AGE_MARKER))

    if not log["absent"] and log["exec_count"] != int(end):
        phys.append("P7 ExecutionTime lines: %d, registered endTime %d. This is a "
                    "HARD EQUALITY. If the cause is a solver that prints extra "
                    "lines it is triaged by the supervisor, never reclassified "
                    "here and never granted a tolerance."
                    % (log["exec_count"], int(end)))

    cm = case / "log.checkMesh"
    if not cm.is_file() or "Mesh OK" not in cm.read_text(errors="replace"):
        infra.append("I1 checkMesh: log absent or not `Mesh OK`")
    mt = case / "mem_time.txt"
    if not mt.is_file() or "Maximum resident set size" not in mt.read_text(errors="replace"):
        infra.append("I2 MaxRSS: no /usr/bin/time -v reading recorded")
    if not (case / "wall_s.txt").is_file():
        infra.append("I3 wall_s: not recorded; the cost calibration has no actual")
    for f in ("V", "wallShearStress", "yPlus"):
        if not (d / f).is_file():
            infra.append("I4 postProcessing: %s absent at endTime (the secondaries "
                         "that need it become NOT A RESULT; the primary does not "
                         "need it)" % f)
    if log["libs_warning"]:
        infra.append("I5 libs: the solver could not load a library named in the "
                     "shipped controlDict. The entry is kept, never deleted to tidy "
                     "a case (standing rule 14); the loader warns and continues.")
    return phys, infra, log


def iterative(log, end):
    fails, diag = [], {}
    for name in RES_REQUIRED:
        if name not in log["final_res"]:
            fails.append("IC1 residual: no `Solving for %s` in the final Time block"
                         % name)
        elif log["final_res"][name] > RES_MAX[name]:
            fails.append("IC1 residual: %s final initial-residual %.3e > registered "
                         "%.0e" % (name, log["final_res"][name], RES_MAX[name]))
    for name in RES_DIAGNOSTIC:
        diag[name] = log["final_res"].get(name)
    g = log["gradP_hist"]
    if len(g) < 10:
        fails.append("IC2 plateau: only %d gradP prints in the log" % len(g))
    else:
        ntail = max(2, int(len(g) * PLATEAU_TAIL_FRAC))
        tail = g[-ntail:]
        ge = g[-1]
        if ge == 0.0:
            fails.append("IC2 plateau: the final gradP is exactly zero")
        else:
            dev = max(abs(x - ge) for x in tail) / abs(ge)
            if dev > PLATEAU_RTOL:
                fails.append("IC2 plateau: over the final %d of %d gradP prints the "
                             "value moves %.3e relative, registered ceiling %.0e"
                             % (ntail, len(g), dev, PLATEAU_RTOL))
    return fails, diag


# --------------------------------------------------------------------------
# Roache.  The monotone branch is the ONLY branch that reaches p, f_ext or GCI.
# --------------------------------------------------------------------------
def classify(f_coarse, f_med, f_fine, floor_mode, floor):
    """Returns (label, R, eps21, eps32).  Roache indices: 1=fine, 2=med, 3=coarse."""
    e21 = f_fine - f_med
    e32 = f_med - f_coarse
    fl = floor * abs(f_fine) if floor_mode == "rel" else floor
    small21, small32 = abs(e21) < fl, abs(e32) < fl
    if small21 and small32:
        return "EXACT", None, e21, e32
    if small21 or small32:
        return "STAGNANT", None, e21, e32
    R = e21 / e32
    if R < 0.0:
        return "OSCILLATORY", R, e21, e32
    if R >= 1.0:
        return "DIVERGENT", R, e21, e32
    return "CONVERGING", R, e21, e32


def roache(f_coarse, f_med, f_fine, floor_mode, floor):
    label, R, e21, e32 = classify(f_coarse, f_med, f_fine, floor_mode, floor)
    out = {"label": label, "R": R, "eps21": e21, "eps32": e32,
           "p": None, "f_ext": None, "gci_pct": None}
    if label != "CONVERGING":
        # Standing rule 5: no GCI is computed, let alone printed, off the
        # monotone branch.  This return is the enforcement.
        return out
    if R21 != R32:
        refuse("ROACHE: this comparator is frozen at constant r; r21=%g r32=%g"
               % (R21, R32))
    p = math.log(abs(e32 / e21)) / math.log(R21)
    denom = R21 ** p - 1.0
    if denom <= 0.0:
        refuse("ROACHE: r^p - 1 = %g is not positive; the extrapolation is undefined"
               % denom)
    if f_fine == 0.0:
        refuse("ROACHE: the fine-grid value is exactly zero; a relative GCI is "
               "undefined")
    out.update(p=p, f_ext=f_fine + e21 / denom,
               gci_pct=100.0 * FS * abs(e21 / f_fine) / denom)
    return out


def verdict_for(res, p_lo, p_hi, gci_max):
    if res["label"] != "CONVERGING":
        return "NOT A RESULT"
    if not (p_lo <= res["p"] <= p_hi):
        return "GATE FAIL"
    if res["gci_pct"] > gci_max:
        return "GATE FAIL"
    return "PASS"


def say(verdict):
    """No verdict leaves this instrument that is not one of the fixed six."""
    if verdict not in VERDICTS:
        refuse("VOCABULARY: %r is not one of the fixed six verdicts %r. Standing "
               "rule 1 admits no synonym and no hedge." % (verdict, VERDICTS))
    return verdict


# --------------------------------------------------------------------------
# grading
# --------------------------------------------------------------------------
def grade(run_root=RUN_ROOT):
    no_assert_control()
    run_root = Path(run_root)
    if not run_root.is_dir():
        refuse("RUN-ROOT: %s does not exist; there is nothing to grade" % run_root)
    tmp = tempfile.mkdtemp(prefix="g2grade_")

    print("=" * 78)
    print("G2 GRID TRIPLE -- square duct AR_1_Ret_360, comparator")
    print("  run root : %s" % run_root)
    print("  D = %d  refinement is applied in y and z; the single streamwise cell"
          % D_SPATIAL)
    print("        sits between MATCHED CYCLIC patches, so d/dx is identically zero")
    print("        over one cell and x carries no discretisation. h = (A/N)^(1/2).")
    print("  r21 = %.4f   r32 = %.4f   Fs = %.2f" % (R21, R32, FS))
    print("=" * 78)

    # ---- reconstruction control ------------------------------------------
    print("\n[RECONSTRUCTION CONTROL]")
    man_path = run_root / "STAGING_MANIFEST_G2.json"
    if not man_path.is_file():
        refuse("RECONSTRUCTION: %s absent; the stager's proof that the constructed "
               "dictionary reproduces the SHIPPED mesh is not on disk" % man_path)
    man = json.loads(man_path.read_text())
    rec = man.get("reconstruction_control", {})
    dev = rec.get("max_point_deviation_m")
    if dev is None:
        refuse("RECONSTRUCTION: the manifest carries no max_point_deviation_m")
    if dev > 1e-9:
        refuse("RECONSTRUCTION: the manifest records a max point deviation of %.4e m "
               "against the shipped mesh; the geometry was not derived" % dev)
    print("  constructed dictionary at the shipped resolution regenerates the "
          "shipped\n  mesh to %.3e m (%d points)  VERIFIED from the staging manifest"
          % (dev, rec.get("npoints", -1)))

    # ---- refinement-family control ---------------------------------------
    print("\n[FAMILY CONTROL]")
    dicts, counts = {}, {}
    for name, ncells, end in LEVELS:
        bmd = run_root / name / "system/blockMeshDict"
        own = run_root / name / "constant/polyMesh/owner"
        if not bmd.is_file():
            refuse("FAMILY: %s absent" % bmd)
        if not own.is_file():
            refuse("FAMILY: %s absent" % own)
        dicts[name] = bmd.read_text()
        m = re.search(r"nCells:\s*(\d+)", own.read_text(errors="replace")[:4000])
        if m is None:
            refuse("FAMILY: %s carries no nCells note" % own)
        counts[name] = int(m.group(1))
        if counts[name] != ncells:
            refuse("FAMILY: %s meshed to %d cells, registered %d"
                   % (name, counts[name], ncells))

    def nonhex(t):
        return "\n".join(ln for ln in t.split("\n")
                         if not ln.lstrip().startswith("hex ")).encode()

    def verts(t):
        m = re.search(r"(?m)^vertices\n\(\n.*?^\);\n", t, re.S)
        if m is None:
            refuse("FAMILY: a dictionary has no vertices block")
        return m.group(0).encode()

    ref = LEVELS[0][0]
    for name, _n, _e in LEVELS[1:]:
        if verts(dicts[name]) != verts(dicts[ref]):
            refuse("FAMILY: the vertices block of %s differs from %s BYTE-WISE. This "
                   "is the alpha_10_9000_{2024,3036,4048} shape: three directories "
                   "that look like a refinement family and are three GEOMETRIES "
                   "(measured: nCells 15600 for all three, three different vertices "
                   "sha256)." % (name, ref))
        if nonhex(dicts[name]) != nonhex(dicts[ref]):
            refuse("FAMILY: %s differs from %s outside the single hex block line"
                   % (name, ref))
    cs = [counts[n] for n, _x, _y in LEVELS]
    if len(set(cs)) != 3:
        refuse("FAMILY: the three cell counts %r are not distinct" % (cs,))
    if cs[1] != 4 * cs[0] or cs[2] != 4 * cs[1]:
        refuse("FAMILY: cell counts %r are not in the registered 1:4:16 ratio" % (cs,))
    print("  vertices block byte-identical across L1/L2/L3          VERIFIED")
    print("  all bytes outside the single hex line byte-identical   VERIFIED")
    print("  nCells %d / %d / %d -- distinct, exact 1:4:16          VERIFIED"
          % tuple(cs))

    # ---- completion + iterative convergence ------------------------------
    print("\n[COMPLETION AND ITERATIVE CONVERGENCE]")
    infra_all, blocked, logs, diags = [], [], {}, {}
    for name, ncells, end in LEVELS:
        case = run_root / name
        phys, infra, log = completion(case, end, ncells)
        logs[name] = log
        it, diag = (iterative(log, end) if not phys else ([], {}))
        diags[name] = diag
        infra_all += ["%s %s" % (name, x) for x in infra]
        if phys or it:
            blocked.append((name, phys + it))
            print("  %s  REFUSED" % name)
            for x in phys + it:
                print("      %s" % x)
        else:
            print("  %s  complete: rc=0, End, last time == %d, fields present, age "
                  "guard held,\n        ExecutionTime lines == %d (hard equality), "
                  "Ux/k/omega below registry,\n        gradP plateaued within %.0e"
                  % (name, end, end, PLATEAU_RTOL))
            print("        DIAGNOSTIC, ungated by design: final p = %s, Uy = %s, "
                  "Uz = %s\n        (a linear eddy-viscosity model makes no secondary "
                  "flow in a straight\n        duct, so these residuals are "
                  "normalised by machine noise and never fall)"
                  % tuple("%.3e" % diag[k] if diag.get(k) is not None else "absent"
                          for k in RES_DIAGNOSTIC))
    for x in infra_all:
        print("  INFRASTRUCTURE DEFECT: %s" % x)

    if blocked:
        print("\n[VERDICT]")
        print("  RUNG VERDICT: %s" % say("NOT A RESULT"))
        print("  Reason: standing rule 5 step 1 -- a level that is not complete or "
              "not\n  iteratively converged makes the triple NOT A RESULT whatever "
              "any number\n  says.  No Roache arithmetic was performed.")
        return 2

    # ---- planted controls -------------------------------------------------
    print("\n[PLANTED CONTROLS -- rule 3, each round-tripping a real file]")
    fine, fine_n, fine_end = LEVELS[-1]
    fine_case = run_root / fine
    geom = read_mesh_geometry(fine_case)
    truth, seen = planted_control_gradP(fine_case / str(fine_end) / GRADP_FILE, tmp)
    print("  gradP  : plant %.6e written to disk and read back %.6e by the SAME "
          "reader;\n           the unplanted file reads %.9g, so the reader is not a "
          "constant" % (PLANT_GRADP, seen, truth))
    base, vtot = planted_control_Kint(fine_case, fine_end, fine_n, tmp)
    print("  Kint   : uniform-k closed form and a single-cell plant at a known index "
          "both\n           recovered exactly; sum(V) = %.9e against the closed-form "
          "%.9e" % (vtot, DOMAIN_VOLUME))
    tw = planted_control_tauw(geom, tmp)
    print("  tauwint: uniform-shear closed form and a single-face plant both "
          "recovered\n           exactly (%.9e); a short face list REFUSED" % tw)
    fa, fb, fc = planted_control_fatal()
    print("  fatal  : a genuine `--> FOAM FATAL ERROR` block reads %r and a fired "
          "sigFpe\n           handler with its stack reads %r, while a CLEAN log "
          "carrying\n           OpenFOAM's `trapFpe:` banner verbatim reads %r -- "
          "the reader\n           is a detector, not a constant" % (fa, fb, fc))

    # ---- functionals ------------------------------------------------------
    print("\n[FUNCTIONALS]")
    vals = {k: {} for k, *_r in FUNCTIONALS}
    alarms = []
    for name, ncells, end in LEVELS:
        case = run_root / name
        g = f_gradP(case, end)
        lg = logs[name]["gradP_hist"][-1]
        if abs(g - lg) > DISK_VS_LOG_RTOL * abs(g):
            refuse("IC3: at %s the disk gradP %.12g and the last log print %.12g "
                   "differ by %.3e relative, registered ceiling %.0e. Two "
                   "independent reads of one quantity must agree."
                   % (name, g, lg, abs(g - lg) / abs(g), DISK_VS_LOG_RTOL))
        vals["gradP"][name] = g
        vals["Kint"][name] = f_Kint(case, end, ncells)[0]
        vals["tauwint"][name] = f_tauwint(case, end, read_mesh_geometry(case))[0]
        print("  %s  gradP = %.12g   Kint = %.9e   tauwint = %.9e"
              % (name, vals["gradP"][name], vals["Kint"][name], vals["tauwint"][name]))
        lhs = vals["gradP"][name] * DOMAIN_VOLUME
        rhs = vals["tauwint"][name]
        if lhs == 0.0:
            refuse("MOMENTUM BALANCE: gradP * V is exactly zero at %s; the relative "
                   "disagreement is undefined" % name)
        rel = abs(lhs - rhs) / abs(lhs)
        fired = rel > MOMENTUM_ALARM_RTOL
        print("       momentum balance: gradP * V = %.9e against the integrated wall "
              "shear\n       %.9e -- disagreement %.4f %% (registered ALARM LEVEL "
              "%.1f %%)%s"
              % (lhs, rhs, 100.0 * rel, 100.0 * MOMENTUM_ALARM_RTOL,
                 "   <<< ALARM" if fired else ""))
        if fired:
            alarms.append((name, rel))

    # ---- Roache -----------------------------------------------------------
    print("\n[ROACHE TRIPLES]")
    rows, headline = {}, None
    for key, label, unit, p_lo, p_hi, gci_max, fmode, floor in FUNCTIONALS:
        fc, fm, ff = (vals[key][LEVELS[0][0]], vals[key][LEVELS[1][0]],
                      vals[key][LEVELS[2][0]])
        res = roache(fc, fm, ff, fmode, floor)
        v = say(verdict_for(res, p_lo, p_hi, gci_max))
        rows[key] = (res, v)
        print("  %s  [%s]" % (label, unit))
        print("      L1 = %.12g   L2 = %.12g   L3 = %.12g" % (fc, fm, ff))
        print("      eps21 = %.6e   eps32 = %.6e   R = %s   triple = %s"
              % (res["eps21"], res["eps32"],
                 "%.6f" % res["R"] if res["R"] is not None else "undefined",
                 res["label"]))
        if res["label"] == "CONVERGING":
            print("      p = %.6f  (band [%.1f, %.1f])   f_ext = %.12g   "
                  "GCI_fine = %.4f %%  (ceiling %.1f %%)"
                  % (res["p"], p_lo, p_hi, res["f_ext"], res["gci_pct"], gci_max))
            if not (p_lo <= res["p"] <= p_hi):
                print(P_BAND_CANDIDATE_CAUSES)
        else:
            print("      p and GCI are NOT computed: standing rule 5 forbids quoting "
                  "an order or\n      a GCI when the three values are not monotone.")
        print("      VERDICT: %s" % v)
        if key == "gradP":
            headline = v

    print("\n[VERDICT]")
    print("  RUNG VERDICT: %s" % say(headline))
    print("  The headline is the PRIMARY's. The secondaries carry their own verdicts "
          "and\n  never change it.")
    if alarms:
        print("\n  MOMENTUM-BALANCE ALARM at %s"
              % ", ".join("%s (%.4f %%)" % (nm, 100.0 * r) for nm, r in alarms))
        print("  The registered ALARM LEVEL of %.1f %% is exceeded. This is an ALARM "
              "and NOT A\n  GATE: it has changed no verdict above, it appears in no "
              "verdict mapping, and\n  it cannot make anything a GATE FAIL. What it "
              "means is that **THE RUNG IS NOT\n  BELIEVED PENDING SUPERVISOR "
              "TRIAGE** -- the verdict stands as computed and is\n  read as "
              "unconfirmed until the cause is found."
              % (100.0 * MOMENTUM_ALARM_RTOL))
    else:
        print("  momentum-balance alarm: NOT FIRED at any level (registered level "
              "%.1f %%).\n  The measured disagreements above are the reading this "
              "rung owes a successor,\n  which may register a real threshold from "
              "them instead of from an argument."
              % (100.0 * MOMENTUM_ALARM_RTOL))
    for x in infra_all:
        print("  INFRASTRUCTURE DEFECT carried into the record: %s" % x)
    print("\n[COST CALIBRATION -- owed at completion, standing rule 12]")
    for name, _n, _e in LEVELS:
        w = run_root / name / "wall_s.txt"
        print("    %s actual wall_s = %s (ranks 1, so core-min = wall_s/60)"
              % (name, w.read_text().strip() if w.is_file() else "UNRECORDED"))
    print("    The ratio actual/predicted, the attribution of the gap and the named "
          "waste\n    land as a row in docs/COST_CALIBRATION.md. A completion report "
          "without that\n    comparison is incomplete.")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if headline == "PASS" else 1


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def _must_refuse(label, fn):
    try:
        fn()
    except Refusal as e:
        print("  REFUSED as registered: %s\n      %s"
              % (label, str(e).split("\n")[0][:150]))
        return True
    print("  CONTROL DID NOT FIRE: %s" % label)
    return False


def selftest():
    ok = True
    print("G2 comparator selftest")
    planted, own = no_assert_control()
    print("  L-332: counter saw %d planted assert, this module holds %d"
          % (planted, own))
    tmp = Path(tempfile.mkdtemp(prefix="g2self_"))

    print("[Roache classification -- the branch table]")
    cases = (
        ("CONVERGING", 10.0, 6.0, 4.0),
        ("DIVERGENT", 4.0, 6.0, 10.0),
        ("OSCILLATORY", 10.0, 4.0, 6.0),
    )
    for want, fc, fm, ff in cases:
        got = classify(fc, fm, ff, "rel", 1e-9)[0]
        if got != want:
            print("  FAIL: (%g,%g,%g) classified %s, expected %s" % (fc, fm, ff, got, want))
            ok = False
        else:
            print("  (%g, %g, %g) -> %s" % (fc, fm, ff, got))
    if classify(1.0, 1.0, 1.0, "rel", 1e-3)[0] != "EXACT":
        print("  FAIL: three equal values are not EXACT")
        ok = False
    else:
        print("  three equal values -> EXACT")
    if classify(2.0, 1.0, 1.0, "rel", 1e-3)[0] != "STAGNANT":
        print("  FAIL: one difference below the floor is not STAGNANT")
        ok = False
    else:
        print("  one difference below the floor -> STAGNANT")

    print("[no GCI off the monotone branch]")
    for want, fc, fm, ff in cases[1:] + (("EXACT", 1.0, 1.0, 1.0),
                                         ("STAGNANT", 2.0, 1.0, 1.0)):
        r = roache(fc, fm, ff, "rel", 1e-3)
        if r["gci_pct"] is not None or r["p"] is not None or r["f_ext"] is not None:
            print("  FAIL: %s produced p/f_ext/GCI" % want)
            ok = False
    print("  DIVERGENT, OSCILLATORY, EXACT and STAGNANT all return with p, f_ext "
          "and GCI\n  still None -- the arithmetic is never reached")
    r = roache(10.0, 6.0, 4.0, "rel", 1e-9)
    p_exact = math.log(4.0 / 2.0) / math.log(2.0)
    if abs(r["p"] - p_exact) > 1e-12:
        print("  FAIL: p = %.12g, closed form %.12g" % (r["p"], p_exact))
        ok = False
    else:
        print("  CONVERGING: p = %.6f matches the closed form at r = 2" % r["p"])

    print("[momentum-balance ALARM -- an alarm, not a gate]")
    for lhs, rhs, want in ((1.0, 1.0 + 0.049, False), (1.0, 1.0 + 0.051, True),
                           (1.0, 1.0 - 0.051, True), (1.0, 1.0, False)):
        rel = abs(lhs - rhs) / abs(lhs)
        fired = rel > MOMENTUM_ALARM_RTOL
        if fired != want:
            print("  FAIL: %.4f disagreement fired=%s, expected %s"
                  % (rel, fired, want))
            ok = False
    print("  fires above %.1f %% and stays silent below it, in both signs"
          % (100.0 * MOMENTUM_ALARM_RTOL))
    # THE ALARM CANNOT CHANGE A VERDICT, and that is checked structurally rather
    # than promised: the three verdict-producing functions must not reference the
    # alarm constant at all.  The scanner is first shown able to FIND the name.
    tree = ast.parse(Path(__file__).read_text())
    fns = {f.name: f for f in ast.walk(tree)
           if isinstance(f, ast.FunctionDef)}
    def names_in(fn):
        return {x.id for x in ast.walk(fn) if isinstance(x, ast.Name)}
    seen_somewhere = any("MOMENTUM_ALARM_RTOL" in names_in(f) for f in fns.values())
    if not seen_somewhere:
        print("  FAIL: the scanner cannot find MOMENTUM_ALARM_RTOL anywhere; its "
              "absence from\n        the verdict functions would be a blind spot, "
              "not a reading")
        ok = False
    else:
        leaked = [nm for nm in ("classify", "roache", "verdict_for", "say")
                  if nm in fns and "MOMENTUM_ALARM_RTOL" in names_in(fns[nm])]
        if leaked:
            print("  FAIL: the alarm constant is referenced inside %r -- it is "
                  "acting as a gate" % leaked)
            ok = False
        else:
            print("  classify, roache, verdict_for and say reference the alarm "
                  "constant ZERO times\n  (the scanner was first shown able to find "
                  "it elsewhere) -- it is structurally\n  incapable of changing a "
                  "verdict")

    print("[registered candidate causes for a p outside the band]")
    for frag in ("THE SCHEME", "NON-SYSTEMATIC WALL-CELL REFINEMENT",
                 "1.9492", "1.9748", "5.3.1"):
        if frag not in P_BAND_CANDIDATE_CAUSES:
            print("  FAIL: the registered text does not name %r" % frag)
            ok = False
    print("  both causes named, with the measured 1.9492 / 1.9748 ratios, ready "
          "before any\n  value exists")

    print("[verdict vocabulary]")
    ok &= _must_refuse("a synonym for a verdict", lambda: say("roughly converged"))
    ok &= _must_refuse("a lower-case verdict", lambda: say("pass"))
    for v in VERDICTS:
        if say(v) != v:
            print("  FAIL: %r was not passed through" % v)
            ok = False
    print("  all six fixed verdicts pass through unchanged")

    print("[fatal reader -- planted control, BOTH directions (rule 3)]")
    fa, fb, fc = planted_control_fatal()
    print("  a genuine `--> FOAM FATAL ERROR` block + `FOAM exiting`  fatal=%r" % fa)
    print("  a fired `Foam::sigFpe::sigHandler` with a printed stack  fatal=%r" % fb)
    print("  a CLEAN log carrying the `trapFpe:` banner verbatim      fatal=%r" % fc)
    ok &= _must_refuse(
        "the FROZEN fatal expression, which fires on OpenFOAM's own startup banner",
        _blind_fatal)

    print("[readers and planted controls, on a REAL shipped mesh]")
    if not SRC_CASE.is_dir():
        print("  SKIPPED: the source case is not on disk")
    else:
        geom = read_mesh_geometry(SRC_CASE)
        pts, faces, patches = geom
        for patch, closed in WALL_AREA.items():
            got = sum(face_areas(pts, faces, patches, patch))
            if abs(got - closed) > WALL_AREA_RTOL * closed:
                print("  FAIL: patch %s area %.9e, closed form %.9e" % (patch, got, closed))
                ok = False
            else:
                print("  patch %-9s area %.9e m2 == the closed form %.9e m2"
                      % (patch, got, closed))
        tw = planted_control_tauw(geom, tmp)
        print("  tauw plant round-tripped through the real reader: %.9e" % tw)
        # blind control: a reader that cannot see the plant must be caught
        ok &= _must_refuse(
            "a shear reader whose per-face plant is invisible",
            lambda: _blind_tauw(geom, tmp))
        # gradP plant, round-tripping a REAL file from a run already on disk
        real = tmp / "meanVelocity1Properties"
        real.write_text("FoamFile\n{\n    version 2.0;\n    object "
                        "meanVelocity1Properties;\n}\n\ngradient        53007.9;\n")
        truth, seen = planted_control_gradP(real, tmp)
        if abs(truth - 53007.9) > 1e-9 or abs(seen - PLANT_GRADP) > 1e-15:
            print("  FAIL: gradP plant round trip returned (%r, %r)" % (truth, seen))
            ok = False
        else:
            print("  gradP plant: unplanted file reads %.9g, planted file reads %.6e"
                  % (truth, seen))
        ok &= _must_refuse(
            "a gradP file whose value equals the plant (a constant, not a reader)",
            lambda: planted_control_gradP(_const_plant(tmp), tmp))
        ok &= _must_refuse("a gradP file with no gradient entry",
                           lambda: read_gradP_disk(_no_gradient(tmp)))

    print("[strict completion, mutated]")
    case = tmp / "case"
    _synth_run(case, end=10, ncells=4)
    phys, infra, log = completion(case, 10, 4)
    if phys:
        print("  FAIL: a clean synthetic run was refused: %r" % phys)
        ok = False
    else:
        print("  a clean synthetic run passes all seven PHYSICS clauses")
    (case / "rc.txt").write_text("1\n")
    if not any(x.startswith("P1") for x in completion(case, 10, 4)[0]):
        print("  FAIL: rc = 1 was not caught")
        ok = False
    else:
        print("  rc = 1                              CAUGHT (P1)")
    (case / "rc.txt").write_text("0\n")
    txt = (case / "log.run").read_text()
    (case / "log.run").write_text(txt.replace("\nEnd\n", "\n"))
    if not any(x.startswith("P2") for x in completion(case, 10, 4)[0]):
        print("  FAIL: a missing End line was not caught")
        ok = False
    else:
        print("  no End line                         CAUGHT (P2)")
    (case / "log.run").write_text(txt.replace("ExecutionTime = 1 s", "", 1))
    got = completion(case, 10, 4)[0]
    if not any(x.startswith("P7") for x in got):
        print("  FAIL: ExecutionTime count 9 against endTime 10 was not caught")
        ok = False
    else:
        print("  ExecutionTime count 9 vs endTime 10 CAUGHT (P7, hard equality, no "
              "tolerance)")
    (case / "log.run").write_text(txt)
    os.utime(case / "0/U", None)
    if not any(x.startswith("P6") for x in completion(case, 10, 4)[0]):
        print("  FAIL: an age marker newer than the answer was not caught")
        ok = False
    else:
        print("  0/U touched AFTER the fields         CAUGHT (P6 age guard)")

    print("[iterative convergence]")
    _synth_run(case2 := tmp / "case2", end=10, ncells=4)
    log = parse_log(case2 / "log.run")
    fails, diag = iterative(log, 10)
    if fails:
        print("  FAIL: a clean synthetic log was refused: %r" % fails)
        ok = False
    else:
        print("  a clean synthetic log passes IC1 and IC2; p/Uy/Uz recorded as "
              "diagnostics %r"
              % {k: ("%.3g" % v if v is not None else None) for k, v in diag.items()})
    bad = (case2 / "log.run").read_text().replace(
        "Solving for k, Initial residual = 1e-09", "Solving for k, Initial residual = 1")
    (case2 / "log.run").write_text(bad)
    if not any(x.startswith("IC1") for x in iterative(parse_log(case2 / "log.run"), 10)[0]):
        print("  FAIL: a k residual of 1 was not caught")
        ok = False
    else:
        print("  final k residual 1.0                CAUGHT (IC1)")
    _synth_run(case3 := tmp / "case3", end=10, ncells=4, wobble=1e-2)
    if not any(x.startswith("IC2") for x in iterative(parse_log(case3 / "log.run"), 10)[0]):
        print("  FAIL: a gradP wobble inside the IC2 window was not caught")
        ok = False
    else:
        print("  gradP wobbling 1e-2 in the tail     CAUGHT (IC2 plateau)")

    print("[run root]")
    ok &= _must_refuse("an absent run root", lambda: grade(tmp / "nope"))

    shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def _blind_fatal():
    """The FROZEN fatal expression, restored for exactly one call: the control
    MUST refuse.  This is the `_blind_tauw` pattern applied to the fatal channel.
    The expression installed here is the second half of the frozen `and` at
    71654cec, which is what actually decided the value (the first half added only
    `--> FOAM Warning : Could not load`, an alternative that could never fire
    alone).  If `planted_control_fatal` does not refuse against it, the control is
    not a control and the repair is unproven.
    """
    global FATAL_RE
    good = FATAL_RE
    FATAL_RE = re.compile(r"FOAM FATAL|Floating point exception|signal \(")
    try:
        planted_control_fatal()
    finally:
        FATAL_RE = good


def _blind_tauw(geom, tmp):
    """A reader that returns zero for every face: the plant must be invisible."""
    pts, faces, patches = geom
    areas = face_areas(pts, faces, patches, "wallTop")
    got = sum(0.0 * a for a in areas)
    want = PLANT_TAU * sum(areas)
    if abs(got - want) > 1e-9 * abs(want):
        refuse("BLIND CONTROL: a reader returning 0.0 for every face gives %.9e "
               "against the planted closed form %.9e -- the control fires, so its "
               "zero on the real reader is a reading" % (got, want))


def _const_plant(tmp):
    p = Path(tmp) / "const_meanVelocity1Properties"
    # the same VALUE as the plant, written in a different REPRESENTATION, so the
    # substitution genuinely rewrites bytes and the inverse control is the clause
    # that fires rather than the "nothing changed" clause
    p.write_text("FoamFile\n{\n    object x;\n}\n\ngradient        %.12f;\n"
                 % PLANT_GRADP)
    return p


def _no_gradient(tmp):
    p = Path(tmp) / "empty_meanVelocity1Properties"
    p.write_text("FoamFile\n{\n    object x;\n}\n\nUbar (1 0 0);\n")
    return p


def _synth_run(case, end, ncells, wobble=0.0):
    """A minimal, complete synthetic run tree, used ONLY by the selftest."""
    case = Path(case)
    shutil.rmtree(case, ignore_errors=True)
    (case / "0").mkdir(parents=True)
    (case / "0/U").write_text("synthetic age marker\n")
    d = case / str(end)
    (d / "uniform").mkdir(parents=True)
    for f in REQ_FIELDS:
        (d / f).write_text("synthetic\n")
    (d / GRADP_FILE).write_text(
        "FoamFile\n{\n    object meanVelocity1Properties;\n}\n\n"
        "gradient        53007.9;\n")
    lines = []
    tail_start = end - max(2, int(end * PLATEAU_TAIL_FRAC)) + 1
    for i in range(1, end + 1):
        # the wobble is placed INSIDE the window IC2 measures -- the final 10 %% --
        # and never on the last iteration, whose value is IC2's reference
        g = 53007.9 * (1.0 + (wobble if tail_start <= i < end else 0.0))
        lines.append("Time = %d\n" % i)
        lines.append("DILUPBiCGStab:  Solving for Ux, Initial residual = 1e-14, "
                     "Final residual = 1e-16, No Iterations 1\n")
        lines.append("DILUPBiCGStab:  Solving for Uy, Initial residual = 0.31, "
                     "Final residual = 1e-3, No Iterations 1\n")
        lines.append("DILUPBiCGStab:  Solving for Uz, Initial residual = 0.42, "
                     "Final residual = 1e-3, No Iterations 1\n")
        lines.append("Pressure gradient source: uncorrected Ubar = 85.4, "
                     "pressure gradient = %.12g\n" % g)
        lines.append("GAMG:  Solving for p, Initial residual = 0.19, "
                     "Final residual = 1e-3, No Iterations 3\n")
        lines.append("DILUPBiCGStab:  Solving for omega, Initial residual = 1e-15, "
                     "Final residual = 1e-16, No Iterations 1\n")
        lines.append("DILUPBiCGStab:  Solving for k, Initial residual = 1e-09, "
                     "Final residual = 1e-11, No Iterations 1\n")
        lines.append("ExecutionTime = %d s  ClockTime = %d s\n\n" % (i, i))
    lines.append("End\n")
    (case / "log.run").write_text("".join(lines))
    (case / "rc.txt").write_text("0\n")
    (case / "wall_s.txt").write_text("1\n")
    (case / "log.checkMesh").write_text("Mesh OK.\n")
    (case / "mem_time.txt").write_text("\tMaximum resident set size (kbytes): 1\n")
    for f in ("V", "wallShearStress", "yPlus"):
        (d / f).write_text("synthetic\n")
    return case


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = RUN_ROOT
    for a in argv:
        if not a.startswith("-"):
            root = Path(a)
    return grade(root)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.exit(2)
