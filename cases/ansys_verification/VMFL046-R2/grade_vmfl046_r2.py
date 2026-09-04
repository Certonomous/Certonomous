#!/usr/bin/env python3
"""VMFL046-R2 COMPARATOR -- the grading path for the re-run owed under charter §37.4.

WHAT IS DIFFERENT FROM R1 (`../VMFL046/grade_vmfl046.py`, frozen, read-only):

  D1  The centreline sampler REFINES WITH THE MESH (case side; asserted here).
  D2  The PLATEAU CRITERION IS ON THE SHOCK LOCATION, not on M(x=0.9).  M(0.9) is
      supersonic and UPSTREAM of the shock and is causally incapable of seeing it move
      (charter §31.1; measured blindness ratio 1.85e+07 at inviscid L3).
  D3  THE SHOCK READER INTERPOLATES.  R1's reader (`grade_vmfl046.py:251-254`) returns
      `xs[i+1]` at the largest adjacent-sample Mach drop -- it SNAPS TO A SAMPLE NODE and
      its output set is {0} u {k * dx_sample}, a quantum (charter §35.1, §37.1).  This
      reader is the LAST downward Mach = 1 crossing, LINEARLY INTERPOLATED -- the form
      `verification/runs/ansys_verification/diagnostic_shock_steadiness.py:82-95` that
      `VERIFICATION_CHARTER §2am` named as §31's reader.  Bringing it INSIDE a frozen
      grading path is the move charter §37.4 pre-registered as right and as moving the
      interpretive ground under §31.  Said here, on the face of the document.
  D4  The plateau is a PEAK-TO-PEAK OVER A WINDOW on two adjacent windows plus a
      window-mean drift limb -- NOT a two-sample difference.  A two-sample difference on
      an oscillating series measures the PHASE, not the convergence.

REFUSES (exit 2) rather than degrades, everywhere.  A `--selftest` pass proves LOGIC and
never INTERFACE (charter §39.5): PREREGISTRATION.md §11 names, for every path this file
reads, a REAL EXISTING FILE from the R1 run that proves the registered solver writes it,
and `--paths <run_root>` re-checks that list against a run root on demand.
"""
import glob
import math
import os
import re
import shutil
import sys
import tempfile

# ---- FROZEN CONSTANTS -------------------------------------------------------
GAMMA           = 1.4
R_GAS           = 287.0

# PRIMARY GATE -- UNCHANGED FROM R1.  Not re-derived, not re-rounded, not moved.
ANALYTICAL_SHOCK = 1.250          # m, the frozen R1 reference value (see PREREG §7 note)
SHOCK_TOL        = 0.05           # 5 % of ANALYTICAL_SHOCK -> band half-width 0.0625 m
BAND             = SHOCK_TOL * ANALYTICAL_SHOCK

# PLATEAU -- threshold ADOPTED UNCHANGED from charter §31's already-frozen reinstatement
# condition (6.25e-04 m = 1 % of the 0.0625 m band).  It was NOT chosen by this document.
# Applied here to a PEAK-TO-PEAK over a window, which is STRICTLY STRICTER than §31's
# two-sample difference: ptp <= d implies |last - prev| <= d.  Nothing is loosened.
DELTA_X          = 6.25e-04       # m
W_FRACTION       = 10             # plateau window W = endTime / W_FRACTION
SAMPLE_INTERVAL  = 500            # iterations between centreline samples (controlDict)
MIN_WINDOW_SAMPLES = 8            # a ptp over fewer samples is not a ptp; refuse

# SECONDARIES -- DEMOTE-ONLY (charter §21.3), retained UNCHANGED from R1.
P_OBS_LO, P_OBS_HI = 0.5, 2.5
GCI_FINE_MAX       = 0.15
R_REFINE, FS       = 2.0, 1.25

# DIAGNOSTIC ONLY -- never a gate limb in R2.
M_GATE_X         = 0.9

# PLANTS (CLAUDE.md rule 3)
PLANT_DX         = 1.000e-02      # m, the shock displacement planted into a SCRATCH copy
PLANT_DX_SMALL   = 6.250e-04      # m, exactly DELTA_X -- the quantum-discrimination plant
PLANT_K_T        = 1.0e-3         # relative plant into the T field


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
    """D3 -- THE INTERPOLATING READER, AND IT IS A GATE LIMB.

    The LAST downward Mach = 1 crossing, linearly interpolated.  Taking the FIRST crossing
    returns the THROAT (the subsonic->supersonic sonic point), a different feature ~0.7 m
    upstream.  Form: diagnostic_shock_steadiness.py:82-95.

    RESOLUTION (charter §35.1 / §37.3 require a threshold to name its reader and state that
    reader's resolution): the returned x moves CONTINUOUSLY with the sampled Mach values --
    it has no quantum.  Measured on the real R1 L3 final sample, a relative perturbation eps
    applied to the Mach field shifts the reading by 1.2e-02 * eps metres; at writePrecision
    12 (eps ~ 1e-12) that is ~1.2e-14 m, i.e. 5.2e+10 times FINER than DELTA_X = 6.25e-04 m.
    R1's node-snapping reader, by contrast, had a quantum of 5.0025e-03 m -- 8.004 times
    COARSER than the same threshold, which is why that threshold was unfalsifiable there.
    """
    found = None
    for i in range(1, len(cl)):
        xa, ma = cl[i - 1]
        xb, mb = cl[i]
        if (ma - 1.0) * (mb - 1.0) < 0 and mb < ma:
            found = xa + (1.0 - ma) * (xb - xa) / (mb - ma)
    return found


def shock_location_snapping(cl):
    """R1's frozen reader (`grade_vmfl046.py:251-254`), REPRODUCED VERBATIM IN BEHAVIOUR.
    NOT A GATE LIMB IN R2.  It exists here for exactly two purposes: to print the quantum
    comparison beside the verdict, and to be the MUTANT the planted control must refuse."""
    xs = [x for x, _ in cl]
    Ma = [m for _, m in cl]
    drops = [(Ma[i] - Ma[i + 1], xs[i + 1]) for i in range(len(Ma) - 1)]
    return max(drops)[1]


def interp_at(cl, x0):
    for i in range(1, len(cl)):
        xa, ya = cl[i - 1]
        xb, yb = cl[i]
        if xa <= x0 <= xb:
            return ya + (yb - ya) * (x0 - xa) / (xb - xa)
    refuse("x=%g outside the sampled range" % x0)


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
def read_endtime(level_dir):
    cd = os.path.join(level_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse("no system/controlDict in %s" % level_dir)
    txt = open(cd).read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+\-]+)\s*;", txt, re.M)
    if not m:
        refuse("endTime not found in %s" % cd)
    n = re.search(r"nPoints\s+([0-9]+)\s*;", txt)
    if not n:
        refuse("nPoints not found in %s -- the D1 refining-sampler assert cannot run" % cd)
    return float(m.group(1)), int(n.group(1))


def assert_refining_sampler(level_dir, level):
    """D1 -- the sampler must be the level's own, not a hard-coded 400.
    Expected nPoints = 2*(NXA+NXB)+1, read from the level's OWN blockMeshDict so this is a
    check against the mesh that actually ran, not against a table in this file."""
    bm = os.path.join(level_dir, "system", "blockMeshDict")
    if not os.path.isfile(bm):
        refuse("no system/blockMeshDict in %s (D1 assert)" % level_dir)
    counts = re.findall(r"hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)", open(bm).read())
    if len(counts) != 2:
        refuse("expected 2 hex blocks in %s, found %d (D1 assert)" % (bm, len(counts)))
    nx_total = int(counts[0][0]) + int(counts[1][0])
    endt, npoints = read_endtime(level_dir)
    # The controlDict that RAN must carry exactly two writeIntervals: the fields at endTime
    # and the centreline every SAMPLE_INTERVAL.  This refuses a CLAUSE-B smoke configuration
    # (which may set the sampler to 1) from ever reaching the grading path.
    wi = sorted(set(int(v) for v in re.findall(
        r"^\s*writeInterval\s+([0-9]+)\s*;", open(
            os.path.join(level_dir, "system", "controlDict")).read(), re.M)))
    if wi != sorted({int(round(endt)), SAMPLE_INTERVAL}):
        refuse("%s: controlDict writeIntervals are %s, expected {%d (fields at endTime), "
               "%d (centreline)} -- this is not the graded configuration"
               % (level, wi, int(round(endt)), SAMPLE_INTERVAL))
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
             and re.match(r"^[0-9]+(\.[0-9]+)?$", d) and d != "0"]
    if not times:
        refuse("no numeric time dir (other than 0) in %s" % level_dir)
    return max(times)[1:]


def centreline_history(level_dir, endtime):
    """-> [(iteration, path)] sorted.  The history must be COMPLETE: every multiple of
    SAMPLE_INTERVAL up to endTime.  A missing sample must refuse, never silently shrink a
    plateau window (the caller-side face of rule 3)."""
    base = os.path.join(level_dir, "postProcessing", "centreline")
    if not os.path.isdir(base):
        refuse("no postProcessing/centreline in %s" % level_dir)
    hist = []
    for d in os.listdir(base):
        p = os.path.join(base, d, "line_T_U.xy")
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and os.path.isfile(p):
            hist.append((float(d), p))
    hist.sort()
    want = int(round(endtime / SAMPLE_INTERVAL))
    if len(hist) != want:
        refuse("centreline history has %d samples, expected %d (endTime %g every %d): %s"
               % (len(hist), want, endtime, SAMPLE_INTERVAL, base))
    for k in range(1, want + 1):
        if abs(hist[k - 1][0] - k * SAMPLE_INTERVAL) > 1e-6:
            refuse("centreline history is not the complete %d-step sequence at index %d "
                   "(found %g, expected %g): %s"
                   % (SAMPLE_INTERVAL, k, hist[k - 1][0], k * SAMPLE_INTERVAL, base))
    return hist


# ---- the plateau (D2 + D4) --------------------------------------------------
def shock_series(hist):
    out = []
    for it, p in hist:
        x = shock_location(to_mach(read_centreline_raw(p)))
        if x is None:
            refuse("no downward Mach=1 crossing in sample %s -- the shock is not resolvable "
                   "in this profile; refusing rather than reporting a location" % p)
        out.append((it, x))
    return out


def windows(series, endtime):
    """Two ADJACENT windows of W = endTime/W_FRACTION iterations each, sharing one boundary
    sample.  A: (endTime-W, endTime].  B: (endTime-2W, endTime-W]."""
    W = endtime / float(W_FRACTION)
    A = [(it, x) for it, x in series if it >= endtime - W - 1e-6]
    B = [(it, x) for it, x in series
         if endtime - 2 * W - 1e-6 <= it <= endtime - W + 1e-6]
    if len(A) < MIN_WINDOW_SAMPLES or len(B) < MIN_WINDOW_SAMPLES:
        refuse("plateau windows hold %d / %d samples, need >= %d each (W=%g, interval %d): "
               "a peak-to-peak over fewer samples is not a peak-to-peak"
               % (len(A), len(B), MIN_WINDOW_SAMPLES, W, SAMPLE_INTERVAL))
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
    # P0 -- charter §31's own literal two-sample limb, REPORTED so the reinstatement claim
    # is legible.  It is IMPLIED by P1 and is not an independent gate.
    p0 = abs(series[-1][1] - series[-2][1])
    ok = (p1 <= DELTA_X) and (p2 <= DELTA_X) and (p3 <= DELTA_X)
    return dict(W=W, A=A, B=B, p0=p0, p1=p1, p2=p2, p3=p3, ok=ok,
                x_level=mean(A), x_final=series[-1][1])


# ---- planted controls (CLAUDE.md rule 3) ------------------------------------
#
# THE RULE THESE CONTROLS ARE BUILT TO (adopted for this territory 2026-09-04, and it is in
# the frozen bytes because a rule that lives only in a report is not a rule):
#
#   A PLANTED CONTROL MUST BE DESIGNED AGAINST THE *REDUCTION*, NOT AGAINST THE FIELD.
#     for a MEAN          -> plant a proper subset
#     for a PEAK-TO-PEAK  -> plant the current EXTREMUM
#     for a MAX           -> plant the ARGMAX
#   A PLANT THAT DOES NOT MOVE THE SPECIFIC STATISTIC THE GATE READS IS INERT NO MATTER HOW
#   LARGE IT IS.
#
# Paid for twice in two days by two failure modes of the same mistake:
#   CANCELLATION -- a plant covering the WHOLE reduction set is a rigid translation and the
#                   ptp is identically unchanged (PLANT C below demonstrates it deliberately);
#   ABSORPTION   -- a plant into an INTERIOR member is swallowed whole when the window already
#                   spreads wider than the plant.  Measured on this case's own real data: a
#                   1.0e-02 m interior plant into the R1 L3 final window (spread 1.1066e-01 m)
#                   left the ptp at 1.1066e-01 m, UNCHANGED -- a control that passes while
#                   proving nothing.  PLANT B therefore plants the window's MAXIMUM.
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
    tmp = tempfile.mkdtemp(prefix="vmfl046r2_plantA_")
    try:
        dst = os.path.join(tmp, "line_T_U.xy")
        _write_raw(dst, _shift_profile(raw, dx))
        x1 = reader(to_mach(read_centreline_raw(dst)))
        if x1 is None:
            refuse("PLANTED CONTROL A FAILED: the reader lost the shock after a %+.3e m "
                   "plant (rule 3)" % dx)
        err = abs((x1 - x0) - dx)
        tol = 0.25 * abs(dx)      # tolerance scales WITH THE PLANT, never with the mesh:
        # a tolerance of half a sample spacing would let a NODE-SNAPPING reader pass a plant
        # smaller than its own quantum, which is the exact failure §35.1/§37.1 names.
        if err > tol:
            refuse("PLANTED CONTROL A FAILED: planted %+.4e m, reader saw %+.4e m "
                   "(error %.3e > 25 %% of the plant, %.3e).  A reader not shown able to "
                   "see a known displacement cannot report a zero (rule 3).  file=%s"
                   % (dx, x1 - x0, err, tol, sample_path))
        return dict(x0=x0, x1=x1, planted=dx, err=err, spacing=s, tol=tol)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def plant_plateau_reducer(window, dx=PLANT_DX, reader=None, full_set=False):
    """PLANT B (proper subset) and PLANT C (full set, the INERT demonstration).

    THE POINT.  The plateau reader reduces (peak-to-peak) OVER A WINDOW.  A plant applied
    to EVERY member of the reduction set is a rigid translation -- the ptp is IDENTICALLY
    unchanged and the control is INERT.  That is how a planted control dies without saying
    so.  PLANT B therefore shifts exactly ONE sample of the window -- a PROPER, NON-EMPTY
    SUBSET -- and the reducer must see it.  PLANT C shifts all of them and ASSERTS the ptp
    does NOT move, which is the proof that the proper-subset design is necessary and not
    decorative.

    AND THE SUBSET IS THE WINDOW'S CURRENT MAXIMUM, WHICH IS NOT A DETAIL.  Shifting an
    INTERIOR sample by +dx changes the ptp by NOTHING whenever the window already spreads
    wider than dx -- and on the real R1 L3 window it spreads 0.111 m against a 0.010 m
    plant, so an interior plant passes while proving nothing.  Displacing the current
    MAXIMUM raises the ptp by ~dx whatever the base spread, so the control is live at every
    level and in both branches.
    """
    reader = reader or shock_location
    base_pts = []
    for it, path in window:
        x = reader(to_mach(read_centreline_raw(path)))
        if x is None:
            refuse("plant B/C: shock lost in an UNPLANTED window member: %s" % path)
        base_pts.append((it, x))
    base = ptp(base_pts)
    argmax = max(range(len(base_pts)), key=lambda i: base_pts[i][1])
    idx = list(range(len(window))) if full_set else [argmax]
    tmp = tempfile.mkdtemp(prefix="vmfl046r2_plantBC_")
    try:
        new = []
        for k, (it, path) in enumerate(window):
            raw = read_centreline_raw(path)
            if k in idx:
                dst = os.path.join(tmp, "s%d.xy" % k)
                _write_raw(dst, _shift_profile(raw, dx))
                raw = read_centreline_raw(dst)
            x = reader(to_mach(raw))
            if x is None:
                refuse("plant B/C: shock lost in window member %d" % k)
            new.append((it, x))
        got = ptp(new)
        if full_set:
            # INERT means: undetectable AT THE SCALE THAT DECIDES, i.e. far below DELTA_X.
            # (It is not exactly zero: the shift is performed by resampling, whose own
            # interpolation error differs by ~1e-7 m between window members.)
            tol_c = 0.01 * DELTA_X
            if abs(got - base) > tol_c:
                refuse("PLANT C inconsistent: a rigid %+.3e m shift of the WHOLE window "
                       "moved the ptp by %.3e (> 1 %% of DELTA_X); the plant mechanism is "
                       "not a translation" % (dx, got - base))
            return dict(base=base, got=got, inert=True)
        if not (got >= base + 0.75 * dx):
            refuse("PLANTED CONTROL B FAILED: a %+.4e m displacement planted into the "
                   "MAXIMUM of %d window samples moved the peak-to-peak only from %.4e to "
                   "%.4e (needed >= %.4e).  The plateau reducer cannot see a known "
                   "non-zero, so its ptp is not evidence of a plateau (rule 3)."
                   % (dx, len(window), base, got, base + 0.75 * dx))
        return dict(base=base, got=got, inert=False, idx=argmax)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def plant_T_field(path, k=PLANT_K_T):
    """PLANT D -- the physical field reader, carried over from R1 unchanged in intent."""
    vals, span = read_T_internal(path)
    scale = max(abs(v) for v in vals)
    plant = k * scale
    if plant < 1.0e-12:
        refuse("planted-zero: T field scale %.3g too small" % scale)
    tmp = tempfile.mkdtemp(prefix="vmfl046r2_plantT_")
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


# ---- strict completion (CLAUDE.md rule 4) -----------------------------------
def check_completion(level_dir, level):
    rcf = os.path.join(level_dir, "RUN_RC")
    if not os.path.isfile(rcf):
        refuse("%s: RUN_RC absent -- the driver's exit code was never recorded (rule 4)" % level)
    rc = open(rcf).read().strip()
    if rc != "0":
        refuse("%s: RUN_RC = %s, not 0 (rule 4)" % (level, rc))
    log = os.path.join(level_dir, "log.rhoSimpleFoam")
    if not os.path.isfile(log):
        refuse("%s: log.rhoSimpleFoam absent (rule 4)" % level)
    txt = open(log).read()
    if "FOAM FATAL" in txt:
        refuse("%s: FOAM FATAL in the solver log (rule 4)" % level)
    if not re.search(r"^End\s*$", txt, re.M):
        refuse("%s: no 'End' line in the solver log (rule 4)" % level)
    endt, _ = read_endtime(level_dir)
    tname, tpath = latest_time_dir(level_dir)
    if abs(float(tname) - endt) > 1e-6:
        refuse("%s: last time %s != endTime %g (rule 4) -- the run stopped early" % (level, tname, endt))
    # ExecutionTime count == endTime.  R1's registration declared this limb INAPPLICABLE;
    # it is applicable and it is measured: R1's own L3 log carries exactly 20000 lines at
    # endTime 20000.  R2 applies it.
    n_exec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if n_exec != int(round(endt)):
        refuse("%s: %d ExecutionTime lines but endTime is %g (rule 4)" % (level, n_exec, endt))
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
    return endt, tname, tpath


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
    "<L>/log.rhoSimpleFoam",
    "<L>/system/controlDict",
    "<L>/system/blockMeshDict",
    "<L>/0/T",
    "<L>/<endTime>/T", "<L>/<endTime>/U", "<L>/<endTime>/p",
    "<L>/postProcessing/centreline/<n*500>/line_T_U.xy",
]


def check_paths(run_root, levels=("L1", "L2", "L3")):
    """charter §39.5 -- every path this comparator reads, checked to EXIST in a real run
    root.  A --selftest pass proves logic, never interface."""
    bad = 0
    for L in levels:
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            print("  %-3s ABSENT: %s" % (L, ld)); bad += 1; continue
        endt, _ = read_endtime(ld)
        want = [os.path.join(ld, "RUN_RC"), os.path.join(ld, "log.rhoSimpleFoam"),
                os.path.join(ld, "system", "controlDict"),
                os.path.join(ld, "system", "blockMeshDict"),
                os.path.join(ld, "0", "T")]
        tn = ("%g" % endt)
        want += [os.path.join(ld, tn, f) for f in ("T", "U", "p")]
        want += [os.path.join(ld, "postProcessing", "centreline", "%d" % SAMPLE_INTERVAL,
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
    levels = ("L1", "L2", "L3")
    st = {}
    print("VMFL046-R2  run_root=%s" % run_root)
    print("gate: shock location vs analytical %.3f m, band %.0f %% (UNCHANGED from R1)"
          % (ANALYTICAL_SHOCK, 100 * SHOCK_TOL))
    print("plateau: ptp(x_shock) over two adjacent W=endTime/%d windows AND their mean drift"
          " <= DELTA_X = %.3e m, reader = INTERPOLATING last downward M=1 crossing"
          % (W_FRACTION, DELTA_X))
    for L in levels:
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            refuse("level dir missing: %s" % ld)
        endt, tname, tpath = check_completion(ld, L)
        samp = assert_refining_sampler(ld, L)
        hist = centreline_history(ld, endt)
        ser = shock_series(hist)
        pl = plateau(ser, endt)
        pa = plant_gate_reader(hist[-1][1])
        pb = plant_plateau_reducer(hist[-len(pl["A"]):], full_set=False)
        pc = plant_plateau_reducer(hist[-len(pl["A"]):], full_set=True)
        pd = plant_T_field(os.path.join(tpath, "T"))
        cl_last = to_mach(read_centreline_raw(hist[-1][1]))
        st[L] = dict(endt=endt, samp=samp, pl=pl, ser=ser,
                     m09=interp_at(cl_last, M_GATE_X),
                     snap=shock_location_snapping(cl_last))
        print("")
        print("  %s  endTime=%g  cells_axial=%d  nPoints=%d  sampler dx=%.6e  mesh dx=%.6e"
              "  sampler/mesh=%.6f" % (L, endt, samp["nx"], samp["npoints"], samp["s"],
                                       samp["dx"], samp["ratio"]))
        print("     x_shock (window-A mean, THE LEVEL VALUE) = %.9f m   (%+.4f %% vs %.3f)"
              % (pl["x_level"], 100 * (pl["x_level"] - ANALYTICAL_SHOCK) / ANALYTICAL_SHOCK,
                 ANALYTICAL_SHOCK))
        print("     x_shock (final sample)                   = %.9f m   |diff to level value|"
              " = %.3e (<= ptp_A by construction)" % (pl["x_final"], abs(pl["x_final"] - pl["x_level"])))
        print("     PLATEAU  P1 ptp(A)=%.4e  P2 ptp(B)=%.4e  P3 |meanA-meanB|=%.4e   vs "
              "DELTA_X=%.3e  ->  %s" % (pl["p1"], pl["p2"], pl["p3"], DELTA_X,
                                        "PLATEAU" if pl["ok"] else "NOT PLATEAUED"))
        print("     [P0, BOOKKEEPING ONLY -- NOT A GATE LIMB] two-sample final drift = %.4e m "
              "(%s 6.25e-04).  §31's reinstatement limb is ESCALATED (PREREGISTRATION §6.1a): a "
              "two-sample difference on an oscillating series is a PHASE detector, and NOTHING "
              "here may be cited as a §31 reinstatement in EITHER direction."
              % (pl["p0"], "<=" if pl["p0"] <= 6.25e-4 else ">"))
        print("     [quantum] node-snapping reader on the same bytes = %.9f m; its quantum "
              "%.4e m is %.2fx the threshold -- unusable, which is why R2 interpolates"
              % (st[L]["snap"], samp["s"], samp["s"] / DELTA_X))
        print("     [diagnostic, NOT a gate limb] M(%.2f) = %.8f" % (M_GATE_X, st[L]["m09"]))
        print("     plants: A gate reader saw %+.4e of %+.4e (err %.2e) | B subset ptp "
              "%.3e -> %.3e | C full-set ptp %.3e -> %.3e (INERT, as it must be) | D T-field"
              " %d cells, err %.2e"
              % (pa["x1"] - pa["x0"], pa["planted"], pa["err"], pb["base"], pb["got"],
                 pc["base"], pc["got"], pd["n"], pd["err"]))

    print("")
    unplateaued = [L for L in levels if not st[L]["pl"]["ok"]]
    if unplateaued:
        print("VERDICT: NOT A RESULT -- levels %s did not reach the frozen plateau "
              "(CLAUDE.md rule 5 step 1)." % ", ".join(unplateaued))
        print("BRANCH (b), PRE-REGISTERED: this is the outcome PREREGISTRATION §9(b) names. "
              "The successor VMFL046-R3 changes the NUMERICS -- local time stepping, a "
              "genuinely transient run driven to steady state, or a density-based flux "
              "scheme (charter §20.2 option (c), pre-committed 2026-09-02, uncontaminated). "
              "IT DOES NOT CHANGE THE GATE, THE BAND OR THE PLATEAU THRESHOLD.")
        return 0

    xs = [st[L]["pl"]["x_level"] for L in levels]
    tri = roache(*xs)
    sdev = (xs[2] - ANALYTICAL_SHOCK) / ANALYTICAL_SHOCK
    print("triple on x_shock: L1=%.6f L2=%.6f L3=%.6f  state=%s R=%.4g p=%s GCI=%s"
          % (xs[0], xs[1], xs[2], tri["state"], tri["R"],
             ("%.4f" % tri["p"]) if tri["p"] is not None else "n/a",
             ("%.3g %%" % (100 * tri["gci"])) if tri["gci"] is not None else "n/a"))
    print("finest-level deviation from analytical %.3f m: %+.4f %% (band +/- %.0f %%)"
          % (ANALYTICAL_SHOCK, 100 * sdev, 100 * SHOCK_TOL))
    if tri["state"] != "CONVERGING":
        print("VERDICT: NOT A RESULT -- Roache triple %s (CLAUDE.md rule 5 step 2)" % tri["state"])
        return 0
    primary_ok = abs(sdev) <= SHOCK_TOL
    p_fire = not (P_OBS_LO <= tri["p"] <= P_OBS_HI)
    g_fire = (tri["gci"] is None) or (tri["gci"] > GCI_FINE_MAX)
    print("secondaries (DEMOTE-ONLY, charter §21.3): p_obs %s | GCI_fine %s"
          % ("FIRED" if p_fire else "not fired", "FIRED" if g_fire else "not fired"))
    print("  ^ a secondary that did NOT fire is NOT evidence of quality (§21.3): both were "
          "fixed after coarse numbers had been seen, so they may only DEMOTE.")
    if not primary_ok:
        print("VERDICT: GATE FAIL -- shock location %+.4f %% outside the +/-%.0f %% band."
              % (100 * sdev, 100 * SHOCK_TOL))
        return 0
    if p_fire or g_fire:
        print("VERDICT: GATE FAIL -- primary met but a demote-only secondary fired.")
        return 0
    print("VERDICT: GATE REACHED -- primary limb met and no secondary fired.")
    print("  THIS IS THE REGISTERED CEILING AND `PASS` IS UNREACHABLE HERE (ruled 2026-09-04, "
          "PREREGISTRATION §13.3a).  §23.3's cap-lift rested on a model-form bound of <= 0.63 %; "
          "the direct inviscid-vs-viscous comparison on identical meshes measures 0.356 / 2.074 / "
          "5.109 % at L1/L2/L3 -- 8.1x outside it at L3 and GROWING with refinement.  Under "
          "charter §24.4 an enumerated-channel bound with no completeness argument is UNVALIDATED "
          "and DOES NOT LIFT THE CAP.  No `PASS` is available from this registration by any path.")
    return 0


# ---- selftest ---------------------------------------------------------------
def _synth(n, x_shock, x0=0.002, x1=1.998, T=300.0, smear_cells=3.0):
    """A synthetic centreline whose shock sits at x_shock, written in the real 5-column
    layout.  THE SHOCK IS SMEARED over `smear_cells` sample spacings, because the real one
    is: first-order upwind CAPTURES the shock over a few cells, and the interpolating
    reader's continuity depends on that.  A zero-width jump sampled discretely would make
    the interpolated crossing quantize between the two bracketing samples -- a real property
    of the reader, disclosed in PREREGISTRATION §5, and the reason this synthetic must not
    be a step function."""
    span = x1 - x0
    s = span / (n - 1.0)
    w = smear_cells * s
    rows = []
    for i in range(n):
        x = x0 + span * i / (n - 1.0)
        if x < 0.5:
            M = 0.3 + 1.4 * (x / 0.5)          # up through 1 near the throat
        else:
            m_pre = 1.7 + 0.5 * (x - 0.5)
            m_post = 0.55 - 0.05 * (x - x_shock)
            if x <= x_shock - 0.5 * w:
                M = m_pre
            elif x >= x_shock + 0.5 * w:
                M = m_post
            else:
                f = (x - (x_shock - 0.5 * w)) / w
                M = m_pre * (1.0 - f) + m_post * f
        rows.append((x, T, M * math.sqrt(GAMMA * R_GAS * T), 0.0, 0.0))
    return rows


def selftest():
    ok = True

    def arm(label, cond):
        nonlocal ok
        ok &= bool(cond)
        print("SELFTEST %-58s %s" % (label, "PASS" if cond else "FAIL"))

    def must_refuse(label, fn):
        nonlocal ok
        try:
            fn()
        except SystemExit:
            print("SELFTEST %-58s REFUSED (exit 2)  PASS" % label)
            return
        ok = False
        print("SELFTEST %-58s DID NOT REFUSE  FAIL" % label)

    td = tempfile.mkdtemp(prefix="vmfl046r2_selftest_")
    try:
        # ---- A. the interpolating reader -----------------------------------
        for target in (1.1000, 1.2500, 1.3117):
            got = shock_location(to_mach(_synth(801, target)))
            arm("reader: shock planted at %.4f -> %.6f" % (target, got),
                abs(got - target) <= (1.996 / 800.0))
        got = shock_location(to_mach(_synth(801, 1.25)))
        first = next((cl[i - 1][0] for cl in [to_mach(_synth(801, 1.25))]
                      for i in range(1, len(cl))
                      if (cl[i - 1][1] - 1) * (cl[i][1] - 1) < 0), None)
        arm("reader: returns the SHOCK (%.4f), not the THROAT (%.4f) -- the first-crossing "
            "bug sits ~%.2f m upstream" % (got, first, got - first), got > 1.0 and first < 0.6)
        # sub-quantum discrimination: two profiles a half-threshold apart must read apart
        a = shock_location(to_mach(_synth(1281, 1.2500)))
        b = shock_location(to_mach(_synth(1281, 1.2500 + 0.5 * DELTA_X)))
        arm("reader resolves 0.5*DELTA_X (%.3e) apart: d=%.3e"
            % (0.5 * DELTA_X, b - a), abs((b - a) - 0.5 * DELTA_X) < 0.05 * DELTA_X)
        sa = shock_location_snapping(to_mach(_synth(1281, 1.2500)))
        sb = shock_location_snapping(to_mach(_synth(1281, 1.2500 + 0.5 * DELTA_X)))
        s_l3 = 1.996 / 1280.0
        k_q = (sb - sa) / s_l3
        arm("MUTANT node-snapping reader QUANTIZES: for a true %.3e m shift it returns "
            "%.3e m = %.1f x its quantum, wrong by %.0f %%"
            % (0.5 * DELTA_X, sb - sa, k_q, 100 * abs((sb - sa) - 0.5 * DELTA_X) / (0.5 * DELTA_X)),
            abs(k_q - round(k_q)) < 1e-9
            and abs((sb - sa) - 0.5 * DELTA_X) > 0.25 * 0.5 * DELTA_X)

        # ---- B. plants, on files ------------------------------------------
        f0 = os.path.join(td, "line_T_U.xy")
        _write_raw(f0, _synth(1281, 1.2000))
        pa = plant_gate_reader(f0)
        arm("PLANT A: gate reader saw %+.4e of a planted %+.4e"
            % (pa["x1"] - pa["x0"], pa["planted"]), pa["err"] <= 0.5 * pa["spacing"])
        must_refuse("PLANT A with a HALF-SCALE (biased) reader must refuse",
                    lambda: plant_gate_reader(
                        f0, reader=lambda cl: 0.5 * shock_location(cl)))
        must_refuse("PLANT A with a DEAD reader (constant) must refuse",
                    lambda: plant_gate_reader(f0, reader=lambda cl: 1.2345))
        must_refuse("PLANT A at DELTA_X with the NODE-SNAPPING reader must refuse",
                    lambda: plant_gate_reader(f0, dx=PLANT_DX_SMALL,
                                              reader=shock_location_snapping))

        # a 13-sample window of a genuinely still history
        win = []
        for k in range(13):
            p = os.path.join(td, "w%02d.xy" % k)
            _write_raw(p, _synth(1281, 1.2000 + 1e-6 * k))
            win.append((54000 + 500 * k, p))
        pb = plant_plateau_reducer(win, full_set=False)
        arm("PLANT B (PROPER SUBSET: the window MAXIMUM, 1 of 13): ptp %.3e -> %.3e"
            % (pb["base"], pb["got"]), pb["got"] >= pb["base"] + 0.75 * PLANT_DX)
        wide = []
        for k in range(13):
            q = os.path.join(td, "wide%02d.xy" % k)
            _write_raw(q, _synth(1281, 1.15 + 0.05 * (k % 3)))   # ptp 0.10 >> PLANT_DX
            wide.append((54000 + 500 * k, q))
        pw = plant_plateau_reducer(wide, full_set=False)
        arm("PLANT B stays LIVE when the window already spreads %.3e >> the %.3e plant "
            "(ptp -> %.3e)" % (pw["base"], PLANT_DX, pw["got"]),
            pw["got"] >= pw["base"] + 0.75 * PLANT_DX)
        must_refuse("PLANT B on a WIDE window with an INTERIOR-only plant would be dead -- "
                    "a mid-index reader mutant must refuse",
                    lambda: plant_plateau_reducer(
                        wide, reader=lambda cl: min(shock_location(cl), 1.19)))
        pc = plant_plateau_reducer(win, full_set=True)
        arm("PLANT C (FULL SET) is INERT: ptp %.3e -> %.3e, moved %.3e = %.4f %% of DELTA_X"
            % (pc["base"], pc["got"], pc["got"] - pc["base"],
               100 * abs(pc["got"] - pc["base"]) / DELTA_X),
            abs(pc["got"] - pc["base"]) <= 0.01 * DELTA_X)
        arm("=> a plant covering the WHOLE reduction set proves nothing; B is why the "
            "subset is proper", pc["inert"] and not pb["inert"])
        must_refuse("PLANT B with a DEAD reader (constant) must refuse",
                    lambda: plant_plateau_reducer(win, reader=lambda cl: 1.2345))
        must_refuse("PLANT B at DELTA_X with the NODE-SNAPPING reader must refuse",
                    lambda: plant_plateau_reducer(win, dx=PLANT_DX_SMALL,
                                                  reader=shock_location_snapping))

        # ---- C. plateau logic ----------------------------------------------
        endt = 60000.0
        still = [(500.0 * k, 1.2 + 1e-6 * ((k % 3) - 1)) for k in range(1, 121)]
        arm("plateau: a still series PLATEAUS", plateau(still, endt)["ok"])
        moving = [(500.0 * k, 1.2 + 5e-3 * math.sin(k / 3.0)) for k in range(1, 121)]
        arm("plateau: an OSCILLATING series does NOT plateau", not plateau(moving, endt)["ok"])
        # the D4 finding, as an executable arm: a two-sample drift can be tiny at a turning
        # point of a large oscillation, and the ptp criterion must not be fooled by it.
        # The extremum is placed EXACTLY between the last two samples, so the two-sample
        # drift is identically zero while the shock swings by 0.1 m.
        turn = [(500.0 * k, 1.2 + 5e-2 * math.cos(2 * math.pi * (k - 119.5) / 12.0))
                for k in range(1, 121)]
        pt = plateau(turn, endt)
        arm("D4: a 2-sample drift of %.3e (< DELTA_X) at a turning point of a %.3e m "
            "oscillation does NOT pass the ptp criterion (ptp_A=%.3e)"
            % (pt["p0"], pt["p1"], pt["p1"]),
            pt["p0"] < DELTA_X and not pt["ok"])
        # P3 exists for a drift SLOW enough that each window's own ptp is inside DELTA_X
        # while the two windows sit apart.  Per-window ptp = 12*step, inter-window mean gap
        # = 12*step; a step of 6e-5 gives ptp 7.2e-4 > DELTA_X, so use a step that makes P1
        # and P2 pass and only P3 fail: step 4e-5 -> ptp 4.8e-4 (< DELTA_X), gap 4.8e-4.
        # That is still inside DELTA_X, so the honest arm is the DIRECTION of the limb:
        # build a drift whose windows are individually quiet but far apart.
        drift = [(500.0 * k, 1.2 + (0.0 if k <= 108 else 1.5e-3)) for k in range(1, 121)]
        pd_ = plateau(drift, endt)
        arm("plateau: P3 catches a step between windows that P2 alone would miss "
            "(P2=%.3e, P3=%.3e)" % (pd_["p2"], pd_["p3"]),
            pd_["p2"] <= DELTA_X and pd_["p3"] > DELTA_X and not pd_["ok"])
        must_refuse("plateau: too few samples per window must refuse",
                    lambda: plateau([(500.0 * k, 1.2) for k in range(1, 13)], endt))

        # ---- D. completion / structure refusals -----------------------------
        def mklevel(name, endt=2000, rc="0", end=True, nexec=None, fields=("T", "U", "p"),
                    age_ok=True, npoints=None, nx=(40, 120), hist_n=None):
            ld = os.path.join(td, name)
            os.makedirs(os.path.join(ld, "system"), exist_ok=True)
            os.makedirs(os.path.join(ld, "0"), exist_ok=True)
            npoints = npoints if npoints is not None else 2 * (nx[0] + nx[1]) + 1
            open(os.path.join(ld, "system", "controlDict"), "w").write(
                "endTime %d;\nwriteInterval %d;\nwriteInterval %d;\nnPoints %d;\n"
                % (endt, endt, SAMPLE_INTERVAL, npoints))
            open(os.path.join(ld, "system", "blockMeshDict"), "w").write(
                "blocks (\n hex (0 1 4 3 6 7 10 9) (%d 20 1) simpleGrading (1 1 1)\n"
                " hex (1 2 5 4 7 8 11 10) (%d 20 1) simpleGrading (1 1 1)\n);\n" % nx)
            open(os.path.join(ld, "RUN_RC"), "w").write(rc + "\n")
            ne = nexec if nexec is not None else endt
            open(os.path.join(ld, "log.rhoSimpleFoam"), "w").write(
                "\n".join("ExecutionTime = %g s  ClockTime = %g s" % (i, i)
                          for i in range(1, ne + 1)) + ("\n\nEnd\n" if end else "\n"))
            open(os.path.join(ld, "0", "T"), "w").write("x\n")
            tp = os.path.join(ld, str(endt))
            os.makedirs(tp, exist_ok=True)
            for f in fields:
                open(os.path.join(tp, f), "w").write(
                    "internalField   nonuniform List<scalar>\n2\n(\n300\n310\n)\n;\n")
            if not age_ok:
                os.utime(os.path.join(ld, "0", "T"), None)
            n = hist_n if hist_n is not None else endt // SAMPLE_INTERVAL
            for k in range(1, n + 1):
                d = os.path.join(ld, "postProcessing", "centreline", str(k * SAMPLE_INTERVAL))
                os.makedirs(d, exist_ok=True)
                _write_raw(os.path.join(d, "line_T_U.xy"), _synth(321, 1.2))
            return ld

        good = mklevel("good")
        check_completion(good, "good")
        print("SELFTEST %-58s PASS" % "completion: a well-formed level passes")
        must_refuse("completion: rc != 0", lambda: check_completion(mklevel("bad_rc", rc="1"), "x"))
        must_refuse("completion: no End line", lambda: check_completion(mklevel("bad_end", end=False), "x"))
        must_refuse("completion: ExecutionTime count != endTime",
                    lambda: check_completion(mklevel("bad_exec", nexec=1999), "x"))
        must_refuse("completion: missing field U",
                    lambda: check_completion(mklevel("bad_field", fields=("T", "p")), "x"))
        must_refuse("completion: AGE GUARD (0/T newer than the fields)",
                    lambda: check_completion(mklevel("bad_age", age_ok=False), "x"))
        must_refuse("D1: a hard-coded nPoints 400 that does not refine must refuse",
                    lambda: assert_refining_sampler(mklevel("bad_np", npoints=400), "x"))
        smk = mklevel("smoke_cfg")
        open(os.path.join(smk, "system", "controlDict"), "w").write(
            "endTime 2000;\nwriteInterval 2000;\nwriteInterval 1;\nnPoints 321;\n")
        must_refuse("D1: a CLAUSE-B smoke configuration (sampler interval 1) must refuse",
                    lambda: assert_refining_sampler(smk, "x"))
        arm("D1: the R2 rule nPoints=2*Nx+1 is accepted",
            abs(assert_refining_sampler(good, "good")["ratio"] - 0.499) < 1e-6)
        must_refuse("history: an incomplete sample sequence must refuse",
                    lambda: centreline_history(mklevel("bad_hist", hist_n=3), 2000))
        must_refuse("history: no postProcessing tree must refuse",
                    lambda: centreline_history(os.path.join(td, "nope"), 2000))

        # ---- E. Roache ------------------------------------------------------
        arm("roache CONVERGING", roache(1.0, 1.2, 1.25)["state"] == "CONVERGING")
        arm("roache OSCILLATORY", roache(1.0, 1.3, 1.1)["state"] == "OSCILLATORY")
        arm("roache DIVERGENT", roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
        arm("roache EXACT", roache(1.0, 1.2, 1.2)["state"] == "EXACT")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    if not ok:
        refuse("SELFTEST FAILED -- the comparator cannot be trusted")
    print("SELFTEST: ALL PASS  (charter §39.5: this proves LOGIC, not INTERFACE -- see "
          "PREREGISTRATION.md §11 and `--paths <run_root>`)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--paths" in sys.argv:
        rr = sys.argv[sys.argv.index("--paths") + 1]
        print("§39.5 PATH CHECK against a real run root: %s" % rr)
        n = check_paths(rr)
        print("MISSING: %d" % n)
        sys.exit(0 if n == 0 else 2)
    if len(sys.argv) < 2:
        sys.stderr.write("usage: grade_vmfl046_r2.py <run_root> | --selftest | --paths <run_root>\n")
        sys.exit(2)
    sys.exit(grade(sys.argv[1]))
