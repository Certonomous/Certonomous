#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_vmfl034_r3.py -- comparator for VMFL034-R3 (constant-kernel aggregation,
CMSMPR box), the FROZEN-FLOW re-scope, graded against the manual's analytical
moment solution (Table .34.1).

SUCCESSOR to VMFL034-R2 (register #59, verdict NOT A RESULT: SIGFPE rc 136 at
t~=0.082 s at ALL three levels, in dragModels::SchillerNaumann::CdRe() computing
Re^0.687 on a non-positive Re -- a LIVE two-phase drag domain error).  The
manual's own setup DECOUPLES the flow from the moments: p.121 states verbatim
"Moments are solved on a frozen flow field", and its journal solves the carrier
(mixture flow + k-epsilon) first, then

    solve set equations mixture flow no ke no mp no      <-- FREEZE the flow
    solve set equations phase-2 moment-0..5 yes          <-- then the moments only

R3 realises exactly that in OpenFOAM: the carrier k-epsilon field is solved once
and FROZEN, and only the alpha-continuity + the constant-kernel population balance
are transported on the frozen field, by a frozen-flow build of
reactingTwoPhaseEulerFoam (solver/reactingTwoPhaseEulerFoamFrozen/, s.SOLVER of
the PREREGISTRATION) whose PIMPLE loop OMITS the pressure-velocity-energy block
(pU/UEqns.H, EEqns.H, pU/pEqn.H).  That block is the ONLY site in the v2606
reactingEuler solver that invokes fluid.Kd()/fluid.momentumTransfer() ->
SchillerNaumann::CdRe(); with it removed, the R2 domain error CANNOT recur --
structurally, not by bounding.

THE GATE AND THE PHYSICS ARE R2's, BYTE-FOR-BYTE (L-487 anti-circularity): the
frozen-flow re-scope is the manual's OWN regime; it changes the SOLVER, not the
band, the targets, the triple, or the aggregation kernel.  The band is the frozen
uniform +-0.76%; the gate conjunction is m1..m5; m0 stays a calibration limb.

Everything R2 got right is retained: the guarded volume->moment conversion with
its PROPER-SUBSET planted-zero control (rule 3, L-487), strict completion + age
guard (rule 4), Roache triple gating at r=2 on 16/32/64 (rule 5), the feed-moment
guard (D3), the measured well-mixedness refusal, and m0 DEMOTED to calibration.

NEW IN R3:
  * physical_range_guard() -- a GATE-BLIND physical-realizability refusal (R6-N4
    style): a valid set of integer moments of a NON-NEGATIVE size distribution
    must be positive and log-convex (Cauchy-Schwarz on adjacent moments,
    m_{k+1}^2 <= m_k*m_{k+2}).  It REFUSES (exit 2) on physically impossible
    moments and references NO manual target, band, or gate quantity.
  * _assert_plant_nondegenerate() -- L-487's "make the defect unrepeatable" guard:
    REFUSE if PLANT_SUBSET is ever the whole reduction (it would cancel to a fixed
    shift and could not fail).

s39.5: every field read is one the FROZEN solver WRITES (proven on the R3
frozen-flow smoke: alpha.air, U.air, p, and f<i>.air.bubbles all written at
endTime).  d_i are NOT read from a field -- they are the frozen sizeGroup
diameters in constant/phaseProperties, asserted here.
"""

import sys, os, re, math, argparse, glob

# ---------------------------------------------------------------------------
# FROZEN CASE CONSTANTS  (must equal constant/phaseProperties; asserted below).
# Byte-identical to VMFL034-R2 -- the frozen-flow re-scope does NOT touch physics.
# ---------------------------------------------------------------------------
KAPPA   = 0.5235987756            # formFactor = pi/6 (spheres)
ALPHA2_INLET = 1.0e-2             # dispersed inlet volume fraction (frozen; Ruling D)
TAU     = 5.0                     # RESCALED residence V/Q [s] (Ruling C; literal 100 s).
M3_TARGET = 1.910                 # manual feed/outlet m3 (volume, conserved)
DMIN, DMAX = 0.45, 22.0           # frozen NOMINAL sectional range (Ruling 4)

# ---------------------------------------------------------------------------
# THE REGISTERED r=2 TRIPLE (unchanged from R2).  Class count N_g / 2N_g / 4N_g.
# RREF is the refinement ratio on CLASS COUNT and is the SINGLE source of the GCI
# exponent base -- asserted against these counts at grade time, never assumed.
# ---------------------------------------------------------------------------
REGISTERED_NGRP = {"coarse": 16, "medium": 32, "fine": 64}   # S1 / S2 / S3
RREF = 2.0                        # = 32/16 = 64/32, asserted in grade_triple()
RREF_TOL = 1e-6

# the base (medium) sectional grid -- 32 groups, geometric [0.45, 22.0].
D_MEDIUM = [
 4.50000000e-01,5.10156194e-01,5.78354095e-01,6.55668720e-01,7.43318798e-01,
 8.42685976e-01,9.55336602e-01,1.08304641e+00,1.22782852e+00,1.39196517e+00,
 1.57804368e+00,1.78899724e+00,2.02815116e+00,2.29927528e+00,2.60664340e+00,
 2.95510061e+00,3.35013974e+00,3.79798787e+00,4.30570453e+00,4.88129297e+00,
 5.53382632e+00,6.27359062e+00,7.11224692e+00,8.06301516e+00,9.14088251e+00,
 1.03628396e+01,1.17481485e+01,1.33186461e+01,1.50990884e+01,1.71175411e+01,
 1.94058214e+01,2.20000000e+01]

# manual Table .34.1 analytical targets (the gate reference)
MANUAL = {0:0.132, 1:0.225, 2:0.547, 3:1.910, 4:9.073, 5:53.797}

# The band is the registration's FROZEN uniform +-0.76% (s4.2/s4.3): tol=q+d.
BAND_REL = 0.0076
CONTENT = {
 0:"CALIBRATION (Ruling B): m0=f(Da) alone; setting beta0_OF for Da=100 SETS m0. Reported vs 0.131774; a miss REFUSES, never a PASS.",
 1:"PRIMARY PREDICTION: sectional resolution (feed-shape dependent, does NOT close for a constant kernel)",
 2:"PRIMARY PREDICTION: sectional resolution (feed-shape dependent, does NOT close for a constant kernel)",
 3:"PRIMARY: VOLUME CONSERVATION in the discretisation (independent of Da; a-priori exact=1.910)",
 4:"PRIMARY PREDICTION: sectional resolution + tail truncation (highest discretisation risk)",
 5:"PRIMARY PREDICTION: sectional resolution + tail truncation (highest discretisation risk)",
}
BANDS = {k:(BAND_REL, CONTENT[k]) for k in range(6)}

# Ruling B: m0 DEMOTED to calibration; GATE conjunction is m1,m2,m3,m4,m5.
GATE_LIMBS = [1, 2, 3, 4, 5]
EXPECT_M0  = 0.131774
CALIB_M0_TOL = 0.03

# well-mixedness MEASURED, comparator REFUSES if not met (CMSMPR premise).
WELLMIXED_COV_MAX   = 0.10
OUTLET_VS_MEAN_TOL  = 0.05

FIELDS_REQUIRED = ["alpha.air", "U.air", "p"]

PLANT = 3.21e-04     # rule-3 plant magnitude (added to a PROPER SUBSET of bins)
PLANT_SUBSET = [8, 9]   # a proper subset of the reduction (all N bins)

# NEW (R3): gate-blind physical-realizability slack for the log-convexity check.
PHYS_LOGCONVEX_TOL = 1e-6   # relative slack on Cauchy-Schwarz m_{k+1}^2 <= m_k*m_{k+2}

# ---------------------------------------------------------------------------
# D3: feed-moment guard constants -- the archive feed and the frozen Wheeler nodes.
# ---------------------------------------------------------------------------
FEED_MOMENTS_ARCHIVE = (1.0, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)
WHEELER_ABSCISSAS = (0.51034075, 1.15677209, 1.85317510)
WHEELER_WEIGHTS   = (0.22888048, 0.62869707, 0.14242245)
FEED_M0_TOL = 1e-6      # m0 normalisation (number)
FEED_M3_TOL = 1e-3      # m3 volume conservation vs archive 1.910 (level-independent)
FEED_SHAPE_TOL = 5e-3   # m1,m2,m4,m5 vs the comparator's own KR expectation at the grid

# ---------------------------------------------------------------------------
# OpenFOAM ascii field parsing
# ---------------------------------------------------------------------------
def _read_text(path):
    with open(path) as fh:
        return fh.read()

def read_internal(path):
    t = _read_text(path)
    m = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", t)
    if m:
        return [float(m.group(1))]
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\d+\s*\((.*?)\)\s*;", t, re.S)
    if m:
        return [float(x) for x in m.group(1).split()]
    raise ValueError("cannot parse internalField in %s" % path)

def read_patch_value(path, patch):
    t = _read_text(path)
    mb = re.search(r"\n    %s\s*\n    \{(.*?)\n    \}" % re.escape(patch), t, re.S)
    if not mb:
        raise ValueError("patch '%s' not found in %s" % (patch, path))
    blk = mb.group(1)
    m = re.search(r"value\s+nonuniform\s+List<scalar>\s*\d+\s*\((.*?)\)\s*;", blk, re.S)
    if m:
        return [float(x) for x in m.group(1).split()]
    m = re.search(r"value\s+uniform\s+([-\d.eE+]+)\s*;", blk)
    if m:
        return [float(m.group(1))]
    raise ValueError("no 'value' in patch '%s' of %s" % (patch, path))

def mean(xs):
    return sum(xs)/len(xs)

def _expect(cond, msg):
    """Explicit assertion that survives `python3 -O` (L-475).  A bare `assert` is
    STRIPPED under -O, which would empty this selftest and disable the production
    guards with no error.  This raise cannot be optimised away."""
    if not cond:
        raise AssertionError(msg)

# ---------------------------------------------------------------------------
# The GUARDED moment conversion  (the single place a silent factor could enter)
# ---------------------------------------------------------------------------
def moments_from_fractions(fvals, alpha2, d, kappa, kmax=5, _mut=None):
    _expect(len(fvals) == len(d), "fraction/grid length mismatch %d vs %d" % (len(fvals), len(d)))
    n = []
    for fi, di in zip(fvals, d):
        if _mut == "no_kappa":
            n.append(alpha2 * fi / (di**3))
        elif _mut == "d2":
            n.append(alpha2 * fi / (kappa * di**2))
        else:
            n.append(alpha2 * fi / (kappa * di**3))
    m = {}
    for k in range(kmax+1):
        if _mut == "mk_shift":
            m[k] = sum(ni * di**(k+1) for ni, di in zip(n, d))
        else:
            m[k] = sum(ni * di**k for ni, di in zip(n, d))
    return m

def normalise(m_out, alpha2_inlet, kappa):
    m3_feed = alpha2_inlet / kappa
    C = M3_TARGET / m3_feed
    return {k: C*v for k, v in m_out.items()}, C

# ---------------------------------------------------------------------------
# rule-3 planted control  (CAN FAIL; PROPER SUBSET of the reduction)
# ---------------------------------------------------------------------------
def _assert_plant_nondegenerate(ngrp):
    """L-487 -- a construction that makes the degenerate defect UNREPEATABLE.  The
    moment reduction sums over ALL ngrp bins, so a plant over the WHOLE set cancels
    to a fixed shift Delta_m = (alpha2/kappa)*P*sum_all d^(k-3) for EVERY input
    (including all zeros) and could not fail.  REFUSE that configuration outright."""
    S = set(PLANT_SUBSET)
    if any(i < 0 or i >= ngrp for i in PLANT_SUBSET):
        sys.stderr.write("PLANT-DESIGN REFUSAL: PLANT_SUBSET %s has an index outside [0,%d) (exit 2)\n"
                         % (PLANT_SUBSET, ngrp))
        raise SystemExit(2)
    if len(S) >= ngrp or S == set(range(ngrp)):
        sys.stderr.write("PLANT-DESIGN REFUSAL (L-487): PLANT_SUBSET spans the whole %d-bin reduction;"
                         " it would cancel to a fixed shift and could not fail (exit 2)\n" % ngrp)
        raise SystemExit(2)
    return True

def planted_control(fvals, alpha2, d, kappa, reader=moments_from_fractions):
    base = reader(fvals, alpha2, d, kappa)
    planted = list(fvals)
    for i in PLANT_SUBSET:
        planted[i] += PLANT
    got = reader(planted, alpha2, d, kappa)
    ok = True; detail = []
    for k in range(6):
        exp = alpha2/kappa * PLANT * sum(d[i]**(k-3) for i in PLANT_SUBSET)
        meas = got[k] - base[k]
        rel = abs(meas-exp)/(abs(exp) if exp else 1.0)
        detail.append((k, exp, meas, rel))
        if rel > 1e-9:
            ok = False
    return ok, detail

# ---------------------------------------------------------------------------
# NEW (R3): GATE-BLIND physical-realizability refusal (R6-N4 style)
# ---------------------------------------------------------------------------
def physical_range_guard(m):
    """REFUSE (exit 2) on physically impossible moments, WITHOUT referencing any
    manual target, band, or gate quantity.  A set of integer moments m_k of a
    NON-NEGATIVE size distribution must be (a) strictly positive, and (b) log-convex
    -- Cauchy-Schwarz on adjacent moments gives m_{k+1}^2 <= m_k*m_{k+2} for any
    positive measure.  A measured moment set that violates either is not the moment
    set of any real particle population and cannot be graded.  This moves NO gate
    quantity: it is a realizability filter on the reading, upstream of the band."""
    fails = []
    for k in range(6):
        if not (m[k] > 0.0):
            fails.append("m%d=%.6g is not positive (a moment of a non-negative measure must be > 0)" % (k, m[k]))
    for k in range(4):
        a, b, c = m[k], m[k+1], m[k+2]
        if a > 0 and b > 0 and c > 0:
            if b*b > a*c*(1.0 + PHYS_LOGCONVEX_TOL):
                fails.append("moment sequence not log-convex at k=%d: m%d^2=%.6g > m%d*m%d=%.6g"
                             " (Cauchy-Schwarz violated; not a valid moment set)"
                             % (k+1, k+1, b*b, k, k+2, a*c))
    if fails:
        sys.stderr.write("PHYSICAL-RANGE REFUSAL (gate-blind; exit 2; moves NO gate quantity):\n  "
                         + "\n  ".join(fails) + "\n")
        raise SystemExit(2)
    return True

# ---------------------------------------------------------------------------
# D3: the FEED-MOMENT GUARD -- reads phaseProperties value_i and REFUSES a feed
# that does not reproduce the archive moments.
# ---------------------------------------------------------------------------
def read_grid_and_values(casedir):
    pp = os.path.join(casedir, "constant", "phaseProperties")
    t = _read_text(pp)
    rows = re.findall(r"f\d+\{d\s+([-\d.eE+]+);\s*value\s+([-\d.eE+]+);", t)
    if not rows:
        raise SystemExit("no sizeGroups (d/value) parsed from %s" % pp)
    d = [float(a) for a, _ in rows]
    v = [float(b) for _, b in rows]
    return d, v

def kr_expected_values(d):
    v = [KAPPA * di**3 for di in d]
    nn = [0.0]*len(d)
    for lj, wj in zip(WHEELER_ABSCISSAS, WHEELER_WEIGHTS):
        vj = KAPPA * lj**3
        if vj <= v[0]:
            nn[0] += wj; continue
        if vj >= v[-1]:
            nn[-1] += wj; continue
        a = 0
        while a+1 < len(v) and v[a+1] <= vj:
            a += 1
        nn[a]   += wj*(v[a+1]-vj)/(v[a+1]-v[a])
        nn[a+1] += wj*(vj-v[a])/(v[a+1]-v[a])
    vol = [ni*KAPPA*di**3 for ni, di in zip(nn, d)]
    s = sum(vol)
    return [x/s for x in vol]

def feed_moments_from_values(d, value):
    n = [vi/(KAPPA*di**3) for vi, di in zip(value, d)]
    s0 = sum(n)
    return [sum(ni*di**k for ni, di in zip(n, d))/s0 for k in range(6)]

def feed_moment_guard(casedir):
    d, value = read_grid_and_values(casedir)
    if abs(sum(value) - 1.0) > 1e-6:
        sys.stderr.write("FEED GUARD REFUSAL: sum(value_i)=%.8f != 1 in %s\n" % (sum(value), casedir))
        raise SystemExit(2)
    m_feed = feed_moments_from_values(d, value)
    m_exp = feed_moments_from_values(d, kr_expected_values(d))
    fails = []
    if abs(m_feed[0] - FEED_MOMENTS_ARCHIVE[0]) > FEED_M0_TOL:
        fails.append("m0=%.6f != archive 1.0 (tol %.0e)" % (m_feed[0], FEED_M0_TOL))
    if abs(m_feed[3] - FEED_MOMENTS_ARCHIVE[3])/FEED_MOMENTS_ARCHIVE[3] > FEED_M3_TOL:
        fails.append("m3=%.6f != archive 1.910 (rel tol %.0e) -- volume NOT conserved by the feed"
                     % (m_feed[3], FEED_M3_TOL))
    for k in (1, 2, 4, 5):
        rel = abs(m_feed[k]-m_exp[k])/abs(m_exp[k])
        if rel > FEED_SHAPE_TOL:
            fails.append("m%d=%.6f != KR-expected %.6f on this grid (rel %.3e > %.0e)"
                         % (k, m_feed[k], m_exp[k], rel, FEED_SHAPE_TOL))
    if fails:
        sys.stderr.write("FEED-MOMENT GUARD REFUSAL (D3; the feed value_i are wrong; exit 2) in %s:\n  %s\n"
                         % (casedir, "\n  ".join(fails)))
        raise SystemExit(2)
    detail = [(k, m_feed[k], FEED_MOMENTS_ARCHIVE[k], m_exp[k]) for k in range(6)]
    return m_feed, detail

# ---------------------------------------------------------------------------
# strict completion (CLAUDE.md rule 4) + age guard
# ---------------------------------------------------------------------------
def latest_time(casedir):
    ts = []
    for d in os.listdir(casedir):
        if re.fullmatch(r"\d+(\.\d+)?([eE][-+]?\d+)?", d) and os.path.isdir(os.path.join(casedir,d)):
            try: ts.append((float(d), d))
            except ValueError: pass
    if not ts: return None
    ts.sort(); return ts[-1][1]

def controldict_endtime(casedir):
    t = _read_text(os.path.join(casedir, "system", "controlDict"))
    m = re.search(r"\bendTime\s+([-\d.eE+]+)\s*;", t)
    return float(m.group(1)) if m else None

def controldict_application(casedir):
    t = _read_text(os.path.join(casedir, "system", "controlDict"))
    m = re.search(r"\bapplication\s+(\S+)\s*;", t)
    return m.group(1) if m else None

def _solver_log(casedir, logpath=None):
    if logpath: return logpath if os.path.exists(logpath) else None
    app = controldict_application(casedir)
    cand = []
    if app: cand.append(os.path.join(casedir, "log." + app))
    cand.append(os.path.join(casedir, "log.solver"))
    for c in cand:
        if os.path.exists(c): return c
    if app:
        for lp in glob.glob(os.path.join(casedir, "log.*")):
            if re.search(r"\b%s\b" % re.escape(app), _read_text(lp)[:4000]):
                return lp
    return None

def strict_completion(casedir, ngrp, logpath=None):
    reasons = []
    slog = _solver_log(casedir, logpath)
    if slog is None:
        reasons.append("no solver log found (log.<application>/log.solver)")
    elif not re.search(r"(?m)^End\s*$", _read_text(slog)):
        reasons.append("no 'End' line in solver log %s" % os.path.basename(slog))
    lt = latest_time(casedir); et = controldict_endtime(casedir)
    if lt is None: reasons.append("no time directories")
    elif et is not None and abs(float(lt)-et) > 1e-9*max(1.0,et):
        reasons.append("last time %s != endTime %s" % (lt, et))
    if lt is not None:
        tdir = os.path.join(casedir, lt)
        for fld in FIELDS_REQUIRED:
            if not os.path.exists(os.path.join(tdir, fld)):
                reasons.append("missing field %s at %s" % (fld, lt))
        for i in range(ngrp):
            fn = "f%d.air.bubbles" % i
            if not os.path.exists(os.path.join(tdir, fn)):
                reasons.append("missing sizeGroup %s at %s" % (fn, lt)); break
    if lt is not None and lt != "0":
        z = os.path.join(casedir, "0", "alpha.air")
        if not os.path.exists(z):
            reasons.append("age guard: no 0/alpha.air to date the launch")
        else:
            t0 = os.path.getmtime(z)
            tdir = os.path.join(casedir, lt)
            for fld in ["alpha.air"] + ["f%d.air.bubbles"%i for i in range(ngrp)]:
                fp = os.path.join(tdir, fld)
                if os.path.exists(fp) and os.path.getmtime(fp) <= t0:
                    reasons.append("age guard: %s not newer than 0/alpha.air" % fld); break
    return (len(reasons)==0), reasons

# ---------------------------------------------------------------------------
# read one case's OUTLET moments (normalised)
# ---------------------------------------------------------------------------
def read_case_moments(casedir, d, ngrp, time=None, patch="outlet"):
    t = time or latest_time(casedir)
    if t is None: raise ValueError("no time dir in %s" % casedir)
    tdir = os.path.join(casedir, t)
    _assert_grid(casedir, d)
    # D3: verify the FROZEN FEED before trusting any outlet number.
    feed_moment_guard(casedir)
    # L-487: the plant design must be non-degenerate for THIS grid before it runs.
    _assert_plant_nondegenerate(ngrp)
    alpha2 = mean(read_patch_value(os.path.join(tdir, "alpha.air"), patch))
    fvals = []
    for i in range(ngrp):
        fvals.append(mean(read_patch_value(os.path.join(tdir, "f%d.air.bubbles"%i), patch)))
    ok, det = planted_control(fvals, alpha2, d, KAPPA)
    if not ok:
        sys.stderr.write("PLANTED CONTROL FAILED on real reader:\n")
        for k,e,mss,r in det: sys.stderr.write("  m%d exp=%.6e meas=%.6e rel=%.2e\n"%(k,e,mss,r))
        raise SystemExit(2)
    wok, cov, ovm, wreasons = wellmixed_check(casedir, d, ngrp, t, patch)
    if not wok:
        sys.stderr.write("WELL-MIXEDNESS REFUSAL (CMSMPR premise fails; exit 2):\n  "
                         + "\n  ".join(wreasons) + "\n"
                         + "  -> NOT A RESULT; the successor changes the RESCALE, not the gate/target\n")
        raise SystemExit(2)
    m_out = moments_from_fractions(fvals, alpha2, d, KAPPA)
    m_norm, C = normalise(m_out, ALPHA2_INLET, KAPPA)
    # NEW (R3): gate-blind physical realizability, upstream of the band.
    physical_range_guard(m_norm)
    m0_rel = (m_norm[0]-EXPECT_M0)/EXPECT_M0
    if abs(m0_rel) > CALIB_M0_TOL:
        sys.stderr.write("m0 CALIBRATION REFUSAL: m0=%.5f vs a-priori %.5f (%.2f%% > %.0f%%);"
                         " indicts the conversion or bin resolution (exit 2)\n"
                         % (m_norm[0], EXPECT_M0, 100*m0_rel, 100*CALIB_M0_TOL))
        raise SystemExit(2)
    return m_norm, alpha2, C, t, dict(cov=cov, outlet_vs_mean=ovm, m0=m_norm[0], m0_rel=m0_rel)

def _assert_grid(casedir, d):
    pp = os.path.join(casedir, "constant", "phaseProperties")
    if not os.path.exists(pp): return
    t = _read_text(pp)
    ds = [float(x) for x in re.findall(r"f\d+\{d\s+([-\d.eE+]+);", t)]
    if len(ds) != len(d):
        raise SystemExit("grid length %d in phaseProperties != comparator %d" % (len(ds), len(d)))
    for a,b in zip(ds, d):
        if abs(a-b) > 1e-6*max(1.0,abs(b)):
            raise SystemExit("grid mismatch phaseProperties vs comparator: %g vs %g" % (a,b))

# ---------------------------------------------------------------------------
# well-mixedness, MEASURED on the internal field (per cell)
# ---------------------------------------------------------------------------
def cell_m0(fvals_by_cell, alpha_by_cell, d, kappa):
    ncell = max(len(alpha_by_cell), max(len(f) for f in fvals_by_cell))
    def cell(x, c): return x[c] if len(x) > 1 else x[0]
    m0 = []
    for c in range(ncell):
        a = cell(alpha_by_cell, c)
        s = 0.0
        for i, fi in enumerate(fvals_by_cell):
            s += a * cell(fi, c) / (kappa * d[i]**3)
        m0.append(s)
    return m0

def wellmixed_check(casedir, d, ngrp, time, patch="outlet"):
    tdir = os.path.join(casedir, time)
    alpha_int = read_internal(os.path.join(tdir, "alpha.air"))
    f_int = [read_internal(os.path.join(tdir, "f%d.air.bubbles"%i)) for i in range(ngrp)]
    m0c = cell_m0(f_int, alpha_int, d, KAPPA)
    n = len(m0c); mu = sum(m0c)/n
    var = sum((x-mu)**2 for x in m0c)/n
    cov = (var**0.5)/mu if mu else float("inf")
    a_out = mean(read_patch_value(os.path.join(tdir,"alpha.air"), patch))
    f_out = [mean(read_patch_value(os.path.join(tdir,"f%d.air.bubbles"%i), patch)) for i in range(ngrp)]
    m0_out = sum(a_out*f_out[i]/(KAPPA*d[i]**3) for i in range(ngrp))
    ovm = abs(m0_out - mu)/mu if mu else float("inf")
    reasons = []
    if cov > WELLMIXED_COV_MAX:
        reasons.append("well-mixedness FAIL: CoV(m0)=%.3f > %.3f" % (cov, WELLMIXED_COV_MAX))
    if ovm > OUTLET_VS_MEAN_TOL:
        reasons.append("well-mixedness FAIL: |outlet-mean - vol-mean|/vol-mean = %.3f > %.3f"
                       % (ovm, OUTLET_VS_MEAN_TOL))
    return (len(reasons)==0), cov, ovm, reasons

# ---------------------------------------------------------------------------
# Roache triple gating (CLAUDE.md rule 5) -- per limb.  rref is a PARAMETER,
# asserted against the registered level list; never a hidden 2.0.
# ---------------------------------------------------------------------------
def roache_triple(coarse, medium, fine, rref=RREF):
    d1 = medium - coarse; d2 = fine - medium
    if d1 == 0 and d2 == 0: return "EXACT", None
    if d1 == 0 or d2 == 0:  return "STAGNANT", None
    if d1*d2 < 0:           return "OSCILLATORY", None
    r = abs(d1)/abs(d2) if d2 != 0 else float("inf")
    if r <= 1.0:            return "DIVERGENT", None
    p = math.log(r)/math.log(rref)
    return "CONVERGING", p

def gci(coarse, medium, fine, Fs=1.25, rref=RREF):
    d2 = fine - medium; d1 = medium - coarse
    if d1 == 0 or d2 == 0: return None
    r = abs(d1)/abs(d2)
    if r <= 1.0: return None
    p = math.log(r)/math.log(rref)
    return Fs*abs(d2/fine)/(rref**p - 1.0)

def assert_ratio(counts):
    c, me, f = counts
    if not (0 < c < me < f):
        raise SystemExit("class counts %s are not strictly increasing -- not a refinement triple" % (counts,))
    r1 = me/c; r2 = f/me
    if abs(r1-RREF) > RREF_TOL or abs(r2-RREF) > RREF_TOL:
        sys.stderr.write("RATIO REFUSAL: class counts %d/%d/%d give ratios %.4f, %.4f != RREF %.1f;"
                         " a single rref and its GCI would be INVALID (exit 2)\n"
                         % (c, me, f, r1, r2, RREF))
        raise SystemExit(2)
    return r1

# ---------------------------------------------------------------------------
def grade_limbs(m_by_grid):
    rows = []
    for k in range(6):
        c = m_by_grid["coarse"][k]; me = m_by_grid["medium"][k]; f = m_by_grid["fine"][k]
        status, p = roache_triple(c, me, f)
        tgt = MANUAL[k]; band, content = BANDS[k]
        val = f
        rel = (val - tgt)/tgt
        gated = (k in GATE_LIMBS)
        if not gated:
            verdict = "CALIBRATION"
            g = gci(c, me, f) if status == "CONVERGING" else None
        elif status != "CONVERGING":
            verdict = "NOT A RESULT"
            g = None
        else:
            g = gci(c, me, f)
            verdict = "PASS" if abs(rel) <= band else "GATE FAIL"
        rows.append(dict(k=k, target=tgt, coarse=c, medium=me, fine=f, rel=rel,
                         band=band, status=status, order=p, gci=g, gated=gated,
                         verdict=verdict, content=content))
    return rows

# ---------------------------------------------------------------------------
def selftest():
    print("=== SELFTEST (VMFL034-R3: plant present/absent limbs + physical-range + feed + ratio) ===")
    passed = 0; total = 0
    def check(name, cond):
        nonlocal passed, total
        total += 1
        ok = bool(cond); passed += 1 if ok else 0
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        _expect(ok, "selftest failed: " + name)

    d = D_MEDIUM; ng = len(d)
    fvals = [0.0]*ng
    for i,v in [(1,0.01587274396),(2,5.506852461e-05),(7,0.2183116101),
                (8,0.2911969412),(11,0.3227629439),(12,0.1518006923)]:
        fvals[i]=v
    a2 = ALPHA2_INLET

    # ---- L-487 plant design: non-degenerate accepted; whole-set REFUSED ----
    print("\n-- L-487 plant-design guard --")
    _assert_plant_nondegenerate(ng)              # proper subset -> no raise
    check("proper-subset plant accepted (non-degenerate)", True)
    caught = False
    try:
        global PLANT_SUBSET
        saved = PLANT_SUBSET; PLANT_SUBSET = list(range(ng))
        _assert_plant_nondegenerate(ng)
    except SystemExit:
        caught = True
    finally:
        PLANT_SUBSET = saved
    check("whole-reduction plant REFUSED (would cancel to a fixed shift)", caught)

    # ---- rule-3 planted control: PRESENT limb passes, ABSENT (blind) limb refuses ----
    print("\n-- rule-3 planted control: plant PRESENT vs plant-ABSENT (blind reader) --")
    ok,_ = planted_control(fvals, a2, d, KAPPA)
    check("plant PRESENT: correct reader SEES the plant (passes)", ok)
    n_absent = 0
    for mut in ("no_kappa","d2","mk_shift"):
        rdr = lambda fv,al,dd,kp,_m=mut: moments_from_fractions(fv,al,dd,kp,_mut=_m)
        okm,_ = planted_control(fvals, a2, d, KAPPA, reader=rdr)
        if not okm: n_absent += 1
    check("plant ABSENT: all 3 blind (mutated) readers REFUSE (%d/3)" % n_absent, n_absent == 3)

    # ---- NEW (R3): gate-blind physical-range guard ----
    print("\n-- physical-range guard (gate-blind realizability) --")
    m_ok = dict(MANUAL)                                  # the manual moments ARE log-convex & positive
    physical_range_guard(m_ok)
    check("valid (positive, log-convex) moment set accepted", True)
    caught = False
    try:
        bad = dict(MANUAL); bad[3] = -1.0                # a negative moment is impossible
        physical_range_guard(bad)
    except SystemExit:
        caught = True
    check("negative moment REFUSED", caught)
    caught = False
    try:
        # break log-convexity: inflate m3 so m3^2 >> m2*m4 (Cauchy-Schwarz violated)
        bad = dict(MANUAL); bad[3] = 100.0
        physical_range_guard(bad)
    except SystemExit:
        caught = True
    check("non-log-convex moment set REFUSED (Cauchy-Schwarz)", caught)

    # ---- D3 feed guard: correct feed passes, mutated feed refuses ----
    print("\n-- D3 feed-moment guard --")
    m_feed = feed_moments_from_values(d, fvals)
    m_exp  = feed_moments_from_values(d, kr_expected_values(d))
    _in_range = (abs(m_feed[0]-1.0)<=FEED_M0_TOL and
                 abs(m_feed[3]-1.91)/1.91<=FEED_M3_TOL and
                 all(abs(m_feed[k]-m_exp[k])/abs(m_exp[k])<=FEED_SHAPE_TOL for k in (1,2,4,5)))
    check("correct feed within guard tolerances", _in_range)
    mut_v = list(fvals); mut_v[8] += 0.05; mut_v[11] -= 0.05
    m_mut = feed_moments_from_values(d, mut_v)
    mut_bad = (abs(m_mut[3]-1.91)/1.91>FEED_M3_TOL or
               any(abs(m_mut[k]-m_exp[k])/abs(m_exp[k])>FEED_SHAPE_TOL for k in (1,2,4,5)))
    check("mutated feed (5% volume shifted 1 bin larger) REFUSED", mut_bad)

    # ---- D2 ratio assert: registered 16/32/64 passes; non-constant refused ----
    print("\n-- D2 refinement-ratio assertion --")
    r = assert_ratio((16,32,64)); check("registered 16/32/64 ratio == 2", abs(r-2.0) < 1e-9)
    caught = False
    try:
        assert_ratio((25,35,50))
    except SystemExit:
        caught = True
    check("non-constant 25/35/50 REFUSED", caught)

    # ---- rule-5 classifier + verdict conjunction ----
    print("\n-- rule-5 classifier + verdict conjunction --")
    for name,tri,exp in [("converging",(9.5,9.2,9.1),"CONVERGING"),
                         ("oscillatory",(9.0,9.2,9.1),"OSCILLATORY"),
                         ("divergent",(9.0,9.2,9.5),"DIVERGENT")]:
        s,_=roache_triple(*tri); check("triple %s -> %s" % (name, exp), s == exp)
    fake = {"coarse":{}, "medium":{}, "fine":{}}
    for k in range(6):
        T = MANUAL[k]
        if k == 4:
            fake["coarse"][k]=T*1.10; fake["medium"][k]=T*1.05; fake["fine"][k]=T*1.03
        else:
            fake["coarse"][k]=T*1.02; fake["medium"][k]=T*1.005; fake["fine"][k]=T*1.001
    rows = grade_limbs(fake)
    gv = [r_["verdict"] for r_ in rows if r_["gated"]]
    overall = "PASS" if all(v=="PASS" for v in gv) else ("NOT A RESULT" if any(v=="NOT A RESULT" for v in gv) else "GATE FAIL")
    check("conjunction: one gated limb out of band -> overall GATE FAIL", overall == "GATE FAIL")

    # ---- well-mixedness reader ----
    print("\n-- well-mixedness reader --")
    nc = 20
    fu = [[fvals[i]]*nc for i in range(ng)]; au=[a2]*nc
    m0u = cell_m0(fu, au, d, KAPPA); mu=sum(m0u)/nc
    covu = (sum((x-mu)**2 for x in m0u)/nc)**0.5/mu
    ag = [a2*(0.5 if c< nc//2 else 1.5) for c in range(nc)]
    m0g = cell_m0(fu, ag, d, KAPPA); mg=sum(m0g)/nc
    covg = (sum((x-mg)**2 for x in m0g)/nc)**0.5/mg
    check("uniform CoV within limit, gradient CoV over limit", covu <= WELLMIXED_COV_MAX and covg > WELLMIXED_COV_MAX)

    print("\nm0 DEMOTED: gate limbs =", GATE_LIMBS, "(m0 is calibration)")
    print("SELFTEST %d/%d" % (passed, total))
    return 0 if passed == total else 1

# ---------------------------------------------------------------------------
def _grid_of(casedir):
    pp = os.path.join(casedir,"constant","phaseProperties")
    ds = [float(x) for x in re.findall(r"f\d+\{d\s+([-\d.eE+]+);", _read_text(pp))]
    if not ds: raise SystemExit("no sizeGroups in %s"%pp)
    return ds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--case", help="single case dir (interface / provisional read)")
    ap.add_argument("--triple", nargs=3, metavar=("COARSE","MEDIUM","FINE"),
                    help="three case dirs -> full Roache-gated per-limb verdict")
    ap.add_argument("--time", default=None)
    ap.add_argument("--patch", default="outlet")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.case:
        dd = _grid_of(args.case); ng = len(dd)
        ok, reasons = strict_completion(args.case, ng)
        if not ok:
            sys.stderr.write("STRICT COMPLETION FAILED (refuse, exit 2):\n  " +
                             "\n  ".join(reasons) + "\n")
            return 2
        mn, a2, C, t, diag = read_case_moments(args.case, dd, ng, time=args.time, patch=args.patch)
        print("case=%s time=%s ngrp=%d alpha2_out=%.6g norm_C=%.6g" % (args.case, t, ng, a2, C))
        print("well-mixed: CoV(m0)=%.4f (<=%.2f) outlet_vs_mean=%.4f (<=%.2f)"
              % (diag["cov"], WELLMIXED_COV_MAX, diag["outlet_vs_mean"], OUTLET_VS_MEAN_TOL))
        print("m0 (CALIBRATION) = %.5f vs a-priori %.5f (%+.2f%%)"
              % (mn[0], EXPECT_M0, 100*diag["m0_rel"]))
        print("PROVISIONAL (single grid -> NO Roache triple -> NOT A RESULT per rule 5):")
        for k in GATE_LIMBS:
            print("  m%d = %.5f   target %.3f   rel %+.3f%%   band +-%.2f%%   [%s]" %
                  (k, mn[k], MANUAL[k], 100*(mn[k]-MANUAL[k])/MANUAL[k], 100*BAND_REL, BANDS[k][1]))
        return 0

    if args.triple:
        mbg = {}
        counts = []
        for name, cdir in zip(("coarse","medium","fine"), args.triple):
            dd = _grid_of(cdir); counts.append(len(dd))
            ok, reasons = strict_completion(cdir, len(dd))
            if not ok:
                sys.stderr.write("STRICT COMPLETION FAILED for %s (refuse, exit 2):\n  %s\n"
                                 % (cdir, "\n  ".join(reasons)))
                return 2
            mn,_,_,_,_ = read_case_moments(cdir, dd, len(dd), time=args.time, patch=args.patch)
            mbg[name] = mn
        r = assert_ratio(tuple(counts))
        reg = sorted(REGISTERED_NGRP.values())
        if sorted(counts) != reg:
            sys.stderr.write("LEVEL REFUSAL: class counts %s != registered triple %s (exit 2)\n"
                             % (counts, reg)); return 2
        rows = grade_limbs(mbg)
        print("VMFL034-R3 per-limb verdict  (FROZEN-FLOW; class counts %s, r=%.3f asserted; m0 DEMOTED):"
              % (counts, r))
        for rr in rows:
            g = ("gci=%.3f%%"%(100*rr["gci"]) if rr["gci"] is not None else "gci=n/a")
            print("  m%d  %-12s  fine=%.5f target=%.3f rel=%+.3f%% band=+-%.2f%% triple=%s %s"
                  % (rr["k"], rr["verdict"], rr["fine"], rr["target"], 100*rr["rel"],
                     100*rr["band"], rr["status"], g))
            print("       tests: %s" % rr["content"])
        gverds = [rr["verdict"] for rr in rows if rr["gated"]]
        if all(v=="PASS" for v in gverds): overall="PASS"
        elif any(v=="NOT A RESULT" for v in gverds): overall="NOT A RESULT (>=1 gated limb)"
        else: overall="GATE FAIL (>=1 gated limb)"
        print("OVERALL (conjunction of the FIVE gated limbs m1,m2,m3,m4,m5; m0 is calibration):", overall)
        return 0

    ap.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
