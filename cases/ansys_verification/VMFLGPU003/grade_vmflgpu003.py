#!/usr/bin/env python3
"""VMFLGPU003 comparator -- THE LAB'S GPU SOLVER PATH, exercised on laminar flow
in a lid-driven TRIANGULAR CAVITY (Ansys Fluid Dynamics Verification Manual,
Release 2026 R1, p. 229).

WHAT IS UNDER VERIFICATION.  Not the physics -- the physics is the CPU parent's,
registered as VMFL011 (manual p. 41, the same cavity, the same reference, the
same digitised benchmark curve).  The object is the lab's GPU solver path:
OpenFOAM v2606 + petsc4Foam + PETSc-CUDA on the L4 (sm_89).  The gate therefore
has THREE LIMBS and a miss on limb A is NOT A RESULT whatever the physics says
(DRAFT_PREREGISTRATIONS_VMFLGPU.md, "THE GPU-SOLVER-PATH GATE").

    limb A  GPU EXECUTION      three tells + the forced-CPU control
    limb B  GPU == CPU         |q_GPU - q_CPU| / |q_CPU| <= TOL_B, on BOTH gate
                               channels, at EVERY level
    limb C  PHYSICS            rms_vs_benchmark at the finest GPU level <=
                               BAND_RMS, where the benchmark is Jyotsna & Vanka
                               1995 -- ANOTHER CODE'S NUMERICAL SOLUTION.  A
                               code-to-code reference buys NEITHER V NOR P, so
                               the ceiling is GATE REACHED and this case cannot
                               earn PASS however well it agrees.

THE PARENT IS NOT A CLEAN CONTROL, and that is registered here rather than
discovered later.  VMFL011 (register row #26) and VMFL011-R2 (row #31) both
graded NOT A RESULT -- both times because the frozen comparator's planted-zero
control REFUSED, first on plant MAGNITUDE (L-340) and then on plant LOCATION
(L-347).  Neither refusal was a physics finding and neither produced a number.
VMFL011-R3 carries the repaired instrument and had not run when this file was
frozen.  THIS CASE MAY WELL LAND NOT A RESULT TOO -- on the Roache triple, on a
missing rc, or on limb A -- and if it does the row is NOT A RESULT however good
the value looks.  The gate can only turn a PASS or GATE FAIL INTO NOT A RESULT,
never the reverse.  Written down BEFORE the run so a NOT A RESULT here reads as
the rule working, not as a disappointment.

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
  * the solver rc, from RUN_RC WHEN PRESENT.  When it is ABSENT the rc is NOT
    MEASURED: the verdict becomes NOT A RESULT and the physics is PRINTED -- it
    is not a voiding refusal.                     (strict_completion, "rc")
  * the End line in log.simpleFoam                (strict_completion clause 2)
  * last time == the level's registered endTime   (strict_completion clause 3)
  * the declared fields present at endTime        (strict_completion clause 4)
  * the `Time =` line count == endTime            (strict_completion clause 5)
  * the age guard on the case's own 0/U           (strict_completion clause 6)
  * the residual clause and the plateau clause    (iterative_convergence)
  * the mesh birth certificate                    (mesh_birth_certificate)
  * the launch-time sha freeze                    (freeze_record)
  * THE THREE GPU TELLS AND THE FORCED-CPU CONTROL (limb_A).  For THIS FAMILY
    limb A is physics-critical because it IS the object under verification.

INFRASTRUCTURE -- NEVER refused on, NEVER voids a verdict; absent or anomalous
is a labelled WARNING and the grade proceeds on the physics artifacts:
  * THE ExecutionTime LINE COUNT.  MEASURED on this very instance, on
    VMFLGPU002's own completed L1 log: 1200 `Time =` lines and 1202
    `ExecutionTime` lines for endTime = 1200 -- petsc4Foam prints endTime + 2
    timing lines.  VMFLGPU001 was frozen with an ExecutionTime-line count as a
    PHYSICS-CRITICAL clause, its six arms all finished rc 0, and it has NO
    VERDICT because of it (post-compute amendment 4, commit 59110074).  That
    clause is INFRASTRUCTURE here, from the first line of this file, and the
    physics-critical clause is the `Time =` line count.
  * COST.txt and every GPU-hour / core-minute figure   (cost_record)
  * LAUNCH_RECORD.txt's non-sha bookkeeping lines      (freeze_record)
  * CAP_OVERRUN.txt, contention and status files; memory figures, pids, sids
=============================================================================

INSTRUMENT RULES OBSERVED HERE, each paid for by a measured failure:
  * NO `assert` carries a refusal, guard, control or gate (PREREG_TEMPLATE
    Amendment 6; L-332).  `python3 -O` deletes every assert.  `--selftest`
    parses this file's own AST and refuses on a single Assert node, and the AST
    counter is shown able to count a planted one.
  * NO UNCONDITIONAL SUCCESS PRINT.  Every green line is emitted from inside the
    branch that verified it.
  * EVERY CONTROL FUNCTION FALLS THROUGH TO refuse(), so the only way to return
    is to have passed.
  * REFUSALS FIRE UNDER `python3 -O` -- `--drive-refusal` drives one, and
    `--selftest` runs it under `-O` and requires exit 2.
  * L-347 CLAUSE 2: EVERY planted-zero channel runs and is REPORTED BEFORE ANY
    EXIT.  A control standing behind another control's refusal is an untested
    control -- that is exactly how VMFL011's u_min plant survived two freezes
    without ever executing on real bisector bytes.
  * L-347 CLAUSE 1: THE PLANT GOES WHERE THE READER LOOKS.  The u_min_norm plant
    is placed at the ARGMIN ROW -- the row a min() reader selects -- never at
    row 0, which on this cavity's bisector is the collapsed apex where u == 0
    exactly and where a correctly sized plant moves a min() reader by ZERO.
  * L-340: the plant is SIZED TO THE READER.  The rms channel is an AVERAGING
    reader over 46 abscissae, so a point-sized plant is diluted; its plant is
    K * U_WALL * max(|base|, floor) with K = 4, and the sizing is MEASURED by
    the control, not asserted by the comment above it.
  * P_MIN = 0.05 and RATIO-FIRST classification (FINDING_p_floor.md section 4).
  * PLATEAU: a FIXED window (not a fraction), a minimum-sample refusal, a
    peak-to-peak statistic, and an EXPLICIT NULL-RANGE RULE (see
    iterative_convergence) that separates a DEAD channel from a PERFECTLY
    CONVERGED one instead of conflating them.

    python3 grade_vmflgpu003.py --run-root <root>
    python3 grade_vmflgpu003.py --selftest
    python3 grade_vmflgpu003.py --drive-refusal <kind>    # used by --selftest
    python3 grade_vmflgpu003.py --drive-verdict <kind>    # used by --selftest
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
CASE = "VMFLGPU003"
MANUAL_PAGE = "229"
CPU_PARENT = "VMFL011"

# --- the physics, manual p. 229 --------------------------------------------
U_WALL = 2.0                # m/s, velocity of the top (base) wall
RHO = 1.0                   # kg/m3
MU = 0.01                   # kg/m-s   -> nu = 0.01 m2/s, Re = U*base/nu = 400
BASE_WIDTH = 2.0            # m
CAVITY_HEIGHT = 4.0         # m

# --- the reference ---------------------------------------------------------
# The manual prints Figure .gpu003.2 and NO discrete target table, so no number
# could be read off the manual text.  The curve is Ansys's own digitisation of
# the cited reference, carried in the parent case's own project archive and
# copied byte-for-byte into reference/vmfl011_benchmark_xnorm.csv (46 rows, git
# blob 9f11191b8c823eb32edd3f2b74bd29da855aab55, identical to the blob committed
# with VMFL011-R3).  Provenance in full is in the CSV's own header.
REF_KIND = ("code-to-code / numerical benchmark (Jyotsna & Vanka, J. Comp. Phys. "
            "122, 107-117, 1995) -- buys NEITHER V nor P")
TIER_CEILING = "GATE REACHED"

# --- the bands -------------------------------------------------------------
# BAND_RMS is carried CHARACTER FOR CHARACTER from the CPU parent's frozen
# comparator (VMFL011-R3, `BAND_RMS = 0.030`), which itself carries it from
# VMFL011-R2 and from the original VMFL011 freeze.  It has never been met and
# has never been moved.  Choosing it here would be gate-fitting; inheriting it
# is the only way this case's band can be older than this case.
BAND_RMS = 0.030            # limb C: rms_vs_benchmark at the finest GPU level
TOL_B = 1e-4                # limb B: GPU == CPU.  Derivation in PREREG 6.2.

# --- the ladder ------------------------------------------------------------
LEVELS = ("L1_20x40", "L2_40x80", "L3_80x160")
CELLS_BY_LEVEL = {"L1_20x40": 800, "L2_40x80": 3200, "L3_80x160": 12800}
# endTime BASIS, and it is a MEASUREMENT of the parent's completed run, never a
# guess and never a gate: in VMFL011-R2's own log.simpleFoam the initial
# residuals of Ux, Uy AND p all fall below 1e-7 and STAY below it from iteration
# 259 / 488 / 1455 at L1 / L2 / L3.  The registered endTimes are 1000 / 1500 /
# 3500 -- margins of 3.9x / 3.1x / 2.4x on the measured convergence point.  An
# endTime is a DURATION, not a gate: it cannot move a band and it cannot change
# a label.  If a level does not reach RESID_FLOOR by its endTime this comparator
# REFUSES; the margin is the protection against that, and the risk is registered
# in PREREGISTRATION.md section 9.
ENDTIME_BY_LEVEL = {"L1_20x40": 1000, "L2_40x80": 1500, "L3_80x160": 3500}
# The parent's MEASURED convergence points, quoted so the margin is a number in
# this file and not a claim in a comment: the iteration from which Ux, Uy and p
# ALL stay below 1e-7 in VMFL011-R2's own log.simpleFoam.
PARENT_CONVERGED_AT = {"L1_20x40": 259, "L2_40x80": 488, "L3_80x160": 1455}
ARMS = ("gpu", "cpu")
GPU_ARM, CPU_ARM = "gpu", "cpu"

# --- Roache ----------------------------------------------------------------
RATIO = 2.0                 # r = 2 exactly (NB and NH double together)
FS = 1.25                   # Roache factor of safety
EPS_ABS = 1e-12             # the "no difference at all" floor
STAG_TOL = 1e-3             # |R - 1| within this is STAGNANT, decided on R FIRST
P_MIN = 0.05                # FINDING_p_floor.md section 4

# --- iterative convergence -------------------------------------------------
RESID_FLOOR = 1.0e-7        # frozen; carried from the parent comparator
PLATEAU_WINDOW = 400        # FIXED sample count, never a fraction
PLATEAU_MIN = 400           # fewer samples -> CANNOT_TELL, never a pass
PLATEAU_TOL = 1.0e-6        # m/s, peak-to-peak of u_min over the window
# THE NULL-RANGE RULE.  A window peak-to-peak of EXACTLY zero is ambiguous: a
# dead channel and a perfectly converged one look identical to a tolerance.
# VMFLGPU001's re-grade refused at exactly this clause.  Instead of conflating
# the two, this comparator SEPARATES them: a null window range is accepted ONLY
# when the channel is shown to have been ALIVE earlier in the same run --
# full-history peak-to-peak strictly greater than PLATEAU_ALIVE_MIN.  A channel
# that never moved at all is still refused.  This is strictly MORE
# discriminating than a bare null-range refusal, it is registered before any
# compute, and it can only be satisfied by evidence from the run's own bytes.
PLATEAU_ALIVE_MIN = 1.0e-3  # m/s, full-history peak-to-peak

# --- planted zero (CLAUDE.md rule 3) ---------------------------------------
PLANT = 1.234e-03           # the POINT-reader plant, carried from the parent
# L-347: BYTE-IDENTICAL IN MAGNITUDE to the parent's u_min plant; the ONLY
# difference is WHERE it is planted -- at the argmin row, which is the row a
# min() reader actually selects.
UMIN_PLANT = -abs(1.234e-03) * 100
# L-340: the rms channel AVERAGES over 46 abscissae, so its plant is sized to
# the reader.  K > 2.5 is required at U_WALL = 2; 4 gives a 2.5x margin.
RMS_PLANT_K = 4.0
RMS_PLANT_FLOOR = 1.0e-6    # so a run that matched the benchmark exactly still plants
PLANT_MIN_GAIN = 0.1        # the threshold rule: delta > 0.1 * |plant|

CHANNELS = ("u_min_norm", "rms_vs_benchmark")

# --- LIMB A, REPAIRED AT THE SUPERVISOR'S RULING OF 2026-08-27 -------------
# VMFLGPU001's and VMFLGPU002's frozen tells were BROKEN BEFORE COMPUTE, and
# provably so from the frozen file alone: their tell 1 fired on ANY
# CUDA-configured build, including the forced-CPU control, so limb_A refused at
# A2 by construction; and their tell 3 looked for a `type: aijcusparse` ksp_view
# line THIS BUILD NEVER PRINTS, so it false-negatived a genuine GPU run.  This
# case does not inherit either of them.
#
# The replacement is PETSc's OWN -log_view event accounting, MEASURED on the
# real VMFLGPU002 artifacts on this very instance (run root
# .../VMFLGPU002/{gpu,cpu}/L1_N20/log.simpleFoam), where it separates the two
# arms without ambiguity:
#
#   event      arm   Total Mflop/s   GPU Mflop/s   CpuToGpu count   GPU %F
#   MatMult    gpu       1184           2834            6000         100
#   MatMult    cpu       2460              0               0           0
#   KSPSolve   gpu        424            680            3601         100
#   KSPSolve   cpu       2056              0               0           0
#
# The last field of a -log_view event row is GPU %F; CpuToGpu count is the fifth
# from the end.  Both are ZERO on the forced-CPU arm and both are large on the
# GPU arm, on the same build, in the same run pair.
LOGVIEW_EVENTS = ("MatMult", "KSPSolve")
GPU_PCTF_MIN = 99.0         # floor, not a target: MEASURED 100 on both events
                            # of the 002 GPU arm; 1 point of headroom for a
                            # rounded print, and still unreachable by a CPU arm,
                            # which reports exactly 0.
CPU_ARM_PCTF_MAX = 0.0      # the control must report NO GPU flops at all
LOGVIEW_ROW_RE = re.compile(r"^(%s)\s+\d" % "|".join(LOGVIEW_EVENTS))

# --- completion ------------------------------------------------------------
FIELDS_AT_ENDTIME = ("U", "p")
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

TIME_RE = re.compile(r"^[0-9]+([.][0-9]*)?([eE][+-]?[0-9]+)?$")
KV_RE = re.compile(r"(\w+)\s*=\s*(.*)")
RES_RE = re.compile(r"Solving for (\w+),\s+Initial residual = ([0-9eE.+-]+)")


# ---------------------------------------------------------------------------
# refusal, warning, vocabulary
# ---------------------------------------------------------------------------
def refuse(code, msg):
    """Exit 2.  Never an assert: `python3 -O` would delete an assert (L-332)."""
    sys.stderr.write("REFUSE (%s %s): %s\n" % (CASE, code, msg))
    sys.exit(2)


def warn_infra(msg):
    """An INFRASTRUCTURE field is absent or anomalous.  This NEVER refuses and
    NEVER changes a verdict (L-342)."""
    print("  WARNING(INFRASTRUCTURE): %s" % msg)
    return None


def checked_verdict(verdict):
    """CLAUDE.md rule 1's vocabulary guard, as an explicit refusal so it
    survives `python3 -O`."""
    if verdict in VERDICTS:
        return verdict
    refuse("V0", "verdict %r is not in the fixed vocabulary %s" % (verdict, list(VERDICTS)))
    refuse("V0-FALLTHROUGH", "unreachable: the vocabulary guard did not exit")


# ---------------------------------------------------------------------------
# THE READERS.
#
# The gate quantity is the normalised X-velocity profile on the vertical line
# bisecting the base (manual Figure .gpu003.2), read from the `bisector` sets
# function object that case/system/controlDict.template registers.  That object
# writes ONE 401-point profile PER SIMPLE ITERATION, so the SAME artifact
# carries the gate value (the directory named exactly endTime) and the plateau
# series (u_min over the whole history).  A plateau measured in something other
# than the gate quantity is not a plateau in the gate quantity, and this
# comparator does not accept a proxy for it.
#
# TWO channels are read off that profile and BOTH are gate channels:
#   rms_vs_benchmark -- the RMS, over the benchmark's own 46 abscissae, of
#       (lab profile interpolated there) - (benchmark).  This is limb C.
#   u_min_norm       -- the most negative normalised X-velocity on the bisector:
#       a SOLUTION FUNCTIONAL, not an error norm.  The Roache triple runs on
#       THIS, for the parent's registered reason: the benchmark curve is a plot
#       digitisation carrying its own noise floor (it reports values between
#       -2.7e-04 and +1.1e-02, changing sign, in the quiescent lower half where
#       the physical velocity is essentially zero), so an error-versus-reference
#       norm cannot converge to zero and would grade STAGNANT for a reason that
#       has nothing to do with this lab's discretisation.
# ---------------------------------------------------------------------------
def _resolve(path):
    """A file is `X` or `X.gz`."""
    if os.path.isfile(path):
        return path
    if os.path.isfile(path + ".gz"):
        return path + ".gz"
    return None


def _ref_csv():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "reference", "vmfl011_benchmark_xnorm.csv")


def _bench():
    """The 46 benchmark rows, sorted by y.  Refuses rather than grading against
    a reference it could not read."""
    p = _ref_csv()
    if not os.path.isfile(p):
        refuse("B0", "the benchmark reference CSV is absent: %s -- there is nothing "
                     "to grade limb C against" % p)
    ys, vs = [], []
    for ln in open(p, errors="replace"):
        if ln.startswith("#") or not ln.strip():
            continue
        parts = ln.strip().split(",")
        if len(parts) != 2:
            refuse("B1", "unparseable benchmark row %r in %s" % (ln.strip(), p))
        try:
            ys.append(float(parts[0]))
            vs.append(float(parts[1]))
        except ValueError:
            refuse("B1", "unparseable benchmark row %r in %s" % (ln.strip(), p))
    if len(ys) < 2:
        refuse("B2", "the benchmark reference carries %d rows; an RMS over fewer than "
                     "two abscissae is not a norm" % len(ys))
    z = sorted(zip(ys, vs))
    return [t[0] for t in z], [t[1] for t in z]


def _interp(xs, ys, x):
    """Linear interpolation on a sorted-ascending abscissa.  Clamps at the ends
    rather than extrapolating: the benchmark's first and last abscissae are the
    cavity apex and the moving wall, both of which the lab profile spans."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    span = xs[hi] - xs[lo]
    if span <= 0.0:
        return ys[lo]
    w = (x - xs[lo]) / span
    return ys[lo] * (1.0 - w) + ys[hi] * w


def _bisector_dirs(level_dir):
    """{iteration:int -> path of bisect_U.xy}.  Sorted NUMERICALLY, never
    lexicographically: '999' sorts after '3500' as a string, and the gate value
    would then be read from the wrong iteration and would still print to twelve
    figures."""
    root = os.path.join(level_dir, "postProcessing", "bisector")
    if not os.path.isdir(root):
        refuse("R0", "no postProcessing/bisector under %s -- the gate artifact is "
                     "absent, and an absent gate artifact is a refusal, never a number"
               % level_dir)
    out = {}
    for name in os.listdir(root):
        d = os.path.join(root, name)
        if not os.path.isdir(d) or not TIME_RE.match(name):
            continue
        f = _resolve(os.path.join(d, "bisect_U.xy"))
        if f is not None:
            out[float(name)] = f
    if not out:
        refuse("R1", "no bisect_U.xy under %s/postProcessing/bisector" % level_dir)
    return out


def _xy_at_endtime(level_dir):
    """The gate artifact, ANCHORED ON THE REGISTERED endTime.

    Never `the last directory`: a truncated or restarted run leaves a perfectly
    well-formed profile for the wrong iteration, and that number is
    indistinguishable from the right one once it is out of context."""
    et = float(ENDTIME_BY_LEVEL[os.path.basename(level_dir)])
    dirs = _bisector_dirs(level_dir)
    hits = [p for (t, p) in dirs.items() if abs(t - et) < 1e-9]
    if len(hits) != 1:
        refuse("R2", "expected exactly one bisector sample at t = %g in %s, found %d -- "
                     "the gate is read AT endTime or it is not read"
               % (et, os.path.basename(level_dir), len(hits)))
    return hits[0]


def _rows(path):
    """[(y, u_x / U_WALL)] from a raw `sets` .xy file."""
    if not os.path.isfile(path):
        refuse("R3", "profile file does not exist: " + path)
    out = []
    for ln in open(path, errors="replace"):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            refuse("R4", "unparseable profile row in %s: %r" % (path, s))
        try:
            out.append((float(parts[0]), float(parts[1]) / U_WALL))
        except ValueError:
            refuse("R4", "unparseable profile row in %s: %r" % (path, s))
    if len(out) < 2:
        refuse("R5", "%s carries %d profile rows; the gate cannot be read from it"
               % (path, len(out)))
    return out


def _read_rms(path):
    """rms_vs_benchmark: the RMS, over the benchmark's own 46 abscissae, of the
    difference between the lab profile interpolated there and the benchmark.

    AN AVERAGING READER.  That is why its plant is sized (L-340)."""
    r = _rows(path)
    xs = [t[0] for t in r]
    ys = [t[1] for t in r]
    by, bv = _bench()
    s = sum((_interp(xs, ys, by[i]) - bv[i]) ** 2 for i in range(len(by)))
    return math.sqrt(s / len(by))


def _read_umin(path):
    """u_min_norm: the most negative normalised X-velocity on the bisector.

    A POINT READER.  That is why its plant must be placed at the row it selects
    (L-347)."""
    return min(u for _, u in _rows(path))


READERS = {"u_min_norm": _read_umin, "rms_vs_benchmark": _read_rms}


def gate_values(level_dir, readers=None):
    """{channel: value} at t == the level's REGISTERED endTime, plus the path."""
    readers = readers or READERS
    p = _xy_at_endtime(level_dir)
    return {ch: readers[ch](p) for ch in CHANNELS}, p


# ---------------------------------------------------------------------------
# planted-zero control (CLAUDE.md rule 3), with the L-340 and L-347 repairs
# ---------------------------------------------------------------------------
def rms_plant_for(base):
    """Size the plant to the AVERAGING reader (L-340).  Driven by the control on
    real bytes, never assumed."""
    return RMS_PLANT_K * U_WALL * max(abs(base), RMS_PLANT_FLOOR)


def _argmin_row(path):
    """The index, among DATA rows only, of the row carrying min(u).  This is the
    row a min() reader selects, and therefore the only row a plant aimed at that
    reader may be placed in (L-347)."""
    r = _rows(path)
    best, idx = None, None
    for i, (_, u) in enumerate(r):
        if best is None or u < best:
            best, idx = u, i
    if idx is None:
        refuse("P0", "no data row to select in " + path)
    return idx


def _data_line_indices(lines):
    return [i for i, ln in enumerate(lines)
            if ln.strip() and not ln.strip().startswith("#") and len(ln.split()) >= 2]


def _perturb_at_argmin(path, plant):
    """THE L-347 REPAIR, and the whole of it: plant into the row the reader
    SELECTS, not the row the file starts with.

    On this cavity's bisector, row 0 is the sample at y = -4 m -- the collapsed
    apex -- where the no-slip solution is u == 0 exactly.  A correctly sized
    plant placed there is ABOVE the profile minimum, min() returns the same
    number, and the reader moves by EXACTLY ZERO.  That is not a broken reader;
    it is a plant outside the reader's support, and it cost this team two
    NOT A RESULT rows on the parent case.

    At the argmin row a NEGATIVE plant makes that row the minimum by exactly
    |plant|, so the read moves by EXACTLY |plant| -- which is > 0.1*|plant| for
    any non-zero plant, BY CONSTRUCTION and independently of the data.  The
    threshold rule is carried CHARACTER FOR CHARACTER from the parent; the
    repair is the LOCATION, never a loosened test."""
    if plant >= 0:
        refuse("P1", "_perturb_at_argmin was handed a non-negative plant (%r); a min() "
                     "reader is driven DOWNWARD or not at all (L-347)" % plant)
    lines = open(path, errors="replace").read().rstrip("\n").split("\n")
    idx = _argmin_row(path)
    data = _data_line_indices(lines)
    if idx >= len(data):
        refuse("P2", "argmin row %d is beyond the %d data rows of %s" % (idx, len(data), path))
    i = data[idx]
    parts = lines[i].split()
    parts[1] = repr(float(parts[1]) + plant * U_WALL)   # the file is RAW u_x
    lines[i] = "\t".join(parts)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return i


def _perturb_row_zero(path, plant):
    """THE PARENT'S DEFECTIVE PLACEMENT, preserved OFF the grading path so
    umin_placement_control() can show it FAILING on real bytes.  Nothing in the
    verdict path calls this."""
    lines = open(path, errors="replace").read().rstrip("\n").split("\n")
    data = _data_line_indices(lines)
    if not data:
        refuse("P3", "no data row in " + path)
    i = data[0]
    parts = lines[i].split()
    parts[1] = repr(float(parts[1]) + plant * U_WALL)
    lines[i] = "\t".join(parts)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return i


def _perturb_all_rows(path, plant):
    """THE L-340 REPAIR: an AVERAGING reader is moved by moving every row it
    averages over.  Sized by rms_plant_for()."""
    lines = open(path, errors="replace").read().rstrip("\n").split("\n")
    data = _data_line_indices(lines)
    if not data:
        refuse("P4", "no data row in " + path)
    for i in data:
        parts = lines[i].split()
        parts[1] = repr(float(parts[1]) + plant * U_WALL)
        lines[i] = "\t".join(parts)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(data)


def _one_plant(src, channel, reader, exit_on_fail=True):
    """Run ONE channel's plant on a COPY of the real artifact and REPORT.

    The run tree is NEVER modified.  `exit_on_fail=False` is L-347 clause 2: the
    caller collects every channel and refuses ONCE with all of them printed, so
    no control can hide behind another control's refusal."""
    d = tempfile.mkdtemp(prefix="vmflgpu003plant_")
    try:
        work = os.path.join(d, "bisect_U.xy")
        shutil.copyfile(src, work)
        base = reader(work)
        if channel == "u_min_norm":
            plant = UMIN_PLANT
            where = _perturb_at_argmin(work, plant)
            placement = "argmin row (file line %d)" % where
        elif channel == "rms_vs_benchmark":
            plant = rms_plant_for(base)
            n = _perturb_all_rows(work, plant)
            placement = "all %d data rows (averaging reader, L-340 sizing)" % n
        else:
            refuse("P5", "unknown planted-zero channel %r" % channel)
        after = reader(work)
        delta = abs(after - base)
        threshold = PLANT_MIN_GAIN * abs(plant)
        rec = dict(channel=channel, artifact=src, base=base, planted=plant,
                   placement=placement, after=after, delta=delta,
                   threshold=threshold, passed=bool(delta > threshold))
        if not rec["passed"]:
            rec["message"] = (
                "planted-zero control FAILED for %s.\n"
                "  planted %g into %s at the %s, reader moved by only %g "
                "(threshold %g).\n"
                "  A reader not shown able to see a non-zero cannot certify a zero "
                "(CLAUDE.md rule 3)." % (channel, plant, src, placement, delta, threshold))
            if exit_on_fail:
                sys.stderr.write("REFUSING (exit 2): %s\n" % rec["message"])
                sys.exit(2)
        return rec
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _plant_negative_arm(src, reader):
    """The NEGATIVE arm of rule 3: the same reader, on an UNPLANTED copy, must
    report NO movement.  A reader that reports a move where none was planted is
    as useless as one that misses a real one."""
    d = tempfile.mkdtemp(prefix="vmflgpu003neg_")
    try:
        work = os.path.join(d, "bisect_U.xy")
        shutil.copyfile(src, work)                      # copied, NOT planted
        return abs(reader(work) - reader(src)) == 0.0
    finally:
        shutil.rmtree(d, ignore_errors=True)


def planted_zero_control(level_dir, readers=None):
    """CLAUDE.md rule 3, PER CHANNEL, SIZED PER CHANNEL, PLACED PER READER.

    EVERY CHANNEL RUNS AND IS REPORTED BEFORE ANY EXIT (L-347 clause 2).

    Falls through to refuse() on every path that is not a pass: the ONLY way
    this returns is with the plant seen on EVERY channel.

    `readers` exists so the selftest can drive the REFUSAL PATH with a
    deliberately BLIND reader -- one that returns the pre-plant value whatever is
    on disk.  Without it, deleting the refusal below would be invisible to the
    selftest."""
    readers = readers or READERS
    src = _xy_at_endtime(level_dir)
    recs = [_one_plant(src, ch, readers[ch], exit_on_fail=False) for ch in CHANNELS]
    for rec in recs:
        print("  PLANT %s: base %.10g -> %.10g, delta %.6g, threshold %.6g, at %s -- %s"
              % (rec["channel"], rec["base"], rec["after"], rec["delta"],
                 rec["threshold"], rec["placement"],
                 "SEEN" if rec["passed"] else "NOT SEEN"))
    failed = [r for r in recs if not r["passed"]]
    if failed:
        refuse("P6", "the planted-zero control FAILED on %d of %d channels; every "
                     "channel was run and is printed above (L-347 clause 2).\n%s"
               % (len(failed), len(recs), "\n".join(f["message"] for f in failed)))
    for ch in CHANNELS:
        if not _plant_negative_arm(src, readers[ch]):
            refuse("P7", "NEGATIVE ARM: reader %s reports movement on an UNPLANTED copy "
                         "of %s -- it is not reading the file it thinks it is" % (ch, src))
    if len(recs) != len(CHANNELS):
        refuse("P8", "the planted-zero control did not complete every gate channel: "
                     "%d of %d" % (len(recs), len(CHANNELS)))
    # Reached, and this structure returned, ONLY when every channel saw its plant
    # AND the negative arm was silent on every channel.
    return dict(artifact=src, channels=len(recs),
                per_channel={r["channel"]: {k: r[k] for k in
                                            ("base", "planted", "after", "delta",
                                             "threshold", "placement", "passed")}
                             for r in recs},
                negative_arm="silent on every channel", passed=True)
    refuse("P9-FALLTHROUGH", "planted-zero control did not reach a verdict")


def umin_placement_control(level_dir):
    """L-347, DRIVEN ON THE REAL BYTES OF THIS RUN, not on a fixture.

    The parent's row-0 placement must STILL FAIL on this artifact, and the
    argmin placement must PASS and move the reader by EXACTLY |plant|.  If the
    argmin happens to BE row 0, the discriminator is degenerate and this control
    says so rather than reporting a pass it did not earn."""
    src = _xy_at_endtime(level_dir)
    argmin_idx = _argmin_row(src)
    d = tempfile.mkdtemp(prefix="vmflgpu003place_")
    try:
        work = os.path.join(d, "bisect_U.xy")
        shutil.copyfile(src, work)
        base = _read_umin(work)
        _perturb_row_zero(work, UMIN_PLANT)
        row0_delta = abs(_read_umin(work) - base)
        shutil.copyfile(src, work)
        _perturb_at_argmin(work, UMIN_PLANT)
        argmin_delta = abs(_read_umin(work) - base)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    theory = abs(UMIN_PLANT)
    if abs(argmin_delta - theory) > 1e-12:
        refuse("P10", "the argmin placement moved the reader by %g, not by the |plant| "
                      "the construction requires (%g). The repair is not doing what it "
                      "claims." % (argmin_delta, theory))
    degenerate = (argmin_idx == 0)
    if degenerate:
        warn_infra("L-347 DISCRIMINATOR DEGENERATE: the argmin IS row 0 on this "
                   "artifact, so the parent's placement and the repaired one coincide. "
                   "The argmin arm still passed by construction; the row-0 arm proves "
                   "nothing here and is NOT reported as a discriminator.")
    elif not row0_delta <= PLANT_MIN_GAIN * theory:
        warn_infra("L-347 DISCRIMINATOR: the parent's row-0 placement moved this "
                   "artifact's reader by %g, which is NOT below the threshold %g. The "
                   "argmin arm passed on its own construction; this arm simply does not "
                   "discriminate on these bytes." % (row0_delta, PLANT_MIN_GAIN * theory))
    else:
        print("  L-347 DRIVEN ON THIS RUN'S OWN BYTES: the parent's row-0 placement "
              "moves the min() reader by %.6g (<= threshold %.6g, it would REFUSE); the "
              "argmin placement moves it by %.6g == |plant| exactly. Argmin row index "
              "%d." % (row0_delta, PLANT_MIN_GAIN * theory, argmin_delta, argmin_idx))
    return dict(argmin_row=argmin_idx, row0_delta=row0_delta,
                argmin_delta=argmin_delta, theory=theory, degenerate=degenerate)


# ---------------------------------------------------------------------------
# strict completion (CLAUDE.md rule 4).  PHYSICS-CRITICAL, except clause 5b.
# ---------------------------------------------------------------------------
def _read_kv(path):
    """Tolerant `key = value` / `key=value` parse; unreadable -> {}.  Callers
    default to the REFUSING value."""
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


RULE4_OTHER_FOUR = ("end_line", "last_time_is_endtime", "fields_present", "age_guard")


def rrc_classify(rc_record_present, other_four):
    """R-RC AS A PURE RULE, so it can be unit-driven instead of only inferred
    from control flow.

    Sanaa's desk ruling of 2026-08-27T16:54Z, verbatim: "rc value is physics, rc
    record is infrastructure; absent record -> NOT MEASURED only when the other
    four rule-4 conditions hold."

    Returns "MEASURED", "NOT MEASURED", or "REFUSE".  The conjunction is the
    whole content of the rule: without it, "the rc record is missing" would be a
    blanket pass.  Every one of the sixteen input combinations is driven by
    --selftest, so an edit that turns the conjunction into a constant is caught
    by a test rather than by a reader's attention."""
    if set(other_four) != set(RULE4_OTHER_FOUR):
        return "REFUSE"
    if rc_record_present:
        return "MEASURED"
    if all(bool(other_four[k]) for k in RULE4_OTHER_FOUR):
        return "NOT MEASURED"
    return "REFUSE"


def strict_completion(level_dir):
    """Returns a dict.  `rc_status` is one of 'MEASURED' or 'NOT MEASURED'.

    L-342: a MISSING RUN_RC does NOT void the run.  rc is reported NOT MEASURED,
    the physics is still read and printed, and the caller votes NOT A RESULT.  A
    PRESENT and NON-ZERO rc is an incomplete run and refuses."""
    name = os.path.basename(level_dir)
    endtime = ENDTIME_BY_LEVEL[name]
    if not os.path.isdir(level_dir):
        refuse("C0", "%s: run directory does not exist" % level_dir)

    arm_name = os.path.basename(os.path.dirname(level_dir))
    run_root_here = os.path.dirname(os.path.dirname(level_dir))
    rc_candidates = [os.path.join(run_root_here, "RUN_RC.%s.%s" % (name, arm_name)),
                     os.path.join(level_dir, "RUN_RC.txt")]
    rc_path = next((p for p in rc_candidates if os.path.isfile(p)), rc_candidates[0])
    rc_status, rc = "MEASURED", None
    rc_record_present = os.path.isfile(rc_path)
    if not rc_record_present:
        # R-RC (Sanaa's desk ruling, 2026-08-27T16:54Z, verbatim: "rc value is
        # physics, rc record is infrastructure; absent record -> NOT MEASURED
        # only when the other four rule-4 conditions hold").
        #
        # The CLASSIFICATION IS DEFERRED to the foot of this function, where the
        # conjunction is written out and checked explicitly.  It is NOT granted
        # here, because "the rc record is missing" must never become a blanket
        # pass: the other four conditions -- End line, last time == endTime,
        # fields present at endTime, age guard -- have not been read yet at this
        # point in the function, and a classification made before its own
        # premises is not a classification.
        warn_infra("%s/%s: neither RUN_RC.%s.%s at the run root nor RUN_RC.txt beside "
                   "the level is present. The rc RECORD is INFRASTRUCTURE (R-RC); the "
                   "rc VALUE is physics. Whether this becomes NOT MEASURED is decided "
                   "at the foot of the completion check, and only if the other four "
                   "rule-4 conditions hold." % (arm_name, name, name, arm_name))
    else:
        rcd = _read_kv(rc_path)
        raw = rcd.get("rc", "1")          # FAIL-SAFE default: the refusing value
        try:
            rc = int(raw)
        except ValueError:
            refuse("C1", "%s: RUN_RC carries an unparseable rc %r" % (name, raw))
        if rc != 0:
            refuse("C2", "%s/%s: solver rc = %d (strict completion clause 1). A non-zero "
                         "rc is a FINDING, not a retry." % (arm_name, name, rc))

    logp = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.isfile(logp):
        refuse("C3", "%s/%s: no log.simpleFoam" % (arm_name, name))
    text = open(logp, errors="replace").read()
    if not re.search(r"^End\b", text, re.M):
        refuse("C4", "%s/%s: no 'End' line in log.simpleFoam (clause 2)" % (arm_name, name))

    times = _time_dirs(level_dir)
    if not times or float(times[-1]) != float(endtime):
        refuse("C5", "%s/%s: last time is %r, the registered endTime is %d (clause 3)"
               % (arm_name, name, times[-1] if times else None, endtime))

    for f in FIELDS_AT_ENDTIME:
        if _resolve(os.path.join(level_dir, times[-1], f)) is None:
            refuse("C6", "%s/%s: field %s missing at endTime (clause 4) -- neither %s "
                         "nor %s.gz" % (arm_name, name, f, f, f))

    # ---- clause 5a: PHYSICS-CRITICAL.  The SOLVER'S OWN TIME LINE COUNT. ----
    n_time = len(re.findall(r"^Time = ", text, re.M))
    if n_time != endtime:
        refuse("C7", "%s/%s: %d `Time =` lines, the registered endTime is %d (clause 5). "
                     "The solver did not take the registered number of outer iterations, "
                     "and both arms taking the SAME number is what makes limb B a "
                     "statement about the linear algebra." % (arm_name, name, n_time, endtime))

    # ---- clause 5b: INFRASTRUCTURE.  A TIMING-LINE COUNT IS BOOKKEEPING. ----
    # MEASURED on this instance on VMFLGPU002's own completed L1 log: 1200
    # `Time =` lines and 1202 `ExecutionTime` lines at endTime = 1200.  petsc4Foam
    # prints endTime + 2 timing lines.  VMFLGPU001 froze this count as
    # physics-critical and has no verdict as a result (commit 59110074).  It is
    # recorded here and it NEVER refuses.
    n_exec = len(re.findall(r"^ExecutionTime", text, re.M))
    exec_note = "as expected for petsc4Foam (endTime + 2)"
    if n_exec != endtime + 2:
        warn_infra("%s/%s: %d ExecutionTime lines against endTime %d (expected %d for "
                   "petsc4Foam). A TIMING-LINE COUNT IS BOOKKEEPING (L-342): it is "
                   "recorded, it does not refuse, and it cannot void the physics."
                   % (arm_name, name, n_exec, endtime, endtime + 2))
        exec_note = "ANOMALOUS -- recorded, not refused (L-342)"

    marker = _resolve(os.path.join(level_dir, "0", "U"))
    if marker is None:
        refuse("C8", "%s/%s: no 0/U age-guard marker (clause 6)" % (arm_name, name))
    m_mtime = os.path.getmtime(marker)
    for f in FIELDS_AT_ENDTIME:
        fp = _resolve(os.path.join(level_dir, times[-1], f))
        if os.path.getmtime(fp) <= m_mtime:
            refuse("C9", "%s/%s: %s/%s is NOT newer than 0/U -- AGE GUARD (clause 6). The "
                         "field did not come from this run." % (arm_name, name, times[-1], f))
    # ---- R-RC, THE CONJUNCTION, WRITTEN OUT --------------------------------
    # Reaching this line means every one of the other four rule-4 conditions was
    # read and HELD: clause 2 (the End line), clause 3 (last time == endTime),
    # clause 4 (the declared fields at endTime) and clause 6 (the age guard)
    # each REFUSE above rather than returning, so their holding is what execution
    # here means.  The conjunction is nevertheless recomputed and stated, so a
    # reader can see the premises rather than infer them from control flow, and
    # so the selftest can drive each one failing.
    other_four = dict(end_line=bool(re.search(r"^End\b", text, re.M)),
                      last_time_is_endtime=(bool(times) and float(times[-1]) == float(endtime)),
                      fields_present=all(_resolve(os.path.join(level_dir, times[-1], f))
                                         is not None for f in FIELDS_AT_ENDTIME),
                      age_guard=all(os.path.getmtime(_resolve(os.path.join(level_dir,
                                    times[-1], f))) > m_mtime for f in FIELDS_AT_ENDTIME))
    if not rc_record_present:
        if rrc_classify(rc_record_present, other_four) == "NOT MEASURED":
            rc_status = "NOT MEASURED"
            warn_infra("%s/%s: rc record ABSENT and the other four rule-4 conditions ALL "
                       "HOLD (%s) -- R-RC: the rc is NOT MEASURED, this level cannot be a "
                       "PASS, and the physics artifacts are read and printed. A "
                       "bookkeeping failure invalidates the bookkeeping, never the "
                       "physics (L-342)."
                       % (arm_name, name, ", ".join(sorted(other_four))))
        else:
            refuse("C10", "%s/%s: the rc record is ABSENT and the other four rule-4 "
                          "conditions do NOT all hold (%s). R-RC grants NOT MEASURED only "
                          "under that conjunction; without it, 'the rc record is missing' "
                          "would be a blanket pass, and it is not."
                   % (arm_name, name, other_four))
    return dict(level=name, arm=arm_name, rc=rc, rc_status=rc_status,
                rc_record_present=rc_record_present, other_four_rule4=other_four,
                rc_source=(rc_path if rc_status == "MEASURED" else None),
                endtime=endtime, latest_time=times[-1], time_lines=n_time,
                execution_lines=n_exec, execution_lines_class="INFRASTRUCTURE",
                execution_lines_note=exec_note, completed=True)


def mesh_birth_certificate(level_dir):
    """PHYSICS-CRITICAL: a mesh is born clean or it does not enter."""
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
# iterative convergence: residuals AND the GATE QUANTITY'S OWN plateau
# ---------------------------------------------------------------------------
def residual_history(level_dir):
    text = open(os.path.join(level_dir, "log.simpleFoam"), errors="replace").read()
    hist = {}
    for fld, val in RES_RE.findall(text):
        try:
            hist.setdefault(fld, []).append(float(val))
        except ValueError:
            continue
    return hist


def umin_series(level_dir, override=None):
    """[(iteration, u_min_norm)] over the WHOLE run, from the SAME function
    object the gate is read from.  This is the gate quantity's own history.

    `override` maps an iteration to a SUBSTITUTE file, so a control can plant
    into one iteration WITHOUT EVER WRITING INTO THE RUN TREE."""
    dirs = dict(_bisector_dirs(level_dir))
    if override:
        dirs.update(override)
    return [(t, _read_umin(dirs[t])) for t in sorted(dirs)]


def _window_ptp(vals):
    w = vals[-PLATEAU_WINDOW:]
    return max(w) - min(w)


def plateau_plant_control(level_dir, perturb=None):
    """CLAUDE.md rule 3 ON THE PLATEAU CHANNEL, placed where the ptp reader
    looks (L-347), because the plateau clause is a gate clause: it can turn a
    graded row into NOT A RESULT, and a clause that can do that must be shown
    able to see a non-zero.

    A peak-to-peak reader selects the window's EXTREME iterations.  So the plant
    goes into the iteration carrying the window MAXIMUM, raised by |plant|:
    the window maximum then rises by exactly |plant| and the minimum is
    unchanged (or, on a perfectly flat window, the range becomes exactly
    |plant|).  Either way the read moves by |plant| BY CONSTRUCTION, for any
    data -- the placement is the repair, never a loosened threshold.

    THE RUN TREE IS NEVER MODIFIED: the plant goes into a temporary copy that is
    substituted for that one iteration through umin_series's override.

    `perturb` exists so the selftest can drive this control's REFUSAL PATH with a
    deliberately INERT plant -- one that writes nothing.  Without it, deleting
    the refusal below would be invisible to the selftest, which is the defect
    this family keeps paying for."""
    perturb = perturb or _perturb_all_rows
    ser = umin_series(level_dir)
    if len(ser) < PLATEAU_MIN:
        refuse("PP1", "%s: only %d plateau samples -- the plateau plant cannot be placed "
                      "in a window that does not exist" % (os.path.basename(level_dir), len(ser)))
    vals = [v for (_, v) in ser]
    base_ptp = _window_ptp(vals)
    window = ser[-PLATEAU_WINDOW:]
    t_star = max(window, key=lambda tv: tv[1])[0]
    src = dict(_bisector_dirs(level_dir))[t_star]
    plant = abs(UMIN_PLANT)
    d = tempfile.mkdtemp(prefix="vmflgpu003pplant_")
    try:
        work = os.path.join(d, "bisect_U.xy")
        shutil.copyfile(src, work)
        perturb(work, plant)
        after_ptp = _window_ptp([v for (_, v) in umin_series(level_dir, override={t_star: work})])
    finally:
        shutil.rmtree(d, ignore_errors=True)
    delta = abs(after_ptp - base_ptp)
    threshold = PLANT_MIN_GAIN * plant
    if not delta > threshold:
        refuse("PP2", "PLATEAU PLANT control FAILED at %s: %g planted into iteration %g "
                      "-- the window's MAXIMUM, the row a peak-to-peak reader selects -- "
                      "moved the plateau statistic by only %g (threshold %g). The plateau "
                      "clause can vote a row NOT A RESULT; a clause not shown able to see "
                      "a non-zero cannot be allowed to do that (rule 3, L-347)."
               % (os.path.basename(level_dir), plant, t_star, delta, threshold))
    print("  PLATEAU PLANT SEEN at %s: %g planted at iteration %g (the window MAXIMUM, "
          "where a peak-to-peak reader looks) moved ptp %g -> %g, delta %g > threshold %g"
          % (os.path.basename(level_dir), plant, t_star, base_ptp, after_ptp, delta, threshold))
    return dict(level=os.path.basename(level_dir), planted=plant, at_iteration=t_star,
                ptp_before=base_ptp, ptp_after=after_ptp, delta=delta,
                threshold=threshold, placement="window maximum (L-347)", passed=True)
    refuse("PP3-FALLTHROUGH", "the plateau plant control did not reach a verdict")


def iterative_convergence(level_dir, series=None):
    name = os.path.basename(level_dir)
    hist = residual_history(level_dir)
    finals = {}
    for fld in ("Ux", "Uy", "p"):
        if fld not in hist or not hist[fld]:
            refuse("I2", "%s: no residual history for %s" % (name, fld))
        finals[fld] = hist[fld][-1]
    bad = {k: v for k, v in finals.items() if not v < RESID_FLOOR}
    if bad:
        refuse("I3", "%s: final initial residual(s) %s are not below %g -- the level is "
                     "not iteratively converged (rule 5 step 1). Its registered endTime "
                     "(%d) carried a margin of %.1fx on the parent's MEASURED convergence "
                     "point for this level; that margin did not hold here, and that is a "
                     "finding, not a reason to extend the run."
               % (name, bad, RESID_FLOOR, ENDTIME_BY_LEVEL[name],
                  ENDTIME_BY_LEVEL[name] / float(PARENT_CONVERGED_AT[name])))

    ser = series if series is not None else umin_series(level_dir)
    vals = [v for (_, v) in ser]
    n_avail = len(vals)
    if n_avail < PLATEAU_MIN:
        refuse("I4", "%s: %d plateau samples < the registered minimum %d -- CANNOT_TELL, "
                     "never a pass" % (name, n_avail, PLATEAU_MIN))
    ptp = _window_ptp(vals)
    full_ptp = max(vals) - min(vals)
    null_range_resolved = None
    if ptp == 0.0:
        # THE NULL-RANGE RULE, registered before compute.  A dead channel and a
        # perfectly converged one are separated by EVIDENCE FROM THE SAME RUN,
        # not conflated by a tolerance.
        if not full_ptp > PLATEAU_ALIVE_MIN:
            refuse("I5", "%s: the plateau window has NULL RANGE (peak-to-peak exactly 0 "
                         "over %d samples) AND the channel's FULL history moved by only "
                         "%g, which is not above the registered aliveness floor %g. A "
                         "dead channel and a perfectly converged one look identical to a "
                         "tolerance, and this one has not been shown to be alive."
                   % (name, PLATEAU_WINDOW, full_ptp, PLATEAU_ALIVE_MIN))
        null_range_resolved = (
            "window peak-to-peak is exactly 0 over %d samples AND the same channel moved "
            "by %g over the full history (> %g): the channel is ALIVE and the window is "
            "PERFECTLY converged, which is the distinction a bare null-range refusal "
            "cannot make" % (PLATEAU_WINDOW, full_ptp, PLATEAU_ALIVE_MIN))
        print("  NULL RANGE RESOLVED at %s: %s" % (name, null_range_resolved))
    elif not ptp < PLATEAU_TOL:
        refuse("I6", "%s: plateau peak-to-peak %g m/s in u_min over the last %d samples "
                     "is not below %g -- not plateaued (rule 5 step 1)"
               % (name, ptp, PLATEAU_WINDOW, PLATEAU_TOL))
    return dict(level=name, final_residuals=finals, residual_tol=RESID_FLOOR,
                plateau_ptp=ptp, plateau_tol=PLATEAU_TOL, plateau_window=PLATEAU_WINDOW,
                plateau_full_ptp=full_ptp, plateau_alive_min=PLATEAU_ALIVE_MIN,
                null_range_resolved=null_range_resolved,
                n_available=n_avail, converged=True)


# ---------------------------------------------------------------------------
# LIMB A -- GPU EXECUTION.  PHYSICS-CRITICAL for this family.
#
# The three tells are the smoke test's tells, deliberately kept BYTE-FOR-BYTE
# equivalent to VMFLGPU001's and VMFLGPU002's so this comparator and
# smoke_test_gpu_path.sh cannot disagree about what a tell is.  TELL 1 IS LOOSE
# AND CANNOT DISCRIMINATE ON ITS OWN -- PETSc's -log_view prints GPU columns and
# CpuToGpu/GpuToCpu rows on a CUDA-configured build EVEN WHEN THE SOLVE RAN ON
# THE CPU.  THE FORCED-CPU CONTROL IS THE DISCRIMINATOR, and a run graded
# without it is NOT A RESULT.
# ---------------------------------------------------------------------------
def logview_rows(solver_log_text):
    """{event: [(gpu_pctf, cputogpu_count), ...]} from PETSc's -log_view table.

    Parsed positionally from the END of the row, which is where PETSc's own
    legend puts these columns: `... Total_Mflop/s GPU_Mflop/s CpuToGpu_Count
    CpuToGpu_Size GpuToCpu_Count GpuToCpu_Size GPU_%F`.  Anchored on the EVENT
    NAME, never on a line number, and a row that does not parse is skipped
    rather than silently read as a zero -- a zero here is the whole question."""
    out = {e: [] for e in LOGVIEW_EVENTS}
    for ln in solver_log_text.splitlines():
        m = LOGVIEW_ROW_RE.match(ln)
        if not m:
            continue
        f = ln.split()
        if len(f) < 8:
            continue
        try:
            pctf = float(f[-1])
            cpu_to_gpu = float(f[-5])
        except ValueError:
            continue
        out[m.group(1)].append((pctf, cpu_to_gpu))
    return out


def gpu_accounting(solver_log_text):
    """(max GPU %F over the graded events, total CpuToGpu transfer count).

    Returns (None, None) when the -log_view table carries no row for either
    event: an ABSENT accounting is not a zero, and it must not be read as one."""
    rows = logview_rows(solver_log_text)
    seen = [r for e in LOGVIEW_EVENTS for r in rows[e]]
    if not seen:
        return None, None
    return max(r[0] for r in seen), sum(r[1] for r in seen)


def tell1_gpu_flops(solver_log_text):
    """TELL 1 -- PETSc accounts the flops of MatMult and KSPSolve TO THE GPU.

    This is the tell the family's earlier comparators did not have.  It is not
    "a CUDA build printed CUDA words"; it is PETSc's own per-event percentage."""
    pctf, _ = gpu_accounting(solver_log_text)
    return pctf is not None and pctf >= GPU_PCTF_MIN


def tell2_pid_on_gpu(gpusample_text):
    """TELL 2 -- the solver PID holds device memory while it solves.  Sound in
    the earlier comparators and carried unchanged."""
    return bool(re.search(r"\b[0-9]+,\s*[1-9][0-9]*\s*MiB", gpusample_text))


def tell3_host_to_device(solver_log_text):
    """TELL 3 -- matrices and vectors were actually COPIED to the device.

    Replaces the `type: aijcusparse` string match, which this build never
    prints: it echoes -eqn_p_mat_type in the options block only, so the old tell
    false-negatived a genuine GPU run.  A transfer count is a count of work
    done, not a string a build might or might not emit."""
    _, n = gpu_accounting(solver_log_text)
    return n is not None and n > 0


def requested_mat_type(solver_log_text):
    """INFRASTRUCTURE (L-342): what the run ASKED for, from the options echo.
    It records intent, never execution, and it NEVER refuses."""
    m = re.search(r"-eqn_p_mat_type\s+(\S+)", solver_log_text)
    return m.group(1) if m else None


def _arm_artifacts(run_root, arm, level):
    d = os.path.join(run_root, arm, level)
    logp = os.path.join(d, "log.simpleFoam")
    smp = os.path.join(d, "gpusample.txt")
    if not os.path.isfile(logp):
        refuse("A0", "%s/%s: no log.simpleFoam -- limb A cannot be evaluated and limb A "
                     "is PHYSICS-CRITICAL for this family" % (arm, level))
    text = open(logp, errors="replace").read()
    if not os.path.isfile(smp):
        refuse("A1", "%s/%s: no gpusample.txt -- TELL 2 (the solver PID holding device "
                     "memory) cannot be evaluated. This is a PHYSICS-CRITICAL artifact "
                     "for this family, not bookkeeping: it is one of the three tells "
                     "that constitute the object under verification." % (arm, level))
    return text, open(smp, errors="replace").read()


def limb_A(run_root, level):
    """Returns a dict ONLY when limb A holds.  Otherwise it exits 2 -- either as
    a refusal (the control is broken: the row certifies NOTHING) or with the
    verdict NOT A RESULT printed (the solve did not run on the GPU)."""
    gtext, gsamp = _arm_artifacts(run_root, GPU_ARM, level)
    ctext, _csamp = _arm_artifacts(run_root, CPU_ARM, level)

    g_pctf, g_xfer = gpu_accounting(gtext)
    c_pctf, c_xfer = gpu_accounting(ctext)

    if g_pctf is None:
        refuse("A3", "%s: the GPU arm's log carries NO -log_view row for %s. The GPU "
                     "accounting is ABSENT, and an absent accounting is not a zero and "
                     "not a one -- limb A cannot be evaluated, and limb A is what this "
                     "family verifies." % (level, " or ".join(LOGVIEW_EVENTS)))
    if c_pctf is None:
        refuse("A4", "%s: the FORCED-CPU CONTROL's log carries no -log_view row for %s, "
                     "so the control cannot be read and cannot discriminate. The row "
                     "certifies NOTHING." % (level, " or ".join(LOGVIEW_EVENTS)))

    # The control first: if it reports GPU work, the tells cannot tell GPU from
    # CPU on this build and NOTHING downstream means anything.  MEASURED on the
    # real 002 control arm: GPU %F exactly 0, CpuToGpu count exactly 0.
    if c_pctf > CPU_ARM_PCTF_MAX or c_xfer > 0:
        refuse("A2", "%s: the FORCED-CPU CONTROL (mat_type aij, vec_type standard) "
                     "REPORTED GPU WORK: GPU %%F = %g (max allowed %g) over %d "
                     "host-to-device transfers. The tells cannot discriminate GPU from "
                     "CPU on this build, so this row certifies NOTHING. It is NOT A "
                     "RESULT and it is never a PASS."
               % (level, c_pctf, CPU_ARM_PCTF_MAX, int(c_xfer)))

    g1, g2, g3 = tell1_gpu_flops(gtext), tell2_pid_on_gpu(gsamp), tell3_host_to_device(gtext)
    if not (g1 and g2 and g3):
        print("  LIMB A FAILED at %s: gpu_pctF=%s (floor %g) pid_on_gpu=%s "
              "host_to_device_transfers=%s" % (level, g_pctf, GPU_PCTF_MIN, g2, int(g_xfer)))
        print("  The linear solve did NOT provably run on the GPU. A CPU number that "
              "happens to match the reference verifies nothing about the GPU path.")
        print("VERDICT: %s" % checked_verdict("NOT A RESULT"))
        sys.exit(2)

    req_g, req_c = requested_mat_type(gtext), requested_mat_type(ctext)
    if req_g is None or req_c is None:
        warn_infra("%s: the -eqn_p_mat_type options echo is absent from one arm "
                   "(gpu=%r cpu=%r). That echo records what was REQUESTED, never what "
                   "ran; limb A rests on the accounting above." % (level, req_g, req_c))

    return dict(level=level, gpu_pctF=g_pctf, gpu_pctF_floor=GPU_PCTF_MIN,
                host_to_device_transfers=int(g_xfer), tell2_pid_on_gpu=True,
                control_pctF=c_pctf, control_transfers=int(c_xfer),
                forced_cpu_control_discriminated=True,
                requested_mat_type={"gpu": req_g, "cpu": req_c})


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
        out["why"] = ("observed order %g is below the registered floor P_MIN = %g; NO GCI "
                      "IS PRINTED -- a GCI computed from a near-zero order is a number "
                      "with no meaning" % (p, P_MIN))
        return out
    out["state"] = "CONVERGING"
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"
        out["why"] = "r^p - 1 <= 0"
        return out
    if abs(f_fine) <= 0.0:
        out["state"] = "DIVERGENT"
        out["why"] = "the fine value is zero; a relative GCI has no denominator"
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
        refuse("F1", "no LAUNCH_RECORD.txt at %s -- the launch-time freeze verification "
                     "left no record, so there is no evidence the solver ran against the "
                     "committed pre-registration and comparator." % run_root)
    kv = _read_kv(p)
    for k in ("prereg_sha_head", "comparator_sha_head"):
        if not kv.get(k):
            refuse("F2", "LAUNCH_RECORD.txt carries no %s -- the freeze is unproven" % k)
    if kv.get("prereg_sha_head") != kv.get("prereg_sha_disk"):
        refuse("F3", "LAUNCH_RECORD.txt: the pre-registration on disk at launch (%s) was "
                     "NOT the blob at HEAD (%s)"
               % (kv.get("prereg_sha_disk"), kv.get("prereg_sha_head")))
    if kv.get("comparator_sha_head") != kv.get("comparator_sha_disk"):
        refuse("F4", "LAUNCH_RECORD.txt: the comparator on disk at launch (%s) was NOT "
                     "the blob at HEAD (%s)"
               % (kv.get("comparator_sha_disk"), kv.get("comparator_sha_head")))
    if not kv.get("host"):
        warn_infra("LAUNCH_RECORD.txt carries no host line -- bookkeeping only; the "
                   "freeze shas above are what the verdict rests on.")
    return kv


# ---------------------------------------------------------------------------
# the grade
# ---------------------------------------------------------------------------
def grade(run_root, out_json=None):
    print("%s -- GPU SOLVER PATH on the lid-driven TRIANGULAR CAVITY (manual p.%s, CPU "
          "parent %s)" % (CASE, MANUAL_PAGE, CPU_PARENT))
    print("  tier ceiling %s (a code-to-code benchmark reference buys NEITHER V NOR P; "
          "this case CANNOT earn PASS)" % TIER_CEILING)
    rec = dict(case=CASE, manual_page=MANUAL_PAGE, cpu_parent=CPU_PARENT,
               tier_ceiling=TIER_CEILING, tol_A="binary", tol_B=TOL_B, band_rms=BAND_RMS,
               reference_kind=REF_KIND, levels={}, infrastructure={})

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
            vals, path = gate_values(d)
            lrec[arm] = dict(mesh=mesh, completion=comp, convergence=conv,
                             gate=vals, gate_artifact=path)
            if arm == GPU_ARM:
                gpu_gate[lvl] = vals
            else:
                cpu_gate[lvl] = vals
        lrec["limb_A"] = limb_A(run_root, lvl)
        print("  LIMB A HELD at %s: three tells fired on the GPU arm and the forced-CPU "
              "control showed GPU-ABSENT" % lvl)
        rec["levels"][lvl] = lrec

    fine = LEVELS[-1]
    fine_gpu_dir = os.path.join(run_root, GPU_ARM, fine)
    rec["planted_zero"] = planted_zero_control(fine_gpu_dir)
    print("  PLANT SEEN ON ALL %d GATE CHANNELS, each placed where ITS reader looks "
          "(L-347) and sized to ITS reader (L-340); negative arm silent on both"
          % rec["planted_zero"]["channels"])
    rec["l347_placement_control"] = umin_placement_control(fine_gpu_dir)
    rec["plateau_plant_control"] = plateau_plant_control(fine_gpu_dir)

    # ---- limb B, BOTH channels, at EVERY level -----------------------------
    limb_b, b_worst, b_worst_where = {}, 0.0, None
    for lvl in LEVELS:
        limb_b[lvl] = {}
        for ch in CHANNELS:
            g, c = gpu_gate[lvl][ch], cpu_gate[lvl][ch]
            if abs(c) <= 0.0:
                refuse("B3", "%s: the forced-CPU arm reports %s = 0; the limb-B ratio has "
                             "no denominator" % (lvl, ch))
            rel = abs(g - c) / abs(c)
            limb_b[lvl][ch] = rel
            if rel > b_worst:
                b_worst, b_worst_where = rel, "%s/%s" % (lvl, ch)
    rec["limb_B"] = dict(rel=limb_b, worst=b_worst, worst_at=b_worst_where, tol=TOL_B)
    limb_b_ok = b_worst <= TOL_B

    # ---- limb C, at the finest level, against the NUMERICAL BENCHMARK ------
    c_value = gpu_gate[fine]["rms_vs_benchmark"]
    rec["limb_C"] = dict(rms=c_value, band=BAND_RMS, at=fine,
                         reference_kind=REF_KIND,
                         reference_source="Jyotsna & Vanka, J. Comp. Phys. 122, 107-117 "
                                          "(1995), via the digitised curve in "
                                          "reference/vmfl011_benchmark_xnorm.csv; the "
                                          "manual prints Figure .gpu003.2 and no table")
    limb_c_ok = c_value <= BAND_RMS

    # ---- Roache triple on the GPU arm, on u_min_norm ------------------------
    triple = [gpu_gate[l]["u_min_norm"] for l in LEVELS]
    rch = roache(triple[0], triple[1], triple[2])
    rec["roache"] = rch
    rec["triple_values"] = triple
    rec["triple_channel"] = "u_min_norm"

    print("  u_min_norm(GPU) L1/L2/L3 = %s" % ["%.10g" % gpu_gate[l]["u_min_norm"] for l in LEVELS])
    print("  u_min_norm(CPU) L1/L2/L3 = %s" % ["%.10g" % cpu_gate[l]["u_min_norm"] for l in LEVELS])
    print("  rms_vs_benchmark(GPU) L1/L2/L3 = %s"
          % ["%.6g" % gpu_gate[l]["rms_vs_benchmark"] for l in LEVELS])
    print("  limb B worst |GPU-CPU|/|CPU| = %.3g at %s (tol %g)"
          % (b_worst, b_worst_where, TOL_B))
    print("  limb C rms_vs_benchmark at %s = %.6g (band %g, %s)"
          % (fine, c_value, BAND_RMS, "INSIDE" if limb_c_ok else "OUTSIDE"))
    print("  reference kind: %s" % REF_KIND)
    print("  triple u_min_norm = %s ; state=%s R=%s p=%s"
          % (["%.10g" % t for t in triple], rch["state"],
             None if rch["R"] is None else "%.6g" % rch["R"],
             None if rch["p"] is None else "%.6g" % rch["p"]))

    # ---- the verdict, in rule 5's order ------------------------------------
    if rc_not_measured:
        verdict = checked_verdict("NOT A RESULT")
        print("  rc is NOT MEASURED for %s -- a PHYSICS-CRITICAL field is absent, so this "
              "cannot be a PASS. The physics above is printed and stands as an artifact; "
              "the bookkeeping failure did not void it (L-342)." % ", ".join(rc_not_measured))
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
        print("  LIMB C MISSED: the physics band against the digitised Jyotsna & Vanka "
              "benchmark was not met. Limb B held, so the GPU path reproduced the lab's "
              "own CPU answer; the miss is against the benchmark, not between the arms.")
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
FIX_HISTORY = 800           # synthetic iterations written per level-arm
FIX_NPTS = 101              # profile points in EVERY synthetic profile.  The
                            # SAME count at every iteration, including endTime:
                            # two different sample counts interpolate the same
                            # curve to two slightly different minima, and the
                            # plateau would then measure the fixture, not the
                            # solution.


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def _synth_profile(scale, npts):
    """A synthetic bisector profile: y from -4 to 0, in the file's RAW units
    (u_x, not u_x/U_WALL), shaped like THE BENCHMARK ITSELF times `scale`.

    Two properties are deliberate, and both matter to what the selftest can
    prove:

      * shaping it on the benchmark means `scale` controls BOTH gate channels in
        a way the selftest can predict -- u_min_norm = scale * min(benchmark),
        and rms_vs_benchmark = |scale - 1| * ||benchmark||.  A fixture whose
        profile has nothing to do with the reference can only ever drive the
        GATE FAIL branch of limb C, never the in-band one.
      * row 0 -- the cavity apex, y = -4 -- is forced to EXACTLY ZERO, which is
        what the no-slip solution gives there and what the real bisector
        carries.  That is the exact geometry that defeated the parent's row-0
        plant (L-347), and the fixture keeps it rather than smoothing it away."""
    by, bv = _bench()
    rows = []
    for i in range(npts):
        y = -4.0 + 4.0 * i / (npts - 1)
        u = 0.0 if i == 0 else scale * _interp(by, bv, y) * U_WALL
        rows.append("%.12g\t%.12g\t0\t0" % (y, u))
    return "\n".join(rows) + "\n"


def _build_level(root, arm, level, *, gpu_tells=True, end_line=True, with_rc=True,
                 scale=1.0, gpusample=True, history=FIX_HISTORY, dead=False,
                 time_lines=None, exec_offset=2, logview_absent=False):
    d = os.path.join(root, arm, level)
    et = ENDTIME_BY_LEVEL[level]
    _write(os.path.join(d, "log.checkMesh"),
           "Checking geometry...\n    cells: %d\nMesh OK.\n" % CELLS_BY_LEVEL[level])

    n_time = et if time_lines is None else time_lines
    body = []
    for i in range(1, n_time + 1):
        body.append("Time = %d\n" % i)
        r = max(1e-14, 1.0e-3 * math.exp(-24.0 * i / max(1, n_time)))
        for f in ("Ux", "Uy"):
            body.append("PETSc-bcgs:  Solving for %s, Initial residual = %.12g, "
                        "Final residual = 1e-13, No Iterations 2\n" % (f, r))
        body.append("PETSc-cg:  Solving for p, Initial residual = %.12g, Final residual "
                    "= 1e-13, No Iterations 9\n" % r)
        body.append("ExecutionTime = %.2f s  ClockTime = %d s\n" % (0.1 * i, i))
    for _ in range(exec_offset):
        body.append("ExecutionTime = %.2f s  ClockTime = %d s\n" % (0.1 * n_time, n_time))
    if not logview_absent:
        # The two rows below are the MEASURED shapes from VMFLGPU002's own
        # log.simpleFoam on this instance -- the GPU arm's and the forced-CPU
        # arm's, column for column.  A fixture that invents its own layout tests
        # the fixture; this one tests the parser against the real thing.
        if gpu_tells:
            body.append("MatMult            12000 1.0 3.2033e-01 1.0 3.79e+08 1.0 0.0e+00 "
                        "0.0e+00 0.0e+00  0  1  0  0  0   9 95  0  0  0  1184    2834   "
                        "6000 1.73e+02    0 0.00e+00  100\n")
            body.append("KSPSolve            1200 1.0 1.6953e+00 1.0 7.18e+08 1.0 0.0e+00 "
                        "0.0e+00 0.0e+00  2  2  0  0  0 100 100  0  0  0   424     680   "
                        "3601 1.04e+02    2 1.70e-01  100\n")
            body.append("-eqn_p_mat_type aijcusparse # (source: code)\n")
        else:
            body.append("MatMult            12000 1.0 1.5417e-01 1.0 3.79e+08 1.0 0.0e+00 "
                        "0.0e+00 0.0e+00  1  1  0  0  0   5 100  0  0  0  2460       0   "
                        "   0 0.00e+00    0 0.00e+00  0\n")
            body.append("KSPSolve            1200 1.0 3.6272e-01 1.0 7.46e+08 1.0 0.0e+00 "
                        "0.0e+00 0.0e+00  2  2  0  0  0 100 100  0  0  0  2056       0   "
                        "   0 0.00e+00    0 0.00e+00  0\n")
            body.append("-eqn_p_mat_type aij # (source: code)\n")
    if end_line:
        body.append("End\n")
    _write(os.path.join(d, "log.simpleFoam"), "".join(body))

    if gpusample:
        _write(os.path.join(d, "gpusample.txt"),
               "12345, 190 MiB\n" if gpu_tells else "\n")

    # the history: `history` iterations ending exactly at endTime.  The first
    # half moves, the last PLATEAU_WINDOW samples are flat -- so the fixture
    # exercises the aliveness clause rather than sidestepping it.
    first = et - history + 1
    for i in range(first, et + 1):
        k = min(1.0, (i - first) / max(1.0, float(history - PLATEAU_WINDOW)))
        s = scale if dead else scale * (0.5 + 0.5 * k)
        _write(os.path.join(d, "postProcessing", "bisector", str(i), "bisect_U.xy"),
               _synth_profile(s, FIX_NPTS))

    _write(os.path.join(d, "0", "U"), "0/U marker\n")
    _write(os.path.join(d, str(et), "U"), "U at endTime\n")
    _write(os.path.join(d, str(et), "p"), "p at endTime\n")
    old = 1_000_000
    os.utime(os.path.join(d, "0", "U"), (old, old))
    for f in FIELDS_AT_ENDTIME:
        os.utime(os.path.join(d, str(et), f), (old + 100, old + 100))
    if with_rc:
        _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)),
               "rc = 0\nwall_s = 10\n")
    return d


def _build_run(root, *, gpu_tells=True, cpu_leaks_gpu=False, end_line=True, with_rc=True,
               gpusample=True, scales=None, cost=True, history=FIX_HISTORY, dead=False,
               logview_absent=False):
    scales = scales or {l: 1.0 for l in LEVELS}
    for lvl in LEVELS:
        _build_level(root, GPU_ARM, lvl, gpu_tells=gpu_tells, end_line=end_line,
                     with_rc=with_rc, scale=scales[lvl], gpusample=gpusample,
                     history=history, dead=dead, logview_absent=logview_absent)
        _build_level(root, CPU_ARM, lvl, gpu_tells=cpu_leaks_gpu, end_line=end_line,
                     with_rc=with_rc, scale=scales[lvl], gpusample=True,
                     history=history, dead=dead)
    _write(os.path.join(root, "LAUNCH_RECORD.txt"),
           "case = %s\nprereg_sha_head = aaa\nprereg_sha_disk = aaa\n"
           "comparator_sha_head = bbb\ncomparator_sha_disk = bbb\nhead = ccc\n"
           "host = fixture\nlaunched_utc = 1970-01-01T00:00:00Z\n" % CASE)
    if cost:
        _write(os.path.join(root, "COST.txt"), "total_gpu_h = 0.1\ncap_gpu_h = 1.5\n")
    return root


# Registered triples for --drive-verdict, each chosen to land on ONE branch of
# the verdict routing.  The scale multiplies u_min, so the triple is
# (-2*s1, -2*s2, -2*s3) in u_min_norm... at U_WALL = 2 the normalisation makes
# u_min_norm = -s.
DRIVEN_TRIPLES = {
    "no-rc-record": {"L1_20x40": 1.04, "L2_40x80": 1.01, "L3_80x160": 1.0025},
    "converging": {"L1_20x40": 1.04, "L2_40x80": 1.01, "L3_80x160": 1.0025},
    "oscillatory": {"L1_20x40": 1.04, "L2_40x80": 1.00, "L3_80x160": 1.02},
    "stagnant": {"L1_20x40": 1.030, "L2_40x80": 1.020, "L3_80x160": 1.010},
    "below-p-min": {"L1_20x40": 1.0400, "L2_40x80": 1.0100, "L3_80x160": 0.9809},
}


def _build_run_scaled(root, scales, cost=True, with_rc=True):
    return _build_run(root, scales=scales, cost=cost, with_rc=with_rc)


def count_assert_nodes(source):
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def drive_refusal(kind):
    """Drive ONE refusal path.  Called by --selftest under `python3 -O` so the
    refusal is shown to survive the optimiser."""
    tmp = tempfile.mkdtemp(prefix="vmflgpu003drive_")
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
        elif kind == "plateau-plant-inert":
            _build_run(tmp)
            def inert(path, plant):
                return 0
            plateau_plant_control(os.path.join(tmp, GPU_ARM, LEVELS[-1]), perturb=inert)
        elif kind == "logview-absent":
            _build_run(tmp, logview_absent=True)
            grade(tmp)
        elif kind == "limbA-miss":
            _build_run(tmp, gpu_tells=False)
            grade(tmp)
        elif kind == "gpusample":
            _build_run(tmp)
            os.remove(os.path.join(tmp, GPU_ARM, LEVELS[0], "gpusample.txt"))
            grade(tmp)
        elif kind == "short-plateau":
            _build_run(tmp, history=PLATEAU_MIN - 1)
            grade(tmp)
        elif kind == "dead-channel":
            # NULL window range AND a full history that never moved: the channel
            # has not been shown alive, so the null-range rule must REFUSE.
            _build_run(tmp, dead=True)
            grade(tmp)
        elif kind == "time-lines":
            _build_run(tmp)
            d = os.path.join(tmp, GPU_ARM, LEVELS[0])
            _build_level(tmp, GPU_ARM, LEVELS[0],
                         time_lines=ENDTIME_BY_LEVEL[LEVELS[0]] - 1)
            grade(tmp)
        elif kind == "plant-blind":
            _build_run(tmp)
            lvl_dir = os.path.join(tmp, GPU_ARM, LEVELS[-1])
            src = _xy_at_endtime(lvl_dir)
            pristine = {ch: READERS[ch](src) for ch in CHANNELS}

            def blind_for(ch):
                def blind(path):
                    return pristine[ch]
                return blind
            planted_zero_control(lvl_dir, readers={ch: blind_for(ch) for ch in CHANNELS})
        elif kind == "no-benchmark":
            _build_run(tmp)
            saved = _ref_csv()
            bak = saved + ".selftest-bak"
            os.rename(saved, bak)
            try:
                grade(tmp)
            finally:
                os.rename(bak, saved)
        elif kind == "freeze":
            _build_run(tmp)
            _write(os.path.join(tmp, "LAUNCH_RECORD.txt"),
                   "case = %s\nprereg_sha_head = aaa\nprereg_sha_disk = ZZZ\n"
                   "comparator_sha_head = bbb\ncomparator_sha_disk = bbb\n" % CASE)
            grade(tmp)
        else:
            refuse("D0", "unknown --drive-refusal kind %r" % kind)
        print("DRIVE-REFUSAL %s: NO REFUSAL FIRED" % kind)
        sys.exit(0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def drive_verdict(kind):
    """Drive ONE registered VERDICT end to end and print it.  P_MIN, STAGNANT
    and the limb-C band do NOT refuse: they ROUTE.  A floor nobody drives is a
    floor nobody has."""
    if kind not in DRIVEN_TRIPLES:
        refuse("D1", "unknown --drive-verdict kind %r" % kind)
    tmp = tempfile.mkdtemp(prefix="vmflgpu003verd_")
    try:
        _build_run_scaled(tmp, DRIVEN_TRIPLES[kind], with_rc=(kind != "no-rc-record"))
        grade(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _drives_exit2(kind):
    proc = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                           "--drive-refusal", kind], capture_output=True, text=True)
    return proc.returncode == 2


def _drives_verdict(kind, expected, forbid=None, require=None):
    proc = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                           "--drive-verdict", kind], capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    got = [ln.split("VERDICT:", 1)[1].strip()
           for ln in proc.stdout.splitlines() if ln.startswith("VERDICT:")]
    if len(got) != 1 or got[0] != expected:
        return False
    if forbid is not None and forbid in proc.stdout:
        return False
    if require is not None and require not in proc.stdout:
        return False
    return True


def rec_band_is_the_parents():
    """The limb-C band is the parent's frozen constant and the reference is a
    BENCHMARK, not an experiment.  A function rather than a comment, so the
    selftest can execute the claim."""
    return BAND_RMS == 0.030 and "code-to-code" in REF_KIND and TIER_CEILING == "GATE REACHED"


def selftest():
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    print("%s comparator --selftest (NO run data touched)" % CASE)

    src = open(os.path.abspath(__file__)).read()
    chk("no assert carries a guard: this file's AST has zero Assert nodes",
        count_assert_nodes(src) == 0)
    chk("the AST counter is shown able to count a PLANTED assert",
        count_assert_nodes("def f():\n    assert 1 == 1\n") == 1)

    chk("the verdict vocabulary is exactly CLAUDE.md rule 1's",
        VERDICTS == ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"))
    chk("the tier ceiling is GATE REACHED and PASS is unreachable",
        TIER_CEILING == "GATE REACHED" and TIER_CEILING != "PASS")
    chk("the limb-C band is the parent's 0.030 and the reference is code-to-code",
        rec_band_is_the_parents())
    chk("the u_min plant magnitude is the parent's, character for character",
        UMIN_PLANT == -abs(1.234e-03) * 100)
    chk("the plant threshold rule is 0.1 * |plant|, unloosened", PLANT_MIN_GAIN == 0.1)
    chk("r = 2 exactly and the cell counts double twice",
        RATIO == 2.0
        and CELLS_BY_LEVEL["L2_40x80"] == 4 * CELLS_BY_LEVEL["L1_20x40"]
        and CELLS_BY_LEVEL["L3_80x160"] == 4 * CELLS_BY_LEVEL["L2_40x80"])
    # --- R-RC as a rule, driven over ALL SIXTEEN input combinations ---------
    _rrc_ok = True
    for bits in range(16):
        of = {k: bool(bits >> i & 1) for i, k in enumerate(RULE4_OTHER_FOUR)}
        want = "NOT MEASURED" if all(of.values()) else "REFUSE"
        if rrc_classify(False, of) != want:
            _rrc_ok = False
        if rrc_classify(True, of) != "MEASURED":
            _rrc_ok = False
    chk("R-RC as a RULE: over all 16 combinations, an absent rc record is NOT MEASURED "
        "ONLY when all four other rule-4 conditions hold, and REFUSE otherwise; a "
        "present record is always MEASURED", _rrc_ok)
    chk("R-RC refuses an other_four dict that is not the four named conditions -- the "
        "rule cannot be satisfied by a differently-shaped input",
        rrc_classify(False, {"end_line": True}) == "REFUSE")
    chk("R-RC: an ABSENT rc record with the other four rule-4 conditions holding is "
        "NOT MEASURED and routes to NOT A RESULT, never a refusal and never a pass",
        _drives_verdict("no-rc-record", "NOT A RESULT", forbid="VERDICT: GATE REACHED"))
    chk("the registered endTimes carry >= 2x margin on the parent's MEASURED "
        "convergence points %s" % PARENT_CONVERGED_AT,
        all(ENDTIME_BY_LEVEL[l] >= 2 * PARENT_CONVERGED_AT[l] for l in LEVELS))

    # --- the benchmark reference -------------------------------------------
    by, bv = _bench()
    chk("the benchmark reference carries the parent's 46 rows", len(by) == 46)
    chk("the benchmark abscissae span the cavity from the apex (y = -4) to within "
        "0.02 m of the moving wall (y = 0), so the lab profile is never extrapolated",
        abs(by[0] + 4.0) < 1e-9 and -0.02 < by[-1] < 0.0)
    chk("_interp reproduces a node exactly", abs(_interp(by, bv, by[10]) - bv[10]) < 1e-15)
    chk("_interp clamps below the first abscissa rather than extrapolating",
        _interp(by, bv, -99.0) == bv[0])

    # --- the readers, on a synthetic profile with a KNOWN minimum -----------
    tmp = tempfile.mkdtemp(prefix="vmflgpu003st_")
    try:
        p = os.path.join(tmp, "bisect_U.xy")
        _write(p, _synth_profile(1.0, 401))
        umin = _read_umin(p)
        chk("the min() reader finds the benchmark's own minimum on a unit-scaled "
            "fixture (%.6g, to interpolation accuracy)" % min(bv),
            umin < 0.0 and abs(umin - min(bv)) < 1e-3)
        chk("row 0 of the synthetic profile is the identically-zero apex -- the exact "
            "geometry that defeated the parent's plant",
            _rows(p)[0][1] == 0.0)
        chk("the argmin is NOT row 0, so the L-347 discriminator is not degenerate here",
            _argmin_row(p) != 0)

        # L-347: the parent's placement FAILS, the repaired one PASSES.
        q = os.path.join(tmp, "row0.xy")
        shutil.copyfile(p, q)
        _perturb_row_zero(q, UMIN_PLANT)
        d0 = abs(_read_umin(q) - umin)
        chk("L-347: the parent's ROW-0 placement moves the min() reader by <= the "
            "threshold, i.e. it would REFUSE a working reader",
            d0 <= PLANT_MIN_GAIN * abs(UMIN_PLANT))
        shutil.copyfile(p, q)
        _perturb_at_argmin(q, UMIN_PLANT)
        d1 = abs(_read_umin(q) - umin)
        chk("L-347: the ARGMIN placement moves the min() reader by EXACTLY |plant|",
            abs(d1 - abs(UMIN_PLANT)) < 1e-12)
        chk("L-347: and that is 10x the threshold, by construction",
            d1 > PLANT_MIN_GAIN * abs(UMIN_PLANT))
        chk("_perturb_at_argmin REFUSES a non-negative plant",
            subprocess.run([sys.executable, "-c",
                            "import sys;sys.path.insert(0,%r);"
                            "import grade_vmflgpu003 as g;"
                            "g._perturb_at_argmin(%r, 1.0)"
                            % (os.path.dirname(os.path.abspath(__file__)), q)],
                           capture_output=True).returncode == 2)

        # L-340: a point-sized plant CANNOT move the averaging reader; the sized
        # one can.  Measured on these bytes, not asserted.
        rms0 = _read_rms(p)
        shutil.copyfile(p, q)
        _perturb_at_argmin(q, -abs(PLANT))
        chk("L-340: a POINT-sized plant does NOT move the AVERAGING reader past its "
            "threshold -- the dilution is real and is measured here",
            abs(_read_rms(q) - rms0) <= PLANT_MIN_GAIN * abs(PLANT))
        shutil.copyfile(p, q)
        sized = rms_plant_for(rms0)
        _perturb_all_rows(q, sized)
        chk("L-340: the SIZED all-row plant DOES move the averaging reader past its "
            "threshold", abs(_read_rms(q) - rms0) > PLANT_MIN_GAIN * abs(sized))
        chk("the sizing floor makes a plant even for an exact match",
            rms_plant_for(0.0) == RMS_PLANT_K * U_WALL * RMS_PLANT_FLOOR)

        chk("the negative arm is silent on an UNPLANTED copy, for both readers",
            _plant_negative_arm(p, _read_umin) and _plant_negative_arm(p, _read_rms))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- LIMB A, driven on the MEASURED bytes of the 002 run pair ----------
    # These two strings are copied column-for-column from VMFLGPU002's own
    # log.simpleFoam on the GPU instance -- the GPU arm's and the forced-CPU
    # arm's.  The tells are exercised on the real thing, not on a shape this
    # file invented for itself.
    gpu_rows = ("MatMult            12000 1.0 3.2033e-01 1.0 3.79e+08 1.0 0.0e+00 0.0e+00 "
                "0.0e+00  0  1  0  0  0   9 95  0  0  0  1184    2834   6000 1.73e+02    0 "
                "0.00e+00  100\n"
                "KSPSolve            1200 1.0 1.6953e+00 1.0 7.18e+08 1.0 0.0e+00 0.0e+00 "
                "0.0e+00  2  2  0  0  0 100 100  0  0  0   424     680   3601 1.04e+02    2 "
                "1.70e-01  100\n-eqn_p_mat_type aijcusparse # (source: code)\n")
    cpu_rows = ("MatMult            12000 1.0 1.5417e-01 1.0 3.79e+08 1.0 0.0e+00 0.0e+00 "
                "0.0e+00  1  1  0  0  0   5 100  0  0  0  2460       0      0 0.00e+00    0 "
                "0.00e+00  0\n"
                "KSPSolve            1200 1.0 3.6272e-01 1.0 7.46e+08 1.0 0.0e+00 0.0e+00 "
                "0.0e+00  2  2  0  0  0 100 100  0  0  0  2056       0      0 0.00e+00    0 "
                "0.00e+00  0\n-eqn_p_mat_type aij # (source: code)\n")
    chk("the -log_view parser reads GPU %F = 100 and 9601 host-to-device transfers off "
        "the MEASURED GPU-arm rows", gpu_accounting(gpu_rows) == (100.0, 9601.0))
    chk("the same parser reads GPU %F = 0 and ZERO transfers off the MEASURED "
        "forced-CPU rows", gpu_accounting(cpu_rows) == (0.0, 0.0))
    chk("tell 1 fires on the GPU arm and NOT on the forced-CPU arm -- the "
        "discrimination the inherited tell could not make",
        tell1_gpu_flops(gpu_rows) and not tell1_gpu_flops(cpu_rows))
    chk("tell 3 fires on the GPU arm and NOT on the forced-CPU arm",
        tell3_host_to_device(gpu_rows) and not tell3_host_to_device(cpu_rows))
    chk("an ABSENT -log_view table reads as ABSENT, never as a zero",
        gpu_accounting("no petsc table here\n") == (None, None)
        and not tell1_gpu_flops("no petsc table here\n"))
    chk("a FORGED GPU-arm row -- everything but GPU %F, which is 0 -- FAILS tell 1",
        not tell1_gpu_flops(gpu_rows.replace("1.04e+02    2 1.70e-01  100",
                                             "1.04e+02    2 1.70e-01  0")
                                    .replace("1.73e+02    0 0.00e+00  100",
                                             "1.73e+02    0 0.00e+00  0")))
    chk("the requested mat_type is read from the options echo and is INFRASTRUCTURE",
        requested_mat_type(gpu_rows) == "aijcusparse"
        and requested_mat_type(cpu_rows) == "aij")
    chk("the GPU %F floor is a floor below the measured 100 and above the measured 0",
        CPU_ARM_PCTF_MAX < GPU_PCTF_MIN < 100.0 + 1e-9)

    # --- Roache classification ---------------------------------------------
    chk("a monotone halving triple is CONVERGING with p ~ 1",
        roache(1.4, 1.2, 1.1)["state"] == "CONVERGING")
    chk("a sign-changing triple is OSCILLATORY",
        roache(1.04, 1.00, 1.02)["state"] == "OSCILLATORY")
    chk("an equally-spaced triple is STAGNANT and is decided on R BEFORE any p",
        roache(1.0, 1.1, 1.2)["state"] == "STAGNANT"
        and roache(1.0, 1.1, 1.2)["p"] is None)
    chk("a growing triple is DIVERGENT", roache(1.0, 1.2, 1.6)["state"] == "DIVERGENT")
    chk("an identical triple is EXACT", roache(1.0, 1.0, 1.0)["state"] == "EXACT")
    r_low = roache(1.0400, 1.0100, 0.9809)   # R = 0.97 -> p = 0.0440 < P_MIN
    chk("an observed order below P_MIN is BELOW_P_MIN with NO GCI",
        r_low["state"] == "BELOW_P_MIN" and r_low["gci_fine"] is None)

    # --- refusals, DRIVEN under python3 -O ---------------------------------
    for kind, label in (
            ("endline", "a missing End line refuses (clause 2)"),
            ("time-lines", "a `Time =` count != endTime refuses (clause 5, PHYSICS)"),
            ("age-guard", "a field older than 0/U refuses (the age guard)"),
            ("control-leak", "a forced-CPU arm reporting GPU work refuses (limb A control)"),
            ("gpusample", "a missing gpusample.txt refuses (tell 2 is physics-critical)"),
            ("logview-absent", "an ABSENT -log_view accounting refuses, rather than "
                               "being read as a zero"),
            ("short-plateau", "too few plateau samples refuses (CANNOT_TELL, never a pass)"),
            ("dead-channel", "a channel never shown alive refuses on NULL RANGE"),
            ("plant-blind", "a BLIND reader refuses the planted-zero control (rule 3)"),
            ("plateau-plant-inert", "an INERT plateau plant refuses -- the plateau clause "
                                    "can vote NOT A RESULT and must be shown able to see "
                                    "a non-zero"),
            ("no-benchmark", "an absent benchmark reference refuses (limb C has no gate)"),
            ("freeze", "a launch-time freeze mismatch refuses"),
            ("vocabulary", "a verdict outside the fixed vocabulary refuses"),
    ):
        chk("%s -- DRIVEN under python3 -O" % label, _drives_exit2(kind))

    # --- limb A miss ROUTES to NOT A RESULT (it does not refuse silently) ---
    proc = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                           "--drive-refusal", "limbA-miss"], capture_output=True, text=True)
    chk("a FORGED GPU-arm log whose GPU %F is 0 prints VERDICT: NOT A RESULT and exits "
        "2 -- the whole run pair, end to end, under python3 -O",
        proc.returncode == 2 and "VERDICT: NOT A RESULT" in proc.stdout)

    chk("the PLATEAU PLANT control is run and reported inside a full grade",
        _drives_verdict("converging", "GATE REACHED", require="PLATEAU PLANT SEEN"))

    # --- verdict ROUTING, driven end to end --------------------------------
    chk("a CONVERGING triple inside every band reaches the CEILING, never PASS",
        _drives_verdict("converging", "GATE REACHED", forbid="VERDICT: PASS"))
    chk("a NULL window range on a channel SHOWN ALIVE is RESOLVED and graded, not "
        "refused -- the clause that left VMFLGPU001 without a verdict, DRIVEN",
        _drives_verdict("converging", "GATE REACHED", require="NULL RANGE RESOLVED"))
    chk("an OSCILLATORY triple routes to NOT A RESULT with NO GCI printed",
        _drives_verdict("oscillatory", "NOT A RESULT", forbid="GCI_fine"))
    chk("a STAGNANT triple routes to NOT A RESULT with NO GCI printed",
        _drives_verdict("stagnant", "NOT A RESULT", forbid="GCI_fine"))
    chk("a BELOW_P_MIN triple routes to NOT A RESULT with NO GCI printed",
        _drives_verdict("below-p-min", "NOT A RESULT", forbid="GCI_fine"))

    npass = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
    print("SELFTEST %d/%d" % (npass, len(checks)))
    if npass != len(checks):
        sys.exit(1)
    print("SELFTEST PASS")
    sys.exit(0)


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
