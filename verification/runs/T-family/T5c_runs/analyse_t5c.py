#!/usr/bin/env python3
"""T5c comparator -- the registered grading path for
`docs/campaigns/T-family/T5c_PREREGISTRATION.md` (frozen blob
e73a16cf5ccf4135f2d1e0b478ce9f829b01be2a, first landed by commit e0c5fee8).

WHAT THIS FILE IS, AND WHAT IT IS NOT
=====================================
T5c re-grades artifacts that ALREADY EXIST -- the three completed T5b levels at
`verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}` -- and changes EXACTLY ONE
thing against `analyse_t5b.py`: the STATISTIC the y+ LADDER clause is written on.
`R_max` (point maximum) -> `R_area` (area-weighted mean).  Every threshold is
carried over BYTE-IDENTICAL and that carry-over is ASSERTED AT GRADE TIME against
`analyse_t5b.py:142-146` rather than claimed (see `assert_thresholds_carried_over`).

`analyse_t5b.py` is FROZEN and is NEVER edited, imported-and-monkeypatched, or
superseded by this file (standing rules 2 and 6).  T5b's six `NOT A RESULT`
verdicts stand as published.  The readers this file reuses -- `read_points`,
`read_faces`, `read_boundary`, `face_area`, `patch_areas`, `check_wall_set`,
`read_patch_field`, `read_yplus_dat`, `read_status`, `check_completion`,
`face_mean_h`, `face_mean_T_C`, `classify_triple`, `gci_triple`, `band_verdict`,
`combined_band`, `grade_row`, `measured_ratios` -- are COPIED VERBATIM from
`analyse_t5b.py` so that the graded rows travel the identical call chain
(T5c section 6.1, "the identical call chain the graded rows travel").  A copy is
used rather than an import because importing a frozen module makes this file's
behaviour depend on a file this registration may not touch, and because
`T5c section 6.1` requires the chain be present in the instrument being frozen.

AUTHORITY THIS FILE RUNS UNDER
==============================
`VERIFICATION_CHARTER.md` v1.45 section 2d.11.2 (commit ad9eda53) GRANTED T5c's
section 2d.1 registration and DISCHARGED T5c's own stop line at `:287`
("No row of T5c may be graded until verification has ruled on section 2d.1").
The grant carries FOUR BINDING CONDITIONS and this file implements all four:

  (1) the section 6 birth arms Y-1..Y-5 PRINT before any row grades
      -> `run()` calls `birth_requirement()` before it reads a single graded
         value, and `refuse()`s (exit 2) if any arm fails either limb.
  (2) Y-3's refusal must be ARMED and must FIRE as designed -- refusing when
      area-weighting and face-count agree within 1 %, rather than passing
      vacuously
      -> `arm_Y3()` `refuse()`s on agreement; `--selftest` control `Y3-VACUOUS`
         drives a UNIFORM-area patch through it and requires the refusal.
  (3) the sublayer bound STAYS on the point maximum
      -> `gate_yplus_t5c()` clause Y-SUBLAYER reads `R_max`, threshold
         `YPLUS_MAX = 5.0`, unchanged.
  (4) because the repair is PERMISSIVE in outcome, EVERY GRADED ROW PRINTS BOTH
      STATISTICS, with the maximum's non-monotonicity shown where it occurs
      -> `print_both_statistics()` prints, for every wall and every level,
         `R_area` and `R_max` with each one's margin against the same bound, and
         flags every wall whose `R_max` is NON-MONOTONE under refinement.  It is
         called for EVERY row regardless of verdict.

T5c section 7 condition (4) additionally requires the pre-repair state beside
every published row; `PRE_REPAIR_STATE` below is printed with each one.

THE RULE-3 CONTROL DEFECT THIS FILE DOES NOT REPRODUCE
======================================================
`VERIFICATION_CHARTER.md` section 2d.11.1 (same commit) GRANTED item A: the T3
rule-3 control sets `seen = max_change over ALL CELLS` and tests
`seen >= PLANT - 1e-15`, so THE PREDICATE NEVER ASKS WHETHER THE MAXIMUM IS AT
THE PLANTED CELL.  It certified a reader on a 2.47 K physical change at a
different cell while the plant was never the argmax.  Ruled: a rule-3 violation
inside a rule-3 control.

Every arm here therefore reads the plant back AT THE PLANTED FACE, by index, in
addition to the aggregate predicate T5c section 6.2 registers.  These per-face
readbacks are STRENGTHENINGS: they can only turn a passing arm into a REFUSAL,
never a refusal into a pass, so they cannot loosen a registered control.  They
are named `strengthening` in the printed output so a reader can tell the
registered predicate from the addition.

Refusals are `refuse()` -> `sys.exit(2)`.  NEVER a bare `assert`: `python3 -O`
strips asserts and a control that vanishes under an interpreter flag is not a
control.

Usage:
    analyse_t5c.py [--root DIR]     grade (default root: ../T5b_runs)
    analyse_t5c.py --selftest       synthetic controls only; reads no run tree
Exit 0 graded and every graded row PASS, 1 a graded row did not PASS,
2 refusal (a control failed, or an input is not what the registration names).
"""
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T_FAMILY = os.path.abspath(os.path.join(HERE, ".."))
DEFAULT_ROOT = os.path.join(T_FAMILY, "T5b_runs")
T5_RUNS = os.path.join(T_FAMILY, "T5_runs")
REFERENCE = os.path.join(T5_RUNS, "T5_reference_primary.json")
FROZEN_T5B = os.path.join(T_FAMILY, "T5b_runs", "analyse_t5b.py")

REGISTRATION = "docs/campaigns/T-family/T5c_PREREGISTRATION.md"
REGISTRATION_BLOB = "e73a16cf5ccf4135f2d1e0b478ce9f829b01be2a"

VERDICT_PASS = "PASS"
VERDICT_FAIL = "GATE FAIL"
VERDICT_NAR = "NOT A RESULT"
VERDICT_REACHED = "GATE REACHED"
VERDICT_BLOCKED = "BLOCKED"
ROWCLASS_REPORTED = "REPORTED"          # D534: a ROW CLASS, never a verdict

# T5c section 7 condition (4), verbatim.  Printed beside EVERY published row.
PRE_REPAIR_STATE = (
    "PRE-REPAIR STATE: NOT A RESULT (T5b y+ ladder clause on cube_front "
    "MAX = 2.310042 against bound 2.0)")

LEVELS = ("c", "m", "f")
CASE_OF = {"c": "T5_CUBE_c", "m": "T5_CUBE_m", "f": "T5_CUBE_f"}

# MEASURED cell counts, carried from analyse_t5b.py:132 and re-read at grade
# time from each case's own log.checkMesh.  T5c section 5: same three meshes.
CELLS_REGISTERED = {"c": 52684, "m": 212942, "f": 882024}

FS = 1.25                        # Roache safety factor, registered
ENDTIME = 5000
REQUIRED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

# ---------------------------------------------------------------------------
# THE CARRIED-OVER THRESHOLDS.  T5c section 5: "No number in this section is new.
# All are analyse_t5b.py:142-146 unchanged."  That claim is ASSERTED against the
# frozen file at grade time by assert_thresholds_carried_over(), not trusted.
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

PLANT_OFFSET = 1.234e-03         # for MEAN readers
PLANT_SPIKE = 9.876e+02          # for RANGE/MAX readers (L-340)

# The birth arms plant on this wall at this level.  cube_front is the patch the
# T5b clause fired on, and f is the level it fired at.
ARM_WALL = "cube_front"
ARM_LEVEL = "f"

Q95 = 0.95
Q50 = 0.50
REL_EXACT = 1e-9                 # T5c section 6.2 Y-1/Y-3: "within 1e-9 relative"
REL_FACE = 1e-12                 # the per-face strengthening readback
Y3_MIN_SEPARATION = 0.01         # T5c section 6.2 Y-3: "differ by > 1 %"
Y2_SEEN_FRACTION = 0.9           # T5c section 6.2 Y-2: ">= 0.9 x spike"
Y2_BLIND_SLACK = 1.001           # T5c section 6.2 Y-2: "no more than 1.001 x ..."


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def _l342_class(name):
    """The declared class of a named artefact.  Driven in --selftest."""
    if name in ("yPlus.dat", "yPlus_field"):
        return ("GATE INPUT (never infrastructure): T5c section 5 registers the "
                "y+ clauses on it and T5 S16.3.1 registers absent y+ as NOT A RESULT")
    if name in ("rc_value", "End", "last_time", "age_guard", "ExecutionTime_count") \
            or name in REQUIRED_FIELDS:
        return "PHYSICS-CRITICAL"
    if name in ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s", "capped",
                "checkMesh_rc", "rc_record", "ExecutionTime_line_count", "pid",
                "ledger_row", "log.launch", "CAP_ENFORCED.txt", "marker_mtime"):
        return "INFRASTRUCTURE"
    return "UNCLASSIFIED"


# ===========================================================================
# SECTION A -- readers COPIED VERBATIM from the frozen analyse_t5b.py.
# Cited by line so a reader can diff them: :193-:277, :280-:298, :304-:368,
# :406-:485, :495-:530, :597-:632, :635-:651, :654-:710, :716-:719.
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
    """BOTH directions.  T5c section 5 carries this clause over VERBATIM."""
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
    """The boundaryField entry for one patch, as a list of floats.

    VERBATIM analyse_t5b.py:304-333.  This is the reader T5c section 6.1 names,
    and it is the reader the graded rows travel."""
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
    """VERBATIM analyse_t5b.py:336-368.  Retained because T5c section 4.2's
    IDENTITY PROOF is re-executed at grade time against this reader, not
    inherited from the registration's prose."""
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
    """VERBATIM analyse_t5b.py:418-485.  Standing rule 4, all of it, including
    THE AGE GUARD: every field at endTime must be NEWER than the case's own
    0/**/T.  T5c section 5 carries the completion rule over unchanged."""
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
    """VERBATIM analyse_t5b.py:495-517."""
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
    """VERBATIM analyse_t5b.py:520-530."""
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
    """VERBATIM analyse_t5b.py:597-609.  Standing rule 5."""
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
    """VERBATIM analyse_t5b.py:612-632.  Fs = 1.25.  NEVER quoted when the three
    values are not monotone -- the caller checks classify_triple first."""
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
    """VERBATIM analyse_t5b.py:641-651.  T5 S7.3 arithmetic, UNCHANGED."""
    u = row.get("uncertainty")
    d = row.get("digitisation_increment")
    if u is None:
        return None
    if d is None:
        return float(u)
    return math.sqrt(float(u) ** 2 + float(d) ** 2)


def grade_row(name, ref_row, vals, yplus_states, r21, r32, identity_ok=True):
    """VERBATIM analyse_t5b.py:654-710.  THE REGISTERED ORDER (T5 S7.5, rule 5).

    T5c section 5: "the Roache ordering of rule 5" carries over unchanged.  The
    ONLY thing T5c moves is what makes `yplus_states[lv]["state"]` MET."""
    out = dict(row=name, values=vals)
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
    if tri != "CONVERGING":
        out.update(verdict=VERDICT_NAR,
                   why="grid triple is %s (rule 5): fine value %.6g printed, "
                       "not graded" % (tri, f_f))
        return out
    p, gci = gci_triple(f_c, f_m, f_f, r21, r32)
    out["order"] = p
    out["gci"] = gci
    if ref_row is None or ref_row.get("value") is None:
        out.update(verdict=VERDICT_BLOCKED,
                   why="no reference value; fine value %.6g and triple %s "
                       "REPORTED" % (f_f, tri))
        return out
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


def measured_ratios(cells):
    """VERBATIM analyse_t5b.py:716-719.  Celik/Roache subscripting, 1 = finest:
    r21 is the MEDIUM->FINE ratio and r32 the COARSE->MEDIUM one (T5c section 2's
    correction of fact, docket D566)."""
    r21 = (cells["f"] / cells["m"]) ** (1.0 / 3.0)
    r32 = (cells["m"] / cells["c"]) ** (1.0 / 3.0)
    return r21, r32


# ===========================================================================
# SECTION B -- THE CARRY-OVER ASSERTION.  T5c section 5's central claim, made
# executable.  "Every threshold is carried over BYTE-IDENTICAL from
# analyse_t5b.py:142-146."  A claim in prose is a claim; this is a check.
# ===========================================================================
def assert_thresholds_carried_over(frozen=FROZEN_T5B):
    """Re-parse the frozen module's own threshold literals and REFUSE on any
    difference.  This is the whole of T5c's rule-2 defence and it is the one
    thing a reader must not have to take on trust."""
    if not os.path.isfile(frozen):
        refuse("the frozen predecessor %s is absent: T5c section 5's "
               "byte-identical carry-over cannot be asserted, and an unasserted "
               "carry-over is a claim, not a check" % frozen)
    src = open(frozen, errors="replace").read()
    ns = {}
    wanted = ("YPLUS_WALLS", "YPLUS_MAX", "YPLUS_TARGET", "YPLUS_TARGET_TOL",
              "CELLS_REGISTERED", "FS", "ENDTIME", "REQUIRED_FIELDS", "T_REF_K",
              "INTRINSIC_FLOOR_PCT", "GRADED_H", "GRADED_T", "REPORTED_ROWS",
              "G5_IDENTITY_MARGIN_K", "G5_BOUND_LO_C", "G5_BOUND_HI_C",
              "PLANT_OFFSET", "PLANT_SPIKE", "LEVELS", "CASE_OF")
    for line in src.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*=\s*(.+?)(?:\s+#.*)?$", line)
        if not m or m.group(1) not in wanted:
            continue
        try:
            ns[m.group(1)] = eval(m.group(2), {"__builtins__": {}}, {})
        except Exception:
            continue
    # multi-line literals (YPLUS_WALLS spans two lines in the frozen file)
    mm = re.search(r"YPLUS_WALLS\s*=\s*\((.*?)\)", src, flags=re.S)
    if mm:
        ns["YPLUS_WALLS"] = tuple(
            x.strip().strip('"').strip("'")
            for x in mm.group(1).replace("\n", " ").split(",") if x.strip())
    here = dict(YPLUS_WALLS=YPLUS_WALLS, YPLUS_MAX=YPLUS_MAX,
                YPLUS_TARGET=YPLUS_TARGET, YPLUS_TARGET_TOL=YPLUS_TARGET_TOL,
                CELLS_REGISTERED=CELLS_REGISTERED, FS=FS, ENDTIME=ENDTIME,
                REQUIRED_FIELDS=REQUIRED_FIELDS, T_REF_K=T_REF_K,
                INTRINSIC_FLOOR_PCT=INTRINSIC_FLOOR_PCT, GRADED_H=GRADED_H,
                GRADED_T=GRADED_T, REPORTED_ROWS=REPORTED_ROWS,
                G5_IDENTITY_MARGIN_K=G5_IDENTITY_MARGIN_K,
                G5_BOUND_LO_C=G5_BOUND_LO_C, G5_BOUND_HI_C=G5_BOUND_HI_C,
                PLANT_OFFSET=PLANT_OFFSET, PLANT_SPIKE=PLANT_SPIKE,
                LEVELS=LEVELS, CASE_OF=CASE_OF)
    missing = [k for k in wanted if k not in ns]
    if missing:
        refuse("could not re-parse %s from the frozen %s -- the carry-over "
               "assertion cannot be performed and this comparator will not "
               "grade on an unverified threshold set"
               % (", ".join(missing), os.path.basename(frozen)))
    diffs = [(k, ns[k], here[k]) for k in wanted if ns[k] != here[k]]
    if diffs:
        refuse("THRESHOLD CARRY-OVER BROKEN. T5c section 5 registers every "
               "threshold as byte-identical to analyse_t5b.py:142-146. These "
               "differ: %s" % "; ".join("%s frozen=%r here=%r" % d for d in diffs))
    return sorted(wanted)


# ===========================================================================
# SECTION C -- THE THREE REGISTERED READERS.  T5c section 4.4.
# ===========================================================================
def R_area(vals, areas):
    """THE GATED STATISTIC.  Sum(y+_i * A_i) / Sum A_i."""
    tot = sum(areas)
    if tot <= 0.0:
        return None
    return sum(v * a for v, a in zip(vals, areas)) / tot


def R_max(vals):
    """The point maximum over the patch.  GATED against the sublayer bound only;
    REPORTED against the ladder.  Verification's binding condition 3."""
    return max(vals)


def R_facecount_mean(vals):
    """The UNWEIGHTED face-count mean -- what yPlus.dat's `average` column is
    proven to be (T5c section 4.2(ii)).  REPORTED, never gated."""
    return sum(vals) / len(vals)


def area_quantile(vals, areas, q):
    """The area-weighted q-quantile: sort faces by y+ ascending (ties broken by
    index, so the result is deterministic), accumulate AREA, and report the y+ at
    q of total patch area.  Returns (value, index, position_in_order)."""
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
    """REPORTED diagnostic.  T5c section 4.4."""
    return area_quantile(vals, areas, Q95)[0]


def R_median_area(vals, areas):
    """The area-weighted median.  Used ONLY by arm Y-4's negative limb."""
    return area_quantile(vals, areas, Q50)[0]


# ===========================================================================
# SECTION D -- SECTION 6.1: THE FOUR ROWS, RE-ASSERTED AT GRADE TIME
# ===========================================================================
FOAMFILE_OBJECT = re.compile(r"object\s+yPlus\s*;")
FOAMFILE_CLASS = re.compile(r"class\s+volScalarField\s*;")


def assert_section_6_1(case_dir, level, areas, bnd):
    """T5c section 6.1: "T5c's comparator MUST re-assert all four rows at grade
    time and refuse if any fails."  Four rows: producer, artifact, reader, write
    path.  Returns the path of the verified yPlus field."""
    out = []

    # ROW 1 -- PRODUCER.  The case's own controlDict must carry `type yPlus;`.
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse("section 6.1 row PRODUCER: no %s -- the producer of the gated "
               "artifact cannot be identified from the case itself" % cd)
    cdtxt = _strip(cd)
    if not re.search(r"type\s+yPlus\s*;", cdtxt):
        refuse("section 6.1 row PRODUCER: %s carries no `type yPlus;` function "
               "object. The registration names the OpenFOAM yPlus function "
               "object as the producer and the case does not run it." % cd)
    out.append("PRODUCER: `type yPlus;` present in %s"
               % os.path.relpath(cd, case_dir))

    # ROW 2 -- ARTIFACT.  The producer's own FoamFile header, and a calculated
    # nonuniform boundaryField entry for every registered wall.
    fld = os.path.join(case_dir, str(ENDTIME), "air", "yPlus")
    if not os.path.isfile(fld):
        refuse("section 6.1 row ARTIFACT: no %s. T5c section 4.1 registers this "
               "volScalarField as present on all three levels; it is not." % fld)
    head = open(fld, errors="replace").read(4096)
    if not FOAMFILE_CLASS.search(head) or not FOAMFILE_OBJECT.search(head):
        refuse("section 6.1 row ARTIFACT: %s does not carry the producer's own "
               "FoamFile header (`class volScalarField;` and `object yPlus;`). "
               "A control that plants into a file it wrote itself is the exact "
               "failure the birth requirement names." % fld)
    out.append("ARTIFACT: %s carries the producer's FoamFile header "
               "(class volScalarField, object yPlus), %d bytes"
               % (os.path.relpath(fld, case_dir), os.path.getsize(fld)))

    # ROW 3 -- READER, and section 6.2 arm Y-5 (SCHEMA / TUPLE INTEGRITY),
    # applied to EVERY registered wall rather than only the planted one.
    for w in YPLUS_WALLS:
        v = read_patch_field(fld, w)
        if v is None:
            refuse("section 6.1 row READER / arm Y-5: read_patch_field returned "
                   "None for wall %s at level %s -- the reader the graded rows "
                   "travel cannot read the gated artifact" % (w, level))
        n_mesh = bnd[w]["nFaces"]
        if len(v) == 0:
            refuse("arm Y-5 REFUSES: wall %s parsed to ZERO values at level %s. "
                   "This is the birth requirement's `empties the tuple it tests` "
                   "failure and it is closed explicitly." % (w, level))
        if len(v) != n_mesh:
            refuse("arm Y-5 REFUSES: wall %s parsed %d values but the mesh's own "
                   "boundary declares nFaces %d at level %s. A reader that "
                   "disagrees with the mesh about how many faces it read is not "
                   "reading the patch." % (w, len(v), n_mesh, level))
        if len(areas[w]) != n_mesh:
            refuse("arm Y-5 REFUSES: patch_areas returned %d areas for wall %s "
                   "but the mesh declares nFaces %d at level %s"
                   % (len(areas[w]), w, n_mesh, level))
    out.append("READER + arm Y-5: read_patch_field and patch_areas agree with "
               "the mesh's own boundary nFaces on all %d registered walls"
               % len(YPLUS_WALLS))

    # ROW 4 -- WRITE PATH.  Refuse if a scratch copy would resolve inside the
    # case tree.  Checked HERE, before any plant is written.
    probe = tempfile.mkdtemp(prefix="t5c_writepath_probe_")
    try:
        rp = os.path.realpath(probe)
        rc = os.path.realpath(case_dir)
        if rp == rc or rp.startswith(rc + os.sep):
            refuse("section 6.1 row WRITE PATH: the scratch directory %s "
                   "resolves INSIDE the case tree %s. A plant written into the "
                   "run tree corrupts the artifact it is testing." % (rp, rc))
    finally:
        shutil.rmtree(probe, ignore_errors=True)
    out.append("WRITE PATH: scratch resolves outside the case tree; the run tree "
               "is never written")
    return fld, out


# ===========================================================================
# SECTION E -- THE IDENTITY PROOF, RE-EXECUTED AT GRADE TIME
# T5c section 4.2 measured it once before the freeze.  A measurement in a
# document is a measurement about the past; this re-runs it on the bytes the
# gate is about to read.
# ===========================================================================
def identity_proof(case_dir, fld, level):
    dat, why = read_yplus_dat(case_dir)
    if dat is None:
        refuse("identity proof: yPlus.dat unreadable at level %s (%s). T5c "
               "section 4.2 proves the field carries the same quantity as the "
               "frozen gate read; without the .dat the proof cannot be re-run."
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
                       "%.0e. T5c changes the STATISTIC and nothing else; if "
                       "the field is not the same data the frozen gate read, "
                       "that claim is false and no row may be graded."
                       % (level, w, label, a, b, rel, REL_EXACT))
        rows.append((w, fmin, fmax, fmean))
    return rows


# ===========================================================================
# SECTION F -- THE BIRTH REQUIREMENT, ARM BY ARM (T5c section 6.2)
# Verification binding condition 1: these PRINT before any row grades.
# Every arm prints BOTH limbs; an arm that prints one limb is a FAILED control.
# ===========================================================================
def _locate_patch_list(text, patch):
    """The (start, end) character span of the patch's nonuniform value list.
    Mirrors analyse_t5b.py:557-565, the frozen plant's own locator."""
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
    control, never a passing one (T5c section 6.2's closing sentence)."""

    def __init__(self, aid, title):
        self.aid = aid
        self.title = title
        self.positive = None
        self.negative = None
        self.strengthening = []
        self.lines = []

    def pos(self, ok, msg):
        self.positive = (ok, msg)

    def neg(self, ok, msg):
        self.negative = (ok, msg)

    def strong(self, ok, msg):
        self.strengthening.append((ok, msg))

    def report(self):
        if self.positive is None or self.negative is None:
            refuse("arm %s printed only one limb. T5c section 6.2: `An arm that "
                   "prints one limb is registered here as a FAILED control, not "
                   "a passing one.`" % self.aid)
        print("  %s %s" % (self.aid, self.title))
        print("      POSITIVE (must be SEEN) : %-4s %s"
              % ("ok" if self.positive[0] else "FAIL", self.positive[1]))
        print("      NEGATIVE (must NOT fire): %-4s %s"
              % ("ok" if self.negative[0] else "FAIL", self.negative[1]))
        for ok, msg in self.strengthening:
            print("      strengthening          : %-4s %s"
                  % ("ok" if ok else "FAIL", msg))
        bad = [m for ok, m in [self.positive, self.negative] + self.strengthening
               if not ok]
        return bad


def birth_requirement(case_dir, fld, areas, wall=ARM_WALL, level=ARM_LEVEL):
    """T5c section 6.2, arms Y-1..Y-5, on the REAL producer's field through the
    REAL reader, planted into a SCRATCH COPY.  Refuses on any failed limb.

    Y-5 is discharged inside assert_section_6_1 (schema/tuple integrity across
    every registered wall, before any plant is written); it is reported here so
    the five arms print together.
    """
    print("\nBIRTH REQUIREMENT (Sanaa 2026-08-28; T5c section 6, made BINDING by")
    print("VERIFICATION_CHARTER section 2d.11.2 condition 1) -- planted on wall")
    print("%s at level %s, in a scratch copy of the producer's own field."
          % (wall, level))

    A = areas[wall]
    totA = sum(A)
    base_text = _strip(fld)
    span = _locate_patch_list(base_text, wall)
    if span is None:
        refuse("birth requirement: wall %s is not a nonuniform list in %s -- "
               "there is nothing to plant into" % (wall, fld))
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

    tmp = tempfile.mkdtemp(prefix="t5c_plant_")
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
                   "(relative %.3e, bound %.0e); a weighted mean is affine so "
                   "the answer is exact, not approximate"
                   % (moved, PLANT_OFFSET, rel, REL_EXACT))
            # NEGATIVE: two reads of IDENTICAL BYTES must differ by EXACTLY 0.0
            again = read_patch_field(wf, wall)
            d0 = R_area(again, A) - R_area(got, A)
            a1.neg(d0 == 0.0,
                   "two reads of identical bytes differ by %r (must be exactly "
                   "0.0); a reader noisy on unchanged bytes cannot be credited "
                   "with any move" % d0)
            # STRENGTHENING (section 2d.11.1): read the plant back AT EVERY
            # PLANTED FACE, not as an aggregate that could move for another reason
            worst = 0.0
            for i in range(n):
                den = abs(base_vals[i] + PLANT_OFFSET)
                den = den if den > 0 else 1.0
                worst = max(worst, abs(got[i] - (base_vals[i] + PLANT_OFFSET)) / den)
            a1.strong(worst <= REL_FACE,
                      "every one of the %d planted faces reads back as "
                      "base+plant, worst relative %.3e (bound %.0e) -- the "
                      "predicate asks whether the plant was seen AT the planted "
                      "faces, not merely whether something moved" % (n, worst, REL_FACE))
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
                   "R_max moved %.6f against the required >= %.6f "
                   "(%.1f x the %.4f spike) -- the max reader sees it"
                   % (dmax, Y2_SEEN_FRACTION * PLANT_SPIKE, Y2_SEEN_FRACTION,
                      PLANT_SPIKE))
            bound = Y2_BLIND_SLACK * PLANT_SPIKE * A[big] / totA
            darea = abs(R_area(got2, A) - base_area)
            a2.neg(darea <= bound,
                   "R_area moved %.9e against the blindness bound %.9e "
                   "(= %.3f x spike x A_face/sumA, A_face %.6e of %.6e); the "
                   "area average is NEARLY BLIND to the point peak the old gate "
                   "was dominated by"
                   % (darea, bound, Y2_BLIND_SLACK, A[big], totA))
            # STRENGTHENING (section 2d.11.1): the argmax must BE the planted
            # face, and the planted face must read back as base+spike.  The
            # registered predicate reads an aggregate move; on its own that is
            # the shape item A condemned.
            arg = max(range(n), key=lambda i: (got2[i], i))
            a2.strong(arg == big,
                      "the argmax of the planted field is face %d, the face the "
                      "spike was planted into (%d) -- the predicate ASKS whether "
                      "the maximum is AT the planted face" % (arg, big))
            den = abs(base_vals[big] + PLANT_SPIKE)
            rel = abs(got2[big] - (base_vals[big] + PLANT_SPIKE)) / (den if den else 1.0)
            a2.strong(rel <= REL_FACE,
                      "face %d reads back %.9f against base+spike %.9f "
                      "(relative %.3e)" % (big, got2[big],
                                           base_vals[big] + PLANT_SPIKE, rel))
            # every OTHER face must be unchanged: a spike that moved its
            # neighbours would make the blindness bound meaningless
            others = max((abs(got2[i] - base_vals[i]) for i in range(n) if i != big),
                         default=0.0)
            a2.strong(others == 0.0,
                      "every one of the other %d faces is byte-for-byte "
                      "unchanged (max |delta| %r), so the blindness bound is "
                      "about the plant and nothing else" % (n - 1, others))
        arms.append(a2)

        # ---- Y-3 AREA WEIGHTING IS REAL --------------------------------
        a3 = Arm("Y-3", "AREA WEIGHTING IS REAL -- not a face count in disguise")
        k = max(1, int(round(0.10 * n)))
        by_area = sorted(range(n), key=lambda i: (-A[i], i))[:k]
        dec_area = sum(A[i] for i in by_area)
        area_pred = PLANT_OFFSET * (dec_area / totA)
        fc_pred = PLANT_OFFSET * (k / n)
        sep = abs(area_pred - fc_pred) / (abs(fc_pred) if fc_pred else 1.0)
        # THE ANTI-VACUITY REFUSAL.  Verification binding condition 2: this must
        # be ARMED and must FIRE as designed, not pass vacuously.
        if sep <= Y3_MIN_SEPARATION:
            refuse("arm Y-3 REFUSES: the area-weighted prediction %.12e and the "
                   "FACE-COUNT prediction %.12e differ by only %.4f %%, which is "
                   "not more than the registered %.0f %%. A weighting control on "
                   "a patch this uniform is VACUOUS and T5c section 6.2 requires "
                   "it to say so rather than pass. (wall %s, level %s, %d faces, "
                   "largest-area decile k=%d holding %.6f of the area)"
                   % (area_pred, fc_pred, 100 * sep, 100 * Y3_MIN_SEPARATION,
                      wall, level, n, k, dec_area / totA))
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
                   "(relative %.3e, bound %.0e); decile k=%d of %d faces holds "
                   "%.6f of the patch area against %.6f of its face count"
                   % (moved, area_pred, rel_a, REL_EXACT, k, n,
                      dec_area / totA, k / n))
            rel_f = abs(moved - fc_pred) / (abs(fc_pred) if fc_pred else 1.0)
            a3.neg(rel_f > Y3_MIN_SEPARATION,
                   "R_area did NOT move by the FACE-COUNT prediction %.12e "
                   "(observed differs from it by %.4f %%, required > %.0f %%); "
                   "the two predictions are separated by %.4f %%, so the arm is "
                   "ARMABLE on this mesh and was re-measured, never assumed"
                   % (fc_pred, 100 * rel_f, 100 * Y3_MIN_SEPARATION, 100 * sep))
        arms.append(a3)

        # ---- Y-4 QUANTILE SENSITIVITY ----------------------------------
        a4 = Arm("Y-4", "QUANTILE SENSITIVITY -- R_q95 is a quantile")
        order = sorted(range(n), key=lambda i: (base_vals[i], i))
        _v95, i95, pos95 = area_quantile(base_vals, A, Q95)
        _v50, i50, pos50 = area_quantile(base_vals, A, Q50)
        tail = order[pos95:]                      # the crossing face and above
        if i50 in tail:
            refuse("arm Y-4 REFUSES: the area-weighted MEDIAN face is inside the "
                   "95th-percentile tail on wall %s level %s, so the negative "
                   "limb (the median must NOT move) is vacuous. One face would "
                   "have to hold more than 45 %% of the patch area." % (wall, level))
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
                   "R_q95 moved %.12e against the plant %.12e (relative %.3e, "
                   "bound %.0e); the tail is %d of %d faces and adding a "
                   "positive constant to the largest values preserves the order, "
                   "so the crossing face is unchanged and the move is exact"
                   % (dq, PLANT_OFFSET, rel_q, REL_EXACT, len(tail), n))
            dmed = R_median_area(got4, A) - base_med
            a4.neg(dmed == 0.0,
                   "the area-weighted MEDIAN moved by %r (must be exactly 0.0). "
                   "A `quantile` that responds to a perturbation confined to the "
                   "far tail the way the median does is not a quantile." % dmed)
            # STRENGTHENING: the plant must be readable back at the crossing face
            den = abs(base_vals[i95] + PLANT_OFFSET)
            rel = abs(got4[i95] - (base_vals[i95] + PLANT_OFFSET)) / (den if den else 1.0)
            a4.strong(rel <= REL_FACE,
                      "the 95 %% crossing face (index %d, order position %d of "
                      "%d) reads back as base+plant, relative %.3e"
                      % (i95, pos95, n, rel))
            a4.strong(got4[i50] == base_vals[i50],
                      "the median face (index %d, order position %d) is "
                      "byte-for-byte unchanged, so its zero move is a fact about "
                      "the plant and not about the reader" % (i50, pos50))
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
               "disagreeing with the mesh -- the birth requirement's `empties "
               "the tuple it tests` failure; it did not fire here, which is the "
               "required outcome for the negative limb")
        arms.append(a5)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for a in arms:
        failures.extend(a.report())
    if failures:
        refuse("BIRTH REQUIREMENT FAILED -- %d limb(s): %s. Sanaa 2026-08-28: "
               "`no instrument grades anything until that answer is yes, "
               "demonstrated.` No row of T5c is graded."
               % (len(failures), " | ".join(failures)))
    print("  ALL FIVE ARMS PRINTED BOTH LIMBS AND PASSED. Verification binding")
    print("  condition 1 (VERIFICATION_CHARTER section 2d.11.2) is discharged.")
    return True


# ===========================================================================
# SECTION G -- THE GATE (T5c section 5)
# ===========================================================================
def read_level_statistics(case_dir, fld, areas):
    """R_area, R_max, R_q95 and the face-count mean for every registered wall."""
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


def gate_yplus_t5c(stats, level):
    """T5c section 5, in the registered order.

    Y-SUBLAYER on R_max (UNCHANGED from T5b -- verification binding condition 3),
    then Y-LADDER on R_area (the ONE thing that moves).  Both breaches are
    NOT A RESULT."""
    tgt = YPLUS_TARGET[level]
    bound = tgt * YPLUS_TARGET_TOL

    over = {w: stats[w]["R_max"] for w in YPLUS_WALLS
            if stats[w]["R_max"] > YPLUS_MAX}
    if over:
        return dict(state=VERDICT_NAR, stats=stats, clause="Y-SUBLAYER",
                    why="R_max exceeds the registered sublayer bound %.1f on: %s "
                        "-- a physics precondition, and it stays on the POINT "
                        "MAXIMUM because one face outside the viscous sublayer "
                        "invalidates the wall treatment there"
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
    """Observed order of a statistic across the ladder, as T5c section 2 reports
    it: p(c->m) uses r32, p(m->f) uses r21.  Returns (p_cm, p_mf) or Nones."""
    def _p(a, b, r):
        if a <= 0 or b <= 0 or r <= 1.0:
            return None
        try:
            return math.log(a / b) / math.log(r)
        except ValueError:
            return None
    return _p(v_c, v_m, r32), _p(v_m, v_f, r21)


def print_both_statistics(levels_stats, r21, r32):
    """VERIFICATION_CHARTER section 2d.11.2 BINDING CONDITION 4, verbatim:
    `BECAUSE THE REPAIR IS PERMISSIVE IN OUTCOME, EVERY GRADED ROW PRINTS BOTH
    STATISTICS -- area average and point maximum, with the maximum's
    non-monotonicity shown where it occurs. A reader must be able to see what the
    old clause would have said, from the row.`

    Printed for EVERY wall and EVERY level regardless of verdict, per T5c
    section 7 condition (4)."""
    print("\nBOTH STATISTICS, EVERY WALL, EVERY LEVEL "
          "(VERIFICATION_CHARTER section 2d.11.2 condition 4)")
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
              % (w,
                 "%.3f" % p_max[0] if p_max[0] is not None else "n/a",
                 "%.3f" % p_max[1] if p_max[1] is not None else "n/a",
                 "MONOTONE decreasing" if mono_max
                 else "*** NON-MONOTONE UNDER REFINEMENT ***"))
        print("  %-12s ->  R_area observed order p(c->m) %s p(m->f) %s  %s"
              % (w,
                 "%.3f" % p_area[0] if p_area[0] is not None else "n/a",
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
        print("  A statistic that increases under refinement cannot estimate how")
        print("  resolution scales (VERIFICATION_CHARTER section 2d.11.2). Where")
        print("  R_area appears here, T5c's OWN replacement statistic carries the")
        print("  defect item B condemned, and that is reported rather than hidden.")
    else:
        print("  NON-MONOTONE UNDER REFINEMENT: none on either statistic.")
    return nonmono


# ===========================================================================
# SECTION H -- run()
# ===========================================================================
def run(root):
    if not os.path.isfile(REFERENCE):
        refuse("no reference at %s" % REFERENCE)
    ref = json.load(open(REFERENCE))
    if not ref.get("provenance", {}).get("digitised"):
        refuse("the reference is not marked digitised")

    print("T5c comparator -- registration %s (frozen blob %s)"
          % (REGISTRATION, REGISTRATION_BLOB))
    print("authority: VERIFICATION_CHARTER.md v1.45 section 2d.11.2, commit "
          "ad9eda53 -- item B GRANTED on four binding conditions; T5c's own")
    print("           stop line at :287 is DISCHARGED. The grant licenses NO "
          "verdict: rule 5's one direction stands.")
    print("re-grades: existing artifacts under %s. NO SOLVER COMPUTE." % root)
    print("reference: %s (digitised %s)"
          % (os.path.relpath(REFERENCE, T_FAMILY),
             ref["provenance"].get("digitised_utc")))

    carried = assert_thresholds_carried_over()
    print("THRESHOLD CARRY-OVER ASSERTED against analyse_t5b.py: %d names "
          "identical (%s). T5c section 5's `only the STATISTIC changes` is a "
          "CHECK here, not a claim." % (len(carried), ", ".join(carried)))
    print("L-342 classes: %s"
          % "; ".join("%s=%s" % (f, _l342_class(f).split(":")[0])
                      for f in ("T", "rc_value", "rc_record", "yPlus_field",
                                "core_min", "ExecutionTime_line_count")))

    cells = {}
    areas_by_level = {}
    fields = {}
    levels_stats = {}
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

        fld, rows61 = assert_section_6_1(case_dir, lv, a, bnd)
        fields[lv] = fld
        idrows = identity_proof(case_dir, fld, lv)
        st, err = read_level_statistics(case_dir, fld, a)
        if st is None:
            refuse("level %s: %s" % (lv, err))
        levels_stats[lv] = st
        yplus[lv] = gate_yplus_t5c(st, lv)

        print("\n  level %s  %-11s cells %7d  completion: %s"
              % (lv, case, cells[lv],
                 "COMPLETE" if ok else "NOT COMPLETE (%s)" % why))
        for r in rows61:
            print("      section 6.1  %s" % r)
        print("      identity proof: field min/max/unweighted-mean reproduce "
              "yPlus.dat's min/max/average to better than %.0e relative on all "
              "%d registered walls -- so the FIELD is the same data the frozen "
              "gate read, and yPlus.dat's `average` column is the UNWEIGHTED "
              "FACE-COUNT mean" % (REL_EXACT, len(idrows)))
        print("      y+ gate: %s -- %s" % (yplus[lv]["state"], yplus[lv]["why"]))
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

    # BINDING CONDITION 1: the birth arms print BEFORE any row grades.
    birth_requirement(os.path.join(root, CASE_OF[ARM_LEVEL]),
                      fields[ARM_LEVEL], areas_by_level[ARM_LEVEL])

    # BINDING CONDITION 4 + T5c section 7(4): both statistics, every wall, every
    # level, before the rows.
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

    print("\nROWS -- each carries the pre-repair state beside it "
          "(T5c section 7 condition 4)")
    for r in rows:
        patch = GRADED_H.get(r["row"]) or GRADED_T.get(r["row"])
        print("  %-4s %-22s %s" % (r["row"], r["verdict"], r["why"]))
        print("       %s" % PRE_REPAIR_STATE)
        print("       both statistics on this row's wall %s: %s"
              % (patch, "; ".join(
                  "%s R_area %.6f / R_max %.6f"
                  % (lv, levels_stats[lv][patch]["R_area"],
                     levels_stats[lv][patch]["R_max"]) for lv in LEVELS)))

    graded = [r for r in rows]
    npass = sum(1 for r in graded if r["verdict"] == VERDICT_PASS)
    print("\nTALLY: %d of %d graded rows PASS. The %d REPORTED rows (%s) are a "
          "ROW CLASS, not a verdict, and are EXCLUDED from this census "
          "(ruling D534, Sanaa APPROVED 2026-08-27)."
          % (npass, len(graded), len(REPORTED_ROWS), ", ".join(REPORTED_ROWS)))
    return 0 if npass == len(graded) else 1


# ===========================================================================
# SECTION I -- selftest.  SYNTHETIC ONLY: it reads no run tree, so it can be
# driven before the re-grade is enqueued and proves the instrument is not
# broken without touching the artifacts it will grade.
# ===========================================================================
def selftest():
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("T5c comparator selftest -- SYNTHETIC FIXTURES ONLY, no run tree read")

    # --- the three readers, against hand-computable answers ---------------
    v = [1.0, 2.0, 3.0, 4.0]
    A = [1.0, 1.0, 1.0, 7.0]          # 10 total; face 3 holds 70 %
    ok(abs(R_area(v, A) - (1 + 2 + 3 + 28) / 10.0) < 1e-15,
       "R_area on a hand-computed patch = %.6f (expected 3.4)" % R_area(v, A))
    ok(abs(R_facecount_mean(v) - 2.5) < 1e-15,
       "R_facecount_mean = %.6f (expected 2.5)" % R_facecount_mean(v))
    ok(R_max(v) == 4.0, "R_max = %.1f (expected 4.0)" % R_max(v))
    # NOTE, recorded because this selftest caught it and the mistake was MINE,
    # not the reader's: the first draft of this line expected 3.0. Cumulative
    # AREA over the value-ascending order is 1, 2, 3, 10; half of the total 10
    # is 5.0, which is not reached until the FOURTH face. The area-weighted
    # median of this patch is 4.0. An area median is not a value median, and a
    # single face holding 70 % of the area drags it to the top. Left in with the
    # arithmetic written out so no later reader re-derives the wrong expectation.
    ok(R_median_area(v, A) == 4.0,
       "area-weighted median = %.1f: cumulative area 1,2,3,10 first reaches "
       "half of 10 at the fourth face (expected 4.0)" % R_median_area(v, A))
    ok(R_q95(v, A) == 4.0,
       "R_q95 = %.1f: 95 %% of area 10 is 9.5, reached only at value 4.0"
       % R_q95(v, A))
    ok(R_area(v, A) != R_facecount_mean(v),
       "on a NON-UNIFORM patch the area mean %.4f and the face-count mean %.4f "
       "are different numbers -- the whole premise of T5c section 4.3"
       % (R_area(v, A), R_facecount_mean(v)))
    vu = [1.0, 2.0, 3.0, 4.0]
    Au = [1.0, 1.0, 1.0, 1.0]
    ok(R_area(vu, Au) == R_facecount_mean(vu),
       "on a UNIFORM patch they coincide -- which is exactly the case Y-3 must "
       "REFUSE rather than pass")

    # --- Y-1 affinity, the closed form the arm relies on ------------------
    moved = R_area([x + PLANT_OFFSET for x in v], A) - R_area(v, A)
    ok(abs(moved - PLANT_OFFSET) / PLANT_OFFSET <= REL_EXACT,
       "Y-1 closed form: a constant offset moves a weighted mean by exactly the "
       "offset (relative error %.3e)" % (abs(moved - PLANT_OFFSET) / PLANT_OFFSET))

    # --- Y-2 blindness bound ----------------------------------------------
    sp = list(v)
    sp[3] += PLANT_SPIKE
    d_area = abs(R_area(sp, A) - R_area(v, A))
    bound = Y2_BLIND_SLACK * PLANT_SPIKE * A[3] / sum(A)
    ok(d_area <= bound,
       "Y-2 negative limb arithmetic: a single-face spike moves R_area by "
       "%.6f, inside the bound %.6f" % (d_area, bound))
    ok(R_max(sp) - R_max(v) >= Y2_SEEN_FRACTION * PLANT_SPIKE,
       "Y-2 positive limb arithmetic: the same spike moves R_max by %.4f"
       % (R_max(sp) - R_max(v)))
    ok(max(range(len(sp)), key=lambda i: (sp[i], i)) == 3,
       "Y-2 STRENGTHENING: the argmax is the PLANTED face. This is the "
       "predicate VERIFICATION_CHARTER section 2d.11.1 found missing in the T3 "
       "control, which read the max change over ALL cells and never asked "
       "whether it was at the planted cell")
    # PLANTED FAILURE: a change at a DIFFERENT face must NOT satisfy the
    # strengthened predicate, even though the aggregate move is identical.
    other = list(v)
    other[0] += PLANT_SPIKE
    agg_ok = (R_max(other) - R_max(v)) >= Y2_SEEN_FRACTION * PLANT_SPIKE
    strong_ok = max(range(len(other)), key=lambda i: (other[i], i)) == 3
    ok(agg_ok and not strong_ok,
       "PLANTED FAILURE (item A's defect, reproduced deliberately): a spike at "
       "face 0 satisfies the AGGREGATE predicate (%s) but FAILS the "
       "at-the-planted-face predicate (%s). The strengthening is load-bearing, "
       "not decoration." % (agg_ok, strong_ok))

    # --- Y-3 anti-vacuity: the refusal must FIRE on a uniform patch -------
    n = 40
    vv = [float(i) for i in range(n)]
    uni = [1.0] * n
    k = max(1, int(round(0.10 * n)))
    by_area = sorted(range(n), key=lambda i: (-uni[i], i))[:k]
    dec = sum(uni[i] for i in by_area)
    ap = PLANT_OFFSET * (dec / sum(uni))
    fp = PLANT_OFFSET * (k / n)
    sep_uniform = abs(ap - fp) / abs(fp)
    ok(sep_uniform <= Y3_MIN_SEPARATION,
       "Y-3 CONTROL (verification binding condition 2): on a UNIFORM-area patch "
       "the area and face-count predictions are separated by %.6f %%, which is "
       "NOT more than %.0f %% -- so arm Y-3 REFUSES rather than passing "
       "vacuously. The refusal is armed."
       % (100 * sep_uniform, 100 * Y3_MIN_SEPARATION))
    # and on a strongly non-uniform patch it is ARMABLE
    nu = [1.0] * (n - k) + [50.0] * k
    by_area2 = sorted(range(n), key=lambda i: (-nu[i], i))[:k]
    dec2 = sum(nu[i] for i in by_area2)
    ap2 = PLANT_OFFSET * (dec2 / sum(nu))
    sep_nu = abs(ap2 - fp) / abs(fp)
    ok(sep_nu > Y3_MIN_SEPARATION,
       "Y-3 is ARMABLE on a non-uniform patch: separation %.4f %% > %.0f %%"
       % (100 * sep_nu, 100 * Y3_MIN_SEPARATION))

    # --- Y-4 quantile behaviour -------------------------------------------
    n2 = 100
    qv = [float(i) for i in range(n2)]
    qa = [1.0 + 0.05 * i for i in range(n2)]
    _b95, i95, pos95 = area_quantile(qv, qa, Q95)
    _b50, i50, pos50 = area_quantile(qv, qa, Q50)
    order = sorted(range(n2), key=lambda i: (qv[i], i))
    tail = order[pos95:]
    pv = list(qv)
    for i in tail:
        pv[i] += PLANT_OFFSET
    dq = R_q95(pv, qa) - R_q95(qv, qa)
    ok(abs(dq - PLANT_OFFSET) / PLANT_OFFSET <= REL_EXACT,
       "Y-4 positive limb: offsetting the %d-face tail moves R_q95 by %.12e "
       "against the plant %.12e" % (len(tail), dq, PLANT_OFFSET))
    ok((R_median_area(pv, qa) - R_median_area(qv, qa)) == 0.0,
       "Y-4 negative limb: the area-weighted median moves by EXACTLY 0.0 under "
       "the same plant (median face index %d, tail starts at order position %d)"
       % (i50, pos95))
    # PLANTED FAILURE: a reader that returned the MEAN instead of a quantile
    # would move under this plant, so the negative limb discriminates.
    mean_moved = R_area(pv, qa) - R_area(qv, qa)
    ok(mean_moved != 0.0,
       "PLANTED FAILURE: a MEAN-shaped reader moves by %.12e under the tail "
       "plant, so Y-4's negative limb distinguishes a quantile from a mean"
       % mean_moved)

    # --- rule 5, the five triple classes ----------------------------------
    ok(classify_triple(3.0, 2.0, 1.5) == "CONVERGING", "triple CONVERGING")
    ok(classify_triple(1.0, 2.0, 4.0) == "DIVERGENT", "triple DIVERGENT")
    ok(classify_triple(1.0, 2.0, 1.5) == "OSCILLATORY", "triple OSCILLATORY")
    ok(classify_triple(1.0, 1.0, 2.0) == "STAGNANT", "triple STAGNANT")
    ok(classify_triple(1.0, 1.0, 1.0) == "EXACT", "triple EXACT")
    st = {lv: dict(state="MET", why="") for lv in LEVELS}
    bad = dict(st)
    bad = {lv: dict(state="MET", why="") for lv in LEVELS}
    bad["f"] = dict(state=VERDICT_NAR, why="planted y+ refusal")
    r = grade_row("G1a", dict(value=10.0, uncertainty=1.0),
                  dict(c=3.0, m=2.0, f=1.5), bad, 1.6, 1.59)
    ok(r["verdict"] == VERDICT_NAR,
       "rule 5 step (1): a y+ gate not MET on ANY level makes the row "
       "NOT A RESULT before any triple is consulted")
    r = grade_row("G1a", dict(value=10.0, uncertainty=1.0),
                  dict(c=1.0, m=2.0, f=4.0), st, 1.6, 1.59)
    ok(r["verdict"] == VERDICT_NAR and r["triple"] == "DIVERGENT",
       "rule 5 step (2): a DIVERGENT triple is NOT A RESULT whatever the value")

    # --- the carry-over assertion, driven against the real frozen file ----
    if os.path.isfile(FROZEN_T5B):
        names = assert_thresholds_carried_over()
        ok(len(names) >= 20,
           "THRESHOLD CARRY-OVER: %d names re-parsed from the frozen "
           "analyse_t5b.py and ALL identical to this file's. T5c section 5's "
           "byte-identical claim is a check, not prose." % len(names))
        src = open(FROZEN_T5B, errors="replace").read()
        for lit in ("YPLUS_MAX = 5.0", "YPLUS_TARGET_TOL = 2.0"):
            ok(lit in src, "the frozen predecessor still carries the literal "
                           "`%s`" % lit)
    else:
        ok(False, "the frozen analyse_t5b.py is absent; the carry-over "
                  "assertion could not be driven")

    # --- no bare assert gates anything (python3 -O strips them) ------------
    me = open(os.path.abspath(__file__), errors="replace").read()
    bare = [ln for ln in me.splitlines()
            if re.match(r"^\s*assert\b", ln)]
    ok(not bare,
       "no control or gate in this file is a bare `assert`: %d found. "
       "`python3 -O` strips asserts and a control that vanishes under an "
       "interpreter flag is not a control." % len(bare))
    ok(sys.flags.optimize == 0,
       "selftest is NOT running under python3 -O (optimize flag %d)"
       % sys.flags.optimize)

    print("\nSELFTEST: %d failure(s)" % len(fails))
    return 0 if not fails else 2


def main(argv):
    root = DEFAULT_ROOT
    if "--selftest" in argv:
        return selftest()
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    if not os.path.isdir(root):
        refuse("no root directory %s" % root)
    return run(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
