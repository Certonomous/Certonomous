#!/usr/bin/env python3
"""PRD-E1 COMPARATOR / GRADER -- Porous Radiator Duct, EXACT-tier rung 1.
Navier-spine Case 3.  Grades the CFD Delta-p across the porous core against the
analytic Darcy-Forchheimer-Ergun law fed into the sink -- a self-consistency gate.

STOP-BEFORE-FREEZE.  THIS IS AN UNFROZEN DRAFT COMPARATOR.  verify_self() below
REFUSES TO GRADE while GRADING_PATH_FREEZE_COMMIT is the placeholder "PIN-AT-FREEZE"
(rule 2: a comparator not pinned to a freeze commit has not been shown to be the
file that ran).  --selftest exercises the instrument WITHOUT a freeze.  It LAUNCHES
NOTHING; it reads artifacts and REFUSES (exit 2) rather than degrade.  The gate
DESIGN is frozen by the ruling; the numbers are believed only after the
supervisor's non-delegable §3 check-1 diff-read and verification's ½rho check-1.

WHAT IS DELEGATED, NEVER REIMPLEMENTED (rule 14 -- imported, asserted at the call
site):
  * rule 5 gating, the observed order, GCI (Fs=1.25), the CONVERGING/DIVERGENT/...
    states and the planted-zero contract come from scripts/roache_triple.py.
    PLANT, FS and grade_ladder are IMPORTED, never redefined.
  * rule 4 completion is DELEGATED to mark_done_prd.py as a subprocess.

THE FROZEN GATE HIERARCHY (ruling §1.4, amendment element 4; rule 5), in order:
  (1) any level not iteratively converged / not plateaued  -> NOT A RESULT;
  (2) triple not CONVERGING (DIVERGENT/STAGNANT/OSCILLATORY/EXACT/DEGENERATE)
      -> NOT A RESULT, both triples + orders printed;
  (3) CONVERGING -> G-ERGUN (per-level Delta-p within ±3%, band > GCI) AND
      G-ASYMP (Richardson-extrapolated Delta-p within ±1.5% of Ergun)
      -> PASS iff BOTH hold, else GATE FAIL naming the failing gate + mechanism.
  GCI (Fs=1.25) is ALWAYS printed.  PASS at all five U_s is the credential.
Pre-asymptotic guard (ruling §1.2): if L3 GCI (Fs=1.25) >= 2.0% for any U_s, that
U_s is PRE-ASYMPTOTIC -> re-form the triple at (L2, L3, L4).  p outside [1, 2.5] or
a non-monotone triple -> NOT A RESULT and run L4 (ruling §2, amendment element 5).

THE ×rho Pa CONVERSION IS LOAD-BEARING (draft §2.1:86-88; ruling §3.3).  simpleFoam
solves KINEMATIC pressure p = P/rho [m2/s2]; Ergun is in Pa.  So the CFD Delta-p
(kinematic) is multiplied by RHO to obtain Pa BEFORE any comparison.  The single
conversion site is dp_pa() below and it is commented for the check-1 diff-read.
The ½rho / 3.5 factor lives in the COEFFICIENTS (build_prd.py, verified against
v2606 source); this file re-states the cross-check 0.5*RHO*f == B in --selftest.
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
RUNS = os.path.join(REPO, "verification/runs/navier_class/PRD")   # not created yet

sys.path.insert(0, os.path.join(REPO, "scripts"))
import roache_triple as RT                                         # noqa: E402
from roache_triple import PLANT, FS                                # noqa: E402


def refuse(msg):
    """REFUSE, exit 2 (the "refuse rather than degrade" contract; fail-closed).
    roache_triple's own refuse raises RT.Refusal for library callers; this file
    is a CLI grader, so its own refusals exit 2.  A RT.Refusal raised from inside
    grade_ladder is caught and converted to exit 2 at the grade site."""
    print("REFUSE: " + msg)
    sys.exit(2)

# ==========================================================================
# FROZEN NUMBERS -- transcribed from the draft/ruling; none chosen here.
# ==========================================================================
RHO = 1.2                # air density [kg/m3]  (draft §1:69) -- the ×rho factor
A_ERGUN = 1687.5         # Ergun viscous per length [Pa.s/m2]   (draft §2.3:147)
B_ERGUN = 6562.5         # Ergun inertial per length [Pa.s2/m3] (draft §2.3:148)
F_STREAM = 10937.5       # DarcyForchheimer f streamwise [1/m]  (draft §2.3:150)
L_CORE = 0.100           # porous-core length [m]               (draft §1:64)

U_S_SET = (0.25, 0.50, 1.00, 2.00, 4.00)                          # draft §3:186-190
ERGUN_TARGET_PA = (83.20, 248.44, 825.00, 2962.50, 11175.00)      # draft §3:186-190

DIM = 3                  # 3D hex duct; representative_h = (Nref/N)^(1/3)
LEVELS = ("L1", "L2", "L3")
CELLS = {"L1": 18432, "L2": 147456, "L3": 1179648, "L4": 9437184}  # draft §5:242-247

# --- the frozen gate bands (ruling §1.1, §1.3, amendment elements 2,3) ------
ERGUN_BAND_REL = 0.03    # G-ERGUN: per-level Delta-p within ±3%   (ruling §1.1)
ASYMP_BAND_REL = 0.015   # G-ASYMP: Richardson extrapolate ±1.5%   (ruling §1.3)
PREASYMP_GCI_PCT = 2.0   # L3 GCI >= 2.0% -> PRE-ASYMPTOTIC, run L4 (ruling §1.2)
ORDER_BAND = (1.0, 2.5)  # p outside [1, ~2.5] -> NOT A RESULT, run L4 (ruling §2)
YPLUS_MAX = 200.0        # continuous/Menter treatment upper bound (ruling §4.6)

# --- §6 planted-zero controls (rule 3) --------------------------------------
PLANT_DP = 3.210         # Pa; distinctive, > solver noise, << smallest gated 83.2 Pa
                         # (draft §6:292).  Planted into the outlet plane sample.
PLANT_DP_TOL_PA = 1e-6   # the readback must land to this [Pa]
INERT_DP_MAX_PA = 1.0    # the D=f=0 (INERT) control: |Delta-p| < 1 Pa (<< 83.2)

# --- the freeze pin (rule 2) ------------------------------------------------
# The supervisor sets this to the commit that freezes PRD-E1 at freeze time.
# While it reads "PIN-AT-FREEZE" the file is an UNFROZEN DRAFT and verify_self()
# REFUSES TO GRADE.  --selftest does NOT need it.
GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"
GRADING_PATH = (
    "docs/campaigns/navier_class/PRD/PRD_E1_PREREGISTRATION.md",
    "cases/navier_class/PRD/build_prd.py",
    "cases/navier_class/PRD/analyse_prd.py",
    "cases/navier_class/PRD/mark_done_prd.py",
    "cases/navier_class/PRD/autograde_prd.py",   # §2ba autograder: pins the plateau
                                                 # criterion (verdict-shaping, rule-5
                                                 # step a) + the y+/checkMesh gates
    "scripts/roache_triple.py",
)


def note(msg):
    print(msg)


def verify_self():
    """Rule 2 freeze pin.  While GRADING_PATH_FREEZE_COMMIT is 'PIN-AT-FREEZE'
    this comparator is UNFROZEN and REFUSES to grade -- an unpinned comparator
    has not been shown to be the file that ran.  The running blob is printed as
    provenance (VERIFICATION_CHARTER §2au.2 print-only pattern; a self-referential
    IDENTICAL assertion against its own freeze commit is a SHA-1 pre-image)."""
    r = subprocess.run(["git", "hash-object", os.path.abspath(__file__)],
                       cwd=REPO, capture_output=True, text=True)
    now = r.stdout.strip() if r.returncode == 0 else "UNAVAILABLE"
    if GRADING_PATH_FREEZE_COMMIT == "PIN-AT-FREEZE":
        refuse("SELF-HASH: GRADING_PATH_FREEZE_COMMIT is still the DRAFT "
               "placeholder 'PIN-AT-FREEZE'.  This comparator is UNFROZEN and "
               "will NOT grade; the supervisor pins the freeze commit at freeze "
               "(rule 2).  Working-tree blob is %s.  Use --selftest to exercise "
               "the instrument without a freeze." % now)
    note("SELF-HASH: running blob %s (freeze pin %s) -- print-only provenance\n"
         % (now, GRADING_PATH_FREEZE_COMMIT))


# ==========================================================================
# ANALYTIC ERGUN reference (from the frozen coefficients)
# ==========================================================================
def ergun_dp(u_s):
    """Analytic Ergun Delta-p [Pa] = A*L_core*U + B*L_core*U^2 = 168.75U+656.25U^2."""
    return A_ERGUN * L_CORE * u_s + B_ERGUN * L_CORE * u_s * u_s


# ==========================================================================
# RULE 4 -- DELEGATED to mark_done_prd.py, CALLED, never reimplemented
# ==========================================================================
def require_done(cases):
    md = os.path.join(HERE, "mark_done_prd.py")
    if not os.path.isfile(md):
        refuse("the completion instrument %s is not on disk; rule 4 cannot be "
               "evaluated and this file will NOT reimplement it" % md)
    note("COMPLETION -- rule 4, DELEGATED to %s and CALLED" % os.path.relpath(md, REPO))
    bad = []
    for case in cases:
        r = subprocess.run([sys.executable, md, "--root", RUNS, "--case", case],
                           capture_output=True, text=True)
        for line in (r.stdout or "").rstrip().split("\n"):
            if line.strip():
                note("  | " + line)
        if r.returncode != 0:
            bad.append((case, r.returncode))
    if bad:
        refuse("rule 4 completion FAILED for %s; a run that fails any clause is "
               "not done and this comparator will not grade it"
               % ", ".join("%s (rc=%d)" % b for b in bad))
    note("")


# ==========================================================================
# THE Delta-p READ PATH -- surfaceFieldValue.dat, and the ×rho Pa conversion
# ==========================================================================
def read_plane_avg(dat_path):
    """Last area-averaged value from an OpenFOAM surfaceFieldValue.dat.  REFUSES
    on a missing/empty/unparsable file rather than returning 0 (which downstream
    would read as 'no pressure')."""
    if not os.path.isfile(dat_path):
        refuse("plane sample %s is not on disk; the gate it feeds CANNOT be "
               "evaluated and an unevaluated gate is not a passed one" % dat_path)
    last = None
    for line in open(dat_path, errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        cols = s.split()
        try:
            last = float(cols[-1])
        except ValueError:
            continue
    if last is None:
        refuse("%s parsed to NO data rows; an empty series is not a reading" % dat_path)
    return last


def _plane_dat(case_dir, name):
    base = os.path.join(case_dir, "postProcessing", name)
    if not os.path.isdir(base):
        refuse("no postProcessing/%s under %s; the Delta-p reader has nothing to "
               "read" % (name, case_dir))
    subs = sorted((d for d in os.listdir(base)
                   if os.path.isdir(os.path.join(base, d))),
                  key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else -1)
    if not subs:
        refuse("no time subdirectory under postProcessing/%s" % name)
    return os.path.join(base, subs[-1], "surfaceFieldValue.dat")


def dp_pa(p_in_kin, p_out_kin):
    """THE ×rho Pa CONVERSION -- LOAD-BEARING (draft §2.1; ruling §3.3).
    simpleFoam solves kinematic pressure p=P/rho [m2/s2]; Ergun is in Pa.  The
    Delta-p across the core is (inlet-plane p) - (outlet-plane p), still kinematic,
    so it is multiplied by RHO to obtain Pa:

        Delta-p_Pa = RHO * (p_in_kin - p_out_kin)          # <-- ×rho, RHO=1.2

    Drop this ×rho and every graded number is wrong by a factor of 1.2; keep it
    and the self-consistency gate reproduces Ergun (which is in Pa)."""
    return RHO * (p_in_kin - p_out_kin)


def read_dp_pa(case_dir):
    """Read the core Delta-p in Pa for one case (one level, one U_s).  REFUSES a
    perfect-zero pair (a reader wired to nothing) -- a real run has pressure."""
    p_in = read_plane_avg(_plane_dat(case_dir, "dp_inlet_plane"))
    p_out = read_plane_avg(_plane_dat(case_dir, "dp_outlet_plane"))
    if p_in == 0.0 and p_out == 0.0:
        refuse("%s: both plane samples read a PERFECT 0.0.  A zero from a reader "
               "not shown able to see a non-zero is not evidence (rule 3)." % case_dir)
    return dp_pa(p_in, p_out), p_in, p_out


# ==========================================================================
# PLANTED CONTROLS (rule 3) -- §6 of the draft
# ==========================================================================
def control_dp_reader(inlet_dat, outlet_dat, reader=read_plane_avg):
    """CONTROL 3 (§6): plant PLANT_DP into the OUTLET plane sample on disk, re-read
    through the REAL reader, and REFUSE unless the reported Delta-p_Pa shifts by
    exactly -PLANT_DP (raising the outlet pressure LOWERS Delta-p = p_in - p_out).
    The plant is a kinematic PLANT_DP/RHO so that after ×rho it is exactly
    PLANT_DP in Pa.  This proves the reader is wired to the field on disk.
    Returns a dict grade_ladder's assert_plant_control accepts.

    `reader` is injected SO THE BLIND ARM CAN BE DRIVEN (rule 3): a reader that
    ignores the file returns the same value from the planted copy, `seen` is
    False, and `passed` is False -- the only property that makes it a control."""
    p_in = reader(inlet_dat)
    p_out = reader(outlet_dat)
    before = dp_pa(p_in, p_out)
    plant_kin = PLANT_DP / RHO
    tmp = outlet_dat + ".plant"
    try:
        _plant_last_value(outlet_dat, tmp, plant_kin)
        p_out_planted = reader(tmp)
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
    after = dp_pa(p_in, p_out_planted)
    shift = after - before
    seen = (p_out_planted != p_out)
    ok = seen and abs(shift - (-PLANT_DP)) <= PLANT_DP_TOL_PA
    if not seen:
        note("    PLANTED CONTROL (Delta-p reader): the reader returned the "
             "IDENTICAL outlet value from a planted file -- it cannot see the "
             "perturbation; its zeros mean nothing (rule 3).")
    return dict(passed=bool(ok), planted=PLANT_DP, reader="read_plane_avg (Delta-p)",
                artifact=outlet_dat, reader_delta=shift, expected=-PLANT_DP)


def visibility_pair(inert_dp_pa, active_dp_pa):
    """CONTROLS 1+2 (§6): the D=f=0 (INERT) case must read |Delta-p| < 1 Pa, and
    the D,f-set (ACTIVE) case must read Delta-p > 0 at Ergun order.  A zero from
    the ACTIVE reader, or a non-zero from the INERT reader, REFUSES the pair --
    the pair is what licenses trusting the INERT near-zero (rule 3)."""
    ok_inert = abs(inert_dp_pa) < INERT_DP_MAX_PA
    ok_active = active_dp_pa > INERT_DP_MAX_PA
    return dict(passed=bool(ok_inert and ok_active), inert=inert_dp_pa,
                active=active_dp_pa, reader="Delta-p visibility pair")


def _plant_last_value(src, dst, plant):
    """Write a copy of a surfaceFieldValue.dat with `plant` ADDED to the last
    data row's last column.  Header/comment lines are copied verbatim."""
    lines = open(src, errors="replace").read().splitlines(keepends=True)
    idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s and not s.startswith("#"):
            try:
                float(s.split()[-1])
                idx = i
            except (ValueError, IndexError):
                continue
    if idx is None:
        refuse("%s: no data row to plant into; the control would be vacuous" % src)
    cols = lines[idx].rstrip("\n").split()
    cols[-1] = repr(float(cols[-1]) + plant)
    lines[idx] = " ".join(cols) + "\n"
    open(dst, "w").write("".join(lines))


# ---- y+ reader (primary log instrument) + its planted control (rule 3) -----
def yplus_from_log(path):
    """Parse `simpleFoam -postProcess -func yPlus` output: per-patch max y+.
    REFUSES a perfect-zero-on-every-patch reading (rule 3)."""
    import re
    if not os.path.isfile(path):
        refuse("y+ log %s is not on disk; the y+ gate CANNOT be evaluated" % path)
    txt = open(path, errors="replace").read()
    out = {}
    for m in re.finditer(r"patch\s+(\S+)\s+y\+\s*:\s*min\s*=\s*([-\d.eE+]+)"
                         r"\s*,?\s*max\s*=\s*([-\d.eE+]+)\s*,?\s*average\s*=\s*"
                         r"([-\d.eE+]+)", txt):
        out[m.group(1)] = dict(min=float(m.group(2)), max=float(m.group(3)),
                               avg=float(m.group(4)))
    if not out:
        refuse("%s parsed to NO y+ patch rows; the gate cannot be evaluated" % path)
    if all(v["max"] == 0.0 and v["min"] == 0.0 for v in out.values()):
        refuse("%s reports y+ = 0 on every patch.  A perfect zero from a reader "
               "not shown able to see a non-zero is REFUSED (rule 3)." % path)
    return out


def control_yplus_log(path):
    """Plant PLANT (additive) into a copy of the y+ log and re-read with the REAL
    parser; REFUSE unless the reported max moves by exactly PLANT."""
    import re
    base = yplus_from_log(path)
    pn = sorted(base)[0]
    before = base[pn]["max"]
    txt = open(path, errors="replace").read()
    pat = re.compile(r"(patch\s+%s\s+y\+\s*:\s*min\s*=\s*[-\d.eE+]+\s*,?\s*max"
                     r"\s*=\s*)([-\d.eE+]+)" % re.escape(pn))
    m = pat.search(txt)
    if m is None:
        refuse("%s: could not locate the max field for patch %s; a control that "
               "cannot be constructed is a refusal" % (path, pn))
    planted = txt[:m.start()] + m.group(1) + repr(float(m.group(2)) + PLANT) + txt[m.end():]
    tmp = path + ".plant"
    try:
        open(tmp, "w").write(planted)
        after = yplus_from_log(tmp)
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
    return RT.external_plant_control("y+ log reader @%s" % pn, before,
                                     after[pn]["max"], artifact=path, level=pn)


# ==========================================================================
# THE GATE, per U_s -- G-ERGUN + G-ASYMP on a CONVERGING triple, rule 5 order.
# ==========================================================================
def grade_us(u_s, dp_by_level, plant_control, iterative_states, plateau_states,
             have_l4=False):
    """Grade one U_s.  dp_by_level maps level name -> Delta-p_Pa (in Pa, already
    ×rho).  Uses roache_triple.grade_ladder for the rule-5 hierarchy + G-ERGUN
    band + GCI, then applies G-ASYMP and the pre-asymptotic / order-band guards.

    Returns (verdict, detail dict).  verdict in the fixed vocabulary."""
    ergun = ergun_dp(u_s)
    band = (ergun * (1.0 - ERGUN_BAND_REL), ergun * (1.0 + ERGUN_BAND_REL))

    def _levels(names):
        return [dict(name=n, cells=CELLS[n], value=dp_by_level[n]) for n in names]

    triple_levels = ("L1", "L2", "L3")
    row = RT.grade_ladder("Delta-p @ U_s=%.2f" % u_s, _levels(triple_levels), DIM,
                          band, plant_control, iterative_states=iterative_states,
                          plateau_states=plateau_states)

    # (1)/(2) rule 5 already applied by grade_ladder -> NOT A RESULT stops here.
    if row["verdict"] == "NOT A RESULT":
        return "NOT A RESULT", dict(row=row, ergun=ergun, why=row["why"])

    # (3) CONVERGING: order-band and pre-asymptotic guards BEFORE grading.
    p = row.get("order")
    gci = row.get("GCI_pct")
    if p is None or not (ORDER_BAND[0] <= p <= ORDER_BAND[1]):
        return "NOT A RESULT", dict(row=row, ergun=ergun, flag_L4=True,
                                    why="observed order p=%s outside %s -> NOT A "
                                        "RESULT, run L4 (ruling §2)"
                                        % ("n/a" if p is None else "%.4f" % p, ORDER_BAND))
    if gci is not None and gci >= PREASYMP_GCI_PCT:
        if not have_l4:
            return "NOT A RESULT", dict(row=row, ergun=ergun, flag_L4=True,
                                        why="L3 GCI=%.4f%% >= %.1f%% -> PRE-ASYMPTOTIC; "
                                            "run L4 and re-form triple at (L2,L3,L4) "
                                            "(ruling §1.2)" % (gci, PREASYMP_GCI_PCT))
        # re-form the triple at (L2, L3, L4)
        row = RT.grade_ladder("Delta-p @ U_s=%.2f (L2,L3,L4)" % u_s,
                              _levels(("L2", "L3", "L4")), DIM, band, plant_control,
                              iterative_states=iterative_states,
                              plateau_states=plateau_states)
        if row["verdict"] == "NOT A RESULT":
            return "NOT A RESULT", dict(row=row, ergun=ergun, why=row["why"])
        p = row.get("order")
        if p is None or not (ORDER_BAND[0] <= p <= ORDER_BAND[1]):
            return "NOT A RESULT", dict(row=row, ergun=ergun,
                                        why="re-formed order p outside band")

    # G-ERGUN: the fine-value band verdict from grade_ladder (band > GCI check).
    g_ergun = row["band_verdict"]
    band_gt_gci = (row.get("GCI_pct") is None) or (
        row["GCI_pct"] < 100.0 * ERGUN_BAND_REL)   # band 3% must exceed GCI%
    # G-ASYMP: Richardson-extrapolated Delta-p within ±1.5% of Ergun.  roache's
    # 'richardson' is the CORRECTED extrapolate (f_fine - e21/den).
    rich = row.get("richardson")
    asymp_rel = abs(rich - ergun) / ergun if rich is not None else None
    g_asymp = (asymp_rel is not None and asymp_rel <= ASYMP_BAND_REL)

    fails = []
    if g_ergun != "PASS":
        fails.append("G-ERGUN (fine Delta-p %.4f Pa outside ±%.0f%% of Ergun %.4f Pa)"
                     % (row["value"], 100 * ERGUN_BAND_REL, ergun))
    if not band_gt_gci:
        fails.append("band>GCI violated (GCI %.4f%% >= band %.1f%%; discretization "
                     "dominates)" % (row["GCI_pct"], 100 * ERGUN_BAND_REL))
    if not g_asymp:
        mech = "core-face velocity non-uniformity, or the rho/superficial-velocity "\
               "handling in explicitPorositySource"
        fails.append("G-ASYMP (Richardson extrapolate %s vs Ergun %.4f Pa, rel %s > "
                     "±%.1f%%; mechanism: %s)"
                     % ("n/a" if rich is None else "%.4f Pa" % rich, ergun,
                        "n/a" if asymp_rel is None else "%.4f%%" % (100 * asymp_rel),
                        100 * ASYMP_BAND_REL, mech))
    verdict = "PASS" if not fails else "GATE FAIL"
    detail = dict(row=row, ergun=ergun, g_ergun=g_ergun, g_asymp=g_asymp,
                  band_gt_gci=band_gt_gci, asymp_rel=asymp_rel,
                  gci_pct=row.get("GCI_pct"), order=p, richardson=rich,
                  why=("both gates hold" if not fails else "; ".join(fails)))
    return verdict, detail


# ==========================================================================
# --selftest -- drive every reader, control and the gate hierarchy on synthetic
# data.  No solver, no freeze.
# ==========================================================================
_CHECKS = []


def _ck(name, ok, detail=""):
    _CHECKS.append(bool(ok))
    print("  [%s] %s%s" % ("ok " if ok else "FAIL", name, ("   " + detail) if detail else ""))


def _write_plane(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("# Time areaAverage(p)\n0 %r\n50 %r\n" % (value, value))


def _synth_case(root, name, level, p_in_kin, p_out_kin):
    cd = os.path.join(root, name)
    _write_plane(os.path.join(cd, "postProcessing", "dp_inlet_plane", "0",
                              "surfaceFieldValue.dat"), p_in_kin)
    _write_plane(os.path.join(cd, "postProcessing", "dp_outlet_plane", "0",
                              "surfaceFieldValue.dat"), p_out_kin)
    return cd


def selftest():
    print("analyse_prd.py --selftest  (readers, controls, gate hierarchy; NO solver)")

    # (0) verify_self refuses to grade while unfrozen
    try:
        verify_self()
        _ck("verify_self REFUSES while PIN-AT-FREEZE", False, "did not refuse")
    except SystemExit as e:
        _ck("verify_self REFUSES to grade while unfrozen (rule 2)", e.code == 2)

    # (1) the ½rho cross-check restated (0.5*RHO*f == B)
    _ck("0.5*RHO*F_STREAM == B_ERGUN (½rho / 3.5 undo, restated)",
        abs(0.5 * RHO * F_STREAM - B_ERGUN) < 1e-6)

    # (2) ergun_dp reproduces the five draft targets
    worst = max(abs(ergun_dp(u) - t) for u, t in zip(U_S_SET, ERGUN_TARGET_PA))
    _ck("ergun_dp reproduces the five draft Delta-p targets", worst < 0.01,
        "worst |delta| = %.5f Pa" % worst)

    tmp = tempfile.mkdtemp(prefix="prd_analyse_")
    try:
        # (3) the ×rho Pa conversion: a known kinematic pair -> Pa
        # p_in_kin=100, p_out_kin=0 -> Delta-p_Pa = 1.2*100 = 120 Pa
        cd = _synth_case(tmp, "c1", "L1", 100.0, 0.0)
        got, pin, pout = read_dp_pa(cd)
        _ck("read_dp_pa applies ×rho (100 kin -> 120 Pa)", abs(got - 120.0) < 1e-9,
            "got %.6f Pa" % got)

        # (4) the perfect-zero pair REFUSES
        cdz = _synth_case(tmp, "cz", "L1", 0.0, 0.0)
        try:
            read_dp_pa(cdz)
            _ck("read_dp_pa REFUSES a perfect-zero pair", False)
        except SystemExit as e:
            _ck("read_dp_pa REFUSES a perfect-zero pair (rule 3)", e.code == 2)

        # (5) Delta-p reader planted control: shift == -PLANT_DP, seen
        inlet = _plane_dat(cd, "dp_inlet_plane")
        outlet = _plane_dat(cd, "dp_outlet_plane")
        pc = control_dp_reader(inlet, outlet)
        _ck("Delta-p reader control SEES the plant (shift == -PLANT_DP)",
            pc["passed"] and abs(pc["reader_delta"] + PLANT_DP) < PLANT_DP_TOL_PA,
            "shift %.6f Pa, expected %.3f" % (pc["reader_delta"], -PLANT_DP))

        # (5b) the Delta-p control CAN FAIL: a BLIND reader that ignores the file
        # (returns a constant) reads the planted copy identical -> not seen -> not
        # passed.  This is the property that makes it a control (rule 3).
        pc_blind = control_dp_reader(inlet, outlet, reader=lambda p: 42.0)
        _ck("Delta-p reader control FAILS with a BLIND reader (constant)",
            not pc_blind["passed"])

        # (6) visibility pair: INERT ~0, ACTIVE > 0 passes; a zero ACTIVE fails
        vp = visibility_pair(0.02, 825.0)
        _ck("visibility pair PASSES (INERT 0.02 Pa, ACTIVE 825 Pa)", vp["passed"])
        vp_bad = visibility_pair(0.02, 0.0)
        _ck("visibility pair FAILS on a zero ACTIVE reading", not vp_bad["passed"])
        vp_bad2 = visibility_pair(50.0, 825.0)
        _ck("visibility pair FAILS on a non-zero INERT reading", not vp_bad2["passed"])

        # (7) y+ log reader + planted control + zero-refusal
        ylog = os.path.join(tmp, "log.yPlus")
        open(ylog, "w").write("patch walls y+ : min = 12.3, max = 78.4, average = 45.1\n")
        yr = yplus_from_log(ylog)
        _ck("y+ reader parses max per patch", abs(yr["walls"]["max"] - 78.4) < 1e-9)
        yc = control_yplus_log(ylog)
        _ck("y+ reader control SEES the plant (rule 3)", yc["passed"])
        yzero = os.path.join(tmp, "log.yPlusZero")
        open(yzero, "w").write("patch walls y+ : min = 0, max = 0, average = 0\n")
        try:
            yplus_from_log(yzero)
            _ck("y+ reader REFUSES an all-zero reading", False)
        except SystemExit as e:
            _ck("y+ reader REFUSES an all-zero reading (rule 3)", e.code == 2)

        # (8) THE GATE HIERARCHY on synthetic Delta-p ladders.  A plant control
        # passed dict is required by grade_ladder; build a passing one.
        good_pc = dict(passed=True, planted=PLANT_DP, reader="synthetic",
                       artifact="synthetic", reader_delta=-PLANT_DP)
        conv = {"c": "CONVERGED", "m": "CONVERGED", "f": "CONVERGED"}
        plat = {"c": "PLATEAUED", "m": "PLATEAUED", "f": "PLATEAUED"}
        # roache uses the level NAMES in the states dict; grade_us builds levels
        # named L1/L2/L3, so map states to those.
        st_it = {"L1": "CONVERGED", "L2": "CONVERGED", "L3": "CONVERGED"}
        st_pl = {"L1": "PLATEAUED", "L2": "PLATEAUED", "L3": "PLATEAUED"}

        # 8a: a converging ladder landing ON Ergun -> PASS (both gates).
        # Build Delta-p_i = ergun + amp*h_i^2 (2nd order), amp tiny so fine and
        # extrapolate are both within band.
        u = 1.00
        erg = ergun_dp(u)
        h = {lv: (1.0 / CELLS[lv]) ** (1.0 / 3.0) for lv in ("L1", "L2", "L3", "L4")}
        amp = 0.5 * erg    # ~0.5 Pa-scale coefficient on h^2
        dp_pass = {lv: erg + amp * h[lv] ** 2 for lv in ("L1", "L2", "L3")}
        v, d = grade_us(u, dp_pass, good_pc, st_it, st_pl)
        _ck("gate: converging ladder ON Ergun -> PASS (G-ERGUN & G-ASYMP)",
            v == "PASS", "order=%.3f GCI=%.4f%% asymp_rel=%.4f%%"
            % (d.get("order", 0), d.get("gci_pct") or 0, 100 * (d.get("asymp_rel") or 0)))

        # 8b: a converging ladder OFFSET well outside ±3% -> GATE FAIL.
        dp_fail = {lv: erg * 1.10 + amp * h[lv] ** 2 for lv in ("L1", "L2", "L3")}
        v2, d2 = grade_us(u, dp_fail, good_pc, st_it, st_pl)
        _ck("gate: fine Delta-p +10% -> GATE FAIL naming a gate", v2 == "GATE FAIL",
            d2["why"][:60])

        # 8c: a NON-monotone ladder -> NOT A RESULT.
        dp_nm = {"L1": erg + 5.0, "L2": erg - 5.0, "L3": erg + 5.0}
        v3, d3 = grade_us(u, dp_nm, good_pc, st_it, st_pl)
        _ck("gate: non-monotone triple -> NOT A RESULT", v3 == "NOT A RESULT")

        # 8d: an unconverged level -> NOT A RESULT (step (a) outranks).
        v4, d4 = grade_us(u, dp_pass, good_pc,
                          {"L1": "CONVERGED", "L2": "NOT_CONVERGED", "L3": "CONVERGED"},
                          st_pl)
        _ck("gate: an unconverged level -> NOT A RESULT (step a)", v4 == "NOT A RESULT")

        # 8e: PRE-ASYMPTOTIC (L3 GCI >= 2%) with no L4 -> NOT A RESULT, flag L4.
        # Make a converging-but-coarse ladder: larger amp so GCI is big.
        amp_big = 400.0 * erg     # sized so L3 GCI comfortably exceeds 2%
        dp_pre = {lv: erg + amp_big * h[lv] ** 2 for lv in ("L1", "L2", "L3")}
        v5, d5 = grade_us(u, dp_pre, good_pc, st_it, st_pl, have_l4=False)
        _ck("gate: L3 GCI >= 2% and no L4 -> NOT A RESULT + flag L4",
            v5 == "NOT A RESULT" and d5.get("flag_L4"),
            "GCI=%.3f%%" % (d5["row"].get("GCI_pct") or 0))

        # 8f: grade_ladder REFUSES a failed plant control.
        bad_pc = dict(passed=False, planted=PLANT_DP, reader="blind")
        try:
            grade_us(u, dp_pass, bad_pc, st_it, st_pl)
            _ck("gate: REFUSES a failed plant control", False)
        except SystemExit as e:
            _ck("gate: REFUSES a failed plant control (rule 3)", e.code == 2)
        except RT.Refusal:
            _ck("gate: REFUSES a failed plant control (rule 3)", True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # (9) no module-level assert (L-332)
    import ast
    src = open(os.path.abspath(__file__)).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    _ck("no assert in module body (L-332)", n0 == 0, "%d asserts" % n0)

    n_ok = sum(1 for c in _CHECKS if c)
    print("\n%d/%d checks passed" % (n_ok, len(_CHECKS)))
    return 0 if n_ok == len(_CHECKS) else 1


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if sys.flags.optimize:
        print("REFUSE: this instrument does not run under python -O")
        return 2
    if args.selftest:
        return selftest()
    # A real grade path pins the freeze and reads RUNS; while unfrozen it refuses.
    verify_self()
    refuse("PRD-E1 has not been run: verification/runs/navier_class/PRD/ does not "
           "exist. This comparator grades on-disk artifacts; there are none. "
           "(STOP-BEFORE-FREEZE: authored + self-tested, not yet graded.)")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
