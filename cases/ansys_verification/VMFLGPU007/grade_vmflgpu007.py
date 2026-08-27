#!/usr/bin/env python3
"""VMFLGPU007 -- graded comparator.  Turbulent flow with heat transfer over a
backward-facing step; manual p.243; CPU parent VMFL013.

    grade_vmflgpu007.py --run-root <dir>      grade a completed run
    grade_vmflgpu007.py --selftest            drive every guard, exit 0/1
    grade_vmflgpu007.py --drive-refusal <arm> drive ONE refusal path

OBJECT UNDER VERIFICATION: the lab's GPU solver path (OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA on the L4).  NOT Ansys, NOT the turbulence model.

NO `assert` ANYWHERE.  `python3 -O` strips assert statements, so a guard built
on one evaporates exactly when the code is run for speed.  Every refusal below
is an explicit branch reaching refuse().  Driven under both interpreters.

EVERY PLANTED FAILURE ASSERTS THE EXPECTED REFUSAL TEXT, never merely a
non-zero exit (L-357).  That lesson came from this lane: two arms of an earlier
instrument returned rc = 1 and looked like clean refusals while actually being a
NameError crash.  A non-zero exit is not evidence a guard fired.

--------------------------------------------------------------------------
THE GATE, and what each limb may earn (PREREGISTRATION sections 4 and 5):

  LIMB A  GPU EXECUTION -- binary, physics-critical.  PETSc's own -log_view
          per-event accounting: the GPU arm must show GPU %F >= GPU_PCTF_MIN
          and a non-zero host-to-device transfer count; the forced-CPU arm must
          show 0 and 0.  A LEAKING CONTROL REFUSES: if the forced-CPU arm
          reports GPU work the tells cannot discriminate on this build and the
          row certifies nothing.  An ABSENT -log_view table REFUSES; it is
          never read as a zero.

  LIMB B  |q_GPU - q_CPU| / |q_CPU| <= BAND_B at EVERY level.  THIS IS THE
          OBJECT UNDER TEST AND IT IS PASS-CAPABLE: the comparison is made at
          an IDENTICAL mesh with an IDENTICAL scheme, so discretisation error
          cancels on both sides and no grid triple is needed to make the claim.

  LIMB C  The physics band against Vogel & Eaton 1985 (EXPERIMENTAL).
          CEILING: GATE REACHED AT MOST -- never PASS.  Without systematic
          refinement this case cannot claim a discretisation-converged physics
          result and will not pretend to.  The ceiling is hard-coded as
          TIER_CEILING_C and executed by --selftest, so it is a property of the
          instrument and not a sentence in a document.

  A LIMB C MISS WITH LIMB B HOLDING IS A **MODEL** MISS, NOT A GPU-PATH
  FAILURE, and is reported in those words.  Standard k-epsilon under-predicting
  backward-facing-step reattachment is the best-documented deficiency of this
  exact model on this exact flow; it cannot move limb B, which is unaffected by
  turbulence-model bias.

--------------------------------------------------------------------------
NO GCI.  NO OBSERVED ORDER.  NOT PRINTED, NOT QUOTED, NOT "FOR INFORMATION".

This is a MESH-SENSITIVITY family, not a Roache r = 2 triple, and the reason is
ARITHMETIC rather than methodological.  The wall-normal first-cell height H1 is
held IDENTICAL at every level because the manual specifies standard wall
functions, which are valid only in the log layer.  Holding H1 fixed while
refining means the wall cell approaches and then exceeds the uniform spacing:
at L3 the solved gradings are already GU = 1.2039 and GC = 1.0411, essentially
uniform, so A FOURTH LEVEL IS ARITHMETICALLY IMPOSSIBLE without reducing H1 --
which drops y+ out of the log layer and CHANGES THE CASE.  Refinement here is
therefore not systematic: the near-wall contribution does not scale with h while
the rest of the mesh does.  An observed order computed across such a family is
not a discretisation order, and a GCI derived from it would be a number wearing
the shape of a rigour it does not have.

RULE 5's TRIPLE GATING DOES NOT FIRE BECAUSE NO TRIPLE IS REGISTERED.  THIS IS
A LIMITATION AND NOT AN EXEMPTION.  Nobody may read the absence of a triple as
a route around CLAUDE.md rule 5.  What replaces the GCI is the MESH-SENSITIVITY
SPREAD of the graded quantity across the three levels, reported beside limb C's
value as an explicit uncertainty channel -- the honest substitute for a number
we are not entitled to.  no_gci_selfcheck() below asserts, by scanning this
module's OWN emitted output, that no GCI or observed-order figure is ever
printed.
"""
import argparse
import glob
import math
import os
import re
import sys

VERSION = "VMFLGPU007-comparator-1.0"

# ---------------------------------------------------------------- VOCABULARY
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
TIER_CEILING_C = "GATE REACHED"   # limb C can never earn PASS
LIMB_B_PASS_CAPABLE = True        # identical mesh + identical scheme

# ------------------------------------------------------- FROZEN PHYSICS CONSTANTS
# Manual p.244 Material Properties column and Boundary Conditions column.
Q_FLUX = 1000.0        # W/m2, "Wall heat transfer, Q = 1,000 W/m2"
KAPPA = 1.408          # W/m-K, "Conductivity = 1.408 W/m-K"
H_STEP = 1.0           # m, "H = 1m" -- the ONLY dimension the manual gives
T_INLET = 300.0        # K, the case's own 0/T inlet fixedValue
# Nu(x) = q'' * H / (kappa * (T_w(x) - T_inlet)).  DERIVED HERE from the frozen
# constants above; a solver-side Nusselt number is never trusted.

# THE REGISTERED VELOCITY SCALE.  The manual says only "ReH is about 28,000" and
# never names the scale.  MEASURED from the archive's own inlet profile with the
# manual's own properties (rho=1, H=1, mu=1e-4): u_max = 2.8 gives EXACTLY 28,000;
# the bulk mean 2.570882 gives 25,709, missing by 8.2 %.  u_max is therefore the
# registered scale.  Recorded so nobody later "corrects" the Reynolds number and
# silently moves the operating point.
U_MAX = 2.8
RE_H_REGISTERED = 28000.0
RE_H_IF_BULK_WERE_USED = 25709.0   # recorded, NOT used

# ------------------------------------------------------------- FROZEN GATE BANDS
BAND_B = 1.0e-4        # limb B: |q_GPU - q_CPU| / |q_CPU|
BAND_C1 = 0.20         # limb C1: relative band on peak Nu
BAND_C2 = 1.5          # limb C2: ABSOLUTE band on peak location, in x/H
REF_PEAK_NU = 64.8530  # reference/vmfl013_vogel_eaton_nu.csv, measured by this lane
REF_PEAK_XH = 5.8209

# --------------------------------------------------------------- MESH FAMILY
# MEASURED cell counts (blockMesh + checkMesh on the lab box, pre-freeze;
# MESH_PREFREEZE_RECORD.md).  These are birth-certificate targets, not guesses.
LEVELS = (("L1", 3648), ("L2", 7776), ("L3", 16128))
ARMS = ("gpu", "cpu")
H1_WALL = 0.07         # m, identical at every level -- see the NO GCI block above

# y+ BAND, REGISTERED ON THE ATTACHED REGION ONLY.  At separation and
# reattachment the wall shear vanishes BY DEFINITION, so y+ -> 0 there; a floor
# demanded everywhere would refuse every correct backward-facing-step mesh.  The
# band is applied to the upper-quartile of the y+ distribution, which samples the
# attached flow, and the near-zero minimum is REPORTED, never gated.
YPLUS_MIN_ATTACHED = 11.0    # below this the log law is not available at all
YPLUS_MAX_ATTACHED = 300.0
YPLUS_QUANTILE = 0.75

# ------------------------------------------------------------ PLANTED CONTROL
PLANT = 1.234e-3       # K, planted into a COPY of the wall-temperature reader
PLANT_MIN_FRACTION = 0.1

# ------------------------------------------------------------------ PLATEAU
PLATEAU_WINDOW = 200          # last N SIMPLE iterations of wallTmin
PLATEAU_MIN_SAMPLES = 200
PLATEAU_PTP_TOL = 1.0e-4      # K, peak-to-peak over the window
PLATEAU_ALIVE_MIN = 1.0e-2    # K, the channel must have MOVED over its history

# LIVENESS, inherited from VMFLGPU001-R2's refusal: a dead channel and a
# perfectly converged one look identical to a peak-to-peak tolerance.  A null
# window is accepted ONLY when the SAME channel moved by more than
# PLATEAU_ALIVE_MIN over its full history.  Strictly MORE discriminating.

# ------------------------------------------------------------------- LIMB A
GPU_PCTF_MIN = 99.0    # PETSc -log_view GPU %F on the GPU arm
# Rebuilt on PETSc's own per-event accounting (the VMFLGPU003 ruling), NOT on
# VMFLGPU001/002's tells: tell 1 fired on ANY CUDA-configured build INCLUDING the
# forced-CPU control, and tell 3 looked for a ksp_view line this build never
# prints.  An ABSENT table refuses; it is never read as a zero.


class Refusal(Exception):
    pass


_EMITTED = []


def emit(msg):
    _EMITTED.append(msg)
    print(msg)


def refuse(clause, msg):
    raise Refusal("REFUSE (VMFLGPU007 %s): %s" % (clause, msg))


# ==========================================================================
# READERS.  Each locates its file by GLOB and refuses unless EXACTLY ONE match
# exists -- an ambiguous reader is a reader that could silently pick the wrong
# file, and this family has lost a verdict to exactly that (L-347).
# ==========================================================================
def one_match(pattern, clause, what):
    hits = sorted(glob.glob(pattern))
    if not hits:
        refuse(clause, "READER ABSENT: no file matches %s (%s). An absent "
                       "reader is NEVER read as a zero; this comparator refuses "
                       "rather than grading a channel it cannot see."
                       % (pattern, what))
    if len(hits) > 1:
        refuse(clause, "%d files match %s for %s: %s. An ambiguous reader could "
                       "silently select the wrong file, so it refuses."
                       % (len(hits), pattern, what, [os.path.basename(h) for h in hits]))
    return hits[0]


def read_wall_T(case_dir, endtime, clause="R1"):
    """The GATE READER: raw face-centre (x y z T) on the heated wall at endTime.

    Returns [(x_over_H, T)] sorted by x.  The surfaces function object writes
    postProcessing/wallT/<time>/T_heatedWall.raw (name order varies between
    OpenFOAM releases, so BOTH orders are globbed and the one-match rule still
    applies).
    """
    base = os.path.join(case_dir, "postProcessing", "wallT", endtime)
    if not os.path.isdir(base):
        refuse(clause, "the gate reader directory %s does not exist. The graded "
                       "quantity has no source." % base)
    path = one_match(os.path.join(base, "*heatedWall*.raw"), clause,
                     "the heated-wall temperature sample")
    rows = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) < 4:
            continue
        try:
            rows.append((float(p[0]) / H_STEP, float(p[3])))
        except ValueError:
            continue
    if not rows:
        refuse(clause, "the gate reader %s parsed to ZERO rows. A reader that "
                       "returns nothing has not measured a null result, it has "
                       "failed." % path)
    rows.sort(key=lambda r: r[0])
    return rows


def nusselt(rows, clause="R2"):
    """Nu(x) = q'' * H / (kappa * (T_w - T_inlet)), DERIVED from frozen constants.

    A wall hotter than the inlet is required; a non-positive or vanishing
    temperature rise would make Nu singular and is refused rather than clipped.
    """
    out = []
    for xh, tw in rows:
        dT = tw - T_INLET
        if dT <= 1.0e-9:
            refuse(clause, "wall temperature rise is %.6g K at x/H = %.4f, which "
                           "is not positive. Nu = q''H/(kappa*dT) is singular "
                           "there and this comparator does not clip a singularity "
                           "into a finite number." % (dT, xh))
        out.append((xh, Q_FLUX * H_STEP / (KAPPA * dT)))
    return out


def peak_of(nu_rows):
    """Peak Nu and its location -- the graded scalars."""
    xh, nu = max(nu_rows, key=lambda r: r[1])
    return nu, xh


def argmax_row_index(nu_rows):
    """The row a max() reader SELECTS -- where the plant must be placed (L-347)."""
    best, idx = None, 0
    for i, (_, nu) in enumerate(nu_rows):
        if best is None or nu > best:
            best, idx = nu, i
    return idx


# ==========================================================================
# PLANTED-ZERO CONTROL (CLAUDE.md rule 3).
# The plant goes at the ROW THE READER ACTUALLY SELECTS -- the argmax row --
# not at an arbitrary first row.  That was the VMFL011 L-347 failure: a plant at
# row 0 proves the reader can see row 0, which is not the row it grades.
# The run tree is NEVER modified; the plant is applied to an in-memory COPY.
# ==========================================================================
def planted_zero_control(rows, clause="P1"):
    idx = argmax_row_index(nusselt(rows))
    base_nu, _ = peak_of(nusselt(rows))

    # Plant into a COPY: raise the wall temperature at the selected row, which
    # LOWERS Nu there -- a signed, supra-threshold move the reader must see.
    planted = list(rows)
    xh, tw = planted[idx]
    planted[idx] = (xh, tw + PLANT)
    moved_nu, _ = peak_of(nusselt(planted))

    # NEGATIVE ARM: an UNPLANTED copy must see no move at all.
    unplanted = list(rows)
    same_nu, _ = peak_of(nusselt(unplanted))
    if abs(same_nu - base_nu) > 0.0:
        refuse(clause, "the NEGATIVE arm moved: an unplanted copy read %.9g "
                       "against a baseline of %.9g. The reader is not "
                       "deterministic and no zero it reports is evidence."
                       % (same_nu, base_nu))

    delta = abs(moved_nu - base_nu)
    # Supra-threshold requirement, expressed on the graded quantity itself.
    dT = rows[idx][1] - T_INLET
    expect = abs(Q_FLUX * H_STEP / (KAPPA * dT) - Q_FLUX * H_STEP / (KAPPA * (dT + PLANT)))
    if expect <= 0.0:
        refuse(clause, "the planted perturbation is not resolvable on this "
                       "channel: the expected Nu move is %.6g. A plant the "
                       "reader could not see even in principle proves nothing."
                       % expect)
    if delta <= PLANT_MIN_FRACTION * expect:
        refuse(clause, "PLANT-BLIND at the argmax row (index %d, x/H = %.4f): a "
                       "plant of %.6g K should have moved peak Nu by about "
                       "%.6g but it moved by %.6g. The reader cannot see a "
                       "known non-zero, so a zero from it is not evidence "
                       "(CLAUDE.md rule 3)."
                       % (idx, rows[idx][0], PLANT, expect, delta))
    return dict(row=idx, x_over_H=rows[idx][0], plant=PLANT,
                expected=expect, observed=delta)


# ==========================================================================
# STRICT COMPLETION (CLAUDE.md rule 4).  Refuses (never degrades) on any
# PHYSICS-CRITICAL clause.  The field-class split is L-342 / Sanaa's universal
# rule: bookkeeping never voids physics.
#
#   PHYSICS-CRITICAL (refuse): solver rc, the End line, last Time == endTime,
#                              `Time =` line count == endTime, the declared
#                              fields present at endTime, the 0/ age guard.
#   INFRASTRUCTURE  (report):  the ExecutionTime LINE COUNT -- petsc4Foam prints
#                              endTime + 2, two initialisation timing lines
#                              inside Time = 1, BEFORE the first solve.  It is a
#                              property of what the libraries print, never of the
#                              physics.  VMFLGPU001 froze that count as
#                              physics-critical, all six of its arms finished
#                              rc = 0, and it has NO VERDICT as a result.
# ==========================================================================
FIELDS_AT_ENDTIME = ("T", "U", "p_rgh", "alphat", "nut", "k", "epsilon")


def _field_present(d, f):
    return os.path.isfile(os.path.join(d, f)) or os.path.isfile(os.path.join(d, f + ".gz"))


def completion(case_dir, endtime, rc_text, clause="C"):
    log = one_match(os.path.join(case_dir, "log.*Foam"), clause + "0", "the solver log")
    txt = open(log, errors="replace").read()

    # C1 rc.  R-RC as an explicit conjunction: an ABSENT rc record is
    # INFRASTRUCTURE and gives rc = NOT MEASURED **only when** every other
    # physics-critical clause holds.  If any of those is ALSO missing, this
    # REFUSES; a missing rc never becomes a blanket pass.
    rc = None
    if rc_text is not None:
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)\s*$", rc_text, re.M)
        if m:
            rc = int(m.group(1))
    if rc is not None and rc != 0:
        refuse(clause + "1", "solver rc = %d in %s" % (rc, case_dir))

    # C2 the End line
    has_end = re.search(r"^End\s*$", txt, re.M) is not None
    if not has_end:
        refuse(clause + "2", "no 'End' line in %s -- the solver did not finish "
                             "its time loop" % log)

    # C3 last time == endTime, and C4 the `Time =` count == endTime.
    times = re.findall(r"^Time = (\S+)\s*$", txt, re.M)
    if not times:
        refuse(clause + "3", "no 'Time =' lines in %s" % log)
    try:
        last = float(times[-1])
    except ValueError:
        refuse(clause + "3", "last 'Time =' value %r in %s is not a number"
                             % (times[-1], log))
    if abs(last - float(endtime)) > 1e-9:
        refuse(clause + "3", "last time %s != registered endTime %s in %s"
                             % (times[-1], endtime, log))
    if len(times) != int(float(endtime)):
        refuse(clause + "4", "%d 'Time =' lines against a registered endTime of "
                             "%s in %s. The `Time =` count IS the physics-critical "
                             "clause here (L-342); the ExecutionTime count is not."
                             % (len(times), endtime, log))

    # C5 fields present at endTime
    td = os.path.join(case_dir, str(endtime))
    if not os.path.isdir(td):
        refuse(clause + "5", "no time directory %s" % td)
    missing = [f for f in FIELDS_AT_ENDTIME if not _field_present(td, f)]
    if missing:
        refuse(clause + "5", "field(s) %s absent from %s -- neither X nor X.gz"
                             % (", ".join(missing), td))

    # C6 THE AGE GUARD.  Every field at endTime must be NEWER than the case's
    # own 0/T, which is touched last at launch and so dates the run allowed to
    # produce this answer.
    zero_T = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(zero_T):
        refuse(clause + "6", "the age-guard reference %s does not exist, so no "
                             "field at endTime can be shown to postdate the "
                             "launch" % zero_T)
    t0 = os.path.getmtime(zero_T)
    stale = []
    for f in FIELDS_AT_ENDTIME:
        for cand in (os.path.join(td, f), os.path.join(td, f + ".gz")):
            if os.path.isfile(cand) and os.path.getmtime(cand) <= t0:
                stale.append(f)
                break
    if stale:
        refuse(clause + "6", "AGE GUARD: field(s) %s at %s are NOT newer than the "
                             "case's own 0/T. They cannot be shown to be this "
                             "run's output." % (", ".join(stale), td))

    # INFRASTRUCTURE, reported and never refusing.
    exec_lines = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    infra = None
    if exec_lines != len(times):
        infra = ("INFRA: %d ExecutionTime lines against %d 'Time =' lines "
                 "(petsc4Foam prints initialisation timing before the first "
                 "solve). INFRASTRUCTURE under L-342 -- reported, never refuses."
                 % (exec_lines, len(times)))
    return dict(rc=("NOT MEASURED" if rc is None else rc), times=len(times),
                last=last, infra=infra, log=log)


# ==========================================================================
# PLATEAU -- with the LIVENESS FLOOR.  A null window is accepted ONLY when the
# same channel MOVED over its full history.  A dead channel is still refused.
# ==========================================================================
def plateau(case_dir, clause="I"):
    base = os.path.join(case_dir, "postProcessing", "wallTmin")
    if not os.path.isdir(base):
        refuse(clause + "1", "no plateau channel at %s" % base)
    path = one_match(os.path.join(base, "*", "*.dat"), clause + "1",
                     "the wallTmin history")
    vals = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) >= 2:
            try:
                vals.append(float(p[-1]))
            except ValueError:
                pass
    if len(vals) < PLATEAU_MIN_SAMPLES:
        refuse(clause + "2", "the plateau channel has %d samples, fewer than the "
                             "registered minimum %d, so no window statement can "
                             "be made" % (len(vals), PLATEAU_MIN_SAMPLES))
    win = vals[-PLATEAU_WINDOW:]
    ptp = max(win) - min(win)
    full = max(vals) - min(vals)
    if ptp > PLATEAU_PTP_TOL:
        refuse(clause + "3", "the plateau window peak-to-peak is %.6g K, above "
                             "the registered %.6g K: the channel has not settled"
                             % (ptp, PLATEAU_PTP_TOL))
    if full < PLATEAU_ALIVE_MIN:
        refuse(clause + "4", "LIVENESS: the plateau window is flat (ptp %.6g) but "
                             "the channel moved only %.6g K over its ENTIRE "
                             "history, below the registered floor %.6g. A dead "
                             "channel and a converged one look identical to a "
                             "peak-to-peak test, so this refuses rather than "
                             "guessing." % (ptp, full, PLATEAU_ALIVE_MIN))
    return dict(samples=len(vals), window_ptp=ptp, history_range=full)


# ==========================================================================
# LIMB A -- GPU EXECUTION.  PETSc's own -log_view per-event accounting.
# An ABSENT table REFUSES; it is never read as a zero.
# ==========================================================================
def logview_gpu(case_dir, clause="A"):
    log = one_match(os.path.join(case_dir, "log.*Foam"), clause + "0", "the solver log")
    txt = open(log, errors="replace").read()
    if "-log_view" not in txt and "Summary of Stages" not in txt and "GPU %F" not in txt:
        refuse(clause + "1", "no PETSc -log_view table in %s. An ABSENT table is "
                             "NEVER read as a zero: without it there is no "
                             "evidence about where the linear algebra ran, and "
                             "this row certifies nothing." % log)
    pctf, h2d = None, None
    for line in txt.splitlines():
        if re.match(r"^\s*(MatMult|KSPSolve)\s", line):
            nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
            if len(nums) >= 2:
                tail = [float(x) for x in nums[-4:]]
                cand = max(tail) if tail else 0.0
                pctf = cand if pctf is None else max(pctf, cand)
        m = re.search(r"CpuToGpu (?:Count|- CopyTo)\s*[:=]?\s*(\d+)", line)
        if m:
            h2d = int(m.group(1)) if h2d is None else h2d + int(m.group(1))
    if pctf is None:
        refuse(clause + "1", "the -log_view table in %s carries no MatMult or "
                             "KSPSolve event row, so no GPU flop fraction can be "
                             "read. Refusing rather than assuming zero." % log)
    return dict(gpu_pctf=pctf, h2d=(0 if h2d is None else h2d))


def limb_A(gpu_dir, cpu_dir, level, clause="A"):
    g = logview_gpu(gpu_dir, clause)
    c = logview_gpu(cpu_dir, clause)
    # THE DISCRIMINATOR: the forced-CPU control must report NO GPU work.
    if c["gpu_pctf"] > 0.0 or c["h2d"] > 0:
        refuse(clause + "2", "%s: the FORCED-CPU CONTROL (mat_type aij, vec_type "
                             "standard) REPORTED GPU WORK (GPU %%F = %.4g, "
                             "host-to-device transfers = %d). The tells cannot "
                             "discriminate GPU from CPU on this build, so this "
                             "row certifies NOTHING."
                             % (level, c["gpu_pctf"], c["h2d"]))
    if g["gpu_pctf"] < GPU_PCTF_MIN:
        refuse(clause + "3", "%s: the GPU arm reports GPU %%F = %.4g, below the "
                             "registered floor %.4g. The object under "
                             "verification did not run on the GPU."
                             % (level, g["gpu_pctf"], GPU_PCTF_MIN))
    if g["h2d"] <= 0:
        refuse(clause + "4", "%s: the GPU arm reports ZERO host-to-device "
                             "transfers. A solve that never staged a buffer to "
                             "the device did not use it." % level)
    return dict(gpu=g, cpu=c)


# ==========================================================================
# LIMB B -- THE OBJECT UNDER TEST.  PASS-CAPABLE: identical mesh, identical
# scheme, so discretisation error cancels and no grid triple is needed.
# ==========================================================================
def limb_B(q_gpu, q_cpu, level, clause="B"):
    if abs(q_cpu) < 1e-30:
        refuse(clause + "0", "%s: the forced-CPU value is %.6g, so a RELATIVE "
                             "comparison is undefined" % (level, q_cpu))
    rel = abs(q_gpu - q_cpu) / abs(q_cpu)
    return rel, (rel <= BAND_B)


# ==========================================================================
# LIMB C -- the physics band.  CEILING: GATE REACHED AT MOST, never PASS.
# ==========================================================================
def limb_C(peak_nu, peak_xh):
    d1 = abs(peak_nu - REF_PEAK_NU) / abs(REF_PEAK_NU)
    d2 = abs(peak_xh - REF_PEAK_XH)
    return dict(rel_peak=d1, abs_loc=d2, held=(d1 <= BAND_C1 and d2 <= BAND_C2))


# ==========================================================================
# y+ BAND -- REGISTERED ON THE ATTACHED REGION ONLY.
# ==========================================================================
def yplus_band(case_dir, level, clause="Y"):
    base = os.path.join(case_dir, "postProcessing", "yPlusFO")
    if not os.path.isdir(base):
        refuse(clause + "1", "no y+ record at %s. The manual specifies STANDARD "
                             "wall functions, whose validity is a registered "
                             "condition of this case, and it cannot be checked "
                             "without this channel." % base)
    path = one_match(os.path.join(base, "*", "*.dat"), clause + "1", "the y+ record")
    vals = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        for tok in p[1:]:
            try:
                vals.append(float(tok))
            except ValueError:
                pass
    if not vals:
        refuse(clause + "2", "the y+ record %s parsed to zero values" % path)
    vals.sort()
    q = vals[min(len(vals) - 1, int(YPLUS_QUANTILE * len(vals)))]
    lo, hi = vals[0], vals[-1]
    if q < YPLUS_MIN_ATTACHED or q > YPLUS_MAX_ATTACHED:
        refuse(clause + "3", "%s: the attached-region y+ (upper-quartile "
                             "representative) is %.4g, outside the registered "
                             "band [%.4g, %.4g]. Standard wall functions assume "
                             "the log layer and this mesh does not deliver it."
                             % (level, q, YPLUS_MIN_ATTACHED, YPLUS_MAX_ATTACHED))
    # The minimum is REPORTED, never gated: y+ -> 0 at separation and
    # reattachment because the wall shear vanishes there BY DEFINITION.
    return dict(attached_q=q, min=lo, max=hi,
                note=("y+ min %.4g is at separation/reattachment where wall "
                      "shear vanishes by definition -- REPORTED, NOT GATED" % lo))


# ==========================================================================
# THE NO-GCI SELF-CHECK.  Enforced in CODE, not in prose: this scans this
# module's OWN emitted output and refuses if anything resembling a GCI or an
# observed order ever reached a reader.
# ==========================================================================
FORBIDDEN = (r"\bGCI\b", r"\bgrid convergence index\b", r"\bobserved order\b",
             r"\bp_obs\b", r"\bapparent order\b", r"\bRichardson\b")


def no_gci_selfcheck(clause="G"):
    blob = "\n".join(_EMITTED)
    for pat in FORBIDDEN:
        m = re.search(pat, blob, re.I)
        if m:
            refuse(clause + "1", "this comparator emitted %r. VMFLGPU007 is a "
                                 "MESH-SENSITIVITY family, not a Roache triple: "
                                 "no GCI and no observed order may be printed, "
                                 "quoted, or offered 'for information', because a "
                                 "reader could mistake it for a Roache result "
                                 "this case is not entitled to." % m.group(0))
    return True


def vocabulary_selfcheck(verdict, clause="V"):
    if verdict not in VOCAB:
        refuse(clause + "1", "verdict %r is not one of the fixed vocabulary %s "
                             "(CLAUDE.md rule 1)" % (verdict, list(VOCAB)))
    return True


# ==========================================================================
# THE GRADE
# ==========================================================================
def read_rc(run_root, level, arm):
    p = os.path.join(run_root, "RUN_RC.%s.%s" % (level, arm))
    return open(p).read() if os.path.isfile(p) else None


def read_endtime(run_root, level, arm):
    p = os.path.join(run_root, "RUN_RC.%s.%s" % (level, arm))
    if os.path.isfile(p):
        m = re.search(r"^\s*endtime\s*=\s*(\S+)\s*$", open(p).read(), re.M)
        if m:
            return m.group(1)
    refuse("E1", "cannot determine the registered endTime for %s/%s: no "
                 "'endtime =' line in %s. The completion rule's 'last time == "
                 "endTime' clause has no referent, so this refuses rather than "
                 "inferring one from the run's own output -- which would let the "
                 "run define its own finish line." % (level, arm, p))


def grade(run_root):
    emit("%s  run_root=%s" % (VERSION, run_root))
    emit("REGISTERED: Re_H = %.0f on u_max = %.4g m/s (bulk would give %.0f -- "
         "recorded, NOT used). q'' = %.4g W/m2, kappa = %.4g W/m-K, H = %.4g m, "
         "T_inlet = %.4g K. Nu is DERIVED here from these frozen constants."
         % (RE_H_REGISTERED, U_MAX, RE_H_IF_BULK_WERE_USED, Q_FLUX, KAPPA,
            H_STEP, T_INLET))
    emit("MESH-SENSITIVITY FAMILY (H1 = %.4g m identical at every level). NO "
         "discretisation-order figure and no extrapolation-based uncertainty "
         "figure is computed or printed by this comparator -- see "
         "PREREGISTRATION section 6 for why this family is not entitled to one. "
         "Rule 5's triple gating does not fire because NO TRIPLE IS REGISTERED: "
         "a LIMITATION, NOT AN EXEMPTION." % H1_WALL)

    per_level, controls = {}, {}
    for level, cells in LEVELS:
        gd = os.path.join(run_root, "gpu", level)
        cd = os.path.join(run_root, "cpu", level)
        for d in (gd, cd):
            if not os.path.isdir(d):
                refuse("D1", "arm directory %s does not exist" % d)

        et_g = read_endtime(run_root, level, "gpu")
        et_c = read_endtime(run_root, level, "cpu")
        if et_g != et_c:
            refuse("D2", "%s: the two arms registered different endTimes (%s vs "
                         "%s). Limb B is a statement about the linear algebra "
                         "ONLY IF both arms took the same number of outer "
                         "iterations." % (level, et_g, et_c))

        comp_g = completion(gd, et_g, read_rc(run_root, level, "gpu"), "CG")
        comp_c = completion(cd, et_c, read_rc(run_root, level, "cpu"), "CC")
        plat_g = plateau(gd, "IG")
        plat_c = plateau(cd, "IC")
        la = limb_A(gd, cd, level)
        yp = yplus_band(gd, level)

        rows_g = read_wall_T(gd, et_g, "RG")
        rows_c = read_wall_T(cd, et_c, "RC")
        # THE CONTROL RUNS BEFORE ANY EXIT, on the arm that is graded.
        controls[level] = planted_zero_control(rows_g, "P1")

        nu_g, nu_c = nusselt(rows_g, "R2"), nusselt(rows_c, "R2")
        pg, xg = peak_of(nu_g)
        pc, xc = peak_of(nu_c)
        relB, heldB = limb_B(pg, pc, level)
        per_level[level] = dict(cells=cells, peak_gpu=pg, xh_gpu=xg,
                                peak_cpu=pc, xh_cpu=xc, relB=relB, heldB=heldB,
                                comp_g=comp_g, comp_c=comp_c, plat_g=plat_g,
                                plat_c=plat_c, limbA=la, yplus=yp)
        for c in (comp_g["infra"], comp_c["infra"]):
            if c:
                emit("  %s %s" % (level, c))
        emit("  %s cells=%d  peak Nu gpu=%.6f @ x/H=%.4f | cpu=%.6f @ x/H=%.4f "
             "| limb B rel=%.3e %s | y+(attached)=%.3g [min %.3g reported, not "
             "gated] | plant %s"
             % (level, cells, pg, xg, pc, xc, relB,
                "HOLDS" if heldB else "MISSES", yp["attached_q"], yp["min"],
                "fired" if controls[level]["observed"] > 0 else "DID NOT FIRE"))

    # THE BIRTH CERTIFICATE, against the MEASURED pre-freeze counts.
    # (The launcher asserts cell counts at mesh time; this records them.)
    emit("BIRTH CERTIFICATE (measured pre-freeze, MESH_PREFREEZE_RECORD.md): %s"
         % ", ".join("%s=%d" % (n, c) for n, c in LEVELS))

    # LIMB B across every level.
    b_all = all(per_level[n]["heldB"] for n, _ in LEVELS)
    b_worst = max(per_level[n]["relB"] for n, _ in LEVELS)

    # LIMB C on the FINEST level, with the MESH-SENSITIVITY SPREAD beside it as
    # the explicit uncertainty channel -- the honest substitute for the GCI this
    # family is not entitled to.
    fine = LEVELS[-1][0]
    peaks = [per_level[n]["peak_gpu"] for n, _ in LEVELS]
    locs = [per_level[n]["xh_gpu"] for n, _ in LEVELS]
    spread_nu = max(peaks) - min(peaks)
    spread_rel = spread_nu / abs(peaks[-1]) if peaks[-1] else float("inf")
    spread_loc = max(locs) - min(locs)
    c = limb_C(per_level[fine]["peak_gpu"], per_level[fine]["xh_gpu"])

    emit("MESH-SENSITIVITY SPREAD (the registered uncertainty channel for this "
         "family): peak Nu over %s = %.6f .. %.6f, spread %.6f (%.3f %% of the "
         "finest), peak location spread %.4f x/H"
         % ("/".join(n for n, _ in LEVELS), min(peaks), max(peaks), spread_nu,
            100.0 * spread_rel, spread_loc))
    emit("LIMB A: GPU execution established at every level; forced-CPU control "
         "reported no GPU work at any level.")
    emit("LIMB B (%s, PASS-CAPABLE -- identical mesh and scheme): worst |dq|/|q| "
         "= %.3e against band %.1e" % ("HOLDS" if b_all else "MISSES", b_worst, BAND_B))
    emit("LIMB C (%s, CEILING %s -- never PASS): finest-level peak Nu = %.6f vs "
         "reference %.6f (rel %.4f, band %.4f); location %.4f vs %.4f "
         "(abs %.4f x/H, band %.4f)"
         % ("HOLDS" if c["held"] else "MISSES", TIER_CEILING_C,
            per_level[fine]["peak_gpu"], REF_PEAK_NU, c["rel_peak"], BAND_C1,
            per_level[fine]["xh_gpu"], REF_PEAK_XH, c["abs_loc"], BAND_C2))

    # ------------------------------------------------------------- VERDICT
    if not b_all:
        verdict = "GATE FAIL"
        why = ("limb B missed: the GPU and forced-CPU arms disagree by %.3e at "
               "identical mesh and scheme, which is a statement about the LINEAR "
               "ALGEBRA and is the object under verification." % b_worst)
    elif c["held"]:
        verdict = TIER_CEILING_C
        why = ("limb B holds and limb C is inside its band. The ceiling is %s: "
               "without systematic refinement this case cannot claim a "
               "discretisation-converged physics result and does not."
               % TIER_CEILING_C)
    else:
        verdict = "GATE FAIL"
        why = ("limb C missed WHILE LIMB B HELD (%.3e <= %.1e). THIS IS A **MODEL** "
               "MISS, NOT A GPU-PATH FAILURE: the GPU path is VERIFIED, because "
               "limb B compares the two arms at an identical mesh with an "
               "identical scheme and is unaffected by turbulence-model bias. "
               "Standard k-epsilon under-predicting backward-facing-step "
               "reattachment is the best-documented deficiency of this exact "
               "model on this exact flow." % (b_worst, BAND_B))

    vocabulary_selfcheck(verdict)
    emit("VERDICT: %s -- %s" % (verdict, why))
    emit("NOT CLAIMED: nothing about Ansys (this box has no Fluent); nothing "
         "about GPU performance (a GPU arm SLOWER than the CPU arm passes every "
         "limb); no PASS on limb C; no discretisation-converged result.")
    no_gci_selfcheck()
    return verdict


# ==========================================================================
# FIXTURES + SELFTEST.  Every arm asserts THE EXPECTED REFUSAL TEXT, never
# merely a non-zero exit (L-357).
# ==========================================================================
def _nu_to_dT(nu):
    return Q_FLUX * H_STEP / (KAPPA * nu)


def _profile(peak_nu):
    """A wall-temperature profile whose peak Nu is exactly `peak_nu`, located
    exactly at REF_PEAK_XH so the fixture is a clean control."""
    xs = [0.5 + 0.5 * i for i in range(40)]
    # put the reference location exactly on the grid
    j = min(range(len(xs)), key=lambda i: abs(xs[i] - REF_PEAK_XH))
    xs[j] = REF_PEAK_XH
    dT_min = _nu_to_dT(peak_nu)
    rows = []
    for x in xs:
        dT = dT_min + 0.5 * (x - REF_PEAK_XH) ** 2
        rows.append((x, T_INLET + dT))
    return rows


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def _make_arm(root, level, arm, endtime, peak_nu, *, rc=0, end_line=True,
              n_times=None, last_time=None, drop_field=None, stale=False,
              plateau_n=600, plateau_flat=True, alive=True, logview=True,
              gpu_pctf=None, h2d=None, yplus=37.0, rows=None, extra_raw=False,
              no_endtime=False):
    d = os.path.join(root, arm, level)
    os.makedirs(d, exist_ok=True)
    n = n_times if n_times is not None else int(endtime)
    lt = last_time if last_time is not None else endtime

    # 0/ (the age-guard reference) -- written FIRST so endTime fields are newer
    _write(os.path.join(d, "0", "T"), "0/T launch marker\n")
    if stale:
        os.utime(os.path.join(d, "0", "T"), (2 ** 31, 2 ** 31))  # far future

    td = os.path.join(d, str(endtime))
    os.makedirs(td, exist_ok=True)
    for f in FIELDS_AT_ENDTIME:
        if f == drop_field:
            continue
        _write(os.path.join(td, f), "field %s\n" % f)

    # solver log
    lines = []
    for i in range(1, n + 1):
        lines.append("Time = %d" % (i if i < n else int(float(lt)) if i == n else i))
    lines = ["Time = %d" % i for i in range(1, n)] + ["Time = %s" % lt] if n else []
    body = "\n".join(lines)
    body += "\n" + "\n".join("ExecutionTime = %d s" % i for i in range(n + 2))
    if logview:
        pf = gpu_pctf if gpu_pctf is not None else (100.0 if arm == "gpu" else 0.0)
        hd = h2d if h2d is not None else (6000 if arm == "gpu" else 0)
        body += ("\n-log_view\nSummary of Stages\nEvent Count Time GPU %%F\n"
                 "MatMult 6000 0 0 0 %g\nKSPSolve 3601 0 0 0 %g\n" % (pf, pf))
        if hd:
            body += "CpuToGpu Count %d\n" % hd
    if end_line:
        body += "\nEnd\n"
    _write(os.path.join(d, "log.buoyantSimpleFoam"), body + "\n")

    # gate reader
    prof = rows if rows is not None else _profile(peak_nu)
    raw = "# x y z T\n" + "\n".join("%.10g 0 0.05 %.10g" % (x * H_STEP, t) for x, t in prof)
    _write(os.path.join(d, "postProcessing", "wallT", str(endtime),
                        "T_heatedWall.raw"), raw + "\n")
    if extra_raw:
        _write(os.path.join(d, "postProcessing", "wallT", str(endtime),
                            "T_heatedWall_2.raw"), raw + "\n")

    # plateau channel
    base_T = prof[0][1]
    vals = []
    for i in range(plateau_n):
        if alive:
            v = base_T + 5.0 * math.exp(-i / 50.0)
        else:
            v = base_T
        if plateau_flat and i >= plateau_n - PLATEAU_WINDOW:
            v = base_T if alive else base_T
        vals.append(v)
    if not plateau_flat:
        for i in range(plateau_n - PLATEAU_WINDOW, plateau_n):
            vals[i] = base_T + (0.5 if i % 2 else -0.5)
    _write(os.path.join(d, "postProcessing", "wallTmin", "0",
                        "surfaceFieldValue.dat"),
           "# it min(T)\n" + "\n".join("%d %.10g" % (i, v) for i, v in enumerate(vals)) + "\n")

    # y+
    _write(os.path.join(d, "postProcessing", "yPlusFO", "0", "yPlus.dat"),
           "# t min max avg\n0 0.01 %g %g\n" % (yplus, yplus))

    if not no_endtime:
        _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)),
               "arm = %s\nlevel = %s\nrc = %d\nendtime = %s\n" % (arm, level, rc, endtime))
    else:
        _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)),
               "arm = %s\nlevel = %s\nrc = %d\n" % (arm, level, rc))
    return d


def _make_run(root, peaks=(64.5, 64.7, REF_PEAK_NU), endtime=1000, **kw):
    """A clean three-level, two-arm run. Per-arm overrides via kw['<level>_<arm>']."""
    for (level, _), pk in zip(LEVELS, peaks):
        for arm in ARMS:
            over = dict(kw.get("%s_%s" % (level, arm), {}))
            _make_arm(root, level, arm, over.pop("endtime", endtime),
                      over.pop("peak_nu", pk), **over)
    return root


ARMS_TABLE = []


def selftest():
    import shutil
    import tempfile
    root = tempfile.mkdtemp(prefix="vmflgpu007_selftest_")
    results = []

    def run(tag, expect_kind, expect_text, build):
        """expect_kind: 'verdict' -> expect_text is the verdict string.
                        'refuse'  -> expect_text MUST appear in the refusal."""
        d = os.path.join(root, tag)
        os.makedirs(d, exist_ok=True)
        try:
            build(d)
        except Exception as exc:                      # fixture bug, not a guard
            results.append((False, tag, "FIXTURE ERROR: %r" % (exc,)))
            return
        del _EMITTED[:]
        try:
            v = grade(d)
            got_kind, got = "verdict", v
        except Refusal as r:
            got_kind, got = "refuse", str(r)
        except Exception as exc:
            results.append((False, tag, "CRASHED (not a refusal): %s: %s"
                            % (type(exc).__name__, exc)))
            return
        if got_kind != expect_kind:
            results.append((False, tag, "expected a %s, got a %s: %s"
                            % (expect_kind, got_kind, got)))
            return
        # L-357: assert THE TEXT, never merely that something went wrong.
        if expect_text not in got:
            results.append((False, tag, "wrong %s. expected to contain %r; got %r"
                            % (expect_kind, expect_text, got)))
            return
        results.append((True, tag, got if expect_kind == "verdict" else
                        got.split(": ", 1)[-1][:110]))

    # ---- CONTROL -----------------------------------------------------------
    run("control", "verdict", "GATE REACHED", lambda d: _make_run(d))

    # ---- COMPLETION (rule 4) ----------------------------------------------
    run("c1_rc", "refuse", "solver rc = 3",
        lambda d: _make_run(d, L1_gpu=dict(rc=3)))
    run("c2_end", "refuse", "no 'End' line",
        lambda d: _make_run(d, L1_gpu=dict(end_line=False)))
    run("c3_lasttime", "refuse", "!= registered endTime",
        lambda d: _make_run(d, L1_gpu=dict(last_time=999)))
    run("c4_timecount", "refuse", "'Time =' lines against a registered endTime",
        lambda d: _make_run(d, L1_gpu=dict(n_times=900)))
    run("c5_field", "refuse", "absent from",
        lambda d: _make_run(d, L1_gpu=dict(drop_field="k")))
    run("c6_ageguard", "refuse", "AGE GUARD",
        lambda d: _make_run(d, L1_gpu=dict(stale=True)))

    # ---- PLATEAU + LIVENESS ------------------------------------------------
    run("i2_short", "refuse", "fewer than the registered minimum",
        lambda d: _make_run(d, L1_gpu=dict(plateau_n=50)))
    run("i3_unsettled", "refuse", "the channel has not settled",
        lambda d: _make_run(d, L1_gpu=dict(plateau_flat=False)))
    run("i4_dead", "refuse", "LIVENESS",
        lambda d: _make_run(d, L1_gpu=dict(alive=False)))

    # ---- LIMB A ------------------------------------------------------------
    run("a1_nolog", "refuse", "ABSENT table is",
        lambda d: _make_run(d, L1_gpu=dict(logview=False)))
    run("a2_leak", "refuse", "FORCED-CPU CONTROL",
        lambda d: _make_run(d, L1_cpu=dict(gpu_pctf=100.0, h2d=6000)))
    run("a3_pctf", "refuse", "below the registered floor",
        lambda d: _make_run(d, L1_gpu=dict(gpu_pctf=0.0)))
    run("a4_noh2d", "refuse", "ZERO host-to-device",
        lambda d: _make_run(d, L1_gpu=dict(h2d=0)))

    # ---- y+ ----------------------------------------------------------------
    run("y3_band", "refuse", "outside the registered band",
        lambda d: _make_run(d, L1_gpu=dict(yplus=4.0)))

    # ---- READERS -----------------------------------------------------------
    run("r_ambiguous", "refuse", "files match",
        lambda d: _make_run(d, L1_gpu=dict(extra_raw=True)))
    run("e1_noendtime", "refuse", "no 'endtime =' line",
        lambda d: _make_run(d, L1_gpu=dict(no_endtime=True)))
    run("d2_endtimes", "refuse", "different endTimes",
        lambda d: _make_run(d, L1_gpu=dict(endtime=900)))
    run("r2_singular", "refuse", "is not positive",
        lambda d: _make_run(d, L1_gpu=dict(
            rows=[(x, T_INLET - 1.0) for x, _ in _profile(REF_PEAK_NU)])))

    # ---- LIMB B / LIMB C VERDICT ROUTING -----------------------------------
    run("b_miss", "verdict", "GATE FAIL",
        lambda d: _make_run(d, L3_cpu=dict(peak_nu=REF_PEAK_NU * 1.05)))
    run("c_miss_model", "verdict", "GATE FAIL",
        lambda d: _make_run(d, peaks=(30.0, 30.0, 30.0)))

    # ---- CEILING, VOCABULARY, NO-GCI --------------------------------------
    def _ceiling(_d):
        if TIER_CEILING_C == "PASS":
            refuse("T1", "limb C's ceiling has been raised to PASS")
    results.append((TIER_CEILING_C == "GATE REACHED" and not LIMB_B_PASS_CAPABLE
                    is None, "ceiling_is_gate_reached",
                    "TIER_CEILING_C = %r (limb C can never earn PASS); limb B "
                    "PASS-capable = %r" % (TIER_CEILING_C, LIMB_B_PASS_CAPABLE)))

    ok_v = False
    try:
        vocabulary_selfcheck("VERIFIED")
    except Refusal as r:
        ok_v = "is not one of the fixed vocabulary" in str(r)
    results.append((ok_v, "vocabulary_rejects_a_synonym",
                    "a non-vocabulary verdict is refused"))

    ok_g = False
    del _EMITTED[:]
    _EMITTED.append("observed order p = 1.97, GCI = 0.4 %")
    try:
        no_gci_selfcheck()
    except Refusal as r:
        ok_g = "MESH-SENSITIVITY family" in str(r)
    del _EMITTED[:]
    results.append((ok_g, "no_gci_selfcheck_fires",
                    "a GCI or observed order reaching a reader is refused"))

    ok_gc = True
    del _EMITTED[:]
    try:
        d = os.path.join(root, "gcicheck"); os.makedirs(d, exist_ok=True)
        _make_run(d); grade(d)
        blob = "\n".join(_EMITTED)
        ok_gc = not re.search(r"\bGCI\b|\bobserved order\b", blob, re.I)
    except Exception:
        ok_gc = False
    results.append((ok_gc, "clean_grade_emits_no_gci",
                    "a full clean grade emits no GCI and no observed order"))

    n_assert = 0
    try:
        import ast
        n_assert = sum(isinstance(n, ast.Assert) for n in
                       ast.walk(ast.parse(open(__file__).read())))
    except Exception:
        n_assert = -1
    results.append((n_assert == 0, "zero_assert_statements",
                    "ast.Assert nodes = %d (python3 -O strips assert; a guard "
                    "built on one evaporates)" % n_assert))

    for good, tag, detail in results:
        print("%s  %-28s %s" % ("PASS" if good else "**FAIL**", tag, detail))
    n_ok = sum(1 for g, _, _ in results if g)
    print("")
    print("%d/%d arms behaved as registered%s  (__debug__=%s)"
          % (n_ok, len(results), "" if n_ok == len(results) else
             "   -- SELFTEST FAILED", __debug__))
    shutil.rmtree(root, ignore_errors=True)
    return 0 if n_ok == len(results) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=VERSION)
    ap.add_argument("--run-root")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.run_root:
        print("usage: grade_vmflgpu007.py --run-root <dir> | --selftest")
        return 2
    try:
        grade(a.run_root)
        return 0
    except Refusal as r:
        print(str(r))
        return 2


if __name__ == "__main__":
    sys.exit(main())
