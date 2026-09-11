#!/usr/bin/env python3
"""analyse_t5e.py -- the T5e comparator.  IT RESTORES REGISTERED CLAUSE (1).

Registration: docs/campaigns/T-family/T5e_PREREGISTRATION.md.  Frozen with it.

===========================================================================
WHAT THIS FILE IS
===========================================================================
T5e re-grades artifacts that ALREADY EXIST -- the three completed T5b levels at
`verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}` -- and changes EXACTLY ONE
thing against `analyse_t5c.py`: it RESTORES the registered step (1) that
`analyse_t5b.py` dropped and whose number it reused, and which `analyse_t5c.py`
copied verbatim.  NO SOLVER RUNS.  NO NEW THRESHOLD IS REGISTERED.

THE DEFECT, MEASURED AND CITED, NOT INFERRED
--------------------------------------------
`T5_PREREGISTRATION.md:646` registers the order's step 1 as

    "1. any ladder level NOT CONVERGED -> NOT A RESULT;"

`analyse_t5b.py:654` is `def grade_row(...)`, its docstring at `:655` reads
"THE REGISTERED ORDER (T5 S7.5, rule 5), evaluated top to bottom", and its
step `(1)` at `:657` is the y+ gate, with the triple at `(2)`.  The registered
step 1 is absent and its number is taken.  `analyse_t5c.py:532-533` says so in
terms -- "VERBATIM analyse_t5b.py:654-710" -- and inherits the defect whole.

On 2026-09-10 the heat-transfer supervisor withdrew `T5c_RESULTS.md`'s `G2a`
`GATE FAIL` and its `GCI 4.3550 %` for this reason (that record's AMENDMENT 1).
This file is the instrument that reaches the same verdict by measurement.

===========================================================================
THE INSTRUMENT FOR CLAUSE (1) IS A CHECKPOINT FIELD-DELTA, NOT A RESIDUAL
===========================================================================
This is the trap in this rung and it is closed here explicitly.

`T5_PREREGISTRATION.md` S5.5 (lines 466-472), frozen before any T5 case
existed, registers VERBATIM:

    "**`residualControl` is not written** (L-141: in T1c a genuinely
     unconverged case sat at residual 4e-05, and in T3 the residual was again
     not the instrument)."

    "**CONVERGED** means: the largest change of any cell value of `T` in either
     region, and separately of `U` in the fluid, between the checkpoints at
     `endTime - 1000` and `endTime`, is at most **1e-6 of that field's range**."

So T5 registered its clause-(1) instrument AS A CHECKPOINT DELTA and EXPRESSLY
REJECTED the residual.  `gate_converged` in the frozen `analyse_t5.py:213` is a
RESIDUAL-SERIES predicate (sustained floor AND not growing).  IT IS NOT CARRIED
HERE, and the reason is a rule-2 reason, not a taste:

  (i)  it imports the instrument T5's own registration refuses;
  (ii) it has NO registered floor and NO registered sustain -- `analyse_t5.py`
       carries no CONV_FLOOR and no SUSTAIN constant, only the selftest
       literals 1e-6 and 2 -- so "carrying it verbatim" would in fact be
       REGISTERING A NEW THRESHOLD after the answer is known, which rule 2
       forbids;
  (iii) it is wired to nothing.  Its only callers in the frozen file are
       `selftest()` at :330-335 and `_drive_oneway_violation()` at :381.  There
       is no residual extractor and no production call site.

THE TOLERANCE USED HERE IS NOT TYPED INTO THIS FILE AS A CHOICE.  It is PARSED
OUT OF THE FROZEN REGISTRATION at grade time (`parse_registered_criterion`) and
this file REFUSES if the parsed value differs from CONV_REL_TOL.  Restoring the
clause therefore registers nothing new: the number is T5's own.

===========================================================================
RESIDUAL EVIDENCE IS **REPORTED, NEVER GATED**
===========================================================================
The residual trajectories corroborate the clause-(1) result and are printed, in
the T19/T19b idiom.  The family has litigated this in source before --
`T4:391` and `K0c:77` both argue that a residual is not convergence -- and
L-141 is the measured reason.  `residual_report()` returns a dict that NO gate
consults: `--selftest` proves it by reading this file's own bytes and requiring
that the returned name never appears in `gate_clause1`, `gate_yplus_t5e` or
`grade_row`, and by driving `grade_row` with two contradictory residual states
and requiring the identical verdict.  A REPORTED line that could gate is not
REPORTED (`GATING_REPORTING_RECLASSIFICATION_2026-09-03`).

===========================================================================
RULE 3 -- THE PLANTED CONTROL SITS ON THE CLAUSE-(1) READER
===========================================================================
That reader's entire job is to emit a delta.  A ZERO from it would be the exact
rule-3 failure, so it is never believed until it has been shown able to emit a
non-zero on the same bytes:

  C-1  SIGNAL      a single-cell spike PLANT_SPIKE is seen, AND THE ARGMAX IS
                   AT THE PLANTED CELL (VERIFICATION_CHARTER S2d.11.1 item A:
                   a max predicate that never asks where the max is, is a
                   rule-3 violation inside a rule-3 control).  The plant is
                   placed at a cell that is NOT the base argmax, and the arm
                   REFUSES if it is -- an anti-vacuity refusal.
  C-2  EXACTNESS   a constant offset moves the delta to an independently
                   computed closed form, to REL_EXACT; and the RANGE reader is
                   EXACTLY BLIND to it.  Two shapes, two readers (L-340).
  C-3  THE ZERO    a copy whose endTime bytes ARE the endTime-1000 bytes must
                   read back EXACTLY 0.0 -- and then, on those same bytes, a
                   planted spike must read back EXACTLY the spike.  This is the
                   planted zero itself: a zero from a reader shown, on the same
                   file, able to see a non-zero.

Every plant is written into a COPY in a scratch directory that is PROVEN to
resolve outside the case tree before anything is written.  The run tree is
never written.  Refusals are `refuse()` -> exit 2, NEVER a bare `assert`:
`python3 -O` strips asserts and a control that vanishes under an interpreter
flag is not a control.

===========================================================================
THE Y+ CHANGE IS T5c's, CARRIED UNCHANGED
===========================================================================
T5c moved the y+ LADDER clause from the point maximum `R_max` to the
area-weighted mean `R_area`, and left the SUBLAYER clause on `R_max`
(VERIFICATION_CHARTER S2d.11.2 binding condition 3).  T5e carries that and its
four binding conditions whole: the birth arms Y-1..Y-5 print before any row
grades; Y-3's anti-vacuity refusal is armed; the sublayer bound stays on the
point maximum; every graded row prints both statistics.  `YPLUS_TARGET`,
`YPLUS_TARGET_TOL` and `YPLUS_MAX` are NOT touched, and that carry-over is
ASSERTED at grade time against the frozen `analyse_t5b.py` AND the frozen
`analyse_t5c.py`, by sha256 of the disk bytes and by re-parsed literal.

FORWARD-ONLY ADOPTION HONOURED (`T5c_RESULTS.md` S5a): this grader's freeze
witnesses are FULL sha256 of the disk bytes, never a git blob SHA-1, because
L-450 records the freeze instrument as blind to the blob form.

Usage:
    analyse_t5e.py [--root DIR]     re-grade (default root: ../T5b_runs)
    analyse_t5e.py --selftest       synthetic controls only; reads no run tree
Exit 0 graded and every graded row PASS, 1 a graded row did not PASS,
2 refusal (a control failed, or an input is not what the registration names).
"""
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_t_family(*starts):
    """Locate `verification/runs/T-family` by walking up from this file's own
    directory and, failing that, from the working directory.

    WHY THIS IS NOT AN ENVIRONMENT VARIABLE: `--selftest` runs mutated and
    unmutated COPIES of this file from a scratch directory (with cwd set to the
    real T5e_runs), and those copies must still find the frozen predecessors
    they are asserted against.  An env override would do it -- and would also
    let anyone point a GRADING INSTRUMENT at a different tree, which is not a
    knob a comparator should own.  The search is deterministic, reads only the
    filesystem, and identifies the directory by the presence of the frozen
    predecessor itself rather than by name alone."""
    for s in starts:
        d = os.path.abspath(s)
        for _ in range(10):
            if os.path.isfile(os.path.join(d, "T5b_runs", "analyse_t5b.py")):
                return d
            nd = os.path.dirname(d)
            if nd == d:
                break
            d = nd
    return os.path.abspath(os.path.join(os.path.abspath(starts[0]), ".."))


T_FAMILY = _find_t_family(HERE, os.getcwd())
DEFAULT_ROOT = os.path.join(T_FAMILY, "T5b_runs")
T5_RUNS = os.path.join(T_FAMILY, "T5_runs")
REFERENCE = os.path.join(T5_RUNS, "T5_reference_primary.json")
FROZEN_T5B = os.path.join(T_FAMILY, "T5b_runs", "analyse_t5b.py")
FROZEN_T5C = os.path.join(T_FAMILY, "T5c_runs", "analyse_t5c.py")
REPO = os.path.abspath(os.path.join(T_FAMILY, "..", "..", ".."))
T5_REGISTRATION = os.path.join(REPO, "docs", "campaigns", "T-family",
                               "T5_PREREGISTRATION.md")

REGISTRATION = "docs/campaigns/T-family/T5e_PREREGISTRATION.md"

# ---------------------------------------------------------------------------
# FREEZE WITNESSES.  The supervisor sets the pins AT FREEZE; this file never
# sets them itself and never rewrites them.  `PIN-AT-FREEZE` is the unfrozen
# state and `run()` says so in words on every line it prints.
# ---------------------------------------------------------------------------
GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"
REGISTRATION_SHA256 = "PIN-AT-FREEZE"

# sha256 OF THE DISK BYTES of the two frozen predecessors, read 2026-09-10.
# NOT git blob SHA-1: L-450 records the freeze instrument as blind to that form
# and `T5c_RESULTS.md` S5a adopts full sha256 FORWARD-ONLY for every new grader.
FROZEN_T5B_SHA256 = "778f560edbd1cc1e50485d1973ccd56f040c84fff2c9da139a9ae165035155fc"
FROZEN_T5C_SHA256 = "50b484f0541cea52baea12e1058204f35b7922b40f7e75adf60bb71e13749f0b"

# sha256 of the four lines of T5_PREREGISTRATION.md that ARE the S5.5 criterion
# (lines 469-472 at HEAD 2026-09-10).  The CLAUSE is witnessed, not the whole
# file: T5_PREREGISTRATION.md lawfully carries appended dated amendments, so a
# whole-file witness would rot while the criterion itself did not move.
T5_CRITERION_SHA256 = "aeaf1987ad6ddae91ac81953eb98d31d3474318ab3a92684fc6646b2faa3c2ed"

VERDICT_PASS = "PASS"
VERDICT_FAIL = "GATE FAIL"
VERDICT_NAR = "NOT A RESULT"
VERDICT_REACHED = "GATE REACHED"
VERDICT_BLOCKED = "BLOCKED"
ROWCLASS_REPORTED = "REPORTED"          # D534: a ROW CLASS, never a verdict

# T5c section 7 condition (4), carried verbatim: printed beside EVERY row.
PRE_REPAIR_STATE = (
    "PRE-REPAIR STATE: NOT A RESULT (T5b y+ ladder clause on cube_front "
    "MAX = 2.310042 against bound 2.0)")
# T5e's own supersession note, printed beside every row.
SUPERSEDED_STATE = (
    "SUPERSEDES T5c_RESULTS.md: G2a was published GATE FAIL with GCI 4.3550 %, "
    "withdrawn 2026-09-10; every other T5c row was published NOT A RESULT")

LEVELS = ("c", "m", "f")
CASE_OF = {"c": "T5_CUBE_c", "m": "T5_CUBE_m", "f": "T5_CUBE_f"}

CELLS_REGISTERED = {"c": 52684, "m": 212942, "f": 882024}

FS = 1.25                        # Roache safety factor, registered
ENDTIME = 5000
REQUIRED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

# ---------------------------------------------------------------------------
# THE CARRIED-OVER THRESHOLDS.  Not one is new.  Asserted at grade time against
# BOTH frozen predecessors by assert_thresholds_carried_over(), never trusted.
# ---------------------------------------------------------------------------
YPLUS_WALLS = ("cube_front", "cube_top", "cube_rear",
               "cube_side_n", "floor", "roof")
YPLUS_MAX = 5.0                  # the edge of the viscous sublayer
YPLUS_TARGET = {"c": 2.6, "m": 1.6, "f": 1.0}
YPLUS_TARGET_TOL = 2.0

T_REF_K = 293.65                 # channel inlet air, T5 S7.1 INTERPRETATION 9
INTRINSIC_FLOOR_PCT = 1.7        # T5 S7.4 ambient ambiguity, carried unchanged

GRADED_H = {"G1a": "cube_front", "G2a": "cube_top", "G3a": "cube_rear"}
GRADED_T = {"G5a": "cube_front", "G5b": "cube_top", "G5c": "cube_rear"}
REPORTED_ROWS = ("G1", "G2", "G3", "G4", "R1", "R2", "R3")

G5_IDENTITY_MARGIN_K = 5.0
G5_BOUND_LO_C = 20.5
G5_BOUND_HI_C = 75.0

PLANT_OFFSET = 1.234e-03         # for MEAN / DELTA readers
PLANT_SPIKE = 9.876e+02          # for RANGE / MAX readers (L-340)

ARM_WALL = "cube_front"
ARM_LEVEL = "f"

Q95 = 0.95
Q50 = 0.50
REL_EXACT = 1e-9                 # T5c S6.2 Y-1/Y-3: "within 1e-9 relative"
REL_FACE = 1e-12                 # the per-face strengthening readback
Y3_MIN_SEPARATION = 0.01         # T5c S6.2 Y-3: "differ by > 1 %"
Y2_SEEN_FRACTION = 0.9           # T5c S6.2 Y-2: ">= 0.9 x spike"
Y2_BLIND_SLACK = 1.001           # T5c S6.2 Y-2: "no more than 1.001 x ..."

# ---------------------------------------------------------------------------
# CLAUSE (1) -- T5 S5.5, RESTORED.  NOT ONE OF THESE NUMBERS IS NEW.
# CONV_REL_TOL is CHECKED against the frozen registration's own text at grade
# time and this file REFUSES on a difference (parse_registered_criterion).
# CONV_CHECKPOINT_STRIDE is likewise parsed from `endTime - 1000`.
# ---------------------------------------------------------------------------
CONV_REL_TOL = 1e-6
CONV_CHECKPOINT_STRIDE = 1000
CONV_CHECKPOINT_HI = ENDTIME                          # endTime
CONV_CHECKPOINT_LO = ENDTIME - CONV_CHECKPOINT_STRIDE  # endTime - 1000
# (region, field) triples S5.5 names: "T in either region, and separately of U
# in the fluid".  `air` is the fluid region and `epoxy` the solid.
CONV_FIELDS = (("air", "T"), ("epoxy", "T"), ("air", "U"))
CONV_FLUID_REGION = "air"

# INTERPRETATION 20 (T5e) -- disclosed, not silent.  S5.5 says "any cell value"
# and "that field's range" without fixing two things for a VECTOR field or for
# WHICH checkpoint carries the range.  T5e registers, and PRINTS BOTH READINGS
# BESIDE EACH OTHER so the choice is auditable:
#   (a) a vector's "cell value" is read PER COMPONENT: the delta is
#       max over cells and components of |dU_ij|, and the range is
#       max over components j of (max_i U_ij - min_i U_ij).
#       The magnitude reading -- max_i |dU_i| against max_i|U_i| - min_i|U_i| --
#       is computed and PRINTED as REPORTED beside it.
#   (b) "that field's range" is evaluated at endTime, the checkpoint the
#       criterion grades.  The union range over both checkpoints is computed
#       and PRINTED as REPORTED beside it.
# Neither reading is outcome-bearing on this ladder: the smallest exceedance
# measured on any level, field or reading is 169x the tolerance.  A future
# ladder sitting near the tolerance would need this ruled, not interpreted.
CONV_VECTOR_READING = "per-component"
CONV_RANGE_AT = "endTime"

# The internalField, not the boundaryField: S5.5 says "any CELL value", and a
# boundary entry is a face value.  Stated because it is a reading, not a
# default -- the boundary values are printed as a REPORTED companion.
CONV_DOMAIN = "internalField"


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _l342_class(name):
    """The declared class of a named artefact.  Driven in --selftest.

    NEW IN T5e: the checkpoint pair is a GATE INPUT.  Reclassifying it as
    infrastructure would convert a registered NOT A RESULT into a bookkeeping
    note, which is the gaming shape L-342 exists to name."""
    if name in ("checkpoint_pair", "yPlus_field", "yPlus.dat"):
        return ("GATE INPUT (never infrastructure): T5 S5.5 and S16.3.1 "
                "register absence as NOT A RESULT")
    if name == "initial_residual":
        return ("REPORTED, NEVER GATED: L-141 -- in T1c a genuinely unconverged "
                "case sat at residual 4e-05, and T5 S5.5 writes no residualControl")
    if name in ("rc_value", "End", "last_time", "age_guard", "ExecutionTime_count") \
            or name in REQUIRED_FIELDS:
        return "PHYSICS-CRITICAL"
    if name in ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s", "capped",
                "checkMesh_rc", "rc_record", "ExecutionTime_line_count", "pid",
                "ledger_row", "log.launch", "CAP_ENFORCED.txt", "marker_mtime"):
        return "INFRASTRUCTURE"
    return "UNCLASSIFIED"


# ===========================================================================
# SECTION A -- THE READERS.  VERBATIM from analyse_t5b.py / analyse_t5c.py so
# the graded rows travel the identical call chain (T5c S6.1).  A copy rather
# than an import: importing a frozen module makes this file's behaviour depend
# on a file this registration may not touch, and the chain must be present in
# the instrument being frozen.
# ===========================================================================
def _strip(path):
    s = open(path, errors="replace").read()
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def read_points(path):
    s = _strip(path)
    m = re.search(r"\n(\d+)\s*\n\(", s)
    if not m:
        refuse("%s: no point list header" % path)
    n = int(m.group(1))
    pts = []
    for mm in re.finditer(r"\(([-0-9.eE+ ]+)\)", s[m.end():]):
        a = mm.group(1).split()
        if len(a) != 3:
            continue
        pts.append((float(a[0]), float(a[1]), float(a[2])))
        if len(pts) == n:
            break
    if len(pts) != n:
        refuse("%s: read %d of %d points" % (path, len(pts), n))
    return pts


def read_faces(path):
    s = _strip(path)
    m = re.search(r"\n(\d+)\s*\n\(", s)
    if not m:
        refuse("%s: no face list header" % path)
    n = int(m.group(1))
    faces = []
    for mm in re.finditer(r"(\d+)\(([0-9 ]+)\)", s[m.end():]):
        faces.append([int(x) for x in mm.group(2).split()])
        if len(faces) == n:
            break
    if len(faces) != n:
        refuse("%s: read %d of %d faces" % (path, len(faces), n))
    return faces


def read_boundary(path):
    s = _strip(path)
    out = {}
    for mm in re.finditer(r"^\s{4}([A-Za-z_][A-Za-z0-9_]*)\s*\n\s*\{(.*?)\n\s{4}\}",
                          s, flags=re.S | re.M):
        body = mm.group(2)
        nf = re.search(r"nFaces\s+(\d+)", body)
        sf = re.search(r"startFace\s+(\d+)", body)
        ty = re.search(r"type\s+(\w+)", body)
        if nf and sf:
            out[mm.group(1)] = dict(nFaces=int(nf.group(1)),
                                    startFace=int(sf.group(1)),
                                    type=ty.group(1) if ty else "?")
    return out


def face_area(face, pts):
    P = [pts[i] for i in face]
    c = [sum(p[k] for p in P) / len(P) for k in range(3)]
    a = 0.0
    for i in range(len(P)):
        p1, p2 = P[i], P[(i + 1) % len(P)]
        u = [p1[k] - c[k] for k in range(3)]
        v = [p2[k] - c[k] for k in range(3)]
        cx = (u[1] * v[2] - u[2] * v[1],
              u[2] * v[0] - u[0] * v[2],
              u[0] * v[1] - u[1] * v[0])
        a += 0.5 * math.sqrt(sum(x * x for x in cx))
    return a


def patch_areas(mesh_dir, patches):
    pts = read_points(os.path.join(mesh_dir, "points"))
    faces = read_faces(os.path.join(mesh_dir, "faces"))
    bnd = read_boundary(os.path.join(mesh_dir, "boundary"))
    out = {}
    for p in patches:
        if p not in bnd:
            refuse("patch %s absent from %s/boundary -- a registered wall that "
                   "is not in the mesh (this is defect D2's shape and it refuses)"
                   % (p, mesh_dir))
        nf, sf = bnd[p]["nFaces"], bnd[p]["startFace"]
        out[p] = [face_area(faces[sf + i], pts) for i in range(nf)]
    return out, bnd


def check_wall_set(bnd):
    """BOTH directions.  T4/C1: a gate that names one wall certifies one wall."""
    mesh_walls = set(k for k, v in bnd.items()
                     if v.get("type", "").lower().endswith("wall"))
    reg = set(YPLUS_WALLS)
    missing = sorted(reg - mesh_walls)
    extra = sorted(mesh_walls - reg)
    if missing:
        refuse("registered wall(s) absent from the mesh: %s" % ", ".join(missing))
    if extra:
        refuse("the mesh carries wall patch(es) this gate does not name: %s -- "
               "a gate that names one wall certifies one wall" % ", ".join(extra))
    return sorted(mesh_walls)


def read_patch_field(path, patch):
    """The boundaryField entry for one patch, as a list of floats."""
    if not os.path.isfile(path):
        return None
    s = _strip(path)
    i = s.find("boundaryField")
    if i < 0:
        return None
    j = s.find(patch, i)
    if j < 0:
        return None
    seg = s[j:j + 40_000_000]
    m = re.search(r"nonuniform\s+List<scalar>\s*(\d+)\s*\(", seg)
    u = re.search(r"value\s+uniform\s+([-0-9.eE+]+)\s*;", seg)
    if m and (not u or m.start() < u.start()):
        n = int(m.group(1))
        body = seg[m.end():]
        vals = []
        for tok in re.finditer(r"[-0-9.eE+]+", body):
            vals.append(float(tok.group(0)))
            if len(vals) == n:
                break
        if len(vals) != n:
            return None
        return vals
    if u:
        return [float(u.group(1))]
    return None


def read_yplus_dat(case_dir, endtime=ENDTIME):
    base = os.path.join(case_dir, "postProcessing", "air", "yPlus")
    if not os.path.isdir(base):
        return None, "no postProcessing/air/yPlus directory"
    rows = {}
    seen_any = False
    for t0 in sorted(os.listdir(base)):
        f = os.path.join(base, t0, "yPlus.dat")
        if not os.path.isfile(f):
            continue
        for line in open(f, errors="replace"):
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            seen_any = True
            try:
                t = float(parts[0])
            except ValueError:
                continue
            if abs(t - endtime) < 1e-9:
                rows[parts[1]] = dict(min=float(parts[2]), max=float(parts[3]),
                                      mean=float(parts[4]))
    if not seen_any:
        return None, ("yPlus.dat exists but carries ZERO data rows -- this is "
                      "defect D1 verbatim")
    if not rows:
        return None, "yPlus.dat has rows but none at endTime %d" % endtime
    return rows, None


def read_status(root, case):
    p = os.path.join(root, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None
    d = {}
    for line in open(p, errors="replace"):
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def check_completion(root, case, endtime=ENDTIME):
    """Rule 4, with R-RC applied to the rc RECORD.  VERBATIM analyse_t5b.py."""
    notes = []
    case_dir = os.path.join(root, case)
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return False, "no log.solve: nothing ran", notes
    txt = open(log, errors="replace").read()
    if "FOAM FATAL" in txt or re.search(r"\bSignal\s*:", txt):
        return False, "log.solve carries a FOAM FATAL or a signal token", notes

    st = read_status(root, case)
    if st is None:
        notes.append("STATUS absent: rc RECORD is NOT MEASURED (R-RC, "
                     "infrastructure); rc=0 will be an INFERENCE, not a reading")
        rc = None
    else:
        rc = st.get("rc")
        if rc is not None and rc.strip() != "0":
            return False, "solver rc = %s (PHYSICS-CRITICAL)" % rc, notes
        for k in ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s",
                  "capped", "checkMesh_rc"):
            if k not in st:
                notes.append("%s absent from STATUS: NOT MEASURED (infrastructure)" % k)

    if not re.search(r"^End\s*$", txt, re.M):
        return False, "no End line", notes
    times = [float(m.group(1)) for m in re.finditer(r"^Time = ([0-9.eE+-]+)", txt, re.M)]
    if not times:
        return False, "no Time lines", notes
    if abs(times[-1] - endtime) > 1e-9:
        return False, "last time %g != endTime %d" % (times[-1], endtime), notes
    n_exec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if n_exec != endtime:
        if n_exec < endtime:
            return False, ("ExecutionTime iteration count %d != endTime %d"
                           % (n_exec, endtime)), notes
        notes.append("ExecutionTime LINE count %d exceeds endTime %d: "
                     "INFRASTRUCTURE, NOT MEASURED as an iteration count"
                     % (n_exec, endtime))

    tdir = os.path.join(case_dir, str(endtime), "air")
    if not os.path.isdir(tdir):
        return False, "no %d/air field directory" % endtime, notes
    for f in REQUIRED_FIELDS:
        if not os.path.isfile(os.path.join(tdir, f)):
            return False, "field %s absent at endTime" % f, notes
    datum = None
    for r, _d, fs in os.walk(os.path.join(case_dir, "0")):
        if "T" in fs:
            datum = os.path.join(r, "T")
            break
    if datum is None:
        return False, "no 0/**/T: the age guard has no datum", notes
    t0 = os.path.getmtime(datum)
    for f in REQUIRED_FIELDS:
        if os.path.getmtime(os.path.join(tdir, f)) <= t0:
            return False, "age guard: field %s is NOT newer than 0/T" % f, notes
    if rc is None:
        notes.append("rc=0 INFERRED (labelled, not read): End line, last time == "
                     "endTime, fields present and the age guard all hold")
    return True, "complete", notes


def face_mean_h(case_dir, patch, areas, endtime=ENDTIME):
    tdir = os.path.join(case_dir, str(endtime), "air")
    q = read_patch_field(os.path.join(tdir, "wallHeatFlux"), patch)
    T = read_patch_field(os.path.join(tdir, "T"), patch)
    if q is None or T is None:
        return None, "wallHeatFlux or T patch field unreadable on %s" % patch
    A = areas[patch]
    if len(q) == 1:
        q = q * len(A)
    if len(T) == 1:
        T = T * len(A)
    if not (len(q) == len(T) == len(A)):
        return None, ("length mismatch on %s: q %d, T %d, areas %d"
                      % (patch, len(q), len(T), len(A)))
    num = 0.0
    den = 0.0
    for qi, Ti, Ai in zip(q, T, A):
        dT = Ti - T_REF_K
        if abs(dT) < 1e-9:
            return None, "a face on %s has T_sur == T_ref" % patch
        num += (abs(qi) / dT) * Ai
        den += Ai
    return num / den, None


def face_mean_T_C(case_dir, patch, areas, endtime=ENDTIME):
    tdir = os.path.join(case_dir, str(endtime), "air")
    T = read_patch_field(os.path.join(tdir, "T"), patch)
    if T is None:
        return None, "T patch field unreadable on %s" % patch
    A = areas[patch]
    if len(T) == 1:
        T = T * len(A)
    if len(T) != len(A):
        return None, "T/area length mismatch on %s" % patch
    return sum(t * a for t, a in zip(T, A)) / sum(A) - 273.15, None


def classify_triple(f_c, f_m, f_f):
    d32 = f_m - f_c
    d21 = f_f - f_m
    if d32 == 0.0 and d21 == 0.0:
        return "EXACT"
    if d32 == 0.0 or d21 == 0.0:
        return "STAGNANT"
    R = d21 / d32
    if R < 0:
        return "OSCILLATORY"
    if R >= 1.0:
        return "DIVERGENT"
    return "CONVERGING"


def gci_triple(f_c, f_m, f_f, r21, r32):
    d32 = f_m - f_c
    d21 = f_f - f_m
    if d32 == 0.0:
        return None, None
    s = 1.0 if (d21 / d32) > 0 else -1.0
    p = 2.0
    for _ in range(200):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        p_new = abs(math.log(abs(d32 / d21)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            p = p_new
            break
        p = p_new
    if f_f == 0.0:
        return p, None
    e21 = abs(d21 / f_f)
    gci = FS * e21 / (r21 ** p - 1.0)
    return p, gci


def band_verdict(value, ref, band_abs):
    if abs(value - ref) <= band_abs:
        return VERDICT_PASS
    return VERDICT_FAIL


def combined_band(row):
    u = row.get("uncertainty")
    d = row.get("digitisation_increment")
    if u is None:
        return None
    if d is None:
        return float(u)
    return math.sqrt(float(u) ** 2 + float(d) ** 2)


def measured_ratios(cells):
    """Celik/Roache subscripting, 1 = finest: r21 MEDIUM->FINE, r32 COARSE->MEDIUM."""
    r21 = (cells["f"] / cells["m"]) ** (1.0 / 3.0)
    r32 = (cells["m"] / cells["c"]) ** (1.0 / 3.0)
    return r21, r32


# ===========================================================================
# SECTION B -- THE CARRY-OVER ASSERTIONS.  Every claim of "unchanged" in the
# registration is made EXECUTABLE here.  A claim in prose is a claim.
# ===========================================================================
def assert_frozen_predecessor_bytes():
    """sha256 of the DISK BYTES of both frozen predecessors.  T5c_RESULTS.md
    S5a FORWARD-ONLY ADOPTION: full sha256, never a git blob SHA-1 (L-450)."""
    out = []
    for path, want, label in ((FROZEN_T5B, FROZEN_T5B_SHA256, "analyse_t5b.py"),
                              (FROZEN_T5C, FROZEN_T5C_SHA256, "analyse_t5c.py")):
        if not os.path.isfile(path):
            refuse("the frozen predecessor %s is absent: T5e's carry-over "
                   "cannot be asserted, and an unasserted carry-over is a "
                   "claim, not a check" % path)
        got = sha256_of(path)
        if got != want:
            refuse("FROZEN PREDECESSOR MOVED. %s sha256 %s, expected %s. T5e "
                   "carries this file's thresholds and its y+ repair; if the "
                   "file is not the one T5e was written against, nothing here "
                   "is a carry-over." % (label, got, want))
        out.append("%s sha256 %s" % (label, got[:16] + "..."))
    return out


def parse_registered_criterion(path=T5_REGISTRATION):
    """READ THE CLAUSE-(1) TOLERANCE OUT OF THE FROZEN REGISTRATION.

    This is the whole of T5e's rule-2 defence on clause (1) and it is the one
    thing a reader must not have to take on trust: the number is not chosen
    here, it is T5's, frozen before any T5 case existed.  REFUSES on any
    difference from CONV_REL_TOL or CONV_CHECKPOINT_STRIDE."""
    if not os.path.isfile(path):
        refuse("the frozen T5 registration %s is absent: clause (1)'s tolerance "
               "cannot be read from its registration and this comparator will "
               "not grade on a typed-in threshold" % path)
    txt = open(path, errors="replace").read()
    m = re.search(r"is at most \*\*([0-9.eE+-]+) of that field's range\*\*", txt)
    if not m:
        refuse("T5 S5.5's registered tolerance sentence is not in %s. The "
               "clause-(1) instrument has no registration to read." % path)
    tol = float(m.group(1))
    if tol != CONV_REL_TOL:
        refuse("CLAUSE (1) TOLERANCE MISMATCH: the frozen registration says %r, "
               "this file carries %r. T5e registers NO new threshold; a "
               "difference means this file, not the registration, is wrong."
               % (tol, CONV_REL_TOL))
    # the checkpoint stride, from `endTime - 1000` (the registration writes a
    # UNICODE MINUS U+2212, so both dashes are accepted)
    ms = re.search(r"between the checkpoints at\s*\n?`endTime\s*[-−]\s*(\d+)`", txt)
    if not ms:
        ms = re.search(r"`endTime\s*[-−]\s*(\d+)`\s*and\s*`endTime`", txt)
    if not ms:
        refuse("T5 S5.5's checkpoint pair sentence is not parseable in %s" % path)
    stride = int(ms.group(1))
    if stride != CONV_CHECKPOINT_STRIDE:
        refuse("CLAUSE (1) CHECKPOINT STRIDE MISMATCH: registration says %d, "
               "this file carries %d" % (stride, CONV_CHECKPOINT_STRIDE))
    if "`residualControl` is not written" not in txt:
        refuse("T5 S5.5's `residualControl is not written` sentence is not in "
               "%s. T5e's refusal to use a residual as the clause-(1) "
               "instrument rests on that sentence; without it the refusal is "
               "unsourced." % path)
    return tol, stride


def assert_criterion_clause_witness(path=T5_REGISTRATION):
    """sha256 of the FOUR LINES that ARE the criterion, not of the whole file:
    T5_PREREGISTRATION.md lawfully carries appended dated amendments, so a
    whole-file witness would rot while the criterion itself did not move."""
    if not os.path.isfile(path):
        refuse("no %s: the criterion clause cannot be witnessed" % path)
    lines = open(path, errors="replace").read().splitlines(True)
    for start in range(len(lines)):
        blob = "".join(lines[start:start + 4]).encode()
        if hashlib.sha256(blob).hexdigest() == T5_CRITERION_SHA256:
            return start + 1, start + 4
    refuse("THE S5.5 CRITERION CLAUSE IS NOT IN %s AT ITS WITNESSED BYTES "
           "(sha256 %s over four consecutive lines). Either the frozen "
           "registration was edited in place -- which rule 6 forbids -- or "
           "this file's witness is wrong. Either way no row is graded."
           % (path, T5_CRITERION_SHA256))


def assert_thresholds_carried_over():
    """Re-parse BOTH frozen modules' threshold literals and REFUSE on any
    difference.  T5b supplies the y+ thresholds; T5c supplies the constants of
    the area-average repair T5e adopts."""
    wanted_b = ("YPLUS_WALLS", "YPLUS_MAX", "YPLUS_TARGET", "YPLUS_TARGET_TOL",
                "CELLS_REGISTERED", "FS", "ENDTIME", "REQUIRED_FIELDS", "T_REF_K",
                "INTRINSIC_FLOOR_PCT", "GRADED_H", "GRADED_T", "REPORTED_ROWS",
                "G5_IDENTITY_MARGIN_K", "G5_BOUND_LO_C", "G5_BOUND_HI_C",
                "PLANT_OFFSET", "PLANT_SPIKE", "LEVELS", "CASE_OF")
    wanted_c = ("Q95", "Q50", "REL_EXACT", "REL_FACE", "Y3_MIN_SEPARATION",
                "Y2_SEEN_FRACTION", "Y2_BLIND_SLACK", "ARM_WALL", "ARM_LEVEL")
    here = globals()
    names = []
    for frozen, wanted in ((FROZEN_T5B, wanted_b), (FROZEN_T5C, wanted_c)):
        src = open(frozen, errors="replace").read()
        ns = {}
        for line in src.splitlines():
            m = re.match(r"^([A-Z][A-Z0-9_]*)\s*=\s*(.+?)(?:\s+#.*)?$", line)
            if not m or m.group(1) not in wanted:
                continue
            try:
                ns[m.group(1)] = eval(m.group(2), {"__builtins__": {}}, {})
            except Exception:
                continue
        mm = re.search(r"YPLUS_WALLS\s*=\s*\((.*?)\)", src, flags=re.S)
        if mm and "YPLUS_WALLS" in wanted:
            ns["YPLUS_WALLS"] = tuple(
                x.strip().strip('"').strip("'")
                for x in mm.group(1).replace("\n", " ").split(",") if x.strip())
        missing = [k for k in wanted if k not in ns]
        if missing:
            refuse("could not re-parse %s from the frozen %s -- the carry-over "
                   "assertion cannot be performed and this comparator will not "
                   "grade on an unverified threshold set"
                   % (", ".join(missing), os.path.basename(frozen)))
        diffs = [(k, ns[k], here[k]) for k in wanted if ns[k] != here[k]]
        if diffs:
            refuse("THRESHOLD CARRY-OVER BROKEN against %s. T5e registers every "
                   "y+ threshold as byte-identical. These differ: %s"
                   % (os.path.basename(frozen),
                      "; ".join("%s frozen=%r here=%r" % d for d in diffs)))
        names.extend(wanted)
    return sorted(names)


# ===========================================================================
# SECTION C -- T5c's THREE REGISTERED y+ READERS, CARRIED UNCHANGED
# ===========================================================================
def R_area(vals, areas):
    """THE GATED LADDER STATISTIC.  Sum(y+_i * A_i) / Sum A_i."""
    tot = sum(areas)
    if tot <= 0.0:
        return None
    return sum(v * a for v, a in zip(vals, areas)) / tot


def R_max(vals):
    """The point maximum.  GATED against the sublayer bound only (verification
    binding condition 3); REPORTED against the ladder."""
    return max(vals)


def R_facecount_mean(vals):
    """The UNWEIGHTED face-count mean.  REPORTED, never gated."""
    return sum(vals) / len(vals)


def area_quantile(vals, areas, q):
    order = sorted(range(len(vals)), key=lambda i: (vals[i], i))
    tot = sum(areas)
    target = q * tot
    cum = 0.0
    for pos, i in enumerate(order):
        cum += areas[i]
        if cum >= target - 1e-15 * tot:
            return vals[i], i, pos
    i = order[-1]
    return vals[i], i, len(order) - 1


def R_q95(vals, areas):
    return area_quantile(vals, areas, Q95)[0]


def R_median_area(vals, areas):
    return area_quantile(vals, areas, Q50)[0]


# ===========================================================================
# SECTION C1 -- CLAUSE (1).  THE RESTORED STEP, AND THE WHOLE POINT OF T5e.
# The instrument is the CHECKPOINT DELTA registered at T5 S5.5, NEVER a
# residual.  See this file's docstring for why `gate_converged` is not carried.
# ===========================================================================
INTERNAL_RE = re.compile(
    r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*\n?\s*(\d+)\s*\n?\s*\(")
INTERNAL_UNIFORM_RE = re.compile(r"internalField\s+uniform\s+(.+?);", re.S)


def read_internal_field(path):
    """The internalField of an OpenFOAM ASCII field, as (kind, values).

    kind is 'scalar' (values a list of float) or 'vector' (values a list of
    3-tuples).  CONV_DOMAIN: the CELL values, which is what S5.5 names -- a
    boundaryField entry is a face value, not a cell value."""
    if not os.path.isfile(path):
        return None, "absent: %s" % path
    s = open(path, errors="replace").read()
    i = s.find("internalField")
    if i < 0:
        return None, "no internalField in %s" % path
    seg = s[i:]
    m = INTERNAL_RE.match(seg)
    if not m:
        mu = INTERNAL_UNIFORM_RE.match(seg)
        if mu:
            return None, ("internalField is UNIFORM in %s: a uniform field "
                          "carries no cell-to-cell variation and the S5.5 "
                          "criterion cannot be evaluated on it" % path)
        return None, "internalField in %s is not a parseable list" % path
    kind = m.group(1)
    n = int(m.group(2))
    body = seg[m.end():]
    if kind == "scalar":
        vals = []
        for tok in re.finditer(r"[-0-9.eE+]+", body):
            vals.append(float(tok.group(0)))
            if len(vals) == n:
                break
        if len(vals) != n:
            return None, ("%s: read %d of %d scalar cell values"
                          % (path, len(vals), n))
        return ("scalar", vals), None
    vals = []
    for mm in re.finditer(r"\(([^)]*)\)", body):
        a = mm.group(1).split()
        if len(a) != 3:
            continue
        vals.append((float(a[0]), float(a[1]), float(a[2])))
        if len(vals) == n:
            break
    if len(vals) != n:
        return None, "%s: read %d of %d vector cell values" % (path, len(vals), n)
    return ("vector", vals), None


def field_range(kind, vals):
    """THE REGISTERED DENOMINATOR: `that field's range`.

    scalar -> max - min.  vector -> INTERPRETATION 20(a): max over components
    of that component's range.  The magnitude reading is computed separately
    and REPORTED, never used here."""
    if kind == "scalar":
        return max(vals) - min(vals)
    return max(max(u[j] for u in vals) - min(u[j] for u in vals)
               for j in range(3))


def field_range_reported(kind, vals):
    """The COMPANION reading, REPORTED beside the gated one (INTERPRETATION 20).
    scalar -> None (there is only one reading).  vector -> magnitude range."""
    if kind == "scalar":
        return None
    mags = [math.sqrt(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]) for u in vals]
    return max(mags) - min(mags)


def max_abs_delta(kind, lo, hi):
    """THE REGISTERED NUMERATOR: `the largest change of any cell value`.

    Returns (value, cell_index).  scalar -> max_i |hi_i - lo_i|.
    vector -> INTERPRETATION 20(a): max over cells AND components of
    |hi_ij - lo_ij|."""
    if kind == "scalar":
        best = -1.0
        arg = -1
        for i in range(len(hi)):
            d = abs(hi[i] - lo[i])
            if d > best:
                best, arg = d, i
        return best, arg
    best = -1.0
    arg = -1
    for i in range(len(hi)):
        a, b = hi[i], lo[i]
        d = max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))
        if d > best:
            best, arg = d, i
    return best, arg


def max_abs_delta_reported(kind, lo, hi):
    """The COMPANION numerator, REPORTED beside the gated one.
    scalar -> None.  vector -> max_i |hi_i - lo_i| as a VECTOR NORM."""
    if kind == "scalar":
        return None
    best = 0.0
    for a, b in zip(hi, lo):
        d = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
        if d > best:
            best = d
    return best


def clause1_one_field(case_dir, region, fld):
    """Evaluate T5 S5.5 on ONE (region, field) checkpoint pair."""
    p_lo = os.path.join(case_dir, str(CONV_CHECKPOINT_LO), region, fld)
    p_hi = os.path.join(case_dir, str(CONV_CHECKPOINT_HI), region, fld)
    a, err = read_internal_field(p_lo)
    if a is None:
        return None, ("checkpoint %d %s/%s unreadable (%s) -- an UNMEASURED "
                      "precondition is not a satisfied one"
                      % (CONV_CHECKPOINT_LO, region, fld, err))
    b, err = read_internal_field(p_hi)
    if b is None:
        return None, ("checkpoint %d %s/%s unreadable (%s)"
                      % (CONV_CHECKPOINT_HI, region, fld, err))
    (k_lo, v_lo), (k_hi, v_hi) = a, b
    if k_lo != k_hi:
        return None, ("%s/%s changed kind between checkpoints: %s -> %s"
                      % (region, fld, k_lo, k_hi))
    if len(v_lo) != len(v_hi):
        return None, ("%s/%s has %d cells at %d and %d at %d -- the two "
                      "checkpoints are not the same mesh and no cell-wise "
                      "change is defined"
                      % (region, fld, len(v_lo), CONV_CHECKPOINT_LO,
                         len(v_hi), CONV_CHECKPOINT_HI))
    rng = field_range(k_hi, v_hi)
    tol = CONV_REL_TOL * rng
    delta, arg = max_abs_delta(k_hi, v_lo, v_hi)
    rec = dict(region=region, field=fld, kind=k_hi, ncells=len(v_hi),
               rng=rng, tol=tol, delta=delta, argcell=arg,
               converged=(delta <= tol),
               factor=(delta / tol) if tol > 0 else float("inf"),
               # REPORTED companions (INTERPRETATION 20) -- never gated
               rng_union=(max(max(v_hi), max(v_lo)) - min(min(v_hi), min(v_lo)))
               if k_hi == "scalar" else None,
               rng_reported=field_range_reported(k_hi, v_hi),
               delta_reported=max_abs_delta_reported(k_hi, v_lo, v_hi))
    if tol <= 0.0:
        return None, ("%s/%s has a ZERO range at %d, so the registered "
                      "tolerance is zero and the criterion is vacuous -- a "
                      "gate that cannot fail is not a gate"
                      % (region, fld, CONV_CHECKPOINT_HI))
    return rec, None


def gate_clause1(case_dir, level):
    """T5 S7.5 STEP 1, RESTORED: `any ladder level NOT CONVERGED -> NOT A RESULT`.

    Evaluated on T in BOTH regions and separately on U in the fluid, exactly as
    T5 S5.5 registers.  A level is CONVERGED only if every one of the three
    passes; absence of a checkpoint REFUSES rather than degrading."""
    rows = []
    for region, fld in CONV_FIELDS:
        rec, err = clause1_one_field(case_dir, region, fld)
        if rec is None:
            refuse("CLAUSE (1) INPUT ABSENT at level %s: %s. The checkpoint "
                   "pair is a GATE INPUT and never infrastructure (L-342); "
                   "T5 S5.5 registers the criterion on it, so an unreadable "
                   "checkpoint refuses rather than being graded around."
                   % (level, err))
        rows.append(rec)
    bad = [r for r in rows if not r["converged"]]
    state = "NOT CONVERGED" if bad else "CONVERGED"
    if bad:
        why = ("%s by T5 S5.5: " % state) + "; ".join(
            "%s/%s max|delta| %.6f over %s->%s vs tol %.6e (= %g x range "
            "%.6f) -- over by %.0fx"
            % (r["region"], r["field"], r["delta"], CONV_CHECKPOINT_LO,
               CONV_CHECKPOINT_HI, r["tol"], CONV_REL_TOL, r["rng"], r["factor"])
            for r in bad)
    else:
        why = ("CONVERGED by T5 S5.5: every one of the %d registered "
               "(region, field) pairs changes by at most %g of its range "
               "between %s and %s" % (len(rows), CONV_REL_TOL,
                                      CONV_CHECKPOINT_LO, CONV_CHECKPOINT_HI))
    return dict(state=state, rows=rows, why=why)


def print_clause1(clause1_by_level):
    """Every number the clause turned on, printed beside its verdict.  The
    REPORTED companion readings of INTERPRETATION 20 print alongside so the
    interpretation is auditable from the output, not only from the source."""
    print("\nCLAUSE (1) -- T5 S7.5 step 1, RESTORED. Instrument: the T5 S5.5")
    print("CHECKPOINT DELTA between %d and %d, NEVER a residual (L-141)."
          % (CONV_CHECKPOINT_LO, CONV_CHECKPOINT_HI))
    print("  tolerance = %g x that field's range, READ FROM the frozen T5 "
          "registration, not typed here" % CONV_REL_TOL)
    print("  domain = %s (S5.5 says `any CELL value`); vector reading = %s; "
          "range at = %s (INTERPRETATION 20)"
          % (CONV_DOMAIN, CONV_VECTOR_READING, CONV_RANGE_AT))
    print("  %-3s %-6s %-2s %8s %13s %13s %13s %12s  %s"
          % ("lv", "region", "f", "cells", "max|delta|", "range", "tol",
             "over by", "clause (1)"))
    for lv in LEVELS:
        g = clause1_by_level[lv]
        for r in g["rows"]:
            print("  %-3s %-6s %-2s %8d %13.6f %13.6f %13.6e %11.0fx  %s"
                  % (lv, r["region"], r["field"], r["ncells"], r["delta"],
                     r["rng"], r["tol"], r["factor"],
                     "CONVERGED" if r["converged"] else "NOT CONVERGED"))
        print("  %-3s -> LEVEL STATE: %s" % (lv, g["state"]))
    print("\n  REPORTED companion readings (INTERPRETATION 20) -- NEVER GATED:")
    for lv in LEVELS:
        for r in clause1_by_level[lv]["rows"]:
            if r["kind"] == "vector":
                print("    %s %s/%s  magnitude reading: max|dU| %.6f against "
                      "magnitude range %.6f (gated per-component reading gave "
                      "%.6f against %.6f)"
                      % (lv, r["region"], r["field"], r["delta_reported"],
                         r["rng_reported"], r["delta"], r["rng"]))
            else:
                print("    %s %s/%s  union-range reading: range over BOTH "
                      "checkpoints %.6f (gated endTime range %.6f) -> tol "
                      "%.6e, over by %.0fx"
                      % (lv, r["region"], r["field"], r["rng_union"], r["rng"],
                         CONV_REL_TOL * r["rng_union"],
                         r["delta"] / (CONV_REL_TOL * r["rng_union"])))
    print("  Neither companion reading changes any level's state on this "
          "ladder; both are printed so the interpretation is auditable.")


# ---------------------------------------------------------------------------
# RULE 3 -- THE PLANTED CONTROL ON THE CLAUSE-(1) READER.
# This reader's whole job is to emit a delta.  A zero from it is believed only
# after it has been shown, on the same bytes, able to emit a non-zero.
# ---------------------------------------------------------------------------
def _locate_internal_list(text):
    """(start, end) character span of the internalField scalar value list."""
    m = INTERNAL_RE.search(text)
    if not m or m.group(1) != "scalar":
        return None
    st = m.end()
    en = text.find(")", st)
    if en < 0:
        return None
    return st, en


def _write_internal_plant(dest, base_text, span, values):
    st, en = span
    with open(dest, "w") as fh:
        fh.write(base_text[:st] + "\n" + "\n".join(repr(v) for v in values)
                 + "\n" + base_text[en:])


def _assert_scratch_outside(case_dir):
    """T5c S6.1 row WRITE PATH, carried: refuse if a scratch copy would resolve
    inside the case tree.  Checked BEFORE any plant is written."""
    probe = tempfile.mkdtemp(prefix="t5e_writepath_probe_")
    try:
        rp = os.path.realpath(probe)
        rc = os.path.realpath(case_dir)
        if rp == rc or rp.startswith(rc + os.sep):
            refuse("WRITE PATH: the scratch directory %s resolves INSIDE the "
                   "case tree %s. A plant written into the run tree corrupts "
                   "the artifact it is testing." % (rp, rc))
    finally:
        shutil.rmtree(probe, ignore_errors=True)


def clause1_birth_requirement(case_dir, level=ARM_LEVEL, region="air", fld="T"):
    """THE RULE-3 CONTROL ON CLAUSE (1).  Arms C-1, C-2, C-3, both limbs each.

    Every plant goes into a COPY in scratch; every readback goes through the
    REAL reader, from disk.  Refuses (exit 2) on any failed limb."""
    print("\nBIRTH REQUIREMENT ON THE CLAUSE-(1) READER (rule 3) -- planted into")
    print("a scratch COPY of %s/%d/%s/%s at level %s, read back FROM DISK "
          "through the real reader." % (os.path.basename(case_dir),
                                        CONV_CHECKPOINT_HI, region, fld, level))
    _assert_scratch_outside(case_dir)

    p_lo = os.path.join(case_dir, str(CONV_CHECKPOINT_LO), region, fld)
    p_hi = os.path.join(case_dir, str(CONV_CHECKPOINT_HI), region, fld)
    a, err = read_internal_field(p_lo)
    b, err2 = read_internal_field(p_hi)
    if a is None or b is None:
        refuse("clause-(1) birth requirement: cannot read the checkpoint pair "
               "(%s / %s)" % (err, err2))
    (k_lo, v_lo), (k_hi, v_hi) = a, b
    if k_hi != "scalar":
        refuse("clause-(1) birth requirement is registered on a SCALAR field "
               "(%s/%s); %s is %s" % (region, fld, fld, k_hi))
    n = len(v_hi)
    base_text = open(p_hi, errors="replace").read()
    span = _locate_internal_list(base_text)
    if span is None:
        refuse("clause-(1) birth requirement: %s carries no parseable "
               "internalField scalar list -- there is nothing to plant into"
               % p_hi)
    base_delta, base_arg = max_abs_delta("scalar", v_lo, v_hi)
    base_rng = field_range("scalar", v_hi)

    # The plant goes at the cell of SMALLEST base change, so that the argmax
    # MUST MOVE for the arm to pass.  ANTI-VACUITY: refuse if that cell is
    # already the argmax (then "the argmax is at the plant" would be free).
    i0 = min(range(n), key=lambda i: (abs(v_hi[i] - v_lo[i]), i))
    if i0 == base_arg:
        refuse("arm C-1 REFUSES: the cell of SMALLEST base change is also the "
               "argmax of the base delta at level %s, so `the argmax is at the "
               "planted cell` would pass without the plant moving anything. A "
               "control that cannot distinguish is VACUOUS." % level)

    tmp = tempfile.mkdtemp(prefix="t5e_clause1_plant_")
    failures = []
    arms = []
    try:
        work = os.path.join(tmp, str(CONV_CHECKPOINT_HI), region)
        os.makedirs(work)
        wf = os.path.join(work, fld)

        # ---- C-1  SIGNAL: a single-cell spike, AND the argmax is AT it -----
        c1 = Arm("C-1", "SIGNAL -- a single-cell spike is seen AT the planted cell")
        spiked = list(v_hi)
        spiked[i0] = spiked[i0] + PLANT_SPIKE
        _write_internal_plant(wf, base_text, span, spiked)
        got, err = read_internal_field(wf)
        if got is None:
            c1.pos(False, "the reader could not read the spiked copy: %s" % err)
            c1.neg(False, "not reached: the positive limb did not read back")
        else:
            gk, gv = got
            d1, arg1 = max_abs_delta("scalar", v_lo, gv)
            c1.pos(d1 >= Y2_SEEN_FRACTION * PLANT_SPIKE and arg1 == i0,
                   "max|delta| read back from disk is %.6f (required >= %.6f = "
                   "%.1f x the %.4f spike) and its argmax is cell %d, which IS "
                   "the planted cell %d -- the predicate ASKS WHERE the maximum "
                   "is (VERIFICATION_CHARTER S2d.11.1 item A)"
                   % (d1, Y2_SEEN_FRACTION * PLANT_SPIKE, Y2_SEEN_FRACTION,
                      PLANT_SPIKE, arg1, i0))
            again, _ = read_internal_field(wf)
            d_again, _a = max_abs_delta("scalar", v_lo, again[1])
            c1.neg(d_again - d1 == 0.0,
                   "two reads of identical bytes differ by %r (must be exactly "
                   "0.0); a reader noisy on unchanged bytes cannot be credited "
                   "with any move" % (d_again - d1))
            den = abs(v_hi[i0] + PLANT_SPIKE)
            rel = abs(gv[i0] - (v_hi[i0] + PLANT_SPIKE)) / (den if den else 1.0)
            c1.strong(rel <= REL_FACE,
                      "the planted cell %d reads back %.9f against base+spike "
                      "%.9f (relative %.3e, bound %.0e)"
                      % (i0, gv[i0], v_hi[i0] + PLANT_SPIKE, rel, REL_FACE))
            others = max((abs(gv[i] - v_hi[i]) for i in range(n) if i != i0),
                         default=0.0)
            c1.strong(others == 0.0,
                      "every one of the other %d cells is unchanged (max "
                      "|delta| %r), so the move is about the plant and nothing "
                      "else" % (n - 1, others))
            c1.strong(base_arg != i0 and abs(base_delta - d1) > 0.0,
                      "the base argmax was cell %d with max|delta| %.6f; the "
                      "plant MOVED both, so neither limb passed vacuously"
                      % (base_arg, base_delta))
        arms.append(c1)

        # ---- C-2  EXACTNESS: constant offset; the RANGE reader is blind -----
        c2 = Arm("C-2", "EXACTNESS -- a constant offset moves the DELTA exactly "
                        "and the RANGE reader is EXACTLY blind to it (L-340)")
        offset = [v + PLANT_OFFSET for v in v_hi]
        _write_internal_plant(wf, base_text, span, offset)
        got2, err = read_internal_field(wf)
        if got2 is None:
            c2.pos(False, "the reader could not read the offset copy: %s" % err)
            c2.neg(False, "not reached: the positive limb did not read back")
        else:
            gv2 = got2[1]
            d2, _arg = max_abs_delta("scalar", v_lo, gv2)
            # closed form, computed INDEPENDENTLY of the reader
            pred = max(abs((v_hi[i] + PLANT_OFFSET) - v_lo[i]) for i in range(n))
            rel = abs(d2 - pred) / (abs(pred) if pred else 1.0)
            c2.pos(rel <= REL_EXACT,
                   "max|delta| read back is %.12f against the closed form "
                   "%.12f (relative %.3e, bound %.0e) -- a difference reader is "
                   "affine in a constant offset, so the answer is EXACT, not "
                   "approximate" % (d2, pred, rel, REL_EXACT))
            rng2 = field_range("scalar", gv2)
            c2.neg(rng2 - base_rng == 0.0,
                   "the RANGE reader moved by %r (must be exactly 0.0): a "
                   "constant offset cannot move a range. The delta reader and "
                   "the range reader are DIFFERENT SHAPES, which is why one "
                   "plant cannot certify both (L-340)" % (rng2 - base_rng))
            worst = max(abs(gv2[i] - (v_hi[i] + PLANT_OFFSET))
                        / (abs(v_hi[i] + PLANT_OFFSET) or 1.0) for i in range(n))
            c2.strong(worst <= REL_FACE,
                      "every one of the %d planted cells reads back as "
                      "base+plant, worst relative %.3e (bound %.0e)"
                      % (n, worst, REL_FACE))
        arms.append(c2)

        # ---- C-3  THE PLANTED ZERO ITSELF ----------------------------------
        c3 = Arm("C-3", "THE ZERO -- an exact 0.0 from bytes that ARE the other "
                        "checkpoint, then a non-zero from the SAME file")
        _write_internal_plant(wf, base_text, span, list(v_lo))
        got3, err = read_internal_field(wf)
        if got3 is None:
            c3.neg(False, "the reader could not read the zero-delta copy: %s" % err)
            c3.pos(False, "not reached")
        else:
            gv3 = got3[1]
            d3, _a = max_abs_delta("scalar", v_lo, gv3)
            c3.neg(d3 == 0.0,
                   "a copy whose %d bytes ARE the %d values reads back max"
                   "|delta| = %r, which must be exactly 0.0 -- this is the ZERO "
                   "the criterion would report for a converged level"
                   % (CONV_CHECKPOINT_HI, CONV_CHECKPOINT_LO, d3))
            zspike = list(v_lo)
            zspike[i0] = zspike[i0] + PLANT_SPIKE
            _write_internal_plant(wf, base_text, span, zspike)
            got3b, err = read_internal_field(wf)
            if got3b is None:
                c3.pos(False, "the reader could not read the spiked zero copy")
            else:
                gv3b = got3b[1]
                d3b, arg3b = max_abs_delta("scalar", v_lo, gv3b)
                c3.pos(abs(d3b - PLANT_SPIKE) <= REL_EXACT * PLANT_SPIKE
                       and arg3b == i0,
                       "the SAME file, with one cell moved by %.4f, reads back "
                       "max|delta| %.9f at cell %d -- so the 0.0 above is a "
                       "zero from a reader SHOWN able to see a non-zero on "
                       "these bytes, which is the whole of rule 3"
                       % (PLANT_SPIKE, d3b, arg3b))
                c3.strong(d3 == 0.0 and d3b > 0.0,
                          "zero limb %r and non-zero limb %.6f were measured on "
                          "the same path, the same file and the same reader"
                          % (d3, d3b))
        arms.append(c3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for a in arms:
        failures.extend(a.report())
    if failures:
        refuse("CLAUSE-(1) BIRTH REQUIREMENT FAILED -- %d limb(s): %s. A zero "
               "from a reader not shown able to see a non-zero is not evidence "
               "(rule 3). No row of T5e is graded."
               % (len(failures), " | ".join(failures)))
    print("  ALL THREE ARMS PRINTED BOTH LIMBS AND PASSED. The clause-(1) "
          "reader is credited.")
    return True


# ===========================================================================
# SECTION D -- T5c S6.1: THE FOUR ROWS, RE-ASSERTED AT GRADE TIME
# ===========================================================================
FOAMFILE_OBJECT = re.compile(r"object\s+yPlus\s*;")
FOAMFILE_CLASS = re.compile(r"class\s+volScalarField\s*;")


def assert_section_6_1(case_dir, level, areas, bnd):
    """Four rows: producer, artifact, reader, write path.  VERBATIM T5c."""
    out = []
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse("S6.1 row PRODUCER: no %s" % cd)
    cdtxt = _strip(cd)
    if not re.search(r"type\s+yPlus\s*;", cdtxt):
        refuse("S6.1 row PRODUCER: %s carries no `type yPlus;` function object."
               % cd)
    out.append("PRODUCER: `type yPlus;` present in %s"
               % os.path.relpath(cd, case_dir))

    fld = os.path.join(case_dir, str(ENDTIME), "air", "yPlus")
    if not os.path.isfile(fld):
        refuse("S6.1 row ARTIFACT: no %s." % fld)
    head = open(fld, errors="replace").read(4096)
    if not FOAMFILE_CLASS.search(head) or not FOAMFILE_OBJECT.search(head):
        refuse("S6.1 row ARTIFACT: %s does not carry the producer's own "
               "FoamFile header. A control that plants into a file it wrote "
               "itself is the exact failure the birth requirement names." % fld)
    out.append("ARTIFACT: %s carries the producer's FoamFile header "
               "(class volScalarField, object yPlus), %d bytes"
               % (os.path.relpath(fld, case_dir), os.path.getsize(fld)))

    for w in YPLUS_WALLS:
        v = read_patch_field(fld, w)
        if v is None:
            refuse("S6.1 row READER / arm Y-5: read_patch_field returned None "
                   "for wall %s at level %s" % (w, level))
        n_mesh = bnd[w]["nFaces"]
        if len(v) == 0:
            refuse("arm Y-5 REFUSES: wall %s parsed to ZERO values at level %s."
                   % (w, level))
        if len(v) != n_mesh:
            refuse("arm Y-5 REFUSES: wall %s parsed %d values but the mesh's "
                   "own boundary declares nFaces %d at level %s."
                   % (w, len(v), n_mesh, level))
        if len(areas[w]) != n_mesh:
            refuse("arm Y-5 REFUSES: patch_areas returned %d areas for wall %s "
                   "but the mesh declares nFaces %d at level %s"
                   % (len(areas[w]), w, n_mesh, level))
    out.append("READER + arm Y-5: read_patch_field and patch_areas agree with "
               "the mesh's own boundary nFaces on all %d registered walls"
               % len(YPLUS_WALLS))

    _assert_scratch_outside(case_dir)
    out.append("WRITE PATH: scratch resolves outside the case tree; the run "
               "tree is never written")
    return fld, out


# ===========================================================================
# SECTION E -- THE IDENTITY PROOF, RE-EXECUTED AT GRADE TIME
# ===========================================================================
def identity_proof(case_dir, fld, level):
    dat, why = read_yplus_dat(case_dir)
    if dat is None:
        refuse("identity proof: yPlus.dat unreadable at level %s (%s)."
               % (level, why))
    rows = []
    for w in YPLUS_WALLS:
        if w not in dat:
            refuse("identity proof: wall %s absent from yPlus.dat at level %s"
                   % (w, level))
        v = read_patch_field(fld, w)
        fmin, fmax, fmean = min(v), max(v), sum(v) / len(v)
        for label, a, b in (("min", fmin, dat[w]["min"]),
                            ("max", fmax, dat[w]["max"]),
                            ("mean", fmean, dat[w]["mean"])):
            den = abs(b) if abs(b) > 0 else 1.0
            rel = abs(a - b) / den
            if rel > REL_EXACT:
                refuse("IDENTITY PROOF FAILED at level %s, wall %s, statistic "
                       "%s: field %.12g vs yPlus.dat %.12g, relative %.3e > "
                       "%.0e." % (level, w, label, a, b, rel, REL_EXACT))
        rows.append((w, fmin, fmax, fmean))
    return rows


# ===========================================================================
# SECTION F -- THE y+ BIRTH ARMS Y-1..Y-5 (T5c S6.2), CARRIED UNCHANGED
# ===========================================================================
def _locate_patch_list(text, patch):
    j = text.find("boundaryField")
    if j < 0:
        return None
    k = text.find(patch, j)
    if k < 0:
        return None
    m = re.search(r"nonuniform\s+List<scalar>\s*(\d+)\s*\(", text[k:])
    if not m:
        return None
    st = k + m.end()
    en = text.find(")", st)
    if en < 0:
        return None
    return st, en


def _write_plant(work_field, base_text, span, values):
    st, en = span
    with open(work_field, "w") as fh:
        fh.write(base_text[:st] + "\n" + "\n".join(repr(v) for v in values)
                 + "\n" + base_text[en:])


class Arm:
    """One birth arm.  BOTH limbs must be recorded or the arm is a FAILED
    control, never a passing one (T5c S6.2's closing sentence)."""

    def __init__(self, aid, title):
        self.aid = aid
        self.title = title
        self.positive = None
        self.negative = None
        self.strengthening = []

    def pos(self, ok, msg):
        self.positive = (ok, msg)

    def neg(self, ok, msg):
        self.negative = (ok, msg)

    def strong(self, ok, msg):
        self.strengthening.append((ok, msg))

    def report(self):
        if self.positive is None or self.negative is None:
            refuse("arm %s printed only one limb. An arm that prints one limb "
                   "is a FAILED control, not a passing one." % self.aid)
        print("  %s %s" % (self.aid, self.title))
        print("      POSITIVE (must be SEEN) : %-4s %s"
              % ("ok" if self.positive[0] else "FAIL", self.positive[1]))
        print("      NEGATIVE (must NOT fire): %-4s %s"
              % ("ok" if self.negative[0] else "FAIL", self.negative[1]))
        for ok, msg in self.strengthening:
            print("      strengthening          : %-4s %s"
                  % ("ok" if ok else "FAIL", msg))
        return [m for ok, m in [self.positive, self.negative]
                + self.strengthening if not ok]


def birth_requirement(case_dir, fld, areas, wall=ARM_WALL, level=ARM_LEVEL):
    """T5c S6.2 arms Y-1..Y-5, carried unchanged with the y+ repair they
    authorise (VERIFICATION_CHARTER S2d.11.2 binding condition 1)."""
    print("\nBIRTH REQUIREMENT ON THE y+ READER (T5c S6, VERIFICATION_CHARTER")
    print("S2d.11.2 condition 1) -- planted on wall %s at level %s, in a "
          "scratch copy of the producer's own field." % (wall, level))

    A = areas[wall]
    totA = sum(A)
    base_text = _strip(fld)
    span = _locate_patch_list(base_text, wall)
    if span is None:
        refuse("birth requirement: wall %s is not a nonuniform list in %s"
               % (wall, fld))
    base_vals = read_patch_field(fld, wall)
    if base_vals is None or len(base_vals) != len(A):
        refuse("birth requirement: base read of %s returned %s values against "
               "%d areas" % (wall, "None" if base_vals is None else len(base_vals),
                             len(A)))
    n = len(base_vals)
    base_area = R_area(base_vals, A)
    base_max = R_max(base_vals)
    base_q95 = R_q95(base_vals, A)
    base_med = R_median_area(base_vals, A)

    tmp = tempfile.mkdtemp(prefix="t5e_yplus_plant_")
    failures = []
    arms = []
    try:
        work = os.path.join(tmp, str(ENDTIME), "air")
        os.makedirs(work)
        wf = os.path.join(work, "yPlus")
        shutil.copy2(fld, wf)

        # ---- Y-1 OFFSET ------------------------------------------------
        a1 = Arm("Y-1", "OFFSET -- R_area sees a real signal")
        planted = [v + PLANT_OFFSET for v in base_vals]
        _write_plant(wf, base_text, span, planted)
        got = read_patch_field(wf, wall)
        if got is None or len(got) != n:
            a1.pos(False, "the reader could not read the planted copy")
            a1.neg(False, "not reached: the positive limb did not read back")
        else:
            moved = R_area(got, A) - base_area
            rel = abs(moved - PLANT_OFFSET) / PLANT_OFFSET
            a1.pos(rel <= REL_EXACT,
                   "R_area moved %.12e against the closed-form %.12e "
                   "(relative %.3e, bound %.0e)"
                   % (moved, PLANT_OFFSET, rel, REL_EXACT))
            again = read_patch_field(wf, wall)
            d0 = R_area(again, A) - R_area(got, A)
            a1.neg(d0 == 0.0,
                   "two reads of identical bytes differ by %r (must be exactly "
                   "0.0)" % d0)
            worst = 0.0
            for i in range(n):
                den = abs(base_vals[i] + PLANT_OFFSET)
                den = den if den > 0 else 1.0
                worst = max(worst, abs(got[i] - (base_vals[i] + PLANT_OFFSET)) / den)
            a1.strong(worst <= REL_FACE,
                      "every one of the %d planted faces reads back as "
                      "base+plant, worst relative %.3e (bound %.0e)"
                      % (n, worst, REL_FACE))
        arms.append(a1)

        # ---- Y-2 SPIKE SPECIFICITY -------------------------------------
        a2 = Arm("Y-2", "SPIKE SPECIFICITY -- R_area is NOT the old statistic")
        big = max(range(n), key=lambda i: (A[i], i))
        spiked = list(base_vals)
        spiked[big] = spiked[big] + PLANT_SPIKE
        _write_plant(wf, base_text, span, spiked)
        got2 = read_patch_field(wf, wall)
        if got2 is None or len(got2) != n:
            a2.pos(False, "the reader could not read the spiked copy")
            a2.neg(False, "not reached: the positive limb did not read back")
        else:
            dmax = R_max(got2) - base_max
            a2.pos(dmax >= Y2_SEEN_FRACTION * PLANT_SPIKE,
                   "R_max moved %.6f against the required >= %.6f"
                   % (dmax, Y2_SEEN_FRACTION * PLANT_SPIKE))
            bound = Y2_BLIND_SLACK * PLANT_SPIKE * A[big] / totA
            darea = abs(R_area(got2, A) - base_area)
            a2.neg(darea <= bound,
                   "R_area moved %.9e against the blindness bound %.9e -- the "
                   "area average is NEARLY BLIND to the point peak the old gate "
                   "was dominated by" % (darea, bound))
            arg = max(range(n), key=lambda i: (got2[i], i))
            a2.strong(arg == big,
                      "the argmax of the planted field is face %d, the face the "
                      "spike was planted into (%d)" % (arg, big))
            den = abs(base_vals[big] + PLANT_SPIKE)
            rel = abs(got2[big] - (base_vals[big] + PLANT_SPIKE)) / (den if den else 1.0)
            a2.strong(rel <= REL_FACE,
                      "face %d reads back %.9f against base+spike %.9f "
                      "(relative %.3e)"
                      % (big, got2[big], base_vals[big] + PLANT_SPIKE, rel))
            others = max((abs(got2[i] - base_vals[i]) for i in range(n) if i != big),
                         default=0.0)
            a2.strong(others == 0.0,
                      "every one of the other %d faces is unchanged (max "
                      "|delta| %r)" % (n - 1, others))
        arms.append(a2)

        # ---- Y-3 AREA WEIGHTING IS REAL --------------------------------
        a3 = Arm("Y-3", "AREA WEIGHTING IS REAL -- not a face count in disguise")
        k = max(1, int(round(0.10 * n)))
        by_area = sorted(range(n), key=lambda i: (-A[i], i))[:k]
        dec_area = sum(A[i] for i in by_area)
        area_pred = PLANT_OFFSET * (dec_area / totA)
        fc_pred = PLANT_OFFSET * (k / n)
        sep = abs(area_pred - fc_pred) / (abs(fc_pred) if fc_pred else 1.0)
        if sep <= Y3_MIN_SEPARATION:
            refuse("arm Y-3 REFUSES: the area-weighted prediction %.12e and the "
                   "FACE-COUNT prediction %.12e differ by only %.4f %%, not more "
                   "than the registered %.0f %%. A weighting control on a patch "
                   "this uniform is VACUOUS and must say so rather than pass."
                   % (area_pred, fc_pred, 100 * sep, 100 * Y3_MIN_SEPARATION))
        dec_vals = list(base_vals)
        for i in by_area:
            dec_vals[i] = dec_vals[i] + PLANT_OFFSET
        _write_plant(wf, base_text, span, dec_vals)
        got3 = read_patch_field(wf, wall)
        if got3 is None or len(got3) != n:
            a3.pos(False, "the reader could not read the decile plant")
            a3.neg(False, "not reached: the positive limb did not read back")
        else:
            moved = R_area(got3, A) - base_area
            rel_a = abs(moved - area_pred) / (abs(area_pred) if area_pred else 1.0)
            a3.pos(rel_a <= REL_EXACT,
                   "R_area moved %.12e against the AREA prediction %.12e "
                   "(relative %.3e); decile k=%d of %d faces holds %.6f of the "
                   "patch area against %.6f of its face count"
                   % (moved, area_pred, rel_a, k, n, dec_area / totA, k / n))
            rel_f = abs(moved - fc_pred) / (abs(fc_pred) if fc_pred else 1.0)
            a3.neg(rel_f > Y3_MIN_SEPARATION,
                   "R_area did NOT move by the FACE-COUNT prediction %.12e "
                   "(differs by %.4f %%, required > %.0f %%)"
                   % (fc_pred, 100 * rel_f, 100 * Y3_MIN_SEPARATION))
        arms.append(a3)

        # ---- Y-4 QUANTILE SENSITIVITY ----------------------------------
        a4 = Arm("Y-4", "QUANTILE SENSITIVITY -- R_q95 is a quantile")
        order = sorted(range(n), key=lambda i: (base_vals[i], i))
        _v95, i95, pos95 = area_quantile(base_vals, A, Q95)
        _v50, i50, pos50 = area_quantile(base_vals, A, Q50)
        tail = order[pos95:]
        if i50 in tail:
            refuse("arm Y-4 REFUSES: the area-weighted MEDIAN face is inside "
                   "the 95th-percentile tail on wall %s level %s, so the "
                   "negative limb is vacuous." % (wall, level))
        q_vals = list(base_vals)
        for i in tail:
            q_vals[i] = q_vals[i] + PLANT_OFFSET
        _write_plant(wf, base_text, span, q_vals)
        got4 = read_patch_field(wf, wall)
        if got4 is None or len(got4) != n:
            a4.pos(False, "the reader could not read the tail plant")
            a4.neg(False, "not reached: the positive limb did not read back")
        else:
            dq = R_q95(got4, A) - base_q95
            rel_q = abs(dq - PLANT_OFFSET) / PLANT_OFFSET
            a4.pos(rel_q <= REL_EXACT,
                   "R_q95 moved %.12e against the plant %.12e (relative %.3e); "
                   "the tail is %d of %d faces"
                   % (dq, PLANT_OFFSET, rel_q, len(tail), n))
            dmed = R_median_area(got4, A) - base_med
            a4.neg(dmed == 0.0,
                   "the area-weighted MEDIAN moved by %r (must be exactly 0.0)"
                   % dmed)
            den = abs(base_vals[i95] + PLANT_OFFSET)
            rel = abs(got4[i95] - (base_vals[i95] + PLANT_OFFSET)) / (den if den else 1.0)
            a4.strong(rel <= REL_FACE,
                      "the 95 %% crossing face (index %d, order position %d of "
                      "%d) reads back as base+plant, relative %.3e"
                      % (i95, pos95, n, rel))
            a4.strong(got4[i50] == base_vals[i50],
                      "the median face (index %d, order position %d) is "
                      "unchanged" % (i50, pos50))
        arms.append(a4)

        # ---- Y-5 SCHEMA / TUPLE INTEGRITY ------------------------------
        a5 = Arm("Y-5", "SCHEMA / TUPLE INTEGRITY")
        a5.pos(True,
               "before any plant, read_patch_field's parsed face count was "
               "asserted equal to the mesh's own boundary nFaces for all %d "
               "registered walls at this level (assert_section_6_1 row READER)"
               % len(YPLUS_WALLS))
        a5.neg(True,
               "the REFUSAL is armed on both a ZERO count and a count "
               "disagreeing with the mesh; it did not fire here, which is the "
               "required outcome for the negative limb")
        arms.append(a5)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for a in arms:
        failures.extend(a.report())
    if failures:
        refuse("y+ BIRTH REQUIREMENT FAILED -- %d limb(s): %s"
               % (len(failures), " | ".join(failures)))
    print("  ALL FIVE ARMS PRINTED BOTH LIMBS AND PASSED.")
    return True


# ===========================================================================
# SECTION G -- THE y+ GATE (T5c S5), CARRIED UNCHANGED
# ===========================================================================
def read_level_statistics(case_dir, fld, areas):
    out = {}
    for w in YPLUS_WALLS:
        v = read_patch_field(fld, w)
        if v is None:
            return None, "read_patch_field returned None for wall %s" % w
        A = areas[w]
        if len(v) != len(A):
            return None, ("wall %s: %d values against %d areas"
                          % (w, len(v), len(A)))
        out[w] = dict(R_area=R_area(v, A), R_max=R_max(v),
                      R_q95=R_q95(v, A), fc_mean=R_facecount_mean(v),
                      nFaces=len(v), area=sum(A))
    return out, None


def gate_yplus_t5e(stats, level):
    """T5c S5, carried unchanged.  Y-SUBLAYER on R_max (binding condition 3),
    then Y-LADDER on R_area.  Both breaches are NOT A RESULT."""
    tgt = YPLUS_TARGET[level]
    bound = tgt * YPLUS_TARGET_TOL

    over = {w: stats[w]["R_max"] for w in YPLUS_WALLS
            if stats[w]["R_max"] > YPLUS_MAX}
    if over:
        return dict(state=VERDICT_NAR, stats=stats, clause="Y-SUBLAYER",
                    why="R_max exceeds the registered sublayer bound %.1f on: "
                        "%s -- a physics precondition, and it stays on the "
                        "POINT MAXIMUM because one face outside the viscous "
                        "sublayer invalidates the wall treatment there"
                        % (YPLUS_MAX, ", ".join("%s=%.6f" % (w, v)
                                                for w, v in sorted(over.items()))))
    drift = {w: stats[w]["R_area"] for w in YPLUS_WALLS
             if stats[w]["R_area"] > bound}
    if drift:
        return dict(state=VERDICT_NAR, stats=stats, clause="Y-LADDER",
                    why="R_area exceeds %.1fx the level target %.2f (bound "
                        "%.4f) on: %s -- the ladder is not the registered ladder"
                        % (YPLUS_TARGET_TOL, tgt, bound,
                           ", ".join("%s=%.6f" % (w, v)
                                     for w, v in sorted(drift.items()))))
    return dict(state="MET", stats=stats, clause=None,
                why="all %d registered walls inside R_max %.1f (Y-SUBLAYER) and "
                    "R_area within %.1fx the level target %.2f (Y-LADDER, bound "
                    "%.4f)" % (len(YPLUS_WALLS), YPLUS_MAX, YPLUS_TARGET_TOL,
                               tgt, bound))


def observed_order(v_c, v_m, v_f, r21, r32):
    def _p(a, b, r):
        if a <= 0 or b <= 0 or r <= 1.0:
            return None
        try:
            return math.log(a / b) / math.log(r)
        except ValueError:
            return None
    return _p(v_c, v_m, r32), _p(v_m, v_f, r21)


def print_both_statistics(levels_stats, r21, r32):
    """VERIFICATION_CHARTER S2d.11.2 BINDING CONDITION 4, carried with the
    repair it conditions."""
    print("\nBOTH STATISTICS, EVERY WALL, EVERY LEVEL "
          "(VERIFICATION_CHARTER S2d.11.2 condition 4)")
    print("  bound at each level = YPLUS_TARGET[lv] x YPLUS_TARGET_TOL = "
          "c %.2f, m %.2f, f %.2f"
          % (YPLUS_TARGET["c"] * YPLUS_TARGET_TOL,
             YPLUS_TARGET["m"] * YPLUS_TARGET_TOL,
             YPLUS_TARGET["f"] * YPLUS_TARGET_TOL))
    print("  %-12s %-3s %11s %8s %11s %8s %11s %11s"
          % ("wall", "lv", "R_area", "margin", "R_max", "margin", "R_q95", "fc_mean"))
    nonmono = []
    for w in YPLUS_WALLS:
        for lv in LEVELS:
            s = levels_stats[lv][w]
            b = YPLUS_TARGET[lv] * YPLUS_TARGET_TOL
            print("  %-12s %-3s %11.6f %8.4f %11.6f %8.4f %11.6f %11.6f"
                  % (w, lv, s["R_area"], s["R_area"] / b, s["R_max"],
                     s["R_max"] / b, s["R_q95"], s["fc_mean"]))
        mx = [levels_stats[lv][w]["R_max"] for lv in LEVELS]
        ar = [levels_stats[lv][w]["R_area"] for lv in LEVELS]
        p_max = observed_order(mx[0], mx[1], mx[2], r21, r32)
        p_area = observed_order(ar[0], ar[1], ar[2], r21, r32)
        mono_max = mx[0] > mx[1] > mx[2]
        mono_area = ar[0] > ar[1] > ar[2]
        print("  %-12s ->  R_max observed order p(c->m) %s p(m->f) %s  %s"
              % (w, "%.3f" % p_max[0] if p_max[0] is not None else "n/a",
                 "%.3f" % p_max[1] if p_max[1] is not None else "n/a",
                 "MONOTONE decreasing" if mono_max
                 else "*** NON-MONOTONE UNDER REFINEMENT ***"))
        print("  %-12s ->  R_area observed order p(c->m) %s p(m->f) %s  %s"
              % (w, "%.3f" % p_area[0] if p_area[0] is not None else "n/a",
                 "%.3f" % p_area[1] if p_area[1] is not None else "n/a",
                 "MONOTONE decreasing" if mono_area
                 else "*** NON-MONOTONE UNDER REFINEMENT ***"))
        if not mono_max:
            nonmono.append((w, "R_max"))
        if not mono_area:
            nonmono.append((w, "R_area"))
    if nonmono:
        print("  NON-MONOTONE UNDER REFINEMENT: %s"
              % ", ".join("%s/%s" % x for x in nonmono))
    else:
        print("  NON-MONOTONE UNDER REFINEMENT: none on either statistic.")
    return nonmono


# ===========================================================================
# SECTION R -- RESIDUAL EVIDENCE.  **REPORTED, NEVER GATED.**
#
# T19/T19b's idiom, and the family has litigated this in source before:
# `T4:391` and `K0c:77` both argue that a residual is not convergence.  T5 S5.5
# writes no residualControl and names L-141 as the reason.  Nothing below feeds
# any gate; `--selftest` proves it two ways.
# ===========================================================================
RESIDUAL_FIELDS = ("p_rgh", "k", "omega")
RESIDUAL_RE = re.compile(
    r"Solving for (\w+), Initial residual = ([-0-9.eE+]+)")


def residual_report(case_dir):
    """REPORTED, NEVER GATED.  The FIRST initial residual per Time block for
    each named field.  Returns a dict this file's gates never receive."""
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return dict(available=False, why="no log.solve")
    series = {f: [] for f in RESIDUAL_FIELDS}
    seen_this_block = set()
    for line in open(log, errors="replace"):
        if line.startswith("Time = "):
            seen_this_block = set()
            continue
        m = RESIDUAL_RE.search(line)
        if not m:
            continue
        f, v = m.group(1), float(m.group(2))
        if f in series and f not in seen_this_block:
            series[f].append(v)
            seen_this_block.add(f)
    out = dict(available=True, series={})
    for f, s in series.items():
        if not s:
            out["series"][f] = None
            continue
        tail = s[-500:] if len(s) >= 500 else s
        pos = [abs(v) for v in tail if v > 0]
        slope = None
        if len(pos) >= 2:
            n = len(pos)
            xs = list(range(n))
            ys = [math.log10(v) for v in pos]
            mx = sum(xs) / n
            my = sum(ys) / n
            den = sum((x - mx) ** 2 for x in xs)
            if den > 0:
                slope = 1000.0 * sum((x - mx) * (y - my)
                                     for x, y in zip(xs, ys)) / den
        out["series"][f] = dict(n=len(s), first=s[0], last=s[-1],
                                tail_min=min(tail), tail_max=max(tail),
                                slope_dec_per_1000=slope)
    return out


def print_residual_report(reports):
    print("\nRESIDUAL EVIDENCE -- **REPORTED, NEVER GATED** "
          "(%s)" % _l342_class("initial_residual"))
    print("  T5 S5.5 writes no residualControl and names the reason: in T1c a")
    print("  genuinely unconverged case sat at residual 4e-05 (L-141). Nothing")
    print("  below feeds any gate; clause (1) is decided ONLY by the checkpoint")
    print("  delta above. These lines corroborate; they never grade.")
    print("  %-3s %-7s %6s %12s %12s %12s %12s %14s"
          % ("lv", "field", "n", "first", "last", "tail min", "tail max",
             "log10 slope"))
    for lv in LEVELS:
        r = reports[lv]
        if not r.get("available"):
            print("  %-3s (%s)" % (lv, r.get("why")))
            continue
        for f in RESIDUAL_FIELDS:
            s = r["series"].get(f)
            if s is None:
                print("  %-3s %-7s NOT MEASURED (no `Solving for %s` lines)"
                      % (lv, f, f))
                continue
            print("  %-3s %-7s %6d %12.4e %12.4e %12.4e %12.4e %14s"
                  % (lv, f, s["n"], s["first"], s["last"], s["tail_min"],
                     s["tail_max"],
                     "%+.3f dec/1000" % s["slope_dec_per_1000"]
                     if s["slope_dec_per_1000"] is not None else "n/a"))


# ===========================================================================
# THE REGISTERED ORDER -- WITH CLAUSE (1) BACK IN POSITION (1)
# ===========================================================================
def grade_row(name, ref_row, vals, clause1_states, yplus_states, r21, r32,
              identity_ok=True):
    """THE REGISTERED ORDER (T5 S7.5 + S16.3.1, rule 5), top to bottom.

    (1) IS T5 S7.5's OWN STEP 1 AND IT IS EVALUATED FIRST -- before the y+
    clause and before any triple.  `analyse_t5b.py:657` put the y+ clause at
    (1) and dropped this step; `analyse_t5c.py:532` copied that verbatim.  The
    instrument is the T5 S5.5 CHECKPOINT DELTA, never a residual.

    NOTE THE SIGNATURE: no residual state is passed in, so no residual can
    reach a verdict even by mistake.  This is checked in --selftest."""
    out = dict(row=name, values=vals)
    # (1) any ladder level NOT CONVERGED -> NOT A RESULT   [T5 S7.5 step 1]
    notconv = [lv for lv in LEVELS
               if clause1_states[lv]["state"] != "CONVERGED"]
    if notconv:
        out.update(verdict=VERDICT_NAR, clause="(1) T5 S5.5 convergence",
                   why="registered criterion (1): level(s) %s NOT CONVERGED. %s"
                       % (",".join(notconv), clause1_states[notconv[0]]["why"]))
        return out
    # (2) any level's y+ gate not MET -> NOT A RESULT      [T5 S16.3.1, T5c stat]
    bad = [lv for lv in LEVELS if yplus_states[lv]["state"] != "MET"]
    if bad:
        out.update(verdict=VERDICT_NAR, clause="(2) y+",
                   why="y+ gate not MET on level(s) %s: %s"
                       % (",".join(bad), yplus_states[bad[0]]["why"]))
        return out
    if any(vals.get(lv) is None for lv in LEVELS):
        out.update(verdict=VERDICT_NAR, why="a level produced no value")
        return out
    f_c, f_m, f_f = vals["c"], vals["m"], vals["f"]
    tri = classify_triple(f_c, f_m, f_f)
    out["triple"] = tri
    # (3) triple not CONVERGING -> NOT A RESULT
    if tri != "CONVERGING":
        out.update(verdict=VERDICT_NAR, clause="(3) triple",
                   why="grid triple is %s (rule 5): fine value %.6g printed, "
                       "not graded" % (tri, f_f))
        return out
    p, gci = gci_triple(f_c, f_m, f_f, r21, r32)
    out["order"] = p
    out["gci"] = gci
    # (4) reference absent -> BLOCKED
    if ref_row is None or ref_row.get("value") is None:
        out.update(verdict=VERDICT_BLOCKED,
                   why="no reference value; fine value %.6g and triple %s "
                       "REPORTED" % (f_f, tri))
        return out
    # (5) G5 identity guard
    if not identity_ok:
        out.update(verdict=VERDICT_NAR + " -- identity",
                   why="the reference T_sur is within %.1f K of an imposed "
                       "bound (T5 S3)" % G5_IDENTITY_MARGIN_K)
        return out
    ref = float(ref_row["value"])
    band = combined_band(ref_row)
    if band is None:
        out.update(verdict=VERDICT_BLOCKED, why="no band registered for this row")
        return out
    out["ref"] = ref
    out["band_abs"] = band
    dev_pct = 100.0 * abs(f_f - ref) / abs(ref) if ref else float("inf")
    out["dev_pct"] = dev_pct
    # (6) below the intrinsic floor -> GATE REACHED
    if dev_pct < INTRINSIC_FLOOR_PCT:
        out.update(verdict=VERDICT_REACHED,
                   why="deviation %.3f %% is below the registered intrinsic "
                       "floor %.1f %% (T5 S7.4 ambient ambiguity)"
                       % (dev_pct, INTRINSIC_FLOOR_PCT))
        return out
    # (7) band
    out.update(verdict=band_verdict(f_f, ref, band),
               why="fine %.6g vs reference %.6g, band +/- %.6g, GCI %s"
                   % (f_f, ref, band, ("%.4f %%" % (100 * gci)) if gci else "n/a"))
    return out


# ===========================================================================
# SECTION H -- run()
# ===========================================================================
def run(root):
    if not os.path.isfile(REFERENCE):
        refuse("no reference at %s" % REFERENCE)
    ref = json.load(open(REFERENCE))
    if not ref.get("provenance", {}).get("digitised"):
        refuse("the reference is not marked digitised")

    print("T5e comparator -- registration %s" % REGISTRATION)
    if GRADING_PATH_FREEZE_COMMIT == "PIN-AT-FREEZE":
        print("*** GRADING_PATH_FREEZE_COMMIT is `PIN-AT-FREEZE`: THIS FILE IS "
              "NOT YET FROZEN. ***")
        print("    The supervisor sets the pin AT FREEZE. Any output produced "
              "in this state is a")
        print("    DRY RUN and is NOT A GRADED RECORD, whatever the rows below "
              "say.")
    else:
        print("grading path frozen by commit %s; registration sha256 %s"
              % (GRADING_PATH_FREEZE_COMMIT, REGISTRATION_SHA256))
    print("re-grades: existing artifacts under %s. NO SOLVER COMPUTE." % root)

    for line in assert_frozen_predecessor_bytes():
        print("frozen predecessor verified: %s" % line)
    lo_ln, hi_ln = assert_criterion_clause_witness()
    tol, stride = parse_registered_criterion()
    print("CLAUSE (1) INSTRUMENT READ FROM ITS OWN REGISTRATION: "
          "T5_PREREGISTRATION.md lines %d-%d, sha256 %s..., tolerance %g x "
          "range, checkpoints endTime-%d and endTime. NOTHING NEW IS "
          "REGISTERED HERE." % (lo_ln, hi_ln, T5_CRITERION_SHA256[:16], tol,
                                stride))
    carried = assert_thresholds_carried_over()
    print("THRESHOLD CARRY-OVER ASSERTED against analyse_t5b.py and "
          "analyse_t5c.py: %d names identical. `only the ORDER changes` is a "
          "CHECK here, not a claim." % len(carried))
    print("L-342 classes: %s"
          % "; ".join("%s=%s" % (f, _l342_class(f).split(":")[0])
                      for f in ("T", "checkpoint_pair", "initial_residual",
                                "yPlus_field", "core_min",
                                "ExecutionTime_line_count")))

    cells = {}
    areas_by_level = {}
    fields = {}
    levels_stats = {}
    yplus = {}
    clause1 = {}
    completion = {}
    residuals = {}
    for lv in LEVELS:
        case = CASE_OF[lv]
        case_dir = os.path.join(root, case)
        if not os.path.isdir(case_dir):
            refuse("no case directory %s" % case_dir)
        mesh = os.path.join(case_dir, "constant", "air", "polyMesh")
        a, bnd = patch_areas(mesh, YPLUS_WALLS)
        check_wall_set(bnd)
        areas_by_level[lv] = a
        m = re.search(r"cells:\s+(\d+)",
                      open(os.path.join(case_dir, "log.checkMesh"),
                           errors="replace").read())
        if not m:
            refuse("%s: no cell count in log.checkMesh" % case)
        cells[lv] = int(m.group(1))
        if cells[lv] != CELLS_REGISTERED[lv]:
            refuse("level %s has %d cells, registered %d -- the ladder is not "
                   "the registered ladder" % (lv, cells[lv], CELLS_REGISTERED[lv]))
        ok, why, notes = check_completion(root, case)
        completion[lv] = (ok, why, notes)

        fld, rows61 = assert_section_6_1(case_dir, lv, a, bnd)
        fields[lv] = fld
        identity_proof(case_dir, fld, lv)
        st, err = read_level_statistics(case_dir, fld, a)
        if st is None:
            refuse("level %s: %s" % (lv, err))
        levels_stats[lv] = st
        yplus[lv] = gate_yplus_t5e(st, lv)
        clause1[lv] = gate_clause1(case_dir, lv)
        residuals[lv] = residual_report(case_dir)

        print("\n  level %s  %-11s cells %7d  completion: %s"
              % (lv, case, cells[lv],
                 "COMPLETE" if ok else "NOT COMPLETE (%s)" % why))
        for r in rows61:
            print("      S6.1  %s" % r)
        print("      clause (1): %s -- %s" % (clause1[lv]["state"],
                                              clause1[lv]["why"]))
        print("      y+ gate  : %s -- %s" % (yplus[lv]["state"],
                                             yplus[lv]["why"]))
        for nt in notes:
            print("      infra: %s" % nt)

    r21, r32 = measured_ratios(cells)
    print("\nMEASURED refinement ratios r21 = %.6f (MEDIUM->FINE) and "
          "r32 = %.6f (COARSE->MEDIUM)" % (r21, r32))

    if not all(completion[lv][0] for lv in LEVELS):
        print("\nNOT A RESULT on every graded row: a level is not complete "
              "(rule 4 is all-or-nothing).")
        for lv in LEVELS:
            if not completion[lv][0]:
                print("  level %s: %s" % (lv, completion[lv][1]))
        return 1

    # RULE 3 ON THE CLAUSE-(1) READER, before its zeros or non-zeros are used.
    clause1_birth_requirement(os.path.join(root, CASE_OF[ARM_LEVEL]))
    # T5c binding condition 1, carried with the repair.
    birth_requirement(os.path.join(root, CASE_OF[ARM_LEVEL]),
                      fields[ARM_LEVEL], areas_by_level[ARM_LEVEL])

    print_clause1(clause1)
    print_residual_report(residuals)
    print_both_statistics(levels_stats, r21, r32)

    rows = []
    for name, patch in sorted(GRADED_H.items()):
        vals = {}
        for lv in LEVELS:
            v, err = face_mean_h(os.path.join(root, CASE_OF[lv]), patch,
                                 areas_by_level[lv])
            vals[lv] = v
            if v is None:
                print("  %s level %s: %s" % (name, lv, err))
        rows.append(grade_row(name, ref["rows"].get(name), vals, clause1,
                              yplus, r21, r32))
    for name, patch in sorted(GRADED_T.items()):
        vals = {}
        for lv in LEVELS:
            v, err = face_mean_T_C(os.path.join(root, CASE_OF[lv]), patch,
                                   areas_by_level[lv])
            vals[lv] = v
        rr = ref["rows"].get(name)
        idok = True
        if rr and rr.get("value") is not None:
            rv = float(rr["value"])
            idok = (abs(rv - G5_BOUND_LO_C) >= G5_IDENTITY_MARGIN_K and
                    abs(rv - G5_BOUND_HI_C) >= G5_IDENTITY_MARGIN_K)
        rows.append(grade_row(name, rr, vals, clause1, yplus, r21, r32,
                              identity_ok=idok))

    print("\nROWS -- each carries the pre-repair and superseded states beside it")
    for r in rows:
        print("  %-4s %-22s %s" % (r["row"], r["verdict"], r["why"]))
        print("       fired at clause %s" % r.get("clause", "(none: graded through)"))
        print("       %s" % PRE_REPAIR_STATE)
        print("       %s" % SUPERSEDED_STATE)
        print("       values printed, not graded: c %s  m %s  f %s"
              % tuple("%.6g" % r["values"][lv] if r["values"].get(lv) is not None
                      else "n/a" for lv in LEVELS))

    graded = list(rows)
    npass = sum(1 for r in graded if r["verdict"] == VERDICT_PASS)
    nnar = sum(1 for r in graded if r["verdict"].startswith(VERDICT_NAR))
    print("\nTALLY: %d of %d graded rows PASS; %d NOT A RESULT. The %d REPORTED "
          "rows (%s) are a ROW CLASS, not a verdict, and are EXCLUDED from this "
          "census (ruling D534)."
          % (npass, len(graded), nnar, len(REPORTED_ROWS),
             ", ".join(REPORTED_ROWS)))
    if nnar == len(graded):
        print("NO GCI IS QUOTABLE FROM ANY ROW ABOVE: rule 5 clause (1) fired "
              "before any triple was classified.")
    if GRADING_PATH_FREEZE_COMMIT == "PIN-AT-FREEZE":
        print("*** DRY RUN: GRADING_PATH_FREEZE_COMMIT is unset. The rows above "
              "are NOT a graded record. ***")
    return 0 if npass == len(graded) else 1


# ===========================================================================
# SELFTEST -- BOTH DIRECTIONS ON EVERY CONTROL
# ===========================================================================
def _forge_scalar_field(path, vals):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                 "    class volScalarField;\n    object T;\n}\n\n"
                 "dimensions      [0 0 0 1 0 0 0];\n\n"
                 "internalField   nonuniform List<scalar> \n%d\n(\n" % len(vals))
        fh.write("\n".join(repr(v) for v in vals))
        fh.write("\n)\n;\n\nboundaryField\n{\n}\n\n"
                 "// ************ //\n")


def _forge_vector_field(path, vals):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                 "    class volVectorField;\n    object U;\n}\n\n"
                 "dimensions      [0 1 -1 0 0 0 0];\n\n"
                 "internalField   nonuniform List<vector> \n%d\n(\n" % len(vals))
        fh.write("\n".join("(%r %r %r)" % v for v in vals))
        fh.write("\n)\n;\n\nboundaryField\n{\n}\n\n"
                 "// ************ //\n")


def _forge_level(root, case, converged, seed=0.0):
    """A synthetic two-checkpoint case.  converged=True builds a pair whose
    change is BELOW 1e-6 x range; converged=False builds one above it."""
    cd = os.path.join(root, case)
    lo = [300.0 + 0.001 * i for i in range(200)]        # range 0.199
    rng = max(lo) - min(lo)
    step = (0.5 * CONV_REL_TOL * rng) if converged else (100.0 * CONV_REL_TOL * rng)
    hi = [v + step for v in lo]
    hi[7] += seed
    for t, vals in ((CONV_CHECKPOINT_LO, lo), (CONV_CHECKPOINT_HI, hi)):
        _forge_scalar_field(os.path.join(cd, str(t), "air", "T"), vals)
        _forge_scalar_field(os.path.join(cd, str(t), "epoxy", "T"), vals)
    ulo = [(1.0 + 0.01 * i, 0.0, 0.0) for i in range(50)]
    ustep = step
    uhi = [(u[0] + ustep, u[1], u[2]) for u in ulo]
    for t, vals in ((CONV_CHECKPOINT_LO, ulo), (CONV_CHECKPOINT_HI, uhi)):
        _forge_vector_field(os.path.join(cd, str(t), "air", "U"), vals)
    return cd


def selftest():
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("analyse_t5e.py --selftest -- SYNTHETIC FIXTURES ONLY, no run tree read")
    src = open(os.path.abspath(__file__), errors="replace").read()

    # ------------------------------------------------------------------
    # 0. THE PIN IS NEVER SET BY THIS FILE
    # ------------------------------------------------------------------
    # Matched with a LINE-ANCHORED regex, never `src.count` on the literal: a
    # scan whose own source line contains the needle counts itself, and that
    # off-by-one is exactly the kind of self-referential miscount this lab has
    # been bitten by before.
    def _pin(name):
        return re.findall(r'^%s\s*=\s*"([^"]*)"\s*$' % name, src, re.M)
    ok(_pin("GRADING_PATH_FREEZE_COMMIT") == ["PIN-AT-FREEZE"],
       "GRADING_PATH_FREEZE_COMMIT is `PIN-AT-FREEZE` and is assigned exactly "
       "once: the supervisor sets the pin AT FREEZE and this file never sets "
       "it itself (found %r)" % _pin("GRADING_PATH_FREEZE_COMMIT"))
    ok(_pin("REGISTRATION_SHA256") == ["PIN-AT-FREEZE"],
       "REGISTRATION_SHA256 is `PIN-AT-FREEZE` for the same reason (found %r)"
       % _pin("REGISTRATION_SHA256"))
    ok(len(_pin("FROZEN_T5B_SHA256")[0]) == 64
       and len(_pin("FROZEN_T5C_SHA256")[0]) == 64
       and len(_pin("T5_CRITERION_SHA256")[0]) == 64,
       "every freeze witness this file DOES set is a full 64-hex sha256 of the "
       "disk bytes, never a 40-hex git blob SHA-1 the freeze instrument is "
       "blind to (L-450; T5c_RESULTS.md S5a forward-only adoption)")

    # ------------------------------------------------------------------
    # 1. NO REFERENCE VALUE IS HARD-CODED -- enforced, not asserted
    # ------------------------------------------------------------------
    leaked = []
    if os.path.isfile(REFERENCE):
        rj = json.load(open(REFERENCE))
        for rn, rr in rj.get("rows", {}).items():
            for key in ("value", "uncertainty", "digitisation_increment"):
                v = rr.get(key)
                if isinstance(v, float) and ("%g" % v) in src:
                    leaked.append("%s.%s=%g" % (rn, key, v))
    ok(not leaked, "no reference value appears in this file's own bytes%s"
       % ("" if not leaked else " -- LEAKED: " + ", ".join(leaked)))

    # ------------------------------------------------------------------
    # 2. CLAUSE (1) IN BOTH DIRECTIONS, ON SYNTHETIC LADDERS
    # ------------------------------------------------------------------
    tmp = tempfile.mkdtemp(prefix="t5e_st_")
    try:
        conv_case = _forge_level(tmp, "CONV", True)
        nonconv_case = _forge_level(tmp, "NONCONV", False)
        gc = gate_clause1(conv_case, "f")
        ok(gc["state"] == "CONVERGED",
           "DIRECTION 1: a synthetic ladder level whose change is 0.5 x the "
           "registered tolerance returns CONVERGED (%s)"
           % "; ".join("%s/%s delta %.3e tol %.3e" % (r["region"], r["field"],
                                                      r["delta"], r["tol"])
                       for r in gc["rows"]))
        gn = gate_clause1(nonconv_case, "f")
        ok(gn["state"] == "NOT CONVERGED",
           "DIRECTION 2: a synthetic level whose change is 100 x the tolerance "
           "returns NOT CONVERGED")
        ok(all(r["factor"] > 1.0 for r in gn["rows"] if not r["converged"]),
           "and every failing row prints its measured over-by factor "
           "(%s)" % ", ".join("%.0fx" % r["factor"] for r in gn["rows"]))
        ok(gn["rows"][0]["delta"] > 0 and gn["rows"][0]["tol"] > 0
           and gn["rows"][0]["rng"] > 0,
           "the failing row prints the measured delta %.6e, the field range "
           "%.6f and the tolerance %.6e beside its verdict"
           % (gn["rows"][0]["delta"], gn["rows"][0]["rng"], gn["rows"][0]["tol"]))

        # THE ROW GRADER, BOTH DIRECTIONS ON CLAUSE (1)
        c1_conv = {lv: dict(state="CONVERGED", why="synthetic") for lv in LEVELS}
        c1_bad = {lv: dict(state="NOT CONVERGED", why="synthetic")
                  for lv in LEVELS}
        ymet = {lv: dict(state="MET", why="") for lv in LEVELS}
        ynar = {lv: dict(state=VERDICT_NAR, why="planted") for lv in LEVELS}
        R = dict(value=100.0, uncertainty=10.0)
        good = dict(c=80.0, m=91.0, f=95.0)
        g1 = grade_row("X", R, good, c1_conv, ymet, 1.6060, 1.5929)
        ok(g1["verdict"] == VERDICT_PASS,
           "a CONVERGED, y+-MET, CONVERGING triple inside the band still "
           "PASSes -- clause (1) does not break the reachable verdict")
        g2 = grade_row("X", R, good, c1_bad, ymet, 1.6060, 1.5929)
        ok(g2["verdict"] == VERDICT_NAR and g2["clause"].startswith("(1)"),
           "THE SAME ROW with clause (1) failing is NOT A RESULT, and it fires "
           "at clause %s" % g2.get("clause"))
        ok("triple" not in g2,
           "and the triple was NEVER CLASSIFIED -- clause (1) short-circuits "
           "before any GCI could be computed, which is the whole repair")

        # CLAUSE (1) IS **FIRST**: it must beat the y+ clause, not tie with it
        g3 = grade_row("X", R, good, c1_bad, ynar, 1.6060, 1.5929)
        ok(g3["clause"].startswith("(1)"),
           "with BOTH clause (1) and the y+ clause failing, the row fires at "
           "clause (1) -- the registered step 1 is FIRST, ahead of the y+ gate "
           "that analyse_t5b.py:657 numbered (1)")
        g4 = grade_row("X", R, good, c1_conv, ynar, 1.6060, 1.5929)
        ok(g4["verdict"] == VERDICT_NAR and g4["clause"] == "(2) y+",
           "with clause (1) satisfied the y+ clause still fires, at (2)")

        # the one-way property (rule 5)
        div = dict(c=99.0, m=97.0, f=90.5)
        g5 = grade_row("X", R, div, c1_conv, ymet, 1.6060, 1.5929)
        ok(g5["verdict"] == VERDICT_NAR and g5["triple"] == "DIVERGENT",
           "a DIVERGENT triple with a value INSIDE the band is still NOT A "
           "RESULT")
        ok(grade_row("X", R, dict(c=200.0, m=150.0, f=125.0), c1_conv, ymet,
                     1.6060, 1.5929)["verdict"] == VERDICT_FAIL,
           "a CONVERGING triple OUTSIDE the band is GATE FAIL")
        ok(grade_row("X", None, good, c1_conv, ymet, 1.6060,
                     1.5929)["verdict"] == VERDICT_BLOCKED,
           "an absent reference is BLOCKED, not a fail")
        ok(grade_row("X", R, dict(c=99.5, m=99.8, f=99.9), c1_conv, ymet,
                     1.6060, 1.5929)["verdict"] == VERDICT_REACHED,
           "a deviation below the 1.7 %% intrinsic floor is GATE REACHED")
        ok(grade_row("X", R, good, c1_conv, ymet, 1.6060, 1.5929,
                     identity_ok=False)["verdict"].endswith("identity"),
           "the G5 identity guard fires")

        # ------------------------------------------------------------------
        # 3. THE PLANT ON THE CLAUSE-(1) READER, SEEN AND MUTATED
        # ------------------------------------------------------------------
        # The fixture is deliberately NON-UNIFORM in its change: delta_i falls
        # with i, so the SMALLEST-change cell is the LAST one and the argmax is
        # the FIRST.  A fixture with a uniform change would put the plant at
        # cell 0 and the `blinded past cell 0` mutant would see it -- the
        # control would then be untestable, which is how this was caught.
        lo = [300.0 + 0.001 * i for i in range(200)]
        hi = [lo[i] + 1e-9 * (len(lo) - i) for i in range(len(lo))]
        base_d, base_arg = max_abs_delta("scalar", lo, hi)
        i0 = min(range(len(hi)), key=lambda i: (abs(hi[i] - lo[i]), i))
        spiked = list(hi)
        spiked[i0] += PLANT_SPIKE
        d_s, arg_s = max_abs_delta("scalar", lo, spiked)
        ok(d_s >= Y2_SEEN_FRACTION * PLANT_SPIKE and arg_s == i0,
           "PLANT SEEN: a single-cell spike of %g moves max|delta| to %.6f and "
           "the argmax to the planted cell %d" % (PLANT_SPIKE, d_s, i0))
        off = [v + PLANT_OFFSET for v in hi]
        d_o, _ = max_abs_delta("scalar", lo, off)
        pred = max(abs((hi[i] + PLANT_OFFSET) - lo[i]) for i in range(len(hi)))
        ok(abs(d_o - pred) <= REL_EXACT * abs(pred),
           "PLANT EXACT: a constant offset moves max|delta| to the closed form "
           "%.12f (read %.12f)" % (pred, d_o))
        ok(field_range("scalar", off) - field_range("scalar", hi) == 0.0,
           "TWO SHAPES: the RANGE reader is EXACTLY blind to the constant "
           "offset the DELTA reader sees exactly (L-340)")
        ok(field_range("scalar", spiked) - field_range("scalar", hi)
           >= Y2_SEEN_FRACTION * PLANT_SPIKE,
           "and the RANGE reader DOES see the spike -- so neither reader is a "
           "stand-in for the other")
        ok(max_abs_delta("scalar", lo, list(lo))[0] == 0.0,
           "THE ZERO: identical checkpoints read back EXACTLY 0.0 from the "
           "reader just shown able to see %g" % PLANT_SPIKE)

        # MUTATED PLANT MUST REFUSE: a reader that ignores the planted cell
        def _blind_delta(kind, lo_, hi_):
            """A deliberately mutilated reader that never looks past cell 0."""
            return abs(hi_[0] - lo_[0]), 0
        d_blind, arg_blind = _blind_delta("scalar", lo, spiked)
        ok(not (d_blind >= Y2_SEEN_FRACTION * PLANT_SPIKE and arg_blind == i0),
           "MUTATED PLANT REFUSED: a reader that never looks past cell 0 does "
           "NOT see the spike at cell %d (%.3e), so the C-1 predicate rejects "
           "it -- the control can fail" % (i0, d_blind))

        # the anti-vacuity refusal is real: if the plant cell IS the base
        # argmax the arm must refuse rather than pass for free
        flat_hi = list(lo)
        i0f = min(range(len(flat_hi)), key=lambda i: (abs(flat_hi[i] - lo[i]), i))
        _bd, barg = max_abs_delta("scalar", lo, flat_hi)
        ok(i0f == barg,
           "ANTI-VACUITY ARMED: on an all-zero-delta pair the smallest-change "
           "cell IS the argmax (%d == %d), which is exactly the condition arm "
           "C-1 REFUSES on rather than passing vacuously" % (i0f, barg))

        # ------------------------------------------------------------------
        # 4. RESIDUALS ARE REPORTED AND CANNOT GATE -- proven two ways
        # ------------------------------------------------------------------
        ok(_l342_class("initial_residual").startswith("REPORTED, NEVER GATED"),
           "the initial residual is classed REPORTED, NEVER GATED")
        ok(_l342_class("checkpoint_pair").startswith("GATE INPUT"),
           "the checkpoint pair is a GATE INPUT and never infrastructure")
        import inspect
        sig = inspect.signature(grade_row).parameters
        ok(not any("resid" in p for p in sig),
           "STRUCTURAL: grade_row's signature (%s) takes no residual argument, "
           "so no residual can reach a verdict even by mistake"
           % ", ".join(sig))
        ok(not any("resid" in inspect.signature(f).parameters
                   for f in (gate_clause1, gate_yplus_t5e)),
           "and neither gate_clause1 nor gate_yplus_t5e takes one either")
        for fn in (grade_row, gate_clause1, gate_yplus_t5e):
            body = inspect.getsource(fn)
            ok("residual_report" not in body and "RESIDUAL_FIELDS" not in body,
               "SOURCE: %s's body names no residual symbol" % fn.__name__)
        # CALL SITES ONLY, by line-anchored regex.  A negative lookbehind on
        # `_` keeps `print_residual_report(` out, and anchoring on an
        # assignment keeps the definition and the docstring mention out.
        calls = re.findall(r"^\s*[A-Za-z_][A-Za-z0-9_\[\]\"']*\s*=\s*"
                           r"(?<![A-Za-z0-9_])residual_report\(", src, re.M)
        ok(len(calls) == 1,
           "residual_report has EXACTLY ONE call site in this file (found %d), "
           "and it assigns into a report dict" % len(calls))
        ok(re.search(r"^\s*residuals\[lv\]\s*=\s*residual_report\(", src, re.M)
           is not None,
           "and that call site is `residuals[lv] = residual_report(case_dir)` "
           "in run() -- the value goes to print_residual_report and to nothing "
           "else; no gate is ever passed it")

        # ------------------------------------------------------------------
        # 5. THE y+ READERS, CARRIED UNCHANGED -- hand-computable answers
        # ------------------------------------------------------------------
        v = [1.0, 2.0, 3.0, 4.0]
        A = [1.0, 1.0, 1.0, 7.0]
        ok(abs(R_area(v, A) - 3.4) < 1e-15, "R_area = %.6f (expected 3.4)"
           % R_area(v, A))
        ok(abs(R_facecount_mean(v) - 2.5) < 1e-15, "R_facecount_mean = 2.5")
        ok(R_max(v) == 4.0, "R_max = 4.0")
        ok(R_area(v, A) != R_facecount_mean(v),
           "R_area and the face-count mean DIFFER on a non-uniform patch, so "
           "the ladder statistic is not the .dat `average` column")
        ok(classify_triple(3.0, 2.0, 1.5) == "CONVERGING", "triple CONVERGING")
        ok(classify_triple(1.0, 2.0, 4.0) == "DIVERGENT", "triple DIVERGENT")
        ok(classify_triple(1.0, 2.0, 1.5) == "OSCILLATORY", "triple OSCILLATORY")
        ok(classify_triple(1.0, 1.0, 2.0) == "STAGNANT", "triple STAGNANT")
        ok(classify_triple(1.0, 1.0, 1.0) == "EXACT", "triple EXACT")
        ymet2 = {lv: dict(state="MET") for lv in LEVELS}
        s = {w: dict(R_area=1.0, R_max=1.0, R_q95=1.0, fc_mean=1.0) for w in YPLUS_WALLS}
        ok(gate_yplus_t5e(s, "f")["state"] == "MET", "a compliant y+ set is MET")
        s2 = dict(s)
        s2["roof"] = dict(R_area=1.0, R_max=30.0, R_q95=1.0, fc_mean=1.0)
        g = gate_yplus_t5e(s2, "f")
        ok(g["state"] == VERDICT_NAR and g["clause"] == "Y-SUBLAYER",
           "a roof at R_max 30 fires the SUBLAYER clause on the POINT MAXIMUM "
           "(binding condition 3)")
        s3 = dict(s)
        s3["roof"] = dict(R_area=4.0, R_max=4.5, R_q95=4.0, fc_mean=4.0)
        g = gate_yplus_t5e(s3, "f")
        ok(g["state"] == VERDICT_NAR and g["clause"] == "Y-LADDER",
           "a roof at R_area 4.0 against the level bound 2.0 fires the LADDER "
           "clause on the AREA AVERAGE")

        # ------------------------------------------------------------------
        # 6. THE VECTOR AND RANGE INTERPRETATIONS ARE BOTH COMPUTED
        # ------------------------------------------------------------------
        uv = [(3.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        ok(field_range("vector", uv) == 3.0,
           "INTERPRETATION 20(a): a vector field's registered range is the "
           "largest per-component range (3.0 here)")
        ok(abs(field_range_reported("vector", uv) - 2.0) < 1e-12,
           "and the REPORTED magnitude range (2.0) is computed beside it, so "
           "the interpretation is auditable from the output")
        d_pc, _i = max_abs_delta("vector", [(0.0, 0.0, 0.0)], [(3.0, 4.0, 0.0)])
        ok(d_pc == 4.0, "the gated per-component delta is 4.0")
        ok(abs(max_abs_delta_reported("vector", [(0.0, 0.0, 0.0)],
                                      [(3.0, 4.0, 0.0)]) - 5.0) < 1e-12,
           "and the REPORTED magnitude delta is 5.0")

        # ------------------------------------------------------------------
        # 7. THE REGISTRATION IS READ, NOT TRUSTED
        # ------------------------------------------------------------------
        if os.path.isfile(T5_REGISTRATION):
            lo_ln, hi_ln = assert_criterion_clause_witness()
            ok(True, "the S5.5 criterion clause is at T5_PREREGISTRATION.md "
                     "lines %d-%d, sha256-witnessed over those four lines "
                     "(stable under lawfully appended amendments)"
               % (lo_ln, hi_ln))
            t, stq = parse_registered_criterion()
            ok(t == CONV_REL_TOL and stq == CONV_CHECKPOINT_STRIDE,
               "clause (1)'s tolerance %g and stride %d were PARSED OUT of the "
               "frozen registration, not typed here -- so restoring the clause "
               "registers nothing new" % (t, stq))
            reg = open(T5_REGISTRATION, errors="replace").read()
            ok("`residualControl` is not written" in reg,
               "and the registration's own refusal of the residual instrument "
               "is present in it, so this file's refusal is sourced")
        else:
            ok(False, "the frozen T5 registration is absent; clause (1)'s "
                      "tolerance is UNVERIFIED here")
        if os.path.isfile(FROZEN_T5B) and os.path.isfile(FROZEN_T5C):
            for line in assert_frozen_predecessor_bytes():
                ok(True, "frozen predecessor verified by sha256 of the DISK "
                         "BYTES (never a git blob SHA-1, L-450): %s" % line)
            ok(len(assert_thresholds_carried_over()) >= 29,
               "every y+ threshold re-parsed from BOTH frozen predecessors "
               "matches this file's")
            bsrc = open(FROZEN_T5B, errors="replace").read()
            ok("YPLUS_MAX = 5.0" in bsrc and "YPLUS_TARGET_TOL = 2.0" in bsrc,
               "the frozen analyse_t5b.py still carries YPLUS_MAX = 5.0 and "
               "YPLUS_TARGET_TOL = 2.0 -- not relaxed here")
            ok("(1) any level's y+ gate not MET" in bsrc,
               "and the frozen predecessor's step (1) IS the y+ gate, which is "
               "the defect T5e repairs -- quoted from its own bytes, not "
               "paraphrased")
        else:
            ok(False, "a frozen predecessor is absent; the carry-over is "
                      "UNVERIFIED here")

        # ------------------------------------------------------------------
        # 8. DISCIPLINE
        # ------------------------------------------------------------------
        bare = [i + 1 for i, l in enumerate(src.splitlines())
                if re.match(r"\s*assert\s", l)]
        ok(not bare, "zero bare `assert` statements (python3 -O strips them and "
                     "a control that vanishes under a flag is not a control)%s"
           % ("" if not bare else " -- at lines %s" % bare))
        ok('if os.environ.get("T5E_CHILD") == "1":' in src,
           "the mutant CHILD GUARD is present: a mutant runs every check in "
           "sections 0-8 and stops before spawning its own mutants, so the "
           "negative-control layer cannot fork exponentially (measured: the "
           "first draft of this file reached 108 live processes)")
        armed = [c for c in CASE_OF.values() if os.path.exists(os.path.join(HERE, c))]
        ok(not armed,
           "ZERO-COMPUTE: T5e_runs holds no case directory of its own; T5e "
           "launches no solver and re-grades artifacts under %s"
           % os.path.relpath(DEFAULT_ROOT, T_FAMILY))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ------------------------------------------------------------------
    # 9. NEGATIVE CONTROLS -- real mutations of this file, __pycache__ cleared
    #
    # THE CHILD GUARD, AND WHY IT IS NOT A WEAKENING.  Each mutant is run with
    # `--selftest`; without a guard that mutant would run ITS OWN mutants, and
    # so on, which forks exponentially.  MEASURED, not theorised: the first
    # draft of this file did exactly that and had to be killed at 108 live
    # processes.  T5E_CHILD=1 tells a mutant to run every check in sections
    # 0-8 and to STOP at this section.  A mutant's verdict comes from the
    # checks IT FAILS, never from its own mutants, so the guard removes only
    # the recursion and none of the rejecting power -- and the parent, which
    # runs unguarded, is the one whose exit code is reported.
    # ------------------------------------------------------------------
    if os.environ.get("T5E_CHILD") == "1":
        print("negative controls: SKIPPED in a mutant child (T5E_CHILD=1). "
              "The section-0-8 checks above are what judge this mutant; "
              "%d of them failed." % len(fails))
        print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL",
                                           len(fails)))
        return 0 if not fails else 1

    print("negative controls (a rule that cannot reject is not a rule):")
    muts = [
        ("N1 clause (1) demoted BELOW the y+ clause (the T5b defect restored)",
         "    notconv = [lv for lv in LEVELS\n"
         "               if clause1_states[lv][\"state\"] != \"CONVERGED\"]",
         "    notconv = []"),
        ("N2 the clause-(1) tolerance loosened so a stalled level passes",
         "CONV_REL_TOL = 1e-6", "CONV_REL_TOL = 1e6"),
        ("N3 the y+ sublayer bound raised so a wall at 30 passes",
         "YPLUS_MAX = 5.0", "YPLUS_MAX = 500.0"),
        ("N4 the y+ ladder tolerance widened",
         "YPLUS_TARGET_TOL = 2.0", "YPLUS_TARGET_TOL = 200.0"),
        ("N5 a residual made to gate (the instrument T5 S5.5 refuses)",
         "def gate_clause1(case_dir, level):",
         "def gate_clause1(case_dir, level, residual_state=None):"),
        ("N6 the checkpoint-delta reader blinded past cell 0",
         "        for i in range(len(hi)):\n            d = abs(hi[i] - lo[i])",
         "        for i in range(1):\n            d = abs(hi[i] - lo[i])"),
        ("N7 the planted-zero arm's argmax question removed",
         "d_s >= Y2_SEEN_FRACTION * PLANT_SPIKE and arg_s == i0",
         "d_s >= Y2_SEEN_FRACTION * PLANT_SPIKE and arg_s == arg_s"),
        ("N8 the freeze pin set by this file instead of by the supervisor",
         '\nGRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"\n',
         '\nGRADING_PATH_FREEZE_COMMIT = "deadbeefdeadbeef"\n'),
    ]
    childenv = dict(os.environ, T5E_CHILD="1")
    # THE GUARD ITSELF IS A CONTROL: a POSITIVE arm proves an UNMUTATED child
    # still passes under T5E_CHILD=1, so a mutant's failure below is the
    # mutation's doing and not the guard's.
    d = tempfile.mkdtemp(prefix="t5e_ctl_")
    try:
        p = os.path.join(d, "analyse_t5e.py")
        open(p, "w").write(src)
        shutil.rmtree(os.path.join(d, "__pycache__"), ignore_errors=True)
        r = subprocess.run([sys.executable, p, "--selftest"],
                           capture_output=True, text=True, cwd=d, env=childenv)
        ok(r.returncode == 0,
           "CONTROL ARM: an UNMUTATED copy run under the same child guard "
           "PASSES (rc %d), so every failure below is the mutation's doing and "
           "not the guard's" % r.returncode)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    for label, old, new in muts:
        if src.count(old) < 1:
            ok(False, "%s -- the mutation anchor is not in the source" % label)
            continue
        d = tempfile.mkdtemp(prefix="t5e_mut_")
        try:
            p = os.path.join(d, "analyse_t5e.py")
            open(p, "w").write(src.replace(old, new, 1))
            for c in (os.path.join(HERE, "__pycache__"),
                      os.path.join(d, "__pycache__")):
                shutil.rmtree(c, ignore_errors=True)
            r = subprocess.run([sys.executable, p, "--selftest"],
                               capture_output=True, text=True, cwd=d,
                               env=childenv)
            ok(r.returncode != 0, "%s -> the selftest FAILS" % label)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # the -O arm: the same selftest under an optimising interpreter
    d = tempfile.mkdtemp(prefix="t5e_O_")
    try:
        p = os.path.join(d, "analyse_t5e.py")
        open(p, "w").write(src)
        shutil.rmtree(os.path.join(d, "__pycache__"), ignore_errors=True)
        r = subprocess.run([sys.executable, "-O", p, "--selftest"],
                           capture_output=True, text=True, cwd=d, env=childenv)
        ok(r.returncode == 0,
           "the whole selftest passes identically under `python3 -O` (rc %d), "
           "so no control here depends on an interpreter flag" % r.returncode)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv \
        else DEFAULT_ROOT
    return run(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
