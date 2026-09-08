#!/usr/bin/env python3
# =============================================================================
# VMFL046-R7 grading path.  COMMENT-ONLY successor of grade_vmfl046_r6.py
# (blob bad1408fd52e8d3bdc91bc64f28036de16f02af4): every executable token,
# every string literal AND the module docstring below are carried BYTE-IDENTICAL
# from R6, so the grading LOGIC is provably R6's -- ast.dump equal, and
# tokenize-equal excluding COMMENT tokens.  R7's ONLY change vs R6 is a CASE
# INPUT, not the grader: 0/U internalField uniform (100 0 0) -> (0 0 0), the
# answer-blind START-FROM-REST that clears R6's ~1.86e-4 s negative-T startup
# core-dump (register row #63).  The comparator never inspects the IC velocity,
# so NO gate / config / completion limb changes.  The docstring and the printed
# banner still read 'R6' ON PURPOSE: rewriting them would alter the module AST
# and break the strict ast.dump equality that proves the logic is unchanged.
# R7 identity, gate carry-forward (L-487) and predicted verdict live in
# cases/ansys_verification/VMFL046-R7/PREREGISTRATION.md.
# =============================================================================
"""VMFL046-R6 -- Supersonic flow with a normal shock in a converging-diverging nozzle.
THE FROZEN GRADING PATH.  Ansys Fluid Dynamics Verification Manual VM2026R1 p.155.

R6 == THE R5 COMPARATOR (blob 476de16a, itself byte-identical to R4's §2aw-repaired grader)
WITH EXACTLY THREE MECHANICAL CHANGES, ALL FORCED BY R6's TWO DELIBERATE AXES (the solver
rhoPimpleFoam -> rhoCentralFoam, and the outlet relaxation length lInf 2.0 -> 0.3):
  (1) N4 REPLACED.  rhoCentralFoam has NO fvOptions limitTemperature (verified at source),
      so R4/R5's "the limiter must be non-binding" limb is structurally inapplicable; it is
      replaced by check_T_physical_range -- a physical-range refusal on the reconstructed T
      field, bounds [50, 1000] K derived gate-blind from the frozen total temperature T0.
  (2) MAXCO_GRADED 0.5 -> 0.2.  A config-verification constant that pins the run to R6's
      frozen explicit acoustic-Courant limit; NOT a gate/threshold/band.
  (3) log filename log.rhoPimpleFoam -> log.rhoCentralFoam.  The solver's name.
EVERYTHING ELSE IS BYTE-FOR-BEHAVIOUR IDENTICAL TO R5: the gate (x_shock vs 1.250 m, band
5 %), DELTA_X, the plateau window and reader, W1/W2/W3, the Roache triple, the demote-only
secondaries, and PLANTS A/B/C1/C2/D.  NO gate quantity moves.
--------------------------------------------------------------------------------------------
The narrative below is the LINEAGE PROVENANCE of the carried-forward limbs (written for R4
and unchanged in behaviour through R5 to R6); it documents WHY each limb exists.

R4 WAS A COST FIX AND A READER-WINDOW FIX.  IT WAS NOT A PHYSICS FIX AND NOT A NUMERICS FIX.
Every one of the eleven case/ inputs was BYTE-IDENTICAL to R3's, and its driver ABORTED if
any one of them differed (run_vmfl046_r4.sh, exit 7).

    ANALYTICAL_SHOCK = 1.250 m      SHOCK_TOL = 5 %      DELTA_X = 6.250e-04 m
    ENDTIME_GRADED   = 0.080 s      SAMPLE_DT = 5.0e-04 s
    MAXCO 0.5   MAXDELTAT 1.0e-04   ddtSchemes Euler   Gauss vanLeer(V) 1

carried forward from R3 UNCHANGED, not re-derived, not re-rounded, not moved.

WHY R4 EXISTS
-------------
R3 (freeze 91f62d73, register row #60) graded NOT A RESULT.  Its NUMERICS CHANGE WORKED
at L1: RUN_RC 0, one End, last Time = 0.08 exactly.  L2 and L3 died rc 124 -- their own
caps firing -- and L3 reached 99.21 % of endTime before being killed after seven hours.
That is charter §26.2/§27's named trap verbatim: AN UNDER-FILED ESTIMATE DOES NOT
OVERSPEND, IT STRANGLES ITS OWN RUN AT THE END, AFTER ALL THE COMPUTE IS SPENT.

THE THREE DEFECTS R4 REPAIRS, AND EACH IS REPAIRED MECHANICALLY, NOT BY A SENTENCE
---------------------------------------------------------------------------------
W1  THE READER CONSUMED SAMPLES OUTSIDE ITS OWN REGISTERED WINDOW, AND THAT IS WHY R3
    REFUSED.  R3's grade() called shock_series() on the COMPLETE 160-sample history and
    only THEN sliced out the last 32.  It refused with

        "no downward Mach=1 crossing in sample .../centreline/0.0005/line_T_U.xy"

    -- a t = 0.0005 s sample, 0.6 % into a transient that has not yet formed a shock.
    THE REFUSAL WAS CORRECT BEHAVIOUR ON A BAD INPUT; THE READER SHOULD NEVER HAVE
    CONSUMED THAT INPUT.  The registered plateau window is the LAST 20 % of the clock,
    t in (endTime - 2W, endTime] = (0.064, 0.080].  128 of the 160 samples the reader
    opened were data the gate never asked for.

    THE REPAIR: registered_window() selects the window FIRST; shock_series() consumes
    only it.  AND IT IS PROVED, NOT ASSERTED: read_centreline_raw() records every path it
    opens in a module-level audit, and grade() REFUSES if any centreline path read for a
    level lies outside that level's registered window.  A reader that reads outside its
    window can no longer produce a verdict.

    NOTHING IS LOOSENED AND NO GRADED NUMBER MOVES.  windows() already selected exactly
    t >= endTime - 2W; P1, P2, P3, x_level and x_final are functions of those samples
    alone.  The repaired reader returns BIT-IDENTICAL values -- proved by a selftest arm
    that grades the same series both ways and compares with ==, not a tolerance.  The
    refusal for a genuinely missing crossing INSIDE the window is UNCHANGED and is
    exercised by its own planted arm.

W2  THE PROBE-LENGTH FLOOR IS NOW A FROZEN CONSTANT AND IT IS CHECKED AT IMPORT.
    R3's L2/L3 estimates came from probes covering 8 ms of the graded 80 ms -- 10 % -- and
    A RATE EXTRAPOLATED FROM THE FIRST 10 % OF AN ADAPTIVE-TIMESTEP TRANSIENT IS NOT A
    RATE, BECAUSE deltaT IS NOT STATIONARY THERE.  Measured on R3's own logs, the probe
    tail's mean deltaT at f = 0.10 is 4.70 / 4.46 / 3.89 times the run-settled value at
    L1 / L2 / L3, and the resulting estimates were 3.55x and 3.09x LOW.  The control is
    inside the same campaign: L1's probe covered 25 % and L1 came in at 0.845x.

    PROBE_FLOOR = 0.25 of the graded clock is registered here, COST_BASIS_FRACTION
    records the fraction of the clock each level's cost basis actually covers, and the
    import-time check REFUSES the module if any level's basis is below the floor.  An
    estimate from a shorter basis cannot be graded through this file at all.

W3  THE writeInterval GUARANTEE IS ARITHMETIC, NOT AN OBSERVATION.
    Three identities, all computable from frozen constants alone and all checked at
    import: endTime/SAMPLE_DT is a whole number (160 samples); W/SAMPLE_DT is a whole
    number of intervals, so each plateau window holds W/SAMPLE_DT + 1 = 17 SAMPLES,
    comfortably above MIN_WINDOW_SAMPLES = 8, at EVERY level because the frozen
    controlDict template carries no per-level clock; and SAMPLE_DT/maxDeltaT >= 1 (5.0),
    so adjustableRunTime always has at least one step in which to land on a write time.
    R3 had all three properties and verified none of them.

    ⚠ AND A COUNT IN R3's FROZEN REGISTRATION IS WRONG BY ONE, FOUND BY DOING THIS
    ARITHMETIC.  R3 §6 and its controlDict template both say the plateau window "holds 16
    samples where R2's held 13".  W/SAMPLE_DT = 16 is the number of INTERVALS; the window
    is closed at both ends, so it holds 17 SAMPLES, and the two adjacent windows share
    their boundary sample for 33 distinct samples in all.  R2's "13" counted samples
    correctly (12 intervals + 1), so R3 compared a sample count against an interval count.
    THE DIRECTION OF R3's CLAIM SURVIVES -- 17 > 13, the limb is strictly stricter than
    R2's -- AND ITS NUMBER DOES NOT.  Nothing graded moves; the count appears in no gate.

WHAT IS CARRIED FORWARD FROM R3'S FROZEN COMPARATOR, UNCHANGED IN BEHAVIOUR
  D1  the refining sampler assert (nPoints = 2*Nx+1, read from the level's OWN mesh)
  D2  the plateau on x_shock, peak-to-peak over two adjacent windows plus the mean drift
  D3  the INTERPOLATING shock reader (last downward M=1 crossing), and it is a gate limb
  D4  the Roache triple, the demote-only secondaries
  N2  the rule-4 DEPARTURE (the ExecutionTime-count limb, replaced by four stronger limbs)
  PLANTS A, B, C1, C2, D -- all five unchanged in design and in tolerance
  (N4 is NOT carried forward -- it is REPLACED for R6; see the R6 header block above and
   check_T_physical_range below.  rhoCentralFoam has no limitTemperature fvOption.)

WHAT IS NEW IN R4 BEYOND W1-W3
  W4  THE PLATEAU CONJUNCTION IS NOW EXERCISED BY THE SELFTEST.  R3's selftest had NO arm
      that ran plateau(); mutating its `ok = (p1<=DX) and (p2<=DX) and (p3<=DX)` to a
      constant True would have passed all 30 of its arms.  A verdict conjunction no
      selftest touches is an untested verdict.  Six arms now cover it: two that must
      plateau (including the exact-threshold boundary) and four that must not (each limb
      alone, plus one just over the threshold).

NO BARE `assert` ANYWHERE IN THIS FILE.  A bare assert vanishes under `python3 -O` and
takes its check with it; every check here is an explicit `refuse()` or `_require()`.

USAGE
    grade_vmfl046_r6.py <run_root>          grade
    grade_vmfl046_r6.py --paths <run_root>  §39.5 path enumeration against a real run root
    grade_vmfl046_r6.py --selftest          planted-failure self-tests
"""

import math
import os
import re
import shutil
import sys
import tempfile

# ---- FROZEN CONSTANTS -------------------------------------------------------
GAMMA           = 1.4
R_GAS           = 287.0

# PRIMARY GATE -- UNCHANGED FROM R1, R2 AND R3.  Not re-derived, not re-rounded, not moved.
ANALYTICAL_SHOCK = 1.250          # m
SHOCK_TOL        = 0.05           # 5 % -> band half-width 0.0625 m
BAND             = SHOCK_TOL * ANALYTICAL_SHOCK

# PLATEAU -- UNCHANGED FROM R2/R3, which adopted it unchanged from charter §31.
DELTA_X          = 6.25e-04       # m
W_FRACTION       = 10             # plateau window W = endTime / W_FRACTION
MIN_WINDOW_SAMPLES = 8            # a ptp over fewer samples is not a ptp; refuse
N_WINDOWS        = 2              # two adjacent windows, A and B -> the REGISTERED window
                                  # of this gate is the last N_WINDOWS*W seconds.

# TRANSIENT CONSTANTS -- PHYSICAL SECONDS.  Every one carried forward from R3 UNCHANGED.
ENDTIME_GRADED   = 0.080          # s.  ~20 upstream acoustic traverses (R3 §5.4)
SAMPLE_DT        = 5.0e-04        # s between centreline samples
MAXCO_GRADED     = 0.2            # R6 rhoCentralFoam EXPLICIT acoustic-Courant limit (PREREG §6);
                                  # tracks R6's deliberate maxCo change (rhoPimpleFoam 0.5 -> 0.2).
                                  # NOT a gate/threshold -- a config-verification constant that
                                  # pins the run to the registered stability limit.
MAXDELTAT_GRADED = 1.0e-04        # s
TIME_RTOL        = 1.0e-06        # relative tolerance on a written time-directory name

# SECONDARIES -- DEMOTE-ONLY (charter §21.3), retained UNCHANGED from R1/R2/R3.
P_OBS_LO, P_OBS_HI = 0.5, 2.5
GCI_FINE_MAX       = 0.15
R_REFINE, FS       = 2.0, 1.25

# N4 REPLACEMENT (R6) -- rhoCentralFoam has NO fvOptions limitTemperature.  VERIFIED AT
# SOURCE: applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C computes
#   e = rhoE/rho - 0.5*magSqr(U);  e.correctBoundaryConditions();  thermo.correct();
# with NO fvOptions, NO fvConstraints and NO bound() on T.  R4/R5's N4 limb -- "the
# constant/fvOptions limitTemperature bounds must be NON-BINDING at endTime" -- is therefore
# STRUCTURALLY INAPPLICABLE to R6 and is NOT carried across.  It is REPLACED by a
# PHYSICAL-RANGE refusal on the reconstructed T field:
#
#   This is an adiabatic-core, cooled-wall nozzle with inlet TOTAL temperature T0 = 500 K
#   (frozen 0/T inlet BC) and gamma = 1.4.  Energy conservation caps the static temperature
#   at the total temperature, and the wall (328 K) only REMOVES energy, so NO physical
#   process in this case raises static T above T0.  A reconstructed T field that leaves the
#   generous envelope [T_MIN_PHYS, T_MAX_PHYS] is a KNP numerical failure (a blow-up shows
#   T -> huge or T collapses toward 0), not the registered physics, and the grade REFUSES.
#
# The bounds are derived from the FROZEN THERMO ALONE (T0 and the case's max Mach), are
# ANSWER-BLIND, and are NON-BINDING on the true field (whose static T spans ~[254, 500] K:
# 254 K at the pre-shock M~=2.2 supersonic point, up to ~500 K near stagnation behind the
# shock).  Like R4's N4, this fires ONLY when something has gone wrong.
T0_TOTAL         = 500.0            # K, inlet total temperature (frozen 0/T inlet BC)
T_MAX_PHYS       = 2.0 * T0_TOTAL   # 1000 K; static T > 2*T0 is definitionally unphysical here
T_MIN_PHYS       = 50.0             # K; << T0/(1+0.2*2.2^2)=254 K (this case's pre-shock min),
                                    #    and << T0 at any Mach this nozzle reaches (M<=2.2)

# PLANTS (CLAUDE.md rule 3) -- all unchanged from R3.
PLANT_DX         = 1.000e-02      # m, the shock displacement planted into a SCRATCH copy
PLANT_DX_SMALL   = 6.250e-04      # m, exactly DELTA_X -- the quantum-discrimination plant
PLANT_K_T        = 1.0e-3         # relative plant into the T field
PLANT_C2_TOL     = 0.25           # fraction of the plant; the SAME tolerance as PLANT A

# ---- W2: THE PROBE-LENGTH FLOOR, FROZEN AND CHECKED AT IMPORT ---------------
#
# PROBE_FLOOR is the MINIMUM FRACTION OF THE GRADED CLOCK that a rate-setting cost basis
# must cover before its extrapolation is admissible in this registration.  It is not a
# gate, a band or a threshold -- it constrains the COST FILING and nothing else, and it
# can only make a registration harder to file.
#
# DEFENCE (PREREGISTRATION §5; all figures measured from R3's own three logs, reading
# ONLY the `Time =` and `ExecutionTime =` lines -- no field, no centreline sample, no
# gate quantity):
#
#   probe tail deltaT as a multiple of the RUN-SETTLED deltaT, at L1 / L2 / L3
#       f = 0.050   5.84  5.34  4.57       f = 0.175   1.07  1.15  1.09
#       f = 0.100   4.70  4.46  3.89       f = 0.200   1.03  1.09  1.00
#       f = 0.150   2.09  2.34  2.41       f = 0.250   1.03  1.03  0.95
#
#   worst |error| of a settled-tail extrapolation to endTime, over the three levels
#       f = 0.100   74.8 %      f = 0.175    6.6 %
#       f = 0.150   51.5 %      f = 0.200    4.7 %      f = 0.250    8.7 %
#
# The transition is between f = 0.15 (every level 1.25-2.4x off in deltaT and 50-61 %
# off in cost) and f = 0.175-0.20 (every level within 15 % in deltaT and 7 % in cost).
# 0.25 is registered rather than the measured edge 0.175-0.20 because a floor set AT its
# measured edge leaves a probe that just clears it with no margin -- and because 0.25 is
# this campaign's own positive control: R3's L1 probe covered 0.25 and L1 landed at
# 0.845x filed, while its L2 and L3 probes covered 0.10 and landed at 3.55x and 3.09x LOW.
#
# ⚠ AND WHAT COULD NOT BE DELIVERED, SAID PLAINLY.  A floor expressed as a fixed fraction
# is calibrated on THIS case at THIS clock and is not claimed to generalise beyond this
# family.  The generalisable alternative -- a test the probe runs ON ITSELF to certify
# that its own deltaT has settled -- WAS BUILT TWICE AND FAILED BOTH TIMES, IN THE
# DANGEROUS DIRECTION:
#   (i)  mean deltaT over the probe's last 20 % vs the 20 % before it: reads 0.986 /
#        0.970 / 0.914 at f = 0.10, i.e. "stationary", on probes that are 4.5x wrong; and
#        reads 0.62 / 0.60 / 0.56, i.e. "not stationary", at f = 0.20 where they are right.
#   (ii) last third vs middle third: worst deviation 14.7 % at f = 0.10 (inside a +-15 %
#        band, and 4.5x wrong) against 73.2 % at f = 0.20 (outside the band, and right).
# Both are ANTI-CORRELATED with the truth, because this case's deltaT keeps oscillating
# with the shock hunt for the whole run, so a short-baseline stationarity test aliases
# against that oscillation instead of measuring the startup collapse.  NEITHER IS
# REGISTERED.  A test that would have waved through the exact probes that killed R3 is
# worse than no test, and saying so is the finding.
PROBE_FLOOR = 0.25

# The fraction of the graded clock each level's FILED COST BASIS actually covers.  These
# are the R3 runs' own reached times divided by endTime -- L1 a COMPLETE run, L2 and L3
# capped.  They are recorded here so the floor is enforced on THIS registration's own
# filing and not merely described in prose.
COST_BASIS_FRACTION = {
    "L1": 0.0800000000 / ENDTIME_GRADED,   # 1.000000  -- COMPLETE, rc 0, End, Time = 0.08
    "L2": 0.0731877615 / ENDTIME_GRADED,   # 0.914847  -- capped at rc 124
    "L3": 0.0793715355 / ENDTIME_GRADED,   # 0.992144  -- capped at rc 124
}


class Refuse(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSE: %s\n" % msg)
        SystemExit.__init__(self, 2)


def refuse(msg):
    raise Refuse(msg)


def _require(cond, msg):
    """An explicit check that SURVIVES `python3 -O`.  A bare `assert` does not: -O strips
    it and takes the check with it, leaving a comparator that looks guarded and is not.
    There is no bare `assert` anywhere in this file and this function is why."""
    if not cond:
        refuse(msg)


# ---- W3 + W2: FROZEN-CONSTANT IDENTITIES, CHECKED AT IMPORT -----------------
#
# Every term below is a frozen constant of this registration, so these run once, at
# import, before any run root is named.  A registration whose own clock arithmetic does
# not close cannot grade anything.
def _check_frozen_arithmetic():
    n_total = ENDTIME_GRADED / SAMPLE_DT
    _require(abs(n_total - round(n_total)) < 1e-9,
             "W3 VIOLATED: endTime %g is not a whole number of SAMPLE_DT %g intervals "
             "(%.6f) -- the sampler cannot land on endTime and the history can never be "
             "complete" % (ENDTIME_GRADED, SAMPLE_DT, n_total))
    W = ENDTIME_GRADED / float(W_FRACTION)
    intervals = W / SAMPLE_DT
    _require(abs(intervals - round(intervals)) < 1e-9,
             "W3 VIOLATED: the plateau window W = %g s is not a whole number of SAMPLE_DT "
             "%g intervals (%.6f)" % (W, SAMPLE_DT, intervals))
    # A window closed at both ends holds one MORE sample than it has intervals, and the
    # two adjacent windows SHARE their boundary sample -- so the registered window holds
    # 2*intervals + 1 distinct samples, not 2*intervals.  Counting intervals as samples is
    # the off-by-one this limb exists to make impossible.
    per_window = int(round(intervals)) + 1
    _require(per_window >= MIN_WINDOW_SAMPLES,
             "W3 VIOLATED: writeInterval %g s puts only %d samples in the plateau window "
             "W = %g s, below the registered minimum of %d.  The plateau windows are the "
             "SAME %g s at every level because the frozen controlDict template carries no "
             "per-level clock, so this identity holds at L1, L2 and L3 alike."
             % (SAMPLE_DT, per_window, W, MIN_WINDOW_SAMPLES, W))
    _require(SAMPLE_DT >= MAXDELTAT_GRADED,
             "W3 VIOLATED: SAMPLE_DT %g is smaller than maxDeltaT %g, so adjustableRunTime "
             "has no step in which to land on a write time"
             % (SAMPLE_DT, MAXDELTAT_GRADED))
    for L in sorted(COST_BASIS_FRACTION):
        f = COST_BASIS_FRACTION[L]
        _require(f >= PROBE_FLOOR,
                 "W2 VIOLATED: %s's cost basis covers %.4f of the graded clock, below the "
                 "registered probe-length floor %.4f.  AN ESTIMATE DERIVED FROM A SHORTER "
                 "BASIS IS NOT ADMISSIBLE: R3's L2 and L3 bases covered 0.10 and were "
                 "3.55x and 3.09x LOW, and their caps -- 3x those bases -- killed both "
                 "runs, L3 at 99.21 %% of endTime after seven hours."
                 % (L, f, PROBE_FLOOR))
    return dict(n_total=int(round(n_total)), W=W,
                intervals=int(round(intervals)),
                per_window=per_window,
                window_total=N_WINDOWS * int(round(intervals)) + 1,
                steps_per_sample=SAMPLE_DT / MAXDELTAT_GRADED)


FROZEN_ARITHMETIC = _check_frozen_arithmetic()


# ---- W1: THE READ AUDIT -----------------------------------------------------
#
# Every centreline sample this comparator opens is recorded here, so "the reader consumes
# only its registered window" is a MEASURED PROPERTY OF THE RUN THAT PRODUCED THE VERDICT
# and not a claim about the source.  grade() refuses on any out-of-window read.
_CL_READS = []


def _audit_reset():
    del _CL_READS[:]


def _audit_paths():
    return list(_CL_READS)


# ---- readers ----------------------------------------------------------------
def read_centreline_raw(path):
    """-> [(x, T, ux, uy, uz)] from a raw `sets` .xy sample.  Refuses on anything it
    cannot parse; a reader that guesses can misread.

    W1: THE PATH IS RECORDED BEFORE IT IS OPENED.  Recording after a successful parse
    would miss exactly the reads that refuse -- which is the class R3's defect belongs to."""
    _CL_READS.append(os.path.realpath(path))
    if not os.path.isfile(path):
        refuse("centreline sample absent: %s" % path)
    out = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) != 5:
            refuse("centreline row has %d cols, expected 5 (x T Ux Uy Uz): %r in %s"
                   % (len(p), s, path))
        try:
            vals = [float(v) for v in p]
        except ValueError:
            refuse("centreline row not numeric (NaN/garbage is a refusal, not a guess): "
                   "%r in %s" % (s, path))
        if vals[1] <= 0.0:
            refuse("centreline T<=0 (%.6g) at x=%.4g in %s -- unphysical, refusing rather "
                   "than sqrt(neg)" % (vals[1], vals[0], path))
        out.append(tuple(vals))
    if len(out) < 10:
        refuse("centreline has %d usable rows (<10): %s" % (len(out), path))
    return out


def to_mach(raw):
    """-> [(x, Mach)]"""
    out = []
    for x, T, ux, uy, uz in raw:
        U = math.sqrt(ux * ux + uy * uy + uz * uz)
        out.append((x, U / math.sqrt(GAMMA * R_GAS * T)))
    return out


def shock_location(cl):
    """D3 -- THE INTERPOLATING READER, AND IT IS A GATE LIMB.  CARRIED FORWARD FROM R2/R3
    UNCHANGED IN BEHAVIOUR.

    The LAST downward Mach = 1 crossing, linearly interpolated.  Taking the FIRST crossing
    returns the THROAT (the subsonic->supersonic sonic point), a different feature ~0.7 m
    upstream.

    RESOLUTION: the returned x moves CONTINUOUSLY with the sampled Mach values -- it has no
    quantum.  Measured on real VMFL046 data, a relative perturbation eps applied to the Mach
    field shifts the reading by 1.2e-02 * eps metres; at writePrecision 12 that is ~1.2e-14
    m, i.e. 5.2e+10 times FINER than DELTA_X.  R1's node-snapping reader had a quantum of
    5.0025e-03 m -- 8.004 times COARSER than the same threshold.
    """
    found = None
    for i in range(1, len(cl)):
        xa, ma = cl[i - 1]
        xb, mb = cl[i]
        if (ma - 1.0) * (mb - 1.0) < 0 and mb < ma:
            found = xa + (1.0 - ma) * (xb - xa) / (mb - ma)
    return found


def shock_location_snapping(cl):
    """R1's frozen reader, REPRODUCED VERBATIM IN BEHAVIOUR.  NOT A GATE LIMB.  It exists
    to print the quantum comparison beside the verdict and to be the MUTANT the planted
    controls must refuse."""
    xs = [x for x, _ in cl]
    Ma = [m for _, m in cl]
    drops = [(Ma[i] - Ma[i + 1], xs[i + 1]) for i in range(len(Ma) - 1)]
    return max(drops)[1]


def read_T_internal(path):
    if not os.path.isfile(path):
        refuse("T field absent: %s" % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\(\s*\n(.*?)\n\)\s*;",
                  txt, re.S)
    if not m:
        refuse("T internalField is not a nonuniform scalar list: %s" % path)
    vals = []
    for row in m.group(2).splitlines():
        row = row.strip()
        if not row:
            continue
        try:
            vals.append(float(row))
        except ValueError:
            refuse("T internalField row not parseable: %r in %s" % (row, path))
    if not vals:
        refuse("T internalField empty: %s" % path)
    return vals, m.span()


# ---- run structure ----------------------------------------------------------
def read_controls(level_dir, strict=True):
    """-> (endTime, nPoints, maxCo, maxDeltaT).  Every one of these is a FROZEN constant of
    this registration and every one is checked against the file that actually ran.

    `strict=False` reads the values WITHOUT asserting them, and is used by ONE caller:
    `check_paths`, the §39.5 path enumerator.  That enumerator's whole job is to make
    contact with a real run root on disk -- including a CLAUSE-B smoke root, whose endTime
    is deliberately not the graded one.  A path enumerator that refuses every root it could
    actually be pointed at before the graded run exists is the §39.5 failure in miniature:
    an instrument that is internally immaculate and never touches reality.  `strict=False`
    is NOT reachable from `grade()`, so no graded verdict can be produced without every
    assertion below having passed."""
    cd = os.path.join(level_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse("no system/controlDict in %s" % level_dir)
    txt = open(cd).read()

    def one(key, what):
        m = re.search(r"^\s*%s\s+([0-9.eE+\-]+)\s*;" % key, txt, re.M)
        if not m:
            refuse("%s not found in %s -- %s" % (key, cd, what))
        return float(m.group(1))

    endt = one("endTime", "the graded physical end time")
    maxco = one("maxCo", "the stability constant fixed by the R3 §5.3 probe")
    maxdt = one("maxDeltaT", "the stability constant fixed by the R3 §5.3 probe")
    n = re.search(r"nPoints\s+([0-9]+)\s*;", txt)
    if not n:
        refuse("nPoints not found in %s -- the D1 refining-sampler assert cannot run" % cd)
    if not strict:
        return endt, int(n.group(1)), maxco, maxdt
    ats = re.search(r"^\s*adjustTimeStep\s+(\w+)\s*;", txt, re.M)
    if not ats or ats.group(1) != "yes":
        refuse("%s: adjustTimeStep is not `yes`; this is not the graded configuration" % cd)
    if abs(endt - ENDTIME_GRADED) > TIME_RTOL * ENDTIME_GRADED:
        refuse("%s: endTime %g is not the GRADED %g -- this is not the registered run"
               % (cd, endt, ENDTIME_GRADED))
    if abs(maxco - MAXCO_GRADED) > 1e-12:
        refuse("%s: maxCo %g is not the GRADED %g.  The stability constants were fixed by a "
               "coarsest- and fine-level probe before R3's freeze and a run at any other "
               "value is not the registered run." % (cd, maxco, MAXCO_GRADED))
    if abs(maxdt - MAXDELTAT_GRADED) > 1e-15:
        refuse("%s: maxDeltaT %g is not the GRADED %g" % (cd, maxdt, MAXDELTAT_GRADED))
    return endt, int(n.group(1)), maxco, maxdt


def assert_refining_sampler(level_dir, level):
    """D1 -- the sampler must be the level's own.  Expected nPoints = 2*(NXA+NXB)+1, read
    from the level's OWN blockMeshDict, so this checks the mesh that actually ran."""
    bm = os.path.join(level_dir, "system", "blockMeshDict")
    if not os.path.isfile(bm):
        refuse("no system/blockMeshDict in %s (D1 assert)" % level_dir)
    counts = re.findall(r"hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)", open(bm).read())
    if len(counts) != 2:
        refuse("expected 2 hex blocks in %s, found %d (D1 assert)" % (bm, len(counts)))
    nx_total = int(counts[0][0]) + int(counts[1][0])
    endt, npoints, _, _ = read_controls(level_dir)
    # W3: the controlDict that RAN must carry exactly two writeIntervals -- the fields at
    # endTime and the centreline every SAMPLE_DT.  This is what makes the import-time
    # window-occupancy arithmetic apply to THIS level: the identity is proved from frozen
    # constants, and this limb proves the level actually ran with those constants.
    wi = sorted(set(float(v) for v in re.findall(
        r"^\s*writeInterval\s+([0-9.eE+\-]+)\s*;", open(
            os.path.join(level_dir, "system", "controlDict")).read(), re.M)))
    want = sorted({ENDTIME_GRADED, SAMPLE_DT})
    if len(wi) != len(want) or any(abs(a - b) > TIME_RTOL * max(b, 1e-30)
                                   for a, b in zip(wi, want)):
        refuse("%s: controlDict writeIntervals are %s, expected %s (fields at endTime, "
               "centreline every SAMPLE_DT) -- this is not the graded configuration, and "
               "the %d-samples-per-plateau-window guarantee does not hold for it"
               % (level, wi, want, FROZEN_ARITHMETIC["per_window"]))
    expected = 2 * nx_total + 1
    if npoints != expected:
        refuse("D1 VIOLATED at %s: nPoints=%d but the mesh has %d axial cells, so the "
               "refining-sampler rule nPoints=2*Nx+1 demands %d.  The sampler is not "
               "refining with the mesh." % (level, npoints, nx_total, expected))
    span = 1.998 - 0.002
    s_samp = span / (npoints - 1)
    dx_mesh = 2.0 / nx_total
    return dict(nx=nx_total, npoints=npoints, s=s_samp, dx=dx_mesh, ratio=s_samp / dx_mesh)


def latest_time_dir(level_dir):
    times = [(float(d), d, os.path.join(level_dir, d)) for d in os.listdir(level_dir)
             if os.path.isdir(os.path.join(level_dir, d))
             and re.match(r"^[0-9]+(\.[0-9]+)?$", d) and float(d) != 0.0]
    if not times:
        refuse("no non-zero numeric time dir in %s" % level_dir)
    return max(times)[1:]


def centreline_history(level_dir, endtime):
    """-> [(time, path)] sorted.  The history must be COMPLETE: every multiple of SAMPLE_DT
    up to endTime.  A missing sample must refuse, never silently shrink a plateau window.

    W1 NOTE, BECAUSE THE DISTINCTION IS THE WHOLE REPAIR: THIS FUNCTION READS NO SAMPLE.
    It enumerates directory names and tests file EXISTENCE, which is a structural check on
    the run and stays exactly as strict as it was in R2 and R3 -- all 160 samples must be
    there.  What R4 changes is which of those files are OPENED AND PARSED, and that is
    registered_window()'s job below."""
    base = os.path.join(level_dir, "postProcessing", "centreline")
    if not os.path.isdir(base):
        refuse("no postProcessing/centreline in %s" % level_dir)
    hist = []
    for d in os.listdir(base):
        p = os.path.join(base, d, "line_T_U.xy")
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and os.path.isfile(p):
            hist.append((float(d), p))
    hist.sort()
    want = int(round(endtime / SAMPLE_DT))
    if len(hist) != want:
        refuse("centreline history has %d samples, expected %d (endTime %g every %g s): %s"
               % (len(hist), want, endtime, SAMPLE_DT, base))
    for k in range(1, want + 1):
        t_want = k * SAMPLE_DT
        if abs(hist[k - 1][0] - t_want) > TIME_RTOL * endtime:
            refuse("centreline history is not the complete %g s sequence at index %d "
                   "(found %g, expected %g): %s"
                   % (SAMPLE_DT, k, hist[k - 1][0], t_want, base))
    return hist


# ---- W1: THE REGISTERED WINDOW ---------------------------------------------
def registered_window(hist, endtime):
    """THE SAMPLES THIS GATE IS REGISTERED TO CONSUME, AND NO OTHERS.

    The gate reads a peak-to-peak over two adjacent windows of W = endTime/W_FRACTION
    seconds and the drift between their means.  Every graded quantity -- P1, P2, P3,
    x_level, x_final -- is a function of the samples with

        t > endTime - N_WINDOWS*W        i.e.  t in (0.064, 0.080] for the graded clock

    and of NO OTHER SAMPLE.  R3's comparator computed the shock location for all 160
    samples and only then discarded 128 of them.  Those 128 could not change a single
    graded number, but any one of them could REFUSE THE WHOLE GRADE -- and one did: the
    t = 0.0005 s sample, 0.6 % into the transient, where no shock has formed yet and the
    interpolating reader correctly returns None.

    A READER THAT CONSUMES DATA ITS OWN GATE NEVER ASKED FOR IS READING SOMETHING ELSE'S
    EVIDENCE.  The refusal was right about the sample and wrong about the question."""
    W = endtime / float(W_FRACTION)
    eps = TIME_RTOL * endtime
    lo = endtime - N_WINDOWS * W - eps
    sel = [(t, p) for t, p in hist if t > lo]
    need = N_WINDOWS * MIN_WINDOW_SAMPLES
    if len(sel) < need:
        refuse("the registered window t in (%.6g, %.6g] holds %d samples, below the "
               "registered minimum of %d (%d windows x %d): a peak-to-peak over fewer "
               "samples is not a peak-to-peak"
               % (endtime - N_WINDOWS * W, endtime, len(sel), need,
                  N_WINDOWS, MIN_WINDOW_SAMPLES))
    return sel, (endtime - N_WINDOWS * W, endtime)


def audit_window_only(level, bounds, hist, run_root):
    """W1's PROOF, AND IT IS A MEASUREMENT OF THE RUN THAT PRODUCED THE VERDICT.

    Every centreline path this comparator opened for this level is compared against the
    set of paths inside the registered window.  A read outside it REFUSES the grade.  This
    cannot be satisfied by a comment, by a docstring or by the author's intention: it is
    satisfied only by the code having actually opened nothing else."""
    lo, hi = bounds
    inside = set(os.path.realpath(p) for t, p in hist if lo - TIME_RTOL * hi < t <= hi)
    read = set(_audit_paths())

    # ---- §2aw (c) REPAIR (VERIFICATION_CHARTER v1.68, grant fa3ab580) ------------
    # W1's SUBJECT IS THE CASE'S DATA.  The planted controls write and re-read their own
    # synthetic samples in a temp dir, through this same audited reader; those are the
    # AUDITOR'S OWN ARTIFACTS, not run data, and were never in W1's scope.  §2aw.4:
    # "an audit's subject is the case's data; the auditor's own artifacts were never in
    # scope, and excluding them narrows nothing that W1 was ever measuring."
    #
    # THE GROUND IS SEMANTIC AND VALUE-FREE.  Nothing computed, compared or thresholded
    # is touched: shock_series, plateau, the gate (1.250 m +-5 %) and DELTA_X are
    # untouched, and any change to them is void under this grant (§2aw.5).
    #
    # WHY THIS IS NOT (d).  A read of a REAL sample outside the window still lies INSIDE
    # the run root, so it is still audited and still refuses -- the hazard W1 exists to
    # catch.  Snapshot-and-restore around the plants would have masked it, which is the
    # stated reason (d) was rejected.  _audit_with_outside_read() drives exactly that.
    root = os.path.realpath(run_root).rstrip(os.sep) + os.sep
    run_reads = set(p for p in read if p.startswith(root))
    excluded = sorted(read - run_reads)

    outside = sorted(run_reads - inside)
    if outside:
        refuse("%s: W1 VIOLATED -- the comparator opened %d centreline sample(s) OUTSIDE "
               "its registered window t in (%.6g, %.6g]: %s%s.  A reader that consumes "
               "data the gate never asked for can be refused by data the gate never asked "
               "for, which is exactly how R3 failed to grade."
               % (level, len(outside), lo, hi, ", ".join(outside[:3]),
                  " ..." if len(outside) > 3 else ""))
    # THE EMPTY CHECK KEYS ON run_reads, NOT read.  Keying it on `read` would let the
    # plants' own scratch reads satisfy it vacuously -- a control that cannot fail.
    if not run_reads:
        refuse("%s: W1 AUDIT IS EMPTY -- no centreline sample INSIDE THE RUN ROOT was "
               "recorded as read, so the window property is vacuously true and proves "
               "nothing.  A control that cannot fail is not a control (rule 3)." % level)
    return dict(n_read=len(run_reads), n_window=len(inside), lo=lo, hi=hi,
                n_excluded=len(excluded), excluded=excluded)


# ---- the plateau (D2 + D4) --------------------------------------------------
def shock_series(win):
    """-> [(t, x_shock)] over the REGISTERED WINDOW ONLY (W1).

    The refusal for a genuinely missing crossing INSIDE the window is UNCHANGED from R2
    and R3, and it is a real limb: a window sample with no downward M = 1 crossing means
    the shock is not resolvable in a profile the gate depends on, and reporting a location
    from it would be a guess."""
    out = []
    for t, p in win:
        x = shock_location(to_mach(read_centreline_raw(p)))
        if x is None:
            refuse("no downward Mach=1 crossing in sample %s -- the shock is not resolvable "
                   "in this profile, and this sample is INSIDE the registered plateau "
                   "window, so the gate depends on it; refusing rather than reporting a "
                   "location" % p)
        out.append((t, x))
    return out


def windows(series, endtime):
    """Two ADJACENT windows of W = endTime/W_FRACTION seconds each, sharing one boundary
    sample.  A: (endTime-W, endTime].  B: (endTime-2W, endTime-W].

    UNCHANGED FROM R3 IN BEHAVIOUR.  Its input is now already restricted to
    (endTime-2W, endTime], which is the union of A and B, so A and B are identical to what
    R3 computed -- see the selftest's BIT-IDENTITY arm."""
    W = endtime / float(W_FRACTION)
    eps = TIME_RTOL * endtime
    A = [(t, x) for t, x in series if t >= endtime - W - eps]
    B = [(t, x) for t, x in series
         if endtime - 2 * W - eps <= t <= endtime - W + eps]
    if len(A) < MIN_WINDOW_SAMPLES or len(B) < MIN_WINDOW_SAMPLES:
        refuse("plateau windows hold %d / %d samples, need >= %d each (W=%g s, interval "
               "%g s): a peak-to-peak over fewer samples is not a peak-to-peak"
               % (len(A), len(B), MIN_WINDOW_SAMPLES, W, SAMPLE_DT))
    return W, A, B


def ptp(win):
    xs = [x for _, x in win]
    return max(xs) - min(xs)


def mean(win):
    xs = [x for _, x in win]
    return sum(xs) / len(xs)


def plateau(series, endtime):
    W, A, B = windows(series, endtime)
    p1, p2 = ptp(A), ptp(B)
    p3 = abs(mean(A) - mean(B))
    p0 = abs(series[-1][1] - series[-2][1])
    ok = (p1 <= DELTA_X) and (p2 <= DELTA_X) and (p3 <= DELTA_X)
    return dict(W=W, A=A, B=B, p0=p0, p1=p1, p2=p2, p3=p3, ok=ok,
                x_level=mean(A), x_final=series[-1][1])


# ---- planted controls (CLAUDE.md rule 3) ------------------------------------
#
# THE RULE THESE CONTROLS ARE BUILT TO:
#
#   A PLANTED CONTROL MUST BE DESIGNED AGAINST THE *REDUCTION*, NOT AGAINST THE FIELD.
#     for a MEAN          -> plant a proper subset
#     for a PEAK-TO-PEAK  -> plant the current EXTREMUM
#     for a MAX           -> plant the ARGMAX
#   A PLANT THAT DOES NOT MOVE THE SPECIFIC STATISTIC THE GATE READS IS INERT NO MATTER HOW
#   LARGE IT IS.
#
# THREE plant-design defects have been paid for in this family, each by a measurement:
#   CANCELLATION -- a plant covering the WHOLE reduction set is a rigid translation and the
#                   ptp is identically unchanged (PLANT C1 demonstrates it deliberately);
#   ABSORPTION   -- a plant into an INTERIOR member is swallowed whole when the window
#                   already spreads wider than the plant.  Measured on real data: a 1.0e-02
#                   m interior plant into a window of spread 1.1066e-01 m left the ptp
#                   UNCHANGED.  PLANT B therefore plants the window's MAXIMUM.
#   ANSWER-DEPENDENCE -- R2's PLANT C asserted an invariance that holds only if the shock is
#                   already steady.  A CONTROL WHOSE VALIDITY DEPENDS ON THE ANSWER IT IS
#                   CHECKING IS NOT A CONTROL.  PLANT C1 + PLANT C2 replace it.
# ALL FIVE PLANTS ARE CARRIED FORWARD FROM R3 UNCHANGED IN DESIGN AND IN TOLERANCE.
def _shift_profile(raw, dx):
    """Return rows whose FIELD values are the original field sampled at (x - dx), so the
    whole profile -- and with it the shock -- moves by exactly +dx.  Clamped at the ends."""
    xs = [r[0] for r in raw]
    out = []
    for x, _, _, _, _ in raw:
        xq = x - dx
        if xq <= xs[0]:
            src = raw[0][1:]
        elif xq >= xs[-1]:
            src = raw[-1][1:]
        else:
            j = 1
            while xs[j] < xq:
                j += 1
            f = (xq - xs[j - 1]) / (xs[j] - xs[j - 1])
            src = tuple(raw[j - 1][k] + f * (raw[j][k] - raw[j - 1][k]) for k in range(1, 5))
        out.append((x,) + tuple(src))
    return out


def _write_raw(path, rows):
    with open(path, "w") as fh:
        for r in rows:
            fh.write("\t".join("%.12g" % v for v in r) + "\n")


def plant_gate_reader(sample_path, dx=PLANT_DX, reader=None):
    """PLANT A -- the GATE reader must see a known shock displacement.
    Planted into a SCRATCH COPY; the run output is never touched."""
    reader = reader or shock_location
    raw = read_centreline_raw(sample_path)
    x0 = reader(to_mach(raw))
    if x0 is None:
        refuse("plant A: no shock in the unplanted sample %s" % sample_path)
    s = raw[1][0] - raw[0][0]
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_plantA_")
    try:
        dst = os.path.join(tmp, "line_T_U.xy")
        _write_raw(dst, _shift_profile(raw, dx))
        x1 = reader(to_mach(read_centreline_raw(dst)))
        if x1 is None:
            refuse("PLANTED CONTROL A FAILED: the reader lost the shock after a %+.3e m "
                   "plant (rule 3)" % dx)
        err = abs((x1 - x0) - dx)
        tol = PLANT_C2_TOL * abs(dx)   # scales WITH THE PLANT, never with the mesh
        if err > tol:
            refuse("PLANTED CONTROL A FAILED: planted %+.4e m, reader saw %+.4e m "
                   "(error %.3e > 25 %% of the plant, %.3e).  A reader not shown able to "
                   "see a known displacement cannot report a zero (rule 3).  file=%s"
                   % (dx, x1 - x0, err, tol, sample_path))
        return dict(x0=x0, x1=x1, planted=dx, err=err, spacing=s, tol=tol)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def plant_plateau_reducer(window, dx=PLANT_DX, reader=None):
    """PLANT B -- the PLATEAU REDUCER, and the subset is a PROPER subset AND is the
    window's CURRENT MAXIMUM, which is not a detail: shifting an INTERIOR sample by +dx
    changes the ptp by NOTHING whenever the window already spreads wider than dx."""
    reader = reader or shock_location
    base_pts = []
    for t, path in window:
        x = reader(to_mach(read_centreline_raw(path)))
        if x is None:
            refuse("plant B: shock lost in an UNPLANTED window member: %s" % path)
        base_pts.append((t, x))
    base = ptp(base_pts)
    argmax = max(range(len(base_pts)), key=lambda i: base_pts[i][1])
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_plantB_")
    try:
        new = []
        for k, (t, path) in enumerate(window):
            raw = read_centreline_raw(path)
            if k == argmax:
                dst = os.path.join(tmp, "s%d.xy" % k)
                _write_raw(dst, _shift_profile(raw, dx))
                raw = read_centreline_raw(dst)
            x = reader(to_mach(raw))
            if x is None:
                refuse("plant B: shock lost in window member %d" % k)
            new.append((t, x))
        got = ptp(new)
        if not (got >= base + 0.75 * dx):
            refuse("PLANTED CONTROL B FAILED: a %+.4e m displacement planted into the "
                   "MAXIMUM of %d window samples moved the peak-to-peak only from %.4e to "
                   "%.4e (needed >= %.4e).  The plateau reducer cannot see a known "
                   "non-zero, so its ptp is not evidence of a plateau (rule 3)."
                   % (dx, len(window), base, got, base + 0.75 * dx))
        return dict(base=base, got=got, idx=argmax)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def plant_series_translation(series_pts, dx=PLANT_DX):
    """PLANT C1 -- THE CANCELLATION DEMONSTRATION, MOVED TO THE REDUCTION WHERE THE CLAIM
    ACTUALLY LIVES.

    THE PREMISE, AND IT IS AN IDENTITY OF THE REALS:
        max(x_i + d) - min(x_i + d)  ==  max(x_i) - min(x_i)
    It is true whether the shock is steady, hunting over 38 cells, or absent.  It is
    INDEPENDENT OF THE ANSWER, which is exactly the property R2's PLANT C lacked.

    IT IS NOT A TAUTOLOGY AND IT CAN FAIL: it fails the moment `ptp` is mutated into a
    reducer that is not translation-invariant -- a relative spread, a normalised range, a
    max|x| -- and such a mutation would silently change the plateau verdict.  The LIVE arm
    below proves the inertness comes from THE COVERING and not from a dead helper."""
    xs = [x for _, x in series_pts]
    base = max(xs) - min(xs)

    shifted = [x + dx for x in xs]
    got_inert = max(shifted) - min(shifted)
    if abs(got_inert - base) > 1e-12 * max(abs(dx), 1.0):
        refuse("PLANT C1 INERT ARM FAILED: adding %+.4e m to EVERY member of the x_shock "
               "series moved the peak-to-peak from %.6e to %.6e (change %.3e).  The "
               "plateau reducer is not translation-invariant, so it is not a peak-to-peak; "
               "a non-translation-invariant reducer changes the plateau verdict silently "
               "(rule 3)." % (dx, base, got_inert, got_inert - base))

    live = list(xs)
    live[max(range(len(xs)), key=lambda i: xs[i])] += dx
    got_live = max(live) - min(live)
    if abs((got_live - base) - dx) > 1e-12 * max(abs(dx), 1.0):
        refuse("PLANT C1 LIVE ARM FAILED: adding %+.4e m to the ARGMAX of the x_shock "
               "series moved the peak-to-peak by %.6e, not %.6e.  The inert arm's zero is "
               "therefore not evidence of a covering -- it may be a dead reducer (rule 3)."
               % (dx, got_live - base, dx))
    return dict(base=base, inert=got_inert, live=got_live)


def plant_field_readback_per_sample(window, dx=PLANT_DX, reader=None):
    """PLANT C2 -- THE FIELD-LEVEL CONTACT R2's PLANT C HAD, WITH THE STEADINESS PREMISE
    REMOVED.  It recovers the planted displacement PER SAMPLE, INDEPENDENTLY, and requires
    each to be within 25 % of the plant -- PLANT A's tolerance, applied N times instead of
    once.  It asserts NOTHING about the relationship between samples, which is exactly
    where R2's premise entered."""
    reader = reader or shock_location
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_plantC2_")
    try:
        d = []
        for k, (t, path) in enumerate(window):
            raw = read_centreline_raw(path)
            x0 = reader(to_mach(raw))
            if x0 is None:
                refuse("plant C2: shock lost in an UNPLANTED window member: %s" % path)
            dst = os.path.join(tmp, "s%d.xy" % k)
            _write_raw(dst, _shift_profile(raw, dx))
            x1 = reader(to_mach(read_centreline_raw(dst)))
            if x1 is None:
                refuse("PLANT C2 FAILED: the reader lost the shock after a %+.3e m plant "
                       "in window member %d (%s)" % (dx, k, path))
            d.append(x1 - x0)
        tol = PLANT_C2_TOL * abs(dx)
        worst = max(abs(v - dx) for v in d)
        if worst > tol:
            refuse("PLANT C2 FAILED: a rigid %+.4e m field shift was recovered per-sample "
                   "as %.4e .. %.4e over %d window members; worst error %.3e exceeds 25 %% "
                   "of the plant (%.3e).  The reader is not recovering a KNOWN displacement "
                   "on these profiles, so its x_shock series is not evidence (rule 3)."
                   % (dx, min(d), max(d), len(d), worst, tol))
        return dict(d_min=min(d), d_max=max(d), spread=max(d) - min(d), worst=worst,
                    tol=tol, n=len(d))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def plant_T_field(path, k=PLANT_K_T):
    """PLANT D -- the physical field reader, carried over unchanged in intent."""
    vals, span = read_T_internal(path)
    scale = max(abs(v) for v in vals)
    plant = k * scale
    if plant < 1.0e-12:
        refuse("planted-zero: T field scale %.3g too small" % scale)
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_plantT_")
    try:
        dst = os.path.join(tmp, "T")
        txt = open(path).read()
        bumped = [v + plant for v in vals]
        newblock = ("internalField   nonuniform List<scalar>\n%d\n(\n%s\n)\n;"
                    % (len(bumped), "\n".join("%.10g" % v for v in bumped)))
        open(dst, "w").write(txt[:span[0]] + newblock + txt[span[1]:])
        seen, _ = read_T_internal(dst)
        if len(seen) != len(vals):
            refuse("planted-zero: T cell count changed across the plant")
        worst = max(abs((seen[i] - vals[i]) - plant) for i in range(len(vals)))
        if worst > 1e-6 * max(abs(plant), 1.0):
            refuse("PLANTED CONTROL D FAILED (T-field reader): planted %.6g, worst read-back "
                   "error %.3g (rule 3)" % (plant, worst))
        return dict(plant=plant, err=worst, n=len(vals))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- N4 REPLACEMENT (R6): the reconstructed T field must lie in the PHYSICAL RANGE ------
def check_T_physical_range(t_path, level):
    """N4 REPLACEMENT -- A REFUSAL LIMB, NOT A PRINTED DIAGNOSTIC.

    rhoCentralFoam has NO fvOptions limitTemperature (verified at source; see T_MAX_PHYS/
    T_MIN_PHYS above), so R4/R5's "the limiter must be non-binding" limb has no subject in
    R6.  It is replaced by an equivalent physical-range refusal derived from the frozen
    thermo: the reconstructed T field at endTime must lie within [T_MIN_PHYS, T_MAX_PHYS]
    = [50, 1000] K.  This is the density-based analogue of N4 -- where rhoPimpleFoam's
    fvOptions limiter would have CLAMPED a blow-up (and N4 caught the clamp), rhoCentralFoam
    has no clamp, so a blow-up shows up DIRECTLY as an out-of-range reconstructed T, and
    THIS limb catches it.  Non-binding on the true field (static T ~ [254, 500] K)."""
    vals, _ = read_T_internal(t_path)
    lo, hi = min(vals), max(vals)
    if lo < T_MIN_PHYS or hi > T_MAX_PHYS:
        refuse("%s: N4(R6) VIOLATED -- reconstructed T at endTime spans [%.4g, %.4g] K, "
               "outside the physical envelope [%.4g, %.4g] K derived from the frozen total "
               "temperature T0 = %.1f K.  rhoCentralFoam has no limitTemperature to clamp "
               "this, so an out-of-range T is a KNP numerical failure, not the registered "
               "physics." % (level, lo, hi, T_MIN_PHYS, T_MAX_PHYS, T0_TOTAL))
    return dict(lo=lo, hi=hi)


# ---- strict completion (CLAUDE.md rule 4) -----------------------------------
def check_completion(level_dir, level):
    """CLAUDE.md rule 4, with ONE DECLARED DEPARTURE (N2), carried forward from R3
    unchanged and consistent with VMFL051's own frozen DEPARTURE 2.

    R2's limb was `count of ExecutionTime lines == endTime`.  That is IDENTICALLY the
    iteration count only for a STEADY solver where one iteration prints one line and
    endTime IS the iteration count.  For an adaptive-time-step transient run,
    int(round(0.080)) = 0 against ~35 000 lines and the limb refuses every level.  RULE 4 IS
    NOT THE PROBLEM; THAT IMPLEMENTATION OF IT IS.

    THE REPLACEMENT IS STRICTLY STRONGER, and every term is computable from frozen
    constants:
      (a) n(ExecutionTime) == n(Time =)        -- every advanced step printed its cost
      (b) last Time == endTime within maxDeltaT -- the run advanced all the way
      (c) n(Time =) >= endTime / maxDeltaT      -- it cannot have got there in fewer steps
      (d) the Time sequence is STRICTLY INCREASING -- which catches a restart splice that
          a bare count never would, and which R2's limb did not test at all.

    ⚠ AND LIMB (a) IS WHAT WOULD HAVE CAUGHT R3's L2 AND L3 EVEN IF THEIR rc HAD BEEN
    FORGED: both logs end mid-run with no `End` line, last Time 0.0731877615 and
    0.0793715355 against endTime 0.080.  A cap kill is a rule-4 failure at four limbs at
    once, not a value with a caveat."""
    rcf = os.path.join(level_dir, "RUN_RC")
    if not os.path.isfile(rcf):
        refuse("%s: RUN_RC absent -- the driver's exit code was never recorded (rule 4)" % level)
    rc = open(rcf).read().strip()
    if rc != "0":
        refuse("%s: RUN_RC = %s, not 0 (rule 4).  rc 124 is a CAP KILL: the run was stopped "
               "by its own registered cap and is NOT A RESULT (budget/kill class)."
               % (level, rc))
    log = os.path.join(level_dir, "log.rhoCentralFoam")
    if not os.path.isfile(log):
        refuse("%s: log.rhoCentralFoam absent (rule 4)" % level)
    txt = open(log).read()
    if "FOAM FATAL" in txt:
        refuse("%s: FOAM FATAL in the solver log (rule 4)" % level)
    if not re.search(r"^End\s*$", txt, re.M):
        refuse("%s: no 'End' line in the solver log (rule 4)" % level)

    endt, _, _, maxdt = read_controls(level_dir)
    times = [float(v) for v in re.findall(r"^Time = ([0-9.eE+\-]+)\s*$", txt, re.M)]
    n_exec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if not times:
        refuse("%s: no 'Time =' lines in the solver log (rule 4, N2a)" % level)
    if n_exec != len(times):
        refuse("%s: %d ExecutionTime lines against %d Time lines -- the log is truncated "
               "mid-step (rule 4, N2a)" % (level, n_exec, len(times)))
    if abs(times[-1] - endt) > maxdt:
        refuse("%s: the log's last Time %g is not endTime %g within maxDeltaT %g "
               "(rule 4, N2b) -- the run stopped early" % (level, times[-1], endt, maxdt))
    n_min = int(math.floor(endt / maxdt))
    if len(times) < n_min:
        refuse("%s: %d time steps to reach endTime %g, but maxDeltaT %g makes %d the "
               "minimum possible -- the log cannot be the whole run (rule 4, N2c)"
               % (level, len(times), endt, maxdt, n_min))
    for i in range(1, len(times)):
        if not (times[i] > times[i - 1]):
            refuse("%s: the Time sequence is not strictly increasing at index %d "
                   "(%g after %g) -- this log is a restart splice, not one run "
                   "(rule 4, N2d)" % (level, i, times[i], times[i - 1]))

    tname, tpath = latest_time_dir(level_dir)
    if abs(float(tname) - endt) > TIME_RTOL * endt:
        refuse("%s: last time dir %s != endTime %g (rule 4)" % (level, tname, endt))
    zero_T = os.path.join(level_dir, "0", "T")
    if not os.path.isfile(zero_T):
        refuse("%s: 0/T absent -- the age guard has no reference (rule 4)" % level)
    z = os.path.getmtime(zero_T)
    for f in ("T", "U", "p"):
        fp = os.path.join(tpath, f)
        if not os.path.isfile(fp):
            refuse("%s: field %s missing at %s (rule 4)" % (level, f, tname))
        if not os.path.getmtime(fp) > z:
            refuse("%s: AGE GUARD (rule 4) -- %s at %s is not newer than the case's own 0/T"
                   % (level, f, tname))
    return endt, tname, tpath, len(times)


# ---- Roache -----------------------------------------------------------------
def roache(f1, f2, f3):
    d12, d23 = (f2 - f1), (f3 - f2)
    if abs(d23) < 1e-30:
        return {"state": "EXACT", "R": 0.0, "p": None, "gci": None}
    R = d23 / d12 if abs(d12) > 1e-30 else float("inf")
    if not (0.0 < R < 1.0):
        return {"state": "OSCILLATORY" if R < 0 else "DIVERGENT", "R": R, "p": None, "gci": None}
    p = math.log(abs(d12 / d23)) / math.log(R_REFINE)
    gci = FS * abs(d23 / f3) / (R_REFINE ** p - 1.0) if abs(f3) > 1e-30 else None
    return {"state": "CONVERGING", "R": R, "p": p, "gci": gci}


# ---- §39.5 path check -------------------------------------------------------
READ_PATHS = [
    "<L>/RUN_RC",
    "<L>/log.rhoCentralFoam",
    "<L>/system/controlDict",
    "<L>/system/blockMeshDict",
    "<L>/0/T",
    "<L>/<endTime>/T", "<L>/<endTime>/U", "<L>/<endTime>/p",
    "<L>/postProcessing/centreline/<k*SAMPLE_DT>/line_T_U.xy   "
    "-- EXISTENCE checked for all k = 1..endTime/SAMPLE_DT; "
    "OPENED only for t in (endTime-2W, endTime]  (W1)",
]


def check_paths(run_root, levels=("L1", "L2", "L3")):
    """charter §39.5 -- every path this comparator reads, checked to EXIST in a real run
    root.  A --selftest pass proves logic, never interface."""
    bad = 0
    for L in levels:
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            print("  %-3s ABSENT: %s" % (L, ld)); bad += 1; continue
        # strict=False on purpose -- see read_controls.  The enumerator must be able to make
        # contact with a CLAUSE-B smoke root, whose endTime is deliberately not the graded
        # one; the graded assertions are enforced in grade(), which this path never reaches.
        endt, _, _, _ = read_controls(ld, strict=False)
        sdt = SAMPLE_DT
        m = re.findall(r"^\s*writeInterval\s+([0-9.eE+\-]+)\s*;", open(
            os.path.join(ld, "system", "controlDict")).read(), re.M)
        cand = sorted(set(float(v) for v in m))
        if cand:
            sdt = min(cand)
        want = [os.path.join(ld, "RUN_RC"), os.path.join(ld, "log.rhoCentralFoam"),
                os.path.join(ld, "system", "controlDict"),
                os.path.join(ld, "system", "blockMeshDict"),
                os.path.join(ld, "0", "T")]
        tn = ("%g" % endt)
        want += [os.path.join(ld, tn, f) for f in ("T", "U", "p")]
        want += [os.path.join(ld, "postProcessing", "centreline", "%g" % sdt,
                              "line_T_U.xy"),
                 os.path.join(ld, "postProcessing", "centreline", tn, "line_T_U.xy")]
        for w in want:
            ok = os.path.exists(w)
            if not ok:
                bad += 1
            print("  %-3s %-6s %s" % (L, "OK" if ok else "MISSING", w))
    return bad


# ---- grade ------------------------------------------------------------------
def grade(run_root):
    print("VMFL046-R6  Supersonic flow with a normal shock in a CD nozzle (VM2026R1 p.155)")
    print("solver: rhoCentralFoam (DENSITY-BASED, TRANSIENT), fluxScheme Kurganov (KNP),")
    print("        reconstruct(rho/U/T) vanLeer, ddtSchemes Euler, maxCo 0.2 -- Greenshields")
    print("        et al. (2010).  R6 changes vs R5: SOLVER (rhoPimpleFoam->rhoCentralFoam)")
    print("        and the OUTLET relaxation length (waveTransmissive lInf 2.0->0.3).  The")
    print("        gate, DELTA_X, endTime, mesh, r=2 triple and every gate limb are UNCHANGED;")
    print("        N4 (limitTemperature) is REPLACED by a physical-range T refusal (no fvOption).")
    print("gate  : x_shock vs %.3f m, band +-%.1f %% (= +-%.4f m)  -- UNCHANGED from R1/R2/R3"
          % (ANALYTICAL_SHOCK, 100 * SHOCK_TOL, BAND))
    print("plateau: ptp(x_shock) over two adjacent W=endTime/%d windows AND their mean drift"
          " <= DELTA_X = %.3e m -- UNCHANGED" % (W_FRACTION, DELTA_X))
    print("        reader = INTERPOLATING last downward M=1 crossing, and it CONSUMES ONLY")
    print("        the registered window t in (%.6g, %.6g] -- %d of the %d samples (W1)"
          % (ENDTIME_GRADED - N_WINDOWS * FROZEN_ARITHMETIC["W"], ENDTIME_GRADED,
             FROZEN_ARITHMETIC["window_total"], FROZEN_ARITHMETIC["n_total"]))
    print("frozen arithmetic (W3): %d samples total, %d per plateau window (>= %d), the "
          "two windows sharing one boundary sample for %d distinct, %.1f steps per sample"
          % (FROZEN_ARITHMETIC["n_total"], FROZEN_ARITHMETIC["per_window"],
             MIN_WINDOW_SAMPLES, FROZEN_ARITHMETIC["window_total"],
             FROZEN_ARITHMETIC["steps_per_sample"]))
    print("probe-length floor (W2): %.2f of the graded clock; this registration's cost "
          "basis covers %s" % (PROBE_FLOOR, ", ".join(
              "%s %.4f" % (L, COST_BASIS_FRACTION[L]) for L in ("L1", "L2", "L3"))))
    print()

    st, xs_level = {}, []
    for L in ("L1", "L2", "L3"):
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            refuse("level directory absent: %s" % ld)
        endt, tname, tpath, nsteps = check_completion(ld, L)
        samp = assert_refining_sampler(ld, L)
        lim = check_T_physical_range(os.path.join(tpath, "T"), L)
        hist = centreline_history(ld, endt)

        # ---- W1: the window is selected BEFORE any sample is opened, and the audit is
        # armed here so it covers every read that contributes to THIS level's verdict.
        _audit_reset()
        win, bounds = registered_window(hist, endt)
        ser = shock_series(win)
        pl = plateau(ser, endt)

        # ---- §2av REPAIR (VERIFICATION_CHARTER v1.67, grant 8bdd5351) ---------------
        # plateau() returns A as SERIES points [(t, x_shock)]; plant_plateau_reducer and
        # plant_field_readback_per_sample take a WINDOW [(t, path)] and iterate
        # `for t, path in window`, so they received a float where a path was required and
        # crashed in read_centreline_raw.  shock_series(win) maps win one-for-one and
        # preserves order, and windows() selects A by `t >= endtime - W - eps` over a
        # time-ordered series, so A is a contiguous SUFFIX -- window A's (t, path) pairs
        # are the corresponding suffix of win.  The argument is FORCED by the signatures;
        # nothing computed, compared or thresholded is touched (§2av.5 requirement 3).
        winA = win[len(ser) - len(pl["A"]):]
        if [t for t, _ in winA] != [t for t, _ in pl["A"]]:
            refuse("§2av repair: winA time-stamps do not match plateau window A -- the "
                   "suffix correspondence shock_series() guarantees does not hold, so the "
                   "plants would be planted into the wrong samples")

        pa = plant_gate_reader(win[-1][1])
        pb = plant_plateau_reducer(winA)
        pc1 = plant_series_translation(pl["A"])
        pc2 = plant_field_readback_per_sample(winA)
        pd = plant_T_field(os.path.join(tpath, "T"))

        cl_last = to_mach(read_centreline_raw(win[-1][1]))
        aud = audit_window_only(L, bounds, hist, ld)

        st[L] = dict(endt=endt, n=nsteps, pl=pl, samp=samp, lim=lim, aud=aud,
                     snap=shock_location_snapping(cl_last),
                     pa=pa, pb=pb, pc1=pc1, pc2=pc2, pd=pd)
        xs_level.append(pl["x_level"])

        dev = 100.0 * (pl["x_level"] - ANALYTICAL_SHOCK) / ANALYTICAL_SHOCK
        print("%s  endTime %.6g s in %d time steps  (sampler nPoints %d, spacing %.6e m, "
              "sampler/mesh %.6f)" % (L, endt, nsteps, samp["npoints"], samp["s"],
                                      samp["ratio"]))
        print("     W1 read audit: %d distinct centreline sample(s) OPENED inside the run "
              "root, all inside the registered window (%.6g, %.6g] which holds %d of the "
              "%d written samples"
              % (aud["n_read"], aud["lo"], aud["hi"], aud["n_window"], len(hist)))
        # §2aw.5 condition (3): the excluded paths are NAMED, in full, in the grade's own
        # output -- not summarised as a count.  A reader must be able to see that every
        # one of them is the comparator's own artifact and none is run data.
        print("     W1 §2aw(c) EXCLUDED from the audit as NOT RUN DATA (outside %s): %d"
              % (os.path.realpath(ld), aud["n_excluded"]))
        for _p in aud["excluded"]:
            print("        %s" % _p)
        print("     x_shock (window-A mean, THE LEVEL VALUE) = %.9f m   (%+.4f %% vs %.3f)"
              % (pl["x_level"], dev, ANALYTICAL_SHOCK))
        print("     x_shock (final sample)                   = %.9f m"
              % pl["x_final"])
        print("     plateau P1=%.4e  P2=%.4e  P3=%.4e   vs DELTA_X=%.3e  ->  %s"
              % (pl["p1"], pl["p2"], pl["p3"], DELTA_X,
                 "PLATEAU" if pl["ok"] else "NOT PLATEAUED"))
        print("     T at endTime spans [%.5g, %.5g] K -- physical envelope [%.4g, %.4g] K "
              "(from T0=%.0f) NON-BINDING (N4 REPLACEMENT: rhoCentralFoam has no "
              "limitTemperature)" % (lim["lo"], lim["hi"], T_MIN_PHYS, T_MAX_PHYS, T0_TOTAL))
        print("     plants: A err %.3e (tol %.3e) | B ptp %.4e->%.4e | C1 inert change "
              "%.3e, live +%.6e | C2 worst %.3e (tol %.3e), spread %.3e | D err %.3e"
              % (pa["err"], pa["tol"], pb["base"], pb["got"],
                 pc1["inert"] - pc1["base"], pc1["live"] - pc1["base"],
                 pc2["worst"], pc2["tol"], pc2["spread"], pd["err"]))
        print("     R1's node-snapping reader on the same bytes: %.9f m (quantum %.4e m, "
              "%.2fx DELTA_X -- unusable, which is why R2/R3/R4 interpolate)"
              % (st[L]["snap"], samp["s"], samp["s"] / DELTA_X))
        print()

    not_plateaued = [L for L in ("L1", "L2", "L3") if not st[L]["pl"]["ok"]]
    tri = roache(*xs_level)
    print("triple on x_shock: L1=%.6f L2=%.6f L3=%.6f  state=%s R=%.4g p=%s GCI=%s"
          % (xs_level[0], xs_level[1], xs_level[2], tri["state"], tri["R"],
             ("%.4f" % tri["p"]) if tri["p"] is not None else "n/a",
             ("%.4f %%" % (100 * tri["gci"])) if tri["gci"] is not None else "n/a"))
    print()

    # RULE 5 STEP 1 -- a level that is not plateaued yields no measurement, whatever its
    # value.  This is the same step that decided R2, and it is unchanged.
    if not_plateaued:
        print("VERDICT: NOT A RESULT")
        print("  reason: level(s) %s did not reach the pre-registered plateau at "
              "endTime %.6g s (CLAUDE.md rule 5 step 1)." % (", ".join(not_plateaued),
                                                             ENDTIME_GRADED))
        for L in not_plateaued:
            p = st[L]["pl"]
            print("    %s  P1=%.4e P2=%.4e P3=%.4e  (DELTA_X=%.3e; worst is %.1fx over)"
                  % (L, p["p1"], p["p2"], p["p3"], DELTA_X,
                     max(p["p1"], p["p2"], p["p3"]) / DELTA_X))
        return 1
    if tri["state"] != "CONVERGING":
        print("VERDICT: NOT A RESULT")
        print("  reason: the grid triple on x_shock is %s, not CONVERGING "
              "(CLAUDE.md rule 5 step 2).  The value is printed above and is not a result."
              % tri["state"])
        return 1

    x3 = xs_level[2]
    dev = abs(x3 - ANALYTICAL_SHOCK) / ANALYTICAL_SHOCK
    sec = []
    if not (P_OBS_LO <= tri["p"] <= P_OBS_HI):
        sec.append("observed order p=%.4f outside [%.2f, %.2f]" % (tri["p"], P_OBS_LO, P_OBS_HI))
    if tri["gci"] is not None and tri["gci"] > GCI_FINE_MAX:
        sec.append("fine-grid GCI %.4f > %.4f" % (tri["gci"], GCI_FINE_MAX))
    print("primary limb: |x_shock(L3) - %.3f| / %.3f = %.4f %%  vs band %.1f %%"
          % (ANALYTICAL_SHOCK, ANALYTICAL_SHOCK, 100 * dev, 100 * SHOCK_TOL))
    print("secondaries (DEMOTE-ONLY, charter §21.3 -- they may turn a pass into a fail and")
    print("             may NEVER license one; a secondary that does NOT fire is NOT")
    print("             evidence of quality, because both are contaminated-loose): %s"
          % ("; ".join(sec) if sec else "none fired"))
    print()
    if dev > SHOCK_TOL:
        print("VERDICT: GATE FAIL")
        print("  the settled, grid-converged shock sits outside the frozen 5 %% band.")
        return 1
    if sec:
        print("VERDICT: GATE FAIL   (primary inside the band; a DEMOTE-ONLY secondary fired)")
        return 1
    print("VERDICT: GATE REACHED")
    print("  the registered CEILING for this case (charter §21.2 model-sameness DIFFERENT:")
    print("  viscous 2-D Navier-Stokes against an inviscid quasi-1D reference).  PASS is")
    print("  unreachable here and this comparator contains no code path that prints it.")
    return 0


# ---- selftest ---------------------------------------------------------------
def _synth(n, x_shock, x0=0.002, x1=1.998, T=300.0, smear_cells=3.0):
    """A synthetic centreline whose shock sits at x_shock, written in the real 5-column
    `x T Ux Uy Uz` layout so the real readers consume it unmodified."""
    rows = []
    s = (x1 - x0) / (n - 1)
    w = smear_cells * s
    for i in range(n):
        x = x0 + i * s
        if x < 0.5:
            m = 0.30 + 1.4 * (x / 0.5)
        else:
            m_pre = 1.70 + 0.55 * (x - 0.5)
            m_post = 0.55 - 0.05 * (x - x_shock)
            if x <= x_shock - 0.5 * w:
                m = m_pre
            elif x >= x_shock + 0.5 * w:
                m = m_post
            else:
                f = (x - (x_shock - 0.5 * w)) / w
                m = m_pre + f * (m_post - m_pre)
        u = m * math.sqrt(GAMMA * R_GAS * T)
        rows.append((x, T, u, 0.0, 0.0))
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_synth_")
    _SYNTH_DIR.append(tmp)
    p = os.path.join(tmp, "line_T_U.xy")
    _write_raw(p, rows)
    return read_centreline_raw(p)


def _shockless(n, x0=0.002, x1=1.998, T=300.0):
    """A profile with NO downward M=1 crossing -- everywhere subsonic.  This is what the
    real t = 0.0005 s sample looks like: the transient has not formed a shock yet, and the
    interpolating reader correctly returns None on it.  R3's comparator consumed 128 such
    early samples per level and refused the whole grade on the first one."""
    rows = []
    s = (x1 - x0) / (n - 1)
    for i in range(n):
        x = x0 + i * s
        m = 0.05 + 0.10 * (x / x1)          # 0.05 .. 0.15, never reaches 1
        rows.append((x, T, m * math.sqrt(GAMMA * R_GAS * T), 0.0, 0.0))
    return rows


def _fake_history(n_total=None, shockless_before=None, xs_of=None):
    """A COMPLETE history of n_total real files on disk at t = k*SAMPLE_DT, in the
    (time, path) shape centreline_history returns.  Samples before `shockless_before`
    (in index terms) carry NO shock at all."""
    if n_total is None:
        n_total = FROZEN_ARITHMETIC["n_total"]
    if shockless_before is None:
        shockless_before = 0
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_hist_")
    _SYNTH_DIR.append(tmp)
    out = []
    for k in range(1, n_total + 1):
        p = os.path.join(tmp, "t%03d.xy" % k)
        if k <= shockless_before:
            _write_raw(p, _shockless(321))
        else:
            xs = xs_of(k) if xs_of else (1.10 + 0.04 * (k % 4))
            _write_raw(p, [tuple(r) for r in _synth(321, xs)])
        out.append((k * SAMPLE_DT, p))
    return out


def _series_over(hist):
    """R3's BEHAVIOUR: compute the shock location for the WHOLE history, then window it.
    Kept here as the reference the BIT-IDENTITY arm compares against, and as the object the
    WINDOW-DEFECT arm shows refusing."""
    out = []
    for t, p in hist:
        x = shock_location(to_mach(read_centreline_raw(p)))
        if x is None:
            refuse("no downward Mach=1 crossing in sample %s (R3 behaviour)" % p)
        out.append((t, x))
    return out


def _plateau_series(b16, shared, a16):
    """A series over the REGISTERED WINDOW in the (t, x) shape plateau() consumes, laid
    out so the arm author controls window membership exactly:

        b16      the 16 samples that are in window B ONLY
        shared   the ONE sample on the B/A boundary, which windows() puts in BOTH
        a16      the 16 samples that are in window A ONLY

    t runs on the real SAMPLE_DT grid and ends exactly at ENDTIME_GRADED, so windows()
    slices it the same way it slices a real run.  The x VALUES ARE OFFSETS FROM ZERO, not
    physical shock locations: these arms exercise the D2 conjunction's arithmetic, and a
    base of 0 keeps P1/P2/P3 EXACT in floating point so the at-threshold arm can be
    compared against DELTA_X with `<=` rather than a tolerance -- which is the only way an
    arm can distinguish `<=` from `<`."""
    vals = list(b16) + [shared] + list(a16)
    k0 = FROZEN_ARITHMETIC["n_total"] - FROZEN_ARITHMETIC["window_total"]
    return [((k0 + i + 1) * SAMPLE_DT, vals[i]) for i in range(len(vals))]


def selftest():
    ok = [0]
    bad = [0]

    def arm(label, cond):
        if cond:
            ok[0] += 1
            print("  [ok ] %s" % label)
        else:
            bad[0] += 1
            print("  [FAIL] %s" % label)

    def must_refuse(label, fn):
        try:
            fn()
        except SystemExit as e:
            arm(label + "  -> REFUSES(%s)" % e.code, e.code == 2)
            return
        arm(label + "  -> DID NOT REFUSE", False)

    print("== W3: the frozen clock arithmetic (checked at import, re-shown here) ==")
    arm("endTime/SAMPLE_DT = %d samples (whole)" % FROZEN_ARITHMETIC["n_total"],
        FROZEN_ARITHMETIC["n_total"] == 160)
    arm("samples per plateau window = %d intervals + 1 = %d >= MIN_WINDOW_SAMPLES %d, at "
        "EVERY level; %d distinct over the two windows (they share one boundary sample)"
        % (FROZEN_ARITHMETIC["intervals"], FROZEN_ARITHMETIC["per_window"],
           MIN_WINDOW_SAMPLES, FROZEN_ARITHMETIC["window_total"]),
        FROZEN_ARITHMETIC["intervals"] == 16 and
        FROZEN_ARITHMETIC["per_window"] == 17 and
        FROZEN_ARITHMETIC["window_total"] == 33 and
        FROZEN_ARITHMETIC["per_window"] >= MIN_WINDOW_SAMPLES)
    arm("SAMPLE_DT/maxDeltaT = %.1f >= 1 (adjustableRunTime can land on a write time)"
        % FROZEN_ARITHMETIC["steps_per_sample"],
        FROZEN_ARITHMETIC["steps_per_sample"] >= 1.0)
    must_refuse("W3 refuses a writeInterval too coarse for MIN_WINDOW_SAMPLES",
                lambda: _w3_with(sample_dt=2.0e-03))
    must_refuse("W3 refuses a writeInterval that does not divide endTime",
                lambda: _w3_with(sample_dt=3.0e-03))
    must_refuse("W3 refuses SAMPLE_DT < maxDeltaT",
                lambda: _w3_with(sample_dt=5.0e-05, endtime=0.080, wfrac=1))

    print("== W2: the probe-length floor ==")
    arm("PROBE_FLOOR = %.2f, and every filed cost basis clears it (L1 %.4f, L2 %.4f, "
        "L3 %.4f)" % (PROBE_FLOOR, COST_BASIS_FRACTION["L1"],
                      COST_BASIS_FRACTION["L2"], COST_BASIS_FRACTION["L3"]),
        all(COST_BASIS_FRACTION[L] >= PROBE_FLOOR for L in COST_BASIS_FRACTION))
    must_refuse("W2 refuses R3's own 10 %% L2/L3 basis (the one that killed both runs)",
                lambda: _w2_with({"L1": 1.0, "L2": 0.10, "L3": 0.10}))
    must_refuse("W2 refuses a basis just below the floor (0.2499)",
                lambda: _w2_with({"L1": 0.2499}))
    arm("W2 admits a basis exactly at the floor (0.25)", _w2_with({"L1": 0.25}) is None)

    print("== W1: the reader consumes ONLY its registered window ==")
    # The real defect, reproduced: the first 32 samples carry no shock at all.
    hist = _fake_history(shockless_before=32)
    must_refuse("R3 BEHAVIOUR on this history (reads all %d) -> refuses on an early sample"
                % FROZEN_ARITHMETIC["n_total"], lambda: _series_over(hist))
    _audit_reset()
    win, bounds = registered_window(hist, ENDTIME_GRADED)
    ser = shock_series(win)
    aud = audit_window_only("SELFTEST", bounds, hist, _hist_root(hist))
    arm("R4 BEHAVIOUR on the SAME history -> grades it, %d samples read, window (%.6g, %.6g]"
        % (aud["n_read"], bounds[0], bounds[1]),
        len(ser) == FROZEN_ARITHMETIC["window_total"] and aud["n_read"] == len(ser))
    arm("the window holds exactly %d = %d x %d intervals + 1 samples, and the reader "
        "opened %d of the %d written (%.0f %% of the history never touched)"
        % (len(win), N_WINDOWS, FROZEN_ARITHMETIC["intervals"], aud["n_read"], len(hist),
           100.0 * (1 - aud["n_read"] / float(len(hist)))),
        len(win) == FROZEN_ARITHMETIC["window_total"])

    # BIT-IDENTITY: on a history where R3's reader does NOT refuse, every graded number is
    # identical.  Compared with == and not a tolerance -- the claim is identity, not
    # agreement.
    hist2 = _fake_history(shockless_before=0)
    full = plateau([pt for pt in _series_over(hist2)
                    if pt[0] > ENDTIME_GRADED - N_WINDOWS * (ENDTIME_GRADED / W_FRACTION)
                    - TIME_RTOL * ENDTIME_GRADED], ENDTIME_GRADED)
    _audit_reset()
    w2_, b2_ = registered_window(hist2, ENDTIME_GRADED)
    wind = plateau(shock_series(w2_), ENDTIME_GRADED)
    arm("BIT-IDENTITY: P1/P2/P3/x_level/x_final identical windowed vs full-history "
        "(P1 %.17g)" % wind["p1"],
        full["p1"] == wind["p1"] and full["p2"] == wind["p2"] and
        full["p3"] == wind["p3"] and full["x_level"] == wind["x_level"] and
        full["x_final"] == wind["x_final"] and full["p0"] == wind["p0"])

    # The refusal INSIDE the window is retained and is a real limb.
    hist3 = _fake_history(shockless_before=0)
    tmpd = tempfile.mkdtemp(prefix="vmfl046r4_inwin_")
    _SYNTH_DIR.append(tmpd)
    bad_p = os.path.join(tmpd, "nowhere.xy")
    _write_raw(bad_p, _shockless(321))
    hist3[-1] = (hist3[-1][0], bad_p)     # the LAST sample, deep inside window A
    must_refuse("a missing crossing INSIDE the window still REFUSES (the real limb)",
                lambda: shock_series(registered_window(hist3, ENDTIME_GRADED)[0]))
    must_refuse("the W1 audit REFUSES a read outside the window (planted)",
                lambda: _audit_with_outside_read(hist2))
    must_refuse("the W1 audit REFUSES an EMPTY audit (a control that cannot fail)",
                lambda: (_audit_reset(),
                         audit_window_only("SELFTEST", (0.064, 0.080), hist2,
                                           _hist_root(hist2)))[1])

    print("== D2 PLATEAU CONJUNCTION -- R3 HAD NO ARM HERE AND A CONSTANT `True` PASSED ==")
    d = DELTA_X
    z16 = [0.0] * 16
    for label, b16, shared, a16, want in (
            ("steady (P1=P2=P3=0)", z16, 0.0, z16, True),
            ("EXACTLY at the threshold (P1 == DELTA_X) -- distinguishes <= from <",
             z16, 0.0, [0.0] * 8 + [d] * 8, True),
            ("just over the threshold (P1 = DELTA_X*(1+1e-9))",
             z16, 0.0, [0.0] * 8 + [d * (1 + 1e-9)] * 8, False),
            ("P1 alone over (window A spreads 2*DELTA_X, both means 0)",
             z16, 0.0, [-d] * 8 + [d] * 8, False),
            ("P2 alone over (window B spreads 2*DELTA_X, both means 0)",
             [-d] * 8 + [d] * 8, 0.0, z16, False),
            ("P3 alone decides: P1 AND P2 BOTH sit exactly AT the threshold and pass, "
             "and the mean drift 32/17*DELTA_X is what fails -- so P3 is not redundant",
             [-d] * 16, 0.0, [d] * 16, False)):
        got = plateau(_plateau_series(b16, shared, a16), ENDTIME_GRADED)
        arm("plateau %s -> %s (P1=%.6e P2=%.6e P3=%.6e vs DELTA_X %.6e)"
            % (label, "PLATEAU" if got["ok"] else "NOT PLATEAUED",
               got["p1"], got["p2"], got["p3"], d), got["ok"] == want)
    # The at-threshold arm is only a <=-vs-< discriminator if its P1 is EXACTLY DELTA_X.
    _at = plateau(_plateau_series(z16, 0.0, [0.0] * 8 + [d] * 8), ENDTIME_GRADED)
    arm("the at-threshold arm's P1 is EXACTLY DELTA_X (%.17g), so `<` would fail it"
        % _at["p1"], _at["p1"] == DELTA_X)
    must_refuse("windows() refuses a series shorter than MIN_WINDOW_SAMPLES per window",
                lambda: plateau([(k * SAMPLE_DT, 1.25)
                                 for k in range(150, 160)], ENDTIME_GRADED))

    print("== readers ==")
    for target in (1.1000, 1.2500, 1.3117):
        got = shock_location(to_mach(_synth(801, target)))
        arm("interpolating reader finds shock at %.4f (got %.6f)" % (target, got),
            abs(got - target) < 0.02)
    a = shock_location(to_mach(_synth(1281, 1.2500)))
    b = shock_location(to_mach(_synth(1281, 1.2500 + 0.5 * DELTA_X)))
    arm("reader resolves 0.5*DELTA_X (%.3e) apart: d=%.3e" % (0.5 * DELTA_X, b - a),
        abs((b - a) - 0.5 * DELTA_X) < 0.05 * DELTA_X)
    sa = shock_location_snapping(to_mach(_synth(1281, 1.2500)))
    sb = shock_location_snapping(to_mach(_synth(1281, 1.2500 + 0.5 * DELTA_X)))
    arm("node-snapping reader CANNOT resolve it (d=%.3e, i.e. 0 or a whole quantum)"
        % (sb - sa), abs(sb - sa) < 1e-12 or abs(sb - sa) > 1.4e-3)
    arm("the reader returns None on a shockless profile (it does NOT guess)",
        shock_location(to_mach(_shockless(321))) is None)

    print("== PLANT C1 -- the replacement for R2's answer-dependent PLANT C ==")
    for label, pts in (("steady series (ptp 0)", [(i * SAMPLE_DT, 1.25) for i in range(16)]),
                       ("hunting series (ptp 1.2e-01)",
                        [(i * SAMPLE_DT, 1.09 + 0.12 * (i % 2)) for i in range(16)]),
                       ("drifting series", [(i * SAMPLE_DT, 1.10 + 0.001 * i)
                                            for i in range(16)])):
        r = plant_series_translation(pts)
        arm("C1 inert exactly, live exactly +plant, on a %s" % label,
            abs(r["inert"] - r["base"]) == 0.0
            and abs((r["live"] - r["base"]) - PLANT_DX) < 1e-12)
    must_refuse("C1 refuses a NON-TRANSLATION-INVARIANT reducer (relative spread)",
                lambda: _c1_with_bad_reducer())
    must_refuse("C1 refuses a DEAD reducer (constant)",
                lambda: _c1_with_dead_reducer())

    print("== PLANT C2 -- per-sample field read-back ==")
    must_refuse("C2 refuses a dead reader (constant)",
                lambda: plant_field_readback_per_sample(
                    _fake_window(8), reader=lambda cl: 1.2345))
    must_refuse("C2 refuses a half-scale (biased) reader",
                lambda: plant_field_readback_per_sample(
                    _fake_window(8), reader=lambda cl: 0.5 * shock_location(cl)))
    must_refuse("C2 refuses R1's node-snapping reader at plant = DELTA_X",
                lambda: plant_field_readback_per_sample(
                    _fake_window(8), dx=PLANT_DX_SMALL, reader=shock_location_snapping))
    r = plant_field_readback_per_sample(_fake_window(8))
    arm("C2 passes the real interpolating reader (worst %.3e < tol %.3e)"
        % (r["worst"], r["tol"]), r["worst"] < r["tol"])

    print("== PLANT A / B ==")
    w = _fake_window(10)
    must_refuse("A refuses a dead reader", lambda: plant_gate_reader(
        w[-1][1], reader=lambda cl: 1.2345))
    must_refuse("A refuses the node-snapping reader at plant = DELTA_X",
                lambda: plant_gate_reader(w[-1][1], dx=PLANT_DX_SMALL,
                                          reader=shock_location_snapping))
    must_refuse("B refuses a dead reader", lambda: plant_plateau_reducer(
        w, reader=lambda cl: 1.2345))
    rb = plant_plateau_reducer(w)
    arm("B moves the ptp by >= 0.75*plant on the argmax (%.4e -> %.4e)"
        % (rb["base"], rb["got"]), rb["got"] >= rb["base"] + 0.75 * PLANT_DX)

    # ---- §2av REQUIREMENT 4: THE DRIVEN CONTROL OVER THE PREVIOUSLY-UNEXERCISED
    # CALL SITE.  59 arms passed while the defect shipped THROUGH them, because every
    # arm called these functions with a CORRECT argument and none exercised what
    # grade() actually passes -- §2p.3(d)'s exact class: "a pass is attributable only
    # if the code that produced it is the code that runs".  These arms drive the
    # ARGUMENT SHAPE at the call site, and they FAIL on the shipped form.
    print("== §2av CALL-SITE SHAPE (the defect this grant repaired) ==")

    def must_reject(label, fn):
        """Arms TRUE only if fn() does NOT return normally.  Distinct from
        must_refuse(): the shipped defect CRASHED (TypeError) rather than refusing,
        and an arm that demanded exit 2 would itself have failed on the real bug."""
        try:
            fn()
        except SystemExit as e:
            arm(label + "  -> REFUSES(%s)" % e.code, True)
            return
        except Exception as e:
            arm(label + "  -> RAISES %s" % type(e).__name__, True)
            return
        arm(label + "  -> RETURNED NORMALLY (the defect would ship again)", False)

    _ser = shock_series(w)
    must_reject("B rejects series points [(t, x)] -- the SHIPPED call-site argument",
                lambda: plant_plateau_reducer(_ser))
    must_reject("C2 rejects series points [(t, x)] -- the SHIPPED call-site argument",
                lambda: plant_field_readback_per_sample(_ser))
    # and the suffix correspondence the repair relies on, driven rather than assumed:
    _k = 4
    _tailA = _ser[len(_ser) - _k:]
    _winA = w[len(_ser) - _k:]
    arm("§2av suffix correspondence: win[-k:] time-stamps == series[-k:] time-stamps",
        [t for t, _ in _winA] == [t for t, _ in _tailA])
    _rb2 = plant_plateau_reducer(_winA)
    arm("§2av B fires on the REPAIRED call-site argument win[-k:] (%.4e -> %.4e)"
        % (_rb2["base"], _rb2["got"]),
        _rb2["got"] >= _rb2["base"] + 0.75 * PLANT_DX)

    # ---- §2aw REQUIRED CONTROL: THE PLANTS-THEN-AUDIT **ORDERING**, DRIVEN -------
    # This is the coverage gap that produced BOTH defects (L-495).  Every arm above
    # exercises a PART; this one runs grade()'s actual sequence against a synthetic run
    # root -- arm the audit, select the window, read the series, RUN THE FIVE PLANTS,
    # then check the audit -- which is the only ordering in which either defect appears.
    print("== §2aw PLANTS-THEN-AUDIT ORDERING (the sequence grade() actually runs) ==")
    _h = _fake_history(shockless_before=0)
    _root = _hist_root(_h)
    _audit_reset()
    _wn, _bd = registered_window(_h, ENDTIME_GRADED)
    _sr = shock_series(_wn)
    _pl = plateau(_sr, ENDTIME_GRADED)
    _wA = _wn[len(_sr) - len(_pl["A"]):]
    plant_gate_reader(_wn[-1][1])
    plant_plateau_reducer(_wA)
    plant_series_translation(_pl["A"])
    plant_field_readback_per_sample(_wA)
    _pre = set(_audit_paths())
    _a = audit_window_only("SELFTEST-ORDER", _bd, _h, _root)
    arm("the plants DO pollute the audit -- %d of %d recorded reads are the comparator's "
        "OWN scratch, outside the run root (this is the defect, still present and still "
        "measured; (c) EXCLUDES it, it does not stop it happening)"
        % (_a["n_excluded"], len(_pre)), _a["n_excluded"] > 0)
    arm("W1 PASSES in the production ordering: %d run-root reads audited, %d excluded as "
        "not run data" % (_a["n_read"], _a["n_excluded"]),
        _a["n_read"] == FROZEN_ARITHMETIC["window_total"])
    arm("every excluded path is OUTSIDE the run root, and none is a run sample",
        all(not p.startswith(_root + os.sep) for p in _a["excluded"]))

    # ⚡ AND THE HAZARD (d) WOULD HAVE MASKED, DRIVEN IN THE SAME ORDERING: a plant that
    # reads a REAL out-of-window sample is INSIDE the run root and MUST still refuse.
    # (c) narrows W1's subject; it does not narrow W1's reach.
    def _plant_reads_real_out_of_window():
        _audit_reset()
        wn, bd = registered_window(_h, ENDTIME_GRADED)
        sr = shock_series(wn)
        pl_ = plateau(sr, ENDTIME_GRADED)
        plant_plateau_reducer(wn[len(sr) - len(pl_["A"]):])
        read_centreline_raw(_h[0][1])      # a REAL sample at t = SAMPLE_DT, out of window
        return audit_window_only("SELFTEST-ORDER", bd, _h, _root)
    must_refuse("⚡ (c) STILL CATCHES a plant reading a REAL out-of-window sample -- the "
                "hazard (d) was rejected for masking", _plant_reads_real_out_of_window)

    print("== PLANT D -- the T-field reader ==")
    must_refuse("D refuses a T internalField that is not a nonuniform scalar list",
                lambda: read_T_internal(_write_T_file("internalField uniform 300;\n")))
    rd = plant_T_field(_write_T_file(
        "FoamFile { object T; }\ninternalField   nonuniform List<scalar>\n3\n(\n"
        "328\n400\n500\n)\n;\n"))
    arm("D recovers a uniform plant per value (worst err %.3e)" % rd["err"],
        rd["err"] < 1e-6 and rd["n"] == 3)

    print("== rule-4 N2 transliteration ==")
    for label, times, nexec, endt, maxdt, want_refuse in (
            ("complete run", [i * 1e-5 for i in range(1, 8001)], 8000, 0.08, 1e-4, False),
            ("truncated log (exec count short)", [i * 1e-5 for i in range(1, 8001)], 7999,
             0.08, 1e-4, True),
            ("stopped early", [i * 1e-5 for i in range(1, 4001)], 4000, 0.08, 1e-4, True),
            ("R3's L3 CAP KILL (0.0793715355 of 0.080)",
             [i * 0.0793715355 / 8000.0 for i in range(1, 8001)], 8000, 0.08, 1e-4, True),
            ("too few steps for maxDeltaT", [i * 1e-4 for i in range(1, 401)] + [0.08],
             401, 0.08, 1e-4, True),
            ("restart splice (non-monotone)",
             [i * 1e-5 for i in range(1, 5001)] + [i * 1e-5 for i in range(4000, 7001)],
             8002, 0.08, 1e-4, True)):
        got = _n2_check(times, nexec, endt, maxdt)
        arm("N2 %s -> %s" % (label, "REFUSE" if got else "pass"), got == want_refuse)

    print("== Roache states ==")
    for label, tri3, want in (("converging", (1.30, 1.26, 1.24), "CONVERGING"),
                              ("divergent", (1.30, 1.26, 1.18), "DIVERGENT"),
                              ("oscillatory", (1.30, 1.20, 1.25), "OSCILLATORY"),
                              ("exact", (1.25, 1.25, 1.25), "EXACT")):
        arm("roache %s -> %s" % (label, want), roache(*tri3)["state"] == want)

    print("== N4 REPLACEMENT: reconstructed T must lie in the physical envelope [50,1000] K ==")
    must_refuse("N4(R6) refuses a T field BELOW the physical floor (min 30 K < %g)"
                % T_MIN_PHYS, lambda: _n4_on([30.0, 300.0, 450.0]))
    must_refuse("N4(R6) refuses a T field ABOVE the physical ceiling (max 1200 K > %g)"
                % T_MAX_PHYS, lambda: _n4_on([300.0, 400.0, 1200.0]))
    must_refuse("N4(R6) refuses a KNP blow-up (T -> 1e5 K -- the planted-zero analogue: a "
                "reader shown able to SEE a non-physical field)",
                lambda: _n4_on([300.0, 400.0, 1.0e5]))
    must_refuse("N4(R6) refuses a T-collapse (T -> 1 K)",
                lambda: _n4_on([1.0, 300.0, 450.0]))
    r = _n4_on([254.0, 400.0, 500.0])
    arm("N4(R6) passes the TRUE physical range [254, 500] K (non-binding on the real field)",
        r["lo"] == 254.0 and r["hi"] == 500.0)
    r2 = _n4_on([T_MIN_PHYS, 400.0, T_MAX_PHYS])
    arm("N4(R6) admits a field EXACTLY at the envelope edges [%g, %g] K (inclusive bounds)"
        % (T_MIN_PHYS, T_MAX_PHYS), r2["lo"] == T_MIN_PHYS and r2["hi"] == T_MAX_PHYS)

    print("\nSELFTEST: %d ok, %d FAILED" % (ok[0], bad[0]))
    print("Per charter §39.5 this proves LOGIC and NOT INTERFACE.  The interface evidence is")
    print("PREREGISTRATION §12, which names the real solver-written paths on disk.")
    return 0 if bad[0] == 0 else 1


_SYNTH_DIR = []


def _write_T_file(text):
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_T_")
    _SYNTH_DIR.append(tmp)
    p = os.path.join(tmp, "T")
    open(p, "w").write(text)
    return p


def _fake_window(n):
    """A window of n REAL FILES on disk, each a synthetic centreline with the shock at a
    different place -- i.e. a HUNTING window, which is the case R2's PLANT C could not
    handle.  Returned in the (time, path) shape the plants consume."""
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_win_")
    _SYNTH_DIR.append(tmp)
    out = []
    for i in range(n):
        xs = 1.10 + 0.04 * (i % 4)
        rows = _synth(641, xs)
        p = os.path.join(tmp, "s%d.xy" % i)
        _write_raw(p, rows)
        out.append(((i + 1) * SAMPLE_DT, p))
    return out


def _w3_with(sample_dt=None, endtime=None, wfrac=None):
    """W3's arithmetic re-run against mutated clock constants, so the import-time limbs
    are shown able to REFUSE and are not merely shown passing on the frozen values."""
    global SAMPLE_DT, ENDTIME_GRADED, W_FRACTION
    old = (SAMPLE_DT, ENDTIME_GRADED, W_FRACTION)
    try:
        if sample_dt is not None:
            SAMPLE_DT = sample_dt
        if endtime is not None:
            ENDTIME_GRADED = endtime
        if wfrac is not None:
            W_FRACTION = wfrac
        return _check_frozen_arithmetic()
    finally:
        SAMPLE_DT, ENDTIME_GRADED, W_FRACTION = old


def _w2_with(basis):
    """W2's floor re-run against a mutated cost basis, same purpose as _w3_with."""
    global COST_BASIS_FRACTION
    old = COST_BASIS_FRACTION
    try:
        COST_BASIS_FRACTION = basis
        _check_frozen_arithmetic()
        return None
    finally:
        COST_BASIS_FRACTION = old


def _hist_root(hist):
    """The synthetic run root for a _fake_history/_fake_window: every sample it wrote
    lives in one temp dir, so that dir plays the part `ld` plays in grade().  Derived
    from the history itself so an arm cannot pass by naming a root that excludes the
    very reads it should audit."""
    return os.path.dirname(os.path.realpath(hist[0][1]))


def _audit_with_outside_read(hist):
    """Plant an OUT-OF-WINDOW read into the audit and require the audit to catch it.  The
    planted path is a real early sample from the same history -- exactly the file R3's
    reader opened and refused on."""
    _audit_reset()
    win, bounds = registered_window(hist, ENDTIME_GRADED)
    shock_series(win)
    read_centreline_raw(hist[0][1])           # t = SAMPLE_DT: outside the window
    return audit_window_only("SELFTEST", bounds, hist, _hist_root(hist))


def _c1_with_bad_reducer():
    """A reducer that is NOT translation-invariant, applied through C1's own arithmetic."""
    pts = [(i * SAMPLE_DT, 1.09 + 0.12 * (i % 2)) for i in range(16)]
    xs = [x for _, x in pts]
    base = (max(xs) - min(xs)) / max(abs(v) for v in xs)          # RELATIVE spread
    sh = [x + PLANT_DX for x in xs]
    got = (max(sh) - min(sh)) / max(abs(v) for v in sh)
    if abs(got - base) > 1e-12 * max(PLANT_DX, 1.0):
        refuse("PLANT C1 INERT ARM FAILED: the reducer is not translation-invariant "
               "(%.6e -> %.6e)" % (base, got))
    return None


def _c1_with_dead_reducer():
    """A reducer that always returns 0 -- inert arm passes, LIVE arm must catch it."""
    base = 0.0
    got_live = 0.0
    if abs((got_live - base) - PLANT_DX) > 1e-12 * max(PLANT_DX, 1.0):
        refuse("PLANT C1 LIVE ARM FAILED: a dead reducer's zero is not evidence of a "
               "covering (moved %.6e, needed %.6e)" % (got_live - base, PLANT_DX))
    return None


def _n2_check(times, n_exec, endt, maxdt):
    """The N2 limbs in isolation, so the selftest can exercise them without a log file.
    Returns True if the limbs would REFUSE."""
    if not times:
        return True
    if n_exec != len(times):
        return True
    if abs(times[-1] - endt) > maxdt:
        return True
    if len(times) < int(math.floor(endt / maxdt)):
        return True
    for i in range(1, len(times)):
        if not (times[i] > times[i - 1]):
            return True
    return False


def _n4_on(vals):
    tmp = tempfile.mkdtemp(prefix="vmfl046r4_n4_")
    try:
        p = os.path.join(tmp, "T")
        open(p, "w").write(
            "FoamFile { version 2.0; format ascii; class volScalarField; object T; }\n"
            "internalField   nonuniform List<scalar>\n%d\n(\n%s\n)\n;\n"
            % (len(vals), "\n".join("%.10g" % v for v in vals)))
        return check_T_physical_range(p, "SELFTEST")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- main -------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    try:
        if args and args[0] == "--selftest":
            return selftest()
        if args and args[0] == "--paths":
            if len(args) != 2:
                sys.stderr.write("usage: %s --paths <run_root>\n" % sys.argv[0])
                return 2
            print("§39.5 path enumeration for VMFL046-R6 against %s" % args[1])
            for p in READ_PATHS:
                print("   reads: %s" % p)
            print()
            bad = check_paths(args[1])
            print("\nMISSING: %d" % bad)
            return 0 if bad == 0 else 1
        if len(args) != 1:
            sys.stderr.write(__doc__.split("USAGE")[-1])
            return 2
        return grade(args[0])
    finally:
        for d in _SYNTH_DIR:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
