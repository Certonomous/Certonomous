#!/usr/bin/env python3
r"""VMFLGPU007-R2 -- graded comparator.  Turbulent flow with heat transfer over a
backward-facing step; manual p.243; CPU parent VMFL013.

    grade_vmflgpu007_r2.py --run-root <dir>       grade a completed run
    grade_vmflgpu007_r2.py --selftest             drive every guard, exit 0/1
    grade_vmflgpu007_r2.py --drive-logview <dir>  print limb A's reading for ONE
                                                  arm directory, from real bytes

OBJECT UNDER VERIFICATION: the lab's GPU solver path (OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA on the L4).  NOT Ansys, NOT the turbulence model.

THIS IS A FRESH REGISTRATION (VERIFICATION_CHARTER 2c/2d), SUCCEEDING VMFLGPU007
(R1) THE WAY VMFLGPU001-R2 SUCCEEDED VMFLGPU001.  R1 IS FROZEN, ITS TREE AND ITS
COMPARATOR ARE PRESERVED UNTOUCHED, AND NOTHING HERE RE-GRADES IT.  R1's row
stands as NOT A RESULT on its supervisor's ruling of 2026-08-27.

NO `assert` ANYWHERE.  `python3 -O` strips assert statements, so a guard built
on one evaporates exactly when the code is run for speed.  Every refusal below
is an explicit branch reaching refuse().  Driven under both interpreters.

EVERY PLANTED FAILURE ASSERTS THE EXPECTED REFUSAL TEXT, never merely a
non-zero exit (L-357).  That lesson came from this lane: two arms of an earlier
instrument returned rc = 1 and looked like clean refusals while actually being a
NameError crash.  A non-zero exit is not evidence a guard fired.

--------------------------------------------------------------------------
WHAT MOVED FROM R1, AND NOTHING ELSE DID.  The constant-by-constant table is
CONSTANT_DIFF_VS_R1.txt beside this file; the three substantive moves are:

  1. THE REGISTERED endTimes.  L1 1200 -> 3200, L2 1800 -> 4400, L3 3000 -> 6200,
     chosen FROM THE MEASURED CONVERGENCE RATE of R1's own wallTmin channel and
     from nothing else.  endTime is a COST parameter.  **PLATEAU_PTP_TOL IS NOT
     TOUCHED**: it is 1.0e-4 K here, byte-identical to R1, because loosening a
     gate that refused is choosing the gate to fit the answer in the favourable
     direction, and this family has already declined to do that once (VMFLGPU001's
     I5 clause was left standing and its row went NOT A RESULT).  The endTimes
     are ALSO now REGISTERED IN THIS COMPARATOR (LEVEL_ENDTIME) and clause E2
     REFUSES a run whose RUN_RC declares a different one -- R1's comparator read
     the endTime out of the run's own bookkeeping and would have accepted any
     value, which is a hole a registration whose whole thesis is "the run was too
     short" cannot leave open.

  2. logview_gpu() IS REBUILT.  R1's reader took `max()` of the LAST FOUR numeric
     tokens of a MatMult/KSPSolve row and called it GPU %F.  On this build's real
     PETSc table the trailing columns are
       GPU Mflop/s | CpuToGpu Count | CpuToGpu Size | GpuToCpu Count | GpuToCpu Size | GPU %F
     so that max() returned the **CpuToGpu SIZE IN MBYTES** whenever it exceeded
     100 -- MEASURED 210.0 / 672.0 / 2320.0 at L1/L2/L3, values that SCALE WITH
     MESH and exceed 100, which a percentage cannot.  Clause A3's floor of 99.0
     was therefore cleared BY A MEGABYTE COUNT: a **SILENT FALSE PASS**, which is
     the dangerous half.  R1's `h2d` was worse in a safer direction: its regex
     `CpuToGpu (?:Count|- CopyTo)\s*[:=]?\s*(\d+)` needs digits immediately after
     the optional colon, and the only line in the file carrying that phrase is
     THE LEGEND, whose colon is followed by descriptive text.  h2d was therefore
     ALWAYS None -> 0, and clause A4 (`h2d <= 0` refuses) WAS UNPASSABLE ON ANY
     RUN, BY CONSTRUCTION.  Both columns are now located BY POSITION against the
     table's own two header lines, by TWO INDEPENDENT DERIVATIONS THAT MUST AGREE.

  3. A NEW REFUSAL: GPU %F IS A PERCENTAGE, so a value above GPU_PCTF_MAX = 100.0
     REFUSES rather than clearing the floor.  Had this clause existed in R1, the
     210.0 MByte figure could not have been read as a pass.  It is a NEW refusal
     path, never a loosening: nothing that refused in R1 passes here.

  The aggregation over rows also TIGHTENS: R1 gated on max(GPU %F) over the
  MatMult/KSPSolve rows, so ONE good row could carry a table full of bad ones.
  This gates on the **MINIMUM** over those rows, and on the **MAXIMUM** over them
  for the forced-CPU control's leak test.  A tightening is disclosed as a
  tightening; it is not presented as a repair.

--------------------------------------------------------------------------
THE GATE, and what each limb may earn (PREREGISTRATION sections 4 and 5), and it
is UNCHANGED FROM R1 IN EVERY BAND AND EVERY CEILING:

  LIMB A  GPU EXECUTION -- binary, physics-critical.  PETSc's own -log_view
          per-event accounting: the GPU arm must show GPU %F >= GPU_PCTF_MIN on
          EVERY MatMult/KSPSolve row and a non-zero host-to-device transfer
          count; the forced-CPU arm must show 0 and 0.  A LEAKING CONTROL
          REFUSES.  An ABSENT -log_view table REFUSES; it is never read as a
          zero.  A GPU %F ABOVE 100 REFUSES: a percentage cannot exceed 100 and
          a reader that returns one has read the wrong column.

  LIMB B  |q_GPU - q_CPU| / |q_CPU| <= BAND_B at EVERY level.  THIS IS THE
          OBJECT UNDER TEST AND IT IS PASS-CAPABLE: the comparison is made at
          an IDENTICAL mesh with an IDENTICAL scheme, so discretisation error
          cancels on both sides and no grid triple is needed to make the claim.
          VERIFICATION_CHARTER 2f.3 classifies it: a SAME-DISCRETE-PROBLEM
          IDENTITY limb, for which a triple is irrelevant and PASS is available.

  LIMB C  The physics band against Vogel & Eaton 1985 (EXPERIMENTAL).
          CEILING: GATE REACHED AT MOST -- never PASS.  VERIFICATION_CHARTER
          2f.3 classifies it: a CONTINUUM limb, from which discretisation error
          is not separable without a triple, so PASS is unavailable.  The ceiling
          is hard-coded as TIER_CEILING_C and executed by --selftest, so it is a
          property of the instrument and not a sentence in a document.

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

AND RULE 5's LIMB (1) FIRES IN FULL (VERIFICATION_CHARTER 2f.2, 2f.7): a level
not iteratively converged, or not plateaued, is NOT A RESULT.  "No triple" never
means "no rule 5".  Because this case registers NO residualControl, the run
always reaches endTime and "it ran to endTime" is NOT convergence; the plateau
channel below is the ONLY convergence gate this family has, and it is not
optional.  IT IS THE CLAUSE THAT REFUSED R1, CORRECTLY, AND IT IS CARRIED HERE
UNCHANGED.
"""
import argparse
import glob
import math
import os
import re
import sys

VERSION = "VMFLGPU007-R2-comparator-1.0"

# ---------------------------------------------------------------- VOCABULARY
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
TIER_CEILING_C = "GATE REACHED"   # limb C can never earn PASS
LIMB_B_PASS_CAPABLE = True        # identical mesh + identical scheme

# TIER_CEILING_C AND LIMB_B_PASS_CAPABLE ARE RE-DERIVED HERE, NOT COPIED, from
# the REFERENCE KIND of each limb (VERIFICATION_CHARTER 2f.3):
#   limb C's reference is Vogel & Eaton 1985, an EXPERIMENT -- an external
#   number about the CONTINUUM solution.  Discretisation error is not separable
#   from model error without systematic refinement, and this family is
#   deliberately not systematically refined, so PASS is unavailable and the
#   ceiling is GATE REACHED.
#   limb B's reference is THE OTHER ARM OF THIS SAME RUN, at an identical mesh
#   with an identical scheme.  It is a SAME-DISCRETE-PROBLEM IDENTITY: both
#   sides carry the SAME discretisation error, it cancels exactly, and the
#   claim is identity rather than accuracy.  A triple is irrelevant to it and
#   PASS is available.

# ------------------------------------------------------- FROZEN PHYSICS CONSTANTS
# Manual p.244 Material Properties column and Boundary Conditions column.
# ALL FOUR BYTE-IDENTICAL TO R1.
Q_FLUX = 1000.0        # W/m2, "Wall heat transfer, Q = 1,000 W/m2"
KAPPA = 1.408          # W/m-K, "Conductivity = 1.408 W/m-K"
H_STEP = 1.0           # m, "H = 1m" -- the ONLY dimension the manual gives
T_INLET = 300.0        # K, the case's own 0/T inlet fixedValue
# Nu(x) = q'' * H / (kappa * (T_w(x) - T_inlet)).  DERIVED HERE from the frozen
# constants above; a solver-side Nusselt number is never trusted.

# THE REGISTERED VELOCITY SCALE.  BYTE-IDENTICAL TO R1.  The manual says only
# "ReH is about 28,000" and never names the scale.  MEASURED from the archive's
# own inlet profile with the manual's own properties (rho=1, H=1, mu=1e-4):
# u_max = 2.8 gives EXACTLY 28,000; the bulk mean 2.570882 gives 25,709, missing
# by 8.2 %.  u_max is therefore the registered scale.  Recorded so nobody later
# "corrects" the Reynolds number and silently moves the operating point.
U_MAX = 2.8
RE_H_REGISTERED = 28000.0
RE_H_IF_BULK_WERE_USED = 25709.0   # recorded, NOT used

# ------------------------------------------------------------- FROZEN GATE BANDS
# ALL FIVE BYTE-IDENTICAL TO R1.
BAND_B = 1.0e-4        # limb B: |q_GPU - q_CPU| / |q_CPU|
BAND_C1 = 0.20         # limb C1: relative band on peak Nu
BAND_C2 = 1.5          # limb C2: ABSOLUTE band on peak location, in x/H
REF_PEAK_NU = 64.8530  # reference/vmfl013_vogel_eaton_nu.csv, measured by lane R2
REF_PEAK_XH = 5.8209

# --------------------------------------------------------------- MESH FAMILY
# MEASURED cell counts (blockMesh + checkMesh on the lab box, pre-freeze;
# VMFLGPU007/MESH_PREFREEZE_RECORD.md).  These are birth-certificate targets, not
# guesses.  BYTE-IDENTICAL TO R1 -- the mesh family does not move; only the
# number of outer iterations run on it does.
LEVELS = (("L1", 3648), ("L2", 7776), ("L3", 16128))
ARMS = ("gpu", "cpu")
H1_WALL = 0.07         # m, identical at every level -- see the NO GCI block above

# ------------------------------------------------- THE REGISTERED endTimes (NEW)
# R1 ran 1200 / 1800 / 3000 and its plateau clause REFUSED all six arms: the
# 200-sample peak-to-peak of wallTmin measured 0.0237893 / 0.0120540 / 0.00358665 K
# on the GPU arm against the registered 1.0e-4 K -- 238x, 121x and 36x the
# tolerance, falling monotonically.  The channel had not settled and the refusal
# was correct.
#
# THESE endTimes ARE CHOSEN FROM THE MEASURED CONVERGENCE RATE OF THAT CHANNEL
# AND FROM NOTHING ELSE.  Method, stated in full so it can be checked:
#   * The forward increment d(n) = wallTmin(n+1) - wallTmin(n) of R1's own
#     histories is a CLEAN DECAYING EXPONENTIAL over the last 200-600 samples of
#     every one of the six arms: fitting ln d(n) = a - n/tau gives R^2 = 0.9999 to
#     1.0000 and tau STABLE across window widths and across the two arms.
#   * For a geometric increment sequence the W-sample peak-to-peak is
#     ptp(n) = d(n-W) * (1 - r^W)/(1 - r) with r = exp(-1/tau), so
#     ptp(n + D) / ptp(n) = exp(-D/tau) EXACTLY.  The extra iterations needed to
#     bring ptp below PLATEAU_PTP_TOL are therefore D = tau * ln(ptp_now / TOL).
#   * A MARGIN of PLATEAU_MARGIN_TAU = 3 time constants is added (a factor
#     e^3 = 20.1 of headroom on the peak-to-peak) and the result is rounded UP to
#     the next multiple of 200.
# Using the CONSERVATIVE reading at each level (the LARGER of the two arms' ptp
# and the LARGEST tau over the 200/400/600-sample fit windows and both arms):
#   L1  ptp 0.02386442  tau 230.35  ->  1200 + 1261.1 + 691.1 = 3152.2  ->  3200
#   L2  ptp 0.01205923  tau 333.29  ->  1800 + 1597.3 + 999.9 = 4397.2  ->  4400
#   L3  ptp 0.003587164 tau 477.39  ->  3000 + 1708.9 + 1432.2 = 6141.1 ->  6200
# THE TOLERANCE IS NOT CHOSEN FROM THE DATA AND DOES NOT MOVE.  Only endTime,
# which is a cost parameter, is chosen from the data.
LEVEL_ENDTIME = {"L1": 3200, "L2": 4400, "L3": 6200}
PLATEAU_MARGIN_TAU = 3          # recorded for the reader; not used at grade time

# y+ BAND, REGISTERED ON THE ATTACHED REGION ONLY.  ALL THREE BYTE-IDENTICAL TO
# R1, and DELIBERATELY not revisited: R1's own artifacts read 36.502 / 36.284 /
# 36.158 on the gate patch, comfortably inside this band, but the band is carried
# because it was frozen BEFORE any run and not because a later reading suited it.
# At separation and reattachment the wall shear vanishes BY DEFINITION, so
# y+ -> 0 there; a floor demanded everywhere would refuse every correct
# backward-facing-step mesh.  The minimum is REPORTED, never gated.
YPLUS_MIN_ATTACHED = 11.0    # below this the log law is not available at all
YPLUS_MAX_ATTACHED = 300.0
YPLUS_GATE_PATCH = "heatedWall"

# ------------------------------------------------------------ PLANTED CONTROL
# BOTH BYTE-IDENTICAL TO R1.
PLANT = 1.234e-3       # K, planted into a COPY of the wall-temperature reader
PLANT_MIN_FRACTION = 0.1

# ------------------------------------------------------------------ PLATEAU
# ALL FOUR BYTE-IDENTICAL TO R1.  PLATEAU_PTP_TOL ESPECIALLY: it is the clause
# that refused R1, it refused for a PHYSICS reason, and a successor that loosened
# it would be choosing a gate to fit an answer in the favourable direction.
PLATEAU_WINDOW = 200          # last N SIMPLE iterations of wallTmin
PLATEAU_MIN_SAMPLES = 200
PLATEAU_PTP_TOL = 1.0e-4      # K, peak-to-peak over the window
PLATEAU_ALIVE_MIN = 1.0e-2    # K, the channel must have MOVED over its history

# LIVENESS, inherited from VMFLGPU001-R2's refusal: a dead channel and a
# perfectly converged one look identical to a peak-to-peak tolerance.  A null
# window is accepted ONLY when the SAME channel moved by more than
# PLATEAU_ALIVE_MIN over its full history.  Strictly MORE discriminating.

# ------------------------------------------------------------------- LIMB A
GPU_PCTF_MIN = 99.0    # PETSc -log_view GPU %F on the GPU arm.  R1's value.
GPU_PCTF_MAX = 100.0   # NEW.  GPU %F IS A PERCENTAGE.  A reader that returns a
                       # value above 100 has read the WRONG COLUMN, and this
                       # comparator refuses rather than clearing a floor with it.
                       # R1 cleared its 99.0 floor with 210.0 -- the CpuToGpu
                       # SIZE IN MBYTES -- and reported a PASS for the wrong
                       # reason.  This clause makes that impossible to repeat.
LIMBA_EVENTS = ("MatMult", "KSPSolve")   # the flop-bearing rows limb A reads

# ---- THE -log_view TABLE'S OWN HEADER.  These are SHAPES, not thresholds. ----
LOGVIEW_TOP_RE = re.compile(r"^Event\s+Count\s+Time\s*\(sec\)\s+Flop\b")
LOGVIEW_PUNCT_RE = re.compile(r"^-+$")
LOGVIEW_STAGE_RE = re.compile(r"^-{2,}\s*Event Stage\s+(\d+)\s*:\s*(.*?)\s*$")
_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
# The two columns limb A reads, named as (TOP-line group, SUB-line token).
COL_PCTF = ("GPU", "%F")
COL_H2D = ("CpuToGpu", "Count")
# The legend block PETSc prints ABOVE the header names the trailing columns in
# order.  It is used ONLY to NAME columns -- never to read a value; R1's h2d bug
# was a value-reading regex that could match this legend and nothing else.
LOGVIEW_LEGEND_TAIL = (("Total Mflop/s", "Mflop/s"),
                       ("GPU Mflop/s", "Mflop/s"),
                       ("CpuToGpu Count", "Count"),
                       ("CpuToGpu Size", "Size"),
                       ("GpuToCpu Count", "Count"),
                       ("GpuToCpu Size", "Size"),
                       ("GPU %F", "%F"))


class Refusal(Exception):
    pass


_EMITTED = []


def emit(msg):
    _EMITTED.append(msg)
    print(msg)


def refuse(clause, msg):
    raise Refusal("REFUSE (VMFLGPU007-R2 %s): %s" % (clause, msg))


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

    Returns [(x_over_H, T)] sorted by x.  BYTE-IDENTICAL IN BEHAVIOUR TO R1's,
    and driven on R1's own real output: 96 / 144 / 216 rows at L1 / L2 / L3,
    which is NXD at each level.
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
#
# LOGIC BYTE-IDENTICAL TO R1.  WHAT IS NEW IS THAT --selftest NOW DRIVES IT:
# R1's control was live on every graded run and NO selftest arm exercised its
# refusal, so the only evidence it could refuse was a hand-drive.  Arms
# `p1_plant_blind` and `p1_negative_arm_moves` below close that, asserting the
# REFUSAL TEXT (L-357) and not merely a non-zero exit.
#
# ON THE MEANING OF `expect`, MEASURED ON REAL DATA AND RECORDED SO A LATER
# READER DOES NOT MISTAKE A CORRECT READING FOR A DEFECT: `expect` is the Nu move
# the plant would produce IF THE PLANTED ROW REMAINED THE ARGMAX.  On a dense
# real profile it may not: raising T at the peak lowers Nu there and the max can
# hand off to the runner-up, so the OBSERVED move is bounded by the gap to that
# runner-up.  Driven on R1's L3 artifacts: expected 0.0070789, observed 0.0045303,
# ratio 0.640 -- far above PLANT_MIN_FRACTION and correctly NOT a refusal.  The
# clause is a FRACTION for exactly this reason and is carried unchanged.
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
# rule: bookkeeping never voids physics.  BYTE-IDENTICAL TO R1.
#
#   PHYSICS-CRITICAL (refuse): solver rc, the End line, last Time == endTime,
#                              `Time =` line count == endTime, the declared
#                              fields present at endTime, the 0/ age guard.
#   INFRASTRUCTURE  (report):  the ExecutionTime LINE COUNT -- petsc4Foam prints
#                              endTime + 2, two initialisation timing lines
#                              inside Time = 1, BEFORE the first solve.  It is a
#                              property of what the libraries print, never of the
#                              physics.  MEASURED endTime + 2 on all six of R1's
#                              arms, exactly as registered.
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
# PLATEAU -- with the LIVENESS FLOOR.  BYTE-IDENTICAL TO R1, INCLUDING ITS
# TOLERANCE.  This is the clause that refused R1 and it refused correctly.
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
#
# THE READER IS REBUILT.  R1's took max() of the LAST FOUR numeric tokens of a
# MatMult/KSPSolve row; on this build's real table the last four are
#   CpuToGpu Size (MB) | GpuToCpu Count | GpuToCpu Size (MB) | GPU %F
# so it returned the CpuToGpu SIZE whenever that exceeded 100 -- 210.0 / 672.0 /
# 2320.0 at L1/L2/L3 -- and cleared a 99.0 percentage floor with a megabyte
# count.  Columns are now located BY POSITION against the table's OWN two header
# lines, by TWO INDEPENDENT DERIVATIONS THAT MUST AGREE:
#
#   D1 CHARACTER-SPAN ASSOCIATION.  Each token of the SUB header line is assigned
#      to the TOP header token whose character span it overlaps, ignoring the
#      pure-punctuation rules ('-', '---').  That gives every data column a
#      (group, sub) name: ('CpuToGpu','Count'), ('GPU','%F'), and so on.
#   D2 THE LEGEND ORDER.  PETSc prints, immediately above the header, one line
#      per trailing column naming it: "Total Mflop/s:", "GPU Mflop/s:",
#      "CpuToGpu Count:", "CpuToGpu Size (Mbytes):", "GpuToCpu Count:",
#      "GpuToCpu Size (Mbytes):", "GPU %F:".  The last seven SUB tokens must be
#      the terminal words of those seven names, in that order.
#
# If D1 and D2 disagree on either column limb A reads, this REFUSES.  The legend
# is used ONLY to name columns and NEVER to read a value: R1's h2d defect was a
# value-reading regex whose only match in the whole file WAS this legend.
#
# An ABSENT table REFUSES; it is never read as a zero.
# ==========================================================================
def logview_columns(top, sub, clause="A"):
    """D1: name every data column by character-span association (top, sub)."""
    tops = [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", top)]
    tops = [t for t in tops if not LOGVIEW_PUNCT_RE.match(t[2])]
    names = []
    for m in re.finditer(r"\S+", sub):
        s, e = m.start(), m.end()
        owner = None
        for gs, ge, gt in tops:
            if s < ge and e > gs:
                owner = gt
        names.append((owner, m.group()))
    if not names:
        refuse(clause + "1H", "the -log_view sub-header line carries no tokens, "
                              "so no data column can be named. Refusing rather "
                              "than counting tokens from the end of a row, which "
                              "is exactly how R1 read a megabyte count as a "
                              "percentage.")
    return names


def logview_legend_indices(lines, hdr, ncols, clause="A"):
    """D2: locate the trailing columns from PETSc's own legend, independently."""
    seen = []
    for ln in lines[max(0, hdr - 30):hdr]:
        for full, tail in LOGVIEW_LEGEND_TAIL:
            if re.match(r"^\s+" + re.escape(full) + r"\b.*:", ln):
                if not seen or seen[-1][0] != full:
                    seen.append((full, tail))
    if [f for f, _ in seen] != [f for f, _ in LOGVIEW_LEGEND_TAIL]:
        refuse(clause + "1L", "the -log_view legend does not name the trailing "
                              "columns in the registered order. Expected %s, "
                              "found %s. The table's shape is not the one this "
                              "comparator can read, and it refuses rather than "
                              "guessing a column index."
                              % ([f for f, _ in LOGVIEW_LEGEND_TAIL],
                                 [f for f, _ in seen]))
    n = len(LOGVIEW_LEGEND_TAIL)
    base = ncols - n
    if base < 0:
        refuse(clause + "1L", "the -log_view table has %d data columns, fewer "
                              "than the %d its own legend names. Refusing."
                              % (ncols, n))
    out = {}
    for k, (full, _tail) in enumerate(LOGVIEW_LEGEND_TAIL):
        out[full] = base + k
    return out


def logview_table(case_dir, clause="A"):
    """Parse the ONE -log_view table in this arm's solver log."""
    log = one_match(os.path.join(case_dir, "log.*Foam"), clause + "0", "the solver log")
    lines = open(log, errors="replace").read().splitlines()
    hdrs = [i for i, l in enumerate(lines) if LOGVIEW_TOP_RE.match(l)]
    if not hdrs:
        refuse(clause + "1", "no PETSc -log_view table in %s. An ABSENT table is "
                             "NEVER read as a zero: without it there is no "
                             "evidence about where the linear algebra ran, and "
                             "this row certifies nothing." % log)
    if len(hdrs) > 1:
        refuse(clause + "1", "%d PETSc -log_view tables in %s. An ambiguous "
                             "table could silently be the wrong one, so this "
                             "refuses." % (len(hdrs), log))
    hdr = hdrs[0]
    if hdr + 1 >= len(lines):
        refuse(clause + "1H", "the -log_view header in %s has no sub-header "
                              "line beneath it." % log)
    names = logview_columns(lines[hdr], lines[hdr + 1], clause)
    ncols = len(names)

    # D1's answers
    d1 = {}
    for k, (grp, tok) in enumerate(names):
        d1.setdefault((grp, tok), k)
    if COL_PCTF not in d1:
        refuse(clause + "1H", "the -log_view header in %s names no %s/%s column. "
                              "R1 read this quantity by counting tokens from the "
                              "end of a row and got a megabyte count; this "
                              "comparator refuses instead."
                              % (log, COL_PCTF[0], COL_PCTF[1]))
    if COL_H2D not in d1:
        refuse(clause + "1H", "the -log_view header in %s names no %s/%s column."
                              % (log, COL_H2D[0], COL_H2D[1]))

    # D2's answers, derived independently
    d2 = logview_legend_indices(lines, hdr, ncols, clause)
    if d1[COL_PCTF] != d2["GPU %F"]:
        refuse(clause + "1X", "the two independent column derivations DISAGREE on "
                              "GPU %%F in %s: the header's character layout says "
                              "column %d, PETSc's own legend order says column "
                              "%d. A column index that cannot be established two "
                              "ways is not established."
                              % (log, d1[COL_PCTF], d2["GPU %F"]))
    if d1[COL_H2D] != d2["CpuToGpu Count"]:
        refuse(clause + "1X", "the two independent column derivations DISAGREE on "
                              "CpuToGpu Count in %s: the header's character "
                              "layout says column %d, PETSc's own legend order "
                              "says column %d."
                              % (log, d1[COL_H2D], d2["CpuToGpu Count"]))

    row_re = re.compile(r"^(\S.*?)\s+((?:%s)(?:\s+(?:%s)){%d})\s*$"
                        % (_NUM, _NUM, ncols - 1))
    rows, stage = [], None
    for ln in lines[hdr + 2:]:
        ms = LOGVIEW_STAGE_RE.match(ln.strip())
        if ms:
            stage = ms.group(2)
            continue
        m = row_re.match(ln)
        if not m:
            continue
        vals = [float(v) for v in m.group(2).split()]
        rows.append(dict(stage=stage, event=m.group(1).strip(), vals=vals))
    return dict(log=log, ncols=ncols, names=names, i_pctf=d1[COL_PCTF],
                i_h2d=d1[COL_H2D], rows=rows)


def logview_gpu(case_dir, clause="A"):
    """Limb A's reading for ONE arm, from the -log_view table's named columns."""
    tab = logview_table(case_dir, clause)
    sel = [r for r in tab["rows"] if r["event"] in LIMBA_EVENTS]
    if not sel:
        refuse(clause + "1", "the -log_view table in %s carries no %s event row, "
                             "so no GPU flop fraction can be read. Refusing "
                             "rather than assuming zero."
                             % (tab["log"], " or ".join(LIMBA_EVENTS)))
    pctf = [r["vals"][tab["i_pctf"]] for r in sel]
    h2d = [r["vals"][tab["i_h2d"]] for r in sel]
    # THE PERCENTAGE SANITY CLAUSE.  A GPU %F above 100 means the wrong column
    # was read, which is precisely what happened in R1.
    hi = max(pctf)
    if hi > GPU_PCTF_MAX:
        bad = [r["event"] for r, v in zip(sel, pctf) if v > GPU_PCTF_MAX]
        refuse(clause + "1P", "the -log_view table in %s reports GPU %%F = %.6g "
                              "on %s, ABOVE 100. GPU %%F IS A PERCENTAGE and "
                              "cannot exceed 100: a reader returning this has "
                              "read the WRONG COLUMN. R1 cleared its 99.0 floor "
                              "with 210.0 -- the CpuToGpu SIZE IN MBYTES -- and "
                              "reported a pass for the wrong reason. This "
                              "refuses instead."
                              % (tab["log"], hi, ", ".join(sorted(set(bad)))))
    by_event = {}
    for r, v in zip(sel, h2d):
        by_event[r["event"]] = max(by_event.get(r["event"], 0.0), v)
    return dict(gpu_pctf_min=min(pctf), gpu_pctf_max=hi, n_rows=len(sel),
                h2d_total=sum(h2d), h2d_by_event=by_event,
                i_pctf=tab["i_pctf"], i_h2d=tab["i_h2d"], ncols=tab["ncols"],
                log=tab["log"])


def limb_A(gpu_dir, cpu_dir, level, clause="A"):
    g = logview_gpu(gpu_dir, clause)
    c = logview_gpu(cpu_dir, clause)
    # THE DISCRIMINATOR: the forced-CPU control must report NO GPU work.  The
    # control is tested on its MAXIMUM over the qualifying rows -- a leak on any
    # row is a leak -- where R1 tested a single pooled maximum of the wrong
    # column and passed by coincidence.
    if c["gpu_pctf_max"] > 0.0 or c["h2d_total"] > 0:
        refuse(clause + "2", "%s: the FORCED-CPU CONTROL (mat_type aij, vec_type "
                             "standard) REPORTED GPU WORK (GPU %%F = %.4g, "
                             "host-to-device transfers = %d). The tells cannot "
                             "discriminate GPU from CPU on this build, so this "
                             "row certifies NOTHING."
                             % (level, c["gpu_pctf_max"], int(c["h2d_total"])))
    if g["gpu_pctf_min"] < GPU_PCTF_MIN:
        refuse(clause + "3", "%s: the GPU arm reports GPU %%F = %.4g on at least "
                             "one of its %d %s rows, below the registered floor "
                             "%.4g. The object under verification did not run on "
                             "the GPU."
                             % (level, g["gpu_pctf_min"], g["n_rows"],
                                "/".join(LIMBA_EVENTS), GPU_PCTF_MIN))
    if g["h2d_total"] <= 0:
        refuse(clause + "4", "%s: the GPU arm reports ZERO host-to-device "
                             "transfers. A solve that never staged a buffer to "
                             "the device did not use it." % level)
    return dict(gpu=g, cpu=c)


# ==========================================================================
# LIMB B -- THE OBJECT UNDER TEST.  PASS-CAPABLE: identical mesh, identical
# scheme, so discretisation error cancels and no grid triple is needed.
# BYTE-IDENTICAL TO R1.
# ==========================================================================
def limb_B(q_gpu, q_cpu, level, clause="B"):
    if abs(q_cpu) < 1e-30:
        refuse(clause + "0", "%s: the forced-CPU value is %.6g, so a RELATIVE "
                             "comparison is undefined" % (level, q_cpu))
    rel = abs(q_gpu - q_cpu) / abs(q_cpu)
    return rel, (rel <= BAND_B)


# ==========================================================================
# LIMB C -- the physics band.  CEILING: GATE REACHED AT MOST, never PASS.
# BYTE-IDENTICAL TO R1.
# ==========================================================================
def limb_C(peak_nu, peak_xh):
    d1 = abs(peak_nu - REF_PEAK_NU) / abs(REF_PEAK_NU)
    d2 = abs(peak_xh - REF_PEAK_XH)
    return dict(rel_peak=d1, abs_loc=d2, held=(d1 <= BAND_C1 and d2 <= BAND_C2))


# ==========================================================================
# y+ BAND -- REGISTERED ON THE ATTACHED REGION ONLY.  BYTE-IDENTICAL TO R1's
# post-Amendment-1 reader: select the GATE PATCH and read its `average`, a
# statistic the file actually contains; report min, max and the other patches
# and gate on none of them.  Driven on R1's own real output at all six arms:
# gate-patch average 36.502 / 36.284 / 36.158, inside the frozen band.
# ==========================================================================
def yplus_band(case_dir, level, clause="Y"):
    base = os.path.join(case_dir, "postProcessing", "yPlusFO")
    if not os.path.isdir(base):
        refuse(clause + "1", "no y+ record at %s. The manual specifies STANDARD "
                             "wall functions, whose validity is a registered "
                             "condition of this case, and it cannot be checked "
                             "without this channel." % base)
    path = one_match(os.path.join(base, "*", "*.dat"), clause + "1", "the y+ record")
    per_patch = {}
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) < 5:
            continue
        try:
            per_patch[p[1]] = (float(p[2]), float(p[3]), float(p[4]))
        except ValueError:
            continue
    if not per_patch:
        refuse(clause + "2", "the y+ record %s parsed to zero patch rows. A "
                             "reader that returns nothing has not measured a "
                             "null result, it has failed." % path)
    if YPLUS_GATE_PATCH not in per_patch:
        refuse(clause + "4", "the y+ record %s carries no row for the GATE PATCH "
                             "%r; it names %s. The band is a statement about the "
                             "wall the gate is computed on, and this comparator "
                             "does not substitute another wall for it."
                             % (path, YPLUS_GATE_PATCH, sorted(per_patch)))
    lo, hi, av = per_patch[YPLUS_GATE_PATCH]
    if av < YPLUS_MIN_ATTACHED or av > YPLUS_MAX_ATTACHED:
        refuse(clause + "3", "%s: y+ on the GATE PATCH %r averages %.4g, outside "
                             "the registered band [%.4g, %.4g]. Standard wall "
                             "functions assume the log layer and this mesh does "
                             "not deliver it."
                             % (level, YPLUS_GATE_PATCH, av, YPLUS_MIN_ATTACHED,
                                YPLUS_MAX_ATTACHED))
    return dict(gate_patch=YPLUS_GATE_PATCH, average=av, min=lo, max=hi,
                other_patches={k: v for k, v in per_patch.items()
                               if k != YPLUS_GATE_PATCH},
                note=("y+ min %.4g on the gate patch is at separation/"
                      "reattachment where wall shear vanishes by definition -- "
                      "REPORTED, NOT GATED. Other patches are reported and never "
                      "gated: the band is a statement about the gate patch."
                      % lo))


# ==========================================================================
# THE NO-GCI SELF-CHECK.  BYTE-IDENTICAL TO R1.  Enforced in CODE, not in prose:
# this scans this module's OWN emitted output and refuses if anything resembling
# a GCI or an observed order ever reached a reader.
# ==========================================================================
FORBIDDEN = (r"\bGCI\b", r"\bgrid convergence index\b", r"\bobserved order\b",
             r"\bp_obs\b", r"\bapparent order\b", r"\bRichardson\b")


def no_gci_selfcheck(clause="G"):
    blob = "\n".join(_EMITTED)
    for pat in FORBIDDEN:
        m = re.search(pat, blob, re.I)
        if m:
            refuse(clause + "1", "this comparator emitted %r. VMFLGPU007-R2 is a "
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
    """The endTime the run declares -- CHECKED AGAINST THE REGISTERED ONE (E2).

    R1's reader took whatever RUN_RC said and graded against it, so a run at any
    endTime would have been accepted.  For a registration whose entire thesis is
    that the previous endTime was too short, that is not a hole to leave open.
    """
    p = os.path.join(run_root, "RUN_RC.%s.%s" % (level, arm))
    got = None
    if os.path.isfile(p):
        m = re.search(r"^\s*endtime\s*=\s*(\S+)\s*$", open(p).read(), re.M)
        if m:
            got = m.group(1)
    if got is None:
        refuse("E1", "cannot determine the registered endTime for %s/%s: no "
                     "'endtime =' line in %s. The completion rule's 'last time == "
                     "endTime' clause has no referent, so this refuses rather "
                     "than inferring one from the run's own output -- which would "
                     "let the run define its own finish line." % (level, arm, p))
    if level not in LEVEL_ENDTIME:
        refuse("E2", "level %r is not one of the registered levels %s"
                     % (level, sorted(LEVEL_ENDTIME)))
    want = LEVEL_ENDTIME[level]
    try:
        got_i = int(float(got))
    except ValueError:
        refuse("E2", "%s/%s declares endtime = %r, which is not a number"
                     % (level, arm, got))
    if got_i != want:
        refuse("E2", "%s/%s ran to endTime %s, but the endTime REGISTERED for "
                     "this level is %d. R1 ran this case to 1200/1800/3000 and "
                     "its plateau channel had not settled; the endTimes here were "
                     "chosen from that channel's MEASURED decay rate and are part "
                     "of the frozen registration, so a run at a different one is "
                     "not this registration's run."
                     % (level, arm, got, want))
    return got


def grade(run_root):
    emit("%s  run_root=%s" % (VERSION, run_root))
    emit("SUCCEEDS VMFLGPU007 (R1), which is FROZEN and PRESERVED and is NOT "
         "re-graded here. R1's row stands as NOT A RESULT: its plateau channel "
         "had not settled at endTime.")
    emit("REGISTERED: Re_H = %.0f on u_max = %.4g m/s (bulk would give %.0f -- "
         "recorded, NOT used). q'' = %.4g W/m2, kappa = %.4g W/m-K, H = %.4g m, "
         "T_inlet = %.4g K. Nu is DERIVED here from these frozen constants."
         % (RE_H_REGISTERED, U_MAX, RE_H_IF_BULK_WERE_USED, Q_FLUX, KAPPA,
            H_STEP, T_INLET))
    emit("REGISTERED endTimes: %s. These are the ONLY registered quantity that "
         "moved from R1, and they were chosen from R1's own MEASURED wallTmin "
         "decay rate. THE PLATEAU TOLERANCE DID NOT MOVE: %.6g K, byte-identical "
         "to R1."
         % (", ".join("%s=%d" % (n, LEVEL_ENDTIME[n]) for n, _ in LEVELS),
            PLATEAU_PTP_TOL))
    emit("MESH-SENSITIVITY FAMILY (H1 = %.4g m identical at every level). NO "
         "discretisation-order figure and no extrapolation-based uncertainty "
         "figure is computed or printed by this comparator -- see "
         "PREREGISTRATION section 6 for why this family is not entitled to one. "
         "Rule 5's triple gating does not fire because NO TRIPLE IS REGISTERED: "
         "a LIMITATION, NOT AN EXEMPTION. Rule 5's limb (1) -- not iteratively "
         "converged, or not plateaued, is NOT A RESULT -- FIRES IN FULL."
         % H1_WALL)

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
        emit("  %s cells=%d endTime=%s  peak Nu gpu=%.6f @ x/H=%.4f | "
             "cpu=%.6f @ x/H=%.4f | limb B rel=%.3e %s | plateau ptp gpu=%.3e "
             "cpu=%.3e (tol %.1e) | y+(gate patch)=%.3g [min %.3g reported, not "
             "gated] | plant %s"
             % (level, cells, et_g, pg, xg, pc, xc, relB,
                "HOLDS" if heldB else "MISSES", plat_g["window_ptp"],
                plat_c["window_ptp"], PLATEAU_PTP_TOL, yp["average"], yp["min"],
                "fired" if controls[level]["observed"] > 0 else "DID NOT FIRE"))
        emit("     %s LIMB A: GPU arm GPU %%F in [%.4g, %.4g] over %d %s rows, "
             "CpuToGpu Count by event %s (total %d); forced-CPU control GPU %%F "
             "max %.4g, CpuToGpu Count total %d. Columns located by the table's "
             "own header: GPU %%F = col %d, CpuToGpu Count = col %d of %d."
             % (level, la["gpu"]["gpu_pctf_min"], la["gpu"]["gpu_pctf_max"],
                la["gpu"]["n_rows"], "/".join(LIMBA_EVENTS),
                {k: int(v) for k, v in sorted(la["gpu"]["h2d_by_event"].items())},
                int(la["gpu"]["h2d_total"]), la["cpu"]["gpu_pctf_max"],
                int(la["cpu"]["h2d_total"]), la["gpu"]["i_pctf"],
                la["gpu"]["i_h2d"], la["gpu"]["ncols"]))

    # THE BIRTH CERTIFICATE, against the MEASURED pre-freeze counts.
    emit("BIRTH CERTIFICATE (measured pre-freeze, VMFLGPU007/MESH_PREFREEZE_RECORD.md): %s"
         % ", ".join("%s=%d" % (n, c) for n, c in LEVELS))

    # LIMB B across every level.
    b_all = all(per_level[n]["heldB"] for n, _ in LEVELS)
    b_worst = max(per_level[n]["relB"] for n, _ in LEVELS)

    # LIMB C on the FINEST level, with the MESH-SENSITIVITY SPREAD beside it as
    # the explicit uncertainty channel -- the honest substitute for the GCI this
    # family is not entitled to (VERIFICATION_CHARTER 2f.6: a BOUND on observed
    # variation over the meshes actually built, never an error estimate).
    fine = LEVELS[-1][0]
    peaks = [per_level[n]["peak_gpu"] for n, _ in LEVELS]
    locs = [per_level[n]["xh_gpu"] for n, _ in LEVELS]
    spread_nu = max(peaks) - min(peaks)
    spread_rel = spread_nu / abs(peaks[-1]) if peaks[-1] else float("inf")
    spread_loc = max(locs) - min(locs)
    c = limb_C(per_level[fine]["peak_gpu"], per_level[fine]["xh_gpu"])

    emit("MESH-SENSITIVITY SPREAD (the registered uncertainty channel for this "
         "family; a BOUND on observed variation over the meshes actually built, "
         "never an error estimate and never extrapolated): peak Nu over %s = "
         "%.6f .. %.6f, spread %.6f (%.3f %% of the finest), peak location "
         "spread %.4f x/H"
         % ("/".join(n for n, _ in LEVELS), min(peaks), max(peaks), spread_nu,
            100.0 * spread_rel, spread_loc))
    emit("LIMB A: GPU execution established at every level; forced-CPU control "
         "reported no GPU work at any level.")
    emit("LIMB B (%s, PASS-CAPABLE -- identical mesh and scheme, a "
         "SAME-DISCRETE-PROBLEM IDENTITY): worst |dq|/|q| = %.3e against band %.1e"
         % ("HOLDS" if b_all else "MISSES", b_worst, BAND_B))
    emit("LIMB C (%s, CEILING %s -- never PASS, a CONTINUUM claim without a "
         "triple): finest-level peak Nu = %.6f vs reference %.6f (rel %.4f, band "
         "%.4f); location %.4f vs %.4f (abs %.4f x/H, band %.4f)"
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
         "limb, and R1 MEASURED the GPU arm slower than the CPU arm at every "
         "level); no PASS on limb C; no discretisation-converged result.")
    no_gci_selfcheck()
    return verdict


# ==========================================================================
# FIXTURES + SELFTEST.  Every arm asserts THE EXPECTED REFUSAL TEXT, never
# merely a non-zero exit (L-357).
#
# THE -log_view FIXTURE IS THE REAL SHAPE, NOT AN INVENTED ONE.  R1's fixture
# wrote a five-token pseudo-table ("Event Count Time GPU %F" over two rows) that
# OpenFOAM+PETSc does not produce, which is exactly why its selftest could not
# discover that the frozen reader read a megabyte count as a percentage.  The
# header, sub-header and legend below are the VERBATIM BYTES of the table PETSc
# wrote in R1's own gpu/L1/log.buoyantSimpleFoam, and the data rows carry all 26
# columns in their real order.  This is the third time this family has frozen a
# fixture-shaped parser (VMFLGPU007 Amendment 1's y+ reader, VMFLGPU002
# Amendment 5's limb-A tell, and now R1's limb-A reader), and the fix is the
# same each time: make the fixture the real shape.
# ==========================================================================
_LOGVIEW_LEGEND = (
    "   Total Mflop/s: 1e-6 * (sum of flop over all processes)/(max time over all processes)\n"
    "   GPU Mflop/s: 1e-6 * (sum of flop on GPU over all processes)/(max GPU time over all processes)\n"
    "   CpuToGpu Count: total number of CPU to GPU copies per processor\n"
    "   CpuToGpu Size (Mbytes): 1e-6 * (total size of CPU to GPU copies per processor)\n"
    "   GpuToCpu Count: total number of GPU to CPU copies per processor\n"
    "   GpuToCpu Size (Mbytes): 1e-6 * (total size of GPU to CPU copies per processor)\n"
    "   GPU %F: percent flops on GPU in this event\n")
_LOGVIEW_HEADER_TOP = (
    "Event                Count      Time (sec)     Flop                     "
    "         --- Global ---  --- Stage ----  Total   GPU    - CpuToGpu -   "
    "- GpuToCpu - GPU")
_LOGVIEW_HEADER_SUB = (
    "                   Max Ratio  Max     Ratio   Max  Ratio  Mess   AvgLen "
    " Reduct  %T %F %M %L %R  %T %F %M %L %R Mflop/s Mflop/s Count   Size   "
    "Count   Size  %F")


def _logview_row(event, count, flop, mflops, gpu_mflops, h2d_count, h2d_size,
                 d2h_count, d2h_size, pctf):
    """One data row in the real 26-column order."""
    v = [count, 1.0,            # Count Max, Ratio
         1.0e-1, 1.0,           # Time Max, Ratio
         flop, 1.0,             # Flop Max, Ratio
         0.0, 0.0, 0.0,         # Mess, AvgLen, Reduct
         0.0, 2.0, 0.0, 0.0, 0.0,   # Global %T %F %M %L %R
         6.0, 95.0, 0.0, 0.0, 0.0,  # Stage  %T %F %M %L %R
         mflops, gpu_mflops,
         h2d_count, h2d_size, d2h_count, d2h_size, pctf]
    return "%-18s %s" % (event, " ".join(("%g" % x) for x in v))


def _logview_table(pctf, h2d_mm, h2d_ks, h2d_size, extra_rows=(),
                   legend=_LOGVIEW_LEGEND, top=_LOGVIEW_HEADER_TOP,
                   sub=_LOGVIEW_HEADER_SUB):
    out = [legend.rstrip("\n"),
           "-" * 120,
           top,
           sub,
           "-" * 161,
           "",
           "--- Event Stage 0: Main Stage",
           "",
           _logview_row("MatMult", 14400, 4.64e8, 1230, 2950,
                        h2d_mm, h2d_size, 0, 0.0, pctf),
           _logview_row("VecCUDACopyTo", 7200, 0.0, 0, 0,
                        h2d_mm, h2d_size, 0, 0.0, 0.0),
           "",
           "--- Event Stage 3: foam_Ux_ksp",
           "",
           _logview_row("MatMult", 6006, 1.94e8, 1755, 3269, 0, 0.0, 0, 0.0, pctf),
           _logview_row("KSPSolve", 1200, 3.34e8, 403, 660,
                        h2d_ks, 1.05e2, 2, 1.73e-1, pctf),
           _logview_row("PCApply", 3604, 1.32e7, 223, 512, 1201, 3.5e1, 2, 1.73e-1, pctf)]
    out.extend(extra_rows)
    return "\n".join(out) + "\n"


def _nu_to_dT(nu):
    return Q_FLUX * H_STEP / (KAPPA * nu)


def _profile(peak_nu):
    """A wall-temperature profile whose peak Nu is exactly `peak_nu`, located
    exactly at REF_PEAK_XH so the fixture is a clean control."""
    xs = [0.5 + 0.5 * i for i in range(40)]
    j = min(range(len(xs)), key=lambda i: abs(xs[i] - REF_PEAK_XH))
    xs[j] = REF_PEAK_XH
    dT_min = _nu_to_dT(peak_nu)
    rows = []
    for x in xs:
        dT = dT_min + 0.5 * (x - REF_PEAK_XH) ** 2
        rows.append((x, T_INLET + dT))
    return rows


def _flat_profile(peak_nu):
    """A FLAT wall-temperature profile: every row is the argmax.  Planting at the
    argmax row then moves nothing, because the max hands off to an identical
    neighbour -- the PLANT-BLIND condition, driven rather than described."""
    dT = _nu_to_dT(peak_nu)
    return [(0.5 + 0.5 * i, T_INLET + dT) for i in range(40)]


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def _make_arm(root, level, arm, endtime, peak_nu, *, rc=0, end_line=True,
              n_times=None, last_time=None, drop_field=None, stale=False,
              plateau_n=600, plateau_flat=True, alive=True, logview=True,
              gpu_pctf=None, h2d=None, yplus=33.44, rows=None, extra_raw=False,
              drop_yplus_gate=False, no_endtime=False, declared_endtime=None,
              logview_legend=_LOGVIEW_LEGEND, logview_top=_LOGVIEW_HEADER_TOP,
              logview_sub=_LOGVIEW_HEADER_SUB, logview_text=None):
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
    lines = ["Time = %d" % i for i in range(1, n)] + ["Time = %s" % lt] if n else []
    body = "\n".join(lines)
    body += "\n" + "\n".join("ExecutionTime = %d s" % i for i in range(n + 2))
    if logview:
        if logview_text is not None:
            body += "\n" + logview_text
        else:
            pf = gpu_pctf if gpu_pctf is not None else (100.0 if arm == "gpu" else 0.0)
            hd = h2d if h2d is not None else (7200 if arm == "gpu" else 0)
            hk = 3601 if hd else 0
            body += "\n" + _logview_table(pf, hd, hk,
                                          2.10e2 if hd else 0.0,
                                          legend=logview_legend,
                                          top=logview_top, sub=logview_sub)
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
            v = base_T
        vals.append(v)
    if not plateau_flat:
        for i in range(plateau_n - PLATEAU_WINDOW, plateau_n):
            vals[i] = base_T + (0.5 if i % 2 else -0.5)
    _write(os.path.join(d, "postProcessing", "wallTmin", "0",
                        "surfaceFieldValue.dat"),
           "# it min(T)\n" + "\n".join("%d %.10g" % (i, v) for i, v in enumerate(vals)) + "\n")

    # y+ -- THE REAL SHAPE: one row per PATCH, columns Time, patch, min, max,
    # average.  The three non-gate patches carry real out-of-band values so the
    # fixture reproduces the trap R1's Amendment 1 repaired.
    yp_rows = [("heatedWall", yplus * 0.6, yplus * 3.2, yplus),
               ("stepFace", 106.5, 1089.8, 626.3),
               ("ductBottom", 37.08, 705.9, 193.9),
               ("topWall", 28.83, 48.44, 33.45)]
    if drop_yplus_gate:
        yp_rows = [r for r in yp_rows if r[0] != YPLUS_GATE_PATCH]
    _write(os.path.join(d, "postProcessing", "yPlusFO", "0", "yPlus.dat"),
           "# y+ ()\n# Time\tpatch\tmin\tmax\taverage\n"
           + "".join("5\t%s\t%.12e\t%.12e\t%.12e\n" % r for r in yp_rows))

    dec = endtime if declared_endtime is None else declared_endtime
    if not no_endtime:
        _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)),
               "arm = %s\nlevel = %s\nrc = %d\nendtime = %s\n" % (arm, level, rc, dec))
    else:
        _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)),
               "arm = %s\nlevel = %s\nrc = %d\n" % (arm, level, rc))
    return d


def _make_run(root, peaks=(64.5, 64.7, REF_PEAK_NU), **kw):
    """A clean three-level, two-arm run AT THE REGISTERED endTimes.

    Per-arm overrides via kw['<level>_<arm>'].
    """
    for (level, _), pk in zip(LEVELS, peaks):
        for arm in ARMS:
            over = dict(kw.get("%s_%s" % (level, arm), {}))
            _make_arm(root, level, arm,
                      over.pop("endtime", LEVEL_ENDTIME[level]),
                      over.pop("peak_nu", pk), **over)
    return root


def selftest():
    import shutil
    import tempfile
    root = tempfile.mkdtemp(prefix="vmflgpu007_r2_selftest_")
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
        lambda d: _make_run(d, L1_cpu=dict(gpu_pctf=100.0, h2d=7200)))
    run("a3_pctf", "refuse", "below the registered floor",
        lambda d: _make_run(d, L1_gpu=dict(gpu_pctf=0.0)))
    run("a4_noh2d", "refuse", "ZERO host-to-device",
        lambda d: _make_run(d, L1_gpu=dict(h2d=0)))
    # THE FALSE-PASS GUARD.  R1 cleared its 99.0 floor with 210.0 -- the
    # CpuToGpu SIZE IN MBYTES.  A percentage above 100 now REFUSES.
    run("a1p_pctf_above_100", "refuse", "ABOVE 100",
        lambda d: _make_run(d, L1_gpu=dict(gpu_pctf=210.0)))
    run("a1p_pctf_above_100_cpu_arm", "refuse", "ABOVE 100",
        lambda d: _make_run(d, L1_cpu=dict(gpu_pctf=672.0)))
    # A HEADER WHOSE SHAPE THIS COMPARATOR CANNOT READ REFUSES -- it does not
    # fall back to counting tokens from the end of a row.
    run("a1h_no_pctf_column", "refuse", "names no GPU/%F column",
        lambda d: _make_run(d, L1_gpu=dict(
            logview_top=_LOGVIEW_HEADER_TOP[:-3] + "XXX")))
    run("a1l_legend_mangled", "refuse", "does not name the trailing columns",
        lambda d: _make_run(d, L1_gpu=dict(
            logview_legend=_LOGVIEW_LEGEND.replace("   CpuToGpu Count:",
                                                   "   CpuToGpuCount:"))))

    # ---- THE REGISTERED endTime (E2) ---------------------------------------
    run("e2_wrong_endtime", "refuse", "is not this registration's run",
        lambda d: _make_run(d, L1_gpu=dict(declared_endtime=1200),
                            L1_cpu=dict(declared_endtime=1200)))

    # ---- y+ ----------------------------------------------------------------
    run("y3_band", "refuse", "outside the registered band",
        lambda d: _make_run(d, L1_gpu=dict(yplus=4.0)))
    run("y4_gate_patch_missing", "refuse", "carries no row for the GATE PATCH",
        lambda d: _make_run(d, L1_gpu=dict(drop_yplus_gate=True)))
    run("y_nongate_patches_do_not_gate", "verdict", "GATE REACHED",
        lambda d: _make_run(d))

    # ---- PLANTED-ZERO CONTROL (rule 3).  R1 HAD NO SELFTEST ARM FOR THIS. ---
    run("p1_plant_blind", "refuse", "PLANT-BLIND at the argmax row",
        lambda d: _make_run(d, L1_gpu=dict(rows=_flat_profile(REF_PEAK_NU))))

    # ---- READERS -----------------------------------------------------------
    run("r_ambiguous", "refuse", "files match",
        lambda d: _make_run(d, L1_gpu=dict(extra_raw=True)))
    run("e1_noendtime", "refuse", "no 'endtime =' line",
        lambda d: _make_run(d, L1_gpu=dict(no_endtime=True)))
    run("d2_endtimes", "refuse", "is not this registration's run",
        lambda d: _make_run(d, L1_gpu=dict(declared_endtime=900)))
    run("r2_singular", "refuse", "is not positive",
        lambda d: _make_run(d, L1_gpu=dict(
            rows=[(x, T_INLET - 1.0) for x, _ in _profile(REF_PEAK_NU)])))

    # ---- LIMB B / LIMB C VERDICT ROUTING -----------------------------------
    run("b_miss", "verdict", "GATE FAIL",
        lambda d: _make_run(d, L3_cpu=dict(peak_nu=REF_PEAK_NU * 1.05)))
    run("c_miss_model", "verdict", "GATE FAIL",
        lambda d: _make_run(d, peaks=(30.0, 30.0, 30.0)))

    # ---- THE PLANT FIRES ON A CLEAN FIXTURE (the positive arm) --------------
    ok_p = False
    try:
        pc = planted_zero_control(_profile(REF_PEAK_NU), "P1")
        ok_p = pc["observed"] > PLANT_MIN_FRACTION * pc["expected"] > 0.0
        detail_p = ("plant %.6g K at row %d moved peak Nu by %.6g against an "
                    "expected %.6g" % (pc["plant"], pc["row"], pc["observed"],
                                       pc["expected"]))
    except Exception as exc:
        detail_p = "CRASHED: %r" % (exc,)
    results.append((ok_p, "p1_plant_fires_on_clean_rows", detail_p))

    # ---- THE PLANT'S NEGATIVE ARM IS REACHABLE -----------------------------
    ok_n = False
    try:
        base = _profile(REF_PEAK_NU)
        moved = list(base)
        moved[argmax_row_index(nusselt(base))] = (base[0][0], T_INLET - 1.0)
        nusselt(moved, "R2")
    except Refusal as r:
        ok_n = "is not positive" in str(r)
    results.append((ok_n, "p1_negative_channel_refuses",
                    "a non-positive wall temperature rise in the planted copy's "
                    "channel refuses rather than producing a finite Nu"))

    # ---- LIMB A'S COLUMN DERIVATION AGREES WITH ITSELF ---------------------
    ok_col = False
    try:
        nm = logview_columns(_LOGVIEW_HEADER_TOP, _LOGVIEW_HEADER_SUB, "A")
        i1 = [k for k, x in enumerate(nm) if x == COL_PCTF]
        i2 = [k for k, x in enumerate(nm) if x == COL_H2D]
        ok_col = (len(nm) == 26 and i1 == [25] and i2 == [21])
        detail_c = ("26 data columns; GPU %F at column 25, CpuToGpu Count at "
                    "column 21, derived from the header's character layout")
    except Exception as exc:
        detail_c = "CRASHED: %r" % (exc,)
    results.append((ok_col, "a_column_indices_from_header", detail_c))

    # ---- THE FIXTURE IS THE REAL TABLE SHAPE, ROUND-TRIPPED ---------------
    # R1's fixture wrote a five-token pseudo-table, which is why its selftest
    # could not discover that the frozen reader read a megabyte count as a
    # percentage.  This arm parses the FIXTURE with the SAME code the grade uses
    # and requires the planted values to come back out of the named columns.
    ok_fx = False
    try:
        import tempfile as _tf
        _d = _tf.mkdtemp(prefix="vmflgpu007_r2_fx_")
        _write(os.path.join(_d, "log.fixtureFoam"),
               _logview_table(100.0, 7200, 3601, 2.10e2) + "\nEnd\n")
        _g = logview_gpu(_d, "A")
        ok_fx = (_g["ncols"] == 26 and _g["i_pctf"] == 25 and _g["i_h2d"] == 21
                 and _g["gpu_pctf_min"] == 100.0 and _g["gpu_pctf_max"] == 100.0
                 and _g["h2d_by_event"].get("MatMult") == 7200
                 and _g["h2d_by_event"].get("KSPSolve") == 3601)
        detail_f = ("the fixture parses through the grade's own reader to 26 "
                    "columns, GPU %F 100/100, CpuToGpu Count MatMult 7200 / "
                    "KSPSolve 3601 -- the values R1's real gpu/L1 log carries")
        shutil.rmtree(_d, ignore_errors=True)
    except Exception as exc:
        detail_f = "CRASHED: %r" % (exc,)
    results.append((ok_fx, "a_fixture_is_the_real_table_shape", detail_f))

    # ---- CEILING, VOCABULARY, NO-GCI --------------------------------------
    results.append((TIER_CEILING_C == "GATE REACHED" and LIMB_B_PASS_CAPABLE is True,
                    "ceiling_is_gate_reached",
                    "TIER_CEILING_C = %r (limb C is a CONTINUUM claim and can "
                    "never earn PASS); limb B PASS-capable = %r (a "
                    "SAME-DISCRETE-PROBLEM IDENTITY)"
                    % (TIER_CEILING_C, LIMB_B_PASS_CAPABLE)))

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
        d = os.path.join(root, "gcicheck")
        os.makedirs(d, exist_ok=True)
        _make_run(d)
        grade(d)
        blob = "\n".join(_EMITTED)
        ok_gc = not re.search(r"\bGCI\b|\bobserved order\b", blob, re.I)
    except Exception:
        ok_gc = False
    results.append((ok_gc, "clean_grade_emits_no_gci",
                    "a full clean grade emits no GCI and no observed order"))

    # ---- THE PLATEAU TOLERANCE HAS NOT MOVED FROM R1 -----------------------
    # The whole ground of this registration is that endTime moved and the
    # TOLERANCE did not.  That is asserted in code, so it cannot rot into prose.
    results.append((PLATEAU_PTP_TOL == 1.0e-4 and PLATEAU_WINDOW == 200
                    and PLATEAU_MIN_SAMPLES == 200 and PLATEAU_ALIVE_MIN == 1.0e-2,
                    "plateau_clause_identical_to_r1",
                    "window %d, min samples %d, ptp tol %.6g K, liveness floor "
                    "%.6g K -- all byte-identical to VMFLGPU007 (R1). endTime is "
                    "a cost parameter and was chosen from the data; the TOLERANCE "
                    "was not." % (PLATEAU_WINDOW, PLATEAU_MIN_SAMPLES,
                                  PLATEAU_PTP_TOL, PLATEAU_ALIVE_MIN)))

    results.append((BAND_B == 1.0e-4 and BAND_C1 == 0.20 and BAND_C2 == 1.5
                    and REF_PEAK_NU == 64.8530 and REF_PEAK_XH == 5.8209
                    and GPU_PCTF_MIN == 99.0 and YPLUS_MIN_ATTACHED == 11.0
                    and YPLUS_MAX_ATTACHED == 300.0 and PLANT == 1.234e-3
                    and PLANT_MIN_FRACTION == 0.1 and H1_WALL == 0.07
                    and LEVELS == (("L1", 3648), ("L2", 7776), ("L3", 16128)),
                    "gate_constants_identical_to_r1",
                    "every band, reference, floor, plant and mesh count carried "
                    "byte-identical from VMFLGPU007 (R1)"))

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
        print("%s  %-32s %s" % ("PASS" if good else "**FAIL**", tag, detail))
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
    ap.add_argument("--drive-logview", metavar="ARM_DIR",
                    help="print limb A's reading for ONE arm directory, from "
                         "that arm's real solver log. Grades nothing.")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.drive_logview:
        try:
            g = logview_gpu(a.drive_logview, "A")
        except Refusal as r:
            print(str(r))
            return 2
        print("log                = %s" % g["log"])
        print("data columns       = %d" % g["ncols"])
        print("GPU %%F column      = %d" % g["i_pctf"])
        print("CpuToGpu Count col = %d" % g["i_h2d"])
        print("%s rows      = %d" % ("/".join(LIMBA_EVENTS), g["n_rows"]))
        print("GPU %%F min / max   = %.6g / %.6g" % (g["gpu_pctf_min"], g["gpu_pctf_max"]))
        print("CpuToGpu Count by event = %s"
              % {k: int(v) for k, v in sorted(g["h2d_by_event"].items())})
        print("CpuToGpu Count total    = %d" % int(g["h2d_total"]))
        return 0
    if not a.run_root:
        print("usage: grade_vmflgpu007_r2.py --run-root <dir> | --selftest | "
              "--drive-logview <arm_dir>")
        return 2
    try:
        grade(a.run_root)
        return 0
    except Refusal as r:
        print(str(r))
        return 2


if __name__ == "__main__":
    sys.exit(main())
