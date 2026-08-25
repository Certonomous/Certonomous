#!/usr/bin/env python3
"""
CURRICULUM D11-C' grader -- the COMPONENT-1 finite-difference STEP SWEEP.  Frozen instrument.

WHAT THIS BUYS, AND WHY IT IS A SEPARATE BUY.
D11-F' returned GATE REACHED with "MRF-ON adjoint vs central FD: relative error
1.704895e-07".  Its gate G11-5 sets `adj = dP[0]`: it compared COMPONENT 0 ONLY.
Read off the D11-F' artifacts on disk, switching the MRF zone from omega=0 to
omega=30 rad/s moves

    component 0   0.23061616252401435  ->  0.23058711100900367   (1.26e-04 relative)
    component 1   3.1484221063860114e-09 -> -1.366011909783860e-04 (4-5 ORDERS)

so the FD-checked component is ~99.99 % non-MRF and the component MRF dominates was
never FD-checked at all.  This instrument buys the missing check.

WHY A SWEEP AND NOT A STEP.  DAFOAM_CHARTER.md section 1 -- "a DAFoam gradient is not a
result until a finite-difference table stands beside it at a step proved to lie in the
plateau" -- and section 3 -- "the plateau is read PER COMPONENT, not off the vector".
`h = 1.0e-3` was the single step D11-F' used, in m/s, on component 0, and NO PLATEAU WAS
EVER DEMONSTRATED FOR IT.  A step proved for one component in one unit has no standing in
another component in another unit, so this grader demonstrates a plateau or it returns
NOT A RESULT.  A separately registered secondary sweep re-asks the same question of
component 0 in m/s, which is the only way the standing of `1.0e-3` can be settled.

REFUSAL DISCIPLINE (CLAUDE.md rules 3 and 4; L-302).
  * Every list is asserted NON-EMPTY **and of the registered LENGTH** before it is
    indexed, and the REFUSAL PRINTS THE COUNT.  The D3 defect this exists to avoid --
    `d3_grade.py` returning PASS at 0.0000 % over an EMPTY component set -- came from a
    refusal that tested KEY PRESENCE and never NON-EMPTINESS.  A partial plant reads on
    the page exactly like a complete one.
  * The discrimination control is placed ON THE QUANTITY THAT REACHES THE VERDICT --
    component 1 of the MRF-ON adjoint -- and not on some other quantity that merely
    correlates with it.  That property's absence is what made the D3 control fire
    correctly while certifying a result it had not measured.
  * A missing or non-COMPLETE stage is NOT A RESULT (a failure of THIS lane's harness),
    never BLOCKED.  BLOCKED is reserved for a stage that ran to completion and returned
    no derivative -- capability shown absent, not capability never reached.  rc=1 and
    rc=2 are different failures and an argparse refusal is not a solver refusal.

Exit codes: 0 verdict rendered; 2 REFUSAL.
"""
import json, os, sys, math, argparse

# ---------------------------------------------------------------- FROZEN CONSTANTS
OMEGA_PLANT = "30.0"
OMEGA_INERT = "0.0"

N_COMPONENTS_REQUIRED = 2       # dTPIn_dpatchV = [d/d(speed), d/d(aoa)]
COMPONENT_UNDER_TEST = 1        # THE component D11-F' did not check
COMPONENT_SECONDARY = 0         # D11-F's own component, re-asked as a sweep

FLOOR_DERIV = 1.0e-12           # |adj| at or below this is a silently-zero derivative
PLANT_ATTRIB_MIN = 0.5          # >= this fraction of |adj_1(omega=30)| must be MRF-attributable
EPS_MACH = 2.220446049250313e-16
NOISE_FACTOR = 10.0             # an FD signal must exceed this many noise floors to be usable
PLATEAU_TOL_REL = 2.0e-2        # max relative spread of FD estimates inside a plateau window
PLATEAU_MIN_STEPS = 3           # a plateau is at least this many CONSECUTIVE usable steps
FD_BAND_REL = 5.0e-2            # adjoint-vs-FD band, the same 5 % D11-F' used for component 0

REGISTERED_CPUSET = [13]        # the core this probe is pinned to; READ BACK from the process

# tag, h.  AOA in degrees (component 1); U in m/s (component 0).
AOA_STEPS = [("1em5", 1.0e-5), ("1em4", 1.0e-4), ("1em3", 1.0e-3),
             ("1em2", 1.0e-2), ("1em1", 1.0e-1), ("1e00", 1.0e0)]
U_STEPS = [("1em4", 1.0e-4), ("1em3", 1.0e-3), ("1em2", 1.0e-2), ("1em1", 1.0e-1)]

# The step whose standing D11-F' left open, and the unit it was used in.
FPRIME_H = 1.0e-3               # m/s, on component 0

STAGES_SCALAR = ["omegaP", "omega0", "base1", "base2"]


class Refusal(Exception):
    pass


def _finite(x):
    return isinstance(x, float) and math.isfinite(x)


def _read_json(path):
    if not os.path.isfile(path):
        raise Refusal("artifact missing: %s -- a stage of THIS lane's harness did not "
                      "produce its record; that is NOT A RESULT, not BLOCKED" % path)
    with open(path) as f:
        return json.load(f)


def read_omega_from_disk(path, expect):
    """Plant read-back (CLAUDE.md rule 3): the planted omega must be visible ON DISK."""
    if not os.path.isfile(path):
        raise Refusal("plant read-back impossible, no such file: %s" % path)
    for line in open(path):
        s = line.strip()
        if s.startswith("omega") and s.endswith(";"):
            got = s.split()[1].rstrip(";")
            if got != expect:
                raise Refusal("plant read-back FAILED: %s carries omega %s, expected %s"
                              % (path, got, expect))
            return got
    raise Refusal("plant read-back FAILED: no omega entry in %s" % path)


def require_components(rec, name):
    """L-302: refuse on an EMPTY **or SHORT** component set, BY COUNT, PRINTING THE COUNT."""
    if "dTPIn_dpatchV" not in rec:
        return None                      # caller decides BLOCKED vs NOT A RESULT
    d = rec["dTPIn_dpatchV"]
    if not isinstance(d, list):
        raise Refusal("dTPIn_dpatchV in %s is not a list, it is %s" % (name, type(d).__name__))
    if len(d) != N_COMPONENTS_REQUIRED:
        raise Refusal("COMPONENT-SET REFUSAL: dTPIn_dpatchV in %s holds %d component(s), "
                      "the registered length is %d. An instrument that cannot say "
                      "'I measured nothing' will report a number it did not measure (L-302); "
                      "no comparison is formed and no verdict is rendered."
                      % (name, len(d), N_COMPONENTS_REQUIRED))
    for i, v in enumerate(d):
        if not _finite(v):
            raise Refusal("component %d of %s is %r (NaN/inf)" % (i, name, v))
    return d


def require_tp(rec, name):
    if rec.get("status") != "COMPLETE":
        raise Refusal("stage %s did not COMPLETE; status=%r -- NOT A RESULT" % (name, rec.get("status")))
    if not _finite(rec.get("TPIn")):
        raise Refusal("TPIn in stage %s is not a finite float: %r" % (name, rec.get("TPIn")))
    return rec["TPIn"]


def sweep_table(recs, steps, pfx, label):
    """Central FD estimate per registered step.  REFUSES on a short table."""
    rows = []
    for tag, h in steps:
        np_, nm_ = "%s_p_%s" % (pfx, tag), "%s_m_%s" % (pfx, tag)
        for nm in (np_, nm_):
            if nm not in recs:
                raise Refusal("SWEEP REFUSAL: %s sweep is missing stage %s; the table would be "
                              "SHORT and a plateau read off a short table is not a plateau" % (label, nm))
        tp_p, tp_m = require_tp(recs[np_], np_), require_tp(recs[nm_], nm_)
        signal = abs(tp_p - tp_m)
        rows.append({"tag": tag, "h": h, "tp_p": tp_p, "tp_m": tp_m,
                     "signal": signal, "fd": (tp_p - tp_m) / (2.0 * h)})
    if len(rows) != len(steps):
        raise Refusal("SWEEP REFUSAL: %s table holds %d rows, %d registered" % (label, len(rows), len(steps)))
    if len(rows) < PLATEAU_MIN_STEPS:
        raise Refusal("SWEEP REFUSAL: %s table holds %d rows, fewer than the %d a plateau needs"
                      % (label, len(rows), PLATEAU_MIN_STEPS))
    return rows


def find_plateau(rows, noise_floor):
    """Longest run of >= PLATEAU_MIN_STEPS CONSECUTIVE steps that are (a) resolved above the
    noise floor, (b) of one sign, and (c) agree to PLATEAU_TOL_REL.  Ties -> lowest start."""
    n = len(rows)
    usable = [r["signal"] >= NOISE_FACTOR * noise_floor for r in rows]
    best = None
    for i in range(n):
        for j in range(i + PLATEAU_MIN_STEPS - 1, n):
            if not all(usable[i:j + 1]):
                continue
            vals = [r["fd"] for r in rows[i:j + 1]]
            if min(vals) > 0.0 or max(vals) < 0.0:
                pass
            else:
                continue                                   # mixed sign is not a plateau
            lo, hi = min(abs(v) for v in vals), max(abs(v) for v in vals)
            if lo <= 0.0:
                continue
            if (hi - lo) / lo > PLATEAU_TOL_REL:
                continue
            if best is None or (j - i) > (best[1] - best[0]):
                best = (i, j)
    return best, usable


def grade_component(rows, adj, noise_floor, comp, label):
    """Returns (status, detail, plateau, ref_index)."""
    best, usable = find_plateau(rows, noise_floor)
    tbl = "; ".join("h=%.1e fd=%.10e signal=%.3e %s"
                    % (r["h"], r["fd"], r["signal"], "usable" if u else "NOISE-DOMINATED")
                    for r, u in zip(rows, usable))
    if best is None:
        return ("NOT A RESULT",
                "%s: NO PLATEAU. No %d consecutive registered steps agree to %.1e relative while "
                "resolved above %.1fx the noise floor %.3e. The adjoint component %d value "
                "%.10e is NOT defended by this sweep and MUST NOT be quoted as verified. "
                "Full table (failed steps included, per VERIFICATION_CHARTER section 7): %s"
                % (label, PLATEAU_MIN_STEPS, PLATEAU_TOL_REL, NOISE_FACTOR, noise_floor, comp,
                   adj, tbl), None, None)
    i, j = best
    ref = i + (j - i) // 2
    fd = rows[ref]["fd"]
    if abs(fd) <= FLOOR_DERIV:
        return ("NOT A RESULT",
                "%s: plateau FD reference is %.6e <= floor %.1e; the ratio cannot be formed. Table: %s"
                % (label, fd, FLOOR_DERIV, tbl), best, ref)
    err = abs(adj - fd) / abs(fd)
    span = "h in [%.1e, %.1e], %d steps, reference h=%.1e" % (rows[i]["h"], rows[j]["h"], j - i + 1, rows[ref]["h"])
    if err > FD_BAND_REL:
        return ("GATE FAIL",
                "%s: PLATEAU DEMONSTRATED (%s) but adjoint component %d = %.10e vs plateau FD "
                "%.10e is %.6e relative, OUTSIDE the band %.3e. Table: %s"
                % (label, span, comp, adj, fd, err, FD_BAND_REL, tbl), best, ref)
    return ("PASS",
            "%s: PLATEAU DEMONSTRATED (%s); adjoint component %d = %.10e vs plateau FD %.10e, "
            "relative error %.6e <= band %.3e. Table: %s"
            % (label, span, comp, adj, fd, err, FD_BAND_REL, tbl), best, ref)


def grade(recs):
    g = {}

    # ---- stage integrity.  A missing/incomplete stage is NOT A RESULT, never BLOCKED.
    for nm in STAGES_SCALAR:
        if nm not in recs:
            raise Refusal("stage %s absent from the record set -- NOT A RESULT" % nm)
    tp_P = require_tp(recs["omegaP"], "omegaP")
    tp_0 = require_tp(recs["omega0"], "omega0")
    tp_b1 = require_tp(recs["base1"], "base1")
    tp_b2 = require_tp(recs["base2"], "base2")

    # ---- G11C-0  the component set, BY COUNT.  BLOCKED only if a COMPLETED stage returned none.
    dP = require_components(recs["omegaP"], "omegaP")
    if dP is None:
        return "BLOCKED", {"G11C-0": ("BLOCKED", "omegaP COMPLETED but returned no dTPIn_dpatchV key -- "
                                                 "the MRF-active adjoint was reached and produced nothing")}
    d0 = require_components(recs["omega0"], "omega0")
    if d0 is None:
        raise Refusal("omega0 COMPLETED but returned no dTPIn_dpatchV key; the MRF-inert reference "
                      "needed by the plant control does not exist")
    g["G11C-0"] = ("PASS", "component set length %d == registered %d in BOTH omegaP and omega0; "
                           "omegaP = %s, omega0 = %s"
                   % (len(dP), N_COMPONENTS_REQUIRED,
                      ["%.10e" % v for v in dP], ["%.10e" % v for v in d0]))

    adj1, adj1_0 = dP[COMPONENT_UNDER_TEST], d0[COMPONENT_UNDER_TEST]
    adj0, adj0_0 = dP[COMPONENT_SECONDARY], d0[COMPONENT_SECONDARY]

    # ---- G11C-1  the verdict quantity is not silently zero
    if abs(adj1) <= FLOOR_DERIV:
        g["G11C-1"] = ("GATE FAIL", "SILENTLY-ZERO MRF-frame adjoint on the component under test: "
                                    "|component %d| = %.6e <= floor %.1e"
                       % (COMPONENT_UNDER_TEST, abs(adj1), FLOOR_DERIV))
        return "GATE FAIL", g
    g["G11C-1"] = ("PASS", "MRF-ON adjoint component %d = %.10e, magnitude above floor %.1e"
                   % (COMPONENT_UNDER_TEST, adj1, FLOOR_DERIV))

    # ---- G11C-2  THE PLANT, ON THE QUANTITY THAT REACHES THE VERDICT
    #      Not on TPIn, not on the vector -- on component 1 itself.
    if adj1 == adj1_0:
        raise Refusal("PLANTED-ZERO REFUSAL: component %d is BIT-IDENTICAL at omega=%s and omega=%s "
                      "(%.17e). The MRF plant does not reach the quantity this probe grades, so no "
                      "agreement measured here would be evidence about MRF."
                      % (COMPONENT_UNDER_TEST, OMEGA_PLANT, OMEGA_INERT, adj1))
    attrib = abs(adj1 - adj1_0) / abs(adj1)
    if attrib < PLANT_ATTRIB_MIN:
        raise Refusal("PLANTED-ZERO REFUSAL: only %.6e of MRF-ON component %d is attributable to "
                      "switching the MRF zone on (floor %.2f). adj=%.10e, inert=%.10e. This probe "
                      "would be checking the NON-MRF part of the derivative -- which is exactly the "
                      "defect in D11-F' that it exists to repair."
                      % (attrib, COMPONENT_UNDER_TEST, PLANT_ATTRIB_MIN, adj1, adj1_0))
    g["G11C-2"] = ("PASS", "MRF-attributable fraction of component %d is %.10f (adj(omega=%s) = %.10e, "
                           "adj(omega=%s) = %.10e); the plant reaches the graded quantity"
                   % (COMPONENT_UNDER_TEST, attrib, OMEGA_PLANT, adj1, OMEGA_INERT, adj1_0))

    # ---- G11C-3  the noise floor, MEASURED, before any step is sized (N-D15 discipline)
    d_rep = abs(tp_b1 - tp_b2)
    d_task = abs(tp_b1 - tp_P)
    noise_floor = max(d_rep, d_task, EPS_MACH * abs(tp_b1))
    g["G11C-3"] = ("PASS", "noise floor MEASURED, not assumed: repeat |base1-base2| = %.6e, "
                           "cross-task |base1-omegaP| = %.6e, representational eps*|TPIn| = %.6e "
                           "-> floor %.6e (TPIn base = %.16e). A zero repeat bounds REPRODUCIBILITY "
                           "only; it does not bound iterative-truncation jitter, which the sweep does."
                   % (d_rep, d_task, EPS_MACH * abs(tp_b1), noise_floor, tp_b1))

    # ---- the two sweeps
    aoa_rows = sweep_table(recs, AOA_STEPS, "aoa", "AOA sweep (component 1, deg)")
    u_rows = sweep_table(recs, U_STEPS, "u", "U sweep (component 0, m/s)")

    max_sig = max(r["signal"] for r in aoa_rows)
    if max_sig < NOISE_FACTOR * noise_floor:
        g["G11C-4"] = ("NOT A RESULT", "NO registered aoa step resolves component 1 above the noise "
                                       "floor: largest signal %.6e < %.1f x %.6e"
                       % (max_sig, NOISE_FACTOR, noise_floor))
        return "NOT A RESULT", g

    # ---- G11C-4/5  the component under test
    st, det, best, ref = grade_component(aoa_rows, adj1, noise_floor, COMPONENT_UNDER_TEST,
                                         "COMPONENT 1 (d TPIn / d aoa, 1/deg), MRF ON at omega=%s" % OMEGA_PLANT)
    g["G11C-4"] = ("PASS", "aoa sweep table formed over %d registered steps" % len(aoa_rows)) \
        if best is not None else ("NOT A RESULT", "aoa sweep formed but no plateau exists in it")
    g["G11C-5"] = (st, det)

    # ---- G11C-6  the SECONDARY, separately registered sweep: component 0 in m/s, and the
    #      standing of D11-F's h = 1.0e-3.  REGISTERED IN ADVANCE AS NOT ALTERING THE VERDICT.
    st0, det0, best0, ref0 = grade_component(u_rows, adj0, noise_floor, COMPONENT_SECONDARY,
                                             "COMPONENT 0 (d TPIn / d U, 1/(m/s)), MRF ON at omega=%s" % OMEGA_PLANT)
    if best0 is None:
        stand = ("NO PLATEAU exists in the registered U sweep, so D11-F's h = %.1e m/s is NOT shown "
                 "to lie in one and its 1.704895e-07 agreement REMAINS UNDEFENDED as a plateau step."
                 % FPRIME_H)
    else:
        i0, j0 = best0
        inside = u_rows[i0]["h"] <= FPRIME_H <= u_rows[j0]["h"]
        stand = ("D11-F's h = %.1e m/s %s the demonstrated plateau h in [%.1e, %.1e]; its agreement "
                 "figure is therefore %s as a plateau step."
                 % (FPRIME_H, "LIES INSIDE" if inside else "LIES OUTSIDE",
                    u_rows[i0]["h"], u_rows[j0]["h"],
                    "RETROACTIVELY DEFENDED" if inside else "STILL UNDEFENDED"))
    g["G11C-6"] = (st0, det0 + " || STANDING OF D11-F' h: " + stand +
                   " || REGISTERED IN ADVANCE: this gate does NOT alter the probe verdict, which is "
                   "the component-1 chain; it is a separately registered finding about D11-F'.")

    # ---- G11C-7  container placement, READ BACK from the process, never inferred
    bad = []
    for nm, r in sorted(recs.items()):
        aff = r.get("sched_affinity")
        if aff != REGISTERED_CPUSET:
            bad.append("%s=%r" % (nm, aff))
    if bad:
        g["G11C-7"] = ("GATE FAIL", "measured CPU affinity differs from the registered cpuset %r in "
                                    "%d stage(s): %s. REGISTERED CONSEQUENCE: this bears on the COST "
                                    "attribution row (contention), NEVER on the derivative verdict."
                       % (REGISTERED_CPUSET, len(bad), ", ".join(bad)))
    else:
        g["G11C-7"] = ("PASS", "every stage reports measured CPU affinity %r, equal to the registered "
                               "cpuset; placement is READ FROM THE PROCESS, not inferred from the flag"
                       % REGISTERED_CPUSET)

    order = {"PASS": 0, "GATE REACHED": 0, "GATE FAIL": 1, "NOT A RESULT": 2, "BLOCKED": 3}
    chain = [g[k][0] for k in ("G11C-0", "G11C-1", "G11C-2", "G11C-3", "G11C-4", "G11C-5")]
    worst = max(chain, key=lambda s: order[s])
    return ("GATE REACHED" if worst in ("PASS", "GATE REACHED") else worst), g


# ------------------------------------------------------------------------ SELFTEST
def _synth(adj1=-1.366011909783860e-04, adj0=0.23058711100900367,
           adj1_inert=3.1484221063860114e-09, tp=1.1859858226134654,
           n_comp=2, drop_key=False, jitter=0.0, base2=None, aff=None, adj1_adj=None):
    """A synthetic record set whose FD tables are EXACTLY linear, so a healthy grade must
    reach the gate.  `jitter` multiplies a per-step perturbation that destroys the plateau.
    `adj1` drives the SYNTHETIC FD TABLE; `adj1_adj` (default equal to it) is what the
    synthetic ADJOINT reports, so the two can be made to disagree independently."""
    aff = REGISTERED_CPUSET if aff is None else aff
    adj1_adj = adj1 if adj1_adj is None else adj1_adj
    recs = {}
    dP = [adj0, adj1_adj][:n_comp]
    d0 = [0.23061616252401435, adj1_inert][:n_comp]
    recs["omegaP"] = {"status": "COMPLETE", "TPIn": tp, "sched_affinity": aff}
    if not drop_key:
        recs["omegaP"]["dTPIn_dpatchV"] = dP
    recs["omega0"] = {"status": "COMPLETE", "TPIn": 1.183671978501559,
                      "dTPIn_dpatchV": d0, "sched_affinity": aff}
    recs["base1"] = {"status": "COMPLETE", "TPIn": tp, "sched_affinity": aff}
    recs["base2"] = {"status": "COMPLETE", "TPIn": tp if base2 is None else base2, "sched_affinity": aff}
    for k, (tag, h) in enumerate(AOA_STEPS):
        w = 1.0 + jitter * ((-1) ** k)
        recs["aoa_p_%s" % tag] = {"status": "COMPLETE", "TPIn": tp + adj1 * h * w, "sched_affinity": aff}
        recs["aoa_m_%s" % tag] = {"status": "COMPLETE", "TPIn": tp - adj1 * h * w, "sched_affinity": aff}
    for tag, h in U_STEPS:
        recs["u_p_%s" % tag] = {"status": "COMPLETE", "TPIn": tp + adj0 * h, "sched_affinity": aff}
        recs["u_m_%s" % tag] = {"status": "COMPLETE", "TPIn": tp - adj0 * h, "sched_affinity": aff}
    return recs


def selftest():
    n = 0
    v, g = grade(_synth())
    assert v == "GATE REACHED", "A: healthy record did not reach the gate, got %r" % v
    assert g["G11C-6"][0] == "PASS", "A: secondary sweep did not PASS on a linear table"
    assert "LIES INSIDE" in g["G11C-6"][1], "A: h=1e-3 should lie inside a full-width U plateau"
    n += 1

    try:                                            # B  EMPTY component set
        grade(_synth(n_comp=0)); raise AssertionError("B: EMPTY component set did NOT refuse")
    except Refusal as e:
        assert "holds 0 component" in str(e), "B: refusal did not PRINT THE COUNT: %s" % e
    n += 1

    try:                                            # C  SHORT (len 1) component set -- the D3 shape
        grade(_synth(n_comp=1)); raise AssertionError("C: SHORT component set did NOT refuse")
    except Refusal as e:
        assert "holds 1 component" in str(e), "C: refusal did not PRINT THE COUNT: %s" % e
    n += 1

    v, _ = grade(_synth(adj1=0.0, adj1_inert=0.0))  # D  silently-zero verdict quantity
    assert v == "GATE FAIL", "D: silently-zero component 1 did not GATE FAIL, got %r" % v
    n += 1

    try:                                            # E  plant blind: MRF does not reach component 1
        grade(_synth(adj1_inert=-1.366011909783860e-04))
        raise AssertionError("E: bit-identical component 1 did NOT refuse")
    except Refusal as e:
        assert "BIT-IDENTICAL" in str(e), "E: wrong refusal: %s" % e
    n += 1

    try:                                            # F  plant mostly non-MRF (the D11-F' defect itself)
        grade(_synth(adj1_inert=-1.36e-04 * 0.9))
        raise AssertionError("F: 90 %-non-MRF component did NOT refuse")
    except Refusal as e:
        assert "attributable" in str(e), "F: wrong refusal: %s" % e
    n += 1

    v, g = grade(_synth(jitter=0.2))                # G  no plateau -> NOT A RESULT
    assert v == "NOT A RESULT", "G: a jittered sweep did not return NOT A RESULT, got %r" % v
    assert "NO PLATEAU" in g["G11C-5"][1], "G: verdict did not name the missing plateau"
    n += 1

    v, g = grade(_synth(adj1_adj=-1.366011909783860e-04 * 1.5))  # H  plateau but adjoint disagrees
    assert v == "GATE FAIL", "H: adjoint-FD disagreement did not GATE FAIL, got %r" % v
    assert "PLATEAU DEMONSTRATED" in g["G11C-5"][1], "H: should have found a plateau first"
    n += 1

    # I  a noise floor that swallows the whole sweep -> NOT A RESULT, no plateau claimed
    v, g = grade(_synth(base2=1.1859858226134654 + 1.0))
    assert v == "NOT A RESULT", "I: a noise-swamped sweep did not return NOT A RESULT, got %r" % v
    assert "noise floor" in g["G11C-4"][1], "I: verdict did not name the noise floor"
    n += 1

    # J  BLOCKED is reserved for a COMPLETED stage that returned no derivative
    v, g = grade(_synth(drop_key=True))
    assert v == "BLOCKED", "J: completed-but-no-derivative did not give BLOCKED, got %r" % v
    n += 1

    # K  misplacement is caught and does NOT change the derivative verdict
    v, g = grade(_synth(aff=[0]))
    assert v == "GATE REACHED", "K: misplacement wrongly changed the derivative verdict to %r" % v
    assert g["G11C-7"][0] == "GATE FAIL", "K: misplacement was not caught"
    n += 1

    # L  a SHORT sweep table refuses rather than reading a plateau off fewer steps
    r = _synth(); del r["aoa_p_1em2"]
    try:
        grade(r); raise AssertionError("L: a missing sweep stage did NOT refuse")
    except Refusal as e:
        assert "SHORT" in str(e), "L: wrong refusal: %s" % e
    n += 1

    print("D11-C' GRADER SELFTEST: %d/%d PASS "
          "(A healthy, B empty-set refuses WITH COUNT, C short-set refuses WITH COUNT, "
          "D zero-component GATE FAIL, E bit-identical plant refuses, F mostly-non-MRF plant refuses, "
          "G no-plateau NOT A RESULT, H disagreement GATE FAIL, I noise-swamped NOT A RESULT, "
          "J completed-but-empty BLOCKED, K misplacement caught without touching the verdict, "
          "L short sweep refuses)" % (n, n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11C")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    names = list(STAGES_SCALAR)
    for tag, _h in AOA_STEPS:
        names += ["aoa_p_%s" % tag, "aoa_m_%s" % tag]
    for tag, _h in U_STEPS:
        names += ["u_p_%s" % tag, "u_m_%s" % tag]
    try:
        # plant read-back off disk for every stage, BEFORE any number is read
        for nm in names:
            want = OMEGA_INERT if nm == "omega0" else OMEGA_PLANT
            read_omega_from_disk(os.path.join(a.root, nm, "constant", "MRFProperties"), want)
        recs = {nm: _read_json(os.path.join(a.root, nm, "d11c_%s.json" % nm)) for nm in names}
        verdict, gates = grade(recs)
    except Refusal as e:
        print("D11-Cprime PROBE VERDICT: NOT A RESULT")
        print("GRADER REFUSED (exit 2): %s" % e)
        return 2
    for k in sorted(gates):
        print("  %-8s %-12s %s" % (k, gates[k][0], gates[k][1]))
    print("D11-Cprime PROBE VERDICT: %s" % verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
