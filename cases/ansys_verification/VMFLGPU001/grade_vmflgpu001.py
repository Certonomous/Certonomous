#!/usr/bin/env python3
"""VMFLGPU001 comparator -- THE LAB'S GPU SOLVER PATH, exercised on flow between
rotating and stationary concentric cylinders (Ansys Fluid Dynamics Verification
Manual, Release 2026 R1, p. 225).

WHAT IS UNDER VERIFICATION.  Not the physics -- the physics is the KNOWN CONTROL,
already graded on the CPU as VMFL001-R2 (PASS).  The object is the lab's GPU
solver path: OpenFOAM v2606 + petsc4Foam + PETSc-CUDA on the L4 (sm_89).  The
gate therefore has THREE LIMBS and a miss on limb A is NOT A RESULT whatever the
physics says (DRAFT_PREREGISTRATIONS_VMFLGPU.md, "THE GPU-SOLVER-PATH GATE").

    limb A  GPU EXECUTION      three tells + the forced-CPU control
    limb B  GPU == CPU         |q_GPU - q_CPU| / |q_CPU| <= TOL_B
    limb C  PHYSICS            |q_GPU - q_exact| / |q_exact| <= TOL_C, where
                               q_exact is the CLOSED-FORM annular-Couette
                               solution THIS FILE EVALUATES ITSELF from the
                               manual's geometry and omega (v_exact below).
                               The manual's printed 2-s.f. "Target" column and
                               its "Ansys Fluent GPU" column are CONTEXT ONLY
                               and are printed beside the verdict, never gated on.

THIS FILE IS THE GRADING PATH.  It is committed with the pre-registration that
cites it, before any solver runs (CLAUDE.md rule 2; VERIFICATION_CHARTER 2d).
It REFUSES (exit 2) rather than degrades, and every refusal names its clause.

=============================================================================
FIELD CLASSES (L-342, Sanaa's universal rule of 2026-08-26T16:15Z, verbatim:
"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts
-- and graders must separate physics-critical fields from infrastructure fields
so a dead poller can never void a run again").

PHYSICS-CRITICAL -- a gate may read these, and a failure here refuses or votes
NOT A RESULT:
  * the solver rc, from RUN_RC.txt WHEN PRESENT.  When RUN_RC.txt is ABSENT the
    rc is NOT MEASURED: the verdict becomes NOT A RESULT and the physics is
    PRINTED -- it is not a voiding refusal.        (strict_completion, "rc")
  * the End line in log.simpleFoam                (strict_completion)
  * last time == the level's registered endTime   (strict_completion)
  * the declared fields present at endTime        (strict_completion)
  * ExecutionTime line count == endTime           (strict_completion)
  * the age guard on the case's own 0/U           (strict_completion)
  * the residual clause and the plateau clause    (iterative_convergence)
  * the mesh birth certificate                    (mesh_birth_certificate)
  * the launch-time sha freeze                    (freeze_record)
  * THE THREE GPU TELLS AND THE FORCED-CPU CONTROL (limb_A).  For THIS FAMILY
    limb A is physics-critical because it IS the object under verification: a
    CPU number that happens to match the reference verifies nothing about the
    GPU path.

INFRASTRUCTURE -- NEVER refused on, NEVER voids a verdict; absent or malformed
is a labelled WARNING and the grade proceeds on the physics artifacts:
  * COST.txt and every GPU-hour / core-minute figure   (cost_record)
  * LAUNCH_RECORD.txt's non-sha bookkeeping lines      (freeze_record)
  * CAP_OVERRUN.txt, contention and status files
  * memory figures, pids, sids, bookkeeping mtimes
=============================================================================

INSTRUMENT RULES OBSERVED HERE, each paid for by a measured failure:
  * NO `assert` carries a refusal, guard, control or gate (PREREG_TEMPLATE
    Amendment 6; L-332).  `python3 -O` deletes every assert.  The verdict
    vocabulary guard is an explicit refusal, V0.  `--selftest` parses this
    file's own AST and refuses on a single Assert node, and the AST counter is
    shown able to count a planted one.
  * NO UNCONDITIONAL SUCCESS PRINT (Amendment 6a item 1).  Every green line is
    emitted from inside the branch that verified it.
  * EVERY CONTROL FUNCTION FALLS THROUGH TO refuse() (Amendment 6a item 2), so
    the only way to return is to have passed.
  * REFUSALS FIRE UNDER `python3 -O` -- `--drive-refusal` drives one, and
    `--selftest` runs it under `-O` and requires exit 2.
  * P_MIN = 0.05 and RATIO-FIRST classification (FINDING_p_floor.md section 4):
    R = e21/e32 within STAG_TOL of 1 is STAGNANT *before* any p is computed, and
    an observed order below P_MIN is NOT A RESULT with NO GCI PRINTED.  The
    selftest DRIVES the degenerate equally-spaced triple (1.0, 1.1, 1.2).
  * PLATEAU: a FIXED window (not a fraction), a minimum-sample refusal, a
    peak-to-peak statistic that rejects a growing series, a null-range refusal,
    and the realised sample count recorded (Amendment 4 items 1-5).
  * Readers are anchored on the QUANTITY NAME, parse the producer's format
    tolerantly, fail safe (rc defaults to the refusing value), and resolve a
    field as `X` or `X.gz` (Amendment 5 items 2-4).

    python3 grade_vmflgpu001.py --run-root <root>
    python3 grade_vmflgpu001.py --selftest
    python3 grade_vmflgpu001.py --drive-refusal <kind>    # used by --selftest
    python3 grade_vmflgpu001.py --drive-verdict <kind>    # used by --selftest
"""

import argparse
import ast
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# THE FROZEN GRADING PATH -- bands, references, row definitions, verdict rules
# ---------------------------------------------------------------------------
CASE = "VMFLGPU001"
MANUAL_PAGE = "225"
CPU_PARENT = "VMFL001 / VMFL001-R2"

OMEGA = 1.0                 # rad/s, inner cylinder                (manual p.225)
R_I = 0.0178                # m, inner radius                      (manual p.225)
R_O = 0.04628               # m, outer radius                      (manual p.225)
RHO = 1.0                   # kg/m3                                (manual p.225)
MU = 2.0e-4                 # kg/m-s                               (manual p.225)
NU = MU / RHO               # m2/s -- what simpleFoam is given

RADII = (0.020, 0.025, 0.030, 0.035)                      # m, manual Table .gpu001.1
# CONTEXT ONLY, never the gate.  The manual's PRINTED "Target" column is the
# closed form ROUNDED TO 2 s.f.; this comparator gates against the closed form
# it EVALUATES ITSELF (v_exact below), so the printed column is carried as
# context and as a printed diagnostic, never as the reference.
MANUAL_PRINTED_TARGET = {0.020: 0.0151, 0.025: 0.0105,
                         0.030: 0.0072, 0.035: 0.0046}    # m/s, column "Target"
# CONTEXT ONLY, never the gate (charter section 5.1): manual Table .gpu001.1,
# column "Ansys Fluent GPU".
ANSYS_FLUENT_GPU = {0.020: 0.0152, 0.025: 0.0105,
                    0.030: 0.0072, 0.035: 0.0045}

TOL_C = 0.02        # limb C, the physics band, AGAINST THE LAB-EVALUATED CLOSED
                    # FORM (not against the manual's rounded printed column).
                    # Justification in PREREGISTRATION.md section 6.3: the
                    # manual's own stated goal is 3%, tightened here to 2%; and
                    # because the reference is evaluated exactly rather than read
                    # off a 2-s.f. table, the 1.148% rounding term that the CPU
                    # parent had to absorb at r = 35 mm is NOT in this budget --
                    # so 2% here is STRICTLY TIGHTER than the parent's 2%.
                    # Frozen before any run.
TOL_B = 1e-4        # limb B, GPU == CPU.  Derivation in PREREGISTRATION.md 6.2.
TOL_PRINTED = 0.02  # DIAGNOSTIC against the manual's PRINTED column. NOT the gate.

LEVELS = ("L1_16x64", "L2_32x128", "L3_64x256")
ENDTIME_BY_LEVEL = {"L1_16x64": 3000, "L2_32x128": 3000, "L3_64x256": 6000}
CELLS_BY_LEVEL = {"L1_16x64": 1024, "L2_32x128": 4096, "L3_64x256": 16384}
ARMS = ("gpu", "cpu")
GPU_ARM, CPU_ARM = "gpu", "cpu"

TRIPLE_RADIUS = 0.035       # the manual's worst-agreement point
RATIO = 2.0                 # r = 2 exactly, both directions
FS = 1.25                   # Roache factor of safety
EPS_ABS = 1e-12             # m/s, the "no difference at all" floor
STAG_TOL = 1e-3             # |R - 1| within this is STAGNANT, decided on R FIRST
P_MIN = 0.05                # FINDING_p_floor.md section 4

RES_TOL = 1e-6              # final initial residual, Ux/Uy/p
PLATEAU_WINDOW = 600        # FIXED sample count (Amendment 4 item 1: prefer fixed)
PLATEAU_MIN = 600           # refusal below this -> CANNOT_TELL, never a pass
PLATEAU_TOL = 1e-6          # m/s, peak-to-peak over the window

PLANT = 1.234e-3            # m/s, planted-zero perturbation
PLANT_TOL = 1e-15           # m/s, read-back tolerance

SET_NAME = "gateAxis"
PROBE_FO = "gateProbes"
FIELDS_AT_ENDTIME = ("U", "p")

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
# The reference is CLOSED-FORM/EXACT (White, Viscous Fluid Flow section 3-2.3):
# it buys V, never P, so the tier ceiling is GATE REACHED (PREREG_TEMPLATE
# Amendment 1).  This constant is the ceiling, not the verdict.
TIER_CEILING = "GATE REACHED"

TIME_RE = re.compile(r"^[0-9]+([.][0-9]*)?([eE][+-]?[0-9]+)?$")
KV_RE = re.compile(r"(\w+)\s*=\s*(.*)")     # Amendment 5 item 2: tolerant parse


# ---------------------------------------------------------------------------
# refusal / warning primitives
# ---------------------------------------------------------------------------
def refuse(code, msg):
    """Exit 2.  Never an assert: `python3 -O` would delete an assert (L-332)."""
    sys.stderr.write("REFUSE (%s %s): %s\n" % (CASE, code, msg))
    sys.exit(2)


def warn_infra(msg):
    """An INFRASTRUCTURE field is absent or malformed.  This NEVER refuses and
    NEVER changes a verdict (L-342)."""
    print("  WARNING(INFRASTRUCTURE): %s" % msg)
    return None


def checked_verdict(verdict):
    """CLAUDE.md rule 1's vocabulary guard, as an explicit refusal so it
    survives `python3 -O` (PREREG_TEMPLATE Amendment 6 item 2)."""
    if verdict in VERDICTS:
        return verdict
    refuse("V0", "verdict %r is not in the fixed vocabulary %s" % (verdict, list(VERDICTS)))
    refuse("V0-FALLTHROUGH", "unreachable: the vocabulary guard did not exit")


# ---------------------------------------------------------------------------
# the reference: exact analytical solution, White section 3-2.3
# ---------------------------------------------------------------------------
def v_exact(r):
    """v_theta(r) = omega R_i^2 (R_o^2 - r^2) / (r (R_o^2 - R_i^2))."""
    return OMEGA * R_I ** 2 * (R_O ** 2 - r ** 2) / (r * (R_O ** 2 - R_I ** 2))


def torque_exact_per_length():
    """M' = 4 pi mu omega R_i^2 R_o^2 / (R_o^2 - R_i^2).  DIAGNOSTIC ONLY: unlike
    v_theta it does depend on mu, which is the one thing the velocity gate
    provably cannot see."""
    return 4.0 * math.pi * MU * OMEGA * R_I ** 2 * R_O ** 2 / (R_O ** 2 - R_I ** 2)


# ---------------------------------------------------------------------------
# readers.  v2606's `sets`/raw writer emits HEADERLESS files named
# <setName>_<fields alphabetical>.xy; the column layout is DERIVED FROM THE
# FILENAME and never guessed (the VMFL001 run-1 refusal, L-286).
# ---------------------------------------------------------------------------
def _resolve(path):
    """Amendment 5 item 4: a field is `X` or `X.gz`."""
    if os.path.isfile(path):
        return path
    if os.path.isfile(path + ".gz"):
        return path + ".gz"
    return None


def _layout_from_filename(fname, set_name):
    base = os.path.basename(fname)
    stem = base.split(".")[0]
    if not stem.startswith(set_name + "_"):
        refuse("R1", "sampled file %r does not begin with the set name %r" % (base, set_name))
    fields = stem[len(set_name) + 1:].split("_")
    if sorted(fields) != ["U", "p"]:
        refuse("R2", "sampled file %r field list %r is not exactly {p, U}; this "
                     "comparator does not guess a column" % (base, fields))
    cols = ["x", "y", "z"]
    for f in fields:
        if f == "p":
            cols.append("p")
        elif f == "U":
            cols += ["U_x", "U_y", "U_z"]
        else:
            refuse("R3", "unknown field %r in %r" % (f, base))
    return cols


def find_set_file(level_dir, set_name, time=None):
    t = str(ENDTIME_BY_LEVEL[os.path.basename(level_dir)]) if time is None else str(time)
    pat = os.path.join(level_dir, "postProcessing", "*", t, set_name + "_*.xy")
    hits = sorted(glob.glob(pat))
    if len(hits) > 1:
        refuse("R4", "ambiguous sampled files for set %r at time %s in %s: %s"
               % (set_name, t, level_dir, hits))
    if not hits:
        refuse("R5", "no sampled file for set %r at time %s under %s/postProcessing"
               % (set_name, t, level_dir))
    return hits[0], _layout_from_filename(hits[0], set_name)


def read_raw_set(path, cols):
    if not os.path.isfile(path):
        refuse("R6", "sampled file does not exist: " + path)
    rows = []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#") or s[0].isalpha():
                continue
            try:
                rows.append([float(p) for p in s.split()])
            except ValueError:
                refuse("R7", "unparseable data row in %s: %r" % (path, s))
    if not rows:
        refuse("R8", "no data rows in " + path)
    for r in rows:
        if len(r) != len(cols):
            refuse("R9", "layout has %d columns but a data row has %d in %s"
                   % (len(cols), len(r), path))
    return rows


def vtheta_from_raw(path, cols):
    """v_theta = -U_x sin(theta) + U_y cos(theta); on the +x axis this is U_y."""
    rows = read_raw_set(path, cols)
    ix, iy = cols.index("x"), cols.index("y")
    iux, iuy = cols.index("U_x"), cols.index("U_y")
    out = []
    for row in rows:
        x, y, ux, uy = row[ix], row[iy], row[iux], row[iuy]
        out.append((math.hypot(x, y), math.atan2(y, x),
                    -ux * math.sin(math.atan2(y, x)) + uy * math.cos(math.atan2(y, x))))
    return out


def gate_values(level_dir):
    """The four gate radii, ANCHORED ON THE RADIUS, never on row order."""
    path, cols = find_set_file(level_dir, SET_NAME)
    got = vtheta_from_raw(path, cols)
    out = {}
    for r in RADII:
        hits = [v for (rr, th, v) in got if abs(rr - r) < 1e-6]
        if len(hits) != 1:
            refuse("R10", "expected exactly one sampled point at r = %.4f m in %s, found %d"
                   % (r, level_dir, len(hits)))
        out[r] = hits[0]
    return out, path, cols


# ---------------------------------------------------------------------------
# planted-zero control (CLAUDE.md rule 3)
# ---------------------------------------------------------------------------
def plant_into_raw(path, r_target, plant, cols):
    ix, iy, j = cols.index("x"), cols.index("y"), cols.index("U_y")
    lines = open(path).read().splitlines()
    hit = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#") or s[0].isalpha():
            continue
        parts = s.split()
        if len(parts) != len(cols):
            continue
        if abs(math.hypot(float(parts[ix]), float(parts[iy])) - r_target) < 1e-6:
            parts[j] = repr(float(parts[j]) + plant)
            lines[i] = "\t".join(parts)
            hit = i
            break
    if hit is None:
        refuse("P1", "no row at r = %.4f m to plant into: %s" % (r_target, path))
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return hit


def planted_zero_control(level_dir, reader=None):
    """CLAUDE.md rule 3, SIZED PER CHANNEL (L-340).

    THE GATE HAS FOUR CHANNELS -- v_theta at r = 20, 25, 30 and 35 mm -- and
    EVERY ONE OF THEM IS A POINT READER: one sampled row in, one number out, so
    the plant-to-read mapping is 1:1 and a plant of PLANT moves the read by
    exactly PLANT.  L-340 cost this team a completed 3-level run because a
    single-point plant was pointed at an AVERAGING channel (an RMS over 401
    points), where the same plant is diluted by ~1/sqrt(N) and a WORKING reader
    is refused.  There is no averaged channel here, and the sizing is checked
    rather than assumed: PLANT = 1.234e-3 m/s against the SMALLEST gated value
    (v_exact(35 mm) = 4.5478e-3 m/s) is 27% of it -- three orders above the
    PLANT_TOL read-back tolerance.

    So the control is run ONCE PER CHANNEL: plant into a COPY on disk at r,
    read it back, require the reader to see exactly PLANT at r and NOTHING at
    the other three.  A channel whose reader cannot see the plant refuses.
    The run tree is never modified.

    Falls through to refuse() on every path that is not a pass (Amendment 6a
    item 2): the ONLY way this function returns is with the plant seen on ALL
    FOUR channels.

    `reader` exists so the selftest can drive this control's REFUSAL PATH with a
    deliberately BLIND reader -- one that returns the pre-plant values whatever
    is on disk.  Without that, removing the refusal below is invisible to the
    selftest, which is exactly the Amendment 6a defect: a control whose failing
    branch nothing drives."""
    reader = reader or vtheta_from_raw
    src, cols = find_set_file(level_dir, SET_NAME)
    before = {r: v for r, v in gate_values(level_dir)[0].items()}
    smallest = min(abs(before[r]) for r in RADII)
    per_channel = {}
    for r_plant in RADII:
        tmp = tempfile.mkdtemp(prefix="vmflgpu001plant_")
        try:
            work = os.path.join(tmp, os.path.basename(src))
            shutil.copyfile(src, work)
            plant_into_raw(work, r_plant, PLANT, cols)
            got = reader(work, cols)
            after = {}
            for r in RADII:
                hits = [v for (rr, th, v) in got if abs(rr - r) < 1e-6]
                if len(hits) != 1:
                    refuse("P2", "planted copy lost the row at r = %.4f m" % r)
                after[r] = hits[0]
            seen = after[r_plant] - before[r_plant]
            if abs(seen - PLANT) > PLANT_TOL:
                refuse("P3", "CHANNEL r = %.3f m: the reader cannot see a %g m/s "
                             "difference planted on disk (saw %g). Its numbers mean "
                             "nothing." % (r_plant, PLANT, seen))
            for r in RADII:
                if r != r_plant and abs(after[r] - before[r]) > PLANT_TOL:
                    refuse("P4", "planting at r = %.3f m moved r = %.3f m by %g -- the "
                                 "reader is not reading the row it thinks it is"
                           % (r_plant, r, after[r] - before[r]))
            per_channel["%.3f" % r_plant] = seen
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if len(per_channel) != len(RADII):
        refuse("P5", "the planted-zero control did not complete every gate channel: "
                     "%d of %d" % (len(per_channel), len(RADII)))
    # Reached, and this structure returned, ONLY when every channel saw its plant.
    return dict(planted=PLANT, per_channel=per_channel, channels=len(per_channel),
                plant_over_smallest_gated_value=PLANT / smallest,
                reader_kind="point reader at each radius (L-340: 1:1 plant->read)",
                passed=True)
    refuse("P6-FALLTHROUGH", "planted-zero control did not reach a verdict")


# ---------------------------------------------------------------------------
# strict completion (CLAUDE.md rule 4).  PHYSICS-CRITICAL.
# ---------------------------------------------------------------------------
def _read_kv(path):
    """Tolerant `key = value` / `key=value` parse; unreadable -> {} (Amendment 5
    item 2).  Callers default to the REFUSING value."""
    out = {}
    try:
        for line in open(path, errors="replace"):
            m = KV_RE.match(line.strip())
            if m:
                out[m.group(1)] = m.group(2).strip()
    except OSError:
        return {}
    return out


def _time_dirs(level_dir):
    try:
        names = os.listdir(level_dir)
    except OSError:
        return []
    out = [n for n in names
           if os.path.isdir(os.path.join(level_dir, n)) and TIME_RE.match(n) and float(n) > 0]
    return sorted(out, key=float)


def strict_completion(level_dir):
    """Returns a dict.  `rc_status` is one of 'MEASURED' or 'NOT MEASURED'.

    L-342: a MISSING RUN_RC.txt does NOT void the run.  rc is reported NOT
    MEASURED, the physics is still read and printed, and the caller votes
    NOT A RESULT.  A PRESENT and NON-ZERO rc is an incomplete run and refuses."""
    name = os.path.basename(level_dir)
    endtime = ENDTIME_BY_LEVEL[name]
    if not os.path.isdir(level_dir):
        refuse("C0", "%s: run directory does not exist" % level_dir)

    # The launcher writes the rc TWICE, from inside itself, with the run root's
    # copy carrying the level and the arm in its NAME (RUN_RC.<level>.<arm>) so
    # that a record cannot be attributed to the wrong arm by being moved.  The
    # canonical reader is the run-root copy; the per-level copy is the fallback.
    # Both are written by the same statement in run_vmflgpu001.sh, so they cannot
    # disagree; reading either is reading the rc the script captured from `$?`.
    arm_name = os.path.basename(os.path.dirname(level_dir))
    run_root_here = os.path.dirname(os.path.dirname(level_dir))
    rc_candidates = [os.path.join(run_root_here, "RUN_RC.%s.%s" % (name, arm_name)),
                     os.path.join(level_dir, "RUN_RC.txt")]
    rc_path = next((p for p in rc_candidates if os.path.isfile(p)), rc_candidates[0])
    rc_status, rc = "MEASURED", None
    if not os.path.isfile(rc_path):
        rc_status = "NOT MEASURED"
        warn_infra("%s: neither RUN_RC.%s.%s at the run root nor RUN_RC.txt beside "
                   "the level is present. rc is PHYSICS-CRITICAL, so this "
                   "level cannot be a PASS -- but a missing bookkeeping file "
                   "does not VOID the physics artifacts (L-342). The physics "
                   "below is read and printed; the verdict is NOT A RESULT."
                   % (name, name, arm_name))
    else:
        rcd = _read_kv(rc_path)
        raw = rcd.get("rc", "1")          # FAIL-SAFE default: refusing value
        try:
            rc = int(raw)
        except ValueError:
            refuse("C1", "%s: RUN_RC.txt carries an unparseable rc %r" % (name, raw))
        if rc != 0:
            refuse("C2", "%s: solver rc = %d (strict completion clause 1). A "
                         "non-zero rc is a FINDING, not a retry." % (name, rc))

    logp = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.isfile(logp):
        refuse("C3", "%s: no log.simpleFoam" % name)
    text = open(logp, errors="replace").read()
    if not re.search(r"^End\b", text, re.M):
        refuse("C4", "%s: no 'End' line in log.simpleFoam (clause 2)" % name)

    times = _time_dirs(level_dir)
    if not times or float(times[-1]) != float(endtime):
        refuse("C5", "%s: last time is %r, the registered endTime is %d (clause 3)"
               % (name, times[-1] if times else None, endtime))

    for f in FIELDS_AT_ENDTIME:
        if _resolve(os.path.join(level_dir, times[-1], f)) is None:
            refuse("C6", "%s: field %s missing at endTime (clause 4) -- neither %s nor %s.gz"
                   % (name, f, f, f))

    n_exec = len(re.findall(r"^ExecutionTime", text, re.M))
    if n_exec != endtime:
        refuse("C7", "%s: %d ExecutionTime lines, the registered endTime is %d (clause 5)"
               % (name, n_exec, endtime))

    marker = _resolve(os.path.join(level_dir, "0", "U"))
    if marker is None:
        refuse("C8", "%s: no 0/U age-guard marker (clause 6)" % name)
    m_mtime = os.path.getmtime(marker)
    for f in FIELDS_AT_ENDTIME:
        fp = _resolve(os.path.join(level_dir, times[-1], f))
        if os.path.getmtime(fp) <= m_mtime:
            refuse("C9", "%s: %s/%s is NOT newer than 0/U -- AGE GUARD (clause 6). "
                         "The field did not come from this run." % (name, times[-1], f))
    return dict(level=name, arm=arm_name, rc=rc, rc_status=rc_status,
                rc_source=(rc_path if rc_status == "MEASURED" else None),
                endtime=endtime, latest_time=times[-1], execution_lines=n_exec,
                completed=True)


def mesh_birth_certificate(level_dir):
    """PHYSICS-CRITICAL: a mesh is born clean or it does not enter
    (VERIFICATION_CHARTER section 9, MESH_STANDARD section 6)."""
    name = os.path.basename(level_dir)
    cm = os.path.join(level_dir, "log.checkMesh")
    if not os.path.isfile(cm):
        refuse("M1", "%s: no log.checkMesh -- no mesh birth certificate" % name)
    text = open(cm, errors="replace").read()
    if not re.search(r"^Mesh OK", text, re.M):
        refuse("M2", "%s: checkMesh did not report 'Mesh OK'" % name)
    m = re.search(r"cells:\s*(\d+)", text)
    if not m:
        refuse("M3", "%s: checkMesh log carries no cell count" % name)
    cells = int(m.group(1))
    if cells != CELLS_BY_LEVEL[name]:
        refuse("M4", "%s: %d cells, the pre-registration registers %d"
               % (name, cells, CELLS_BY_LEVEL[name]))
    return dict(level=name, cells=cells, mesh_ok=True)


# ---------------------------------------------------------------------------
# iterative convergence: residuals AND a FIXED-WINDOW plateau (Amendment 4)
# ---------------------------------------------------------------------------
RES_RE = re.compile(r"Solving for (\w+),\s+Initial residual = ([0-9eE.+-]+)")
VEC_RE = re.compile(r"\(([-0-9eE.+]+)\s+([-0-9eE.+]+)\s+([-0-9eE.+]+)\)")


def residual_history(level_dir):
    text = open(os.path.join(level_dir, "log.simpleFoam"), errors="replace").read()
    hist = {}
    for fld, val in RES_RE.findall(text):
        try:
            hist.setdefault(fld, []).append(float(val))
        except ValueError:
            continue
    return hist


def probe_series(level_dir):
    """Per-iteration v_theta at TRIPLE_RADIUS from the `probes` function object.
    CELL values -- the plateau leg ONLY, never the graded number."""
    hits = sorted(glob.glob(os.path.join(level_dir, "postProcessing", PROBE_FO, "*", "U")))
    if not hits:
        refuse("I1", "%s: no %r probe series under postProcessing"
               % (os.path.basename(level_dir), PROBE_FO))
    vals = []
    for h in hits:
        for line in open(h, errors="replace"):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            vs = VEC_RE.findall(s)
            if len(vs) != len(RADII):
                continue
            vals.append(float(vs[-1][1]))   # last probe = TRIPLE_RADIUS, +x axis, v_theta == U_y
    return vals


def iterative_convergence(level_dir):
    name = os.path.basename(level_dir)
    hist = residual_history(level_dir)
    finals = {}
    for fld in ("Ux", "Uy", "p"):
        if fld not in hist or not hist[fld]:
            refuse("I2", "%s: no residual history for %s" % (name, fld))
        finals[fld] = hist[fld][-1]
    bad = {k: v for k, v in finals.items() if not v < RES_TOL}
    if bad:
        refuse("I3", "%s: final initial residual(s) %s are not below %g -- the level "
                     "is not iteratively converged (rule 5 step 1)" % (name, bad, RES_TOL))

    vals = probe_series(level_dir)
    n_avail = len(vals)
    if n_avail < PLATEAU_MIN:
        refuse("I4", "%s: %d plateau samples < the registered minimum %d -- "
                     "CANNOT_TELL, never a pass (Amendment 4 item 2)" % (name, n_avail, PLATEAU_MIN))
    window = vals[-PLATEAU_WINDOW:]
    ptp = max(window) - min(window)
    if ptp == 0.0:
        refuse("I5", "%s: the plateau window has NULL RANGE (peak-to-peak exactly 0 "
                     "over %d samples). A dead field and a perfectly converged one "
                     "look identical to a tolerance (Amendment 4 item 4)."
               % (name, PLATEAU_WINDOW))
    if not ptp < PLATEAU_TOL:
        refuse("I6", "%s: plateau peak-to-peak %g m/s over the last %d samples is not "
                     "below %g -- not plateaued (rule 5 step 1)"
               % (name, ptp, PLATEAU_WINDOW, PLATEAU_TOL))
    return dict(level=name, final_residuals=finals, residual_tol=RES_TOL,
                plateau_ptp=ptp, plateau_tol=PLATEAU_TOL,
                plateau_window=PLATEAU_WINDOW, n_window=PLATEAU_WINDOW,
                n_available=n_avail, converged=True)


# ---------------------------------------------------------------------------
# LIMB A -- GPU EXECUTION.  PHYSICS-CRITICAL for this family.
#
# The three tells are the smoke test's tells, deliberately kept BYTE-FOR-BYTE
# equivalent so this comparator and smoke_test_gpu_path.sh cannot disagree
# about what a tell is.  TELL 1 IS LOOSE AND CANNOT DISCRIMINATE ON ITS OWN --
# PETSc's -log_view prints GPU columns and CpuToGpu/GpuToCpu rows on a
# CUDA-configured build EVEN WHEN THE SOLVE RAN ON THE CPU (PREREG_TEMPLATE
# Amendment 5, "THE SAME REQUIREMENT ON THE GPU RECIPE").  THE FORCED-CPU
# CONTROL IS THE DISCRIMINATOR, and a run graded without it is NOT A RESULT.
# ---------------------------------------------------------------------------
def tell1_gpu_flops(solver_log_text):
    return bool(re.search(r"GPU[^\n]*?[1-9][0-9]*", solver_log_text, re.I)
                and re.search(r"CpuToGpu|GpuToCpu", solver_log_text, re.I))


def tell2_pid_on_gpu(gpusample_text):
    return bool(re.search(r"\b[0-9]+,\s*[1-9][0-9]*\s*MiB", gpusample_text))


def tell3_cuda_type(solver_log_text):
    return bool(re.search(r"type:\s*(seqaijcusparse|mpiaijcusparse|aijcusparse)",
                          solver_log_text, re.I))


def _arm_artifacts(run_root, arm, level):
    d = os.path.join(run_root, arm, level)
    logp = os.path.join(d, "log.simpleFoam")
    smp = os.path.join(d, "gpusample.txt")
    if not os.path.isfile(logp):
        refuse("A0", "%s/%s: no log.simpleFoam -- limb A cannot be evaluated and "
                     "limb A is PHYSICS-CRITICAL for this family" % (arm, level))
    text = open(logp, errors="replace").read()
    if not os.path.isfile(smp):
        refuse("A1", "%s/%s: no gpusample.txt -- TELL 2 (the solver PID holding "
                     "device memory) cannot be evaluated. This is a PHYSICS-CRITICAL "
                     "artifact for this family, not bookkeeping: it is one of the "
                     "three tells that constitute the object under verification."
               % (arm, level))
    return text, open(smp, errors="replace").read()


def limb_A(run_root, level):
    """Returns a dict ONLY when limb A holds.  Otherwise it exits 2 -- either as
    a refusal (the control is broken: the row certifies NOTHING) or with the
    verdict NOT A RESULT printed (the solve did not run on the GPU).  It NEVER
    returns a passing structure it did not verify (Amendment 6a item 2)."""
    gtext, gsamp = _arm_artifacts(run_root, GPU_ARM, level)
    ctext, _csamp = _arm_artifacts(run_root, CPU_ARM, level)

    g1, g2, g3 = tell1_gpu_flops(gtext), tell2_pid_on_gpu(gsamp), tell3_cuda_type(gtext)
    c1, c3 = tell1_gpu_flops(ctext), tell3_cuda_type(ctext)

    # The control first: if it reports GPU work, the tells cannot tell GPU from
    # CPU and NOTHING downstream means anything.
    if c1 or c3:
        refuse("A2", "%s: the FORCED-CPU CONTROL (mat_type aij, vec_type standard) "
                     "REPORTED GPU WORK (tell1=%s tell3=%s). The tells cannot "
                     "discriminate GPU from CPU on this build, so this row certifies "
                     "NOTHING. It is NOT A RESULT and it is never a PASS."
               % (level, c1, c3))

    if not (g1 and g2 and g3):
        print("  LIMB A FAILED at %s: flops=%s pid_on_gpu=%s cuda_type=%s"
              % (level, g1, g2, g3))
        print("  The linear solve did NOT provably run on the GPU. A CPU number that "
              "happens to match the reference verifies nothing about the GPU path.")
        print("VERDICT: %s" % checked_verdict("NOT A RESULT"))
        sys.exit(2)

    # Reached only when all three tells fired AND the control discriminated.
    return dict(level=level, tell1_gpu_flops=True, tell2_pid_on_gpu=True,
                tell3_cuda_type=True, forced_cpu_control_discriminated=True)


# ---------------------------------------------------------------------------
# Roache triple.  RATIO FIRST, then the order; P_MIN floors it.
# ---------------------------------------------------------------------------
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine, d21=d21, d32=d32,
               ratio=ratio, fs=fs, R=None, p=None, gci_fine=None, f_extrapolated=None)
    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"
        return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"
        out["why"] = "coarse-medium difference below %g while medium-fine is not" % EPS_ABS
        return out
    R = d21 / d32
    out["R"] = R
    # RATIO FIRST (FINDING_p_floor.md section 4): a stagnant triple is caught
    # BEFORE ln(R)/ln(r) can turn a floating-point crumb into a valid-looking
    # near-zero observed order.
    if abs(R - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"
        return out
    if R < 0:
        out["state"] = "OSCILLATORY"
        return out
    if R > 1.0:
        out["state"] = "DIVERGENT"
        return out
    p = math.log(1.0 / R) / math.log(ratio)
    out["p"] = p
    if p < P_MIN:
        out["state"] = "BELOW_P_MIN"
        out["why"] = ("observed order %g is below the registered floor P_MIN = %g; "
                      "NO GCI IS PRINTED -- a GCI computed from a near-zero order is "
                      "a number with no meaning" % (p, P_MIN))
        return out
    out["state"] = "CONVERGING"
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"
        out["why"] = "r^p - 1 <= 0"
        out["p"] = p
        return out
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


# ---------------------------------------------------------------------------
# INFRASTRUCTURE readers -- these NEVER refuse (L-342)
# ---------------------------------------------------------------------------
def cost_record(run_root):
    p = os.path.join(run_root, "COST.txt")
    if not os.path.isfile(p):
        return warn_infra("COST.txt absent -- GPU-hours and core-minutes are NOT "
                          "MEASURED. Cost is an INFRASTRUCTURE field: the grade "
                          "proceeds on the physics artifacts (L-342).")
    kv = _read_kv(p)
    if not kv:
        return warn_infra("COST.txt is present but unparseable -- cost NOT MEASURED. "
                          "The grade proceeds (L-342).")
    return kv


def freeze_record(run_root):
    """The sha lines are PHYSICS-CRITICAL (they are the freeze).  The rest of
    LAUNCH_RECORD.txt is bookkeeping."""
    p = os.path.join(run_root, "LAUNCH_RECORD.txt")
    if not os.path.isfile(p):
        refuse("F1", "no LAUNCH_RECORD.txt at %s -- the launch-time freeze "
                     "verification (PREREG_TEMPLATE Amendment 2) left no record, so "
                     "there is no evidence the solver ran against the committed "
                     "pre-registration and comparator." % run_root)
    kv = _read_kv(p)
    for k in ("prereg_sha_head", "comparator_sha_head"):
        if not kv.get(k):
            refuse("F2", "LAUNCH_RECORD.txt carries no %s -- the freeze is unproven" % k)
    if kv.get("prereg_sha_head") != kv.get("prereg_sha_disk"):
        refuse("F3", "LAUNCH_RECORD.txt: the pre-registration on disk at launch "
                     "(%s) was NOT the blob at HEAD (%s)"
               % (kv.get("prereg_sha_disk"), kv.get("prereg_sha_head")))
    if kv.get("comparator_sha_head") != kv.get("comparator_sha_disk"):
        refuse("F4", "LAUNCH_RECORD.txt: the comparator on disk at launch (%s) was "
                     "NOT the blob at HEAD (%s)"
               % (kv.get("comparator_sha_disk"), kv.get("comparator_sha_head")))
    if not kv.get("host"):
        warn_infra("LAUNCH_RECORD.txt carries no host line -- bookkeeping only; "
                   "the freeze shas above are what the verdict rests on.")
    return kv


# ---------------------------------------------------------------------------
# the grade
# ---------------------------------------------------------------------------
def grade(run_root, out_json=None):
    print("%s -- GPU SOLVER PATH on the concentric-cylinder case (manual p.%s, "
          "CPU parent %s)" % (CASE, MANUAL_PAGE, CPU_PARENT))
    print("  tier ceiling %s (closed-form/exact reference buys V, NEVER P)" % TIER_CEILING)
    rec = dict(case=CASE, manual_page=MANUAL_PAGE, cpu_parent=CPU_PARENT,
               tier_ceiling=TIER_CEILING, tol_A="binary", tol_B=TOL_B, tol_C=TOL_C,
               levels={}, infrastructure={})

    fz = freeze_record(run_root)
    print("  FREEZE PROVEN AT LAUNCH: prereg %s ; comparator %s"
          % (fz["prereg_sha_head"], fz["comparator_sha_head"]))
    rec["freeze"] = {k: fz.get(k) for k in
                     ("prereg_sha_head", "comparator_sha_head", "head", "launched_utc")}
    rec["infrastructure"]["cost"] = cost_record(run_root)

    rc_not_measured = []
    gpu_gate, cpu_gate = {}, {}
    for lvl in LEVELS:
        lrec = {}
        for arm in ARMS:
            d = os.path.join(run_root, arm, lvl)
            mesh = mesh_birth_certificate(d)
            comp = strict_completion(d)
            conv = iterative_convergence(d)
            if comp["rc_status"] != "MEASURED":
                rc_not_measured.append("%s/%s" % (arm, lvl))
            vals, path, _cols = gate_values(d)
            lrec[arm] = dict(mesh=mesh, completion=comp, convergence=conv,
                             v_theta={("%.3f" % r): vals[r] for r in RADII},
                             sampled_file=path)
            if arm == GPU_ARM:
                gpu_gate[lvl] = vals
            else:
                cpu_gate[lvl] = vals
        lrec["limb_A"] = limb_A(run_root, lvl)
        print("  LIMB A HELD at %s: three tells fired on the GPU arm and the "
              "forced-CPU control showed GPU-ABSENT" % lvl)
        rec["levels"][lvl] = lrec

    plant = planted_zero_control(os.path.join(run_root, GPU_ARM, LEVELS[-1]))
    print("  PLANT SEEN ON ALL %d GATE CHANNELS (L-340, per-channel sizing): "
          "%g m/s planted at each radius moved that radius by %s m/s and no other"
          % (plant["channels"], plant["planted"],
             ["%.6g" % plant["per_channel"]["%.3f" % r] for r in RADII]))
    rec["planted_zero"] = plant

    # ---- limb B, at every level, at every radius --------------------------
    fine = LEVELS[-1]
    limb_b = {}
    b_worst, b_worst_where = 0.0, None
    for lvl in LEVELS:
        for r in RADII:
            g, c = gpu_gate[lvl][r], cpu_gate[lvl][r]
            if abs(c) <= 0.0:
                refuse("B1", "%s: the forced-CPU arm reports v_theta = 0 at r = %.3f m; "
                             "the limb-B ratio has no denominator" % (lvl, r))
            rel = abs(g - c) / abs(c)
            limb_b["%s@%.3f" % (lvl, r)] = rel
            if rel > b_worst:
                b_worst, b_worst_where = rel, "%s@r=%.3f m" % (lvl, r)
    rec["limb_B"] = dict(rel=limb_b, worst=b_worst, worst_at=b_worst_where, tol=TOL_B)
    limb_b_ok = b_worst <= TOL_B

    # ---- limb C, at the finest level, AGAINST THE LAB-EVALUATED CLOSED FORM -
    limb_c, diag = {}, {}
    c_worst, c_worst_where = 0.0, None
    for r in RADII:
        g = gpu_gate[fine][r]
        ex = v_exact(r)
        if abs(ex) <= 0.0:
            refuse("C-REF", "the closed form evaluates to zero at r = %.3f m; the "
                            "limb-C ratio has no denominator" % r)
        rel = abs(g - ex) / abs(ex)
        limb_c["%.3f" % r] = rel
        diag["%.3f" % r] = (abs(g - MANUAL_PRINTED_TARGET[r])
                            / abs(MANUAL_PRINTED_TARGET[r]))
        if rel > c_worst:
            c_worst, c_worst_where = rel, "r=%.3f m" % r
    rec["limb_C"] = dict(rel=limb_c, worst=c_worst, worst_at=c_worst_where, tol=TOL_C,
                         reference="closed form v_theta(r) = omega R_i^2 (R_o^2 - r^2)"
                                   " / (r (R_o^2 - R_i^2)), evaluated by this file",
                         v_exact={("%.3f" % r): v_exact(r) for r in RADII})
    rec["diagnostic_vs_manual_printed"] = dict(
        rel=diag, tol=TOL_PRINTED,
        target={("%.3f" % r): MANUAL_PRINTED_TARGET[r] for r in RADII},
        note="DIAGNOSTIC against the manual's 2-s.f. printed column, never the gate")
    rec["torque_exact_per_length_Nm_per_m"] = torque_exact_per_length()
    rec["ansys_fluent_gpu_context_only"] = {("%.3f" % r): ANSYS_FLUENT_GPU[r] for r in RADII}
    limb_c_ok = c_worst <= TOL_C

    # ---- Roache triple on the GPU arm -------------------------------------
    triple = [gpu_gate[l][TRIPLE_RADIUS] for l in LEVELS]
    rch = roache(triple[0], triple[1], triple[2])
    rec["roache"] = rch
    rec["triple_values"] = triple

    print("  v_theta(GPU, %s) at r=20/25/30/35 mm = %s"
          % (fine, ["%.6g" % gpu_gate[fine][r] for r in RADII]))
    print("  v_theta(CPU, %s) at r=20/25/30/35 mm = %s"
          % (fine, ["%.6g" % cpu_gate[fine][r] for r in RADII]))
    print("  limb B worst |GPU-CPU|/|CPU| = %.3g at %s (tol %g)"
          % (b_worst, b_worst_where, TOL_B))
    print("  v_exact (closed form, this file)  at r=20/25/30/35 mm = %s"
          % ["%.6g" % v_exact(r) for r in RADII])
    print("  manual printed target (CONTEXT)   at r=20/25/30/35 mm = %s"
          % ["%.6g" % MANUAL_PRINTED_TARGET[r] for r in RADII])
    print("  Ansys Fluent GPU      (CONTEXT)   at r=20/25/30/35 mm = %s"
          % ["%.6g" % ANSYS_FLUENT_GPU[r] for r in RADII])
    print("  limb C worst |GPU-exact|/|exact| = %.4g at %s (tol %g)"
          % (c_worst, c_worst_where, TOL_C))
    print("  diagnostic worst |GPU-printed|/|printed| = %.4g (NOT the gate)"
          % max(diag.values()))
    print("  triple v_theta(35 mm) = %s ; state=%s R=%s p=%s"
          % (["%.8g" % t for t in triple], rch["state"],
             None if rch["R"] is None else "%.6g" % rch["R"],
             None if rch["p"] is None else "%.6g" % rch["p"]))

    # ---- the verdict, in rule 5's order -----------------------------------
    if rc_not_measured:
        verdict = checked_verdict("NOT A RESULT")
        print("  rc is NOT MEASURED for %s -- a PHYSICS-CRITICAL field is absent, so "
              "this cannot be a PASS. The physics above is printed and stands as an "
              "artifact; the bookkeeping failure did not void it (L-342)."
              % ", ".join(rc_not_measured))
    elif rch["state"] != "CONVERGING":
        verdict = checked_verdict("NOT A RESULT")
        print("  the grid triple is %s -- rule 5 step 2. %s"
              % (rch["state"], rch.get("why", "")))
        print("  NO GCI IS QUOTED off a non-CONVERGING triple.")
    elif not limb_b_ok:
        verdict = checked_verdict("GATE FAIL")
        print("  LIMB B MISSED: the GPU arm does not equal the forced-CPU arm to the "
              "frozen tolerance. The GPU linear-algebra path is NOT verified.")
    elif not limb_c_ok:
        verdict = checked_verdict("GATE FAIL")
        print("  LIMB C MISSED: the physics band against the lab-evaluated closed form "
              "was not met. Limb B held, so the GPU path reproduced the lab's own CPU "
              "answer; the miss is against the analytical reference, not between the "
              "two arms.")
    else:
        verdict = checked_verdict(TIER_CEILING)
        print("  GCI_fine = %.4g %% at Fs = %g, observed order p = %.4f"
              % (100.0 * rch["gci_fine"], FS, rch["p"]))
    rec["verdict"] = verdict
    print("VERDICT: %s" % verdict)

    if out_json:
        try:
            with open(out_json, "w") as fh:
                json.dump(rec, fh, indent=2, sort_keys=True, default=str)
            print("  grading record written to %s" % out_json)
        except OSError as exc:
            warn_infra("could not write the grading JSON (%s) -- INFRASTRUCTURE; the "
                       "verdict above stands" % exc)
    return verdict


# ---------------------------------------------------------------------------
# fixtures + selftest
# ---------------------------------------------------------------------------
def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def _build_level(root, arm, level, *, gpu_tells=True, end_line=True, with_rc=True,
                 vfun=None, gpusample=True):
    """Construct a synthetic level directory good enough to drive the guards."""
    d = os.path.join(root, arm, level)
    et = ENDTIME_BY_LEVEL[level]
    _write(os.path.join(d, "log.checkMesh"),
           "Checking geometry...\n    cells: %d\nMesh OK.\n" % CELLS_BY_LEVEL[level])
    lines = []
    for i in range(1, et + 1):
        res = 1e-14 if i > 1 else 1e-2
        lines.append("Time = %d\nsmoothSolver:  Solving for Ux, Initial residual = %g, "
                     "Final residual = 1e-20, No Iterations 1\n"
                     "smoothSolver:  Solving for Uy, Initial residual = %g, "
                     "Final residual = 1e-20, No Iterations 1\n"
                     "GAMG:  Solving for p, Initial residual = %g, Final residual = "
                     "1e-20, No Iterations 1\nExecutionTime = %g s\n" % (i, res, res, res, i * 0.01))
    tail = ""
    if gpu_tells:
        tail += ("Mat Object: 1 MPI process\n  type: seqaijcusparse\n"
                 "KSPSolve             300 1.0 1.0e+00 1.0 1.0e+08 1.0 "
                 "GPU Mflop/s 1234 CpuToGpu Count 42 GpuToCpu Count 42\n")
    else:
        tail += ("Mat Object: 1 MPI process\n  type: seqaij\n"
                 "KSPSolve             300 1.0 1.0e+00 1.0 1.0e+08 1.0\n")
    if end_line:
        tail += "End\n"
    _write(os.path.join(d, "log.simpleFoam"), "".join(lines) + tail)
    if with_rc:
        rc_text = ("case_id = %s\narm = %s\nlevel = %s\nrc = 0\nwall_s = 10\nranks = 1\n"
                   "core_min = 0.1667\ngpu_h = 0.002778\n" % (CASE, arm, level))
        # BOTH copies the launcher writes: the run-root canonical one, whose NAME
        # carries the level and the arm, and the per-level fallback.
        _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)), rc_text)
        _write(os.path.join(d, "RUN_RC.txt"), rc_text)
    if gpusample:
        _write(os.path.join(d, "gpusample.txt"),
               "2026-01-01T00:00:00Z 4242, 512 MiB\n" * 4)
    # fields + age-guard marker
    _write(os.path.join(d, "0", "U"), "marker\n")
    _write(os.path.join(d, "0", "p"), "marker\n")
    _write(os.path.join(d, str(et), "U"), "field\n")
    _write(os.path.join(d, str(et), "p"), "field\n")
    os.utime(os.path.join(d, "0", "U"), (1_000_000, 1_000_000))
    os.utime(os.path.join(d, "0", "p"), (1_000_000, 1_000_000))
    os.utime(os.path.join(d, str(et), "U"), (2_000_000, 2_000_000))
    os.utime(os.path.join(d, str(et), "p"), (2_000_000, 2_000_000))
    # sampled set, in v2606's REAL headerless <set>_p_U.xy form
    vf = vfun or (lambda r: v_exact(r))
    rows = []
    for r in RADII:
        rows.append("%.12g %.12g %.12g %.12g %.12g %.12g %.12g"
                    % (r, 0.0, 0.0025, 0.0, 0.0, vf(r), 0.0))
    _write(os.path.join(d, "postProcessing", "radialProbes", str(et),
                        "%s_p_U.xy" % SET_NAME), "\n".join(rows) + "\n")
    # per-iteration probe series: PLATEAU_MIN samples minimum, tiny wobble
    pr = []
    for i in range(1, et + 1):
        wob = 1e-9 * ((i % 3) - 1)
        pr.append("%d " % i + " ".join("(%.17g %.17g %.17g)" % (0.0, vf(r) + wob, 0.0)
                                       for r in RADII))
    _write(os.path.join(d, "postProcessing", PROBE_FO, "0", "U"), "\n".join(pr) + "\n")
    return d


def _build_run(root, *, gpu_tells=True, cpu_leaks_gpu=False, end_line=True,
               with_rc=True, gpu_vfun=None, cpu_vfun=None, launch_record=True,
               cost=True):
    for lvl in LEVELS:
        _build_level(root, GPU_ARM, lvl, gpu_tells=gpu_tells, end_line=end_line,
                     with_rc=with_rc, vfun=gpu_vfun)
        _build_level(root, CPU_ARM, lvl, gpu_tells=cpu_leaks_gpu, end_line=True,
                     with_rc=with_rc, vfun=cpu_vfun or gpu_vfun)
    if launch_record:
        _write(os.path.join(root, "LAUNCH_RECORD.txt"),
               "case_id = %s\nlaunched_utc = 2026-01-01T00:00:00Z\nhead = %s\n"
               "prereg_sha_head = %s\nprereg_sha_disk = %s\n"
               "comparator_sha_head = %s\ncomparator_sha_disk = %s\nhost = selftest\n"
               % (CASE, "0" * 40, "a" * 40, "a" * 40, "b" * 40, "b" * 40))
    if cost:
        _write(os.path.join(root, "COST.txt"),
               "case_id = %s\ntotal_wall_s = 60\ntotal_gpu_h = 0.016667\n"
               "cost_basis = derived, not measured\n" % CASE)
    return root


def _build_run_scaled(root, gpu_scales, cpu_scales=None, cost=True):
    """A whole synthetic run with a CHOSEN per-level relative offset, so a triple
    of a chosen Roache class can be driven end to end through grade()."""
    cpu_scales = cpu_scales if cpu_scales is not None else gpu_scales
    for lvl, gs, cs in zip(LEVELS, gpu_scales, cpu_scales):
        _build_level(root, GPU_ARM, lvl, vfun=_converging_vfun(gs))
        _build_level(root, CPU_ARM, lvl, gpu_tells=False, vfun=_converging_vfun(cs))
    _write(os.path.join(root, "LAUNCH_RECORD.txt"),
           "case_id = %s\nlaunched_utc = 2026-01-01T00:00:00Z\nhead = %s\n"
           "prereg_sha_head = %s\nprereg_sha_disk = %s\n"
           "comparator_sha_head = %s\ncomparator_sha_disk = %s\nhost = selftest\n"
           % (CASE, "0" * 40, "a" * 40, "a" * 40, "b" * 40, "b" * 40))
    if cost:
        _write(os.path.join(root, "COST.txt"),
               "case_id = %s\ntotal_wall_s = 60\ntotal_gpu_h = 0.016667\n"
               "cost_basis = derived, not measured\n" % CASE)
    return root


# The per-level relative offsets that DRIVE each registered Roache class and
# each gate outcome end to end.  Written here, beside the classifier, so the
# arithmetic can be checked without running anything:
#   f_level = v_exact(r) * (1 + scale);  d21 = f_med - f_fine,  d32 = f_coarse - f_med
#   R = d21/d32,  p = ln(1/R)/ln 2
DRIVEN_TRIPLES = {
    # R = 0.98e-3 / 1.00e-3 = 0.98 -> p = 0.02915, BELOW P_MIN = 0.05 and OUTSIDE
    # the STAGNANT band (|R-1| = 0.02 > STAG_TOL = 1e-3), so this drives the
    # FLOOR ITSELF and not the ratio-first clause above it.
    "below-p-min": (1.98e-3, 0.98e-3, 0.0),
    # R = 1e-3 / 1e-3 = 1 exactly -> STAGNANT, caught on the RATIO before any p.
    "stagnant-triple": (2.0e-3, 1.0e-3, 0.0),
    # R = 1e-3 / 3e-3 = 1/3 -> p = 1.585, a CONVERGING triple; the finest level
    # sits 3.0% from the closed form, outside the 2% limb-C band.
    "limbC-miss": (0.034, 0.031, 0.030),
}


def _converging_vfun(scale):
    """A synthetic field whose triple converges at second order on r = 2."""
    def f(r):
        return v_exact(r) * (1.0 + scale)
    return f


def count_assert_nodes(source):
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def drive_refusal(kind):
    """Drive ONE refusal path.  Called by --selftest under `python3 -O` so the
    refusal is shown to survive the optimiser (Amendment 6 item 3)."""
    tmp = tempfile.mkdtemp(prefix="vmflgpu001drive_")
    try:
        if kind == "endline":
            _build_run(tmp, end_line=False)
            grade(tmp)
        elif kind == "control-leak":
            _build_run(tmp, cpu_leaks_gpu=True)
            grade(tmp)
        elif kind == "vocabulary":
            checked_verdict("FAIL")
        elif kind == "age-guard":
            _build_run(tmp)
            d = os.path.join(tmp, GPU_ARM, LEVELS[0])
            et = str(ENDTIME_BY_LEVEL[LEVELS[0]])
            for f in FIELDS_AT_ENDTIME:
                os.utime(os.path.join(d, et, f), (500_000, 500_000))
            grade(tmp)
        elif kind == "limbA-miss":
            _build_run(tmp, gpu_tells=False)
            grade(tmp)
        elif kind == "short-plateau":
            _build_run(tmp)
            f = os.path.join(tmp, GPU_ARM, LEVELS[0], "postProcessing", PROBE_FO, "0", "U")
            keep = open(f).read().splitlines()[:10]
            _write(f, "\n".join(keep) + "\n")
            grade(tmp)
        elif kind == "null-plateau":
            _build_run(tmp)
            f = os.path.join(tmp, GPU_ARM, LEVELS[0], "postProcessing", PROBE_FO, "0", "U")
            et = ENDTIME_BY_LEVEL[LEVELS[0]]
            flat = ["%d " % i + " ".join("(0 %.17g 0)" % v_exact(r) for r in RADII)
                    for i in range(1, et + 1)]
            _write(f, "\n".join(flat) + "\n")
            grade(tmp)
        elif kind == "plant-blind":
            _build_run(tmp)
            lvl_dir = os.path.join(tmp, GPU_ARM, LEVELS[-1])
            src, cols0 = find_set_file(lvl_dir, SET_NAME)

            def blind(_path, _cols):
                # returns the UNPLANTED values whatever is on disk
                return vtheta_from_raw(src, cols0)

            planted_zero_control(lvl_dir, reader=blind)
        elif kind == "gpusample":
            _build_run(tmp)
            os.remove(os.path.join(tmp, GPU_ARM, LEVELS[0], "gpusample.txt"))
            grade(tmp)
        else:
            refuse("D0", "unknown --drive-refusal kind %r" % kind)
        # Reached only if the refusal DID NOT fire.
        print("DRIVE-REFUSAL %s: NO REFUSAL FIRED" % kind)
        sys.exit(0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def drive_verdict(kind):
    """Drive ONE registered VERDICT end to end and print it.  Called by
    --selftest under `python3 -O`, so the gate's own routing -- not only its
    refusals -- is shown to survive the optimiser.

    This exists because P_MIN, STAGNANT and the limb-C band do NOT refuse: they
    ROUTE, to NOT A RESULT or GATE FAIL.  A floor nobody drives is a floor
    nobody has (FINDING_p_floor.md section 4), and a routing decision is
    invisible to an exit-code check."""
    if kind not in DRIVEN_TRIPLES:
        refuse("D1", "unknown --drive-verdict kind %r" % kind)
    tmp = tempfile.mkdtemp(prefix="vmflgpu001verd_")
    try:
        _build_run_scaled(tmp, DRIVEN_TRIPLES[kind])
        grade(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _drives_verdict(kind, expected, forbid=None):
    """Run `python3 -O <this file> --drive-verdict <kind>` and require the
    printed verdict to be `expected`.  `forbid`, when given, must NOT appear
    anywhere in the output -- that is how "NO GCI IS PRINTED" is checked as a
    reading rather than asserted as a belief."""
    proc = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                           "--drive-verdict", kind],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    got = [ln.split("VERDICT:", 1)[1].strip()
           for ln in proc.stdout.splitlines() if ln.startswith("VERDICT:")]
    if len(got) != 1 or got[0] != expected:
        return False
    if forbid is not None and forbid in proc.stdout:
        return False
    return True


def selftest():
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    print("%s comparator --selftest (NO run data touched)" % CASE)

    # --- the instrument's own AST, and the counter shown able to count -----
    src = open(os.path.abspath(__file__)).read()
    n_here = count_assert_nodes(src)
    chk("zero `assert` statements in this instrument (Amendment 6 item 1)", n_here == 0)
    chk("the AST counter can SEE a planted assert, so its zero is a reading",
        count_assert_nodes("def f(x):\n    assert x > 0\n    return x\n") == 1)

    # --- the reference arithmetic ------------------------------------------
    chk("v_exact(20 mm) == 0.015120 m/s to 6 s.f.", abs(v_exact(0.020) - 0.0151201) < 5e-7)
    chk("v_exact(R_i) == omega R_i exactly", abs(v_exact(R_I) - OMEGA * R_I) < 1e-15)
    chk("v_exact(R_o) == 0", abs(v_exact(R_O)) < 1e-18)

    # --- the Roache classifier, INCLUDING the degenerate triple ------------
    deg = roache(1.0, 1.1, 1.2)
    chk("equally spaced triple (1.0, 1.1, 1.2) is STAGNANT, not CONVERGING "
        "(FINDING_p_floor.md)", deg["state"] == "STAGNANT")
    chk("...and NO GCI is printed for it", deg["gci_fine"] is None)
    conv = roache(2.50125, 2.5003125, 2.50007812)
    chk("second-order family is CONVERGING with p ~ 2",
        conv["state"] == "CONVERGING" and abs(conv["p"] - 2.0) < 1e-3)
    chk("oscillatory triple is OSCILLATORY", roache(1.0, 1.2, 1.1)["state"] == "OSCILLATORY")
    chk("divergent triple is DIVERGENT", roache(1.0, 1.1, 1.3)["state"] == "DIVERGENT")
    # R = d21/d32 = 0.98 -> p = ln(1/0.98)/ln 2 = 0.0291, BELOW the P_MIN floor
    # and OUTSIDE the STAGNANT band, so this drives the floor itself and not the
    # ratio-first clause above it.
    lowp = roache(1.0, 1.0 + 1e-3, 1.0 + 1.98e-3)
    chk("an observed order below P_MIN = %g is NOT CONVERGING and prints NO GCI "
        "(FINDING_p_floor.md section 4)" % P_MIN,
        lowp["state"] == "BELOW_P_MIN" and lowp["p"] < P_MIN
        and lowp["gci_fine"] is None)

    # --- the tells ----------------------------------------------------------
    chk("tell3 sees seqaijcusparse", tell3_cuda_type("Mat Object:\n  type: seqaijcusparse\n"))
    chk("tell3 does NOT see seqaij as a cusparse type",
        not tell3_cuda_type("Mat Object:\n  type: seqaij\n"))
    chk("tell2 sees a PID holding device memory", tell2_pid_on_gpu("4242, 512 MiB\n"))
    chk("tell2 does NOT fire on an empty GPU", not tell2_pid_on_gpu("\n\n"))

    # --- end-to-end on synthetic runs --------------------------------------
    tmp = tempfile.mkdtemp(prefix="vmflgpu001self_")
    try:
        # (1) a clean, CONVERGING, in-band run must reach the tier ceiling.
        good = os.path.join(tmp, "good")
        # errors 4x, 1x, 0.25x of a base offset -> exactly second order on r = 2
        _build_run(good, gpu_vfun=_converging_vfun(4e-4))
        for lvl, sc in zip(LEVELS, (4e-3, 1e-3, 2.5e-4)):
            _build_level(good, GPU_ARM, lvl, vfun=_converging_vfun(sc))
            _build_level(good, CPU_ARM, lvl, gpu_tells=False, vfun=_converging_vfun(sc))
        v = grade(good)
        chk("a clean in-band run reaches the tier ceiling %r" % TIER_CEILING,
            v == TIER_CEILING)

        # (2) INFRASTRUCTURE plant: corrupt COST.txt -> the verdict must NOT move.
        infra = os.path.join(tmp, "infra")
        for lvl, sc in zip(LEVELS, (4e-3, 1e-3, 2.5e-4)):
            _build_level(infra, GPU_ARM, lvl, vfun=_converging_vfun(sc))
            _build_level(infra, CPU_ARM, lvl, gpu_tells=False, vfun=_converging_vfun(sc))
        _write(os.path.join(infra, "LAUNCH_RECORD.txt"),
               "case_id = %s\nprereg_sha_head = %s\nprereg_sha_disk = %s\n"
               "comparator_sha_head = %s\ncomparator_sha_disk = %s\n"
               % (CASE, "a" * 40, "a" * 40, "b" * 40, "b" * 40))
        _write(os.path.join(infra, "COST.txt"), "\x00\x01 garbage not a kv file\n")
        v2 = grade(infra)
        chk("a CORRUPT COST.txt (INFRASTRUCTURE) leaves the verdict unchanged (L-342)",
            v2 == v)

        # (3) INFRASTRUCTURE plant: delete COST.txt entirely -> unchanged.
        os.remove(os.path.join(infra, "COST.txt"))
        v3 = grade(infra)
        chk("a MISSING COST.txt leaves the verdict unchanged (L-342)", v3 == v)

        # (4) PHYSICS plant: remove the End line -> must REFUSE (exit 2).
        chk("removing the End line (PHYSICS) REFUSES",
            _drives_exit2("endline"))
        # (5) PHYSICS plant: remove the gpusample tell -> must REFUSE.
        chk("removing gpusample.txt (PHYSICS: tell 2) REFUSES",
            _drives_exit2("gpusample"))
        # (6) the forced-CPU control leaking GPU work -> must REFUSE.
        chk("a forced-CPU control that REPORTS GPU work REFUSES (certifies nothing)",
            _drives_exit2("control-leak"))
        # (7) the vocabulary guard, under -O.
        chk("the verdict-vocabulary guard REFUSES under `python3 -O`",
            _drives_exit2("vocabulary"))

        # (8) rc bookkeeping absent -> NOT A RESULT, NOT a refusal, physics printed.
        norc = os.path.join(tmp, "norc")
        for lvl, sc in zip(LEVELS, (4e-3, 1e-3, 2.5e-4)):
            _build_level(norc, GPU_ARM, lvl, vfun=_converging_vfun(sc))
            _build_level(norc, CPU_ARM, lvl, gpu_tells=False, vfun=_converging_vfun(sc))
        os.remove(os.path.join(norc, GPU_ARM, LEVELS[0], "RUN_RC.txt"))
        os.remove(os.path.join(norc, "RUN_RC.%s.%s" % (LEVELS[0], GPU_ARM)))
        _write(os.path.join(norc, "LAUNCH_RECORD.txt"),
               "prereg_sha_head = %s\nprereg_sha_disk = %s\n"
               "comparator_sha_head = %s\ncomparator_sha_disk = %s\n"
               % ("a" * 40, "a" * 40, "b" * 40, "b" * 40))
        v4 = grade(norc)
        chk("an ABSENT RUN_RC.txt gives NOT A RESULT with the physics printed, "
            "not a voiding refusal (supervisor addendum, L-342)", v4 == "NOT A RESULT")

        # (9) limb B: a GPU arm that differs from the CPU arm must GATE FAIL.
        bad = os.path.join(tmp, "limbB")
        for lvl, sc in zip(LEVELS, (4e-3, 1e-3, 2.5e-4)):
            _build_level(bad, GPU_ARM, lvl, vfun=_converging_vfun(sc))
            _build_level(bad, CPU_ARM, lvl, gpu_tells=False,
                         vfun=_converging_vfun(sc + 1e-2))
        _write(os.path.join(bad, "LAUNCH_RECORD.txt"),
               "prereg_sha_head = %s\nprereg_sha_disk = %s\n"
               "comparator_sha_head = %s\ncomparator_sha_disk = %s\n"
               % ("a" * 40, "a" * 40, "b" * 40, "b" * 40))
        v5 = grade(bad)
        chk("a GPU arm that does NOT match the forced-CPU arm is GATE FAIL",
            v5 == "GATE FAIL")

        # (10) the planted-zero control, both arms.
        pz = planted_zero_control(os.path.join(good, GPU_ARM, LEVELS[-1]))
        chk("planted-zero control fires ON EVERY ONE OF THE %d GATE CHANNELS: the "
            "reader SEES %g m/s planted on disk at each radius (L-340 per-channel "
            "sizing)" % (len(RADII), PLANT),
            pz["passed"] and len(pz["per_channel"]) == len(RADII)
            and all(abs(pz["per_channel"]["%.3f" % r] - PLANT) <= PLANT_TOL
                    for r in RADII))
        chk("the plant is supra-threshold on the SMALLEST gated channel: "
            "PLANT / v(35 mm) > 0.1, so a point reader that works cannot be "
            "refused by dilution (L-340)",
            pz["plant_over_smallest_gated_value"] > 0.1)
        chk("planted-zero NEGATIVE arm: a reader given an unplanted copy sees 0 move",
            _plant_negative_arm(os.path.join(good, GPU_ARM, LEVELS[-1])))
        # (11) drive the planted-zero control's OWN REFUSAL with a blind reader:
        # a reader not shown able to MISS a plant is not shown able to see one.
        chk("a BLIND reader (returns the pre-plant values) makes the planted-zero "
            "control REFUSE -- the guard's failing branch is driven, not assumed",
            _drives_exit2("plant-blind"))
        # (12) the plateau clause's own two refusals, driven (Amendment 4 items 2, 4).
        chk("a plateau series shorter than the registered minimum %d REFUSES as "
            "CANNOT_TELL, never a lenient pass" % PLATEAU_MIN,
            _drives_exit2("short-plateau"))
        chk("a plateau window with NULL RANGE (a dead series) REFUSES",
            _drives_exit2("null-plateau"))
        # (13) the age guard's own refusal, driven: a field at endTime that is
        # OLDER than the case's own 0/U did not come from this run (rule 4).
        chk("a field at endTime OLDER than 0/U REFUSES on the AGE GUARD",
            _drives_exit2("age-guard"))
        # (14) limb A's failing branch, driven: the GPU arm showing no GPU tells
        # is NOT A RESULT and exits 2 -- never a PASS on CPU physics.
        chk("a GPU arm whose tells do NOT fire yields NOT A RESULT and exits 2, "
            "never a PASS (limb A is the object under verification)",
            _drives_exit2("limbA-miss"))
        # (15) THE P_MIN FLOOR, DRIVEN END TO END under `-O`: a triple whose
        # observed order is 0.0292 (below the registered floor 0.05) must route
        # to NOT A RESULT, and NO GCI may appear anywhere in the output.
        chk("a triple whose observed order is BELOW P_MIN = %g routes to NOT A "
            "RESULT end to end under `python3 -O` (FINDING_p_floor.md section 4)"
            % P_MIN,
            _drives_verdict("below-p-min", "NOT A RESULT"))
        chk("...and NO GCI is printed anywhere for it -- a GCI from a near-zero "
            "order is a number with no meaning",
            _drives_verdict("below-p-min", "NOT A RESULT", forbid="GCI_fine ="))
        # (16) the ratio-first STAGNANT clause, driven end to end.
        chk("an equally-spaced triple (R = 1 exactly) routes to NOT A RESULT end "
            "to end, classified on the RATIO before any p is computed",
            _drives_verdict("stagnant-triple", "NOT A RESULT", forbid="GCI_fine ="))
        # (17) limb C's own failing branch, driven: a CONVERGING triple sitting
        # 3.0% from the closed form is outside the 2% band.
        chk("a CONVERGING triple 3.0%% from the lab-evaluated closed form is "
            "GATE FAIL against the %g limb-C band" % TOL_C,
            _drives_verdict("limbC-miss", "GATE FAIL"))
        # (18) the limb-C reference is the closed form THIS FILE evaluates, not
        # the manual's rounded printed column -- shown by the two disagreeing.
        chk("the limb-C reference is the lab-evaluated closed form, which "
            "DIFFERS from the manual's printed 2-s.f. column by 1.15% at "
            "r = 35 mm (so the two are not interchangeable)",
            abs(abs(MANUAL_PRINTED_TARGET[0.035] - v_exact(0.035))
                / v_exact(0.035) - 0.011476) < 1e-5)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("  PASS  " if ok else "  FAIL  ") + n)
    if failed:
        print("")
        print("SELFTEST FAILED: %d of %d checks did not behave." % (len(failed), len(checks)))
        sys.exit(1)
    # The ONLY place a pass is claimed; unreachable when a check fails above.
    print("")
    print("SELFTEST GREEN: %d checks, each shown able to fail." % len(checks))
    sys.exit(0)


def _drives_exit2(kind):
    """Run `python3 -O <this file> --drive-refusal <kind>` and require exit 2."""
    proc = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                           "--drive-refusal", kind],
                          capture_output=True, text=True)
    return proc.returncode == 2


def _plant_negative_arm(level_dir):
    """The NEGATIVE arm of rule 3: the same reader, on an UNPLANTED copy, must
    report no movement.  A reader that reports a move where none was planted is
    as useless as one that misses a real one."""
    src, cols = find_set_file(level_dir, SET_NAME)
    before = gate_values(level_dir)[0]
    tmp = tempfile.mkdtemp(prefix="vmflgpu001neg_")
    try:
        work = os.path.join(tmp, os.path.basename(src))
        shutil.copyfile(src, work)
        got = vtheta_from_raw(work, cols)
        for r in RADII:
            hits = [v for (rr, th, v) in got if abs(rr - r) < 1e-6]
            if len(hits) != 1 or abs(hits[0] - before[r]) > PLANT_TOL:
                return False
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(description="%s comparator" % CASE)
    ap.add_argument("--run-root")
    ap.add_argument("--out-json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drive-refusal")
    ap.add_argument("--drive-verdict")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
    elif a.drive_refusal:
        drive_refusal(a.drive_refusal)
    elif a.drive_verdict:
        drive_verdict(a.drive_verdict)
    elif a.run_root:
        out = a.out_json or os.path.join(a.run_root, "GRADING_%s.json" % CASE)
        grade(a.run_root, out)
    else:
        ap.error("give --selftest or --run-root")


if __name__ == "__main__":
    main(sys.argv[1:])
