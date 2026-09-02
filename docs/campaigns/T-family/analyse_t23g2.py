#!/usr/bin/env python3
"""T23G2 COMPARATOR.  Grades the rebuilt, similarity-repaired, wall-resolved
three-level ladder against the gates frozen in
``docs/campaigns/T-family/T23G2_PREREGISTRATION.md`` v1.2 (v1.0 + AMENDMENT A1 +
AMENDMENT A2).

IT LAUNCHES NOTHING.  It reads artifacts and refuses.

DEFAULT DENY, EVERYWHERE.  A missing artifact, an unparsable one, a control that
cannot be constructed, or any non-PASS is a REFUSAL (exit 2) -- never a softer
number and never a silently skipped gate.  An unevaluated gate is NOT a passed
one (VERIFICATION_CHARTER.md section 9).

WHAT THIS FILE DOES NOT REIMPLEMENT, ON PURPOSE:
  * rule 5 gating, the observed order, the GCI and the planted-zero contract all
    come from ``scripts/roache_triple.py``.  ``PLANT``, ``FS`` and the state
    names are IMPORTED and never redefined (CLAUDE.md rule 14 -- a lesson is not
    applied until every call site asserts it).
  * rule 4 completion is DELEGATED to ``mark_done_t23.py`` as a subprocess.  No
    completion logic lives here.

THE ONE THING THIS COMPARATOR MUST NOT DO, AND THE REASON:
  ** GRADE THE FINE VALUE, NEVER THE RICHARDSON EXTRAPOLATE. **
  The extrapolate sign inversion is a known live defect in this family's
  comparators, survivable only because it is display-only everywhere it lives.
  This file was written AFTER that defect was known, so gating on the
  extrapolate here would make a display-only defect load-bearing.  The
  extrapolate is REPORTED beside the fine value and is never a gate input.
"""
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
RUNS = os.path.join(REPO, "verification/runs/T-family/T23G2_runs")
T23_RUNS = os.path.join(REPO, "verification/runs/T-family/T23_runs")

sys.path.insert(0, os.path.join(REPO, "scripts"))
import roache_triple as RT                                    # noqa: E402
from roache_triple import PLANT, FS, refuse                    # noqa: E402

sys.path.insert(0, HERE)
import t23g_readonly_diagnosis as GEOM                         # noqa: E402

# --------------------------------------------------------------------------
# THE REGISTRATION, TRANSCRIBED.  Every number below is quoted from the frozen
# file; none is chosen here.  Section references are to T23G2_PREREGISTRATION.md.
# --------------------------------------------------------------------------
LEVELS = ("T23G2_L1", "T23G2_L2", "T23G2_L3")
ENDTIME = {"T23G2_L1": 6000, "T23G2_L2": 12000, "T23G2_L3": 24000}   # A1.6
CELLS = {"T23G2_L1": 40320, "T23G2_L2": 90720, "T23G2_L3": 204120}   # 2.1
DIM = 2                       # 5 deg wedge, one cell circumferentially; 2.1
R_REFINE = 1.5                # 2.25x cells per step at dim = 2

T_REF = 288.0                 # triples are graded on dT = T - 288.0 K; 3

# G-ORDER, as amended by A1.2.  [0.5, 1.5] and NOT [1.5, 2.5], because the
# formal order of the energy equation's convection term is ONE:
#   T23G_F/system/fluid/fvSchemes line 33 -- `div(phi,h) bounded Gauss upwind`
# Sanaa's section 0 point 3 is scheme-relative ("p within 0.5 of the scheme's
# formal order"); [0.5, 1.5] IS her rule applied, not a relaxation of it (A2.3).
ORDER_BAND = (0.5, 1.5)
ORDER_QUANTITY = "Q4"         # core volume-averaged T; section 3

# G-BAND, as amended by A1.2: tightened from [45, 60] once the scheme stopped
# changing.  Applied to the FINE value of Q1, on dT.
BAND_Q1 = (46.0, 56.0)

# G-CONV, section 5.3.  `h` carries Sanaa's tightened 1e-9; the rest 1e-8.
RESID_TOL = {"h": 1.0e-9, "Uy": 1.0e-8, "Uz": 1.0e-8,
             "p_rgh": 1.0e-8, "k": 1.0e-8, "omega": 1.0e-8}
UX_EXCLUSION_MAX = 1.0e-12    # measured per level, never assumed

# G-PLATEAU, section 5.3 as amended: EVERY graded quantity, not only the maxima.
PLATEAU_WINDOW_ITERS = 2000
PLATEAU_MAX_SPREAD_K = 0.005          # Sanaa's tightened stationarity
PLATEAU_MAX_SPREAD_REL = 0.001        # 0.1 % for Q5, which is in W

# G-RATIO, section 5.3: Sanaa's section 0 point 2, promoted to a gate.
RATIO_MIN = 10.0

# G-YPLUS, as amended by A2.2: GATED on EVERY wall patch, EVERY level.
YPLUS_MAX = 1.0
YPLUS_INSTRUMENT_AGREE_REL = 0.02     # 2 %; disagreement REFUSES, never averages

# G-MESHSIM, section 5.5 as amended by A2.4.
MESHSIM_CELL_RATIO = 2.25
MESHSIM_CELL_TOL = 1e-9
MESHSIM_D1_RATIO = 1.5
MESHSIM_D1_TOL = 0.005                # 1.500 +/- 0.005
MESHSIM_MIN_HOUSING_CELLS = 8         # at the COARSEST level; T23G carried 4

NU = 1.8e-05 / 1.2            # fluid kinematic viscosity, m2/s (mu/rho, const)

# --------------------------------------------------------------------------
# AMENDMENT v1.1, 2026-09-02 -- REPAIR R2 (T23G2_PREREGISTRATION.md:671).
#
# GRANTED AND WIDENED: VERIFICATION_CHARTER.md v1.38 section 2d.7, commit
# 3dad5bae.  The registration at :671 says this comparator will "record its own
# grading-path shas on the artifact's face"; it recorded none -- a REGISTERED
# FEATURE NEVER BUILT (section 2d.4.3), not a departure from a registered path.
#
# FIVE FILES, NOT THE FOUR PETITIONED.  The ruling refused the petitioned scope:
# `t23g_readonly_diagnosis` is imported at :46 and used in `yplus_from_fields`,
# `_first_cell_heights`, `gate_meshsim` and `_u_maxima`, so it is on the grading
# path for G-YPLUS, G-MESHSIM and G-CONV, and it was in neither the freeze table
# nor the petition's list.  A sha recorder that leaves a grading-path member
# silent is the defect it was built to cure.
#
# THE DUAL-SHA CONDITION (section 2d.4.3) IS WHY TWO COLUMNS ARE PRINTED AND NOT
# ONE.  The recorder records this file's sha -- and ADDING the recorder CHANGES
# that sha.  The registration contemplated provenance present from the FIRST
# GRADED SOLVE; what this repair can deliver is provenance FROM THE REPAIR
# FORWARD, carrying a POST-REPAIR sha that is NOT the blob frozen at
# pre-registration.  The registered intent is UNRECOVERABLE and this recorder
# does not claim to restore it.
GRADING_PATH_FREEZE_COMMIT = "976776f4"   # the commit that froze the comparator
GRADING_PATH = (
    "docs/campaigns/T-family/T23G2_PREREGISTRATION.md",
    "docs/campaigns/T-family/analyse_t23g2.py",
    "docs/campaigns/T-family/t23g_readonly_diagnosis.py",
    "verification/runs/T-family/T23_runs/mark_done_t23.py",
    "scripts/roache_triple.py",
)


def note(msg):
    print(msg)


def _need(path, what):
    if not os.path.isfile(path):
        refuse("%s: %s is not on disk; the gate it feeds CANNOT be evaluated "
               "and an unevaluated gate is not a passed one" % (what, path))
    return path


def case_dir(level):
    d = os.path.join(RUNS, level)
    if not os.path.isdir(d):
        refuse("case directory %s does not exist; T23G2 has not been run" % d)
    return d


# ==========================================================================
# RULE 4 -- DELEGATED, CALLED, NEVER REIMPLEMENTED
# ==========================================================================
def require_done():
    """`mark_done_t23.py` as a subprocess.  T23G2's endTime is a LEVEL VARIABLE
    (A1.6), unlike T23G's invariant 10000, so each level is checked against its
    own registered endTime and the value is passed explicitly rather than left
    to a default that would silently check the wrong time."""
    md = os.path.join(T23_RUNS, "mark_done_t23.py")
    if not os.path.isfile(md):
        refuse("the completion instrument %s is not on disk; rule 4 cannot be "
               "evaluated and this file will NOT reimplement it" % md)
    note("COMPLETION -- rule 4, DELEGATED to %s and CALLED\n"
         % os.path.relpath(md, REPO))
    # endTime is NOT passed: that instrument reads it from each case's own
    # system/controlDict (mark_done_t23.py:160), so T23G2's per-level endTime
    # (A1.6) is handled correctly without this file telling it what to expect.
    # A comparator that ASSERTED the endTime it wanted would be marking its own
    # homework.
    bad = []
    for lv in LEVELS:
        r = subprocess.run([sys.executable, md, "--root", RUNS, lv],
                           capture_output=True, text=True)
        for line in (r.stdout or "").rstrip().split("\n"):
            if line.strip():
                note("  | " + line)
        if r.returncode != 0:
            bad.append((lv, r.returncode, (r.stderr or "").strip()[:300]))
    if bad:
        refuse("rule 4 completion FAILED for %s; a run that fails any clause is "
               "not done, and this comparator will not grade it"
               % ", ".join("%s (rc=%d) %s" % b for b in bad))
    note("")


# ==========================================================================
# SERIES READERS -- the function-object output the build script writes
# ==========================================================================
def _read_dat(path, want_field=None, value_col=-1):
    """A tab-separated OpenFOAM functionObject .dat.  Returns [(iter, value)].
    REFUSES on an unparsable file rather than returning an empty series that
    would read downstream as 'no movement'."""
    out = []
    for line in open(path, errors="replace"):
        if line.startswith("#"):
            continue
        f = [c.strip() for c in line.split("\t") if c.strip()]
        if len(f) < 2:
            continue
        if want_field is not None:
            if len(f) < 5 or f[1] != want_field:
                continue
            out.append((float(f[0]), float(f[4])))
        else:
            try:
                out.append((float(f[0]), float(f[value_col])))
            except ValueError:
                continue
    if not out:
        refuse("%s parsed to an EMPTY series; an empty series is not a "
               "stationary one" % path)
    return out


def series_minmax(cd, region):
    p = _need(os.path.join(cd, "postProcessing", region, "%s_T" % region,
                           "0", "fieldMinMax.dat"), "fieldMinMax(%s)" % region)
    return _read_dat(p, want_field="T")


def series_volavg(cd, region):
    nm = "core_volavg_T" if region == "core" else "housing_volavg_T"
    p = _need(os.path.join(cd, "postProcessing", region, nm, "0",
                           "volFieldValue.dat"), nm)
    return _read_dat(p)


def series_patch_T(cd):
    p = _need(os.path.join(cd, "postProcessing", "housing", "housing_patch_T",
                           "0", "surfaceFieldValue.dat"), "housing_patch_T")
    return _read_dat(p)


def series_wall_heat(cd):
    p = _need(os.path.join(cd, "postProcessing", "housing", "housing_wall_heat",
                           "0", "surfaceFieldValue.dat"), "housing_wall_heat")
    return _read_dat(p)


# ==========================================================================
# G-PLATEAU and G-RATIO -- section 5.3, on EVERY graded quantity
# ==========================================================================
def plateau(series, endtime, rel=False):
    """Peak-to-peak over the last PLATEAU_WINDOW_ITERS iterations.  Selection is
    by ITERATION SPAN, never by sample count, because Q1/Q3 sample every 100 and
    the T23G2 additions sample every 200 (build script comment)."""
    tail = [v for (it, v) in series if it >= endtime - PLATEAU_WINDOW_ITERS]
    if len(tail) < 3:
        refuse("only %d samples in the last %d iterations; G-PLATEAU needs at "
               "least 3 and an unevaluated gate is not a passed one"
               % (len(tail), PLATEAU_WINDOW_ITERS))
    spread = max(tail) - min(tail)
    last = series[-1][1]
    lim = (abs(last) * PLATEAU_MAX_SPREAD_REL) if rel else PLATEAU_MAX_SPREAD_K
    return ("PLATEAUED" if spread <= lim else "NOT PLATEAUED"), spread, lim, len(tail)


def g_ratio(name, iter_change, level_diffs):
    """Sanaa's section 0 point 2, gated: the iterative change on the finest level
    must be at least 10x smaller than the SMALLEST consecutive inter-level
    difference.  Otherwise the observed order is noise, not discretisation."""
    smallest = min(abs(d) for d in level_diffs)
    if iter_change <= 0.0:
        # an exact zero passes, and the planted-zero control is what makes an
        # exact zero mean something (rule 3).  Reported, not silently blessed.
        return "PASS", float("inf"), smallest
    ratio = smallest / iter_change
    return ("PASS" if ratio >= RATIO_MIN else "GATE FAIL"), ratio, smallest


# ==========================================================================
# G-YPLUS -- A2.2: GATED on EVERY wall patch, EVERY level, two instruments
# ==========================================================================
def yplus_from_fields(cd):
    """Independent y+ from U, nut and the polyMesh.  The wall condition is
    `nutLowReWallFunction`, so nut_w = 0 and u_tau = sqrt(nu * U_t / y).  This
    reader's ability to see what it claims is established in
    T23G2_PREREGISTRATION.md A1.4: on T23G_M it reproduced T23_RESULTS.md
    section 4's OpenFOAM-produced values to every digit that record carries."""
    mf = GEOM.Mesh(cd, "fluid")
    et = None
    for lv, t in ENDTIME.items():
        if os.path.basename(cd) == lv:
            et = str(t)
    if et is None:
        refuse("cannot resolve endTime for %s" % cd)
    Ui, Ub = GEOM.read_field(_need(os.path.join(cd, et, "fluid", "U"), "U"))
    nuti, nutb = GEOM.read_field(_need(os.path.join(cd, et, "fluid", "nut"), "nut"))
    Uc = GEOM.expand(Ui, mf.nCells)
    nutc = GEOM.expand(nuti, mf.nCells)
    out = {}
    for pn, pb in mf.boundary.items():
        if pb["type"] not in ("wall", "mappedWall"):
            continue
        nf, sf = pb["nFaces"], pb["startFace"]
        if Ub[pn][0] == "no-value" and "noSlip" in str(Ub[pn][1]):
            Uw = [(0.0, 0.0, 0.0)] * nf
        else:
            Uw = GEOM.expand(Ub[pn], nf)
        nutw = GEOM.expand(nutb[pn], nf)
        vals = []
        for i in range(nf):
            fi = sf + i
            c = mf.owner[fi]
            fa = mf.fa[fi]
            A = math.sqrt(sum(x * x for x in fa))
            nh = tuple(x / A for x in fa)
            dv = tuple(mf.fc[fi][k] - mf.C[c][k] for k in range(3))
            y = abs(sum(dv[k] * nh[k] for k in range(3)))
            rel = tuple(Uc[c][k] - Uw[i][k] for k in range(3))
            dot = sum(rel[k] * nh[k] for k in range(3))
            tang = tuple(rel[k] - dot * nh[k] for k in range(3))
            Ut = math.sqrt(sum(x * x for x in tang))
            utau = math.sqrt(max((NU + nutw[i]) * Ut / y, 0.0))
            vals.append(y * utau / NU)
        out[pn] = dict(min=min(vals), max=max(vals),
                       avg=sum(vals) / len(vals), n=len(vals))
    if not out:
        refuse("%s: no wall patches found; y+ CANNOT be evaluated" % cd)
    return out


def yplus_from_log(cd):
    """The PRIMARY instrument: `chtMultiRegionSimpleFoam -postProcess -func
    yPlus`, whose log is filed as log.yPlus.fluid.  Plain `postProcess` is
    MEASURED BLIND on this family -- it does not construct the compressible
    turbulence model -- so a log whose own text says so, or whose numbers are
    perfect zeros, is REFUSED and never read (CLAUDE.md rule 3)."""
    p = os.path.join(cd, "log.yPlus.fluid")
    if not os.path.isfile(p):
        return None
    txt = open(p, errors="replace").read()
    if "Unable to find turbulence model" in txt:
        return "BLIND"
    out = {}
    for m in re.finditer(r"patch\s+(\S+)\s+y\+\s*:\s*min\s*=\s*([-\d.eE+]+)"
                         r"\s*,?\s*max\s*=\s*([-\d.eE+]+)\s*,?\s*average\s*=\s*"
                         r"([-\d.eE+]+)", txt):
        out[m.group(1)] = dict(min=float(m.group(2)), max=float(m.group(3)),
                               avg=float(m.group(4)))
    if not out:
        return None
    if all(v["max"] == 0.0 and v["min"] == 0.0 for v in out.values()):
        refuse("%s reports y+ = 0 on every patch.  A perfect zero from a reader "
               "not shown able to see a non-zero is REFUSED, not read "
               "(CLAUDE.md rule 3)." % p)
    return out


def gate_yplus():
    note("G-YPLUS -- A2.2: GATED on EVERY wall patch, EVERY level (max <= %.1f)"
         % YPLUS_MAX)
    rows, verdict = {}, "PASS"
    for lv in LEVELS:
        cd = case_dir(lv)
        field = yplus_from_fields(cd)
        log = yplus_from_log(cd)
        if isinstance(log, dict):
            for pn, d in log.items():
                if pn in field:
                    a, b = d["max"], field[pn]["max"]
                    if abs(a - b) > YPLUS_INSTRUMENT_AGREE_REL * max(abs(a), abs(b), 1e-30):
                        refuse("y+ instruments DISAGREE on %s/%s: log %.6g vs "
                               "field %.6g (> %.0f%%).  A disagreement is a "
                               "REFUSAL, never an average."
                               % (lv, pn, a, b, 100 * YPLUS_INSTRUMENT_AGREE_REL))
            note("  %s: primary instrument PRESENT and agrees with the "
                 "independent reader to within %.0f%%" % (lv, 100 * YPLUS_INSTRUMENT_AGREE_REL))
        elif log == "BLIND":
            note("  %s: primary instrument BLIND (its own log says the "
                 "turbulence model was not in the database); the independent "
                 "reader carries the gate, and its validation is A1.4" % lv)
        else:
            note("  %s: primary instrument ABSENT; the independent reader "
                 "carries the gate, and its validation is A1.4" % lv)
        rows[lv] = field
        for pn in sorted(field):
            d = field[pn]
            ok = d["max"] <= YPLUS_MAX
            if not ok:
                verdict = "GATE FAIL"
            note("    %-18s n=%4d  min %7.4f  avg %7.4f  max %7.4f   %s"
                 % (pn, d["n"], d["min"], d["avg"], d["max"],
                    "PASS" if ok else "GATE FAIL"))
    note("  G-YPLUS: %s\n" % verdict)
    return verdict, rows


# ==========================================================================
# G-MESHSIM -- section 5.5, measured from the BUILT mesh
# ==========================================================================
def gate_meshsim():
    note("G-MESHSIM -- section 5.5 / A2.4, measured from the BUILT polyMesh")
    verdict = "PASS"
    cells = {}
    for lv in LEVELS:
        cd = case_dir(lv)
        cells[lv] = {r: GEOM.Mesh(cd, r).nCells for r in ("fluid", "housing", "core")}
        tot = sum(cells[lv].values())
        if tot != CELLS[lv]:
            refuse("%s has %d cells; the registration says %d.  The mesh that "
                   "ran is not the mesh that was registered."
                   % (lv, tot, CELLS[lv]))
    for a, b in zip(LEVELS, LEVELS[1:]):
        for r in ("fluid", "housing", "core"):
            ratio = cells[b][r] / cells[a][r]
            ok = abs(ratio - MESHSIM_CELL_RATIO) <= MESHSIM_CELL_TOL
            if not ok:
                verdict = "GATE FAIL"
            note("  cells %-8s %s/%s = %.9f  %s"
                 % (r, b, a, ratio, "PASS" if ok else "GATE FAIL"))
    d1 = {lv: _first_cell_heights(case_dir(lv)) for lv in LEVELS}
    for a, b in zip(LEVELS, LEVELS[1:]):
        for pn in sorted(d1[a]):
            ratio = d1[a][pn] / d1[b][pn]
            ok = abs(ratio - MESHSIM_D1_RATIO) <= MESHSIM_D1_TOL
            if not ok:
                verdict = "GATE FAIL"
            note("  first cell %-18s %s/%s = %.6f  %s"
                 % (pn, a, b, ratio, "PASS" if ok else "GATE FAIL"))
    hc = cells[LEVELS[0]]["housing"]
    nz_mid = 140
    across = hc // nz_mid
    ok = across >= MESHSIM_MIN_HOUSING_CELLS
    if not ok:
        verdict = "GATE FAIL"
    note("  cells across the housing wall at the COARSEST level: %d (floor %d; "
         "T23G carried 4)  %s" % (across, MESHSIM_MIN_HOUSING_CELLS,
                                  "PASS" if ok else "GATE FAIL"))
    note("  G-MESHSIM: %s\n" % verdict)
    return verdict


def _first_cell_heights(cd):
    mf = GEOM.Mesh(cd, "fluid")
    out = {}
    for pn, pb in mf.boundary.items():
        if pb["type"] not in ("wall", "mappedWall"):
            continue
        nf, sf = pb["nFaces"], pb["startFace"]
        ds = []
        for i in range(nf):
            fi = sf + i
            c = mf.owner[fi]
            fa = mf.fa[fi]
            A = math.sqrt(sum(x * x for x in fa))
            nh = tuple(x / A for x in fa)
            dv = tuple(mf.fc[fi][k] - mf.C[c][k] for k in range(3))
            ds.append(abs(sum(dv[k] * nh[k] for k in range(3))))
        out[pn] = sum(ds) / len(ds)
    return out


# ==========================================================================
# G-CONV -- section 5.3
# ==========================================================================
def gate_conv():
    note("G-CONV -- section 5.3; h <= 1e-9 (Sanaa's tightened criterion), "
         "others <= 1e-8")
    verdict, states = "PASS", {}
    for lv in LEVELS:
        cd = case_dir(lv)
        res = _final_residuals(cd, ENDTIME[lv])
        bad = {k: res[k] for k, tol in RESID_TOL.items()
               if k not in res or res[k] > tol}
        mx = _u_maxima(cd, ENDTIME[lv])
        ratio = (mx[0] / mx[2]) if mx[2] > 0 else float("inf")
        if ratio > UX_EXCLUSION_MAX:
            refuse("%s: Ux is excluded from G-CONV BY MEASUREMENT, and the "
                   "measurement does not support it here: max|Ux|/max|Uz| = "
                   "%.3e > %.0e.  The exclusion is re-measured per level and "
                   "never assumed." % (lv, ratio, UX_EXCLUSION_MAX))
        states[lv] = "CONVERGED" if not bad else "NOT CONVERGED"
        if bad:
            verdict = "GATE FAIL"
        note("  %-11s %-14s worst asserted: %s   (Ux excluded, "
             "max|Ux|/max|Uz| = %.3e)"
             % (lv, states[lv],
                ", ".join("%s %.3e" % (k, v) for k, v in sorted(bad.items()))
                or "all within tolerance", ratio))
    note("  G-CONV: %s\n" % verdict)
    return verdict, states


def _final_residuals(cd, endtime):
    p = _need(os.path.join(cd, "log.solve"), "log.solve")
    txt = open(p, errors="replace").read()
    out = {}
    for f in ("Ux", "Uy", "Uz", "h", "p_rgh", "k", "omega"):
        ms = re.findall(r"Solving for %s, Initial residual = ([\d.eE+-]+)"
                        % re.escape(f), txt)
        if ms:
            out[f] = float(ms[-1])
    if "h" not in out:
        refuse("%s: no `h` residual in log.solve; G-CONV cannot be evaluated"
               % cd)
    return out


def _u_maxima(cd, endtime):
    p = _need(os.path.join(cd, str(endtime), "fluid", "U"), "U at endTime")
    i, _ = GEOM.read_field(p)
    kind, data = i
    if kind != "nonuniform":
        refuse("%s: U internalField is %r, not a nonuniform list" % (p, kind))
    return [max(abs(v[k]) for v in data) for k in range(3)]


# ==========================================================================
# THE QUANTITIES
# ==========================================================================
def read_quantities():
    """Every quantity is read from its function-object SERIES, whose last sample
    is the endTime value.  That gives the graded value and the plateau series
    from one artifact, which is what T23G could not do for Q2."""
    q = {}
    for lv in LEVELS:
        cd = case_dir(lv)
        et = ENDTIME[lv]
        s_h = series_minmax(cd, "housing")
        s_c = series_minmax(cd, "core")
        s_q4 = series_volavg(cd, "core")
        s_q6 = series_volavg(cd, "housing")
        s_q2 = series_patch_T(cd)
        s_q5 = series_wall_heat(cd)
        for nm, s in (("Q1", s_h), ("Q3", s_c), ("Q4", s_q4),
                      ("Q6", s_q6), ("Q2", s_q2), ("Q5", s_q5)):
            if s[-1][0] != et:
                refuse("%s/%s: last series sample is at iteration %g, not the "
                       "registered endTime %d" % (lv, nm, s[-1][0], et))
        q[lv] = dict(Q1=s_h[-1][1], Q3=s_c[-1][1], Q4=s_q4[-1][1],
                     Q6=s_q6[-1][1], Q2=s_q2[-1][1], Q5=s_q5[-1][1],
                     _series=dict(Q1=s_h, Q3=s_c, Q4=s_q4, Q6=s_q6,
                                  Q2=s_q2, Q5=s_q5))
    return q


def plant_control_for(qname, level, series_path_fn):
    """A planted-zero control on the REAL artifact, read back through the REAL
    parser -- not the generic series control.  A control that cannot be built is
    a refusal, never a pass."""
    cd = case_dir(level)
    p = series_path_fn(cd)
    before = _read_dat(p, want_field=("T" if qname in ("Q1", "Q3") else None))[-1][1]
    lines = open(p, errors="replace").read().split("\n")
    idx = max(k for k, l in enumerate(lines) if l.strip() and not l.startswith("#"))
    orig = lines[idx]
    cols = orig.split("\t")
    col = 4 if qname in ("Q1", "Q3") else len(cols) - 1
    cols[col] = repr(float(cols[col]) + PLANT)
    lines[idx] = "\t".join(cols)
    tmp = p + ".plant"
    open(tmp, "w").write("\n".join(lines))
    try:
        after = _read_dat(tmp, want_field=("T" if qname in ("Q1", "Q3") else None))[-1][1]
    finally:
        os.remove(tmp)
    return RT.external_plant_control("%s @%s" % (qname, level), before, after,
                                     artifact=p, level=level)


# ==========================================================================
# REPAIR R2 -- the grading-path sha recorder.  IT GRADES NOTHING.
# ==========================================================================
def _git(args):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def grading_path_shas():
    """(rel, post-repair working-tree blob, pre-registration frozen blob).

    TWO DIFFERENT OBJECTS, labelled as two (section 2d.4.3).  The left column is
    what is running NOW; the right is what stood in the tree at
    GRADING_PATH_FREEZE_COMMIT, the commit that froze this comparator.
    """
    out = []
    for rel in GRADING_PATH:
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            refuse("grading-path member %s is not on disk; the path this "
                   "comparator grades on cannot be recorded" % rel)
        now = _git(["hash-object", p])
        frozen = _git(["rev-parse", "%s:%s"
                       % (GRADING_PATH_FREEZE_COMMIT, rel)])
        out.append((rel, now or "UNAVAILABLE", frozen or "ABSENT-AT-FREEZE"))
    return out


def print_grading_path_shas():
    """SANAA'S UNIVERSAL RULE OF 2026-08-26 GOVERNS THE CHOICE NOT TO REFUSE ON
    AN UNAVAILABLE SHA: bookkeeping never voids physics.  A missing FILE is a
    refusal above, because a grading-path member that is not on disk cannot have
    graded anything.  A git query that cannot answer is INFRASTRUCTURE: it is
    printed as UNAVAILABLE, loudly, and it does not void a solve.  This is the
    same posture `analyse_t23g.py:grading_path_shas` took under its own
    section 2d.1 grant (DEAD_LEVER_AUDIT section 27.4)."""
    note("GRADING-PATH SHAS -- REPAIR R2, registered at "
         "T23G2_PREREGISTRATION.md:671")
    note("  THIS RECORDER GRADES NOTHING.  It reads no field and moves no "
         "comparison.")
    note("  Frozen column = the blob in %s, the commit that froze this "
         "comparator." % GRADING_PATH_FREEZE_COMMIT)
    for rel, now, frozen in grading_path_shas():
        same = "IDENTICAL" if now == frozen else "DIFFERS"
        note("  %s" % rel)
        note("      post-repair (working tree) : %s" % now)
        note("      pre-registration (frozen)  : %s   %s" % (frozen, same))
    note("")
    note("  THE TWO COLUMNS ARE TWO DIFFERENT OBJECTS AND ARE NOT INTERCHANGEABLE.")
    note("  THIS RECORDER DOES NOT RESTORE THE REGISTERED PROVENANCE AND DOES "
         "NOT CLAIM TO:")
    note("  :671 contemplated shas present FROM THE FIRST GRADED SOLVE.  Adding "
         "the recorder\n  CHANGES this file's sha, so only the forward half is "
         "available (section 2d.4.3).")
    note("  NO GRADED SOLVE WAS EVER PRODUCED UNDER A COMPARATOR CARRYING THIS "
         "RECORDER.\n")


# ==========================================================================
def main(argv):
    note("=" * 74)
    note("T23G2 COMPARATOR -- gates frozen in T23G2_PREREGISTRATION.md v1.2")
    note("GRADING THE FINE VALUE.  The Richardson extrapolate is REPORTED and "
         "NEVER GATED ON.")
    note("=" * 74 + "\n")

    print_grading_path_shas()          # REPAIR R2, before the first gate
    require_done()
    ms = gate_meshsim()
    cv, it_states = gate_conv()
    yv, ypl = gate_yplus()

    q = read_quantities()

    # ---- G-PLATEAU and G-RATIO, on EVERY graded quantity -----------------
    note("G-PLATEAU and G-RATIO -- section 5.3, on EVERY graded quantity")
    pl_states, pv, rv = {}, "PASS", "PASS"
    for qn in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
        pl_states[qn] = {}
        for lv in LEVELS:
            st, spread, lim, n = plateau(q[lv]["_series"][qn], ENDTIME[lv],
                                         rel=(qn == "Q5"))
            pl_states[qn][lv] = st
            if st != "PLATEAUED":
                pv = "GATE FAIL"
        vals = [q[lv][qn] for lv in LEVELS]
        diffs = [vals[0] - vals[1], vals[1] - vals[2]]
        _, sp, _, _ = plateau(q[LEVELS[-1]]["_series"][qn], ENDTIME[LEVELS[-1]],
                              rel=(qn == "Q5"))
        rst, ratio, smallest = g_ratio(qn, sp, diffs)
        if rst != "PASS":
            rv = "GATE FAIL"
        note("  %s  plateau %s | finest iterative change %.6e, smallest "
             "inter-level difference %.6e, ratio %.1f (needs >= %.0f)  %s"
             % (qn, "/".join(pl_states[qn][lv][:4] for lv in LEVELS),
                sp, smallest, ratio, RATIO_MIN, rst))
    note("  G-PLATEAU: %s    G-RATIO: %s\n" % (pv, rv))

    # ---- the order, on Q4 -------------------------------------------------
    note("G-ORDER -- on %s (core volume-averaged T), band %s" %
         (ORDER_QUANTITY, ORDER_BAND))
    note("  The band is [0.5, 1.5] and NOT [1.5, 2.5] because the formal order "
         "of the\n  energy convection term is ONE: T23G_F/system/fluid/"
         "fvSchemes line 33,\n  `div(phi,h) bounded Gauss upwind`.  Sanaa's "
         "section 0 point 3 is scheme-relative.\n")

    rows = {}
    for qn in ("Q4", "Q1", "Q2", "Q3", "Q6"):
        levels = [dict(name=lv, cells=CELLS[lv], value=q[lv][qn] - T_REF)
                  for lv in LEVELS]
        pc = plant_control_for(qn, LEVELS[-1],
                               (lambda cd, _q=qn: _series_path(cd, _q)))
        row = RT.grade_ladder(qn, levels, DIM, BAND_Q1, pc,
                              iterative_states=it_states,
                              plateau_states=pl_states[qn])
        rows[qn] = row
        note(RT.format_row(row))

    # Q5 -- REPORTED, NEVER GATED (section 5.2; P4 predicts it fails again)
    v5 = [q[lv]["Q5"] for lv in LEVELS]
    t5 = RT.triple_from_cells(v5[0], v5[1], v5[2],
                              CELLS[LEVELS[0]], CELLS[LEVELS[1]],
                              CELLS[LEVELS[2]], DIM)
    note("Q5 housing surface heat flux -- REPORTED, NEVER GATED")
    note("  values %s  state %s  order %s"
         % (v5, t5["state"], t5.get("order")))
    note("  A DIVERGENT or STAGNANT reading here is PRE-REGISTERED as the "
         "expected outcome (P4)\n  and is NOT a failure of this rung: the "
         "quantity is pinned by the imposed 305 W\n  source to ~4e-5 relative. "
         "A CONVERGING reading in [1.5, 2.5] would mean P4 LOST.\n")

    # ---- A2.1: the discriminating observation ----------------------------
    p4 = rows["Q4"]["orders"][-1]
    p1 = rows["Q1"]["orders"][-1]
    if p4 is not None and p1 is not None:
        spread = abs(p4 - p1)
        note("A2.1 -- THE DISCRIMINATING OBSERVATION, registered before the run")
        note("  p(Q4) = %.4f, p(Q1) = %.4f, spread = %.4f" % (p4, p1, spread))
        note("  H-MESH predicts spread < 0.05 with p in [0.7, 1.3]; "
             "H-IFACE predicts spread > 0.15\n  with p in [0.25, 0.65] and the "
             "housing quantity LOWER.  On T23G the spread was\n  0.0027, which "
             "is a point AGAINST H-IFACE recorded before this run.\n")

    verdicts = [ms, cv, yv, pv, rv] + [rows[q_]["verdict"] for q_ in rows]
    final = ("NOT A RESULT" if "NOT A RESULT" in verdicts else
             "GATE FAIL" if "GATE FAIL" in verdicts else "PASS")
    note("=" * 74)
    note("RUNG VERDICT: %s" % final)
    note("=" * 74)
    return RT.exit_code_for(final)


def _series_path(cd, qn):
    if qn in ("Q1",):
        return os.path.join(cd, "postProcessing", "housing", "housing_T", "0",
                            "fieldMinMax.dat")
    if qn in ("Q3",):
        return os.path.join(cd, "postProcessing", "core", "core_T", "0",
                            "fieldMinMax.dat")
    if qn == "Q4":
        return os.path.join(cd, "postProcessing", "core", "core_volavg_T", "0",
                            "volFieldValue.dat")
    if qn == "Q6":
        return os.path.join(cd, "postProcessing", "housing",
                            "housing_volavg_T", "0", "volFieldValue.dat")
    if qn == "Q2":
        return os.path.join(cd, "postProcessing", "housing", "housing_patch_T",
                            "0", "surfaceFieldValue.dat")
    if qn == "Q5":
        return os.path.join(cd, "postProcessing", "housing",
                            "housing_wall_heat", "0", "surfaceFieldValue.dat")
    refuse("no series path registered for %r" % qn)


if __name__ == "__main__":
    # A REFUSAL EXITS 2, UNAMBIGUOUSLY, AND NEVER AS A TRACEBACK.
    # T23G's record had to read its verdict off stdout because exit 1 was
    # ambiguous by design there.  A refusal that arrives as an uncaught
    # exception is worse still: it is indistinguishable from the comparator
    # itself being broken.  Here 0 = PASS, 1 = a graded non-PASS, 2 = REFUSED.
    try:
        sys.exit(main(sys.argv[1:]))
    except RT.Refusal as e:
        print("\nREFUSED (exit 2): %s" % e)
        sys.exit(2)
