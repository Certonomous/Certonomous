#!/usr/bin/env python3
"""analyse_t5b.py -- the T5b comparator.  IT GRADES; it does not print a sentence.

Registration: docs/campaigns/T-family/T5b_PREREGISTRATION.md.  Frozen with it.

===========================================================================
TWO LABELS THIS FILE MUST CARRY, STATED BEFORE ANYTHING ELSE
===========================================================================
1. THE AUTHOR OF THIS FILE HAS READ THE REFERENCE VALUES.  They are at HEAD in
   ../T5_runs/T5_reference_primary.json (blob 04dfd7e2), digitised 2026-08-26,
   and this lane read them while scoping T5b.  T5 S10 registered the opposite
   ordering and for T5b it is BROKEN and cannot be repaired by anything written
   here.  The ONE auditable mitigation is a property a reader can check in
   thirty seconds AND WHICH THIS FILE ENFORCES ON ITSELF: no reference value is
   hard-coded anywhere in this source.  `--selftest` reads this file's own bytes,
   scans them for every numeric value in the reference JSON, and FAILS if one
   appears.  A mitigation that is only asserted is not a mitigation.
2. This file is written BEFORE T5b's first compute.  `verification/runs/
   T-family/T5b_runs/STATUS.*` does not exist and no T5b case holds a `0/` or a
   numeric time directory; that is the condition, and it is checked, not assumed
   (`--selftest` prints it).

===========================================================================
THE THREE DEFECTS T5b REPAIRS, EACH MEASURED, NONE INFERRED
===========================================================================
T5's y+ gate (T5_PREREGISTRATION S16.3.1) could not be satisfied by ANY run,
for three INDEPENDENT reasons.  Any one of them alone returns NOT A RESULT on
every graded row of every level:

  D1  THE FUNCTION OBJECT NEVER EXECUTED.  `writeControl writeTime;
      writeInterval 1000` on a run with five write times means "every 1000th
      write time", so `write()` never ran.  MEASURED: yPlus.dat carries two
      header lines and ZERO data rows on T5's c, m and f, while wallHeatFlux
      wrote 30,000 rows under the identical control because ITS rows come from
      `execute()`.  Reproduced 2026-08-27 by a driven CONTROL arm (0 rows) and
      a FIX arm (12 rows) differing in that one keyword.  Repaired in
      build_t5b.py.
  D2  A REGISTERED WALL THAT CANNOT EXIST.  T5's YPLUS_WALLS names
      `cube_side_s`; the registered geometry is a HALF domain with a symmetry
      plane at z/H = 0, so that patch is not in any mesh.  T5's own AMENDMENT 3
      found this, proposed the fix and records it as PROPOSED, NOT ADOPTED:
      "Until adopted, S16.3.1's 'a wall not reported -> NOT A RESULT' fires on
      every level by construction."  T5b registers the SIX walls that exist and
      ASSERTS them against the mesh's own boundary file, both directions.
  D3  A READER WITH NO WRITER.  T5's comparator reads `yPlus.json`.  NOTHING IN
      THE REPOSITORY EVER WRITES `yPlus.json` -- the function object writes
      `postProcessing/air/yPlus/0/yPlus.dat`.  Even a firing FO and a correct
      wall list would still have returned NOT A RESULT.  T5b reads the .dat the
      solver actually writes.

T5's NOT A RESULT therefore STANDS and is not reopened here.  `postProcess` was
NOT re-run on T5's completed cases to manufacture the missing measurement: S16.3.1
registered its absence as NOT A RESULT BEFORE compute, and producing it afterwards
to escape a registered verdict is answer-changing (Sanaa 2026-08-27 S3 anti-gaming).
The legitimate route is this successor rung.

===========================================================================
L-342 FIELD CLASSES -- DECLARED, and both halves driven in --selftest
(the model is verification/runs/T-family/T3_runs/mark_done_t3_rff.py:8-18,
 whose selftest at :143-144 drives an infrastructure-absent arm AND a
 physics-critical arm; that shape is copied, not paraphrased)
===========================================================================
PHYSICS-CRITICAL -- any failure is NOT A RESULT; absence REFUSES (exit 2):
    the solver rc VALUE; the `End` line in log.solve; last time == endTime;
    fields T U p_rgh alphat nut k omega present at endTime; the ExecutionTime
    count == endTime; every field NEWER than the case's own 0/T (age guard);
    and the y+ measurement -- yPlus.dat rows at endTime on all six walls.
GATE INPUT, WHICH IS NEVER INFRASTRUCTURE:
    yPlus.dat.  S16.3.1 registers absent y+ as NOT A RESULT.  Reclassifying a
    registered gate input as infrastructure would convert a registered NOT A
    RESULT into a bookkeeping note, which is the gaming shape.  `_l342_class`
    returns "GATE INPUT" for it and --selftest fails if that ever changes.
INFRASTRUCTURE -- reported; absent or odd values are stated NOT MEASURED and
NEVER refuse:
    wall_s, ranks, core_min, cap_core_min, timeout_s, capped, checkMesh_rc,
    the ExecutionTime-LINE count as distinct from the iteration count, ledger
    rows, pids, log.launch presence, CAP_ENFORCED.txt, marker mtimes.

RULING R-RC (Sanaa APPROVED 2026-08-27): the rc VALUE is PHYSICS; the rc RECORD
is INFRASTRUCTURE.  An absent STATUS file is NOT MEASURED -- and only if the
other four rule-4 conditions hold -- whereupon rc=0 is printed as a LABELLED
INFERENCE, never as a reading.  A `FOAM FATAL` or a signal token anywhere in
log.solve still REFUSES regardless.

RULING D534 (Sanaa APPROVED 2026-08-27): REPORTED is a ROW CLASS, not a verdict.
Every REPORTED row is EXCLUDED from the N-of-M census and the tally line says so
in words.

RULE 3 PLANTED-ZERO CONTROL, SIZED TO EACH READER'S SHAPE (L-340): a constant
offset is INVISIBLE to a range or a dispersion reader by construction, so the
range readers get a SINGLE-CELL SPIKE and the mean readers get a constant offset.
Both are planted into a copy, read back through the real reader, and the run
REFUSES if the reader cannot see its own plant.

RULE 5 TRIPLE GATING, in the registered order, GCI at Fs = 1.25, on the MEASURED
refinement ratios r21 = 1.6060 and r32 = 1.5929 from the actual cell counts --
NEVER the r = 2.0 default, which is wrong by 25 % in log r on this ladder.

DISCIPLINE: zero `assert` statements; `--selftest` byte-identical under `python3`
and `python3 -O`; every negative control drives a real mutation of this file with
`__pycache__` cleared between the control and the mutant.

Usage: analyse_t5b.py [--root DIR] | --selftest
Exit 0 graded, 1 a graded row did not PASS, 2 refusal.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T5_RUNS = os.path.abspath(os.path.join(HERE, "..", "T5_runs"))
REFERENCE = os.path.join(T5_RUNS, "T5_reference_primary.json")

VERDICT_PASS = "PASS"
VERDICT_FAIL = "GATE FAIL"
VERDICT_NAR = "NOT A RESULT"
VERDICT_REACHED = "GATE REACHED"
VERDICT_BLOCKED = "BLOCKED"
ROWCLASS_REPORTED = "REPORTED"          # D534: a ROW CLASS, never a verdict

LEVELS = ("c", "m", "f")
CASE_OF = {"c": "T5_CUBE_c", "m": "T5_CUBE_m", "f": "T5_CUBE_f"}

# MEASURED cell counts, read back from each case's own log.checkMesh at build
# time 2026-08-27 and re-read by this file at grade time; the ratios below are
# derived from them, never typed.
CELLS_REGISTERED = {"c": 52684, "m": 212942, "f": 882024}

FS = 1.25                        # Roache safety factor, registered
ENDTIME = 5000
REQUIRED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

# THE SIX WALLS THAT EXIST (D2).  `cube_side_s` is deliberately absent: the
# registered geometry is a half domain.  This tuple is CHECKED against the
# mesh's own boundary file in BOTH directions -- a registered wall that is not
# in the mesh refuses, and a wall in the mesh that is not registered refuses.
YPLUS_WALLS = ("cube_front", "cube_top", "cube_rear",
               "cube_side_n", "floor", "roof")
YPLUS_MAX = 5.0                  # the edge of the viscous sublayer
YPLUS_TARGET = {"c": 2.6, "m": 1.6, "f": 1.0}
YPLUS_TARGET_TOL = 2.0

T_REF_K = 293.65                 # channel inlet air, T5 S7.1 INTERPRETATION 9
INTRINSIC_FLOOR_PCT = 1.7        # T5 S7.4 ambient ambiguity, carried unchanged

# GRADED rows and the face each reads.  REPORTED rows are listed so the tally
# can EXCLUDE them by name rather than by omission (D534).
GRADED_H = {"G1a": "cube_front", "G2a": "cube_top", "G3a": "cube_rear"}
GRADED_T = {"G5a": "cube_front", "G5b": "cube_top", "G5c": "cube_rear"}
REPORTED_ROWS = ("G1", "G2", "G3", "G4", "R1", "R2", "R3")

# G5 identity guard (T5 S3): the reference T_sur must sit at least this far from
# BOTH imposed bounds, else the row is NOT A RESULT -- identity.
G5_IDENTITY_MARGIN_K = 5.0
G5_BOUND_LO_C = 20.5
G5_BOUND_HI_C = 75.0

PLANT_OFFSET = 1.234e-03         # for MEAN readers
PLANT_SPIKE = 9.876e+02          # for RANGE/MAX readers (L-340)


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def _l342_class(name):
    """The declared class of a named artefact.  Driven in --selftest."""
    if name == "yPlus.dat":
        return "GATE INPUT (never infrastructure): S16.3.1 registers absent y+ as NOT A RESULT"
    if name in ("rc_value", "End", "last_time", "age_guard", "ExecutionTime_count") \
            or name in REQUIRED_FIELDS:
        return "PHYSICS-CRITICAL"
    if name in ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s", "capped",
                "checkMesh_rc", "rc_record", "ExecutionTime_line_count", "pid",
                "ledger_row", "log.launch", "CAP_ENFORCED.txt", "marker_mtime"):
        return "INFRASTRUCTURE"
    return "UNCLASSIFIED"


# ---------------------------------------------------------------------------
# polyMesh patch areas.  PROVEN, not trusted: the cube faces on the registered
# half domain must come back at exactly H*(H/2) = 1.125e-04 m^2 and the north
# side face at H*H = 2.25e-04 m^2, both known by construction.  Measured on the
# built coarse mesh 2026-08-27: 1.125000000e-04 / 1.125000000e-04 /
# 1.125000000e-04 / 2.250000000e-04, ten significant figures.
# ---------------------------------------------------------------------------
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
    """BOTH directions.  A registered wall missing from the mesh refuses; a wall
    IN the mesh that is not registered also refuses -- T4/C1: a gate that names
    one wall certifies one wall, and the pipe wall sat at y+ 30 unseen."""
    # MEASURED on the built mesh: the floor and roof are `wall`; the four cube
    # faces are `mappedWall`, because they ARE the conjugate interface.  A check
    # that only accepted `wall` would silently drop every cube face -- the very
    # walls this rung grades.
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


# ---------------------------------------------------------------------------
# OpenFOAM field readers
# ---------------------------------------------------------------------------
def read_patch_field(path, patch):
    """The boundaryField entry for one patch, as a list of floats.

    Handles `nonuniform List<scalar> N ( ... )` and `uniform V`."""
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
    """D3: read what the SOLVER WRITES -- postProcessing/air/yPlus/<t0>/yPlus.dat --
    not a yPlus.json that no producer in this repository has ever written."""
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
                      "defect D1 verbatim and it is what T5 produced on all "
                      "three levels")
    if not rows:
        return None, "yPlus.dat has rows but none at endTime %d" % endtime
    return rows, None


def gate_yplus(case_dir, level, endtime=ENDTIME):
    got, why = read_yplus_dat(case_dir, endtime)
    if got is None:
        return dict(state=VERDICT_NAR,
                    why="y+ NOT MEASURED (%s): the sublayer assumption is "
                        "unmeasured and an unmeasured precondition is not a "
                        "satisfied one" % why)
    missing = [w for w in YPLUS_WALLS if w not in got]
    if missing:
        return dict(state=VERDICT_NAR,
                    why="y+ not reported on wall(s): " + ",".join(missing))
    over = {w: got[w]["max"] for w in YPLUS_WALLS if got[w]["max"] > YPLUS_MAX}
    if over:
        return dict(state=VERDICT_NAR, walls=got,
                    why="y+ exceeds the registered sublayer bound %.1f on: %s"
                        % (YPLUS_MAX, ", ".join("%s=%.3f" % (w, v)
                                                for w, v in sorted(over.items()))))
    tgt = YPLUS_TARGET[level]
    drift = {w: got[w]["max"] for w in YPLUS_WALLS
             if got[w]["max"] > tgt * YPLUS_TARGET_TOL}
    if drift:
        return dict(state=VERDICT_NAR, walls=got,
                    why="y+ exceeds %.1fx the level target %.2f on: %s -- the "
                        "ladder is not the registered ladder"
                        % (YPLUS_TARGET_TOL, tgt,
                           ", ".join("%s=%.3f" % (w, v) for w, v in sorted(drift.items()))))
    return dict(state="MET", walls=got,
                why="all %d registered walls inside y+ %.1f and within %.1fx the "
                    "level target %.2f" % (len(YPLUS_WALLS), YPLUS_MAX,
                                           YPLUS_TARGET_TOL, tgt))


# ---------------------------------------------------------------------------
# Completion: rule 4, with R-RC applied to the rc RECORD
# ---------------------------------------------------------------------------
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
    """Returns (ok, why, infra_notes).  PHYSICS-CRITICAL failures -> not ok."""
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
        # R-RC: the rc RECORD is INFRASTRUCTURE.  Its absence is NOT MEASURED,
        # and rc=0 may be INFERRED -- but ONLY if the other four rule-4
        # conditions hold, and the inference is LABELLED as one.
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
        # THE ITERATION COUNT is physics-critical (rule 4).  The LINE count is
        # infrastructure and is reported separately -- a solver that prints an
        # extra banner line is a bookkeeping fact, not a physics failure.
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


# ---------------------------------------------------------------------------
# Row extraction: LOCAL h, area-weighted.  This is what the wallHeatFlux FIELD
# buys and why T5's per-patch min/max/integral could not serve:
#     hbar_face = (1/A) * INT phi''/(T_sur - T_ref) dA
# is NOT integral(phi'')/(A (Tbar - T_ref)) when T_sur varies over the face --
# and making it vary is the entire point of a conjugate rung.
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Rule 3: planted-zero controls, SIZED TO THE READER (L-340)
# ---------------------------------------------------------------------------
def plant_and_read_back(case_dir, patch, areas):
    """Two plants, two shapes, both read back through THE REAL READERS.

    A CONSTANT OFFSET moves a mean and is invisible to a max.
    A SINGLE-CELL SPIKE moves a max and is nearly invisible to a mean.
    Planting only one shape proves only one reader (L-340)."""
    tdir = os.path.join(case_dir, str(ENDTIME), "air")
    src = os.path.join(tdir, "T")
    if not os.path.isfile(src):
        return False, "no T field to plant into"
    tmp = tempfile.mkdtemp(prefix="t5b_plant_")
    try:
        work = os.path.join(tmp, str(ENDTIME), "air")
        os.makedirs(work)
        shutil.copy2(src, os.path.join(work, "T"))
        shutil.copy2(os.path.join(tdir, "wallHeatFlux"),
                     os.path.join(work, "wallHeatFlux"))
        base, err = face_mean_T_C(tmp, patch, areas)
        if base is None:
            return False, "the reader could not read the unplanted copy: %s" % err
        # ARM 1 -- constant offset, for the MEAN reader
        s = open(os.path.join(work, "T"), errors="replace").read()
        j = s.find("boundaryField")
        k = s.find(patch, j)
        m = re.search(r"nonuniform\s+List<scalar>\s*(\d+)\s*\(", s[k:])
        if not m:
            return False, "patch %s is not a nonuniform list: nothing to plant" % patch
        st = k + m.end()
        en = s.find(")", st)
        vals = [float(x) for x in s[st:en].split()]
        off = [v + PLANT_OFFSET for v in vals]
        open(os.path.join(work, "T"), "w").write(
            s[:st] + "\n" + "\n".join(repr(v) for v in off) + "\n" + s[en:])
        got, err = face_mean_T_C(tmp, patch, areas)
        if got is None:
            return False, "reader failed on the offset plant: %s" % err
        if abs((got - base) - PLANT_OFFSET) > 0.1 * PLANT_OFFSET:
            return False, ("MEAN reader is BLIND to a constant offset of %g: "
                           "base %.9f, planted %.9f" % (PLANT_OFFSET, base, got))
        # ARM 2 -- single-cell spike, for the RANGE/MAX reader
        spike = list(vals)
        spike[0] = spike[0] + PLANT_SPIKE
        open(os.path.join(work, "T"), "w").write(
            s[:st] + "\n" + "\n".join(repr(v) for v in spike) + "\n" + s[en:])
        back = read_patch_field(os.path.join(work, "T"), patch)
        if back is None:
            return False, "reader failed on the spike plant"
        if max(back) - max(vals) < 0.9 * PLANT_SPIKE:
            return False, ("RANGE reader is BLIND to a single-cell spike of %g "
                           "-- exactly the shape a constant offset cannot test "
                           "(L-340)" % PLANT_SPIKE)
        return True, ("both plants seen: constant offset %g through the MEAN "
                      "reader and single-cell spike %g through the RANGE reader"
                      % (PLANT_OFFSET, PLANT_SPIKE))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Convergence and the Roache triple
# ---------------------------------------------------------------------------
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
    """Roache, unequal-ratio fixed point.  Fs = 1.25.  NEVER quoted when the
    three values are not monotone -- the caller checks classify_triple first."""
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
    """sqrt(stated^2 + digitisation^2), the T5 S7.3 arithmetic, UNCHANGED.
    T5b neither restates nor relaxes a T5 gate: it registers the same
    arithmetic on the same reference for a new rung."""
    u = row.get("uncertainty")
    d = row.get("digitisation_increment")
    if u is None:
        return None
    if d is None:
        return float(u)
    return math.sqrt(float(u) ** 2 + float(d) ** 2)


def grade_row(name, ref_row, vals, yplus_states, r21, r32, identity_ok=True):
    """THE REGISTERED ORDER (T5 S7.5, rule 5), evaluated top to bottom."""
    out = dict(row=name, values=vals)
    # (1) any level's y+ gate not MET -> NOT A RESULT
    bad = [lv for lv in LEVELS if yplus_states[lv]["state"] != "MET"]
    if bad:
        out.update(verdict=VERDICT_NAR,
                   why="y+ gate not MET on level(s) %s: %s"
                       % (",".join(bad), yplus_states[bad[0]]["why"]))
        return out
    if any(vals.get(lv) is None for lv in LEVELS):
        out.update(verdict=VERDICT_NAR, why="a level produced no value")
        return out
    f_c, f_m, f_f = vals["c"], vals["m"], vals["f"]
    tri = classify_triple(f_c, f_m, f_f)
    out["triple"] = tri
    # (2) triple not CONVERGING -> NOT A RESULT, value and triple printed
    if tri != "CONVERGING":
        out.update(verdict=VERDICT_NAR,
                   why="grid triple is %s (rule 5): fine value %.6g printed, "
                       "not graded" % (tri, f_f))
        return out
    p, gci = gci_triple(f_c, f_m, f_f, r21, r32)
    out["order"] = p
    out["gci"] = gci
    # (3) reference absent -> BLOCKED
    if ref_row is None or ref_row.get("value") is None:
        out.update(verdict=VERDICT_BLOCKED,
                   why="no reference value; fine value %.6g and triple %s "
                       "REPORTED" % (f_f, tri))
        return out
    # (4) G5 identity guard
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
    # (5) below the intrinsic floor -> GATE REACHED
    if dev_pct < INTRINSIC_FLOOR_PCT:
        out.update(verdict=VERDICT_REACHED,
                   why="deviation %.3f %% is below the registered intrinsic "
                       "floor %.1f %% (T5 S7.4 ambient ambiguity): the rung "
                       "cannot resolve it" % (dev_pct, INTRINSIC_FLOOR_PCT))
        return out
    out.update(verdict=band_verdict(f_f, ref, band),
               why="fine %.6g vs reference %.6g, band +/- %.6g, GCI %s"
                   % (f_f, ref, band, ("%.4f %%" % (100 * gci)) if gci else "n/a"))
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def measured_ratios(cells):
    r21 = (cells["f"] / cells["m"]) ** (1.0 / 3.0)
    r32 = (cells["m"] / cells["c"]) ** (1.0 / 3.0)
    return r21, r32


def run(root):
    if not os.path.isfile(REFERENCE):
        refuse("no reference at %s" % REFERENCE)
    ref = json.load(open(REFERENCE))
    if not ref.get("provenance", {}).get("digitised"):
        refuse("the reference is not marked digitised")

    print("T5b comparator -- registration docs/campaigns/T-family/T5b_PREREGISTRATION.md")
    print("reference: %s (digitised %s)"
          % (os.path.relpath(REFERENCE, os.path.dirname(HERE)),
             ref["provenance"].get("digitised_utc")))
    print("L-342 classes: %s"
          % "; ".join("%s=%s" % (f, _l342_class(f).split(":")[0])
                      for f in ("T", "rc_value", "rc_record", "yPlus.dat",
                                "core_min", "ExecutionTime_line_count")))

    cells = {}
    areas_by_level = {}
    yplus = {}
    completion = {}
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
        yplus[lv] = gate_yplus(case_dir, lv)
        print("  level %s  %-11s cells %7d  completion: %s  y+: %s"
              % (lv, case, cells[lv], "COMPLETE" if ok else "NOT COMPLETE (%s)" % why,
                 yplus[lv]["state"]))
        for n in notes:
            print("      infra: %s" % n)

    r21, r32 = measured_ratios(cells)
    print("MEASURED refinement ratios r21 = %.4f, r32 = %.4f (NEVER the r = 2.0 "
          "default: that is wrong by %.0f %% in log r on this ladder)"
          % (r21, r32, 100 * abs(math.log(2.0) - math.log(r21)) / math.log(r21)))

    if not all(completion[lv][0] for lv in LEVELS):
        print("\nNOT A RESULT on every graded row: a level is not complete "
              "(rule 4 is all-or-nothing).")
        for lv in LEVELS:
            if not completion[lv][0]:
                print("  level %s: %s" % (lv, completion[lv][1]))
        return 1

    # rule 3, on the fine level and on a real patch, BEFORE any value is read
    ok, why = plant_and_read_back(os.path.join(root, CASE_OF["f"]),
                                  "cube_front", areas_by_level["f"])
    if not ok:
        refuse("PLANTED-ZERO CONTROL FAILED: %s. A zero from a reader not shown "
               "able to see a non-zero is not evidence (rule 3)." % why)
    print("planted-zero control: %s" % why)

    rows = []
    for name, patch in sorted(GRADED_H.items()):
        vals = {}
        for lv in LEVELS:
            v, err = face_mean_h(os.path.join(root, CASE_OF[lv]), patch,
                                 areas_by_level[lv])
            vals[lv] = v
            if v is None:
                print("  %s level %s: %s" % (name, lv, err))
        rows.append(grade_row(name, ref["rows"].get(name), vals, yplus, r21, r32))
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
        rows.append(grade_row(name, rr, vals, yplus, r21, r32, identity_ok=idok))

    print("\nROWS")
    for r in rows:
        print("  %-4s %-22s %s" % (r["row"], r["verdict"], r["why"]))

    # D534: REPORTED is a ROW CLASS and is EXCLUDED from the census, in words.
    graded = [r for r in rows]
    npass = sum(1 for r in graded if r["verdict"] == VERDICT_PASS)
    print("\nTALLY: %d of %d graded rows PASS. The %d REPORTED rows (%s) are a "
          "ROW CLASS, not a verdict, and are EXCLUDED from this census "
          "(ruling D534, Sanaa APPROVED 2026-08-27)."
          % (npass, len(graded), len(REPORTED_ROWS), ", ".join(REPORTED_ROWS)))
    return 0 if npass == len(graded) else 1


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
def selftest():
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("analyse_t5b.py --selftest")

    # -- NO REFERENCE VALUE IS HARD-CODED, AND THIS IS ENFORCED, NOT ASSERTED --
    src = open(os.path.abspath(__file__), errors="replace").read()
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

    # -- L-342 CLASSES, BOTH HALVES (the mark_done_t3_rff.py:143-144 shape) --
    ok(_l342_class("yPlus.dat").startswith("GATE INPUT"),
       "yPlus.dat is a GATE INPUT and NEVER infrastructure")
    ok(_l342_class("rc_value") == "PHYSICS-CRITICAL", "R-RC: the rc VALUE is physics")
    ok(_l342_class("rc_record") == "INFRASTRUCTURE", "R-RC: the rc RECORD is infrastructure")
    ok(_l342_class("core_min") == "INFRASTRUCTURE", "core_min is infrastructure")
    ok(_l342_class("ExecutionTime_line_count") == "INFRASTRUCTURE",
       "the ExecutionTime LINE count is infrastructure")
    ok(_l342_class("T") == "PHYSICS-CRITICAL", "a solved field is physics-critical")

    tmp = tempfile.mkdtemp(prefix="t5b_st_")
    try:
        # a forged COMPLETE case, then each physics-critical clause knocked out
        def forge(case="C", rc="0", with_end=True, last=ENDTIME, n_exec=ENDTIME,
                  fields=True, stale=False, status=True, fatal=False):
            root = os.path.join(tmp, "root_%d" % len(os.listdir(tmp)))
            cd = os.path.join(root, case)
            os.makedirs(os.path.join(cd, "0", "air"))
            os.makedirs(os.path.join(cd, str(ENDTIME), "air"))
            open(os.path.join(cd, "0", "air", "T"), "w").write("x")
            n_time = min(n_exec, ENDTIME)
            body = "".join("Time = %d\nExecutionTime = 1 s\n" % (i + 1)
                           for i in range(n_time))
            # extra ExecutionTime LINES with NO extra Time line: exactly the
            # petsc4Foam shape that L-342 classifies as INFRASTRUCTURE
            body += "ExecutionTime = 1 s\n" * max(0, n_exec - n_time)
            body = body.replace("Time = %d\n" % ENDTIME, "Time = %g\n" % last, 1) \
                if last != ENDTIME else body
            if fatal:
                body += "FOAM FATAL ERROR\n"
            if with_end:
                body += "End\n"
            open(os.path.join(cd, "log.solve"), "w").write(body)
            import time as _t
            _t.sleep(0.01)
            if fields:
                for f in REQUIRED_FIELDS:
                    open(os.path.join(cd, str(ENDTIME), "air", f), "w").write("y")
            if stale:
                old = os.path.getmtime(os.path.join(cd, "0", "air", "T")) + 10000
                for f in REQUIRED_FIELDS:
                    os.utime(os.path.join(cd, str(ENDTIME), "air", f), (old - 20000, old - 20000))
                os.utime(os.path.join(cd, "0", "air", "T"), (old, old))
            if status:
                open(os.path.join(root, "STATUS.%s" % case), "w").write(
                    "case=%s\nrc=%s\nwall_s=10\nranks=1\ncore_min=0.2\n"
                    "cap_core_min=1\ntimeout_s=60\ncapped=0\ncheckMesh_rc=0\n"
                    % (case, rc))
            return root

        r = check_completion(forge(), "C")
        ok(r[0], "a clean forged case is COMPLETE")
        ok(not check_completion(forge(rc="1"), "C")[0], "rc=1 -> NOT COMPLETE (physics)")
        ok(not check_completion(forge(with_end=False), "C")[0], "no End -> NOT COMPLETE")
        ok(not check_completion(forge(n_exec=ENDTIME - 1), "C")[0],
           "short ExecutionTime iteration count -> NOT COMPLETE")
        ok(not check_completion(forge(fields=False), "C")[0], "absent fields -> NOT COMPLETE")
        ok(not check_completion(forge(stale=True), "C")[0], "age guard -> NOT COMPLETE")
        ok(not check_completion(forge(fatal=True), "C")[0], "FOAM FATAL -> NOT COMPLETE")
        # THE INFRASTRUCTURE HALF (R-RC): absent STATUS is NOT MEASURED, not a refusal
        r2 = check_completion(forge(status=False), "C")
        ok(r2[0], "absent STATUS -> STILL COMPLETE (R-RC: the rc RECORD is infrastructure)")
        ok(any("INFERENCE" in n for n in r2[2]),
           "and rc=0 is printed as a LABELLED INFERENCE, never as a reading")
        ok(any("NOT MEASURED" in n for n in r2[2]), "and the record is NOT MEASURED")
        # a super-count of ExecutionTime LINES is infrastructure, not a refusal
        r3 = check_completion(forge(n_exec=ENDTIME + 2), "C")
        ok(r3[0], "ExecutionTime LINE over-count -> STILL COMPLETE (infrastructure)")

        # -- the y+ gate, four arms --
        def yp(rows_txt):
            cd = os.path.join(tmp, "yp_%d" % len(os.listdir(tmp)))
            d = os.path.join(cd, "postProcessing", "air", "yPlus", "0")
            os.makedirs(d)
            open(os.path.join(d, "yPlus.dat"), "w").write(
                "# y+ ()\n# Time\tpatch\tmin\tmax\taverage\n" + rows_txt)
            return cd
        good = "".join("%d\t%s\t0.1\t1.0\t0.5\n" % (ENDTIME, w) for w in YPLUS_WALLS)
        ok(gate_yplus(yp(good), "f")["state"] == "MET", "a compliant y+ set is MET")
        bad_roof = good.replace("%d\troof\t0.1\t1.0\t0.5" % ENDTIME,
                                "%d\troof\t0.1\t30.0\t12.0" % ENDTIME)
        ok(gate_yplus(yp(bad_roof), "f")["state"] == VERDICT_NAR,
           "roof at y+ 30 FIRES (T4/C1: a gate that names one wall certifies one wall)")
        short = "".join("%d\t%s\t0.1\t1.0\t0.5\n" % (ENDTIME, w)
                        for w in YPLUS_WALLS[:-1])
        ok(gate_yplus(yp(short), "f")["state"] == VERDICT_NAR, "an unreported wall FIRES")
        empty = os.path.join(tmp, "yp_empty")
        os.makedirs(os.path.join(empty, "postProcessing", "air", "yPlus", "0"))
        open(os.path.join(empty, "postProcessing", "air", "yPlus", "0",
                          "yPlus.dat"), "w").write("# y+ ()\n# Time\tpatch\tmin\tmax\taverage\n")
        g = gate_yplus(empty, "f")
        ok(g["state"] == VERDICT_NAR and "ZERO data rows" in g["why"],
           "DEFECT D1 REPRODUCED: a header-only yPlus.dat FIRES and names the defect")
        ok(gate_yplus(os.path.join(tmp, "nothing_here"), "f")["state"] == VERDICT_NAR,
           "an absent yPlus directory FIRES")
        ok(gate_yplus(yp(good.replace("\t1.0\t", "\t6.0\t")), "f")["state"] == VERDICT_NAR,
           "y+ above the sublayer bound 5.0 FIRES")

        # -- rule 5, the registered order, on synthetic triples --
        ymet = {lv: dict(state="MET", why="") for lv in LEVELS}
        ynar = {lv: dict(state=VERDICT_NAR, why="planted") for lv in LEVELS}
        R = dict(value=100.0, uncertainty=10.0)
        # f = 95 against ref 100: deviation 5 %, ABOVE the 1.7 % intrinsic floor
        # (a 1 % deviation would correctly return GATE REACHED, not PASS, and a
        # test that used one would be testing the floor, not the band)
        conv = dict(c=80.0, m=91.0, f=95.0)
        ok(grade_row("X", R, conv, ymet, 1.6060, 1.5929)["verdict"] == VERDICT_PASS,
           "a CONVERGING triple inside the band PASSes")
        div = dict(c=99.0, m=97.0, f=90.5)
        gr = grade_row("X", R, div, ymet, 1.6060, 1.5929)
        ok(gr["verdict"] == VERDICT_NAR and gr["triple"] == "DIVERGENT",
           "a DIVERGENT triple with a value INSIDE the band is still NOT A RESULT")
        ok(grade_row("X", R, dict(c=200.0, m=150.0, f=125.0), ymet, 1.6060,
                     1.5929)["verdict"] == VERDICT_FAIL,
           "a CONVERGING triple OUTSIDE the band is GATE FAIL")
        ok(grade_row("X", R, conv, ynar, 1.6060, 1.5929)["verdict"] == VERDICT_NAR,
           "the y+ gate turns a PASS into NOT A RESULT (never the reverse)")
        ok(grade_row("X", None, conv, ymet, 1.6060, 1.5929)["verdict"] == VERDICT_BLOCKED,
           "an absent reference is BLOCKED, not a fail")
        ok(grade_row("X", R, dict(c=99.5, m=99.8, f=99.9), ymet, 1.6060,
                     1.5929)["verdict"] == VERDICT_REACHED,
           "a deviation below the 1.7 %% intrinsic floor is GATE REACHED")
        ok(grade_row("X", R, conv, ymet, 1.6060, 1.5929, identity_ok=False)["verdict"]
           .endswith("identity"), "the G5 identity guard fires")
        ok(classify_triple(1.0, 1.0, 1.0) == "EXACT", "an EXACT triple is named")
        ok(classify_triple(1.0, 2.0, 1.5) == "OSCILLATORY", "an OSCILLATORY triple is named")

        # -- the MEASURED ratio is used, and it is not 2.0 --
        r21m, r32m = measured_ratios(CELLS_REGISTERED)
        ok(abs(r21m - 1.6060) < 5e-4 and abs(r32m - 1.5929) < 5e-4,
           "measured r21 = %.4f, r32 = %.4f from the registered cell counts"
           % (r21m, r32m))
        p_meas = gci_triple(90.0, 97.0, 99.0, r21m, r32m)[0]
        p_wrong = gci_triple(90.0, 97.0, 99.0, 2.0, 2.0)[0]
        ok(abs(p_meas - p_wrong) > 0.2,
           "using r = 2.0 instead of the measured ratio moves the observed order "
           "from %.3f to %.3f -- it is not a rounding choice" % (p_meas, p_wrong))

        # -- polyMesh area reader, PROVEN against a value known by construction --
        mesh = os.path.join(HERE, CASE_OF["c"], "constant", "air", "polyMesh")
        if os.path.isdir(mesh):
            a, bnd = patch_areas(mesh, YPLUS_WALLS)
            front = sum(a["cube_front"])
            ok(abs(front - 0.015 * 0.0075) < 1e-12,
               "the patch-area reader returns cube_front = %.9e m2, the analytic "
               "H*(H/2) on the half domain, to 1e-12" % front)
            ok(check_wall_set(bnd) == sorted(YPLUS_WALLS),
               "the mesh's OWN wall set equals the six registered walls "
               "(D2: cube_side_s does not exist and is not named)")
        else:
            ok(False, "the coarse mesh is not built, so the area reader is UNPROVEN here")

        # -- PRE-COMPUTE condition, checked not assumed --
        armed = [c for c in CASE_OF.values()
                 if os.path.exists(os.path.join(HERE, c, "0"))
                 or any(re.fullmatch(r"[0-9]+", d)
                        for d in os.listdir(os.path.join(HERE, c))
                        if os.path.isdir(os.path.join(HERE, c, d)))]
        ok(not armed, "PRE-COMPUTE: no T5b case holds a 0/ or a numeric time "
                      "directory%s" % ("" if not armed else " -- ARMED: %s" % armed))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # -- NEGATIVE CONTROLS: real mutations of this file, __pycache__ cleared --
    print("negative controls (a rule that cannot reject is not a rule):")
    muts = [
        ("N1 the y+ sublayer bound raised so a wall at 30 passes",
         "YPLUS_MAX = 5.0", "YPLUS_MAX = 500.0"),
        ("N2 cube_side_s put back into YPLUS_WALLS (defect D2 restored)",
         '"cube_side_n", "floor", "roof")', '"cube_side_n", "cube_side_s", "floor", "roof")'),
        ("N3 a DIVERGENT triple allowed to reach the band",
         'if tri != "CONVERGING":', 'if tri == "NEVER_THIS":'),
        ("N4 yPlus.dat reclassified as infrastructure",
         'if name == "yPlus.dat":\n        return "GATE INPUT',
         'if name == "yPlus.dat":\n        return "INFRASTRUCTURE" or ("GATE INPUT'),
    ]
    for label, old, new in muts:
        if src.count(old) < 1:
            ok(False, "%s -- the mutation anchor is not in the source" % label)
            continue
        d = tempfile.mkdtemp(prefix="t5b_mut_")
        try:
            p = os.path.join(d, "analyse_t5b.py")
            open(p, "w").write(src.replace(old, new, 1))
            for c in (os.path.join(HERE, "__pycache__"), os.path.join(d, "__pycache__")):
                shutil.rmtree(c, ignore_errors=True)
            r = subprocess.run([sys.executable, p, "--selftest"],
                               capture_output=True, text=True, cwd=d)
            ok(r.returncode != 0, "%s -> the selftest FAILS" % label)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv else HERE
    return run(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
