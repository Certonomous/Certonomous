#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_vmfl034.py  --  comparator for VMFL034 (constant-kernel aggregation,
CMSMPR box), OpenFOAM v2606 reactingTwoPhaseEulerFoam sectional population balance
vs the manual's analytical moment solution (Table .34.1).

DELIVERABLE, NOT YET FROZEN. The bands and the verdict logic below are proposed
to the supervisor; committing this file IS the freeze (SUPERVISION_CHARTER s3
check 4) and is the supervisor's act, not this lane's.

What it does, and the rules it enforces:
  * Converts OpenFOAM per-group VOLUME fractions f_i to number-based diameter
    moments:  n_i = alpha2 * f_i / (kappa * d_i^3);  m_k = sum_i n_i * d_i^k.
    kappa = formFactor = pi/6.  This conversion is GUARDED (CLAUDE.md rule 3 plant).
  * Normalises the outlet moments to the manual's nominal m0_feed=1 normalisation
    by C = m3_target / m3_feed(OF), with m3_feed(OF) = alpha2_inlet/kappa (frozen).
    m3 then TESTS VOLUME CONSERVATION (Ruling 1); it is not forced to 1.910.
  * Strict completion (CLAUDE.md rule 4) with the age guard; REFUSES (exit 2)
    rather than degrade.
  * Roache triple gating (CLAUDE.md rule 5) across a coarse/medium/fine size-group
    triple, per-limb (Ruling 1); a limb whose triple is not CONVERGING is
    NOT A RESULT whatever its value.
  * A rule-3 planted control that CAN FAIL: perturbs a PROPER SUBSET of the bins
    (the reduction is a weighted SUM over all bins, so a subset moves it by a
    computable non-zero amount -- NOT the whole set, which would cancel), and
    checks the measured moment response against the response computed from the
    geometry (d_i, kappa) the comparator itself holds. A mutated reader is REFUSED.

s39.5: every field this comparator reads is one the registered solver WRITES.
  proven on real smoke output 2026-09-04 (see PREREGISTRATION.md s.B):
    - alpha.air                 (volVectorField? no: volScalarField; written AUTO_WRITE)
    - f<i>.air.bubbles          (sizeGroup fields; sizeGroup.C:46-60 AUTO_WRITE)
  d_i are NOT read from a field -- they are the frozen sizeGroup diameters, held
  here and asserted equal to constant/phaseProperties (interface + freeze check).
"""

import sys, os, re, math, argparse, glob

# ---------------------------------------------------------------------------
# FROZEN CASE CONSTANTS  (must equal constant/phaseProperties; asserted below)
# ---------------------------------------------------------------------------
KAPPA   = 0.5235987756            # formFactor = pi/6 (spheres)
ALPHA2_INLET = 1.0e-2             # dispersed inlet volume fraction (frozen; Ruling D)
TAU     = 5.0                     # RESCALED residence V/Q [s] (Ruling C; literal 100 s).
                                  # NOT used in grading: normalisation is by m3_feed and
                                  # the m0 calibration is Da=100 based -- both tau-invariant
                                  # because beta0_OF=2000 compensates (Da=beta0*alpha2*tau=100).
M3_TARGET = 1.910                 # manual feed/outlet m3 (volume, conserved)

# the base (medium) sectional grid -- 35 groups, geometric [0.45, 22.0].
# The coarse/fine grids of the Roache triple are supplied by their own case dirs;
# this list is the MEDIUM grid and is asserted against that case's phaseProperties.
D_MEDIUM = [
 4.50000000e-01,5.04539492e-01,5.65689109e-01,6.34249991e-01,7.11120374e-01,
 7.97307361e-01,8.93940113e-01,1.00228465e+00,1.12376041e+00,1.25995891e+00,
 1.41266451e+00,1.58387785e+00,1.77584206e+00,1.99107211e+00,2.23238780e+00,
 2.50295069e+00,2.80630549e+00,3.14642654e+00,3.52776989e+00,3.95533162e+00,
 4.43471335e+00,4.97219560e+00,5.57482010e+00,6.25048200e+00,7.00803337e+00,
 7.85739911e+00,8.80970701e+00,9.87743356e+00,1.10745674e+01,1.24167924e+01,
 1.39216937e+01,1.56089872e+01,1.75007789e+01,1.96218535e+01,2.20000000e+01]

# manual Table .34.1 analytical targets (the gate reference)
MANUAL = {0:0.132, 1:0.225, 2:0.547, 3:1.910, 4:9.073, 5:53.797}

# The band is the registration's FROZEN uniform +-0.76% (s4.2/s4.3): tol=q+d,
# q=d=0.379% = the reference's honest relative quantisation. The comparator MUST
# match the registration's conjunction, NOT a looser per-limb band -- so BAND is
# uniform here, and only the per-limb CONTENT differs (Ruling 1: six numbers are
# not six equivalent tests). If the supervisor freezes per-limb bands instead,
# change BAND_REL and CONTENT together and re-run --selftest.
BAND_REL = 0.0076   # +-0.76% on every GATED moment (s4.2)
CONTENT = {
 0:"CALIBRATION (Ruling B): m0=f(Da) alone; setting beta0_OF for Da=100 SETS m0, so it is NOT an independent prediction. Reported vs 0.131774; a miss REFUSES, never licenses a PASS.",
 1:"PRIMARY PREDICTION: sectional resolution (feed-shape dependent, does NOT close for a constant kernel)",
 2:"PRIMARY PREDICTION: sectional resolution (feed-shape dependent, does NOT close for a constant kernel)",
 3:"PRIMARY: VOLUME CONSERVATION in the discretisation (independent of Da; a-priori exact=1.910)",
 4:"PRIMARY PREDICTION: sectional resolution + tail truncation (highest discretisation risk)",
 5:"PRIMARY PREDICTION: sectional resolution + tail truncation (highest discretisation risk)",
}
BANDS = {k:(BAND_REL, CONTENT[k]) for k in range(6)}

# Ruling B: m0 is DEMOTED to a calibration/consistency limb. The GATE conjunction
# is m1,m2,m3,m4,m5 only. m0 is reported beside the gate against its a-priori value,
# and a large miss is a REFUSAL trigger (exit 2), never a gate limb.
GATE_LIMBS = [1, 2, 3, 4, 5]
EXPECT_M0  = 0.131774            # a-priori CMSMPR m0 at Da=100 (net-1/2), forward-computed
CALIB_M0_TOL = 0.03             # >3% miss on m0 => REFUSE (indicts conversion/resolution)

# Ruling C condition 3: well-mixedness is MEASURED, not assumed. The reactor must
# remain a CMSMPR after the similarity rescale (s.RESCALE). Registered metric +
# threshold, read BEFORE grading; the comparator REFUSES (exit 2) if not met.
WELLMIXED_COV_MAX   = 0.10      # CoV(m0) over interior cells must be <= this
OUTLET_VS_MEAN_TOL  = 0.05      # |outlet-mean m0 - volume-mean m0| / volume-mean <= this

REQUIRED_FIELDS_THERMAL = None  # n/a here; see FIELDS_REQUIRED
FIELDS_REQUIRED = ["alpha.air", "U.air", "p"]   # + f<i>.air.bubbles checked separately

PLANT = 3.21e-04     # rule-3 plant magnitude (added to a PROPER SUBSET of bins)
PLANT_SUBSET = [8, 9]   # a proper subset of the reduction (all 35 bins)

# ---------------------------------------------------------------------------
# OpenFOAM ascii field parsing
# ---------------------------------------------------------------------------
def _read_text(path):
    with open(path) as fh:
        return fh.read()

def read_internal(path):
    """Return internalField as a list of floats (uniform -> single-value list)."""
    t = _read_text(path)
    m = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", t)
    if m:
        return [float(m.group(1))]
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\d+\s*\((.*?)\)\s*;", t, re.S)
    if m:
        return [float(x) for x in m.group(1).split()]
    raise ValueError("cannot parse internalField in %s" % path)

def read_patch_value(path, patch):
    """Return the boundaryField[patch].value as a list of floats (face values).
    Handles uniform and nonuniform List<scalar>. Raises if absent."""
    t = _read_text(path)
    # isolate the patch block
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

# ---------------------------------------------------------------------------
# The GUARDED moment conversion  (the single place a silent factor could enter)
# ---------------------------------------------------------------------------
def moments_from_fractions(fvals, alpha2, d, kappa, kmax=5, _mut=None):
    """n_i = alpha2 * f_i / (kappa * d_i^3);  m_k = sum_i n_i * d_i^k.
    _mut is used ONLY by --selftest to inject a deliberately WRONG reader that the
    planted control must catch; it is never set in production."""
    assert len(fvals) == len(d), "fraction/grid length mismatch %d vs %d" % (len(fvals), len(d))
    n = []
    for fi, di in zip(fvals, d):
        if _mut == "no_kappa":
            n.append(alpha2 * fi / (di**3))            # forgets kappa
        elif _mut == "d2":
            n.append(alpha2 * fi / (kappa * di**2))    # wrong power in conversion
        else:
            n.append(alpha2 * fi / (kappa * di**3))    # CORRECT
    m = {}
    for k in range(kmax+1):
        if _mut == "mk_shift":
            m[k] = sum(ni * di**(k+1) for ni, di in zip(n, d))  # wrong moment power
        else:
            m[k] = sum(ni * di**k for ni, di in zip(n, d))      # CORRECT
    return m

def normalise(m_out, alpha2_inlet, kappa):
    """C = m3_target / m3_feed(OF); m3_feed(OF) = alpha2_inlet/kappa (frozen feed)."""
    m3_feed = alpha2_inlet / kappa
    C = M3_TARGET / m3_feed
    return {k: C*v for k, v in m_out.items()}, C

# ---------------------------------------------------------------------------
# rule-3 planted control  (CAN FAIL; PROPER SUBSET of the reduction)
# ---------------------------------------------------------------------------
def planted_control(fvals, alpha2, d, kappa, reader=moments_from_fractions):
    """Perturb a PROPER SUBSET of bins by +PLANT, and require the reader's moment
    response to match the response computed from (d, kappa) held here. Returns
    (ok, detail). A reader that mis-converts fails to reproduce the expected
    response and is thus REFUSED by the caller."""
    base = reader(fvals, alpha2, d, kappa)
    planted = list(fvals)
    for i in PLANT_SUBSET:
        planted[i] += PLANT
    got = reader(planted, alpha2, d, kappa)
    # expected delta from the FROZEN geometry the comparator holds:
    #   dm_k = alpha2/kappa * PLANT * sum_{i in S} d_i^(k-3)
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
    """Identify the SOLVER log specifically -- never log.blockMesh/checkMesh, which
    also print 'End' (that loophole passed a broken case before this fix)."""
    if logpath: return logpath if os.path.exists(logpath) else None
    app = controldict_application(casedir)
    cand = []
    if app: cand.append(os.path.join(casedir, "log." + app))   # RunFunctions convention
    cand.append(os.path.join(casedir, "log.solver"))           # this lane's smoke name
    for c in cand:
        if os.path.exists(c): return c
    # last resort: a log.* whose banner names the application (not the mesh utils)
    if app:
        for lp in glob.glob(os.path.join(casedir, "log.*")):
            if re.search(r"\b%s\b" % re.escape(app), _read_text(lp)[:4000]):
                return lp
    return None

def strict_completion(casedir, ngrp, logpath=None):
    """Return (ok, reasons[]). REFUSE (caller exits 2) if not ok."""
    reasons = []
    # 1. a standalone 'End' line at EOF of the SOLVER log (not any log.*)
    slog = _solver_log(casedir, logpath)
    if slog is None:
        reasons.append("no solver log found (log.<application>/log.solver)")
    elif not re.search(r"(?m)^End\s*$", _read_text(slog)):
        reasons.append("no 'End' line in solver log %s" % os.path.basename(slog))
    # 2. last written time == endTime
    lt = latest_time(casedir); et = controldict_endtime(casedir)
    if lt is None: reasons.append("no time directories")
    elif et is not None and abs(float(lt)-et) > 1e-9*max(1.0,et):
        reasons.append("last time %s != endTime %s" % (lt, et))
    # 3. fields present at last time
    if lt is not None:
        tdir = os.path.join(casedir, lt)
        for fld in FIELDS_REQUIRED:
            if not os.path.exists(os.path.join(tdir, fld)):
                reasons.append("missing field %s at %s" % (fld, lt))
        for i in range(ngrp):
            fn = "f%d.air.bubbles" % i
            if not os.path.exists(os.path.join(tdir, fn)):
                reasons.append("missing sizeGroup %s at %s" % (fn, lt)); break
    # 4. AGE GUARD: every field at endTime NEWER than the case's own 0/alpha.air
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
    # assert grid matches phaseProperties (freeze + interface check)
    _assert_grid(casedir, d)
    alpha2 = mean(read_patch_value(os.path.join(tdir, "alpha.air"), patch))
    fvals = []
    for i in range(ngrp):
        fvals.append(mean(read_patch_value(os.path.join(tdir, "f%d.air.bubbles"%i), patch)))
    # GUARD: run the planted control on THIS run's reader before trusting a zero
    ok, det = planted_control(fvals, alpha2, d, KAPPA)
    if not ok:
        sys.stderr.write("PLANTED CONTROL FAILED on real reader:\n")
        for k,e,mss,r in det: sys.stderr.write("  m%d exp=%.6e meas=%.6e rel=%.2e\n"%(k,e,mss,r))
        raise SystemExit(2)
    # Ruling C cond 3: well-mixedness measured BEFORE trusting any moment
    wok, cov, ovm, wreasons = wellmixed_check(casedir, d, ngrp, t, patch)
    if not wok:
        sys.stderr.write("WELL-MIXEDNESS REFUSAL (CMSMPR premise fails; exit 2):\n  "
                         + "\n  ".join(wreasons) + "\n"
                         + "  -> NOT A RESULT; the successor changes the RESCALE, not the gate/target (Ruling C.4)\n")
        raise SystemExit(2)
    m_out = moments_from_fractions(fvals, alpha2, d, KAPPA)
    m_norm, C = normalise(m_out, ALPHA2_INLET, KAPPA)
    # Ruling B: m0 is a calibration/consistency limb; a large miss REFUSES.
    m0_rel = (m_norm[0]-EXPECT_M0)/EXPECT_M0
    if abs(m0_rel) > CALIB_M0_TOL:
        sys.stderr.write("m0 CALIBRATION REFUSAL: m0=%.5f vs a-priori %.5f (%.2f%% > %.0f%%);"
                         " indicts the conversion or bin resolution (exit 2)\n"
                         % (m_norm[0], EXPECT_M0, 100*m0_rel, 100*CALIB_M0_TOL))
        raise SystemExit(2)
    return m_norm, alpha2, C, t, dict(cov=cov, outlet_vs_mean=ovm, m0=m_norm[0], m0_rel=m0_rel)

def _assert_grid(casedir, d):
    pp = os.path.join(casedir, "constant", "phaseProperties")
    if not os.path.exists(pp): return  # skip if not present (synthetic)
    t = _read_text(pp)
    ds = [float(x) for x in re.findall(r"f\d+\{d\s+([-\d.eE+]+);", t)]
    if len(ds) != len(d):
        raise SystemExit("grid length %d in phaseProperties != comparator %d" % (len(ds), len(d)))
    for a,b in zip(ds, d):
        if abs(a-b) > 1e-6*max(1.0,abs(b)):
            raise SystemExit("grid mismatch phaseProperties vs comparator: %g vs %g" % (a,b))

# ---------------------------------------------------------------------------
# Ruling C cond 3: well-mixedness, MEASURED on the internal field (per cell)
# ---------------------------------------------------------------------------
def cell_m0(fvals_by_cell, alpha_by_cell, d, kappa):
    """Per-cell m0 = sum_i alpha_cell*f_i_cell/(kappa*d_i^3). Broadcasts a uniform
    (single-value) field over the cell count of the nonuniform ones."""
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
    """Return (ok, cov, outlet_vs_mean, reasons[]). REFUSE (caller exits 2) if not
    well mixed -- the CMSMPR premise the rescaled target depends on."""
    tdir = os.path.join(casedir, time)
    alpha_int = read_internal(os.path.join(tdir, "alpha.air"))
    f_int = [read_internal(os.path.join(tdir, "f%d.air.bubbles"%i)) for i in range(ngrp)]
    m0c = cell_m0(f_int, alpha_int, d, KAPPA)
    n = len(m0c); mu = sum(m0c)/n
    var = sum((x-mu)**2 for x in m0c)/n
    cov = (var**0.5)/mu if mu else float("inf")
    # outlet-patch mean m0 vs volume(cell) mean m0
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
# Roache triple gating (CLAUDE.md rule 5) -- per limb (Ruling 1)
# ---------------------------------------------------------------------------
def roache_triple(coarse, medium, fine):
    """Classify a monotone/converging triple. Returns (status, order-or-None).
    status in {CONVERGING, DIVERGENT, OSCILLATORY, STAGNANT, EXACT}."""
    d1 = medium - coarse; d2 = fine - medium
    if d1 == 0 and d2 == 0: return "EXACT", None
    if d1 == 0 or d2 == 0:  return "STAGNANT", None
    if d1*d2 < 0:           return "OSCILLATORY", None
    r = abs(d1)/abs(d2) if d2 != 0 else float("inf")
    if r <= 1.0:            return "DIVERGENT", None
    p = math.log(r)/math.log(2.0)   # refinement ratio 2 assumed nominal
    return "CONVERGING", p

def gci(coarse, medium, fine, Fs=1.25, rref=2.0):
    d2 = fine - medium; d1 = medium - coarse
    if d1 == 0 or d2 == 0: return None
    r = abs(d1)/abs(d2)
    if r <= 1.0: return None
    p = math.log(r)/math.log(rref)
    return Fs*abs(d2/fine)/(rref**p - 1.0)

# ---------------------------------------------------------------------------
def grade_limbs(m_by_grid):
    """m_by_grid: dict grid->{k:value}, grids keyed 'coarse','medium','fine'.
    Applies rule-5 gating then the per-limb band. Returns list of rows."""
    rows = []
    for k in range(6):
        c = m_by_grid["coarse"][k]; me = m_by_grid["medium"][k]; f = m_by_grid["fine"][k]
        status, p = roache_triple(c, me, f)
        tgt = MANUAL[k]; band, content = BANDS[k]
        val = f  # finest is the reported value
        rel = (val - tgt)/tgt
        gated = (k in GATE_LIMBS)
        if not gated:
            # Ruling B: m0 is calibration -- never a gate limb, never a PASS/GATE FAIL.
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
    print("=== SELFTEST (logic + planted-control mutation) ===")
    d = D_MEDIUM; ng = len(d)
    # synthetic feed fractions = the frozen feed (6 populated bins)
    fvals = [0.0]*ng
    for i,v in [(1,0.01407919889),(2,0.001848613591),(8,0.3635959616),
                (9,0.1459125896),(12,0.2784678713),(13,0.1960957649)]:
        fvals[i]=v
    a2 = ALPHA2_INLET
    # 1. correct reader passes the planted control
    ok,det = planted_control(fvals, a2, d, KAPPA)
    print("correct reader planted-control:", "OK" if ok else "FAIL(!)")
    assert ok, "correct reader must pass the plant"
    # 2. mutated readers must be REFUSED (plant catches them)
    for mut in ("no_kappa","d2","mk_shift"):
        rdr = lambda fv,al,dd,kp,_m=mut: moments_from_fractions(fv,al,dd,kp,_mut=_m)
        okm,_ = planted_control(fvals, a2, d, KAPPA, reader=rdr)
        print("mutated reader [%-8s] planted-control:" % mut, "REFUSED" if not okm else "PASSED(!! bad)")
        assert not okm, "plant failed to catch mutation %s" % mut
    # 3. feed moments (normalised) reproduce the manual feed shape m0..m5
    m = moments_from_fractions(fvals, a2, d, KAPPA)
    mn,C = normalise(m, a2, KAPPA)
    feed_manual = {0:1.0,1:1.108,2:1.39,3:1.91,4:2.8210001,5:4.4229999}
    print("normalised FEED moments vs archive feed (KR fixed-pivot residual):")
    for k in range(6):
        print("  m%d: %.5f  feed=%.5f  resid=%+.3f%%" % (k, mn[k], feed_manual[k],
              100*(mn[k]-feed_manual[k])/feed_manual[k]))
    # 4. Roache classifier sanity
    for name,tri,exp in [("converging",(9.5,9.2,9.1),"CONVERGING"),
                         ("oscillatory",(9.0,9.2,9.1),"OSCILLATORY"),
                         ("divergent",(9.0,9.2,9.5),"DIVERGENT")]:
        s,_=roache_triple(*tri); print("  triple %-11s -> %s" % (name,s)); assert s==exp
    # 5. well-mixedness reader logic (Ruling C cond 3)
    #    uniform cells -> CoV 0 (well mixed); a strong gradient -> large CoV
    nc = 20
    fu = [[fvals[i]]*nc for i in range(ng)]; au=[a2]*nc
    m0u = cell_m0(fu, au, d, KAPPA); mu=sum(m0u)/nc
    covu = (sum((x-mu)**2 for x in m0u)/nc)**0.5/mu
    ag = [a2*(0.5 if c< nc//2 else 1.5) for c in range(nc)]   # +-50% gradient in alpha
    m0g = cell_m0(fu, ag, d, KAPPA); mg=sum(m0g)/nc
    covg = (sum((x-mg)**2 for x in m0g)/nc)**0.5/mg
    print("well-mixed reader: uniform CoV=%.3f (<= %.2f OK)  gradient CoV=%.3f (> %.2f REFUSE)"
          % (covu, WELLMIXED_COV_MAX, covg, WELLMIXED_COV_MAX))
    assert covu <= WELLMIXED_COV_MAX and covg > WELLMIXED_COV_MAX, "well-mixed reader logic wrong"
    print("m0 DEMOTED: gate limbs =", GATE_LIMBS, "(m0 is calibration, Ruling B)")
    print("SELFTEST PASSED")
    return 0

# ---------------------------------------------------------------------------
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
        d = D_MEDIUM; ng = len(d)
        ok, reasons = strict_completion(args.case, ng)
        if not ok:
            sys.stderr.write("STRICT COMPLETION FAILED (refuse, exit 2):\n  " +
                             "\n  ".join(reasons) + "\n")
            return 2
        mn, a2, C, t, diag = read_case_moments(args.case, d, ng, time=args.time, patch=args.patch)
        print("case=%s time=%s alpha2_out=%.6g norm_C=%.6g" % (args.case, t, a2, C))
        print("well-mixed: CoV(m0)=%.4f (<=%.2f) outlet_vs_mean=%.4f (<=%.2f)"
              % (diag["cov"], WELLMIXED_COV_MAX, diag["outlet_vs_mean"], OUTLET_VS_MEAN_TOL))
        print("m0 (CALIBRATION, Ruling B) = %.5f vs a-priori %.5f (%+.2f%%)"
              % (mn[0], EXPECT_M0, 100*diag["m0_rel"]))
        print("PROVISIONAL (single grid -> NO Roache triple -> NOT A RESULT per rule 5):")
        for k in GATE_LIMBS:
            print("  m%d = %.5f   target %.3f   rel %+.3f%%   band +-%.2f%%   [%s]" %
                  (k, mn[k], MANUAL[k], 100*(mn[k]-MANUAL[k])/MANUAL[k], 100*BAND_REL, BANDS[k][1]))
        return 0

    if args.triple:
        d = D_MEDIUM
        mbg = {}
        for name, cdir in zip(("coarse","medium","fine"), args.triple):
            # each grid has its OWN d list; medium asserted, coarse/fine read from their pp
            dd = _grid_of(cdir)
            ok, reasons = strict_completion(cdir, len(dd))
            if not ok:
                sys.stderr.write("STRICT COMPLETION FAILED for %s (refuse, exit 2):\n  %s\n"
                                 % (cdir, "\n  ".join(reasons)))
                return 2
            mn,_,_,_,_ = read_case_moments(cdir, dd, len(dd), time=args.time, patch=args.patch)
            mbg[name] = mn
        rows = grade_limbs(mbg)
        print("VMFL034 per-limb verdict (Roache-gated; m0 DEMOTED to calibration, Ruling B):")
        for r in rows:
            g = ("gci=%.3f%%"%(100*r["gci"]) if r["gci"] is not None else "gci=n/a")
            print("  m%d  %-12s  fine=%.5f target=%.3f rel=%+.3f%% band=+-%.2f%% triple=%s %s"
                  % (r["k"], r["verdict"], r["fine"], r["target"], 100*r["rel"],
                     100*r["band"], r["status"], g))
            print("       tests: %s" % r["content"])
        # overall = conjunction of the GATED limbs (m1,m2,m3,m4,m5); m0 excluded (Ruling B)
        gverds = [r["verdict"] for r in rows if r["gated"]]
        if all(v=="PASS" for v in gverds): overall="PASS"
        elif any(v=="NOT A RESULT" for v in gverds): overall="NOT A RESULT (>=1 gated limb)"
        else: overall="GATE FAIL (>=1 gated limb)"
        print("OVERALL (conjunction of the FIVE gated limbs m1,m2,m3,m4,m5; m0 is calibration):", overall)
        return 0

    ap.print_help()
    return 1

def _grid_of(casedir):
    pp = os.path.join(casedir,"constant","phaseProperties")
    ds = [float(x) for x in re.findall(r"f\d+\{d\s+([-\d.eE+]+);", _read_text(pp))]
    if not ds: raise SystemExit("no sizeGroups in %s"%pp)
    return ds

if __name__ == "__main__":
    sys.exit(main())
