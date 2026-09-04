#!/usr/bin/env python3
"""VMFL046-R3 -- Supersonic flow with a normal shock in a converging-diverging nozzle.
THE FROZEN GRADING PATH.  Ansys Fluid Dynamics Verification Manual VM2026R1 p.155.

R3 is the successor VMFL046-R2's registration PRE-COMMITTED in its branch (b), before any
R2 compute existed:

    "BRANCH (b) -- ANY LEVEL FAILS THE PLATEAU AT endTime = 60000.  Verdict NOT A RESULT.
     The successor, VMFL046-R3, CHANGES THE NUMERICS AND NEVER THE GATE, THE BAND OR THE
     PLATEAU THRESHOLD."

R2 graded NOT A RESULT (register row #57).  This file therefore carries, UNCHANGED and
not re-derived, not re-rounded, not moved:

    ANALYTICAL_SHOCK = 1.250 m      SHOCK_TOL = 5 %      DELTA_X = 6.250e-04 m

and changes ONLY the numerics: rhoSimpleFoam (steady, no time derivative anywhere, first
order upwind) -> rhoPimpleFoam (transient, Euler, second-order TVD).  See PREREGISTRATION
§5 and §6.

WHAT IS CARRIED FORWARD FROM R2's FROZEN COMPARATOR, UNCHANGED IN BEHAVIOUR
  D1  the refining sampler assert (nPoints = 2*Nx+1, read from the level's OWN mesh)
  D2  the plateau on x_shock, peak-to-peak over two adjacent windows plus the mean drift
  D3  the INTERPOLATING shock reader (last downward M=1 crossing), and it is a gate limb
  D4  the Roache triple, the demote-only secondaries, PLANT A, PLANT B and PLANT D

WHAT IS NEW IN R3, AND EVERY ITEM IS DECLARED ON THE FACE OF THE REGISTRATION
  N1  SAMPLE_DT / ENDTIME / MAXCO / MAXDELTAT are PHYSICAL SECONDS, not iteration counts
  N2  DEPARTURE from R2's rule-4 `ExecutionTime count == endTime` limb, which an adaptive
      time-step solver can never satisfy.  Ruled by the supervisor 2026-09-04; the
      replacement is STRICTLY STRONGER and every term is computable from frozen constants.
  N3  PLANT C is REPLACED.  R2's Plant C asserted that a rigid shift of the Mach FIELD
      leaves the ptp of the x_shock SERIES unchanged -- true only when the profile shape is
      identical across samples, i.e. ONLY WHEN THE SHOCK IS ALREADY STEADY.  It refused on
      R2's own real data.  A CONTROL WHOSE VALIDITY DEPENDS ON THE ANSWER IT IS CHECKING is
      not a control.  It is replaced by two arms whose premises are answer-independent:
        PLANT C1  the cancellation demonstration, moved to the REDUCTION where the claim
                  lives: add the plant to every member of the x_shock SERIES and assert the
                  ptp is unchanged.  Premise: max(x+d) - min(x+d) = max(x) - min(x), an
                  identity of the reals.  Paired with a LIVE arm on the argmax so the
                  inertness is shown to come from the covering and not from a dead helper.
        PLANT C2  the field-level contact Plant C had, with the steadiness premise removed:
                  recover the planted displacement PER SAMPLE, INDEPENDENTLY, and require
                  each within 25 % of the plant.  It asserts nothing about the relationship
                  BETWEEN samples, which is exactly where the old premise entered.
      DELETING A FALSE ASSERTION IS THE REPAIR, NOT A LOSS OF COVERAGE.
  N4  the limitTemperature bounds frozen in constant/fvOptions must be NON-BINDING at
      endTime.  They bound at BOTH ends during every failed transient probe (§5.3), so a
      run in which they bind is not reporting the registered physics.  A REFUSAL, never a
      printed diagnostic.

USAGE
    grade_vmfl046_r3.py <run_root>          grade
    grade_vmfl046_r3.py --paths <run_root>  §39.5 path enumeration against a real run root
    grade_vmfl046_r3.py --selftest          planted-failure self-tests
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

# PRIMARY GATE -- UNCHANGED FROM R1 AND R2.  Not re-derived, not re-rounded, not moved.
ANALYTICAL_SHOCK = 1.250          # m
SHOCK_TOL        = 0.05           # 5 % -> band half-width 0.0625 m
BAND             = SHOCK_TOL * ANALYTICAL_SHOCK

# PLATEAU -- UNCHANGED FROM R2, which adopted it unchanged from charter §31.
DELTA_X          = 6.25e-04       # m
W_FRACTION       = 10             # plateau window W = endTime / W_FRACTION
MIN_WINDOW_SAMPLES = 8            # a ptp over fewer samples is not a ptp; refuse

# R3's TRANSIENT CONSTANTS -- PHYSICAL SECONDS.  Fixed by the §5.3 stability probe and by
# the §5.4 settling-time derivation, both BEFORE this file was frozen.  None is a
# threshold, a band or a cap.
ENDTIME_GRADED   = 0.080          # s.  ~20 upstream acoustic traverses of the 0.85 m
                                  # subsonic section at c-u ~ 220 m/s (3.9 ms each).
SAMPLE_DT        = 5.0e-04        # s between centreline samples -> 160 samples,
                                  # 16 per plateau window (R2 had 13).
MAXCO_GRADED     = 0.5            # the value the FINE-LEVEL probe validated
MAXDELTAT_GRADED = 1.0e-04        # s
TIME_RTOL        = 1.0e-06        # relative tolerance on a written time-directory name

# SECONDARIES -- DEMOTE-ONLY (charter §21.3), retained UNCHANGED from R1/R2.
P_OBS_LO, P_OBS_HI = 0.5, 2.5
GCI_FINE_MAX       = 0.15
R_REFINE, FS       = 2.0, 1.25

# N4 -- the frozen constant/fvOptions bounds.  Physical range is T in [328, 500] K, so a
# 1 % margin is enormous; this limb can only fire if the solve left the registered physics.
LIMIT_T_MIN, LIMIT_T_MAX = 150.0, 2000.0
LIMIT_T_MARGIN           = 0.01

# PLANTS (CLAUDE.md rule 3)
PLANT_DX         = 1.000e-02      # m, the shock displacement planted into a SCRATCH copy
PLANT_DX_SMALL   = 6.250e-04      # m, exactly DELTA_X -- the quantum-discrimination plant
PLANT_K_T        = 1.0e-3         # relative plant into the T field
PLANT_C2_TOL     = 0.25           # fraction of the plant; the SAME tolerance as PLANT A


class Refuse(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSE: %s\n" % msg)
        SystemExit.__init__(self, 2)


def refuse(msg):
    raise Refuse(msg)


# ---- readers ----------------------------------------------------------------
def read_centreline_raw(path):
    """-> [(x, T, ux, uy, uz)] from a raw `sets` .xy sample.  Refuses on anything it
    cannot parse; a reader that guesses can misread."""
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
    """D3 -- THE INTERPOLATING READER, AND IT IS A GATE LIMB.  CARRIED FORWARD FROM R2
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
    maxco = one("maxCo", "the stability constant fixed by the §5.3 probe")
    maxdt = one("maxDeltaT", "the stability constant fixed by the §5.3 probe")
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
               "coarsest- and fine-level probe before the freeze and a run at any other "
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
    # The controlDict that RAN must carry exactly two writeIntervals: the fields at endTime
    # and the centreline every SAMPLE_DT.  This refuses a CLAUSE-B smoke configuration from
    # ever reaching the grading path.  R3 reads them as FLOATS (R2's were integers).
    wi = sorted(set(float(v) for v in re.findall(
        r"^\s*writeInterval\s+([0-9.eE+\-]+)\s*;", open(
            os.path.join(level_dir, "system", "controlDict")).read(), re.M)))
    want = sorted({ENDTIME_GRADED, SAMPLE_DT})
    if len(wi) != len(want) or any(abs(a - b) > TIME_RTOL * max(b, 1e-30)
                                   for a, b in zip(wi, want)):
        refuse("%s: controlDict writeIntervals are %s, expected %s (fields at endTime, "
               "centreline every SAMPLE_DT) -- this is not the graded configuration"
               % (level, wi, want))
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
    up to endTime.  A missing sample must refuse, never silently shrink a plateau window."""
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


# ---- the plateau (D2 + D4) --------------------------------------------------
def shock_series(hist):
    out = []
    for t, p in hist:
        x = shock_location(to_mach(read_centreline_raw(p)))
        if x is None:
            refuse("no downward Mach=1 crossing in sample %s -- the shock is not resolvable "
                   "in this profile; refusing rather than reporting a location" % p)
        out.append((t, x))
    return out


def windows(series, endtime):
    """Two ADJACENT windows of W = endTime/W_FRACTION seconds each, sharing one boundary
    sample.  A: (endTime-W, endTime].  B: (endTime-2W, endTime-W]."""
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
# THREE plant-design defects have now been paid for in this family, each by a measurement:
#   CANCELLATION -- a plant covering the WHOLE reduction set is a rigid translation and the
#                   ptp is identically unchanged (PLANT C1 demonstrates it deliberately);
#   ABSORPTION   -- a plant into an INTERIOR member is swallowed whole when the window
#                   already spreads wider than the plant.  Measured on real data: a 1.0e-02
#                   m interior plant into a window of spread 1.1066e-01 m left the ptp
#                   UNCHANGED.  PLANT B therefore plants the window's MAXIMUM.
#   ANSWER-DEPENDENCE -- R2's PLANT C asserted an invariance that holds only if the shock is
#                   already steady.  Measured on R2's own data: inert at L1 (ptp 1.15e-13,
#                   steady) and moving the ptp by 3.953e-05 at L2 and 2.962e-05 at L3, i.e.
#                   REFUSING at both levels where the shock actually moved.  A CONTROL WHOSE
#                   VALIDITY DEPENDS ON THE ANSWER IT IS CHECKING IS NOT A CONTROL.
#                   PLANT C1 + PLANT C2 replace it; see the module docstring, N3.
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
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_plantA_")
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
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_plantB_")
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
    ACTUALLY LIVES.  This is the repair of R2's PLANT C.

    THE PREMISE, AND IT IS AN IDENTITY OF THE REALS:
        max(x_i + d) - min(x_i + d)  ==  max(x_i) - min(x_i)
    It is true whether the shock is steady, hunting over 38 cells, or absent.  It is
    INDEPENDENT OF THE ANSWER, which is exactly the property R2's PLANT C lacked.

    IT IS NOT A TAUTOLOGY AND IT CAN FAIL: it fails the moment `ptp` is mutated into a
    reducer that is not translation-invariant -- a relative spread, a normalised range, a
    max|x| -- and such a mutation would silently change the plateau verdict.  The LIVE arm
    below proves the inertness comes from THE COVERING and not from a dead helper: the same
    helper applied to a PROPER SUBSET (the argmax) must move the ptp by exactly +dx.
    """
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
    REMOVED.

    R2's PLANT C shifted the Mach FIELD on every window member and asserted the ptp of the
    x_shock SERIES was unchanged.  That is a claim about the relationship BETWEEN samples,
    and it holds only if the profile SHAPE is identical across them -- i.e. only if the
    shock is already steady.  It refused on R2's own real data at both levels where the
    shock moved.

    C2 makes the SAME measurement without the same premise: it recovers the planted
    displacement PER SAMPLE, INDEPENDENTLY, and requires each to be within 25 % of the
    plant -- PLANT A's tolerance, applied N times instead of once.  It asserts NOTHING
    about the relationship between samples.  Validated on R2's real windows: the worst
    per-sample recovery error was 0.46 % of the plant at L1, 0.45 % at L2 and 0.41 % at L3,
    i.e. 54x inside tolerance AT EVERY LEVEL INCLUDING THE ONE HUNTING OVER 38 CELLS.
    """
    reader = reader or shock_location
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_plantC2_")
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
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_plantT_")
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


# ---- N4: the frozen fvOptions limiters must be NON-BINDING ------------------
def check_limiters_nonbinding(t_path, level):
    """N4 -- A REFUSAL LIMB, NOT A PRINTED DIAGNOSTIC.

    `constant/fvOptions` carries `limitTemperature min 150 max 2000`, byte-identical to R2.
    During EVERY failed transient probe of §5.3 that limiter bound at BOTH ends within a
    few time steps of the blow-up, together with pMinFactor/pMaxFactor.  A run whose T
    field touches those bounds at endTime is not reporting the registered physics, and
    printing that as a diagnostic beside a verdict would be worse than never computing it.
    The physical range is T in [328, 500] K, so this limb is non-binding by construction
    unless something has gone wrong."""
    vals, _ = read_T_internal(t_path)
    lo, hi = min(vals), max(vals)
    m_lo = LIMIT_T_MIN * (1.0 + LIMIT_T_MARGIN)
    m_hi = LIMIT_T_MAX * (1.0 - LIMIT_T_MARGIN)
    if lo < m_lo or hi > m_hi:
        refuse("%s: N4 VIOLATED -- T at endTime spans [%.4g, %.4g] K, which reaches within "
               "1 %% of the frozen limitTemperature bounds [%.4g, %.4g].  The fvOptions "
               "limiter is BINDING, so the solve is not reporting the registered physics."
               % (level, lo, hi, LIMIT_T_MIN, LIMIT_T_MAX))
    return dict(lo=lo, hi=hi)


# ---- strict completion (CLAUDE.md rule 4) -----------------------------------
def check_completion(level_dir, level):
    """CLAUDE.md rule 4, with ONE DECLARED DEPARTURE (N2), ruled by the supervisor
    2026-09-04 and consistent with VMFL051's own frozen DEPARTURE 2.

    R2's limb was `count of ExecutionTime lines == endTime`.  That is IDENTICALLY the
    iteration count only for a STEADY solver where one iteration prints one line and
    endTime IS the iteration count.  For an adaptive-time-step transient run,
    int(round(0.080)) = 0 against ~38 000 lines and the limb refuses every level.  RULE 4 IS
    NOT THE PROBLEM; THAT IMPLEMENTATION OF IT IS.

    THE REPLACEMENT IS STRICTLY STRONGER, and every term is computable from frozen
    constants:
      (a) n(ExecutionTime) == n(Time =)        -- every advanced step printed its cost
      (b) last Time == endTime within maxDeltaT -- the run advanced all the way
      (c) n(Time =) >= endTime / maxDeltaT      -- it cannot have got there in fewer steps
      (d) the Time sequence is STRICTLY INCREASING -- which catches a restart splice that
          a bare count never would, and which R2's limb did not test at all.
    """
    rcf = os.path.join(level_dir, "RUN_RC")
    if not os.path.isfile(rcf):
        refuse("%s: RUN_RC absent -- the driver's exit code was never recorded (rule 4)" % level)
    rc = open(rcf).read().strip()
    if rc != "0":
        refuse("%s: RUN_RC = %s, not 0 (rule 4)" % (level, rc))
    log = os.path.join(level_dir, "log.rhoPimpleFoam")
    if not os.path.isfile(log):
        refuse("%s: log.rhoPimpleFoam absent (rule 4)" % level)
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
    "<L>/log.rhoPimpleFoam",
    "<L>/system/controlDict",
    "<L>/system/blockMeshDict",
    "<L>/0/T",
    "<L>/<endTime>/T", "<L>/<endTime>/U", "<L>/<endTime>/p",
    "<L>/postProcessing/centreline/<k*SAMPLE_DT>/line_T_U.xy",
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
        want = [os.path.join(ld, "RUN_RC"), os.path.join(ld, "log.rhoPimpleFoam"),
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
    print("VMFL046-R3  Supersonic flow with a normal shock in a CD nozzle (VM2026R1 p.155)")
    print("solver: rhoPimpleFoam (TRANSIENT).  R2's rhoSimpleFoam had NO time derivative;")
    print("        branch (b) pre-committed a NUMERICS change and this is it.")
    print("gate  : x_shock vs %.3f m, band +-%.1f %% (= +-%.4f m)  -- UNCHANGED from R1/R2"
          % (ANALYTICAL_SHOCK, 100 * SHOCK_TOL, BAND))
    print("plateau: ptp(x_shock) over two adjacent W=endTime/%d windows AND their mean drift"
          " <= DELTA_X = %.3e m -- UNCHANGED from R2" % (W_FRACTION, DELTA_X))
    print("        reader = INTERPOLATING last downward M=1 crossing")
    print()

    st, xs_level = {}, []
    for L in ("L1", "L2", "L3"):
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            refuse("level directory absent: %s" % ld)
        endt, tname, tpath, nsteps = check_completion(ld, L)
        samp = assert_refining_sampler(ld, L)
        lim = check_limiters_nonbinding(os.path.join(tpath, "T"), L)
        hist = centreline_history(ld, endt)
        ser = shock_series(hist)
        pl = plateau(ser, endt)

        pa = plant_gate_reader(hist[-1][1])
        pb = plant_plateau_reducer(pl["A"])
        pc1 = plant_series_translation(pl["A"])
        pc2 = plant_field_readback_per_sample(pl["A"])
        pd = plant_T_field(os.path.join(tpath, "T"))

        cl_last = to_mach(read_centreline_raw(hist[-1][1]))
        st[L] = dict(endt=endt, n=nsteps, pl=pl, samp=samp, lim=lim,
                     snap=shock_location_snapping(cl_last),
                     pa=pa, pb=pb, pc1=pc1, pc2=pc2, pd=pd)
        xs_level.append(pl["x_level"])

        dev = 100.0 * (pl["x_level"] - ANALYTICAL_SHOCK) / ANALYTICAL_SHOCK
        print("%s  endTime %.6g s in %d time steps  (sampler nPoints %d, spacing %.6e m, "
              "sampler/mesh %.6f)" % (L, endt, nsteps, samp["npoints"], samp["s"],
                                      samp["ratio"]))
        print("     x_shock (window-A mean, THE LEVEL VALUE) = %.9f m   (%+.4f %% vs %.3f)"
              % (pl["x_level"], dev, ANALYTICAL_SHOCK))
        print("     x_shock (final sample)                   = %.9f m"
              % pl["x_final"])
        print("     plateau P1=%.4e  P2=%.4e  P3=%.4e   vs DELTA_X=%.3e  ->  %s"
              % (pl["p1"], pl["p2"], pl["p3"], DELTA_X,
                 "PLATEAU" if pl["ok"] else "NOT PLATEAUED"))
        print("     T at endTime spans [%.5g, %.5g] K -- limitTemperature bounds "
              "[%.4g, %.4g] NON-BINDING (N4)" % (lim["lo"], lim["hi"],
                                                 LIMIT_T_MIN, LIMIT_T_MAX))
        print("     plants: A err %.3e (tol %.3e) | B ptp %.4e->%.4e | C1 inert change "
              "%.3e, live +%.6e | C2 worst %.3e (tol %.3e), spread %.3e | D err %.3e"
              % (pa["err"], pa["tol"], pb["base"], pb["got"],
                 pc1["inert"] - pc1["base"], pc1["live"] - pc1["base"],
                 pc2["worst"], pc2["tol"], pc2["spread"], pd["err"]))
        print("     R1's node-snapping reader on the same bytes: %.9f m (quantum %.4e m, "
              "%.2fx DELTA_X -- unusable, which is why R2/R3 interpolate)"
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
    print("  unreachable here and this comparator cannot print it.")
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
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_synth_")
    p = os.path.join(tmp, "line_T_U.xy")
    _write_raw(p, rows)
    return read_centreline_raw(p)


def selftest():
    ok = [0]
    bad = [0]

    def arm(label, cond):
        (ok if cond else bad).__getitem__(0)
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

    print("== rule-4 N2 transliteration ==")
    for label, times, nexec, endt, maxdt, want_refuse in (
            ("complete run", [i * 1e-5 for i in range(1, 8001)], 8000, 0.08, 1e-4, False),
            ("truncated log (exec count short)", [i * 1e-5 for i in range(1, 8001)], 7999,
             0.08, 1e-4, True),
            ("stopped early", [i * 1e-5 for i in range(1, 4001)], 4000, 0.08, 1e-4, True),
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

    print("== N4 limiter non-binding ==")
    must_refuse("N4 refuses a T field touching the lower bound",
                lambda: _n4_on([151.0, 400.0, 450.0]))
    must_refuse("N4 refuses a T field touching the upper bound",
                lambda: _n4_on([330.0, 400.0, 1990.0]))
    r = _n4_on([328.0, 400.0, 500.0])
    arm("N4 passes the physical range [328, 500] K", r["lo"] == 328.0 and r["hi"] == 500.0)

    print("\nSELFTEST: %d ok, %d FAILED" % (ok[0], bad[0]))
    print("Per charter §39.5 this proves LOGIC and NOT INTERFACE.  The interface evidence is")
    print("PREREGISTRATION §12, which names the real solver-written paths on disk.")
    return 0 if bad[0] == 0 else 1


_SYNTH_DIR = []


def _fake_window(n):
    """A window of n REAL FILES on disk, each a synthetic centreline with the shock at a
    different place -- i.e. a HUNTING window, which is the case R2's PLANT C could not
    handle.  Returned in the (time, path) shape the plants consume."""
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_win_")
    _SYNTH_DIR.append(tmp)
    out = []
    for i in range(n):
        xs = 1.10 + 0.04 * (i % 4)
        rows = _synth(641, xs)
        p = os.path.join(tmp, "s%d.xy" % i)
        _write_raw(p, rows)
        out.append(((i + 1) * SAMPLE_DT, p))
    return out


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
    pts = [(i * SAMPLE_DT, 1.09 + 0.12 * (i % 2)) for i in range(16)]
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
    tmp = tempfile.mkdtemp(prefix="vmfl046r3_n4_")
    try:
        p = os.path.join(tmp, "T")
        open(p, "w").write(
            "FoamFile { version 2.0; format ascii; class volScalarField; object T; }\n"
            "internalField   nonuniform List<scalar>\n%d\n(\n%s\n)\n;\n"
            % (len(vals), "\n".join("%.10g" % v for v in vals)))
        return check_limiters_nonbinding(p, "SELFTEST")
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
            print("§39.5 path enumeration for VMFL046-R3 against %s" % args[1])
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
